import sys, os, time, subprocess, json
G=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,G)
from cdp import Chrome
from journeys import free
R=os.path.join(G,'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
W="""(()=>{return [...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).map(t=>({w:t.scrollWidth,pw:t.parentElement.clientWidth,cols:getComputedStyle(t).gridTemplateColumns}));})()"""
c=None
try:
    c=Chrome(port=free()); J=c.js
    def clk(t,root=None,w=.45): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(w); return r
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/CMP.dc.html'); time.sleep(.6)
    print('e1',J(W)); clk('Abrir compra'); print('e2',J(W)); clk('Solicitar cotações'); clk('Enviar convites (simulado)'); time.sleep(6.5); print('e3',J(W))
    clk('Comparar propostas'); print('e4',J(W)); clk('Revisar aprovação'); print('e5',J(W)); clk('Enviar à Direção'); clk('Registrar aprovação da Direção'); clk('Acompanhar entrega'); print('e6',J(W))
    clk('1 Escolha a safra'); clk('Consultar pedidos'); print('e6-2526',J(W))
finally:
    if c: c.close()
    srv.terminate()
