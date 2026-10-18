// EX-55 F1 · ordens do mapa: fonte única do Mapa da fazenda (IN-04) e do mapa embutido da O.S. (visão Mapa).
// mcOrdsCen é o antigo mapOrdsCen do IN-04 (areas/inicio.py), movido sem mudar a regra: registro do mapa (mapa_ordens.py) + cenário
// compartilhado (fase, realizado, saldo, custódia e selos iguais às telas O.S., Estoque e App). mcOrdsBase acrescenta as O.S. do cenário
// que o registro do mapa não tem (as de demonstração e as emitidas no protótipo), com os talhões da ordem e o prazo pela janela.
// Depende de cenario.js (cenPodeEncerrar) e de mapa_camadas.js (mc_nfx).
function mc_idGeo(t){ const m=/^PV(\d+)$/.exec(t); return m?'Pivô '+Number(m[1]):t; }   // chave do IN-04 (PVxx) → contorno (geo_talhoes)
function mc_geoId(n){ const m=/^Pivô (\d+)$/.exec(n); return m?'PV'+String(m[1]).padStart(2,'0'):String(n||'').replace(/-[A-Z0-9]+$/,''); }   // contorno → chave do IN-04 (parcela T1-A → T1)
// irrigação só com água é do módulo Irrigação (IR-03): fica fora da camada O.S. e das contagens de ordens; aparece na camada Irrigação
function mc_irrAgua(o){ return /^Irrigação/.test(o.tipo||''); }
// prazo de uma O.S. fora do registro do mapa: pela data final da janela contra o "hoje" da demonstração; sem data, "sem prazo" (nunca "no prazo")
function mc_pzJanela(fim,hoje,fase){ if(fase==='Encerradas'||fase==='Canceladas') return 'encerrada'; const f=/^\d{4}-\d{2}-\d{2}/.test(String(fim||''))?String(fim).slice(0,10):'';
  if(!f||!hoje) return 'sem prazo'; const d=Math.round((Date.parse(f)-Date.parse(hoje))/864e5);
  return d<0?'atrasada':(d===0?'vence hoje':(d<=3?'até 3 dias':'no prazo')); }
function mc_mapSc(it){ const m=/saco (\d+) kg/.exec(it.emb||''); return (m&&it.un==='kg')?mc_nfx(it.custodia/Number(m[1]),0)+' sc':mc_nfx(it.custodia,it.custodia%1?1:0)+' '+it.un; }
// liberação pelo agrônomo: pendente = ordem A liberar no cenário (a ação 'lib' só existe em ordem com produto); liberada, sai da contagem
function mc_inPendLib(c,id){ const co=c&&c.ordens?c.ordens[id]:null; return !!co&&co.etapa==='A liberar'; }
function mc_mapItVis(co,it){ if(typeof CEN_BAIXA_NO_SINAL!=='undefined') return it;
  const q=Math.min((co.ap||[]).filter(a=>a.sinc===false).reduce((s,a)=>s+(Number((a.cons||{})[it.prod])||0),0),it.consumido||0);
  return q>1e-9?Object.assign({},it,{consumido:it.consumido-q,custodia:it.custodia+q}):it; }
// registro do mapa + as O.S. da projeção (osProjecao) que ele não tem; os campos são os do registro (mapa_ordens.ordens)
function mcOrdsBase(ord0,proj,hoje){ const tem=new Set(ord0.map(o=>o.id));
  const extra=(proj||[]).filter(r=>r&&/^OS-/.test(r.id)&&!tem.has(r.id)).map(r=>{ const ts=(r.talhoes||[]).map(t=>t.nome||t.id).filter(Boolean);
    const tal=[...new Set((ts.length?ts:String(r.talhao||'').split('+')).map(n=>mc_geoId(String(n).trim())).filter(Boolean))];
    return {id:r.id,tal,tipo:r.tipo||'',fase:r.etapa,selos:(r.selos||[]).map(s=>Array.isArray(s)?s:[s.t,s.c||'yellow']),area:Number(r.area)||0,rz:Number(r.realizado)||0,suf:'',
      jan:r.janela||'',real:'',saldo:Number(r.saldo)||0,resp:r.resp||'',pz:mc_pzJanela(r.fim,hoje,r.etapa),h:'OS.dc.html#'+r.id,saf:r.saf||'2026/27',doCen:true}; });
  return ord0.concat(extra); }
function mcOrdsCen(c,base){
  return base.map(o=>{ const co=c&&c.ordens?c.ordens[o.id]:null; const x=Object.assign({},o,{selos:o.selos.slice()});
    let cust=[];
    if(co&&co.selos) x.selos=co.selos.map(s=>[s.t,s.c||'yellow']);
    if(co){ x.fase=co.etapa; x.saldo=co.saldo||0; const area=co.area||o.area; x.rz=co.realizado||0; x.area=area;
      let real=mc_nfx(co.realizado||0,(co.realizado||0)%1?1:0)+'/'+mc_nfx(area)+' ha'; if(co.realizado>0&&co.saldo>0) real+=' · saldo '+mc_nfx(co.saldo,co.saldo%1?1:0)+' ha';
      if(o.suf) real+=' · '+o.suf;
      const r=co.req&&c.reqs?c.reqs[co.req]:null; cust=r?r.itens.map(i=>mc_mapItVis(co,i)).filter(i=>i.custodia>0.001):[];
      if(cust.length) real+=' · '+cust.map(mc_mapSc).join(' + ')+' em custódia';
      if((co.ap||[]).some(a=>a.sinc===false)) real+=' · apontamento aguardando sinal';
      x.real=real;
      if(!cust.length) x.selos=x.selos.filter(s=>!/^Sobras a receber/i.test(s[0])); }
    let bq='';
    if(co&&co.etapa==='Em conferência'){ try{ bq=cenPodeEncerrar(c,o.id)||''; }catch(e){ bq=''; } x.selos=x.selos.filter(s=>!/^Aguardando sinal do app/.test(s[0]));
      if(/^Carga a pesar/.test(bq)){ if(!x.selos.some(s=>s[0]==='Carga a pesar')) x.selos=x.selos.concat([['Carga a pesar','yellow']]); }   /* colheita (R-18): não é sobra em custódia */
      else if(/sinal/.test(bq)) x.selos=x.selos.filter(s=>!/^Sobras a receber/i.test(s[0])).concat([['Aguardando sinal do app','yellow']]);
      else if(bq){ const t=/^Sobra em custódia/.test(bq)?'Sobras a receber':(/^Consumo em conferência/.test(bq)?'Consumo em conferência':(/duplicidade/.test(bq)?'Apontamento em conferência':''));   /* o selo do bloqueio que existe; a divergência de dose já vem do cenário (revisão DOM achado 3) */
        if(t&&!x.selos.some(s=>s[0]===t)) x.selos=x.selos.concat([[t,'yellow']]); } }
    if(x.fase!=='A liberar') x.selos=x.selos.filter(s=>!/^Aguardando(?! sinal do app)/.test(s[0]));
    if(x.fase==='Encerradas'||x.fase==='Canceladas') x.pz='encerrada';
    const a=o.act; x.act=(!a||(a.c==='ag'&&!mc_inPendLib(c,o.id))||(a.c==='cust'&&co&&!cust.length))?null:a;
    if(bq&&!/sinal/.test(bq)&&cust.length&&!x.act) x.act={t:'Receber sobras',h:'EST.dc.html',k:'op',c:'cust'};
    return x; }); }
if (typeof module !== 'undefined') module.exports = { mc_idGeo, mc_geoId, mc_irrAgua, mc_pzJanela, mcOrdsBase, mcOrdsCen };
