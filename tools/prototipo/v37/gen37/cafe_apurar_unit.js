// COLH-C01 · café recebido em litros sem rendimento beneficiado fica "sc a apurar" com ou sem área apontada (revisão Codex 6070584991;
// contrato docs/colheita R-09: "produção em sc só pelo rendimento medido no beneficiamento; até lá sc a apurar"). Node, sem navegador.
// Carregado depois de: perfis + CEN0 + cenario.js + PRDC + producao.js + núcleo da O.S. + PR_UI_JS + PR_PED_JS + COLH_JS + prLoteRow/prPanLote/prPanCarga.
// Dano evitado: "0 sc", "0,00 sc/ha" e "−100,0 %" apresentados como resultado medido (decisão de produtividade e venda sobre zero falso);
// litros convertidos em sacas por fator fixo no estoque. Zero medido (rendimento 0) continua zero e distinguível do pendente.
const R = []; function ok(n, c, info) { R.push({ n, ok: !!c, info: c ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 900) }); }
function MUD(c, fn) { const x = cenClone(c); try { const r = fn(x) || {}; Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); return r; } catch (e) { return { erro: String(e.message || e) }; } }
const SELF = { state: {} };
function OSX(c, id, tal, etapa, ap, tipo) { c.ordens[id] = { id, tipo: tipo || 'Colheita de café', talhao: tal, area: 0, etapa, versao: 'v1', realizado: 0, saldo: 0, resp: 'Sérgio', ins: [], req: null, selos: [],
  ap: (ap || []).map((a, i) => ({ d: a[0], dia: i + 1, ha: a[1], st: a[2] || 'Conferido', sinc: true, origem: 'web' })), reservado: false, osc: {} }; return c.ordens[id]; }
const CID = 'c9';   // C1 · Café Catuaí 144 (38 ha, meta 38 sc/ha), Santa Rita · sintético
// a carga da revisão Codex: 12.000 L de café da roça recebidos (bruto 9.200 − tara 3.200 = 6.000 kg), sem rendimento beneficiado medido
function base(area) { const c = cenClone(CEN0); OSX(c, 'OS-0930', 'C1', 'Em execução', area ? [['25/09', area]] : []);
  const r = MUD(c, x => prReceber(x, { os: 'OS-0930', ticket: 'TK-CF1', bruto: 9200, tara: 3200, litros: 12000, cond: 'Íntegra', dcol: '2026-09-25' })); return { c, r }; }
const linha = (c) => { const X = prTal(c, CID); return { X, row: prTalRow(c, X) }; };
const FALSO = /(^|[^\d.,])0 sc\b|0,00 sc\/ha|−100,0 %/;
const ORIG = (c, ben) => Object.values(c.producao.cargas).filter(g => g.st === 'Recebida' && g.cultura === 'Café').forEach(g => g.origem.forEach(x => { x.ben = ben; }));

// ---- C01a/b · a mesma carga, com e sem área apontada: "12.000 L · sc a apurar", nunca 0 sc / 0,00 sc/ha / −100,0 % ----
{ const A = base(5), B = base(0); const la = linha(A.c), lb = linha(B.c);
  console.log('REPRO COLH-C01 ' + JSON.stringify({ comArea: { colh: la.row.s.colh, prtv: la.row.s.prtv, ref: la.row.s.ref }, semArea: { colh: lb.row.s.colh, prtv: lb.row.s.prtv, ref: lb.row.s.ref } }));
  ok('C01a com 5 ha apontados: colhido "12.000 L · sc a apurar"; produtividade e desvio a apurar (nada de 0 sc, 0,00 sc/ha ou −100,0 %)',
     !A.r.erro && la.row.s.colh === '12.000 L · sc a apurar' && la.row.s.prtv === 'sc/ha a apurar' && /a apurar$/.test(la.row.s.ref) && !FALSO.test(la.row.s.colh + ' ' + la.row.s.prtv + ' ' + la.row.s.ref),
     [A.r.erro, la.row.s]);
  ok('C01b sem área apontada: o mesmo texto (o apontamento não muda o estado de apuração)', !B.r.erro && lb.row.s.colh === la.row.s.colh && lb.row.s.prtv === la.row.s.prtv && lb.row.s.ref === la.row.s.ref, [lb.row.s, la.row.s]);
  ok('C01c a linha não ordena o café a apurar como zero colhido (valor vazio, não 0)', la.row.v.colh === null && lb.row.v.colh === null, [la.row.v.colh, lb.row.v.colh]);
  const R5 = la.X.R; ok('C01d estado único (prResultado): a apurar, 12.000 L pendentes, 0 kg medidos, produtividade e desvio nulos', R5.apurar === true && R5.cafe === 12000 && R5.kg === 0 && R5.prtv === null && R5.desv === null, R5); }

// ---- C01e · consumidores: total por cultura (grupo), painel do talhão (resultado, passes), mensagem do recebimento ----
{ const A = base(5); const X = prTal(A.c, CID); const pd = prPonderada([X.R]);
  ok('C01e total da cultura: a produtividade ponderada não soma o café a apurar como zero', pd === null || pd.area === 0, pd);
  const P = prPanTal(SELF, A.c, X); const kv = Object.fromEntries(P.kv.map(x => [x.l, x.v])); const txt = JSON.stringify(P.secs);
  ok('C01f painel do talhão: colhido "12.000 L · sc a apurar", produtividade e meta a apurar; passe e resultado sem 0 sc',
     kv['Colhido na safra'] === '12.000 L · sc a apurar' && kv['Produtividade'] === 'sc/ha a apurar' && /12\.000 L · sc a apurar/.test(txt) && !FALSO.test(JSON.stringify(P.kv) + txt), [P.kv, txt.slice(0, 600)]);
  ok('C01g mensagem do recebimento com área apontada: passe "sc/ha a apurar", não "0,00 sc/ha"', /passe S\d\d sc\/ha a apurar/.test(A.r.msg) && !FALSO.test(A.r.msg), A.r.msg); }

// ---- C01h · estoque de produto: lote "Café da roça" em L, sem saca derivada de litros ----
{ const A = base(5); const L = A.r.L; const S = prSaldos(A.c, L); const rw = prLoteRow(A.c, L, S); const pl = prPanLote(SELF, A.c, L); const pc = prPanCarga(SELF, A.c, A.r.g);
  ok('C01h estoque de produto: lote Café da roça 12.000 L (físico e em processo), nunca "200 sc"; painel do lote e da carga também',
     rw.s.fis === '12.000 L' && rw.s.proc === '12.000 L' && !/sc/.test(JSON.stringify(rw.s)) && !/\b200 sc\b/.test(JSON.stringify(pl) + JSON.stringify(pc)) && /12\.000 L/.test(JSON.stringify(pl)),
     [rw.s, JSON.stringify(pl).slice(0, 300)]); }

// ---- C01i · transição: o beneficiamento mede o rendimento (BEN-4 · R-D02 grava o beneficiado rateado na origem) ----
{ const A = base(5); ORIG(A.c, 3000); const { X, row } = linha(A.c);
  ok('C01i rendimento medido 3.000 kg beneficiado: 50 sc, 10,00 sc/ha em 5 ha e desvio contra a meta de 38 sc/ha (−73,7 %)',
     X.R.apurar === false && row.s.colh === '50 sc' && row.s.prtv === '10,00 sc/ha · safra parcial' && /meta 38 sc\/ha −73,7 %$/.test(row.s.ref) && row.v.colh === 3000, [X.R.apurar, row.s, row.v.colh]); }

// ---- C01n · linha e painel da carga (Cargas e recebimento): litros a apurar → sacas medidas, pela mesma regra ----
{ const A = base(5); const g = A.r.g; const TX = (x) => { try { return prCargaCafeTxt(x); } catch (e) { return String(e.message || e); } };
  const t0 = TX(A.c.producao.cargas[g.id]); ORIG(A.c, 3000); const t1 = TX(A.c.producao.cargas[g.id]);
  ok('C01n carga de café: "12.000 L · sc a apurar" e, medido o rendimento, "12.000 L · 50 sc"', t0 === '12.000 L · sc a apurar' && t1 === '12.000 L · 50 sc', [t0, t1]); }

// ---- C01j · zero real: rendimento medido 0 kg é zero (distinguível do pendente) ----
{ const A = base(5); ORIG(A.c, 0); const { X, row } = linha(A.c);
  ok('C01j zero medido: 0 sc, 0,00 sc/ha e −100,0 % aparecem porque foram medidos (não a apurar)',
     X.R.apurar === false && row.s.colh === '0 sc' && row.s.prtv === '0,00 sc/ha · safra parcial' && /−100,0 %$/.test(row.s.ref), [X.R.apurar, row.s]); }

// ---- C01k · parte medida e parte pendente: soma só o medido e diz o que falta, sem produtividade ----
{ const A = base(5); ORIG(A.c, 3000);
  const r2 = MUD(A.c, x => prReceber(x, { os: 'OS-0930', ticket: 'TK-CF2', bruto: 7200, tara: 3200, litros: 8000, cond: 'Íntegra', dcol: '2026-09-25' }));
  const { X, row } = linha(A.c);
  ok('C01k 3.000 kg medidos + 8.000 L pendentes: "50 sc + 8.000 L · sc a apurar", produtividade a apurar',
     !r2.erro && X.R.apurar === true && row.s.colh === '50 sc + 8.000 L · sc a apurar' && row.s.prtv === 'sc/ha a apurar', [r2.erro, row.s]); }

// ---- C01l · ligação com o Comercial: a oferta de café beneficiado vem da previsão publicada; o café a apurar não entra como zero ----
{ const c0 = cenClone(CEN0); const o0 = prOfertaSafra(c0, 'Café beneficiado', '2026/27'); const A = base(5); const o1 = prOfertaSafra(A.c, 'Café beneficiado', '2026/27');
  ok('C01l oferta de Café beneficiado igual antes e depois dos 12.000 L (o físico em litros não vira oferta nem zero)', JSON.stringify(o0) === JSON.stringify(o1), [o0, o1]); }

// ---- C01m · outras culturas não mudam: grão com carga continua "sc" medido ----
{ const c = cenClone(CEN0); const s = prResultado(c, 'lg19'); ok('C01m mamão (Pivô 19) segue medido: não fica a apurar', s && s.apurar === false && s.kg > 0, s && [s.apurar, s.kg]); }

console.log(JSON.stringify(R));
