// Testes puros da Produção (docs/colheita/ESPECIFICACAO.md §6 e §8) · node, sem navegador.
// Carregado depois de: CEN0 + cenario.js + PRDC + producao.js (+ núcleo da O.S. com CARD e o motor de carência).
// Cada verificação vira uma linha do JSON final; os números são os de docs/colheita/verificacao/contas.py (K01..K15).
const R = []; function ok(n, c, info) { R.push({ n, ok: !!c, info: c ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 700) }); }
const TRY = (f) => { try { f(); return ''; } catch (e) { return String(e.message || e); } };

// ---- U01 · unidade de cada cultura (DEC-0510-03) e conversões K11 ----
ok('U01a soja: 2.305.200 kg = 38.420 sc (saca de 60 kg)', prQ('Soja', 2305200) === 38420 && prUnTxt('Soja', 2305200) === '38.420 sc', prUnTxt('Soja', 2305200));
ok('U01b mamão: produção em t, produtividade em t/ha, estoque em kg', prUnTxt('Mamão Formosa', 60320) === '60,32 t' && prUn('Mamão Formosa').prtv === 't/ha' && prEstTxt('Mamão Formosa', 12050) === '12.050 kg', [prUnTxt('Mamão Formosa', 60320), prEstTxt('Mamão Formosa', 12050)]);
ok('U01c K11 laranja: 24.480 kg = 600 cx (40,8 kg); em 2 ha = 300 cx/ha com 12,24 t/ha ao lado', prQ('Laranja', 24480) === 600 && prPrtvTxt('Laranja', 24480, 2) === '300,00 cx/ha · 12,24 t/ha', prPrtvTxt('Laranja', 24480, 2));
ok('U01d K11 coco: 12.500 frutos em 1,25 ha = 10 mil frutos/ha', prPrtv('Coco', 12500, 1.25) === 10 && prUn('Coco').prtv === 'mil frutos/ha', prPrtv('Coco', 12500, 1.25));
ok('U01e K11 arroz RS: 9.044 kg = 180,88 sc de 50 kg (não 150,73 sc de 60)', prQ('Arroz RS', 9044) === 180.88 && prFmt(prQ('Arroz RS', 9044), 2) === '180,88', prQ('Arroz RS', 9044));
ok('U01f cultura sem unidade no cadastro é recusada (nada é presumido)', /sem unidade de mercado/.test(TRY(() => prUn('Pitaya'))), TRY(() => prUn('Pitaya')));
ok('U01g decimal: 0,1 + 0,2 = 0,3 exato; 1,005 com 2 casas = 1,01 (meio para cima, sem erro de float)', prSoma([0.1, 0.2]) === 0.3 && prFmt(1.005, 2) === '1,01' && prFmt(-2.5, 0) === '−3', [prSoma([0.1, 0.2]), prFmt(1.005, 2)]);

// ---- U02 · descontos de grão K01..K03 (R-08) ----
{ const a = prCorrigir(30000, '16.5', '2.0', 14, 1);
  ok('U02a K01 soja 30.000 kg, 16,5 % e 2 %: limpo 29.700, comercial 28.836,627907 kg = 480,61 sc', a.limpo === 29700 && a.com === 28836.627907 && prFmt(prQ('Soja', a.com), 2) === '480,61' && a.dImp === 300 && a.dUmid === 863.372093, a);
  const b = prCorrigir(30000, '13.0', '0.8', 14, 1);
  ok('U02b K02 abaixo do padrão não dá bônus: 30.000 kg', b.com === 30000 && b.limpo === 30000, b);
  const f = prCorrigir(28000, '15.2', '1.4', 14, '0.5');
  ok('U02c K03 feijão: 27.360,818605 kg = 456,01 sc', f.com === 27360.818605 && prFmt(prQ('Feijão', f.com), 2) === '456,01', f);
  ok('U02d matéria seca: função única (prMs) usada no comercial', prMs(29700, '16.5', 14) === a.com, prMs(29700, '16.5', 14)); }

// ---- U05 · rateio da mistura K04 (BEN §3.3) ----
{ const r = prRateio(10001, [60, 40]);
  ok('U05a K04 10.001 kg 60/40: 6.000,6 + 4.000,4 e a soma fecha', r[0] === 6000.6 && r[1] === 4000.4 && prSoma(r) === 10001, r);
  const t = prRateio(100, [1, 1, 1]); ok('U05b três partes iguais de 100 kg: acumulado arredondado (33,333333 · 33,333334 · 33,333333) e a soma fecha em 100', prSoma(t) === 100 && t[0] === 33.333333 && t[1] === 33.333334 && t[2] === 33.333333, t); }

// ---- U06 (parte da conta) · K15: área do ciclo perene = área do cultivo, não o maior passe ----
ok('U06k K15 passes parciais alternados (31 ha e 31,79 ha, 30 t cada): 0,96 t/ha pela área do cultivo; o maior passe daria 1,89', prFmt(prPrtv('Mamão Formosa', 60000, 62.79), 2) === '0,96' && prFmt(prPrtv('Mamão Formosa', 60000, 31.79), 2) === '1,89', [prPrtv('Mamão Formosa', 60000, 62.79), prPrtv('Mamão Formosa', 60000, 31.79)]);

// ---- K12 · semana ISO do lote ----
ok('K12 semana ISO: 16/09 = S38; 22/09 = S39; 05/03 = S10; 26/09 = S39; S40 começa em 28/09', prSem('2026-09-16') === '2026-W38' && prSem('2026-09-22') === '2026-W39' && prSem('2026-03-05') === '2026-W10' && prSem('2026-09-26') === '2026-W39' && prSemIni('2026-W40') === '2026-09-28',
   [prSem('2026-09-16'), prSem('2026-09-22'), prSem('2026-03-05'), prSem('2026-09-26'), prSemIni('2026-W40')]);
