# -*- coding: utf-8 -*-
"""INTEL-01 · testes de unidade da Inteligência de vendas e de compras (inteligencia.js) no node, sem navegador.
Oráculo independente: as contas esperadas saem daqui, em Decimal, dos mesmos dados (INTC e a semente), e não do JS testado.
Monta o JS real: perfis + cenário + producao.js + PR_UI_JS/PR_PED_JS + comercial.js + INTC + inteligencia.js (a mesma montagem
do comercial_unit_test.py). Uso (de gen37/): SAFRION_DADOS=sintetico python3 inteligencia_unit_test.py → 'RESULTADO: OK n/n'."""
import os, sys, json, subprocess
from decimal import Decimal as D
sys.dont_write_bytecode = True
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comercial_unit_test as CU
import dados_inteligencia as DI


def oraculo():
    d = DI.dados(); hoje = '2026-09-26'
    iso = lambda s: s[6:10] + '-' + s[3:5] + '-' + s[0:2]
    it = {}
    for i in d['itens']:
        cs = sorted(d['cot'].get(i['nome'], []), key=lambda x: D(x['preco']))
        val = [x for x in cs if iso(x['validade']) >= hoje]
        m = val[0] if val else None
        it[i['nome']] = dict(melhor=m['preco'] if m else None, f=m['f'] if m else None,
                             vref=str((D(m['preco']) - D(i['ref'])) / D(i['ref'])) if m else None,
                             eco=str(D(i['qtd']) * (D(i['ref']) - D(m['preco']))) if m else None)
    eco = sum((D(v['eco']) for v in it.values() if v['eco'] is not None and D(v['eco']) > 0), D(0))
    tot = sum((D(i['qtd']) * D(i['ref']) for i in d['itens']), D(0))
    pont = {}
    for f in d['forn']:
        es = [h for h in d['hist'] if h['f'] == f['id'] and h['entregue']]
        pont[f['id']] = str(D(sum(1 for h in es if not h['atraso'] > 0)) / D(len(es))) if es else None
    return dict(itens=it, eco=str(eco), rsha=str(tot / D(d['area'])), pont=pont, n_itens=len(d['itens']))


def main():
    src = CU.fonte(True).split('const NUCLEO =')[0]
    src += DI.js() + open(os.path.join(HERE, 'inteligencia.js'), encoding='utf-8').read()
    src += 'const ORA = ' + json.dumps(oraculo(), ensure_ascii=False) + ';\n'
    src += open(os.path.join(HERE, 'inteligencia_unit.js'), encoding='utf-8').read() + '\nprint(JSON.stringify(R));\n'
    os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True)
    p = os.path.join(HERE, '_probe', 'inteligencia_unit.js'); open(p, 'w', encoding='utf-8').write(src)
    r = subprocess.run(['node', p], capture_output=True, text=True, timeout=180)
    out = r.stdout.strip().splitlines(); res = json.loads(out[-1]) if out and r.returncode == 0 else []
    ok = [r.returncode == 0 and bool(res)]
    print(('OK    ' if ok[0] else 'FALHA ') + 'motor JS (node) executou sem erro' + ('' if ok[0] else ' · ' + r.stderr[-900:]))
    for x in res:
        ok.append(x['ok']); print(('OK    ' if x['ok'] else 'FALHA ') + x['n'] + ('' if x['ok'] else ' · ' + x['info']))
    print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
    return all(ok)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
