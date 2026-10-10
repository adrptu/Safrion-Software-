// Oráculo de força bruta, INDEPENDENTE de ocupacao.js/py (não importa nada do serviço). Versão 2 (correções da verificação SAF-C01, 09/10/2026):
// área física por dia (na mesma faixa a maior; talhão inteiro cobre o talhão); o dia só sai da soma do alvo com par do próprio alvo na mesma área
// (no núcleo, com plano em um dos dois; no previsto, qualquer); M1 pelo núcleo do alvo (pior dia, quem, período e Máximo, com a T-área).
// Base: oraculo.js do verificador 1 (scratchpad safc01-oraculo), mesma derivação das ocupações e o mesmo horizonte.
// Para cada fixture: deriva as ocupações a partir da ESPECIFICACAO.md (R-03, R-04, R-06, R-07, R-08, R-14 núcleo) para planos só com DAP,
// e soma DIA A DIA, de min(início) até um horizonte finito grande (31/12/2080; perene sem fim = ativa até o horizonte, só aqui no oráculo):
//   núcleo (certo) ativo em x: plantio <= x < fim do núcleo + folga, ou x = plantio            → T-soma (R-14)
//   previsto ativo em x: início <= x < Ocupa até (est) + folga                                 → soma prevista (R-15)
// T-soma num dia: Σ núcleos > T + 0,005, com plano (ou perene) em algum, e sem par na mesma faixa/talhão inteiro (faixas diferentes).
// Saída por fixture: soma_trav (com alvo, mesma forma do serviço), soma_pend (pendências NOVAS = depois(alvo) − antes(sem alvo)),
// tabela (alvo nulo sobre próprias + de fora da safra), excesso, pior dia da mensagem M1, e "excesso físico" (núcleos > T com o alvo, sem filtros).
// Uso: node oraculo.js <fixtures.json>
const fs = require('fs');
const INF = 1e8;
const H = Math.round(Date.UTC(2080, 11, 31) / 86400000);
const dia = (s) => { if (!s) return null; const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(s); return Math.round(Date.UTC(+m[1], +m[2] - 1, +m[3]) / 86400000); };
const r2 = (x) => Math.floor(x * 100 + 0.5) / 100;
const mais = (d, n) => (d >= INF ? INF : d + n);

function ctxDe(c, folga) {
  const cic = {}, mn = {}, mx = {};
  c.cultivares.forEach(([cu, v, d]) => { cic[cu + '|' + v] = d; mn[cu] = Math.min(mn[cu] ?? 1e9, d); mx[cu] = Math.max(mx[cu] ?? 0, d); });
  const pl = {}; c.planos.forEach((p) => { pl[p.id] = p; });
  return { classe: c.culturas, cic, mn, mx, pl, pub: c.planos.filter((p) => (p.estado || 'Publicado') === 'Publicado'), folga };
}
// R-03/R-04/R-06/R-08/R-14 só com gatilhos DAP (as fixtures não usam DATA/DANC/DAPC)
function deriva(K, c, s) {
  const p = dia(c.plantio);
  let pid = c.plano || null; if (pid && (!K.pl[pid] || K.pl[pid].cultura !== c.cult)) pid = null;
  const dap = pid ? K.pl[pid].atividades.map((a) => { if (a.g.tipo !== 'DAP') throw new Error('fixture fora do oráculo'); return a.g.dias; }) : [];
  const ini = pid ? Math.min(p, ...dap.map((d) => p + d)) : p;
  const colh = c.colheita ? dia(c.colheita) : null, real = c.colheita_real ? dia(c.colheita_real) : null;
  let classe, fim;
  if (K.classe[c.cult] === 'Perene') { classe = 'perene'; fim = INF; }
  else if (real !== null) { classe = 'observado'; fim = real; }
  else if (pid) { classe = 'plano'; fim = Math.max(p, ...dap.map((d) => p + d), ...(colh !== null ? [colh] : [])); }
  else if (colh !== null) { classe = 'informada'; fim = colh; }
  else {
    const cands = []; const k = c.cult + '|' + (c.var || ''); if (k in K.cic) cands.push(p + K.cic[k]);
    K.pub.filter((q) => q.cultura === c.cult).forEach((q) => { cands.push(Math.max(...q.atividades.map((a) => p + a.g.dias))); });
    if (cands.length) { classe = 'estimado'; fim = Math.max(...cands); } else { classe = 'semdata'; fim = null; }
  }
  const cm = K.mn[c.cult];
  const nuc = classe === 'perene' ? INF : classe === 'observado' ? real : cm ? Math.min(fim === null ? INF : fim, p + cm - 1) : p;
  const safim = dia(s.fim);
  const P = classe === 'perene' ? INF : ['plano', 'informada', 'observado'].includes(classe) ? fim
    : classe === 'estimado' ? Math.max(safim, fim) : (K.mx[c.cult] ? Math.max(safim, p + K.mx[c.cult]) : INF);
  return { id: c.id, ciclo: c.ciclo || c.id, safs: [c.saf], faz: c.faz, t: c.talhao, faixa: c.faixa, tipo: c.tipo, area: Number(c.area || 0), cult: c.cult,
    plantio: p, ini, classe, fim, nuc, nucLib: mais(nuc, K.folga), libEst: mais(classe === 'semdata' ? p : fim, K.folga), libPior: mais(P, K.folga),
    plano: pid, comPlano: !!pid || classe === 'perene' };
}
function ocupacoes(K, safras, cults) { // R-07: uma por ciclo, a primeira da lista, lembrando as safras
  const out = [], vis = {};
  cults.forEach((c) => { const s = safras[c.saf]; if (!s) return; const o = deriva(K, c, s); if (vis[o.ciclo]) { vis[o.ciclo].safs.push(c.saf); return; } vis[o.ciclo] = o; out.push(o); });
  return out;
}
const mesma = (a, b) => a.faixa === b.faixa || a.tipo !== 'Parcela' || b.tipo !== 'Parcela';
const fisica = (l) => { const ti = []; const fx = {}; l.forEach((o) => { if (o.tipo !== 'Parcela') ti.push(o.area); else (fx[o.faixa] = fx[o.faixa] || []).push(o.area); });
  let p = 0; const ks = Object.keys(fx); ks.forEach((k) => { p += Math.max(...fx[k]); }); return !ti.length ? p : (ks.length ? Math.max(...ti, p) : Math.max(...ti)); };
const parAlvo = (l, alvo, plano) => { const a = l.find((o) => alvo && o.id === alvo); return !!a && l.some((b) => b !== a && b.ciclo !== a.ciclo && mesma(a, b) && (!plano || a.comPlano || b.comPlano)); };
const nucAt = (o, x) => (o.plantio <= x && x < o.nucLib) || o.plantio === x;
const posterior = (a, b) => (a.plantio !== b.plantio ? a.plantio > b.plantio : a.id > b.id); // a vem depois de b (plantio, id)
// força bruta dia a dia
function soma(occs, T, alvo) {
  const trav = [], visT = new Set(), pv = new Map(), ord = [];
  if (!occs.length) return { trav, pend: {} };
  const lo = Math.min(...occs.map((o) => o.ini)) - 1;
  for (let x = lo; x <= H; x++) {
    const nu = occs.filter((o) => (o.plantio <= x && x < o.nucLib) || o.plantio === x);
    const sN = fisica(nu);
    if (sN > T + 0.005 && nu.some((o) => o.comPlano) && !parAlvo(nu, alvo, true)) {
      if (!alvo || nu.some((o) => o.id === alvo)) {
        const last = nu.reduce((m, o) => (!m || posterior(o, m) ? o : m), null);
        const k = nu.filter((o) => o !== last).map((o) => o.id).sort().join('+');
        if (!visT.has(k + '>' + last.id)) { visT.add(k + '>' + last.id); trav.push(['soma', k, last.id, x, r2(sN)]); }
      }
      continue;
    }
    const pr = occs.filter((o) => o.ini <= x && x < o.libEst);
    const sP = fisica(pr);
    if (sP > T + 0.005 && !parAlvo(pr, alvo, false)) {
      const last = pr.reduce((m, o) => (!m || posterior(o, m) ? o : m), null);
      const key = last.id + '>' + pr.filter((o) => o !== last).map((o) => o.id).sort().join('+');
      if (!pv.has(key)) { pv.set(key, []); ord.push(key); } pv.get(key).push(x);
    }
  }
  const pend = {};
  ord.forEach((key) => { const i = key.indexOf('>'); const lid = key.slice(0, i), causa = key.slice(i + 1); const d = pv.get(key);
    if (alvo && alvo !== lid && causa.split('+').indexOf(alvo) < 0) return;
    (pend[lid] = pend[lid] || []).push(['soma', causa, d[0], d[d.length - 1], d.length]); });
  return { trav, pend };
}
const eq = (p, q) => JSON.stringify(p) === JSON.stringify(q);
const dados = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const out = {};
const t0 = Date.now();
for (const f of dados.fixtures) {
  const K = ctxDe(f.ctx || dados.ctx, f.folga);
  const occ = ocupacoes(K, f.safras, f.depois); const o = occ.find((x) => x.id === f.alvo);
  if (!o) { out[f.id] = { sem_alvo: true }; continue; }
  const mesmo = occ.filter((x) => x.faz === o.faz && x.t === o.t);
  const dep = soma(mesmo, f.T, f.alvo);
  const occ0 = ocupacoes(K, f.safras, f.antes).filter((x) => x.faz === o.faz && x.t === o.t);
  const ant = soma(occ0, f.T, null);
  const novas = {}; Object.keys(dep.pend).forEach((k) => { const n = dep.pend[k].filter((p) => !(ant.pend[k] || []).some((q) => eq(p, q))); if (n.length) novas[k] = n; });
  // excesso físico com o alvo (sem filtro de plano nem de faixa): soma dos núcleos > T num dia em que o alvo está em núcleo
  let fis = null;
  for (let x = Math.min(...mesmo.map((y) => y.ini)); x <= H && fis === null; x++) {
    if (!((o.plantio <= x && x < o.nucLib) || o.plantio === x)) continue;
    const nu = mesmo.filter((y) => (y.plantio <= x && x < y.nucLib) || y.plantio === x); const s = fisica(nu);
    if (s > f.T + 0.005) fis = { x, s: r2(s), ids: nu.map((y) => y.id), comPlano: nu.some((y) => y.comPlano), cruz: parAlvo(nu, f.alvo, true) };
  }
  // tabela da safra do alvo (alvo nulo): próprias + de fora que cruzam a safra no pior caso (R-09/R-12)
  const s = f.safras[f.sid]; const a = dia(s.ini), b = dia(s.fim);
  const occT = ocupacoes(K, f.safras, f.depois).filter((x) => x.faz === s.faz && x.t === 'T1');
  const own = occT.filter((x) => x.safs.indexOf(f.sid) >= 0), fora = occT.filter((x) => x.safs.indexOf(f.sid) < 0 && x.ini <= b && x.libPior > a);
  const tb = soma(own.concat(fora), f.T, null);
  const exc = r2(Math.max(0, Math.max(f.T, ...tb.trav.map((t) => t[4])) - f.T));
  // M1 (v2): nos dias de núcleo do alvo, a maior área física dos outros em núcleo; quem = os do primeiro desses dias; período do maior início
  // ao menor fim entre o alvo e eles; Máximo = T − pior (com a T-área: o mínimo com o que sobra desta safra). Dia a dia até o horizonte.
  const outros = mesmo.filter((x) => x !== o);
  let m1 = null, best = null;
  for (let x = o.plantio; x <= H; x++) { if (!nucAt(o, x)) { if (x > o.plantio) break; continue; } const at = outros.filter((y) => nucAt(y, x)); if (at.length && (!best || fisica(at) > best.pior)) best = { pior: fisica(at), quem: at }; }
  if (best) {
    const ini = Math.max(o.ini, ...best.quem.map((x) => x.ini));
    const fim = Math.max(ini, Math.min(o.fim !== null ? o.fim : o.plantio, ...best.quem.filter((x) => x.fim !== null).map((x) => x.fim)));
    const somaSafra = mesmo.filter((x) => x.safs.indexOf(f.sid) >= 0).reduce((q, x) => q + x.area, 0);
    let mx = f.T - best.pior; if (somaSafra > f.T + 0.005) mx = Math.min(mx, f.T - outros.filter((x) => x.safs.indexOf(f.sid) >= 0).reduce((q, x) => q + x.area, 0));
    m1 = { ini, fim, fim_inf: fim >= INF, pior: r2(best.pior), max: Math.max(0, Math.floor(mx * 100 + 1e-6) / 100), quem: best.quem.map((x) => x.id) };   // Máximo para baixo
  }
  out[f.id] = { soma_trav: dep.trav, soma_pend: novas, tab_soma_trav: tb.trav, tab_soma_pend: tb.pend, tab_exc: exc, tab_own: own.map((x) => x.id), tab_fora: fora.map((x) => x.id),
    fis, m1, occ: mesmo.map((x) => [x.id, x.classe, x.ini, x.plantio, x.nucLib, x.libEst, x.libPior]) };
}
process.stdout.write(JSON.stringify({ H, ms: Date.now() - t0, res: out }));
