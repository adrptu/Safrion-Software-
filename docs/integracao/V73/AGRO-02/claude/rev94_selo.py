# -*- coding: utf-8 -*-
"""rev94 · achado A2: selo do produto escolhido na decisão (agDec real, sem navegador). Dados sintéticos. Uso: python3 -B rev94_selo.py <gen37>
Roda o agDec do AG-01 na VIS-013 com o 1º produto escolhido e dose '', '0', '0,' e válida; depois o mesmo com a correção proposta
(selo neutro "Informe a dose" quando a dose do escolhido não é > 0), aplicada só em memória."""
import os, sys, json, subprocess, tempfile
G = os.path.abspath(sys.argv[1]); os.chdir(G); sys.path.insert(0, G)
src = open(os.path.join(G, 'quantidade_test.py'), encoding='utf-8').read(); ns = {}
exec(src[src.index('LS = ('):src.index('JS_FLUXO = r"""')], ns)
import cenario, dados_mip, dados_irrigacao
from areas.processo_os import JS_NUCLEO
import areas.agronomia as AG
PRE = 'globalThis.print=(...a)=>console.log(...a);\n'
G2C = next(l for l in open(os.path.join(G, 'g2lib.js'), encoding='utf-8') if l.startswith('const G2C='))   # cores reais dos selos (g2lib.js)
DOM = 'globalThis.document={getElementById:()=>null,querySelector:()=>null};globalThis.setTimeout=()=>0;\n' + G2C
CINZA = json.loads(G2C[G2C.index('gray:') + 5:].split(']')[0].replace("'", '"') + ']')[1]
ANTES = "const cc=tt.length?[tt[0],'red']:(ta.length?[ta.slice(0,2).join(' · '),'yellow']:['Conferido','green']);"
DEPOIS = "const cc=(sel&&!(num(d.dose)>0))?['Informe a dose','gray']:(tt.length?[tt[0],'red']:(ta.length?[ta.slice(0,2).join(' · '),'yellow']:['Conferido','green']));"
JS = r"""
const out=[]; let st=null; const self={state:{},setState:x=>{ st=Object.assign({},st||{},x); self.state=st; }};
agDecIni(self,'VIS-013'); const L=mipElig(mipGet().vis['VIS-013']); const u0=L[0];
for(const dose of ['','0','0,','abc',String((u0.dmin+u0.dmax)/2).replace('.',',')]){ self.state=Object.assign({},self.state,{dec:Object.assign({},self.state.dec,{prod:u0.id,dose})});
  const v={}; agDec(self,v); const row=v.dc_prods.find(x=>x.nome===u0.nome); out.push({dose,selo:row.cht,cor:/background:#?[^;]*/.exec(row.chst)[0],bloq:v.dc_bloq,tr:v.dc_tr.map(x=>x.t)}); }
const v={}; self.state=Object.assign({},self.state,{dec:Object.assign({},self.state.dec,{prod:'',dose:''})}); agDec(self,v);
out.push({dose:'(nenhum escolhido)',selos:v.dc_prods.map(x=>x.nome+': '+x.cht)});
print(JSON.stringify(out));
"""
def roda(ag):
    f = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8')
    f.write(PRE + ns['LS'] + DOM + cenario.perfis_js() + cenario.js_prefixo() + JS_NUCLEO + dados_mip.js_prefixo() + dados_irrigacao.js_prefixo() + ag + JS); f.close()
    p = subprocess.run(['node', f.name], capture_output=True, text=True, timeout=300); os.unlink(f.name)
    if p.returncode: print(p.stderr[-1500:]); sys.exit(2)
    return json.loads(p.stdout.strip().splitlines()[-1])
OK = []
def chk(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHOU ') + nome + ' · ' + json.dumps(info, ensure_ascii=False)[:400], flush=True)
a = roda(AG.JS_AG01)
for x in a[:4]: chk(f'HEAD: produto escolhido com dose {x["dose"]!r} não mostra "Conferido"', x['selo'] != 'Conferido', x)
chk(f'HEAD: dose válida {a[4]["dose"]} mantém o selo da conferência', a[4]['selo'] != 'Informe a dose', a[4])
print('  sem escolha:', a[5]['selos'])
if AG.JS_AG01.count(ANTES) != 1:   # novo HEAD com outra forma do trecho: só as verificações do HEAD valem
    print('trecho original do selo ausente: a correção em memória não se aplica'); print(f'RESULTADO {sum(OK)}/{len(OK)}'); sys.exit(0 if all(OK) else 1)
b = roda(AG.JS_AG01.replace(ANTES, DEPOIS))
for x in b[:4]: chk(f'correção proposta: dose {x["dose"]!r} → selo neutro "Informe a dose" e emissão bloqueada', x['selo'] == 'Informe a dose' and x['cor'].lower() == 'background:' + CINZA.lower() and x['bloq'] is True, x)
chk(f'correção proposta: dose válida {b[4]["dose"]} → mesmo selo do HEAD ({a[4]["selo"]})', b[4]['selo'] == a[4]['selo'], [a[4], b[4]])
chk('correção proposta: sem escolha, os selos de prévia não mudam', b[5] == a[5], [a[5], b[5]])
print(f'RESULTADO {sum(OK)}/{len(OK)}'); sys.exit(0 if all(OK) else 1)
