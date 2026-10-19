// EX-53 M5 / KPI-PCM-05 · cumprimento de preventiva (man_cumprimento_unit_test.py monta: perfis + cenário + regras da manutenção + este arquivo).
// Cada caso parte da semente (MAN0) com ordens sintéticas copiadas de uma preventiva da própria semente. Saída: uma linha JSON.
const R = []; const ok = (n, cond, info) => R.push({ n, ok: !!cond, info: cond ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 600) });
const caso = (n, fn) => { try { fn(); } catch (e) { R.push({ n: n + ' (exceção)', ok: false, info: String(e && e.stack || e).slice(0, 600) }); } };
const S = () => manClone(MAN0);
const base = c => Object.values(c.oms).find(o => o.tipo === 'Preventiva');
const dia = (c, d) => manAdd(c.hoje, d);
const MOLDE = base(MAN0);
const nova = (c, id, etapa, venc, exec) => { const o = manClone(MOLDE); Object.assign(o, { id, etapa, vencOrig: venc, janIso: venc, exec: exec ? { data: exec } : null }); c.oms[id] = o; return o; };
const soPrev = c => { Object.keys(c.oms).forEach(k => { if (c.oms[k].tipo === 'Preventiva') delete c.oms[k]; }); };
// a regra anterior (até d491c55e): só encerradas, pelo dia da execução no período
const antiga = (c, k) => { const P = manPeriodo(c, k); const os = Object.values(c.oms).filter(o => o.tipo === 'Preventiva' && o.etapa === 'Encerradas' && o.vencOrig && o.exec && o.exec.data >= P.de && o.exec.data <= P.ate);
  if (!os.length) return null; const n = os.filter(o => o.exec.data <= o.vencOrig).length; return { ok: n, n: os.length, pct: Math.round(n * 100 / os.length) }; };

caso('semente', () => {
  const c = S(); const r = manCumprimento(c, '12m'); const so = manSemOrdem(c).venc.filter(l => l.x.sit === 'Vencida');
  ok('C0 · há preventiva na semente para servir de molde', !!base(c), Object.keys(c.oms));
  ok('C1 · composição: n = encerradas no prazo + atrasadas + abertas vencidas + vencidas sem ordem; pct = ok ÷ n', r === null || (r.n === r.ok + r.atrasadas + r.abertas + r.semOrdem && r.pct === Math.round(r.ok * 100 / r.n)), r);
  ok('C2 · vencida sem ordem não tem OM (não conta duas vezes)', so.every(l => !l.om), so.map(l => [l.aid, l.sid, !!l.om]));
});

caso('regras', () => {
  const c = S(); soPrev(c); c.planos = {}; c.vinc = {};
  ok('C3 · base vazia = null (nunca 100%)', manCumprimento(c, '12m') === null, manCumprimento(c, '12m'));
  nova(c, 'T1', 'Encerradas', dia(c, -10), dia(c, -12));
  let r = manCumprimento(c, '12m');
  ok('C4 · uma encerrada antes do vencimento: 1 de 1, 100%', r && r.ok === 1 && r.n === 1 && r.pct === 100, r);
  nova(c, 'T2', 'Encerradas', dia(c, -20), dia(c, -15));
  r = manCumprimento(c, '12m');
  ok('C5 · encerrada com atraso fica só no denominador: 1 de 2, 50%, 1 atrasada', r && r.ok === 1 && r.n === 2 && r.atrasadas === 1 && r.pct === 50, r);
  nova(c, 'T3', 'Liberadas', dia(c, -5), null);
  r = manCumprimento(c, '12m');
  ok('C6 · aberta já vencida entra no denominador: 1 de 3, 33%', r && r.ok === 1 && r.n === 3 && r.abertas === 1 && r.pct === 33, r);
  nova(c, 'T4', 'A liberar', c.hoje, null);
  r = manCumprimento(c, '12m');
  ok('C7 · aberta que vence hoje ainda não conta', r && r.n === 3 && r.abertas === 1, r);
  nova(c, 'T5', 'Canceladas', dia(c, -3), null);
  r = manCumprimento(c, '12m');
  ok('C8 · cancelada fora da base', r && r.n === 3, r);
  nova(c, 'T6', 'Encerradas', dia(c, -400), dia(c, -401));
  r = manCumprimento(c, '12m');
  ok('C9 · vencimento original fora do período (12 m) não entra', r && r.n === 3, r);
  const a = antiga(c, '12m');
  ok('C10 · contraprova: a regra antiga ignora a aberta vencida (1 de 2 = 50%); a nova dá 1 de 3 = 33%', a && a.n === 2 && a.pct === 50 && r.pct === 33, [a, r]);
});

caso('por ativo', () => {
  const c = S(); soPrev(c); c.planos = {}; c.vinc = {};
  const a1 = MOLDE.aid, a2 = Object.keys(c.ativos).find(k => k !== a1);
  nova(c, 'P1', 'Encerradas', dia(c, -10), dia(c, -12));
  const o2 = nova(c, 'P2', 'Liberadas', dia(c, -5), null); o2.aid = a2;
  const t = manCumprimento(c, '12m'), r1 = manCumprimento(c, '12m', a1), r2 = manCumprimento(c, '12m', a2);
  ok('C11 · aid filtra o ativo: o total vê 1 de 2; o ativo 1 vê 1 de 1; o ativo 2 vê 0 de 1 (a aberta vencida dele)', t && t.n === 2 && r1 && r1.ok === 1 && r1.n === 1 && r2 && r2.ok === 0 && r2.n === 1, [t, r1, r2]);
  const velha = (c, aid) => { const os = Object.values(c.oms).filter(o => o.aid === aid && o.tipo === 'Preventiva' && o.etapa === 'Encerradas' && o.vencOrig); return os.length ? os.filter(o => o.exec && o.exec.data <= o.vencOrig).length + ' de ' + os.length : 'não calculável'; };
  ok('C12 · contraprova: a conta antiga do detalhe do ativo (só encerradas) dava "não calculável" ao ativo 2 com a preventiva vencida em aberto', velha(c, a2) === 'não calculável' && r2.n === 1, [velha(c, a2), r2]);
});

print(JSON.stringify(R));   // print: o jsc do Mac não tem console; no node o prelúdio do teste define print (Codex 6258137889)
