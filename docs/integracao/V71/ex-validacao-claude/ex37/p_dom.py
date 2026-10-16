import json,time,sys
from lib import *
c=novo()
try:
    abre(c,sys.argv[1])
    print(clica(c,sys.argv[2]))
    time.sleep(.5)
    print(c.js("(()=>{const d=[...document.querySelectorAll('[role=dialog],aside,dialog')];return d.map(e=>e.tagName+' '+[...e.attributes].map(a=>a.name+'='+a.value.slice(0,40)).join(' ')+' | parent '+e.parentElement.tagName+' '+[...e.parentElement.attributes].map(a=>a.name+'='+a.value.slice(0,40)).join(' '))})()"))
finally: c.close()
