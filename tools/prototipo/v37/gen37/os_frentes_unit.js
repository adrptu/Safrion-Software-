// EX-54 · regras das frentes de trabalho (os_frentes.js), sem navegador. Uso: node os_frentes_unit.js
const assert = require('assert'), path = require('path');
// a regra única de quantidade (cenQtd) vem do cenario.js real, como na página
{ const src = require('fs').readFileSync(path.join(__dirname, 'cenario.js'), 'utf8'), pega = n => { const i = src.indexOf('function ' + n + '('); let d = 0, j = src.indexOf('{', i);
    for (; j < src.length; j++) { if (src[j] === '{') d++; else if (src[j] === '}' && --d === 0) break; } return src.slice(i, j + 1); };
  (0, eval)(pega('cenDec') + '\n' + pega('cenQtd') + '\nglobalThis.cenQtd = cenQtd;'); }
const F = require(path.join(__dirname, 'os_frentes.js'));
let n = 0; const ok = (nome, fn) => { fn(); n++; console.log('PASS', nome); };
const ABA = [{ p: 'Abamectina 18 EC', dose: 0.5, un: 'L' }, { p: 'Óleo mineral', dose: 1, un: 'L' }];
const base = (id, o) => Object.assign({ id, faz: 'Lagoa Grande', saf: '2026/27', cultura: 'Mamão Formosa', fam: 'Pulverização', atv: 'Controle de ácaro',
  talhao: id, tkey: id, area: 10, ins: ABA, liquido: true, vazao: 100, tanque: 2000, rend: null, ini: '2026-10-12', fim: '2026-10-14', liberada: true, bloq: '' }, o || {});
// centros em lon/lat: A–B–C–D numa linha leste-oeste, E ao sul
const geo = { tipo: 'lonlat', c: { A: [-47.150, -34.629], B: [-47.136, -34.629], C: [-47.122, -34.629], D: [-47.164, -34.629], E: [-47.136, -34.641] } };
const cosLaw = (p, q) => { const r = x => x * Math.PI / 180; return 6371008.8 * Math.acos(Math.min(1, Math.sin(r(p[1])) * Math.sin(r(q[1])) + Math.cos(r(p[1])) * Math.cos(r(q[1])) * Math.cos(r(q[0] - p[0])))); };

ok('U1 calda: outra ordem e 1.000 mL/ha = 1 L/ha são a mesma; kg ≠ L', () => {
  const a = { ins: [{ p: 'X', dose: 1, un: 'L' }, { p: 'Y', dose: 2, un: 'kg' }] }, b = { ins: [{ p: 'Y', dose: 2000, un: 'g' }, { p: 'X', dose: 1000, un: 'mL' }] };
  assert.equal(F.frCalda(a), F.frCalda(b)); assert.notEqual(F.frCalda({ ins: [{ p: 'X', dose: 1, un: 'L' }] }), F.frCalda({ ins: [{ p: 'X', dose: 1, un: 'kg' }] }));
});
ok('U2 mesmo produto com outra dose entra na mesma frente como nova calda, com a troca escrita', () => {
  const r = F.osFrentes([base('A'), base('B'), base('C', { ins: [{ p: 'Abamectina 18 EC', dose: 0.6, un: 'L' }, { p: 'Óleo mineral', dose: 1, un: 'L' }] })], geo);
  assert.equal(r.frentes.length, 1); const f = r.frentes[0]; assert.equal(f.caldas, 2); assert.equal(f.trocas.length, 1); assert.match(f.trocas[0].t, /^Troca de calda antes de [ABC]: Abamectina 18 EC 0,[56] L\/ha/);
  assert.equal(Math.abs(f.ids.indexOf('A') - f.ids.indexOf('B')), 1);   // mesma calda junta: A e B seguidas, a troca só uma vez
});
ok('U3 adjuvante diferente não separa (OS-0421 × OS-0424): mesma frente com troca de calda', () => {
  const r = F.osFrentes([base('A', { ins: [{ p: 'Fungicida A', dose: 0.5, un: 'L' }, { p: 'Adjuvante espalhante', dose: 0.25, un: 'L' }] }), base('B', { ins: [{ p: 'Fungicida A', dose: 0.5, un: 'L' }] })], geo);
  assert.equal(r.frentes.length, 1); assert.equal(r.frentes[0].caldas, 2); assert.equal(r.frentes[0].compat, 'Fungicida A');
});
ok('U4 herbicida sempre por último, mesmo com a janela que fecha antes, e a frente fecha com tríplice lavagem', () => {
  const G = [{ p: 'Glifosato 480', dose: 3, un: 'L' }, { p: 'Óleo mineral', dose: 0.5, un: 'L' }];
  const s = F.frOrdem([base('H', { ins: G, fim: '2026-10-12', herb: true, calda: 'g' }), base('A', { calda: 'a' }), base('B', { calda: 'a' })], geo);
  assert.deepEqual(s.map(x => x.id).slice(-1), ['H']);
  const t = F.frTrocas(s); assert.match(t[t.length - 1].t, /tríplice lavagem/);
  assert.equal(F.frHerb(base('X', { ins: G })), true); assert.equal(F.frHerb(base('X')), false);
});
ok('U5 período: janelas que se cruzam ou se seguem ficam juntas; a que começa depois de todas abre outra', () => {
  const r = F.osFrentes([base('A'), base('B', { ini: '2026-10-14', fim: '2026-10-16' }), base('C', { ini: '2026-10-20', fim: '2026-10-21' })], geo);
  assert.equal(r.frentes.length, 1); assert.deepEqual(r.frentes[0].ids.slice().sort(), ['A', 'B']); assert.deepEqual(r.frentes[0].janela, { ini: '2026-10-12', fim: '2026-10-16' });
  assert.equal(r.soltas[0].id, 'C'); assert.match(r.soltas[0].motivo, /Janela sem encontro/);
});
ok('U6 ordem: a janela que fecha antes; no empate, segue a mesma calda e depois o mais perto', () => {
  // C fecha antes; depois empatam A, B, D: B tem outra calda; das de mesma calda (A, D) a mais perto de C é A
  const B2 = { ins: [{ p: 'Abamectina 18 EC', dose: 0.6, un: 'L' }] };
  const r = F.osFrentes([base('A'), base('B', B2), base('C', { fim: '2026-10-13' }), base('D')], geo);
  assert.deepEqual(r.frentes[0].ids, ['C', 'A', 'D', 'B']);
  const s = r.frentes[0].seq; assert.ok(Math.abs(s[1].leg - cosLaw(geo.c.C, geo.c.A)) < 0.5 && Math.abs(s[2].leg - cosLaw(geo.c.A, geo.c.D)) < 0.5);
});
ok('U7 cargas: fechadas por O.S. hoje (10 + 15 + 5 ha a 100 L/ha, tanque 2.000 L = 3) e contínuas só como ganho a decidir (= 2)', () => {
  const r = F.osFrentes([base('A', { area: 10, fim: '2026-10-13' }), base('B', { area: 15 }), base('C', { area: 5 })], { tipo: 'lonlat', c: { A: geo.c.A, B: geo.c.B, C: geo.c.C } });
  assert.deepEqual(r.frentes[0].cargas, { porOS: 3, continuas: 2, tanque: 2000, todas: true });
});
ok('U8 plantio junta pela cultura (OS-0420 × OS-0431); troca de semente pede limpeza; a lanço com outra dose é nova regulagem', () => {
  const pl = { fam: 'Plantio', liquido: false, vazao: null, tanque: null, cultura: 'Soja' };
  const r = F.osFrentes([base('A', Object.assign({ ins: [{ p: 'Semente de soja 58 W', dose: 52, un: 'kg' }] }, pl)), base('B', Object.assign({ ins: [{ p: 'Semente de soja 62 X', dose: 50, un: 'kg' }] }, pl))], geo);
  assert.equal(r.frentes.length, 1); assert.match(r.frentes[0].trocas[0].t, /limpeza da plantadeira/);
  const ln = { fam: 'A lanço', liquido: false, vazao: null, tanque: null };
  const q = F.osFrentes([base('A', Object.assign({ ins: [{ p: 'KCl 60%', dose: 150, un: 'kg' }] }, ln)), base('B', Object.assign({ ins: [{ p: 'KCl 60%', dose: 120, un: 'kg' }] }, ln))], geo);
  assert.equal(q.frentes.length, 1); assert.match(q.frentes[0].trocas[0].t, /^Nova regulagem/); assert.equal(q.frentes[0].cargas.porOS, null);
});
ok('U9 ganho em km contra cada O.S. sozinha (ida e volta da sede), com oráculo independente', () => {
  const g = Object.assign({}, geo, { sede: [-47.143, -34.612], sedeNome: 'Sede' });
  const r = F.osFrentes([base('A'), base('B'), base('E')], g), f = r.frentes[0], c = f.ids.map(id => g.c[id]);
  let rota = cosLaw(g.sede, c[0]); for (let i = 1; i < c.length; i++) rota += cosLaw(c[i - 1], c[i]); rota += cosLaw(c[c.length - 1], g.sede);
  const so = c.reduce((s, p) => s + 2 * cosLaw(g.sede, p), 0);
  assert.ok(Math.abs(f.km - rota / 1000) < 0.002 && Math.abs(f.kmSo - so / 1000) < 0.002 && f.km < f.kmSo, JSON.stringify([f.km, rota, f.kmSo, so]));
  assert.equal(f.seq[0].legDe, 'Sede');
});
ok('U10 família pelo implemento antes da operação; fertirrigação vai pelo pivô (sem frente)', () => {
  assert.equal(F.frFamilia('Plantadeira', 'Pulverização'), 'Plantio'); assert.equal(F.frFamilia('Distribuidor', ''), 'A lanço');
  assert.equal(F.frFamilia('', 'Fertirrigação de arranque'), null); assert.equal(F.frFamilia('', 'Calagem'), 'A lanço');
  assert.equal(F.frFamilia('', 'Plantio · Soja 58 W'), 'Plantio'); assert.equal(F.frFamilia('', 'Dessecação pré-plantio'), 'Pulverização');
  const r = F.osFrentes([base('A', { fam: null }), base('B')], geo); assert.equal(r.frentes.length, 0); assert.match(r.soltas.find(s => s.id === 'A').motivo, /pivô/);
});
ok('U11 a frente separa liberadas (executa) e pendentes (quem decide), sem mudar nada', () => {
  const r = F.osFrentes([base('A'), base('B', { liberada: false })], geo); assert.deepEqual(r.frentes[0].liberadas, ['A']); assert.deepEqual(r.frentes[0].pendentes, ['B']);
});
ok('U12 desenho sem escala (plano): ordena pela proximidade, sem km', () => {
  const plano = { tipo: 'plano', c: { A: [0, 0], B: [10, 0], C: [100, 0] } };
  const r = F.osFrentes([base('A', { fim: '2026-10-13' }), base('C'), base('B')], plano);
  assert.deepEqual(r.frentes[0].ids, ['A', 'B', 'C']); assert.equal(r.frentes[0].km, null); assert.equal(r.frentes[0].kmSo, null);
});
ok('U13 produtos somados na unidade canônica (mL vira L), pela área de cada O.S.', () => {
  const r = F.osFrentes([base('A', { area: 10, ins: [{ p: 'X', dose: 500, un: 'mL' }] }), base('B', { area: 15, ins: [{ p: 'X', dose: 0.5, un: 'L' }] })], geo);
  assert.deepEqual(r.frentes[0].produtos, [{ p: 'X', un: 'L', q: 12.5 }]);
});
ok('U14 produto diferente não se mistura; família diferente nunca', () => {
  const r = F.osFrentes([base('A'), base('B', { ins: [{ p: 'Tebuconazol 200 EC', dose: 1, un: 'L' }] }), base('C', { fam: 'A lanço', liquido: false })], geo);
  assert.equal(r.frentes.length, 0); assert.equal(r.soltas.length, 3);
});
ok('U15 vazão ainda não definida não vira outra calda: entra na mesma, sem contar na carga até definir', () => {
  const r = F.osFrentes([base('A'), base('B'), base('C', { vazao: null, bloq: 'Definir vazão' })], geo);
  assert.equal(r.frentes[0].caldas, 1); assert.equal(r.frentes[0].trocas.length, 0); assert.equal(r.frentes[0].cargas.porOS, 2); assert.equal(r.frentes[0].porque[0], 'mesma calda');
});
console.log('TOTAL ' + n + ' PASS');
