# -*- coding: utf-8 -*-
"""Prepara a medida do robô v5 (EX-51): copia a candidata e gera as entradas.

Uso: python3 -I preparar.py --render <_render da candidata> --trabalho <dir> [--pedidos <pasta pedidos-1710>]

Faz:
  1. copia o _render para <trabalho>/v3 (o original não é alterado) e grava <trabalho>/v3.sha256 (um hash por arquivo e o hash do conjunto);
  2. gera <trabalho>/entradas/ocultas.json [{tela, decisao}] a partir da classificação do EX-50
     (ex50-classificacao-codex.md: os 123 itens na ordem do anexo original, com a decisão do anexo-telas-ocultas.md
     e as retiradas de exclusão registradas na própria classificação);
  3. gera <trabalho>/robot3/screens.json [{"n": TELA}]: as páginas .dc.html que carregam o aplicativo (support.js),
     menos as marcadas Excluir. As 8 páginas sem aplicativo (7 aliases que só redirecionam para MA e a Main) ficam fora:
     o resumo conta "só as telas que ficam no sistema (exclui as marcadas Excluir e as que só redirecionam)".
"""
import argparse, hashlib, json, os, re, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PEDIDOS = os.path.normpath(os.path.join(AQUI, '..', '..'))


def classificacao(ped):
    """Lista [(n, tela, decisao, situacao)] dos 123 itens."""
    cls = open(os.path.join(ped, 'ex50-classificacao-codex.md'), encoding='utf-8').read()
    anexo = open(os.path.join(ped, 'anexo-telas-ocultas.md'), encoding='utf-8').read()
    # itens da classificação: "## N · NOME" seguido da linha de situação; só a primeira ocorrência de cada N (o delta repete alguns)
    itens = {}
    linhas = cls.split('\n')
    for k, l in enumerate(linhas):
        m = re.match(r'^## (\d+) · (.+)$', l)
        if m and int(m.group(1)) not in itens:
            itens[int(m.group(1))] = (m.group(2).strip(), linhas[k + 1].strip() if k + 1 < len(linhas) else '')
    # tabela completa do anexo: | Tela | Título | Hoje | Decisão | ...
    tab = []
    em = False
    for l in anexo.split('\n'):
        if l.startswith('| Tela | Título | Hoje | Decisão'):
            em = True
            continue
        if em:
            if not l.startswith('|'):
                if tab:
                    break
                continue
            if re.match(r'^\|[-:| ]+\|?\s*$', l):
                continue
            c = [x.strip() for x in l.strip().strip('|').split(' | ')]
            tab.append((c[0], c[3]))
    if len(itens) != 123 or len(tab) != 123:
        sys.exit(f'esperava 123 itens; classificação {len(itens)}, anexo {len(tab)}')
    out = []
    for n in range(1, 124):
        nome, sit = itens[n]
        tela, dec = tab[n - 1]
        if nome != tela:
            sys.exit(f'item {n}: classificação "{nome}" × anexo "{tela}" (ordem diferente)')
        if re.match(r'^Exclusao (retirada|refutada)', sit):
            dec = 'Manter (exclusão retirada na classificação do EX-50)'
        out.append((n, tela, dec, sit))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--render', required=True)
    ap.add_argument('--trabalho', required=True)
    ap.add_argument('--pedidos', default=PEDIDOS)
    a = ap.parse_args()
    v3 = os.path.join(a.trabalho, 'v3')
    if os.path.exists(v3):
        shutil.rmtree(v3)
    os.makedirs(a.trabalho, exist_ok=True)
    shutil.copytree(a.render, v3)
    # hashes da cópia
    h_all = hashlib.sha256()
    linhas = []
    for f in sorted(os.listdir(v3)):
        p = os.path.join(v3, f)
        if not os.path.isfile(p):
            continue
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        linhas.append(f'{h}  {f}')
        h_all.update(f'{h}  {f}\n'.encode())
    open(os.path.join(a.trabalho, 'v3.sha256'), 'w').write('\n'.join(linhas) + '\n')
    # ocultas.json
    itens = classificacao(a.pedidos)
    ent = os.path.join(a.trabalho, 'entradas')
    os.makedirs(ent, exist_ok=True)
    json.dump([{'n': n, 'tela': t, 'decisao': d, 'situacao': s} for n, t, d, s in itens],
              open(os.path.join(ent, 'ocultas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sai = {t for _, t, d, _ in itens if d == 'Excluir'}
    # screens.json
    paginas = sorted(f[:-len('.dc.html')] for f in os.listdir(v3) if f.endswith('.dc.html'))
    sem_app = [p for p in paginas if 'support.js' not in open(os.path.join(v3, p + '.dc.html'), encoding='utf-8').read()]
    telas = [p for p in paginas if p not in sai and p not in sem_app]
    os.makedirs(os.path.join(a.trabalho, 'robot3'), exist_ok=True)
    json.dump([{'n': t} for t in telas], open(os.path.join(a.trabalho, 'robot3', 'screens.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    excl_pag = sorted(sai & set(paginas))
    info = {'render': os.path.abspath(a.render), 'sha256_conjunto': h_all.hexdigest(), 'arquivos': len(linhas), 'paginas': len(paginas),
            'excluir_itens': len(sai), 'excluir_paginas': excl_pag, 'excluir_sem_pagina': sorted(sai - set(paginas)),
            'sem_aplicativo': sem_app, 'telas_robo': len(telas),
            'retiradas': [t for _, t, d, _ in itens if d.startswith('Manter (exclusão retirada')]}
    json.dump(info, open(os.path.join(a.trabalho, 'preparo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps({k: (v if not isinstance(v, list) or len(v) < 12 else f'{len(v)} itens') for k, v in info.items()}, ensure_ascii=False))


if __name__ == '__main__':
    main()
