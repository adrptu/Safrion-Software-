# -*- coding: utf-8 -*-
"""Manifesto das medidas de navegador da avaliação do Claude (6c03d7e): liga cada medida ao render e ao SHA.

Responde ao ponto 8 do retorno do Codex (PR #47, comentário 6227708290). Só lê os brutos; não altera nenhum.
Uso: python3 -I -B manifesto_medidas.py <pasta reproducao/ da avaliação>

Por que existe: os JSONs declaram "versao_publicada": "1792184197-5a81" para todas as medidas porque o valor
vem fixo de repro_mapa.py:15. O espelho foi trocado às 00:16:19.98 UTC (espelho_troca.txt) pelo render da
composição 05947ad. Os brutos não têm hora por medida, mas o .txt traz a duração de cada uma ("[ 15.1s]"),
e a hora de gravação do arquivo marca o fim da passada. Contando para trás, cada início calculado é um limite
superior (as folgas entre medidas só antecipam o início real). As folgas são a impressão do resultado entre
medidas e, no fim, fechar o Chrome e gravar o JSON (repro_mapa.py:486-491): segundos. Por isso "certo" exige
margem acima de 5 min e "provável" marca margem de segundos.
"""
import os, re, sys, datetime as dt

D = sys.argv[1]
TROCA = dt.datetime(2026, 10, 17, 0, 16, 19, 984000)
ANTIGO = 'espelho antigo: versão publicada 1792184197-5a81, fonte b9898643662715a3f7b17bf7797d44e81e5e4a3d (fonte_publicado.txt: 0 de 1028 linhas sem par)'
NOVO = 'espelho novo: render da composição 05947ad0152c31c106569219d4fdd09b8c7849a1 (publicação registrada em 47ccc1d5739235b6ebb4f1fcad3e91bb324c7da1; fonte_publicado_05947ad.txt: 0 de 875 linhas sem par)'
print('# Manifesto das medidas M0–M20 (avaliação do Claude, 6c03d7e)')
print('troca do espelho:', TROCA.time(), 'UTC (espelho_troca.txt)')
print('A:', ANTIGO)
print('B:', NOVO)
print('Os 9 arquivos do mapa são iguais nas duas fontes (git diff b989864 05947ad vazio; espelho_troca.txt), então a medida vale')
print('para as duas; o manifesto corrige o rótulo de versão, não o resultado.\n')

def linhas(txt):
    return [(float(re.match(r'\[\s*([\d.]+)s\]', l).group(1)), l.split(']', 1)[1].split(':')[0].strip())
            for l in open(txt, encoding='utf-8') if re.match(r'\[\s*[\d.]+s\]', l)]

print(f"{'arquivo bruto':22} {'medida':6} {'início ≤':15} {'fim ≤':15} espelho")
for suf in ['', '_b', '_c', '_d', '_e', '_f', '_g', '_h']:
    js = os.path.join(D, f'repro_mapa{suf}.json'); txt = os.path.join(D, f'repro_mapa{suf}.txt')
    fim = dt.datetime.utcfromtimestamp(os.stat(txt).st_mtime)
    ms = linhas(txt); t = fim; out = []
    for d, nome in reversed(ms):
        ini = t - dt.timedelta(seconds=d); out.append((nome, ini, t)); t = ini
    for nome, ini, f in reversed(out):
        mid = nome.split()[0]
        if f <= TROCA: esp = 'A (certo: termina antes da troca)'
        elif ini > TROCA + dt.timedelta(minutes=5): esp = 'B (certo: margem > 5 min, muito maior que as folgas)'
        elif ini > TROCA: esp = f'B (provável: margem de {(ini-TROCA).total_seconds():.1f} s menos as folgas entre medidas)'
        else: esp = 'indeterminado (cruza a troca); arquivos do mapa iguais em A e B'
        print(f"{os.path.basename(js):22} {mid:6} {str(ini.time())[:12]:15} {str(f.time())[:12]:15} {esp}")
print('\nO PNG m18c_T7_satelite_1440.png foi gravado às',
      str(dt.datetime.utcfromtimestamp(os.stat(os.path.join(D, 'm18c_T7_satelite_1440.png')).st_mtime).time())[:12],
      'UTC, junto do M18c: espelho B.')
print('Horas de gravação lidas do sistema de arquivos da worktree em que as medidas rodaram (antes do commit 6c03d7e).')
