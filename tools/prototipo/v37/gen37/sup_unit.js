// SUP · Suprimentos simplificado (docs/suprimentos-simplificado, §6 e §9.2) · node, sem navegador. Executor: sup_unit_test.py.
// Regras do Estoque sobre o cenário compartilhado (cenario.js + est.js), com o perfil de quem age (G2_PERFIS, CTL-3) e o padrão (2) de 05/10/2026:
// quem decide o que exige papel (laudo, ajuste, consumo acima da custódia) é a gestora; se ela também fez o fato, a decisão vale e fica
// "revisão posterior pendente". Cada caso parte do cenário inicial e grava pelo cenMudar (atômico: erro não grava nada). NEGATIVO = recusado.
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
caso('N2b', () => {
  ini(); M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 15, 'Marcos', RUI));
  ok('N2b entregar 15 L à REQ-035 mantém a reserva própria da REQ-039 em 65 L (antes: 65 → 50)', own('REQ-039', 'Fungicida A') === 65 && G().lotes[KF].reservado === 65, [own('REQ-039', 'Fungicida A'), G().lotes[KF].reservado]);
  ini(); M(c => cenDevolver(c, 'REQ-035', 'Fungicida A', 30, true, RUI)); const own35 = own('REQ-035', 'Fungicida A');
  const r = M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 45, 'Marcos', RUI)); const l = G().lotes[KF];
  ok('N2b devolução apta de O.S. em execução volta à reserva dela: 15 + 30 = 45 L reentregues; F26-02 545 + 30 − 45 = 530 L; reserva da REQ-039 (65 L) preservada',
    own35 === 45 && !r.erro && l.fisico === 530 && l.reservado === 65 && own('REQ-039', 'Fungicida A') === 65, [own35, r.erro, l.fisico, l.reservado]);
});

console.log('\n— Entregar REQ inteira: tudo ou nada, chave de quem inicia e versão (N3, N4, N12)');
caso('N3', () => {
  ini(); M(c => { c.lotes['Superfosfato simples|LG26-09'].fisico = 10000; return { msg: 'caso montado: LG26-09 com 10.000 kg' }; });
  const a = foto(); const r = M(c => estEntregarReq(c, 'REQ-021', 'Renato', RUI));
  ok('N3 NEGATIVO REQ-021 com o 2º item sem físico (10.000 de 20.000 kg): nada é gravado (rev, lotes, movimentos e requisição iguais)', !!r.erro && foto() === a, r.erro || r.msg);
  ini(); const r2 = M(c => estEntregarReq(c, 'REQ-021', 'Renato', RUI)); const its = G().reqs['REQ-021'].itens;
  ok('N3 REQ-021 inteira a Renato: 92.500 un + 20.000 kg em custódia, 2 entregas gravadas por Rui', !r2.erro && its.map(i => i.custodia).join('|') === '92500|20000'
    && G().movs.filter(m => m.tipo === 'entrega').map(m => m.quem).join('|') === 'Rui (almoxarife) → Renato|Rui (almoxarife) → Renato', r2.erro || its.map(i => i.custodia));
  ok('N3 comprovante nomeia o que saiu, lote e para quem', /^REQ-021: 92\.500 un de Muda de mamão Formosa \(1\.850 bandejas, lote LG26-05\) e 20\.000 kg de Superfosfato simples \(400 sacos, lote LG26-09\) entregues a Renato · aguarda confirmação no app\.$/.test(r2.msg || ''), r2.msg);
});
caso('N4', () => {
  ini(); const ver = cenVer(G(), 'REQ-039'); const cmd = { chave: 'EST-REQ-039-t1', nome: 'entregar-req', obj: 'REQ-039', ver, payload: [['Fungicida A', 65, 'Marcos']] };
  const r1 = M(c => estEntregarReq(c, 'REQ-039', 'Marcos', RUI), cmd); const a = foto();
  const r2 = M(c => estEntregarReq(c, 'REQ-039', 'Marcos', RUI), cmd);
  ok('N4 mesma chave duas vezes (toque duplo): a 2ª devolve o recibo, sem movimento nem rev novo', !r1.erro && r2.repetido === true && foto() === a && G().movs.filter(m => m.tipo === 'entrega').length === 1, [r1.erro, r2]);
  const r3 = M(c => estEntregarReq(c, 'REQ-039', 'Paula', RUI), Object.assign({}, cmd, { payload: [['Fungicida A', 65, 'Paula']] }));
  ok('N4 NEGATIVO mesma chave com outro conteúdo: conflito, nada gravado', !!r3.erro && /conflito/i.test(r3.erro) && foto() === a, r3.erro || r3.msg);
  ini(); const v0 = cenVer(G(), 'REQ-035'); M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 5, 'Marcos', PAULA)); const b = foto();
  const r4 = M(c => estEntregarReq(c, 'REQ-035', 'Marcos', RUI), { chave: 'EST-REQ-035-t2', nome: 'entregar-req', obj: 'REQ-035', ver: v0, payload: [['Fungicida A', 15, 'Marcos']] });
  ok('N4 NEGATIVO versão diferente (outra tela entregou 5 L depois de abrir o painel): "Mudou desde que você abriu", nada gravado', !!r4.erro && /^Mudou desde que você abriu/.test(r4.erro) && foto() === b, r4.erro || r4.msg);
});
caso('N12', () => {
  ini(); const x = estRotuloReq(G(), 'REQ-021', 'Renato');
  ok('N12 rótulo da REQ-021 confirma o quê, quanto, lote e para quem', x.rotulo === 'Entregar REQ-021 · 92.500 un Muda de mamão Formosa (lote LG26-05) + 20.000 kg Superfosfato simples (lote LG26-09) a Renato', x.rotulo);
  ok('N12 "Separe:" com 1.850 bandejas de 50 mudas e 400 sacos de 50 kg, lote, validade e local', x.separe.some(t => /^Muda de mamão Formosa: LG26-05 · val\. 12\/2027 · Almox\. Lagoa Grande · 1\.850 bandejas de 50 mudas$/.test(t))
    && x.separe.some(t => /400 sacos de 50 kg/.test(t)), x.separe);
  const y = estRotuloReq(G(), 'REQ-039', 'Marcos');
  ok('N12 REQ-039: "Separe:" F26-02 · val. 03/2028 · Almox. defensivos · 13 galões de 5 L', y.separe[0] === 'Fungicida A: F26-02 · val. 03/2028 · Almox. defensivos · 13 galões de 5 L', y.separe);
});

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
});
caso('N5b', () => {
  ini(); M(c => cenDevolver(c, 'REQ-031', 'MAP 11-52', 100, false, RUI, 'Sacaria rasgada'));
  M(c => cenReceber(c, 'MAP 11-52', 'M26-07', 2000, 'kg', 'Galpão 2', '', 'NF 4600', false, RUI, 'Umidade a conferir'));
  const r = M(c => cenLaudo(c, KM, 'NF 4600', 'LAB-0920', 'Aprovado', ANA)); const l = G().lotes[KM];
  ok('N5b o laudo da NF 4600 libera só os 2.000 kg da nota e mantém os 100 kg da devolução da REQ-031 (antes: liberava 2.100 kg)', !r.erro && l.quarentena === 100 && JSON.stringify(l.quar.map(p => [p.doc, p.qtd])) === '[["REQ-031",100]]', r.erro || [l.quarentena, l.quar]);
  const ps = G().movs.filter(m => m.tipo === 'inspecao'); ok('N5b um só movimento de liberação (2.000 kg)', ps.length === 1 && ps[0].qtd === 2000, ps);
});

console.log('\n— Contagem cega gravada sempre e ajuste decidido pela gestora com o padrão (2) (N6, N6b, N10)');
caso('N6', () => {
  ini(); const a = G().movs.length; const r = M(c => estAprovar(c, 'INV-2609', RUI));
  ok('N6 NEGATIVO Rui (contou a INV-2609) não aprova: decisão de Ana (gestora); c.movs igual', r.erro === 'Aprovar o ajuste INV-2609: decisão de Ana (gestora). Nada foi alterado.' && G().movs.length === a, r.erro || r.msg);
  const r2 = M(c => estAprovar(c, 'INV-2609', ANA)); const m = G().movs.find(x => x.tipo === 'ajuste');
  ok('N6 Ana aprova o INV-2609: −600 kg no M26-07, gravado "Ana (gestora)", sem revisão posterior (quem contou foi Rui)', !r2.erro && m && m.qtd === -600 && m.quem === 'Ana (gestora)' && !m.rev && G().lotes[KM].fisico === 89400, r2.erro || m);
  ini(); M(c => estContar(c, 'INV-2611', KG, 1180, 'Ana (gestora)', 'bombona avariada', ANA)); const r3 = M(c => estAprovar(c, 'INV-2611', ANA)); const aj = G().ajustes[0];
  ok('N6 padrão (2): Ana contou e aprova: a decisão vale (1.180 L) e fica "revisão posterior pendente (Ana contou e decidiu)"', !r3.erro && G().lotes[KG].fisico === 1180 && aj.rev === 'revisão posterior pendente (Ana contou e decidiu)', r3.erro || aj.rev);
});
caso('N6b', () => {
  ini(); M(c => estContar(c, 'INV-2611', KG, 1180, 'Paula (almoxarife)', 'bombona', PAULA)); const r = M(c => estRecontar(c, 'INV-2611'));
  ok('N6b quem contou ainda pede recontagem (recusar é livre): ajuste Recusado e físico 1.200 L', !r.erro && G().ajustes[0].estado === 'Recusado' && G().lotes[KG].fisico === 1200, r.erro || r.msg);
});
caso('N10', () => {
  ini(); const r = M(c => estContar(c, 'INV-2612', KN, 7900, 'Paula (almoxarife)', '', PAULA)); const aj = (G().ajustes || [])[0] || {};
  ok('N10 contagem de 7.900 kg no N26-03 (8.000 kg reservados para a REQ-040) é gravada: ajuste aguardando a gestora com "afeta" REQ-040 (antes: recusada)', !r.erro && aj.estado === 'Aguardando gestor' && aj.contado === 7900 && JSON.stringify(aj.afeta) === '["REQ-040"]', r.erro || aj);
  ok('N10 nenhuma mensagem mostra a quantidade do sistema (8.000)', !/8\.000/.test(r.msg || r.erro || ''), r.msg || r.erro);
  M(c => estCausa(c, 'INV-2612', 'Big bag rasgado')); const r2 = M(c => estAprovar(c, 'INV-2612', ANA)); const x = estFila(G(), 'Santa Rita').find(y => y.rid === 'REQ-040');
  ok('N10b ajuste aprovado: a REQ-040 fica "Lote insuficiente" e oferece só Entregar parte (7.900 kg)', !r2.erro && x && x.sit === 'Lote insuficiente' && !x.inteira && x.itens[0].parte === 7900, r2.erro || x);
  const r3 = M(c => estEntregarReq(c, 'REQ-040', 'Paula', RUI));
  ok('N10b NEGATIVO "Entregar REQ-040 inteira" com lote insuficiente é recusado pela função', !!r3.erro && /insuficiente/i.test(r3.erro), r3.erro || r3.msg);
});

console.log('\n— Conciliação do consumo (N7, N8, N9)');
caso('N7', () => {
  for (const mot of [undefined, '', '   ']) { const k = relato(85); const a = foto(); const r = M(c => cenConciliar(c, k.id, false, mot, RUI));
    ok('N7 NEGATIVO recusar o relato ' + k.id + ' com motivo ' + JSON.stringify(mot) + ': recusado, caso segue Em conferência (antes: gravava texto fixo)', !!r.erro && /motivo/i.test(r.erro) && G().confs[0].estado === 'Em conferência' && foto() === a, r.erro || r.msg); }
  const k = relato(85); const r = M(c => cenConciliar(c, k.id, false, 'Operador confirmou 65 L', RUI));
  ok('N7 recusa com motivo digitado grava o motivo e quem recusou', !r.erro && G().confs[0].decisao === 'Operador confirmou 65 L' && G().confs[0].por === 'Rui (almoxarife)', r.erro || G().confs[0]);
});
caso('N8', () => {
  ini(); const a = foto(); const r = M(c => cenDevolver(c, 'REQ-031', 'MAP 11-52', 600, true, RUI));
  ok('N8 NEGATIVO devolução acima da custódia (600 de 500 kg) é recusada; nada muda', !!r.erro && foto() === a, r.erro || r.msg);
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
  M(c => cenLaudo(c, KK, 'NF 4501', 'LAB-1', 'Aprovado', ANA)); const lb = last();
  ok('N11 cada movimento grava o perfil de quem agiu: entrega, devolução e recebimento por Paula; laudo por Ana', e.quem === 'Paula (almoxarife) → Marcos' && d.quem === 'Paula (almoxarife)' && rc.quem === 'Paula (almoxarife)' && lb.quem === 'Ana (gestora)', [e.quem, d.quem, rc.quem, lb.quem]);
  const r = M(c => cenEntregar(c, 'REQ-039', 'Fungicida A', 10, 'Marcos'));
  ok('N11 NEGATIVO sem perfil nada é gravado (nenhum registro grava quem não agiu; CTL-3)', !!r.erro, r.msg);
});

console.log('\n— Fila, contadores por fazenda, abertura pelo perfil e visão Produção (F1-F4)');
caso('F1', () => {
  ini(); const k = f => estContadores(G(), f);
  ok('F1 Santa Rita: "3 a entregar · 1 sobra", "1 nota · 1 laudo", "1 a contar · 1 ajuste"', k('Santa Rita').req === '3 a entregar · 1 sobra' && k('Santa Rita').rec === '1 nota · 1 laudo' && k('Santa Rita').cnt === '1 a contar · 1 ajuste', k('Santa Rita'));
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
caso('F4', () => {
  ini(); ok('F4 visão Produção vazia na semente (a Colheita grava em c.producao)', estProducao(G(), 'Todas').length === 0, estProducao(G(), 'Todas'));
  M(c => { c.producao = { 'Soja|SJ26-01': { prod: 'Soja', lote: 'SJ26-01', cultura: 'Soja', un: 'sc', qtd: 1240, local: 'Silo 01', origem: { os: 'OS-0600', talhao: 'T1-A', safra: '2026/27' } } }; return { msg: 'lote de produção' }; });
  const p = estProducao(G(), 'Santa Rita'), q = estProducao(G(), 'Lagoa Grande');
  ok('F4 lote de produto acabado escrito pela Colheita aparece na fazenda do local (Silo 01 → Santa Rita), com a unidade da cultura', p.length === 1 && p[0].lote === 'SJ26-01' && p[0].qtdTxt === '1.240 sc' && q.length === 0, [p, q]);
});

console.log('\n' + (nfail ? nfail + ' FALHA(S)' : 'sem falhas'));
