import sys,os,time,subprocess,socket,json
sys.path.insert(0,'.')
from cdp import Chrome
def _free():
    s=socket.socket(); s.bind(('127.0.0.1',0)); x=s.getsockname()[1]; s.close(); return x
port=_free(); srv=subprocess.Popen(['python3','-m','http.server',str(port),'--bind','127.0.0.1','--directory','_render'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=_free())
FULL=open('pack37.py').read().split('FULL="',1)[1].split('"\nPRE_ETAPAS')[0].encode().decode('unicode_escape')
try:
  for i in (1,2,3):
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{port}/SAF.dc.html',wait=1.1)
    c.js("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/^Abrir safra/.test(b.innerText.trim())); if(b) b.click();})()"); time.sleep(.5)
    c.js(f"document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[{i}].click()"); time.sleep(.5)
    before=c.js("document.querySelector('main').innerText.length")
    c.js(FULL); c.js("(()=>{const st=document.createElement('style'); st.textContent='*{break-inside:auto!important;break-before:auto!important;break-after:auto!important;page-break-inside:auto!important}'; document.head.appendChild(st);})()"); time.sleep(.4)
    after=c.js("(()=>{const m=document.querySelector('main');return [m.innerText.length,m.getBoundingClientRect().height,[...m.children].map(x=>x.tagName+':'+Math.round(x.getBoundingClientRect().height)+':'+getComputedStyle(x).display).join(' | ')]})()")
    h=c.js("Math.ceil(Math.max(document.querySelector('[data-root]').scrollHeight, document.documentElement.scrollHeight))")
    c.size(1440,h); time.sleep(.3)
    c.shot(f'_probe/s{i+1}.png')
    import base64
    c.call('Emulation.setEmulatedMedia',{'media':'screen'})
    d=c.call('Page.printToPDF',{'printBackground':True,'paperWidth':1440/96,'paperHeight':(h+24)/96,'marginTop':0,'marginBottom':0,'marginLeft':0,'marginRight':0,'pageRanges':'1'},timeout=120)
    open(f'_probe/q{i+1}.pdf','wb').write(base64.b64decode(d['data']))
    after2=c.js("document.querySelector('main').innerText.length")
    print(i+1,before,after,h,after2)
finally:
  c.close(); srv.terminate()
