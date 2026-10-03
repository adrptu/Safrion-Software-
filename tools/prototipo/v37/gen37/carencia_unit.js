// Testes puros do motor de carência e destino (MAPA-CARENCIA-LMR-20261003) · jsc (JavaScriptCore) sem navegador.
// Carregado depois de: CEN0 + cenario.js + JS_NUCLEO (que traz CARD e o motor). Cada verificação imprime uma linha JSON.
const R=[]; function ok(n,c,info){ R.push({n,ok:!!c,info:c?'':JSON.stringify(info===undefined?'':info).slice(0,600)}); }
function CEN(ordens,car){ return {v:2,rev:1,ordens,reqs:{},lotes:{},movs:[],ocorr:[],app:{online:true,fila:[],operador:'Marcos'},car:car||{}}; }
function O(id,tipo,talhao,etapa,ins,ap,x){ return Object.assign({id,tipo,talhao,etapa,area:(CARD.tal[(carTals(talhao)[0]||{}).tid]||{}).ha||0,realizado:0,saldo:0,resp:'Wesley',
  ins:ins.map(p=>({p,dose:1,un:'L',tot:1})),ap:ap.map((a,i)=>({d:a[0],dia:i+1,ha:a[1],st:a[2]||'Conferido',sinc:a[3]!==false,parc:a[4]})),selos:[],osc:{}},x||{}); }
const TRY=(f)=>{ try{ f(); return ''; }catch(e){ return String(e.message||e); } };
const H=CARD.hoje;   // 2026-09-23

// ---- 1 · duas aplicações com vencimentos distintos: a ANTERIOR restringe mais (vale o maior prazo, não a mais recente) ----
{ const c=CEN({'OS-A':O('OS-A','Pulverização · ácaro','Pivô 6','Em conferência',['Abamectina 18 EC'],[['10/09',86]]),
               'OS-B':O('OS-B','Pulverização · mosca-branca','Pivô 6','Em conferência',['Acetamiprido 200 SP'],[['19/09',86]]),
               'OS-C':O('OS-C','Colheita · semana 39','Pivô 6','A liberar',[],[],{janela:'21–22/09'})});
  const e20=carEstado(c,'PV06','2026-09-20'), e24=carEstado(c,'PV06','2026-09-24');
  ok('1a duas aplicações ativas em 20/09: a ANTERIOR (abamectina 10/09 → 24/09) determina o prazo, não a mais recente (acetamiprido 19/09 → 22/09)',
     e20.k==='curso'&&e20.det.os==='OS-A'&&e20.det.fim==='2026-09-24'&&e20.ativos.length===2&&carBloqColheita(c,c.ordens['OS-C'],'liberar').fim==='2026-09-24', [e20.k,e20.det,e20.ativos.length]);
  ok('1b em 24/09 o prazo está cumprido, mas o rótulo diz "destino a avaliar" (não é conforme)', e24.k==='cumprida'&&/destino a avaliar/.test(carRot(e24)), carRot(e24));
  const b=carBloqColheita(c,c.ordens['OS-C'],'liberar');
  ok('1c liberar a colheita OS-C (janela 21–22/09) é impedido no comando, com motivo (até 24/09, OS-A) e dono', !!b&&b.fim==='2026-09-24'&&/OS-A/.test(b.t)&&/Ana/.test(b.q), b);
  const er=TRY(()=>osc_liberar(c,'OS-C',false,'')); ok('1d osc_liberar recusa com o mesmo motivo; a O.S. continua A liberar', /carência em curso/.test(er)&&c.ordens['OS-C'].etapa==='A liberar', er);
  const m=carc_janela(c,'OS-C','2026-09-24'); const er2=TRY(()=>osc_liberar(c,'OS-C',false,''));
  ok('1e Rever programação: janela a partir de 24/09 → liberar passa; histórico da reprogramação guardado', er2===''&&c.ordens['OS-C'].etapa==='Liberadas'&&(c.ordens['OS-C'].osc.carh||[]).length===1, [er2,m]); }

// ---- 2 · aplicação parcial só na parcela A; O.S. apenas planejada na parcela B ----
{ const c=CEN({'OS-PA':O('OS-PA','Pulverização · fungicida','T1-A','Em conferência',['Fungicida A'],[['20/09',160]]),
               'OS-PB':O('OS-PB','Pulverização · fungicida','T1-B','A liberar',['Fungicida A'],[],{janela:'25/09'}),
               'OS-PX':O('OS-PX','Pulverização · fungicida','T1-B','Canceladas',['Fungicida A'],[])});
  const eA=carEstado(c,'T1',H,'T1-A'), eB=carEstado(c,'T1',H,'T1-B'), eT=carEstado(c,'T1',H);
  ok('2a parcela A: carência em curso pela aplicação apontada em T1-A', eA.k==='curso'&&eA.det.parc==='T1-A', [eA.k,eA.det]);
  ok('2b parcela B: O.S. planejada e O.S. cancelada sem apontamento não geram carência (planejada só como previsão)', eB.k==='sem'&&eB.prev.length===1&&eB.prev[0].os==='OS-PB'&&!eB.apl.length, [eB.k,eB.apl,eB.prev]);
  ok('2c talhão T1: rótulo indica que só T1-A está restrita', eT.k==='curso'&&eT.parcial&&/em T1-A/.test(carRot(eT)), carRot(eT));
  const c2=CEN({'OS-P2':O('OS-P2','Pulverização · antracnose','Pivô 23','Em conferência',['Tebuconazol 200 EC'],[['20/09',30]])});
  const e2=carEstado(c2,'PV23',H); ok('2d apontamento parcial SEM parcela (30 de 60 ha): faixa não identificada → prazo vale para o pivô todo', e2.k==='curso'&&e2.det.faixa===true, e2.det); }

// ---- 3 · carência vencida com destino/LMR/evidência pendentes continua sem liberação comercial ----
{ const ords={'OS-T':O('OS-T','Pulverização · antracnose','Pivô 23','Encerradas',['Tebuconazol 200 EC'],[['05/09',60]]),
              'OS-H':O('OS-H','Colheita · semana 39','Pivô 23','Em execução',[],[['22/09',20]])};
  const c=CEN(ords); const L='LC-0000-1';   // id do lote: LC + dígitos da O.S. + dia
  const lid=Object.keys(carLotes(c))[0];
  const sem=carAvaliar(c,lid,''), ue=carAvaliar(c,lid,'EXP-UE'), nd=carAvaliar(c,lid,'EXP-ND'), sint=carAvaliar(c,lid,'DEMO-S'), br=carAvaliar(c,lid,'MI-BR');
  ok('3a prazo cumprido (05/09 + 7 = 12/09) e colheita em 22/09: nenhum motivo de carência', !br.motivos.length&&carEstado(c,'PV23','2026-09-22').k!=='curso', br.motivos);
  ok('3b sem destino → Não avaliado; UE sem regra carregada → Pendente; mercado indefinido → Pendente', sem.st==='nao_avaliado'&&ue.st==='pendente'&&/não carregada/.test(ue.faltas.map(f=>f.t).join())&&nd.st==='pendente'&&/não identificado/.test(nd.faltas.map(f=>f.t).join()), [sem.st,ue.st,nd.st]);
  ok('3c destino que exige laudo, sem laudo → Pendente com dono (Qualidade)', sint.st==='pendente'&&sint.faltas.some(f=>/Laudo de resíduos/.test(f.t)&&/Qualidade/.test(f.q)), sint.faltas);
  ok('3d mercado interno: LMR ANVISA vigente de tebuconazol em mamão (1 mg/kg) e Conforme só "no escopo"', br.st==='conforme'&&/no escopo/.test(br.rot)&&br.ings.some(i=>i.ingr==='tebuconazol'&&/1 mg\/kg/.test(i.lim)), [br.st,br.rot,br.ings,br.faltas]);
  ok('3e nenhuma avaliação tem rótulo "Pode exportar"', ![sem,ue,nd,sint,br].some(a=>/pode exportar/i.test(a.rot)), [sem.rot,ue.rot]); }

// ---- 4 · dois lotes antes/depois de nova aplicação + tratamento pós-colheita ----
{ const c=CEN({'OS-H':O('OS-H','Colheita · semanal','Pivô 6','Em execução',[],[['18/09',43],['30/09',43]]),
               'OS-A':O('OS-A','Pulverização · ácaro','Pivô 6','Em conferência',['Abamectina 18 EC'],[['24/09',86]])},
              {ops:[{k:'pos',lote:'LC-0000-1',p:'Tiabendazol (imersão pós-colheita)',ingr:'tiabendazol',d:'2026-09-19',reg:false}]});
  const Ls=carLotes(c); const ids=Object.keys(Ls).sort(); const l1=ids.find(k=>Ls[k].d==='2026-09-18'), l2=ids.find(k=>Ls[k].d==='2026-09-30');
  c.car.ops[0].lote=l1;   // pós-colheita no lote de 18/09
  const a1=carAvaliar(c,l1,'MI-BR'), a2=carAvaliar(c,l2,'MI-BR');
  ok('4a lote de 18/09 (antes da aplicação de 24/09) não é contaminado retroativamente', !a1.motivos.length&&!a1.apl.length, a1.motivos);
  ok('4b lote de 30/09 colhido dentro da carência (último dia 07/10) → Não conforme com motivo e dono', a2.st==='nao_conforme'&&/até 07\/10/.test(a2.motivos[0].t)&&/Ana/.test(a2.motivos[0].q), a2.motivos);
  ok('4c pós-colheita liga-se só ao lote tratado: tiabendazol no lote de 18/09 (uso pós-colheita a conferir), não no de 30/09',
     a1.ings.some(i=>i.ingr==='tiabendazol')&&a1.st==='pendente'&&a1.faltas.some(f=>/pós-colheita/.test(f.t))&&!a2.ings.some(i=>i.ingr==='tiabendazol'), [a1.ings,a2.ings]);
  const cc=carColhidoEmCarencia(c,c.ordens['OS-H']);
  ok('4d colheita apontada em carência é registrada (não impedida) e marcada para conferência', cc.length===1&&cc[0].d==='2026-09-30', cc);
  const o={}; carMerge(o,c.ordens['OS-H'],c); ok('4e O.S. de colheita recebe o selo "Colhido em carência · conferir" e dono Ana', (o.selos||[]).some(s=>/Colhido em carência/.test(s.t))&&/Ana/.test(o.dono||''), o.selos); }

// ---- 5 · mistura/divisão e troca de destino preservam origem e reavaliam (sem diluição) ----
{ const c=CEN({'OS-H':O('OS-H','Colheita · semanal','Pivô 6','Em execução',[],[['18/09',43],['30/09',43]]),
               'OS-A':O('OS-A','Pulverização · ácaro','Pivô 6','Em conferência',['Abamectina 18 EC'],[['24/09',86]])},{ops:[]});
  const Ls=carLotes(c); const l1=Object.keys(Ls).find(k=>Ls[k].d==='2026-09-18'), l2=Object.keys(Ls).find(k=>Ls[k].d==='2026-09-30');
  c.car.ops.push({k:'mistura',d:'2026-10-01',de:[l1,l2],novos:[{id:'LM-T',q:'mistura'}]}); c.car.ops.push({k:'divisao',d:'2026-10-01',de:[l2],novos:[{id:'LD-TA',q:'classe A'},{id:'LD-TB',q:'classe B'}]});
  c.car.laudos=[{id:'LAB-T',escopo:['LM-T'],sint:true,res:{abamectina:{nd:true,lq:0.005,un:'mg/kg'}}}];
  const m=carAvaliar(c,'LM-T','DEMO-S'), dA=carAvaliar(c,'LD-TA','MI-BR');
  ok('5a mistura com lote colhido em carência continua Não conforme mesmo com laudo "não detectado" (sem diluição)', m.st==='nao_conforme'&&m.orig.length===2&&m.motivos.some(x=>/dentro da carência/.test(x.t)), [m.st,m.orig.map(x=>x.id)]);
  ok('5b divisão herda origem e restrição do lote de origem', dA.st==='nao_conforme'&&dA.orig.length===1&&dA.orig[0].id===l2, [dA.st,dA.orig]);
  const a0=carAvaliar(c,l1,'MI-BR'); c.car.dest={}; c.car.dest[l1]='MI-BR';
  const r=carc_destino(c,l1,'EXP-UE'); const a1=carAvaliar(c,l1); const h=c.car.hist[l1];
  ok('5c troca de destino MI-BR → UE reavalia (Conforme no escopo → Pendente) e preserva a avaliação anterior no histórico',
     a0.st==='conforme'&&a1.st==='pendente'&&h.length===1&&h[0].st0==='conforme'&&h[0].st1==='pendente'&&h[0].de==='MI-BR', [a0.st,a1.st,h,r]);
  const lau=carLaudos(c,carLotes(c),'LD-TA'); ok('5d laudo da mistura não vale para a divisão de outro lote (escopo da amostra)', !lau.length, lau); }

// ---- 6 · aplicação sincronizada depois ou fonte incompleta: nenhuma liberação falsa ----
{ const c=CEN({'OS-S':O('OS-S','Pulverização · antracnose','Pivô 23','Em execução',['Tebuconazol 200 EC'],[['22/09',60,'Provisório',false]],{saldo:0}),
               'OS-K':O('OS-K','Colheita · semana 39','Pivô 23','A liberar',[],[],{janela:'24/09'})});
  const e=carEstado(c,'PV23',H); const b=carBloqColheita(c,c.ordens['OS-K'],'liberar');
  ok('6a apontamento ainda no aparelho já conta: carência até 29/09 + pendência "aguardando sinal"', e.k==='curso'&&e.det.fim==='2026-09-29'&&e.pend.some(p=>p.k==='sinc'), [e.k,e.det&&e.det.fim,e.pend]);
  ok('6b colheita OS-K impedida pela aplicação não sincronizada', !!b&&b.fim==='2026-09-29', b);
  const c2=CEN({'OS-E':O('OS-E','Pulverização · fungicida','Pivô 23','Em execução',['Tebuconazol 200 EC'],[['10/09',20]],{saldo:40}),
                'OS-K':O('OS-K','Colheita · semana 39','Pivô 23','A liberar',[],[],{janela:'24/09'})});
  const e2=carEstado(c2,'PV23',H), b2=carBloqColheita(c2,c2.ordens['OS-K'],'liberar');
  ok('6c O.S. de defensivo em execução com saldo: dados insuficientes (pode haver aplicação não apontada) e colheita impedida', e2.k==='insuf'&&e2.pend.some(p=>p.k==='exec')&&!!b2&&/sem dados suficientes/.test(b2.t), [e2.k,b2]);
  const c3=CEN({'OS-R':O('OS-R','Pulverização · fungicida','Pivô 23','Encerradas',['Fungicida C'],[['01/09',60]]),
                'OS-Z':O('OS-Z','Pulverização · antracnose','Pivô 23','Encerradas',['Azoxistrobina 250 SC'],[['02/09',60]]),
                'OS-H':O('OS-H','Colheita · semana 37','Pivô 23','Encerradas',[],[['12/09',60]])});
  const e3=carEstado(c3,'PV23',H); const lid=Object.keys(carLotes(c3))[0]; const a3=carAvaliar(c3,lid,'MI-BR');
  ok('6d produto sem uso registrado na cultura e carência não conferida: nunca "cumprida"; lote Pendente', e3.k==='insuf'&&e3.pend.some(p=>p.k==='regra')&&e3.pend.some(p=>p.k==='bula')&&a3.st==='pendente', [e3.k,e3.pend,a3.st]);
  const c4=CEN({'OS-H':O('OS-H','Colheita · semana 36','Pivô 6','Encerradas',[],[['05/09',86]])}); const l4=Object.keys(carLotes(c4))[0]; const a4=carAvaliar(c4,l4,'MI-BR');
  ok('6e colheita de 05/09 exige histórico desde 22/08, antes do início do registro (01/09): pendente (caderno de campo)', a4.st==='pendente'&&a4.faltas.some(f=>/caderno de campo/.test(f.t)), a4.faltas); }
{ const c=CEN({'OS-F':O('OS-F','Pulverização · ácaro','Pivô 6','Em execução',['Abamectina 18 EC'],[['24/09',86,'Provisório']])});
  const e=carEstado(c,'PV06',H); ok('6f apontamento com data depois da consultada (24/09 > 23/09) é fato registrado: o talhão já mostra a carência (até 08/10)', e.k==='curso'&&e.det.fim==='2026-10-08', [e.k,e.det]); }

// ---- comandos e aviso preventivo no núcleo da O.S. ----
{ const c=CEN({'OS-AP':O('OS-AP','Pulverização · ácaro','Pivô 19','A liberar',['Abamectina 18 EC'],[],{janela:'25/09'}),
               'OS-CO':O('OS-CO','Colheita · semana 39','Pivô 19','Em execução',[],[['21/09',14]],{saldo:28})});
  const w=carAvisoAplic(c,c.ordens['OS-AP']);
  ok('7a liberar aplicação: aviso preventivo de conflito com a colheita (OS-CO) até 09/10, sem bloquear', !!w&&/OS-CO/.test(w.t)&&w.fim==='2026-10-09'&&!carBloqColheita(c,c.ordens['OS-AP'],'liberar'), w);
  c.ordens['OS-K']=O('OS-K','Colheita · semana 39','Pivô 23','Liberadas',[],[],{janela:'24/09'}); c.ordens['OS-T']=O('OS-T','Pulverização · antracnose','Pivô 23','Em conferência',['Tebuconazol 200 EC'],[['20/09',60]]);
  const er=TRY(()=>osc_iniciar(c,'OS-K')); ok('7b iniciar colheita liberada antes da aplicação também é impedido (comando)', /Iniciar bloqueado: carência em curso/.test(er)&&c.ordens['OS-K'].etapa==='Liberadas', er);
  c.ordens['OS-K'].etapa='Em execução'; c.ordens['OS-K'].saldo=60; const ea=TRY(()=>osc_apontar(c,'OS-K','24/09',10));
  ok('7c registrar a colheita feita (fato) nunca é impedido: apontamento aceito e marcado para conferência', ea===''&&carColhidoEmCarencia(c,c.ordens['OS-K']).length===1, ea); }

// ---- 8 · contraexemplos da verificação (03/10): nenhum falso verde, nenhuma diluição, comando impedido e recuperação ----
{ // 8a produto fora de todo cadastro: possível defensivo → dados insuficientes, colheita impedida; registrar a carência da bula recupera
  const c=CEN({'OS-X':O('OS-X','Pulverização · fungicida novo','Pivô 23','Em conferência',['Fungicida Novo 500 SC'],[['22/09',60]]),
               'OS-K':O('OS-K','Colheita · semana 39','Pivô 23','A liberar',[],[],{janela:'24/09'})});
  const e=carEstado(c,'PV23',H), b=carBloqColheita(c,c.ordens['OS-K'],'liberar');
  ok('8a produto fora do cadastro aplicado: "dados insuficientes" (nunca "sem aplicação") e liberar a colheita impedido com dono', e.k==='insuf'&&e.pend.some(p=>p.k==='regra'&&/sem cadastro/.test(p.t))&&!!b&&b.pk==='regra'&&b.p==='Fungicida Novo 500 SC'&&/Ana/.test(b.q), [e.k,e.pend,b]);
  const eb=TRY(()=>carc_bula(c,'Fungicida Novo 500 SC','Mamão','x')); carc_bula(c,'Fungicida Novo 500 SC','Mamão','14');
  const e2=carEstado(c,'PV23',H), b2=carBloqColheita(c,c.ordens['OS-K'],'liberar');
  ok('8b registrar a carência conferida (14 dias): valor inválido recusado; o prazo passa a contar (até 05/10) e a colheita segue impedida pela carência', /dias inteiros/.test(eb)&&e2.k==='curso'&&e2.det.fim==='2026-10-06'&&!!b2&&b2.fim==='2026-10-06'&&/até 05\/10/.test(b2.t), [eb,e2.k,e2.det&&e2.det.fim,b2&&b2.t]); }
{ // 8c carência não conferida na bula com prazo provisório já vencido: não autoriza a colheita; conferida (10 dias) libera
  const c=CEN({'OS-Z':O('OS-Z','Pulverização · antracnose','Pivô 23','Encerradas',['Azoxistrobina 250 SC'],[['05/09',60]]),
               'OS-K':O('OS-K','Colheita · semana 39','Pivô 23','A liberar',[],[],{janela:'24/09'})});
  const er=TRY(()=>osc_liberar(c,'OS-K',false,'')); const b=carBloqColheita(c,c.ordens['OS-K'],'liberar');
  ok('8c prazo provisório vencido (7 dias não conferidos): liberar a colheita recusado, motivo "não conferidos na bula"', /bloqueado/.test(er)&&/não conferidos na bula/.test(er)&&c.ordens['OS-K'].etapa==='A liberar'&&b.pk==='bula', [er,b]);
  carc_bula(c,'Azoxistrobina 250 SC','Mamão',10); const er2=TRY(()=>osc_liberar(c,'OS-K',false,''));
  ok('8d carência conferida (10 dias → 15/09): liberar passa; a conferência fica registrada com quem e quando', er2===''&&c.ordens['OS-K'].etapa==='Liberadas'&&c.car.bula['Azoxistrobina 250 SC|Mamão'][0].por===CARD.quem.ag, [er2,c.car.bula]); }
{ // 8e mercado interno com laudo acima do LMR ANVISA: Não conforme (contraprova vale mesmo sem exigência de laudo)
  const c=CEN({'OS-T':O('OS-T','Pulverização · antracnose','Pivô 23','Encerradas',['Tebuconazol 200 EC'],[['05/09',60]]),
               'OS-H':O('OS-H','Colheita · semana 39','Pivô 23','Em execução',[],[['22/09',20]])});
  const lid=Object.keys(carLotes(c))[0]; const a0=carAvaliar(c,lid,'MI-BR');
  c.car={laudos:[{id:'LAB-V2',escopo:[lid],d:'2026-09-23',sint:true,res:{tebuconazol:{v:5.0,un:'mg/kg'}}}]}; const a1=carAvaliar(c,lid,'MI-BR');
  c.car.laudos[0].res={tebuconazol:{v:0.4,un:'mg/kg'}}; const a2=carAvaliar(c,lid,'MI-BR');
  c.car.laudos[0].res={tebuconazol:{v:400,un:'µg/kg'}}; const a3=carAvaliar(c,lid,'MI-BR');
  c.car.laudos[0].res={carbendazim:{v:0.2,un:'mg/kg'}}; const a4=carAvaliar(c,lid,'MI-BR');
  ok('8e mercado interno: sem laudo Conforme no escopo; laudo 5,0 > LMR 1,0 → Não conforme; 0,4 → Conforme; unidade µg/kg → Pendente; resíduo sem aplicação apontada → Pendente',
     a0.st==='conforme'&&a1.st==='nao_conforme'&&/acima do limite 1 mg\/kg/.test(a1.motivos[0].t)&&a2.st==='conforme'&&a3.st==='pendente'&&a4.st==='pendente'&&a4.faltas.some(f=>/sem aplicação apontada/.test(f.t)), [a0.st,a1.st,a2.st,a3.st,a4.st,a4.faltas]); }
{ // 8f/8g mistura e divisão: resultado acima do limite numa origem não se dilui (com ou sem laudo próprio abaixo)
  const c=CEN({'OS-0901':O('OS-0901','Pulverização · antracnose','Pivô 23','Encerradas',['Tebuconazol 200 EC'],[['05/09',60]]),
               'OS-0902':O('OS-0902','Colheita · semana 39','Pivô 23','Encerradas',[],[['22/09',20]]),
               'OS-0903':O('OS-0903','Colheita · semana 39','Pivô 19','Encerradas',[],[['22/09',14]])});
  const A='LC-0902-1', B='LC-0903-1';
  c.car={ops:[{k:'mistura',d:'2026-09-23',de:[A,B],novos:[{id:'LM-V3',q:'mistura'}]},{k:'divisao',d:'2026-09-23',de:[A],novos:[{id:'LD-V4A',q:'classe A'}]}],
         laudos:[{id:'LAB-A',escopo:[A],d:'2026-09-22',sint:true,res:{tebuconazol:{v:0.2,un:'mg/kg'}}},{id:'LAB-M',escopo:['LM-V3'],d:'2026-09-23',sint:true,res:{tebuconazol:{v:0.03,un:'mg/kg'}}},
                 {id:'LAB-D',escopo:['LD-V4A'],d:'2026-09-23',sint:true,res:{tebuconazol:{v:0.03,un:'mg/kg'}}}]};
  const aA=carAvaliar(c,A,'DEMO-S'), aM=carAvaliar(c,'LM-V3','DEMO-S'), aD=carAvaliar(c,'LD-V4A','DEMO-S');
  ok('8f mistura com laudo próprio abaixo (0,03) de origem acima (0,2 > 0,05 sintético): Não conforme, motivo cita o lote de origem', aA.st==='nao_conforme'&&aM.st==='nao_conforme'&&aM.motivos.some(m=>/LAB-A do lote de origem LC-0902-1/.test(m.t)), [aA.rot,aM.rot,aM.motivos]);
  ok('8g parte de divisão com laudo próprio abaixo: herda o resultado acima da origem (Não conforme)', aD.st==='nao_conforme'&&aD.ings.some(g=>g.st==='acima'), [aD.rot,aD.ings]);
  c.car.laudos=c.car.laudos.slice(0,1); const aM2=carAvaliar(c,'LM-V3','DEMO-S'), aMI=carAvaliar(c,'LM-V3','MI-BR');
  ok('8h mistura sem laudo próprio: Não conforme no destino sintético; no mercado interno (LMR 1,0) o 0,2 da origem não impede', aM2.st==='nao_conforme'&&aMI.st!=='nao_conforme', [aM2.rot,aMI.rot]); }
{ // 8i O.S. cancelada COM apontamento (sincronização tardia): a aplicação conta e fica a pendência; sem apontamento não conta
  const c=CEN({'OS-C':O('OS-C','Pulverização · ácaro','Pivô 6','Canceladas',['Abamectina 18 EC'],[['20/09',86]]),'OS-C2':O('OS-C2','Pulverização · ácaro','Pivô 19','Canceladas',['Abamectina 18 EC'],[])});
  const e=carEstado(c,'PV06',H), e2=carEstado(c,'PV19',H);
  ok('8i cancelada com apontamento em 20/09: carência até 03/10 + pendência "cancelada com apontamento"; cancelada sem apontamento: nada', e.k==='curso'&&e.det.fim==='2026-10-04'&&e.pend.some(p=>p.k==='canc')&&e2.k==='sem', [carRot(e),e.pend,e2.k]); }
{ // 8j colheita em execução e aplicação apontada depois: selo e dono na O.S.; próximo turno impedido; apontar o que foi colhido continua livre
  const c=CEN({'OS-H':O('OS-H','Colheita · semana 39','Pivô 19','Em execução',[],[['21/09',14]],{saldo:28}),
               'OS-A':O('OS-A','Pulverização · ácaro','Pivô 19','Em conferência',['Abamectina 18 EC'],[['22/09',42]])});
  const o={}; carMerge(o,c.ordens['OS-H'],c); const ea=TRY(()=>osc_apontar(c,'OS-H','23/09',5));
  ok('8j colheita OS-H em execução: selo "Carência até 05/10", dono Ana e prazo "suspender novos turnos"; apontamento aceito', (o.selos||[]).some(s=>s.t==='Carência até 05/10')&&/Ana/.test(o.dono||'')&&/suspender novos turnos/.test(o.prazo||'')&&!o.carB&&ea==='', [o.selos,o.dono,o.prazo,ea]); }
{ // 8k id de lote sem colisão entre prefixos diferentes de O.S.
  const c=CEN({'OS-0505':O('OS-0505','Colheita · semana 39','Pivô 19','Encerradas',[],[['21/09',14]]),'OC-10505':O('OC-10505','Colheita · semana 39','Pivô 23','Encerradas',[],[['22/09',20]])});
  const L=carLotes(c); const ks=Object.keys(L).filter(k=>L[k].tipo==='campo');
  ok('8k duas colheitas (OS-0505 e OC-10505) geram dois lotes distintos (LC-0505-1 e LC-OC10505-1)', ks.length===2&&L['LC-0505-1']&&L['LC-0505-1'].tal==='PV19'&&L['LC-OC10505-1']&&L['LC-OC10505-1'].tal==='PV23', ks); }
{ // 8l "carência até" = último dia em carência; no dia seguinte a colheita é liberada
  const c=CEN({'OS-T':O('OS-T','Pulverização · antracnose','Pivô 23','Em conferência',['Tebuconazol 200 EC'],[['20/09',60]]),
               'OS-K':O('OS-K','Colheita · semana 39','Pivô 23','A liberar',[],[],{janela:'26/09'}),'OS-L':O('OS-L','Colheita · semana 39','Pivô 23','A liberar',[],[],{janela:'27/09'})});
  const e=carEstado(c,'PV23',H), b26=carBloqColheita(c,c.ordens['OS-K'],'liberar'), b27=carBloqColheita(c,c.ordens['OS-L'],'liberar');
  ok('8l aplicação 20/09 + 7 dias: rótulo "carência até 26/09"; colheita em 26/09 impedida, em 27/09 liberada', carRot(e)==='carência até 26/09'&&!!b26&&/até 26\/09/.test(b26.t)&&!b27, [carRot(e),b26&&b26.t,b27]); }
{ // 8m liberação comercial do lote: impedida fora de "conforme no escopo"; dado novo suspende a liberação já feita
  const c=CEN({'OS-T':O('OS-T','Pulverização · antracnose','Pivô 23','Encerradas',['Tebuconazol 200 EC'],[['05/09',60]]),
               'OS-H':O('OS-H','Colheita · semana 39','Pivô 23','Em execução',[],[['22/09',20]])});
  const lid=Object.keys(carLotes(c))[0]; c.car.dest={}; c.car.dest[lid]='EXP-UE';
  const e1=TRY(()=>carc_liberar_lote(c,lid)); c.car.dest[lid]='MI-BR'; const e2=TRY(()=>carc_liberar_lote(c,lid)); const a=carAvaliar(c,lid);
  c.ordens['OS-S']=O('OS-S','Pulverização · antracnose','Pivô 23','Em execução',['Tebuconazol 200 EC'],[['20/09',60,'Provisório',false]]); const b=carAvaliar(c,lid);
  ok('8m UE (regra não carregada): liberar impedido com motivo e dono; mercado interno conforme: liberado; apontamento tardio de 20/09 → Não conforme e liberação suspensa',
     /Liberação comercial impedida/.test(e1)&&/não carregada/.test(e1)&&e2===''&&a.lib&&a.lib.valida&&b.st==='nao_conforme'&&!!b.libSusp&&/suspensa/.test(b.libSusp.t), [e1,e2,a.lib,b.st,b.libSusp]); }

print(JSON.stringify(R));
