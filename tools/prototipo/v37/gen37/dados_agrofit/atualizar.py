#!/usr/bin/env python3
"""Atualização manual dos dados do AGROFIT/ANVISA para o protótipo.

Faz GET condicional (If-None-Match / If-Modified-Since) dos arquivos oficiais,
só baixa o que mudou, confere tamanho, cabeçalho do CSV e SHA-256, troca o
arquivo de forma atômica e, se algo mudou, roda processar.py.

No sistema real isto vira um job diário no servidor (ver JOB_PRODUCAO.md);
não agendar em computador pessoal.

Uso:
  python3 atualizar.py                 # verifica as 3 fontes e reprocessa se mudou
  python3 atualizar.py --forcar        # reprocessa mesmo sem mudança
  python3 atualizar.py --sem-processar # só verifica/baixa
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import processar  # noqa: E402  (reaproveita fontes, caminhos e leitura dos cabeçalhos antigos)

USER_AGENT = 'SafrionPrototipo/1.0 (consulta a dados abertos AGROFIT/MAPA)'
TIMEOUT_S = 60
TENTATIVAS = 3
ESPERA_S = (5, 20, 60)
PRIMEIRA_COLUNA = {'formulados': 'NR_REGISTRO', 'tecnicos': 'NUMERO_REGISTRO', 'monografias': 'NO_SUBSTANCIA'}


def agora_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def le_estado(raw):
    caminho = os.path.join(raw, 'estado_fontes.json')
    estado = {}
    if os.path.exists(caminho):
        with open(caminho, encoding='utf-8') as f:
            estado = json.load(f)
    for nome in processar.FONTES:  # primeira execução: aproveita os .headers do download original
        e = estado.setdefault(nome, {})
        if not e.get('etag') and not e.get('last_modified'):
            e.update({k: v for k, v in processar.le_headers(raw, nome).items() if v})
        arq = os.path.join(raw, processar.FONTES[nome]['arquivo'])
        if os.path.exists(arq) and not e.get('sha256'):
            e['sha256'] = processar.sha256_arquivo(arq)
            e['bytes'] = os.path.getsize(arq)
    return estado


def grava_estado(raw, estado):
    caminho = os.path.join(raw, 'estado_fontes.json')
    tmp = caminho + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)
    os.replace(tmp, caminho)


def confere_cabecalho(caminho, nome):
    cod = processar.FONTES[nome]['codificacao']
    with open(caminho, encoding=cod, errors='replace') as f:
        primeira = f.readline().strip().lstrip('﻿').strip('"')
    if not primeira.startswith(PRIMEIRA_COLUNA[nome]):
        raise ValueError('cabeçalho inesperado: %r' % primeira[:120])
    if nome == 'formulados':
        colunas = [c.strip() for c in primeira.split(';')]
        if colunas != processar.COLUNAS_FORMULADOS:
            raise ValueError('colunas do formulados mudaram: %s' % colunas)


def baixar_condicional(url, destino, estado_fonte, nome):
    """Devolve 'inalterado' (304 ou mesmo SHA-256) ou 'alterado'. Mantém o arquivo anterior em caso de erro."""
    cab = {'User-Agent': USER_AGENT, 'Accept-Encoding': 'identity'}
    if estado_fonte.get('etag'):
        cab['If-None-Match'] = estado_fonte['etag']
    if estado_fonte.get('last_modified'):
        cab['If-Modified-Since'] = estado_fonte['last_modified']
    req = urllib.request.Request(url, headers=cab)
    try:
        resp = urllib.request.urlopen(req, timeout=TIMEOUT_S)
    except urllib.error.HTTPError as e:
        if e.code == 304:
            estado_fonte['verificado_em'] = agora_iso()
            return 'inalterado'
        raise
    parcial = destino + '.parcial'
    h = hashlib.sha256()
    n = 0
    with resp, open(parcial, 'wb') as f:
        esperado = resp.headers.get('Content-Length')
        while True:
            bloco = resp.read(1024 * 1024)
            if not bloco:
                break
            f.write(bloco)
            h.update(bloco)
            n += len(bloco)
        etag, lm = resp.headers.get('ETag'), resp.headers.get('Last-Modified')
    try:
        if esperado and int(esperado) != n:
            raise ValueError('download incompleto: %d de %s bytes' % (n, esperado))
        if n == 0:
            raise ValueError('arquivo vazio')
        confere_cabecalho(parcial, nome)
    except Exception:
        os.remove(parcial)
        raise
    sha = h.hexdigest()
    estado_fonte.update({'etag': etag, 'last_modified': lm, 'verificado_em': agora_iso()})
    if sha == estado_fonte.get('sha256') and os.path.exists(destino):
        os.remove(parcial)
        return 'inalterado'
    os.replace(parcial, destino)
    estado_fonte.update({'sha256': sha, 'bytes': n, 'baixado_em': agora_iso()})
    return 'alterado'


def main():
    ap = argparse.ArgumentParser(description='GET condicional das fontes oficiais e reprocessamento.')
    ap.add_argument('--raw', default=processar.RAW_PADRAO, help='pasta dos CSVs oficiais e do estado_fontes.json')
    ap.add_argument('--saida', default=processar.SAIDA_PADRAO, help='pasta dos JSON do site')
    ap.add_argument('--fontes', default=','.join(processar.FONTES), help='lista separada por vírgula')
    ap.add_argument('--forcar', action='store_true', help='reprocessa mesmo sem mudança')
    ap.add_argument('--sem-processar', action='store_true', help='só verifica/baixa')
    ap.add_argument('--url-base', help='testes: troca o endereço oficial por <url-base>/<arquivo>')
    args = ap.parse_args()
    os.makedirs(args.raw, exist_ok=True)
    estado = le_estado(args.raw)
    mudou, falhas = [], []
    for nome in [n.strip() for n in args.fontes.split(',') if n.strip()]:
        fonte = processar.FONTES[nome]
        url = (args.url_base.rstrip('/') + '/' + fonte['arquivo']) if args.url_base else fonte['url']
        destino = os.path.join(args.raw, fonte['arquivo'])
        for tentativa in range(TENTATIVAS):
            try:
                r = baixar_condicional(url, destino, estado[nome], nome)
                print('%-12s %s' % (nome, r))
                if r == 'alterado':
                    mudou.append(nome)
                break
            except Exception as e:  # rede, HTTP != 304, validação
                print('%-12s falhou (tentativa %d/%d): %s' % (nome, tentativa + 1, TENTATIVAS, e))
                if tentativa + 1 < TENTATIVAS:
                    time.sleep(ESPERA_S[tentativa])
                else:
                    falhas.append(nome)
                    estado[nome]['ultima_falha'] = '%s %s' % (agora_iso(), e)
        grava_estado(args.raw, estado)
    if (mudou or args.forcar) and not args.sem_processar:
        print('reprocessando:', ', '.join(mudou) or 'forçado')
        subprocess.run([sys.executable, os.path.join(AQUI, 'processar.py'), '--raw', args.raw, '--saida', args.saida],
                       check=True)
    elif not mudou:
        print('nada mudou; site mantido')
    if falhas:
        print('ATENÇÃO: falharam', ', '.join(falhas), '- os arquivos anteriores foram mantidos')
        sys.exit(2)


if __name__ == '__main__':
    main()
