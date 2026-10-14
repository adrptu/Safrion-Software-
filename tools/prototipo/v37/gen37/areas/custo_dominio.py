# -*- coding: utf-8 -*-
"""Custo das O.S. agrícolas: fonte única do Mapa (camada Custos) e do Painel Agrícola (PAINEL-02, contrato 6166150698).

Previsto por talhão (PREV: plano da safra; sem plano, as O.S. emitidas no talhão), preço e custo de operação vêm do Mapa (areas.inicio);
o realizado é calculado aqui, sobre a projeção das ordens, pelas mesmas regras de antes:
  - preço ausente não vira zero: o item vai para pend e o cultivo fica parcial;
  - provisório = apontamentos aceitos (cenApSomado); conferido = os de status Conferido;
  - O.S. de vários talhões sem apontamento por talhão não é rateada: fica em sem_rateio, fora do R$/ha.
Ordem emitida na tela O.S. (fora de ORD) não entra no realizado, como no Mapa.
"""
import json

JS = r'''
// ===== custo das O.S. (custo_dominio.py): D = dados de custo (M no Mapa, CUSD no Painel) =====
function cusPreco(D,p){ if(D.preco[p]!==undefined) return D.preco[p]; for(const k in D.gen){ if(p.indexOf(k)===0) return D.preco[D.gen[k]]!==undefined?D.preco[D.gen[k]]:null; } return null; }
function cusOrdem(D,o){ const r={ins:0,op:0,ha:0,haConf:0,rs:0,rsConf:0,prevExec:0,pend:[]}; const op=(o.atv||{}).op||''; const cop=D.cop[op];
  if(cop===undefined) r.pend.push('Operação '+(op||'—')+' sem rendimento na safra: custo de operação não somado');
  const prHa=(o.ins||[]).reduce((s,x)=>{ const p=cusPreco(D,x.p); if(p===null){ r.pend.push('Sem preço: '+x.p+' (não somado)'); return s; } return s+x.dose*p; },0);
  (o.ap||[]).forEach(a=>{ if(!cenApSomado(a)) return; const ha=Number(a.ha)||0; let vi=0;   // duplicidade retida ou guardada não vira custo
    /* consumo informado sem preço não vira zero calado (Codex 6166518949, achado 2): entra em pend e torna o resultado parcial (Mapa e Painel) */
    if(a.cons&&Object.keys(a.cons).length) Object.keys(a.cons).forEach(p=>{ const pr=cusPreco(D,p); if(pr!==null) vi+=(Number(a.cons[p])||0)*pr; else if((Number(a.cons[p])||0)>0) r.pend.push('Sem preço: '+p+' (consumo não somado)'); }); else vi=prHa*ha;
    const vo=(cop||0)*ha; r.ins+=vi; r.op+=vo; r.ha+=ha; r.rs+=vi+vo; r.prevExec+=(prHa+(cop||0))*ha; if(a.st==='Conferido'){ r.haConf+=ha; r.rsConf+=vi+vo; } });
  r.pend=r.pend.filter((x,i,a)=>a.indexOf(x)===i); return r; }
// realizado do talhão t sobre as ordens projetadas osn; D.ord = [{id, tal:[talhões]}]
function cusTalhao(D,t,osn){ const R={ins:0,op:0,ha:0,haConf:0,rs:0,rsConf:0,prevExec:0,pend:[],ords:[],shared:[]};
  D.ord.forEach(mo=>{ if(mo.tal.indexOf(t)<0) return; const o=osn.find(x=>x.id===mo.id); if(!o) return; const c=cusOrdem(D,o); if(!c.ha) return;
    if(mo.tal.length>1){ R.shared.push({o,c,tal:mo.tal}); return; }
    ['ins','op','ha','haConf','rs','rsConf','prevExec'].forEach(k=>{ R[k]+=c[k]; }); R.ords.push({o,c}); c.pend.forEach(p=>R.pend.push(o.id+' · '+p)); });
  return R; }
// PAINEL-02 · custo por cultura para o Painel (contrato 6166150698; revisão Codex 6166518949). Agrupamento: fazenda · safra · cultura (identidade
// estável faz|saf|cultura + talhões; não separa cultivar nem ciclo). Sem comando nem mutação; null = Sem dados.
//   orcado_rs: previsto do plano dos talhões (talhão sem plano em sem_orc; R$/ha orçado null);
//   real_total_rs = real_prov_rs (apontamentos aceitos ainda não conferidos) + real_conf_rs (conferidos): confirmar move de um para o outro sem mudar o total;
//   real_rs_ha = real_total_rs / area_ha (custo acumulado por hectare PLANTADO, comparável ao orçado por ha); null com área 0 ou ausente;
//   ha_exec e desvio_exec_pct: execução (soma das passagens apontadas) contra o previsto da mesma área executada, a conta da camada Custos do Mapa;
//     não é o comparativo da safra; null quando parcial (preço ausente ou ordem fora da cobertura);
//   fora: ordens emitidas na tela sem vínculo de talhão no custo (fora da cobertura, com o realizado delas), nunca somadas caladas.
function agrCustoRef(c,rec) { rec=rec||{};
 if(typeof CUSD==='undefined'||typeof osProjecaoEstado!=='function') return null;
 let osn=null; try { osn=osProjecaoEstado(c,id=>/^OB-/.test(id)); } catch(e) { osn=null; } if(!osn) return null;
 const r2=x=>Math.round(x*100)/100, G={}, sem={}, noOrd=new Set(CUSD.ord.map(o=>o.id));
 Object.keys(CUSD.tal).forEach(t=>{ const x=CUSD.tal[t]; if((rec.faz&&x.faz!==rec.faz)||(rec.saf&&x.saf!==rec.saf)) return;
  const k=x.faz+'|'+x.saf+'|'+x.cultura;
  const g=G[k]||(G[k]={id:k,cultura:x.cultura,faz:x.faz,saf:x.saf,talhoes:[],area_ha:0,orcado_rs:0,sem_orc:[],tot:0,conf:0,ha_exec:0,prev_exec_rs:0,pend:[]});
  g.talhoes.push(t); g.area_ha+=x.area; const P=CUSD.prev[t];
  if(P&&P.fonte==='plano') g.orcado_rs+=P.tot; else g.sem_orc.push(t);
  ((P&&P.pend)||[]).forEach(p=>g.pend.push(t+' · '+p));
  const R=cusTalhao(CUSD,t,osn); g.tot+=R.rs; g.conf+=R.rsConf; g.ha_exec+=R.ha; g.prev_exec_rs+=R.prevExec; R.pend.forEach(p=>g.pend.push(p));
  R.shared.forEach(s=>{ sem[s.o.id]={os:s.o.id,talhoes:s.tal,rs:r2(s.c.rs)}; }); });
 const fora=osn.filter(o=>!noOrd.has(o.id)&&(!rec.faz||o.faz===rec.faz)&&(!rec.saf||o.saf===rec.saf)).map(o=>({os:o.id,talhao:o.talhao||'',rs:r2(cusOrdem(CUSD,o).rs),motivo:'ordem emitida na tela sem vínculo de talhão no custo'}));
 const cultivos=Object.values(G).map(g=>{ const pend=g.pend.filter((p,i,a)=>a.indexOf(p)===i), parcial=pend.length>0||g.sem_orc.length>0||fora.some(f=>f.rs>0);
  return {id:g.id,cultura:g.cultura,faz:g.faz,saf:g.saf,talhoes:g.talhoes,area_ha:r2(g.area_ha),
   orcado_rs:g.sem_orc.length&&!g.orcado_rs?null:r2(g.orcado_rs),orcado_rs_ha:g.sem_orc.length||!(g.area_ha>0)?null:r2(g.orcado_rs/g.area_ha),sem_orc:g.sem_orc,
   real_total_rs:r2(g.tot),real_prov_rs:r2(g.tot-g.conf),real_conf_rs:r2(g.conf),real_rs_ha:g.area_ha>0?r2(g.tot/g.area_ha):null,
   ha_exec:r2(g.ha_exec),prev_exec_rs:r2(g.prev_exec_rs),desvio_exec_pct:(!parcial&&g.prev_exec_rs>0)?Math.round((g.tot-g.prev_exec_rs)/g.prev_exec_rs*1000)/10:null,
   parcial,pend}; });
 return {cultivos,sem_rateio:Object.values(sem),fora};
}
'''


def dados():
    """Dados de custo do Mapa (mesmos PRECO, _GEN, COP, PREV e ORD) + fazenda, safra e cultura de cada talhão com cultivo na safra aberta."""
    import areas.inicio as I
    import dados2 as D2
    import dados_lagoa_safra as DLS
    tal = {}
    def add(t, faz, cultura, area):
        x = tal.setdefault(t, dict(faz=faz, saf='2026/27', cultura=cultura, area=0))
        assert x['cultura'] == cultura and x['faz'] == faz, f'talhão {t} com duas culturas na safra'
        x['area'] += area
    for c in D2.CULTIVOS['S2627']:
        add(c['local'].split('-')[0], c.get('fazenda', 'Santa Rita'), c['cultura'], c['area'])
    for c in DLS.CULTIVOS:
        add(DLS.PID_DE[c['local']], 'Lagoa Grande', c['cultura'], c['area'])
    assert set(tal) <= set(I.PREV), 'talhão com cultivo sem previsto no Mapa'
    return dict(preco=I.PRECO, gen=I._GEN, cop=I.COP,
                prev={t: dict(fonte=p['fonte'], tot=p['tot'], base=p['base'], pend=p['pend']) for t, p in I.PREV.items()},
                ord=[dict(id=o['id'], tal=o['tal']) for o in I.ORD], tal=tal)


def js_prefixo():
    return 'const CUSD = ' + json.dumps(dados(), ensure_ascii=False).replace('</', '<\\/') + ';\n' + JS
