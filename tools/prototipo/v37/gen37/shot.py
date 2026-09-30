import sys, os, re, subprocess, shutil
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,'_shots'); os.makedirs(OUT,exist_ok=True)
R=os.path.join(HERE,'_render'); os.makedirs(R,exist_ok=True); shutil.copy(os.path.join(HERE,'..','..','telas','pack','measure','support.js'),os.path.join(R,'support.js'))
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for n in sys.argv[1:]:
    s=open(os.path.join(HERE,'project',n)).read(); open(os.path.join(R,n),'w').write(s)
    w,h=map(int,re.search(r'"\$preview":\{"width":(\d+),"height":(\d+)\}',s).groups())
    p=os.path.join(OUT,n.replace('.dc.html','.png'))
    subprocess.run([CH,'--headless=new','--disable-gpu','--hide-scrollbars','--virtual-time-budget=9000',f'--window-size={w},{h}',f'--screenshot={p}','file://'+os.path.join(R,n)],capture_output=True,timeout=180)
    print(p, os.path.exists(p))
