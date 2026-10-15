# -*- coding: utf-8 -*-
"""Compras de materiais, peças e serviços (CMP-MAT, V69 · docs/integracao/V69/COMPRAS-MATERIAIS.md). Dados sintéticos.

Pedido do proprietário (15/10/2026): "Compra de materiais, peças, etc tem que seguir uma lógica diferente, porque pode atender varias
culturas e safras diferentes o que se está comprando." A compra de insumos nasce da safra (SOL do Planejar safra); esta nasce de:
(a) OM da Manutenção que precisa de peça (o "Solicitar compra" da OM) ou de serviço de terceiro; (b) reposição do almoxarifado da oficina
quando o saldo livre + o já pedido fica abaixo do ponto de pedido do item; (c) requisição avulsa de uma área, com urgência.
A apropriação é por OM, ativo ou centro de custo, nunca por safra ou cultura; o custo chega às culturas pelo uso do ativo (horas ×
custo R$/h), sem rateio na compra.

Estado: c.man.cmp do cenário único (reqs SC-nnn, seqpc), ao lado de c.man.itens (o saldo da oficina) e c.man.oms (a OM que recebe a
peça, reservada na liberação pela DEC-2609-13, ou o custo do serviço). A numeração SC é a mesma do "Solicitar compra" da OM (c.man.seqsc). Fornecedores de peças e
serviços são fictícios e ficam aqui até entrarem no CD-05 (decisão de integração registrada no V69)."""
import json

HOJE = '2026-09-23'
PC0 = 201   # pedidos de manutenção em PC-2nn, série única de materiais e serviços (docs/pcm-suprimentos: "Mesma série PC-2xx, com tipo"); insumos em PC-1nn
G_PECAS = 'Peças'                         # grupos de dados2.GRUPOS / docs/pcm-suprimentos (Peças; Lubrificantes)
G_LUB = 'Lubrificantes'
G_MAT = 'Materiais gerais'                # material sem código (avulsa): vai direto ao centro de custo
G_SERV = 'Serviços de manutenção'         # serviço de terceiro (PRD, grupo "Serviços de manutenção"): sem estoque; o recebimento é o aceite
GRUPO_ITEM = {'OL-1540': G_LUB, 'OL-HID68': G_LUB, 'GR-EP2': G_LUB}   # os demais itens da oficina são Peças
CCS = ['Oficina', 'Sede', 'Irrigação', 'Armazém e beneficiamento']   # centros de custo das áreas (requisição avulsa)
CC_REP = 'Almoxarifado da oficina'
URG = ['Normal', 'Alta', 'Urgente']
URG_DIAS = {'Alta': 3, 'Urgente': 1}   # requisição avulsa: "precisa até" pela urgência (Normal fica sem data)
# DEC-2609-13 (decisão registrada do proprietário): a reserva nasce na liberação. A peça comprada para a OM entra no saldo e cobre a OM, que
# passa a poder ser liberada; prendê-la à OM desde o recebimento é a pergunta D5 ao proprietário (docs/pcm-suprimentos/DECISOES.md §4).
# Se ele aprovar (DEC registrada), True: o recebimento já reserva para a OM e a liberação só reserva o que falta (manLiberar).
RESERVA_NO_RECEBIMENTO = False
# fornecedores de peças e serviços (fictícios, IDs e propostas de docs/pcm-suprimentos: F08 Peças e Lubrificantes, F09 Peças; homologação e
# grupos como no CD-05: cotação só vai a homologado do grupo). Ficam aqui até entrarem no CD-05 (parceiros 20 → 25).
FORN = [
    dict(id='F08', nome='Agro Peças Centro-Oeste', grupos=[G_PECAS, G_LUB, G_MAT, G_SERV], homologado=True, fator=1.00, prazo=1, pag='28 dias',
         fs={G_LUB: dict(prazo=2), G_MAT: dict(prazo=2), G_SERV: dict(fator=1.06, prazo=3)}),
    dict(id='F09', nome='Rondon Peças Agrícolas', grupos=[G_PECAS], homologado=True, fator=0.97, prazo=6, pag='30 dias'),
    dict(id='F10', nome='Hidráulica Rondon', grupos=[G_SERV], homologado=True, fator=0.97, prazo=1, pag='28 dias'),
    dict(id='F11', nome='Oficina Volante MT', grupos=[G_SERV], homologado=False, fator=0.90, prazo=2, pag='à vista', motivo='documentação fiscal pendente'),
    dict(id='F12', nome='Ferragens São Bento', grupos=[G_MAT], homologado=True, fator=1.03, prazo=1, pag='à vista'),
]


def _f(fid): return next(f for f in FORN if f['id'] == fid)


def _cond(f, grupo):
    x = dict(fator=f['fator'], prazo=f['prazo']); x.update((f.get('fs') or {}).get(grupo, {})); return x


def _add(iso, n):
    import datetime
    return (datetime.date.fromisoformat(iso) + datetime.timedelta(days=n)).isoformat()


def props(itens, hoje=HOJE):
    """Propostas simuladas de quem pode ser convidado (homologado em todos os grupos da requisição): a mesma conta do cmmProps (JS)."""
    gs = list(dict.fromkeys(x['grupo'] for x in itens))
    out = []
    for f in FORN:
        if not f['homologado'] or not all(g in f['grupos'] for g in gs): continue
        cs = [_cond(f, g) for g in gs]; prazo = max(c['prazo'] for c in cs)
        tot = sum(x['qtd'] * round(x['preco'] * _cond(f, x['grupo'])['fator'], 2) for x in itens)
        out.append(dict(f=f['id'], valor=round(tot, 2), prazo=prazo, pag=f['pag'], chega=_add(hoje, prazo)))
    return out


def seed():
    """Três requisições em três etapas (uma por origem) + o que a tela calcula ao vivo (GR-EP2 abaixo do ponto de pedido, sem requisição)."""
    s38 = [dict(item='', nome='Diagnóstico do circuito hidráulico em bancada', un='serv', qtd=1, preco=1900, grupo=G_SERV)]
    p38 = props(s38, '2026-09-22'); e38 = min(p38, key=lambda p: p['valor'])
    s39 = [dict(item='FIL-MF4292', nome='Filtro de óleo MF 4292', un='un', qtd=4, preco=160, grupo=G_PECAS)]
    s40 = [dict(item='', nome='Eletrodo de solda E6013 2,5 mm', un='kg', qtd=10, preco=38, grupo=G_MAT)]
    reqs = {
        'SC-038': dict(id='SC-038', orig='om', tipo='Serviço', om='OM-0233', aid='a01', cc='Oficina', urg='Urgente', data='2026-09-22',
                       por='Otávio (responsável de manutenção)', motivo='Teste de pressão reprovado (120 bar; mínimo 180 bar): diagnóstico do circuito por terceiro',
                       itens=s38, etapa='Pedido emitido',
                       cot=dict(em='2026-09-22', por='Ana (gestora)', conv=[p['f'] for p in p38], props=p38),
                       ped=dict(id='PC-201', f=e38['f'], valor=e38['valor'], prazo=e38['prazo'], pag=e38['pag'], prev=e38['chega'], em='2026-09-22', por='Ana (gestora)', just='')),
        'SC-039': dict(id='SC-039', orig='rep', tipo='Material', cc=CC_REP, urg='Normal', data='2026-09-22', por='Rui (almoxarife)',
                       motivo='Saldo livre 0 un abaixo do ponto de pedido (2 un)', itens=s39, etapa='Em cotação',
                       cot=dict(em='2026-09-22', por='Ana (gestora)', conv=[p['f'] for p in props(s39, '2026-09-22')], props=props(s39, '2026-09-22'))),
        'SC-040': dict(id='SC-040', orig='avulsa', tipo='Material', cc='Oficina', urg='Alta', ate=_add(HOJE, URG_DIAS['Alta']), data=HOJE,
                       por='Zé (mecânico)', motivo='Solda do suporte da barra do pulverizador', itens=s40, etapa='A cotar'),
    }
    return dict(reqs=reqs, seqpc=PC0 + 1)


def js():
    """Regras sobre c.man (o estado da manutenção no cenário único): entram em dados_manutencao.js_regras(), depois das regras da OM."""
    cfg = dict(forn=FORN, ccs=CCS, ccRep=CC_REP, urg=URG, urgDias=URG_DIAS, gPecas=G_PECAS, gItem=GRUPO_ITEM, gMat=G_MAT, gServ=G_SERV, pc0=PC0,
               resRec=RESERVA_NO_RECEBIMENTO, alcada=__import__('dados2').ALCADA)
    return 'const CMM = ' + json.dumps(cfg, ensure_ascii=False) + ';\n' + JS


JS = r'''
/* ===== Compras de materiais, peças e serviços (CMP-MAT, V69): requisições SC-nnn em c.cmp, no estado da manutenção ===== */
const CMM_ETAPAS=['A cotar','Em cotação','Pedido emitido','Recebida','Aceita'];
function cmmDe(c){ return c.cmp||MAN0.cmp; }                                   /* leitura: estado salvo antes da V69 não tem c.cmp (vale a semente) */
function cmmEst(c){ if(!c.cmp) c.cmp=manClone(MAN0.cmp); return c.cmp; }       /* escrita */
function cmmForn(id){ return CMM.forn.find(f=>f.id===id)||{id,nome:id,grupos:[],homologado:false}; }
function cmmCond(f,g){ return Object.assign({fator:f.fator,prazo:f.prazo},(f.fs||{})[g]||{}); }
function cmmGrupos(r){ return [...new Set((r.itens||[]).map(x=>x.grupo))]; }
function cmmAberta(r){ return ['Recebida','Aceita'].indexOf(r.etapa)<0; }
function cmmServ(r){ return r.tipo==='Serviço'; }
function cmmGrupoItem(k){ return CMM.gItem[k]||CMM.gPecas; }
/* cotação só para fornecedor homologado em todos os grupos da requisição (a mesma regra da compra de insumos, CD-05) */
function cmmConvidaveis(r){ const gs=cmmGrupos(r); return CMM.forn.filter(f=>f.homologado&&gs.every(g=>f.grupos.indexOf(g)>=0)); }
function cmmForaRegra(r){ const gs=cmmGrupos(r); return CMM.forn.filter(f=>!f.homologado&&gs.some(g=>f.grupos.indexOf(g)>=0)); }
/* propostas simuladas: preço de referência × fator do fornecedor no grupo; prazo em dias a partir de hoje (paridade com dados_compras_mat.props) */
function cmmProps(c,r){ const gs=cmmGrupos(r); return cmmConvidaveis(r).map(f=>{ const prazo=Math.max.apply(null,gs.map(g=>cmmCond(f,g).prazo));
  const tot=(r.itens||[]).reduce((s,x)=>s+x.qtd*Math.round(x.preco*cmmCond(f,x.grupo).fator*100)/100,0);
  return {f:f.id,valor:Math.round(tot*100)/100,prazo,pag:f.pag,chega:manAdd(c.hoje,prazo)}; }); }
/* "precisa até": a janela da OM; na avulsa, a data da urgência; reposição não tem data */
function cmmAte(c,r){ if(r.om&&c.oms[r.om]) return c.oms[r.om].janIso||''; return r.ate||''; }
/* a proposta de referência: a de menor custo entre as que chegam a tempo (sem nenhuma a tempo, a de menor custo) */
function cmmSugerida(c,r){ const ps=(r.cot&&r.cot.props)||[]; if(!ps.length) return null; const ate=cmmAte(c,r); const ok=ate?ps.filter(p=>p.chega<=ate):ps;
  return (ok.length?ok:ps).slice().sort((a,b)=>a.valor-b.valor||a.prazo-b.prazo)[0]; }
/* alçada da compra (dados2.ALCADA, a mesma da compra de insumos): nível exigido pelo valor e nível de quem age (gestor → 2º, direção → 3º) */
function cmmNivel(v){ let i=CMM.alcada.findIndex(x=>x.ate===null||v<=x.ate+1e-9); return i<0?CMM.alcada.length-1:i; }
function cmmAlcIdx(pf){ const p=(manPf(pf).papeis)||{}; return p.direcao?2:(p.gestor?1:-1); }
/* quem faz (perfil de demonstração, não é segurança): pedir a reposição = almoxarife, PCM ou gestor; cotar e emitir pedido = gestor ou direção;
   receber material = almoxarife ou gestor; aceitar serviço = PCM ou gestor (quem pediu a OM confere o serviço); abrir avulsa = quem tem papel */
function cmmPode(pf,cmd){ const p=(manPf(pf).papeis)||{}; const tem=(...ks)=>ks.some(k=>!!p[k]);
  if(cmd==='repor') return tem('almoxarife','pcm','gestor','direcao')?'':'Ação do almoxarife, do PCM ou da gestora';
  if(cmd==='cotar'||cmd==='pedir') return tem('gestor','direcao')?'':'Ação de quem compra (gestora ou direção)';
  if(cmd==='receber') return tem('almoxarife','gestor')?'':'Ação do almoxarife ou da gestora';
  if(cmd==='aceitar') return tem('pcm','gestor')?'':'Ação do PCM (quem pediu) ou da gestora';
  if(cmd==='nova') return Object.keys(p).length?'':'Escolha um perfil com papel (Ver como)';
  return ''; }
function cmmExige(pf,cmd){ const m=cmmPode(pf,cmd); if(m) throw new Error(m+'. Nada foi alterado.'); }
function cmmQuem(pf){ const q=manPf(pf); const ks=Object.keys(q.papeis||{}); if(typeof g2ator==='function'&&ks.length){ const t=g2ator(q,ks[0]); if(t) return t; } return String(q.k||''); }
/* reposição: item com ponto de pedido cujo saldo livre (saldo − reservado) + o já pedido em reposição aberta fica abaixo do ponto;
   a sugestão repõe até o máximo do item. O estado salvo sem min/max lê a política da semente. */
function cmmPol(c,k){ const it=c.itens[k]||{}, b=(MAN0.itens||{})[k]||{}; return {min:Number(it.min!==undefined?it.min:b.min)||0,max:Number(it.max!==undefined?it.max:b.max)||0}; }
function cmmLivre(c,k){ const it=c.itens[k]; return it?it.saldo-it.reservado:0; }
function cmmPedido(c,k){ return Object.values(cmmDe(c).reqs).filter(r=>r.orig==='rep'&&cmmAberta(r)).reduce((s,r)=>s+(r.itens||[]).filter(x=>x.item===k).reduce((a,x)=>a+x.qtd,0),0); }
function cmmRepos(c){ return Object.keys(c.itens).map(k=>{ const p=cmmPol(c,k); if(!(p.min>0)) return null; const it=c.itens[k]; const livre=cmmLivre(c,k), ped=cmmPedido(c,k);
  if(livre+ped>=p.min-1e-9) return null; const qtd=Math.max(p.max,p.min)-(livre+ped);
  return {k,nome:it.nome,un:it.un,livre,ped,min:p.min,max:p.max,qtd,preco:it.preco}; }).filter(Boolean); }
function cmmNovoId(c){ const n=c.seqsc||41; c.seqsc=n+1; return 'SC-'+String(n).padStart(3,'0'); }
function cmmItensTxt(r){ return (r.itens||[]).map(x=>x.nome+' '+manN(x.qtd,1)+' '+x.un).join(', '); }
/* requisição da OM (o "Solicitar compra" da Manutenção): a mesma SC, na fila de Compras */
function cmmDaOm(c,o){ const s=cmmEst(c); const sc=o.sc;
  s.reqs[sc.id]={id:sc.id,orig:'om',tipo:'Material',om:o.id,aid:o.aid,cc:'Oficina',urg:o.crit==='Alta'?'Alta':'Normal',data:c.hoje,por:sc.por||'',
    motivo:'Falta peça para liberar a '+o.id+' · '+o.serv,itens:sc.itens.map(x=>({item:x.item,nome:x.nome,un:x.un,qtd:x.qtd,preco:(c.itens[x.item]||{}).preco||0,grupo:cmmGrupoItem(x.item)})),etapa:'A cotar'};
  return s.reqs[sc.id]; }
function cmmRepor(c,k,pf){ if(pf!==undefined) cmmExige(pf,'repor'); const x=cmmRepos(c).find(y=>y.k===k);
  if(!x) return {nada:true,msg:((c.itens[k]||{}).nome||k)+' não está abaixo do ponto de pedido (ou a reposição já foi pedida) · nada aberto.'};
  const s=cmmEst(c); const id=cmmNovoId(c);
  s.reqs[id]={id,orig:'rep',tipo:'Material',cc:CMM.ccRep,urg:'Normal',data:c.hoje,por:cmmQuem(pf),motivo:'Saldo livre '+manN(x.livre,1)+' '+x.un+(x.ped?' + '+manN(x.ped,1)+' '+x.un+' pedidos':'')+' abaixo do ponto de pedido ('+manN(x.min,1)+' '+x.un+')',
    itens:[{item:k,nome:x.nome,un:x.un,qtd:x.qtd,preco:x.preco,grupo:cmmGrupoItem(k)}],etapa:'A cotar'};
  return {id,msg:id+' aberta: reposição de '+manN(x.qtd,1)+' '+x.un+' de '+x.nome+' para o '+CMM.ccRep.toLowerCase()+' (repõe até '+manN(x.max,1)+' '+x.un+').'}; }
/* requisição avulsa: tipo, item do almoxarifado ou descrição, quantidade, destino (ativo ou centro de custo), urgência e motivo. Nunca safra ou cultura. */
function cmmNova(c,d,pf){ if(pf!==undefined) cmmExige(pf,'nova'); d=d||{}; const err={};
  const tipo=d.tipo==='Serviço'?'Serviço':'Material'; const cat=tipo==='Material'&&d.item&&c.itens[d.item]?c.itens[d.item]:null;
  const nome=cat?cat.nome:String(d.nome||'').trim(); if(!nome) err.nome=tipo==='Serviço'?'Descreva o serviço.':'Escolha o item ou descreva o material.';
  const qtd=manNum(d.qtd); if(!(qtd>0)) err.qtd='Informe a quantidade (maior que zero).';
  const preco=cat?cat.preco:manNum(d.preco); if(!cat&&!(preco>0)) err.preco='Informe a estimativa em R$ por unidade.';
  const aid=d.destino&&c.ativos[d.destino]?d.destino:''; const cc=aid?'':(CMM.ccs.indexOf(d.destino)>=0?d.destino:''); if(!aid&&!cc) err.destino='Escolha o ativo ou o centro de custo.';
  const urg=CMM.urg.indexOf(d.urg)>=0?d.urg:''; if(!urg) err.urg='Escolha a urgência.';
  if(manVazio(d.motivo)) err.motivo='Diga para que é (o motivo).';
  if(Object.keys(err).length) return {erro:'Corrija os campos destacados; o que você preencheu foi mantido.',err};
  const s=cmmEst(c); const id=cmmNovoId(c); const un=cat?cat.un:(tipo==='Serviço'?'serv':(String(d.un||'').trim()||'un'));
  const grupo=tipo==='Serviço'?CMM.gServ:(cat?cmmGrupoItem(d.item):CMM.gMat);
  s.reqs[id]={id,orig:'avulsa',tipo,aid,cc:cc||'Oficina',urg,ate:CMM.urgDias[urg]?manAdd(c.hoje,CMM.urgDias[urg]):'',data:c.hoje,por:cmmQuem(pf),motivo:String(d.motivo).trim(),
    itens:[{item:cat?d.item:'',nome,un,qtd,preco,grupo}],etapa:'A cotar'};
  return {id,msg:id+' aberta: '+nome+' '+manN(qtd,1)+' '+un+' · '+(aid?c.ativos[aid].nome:'centro de custo '+cc)+' · urgência '+urg.toLowerCase()+'.'}; }
function cmmPega(c,id){ const r=cmmDe(c).reqs[id]; if(!r) throw new Error('Requisição '+id+' não encontrada.'); return cmmEst(c).reqs[id]; }
/* cotação (simulada): convites aos homologados do grupo e as propostas chegam na hora; repetir não convida de novo */
function cmmCotar(c,id,pf){ if(pf!==undefined) cmmExige(pf,'cotar'); const r=cmmPega(c,id);
  if(r.etapa!=='A cotar') return {nada:true,msg:'Cotação da '+id+' já solicitada'+(r.cot?' em '+manBr(r.cot.em):'')+' · nenhum convite repetido.'};
  const fs=cmmConvidaveis(r); if(!fs.length) throw new Error('Nenhum fornecedor homologado em '+cmmGrupos(r).join(' e ')+': homologue um no cadastro de parceiros (CD-05). Nada foi enviado.');
  r.cot={em:c.hoje,por:cmmQuem(pf),conv:fs.map(f=>f.id),props:cmmProps(c,r)}; r.etapa='Em cotação';
  return {msg:'Cotação da '+id+' enviada a '+fs.length+(fs.length>1?' fornecedores homologados':' fornecedor homologado')+' (simulado · nenhuma mensagem real) · '+r.cot.props.length+(r.cot.props.length>1?' propostas recebidas':' proposta recebida')+'.'}; }
/* pedido: a proposta escolhida; fora da referência (menor custo a tempo) exige justificativa; o valor passa pela alçada de quem age */
function cmmPedir(c,id,fid,just,pf){ if(pf!==undefined) cmmExige(pf,'pedir'); const r=cmmPega(c,id);
  if(r.ped) return {nada:true,msg:'Pedido '+r.ped.id+' da '+id+' já emitido · nada repetido.'};
  if(r.etapa!=='Em cotação') throw new Error('Solicite as cotações da '+id+' antes de emitir o pedido.');
  const p=(r.cot.props||[]).find(x=>x.f===fid); if(!p) throw new Error('Escolha uma proposta.');
  const ref=cmmSugerida(c,r); if(ref&&p.f!==ref.f&&manVazio(just)) throw new Error('Justifique a escolha: a de menor custo que chega a tempo é '+cmmForn(ref.f).nome+' ('+manRS(ref.valor)+').');
  if(pf!==undefined){ const ix=cmmAlcIdx(pf), ni=cmmNivel(p.valor); if(ix<ni) throw new Error('Acima da sua alçada: '+manRS(p.valor)+' é decisão de '+CMM.alcada[ni].quem+'. Nada foi emitido.'); }
  const s=cmmEst(c); const pc='PC-'+(s.seqpc||CMM.pc0); s.seqpc=(s.seqpc||CMM.pc0)+1;
  r.ped={id:pc,f:p.f,valor:p.valor,prazo:p.prazo,pag:p.pag,prev:p.chega,em:c.hoje,por:cmmQuem(pf),just:ref&&p.f!==ref.f?String(just).trim():''}; r.etapa='Pedido emitido';
  return {msg:pc+' emitido para '+cmmForn(p.f).nome+' · '+manRS(p.valor)+' · previsão '+manBr(p.chega)+' · vinculado à '+id+(r.om?' e à '+r.om:'')+'.'}; }
/* recebimento do material: peça da OM entra no saldo e fica reservada para a OM (manReceberSc, a mesma função da ponte da Manutenção);
   reposição entra no estoque da oficina; material sem código vai direto ao centro de custo (consumo, sem saldo) */
function cmmReceber(c,id,pf){ if(pf!==undefined) cmmExige(pf,'receber'); const r=cmmPega(c,id);
  if(cmmServ(r)) throw new Error('Serviço não tem recebimento de estoque: registre o aceite do serviço.');
  if(r.etapa==='Recebida') return {nada:true,msg:'Recebimento da '+id+' já registrado em '+manBr(r.rec.em)+' · nada somado de novo.'};
  if(r.etapa!=='Pedido emitido') throw new Error('Emita o pedido da '+id+' antes de receber.');
  const quem=cmmQuem(pf);
  if(r.orig==='om'){ const o=c.oms[r.om]; if(!o||!o.sc||o.sc.id!==id) throw new Error('A '+(r.om||'OM')+' não aguarda a '+id+'.');
    const res=manReceberSc(c,o,quem); return {msg:'Recebimento da '+id+' ('+r.ped.id+'): '+cmmItensTxt(r)+(res.length?' · reservado para a '+o.id+': '+res.join(', '):' · no saldo da oficina para a '+o.id)
      +(o.etapa==='A liberar'?' · '+o.id+' pronta para liberar'+(res.length?'':' (a reserva nasce na liberação)'):'')+'.'}; }
  const est=[]; (r.itens||[]).forEach(x=>{ if(x.item&&c.itens[x.item]){ c.itens[x.item].saldo+=x.qtd; est.push(x.nome+' · saldo '+manN(c.itens[x.item].saldo,1)+' '+x.un); } });
  r.etapa='Recebida'; r.rec={em:c.hoje,por:quem,dest:est.length?'estoque':'cc'};
  return {msg:'Recebimento da '+id+' ('+r.ped.id+'): '+cmmItensTxt(r)+(est.length?' · no estoque da oficina: '+est.join(', '):' · entregue a '+(r.aid?c.ativos[r.aid].nome:'centro de custo '+r.cc)+' (consumo direto, sem estoque)')+'.'}; }
/* aceite do serviço: sem estoque; o valor do pedido vira custo de terceiro da OM (manCusto: peças + horas × custo-hora + terceiro) */
function cmmAceitar(c,id,pf){ if(pf!==undefined) cmmExige(pf,'aceitar'); const r=cmmPega(c,id);
  if(!cmmServ(r)) throw new Error('Material se recebe: registre o recebimento.');
  if(r.etapa==='Aceita') return {nada:true,msg:'Aceite da '+id+' já registrado em '+manBr(r.aceite.em)+' · custo não lançado de novo.'};
  if(r.etapa!=='Pedido emitido') throw new Error('Emita o pedido da '+id+' antes do aceite.');
  const o=r.om?c.oms[r.om]:null; if(r.om&&!o) throw new Error('A '+r.om+' não foi encontrada.');
  if(o){ o.terc=Math.round(((Number(o.terc)||0)+r.ped.valor)*100)/100; o.servs=(o.servs||[]).concat([{sc:id,pc:r.ped.id,valor:r.ped.valor,em:c.hoje,por:cmmQuem(pf)}]); manToca(o); }
  r.etapa='Aceita'; r.aceite={em:c.hoje,por:cmmQuem(pf)};
  return {msg:'Serviço da '+id+' aceito ('+r.ped.id+' · '+manRS(r.ped.valor)+')'+(o?' · custo de terceiro da '+o.id+': '+manRS(o.terc)+' (custo estimado da ordem '+manRS(manCusto(c,o,'est'))+')':' · custo no centro de custo '+r.cc)+'.'}; }
try { window.__cmm = { cmmDe, cmmRepos, cmmProps, cmmSugerida, cmmPode, manGet }; } catch (e) {}
'''
