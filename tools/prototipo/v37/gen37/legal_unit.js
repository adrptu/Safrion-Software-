// Frente E1 (CTL-1) · trava legal única na O.S. (cenUsoLegal, a mesma do AG-01): liberar e ajustar recusam uso fora do registro, dose fora da
// bula e nº máximo de aplicações; alertas recolhidos para a confirmação. Executor: legal_unit_test.py (node ou jsc, sem navegador).
// Parte 1 (26 casos, ctl/e2/e1_unit.js) e parte 2 (5 casos da revisão C1–C3, ctl/e2/e1_extra.js). Na base sem a regra, os stubs abaixo fazem os casos falharem.
{ // parte 1
// E1 · testes unitários da regra legal única (sem navegador). Saída: uma linha por caso + resumo.
if(typeof osUsoErro!=='function'){ globalThis.osUsoErro=()=>''; globalThis.osUsoItem=()=>''; globalThis.cenUsoLegal=()=>({tr:[],al:[]}); }   // base 884620c: a regra não existe
const R=[]; const ok=(n,c,info)=>{ R.push({n,ok:!!c}); console.log((c?'OK    ':'FALHA ')+n+(c?'':' · '+JSON.stringify(info).slice(0,400))); };
const T=(f)=>{ try{ const r=f(); return {ok:true,msg:r&&r.msg}; }catch(e){ return {ok:false,msg:e.message}; } };
const C=()=>cenClone(CEN0);
// ---- positivos
{ const c=C(); const r=T(()=>osc_liberar(c,'OS-0430',false,'','Ana')); ok('P1 OS-0430 como está (Glifosato 2 · 2,4-D 1 · Óleo 0,5 L/ha em soja T1-A) libera', r.ok&&c.ordens['OS-0430'].etapa==='Liberadas', r); }
{ const c=C(); const r=T(()=>osc_ajustar(c,'OS-0430',150,{'Glifosato 480':1.8},'',[],[],true,'Ana')); const o=c.ordens['OS-0430'];
  ok('P2 ajuste 150 ha + Glifosato 1,8 L/ha (os_cenario_test 14) libera a v2 com 270 L', r.ok&&o.etapa==='Liberadas'&&o.ins[0].tot===270&&/\bv2\b/.test(o.versao), [r,o.versao,o.ins[0]]); }
for(const d of [1.5,3]){ const c=C(); const r=T(()=>osc_ajustar(c,'OS-0430',160,{'Glifosato 480':d},'',[],[],true,'Ana')); ok('P3 limite da bula: Glifosato '+d+' L/ha libera', r.ok, r); }
{ const c=C(); const r=T(()=>osc_ajustar(c,'OS-0430',160,{'Óleo mineral':2},'',[],[],true,'Ana')); ok('P4 Óleo mineral 2 L/ha (adjuvante) não passa pela regra de agrotóxico', r.ok, r); }
{ const c=C(); const r=T(()=>osc_liberar(c,'OS-0431',false,'','Ana')); ok('P5 OS-0431 (semente e MAP) libera: fertilizante e semente fora da regra', r.ok, r); }
{ cenReset(); mipReset(); const s=mipGet(); const v=s.vis['VIS-054']; const u=mipElig(v)[0];
  const e=mipEmitir(null,'VIS-054',{ator:'Ana',chave:'TESTE-VIS-054-P6',dver:((v.dec&&v.dec.ver)||0)+1,kind:'controlar',prod:u.id,dose:String(u.dmin),area:String(mipT(v).area),data:'2026-09-28'}); const c=cenGet();
  if(!e.erro){ const o=c.ordens[e.os]; const l=cenLote(c,o.ins[0].p); if(l&&cenDisp(l)<o.ins[0].tot) l.fisico+=o.ins[0].tot; }
  const r=e.erro?{ok:false,msg:e.erro}:T(()=>osc_liberar(c,e.os,false,'','Ana'));
  ok('P6 AG-01 → O.S.: VIS-054 (PV02 mamão × mosca-branca) '+(u&&u.nome)+' '+(u&&u.dmin)+' '+(u&&u.un)+'/ha emite e a O.S. libera', r.ok, [e,r]); }
{ const c=C(); osc_cancelar(c,'OS-0430','teste',['','',''],'Ana'); osc_nova(c,{id:'OS-0440',tipo:'Dessecação pré-plantio · repasse',talhao:'T1-A',area:160,versao:'v1',resp:'Marcos',ins:[{p:'Glifosato 480',dose:2,un:'L',tot:320}],selos:[],saf:'2026/27'});
  c.ordens['OS-0440'].osc.novo.saf='2026/27'; const r=T(()=>osc_liberar(c,'OS-0440',false,'','Ana')); ok('P7 OS-0430 cancelada sem execução não conta: a nova dessecação no T1-A libera', r.ok, r); }
{ const c=C(); osc_nova(c,{id:'OS-0440',tipo:'Dessecação pré-plantio',talhao:'T3',area:96,versao:'v1',resp:'Marcos',ins:[{p:'Glifosato 480',dose:2,un:'L',tot:192}],selos:[]});
  c.ordens['OS-0440'].osc.novo.saf='2026/27'; const r=T(()=>osc_liberar(c,'OS-0440',false,'','Ana')); ok('P8 OS-0415 (T3, safra 2025/26) não conta para a safra 2026/27: Glifosato no T3 libera', r.ok, r); }
{ const c=C(); osc_nova(c,{id:'OS-0440',tipo:'Dessecação pré-plantio',talhao:'T1-B',area:152,versao:'v1',resp:'Marcos',ins:[{p:'Glifosato 480',dose:2,un:'L',tot:304}],selos:[]});
  c.ordens['OS-0440'].osc.novo.saf='2026/27'; T(()=>osc_liberar(c,'OS-0430',false,'','Ana')); const r=T(()=>osc_liberar(c,'OS-0440',false,'','Ana'));
  ok('P9 parcela: dessecação no T1-B libera mesmo com a OS-0430 (T1-A) liberada — a contagem é por parcela', r.ok, r); }
{ const c=C(); osc_nova(c,{id:'OS-0440',tipo:'Herbicida pós-emergente',talhao:'T1-A',area:160,versao:'v1',resp:'Marcos',ins:[{g:'Herbicidas',p:'Atrazina 500',dose:3,un:'L',tot:480}],selos:[]});
  const o=c.ordens['OS-0440']; o.osc.novo.saf='Safrinha 2027'; o.osc.novo.cultura='Milho';
  const e1=osUsoErro(c,o); o.osc.novo.cultura=''; const e2=osUsoErro(c,o);
  ok('P10 cultura do cultivo da ordem (safrinha de milho no T1-A): Atrazina 500 3 L/ha passa na regra', e1==='', e1);
  ok('N10 a mesma Atrazina sem a cultura do cultivo cai na cultura atual do talhão (soja) e é recusada', /sem registro para soja/.test(e2), e2); }
{ const c=C(); const e=osUsoItem(c,{id:'X',talhao:'T1-A'},{g:'Inseticidas',p:'Inseticida B',dose:0.3,un:'L'}); const k=cenUsoLegal([{sit:'Vigente',dmin:0.8,dmax:1,un:'kg',mx:2,conf:true}],'soja',0.3,'L',0);
  ok('N11 unidade da ordem (L/ha) diferente da bula (kg/ha): trava "unidade diferente da bula" (antes só alerta; CTL-1 rev. 1)', /^Inseticida B 0,3 L\/ha em T1 \(T1-A\): dose em L\/ha e bula em 0,8–1 kg\/ha: unidade diferente da bula/.test(e)&&k.tr.length===1&&/corrija a unidade/.test(k.tr[0]), [e,k]); }
{ const c=C(); const e=osUsoItem(c,{id:'X',talhao:'T1-A'},{g:'Sementes',p:'Semente de milho Híbrido AG 8700',dose:20,un:'kg'});
  ok('P12 produto fora do cadastro classificado pelo plano como semente fica fora da regra', e==='', e); }
// ---- negativos
{ const c=C(); const r=T(()=>osc_ajustar(c,'OS-0430',160,{'Glifosato 480':7.5},'',[],[],true,'Ana')); const o=c.ordens['OS-0430'];
  ok('N1 Glifosato 7,5 L/ha (2,5 × o máximo) recusado com a faixa da bula', !r.ok&&/dose fora da bula: 1,5–3 L\/ha/.test(r.msg), r); console.log('       msg:', r.msg); }
for(const d of [1.49,3.01]){ const c=C(); const r=T(()=>osc_ajustar(c,'OS-0430',160,{'Glifosato 480':d},'',[],[],true,'Ana')); ok('N2 fora do limite: Glifosato '+d+' L/ha recusado', !r.ok&&/fora da bula/.test(r.msg), r); }
{ const c=C(); const r=T(()=>osc_ajustar(c,'OS-0430',160,{},'',[],[{p:'Abamectina 18 EC',dose:0.5,un:'L'}],true,'Ana')); ok('N3 Abamectina 18 EC (registro só em mamão) em soja recusada', !r.ok&&/sem registro para soja/.test(r.msg), r); console.log('       msg:', r.msg); }
{ const c=C(); const r=T(()=>osc_ajustar(c,'OS-0501',49.31,{},'',[],[{p:'Fungicida A',dose:0.5,un:'L'}],true,'Ana')); ok('N4 Fungicida A no Pivô 13 (mamão) recusado', !r.ok&&/sem registro para mamão/.test(r.msg), r); console.log('       msg:', r.msg); }
{ const c=C(); osc_nova(c,{id:'OS-0440',tipo:'Dessecação pré-plantio · repasse',talhao:'T1-A',area:160,versao:'v1',resp:'Marcos',ins:[{p:'Glifosato 480',dose:2,un:'L',tot:320}],selos:[]});
  c.ordens['OS-0440'].osc.novo.saf='2026/27'; T(()=>osc_liberar(c,'OS-0430',false,'','Ana')); const r=T(()=>osc_liberar(c,'OS-0440',false,'','Ana'));
  ok('N5 2ª dessecação com Glifosato 480 no T1-A recusada (bula: 1 aplicação no ciclo)', !r.ok&&/1 de 1/.test(r.msg), r); console.log('       msg:', r.msg); }
{ const c=C(); const v0=c.ordens['OS-0430'].versao; const r=T(()=>osc_ajustar(c,'OS-0430',160,{'Glifosato 480':7.5},'',[],[],false,'Ana'));
  ok('N6 "Salvar ajuste" sem liberar também recusa e não grava a versão', !r.ok&&c.ordens['OS-0430'].versao===v0, [r,c.ordens['OS-0430'].versao]); }
{ const c=C(); osc_nova(c,{id:'OS-0440',tipo:'Controle de ácaro',talhao:'Pivô 6',area:62.79,versao:'v1',resp:'Lúcia',ins:[{p:'Abamectina 18 EC',dose:0.5,un:'L',tot:31.4}],selos:[]});
  c.ordens['OS-0440'].osc.novo.saf='2026/27'; const r=T(()=>osc_liberar(c,'OS-0440',false,'','Ana'));
  ok('N7 Pivô 6: Abamectina já aplicada em 28/08 (caderno) + OS-0504 → nova O.S. recusada "2 de 2"', !r.ok&&/2 de 2/.test(r.msg), r); console.log('       msg:', r.msg); }
{ const c=C(); const o={id:'X',talhao:'T1'}; const m1=typeof osUsoItem==='function'?osUsoItem(c,o,{p:'Paraquate 200 SL',dose:1.5,un:'L'}):'(sem regra)';
  const m2=typeof osUsoItem==='function'?osUsoItem(c,o,{p:'Produto sem cadastro',dose:1,un:'L'}):'(sem regra)';
  ok('N8 Paraquate 200 SL em soja: "registro cancelado: uso proibido"', /registro cancelado/.test(m1), m1);
  ok('N9 produto fora de todo cadastro é tratado como sem registro (nunca liberado por falta de dado)', /sem registro para soja/.test(m2), m2); }
// ---- painel e quem resolve (osMerge/osProx, o mesmo do Mapa)
{ const c=C(); c.ordens['OS-0430'].ins[0].dose=7.5; c.ordens['OS-0430'].ins[0].tot=1200;
  const o=osMerge({id:'OS-0430',talhao:'T1-A',etapa:'A liberar',area:160,ins:[],selos:[],agua:false,dono:'Ana (agrônoma)',cond:'Ana confere. Próximo passo: liberar para execução.',janela:'24/09'},c.ordens['OS-0430'],c);
  const b=osProx(o).b||{}; ok('M1 painel: selo "Fora do registro · Glifosato 480", dono Ana, "Liberar bloqueado" com quem resolve = agrônoma (não Suprimentos)',
    o.selos.some(s=>s.t==='Fora do registro · Glifosato 480'&&s.c==='red')&&o.dono==='Ana (agrônoma)'&&/^Liberar bloqueado: Glifosato 480 7,5 L\/ha/.test(b.t||'')&&/Ana \(agrônoma\)/.test(b.q||'')&&!/Suprimentos/.test(b.q||''), [o.selos,o.dono,b]);
  console.log('       painel:', b.t, '· Quem resolve:', b.q); }
// ---- a semente inteira pela regra (todas as fases, só leitura)
if(typeof osUsoErro==='function'){ const c=C(); const f=Object.keys(c.ordens).map(k=>[k,c.ordens[k].etapa,osUsoErro(c,c.ordens[k])]).filter(x=>x[2]);
  console.log('SEMENTE · '+Object.keys(c.ordens).length+' ordens · fora da regra:', JSON.stringify(f));
  /* G1 (CTL-1, commit 3): a OS-0424 saiu do milho do P2 (Fungicida A sem registro) para a soja do T1-B a 0,5 L/ha; nenhuma ordem da semente falha */
  ok('S1 semente: nenhuma ordem fora da regra legal (osUsoErro vazio em todas, em todas as fases; OS-0424 em soja T1-B 0,5 L/ha)', f.length===0&&Object.keys(c.ordens).length>20&&!osUsoErro(c,c.ordens['OS-0424']), f); }
console.log(MODO+': '+R.filter(x=>x.ok).length+'/'+R.length+' passaram');

}
{ // parte 2
// casos novos da revisão (C1–C3). Saída: uma linha por caso + resumo.
if(typeof osUsoErro!=="function"){ globalThis.osUsoErro=()=>""; globalThis.osUsoItem=()=>""; }
const R=[]; const ok=(n,c,info)=>{ R.push(!!c); console.log((c?'OK    ':'FALHA ')+n+(c?'':' · '+JSON.stringify(info).slice(0,400))); };
const T=(c,id)=>{ try{ osc_liberar(c,id,false,'','Ana'); return ''; }catch(e){ return e.message; } };
const nova=(c,id,tal,ins,saf)=>osc_nova(c,{id,tipo:'Teste',talhao:tal,area:160,versao:'v1',resp:'Marcos',saf:saf||'2026/27',ins,selos:[]});
// D1 · duas ordens A liberar com o mesmo produto (bula: 1 aplicação): nenhuma bloqueia a outra; a primeira a liberar ocupa a vaga
{ const c=cenClone(CEN0); nova(c,'OS-0440','T1-A',[{p:'Glifosato 480',dose:2,un:'L',tot:320}]);
  const a0=T(cenClone(c),'OS-0430'), b0=T(cenClone(c),'OS-0440'); const a1=T(c,'OS-0440'), b1=T(c,'OS-0430');
  ok('D1 duas A liberar: cada uma libera sozinha; liberada a OS-0440, a OS-0430 é recusada nomeando a OS-0440', a0===''&&b0===''&&a1===''&&/1 de 1 \(OS-0440\)/.test(b1), [a0,b0,a1,b1]); }
// D2 · a mensagem nomeia o caderno de campo e a O.S. contados (Pivô 6)
{ const c=cenClone(CEN0); nova(c,'OS-0440','Pivô 6',[{p:'Abamectina 18 EC',dose:0.5,un:'L',tot:31.4}]); const e=T(c,'OS-0440');
  ok('D2 Pivô 6: "2 de 2 (OS-0504, caderno 28/08)"', /2 de 2 \(OS-0504, caderno 28\/08\)/.test(e), e); }
// D3 · O.S. cancelada sem execução continua fora da conta; A liberar também
{ const c=cenClone(CEN0); nova(c,'OS-0440','Pivô 6',[{p:'Abamectina 18 EC',dose:0.5,un:'L',tot:31.4}]); osc_cancelar(c,'OS-0504','teste',['','',''],'Ana');
  const e=T(c,'OS-0440'); ok('D3 OS-0504 cancelada: Pivô 6 tem 1 de 2 (caderno) e a nova libera', e==='', e); }
// A1 · alertas recolhidos para a confirmação (antes descartados): produto em reavaliação e uso não conferido (M19 da revisão do CTL-1)
{ const c=cenClone(CEN0); const E='Epoxiconazol + piraclostrobina 50+133 SE'; const o={id:'X',talhao:'T1-A',ins:[{p:'Fungicida A',dose:0.5,un:'L'},{p:E,dose:0.5,un:'L'},{p:'Cletodim 240',dose:0.4,un:'L'}]};
  const al=[]; const e=osUsoErro(c,o,al);
  ok('A1 sem trava e com 3 alertas: Epoxiconazol em reavaliação e não conferido, Cletodim não conferido (T1 e T1-A não repetem)', e===''&&al.length===3&&al[0]===E+': produto em reavaliação na Anvisa.'&&/^Epoxiconazol .*: uso não conferido/.test(al[1])&&/^Cletodim 240: uso não conferido/.test(al[2]), [e,al]); console.log('       ', JSON.stringify(al)); }
// R1 · revisão do CTL-1, achado 1: Inseticida B (bula em kg/ha) incluído em L/ha no ajuste é recusado em qualquer dose; nada gravado
for(const d of [0.3,5]){ const c=cenClone(CEN0); let m=''; try{ osc_ajustar(c,'OS-0430',10,{},'',[],[{p:'Inseticida B',dose:d,un:'L',g:'Inseticidas'}],true,'Ana'); }catch(x){ m=x.message; } const o=c.ordens['OS-0430'];
  ok('R1 ajuste com Inseticida B '+d+' L/ha: recusado pela unidade, v1 e A liberar, sem CMD-42', /unidade diferente da bula/.test(m)&&o.etapa==='A liberar'&&!/v2/.test(o.versao)&&!((o.osc||{}).ev||[]).length, [m,o.etapa,o.versao]); }
// R2 · achado 2: produto registrado só para tratamento de sementes recusado como pulverização; aceito em ordem de tratamento de sementes
{ const c=cenClone(CEN0); let m=''; try{ osc_ajustar(c,'OS-0430',4,{},'',[],[{p:'Fungicida TS',dose:5,un:'L',g:'Fungicidas'}],true,'Ana'); }catch(x){ m=x.message; }
  const ts={id:'X',tipo:'Tratamento de sementes',talhao:'T1-A',ins:[{p:'Fungicida TS',dose:0.1,un:'L'}]};
  ok('R2 Fungicida TS 5 L/ha na dessecação da soja: recusado ("só para tratamento de sementes"); na ordem de tratamento de sementes passa', m==='Fungicida TS em T1 (T1-A): registro em soja só para tratamento de sementes.'&&c.ordens['OS-0430'].etapa==='A liberar'&&osUsoErro(c,ts)==='', [m,osUsoErro(c,ts)]); }
// R3 · achado 1 (complemento): o Salvar e liberar do ajuste devolve os alertas (antes só a confirmação do Liberar mostrava)
{ const c=cenClone(CEN0); let m=''; try{ m=osc_ajustar(c,'OS-0430',10,{},'',[],[{p:'Cletodim 240',dose:0.4,un:'L',g:'Herbicidas'}],true,'Ana').msg; }catch(x){ m='ERRO '+x.message; }
  ok('R3 ajuste com Cletodim (uso não conferido): liberado e a mensagem traz "Atenção (não bloqueia): Cletodim 240: uso não conferido"', /ajustada para v2 e liberada/.test(m)&&/Atenção \(não bloqueia\): Cletodim 240: uso não conferido/.test(m), m); }
// U1 · erro junto ao campo: com a ordem do cenário, a tela dá o mesmo resultado do comando (com o objeto da tela, não)
{ const c=cenClone(CEN0); osc_nova(c,{id:'OS-0440',tipo:'Herbicida',talhao:'T1-A',area:160,versao:'v1',resp:'Marcos',saf:'Safrinha 2027',cultura:'Milho safrinha',ins:[{g:'Herbicidas',p:'Atrazina 500',dose:3,un:'L',tot:480}],selos:[]});
  const co=c.ordens['OS-0440'], tela=osMerge(co.osc.novo,co,c), x={p:'Atrazina 500',un:'L',dose:3,g:'Herbicidas'};
  ok('U1 Atrazina na safrinha de milho: ordem do cenário passa (como o comando); objeto da tela recusaria "sem registro para soja"', osUsoItem(c,c.ordens[tela.id],x)===''&&/sem registro para soja/.test(osUsoItem(c,tela,x)), [osUsoItem(c,c.ordens[tela.id],x),osUsoItem(c,tela,x)]); }
console.log(MODO+': '+R.filter(Boolean).length+'/'+R.length+' passaram');

}
