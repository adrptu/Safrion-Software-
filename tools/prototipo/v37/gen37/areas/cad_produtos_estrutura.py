# -*- coding: utf-8 -*-
"""CD-06 · Produtos, unidades e locais · CD-07 · Estrutura gerencial (módulo próprio; areas.cadastros.build() usa estes cd06()/cd07()).
CD-06: árvore Grupo → item. A linha do grupo abre nome e natureza de custo (da Estrutura gerencial); a do item abre unidade-base
(travada quando há saldo ou plano, com o motivo), embalagem estruturada (tipo + conteúdo na unidade-base), controle (lote e validade /
só lote / sem lote), preço de referência com data, local padrão e situação Ativo/Inativo. 'Outro grupo…' cria o grupo no formulário.
Locais com fazenda; capacidade só em tanque (informada) e silo (do ativo do CD-03). Saldos e movimentos continuam no Estoque.
CD-07 (CADUX P8): mestre com as 7 dimensões → árvore Código › subcódigo → painel do código em consulta. Cultura e Processo vêm do CD-02
(só a tradução é editável, sem "+ Criar código"); natureza mostra os grupos do CD-06;
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
from areas.cadastros import (cadx_css, abas, pane, se, faixa, prim, secbtn, qf_chips, bloco_cad, estado_cab, acoes_form, arv,
                             md, mestre, det_cab, vazio, md_css, criar_cab, ncol_dinamico)

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
    # preço de referência: o dos planos (última cotação homologada) e os extras; semente de cultivar usa o preço da semente da cultura no plano
    preco={}
    for p in D2.PLANOS:
        for a in p['atividades']:
            for x in a['prods']:
                if 'do cultivo' in x['prod']: preco.setdefault('Semente de '+p['cultura'].lower(),x['preco'])
                else: preco.setdefault(x['prod'],x['preco'])
    preco.update(DC.PRECO_EXTRA)
    def preco_de(n): return preco.get(n, next((v for k,v in preco.items() if k.startswith('Semente de ') and n.startswith(k+' ')),''))
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
    gar={'MAP 11-52':'11% N · 52% P₂O₅','KCl 60%':'60% K₂O','Ureia 45%':'45% N','NPK 20-05-20':'20-05-20','Nitrato de cálcio':'15,5% N · 19% Ca','Nitrato de potássio':'13% N · 44% K₂O',
         'Diesel S10':'densidade 0,85 kg/L a 20 °C','Soja em grão':'umidade-base 14%','Café beneficiado':'umidade-base 12%',DC.CX_MAMAO:'tara '+DC.EMB_PACK[DC.CX_MAMAO]['tara'].replace('.',',')+' kg',
         'Calcário dolomítico':'PRNT 85%'}
    fmt=lambda x: f'{x:,.0f}'.replace(',','.')
    grupos={}; k=0
    for n,d in sorted(it.items(),key=lambda x:(x[1]['grupo'],x[0])):
        g=d['grupo']; s=saldo(n); emb,cont=DC.EMB_ITEM.get(n,('Granel',''))
        # saldo, lotes e trava da unidade-base são da tela, lidos do cenário do Estoque ao abrir (c6saldo; achado 4 da revisão): aqui só ficam o
        # saldo inicial dos itens que não têm lote no cenário (Diesel, café beneficiado) e o plano que usa o item
        pr=preco_de(n) if g!='Produto agrícola' else ''
        grupos.setdefault(g,[]).append(R(f'i{k}',dict(item=n,grupo=g,un=d['un'],emb=emb,cont=cont,ctrl=DC.CONTROLE_GRUPO.get(g,'Só lote'),
            preco=pr,pdata=DC.PRECO_DATA if pr!='' else '',gar=gar.get(n,''),local=loc(n,g),sit='Ativo',saldo0=s,plano=(uso[n][0] if n in uso else ''),trava=''))); k+=1
    ordem=[g for g in DC.GRUPOS if g in grupos]+[g for g in DC.GRUPOS if g not in grupos]   # grupo sem item (Peças) aparece vazio
    g_rows=[]; tree=[]
    for i,g in enumerate(sorted(ordem),1):
        gid=f'GR{i}'
        g_rows.append(R(gid,dict(nome=g,nat=_nat(g))))
        tree.append(dict(id=gid,v=dict(item=g),s={},p={},kids=grupos.get(g,[])))
    # CADUX (09/10/2026): mestre Todos os itens · grupos · Locais de estoque → itens do grupo (natureza uma vez, no cabeçalho do grupo: I18) →
    # painel do item em consulta (unidade-base com a trava, embalagem e conteúdo, controle, preço, locais com saldo, fornecedores, registro e bula).
    # Item | Situação | Unidade-base | Embalagem | Controle | Preço de referência | Data do preço (a natureza sai da linha)
    gi=grid([dict(k='item',l='Item',w=230),dict(k='est',l='Situação',w=170),dict(k='un',l='Unidade-base'),dict(k='embt',l='Embalagem',w=150),
             dict(k='ctrl',l='Controle'),dict(k='preco',l='Preço de referência',t='num',a='r',w=140),dict(k='pdata',l='Data do preço',t='date')],
        tree,gid='g_itm',tree=True,dele=False,total=False,frame=False,search=False,x0={r['id']:True for r in tree},
        tools=f'<span class="cmd-conta">{H("c6_conta")}</span>'+qf_chips('g_itm'),
        edit=dict(m='form',title='Item',newTitle='Criar item',leafOnly=True,alvo='item',
            sub='Altere o item. O saldo não se edita aqui: nasce de recebimentos e movimentos no Estoque.',
            # criação mínima sem padrão escondido (regra 6, R14): unidade-base, embalagem, conteúdo e local padrão nascem vazios; o controle vem do grupo
            fields=[txt('item','Nome do item'),
                    sel('grupo','Grupo',sorted(ordem)+[OUTRO_G]),
                    txt('ngrupo','Nome do novo grupo',cond=cond('grupo',OUTRO_G)),
                    sel('nnat','Natureza de custo',NAT_OPTS,cond=cond('grupo',OUTRO_G),help='Vem da Estrutura gerencial; o custo dos itens do grupo vai para ela. Defensivos pedem o local próprio (NR-31) e nascem com lote e validade.'),
                    sel('un','Unidade-base',UNIDS,help='Dose do plano, compra e estoque usam esta unidade; trava depois do 1º saldo e só troca dentro da mesma grandeza.'),
                    sel('emb','Embalagem de entrega',DC.EMBALAGENS,help='Retirada e compra são em embalagens inteiras.'),
                    num('cont','Conteúdo da embalagem',req=False,min=0.001,help='Na unidade-base; retirada e compra usam embalagens inteiras.'),
                    sel('ctrl','Controle',DC.CONTROLES,help='Vem do grupo. Lote e validade: o recebimento pede a validade e a saída começa pela mais próxima.'),
                    num('preco','Preço de referência',req=False,min=0,help='Sem preço, o item fica pendente no custo do plano e na cotação.'),
                    dat('pdata','Data do preço',req=False),
                    txt('gar','Garantia ou densidade',req=False),
                    sel('local','Local padrão',[l[1] for l in DC.LOCAIS],req=False,help='O recebimento no Estoque sugere este local. Defensivo pede o almoxarifado próprio (NR-31).'),
                    sel('sit','Situação',['Ativo','Inativo'],**{'def':'Ativo'},help='Inativo sai dos planos e das cotações; saldo e histórico continuam no Estoque.')]))
    # grupo: fonte do mestre e da ficha (natureza de custo do CD-07)
    grid([dict(k='nome',l='Grupo')],g_rows,gid='g_grp',search=False,total=False,
         edit=dict(m='form',title='Grupo',newTitle='Criar grupo',sub='O grupo é a chave da cotação e da homologação do fornecedor; a natureza leva o custo dos itens à Estrutura gerencial.',
             fields=[txt('nome','Nome do grupo'),sel('nat','Natureza de custo',NAT_OPTS,help='Vem da Estrutura gerencial; o custo dos itens do grupo vai para ela.')]))
    cap_silo={a['local']:a for a in DC.ATIVOS if a.get('cap_sc')}
    lrows=[]
    for i,n,faz,tp,cap,capu in DC.LOCAIS:
        v=dict(nome=n,faz=faz,tipo=tp,cap=cap if tp=='Tanque' else '',capa='',capsc='')
        if tp=='Silo':
            a=next((a for a in DC.ATIVOS if a['nome']==n and a.get('cap_sc')),None)
            if a: v['capa']=f'{fmt(a["cap_sc"])} sc 60 kg · ativo {a["nome"]}'; v['capsc']=a['cap_sc']
        lrows.append(R(i,v))
    gl=grid([dict(k='nome',l='Local'),dict(k='faz',l='Fazenda'),dict(k='tipo',l='Tipo'),dict(k='capn',l='Capacidade',t='num',a='r'),dict(k='itens',l='Itens com este local padrão',t='num',a='r')],
        lrows,gid='g_loc',qf=dict(k='tipo',todas='Todos'),dele=False,total=False,search=False,frame=False,tools=f'<span class="cmd-conta">{H("c6_contaLoc")}</span>',
        edit=dict(m='form',title='Local',newTitle='Criar local',alvo='local',sub='Altere o local de estoque. Local com itens não pode ser excluído.',
            fields=[txt('nome','Nome do local'),sel('faz','Fazenda',[f['nome'] for f in DC.FAZENDAS]),
                    sel('tipo','Tipo',['Galpão','Almoxarifado','Câmara fria','Tanque','Silo','Armazém'],**{'def':'Galpão'}),
                    num('cap','Capacidade do tanque','L',min=1,cond=cond('tipo','Tanque')),
                    dict(k='capa',l='Capacidade do silo',ro=True,cond=cond('tipo','Silo'),help='Vem do ativo em Máquinas, instalações e setores.')]))
    acoes_form('g_itm'); acoes_form('g_loc'); cadx_css(); md_css()
    det=det_cab()+f'<div class="cadx-dados">'+vazio('c6_v')+se('c6_itm_on',arv(gi),True)+se('c6_loc_on',gl)+'</div>'
    corpo=md(mestre('Grupos de itens','Buscar item, grupo ou local',secbtn('c6_ngrp','+ Criar grupo')),det,'Produtos, unidades e locais')
    forn={}
    for f in D2.FORNECEDORES:
        if f.get('homologado'):
            for gname in f.get('grupos') or []: forn.setdefault(gname,[]).append(dict(id=f['id'],nome=f['nome']))
    dados=json.dumps(dict(receita=RECEITA,defg=next(r['id'] for r in g_rows if r['v']['nome']=='Fertilizantes'),ctrlg=DC.CONTROLE_GRUPO,
                          defens=[g for g,c in DC.GRUPO_NAT.items() if c=='3.1.02'],forn=forn,natcod={v:k for k,v in NATS.items()},
                          grand={'kg':'massa','t':'massa','sc 60 kg':'massa','L':'volume','un':'contagem'}),ensure_ascii=False)
    js({},CADC_JS+f"const C6={dados}; const OUTRO_G={json.dumps(OUTRO_G,ensure_ascii=False)};\n"+CD06JS)
    import cenario
    E.EXTRAJS[0]=cenario.js_prefixo()+E.EXTRAJS[0]   # saldos e lotes do cenário compartilhado do Estoque (a mesma leitura do EST)
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a lista rola
    shell37('CD-06','Produtos, unidades e locais',corpo,fname=fname,status=None,primary_html=criar_cab('c6_criar','+ Criar item'),search=False)
    estado_cab(fname,'Produtos, unidades e locais','c6e')
CD06JS=r'''
// itens de semente criados no CD-02 (cultivar nova) entram no grupo Sementes ao abrir a tela; ficam pendentes de preço e embalagem
(function(){ try{ const o=cadLS(); const g=GR('g_itm'); const par=g.rows.find(p=>p.v.item==='Sementes'); if(!par) return;
  (o.sementes||[]).forEach((n,i)=>{ if(leaves(g.rows).some(r=>r.v.item===n)) return;
    par.kids.push({id:'ls'+i,v:{item:n,grupo:'Sementes',un:'kg',emb:'',cont:'',ctrl:'Lote e validade',preco:'',pdata:'',gar:'',local:'Câmara fria',sit:'Ativo',saldo0:0,plano:'',trava:''},s:{},p:{},nd:''}); }); }catch(e){} })();
// saldo e lotes do item: a mesma fonte do Estoque (cenário compartilhado, cenGet().lotes), não números congelados no build (achado 4 da revisão).
// Item sem lote no cenário (Diesel S10, café beneficiado) fica com o saldo inicial. A trava da unidade-base vale com estoque FÍSICO: um lote todo
// reservado (NPK 20-05-20: 8.000 kg físicos, 0 disponível) continua na unidade dele; travar pelo disponível soltaria a unidade com estoque no galpão
function c6saldo(V){ let ls=[]; try{ const c=cenGet(); ls=Object.values(c.lotes||{}).filter(l=>l.prod===V.item).map(l=>{ const f=Number(l.fisico)||0;
    return {lote:l.lote,local:l.local,un:l.un||V.un,fis:f,livre:f-(Number(l.reservado)||0)-(Number(l.quarentena)||0),val:l.validade||''}; }); }catch(e){ ls=[]; }
  if(ls.length) return {ls:ls,fis:ls.reduce((a,x)=>a+x.fis,0),livre:ls.reduce((a,x)=>a+x.livre,0)};
  const s=Number(V.saldo0)||0; return {ls:[],fis:s,livre:s}; }
function c6trava(V){ const s=c6saldo(V); if(s.fis>0) return 'item com '+nf(s.fis)+' '+V.un+' no Estoque'+(s.ls.length?' ('+nf(s.livre)+' '+V.un+' disponíveis)':'');
  return V.plano?'usado no plano '+V.plano:''; }
function c6rm(list,id){ const i=list.findIndex(x=>x.id===id); if(i>=0){ list.splice(i,1); return true; } return list.some(x=>x.kids&&c6rm(x.kids,id)); }
function c6pais(self){ return RW(self,'g_itm').filter(p=>/^GR/.test(p.id)); }
function c6custo(nat){ return nat&&nat!==C6.receita; }
function c6emb(V){ if(V.emb==='Granel') return 'granel'; return (V.emb&&isnum(V.cont))?V.emb.toLowerCase()+' de '+nfa(V.cont)+' '+V.un:''; }
// situação do item: um só cálculo para a linha (só o estado), o filtro "A resolver", o mestre e o cabeçalho
function c6sit(V){ if(V.sit==='Inativo') return {t:'Inativo',p:[chipc('Inativo','gray')]};
  if(V.custo&&!isnum(V.preco)) return {t:'Sem preço',p:sitX('Sem preço','yellow'),res:'pre'};
  if(!c6emb(V)) return {t:'Sem embalagem',p:sitX('Sem embalagem','yellow'),res:'emb'};
  return {t:'Em dia',p:sitOk('Em dia')}; }
// B24: a unidade-base só troca dentro da mesma grandeza (massa: kg, t, sc 60 kg; volume: L; contagem: un) e trava com saldo ou plano (C1);
// troca não reescreve lançamentos. Item novo escolhe qualquer uma. Devolve '' (pode) ou o motivo.
function c6unTroca(de,para,trava){ if(!de||de===para) return ''; if(trava) return 'Unidade-base travada: '+trava+'. A dose dos planos e o estoque usam '+de+'.';
  const a=C6.grand[de], b=C6.grand[para]; if(a&&b&&a!==b) return 'A unidade-base só troca dentro da mesma grandeza ('+a+'): '+de+' → '+para+' mudaria dose, compra e estoque.'; return ''; }
function c6grp(self,id){ return RW(self,'g_grp').find(g=>g.id===id)||null; }
const C6LOC='locais';
CAD_ACTS.g_itm=(self,r)=>{ const why=r.nd==='com saldo'?'tem saldo no Estoque; inative em vez de excluir':(r.nd==='em plano'?'está num plano agronômico; inative em vez de excluir':''); return [cadExcluir(self,'g_itm',r,'item',why)]; };
CAD_ACTS.g_loc=(self,r)=>[cadExcluir(self,'g_loc',r,'local',r.nd?'tem itens com este local padrão; troque o local deles antes':'')];
function c6pends(self,gid){ const out=[]; const grp=gid&&gid!==C6LOC?c6grp(self,gid):null;
  leaves(RW(self,'g_itm')).filter(r=>!/^GR/.test(r.id)&&(!grp||r.v.grupo===grp.v.nome)).forEach(r=>{ const S=c6sit(r.v); if(!S.res) return; const V=r.v;
    out.push(S.res==='pre'?{cor:'yellow',t:V.item+' sem preço de referência: fica pendente no custo do plano e na cotação.',prim:{t:'Informar preço do '+V.item,go:()=>{ g2open(self,GR('g_itm'),r.id,null); setTimeout(()=>g2editar(self,GR('g_itm'),r.id,'preco'),0); }},s:V.item+' sem preço'}
      :{cor:'yellow',t:V.item+' sem embalagem: a retirada e a compra são em embalagens inteiras.',prim:{t:'Informar embalagem do '+V.item,go:()=>{ g2open(self,GR('g_itm'),r.id,null); setTimeout(()=>g2editar(self,GR('g_itm'),r.id,'emb'),0); }},s:V.item+' sem embalagem'}); });
  return out; }
function c6prox(ps,ok){ if(!ps.length) return {cor:'green',t:ok||'Em dia: itens com preço e embalagem.'}; const p=ps[0], r=ps.slice(1);
  return {cor:p.cor,t:p.t,prim:p.prim||null,mais:r.length?('e mais '+r.length+': '+r.map(x=>x.s).join('; ')+'.'):''}; }
function c6consItm(self,r){ const V=r.v; const S=c6sit(V); const e=c6emb(V); const sd=c6saldo(V); const ls=sd.ls; const fo=C6.forn[V.grupo]||[]; const g=RW(self,'g_grp').find(x=>x.v.nome===V.grupo);
  const nat=g&&c6custo(g.v.nat)?g.v.nat:'Receita (sem natureza de custo)'; const cod=g?C6.natcod[g.v.nat]:'';
  const prox=V.sit==='Inativo'?{cor:'gray',t:'Inativo: fora dos planos e das cotações; saldo e histórico continuam no Estoque.'}
    :(S.res==='pre'?{cor:'yellow',t:'Sem preço de referência: o item fica pendente no custo do plano e na cotação.',prim:{t:'Informar preço',go:()=>g2editar(self,GR('g_itm'),r.id,'preco')}}
    :(S.res==='emb'?{cor:'yellow',t:'Sem embalagem: retirada e compra são em embalagens inteiras.',prim:{t:'Informar conteúdo da embalagem',go:()=>g2editar(self,GR('g_itm'),r.id,V.emb&&V.emb!=='Granel'?'cont':'emb')}}
    :{cor:'green',t:'Em dia: unidade, embalagem, controle e preço informados.'}));
  return {titulo:'Item · '+V.item,sub:V.grupo+' · '+(V.un||'sem unidade')+' · '+(V.sit||'Ativo'),prox:prox,sec:[{t:'Editar item',go:()=>g2editar(self,GR('g_itm'),r.id)}],
    blocos:[{t:'Unidade e embalagem',lin:[{l:'Unidade-base',v:(V.un||'—')+(V.trava?' · travada: '+V.trava:'')},{l:'Embalagem de entrega',v:e||'a informar',cor:e?'':'yellow'},
        {l:'Controle',v:V.ctrl||'—'},V.gar?{l:'Garantia ou densidade',v:V.gar}:null],nota:V.trava?'Travada: a dose dos planos e o estoque usam esta unidade. Troca só dentro da mesma grandeza e nunca reescreve lançamentos (B24).':'Troca só dentro da mesma grandeza (massa, volume ou contagem) e nunca reescreve lançamentos (B24).'},
      {t:'Preço',lin:[{l:'Preço de referência',v:isnum(V.preco)&&String(V.preco)!==''?'R$ '+nf(V.preco,2)+'/'+V.un:(V.custo?'sem preço':'não se aplica (receita)'),cor:(V.custo&&!isnum(V.preco))?'yellow':''},{l:'Data do preço',v:V.pdata?br(V.pdata):'—'}]},
      {t:'Locais',lin:[{l:'Local padrão',v:V.local||'a informar',cor:V.local?'':'yellow'}],
        tab:ls.length?{cols:['Lote','Local','Físico','Disponível','Validade'],rows:ls.map(x=>[x.lote,x.local,nf(x.fis)+' '+x.un,nf(x.livre)+' '+x.un,x.val])}:null,
        nota:ls.length?'Saldo e lotes vêm do Estoque (consulta; não se editam aqui).':(sd.fis?'Saldo de '+nf(sd.fis)+' '+V.un+' no Estoque.':'Sem saldo no Estoque.'),
        lks:[{t:'Abrir saldos e lotes',h:'EST.dc.html#sec=saldos&item='+encodeURIComponent(r.id)}]},
      {t:'Fornecedores do grupo',lin:[{l:'Homologados em '+V.grupo,v:fo.length?fo.map(x=>x.nome).join(', '):'nenhum'}],lks:[{t:'Abrir o grupo em Parceiros',h:'CD-05.dc.html#grp='+encodeURIComponent(V.grupo)}]},
      {t:'Registro e bula',nota:'Não cadastrado: lacuna L01, consulta ao AG-07 a definir. O protótipo não guarda registro nem bula do produto.'},
      {t:'Natureza de custo',lin:[{l:'Natureza (do grupo)',v:nat}],lks:cod?[{t:'Abrir na Estrutura gerencial',h:'CD-07.dc.html#dim=natureza&cod='+encodeURIComponent(cod)}]:[]}]}; }
function c6consGrp(self,g){ const G=g.v; const its=leaves(RW(self,'g_itm')).filter(r=>!/^GR/.test(r.id)&&r.v.grupo===G.nome); const fo=C6.forn[G.nome]||[]; const cod=C6.natcod[G.nat]||'';
  const ps=c6pends(self,g.id);
  return {titulo:'Grupo · '+G.nome,sub:(c6custo(G.nat)?G.nat:'Receita, sem natureza de custo')+' · '+its.length+(its.length===1?' item':' itens'),
    prox:ps.length?{cor:'yellow',t:ps[0].t,mais:ps.length>1?('e mais '+(ps.length-1)+'.'):''}:{cor:'green',t:'Em dia: itens com preço e embalagem.'},sec:[{t:'Editar grupo',go:()=>g2editar(self,GR('g_grp'),g.id)}],
    blocos:[{t:'Itens',fil:its.map(r=>{ const S=c6sit(r.v); return {t:r.v.item,sub:(r.v.un||'—')+(c6emb(r.v)?' · '+c6emb(r.v):''),chip:{t:S.t,c:S.res?'yellow':(S.t==='Inativo'?'gray':'green')},
        go:()=>{ g2set(self,'g_grp',{fm:null}); g2open(self,GR('g_itm'),r.id,null,{pai:{gid:'g_grp',rid:g.id,t:G.nome}}); }}; }),nota:its.length?'':'Nenhum item neste grupo.'},
      {t:'Natureza de custo',lin:[{l:'Natureza',v:c6custo(G.nat)?G.nat:'Receita'},{l:'Controle padrão dos itens',v:C6.ctrlg[G.nome]||'—'}],lks:cod?[{t:'Abrir na Estrutura gerencial',h:'CD-07.dc.html#dim=natureza&cod='+encodeURIComponent(cod)}]:[]},
      {t:'Fornecedores homologados',lin:[{l:'Recebem cotação',v:fo.length?fo.map(x=>x.nome).join(', '):'nenhum'}],lks:[{t:'Abrir o grupo em Parceiros',h:'CD-05.dc.html#grp='+encodeURIComponent(G.nome)}]}]}; }
function c6consLoc(self,l){ const V=l.v; const its=leaves(RW(self,'g_itm')).filter(r=>!/^GR/.test(r.id)&&r.v.local===V.nome);
  return {titulo:'Local · '+V.nome,sub:V.faz+' · '+V.tipo,prox:{cor:'green',t:its.length?(its.length+(its.length===1?' item usa':' itens usam')+' este local como padrão.'):'Nenhum item usa este local como padrão.'},
    sec:[{t:'Editar local',go:()=>g2editar(self,GR('g_loc'),l.id)}],
    blocos:[{t:'Local',lin:[{l:'Fazenda',v:V.faz},{l:'Tipo',v:V.tipo},{l:'Capacidade',v:V.tipo==='Tanque'&&isnum(V.cap)?nf(V.cap)+' L':(V.capa||'—')}]},
      {t:'Itens com este local padrão',fil:its.map(r=>({t:r.v.item,sub:r.v.grupo,go:()=>{ g2set(self,'g_loc',{fm:null}); g2open(self,GR('g_itm'),r.id,null,{pai:{gid:'g_loc',rid:l.id,t:V.nome}}); }})),nota:its.length?'':'Nenhum.'}]}; }
function c6cfg(self){ cmdIni(self,{gp:'grp',ip:{g_itm:'item',g_loc:'local'},grpPre:'GR',
  grupoDe:(s,gid,r)=>{ if(gid==='g_loc') return C6LOC; const sel=cmdSel(s); const g=RW(s,'g_grp').find(x=>x.v.nome===r.v.grupo); return (sel===''&&s.state.mx_sel!==undefined)?'':(g?g.id:''); },
  existeGrupo:(s,id)=>id===C6LOC||!!c6grp(s,id),
  normGrupo:(s,id)=>{ const g=RW(s,'g_grp').find(x=>x.id===id||x.v.nome===id); return g?g.id:id; },   /* #grp=Fungicidas (link do CD-05) = #grp=GR6 */
  reg:(s,id)=>leaves(RW(s,'g_itm')).some(r=>r.id===id&&!/^GR/.test(id))?{gid:'g_itm',rid:id}:(RW(s,'g_loc').some(r=>r.id===id)?{gid:'g_loc',rid:id}:(c6grp(s,id)?{grupo:id}:null)),
  indisp:(id,gid)=>cmdIndisp(gid==='g_loc'?'Local de estoque':'Item',id),
  indispGrupo:(id)=>'Grupo “'+id+'” indisponível: não existe neste cadastro ou não está liberado para o seu perfil.',
  inativo:(gid,r)=>(gid==='g_itm'&&r.v.sit==='Inativo')?{c6qf:'inat'}:null,
  novo:(s)=>{ if(s.__v&&s.__v.c6_criar) s.__v.c6_criar(); },
  anuncio:(s,id)=>{ if(id===C6LOC) return 'Locais de estoque: '+RW(s,'g_loc').length+' locais'; const g=c6grp(s,id); const n=leaves(RW(s,'g_itm')).filter(r=>!/^GR/.test(r.id)&&(!g||r.v.grupo===g.v.nome)).length; const p=c6pends(s,id).length;
    return (g?g.v.nome:'Todos os itens')+': '+n+(n===1?' item':' itens')+' · '+(p?p+' a resolver':'Em dia'); },
  cons:{g_itm:c6consItm,g_grp:c6consGrp,g_loc:c6consLoc}}); }
function PREVALS(self,v){ cadActsIni(self); c6cfg(self); cenOuvir(self); if(self.state.mx_q===undefined){ const k=cadKeepLe('q'); if(k) self.state.mx_q=k; }
  const grps=RW(self,'g_grp'); const its=[]; const locs=RW(self,'g_loc'); const sel=cmdSel(self); const gs=sel&&sel!==C6LOC?c6grp(self,sel):null; const q=self.state.mx_q||'';
  c6pais(self).forEach(p=>{ const g=grps.find(x=>x.id===p.id); if(!g) return; const G=g.v; const ks=p.kids||[]; p.v.item=G.nome;
    p.p.item=[{k:'b',t:G.nome},{k:'mut',t:ks.length+(ks.length===1?' item':' itens')}]; p.s.item=G.nome;
    ['est','un','embt','ctrl','preco','pdata'].forEach(k=>{ p.p[k]=[{k:'mut',t:''}]; p.s[k]=''; });
    ks.forEach(r=>{ const V=r.v; V.grupo=G.nome; V.custo=c6custo(G.nat); its.push(r);
      r.p.item=[{k:'b',t:V.item||''}]; r.s.item=V.item||'';
      const e=c6emb(V); r.p.un=[{k:'txt',t:V.un||'—'}]; r.s.un=V.un||''; r.p.embt=[e?{k:'txt',t:e}:{k:'mut',t:'—'}]; r.s.embt=e||'';
      r.p.ctrl=[{k:(V.ctrl==='Sem lote'?'mut':'txt'),t:V.ctrl||'—'}]; r.s.ctrl=V.ctrl||'';
      const pr=isnum(V.preco)&&String(V.preco)!==''; r.p.preco=pr?[{k:'txt',t:'R$ '+nf(V.preco,2)+'/'+V.un}]:[{k:'mut',t:'—'}]; r.s.preco=pr?'R$ '+nf(V.preco,2)+'/'+V.un:'';
      r.p.pdata=[pr&&V.pdata?{k:'txt',t:br(V.pdata)}:{k:'mut',t:'—'}]; r.s.pdata=pr&&V.pdata?br(V.pdata):'';
      const S=c6sit(V); r.p.est=S.p; r.s.est=S.t;
      const sd=c6saldo(V); V.trava=c6trava(V); r.nd=sd.fis>0?'com saldo':(V.plano?'em plano':''); }); });
  const ti=RW(self,'g_itm');
  // mestre → busca da tela (item, grupo, natureza; "Herbicidas" acha os itens do grupo) → filtro rápido
  cmdPasse(ti,'cadm_g_itm',r=>!gs||r.v.grupo===gs.v.nome);
  cmdPasse(ti,'cadb_g_itm',r=>cmdCasa([r.v.item,r.v.grupo,r.v.gar].join(' '),q),!!q);
  cmdQf(self,v,'g_itm','c6qf',[{k:'res',t:'A resolver',f:r=>!!c6sit(r.v).res},{k:'inat',t:'Inativos',f:r=>r.v.sit==='Inativo',oculta:true}],ti);
  if(gs){ const g=ti.find(x=>x.id===gs.id); G2DISP.g_itm=g?g.kids:[]; } else delete G2DISP.g_itm;
  GR('g_itm').cols[0]=Object.assign({},GR('g_itm').cols[0],{l:gs?'Item':'Grupo › item'});
  const f=(GR('g_itm').edit.fields||[]).find(x=>x.k==='grupo'); if(f) f.opts=grps.map(g=>g.v.nome).sort((a,b)=>a.localeCompare(b,'pt-BR')).concat([OUTRO_G]);
  const lf=(GR('g_itm').edit.fields||[]).find(x=>x.k==='local'); if(lf) lf.opts=locs.map(l=>l.v.nome);
  locs.forEach(r=>{ const V=r.v; const n=its.filter(i=>i.v.local===V.nome).length; V.itens=n; r.nd=n?'com itens':''; r.p.nome=[{k:'b',t:V.nome||''}]; r.s.nome=V.nome||'';
    const tq=V.tipo==='Tanque'&&isnum(V.cap)&&String(V.cap)!==''; const si=V.tipo==='Silo'&&isnum(V.capsc)&&String(V.capsc)!=='';
    V.capn=tq?Number(V.cap):(si?Number(V.capsc):''); const cap=tq?nf(V.cap)+' L':(si?nf(V.capsc)+' sc de 60 kg':'');
    r.p.capn=cap?[{k:'txt',t:cap}]:[{k:'mut',t:'—'}]; r.s.capn=cap; });
  cmdPasse(locs,'cadb_g_loc',r=>cmdCasa([r.v.nome,r.v.faz,r.v.tipo].join(' '),q)); }
function EXTRAVALS(self,v){ const its=leaves(RW(self,'g_itm')).filter(r=>!/^GR/.test(r.id)); const grps=RW(self,'g_grp'); const locs=RW(self,'g_loc'); const sel=cmdSel(self); const q=self.state.mx_q||''; const larga=cadLarga();
  const gs=sel&&sel!==C6LOC?c6grp(self,sel):null;
  // ---- mestre: Todos os itens · grupos · Locais de estoque ----
  const casa=(g)=>!q||g.id===sel||cmdCasa(g.v.nome,q)||its.some(r=>r.v.grupo===g.v.nome&&cmdCasa([r.v.item,r.v.gar].join(' '),q));
  const lst=grps.slice().sort((a,b)=>a.v.nome.localeCompare(b.v.nome,'pt-BR')).filter(casa).map(g=>{ const n=its.filter(r=>r.v.grupo===g.v.nome&&r.v.sit!=='Inativo').length; const p=c6pends(self,g.id).length;
    return {id:g.id,t:g.v.nome,n:String(n),sub:C6.ctrlg[g.v.nome]||'',res:p?p+' a resolver':'Em dia',cor:p?'yellow':'green'}; });
  lst.push({tit:true,t:'Onde fica'}); lst.push({id:C6LOC,t:'Locais de estoque',n:String(locs.length),sub:'almoxarifados, galpões, tanques e silos',res:'',cor:''});
  cadMestreVals(self,v,{todos:{t:'Todos os itens',sub:its.filter(r=>r.v.sit!=='Inativo').length+' itens'},itens:lst,sel:sel,inatN:0,escolhe:id=>cmdEscolhe(self,id)});
  const rs=[]; if(q&&!larga){ its.filter(r=>r.v.sit!=='Inativo'&&cmdCasa([r.v.item,r.v.grupo].join(' '),q)).forEach(r=>{ const g=grps.find(x=>x.v.nome===r.v.grupo); rs.push({t:r.v.item+' · '+r.v.grupo,sub:'Item · '+(r.v.un||'—'),go:()=>cmdAbre(self,'g_itm',r.id,g?g.id:'')}); }); }
  cadResVals(v,rs); v.c6_ngrp=()=>g2new(self,GR('g_grp'));
  // ---- detalhe ----
  const av=cmdAviso(self,'Ver todos os itens'); v.c6_itm_on=sel!==C6LOC; v.c6_loc_on=sel===C6LOC;
  if(sel===C6LOC) cadDetVals(self,v,Object.assign({t:'Locais de estoque',sub:locs.length+' locais em '+[...new Set(locs.map(l=>l.v.faz))].length+' fazendas · o saldo de cada local fica no Estoque',chip:{t:'Em dia',c:'green'},
      prox:null,lks:[{t:'Abrir saldos no Estoque',h:'EST.dc.html#sec=saldos'}],volta:'Grupos',voltar:()=>cmdVolta(self)},av));
  else if(gs){ const G=gs.v; const ps=c6pends(self,gs.id); const n=its.filter(r=>r.v.grupo===G.nome&&r.v.sit!=='Inativo').length; const cod=C6.natcod[G.nat]||'';
    cadDetVals(self,v,Object.assign({t:G.nome,sub:'Natureza de custo: '+(c6custo(G.nat)?G.nat:'receita, sem natureza de custo')+' · controle '+(C6.ctrlg[G.nome]||'—').toLowerCase()+' · '+n+(n===1?' item':' itens'),
      chip:ps.length?{t:ps.length+' a resolver',c:'yellow'}:{t:'Em dia',c:'green'},ficha:{t:'Ver ficha do grupo',go:()=>g2open(self,GR('g_grp'),gs.id,null)},
      lks:cod?[{t:'Natureza na Estrutura gerencial',h:'CD-07.dc.html#dim=natureza&cod='+encodeURIComponent(cod)}]:[],prox:c6prox(ps),volta:'Grupos',voltar:()=>cmdVolta(self)},av)); }
  else { const ps=c6pends(self,''); cadDetVals(self,v,Object.assign({t:'Todos os itens',sub:its.length+' itens em '+grps.length+' grupos · a natureza de custo fica no cabeçalho de cada grupo',
      chip:ps.length?{t:ps.length+' a resolver',c:'yellow'}:{t:'Em dia',c:'green'},prox:c6prox(ps),volta:'Grupos',voltar:()=>cmdVolta(self)},av)); }
  // "+ Criar item": herda o grupo; controle pelo grupo, visível; unidade, embalagem e local vazios (R14). Em Locais de estoque, "+ Criar local"
  v.cab_criar_on=true; v.cab_criarT=sel===C6LOC?'+ Criar local':'+ Criar item';
  v.c6_criar=()=>{ if(sel===C6LOC){ g2new(self,GR('g_loc')); return; } g2set(self,'g_itm',{fm:null}); g2new(self,GR('g_itm'),{draft:c6novoDraft(gs?gs.v.nome:'')});
    setTimeout(()=>{ try{ const x=document.getElementById('fx_g_itm_item'); if(x) x.focus(); }catch(z){} },90); };
  const semP=its.filter(r=>r.v.sit!=='Inativo'&&r.v.custo&&!isnum(r.v.preco)).length, semE=its.filter(r=>r.v.sit!=='Inativo'&&!c6emb(r.v)).length;
  cadEstado(v,'c6e',[semP?semP+(semP>1?' itens':' item')+' sem preço':'',semE?semE+(semE>1?' itens':' item')+' sem embalagem':''].filter(Boolean).join(' · ')||'Cadastro completo',(semP||semE)?'yellow':'green');
  cadQfPos(self,v,'g_itm','c6qf'); const ct=cmdConta(self,'g_itm',RW(self,'g_itm')); v.c6_conta=ct.n+' de '+ct.tot; const cl=cmdConta(self,'g_loc',locs); v.c6_contaLoc=cl.n+' de '+cl.tot;
  const vz=sel===C6LOC?(!cl.n?{t:q?'Nenhum local encontrado para “'+q+'”.':'Nenhum local. Crie o 1º em + Criar local, no topo.'}:null)
    :(!ct.n?(q?{t:'Nenhum item encontrado para “'+q+'”. Para cadastrar, use + Criar item, no topo.'}:(ct.tot?{t:'Nenhum item com este filtro.',go:{t:'Mostrar todos',fn:()=>self.setState({c6qf:''})}}:{t:'O grupo '+(gs?gs.v.nome:'')+' não tem item. Crie o 1º em + Criar item, no topo.'})):null);
  cadVazioSe(self,v,'c6_v',vz,['g_itm','g_loc']);
  // linha do grupo na árvore ("Todos"): escolhe o grupo
  (v.g_itm_rows||[]).forEach(x=>{ if(/^GR/.test(String(x.id))){ const gid=x.id; x.cls='g2r g2ed'; x.tab='-1'; x.open=(e)=>{ if(e&&e.target&&e.target.closest&&e.target.closest('button')) return; cmdEscolhe(self,gid); }; x.key=()=>{};
    const c0=x.cells.find(c=>c.isData); if(c0&&c0.parts[0]) c0.parts[0]=g2part({k:'act',alvo:true,t:c0.parts[0].t,al:'Abrir grupo '+c0.parts[0].t,go:()=>cmdEscolhe(self,gid)},v); } });
  // ---- formulário do item: unidade-base travada ou só na mesma grandeza (B24); conteúdo some no granel; local pedido em defensivos ----
  const F=v.g_itm_F; const fm=g2st(self,'g_itm').fm;
  if(F&&F.open&&F.fields&&fm){ const r=fm.rid?its.find(x=>x.id===fm.rid):null; const d=fm.draft; const un=d.un||'';
    F.fields=F.fields.filter(f=>!(f.fid==='fx_g_itm_cont'&&d.emb==='Granel'));
    F.fields.forEach(f=>{ const k=f.fid.replace('fx_g_itm_','');
      if(k==='un'&&r&&!fm.ro){ if(r.v.trava){ f.dis=true; f.ist=f.ist.replace('background:#FFFFFF','background:#F4F6F3'); f.help='Travada: '+r.v.trava+'. A dose dos planos e o estoque usam esta unidade.'; f.hasHelp=true; }
        else { const gr=C6.grand[r.v.un]; f.opts=f.opts.filter(o=>!o.v||!gr||C6.grand[o.v]===gr); f.help='Troca só dentro da mesma grandeza ('+gr+'); lançamentos antigos não mudam.'; f.hasHelp=true; } }
      if(k==='cont'){ f.u=un; f.hasU=!!un; }
      if(k==='preco'){ f.u=un?'R$/'+un:'R$'; f.hasU=true; }
      if(k==='local'&&c6defens(self,d.grupo,d.nnat)){ f.l='Local padrão (defensivo)'; f.help='Defensivo pede o almoxarifado próprio (NR-31): escolha o local.'; f.hasHelp=true; }
      // na criação, escolher o grupo traz o controle dele (R14: "Controle com o valor do grupo"); a pessoa pode trocar depois
      if(k==='grupo'&&fm.isNew&&!f.dis) f.set=(e)=>{ const cur=g2st(self,'g_itm').fm; if(!cur) return; const g=e.target.value; const dd=Object.assign({},cur.draft,{grupo:g});
        const prev=c6ctrlPad(cur.draft); const nv=c6ctrlPad(dd); if(nv&&(!cur.draft.ctrl||cur.draft.ctrl===prev)) dd.ctrl=nv; const er=Object.assign({},cur.errs||{}); delete er.grupo; delete er.ctrl;
        g2set(self,'g_itm',{fm:Object.assign({},cur,{draft:dd,errs:er,warn:false})}); };
      // "Outro grupo…": a natureza escolhida decide se é defensivo (local próprio, NR-31) e traz o controle padrão dele (achado 6 da revisão)
      if(k==='nnat'&&fm.isNew&&!f.dis) f.set=(e)=>{ const cur=g2st(self,'g_itm').fm; if(!cur) return; const dd=Object.assign({},cur.draft,{nnat:e.target.value});
        const prev=c6ctrlPad(cur.draft); const nv=c6ctrlPad(dd); if(nv&&(!cur.draft.ctrl||cur.draft.ctrl===prev)) dd.ctrl=nv; const er=Object.assign({},cur.errs||{}); delete er.nnat; delete er.local;
        g2set(self,'g_itm',{fm:Object.assign({},cur,{draft:dd,errs:er,warn:false})}); }; }); }
  valida(self,v,'g_itm',(d,fm)=>{ const e={}; const dup=unico(self,'g_itm',fm,r=>String(r.v.item).toLowerCase(),d.item); if(dup) e.item='Já existe o item '+d.item+' em '+dup.v.grupo+'.';
    if(d.grupo===OUTRO_G){ const n=String(d.ngrupo||'').trim(); if(n&&RW(self,'g_grp').some(g=>g.v.nome.toLowerCase()===n.toLowerCase())) e.ngrupo=n+' já existe; escolha na lista Grupo.'; }
    if(d.emb&&d.emb!=='Granel'&&!(g2num(d.cont)>0)) e.cont='Informe quanto cabe em 1 '+String(d.emb||'embalagem').toLowerCase()+' (em '+(d.un||'unidade-base')+').';
    if(String(d.preco||'').trim()&&!d.pdata) e.pdata='Informe a data do preço.';
    if(d.grupo&&d.grupo!==OUTRO_G&&!RW(self,'g_grp').some(g=>g.v.nome===d.grupo)) e.grupo='Escolha o grupo.';
    if(d.local&&!RW(self,'g_loc').some(l=>l.v.nome===d.local)) e.local='Escolha um local cadastrado.';
    if(!d.local&&c6defens(self,d.grupo,d.nnat)) e.local='Defensivo pede o local padrão (almoxarifado próprio, NR-31).';
    const o=fm.rid?its.find(x=>x.id===fm.rid):null; if(o){ const m=c6unTroca(o.v.un,d.un,o.v.trava); if(m) e.un=m; }
    return e; });
  valida(self,v,'g_grp',(d,fm)=>{ const e={}; const og=fm.rid?RW(self,'g_grp').find(g=>g.id===fm.rid):null; self.__c6gold=og?{id:og.id,nome:og.v.nome}:null; const n=String(d.nome||'').trim().toLowerCase(); if(RW(self,'g_grp').some(g=>g.id!==fm.rid&&g.v.nome.toLowerCase()===n)) e.nome='Já existe o grupo '+d.nome+'.'; return e; });
  valida(self,v,'g_loc',(d,fm)=>{ const e={}; const o=fm.rid?RW(self,'g_loc').find(l=>l.id===fm.rid):null; self.__c6old=o?{id:o.id,nome:o.v.nome}:null; const dup=unico(self,'g_loc',fm,r=>String(r.v.nome).toLowerCase(),d.nome); if(dup) e.nome='Já existe o local '+d.nome+'.'; return e; });
  ['g_itm','g_grp','g_loc'].forEach(g=>cadcEscolha(v,g));
  self.g2after=(gid,rows,r,isNew)=>{ if(!r) return;
    if(gid==='g_grp'){ const og=self.__c6gold; if(!isNew&&og&&og.id===r.id&&og.nome!==r.v.nome&&C6.ctrlg[og.nome]&&!C6.ctrlg[r.v.nome]) C6.ctrlg[r.v.nome]=C6.ctrlg[og.nome];   // renomear leva o controle padrão do grupo
      if(isNew){ const it=g2clone(RW(self,'g_itm')); it.push({id:r.id.indexOf('GR')===0?r.id:('GR'+r.id),v:{item:r.v.nome},s:{},p:{},kids:[]}); g2set(self,'g_itm',{rows:it}); }
      self.setState({g2toast:'Salvo: grupo '+r.v.nome+' · '+(c6custo(r.v.nat)?'custo dos itens vai para '+r.v.nat:'receita, sem natureza de custo')+'.'}); return; }
    if(gid==='g_loc'){ const o=self.__c6old; let n=0;
      if(!isNew&&o&&o.id===r.id&&o.nome!==r.v.nome){ const it=g2clone(RW(self,'g_itm')); leaves(it).forEach(x=>{ if(x.v.local===o.nome){ x.v.local=r.v.nome; n++; } }); if(n) g2set(self,'g_itm',{rows:it}); }
      self.setState({g2toast:'Salvo: '+r.v.nome+' · '+r.v.faz+' · '+r.v.tipo+(n?' · '+n+(n>1?' itens passam':' item passa')+' a usar este local padrão':'')+'. O recebimento no Estoque passa a oferecer este local.'}); return; }
    if(gid!=='g_itm') return;
    if(r.v.emb==='Granel') r.v.cont='';
    const grps2=g2clone(RW(self,'g_grp')); let g; const msg=[];
    if(r.v.grupo===OUTRO_G){ const nm=String(r.v.ngrupo).trim(); g={id:'GR'+(grps2.length+1)+'_'+String(Date.now()).slice(-4),v:{nome:nm,nat:r.v.nnat||C6.receita},s:{},p:{}};
      const cp=c6ctrlPad({grupo:OUTRO_G,nnat:g.v.nat}); if(cp||r.v.ctrl) C6.ctrlg[nm]=cp||r.v.ctrl;   /* o grupo novo de defensivos nasce com "Lote e validade" */
      grps2.push(g); g2set(self,'g_grp',{rows:grps2}); rows.push({id:g.id,v:{item:nm},s:{},p:{},kids:[]}); msg.push('grupo '+nm+' criado ('+g.v.nat+')'); }
    else g=grps2.find(x=>x.v.nome===r.v.grupo);
    if(!g) return;
    r.v.grupo=g.v.nome; r.v.ngrupo='';
    const par=rows.find(p=>p.id===g.id); const cur=rows.find(p=>(p.kids||[]).some(k=>k.id===r.id));
    if(cur!==par){ c6rm(rows,r.id); par.kids=par.kids||[]; par.kids.push(r); }
    const x=Object.assign({},g2st(self,'g_itm').x||GR('g_itm').x0||{}); x[par.id]=true; g2set(self,'g_itm',{rows:rows,x:x,fl:r.id});
    const e=c6emb(r.v); msg.push(r.v.un+(e?' · '+e:'')); msg.push(isnum(r.v.preco)?'R$ '+nf(r.v.preco,2)+'/'+r.v.un+' em '+br(r.v.pdata):'sem preço de referência');
    if(r.v.sit==='Inativo'){ const sd=c6saldo(r.v); msg.push('inativo: sai dos planos e das cotações'+(sd.fis?'; o saldo de '+nf(sd.fis)+' '+r.v.un+' segue no Estoque':'')); }
    self.setState({g2toast:(isNew?'Criado: ':'Salvo: ')+r.v.item+' · '+msg.join(' · ')+'.'}); }; }
// criação mínima sem padrão escondido (regra 6, R14): o grupo herdado traz o controle dele, visível; unidade, embalagem, conteúdo e local nascem vazios
// defensivo pela natureza do grupo (3.1.02 · Defensivos), não pelo nome: renomear o grupo não tira a exigência do local próprio (NR-31)
// com "Outro grupo…", vale a natureza escolhida para o grupo novo (nnat): defensivo criado assim também pede o almoxarifado próprio (achado 6)
function c6defens(self,grupo,nnat){ if(grupo===OUTRO_G) return C6.natcod[nnat]==='3.1.02'; const g=RW(self,'g_grp').find(x=>x.v.nome===grupo); return g?(C6.natcod[g.v.nat]==='3.1.02'):(C6.defens.indexOf(grupo)>=0); }
// controle padrão do grupo (o do cadastro) ou, no grupo novo, o da natureza: defensivo nasce "Lote e validade", como os grupos de defensivos de hoje
function c6ctrlPad(d){ if(d.grupo===OUTRO_G) return C6.natcod[d.nnat]==='3.1.02'?'Lote e validade':''; return C6.ctrlg[d.grupo]||''; }
function c6novoDraft(grupo){ return {grupo:grupo||'',ctrl:(grupo&&C6.ctrlg[grupo])||'',un:'',emb:'',cont:'',local:''}; }
'''

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

def _slug(s):
    import unicodedata, re
    s=unicodedata.normalize('NFD',s).encode('ascii','ignore').decode().lower()
    return re.sub('[^a-z0-9]+','-',s).strip('-')
DIM_SLUG={d:_slug(d) for d in DC.DIMS}

def cd07():
    # CADUX P8 (09/10/2026): mestre com as 7 dimensões → árvore Código › subcódigo da dimensão → painel do código em consulta (vigência, superior,
    # rateio, tradução ERP, onde é usado, versões). O Próximo passo da tela ("Publicar estrutura v6 (3 alterações)") fica fixo no topo do
    # detalhe; o painel só tem "Traduzir no ERP". "+ Criar código" no cabeçalho, menos em Cultura e Processo (a fonte é o CD-02, R15).
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
    def aninha(lst):   # código › subcódigo dentro da dimensão (3.1 → 3.1.01 …)
        by={r['v']['cod']:r for r in lst}; top=[]
        for r in lst:
            pai=by.get(r['v']['sup']) if r['v']['sup'] else None
            if pai is not None and pai is not r: pai.setdefault('kids',[]).append(r)
            else: top.append(r)
        return top
    tree=[dict(id=f'DM{i}',ro=True,nosel=True,v=dict(cod=d),s={},p={},kids=aninha(kids[d])) for i,d in enumerate(DC.DIMS,1)]
    x0={r['id']:True for r in tree}
    for d in DC.DIMS:
        for r in kids[d]:
            if r.get('kids'): x0[r['id']]=True
    # Código › subcódigo | Nome | Situação | Início da vigência | Conta no ERP | No rascunho (o resto da ficha fica no painel)
    g=grid([dict(k='cod',l='Código › subcódigo',w=190),dict(k='nome',l='Nome',w=240),dict(k='est',l='Situação',w=170),dict(k='ini',l='Início da vigência',t='date'),
            dict(k='conta',l='Conta no ERP',w=150),dict(k='rasc',l='No rascunho',w=110)],
        tree,gid='g_dim',tree=True,dele=False,total=False,frame=False,search=False,x0=x0,
        tools=f'<span class="cmd-conta">{H("c7_conta")}</span>'+qf_chips('g_dim')+secbtn('c7imp','Importar do ERP','Simulação: mostra a prévia antes de trazer qualquer código'),
        edit=dict(m='form',title='Código',newTitle='Criar código',alvo='código',
            sub='Altere o código e a tradução. A mudança entra no rascunho e vale para novos lançamentos depois de publicada; fatos já gravados mantêm as dimensões da época.',
            fields=[txt('cod','Código'),txt('nome','Nome'),sel('dim','Dimensão',DIMS_MANUAIS,help='Cada código em uma dimensão: nunca combine fazenda, cultura e processo num único centro.'),
                    sel('sup','Código superior',[''],req=False,help='Soma no total do superior (ex.: 3.1.01 em 3.1).'),
                    sel('rat','Direcionador de rateio',DC.RATEIO,cond=cond('dim','Centro de responsabilidade'),help='Como o custo deste centro chega às culturas, em vez de ratear tudo por hectare.'),
                    dict(k='grp',l='Grupos de insumo',ro=True,cond=cond('dim','Natureza'),help='Vêm de Produtos, unidades e locais; troque a natureza no grupo.'),
                    dict(k='ops',l='Operações',ro=True,cond=cond('dim','Processo'),help='Vêm de Culturas, cultivares e operações; troque o processo na operação.'),
                    dat('ini','Início da vigência'),dat('fim','Fim da vigência',req=False,help='Deixe em branco se não houver fim previsto.'),
                    sel('trad','Tradução no ERP',TRAD,**{'def':'Conta do ERP'},help='Dimensão própria segue no lançamento e é traduzida pela integração, sem conta fixa.'),
                    txt('conta','Conta ou centro no ERP',req=False,cond=cond('trad','Conta do ERP'),help='Em branco, o código fica fora da publicação até ser mapeado. Exemplo: pulverização na soja do T1 = empresa 01 + natureza 3.1.02 + CR-SR + cultura SOJA + processo TRAT + talhão T1 → conta 4.1.1.02 · TOP 1201.'),
                    txt('top','Tipo de operação (TOP) no ERP',req=False,cond=cond('trad','Conta do ERP'))]))
    acoes_form('g_dim'); cadx_css(); md_css()
    det=det_cab()+f'<div class="cadx-dados">'+vazio('c7_v')+f'<div style="padding: 0 16px;">{_imp_html()}</div>'+arv(g)+'</div>'
    corpo=md(mestre('Dimensões','Buscar código, nome ou conta'),det,'Estrutura gerencial')
    ops=[]
    for c in D2.CONJ:
        if c['op'] not in ops: ops.append(c['op'])
    dados=json.dumps(dict(ver=VERSAO,mud=V6_MUD,imp=IMP,dims=DC.DIMS,slug=DIM_SLUG,manuais=DIMS_MANUAIS,
                          cul={c:f'CU{j}' for j,(n,c,*_) in enumerate(DC.CULTURAS,1)},op={o:f'OP{i}' for i,o in enumerate(ops,1)}),ensure_ascii=False)
    js({},CADC_JS+f"const C7={dados};\n"+CD07JS)
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a árvore rola
    shell37('CD-07','Estrutura gerencial',corpo,fname=fname,status=None,primary_html=criar_cab('c7_criar','+ Criar código'),search=False)
    estado_cab(fname,'Estrutura gerencial','c7e')
CD07JS=r'''
function c7rm(list,id){ const i=list.findIndex(x=>x.id===id); if(i>=0){ list.splice(i,1); return true; } return list.some(x=>x.kids&&c7rm(x.kids,id)); }
function c7ver(self){ return self.state.c7ver||C7.ver; }
function c7mud(self){ return self.state.c7mud||C7.mud; }
// todos os códigos da árvore, também os que têm subcódigo (3.1); a linha da dimensão não é código
function c7todos(rows){ const o=[]; const w=l=>l.forEach(r=>{ if(r.v&&r.v.dim) o.push(r); if(Array.isArray(r.kids)) w(r.kids); }); w(rows); return o; }
function c7cods(self){ return c7todos(RW(self,'g_dim')); }
function c7dimDe(sl){ return Object.keys(C7.slug).find(d=>C7.slug[d]===sl)||''; }
function c7dm(rows,dim){ return rows.find(p=>!p.v.dim&&p.v.cod===dim); }
// código excluído no rascunho continua na tabela até publicar, mas já não conta como vigente para a próxima versão
function c7vivos(self){ const m=c7mud(self); return c7cods(self).filter(r=>m[r.id]!=='excluído'); }
function c7pend(self,dim){ return c7vivos(self).filter(r=>r.v.trad!=='Dimensão própria'&&!r.v.conta&&(!dim||r.v.dim===dim)); }
// põe o código no lugar da árvore: sob o superior da mesma dimensão ou na raiz da dimensão (o subcódigo vai junto)
function c7poe(rows,r){ c7rm(rows,r.id); const pai=r.v.sup?c7todos(rows).find(x=>x.v.dim===r.v.dim&&x.v.cod===r.v.sup&&x.id!==r.id):null; const dm=c7dm(rows,r.v.dim);
  const alvo=pai||dm; if(!alvo) return null; alvo.kids=alvo.kids||[]; alvo.kids.push(r); return alvo; }
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
// situação do código (sem verbo na célula, BOT-07): sai na próxima versão, tradução pendente, mapeado ou dimensão própria
function c7sit(self,r){ const V=r.v; const m=c7mud(self)[r.id]; const prop=V.trad==='Dimensão própria';
  if(m==='excluído'){ const t='Sai na v'+(c7ver(self)+1); return {t,p:[chipc(t,'gray')]}; }
  if(!prop&&!V.conta) return {t:'Tradução pendente',p:sitX('Tradução pendente','yellow'),res:true};
  return {t:prop?'Dimensão própria':'Mapeado',p:(prop?sitInfo('Dimensão própria'):sitOk('Mapeado'))}; }
const C7_ND={'com lançamentos':'tem lançamentos; encerre a vigência em vez de excluir','usada em grupos':'é a natureza de grupos de insumo em Produtos; troque lá antes',
  'vem de Culturas':'vem de Culturas, cultivares e operações; exclua lá','vem de Operações':'vem de Culturas, cultivares e operações; exclua lá'};
CAD_ACTS.g_dim=(self,r,fm)=>{ if(!r.v.dim||r.ro||fm.ro) return []; const sub=(r.kids||[]).length;
  return [cadExcluir(self,'g_dim',r,'código',sub?('tem '+sub+(sub===1?' subcódigo':' subcódigos')+'; exclua ou mova os subcódigos antes'):(C7_ND[r.nd]||r.nd||''),()=>c7excluir(self,r.id))]; };
function c7abreCod(self,id,o){ g2open(self,GR('g_dim'),id,null,o||null); }
// painel do código em consulta: vigência, estrutura (superior e subcódigos), rateio, tradução, onde é usado e versões; o verde só em "Traduzir no ERP"
function c7consCod(self,r){ const V=r.v; const S=c7sit(self,r); const m=c7mud(self)[r.id]; const ver=c7ver(self); const prop=V.trad==='Dimensão própria'; const orig=!!V.orig;
  const sup=V.sup?c7cods(self).find(x=>x.v.dim===V.dim&&x.v.cod===V.sup):null; const subs=(r.kids||[]).filter(k=>k.v&&k.v.dim);
  const uso=[];
  if(V.dim==='Natureza') uso.push({t:'Onde é usado',lin:[{l:'Grupos de insumo',v:V.grp||'nenhum grupo'}],lks:String(V.grp||'').split(', ').filter(Boolean).map(gn=>({t:'Abrir '+gn+' em Produtos',h:'CD-06.dc.html#grp='+encodeURIComponent(gn)})),nota:'A natureza se troca no grupo, em Produtos, unidades e locais.'});
  if(V.dim==='Cultura') uso.push({t:'Onde é usado',lin:[{l:'Cultivares',v:String(V.cvs||0)}],lks:C7.cul[V.cod]?[{t:'Abrir '+V.nome+' em Culturas',h:'CD-02.dc.html#cul='+C7.cul[V.cod]}]:[]});
  if(V.dim==='Processo') uso.push({t:'Onde é usado',lin:[{l:'Operações',v:V.ops||'nenhuma operação'}],lks:String(V.ops||'').split(', ').filter(o=>C7.op[o]).map(o=>({t:'Abrir '+o+' em Operações',h:'CD-02.dc.html#aba=operacoes&op='+C7.op[o]}))});
  return {titulo:'Código · '+V.cod+' '+V.nome,sub:V.dim+' · '+S.t+(orig?' · vem do CD-02: aqui só a tradução':''),
    prox:m==='excluído'?{cor:'gray',t:'Excluído no rascunho v'+(ver+1)+': sai da estrutura na publicação; até lá, só consulta.'}
      :(S.res?{cor:'yellow',t:'Sem conta no ERP: fica fora da publicação até ser traduzido.',prim:{t:'Traduzir no ERP',go:()=>g2editar(self,GR('g_dim'),r.id,'conta')}}
      :{cor:'green',t:prop?'Dimensão própria: segue no lançamento e é traduzida na integração.':('Mapeado: '+V.conta+(V.top?' · TOP '+V.top:'')+'.')}),
    sec:m==='excluído'?[]:[{t:orig?'Editar tradução':'Editar código',go:()=>g2editar(self,GR('g_dim'),r.id)}],
    blocos:[{t:'Vigência',lin:[{l:'Início',v:V.ini?br(V.ini):'—'},{l:'Fim',v:V.fim?br(V.fim):'sem fim previsto'}]},
      {t:'Estrutura',lin:[{l:'Dimensão',v:V.dim},{l:'Superior',v:sup?(sup.v.cod+' · '+sup.v.nome):'nenhum (código de topo)'},V.dim==='Centro de responsabilidade'?{l:'Direcionador de rateio',v:V.rat||'—'}:null],
        fil:subs.map(k=>({t:k.v.cod+' · '+k.v.nome,sub:c7sit(self,k).t,al:'Abrir subcódigo '+k.v.cod,go:()=>c7abreCod(self,k.id,{pai:{gid:'g_dim',rid:r.id,t:V.cod}})})),
        lks:sup?[{t:'Abrir superior '+sup.v.cod,go:()=>c7abreCod(self,sup.id)}]:[]},
      {t:'Tradução no ERP',lin:[{l:'Tradução',v:V.trad},prop?null:{l:'Conta ou centro',v:V.conta||'sem conta'},prop?null:{l:'TOP',v:V.top||'—'}]}]
      .concat(uso).concat([{t:'Versões',lin:[{l:'Em vigor',v:'v'+ver},{l:'Rascunho v'+(ver+1),v:m?(m.charAt(0).toUpperCase()+m.slice(1)):'sem alteração'}],nota:'Fatos já gravados mantêm as dimensões da época.'}])}; }
function c7cfg(self){ cmdIni(self,{gp:'dim',ip:{g_dim:'cod'},endSempre:true,
  // cod= é o código (3.1.02), como o link do CD-06 já usa; o id interno também é aceito
  normItem:(gid,x,s,o)=>{ const cs=c7cods(s); const dim=o&&o.dim?c7dimDe(o.dim):''; const r=cs.find(c=>c.id===x)||cs.find(c=>c.v.cod===x&&(!dim||c.v.dim===dim))||cs.find(c=>c.v.cod===x); return r?r.id:x; },
  endItem:(s,gid,rid)=>{ const r=g2find(RW(s,'g_dim'),rid); return (r&&r.v.cod)||rid; },
  grupoDe:(s,gid,r)=>C7.slug[r.v.dim]||'',
  existeGrupo:(s,id)=>!!c7dimDe(id),
  grupoLinha:(gid,r)=>!(r.v&&r.v.dim),
  reg:(s,id)=>{ const r=c7cods(s).find(c=>c.id===id||c.v.cod===id); return r?{gid:'g_dim',rid:r.id}:null; },
  indisp:(id)=>'Código “'+id+'” indisponível: não existe nesta estrutura ou não está liberado para o seu perfil. Nada foi aberto.',
  indispGrupo:(id)=>'Dimensão “'+id+'” não existe na Estrutura gerencial. Nada foi aberto.',
  novo:(s)=>{ if(s.__v&&s.__v.c7_criar) s.__v.c7_criar(); return null; },
  anuncio:(s,id)=>{ const d=c7dimDe(id); const n=c7vivos(s).filter(r=>!d||r.v.dim===d).length; const p=c7pend(s,d).length; return (d||'Todas as dimensões')+': '+n+(n===1?' código':' códigos')+' · '+(p?p+' a resolver':'Em dia'); },
  cons:{g_dim:c7consCod}}); }
function PREVALS(self,v){ cadActsIni(self); c7cfg(self); if(self.state.mx_q===undefined){ const k=cadKeepLe('q'); if(k) self.state.mx_q=k; }
  const mud=c7mud(self); const rows=RW(self,'g_dim'); const cods=c7cods(self); const viv=c7vivos(self); const sel=cmdSel(self); const dim=c7dimDe(sel); const q=self.state.mx_q||'';
  cods.forEach(r=>{ if(mud[r.id]==='excluído') r.ro=true; });
  rows.forEach(p=>{ const n=viv.filter(r=>r.v.dim===p.v.cod).length;
    p.p.cod=[{k:'b',t:p.v.cod},{k:'mut',t:n+(n===1?' código':' códigos')}]; p.s.cod=p.v.cod;
    ['nome','est','ini','conta','rasc'].forEach(k=>{ p.p[k]=[{k:'mut',t:''}]; p.s[k]=''; }); });
  cods.forEach(r=>{ const V=r.v; const prop=V.trad==='Dimensão própria';
    r.p.cod=[{k:(r.kids||[]).length?'b':'txt',t:V.cod||''}]; r.s.cod=V.cod||''; r.p.nome=[{k:'txt',t:V.nome||''}]; r.s.nome=V.nome||'';
    r.p.ini=[V.ini?{k:'txt',t:br(V.ini)}:{k:'mut',t:'—'}]; r.s.ini=V.ini?br(V.ini):'';
    r.p.conta=[!prop&&V.conta?{k:'txt',t:V.conta}:{k:'mut',t:'—'}]; r.s.conta=!prop&&V.conta?V.conta:'';
    const S=c7sit(self,r); r.p.est=S.p; r.s.est=S.t;
    const m=mud[r.id]; const mt=m?m.charAt(0).toUpperCase()+m.slice(1):''; r.p.rasc=[m?chipc(mt,'gray'):{k:'mut',t:'—'}]; r.s.rasc=mt; });
  // mestre → recorte da árvore; busca da tela (código, nome, conta, TOP e a dimensão); filtro rápido
  cmdPasse(rows,'cadm_g_dim',r=>!dim||r.v.dim===dim,false,c7todos);
  cmdPasse(rows,'cadb_g_dim',r=>cmdCasa([r.v.cod,r.v.nome,r.v.conta,r.v.top,r.v.dim].join(' '),q),!!q,c7todos);
  const nv=c7ver(self)+1;
  cmdQf(self,v,'g_dim','c7qf',[{k:'alt',t:'No rascunho v'+nv,f:r=>!!mud[r.id]},{k:'res',t:'A resolver',f:r=>!!c7sit(self,r).res}],rows,c7todos);
  if(dim){ const g=c7dm(rows,dim); G2DISP.g_dim=g?(g.kids||[]):[]; } else delete G2DISP.g_dim;
  GR('g_dim').cols[0]=Object.assign({},GR('g_dim').cols[0],{l:dim?'Código › subcódigo':'Dimensão › código'}); }
function EXTRAVALS(self,v){ const ver=c7ver(self), mud=c7mud(self), n=Object.keys(mud).length; const pl=c7pend(self); const pend=pl.length;
  const sel=cmdSel(self); const dim=c7dimDe(sel); const q=self.state.mx_q||''; const larga=cadLarga(); const viv=c7vivos(self);
  cadEstado(v,'c7e','v'+ver+' em vigor'+(n?' · rascunho v'+(ver+1)+' com '+n+(n===1?' alteração':' alterações'):'')+(pend?' · '+pend+(pend===1?' tradução pendente':' traduções pendentes'):''),(n||pend)?'yellow':'green');
  // ---- mestre: as 7 dimensões (categorias fixas, sem ficha, C26) ----
  const casa=(r)=>cmdCasa([r.v.cod,r.v.nome,r.v.conta,r.v.top,r.v.dim].join(' '),q);
  const its=C7.dims.filter(d=>!q||C7.slug[d]===sel||cmdCasa(d,q)||viv.some(r=>r.v.dim===d&&casa(r))).map(d=>{ const k=viv.filter(r=>r.v.dim===d).length; const p=c7pend(self,d).length;
    const md=Object.keys(mud).filter(id=>{ const r=g2find(RW(self,'g_dim'),id); return r&&r.v.dim===d; }).length;
    return {id:C7.slug[d],t:d,n:String(k),sub:(C7.manuais.indexOf(d)<0?'do CD-02: só a tradução':(d==='Centro de responsabilidade'?'com direcionador de rateio':''))+(md?((C7.manuais.indexOf(d)<0||d==='Centro de responsabilidade')?' · ':'')+md+' no rascunho':''),
      res:p?p+' a resolver':'Em dia',cor:p?'yellow':'green'}; });
  cadMestreVals(self,v,{todos:{t:'Todas as dimensões',sub:viv.length+' códigos · v'+ver+' em vigor'},itens:its,sel:sel,inatN:0,escolhe:id=>cmdEscolhe(self,id)});
  const rs=[]; if(q&&!larga) viv.filter(casa).forEach(r=>rs.push({t:r.v.cod+' · '+r.v.nome,sub:r.v.dim,go:()=>cmdAbre(self,'g_dim',r.id,C7.slug[r.v.dim])}));
  cadResVals(v,rs);
  // ---- detalhe: cabeçalho com a origem (I19) e o Próximo passo da tela, fixo no topo: publicar o rascunho ----
  const av=cmdAviso(self,'Ver todas as dimensões'); const k=viv.filter(r=>!dim||r.v.dim===dim).length; const pd=c7pend(self,dim).length;
  const sub=!dim?(C7.dims.length+' dimensões · '+k+' códigos · cada código em uma dimensão: nunca combine fazenda, cultura e processo num único centro')
    :(C7.manuais.indexOf(dim)<0?'Cultura e Processo vêm do CD-02: aqui só a tradução para o ERP · '+k+(k===1?' código':' códigos')
    :(dim==='Natureza'?'Natureza de custo: os grupos de insumo do CD-06 levam o custo para cá · ':(dim==='Centro de responsabilidade'?'Cada centro tem o direcionador de rateio às culturas · ':''))+k+(k===1?' código':' códigos'));
  const p1=pl[0]; const maisP=pend?(pend+(pend===1?' código sem conta no ERP: ':' códigos sem conta no ERP: ')+pl.map(r=>r.v.cod).join(', ')+' (fica fora da publicação até ser traduzido).'):'';
  const abreP=p1?[{t:'Abrir '+p1.v.cod,go:()=>c7abreCod(self,p1.id)}]:[];
  const prox=n?{cor:'yellow',t:'Rascunho v'+(ver+1)+' com '+n+(n===1?' alteração':' alterações')+': a v'+ver+' segue em vigor até publicar.',prim:{t:'Publicar estrutura v'+(ver+1)+' ('+n+(n===1?' alteração)':' alterações)'),go:()=>v.c7pub()},mais:maisP?('e mais: '+maisP):'',lks:abreP}
    :(pend?{cor:'yellow',t:maisP.charAt(0).toUpperCase()+maisP.slice(1),lks:abreP}:{cor:'green',t:'v'+ver+' em vigor · nada no rascunho.'});
  cadDetVals(self,v,Object.assign({t:dim||'Todas as dimensões',sub:sub,chip:pd?{t:pd+' a resolver',c:'yellow'}:{t:'Em dia',c:'green'},prox:prox,volta:'Dimensões',voltar:()=>cmdVolta(self)},av));
  // ---- criar: só onde a tela é a fonte (Cultura e Processo vêm do CD-02, R15); a dimensão vem do mestre ----
  v.cab_criar_on=!dim||C7.manuais.indexOf(dim)>=0; v.cab_criarT='+ Criar código';
  v.c7_criar=()=>{ g2set(self,'g_dim',{fm:null}); g2new(self,GR('g_dim'),{draft:{dim:(dim&&C7.manuais.indexOf(dim)>=0)?dim:'',sup:'',rat:''}});
    setTimeout(()=>{ try{ const x=document.getElementById('fx_g_dim_cod'); if(x) x.focus(); }catch(z){} },90); };
  const ct=cmdConta(self,'g_dim',RW(self,'g_dim'),c7todos); v.c7_conta=ct.n+' de '+ct.tot;
  const vz=!ct.n?(q?{t:'Nenhum código encontrado para “'+q+'”.'+(v.cab_criar_on?' Para cadastrar, use + Criar código, no topo.':'')}:{t:'Nenhum código com este filtro.',go:{t:'Mostrar todos',fn:()=>self.setState({c7qf:''})}}):null;
  cadVazioSe(self,v,'c7_v',vz,['g_dim']);
  cadQfPos(self,v,'g_dim','c7qf');
  // linha da dimensão (em "Todas"): um alvo que escolhe a dimensão (BOT-07)
  (v.g_dim_rows||[]).forEach(x=>{ const p=RW(self,'g_dim').find(d=>d.id===x.id&&!d.v.dim); if(!p) return; const sl=C7.slug[p.v.cod]; x.tab='-1'; x.key=()=>{};
    x.open=(e)=>{ if(e&&e.target&&e.target.closest&&e.target.closest('button')) return; cmdEscolhe(self,sl); };
    const cc=x.cells.find(c=>c.isData); if(cc&&cc.parts[0]) cc.parts[0]=g2part({k:'act',alvo:true,t:cc.parts[0].t,al:'Abrir '+cc.parts[0].t,go:()=>cmdEscolhe(self,sl)},v); });
  // ---- formulário: Cultura e Processo (do CD-02) só a tradução; superior da mesma dimensão, escolhido da lista ----
  const F=v.g_dim_F; const fm=g2st(self,'g_dim').fm;
  if(F&&F.open&&fm&&fm.rid&&mud[fm.rid]==='excluído') F.sub='Excluído no rascunho v'+(ver+1)+': o código sai da estrutura quando a versão for publicada; até lá, só consulta.';
  if(F&&F.open&&F.fields&&fm&&!fm.ro&&!fm.cons){ const r=fm.rid?g2find(RW(self,'g_dim'),fm.rid):null; const d=fm.draft||{};
    if(r&&r.v.orig){ F.sub=r.v.dim+' vem de Culturas, cultivares e operações: aqui você altera só a tradução para o ERP.';
      F.fields=F.fields.filter(f=>['fx_g_dim_sup'].indexOf(f.fid)<0);
      F.fields.forEach(f=>{ const k=f.fid.replace('fx_g_dim_',''); if(['cod','nome','dim','ini','fim'].indexOf(k)>=0){ f.dis=true; f.ist=f.ist.replace('background:#FFFFFF','background:#F4F6F3'); if(k==='dim') f.opts=[{v:r.v.dim,t:r.v.dim}]; } }); }
    else { const desc=new Set(); const w=(x)=>(x.kids||[]).forEach(k=>{ desc.add(k.id); w(k); }); if(r) w(r);
      const fs=F.fields.find(f=>f.fid==='fx_g_dim_sup'); if(fs){ const ops=c7vivos(self).filter(x=>x.v.dim===d.dim&&(!r||x.id!==r.id)&&!desc.has(x.id));
        fs.opts=[{v:'',t:d.dim?'Nenhum (código de topo)':'Escolha a dimensão primeiro'}].concat(ops.map(x=>({v:x.v.cod,t:x.v.cod+' · '+x.v.nome}))); }
      const fd=F.fields.find(f=>f.fid==='fx_g_dim_dim'); if(fd&&!fd.dis) fd.set=(e)=>{ const cur=g2st(self,'g_dim').fm; if(!cur) return; const er=Object.assign({},cur.errs||{}); delete er.dim; delete er.sup;
        g2set(self,'g_dim',{fm:Object.assign({},cur,{draft:Object.assign({},cur.draft,{dim:e.target.value,sup:''}),errs:er,warn:false})}); }; } }
  valida(self,v,'g_dim',(d,fm)=>{ const e={}; const r=fm.rid?g2find(RW(self,'g_dim'),fm.rid):null; self.__c7old=r?{id:r.id,cod:r.v.cod}:null; if(r&&r.v.orig) return e;
    if(d.fim&&d.ini&&d.fim<d.ini) e.fim='O fim da vigência não pode ser antes do início ('+br(d.ini)+').';
    const dup=c7vivos(self).find(x=>x.id!==fm.rid&&x.v.dim===d.dim&&String(x.v.cod).trim().toLowerCase()===String(d.cod||'').trim().toLowerCase()); if(dup) e.cod='O código '+d.cod+' já existe em '+d.dim+'.';
    const sp=String(d.sup||'').trim(); if(sp){ if(sp===String(d.cod).trim()) e.sup='O superior não pode ser o próprio código.';
      else if(!c7vivos(self).some(x=>x.v.dim===d.dim&&x.v.cod===sp)) e.sup='Não existe o código '+sp+' em '+d.dim+'.';
      else if(r){ const desc=[]; const w=(x)=>(x.kids||[]).forEach(k=>{ desc.push(k.v.cod); w(k); }); w(r); if(desc.indexOf(sp)>=0) e.sup=sp+' é subcódigo deste código; escolha um superior fora dele.'; } }
    return e; });
  const marca=(id,tipo)=>{ const m=Object.assign({},c7mud(self)); if(!m[id]) m[id]=tipo; self.setState({c7mud:m}); };
  self.g2after=(gid,rows,r,isNew)=>{ if(gid!=='g_dim'||!r) return; const o=self.__c7old;
    if(o&&o.id===r.id&&o.cod!==r.v.cod) (r.kids||[]).forEach(k=>{ k.v.sup=r.v.cod; });   // subcódigos seguem o código renomeado
    const pai=c7poe(rows,r); const x=Object.assign({},g2st(self,'g_dim').x||GR('g_dim').x0||{}); if(pai) x[pai.id]=true; const dm=c7dm(rows,r.v.dim); if(dm) x[dm.id]=true;
    g2set(self,'g_dim',{rows:rows,x:x,fl:r.id}); marca(r.id,isNew?'novo':'alterado');
    self.setState({g2toast:'Salvo no rascunho v'+(c7ver(self)+1)+': '+r.v.cod+' · '+r.v.nome+(r.v.trad==='Dimensão própria'?' · traduzido na integração':(r.v.conta?' → '+r.v.conta:' · sem conta: fica fora da publicação até ser mapeado'))+'. Publique a estrutura para valer.'}); };
  const SEMNOV='Simulação: o ERP não tem mudanças novas para o rascunho.'; const IC=c7impCalc(self); const lis=a=>a.length?a:[{t:'nenhum'}];
  v.c7imp=()=>{ if(!c7impCalc(self).n){ self.setState({c7imp:false,g2toast:SEMNOV}); return; } self.setState({c7imp:true}); };
  v.c7imp_on=!!self.state.c7imp;
  v.c7imp_novos=lis(IC.novos.map(x=>({t:x.cod+' · '+x.nome+' · '+x.conta+(x.top?' · TOP '+x.top:'')})));
  v.c7imp_alts=lis(IC.alts.map(a=>({t:a.t}))); v.c7imp_sem=lis(c7pend(self).map(r=>({t:r.v.cod+' · '+r.v.nome})));
  v.c7imp_okt='Trazer '+IC.n+(IC.n===1?' mudança':' mudanças')+' para o rascunho';
  v.c7imp_no=()=>self.setState({c7imp:false,g2toast:'Prévia descartada · nada mudou no rascunho.'});
  v.c7imp_ok=()=>{ const C=c7impCalc(self); if(!C.n){ self.setState({c7imp:false,g2toast:SEMNOV}); return; }
    const rows=g2clone(RW(self,'g_dim')); const m=Object.assign({},c7mud(self)); const suf=String(Date.now()).slice(-5);
    C.novos.forEach((x,i)=>{ const id='imp'+(i+1)+'_'+suf; const r={id,v:{dim:x.dim,cod:x.cod,nome:x.nome,sup:x.sup,rat:x.rat||'',ini:'2026-10-01',fim:'',trad:'Conta do ERP',conta:x.conta,top:x.top,orig:'',grp:'',ops:''},s:{},p:{}};
      if(c7poe(rows,r)) m[id]='novo'; });
    C.alts.forEach(a=>{ const r=g2find(rows,a.id); if(r){ Object.assign(r.v,a.set); m[r.id]=m[r.id]||'alterado'; } });
    const nn=C.novos.length, na=C.alts.length; const txt=[nn?nn+(nn>1?' códigos novos':' código novo'):'',na?na+(na>1?' códigos alterados':' código alterado'):''].filter(Boolean).join(' e ');
    g2set(self,'g_dim',{rows}); self.setState({c7imp:false,c7mud:m,g2toast:'Rascunho v'+(c7ver(self)+1)+': '+txt+' vindos do ERP · nada foi publicado.'}); };
  v.c7pub=()=>{ const m=c7mud(self); const n2=Object.keys(m).length; const ver2=c7ver(self);
    if(!n2){ self.setState({g2toast:'Nada a publicar: o rascunho não tem alterações.'}); return; }
    const exc=Object.keys(m).filter(id=>m[id]==='excluído'); const rows=g2clone(RW(self,'g_dim')); exc.forEach(id=>c7rm(rows,id));
    const cs=c7todos(rows); const pe=cs.filter(r=>r.v.trad!=='Dimensão própria'&&!r.v.conta);
    if(exc.length) g2set(self,'g_dim',{rows});
    self.setState({c7ver:ver2+1,c7mud:{},g2toast:'Simulação: estrutura v'+(ver2+1)+' publicada para novos lançamentos com '+(cs.length-pe.length)+' de '+cs.length+' códigos'
      +(exc.length?' · '+exc.length+(exc.length>1?' códigos excluídos':' código excluído'):'')+' · v'+ver2+' preservada'+(pe.length?' · fora até ter conta: '+pe.map(r=>r.v.cod).join(', '):'')+'.'}); }; }
'''
