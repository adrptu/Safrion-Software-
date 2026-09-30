# Irrigação sem aprovação do agrônomo (decisão do proprietário, 26/09): água só-água é programada pela necessidade da cultura
# (balanço hídrico) e liberada pela prontidão operacional; acima do limite do equipamento a lâmina é dividida em passadas;
# sonda sem dado usa estimativa por ET e não bloqueia. Fertirrigação (produto na água) continua com o agrônomo.
p = 'areas/irrigacao.py'; s = open(p).read()
def rep(a, b, tag, n=1):
    global s
    c = s.count(a); assert c == n, f'{tag}: {c}'
    s = s.replace(a, b)

# ---------------- cabeçalho do módulo ----------------
rep("""Regras preservadas (cap. 41.8 · DEMO-05/15/16): água só-água dentro da política PA-07 é autorizada por evento (sem assinatura,
sem requisição/custódia) e liberada por prontidão; fora da política = A liberar aguardando revisão individual, cuja aprovação
NÃO altera a política; adicionar produtos reclassifica a MESMA ordem (nova versão) e a leva à aprovação individual.""",
"""Regra v3.9 (decisão do proprietário, 26/09): água só-água NÃO passa pelo agrônomo. O sistema programa a lâmina que a cultura
precisa (balanço hídrico) e libera pela prontidão operacional (janela, bomba, energia, sem conflito), sem requisição/custódia.
Acima do limite por passada do equipamento, a lâmina é dividida em passadas; sonda sem dado usa estimativa por ET (não bloqueia).
Adicionar produtos reclassifica a MESMA ordem (nova versão, fertirrigação) e só essa versão vai à aprovação do agrônomo.""", 'doc')
rep("- OS-0422 (água fora da política, lâmina 13,5 > 12,0 mm) e OS-0423 (gotejo T7, sonda sem dado) = as mesmas de processo_os.py.\n  Recibos de exceção: AU-3104 (OS-0422) e AU-3105 (OS-0423); novas liberações LIB-2291/LIB-2292; novas ordens a partir de OS-0440 (OS-0425 é a adubação do café C1).",
    "- OS-0422 (próximo ciclo, 13,5 mm = 2 passadas de 6,75 mm, janela a definir) e OS-0423 (gotejo T7, estimativa por ET, conflito com a\n  parada da B3) = as mesmas de processo_os.py. Liberações LIB-2291/LIB-2292; novas ordens a partir de OS-0440 (OS-0425 é a adubação do café C1).", 'doc2')

# ---------------- faixa de etapas ----------------
rep("WHY={2:'2 exceções aguardam revisão',4:'Sonda T7 sem dado há 3 d'}", "WHY={2:'1 conflito · 1 janela a definir',4:'Sonda T7 sem dado há 3 d'}", 'why')

# ---------------- IR-01 ----------------
rep("lam=b['lam'],enq=[Pt.chip('—','gray')],tar=b['tar'][0]))", "lam=b['lam'],enq=[Pt.chip('—','gray')],tar=b['tar'][0]))\n        rows[-1]['v']['sid']=b['id']", 'ir01-sid')
rep("num('dfin','= Déficit hoje',w=150),dict(k='enq',l='Enquadramento · tarefa',w=230)]", "num('dfin','= Déficit hoje',w=150),dict(k='enq',l='Necessidade · ordem',w=250)]", 'ir01-col')
old = s[s.index("    POLS=[R('v3'"):s.index("    corpo=(\n      section('Balanço por setor'")]
new = r'''    PARS=[R('P2',setor=[Pt.b('Pivô 2'),Pt.mut('Milho V10 · 80 ha')],lmax=POL['lamina_max'],imin=18,efic=90,fonte=[Pt.txt('Sonda + estação')]),
          R('P1',setor=[Pt.b('Pivô 1'),Pt.mut('Feijão R5 · 95 ha')],lmax=POL['lamina_max'],imin=18,efic=90,fonte=[Pt.chip('Sonda suspeita · usa ET','yellow')]),
          R('T7',setor=[Pt.b('Gotejo T7'),Pt.mut('Mamão · 42 ha')],lmax=6.0,imin=12,efic=95,fonte=[Pt.chip('Sem sonda · usa ET','yellow')])]
    g_pol=grid([dict(k='setor',l='Setor',w=190),dict(k='lmax',l='Lâmina máx. por passada',t='num',a='r',u='mm',d=1,w=170),dict(k='imin',l='Intervalo mín.',t='num',a='r',u='h'),
                dict(k='efic',l='Eficiência do sistema',t='num',a='r',u='%',w=150),dict(k='fonte',l='Umidade do solo',w=200)],PARS,
               edit=dict(m='form',title='Limites do equipamento',sub='Vale para a próxima programação. As ordens já liberadas não mudam.',
                   fields=[dict(k='lmax',l='Lâmina máxima por passada',t='num',req=True,min=1,max=40,u='mm'),dict(k='imin',l='Intervalo mínimo entre passadas',t='num',req=True,min=6,max=96,u='h'),
                           dict(k='efic',l='Eficiência do sistema',t='num',req=True,min=50,max=100,u='%')]),gid='g_pol',total=False,search=False)
    EXTRAJS[0]=JS_COMUM+r"""
const PROX={'P2':13.5};
function PREVALS(self,v){ const par={}; g2rows(self,IRG('g_pol')).forEach(r=>{ par[r.id]=r.v; });
  g2rows(self,IRG('g_bal')).forEach(r=>{ let e; const lm=Number((par[r.v.sid]||{}).lmax)||12;
    if(r.v.sid==='P1') e=[{k:'chip',t:'Fertirrigação · aguarda agrônomo',c:'yellow'}];
    else if(r.v.sid==='T7') e=[{k:'chip',t:'Irrigar 4,0 mm · estimativa por ET',c:'yellow'}];
    else { const n=Math.ceil(PROX.P2/lm); e=[{k:'chip',t:'Irrigar 10,81 mm hoje · liberada',c:'green'},{k:'br',t:''},{k:'mut',t:'próximo ciclo 13,5 mm em '+n+(n>1?' passadas':' passada')}]; }
    e=e.concat([{k:'br',t:''},{k:'link',t:'Abrir '+r.v.tar,h:r.v.href}]); r.p.enq=e; r.s.enq=e[0].t; }); }
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_pol'||!r) return; const n=Math.ceil(PROX.P2/(Number(r.v.lmax)||12));
    self.setState({g2toast:'Limites do '+r.p.setor[0].t+' salvos · próxima programação usa até '+nfx(r.v.lmax,1)+' mm por passada'+(r.id==='P2'?' · 13,5 mm do próximo ciclo = '+n+(n>1?' passadas':' passada'):'')+' · ordens liberadas não mudam.'}); }; }
"""
'''
s = s.replace(old, new)
rep("""      + section('Política de água e exceções','Ajuste a política pela linha (nova versão) e revise as exceções na programação.',
          [ilink('Revisar exceções','IR-02.dc.html','alert','Abrir as 2 ordens fora da política na programação')],
          g_pol+f'<div style="margin-top: 10px;">'+txt(f'Dentro dos limites, a autorização é automática e rastreável, sem assinatura diária. Fora deles, a ordem fica {B("A liberar")} para revisão individual: '
          f'{B("OS-0422")} (lâmina 13,5 &gt; 12,0 mm) e {B("OS-0423")} (sonda do Gotejo T7 sem dado). Aprovar uma exceção não altera a política.')+'</div>',state='yellow')""",
    """      + section('Limites do equipamento','Ajuste pela linha; acima do limite a lâmina é dividida em passadas.','',g_pol)""", 'ir01-sec')
rep("""      subtitle='Confira o déficit de cada setor e se a irrigação cabe na política de água.',
      status=('2 exceções aguardam revisão','yellow'),primary='Programar irrigação',primary_href='IR-02.dc.html',steps=faixa(1),search=False,
      footer='Sem dados suficientes, o setor mostra estimativa e exige revisão individual; previsão do tempo nunca entra como chuva realizada.')""",
    """      subtitle='Confira o déficit de cada setor; o sistema programa a lâmina que a cultura precisa.',
      status=('T7 com estimativa por ET','yellow'),primary='Programar irrigação',primary_href='IR-02.dc.html',steps=faixa(1),search=False,
      footer='Água sem produto não passa pelo agrônomo. Sem sonda, o balanço usa ET e mostra estimativa; previsão do tempo nunca entra como chuva realizada.')""", 'ir01-shell')

# ---------------- IR-02 ----------------
rep("sub='Ajuste janela, lâmina e bomba. Ao salvar, o enquadramento na política e a prontidão são refeitos.',",
    "sub='Ajuste janela, lâmina e bomba. Com janela definida e sem conflito, a ordem é liberada ao salvar.',", 'ir02-sub')
rep("""help=f'Até {_n(POL["lamina_max"])} mm a autorização é automática ({POL["id"]}).'),""",
    """help=f'Acima de {_n(POL["lamina_max"])} mm por passada, o sistema divide em passadas.'),""", 'ir02-help')
a = s.index("const LMAX=12.0; const SONDA=")
b = s.index("'''", a)
s = s[:a] + r"""const LMAX=12.0; const SONDA={'Pivô 2 · Milho V10':'','Pivô 1 · Feijão R5':'sonda P1 suspeita','Gotejo T7 · Mamão':'sonda sem dado'};
const BOMBA={'Pivô 2 · Milho V10':['rio · bomba B2',166],'Pivô 1 · Feijão R5':['rio · bomba B1',150],'Gotejo T7 · Mamão':['reservatório · bomba B3',233]};
const LIBID={'OS-0422':'LIB-2291','OS-0423':'LIB-2292'};
function janOk(j){ j=String(j||'').trim().toLowerCase(); return !!j && j.indexOf('definir')<0; }
// água só-água: sem aprovação; passadas pelo limite do equipamento; liberada quando a operação está pronta
function aval(self,r){ const x=r.v;
  if(x.fert) return {fert:true,etapa:'A liberar'};
  const lam=Number(x.lamina)||0; const np=Math.max(1,Math.ceil(lam/LMAX-1e-9)); const est=SONDA[x.setor]||'';
  const pronto=janOk(x.janela)&&!x.conf;
  return {np,por:lam/np,est,pronto,etapa:pronto?'Liberadas':'A liberar'}; }
function PREVALS(self,v){ g2rows(self,IRG('g_ag')).forEach(r=>{ const x=r.v; const a=aval(self,r);
  r.p.tar=[{k:'b',t:x.tar||'nova'},{k:'br',t:''},{k:'mut',t:x.tipo||'água'}]; r.s.tar=x.tar||'';
  r.p.setor=[{k:'txt',t:x.setor},{k:'br',t:''},{k:'mut',t:(x.bomba||'')+(x.vazao?' · '+nfx(x.vazao,0)+' L/s':'')}]; r.s.setor=x.setor;
  r.p.janela=[{k:'txt',t:x.janela},{k:'br',t:''},{k:'mut',t:x.energia||''}]; r.s.janela=x.janela;
  r.p.lamina=[{k:'txt',t:nfx(x.lamina,2)+' mm'},{k:'br',t:''},{k:'mut',t:(a.np>1?a.np+' passadas de '+nfx(a.por,2)+' mm':nfx(x.dur,1)+' h')}]; r.s.lamina=nfx(x.lamina,2)+' mm';
  let au, ac=[];
  if(a.fert){ au=[{k:'chip',t:'A liberar',c:'gray'},{k:'chip',t:'Aguardando agrônomo',c:'yellow'},{k:'br',t:''},{k:'mut',t:'fertirrigação · produto na água'}]; ac=[{k:'link',t:'Ver decisão',h:'IN-02det.dc.html'}]; }
  else { au=[{k:'chip',t:a.etapa,c:a.etapa==='Liberadas'?'green':'gray'}];
    if(x.conf) au.push({k:'chip',t:'Conflito · '+x.conf,c:'red'});
    else if(!janOk(x.janela)) au.push({k:'chip',t:'Janela a definir',c:'yellow'});
    if(a.est) au.push({k:'br',t:''},{k:'mut',t:'estimativa por ET · '+a.est});
    if(x.conf) ac.push({k:'act',t:'Resolver conflito',fn:'conf:'+r.id,u:true});
    else if(!janOk(x.janela)) ac.push({k:'act',t:'Definir janela',fn:'jan:'+r.id,u:true});
    if(a.etapa==='Liberadas') ac.push(x.tar==='OS-0419'?{k:'link',t:'Abrir ordem',h:'IR-03det.dc.html'}:{k:'link',t:'Ver nas ordens',h:'IR-03.dc.html'}); }
  r.p.aut=au; r.s.aut=au.map(p=>p.t).join(' '); r.p.acao=ac.length?ac:[{k:'mut',t:'—'}]; r.s.acao=''; }); }
function upd(self,rid,fn){ const rows=g2clone(g2rows(self,IRG('g_ag'))); const r=rows.find(x=>x.id===rid); if(!r) return null; fn(r); g2set(self,'g_ag',{rows,fl:rid}); return r; }
function libMsg(self,r){ const a=aval(self,r); const x=r.v;
  return x.tar+' Liberada · '+(LIBID[x.tar]||'LIB-2293')+' · '+nfx(x.lamina,2)+' mm'+(a.np>1?' em '+a.np+' passadas de '+nfx(a.por,2)+' mm':'')+' · janela '+x.janela+' · liberar não liga o equipamento.'; }
function EXTRAVALS(self,v){ const st=self.state;
  self.g2after=(gid,rows,r,isNew)=>{ if(gid!=='g_ag'||!r) return;
    if(!r.v.tar){ const dup=rows.find(x=>x!==r && x.v.tar && !x.v.fert && x.v.setor===r.v.setor && String(x.v.janela).trim()===String(r.v.janela).trim());
      if(dup){ g2set(self,'g_ag',{rows:rows.filter(x=>x!==r),fl:dup.id}); self.setState({g2toast:'Tarefa única '+dup.v.tar+' recuperada ('+dup.v.setor+' · '+dup.v.janela+') · nenhuma ordem duplicada.'}); return; }
      const n=self.state.seq||440; const bb=BOMBA[r.v.setor]||['',0]; r.v.tar='OS-0'+n; r.v.tipo='água'; r.v.bomba=bb[0]; if(!r.v.vazao) r.v.vazao=bb[1]; r.v.conf=''; r.v.novo='0'; r.v.fert=false;
      const a=aval(self,r); self.setState({seq:n+1,g2toast:r.v.tar+' programada · '+(a.etapa==='Liberadas'?'liberada automaticamente · '+nfx(r.v.lamina,2)+' mm'+(a.np>1?' em '+a.np+' passadas':'')+' · sem requisição nem custódia.':'A liberar até definir a janela.')}); return; }
    const a=aval(self,r); self.setState({g2toast:a.fert?'Salvo · '+r.v.tar+' segue com o agrônomo (fertirrigação).':(a.etapa==='Liberadas'?libMsg(self,r):'Salvo · '+r.v.tar+' A liberar: '+(r.v.conf?'resolva o conflito.':'defina a janela.'))}); };
  v.conf=(rid)=>{ const r=upd(self,rid,(x)=>{ x.v.janela='hoje 15:00–17:00'; x.v.conf=''; x.s.janela='hoje 15:00–17:00'; });
    if(r) self.setState({g2toast:'Janela de '+r.v.tar+' movida para 15:00–17:00 · sem sobreposição com a parada da B3 · '+libMsg(self,r)}); };
  v.jan=(rid)=>g2open(self,IRG('g_ag'),rid,null);
  // estado no cabeçalho
  const all=g2rows(self,IRG('g_ag')); const nconf=all.filter(r=>r.v.conf).length; const njan=all.filter(r=>!r.v.fert&&!r.v.conf&&!janOk(r.v.janela)).length;
  const t=[]; if(nconf) t.push(nconf+(nconf>1?' conflitos':' conflito')); if(njan) t.push(njan+(njan>1?' janelas a definir':' janela a definir'));
  v.hs_t=t.length?t.join(' · '):'Programação sem pendências'; v.hs_st=chipSt(t.length?'yellow':'green'); }
""" + s[b:]
a = s.index("    rv_corpo=(f'<div style=\"display: flex; flex-direction: column; border-top")
b = s.index("    corpo=(\n      section('Agenda por setor e bomba'")
s = s[:a] + s[b:]
rep("section('Agenda por setor e bomba','Programe janela, lâmina e bomba; clique na linha para ajustar e revise exceções e conflitos na coluna Ação.',",
    "section('Agenda por setor e bomba','Programe janela, lâmina e bomba; clique na linha para ajustar e resolva conflitos na coluna Ação.',", 'ir02-sec')
rep("dict(k='aut',l='Autorização · etapa',w=260)", "dict(k='aut',l='Etapa · pendência',w=260)", 'ir02-col')
rep("""      subtitle='Programe janela, lâmina e bomba; água dentro da política libera sozinha, o resto vai à revisão individual.',
      primary_html=prim,steps=faixa(2),search=False,
      footer='Produtos exigem aprovação individual e requisição; água só-água não usa requisição nem custódia. Aprovar ou liberar não liga equipamento.')""",
    """      subtitle='Programe janela, lâmina e bomba; água sem produto é liberada sozinha quando a operação está pronta.',
      primary_html=prim,steps=faixa(2),search=False,
      footer='Só a fertirrigação vai ao agrônomo, com requisição. Água sem produto não usa requisição nem custódia. Liberar não liga equipamento.')""", 'ir02-shell')

# ---------------- IR-03 ----------------
rep("""apl=[Pt.mut('— · prevista em 11,6 de 80 ha')],aut='PA-07 v3 · AU-3098',""", """apl=[Pt.mut('— · prevista em 11,6 de 80 ha')],aut='Necessidade do balanço · AU-3098',""", 'ir03-a')
rep("""aut='PA-07 v3',at='hoje 06:00'""", """aut='Necessidade do balanço',at='hoje 06:00'""", 'ir03-b')
rep("""etapa=ET('A liberar')+[Pt.chip('Conflito · parada da B3','red'),Pt.chip('Fora da política · sem sonda','yellow')],alvo=4.0,apl=[Pt.mut('— · 0 de 42 ha')],aut='Revisão individual pendente',at='hoje 06:12',""",
    """etapa=ET('A liberar')+[Pt.chip('Conflito · parada da B3','red'),Pt.mut('estimativa por ET')],alvo=4.0,apl=[Pt.mut('— · 0 de 42 ha')],aut='Necessidade estimada por ET · sonda sem dado',at='hoje 06:12',""", 'ir03-c')
rep("""etapa=ET('A liberar')+[Pt.chip('Fora da política · 13,5 > 12,0 mm','yellow')],alvo=13.5,apl=[Pt.mut('— · 0 de 80 ha')],aut='Revisão individual pendente',at='hoje 06:12',
       acao=[Pt.link('Revisar exceção','IR-02.dc.html')]),""",
    """etapa=ET('A liberar')+[Pt.chip('Janela a definir','yellow'),Pt.mut('2 passadas de 6,75 mm')],alvo=13.5,apl=[Pt.mut('— · 0 de 80 ha')],aut='Necessidade do balanço · próximo ciclo',at='hoje 06:12',
       acao=[Pt.link('Definir janela','IR-02.dc.html')]),""", 'ir03-d')
rep("""aut='PA-07 v3',at='19/09 16:04'""", """aut='Necessidade do balanço',at='19/09 16:04'""", 'ir03-e')
rep("dict(k='aut',l='Autorização',ro=True)", "dict(k='aut',l='Origem da lâmina',ro=True)", 'ir03-f')

# ---------------- IR-03det ----------------
rep("""aut.push({id:'a1',v:{ver:'Autorização técnica',ori:'PA-07 v3 · memória de cálculo · AU-3098'},s:{},p:{sit:ch('Enquadrada na política · evento rastreável','green')}});""",
    """aut.push({id:'a1',v:{ver:'Necessidade da cultura',ori:'balanço de 23/09 · déficit 11,2 mm · AU-3098'},s:{},p:{sit:ch('10,81 mm em 1 passada · sem aprovação','green')}});""", 'det-a1')
rep("""aut.push({id:'b2',v:{ver:'Autorização de água',ori:'AU-3098 mantida só no histórico'},s:{},p:{sit:ch('Invalidada para o saldo','gray')}});""",
    """aut.push({id:'b2',v:{ver:'Liberação da água',ori:'AU-3098 mantida só no histórico'},s:{},p:{sit:ch('Não vale para o saldo com produto','gray')}});""", 'det-b2')
rep("""const ev=[['23/09 06:12','AU-3098','Autorização por política PA-07 v3 · lâmina 10,81 ≤ 12,0 mm · déficit 11,2 mm','sistema'],""",
    """const ev=[['23/09 06:12','AU-3098','Necessidade calculada pelo balanço · déficit 11,2 mm → 10,81 mm brutos em 1 passada (limite 12,0 mm)','sistema'],""", 'det-ev')
rep(""":(fase==='Encerradas'?'Fatos consistentes: conferida e encerrada automaticamente.':'Água dentro da política: com registros consistentes, conferência e encerramento são automáticos.');""",
    """:(fase==='Encerradas'?'Fatos consistentes: conferida e encerrada automaticamente.':'Água sem produto: sem aprovação; com registros consistentes, conferência e encerramento são automáticos.');""", 'det-hint')
rep("(ex?'segue Em execução com selo Revisão de saldo · saldo pausado':'voltou a A liberar · autorização de água invalidada para o saldo')",
    "(ex?'segue Em execução com selo Revisão de saldo · saldo pausado':'voltou a A liberar · a liberação da água não vale para o saldo com produto')", 'det-toast')
rep("'A ordem volta a A liberar: a autorização de água deixa de valer para o saldo e a liberação LIB-2287 é revogada.'",
    "'A ordem volta a A liberar: com produto, o saldo precisa do agrônomo e a liberação LIB-2287 é revogada.'", 'det-prev')
rep("section('Autorização e materiais','Confira a autorização e o que não se aplica à água sem produtos.','',g_aut)",
    "section('Origem e materiais','Confira de onde vem a lâmina e o que não se aplica à água sem produtos.','',g_aut)", 'det-sec')
rep("subtitle='Execute a irrigação e confirme o término; a política autoriza, o comando físico continua com o irrigante.',",
    "subtitle='Execute a irrigação e confirme o término; o comando físico continua com o irrigante.',", 'det-sub')
open(p, 'w').write(s); print('patch irrigação ok')
