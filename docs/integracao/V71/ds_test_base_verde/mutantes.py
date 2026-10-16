# -*- coding: utf-8 -*-
"""Contraprova do ds_test.py D15 e E2: copia um _render e troca uma linha do OS.dc.html (o código do produto não muda).
Uso: python3 mutantes.py <_render> <pasta de saída> · cria <saída>/m_d15 e <saída>/m_e2 e imprime o sha256 de cada OS.dc.html.
- m_d15: o ícone de situação da linha usa a dica genérica do dicionário (G2_DICAS) em vez da do bloqueio do encerramento (osSeloDica),
  o defeito do achado 6 da revisão DS;
- m_e2: a liberação grava a reserva e avisa "liberada", mas a ordem fica em A liberar."""
import hashlib, os, shutil, sys

TROCAS = {
    'm_d15': ("const d=osSeloDica(o,x.t)||g2dicaDe(x.t);", "const d=g2dicaDe(x.t);"),
    'm_e2': ("o.req = rid; o.reservado = true; o.etapa = 'Liberadas';", "o.req = rid; o.reservado = true;"),
}
render, saida = sys.argv[1], sys.argv[2]
orig = os.path.join(render, 'OS.dc.html')
print('normal', hashlib.sha256(open(orig, 'rb').read()).hexdigest(), 'OS.dc.html')
for nome, (de, para) in TROCAS.items():
    alvo = os.path.join(saida, nome)
    if os.path.exists(alvo): shutil.rmtree(alvo)
    shutil.copytree(render, alvo)
    f = os.path.join(alvo, 'OS.dc.html'); s = open(f, encoding='utf-8').read()
    if s.count(de) != 1: sys.exit(f'{nome}: o trecho aparece {s.count(de)} vezes (esperado 1)')
    open(f, 'w', encoding='utf-8').write(s.replace(de, para))
    print(nome, hashlib.sha256(open(f, 'rb').read()).hexdigest(), 'OS.dc.html')
