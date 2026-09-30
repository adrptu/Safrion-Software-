import sys,os,time,subprocess,socket,json
sys.path.insert(0,'.')
from cdp import Chrome
def _free():
    s=socket.socket(); s.bind(('127.0.0.1',0)); x=s.getsockname()[1]; s.close(); return x
D=sys.argv[1] if len(sys.argv)>1 else '_render'
port=_free(); srv=subprocess.Popen(['python3','-m','http.server',str(port),'--bind','127.0.0.1','--directory',D],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=_free())
try:
  c.size(1440,900); c.goto(f'http://127.0.0.1:{port}/SAF.dc.html',wait=1.2)
  c.js("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/^Abrir safra/.test(b.innerText.trim())); b&&b.click();})()"); time.sleep(.5)
  r=c.js("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/^Soja alta tecnologia v6/.test(b.innerText.trim())); if(!b) return 'sem botão'; b.click(); return 'ok';})()"); time.sleep(.6)
  print('abrir:',r)
  out=c.js("""(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return 'sem painel';
    const cards=[...a.querySelectorAll('div')].filter(d=>getComputedStyle(d).overflow==='hidden'&&getComputedStyle(d).borderRadius==='12px');
    return {aside:[a.clientHeight,a.scrollHeight], cards:cards.map(d=>{const t=d.querySelector('b'); return (t?t.innerText:'?')+' '+d.clientHeight+'/'+d.scrollHeight+' shrink='+getComputedStyle(d).flexShrink;})};})()""")
  print(json.dumps(out,ensure_ascii=False,indent=0))
  c.shot('_probe/lp_antes.png')
  print('cadeia:',c.js("(()=>{const a=document.querySelector('aside[role=dialog]'); const d=[...a.querySelectorAll('div')].find(x=>getComputedStyle(x).overflow==='hidden'); const ch=[]; let p=d.parentElement; while(p&&p!==a){ch.push(p.tagName.toLowerCase()); p=p.parentElement;} return ch.join(' < ');})()"))
  CSS=open('_probe/fix.css').read()
  c.js("(()=>{const st=document.createElement('style'); st.textContent="+json.dumps(CSS)+"; document.head.appendChild(st);})()"); time.sleep(.3)
  out=c.js("""(()=>{const a=document.querySelector('aside[role=dialog]'); const cards=[...a.querySelectorAll('div')].filter(d=>getComputedStyle(d).overflow==='hidden'&&getComputedStyle(d).borderRadius==='12px');
    return {aside:[a.clientHeight,a.scrollHeight], cards:cards.map(d=>{const t=d.querySelector('b'); return (t?t.innerText:'?')+' '+d.clientHeight+'/'+d.scrollHeight;})};})()""")
  print('depois:',json.dumps(out,ensure_ascii=False))
  c.shot('_probe/lp_depois.png')
finally:
  c.close(); srv.terminate()
