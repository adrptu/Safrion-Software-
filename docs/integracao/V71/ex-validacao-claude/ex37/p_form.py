# Uso: EXCH=CHROME2 python3 p_form.py TELA 'rótulo do botão' [hash] -> abre o formulário pelo clique real e resume campos/primária
import json,time,sys,re
from lib import *
c=novo()
try:
    abre(c,sys.argv[1],sys.argv[3] if len(sys.argv)>3 else '')
    r=clica(c,sys.argv[2]); print('clique',r); time.sleep(.6)
    d=dialogo(c); print(json.dumps(resume_dlg(d),ensure_ascii=False))
    for x in d or []:
        print('valores:',[(f['lab'][:30],f['val']) for f in x['campos'] if f['vis']])
        print('texto:',x['txt'][:800])
    shot(c,(sys.argv[1]+'_'+re.sub(r'\W+','_',sys.argv[2]))[:60])
finally: c.close()
