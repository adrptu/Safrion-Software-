import sys, os, time, subprocess, json
G=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,G)
from cdp import Chrome
from journeys import free
R=os.path.join(G,'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
c=None
try:
    c=Chrome(port=free()); J=c.js
    def clk(t,root=None,w=.45): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(w); return r
    W=int(sys.argv[1]) if len(sys.argv)>1 else 1440
    c.size(W,1000); c.goto(f'http://127.0.0.1:{p}/CMP.dc.html'); time.sleep(.6)
    c.shot(f'_probe/cmp_{W}_e1.png')
    clk('Abrir compra'); c.shot(f'_probe/cmp_{W}_e2.png')
    clk('Solicitar cotações'); c.shot(f'_probe/cmp_{W}_e3a.png')
    clk('Enviar convites (simulado)'); time.sleep(2.2); c.shot(f'_probe/cmp_{W}_e3b.png'); time.sleep(4.5)
    clk('Comparar propostas'); time.sleep(.3); c.shot(f'_probe/cmp_{W}_e4.png')
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/MAP 11-52/.test(r.innerText)); r.querySelector('[role=cell] b').click();})()"); time.sleep(.5)
    c.shot(f'_probe/cmp_{W}_e4form.png'); clk('Cancelar','aside[role=dialog]')
    clk('Revisar aprovação'); c.shot(f'_probe/cmp_{W}_e5.png')
    clk('Enviar à Direção'); clk('Registrar aprovação da Direção'); time.sleep(.3); c.shot(f'_probe/cmp_{W}_e5b.png')
    clk('Acompanhar entrega'); c.shot(f'_probe/cmp_{W}_e6.png')
finally:
    if c: c.close()
    srv.terminate()
