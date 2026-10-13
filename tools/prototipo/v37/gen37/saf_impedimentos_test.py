# -*- coding: utf-8 -*-
"""CONTROLE-02 F2 · adaptador de impedimentos da publicação da referência técnica (safImpedimentosRef, mapa no PR #58 6152055144).
Recusa só o que já trava no Planejar safra (sobreposição de ocupação e plano de outra cultura); sem plano, "A conferir" e sugestões das
análises são avisos. Contraprovas: a sobreposição e o plano incompatível são injetados no estado da tela (como o S3.4 do saf_revisao_test)
e passam a recusar; sem eles, nada recusa. Conferido também: o adaptador não escreve na grade nem no cenário (puro).
Uso: python3 saf_impedimentos_test.py (lê _render)."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome
import saf_nav_lib as L
from saf_nav_lib import *   # chk, abre, clica_linha, salvar, FAIL, OK
IMP = "JSON.stringify(window.__safRef.impedimentos('%s'))"
ESTADO = "JSON.stringify([window.__safSelf.state.g2, (JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'{}').rev||0)])"
try:
    c = L.c = Chrome()
    abre('#saf=S2627&passo=cultivos'); r = json.loads(c.js(IMP % 'S2627'))
    chk('I1 semente S2627: nenhum impedimento; avisos dizem os 4 sem plano (fora da referência), 1 a conferir e 4 sugestões opcionais',
        r['impedimentos'] == [] and any('4 cultivos sem plano ficam fora da referência (T4, T3, P1, P2)' in a for a in r['avisos'])
        and any('a conferir' in a for a in r['avisos']) and any('sugestões das análises de solo' in a for a in r['avisos']), r)
    e0 = c.js(ESTADO); c.js(IMP % 'S2627'); c.js(IMP % 'S27SF')
    chk('I2 o adaptador é puro: a grade e a revisão do cenário não mudam ao calcular', c.js(ESTADO) == e0)
    # contraprova 1: sobreposição (estado antigo injetado, como o S3.4)
    abre('#saf=S27SF&passo=cultivos'); clica_linha('d2'); salvar()
    r0 = json.loads(c.js(IMP % 'S27SF'))
    c.js("""(()=>{const s=window.__safSelf; const g=Object.assign({},s.state.g2['g_cult_S27SF']); const rs=JSON.parse(JSON.stringify(g.rows));
      rs.push({id:'x9',v:{talhao:'T1',faz:'Santa Rita',local:'T1-B',tipo:'Parcela',cult:'Soja',var:'62 X',area:152,plantio:'2027-02-10',meta:60,unm:'sc/ha',plano:'SOJA-AT',colheita:''},s:{},p:{}});
      g.rows=rs; s.setState({g2:Object.assign({},s.state.g2,{g_cult_S27SF:g})}); return 'ok';})()""")
    import time; time.sleep(.8); r1 = json.loads(c.js(IMP % 'S27SF'))
    chk('I3 contraprova: sem a sobreposição não recusa; com ela, recusa "Sobreposição em T1" (a mesma trava da etapa 2)',
        r0['impedimentos'] == [] and any(x.startswith('Sobreposição em T1') for x in r1['impedimentos']), [r0, r1])
    # contraprova 2: plano de outra cultura (Milho com o plano da Soja)
    abre('#saf=S27SF&passo=cultivos'); clica_linha('d2'); salvar()
    alvo = c.js("(()=>{const rs=window.__safSelf.state.g2['g_cult_S27SF'].rows; const f=[]; const w=x=>{ (x.kids||[]).forEach(w); if(!x.grp&&x.v&&x.v.cult==='Milho') f.push(x.id); }; rs.forEach(w); return f[0]||'';})()")
    c.js("""(()=>{const s=window.__safSelf; const g=Object.assign({},s.state.g2['g_cult_S27SF']); const rs=JSON.parse(JSON.stringify(g.rows));
      const w=x=>{ (x.kids||[]).forEach(w); if(x.id===%s) x.v.plano='SOJA-AT'; }; rs.forEach(w); g.rows=rs; s.setState({g2:Object.assign({},s.state.g2,{g_cult_S27SF:g})}); return 'ok';})()""" % json.dumps(alvo))
    time.sleep(.8); r2 = json.loads(c.js(IMP % 'S27SF'))
    chk('I4 contraprova: cultivo de Milho com o plano da Soja recusa ("plano de Soja num cultivo de Milho")',
        bool(alvo) and any('plano de Soja num cultivo de Milho' in x for x in r2['impedimentos']), [alvo, r2])
    chk('I5 contrato do comando (PR #58): impedimentos é lista de textos não vazios', all(isinstance(x, str) and x.strip() for x in r1['impedimentos'] + r2['impedimentos']))
finally:
    try: c.close()
    except Exception: pass
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
