// SAF-C01 · desempenho de ocChecar / ocTabela / ocPlantioMin (process.hrtime.bigint, mediana de 50 execuções depois de 5 de aquecimento).
// Cada fonte roda num contexto vm próprio, no mesmo processo, sobre a mesma fixture (desempenho_fixture.json, dado sintético).
// Uso: node desempenho.js <fixture.json> rotulo=caminho/ocupacao.js [rotulo2=outro.js ...]
// Correções da verificação (09/10/2026): + histórico longo com ocPlantioMin sem janela (achado de desempenho do verificador 3).
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
  // histórico longo (verificador 3): talhão X 500 ha, café 1996 100 ha + k safras com 3 ocupações cada; soja nova 410 ha na 2027/28 (sempre trava, sem
  // janela): o ocPlantioMin percorre a safra inteira. Mediana de 3 (o caso de 91 ocupações leva ~15 s por chamada na rodada anterior)
  const hist = {};
  for (const anos of [0, 3, 7, 15, 30]) {
    const S2 = { H96: { id: 'H96', nome: 'Café 1996', ini: '1996-01-01', fim: '1996-12-31', faz: 'FH', ro: true }, H2728: { id: 'H2728', nome: 'Safra 2027/28', ini: '2027-09-01', fim: '2028-08-31', faz: 'FH', ro: false } };
    const x = [{ id: 'hcafe', saf: 'H96', faz: 'FH', faixa: 'X-A', tipo: 'Parcela', talhao: 'X', area: 100, cult: 'Café', var: 'Catuaí 144', plantio: '1996-01-01' }];
    for (let a = 2027 - anos; a <= 2026; a++) { const sid = 'H' + a; S2[sid] = { id: sid, nome: 'Safra ' + a, ini: a + '-09-01', fim: (a + 1) + '-08-31', faz: 'FH', ro: true };
      x.push({ id: 'hs' + a, saf: sid, faz: 'FH', faixa: 'X-B', tipo: 'Parcela', talhao: 'X', area: 200, cult: 'Soja', var: '58 W', plantio: a + '-10-01', plano: 'SOJA-AT' });
      x.push({ id: 'hm' + a, saf: sid, faz: 'FH', faixa: 'X-B', tipo: 'Parcela', talhao: 'X', area: 200, cult: 'Milho', var: 'Híbrido AG 8700', plantio: (a + 1) + '-03-01', plano: 'MILHO-SF' });
      x.push({ id: 'hf' + a, saf: sid, faz: 'FH', faixa: 'X-C', tipo: 'Parcela', talhao: 'X', area: 150, cult: 'Feijão', var: 'Pérola', plantio: (a + 1) + '-05-10' }); }
    const exc = { id: 'hnovo', saf: 'H2728', faz: 'FH', faixa: 'X-D', tipo: 'Parcela', talhao: 'X', area: 410, cult: 'Soja', var: '58 W', plantio: '2027-10-01', plano: 'SOJA-AT' };
    const lim = Object.assign({}, exc, { area: 400 });
    const chk = X.ocChecar(ctx, S2, x, x.concat([exc]), 'H2728', 'hnovo', 500); const pm = [];
    const t = []; for (let i = 0; i < 3; i++) { const a0 = process.hrtime.bigint(); pm.push(X.ocPlantioMin(ctx, S2, x, 'H2728', exc, X.ocDia('2027-09-01'), 500, null)); t.push(Number(process.hrtime.bigint() - a0) / 1e6); }
    t.sort((p, q) => p - q);
    hist['k=' + anos + ' (' + x.length + ' ocupações)'] = { trava_410: chk.trav.map(z => z[0]).join(','), plantioMin_410: pm[0], plantioMin_ms_mediana3: +t[1].toFixed(1),
      plantioMin_400_limite: X.ocPlantioMin(ctx, S2, x, 'H2728', lim, X.ocDia('2027-09-01'), 500, null), ocChecar_410: mede(() => X.ocChecar(ctx, S2, x, x.concat([exc]), 'H2728', 'hnovo', 500)) };
  }
  out.fontes[rot].historico_longo = hist;
}
console.log(JSON.stringify(out, null, 2));
