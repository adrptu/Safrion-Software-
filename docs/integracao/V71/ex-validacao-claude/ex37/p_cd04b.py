import json,time
from lib import *
c=novo()
try:
    abre(c,'CD-04')
    print(clica(c,'Cadastrar pessoa'))
    time.sleep(.5)
    print(json.dumps(resume_dlg(dialogo(c)),ensure_ascii=False,indent=1))
    shot(c,'cd04_cadastrar_pessoa')
finally: c.close()
