# -*- coding: utf-8 -*-
"""CD-06 · Produtos, unidades e locais · CD-07 · Estrutura gerencial (módulo próprio; areas.cadastros.build() usa estes cd06()/cd07()).
CD-06: árvore Grupo → item. A linha do grupo abre nome e natureza de custo (da Estrutura gerencial); a do item abre unidade-base
(travada quando há saldo ou plano, com o motivo), embalagem estruturada (tipo + conteúdo na unidade-base), controle (lote e validade /
só lote / sem lote), preço de referência com data, local padrão e situação Ativo/Inativo. 'Outro grupo…' cria o grupo no formulário.
Locais com fazenda; capacidade só em tanque (informada) e silo (do ativo do CD-03). Saldos e movimentos continuam no Estoque.
CD-07: árvore Dimensão → código. Cultura e Processo vêm do CD-02 (só a tradução é editável); natureza mostra os grupos do CD-06;
centro de responsabilidade tem direcionador de rateio; versão (em vigor × rascunho) no cabeçalho; 'Importar do ERP' simulado com prévia
calculada sobre o rascunho (código que já existe não entra como novo); exclusão de código publicado entra no rascunho e sai na publicação."""
import json
from engine import grid, esc, MUTED, LINE, BG, _MINI
import engine as E
import ui37
from ui37 import shell37, HEIGHTS37
import dados as D
import dados2 as D2
import dados_cad as DC
from areas.cadastros import (sel, num, txt, dat, cond, R, js, _itens, CULTIVARES)
from areas.cad_culturas import CADC_JS
from areas.cadastros import (cadx_css, abas, pane, faixa, prim, secbtn, qf_chips, bloco_cad, estado_cab, acoes_form, arv)

H=lambda s: '{{'+s+'}}'
for _f in ('CD-06.dc.html','CD-07.dc.html'): ui37.H_OVR.pop(_f,None)   # layout novo: a altura vem de HEIGHTS37
OUTRO_G='Outro grupo…'
# naturezas analíticas da Estrutura gerencial (CD-07) oferecidas ao grupo de insumo; produto agrícola é receita
NATS={c:f'{c} · {n}' for _,d,c,n,sup,*_ in DC.ESTR if d=='Natureza' and sup}
RECEITA='Receita · sem natureza de custo'
NAT_OPTS=list(NATS.values())+[RECEITA]
def _nat(g): c=DC.GRUPO_NAT.get(g,''); return NATS.get(c,RECEITA)
UNIDS=['kg','L','un','sc 60 kg','t']

def cd06():
    fname='CD-06.dc.html'; E._reset_screen(fname)
    it=_itens(); it.update(DC.ITENS_NOVOS)
    lotes={l['item']:l for l in D2.LOTES}
    # preço de referência: fonte única em dados_cad.preco_ref (planos + extras; semente de cultivar pelo preço da semente da cultura)
    preco_de=DC.preco_ref
    # onde o item é usado nos planos (trava a unidade-base: a dose do plano é digitada nela)
    uso={}
    for p in D2.PLANOS:
        for a in p['atividades']:
            for x in a['prods']:
                nm=x['prod'] if 'do cultivo' not in x['prod'] else None
                if nm: uso.setdefault(nm,[]).append(p['nome'])
                else:
                    for n in it:
                        if n.startswith('Semente de '+p['cultura'].lower()+' '): uso.setdefault(n,[]).append(p['nome'])
    # insumo só da Lagoa Grande fica no almoxarifado dela
    import dados_lagoa_safra as DL
    lg_so={x['prod'] for p in DL.PLANOS for a in p['atividades'] for x in a['prods']}|set(DL.ESTOQUE)
    lg_so-={x['prod'] for p in D2.PLANOS if p not in DL.PLANOS for a in p['atividades'] for x in a['prods']}
    def loc(n,g):
        if n in lotes: return lotes[n]['local']
        if n in lg_so: return 'Almox. Lagoa Grande'
        return {'Herbicidas':'Almox. defensivos','Fungicidas':'Almox. defensivos','Inseticidas':'Almox. defensivos','Adjuvantes':'Almox. defensivos','Inoculantes':'Câmara fria',
                'Sementes':'Câmara fria','Fertilizantes':'Galpão 2','Corretivos':'Galpão 1','Combustível':'Tanque Sede','Embalagem':'Packing'}.get(g,'Armazém Sede')
    def saldo(n):
        if n=='Café beneficiado': return D.LOTE_BLOQ['sc']
        if n=='Diesel S10': return 9800
        return D2.ESTOQUE.get(n,0)
    gar={n:g['txt'] for n,g in DC.GARANTIA.items()}   # texto da garantia: fonte estruturada em dados_cad (SOLO-01, D-11)
    fmt=lambda x: f'{x:,.0f}'.replace(',','.')
    grupos={}; k=0
    for n,d in sorted(it.items(),key=lambda x:(x[1]['grupo'],x[0])):
        g=d['grupo']; s=saldo(n); emb,cont=DC.EMB_ITEM.get(n,('Granel',''))
        trava=(f'item com saldo de {fmt(s)} {d["un"]}' if s>0 else (f'usado no plano {uso[n][0]}' if n in uso else ''))
        pr=preco_de(n) if g!='Produto agrícola' else ''
        grupos.setdefault(g,[]).append(R(f'i{k}',dict(item=n,grupo=g,un=d['un'],emb=emb,cont=cont,ctrl=DC.CONTROLE_GRUPO.get(g,'Só lote'),
            preco=pr,pdata=DC.PRECO_DATA if pr!='' else '',gar=gar.get(n,''),local=loc(n,g),sit='Ativo',saldo=s,trava=trava),
            nd=('com saldo' if s>0 else ('em plano' if n in uso else '')))); k+=1
    ordem=[g for g in DC.GRUPOS if g in grupos]+[g for g in DC.GRUPOS if g not in grupos]   # grupo sem item (Peças) aparece vazio
    g_rows=[]; tree=[]
    for i,g in enumerate(sorted(ordem),1):
        gid=f'GR{i}'
        g_rows.append(R(gid,dict(nome=g,nat=_nat(g))))
        tree.append(dict(id=gid,v=dict(item=g),s={},p={},kids=grupos.get(g,[])))
    # item numa linha: nome e garantia · unidade e embalagem · controle · preço com data · situação; o saldo vive no Estoque (painel do item)
    gi=grid([dict(k='item',l='Grupo · item',w=330),dict(k='un',l='Unidade · embalagem',w=220),dict(k='ctrl',l='Controle'),
             dict(k='preco',l='Preço de referência',t='num',a='r',w=190),dict(k='est',l='Situação',w=300)],
        tree,gid='g_itm',tree=True,dele=False,total=False,frame=False,x0={r['id']:True for r in tree},
        tools=qf_chips('g_itm')+prim('g_itm_new','Cadastrar item'),
        edit=dict(m='form',title='Item',newTitle='Cadastrar item',
            sub='Altere o item. O saldo não se edita aqui: nasce de recebimentos e movimentos no Estoque.',
            fields=[txt('item','Nome do item'),
                    sel('grupo','Grupo',sorted(ordem)+[OUTRO_G],**{'def':'Fertilizantes'}),
                    txt('ngrupo','Nome do novo grupo',cond=cond('grupo',OUTRO_G)),
                    sel('nnat','Natureza de custo',NAT_OPTS,cond=cond('grupo',OUTRO_G),**{'def':NAT_OPTS[0]},help='Vem da Estrutura gerencial; o custo dos itens do grupo vai para ela.'),
                    sel('un','Unidade-base',UNIDS,**{'def':'kg'},help='Dose do plano, compra e estoque usam esta unidade.'),
                    sel('emb','Embalagem de entrega',DC.EMBALAGENS,**{'def':'Saco'}),
                    num('cont','Conteúdo da embalagem',req=False,min=0.001,help='Na unidade-base; retirada e compra usam embalagens inteiras.'),
                    sel('ctrl','Controle',DC.CONTROLES,**{'def':'Lote e validade'},help='Lote e validade: o recebimento pede a validade e a saída começa pela mais próxima.'),
                    num('preco','Preço de referência',req=False,min=0,help='Sem preço, o item fica pendente no custo do plano e na cotação.'),
                    dat('pdata','Data do preço',req=False),
                    txt('gar','Garantia ou densidade',req=False),
                    sel('local','Local padrão',[l[1] for l in DC.LOCAIS],**{'def':'Galpão 2'},help='O recebimento no Estoque sugere este local.'),
                    sel('sit','Situação',['Ativo','Inativo'],**{'def':'Ativo'},help='Inativo sai dos planos e das cotações; saldo e histórico continuam no Estoque.')]))
    # formulário do grupo (a linha do grupo na árvore abre este formulário)
    grid([dict(k='nome',l='Grupo')],g_rows,gid='g_grp',search=False,total=False,
         edit=dict(m='form',title='Grupo',sub='O grupo é a chave da cotação e da homologação do fornecedor; a natureza leva o custo dos itens à Estrutura gerencial.',
             fields=[txt('nome','Nome do grupo'),sel('nat','Natureza de custo',NAT_OPTS,help='Vem da Estrutura gerencial; o custo dos itens do grupo vai para ela.')]))
    cap_silo={a['local']:a for a in DC.ATIVOS if a.get('cap_sc')}
    lrows=[]
    for i,n,faz,tp,cap,capu in DC.LOCAIS:
        v=dict(nome=n,faz=faz,tipo=tp,cap=cap if tp=='Tanque' else '',capa='')
        if tp=='Silo':
            a=next((a for a in DC.ATIVOS if a['nome']==n and a.get('cap_sc')),None)
            if a: v['capa']=f'{fmt(a["cap_sc"])} sc 60 kg · ativo {a["nome"]}'
        lrows.append(R(i,v))
    gl=grid([dict(k='nome',l='Local'),dict(k='faz',l='Fazenda'),dict(k='tipo',l='Tipo'),dict(k='cap',l='Capacidade',a='r'),dict(k='itens',l='Itens com este local padrão',t='num',a='r')],
        lrows,gid='g_loc',qf=dict(k='tipo',todas='Todos'),dele=False,total=False,search=True,frame=False,tools=prim('g_loc_new','Cadastrar local'),
        edit=dict(m='form',title='Local',newTitle='Cadastrar local',sub='Altere o local de estoque. Local com itens não pode ser excluído.',
            fields=[txt('nome','Nome do local'),sel('faz','Fazenda',[f['nome'] for f in DC.FAZENDAS],**{'def':'Santa Rita'}),
                    sel('tipo','Tipo',['Galpão','Almoxarifado','Câmara fria','Tanque','Silo','Armazém'],**{'def':'Galpão'}),
                    num('cap','Capacidade do tanque','L',min=1,cond=cond('tipo','Tanque')),
                    dict(k='capa',l='Capacidade do silo',ro=True,cond=cond('tipo','Silo'),help='Vem do ativo em Máquinas, instalações e setores.')]))
    # um bloco com abas: Itens (árvore grupo › item) | Locais de estoque; exclusão e saldo no painel de cada registro
    acoes_form('g_itm'); acoes_form('g_loc'); cadx_css()
    corpo=bloco_cad(abas('c6t',['Itens','Locais de estoque'],'Cadastros de produtos'),pane('c6t',0,faixa('c6_fx0')+arv(gi))+pane('c6t',1,gl),'Produtos, unidades e locais')
    dados=json.dumps(dict(receita=RECEITA,defg=next(r['id'] for r in g_rows if r['v']['nome']=='Fertilizantes'),
                          defl=next(l[0] for l in DC.LOCAIS if l[1]=='Galpão 2')),ensure_ascii=False)
    js({},CADC_JS+f"const C6={dados}; const OUTRO_G={json.dumps(OUTRO_G,ensure_ascii=False)};\n"+r'''
// itens de semente criados no CD-02 (cultivar nova) entram no grupo Sementes ao abrir a tela; ficam pendentes de preço e embalagem
(function(){ try{ const o=JSON.parse(localStorage.getItem('talhao-os-cadastros-v1')||'{}'); const g=GR('g_itm'); const par=g.rows.find(p=>p.v.item==='Sementes'); if(!par) return;
  (o.sementes||[]).forEach((n,i)=>{ if(leaves(g.rows).some(r=>r.v.item===n)) return;
    par.kids.push({id:'ls'+i,v:{item:n,grupo:'Sementes',un:'kg',emb:'Saco',cont:'',ctrl:'Lote e validade',preco:'',pdata:'',gar:'',local:'Câmara fria',sit:'Ativo',saldo:0,trava:''},s:{},p:{},nd:''}); }); }catch(e){} })();
function c6rm(list,id){ const i=list.findIndex(x=>x.id===id); if(i>=0){ list.splice(i,1); return true; } return list.some(x=>x.kids&&c6rm(x.kids,id)); }
function c6pais(self){ return RW(self,'g_itm').filter(p=>/^GR/.test(p.id)); }
function c6custo(nat){ return nat&&nat!==C6.receita; }
function c6emb(V){ if(V.emb==='Granel') return 'granel'; return isnum(V.cont)?V.emb.toLowerCase()+' de '+nfa(V.cont)+' '+V.un:''; }
// situação do item: um só cálculo para a linha, o filtro "A resolver", a faixa, o ponto da aba e o cabeçalho
function c6sit(V){ if(V.sit==='Inativo') return {t:'Inativo',p:[chipc('Inativo','gray')]};
  if(V.custo&&!isnum(V.preco)) return {t:'Sem preço',p:sitX('Sem preço','yellow','Informar preço'),res:'pre'};
  if(!c6emb(V)) return {t:'Sem embalagem',p:sitX('Sem embalagem','yellow','Informar embalagem'),res:'emb'};
  return {t:'Em dia',p:sitOk('Em dia')}; }
CAD_ACTS.g_itm=(self,r)=>{ const s=Number(r.v.saldo)||0; const why=r.nd==='com saldo'?'tem saldo no Estoque; inative em vez de excluir':(r.nd==='em plano'?'está num plano agronômico; inative em vez de excluir':'');
  return [s?{t:'Ver saldo no Estoque ›',h:'Saldo: '+nf(s)+' '+r.v.un+'. Saldo e movimentos vivem no Estoque.',go:()=>{ location.href='EST.dc.html'; }}:null,cadExcluir(self,'g_itm',r,'item',why)]; };
CAD_ACTS.g_loc=(self,r)=>[cadExcluir(self,'g_loc',r,'local',r.nd?'tem itens com este local padrão; troque o local deles antes':'')];
function PREVALS(self,v){ cadActsIni(self); const grps=RW(self,'g_grp'); const its=[]; const locs=RW(self,'g_loc');
  c6pais(self).forEach(p=>{ const g=grps.find(x=>x.id===p.id); if(!g) return; const G=g.v; const ks=p.kids||[]; p.dr='c6g_'+p.id; p.v.item=G.nome;
    p.p.item=[{k:'b',t:G.nome},{k:'mut',t:ks.length+(ks.length===1?' item':' itens')+' · '+(c6custo(G.nat)?G.nat:'receita')}]; p.s.item=G.nome;
    ['un','ctrl','preco','est'].forEach(k=>{ p.p[k]=[{k:'mut',t:''}]; p.s[k]=''; });
    ks.forEach(r=>{ const V=r.v; V.grupo=G.nome; V.custo=c6custo(G.nat); its.push(r); r.dr='c6i_'+r.id;
      r.p.item=[{k:'b',t:V.item||''}].concat(V.gar?[{k:'mut',t:V.gar}]:[]); r.s.item=V.item||'';
      const e=c6emb(V); r.p.un=[{k:'txt',t:V.un||''},{k:'mut',t:e||'sem embalagem'}]; r.s.un=(V.un||'')+' '+(e||'sem embalagem');
      r.p.ctrl=[{k:(V.ctrl==='Sem lote'?'mut':'txt'),t:V.ctrl||'—'}]; r.s.ctrl=V.ctrl||'';
      r.p.preco=isnum(V.preco)?[{k:'mut',t:V.pdata?br(V.pdata):'sem data'},{k:'txt',t:'R$ '+nf(V.preco,2)+'/'+V.un}]:[{k:'mut',t:'—'}];
      r.s.preco=isnum(V.preco)?nf(V.preco,2):(V.custo?'Sem preço':'');
      const S=c6sit(V); r.p.est=S.p; r.s.est=S.t; }); });
  cadQf(self,v,'g_itm','c6qf',[{k:'res',t:'A resolver',f:r=>!!c6sit(r.v).res},{k:'inat',t:'Inativos',f:r=>r.v.sit==='Inativo',oz:true}]);
  const f=(GR('g_itm').edit.fields||[]).find(x=>x.k==='grupo'); if(f) f.opts=grps.map(g=>g.v.nome).sort((a,b)=>a.localeCompare(b,'pt-BR')).concat([OUTRO_G]);
  const dg=grps.find(g=>g.id===C6.defg); cadcPadrao('g_itm','grupo',dg?dg.v.nome:'');
  // Local padrão do item = locais cadastrados (novo, renomeado ou excluído acompanha); padrão pelo id do Galpão 2
  const lf=(GR('g_itm').edit.fields||[]).find(x=>x.k==='local'); if(lf) lf.opts=locs.map(l=>l.v.nome);
  const dl=locs.find(l=>l.id===C6.defl); cadcPadrao('g_itm','local',dl?dl.v.nome:'');
  locs.forEach(r=>{ const V=r.v; const n=its.filter(i=>i.v.local===V.nome).length; V.itens=n; r.nd=n?'com itens':''; r.p.nome=[{k:'b',t:V.nome||''}]; r.s.nome=V.nome||'';
    const cap=V.tipo==='Tanque'&&isnum(V.cap)?nf(V.cap)+' L':(V.tipo==='Silo'?(V.capa||''):'');
    r.p.cap=cap?[{k:'txt',t:cap}]:[{k:'mut',t:'—'}]; r.s.cap=cap; }); }
function EXTRAVALS(self,v){
  const its=leaves(RW(self,'g_itm')).filter(r=>!/^GR/.test(r.id));
  const semP=its.filter(r=>r.v.sit!=='Inativo'&&r.v.custo&&!isnum(r.v.preco)).length, semE=its.filter(r=>r.v.sit!=='Inativo'&&!c6emb(r.v)).length;
  cadEstado(v,'c6e',[semP?semP+(semP>1?' itens':' item')+' sem preço':'',semE?semE+(semE>1?' itens':' item')+' sem embalagem':''].filter(Boolean).join(' · ')||'Cadastro completo',(semP||semE)?'yellow':'green');
  cadAbas(self,v,'c6t','c6aba',[{slug:'itens',n:its.length,cor:(semP||semE)?'yellow':''},{slug:'locais',n:RW(self,'g_loc').length,cor:''}]);
  cadQfPos(self,v,'g_itm','c6qf'); cadConta(self,v,'g_itm');
  const pL=its.filter(r=>r.v.sit!=='Inativo'&&r.v.custo&&!isnum(r.v.preco)), eL=its.filter(r=>r.v.sit!=='Inativo'&&!c6emb(r.v)), res=()=>self.setState({c6qf:'res'});
  cadFaixa(v,'c6_fx0',[pL.length?{n:pL.length,rot:pL.length>1?'itens sem preço de referência':'item sem preço de referência',reg:pL.map(r=>r.v.item).join(', '),verbo:'Informar preço',
                         go:pL.length===1?()=>cadcAbrir(self,'g_itm',pL[0].id):res}:null,
                       eL.length?{n:eL.length,rot:eL.length>1?'itens sem embalagem':'item sem embalagem',reg:eL.map(r=>r.v.item).join(', '),verbo:'Informar embalagem',
                         go:eL.length===1?()=>cadcAbrir(self,'g_itm',eL[0].id):res}:null],res);
  c6pais(self).forEach(p=>{ v['c6g_'+p.id]=()=>g2open(self,GR('g_grp'),p.id,null); });
  // linha do item abre só com os valores gravados: item sem preço abre o campo vazio ('Sem preço' fica no chip da tabela)
  its.forEach(r=>{ v['c6i_'+r.id]=()=>cadcAbrir(self,'g_itm',r.id); });
  // exclusão sai da linha: fica no painel do item e do local, com a causa quando não pode (saldo, plano, itens no local)
  // formulário do item: unidade-base travada com motivo; unidade nos campos de conteúdo e preço; conteúdo some no granel
  const F=v.g_itm_F; const fm=g2st(self,'g_itm').fm;
  if(F&&F.open&&F.fields&&fm){ const r=fm.rid?its.find(x=>x.id===fm.rid):null; const d=fm.draft; const un=d.un||'';
    F.fields=F.fields.filter(f=>!(f.fid==='fx_g_itm_cont'&&d.emb==='Granel'));
    F.fields.forEach(f=>{ const k=f.fid.replace('fx_g_itm_','');
      if(k==='un'&&r&&r.v.trava&&!fm.ro){ f.dis=true; f.ist=f.ist.replace('background:#FFFFFF','background:#F4F6F3'); f.help='Travada: '+r.v.trava+'. A dose dos planos e o estoque usam esta unidade.'; f.hasHelp=true; }
      if(k==='cont'){ f.u=un; f.hasU=!!un; }
      if(k==='preco'){ f.u=un?'R$/'+un:'R$'; f.hasU=true; } }); }
  valida(self,v,'g_itm',(d,fm)=>{ const e={}; const dup=unico(self,'g_itm',fm,r=>String(r.v.item).toLowerCase(),d.item); if(dup) e.item='Já existe o item '+d.item+' em '+dup.v.grupo+'.';
    if(d.grupo===OUTRO_G){ const n=String(d.ngrupo||'').trim(); if(n&&RW(self,'g_grp').some(g=>g.v.nome.toLowerCase()===n.toLowerCase())) e.ngrupo=n+' já existe; escolha na lista Grupo.'; }
    if(d.emb!=='Granel'&&!(g2num(d.cont)>0)) e.cont='Informe quanto cabe em 1 '+String(d.emb||'embalagem').toLowerCase()+' (em '+(d.un||'unidade-base')+').';
    if(String(d.preco||'').trim()&&!d.pdata) e.pdata='Informe a data do preço.';
    if(d.grupo&&d.grupo!==OUTRO_G&&!RW(self,'g_grp').some(g=>g.v.nome===d.grupo)) e.grupo='Escolha o grupo.';
    if(d.local&&!RW(self,'g_loc').some(l=>l.v.nome===d.local)) e.local='Escolha um local cadastrado.';
    return e; });
  valida(self,v,'g_grp',(d,fm)=>{ const e={}; const n=String(d.nome||'').trim().toLowerCase(); if(RW(self,'g_grp').some(g=>g.id!==fm.rid&&g.v.nome.toLowerCase()===n)) e.nome='Já existe o grupo '+d.nome+'.'; return e; });
  valida(self,v,'g_loc',(d,fm)=>{ const e={}; const o=fm.rid?RW(self,'g_loc').find(l=>l.id===fm.rid):null; self.__c6old=o?{id:o.id,nome:o.v.nome}:null; const dup=unico(self,'g_loc',fm,r=>String(r.v.nome).toLowerCase(),d.nome); if(dup) e.nome='Já existe o local '+d.nome+'.'; return e; });
  ['g_itm','g_grp','g_loc'].forEach(g=>cadcEscolha(v,g));
  self.g2after=(gid,rows,r,isNew)=>{ if(!r) return;
    if(gid==='g_grp'){ self.setState({g2toast:'Salvo: grupo '+r.v.nome+' · '+(c6custo(r.v.nat)?'custo dos itens vai para '+r.v.nat:'receita, sem natureza de custo')+'.'}); return; }
    if(gid==='g_loc'){ const o=self.__c6old; let n=0;   // renomear o local leva junto os itens que o usam como padrão
      if(!isNew&&o&&o.id===r.id&&o.nome!==r.v.nome){ const it=g2clone(RW(self,'g_itm')); leaves(it).forEach(x=>{ if(x.v.local===o.nome){ x.v.local=r.v.nome; n++; } }); if(n) g2set(self,'g_itm',{rows:it}); }
      self.setState({g2toast:'Salvo: '+r.v.nome+' · '+r.v.faz+' · '+r.v.tipo+(n?' · '+n+(n>1?' itens passam':' item passa')+' a usar este local padrão':'')+'. O recebimento no Estoque passa a oferecer este local.'}); return; }
    if(gid!=='g_itm') return;
    if(!r.v.saldo) r.v.saldo=0; if(r.v.emb==='Granel') r.v.cont='';
    const grps=g2clone(RW(self,'g_grp')); let g; const msg=[];
    if(r.v.grupo===OUTRO_G){ const nm=String(r.v.ngrupo).trim(); g={id:'GR'+(grps.length+1)+'_'+String(Date.now()).slice(-4),v:{nome:nm,nat:r.v.nnat||C6.receita},s:{},p:{}};
      grps.push(g); g2set(self,'g_grp',{rows:grps}); rows.push({id:g.id,v:{item:nm},s:{},p:{},kids:[]}); msg.push('grupo '+nm+' cadastrado ('+g.v.nat+')'); }
    else g=grps.find(x=>x.v.nome===r.v.grupo);
    if(!g) return;
    r.v.grupo=g.v.nome; r.v.ngrupo='';
    const par=rows.find(p=>p.id===g.id); const cur=rows.find(p=>(p.kids||[]).some(k=>k.id===r.id));
    if(cur!==par){ c6rm(rows,r.id); par.kids=par.kids||[]; par.kids.push(r); }
    const x=Object.assign({},g2st(self,'g_itm').x||GR('g_itm').x0||{}); x[par.id]=true; g2set(self,'g_itm',{rows:rows,x:x,fl:r.id});
    const e=c6emb(r.v); msg.push(r.v.un+(e?' · '+e:'')); msg.push(isnum(r.v.preco)?'R$ '+nf(r.v.preco,2)+'/'+r.v.un+' em '+br(r.v.pdata):'sem preço de referência');
    if(r.v.sit==='Inativo') msg.push('inativo: sai dos planos e das cotações'+(Number(r.v.saldo)?'; o saldo de '+nf(r.v.saldo)+' '+r.v.un+' segue no Estoque':''));
    self.setState({g2toast:'Salvo: '+r.v.item+' · '+msg.join(' · ')+'.'}); }; }
''')
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a tabela da aba rola
    shell37('CD-06','Produtos, unidades e locais',corpo,fname=fname,status=None,primary_html=None,search=False)
    estado_cab(fname,'Produtos, unidades e locais','c6e')

# ================= CD-07 · Estrutura gerencial =================
TRAD=['Conta do ERP','Dimensão própria']
DIMS_MANUAIS=[d for d in DC.DIMS if d not in ('Cultura','Processo')]   # Cultura e Processo vêm do CD-02
VERSAO=5
V6_MUD={'d11':'novo','d6':'novo','d15':'novo'}   # rascunho v6 já aberto: empresa 02, centro da Boa Vista e natureza de embalagens
# prévia simulada do 'Importar do ERP': o que o Sankhya tem de diferente do rascunho
IMP=dict(novos=[dict(dim='Natureza',cod='3.1.07',nome='Serviços de terceiros',sup='3.1',conta='4.1.1.07',top='1203'),
                dict(dim='Centro de responsabilidade',cod='CC-ARM',nome='Armazém · apoio',sup='',conta='centro 312',top='',rat='kg processados')],
         alterados=[dict(cod='3.1.02',de='Defensivos',para='Defensivos agrícolas')],
         semconta=['PRJ-PIVO3 · Expansão pivô 3 · investimento'])
def _imp_html():
    lst=lambda titulo,k: (f'<div style="display: flex; flex-direction: column; gap: 2px; min-width: 220px; flex: 1 1 0;"><b style="font-size: 12px; color: {MUTED}; letter-spacing: .04em;">{esc(titulo)}</b>'
                          f'<ul style="margin: 0; padding-left: 18px; font-size: 13px;"><sc-for list="{H(k)}" as="x" hint-placeholder-count="2"><li style="padding: 2px 0;">{H("x.t")}</li></sc-for></ul></div>')
    return (f'<sc-if value="{H("c7imp_on")}" hint-placeholder-val="{H("false")}"><div role="region" aria-label="Prévia da importação do ERP" style="border: 1px solid {LINE}; border-radius: 12px; background: {BG}; padding: 12px 14px; margin-bottom: 10px; display: flex; flex-direction: column; gap: 10px;">'
            f'<div style="display: flex; align-items: center; gap: 8px;"><b style="font-size: 14px;">Prévia do ERP (Sankhya)</b><span style="font-size: 12px; color: {MUTED};">simulada · nenhum dado real é lido</span></div>'
            f'<div style="display: flex; gap: 16px; flex-wrap: wrap;">{lst("NOVOS NO ERP","c7imp_novos")}{lst("ALTERADO NO ERP","c7imp_alts")}{lst("SEM CONTA NO ERP","c7imp_sem")}</div>'
            f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("c7imp_ok")}" style="{_MINI}">{H("c7imp_okt")}</button>'
            f'<button type="button" onClick="{H("c7imp_no")}" style="{_MINI}">Descartar prévia</button></div></div></sc-if>')

def cd07():
    fname='CD-07.dc.html'; E._reset_screen(fname)
    grp_nat={}
    for g,c in DC.GRUPO_NAT.items():
        if c: grp_nat.setdefault(c,[]).append(g)
    op_proc={}
    for op,pr in DC.OP_PROC.items(): op_proc.setdefault(pr,[]).append(op)
    kids={d:[] for d in DC.DIMS}
    for i,d,c,n,sup,rat,a,b,t,ct,tp,l in DC.ESTR:
        kids[d].append(R(i,dict(dim=d,cod=c,nome=n,sup=sup,rat=rat,ini=a,fim=b,trad=t,conta=ct,top=tp,orig='',grp=', '.join(grp_nat.get(c,[])),ops=''),
                         nd=('com lançamentos' if l else ('usada em grupos' if grp_nat.get(c) else ''))))
    for j,(n,c,*_) in enumerate(DC.CULTURAS,1):   # do CD-02: só a tradução é editável aqui
        kids['Cultura'].append(R(f'cu{j}',dict(dim='Cultura',cod=c,nome=n,sup='',rat='',ini='2024-07-01',fim='',trad='Dimensão própria',conta='',top='',orig='Culturas e cultivares',grp='',ops='',cvs=sum(1 for x in CULTIVARES if x[1]==n)),nd='vem de Culturas'))
    for j,(c,n) in enumerate(DC.PROCESSOS,1):
        kids['Processo'].append(R(f'pr{j}',dict(dim='Processo',cod=c,nome=n,sup='',rat='',ini='2024-07-01',fim='',trad='Dimensão própria',conta='',top='',orig='Operações e rendimentos',grp='',ops=', '.join(op_proc.get(n,[]))),nd='vem de Operações'))
    tree=[dict(id=f'DM{i}',ro=True,v=dict(cod=d),s={},p={},kids=kids[d]) for i,d in enumerate(DC.DIMS,1)]
    g=grid([dict(k='cod',l='Dimensão · código',w=270),dict(k='vig',l='Vigência',w=170),dict(k='vinc',l='Vínculos',w=200),dict(k='conta',l='Tradução no ERP (Sankhya)',w=160),dict(k='est',l='Situação',w=240)],
        tree,gid='g_dim',tree=True,dele=False,total=False,frame=False,x0={r['id']:True for r in tree},
        tools=qf_chips('g_dim')+secbtn('c7imp','Importar do ERP','Simulação: mostra a prévia antes de trazer qualquer código')+prim('g_dim_new','Cadastrar código'),
        edit=dict(m='form',title='Código',newTitle='Cadastrar código',leafOnly=True,
            sub='Altere o código e a tradução. A mudança entra no rascunho e vale para novos lançamentos depois de publicada; fatos já gravados mantêm as dimensões da época.',
            fields=[txt('cod','Código'),txt('nome','Nome'),sel('dim','Dimensão',DIMS_MANUAIS,**{'def':'Natureza'},help='Cada código em uma dimensão: nunca combine fazenda, cultura e processo num único centro.'),
                    txt('sup','Código superior',req=False,help='Soma no total do superior (ex.: 3.1.01 em 3.1).'),
                    sel('rat','Direcionador de rateio',DC.RATEIO,cond=cond('dim','Centro de responsabilidade'),**{'def':DC.RATEIO[0]},help='Como o custo deste centro chega às culturas, em vez de ratear tudo por hectare.'),
                    dict(k='grp',l='Grupos de insumo',ro=True,cond=cond('dim','Natureza'),help='Vêm de Produtos, unidades e locais; troque a natureza no grupo.'),
                    dict(k='ops',l='Operações',ro=True,cond=cond('dim','Processo'),help='Vêm de Culturas, cultivares e operações; troque o processo na operação.'),
                    dat('ini','Início da vigência'),dat('fim','Fim da vigência',req=False,help='Deixe em branco se não houver fim previsto.'),
                    sel('trad','Tradução no ERP',TRAD,**{'def':'Conta do ERP'},help='Dimensão própria segue no lançamento e é traduzida pela integração, sem conta fixa.'),
                    txt('conta','Conta ou centro no ERP',req=False,cond=cond('trad','Conta do ERP'),help='Em branco, o código fica fora da publicação até ser mapeado. Exemplo: pulverização na soja do T1 = empresa 01 + natureza 3.1.02 + CR-SR + cultura SOJA + processo TRAT + talhão T1 → conta 4.1.1.02 · TOP 1201.'),
                    txt('top','Tipo de operação (TOP) no ERP',req=False,cond=cond('trad','Conta do ERP'))]))
    # um bloco (sem abas: a dimensão é o 1º nível da árvore). Na faixa: publicar o rascunho e traduzir o que falta; Importar do ERP na barra
    acoes_form('g_dim'); cadx_css()
    corpo=bloco_cad('',faixa('c7_fx')+f'<div style="padding: 0 16px;">{_imp_html()}</div>'+arv(g),'Estrutura gerencial')
    dados=json.dumps(dict(ver=VERSAO,mud=V6_MUD,imp=IMP,dims=DC.DIMS),ensure_ascii=False)
    js({},CADC_JS+f"const C7={dados};\n"+r'''
function c7rm(list,id){ const i=list.findIndex(x=>x.id===id); if(i>=0){ list.splice(i,1); return true; } return list.some(x=>x.kids&&c7rm(x.kids,id)); }
function c7ver(self){ return self.state.c7ver||C7.ver; }
function c7mud(self){ return self.state.c7mud||C7.mud; }
function c7cods(self){ return leaves(RW(self,'g_dim')).filter(r=>r.v.dim); }
// código excluído no rascunho continua na tabela até publicar, mas já não conta como vigente para a próxima versão
function c7vivos(self){ const m=c7mud(self); return c7cods(self).filter(r=>m[r.id]!=='excluído'); }
function c7pend(self){ return c7vivos(self).filter(r=>r.v.trad!=='Dimensão própria'&&!r.v.conta); }
// exclusão: código novo do rascunho sai na hora; código já publicado entra no rascunho e sai na publicação
function c7excluir(self,id){ const ver=c7ver(self); const m=Object.assign({},c7mud(self)); const rows=g2clone(RW(self,'g_dim')); const r=g2find(rows,id); if(!r) return;
  const nome=r.v.cod+' · '+r.v.nome;
  if(m[id]==='novo'){ c7rm(rows,id); delete m[id]; g2set(self,'g_dim',{rows,cf:null}); self.setState({c7mud:m,g2toast:'Excluído do rascunho v'+(ver+1)+': '+nome+' (não chegou a ser publicado).'}); return; }
  m[id]='excluído'; r.ro=true; g2set(self,'g_dim',{rows,cf:null});
  self.setState({c7mud:m,g2toast:'Exclusão de '+nome+' no rascunho v'+(ver+1)+': o código sai da estrutura para novos lançamentos quando a versão for publicada.'}); }
// prévia do ERP calculada sobre o rascunho: código que já existe na dimensão não é novo (vira alteração, se algo difere)
function c7impCalc(self){ const viv=c7vivos(self); const novos=[], alts=[];
  C7.imp.novos.forEach(x=>{ const r=viv.find(q=>q.v.dim===x.dim&&q.v.cod===x.cod); if(!r){ novos.push(x); return; }
    const set={}, t=[]; if(r.v.nome!==x.nome){ set.nome=x.nome; t.push(r.v.nome+' → '+x.nome); }
    if(x.conta&&r.v.conta!==x.conta){ set.conta=x.conta; set.trad='Conta do ERP'; t.push('conta '+(r.v.conta||'—')+' → '+x.conta); }
    if(x.top&&r.v.top!==x.top){ set.top=x.top; t.push('TOP '+(r.v.top||'—')+' → '+x.top); }
    if(t.length) alts.push({id:r.id,set,t:x.cod+' · '+t.join(' · ')}); });
  C7.imp.alterados.forEach(x=>{ const r=viv.find(q=>q.v.dim==='Natureza'&&q.v.cod===x.cod); if(r&&r.v.nome!==x.para) alts.push({id:r.id,set:{nome:x.para},t:x.cod+' · '+r.v.nome+' → '+x.para}); });
  return {novos,alts,n:novos.length+alts.length}; }
// situação do código: excluído no rascunho, tradução pendente, mapeado ou dimensão própria (com "novo/alterado na vN")
function c7sit(self,r){ const V=r.v; const m=c7mud(self)[r.id]; const nv=c7ver(self)+1; const prop=V.trad==='Dimensão própria'; const ex=m&&m!=='excluído'?[{k:'mut',t:m+' na v'+nv}]:[];
  if(m==='excluído') return {t:'Excluído',p:[chipc('Excluído','gray'),{k:'mut',t:'sai na v'+nv}]};
  if(!prop&&!V.conta) return {t:'Tradução pendente',p:sitX('Tradução pendente','yellow','Traduzir').concat(ex),res:true};
  return {t:prop?'Dimensão própria':'Mapeado',p:(prop?sitInfo('Dimensão própria'):sitOk('Mapeado')).concat(ex)}; }
const C7_ND={'com lançamentos':'tem lançamentos; encerre a vigência em vez de excluir','usada em grupos':'é a natureza de grupos de insumo em Produtos; troque lá antes',
  'vem de Culturas':'vem de Culturas, cultivares e operações; exclua lá','vem de Operações':'vem de Culturas, cultivares e operações; exclua lá'};
CAD_ACTS.g_dim=(self,r,fm)=>{ if(!r.v.dim||r.ro||fm.ro) return []; return [cadExcluir(self,'g_dim',r,'código',C7_ND[r.nd]||r.nd||'',()=>c7excluir(self,r.id))]; };
function PREVALS(self,v){ cadActsIni(self); const mud=c7mud(self); const cods=c7vivos(self);
  c7cods(self).forEach(r=>{ if(mud[r.id]==='excluído') r.ro=true; });
  RW(self,'g_dim').forEach(p=>{ const ks=(p.kids||[]).filter(k=>k.v.dim); const orig=ks.length&&ks[0].v.orig;
    p.p.cod=[{k:'b',t:p.v.cod},{k:'mut',t:ks.length+(ks.length===1?' código':' códigos')+(orig?' · de '+orig:'')}]; p.s.cod=p.v.cod; });
  c7cods(self).forEach(r=>{ const V=r.v;
    r.p.cod=[{k:'b',t:V.cod||''},{k:'mut',t:(V.nome||'')+(V.sup?' · em '+V.sup:'')}]; r.s.cod=(V.cod||'')+' '+(V.nome||'');
    r.p.vig=[{k:'txt',t:V.fim?br(V.ini)+' – '+br(V.fim):'desde '+br(V.ini)}]; r.s.vig=V.ini||'';
    let vi='';
    if(V.dim==='Natureza'){ const fil=cods.filter(x=>x.v.dim==='Natureza'&&x.v.sup===V.cod).length; vi=fil?'soma '+fil+(fil===1?' natureza':' naturezas'):(V.grp?'grupos '+V.grp:''); }
    else if(V.dim==='Processo') vi=V.ops?'operações '+V.ops:'';
    else if(V.dim==='Cultura') vi=V.cvs?V.cvs+(Number(V.cvs)===1?' cultivar':' cultivares'):'';
    else if(V.dim==='Centro de responsabilidade') vi=V.rat?'rateio por '+String(V.rat).toLowerCase():'';
    r.p.vinc=vi?[{k:'txt',t:vi}]:[{k:'mut',t:'—'}]; r.s.vinc=vi;
    const prop=V.trad==='Dimensão própria';
    r.p.conta=prop?[{k:'mut',t:'traduzida na integração'}]:(V.conta?[{k:'txt',t:V.conta+(V.top?' · TOP '+V.top:'')}]:[{k:'mut',t:'sem conta'}]); r.s.conta=V.conta||'';
    const S=c7sit(self,r); r.p.est=S.p; r.s.est=S.t; });
  RW(self,'g_dim').forEach(p=>{ ['vig','vinc','conta','est'].forEach(k=>{ p.p[k]=[{k:'mut',t:''}]; p.s[k]=''; }); });
  const nv=c7ver(self)+1;
  cadQf(self,v,'g_dim','c7qf',[{k:'alt',t:'No rascunho v'+nv,f:r=>!!mud[r.id]},{k:'res',t:'A resolver',f:r=>!!c7sit(self,r).res}]); }
function EXTRAVALS(self,v){ const ver=c7ver(self), mud=c7mud(self), n=Object.keys(mud).length, pend=c7pend(self).length;
  cadEstado(v,'c7e','v'+ver+' em vigor'+(n?' · rascunho v'+(ver+1)+' com '+n+(n===1?' alteração':' alterações'):'')+(pend?' · '+pend+(pend===1?' tradução pendente':' traduções pendentes'):''),(n||pend)?'yellow':'green');
  cadQfPos(self,v,'g_dim','c7qf'); cadConta(self,v,'g_dim');
  // faixa: o próximo passo do rascunho (publicar) e a tradução que falta; a exclusão vai para o painel do código (entra no rascunho)
  const pl=c7pend(self);
  cadFaixa(v,'c7_fx',[n?{n:n,rot:(n===1?'alteração':'alterações')+' no rascunho v'+(ver+1),reg:'v'+ver+' segue em vigor até publicar',verbo:'Publicar estrutura',cor:'yellow',go:()=>v.c7pub()}:null,
                      pend?{n:pend,rot:pend===1?'tradução pendente':'traduções pendentes',reg:pl.map(r=>r.v.cod+' · '+r.v.nome).join(', '),verbo:'Traduzir no ERP',cor:'yellow',
                            go:pend===1?()=>g2open(self,GR('g_dim'),pl[0].id,null):()=>self.setState({c7qf:'res'})}:null]);
  // código vindo do CD-02 (Cultura, Processo): só a tradução é editável
  const F=v.g_dim_F; const fm=g2st(self,'g_dim').fm;
  if(F&&F.open&&fm&&fm.rid&&mud[fm.rid]==='excluído') F.sub='Excluído no rascunho v'+(ver+1)+': o código sai da estrutura quando a versão for publicada; até lá, só consulta.';
  if(F&&F.open&&F.fields&&fm&&fm.rid&&!fm.ro){ const r=g2find(RW(self,'g_dim'),fm.rid);
    if(r&&r.v.orig){ F.sub=r.v.dim+' vem de Culturas, cultivares e operações: aqui você altera só a tradução para o ERP.';
      F.fields=F.fields.filter(f=>['fx_g_dim_sup'].indexOf(f.fid)<0);
      F.fields.forEach(f=>{ const k=f.fid.replace('fx_g_dim_',''); if(['cod','nome','dim','ini','fim'].indexOf(k)>=0){ f.dis=true; f.ist=f.ist.replace('background:#FFFFFF','background:#F4F6F3'); if(k==='dim') f.opts=[{v:r.v.dim,t:r.v.dim}]; } }); } }
  valida(self,v,'g_dim',(d,fm)=>{ const e={}; const r=fm.rid?g2find(RW(self,'g_dim'),fm.rid):null; if(r&&r.v.orig) return e;
    if(d.fim&&d.ini&&d.fim<d.ini) e.fim='O fim da vigência não pode ser antes do início ('+br(d.ini)+').';
    const dup=unico(self,'g_dim',fm,r=>(r.v.dim+'|'+r.v.cod).toLowerCase(),d.dim+'|'+d.cod); if(dup) e.cod='O código '+d.cod+' já existe em '+d.dim+'.';
    const sp=String(d.sup||'').trim(); if(sp){ if(sp===String(d.cod).trim()) e.sup='O superior não pode ser o próprio código.';
      else if(!c7vivos(self).some(x=>x.v.dim===d.dim&&x.v.cod===sp)) e.sup='Não existe o código '+sp+' em '+d.dim+'.'; }
    return e; });
  const marca=(id,tipo)=>{ const m=Object.assign({},c7mud(self)); if(!m[id]) m[id]=tipo; self.setState({c7mud:m}); };
  self.g2after=(gid,rows,r,isNew)=>{ if(gid!=='g_dim'||!r) return;
    const par=rows.find(p=>p.v.cod===r.v.dim&&p.kids); const cur=rows.find(p=>(p.kids||[]).some(k=>k.id===r.id));
    if(par&&cur!==par){ c7rm(rows,r.id); par.kids.push(r); const x=Object.assign({},g2st(self,'g_dim').x||GR('g_dim').x0||{}); x[par.id]=true; g2set(self,'g_dim',{rows:rows,x:x,fl:r.id}); }
    marca(r.id,isNew?'novo':'alterado');
    self.setState({g2toast:'Salvo no rascunho v'+(c7ver(self)+1)+': '+r.v.cod+' · '+r.v.nome+(r.v.trad==='Dimensão própria'?' · traduzido na integração':(r.v.conta?' → '+r.v.conta:' · sem conta: fica fora da publicação até ser mapeado'))+'.'}); };
  const SEMNOV='Simulação: o ERP não tem mudanças novas para o rascunho.'; const IC=c7impCalc(self); const lis=a=>a.length?a:[{t:'nenhum'}];
  v.c7imp=()=>{ if(!c7impCalc(self).n){ self.setState({c7imp:false,g2toast:SEMNOV}); return; } self.setState({c7imp:true}); };
  v.c7imp_on=!!self.state.c7imp;
  v.c7imp_novos=lis(IC.novos.map(x=>({t:x.cod+' · '+x.nome+' · '+x.conta+(x.top?' · TOP '+x.top:'')})));
  v.c7imp_alts=lis(IC.alts.map(a=>({t:a.t}))); v.c7imp_sem=lis(c7pend(self).map(r=>({t:r.v.cod+' · '+r.v.nome})));
  v.c7imp_okt='Trazer '+IC.n+(IC.n===1?' mudança':' mudanças')+' para o rascunho';
  v.c7imp_no=()=>self.setState({c7imp:false,g2toast:'Prévia descartada · nada mudou no rascunho.'});
  v.c7imp_ok=()=>{ const C=c7impCalc(self); if(!C.n){ self.setState({c7imp:false,g2toast:SEMNOV}); return; }
    const rows=g2clone(RW(self,'g_dim')); const m=Object.assign({},c7mud(self)); const suf=String(Date.now()).slice(-5);
    C.novos.forEach((x,i)=>{ const par=rows.find(p=>p.v.cod===x.dim&&p.kids); if(!par) return; const id='imp'+(i+1)+'_'+suf; par.kids.push({id,v:{dim:x.dim,cod:x.cod,nome:x.nome,sup:x.sup,rat:x.rat||'',ini:'2026-10-01',fim:'',trad:'Conta do ERP',conta:x.conta,top:x.top,orig:'',grp:'',ops:''},s:{},p:{}}); m[id]='novo'; });
    C.alts.forEach(a=>{ const r=g2find(rows,a.id); if(r){ Object.assign(r.v,a.set); m[r.id]=m[r.id]||'alterado'; } });
    const nn=C.novos.length, na=C.alts.length; const txt=[nn?nn+(nn>1?' códigos novos':' código novo'):'',na?na+(na>1?' códigos alterados':' código alterado'):''].filter(Boolean).join(' e ');
    g2set(self,'g_dim',{rows}); self.setState({c7imp:false,c7mud:m,g2toast:'Rascunho v'+(c7ver(self)+1)+': '+txt+' vindos do ERP · nada foi publicado.'}); };
  v.c7pub=()=>{ const m=c7mud(self); const n=Object.keys(m).length; const ver=c7ver(self);
    if(!n){ self.setState({g2toast:'Nada a publicar: o rascunho não tem alterações.'}); return; }
    const exc=Object.keys(m).filter(id=>m[id]==='excluído'); const rows=g2clone(RW(self,'g_dim')); exc.forEach(id=>c7rm(rows,id));
    const cs=leaves(rows).filter(r=>r.v.dim); const pend=cs.filter(r=>r.v.trad!=='Dimensão própria'&&!r.v.conta);
    if(exc.length) g2set(self,'g_dim',{rows});
    self.setState({c7ver:ver+1,c7mud:{},g2toast:'Simulação: estrutura v'+(ver+1)+' publicada para novos lançamentos com '+(cs.length-pend.length)+' de '+cs.length+' códigos'
      +(exc.length?' · '+exc.length+(exc.length>1?' códigos excluídos':' código excluído'):'')+' · v'+ver+' preservada'+(pend.length?' · fora até ter conta: '+pend.map(r=>r.v.cod).join(', '):'')+'.'}); }; }
''')
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a árvore rola
    shell37('CD-07','Estrutura gerencial',corpo,fname=fname,status=None,primary_html=None,search=False)
    estado_cab(fname,'Estrutura gerencial','c7e')
