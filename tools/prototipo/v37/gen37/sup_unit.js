// SUP · Suprimentos simplificado (docs/suprimentos-simplificado, §6 e §9.2) · node, sem navegador. Executor: sup_unit_test.py.
// Regras do Estoque sobre o cenário compartilhado (cenario.js), com o perfil de quem age (G2_PERFIS, CTL-3) e o padrão (2) de 05/10/2026
// (PEND-CTL-02): quem decide o que exige papel (laudo, ajuste, consumo acima da custódia) é a gestora; se ela também fez o fato, a decisão vale
// e fica revisão independente pendente. Cada caso parte do cenário inicial e grava pelo cenMudar (atômico: erro não grava nada). NEGATIVO = recusado.
let nfail = 0;
function ok(t, c, got) { if (c) console.log('OK    ' + t); else { nfail++; console.log('FALHA ' + t + (got === undefined ? '' : ' · ' + JSON.stringify(got).slice(0, 500))); } }
const caso = (t, f) => { try { f(); } catch (e) { ok('ERRO no caso "' + t + '": ' + String(e.message || e), false); } };
const P = k => G2_PERFIS.find(p => p.k === k);
const ANA = P('Ana'), RUI = P('Rui'), PAULA = P('Paula');
const ini = () => { cenReset(); delete __ls['safrion.perfilDemo']; G2_PERFIL_MEM = ''; };
const G = () => cenGet();
const M = (f, cmd) => cenMudar(null, f, cmd);
const KF = 'Fungicida A|F26-02', KK = 'KCl 60%|K26-11', KM = 'MAP 11-52|M26-07', KG = 'Glifosato 480|G26-14', KN = 'NPK 20-05-20|N26-03';
const own = (rid, prod) => { const c = G(); const it = c.reqs[rid].itens.find(i => i.prod === prod); return cenResPropria(c, rid, it, c.lotes[prod + '|' + it.lote]); };
const foto = () => { const c = G(); return JSON.stringify([c.rev, c.movs.length, c.lotes, c.reqs, c.confs || [], c.ajustes || []]); };
function relato(q) { ini(); M(c => cenIniciarTurno(c, 'OS-0421')); M(c => cenFecharTurno(c, 10, 2, { 'Fungicida A': q }, '', [])); return G().confs[0]; }

// ===================== Etapa SUP-2a · entrega, devolução e conciliação =====================
console.log('— Entrega só do reservado (72.3 item 2) e O.S. impedida (N1, N2, N2b)');
caso('N1', () => {
  ini(); const a = foto(); const r = M(c => cenEntregar(c, 'REQ-036', 'Semente de soja 58 W', 3640, 'Carlos', RUI));
  ok('N1 NEGATIVO entregar à REQ-036 da OS-0420 (selo Impedida) é recusado pela função e nada muda (antes: entregava 3.640 kg)', !!r.erro && /impedida/i.test(r.erro) && foto() === a, r.erro || r.msg);
});
caso('N2', () => {
  ini(); const L0 = G().lotes[KF];
  ok('N2 semente: F26-02 com 80 L reservados (65 da REQ-039 + 15 da REQ-035); reserva própria da REQ-035 = 15 L', L0.reservado === 80 && own('REQ-035', 'Fungicida A') === 15 && own('REQ-039', 'Fungicida A') === 65,
    [L0.reservado, own('REQ-035', 'Fungicida A'), own('REQ-039', 'Fungicida A')]);
  M(c => { c.reqs['REQ-035'].itens[0].res0 = 160; c.lotes[KF].reservado = 65; return { msg: 'caso montado: REQ-035 sem reserva própria' }; });
  const a = foto(); const r = M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 15, 'Marcos', RUI));
  ok('N2 NEGATIVO REQ-035 sem reserva própria: 15 L recusados mesmo com 480 L livres no lote; nada muda', !!r.erro && /reserv/i.test(r.erro) && foto() === a, r.erro || r.msg);
  ini(); const r2 = M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 15, 'Marcos', RUI)); const c = G(); const it = c.reqs['REQ-035'].itens[0];
  ok('N2 com a semente nova (própria 15 L) os 15 L saem: entregue 175 L, custódia 80 L, F26-02 530 L físicos', !r2.erro && it.entregue === 175 && it.custodia === 80 && c.lotes[KF].fisico === 530, r2.erro || [it.entregue, it.custodia, c.lotes[KF].fisico]);
  const r3 = M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 1, 'Marcos', RUI));
  ok('N2 NEGATIVO 1 L além do saldo a entregar é recusado', !!r3.erro, r3.msg);
});
caso('N2c', () => {
  /* regra do merge SUP × BEN-1 (cenAindaRetira): a sobra apta volta à reserva só de ordem ativa com área a fazer; sem área a fazer, ao livre */
  ini(); const r0 = G().lotes[KF].reservado; M(c => cenDevolver(c, 'REQ-035', 'Fungicida A', 30, true, RUI)); const l1 = G().lotes[KF]; const m1 = G().movs.slice(-1)[0];
  ok('N2c OS-0421 em execução com 160 ha a fazer: 30 L aptos voltam à reserva da REQ-035 (reservado 80 → 110 L, movimento com res)', l1.reservado === r0 + 30 && m1.res === 30, [r0, l1.reservado, m1]);
  ini(); M(c => { c.ordens['OS-0421'].saldo = 0; return { msg: 'caso montado: área da OS-0421 feita' }; }); const r = M(c => cenDevolver(c, 'REQ-035', 'Fungicida A', 30, true, RUI)); const l2 = G().lotes[KF]; const m2 = G().movs.slice(-1)[0];
  ok('N2c OS-0421 em execução com a área feita: 30 L aptos vão ao livre (reservado continua 80 L; movimento sem res; "ao disponível")', l2.reservado === r0 && !m2.res && /ao disponível/.test(r.msg || ''), [l2.reservado, m2, r.msg]);
  const CXK = BENC.cx.item + '|CX26-01'; ini(); const d0 = cenDisp(G().lotes[CXK]); const rb = M(c => cenDevolver(c, 'REQ-030', BENC.cx.item, 60, true, RUI)); const lc = G().lotes[CXK];
  ok('N2c OB-0110 (beneficiamento em execução, sem área): 60 caixas aptas vão ao livre do CX26-01 (540 → 600 un), como o BEN-1 pede (I4)', !rb.erro && d0 === 540 && cenDisp(lc) === 600 && lc.reservado === 0, [rb, d0, lc]);
});
caso('N2b', () => {
  ini(); M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 15, 'Marcos', RUI));
  ok('N2b entregar 15 L à REQ-035 mantém a reserva própria da REQ-039 em 65 L (antes: 65 → 50)', own('REQ-039', 'Fungicida A') === 65 && G().lotes[KF].reservado === 65, [own('REQ-039', 'Fungicida A'), G().lotes[KF].reservado]);
  ini(); M(c => cenDevolver(c, 'REQ-035', 'Fungicida A', 30, true, RUI)); const own35 = own('REQ-035', 'Fungicida A');
  const r = M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 45, 'Marcos', RUI)); const l = G().lotes[KF];
  ok('N2b devolução apta de O.S. em execução volta à reserva dela: 15 + 30 = 45 L reentregues; F26-02 545 + 30 − 45 = 530 L; reserva da REQ-039 (65 L) preservada',
    own35 === 45 && !r.erro && l.fisico === 530 && l.reservado === 65 && own('REQ-039', 'Fungicida A') === 65, [own35, r.erro, l.fisico, l.reservado]);
});

console.log('\n— Comando com chave de quem inicia e versão do registro (N4)');
caso('N4', () => {
  ini(); const ver = cenVer(G(), 'REQ-039'); const cmd = { chave: 'EST-REQ-039-t1', nome: 'entregar', obj: 'REQ-039', ver, payload: ['Fungicida A', 65, 'Marcos'] };
  const r1 = M(c => cenEntregar(c, 'REQ-039', 'Fungicida A', 65, 'Marcos', RUI), cmd); const a = foto();
  const r2 = M(c => cenEntregar(c, 'REQ-039', 'Fungicida A', 65, 'Marcos', RUI), cmd);
  ok('N4 mesma chave duas vezes (toque duplo): a 2ª devolve o recibo, sem movimento nem rev novo', !r1.erro && r2.repetido === true && foto() === a && G().movs.filter(m => m.tipo === 'entrega').length === 1, [r1.erro, r2]);
  const r3 = M(c => cenEntregar(c, 'REQ-039', 'Fungicida A', 65, 'Paula', RUI), Object.assign({}, cmd, { payload: ['Fungicida A', 65, 'Paula'] }));
  ok('N4 NEGATIVO mesma chave com outro conteúdo: conflito, nada gravado', !!r3.erro && /conflito/i.test(r3.erro) && foto() === a, r3.erro || r3.msg);
  ini(); const v0 = cenVer(G(), 'REQ-035'); M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 5, 'Marcos', PAULA)); const b = foto();
  const r4 = M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 10, 'Marcos', RUI), { chave: 'EST-REQ-035-t2', nome: 'entregar', obj: 'REQ-035', ver: v0, payload: ['Fungicida A', 10, 'Marcos'] });
  ok('N4 NEGATIVO versão diferente (outra tela entregou 5 L depois de abrir o painel): "Mudou desde que você abriu", nada gravado', !!r4.erro && /^Mudou desde que você abriu/.test(r4.erro) && foto() === b, r4.erro || r4.msg);
  ini(); const r5 = M(c => cenEntregar(c, 'REQ-039', 'Fungicida A', 10, 'Marcos', RUI));
  ok('N4 sem comando, igual a antes (nenhum recibo gravado)', !r5.erro && !Object.keys(G().recibos || {}).length, r5.erro || G().recibos);
});

console.log('\n— Conciliação do consumo e devolução (N7, N8, N9)');
caso('N7', () => {
  for (const mot of [undefined, '', '   ']) { const k = relato(85); const a = foto(); const r = M(c => cenConciliar(c, k.id, false, mot, RUI));
    ok('N7 NEGATIVO recusar o relato ' + k.id + ' com motivo ' + JSON.stringify(mot) + ': recusado, caso segue Em conferência (antes: gravava texto fixo)', !!r.erro && /motivo/i.test(r.erro) && G().confs[0].estado === 'Em conferência' && foto() === a, r.erro || r.msg); }
  const k = relato(85); const r = M(c => cenConciliar(c, k.id, false, 'Operador confirmou 65 L', RUI));
  ok('N7 recusa com motivo digitado grava o motivo e quem recusou', !r.erro && G().confs[0].decisao === 'Operador confirmou 65 L' && G().confs[0].por === 'Rui (almoxarife)', r.erro || G().confs[0]);
});
caso('N8', () => {
  ini(); const a = foto(); const r = M(c => cenDevolver(c, 'REQ-031', 'MAP 11-52', 600, true, RUI));
  ok('N8 NEGATIVO devolução acima da custódia (600 de 500 kg) é recusada; nada muda', !!r.erro && foto() === a, r.erro || r.msg);
  ini(); const r2 = M(c => cenDevolver(c, 'REQ-031', 'MAP 11-52', 100, false, RUI, 'Sacaria rasgada')); const l = G().lotes[KM];
  ok('N8 devolução bloqueada vira parcela em quarentena da própria requisição, com o motivo', !r2.erro && l.quarentena === 100 && JSON.stringify(cenQuar(l).map(p => [p.doc, p.qtd, p.motivo])) === '[["REQ-031",100,"Sacaria rasgada"]]', r2.erro || l.quar);
});
caso('N9', () => {
  const k = relato(80); const r = M(c => cenConciliar(c, k.id, true, undefined, RUI));
  ok('N9 NEGATIVO 80 L relatados com 65 L em custódia: Rui não aceita os 15 L além da custódia', r.erro === 'Aceitar 15 L acima da custódia (CC-301): decisão de Ana (gestora). Nada foi alterado.', r.erro || r.msg);
  const p = cenConcPrevia(G(), k.id);
  ok('N9 prévia: os 15 L saem da reserva da própria REQ-035 (semente com a reserva da liberação)', p.txt === 'Baixa 80 L na OS-0421: 65 L da custódia de Marcos · 15 L saem do lote F26-02 (reserva da REQ-035).', p.txt);
  const r2 = M(c => cenConciliar(c, k.id, true, undefined, ANA)); const c = G(); const l = c.lotes[KF];
  ok('N9 Ana aceita: F26-02 545 → 530 L e reserva 80 → 65 L (a da REQ-039 intacta); caso Aceito por Ana (gestora)', !r2.erro && l.fisico === 530 && l.reservado === 65 && own('REQ-039', 'Fungicida A') === 65 && c.confs[0].estado === 'Aceito' && c.confs[0].por === 'Ana (gestora)', r2.erro || [l.fisico, l.reservado, c.confs[0]]);
});

console.log('\n— Quem agiu fica gravado (N11)');
caso('N11', () => {
  ini(); const last = () => G().movs[G().movs.length - 1];
  M(c => cenEntregar(c, 'REQ-039', 'Fungicida A', 10, 'Marcos', PAULA)); const e = last();
  M(c => cenDevolver(c, 'REQ-031', 'MAP 11-52', 100, true, PAULA)); const d = last();
  M(c => cenReceber(c, 'Ureia 45%', 'U26-01', 100, 'kg', 'Galpão 1', '12/2027', 'NF-9001', true, PAULA)); const rc = last();
  ok('N11 cada movimento grava o perfil de quem agiu: entrega, devolução e recebimento por Paula', e.quem === 'Paula (almoxarife) → Marcos' && d.quem === 'Paula (almoxarife)' && rc.quem === 'Paula (almoxarife)', [e.quem, d.quem, rc.quem]);
  const r = M(c => cenEntregar(c, 'REQ-039', 'Fungicida A', 10, 'Marcos'));
  ok('N11 NEGATIVO sem perfil nada é gravado (nenhum registro grava quem não agiu; CTL-3)', !!r.erro, r.msg);
});

// ===================== Etapa SUP-2b · quarentena por parcela, laudo, contagem e ajuste =====================
console.log('\n— Quarentena por parcela e laudo (N5, N5b)');
caso('N5', () => {
  ini(); const l0 = G().lotes[KK];
  ok('N5 semente: K26-11 com 1 parcela em quarentena (NF 4501, 10.000 kg, laudo de umidade pendente)', JSON.stringify((l0.quar || []).map(p => [p.doc, p.qtd, p.motivo])) === '[["NF 4501",10000,"Laudo de umidade pendente"]]' && l0.quarentena === 10000, l0.quar);
  const a = foto(); const r = M(c => cenLaudo(c, KK, 'NF 4501', '', 'Aprovado', ANA));
  ok('N5 NEGATIVO liberar sem nº de laudo: recusado; 10.000 kg seguem bloqueados', !!r.erro && /laudo/i.test(r.erro) && foto() === a, r.erro || r.msg);
  const rr = M(c => cenLaudo(c, KK, 'NF 4501', 'LAB-0917', 'Aprovado', RUI));
  ok('N5 NEGATIVO Rui (sem papel de gestor) não registra o laudo (cenExige)', rr.erro === 'Registrar o laudo da parcela NF 4501 do lote K26-11: decisão de Ana (gestora). Nada foi alterado.', rr.erro || rr.msg);
  const r2 = M(c => cenLaudo(c, KK, 'NF 4501', 'LAB-0917', 'Reprovado', ANA, 'Devolver ao fornecedor')); const l = G().lotes[KK];
  ok('N5 laudo reprovado mantém a parcela bloqueada com o laudo e o destino gravados', !r2.erro && l.quarentena === 10000 && l.quar[0].laudo && l.quar[0].laudo.res === 'Reprovado' && l.quar[0].laudo.destino === 'Devolver ao fornecedor' && l.quar[0].laudo.por === 'Ana (gestora)', r2.erro || l.quar);
  ini(); M(c => cenReceber(c, 'Óleo mineral', 'O26-07V', 40, 'L', 'Almox. defensivos', '07/2026', 'NF 9001', false, RUI, 'Lote vencido'));
  const r3 = M(c => cenLaudo(c, 'Óleo mineral|O26-07V', 'NF 9001', 'LAB-1', 'Aprovado', ANA));
  ok('N5 NEGATIVO lote vencido (07/2026) não é aprovado: 40 L seguem bloqueados', !!r3.erro && /vencido/i.test(r3.erro) && G().lotes['Óleo mineral|O26-07V'].quarentena === 40, r3.erro || r3.msg);
  ini(); const r4 = M(c => cenLaudo(c, KK, 'NF 4501', 'LAB-0917', 'Aprovado', ANA)); const m = G().movs[G().movs.length - 1];
  ok('N5 laudo aprovado libera a parcela: K26-11 sem quarentena, movimento "inspecao" com o laudo e quem decidiu', !r4.erro && G().lotes[KK].quarentena === 0 && !G().lotes[KK].quar.length && m.tipo === 'inspecao' && m.doc === 'LAB-0917' && m.quem === 'Ana (gestora)' && m.qtd === 10000, r4.erro || m);
  const r5 = M(c => cenLaudo(c, KK, 'NF 4501', 'LAB-0917', 'Aprovado', ANA));
  ok('N5 NEGATIVO repetir o laudo não libera de novo', !!r5.erro && G().lotes[KK].quarentena === 0, r5.erro || r5.msg);
});
caso('N5b', () => {
  ini(); M(c => cenDevolver(c, 'REQ-031', 'MAP 11-52', 100, false, RUI, 'Sacaria rasgada'));
  M(c => cenReceber(c, 'MAP 11-52', 'M26-07', 2000, 'kg', 'Galpão 2', '', 'NF 4600', false, RUI, 'Umidade a conferir'));
  const r = M(c => cenLaudo(c, KM, 'NF 4600', 'LAB-0920', 'Aprovado', ANA)); const l = G().lotes[KM];
  ok('N5b o laudo da NF 4600 libera só os 2.000 kg da nota e mantém os 100 kg da devolução da REQ-031 (antes: liberava 2.100 kg)', !r.erro && l.quarentena === 100 && JSON.stringify(l.quar.map(p => [p.doc, p.qtd])) === '[["REQ-031",100]]', r.erro || [l.quarentena, l.quar]);
  const ps = G().movs.filter(m => m.tipo === 'inspecao'); ok('N5b um só movimento de liberação (2.000 kg)', ps.length === 1 && ps[0].qtd === 2000, ps);
});

console.log('\n— Recebimento em lote existente: a validade é a do lote de fabricação (N13; SUP §9.3, verif_ce_est:35)');
caso('N13', () => {
  const KS = 'Semente de soja 58 W|S58-0801';
  ini(); const a = foto(); const r = M(c => cenReceber(c, 'Semente de soja 58 W', 'S58-0801', 1000, 'kg', 'Câmara fria', '03/2027', 'NF 7003', true, RUI));
  ok('N13 NEGATIVO S58-0801 (validade 06/2027) recebido com validade 03/2027: recusado, nada gravado (antes: entrava 1.000 kg sob a validade 06/2027)',
    !!r.erro && /06\/2027/.test(r.erro) && /03\/2027/.test(r.erro) && foto() === a, r.erro || r.msg);
  ini(); const r2 = M(c => cenReceber(c, 'Semente de soja 58 W', 'S58-0801', 1000, 'kg', 'Câmara fria', '06/2027', 'NF 7004', true, RUI));
  ok('N13 mesma validade (06/2027): entra no lote', !r2.erro && G().lotes[KS].fisico === 13000 && G().lotes[KS].validade === '06/2027', r2.erro || G().lotes[KS]);
  ini(); const r3 = M(c => cenReceber(c, 'MAP 11-52', 'M26-07', 500, 'kg', 'Galpão 2', '', 'NF 4601', true, RUI));
  ok('N13 lote sem validade ("—", fertilizante) e nota sem validade: entra', !r3.erro && G().lotes[KM].fisico === 90500, r3.erro || r3.msg);
});
console.log('\n— Contagem gravada sempre e ajuste decidido pela gestora, com o padrão (2) (N6, N6b, N10)');
caso('N6', () => {
  ini(); M(c => cenContar(c, KG, 1180, 'Rui (almoxarife)')); const id = G().ajustes[0].id; const a = G().movs.length;
  ok('N6 o ajuste guarda quem contou', G().ajustes[0].contador === 'Rui (almoxarife)', G().ajustes[0]);
  const r = M(c => cenAprovarAjuste(c, id, true, RUI));
  ok('N6 NEGATIVO Rui (contou, sem papel de gestor) não aprova: decisão de Ana (gestora); c.movs igual', r.erro === 'Aprovar o ajuste ' + id + ': decisão de Ana (gestora). Nada foi alterado.' && G().movs.length === a, r.erro || r.msg);
  const r2 = M(c => cenAprovarAjuste(c, id, true, ANA)); const m = G().movs.find(x => x.tipo === 'ajuste');
  ok('N6 Ana aprova: −20 L no G26-14, gravado "Ana (gestora)", sem revisão pendente (quem contou foi Rui)', !r2.erro && m && m.qtd === -20 && m.quem === 'Ana (gestora)' && !m.rev && G().lotes[KG].fisico === 1180, r2.erro || m);
  ini(); M(c => cenContar(c, KG, 1180, 'Ana (gestora)')); const r3 = M(c => cenAprovarAjuste(c, G().ajustes[0].id, true, ANA)); const aj = G().ajustes[0];
  ok('N6 padrão (2), PEND-CTL-02: Ana contou e aprova: a decisão vale (1.180 L) e fica "Decisão do gestor registrada · revisão independente pendente", sem fingir outra revisão',
    !r3.erro && G().lotes[KG].fisico === 1180 && aj.rev === 'Decisão do gestor registrada · revisão independente pendente (Ana contou e decidiu)' && / Decisão do gestor registrada · revisão independente pendente \(Ana contou e decidiu\)\.$/.test(r3.msg), r3.erro || [aj.rev, r3.msg]);
});
caso('N6b', () => {
  ini(); M(c => cenContar(c, KG, 1180, 'Paula (almoxarife)')); const r = M(c => cenAprovarAjuste(c, G().ajustes[0].id, false, PAULA));
  ok('N6b quem contou ainda pede recontagem (recusar é livre): ajuste Recusado e físico 1.200 L', !r.erro && G().ajustes[0].estado === 'Recusado' && G().lotes[KG].fisico === 1200, r.erro || r.msg);
});
caso('N10', () => {
  ini(); const r = M(c => cenContar(c, KN, 7900, 'Paula (almoxarife)')); const aj = (G().ajustes || [])[0] || {};
  ok('N10 contagem de 7.900 kg no N26-03 (8.000 kg reservados para a REQ-040) é gravada: ajuste aguardando a gestora com "afeta" REQ-040 (antes: recusada)', !r.erro && aj.estado === 'Aguardando gestor' && aj.contado === 7900 && JSON.stringify(aj.afeta) === '["REQ-040"]', r.erro || aj);
  ok('N10 nenhuma mensagem mostra a quantidade do sistema (8.000)', !/8\.000/.test(r.msg || r.erro || ''), r.msg || r.erro);
});
caso('N11b', () => {
  ini(); M(c => cenLaudo(c, KK, 'NF 4501', 'LAB-1', 'Aprovado', ANA)); const lb = G().movs[G().movs.length - 1];
  M(c => cenReceber(c, 'Ureia 45%', 'U26-01', 100, 'kg', 'Galpão 1', '12/2027', 'NF-9002', false, PAULA, 'Sem laudo')); const rq = G().lotes['Ureia 45%|U26-01'].quar[0];
  ok('N11b laudo grava quem decidiu (Ana) e a parcela bloqueada grava quem a registrou (Paula)', lb.quem === 'Ana (gestora)' && rq.por === 'Paula (almoxarife)', [lb.quem, rq]);
});

// ===================== Tela do Estoque (est.js): fila, rótulo, Entregar REQ inteira, contagens e abertura pelo perfil =====================
console.log('\n— Entregar REQ inteira: tudo ou nada, chave de quem inicia e rótulo que confirma (N3, N4r, N12)');
caso('N3', () => {
  ini(); M(c => { c.lotes['Superfosfato simples|LG26-09'].fisico = 10000; return { msg: 'caso montado: LG26-09 com 10.000 kg' }; });
  const a = foto(); const r = M(c => estEntregarReq(c, 'REQ-021', 'Renato', RUI));
  ok('N3 NEGATIVO REQ-021 com o 2º item sem físico (10.000 de 20.000 kg): nada é gravado (rev, lotes, movimentos e requisição iguais)', !!r.erro && foto() === a, r.erro || r.msg);
  ini(); const r2 = M(c => estEntregarReq(c, 'REQ-021', 'Renato', RUI)); const its = G().reqs['REQ-021'].itens;
  ok('N3 REQ-021 inteira a Renato: 92.500 un + 20.000 kg em custódia, 2 entregas gravadas por Rui', !r2.erro && its.map(i => i.custodia).join('|') === '92500|20000'
    && G().movs.filter(m => m.tipo === 'entrega').map(m => m.quem).join('|') === 'Rui (almoxarife) → Renato|Rui (almoxarife) → Renato', r2.erro || its.map(i => i.custodia));
  ok('N3 comprovante nomeia o que saiu, lote e para quem', /^REQ-021: 92\.500 un de Muda de mamão Formosa \(1\.850 bandejas, lote LG26-05\) e 20\.000 kg de Superfosfato simples \(400 sacos, lote LG26-09\) entregues a Renato · aguarda confirmação no app\.$/.test(r2.msg || ''), r2.msg);
});
caso('N4r', () => {
  ini(); const ver = cenVer(G(), 'REQ-039'); const cmd = { chave: 'EST-req-t1', nome: 'entregar-req', obj: 'REQ-039', ver, payload: [['Fungicida A', 65, 'Marcos']] };
  const r1 = M(c => estEntregarReq(c, 'REQ-039', 'Marcos', RUI), cmd); const a = foto(); const r2 = M(c => estEntregarReq(c, 'REQ-039', 'Marcos', RUI), cmd);
  ok('N4r "Entregar REQ-039 inteira" com a mesma chave duas vezes: uma entrega só, a 2ª devolve o recibo', !r1.erro && r2.repetido === true && foto() === a && G().movs.filter(m => m.tipo === 'entrega').length === 1, [r1.erro, r2]);
  const r3 = M(c => estEntregarReq(c, 'REQ-040', 'Paula', RUI), cmd);
  ok('N4r NEGATIVO a mesma chave não entrega outra requisição: devolve o recibo da REQ-039 e a REQ-040 fica intacta', r3.repetido === true && r3.recibo && r3.recibo.obj === 'REQ-039' && G().reqs['REQ-040'].itens[0].entregue === 0 && foto() === a, r3.erro || r3);
});
caso('N12', () => {
  ini(); const x = estRotuloReq(G(), 'REQ-021', 'Renato');
  ok('N12 rótulo da REQ-021 confirma o quê, quanto, lote e para quem', x.rotulo === 'Entregar REQ-021 · 92.500 un Muda de mamão Formosa (lote LG26-05) + 20.000 kg Superfosfato simples (lote LG26-09) a Renato', x.rotulo);
  ok('N12 "Separe:" com 1.850 bandejas de 50 mudas e 400 sacos de 50 kg, lote, validade e local', x.separe.some(t => /^Muda de mamão Formosa: LG26-05 · val\. 12\/2027 · Almox\. Lagoa Grande · 1\.850 bandejas de 50 mudas$/.test(t))
    && x.separe.some(t => /400 sacos de 50 kg/.test(t)), x.separe);
  const y = estRotuloReq(G(), 'REQ-039', 'Marcos');
  ok('N12 REQ-039: "Separe:" F26-02 · val. 03/2028 · Almox. defensivos · 13 galões de 5 L', y.separe[0] === 'Fungicida A: F26-02 · val. 03/2028 · Almox. defensivos · 13 galões de 5 L', y.separe);
});

console.log('\n— Contagem da tela: contagem antiga (INV-2609) e ajuste que atinge a reserva (N6t, N10b)');
caso('N6t', () => {
  ini(); const a = G().movs.length; const r = M(c => estAprovar(c, 'INV-2609', RUI));
  ok('N6t NEGATIVO Rui (contou a INV-2609, sem papel de gestor) não aprova: decisão de Ana (gestora); c.movs igual', r.erro === 'Aprovar o ajuste INV-2609: decisão de Ana (gestora). Nada foi alterado.' && G().movs.length === a, r.erro || r.msg);
  const r2 = M(c => estAprovar(c, 'INV-2609', ANA)); const m = G().movs.find(x => x.tipo === 'ajuste');
  ok('N6t Ana aprova o INV-2609: −600 kg no M26-07, gravado "Ana (gestora)", sem revisão pendente (quem contou foi Rui)', !r2.erro && m && m.qtd === -600 && m.quem === 'Ana (gestora)' && !m.rev && G().lotes[KM].fisico === 89400, r2.erro || m);
});
caso('N10b', () => {
  ini(); M(c => estContar(c, 'INV-2612', KN, 7900, 'Paula (almoxarife)', '', PAULA)); M(c => estCausa(c, 'INV-2612', 'Big bag rasgado'));
  const r2 = M(c => estAprovar(c, 'INV-2612', ANA)); const x = estFila(G(), 'Santa Rita').find(y => y.rid === 'REQ-040');
  ok('N10b ajuste aprovado: a REQ-040 fica "Lote insuficiente" e oferece só Entregar parte (7.900 kg)', !r2.erro && x && x.sit === 'Lote insuficiente' && !x.inteira && x.itens[0].parte === 7900, r2.erro || x);
  const r3 = M(c => estEntregarReq(c, 'REQ-040', 'Paula', RUI));
  ok('N10b NEGATIVO "Entregar REQ-040 inteira" com lote insuficiente é recusado pela função', !!r3.erro && /insuficiente/i.test(r3.erro), r3.erro || r3.msg);
});

console.log('\n— Fila, contadores por fazenda, abertura pelo perfil e visão Produção (F1-F4)');
caso('F1', () => {
  ini(); const k = f => estContadores(G(), f);
  /* "2 notas" desde o merge do BEN rodada 1 (BEN-D23): a NF 7731 das caixas (PC-096, 1.200 un, Packing da Santa Rita) espera a conferência */
  ok('F1 Santa Rita: "3 a entregar · 1 sobra", "2 notas · 1 laudo" (NF 4533 prevista e NF 7731 das caixas), "1 a contar · 1 ajuste"', k('Santa Rita').req === '3 a entregar · 1 sobra' && k('Santa Rita').rec === '2 notas · 1 laudo' && k('Santa Rita').cnt === '1 a contar · 1 ajuste', k('Santa Rita'));
  ok('F1 Lagoa Grande: "1 a entregar"; Todas: "4 a entregar · 1 sobra"; Boa Vista sem pendência', k('Lagoa Grande').req === '1 a entregar' && k('Todas').req === '4 a entregar · 1 sobra' && !k('Boa Vista').req && !k('Boa Vista').rec && !k('Boa Vista').cnt, [k('Lagoa Grande'), k('Todas'), k('Boa Vista')]);
});
caso('F2', () => {
  ini(); const ids = f => estFila(G(), f).filter(x => x.acao).map(x => x.rid).join(' ');
  ok('F2 Santa Rita com ação, nesta ordem: REQ-035 REQ-031 REQ-039 REQ-040', ids('Santa Rita') === 'REQ-035 REQ-031 REQ-039 REQ-040', ids('Santa Rita'));
  ok('F2 Todas com ação: REQ-035 REQ-031 REQ-021 REQ-039 REQ-040', ids('Todas') === 'REQ-035 REQ-031 REQ-021 REQ-039 REQ-040', ids('Todas'));
  const s = estFila(G(), 'Santa Rita'); const S = id => (s.find(x => x.rid === id) || {}).sit;
  ok('F2 Situação: REQ-036 "O.S. impedida", REQ-038 "Aguarda liberação", REQ-040 "Reserva parcial · faltam 3.400 kg", REQ-031 "Sobra a receber", REQ-039 "A entregar"',
    S('REQ-036') === 'O.S. impedida' && S('REQ-038') === 'Aguarda liberação' && S('REQ-040') === 'Reserva parcial · faltam 3.400 kg' && S('REQ-031') === 'Sobra a receber' && S('REQ-039') === 'A entregar', s.map(x => x.rid + ':' + x.sit));
  const k = relato(85); const t = estFila(G(), 'Santa Rita'); const r35 = t.find(x => x.rid === 'REQ-035');
  ok('F2 consumo acima da custódia na REQ-035: a requisição segue "A entregar" (15 L, prioridade do §3) e o relato fica "Aguardando gestora" na linha filha e no contador',
    r35 && r35.sit === 'A entregar' && r35.confs.length === 1 && r35.confs[0].id === k.id && estSitCf(G(), r35.confs[0]) === 'Aguardando gestora'
    && estContadores(G(), 'Santa Rita').req === '3 a entregar · 1 sobra · 1 aguardando gestora' && estAbertura(G(), 'Ana', 'Santa Rita') === 1, [r35 && r35.sit, estContadores(G(), 'Santa Rita').req]);
});
caso('F3', () => {
  ini(); const r0 = G().rev; const ab = k => estAbertura(G(), k, 'Santa Rita');
  ok('F3 abertura pelo perfil: Rui → Atenda requisições (1); Paula (INV-2611 atribuída) → Faça contagens (3); Ana → Receba e inspecione (2: laudo do K26-11 aguarda a gestora)', ab('Rui') === 1 && ab('Paula') === 3 && ab('Ana') === 2, [ab('Rui'), ab('Paula'), ab('Ana')]);
  M(c => cenLaudo(c, KK, 'NF 4501', 'LAB-1', 'Aprovado', ANA)); const r1 = G().rev;
  ok('F3 sem laudo pendente, Ana abre em Faça contagens (INV-2609 aguarda a gestora); abrir não muda o cenário', ab('Ana') === 3 && G().rev === r1 && r1 === r0 + 1, [ab('Ana'), r0, r1]);
});

caso('F6', () => {
  /* merge SUP × BEN-1: a ordem de beneficiamento guarda a fazenda em o.ben.faz (estFazOrd); antes a REQ-030 só aparecia em "Todas" */
  ini(); const ids = f => estFila(G(), f).map(y => y.rid);
  ok('F6 REQ-030 da OB-0110 (Packing, Santa Rita) na fila da Santa Rita e de Todas, fora da Lagoa Grande', ids('Santa Rita').includes('REQ-030') && ids('Todas').includes('REQ-030') && !ids('Lagoa Grande').includes('REQ-030'),
    [ids('Santa Rita'), ids('Lagoa Grande')]);
});
caso('F7', () => {
  /* merge SUP × BEN rodada 1 (BEN-REV-08): fruta da Lagoa Grande processada no Packing da Santa Rita (o.ben.faz = Lagoa Grande, o.ben.local = l8).
     A requisição de caixas é atendida onde a ordem roda e o lote está (Packing, Santa Rita); pela fazenda da fruta ela sumia da fila da Santa Rita
     e o almoxarife que entrega no balcão do Packing não a via (roteiro do BEN, R6: "NÃO ACHEI: REQ-041") */
  ini(); M(c => { const o = c.ordens['OB-0110']; o.ben.faz = 'Lagoa Grande'; return { msg: 'caso montado: OB-0110 com fruta da Lagoa Grande no Packing (l8)' }; });
  const ids = f => estFila(G(), f).map(y => y.rid);
  ok('F7 REQ-030 de ordem com fruta da Lagoa Grande no Packing (l8, Santa Rita): na fila da Santa Rita, fora da Lagoa Grande; estFazOrd = Santa Rita',
    ids('Santa Rita').includes('REQ-030') && !ids('Lagoa Grande').includes('REQ-030') && estFazOrd(G().ordens['OB-0110']) === 'Santa Rita', [ids('Santa Rita'), ids('Lagoa Grande'), estFazOrd(G().ordens['OB-0110'])]);
});
caso('F4', () => {
  ini(); const c0 = JSON.stringify(G().producao); const r0 = G().rev; const T = estProducao(G(), 'Todas'), S = estProducao(G(), 'Santa Rita'), L = estProducao(G(), 'Lagoa Grande');
  /* expectativa mudada no merge com o BEN-1 (dados_ben.semear): a Santa Rita ganha os 7 lotes de fruta de campo do packing (4 na OB-0110, 3 da
     OB-0112: 21.270 kg) e o L26-118 de fruta embalada (300 kg, bloqueado: o físico conta; qualidade e disponível ficam na Produção) */
  ok('F4 visão Produção lê o produto da Colheita (c.producao): Santa Rita 21.270 kg de fruta de campo em 7 lotes, 300 kg de fruta embalada em 1 e 38.420 sc de soja em 1; Lagoa Grande 66.250 kg de mamão em 3 lotes (o esgotado não conta)',
    JSON.stringify(S.map(x => [x.prod, x.txt, x.lotes])) === '[["Mamão Formosa · fruta de campo","21.270 kg",7],["Mamão Formosa · fruta embalada","300 kg",1],["Soja em grão","38.420 sc",1]]'
    && JSON.stringify(L.map(x => [x.prod, x.txt, x.lotes])) === '[["Mamão Formosa · fruta de campo","66.250 kg",3]]' && T.length === 3, [S, L, T.length]);
  ok('F4 só leitura: c.producao e c.rev iguais depois de ler', JSON.stringify(G().producao) === c0 && G().rev === r0);
});
// CTL-2 (apontamento único web × app) na fila nova: o turno do app que chega com a mesma data de um dia já somado pela web fica retido
// (CEN_AP_DUP) e o consumo dele "Aguarda duplicidade": nada vira linha, contador ou item no Estoque até Paula decidir. Dano evitado:
// o almoxarife conciliar (ou a gestora aceitar) um consumo que pode ser o mesmo turno contado duas vezes.
const dupRetido = () => { ini(); M(c => cenSinal(c, false)); M(c => cenIniciarTurno(c, 'OS-0421')); M(c => cenFecharTurno(c, 10, 2, { 'Fungicida A': 85 }, '', []));
  const a = G().ordens['OS-0421'].ap.find(x => x.origem === 'app' && x.sinc === false);
  M(c => cenApontar(c, { os: 'OS-0421', d: a.d, ha: 5, origem: 'web', chave: 'W-SUP-F5' })); M(c => cenSinal(c, true)); return a.dia; };
const fila35 = () => { const c = G(); const r = estFila(c, 'Santa Rita').find(x => x.rid === 'REQ-035'); return [r.sit, r.confs.length, estContadores(c, 'Santa Rita').req]; };
caso('F5', () => {
  ini(); const k0 = estContadores(G(), 'Santa Rita').req; const dia = dupRetido(); const c = G(); const ap = c.ordens['OS-0421'].ap.find(a => a.dia === dia);
  const cf = (c.confs || []).filter(k => k.os === 'OS-0421' && k.dia === dia); const mv = c.movs.find(x => x.id === ap.mov);
  ok('F5 duplicidade retida (CTL-2): consumo "Aguarda duplicidade", REQ-035 sem linha de conferência, contador igual e movimento sem item (econsDet vazio)',
    ap.st === CEN_AP_DUP && cf.length === 1 && cf[0].estado === CEN_CC_AGUARDA && JSON.stringify(fila35()) === JSON.stringify(['A entregar', 0, k0]) && econsDet(c, mv).length === 0, [ap.st, cf.map(k => k.estado), fila35(), k0]);
  M(c => cenApDecidir(c, 'OS-0421', dia, 'anterior', PAULA));
  ok('F5 Paula decide "mesmo turno": o relato fica recusado e continua fora da fila e do contador', G().confs.find(k => k.id === cf[0].id).estado === 'Recusado' && JSON.stringify(fila35()) === JSON.stringify(['A entregar', 0, k0]), fila35());
  dupRetido(); M(c => cenApDecidir(c, 'OS-0421', dia, 'somar', PAULA, { 'Fungicida A': 85 })); const c2 = G();
  const ab = (c2.confs || []).filter(k => k.os === 'OS-0421' && k.estado === 'Em conferência');
  ok('F5 "outro turno": o mesmo relato volta uma vez só (1 caso, 85 L), linha "Aguardando gestora" e contador da gestora',
    ab.length === 1 && ab[0].relatado === 85 && JSON.stringify(fila35()) === JSON.stringify(['A entregar', 1, k0 + ' · 1 aguardando gestora']), [ab.map(k => [k.id, k.relatado]), fila35()]);
});
console.log('\n' + (nfail ? nfail + ' FALHA(S)' : 'sem falhas'));
