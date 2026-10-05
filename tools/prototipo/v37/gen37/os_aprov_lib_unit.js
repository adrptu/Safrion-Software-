// Frente F (CTL-1) · unitário sem navegador: liberar grava aprovação (CMD-42) e liberação (CMD-06) separadas, numa só confirmação. Executor: os_aprov_lib_test.py.
const R=[]; function ok(n,c,info){ R.push(n); print((c?'OK   ':'FALHA')+' '+n+(c?'':' · '+JSON.stringify(info===undefined?'':info).slice(0,500))); if(!c) ok.f=(ok.f||0)+1; }
const T=(f)=>{ try{ f(); return ''; }catch(e){ return String(e.message||e); } };
const L=(c,id)=>cenMudar(null,k=>osc_liberar(k,id,false,''));
const ev=(id)=>((cenGet().ordens[id].osc||{}).ev||[]);
const AGRO='Ana (agrônoma)';
// P1 · OS-0430 (3 produtos, 160 ha): dois registros, versão, escopo e reserva do seed
cenReset(); let r=L(null,'OS-0430'); let e=ev('OS-0430'); let c=cenGet();
ok('P1a liberar OS-0430 grava 2 registros: CMD-42 e CMD-06, ambos por Ana (agrônoma), versão v1',
  e.length===2&&e[0].cmd==='CMD-42'&&e[1].cmd==='CMD-06'&&e.every(x=>x.por===AGRO&&x.v==='v1'), e);
ok('P1b aprovação com escopo: 160 ha · Glifosato 480 2 L/ha, 2,4-D 806 1 L/ha, Óleo mineral 0,5 L/ha', e[0]&&/^v1 aprovada por Ana \(agrônoma\) às \d\d:\d\d · 160 ha · Glifosato 480 2 L\/ha, 2,4-D 806 1 L\/ha, Óleo mineral 0,5 L\/ha \(CMD-42\)$/.test(e[0].t), e[0]&&e[0].t);
ok('P1c liberação cita a requisição: "v1 liberada por Ana (agrônoma) às hh:mm · REQ-041 reservada no Estoque (CMD-06)"', e[1]&&/^v1 liberada por Ana \(agrônoma\) às \d\d:\d\d · REQ-041 reservada no Estoque \(CMD-06\)$/.test(e[1].t), e[1]&&e[1].t);
ok('P1d aviso: texto antigo preservado + aprovação; sem segundo "Próximo passo" (o do painel é o único)', r.msg==='OS-0430 liberada. REQ-041 reservou no Estoque: Glifosato 480 320 L, 2,4-D 806 160 L, Óleo mineral 80 L. v1 aprovada e liberada por Ana (agrônoma).'
  &&ords().find(x=>x.id==='OS-0430').cond==='Liberada · REQ-041 reservou os insumos no Estoque. Próximo passo: iniciar na janela 25/09 (DAP −20).', [r,ords().find(x=>x.id==='OS-0430').cond]);
ok('P1e efeito no Estoque igual ao de hoje: G26-14 reserva 320 L, D26-01 160 L, O26-05 80 L', c.lotes['Glifosato 480|G26-14'].reservado===320&&c.lotes['2,4-D 806|D26-01'].reservado===160&&c.lotes['Óleo mineral|O26-05'].reservado===80);
const og=ords().find(x=>x.id==='OS-0430').orig;
ok('P1f a Origem da tela mostra as 2 linhas depois das de origem (4 registros)', og.length===4&&/CMD-42\)$/.test(og[2])&&/CMD-06\)$/.test(og[3]), og);
// N1 · repetir a confirmação não duplica
const rev=cenGet().rev; r=L(null,'OS-0430');
ok('N1 repetir a confirmação: recusada pelo estado, sem 3º registro e sem gravar', r.erro==='OS-0430 não está em A liberar.'&&ev('OS-0430').length===2&&cenGet().rev===rev, [r,ev('OS-0430').length]);
// P2 · OS-0511 (Lagoa Grande, sem insumos)
const nmov=cenGet().movs.length; r=L(null,'OS-0511'); e=ev('OS-0511');
ok('P2 sem insumos: 2 registros, CMD-06 sem requisição, nenhuma reserva', e.length===2&&/^v1 aprovada por Ana \(agrônoma\) às \d\d:\d\d · 36,17 ha · sem insumos \(CMD-42\)$/.test(e[0].t)&&/^v1 liberada por Ana \(agrônoma\) às \d\d:\d\d \(CMD-06\)$/.test(e[1].t)
  &&cenGet().movs.length===nmov&&r.msg==='OS-0511 liberada. Sem insumos a reservar: nenhuma requisição no Estoque. v1 aprovada e liberada por Ana (agrônoma).', [e,r]);
// P3 · OS-0501 ajustada (Glifosato 3 → 2,5 L/ha) e liberada: aprova a v2 com a dose nova
r=cenMudar(null,k=>osc_ajustar(k,'OS-0501',49.31,{'Glifosato 480':2.5},'',[],[],true)); e=ev('OS-0501'); const o501=cenGet().ordens['OS-0501'];
ok('P3 ajustar e liberar: aprova a v2 (Glifosato 480 2,5 L/ha), REQ-042 reserva 123,28 L; linha do ajuste antes da aprovação',
  e.length===2&&e[0].v==='v2'&&/· 49,31 ha · Glifosato 480 2,5 L\/ha, Óleo mineral 0,5 L\/ha \(CMD-42\)$/.test(e[0].t)&&/REQ-042 reservada/.test(e[1].t)&&o501.osc.aj[0].t.indexOf('ajustada por Ana (agrônoma)')>0
  &&cenGet().lotes['Glifosato 480|G26-14'].reservado===320+123.28&&/^OS-0501 ajustada para v2 e liberada\. REQ-042/.test(r.msg), [e,r]);
// N2 · Ureia sem lote: recusado, nada gravado
cenReset(); r=L(null,'OS-0418');
ok('N2 OS-0418 sem lote de Ureia 45%: recusa com o motivo do Estoque e nenhum registro de aprovação', r.erro==='Sem lote de Ureia 45% no Estoque.'&&ev('OS-0418').length===0&&cenGet().ordens['OS-0418'].etapa==='A liberar', r);
// P4 · fertirrigação (produto na água) volta a exigir aprovação: recebida a Ureia, a liberação grava CMD-42
cenMudar(null,k=>cenReceber(k,'Ureia 45%','U26-01',1140,'kg','Galpão 1','12/2027','NF-9001',true)); r=L(null,'OS-0418'); e=ev('OS-0418');
ok('P4 OS-0418 fertirrigação v2: CMD-42 por Ana com 95 ha · Ureia 45% 12 kg/ha; REQ-038 reserva 1.140 kg', e.length===2&&e[0].v==='v2'&&/· 95 ha · Ureia 45% 12 kg\/ha \(CMD-42\)$/.test(e[0].t)&&/REQ-038 reservada/.test(e[1].t)&&cenGet().lotes['Ureia 45%|U26-01'].reservado===1140, [e,r]);
// N3 · saldo insuficiente: recusado, nada gravado
cenReset(); cenMudar(null,k=>{ k.lotes['Glifosato 480|G26-14'].fisico=100; return {msg:''}; }); r=L(null,'OS-0430');
ok('N3 saldo insuficiente (Glifosato 100 L para 320 L): recusa e nenhum registro', r.erro==='Saldo insuficiente de Glifosato 480: 100 L disponíveis para 320 L.'&&ev('OS-0430').length===0, r);
// N4 · água só com água (DEC-2609-10): liberada pela prontidão, sem CMD-42
cenReset(); cenMudar(null,k=>{ k.ordens['OS-W']={id:'OS-W',tipo:'Irrigação · água',talhao:'P2',area:80,etapa:'A liberar',versao:'v1',realizado:0,saldo:80,resp:'João',ins:[],req:null,selos:[],ap:[],reservado:false}; return {msg:''}; });
r=cenMudar(null,k=>osc_liberar(k,'OS-W',true,'')); 
ok('N4 água sem produto: Liberadas pela prontidão, sem registro de agrônomo', cenGet().ordens['OS-W'].etapa==='Liberadas'&&ev('OS-W').length===0&&!/aprovada|agrônom/.test(r.msg), r);
// N4b · revisão do CTL-1, achado 3: o sinal "água" vindo da tela não libera ordem com produto (o comando confere); N4c · nem ordem já liberada (M16)
r=cenMudar(null,k=>osc_liberar(k,'OS-0430',true,''));
ok('N4b sinal água na OS-0430 (herbicidas): recusa "exige aprovação agronômica", segue A liberar, sem CMD-42 e sem reserva', /OS-0430 tem produto: exige aprovação agronômica/.test(r.erro||'')&&cenGet().ordens['OS-0430'].etapa==='A liberar'&&ev('OS-0430').length===0&&!cenGet().lotes['Glifosato 480|G26-14'].reservado, r);
r=cenMudar(null,k=>osc_liberar(k,'OS-W',true,''));
ok('N4c água na OS-W já liberada: recusa "não está em A liberar"', /OS-W não está em A liberar/.test(r.erro||''), r);
// N5 · ajuste sem liberar (liberação impedida por outro motivo): grava a versão, sem aprovação nem liberação
r=cenMudar(null,k=>osc_ajustar(k,'OS-0430',150,{},'',[],[],false));
ok('N5 ajustar sem liberar: v2 gravada, etapa A liberar, nenhum CMD-42/CMD-06', cenGet().ordens['OS-0430'].etapa==='A liberar'&&ev('OS-0430').length===0&&/v2/.test(cenGet().ordens['OS-0430'].versao), r);
// N6 · a checagem prévia do bloqueio (cópia do cenário) não vaza registro
cenReset(); const pre=osLibErro({id:'OS-0430'},cenGet());
ok('N6 osLibErro (prévia na cópia) = "" e o cenário gravado continua sem registro', pre===''&&ev('OS-0430').length===0&&cenGet().ordens['OS-0430'].etapa==='A liberar', pre);
// N7 · colheita impedida pela carência: recusa antes de qualquer registro
cenReset(); cenMudar(null,k=>{ k.ordens['OS-0442']={id:'OS-0442',tipo:'Colheita · Soja',talhao:'T1-A',area:160,etapa:'A liberar',versao:'v1',realizado:0,saldo:160,resp:'Sérgio',ins:[],req:null,selos:[],ap:[],reservado:false}; return {msg:''}; });
r=L(null,'OS-0442');
ok('N7 colheita no T1-A com carência em curso: recusa e nenhum registro', !!r.erro&&/carência/.test(r.erro)&&ev('OS-0442').length===0, r);
// versão exibida
ok('V osVn: "REC-014 v2 · v1" → v1 (OS-0431); "plano CAFE-AR · v1" → v1 (OS-0425); "v1" → v1', typeof osVn==='function'&&osVn('REC-014 v2 · v1')==='v1'&&osVn('plano CAFE-AR · v1')==='v1'&&osVn('v1')==='v1');
// P5 · ordem nova (sem executor "—"): aprova com o escopo do plano; aviso sem "—"
cenReset(); cenMudar(null,k=>{ k.ordens['OS-0440']={id:'OS-0440',tipo:'Tratamento de sementes',talhao:'T1-A',area:160,etapa:'A liberar',versao:'v1',realizado:0,saldo:160,resp:'—',ins:[{p:'Fungicida TS',dose:0.1,un:'L',tot:16},{p:'Inoculante líquido',dose:0.2,un:'L',tot:32}],req:null,selos:[],ap:[],reservado:false}; return {msg:''}; });
const r5=L(null,'OS-0440');
ok('P5 ordem nova: CMD-42 "160 ha · Fungicida TS 0,1 L/ha, Inoculante líquido 0,2 L/ha" e aviso sem "—"', !/—/.test(r5.msg||'')&&/v1 aprovada e liberada por Ana \(agrônoma\)\.$/.test(r5.msg||'')
  &&/^v1 aprovada por Ana \(agrônoma\) às \d\d:\d\d · 160 ha · Fungicida TS 0,1 L\/ha, Inoculante líquido 0,2 L\/ha \(CMD-42\)$/.test(ev('OS-0440')[0].t), [r5,ev('OS-0440')]);
// N8 · ajuste tira o único produto de ordem com requisição aberta antes (OS-0418 · REQ-038 sem lote): o CMD-06 não afirma reserva que não houve
cenReset(); r=cenMudar(null,k=>osc_ajustar(k,'OS-0418',95,{},'',['Ureia 45%'],[],true)); e=ev('OS-0418');
ok('N8 OS-0418 sem a Ureia: CMD-42 da v3 "95 ha · sem insumos" e CMD-06 sem "reservada"', e.length===2&&/^v3 aprovada por .* · 95 ha · sem insumos \(CMD-42\)$/.test(e[0].t)&&/^v3 liberada por Ana \(agrônoma\) às \d\d:\d\d \(CMD-06\)$/.test(e[1].t)&&cenGet().ordens['OS-0418'].reservado===false, [e,r]);
// V2 · osVn igual à regra de osc_ajustar (\bvN\b, o último) e com padrão v1
ok('V2 osVn: "v3 no saldo de 70 ha (KCl −12 %) · 30 ha na v2" → v2 (o último, como osc_ajustar); "" → v1', typeof osVn==='function'&&osVn('v3 no saldo de 70 ha (KCl −12 %) · 30 ha na v2')==='v2'&&osVn('')==='v1');
// D · dose com 3 casas (1,125 L/ha, dentro da bula do 2,4-D em soja: 0,8–1,5) aparece igual na linha do ajuste e na aprovação; reserva 1,125 × 160 = 180 L
cenReset(); r=cenMudar(null,k=>osc_ajustar(k,'OS-0430',160,{'2,4-D 806':1.125},'',[],[],true)); e=ev('OS-0430');
ok('D dose 1,125 L/ha sem arredondar na trilha (ajuste e CMD-42) e 180 L reservados', /2,4-D 806 1,125 L\/ha/.test((e[0]||{}).t||'')&&/2,4-D 806 1 → 1,125 L\/ha/.test(((cenGet().ordens['OS-0430'].osc||{}).aj||[{}])[0].t||'')&&cenGet().lotes['2,4-D 806|D26-01'].reservado===180, [r,e,(cenGet().ordens['OS-0430'].osc||{}).aj]);
// N9 · CTL-1 (Frente E1): a trava legal recusa antes de qualquer gravação: nem CMD-42, nem CMD-06, nem versão nova, nem reserva
cenReset(); r=cenMudar(null,k=>osc_ajustar(k,'OS-0430',160,{'Glifosato 480':7.5},'',[],[],true)); const o9=cenGet().ordens['OS-0430'];
cenMudar(null,k=>{ k.ordens['OS-0430'].ins[0].dose=7.5; k.ordens['OS-0430'].ins[0].tot=1200; return {msg:''}; }); const r9=L(null,'OS-0430');
ok('N9 recusa legal (Glifosato 7,5 L/ha, bula 1,5–3) no ajuste e na liberação: nenhum CMD-42/CMD-06, versão v1 e nada reservado',
  !!r.erro&&/dose fora da bula/.test(r.erro)&&!!r9.erro&&/dose fora da bula/.test(r9.erro)&&ev('OS-0430').length===0&&o9.versao==='v1'
  &&cenGet().ordens['OS-0430'].etapa==='A liberar'&&cenGet().lotes['Glifosato 480|G26-14'].reservado===0, [r,r9,ev('OS-0430'),o9.versao]);
print('TOTAL '+R.length+' · falhas '+(ok.f||0));
