# listas derivadas (sem aleatoriedade): extras divididos para o Python (os 3 maiores só no JS, por tempo); piores adversariais para P1 2^20/2^22
# no Python; amostra de 40 entradas aleatórias da categoria C (índices 2500, 2520, …, 3280) para P1 no Python
import json,sys
W=sys.argv[1]; E=json.load(open(W+'/entradas/casos_extras.json'))
so_js={'extra 7x7 partes fixas, todas 10 h','extra 8x8 partes fixas, todas 10 h','extra 10x10 partes fixas, todas 10 h'}
json.dump([c for c in E if c['nome'] not in so_js],open(W+'/entradas/casos_extras_py.json','w'),ensure_ascii=False,indent=0)
json.dump([c for c in E if c['nome'] in so_js],open(W+'/entradas/casos_extras_so_js.json','w'),ensure_ascii=False,indent=0)
A=json.load(open(W+'/entradas/adversariais.json')); nomes=['trator×implemento 5x6 jan 10','trator×implemento 6x6 jan 10','trator×implemento 7x5 jan 10','trator×implemento 6x6 janelas variadas (todas finitas)','hipercubo Q5']
P=[c for c in A if c['nome'] in nomes]+[c for c in E if c['nome'] in ('extra 7x6 partes fixas, todas 10 h','extra 10x10 partes fixas, todas 10 h')]
assert len(P)==7; json.dump(P,open(W+'/entradas/adversariais_piores.json','w'),ensure_ascii=False)
json.dump(list(range(2500,3300,20)),open(W+'/entradas/aleatorias_amostra_P1_py.json','w'))
L=open(sys.argv[2],encoding='utf-8').read().split('\n')   # M2: lido do oráculo de 2e31588 (linhas 142–144), sem cópia manual
i=[k for k,l in enumerate(L) if l.startswith(" ('M2 ")][0]; txt='\n'.join(L[i:i+3]).strip().rstrip(',')
open(W+'/entradas/M2_oraculo_linhas_%d-%d.txt'%(i+1,i+3),'w').write('\n'.join(L[i:i+3])+'\n'); M=eval(txt,{'dict':dict})
json.dump([{'nome':'M2 fracao_final_no_corte_aninhado (oráculo, linhas 142–144)','Q':M[2],'cfgs':M[3],'pools':M[4]}],open(W+'/entradas/M2.json','w'),ensure_ascii=False)
print('ok')
