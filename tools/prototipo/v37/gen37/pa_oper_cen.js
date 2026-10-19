// PA-OPER F1 · P4, P19 e propriedade sobre cenPreparoOrdem (EX-38). Rodado por pa_oper_cen_test.py depois do js_prefixo.
const R = []; const ok = (id, desc, c, info) => { R.push(!!c); console.log((c ? 'OK    ' : 'FALHA ') + id + ' · ' + desc + (c ? '' : ' · ' + JSON.stringify(info === undefined ? '' : info).slice(0, 400))); };
const clone = x => JSON.parse(JSON.stringify(x)), perto = (a, b) => Math.abs(a - b) < 1e-9 * Math.max(1, Math.abs(b));
const c0 = clone(CEN0), o0 = c0.ordens['OS-0421'];
let p = cenPreparoOrdem(c0, o0);
ok('P4a', 'OS-0421 (plano v6, 100 L/ha, PJ 3.000 L): 6 cargas, 5 de 30 ha + 1 de 10 ha, 15 L e 5 L de Fungicida A, 16.000 L de calda',
  p.ok && p.n === 6 && p.cargas.slice(0, 5).every(x => perto(x.area, 30) && x.prods[0].q === 15) && perto(p.cargas[5].area, 10) && p.cargas[5].prods[0].q === 5
  && perto(p.cargas.reduce((s, x) => s + x.vol, 0), 16000) && p.cargas.reduce((s, x) => s + x.prods[0].q, 0) === 80, p.cargas && p.cargas.map(x => [x.area, x.prods[0].q]));
ok('P4b', 'a instrução traz o retrato do tanque (3.000 L) e a versão do plano', o0.instrucao.tanque === 3000 && o0.instrucao.plano === 'SOJA-AT' && o0.instrucao.planoVer === 6, o0.instrucao);
// P19: o cadastro muda para 2.500 L depois da emissão; a O.S. emitida segue com o retrato
const velho = CEN_PREP_ATIVOS.a05.tanque; CEN_PREP_ATIVOS.a05.tanque = 2500;
try {
  p = cenPreparoOrdem(c0, o0);
  ok('P19a', 'tanque do cadastro mudado para 2.500 L: a OS-0421 emitida continua com 6 cargas de 3.000 L', p.ok && p.n === 6 && p.tanque === 3000, [p.n, p.tanque]);
  const c1 = clone(c0), o1 = c1.ordens['OS-0421']; o1.instrucao.tanque = 2500;     // "Trocar conjunto" / O.S. emitida depois: retrato novo
  p = cenPreparoOrdem(c1, o1);
  ok('P4c', 'retrato de 2.500 L: 7 cargas, 6 de 25 ha + 1 de 10 ha, 12,5 L e 5 L',
    p.ok && p.n === 7 && p.cargas.slice(0, 6).every(x => perto(x.area, 25) && x.prods[0].q === 12.5) && perto(p.cargas[6].area, 10) && p.cargas[6].prods[0].q === 5, p.cargas && p.cargas.map(x => [x.area, x.prods[0].q]));
  const c2 = clone(c0), o2 = c2.ordens['OS-0421']; delete o2.instrucao.tanque;   // O.S. antiga, sem retrato: vale o cadastro
  p = cenPreparoOrdem(c2, o2);
  ok('P19b', 'sem retrato (O.S. de antes da F1), o tanque vem do cadastro (2.500 L)', p.ok && p.tanque === 2500 && p.n === 7, [p.tanque, p.n]);
} finally { CEN_PREP_ATIVOS.a05.tanque = velho; }
// 41.5: 12 ha, 100 L/ha, tanque de 500 L, 2 L/ha → 500 + 500 + 200 L; 5 + 5 + 2 ha; 10 + 10 + 4 L (total 24 L)
{ const c = clone(c0), o = c.ordens['OS-0421']; o.saldo = 12; o.ap = []; o.ins = [{p: 'P', dose: 2, un: 'L'}]; o.instrucao.tanque = 500;
  p = cenPreparoOrdem(c, o);
  ok('P4d', 'exemplo do 41.5: 500 + 500 + 200 L, 5 + 5 + 2 ha, 10 + 10 + 4 L (a última não é cheia)',
    p.ok && p.cargas.map(x => x.vol).join() === '500,500,200' && p.cargas.map(x => x.area).join() === '5,5,2' && p.cargas.map(x => x.prods[0].q).join() === '10,10,4', p.cargas); }
// Propriedade: 1.000 casos com semente fixa, retrato variando; Σ calda = área × volume, nenhuma carga passa do tanque nem fica vazia,
// Σ produto = dose × área na regra de quantidade da EX-38 (cenQtd, centésimos)
{ let s = 20261019; const rnd = () => (s = (1103515245 * s + 12345) % 2147483648) / 2147483648; let falhas = 0, ex = null;
  for (let i = 0; i < 1000; i++) {
    const c = clone(c0), o = c.ordens['OS-0421']; o.ap = [];
    o.saldo = Math.round((0.5 + rnd() * 400) * 100) / 100; o.instrucao.vazao = [50, 80, 100, 120, 150, 200][Math.floor(rnd() * 6)];
    o.instrucao.tanque = [500, 600, 2000, 2500, 3000][Math.floor(rnd() * 5)]; const dose = Math.max(0.01, Math.round(rnd() * 300) / 100);
    o.ins = [{p: 'A', dose, un: 'L'}];
    const q = cenPreparoOrdem(c, o);
    const vol = q.cargas.reduce((a, x) => a + x.vol, 0), prod = q.cargas.reduce((a, x) => a + x.prods[0].q, 0);
    if (!q.ok || Math.abs(vol - o.saldo * o.instrucao.vazao) > 1e-6 || q.cargas.some(x => x.vol > o.instrucao.tanque + 1e-7 || !(x.area > 0))
        || Math.abs(prod - cenQtd(dose, o.saldo)) > 0.005 * q.n + 1e-9) { falhas++; ex = ex || {saldo: o.saldo, vaz: o.instrucao.vazao, tq: o.instrucao.tanque, dose, vol, prod}; }
  }
  ok('PROP', '1.000 casos: Σ calda = área × volume; nenhuma carga passa do tanque nem fica vazia; Σ produto = dose × área (centésimos)', falhas === 0, ex); }
const n = R.filter(Boolean).length; console.log(`\n${n}/${R.length} OK`); process.exitCode = n === R.length ? 0 : 1;
