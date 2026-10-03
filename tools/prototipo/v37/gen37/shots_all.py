import os, re, subprocess, shutil, glob
from concurrent.futures import ThreadPoolExecutor
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,'_shots'); R=os.path.join(HERE,'_render')
os.makedirs(OUT,exist_ok=True); os.makedirs(R,exist_ok=True)
shutil.copy(os.path.join(HERE,'..','..','telas','pack','measure','support.js'),os.path.join(R,'support.js'))
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
def one(f):
    n=os.path.basename(f); s=open(f).read(); open(os.path.join(R,n),'w').write(s)
    w,h=map(int,re.search(r'"\$preview":\{"width":(\d+),"height":(\d+)\}',s).groups())
    p=os.path.join(OUT,n.replace('.dc.html','.png'))
    subprocess.run([CH,'--headless=new','--disable-gpu','--hide-scrollbars','--virtual-time-budget=9000',f'--window-size={w},{h}',f'--screenshot={p}','file://'+os.path.join(R,n)],capture_output=True,timeout=180)
    return n, os.path.exists(p)
with ThreadPoolExecutor(6) as ex: res=list(ex.map(one,sorted(glob.glob(os.path.join(HERE,'project','*.dc.html')))))
print(len(res),'capturas ·',sum(1 for _,ok in res if ok),'ok')
