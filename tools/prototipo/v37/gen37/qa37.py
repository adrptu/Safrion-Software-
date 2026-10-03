# -*- coding: utf-8 -*-
"""QA do protótipo v3.7: (1) links quebrados; (2) overflow medido em Chrome headless → heights_override.json."""
import glob, os, re, json, subprocess, shutil, math, sys
from concurrent.futures import ThreadPoolExecutor
HERE=os.path.dirname(os.path.abspath(__file__)); PROJ=os.path.join(HERE,'project'); MEAS=os.path.join(HERE,'_measure')
SUPPORT=os.path.join(HERE,'..','..','telas','pack','measure','support.js')
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
def links():
    files={os.path.basename(f) for f in glob.glob(PROJ+'/*.dc.html')}
    broken={}
    for f in sorted(files):
        s=open(os.path.join(PROJ,f)).read()
        for h in set(re.findall(r'href="([^"#]+\.dc\.html)"',s)):
            if h not in files: broken.setdefault(h,[]).append(f)
    return files,broken
JS="""<script>setTimeout(function(){var R=document.querySelector('[data-root]')||document.querySelector('x-dc > div')||document.body.firstElementChild; var H0=R?R.getBoundingClientRect().height:0; if(R){R.style.height='auto'; var M=R.querySelector('main[data-scroll="1"]'); } var need=R?Math.ceil(R.getBoundingClientRect().height):0; document.body.setAttribute('data-need',need+'|'+(R&&R.querySelector('main[data-scroll="1"]')?1:0)); var r=0,who='';document.querySelectorAll('main, [style*="overflow: hidden"]').forEach(function(e){var d=e.scrollHeight-e.clientHeight;if(e.clientHeight>200&&d>r){r=d;who=e.tagName}});document.body.setAttribute('data-ov',r+'|'+who)},5000)</script>"""
def measure_one(f):
    n=os.path.basename(f); s=open(f).read().replace('</body>',JS+'</body>',1)
    p=os.path.join(MEAS,n); open(p,'w').write(s)
    w=int(re.search(r'"\$preview":\{"width":(\d+)',s).group(1))
    out=subprocess.run([CH,'--headless=new','--disable-gpu','--virtual-time-budget=9000',f'--window-size={max(w,1280)},3200','--dump-dom','file://'+p],capture_output=True,text=True,timeout=180).stdout
    m=re.search(r'data-need="(\d+)\|(\d)"',out)
    fh=int(re.search(r'"\$preview":\{"width":\d+,"height":(\d+)\}',s).group(1))
    return n,((int(m.group(1)) if m else None), fh, (m.group(2)=='1') if m else False)
def measure(only=None):
    os.makedirs(MEAS,exist_ok=True); shutil.copy(SUPPORT,os.path.join(MEAS,'support.js'))
    fs=sorted(glob.glob(PROJ+'/*.dc.html'))
    if only: fs=[f for f in fs if os.path.basename(f) in only]
    with ThreadPoolExecutor(6) as ex: res=dict(ex.map(measure_one,fs))
    ovr_p=os.path.join(HERE,'heights_override.json')
    ovr=json.load(open(ovr_p)) if os.path.exists(ovr_p) else {}
    changed={}
    for n,(need,fh,scroll) in res.items():
        if need is None: changed[n]='SEM MEDIDA'; continue
        if scroll: continue  # processos: altura fixa com rolagem interna
        new=int(math.ceil((need+16)/10.0)*10)
        if abs(new-fh)>20: ovr[n]=new; changed[n]=(fh,new)
    json.dump(ovr,open(ovr_p,'w'),indent=1,sort_keys=True)
    return res,changed
if __name__=='__main__':
    files,broken=links()
    print(f'telas: {len(files)} · destinos inexistentes: {len(broken)}')
    for h,src in sorted(broken.items()): print(f'  {h}  ← {", ".join(sorted(src)[:4])}{" …" if len(src)>4 else ""}')
    if '--measure' in sys.argv:
        res,ch=measure()
        print(f'medidas: {len(res)} · ajustadas: {len(ch)}')
        for k,v in sorted(ch.items()): print('  ',k,v)
