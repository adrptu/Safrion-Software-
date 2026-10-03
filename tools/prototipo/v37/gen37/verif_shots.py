# -*- coding: utf-8 -*-
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(HERE,'_render'); PR=os.path.join(HERE,'_probe')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js
def btn(t,root='aside[role=dialog]'):
    J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps(root+' button')})].find(b=>b.innerText.trim()==={json.dumps(t)}); b&&b.click();}})()"); time.sleep(.4)
def abrir(id_): J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(id_)})); r.click();}})()"); time.sleep(.5)
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.2)
    abrir('OS-0424'); btn('Cancelar sem execução'); c.shot(os.path.join(PR,'verif_canc_form.png'))
    J("(()=>{const i=document.querySelector('aside[role=dialog] textarea'); Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(i,'Chuva'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"); time.sleep(.3)
    btn('Confirmar cancelamento'); time.sleep(.3); c.shot(os.path.join(PR,'verif_canc_done.png'))
    J("document.querySelector('aside[role=dialog] button[aria-label=Fechar]').click()"); time.sleep(.3)
    abrir('OS-0420'); btn('Dispensar saldo'); c.shot(os.path.join(PR,'verif_disp_form.png'))
    c.size(1440,900); c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html',wait=1.2)
    J("(()=>{const e=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].find(x=>x.innerText.trim()==='MIP/MID'); e.click();})()"); time.sleep(.4)
    J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Criar vistoria' && b.title).click()"); time.sleep(.4)
    c.shot(os.path.join(PR,'verif_mip_modo.png'))
finally:
    c.close(); srv.terminate()
