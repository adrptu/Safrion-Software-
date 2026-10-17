// Reprodução, sem navegador, dos números declarados do protótipo "Raio-X do alvo" (versão 3).
// Uso: node raiox_repro.mjs <caminho do HTML do v3> [saída.json] [origem] [nota]
// Fonte: docs/integracao/V73/pedidos-1610/raiox-pragas-no-tempo-v3.html, commit 529adf7, SHA-256 e7872cb0…805e5e (extrair com git show).
// Conteúdo igual ao do artefato publicado 00b5d915…ed72e, salvo o invólucro de publicação.
// O script lê o arquivo indicado, registra o SHA-256 e a origem, extrai o motor (simulação + camadas 1 a 4)
// e roda num contexto vm isolado (sem require, sem process). Dados 100 % sintéticos. Nenhum dado real, nenhum segredo.
import fs from 'node:fs';
import crypto from 'node:crypto';
import vm from 'node:vm';

const htmlPath = process.argv[2];
const outPath = process.argv[3];
const origem = process.argv[4] || htmlPath;
const nota = process.argv[5] || '';
if (!htmlPath) { console.error('uso: node raiox_repro.mjs <v3.html> [saida.json] [origem] [nota]'); process.exit(2); }
const html = fs.readFileSync(htmlPath, 'utf8');
const sha = crypto.createHash('sha256').update(html).digest('hex');

// ---------- extração do motor ----------
const sIdx = html.lastIndexOf('<script>');
const useStrict = "'use strict';";
const start = html.indexOf(useStrict, sIdx) + useStrict.length;
const end = html.indexOf('// ================= estado =================');
if (sIdx < 0 || start < useStrict.length || end < 0 || end < start) throw new Error('marcadores do motor não encontrados');
let core = html.slice(start, end);
const pick = (re, nome) => { const m = html.match(re); if (!m) throw new Error('não achei ' + nome); return m[0]; };
const LV = pick(/^const LV = .*$/m, 'LV');
const SHOWN = pick(/^const shown = .*$/m, 'shown');
const gIni = html.indexOf('function gabaritoRows(R, a, only) {'), gFim = html.indexOf('\nfunction calcDetails', gIni);
if (gIni < 0 || gFim < 0) throw new Error('não achei gabaritoRows');
const GAB = html.slice(gIni, gFim);
const RXK_OK = core.includes('const RXK = ');

// Ganchos mínimos (1 substituição cada, conferida): semente (réplicas) e deslocamento do clima só na análise (teste nulo).
const swap = (from, to) => { const n = core.split(from).length - 1; if (n !== 1) throw new Error('gancho ambíguo (' + n + '): ' + from.slice(0, 40)); core = core.replace(from, to); };
swap('function rngFor(s) { let h = 2166136261;', 'function rngFor(s) { s = __SALT + s; let h = 2166136261;');
swap("const ctrlCols = r => [Math.log((r.v1 + r.eps) / r.nc), r.stage === 'media' ? 1 : 0, r.stage === 'jovem' ? 1 : 0];",
     "const ctrlCols = r => [Math.log((r.v1 + r.eps) / r.nc), r.stage === 'media' ? 1 : 0, r.stage === 'jovem' ? 1 : 0, ...__EPOCA(r.d2)];");
swap('const climaAt = d => d <= DAYS ? CLIMA[d] : CLIMA_PREV[d - DAYS - 1];',
     'const climaAt = d => { if (__SHIFT && d >= 0 && d <= DAYS) d = (d + __SHIFT) % (DAYS + 1); return d <= DAYS ? CLIMA[d] : CLIMA_PREV[d - DAYS - 1]; };');

// ---------- análises extras (rodam dentro do mesmo escopo do motor) ----------
const EXTRA = String.raw`
const strip = s => s.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
function gabTable(R, a) {
  const pl = PLANTED[a.id] || {}, px = PROXY[a.id] || {};
  return RXF.map(f => { const q = R.M.reps.find(x => x.f.k === f.k), mate = q ? null : R.M.reps.find(x => x.mates.some(m => m.f.k === f.k));
    return { k: f.k, plantado: pl[f.k] || 0, proxy: px[f.k] || null, nivel: q ? q.level : (mate ? 'anda junto de ' + mate.f.k : '-'),
      efeito: q ? Math.round(q.eff * 1000) / 10 : null, ic95: q ? q.effCI.map(v => Math.round(v * 1000) / 10) : null, janela: q ? q.wi : null, limiar: q ? q.t : null,
      nHi: q ? q.nHi : null, talhoes: q ? q.pivHi : null, semanas: q ? q.wkHi : null, qBH: q && q.q != null ? Math.round(q.q * 1000) / 1000 : null }; });
}
function ruidoExibido(R, a) {   // variável sem efeito plantado e que não é proxy: exibida em qualquer nível (forte, moderada, fraca, a confirmar)
  const pl = PLANTED[a.id] || {}, px = PROXY[a.id] || {}; const out = [];
  R.M.reps.forEach(q => { if (!pl[q.f.k] && !px[q.f.k] && shown(q)) out.push(q.f.k + ':' + q.level); }); return out;
}
// Brier em origem móvel: treina com pares que terminam até a origem, testa nos 7 dias seguintes; compara 5 previsores.
function backtest(a) {
  const all = rxRows(a, DAYS).map(r => Object.assign({}, r)); const res = { cortes: [], n: 0, ev: 0, modelo: 0, modeloSemPrevisao: 0, nivelEstadio: 0, persistencia: 0, taxaBase: 0 };
  for (let o = 43; o <= DAYS - 7; o += 7) {
    const tr = all.filter(r => r.d2 <= o).map(r => Object.assign({}, r)), te = all.filter(r => r.d2 > o && r.d2 <= o + 7);
    if (tr.length < 24 || !te.length) continue; const M = rxFit(tr); if (!M) continue;
    const y0 = tr.map(r => r.r), X0 = tr.map(r => designRow(r, [])), b0 = wls(X0, y0);
    const sd0 = Math.sqrt(y0.reduce((s, v, i) => s + (v - dot(X0[i], b0)) ** 2, 0) / Math.max(1, y0.length - X0[0].length)), M0 = { reps: [], beta: b0, sd: sd0 };
    const base = tr.filter(r => r.v2 >= a.nc).length / tr.length;
    te.forEach(r => { const y = r.v2 >= a.nc ? 1 : 0;
      const xs = M.reps.map(q => { const v = fval(r, q.f, q.wi); return v == null ? -Infinity : v; });
      const g = r.d2 - r.d1, rp = Object.assign({}, r, { d1: r.d1 - g, d2: r.d1 });   // "sem previsão": usa as janelas deslocadas para antes da 1ª vistoria
      const xn = M.reps.map(q => { const v = fval(rp, q.f, q.wi); return v == null ? -Infinity : v; });
      res.modelo += (predictRow(M, r, xs).p - y) ** 2; res.modeloSemPrevisao += (predictRow(M, r, xn).p - y) ** 2;
      res.nivelEstadio += (predictRow(M0, r, []).p - y) ** 2; res.persistencia += ((r.v1 >= a.nc ? 1 : 0) - y) ** 2; res.taxaBase += (base - y) ** 2;
      res.n++; res.ev += y; });
    res.cortes.push(o);
  }
  ['modelo', 'modeloSemPrevisao', 'nivelEstadio', 'persistencia', 'taxaBase'].forEach(k => { res[k] = res.n ? Math.round(res[k] / res.n * 1000) / 1000 : null; });
  return res;
}
function residuoNaJanela(a) {   // pares aceitos como "sem controle" mas com resíduo de aplicação ainda ativo na simulação
  let n = 0, tot = 0; PIVOS.forEach(p => { const s = PEST[a.id][p.id]; if (!s) return; });
  rxRows(a, DAYS).forEach(r => { tot++; const s = PEST[a.id][r.pid];
    if (s.apps.some(ap => ap.day <= r.d1 && ap.day + Math.round(ap.prod.res * (0.7 + 0.3 * EQ[ap.eq].cov)) > r.d1)) n++; });
  return { pares: tot, comResiduo: n };
}
function controle(a) {
  const H = rxHT(a, DAYS), E = g => g && g.E != null ? Math.round(g.E * 1000) / 10 : null, ci = g => g && g.ci ? g.ci.map(v => Math.round(v * 1000) / 10) : null;
  const cmp = (fn, k1, k2) => { const g = htGroups(H, fn, null, 'c' + k1 + DAYS), x = g.find(z => z.k === k1), y = g.find(z => z.k === k2);
    return { com: { n: x ? x.nValid : 0, E: E(x), ic90: ci(x) }, sem: { n: y ? y.nValid : 0, E: E(y), ic90: ci(y) } }; };
  const semControle = H.filter(h => h.E == null).length;
  let reaplicaAntes = 0; PIVOS.forEach(p => { const s = PEST[a.id][p.id]; if (!s) return; s.apps.forEach((ap, i) => { const nx = s.apps[i + 1]; if (nx && (ap.backDay == null || nx.day < ap.backDay)) reaplicaAntes++; }); });
  const per = PIVOS.filter(p => PEST[a.id][p.id]).map(p => { const s = PEST[a.id][p.id], ob = s.obs.filter(o => o.day <= DAYS); return { n: s.apps.filter(x => x.day <= DAYS).length, v: ob.length ? ob.reduce((t, o) => t + o.v, 0) / ob.length : 0 }; });
  const mesmoDia = H.filter(h => h.ap.before && h.ap.before.day === h.ap.day).length;
  let voltaSemFicarAbaixo = 0, voltaAntesDe5d = 0, voltas = 0;
  PIVOS.forEach(p => { const s = PEST[a.id][p.id]; if (!s) return; s.apps.forEach(ap => { if (ap.backDay == null || ap.backDay > DAYS) return; voltas++;
    const pos = s.obs.filter(o => o.day > ap.day && o.day <= ap.backDay); if (!pos.some(o => o.v < a.nc)) voltaSemFicarAbaixo++; if (ap.backDay - ap.day < 5) voltaAntesDe5d++; }); });
  return { aplicacoesComAntesDepois: H.length, semControleValido: semControle, antesNoMesmoDia: mesmoDia, voltasAoNC: voltas, voltaSemNuncaFicarAbaixo: voltaSemFicarAbaixo, voltaContadaAntesDe5Dias: voltaAntesDe5d,
    diaQuenteSeco: cmp(h => h.ap.qsDia ? 'qs' : 'ok', 'qs', 'ok'), chuvaAte1Dia: cmp(h => h.ap.chuvaDepois ? 'ch' : 'ok', 'ch', 'ok'),
    barra100: cmp(h => h.ap.eq === 'b100' ? 'b' : 'at', 'b', 'at'), mesmoGrupoSeguido: cmp(h => h.ap.consec >= 1 ? 'seq' : 'rot', 'seq', 'rot'),
    reaplicacaoAntesDeVoltarAoNC: reaplicaAntes, armadilhaAplicacoesXNivel: Math.round(spear(per.map(z => z.n), per.map(z => z.v)) * 100) / 100 };
}
function hitFM(R, a) {   // critério estrito: efeito plantado achado com nível Forte ou Moderada e sinal certo (direto ou pelo grupo que anda junto)
  const pl = PLANTED[a.id] || {}; let h = 0;
  Object.entries(pl).forEach(([k, sg]) => { const q = R.M.reps.find(x => x.f.k === k);
    if (q) { if (['forte', 'moderada'].includes(q.level) && Math.sign(q.beta) === sg) h++; return; }
    const mate = R.M.reps.find(x => x.mates.some(m => m.f.k === k)); if (!mate) return; const m = mate.mates.find(z => z.f.k === k), c = spear(mate.xv, m.x);
    if (['forte', 'moderada'].includes(mate.level) && Math.sign(mate.beta) * Math.sign(c || 1) === sg) h++; });
  return h;
}
function rodar(full) {
  const out = {};
  ALVOS.forEach(a => { const t0 = __now(); const R = rxGet(a.id, DAYS); const ms = __now() - t0;
    if (R.cold) { out[a.id] = { frio: true }; return; }
    const g = gabaritoRows(R, a); const o = { hit: g.hit, tot: g.tot, fp: g.fp, ruido: g.noise, ruidoExibido: ruidoExibido(R, a),
      aConfirmar: R.M.reps.filter(q => q.level === 'confirmar').map(q => q.f.k), gate: R.risk ? R.risk.gate : null, msRxGet: Math.round(ms * 10) / 10,
      pares: R.n, talhoes: R.piv, semanas: R.wks, hitFM: hitFM(R, a),
      exibidos: R.M.reps.filter(shown).map(q => q.f.k + (q.beta > 0 ? '+' : '-') + ':' + q.level + ((PLANTED[a.id] || {})[q.f.k] ? '[plantado]' : (PROXY[a.id] || {})[q.f.k] ? '[proxy]' : '[ruído]')),
      backtest: backtest(a) };
    if (full) { o.tabela = gabTable(R, a); o.residuo = residuoNaJanela(a); o.controle = controle(a); }
    out[a.id] = o; });
  return out;
}
globalThis.__result = rodar(__FULL);
`;

// Controle de época na regressão: 'nenhum' (como o v3), 'mes' (mês da vistoria, indicadores) ou 'suave' (tendência quadrática na data).
const EPOCA = { nenhum: () => [], mes: d => { const m = d <= 30 ? 0 : d <= 61 ? 1 : 2; return [m === 1 ? 1 : 0, m === 2 ? 1 : 0]; }, suave: d => { const t = d / 86; return [t, t * t]; } };
function run(salt, shift, full, epoca = 'nenhum') {
  const ctx = vm.createContext({ __SALT: salt, __SHIFT: shift, __FULL: full, __EPOCA: EPOCA[epoca], __now: () => performance.now(), Intl, Math, Date, JSON, Map, Set, Object, Array, Number, String, Infinity, NaN, console });
  const src = '(() => {\n"use strict";\n' + core + '\n' + LV + '\n' + SHOWN + '\n' + GAB + '\n' + EXTRA + '\n})();';
  vm.runInContext(src, ctx, { timeout: 120000 });
  return ctx.__result;
}

const t0 = performance.now();
const resultado = { artefato: { origem, nota, arquivo: htmlPath.split('/').pop(), bytes: Buffer.byteLength(html), sha256: sha, rxkPresente: RXK_OK }, node: process.version, quando: new Date().toISOString() };
// 1) Reprodução do número declarado (semente original, 25/09 = dia 86)
resultado.original = run('', 0, true);
// 2) Réplicas: mesma estrutura de fazenda, ruído com outra semente (chuva e ondas de calor ficam fixas no gerador)
resultado.replicas = {};
for (let i = 1; i <= 20; i++) { const s = 'r' + String(i).padStart(2, '0') + ':'; resultado.replicas[s] = run(s, 0, false); }
// 3) Nulo para o clima: série do clima deslocada no tempo só na análise (a simulação usa o clima verdadeiro)
resultado.nuloClima = {};
for (const sh of [21, 35, 49, 63]) resultado.nuloClima['desloca' + sh] = run('', sh, false);
resultado.nuloClimaSuave = {};
for (const sh of [21, 35, 49, 63]) resultado.nuloClimaSuave['desloca' + sh] = run('', sh, false, 'suave');
// 4) Lição "época × clima" com 1 safra: mesma análise com o mês ou uma tendência suave como controle
resultado.epoca = { mes: {}, suave: {} };
for (const ep of ['mes', 'suave']) for (let i = 0; i <= 20; i++) { const s = i ? 'r' + String(i).padStart(2, '0') + ':' : ''; resultado.epoca[ep][s || 'original'] = run(s, 0, false, ep); }
resultado.segundos = Math.round((performance.now() - t0) / 100) / 10;
const txt = JSON.stringify(resultado, null, 1);
if (outPath) fs.writeFileSync(outPath, txt + '\n');
console.log(txt);
