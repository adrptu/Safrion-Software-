// Beneficiamento · rodada 3 da integração (BEN-D33..D36): propriedade aleatória no motor real das telas (perfis + CEN0 + cenario.js + producao.js
// + ben.js + núcleo da O.S.), sem navegador. Sementes fixas; a cada passo o oráculo (independente das funções sob teste: refaz as contas pelos
// campos e movimentos, só com os primitivos decimais) confere os invariantes I-a..I-f de docs/integracao/BEN3/DESENHO.md §3; cada invariante
// violado é registrado na 1ª vez, com a menor sequência reprodutora (encolhida por remoção de passos). Antes do aleatório, as trilhas mínimas
// achadas no 0139898 (U53a..g) e no 15e2976 pela revisão adversarial (U53h..j) rodam como casos fixos. Fora do gerador, de propósito: contagem e ajuste de inventário (I-e4 vale sem eles;
// a trava física do cenEntregar cobre o ajuste), benRetirar, benConfirmarCorrecao e comandos de O.S. (cobertos pelos testes de O.S.).
// Saída: uma linha JSON {ok, runs, steps, invariantes, fixas, falhas}. Uso: ben_prop_test.py (RUNS e STEPS pelo ambiente).
// ben_prop.js — depois do motor. Saída: JSON {ok, runs, falhas:[{seed, passo, inv, info, trilha}]}
const SEEDS = [20261010, 7, 4242], RUNS = Number((globalThis.process && process.env.RUNS) || 120), STEPS = Number((globalThis.process && process.env.STEPS) || 35);
const CX = BENC.cx.item, MASSA = BENC.cx.massa, IG = 'Igor', PA = 'Paula', AN = 'Ana', RU = 'Rui', EPS = 1e-9;
const ABERTA = ['Liberadas', 'Em execução', 'Em conferência'];
function rng(s) { return () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function MUD(c, fn) { const x = cenClone(c); let r; try { r = fn(x) || {}; } catch (e) { r = { erro: String(e.message || e) }; }
  if (!r.erro && !r.nada) { Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); } return r; }
/* ---------- oráculo (independente das funções sob teste) ---------- */
const N = v => Number(v) || 0;
const lotesCx = c => Object.values(c.lotes).filter(l => l.prod === CX);
const linhas = c => Object.values(c.reqs).flatMap(r => r.itens.filter(i => i.prod === CX).map(it => ({ r, it, o: c.ordens[r.os] })));
const livreTot = c => lotesCx(c).reduce((a, l) => a + Math.floor(Math.max(0, l.fisico - l.quarentena - l.reservado) + EPS), 0);
function kgAberto(o) { if (!benEh(o) || ABERTA.indexOf(o.etapa) < 0) return 0;
  const x = prSub(prSoma(o.ben.ent.map(e => e.kg)), prSoma(o.ben.sai.filter(s => !s.estorno).map(s => s.kg))); return prCmp(x, 0) > 0 ? x : 0; }
function usoMax(o) { const k = kgAberto(o), m = prM(MASSA); return prCmp(k, 0) > 0 ? Number((prM(k) + m - 1n) / m) : 0; }
const custO = (c, o) => linhas(c).filter(x => x.o === o).reduce((a, x) => a + x.it.custodia, 0);
const sobra = (c, o) => { const cu = Math.floor(custO(c, o) + EPS); return ABERTA.indexOf(o.etapa) >= 0 ? Math.max(0, cu - usoMax(o)) : cu; };
const pend = it => Math.max(0, it.solicitado - N(it.dispensado) - it.consumido - it.custodia);
function resTot(c, rid) { const s0 = CEN0.reqs[rid], i0 = s0 && s0.itens.find(i => i.prod === CX); const b = i0 ? (s0.estado === 'Reservada' ? i0.solicitado : i0.entregue) : 0;
  return b + c.movs.filter(m => m.req === rid && m.prod === CX && (m.tipo === 'reserva' || m.tipo === 'reserva-baixa')).reduce((a, m) => a + (m.tipo === 'reserva' ? m.qtd : -m.qtd), 0); }
const own = (c, x) => Math.max(0, resTot(c, x.r.id) - x.it.entregue);
function ledger(c, l) { const z = CEN0.lotes[CX + '|' + l.lote] || { fisico: 0, quarentena: 0 }; const mv = c.movs.filter(m => m.prod === CX && m.lote === l.lote);
  const S = (t, f) => mv.filter(m => m.tipo === t && (!f || f(m))).reduce((a, m) => a + m.qtd, 0);
  return { fis: z.fisico + S('recebimento-nf') - S('entrega') + S('devolucao') + S('ajuste'), quar: z.quarentena + S('recebimento-nf', m => !m.apto) + S('devolucao', m => !m.apto) - S('inspecao') }; }
const total0 = (() => { const c = CEN0; return lotesCx(c).reduce((a, l) => a + l.fisico, 0) + linhas(c).reduce((a, x) => a + x.it.custodia + x.it.consumido, 0); })();
/* ---------- invariantes de estado ---------- */
function inv(c) { const V = [], bad = (id, info) => V.push({ id, info }); const L = linhas(c);
  L.forEach(x => { const it = x.it;
    if (Math.abs(it.entregue - it.consumido - it.custodia - it.devolvido) > EPS) bad('I-e1', [x.r.id, it]);
    if ([it.entregue, it.consumido, it.custodia, it.devolvido, N(it.dispensado)].some(v => v < -EPS)) bad('I-e1', [x.r.id, 'negativo', it]);
    if (benEh(x.o) && ABERTA.indexOf(x.o.etapa) >= 0 && Math.abs(pend(it) - own(c, x)) > EPS) bad('I-d2', [x.r.id, pend(it), own(c, x)]);
    if (benEh(x.o) && x.o.etapa === 'Encerradas' && (it.custodia > EPS || pend(it) > EPS || own(c, x) > EPS)) bad('I-a4', [x.r.id, it, own(c, x)]);
    if (benEh(x.o) && x.o.etapa === 'Canceladas') bad('I-a4', [x.r.id, 'linha em ordem cancelada']);
    /* I-d4 (integração na v56): a reserva própria que o motor usa (cenResPropria: entrega, Fechar, Estoque, demanda da CTL-4) é a do oráculo,
       em toda linha BEN, inclusive encerrada (a reserva-baixa do Fechar não volta como reserva própria quando outra ordem reserva no lote) */
    const lx = c.lotes[CX + '|' + it.lote]; if (benEh(x.o) && lx) { const eng = cenResPropria(c, x.r.id, it, lx), ora = Math.max(0, Math.min(lx.reservado, own(c, x)));
      if (Math.abs(eng - ora) > EPS) bad('I-d4', [x.r.id, x.o.etapa, eng, ora]); } });
  lotesCx(c).forEach(l => { const g = ledger(c, l);
    if (Math.abs(g.fis - l.fisico) > EPS) bad('I-e2', [l.lote, g.fis, l.fisico]);
    if (Math.abs(g.quar - l.quarentena) > EPS || l.quarentena < -EPS || l.quarentena > l.fisico + EPS) bad('I-e3', [l.lote, g.quar, l.quarentena]);
    const r = L.filter(x => x.it.lote === l.lote && x.o && x.o.etapa !== 'Encerradas').reduce((a, x) => a + own(c, x), 0);
    if (Math.abs(r - l.reservado) > EPS || l.reservado > l.fisico - l.quarentena + EPS) bad('I-e4', [l.lote, r, l.reservado]); });
  const T = lotesCx(c).reduce((a, l) => a + l.fisico, 0) + L.reduce((a, x) => a + x.it.custodia + x.it.consumido, 0);
  const T0 = total0 + c.movs.filter(m => m.prod === CX && (m.tipo === 'recebimento-nf' || m.tipo === 'ajuste')).reduce((a, m) => a + m.qtd, 0);
  if (Math.abs(T - T0) > EPS) bad('I-e6', [T, T0]);
  benOrdens(c).forEach(o => { const cons = L.filter(x => x.o === o).reduce((a, x) => a + x.it.consumido, 0);
    const cx = o.ben.sai.filter(s => !s.estorno && s.fluxo === 'Produto').reduce((a, s) => a + s.cx, 0); if (Math.abs(cons - cx) > EPS) bad('I-e5', [o.id, cons, cx]);
    if (benCxSobra(c, o) !== sobra(c, o)) bad('I-a1', [o.id, o.etapa, benCxSobra(c, o), sobra(c, o)]);
    /* o selo "Sobra em custódia" da conferência acompanha a sobra provada (I-a1 na tela; integração na v56) */
    if (o.etapa === 'Em conferência' && benSelos(c, o).some(s => s.t === 'Sobra em custódia') !== (sobra(c, o) > 0)) bad('I-a1', [o.id, 'selo', sobra(c, o)]);
    const tot = ((o.ins || [])[0] || {}).tot || 0;
    if (o.etapa === 'A liberar') { const im = benImpedimentos(c, o).find(x => x.cx);
      if (!!im !== (livreTot(c) < tot)) bad('I-b1', [o.id, livreTot(c), tot, im && im.t]);
      /* [crítica: 'falta' in k — no "antes" (0139898) a API nova não existe; pular em vez de reprovar tudo no passo 0] */
      const k = im && im.link; if (k && 'falta' in k) { if (k.falta !== tot - livreTot(c)) bad('I-f1', [o.id, 'falta', k.falta, tot - livreTot(c)]);
        (k.fontes || []).forEach(f => { if (f.os === o.id) bad('I-f3', [o.id, f]); if (f.tipo === 'sobra' && f.qtd !== sobra(c, c.ordens[f.os])) bad('I-a2', [f, sobra(c, c.ordens[f.os])]);
          /* I-f6 (revisões A2 e A3): a quarentena citada como fonte é só a que pode ser liberada para outra ordem */
          if (f.tipo === 'quarentena' && f.qtd !== quarLivreO(c, c.lotes[CX + '|' + f.lote])) bad('I-f6', [o.id, f, quarLivreO(c, c.lotes[CX + '|' + f.lote])]); });
        if (k.cobre !== ((k.fontes || []).reduce((a, f) => a + f.qtd, 0) >= k.falta)) bad('I-f1', [o.id, 'cobre', k]); } }
    else { const t = benCaixasRec(c, o, livreTot(c), livreTot(c) + 1).why || ''; if (/Cancelar a ordem/.test(t)) bad('I-f2', [o.id, o.etapa, t]);
      if (o.etapa === 'Em conferência' && /Pedir mais caixas|entrega no balcão/.test(t) && !/Reabr/.test(t)) bad('I-f2', [o.id, 'conferência sem Reabrir', t]); }
    /* [crítica: I-e9 e I-f4 (benFaltaCx = faltaExec da seção 2)] */
    const Lo = L.filter(x => x.o === o), sol = Lo.reduce((a, x) => a + x.it.solicitado, 0), consO = Lo.reduce((a, x) => a + x.it.consumido, 0);
    if (Lo.length && (ABERTA.indexOf(o.etapa) >= 0 || o.etapa === 'Encerradas') && sol !== (((o.ins || [])[0] || {}).tot || 0)) bad('I-e9', [o.id, 'Σsol ≠ ins.tot', sol, o.ins]);
    Lo.forEach(x => { if (x.it.solicitado - N(x.it.dispensado) - x.it.consumido - x.it.custodia < -EPS) bad('I-e9', [x.r.id, 'pend bruto < 0', x.it]); });
    if (ABERTA.indexOf(o.etapa) >= 0 && typeof benFaltaCx === 'function') { const f = faltaO(c, o);
      if (benFaltaCx(c, o) !== f) bad('I-f4', [o.id, benFaltaCx(c, o), f]); } });
  return V; }
/* caixas em uso de ordem aberta esperando o laudo num lote (it.quarUso, revisão A2) e a quarentena que pode ir a outra ordem */
const quarUsoO = (c, l, oid) => linhas(c).filter(x => x.it.lote === l.lote && x.o && benEh(x.o) && ABERTA.indexOf(x.o.etapa) >= 0 && (!oid || x.o.id === oid)).reduce((a, x) => a + N(x.it.quarUso), 0);
const quarLivreO = (c, l) => l ? Math.floor(Math.max(0, l.quarentena - N(l.quarRep) - quarUsoO(c, l)) + EPS) : 0;   /* sem a reprovada (revisão A3) */
/* falta pelo oráculo: o planejado sem a reposição (o.ben.cxRepos, revisão A1) e ainda não usado, até o teto, menos custódia e a entregar */
function faltaO(c, o) { if (!o || !benEh(o) || ABERTA.indexOf(o.etapa) < 0) return 0; const Lo = linhas(c).filter(x => x.o === o);
  const sol = Lo.reduce((a, x) => a + x.it.solicitado, 0), cons = Lo.reduce((a, x) => a + x.it.consumido, 0);
  return Math.max(0, Math.min(usoMax(o), sol - N((o.ben || {}).cxRepos) - cons) - custO(c, o) - Lo.reduce((a, x) => a + pend(x.it), 0)); }
/* ---------- comandos (parâmetros fixos no objeto: a trilha se repete igual) ---------- */
function exec(c, op) { const o = op.o && c.ordens[op.o]; const r0 = benRota('PACK-FRU|3');
  switch (op.k) {
    case 'criar': return MUD(c, x => benNova(x, { lotes: [{ lote: op.lote, kg: prFis(x, op.lote) }], cx: op.cx }, IG));
    case 'liberar': return MUD(c, x => benAutorizarLiberar(x, op.o, IG));
    case 'cancelar': return MUD(c, x => benCancelar(x, op.o, 'prop', IG));
    case 'iniciar': return MUD(c, x => benIniciar(x, op.o, IG));
    case 'pedir': { const nn = pedirN(c, op); if (!(nn >= 1)) return { erro: 'sem falta a pedir' }; return MUD(c, x => benComplementar(x, op.o, nn, IG)); }
    case 'entregar': { const it = (c.reqs[op.rid] || { itens: [] }).itens.find(i => i.prod === CX); const q = op.q === 'pend' ? (it ? Math.floor(pend(it)) : 0) : op.q;
      return MUD(c, x => cenEntregar(x, op.rid, CX, q, IG, RU)); }
    case 'saidaP': { const sub = o && o.etapa === 'Em conferência' ? (o.ben.sai.find(s => s.estorno && !o.ben.sai.some(y => y.subst === s.id && !y.estorno)) || {}).id : '';
      const liq = prMul(op.cx, prMul(MASSA, op.fat)); const bruto = prSoma([liq, benTara(op.cx, 0, r0)]);
      return MUD(c, x => benSaida(x, op.o, { fluxo: 'Produto', classe: op.classe, cx: op.cx, bruto, subst: sub || '', motivo: 'prop' }, IG)); }
    case 'saidaD': return MUD(c, x => benSaida(x, op.o, { fluxo: 'Descarte', destino: 'Compostagem', kg: op.kg, motivo: 'prop' }, IG));
    case 'estornar': { const v = o ? o.ben.sai.filter(s => !s.estorno) : []; const s = v[op.i % Math.max(1, v.length)];
      return s ? MUD(c, x => benEstornar(x, op.o, s.id, 'Pesagem refeita', '', IG)) : { erro: 'sem saída' }; }
    case 'concluir': return MUD(c, x => benConcluir(x, op.o, IG));
    case 'reabrir': return MUD(c, x => benReabrir(x, op.o, 'prop', IG));
    case 'justificar': return MUD(c, x => benJustificar(x, op.o, 'Perda não identificada', 'prop', AN));
    case 'conferir': return MUD(c, x => benConferir(x, op.o, PA));
    case 'fechar': return MUD(c, x => benFechar(x, op.o, IG));
    case 'nf': return MUD(c, x => { if (op.apto > 0) cenReceber(x, CX, op.lote, op.apto, 'un', 'Packing', '—', op.doc, true, RU);
      if (op.quar > 0) cenReceber(x, CX, op.lote, op.quar, 'un', 'Packing', '—', op.doc, false, RU); });
    case 'laudo': return MUD(c, x => cenLiberarQuarentena(x, op.key, 'LAUDO-PROP', AN));
    case 'reprovar': return MUD(c, x => cenReprovarQuarentena(x, op.key, 'LAUDO-REP-PROP', 'prop', AN));   /* CTL-4: laudo que reprova (revisão A3) */
    case 'devolver': { const it = (c.reqs[op.rid] || { itens: [] }).itens.find(i => i.prod === CX); if (!it || !(it.custodia > 0)) return { erro: 'sem custódia' };
      /* [crítica: no "antes" não há benDevPadrao; o guiado de 0139898 é a custódia inteira (processo_estoque.py 449)] */
      const q = op.q === 'guiado' ? (typeof benDevPadrao === 'function' ? N(benDevPadrao(c, c.ordens[c.reqs[op.rid].os], it)) : it.custodia) : Math.min(op.q, it.custodia);
      return q > 0 ? MUD(c, x => cenDevolver(x, op.rid, CX, q, op.apto, RU)) : { erro: 'nada a devolver' }; }
    case 'seguirRec': { if (!o || o.etapa !== 'A liberar') return { erro: 'fase' }; const im = benImpedimentos(c, o).find(x => x.cx); if (!im || !im.link || !im.link.fontes) return { erro: 'sem falta ou sem fontes (antes)' };
      const k = im.link; for (const f of k.fontes || []) {
        if (f.tipo === 'sobra') for (const p of f.linhas) MUD(c, x => cenDevolver(x, p.rid, CX, p.qtd, true, RU));
        else if (f.tipo === 'nf') MUD(c, x => { const n0 = x.movs.length; cenReceber(x, CX, f.lote, f.qtd, 'un', 'Packing', '—', f.id, true, RU); x.movs[n0].estRec = { id: f.rid }; });
        else if (f.tipo === 'quarentena') MUD(c, x => cenLiberarQuarentena(x, CX + '|' + f.lote, 'LAUDO-PROP', AN)); }
      return { cobre: k.cobre }; } } }
/* "Pedir mais caixas" com a quantidade fixa da trilha ou com a falta sugerida pela tela (n: 'falta', revisão A1) */
function pedirN(c, op) { return op.n === 'falta' ? (typeof benFaltaCx === 'function' ? benFaltaCx(c, c.ordens[op.o]) : 0) : op.n; }
/* ---------- invariantes de transição ---------- */
function passo(c, op) { const a = cenClone(c); const nn = op.k === 'pedir' ? pedirN(a, op) : 0; const r = exec(c, op) || {}; const V = inv(c), bad = (id, info) => V.push({ id, info });
  /* I-f5 (revisão A1): "Pedir mais caixas" aceito baixa a falta: depois = máx(0, antes − n) (a reposição não entra no planejado) */
  if (op.k === 'pedir' && !r.erro && nn >= 1 && a.ordens[op.o]) { const f0 = faltaO(a, a.ordens[op.o]), f1 = faltaO(c, c.ordens[op.o]);
    if (Math.abs(f1 - Math.max(0, f0 - nn)) > EPS) bad('I-f5', [op, nn, f0, f1]); }
  if (r.erro && JSON.stringify(c) !== JSON.stringify(a)) bad('I-e7', op);
  if (op.k === 'devolver' && !r.erro) { const ob = a.ordens[a.reqs[op.rid].os];
    if (livreTot(c) - livreTot(a) > sobra(a, ob) + EPS) bad('I-a3', [op, livreTot(c) - livreTot(a), sobra(a, ob)]);
    const tem = (cc, o) => custO(cc, o) + linhas(cc).filter(x => x.o === o).reduce((s, x) => s + own(cc, x), 0);
    if (op.apto && ABERTA.indexOf(ob.etapa) >= 0 && tem(c, c.ordens[ob.id]) + EPS < Math.min(usoMax(ob), tem(a, ob))) bad('I-a3', [op, 'perdeu caixa em uso']);
    /* revisão A2: bloqueada para inspeção, a parte em uso continua da ordem (custódia + reserva própria + em uso esperando o laudo) */
    const lt = c.lotes[CX + '|' + a.reqs[op.rid].itens.find(i => i.prod === CX).lote];
    if (!op.apto && ABERTA.indexOf(ob.etapa) >= 0 && tem(c, c.ordens[ob.id]) + quarUsoO(c, lt, ob.id) + EPS < Math.min(usoMax(ob), tem(a, ob) + quarUsoO(a, a.lotes[CX + '|' + lt.lote], ob.id))) bad('I-a3', [op, 'bloqueada: perdeu caixa em uso']); }
  /* I-a5 (revisão A2): o laudo que aprova devolve a cada ordem aberta as caixas em uso dela, até a falta: falta depois = máx(0, antes − em uso) */
  if (op.k === 'laudo' && !r.erro) { const la = a.lotes[op.key];
    benOrdens(a).filter(o => ABERTA.indexOf(o.etapa) >= 0).forEach(o => { const u = quarUsoO(a, la, o.id); if (!(u > 0)) return;
      const f0 = faltaO(a, o), f1 = faltaO(c, c.ordens[o.id]); if (Math.abs(f1 - Math.max(0, f0 - u)) > EPS) bad('I-a5', [op, o.id, u, f0, f1]); }); }
  const alvo = op.rid ? (a.reqs[op.rid] || {}).os : op.o;
  if (!r.erro && ['nf', 'laudo', 'seguirRec'].indexOf(op.k) < 0) linhas(a).filter(x => x.r.os !== alvo).forEach(x => { const y = linhas(c).find(z => z.r.id === x.r.id);
    if (!y || y.it.custodia !== x.it.custodia || y.it.consumido !== x.it.consumido || y.it.solicitado !== x.it.solicitado || N(y.it.dispensado) !== N(x.it.dispensado) || Math.abs(own(c, y) - own(a, x)) > EPS) bad('I-e8', [op, x.r.id]); });
  if (op.k === 'liberar' && a.ordens[op.o] && a.ordens[op.o].etapa === 'A liberar') { const tot = (a.ordens[op.o].ins[0] || {}).tot || 0;
    if (!benImpedimentos(a, a.ordens[op.o]).length && r.erro) bad('I-b2', [op, r.erro]);
    if (r.erro && lotesCx(c).some(l => l.reservado !== (a.lotes[CX + '|' + l.lote] || {}).reservado)) bad('I-b2', [op, 'reserva órfã']);
    if (!r.erro) { const ls = benLinhas(c, c.ordens[op.o]); const lt = ls.map(x => x.it.lote);
      if (ls.reduce((s, x) => s + x.it.solicitado, 0) !== tot || new Set(lt).size !== lt.length) bad('I-b2', [op, ls.map(x => [x.rid, x.it.lote, x.it.solicitado])]); } }
  if (op.k === 'seguirRec' && r.cobre && benImpedimentos(c, c.ordens[op.o]).some(x => x.cx)) bad('I-f1', [op, 'cobre e não libera']);
  /* [crítica: I-b3 — o complemento aceito se e só se há livre total, na fase que permite] */
  if (op.k === 'pedir' && nn >= 1 && a.ordens[op.o] && ['Liberadas', 'Em execução'].indexOf(a.ordens[op.o].etapa) >= 0 && !a.ordens[op.o].ben.conc && !!r.erro !== (livreTot(a) < nn)) bad('I-b3', [op, livreTot(a), r.erro]);
  return { r, V }; }
/* ---------- gerador: só comandos plausíveis no estado, com uma fração inválida de propósito ---------- */
function escolher(c, R) { const n = (a, b) => a + Math.floor(R() * (b - a + 1)), pick = a => a[Math.floor(R() * a.length)], ops = [];
  benLotesAptos(c).slice(0, 3).forEach(L => ops.push({ k: 'criar', lote: L.id, cx: R() < 0.7 ? undefined : n(1, 2500) }));
  benOrdens(c).forEach(o => { const id = o.id;
    if (o.etapa === 'A liberar') ops.push({ k: 'liberar', o: id }, { k: 'seguirRec', o: id }, { k: 'cancelar', o: id });
    if (o.etapa === 'Liberadas') ops.push({ k: 'iniciar', o: id });
    if (ABERTA.indexOf(o.etapa) >= 0) ops.push({ k: 'pedir', o: id, n: n(1, 900) });
    if (ABERTA.indexOf(o.etapa) >= 0 && faltaO(c, o) > 0) ops.push({ k: 'pedir', o: id, n: 'falta' }, { k: 'pedir', o: id, n: 'falta' });   /* a sugestão da tela, com peso dobrado */
    if (['Em execução', 'Em conferência'].indexOf(o.etapa) >= 0) ops.push({ k: 'saidaP', o: id, cx: n(1, 1200), classe: pick(['A', 'B']), fat: pick(['1', '0.97', '1.02']) },
      { k: 'saidaD', o: id, kg: n(10, 3000) }, { k: 'estornar', o: id, i: n(0, 9) });
    if (o.etapa === 'Em execução') ops.push({ k: 'concluir', o: id });
    if (o.etapa === 'Em conferência') ops.push({ k: 'reabrir', o: id }, { k: 'justificar', o: id }, { k: 'conferir', o: id }, { k: 'fechar', o: id }); });
  linhas(c).forEach(x => { ops.push({ k: 'entregar', rid: x.r.id, q: R() < 0.6 ? 'pend' : n(1, 1500) });
    if (x.it.custodia > 0) ops.push({ k: 'devolver', rid: x.r.id, q: R() < 0.5 ? 'guiado' : n(1, Math.ceil(x.it.custodia)), apto: R() < 0.85 }); });
  ops.push({ k: 'nf', lote: pick(['CX26-02', 'QA-CX-02', 'QA-CX-03']), doc: 'NF-P' + n(1, 99), apto: n(0, 1300), quar: R() < 0.3 ? n(1, 200) : 0 });
  lotesCx(c).filter(l => l.quarentena > 0).forEach(l => ops.push({ k: 'laudo', key: CX + '|' + l.lote }));
  lotesCx(c).filter(l => l.quarentena - N(l.quarRep) > 0).forEach(l => ops.push({ k: 'reprovar', key: CX + '|' + l.lote }));
  return pick(ops); }
/* ---------- execução, reprodução e encolhimento ---------- */
/* [crítica: a semente também é conferida (passo −1); cada invariante é registrado na 1ª vez que aparece e a sequência SEGUE (no "antes",
   parar no 1º esconde I-a4 e I-e4 atrás do I-d2, executado em crit/ben_prop_shim2.js); o encolhimento pode tirar inclusive o último passo] */
const V0 = inv(cenClone(CEN0)); const VISTOS = {}, falhas = [];
V0.forEach(v => { VISTOS[v.id] = 1; falhas.push({ seed: 0, passo: -1, inv: v.id, info: v.info, trilha: [] }); });
function rodar(seed) { const R = rng(seed), c = cenClone(CEN0), t = [], out = [];
  for (let i = 0; i < STEPS; i++) { const op = escolher(c, R); t.push(op); const { V } = passo(c, op);
    V.forEach(v => { if (!VISTOS[v.id]) { VISTOS[v.id] = 1; out.push({ seed, passo: i, V: [v], trilha: t.slice() }); } }); } return out; }
function reproduz(t, alvo) { const c = cenClone(CEN0); for (const op of t) { const { V } = passo(c, op); if (V.some(x => x.id === alvo)) return true; } return false; }
function encolher(f) { const alvo = f.V[0].id; let t = f.trilha.slice();
  for (let j = t.length - 1; j >= 0; j--) { const u = t.slice(0, j).concat(t.slice(j + 1)); if (reproduz(u, alvo)) t = u; } return t; }

/* ---------- casos fixos: as trilhas mínimas do "antes" (0139898), uma por invariante achado (U53) ---------- */
const FIXAS = [
  ['U53a', 'I-d2 · devolução guiada da sobra sem "a entregar" fantasma', [{ k: 'devolver', rid: 'REQ-030', q: 'guiado', apto: true }]],
  ['U53b', 'I-a3 · a devolução guiada não tira caixa em uso', [{ k: 'estornar', o: 'OB-0110', i: 7 }, { k: 'devolver', rid: 'REQ-030', q: 'guiado', apto: true }]],
  ['U53c', 'I-b1 · livre total de dois lotes', [{ k: 'estornar', o: 'OB-0110', i: 7 }, { k: 'devolver', rid: 'REQ-030', q: 'guiado', apto: true }, { k: 'cancelar', o: 'OB-0114' }, { k: 'criar', lote: 'L39-132', cx: 299 }, { k: 'nf', lote: 'QA-CX-03', doc: 'NF-P92', apto: 165, quar: 75 }]],
  ['U53d', 'I-a4 · Encerradas sem custódia, a entregar nem reserva', [{ k: 'devolver', rid: 'REQ-030', q: 'guiado', apto: true }, { k: 'concluir', o: 'OB-0110' }, { k: 'justificar', o: 'OB-0110' }, { k: 'conferir', o: 'OB-0110' }, { k: 'fechar', o: 'OB-0110' }]],
  ['U53e', 'I-e4 · reserva do lote = reserva própria das linhas abertas (Fechar baixa)', [{ k: 'estornar', o: 'OB-0110', i: 7 }, { k: 'devolver', rid: 'REQ-030', q: 'guiado', apto: true }, { k: 'pedir', o: 'OB-0110', n: 636 }, { k: 'concluir', o: 'OB-0110' }, { k: 'justificar', o: 'OB-0110' }, { k: 'conferir', o: 'OB-0110' }, { k: 'fechar', o: 'OB-0110' }]],
  ['U53f', 'I-b3 · Pedir mais caixas aceito com o livre total', [{ k: 'criar', lote: 'L39-132' }, { k: 'nf', lote: 'QA-CX-03', doc: 'NF-P11', apto: 795, quar: 0 }, { k: 'criar', lote: 'L39-131', cx: 710 }, { k: 'liberar', o: 'OB-0114' }, { k: 'pedir', o: 'OB-0114', n: 616 }]],
  ['U53g', 'I-a1 · sobra em conferência pelo kg aberto', [{ k: 'estornar', o: 'OB-0110', i: 6 }, { k: 'concluir', o: 'OB-0110' }]],
  /* revisão adversarial da rodada 3: as trilhas mínimas que reprovavam no 15e2976 viram casos fixos (A1, A2, A3) */
  ['U53h', 'I-f5 · pedir a falta sugerida a baixa (revisão A1)', [{ k: 'nf', lote: 'CX26-02', doc: 'NF-P69', apto: 117, quar: 0 }, { k: 'nf', lote: 'CX26-02', doc: 'NF-P63', apto: 948, quar: 0 },
    { k: 'nf', lote: 'QA-CX-03', doc: 'NF-P93', apto: 510, quar: 0 }, { k: 'nf', lote: 'QA-CX-02', doc: 'NF-P37', apto: 1260, quar: 175 }, { k: 'criar', lote: 'L39-132' }, { k: 'criar', lote: 'L38-132' },
    { k: 'laudo', key: CX + '|QA-CX-02' }, { k: 'liberar', o: 'OB-0114' }, { k: 'entregar', rid: 'REQ-041', q: 'pend' }, { k: 'devolver', rid: 'REQ-041', q: 639, apto: false }, { k: 'pedir', o: 'OB-0114', n: 'falta' }]],
  ['U53i', 'I-a3 · caixa em uso devolvida bloqueada continua da ordem (revisão A2)', [{ k: 'criar', lote: 'L38-132' }, { k: 'seguirRec', o: 'OB-0113' }, { k: 'estornar', o: 'OB-0110', i: 4 },
    { k: 'devolver', rid: 'REQ-030', q: 7, apto: false }]],
  ['U53j', 'I-f6 · quarentena reprovada não é fonte (revisão A3)', [{ k: 'devolver', rid: 'REQ-030', q: 22, apto: false }, { k: 'reprovar', key: CX + '|CX26-01' }, { k: 'criar', lote: 'L38-132' }]]];
const FIX = FIXAS.map(([n, t, trilha]) => { const c = cenClone(CEN0); const V = [];
  trilha.forEach((op, i) => { const r = passo(c, op); r.V.forEach(v => V.push({ passo: i, inv: v.id, info: v.info })); });
  return { n, t, ok: !V.length, V: V.slice(0, 4) }; });
SEEDS.forEach(s0 => { for (let k = 0; k < RUNS; k++) rodar(s0 * 1000 + k).forEach(f => falhas.push({ seed: f.seed, passo: f.passo, inv: f.V[0].id, info: f.V[0].info, trilha: encolher(f) })); });
console.log(JSON.stringify({ ok: !falhas.length && FIX.every(f => f.ok), runs: SEEDS.length * RUNS, steps: STEPS, invariantes: Object.keys(VISTOS), fixas: FIX, falhas }));
