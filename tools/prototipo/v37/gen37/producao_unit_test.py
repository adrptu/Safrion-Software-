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
    pre = cenario.perfis_js() + cenario.js_prefixo()   # CTL-3: comandos com papel (cenExige) precisam dos perfis
    if 'function prUn(' not in pre: pre += dados_producao.js_regras()   # antes do P2 as regras não estão no prefixo
    from areas import producao as AP   # funções de leitura das telas (prLoteProx etc.): só definições, sem DOM (revisão A-13)
    import dados_comercial   # Comercial A-17: a massa da saca dos contratos legados é registrada pelo comando do Comercial (comConverterSaca), não por atalho no teste
    return PRELUDIO + pre + JS_NUCLEO + AP.PR_UI_JS + AP.PR_PED_JS + dados_comercial.js_regras() + open(os.path.join(HERE, 'producao_unit.js'), encoding='utf-8').read() + '\nprint(JSON.stringify(R));\n'


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
    # regressão (06/10): a tela redefinia prNum (parte de célula) por cima do leitor de número de producao.js e a pesagem recusava o bruto.
    # Nenhum nome global de producao.js pode ser redefinido pelo JS das telas, do cenário ou da carência.
    import re
    from areas import producao as AP
    defs = lambda t: set(re.findall(r'^(?:function|const|let|var)\s+([A-Za-z_$][\w$]*)', t, re.M)) | set(re.findall(r'(?<![\w.])function\s+([A-Za-z_$][\w$]*)\s*\(', t))
    pr = defs(open(os.path.join(HERE, 'producao.js'), encoding='utf-8').read())
    outros = {'cenario.js': open(os.path.join(HERE, 'cenario.js'), encoding='utf-8').read(), 'dados_carencia.JS': __import__('dados_carencia').JS}
    outros.update({'areas/producao.py:' + k: getattr(AP, k) for k in dir(AP) if k.endswith('_JS') and isinstance(getattr(AP, k), str)})
    for nome, t in outros.items():
        dup = sorted(pr & defs(t)); ok(f'nomes de producao.js não são redefinidos em {nome}', not dup, dup)
    print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
    return all(OK)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
