// SUP-1 · O.S. × Estoque (docs/suprimentos-simplificado §0.2 e §7): o bloqueio do encerramento diz o caso certo (sinal, consumo em conferência ou sobra)
// e os atalhos da O.S. levam ao registro no Estoque (#req=), sem o almoxarife procurar. Node, sem navegador. Executor: sup_os_test.py.
let nfail = 0;
function ok(t, c, got) { if (c) console.log('OK    ' + t); else { nfail++; console.log('FALHA ' + t + (got === undefined ? '' : ' · ' + JSON.stringify(got).slice(0, 400))); } }
const caso = (t, f) => { try { f(); } catch (e) { ok('ERRO no caso "' + t + '": ' + String(e.message || e), false); } };
const P = k => G2_PERFIS.find(p => p.k === k); const RUI = P('Rui');
const M = f => cenMudar(null, f); const O = id => ords(null).find(o => o.id === id);
caso('D-R10', () => {
  cenReset(); M(c => cenDevolver(c, 'REQ-031', 'MAP 11-52', 500, true, RUI));
  // OS-0417 em conferência sem sobra, com um consumo em conferência aberto (relato acima do que estava com Paula)
  M(c => { c.confs = [{ id: 'CC-301', os: 'OS-0417', req: 'REQ-031', prod: 'MAP 11-52', lote: 'M26-07', un: 'kg', relatado: 100, custodia: 0, dia: 4, at: '10:00', quem: 'Paula', resp: CEN_CONC_RESP,
    estado: 'Em conferência', motivo: 'Consumo acima da custódia', sinc: true }]; cenSeloConf(c, 'OS-0417'); return { msg: 'caso montado' }; });
  const o = O('OS-0417'); const b = osEncBloq(o);
  ok('D-R10 O.S. em conferência com consumo em conferência e nada em custódia: sem selo "Sobras a receber" (antes: ficava)', !o.selos.some(s => s.t === 'Sobras a receber') && o.selos.some(s => s.t === 'Consumo em conferência'), o.selos);
  ok('D-R10 dono e prazo: Rui concilia o consumo (antes: "receber a devolução")', o.dono === 'Rui (almoxarife)' && o.prazo === 'conciliar o consumo', [o.dono, o.prazo]);
  ok('D-R10 encerrar bloqueado nomeia o consumo em conferência, não sobra em custódia, e leva à REQ-031 no Estoque', /consumo em conferência/i.test(b.t) && !/sobra em custódia/i.test(b.t) && b.h === 'EST.dc.html#req=REQ-031' && /concilia/.test(b.q), b);
});
caso('links', () => {
  cenReset(); const b = osEncBloq(O('OS-0417'));
  ok('sobra em custódia: "Receber devolução no Estoque" abre a REQ-031 (#req=), não a seção 1', /sobra em custódia/.test(b.t) && b.h === 'EST.dc.html#req=REQ-031', b);
  const e = osIniErro(O('OS-0424'), cenGet().reqs['REQ-039']);
  ok('iniciar sem entrega: "Entregar no Estoque" abre a REQ-039 (#req=)', e && e.h === 'EST.dc.html#req=REQ-039' && e.hl === 'Entregar no Estoque', e);
});
console.log('\n' + (nfail ? nfail + ' FALHA(S)' : 'sem falhas'));
