// AGUA-SOLO-IRR · balanço com teto da CAD na ordem do tempo (Codex 6252809331, S2): sem navegador, arquivo integral irrigacao_estado.js,
// fronteira soloAguaDo/soloCAD controlada e cenário sintético. Oráculo independente: balanço diário FAO-56 (eq. 85–86) escrito aqui.
// Uso: node agua_irr_unit.js   (IRR_SOURCE=<outro irrigacao_estado.js> para a contraprova)
const fs = require('node:fs'), vm = require('node:vm'), A = require('node:assert/strict');
const source = fs.readFileSync(process.env.IRR_SOURCE || __dirname + '/irrigacao_estado.js', 'utf8');
let ok = 0, fail = 0;
function test(nome, fn) { try { fn(); ok++; console.log('OK   ' + nome); } catch (e) { fail++; console.log('FALHA ' + nome + ' :: ' + e.message); } }
function ctx(cad) {
  const c = { console, CAD: cad }; vm.createContext(c);
  vm.runInContext(`const store={}; const localStorage={getItem:k=>store[k]||null,setItem:(k,v)=>{store[k]=String(v)},removeItem:k=>{delete store[k]}};
    var cenGet=()=>({ordens:{}}); var soloAguaDo=()=>(CAD===null?null:{id:'CAD-SINT'}); var soloCAD=()=>({v:CAD===null?null:String(CAD),nc:'sem CAD'});
    var IRR_SOLO0={agua:[],fdep:{}};\n` + source, c);
  c.run = js => vm.runInContext(js, c); return c;
}
// setor sintético: 10 ha, eficiência 100 %; balanço de b.dias dias antes de hoje; aplicação no dia k (minuto k·1440 + 480)
function setor(c, bal) { c.run(`var s={setores:{P1:{faz:'SR',nome:'P1',cult:'Milho',ha:10,efic:100,limiar:3,lmax:12,vazao:100,tipo:'gotejo',bal:${JSON.stringify(bal)}}},faz:{SR:{nome:'Sintética'}},ordens:{},fert:{},fontes:{}}`); }
const ap = (k, mm, cob) => ({ os: 'SINT-' + k, q: k * 1440 + 480, vol: Math.round(mm * (cob || 10) * 10), ha: 10, cob: cob || 10, ef: 100 });
// oráculo: Dr,i = clip(Dr,i−1 + ETc − P − I, 0, CAD), dia a dia; ETc nos dias −dias..−1; aplicação antes do início entra no 1º dia
function oraculo(bal, cad, aps) {
  const k1 = -bal.dias, et = bal.dias ? bal.etc / bal.dias : 0; let kEnd = -1; aps.forEach(a => { kEnd = Math.max(kEnd, Math.max(k1, Math.floor(a.q / 1440))); });
  let D = Math.min(cad, Math.max(0, bal.d0)); const fim = {};
  for (let k = k1; k <= kEnd; k++) { let v = D + (k <= -1 ? et : 0); aps.forEach(a => { if (Math.max(k1, Math.floor(a.q / 1440)) === k && a.cob >= 10) v -= a.vol / (10 * a.cob) * a.ef / 100; }); D = Math.min(cad, Math.max(0, v)); fim[k] = D; }
  return { d: D, fim };
}
const near = (a, b, m) => A.ok(Math.abs(a - b) < 1e-6, `${m}: ${a} ≠ ${b}`);

test('C1 contraexemplo do Codex: d0 8,4 com CAD 6 mostra 6; aplicar os 6 mm líquidos zera (antes ficava 2,4)', () => {
  const c = ctx(6); setor(c, { d0: 8.4, etc: 0, pef: 0, dias: 0, ap: [] }); near(c.run(`irrDef(s,'P1')`), 6, 'antes');
  c.run(`s.setores.P1.bal.ap.push(${JSON.stringify(ap(0, 6))})`); near(c.run(`irrDef(s,'P1')`), 0, 'depois');
  A.equal(c.run(`irrDemanda(s,'P1').liq`), 0, 'sem nova demanda');
});
test('C2 a necessidade exibida, aplicada, zera o déficit (lâmina líquida = déficit mostrado)', () => {
  const c = ctx(6); setor(c, { d0: 8.4, etc: 7, pef: 0, dias: 7, ap: [] }); const liq = c.run(`irrDemanda(s,'P1').liq`); near(liq, 6, 'necessidade');
  c.run(`s.setores.P1.bal.ap.push(${JSON.stringify(ap(0, liq))})`); near(c.run(`irrDef(s,'P1')`), 0, 'depois de aplicar a necessidade');
});
test('C3 ETc depois da aplicação não se perde: aplicação no dia −5, ETc 1 mm/dia, CAD 6 (oráculo diário)', () => {
  const bal = { d0: 8.4, etc: 7, pef: 0, dias: 7, ap: [ap(-5, 6)] }; const c = ctx(6); setor(c, bal);
  const o = oraculo(bal, 6, bal.ap); near(c.run(`irrDef(s,'P1')`), o.d, 'hoje'); near(o.d, 5, 'oráculo: zera no dia −5 e soma 5 dias de ETc');
});
test('C4 série e déficit de hoje coerentes: cada fim de dia igual ao oráculo e o último dia = hoje sem aplicação hoje', () => {
  const bal = { d0: 4, etc: 14, pef: 0, dias: 7, ap: [ap(-4, 5), ap(-2, 3)] }; const c = ctx(6); setor(c, bal); c.run(`s.setores.P1.bal.ini=-7*1440`);
  const o = oraculo(bal, 6, bal.ap); const se = c.run(`JSON.stringify(irrSerie(s,'P1'))`); JSON.parse(se).forEach(p => near(p.v, o.fim[p.k], 'dia ' + p.k));
  near(c.run(`irrDef(s,'P1')`), o.fim[-1], 'hoje = fim de ontem');
});
test('C5 parcial zera só a faixa: déficit do pivô fica; a faixa coberta vai a 0', () => {
  const c = ctx(6); setor(c, { d0: 8.4, etc: 0, pef: 0, dias: 0, ap: [ap(0, 6, 4)] }); near(c.run(`irrDef(s,'P1')`), 6, 'pivô');
  const fx = c.run(`JSON.stringify(irrFaixaCob(s,'P1'))`); near(JSON.parse(fx).d, 0, 'faixa');
});
test('C6 sem CAD calculável: o balanço de antes (8,4 − 6 = 2,4), sem passo diário', () => {
  const c = ctx(null); setor(c, { d0: 8.4, etc: 0, pef: 0, dias: 0, ap: [] }); near(c.run(`irrDef(s,'P1')`), 8.4, 'antes');
  c.run(`s.setores.P1.bal.ap.push(${JSON.stringify(ap(0, 6))})`); near(c.run(`irrDef(s,'P1')`), 2.4, 'depois');
});
test('C7 água acima da CAD drena: d0 2, aplicação de 6 mm no dia −6 e 7 mm de ETc em 7 dias dão 5 (oráculo), não 3', () => {
  const bal = { d0: 2, etc: 7, pef: 0, dias: 7, ap: [ap(-6, 6)] }; const c = ctx(20); setor(c, bal); const o = oraculo(bal, 20, bal.ap);
  near(c.run(`irrDef(s,'P1')`), o.d, 'hoje'); near(o.d, 5, 'oráculo');
});
console.log(`RESULTADO: ${ok}/${ok + fail} ok`); process.exit(fail ? 1 : 0);
