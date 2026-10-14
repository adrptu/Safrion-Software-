# Métrica da explicação: classifica cada bloco de texto solto (varredura sem corte de 140 caracteres) do render de antes
# pela lista TIRADAS do textos_soltos_test.py; mede quanto de explicação havia e quanto segue à vista no render novo.
import json, sys, os, unicodedata
G=os.environ.get('GEN37') or os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','..','tools','prototipo','v37','gen37')
src=open(os.path.join(G,'textos_soltos_test.py'),encoding='utf-8').read()
ns={}; exec(src.split("def norm")[0].split("R = os.environ")[1].split('\n',1)[1], ns)
T=ns['TIRADAS']; F=ns['FICAM']
def norm(s): return ' '.join(unicodedata.normalize('NFC', str(s or '')).replace(' ',' ').lower().split())
A=json.load(open(sys.argv[1])); D=json.load(open(sys.argv[2]))
# frases deixadas à vista por serem trava, dado, licença ou documento impresso (contam como explicação que FICOU, por conservadorismo)
MANTIDAS=json.load(open(sys.argv[3])) if len(sys.argv)>3 else {}
tot_e=0; rest_e=0; linhas=[]
for k,itens in A.items():
    t=k[:-8]; dn=[norm(x) for x in D.get(k,[])]; an=[norm(x) for x in itens]
    for it in itens:
        n=norm(it); chaves=[x for x in T if x[0]==t and norm(x[2]) in n]
        man=[m for m in MANTIDAS.get(t,[]) if norm(m) in n]
        if not chaves and not man: continue
        # o que ficou como dado: bloco novo (não existia antes) com o mesmo começo, ou trechos FICAM contidos no bloco antigo
        novos=[x for x in dn if x not in an]
        fk=[norm(f) for tt,f in F if tt==t and norm(f) in n]
        par=[x for x in novos if x[:14]==n[:14]] or [x for x in novos if any(k in x for k in fk)]
        kept=len(par[0]) if par else sum(len(norm(f)) for tt,f in F if tt==t and norm(f) in n)
        if not chaves:   # mantida de propósito
            e=len(n); tot_e+=e; rest_e+=e; linhas.append((t,'mantida',e,it[:90])); continue
        e=max(0,len(n)-kept); tot_e+=e
        ainda=any(norm(x[2]) in ' '.join(dn) for x in chaves)
        if ainda: rest_e+=e
        linhas.append((t,'ainda' if ainda else 'cortada',e,it[:90]))
for l in sorted(linhas): print(f'{l[0]:16s} {l[1]:8s} {l[2]:5d}  {l[3]}')
print(f'\nexplicação antes: {tot_e} car. · ainda à vista: {rest_e} car. · cortada: {tot_e-rest_e} car. ({100*(tot_e-rest_e)/max(1,tot_e):.1f}%)')
