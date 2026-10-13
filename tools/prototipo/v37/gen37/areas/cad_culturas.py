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
from areas.cadastros import (cadx_css, abas, pane, se, faixa, prim, secbtn, qf_chips, bloco_cad, estado_cab, acoes_form, arv,
                             md, mestre, det_cab, vazio, md_css, criar_cab)

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
function cadcEscolha(v,gid){ const F=v[gid+'_F']; if(!F||!F.open||!F.fields) return; F.fields.forEach(f=>{ if(f.isSel&&!f.dis&&f.v===''&&!(f.opts||[]).some(o=>o&&o.v==='')) f.opts=[{v:'',t:'Escolha…'}].concat(f.opts); }); }
// abre a linha só com os valores gravados (r.v): o texto de exibição da tabela (r.s, ex.: 'Sem preço') não entra no rascunho
function cadcAbrir(self,gid,rid){ const sp=GR(gid); const r=g2find(RW(self,gid),rid); if(!r) return; const d={};
  (sp.edit.fields||[]).forEach(f=>{ const x=r.v[f.k]; d[f.k]=(x===undefined||x===null||x==='')?'':(f.t==='num'?String(x).replace('.',','):String(x)); });
  g2set(self,gid,{fm:{rid,draft:d,orig:Object.assign({},d),errs:{},warn:false,ro:!!r.ro,isNew:false,mode:'form'},fl:null,fmc:null}); }
// valor-padrão que acompanha o registro de origem pelo id: renomear a cultura, o grupo ou o local não deixa o padrão órfão
function cadcPadrao(gid,k,val){ const f=(GR(gid).edit.fields||[]).find(x=>x.k===k); if(f) f.def=val; }
'''

def _cj_cd03():
    """X-CAD-1: conjuntos do CD-03 (largura do implemento e R$/h da máquina e do implemento) e equipes do CD-04 (pessoas ativas e custo somado),
    para o rendimento escolher em vez de redigitar; o custo da equipe só aparece somado (G1)."""
    at={a['nome']:a for a in DC.ATIVOS}
    def larg(a):
        if not a: return ''
        if a.get('barra'): return a['barra']
        if a.get('larg'): return a['larg']
        if a.get('plat'): return a['plat']
        if a.get('linhas') and a.get('esp'): return round(a['linhas']*a['esp'],2)
        return ''
    cjs=[]
    for k,m,i,op,rid in DC.CONJUNTOS:
        M=at.get(m); I=at.get(i) if i else None
        cjs.append(dict(id=k,nome=m+(' + '+i if i else ''),ops=op,rid=rid,larg=larg(I) or larg(M),maq=(M or {}).get('custo_h',''),impl=(I or {}).get('custo_h','') if I else 0,maqn=m,impln=i or '',
                        maqid=(M or {}).get('id',''),implid=(I or {}).get('id','') if I else ''))
    from areas.cad_ativos_pessoas import pessoas
    ps=pessoas(); eqs=[]
    for eid,en,lid,cal in DC.EQUIPES:
        mem=[v for _,v in ps if v['equipe']==en and v['sit']!='Inativa']
        if not mem: continue
        tot=round(sum(float(v['custo'] or 0) for v in mem),2)
        eqs.append(dict(id=eid,nome='Equipe '+en,n=len(mem),tot=tot))
    return cjs,eqs
def cd02():
    fname='CD-02.dc.html'; E._reset_screen(fname)
    uso=_uso_cultivar(); cjs,eqs=_cj_cd03(); cj_de_rend={c['rid']:c['id'] for c in cjs}
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
    # Cultivar | Situação | Ciclo | Item de semente | Cultivos (tipo de ciclo e unidade de produtividade ficam no cabeçalho da cultura, I21)
    cv=grid([dict(k='nome',l='Cultivar',w=200),dict(k='est',l='Situação',w=170),dict(k='dias',l='Ciclo',t='num',a='r',un='dias'),dict(k='sem',l='Item de semente',w=220),dict(k='uso',l='Cultivos',t='num',a='r')],
        tree,gid='g_cv',tree=True,dele=False,total=False,frame=False,search=False,x0={r['id']:True for r in tree},
        tools=f'<span class="cmd-conta">{H("c2_conta")}</span>'+qf_chips('g_cv'),
        edit=dict(m='form',title='Cultivar',newTitle='Criar cultivar',leafOnly=True,alvo='cultivar',sub='Registro no RNC é referência, não prova de adaptação local; cultivar em uso não se exclui, inative.',
            fields=[txt('nome','Cultivar ou híbrido'),
                    sel('cult','Cultura',[n for n,*_ in DC.CULTURAS]+[OUTRA_C]),
                    txt('ncult','Nome da nova cultura',cond=cond('cult',OUTRA_C)),
                    sel('tipo','Tipo de ciclo',['Anual','Perene'],cond=cond('cult',OUTRA_C),**{'def':'Anual'}),
                    sel('unid','Unidade de produtividade',DC.UNID_PROD,cond=cond('cult',OUTRA_C),**{'def':DC.UNID_PROD[0]},
                        help='Meta e custo por unidade do Planejar safra usam esta unidade.'),
                    num('dias','Ciclo até a colheita','dias',min=30,max=250,cond=cond('tipo','Anual')),
                    sel('sem','Item de semente',SEMENTES_BASE+[CRIAR],cond=cond('tipo','Anual'),**{'def':CRIAR},
                        help='Grupo Sementes, em kg: Compras cota e o Estoque recebe por este item.'),
                    sel('reg','Registro',['RNC · referência','Cadastro próprio'],**{'def':'RNC · referência'}),
                    sel('sit','Situação',['Ativa','Inativa'],**{'def':'Ativa'})]))
    grid([dict(k='nome',l='Cultura')],cul_rows,gid='g_cult',search=False,total=False,
         edit=dict(m='form',title='Cultura',newTitle='Criar cultura',sub='Altere nome e unidade de produtividade; o tipo de ciclo fica fixo depois do cadastro.',
             fields=[txt('nome','Nome da cultura'),
                     sel('tipo','Tipo de ciclo',['Anual','Perene'],ro=True,help='Anual pede ciclo e semente na cultivar; perene carrega a data real do ciclo.'),
                     sel('unid','Unidade de produtividade',DC.UNID_PROD,help='Meta e custo por unidade do Planejar safra usam esta unidade.')]))
    # ---- operações (fonte) e árvore Operação → rendimento (conjunto × cultura) ----
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
            v=dict(op=op,conj=c['conj'],nome=c['conj'],cult='Todas',maq=c['maq'],impl=c['impl'],pess=c['pess'],pess_rs=c['pess_rs'],fonte=FONTE.get(c['id'],'Equipe da fazenda'),vig='2027-06-30',rend=c['rend'],cjid=cj_de_rend.get(c['id'],''))
            if c['id'] in MODO: v.update(modo='Largura × velocidade',larg=MODO[c['id']][0],vel=MODO[c['id']][1],efic=MODO[c['id']][2])
            else: v.update(modo='Informado',larg='',vel='',efic='')
            ch=D2.custo_h(c); v.update(custo_h=round(ch,2),custo_ha=round(ch/c['rend'],2))
            kids.append(R(c['id'],v))
        rtree.append(dict(id=oid,v=dict(nome=op),s={},p={},kids=kids))
    # Conjunto | Situação | Cultura | Modo | Rendimento | Custo R$/h | Fonte (largura, velocidade, eficiência e Custo R$/ha no painel: ≤ 7 colunas)
    rend=grid([dict(k='nome',l='Conjunto',w=280),dict(k='est',l='Situação',w=170),dict(k='cult',l='Cultura'),dict(k='modo',l='Modo',w=150),
               dict(k='rend',l='Rendimento',t='num',a='r',un='ha/h',d=2),dict(k='custo_h',l='R$/h',t='num',a='r',d=2),dict(k='fonte',l='Fonte',w=170)],
        rtree,gid='g_rend',tree=True,dele=False,total=False,frame=False,search=False,x0={r['id']:True for r in rtree},
        tools=f'<span class="cmd-conta">{H("c2_contaR")}</span>'+qf_chips('g_rend'),
        edit=dict(m='form',title='Rendimento',newTitle='Criar rendimento',leafOnly=True,alvo='rendimento',
            sub='Escolha o conjunto (CD-03) ou a equipe (CD-04): largura e custo por hora vêm de lá, só leitura. Rendimento e custo por hectare são recalculados. Planejar safra parte deste padrão.',
            fields=[sel('op','Operação',ops+[OUTRA_O]),
                    txt('nop','Nome da nova operação',cond=cond('op',OUTRA_O)),
                    sel('nproc','Processo',PROC_NOMES,cond=cond('op',OUTRA_O),**{'def':'Tratos culturais'},help='Etapa de custo da Estrutura gerencial que recebe o custo desta operação.'),
                    sel('cjid','Conjunto ou equipe',[c['id'] for c in cjs]+[e['id'] for e in eqs]+[CJ_OUTRO],req=False,help='Do CD-03 (máquina + implemento) ou do CD-04 (equipe); "Outro" para descrever um conjunto que ainda não está lá.'),
                    txt('conj','Descrição do conjunto ou da equipe',help='Preenchida pelo conjunto ou pela equipe escolhida; edite só em "Outro".'),
                    sel('cult','Cultura',['Todas']+[n for n,*_ in DC.CULTURAS],**{'def':'Todas'},help='O Planejar safra usa o rendimento da cultura do cultivo e, na falta dele, o de Todas.')]
                   + REND_CAMPOS
                   + [sel('fonte','Fonte do dado',['Medição local','Ensaio da fazenda','Fabricante','Referência','Premissa a validar'],**{'def':'Premissa a validar'}),
                      dat('vig','Vigente até')]))
    grid([dict(k='nome',l='Operação')],op_rows,gid='g_op',search=False,total=False,
         edit=dict(m='form',title='Operação',newTitle='Criar operação',sub='Defina a etapa de custo e as atividades que os Planos agronômicos oferecem para esta operação.',
             fields=[txt('nome','Nome da operação'),
                     sel('proc','Processo',PROC_NOMES,help='Etapa de custo: o custo da O.S. e do orçamento desta operação vai para este processo.'),
                     dict(k='atvs',l='Atividades usuais',t='area',req=False,help='Separe por ponto e vírgula; no plano, a operação vem primeiro e filtra estas atividades.')]))
    acoes_form('g_cv'); cadx_css(); md_css()
    det=det_cab()+f'<div class="cadx-dados">'+vazio('c2_v')+se('c2_cv_on',arv(cv),True)+se('c2_rend_on',arv(rend))+'</div>'
    corpo=md(mestre(H('c2_mrot'),'Buscar cultura, cultivar, operação ou conjunto'),det,'Culturas, cultivares e operações',
             topo=abas('c2t',['Culturas e cultivares','Operações e rendimentos'],'Cadastros de culturas e operações'))
    dados=json.dumps(dict(unid=DC.UNID_PROD,sem=SEMENTES_BASE,son=SEG_ON(),soff=SEG_OFF(),cjs=cjs,eqs=eqs,outro=CJ_OUTRO,
                      defc=next(r['id'] for r in cul_rows if r['v']['nome']=='Soja'),defo='OP1'),ensure_ascii=False)
    js(dict(cmp='Pulverização: padrão 21,6 ha/h × realizado 19,8 ha/h (OS-0421, 4 dias) · revisão sugerida, nada alterado.'),REND_JS
       +CADC_JS+f"\nconst C2={dados}; const OUTRA_C={json.dumps(OUTRA_C)}, OUTRA_O={json.dumps(OUTRA_O)}, CRIAR={json.dumps(CRIAR,ensure_ascii=False)};\n"+CD02JS)
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a lista rola
    shell37('CD-02','Culturas, cultivares e operações',corpo,fname=fname,status=None,primary_html=criar_cab('c2_criar','+ Criar cultivar'),search=False)
    estado_cab(fname,'Culturas, cultivares e operações','c2e')
CJ_OUTRO='Outro (descrever)'
CD02JS=r'''
// item de semente criado aqui chega ao CD-06 pelo armazenamento do navegador (chave própria dos cadastros; o CD-06 lê ao abrir)
function c2lsSemente(n){ cadLSPoe(o=>{ o.sementes=o.sementes||[]; if(o.sementes.indexOf(n)<0) o.sementes.push(n); }); }
// X-CAD-1: o R$/h dos ativos vem do CD-03 pela mesma leitura que o CD-03 usa ao abrir (cadCustoH): mudar o R$/h do Trator 02 muda o R$/ha do rendimento
function c2cj(id){ const c=C2.cjs.find(x=>x.id===id); if(!c) return null;
  return Object.assign({},c,{maq:cadCustoH(c.maqid,c.maq),impl:c.impln?cadCustoH(c.implid,c.impl):0}); }
function c2eq(id){ return C2.eqs.find(x=>x.id===id)||null; }
function c2rm(list,id){ const i=list.findIndex(x=>x.id===id); if(i>=0){ list.splice(i,1); return true; } return list.some(x=>x.kids&&c2rm(x.kids,id)); }
function c2opts(gid,k,opts){ const f=(GR(gid).edit.fields||[]).find(x=>x.k===k); if(f) f.opts=opts; }
function c2sem(cult,cv){ return 'Semente de '+String(cult).toLowerCase()+' '+String(cv).replace(/^Híbrido /,''); }
function c2cod(n){ return String(n).normalize('NFD').replace(/[̀-ͯ]/g,'').toUpperCase().replace(/[^A-Z0-9]+/g,'').slice(0,8); }
function cvFalta(V){ return V.tipo==='Anual'&&V.sit!=='Inativa'&&(!V.sem||V.sem===CRIAR); }
function cvSit(V){ if(V.sit==='Inativa') return {t:'Inativa',p:[chipc('Inativa','gray')]}; if(cvFalta(V)) return {t:'Sem semente',p:sitX('Sem semente','yellow'),res:true};
  return {t:'Em dia',p:sitOk('Em dia')}; }
function rdSit(V){ if(V.fonte==='Premissa a validar') return {t:'Premissa a validar',p:sitX('Premissa a validar','yellow'),res:true}; return {t:'Em dia',p:sitOk('Em dia')}; }
CAD_ACTS.g_cv=(self,r)=>{ const n=Number(r.v.uso)||0; return [cadExcluir(self,'g_cv',r,'cultivar',n?('usada em '+n+(n>1?' cultivos':' cultivo')+'; inative em vez de excluir'):'')]; };
const C2ABAS=['culturas','operacoes'];
function c2aba(self){ return self.state.c2aba||0; }
function c2leaves(self,gid){ return cadRegs(RW(self,gid)).filter(r=>!/^(CU|OP)/.test(r.id)||r.v.cult!==undefined||r.v.op!==undefined); }
// rendimento visto da cultivar: os que valem para a cultura dela (o da cultura e o de "Todas"), em consulta; a única porta de edição é Operações (I07)
function c2rendsDe(self,cult){ return cadRegs(RW(self,'g_rend')).filter(r=>r.v.op!==undefined&&(r.v.cult===cult||(r.v.cult||'Todas')==='Todas')); }
function c2abreRend(self,rid){ const r=g2find(RW(self,'g_rend'),rid); if(!r) return; const o=RW(self,'g_op').find(x=>x.v.nome===r.v.op);
  GRIDS.forEach(sp=>g2set(self,sp.id,{fm:null})); self.setState({c2aba:1,mx_sel:o?o.id:'',mx_nivel:'d'}); setTimeout(()=>g2open(self,GR('g_rend'),rid,null),0); }
function c2consCv(self,r){ const V=r.v; const S=cvSit(V); const C=RW(self,'g_cult').find(x=>x.v.nome===V.cult)||{v:{}}; const rs=c2rendsDe(self,V.cult);
  return {titulo:'Cultivar · '+V.nome,sub:V.cult+' · '+(V.tipo||'')+' · '+S.t,
    prox:V.sit==='Inativa'?{cor:'gray',t:'Inativa: fora do Planejar safra; o histórico continua.'}:(cvFalta(V)?{cor:'yellow',t:'Sem item de semente: Compras não cota e o Estoque não recebe a semente desta cultivar.',prim:{t:'Vincular semente da '+V.nome,go:()=>g2editar(self,GR('g_cv'),r.id,'sem')}}:{cor:'green',t:'Em dia: semente vinculada.'}),
    sec:[{t:'Editar cultivar',go:()=>g2editar(self,GR('g_cv'),r.id)}],
    blocos:[{t:'Ficha',lin:[{l:'Cultura',v:V.cult},{l:'Tipo de ciclo',v:C.v.tipo||V.tipo},{l:'Unidade de produtividade',v:C.v.unid||'—'},V.tipo==='Anual'?{l:'Ciclo até a colheita',v:isnum(V.dias)?V.dias+' dias':'—'}:null,{l:'Registro',v:V.reg},{l:'Cultivos',v:String(V.uso||0)}]},
      V.tipo==='Anual'?{t:'Semente',lin:[{l:'Item de semente',v:(!V.sem||V.sem===CRIAR)?'sem item vinculado':V.sem,cor:cvFalta(V)?'yellow':''}],lks:[{t:'Abrir sementes nos Produtos',h:'CD-06.dc.html#grp=Sementes'}]}:null,
      {t:'Rendimentos que valem para a '+String(V.cult).toLowerCase(),fil:rs.map(x=>({t:x.v.op+' · '+x.v.conj,sub:nf(x.v.rend,2)+' ha/h · vale para: '+((x.v.cult||'Todas')==='Todas'?'todas as culturas':x.v.cult)+' · Abrir em Operações ›',al:'Abrir em Operações: '+x.v.op+' · '+x.v.conj,go:()=>c2abreRend(self,x.id)})),
        nota:rs.length?'Consulta: o rendimento se edita em Operações (uma porta só).':'Nenhum rendimento para esta cultura.'}]}; }
function c2consRend(self,r){ const V=rendCalc(Object.assign({},r.v)); const S=rdSit(V); const cj=V.cjid?c2cj(V.cjid):null, eq=V.cjid?c2eq(V.cjid):null;
  return {titulo:'Rendimento · '+V.conj,sub:V.op+' · cultura '+(V.cult||'Todas')+' · '+(V.fonte||'—'),
    prox:S.res?{cor:'yellow',t:'Premissa a validar: o planejamento usa este rendimento sem medição.',prim:{t:'Validar rendimento',go:()=>g2editar(self,GR('g_rend'),r.id,'fonte')}}:{cor:'green',t:'Em dia: fonte '+String(V.fonte||'').toLowerCase()+'.'},
    sec:[{t:'Editar rendimento',go:()=>g2editar(self,GR('g_rend'),r.id)}],
    blocos:[{t:'Rendimento',lin:[{l:'Modo',v:V.modo},V.modo==='Informado'?null:{l:'Fórmula',v:'L × V ÷ 10 × eficiência = '+nfa(V.larg)+' m × '+nfa(V.vel)+' km/h ÷ 10 × '+nfa(V.efic)+' %'},{l:'Rendimento efetivo',v:nf(V.rend,2)+' ha/h'}]},
      {t:'Custo',lin:[{l:'Custo R$/h',v:'R$ '+nf(V.custo_h,2)+'/h'},{l:'Custo R$/ha',v:'R$ '+nf(V.custo_ha,2)+'/ha'},eq?{l:'Equipe',v:eq.n+' pessoas · custo somado'}:{l:'Pessoas',v:String(V.pess||0)}]},
      {t:'Conjunto',lin:[{l:'Conjunto ou equipe',v:V.conj},{l:'Origem',v:cj?'Conjunto do CD-03: largura e R$/h só leitura aqui':(eq?'Equipe do CD-04: custo somado, nunca por pessoa':'Descrito aqui (sem vínculo)')}],
        lks:[cj?{t:'Abrir conjunto em Máquinas',h:'CD-03.dc.html#cj='+encodeURIComponent(cj.id)}:null,eq?{t:'Abrir equipe em Pessoas',h:'CD-04.dc.html#eq='+encodeURIComponent(eq.id)}:null]},
      {t:'Vigência',lin:[{l:'Vigente até',v:br(V.vig)},{l:'Fonte do dado',v:V.fonte}]}]}; }
function c2consCult(self,c){ const C=c.v; const kids=cadRegs(RW(self,'g_cv')).filter(r=>r.v.cult===C.nome);
  return {titulo:'Cultura · '+C.nome,sub:C.tipo+' · produtividade em '+C.unid+' · '+kids.length+(kids.length===1?' cultivar':' cultivares'),prox:{cor:'green',t:'A unidade de produtividade vale para a meta e o custo por unidade do Planejar safra.'},
    sec:[{t:'Editar cultura',go:()=>g2editar(self,GR('g_cult'),c.id)}],
    blocos:[{t:'Cultivares',fil:kids.map(r=>({t:r.v.nome,sub:cvSit(r.v).t,go:()=>{ g2set(self,'g_cult',{fm:null}); g2open(self,GR('g_cv'),r.id,null,{pai:{gid:'g_cult',rid:c.id,t:C.nome}}); }})),nota:kids.length?'':'Nenhuma cultivar.'}]}; }
function c2consOp(self,o){ const O=o.v; const kids=cadRegs(RW(self,'g_rend')).filter(r=>r.v.op===O.nome);
  return {titulo:'Operação · '+O.nome,sub:'Processo '+(O.proc||'—')+' · aprovação agronômica pela regra (APROV-04), sem dispensa no cadastro',prox:{cor:'green',t:ml(O.atvs).length+' atividades usuais oferecidas nos Planos agronômicos.'},
    sec:[{t:'Editar operação',go:()=>g2editar(self,GR('g_op'),o.id)}],
    blocos:[{t:'Rendimentos',fil:kids.map(r=>({t:r.v.conj,sub:nf(r.v.rend,2)+' ha/h · '+(r.v.cult||'Todas'),go:()=>{ g2set(self,'g_op',{fm:null}); g2open(self,GR('g_rend'),r.id,null,{pai:{gid:'g_op',rid:o.id,t:O.nome}}); }}))},
      {t:'Atividades usuais',lin:[{l:'Atividades',v:ml(O.atvs).join(', ')||'—'}]}]}; }
function c2pends(self,aba,gid){ const out=[];
  if(aba===0){ const C=gid?RW(self,'g_cult').find(x=>x.id===gid):null; cadRegs(RW(self,'g_cv')).filter(r=>r.v.cult!==undefined&&cvFalta(r.v)&&(!C||r.v.cult===C.v.nome)).forEach(r=>out.push({cor:'yellow',t:r.v.cult+' '+r.v.nome+' sem item de semente: Compras não cota a semente.',
      prim:{t:'Vincular semente da '+r.v.nome,go:()=>{ g2open(self,GR('g_cv'),r.id,null); setTimeout(()=>g2editar(self,GR('g_cv'),r.id,'sem'),0); }},s:r.v.nome+' sem semente'})); }
  else { const O=gid?RW(self,'g_op').find(x=>x.id===gid):null; cadRegs(RW(self,'g_rend')).filter(r=>r.v.op!==undefined&&rdSit(r.v).res&&(!O||r.v.op===O.v.nome)).forEach(r=>out.push({cor:'yellow',t:r.v.op+' · '+r.v.conj+': rendimento como premissa a validar.',
      prim:{t:'Validar rendimento',go:()=>{ g2open(self,GR('g_rend'),r.id,null); setTimeout(()=>g2editar(self,GR('g_rend'),r.id,'fonte'),0); }},s:r.v.conj+' premissa'})); }
  return out; }
function c2prox(ps,ok){ if(!ps.length) return {cor:'green',t:ok}; const p=ps[0], r=ps.slice(1); return {cor:p.cor,t:p.t,prim:p.prim,mais:r.length?('e mais '+r.length+': '+r.map(x=>x.s).join('; ')+'.'):''}; }
// abre a criação do rendimento: operação herdada; vindo do CD-03 (#cj=&novo=1), o conjunto e a 1ª operação dele (X-CAD-1)
function c2novoRend(self,cjid){ const o=RW(self,'g_op').find(x=>x.id===cmdSel(self)); const cj=cjid?c2cj(cjid):null; const op=cj?(RW(self,'g_op').find(x=>x.v.nome===ml(cj.ops)[0])||null):o;
  const d={op:op?op.v.nome:''}; if(cj) Object.assign(d,c2draftCj(cj)); g2set(self,'g_rend',{fm:null}); g2new(self,GR('g_rend'),{draft:d});
  if(cj&&op) self.setState({c2aba:1,mx_sel:op.id,mx_nivel:'d'}); return op?op.id:''; }
function c2draftCj(cj){ return {cjid:cj.id,conj:cj.nome,larg:isnum(cj.larg)?String(cj.larg).replace('.',','):'',maq:isnum(cj.maq)?String(cj.maq).replace('.',','):'',impl:isnum(cj.impl)?String(cj.impl).replace('.',','):'0',modo:isnum(cj.larg)?'Largura × velocidade':'Informado'}; }
// equipe (operação manual): sem largura nem máquina; rendimento informado (ha/h medidos) e o custo da equipe somado
function c2draftEq(eq){ return {cjid:eq.id,conj:eq.nome,pess:String(eq.n),pess_rs:String(Math.round(eq.tot/eq.n*100)/100).replace('.',','),modo:'Informado',larg:'',maq:'',impl:'0'}; }
function c2cfg(self){ cmdIni(self,{gp:(s)=>c2aba(s)===1?'op':'cul',gps:['cul','op'],abaDoGp:{cul:0,op:1},ip:{g_cv:'cv',g_rend:'rend'},abas:C2ABAS,abaKey:'c2aba',
  gpDe:(gid)=>gid==='g_rend'?'op':'cul',
  grupoDe:(s,gid,r)=>{ if(gid==='g_rend'){ const o=RW(s,'g_op').find(x=>x.v.nome===r.v.op); return o?o.id:''; } const c=RW(s,'g_cult').find(x=>x.v.nome===r.v.cult); return c?c.id:''; },
  existeGrupo:(s,id)=>RW(s,'g_cult').some(x=>x.id===id)||RW(s,'g_op').some(x=>x.id===id),
  abaDe:(gid)=>({c2aba:gid==='g_rend'?1:0}),
  reg:(s,id)=>cadRegs(RW(s,'g_cv')).some(r=>r.id===id)?{gid:'g_cv',rid:id}:(cadRegs(RW(s,'g_rend')).some(r=>r.id===id)?{gid:'g_rend',rid:id}:null),
  indisp:(id,gid)=>gid==='g_cv'?cmdIndisp('Cultivar',id,true):(gid==='g_rend'?cmdIndisp('Rendimento',id):cmdIndisp('Registro',id)),
  indispGrupo:(id)=>'Cultura ou operação “'+id+'” não está neste cadastro. Nada foi aberto.',
  inativo:(gid,r)=>(gid==='g_cv'&&r.v.sit==='Inativa')?{c2qf0:'inat'}:null,
  // cj=&novo=1 (X-CAD-1): a criação do rendimento abre com o conjunto e a operação dele; o endereço passa a dizer a operação (cj= só existe no CD-03)
  novo:(s,o)=>{ if(o&&o.cj){ s.state.c2aba=1; const op=c2novoRend(s,o.cj); return op?{aba:'operacoes',op:op}:{aba:'operacoes'}; } if(s.__v&&s.__v.c2_criar) s.__v.c2_criar(); return null; },
  anuncio:(s,id)=>{ const c=RW(s,'g_cult').find(x=>x.id===id), o=RW(s,'g_op').find(x=>x.id===id);
    if(c){ const n=cadRegs(RW(s,'g_cv')).filter(r=>r.v.cult===c.v.nome).length; return c.v.nome+': '+n+(n===1?' cultivar':' cultivares'); }
    if(o){ const n=cadRegs(RW(s,'g_rend')).filter(r=>r.v.op===o.v.nome).length; return o.v.nome+': '+n+(n===1?' rendimento':' rendimentos'); }
    return c2aba(s)===1?'Todas as operações':'Todas as culturas'; },
  cons:{g_cv:c2consCv,g_rend:c2consRend,g_cult:c2consCult,g_op:c2consOp}}); }
function PREVALS(self,v){ cadActsIni(self); if(self.state.mx_q===undefined){ const k=cadKeepLe('q'); if(k) self.state.mx_q=k; }
  const cul=RW(self,'g_cult'); const dc=cul.find(c=>c.id===C2.defc); cadcPadrao('g_cv','cult','');
  RW(self,'g_cv').forEach(p=>{ const c=cul.find(x=>x.id===p.id); if(!c) return; const C=c.v; const ks=p.kids||[]; p.v.nome=C.nome;
    p.p.nome=[{k:'b',t:C.nome},{k:'mut',t:ks.length+(ks.length===1?' cultivar':' cultivares')}]; p.s.nome=C.nome;
    ['est','dias','sem','uso'].forEach(k=>{ p.p[k]=[{k:'mut',t:''}]; p.s[k]=''; });
    ks.forEach(r=>{ const V=r.v; V.cult=C.nome; V.tipo=C.tipo; const an=C.tipo==='Anual';
      r.p.nome=[{k:'b',t:V.nome||''}]; r.s.nome=V.nome||'';
      const cic=an&&isnum(V.dias)&&String(V.dias)!==''; r.p.dias=[cic?{k:'txt',t:nf(V.dias)}:{k:'mut',t:'—'}]; r.s.dias=cic?nf(V.dias):'';
      const falta=an&&(!V.sem||V.sem===CRIAR); r.p.sem=(!an||falta)?[{k:'mut',t:'—'}]:[{k:'txt',t:V.sem}]; r.s.sem=(!an||falta)?'':V.sem;
      const n=Number(V.uso)||0; r.p.uso=[{k:(n?'txt':'mut'),t:String(n)}]; r.s.uso=String(n); r.nd=n?'em uso':'';
      const S=cvSit(V); r.p.est=S.p; r.s.est=S.t; }); });
  c2opts('g_cv','cult',cul.map(c=>c.v.nome).concat([OUTRA_C]));
  const sems=C2.sem.slice(); leaves(RW(self,'g_cv')).forEach(r=>{ if(r.v.sem&&r.v.sem!==CRIAR&&sems.indexOf(r.v.sem)<0) sems.push(r.v.sem); });
  c2opts('g_cv','sem',sems.sort((a,b)=>a.localeCompare(b,'pt-BR')).concat([CRIAR]));
  const ops=RW(self,'g_op'); cadcPadrao('g_rend','op','');
  RW(self,'g_rend').forEach(p=>{ const o=ops.find(x=>x.id===p.id); if(!o) return; const O=o.v; const ks=p.kids||[]; p.v.nome=O.nome;
    p.p.nome=[{k:'b',t:O.nome},{k:'mut',t:ks.length+(ks.length===1?' rendimento':' rendimentos')}]; p.s.nome=O.nome;
    ['est','cult','modo','rend','custo_h','fonte'].forEach(k=>{ p.p[k]=[{k:'mut',t:''}]; p.s[k]=''; });
    ks.forEach(r=>{ const V=r.v; V.op=O.nome; V.nome=V.conj;
      // X-CAD-1: rendimento ligado a conjunto do CD-03 lê largura e R$/h de lá (o R$/ha acompanha)
      const cj=V.cjid?c2cj(V.cjid):null; if(cj){ if(isnum(cj.maq)) V.maq=cj.maq; V.impl=isnum(cj.impl)?cj.impl:0; if(isnum(cj.larg)&&V.modo!=='Informado') V.larg=cj.larg; rendCalc(V); }
      r.p.nome=[{k:'b',t:V.conj||''}]; r.s.nome=V.conj||''; r.p.modo=[{k:'txt',t:V.modo||'—'}]; r.s.modo=V.modo||'';
      const cu=V.cult||'Todas'; r.p.cult=[cu==='Todas'?{k:'mut',t:'Todas'}:{k:'txt',t:cu}]; r.s.cult=cu;
      r.p.custo_h=[{k:'txt',t:nf(V.custo_h,2)}]; r.s.custo_h=nf(V.custo_h,2); r.p.fonte=[{k:'txt',t:V.fonte||'—'}]; r.s.fonte=V.fonte||'';
      const S=rdSit(V); r.p.est=S.p; r.s.est=S.t; }); });
  c2opts('g_rend','op',ops.map(o=>o.v.nome).concat([OUTRA_O]));
  c2opts('g_rend','cult',['Todas'].concat(cul.map(c=>c.v.nome)));
  const aba=c2aba(self); const sel=cmdSel(self); const q=self.state.mx_q||'';
  const cs=aba===0&&sel?cul.find(x=>x.id===sel):null, os=aba===1&&sel?ops.find(x=>x.id===sel):null;
  const tv=RW(self,'g_cv'), tr=RW(self,'g_rend');
  cmdPasse(tv,'cadm_g_cv',r=>!cs||r.v.cult===cs.v.nome); cmdPasse(tv,'cadb_g_cv',r=>cmdCasa([r.v.nome,r.v.cult,r.v.sem].join(' '),q),!!q);
  cmdQf(self,v,'g_cv','c2qf0',[{k:'res',t:'A resolver',f:r=>!!cvSit(r.v).res},{k:'inat',t:'Inativas',f:r=>r.v.sit==='Inativa',oculta:true}],tv);
  cmdPasse(tr,'cadm_g_rend',r=>!os||r.v.op===os.v.nome); cmdPasse(tr,'cadb_g_rend',r=>cmdCasa([r.v.conj,r.v.op,r.v.cult,r.v.fonte].join(' '),q),!!q);
  cmdQf(self,v,'g_rend','c2qf1',[{k:'res',t:'A resolver',f:r=>!!rdSit(r.v).res}],tr);
  if(cs){ const g=tv.find(x=>x.id===cs.id); G2DISP.g_cv=g?g.kids:[]; } else delete G2DISP.g_cv;
  if(os){ const g=tr.find(x=>x.id===os.id); G2DISP.g_rend=g?g.kids:[]; } else delete G2DISP.g_rend;
  GR('g_cv').cols[0]=Object.assign({},GR('g_cv').cols[0],{l:cs?'Cultivar':'Cultura › cultivar'}); GR('g_rend').cols[0]=Object.assign({},GR('g_rend').cols[0],{l:os?'Conjunto':'Operação › conjunto'});
  c2cfg(self); }
function EXTRAVALS(self,v){ simv(self,v); const aba=c2aba(self); const sel=cmdSel(self); const q=self.state.mx_q||''; const larga=cadLarga(); const cul=RW(self,'g_cult'), ops=RW(self,'g_op');
  const cvs=cadRegs(RW(self,'g_cv')).filter(r=>r.v.cult!==undefined), rds=cadRegs(RW(self,'g_rend')).filter(r=>r.v.op!==undefined);
  // abas da tela (duas árvores independentes, C17): trocar de aba volta o mestre a "Todas"
  cadAbas(self,v,'c2t','c2aba',[{slug:'culturas',n:cvs.length,cor:''},{slug:'operacoes',n:rds.length,cor:''}]);
  [0,1].forEach(i=>{ v['c2t'+i+'_go']=()=>{ if(c2aba(self)===i) return; GRIDS.forEach(sp=>g2set(self,sp.id,{fm:null})); cadHashPoe(self,i?{aba:'operacoes'}:{}); self.setState({c2aba:i,mx_sel:'',mx_nivel:larga?'d':'m'}); }; });
  // ---- mestre ----
  v.c2_mrot=aba===1?'Operações':'Culturas';
  let its, todos;
  if(aba===0){ its=cul.filter(c=>!q||c.id===sel||cmdCasa(c.v.nome,q)||cvs.some(r=>r.v.cult===c.v.nome&&cmdCasa([r.v.nome,r.v.sem].join(' '),q))).map(c=>{ const n=cvs.filter(r=>r.v.cult===c.v.nome).length; const p=c2pends(self,0,c.id).length;
      return {id:c.id,t:c.v.nome,n:String(n),sub:c.v.tipo+' · '+c.v.unid,res:p?p+' a resolver':'Em dia',cor:p?'yellow':'green'}; }); todos={t:'Todas as culturas',sub:cvs.length+' cultivares'}; }
  else { its=ops.filter(o=>!q||o.id===sel||cmdCasa(o.v.nome,q)||rds.some(r=>r.v.op===o.v.nome&&cmdCasa([r.v.conj,r.v.cult].join(' '),q))).map(o=>{ const n=rds.filter(r=>r.v.op===o.v.nome).length; const p=c2pends(self,1,o.id).length;
      return {id:o.id,t:o.v.nome,n:String(n),sub:'processo '+(o.v.proc||'—'),res:p?p+' a resolver':'Em dia',cor:p?'yellow':'green'}; }); todos={t:'Todas as operações',sub:rds.length+' rendimentos'}; }
  cadMestreVals(self,v,{todos:todos,itens:its,sel:sel,inatN:0,escolhe:id=>cmdEscolhe(self,id)});
  const rs=[]; if(q&&!larga){ if(aba===0) cvs.filter(r=>cmdCasa([r.v.nome,r.v.cult].join(' '),q)).forEach(r=>{ const c=cul.find(x=>x.v.nome===r.v.cult); rs.push({t:r.v.nome+' · '+r.v.cult,sub:'Cultivar',go:()=>cmdAbre(self,'g_cv',r.id,c?c.id:'')}); });
    else rds.filter(r=>cmdCasa([r.v.conj,r.v.op].join(' '),q)).forEach(r=>{ const o=ops.find(x=>x.v.nome===r.v.op); rs.push({t:r.v.conj+' · '+r.v.op,sub:'Rendimento · '+nf(r.v.rend,2)+' ha/h',go:()=>cmdAbre(self,'g_rend',r.id,o?o.id:'')}); }); }
  cadResVals(v,rs);
  // ---- detalhe ----
  const av=cmdAviso(self,aba===1?'Ver todas as operações':'Ver todas as culturas'); v.c2_cv_on=aba===0; v.c2_rend_on=aba===1;
  const ps=c2pends(self,aba,sel); const chip=ps.length?{t:ps.length+' a resolver',c:'yellow'}:{t:'Em dia',c:'green'};
  if(aba===0){ const c=sel?cul.find(x=>x.id===sel):null; const n=cvs.filter(r=>!c||r.v.cult===c.v.nome).length;
    cadDetVals(self,v,Object.assign(c?{t:c.v.nome,sub:c.v.tipo+' · produtividade em '+c.v.unid+' · '+n+(n===1?' cultivar':' cultivares'),ficha:{t:'Ver ficha da cultura',go:()=>g2open(self,GR('g_cult'),c.id,null)}}
      :{t:'Todas as culturas',sub:cul.length+' culturas · '+n+' cultivares · Cultura e Processo daqui são a fonte das dimensões da Estrutura gerencial'},{chip:chip,prox:c2prox(ps,'Em dia: cultivares anuais com semente vinculada.'),volta:'Culturas',voltar:()=>cmdVolta(self)},av)); }
  else { const o=sel?ops.find(x=>x.id===sel):null; const n=rds.filter(r=>!o||r.v.op===o.v.nome).length;
    cadDetVals(self,v,Object.assign(o?{t:o.v.nome,sub:'Processo '+(o.v.proc||'—')+' · aprovação agronômica pela regra (APROV-04), sem dispensa no cadastro · '+n+(n===1?' rendimento':' rendimentos'),ficha:{t:'Ver ficha da operação',go:()=>g2open(self,GR('g_op'),o.id,null)}}
      :{t:'Todas as operações',sub:ops.length+' operações · '+n+' rendimentos (conjunto × cultura)'},{chip:chip,prox:c2prox(ps,'Em dia: rendimentos medidos ou de referência.'),lks:[{t:'Comparar com o realizado',go:v.sim_cmp}],volta:'Operações',voltar:()=>cmdVolta(self)},av)); }
  v.cab_criar_on=true; v.cab_criarT=aba===1?'+ Criar rendimento':'+ Criar cultivar';
  v.c2_criar=()=>{ if(aba===1){ c2novoRend(self,''); return; } const c=sel?cul.find(x=>x.id===sel):null; g2set(self,'g_cv',{fm:null}); g2new(self,GR('g_cv'),{draft:c?{cult:c.v.nome,tipo:c.v.tipo}:{cult:''}});
    setTimeout(()=>{ try{ const x=document.getElementById('fx_g_cv_nome'); if(x) x.focus(); }catch(z){} },90); };
  const semF=cvs.filter(r=>cvFalta(r.v)).length, prem=rds.filter(r=>r.v.fonte==='Premissa a validar').length;
  cadEstado(v,'c2e',[semF?semF+(semF>1?' cultivares':' cultivar')+' sem semente':'',prem?prem+(prem>1?' premissas':' premissa')+' a validar':''].filter(Boolean).join(' · ')||'Sem pendências',(semF||prem)?'yellow':'green');
  cadQfPos(self,v,'g_cv','c2qf0'); cadQfPos(self,v,'g_rend','c2qf1');
  const c0=cmdConta(self,'g_cv',RW(self,'g_cv')), c1=cmdConta(self,'g_rend',RW(self,'g_rend')); v.c2_conta=c0.n+' de '+c0.tot; v.c2_contaR=c1.n+' de '+c1.tot;
  const ct=aba===1?c1:c0; const vz=!ct.n?(q?{t:'Nada encontrado para “'+q+'”. Para cadastrar, use '+v.cab_criarT+', no topo.'}:{t:'Nenhum registro com este filtro.',go:{t:'Mostrar todos',fn:()=>self.setState(aba===1?{c2qf1:''}:{c2qf0:''})}}):null;
  cadVazioSe(self,v,'c2_v',vz,['g_cv','g_rend']);
  // linhas de grupo da árvore (em "Todas"): escolhem a cultura ou a operação
  ['g_cv','g_rend'].forEach(gid=>(v[gid+'_rows']||[]).forEach(x=>{ if(/^(CU|OP)/.test(String(x.id))&&(cul.some(c=>c.id===x.id)||ops.some(o=>o.id===x.id))){ const id=x.id; x.cls='g2r g2ed'; x.tab='-1'; x.key=()=>{};
    x.open=(e)=>{ if(e&&e.target&&e.target.closest&&e.target.closest('button')) return; cmdEscolhe(self,id); };
    const cc=x.cells.find(c=>c.isData); if(cc&&cc.parts[0]) cc.parts[0]=g2part({k:'act',alvo:true,t:cc.parts[0].t,al:'Abrir '+cc.parts[0].t,go:()=>cmdEscolhe(self,id)},v); } }));
  // ---- formulários ----
  const F=v.g_cv_F; if(F&&F.open&&F.fields){ const f=F.fields.find(x=>x.fid==='fx_g_cv_cult');
    if(f&&!f.dis) f.set=(e)=>{ const cur=g2st(self,'g_cv').fm; if(!cur) return; const val=e.target.value; const c=RW(self,'g_cult').find(x=>x.v.nome===val);
      const d=Object.assign({},cur.draft,{cult:val}); if(c) d.tipo=c.v.tipo; const er=Object.assign({},cur.errs||{}); delete er.cult; delete er.sem;
      g2set(self,'g_cv',{fm:Object.assign({},cur,{draft:d,errs:er,warn:false})}); }; }
  // X-CAD-1: "Conjunto ou equipe" vem do CD-03 ou do CD-04; com conjunto, largura e R$/h ficam só leitura (do CD-03); com equipe, pessoas e o custo somado (CD-04)
  const FR=v.g_rend_F; const fr=g2st(self,'g_rend').fm;
  if(FR&&FR.open&&FR.fields&&fr){ const d=fr.draft; const cj=d.cjid?c2cj(d.cjid):null, eq=d.cjid?c2eq(d.cjid):null; const ro=(f,h)=>{ f.dis=true; f.ist=f.ist.replace('background:#FFFFFF','background:#F4F6F3'); if(h){ f.help=h; f.hasHelp=true; } };
    const fcj=FR.fields.find(x=>x.fid==='fx_g_rend_cjid'); if(fcj){ fcj.opts=[{v:'',t:'Escolha…'}].concat(C2.cjs.map(c=>({v:c.id,t:c.nome+' (conjunto)'}))).concat(C2.eqs.map(e=>({v:e.id,t:e.nome+' ('+e.n+(e.n===1?' pessoa)':' pessoas)')}))).concat([{v:C2.outro,t:C2.outro}]);
      if(!fcj.dis) fcj.set=(e)=>{ const val=e.target.value; const c=c2cj(val), q2=c2eq(val); const patch={cjid:val}; if(c) Object.assign(patch,c2draftCj(c)); else if(q2) Object.assign(patch,c2draftEq(q2)); else if(val===C2.outro) patch.conj='';
        const cur=g2st(self,'g_rend').fm; if(!cur) return; const er=Object.assign({},cur.errs||{}); delete er.cjid; delete er.conj; g2set(self,'g_rend',{fm:Object.assign({},cur,{draft:Object.assign({},cur.draft,patch),errs:er,warn:false})}); }; }
    FR.fields.forEach(f=>{ const k=f.fid.replace('fx_g_rend_','');
      if(k==='conj'&&(cj||eq)) ro(f,'Do '+(cj?'CD-03 (Máquinas, instalações e setores)':'CD-04 (Pessoas e equipes)')+'.');
      if(cj&&k==='larg'&&isnum(cj.larg)) ro(f,'Do implemento no CD-03: '+nfa(cj.larg)+' m.');
      if(cj&&k==='maq') ro(f,'Do CD-03 ('+cj.maqn+'): R$ '+nf(cj.maq,2)+'/h. Mude lá; o R$/ha acompanha.');
      if(cj&&k==='impl') ro(f,cj.impln?('Do CD-03 ('+cj.impln+'): R$ '+nf(cj.impl,2)+'/h.'):'Conjunto sem implemento.');
      if(eq&&k==='pess') ro(f,'Pessoas ativas da equipe no CD-04.');
      if(eq&&k==='pess_rs'){ ro(f,'Custo da equipe somado no CD-04 (nunca por pessoa, G1): R$ '+nf(eq.tot,2)+'/h.'); f.v='—'; } });
    FR.fields=FR.fields.filter(f=>!(eq&&f.fid==='fx_g_rend_pess_rs')); }
  valida(self,v,'g_cv',(d,fm)=>{ const e={}; const cul2=RW(self,'g_cult'); const nova=d.cult===OUTRA_C; const cn=nova?String(d.ncult||'').trim():d.cult;
    if(!nova&&d.cult&&!cul2.some(c=>c.v.nome===d.cult)) e.cult='Escolha a cultura.';
    if(nova&&cn&&cul2.some(c=>c.v.nome.toLowerCase()===cn.toLowerCase())) e.ncult=cn+' já existe; escolha na lista Cultura.';
    const dup=leaves(RW(self,'g_cv')).find(r=>r.id!==fm.rid&&r.v.cult&&r.v.cult.toLowerCase()===String(cn||'').toLowerCase()&&String(r.v.nome).trim().toLowerCase()===String(d.nome||'').trim().toLowerCase());
    if(dup) e.nome=d.nome+' já está cadastrada em '+cn+'.';
    if(d.tipo==='Anual'&&d.sem&&d.sem!==CRIAR){ const pre=('Semente de '+cn).toLowerCase(); const dono=leaves(RW(self,'g_cv')).find(r=>r.id!==fm.rid&&r.v.sem===d.sem);
      if(d.sem.toLowerCase().indexOf(pre)!==0) e.sem='Escolha uma semente de '+String(cn).toLowerCase()+' ou "'+CRIAR+'".';
      else if(dono) e.sem=d.sem+' já é a semente da cultivar '+dono.v.nome+'.'; }
    return e; });
  valida(self,v,'g_cult',(d,fm)=>{ const e={}; const o=fm.rid?RW(self,'g_cult').find(c=>c.id===fm.rid):null; self.__c2old=o?{id:o.id,nome:o.v.nome}:null; const n=String(d.nome||'').trim().toLowerCase(); if(RW(self,'g_cult').some(c=>c.id!==fm.rid&&c.v.nome.toLowerCase()===n)) e.nome='Já existe a cultura '+d.nome+'.'; return e; });
  valida(self,v,'g_rend',(d,fm)=>{ const e={}; const nova=d.op===OUTRA_O; const on=nova?String(d.nop||'').trim():d.op;
    if(nova&&on&&RW(self,'g_op').some(o=>o.v.nome.toLowerCase()===on.toLowerCase())) e.nop=on+' já existe; escolha na lista Operação.';
    if(!nova&&d.op&&!RW(self,'g_op').some(o=>o.v.nome===d.op)) e.op='Escolha a operação.';
    if(d.cult&&d.cult!=='Todas'&&!RW(self,'g_cult').some(c=>c.v.nome===d.cult)) e.cult='Escolha a cultura.';
    const cu=d.cult||'Todas'; const mesmo=(r)=>(d.cjid&&d.cjid!==C2.outro&&r.v.cjid===d.cjid)||String(r.v.conj).trim().toLowerCase()===String(d.conj||'').trim().toLowerCase();
    const dup=leaves(RW(self,'g_rend')).find(r=>r.id!==fm.rid&&r.v.op===on&&(r.v.cult||'Todas')===cu&&mesmo(r));
    if(dup){ const m='Este '+(c2eq(d.cjid)?'equipe':'conjunto')+' já tem rendimento em '+on+' para '+(cu==='Todas'?'todas as culturas':cu)+': edite o rendimento dele ou escolha outra cultura.';
      if(d.cjid&&d.cjid!==C2.outro) e.cjid=m.replace('Este equipe','Esta equipe'); else e.conj=m; } return e; });
  valida(self,v,'g_op',(d,fm)=>{ const e={}; const n=String(d.nome||'').trim().toLowerCase(); if(RW(self,'g_op').some(o=>o.id!==fm.rid&&o.v.nome.toLowerCase()===n)) e.nome='Já existe a operação '+d.nome+'.'; return e; });
  self.g2live=(gid,k,d)=>(gid==='g_rend'?rendLive(k,d):null);
  ['g_cv','g_cult','g_op','g_rend'].forEach(g=>cadcEscolha(v,g));   // em "Todas as operações" a operação do rendimento novo vem vazia (X01): "Escolha…", não a 1ª da lista
  const soPai=(gid,rows,r,pid)=>{ const par=rows.find(p=>p.id===pid); const cur=rows.find(p=>(p.kids||[]).some(k=>k.id===r.id));
    if(cur!==par){ c2rm(rows,r.id); par.kids=par.kids||[]; par.kids.push(r); }
    const x=Object.assign({},g2st(self,gid).x||GR(gid).x0||{}); x[pid]=true; g2set(self,gid,{rows:rows,x:x,fl:r.id}); };
  self.g2after=(gid,rows,r,isNew)=>{ if(!r) return;
    if(gid==='g_cv'){ const cul2=g2clone(RW(self,'g_cult')); const msg=[]; let c;
      if(r.v.cult===OUTRA_C){ const nm=String(r.v.ncult).trim(); c={id:'CU'+(cul2.length+1)+'_'+String(Date.now()).slice(-4),v:{nome:nm,tipo:r.v.tipo||'Anual',unid:r.v.unid||C2.unid[0],cod:c2cod(nm)},s:{},p:{}};
        cul2.push(c); g2set(self,'g_cult',{rows:cul2}); rows.push({id:c.id,v:{nome:nm},s:{},p:{},kids:[]}); msg.push('cultura '+nm+' criada ('+c.v.tipo+' · '+c.v.unid+')'); }
      else c=cul2.find(x=>x.v.nome===r.v.cult);
      if(!c) return;
      r.v.cult=c.v.nome; r.v.ncult=''; r.v.tipo=c.v.tipo;
      if(c.v.tipo==='Anual'){ if(!r.v.sem||r.v.sem===CRIAR){ r.v.sem=c2sem(c.v.nome,r.v.nome); c2lsSemente(r.v.sem); msg.push('item '+r.v.sem+' criado em Produtos, unidades e locais (Sementes · kg)'); } else msg.push('semente '+r.v.sem); }
      else r.v.sem='';
      soPai('g_cv',rows,r,c.id); self.setState({g2toast:(isNew?'Criada: ':'Salvo: ')+r.v.nome+' em '+c.v.nome+' · '+msg.join(' · ')+'.'}); return; }
    if(gid==='g_cult'){ const o=self.__c2old; let n=0;
      if(o&&o.id===r.id&&o.nome!==r.v.nome){ const rr=g2clone(RW(self,'g_rend')); leaves(rr).forEach(x=>{ if(x.v.cult===o.nome){ x.v.cult=r.v.nome; n++; } }); if(n) g2set(self,'g_rend',{rows:rr}); }
      self.setState({g2toast:'Salvo: cultura '+r.v.nome+' · produtividade em '+r.v.unid+(n?' · '+n+(n>1?' rendimentos passam':' rendimento passa')+' a '+r.v.nome:'')+'. Planejar safra usa esta unidade na meta.'}); return; }
    if(gid==='g_op'){ const n=ml(r.v.atvs).length; self.setState({g2toast:'Salvo: '+r.v.nome+' · processo '+r.v.proc+' · '+n+(n===1?' atividade usual':' atividades usuais')+' nos Planos agronômicos.'}); return; }
    if(gid==='g_rend'){ const ops2=g2clone(RW(self,'g_op')); let o; let pre='';
      if(r.v.op===OUTRA_O){ const nm=String(r.v.nop).trim(); o={id:'OP'+(ops2.length+1)+'_'+String(Date.now()).slice(-4),v:{nome:nm,proc:r.v.nproc||'Tratos culturais',atvs:''},s:{},p:{}};
        ops2.push(o); g2set(self,'g_op',{rows:ops2}); rows.push({id:o.id,v:{nome:nm},s:{},p:{},kids:[]}); pre='Operação '+nm+' criada ('+o.v.proc+') · '; }
      else o=ops2.find(x=>x.v.nome===r.v.op);
      if(!o) return;
      r.v.op=o.v.nome; r.v.nop=''; r.v.cult=r.v.cult||'Todas'; if(r.v.cjid===C2.outro) r.v.cjid=''; const V=rendCalc(r.v);
      soPai('g_rend',rows,r,o.id);
      self.setState({g2toast:pre+(isNew?'Criado: ':'Salvo: ')+V.op+' rende '+nf(V.rend,2)+' ha/h a R$ '+nf(V.custo_h,2)+'/h e R$ '+nf(V.custo_ha,2)+'/ha. Novos planejamentos usam este padrão.'}); } }; }
'''
