# -*- coding: utf-8 -*-
"""UNID-PROD P5 · o rótulo da camada Colheita e produtividade (colhNum, areas/inicio.py) traz o indicador inteiro de prPrtvResTxt, com as
qualificações obrigatórias (R-U03 estimativa, R-U07 a apurar com a produtividade medida do estágio de campo), na unidade escolhida.
Achado do Codex no PR #133 (6262164118 e 4311323857): o split(' · ')[0] cortava "· estimativa" e, no café a apurar, a produtividade medida.
No node, sem navegador, com as regras reais (cenario.perfis_js() + cenario.js_prefixo()) e o colhNum extraído do gerador, sem alteração.
  C1 Mamão estimado em kg/ha: o rótulo = prPrtvResTxt inteiro e contém "estimativa"
  C2 Café a apurar em kg/ha: o rótulo = prPrtvResTxt inteiro, com "a apurar" e "1.200,00 kg/ha de Café da roça"
  C3 Mamão medido em t/ha (padrão): o rótulo = prPrtvResTxt, sem qualificação inventada
  C4 a mesma função do painel do talhão (colhKv) e da Previsão e colheita: nenhuma cópia da conta no Mapa
Contraprova: com o inicio.py do HEAD 77544fe2 (split), C1 e C2 reprovam.
Uso: SAFRION_DADOS=sintetico python3 -B mapa_colheita_unid_unit_test.py [caminho do inicio.py]"""
import os, sys, json, re, subprocess
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ARQ = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'areas', 'inicio.py')
OK = []
def ok(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + str(info)[:600]), flush=True)

src = open(ARQ, encoding='utf-8').read()
m = re.search(r'^function colhNum\(L,x\)\{.*$', src, re.M)
ok('C0 colhNum existe no gerador', bool(m), ARQ)
import cenario
CASOS = r"""
const PREF={}; function g2unidPref(c){ return PREF[c]||'padrao'; }   // a preferência do perfil × cultura (g2lib), aqui fixada por caso
const R=[]; const ok=(n,c,i)=>R.push({n,ok:!!c,info:c?'':JSON.stringify(i===undefined?'':i).slice(0,500)});
const L={c:null};
const caso=(cult,op,X)=>{ PREF[cult]=op; const x={k:{cultura:cult},R:X,sit:'Em colheita'}; return {rot:colhNum(L,x), ref:prPrtvResTxt(cult,X,op)}; };
try{
  const a=caso('Mamão Formosa','kg',{comecou:true,kg:1000,area:2,estim:true,apurar:false});
  ok('C1 Mamão estimado em kg/ha: o rótulo é o indicador inteiro e diz "estimativa"', a.rot===a.ref&&/estimativa/.test(a.rot)&&/kg\/ha/.test(a.rot), a);
  const b=caso('Café','kg',{comecou:true,kg:0,area:2,estim:false,apurar:true,litros:2400,liq:2400,kgOk:true});
  ok('C2 Café a apurar em kg/ha: "a apurar" e a produtividade medida do campo ("1.200,00 kg/ha de Café da roça")', b.rot===b.ref&&/a apurar/.test(b.rot)&&b.rot.indexOf('1.200,00 kg/ha de Café da roça')>=0, b);
  const d=caso('Mamão Formosa','padrao',{comecou:true,kg:2000,area:2,estim:false,apurar:false});
  ok('C3 Mamão medido na unidade padrão: o rótulo é o indicador, sem qualificação inventada', d.rot===d.ref&&!/estimativa|apurar/.test(d.rot), d);
}catch(e){ R.push({n:'exceção',ok:false,info:String(e&&e.stack||e).slice(0,500)}); }
console.log(JSON.stringify(R));
"""
if m:
    js = 'globalThis.print=(...a)=>console.log(...a);\n' + cenario.perfis_js() + cenario.js_prefixo() + m.group(0) + '\n' + CASOS
    os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True)
    p = os.path.join(HERE, '_probe', 'mapa_colheita_unid_unit.js'); open(p, 'w', encoding='utf-8').write(js)
    r = subprocess.run(['node', p], capture_output=True, text=True, timeout=120)
    out = r.stdout.strip().splitlines()
    ok('motor JS (node) executou sem erro', r.returncode == 0 and out, r.stderr[-600:])
    for x in (json.loads(out[-1]) if out else []): ok(x['n'], x['ok'], x['info'])
    ok('C4 colhNum usa prPrtvResTxt (a função do painel do talhão e da Previsão e colheita), sem cópia da conta', 'prPrtvResTxt(' in m.group(0) and 'prPrtvResTxt(' in src[src.index('function colhKv('):src.index('function colhKv(') + 600])
print(f'RESULTADO: {"OK" if all(OK) else "FALHOU"} {sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
