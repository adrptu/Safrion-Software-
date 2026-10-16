// biblioteca das sondas da revisão (independente do ben_prop.js): MUD, oráculo de conservação e utilidades
const CX = BENC.cx.item, IG = 'Igor', PA = 'Paula', AN = 'Ana', RU = 'Rui', EPS = 1e-9;
const LOG = [];
function zMUD(c, fn) { const x = cenClone(c); let r; try { r = fn(x) || {}; } catch (e) { r = { erro: String(e.message || e) }; }
  if (!r.erro && !r.nada) { Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); } return r; }
function zStep(c, nome, fn) { const r = zMUD(c, fn); LOG.push({ nome, ok: !r.erro, msg: (r.erro || r.msg || '').slice(0, 400) }); return r; }
const zLotesCx = c => Object.values(c.lotes).filter(l => l.prod === CX);
const zLinhas = c => Object.values(c.reqs).flatMap(r => r.itens.filter(i => i.prod === CX).map(it => ({ r, it, o: c.ordens[r.os] })));
const T0 = (() => { const c = CEN0; return zLotesCx(c).reduce((a, l) => a + l.fisico, 0) + zLinhas(c).reduce((a, x) => a + x.it.custodia + x.it.consumido, 0); })();
function resTotO(c, rid) { const s0 = CEN0.reqs[rid], i0 = s0 && s0.itens.find(i => i.prod === CX); const b = i0 ? (s0.estado === 'Reservada' ? i0.solicitado : (i0.entregue || 0)) : 0;
  return b + c.movs.filter(m => m.req === rid && m.prod === CX && (m.tipo === 'reserva' || m.tipo === 'reserva-baixa')).reduce((a, m) => a + (m.tipo === 'reserva' ? m.qtd : -m.qtd), 0); }
const ownO = (c, x) => Math.max(0, resTotO(c, x.r.id) - x.it.entregue);
const pendO = it => it.solicitado - (it.dispensado || 0) - it.consumido - it.custodia;
function zOraculo(c) { const V = [];
  zLotesCx(c).forEach(l => { if (l.fisico < -EPS || l.quarentena < -EPS || l.reservado < -EPS || l.quarentena > l.fisico + EPS) V.push(['lote', l.lote, l.fisico, l.quarentena, l.reservado]);
    const r = zLinhas(c).filter(x => x.it.lote === l.lote && x.o && x.o.etapa !== 'Encerradas').reduce((a, x) => a + ownO(c, x), 0);
    if (Math.abs(r - l.reservado) > EPS) V.push(['reserva≠Σown', l.lote, l.reservado, r]); });
  zLinhas(c).forEach(x => { const it = x.it; if (Math.abs(it.entregue - it.consumido - it.custodia - it.devolvido) > EPS) V.push(['linha', x.r.id, it]);
    if (pendO(it) < -EPS) V.push(['pend<0', x.r.id, pendO(it)]);
    if (benEh(x.o) && ['Liberadas', 'Em execução', 'Em conferência'].indexOf(x.o.etapa) >= 0 && Math.abs(Math.max(0, pendO(it)) - ownO(c, x)) > EPS) V.push(['pend≠own', x.r.id, pendO(it), ownO(c, x)]);
    if (benEh(x.o) && x.o.etapa === 'Encerradas' && (it.custodia > EPS || pendO(it) > EPS || ownO(c, x) > EPS)) V.push(['encerrada', x.r.id, it]); });
  const T = zLotesCx(c).reduce((a, l) => a + l.fisico, 0) + zLinhas(c).reduce((a, x) => a + x.it.custodia + x.it.consumido, 0);
  const T1 = T0 + c.movs.filter(m => m.prod === CX && (m.tipo === 'recebimento-nf' || m.tipo === 'ajuste')).reduce((a, m) => a + m.qtd, 0);
  if (Math.abs(T - T1) > EPS) V.push(['conservação', T, T1]);
  return V; }
const zLot = (c, l) => { const x = c.lotes[CX + '|' + l]; return x ? [x.fisico, x.quarentena, x.reservado, x.quarRep || 0] : null; };
const zLin = (c, o) => benLinhas(c, c.ordens[o]).map(x => ({ rid: x.rid, lote: x.it.lote, sol: x.it.solicitado, ent: x.it.entregue, cust: x.it.custodia, cons: x.it.consumido, dev: x.it.devolvido, disp: x.it.dispensado || 0, pend: cenSaldoEntregar(x.it) }));
function zBruto(cx, fat) { const r0 = benRota('PACK-FRU|3'); return prSoma([prMul(cx, prMul(BENC.cx.massa, fat || '1')), benTara(cx, 0, r0)]); }
const zSP = (c, o, cx, cl, sub) => benSaida(c, o, { fluxo: 'Produto', classe: cl || 'A', cx, bruto: zBruto(cx), subst: sub || '', motivo: 'sonda' }, IG);
const zSD = (c, o, kg, sub) => benSaida(c, o, { fluxo: 'Descarte', destino: 'Compostagem', kg, subst: sub || '', motivo: 'sonda' }, IG);
const zNF = (c, lote, q, doc, apto, rid) => { const n0 = c.movs.length; const r = cenReceber(c, CX, lote, q, 'un', 'Packing', '—', doc, apto !== false, RU); if (rid) c.movs[n0].estRec = { id: rid }; return r; };
const zPend = (c, rid) => cenSaldoEntregar(c.reqs[rid].itens.find(i => i.prod === CX));
const zEst = (c, oid) => { const o = c.ordens[oid]; return { etapa: o.etapa, kgAberto: String(benKgAberto(o)), usoMax: benCxUsoMax(o), sobra: benCxSobra(c, o), falta: benFaltaCx(c, o), livreTot: benLivreCx(c), selos: benSelos(c, o).map(s => s.t), prox: benProx(c, o).t, nota: (benProx(c, o).nota || '').slice(0, 500) }; };
