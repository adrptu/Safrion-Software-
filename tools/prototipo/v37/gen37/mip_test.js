// Teste unitário do núcleo MIP (mip.js) com o JavaScriptCore do macOS: python3 mip_unit_test.py
let OK=0, FAIL=0; function chk(n,c,x){ if(c){OK++; print('OK   '+n);} else {FAIL++; print('FALHA '+n+' '+(x===undefined?'':JSON.stringify(x)));} }
const S0=()=>mipGet(); const R=(id)=>mipRes(S0().vis[id],S0());
chk('VIS-011: média 13,0 com 13 válidos (ponto 11 em recoleta) → foco', Math.abs(R('VIS-011').media-13)<1e-9 && R('VIS-011').val===13 && R('VIS-011').kr==='foco', R('VIS-011'));
chk('VIS-013: 5,1 / 4 adultos/folíolo · acima do NC (R5)', R('VIS-013').k==='acima' && /^5,1 \/ 4 adultos\/folíolo · 128 % do NC$/.test(R('VIS-013').txt), R('VIS-013').txt);
chk('resultados da semente', ['VIS-054','VIS-053','VIS-016','VIS-014','VIS-017','VIS-015','VIS-008','VIS-055'].map(i=>R(i).k).join()==='perto,foco,sinc,coleta,programada,abaixo,perto,foco', ['VIS-054','VIS-053','VIS-016','VIS-014','VIS-017','VIS-015','VIS-008','VIS-055'].map(i=>R(i).k));
const c0=cenGet();
chk('VIS-051 em controle pela OS-0504 do cenário', mipSit(S0(),S0().vis['VIS-051'],c0).k==='controle' && mipProx(S0(),S0().vis['VIS-051'],c0).h==='OS.dc.html#OS-0504');
chk('VIS-051: alerta de rotação IRAC 6 e colheita suspensa (mamão, carência 14 d)', (()=>{ const k=mipChecks(S0(),S0().vis['VIS-051'],{kind:'controlar',prod:'abamectina-18-ec',dose:0.5,area:86,data:'2026-09-24',os:'OS-0504'},c0); return k.al.some(x=>/Rotação: mesmo grupo IRAC 6/.test(x)) && /suspensa até 08\/10/.test(k.cond); })());
const v13=S0().vis['VIS-013']; const L=mipElig(v13);
chk('feijão × mosca-branca: só os 4 registrados', L.map(x=>x.nome).join()==='Ciantraniliprole 100 OD,Acaricida D,Inseticida B,Piriproxifem 100 EC', L.map(x=>x.nome));
let k=mipChecks(S0(),v13,{kind:'controlar',prod:'inseticida-b',dose:1,area:95,data:'2026-09-24'},c0);
chk('Inseticida B: alerta de rotação IRAC 1B, sem trava', !k.tr.length && k.al.some(x=>/IRAC 1B/.test(x)), k);
k=mipChecks(S0(),v13,{kind:'controlar',prod:'acaricida-d',dose:0.5,area:95,data:'2026-09-28'},c0);
chk('Acaricida D em 28/09: trava de carência (14 d passa da colheita 10/10)', k.tr.some(x=>/Carência de 14 dias passa da colheita prevista \(10\/10\): aplicar até 26\/09/.test(x)), k.tr);
k=mipChecks(S0(),v13,{kind:'controlar',prod:'ciantraniliprole-100-od',dose:0.8,area:95,data:'2026-09-24'},c0);
chk('dose acima da bula trava', k.tr.some(x=>/Dose fora da bula: 0,5–0,75 L\/ha/.test(x)), k.tr);
let r=mipEmitir(null,'VIS-013',{kind:'controlar',prod:'ciantraniliprole-100-od',dose:0.5,area:95,data:'2026-09-24'});
const c1=cenGet(); const o=c1.ordens['OS-0440'];
chk('emitir: OS-0440 em A liberar com Ciantraniliprole 47,5 L', !r.erro && o && o.etapa==='A liberar' && o.ins[0].p==='Ciantraniliprole 100 OD' && Math.abs(o.ins[0].tot-47.5)<1e-9 && o.osc.novo.keys[0]==='mip|VIS-013|feijao-mosca', r);
chk('emitir: DIA-009 registrada, REC-015 com RA-0142, decisão na VIS-013', S0().dia['DIA-009'].sit==='Registrada' && S0().rec['REC-015'].ra==='RA-0142' && S0().vis['VIS-013'].dec.os==='OS-0440');
chk('não duplica a O.S. da mesma vistoria', !!mipEmitir(null,'VIS-013',{kind:'controlar',prod:'ciantraniliprole-100-od',dose:0.5,area:95,data:'2026-09-24'}).erro);
r=mipMudar(null,s=>mipMonitorar(s,'VIS-015',''));
chk('seguir monitorando (abaixo do NC): VIS-018 programada para 29/09', !r.erro && S0().vis['VIS-018'] && S0().vis['VIS-018'].data==='2026-09-29' && S0().vis['VIS-018'].est==='programada' && S0().vis['VIS-015'].dec.t==='monitorar', r);
r=mipMudar(null,s=>mipNovaVis(s,'T7','mamao-acaro','2026-09-24','Marcos','mapa'));
chk('programar no T7: VIS-019 com 20 pontos', !r.erro && S0().vis['VIS-019'].npts===20, r);
r=mipMudar(null,s=>mipNovaVis(s,'T7','mamao-acaro','2026-09-25','Marcos','mapa'));
chk('não duplica talhão × alvo aberto', !!r.erro && /VIS-019 já está aberta para T7/.test(r.erro), r);
r=mipMudar(null,s=>mipNovaVis(s,'P1','mamao-acaro','2026-09-25','Marcos','mapa'));
chk('combinação fora do protocolo é recusada', !!r.erro && /não está no protocolo de feijão/.test(r.erro), r);
r=mipEmitir(null,'VIS-053',{kind:'erradicar',area:1,data:'2026-09-24'});
chk('meleira: O.S. de erradicação OS-0441 sem produto', !r.erro && cenGet().ordens['OS-0441'] && cenGet().ordens['OS-0441'].ins.length===0 && S0().vis['VIS-053'].dec.t==='erradicar', r);
r=mipMudar(null,s=>mipColetar(s,'VIS-014','5',true));
chk('app: ponto 10 da VIS-014 registrado', !r.erro && S0().vis['VIS-014'].pts[9].v===5, r);
r=mipMudar(null,s=>mipConcluir(s,'VIS-014'));
chk('concluir com 10 de 14 → coleta incompleta', !r.erro && R('VIS-014').k==='incompleta', [r,R('VIS-014').k]);
r=mipMudar(null,s=>mipSinc(s,'VIS-016')); const r16=R('VIS-016');
chk('sincronizar VIS-016: 6 de 12 → incompleta; decidir com 6 → acima do NC', !r.erro && r16.k==='incompleta' && (mipMudar(null,s=>mipParcial(s,'VIS-016')), R('VIS-016').k==='acima'), [r, r16.k, R('VIS-016').k]);
// ---------- correções do parecer de 03/10 ----------
mipReset(); cenReset(); const C=()=>cenGet();
// foco monotônico: mais reboleiras nunca rebaixam o resultado (mamão × ácaro-rajado, NC 15, 20 pontos)
const vf=(n)=>{ const v=JSON.parse(JSON.stringify(S0().vis['VIS-008'])); v.pts.forEach((q,i)=>{ q.v=i<n?30:0; q.ok=true; q.rec=false; }); return mipRes(v); };
chk('foco: 6 reboleiras (média 9,0) e 7 reboleiras (média 10,5) ficam "foco"; 7 > 30 % é reboleira larga', vf(6).kr==='foco' && !vf(6).larga && vf(7).kr==='foco' && vf(7).larga===true && vf(10).kr==='acima', [vf(6).kr,vf(7).kr,vf(10).kr]);
// atraso de ritmo por talhão × alvo, visível na situação
const sa=(id)=>mipSit(S0(),S0().vis[id],C());
chk('VIS-060 e VIS-006: "Vistoria atrasada" com "Programar vistoria"; VIS-012 seguida pela VIS-015 sem atraso', sa('VIS-060').k==='atrasada' && /17\/09 · 6 dias/.test(sa('VIS-060').sub)
  && sa('VIS-006').k==='atrasada' && /11\/09 · 12 dias/.test(sa('VIS-006').sub) && mipProx(S0(),S0().vis['VIS-060'],C()).t==='Programar vistoria' && sa('VIS-012').k==='encerrada', [sa('VIS-060'),sa('VIS-006').sub,sa('VIS-012').k]);
chk('Mapa (7 dias) do T7 mostra a VIS-008 perto do NC, igual ao AG-01', (mipDoTal(S0(),'T7',7,C())[0]||{v:{}}).v.id==='VIS-008' && mipDoTal(S0(),'T7',7,C())[0].S.k==='perto');
// O.S. cancelada sem execução: aplicação fora do nº máximo e da rotação; mesmo DIA na nova decisão; receituário antigo cancelado
let e1=mipEmitir(null,'VIS-013',{kind:'controlar',prod:'inseticida-b',dose:1,area:95,data:'2026-09-24'});
cenMudar(null,c=>{ c.ordens['OS-0440'].etapa='Canceladas'; return {msg:''}; });
k=mipChecks(S0(),S0().vis['VIS-013'],{kind:'controlar',prod:'inseticida-b',dose:1,area:95,data:'2026-09-24'},C());
chk('cancelar a OS-0440: Inseticida B sem trava de nº máximo e rotação citando 08/09 (não a cancelada)', !e1.erro && !k.tr.length && k.al.some(x=>/08\/09 · Inseticida B/.test(x)) && !k.al.some(x=>/24\/09/.test(x)), [e1,k]);
chk('histórico mostra a aplicação da OS-0440 como cancelada', mipHist(S0(),'P1',C()).some(x=>/OS-0440/.test(x.sub) && x.ch==='cancelada'));
let e2=mipEmitir(null,'VIS-013',{kind:'controlar',prod:'ciantraniliprole-100-od',dose:0.5,area:95,data:'2026-09-24'});
const s2=S0();
chk('decidir de novo: mesmo DIA-009 → REC-019/RA-0143/OS-0441; REC-015 "Cancelado" substituído pelo REC-019', !e2.erro && e2.os==='OS-0441' && s2.vis['VIS-013'].dia==='DIA-009' && s2.dia['DIA-009'].rec==='REC-019'
  && s2.rec['REC-019'].ra==='RA-0143' && s2.rec['REC-015'].sit==='Cancelado' && s2.rec['REC-015'].subst==='REC-019' && !s2.dia['DIA-011'], [e2, s2.dia['DIA-009'], s2.rec['REC-015']]);
// erradicação: área do foco não passa do talhão
k=mipChecks(S0(),S0().vis['VIS-055'],{kind:'erradicar',area:999,data:'2026-09-24'},C());
// SINT-T01: a área vem da semente (MIPD.tal ← dados_lagoa_fonte), sem literal de área
const A22=MIPD.tal['PV22'].area, MSG22='Área maior que o talhão ('+mipN(A22,2)+' ha).';
chk('erradicação com 999 ha no Pivô 22 ('+mipN(A22,2)+' ha) trava', A22>0 && A22<999 && k.tr.indexOf(MSG22)>=0, k.tr);
// app: contagem impossível, correção, recoleta e reabertura da coleta incompleta
r=mipMudar(null,s=>mipColetar(s,'VIS-014','500',true));
chk('500 em "% folíolos com ácaro" é recusado', !!r.erro && /passa de 100/.test(r.erro), r);
r=mipMudar(null,s=>mipColetar(s,'VIS-014','12',false));
chk('ponto 10 com GPS fora vai para recoleta', !r.erro && S0().vis['VIS-014'].pts[9].rec===true, r);
r=mipMudar(null,s=>mipCorrigir(s,'VIS-014',8,'2',true));
chk('corrigir o ponto 8 (20 → 2)', !r.erro && S0().vis['VIS-014'].pts[7].v===2 && /20 → 2/.test(r.msg), r);
r=mipMudar(null,s=>mipConcluir(s,'VIS-014'));
chk('concluir com 10 de 14 → coleta incompleta, coletável no app', !r.erro && R('VIS-014').k==='incompleta' && mipColetavel(S0().vis['VIS-014']) && mipAlvoPt(S0().vis['VIS-014']).n===11, r);
r=mipMudar(null,s=>mipColetar(s,'VIS-014','5',true));
chk('"Completar coleta": o app reabre a VIS-014 no ponto 11', !r.erro && S0().vis['VIS-014'].est==='coleta' && /reaberta · Ponto 11 registrado/.test(r.msg), r);
['5','5','5'].forEach(x=>mipMudar(null,s=>mipColetar(s,'VIS-014',x,true)));
chk('depois dos pontos sem contagem, o app pede a recoleta do ponto 10', mipAlvoPt(S0().vis['VIS-014']).n===10 && mipAlvoPt(S0().vis['VIS-014']).rec===true);
r=mipMudar(null,s=>mipColetar(s,'VIS-014','10',true));
chk('recoleta do ponto 10 entra na média', !r.erro && /Ponto 10 recoletado/.test(r.msg) && R('VIS-014').rec===0 && R('VIS-014').falt===0, r);
print('RESULTADO '+OK+'/'+(OK+FAIL));
