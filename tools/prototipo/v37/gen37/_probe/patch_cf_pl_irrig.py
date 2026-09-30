import re
def patch(p, pares):
    s=open(p,encoding='utf-8').read()
    for a,b,tag in pares:
        c=s.count(a); assert c==1, f'{p} {tag}: {c}'
        s=s.replace(a,b)
    open(p,'w',encoding='utf-8').write(s)

# ---- Configurações (CF-02 e CF-04): limites de irrigação são parâmetro do equipamento, sem aprovação ----
s=open('areas/configuracoes.py',encoding='utf-8').read()
i=s.index("      pol('pa07',"); j=s.index("\n",s.index("      pol('pa08',"))+1
s=s[:i]+"""      pol('pa07','IR-LIM','limites de irrigação (só água)','v4',f'{D.PIVO["id"]} + pivô 1 + gotejo T7',f'lâmina ≤ {lam} mm por passada · intervalo ≥ {D.POLITICA_AGUA["intervalo_min"]}','Gestor · sem aprovação por evento','Ana (gestora)','sem validade',ch('Vigente','green'),[]),
"""+s[j:]
open('areas/configuracoes.py','w',encoding='utf-8').write(s)
patch('areas/configuracoes.py',[
 ("  const rev=2+A.filter(r=>r.v.__rev).length+P.filter(r=>r.v.__rev).length;","  const rev=1+A.filter(r=>r.v.__rev).length+P.filter(r=>r.v.__rev).length;",'rev'),
 (".concat(['PA-08','AL-05 v3'])).join(' · ');",".concat(['AL-05 v3'])).join(' · ');",'revu'),
 ("('VENCEM EM 60 DIAS','1','PA-07 · 30/11')","('VENCEM EM 60 DIAS','0','nenhuma no período')",'kpi'),
 ("'Serviço · política PA-07 v3','A liberar → Liberadas','água sem produtos enquadrada na política','evento de liberação automático, individual e rastreável'",
  "'Serviço · balanço hídrico','A liberar → Liberadas','água sem produto pela necessidade da cultura','liberação automática pela prontidão, sem aprovação'",'aud1'),
 ("'autorização de água invalidada para o saldo · revisão indi","'liberação da água não vale para o saldo com produto · revisão indi",'aud2'),
 ("('20/09 11:02',[Pt.b('PA-07'),Pt.txt(' · v2 → v3')],'Ana · agrônoma RT','lâmina máx. 11 mm → 12 mm','recomendação do plano técnico','aprovador registrado · validade 30/11'),",
  "('20/09 11:02',[Pt.b('Limites de irrigação'),Pt.txt(' · Pivô 2')],'Ana · gestora','lâmina máx. por passada 11 → 12 mm','ajuste do percentímetro','vale para a próxima programação'),",'aud3'),
])

# ---- Planejamento (PL-04): água não vai ao agrônomo; pendências operacionais ----
patch('areas/planejamento.py',[
 ("p=dict(os=O('OS-0419','água Pivô 2 · política'),","p=dict(os=O('OS-0419','água Pivô 2'),",'o419'),
 ("R('o422',dict(os='OS-0422',jan='a definir',rec='Pivô 2',oper='João',dur='—',mat='sem insumo',etp='A liberar'),\n        p=dict(os=O('OS-0422','água Pivô 2 · próximo ciclo'),sel=[CH('Fora da política · aguardando revisão','red')],",
  "R('o422',dict(os='OS-0422',jan='a definir',rec='Pivô 2',oper='João',dur='2 passadas',mat='sem insumo',etp='A liberar'),\n        p=dict(os=O('OS-0422','água Pivô 2 · próximo ciclo'),sel=[CH('Janela a definir','yellow')],",'o422'),
 ("p=dict(os=O('OS-0423','água gotejo T7'),sel=[CH('Fora da política · sonda sem dado','red')],",
  "p=dict(os=O('OS-0423','água gotejo T7'),sel=[CH('Conflito · parada da B3','red')],",'o423'),
 ("    SELC={'Fora da política · aguardando revisão':('Fora da política','aguardando revisão'),'Fora da política · sonda sem dado':('Fora da política','sonda sem dado')}",
  "    SELC={'Conflito · parada da B3':('Conflito','parada da B3 14:00–15:00')}",'selc'),
 ("· OS-0422 e OS-0423 fora da política de água. Material previsto","· OS-0422 sem janela e OS-0423 em conflito com a parada da B3 (água não passa pelo agrônomo). Material previsto",'pront'),
 ("imsg('Enviar ao agrônomo','OS-0418, OS-0422 e OS-0423 na fila de Ana (agrônoma) · a fila mostra só ordens emitidas do período (simulado · nenhuma mensagem real enviada).'",
  "imsg('Enviar ao agrônomo','OS-0418 (fertirrigação) na fila de Ana (agrônoma) · água sem produto não vai à fila · a fila mostra só ordens emitidas do período (simulado · nenhuma mensagem real enviada).'",'agro'),
 ("· OS-0422 e OS-0423 continuam: fora da política de água. Resultado por item;","· OS-0422 continua: janela a definir · OS-0423 continua: conflito com a parada da B3. Resultado por item;",'lib'),
])
t=open('cftest.py',encoding='utf-8').read(); assert t.count("chk('KPI em revisão = 3', '3 em revisão' in body())")==1
open('cftest.py','w',encoding='utf-8').write(t.replace("chk('KPI em revisão = 3', '3 em revisão' in body())","chk('KPI em revisão = 2', '2 em revisão' in body())"))
print('ok')
