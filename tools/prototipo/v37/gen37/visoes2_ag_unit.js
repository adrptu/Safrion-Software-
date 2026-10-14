// VISOES-2 · "Agrupar por" no g2lib, sem navegador: node visoes2_ag_unit.js (dados sintéticos)
// A1–A3: a trilha sobrevive ao endereço com "/", "%", "&", "+" e acento (Codex 6168779649, achado 1).
// A4–A7: o filtro de Talhão limita os grupos do nível Talhão aos escolhidos, sem perder a O.S. de dois talhões (achado 2).
// VISOES_G2LIB=<arquivo> roda contra outro g2lib (o anterior, para ver o vermelho).
const fs = require('fs'), path = require('path');
const arq = process.env.VISOES_G2LIB || path.join(__dirname, 'g2lib.js');
const src = fs.readFileSync(arq, 'utf8');
const NOMES = ['g2agUrl', 'g2agTrilha', 'g2agRows', 'g2agLer'];
// location falso: o caminho real de leitura (g2agLer) usa location.search, como no navegador
const G = new Function('const G2_GLOSS=[]; var location={search:"",pathname:"/OS.dc.html",hash:""};\n' + src + '\nreturn {__loc:(s)=>{location.search=s;},' + NOMES.map(n => n + ': (typeof ' + n + "==='function'?" + n + ':null)').join(',') + '};')();
let ok = 0, falhas = 0;
const chk = (nome, f, extra) => { let c = false, x, e2; try { c = !!f(); } catch (e) { x = String(e && e.message || e); } try { e2 = extra && extra(); } catch (e) { e2 = String(e.message); }
  if (c) { ok++; console.log('OK  ' + nome); } else { falhas++; console.log('FALHOU ' + nome + (x ? ' · erro: ' + x : '') + (e2 !== undefined ? ' · ' + JSON.stringify(e2) : '')); } };
const F = (n) => { if (!G[n]) throw new Error(n + ' ausente no g2lib'); return G[n]; };
// leitura como o navegador faz: o endereço gravado volta como location.search
const ida = (t) => { const u = F('g2agUrl')('/OS.dc.html', '?theme=dark', '#x', { d: 'quando', t }); return u.slice(u.indexOf('?'), u.indexOf('#')); };
const volta = (t) => F('g2agTrilha')(ida(t));
const T1 = ['Safra 2026/27', 'Março de 2027'];
chk('A1 "Safra 2026/27" ida → endereço → leitura idêntica (2 níveis, não 3)', () => JSON.stringify(volta(T1)) === JSON.stringify(T1), () => [ida(T1), volta(T1)]);
const T2 = ['100% & mais', 'São João + Ré', 'a/b/c'];
const SPQ = { id: 'g_q', cols: [{ k: 'id', l: 'O.S.' }], ag: [{ pq: 'quando', l: 'Início', niv: ['Safra', 'Mês', 'Semana'] }] };
const leAg = (t) => { G.__loc(ida(t)); const self = { state: { g2: {} } }; const a = F('g2agLer')(self, SPQ); return a && a.t; };
chk('A1b caminho real (g2agLer com o endereço gravado): a trilha "Safra 2026/27 › Março de 2027" volta igual', () => JSON.stringify(leAg(T1)) === JSON.stringify(T1), () => leAg(T1));
chk('A2 "%", "&", "+", acento e várias "/" voltam iguais; theme preservado', () => JSON.stringify(volta(T2)) === JSON.stringify(T2) && new URLSearchParams(ida(T2)).get('theme') === 'dark', () => [ida(T2), volta(T2)]);
chk('A3 sem trilha: lista vazia; ag sem trilha não grava "trilha="', () => volta([]).length === 0 && ida([]).indexOf('trilha=') < 0, () => ida([]));
// agrupamento por Onde (Fazenda › Talhão) com filtro na coluna Talhão (multi)
const SP = { id: 'g_t', cols: [{ k: 'id', l: 'O.S.' }, { k: 'tal', l: 'Talhão', multi: true }, { k: 'area', l: 'Área', agg: 'sum' }],
  ag: [{ pq: 'onde', l: 'Talhão', niv: ['Fazenda', 'Talhão'], fc: ['', 'tal'], um: 'O.S.', plural: 'O.S.' }] };
const linha = (id, tals, area) => ({ id, v: { id, area }, s: { id, tal: tals.join(', ') }, m: { tal: tals.map(t => ({ id: t, l: t })) }, g: { onde: ['Lagoa', tals] } });
const ROWS = [linha('OS-1', ['T1', 'T2'], 10), linha('OS-2', ['T2'], 5), linha('OS-3', ['T3'], 7)];
const grupos = (f) => { const self = { state: { g2: { g_t: { ag: { d: 'onde', t: [] }, f } } } };
  const R = F('g2agRows')(self, SP, { ag: { d: 'onde', t: [] }, f, agx: 'x' }, ROWS);
  return R.rows.map(r => [r.grp.k, r.v.area, r.kids.map(k => k.id.split('@')[0]).join(',')]); };
chk('A4 filtro Talhão = T1: só o grupo T1 (OS-1, área 10); T2 não reaparece', () => JSON.stringify(grupos({ tal: ['T1'] })) === JSON.stringify([['T1', 10, 'OS-1']]), () => grupos({ tal: ['T1'] }));
chk('A5 filtro T1 + T2: grupos T1 (OS-1) e T2 (OS-1, OS-2), sem T3', () => JSON.stringify(grupos({ tal: ['T1', 'T2'] })) === JSON.stringify([['T1', 10, 'OS-1'], ['T2', 15, 'OS-1,OS-2']]), () => grupos({ tal: ['T1', 'T2'] }));
chk('A6 sem filtro: T1, T2 e T3 com a O.S. de dois talhões nos dois', () => JSON.stringify(grupos({})) === JSON.stringify([['T1', 10, 'OS-1'], ['T2', 15, 'OS-1,OS-2'], ['T3', 7, 'OS-3']]), () => grupos({}));
chk('A7 descer em T1 sob o filtro T1: a linha da O.S. continua inteira (os dois talhões no detalhe)', () => {
  const self = { state: { g2: {} } }, st = { ag: { d: 'onde', t: ['Lagoa', 'T1'] }, f: { tal: ['T1'] } }; self.state.g2.g_t = st;
  const R = F('g2agRows')(self, SP, st, ROWS); return R.rows.length === 1 && R.rows[0].id === 'OS-1' && R.rows[0].m.tal.length === 2; });
chk('A8 O.S. sem talhão (lista vazia) entra no grupo "Sem talhão"; Σ das O.S. distintas dos grupos = total', () => {
  const rows = ROWS.concat([{ id: 'OB-9', v: { id: 'OB-9', area: 0 }, s: { id: 'OB-9', tal: '' }, m: { tal: [] }, g: { onde: ['Lagoa', []] } }]);
  const self = { state: { g2: { g_t: { ag: { d: 'onde', t: [] } } } } }; const R = F('g2agRows')(self, SP, { ag: { d: 'onde', t: [] }, agx: 'x' }, rows);
  const ids = new Set(); R.rows.forEach(g => g.kids.forEach(k => ids.add(k.id.split('@')[0])));
  return R.rows.some(g => g.grp.k === 'Sem talhão' && g.kids.length === 1) && ids.size === rows.length; }, () => { const self = { state: { g2: {} } };
  return 'ver A8'; });
console.log(`TOTAL ${ok + falhas} · OK ${ok} · FALHAS ${falhas}`);
process.exit(falhas ? 1 : 0);
