// EX-53 M7a / KPI-PCM-08 · backlog por especialidade (man_backlog_unit_test.py monta: perfis + cenário + regras da manutenção + este arquivo).
// Oráculo independente: a definição do acordo (PR #47, 6259217691) refeita sobre os dados crus. Saída: uma linha JSON.
const R = []; const ok = (n, cond, info) => R.push({ n, ok: !!cond, info: cond ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 600) });
const caso = (n, fn) => { try { fn(); } catch (e) { R.push({ n: n + ' (exceção)', ok: false, info: String(e && e.stack || e).slice(0, 600) }); } };
const S = () => manClone(MAN0);
const PEND = ['A liberar', 'Liberadas', 'Em execução'];
const oraculo = (c, aid) => { const os = Object.values(c.oms).filter(o => PEND.indexOf(o.etapa) >= 0 && (!aid || o.aid === aid)); const esp = {}; let hh = 0, sem = 0;
  os.forEach(o => { const t = Number(o.tempo); if (t > 0) { hh += t; const e = o.esp || 'sem especialidade'; esp[e] = (esp[e] || 0) + t; } else sem++; }); return { n: os.length, hh, sem, esp }; };
const igual = (a, b) => Math.abs(a - b) < 1e-9;
const MOLDE = Object.values(MAN0.oms).find(o => o.tipo === 'Corretiva') || Object.values(MAN0.oms)[0];
// ordem de teste sem janela (sem conflito possível) e com executante: só o que o caso muda decide a situação
const nova = (c, id, etapa, tempo, extra) => { const o = manClone(MOLDE); Object.assign(o, { id, etapa, tempo, pecas: [], janIso: '', executante: 'Zé', conflitoAceito: false }, extra || {}); c.oms[id] = o; return o; };
const SIT = ['pronto', 'peca', 'tecnica'];
// a soma anterior da carga do Kanban da MA (até 262662af): tempo ausente vira 0 e não aparece
const antiga = os => os.reduce((s, o) => s + (Number(o.tempo) || 0), 0);

caso('semente', () => {
  const c = S(), r = manBacklog(c), o = oraculo(c);
  ok('B0 · semente: total, ordens e horas por especialidade batem com o oráculo independente', r.n === o.n && igual(r.hh, o.hh) && r.semTempo === o.sem
     && Object.keys(o.esp).length === Object.keys(r.porEsp).length && Object.keys(o.esp).every(k => igual(o.esp[k], r.porEsp[k])), [r.n, r.hh, r.semTempo, r.porEsp, o]);
  const soma = SIT.reduce((s, k) => s + r.sit[k].n, 0);
  ok('B1 · os três componentes (pronto, falta de peça, pendência técnica) repartem o backlog sem perder nem repetir ordem nem hora', Object.keys(r.sit).length === 3 && soma === r.n
     && igual(SIT.reduce((s, k) => s + r.sit[k].hh, 0), r.hh) && SIT.reduce((s, k) => s + r.sit[k].semTempo, 0) === r.semTempo, r.sit);
  // oráculo de dados (sonda de 19/10 na semente): OM-0228 Liberadas 3 h e OM-0233 Em execução 6,5 h prontas; OM-0234 A liberar 5 h em conflito com a OS-0420
  ok('B11 · semente: OM-0234 (A liberar com "Conflito · OS-0420") é pendência técnica, 5 HH; pronto = OM-0228 + OM-0233 = 9,5 HH',
     manBacklogSit(c, c.oms['OM-0234']) === 'tecnica' && /OS-0420/.test((manConflito(c, c.oms['OM-0234']) || {}).t || '') && igual(r.sit.tecnica.hh, 5) && r.sit.tecnica.n === 1
     && igual(r.sit.pronto.hh, 9.5) && r.sit.pronto.n === 2 && r.sit.peca.n === 0, r.sit);
  const d = manClone(c); d.oms['OM-0234'].conflitoAceito = true;
  ok('B12 · o mesmo conflito aceito pelo PCP não bloqueia: OM-0234 passa a "Pronta para liberar" (pronto)', manBacklogSit(d, d.oms['OM-0234']) === 'pronto' && igual(manBacklog(d).sit.pronto.hh, 14.5), manBacklog(d).sit);
  const e = manClone(c), k0 = Object.keys(e.itens)[0], i0 = e.itens[k0]; e.oms['OM-0234'].pecas = [{ item: k0, nome: 'peça', qtd: i0.saldo - i0.reservado + 10, un: 'un' }];
  ok('B13 · conflito e peça em falta juntos: vale a ordem do §5.2, pendência técnica (não falta de peça); as duas pendências são reais',
     manFalta(e, e.oms['OM-0234']).length === 1 && !!manConflito(e, e.oms['OM-0234']) && manBacklogSit(e, e.oms['OM-0234']) === 'tecnica' && manBacklog(e).sit.peca.n === 0, manBacklog(e).sit);
  ok('B2 · sem capacidade configurada não há semanas equivalentes', r.semanas === null, r.semanas);
});

caso('regras', () => {
  const c = S(); c.oms = {};
  ok('B3 · sem ordem pendente: n = 0 e 0 HH', manBacklog(c).n === 0 && manBacklog(c).hh === 0, manBacklog(c));
  nova(c, 'X1', 'Liberadas', 4, { esp: 'Mecânico' });
  nova(c, 'X2', 'Em execução', 2.5, { esp: 'Eletricista' });
  nova(c, 'X3', 'Em conferência', 9, { esp: 'Mecânico' });
  nova(c, 'X4', 'Encerradas', 7, { esp: 'Mecânico' });
  nova(c, 'X5', 'Canceladas', 3, { esp: 'Mecânico' });
  let r = manBacklog(c);
  ok('B4 · em conferência, encerrada e cancelada ficam fora: 6,5 HH (Mecânico 4, Eletricista 2,5)', r.n === 2 && igual(r.hh, 6.5) && igual(r.porEsp['Mecânico'], 4) && igual(r.porEsp['Eletricista'], 2.5), r);
  ok('B5 · Liberadas e Em execução = pronto', r.sit.pronto.n === 2 && igual(r.sit.pronto.hh, 6.5) && r.sit.peca.n === 0 && r.sit.tecnica.n === 0, r.sit);
  nova(c, 'X6', 'Liberadas', undefined, { esp: 'Mecânico' });
  r = manBacklog(c);
  ok('B6 · ordem aberta sem tempo previsto não vira 0: conta em sem estimativa e não muda o total', r.n === 3 && r.semTempo === 1 && igual(r.hh, 6.5) && /1 sem estimativa/.test(manHHTxt(r)), [r, manHHTxt(r)]);
  const abertas = Object.values(c.oms).filter(o => PEND.indexOf(o.etapa) >= 0);
  ok('B7 · contraprova: a soma antiga da carga (tempo ausente = 0) dá o mesmo total sem avisar que falta estimativa', igual(antiga(abertas), 6.5) && !/sem estimativa/.test(manN(antiga(abertas), 1) + ' HH'), antiga(abertas));
  const k = Object.keys(c.itens)[0], it = c.itens[k];
  nova(c, 'X7', 'A liberar', 3, { esp: 'Mecânico', pecas: [{ item: k, nome: 'peça', qtd: it.saldo - it.reservado + 10, un: 'un' }] });
  nova(c, 'X8', 'A liberar', 1, { esp: 'Mecânico' });
  r = manBacklog(c);
  ok('B8 · A liberar com peça em falta fica em falta de peça; sem impedimento, "Pronta para liberar" entra em pronto', manFalta(c, c.oms.X7).length === 1 && r.sit.peca.n === 1 && igual(r.sit.peca.hh, 3)
     && manBacklogSit(c, c.oms.X8) === 'pronto' && r.sit.pronto.n === 4 && r.sit.tecnica.n === 0, r.sit);
  nova(c, 'X9', 'A liberar', 2, { esp: 'Especialidade sem pessoa', executante: '' });
  nova(c, 'X10', 'A liberar', undefined, { esp: 'Mecânico' });
  r = manBacklog(c);
  ok('B14 · pronta × bloqueada: A liberar sem executante possível (X9) e sem tempo previsto (X10) são pendência técnica, como no manLiberar; a X8 continua pronta',
     manExecSug(c.oms.X9) === '' && manBacklogSit(c, c.oms.X9) === 'tecnica' && manBacklogSit(c, c.oms.X10) === 'tecnica' && manBacklogSit(c, c.oms.X8) === 'pronto'
     && r.sit.tecnica.n === 2 && igual(r.sit.tecnica.hh, 2) && r.sit.tecnica.semTempo === 1 && SIT.reduce((s, k) => s + r.sit[k].n, 0) === r.n && igual(SIT.reduce((s, k) => s + r.sit[k].hh, 0), r.hh), r.sit);
  delete c.oms.X9; delete c.oms.X10;
  const s = manClone(c); Object.values(s.oms).forEach(o => { o.tempo = undefined; });
  const t = manBacklog(s);
  ok('B9 · todas sem tempo: o texto é "N sem estimativa", nunca "0 HH"', manHHTxt(t) === t.n + ' sem estimativa' && !/0 HH/.test(manHHTxt(t)), manHHTxt(t));
  const a1 = c.oms.X1.aid; c.oms.X2.aid = a1 + '_outro';
  r = manBacklog(c, a1);
  const oa = oraculo(c, a1);
  ok('B10 · filtro por ativo: só as ordens daquele ativo (a X2 movida para outro ativo sai)', r.n === oa.n && igual(r.hh, oa.hh) && r.n === manBacklog(c).n - 1, [r.n, r.hh, oa]);
});
print(JSON.stringify(R));
