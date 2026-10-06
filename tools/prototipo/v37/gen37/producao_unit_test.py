# -*- coding: utf-8 -*-
"""Produção · testes de unidade das regras (producao.js) no node, sem navegador; e a fonte única da unidade (Python).
Uso: SAFRION_DADOS=sintetico python3 producao_unit_test.py   → uma linha por verificação e 'RESULTADO: OK n/n' no fim.
Números: docs/colheita/verificacao/contas.py (K01..K15)."""
import os, sys, json, subprocess
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
PRELUDIO = 'globalThis.print=(...a)=>console.log(...a);\n'
OK = []
def ok(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:600]), flush=True)


def fonte():
    import cenario, dados_producao
    from areas.processo_os import JS_NUCLEO
    pre = cenario.js_prefixo()
    if 'function prUn(' not in pre: pre += dados_producao.js_regras()   # antes do P2 as regras não estão no prefixo
    return PRELUDIO + pre + JS_NUCLEO + open(os.path.join(HERE, 'producao_unit.js'), encoding='utf-8').read() + '\nprint(JSON.stringify(R));\n'


def main():
    os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True)
    p = os.path.join(HERE, '_probe', 'producao_unit_all.js'); open(p, 'w', encoding='utf-8').write(fonte())
    r = subprocess.run(['node', p], capture_output=True, text=True, timeout=120)
    out = r.stdout.strip().splitlines()
    ok('motor JS (node) executou sem erro', r.returncode == 0 and out, r.stderr[-800:])
    for x in (json.loads(out[-1]) if out else []): ok(x['n'], x['ok'], x['info'])
    # U01 · o item do CD-06 com fator coincide com CULTURA_UN (uma fonte de fator: D-03)
    import dados_cad as DC
    from areas import cadastros
    it = cadastros._itens()
    for prod in ('Soja em grão', 'Café beneficiado'):
        cu = next((k for k, u in DC.CULTURA_UN.items() if u['prod'] == prod), None)
        ok(f'U01 item do CD-06 "{prod}" na mesma unidade de CULTURA_UN ({it.get(prod, {}).get("un")})',
           cu and it.get(prod, {}).get('un') == f"{DC.CULTURA_UN[cu]['un']} {DC.CULTURA_UN[cu]['massa']} kg", (cu, it.get(prod)))
    print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
    return all(OK)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
