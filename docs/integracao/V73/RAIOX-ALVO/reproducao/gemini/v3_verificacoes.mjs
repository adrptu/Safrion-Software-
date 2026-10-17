// Verificações no motor do v3 que sustentam a revisão da consolidação Gemini (bff2e0e) e o contrato RX-0 proposto.
// Uso: node v3_verificacoes.mjs <v3.html> <saída.json>
// Fonte: docs/integracao/V73/pedidos-1610/raiox-pragas-no-tempo-v3.html, commit 529adf7, SHA-256 e7872cb0…805e5e (extrair com git show).
// Mesmo método de ../confronto/confronto.mjs: extrai o motor (do 'use strict' do último <script> até "// ===== estado =====")
// e roda num contexto vm isolado, sem require e sem process. Um só gancho (semente das réplicas, igual ao G1 do confronto).
// Blocos: V1 rxHT do v3 nos casos de zero da Q2; V2 fatos do gerador (zeros, intervalos entre vistorias, gatilho das aplicações);
//         V3 contraprova dedicada do N5 (avaliador da leitura futura no teste da previsão). Dados 100 % sintéticos.
import fs from 'node:fs';
import crypto from 'node:crypto';
import vm from 'node:vm';

const htmlPath = process.argv[2], outPath = process.argv[3];
if (!htmlPath || !outPath) { console.error('uso: node v3_verificacoes.mjs <v3.html> <saida.json>'); process.exit(2); }
const html = fs.readFileSync(htmlPath, 'utf8');
const sha = crypto.createHash('sha256').update(html).digest('hex');
const sIdx = html.lastIndexOf('<script>'), US = "'use strict';", start = html.indexOf(US, sIdx) + US.length, end = html.indexOf('// ================= estado =================');
if (sIdx < 0 || start < US.length || end < start) throw new Error('marcadores do motor não encontrados');
let CORE = html.slice(start, end);
const de = 'function rngFor(s) { let h = 2166136261;', para = 'function rngFor(s) { s = __SALT + s; let h = 2166136261;';
if (CORE.split(de).length !== 2) throw new Error('gancho da semente ambíguo ou ausente');
CORE = CORE.replace(de, para);

const EXTRA = String.raw`
const r4 = v => v == null || !isFinite(v) ? (v == null ? null : String(v)) : Math.round(v * 1e4) / 1e4;
const limpa = () => { WCACHE.clear(); RXC.clear(); };

// ---------- V1 · rxHT do v3 nos casos de zero da Q2 (fixture de 3 talhões, NC 10, ε = 0,5) ----------
function v1Q2() {
  const savedP = PIVOS.slice(), a = { id: 'teste', nc: 10 };
  const roda = (Ta0, Ta1, Ca0, Ca1) => { PIVOS.splice(0, PIVOS.length, { id: 'T', stage: 'adulta' }, { id: 'C1', stage: 'adulta' }, { id: 'C2', stage: 'adulta' });
    PEST.teste = { T: { obs: [], apps: [{ day: 2, before: { day: 1, v: Ta0 }, after: { day: 10, v: Ta1 }, backDay: null, red: null }] } };
    ['C1', 'C2'].forEach(id => { PEST.teste[id] = { obs: [{ day: 1, v: Ca0 }, { day: 10, v: Ca1 }], apps: [] }; });
    const h = rxHT(a, 10)[0]; return { entrada: 'T ' + Ta0 + ' → ' + Ta1 + '; C ' + Ca0 + ' → ' + Ca1, E: r4(h.E), nCtrl: h.nCtrl }; };
  const r = { controleZeradoAntes: roda(10, 5, 0, 10), tratadoZeradoAntes: roda(0, 2, 10, 10), controleZeradoDepois: roda(10, 5, 10, 0),
    tratadoZeradoDepois: roda(10, 0, 10, 10), controleZeradoAntesEDepois: roda(10, 5, 0, 0), controleNoPiso10pctNC: roda(10, 50, 1, 10), regular: roda(10, 5, 10, 10) };
  PIVOS.splice(0, PIVOS.length, ...savedP); delete PEST.teste; return r;
}

// ---------- V2 · fatos do gerador ----------
function v2Gerador() {
  let leituras = 0, zeros = 0, minV = Infinity; const gaps = {}; let apps = 0, semGatilho = 0, gatilhoAcimaNC = 0, gatilhoAbaixoNC = 0;
  ALVOS.forEach(a => PIVOS.forEach(p => { const s = PEST[a.id][p.id]; if (!s) return; const pf = PROF[p.id];
    s.obs.forEach((o, i) => { leituras++; if (o.v === 0) zeros++; minV = Math.min(minV, o.v); if (i) { const g = o.day - s.obs[i - 1].day; gaps[g] = (gaps[g] || 0) + 1; } });
    s.apps.forEach(ap => { apps++; const prev = s.obs.filter(o => o.day < ap.day && o.v >= a.nc * pf.gatilho).pop();
      if (!prev) semGatilho++; else if (prev.v >= a.nc) gatilhoAcimaNC++; else gatilhoAbaixoNC++; }); }));
  return { leituras, leiturasZero: zeros, menorLeitura: r4(minV), intervaloEntreVistorias_dias: gaps, aplicacoes: apps, aplicacoesSemLeituraGatilhoAntes: semGatilho,
    gatilhoComLeituraMaiorOuIgualNC: gatilhoAcimaNC, gatilhoComLeituraEntre90pctNCeNC: gatilhoAbaixoNC };
}

// ---------- V3 · N5: avaliador da 2ª leitura (futura na origem) entra no teste da previsão ----------
const nv = v => v == null ? -Infinity : v;
function gate(a, D, R, feat) {   // réplica do gate do rxRisk (ART:660-663), como ../confronto/confronto.mjs gateCom
  const cut = D - 21, tr = R.rows.filter(r => r.d2 <= cut), te = R.rows.filter(r => r.d2 > cut);
  if (!(tr.length >= 24 && te.length >= 10)) return null; const Mt = rxFit(tr.map(r => Object.assign({}, r))); if (!Mt) return null;
  let bm = 0, bp = 0; te.forEach(r => { const xs = feat(Mt, r), y = r.v2 >= a.nc ? 1 : 0; bm += (predictRow(Mt, r, xs).p - y) ** 2; bp += ((r.v1 >= a.nc ? 1 : 0) - y) ** 2; });
  const qa = Mt.reps.find(q => q.f.k === 'aval');
  return { ok: bm < bp, bm: r4(bm / te.length), bp: r4(bp / te.length), n: te.length, avalNoModelo: !!qa, betaAval: qa ? r4(qa.beta) : null, te };
}
function v3N5(D) {
  const out = {};
  ALVOS.forEach(a => { limpa(); const R = rxGet(a.id, D); if (R.cold || !R.risk) { out[a.id] = { frio: true }; return; }
    const featV3 = (Mt, r) => Mt.reps.map(q => nv(fval(r, q.f, q.wi)));
    const avOrigem = r => PEST[a.id][r.pid].obs.find(z => z.day === r.d1).aval;
    const featN5 = (Mt, r) => Mt.reps.map(q => q.f.k === 'aval' ? (avOrigem(r) === 'B' ? 1 : 0) : nv(fval(r, q.f, q.wi)));
    const g0 = gate(a, D, R, featV3); if (!g0) { out[a.id] = { semGate: true }; return; }
    if (g0.bm !== r4(R.risk.gate.bm) || g0.bp !== r4(R.risk.gate.bp)) throw new Error('réplica do gate diverge do v3 em ' + a.id);
    const g1 = gate(a, D, R, featN5);
    out[a.id] = { nTeste: g0.n, avalNoModelo: g0.avalNoModelo, betaAval: g0.betaAval, linhasComAvaliadorDaOrigemDiferente: g0.te.filter(r => avOrigem(r) !== r.aval).length,
      v3_avaliadorDa2aLeitura: { ok: g0.ok, brierModelo: g0.bm, brierPersistencia: g0.bp }, avaliadorConhecidoNaOrigem: { ok: g1.ok, brierModelo: g1.bm } }; });
  return out;
}
globalThis.__result = (() => { const r = { v2: v2Gerador(), v3: v3N5(DAYS) }; if (__MODO === 'completo') r.v1 = v1Q2(); return r; })();
`;

function rodar(salt, modo) {
  const ctx = vm.createContext({ __SALT: salt, __MODO: modo, Intl, Math, Date, JSON, Map, Set, Object, Array, Number, String, Infinity, NaN, isFinite, Error, console });
  vm.runInContext('(() => {\n"use strict";\n' + CORE + '\n' + EXTRA + '\n})();', ctx, { timeout: 600000 });
  return JSON.parse(JSON.stringify(ctx.__result));
}
const t0 = performance.now();
const res = { artefato: { arquivo: htmlPath.split('/').pop(), bytes: Buffer.byteLength(html), sha256: sha }, node: process.version, original: rodar('', 'completo'), replicas: {} };
for (let i = 1; i <= 20; i++) { const s = 'r' + String(i).padStart(2, '0') + ':'; res.replicas[s] = rodar(s, 'basico'); }
fs.writeFileSync(outPath, JSON.stringify(res, null, 1) + '\n');
console.error('ok · ' + Math.round((performance.now() - t0) / 100) / 10 + ' s');
