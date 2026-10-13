# uso: mutar.py <nome> <arquivo relativo ao gen37 do mutante> <antes> <depois> -- <comando do teste...>
# aplica a troca (exatamente 1 ocorrência) no gen37 do mutante, roda o teste na trava cdpB, guarda o log e restaura o arquivo
import sys, os, subprocess, shutil, time
S='/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera'; G=S+'/mut/v37/gen37'
a=sys.argv; i=a.index('--'); nome,arq,antes,depois=a[1:5]; cmd=a[i+1:]
f=os.path.join(G,arq); orig=open(f,encoding='utf-8').read(); n=orig.count(antes)
bk={p:open(p,'rb').read() for p in (os.path.join(G,'project',os.path.basename(arq)),os.path.join(G,'_render',os.path.basename(arq))) if os.path.exists(p)}   # o teste pode copiar project → _render
if n!=1 and not (os.environ.get('MUT_TODAS') and n>=1): sys.exit(f'{nome}: {n} ocorrências de {antes[:60]!r} em {arq}')
print(f'{nome}: {n} troca(s) em {arq}',flush=True)
open(f,'w',encoding='utf-8').write(orig.replace(antes,depois))
os.makedirs(S+'/mutantes',exist_ok=True); log=S+f'/mutantes/{nome}.log'
try:
    env=dict(os.environ,CHROME_BIN='/tmp/cloudchrome/chrome',CDP_GL='1',SAFRION_DADOS='sintetico')
    t=time.time(); r=subprocess.run(['flock','/tmp/cdpB.lock','timeout','900','python3']+cmd,cwd=G,env=env,stdout=open(log,'w'),stderr=subprocess.STDOUT)
    linhas=[l.rstrip() for l in open(log,encoding='utf-8',errors='replace') if l.startswith(('FALHA','  FALHOU','FALHOU','RESULTADO','Traceback'))or ' ok · ' in l]
    print(f'{nome} rc={r.returncode} {time.time()-t:.0f}s ::',' || '.join(x[:230] for x in linhas[-4:]))
finally:
    open(f,'w',encoding='utf-8').write(orig)
    for p,b in bk.items(): open(p,'wb').write(b)
