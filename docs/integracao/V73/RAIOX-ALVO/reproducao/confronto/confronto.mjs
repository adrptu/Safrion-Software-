// Confronto Claude × Codex do Raio-X do alvo: provas próprias, sem navegador, das contraprovas do Codex e das divergências.
// Uso: node confronto.mjs <v3.html> <saída.json>
// Fonte: docs/integracao/V73/pedidos-1610/raiox-pragas-no-tempo-v3.html, commit 529adf7, SHA-256 e7872cb0…805e5e (extrair com git show).
// Extrai o motor do v3 (do 'use strict' do último <script> até "// ===== estado =====") e roda num contexto vm isolado,
// sem require e sem process. Dados 100 % sintéticos; nenhum dado real; nenhum segredo.
// Ganchos (cada um com 1 ocorrência conferida; falha se não achar o texto exato):
//   G1 semente das réplicas (igual à reprodução da crítica);
//   G2 clima da análise trocável depois de um dia de corte (a simulação continua com o clima verdadeiro);
//   G3 a G5 instrumentam o rxHT só com campos de leitura (nível de pareamento usado, controles com leitura depois de D);
//       E e nCtrl não mudam: a seção "autoconferencia" compara com o rxHT sem instrumentação.
import fs from 'node:fs';
import crypto from 'node:crypto';
import vm from 'node:vm';

const htmlPath = process.argv[2], outPath = process.argv[3];
if (!htmlPath || !outPath) { console.error('uso: node confronto.mjs <v3.html> <saida.json>'); process.exit(2); }
const html = fs.readFileSync(htmlPath, 'utf8');
const sha = crypto.createHash('sha256').update(html).digest('hex');
const sIdx = html.lastIndexOf('<script>'), US = "'use strict';", start = html.indexOf(US, sIdx) + US.length, end = html.indexOf('// ================= estado =================');
if (sIdx < 0 || start < US.length || end < start) throw new Error('marcadores do motor não encontrados');
const CORE = html.slice(start, end);

function montar(instrumentar) {
  let core = CORE;
  const swap = (from, to) => { const n = core.split(from).length - 1; if (n !== 1) throw new Error('gancho ambíguo (' + n + '): ' + from.slice(0, 50)); core = core.replace(from, to); };
  swap('function rngFor(s) { let h = 2166136261;', 'function rngFor(s) { s = __SALT + s; let h = 2166136261;');
  swap('const climaAt = d => d <= DAYS ? CLIMA[d] : CLIMA_PREV[d - DAYS - 1];',
       'const climaAt = d => { const P = __CFG.pos; if (P && d > P.cut && d <= DAYS) d = P.map(d); return d <= DAYS ? CLIMA[d] : CLIMA_PREV[d - DAYS - 1]; };');
  if (instrumentar) {
    swap('near: cb.v >= .3 * ap.before.v });', 'near: cb.v >= .3 * ap.before.v, fut: cb.day > D || ca.day > D });');
    swap('let use = cands.filter(c => c.same && c.near); if (use.length < 2) use = cands.filter(c => c.same); if (use.length < 2) use = cands;',
         'let use = cands.filter(c => c.same && c.near), __tier = 1; if (use.length < 2) { use = cands.filter(c => c.same); __tier = 2; } if (use.length < 2) { use = cands; __tier = 3; }');
    swap('ev: back });', 'ev: back, tier: use.length >= 2 ? __tier : 0, nCands: cands.length, futUsed: use.filter(c => c.fut).length });');
  }
  return core;
}

const EXTRA = String.raw`
const r4 = v => v == null || !isFinite(v) ? v : Math.round(v * 1e4) / 1e4;
const pp = v => v == null ? null : Math.round(v * 1000) / 10;
const limpa = () => { WCACHE.clear(); RXC.clear(); };
const hsh = (d, s) => { let h = (d * 2654435761 + s * 40503) >>> 0; h ^= h >>> 13; h = Math.imul(h, 2246822519) >>> 0; return (h ^ (h >>> 16)) >>> 0; };

// ---------- C1 · controle lido depois de D (contraprova 1 do Codex) ----------
function c1Fixture() {   // mesma fixture do Codex, rodando o rxHT extraído do v3; mais duas variantes só da leitura posterior a D
  const savedP = PIVOS.slice(), a = { id: 'teste', nc: 10 };
  const roda = ctrl => { PIVOS.splice(0, PIVOS.length, { id: 'T', stage: 'adulta' }, { id: 'C1', stage: 'adulta' }, { id: 'C2', stage: 'adulta' });
    PEST.teste = { T: { obs: [], apps: [{ day: 2, before: { day: 1, v: 10 }, after: { day: 10, v: 5 }, backDay: null, red: .5 }] } };
    ['C1', 'C2'].forEach(id => { PEST.teste[id] = { obs: ctrl.map(o => Object.assign({}, o)), apps: [] }; });
    const h = rxHT(a, 10)[0]; return { E: r4(h.E), nCtrl: h.nCtrl, controlesComLeituraDepoisDeD: h.futUsed }; };
  const r = { D: 10, tratado: 'antes D1 = 10, depois D10 = 5',
    controlesD1e12_iguais: roda([{ day: 1, v: 10 }, { day: 12, v: 10 }]),
    controlesSoAteD: roda([{ day: 1, v: 10 }]),
    controlesD12triplicado: roda([{ day: 1, v: 10 }, { day: 12, v: 30 }]) };
  PIVOS.splice(0, PIVOS.length, ...savedP); delete PEST.teste; return r;
}
function asOfPest(aId, D) { const o = PEST[aId], c = {}; Object.keys(o).forEach(pid => { c[pid] = { obs: o[pid].obs.filter(x => x.day <= D), apps: o[pid].apps.filter(x => x.day <= D) }; }); return c; }
function htAsOf(a, D) { const s = PEST[a.id]; PEST[a.id] = asOfPest(a.id, D); try { return rxHT(a, D); } finally { PEST[a.id] = s; } }
function c1Dados() {   // em cada data D da linha do tempo (1 a 86): rxHT do v3 × rxHT só com o que existia até D
  const out = {};
  ALVOS.forEach(a => { let itens = 0, comFut = 0, muda = 0, viraSem = 0, maxd = 0, em86 = 0; const apps = new Set(), datas = new Set();
    for (let D = 1; D <= DAYS; D++) { const H = rxHT(a, D), A = htAsOf(a, D); if (H.length !== A.length) throw new Error('as-of mudou a lista');
      H.forEach((h, i) => { const g = A[i]; if (h.ap !== g.ap) throw new Error('ordem'); itens++; if (h.futUsed > 0) { comFut++; if (D === DAYS) em86++; }
        const dif = (h.E == null) !== (g.E == null) || (h.E != null && Math.abs(h.E - g.E) > 1e-12);
        if (dif) { muda++; apps.add(h.pid + '@' + h.ap.day); datas.add(D); if (h.E != null && g.E == null) viraSem++; if (h.E != null && g.E != null) maxd = Math.max(maxd, Math.abs(h.E - g.E)); } }); }
    out[a.id] = { itensData: itens, usaControleLidoDepoisDeD: comFut, eMudaComDadosAteD: muda, viraSemComparacaoValida: viraSem, maxDeltaEpp: pp(maxd), aplicacoesAfetadas: apps.size, datasAfetadas: datas.size, emD86: em86 }; });
  return out;
}

// ---------- C3 · pareamento com fallback (contraprova 3 do Codex) ----------
const residuo = ap => Math.round(ap.prod.res * (0.7 + 0.3 * EQ[ap.eq].cov));
function c3Pareamento(D) {
  const out = {};
  ALVOS.forEach(a => { const H = rxHT(a, D), t = { 0: 0, 1: 0, 2: 0, 3: 0 }; H.forEach(h => { t[h.tier]++; });
    let estrita = 0, mesmoDia = 0;
    H.forEach(h => { const ap = h.ap, p = PIVOS.find(x => x.id === h.pid); if (ap.before.day === ap.day) { mesmoDia++; return; }
      let n = 0; PIVOS.forEach(q => { if (q.id === h.pid) return; const sq = PEST[a.id][q.id]; if (!sq) return; const ob = sq.obs.filter(o => o.day <= D);
        const cb = nearestObs(ob, ap.before.day, 2), ca = nearestObs(ob, ap.after.day, 2);
        if (!cb || !ca || ca.day <= cb.day || cb.v < .1 * a.nc) return; const ra = cb.v / ap.before.v; if (ra < .5 || ra > 2) return;
        if ((q.stage === 'jovem') !== (p.stage === 'jovem')) return; if (sq.apps.some(x => x.day <= ca.day && x.day + residuo(x) > cb.day)) return; n++; });
      if (n >= 2) estrita++; });
    out[a.id] = { aplicacoesComAntesDepois: H.length, nivel1_estadioENivel: t[1], nivel2_soEstadio: t[2], nivel3_qualquerCandidato: t[3], semComparacaoValida: t[0],
      regraEstritaClaude_valida: estrita, regraEstritaClaude_semComparacao: H.length - mesmoDia - estrita, antesNoMesmoDia_excluidas: mesmoDia }; });
  return out;
}

// ---------- C4 · seguimento do NC (EX-42 §8) × dias de proteção do v3 ----------
function c4Seguimento(D) {
  const out = {};
  ALVOS.forEach(a => { const H = rxHT(a, D); const c = { itens: H.length, v3_eventos: 0, v3_censurados: 0, retornoDemonstrado: 0, v3EventoSemLeituraAbaixo: 0, seguiuAbaixoAteUltimaLeitura: 0, semLeituraPos: 0, outraAplicacaoNoSeguimento: 0 };
    const larg = [], acres = [];
    H.forEach(h => { const s = PEST[a.id][h.pid], ap = h.ap; if (h.ev) c.v3_eventos++; else c.v3_censurados++;
      const pos = s.obs.filter(o => o.day > ap.day && o.day <= D), nx = s.apps.find(x => x.day > ap.day && x.day <= D);
      if (!pos.length) { c.semLeituraPos++; return; }
      if (pos[0].v >= a.nc) { c.v3EventoSemLeituraAbaixo++; return; }
      const j = pos.findIndex(o => o.v >= a.nc);
      if (j > 0) { c.retornoDemonstrado++; larg.push(pos[j].day - pos[j - 1].day); if (nx && nx.day < pos[j].day) c.outraAplicacaoNoSeguimento++; }
      else { c.seguiuAbaixoAteUltimaLeitura++; acres.push(D - pos[pos.length - 1].day); if (nx) c.outraAplicacaoNoSeguimento++; } });
    const st = v => v.length ? { n: v.length, min: Math.min(...v), max: Math.max(...v), media: r4(v.reduce((x, y) => x + y, 0) / v.length) } : { n: 0 };
    c.larguraDoIntervaloDeRetorno_dias = st(larg); c.diasAcrescidosPorCensurarEmD = st(acres); out[a.id] = c; });
  return out;
}

// ---------- C2 · teste da previsão com dado posterior à origem (contraprova 2 do Codex) ----------
function gateCom(a, D, R, feat) {   // réplica do gate do rxRisk (corte D − 21, 3 semanas de teste); só muda o cálculo das variáveis do teste
  const cut = D - 21, tr = R.rows.filter(r => r.d2 <= cut), te = R.rows.filter(r => r.d2 > cut);
  if (!(tr.length >= 24 && te.length >= 10)) return null; const Mt = rxFit(tr.map(r => Object.assign({}, r))); if (!Mt) return null;
  let bm = 0, bp = 0; te.forEach(r => { const xs = feat(Mt, r), y = r.v2 >= a.nc ? 1 : 0; bm += (predictRow(Mt, r, xs).p - y) ** 2; bp += ((r.v1 >= a.nc ? 1 : 0) - y) ** 2; });
  return { ok: bm < bp, bm: r4(bm / te.length), bp: r4(bp / te.length), n: te.length, ev: te.filter(r => r.v2 >= a.nc).length, beta: Mt.beta.map(r4), reps: Mt.reps.map(q => q.f.k + '/' + q.wi), te };
}
const nv = v => v == null ? -Infinity : v;
const featRealizado = (Mt, r) => Mt.reps.map(q => nv(fval(r, q.f, q.wi)));
function featPersistencia(a) { return (Mt, r) => { const g = r.d2 - r.d1, rp = Object.assign({}, r, { d1: r.d1 - g, d2: r.d1 });   // janelas que terminam na origem d1
  return Mt.reps.map(q => q.f.k === 'ndvi' || q.f.k === 'def' ? nv(fval(r, q.f, q.wi)) : q.f.k === 'aval' ? (PEST[a.id][r.pid].obs.find(z => z.day === r.d1).aval === 'B' ? 1 : 0) : nv(fval(rp, q.f, q.wi))); }; }
function featTroca(mapFor) { return (Mt, r) => { __CFG.pos = { cut: r.d1, map: mapFor(r.d1) }; WCACHE.clear(); const xs = featRealizado(Mt, r); __CFG.pos = null; WCACHE.clear(); return xs; }; }
const climatologia = d1 => d => Math.max(0, d1 - (hsh(d, 7) % 28));                  // dia sorteado das 4 semanas anteriores à origem
const previsao50 = d1 => d => (hsh(d, 11) % 2 === 0 ? d : Math.max(0, d1 - (hsh(d, 7) % 28)));   // metade dos dias certos
function janelaPosOrigem(Mt, te) { let tot = 0, pos = 0; te.forEach(r => Mt.reps.forEach(q => { if (q.f.wins === W1) return; tot++;
  const [, lo, hi] = q.f.wins[q.wi], a0 = q.wi === 0 && q.f.wins === W3 ? r.d1 : r.d2 - hi; if (r.d2 - lo > r.d1) pos++; })); return { variaveisDeJanela: tot, comDiasDepoisDaOrigem: pos }; }
function c2Gate(D) {
  const out = {};
  ALVOS.forEach(a => { limpa(); const R = rxGet(a.id, D); if (R.cold || !R.risk) { out[a.id] = { frio: true }; return; }
    const g0 = gateCom(a, D, R, featRealizado); if (!g0) { out[a.id] = { semGate: true }; return; }
    if (g0.bm !== r4(R.risk.gate.bm) || g0.bp !== r4(R.risk.gate.bp)) throw new Error('réplica do gate diverge do v3 em ' + a.id);
    const Mt = rxFit(R.rows.filter(r => r.d2 <= D - 21).map(r => Object.assign({}, r)));
    __CFG.pos = { cut: D - 21, map: d => d - 35 }; WCACHE.clear(); const gT = gateCom(a, D, R, featRealizado); __CFG.pos = null; WCACHE.clear();
    if (JSON.stringify(gT.beta) !== JSON.stringify(g0.beta)) throw new Error('o treino mudou ao trocar só o clima depois do corte');
    const gP = gateCom(a, D, R, featPersistencia(a)), gC = gateCom(a, D, R, featTroca(climatologia)), gH = gateCom(a, D, R, featTroca(previsao50));
    const f = g => ({ ok: g.ok, brierModelo: g.bm, brierPersistencia: g.bp });
    out[a.id] = { n: g0.n, eventos: g0.ev, reps: g0.reps, ...janelaPosOrigem(Mt, g0.te), v3_climaRealizado: f(g0), climaPosCorteTrocadoPor35DiasAntes: f(gT),
      honesto_tempoDosDiasAntesDaOrigem: f(gP), climatologia4Semanas: f(gC), previsaoMetadeDosDiasCerta: f(gH) }; });
  return out;
}
function c2SelecaoTeste(D) {   // o conjunto de teste só tem pares sem aplicação entre as vistorias: informação posterior à origem
  const out = {}, cut = D - 21;
  ALVOS.forEach(a => { let cand = 0, antes = 0, depois = 0, depoisPerto = 0, depoisAbaixo = 0;
    PIVOS.forEach(p => { const s = PEST[a.id][p.id]; if (!s) return; for (let i = 1; i < s.obs.length; i++) { const o1 = s.obs[i - 1], o2 = s.obs[i]; if (o2.day > D) break; if (o2.day <= cut) continue;
      const gap = o2.day - o1.day; if (gap < 5 || gap > 10 || o1.v < .1 * a.nc) continue; cand++;
      if (s.apps.some(ap => ap.day > o1.day - 10 && ap.day <= o1.day)) antes++; else if (s.apps.some(ap => ap.day > o1.day && ap.day <= o2.day)) { depois++; if (o1.v >= .9 * a.nc) depoisPerto++; if (o1.v >= .9 * a.nc && o1.v < a.nc) depoisAbaixo++; } } });
    out[a.id] = { paresCandidatos: cand, excluidosPorAplicacaoAteOrigem: antes, excluidosPorAplicacaoDepoisDaOrigem: depois, dessesComNivelNaOrigemAcimaDe90pctNC: depoisPerto, dessesAbaixoDoNCnaOrigem: depoisAbaixo }; });
  return out;
}
function c2Tela(Ds) {   // "Próximos 7 dias" no detalhe do talhão quando o usuário volta a linha do tempo para D < 86
  const out = {};
  ALVOS.forEach(a => { out[a.id] = Ds.map(D => { limpa(); const R1 = rxGet(a.id, D); if (R1.cold || !R1.risk) return { D, frio: true };
    const base = R1.risk.list.filter(x => x.st === 'ok'); __CFG.pos = { cut: D, map: d => d - 35 }; limpa(); const R2 = rxGet(a.id, D); __CFG.pos = null; limpa();
    const m = new Map(R2.risk.list.filter(x => x.st === 'ok').map(x => [x.pid, x])); let mud = 0, maxd = 0, fat = 0;
    base.forEach(b => { const x = m.get(b.pid), d = Math.abs(x.prob - b.prob); if (d > 1e-9) mud++; maxd = Math.max(maxd, d);
      if (JSON.stringify(x.up.map(z => z.q.f.k)) !== JSON.stringify(b.up.map(z => z.q.f.k))) fat++; });
    return { D, gateOk: R1.risk.gate.ok, talhoesComRisco: base.length, probMudouTrocandoSoClimaDepoisDeD: mud, maxDeltaPp: pp(maxd), fatoresMudaram: fat }; }); });
  return out;
}
function c2Manejo(D) {   // irrigação e adubação realizadas depois da origem também entram nas variáveis do risco
  limpa(); const a = ALVOS[0], p = PIVOS.find(x => PEST[a.id][x.id]), r = { pid: p.id, stage: p.stage, d1: D, d2: D + 7, v1: 1, eps: .05 * a.nc, nc: a.nc, aval: 'A' }, f = RXK('irr');
  const antes = fval(r, f, 0), old = WATER[p.id].irr[D + 3]; WATER[p.id].irr[D + 3] = old + 70; WCACHE.clear(); const depois = fval(r, f, 0); WATER[p.id].irr[D + 3] = old; WCACHE.clear();
  let adub = 0; const tal = new Set(); Object.keys(ADUB_BY).forEach(pid => ADUB_BY[pid].forEach(e => { if (e.day > D && e.day <= D + 7) { adub++; tal.add(pid); } }));
  return { origem: D, talhao: p.id, irrigacaoJanela0_antes: r4(antes), depoisDeSomar70mmNoDia: D + 3, irrigacaoJanela0_depois: r4(depois), delta: r4(depois - antes), adubacoesNos7DiasSeguintes: adub, talhoesComAdubacao: tal.size };
}

// ---------- C5 · seleção refeita em cada reamostragem (ponto 5 do Codex; 3.2 da crítica) ----------
function c5Selecao(B) {
  const out = {};
  ALVOS.forEach(a => { limpa(); const R = rxGet(a.id, DAYS), M = R.M, pl = PLANTED[a.id] || {}, px = PROXY[a.id] || {};
    const pids = [...new Set(R.rows.map(r => r.pid))], wks = [...new Set(R.rows.map(r => r.wk))], rng = rngFor('selboot' + a.id);
    const ks = RXF.map(f => f.k), dr = Object.fromEntries(ks.map(k => [k, []])), jan = Object.fromEntries(ks.map(k => [k, []])); let nb = 0;
    for (let b = 0; b < B; b++) { const cp = {}, cw = {}; pids.forEach(() => { const k = pids[Math.floor(rng() * pids.length)]; cp[k] = (cp[k] || 0) + 1; }); wks.forEach(() => { const k = wks[Math.floor(rng() * wks.length)]; cw[k] = (cw[k] || 0) + 1; });
      const rows = []; R.rows.forEach(r => { const m = (cp[r.pid] || 0) * (cw[r.wk] || 0); for (let i = 0; i < m; i++) rows.push(Object.assign({}, r)); });
      if (rows.length < 24) continue; const Mb = rxFit(rows); if (!Mb) continue; nb++;
      ks.forEach(k => { const q = Mb.reps.find(x => x.f.k === k); if (q) { dr[k].push(q.beta); jan[k].push(q.wi); return; }
        const mt = Mb.reps.find(x => x.mates.some(m => m.f.k === k)); if (mt) { const m = mt.mates.find(z => z.f.k === k), c = spear(mt.xv, m.x); dr[k].push(mt.beta * Math.sign(c || 1)); jan[k].push('grupo'); return; }
        dr[k].push(0); jan[k].push('fora'); }); }
    const pc = (v, f) => { const s = [...v].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.max(0, Math.round(f * (s.length - 1))))]; };
    const linhas = ks.map(k => { const q = M.reps.find(x => x.f.k === k), mt = q ? null : M.reps.find(x => x.mates.some(m => m.f.k === k)), src = q || mt;
      const nivel = q ? q.level : mt ? 'grupo de ' + mt.f.k + ':' + mt.level : '-';
      const ic = [pc(dr[k], .025), pc(dr[k], .975)], sinal = pl[k] || 0;
      return { k, plantado: sinal, proxy: px[k] || null, nivelV3: nivel, ic95v3_fixo: src ? src.ci95.map(r4) : null, ic95_selecaoRefeita: ic.map(r4),
        excluiZeroComSinalCerto: sinal ? (sinal > 0 ? ic[0] > 0 : ic[1] < 0) : null, excluiZero: ic[0] > 0 || ic[1] < 0,
        mesmaJanelaQueV3: q ? r4(jan[k].filter(w => w === q.wi).length / jan[k].length) : null, foraDoModelo: r4(jan[k].filter(w => w === 'fora').length / jan[k].length) }; });
    out[a.id] = { reamostras: nb, linhas }; });
  return out;
}

// ---------- C6 · o "nulo do clima" da crítica: o clima deslocado continua correlacionado com o verdadeiro? ----------
function c6Nulo(shifts) {
  const out = { diario: {}, janela0: {} }, ks = ['qs', 'tmax', 'ur', 'molh', 'chuva', 'lav'];
  shifts.forEach(sh => { const mp = d => (d + sh) % (DAYS + 1), dd = Array.from({ length: DAYS + 1 }, (_, d) => d);
    out.diario['desloca' + sh] = Object.fromEntries(['tmax', 'ur', 'chuva'].map(k => [k, r4(spear(dd.map(d => CLIMA[d][k]), dd.map(d => CLIMA[mp(d)][k])))]));
    out.janela0['desloca' + sh] = {};
    ALVOS.forEach(a => { limpa(); const rows = rxRows(a, DAYS), xt = {}; ks.forEach(k => { xt[k] = rows.map(r => fval(r, RXK(k), 0)); });
      __CFG.pos = { cut: -1, map: mp }; WCACHE.clear(); const o = {}; ks.forEach(k => { o[k] = r4(spear(impute(xt[k]), impute(rows.map(r => fval(r, RXK(k), 0))))); }); __CFG.pos = null; limpa();
      out.janela0['desloca' + sh][a.id] = o; }); });
  return out;
}
// ---------- C7 · contrato do backtest em origem móvel da crítica (reproducao/raiox_repro.mjs, função backtest) ----------
function c7Backtest() {
  const out = {};
  ALVOS.forEach(a => { const all = rxRows(a, DAYS); let n = 0, d1Depois = 0, maxDiasDepois = 0; const hz = {};
    for (let o = 43; o <= DAYS - 7; o += 7) { all.filter(r => r.d2 > o && r.d2 <= o + 7).forEach(r => { n++; const h = r.d2 - o; hz[h] = (hz[h] || 0) + 1; if (r.d1 > o) { d1Depois++; maxDiasDepois = Math.max(maxDiasDepois, r.d1 - o); } }); }
    out[a.id] = { paresDeTeste: n, d1DepoisDaOrigem: d1Depois, maxDiasDeTempoRealizadoDepoisDaOrigemNoSemPrevisao: maxDiasDepois, horizonteD2menosOrigem: hz }; });
  return out;
}

function hitsOriginais() { const o = {}; ALVOS.forEach(a => { limpa(); const R = rxGet(a.id, DAYS), g = gabaritoRows(R, a); o[a.id] = { hit: g.hit, tot: g.tot, fp: g.fp, gate: { ok: R.risk.gate.ok, bm: r4(R.risk.gate.bm), bp: r4(R.risk.gate.bp), n: R.risk.gate.n, ev: R.risk.gate.ev } }; }); return o; }
function htResumo(Ds) { const o = {}; ALVOS.forEach(a => { o[a.id] = Ds.map(D => rxHT(a, D).map(h => [h.pid, h.ap.day, r4(h.E), h.nCtrl])); }); return o; }

globalThis.__result = (() => {
  if (__MODO === 'auto') return htResumo([30, 50, 70, 86]);
  const r = { gabarito: hitsOriginais(), c1Dados: c1Dados(), c3: c3Pareamento(DAYS), c4: c4Seguimento(DAYS), c2Gate: c2Gate(DAYS), c2SelecaoTeste: c2SelecaoTeste(DAYS) };
  if (__MODO === 'completo') { r.c1Fixture = c1Fixture(); r.c2Tela = c2Tela([58, 65, 72, 79]); r.c2Manejo = c2Manejo(72); r.c5 = c5Selecao(200); r.c6Nulo = c6Nulo([21, 35, 49, 63]); r.c7Backtest = c7Backtest(); }
  return r;
})();
`;

function rodar(salt, modo, instr = modo !== 'auto') {
  const ctx = vm.createContext({ __SALT: salt, __CFG: { pos: null }, __MODO: modo, Intl, Math, Date, JSON, Map, Set, Object, Array, Number, String, Infinity, NaN, isFinite, Error, console });
  const LV = html.match(/^const LV = .*$/m)[0], SHOWN = html.match(/^const shown = .*$/m)[0];
  const gI = html.indexOf('function gabaritoRows(R, a, only) {'), gF = html.indexOf('\nfunction calcDetails', gI);
  if (gI < 0 || gF < 0) throw new Error('gabaritoRows não encontrado');
  const src = '(() => {\n"use strict";\n' + montar(instr) + '\n' + LV + '\n' + SHOWN + '\n' + html.slice(gI, gF) + '\n' + EXTRA + '\n})();';
  vm.runInContext(src, ctx, { timeout: 600000 });
  return JSON.parse(JSON.stringify(ctx.__result));
}

const t0 = performance.now();
const res = { artefato: { arquivo: htmlPath.split('/').pop(), bytes: Buffer.byteLength(html), sha256: sha }, node: process.version };
// Autoconferência: a instrumentação não muda E nem nCtrl do rxHT (D = 30, 50, 70 e 86).
res.autoconferencia = { rxHTigualSemInstrumentacao: JSON.stringify(rodar('', 'auto', false)) === JSON.stringify(rodar('', 'auto', true)) };
if (!res.autoconferencia.rxHTigualSemInstrumentacao) throw new Error('instrumentação alterou o rxHT');
res.original = rodar('', 'completo');
res.replicas = {};
for (let i = 1; i <= 20; i++) { const s = 'r' + String(i).padStart(2, '0') + ':'; res.replicas[s] = rodar(s, 'basico'); }
fs.writeFileSync(outPath, JSON.stringify(res, null, 1) + '\n');
console.error('ok · ' + Math.round((performance.now() - t0) / 100) / 10 + ' s');
