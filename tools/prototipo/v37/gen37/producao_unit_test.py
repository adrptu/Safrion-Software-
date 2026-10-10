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
    outros = {'cenario.js': open(os.path.join(HERE, 'cenario.js'), encoding='utf-8').read(), 'dados_carencia.JS': __import__('dados_carencia').JS,
              'safra.js': open(os.path.join(HERE, 'safra.js'), encoding='utf-8').read(),   # UNID-PROD (D-U14): o Planejar safra carrega o conversor
              'ocupacao.js': open(os.path.join(HERE, 'ocupacao.js'), encoding='utf-8').read(), 'cal01.js': open(os.path.join(HERE, 'cal01.js'), encoding='utf-8').read(),
              'unidprod_ui.JS': __import__('unidprod_ui').JS}
    outros.update({'areas/producao.py:' + k: getattr(AP, k) for k in dir(AP) if k.endswith('_JS') and isinstance(getattr(AP, k), str)})
    for nome, t in outros.items():
        dup = sorted(pr & defs(t)); ok(f'nomes de producao.js não são redefinidos em {nome}', not dup, dup)
    # U22 · UNID-PROD (R-U11, revisão RC-03/RC-04): a coluna Produtividade/Meta mostra um texto que muda com a unidade escolhida; a ordem e o
    # filtro por valores usam a chave estável r.ordk (kg/ha), não o texto. Falha na base 47ff754 (o g2lib ordenava e filtrava pelo texto).
    js = r'''const vm=require('vm'),fs=require('fs'); const ctx={}; vm.createContext(ctx);
      vm.runInContext(fs.readFileSync(process.argv[1],'utf8')+';this.g2sort=g2sort;this.g2match=g2match;this.g2fkeys=g2fkeys;',ctx);
      const sp={cols:[{k:'tal'},{k:'prtv'}]}; const c=sp.cols[1];
      const R=(id,kg,t)=>({id,v:{tal:id},s:{tal:id,prtv:t},ordk:{prtv:kg}});
      const kg=[R('A',1200,'1.200,00 kg/ha'),R('B',484.89,'484,89 kg/ha'),R('C','apurar','sc/ha a apurar')];
      const t=[R('A',1200,'1,20 t/ha'),R('B',484.89,'0,48 t/ha'),R('C','apurar','sc/ha a apurar')];
      const ord=ctx.g2sort(kg,sp,{so:{k:'prtv'}}).map(r=>r.id).join('');
      const chave=ctx.g2fkeys(t[1],c)[0]; const f={f:{prtv:[chave]}};
      console.log(JSON.stringify({ord, chave, kgB:kg.filter(r=>ctx.g2match(r,sp,f)).map(r=>r.id), tB:t.filter(r=>ctx.g2match(r,sp,f)).map(r=>r.id),
        mesma:ctx.g2fkeys(kg[1],c)[0]===ctx.g2fkeys(t[1],c)[0]}));'''
    r = subprocess.run(['node', '-e', js, os.path.join(HERE, 'g2lib.js')], capture_output=True, text=True, timeout=60)
    u = json.loads((r.stdout or 'null').strip().splitlines()[-1]) if r.stdout.strip() else None
    ok('U22a R-U11 ordenação pela chave em kg/ha: "484,89 kg/ha" antes de "1.200,00 kg/ha"; "a apurar" no fim (o texto punha 1.200 antes)', u and u['ord'] == 'BAC', [u, r.stderr[-300:]])
    ok('U22b R-U11 filtro por valor aplicado em t/ha continua achando a mesma linha em kg/ha (chave igual nas duas unidades)', u and u['mesma'] and u['kgB'] == ['B'] and u['tB'] == ['B'], u)
    # U23 · UNID-PROD R-U06 no Planejar safra (safra.js, regras sem tela): a meta guarda valor e unidade informados; o rascunho fixa a unidade
    # ao abrir (D-U20, RC-01); salvar com o texto mostrado não regrava (RC-02); trocas repetidas não derivam
    import ocupacao_cen as OCEN, cenario
    js23 = ('globalThis.localStorage=undefined;\n' + open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8').read() + '\n' + cenario.js_prefixo()
            + 'const GRIDS=[];const D2={unMeta:' + json.dumps(OCEN.UN_META, ensure_ascii=False) + '};\n' + open(os.path.join(HERE, 'safra.js'), encoding='utf-8').read() + r'''
const o={}; const G=(r,x)=>metaGravar(Object.assign({cult:'Soja'},r,x||{}));
o.p=metaRascunho('Soja',64,'sc/ha'); g2unidSet('Soja','t'); o.t=metaRascunho('Soja',64,'sc/ha'); o.tg=G(o.t);
g2unidSet('Soja','kg'); o.fixo=[metaUnTxt(Object.assign({cult:'Soja'},o.t)), G(o.t,{meta:'3,9'})];
g2unidSet('Soja','padrao'); o.r385=metaRascunho('Soja',3.85,'t/ha'); o.g385=G(o.r385);
let m={meta:3.85,unm:'t/ha'}; const ks=['t','kg','padrao']; for(let i=0;i<20;i++){ g2unidSet('Soja',ks[i%3]); const r=metaRascunho('Soja',m.meta,m.unm); m=G(r); }
o.deriva=m; g2unidSet('Soja','padrao'); o.tela=metaTela({v:{cult:'Soja',meta:3.85,unm:'t/ha'}});
o.un=[metaUnTxt({cult:'Soja',_un:'kg/ha'}),metaUnTxt({cult:'Soja',_un:'sc/ha'}),metaUnTxt({cult:'Mamão Formosa',_un:'kg/ha/ano'})];
console.log(JSON.stringify(o));''')
    p23 = os.path.join(HERE, '_probe', 'unidprod_saf_unit.js'); open(p23, 'w', encoding='utf-8').write(js23)
    r = subprocess.run(['node', p23], capture_output=True, text=True, timeout=60)
    o = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
    ok('U23a R-U06 meta do T1-A (64 sc/ha): no Padrão o painel abre "64"; com t/ha abre "3,84" em t/ha; salvar sem mexer mantém {64, sc/ha} (RC-02)',
       o.get('p', {}).get('meta') == '64' and o.get('t', {}).get('meta') == '3,84' and o.get('t', {}).get('_un') == 't/ha' and o.get('tg') == {'meta': 64, 'unm': 'sc/ha'}, [o.get('t'), o.get('tg'), r.stderr[-300:]])
    ok('U23b D-U20 rascunho aberto em t/ha: trocar a preferência para kg/ha não muda a unidade do campo; 3,9 grava {3,9, t/ha} (não 3.900 vezes, RC-01)',
       o.get('fixo') == ['t/ha · Padrão da cultura: sc/ha (60 kg)', {'meta': 3.9, 'unm': 't/ha'}], o.get('fixo'))
    ok('U23c 3,85 t/ha no Padrão abre "64,17" e salvar sem mexer mantém {3,85, t/ha}; 20 aberturas e salvamentos em t → kg → Padrão sem deriva; a tabela mostra "64,17 sc/ha"',
       o.get('r385', {}).get('meta') == '64,17' and o.get('g385') == {'meta': 3.85, 'unm': 't/ha'} and o.get('deriva') == {'meta': 3.85, 'unm': 't/ha'} and o.get('tela') == {'t': '64,17 sc/ha', 'k': 3850},
       [o.get('r385'), o.get('g385'), o.get('deriva'), o.get('tela')])
    ok('U23d campo "Unidade da meta": "kg/ha · Padrão da cultura: sc/ha (60 kg)"; no Padrão "sc/ha · Padrão da cultura"; mamão "kg/ha/ano · Padrão da cultura: t/ha/ano"',
       o.get('un') == ['kg/ha · Padrão da cultura: sc/ha (60 kg)', 'sc/ha · Padrão da cultura', 'kg/ha/ano · Padrão da cultura: t/ha/ano'], o.get('un'))
    # AC-j · fonte única do fator (ENG-011, R-U01): a segunda tabela (KG_UN do Planejar safra) e o × 1000 fixo do rascunho pela meta saíram
    saf = open(os.path.join(HERE, 'safra.js'), encoding='utf-8').read(); prj = open(os.path.join(HERE, 'producao.js'), encoding='utf-8').read()
    ok('AC-j fonte única: sem KG_UN no safra.js e sem o × 1000 fixo no rascunho; o Planejar safra converte pelo prUnpKgHa',
       'KG_UN' not in saf and 'prMul(prMul(k.area, k.meta), 1000)' not in prj and 'prUnpKgHa(' in saf, ['KG_UN' in saf, 'prUnpKgHa(' in saf])
    print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
    return all(OK)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
