/* ===== EX-54 · Frentes de trabalho (proprietário, 18/10/2026: "o agrupamento de OS e talhoes semelhantes para facilitar execucao e logistica
   contínua na fazenda esta muito ruim"; prompt-safrion-frentes-trabalho.md). Especificação: docs/os-agrupa/OS-AGRUPA-2.md.
   Frente = uma família de implemento percorrendo uma sequência de talhões. Só calcula e sugere; não grava, não aprova, não libera, não reserva.
   Entrada: linhas normalizadas pela tela (O.S. não encerradas do recorte) e a geometria da fazenda (OS_GEO). ===== */
const FR_UN = { mL: ['L', 1e-3], g: ['kg', 1e-3], L: ['L', 1], kg: ['kg', 1], un: ['un', 1] };
function frDose(dose, un){ const u = FR_UN[un] || [un, 1]; return { un: u[0], dose: Math.round(Number(dose) * u[1] * 1e6) / 1e6 }; }
function frNum(x, d){ return Number(x).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: d === undefined ? 2 : d }); }
const FR_ADJ = /adjuvante|óleo|oleo|espalhante|surfactante|redutor de deriva/i;
const FR_HERB = /glifosato|2,4-d|dicamba|paraquat|diquat|glufosinato|atrazina|imazet|clorimurom|herbicida/i;
// calda exata: produtos com dose e unidade canônicas (a ordem da tela não muda a calda; 1.000 mL/ha = 1 L/ha; kg ≠ L) e a vazão
function frCaldaP(r){ return (r.ins || []).map(i => { const d = frDose(i.dose, i.un); return i.p + '|' + d.dose + '|' + d.un; }).sort().join(' + '); }
function frCalda(r){ return frCaldaP(r) + (r.liquido && r.vazao > 0 ? ' @' + r.vazao : ''); }
// mesma calda: mesmos produtos e doses e a mesma vazão; vazão ainda não definida não separa (a O.S. fica com a pendência "Definir vazão")
function frMesma(a, b){ return !!a && !!b && frCaldaP(a) === frCaldaP(b) && (!(a.vazao > 0) || !(b.vazao > 0) || a.vazao === b.vazao); }
function frCaldaTxt(r){ return (r.ins || []).slice().sort((a, b) => a.p.localeCompare(b.p)).map(i => i.p + ' ' + frNum(i.dose) + ' ' + i.un + '/ha').join(' + ') || 'sem insumo'; }
// compatibilidade dentro da família (prompt EX-54 §3): pulverização e a lanço pelos produtos ativos (adjuvante e dose não separam: viram troca de
// calda ou nova regulagem); plantio e demais pela cultura (cultivar ou adubo diferente vira troca com limpeza registrada)
function frCompat(r){
  if (r.fam === 'Pulverização' || r.fam === 'A lanço') return (r.ins || []).map(i => i.p).filter(p => !FR_ADJ.test(p)).sort().join(' + ') || r.atv || '';
  return r.cultura || '';
}
function frHerb(r){ return r.fam === 'Pulverização' && (r.ins || []).some(i => FR_HERB.test(i.p)); }
// distância entre centros: geometria real (lon/lat) em metros, linha reta; desenho sem escala só ordena (m = null)
function frDist(geo, a, b){
  const p = Array.isArray(a) ? a : geo && geo.c && geo.c[a], q = Array.isArray(b) ? b : geo && geo.c && geo.c[b]; if (!p || !q) return null;
  if (!geo || geo.tipo !== 'lonlat') return { u: Math.hypot(p[0] - q[0], p[1] - q[1]), m: null };
  const R = 6371008.8, r = x => x * Math.PI / 180, dLa = r(q[1] - p[1]), dLo = r(q[0] - p[0]);
  const h = Math.sin(dLa / 2) ** 2 + Math.cos(r(p[1])) * Math.cos(r(q[1])) * Math.sin(dLo / 2) ** 2;
  const m = 2 * R * Math.asin(Math.sqrt(h)); return { u: m, m };
}
const FR_FIM = '9999-12-31';
// R3 · período: junta as O.S. cujas janelas se encostam ou se cruzam (execução em sequência); a que começa depois do fim de todas abre outra frente
function frPorJanela(rows){
  const ord = rows.slice().sort((a, b) => (a.ini || '').localeCompare(b.ini || '') || (a.fim || FR_FIM).localeCompare(b.fim || FR_FIM) || a.id.localeCompare(b.id));
  const out = []; let g = [], fimG = '';
  ord.forEach(r => { if (g.length && r.ini && fimG && r.ini > fimG) { out.push(g); g = []; fimG = ''; }
    g.push(r); const f = r.fim || FR_FIM; if (!fimG || f > fimG) fimG = f; });
  if (g.length) out.push(g); return out;
}
// R4 · ordem: herbicida sempre no fim; entre as demais, a janela que fecha antes; no empate, seguir na mesma calda e depois o talhão mais perto
// (do anterior; a primeira, a partir da sede quando houver, senão da ponta do conjunto, para varrer sem voltar)
function frOrdem(rows, geo){
  const pts = rows.map(r => geo && geo.c && geo.c[r.tkey]).filter(Boolean);
  const centro = pts.length ? [pts.reduce((s, p) => s + p[0], 0) / pts.length, pts.reduce((s, p) => s + p[1], 0) / pts.length] : null;
  const origem = geo && geo.sede ? geo.sede : null;
  const resto = rows.slice(), seq = [];
  const pos = r => geo && geo.c && geo.c[r.tkey];
  const dist = (a, r) => { const d = a && pos(r) ? frDist(geo, a, pos(r)) : null; return d ? d.u : Infinity; };
  while (resto.length){
    const nh = resto.filter(r => !r.herb), cand = nh.length ? nh : resto;
    const fimMin = cand.reduce((m, r) => (r.fim || FR_FIM) < m ? (r.fim || FR_FIM) : m, FR_FIM), emp = cand.filter(r => (r.fim || FR_FIM) === fimMin);
    const prev = seq.length ? seq[seq.length - 1] : null;
    emp.sort((a, b) => {
      if (prev){ const ca = frMesma(a, prev) ? 0 : 1, cb = frMesma(b, prev) ? 0 : 1; if (ca !== cb) return ca - cb; return dist(pos(prev), a) - dist(pos(prev), b) || a.id.localeCompare(b.id); }
      if (origem) return dist(origem, a) - dist(origem, b) || a.id.localeCompare(b.id);
      if (centro) return dist(centro, b) - dist(centro, a) || a.id.localeCompare(b.id);   // ponta do conjunto
      return b.area - a.area || a.id.localeCompare(b.id);
    });
    const r = emp[0]; resto.splice(resto.indexOf(r), 1);
    const d = prev ? (pos(prev) && pos(r) ? frDist(geo, pos(prev), pos(r)) : null) : (origem && pos(r) ? frDist(geo, origem, pos(r)) : null);
    seq.push(Object.assign({ leg: d ? d.m : null, legDe: prev ? prev.talhao : (origem && geo.sedeNome) || null }, r));
  }
  return seq;
}
// cargas fechadas por O.S. (vale hoje) e as que a calda contínua daria (só com a decisão do RT sobre o rateio: EX-54 §7)
function frCargas(seq){
  const liq = seq.filter(r => r.liquido && r.vazao > 0 && r.tanque > 0);
  if (!liq.length) return { porOS: null, continuas: null, tanque: null, todas: false };
  const porOS = liq.reduce((s, r) => s + Math.ceil(r.area * r.vazao / r.tanque - 1e-9), 0);
  let continuas = 0, i = 0;
  while (i < seq.length){ let j = i, vol = 0; const T = seq[i].tanque;
    while (j < seq.length && frMesma(seq[j], seq[i]) && seq[j].liquido && seq[j].vazao > 0 && seq[j].tanque === T) { vol += seq[j].area * seq[j].vazao; j++; }
    if (j === i) { i++; continue; } continuas += Math.ceil(vol / T - 1e-9); i = j; }
  return { porOS, continuas, tanque: liq[0].tanque, todas: liq.length === seq.length };
}
// trocas ao longo da sequência: calda (pulverização), semente ou adubo (plantio: limpeza da plantadeira), regulagem (a lanço); herbicida fecha com
// tríplice lavagem registrada
function frTrocas(seq){
  const out = [];
  for (let i = 1; i < seq.length; i++){ const a = seq[i - 1], b = seq[i]; if (frMesma(a, b)) continue;
    const t = b.fam === 'Pulverização' ? 'Troca de calda antes de ' + b.talhao + ': ' + frCaldaTxt(b) + (a.herb && !b.herb ? ' · tríplice lavagem registrada antes' : '')
      : b.fam === 'Plantio' ? 'Troca de semente ou adubo antes de ' + b.talhao + ': limpeza da plantadeira registrada (pureza)'
      : 'Nova regulagem antes de ' + b.talhao + ': ' + frCaldaTxt(b);
    out.push({ antes: i + 1, t }); }
  if (seq.length && seq[seq.length - 1].herb) out.push({ antes: seq.length + 1, t: 'Fim com herbicida: tríplice lavagem registrada antes de voltar a cultura sensível' });
  return out;
}
const FR_ORDEM_FAM = { 'Pulverização': 1, 'A lanço': 2, 'Plantio': 3, 'Colheita': 4, 'Tratos manuais': 5 };
function osFrentes(rows, geo){
  rows = rows.map(r => Object.assign({}, r, { calda: frCalda(r), herb: frHerb(r), compat: frCompat(r) }));
  const grupos = new Map(), soltas = [];
  rows.forEach(r => { if (!r.fam) { soltas.push({ id: r.id, motivo: 'Sem conjunto que percorra talhões (vai pelo pivô ou não usa implemento)' }); return; }
    const k = [r.faz, r.fam, r.compat].join(' ¦ '); if (!grupos.has(k)) grupos.set(k, []); grupos.get(k).push(r); });
  const frentes = [];
  grupos.forEach(gr => frPorJanela(gr).forEach(jg => {
    if (jg.length < 2){ soltas.push({ id: jg[0].id, motivo: gr.length > 1 ? 'Janela sem encontro com as outras da mesma família' : 'Sem outra O.S. da mesma família e produto neste período' }); return; }
    const seq = frOrdem(jg, geo), r0 = seq[0], caldas = seq.reduce((l, r) => l.some(x => frMesma(x, r)) ? l : l.concat([r]), []);
    const ini = seq.map(r => r.ini).filter(Boolean).sort()[0] || '', fim = seq.map(r => r.fim).filter(Boolean).sort().pop() || '';
    const prods = {}; seq.forEach(r => (r.ins || []).forEach(i => { const d = frDose(i.dose, i.un), k = i.p + '|' + d.un; prods[k] = prods[k] || { p: i.p, un: d.un, q: 0 }; prods[k].q += d.dose * r.area; }));
    const lonlat = !!geo && geo.tipo === 'lonlat', ult = seq[seq.length - 1];
    const volta = lonlat && geo.sede && geo.c[ult.tkey] ? frDist(geo, geo.c[ult.tkey], geo.sede).m : 0;
    const km = lonlat && seq.every(r => r.leg !== null) ? (seq.reduce((s, r) => s + r.leg, 0) + volta) / 1000 : null;
    // cada O.S. sozinha: ida e volta da sede (só com a sede no mapa)
    const kmSo = lonlat && geo.sede && seq.every(r => geo.c[r.tkey]) ? seq.reduce((s, r) => s + 2 * frDist(geo, geo.sede, geo.c[r.tkey]).m, 0) / 1000 : null;
    const rend = seq.every(r => r.rend > 0) ? seq.reduce((s, r) => s + r.area / r.rend, 0) : null;
    const um = { 'Pulverização': ['mesma calda', ' caldas do mesmo produto, em sequência'], 'Plantio': ['mesma semente e adubo', ' sementes ou adubos, com limpeza entre eles'] }[r0.fam] || ['mesmo produto e dose', ' regulagens do mesmo produto, em sequência'];
    const porque = [caldas.length === 1 ? um[0] : caldas.length + um[1], 'janelas que se cruzam ou se seguem'];
    if (km !== null) porque.push('talhões vizinhos');
    frentes.push({ k: seq.map(r => r.id).join('+'), faz: r0.faz, fam: r0.fam, compat: r0.compat, atv: r0.atv, cultura: r0.cultura,
      seq: seq.map((r, i) => Object.assign({ ordem: i + 1 }, r)), ids: seq.map(r => r.id), caldas: caldas.length, trocas: frTrocas(seq),
      liberadas: seq.filter(r => r.liberada).map(r => r.id), pendentes: seq.filter(r => !r.liberada).map(r => r.id),
      area: Math.round(seq.reduce((s, r) => s + r.area, 0) * 1e4) / 1e4, janela: { ini, fim }, km, kmSo, horas: rend, cargas: frCargas(seq), porque,
      herb: seq.some(r => r.herb), produtos: Object.values(prods).map(x => Object.assign(x, { q: Math.round(x.q * 1e4) / 1e4 })) });
  }));
  frentes.sort((a, b) => (FR_ORDEM_FAM[a.fam] || 9) - (FR_ORDEM_FAM[b.fam] || 9) || (a.janela.fim || FR_FIM).localeCompare(b.janela.fim || FR_FIM) || b.area - a.area || a.k.localeCompare(b.k));
  return { frentes, soltas };
}
// família pelo implemento exigido (EX-54 §2): pela alocação, senão pela operação; fertirrigação e irrigação vão pelo pivô (sem frente)
function frFamilia(implClasse, texto){
  const c = String(implClasse || ''), t = String(texto || '');
  if (/fertirriga|irriga/i.test(t)) return null;
  if (/pulveriz|turbo|atomiz/i.test(c)) return 'Pulverização';
  if (/plantadeira|semeadora|sulcador/i.test(c)) return 'Plantio';
  if (/distribuidor|lanço/i.test(c)) return 'A lanço';
  if (/colhed/i.test(c)) return 'Colheita';
  if (/pulveriz|dessec|fungic|herbic|insetic|acaric|controle de/i.test(t)) return 'Pulverização';
  if (/plantio|semeadura/i.test(t)) return 'Plantio';
  if (/lanço|calag|gessag|aduba/i.test(t)) return 'A lanço';
  if (/colheita/i.test(t)) return 'Colheita';
  if (/sexagem|desbaste|desbrota|tratos|poda|limpeza/i.test(t)) return 'Tratos manuais';
  return null;
}
if (typeof module !== 'undefined') module.exports = { osFrentes, frOrdem, frCargas, frPorJanela, frCalda, frMesma, frCompat, frDist, frDose, frFamilia, frTrocas, frHerb };
