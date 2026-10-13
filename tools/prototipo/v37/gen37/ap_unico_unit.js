// CTL-2 · Frente A (AP-ÚNICO): o mesmo turno apontado na web (O.S. e Mapa) e no app conta uma vez (PRD 8.5 l.3017-3036; OSDIA-03/04/06;
// DEMO-11 l.4751; CMD-09; ENG-021). Node, sem navegador: o executor ap_unico_test.py (modo unit) monta cenario.js + JS_NUCLEO da O.S. + OSD.
// Casos P/D/N/W/F/R do desenho e C1–C11b do cético (CONTROLE-01-A §5).
const R=[]; function ok(n,c,info){ R.push({n,ok:!!c,info:c?'':JSON.stringify(info===undefined?'':info).slice(0,700)}); }
const caso=(f)=>{ try{ f(); }catch(e){ R.push({n:'ERRO no caso '+(R.length+1)+': '+String(e.message||e),ok:false,info:String(e.stack||'').slice(0,300)}); } };
const TRY=(f)=>{ try{ const r=f(); return {r,e:''}; }catch(e){ return {r:null,e:String(e.message||e)}; } };
const C=()=>cenClone(CEN0); const O=c=>c.ordens['OS-0421']; const FA=c=>c.reqs['REQ-035'].itens[0];
const fato=c=>({real:O(c).realizado,saldo:O(c).saldo,cons:FA(c).consumido,cust:FA(c).custodia});
const apS=(c,dia)=>(O(c).ap.find(a=>a.dia===dia)||{}).st;
const turno=(c,ha,h,cons)=>{ cenIniciarTurno(c,'OS-0421'); return cenFecharTurno(c,ha,h||8,cons,'',[]); };
// ---- seed ----
caso(()=>{ const c=C(); ok('S0 seed OS-0421: 190/350 ha, saldo 160, Fungicida A consumido 95 L e 65 L em custódia', JSON.stringify(fato(c))==='{"real":190,"saldo":160,"cons":95,"cust":65}', fato(c)); });
// ---- POSITIVOS: duplicata provável fica retida, sem somar ----
caso(()=>{ const c=C(); const w=osc_apontar(c,'OS-0421','26/09',50); const a=turno(c,50);
  ok('P1 web 26/09 50 ha e depois app (turno de 26/09) 50 ha: o 2º fica "Duplicidade a conferir"; 240 ha, saldo 110, Fungicida A 120 L consumido / 40 L em custódia (antes: 290 ha e 145 L)',
     JSON.stringify(fato(c))==='{"real":240,"saldo":110,"cons":120,"cust":40}'&&apS(c,6)===CEN_AP_DUP&&O(c).ap.find(x=>x.dia===6).dupDe.join()==='5', [fato(c),w.msg,a.msg]);
  ok('P1b mensagem do app diz o que existe, que nada foi somado e quem decide', /em conferência: já há dia 5, 50 ha pela web em 26\/09\. Nada foi somado nem baixado; Paula \(conferência\) decide/.test(a.msg), a.msg);
  ok('P1c selo "Apontamento em conferência" na ordem e encerramento bloqueado com dono', O(c).selos.some(s=>s.t==='Apontamento em conferência')&&/duplicidade: dia 6 \(26\/09, 50 ha\)\. Paula/.test(cenPodeEncerrar(c,'OS-0421')), [O(c).selos,cenPodeEncerrar(c,'OS-0421')]); });
caso(()=>{ const c=C(); turno(c,50); const w=osc_apontar(c,'OS-0421','26/09',50);
  ok('P2 app primeiro, web depois (mesma data): a web fica retida; 240 ha, 120 L', JSON.stringify(fato(c))==='{"real":240,"saldo":110,"cons":120,"cust":40}'&&apS(c,6)===CEN_AP_DUP&&/em conferência: já há dia 5, 50 ha pelo app \(Marcos\)/.test(w.msg), [fato(c),w.msg]); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50); const w=osc_apontar(c,'OS-0421','26/09',50);
  ok('P3 web repetida na mesma data (outra chave): o 2º fica retido; 240 ha', fato(c).real===240&&apS(c,6)===CEN_AP_DUP, [fato(c),w.msg]); });
caso(()=>{ const c=C(); cenSinal(c,false); turno(c,50); const loc=fato(c); osc_apontar(c,'OS-0421','26/09',50); const s=cenSinal(c,true);
  ok('P4 app sem sinal + web na mesma data: a web soma (o servidor não via o aparelho); no envio o turno do app fica retido e a baixa local é desfeita: 240 ha, 120 L / 40 L',
     JSON.stringify(fato(c))==='{"real":240,"saldo":110,"cons":120,"cust":40}'&&apS(c,5)===CEN_AP_DUP&&apS(c,6)==='Provisório'&&/Em conferência de duplicidade: OS-0421 dia 5/.test(s.msg), [loc,fato(c),s.msg]);
  const s2=cenSinal(c,true); ok('P4b reenvio da fila não soma de novo (OSDIA-03)', fato(c).real===240&&/Nada pendente/.test(s2.msg), s2.msg); });
// ---- decisão ----
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50); turno(c,50); const d=cenApDecidir(c,'OS-0421',6,false,'Paula');
  ok('D1 "mesmo turno": dia 6 Descartado, nada somado nem baixado (240 ha, 120 L), selo sai, encerramento não fica preso por ele', JSON.stringify(fato(c))==='{"real":240,"saldo":110,"cons":120,"cust":40}'&&apS(c,6)===CEN_AP_DESC&&!O(c).selos.some(s=>s.t==='Apontamento em conferência')&&!/duplicidade/.test(cenPodeEncerrar(c,'OS-0421')), [fato(c),d.msg]);
  const x=TRY(()=>cenApDecidir(c,'OS-0421',6,true,'Paula')); ok('D1b decidir de novo é recusado (não está mais em conferência)', /não está em conferência de duplicidade/.test(x.e), x); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50); turno(c,50); const d=cenApDecidir(c,'OS-0421',6,true,'Paula');
  ok('D2 "outro turno": soma uma vez: 290 ha, saldo 60, Fungicida A 145 L / 15 L; dia 6 Provisório com a decisão registrada', JSON.stringify(fato(c))==='{"real":290,"saldo":60,"cons":145,"cust":15}'&&apS(c,6)==='Provisório'&&O(c).ap.find(a=>a.dia===6).dec.quem==='Paula (conferência)', [fato(c),d.msg]); });
caso(()=>{ const c=C(); cenSinal(c,false); turno(c,50); osc_apontar(c,'OS-0421','26/09',50); cenSinal(c,true); const d=cenApDecidir(c,'OS-0421',5,true,'Paula');
  ok('D3 "outro turno" do apontamento que veio da fila: rebaixa uma vez (290 ha, 145 L / 15 L)', JSON.stringify(fato(c))==='{"real":290,"saldo":60,"cons":145,"cust":15}', [fato(c),d.msg]); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50); turno(c,50); osc_apontar(c,'OS-0421','25/09',110,{'Fungicida A':40,'Adjuvante espalhante':0},[]); const x=TRY(()=>cenApDecidir(c,'OS-0421',6,true,'Paula'));
  ok('D4 NEGATIVO "outro turno" que passa do saldo é recusado com a causa; nada muda (350 ha, retido)', /passa do saldo da ordem \(0 ha\)/.test(x.e)&&fato(c).real===350&&apS(c,6)===CEN_AP_DUP, [x.e,fato(c)]); });
// ---- NEGATIVOS: não é duplicata ----
caso(()=>{ const c=C(); turno(c,50); turno(c,50);
  ok('N1 dois turnos do mesmo operador no app no mesmo dia somam (turnos distintos): 290 ha', fato(c).real===290&&apS(c,5)==='Provisório'&&apS(c,6)==='Provisório', fato(c)); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','25/09',50); turno(c,50);
  ok('N2 datas diferentes (web 25/09, app 26/09) somam: 290 ha', fato(c).real===290&&apS(c,6)==='Provisório', fato(c)); });
caso(()=>{ const c=C(); cenApontar(c,{os:'OS-0421',d:'26/09',parc:'T1',ha:50,origem:'web',chave:'W-1'}); cenApontar(c,{os:'OS-0421',d:'26/09',parc:'T2',ha:50,origem:'app',quem:'Marcos',chave:'TU-x'});
  ok('N3 talhões diferentes na mesma data (T1 web, T2 app) somam: 290 ha', fato(c).real===290, fato(c)); });
caso(()=>{ const c=C(); const k='W-OS-0421-fixa'; const a=osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,k); const b=osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,k);
  ok('N4 idempotência: a mesma chave (duplo clique) devolve o mesmo apontamento; 240 ha, um só registro', fato(c).real===240&&O(c).ap.filter(x=>x.chave===k).length===1&&/já registrado/.test(b.msg), [fato(c),b.msg]); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50); turno(c,50);
  const x=TRY(()=>osc_conferencia(c,'OS-0421')); ok('N5 a retida não conta para concluir: "Enviar para conferência" recusa por saldo (110 ha)', /Ainda há 110 ha de saldo/.test(x.e), x.e); });
// ---- consumo real na web (como no app) ----
caso(()=>{ const c=C(); const w=osc_apontar(c,'OS-0421','26/09',50,{'Fungicida A':27,'Adjuvante espalhante':0},[]);
  ok('W1 web aceita o consumo real informado: 27 L baixados (122 L / 38 L), sem linha 0 do adjuvante fora da requisição', JSON.stringify(fato(c))==='{"real":240,"saldo":110,"cons":122,"cust":38}'&&/usado: Fungicida A 27 L\./.test(w.msg)&&!('Adjuvante espalhante' in O(c).ap.find(a=>a.dia===5).cons), [fato(c),w.msg]); });
caso(()=>{ const c=C(); const w=osc_apontar(c,'OS-0421','26/09',50,{'Fungicida A':80,'Adjuvante espalhante':0},[]); const cc=(c.confs||[])[0]||{};
  ok('W2 web informado acima da custódia (80 > 65 L): fica Em conferência com Rui, sem baixa (95 L / 65 L), área soma 240 ha; o texto diz que Rui confere e Ana (gestora) aceita o excedente (revisão do CTL-3, achado 7)', fato(c).real===240&&FA(c).consumido===95&&FA(c).custodia===65&&cc.estado==='Em conferência'&&cc.relatado===80&&/Rui \(almoxarife\) confere; Ana \(gestora\) aceita o excedente\.$/.test(w.msg), [fato(c),cc,w.msg]); });
caso(()=>{ const c=C(); FA(c).custodia=10; const x=TRY(()=>osc_apontar(c,'OS-0421','26/09',50,{'Fungicida A':25,'Adjuvante espalhante':0},['Fungicida A']));
  ok('W3 NEGATIVO web com a sugestão não editada acima da custódia (25 > 10 L) é recusada pedindo o usado; nada gravado', /acima do que está em custódia \(10 L\)\. Informe quanto foi usado/.test(x.e)&&O(c).ap.length===7&&fato(c).real===190, x.e); });
caso(()=>{ const c=C(); const w=osc_apontar(c,'OS-0421','26/09',50);
  ok('W4 web sem consumo informado (Mapa, chamada antiga): dose × área do trecho, 25 L (SINT-C03)', FA(c).consumido===120&&/Fungicida A 25 L/.test(w.msg), w.msg);
  const mv=(c.movs||[]).filter(m=>m.tipo==='consumo'&&m.origem==='web'); ok('W5 a web também grava o movimento de consumo (como o app)', mv.length===1&&/Fungicida A 25/.test(mv[0].det), mv); });
// ---- data, chave e formulário ----
caso(()=>{ const c=C(); cenIniciarTurno(c,'OS-0421'); const t=c.app.turno; ok('F1 turno do app leva a data operacional 26/09 (não o relógio do aparelho) e a chave do turno', t.d==='26/09'&&/^TU-OS-0421-\d+$/.test(t.chave), t); });
caso(()=>{ const c=C(); const L=osApIns(c,O(c),50,{}); ok('F2 formulário da web: Fungicida A sugere 25 L (editável, estimativa); Adjuvante fora da REQ-035 vazio = 0',
    L[0].v==='25'&&L[0].est&&L[0].q===25&&L[1].v===''&&L[1].q===0&&/Fora da REQ-035/.test(L[1].hint), L);
  const L2=osApIns(c,O(c),50,{'Fungicida A':'27,5'}); const col=osApColeta(L2); ok('F3 editado "27,5" vai como informado (fora de est)', col.cons['Fungicida A']===27.5&&col.est.indexOf('Fungicida A')<0&&col.est.indexOf('Adjuvante espalhante')>=0, col);
  const L3=osApIns(c,O(c),50,{'Fungicida A':'abc'}); ok('F4 NEGATIVO usado inválido: erro no campo, nada vai ao comando', /Informe o usado de Fungicida A em L/.test(osApColeta(L3).erro), osApColeta(L3)); });
// ---- regressões que devem continuar ----
caso(()=>{ const c=C(); cenSinal(c,false); turno(c,60,5); ok('R1 app sem sinal: não soma até o envio (190 ha) e entra na fila uma vez', fato(c).real===190&&c.app.fila.length===1, [fato(c),c.app.fila]);
  cenSinal(c,true); ok('R1b no envio soma uma vez: 250 ha', fato(c).real===250, fato(c)); });
caso(()=>{ const c=C(); FA(c).custodia=10; const x=TRY(()=>turno(c,50)); ok('R2 app: sugestão acima da custódia segue recusada com o texto do app', /acima do que está com você \(10 L\)\. Confira a retirada/.test(x.e), x.e); });
caso(()=>{ const c=C(); const x=TRY(()=>osc_apontar(c,'OS-0421','26/09',161)); ok('R3 área acima do saldo recusada (161 > 160)', /Máximo 160 ha: é o saldo da ordem\./.test(x.e), x.e); });
const TRYM=f=>{ try{ const r=f(); return (r&&r.msg)||'ok'; }catch(e){ return 'ERRO '+e.message; } };
const view=(c,id)=>{ const b=OSD.ords.find(x=>x.id===id); const o=osMerge(b,c.ordens[id],c); const pb=osProx(o); return {etapa:o.etapa,selos:o.selos.map(s=>s.t),dono:o.dono,prazo:o.prazo,P:pb.P.btn,b:pb.b&&pb.b.t,q:pb.b&&pb.b.q}; };
const f=c=>{ const it=c.reqs['REQ-035'].itens[0]; return [c.ordens['OS-0421'].realizado,it.consumido,it.custodia]; };
// 1 · Em execução com retido: dono/prazo
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1'); cenIniciarTurno(c,'OS-0421'); cenFecharTurno(c,50,8,undefined,'',[]);
  const v=view(c,'OS-0421'); ok('C0 retido em Em execução: selo "Apontamento em conferência", dono Paula (conferência), prazo com o dia', v.selos.indexOf('Apontamento em conferência')>=0&&v.dono===CEN_CONF_AP()&&v.prazo==='decidir se o dia 6 é outro turno', v); });
// 2 · retido chega a Em conferência: dono deveria ser a conferência, não o almoxarife
caso(()=>{ const c=C(); cenEntregar(c,'REQ-035','Fungicida A',15,'Marcos','Rui');
  console.log('2a', TRYM(()=>osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1')));
  cenIniciarTurno(c,'OS-0421'); console.log('2b', TRYM(()=>cenFecharTurno(c,50,8,undefined,'',[])));
  console.log('2c', TRYM(()=>osc_apontar(c,'OS-0421','27/09',110,undefined,undefined,'W-2')), JSON.stringify(f(c)));
  console.log('2d', TRYM(()=>osc_conferencia(c,'OS-0421')));
  const v=view(c,'OS-0421'); console.log('2 em conferência', JSON.stringify(v));
  ok('C1 retido em Em conferência: dono = conferência (Paula), não Rui', v.dono===CEN_CONF_AP(), v); });
// 3 · web informado acima da custódia: CC.quem e texto da prévia do Rui
caso(()=>{ const c=C(); const m=osc_apontar(c,'OS-0421','26/09',50,{'Fungicida A':80},[],'W-1'); const k=c.confs[0]; const p=cenConcPrevia(c,k.id);
  console.log('3', m.msg, '|', k.quem, '|', p.txt, '|', JSON.stringify(c.movs.slice(-1)[0]));
  ok('C2 web acima da custódia: a prévia do almoxarife não diz "custódia de web"', !/custódia de web/.test(p.txt), p.txt); });
// 4 · app sem sinal + web: no envio o movimento retido vira texto em det e o Estoque lê um item fantasma
caso(()=>{ const c=C(); cenSinal(c,false); cenIniciarTurno(c,'OS-0421'); cenFecharTurno(c,50,8,undefined,'',[]); osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1'); const s=cenSinal(c,true);
  const ap=c.ordens['OS-0421'].ap.find(a=>a.st===CEN_AP_DUP); const mv=c.movs.find(x=>x.id===ap.mov); const it=econsDet(c,mv);
  console.log('4', s.msg, '| det=', mv.det, '| econsDet=', JSON.stringify(it));
  ok('C3 movimento retido sem item no Estoque: det vazio, econsDet vazio, motivo em obs', mv.det===''&&it.length===0&&/^Retido: mesma data do dia 6/.test(mv.obs||''), [mv.det,it,mv.obs]);
  const d=cenApDecidir(c,'OS-0421',ap.dia,false,'Paula'); const it2=econsDet(c,mv); console.log('4b', d.msg, '| det=', mv.det, JSON.stringify(it2));
  ok('C3b movimento descartado também sem item fantasma', it2.length===0, it2); });
// 5 · colheita: retido e descartado viram lote de colheita (carLotes)
caso(()=>{ const c=C(); const o=c.ordens['OS-0505']; console.log('5 resp', o.resp, 'lotes antes', Object.keys(carLotes(c)).filter(k=>/0505/.test(k)).join(','));
  console.log('5a', TRYM(()=>osc_apontar(c,'OS-0505','26/09',10,undefined,undefined,'W-1')));
  cenIniciarTurno(c,'OS-0505'); console.log('5b', TRYM(()=>cenFecharTurno(c,10,4,undefined,'',[])));
  const ap=o.ap.find(a=>a.st===CEN_AP_DUP); console.log('5c retido', JSON.stringify(ap&&[ap.dia,ap.d,ap.ha,ap.st]), 'lotes', Object.keys(carLotes(c)).filter(k=>/0505/.test(k)).join(','));
  cenApDecidir(c,'OS-0505',ap.dia,false,'Paula'); const L=carLotes(c); const ids=Object.keys(L).filter(k=>/0505/.test(k));
  console.log('5d descartado → lotes', ids.join(','), JSON.stringify(ids.map(k=>[k,L[k].ha,L[k].st])));
  ok('C4 colheita descartada como duplicidade não cria lote de colheita', !ids.some(k=>L[k].st===CEN_AP_DESC), ids.map(k=>[k,L[k].st])); });
// 6 · mesma chave, payload diferente (ENG-021: conflito)
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1'); const r=TRYM(()=>osc_apontar(c,'OS-0421','26/09',30,undefined,undefined,'W-1'));
  console.log('6', r); ok('C5 mesma chave com área diferente é conflito (ENG-021), não "já registrado"', /^ERRO/.test(r), r); });
// 7 · arredondamento: "somar" usa o trecho calculado na captura (antes = realizado da época) → soma dos trechos ≠ dose × área
caso(()=>{ const c=C(); const o=c.ordens['OS-0421']; o.ins[0].dose=0.3333; const it=c.reqs['REQ-035'].itens[0];
  const c0=it.consumido; osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1'); cenIniciarTurno(c,'OS-0421'); cenFecharTurno(c,50,8,undefined,'',[]);
  osc_apontar(c,'OS-0421','27/09',50,undefined,undefined,'W-2'); const ap=o.ap.find(a=>a.st===CEN_AP_DUP); cenApDecidir(c,'OS-0421',ap.dia,true,'Paula');
  const soma=Math.round((it.consumido-c0)*100)/100, certo=Math.round((cenQtd(0.3333,o.realizado)-cenQtd(0.3333,190))*100)/100;
  console.log('7', o.realizado, 'consumido no período', soma, 'regra única', certo);
  ok('C6 somar depois de outro apontamento fecha na regra única (SINT-C03)', Math.abs(soma-certo)<1e-9, [soma,certo]); });
// 8 · web retida consome o 1º previsto (a linha do plano some sem nada somado)
caso(()=>{ const c=C(); const o=c.ordens['OS-0421']; const p0=o.ap.filter(a=>a.st==='Previsto').map(a=>a.d+':'+a.ha).join(',');
  osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1'); const p1=o.ap.filter(a=>a.st==='Previsto').map(a=>a.d+':'+a.ha).join(',');
  osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-2'); const p2=o.ap.filter(a=>a.st==='Previsto').map(a=>a.d+':'+a.ha).join(',');
  console.log('8 previstos', p0, '→', p1, '→ (retido)', p2); ok('C8 apontamento retido não consome o previsto', p2===p1, [p1,p2]); });
// 9 · OS-0421: o "hoje" da demonstração (23/09) é a data do dia 4; o Mapa no padrão antigo ficaria retido
caso(()=>{ const c=C(); const m=TRYM(()=>osc_apontar(c,'OS-0421','23/09',50,undefined,undefined,'W-1'));
  ok('C12 data antiga do Mapa (23/09, a do dia 4) fica retida contra o dia 4; nada somado (o Mapa usa 26/09: nav)', apS(c,5)===CEN_AP_DUP&&O(c).ap.find(a=>a.dia===5).dupDe.join()==='4'&&fato(c).real===190, [m,fato(c)]); });
// 10 · app: o caso do aparelho fica "Aguarda duplicidade" (conta como aberto no cartão; texto conferido no navegador)
caso(()=>{ const c=C(); cenSinal(c,false); cenIniciarTurno(c,'OS-0421'); cenFecharTurno(c,2,1,{'Fungicida A':70},'',[]); osc_apontar(c,'OS-0421','26/09',2,undefined,undefined,'W-1'); cenSinal(c,true);
  const ap=c.ordens['OS-0421'].ap.find(a=>a.st===CEN_AP_DUP); const cf=(c.confs||[]).filter(k=>k.os==='OS-0421'&&k.dia===ap.dia);
  ok('C7 caso do aparelho retido fica "Aguarda duplicidade" (não "resolvido") e sem baixa', cf.length===1&&cf[0].estado===CEN_CC_AGUARDA&&!/undefined/.test(cenConfTxt(cf[0],c)), cf); });
// 11 · duas pessoas no app (dois aparelhos), mesma O.S., mesma data, talhões não informados → retido (falso positivo previsto)
caso(()=>{ const c=C(); cenIniciarTurno(c,'OS-0421'); cenFecharTurno(c,50,8,undefined,'',[]); c.app.operador='Carlos'; cenIniciarTurno(c,'OS-0421'); const m=TRYM(()=>cenFecharTurno(c,50,8,undefined,'',[]));
  ok('C13 residual declarado: dois aparelhos (Marcos e Carlos), mesma O.S. e data, sem talhão: o 2º fica retido para Paula (falso positivo previsto), 240 ha', c.ordens['OS-0421'].realizado===240&&apS(c,6)===CEN_AP_DUP&&/já há dia 5, 50 ha pelo app \(Marcos\)/.test(m), m); });
caso(()=>{ const c=C(); const o=c.ordens['OS-0421'];
c.app.turno={os:'OS-0421',ini:'07:00',pausas:[],fim:null};   // estado salvo antigo: sem chave e sem data
console.log('legado', cenFecharTurno(c,10,2,undefined,'',[]).msg, '| chave', o.ap.filter(a=>a.st!=='Previsto').slice(-1)[0].chave);
const antes=o.realizado; let msgs=[];
for(let i=0;i<5;i++){ cenIniciarTurno(c,'OS-0421'); msgs.push(cenFecharTurno(c,10,2,undefined,'',[]).msg.slice(0,60)+' | '+c.ordens['OS-0421'].realizado); }
console.log(msgs.join('\n'));
console.log('5 turnos fechados, somado', o.realizado-antes, 'ha (esperado 50) · registros', o.ap.filter(a=>a.st!=='Previsto').length);
ok('C9 turno aberto em estado antigo (sem chave) + 5 turnos de 10 ha: chave reserva não colide, soma 50 ha', o.realizado-antes===50, o.realizado-antes); });
caso(()=>{ const c2=C(); const o2=c2.ordens['OS-0421']; osc_apontar(c2,'OS-0421','26/09',50,undefined,undefined,'W-1');
  const a1=osApDupAviso(c2,o2,'26/09'), a2=osApDupAviso(c2,o2,'27/09'); console.log('aviso 26/09:', a1, '| 27/09:', JSON.stringify(a2));
  ok('C10 aviso no formulário com o mesmo critério do servidor (26/09 avisa; 27/09 não)', /^Já há dia 5, 50 ha pela web em 26\/09/.test(a1)&&a2==='', [a1,a2]); });
const f4=c=>{ const it=c.reqs['REQ-035'].itens[0]; return [c.ordens['OS-0421'].realizado,c.ordens['OS-0421'].saldo,it.consumido,it.custodia]; };
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1'); cenIniciarTurno(c,'OS-0421'); cenFecharTurno(c,50,8,{'Fungicida A':27},'',[]);
  const ant=cenClone(c); cenApDecidir(ant,'OS-0421',6,false,'Paula'); console.log('mesmo turno, vale o anterior:', JSON.stringify(f4(ant)), '(o real era 27 L → 122/38)');
  { const m=cenApDecidir(c,'OS-0421',6,'este','Paula'); const K=c.ordens['OS-0421'].ap.find(a=>a.dia===5); const mk=c.movs.find(x=>x.id===K.mov);
    console.log('vale este:', m.msg, JSON.stringify(f4(c)), K.st, JSON.stringify(mk), JSON.stringify(econsDet(c,mk)));
    ok('C11 "mesmo turno: vale este" fica com o usado real do app: 240 ha, 122 L / 38 L; o dia 5 estornado e guardado', JSON.stringify(f4(c))==='[240,110,122,38]'&&K.st===CEN_AP_DESC&&econsDet(c,mk).length===0, [f4(c),K.st]);
    const c2=C(); osc_apontar(c2,'OS-0421','26/09',50,undefined,undefined,'W-1'); osc_apontar(c2,'OS-0421','26/09',50,undefined,undefined,'W-2'); osc_apontar(c2,'OS-0421','26/09',50,undefined,undefined,'W-3');
    let e=''; try{ cenApDecidir(c2,'OS-0421',7,'este','Paula'); }catch(x){ e=x.message; } ok('C11b "vale este" contra dois anteriores é recusado com a causa', /só contra um apontamento já somado/.test(e), e); }});
// ---- B × A (PLANO §3): duplicidade retida numa ordem com insumo esgotado → dono Paula (decisão muda saldo e custódia); o selo da Frente B continua ----
caso(()=>{ const c=C(); const it=FA(c); it.consumido=it.solicitado; it.custodia=0;
  osc_apontar(c,'OS-0421','26/09',10,{'Fungicida A':0,'Adjuvante espalhante':0},[],'W-1'); osc_apontar(c,'OS-0421','26/09',10,{'Fungicida A':0,'Adjuvante espalhante':0},[],'W-2');
  const v=view(c,'OS-0421'); ok('BA retido + insumo esgotado: selos "Insumo esgotado · Fungicida A" e "Apontamento em conferência", dono Paula (conferência)',
    v.selos.some(s=>/^Insumo esgotado · Fungicida A/.test(s))&&v.selos.indexOf('Apontamento em conferência')>=0&&v.dono===CEN_CONF_AP()&&/decidir se o dia 6 é outro turno/.test(v.prazo), v); });
// ---- reprodução da auditoria (falha da base): web 50 ha + app 50 ha no mesmo turno → 240 ha · 120 L (base: 290 ha · 145 L) ----
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50); cenIniciarTurno(c,'OS-0421'); cenFecharTurno(c,50,8,undefined,'',[]);
  console.log('REPRO OS-0421 realizado '+O(c).realizado+' ha · Fungicida A consumido '+FA(c).consumido+' L · custódia '+FA(c).custodia+' L');
  ok('REPRO auditoria: web 50 ha + app 50 ha do mesmo turno = 240 ha · 120 L (base: 290 ha · 145 L)', JSON.stringify(fato(c))==='{"real":240,"saldo":110,"cons":120,"cust":40}', fato(c)); });
// ---- revisão 2 do CTL-2 (contraexemplos do revisor, executados): V = achados confirmados, K = mutantes que viviam ----
const inv=c=>{ const o=O(c); return o.realizado+((o.osc&&o.osc.disp)||0)<=o.area+1e-9; };   // invariante: realizado + dispensado ≤ área autorizada
const t0505=(c,ha)=>{ cenIniciarTurno(c,'OS-0505'); return cenFecharTurno(c,ha,4,undefined,'',[]); };
const st0505=(c,dia)=>(c.ordens['OS-0505'].ap.find(a=>a.dia===dia)||{}).st;
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','27/09',50,undefined,undefined,'W-1'); osc_apontar(c,'OS-0421','27/09',50,undefined,undefined,'W-2');
  cenSinal(c,false); turno(c,70,8,{'Fungicida A':35}); const x=TRY(()=>cenApDecidir(c,'OS-0421',6,'somar','Paula')); cenSinal(c,true);
  ok('V1 S2 "Outro turno: somar" desconta a área no aparelho: recusado (máximo 40 ha, 70 ha no aparelho); depois do sinal 310 ≤ 350 ha', /^Somar 50 ha passa do saldo da ordem \(40 ha, descontando 70 ha ainda no aparelho\)/.test(x.e)&&O(c).realizado===310&&apS(c,6)===CEN_AP_DUP&&inv(c), [x.e,fato(c)]); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','27/09',50,undefined,undefined,'W-1'); osc_apontar(c,'OS-0421','27/09',100,{'Fungicida A':0,'Adjuvante espalhante':0},[],'W-2');
  cenSinal(c,false); turno(c,70,8,{'Fungicida A':35}); const x=TRY(()=>cenApDecidir(c,'OS-0421',6,'este','Paula')); cenSinal(c,true);
  ok('V1b S2 "vale este" também desconta: 100 ha contra 90 ha (160 depois do estorno − 70 no aparelho) é recusado e nada é estornado', /^"Vale este" com 100 ha passa do saldo da ordem \(90 ha, descontando 70 ha ainda no aparelho\)\.$/.test(x.e)&&apS(c,5)==='Provisório'&&O(c).realizado===310&&inv(c), [x.e,fato(c)]); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50,{'Fungicida A':70,'Adjuvante espalhante':0},[],'W-1'); cenConciliar(c,c.confs[0].id,true,undefined,'Ana');   // CTL-3 (padrão 2): os 5 L acima da custódia, aceite da gestora
  osc_apontar(c,'OS-0421','26/09',50,{'Fungicida A':27,'Adjuvante espalhante':0},[],'W-2'); const f0=JSON.stringify(fato(c)); const K=O(c).ap.find(a=>a.dia===5);
  const x=TRY(()=>cenApDecidir(c,'OS-0421',6,'este','Paula'));
  ok('V2 S2 "vale este" com o consumo do dia 5 já aceito (CC-301, pela gestora: CTL-3) é recusado com quem aceitou; nada muda (165 L, sem caso novo); a tela esconde o botão (cenApUsoK)', /^"Vale este" não desfaz o dia 5: consumo já aceito por Ana \(gestora\) \(CC-301\)\. Escolha "Mesmo turno: vale o dia 5"\.$/.test(x.e)
     &&JSON.stringify(fato(c))===f0&&f0==='{"real":240,"saldo":110,"cons":165,"cust":0}'&&c.confs.length===1&&apS(c,5)==='Provisório'&&apS(c,6)===CEN_AP_DUP&&cenApUsoK(c,O(c),K)==='consumo já aceito por Ana (gestora) (CC-301)', [x.e,fato(c),c.confs.length]);
  const d=TRY(()=>cenApDecidir(c,'OS-0421',6,'anterior','Paula')); ok('V2b a saída que resta ("vale o dia 5") guarda o dia 6 sem baixa', !d.e&&apS(c,6)===CEN_AP_DESC&&JSON.stringify(fato(c))===f0, [d.e,fato(c)]); });
caso(()=>{ const c=C(); const ids=()=>Object.keys(carLotes(c)).filter(k=>/^LC-0505-\d+$/.test(k)).join(','); const lid=carLid('OS-0505',4);
  osc_apontar(c,'OS-0505','26/09',10,undefined,undefined,'W-1'); t0505(c,10);
  const x=TRY(()=>carc_destino(c,lid,Object.keys(CARD.dest)[0])), y=TRY(()=>carc_liberar_lote(c,lid));
  ok('V3 S2 colheita retida não vira lote: LC-0505-4 não existe; destino e liberação recusados, nada gravado', st0505(c,4)===CEN_AP_DUP&&ids()==='LC-0505-1,LC-0505-2,LC-0505-3'&&/LC-0505-4 não encontrado/.test(x.e)&&/impedida/.test(y.e)&&!((c.car||{}).dest||{})[lid]&&!((c.car||{}).lib||{})[lid], [ids(),x.e,y.e]);
  const d=TRY(()=>cenApDecidir(c,'OS-0505',4,'somar','Paula')); ok('V3b somada como outro turno, o lote LC-0505-4 aparece com 10 ha', !d.e&&!!carLotes(c)[lid]&&carLotes(c)[lid].ha===10, [d.e,ids()]); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0505','26/09',10,undefined,undefined,'W-1'); const lk=carLid('OS-0505',3); carc_destino(c,lk,Object.keys(CARD.dest)[0]); carc_liberar_lote(c,lk);
  t0505(c,10); const x=TRY(()=>cenApDecidir(c,'OS-0505',4,'este','Paula'));
  ok('V3c "vale este" na colheita com o lote do dia 3 já com destino e liberação é recusado; lote, destino e liberação ficam', /^"Vale este" não desfaz o dia 3: lote LC-0505-3 com destino, liberação comercial\./.test(x.e)&&!!carLotes(c)[lk]&&st0505(c,3)==='Provisório'&&st0505(c,4)===CEN_AP_DUP&&!!carLib(c,lk), x.e); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0505','26/09',10,undefined,undefined,'W-1'); t0505(c,10); const d=TRY(()=>cenApDecidir(c,'OS-0505',4,'este','Paula')); const L=carLotes(c);
  ok('V3d sem registro sobre o lote, "vale este" troca o lote: LC-0505-3 sai, LC-0505-4 entra', !d.e&&!L['LC-0505-3']&&!!L['LC-0505-4'], [d.e,Object.keys(L)]); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1'); turno(c,50); const x=TRY(()=>osc_dispensar(c,'OS-0421',110,'chuva','Ana'));
  const s=TRY(()=>cenApDecidir(c,'OS-0421',6,'somar','Paula'));
  ok('V4 dispensar saldo com retido é recusado (Paula decide antes); "Outro turno: somar" continua possível: 290 ha', /^Apontamento em conferência de duplicidade \(dia 6\): Paula \(conferência\) decide antes de dispensar o saldo\.$/.test(x.e)&&!s.e&&O(c).realizado===290&&!(O(c).osc||{}).disp, [x.e,s.e,fato(c)]); });
caso(()=>{ const c=C(); osc_dispensar(c,'OS-0421',10,'borda','Ana'); osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1'); turno(c,50); const v=view(c,'OS-0421');
  ok('V4b dispensa parcial na mesma fase e depois retido: dono Paula (conferência), não vazio', v.dono===CEN_CONF_AP()&&v.prazo==='decidir se o dia 6 é outro turno', v); });
// CTL-3 (R-D3): a alçada de 20 % (70 ha) passou para o comando; o turno no aparelho vira 100 ha para o máximo (60 ha) ficar dentro da alçada
caso(()=>{ const c=C(); cenSinal(c,false); turno(c,100,8,{'Fungicida A':50}); const x=TRY(()=>osc_dispensar(c,'OS-0421',61,'chuva','Ana')); const y=TRY(()=>osc_dispensar(c,'OS-0421',60,'chuva','Ana')); cenSinal(c,true);
  ok('V4c S2 pré-existente: dispensar desconta a área no aparelho; 61 recusado (máximo 60 ha), 60 aceito; com o sinal, 290 + 60 dispensados = 350 ha', /^Máximo 60 ha: é o saldo da ordem descontando 100 ha ainda no aparelho\.$/.test(x.e)&&!y.e&&O(c).realizado===290&&O(c).osc.disp===60&&inv(c), [x.e,y.e,fato(c)]); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1'); osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-2'); turno(c,50);
  const d7=O(c).ap.find(a=>a.dia===7); const de0=d7.dupDe.join(); cenApDecidir(c,'OS-0421',6,'anterior','Paula'); const viv=cenApDupVivos(O(c),d7).map(a=>a.dia).join(); const x=TRY(()=>cenApDecidir(c,'OS-0421',7,'este','Paula'));
  ok('V5 "vale este" só olha o que ainda vale: dia 7 (dupDe 5, 6), com o 6 guardado, vale contra o 5: 240 ha, 120 L (DEMO-11)', de0==='5,6'&&viv==='5'&&!x.e&&JSON.stringify(fato(c))==='{"real":240,"saldo":110,"cons":120,"cust":40}'&&apS(c,5)===CEN_AP_DESC&&apS(c,7)==='Provisório', [de0,viv,x.e,fato(c)]); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1'); cenSinal(c,false); turno(c,25); turno(c,25); cenSinal(c,true);
  cenApDecidir(c,'OS-0421',6,'este','Paula'); const d7=O(c).ap.find(a=>a.dia===7); const a=TRY(()=>cenApDecidir(c,'OS-0421',7,'anterior','Paula')), e=TRY(()=>cenApDecidir(c,'OS-0421',7,'este','Paula'));
  ok('V5b com o dia 5 estornado, o dia 7 não tem "mesmo turno": as duas saídas recusadas com a causa (a tela mostra só "somar"); nada guardado', cenApDupVivos(O(c),d7).length===0&&/^O dia 5 já não vale \(estornado ou guardado\): o dia 7 só pode ser somado como outro turno\.$/.test(a.e)&&a.e===e.e&&apS(c,7)===CEN_AP_DUP, [a.e,e.e]);
  const s=TRY(()=>cenApDecidir(c,'OS-0421',7,'somar','Paula')); ok('V5c o dia 7 soma como outro turno: 240 ha, 120 L (25 + 25 ha do app)', !s.e&&JSON.stringify(fato(c))==='{"real":240,"saldo":110,"cons":120,"cust":40}', [s.e,fato(c)]); });
const v6=()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1'); osc_apontar(c,'OS-0421','26/09',40,{'Fungicida A':20,'Adjuvante espalhante':0},['Fungicida A'],'W-2');
  osc_apontar(c,'OS-0421','27/09',60,{'Fungicida A':30,'Adjuvante espalhante':0},[],'W-3'); return c; };
caso(()=>{ const c=v6(); const f0=JSON.stringify(fato(c)); const x=TRY(()=>cenApDecidir(c,'OS-0421',6,'somar','Paula'));
  ok('V6 decisão com a estimativa acima da custódia é recusada pedindo o usado (AP-04): nenhum caso para Rui, nada muda', /^Fungicida A: a estimativa dose × área \(20 L\) passa do que está em custódia \(10 L\)\. Informe o usado \(com Marcos\) e decida de novo\.$/.test(x.e)&&JSON.stringify(fato(c))===f0&&!(c.confs||[]).length&&apS(c,6)===CEN_AP_DUP, [x.e,fato(c)]);
  const y=TRY(()=>cenApDecidir(c,'OS-0421',6,'somar','Paula',{'Fungicida A':8}));
  ok('V6b com o usado informado na conferência (8 L) soma e baixa 8 L, como informado', !y.e&&FA(c).custodia===2&&O(c).ap.find(a=>a.dia===6).inf['Fungicida A']===true&&O(c).realizado===340, [y.e,fato(c)]); });
caso(()=>{ const c=v6(); const y=TRY(()=>cenApDecidir(c,'OS-0421',6,'somar','Paula',{'Fungicida A':15})); const k=(c.confs||[])[0]||{};
  ok('V6c usado informado acima da custódia (15 > 10 L) vai para Rui como relato (CONC-07), sem baixa', !y.e&&k.relatado===15&&k.motivo==='Consumo acima da custódia'&&k.estado==='Em conferência'&&FA(c).custodia===10, [y.e,k]); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50,{'Fungicida A':25,'Adjuvante espalhante':0},[],'W-K');
  const a=TRY(()=>osc_apontar(c,'OS-0421','26/09',50,{'Fungicida A':40,'Adjuvante espalhante':0},[],'W-K'));
  const b=TRY(()=>cenApontar(c,{os:'OS-0421',d:'26/09',ha:50,h:2,origem:'app',quem:'Carlos',chave:'W-K',cons:{'Fungicida A':25,'Adjuvante espalhante':0}}));
  const r=TRY(()=>osc_apontar(c,'OS-0421','26/09',50,{'Fungicida A':25,'Adjuvante espalhante':0},[],'W-K'));
  ok('V7 ENG-021: mesma chave com outro consumo, horas, origem ou operador = conflito; o mesmo conteúdo = "já registrado"; 240 ha, 120 L, um registro', /com outro conteúdo: conflito, nada gravado\.$/.test(a.e)&&/com outro conteúdo: conflito/.test(b.e)&&/já registrado/.test((r.r||{}).msg||'')
     &&JSON.stringify(fato(c))==='{"real":240,"saldo":110,"cons":120,"cust":40}'&&O(c).ap.filter(x=>x.chave==='W-K').length===1, [a.e,b.e,r]); });
caso(()=>{ const c=C(); FA(c).custodia=10; const x=TRY(()=>osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-M'));
  ok('V8 Mapa (sem campo de consumo): a recusa manda apontar pela O.S. informando o usado', /em custódia \(10 L\)\. Aponte pela O\.S\., informando quanto foi usado, ou confira a entrega no Estoque\.$/.test(x.e), x.e); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-1'); osc_apontar(c,'OS-0421','26/09',50,undefined,undefined,'W-2'); cenApDecidir(c,'OS-0421',6,'anterior','Paula');
  osc_apontar(c,'OS-0421','26/09',30,undefined,undefined,'W-3'); const d=O(c).ap.find(a=>a.dia===7).dupDe.join();
  ok('K1 relato guardado não é duplicata de um novo: o dia 7 fica retido só contra o dia 5', d==='5', d); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50,{'Fungicida A':80,'Adjuvante espalhante':0},[],'W-1'); turno(c,50); const d=TRY(()=>cenApDecidir(c,'OS-0421',6,'este','Paula')); const k=c.confs[0];
  ok('K2 "vale este" recusa o caso ainda aberto do dia 5 (CC-301 Recusado) e baixa só o dia 6: 240 ha, 120 L', !d.e&&k.estado==='Recusado'&&k.decisao==='mesmo turno: vale o dia 6'&&JSON.stringify(fato(c))==='{"real":240,"saldo":110,"cons":120,"cust":40}', [d.e,k,fato(c)]); });
caso(()=>{ const c=C(); const o=c.ordens['OS-0505'];   // aplicação sintética de Glifosato 480 (carência 3 dias no mamão) no Pivô 19 em 25/09
  c.ordens['OS-9901']={id:'OS-9901',tipo:'Pulverização',talhao:o.talhao,etapa:'Em execução',ins:[{p:'Glifosato 480',dose:1,un:'L'}],ap:[{d:'25/09',dia:1,ha:10,st:'Provisório',sinc:true,cons:{'Glifosato 480':10}}],resp:'Ana (agrônoma)'};
  osc_apontar(c,'OS-0505','26/09',10,undefined,undefined,'W-1'); t0505(c,10);
  const r0=carColhidoEmCarencia(c,o).map(x=>x.dia).join(); cenApDecidir(c,'OS-0505',4,'anterior','Paula'); const r1=carColhidoEmCarencia(c,o).map(x=>x.dia).join();
  ok('K3 colheita na carência (AP-09): o retido conta (conservador) e o guardado como duplicidade não', r0==='3,4'&&r1==='3', [r0,r1]); });
caso(()=>{ const c=C(); const o=c.ordens['OS-0505']; const tid=carTals(o.talhao)[0].tid;
  c.ordens['OS-9902']={id:'OS-9902',tipo:'Pulverização',talhao:o.talhao,etapa:'Em execução',area:20,realizado:0,saldo:20,ins:[{p:'Glifosato 480',dose:1,un:'L'}],ap:[],resp:'Ana (agrônoma)',req:null};
  osc_apontar(c,'OS-9902','26/09',10,{'Glifosato 480':10},[],'W-1'); osc_apontar(c,'OS-9902','26/09',10,{'Glifosato 480':10},[],'W-2'); const n0=carAplic(c,tid).apl.filter(x=>x.os==='OS-9902').length;
  cenApDecidir(c,'OS-9902',2,'anterior','Paula'); const n1=carAplic(c,tid).apl.filter(x=>x.os==='OS-9902').length;
  ok('K4 aplicação retida conta na carência e, guardada como duplicidade, deixa de contar (carAplic)', n0===2&&n1===1, [n0,n1]); });
caso(()=>{ const ap=(dia,st)=>({d:'26/09',dia,ha:10,st,sinc:true,cons:{'Fungicida A':5}});
  const r=CUSTO.ordCusto({atv:{op:'Pulverização'},ins:[{p:'Fungicida A',dose:0.5}],ap:[ap(1,'Provisório'),ap(2,CEN_AP_DUP),ap(3,CEN_AP_DESC)]});
  ok('K5 custo do Mapa (ordCusto) soma só o relato somado: 10 ha, insumo 500, operação 100 (retido e guardado fora)', r.ha===10&&r.ins===500&&r.op===100, r); });
// ---- CTL-3 · ATOR: só quem confere (papel conferente: Paula) decide a duplicidade; nenhum registro grava "Paula" sem Paula ----
const PF_=(k)=>(typeof G2_PERFIS!=='undefined'?G2_PERFIS.find(p=>p.k===k):null)||{k};
for(const [ator,nome] of [[PF_('Rui'),'Rui (almoxarife)'],[PF_('Ana'),'Ana (gestora e agrônoma)'],[PF_('Caio'),'Caio (PCP)'],[undefined,'sem perfil'],[{k:'Rui',papeis:{conferente:'conferência'}},'Rui forjado como conferente']]) caso(()=>{
  const c=C(); osc_apontar(c,'OS-0421','26/09',50); turno(c,50); const f0=JSON.stringify(fato(c)); const x=TRY(()=>osc_apDecidir(c,'OS-0421',6,'somar',undefined,ator)); const a6=O(c).ap.find(a=>a.dia===6);
  ok('AT1 NEGATIVO '+nome+' decide a duplicidade: recusado com quem decide; nada somado, dia 6 segue retido e sem decisão gravada (antes: somava e gravava "Paula (conferência)")',
     x.e==='Decidir a duplicidade do dia 6 da OS-0421: decisão de Paula (conferência). Nada foi alterado.'&&JSON.stringify(fato(c))===f0&&a6.st===CEN_AP_DUP&&!a6.dec, [x.e,fato(c),a6.dec]); });
caso(()=>{ const c=C(); osc_apontar(c,'OS-0421','26/09',50); turno(c,50); const x=TRY(()=>osc_apDecidir(c,'OS-0421',6,'anterior',undefined,PF_('Paula'))); const a6=O(c).ap.find(a=>a.dia===6);
  ok('AT2 Paula (conferência) decide pela tela (osc_apDecidir com o perfil): vale o dia 5, a decisão grava Paula (conferência)', !x.e&&a6.st===CEN_AP_DESC&&a6.dec&&a6.dec.quem==='Paula (conferência)'&&fato(c).real===240, [x.e,a6.dec]); });
caso(()=>{ ok('AT3 o papel de conferência é da Paula: g2quem("conferente") = CEN_CONF_AP (o texto "Quem decide" das telas e do app)', typeof g2quem==='function'&&g2quem('conferente')===CEN_CONF_AP()&&g2quem('almoxarife')==='Rui (almoxarife) ou Paula (almoxarife)', typeof g2quem==='function'?[g2quem('conferente'),g2quem('almoxarife')]:'sem g2quem'); });
console.log(JSON.stringify(R));
