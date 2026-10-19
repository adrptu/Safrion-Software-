# Gera cópias de gen37 (2e31588) com as variantes P1, P2 e P0nR23 (só diagnóstico: sem a ordem R2-3). JS e Python iguais.
import os, shutil, sys
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE=os.path.join(W,'src','2e31588','tools','prototipo','v37','gen37')
def sub(t,a,b):
    assert t.count(a)==1, ('âncora', a[:80], t.count(a)); return t.replace(a,b)
# ---- âncoras (2e31588) ----
JS_LOOP_END="cz.seq=1; cortes.push(g); liga[g]=1; } });\n"
PY_LOOP_END="                cz['seq']=1; cortes.append(g); liga[g]=1\n"
# P1: devolução de folga depois do laço das partes fixas (antes dos motivos, que dizem a fração final)
JS_P1=JS_LOOP_END+"""    // P1 (variante): devolve a folga liberada por um corte posterior, sem passar da própria janela nem de nenhuma restrição dela
    fx.forEach(x=>{ if(x.r===null||!(q[x.i]<cab[x.i]-1e-12)) return; let fol=(cab[x.i]-q[x.i])/x.r;
      pl(x).forEach(g=>{ const u=pistaA[g].filter(y=>y.p!==null).reduce((a,y)=>a+q[y.i]/y.r,0); fol=Math.min(fol,Math.max(0,jan[g]-u)); });
      if(fol>1e-12){ q[x.i]+=x.r*fol; saldo-=x.r*fol; } });
"""
PY_P1=PY_LOOP_END+"""        for x in fx:   # P1 (variante): devolve a folga liberada por um corte posterior
            if x['r'] is None or not (q[x['i']]<cab[x['i']]-1e-12): continue
            fol=(cab[x['i']]-q[x['i']])/x['r']
            for g in pl(x):
                u=sum((q[y['i']]/y['r'] for y in pista_a[g] if y['p'] is not None),0); fol=min(fol,max(0,jan[g]-u))
            if fol>1e-12: q[x['i']]+=x['r']*fol; saldo-=x['r']*fol
"""
# P2: a restrição antiga (sq/at:/pl:) não entra na divisão quando um corte da divisão tem os mesmos membros e o mesmo prazo
JS_A2="  const W={}, jan={}, pista={}, pistaA={}, TRC={}, SUB={}, MS={}, EC={}, OC={};\n"
JS_P2="""  { const ch=xs=>xs.map(x=>x.i).sort((a,b)=>a-b).join(','); const cs={};   // P2 (variante)
    RS.forEach(r=>{ if(r[3]!==undefined&&r[2].length>1) cs[ch(r[2])+'@'+r[3]]=1; });
    RS.forEach((r,j)=>{ if(r[3]!==undefined||r[2].length<2) return; const w=Math.max.apply(null,r[1].concat(r[2]).map(x=>x.H)); if(isFinite(w)&&cs[ch(r[2])+'@'+w]) RS[j]=[r[0],r[1],[]]; }); }
"""+JS_A2
PY_A2="    W={}; jan={}; pista={}; pista_a={}; TRC={}; SUB={}; MS={}; EC={}; OC={}\n"
PY_P2="""    _ch=lambda xs: ','.join(str(i) for i in sorted(x['i'] for x in xs)); _cs=set()   # P2 (variante)
    for r_ in RS:
        if len(r_)>3 and len(r_[2])>1: _cs.add((_ch(r_[2]),r_[3]))
    for j,r_ in enumerate(RS):
        if len(r_)>3 or len(r_[2])<2: continue
        w=max((x['H'] for x in r_[1]+r_[2]))
        if w!=_math.inf and (_ch(r_[2]),w) in _cs: RS[j]=(r_[0],r_[1],[])
"""+PY_A2
# P0nR23: diagnóstico, ordem de Object.keys(jan) como em 04bf6f2
JS_O="const gs=Object.keys(jan); gs.filter(g=>!SUB[g]).concat(gs.filter(g=>SUB[g])).forEach(g=>{"
JS_On="const gs=Object.keys(jan); gs.forEach(g=>{"
PY_O="        for g in [g for g in jan if not SUB[g]]+[g for g in jan if SUB[g]]:"
PY_On="        for g in list(jan):"
VAR={'P1':[(JS_LOOP_END,JS_P1,PY_LOOP_END,PY_P1)],'P2':[(JS_A2,JS_P2,PY_A2,PY_P2)],'P0nR23':[(JS_O,JS_On,PY_O,PY_On)],
     'P2nR23':[(JS_A2,JS_P2,PY_A2,PY_P2),(JS_O,JS_On,PY_O,PY_On)]}   # P2nR23: só diagnóstico (P2 sem a ordem R2-3)
for v,ps in VAR.items():
    d=os.path.join(W,'var',v,'gen37')
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree(BASE,d)
    js=open(os.path.join(d,'safra.js')).read(); py=open(os.path.join(d,'dados2.py')).read()
    for a,b,c,e in ps: js=sub(js,a,b); py=sub(py,c,e)
    open(os.path.join(d,'safra.js'),'w').write(js); open(os.path.join(d,'dados2.py'),'w').write(py)
    print(v,'ok',d)
