# cria cópias de 2e31588 (src/c2e3) com cada proposta, JS e Python iguais; cada troca é conferida (exatamente 1 ocorrência)
import shutil,os,sys,subprocess
W=sys.argv[1]; BASE=W+'/src/c2e3'; G='tools/prototipo/v37/gen37'
def troca(txt,a,b,nome):
    n=txt.count(a); assert n==1,(nome,n,a[:80]); return txt.replace(a,b)
JS_TETO="const ext=(c,v0)=>{ if(++passos>65536) return null;"
PY_TETO="            if st['passos']>65536: return None"
JS_CALL="let h=buraco(cf0,adj); if(h===false) h=buraco(cf0,adj.map((r,a)=>r.map((e,b)=>a!==b&&!e)));"
PY_CALL=("h=buraco(cf0,adj)   # só quem tem janela (R2-2)\n"
         "                if h is False: h=buraco(cf0,[[a!=b and not adj[a][b] for b in range(n)] for a in range(n)])")
JS_GRAFO="  const grafo=(V,pref,S)=>{ const n=V.length;"
PY_GRAFO="    def grafo(V,pref,S):\n"
JS_LB=("  // P2: grafo de linhas de um bipartido (trator × implemento) é perfeito (Kőnig), sem busca: exclusão só por ativo em comum, cada\n"
"  // configuração com até dois ativos compartilhados (entre as de cs) e esses ativos 2-coloríveis; senão, a busca de buraco decide\n"
"  const linhaBip=(cs,A,V)=>{ const sh=(a,b)=>V[a].ativos.some(z=>V[b].ativos.indexOf(z)>=0);\n"
"    for(let a=0;a<cs.length;a++) for(let b=a+1;b<cs.length;b++) if(A[cs[a]][cs[b]]!==sh(cs[a],cs[b])) return false;\n"
"    const un=(l)=>l.filter((z,j)=>l.indexOf(z)===j); const cnt=new Map(); cs.forEach(i=>un(V[i].ativos).forEach(z=>cnt.set(z,(cnt.get(z)||0)+1)));\n"
"    const viz=new Map(); for(const i of cs){ const s=un(V[i].ativos).filter(z=>cnt.get(z)>1); if(s.length>2) return false;\n"
"      if(s.length===2){ if(!viz.has(s[0])) viz.set(s[0],[]); if(!viz.has(s[1])) viz.set(s[1],[]); viz.get(s[0]).push(s[1]); viz.get(s[1]).push(s[0]); } }\n"
"    const cor=new Map(); for(const z0 of viz.keys()){ if(cor.has(z0)) continue; cor.set(z0,0); const pl=[z0];\n"
"      while(pl.length){ const z=pl.pop(); for(const w of viz.get(z)){ if(!cor.has(w)){ cor.set(w,1-cor.get(z)); pl.push(w); } else if(cor.get(w)===cor.get(z)) return false; } } }\n"
"    return true; };\n")
PY_LB=("    def linha_bip(cs,A,V):   # P2: grafo de linhas de um bipartido é perfeito (Kőnig), sem busca; senão, a busca de buraco decide (como no safra.js)\n"
"        def sh(a,b): return any(z in V[b]['ativos'] for z in V[a]['ativos'])\n"
"        for ia in range(len(cs)):\n"
"            for ib in range(ia+1,len(cs)):\n"
"                if A[cs[ia]][cs[ib]]!=sh(cs[ia],cs[ib]): return False\n"
"        def un(l): return [z for j,z in enumerate(l) if l.index(z)==j]\n"
"        cnt={}\n"
"        for i in cs:\n"
"            for z in un(V[i]['ativos']): cnt[z]=cnt.get(z,0)+1\n"
"        viz={}\n"
"        for i in cs:\n"
"            s=[z for z in un(V[i]['ativos']) if cnt[z]>1]\n"
"            if len(s)>2: return False\n"
"            if len(s)==2: viz.setdefault(s[0],[]).append(s[1]); viz.setdefault(s[1],[]).append(s[0])\n"
"        cor={}\n"
"        for z0 in viz:\n"
"            if z0 in cor: continue\n"
"            cor[z0]=0; pl=[z0]\n"
"            while pl:\n"
"                z=pl.pop()\n"
"                for w in viz[z]:\n"
"                    if w not in cor: cor[w]=1-cor[z]; pl.append(w)\n"
"                    elif cor[w]==cor[z]: return False\n"
"        return True\n")
SO=sys.argv[2:]   # opcional: só estas variantes
def variante(nome,fjs,fpy):
    if SO and nome not in SO: return
    d=W+'/var/'+nome
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree(BASE,d)
    for f,fn in ((G+'/safra.js',fjs),(G+'/dados2.py',fpy)):
        p=d+'/'+f; t=open(p).read(); open(p,'w').write(fn(t))
    shutil.rmtree(d+'/'+G+'/__pycache__',ignore_errors=True)
    r=subprocess.run(['diff','-u',BASE+'/'+G+'/safra.js',d+'/'+G+'/safra.js'],capture_output=True,text=True).stdout
    r+=subprocess.run(['diff','-u',BASE+'/'+G+'/dados2.py',d+'/'+G+'/dados2.py'],capture_output=True,text=True).stdout
    open(W+'/var/'+nome+'.diff','w').write(r); print(nome,'ok',len(r.splitlines()),'linhas de diff')
for e,nm in ((18,'p1_2e18'),(20,'p1_2e20'),(22,'p1_2e22')):
    variante(nm,lambda t,e=e:troca(t,JS_TETO,JS_TETO.replace('65536',str(1<<e)),'js teto'),lambda t,e=e:troca(t,PY_TETO,PY_TETO.replace('65536',str(1<<e)),'py teto'))
P2JS=lambda t:troca(troca(t,JS_GRAFO,JS_LB+JS_GRAFO,'js lb'),JS_CALL,"const lb=linhaBip(cf0,adj,V); let h=lb?false:buraco(cf0,adj); if(h===false&&!lb) h=buraco(cf0,adj.map((r,a)=>r.map((e,b)=>a!==b&&!e)));",'js call')
P2PY=lambda t:troca(troca(t,PY_GRAFO,PY_LB+PY_GRAFO,'py lb'),PY_CALL,"lb=linha_bip(cf0,adj,V); h=False if lb else buraco(cf0,adj)   # só quem tem janela (R2-2); linhas de bipartido: perfeito sem busca (P2)\n                if h is False and not lb: h=buraco(cf0,[[a!=b and not adj[a][b] for b in range(n)] for a in range(n)])",'py call')
variante('p2',P2JS,P2PY)
variante('cliq',lambda t:troca(t,JS_CALL,"let h=false;   /* MEDIÇÃO: caminho de cliques forçado */",'js cliq'),
                lambda t:troca(t,PY_CALL,"h=False   # MEDIÇÃO: caminho de cliques forçado\n                if False: pass",'py cliq'))
# P2u (derivada, para o achado N1): P2 só quando quem tem janela no componente tem UM prazo (König vale para prazo único); senão, a busca decide
JS_U="  const linhaBip=(cs,A,V)=>{ const sh=(a,b)=>V[a].ativos.some(z=>V[b].ativos.indexOf(z)>=0);\n"
PY_U="    def linha_bip(cs,A,V):   # P2: grafo de linhas de um bipartido é perfeito (Kőnig), sem busca; senão, a busca de buraco decide (como no safra.js)\n"
variante('p2u',lambda t:troca(P2JS(t),JS_U,JS_U+"    if(new Set(cs.map(i=>V[i].H)).size>1) return false;   // P2u: só prazo único\n",'js p2u'),
               lambda t:troca(P2PY(t),PY_U,PY_U+"        if len({V[i]['H'] for i in cs})>1: return False   # P2u: só prazo único\n",'py p2u'))
