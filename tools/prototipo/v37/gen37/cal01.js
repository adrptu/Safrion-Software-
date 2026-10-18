// ===== CAL-01 · Necessidade líquida por data (PRD v3.9) — a mesma memória de cálculo no Planejar safra (etapa 4), na Compra de insumos e no Mapa › Insumos =====
// Convenção única: o físico apto (fora quarentena) INCLUI as reservas; cada necessidade entra uma vez. Reserva da mesma demanda (chave
// cultivo|atividade ou ID da O.S. presente na demanda, DEM-04) não é subtraída de novo; reserva para outro destino entra como demanda na data dela.
// Recebimento só cobre usos na data dele ou depois. A reposição proposta entra no saldo projetado: faltas sucessivas não se acumulam.
// opt {hoje, viavel} (AAAA-MM-DD): uso do plano com data antes de hoje e sem O.S. fica fora da demanda (DEM-06: histórico do plano, não
// "realizado"; o realizado vem das O.S., DEM-02). Falta antes da chegada viável de uma compra nova é ruptura: os recebimentos até lá a cobrem
// (a mais antiga primeiro) e o que sobrar vira reposição na data viável. Sem opt, a reposição entra na própria data da falta.
// O que entra nos eventos (plano sem a parte das O.S., O.S. pelo pendente, outras safras, reservas e recebimentos da fazenda) sai de demFazenda (abaixo).
// ev: {dt:'AAAA-MM-DD', q, tipo:'rec'|'res'|'dem', own:bool (é da solicitação calculada), ord:ordem global da origem, t:texto, chave|chaves, ref}
// No mesmo dia: recebimento, chegada viável, reserva e as demandas na ordem global das safras (igual em todas as telas: a falta não é atribuída duas vezes).
function cal01(fis, evs, seg, opt){
  seg=Number(seg)||0; opt=opt||{}; const hoje=opt.hoje||'', via=opt.viavel||''; const ks={};
  (evs||[]).forEach(e=>{ if(e.tipo!=='dem') return; if(e.chave) ks[e.chave]=1; (e.chaves||[]).forEach(k=>{ ks[k]=1; }); });
  let real=0, nreal=0; const E0=[], pendentes=[];
  (evs||[]).forEach((e,i)=>{ if(e.tipo==='dem'&&!e.dt){ pendentes.push(Object.assign({},e)); return; } if(e.tipo==='dem'&&hoje&&e.dt&&e.dt<hoje){ if(e.own){ real+=Number(e.q)||0; nreal++; } return; } E0.push(Object.assign({i:i},e)); });
  if(via) E0.push({i:1e9,dt:via,q:0,tipo:'via',ord:0});
  const pri=(e)=>e.tipo==='rec'?0:(e.tipo==='via'?1:(e.tipo==='res'?2:3));
  const E=E0.sort((a,b)=>(a.dt<b.dt?-1:(a.dt>b.dt?1:0))||(pri(a)-pri(b))||((a.ord||0)-(b.ord||0))||(a.i-b.i));
  let ult=''; E.forEach(e=>{ if(e.tipo==='dem'&&e.own&&e.dt>ult) ult=e.dt; });
  const semData=pendentes.filter(e=>e.own).reduce((s,e)=>s+(Number(e.q)||0),0);
  let saldo=Number(fis)||0, bruta=semData, rec=0, liq=0, tot=0, antes=0, falta=null, faltaTot=null, saldoUlt=null, rup=0, rupVia=0, cob=null; const L=[]; const bk=[];
  const def=()=>Math.max(0,seg-saldo);
  E.forEach(e=>{ const q=Number(e.q)||0;
    if(e.tipo==='via'){ const d=def(); if(d<=1e-9) return; let own=0; bk.forEach(b=>{ if(b.own) own+=b.q; }); bk.length=0;
      liq+=own; rupVia+=own; tot+=d; saldo=seg; if(own>1e-9) cob=e.dt; L.push({dt:e.dt,tipo:'via',t:'Reposição com chegada viável',q:d,saldo:saldo,nec:own}); return; }
    if(e.tipo==='rec'){ const d0=def(); saldo+=q; rec+=q; let c=d0-def(), dono=false;
      while(c>1e-9&&bk.length){ const b=bk[0], x=Math.min(b.q,c); b.q-=x; c-=x; if(b.own) dono=true; if(b.q<=1e-9) bk.shift(); }
      if(dono&&!bk.some(b=>b.own)) cob=e.dt;
      L.push({dt:e.dt,tipo:'rec',t:e.t,q:q,saldo:saldo,nec:0,cobre:d0-def()}); return; }
    if(e.tipo==='res'&&e.chave&&ks[e.chave]){ L.push({dt:e.dt,tipo:'res0',t:e.t,q:q,saldo:saldo,nec:0}); return; }   // mesma demanda: conta uma vez
    const own=(e.tipo==='dem'&&e.own), d0=def(); saldo-=q; let nec=0, rp=0;
    if(saldo<seg-1e-9){ if(!via||e.dt>=via){ nec=seg-saldo; saldo=seg; } else { rp=def()-d0; bk.push({own:own,q:rp}); } }
    if(own){ bruta+=q; liq+=nec; rup+=rp; if((nec>1e-9||rp>1e-9)&&!falta) falta=e.dt; if(e.dt===ult) saldoUlt=saldo; }
    else if(e.dt<=ult) antes+=q-nec-rp;
    tot+=nec; if((nec>1e-9||rp>1e-9)&&!faltaTot) faltaTot=e.dt;
    L.push({dt:e.dt,tipo:(e.tipo==='res'?'res':(own?'dem':'out')),t:e.t,calc:e.calc,q:q,saldo:saldo,nec:nec,rup:rp}); });
  const lim=(cob&&cob>ult)?cob:ult; L.forEach(l=>{ l.ate=l.dt<=lim; });
  const tarde=falta?E.filter(e=>e.tipo==='rec'&&e.dt>falta).reduce((a,e)=>a+(Number(e.q)||0),0):0;
  return {fis:Number(fis)||0,bruta:bruta,rec:rec,liq:liq,tot:tot,falta:falta,faltaTot:faltaTot,antes:antes,tarde:tarde,saldo:saldo,saldoUlt:saldoUlt,
    semData:semData,parcial:pendentes.length>0,pendentes:pendentes,real:real,nreal:nreal,hoje:hoje,via:via,rup:rup,rupRec:Math.max(0,rup-rupVia),cob:cob,linhas:L};
}
// falta condicionada à qualidade (PRD 65.4; CAL-01 "Qualidade pendente"; DEMO-02) · o mesmo texto na memória do Planejar safra e da Compra, no aviso
// da Compra e no Mapa › Insumos: motivo (lote, documento e o motivo registrado na entrada), responsável (o gestor decide com o laudo no Estoque),
// prazo (a data em que a falta começa se o laudo reprovar) e a decisão fora da compra. o: {quarC, quarRef, condFalta, un}
function demCondTxt(o){ o=o||{}; const u=' '+(o.un||''); const d4=(s)=>s?String(s).slice(8,10)+'/'+String(s).slice(5,7)+'/'+String(s).slice(0,4):'';
  const ls=(o.quarRef||[]).filter(x=>!x.rep&&!x.vencido).map(x=>'lote '+x.lote+(x.doc?' · '+x.doc:'')+(x.mot?': '+x.mot:'')).join('; ');
  return 'motivo: '+calNfa(Number(o.quarC)||0)+u+' em quarentena aguardam laudo'+(ls?' ('+ls+')':'')
    +' · responsável: o gestor libera ou reprova com o laudo no Estoque (reprovado, vira falta firme)'
    +' · prazo: '+(o.condFalta?'decidir antes de '+d4(o.condFalta)+', quando a falta começa se reprovar':'decidir antes do uso')
    +' · fora da compra: sem nova compra automática'; }
// memória em linhas curtas (painel de origem do insumo), como um extrato por data: estoque apto, o já realizado, cada movimento até o último
// uso da safra (ou até a ruptura ser coberta) e o resultado. Linha com a data no início ("25/09/2026 · T1-A · Dessecação pré-plantio · 2,00 L/ha × 160 ha = 320,0 L → saldo 980 L").
function cal01Memo(r, o){ o=o||{}; const u=' '+(o.un||'');
  const n=(x)=>Number(x||0).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:1});
  const n1=(x)=>Number(x||0).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1});
  const d=(s)=>s?String(s).slice(8,10)+'/'+String(s).slice(5,7)+'/'+String(s).slice(0,4):'—';
  const cu=Number(o.cust)||0;   // custódia sem uso nas O.S. (revisão do 853a6a8, achado 1): suprimento que volta na devolução
  const qc=Number(o.quarC)||0;   // quarentena com laudo pendente: cobertura condicionada à qualidade (revisão do 853a6a8, achado 2; PRD 65.4)
  const quarNaoVencida=Math.max(0,(Number(o.quar)||0)-(o.quarRef||[]).filter(x=>x.vencido).reduce((s,x)=>s+(Number(x.q)||0),0));
  const qd=(rep)=>(o.quarRef||[]).filter(x=>!!x.rep===rep&&!x.vencido).map(x=>'lote '+x.lote+(x.doc?' · '+x.doc:'')).join('; ');
  const out=['Estoque apto hoje: '+n(r.fis-cu-qc)+u+(o.res?' (inclui '+n(o.res)+u+' reservados)':'')+(cu>1e-9?' + '+n(cu)+u+' em custódia sem uso nas O.S., a devolver ao Estoque ('+(o.custT||[]).join('; ')+')':'')
    +(qc>1e-9?' + '+n(qc)+u+' em quarentena, cobertura condicionada à qualidade ('+(qd(false)||'laudo pendente')+': laudo pendente)':'')+((cu>1e-9||qc>1e-9)?' = '+n(r.fis)+u:'')
    +(!qc&&quarNaoVencida?' · '+n(quarNaoVencida)+u+' em quarentena não contam até o laudo':'')];
  (o.quarRef||[]).filter(x=>x.vencido).forEach(x=>out.push('Vencido: '+n(x.q)+u+' em quarentena no lote '+x.lote+' (validade '+x.validade+')'+(x.doc?' · '+x.doc:'')+(x.mot?' · '+x.mot:'')+' · não cobre a demanda e não pode ser liberado por laudo; físico e quarentena preservados.'));
  if(r.parcial){ out.push('Projeção datada parcial · há demanda sem data: aguarda âncora'); (r.pendentes||[]).forEach(e=>out.push('Sem data: aguarda âncora · '+(e.t||'Uso')+' · '+n(e.q)+u+' · quantidade preservada no planejamento')); }
  if(r.real>1e-9) out.push('Antes de '+d(r.hoje)+' sem O.S. · '+r.nreal+(r.nreal>1?' usos':' uso')+' · '+n(r.real)+u+' · fora da demanda (histórico do plano; se ainda vai acontecer, emita a O.S.)');   // DEM-06 (RN-003)
  r.linhas.filter(l=>l.ate).forEach(l=>{ const sx=' → saldo '+n(l.saldo)+u; const t=d(l.dt)+' · '+(l.t||'Uso')+' · ';
    if(l.tipo==='rec') out.push(t+'+'+n1(l.q)+u+sx+(l.cobre>1e-9?' · cobre a ruptura':''));
    else if(l.tipo==='via') out.push(t+'+'+n1(l.q)+u+sx);
    else if(l.tipo==='res0') out.push(t+n1(l.q)+u+' da mesma demanda, contados uma vez');
    else if(l.tipo==='dem') out.push(t+(l.calc?l.calc+' = ':'')+n1(l.q)+u+sx+(l.nec>1e-9?' · falta '+n(l.nec)+u:'')+(l.rup>1e-9?' · ruptura '+n(l.rup)+u:''));
    else out.push(t+'−'+n1(l.q)+u+sx); });
  if((Number(o.cond)||0)>1e-9) out.push('Falta condicionada à qualidade: '+n(o.cond)+u+(o.condFalta?' a partir de '+d(o.condFalta):'')+' se o laudo reprovar · '+demCondTxt(o));   // PRD 65.4; CAL-01 "Qualidade pendente"; DEMO-02
  // reprovado por laudo (revisão do 16fb55e, ajuste 2): com mais de um laudo no lote, cada um com a sua quantidade e o seu motivo (x.reps, do histórico)
  const rl=(r,dc)=>' laudo '+(r.laudo||'—')+(dc&&r.doc?' ('+r.doc+')':'')+(r.motivo?': '+r.motivo:'');
  (o.quarRef||[]).filter(x=>x.rep).forEach(x=>{ const rs=(x.reps||[]).length>1?x.reps:null; const dc=!!rs&&rs.some(r=>r.doc!==rs[0].doc);
    out.push('Reprovado: '+n(x.q)+u+' do lote '+x.lote+(x.doc&&!dc?' ('+x.doc+')':'')
      +(rs?' = '+rs.map(r=>n(r.q)+u+' no'+rl(r,dc)).join(' + '):' ·'+rl(x.rep,false))
      +' · segregado para devolução ao fornecedor, não cobre: a falta é firme'); });
  out.push(r.liq>1e-9?('Necessidade líquida = soma das faltas desta safra = '+n(r.liq)+u+' · falta a partir de '+d(r.falta))
    :(r.rupRec>1e-9?('Sem compra nova · ruptura de '+n(r.rupRec)+u+' de '+d(r.falta)+' a '+d(r.cob)+', coberta pelo recebimento')
    :((r.parcial?'Sem falta na parcela datada (projeção parcial)':'Sem falta nesta safra')+((Number(o.cond)||0)>1e-9?' se o laudo liberar os '+n(qc)+u+' em quarentena (a falta condicionada está acima)':'')+' · saldo depois do último uso: '+n(r.saldoUlt==null?r.saldo:r.saldoUlt)+u)));
  return out;
}

// ===== CTL-4 · demanda líquida única por fazenda (DEM-01..07; PRD RN-006, AC-08, RN-008, CAL-01 l.4199–4201, RN-011, l.9184) =====
// Uma só conta para o Planejar safra (etapa 4, passo=demanda) e o Mapa › Insumos: demFazenda, com as ordens lidas do cenário compartilhado
// (cenOsDem, cenario.js). A Compra de insumos lê o espelho Python (dados2.demanda: mesmos eventos na mesma ordem; paridade em demanda_unica_test.py).
function calNf(x,d){ return Number(x||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
// quantidade a comprar com 0,01 da unidade: a solicitação leva este número e o valor sai dele (Planejar safra = Compra = Mapa; espelho dados2._r2)
function calR2(x){ return Math.round((Number(x)||0)*100)/100; }
function calNfa(x){ return Number(x||0).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:2}); }
function demTal(t){ return String(t||'').split('-')[0]; }   // talhão de um local da O.S. ('T1-B' → 'T1'; 'Pivô 13' fica)
// DEM-01 · a O.S. cobre, em cada atividade das chaves dela, as ocorrências do plano da safra dela nos talhões dela (o próprio cultivo ou as
// parcelas do talhão: dividir o talhão com o mesmo plano não muda a parte coberta). Fração coberta = área da O.S. ÷ área dessas ocorrências
// (máx. 1). occ: [{saf, k:'cultivo|atividade', a, local, tal, area}] · osd: cenOsDem · devolve {chave: {f: fração sem O.S., txt}}.
// Dano evitado: compra em dobro do que a O.S. já tem (Fungicida A 145,2 L na OS-0421).
function demRestante(osd, occ){ const cob={}, txt={};
  (osd||[]).forEach(o=>{ const ts={}; (o.loc||[]).forEach(t=>{ ts[t]=1; }); const ats=[];
    (o.chaves||[]).forEach(k=>{ const a=String(k).split('|')[1]; if(ats.indexOf(a)<0) ats.push(a); });
    ats.forEach(a=>{ const ks=(occ||[]).filter(x=>x.saf===o.saf&&x.a===a&&(ts[x.local]||ts[x.tal])); const tot=ks.reduce((s,x)=>s+(Number(x.area)||0),0); if(!(tot>0)) return;
      ks.forEach(x=>{ cob[x.k]=(cob[x.k]||0)+Math.min(1,(Number(o.area)||0)/tot);
        (txt[x.k]=txt[x.k]||[]).push(o.id+' cobre '+calNfa(o.area)+' de '+calNfa(tot)+' ha'+(ks.length>1?', rateados pela área':'')); }); }); });
  const fr={}; Object.keys(cob).forEach(k=>{ fr[k]={f:Math.max(0,1-cob[k]),txt:txt[k].join('; ')}; }); return fr; }
// DEM-02/03/04 · eventos das ordens para o insumo prod: cada ordem conta pelo que ainda vai tirar do almoxarifado (pendente de cenOsDem), na data
// máx(hoje, início da janela); é dona da safra dela; chave = ID da ordem (a reserva da mesma ordem conta uma vez). Ordem sem chave nunca some
// (dano evitado: compra a menos, MAP 17.500 kg da OS-0420, Ureia 1.140 kg da OS-0418); a linha avisa só quando o plano do mesmo talhão usa o
// mesmo produto (talProd[safra][talhão][produto]) — casar por coincidência seria vínculo inventado (RN-003).
function demOsEvs(osd, prod, saf, ordem, talProd){ const out=[]; const tp=talProd||{};
  (osd||[]).forEach(o=>{ (o.itens||[]).forEach(i=>{ if(i.p!==prod||!(i.q>1e-9)) return;
    const av=!(o.chaves||[]).length&&(o.loc||[]).some(t=>((tp[o.saf]||{})[demTal(t)]||{})[prod]);
    out.push({dt:o.dt,q:i.q,tipo:'dem',own:o.saf===saf,ord:ordem(o.saf),chave:o.id,t:o.t+(av?' · sem vínculo com o plano do talhão: se for o mesmo uso, retire o produto do plano do talhão (etapa 2)':''),
      calc:i.calc,loc:o.loc}); }); });
  return out; }
// DEM-05/06/07 · demanda por insumo da safra x.saf na fazenda x.faz: o plano sem a parte coberta por O.S. (DEM-01), as O.S. pelo pendente
// (DEM-02/03), as outras safras abertas da fazenda (agregadas por data, também sem a parte coberta), reservas, recebimentos e o físico apto
// da PRÓPRIA fazenda (DEM-07: estoque de outra fazenda não cobre; dano evitado: Glifosato 293 L a menos na Lagoa Grande).
// x: {saf, faz, hoje, viavel, ordem:{safra:índice}, nomes:{safra:nome}, occ, osd, reservas, recebDt, fisico:{insumo: físico apto da fazenda},
//    quar/quarRep:{insumo: quarentena com laudo pendente / reprovada}, quarRef:[{item,q,lote,doc,rep}] (cenEstDem),
//    sobra:[{item,q,t,faz}] custódia sem uso nas O.S. da fazenda (cenEstDem): entra no saldo inicial junto do físico apto (revisão do 853a6a8, achado 1)}
// occ: ocorrências das safras abertas da fazenda, na ordem cultivo → atividade: [{saf,k,a,local,tal,area,dt,nome,prods:[{nome,grupo,un,preco,dose,q,orig,laudo}]}]
//    (orig 'análise' ou 'sessão' e laudo: a origem da dose escrita na memória, R21 da análise de solo)
function demFazenda(x){ const m={}; const ord=(s)=>{ const i=(x.ordem||{})[s]; return i===undefined?99:i; };
  const occ=x.occ||[]; const osd=(x.osd||[]).filter(o=>o.faz===x.faz); const fr=demRestante(osd,occ); const tp={};
  occ.forEach(o=>{ const t=(tp[o.saf]||(tp[o.saf]={})); const p=(t[o.tal]||(t[o.tal]={})); (o.prods||[]).forEach(q=>{ p[q.nome]=1; }); });
  const novo=(nome,g,un,preco)=>m[nome]||(m[nome]={nome,grupo:g||'',un,preco:Number(preco)||0,plano:0,evs:[]});
  occ.forEach(o=>{ if(o.saf!==x.saf) return; const c=fr[o.k]; const f=c?c.f:1;
    (o.prods||[]).forEach(p=>{ const d=novo(p.nome,p.grupo,p.un,p.preco); d.plano+=p.q*f; if(!(f>1e-9)) return; const ar=o.area*f;
      d.evs.push({dt:o.dt||'',q:p.dose*ar,tipo:'dem',own:true,ord:ord(x.saf),chave:o.k,t:o.local+' · '+o.nome+((c&&f<1-1e-9)?' · parte sem O.S. ('+c.txt+')':''),
        calc:calNf(p.dose,2)+' '+p.un+'/ha'+(p.orig==='análise'?' (pela análise · '+p.laudo+')':(p.orig==='sessão'?' (ajustado pelo usuário)':''))+' × '+calNfa(ar)+' ha',loc:[o.local]}); }); });   /* origem da dose na memória (R21 da análise de solo) */
  osd.forEach(o=>{ if(o.saf!==x.saf) return; (o.itens||[]).forEach(i=>{ if(i.q>1e-9) novo(i.p,i.g,i.un,i.preco); }); });   // insumo que só a O.S. usa
  Object.values(m).forEach(d=>{ d.evs=d.evs.concat(demOsEvs(osd,d.nome,x.saf,ord,tp)); });
  Object.keys(x.ordem||{}).sort((a,b)=>x.ordem[a]-x.ordem[b]).forEach(s=>{ if(s===x.saf) return; const ag={}, ks=[];
    occ.forEach(o=>{ if(o.saf!==s) return; const c=fr[o.k]; const f=c?c.f:1; if(!(f>1e-9)) return;
      (o.prods||[]).forEach(p=>{ if(!m[p.nome]) return; const k=p.nome+'|'+o.dt; if(!ag[k]){ ag[k]={nome:p.nome,dt:o.dt||'',q:0,n:0,chaves:[]}; ks.push(k); }
        ag[k].q+=p.q*f; ag[k].n++; ag[k].chaves.push(o.k); }); });
    ks.forEach(k=>{ const a=ag[k]; m[a.nome].evs.push({dt:a.dt,q:a.q,tipo:'dem',own:false,ord:ord(s),chaves:a.chaves,t:((x.nomes||{})[s]||s)+' · '+a.n+(a.n>1?' usos':' uso')}); }); });
  Object.values(m).forEach(d=>{ const daFaz=(r)=>r.item===d.nome&&r.faz===x.faz;
    (x.reservas||[]).forEach(r=>{ if(daFaz(r)) d.evs.push({dt:r.dt,q:r.q,tipo:'res',own:false,ord:0,chave:r.chave,t:r.t}); });
    (x.recebDt||[]).forEach(r=>{ if(daFaz(r)) d.evs.push({dt:r.dt,q:r.q,tipo:'rec',own:false,ord:0,ref:r.ref,t:r.t}); });
    d.res=(x.reservas||[]).filter(daFaz).reduce((a,r)=>a+r.q,0); d.rec=(x.recebDt||[]).filter(daFaz).reduce((a,r)=>a+r.q,0);
    d.est=Number((x.fisico||{})[d.nome])||0;
    const cs=(x.sobra||[]).filter(daFaz); d.cust=cs.reduce((a,r)=>a+r.q,0); d.custT=cs.map(r=>calNfa(r.q)+' '+d.un+' · '+r.t);   // custódia sem uso (suprimento)
    // quarentena (revisão do 853a6a8, achado 2, S2; PRD 65.4; CAL-01 "Qualidade pendente"; DEMO-02): a parte com laudo pendente entra no saldo como
    // cobertura condicionada — a compra (liq) é a falta mesmo com ela liberada; cond = a parte da falta que só existe se o laudo reprovar (fica
    // visível, fora do total e sem trocar a primária). Reprovada (quarRep) não cobre: a falta é firme. Dano evitado: compra duplicada automática
    // (Semente de soja 58 W 15.456 kg · R$ 146.832 com a NF 4533 em quarentena).
    d.quarC=Number((x.quar||{})[d.nome])||0; d.quarRep=Number((x.quarRep||{})[d.nome])||0; d.quarRef=(x.quarRef||[]).filter(r=>r.item===d.nome);
    const op={hoje:x.hoje,viavel:x.viavel}; const cF=cal01(d.est+d.cust,d.evs,0,op); const c=d.quarC>1e-9?cal01(d.est+d.cust+d.quarC,d.evs,0,op):cF; d.cal=c;
    d.cond=d.quarC>1e-9?Math.max(0,calR2(calR2(cF.liq)-calR2(c.liq))):0; d.condFalta=d.cond>0.001?(cF.falta||''):'';
    d.liq=calR2(c.liq); d.falta=c.falta; d.antes=c.antes; d.tarde=c.tarde; d.valor=d.liq*d.preco; d.bruta=c.bruta; d.real=c.real; d.rup=c.rupRec; d.cob=c.cob;
    d.uso=d.evs.filter(e=>e.tipo==='dem'&&e.own&&e.dt&&e.dt>=(x.hoje||'')).map(e=>e.dt).sort()[0]||''; });   // 1º uso desta safra de hoje em diante
  return m; }
// DEM-05 · Mapa › Insumos: situação de cada insumo da fazenda no período (eventos até lim; sem lim, a safra toda) pela mesma projeção:
// Falta (necessidade líquida) · Pedido a receber (sem os recebimentos faltaria) · Estoque cobre. Entra o insumo com uso desta safra de hoje em
// diante no período. Devolve {insumo: [rótulo, cor ('red'|'yellow'|'ok'), detalhe, qualidade pendente junto da falta firme ('' sem ela)]}.
// Revisão do 16fb55e (ajuste 1, PRD 65.4): com falta firme E quarentena com laudo pendente, o rótulo segue a compra firme e a parte condicionada
// aparece à parte (4º item e detalhe, com quem decide), fora da compra e sem segunda ação (dano evitado: o Mapa esconder 40 kg aguardando laudo
// e o comprador decidir sem saber que eles podem virar falta).
function demSituacao(m, lim, hoje, viavel){ const st={}; const dm=(s)=>s?s.slice(8,10)+'/'+s.slice(5,7):''; const d4=(s)=>s?dm(s)+'/'+s.slice(0,4):'';
  Object.values(m||{}).forEach(d=>{ const evs=lim?d.evs.filter(e=>!e.dt||e.dt<=lim):d.evs; const own=evs.filter(e=>e.tipo==='dem'&&e.own&&(!e.dt||e.dt>=hoje)); if(!own.length) return;
    const s0=d.est+(Number(d.cust)||0), qc=Number(d.quarC)||0; const r=cal01(s0+qc,evs,0,{hoje,viavel}), r0=cal01(s0+qc,evs.filter(e=>e.tipo!=='rec'),0,{hoje,viavel}); const u=' '+d.un;
    const rF=qc>1e-9?cal01(s0,evs,0,{hoje,viavel}):r;   // sem a quarentena: falta condicionada à qualidade (revisão do 853a6a8, achado 2)
    const cq=qc>1e-9?Math.max(0,calR2(calR2(rF.liq)-calR2(r.liq))):0;   // a parte da falta que só existe se o laudo reprovar (a mesma conta de d.cond, no período)
    const rc=evs.filter(e=>e.tipo==='rec').sort((a,b)=>a.dt<b.dt?-1:(a.dt>b.dt?1:0))[0]; const ar=evs.filter(e=>e.tipo==='rec').reduce((a,e)=>a+e.q,0);
    const base='precisa de '+calNf(own.reduce((a,e)=>a+e.q,0))+u+' · estoque apto '+calNf(d.est)+u+((d.cust||0)>1e-9?' + '+calNf(d.cust)+u+' em custódia a devolver':'');
    const ctx=qc>1e-9?demCondTxt({quarC:qc,quarRef:d.quarRef,condFalta:rF.falta,un:d.un}):'';   /* motivo, responsável, prazo e fora da compra: o texto único da falta condicionada (integração V56) */
    if(r.liq>1e-9) st[d.nome]=['Falta '+calNf(r.liq)+u,'red',base+' · falta a partir de '+d4(r.falta)+' · Suprimentos compra na Compra de insumos'
      +(cq>0.001?' · se o laudo reprovar, faltam mais '+calNf(cq)+u+' · '+ctx:''),cq>0.001?'Qualidade pendente · '+calNf(cq)+u:''];
    else if(rF.liq>1e-9) st[d.nome]=['Qualidade pendente · '+calNf(rF.liq)+u,'yellow',base+' · se o laudo reprovar, falta a partir de '+d4(rF.falta)+' · '+ctx];
    else if(r0.liq>1e-9||r0.rupRec>1e-9) st[d.nome]=['Pedido a receber'+(rc?(rc.ref?' · '+rc.ref:'')+' · '+dm(rc.dt):''),'yellow',base+' · a receber '+calNf(ar)+u];
    else st[d.nome]=r.parcial?['Data pendente','yellow',base]:['Estoque cobre','ok',base];
    if(r.parcial) st[d.nome][2]+=' · projeção datada parcial · sem data: aguarda âncora · '+calNfa(r.pendentes.reduce((s,e)=>s+(Number(e.q)||0),0))+u; });
  return st; }
// DEM-05 · necessidade por talhão no Mapa: os eventos desta safra de hoje em diante; a O.S. de vários talhões é rateada pela área dos cultivos
// da safra em cada talhão (areaT[talhão]), e a soma dos talhões fecha com a fazenda. tid: local → talhão do mapa.
function demPorLocal(m, tid, areaT, hoje){ const out={};
  Object.values(m||{}).forEach(d=>d.evs.forEach(e=>{ if(e.tipo!=='dem'||!e.own||!(e.dt>=hoje)) return; const ls=e.loc||[]; if(!ls.length) return;
    const ar=ls.map(t=>Number((areaT||{})[tid(t)])||1); const s=ar.reduce((a,b)=>a+b,0);
    ls.forEach((t,i)=>{ const k=tid(t); (out[k]||(out[k]=[])).push({p:d.nome,q:e.q*ar[i]/s,un:d.un,dt:e.dt,orig:e.t}); }); }));
  return out; }
// DEM-09 · a solicitação já enviada × a demanda de agora (Planejar safra, etapa 4). Depois do envio a demanda pode baixar (O.S. cancelada,
// plano mudado): o insumo que a solicitação pede acima da necessidade líquida fica "Acima da demanda" e a atualização tira só a diferença
// (dano evitado: comprar o que a demanda já não pede). Com pedido já emitido a solicitação não muda: o excedente entra no estoque e a linha
// só avisa (cancelar pedido é decisão da Compra). Quantidades na unidade do insumo; tolerância de 0,01 (a mesma do complemento).
// d: {liq, rup} da demanda (ou nada, se ela não pede o insumo); sent: o que a solicitação pede. Devolve {t, c, dif, pend, sol}.
function demSolSit(d, sent, temSol, pedEmit){ const liq=Number(d&&d.liq)||0, rup=Number(d&&d.rup)||0, cond=Number(d&&d.cond)||0; sent=Number(sent)||0;
  if(temSol&&sent>liq+0.01) return {t:'Acima da demanda',c:'red',dif:sent-liq,pend:!pedEmit,sol:true};
  if(liq<=0.001&&cond>0.001) return {t:'Qualidade pendente',c:'yellow',dif:0,pend:false,sol:false,cond};   // PRD 65.4: falta condicionada, sem compra automática
  if(liq<=0.001&&rup>0.001) return {t:'Coberto pelo recebimento',c:'yellow',dif:0,pend:false,sol:false};
  if(liq<=0.001) return {t:'Coberto pelo estoque',c:'green',dif:0,pend:false,sol:false};
  if(temSol&&sent>=liq-0.01) return {t:'Em cotação',c:'blue',dif:0,pend:false,sol:true};
  if(temSol) return {t:'Complemento',c:'yellow',dif:liq-sent,pend:true,sol:true};
  return {t:'A enviar',c:'gray',dif:liq,pend:true,sol:false}; }
// itens da versão nova da solicitação: sobe o que a demanda pede a mais (complemento) e baixa o que ela pede a menos (sai com 0); com pedido
// emitido nada baixa. itens {insumo: quantidade}; dm {insumo: {liq}}. Devolve {it, novos, menos} (novos e menos: nomes dos insumos).
function demSolRevisar(itens, dm, pedEmit){ const it=Object.assign({},itens||{}); const novos=[], menos=[]; const L=(n)=>Number(((dm||{})[n]||{}).liq)||0;
  Object.keys(dm||{}).forEach(n=>{ if(L(n)>0.001&&L(n)>(Number(it[n])||0)+0.01){ novos.push(n); it[n]=L(n); } });
  if(!pedEmit) Object.keys(itens||{}).forEach(n=>{ if((Number(itens[n])||0)>L(n)+0.01){ menos.push(n); if(L(n)>0.001) it[n]=L(n); else delete it[n]; } });
  return {it,novos,menos}; }
// DEM-09 na Compra (revisão do CTL-4, achado 2) · insumos que a solicitação pede acima da demanda de agora, pela mesma regra do Planejar safra
// (demSolSit), para a Compra avisar nas etapas 2, 4 e 5 — sem trava: quem atualiza a solicitação é o Planejar safra (dano evitado: aprovar a
// compra do que a demanda já não pede, ex.: a Ureia da OS-0418 cancelada, R$ 3.534,00). m: demFazenda; itens: [{nome, nec}] da solicitação.
function demSolAcima(m, itens){ const out={}; (itens||[]).forEach(it=>{ const d=(m||{})[it.nome]; const s=demSolSit(d,it.nec,true,false);
  if(s.t==='Acima da demanda') out[it.nome]={dif:s.dif,liq:Number(d&&d.liq)||0}; }); return out; }
// DEM-08 · Compra, etapa 4: escolha padrão = a de menor custo que chega antes da falta; sem nenhuma a tempo, a que chega primeiro (empate: menor
// custo), sem justificativa obrigatória — não existe alternativa a tempo a justificar (AGENTS §4); o aviso "chega depois da falta" continua.
// props em ordem de custo (unit crescente), com {f, unit, chega, late}.
function cmpRef(props){ const ps=props||[]; const ok=ps.find(p=>!p.late); if(ok) return ok;
  return ps.slice().sort((a,b)=>(a.chega<b.chega?-1:(a.chega>b.chega?1:0))||(a.unit-b.unit))[0]||null; }
// justificativa obrigatória: a escolhida chega depois da falta havendo proposta a tempo, ou custa mais que a referência (dano: pagar mais ou faltar sem motivo registrado)
function cmpJust(ch, ref, props){ return !!(ch&&((ch.late&&(props||[]).some(p=>!p.late))||(ref&&ch.f!==ref.f&&ch.unit>ref.unit+1e-9))); }
// escolha sem justificativa: selo e motivo escritos (menor custo total; menor custo a tempo; sem nenhuma a tempo, a que chega primeiro)
function cmpEscolha(ch, ref, low, props){ const aTempo=(props||[]).some(p=>!p.late); if(!ch) return {selo:'',txt:''};
  if(low&&ch.f===low.f) return {selo:'Menor custo total',txt:'menor custo total'};
  if(aTempo) return {selo:'Menor custo a tempo',txt:'menor custo que chega a tempo'+(low?' ('+low.nome+' custa menos, mas chega depois da falta)':'')};
  if(ref&&ch.f===ref.f) return {selo:'Chega primeiro',txt:'a que chega primeiro (nenhuma proposta chega antes da falta)'};
  return {selo:'',txt:'chega depois da falta, como todas, e custa menos que a primeira a chegar'+(ref?' ('+ref.nome+')':'')}; }
