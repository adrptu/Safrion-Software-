import json,time
from lib import *
c=novo()
try:
    abre(c,'CD-04')
    b=botoes(c,'document.querySelector("main")||document')
    print(json.dumps([x for x in b][:60],ensure_ascii=False))
finally: c.close()
