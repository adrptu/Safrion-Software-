// ===== Estoque · regras e leitura da tela (SUP · Suprimentos simplificado; docs/suprimentos-simplificado) =====
// Funções est* e e* do Estoque sobre o cenário compartilhado (cenario.js): a tela (EST.dc.html), os testes em node (sup_unit.js) e, depois, a fila em
// cartões do app leem e mudam o cenário só por aqui (uma regra por problema). Precisa de CEN0/cenario.js, E2 (dados da tela, _dados_js) e do bloco de
// perfis do g2lib.js (g2ator, g2papel, g2quem). Nada aqui mexe em estado de tela.
function nf(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function eq(n,un){ n=Number(n)||0; const d=Math.abs(n-Math.round(n))<1e-6?0:(Math.abs(n*10-Math.round(n*10))<1e-6?1:2); return nf(n,d)+(un?' '+un:''); }
function esig(n,un){ return (n>0?'+':(n<0?'−':''))+eq(Math.abs(n),un); }
function eblank(x){ return x===null||x===undefined||String(x).trim()===''; }
function elotId(s){ return String(s||'').split(' · ')[0].trim(); }
// datas tipadas (TABELAS-FOCO): ISO no valor (ordena), dd/mm/aaaa ou mm/aaaa no texto; "previsto 24/09" usa o ano de hoje
function eiso(s){ const t=String(s||'').replace(/^previsto /,'').replace(/ \(previsto\)$/,'').trim(); let m=/^(\d{2})\/(\d{2})\/(\d{4})$/.exec(t); if(m) return m[3]+'-'+m[2]+'-'+m[1];
  m=/^(\d{2})\/(\d{2})$/.exec(t); return m?String(E2.hoje).split('/')[2]+'-'+m[2]+'-'+m[1]:''; }
function edmy(iso){ const a=String(iso||'').split('-'); return a.length===3?a[2]+'/'+a[1]+'/'+a[0]:'—'; }
function eym(s){ const m=/^(\d{2})\/(\d{4})$/.exec(String(s||'')); return m?m[2]+'-'+m[1]:''; }
function eval_(s){ const m=/^(\d{2})\/(\d{4})$/.exec(String(s||'')); return m?Number(m[2])*100+Number(m[1]):999999; }
function ehojeYM(){ const a=String(E2.hoje).split('/'); return Number(a[2])*100+Number(a[1]); }
function ereqN(id){ return Number(String(id||'').replace(/\D/g,''))||0; }
const EOK=['Liberadas','Em execução'];
const FCOR={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray'};
const EFASE={'A liberar':'a liberar','Liberadas':'liberada','Em execução':'em execução','Em conferência':'em conferência','Encerradas':'encerrada'};
// embalagem: "galão 20 L" → 16 galões; aceita a unidade do item ("bandeja 50 mudas" num item em un → 1.850 bandejas; SUP N12)
function eemb(emb,un){ const m=/^(.*?)\s*(\d[\d.]*)\s*(\S+)\s*$/.exec(String(emb||'')); if(!m) return null; const u=m[3];
  if(!(u==='kg'||u==='L'||(un&&u===un)||un==='un')) return null; return {nome:m[1].trim(),n:Number(m[2].replace(/\./g,'')),un:u}; }
function eplur(nome,k){ if(k===1) return nome; return nome.split(' ').map((w,i,a)=>i<a.length-1?w:(/ão$/.test(w)?w.replace(/ão$/,'ões'):w+'s')).join(' '); }
function epk(q,emb,un){ const e=eemb(emb,un); if(!e||!(q>1e-9)||!(e.n>0)) return ''; const w=Math.floor(q/e.n+1e-9), r=q-w*e.n; if(!w) return 'menos de 1 '+e.nome; return nf(w)+' '+eplur(e.nome,w)+(r>1e-6?' + '+eq(r,e.un):''); }
function epkDe(q,emb,un){ const e=eemb(emb,un); if(!e||!(q>1e-9)||!(e.n>0)) return ''; const w=Math.floor(q/e.n+1e-9), r=q-w*e.n; if(!w) return 'menos de 1 '+e.nome+' de '+nf(e.n)+' '+e.un;
  return nf(w)+' '+eplur(e.nome,w)+' de '+nf(e.n)+' '+e.un+(r>1e-6?' + '+eq(r,e.un):''); }

// ---------- leitura do cenário ----------
// reserva feita para o item (na liberação da O.S. ou no início da demonstração); só ela pode ser consumida pela entrega
function eresTot(c,rid,prod){ return cenResTot(c,rid,prod); }
// turno fechado sem sinal: o consumo ainda está no aparelho; o Estoque vê consumo e custódia mudarem só quando o app envia
// (cenFecharTurno já baixou a custódia no aparelho; o item exibido devolve essa baixa até o envio · CEN_BAIXA_NO_SINAL desliga)
function epCons(o,prod){ if(typeof CEN_BAIXA_NO_SINAL!=='undefined') return 0;
  return (o.ap||[]).filter(a=>a.sinc===false).reduce((s,a)=>s+(Number((a.cons||{})[prod])||0),0); }
function eitem(c,r,it0){ const o=c.ordens[r.os]||{}; const sq=Math.min(epCons(o,it0.prod),it0.consumido||0);
  const it=sq>1e-9?Object.assign({},it0,{consumido:it0.consumido-sq,custodia:it0.custodia+sq}):it0;
  const l=c.lotes[it.prod+'|'+it.lote]||null; const pend=cenSaldoEntregar(it);
  const imp=(o.selos||[]).find(s=>/impedida/i.test(s.t||'')); const im=E2.imped[r.os]||null;
  const bloq=imp?(im?im.txt:(r.os+' '+String(imp.t).toLowerCase())):''; const selo=imp?(im?im.selo:'O.S. impedida'):'';
  const pode=!bloq&&EOK.indexOf(o.etapa)>=0;
  let motivo=bloq;
  if(!motivo&&!pode) motivo=(o.etapa==='A liberar')?(r.os+' aguarda a liberação na O.S. (agrônomo)'):(r.os+' '+(EFASE[o.etapa]||String(o.etapa||'').toLowerCase())+': sem nova entrega');
  const resP=l?Math.max(0,Math.min(l.reservado,eresTot(c,r.id,it.prod)-it.entregue)):0;
  const sinal=(o.ap||[]).some(a=>a.sinc===false);  /* apontamento no aparelho: a sobra só é conferida depois do envio */
  const cf=cenConfAbertas(c,r.os).find(k=>k.req===r.id&&k.prod===it.prod)||null;
  // entrega só do reservado (72.3 item 2): inteira = saldo coberto pela reserva própria; parte = até o que o lote tem para esta requisição
  const livreReq=l?Math.max(0,l.fisico-l.quarentena-Math.max(0,l.reservado-resP)):0; const ent=pode&&l?Math.min(pend,resP):0;
  const x={id:r.id+'|'+it.prod, rid:r.id, os:r.os, o, it, l, un:it.un, pend, pode, bloq, selo, motivo, resP, livre:l?cenDisp(l)+resP:0, quem:it.quem||o.resp||'', sinal, cf,
    faz:o.faz||'', livreReq, ent, parte:Math.min(ent,livreReq), insuf:ent>1e-9&&livreReq+1e-9<ent};
  x.sit=estSitItem(c,x); return x; }
function eitens(c){ const out=[]; Object.keys(c.reqs||{}).sort((a,b)=>ereqN(a)-ereqN(b)).forEach(k=>{ const r=c.reqs[k]; (r.itens||[]).forEach(it=>out.push(eitem(c,r,it))); }); return out; }
function econta(x){ return eq(x.it.solicitado,x.un)+' solicitado − '+eq(x.it.consumido,x.un)+' consumido − '+eq(x.it.custodia,x.un)+' em custódia'; }
function elotes(c){ return Object.keys(c.lotes).map(k=>Object.assign({key:k},c.lotes[k])); }
function eitemDisp(c,prod){ return Object.values(c.lotes).filter(l=>l.prod===prod).reduce((a,l)=>a+cenDisp(l),0); }
function elotLbl(l){ return l.lote+' · '+l.prod+' · '+l.local; }
function elotKey(c,lbl){ const a=String(lbl||'').split(' · '); const k=(a[1]||'').trim()+'|'+(a[0]||'').trim(); return c.lotes[k]?k:null; }
// recebimentos: notas de base + recebimentos gravados (movimento recebimento-nf com os dados da conferência)
function erecs(c){ const mv={}; (c.movs||[]).forEach(m=>{ if(m.tipo==='recebimento-nf'&&m.estRec&&!mv[m.estRec.id]) mv[m.estRec.id]=m.estRec; });
  const out=E2.recs.map(b=>mv[b.id]?Object.assign({},b,mv[b.id],{ok:true,hoje:true}):b);
  Object.keys(mv).forEach(k=>{ if(!E2.recs.some(b=>b.id===k)) out.push(Object.assign({},mv[k],{ok:true,hoje:true})); }); return out; }
function epedBase(lbl){ const id=elotId(lbl); return E2.pedidos.find(p=>p.id===id)||null; }
function epeds(c){ const RC=erecs(c); return E2.pedidos.map(p=>{ const x=Object.assign({},p); RC.forEach(r=>{ if(r.hoje&&elotId(r.ped)===p.id) x.a_entregar=Math.max(0,x.a_entregar-(Number(r.conf)||0)); }); return x; }); }
function efert(lbl){ const p=epedBase(lbl); return !!(p&&E2.sem_validade.indexOf(p.grupo)>=0); }
// contagens: registros de base + os gravados no cenário (c.estInv)
function einvs(c){ const S=c.estInv||{}; const out=E2.contagens.map(b=>S[b.id]||b); Object.keys(S).sort().forEach(k=>{ if(!E2.contagens.some(b=>b.id===k)) out.push(S[k]); }); return out; }
function einvRec(c,id){ const r=einvs(c).find(x=>x.id===id); return r?cenClone(r):null; }
function eput(c,rec){ c.estInv=c.estInv||{}; c.estInv[rec.id]=rec; }
function eajuste(c,rec){ return rec&&rec.aj?((c.ajustes||[]).find(a=>a.id===rec.aj)||null):null; }
function econtou(rec){ return !!rec&&rec.cont!==null&&rec.cont!==undefined&&rec.cont!==''; }
function enovoInv(c){ let n=2612; const ids=einvs(c).map(x=>x.id); while(ids.indexOf('INV-'+n)>=0) n++; return 'INV-'+n; }
const MTIPO={'reserva':'Reserva','entrega':'Entrega','recebimento':'Recebimento confirmado no app','consumo':'Consumo apontado no app','devolucao':'Devolução',
  'recebimento-nf':'Recebimento de nota','inspecao':'Quarentena liberada','laudo-reprovado':'Laudo reprovado','contagem':'Contagem sem diferença','ajuste':'Ajuste de inventário'};
function emovQtd(m){ const u=m.un||''; switch(m.tipo){ case 'entrega': return '−'+eq(m.qtd,u); case 'devolucao': case 'recebimento-nf': return '+'+eq(m.qtd,u);
  case 'ajuste': return esig(m.qtd,u); case 'reserva': return eq(m.qtd,u)+' reservados'; case 'inspecao': return eq(m.qtd,u)+' liberados'; case 'laudo-reprovado': return eq(m.qtd,u)+' bloqueados'; default: return ''; } }
function emovTxt(m){ const u=m.un||'';
  if(m.tipo==='reserva') return 'reserva '+m.req+' → '+m.os+': '+eq(m.qtd,u)+' reservados';
  if(m.tipo==='entrega') return 'entrega '+m.req+' → '+m.os+': −'+eq(m.qtd,u)+' ('+m.quem+')';
  if(m.tipo==='devolucao') return 'devolução '+m.req+' ('+m.os+'): +'+eq(m.qtd,u)+(m.apto?' apta':' bloqueada para inspeção');
  if(m.tipo==='recebimento-nf') return 'recebimento '+m.doc+': +'+eq(m.qtd,u)+(m.apto?' apto':' em quarentena')+(m.val&&m.val!=='—'?' · validade '+m.val:'');
  if(m.tipo==='inspecao') return 'quarentena liberada '+(m.doc?'com o laudo '+m.doc+' por '+m.quem:'após inspeção')+(m.parcela?' (parcela '+m.parcela+')':'')+': '+eq(m.qtd,u)+' passam a disponível'+(m.rev?' · '+m.rev:'');
  if(m.tipo==='laudo-reprovado') return 'laudo '+m.doc+' reprovado por '+m.quem+(m.parcela?' (parcela '+m.parcela+')':'')+': '+eq(m.qtd,u)+' seguem bloqueados'+(m.rev?' · '+m.rev:'');
  if(m.tipo==='contagem') return 'contagem '+(m.doc?m.doc+' ':'')+'sem diferença';
  if(m.tipo==='ajuste') return 'ajuste de inventário '+(m.doc?m.doc+' ':'')+'aprovado por '+(m.quem||'gestor')+': '+esig(m.qtd,u)+(m.rev?' · '+m.rev:'');
  return emovTipo(m); }
// consumo: o canal do apontamento (app ou web) ou o aceite do almoxarife (conf = o caso conciliado)
function emovTipo(m){ if(m.tipo==='consumo'&&m.origem!=='app') return typeof m.conf==='string'?'Consumo aceito na conferência':'Consumo apontado na web'; return MTIPO[m.tipo]||m.tipo; }
// lote vencido: validade (mês/ano) anterior ao mês de hoje; entra todo em quarentena e não volta ao disponível
function evenc(l){ return !!l&&!!l.validade&&l.validade!=='—'&&eval_(l.validade)<ehojeYM(); }
// consumo apontado no app: "Glifosato 480 10, 2,4-D 806 5" (cenFecharTurno) → itens com a unidade da requisição ou da O.S.
function econsDet(c,m){ const r=m.req&&c.reqs[m.req]; const o=c.ordens[m.os]||{};
  return String(m.det||'').split(', ').map(s=>{ const x=/^(.*)\s(-?[\d.]+(?:,\d+)?)$/.exec(s.trim()); if(!x) return null; const prod=x[1];
    const it=r&&r.itens.find(i=>i.prod===prod); const ins=(o.ins||[]).find(i=>i.p===prod);
    return {prod,qtd:Number(x[2].replace(/\./g,'').replace(',','.')),un:(it&&it.un)||(ins&&ins.un)||''}; }).filter(Boolean); }
// itens de cada movimento do app: a confirmação vale só para o que estava entregue e ainda sem confirmação naquele momento
// (mesma regra de cenConfirmarRecebimento, refeita pela trilha); usa m.itens quando o cenário gravar a lista no movimento
function eappItens(c){ const st={}, out={};
  const S=(rid,prod)=>{ const k=rid+'|'+prod; if(!st[k]){ const r0=CEN0.reqs[rid]; const i0=r0&&r0.itens.find(i=>i.prod===prod); st[k]={cust:i0?i0.custodia:0,conf:!!(i0&&i0.confirmado)}; } return st[k]; };
  (c.movs||[]).forEach(m=>{
    if(m.tipo==='entrega'){ const s=S(m.req,m.prod); s.cust+=m.qtd; s.conf=false; }
    else if(m.tipo==='devolucao'){ S(m.req,m.prod).cust-=m.qtd; }
    else if(m.tipo==='consumo'){ const cs=econsDet(c,m); out[m.id]=cs; if(m.req) cs.forEach(x=>{ S(m.req,x.prod).cust-=x.qtd; }); }
    else if(m.tipo==='recebimento'){ const r=c.reqs[m.req]; const l=[];
      (r?r.itens:[]).forEach(it=>{ const s=S(m.req,it.prod); if(s.cust>1e-9&&!s.conf){ l.push({prod:it.prod,qtd:s.cust,un:it.un}); s.conf=true; } });
      out[m.id]=Array.isArray(m.itens)?m.itens:l; } });
  return out; }
// consumo sem sinal: o apontamento é enviado por cenSinal (fila AP|…); o movimento fica pendente só enquanto a O.S. tiver apontamento sem envio
function esemSinal(c){ const sem={}, porOS={};
  (c.movs||[]).forEach(m=>{ if(m.sinc!==false) return; if(m.tipo==='consumo') (porOS[m.os]=porOS[m.os]||[]).push(m.id); else sem[m.id]=true; });
  Object.keys(porOS).forEach(os=>{ const o=c.ordens[os]||{}; const n=(o.ap||[]).filter(a=>a.sinc===false).length; const ids=porOS[os]; ids.slice(Math.max(0,ids.length-n)).forEach(id=>{ sem[id]=true; }); });
  return sem; }
// documento do ajuste aprovado fora desta tela: o ajuste do cenário com o mesmo lote e a mesma diferença
function emovDoc(c,m,usados){ if(m.doc||m.tipo!=='ajuste') return m.doc?{doc:m.doc,aj:m.aj||''}:null;
  const aj=(c.ajustes||[]).find(a=>a.estado==='Aprovado'&&a.prod===m.prod&&a.lote===m.lote&&Math.abs(a.dif-m.qtd)<1e-9&&!usados[a.id]); if(!aj) return null;
  usados[aj.id]=true; return {doc:aj.inv||aj.id,aj:aj.inv?aj.id:''}; }

// ---------- fazenda (DEC-2609-11, AC-72-10): da O.S. para requisição; do local (fonte única dados_cad.LOCAIS) para lote, nota e contagem ----------
function estFazLocal(local){ const x=(E2.locais||[]).find(l=>l.nome===local); return x?x.faz:''; }
function estNaFaz(faz,f){ return !f||f==='Todas'||faz===f; }
function estFazLote(c,key){ const l=c.lotes[key]; return l?estFazLocal(l.local):''; }

// ---------- Atenda requisições: situação de cada item e de cada requisição (uma variável por coluna; a linha não carrega comando) ----------
// Prioridade (SUP §3): O.S. impedida · Aguarda liberação · Lote insuficiente · Reserva parcial · faltam X · A entregar · Aguarda confirmação no app ·
// Consumo em conferência · Aguardando gestora · Sobra a receber · Em uso · Concluída
const ESIT=['O.S. impedida','Aguarda liberação','Lote insuficiente','Reserva parcial','A entregar','Aguarda confirmação no app','Consumo em conferência','Aguardando gestora','Sobra a receber','Em uso','Concluída'];
function estSitPri(t){ const i=ESIT.findIndex(s=>String(t||'').indexOf(s)===0); return i<0?ESIT.length:i; }
function estSitCf(c,k){ return k.relatado-cenConfCust(c,k)>1e-9?'Aguardando gestora':'Consumo em conferência'; }
function estAreaFeita(o){ return (o.etapa==='Em execução'||o.etapa==='Liberadas')&&!((o.saldo||0)>1e-6)&&(o.area||0)>0; }
function estSitItem(c,x){ const o=x.o, it=x.it;
  if(x.bloq) return 'O.S. impedida';
  if(o.etapa==='A liberar') return 'Aguarda liberação';
  if(x.ent>1e-9){ if(x.insuf) return 'Lote insuficiente';
    const tot=((o.ins||[]).find(i=>i.p===it.prod)||{}).tot; if(tot&&tot>it.solicitado+1e-6) return 'Reserva parcial · faltam '+eq(tot-it.solicitado,x.un);
    if(x.ent+1e-9<x.pend) return 'Reserva parcial · faltam '+eq(x.pend-x.ent,x.un);
    return 'A entregar'; }
  if(it.custodia>1e-9&&!it.confirmado&&it.entregue>1e-9&&o.etapa!=='Em conferência') return 'Aguarda confirmação no app';
  if(x.cf) return estSitCf(c,x.cf);
  if(it.custodia>1e-9&&(o.etapa==='Em conferência'||estAreaFeita(o))) return 'Sobra a receber';
  if(it.custodia>1e-9) return 'Em uso';
  return 'Concluída'; }
// fila por requisição (Santa Rita, "Com ação"): O.S. em execução com saldo a entregar → encerramento bloqueado (sobra ou conferência) → O.S. liberadas
// com saldo, pela ordem da REQ; o resto (em uso, concluída, impedida, aguardando liberação ou confirmação) depois. Consumo fora da requisição vira linha
// filha "<produto> · fora da requisição"; sem requisição, a linha-mãe "<O.S.> · sem requisição" (cobertura do CC-302)
function estFila(c,faz){ const IT=eitens(c), CF=cenConfAbertas(c), out=[];
  Object.keys(c.reqs||{}).sort((a,b)=>ereqN(a)-ereqN(b)).forEach(rid=>{ const r=c.reqs[rid]; const o=c.ordens[r.os]||{};
    if(!estNaFaz(o.faz||'',faz)) return;
    const its=IT.filter(x=>x.rid===rid); const fora=CF.filter(k=>k.req===rid&&!r.itens.some(i=>i.prod===k.prod));
    const confs=CF.filter(k=>k.req===rid); const sits=its.map(x=>x.sit).concat(fora.map(k=>estSitCf(c,k)));
    const sit=sits.slice().sort((a,b)=>estSitPri(a)-estSitPri(b))[0]||'Concluída';
    const entregar=its.some(x=>x.parte>1e-9); const bloq=its.some(x=>x.sit==='Sobra a receber')||confs.length>0;
    const grp=entregar&&o.etapa==='Em execução'?0:(bloq?1:(entregar?2:3));
    const inteira=entregar&&its.filter(x=>x.ent>1e-9).every(x=>!x.insuf);
    out.push({rid, os:r.os, o, faz:o.faz||'', sit, grp, acao:grp<3, itens:its, fora, confs, inteira, entregar, sobra:its.some(x=>x.sit==='Sobra a receber'),
      quem:(its.find(x=>x.it.quem)||{quem:o.resp||''}).quem||o.resp||''}); });
  CF.filter(k=>!k.req).forEach(k=>{ const o=c.ordens[k.os]||{}; if(!estNaFaz(o.faz||'',faz)) return;
    let row=out.find(y=>y.semReq&&y.os===k.os); if(!row){ row={rid:'', semReq:true, os:k.os, o, faz:o.faz||'', sit:'', grp:1, acao:true, itens:[], fora:[], confs:[], inteira:false, entregar:false, sobra:false, quem:o.resp||''}; out.push(row); }
    row.fora.push(k); row.confs.push(k); row.sit=row.fora.map(x=>estSitCf(c,x)).sort((a,b)=>estSitPri(a)-estSitPri(b))[0]; });
  return out.sort((a,b)=>(a.grp-b.grp)||(ereqN(a.rid)-ereqN(b.rid))); }
// "Entregar REQ inteira": o rótulo confirma o quê, quanto, lote e para quem; "Separe:" diz lote, validade, local e embalagem (SUP §4.3)
function estRotuloReq(c,rid,quem){ const r=c.reqs[rid]; if(!r) return {rotulo:'',separe:[],itens:[],inteira:false};
  const its=eitens(c).filter(x=>x.rid===rid&&x.ent>1e-9); const q=quem||(its[0]&&its[0].quem)||(c.ordens[r.os]||{}).resp||'';
  const sep=its.map(x=>{ const l=x.l; const pk=epkDe(x.ent,x.it.emb,x.un); return x.it.prod+': '+x.it.lote+(l&&l.validade&&l.validade!=='—'?' · val. '+l.validade:'')+(l?' · '+l.local:'')+(pk?' · '+pk:''); });
  return {rotulo:its.length?'Entregar '+rid+' · '+its.map(x=>eq(x.ent,x.un)+' '+x.it.prod+' (lote '+x.it.lote+')').join(' + ')+' a '+q:'', separe:sep,
    itens:its.map(x=>[x.it.prod,x.ent,q]), inteira:its.length>0&&its.every(x=>!x.insuf), quem:q}; }
function ejunta(a){ return a.length<2?a.join(''):a.slice(0,-1).join(', ')+' e '+a[a.length-1]; }
// tudo ou nada (um cenMudar; um item recusado desfaz todos): cada item com saldo coberto pela reserva própria sai inteiro. PCMS-M14; o PCM 1b estende para OM.
function estEntregarReq(c,rid,quem,ator){ const r=c.reqs[rid]; if(!r) throw new Error('Requisição não encontrada.');
  const its=r.itens.map(it=>({it,q:Math.min(cenSaldoEntregar(it),cenResPropria(c,rid,it,c.lotes[it.prod+'|'+it.lote]))})).filter(y=>y.q>1e-9);
  if(!its.length) throw new Error('Nada a entregar na '+rid+' pela reserva da liberação.');
  const q=quem||(c.ordens[r.os]||{}).resp||''; const feitos=[];
  its.forEach(y=>{ estEntregar(c,rid,y.it.prod,y.q,q,ator); const pk=epk(y.q,y.it.emb,y.it.un); feitos.push(eq(y.q,y.it.un)+' de '+y.it.prod+' ('+(pk?pk+', ':'')+'lote '+y.it.lote+')'); });
  return {msg:rid+': '+ejunta(feitos)+' entregues a '+q+' · aguarda confirmação no app.', por:g2ator(ator,'almoxarife')}; }

// ---------- contadores das seções (neutros; vermelho só para impedimento) e abertura pelo perfil de quem age ----------
function epl(n,s,p){ return n+' '+(n===1?s:p); }
function estParcelas(c,faz){ const out=[]; Object.keys(c.lotes).forEach(k=>{ const l=c.lotes[k]; if(!estNaFaz(estFazLocal(l.local),faz)) return;
    cenQuar(cenClone(l)).forEach(p=>out.push(Object.assign({key:k,lote:l.lote,prod:l.prod,un:l.un,local:l.local,venc:evenc(l),validade:l.validade},p))); }); return out; }
function estNotas(c,faz){ return erecs(c).filter(x=>estNaFaz(estFazLocal(x.local),faz)); }
function estContagens(c,faz){ return einvs(c).filter(x=>estNaFaz(estFazLote(c,x.key),faz)); }
function estInvSit(c,rec){ const aj=eajuste(c,rec); if(!econtou(rec)) return (rec.hist||[]).length?'Recontar':'A contar';
  const d=rec.cont-rec.sis; if(Math.abs(d)<1e-9) return 'Conferida'; if(aj&&aj.estado==='Aprovado') return 'Ajustada';
  return String(rec.causa||'').trim()?'Aguardando gestora':'Informar causa'; }
function estContadores(c,faz){ const F=estFila(c,faz); const ne=F.filter(x=>x.entregar).length, ns=F.filter(x=>x.sobra).length, nk=F.filter(x=>x.confs.some(k=>estSitCf(c,k)==='Consumo em conferência')).length;
  const ng=F.reduce((a,x)=>a+x.confs.filter(k=>estSitCf(c,k)==='Aguardando gestora').length,0);
  const nn=estNotas(c,faz).filter(x=>!x.ok).length, nl=estParcelas(c,faz).filter(p=>!p.laudo).length;
  const CT=estContagens(c,faz).map(r=>estInvSit(c,r)); const nc=CT.filter(s=>s==='A contar'||s==='Recontar').length, na=CT.filter(s=>s==='Aguardando gestora'||s==='Informar causa').length;
  const J=a=>a.filter(Boolean).join(' · ');
  return {req:J([ne?ne+' a entregar':'',ns?epl(ns,'sobra','sobras'):'',nk?nk+' em conferência':'',ng?ng+' aguardando gestora':'']), rec:J([nn?epl(nn,'nota','notas'):'',nl?epl(nl,'laudo','laudos'):'']),
    cnt:J([nc?nc+' a contar':'',na?epl(na,'ajuste','ajustes'):'']), n:{ne,ns,nk,ng,nn,nl,nc,na}}; }
// abertura sem endereço (SUP §2.2): contador com contagem atribuída "A contar" → Faça contagens; gestora → 1ª seção com decisão dela (consumo acima da
// custódia, laudo, ajuste); almoxarife → 1ª seção com pendência; os demais → Confira saldos. Abrir nunca muda o cenário.
function estAbertura(c,k,faz){ const pf=g2pf(k)||{k:''};
  if(estContagens(c,faz).some(r=>g2mesma(pf.k,r.contador)&&!econtou(r))) return 3;
  const n=estContadores(c,faz).n;
  if(g2papel(pf,'gestor')){ if(n.ng) return 1; if(n.nl) return 2; if(n.na) return 3; return 4; }
  if(g2papel(pf,'almoxarife')){ if(n.ne||n.ns||n.nk||n.ng) return 1; if(n.nn||n.nl) return 2; if(n.nc||n.na) return 3; return 4; }
  return 4; }
// visão Produção do Confira saldos: produto acabado que a Colheita grava no cenário em c.producao (chave produto|lote; {prod, lote, cultura, un da cultura
// (DEC-0510-03), qtd, local, origem:{os, talhao, safra}, situacao}). Ponto de entrada: esta frente só lê; quem grava é a frente da Colheita.
function estProducao(c,faz){ return Object.keys(c.producao||{}).map(k=>Object.assign({key:k},c.producao[k])).filter(p=>estNaFaz(estFazLocal(p.local),faz))
  .map(p=>Object.assign(p,{qtdTxt:eq(p.qtd,p.un),sit:p.situacao||'Em estoque'})); }

// ---------- mudanças no cenário (sempre dentro de cenMudar) ----------
// Recebimento: a parte apta e a parte em quarentena entram no mesmo lote (cenReceber); a quarentena vira parcela da nota; os dados da conferência ficam no movimento.
function estReceber(c,d,ator){   /* ator: quem confere (perfil); o movimento grava quem agiu (revisão do CTL-3, achado 4) */ const n0=c.movs.length; const antes=eitemDisp(c,d.item);
  if(d.apto>0) cenReceber(c,d.item,d.lote,d.apto,d.un,d.local,d.val,d.nf,true,ator);
  if(d.quar>0) cenReceber(c,d.item,d.lote,d.quar,d.un,d.local,d.val,d.nf,false,ator,d.obs);
  if(c.movs.length===n0) throw new Error('Nada conferido para entrar no estoque.');
  c.movs.slice(n0).forEach(m=>{ m.val=d.val; }); c.movs[n0].estRec=d;
  return {msg:'Recebimento '+d.nf+' conferido: '+eq(d.conf,d.un)+' de '+d.item+' no lote '+d.lote+(d.val&&d.val!=='—'?' (validade '+d.val+')':'')+'. Disponível '+eq(antes,d.un)+' → '+eq(eitemDisp(c,d.item),d.un)+(d.quar?'; '+eq(d.quar,d.un)+' em quarentena aguardam o laudo.':'.')}; }
// Entrega: só a reserva desta requisição é baixada (cenEntregar); a nova entrega aguarda a confirmação no app.
function estEntregar(c,rid,prod,qtd,quem,ator){ const r0=c.reqs[rid]; const it0=r0&&r0.itens.find(i=>i.prod===prod);
  const r=cenEntregar(c,rid,prod,qtd,quem,ator); it0.confirmado=false; return r; }
function estDevolver(c,rid,prod,qtd,apto,obs,ator){ const r=cenDevolver(c,rid,prod,qtd,apto,ator,obs); if(obs) c.movs[c.movs.length-1].obs=obs;
  const req=c.reqs[rid]; const o=c.ordens[req.os]||{}; const it=req.itens.find(i=>i.prod===prod); const pe=cenPodeEncerrar(c,req.os);
  return {msg:r.msg+' Custódia de '+prod+' na '+req.os+': '+eq(it.custodia+qtd,it.un)+' → '+eq(it.custodia,it.un)+(o.etapa==='Em conferência'&&!pe?' · encerramento liberado.':'.')}; }
// Contagem cega, sempre gravada; recontagem por outro contador (quem contou antes não reconta: dano evitado, a mesma pessoa confirmar a própria perda)
function estContar(c,inv,key,contado,contador,causa,ator){ const l=c.lotes[key]; if(!l) throw new Error('Escolha o lote contado.');
  const rec=einvRec(c,inv)||{id:inv,key,hist:[]}; const h=rec.hist||[]; const ant=h.length?h[h.length-1]:null;
  if(ant&&!econtou(rec)&&g2mesma(contador,ant.contador)) throw new Error('Recontagem exige outro contador: '+ant.contador+' fez a contagem anterior.');
  const sis=l.fisico; const n0=(c.ajustes||[]).length;
  const m0=c.movs.length; cenContar(c,key,contado,contador); const aj=(c.ajustes||[]).length>n0?c.ajustes[c.ajustes.length-1]:null; const reg=ator?g2ator(ator,'almoxarife'):''; if(aj){ aj.inv=inv; aj.causa=causa; aj.contador=contador; aj.reg=reg; }   /* reg: quem registrou (perfil) */
  c.movs.slice(m0).forEach(m=>{ if(m.tipo==='contagem'){ m.doc=inv; m.quem=contador; } });   /* contagem sem diferença: documento e contador na trilha */
  Object.assign(rec,{key,sis,cont:contado,contador,reg,causa,aj:aj?aj.id:null}); eput(c,rec); const d=contado-sis;
  return {msg:Math.abs(d)<1e-9?('Contagem '+inv+' conferida: sem diferença.'):('Contagem '+inv+' registrada: diferença '+esig(d,l.un)+' · '+aj.id+' vai à gestora'+(aj.afeta&&aj.afeta.length?' (atinge a reserva da '+aj.afeta.join(', ')+')':'')+'. O saldo não muda até aprovar'+(causa?'.':' · informe a causa.'))}; }
function estCausa(c,inv,causa){ const rec=einvRec(c,inv); rec.causa=causa; const aj=eajuste(c,rec); if(aj) aj.causa=causa; eput(c,rec);
  return {msg:'Causa da diferença de '+inv+' registrada'+(causa?': '+causa:'')+'. O ajuste vai à gestora; a quantidade contada segue travada.'}; }
function estRecontar(c,inv){ const rec=einvRec(c,inv); if(!econtou(rec)) throw new Error(inv+' ainda não foi contada.');
  const aj=eajuste(c,rec); if(aj&&aj.estado==='Aprovado') throw new Error('Ajuste '+inv+' já aprovado: não há recontagem.');
  if(aj&&aj.estado==='Aguardando gestor') cenAprovarAjuste(c,aj.id,false);
  rec.hist=(rec.hist||[]).concat([{cont:rec.cont,contador:rec.contador,causa:rec.causa||'',dif:rec.cont-rec.sis}]);
  const outro=E2.contadores.find(x=>x!==rec.contador)||rec.contador;
  Object.assign(rec,{cont:null,sis:null,causa:'',contador:outro,reg:'',aj:null}); eput(c,rec);
  return {msg:'Recontagem de '+inv+' aberta: outro contador conta sem ver o saldo; a contagem anterior fica registrada na origem da linha.'}; }
// Aprovar: a diferença contada é aplicada sobre o físico atual (movimentos depois da contagem continuam valendo).
function estAprovar(c,inv,ator){ const rec=einvRec(c,inv); const l=rec&&c.lotes[rec.key]; if(!l||!econtou(rec)) throw new Error('Nada a aprovar nesta contagem.');
  const d=rec.cont-rec.sis; if(Math.abs(d)<1e-9) throw new Error('Nada a aprovar nesta contagem.');
  if(!String(rec.causa||'').trim()) throw new Error('Informe a causa da diferença de '+inv+' na contagem antes de aprovar o ajuste.');
  let aj=eajuste(c,rec); if(aj&&aj.estado==='Aprovado') throw new Error('Ajuste '+inv+' já aprovado · nada aplicado de novo.');
  const antes=l.fisico;
  if(!aj){ const n0=(c.ajustes||[]).length; cenContar(c,rec.key,l.fisico+d,rec.contador); aj=c.ajustes[n0]; aj.inv=inv; aj.contador=rec.contador; aj.reg=rec.reg||''; rec.aj=aj.id; }   /* contagem anterior ao cenário (INV-2609) */
  aj.contado=l.fisico+d; aj.dif=d; aj.causa=rec.causa; const m0=c.movs.length; cenAprovarAjuste(c,aj.id,true,ator); eput(c,rec);
  c.movs.slice(m0).forEach(m=>{ if(m.tipo==='ajuste'){ m.doc=inv; m.aj=aj.id; } });   /* documento do ajuste na trilha de movimentos */
  return {msg:'Ajuste '+inv+' ('+aj.id+') aprovado por '+aj.por+': '+esig(d,l.un)+' no lote '+l.lote+'. Físico '+eq(antes,l.un)+' → '+eq(l.fisico,l.un)+'.'+(aj.rev?' Fica '+aj.rev+'.':'')}; }
