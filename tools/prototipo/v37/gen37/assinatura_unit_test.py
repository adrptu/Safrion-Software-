# -*- coding: utf-8 -*-
"""PLAT-01 · executor do assinatura_unit.js (regras da assinatura, sem navegador). Roda duas vezes no node (Linux/nuvem) ou no jsc (macOS):
(A) cenario.js + assinatura (prefixo do engine) + base do cadastro + talgeo.js + talmapa.js, como no CF-05, no BO-02 e no Mapa;
(B) só o prefixo do engine, como nas telas sem cenario.js (CD-01, CMP, PA). Expectativas em Python com Decimal a partir das mesmas linhas
do cadastro; com a Lagoa Grande sintética elas são os números da especificação (§6). Uso: python3 assinatura_unit_test.py"""
import os, sys, json, subprocess, tempfile
from decimal import Decimal
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MOTOR, PRELUDIO = ([JSC], '') if os.path.exists(JSC) else (['node'], 'globalThis.print=(...a)=>console.log(...a);\n')
SHIM = ("globalThis.localStorage=(()=>{const m=new Map();return{getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k),clear:()=>m.clear()};})();\n"
        "globalThis.window=globalThis; if(!globalThis.addEventListener) globalThis.addEventListener=()=>{};\n")
import cenario, dados_assinatura as DA, dados_lagoa_fonte as LF
import areas.inicio as I
base = DA.cad0(); med, n = DA.medir(base); v2 = int((med / 100).to_integral_value(rounding='ROUND_CEILING') * 100)
m50 = med + 50
def mens(p, m, c): return str(DA.mensalidade(p, m, c)[1])
vig = DA.mensalidade('comp', med, v2)[1] + Decimal('299') + Decimal('199') + Decimal('640')
vig50 = DA.mensalidade('comp', m50, v2)[1] + Decimal('299') + Decimal('199') + Decimal('640')
EXP = dict(med=str(med), n=n, v2=v2, comp=mens('comp', med, v2), ess=mens('ess', med, v2), med50=str(m50), comp50=mens('comp', m50, v2), amp=mens('comp', m50, v2 + 100),
           vig=str(vig), vig50=str(vig50), cob=str(min(med, v2) + 35 + 20 + 320), medT=str(med + 35 + 20 + 333))
FALHAS = []
if LF.ROTULO:   # Lagoa Grande sintética: os números da especificação (§6)
    esp = dict(med='2570.23', n=32, v2=2600, comp='5140.46', ess='3855.35', med50='2620.23', comp50='5200.00', amp='5240.46', vig='6278.46', vig50='6338.00', cob='2945.23', medT='2958.23')
    dif = {k: (EXP[k], v) for k, v in esp.items() if str(EXP[k]) != str(v)}
    print(('OK   ' if not dif else 'FALHA') + ' S0 com a Lagoa sintética os números batem com a especificação §6 (2.570,23 ha · 5.140,46 · 3.855,35 · 5.200,00 · 5.240,46 · 6.278,46 · 6.338,00 · 2.945,23 ha)' + ('' if not dif else ' · ' + str(dif)))
    if dif: FALHAS.append('S0')
M = dict(cad0=I._cad0(), hoje_iso='2026-09-23', lg=dict(pivos=[]))
CAB = 'const EXP = ' + json.dumps(EXP) + ';\n'
A = (PRELUDIO + SHIM + cenario.js_prefixo() + DA.js_prefixo() + DA.js_cad0() + CAB
     + 'const M = ' + json.dumps(M, ensure_ascii=False) + ';\nfunction nfx(n,d){ return Number(n||0).toLocaleString("pt-BR",{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }\nfunction isLG(t){ return String(t).indexOf("PV")===0; }\n'
     + open('talgeo.js', encoding='utf-8').read() + '\n' + open('talmapa.js', encoding='utf-8').read() + '\n' + open('assinatura_unit.js', encoding='utf-8').read())
B = PRELUDIO + SHIM + DA.js_prefixo() + CAB + open('assinatura_unit.js', encoding='utf-8').read()
tot = 0
for nome, src in (('A', A), ('B', B)):
    fd, p = tempfile.mkstemp(prefix='assin_' + nome + '_', suffix='.js')
    with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
    try: r = subprocess.run(MOTOR + [p], capture_output=True, text=True, timeout=120)
    finally: os.unlink(p)
    print(f'--- ({nome}) ' + ('com cenario.js' if nome == 'A' else 'sem cenario.js'))
    print(r.stdout, end='')
    linhas = r.stdout.strip().splitlines(); t = [l for l in linhas if l.startswith('TOTAL ')]
    if r.returncode or not t: print('FALHA motor JS não terminou:', r.stderr[-1500:]); FALHAS.append(nome + ':motor'); continue
    FALHAS += [l for l in linhas if l.startswith('FALHA')]; tot += int(t[-1].split()[1])
print('RESULTADO', 'falhou' if FALHAS else 'passou', f'· {tot} verificações JS · falhas {len(FALHAS)}')
sys.exit(1 if FALHAS else 0)
