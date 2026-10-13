// ===== CAL-01 · Necessidade líquida por data (PRD v3.9) — a mesma memória de cálculo no Planejar safra (etapa 6) e na Compra de insumos =====
// Convenção única: o físico apto (fora quarentena) INCLUI as reservas; cada necessidade entra uma vez. Reserva da mesma demanda (chave
// cultivo|atividade presente na demanda) não é subtraída de novo; reserva para outro destino entra como demanda na data dela.
// Recebimento só cobre usos na data dele ou depois. A reposição proposta entra no saldo projetado: faltas sucessivas não se acumulam.
// opt {hoje, viavel} (AAAA-MM-DD): uso planejado antes de hoje já foi realizado ou entregue à O.S. — saiu do físico e da demanda residual (só
// aparece na memória). Falta antes da chegada viável de uma compra nova é ruptura: os recebimentos até lá a cobrem (a mais antiga primeiro) e o
// que sobrar vira reposição na data viável. Sem opt, a reposição entra na própria data da falta.
// ev: {dt:'AAAA-MM-DD', q, tipo:'rec'|'res'|'dem', own:bool (é da solicitação calculada), ord:ordem global da origem, t:texto, chave|chaves, ref}
// No mesmo dia: recebimento, chegada viável, reserva e as demandas na ordem global das safras (igual em todas as telas: a falta não é atribuída duas vezes).
function cal01(fis, evs, seg, opt){
  seg=Number(seg)||0; opt=opt||{}; const hoje=opt.hoje||'', via=opt.viavel||''; const ks={};
  (evs||[]).forEach(e=>{ if(e.tipo!=='dem') return; if(e.chave) ks[e.chave]=1; (e.chaves||[]).forEach(k=>{ ks[k]=1; }); });
  let real=0, nreal=0; const E0=[];
  (evs||[]).forEach((e,i)=>{ if(e.tipo==='dem'&&hoje&&e.dt&&e.dt<hoje){ if(e.own){ real+=Number(e.q)||0; nreal++; } return; } E0.push(Object.assign({i:i},e)); });
  if(via) E0.push({i:1e9,dt:via,q:0,tipo:'via',ord:0});
  const pri=(e)=>e.tipo==='rec'?0:(e.tipo==='via'?1:(e.tipo==='res'?2:3));
  const E=E0.sort((a,b)=>(a.dt<b.dt?-1:(a.dt>b.dt?1:0))||(pri(a)-pri(b))||((a.ord||0)-(b.ord||0))||(a.i-b.i));
  let ult=''; E.forEach(e=>{ if(e.tipo==='dem'&&e.own&&e.dt>ult) ult=e.dt; });
  let saldo=Number(fis)||0, bruta=0, rec=0, liq=0, tot=0, antes=0, falta=null, faltaTot=null, saldoUlt=null, rup=0, rupVia=0, cob=null; const L=[]; const bk=[];
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
    real:real,nreal:nreal,hoje:hoje,via:via,rup:rup,rupRec:Math.max(0,rup-rupVia),cob:cob,linhas:L};
}
// memória em linhas curtas (painel de origem do insumo), como um extrato por data: estoque apto, o já realizado, cada movimento até o último
// uso da safra (ou até a ruptura ser coberta) e o resultado. Linha com a data no início ("25/09/2026 · T1-A · Dessecação pré-plantio · 2,00 L/ha × 160 ha = 320,0 L → saldo 980 L").
function cal01Memo(r, o){ o=o||{}; const u=' '+(o.un||'');
  const n=(x)=>Number(x||0).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:1});
  const n1=(x)=>Number(x||0).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1});
  const d=(s)=>s?String(s).slice(8,10)+'/'+String(s).slice(5,7)+'/'+String(s).slice(0,4):'—';
  const out=['Estoque apto hoje: '+n(r.fis)+u+(o.res?' (inclui '+n(o.res)+u+' reservados)':'')+(o.quar?' · '+n(o.quar)+u+' em quarentena não contam até o laudo':'')];
  if(r.real>1e-9) out.push('Realizado antes de '+d(r.hoje)+' · '+r.nreal+(r.nreal>1?' usos':' uso')+' · '+n(r.real)+u+' · fora do estoque e da demanda');
  r.linhas.filter(l=>l.ate).forEach(l=>{ const sx=' → saldo '+n(l.saldo)+u; const t=d(l.dt)+' · '+(l.t||'Uso')+' · ';
    if(l.tipo==='rec') out.push(t+'+'+n1(l.q)+u+sx+(l.cobre>1e-9?' · cobre a ruptura':''));
    else if(l.tipo==='via') out.push(t+'+'+n1(l.q)+u+sx);
    else if(l.tipo==='res0') out.push(t+n1(l.q)+u+' da mesma demanda, contados uma vez');
    else if(l.tipo==='dem') out.push(t+(l.calc?l.calc+' = ':'')+n1(l.q)+u+sx+(l.nec>1e-9?' · falta '+n(l.nec)+u:'')+(l.rup>1e-9?' · ruptura '+n(l.rup)+u:''));
    else out.push(t+'−'+n1(l.q)+u+sx); });
  out.push(r.liq>1e-9?('Necessidade líquida = soma das faltas desta safra = '+n(r.liq)+u+' · falta a partir de '+d(r.falta))
    :(r.rupRec>1e-9?('Sem compra nova · ruptura de '+n(r.rupRec)+u+' de '+d(r.falta)+' a '+d(r.cob)+', coberta pelo recebimento')
    :('Sem falta nesta safra · saldo depois do último uso: '+n(r.saldoUlt==null?r.saldo:r.saldoUlt)+u)));
  return out;
}
