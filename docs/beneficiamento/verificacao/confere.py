# Conferência estrutural da ESPECIFICACAO.md v2: referências cruzadas e dano nomeado
import re,sys
s=open('ESPECIFICACAO.md').read()
sec=lambda a,b: s[s.index(a):s.index(b)] if b else s[s.index(a):]
s4=sec('## 4. Regras','## 5. Telas'); s10=sec('## 10. Seed','## 11. Ordem'); s11=sec('## 11. Ordem','## 12. Crit'); s12=sec('## 12. Crit',None)
regras=set(re.findall(r'\*\*(R-[A-G]\d\d)',s4))
regras|={f'R-D0{i}' for i in range(4,8)}
casos=set(re.findall(r'\| (K\d\d) ',s10))
testes=set(re.findall(r'^- ([UET]\d\d) ',s11,re.M))|set(re.findall(r'^- (T\d\d)',s11,re.M))
testes|=set(re.findall(r'^- T02, T03, T04 e T06',s11,re.M) and ['T02','T03','T04','T06'])
def faixa(x):
    m=re.match(r'([A-Z])(\d\d)-[A-Z]?(\d\d)',x)
    return [f'{m.group(1)}{i:02d}' for i in range(int(m.group(2)),int(m.group(3))+1)]
falta=[]
for ref in set(re.findall(r'\bR-[A-G]\d\d\b',s)):
    if ref not in regras: falta.append(('regra',ref))
for ref in set(re.findall(r'\bK\d\d\b',s)):
    if ref not in casos: falta.append(('caso',ref))
for ref in set(re.findall(r'\b([UET]\d\d)\b',s11+s12)):
    if ref not in testes: falta.append(('teste',ref))
acs=re.findall(r'^\| (AC-\d\d)',s12,re.M)
dup=[a for a in set(acs) if acs.count(a)>1]
# toda regra com "Trava" tem "Dano" no mesmo item
semdano=[]
for bloco in re.split(r'\n- \*\*(?=R-)',s4)[1:]:
    rid=bloco[:5]
    if 'Trava' in bloco and 'Dano' not in bloco: semdano.append(rid)
print('regras',len(regras),'casos',len(casos),'testes',len(testes),'ACs',len(acs))
print('referencias sem alvo',sorted(falta))
print('AC duplicados',dup)
print('trava sem dano',semdano)
