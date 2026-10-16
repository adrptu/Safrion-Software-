# -*- coding: utf-8 -*-
"""2ª passada do robô: só as execuções da 1ª (forms_*.jsonl) que não abriram diálogo nem navegaram; agora também conta o painel
lateral antigo (aside visível sem role=dialog, do drawer_button do motor). Saída: legacy_k.jsonl"""
import json, time, os, sys, re
from lib import *
exec(open(os.path.join(EX,'crawl_forms.py')).read().split('def registra')[0].split("SAIDA = ")[0].split('k, nparte')[0])
src=open(os.path.join(EX,'crawl_forms.py')).read()
FORM=re.search(r'FORM = r"""(.*?)"""',src,re.S).group(1).replace("document.querySelectorAll('[role=dialog]')","document.querySelectorAll('[role=dialog],aside')")
CLK=re.search(r'CLK = r"""(.*?)"""',src,re.S).group(1); LINHA=re.search(r'LINHA = r"""(.*?)"""',src,re.S).group(1)
k,n=int(sys.argv[1]),int(sys.argv[2])
L=[]
for i in (0,1): L+=[json.loads(l) for l in open(os.path.join(EX,f'forms_{i}.jsonl'))]
alvo=[x for x in L if not x.get('erro') and not x.get('nav') and not any(d['campos'] for d in x.get('dlg',[]))][k::n]
SAIDA=os.path.join(EX,f'legacy_{k}.jsonl')
c=novo()
try:
    for x in alvo:
        tela=x['tela']; passos=x['passos']
        try:
            abre(c,tela)
            for tipo,a in passos:
                if tipo=='btn': c.js(f"({CLK})({json.dumps(a)},false)")
                elif tipo=='menu': c.js(f"({CLK})({json.dumps(a)},true)")
                else: c.js(LINHA)
                time.sleep(.75)
            d=c.js(FORM) or []
            d=[y for y in d if y['campos']]
            rec={'tela':tela,'passos':passos,'dlg':d}
            if d: rec['cap']=shot(c,'legacy_'+re.sub(r'\W+','_',tela+'_'+'_'.join(str(p[1]) for p in passos))[:80])
        except Exception as ex: rec={'tela':tela,'passos':passos,'erro':str(ex)[:200]}
        open(SAIDA,'a').write(json.dumps(rec,ensure_ascii=False)+'\n')
finally: c.close()
print('fim',k)
