# -*- coding: utf-8 -*-
"""CD-02 · Culturas e cultivares e CD-08 · Operações e rendimentos (módulo próprio; areas.cadastros.build() usa cd02() e cd08()).
Até 13/10/2026 eram duas abas do CD-02; o proprietário pediu Operações no lugar mais correto: cadastro próprio.
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
from areas.cadastros import (secbtn, prim_cab, QF_CAD, bloco_cad, estado_cab, acoes_form)

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
// chave dos cadastros no navegador (o CD-06 lê as sementes; CD-02 e CD-08 leem as culturas)
const CAD_LS='talhao-os-cadastros-v1';
// fonte única de culturas entre telas (CD08-CULTURA-01, revisão Codex de 13/10): o CD-02 grava a lista atual a cada mudança (cadLsSe) e o
// CD-02 e o CD-08 leem ao abrir. O CD-08 guarda os seus rendimentos e operações do mesmo jeito; cada rendimento guarda o id da cultura
// (cultId) e, ao abrir, mostra o nome atual dela: renomear no CD-02 muda o nome no CD-08 sem perder custos (sem catálogo paralelo)
function cadCulLer(){ try{ const o=JSON.parse(localStorage.getItem(CAD_LS)||'{}'); return Array.isArray(o.culturas)&&o.culturas.length?o.culturas:null; }catch(e){ return null; } }
// grava a chave k do CAD_LS só quando o valor muda (cada desenho compara com o último gravado): salvar, excluir e criar entram iguais
// CD08-GRAVA-01 (revisão Codex de 14/10, S2): a marca do último gravado só muda depois da gravação; a falha volta como motivo (o salvar da
// tela chama cadLsGrava pelo g2persist e, se falhar, não confirma e devolve o rascunho); as chaves do mesmo salvar vão numa gravação só
function cadLsGrava(self,obj){ self.__lsU=self.__lsU||{}; const ks=Object.keys(obj).filter(k=>self.__lsU[k]!==JSON.stringify(obj[k])); if(!ks.length) return '';
  try{ const o=JSON.parse(localStorage.getItem(CAD_LS)||'{}'); ks.forEach(k=>{ o[k]=obj[k]; }); const j=JSON.stringify(o); if(j.length>4e6) throw new Error('cadastro grande demais');
    localStorage.setItem(CAD_LS,j); }
  catch(e){ return 'o navegador não gravou o cadastro ('+((e&&e.name&&e.name!=='Error')?e.name:(e&&e.message)||'erro')+').'; }
  ks.forEach(k=>{ self.__lsU[k]=JSON.stringify(obj[k]); }); return ''; }
function cadLsSe(self,k,val){ return !cadLsGrava(self,{[k]:val}); }
function cadLsLer(k){ try{ const o=JSON.parse(localStorage.getItem(CAD_LS)||'{}'); return o[k]||null; }catch(e){ return null; } }
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
    # uma variável por coluna (TABELAS-FOCO, 04/10/2026): a linha da cultura mostra o tipo de ciclo e a unidade de produtividade (DEC-0510-03);
    # a da cultivar, o ciclo em dias, a semente, os cultivos (número) e a situação
    # revisão TABR (A1, 09/10): a Situação logo depois da identificação, à vista sem rolar
    cv=grid([dict(k='nome',l='Cultura › cultivar',w=200),dict(k='est',l='Situação',w=230),dict(k='tipo',l='Tipo de ciclo'),dict(k='unid',l='Unidade de produtividade',w=170),
             dict(k='dias',l='Ciclo',t='num',a='r',un='dias'),dict(k='sem',l='Item de semente',w=220),dict(k='uso',l='Cultivos',t='num',a='r')],
        tree,gid='g_cv',tree=True,dele=False,total=False,x0={r['id']:True for r in tree},qf=QF_CAD,
        edit=dict(m='form',title='Cultivar',newTitle='Cadastrar cultivar',sub='Registro no RNC é referência, não prova de adaptação local; cultivar em uso não se exclui, inative.',
            fields=[txt('nome','Cultivar ou híbrido'),
                    sel('cult','Cultura',[n for n,*_ in DC.CULTURAS]+[OUTRA_C],**{'def':'Soja'}),
                    txt('ncult','Nome da nova cultura',cond=cond('cult',OUTRA_C)),
                    sel('tipo','Tipo de ciclo',['Anual','Perene'],cond=cond('cult',OUTRA_C),**{'def':'Anual'}),
                    sel('unid','Unidade de produtividade',DC.UNID_PROD,cond=cond('cult',OUTRA_C),**{'def':DC.UNID_PROD[0]},
                        help='Padrão da cultura na meta e no custo por unidade do Planejar safra; o seletor "Unidade de produtividade" das tabelas também mostra kg/ha, t/ha e sc 60 kg/ha.'),
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
                     sel('unid','Unidade de produtividade',DC.UNID_PROD,help='Padrão da cultura na meta e no custo por unidade do Planejar safra; o seletor "Unidade de produtividade" das tabelas também mostra kg/ha, t/ha e sc 60 kg/ha.')]))
    # ---- corpo: um bloco só (13/10/2026, proprietário: "tire cadastro de operações de culturas e cultivares, e coloque no lugar mais correto";
    # Operações e rendimentos virou o CD-08, ao lado deste no grupo Propriedade e produção da tela Cadastros) ----
    # padrão comum (16/10/2026): bloco e grade do motor; "Criar cultivar" no cabeçalho (BOT-01/03/05); sem faixa de atenção (TAB-06/07)
    acoes_form('g_cv')
    corpo=bloco_cad('',cv,'Culturas e cultivares',titulo='Cultivares por cultura')
    dados=json.dumps(dict(unid=DC.UNID_PROD,sem=SEMENTES_BASE,son=SEG_ON(),soff=SEG_OFF(),
                      defc=next(r['id'] for r in cul_rows if r['v']['nome']=='Soja')),ensure_ascii=False)
    js({},CADC_JS+f"\nconst C2={dados}; const OUTRA_C={json.dumps(OUTRA_C)}, CRIAR={json.dumps(CRIAR,ensure_ascii=False)};\n"+r'''
// item de semente criado aqui chega ao CD-06 pelo armazenamento do navegador (chave própria dos cadastros, CAD_LS; o CD-06 lê ao abrir).
// CD08-GRAVA-01 residual (revisão Codex de 14/10, S2): a semente nova não grava sozinha; fica pendente e vai na MESMA gravação das culturas e
// cultivares (c2grava). Se a gravação falhar, nada entra (nem a semente) e a pendência some com o rascunho devolvido.
function c2lsSemente(self,n){ self.__c2semNova=self.__c2semNova||[]; if(self.__c2semNova.indexOf(n)<0) self.__c2semNova.push(n); }
function c2rm(list,id){ const i=list.findIndex(x=>x.id===id); if(i>=0){ list.splice(i,1); return true; } return list.some(x=>x.kids&&c2rm(x.kids,id)); }
function c2opts(gid,k,opts){ const f=(GR(gid).edit.fields||[]).find(x=>x.k===k); if(f) f.opts=opts; }
function c2sem(cult,cv){ return 'Semente de '+String(cult).toLowerCase()+' '+String(cv).replace(/^Híbrido /,''); }
function c2cod(n){ return String(n).normalize('NFD').replace(/[̀-ͯ]/g,'').toUpperCase().replace(/[^A-Z0-9]+/g,'').slice(0,8); }
function c2pais(self,gid){ return RW(self,gid).filter(p=>/^CU/.test(p.id)); }
// situação da cultivar e do rendimento: um só cálculo para a linha, o filtro "A resolver", a faixa, o ponto da aba e o cabeçalho
function cvFalta(V){ return V.tipo==='Anual'&&V.sit!=='Inativa'&&(!V.sem||V.sem===CRIAR); }
function cvSit(V){ if(V.sit==='Inativa') return {t:'Inativa',p:[chipc('Inativa','gray')]}; if(cvFalta(V)) return {t:'Sem semente',p:sitX('Sem semente','yellow','Vincular semente'),res:true};
  return {t:'Em dia',p:sitOk('Em dia')}; }
CAD_ACTS.g_cv=(self,r)=>{ const n=Number(r.v.uso)||0; return [cadExcluir(self,'g_cv',r,'cultivar',n?('usada em '+n+(n>1?' cultivos':' cultivo')+'; inative em vez de excluir'):'')]; };
function c2culIni(self){ if(self.__culLido) return; self.__culLido=1; const L=cadCulLer(); if(!L) return;
  const all=Object.assign({},self.state.g2||{}); const cvG=cadLsLer('cultivares'); const cv=g2clone(Array.isArray(cvG)?cvG:RW(self,'g_cv')); const ant={};   /* cultivares gravadas junto */ RW(self,'g_cult').forEach(c=>{ ant[c.id]=c.v.nome; });
  L.forEach(c=>{ const p=cv.find(x=>x.id===c.id), velho=ant[c.id];
    if(!p) cv.push({id:c.id,v:{nome:c.v.nome},s:{},p:{},kids:[]});
    else if(velho&&velho!==c.v.nome) (p.kids||[]).forEach(k=>{ if(k.v.cult===velho) k.v.cult=c.v.nome; }); });
  all.g_cult=Object.assign({},all.g_cult||{},{rows:L.map(c=>({id:c.id,v:Object.assign({},c.v),s:{},p:{}}))}); all.g_cv=Object.assign({},all.g_cv||{},{rows:cv}); self.state.g2=all; }
function PREVALS(self,v){ cadActsIni(self); c2culIni(self);
  const cul=RW(self,'g_cult'); const dc=cul.find(c=>c.id===C2.defc); cadcPadrao('g_cv','cult',dc?dc.v.nome:'');
  RW(self,'g_cv').forEach(p=>{ const c=cul.find(x=>x.id===p.id); if(!c) return; const C=c.v; const ks=p.kids||[]; p.dr='c2oc_'+p.id; p.v.nome=C.nome;
    p.p.nome=[{k:'b',t:C.nome},{k:'mut',t:ks.length+(ks.length===1?' cultivar':' cultivares')}]; p.s.nome=C.nome;
    p.p.tipo=[{k:'txt',t:C.tipo}]; p.s.tipo=C.tipo; p.p.unid=[{k:'txt',t:C.unid}]; p.s.unid=C.unid;
    ['dias','sem','uso','est'].forEach(k=>{ p.p[k]=[{k:'mut',t:''}]; p.s[k]=''; });
    ks.forEach(r=>{ const V=r.v; V.cult=C.nome; V.tipo=C.tipo; const an=C.tipo==='Anual'; r.dr='c2ab_'+r.id;
      // tipo de ciclo e unidade são da cultura: a cultivar mostra os da cultura (apagados), para o filtro da coluna valer nas cultivares
      r.p.nome=[{k:'b',t:V.nome||''}]; r.s.nome=V.nome||''; r.p.tipo=[{k:'mut',t:C.tipo}]; r.s.tipo=C.tipo; r.p.unid=[{k:'mut',t:C.unid}]; r.s.unid=C.unid;
      const cic=an&&isnum(V.dias)&&String(V.dias)!==''; r.p.dias=[cic?{k:'txt',t:nf(V.dias)}:{k:'mut',t:'—'}]; r.s.dias=cic?nf(V.dias):'';
      const falta=an&&(!V.sem||V.sem===CRIAR);
      r.p.sem=(!an||falta)?[{k:'mut',t:'—'}]:[{k:'link',t:V.sem+' ›',h:'CD-06.dc.html'}]; r.s.sem=(!an||falta)?'':V.sem;
      const n=Number(V.uso)||0; r.p.uso=[{k:(n?'txt':'mut'),t:String(n)}]; r.s.uso=String(n); r.nd=n?'em uso':'';
      const S=cvSit(V); r.p.est=S.p; r.s.est=S.t; }); });
  c2opts('g_cv','cult',cul.map(c=>c.v.nome).concat([OUTRA_C]));
  const sems=C2.sem.slice(); leaves(RW(self,'g_cv')).forEach(r=>{ if(r.v.sem&&r.v.sem!==CRIAR&&sems.indexOf(r.v.sem)<0) sems.push(r.v.sem); });
  c2opts('g_cv','sem',sems.sort((a,b)=>a.localeCompare(b,'pt-BR')).concat([CRIAR]));
  // filtro rápido de cada aba (dentro do bloco)
  cadQf(self,v,'g_cv','c2qf0',[{k:'res',t:'A resolver',f:r=>!!cvSit(r.v).res},{k:'inat',t:'Inativas',f:r=>r.v.sit==='Inativa',oz:true}]); }
function c2grava(self){ const nov=self.__c2semNova||[]; self.__c2semNova=[];
  const obj={culturas:RW(self,'g_cult').map(c=>({id:c.id,v:Object.assign({},c.v)})),cultivares:RW(self,'g_cv')};
  if(nov.length){ const ss=(cadLsLer('sementes')||[]).slice(); nov.forEach(n=>{ if(ss.indexOf(n)<0) ss.push(n); }); obj.sementes=ss; }
  return cadLsGrava(self,obj); }
function EXTRAVALS(self,v){ simv(self,v); self.g2persist=()=>c2grava(self); c2grava(self);
  const cvs=cadRegs(RW(self,'g_cv'));
  const semL=cvs.filter(r=>cvFalta(r.v)); const semF=semL.length;
  v.c2e=semF?semF+(semF>1?' cultivares':' cultivar')+' sem semente':'Sem pendências';
  cadEstado(v,'c2e',v.c2e,semF?'yellow':'green');
  cadQfPos(self,v,'g_cv','c2qf0'); cadConta(self,v,'g_cv');
  // linha da cultura / da operação abre o formulário próprio
  c2pais(self,'g_cv').forEach(p=>{ v['c2oc_'+p.id]=()=>g2open(self,GR('g_cult'),p.id,null); (p.kids||[]).forEach(r=>{ v['c2ab_'+r.id]=()=>cadcAbrir(self,'g_cv',r.id); }); });
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
  ['g_cv','g_cult'].forEach(g=>cadcEscolha(v,g));
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
      if(c.v.tipo==='Anual'){ if(!r.v.sem||r.v.sem===CRIAR){ r.v.sem=c2sem(c.v.nome,r.v.nome); c2lsSemente(self,r.v.sem); msg.push('item '+r.v.sem+' criado em Produtos, unidades e locais (Sementes · kg)'); } else msg.push('semente '+r.v.sem); }
      else r.v.sem='';
      soPai('g_cv',rows,r,c.id); self.setState({g2toast:'Salvo: '+r.v.nome+' em '+c.v.nome+' · '+msg.join(' · ')+'.'}); return; }
    if(gid==='g_cult'){
      self.setState({g2toast:'Salvo: cultura '+r.v.nome+' · produtividade em '+r.v.unid+'. É o Padrão da cultura na meta do Planejar safra.'}); return; }
  }; }
''')
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a tabela rola
    shell37('CD-02','Culturas e cultivares',corpo,fname=fname,status=None,primary_html=prim_cab('Criar cultivar','g_cv_new'),search=False)
    estado_cab(fname,'Culturas e cultivares','c2e')


def cd08():
    """CD-08 · Operações e rendimentos (13/10/2026, saiu do CD-02): árvore Operação → conjunto. A linha da operação abre processo (etapa de
    custo da Estrutura gerencial) e atividades usuais; a do conjunto abre o rendimento com a cultura (Todas ou uma), no formulário do
    Planejar safra (REND_CAMPOS). As culturas da lista vêm do cadastro de culturas (DC.CULTURAS)."""
    fname='CD-08.dc.html'; E._reset_screen(fname)
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
    # processo na linha da operação; custos "Custo R$/h" e "Custo R$/ha" com a unidade na célula (proprietário, 05/10/2026). Revisão TABR (A1,
    # 09/10): a fonte do dado (a premissa a validar é a pendência, com o verbo) logo depois do conjunto; modo, largura, velocidade e eficiência,
    # que formam o rendimento, ficam no painel (o mesmo formulário do Planejar safra), e a grade cabe sem rolar a 1440 px
    rend=grid([dict(k='nome',l='Operação › conjunto',w=300),dict(k='fonte',l='Fonte',w=200),dict(k='proc',l='Processo',w=140),dict(k='cult',l='Cultura'),
               dict(k='rend',l='Rendimento',t='num',a='r',un='ha/h',d=2),dict(k='custo_h',l='R$/h',t='num',a='r',d=2),dict(k='custo_ha',l='R$/ha',t='num',a='r',d=2)],rtree,gid='g_rend',tree=True,dele=False,total=False,x0={r['id']:True for r in rtree},qf=QF_CAD,
        tools=secbtn('sim_cmp','Comparar com o realizado','Compara o padrão com os apontamentos de campo'),
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
    corpo=bloco_cad('',rend,'Operações e rendimentos',titulo='Rendimentos por operação')
    dados=json.dumps(dict(cul=[dict(id=f'CU{i}',nome=n) for i,(n,*_) in enumerate(DC.CULTURAS,1)],defo='OP1'),ensure_ascii=False)   # mesmos ids do CD-02
    js(dict(cmp='Pulverização: padrão 21,6 ha/h × realizado 19,8 ha/h (OS-0421, 4 dias) · revisão sugerida, nada alterado.'),REND_JS
       +CADC_JS+f"\nconst C8={dados}; const OUTRA_O={json.dumps(OUTRA_O)};\n"+r'''
function c2rm(list,id){ const i=list.findIndex(x=>x.id===id); if(i>=0){ list.splice(i,1); return true; } return list.some(x=>x.kids&&c2rm(x.kids,id)); }

function c2opts(gid,k,opts){ const f=(GR(gid).edit.fields||[]).find(x=>x.k===k); if(f) f.opts=opts; }

function c2pais(self,gid){ return RW(self,gid).filter(p=>/^OP/.test(p.id)); }
// a fonte do dado é texto; só a premissa a validar é pendência (chip com o verbo). Antes a fonte saía em chip verde de estado (revisão TABR A11)
function rdSit(V){ if(V.fonte==='Premissa a validar') return {t:'Premissa a validar',p:sitX('Premissa a validar','yellow','Validar'),res:true}; return {t:V.fonte||'—',p:[V.fonte?{k:'txt',t:V.fonte}:{k:'mut',t:'—'}]}; }
// culturas da fonte única (CD-02, cadCulLer) ou, sem ela, as do cenário; ao abrir, os rendimentos seguem o id da cultura renomeada
function c8culs(){ return C8.lista||C8.cul; }   // [{id,nome}] atuais
function c8cul(){ return c8culs().map(c=>c.nome); }
function c8culIni(self){ if(self.__culLido) return; self.__culLido=1; const L=cadCulLer(); if(L) C8.lista=L.map(c=>({id:c.id,nome:c.v.nome}));
  const G=cadLsLer('cd08'), all=Object.assign({},self.state.g2||{}); const rr=g2clone(G&&Array.isArray(G.rend)?G.rend:RW(self,'g_rend'));
  if(G&&Array.isArray(G.op)) all.g_op=Object.assign({},all.g_op||{},{rows:G.op});
  const porId={}, seedId={}; c8culs().forEach(c=>{ porId[c.id]=c.nome; }); C8.cul.forEach(c=>{ seedId[c.nome]=c.id; });
  leaves(rr).forEach(x=>{ const V=x.v; if(!V.cult||V.cult==='Todas') return; const id=V.cultId||seedId[V.cult]; if(id&&porId[id]){ V.cultId=id; V.cult=porId[id]; } });
  all.g_rend=Object.assign({},all.g_rend||{},{rows:rr}); self.state.g2=all; }
function PREVALS(self,v){ cadActsIni(self); c8culIni(self);
  const ops=RW(self,'g_op'); const dop=ops.find(o=>o.id===C8.defo); cadcPadrao('g_rend','op',dop?dop.v.nome:'');
  RW(self,'g_rend').forEach(p=>{ const o=ops.find(x=>x.id===p.id); if(!o) return; const O=o.v; const ks=p.kids||[]; p.dr='c2oo_'+p.id; p.v.nome=O.nome;
    p.p.nome=[{k:'b',t:O.nome},{k:'mut',t:ks.length+(ks.length===1?' conjunto':' conjuntos')}]; p.s.nome=O.nome;
    p.p.proc=[O.proc?{k:'txt',t:O.proc}:{k:'mut',t:'sem processo'}]; p.s.proc=O.proc||'';
    ['cult','rend','custo_h','custo_ha','fonte'].forEach(k=>{ p.p[k]=[{k:'mut',t:''}]; p.s[k]=''; });
    ks.forEach(r=>{ const V=r.v; V.op=O.nome; V.nome=V.conj;
      r.p.nome=[{k:'b',t:V.conj||''}]; r.s.nome=V.conj||''; r.p.proc=[{k:'mut',t:O.proc||'—'}]; r.s.proc=O.proc||'';   // processo da operação (filtro vale no conjunto)
      /* modo, largura, velocidade e eficiência ficam no painel (formulário do rendimento) */
      const cu=V.cult||'Todas'; r.p.cult=[cu==='Todas'?{k:'mut',t:'Todas'}:{k:'txt',t:cu}]; r.s.cult=cu;
      r.p.custo_h=[{k:'txt',t:nf(V.custo_h,2)}]; r.s.custo_h=nf(V.custo_h,2);   // a coluna põe "R$ …/h" (unidade na célula)
      const S=rdSit(V); r.p.fonte=S.p; r.s.fonte=V.fonte||''; }); });
  c2opts('g_rend','op',ops.map(o=>o.v.nome).concat([OUTRA_O]));
  c2opts('g_rend','cult',['Todas'].concat(c8cul()));
  cadQf(self,v,'g_rend','c2qf1',[{k:'res',t:'A resolver',f:r=>!!rdSit(r.v).res}]); }
function EXTRAVALS(self,v){ simv(self,v); const c8grava=()=>cadLsGrava(self,{cd08:{rend:RW(self,'g_rend'),op:RW(self,'g_op')}}); self.g2persist=c8grava; c8grava();
  const rds=cadRegs(RW(self,'g_rend')); const premL=rds.filter(r=>r.v.fonte==='Premissa a validar'); const prem=premL.length;
  v.c8e=prem?prem+(prem>1?' premissas':' premissa')+' a validar':'Sem pendências';
  cadEstado(v,'c8e',v.c8e,prem?'yellow':'green');
  cadQfPos(self,v,'g_rend','c2qf1'); cadConta(self,v,'g_rend');
  // linha da operação abre o formulário próprio
  c2pais(self,'g_rend').forEach(p=>{ v['c2oo_'+p.id]=()=>g2open(self,GR('g_op'),p.id,null); });
  valida(self,v,'g_rend',(d,fm)=>{ const e={}; const nova=d.op===OUTRA_O; const on=nova?String(d.nop||'').trim():d.op;
    if(nova&&on&&RW(self,'g_op').some(o=>o.v.nome.toLowerCase()===on.toLowerCase())) e.nop=on+' já existe; escolha na lista Operação.';
    if(!nova&&d.op&&!RW(self,'g_op').some(o=>o.v.nome===d.op)) e.op='Escolha a operação.';
    if(d.cult&&d.cult!=='Todas'&&c8cul().indexOf(d.cult)<0) e.cult='Escolha a cultura.';
    const cu=d.cult||'Todas'; const dup=leaves(RW(self,'g_rend')).find(r=>r.id!==fm.rid&&r.v.op===on&&(r.v.cult||'Todas')===cu&&String(r.v.conj).trim().toLowerCase()===String(d.conj||'').trim().toLowerCase());
    if(dup) e.conj='Este conjunto já tem rendimento em '+on+' para '+(cu==='Todas'?'todas as culturas':cu)+'.'; return e; });
  valida(self,v,'g_op',(d,fm)=>{ const e={}; const n=String(d.nome||'').trim().toLowerCase(); if(RW(self,'g_op').some(o=>o.id!==fm.rid&&o.v.nome.toLowerCase()===n)) e.nome='Já existe a operação '+d.nome+'.'; return e; });

  self.g2live=(gid,k,d)=>(gid==='g_rend'?rendLive(k,d):null);
  ['g_rend','g_op'].forEach(g=>cadcEscolha(v,g));
  // coloca o registro salvo sob o pai certo (novo ou com pai trocado) e abre o pai
  const soPai=(gid,rows,r,pid)=>{ const par=rows.find(p=>p.id===pid); const cur=rows.find(p=>(p.kids||[]).some(k=>k.id===r.id));
    if(cur!==par){ c2rm(rows,r.id); par.kids=par.kids||[]; par.kids.push(r); }
    const x=Object.assign({},g2st(self,gid).x||GR(gid).x0||{}); x[pid]=true; g2set(self,gid,{rows:rows,x:x,fl:r.id}); };
  self.g2after=(gid,rows,r)=>{ if(!r) return;
    if(gid==='g_op'){ const n=ml(r.v.atvs).length; self.setState({g2toast:'Salvo: '+r.v.nome+' · processo '+r.v.proc+' · '+n+(n===1?' atividade usual':' atividades usuais')+' nos Planos agronômicos.'}); return; }
    if(gid==='g_rend'){ const ops=g2clone(RW(self,'g_op')); let o; let pre='';
      if(r.v.op===OUTRA_O){ const nm=String(r.v.nop).trim(); o={id:'OP'+(ops.length+1)+'_'+String(Date.now()).slice(-4),v:{nome:nm,proc:r.v.nproc||'Tratos culturais',atvs:''},s:{},p:{}};
        ops.push(o); g2set(self,'g_op',{rows:ops}); rows.push({id:o.id,v:{nome:nm},s:{},p:{},kids:[]}); pre='Operação '+nm+' cadastrada ('+o.v.proc+') · '; }
      else o=ops.find(x=>x.v.nome===r.v.op);
      if(!o) return;
      r.v.op=o.v.nome; r.v.nop=''; r.v.cult=r.v.cult||'Todas'; const cx=c8culs().find(c=>c.nome===r.v.cult); r.v.cultId=cx?cx.id:''; const V=rendCalc(r.v);
      soPai('g_rend',rows,r,o.id);
      self.setState({g2toast:pre+'Salvo: '+V.op+' rende '+nf(V.rend,2)+' ha/h a R$ '+nf(V.custo_h,2)+'/h e R$ '+nf(V.custo_ha,2)+'/ha. Novos planejamentos usam este padrão.'}); } }; }
''')
    HEIGHTS37[fname]=1000
    shell37('CD-08','Operações e rendimentos',corpo,fname=fname,status=None,primary_html=prim_cab('Criar rendimento','g_rend_new'),search=False)
    estado_cab(fname,'Operações e rendimentos','c8e')
