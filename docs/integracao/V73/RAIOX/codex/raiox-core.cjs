
(() => {
'use strict';
// ================= base sintética · Lagoa Grande · mamão =================
const START = new Date(2026, 6, 1);   // 01/07/2026
const DAYS = 86;                      // 25/09/2026, data da última cena de satélite
const RAINMM = { 18: 22, 19: 9, 37: 14, 38: 31, 39: 6, 52: 18, 66: 11, 67: 25, 79: 16 };
const nf0 = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 });
const nf1 = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 });
const nf2 = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const dDate = d => { const x = new Date(START); x.setDate(x.getDate() + d); return x; };
const fmtD = d => { const x = dDate(d); return String(x.getDate()).padStart(2, '0') + '/' + String(x.getMonth() + 1).padStart(2, '0'); };
const median = arr => { if (!arr.length) return null; const s = [...arr].sort((a, b) => a - b); const m = Math.floor(s.length / 2); return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const signed2 = v => (Math.abs(v) < .005 ? '' : v > 0 ? '+' : '−') + nf2.format(Math.abs(v));
const pct = v => (v >= 0 ? '+' : '−') + nf0.format(Math.abs(v * 100)) + ' %';
const dose = (v) => nf2.format(v).replace(/,00$/, '');
function rngFor(s) { let h = 2166136261; for (const ch of s) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); } let a = h >>> 0;
  return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

// ---- clima diário da estação da fazenda (sintético) e previsão dos 7 dias seguintes ----
const PREV_RAIN = { 90: 14 };   // previsão sintética: chuva em 30/09
function climaDia(d, r, rv, rainMap) {
  const t = d / DAYS, rain = rainMap[d] || 0, rainPrev = rainMap[d - 1] || 0;
  const wave = d >= 44 && d <= 50 ? 3.6 : d >= 74 && d <= 80 ? 3.1 : 0;
  const tmax = 29.2 + 4.4 * t + wave + (r() - .5) * 1.8 - (rain ? 3.5 : 0) - (rainPrev ? 1.2 : 0);
  const tmin = tmax - 11.5 + (r() - .5) * 2 + (rain ? 2.5 : 0);
  const ur = Math.max(24, Math.min(96, 60 - 16 * t - wave * 2.6 + (rain ? 26 : 0) + (rainPrev ? 12 : 0) + (r() - .5) * 8));
  const molh = rain ? 9 + r() * 5 : rainPrev ? 5 + r() * 4 : ur > 62 ? 2 + r() * 3 : r() * 1.5;
  const tmed = (tmax + tmin) / 2, es = 0.6108 * Math.exp(17.27 * tmed / (tmed + 237.3));
  return { tmax, tmin, ur, molh, dpv: es * (1 - ur / 100), chuva: rain, vento: 1.2 + rv() * 2.8, quenteSeco: tmax >= 32 && ur < 50, calor: tmax >= 35, molhado: molh >= 8 && tmed >= 18 && tmed <= 30 };
}
const CLIMA = [], CLIMA_PREV = [];
(() => { const r = rngFor('clima'), rv = rngFor('vento'); for (let d = 0; d <= DAYS; d++) CLIMA.push(climaDia(d, r, rv, RAINMM)); })();
(() => { const r = rngFor('previsao'), rv = rngFor('vento-prev'), m = Object.assign({}, RAINMM, PREV_RAIN); for (let d = DAYS + 1; d <= DAYS + 7; d++) CLIMA_PREV.push(Object.assign(climaDia(d, r, rv, m), { prev: true })); })();
const climaAt = d => d <= DAYS ? CLIMA[d] : CLIMA_PREV[d - DAYS - 1];

// ---- pivôs: áreas e NDVI das cenas de 10/09 e 25/09 do protótipo oficial (lagoa_s2.json, sintético) ----
const PIVO_DATA = [
  ['P1', 29.92, .58, .56], ['P2', 37.75, .78, .80], ['P3', 70.18, .55, .55], ['P4', 73.18, .77, .78], ['P5', 71.11, .26, .39], ['P6', 62.79, .78, .78],
  ['P7', 61.39, .38, .38], ['P8', 50.63, .39, .39], ['P9', 74.98, .80, .78], ['P10', 30.15, .58, .55], ['P11', 50.0, .15, .17], ['P12', 48.47, .64, .14],
  ['P13', 49.31, .15, .16], ['P14', 63.16, .55, .58], ['P15', 36.17, .38, .36], null, ['P17', 33.36, .80, .78], ['P18', 48.93, .80, .80],
  ['P19', 75.11, .79, .78], ['P20', 77.39, .78, .79], ['P21', 80.82, .55, .58], ['P22', 62.07, .77, .77], ['P23', 63.99, .78, .78], ['P24', 34.37, .78, .80]];
const STAGE = { P1: 'media', P3: 'media', P10: 'media', P14: 'media', P21: 'media', P5: 'jovem', P7: 'jovem', P8: 'jovem', P15: 'jovem', P11: 'solo', P13: 'solo', P12: 'velha' };
const STAGE_TXT = { adulta: 'em produção', media: 'em formação', jovem: 'plantio novo', solo: 'sem lavoura', velha: 'lavoura velha erradicada' };
const PIVOS = PIVO_DATA.map((p, i) => { if (!p) return null; const col = i % 6, row = Math.floor(i / 6);
  return { id: p[0], ha: p[1], a71: p[2], a86: p[3], stage: STAGE[p[0]] || 'adulta', x: 8.5 + col * 16.6, y: 12.8 + row * 24.8 }; }).filter(Boolean);
PIVOS.forEach(p => { p.pestOff = ['solo', 'velha'].includes(p.stage); });
const P = id => PIVOS.find(p => p.id === id);

// ---- pragas e doenças (resposta ligada ao clima) ----
const ALVOS = [
  { id: 'acaro', nome: 'Ácaro-rajado', art: 'o ácaro-rajado', fx: { def: .05, n: .004, k: 0, lav: .6 }, med: 'folhas com ácaro', un: '%', curto: '%', nc: 15, cap: 70, x0: [.5, 2.2], wk: [1.45, 1.45], imm: .05,
    clima: c => 1 + (c.quenteSeco ? .05 : 0) - (c.molhado ? .025 : 0), fav: c => c.quenteSeco, favTxt: 'dia quente e seco (≥ 32 °C e UR < 50 %)', favCurto: 'quente e seco',
    prods: [ { n: 'Espirodiclofeno 240 SC', c: 'Espirodiclofeno', g: 'IRAC 23', base: .86, res: 18, dose: .3, du: 'L' },
             { n: 'Abamectina 18 EC', c: 'Abamectina', g: 'IRAC 6', base: .80, res: 10, dose: .5, du: 'L' },
             { n: 'Fenpiroximato 50 SC', c: 'Fenpiroximato', g: 'IRAC 21A', base: .80, res: 13, dose: 1, du: 'L' },
             { n: 'Óleo mineral', c: 'Óleo mineral', g: 'ação física', base: .38, res: 3, dose: 1.5, du: 'L' } ] },
  { id: 'mosca', nome: 'Mosca-branca', art: 'a mosca-branca', fx: { def: 0, n: .006, k: 0, lav: .7 }, med: 'adultos por folha', un: '', curto: '/folha', nc: 5, cap: 40, x0: [.3, 1.2], wk: [1.36, 1.36], imm: .025,
    clima: c => 1 + (c.quenteSeco ? .04 : 0) - (c.molhado ? .02 : 0), fav: c => c.quenteSeco, favTxt: 'dia quente e seco (≥ 32 °C e UR < 50 %)', favCurto: 'quente e seco',
    prods: [ { n: 'Espiromesifeno 240 SC', c: 'Espiromesifeno', g: 'IRAC 23', base: .80, res: 16, dose: .5, du: 'L' },
             { n: 'Acetamiprido 200 SP', c: 'Acetamiprido', g: 'IRAC 4A', base: .74, res: 10, dose: .25, du: 'kg' },
             { n: 'Piriproxifem 100 EC', c: 'Piriproxifem', g: 'IRAC 7C', base: .62, res: 20, dose: .5, du: 'L' } ] },
  { id: 'antrac', nome: 'Antracnose', art: 'a antracnose', fx: { def: 0, n: 0, k: .03, lav: 1 }, med: 'frutos com lesão', un: '%', curto: '%', nc: 5, cap: 45, x0: [.3, 1.1], wk: [1.0, 1.0], imm: .01,
    clima: c => c.molhado ? 1.085 : (c.ur > 65 ? 1.012 : .993), fav: c => c.molhado, favTxt: 'dia com 8 h ou mais de folha molhada (UR ≥ 90 %) entre 18 e 30 °C', favCurto: 'molhamento ≥ 8 h',
    prods: [ { n: 'Azoxistrobina 250 SC', c: 'Azoxistrobina', g: 'FRAC 11', base: .70, res: 14, dose: .4, du: 'L' },
             { n: 'Tebuconazol 200 EC', c: 'Tebuconazol', g: 'FRAC 3', base: .66, res: 12, dose: 1, du: 'L' },
             { n: 'Mancozebe 800 WP', c: 'Mancozebe', g: 'FRAC M3', base: .45, res: 7, dose: 3, du: 'kg' } ] },
  { id: 'cochon', nome: 'Cochonilha', art: 'a cochonilha', fx: { def: 0, n: .004, k: 0, lav: 1 }, med: 'plantas com colônia', un: '%', curto: '%', nc: 10, cap: 50, x0: [.8, 2.5], wk: [1.12, 1.12], imm: .03,
    clima: c => 1 + (c.quenteSeco ? .03 : 0), fav: c => c.quenteSeco, favTxt: 'dia quente e seco (≥ 32 °C e UR < 50 %)', favCurto: 'quente e seco',
    prods: [ { n: 'Buprofezina 250 SC', c: 'Buprofezina', g: 'IRAC 16', base: .74, res: 20, dose: 1, du: 'L' },
             { n: 'Acetamiprido 200 SP', c: 'Acetamiprido', g: 'IRAC 4A', base: .70, res: 12, dose: .25, du: 'kg' },
             { n: 'Óleo mineral', c: 'Óleo mineral', g: 'ação física', base: .45, res: 4, dose: 1.5, du: 'L' } ] } ];
// efeitos plantados na eficácia (gabarito da demonstração): dia quente e seco e chuva até 1 dia depois reduzem a eficácia
const APP_FX = { qs: .78, chuva: .7 };
const avOf = (pid, d) => (rngFor('av' + pid + '|' + d)() < .5 ? 'A' : 'B');   // avaliador da vistoria (sem efeito: variável de ruído)
const EQ = { a600: { n: 'Atomizador · 600 L/ha', c: 'Atomizador 600 L/ha', cov: 1.0, lha: 600 }, a400: { n: 'Atomizador · 400 L/ha', c: 'Atomizador 400 L/ha', cov: .9, lha: 400 }, b100: { n: 'Barra · 100 L/ha', c: 'Barra 100 L/ha', cov: .6, lha: 100 } };
const PROF = {};
PIVOS.forEach(p => { const r = rngFor('prof' + p.id); const late = ['P4', 'P9', 'P21', 'P20'].includes(p.id);
  PROF[p.id] = { press: 0.75 + r() * 0.7, eq: ['P4', 'P6', 'P20'].includes(p.id) ? 'b100' : (['P3', 'P9', 'P14', 'P22'].includes(p.id) ? 'a400' : 'a600'),
    repete: ['P6', 'P17', 'P21'].includes(p.id), oleo1: ['P2', 'P9', 'P24'].includes(p.id), delay: late ? 6 + Math.floor(r() * 2) : 2 + Math.floor(r() * 3),
    gatilho: late ? 1.15 : 0.9, off: Math.floor(r() * 3), falha: p.id === 'P17' ? [71, 78] : [] }; });
const HOT = { acaro: ['P4', 'P6', 'P17', 'P9', 'P21'], mosca: ['P1', 'P2', 'P8'], antrac: ['P19', 'P23', 'P5'], cochon: ['P18', 'P14'] };

function simulatePest(p, a) {
  const r = rngFor(p.id + a.id), pf = PROF[p.id], hot = HOT[a.id].includes(p.id) ? 1.55 : 1;
  const fx = a.fx, falta = Math.max(0, .95 - WATER[p.id].suff) / .27, NK = NUT[p.id];   // efeitos plantados: falta de água, N e K recentes, chuva forte
  let x = (a.x0[0] + r() * (a.x0[1] - a.x0[0])) * pf.press * hot * (p.stage === 'jovem' ? .7 : 1);
  const obs = [], apps = []; let resid = 0, last = -99, pending = null, lastGroup = null, n = 0, consec = 0; const groupCount = {};
  for (let d = 0; d <= DAYS; d++) {
    if (pending && pending.day === d) {
      let prod;
      if (pf.oleo1 && n === 0 && a.prods.some(q => q.c === 'Óleo mineral')) prod = a.prods.find(q => q.c === 'Óleo mineral');
      else if (pf.repete) prod = a.prods.find(q => q.c !== 'Óleo mineral') || a.prods[0];
      else { const cand = a.prods.filter(q => q.c !== 'Óleo mineral' && q.g !== lastGroup); prod = cand[(n + p.id.length) % cand.length] || a.prods[0]; }
      const rep = groupCount[prod.g] || 0; consec = prod.g === lastGroup ? consec + 1 : 0;
      const eq = EQ[pf.eq], resist = consec > 0 ? Math.pow(.7, consec) : Math.pow(.93, rep);
      const qsDia = CLIMA[d].quenteSeco, chuvaDepois = (RAINMM[d] || 0) + (RAINMM[d + 1] || 0) >= 5;
      const eff = Math.min(.95, prod.base * eq.cov * resist * (qsDia ? APP_FX.qs : 1) * (chuvaDepois ? APP_FX.chuva : 1) * (0.9 + r() * 0.18));
      x = x * (1 - eff); resid = Math.round(prod.res * (0.7 + 0.3 * eq.cov));
      groupCount[prod.g] = rep + 1; lastGroup = prod.g; n++; last = d;
      apps.push({ day: d, prod, eq: pf.eq, entrada: n, rep: rep + 1, consec, alvo: a.id, qsDia, chuvaDepois }); pending = null;
    }
    const wk = a.wk[0] + (a.wk[1] - a.wk[0]) * d / DAYS;
    let g = Math.pow(wk, 1 / 7) * a.clima(CLIMA[d]) * (1 + fx.def * falta + fx.n * (NK.n14[d] - 6.4) + fx.k * Math.max(0, 1 - NK.k14[d] / 20)); if (resid > 0) { g = 1 + (g - 1) * 0.2; resid--; }
    x = Math.max(.05, Math.min(a.cap, x * g + a.imm * pf.press * hot * (resid > 0 ? 0.3 : 1)));
    if ((RAINMM[d] || 0) >= 10) x = Math.max(.05, x * fx.lav);
    if ((d - 1 - pf.off) % 7 === 0 && d >= 1 + pf.off && !pf.falha.includes(d)) {
      const v = Math.max(0, x * (0.88 + r() * 0.24)); obs.push({ day: d, v, aval: avOf(p.id, d) });
      if (v >= a.nc * pf.gatilho && d - last > 9 && !pending) pending = { day: Math.min(DAYS, d + pf.delay) };
    }
  }
  apps.forEach(ap => { const before = [...obs].reverse().find(o => o.day <= ap.day && ap.day - o.day <= 10); const after = obs.find(o => o.day >= ap.day + 5 && o.day <= ap.day + 14);
    ap.before = before || null; ap.after = after || null; ap.red = before && after && before.v > 0 ? (before.v - after.v) / before.v : null;
    const back = obs.find(o => o.day > ap.day && o.v >= a.nc); ap.backDay = back ? back.day : null; });
  return { obs, apps };
}

// ---- água e adubação ----
const NEED = { adulta: 5.2, media: 4.6, jovem: 3.0, solo: 0, velha: 4.0 };        // mm/dia (ETc de exemplo, ajustada pelo DPV)
const SUFF = { P3: .68, P14: .7, P21: .7, P20: .9 };                              // fração da necessidade atendida pela irrigação
const FERT = {
  std: { every: 14, items: [['Nitrato de amônio', 20, { N: .32 }], ['Sulfato de potássio', 45, { K2O: .5, S: .17 }]], via: 'Fertirrigação', nome: 'Nitrato de amônio + sulfato de potássio · a cada 14 dias' },
  ureia: { every: 14, items: [['Ureia', 12, { N: .45 }], ['Cloreto de potássio', 30, { K2O: .6 }]], via: 'Fertirrigação', nome: 'Ureia + cloreto de potássio' },
  irreg: { every: 31, items: [['Nitrato de amônio', 20, { N: .32 }], ['Sulfato de potássio', 45, { K2O: .5, S: .17 }]], via: 'Fertirrigação', nome: 'Nitrato de amônio + sulfato de potássio · intervalo > 21 dias' },
  arranque: { every: 10, items: [['Nitrato de amônio', 25, { N: .32 }], ['Ácido bórico', 1, { B: .17 }]], via: 'Fertirrigação de arranque', nome: 'Arranque: nitrato de amônio + ácido bórico' } };
const PLAN = { P9: 'ureia', P23: 'ureia', P20: 'irreg', P24: 'irreg', P1: 'irreg', P10: 'irreg' };
const EVENTS = [], WATER = {}, SAT = {}; let evSeq = 0;
const addEvent = e => { e.id = 'e' + (++evSeq); EVENTS.push(e); return e; };
const needOn = (p, d) => NEED[p.stage] * Math.max(.75, Math.min(1.35, 1 + .14 * (CLIMA[d].dpv - 1.9)));
PIVOS.forEach(p => {
  const r = rngFor('w' + p.id); const suff = SUFF[p.id] || (p.stage === 'jovem' ? 1 : .98);
  const irr = new Array(DAYS + 1).fill(0); const off = Math.floor(r() * 3);
  if (NEED[p.stage] > 0) for (let d = off; d <= DAYS; d += 3) {
    if ((RAINMM[d] || 0) + (RAINMM[d - 1] || 0) >= 10) continue;
    const rain3 = [0, 1, 2].reduce((s, k) => s + (RAINMM[d - k] || 0), 0); const need3 = [0, 1, 2].reduce((s, k) => s + needOn(p, Math.min(DAYS, d + k)), 0);
    irr[d] = Math.max(0, Math.round((need3 - rain3) * suff * 2) / 2);
  }
  WATER[p.id] = { irr, suff };
  if (['adulta', 'media', 'jovem'].includes(p.stage)) {
    const prog = p.stage === 'jovem' ? 'arranque' : (PLAN[p.id] || 'std'); const pr = FERT[prog]; let d = 3 + Math.floor(r() * 6);
    while (d <= DAYS) {
      const items = pr.items.map(([n, ds, nut]) => ({ n, dose: ds, du: 'kg', total: ds * p.ha, nut: Object.fromEntries(Object.entries(nut).map(([k, f]) => [k, ds * f])) }));
      addEvent({ kind: 'adub', day: d, pid: p.id, via: pr.via, prog, progNome: pr.nome, items });
      d += pr.every + (prog === 'irreg' ? Math.floor(r() * 6) : Math.floor(r() * 2));
    }
  }
});
// N e K2O aplicados nos 14 dias até cada data (kg/ha), por pivô
const NUT = {}; PIVOS.forEach(p => { const n = new Array(DAYS + 8).fill(0), k = new Array(DAYS + 8).fill(0);
  EVENTS.forEach(e => { if (e.kind !== 'adub' || e.pid !== p.id) return; const N = e.items.reduce((s, it) => s + (it.nut.N || 0), 0), K = e.items.reduce((s, it) => s + (it.nut.K2O || 0), 0);
    for (let d = e.day; d < e.day + 14 && d < n.length; d++) { n[d] += N; k[d] += K; } });
  NUT[p.id] = { n14: n, k14: k }; });
const PEST = {}; ALVOS.forEach(a => { PEST[a.id] = {}; PIVOS.forEach(p => { if (!p.pestOff) PEST[a.id][p.id] = simulatePest(p, a); }); });
addEvent({ kind: 'oper', day: 73, pid: 'P12', via: 'Erradicação da lavoura velha', items: [{ n: 'Glifosato 480', dose: 3, du: 'L', total: 3 * P('P12').ha }], os: 'OS-0509', calda: 'Barra · 100 L/ha' });
ALVOS.forEach(a => PIVOS.forEach(p => { const s = PEST[a.id][p.id]; if (!s) return; s.apps.forEach(ap => {
  ap.ev = addEvent({ kind: 'def', day: ap.day, pid: p.id, alvo: a.id, ap, items: [{ n: ap.prod.n, dose: ap.prod.dose, du: ap.prod.du, total: ap.prod.dose * p.ha }], calda: EQ[ap.eq].n, caldaL: EQ[ap.eq].lha * p.ha }); }); }));
EVENTS.sort((x, y) => x.day - y.day);

// ---- vigor por satélite: cenas a cada 5 dias; NDVI ancorado em 10/09 e 25/09; calor e falta de água pesam ----
const SCENES = []; for (let d = 1; d <= DAYS; d += 5) SCENES.push(d);
const SCENE_CLOUD = { 16: 62, 36: 88, 51: 34, 66: 74 };
const IDX = { NDVI: { cuts: [.30, .45, .60, .72, .82] }, NDRE: { cuts: [.10, .18, .25, .30, .35] } };
PIVOS.forEach(p => {
  const r = rngFor('s' + p.id), W = WATER[p.id];
  const base = d => p.stage === 'adulta' ? .79 : p.stage === 'media' ? .61 : p.stage === 'jovem' ? (p.id === 'P5' ? .14 + .25 * Math.pow(d / DAYS, 1.6) : .27 + .11 * d / DAYS)
    : p.stage === 'solo' ? .15 : (d < 72 ? .66 : d > 75 ? .14 : .66 - (.52 * (d - 72) / 3));
  let sw = 40, wEff = 0, pool = 1.1, nEff = 0; const ndvi = [], nut = [];
  const fertN = {}; EVENTS.forEach(e => { if (e.kind === 'adub' && e.pid === p.id) fertN[e.day] = e.items.reduce((s, it) => s + (it.nut.N || 0), 0); });
  for (let d = 0; d <= DAYS; d++) {
    const need = NEED[p.stage] ? needOn(p, d) : 0;
    sw = Math.max(0, Math.min(60, sw + (RAINMM[d] || 0) + W.irr[d] - need));
    const stress = need > 0 ? Math.max(0, 1 - sw / 22) : 0;
    const heat = need > 0 && CLIMA[d].calor ? .018 * (1.15 - W.suff) * 3 : 0;
    wEff += (-0.11 * stress - heat - wEff) * 0.12;
    pool = pool * 0.962 + (fertN[d] || 0) * 0.085;
    const target = need > 0 && p.stage !== 'velha' ? 0.085 * Math.tanh(pool - 0.9) : 0; nEff += (target - nEff) * 0.14;
    ndvi.push(base(d) + (p.stage === 'solo' || (p.stage === 'velha' && d > 75) ? 0 : wEff + nEff) + (r() - .5) * .006); nut.push(p.stage === 'solo' ? 0 : nEff);
  }
  const c71 = p.a71 - ndvi[71], c86 = p.a86 - ndvi[86]; const corr = d => d <= 71 ? c71 : c71 + (c86 - c71) * (d - 71) / 15;
  const ndviC = ndvi.map((v, d) => Math.max(.05, Math.min(.95, v + corr(d))));
  const spread = p.stage === 'adulta' ? .045 : p.stage === 'solo' ? .03 : .065;
  SAT[p.id] = { scenes: SCENES.map(d => {
    const cloud = d === 71 ? (p.id === 'P24' ? 44.4 : 0) : d === 86 ? 0 : Math.max(0, Math.min(100, (SCENE_CLOUD[d] || 2) + (r() - .5) * 30));
    const v = ndviC[d] + (r() - .5) * .006, ndre = .508 * v - .036 + 1.1 * nut[d] + (r() - .5) * .004;
    return { day: d, cloud: Math.round(cloud * 10) / 10, ok: cloud <= 20, NDVI: { med: v, p10: v - spread, p90: v + spread * .8 }, NDRE: { med: ndre, p10: ndre - spread / 2, p90: ndre + spread * .4 } }; }) };
});
const sceneAt = (pid, day, idx) => { const s = SAT[pid].scenes.find(q => q.day === day); return s && s.ok ? s[idx].med : null; };
function vigorEffect(e, idx) {
  const sc = SAT[e.pid].scenes; const before = [...sc].reverse().find(s => s.ok && s.day <= e.day && e.day - s.day <= 10); const after = sc.find(s => s.ok && s.day >= e.day + 10 && s.day <= e.day + 25);
  if (!before || !after) return null; const d = after[idx].med - before[idx].med, st = P(e.pid).stage;
  const peers = PIVOS.filter(q => q.stage === st && q.id !== e.pid).map(q => { const b = sceneAt(q.id, before.day, idx), a = sceneAt(q.id, after.day, idx); return b != null && a != null ? a - b : null; }).filter(v => v != null);
  const dc = median(peers); return { before, after, d, dc, rel: dc != null ? d - dc : null };
}
const climaBetween = (a, b) => { let qs = 0, cal = 0, mol = 0, n = 0, tx = 0, ur = 0; for (let d = a + 1; d <= b; d++) { const c = CLIMA[d]; n++; tx += c.tmax; ur += c.ur; if (c.quenteSeco) qs++; if (c.calor) cal++; if (c.molhado) mol++; } return { qs, cal, mol, tmax: n ? tx / n : null, ur: n ? ur / n : null }; };

// ================= Raio-X do alvo: o que faz subir e descer (motor estatístico, sem IA generativa) =================
// Resposta: crescimento semanal entre vistorias seguidas sem aplicação contra o alvo (nem resíduo de 10 dias): r = ln((v2 + ε) ÷ (v1 + ε)) × 7 ÷ dias.
// Camada 1: Spearman por janela. Camada 2: regressão com indicadores (limiar) ajustada pelo nível de partida, estádio e época; intervalo por
// bootstrap em blocos de semana × talhão e Benjamini-Hochberg. Camada 3: eficácia de Henderson-Tilton com talhões-controle. Camada 4: risco em 7 dias.
const W3 = [['na semana da vistoria', 0, 7], ['8 a 14 dias antes', 7, 14], ['15 a 28 dias antes', 14, 28]];
const W2N = [['nos 14 dias antes', 0, 14], ['de 15 a 28 dias antes', 14, 28]];
const W1 = [['', 0, 0]];
const plural = (t, s, p) => (t === 1 ? s : p);
const RXF = [
  { k: 'qs', t: 'Dias quentes e secos', tipo: 'Clima', wins: W3, dec: 0, cond: (t, w) => t + ' ' + plural(t, 'dia', 'dias') + ' ou mais por semana, ' + w + ' (≥ 32 °C e UR < 50 %)', fmt: v => nf1.format(v) + ' dias quentes e secos por semana' },
  { k: 'tmax', t: 'Temperatura máxima', tipo: 'Clima', wins: W3, dec: 1, cond: (t, w) => 'média de ' + nf1.format(t) + ' °C ou mais, ' + w, fmt: v => 'máxima média de ' + nf1.format(v) + ' °C' },
  { k: 'ur', t: 'Umidade do ar', tipo: 'Clima', wins: W3, dec: 0, cond: (t, w) => 'média de ' + nf0.format(t) + ' % ou mais, ' + w, fmt: v => 'UR média de ' + nf0.format(v) + ' %' },
  { k: 'dpv', t: 'Ar seco (DPV)', tipo: 'Clima', wins: W3, dec: 2, cond: (t, w) => 'DPV médio de ' + nf2.format(t) + ' kPa ou mais, ' + w, fmt: v => 'DPV médio de ' + nf2.format(v) + ' kPa' },
  { k: 'molh', t: 'Folha molhada', tipo: 'Clima', wins: W3, dec: 0, cond: (t, w) => t + ' ' + plural(t, 'dia', 'dias') + ' ou mais por semana com 8 h ou mais de folha molhada, ' + w, fmt: v => nf1.format(v) + ' dias de folha molhada por semana' },
  { k: 'chuva', t: 'Chuva', tipo: 'Clima', wins: W3, dec: 0, cond: (t, w) => nf0.format(t) + ' mm ou mais por semana, ' + w, fmt: v => nf0.format(v) + ' mm de chuva por semana' },
  { k: 'lav', t: 'Chuva forte', tipo: 'Clima', wins: W3, bin: true, cond: (t, w) => '1 dia ou mais com 10 mm ou mais, ' + w, fmt: () => 'chuva forte prevista' },
  { k: 'vento', t: 'Vento', tipo: 'Clima', wins: W3, dec: 1, cond: (t, w) => 'média de ' + nf1.format(t) + ' m/s ou mais, ' + w, fmt: v => 'vento médio de ' + nf1.format(v) + ' m/s' },
  { k: 'irr', t: 'Irrigação', tipo: 'Água', wins: W3, dec: 0, cond: (t, w) => nf0.format(t) + ' mm ou mais por semana, ' + w, fmt: v => nf0.format(v) + ' mm de irrigação por semana' },
  { k: 'def', t: 'Falta de água na irrigação', tipo: 'Água', wins: W1, dec: 0, cond: t => 'irrigação abaixo da necessidade em ' + nf0.format(t) + ' % ou mais', fmt: v => 'irrigação ' + nf0.format(v) + ' % abaixo da necessidade' },
  { k: 'n14', t: 'Nitrogênio aplicado', tipo: 'Nutrição', wins: W2N, dec: 1, cond: (t, w) => nf1.format(t) + ' kg/ha de N ou mais, ' + w, fmt: v => nf1.format(v) + ' kg/ha de N recente' },
  { k: 'k14', t: 'Potássio aplicado', tipo: 'Nutrição', wins: W2N, dec: 0, cond: (t, w) => nf0.format(t) + ' kg/ha de K2O ou mais, ' + w, fmt: v => nf0.format(v) + ' kg/ha de K2O recente' },
  { k: 'ndvi', t: 'Vigor da planta (NDVI)', tipo: 'Planta', wins: W1, dec: 2, cond: t => 'NDVI de ' + nf2.format(t) + ' ou mais na última cena antes da vistoria', fmt: v => 'NDVI ' + nf2.format(v) },
  { k: 'aval', t: 'Avaliador da vistoria', tipo: 'Amostragem', wins: W1, bin: true, cond: () => 'vistoria feita pelo avaliador B, em vez do A', fmt: () => 'avaliador B' } ];
const RXK = k => RXF.find(f => f.k === k);
// Referência agronômica de exemplo (no Safrion vem do protocolo do alvo, validado pelo RT): direção esperada de cada fator.
const PRIOR = { acaro: { qs: 1, tmax: 1, dpv: 1, ur: -1, lav: -1, chuva: -1, molh: -1, def: 1, n14: 1 }, mosca: { qs: 1, tmax: 1, dpv: 1, lav: -1, chuva: -1, n14: 1 },
  antrac: { molh: 1, ur: 1, chuva: 1, lav: 1, k14: -1, qs: -1, dpv: -1 }, cochon: { qs: 1, tmax: 1, dpv: 1, n14: 1 } };
const PRIOR_TXT = { acaro: ['Calor com ar seco (≥ 32 °C e UR < 50 %) acelera a população.', 'Chuva forte derruba a população nas folhas.', 'Falta de água e excesso de nitrogênio favorecem o ácaro.'],
  mosca: ['Tempo quente e seco favorece.', 'Chuva forte reduz os adultos nas folhas.', 'Excesso de nitrogênio favorece insetos sugadores.'],
  antrac: ['Folha e fruto molhados por 8 h ou mais entre 18 e 30 °C favorecem a infecção.', 'Umidade alta e chuva espalham os esporos.', 'Potássio adequado reduz a suscetibilidade.'],
  cochon: ['Tempo quente e seco favorece.', 'Excesso de nitrogênio favorece.'] };
// Gabarito desta demonstração: efeitos plantados na simulação (1 sobe, −1 desce) e variáveis que só andam junto com um efeito plantado.
const PLANTED = { acaro: { qs: 1, molh: -1, lav: -1, def: 1, n14: 1 }, mosca: { qs: 1, molh: -1, lav: -1, n14: 1 }, antrac: { molh: 1, ur: 1, k14: -1 }, cochon: { qs: 1, n14: 1 } };
const PROXY = { acaro: { tmax: 'qs', dpv: 'qs', ur: 'qs', chuva: 'lav', irr: 'def', ndvi: 'def' }, mosca: { tmax: 'qs', dpv: 'qs', ur: 'qs', chuva: 'lav' },
  antrac: { chuva: 'molh', lav: 'molh', dpv: 'ur', tmax: 'ur', qs: 'ur' }, cochon: { tmax: 'qs', dpv: 'qs', ur: 'qs' } };

const ADUB_BY = {}; EVENTS.forEach(e => { if (e.kind === 'adub') (ADUB_BY[e.pid] = ADUB_BY[e.pid] || []).push(e); });
const irrAt = (pid, d) => d <= DAYS ? WATER[pid].irr[d] : WATER[pid].irr.slice(DAYS - 5, DAYS + 1).reduce((s, v) => s + v, 0) / 6;
const WCACHE = new Map();
function winVals(pid, a, b) {   // dias a+1..b; contagens e somas por semana; nutrientes somados na janela
  const key = pid + '|' + a + '|' + b; if (WCACHE.has(key)) return WCACHE.get(key);
  let n = 0, qs = 0, tx = 0, ur = 0, dpv = 0, molh = 0, ch = 0, lav = 0, ve = 0, irr = 0, N = 0, K = 0;
  for (let d = Math.max(0, a + 1); d <= b; d++) { const c = climaAt(d); if (!c) continue; n++; if (c.quenteSeco) qs++; tx += c.tmax; ur += c.ur; dpv += c.dpv; if (c.molhado) molh++; ch += c.chuva; if (c.chuva >= 10) lav++; ve += c.vento; irr += irrAt(pid, d); }
  (ADUB_BY[pid] || []).forEach(e => { if (e.day > a && e.day <= b) e.items.forEach(it => { N += it.nut.N || 0; K += it.nut.K2O || 0; }); });
  const w = v => v * 7 / n, o = n ? { qs: w(qs), tmax: tx / n, ur: ur / n, dpv: dpv / n, molh: w(molh), chuva: w(ch), lav: lav ? 1 : 0, vento: ve / n, irr: w(irr), n14: N, k14: K } : null;
  WCACHE.set(key, o); return o;
}
function fval(row, f, wi) {
  if (f.k === 'def') return Math.max(0, 1 - WATER[row.pid].suff) * 100;
  if (f.k === 'ndvi') { const sc = SAT[row.pid].scenes.filter(s => s.ok && s.day <= row.d1); return sc.length ? sc[sc.length - 1].NDVI.med : null; }
  if (f.k === 'aval') return row.aval === 'B' ? 1 : 0;
  const [, lo, hi] = f.wins[wi], a = wi === 0 && f.wins === W3 ? row.d1 : row.d2 - hi, o = winVals(row.pid, a, row.d2 - lo);
  return o ? o[f.k] : null;
}
const impute = x => { const v = x.filter(z => z != null), m = v.length ? v.reduce((s, z) => s + z, 0) / v.length : 0; return x.map(z => z == null ? m : z); };
function ranks(v) { const idx = v.map((x, i) => i).sort((i, j) => v[i] - v[j]), r = new Array(v.length); let i = 0;
  while (i < idx.length) { let j = i; while (j + 1 < idx.length && v[idx[j + 1]] === v[idx[i]]) j++; for (let k = i; k <= j; k++) r[idx[k]] = (i + j) / 2 + 1; i = j + 1; } return r; }
function pearson(x, y) { const n = x.length; if (n < 3) return null; let mx = 0, my = 0; for (let i = 0; i < n; i++) { mx += x[i]; my += y[i]; } mx /= n; my /= n;
  let sxy = 0, sx = 0, sy = 0; for (let i = 0; i < n; i++) { const a = x[i] - mx, b = y[i] - my; sxy += a * b; sx += a * a; sy += b * b; } return sx && sy ? sxy / Math.sqrt(sx * sy) : null; }
const spear = (x, y) => pearson(ranks(x), ranks(y));
const dot = (a, b) => a.reduce((s, v, i) => s + v * b[i], 0);
function solve(A, b) { const n = b.length, M = A.map((r, i) => [...r, b[i]]);
  for (let c = 0; c < n; c++) { let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r; if (Math.abs(M[p][c]) < 1e-12) return null; [M[c], M[p]] = [M[p], M[c]];
    for (let r = 0; r < n; r++) { if (r === c) continue; const f = M[r][c] / M[c][c]; if (f) for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; } }
  return M.map((r, i) => r[n] / r[i]); }
function wls(X, y, w) { const p = X[0].length, A = Array.from({ length: p }, () => new Array(p).fill(0)), b = new Array(p).fill(0);
  for (let i = 0; i < X.length; i++) { const wi = w ? w[i] : 1; if (!wi) continue; const xi = X[i]; for (let j = 0; j < p; j++) { const v = wi * xi[j]; b[j] += v * y[i]; for (let k = j; k < p; k++) A[j][k] += v * xi[k]; } }
  for (let j = 0; j < p; j++) { for (let k = 0; k < j; k++) A[j][k] = A[k][j]; if (j) A[j][j] += .5; }   // ridge leve: estabiliza indicadores raros e puxa para zero (conservador)
  return solve(A, b); }
const Phi = z => { const t = 1 / (1 + .2316419 * Math.abs(z)), d = .3989423 * Math.exp(-z * z / 2), p = d * t * (.3193815 + t * (-.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274)))); return z > 0 ? 1 - p : p; };
const roundF = (v, f) => { const p = Math.pow(10, f.dec || 0); return Math.round(v * p) / p; };

function rxRows(a, D) {
  const eps = .05 * a.nc, rows = [];
  PIVOS.forEach(p => { const s = PEST[a.id][p.id]; if (!s) return;
    for (let i = 1; i < s.obs.length; i++) { const o1 = s.obs[i - 1], o2 = s.obs[i]; if (o2.day > D) break; const gap = o2.day - o1.day;
      if (gap < 5 || gap > 10 || o1.v < .1 * a.nc) continue; if (s.apps.some(ap => ap.day > o1.day - 10 && ap.day <= o2.day)) continue;
      rows.push({ pid: p.id, stage: p.stage, d1: o1.day, d2: o2.day, v1: o1.v, v2: o2.v, aval: o2.aval, eps, nc: a.nc, r: Math.log((o2.v + eps) / (o1.v + eps)) * 7 / gap, wk: Math.floor((o2.day - 1) / 7) }); } });
  return rows;
}
// controles: nível de partida e estádio. A época só entra com 2 safras ou mais: com uma safra, clima e época andam juntos e o controle apagaria o efeito do clima.
const ctrlCols = r => [Math.log((r.v1 + r.eps) / r.nc), r.stage === 'media' ? 1 : 0, r.stage === 'jovem' ? 1 : 0];
function rxResid(rows) {   // crescimento sem o efeito do nível de partida, do estádio e da época (base da correlação parcial)
  const y = rows.map(r => r.r), Xc = rows.map(r => [1, ...ctrlCols(r)]), bc = wls(Xc, y); return bc ? y.map((v, i) => v - dot(Xc[i], bc)) : y; }
function rxSelect(rows) {   // camada 1: janela de maior associação parcial de cada variável e grupos de variáveis que andam juntas
  const y = rxResid(rows), F = [];
  RXF.forEach(f => { const per = f.wins.map((w, wi) => { const x = impute(rows.map(r => fval(r, f, wi))); return { wi, x, rho: spear(x, y) }; });
    const best = per.filter(q => q.rho != null).sort((p, q) => Math.abs(q.rho) - Math.abs(p.rho))[0]; if (best) F.push({ f, wi: best.wi, x: best.x, rho: best.rho, rhoW: per.map(q => q.rho), mates: [] }); });
  F.sort((p, q) => Math.abs(q.rho) - Math.abs(p.rho));
  F.forEach(g => { if (g.of) return; g.rep = true; F.forEach(h => { if (h === g || h.of || h.rep) return; const c = spear(g.x, h.x); if (c != null && Math.abs(c) >= .7) { h.of = g; h.withRho = c; g.mates.push(h); } }); });
  return F;
}
function stump(x, y, f) {   // limiar que melhor separa o crescimento (mínimo de 8 casos de cada lado)
  if (f.bin) return x.some(v => v >= 1) ? 1 : null;
  const n = x.length, s = [...x].sort((a, b) => a - b), cands = new Set(); for (let q = .15; q <= .851; q += .05) cands.add(roundF(s[Math.floor(q * (n - 1))], f));
  let best = null; cands.forEach(t => { let nh = 0, sh = 0, nl = 0, sl = 0; x.forEach((v, i) => { if (v >= t) { nh++; sh += y[i]; } else { nl++; sl += y[i]; } }); if (nh < 8 || nl < 8) return;
    const sc = Math.abs(sh / nh - sl / nl) * Math.sqrt(nh * nl / n); if (!best || sc > best.sc) best = { t, sc }; });
  return best ? best.t : null;
}
function stumpScore(x, y, f) { const t = stump(x, y, f); if (t == null) return null; let nh = 0, sh = 0, nl = 0, sl = 0; x.forEach((v, i) => { if (v >= t) { nh++; sh += y[i]; } else { nl++; sl += y[i]; } }); return { t, sc: Math.abs(sh / nh - sl / nl) * Math.sqrt(nh * nl / x.length) }; }
const designRow = (r, reps, xs) => [1, ...reps.map((q, j) => (xs ? xs[j] : q.xv[r._i]) >= q.t ? 1 : 0), ...ctrlCols(r)];
function rxFit(rows) {
  rows.forEach((r, i) => { r._i = i; }); const y = rows.map(r => r.r), yr = rxResid(rows), F = rxSelect(rows);
  // no grupo de variáveis que andam juntas, representa quem melhor separa o crescimento (limiar com 8 casos ou mais de cada lado)
  const reps = F.filter(g => g.rep).map(g => { const best = [g, ...g.mates].map(h => ({ h, s: stumpScore(h.x, yr, h.f) })).filter(z => z.s).sort((u, w) => w.s.sc - u.s.sc)[0]; if (!best) return null;
    const h = best.h, mates = [g, ...g.mates].filter(z => z !== h); mates.forEach(z => { z.of = h; }); return { g: h, f: h.f, wi: h.wi, xv: h.x, rho: h.rho, mates, t: best.s.t }; }).filter(Boolean);
  const X = rows.map(r => designRow(r, reps)), beta = wls(X, y); if (!beta) return null;
  const res = y.map((v, i) => v - dot(X[i], beta)), sd = Math.sqrt(res.reduce((s, v) => s + v * v, 0) / Math.max(1, y.length - X[0].length));
  reps.forEach((q, j) => { q.beta = beta[1 + j]; });
  return { F, reps, X, y, beta, sd };
}
function rxBoot(R, M) {
  const B = 200, rng = rngFor('boot' + R.a.id + R.D), pids = [...new Set(R.rows.map(r => r.pid))], wks = [...new Set(R.rows.map(r => r.wk))];
  const pi = Object.fromEntries(pids.map((id, i) => [id, i])), wi = Object.fromEntries(wks.map((w, i) => [w, i])), draws = M.reps.map(() => []);
  for (let b = 0; b < B; b++) { const cp = new Array(pids.length).fill(0), cw = new Array(wks.length).fill(0);
    for (let i = 0; i < pids.length; i++) cp[Math.floor(rng() * pids.length)]++; for (let i = 0; i < wks.length; i++) cw[Math.floor(rng() * wks.length)]++;
    const be = wls(M.X, M.y, R.rows.map(r => cp[pi[r.pid]] * cw[wi[r.wk]])); if (be) M.reps.forEach((q, j) => draws[j].push(be[1 + j])); }
  M.reps.forEach((q, j) => { const d = draws[j].sort((x, y) => x - y), m = d.length, pc = f => d[Math.min(m - 1, Math.max(0, Math.round(f * (m - 1))))];
    q.ci95 = [pc(.025), pc(.975)]; q.ci80 = [pc(.1), pc(.9)];
    const mu = d.reduce((s, v) => s + v, 0) / m, se = Math.sqrt(d.reduce((s, v) => s + (v - mu) ** 2, 0) / Math.max(1, m - 1)) || 1e-9;
    q.se = se; q.p = Math.min(1, 2 * (1 - Phi(Math.abs(q.beta) / se)) * q.f.wins.length);   // aproximação normal do bootstrap; multiplica pelas janelas testadas
    const I = q.xv.map(v => v >= q.t ? 1 : 0), hi = R.rows.filter((r, i) => I[i]); q.nHi = hi.length; q.nLo = I.length - hi.length; q.pivHi = new Set(hi.map(r => r.pid)).size; q.wkHi = new Set(hi.map(r => r.wk)).size; });
  const ord = [...M.reps].sort((x, y) => x.p - y.p); let prev = 1; for (let i = ord.length - 1; i >= 0; i--) { prev = Math.min(prev, ord[i].p * ord.length / (i + 1)); ord[i].q = Math.min(1, prev); }   // Benjamini-Hochberg
}
function rxStable(R, M) {   // mesmo sinal na primeira e na segunda metade do período
  const ds = R.rows.map(r => r.d2).sort((a, b) => a - b), mid = ds[Math.floor(ds.length / 2)], half = h => R.rows.map(r => (h ? r.d2 > mid : r.d2 <= mid) ? 1 : 0);
  const fits = [wls(M.X, M.y, half(0)), wls(M.X, M.y, half(1))];
  M.reps.forEach((q, j) => { const ok = [0, 1].every(h => { const w = half(h); let nh = 0, nl = 0; q.xv.forEach((v, i) => { if (!w[i]) return; if (v >= q.t) nh++; else nl++; }); return nh >= 3 && nl >= 3; });
    q.stable = ok && fits.every(b => b && Math.sign(b[1 + j]) === Math.sign(q.beta)); });
}
function rxLevels(R) { const prior = PRIOR[R.a.id] || {};
  R.M.reps.forEach(q => { const ex = q.ci95[0] > 0 || q.ci95[1] < 0, ex80 = q.ci80[0] > 0 || q.ci80[1] < 0, enough = q.nHi >= 8 && q.nLo >= 8 && q.pivHi >= 3;
    let lv = !enough ? 'insuf' : ex && q.q < .1 ? (q.stable && (q.f.tipo !== 'Clima' || q.wkHi >= 3) ? 'forte' : 'moderada') : ex80 ? 'fraca' : 'nulo';
    if (['forte', 'moderada', 'fraca'].includes(lv) && prior[q.f.k] && Math.sign(prior[q.f.k]) !== Math.sign(q.beta)) lv = 'confirmar';
    q.level = lv; q.eff = Math.exp(q.beta) - 1; q.effCI = q.ci95.map(v => Math.exp(v) - 1); });
}
// camada 3: eficácia de Henderson-Tilton contra talhões-controle (sem aplicação contra o alvo na mesma janela, mesmo estádio e nível parecido)
const nearestObs = (obs, d, tol) => { let b = null; obs.forEach(o => { if (Math.abs(o.day - d) <= tol && (!b || Math.abs(o.day - d) < Math.abs(b.day - d))) b = o; }); return b; };
function rxHT(a, D) {
  const eps = .05 * a.nc, out = [];
  PIVOS.forEach(p => { const s = PEST[a.id][p.id]; if (!s) return; s.apps.forEach(ap => { if (!ap.before || !ap.after || ap.after.day > D) return;
    const db = ap.before.day, da = ap.after.day, cands = [];
    PIVOS.forEach(q => { if (q.id === p.id) return; const sq = PEST[a.id][q.id]; if (!sq) return; const cb = nearestObs(sq.obs, db, 3), ca = nearestObs(sq.obs, da, 3);
      if (!cb || !ca || ca.day <= cb.day || cb.v < .1 * a.nc || sq.apps.some(x => x.day > cb.day - 10 && x.day <= ca.day)) return;
      cands.push({ ratio: (ca.v + eps) / (cb.v + eps), same: (q.stage === 'jovem') === (p.stage === 'jovem'), near: cb.v >= .3 * ap.before.v }); });
    let use = cands.filter(c => c.same && c.near); if (use.length < 2) use = cands.filter(c => c.same); if (use.length < 2) use = cands;
    const ctrl = use.length >= 2 ? median(use.map(c => c.ratio)) : null, tr = (ap.after.v + eps) / (ap.before.v + eps), back = ap.backDay != null && ap.backDay <= D;
    out.push({ pid: p.id, ap, E: ctrl != null ? 1 - tr / ctrl : null, nCtrl: use.length, raw: ap.red, t: back ? ap.backDay - ap.day : D - ap.day, ev: back }); }); });
  return out;
}
function kmMedian(items) {   // dias até voltar ao NC (Kaplan-Meier; quem segue abaixo do NC entra como censurado)
  if (!items.length) return null; const ts = [...new Set(items.filter(i => i.ev).map(i => i.t))].sort((a, b) => a - b); let S = 1;
  for (const t of ts) { const n = items.filter(i => i.t >= t).length, d = items.filter(i => i.ev && i.t === t).length; S *= 1 - d / n; if (S <= .5) return { med: t }; }
  return { med: null, min: Math.max(...items.map(i => i.t)) };
}
function htGroups(list, keyFn, subFn, seed) {
  const G = {}; list.forEach(h => { const k = keyFn(h); (G[k] = G[k] || { k, sub: subFn ? subFn(h) : '', items: [] }).items.push(h); });
  return Object.values(G).map(g => { const v = g.items.filter(h => h.E != null).map(h => h.E), rng = rngFor('ht' + seed + g.k), bs = [];
    if (v.length >= 3) for (let b = 0; b < 200; b++) bs.push(median(v.map(() => v[Math.floor(rng() * v.length)]))); bs.sort((x, y) => x - y);
    return Object.assign(g, { n: g.items.length, nValid: v.length, E: v.length ? median(v) : null, ci: bs.length ? [bs[5], bs[194]] : null, piv: new Set(g.items.map(h => h.pid)).size, km: kmMedian(g.items), raw: median(g.items.map(h => h.raw).filter(x => x != null)) }); });
}
const htLevel = g => g.nValid >= 8 && g.piv >= 3 && g.ci && g.ci[0] > 0 ? 'forte' : g.nValid >= 5 && g.ci && g.ci[0] > 0 ? 'moderada' : g.nValid >= 3 ? 'fraca' : null;
// camada 4: risco de passar do NC em 7 dias, com a previsão do tempo; só mostra probabilidade se vencer a referência (repetir a última vistoria)
function predictRow(M, r, xs) { const x = designRow(r, M.reps, xs), gap = r.d2 - r.d1, mu = Math.log(r.v1 + r.eps) + dot(x, M.beta) * gap / 7, sig = Math.max(.05, M.sd * Math.sqrt(gap / 7));
  return { mu, p: 1 - Phi((Math.log(r.nc + r.eps) - mu) / sig) }; }
function rxRisk(a, D, R) {
  const M = R.M, eps = .05 * a.nc, T = D + 7, list = [];
  PIVOS.forEach(p => { const s = PEST[a.id][p.id]; if (!s) return; let o = null; for (const q of s.obs) { if (q.day <= D) o = q; else break; }
    const lastApp = s.apps.filter(x => x.day <= D).pop(), recent = lastApp && D - lastApp.day <= 10 ? lastApp : null, base = { pid: p.id };
    if (!o || D - o.day > 14) return list.push(Object.assign(base, { st: 'sem' }));
    if (o.v >= a.nc) return list.push(Object.assign(base, { st: 'acima', v: o.v, day: o.day, app: recent }));
    if (recent) return list.push(Object.assign(base, { st: 'ctl', v: o.v, day: o.day, app: recent }));
    const r = { pid: p.id, stage: p.stage, d1: o.day, d2: T, v1: o.v, eps, nc: a.nc, aval: 'A' }, xs = M.reps.map(q => { const v = fval(r, q.f, q.wi); return v == null ? -Infinity : v; });
    const pr = predictRow(M, r, xs), factors = M.reps.map((q, j) => ({ q, v: xs[j], on: xs[j] >= q.t })).filter(z => z.on && ['forte', 'moderada'].includes(z.q.level));
    list.push(Object.assign(base, { st: 'ok', v: o.v, day: o.day, prob: pr.p, pred: Math.exp(pr.mu) - eps, up: factors.filter(z => z.q.beta > 0).sort((u, w) => w.q.beta - u.q.beta).slice(0, 3), down: factors.filter(z => z.q.beta < 0).sort((u, w) => u.q.beta - w.q.beta).slice(0, 2) })); });
  const cut = D - 21, tr = R.rows.filter(r => r.d2 <= cut), te = R.rows.filter(r => r.d2 > cut); let gate = { ok: false, n: te.length };
  if (tr.length >= 24 && te.length >= 10) { const Mt = rxFit(tr.map(r => Object.assign({}, r))); if (Mt) { let bm = 0, bp = 0;
    te.forEach(r => { const xs = Mt.reps.map(q => { const v = fval(r, q.f, q.wi); return v == null ? -Infinity : v; }), y = r.v2 >= a.nc ? 1 : 0; bm += (predictRow(Mt, r, xs).p - y) ** 2; bp += ((r.v1 >= a.nc ? 1 : 0) - y) ** 2; });
    gate = { ok: bm < bp, bm: bm / te.length, bp: bp / te.length, n: te.length, ev: te.filter(r => r.v2 >= a.nc).length }; } }
  return { list, gate, T };
}
const RXC = new Map();
function rxGet(alvoId, D) {
  const key = alvoId + '|' + D; if (RXC.has(key)) return RXC.get(key);
  const a = ALVOS.find(x => x.id === alvoId), rows = rxRows(a, D), R = { a, D, rows, n: rows.length, piv: new Set(rows.map(r => r.pid)).size, wks: new Set(rows.map(r => r.wk)).size };
  R.nObs = PIVOS.reduce((s, p) => s + (PEST[a.id][p.id] ? PEST[a.id][p.id].obs.filter(o => o.day <= D).length : 0), 0);
  R.ht = rxHT(a, D); R.cold = R.n < 24 || R.piv < 3 || R.wks < 4;
  if (!R.cold) { const M = rxFit(rows); if (M) { R.M = M; rxBoot(R, M); rxStable(R, M); rxLevels(R); R.risk = rxRisk(a, D, R); } else R.cold = true; }
  RXC.set(key, R); if (RXC.size > 80) RXC.delete(RXC.keys().next().value); return R;
}
function rxHeat(R) {   // mapa de correlações: Spearman de cada variável × janela com o crescimento; intervalo de 90 % por bootstrap em blocos
  if (R.heat) return R.heat; const y = rxResid(R.rows), rng = rngFor('heat' + R.a.id + R.D), pids = [...new Set(R.rows.map(r => r.pid))], wks = [...new Set(R.rows.map(r => r.wk))], samples = [];
  for (let b = 0; b < 80; b++) { const cp = {}, cw = {}; pids.forEach(() => { const k = pids[Math.floor(rng() * pids.length)]; cp[k] = (cp[k] || 0) + 1; }); wks.forEach(() => { const k = wks[Math.floor(rng() * wks.length)]; cw[k] = (cw[k] || 0) + 1; });
    const ix = []; R.rows.forEach((r, i) => { const m = (cp[r.pid] || 0) * (cw[r.wk] || 0); for (let k = 0; k < m; k++) ix.push(i); }); if (ix.length > 10) samples.push(ix); }
  R.heat = RXF.map(f => ({ f, cells: f.wins.map((w, wi) => { const x = impute(R.rows.map(r => fval(r, f, wi))), rho = spear(x, y);
    const bs = samples.map(ix => spear(ix.map(i => x[i]), ix.map(i => y[i]))).filter(v => v != null).sort((p, q) => p - q), lo = bs[Math.floor(.05 * (bs.length - 1))], hi = bs[Math.ceil(.95 * (bs.length - 1))];
    return { w: w[0], rho, sig: rho != null && bs.length > 20 && (lo > 0 || hi < 0) }; }) }));
  return R.heat;
}


const LV={forte:["Forte"],moderada:["Moderada"],fraca:["Fraca"],confirmar:["A confirmar"]}; const shown=q=>!!LV[q.level];
function gabaritoRows(R, a, only) {
  const pl = PLANTED[a.id] || {}, px = PROXY[a.id] || {}; let hit = 0, tot = 0, fp = 0, noise = 0;
  const rows = RXF.filter(f => !only || f.k === only).map(f => { const q = R.M.reps.find(x => x.f.k === f.k), mate = q ? null : R.M.reps.find(x => x.mates.some(m => m.f.k === f.k));
    const planted = pl[f.k] || 0, proxy = px[f.k]; let found, ok = '';
    if (q) found = shown(q) ? (q.beta > 0 ? 'sobe' : 'desce') + ' · ' + LV[q.level][0].toLowerCase() : q.level === 'insuf' ? 'poucos casos' : 'sem efeito claro';
    else if (mate) found = 'anda junto de ' + mate.f.t.toLowerCase(); else found = '—';
    if (planted) { tot++; let good;
      if (q) good = shown(q) && q.level !== 'confirmar' && Math.sign(q.beta) === planted;
      else if (mate) { const m = mate.mates.find(z => z.f.k === f.k), c = spear(mate.xv, m.x); good = shown(mate) && mate.level !== 'confirmar' && Math.sign(mate.beta) * Math.sign(c || 1) === planted; }
      if (good) hit++; ok = good ? '✓' : '✗ não achou'; }
    else if (!proxy) { noise++; const bad = q && ['forte', 'moderada'].includes(q.level); if (bad) fp++; ok = bad ? '✗ falso positivo' : '✓'; }
    else ok = 'não conta';
    return '<tr><td>' + f.t + '</td><td>' + (planted > 0 ? 'sobe' : planted < 0 ? 'desce' : proxy ? 'junto de ' + RXK(proxy).t.toLowerCase() : 'nenhum') + '</td><td>' + found + '</td><td>' + ok + '</td></tr>'; }).join('');
  return { rows, hit, tot, fp, noise };
}

console.log(JSON.stringify(ALVOS.map(a=>{const R=rxGet(a.id,DAYS);const g=gabaritoRows(R,a);delete g.rows;return {alvo:a.id,gabarito:g,gate:R.risk.gate}}),null,2));
})();
