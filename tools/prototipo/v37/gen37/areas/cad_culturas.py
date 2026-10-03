# -*- coding: utf-8 -*-
"""CD-02 · Culturas, cultivares e operações (módulo próprio; areas.cadastros.build() usa este cd02()).
Duas abas, uma primária por aba:
 · Culturas e cultivares — árvore Cultura → cultivar. A linha da cultura abre nome, tipo de ciclo e unidade de produtividade;
   a da cultivar abre ciclo, item de semente vinculado, registro e situação. 'Outra cultura…' cria a cultura no próprio formulário.
 · Operações e rendimentos — árvore Operação → conjunto (mesmo desenho da etapa 3 do Planejar safra). A linha da operação abre
   processo (etapa de custo da Estrutura gerencial) e atividades usuais; a do conjunto abre o rendimento, agora com a cultura
   (Todas ou uma). O formulário de rendimento mantém largura × velocidade × eficiência e custo/h do Planejar safra (REND_CAMPOS).
Culturas e processos daqui são a fonte das dimensões Cultura e Processo do CD-07; o item de semente é o do CD-06."""
import json
from engine import grid, SEG_ON, SEG_OFF
import engine as E
import ui37
from ui37 import shell37, HEIGHTS37
import dados2 as D2
import dados_cad as DC
from areas.cadastros import (sel, num, txt, dat, cond, R, js,
                             CULTIVARES, MODO, FONTE, REND_CAMPOS, REND_JS, _uso_cultivar)
from areas.cadastros import (cadx_css, abas, pane, faixa, prim, secbtn, qf_chips, bloco_cad, estado_cab, acoes_form, arv)

H=lambda s: '{{'+s+'}}'
ui37.H_OVR.pop('CD-02.dc.html',None)   # layout novo: a altura vem de HEIGHTS37
OUTRA_C='Outra cultura…'; OUTRA_O='Outra operação…'; CRIAR='Criar item ao salvar'
# atividades usuais de cada operação (cópia de processo_planos.ATV_PADRAO; o cadastro passa a ser a fonte — ver pendências)
ATV_OPERACAO={
    'Pulverização':['Dessecação pré-plantio','Herbicida pré-emergente','Herbicida pós-emergente','Inseticida','Fungicida 1ª aplicação',
                    'Fungicida 2ª aplicação + inseticida','Fungicida 3ª aplicação','Adubação foliar','Controle de ácaro','Dessecação pré-colheita'],
    'Plantio':['Plantio e adubação de base','Plantio','Replantio'],
    'Adubação a lanço':['Calagem','Gessagem','Potássio pré-plantio','Adubação de cobertura','Adubação 1ª parcela','Adubação 2ª parcela'],
    'Tratamento de sementes':['Tratamento de sementes','Inoculação'],
    'Colheita de grãos':['Colheita'],
    'Colheita de café':['Colheita','Repasse'],
    'Poda':['Poda de esqueletamento','Recepa','Desbrota'],
    'Fertirrigação':['Fertirrigação de nitrogênio','Fertirrigação de potássio','Fertirrigação de cálcio']}
PROC_NOMES=[n for _,n in DC.PROCESSOS]
SEMENTES_BASE=sorted(set(DC.SEMENTES.values()))

# ---- auxiliares desta frente (CD-02, CD-06, CD-07 importam daqui; o estado do cabeçalho fica em areas/cadastros.estado_cab) ----
CADC_JS=r'''
// lista sem valor escolhido mostra "Escolha…" (sem isto o navegador exibe a 1ª opção e o rascunho continua vazio)
function cadcEscolha(v,gid){ const F=v[gid+'_F']; if(!F||!F.open||!F.fields) return; F.fields.forEach(f=>{ if(f.isSel&&!f.dis&&f.v==='') f.opts=[{v:'',t:'Escolha…'}].concat(f.opts); }); }
// abre a linha só com os valores gravados (r.v): o texto de exibição da tabela (r.s, ex.: 'Sem preço') não entra no rascunho
function cadcAbrir(self,gid,rid){ const sp=GR(gid); const r=g2find(RW(self,gid),rid); if(!r) return; const d={};
  (sp.edit.fields||[]).forEach(f=>{ const x=r.v[f.k]; d[f.k]=(x===undefined||x===null||x==='')?'':(f.t==='num'?String(x).replace('.',','):String(x)); });
  g2set(self,gid,{fm:{rid,draft:d,orig:Object.assign({},d),errs:{},warn:false,ro:!!r.ro,isNew:false,mode:'form'},fl:null,fmc:null}); }
// valor-padrão que acompanha o registro de origem pelo id: renomear a cultura, o grupo ou o local não deixa o padrão órfão
function cadcPadrao(gid,k,val){ const f=(GR(gid).edit.fields||[]).find(x=>x.k===k); if(f) f.def=val; }
'''

def cd02():
    fname='CD-02.dc.html'; E._reset_screen(fname)
    uso=_uso_cultivar()
    # ---- culturas (fonte) e árvore Cultura → cultivar ----
    cul_rows=[]; tree=[]
    for i,(nome,cod,tipo,unid) in enumerate(DC.CULTURAS,1):
        cid=f'CU{i}'
        cul_rows.append(R(cid,dict(nome=nome,tipo=tipo,unid=unid,cod=cod)))
        kids=[]
        for kid,c,vr,tp,dd,rg in CULTIVARES:
            if c!=nome: continue
            sem=DC.SEMENTES.get((c,vr),CRIAR if tipo=='Anual' else '')
            kids.append(R(kid,dict(nome=vr,cult=c,tipo=tipo,dias=dd,reg=rg,sit='Ativa',uso=uso.get((c,vr),0),sem=sem)))
        tree.append(dict(id=cid,v=dict(nome=nome),s={},p={},kids=kids))
    cv=grid([dict(k='nome',l='Cultura · cultivar',w=300),dict(k='ciclo',l='Ciclo'),dict(k='sem',l='Item de semente',w=260),
             dict(k='uso',l='Cultivos'),dict(k='est',l='Situação',w=320)],
        tree,gid='g_cv',tree=True,dele=False,total=False,frame=False,x0={r['id']:True for r in tree},
        tools=qf_chips('g_cv')+prim('g_cv_new','Cadastrar cultivar'),
        edit=dict(m='form',title='Cultivar',newTitle='Cadastrar cultivar',sub='Registro no RNC é referência, não prova de adaptação local; cultivar em uso não se exclui, inative.',
            fields=[txt('nome','Cultivar ou híbrido'),
                    sel('cult','Cultura',[n for n,*_ in DC.CULTURAS]+[OUTRA_C],**{'def':'Soja'}),
                    txt('ncult','Nome da nova cultura',cond=cond('cult',OUTRA_C)),
                    sel('tipo','Tipo de ciclo',['Anual','Perene'],cond=cond('cult',OUTRA_C),**{'def':'Anual'}),
                    sel('unid','Unidade de produtividade',DC.UNID_PROD,cond=cond('cult',OUTRA_C),**{'def':DC.UNID_PROD[0]},
                        help='Meta e custo por unidade do Planejar safra usam esta unidade.'),
                    num('dias','Ciclo até a colheita','dias',min=30,max=250,cond=cond('tipo','Anual')),
                    sel('sem','Item de semente',SEMENTES_BASE+[CRIAR],cond=cond('tipo','Anual'),**{'def':CRIAR},
                        help='Grupo Sementes, em kg: Compras cota e o Estoque recebe por este item.'),
                    sel('reg','Registro',['RNC · referência','Cadastro próprio'],**{'def':'RNC · referência'}),
                    sel('sit','Situação',['Ativa','Inativa'],**{'def':'Ativa'})]))
    # formulário da cultura (a linha da cultura na árvore abre este formulário)
    grid([dict(k='nome',l='Cultura')],cul_rows,gid='g_cult',search=False,total=False,
         edit=dict(m='form',title='Cultura',sub='Altere nome e unidade de produtividade; o tipo de ciclo fica fixo depois do cadastro.',
             fields=[txt('nome','Nome da cultura'),
                     sel('tipo','Tipo de ciclo',['Anual','Perene'],ro=True,help='Anual pede ciclo e semente na cultivar; perene carrega a data real do ciclo.'),
                     sel('unid','Unidade de produtividade',DC.UNID_PROD,help='Meta e custo por unidade do Planejar safra usam esta unidade.')]))
    # ---- operações (fonte) e árvore Operação → conjunto ----
    ops=[]
    for c in D2.CONJ:
        if c['op'] not in ops: ops.append(c['op'])
    op_rows=[]; rtree=[]
    for i,op in enumerate(ops,1):
        oid=f'OP{i}'
        op_rows.append(R(oid,dict(nome=op,proc=DC.OP_PROC.get(op,''),atvs='; '.join(ATV_OPERACAO.get(op,[])))))
        kids=[]
        for c in D2.CONJ:
            if c['op']!=op: continue
            v=dict(op=op,conj=c['conj'],nome=c['conj'],cult='Todas',maq=c['maq'],impl=c['impl'],pess=c['pess'],pess_rs=c['pess_rs'],fonte=FONTE.get(c['id'],'Equipe da fazenda'),vig='2027-06-30',rend=c['rend'])
            if c['id'] in MODO: v.update(modo='Largura × velocidade',larg=MODO[c['id']][0],vel=MODO[c['id']][1],efic=MODO[c['id']][2])
            else: v.update(modo='Informado',larg='',vel='',efic='')
            ch=D2.custo_h(c); v.update(custo_h=round(ch,2),custo_ha=round(ch/c['rend'],2))
            kids.append(R(c['id'],v))
        rtree.append(dict(id=oid,v=dict(nome=op),s={},p={},kids=kids))
    rend=grid([dict(k='nome',l='Operação · conjunto',w=390),dict(k='cult',l='Cultura'),dict(k='rend',l='Rendimento',t='num',a='r',u='ha/h',d=2),
               dict(k='custo_h',l='Custo por hora',t='num',a='r',pre='R$ ',d=2),dict(k='custo_ha',l='Custo por hectare',t='num',a='r',pre='R$ ',d=2),
               dict(k='fonte',l='Fonte',w=240)],rtree,gid='g_rend',tree=True,dele=False,total=False,frame=False,x0={r['id']:True for r in rtree},
        tools=qf_chips('g_rend')+secbtn('sim_cmp','Comparar com o realizado','Compara o padrão com os apontamentos de campo')+prim('g_rend_new','Cadastrar rendimento'),
        edit=dict(m='form',title='Rendimento',newTitle='Cadastrar rendimento',
            sub='Informe como o conjunto trabalha e quanto custa por hora; rendimento e custo por hectare são recalculados. Planejar safra parte deste padrão.',
            fields=[sel('op','Operação',ops+[OUTRA_O],**{'def':ops[0]}),
                    txt('nop','Nome da nova operação',cond=cond('op',OUTRA_O)),
                    sel('nproc','Processo',PROC_NOMES,cond=cond('op',OUTRA_O),**{'def':'Tratos culturais'},help='Etapa de custo da Estrutura gerencial que recebe o custo desta operação.'),
                    txt('conj','Conjunto ou equipe',help='Máquina + implemento, ou equipe (ex.: 6 pessoas + carreta).'),
                    sel('cult','Cultura',['Todas']+[n for n,*_ in DC.CULTURAS],**{'def':'Todas'},help='O Planejar safra usa o rendimento da cultura do cultivo e, na falta dele, o de Todas.')]
                   + REND_CAMPOS
                   + [sel('fonte','Fonte do dado',['Medição local','Ensaio da fazenda','Fabricante','Referência','Premissa a validar'],**{'def':'Premissa a validar'}),
                      dat('vig','Vigente até')]))
    # formulário da operação (a linha da operação na árvore abre este formulário)
    grid([dict(k='nome',l='Operação')],op_rows,gid='g_op',search=False,total=False,
         edit=dict(m='form',title='Operação',sub='Defina a etapa de custo e as atividades que os Planos agronômicos oferecem para esta operação.',
             fields=[txt('nome','Nome da operação'),
                     sel('proc','Processo',PROC_NOMES,help='Etapa de custo: o custo da O.S. e do orçamento desta operação vai para este processo.'),
                     dict(k='atvs',l='Atividades usuais',t='area',req=False,help='Separe por ponto e vírgula; no plano, a operação vem primeiro e filtra estas atividades.')]))
    # ---- corpo: um bloco com abas; cada aba tem a sua faixa de atenção, o seu filtro rápido e as suas ações (primária por último) ----
    acoes_form('g_cv'); cadx_css()
    corpo=bloco_cad(abas('c2t',['Culturas e cultivares','Operações e rendimentos'],'Cadastros de culturas e operações'),
                    pane('c2t',0,faixa('c2_fx0')+arv(cv))+pane('c2t',1,faixa('c2_fx1')+arv(rend)),'Culturas, cultivares e operações')
    dados=json.dumps(dict(unid=DC.UNID_PROD,sem=SEMENTES_BASE,son=SEG_ON(),soff=SEG_OFF(),
                      defc=next(r['id'] for r in cul_rows if r['v']['nome']=='Soja'),defo='OP1'),ensure_ascii=False)
    js(dict(cmp='Pulverização: padrão 21,6 ha/h × realizado 19,8 ha/h (OS-0421, 4 dias) · revisão sugerida, nada alterado.'),REND_JS
       +CADC_JS+f"\nconst C2={dados}; const OUTRA_C={json.dumps(OUTRA_C)}, OUTRA_O={json.dumps(OUTRA_O)}, CRIAR={json.dumps(CRIAR,ensure_ascii=False)};\n"+r'''
// item de semente criado aqui chega ao CD-06 pelo armazenamento do navegador (chave própria dos cadastros; o CD-06 lê ao abrir)
const CAD_LS='talhao-os-cadastros-v1';
function c2lsSemente(n){ try{ const o=JSON.parse(localStorage.getItem(CAD_LS)||'{}'); o.sementes=o.sementes||[]; if(o.sementes.indexOf(n)<0) o.sementes.push(n); localStorage.setItem(CAD_LS,JSON.stringify(o)); }catch(e){} }
function c2rm(list,id){ const i=list.findIndex(x=>x.id===id); if(i>=0){ list.splice(i,1); return true; } return list.some(x=>x.kids&&c2rm(x.kids,id)); }
function c2opts(gid,k,opts){ const f=(GR(gid).edit.fields||[]).find(x=>x.k===k); if(f) f.opts=opts; }
function c2sem(cult,cv){ return 'Semente de '+String(cult).toLowerCase()+' '+String(cv).replace(/^Híbrido /,''); }
function c2cod(n){ return String(n).normalize('NFD').replace(/[̀-ͯ]/g,'').toUpperCase().replace(/[^A-Z0-9]+/g,'').slice(0,8); }
function c2pais(self,gid){ return RW(self,gid).filter(p=>/^(CU|OP)/.test(p.id)); }
// situação da cultivar e do rendimento: um só cálculo para a linha, o filtro "A resolver", a faixa, o ponto da aba e o cabeçalho
function cvFalta(V){ return V.tipo==='Anual'&&V.sit!=='Inativa'&&(!V.sem||V.sem===CRIAR); }
function cvSit(V){ if(V.sit==='Inativa') return {t:'Inativa',p:[chipc('Inativa','gray')]}; if(cvFalta(V)) return {t:'Sem semente',p:sitX('Sem semente','yellow','Vincular semente'),res:true};
  return {t:'Em dia',p:sitOk('Em dia')}; }
function rdSit(V){ if(V.fonte==='Premissa a validar') return {t:'Premissa a validar',p:sitX('Premissa a validar','yellow','Validar'),res:true}; return {t:V.fonte||'—',p:sitOk(V.fonte||'—')}; }
CAD_ACTS.g_cv=(self,r)=>{ const n=Number(r.v.uso)||0; return [cadExcluir(self,'g_cv',r,'cultivar',n?('usada em '+n+(n>1?' cultivos':' cultivo')+'; inative em vez de excluir'):'')]; };
function PREVALS(self,v){ cadActsIni(self);
  const cul=RW(self,'g_cult'); const dc=cul.find(c=>c.id===C2.defc); cadcPadrao('g_cv','cult',dc?dc.v.nome:'');
  RW(self,'g_cv').forEach(p=>{ const c=cul.find(x=>x.id===p.id); if(!c) return; const C=c.v; const ks=p.kids||[]; p.dr='c2oc_'+p.id; p.v.nome=C.nome;
    p.p.nome=[{k:'b',t:C.nome},{k:'mut',t:ks.length+(ks.length===1?' cultivar':' cultivares')+' · '+C.unid}]; p.s.nome=C.nome;
    p.p.ciclo=[{k:'mut',t:C.tipo}]; p.s.ciclo=C.tipo; ['sem','uso','est'].forEach(k=>{ p.p[k]=[{k:'mut',t:''}]; p.s[k]=''; });
    ks.forEach(r=>{ const V=r.v; V.cult=C.nome; V.tipo=C.tipo; const an=C.tipo==='Anual'; r.dr='c2ab_'+r.id;
      r.p.nome=[{k:'b',t:V.nome||''}]; r.s.nome=V.nome||'';
      const cic=an&&isnum(V.dias)?nf(V.dias)+' dias':''; r.p.ciclo=[cic?{k:'txt',t:cic}:{k:'mut',t:'—'}]; r.s.ciclo=cic;
      const falta=an&&(!V.sem||V.sem===CRIAR);
      r.p.sem=(!an||falta)?[{k:'mut',t:'—'}]:[{k:'link',t:V.sem+' ›',h:'CD-06.dc.html'}]; r.s.sem=(!an||falta)?'':V.sem;
      const n=Number(V.uso)||0; r.p.uso=[{k:(n?'txt':'mut'),t:n?(n+(n>1?' cultivos':' cultivo')):'Sem uso'}]; r.s.uso=String(n); r.nd=n?'em uso':'';
      const S=cvSit(V); r.p.est=S.p; r.s.est=S.t; }); });
  c2opts('g_cv','cult',cul.map(c=>c.v.nome).concat([OUTRA_C]));
  const sems=C2.sem.slice(); leaves(RW(self,'g_cv')).forEach(r=>{ if(r.v.sem&&r.v.sem!==CRIAR&&sems.indexOf(r.v.sem)<0) sems.push(r.v.sem); });
  c2opts('g_cv','sem',sems.sort((a,b)=>a.localeCompare(b,'pt-BR')).concat([CRIAR]));
  const ops=RW(self,'g_op'); const dop=ops.find(o=>o.id===C2.defo); cadcPadrao('g_rend','op',dop?dop.v.nome:'');
  RW(self,'g_rend').forEach(p=>{ const o=ops.find(x=>x.id===p.id); if(!o) return; const O=o.v; const ks=p.kids||[]; p.dr='c2oo_'+p.id; p.v.nome=O.nome;
    p.p.nome=[{k:'b',t:O.nome},{k:'mut',t:(O.proc||'sem processo')+' · '+ks.length+(ks.length===1?' conjunto':' conjuntos')}]; p.s.nome=O.nome;
    ['cult','rend','custo_h','custo_ha','fonte'].forEach(k=>{ p.p[k]=[{k:'mut',t:''}]; p.s[k]=''; });
    ks.forEach(r=>{ const V=r.v; V.op=O.nome; V.nome=V.conj;
      r.p.nome=[{k:'b',t:V.conj||''},{k:'mut',t:rendParam(V)}]; r.s.nome=V.conj||'';
      const cu=V.cult||'Todas'; r.p.cult=[cu==='Todas'?{k:'mut',t:'Todas'}:{k:'txt',t:cu}]; r.s.cult=cu;
      r.p.custo_h=[{k:'txt',t:'R$ '+nf(V.custo_h,2)}]; r.s.custo_h='R$ '+nf(V.custo_h,2);
      const S=rdSit(V); r.p.fonte=S.p; r.s.fonte=V.fonte||''; }); });
  c2opts('g_rend','op',ops.map(o=>o.v.nome).concat([OUTRA_O]));
  c2opts('g_rend','cult',['Todas'].concat(cul.map(c=>c.v.nome)));
  // filtro rápido de cada aba (dentro do bloco)
  cadQf(self,v,'g_cv','c2qf0',[{k:'res',t:'A resolver',f:r=>!!cvSit(r.v).res},{k:'inat',t:'Inativas',f:r=>r.v.sit==='Inativa',oz:true}]);
  cadQf(self,v,'g_rend','c2qf1',[{k:'res',t:'A resolver',f:r=>!!rdSit(r.v).res}]); }
function EXTRAVALS(self,v){ simv(self,v);
  const cvs=cadRegs(RW(self,'g_cv')), rds=cadRegs(RW(self,'g_rend'));
  const semL=cvs.filter(r=>cvFalta(r.v)), premL=rds.filter(r=>r.v.fonte==='Premissa a validar'); const semF=semL.length, prem=premL.length;
  v.c2e=[semF?semF+(semF>1?' cultivares':' cultivar')+' sem semente':'',prem?prem+(prem>1?' premissas':' premissa')+' a validar':''].filter(Boolean).join(' · ')||'Sem pendências';
  cadEstado(v,'c2e',v.c2e,(semF||prem)?'yellow':'green');
  cadAbas(self,v,'c2t','c2aba',[{slug:'culturas',n:cvs.length,cor:semF?'yellow':''},{slug:'operacoes',n:rds.length,cor:prem?'yellow':''}]);
  cadQfPos(self,v,'g_cv','c2qf0'); cadQfPos(self,v,'g_rend','c2qf1'); cadConta(self,v,'g_cv'); cadConta(self,v,'g_rend');
  cadFaixa(v,'c2_fx0',[semF?{n:semF,rot:semF>1?'cultivares anuais sem item de semente':'cultivar anual sem item de semente',reg:semL.map(r=>r.v.cult+' '+r.v.nome).join(', '),verbo:'Vincular semente',
    go:semF===1?()=>cadcAbrir(self,'g_cv',semL[0].id):()=>self.setState({c2qf0:'res'})}:null]);
  cadFaixa(v,'c2_fx1',[prem?{n:prem,rot:prem>1?'rendimentos como premissa':'rendimento como premissa',reg:premL.map(r=>r.v.op+' · '+r.v.conj).join(', '),verbo:'Validar rendimento',
    go:prem===1?()=>g2open(self,GR('g_rend'),premL[0].id,null):()=>self.setState({c2qf1:'res'})}:null]);
  // linha da cultura / da operação abre o formulário próprio
  c2pais(self,'g_cv').forEach(p=>{ v['c2oc_'+p.id]=()=>g2open(self,GR('g_cult'),p.id,null); (p.kids||[]).forEach(r=>{ v['c2ab_'+r.id]=()=>cadcAbrir(self,'g_cv',r.id); }); });
  c2pais(self,'g_rend').forEach(p=>{ v['c2oo_'+p.id]=()=>g2open(self,GR('g_op'),p.id,null); });
 // exclusão sai da linha: fica no painel da cultivar (Excluir cultivar, com a causa quando está em uso)
  // trocar a cultura no formulário da cultivar traz o tipo de ciclo dela (mostra ou esconde ciclo e semente)
  const F=v.g_cv_F; if(F&&F.open&&F.fields){ const f=F.fields.find(x=>x.fid==='fx_g_cv_cult');
    if(f&&!f.dis) f.set=(e)=>{ const cur=g2st(self,'g_cv').fm; if(!cur) return; const val=e.target.value; const c=RW(self,'g_cult').find(x=>x.v.nome===val);
      const d=Object.assign({},cur.draft,{cult:val}); if(c) d.tipo=c.v.tipo; const er=Object.assign({},cur.errs||{}); delete er.cult; delete er.sem;
      g2set(self,'g_cv',{fm:Object.assign({},cur,{draft:d,errs:er,warn:false})}); }; }
  valida(self,v,'g_cv',(d,fm)=>{ const e={}; const cul=RW(self,'g_cult'); const nova=d.cult===OUTRA_C; const cn=nova?String(d.ncult||'').trim():d.cult;
    if(!nova&&d.cult&&!cul.some(c=>c.v.nome===d.cult)) e.cult='Escolha a cultura.';
    if(nova&&cn&&cul.some(c=>c.v.nome.toLowerCase()===cn.toLowerCase())) e.ncult=cn+' já existe; escolha na lista Cultura.';
    const dup=leaves(RW(self,'g_cv')).find(r=>r.id!==fm.rid&&r.v.cult&&r.v.cult.toLowerCase()===cn.toLowerCase()&&String(r.v.nome).trim().toLowerCase()===String(d.nome||'').trim().toLowerCase());
    if(dup) e.nome=d.nome+' já está cadastrada em '+cn+'.';
    if(d.tipo==='Anual'&&d.sem&&d.sem!==CRIAR){ const pre=('Semente de '+cn).toLowerCase(); const dono=leaves(RW(self,'g_cv')).find(r=>r.id!==fm.rid&&r.v.sem===d.sem);
      if(d.sem.toLowerCase().indexOf(pre)!==0) e.sem='Escolha uma semente de '+cn.toLowerCase()+' ou "'+CRIAR+'".';
      else if(dono) e.sem=d.sem+' já é a semente da cultivar '+dono.v.nome+'.'; }
    return e; });
  valida(self,v,'g_cult',(d,fm)=>{ const e={}; const o=fm.rid?RW(self,'g_cult').find(c=>c.id===fm.rid):null; self.__c2old=o?{id:o.id,nome:o.v.nome}:null; const n=String(d.nome||'').trim().toLowerCase(); if(RW(self,'g_cult').some(c=>c.id!==fm.rid&&c.v.nome.toLowerCase()===n)) e.nome='Já existe a cultura '+d.nome+'.'; return e; });
  valida(self,v,'g_rend',(d,fm)=>{ const e={}; const nova=d.op===OUTRA_O; const on=nova?String(d.nop||'').trim():d.op;
    if(nova&&on&&RW(self,'g_op').some(o=>o.v.nome.toLowerCase()===on.toLowerCase())) e.nop=on+' já existe; escolha na lista Operação.';
    if(!nova&&d.op&&!RW(self,'g_op').some(o=>o.v.nome===d.op)) e.op='Escolha a operação.';
    if(d.cult&&d.cult!=='Todas'&&!RW(self,'g_cult').some(c=>c.v.nome===d.cult)) e.cult='Escolha a cultura.';
    const cu=d.cult||'Todas'; const dup=leaves(RW(self,'g_rend')).find(r=>r.id!==fm.rid&&r.v.op===on&&(r.v.cult||'Todas')===cu&&String(r.v.conj).trim().toLowerCase()===String(d.conj||'').trim().toLowerCase());
    if(dup) e.conj='Este conjunto já tem rendimento em '+on+' para '+(cu==='Todas'?'todas as culturas':cu)+'.'; return e; });
  valida(self,v,'g_op',(d,fm)=>{ const e={}; const n=String(d.nome||'').trim().toLowerCase(); if(RW(self,'g_op').some(o=>o.id!==fm.rid&&o.v.nome.toLowerCase()===n)) e.nome='Já existe a operação '+d.nome+'.'; return e; });
  self.g2live=(gid,k,d)=>(gid==='g_rend'?rendLive(k,d):null);
  ['g_cv','g_cult','g_rend','g_op'].forEach(g=>cadcEscolha(v,g));
  // coloca o registro salvo sob o pai certo (novo ou com pai trocado) e abre o pai
  const soPai=(gid,rows,r,pid)=>{ const par=rows.find(p=>p.id===pid); const cur=rows.find(p=>(p.kids||[]).some(k=>k.id===r.id));
    if(cur!==par){ c2rm(rows,r.id); par.kids=par.kids||[]; par.kids.push(r); }
    const x=Object.assign({},g2st(self,gid).x||GR(gid).x0||{}); x[pid]=true; g2set(self,gid,{rows:rows,x:x,fl:r.id}); };
  self.g2after=(gid,rows,r)=>{ if(!r) return;
    if(gid==='g_cv'){ const cul=g2clone(RW(self,'g_cult')); const msg=[]; let c;
      if(r.v.cult===OUTRA_C){ const nm=String(r.v.ncult).trim(); c={id:'CU'+(cul.length+1)+'_'+String(Date.now()).slice(-4),v:{nome:nm,tipo:r.v.tipo||'Anual',unid:r.v.unid||C2.unid[0],cod:c2cod(nm)},s:{},p:{}};
        cul.push(c); g2set(self,'g_cult',{rows:cul}); rows.push({id:c.id,v:{nome:nm},s:{},p:{},kids:[]}); msg.push('cultura '+nm+' cadastrada ('+c.v.tipo+' · '+c.v.unid+')'); }
      else c=cul.find(x=>x.v.nome===r.v.cult);
      if(!c) return;
      r.v.cult=c.v.nome; r.v.ncult=''; r.v.tipo=c.v.tipo;
      if(c.v.tipo==='Anual'){ if(!r.v.sem||r.v.sem===CRIAR){ r.v.sem=c2sem(c.v.nome,r.v.nome); c2lsSemente(r.v.sem); msg.push('item '+r.v.sem+' criado em Produtos, unidades e locais (Sementes · kg)'); } else msg.push('semente '+r.v.sem); }
      else r.v.sem='';
      soPai('g_cv',rows,r,c.id); self.setState({g2toast:'Salvo: '+r.v.nome+' em '+c.v.nome+' · '+msg.join(' · ')+'.'}); return; }
    if(gid==='g_cult'){ const o=self.__c2old; let n=0;
      if(o&&o.id===r.id&&o.nome!==r.v.nome){ const rr=g2clone(RW(self,'g_rend')); leaves(rr).forEach(x=>{ if(x.v.cult===o.nome){ x.v.cult=r.v.nome; n++; } }); if(n) g2set(self,'g_rend',{rows:rr}); }
      self.setState({g2toast:'Salvo: cultura '+r.v.nome+' · produtividade em '+r.v.unid+(n?' · '+n+(n>1?' rendimentos passam':' rendimento passa')+' a '+r.v.nome:'')+'. Planejar safra usa esta unidade na meta.'}); return; }
    if(gid==='g_op'){ const n=ml(r.v.atvs).length; self.setState({g2toast:'Salvo: '+r.v.nome+' · processo '+r.v.proc+' · '+n+(n===1?' atividade usual':' atividades usuais')+' nos Planos agronômicos.'}); return; }
    if(gid==='g_rend'){ const ops=g2clone(RW(self,'g_op')); let o; let pre='';
      if(r.v.op===OUTRA_O){ const nm=String(r.v.nop).trim(); o={id:'OP'+(ops.length+1)+'_'+String(Date.now()).slice(-4),v:{nome:nm,proc:r.v.nproc||'Tratos culturais',atvs:''},s:{},p:{}};
        ops.push(o); g2set(self,'g_op',{rows:ops}); rows.push({id:o.id,v:{nome:nm},s:{},p:{},kids:[]}); pre='Operação '+nm+' cadastrada ('+o.v.proc+') · '; }
      else o=ops.find(x=>x.v.nome===r.v.op);
      if(!o) return;
      r.v.op=o.v.nome; r.v.nop=''; r.v.cult=r.v.cult||'Todas'; const V=rendCalc(r.v);
      soPai('g_rend',rows,r,o.id);
      self.setState({g2toast:pre+'Salvo: '+V.op+' rende '+nf(V.rend,2)+' ha/h a R$ '+nf(V.custo_h,2)+'/h e R$ '+nf(V.custo_ha,2)+'/ha. Novos planejamentos usam este padrão.'}); } }; }
''')
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a tabela da aba rola
    shell37('CD-02','Culturas, cultivares e operações',corpo,fname=fname,status=None,primary_html=None,search=False)
    estado_cab(fname,'Culturas, cultivares e operações','c2e')
