import json,time,sys,re
from lib import *
c=novo()
try:
    abre(c,'COLH')
    print(json.dumps(c.js("""(()=>{const e=[...document.querySelectorAll('main *')].find(x=>x.children.length===0&&x.textContent.trim()==='Pivô 19'&&!x.closest('select')&&x.getClientRects().length); const ch=[]; let r=e; for(let k=0;k<8&&r;k++){ ch.push(r.tagName+' role='+r.getAttribute('role')+' cursor='+getComputedStyle(r).cursor+' btns='+[...r.querySelectorAll('button')].map(b=>(b.innerText||b.getAttribute('aria-label')||'').trim().slice(0,20)).join('|')); r=r.parentElement; } return ch;})()"""),ensure_ascii=False,indent=0))
finally: c.close()
