// SAF-C01 · desempenho de ocChecar / ocTabela / ocPlantioMin (process.hrtime.bigint, mediana de 50 execuções depois de 5 de aquecimento).
// Cada fonte roda num contexto vm próprio, no mesmo processo, sobre a mesma fixture (desempenho_fixture.json, dado sintético).
// Uso: node desempenho.js <fixture.json> rotulo=caminho/ocupacao.js [rotulo2=outro.js ...]
const fs = require('node:fs'), vm = require('node:vm'), crypto = require('node:crypto');
const F = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const N = 50, AQ = 5;
function carrega(src) {
  const code = fs.readFileSync(src, 'utf8'); const sb = {}; vm.createContext(sb);
  vm.runInContext(code + '\n;globalThis.X={ocCtx,ocOcupacoes,ocTabela,ocChecar,ocPlantioMin,ocDia};', sb);
  return { X: sb.X, sha: crypto.createHash('sha256').update(code).digest('hex') };
}
function mede(fn) {
  for (let i = 0; i < AQ; i++) fn();
  const t = [];
  for (let i = 0; i < N; i++) { const a = process.hrtime.bigint(); fn(); t.push(Number(process.hrtime.bigint() - a) / 1e6); }
  t.sort((p, q) => p - q);
  return { mediana_ms: +(((t[N / 2 - 1] + t[N / 2]) / 2).toFixed(4)), min_ms: +t[0].toFixed(4), max_ms: +t[N - 1].toFixed(4), n: N };
}
const out = { node: process.version, execucoes: N, aquecimento: AQ, fontes: {} };
for (const arg of process.argv.slice(3)) {
  const [rot, src] = arg.split('='); const { X, sha } = carrega(src);
  const ctx = X.ocCtx(F.ctx.culturas, F.ctx.cultivares, F.ctx.planos, F.ctx.folga);
  const S = F.safras, CU = F.cults, TAL = F.talhoes, E = F.extremo;
  const SX = Object.assign({}, S); const CX = E.cults;
  const lg01 = CU.find(c => c.id === 'lg01'); const Tlg = TAL['Lagoa Grande'].find(x => x[0] === lg01.talhao)[1];
  const tab = (sid, cults, tal) => () => X.ocTabela(ctx, S[sid] || SX[sid], X.ocOcupacoes(ctx, SX, cults), tal, SX);
  const r = {};
  r['LG ocTabela LG2627 (23 pivôs)'] = mede(tab('LG2627', CU, TAL['Lagoa Grande']));
  r['LG ocTabela Nova Lagoa 2027/28'] = mede(tab('NLG28', CU, TAL['Lagoa Grande']));
  r['LG ocChecar lg01 (editar, Pivô 1)'] = mede(() => X.ocChecar(ctx, S, CU, CU, 'LG2627', 'lg01', Tlg));
  r['SR ocTabela S27SF'] = mede(tab('S27SF', CU, TAL['Santa Rita']));
  r['SR ocChecar T1-B 152 ha 21/02/2027'] = mede(() => X.ocChecar(ctx, S, CU, CU.concat([F.sr_novo]), 'S27SF', 'nv', 312));
  r['SR ocPlantioMin T1-B desde 21/02/2027'] = mede(() => X.ocPlantioMin(ctx, S, CU, 'S27SF', F.sr_novo, X.ocDia('2027-02-21'), 312, null));
  r['EXT ocChecar soja X1-C 400 ha (perene 1996 + 20)'] = mede(() => X.ocChecar(ctx, SX, CX, CX.concat([E.novo]), 'FX2728', 'xnovo', 500));
  r['EXT ocTabela 2027/28 (perene 1996 + 20)'] = mede(tab('FX2728', CX.concat([E.novo]), E.talhoes));
  const ex = X.ocChecar(ctx, SX, CX, CX.concat([E.excesso]), 'FX2728', 'xnovo', 500);
  const ok = X.ocChecar(ctx, SX, CX, CX.concat([E.novo]), 'FX2728', 'xnovo', 500);
  out.fontes[rot] = { fonte: src, sha256: sha, medidas: r,
    conferencia: { 'EXT X1-C 410 ha (soma 510 > 500) trava': ex.trav.map(x => x.slice(0, 1).concat(x.slice(3))), 'EXT X1-C 400 ha (soma 500, limite) trava': ok.trav } };
}
console.log(JSON.stringify(out, null, 2));
