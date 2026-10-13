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

// =====================================================================================================================
// P2 · estado c.producao, comandos e integrações (cada bloco parte da semente: cenClone(CEN0))
// =====================================================================================================================
function MUD(c, fn) { const x = cenClone(c); try { const r = fn(x) || {}; Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); return r; } catch (e) { return { erro: String(e.message || e) }; } }
const NOVO = () => cenClone(CEN0);
const F2 = (x) => prFmt(x, 2);
const MAM = 'Mamão Formosa · fruta de campo';
function OSX(c, id, tal, etapa, ap, tipo, ins) { c.ordens[id] = { id, tipo: tipo || 'Colheita · semana 39', talhao: tal, area: 0, etapa, versao: 'v1', realizado: 0, saldo: 0, resp: 'Sérgio', ins: (ins || []).map(p => ({ p, dose: 1, un: 'L', tot: 1 })), req: null, selos: [],
  ap: (ap || []).map((a, i) => ({ d: a[0], dia: i + 1, ha: a[1], st: a[2] || 'Conferido', sinc: true, origem: 'web' })), reservado: false, osc: {} };
  const o = c.ordens[id]; o.realizado = (o.ap || []).filter(cenApSomado).reduce((s, a) => s + a.ha, 0); return o; }

// ---- U06 · produtividade K05..K07 (semente) ----
{ const c = NOVO(); const r6 = prResultado(c, 'lg06'), r19 = prResultado(c, 'lg19'); const p6 = r6.passes[0], p19 = r19.passes[0];
  ok('U06a K05 Pivô 6 passe S38 final: 60,32 t · 0,96 t/ha · −2,71 % da previsão v1 (62 t)', prUnTxt('Mamão Formosa', p6.kg) === '60,32 t' && F2(p6.prtv) === '0,96' && p6.final && F2(p6.desv) === '−2,71' && p6.refKg === 62000, p6);
  ok('U06b K05 Pivô 6 ciclo 0,96 t/ha (área do cultivo 62,79 ha), parcial: sem desvio contra a meta anual', F2(r6.prtv) === '0,96' && r6.area === 62.79 && r6.parcial && r6.desv === null, r6);
  ok('U06c K06 Pivô 19 passe S39 parcial 36,42 t · 0,73 t/ha (50 ha apontados) com 1 carga a pesar; passe parcial não mostra desvio', F2(p19.prtv) === '0,73' && !p19.final && p19.aPesar.length === 1 && p19.desv === null && p19.area === 50, p19);
  ok('U06d K06 Pivô 19 ciclo 0,48 t/ha (75,11 ha)', F2(r19.prtv) === '0,48' && r19.area === 75.11, r19.prtv);
  const cu = prPonderada([r6, r19]); ok('U06e K07 mamão no ciclo: 0,70 t/ha ponderado (média simples daria 0,72)', F2(cu.prtv) === '0,70' && F2((r6.prtv + r19.prtv) / 2) === '0,72', cu); }

// ---- U03 · K13 apontar 25 ha sem carga não muda a produção; o passe cai de 0,73 para 0,49 t/ha ----
{ const c = NOVO(); const r = MUD(c, x => cenApontar(x, { os: 'OS-0505', d: '26/09', ha: 25, h: 8, origem: 'app', quem: 'Marcos', chave: 'APC-OS-0505-1' }));
  const p = prResultado(c, 'lg19').passes[0];
  ok('U03a apontamento de área pela regra única (cenApontar, app): 25 ha somados, OS-0505 com 75 ha', !r.erro && p.area === 75, [r.erro, p.area]);
  ok('U03b K13 a produção continua 36,42 t (área não gera kg) e o passe S39 vai a 0,49 t/ha', p.kg === 36420 && F2(p.prtv) === '0,49', [p.kg, p.prtv]);
  // pesar a CG-2108 (bruto 19.250, tara 7.200, Íntegra) → L39-133, 12.050 kg, Liberado, vence 29/09; passe 0,65
  const g = MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra', chave: 'W-REC-1', quem: 'Lúcia' }));
  const L = c.producao.lotes['L39-133']; const S = L && prSaldos(c, L); const p2 = prResultado(c, 'lg19').passes[0];
  ok('U03c K13 CG-2108 pesada: L39-133 com 12.050 kg, Liberado, vence 29/09, no Galpão de frutas Lagoa Grande', !g.erro && L && S.fis === 12050 && S.q === 'Liberado' && L.validade === '2026-09-29' && L.local === 'l11', [g.erro, L, S]);
  ok('U03d K13 passe S39 0,65 t/ha (48,47 t em 75 ha); ciclo 0,65 t/ha (75,11 ha)', F2(p2.prtv) === '0,65' && F2(prResultado(c, 'lg19').prtv) === '0,65' && p2.kg === 48470, [p2.prtv, p2.kg]);
  const rs = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 10000, chave: 'W-RS-1', ator: 'Ana' }));
  const S2 = prSaldos(c, c.producao.lotes['L39-133']); const sit = prSitPed(c, c.producao.pedidos['PV-036']);
  ok('U03e K13 reservar 10.000 kg para o PV-036: L39-133 disponível 2.050 kg; PV-036 Coberto', !rs.erro && S2.disp === 2050 && S2.res === 10000 && sit.t === 'Coberto' && rs.rs.id === 'RS-0002', [rs.erro, S2, sit]);
  // K06: sem o apontamento, pesar a CG-2108 dá passe 0,97 e ciclo 0,65
  const c2 = NOVO(); MUD(c2, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' }));
  ok('U03f K06 sem apontar: passe 0,97 t/ha (48,47 t em 50 ha); ciclo 0,65 t/ha', F2(prResultado(c2, 'lg19').passes[0].prtv) === '0,97' && F2(prResultado(c2, 'lg19').prtv) === '0,65', prResultado(c2, 'lg19').passes[0].prtv); }

// ---- U04 · idempotência (R-07): chave e ticket ----
{ const c = NOVO(); const k = { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra', chave: 'W-REC-9' };
  const a = MUD(c, x => prReceber(x, k)); const n1 = c.producao.movs.length; const b = MUD(c, x => prReceber(x, k));
  ok('U04a mesma chave e mesmo conteúdo = mesmo registro (nada somado de novo)', !a.erro && b.repetido && c.producao.movs.length === n1 && prFis(c, 'L39-133') === 12050, [a.erro, b, prFis(c, 'L39-133')]);
  const d = MUD(c, x => prReceber(x, Object.assign({}, k, { bruto: 19300 })));
  ok('U04b mesma chave e outro conteúdo = conflito, nada gravado', /conflito/.test(d.erro || '') && c.producao.movs.length === n1, d);
  const e = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra', dcol: '2026-09-22' }));
  ok('U04c ticket já recebido com o mesmo conteúdo (outro formulário) = a mesma carga, nada somado', e.repetido && c.producao.movs.length === n1, e);
  const f = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-4520', bruto: 20000, tara: 7200, cond: 'Íntegra', dcol: '2026-09-22' }));
  ok('U04d ticket já recebido com outro conteúdo = conflito com a carga original', /TK-4520 já recebido na CG-2108/.test(f.erro || '') && /conflito/.test(f.erro), f);
  const g = MUD(c, x => prCarga(x, { os: 'OS-0505', cx: 300, veic: 'Carreta 02', chave: 'APP-CG-X1', via: 'app', quem: 'Marcos' }));
  const g2 = MUD(c, x => prCarga(x, { os: 'OS-0505', cx: 300, veic: 'Carreta 02', chave: 'APP-CG-X1', via: 'app', quem: 'Marcos' }));
  const g3 = MUD(c, x => prCarga(x, { os: 'OS-0505', cx: 310, veic: 'Carreta 02', chave: 'APP-CG-X1', via: 'app', quem: 'Marcos' }));
  ok('U04e carga do app com a mesma chave: uma carga só; outra quantidade com a mesma chave = conflito', !g.erro && g2.repetido && /conflito/.test(g3.erro || '') && Object.keys(c.producao.cargas).length === 9, [g.erro, g2, g3.erro]);
  const z = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-9', bruto: 7000, tara: 7200, cond: 'Íntegra' }));
  ok('U04f líquido ≤ 0 é recusado', /maior que zero/.test(z.erro || ''), z); }

// ---- U05b · mistura 60/40 K04: rastreio nos dois talhões ----
{ const c = NOVO(); OSX(c, 'OS-0912', 'Pivô 24', 'Em execução', [['22/09', 10]], 'Colheita · semana 39');
  const r = MUD(c, x => prReceber(x, { mix: [{ os: 'OS-0505', pct: 60 }, { os: 'OS-0912', pct: 40, modo: 'estimada' }], ticket: 'TK-M1', bruto: 17201, tara: 7200, cond: 'Íntegra', dcol: '2026-09-22' }));
  const L = r.L; const o = (L && L.origem) || [];
  ok('U05c K04 carga mista 10.001 kg: 6.000,6 kg no Pivô 19 e 4.000,4 kg no Pivô 24, lote próprio (misto)', !r.erro && L.misto && o.length === 2 && o[0].kg === 6000.6 && o[1].kg === 4000.4 && o[1].modo === 'estimada', [r.erro, o]);
  ok('U05d a produção de cada talhão recebe a sua parte (Pivô 19 36.420 + 6.000,6; Pivô 24 4.000,4)', prResultado(c, 'lg19').kg === 42420.6 && prResultado(c, 'lg24').kg === 4000.4, [prResultado(c, 'lg19').kg, prResultado(c, 'lg24').kg]);
  const e = MUD(c, x => prReceber(x, { mix: [{ os: 'OS-0505', pct: 60 }, { os: 'OS-0912', pct: 30 }], ticket: 'TK-M2', bruto: 17201, tara: 7200, cond: 'Íntegra', dcol: '2026-09-22' }));
  ok('U05e participação que não soma 100 % é recusada', /somar 100/.test(e.erro || ''), e); }

// ---- U07 · qualidade efetiva pela carência AO VIVO (R-12, AC-08) ----
{ const c = NOVO(); const P = 'Tebuconazol 200 EC'; const cr = carRegraC(c, P, 'Mamão'); const d0 = cr.dias;
  // aplicação em 05/09 no Pivô 24; colheita em 24/09 (cumprida pela bula de referência); a bula corrigida depois põe a colheita na carência
  OSX(c, 'OS-0920', 'Pivô 24', 'Encerradas', [['05/09', 34.37]], 'Pulverização · antracnose', [P]);
  OSX(c, 'OS-0921', 'Pivô 24', 'Em execução', [['24/09', 10]], 'Colheita · semana 39');
  const r = MUD(c, x => prReceber(x, { os: 'OS-0921', ticket: 'TK-C1', bruto: 17200, tara: 7200, cond: 'Íntegra', dcol: '2026-09-24' }));
  const L = r.L; const S0 = prSaldos(c, L);
  ok('U07a Íntegra e carência cumprida (' + d0 + ' dias de bula) → Liberado', !r.erro && typeof d0 === 'number' && d0 < 19 && S0.q === 'Liberado', [r.erro, d0, S0.q, S0.mot]);
  c.producao.pedidos['PV-T1'] = { id: 'PV-T1', cliente: 'Cliente teste', prod: MAM, cultura: 'Mamão Formosa', classe: '', saf: '', tipo: 'pronta', janela: '26/09', qtd: 5000, dest: 'MI-BR' };
  const rs = MUD(c, x => prReservar(x, { pedido: 'PV-T1', lote: L.id, kg: 5000, ator: 'Ana' }));
  const b = MUD(c, x => carc_bula(x, P, 'Mamão', 30)); const S1 = prSaldos(c, c.producao.lotes[L.id]); const sit = prSitPed(c, c.producao.pedidos['PV-T1']);
  ok('U07b bula corrigida para 30 dias DEPOIS do recebimento: o lote passa a Bloqueado (carência até 04/10) sem nada regravado', !rs.erro && !b.erro && S1.q === 'Bloqueado' && /carência até 04\/10/.test(S1.mot), [rs.erro, b.erro, S1]);
  ok('U07c a reserva já feita fica com a expedição impedida (pedido Em risco)', sit.t === 'Em risco' && sit.imp.length === 1, sit);
  const lb = MUD(c, x => prLiberarLote(x, L.id, 'Marta')); ok('U07d Liberar lote bloqueado por carência é recusado (só com laudo, fora)', /bloqueado por carência/.test(lb.erro || ''), lb);
  // dados insuficientes: aplicação em execução com saldo no talhão → Em inspeção, dono nomeado; Liberar recusa com a pendência
  const c2 = NOVO(); OSX(c2, 'OS-0922', 'Pivô 24', 'Em execução', [['20/09', 10]], 'Pulverização · ácaro', ['Abamectina 18 EC']); c2.ordens['OS-0922'].saldo = 24.37; c2.ordens['OS-0922'].resp = 'Wesley';
  OSX(c2, 'OS-0923', 'Pivô 24', 'Em execução', [['10/09', 10]], 'Colheita · semana 37');
  const r2 = MUD(c2, x => prReceber(x, { os: 'OS-0923', ticket: 'TK-C2', bruto: 17200, tara: 7200, cond: 'Íntegra', dcol: '2026-09-10' }));
  const S2 = prSaldos(c2, r2.L); const lb2 = MUD(c2, x => prLiberarLote(x, r2.L.id, 'Marta'));
  ok('U07e carência sem dados (aplicação em execução sem apontamento completo) → Em inspeção com dono (Wesley)', !r2.erro && S2.q === 'Em inspeção' && /Wesley/.test(S2.dono), [r2.erro, S2]);
  ok('U07f Liberar lote (Qualidade) recusa enquanto a pendência existir, com o dono', /Liberar recusado/.test(lb2.erro || '') && /Wesley/.test(lb2.erro), lb2);
  // avaria: Em inspeção; a Qualidade libera; colheita sem ordem liberada (ordem cancelada depois) volta a Em inspeção
  const c3 = NOVO(); const r3 = MUD(c3, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Com avaria' }));
  const S3 = prSaldos(c3, r3.L); const l3 = MUD(c3, x => prLiberarLote(x, r3.L.id, 'Marta')); const S3b = prSaldos(c3, c3.producao.lotes[r3.L.id]);
  ok('U07g Com avaria → Em inspeção (dono Qualidade); Liberar lote pela Qualidade → Liberado', S3.q === 'Em inspeção' && /Qualidade/.test(S3.dono) && !l3.erro && S3b.q === 'Liberado', [S3, l3.erro, S3b.q]);
  c3.ordens['OS-0505'].etapa = 'Canceladas'; ok('U07h colheita sem ordem liberada (O.S. cancelada) → Em inspeção', prSaldos(c3, c3.producao.lotes[r3.L.id]).q === 'Em inspeção', prSaldos(c3, c3.producao.lotes[r3.L.id])); }

/* Comercial A-17 (Codex 6070584991): a saca dos contratos de soja legados (PV-030 do CT-201, CT-203, CRE-0095, BT-090) está ambígua na semente
   (VE-05 oculto: sc 50 kg; Colheita D-19: 60 kg) e nada é convertido em silêncio. Os casos que medem falta e oferta registram antes a massa de
   60 kg com a fonte, pelo mesmo comando da tela (comConverterSaca) */
function SACA60(c, ids) { (ids || ['PV-030', 'CT-203', 'CRE-0095', 'BT-090']).forEach(id => { const r = MUD(c, x => comConverterSaca(x, { venda: id, fat: '60', fonte: 'Contrato ' + id + ' (teste)', ator: 'Ana', chave: 'T-SACA-' + id })); if (r.erro) throw new Error(r.erro); }); return c; }

// ---- U08 · saldos do L10-031 (AC-09) ----
{ const c = NOVO(); const S = prSaldos(c, c.producao.lotes['L10-031']); const T = x => prEstTxt('Soja', x);
  ok('U08 L10-031: físico 38.420 sc · bloqueado 0 · apto 38.420 · reservado 3.875 · disponível 34.545 sc', T(S.fis) === '38.420 sc' && S.blq === 0 && T(S.apto) === '38.420 sc' && T(S.res) === '3.875 sc' && T(S.disp) === '34.545 sc', S);
  /* expectativa mudada no Comercial (A-17): na semente a falta do PV-030 fica suspensa (saca a conferir); com 60 kg registrados, 7.500 kg */
  const s0 = prSitPed(c, c.producao.pedidos['PV-030']).t; SACA60(c, ['PV-030']);
  ok('U08b PV-030: na semente "Saca a conferir" (falta suspensa); com a saca de 60 kg registrada, falta 7.500 kg depois da RS-0001 (4.000 sc = 240.000 kg)', s0 === 'Saca a conferir' && prFalta(c, c.producao.pedidos['PV-030']) === 7500, [s0, prFalta(c, c.producao.pedidos['PV-030'])]); }

// ---- U09 · reserva: recusas (AC-10) ----
{ const c = SACA60(NOVO(), ['PV-030']); const e1 = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-131', kg: 1000, ator: 'Ana' }));
  ok('U09a lote Em processo (CAR0: mistura LM-39-01) não reserva', /não está apto/.test(e1.erro || '') && /Em processo/.test(e1.erro), e1);
  const e2 = MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 7501, ator: 'Ana' }));
  ok('U09b acima da falta do pedido (7.500 kg) é recusado', /Acima da falta/.test(e2.erro || ''), e2);
  MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' }));
  const e3 = MUD(c, x => prReservar(x, { pedido: 'PV-038', lote: 'L39-133', kg: 12051, ator: 'Ana' }));
  ok('U09c acima do disponível do lote é recusado', /Acima do disponível/.test(e3.erro || ''), e3);
  const e4 = MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L39-133', kg: 100, ator: 'Ana' }));
  ok('U09d produto diferente do pedido é recusado', /não atende o PV-030/.test(e4.erro || ''), e4);
  c.car = c.car || {}; c.car.laudos = [{ id: 'LAB-T9', escopo: ['LC-0505-2'], d: '2026-09-25', res: { tebuconazol: { v: 5, un: 'mg/kg', lq: 0.01 } } }];
  const e5 = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 1000, ator: 'Ana' }));
  ok('U09e destino do pedido Não conforme (laudo acima do limite da ANVISA) recusa a reserva, com quem decide', /Reserva recusada/.test(e5.erro || '') && /Não conforme/.test(e5.erro) && /Qualidade/.test(e5.erro), e5);
  c.car.laudos = []; const ok1 = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 4000, ator: 'Ana' }));
  const e6 = MUD(c, x => prCancelarReserva(x, ok1.rs.id, '', 'Ana'));
  const k6 = MUD(c, x => prCancelarReserva(x, ok1.rs.id, 'cliente adiou', 'Ana')); const S = prSaldos(c, c.producao.lotes['L39-133']);
  ok('U09f cancelar sem motivo é recusado; com motivo o disponível volta (12.050 kg)', /motivo/.test(e6.erro || '') && !k6.erro && S.disp === 12050, [e6, k6.erro, S.disp]);
  const k7 = MUD(c, x => prReservar(x, { pedido: 'PV-038', lote: 'L39-133', kg: 3000, ator: 'Ana' }));
  ok('U09g venda futura (PV-038) aceita reserva de lote apto (R-15)', !k7.erro && prSaldos(c, c.producao.lotes['L39-133']).disp === 9050, k7); }

// ---- U10 · venda futura não muda o físico; oferta livre (AC-11, K10, K14) ----
{ const c = NOVO(); const of0 = prOfertaSafra(c, 'Soja em grão', '2026/27'); SACA60(c); const of = prOfertaSafra(c, 'Soja em grão', '2026/27'); const T = x => prEstTxt('Soja', x);
  /* expectativa mudada no Comercial P1 (D-C04): CT-203, CRE-0095 e BT-090 saem do catálogo e entram no estado como vendas futuras; a oferta livre é a mesma.
     Comercial A-17: na semente a oferta livre fica suspensa (null) até registrar a saca dos três contratos; com 60 kg, 48.280 sc */
  ok('U10a0 soja 26/27 na semente: oferta livre suspensa (saca a conferir de CT-203, CRE-0095 e BT-090), nunca convertida pela unidade atual', of0.livre === null && of0.amb.join() === 'CT-203,CRE-0095,BT-090' && T(of0.pub) === '68.180 sc', of0);
  ok('U10a soja 26/27: oferta publicada 68.180 sc; vendas futuras do estado (CT-203, CRE-0095, BT-090) 19.900 sc; oferta livre 48.280 sc', T(of.pub) === '68.180 sc' && T(of.futKg) === '19.900 sc' && T(of.livre) === '48.280 sc' && of.fut.map(p => p.id).sort().join() === 'BT-090,CRE-0095,CT-203' && of.ob === undefined, [T(of.pub), T(of.futKg), T(of.livre), of.fut.map(p => p.id)]);
  ok('U10b o L10-031 continua com 34.545 sc disponíveis (a venda futura não desconta o físico)', T(prSaldos(c, c.producao.lotes['L10-031']).disp) === '34.545 sc');
  const s41 = prOfertaSem(c, MAM, '2026-W41'); ok('U10c S41 sem versão publicada: PV-038 aparece como déficit de 30.000 kg', s41.livre === -30000 && !s41.tem, s41);
  const pb = MUD(c, x => prPublicar(x, 'lg19', 'Ana (agrônoma)')); const s41b = prOfertaSem(c, MAM, '2026-W41');
  ok('U10d publicada a v2 do Pivô 19: oferta livre S41 = 57.337,908 kg (K14)', !pb.erro && s41b.livre === 57337.908 && pb.v.v === 2, [pb.erro, s41b]); }

// ---- U10e · Comercial A-17: o texto do compromisso usa a massa gravada nele, nunca a do cadastro atual (Estoque e VE-04 oculto, sem comercial.js) ----
{ const c = NOVO(); const ct = c.producao.pedidos['CT-203']; const t0 = prQtdTxt(ct);
  const r = MUD(c, x => comConverterSaca(x, { venda: 'CT-203', fat: '50', fonte: 'Contrato CT-203 (teste)', ator: 'Ana', chave: 'T-50' })); const ct2 = c.producao.pedidos['CT-203'];
  const m0 = PRDC.un['Soja'].massa; let t2 = ''; try { PRDC.un['Soja'].massa = 50; t2 = prQtdTxt(ct2); } finally { PRDC.un['Soja'].massa = m0; }
  ok('U10e CT-203: semente "12.000 sc (saca de 50 ou 60 kg a conferir)"; com 50 kg registrados, "12.000 sc 50 kg" (600.000 kg); com o cadastro da soja em 50 kg, "12.000 sc"; PV-036 continua "10.000 kg"',
     t0 === '12.000 sc (saca de 50 ou 60 kg a conferir)' && !r.erro && ct2.qtd === 600000 && prQtdTxt(ct2) === '12.000 sc 50 kg' && t2 === '12.000 sc' && prQtdTxt(c.producao.pedidos['PV-036']) === '10.000 kg', [t0, r.erro, ct2.qtd, prQtdTxt(ct2), t2]); }

// ---- U11 · contagem não publica; publicar congela só as semanas não começadas (AC-12, K08) ----
{ const c = NOVO(); const r0 = prRascunho(c, 'lg19');
  ok('U11a K08 rascunho do Pivô 19 pela CNT-0001: S40 72.781,59 kg; S41 87.337,908 kg', r0.sem['2026-W40'] === 72781.59 && r0.sem['2026-W41'] === 87337.908, r0.sem);
  ok('U11b K08 Pivô 6 (10 frutos, 62,79 ha) = 60.843,51 kg', prKgEstadio(62.79, 1700, 10, 20, '1.20', '0.05') === 60843.51);
  ok('U11c K09 sem contagem, pela meta: Pivô 2 = 36.298,076923 kg/semana, não publicado', prRascunho(c, 'lg02').sem['2026-W40'] === 36298.076923 && prRascunho(c, 'lg02').base === 'meta' && !(c.producao.previsoes.lg02 || []).length);
  const n = MUD(c, x => prContar(x, { cult: 'lg06', plantas: 20, pintado: 9, devez: 10, verde: 11, peso: '1,10', quem: 'Marcos', via: 'app', chave: 'APP-CNT-1' }));
  ok('U11d contar no app grava CNT-0002 e não publica (a versão vigente do Pivô 6 continua a v1)', !n.erro && n.cnt.id === 'CNT-0002' && c.producao.previsoes.lg06.length === 1, [n.erro, c.producao.previsoes.lg06.length]);
  const p = MUD(c, x => prPublicar(x, 'lg19')); const v = c.producao.previsoes.lg19[1];
  ok('U11e publicar congela v2 só com S40 e S41 (a S39 já começou: orienta a OS-0505)', !p.erro && Object.keys(v.sem).join() === '2026-W40,2026-W41' && /S39\) não muda: orienta a OS-0505/.test(p.msg), [p.erro, v, p.msg]);
  ok('U11f a referência do passe S39 continua a v1 (publicada antes da semana): 72.900 kg', prVersaoRef(c, 'lg19', '2026-W39').v === 1 && prVersaoRef(c, 'lg19', '2026-W39').sem['2026-W39'] === 72900);
  const p2 = MUD(c, x => prPublicar(x, 'lg19')); ok('U11g publicar de novo sem mudança é recusado', /Nada novo a publicar/.test(p2.erro || ''), p2); }

// ---- U12 · café: L, Em processo, sc a apurar (AC-13, R-09) ----
{ const c = NOVO(); OSX(c, 'OS-0930', 'C1', 'Em execução', [['25/09', 5]], 'Colheita de café');
  const r = MUD(c, x => prReceber(x, { quem: 'Rui', os: 'OS-0930', ticket: 'TK-CF1', bruto: 9200, tara: 3200, litros: 12000, cond: 'Íntegra', dcol: '2026-09-25' }));
  const S = r.L && prSaldos(c, r.L); const R = prResultado(c, 'c9');
  ok('U12 café: lote "Café da roça" em L, Em processo; produção em sc a apurar (0 sc, 12.000 L)', !r.erro && r.L.prod === 'Café da roça' && S.q === 'Em processo' && S.fis === 12000 && R.kg === 0 && R.cafe === 12000, [r.erro, S, R && R.kg, R && R.cafe]);
  const e = MUD(c, x => prReceber(x, { quem: 'Rui', os: 'OS-0930', ticket: 'TK-CF2', bruto: 9200, tara: 3200, cond: 'Íntegra', dcol: '2026-09-25' }));
  ok('U12b café sem litros é recusado', /litros/.test(e.erro || ''), e); }

// ---- U02e · grão: descontos na pesagem; umidade e impureza obrigatórias ----
{ const c = NOVO(); OSX(c, 'OS-0931', 'T1-A', 'Em execução', [['25/09', 20]], 'Colheita de grãos');
  const e = MUD(c, x => prReceber(x, { quem: 'Rui', os: 'OS-0931', ticket: 'TK-S0', bruto: 45000, tara: 15000, cond: 'Íntegra', dcol: '2026-09-25' }));
  const r = MUD(c, x => prReceber(x, { quem: 'Rui', os: 'OS-0931', ticket: 'TK-S1', bruto: 45000, tara: 15000, u: '16,5', imp: '2,0', cond: 'Íntegra', dcol: '2026-09-25' }));
  ok('U02e grão sem umidade é recusado; com 16,5 % e 2 %: comercial 28.836,627907 kg = 480,61 sc no lote do Silo 01 (bruto, descontos e comercial separados)', /umidade/.test(e.erro || '') && !r.erro && r.g.com === 28836.627907 && r.g.desc.dImp === 300 && r.L.local === 'l6' && prUnTxt('Soja', prFis(c, r.L.id)) === '480,61 sc', [e.erro, r.erro, r.g && r.g.desc]); }

// ---- U13 · estorno (AC-14, R-19) ----
{ const c = NOVO(); MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' }));
  MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 10000, ator: 'Ana' }));
  const e = MUD(c, x => prEstornar(x, 'CG-2108', 'ticket trocado')); ok('U13a estorno que deixaria o lote abaixo do reservado é recusado', /abaixo do reservado/.test(e.erro || ''), e);
  const e0 = MUD(c, x => prEstornar(x, 'CG-2108', '')); ok('U13b estorno sem motivo é recusado', /motivo/.test(e0.erro || ''), e0);
  MUD(c, x => prCancelarReserva(x, 'RS-0002', 'refazer pesagem', 'Ana'));
  const ok1 = MUD(c, x => prEstornar(x, 'CG-2108', 'ticket trocado')); const g = c.producao.cargas['CG-2108'];
  ok('U13c estorno com motivo: lote volta a 0 kg, carga Estornada, produção do Pivô 19 volta a 36,42 t e o histórico fica', !ok1.erro && prFis(c, 'L39-133') === 0 && g.st === 'Estornada' && prResultado(c, 'lg19').kg === 36420 && c.producao.movs.some(m => m.tipo === 'estorno'), [ok1.erro, prFis(c, 'L39-133')]);
  const nv = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-4520', bruto: 19200, tara: 7200, cond: 'Íntegra', dcol: '2026-09-22' }));
  ok('U13d o ticket estornado fica livre para novo registro', !nv.erro, nv); }

// ---- U14 · encerrar O.S. de colheita com carga a pesar (AC-15, R-18), pelo comando da O.S. ----
// v57: a conferência diária (CONTROLE-02, PR #55) vale para toda O.S. agrícola; o dia 2 da OS-0505 é conferido antes de encerrar
const CONF_DIA = (x, id, dia) => cdConferir(x, id, dia, 'conferir', 'apontamento conferido com o ticket', cdReferencia(x, id, dia), G2_PERFIS.find(p => p.k === 'Paula'));
{ const c = NOVO(); c.ordens['OS-0505'].etapa = 'Em conferência'; c.ordens['OS-0505'].saldo = 0;
  const e = MUD(c, x => osc_encerrar(x, 'OS-0505'));
  ok('U14a Encerrar a OS-0505 com a CG-2108 a pesar é recusado com dono (Lúcia)', /Encerrar bloqueado/.test(e.erro || '') && /CG-2108/.test(e.erro) && /Lúcia/.test(e.erro), e);
  MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' }));
  MUD(c, x => CONF_DIA(x, 'OS-0505', 2));
  const ok2 = MUD(c, x => osc_encerrar(x, 'OS-0505')); ok('U14b pesada a carga, encerrar passa; o passe S39 fica final', !ok2.erro && prResultado(c, 'lg19').passes[0].final, ok2); }

// ---- U15 · carga sem sinal: fora da web até o sinal; entra uma vez (AC-16) ----
{ const c = NOVO(); MUD(c, x => cenSinal(x, false));
  const g = MUD(c, x => prCarga(x, { os: 'OS-0505', cx: 280, veic: 'Carreta 02', chave: 'APP-CG-OFF', via: 'app', quem: 'Marcos' }));
  const web = () => prCargas(c, x => x.sinc !== false).map(x => x.id);
  ok('U15a sem sinal: a carga fica no aparelho (fora da lista da web) e a O.S. não encerra', !g.erro && g.g.sinc === false && web().indexOf(g.g.id) < 0 && /aguardando sinal/.test(prPodeEncerrar(c, 'OS-0505')), [g.erro, web()]);
  MUD(c, x => cenSinal(x, true)); const n1 = web().length; MUD(c, x => cenSinal(x, true));
  ok('U15b ao voltar o sinal entra uma vez (repetir o envio não duplica)', web().indexOf(g.g.id) >= 0 && web().length === n1 && !(c.app.fila || []).length, web()); }

// ---- U16 · semente respeita o CAR0; T7 no Packing nasce Em processo (AC-21) ----
{ const c = NOVO(); const L = c.producao.lotes; const q = id => prSaldos(c, L[id]);
  ok('U16a L38-132, L39-131 e L39-132 Em processo com a operação do CAR0 como motivo (imersão, mistura, divisão)', q('L38-132').q === 'Em processo' && /Tiabendazol/.test(q('L38-132').mot) && /LM-39-01/.test(q('L39-131').mot) && /Dividido/.test(q('L39-132').mot), [q('L38-132').mot, q('L39-131').mot, q('L39-132').mot]);
  const aptoM = prSoma(Object.values(L).filter(x => x.prod === MAM).map(x => q(x.id).apto)); const proc = prSoma(Object.values(L).filter(x => x.prod === MAM && !x.abertura).map(x => q(x.id).proc));
  const procPk = prSoma(Object.values(L).filter(x => x.prod === MAM && x.abertura).map(x => q(x.id).proc));
  ok('U16b apto de mamão na semente = 0; 66.250 kg da colheita fora do acabado (+ 21.270 kg do packing do BEN-1, saldo de abertura); L38-131 expedido ao PV-037 (físico 0, 30.490 kg)', aptoM === 0 && proc === 66250 && procPk === 21270 && q('L38-131').fis === 0 && prExpedido(c, 'PV-037') === 30490, [aptoM, proc, procPk]);
  OSX(c, 'OS-0932', 'T7', 'Em execução', [['25/09', 6]], 'Colheita · semana 39');
  const r = MUD(c, x => prReceber(x, { quem: 'Rui', os: 'OS-0932', ticket: 'TK-T7', bruto: 9400, tara: 3200, cond: 'Íntegra', dcol: '2026-09-25' }));
  ok('U16c carga do T7 vai ao l8 Packing (tipo Packing, D-24) e nasce Em processo', !r.erro && r.L.local === 'l8' && prSaldos(c, r.L).q === 'Em processo' && PRDC.locais.l8.tipo === 'Packing', [r.erro, r.L && r.L.local]);
  ok('U16d seq da semente: próxima carga CG-2109, próximo lote da S39 L39-133, próxima reserva RS-0002, próximo MP-1019 (MP-1011..1018: saldos de abertura do packing, BEN-1)', CEN0.producao.seq.cg === 2108 && CEN0.producao.seq.lote['39'] === 132 && CEN0.producao.seq.rs === 1 && CEN0.producao.seq.mp === 1018); }

// ---- U15c · contagem sem sinal: fica no aparelho, não vira rascunho; ao voltar o sinal entra uma vez (R-07, AC-16) ----
{ const c = NOVO(); MUD(c, x => cenSinal(x, false));
  const n = MUD(c, x => prContar(x, { cult: 'lg06', plantas: 20, pintado: 9, devez: 10, verde: 11, peso: '1,10', quem: 'Marcos', via: 'app', chave: 'APP-CNT-OFF' }));
  ok('U15c contagem sem sinal fica no aparelho (fila) e não entra no rascunho do Pivô 6', !n.erro && n.cnt.sinc === false && c.app.fila.indexOf(n.cnt.id) >= 0 && prContagem(c, 'lg06') === null, [n.erro, c.app.fila]);
  MUD(c, x => cenSinal(x, true)); MUD(c, x => cenSinal(x, true)); const r = MUD(c, x => prContar(x, { cult: 'lg06', plantas: 20, pintado: 9, devez: 10, verde: 11, peso: '1,10', quem: 'Marcos', via: 'app', chave: 'APP-CNT-OFF' }));
  ok('U15d ao voltar o sinal a contagem entra uma vez; reenviar a mesma chave não cria outra', prContagem(c, 'lg06') && prContagem(c, 'lg06').id === n.cnt.id && r.repetido && c.producao.contagens.length === 2, [prContagem(c, 'lg06'), r]); }

// =====================================================================================================================
// Revisão adversarial (Codex, 06/10/2026) · uma regressão por achado (A-01..A-19) e pelos mutantes que sobreviviam
// =====================================================================================================================
const TEB = (c, dap) => { c.ordens['OS-0999'] = { id: 'OS-0999', tipo: 'Pulverização · antracnose', talhao: 'Pivô 19', area: 75.11, etapa: 'Encerradas', versao: 'v1', realizado: 75.11, saldo: 0, resp: 'Wesley',
  ins: [{ p: 'Tebuconazol 200 EC', dose: 1, un: 'L', tot: 75.11 }], req: null, selos: [], ap: [{ d: dap, dia: 1, ha: 75.11, st: 'Conferido', sinc: true, origem: 'web' }], reservado: false, osc: {} }; };
// ---- A-01 (S1 cond.) · o dia da colheita decide a carência: dia sem apontamento somado na O.S. deixa o lote Em inspeção ----
{ const c = NOVO(); TEB(c, '19/09');
  const r = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-D1', bruto: 19200, tara: 7200, cond: 'Íntegra', dcol: '2026-09-26' })); const S = r.L && prSaldos(c, r.L);
  ok('R01a carga "colhida" em 26/09 sem apontamento da OS-0505 nesse dia: lote Em inspeção, dono Sérgio (não Liberado)', !r.erro && S.q === 'Em inspeção' && S.dono === 'Sérgio' && /sem apontamento de área da OS-0505/.test(S.mot), [r.erro, S]);
  const rs = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: r.L.id, kg: 10000, chave: 'W-R01', ator: 'Ana' })); const lb = MUD(c, x => prLiberarLote(x, r.L.id, 'Marta'));
  ok('R01b esse lote não é reservado e a Qualidade não o libera enquanto o dia não for confirmado (quem resolve: Sérgio)', /não está apto/.test(rs.erro || '') && /Liberar recusado/.test(lb.erro || '') && /Sérgio/.test(lb.erro), [rs.erro, lb.erro]);
  const c2 = NOVO(); TEB(c2, '19/09'); MUD(c2, x => cenApontar(x, { os: 'OS-0505', d: '25/09', ha: 10, h: 4, origem: 'app', quem: 'Marcos', chave: 'APC-R01-25' }));
  const r2 = MUD(c2, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-D2', bruto: 19200, tara: 7200, cond: 'Íntegra', dcol: '2026-09-25' }));
  ok('R01c o dia real (25/09, apontado) cai na carência do Tebuconazol: Bloqueado', !r2.erro && prSaldos(c2, r2.L).q === 'Bloqueado', [r2.erro, r2.L && prSaldos(c2, r2.L)]);
  MUD(c, x => cenApontar(x, { os: 'OS-0505', d: '26/09', ha: 10, h: 4, origem: 'app', quem: 'Marcos', chave: 'APC-R01-26' }));
  ok('R01d apontada a área de 26/09 (fato que chega depois), o lote de 26/09 (fora da carência) passa a Liberado sem regravar', prSaldos(c, c.producao.lotes[r.L.id]).q === 'Liberado', prSaldos(c, c.producao.lotes[r.L.id]));
  const c0 = NOVO(); ok('R01e (M17) o lote de campo só nasce de apontamento somado: 24/09 Previsto (semente) não gera LC-; 22/09 Provisório gera', c0.ordens['OS-0505'].ap.some(x => x.d === '24/09' && x.st === 'Previsto') && prLc(c0, 'OS-0505', '2026-09-24') === '' && /^LC-/.test(prLc(c0, 'OS-0505', '2026-09-22')),
     [prLc(c0, 'OS-0505', '2026-09-24'), prLc(c0, 'OS-0505', '2026-09-22')]); }

// ---- A-02 (S2) · número pt-BR com ponto de milhar ----
ok('R02a prNum: "19.250" = 19.250; "1.234.567,8"; "1,20" = 1,2; "1.20" = 1,2; "12abc" e "1,2,3" recusados', prNum('19.250') === 19250 && prNum('1.234.567,8') === 1234567.8 && prNum('1,20') === 1.2 && prNum('1.20') === 1.2 && isNaN(prNum('12abc')) && isNaN(prNum('1,2,3')) && !prNumOk('abc') && prNumOk('7.200'),
   [prNum('19.250'), prNum('1.234.567,8'), prNum('1,20'), prNum('1.20'), prNum('12abc')]);
{ const c = NOVO(); const r = MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: '19.250', tara: '7.200', cond: 'Íntegra', chave: 'W-REC-CG-2108' }));
  ok('R02b pesar com "19.250" e "7.200" (como no ticket): 12.050 kg líquidos, não 12,05', !r.erro && r.g.liq === 12050 && prFis(c, r.L.id) === 12050, [r.erro, r.g && r.g.liq]); }

// ---- A-03 (S2) · reservar, cancelar e reservar de novo (chave nova do formulário); mesma chave e outro conteúdo = conflito (M34) ----
{ const c = NOVO(); MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' }));
  const a = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 10000, chave: 'W-RS-k1', ator: 'Ana' }));
  const x8 = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 8000, chave: 'W-RS-k1', ator: 'Ana' }));
  ok('R03a (M34) mesma chave com outra quantidade = conflito, nada deduzido', !a.erro && /conflito/.test(x8.erro || '') && prResPed(c, 'PV-036').length === 1, [a.erro, x8]);
  MUD(c, x => prCancelarReserva(x, a.rs.id, 'cliente adiou', 'Ana'));
  const b = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 10000, chave: 'W-RS-k2', ator: 'Ana' }));
  ok('R03b depois de cancelar, a reserva com a chave do novo formulário fica ativa (PV-036 coberto)', !b.erro && !b.repetido && prResPed(c, 'PV-036').length === 1 && prSitPed(c, c.producao.pedidos['PV-036']).t === 'Coberto', [b.erro, b.repetido, prResPed(c, 'PV-036').length]); }

// ---- A-04 (S2) · O.S. de colheita com carga não é cancelada "sem execução" ----
{ const c = NOVO(); OSX(c, 'OS-0950', 'Pivô 19', 'Liberadas', [], 'Colheita · semana 40'); c.ordens['OS-0950'].saldo = 75.11; c.ordens['OS-0950'].area = 75.11;
  const r = MUD(c, x => prReceber(x, { os: 'OS-0950', ticket: 'TK-L1', bruto: 19200, tara: 7200, cond: 'Íntegra', dcol: '2026-09-26' }));
  const k = MUD(c, x => osc_cancelar(x, 'OS-0950', 'engano', ['', 'Cancelada.', ''], {k:'Ana'}));
  ok('R04a cancelar sem execução a OS-0950 com carga recebida é recusado; a ordem continua Liberadas e a produção fica', !r.erro && /Cancelar recusado/.test(k.erro || '') && new RegExp(r.g.id).test(k.erro) && c.ordens['OS-0950'].etapa === 'Liberadas' && prResultado(c, 'lg19').kg === 48420, [r.erro, k.erro, prResultado(c, 'lg19').kg]);
  MUD(c, x => prEstornar(x, r.g.id, 'ordem errada')); const g = MUD(c, x => prCarga(x, { os: 'OS-0950', cx: 100, veic: 'Carreta 01', chave: 'APP-R04', via: 'app', quem: 'Marcos' }));
  const k2 = MUD(c, x => osc_cancelar(x, 'OS-0950', 'engano', ['', 'Cancelada.', ''], {k:'Ana'}));
  MUD(c, x => prDescartarCarga(x, g.g.id, 'registrada por engano', 'Marcos')); const k3 = MUD(c, x => osc_cancelar(x, 'OS-0950', 'engano', ['', 'Cancelada.', ''], {k:'Ana'}));
  ok('R04b com carga a pesar também recusa; estornada a recebida e descartada a a pesar, o cancelamento passa', /Cancelar recusado/.test(k2.erro || '') && !k3.erro && c.ordens['OS-0950'].etapa === 'Canceladas', [k2.erro, k3.erro]); }

// ---- A-05 (S2) · carga com avaria não entra apta no lote que a Qualidade liberou; condições diferentes não se juntam (M22) ----
{ const c = NOVO(); const a = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-A1', bruto: 12000, tara: 7200, cond: 'Com avaria', dcol: '2026-09-22' }));
  MUD(c, x => prLiberarLote(x, a.L.id, 'Marta'));
  const b = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-A2', bruto: 15000, tara: 7200, cond: 'Com avaria', dcol: '2026-09-22' }));
  ok('R05a 2ª carga com avaria depois da liberação: lote novo Em inspeção; o liberado continua com 4.800 kg aptos', !b.erro && b.L.id !== a.L.id && prSaldos(c, b.L).q === 'Em inspeção' && prSaldos(c, c.producao.lotes[a.L.id]).apto === 4800, [b.erro, b.L && b.L.id, a.L.id]);
  const d = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-A3', bruto: 9000, tara: 7200, cond: 'Fora do padrão', dcol: '2026-09-22' }));
  const e = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-A4', bruto: 9000, tara: 7200, cond: 'Com avaria', dcol: '2026-09-22' }));
  ok('R05b (M22) "Fora do padrão" não entra no lote "Com avaria" do mesmo dia; outra avaria junta-se ao lote em inspeção', !d.erro && d.L.id !== b.L.id && !e.erro && e.L.id === b.L.id, [d.L && d.L.id, e.L && e.L.id, b.L.id]); }

// ---- A-06 (S2) · descartar carga A pesar (registro em dobro) destrava o encerramento ----
{ const c = NOVO(); MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' }));
  const g = MUD(c, x => prCarga(x, { os: 'OS-0505', cx: 300, veic: 'Carreta 02', chave: 'APP-R06', via: 'app', quem: 'Marcos' }));
  c.ordens['OS-0505'].etapa = 'Em conferência'; c.ordens['OS-0505'].saldo = 0;
  const e0 = MUD(c, x => prDescartarCarga(x, g.g.id, '')); const e1 = MUD(c, x => prDescartarCarga(x, 'CG-2108', 'teste'));
  ok('R06a descartar exige motivo e só vale para carga a pesar (recebida: estorne)', /motivo/.test(e0.erro || '') && /só carga a pesar/.test(e1.erro || '') && /estorne/.test(e1.erro), [e0.erro, e1.erro]);
  const enc0 = MUD(c, x => osc_encerrar(x, 'OS-0505')); const ds = MUD(c, x => prDescartarCarga(x, g.g.id, 'registrada duas vezes no app', 'Lúcia'));
  MUD(c, x => CONF_DIA(x, 'OS-0505', 2));
  const enc = MUD(c, x => osc_encerrar(x, 'OS-0505'));
  ok('R06b a carga fantasma impede encerrar; descartada (motivo e trilha), a O.S. encerra e a produção não muda', /Encerrar bloqueado/.test(enc0.erro || '') && !ds.erro && c.producao.cargas[g.g.id].st === 'Descartada' && c.producao.cargas[g.g.id].descarte.motivo === 'registrada duas vezes no app' && !enc.erro && prResultado(c, 'lg19').kg === 48470,
     [enc0.erro, ds.erro, enc.erro]); }

// ---- A-07 (S2) · ticket com outra grafia não duplica ----
{ const c = NOVO(); MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' }));
  const a = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'tk-4520', bruto: 24000, tara: 7200, cond: 'Íntegra', dcol: '2026-09-22' }));
  const b = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK 4520', bruto: 19250, tara: 7200, cond: 'Íntegra', dcol: '2026-09-22' }));
  ok('R07 "tk-4520" (outro peso) = conflito; "TK 4520" (mesmo conteúdo) = a mesma carga; produção do Pivô 19 fica 48.470 kg', /conflito/.test(a.erro || '') && /CG-2108/.test(a.erro) && b.repetido && prResultado(c, 'lg19').kg === 48470 && prTk('tk 45-20') === '4520',
     [a.erro, b, prResultado(c, 'lg19').kg]); }

// ---- A-08 (S2) · mistura só da mesma cultura e fazenda ----
{ const c = NOVO(); const soja = Object.keys(PRDC.cult).find(k => PRDC.cult[k].cultura === 'Soja'); OSX(c, 'OS-0960', PRDC.cult[soja].local, 'Em execução', [['25/09', 10]], 'Colheita de grãos'); PRDC.osCult['OS-0960'] = soja;
  const r = MUD(c, x => prReceber(x, { mix: [{ os: 'OS-0505', pct: 60 }, { os: 'OS-0960', pct: 40 }], ticket: 'TK-MX', bruto: 17200, tara: 7200, cond: 'Íntegra', dcol: '2026-09-22' }));
  const g = MUD(c, x => prCarga(x, { os: 'OS-0505', mix: [{ os: 'OS-0505', pct: 60 }, { os: 'OS-0960', pct: 40 }], cx: 10, veic: 'Carreta 01', chave: 'APP-MX', via: 'app' }));
  ok('R08 mamão (Lagoa Grande) + soja (' + PRDC.cult[soja].faz + ') na mesma carga é recusado na web e no app; a soja não ganha kg; a lista do 2º talhão não oferece a O.S. de soja',
     /Mistura recusada/.test(r.erro || '') && /Mistura recusada/.test(g.erro || '') && prResultado(c, soja).kg === 0 && prMixCompat(c, 'OS-0505').every(o => o.id !== 'OS-0960'), [r.erro, g.erro]);
  delete PRDC.osCult['OS-0960']; }

// ---- A-11 (S3) · carga sem sinal: quem resolve é quem tem o aparelho, não o recebimento ----
{ const c = NOVO(); MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' }));
  MUD(c, x => cenSinal(x, false)); MUD(c, x => prCarga(x, { os: 'OS-0505', cx: 200, veic: 'Carreta 02', chave: 'APP-R11', via: 'app', quem: 'Marcos' }));
  c.ordens['OS-0505'].etapa = 'Em conferência'; c.ordens['OS-0505'].saldo = 0; const m = cenPodeEncerrar(c, 'OS-0505');
  const b = osEncBloq({ encM: m, dono: 'Lúcia', resp: 'Sérgio', r: null });
  ok('R11 encerrar com carga no aparelho: "Sérgio reconecta o app", sem link de pesar e sem "Lúcia pesa"', /^Carga no aparelho/.test(m) && /Sérgio reconecta o app/.test(b.q) && !b.h && !/Lúcia/.test(b.q), [m, b]); }

// ---- A-12 (S3) · sugestão de reserva arredondada para baixo nunca passa do disponível ----
ok('R12 sugestão em sc para baixo: 28.836,65 kg → 480,61 sc (≤ disponível); 59,99 kg → 0,999 sc', prPiso(prEstQ('Soja', 28836.65), 3) === 480.61 && prCmp(prEstBase('Soja', prPiso(prEstQ('Soja', 28836.65), 3)), 28836.65) <= 0 && prPiso(prEstQ('Soja', 59.99), 3) === 0.999 && prPiso(-1.0005, 3) === -1.001,
   [prPiso(prEstQ('Soja', 28836.65), 3), prPiso(prEstQ('Soja', 59.99), 3)]);

// ---- A-13 (S3) · "Liberar lote" só quando a pendência é da Qualidade ----
{ const c = NOVO(); const a = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-Q1', bruto: 19200, tara: 7200, cond: 'Íntegra', dcol: '2026-09-26' }));
  const n1 = prLoteProx(c, a.L, prSaldos(c, a.L)); const b = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-Q2', bruto: 9200, tara: 7200, cond: 'Com avaria', dcol: '2026-09-22' })); const n2 = prLoteProx(c, b.L, prSaldos(c, b.L));
  ok('R13 pendência do Sérgio (dia sem apontamento): "Sérgio resolve", sem ação; avaria: "Liberar lote · Qualidade (Marta)"', !n1.a && /^Sérgio resolve/.test(n1.t) && n2.a === 'liberar' && /Qualidade \(Marta\)/.test(n2.t), [n1, n2]); }

// ---- A-19 (S4) · ano da semana e do dd/mm ----
ok('R19 "semana 2" lida em 26/09/2026 = 2027-W02; "semana 39" = 2026-W39; janela ISO da ordem nova vale; 30/12 em 02/01/2027 = 2026-12-30; 27/09 em 26/09 continua futuro',
   prSemAno(2) === '2027-W02' && prSemAno(39) === '2026-W39' && prSemDaOS({ tipo: 'Colheita · semana 2' }) === '2027-W02' && prSemDaOS({ tipo: 'Colheita · semana 39' }) === '2026-W39' && prSemDaOS({ tipo: 'Colheita · semana 39', osc: { novo: { jan: '2027-10-04' } } }) === '2027-W40' && prIsoDe('30/12', '2027-01-02') === '2026-12-30' && prIsoDe('27/09') === '2026-09-27',
   [prSemAno(2), prSemAno(39), prSemDaOS({ tipo: 'x', osc: { novo: { jan: '2027-10-04' } } }), prIsoDe('30/12', '2027-01-02')]);

// ---- mutantes que sobreviviam (revisão: M02, M09, M11, M12, M23, M24, M26, M32, M36, M39, M40) ----
{ const c = NOVO(); OSX(c, 'OS-0961', 'Pivô 24', 'A liberar', [], 'Colheita · semana 40');
  const m02 = MUD(c, x => prReceber(x, { os: 'OS-0961', ticket: 'TK-M02', bruto: 9200, tara: 7200, cond: 'Íntegra', dcol: '2026-09-22' }));
  ok('M02 carga de O.S. de colheita em A liberar é recusada (R-06)', /está em A liberar/.test(m02.erro || ''), m02);
  const m23 = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-M23', bruto: 9200, tara: 7200, cond: 'Íntegra', dcol: '2026-09-27' }));
  const m24 = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-M24', bruto: 9200, tara: -1, cond: 'Íntegra', dcol: '2026-09-22' }));
  ok('M23 colheita depois de hoje é recusada; M24 tara negativa é recusada', /depois de hoje/.test(m23.erro || '') && /tara/.test(m24.erro || ''), [m23.erro, m24.erro]);
  MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra', chave: 'W-M39a' }));
  const m39 = MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4521', bruto: 19250, tara: 7200, cond: 'Íntegra', chave: 'W-M39b' }));
  ok('M39 pesar de novo uma carga já recebida é recusado', /já está recebida/.test(m39.erro || ''), m39);
  OSX(c, 'OS-0931', 'T1-A', 'Em execução', [['25/09', 20]], 'Colheita de grãos');
  const m40 = MUD(c, x => prReceber(x, { quem: 'Rui', os: 'OS-0931', ticket: 'TK-M40', bruto: 45000, tara: 15000, u: '41', imp: '1', cond: 'Íntegra', dcol: '2026-09-25' }));
  ok('M40 umidade acima de 40 % é recusada', /umidade/.test(m40.erro || ''), m40);
  const m36a = MUD(c, x => prPublicar(x, 'lg19', 'Ana (agrônoma)', { plantas_ha: 1700, perda: 1.5 })); const m36b = MUD(c, x => prPublicar(x, 'lg19', 'Ana (agrônoma)', { plantas_ha: 1700, perda: -0.1 }));
  ok('M36 perda fora de 0 a 100 % é recusada ao publicar', /Perda entre/.test(m36a.erro || '') && /Perda entre/.test(m36b.erro || ''), [m36a.erro, m36b.erro]);
  ok('M26 a falta desconta o expedido: PV-037 (30.490 kg expedidos) sem falta', prFalta(c, c.producao.pedidos['PV-037']) === 0, prFalta(c, c.producao.pedidos['PV-037']));
  MUD(c, x => prEstornar(x, 'CG-2108', 'teste'));
  const lg = c.producao.lotes[c.producao.cargas['CG-2108'].lote] || { origem: [] }; const og = lg.origem.find(x => x.carga === 'CG-2108') || {};
  ok('M32 estorno marca a origem do lote (sai do lote de campo e da qualidade)', og.est === true && prLcs(c, lg).length === 0, lg.origem); }
{ const c = NOVO(); const sem = c.producao.pedidos['PV-038'].sem; const f0 = prOfertaSem(c, MAM, sem);
  MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' })); MUD(c, x => prReservar(x, { pedido: 'PV-038', lote: 'L39-133', kg: 3000, chave: 'W-M09', ator: 'Ana' }));
  const f1 = prOfertaSem(c, MAM, sem);
  ok('M09 reserva de lote para venda futura sai da oferta comprometida: oferta livre ' + sem + ' sobe 3.000 kg', prSub(f1.livre, f0.livre) === 3000 && f1.resKg === 3000, [f0.livre, f1.livre]);
  const v1 = c.producao.previsoes.lg19[0]; c.producao.previsoes.lg19.push(Object.assign({}, v1, { v: 2, d: prSemIni('2026-W39'), sem: { '2026-W39': 1 } }));
  ok('M11 versão publicada no 1º dia da semana não é a referência do passe (só a publicada antes)', prVersaoRef(c, 'lg19', '2026-W39').v === 1, prVersaoRef(c, 'lg19', '2026-W39'));
  const so = Object.keys(PRDC.cult).find(k => PRDC.cult[k].cultura === 'Soja' && !PRDC.cult[k].semanal); const kk = PRDC.cult[so];
  OSX(c, 'OS-0962', kk.local, 'Em execução', [['20/09', prSoma([kk.area, 10])]], 'Colheita de grãos'); PRDC.osCult['OS-0962'] = so;
  ok('M12 anual: área colhida limitada à área do cultivo (' + kk.area + ' ha), mesmo com apontamento maior', prResultado(c, so).area === kk.area, prResultado(c, so).area); delete PRDC.osCult['OS-0962']; }

// =====================================================================================================================
// U21 · UNID-PROD · defeitos reproduzidos (falham na base 47ff754; só usam funções que já existiam lá, cada conta isolada em try)
// =====================================================================================================================
{ const T = (f) => { try { return f(); } catch (e) { return 'ERRO ' + String(e.message || e); } }; const c0 = cenClone(CEN0);
  // RC-09 (S3): o rascunho "pela meta" multiplicava por 1000 fixo, supondo a meta em t/ha: 50.000 kg/ha/ano viravam 36,3 milhões de kg na semana
  const lg = PRDC.cult.lg02; const m0 = [lg.meta, lg.un_meta]; const a = T(() => prRascunho(c0, 'lg02').sem); lg.meta = 50000; lg.un_meta = 'kg/ha/ano';
  const b = T(() => prRascunho(c0, 'lg02').sem); lg.meta = m0[0]; lg.un_meta = m0[1];
  ok('U21a RC-09 (K-U12) rascunho pela meta pelo conversor: Pivô 2 = 36.298,076923 kg/semana com 50 t/ha/ano e com 50.000 kg/ha/ano (sem × 1000 fixo)',
     a && Object.values(a)[0] === 36298.076923 && JSON.stringify(a) === JSON.stringify(b), [a, b]);
  // R-U09 (S2 latente): o desvio comparava a produtividade no Padrão com o número da meta sem ler a unidade gravada (k.un_meta)
  const so = Object.keys(PRDC.cult).find(k => PRDC.cult[k].cultura === 'Soja' && !PRDC.cult[k].semanal); const ks = PRDC.cult[so];
  PRDC.cult.tu2 = Object.assign({}, ks, { id: 'tu2', area: 10, meta: 25, un_meta: 'sc/ha', prod: true }); PRDC.osCult['OS-0973'] = 'tu2';
  const c = cenClone(CEN0); OSX(c, 'OS-0973', ks.local, 'Em execução', [['25/09', 10]], 'Colheita de grãos');
  const g = MUD(c, x => prReceber(x, { os: 'OS-0973', ticket: 'TK-U73', bruto: 30000, tara: 15000, u: '14', imp: '1', cond: 'Íntegra', dcol: '2026-09-25' }));
  const D = (m, u) => { PRDC.cult.tu2.meta = m; PRDC.cult.tu2.un_meta = u; return T(() => prResultado(c, 'tu2').desv); };
  const d1 = D(25, 'sc/ha'), d2 = D(1.5, 't/ha'), d3 = D(1200, 'kg/ha'); delete PRDC.cult.tu2; delete PRDC.osCult['OS-0973'];
  ok('U21b R-U09 desvio com a unidade gravada na meta: 1.500 kg/ha contra 25 sc/ha, 1,5 t/ha e 1.200 kg/ha = 0 %, 0 % e +25 % (a base dava +1.566,7 % com 1,5 t/ha)',
     !g.erro && d1 === 0 && d2 === 0 && d3 === 25, [g.erro, d1, d2, d3]);
  // R-U08 (S2): a ponderada somava produtos e estágios diferentes (café da roça com café beneficiado) sem recusar
  const e1 = T(() => prPonderada([{ k: { cultura: 'Café' }, kg: 3000, area: 5 }, { k: { cultura: 'Café' }, kg: 6000, area: 5, estagio: 'campo' }]));
  ok('U21c R-U08 café beneficiado × café da roça na mesma ponderada é recusado (a base somava 9.000 kg em 10 ha)',
     e1 === 'ERRO Produtos ou estágios diferentes não se agregam: Café beneficiado × Café da roça.', e1);
  ok('U21d o catálogo volta ao original (lg02, tu2, OS-0973)', PRDC.cult.lg02.meta === m0[0] && PRDC.cult.lg02.un_meta === m0[1] && !PRDC.cult.tu2 && !PRDC.osCult['OS-0973']); }

// =====================================================================================================================
// U20 · UNID-PROD: unidade de produtividade selecionável (docs/unidades-produtividade/ESPECIFICACAO.md v1.1 §6 e §8; contas K-U01..K-U14
// em docs/unidades-produtividade/verificacao/contas.py). Conversor único (prUnp*); a troca é exibição: nada muda no cenário.
// =====================================================================================================================
{ const TX = (cu, X, k) => prUnpTxt(prUnpInd(cu, X, k)); const KS = (cu, est, X) => prUnpOpcoes(cu, est || 'base', X).map(o => o.k);
  const ERR = (f) => { try { f(); return ''; } catch (e) { return String(e.message || e); } };
  // AC-a · K-U01: 6.000 kg/ha = 6 t/ha = 100 sc60 eq./ha, nos dois sentidos (soja tem sc 60 kg como Padrão; o mamão mostra a equivalência)
  const S6 = { kg: 60000, area: 10 };
  ok('U20a K-U01 6.000 kg/ha ↔ 6 t/ha ↔ 100 sc/ha (soja) ↔ 100 sc60 eq./ha (mamão): a volta é multiplicação exata',
     TX('Soja', S6, 'kg') === '6.000,00 kg/ha' && TX('Soja', S6, 't') === '6,00 t/ha' && TX('Soja', S6, 'padrao') === '100,00 sc/ha'
     && TX('Mamão Formosa', S6, 'sc60') === '100,00 sc60 eq./ha de Mamão Formosa · fruta de campo' && TX('Mamão Formosa', S6, 'kg') === '6.000,00 kg/ha'
     && prUnpKgHa('Soja', 100, 'sc/ha') === 6000 && prUnpKgHa('Soja', 6, 't/ha') === 6000 && prUnpKgHa('Mamão Formosa', 100, 'sc60 eq./ha') === 6000 && prUnpInd('Soja', S6, 't').kgHa === 6000,
     [TX('Soja', S6, 'kg'), TX('Soja', S6, 't'), TX('Soja', S6, 'padrao'), TX('Mamão Formosa', S6, 'sc60')]);
  // AC-b · K-U02: massa declarada (algodão @ 15 kg; arroz RS sc 50 kg com a sc 60 separada; cx 10 kg do mamão vinda do EMB_PACK)
  const al = prUnpOpcoes('Algodão em caroço', 'base'); const ar = prUnpOpcoes('Arroz RS', 'base');
  ok('U20b K-U02 algodão em caroço 4.526 kg/ha = 301,73 @/ha (Padrão "@/ha (15 kg)"); arroz RS 9.044 kg/ha = 180,88 sc/ha (50 kg) e 150,73 sc60 eq./ha, separadas',
     TX('Algodão em caroço', { kg: 4526, area: 1 }, 'padrao') === '301,73 @/ha' && al[0].rot === 'Padrão da cultura · @/ha (15 kg)'
     && TX('Arroz RS', { kg: 9044, area: 1 }, 'padrao') === '180,88 sc/ha' && TX('Arroz RS', { kg: 9044, area: 1 }, 'sc60') === '150,73 sc60 eq./ha de Arroz em casca RS'
     && ar[0].rot === 'Padrão da cultura · sc/ha (50 kg)' && ar.some(o => o.k === 'sc60' && o.rot === 'sc 60 kg/ha (equivalência)'),
     [TX('Algodão em caroço', { kg: 4526, area: 1 }, 'padrao'), al[0].rot, TX('Arroz RS', { kg: 9044, area: 1 }, 'sc60'), ar.map(o => o.rot)]);
  const mo = prUnpOpcoes('Mamão Formosa', 'base'); const cx = mo.find(o => o.k === 'cx10'); const c0 = cenClone(CEN0); const r6 = prResultado(c0, 'lg06');
  ok('U20b2 opções do mamão: Padrão t/ha, kg/ha, sc 60 e cx 10 kg (EMB_PACK), sem t/ha repetido; Pivô 6 = 96,07 cx10 eq./ha de Mamão Formosa · fruta de campo; soja sem sc 60 repetida; café com sc 60 (fruto)',
     KS('Mamão Formosa').join() === 'padrao,kg,sc60,cx10' && cx && cx.rot === 'cx 10 kg/ha (equivalência)' && cx.massa === '10' && mo[0].rot === 'Padrão da cultura · t/ha'
     && TX('Mamão Formosa', r6, 'cx10') === '96,07 cx10 eq./ha de Mamão Formosa · fruta de campo' && KS('Soja').join() === 'padrao,kg,t' && KS('Café').join() === 'padrao,kg,t,sc60',
     [KS('Mamão Formosa'), cx, mo[0].rot, TX('Mamão Formosa', r6, 'cx10'), KS('Soja'), KS('Café')]);
  // K-U03..K-U05 · semente: Pivô 6, Pivô 19 e a ponderada do mamão em todas as unidades, com um arredondamento (K-U14)
  const r19 = prResultado(c0, 'lg19'); const pm = prPonderada([r6, r19]);
  ok('U20s K-U03..05 semente: Pivô 6 960,66 kg/ha · 0,96 t/ha · 16,01 sc60 eq.; Pivô 19 484,89 · 8,08; mamão ponderado 701,52 kg/ha · 0,70 t/ha · 11,69 sc60 eq. (a média simples daria 722,78)',
     TX('Mamão Formosa', r6, 'kg') === '960,66 kg/ha' && TX('Mamão Formosa', r6, 'padrao') === '0,96 t/ha' && TX('Mamão Formosa', r6, 'sc60') === '16,01 sc60 eq./ha de Mamão Formosa · fruta de campo'
     && TX('Mamão Formosa', r19, 'kg') === '484,89 kg/ha' && TX('Mamão Formosa', r19, 'sc60') === '8,08 sc60 eq./ha de Mamão Formosa · fruta de campo' && TX('Mamão Formosa', r19, 'cx10') === '48,49 cx10 eq./ha de Mamão Formosa · fruta de campo'
     && TX('Mamão Formosa', pm, 'kg') === '701,52 kg/ha' && TX('Mamão Formosa', pm, 'padrao') === '0,70 t/ha' && TX('Mamão Formosa', pm, 'sc60') === '11,69 sc60 eq./ha de Mamão Formosa · fruta de campo'
     && prFmt(prDiv(prSoma([prUnpInd('Mamão Formosa', r6, 'kg').kgHa, prUnpInd('Mamão Formosa', r19, 'kg').kgHa]), 2), 2) === '722,78',
     [TX('Mamão Formosa', r6, 'kg'), TX('Mamão Formosa', r19, 'kg'), TX('Mamão Formosa', pm, 'kg'), TX('Mamão Formosa', pm, 'sc60')]);
  // AC-c · K-U11: 20 trocas sem deriva e sem mudar o cenário; a meta também parte sempre do valor gravado
  const cj = JSON.stringify(c0); const prim = {}; let deriva = []; const mt = {};
  for (let i = 0; i < 20; i++) KS('Mamão Formosa').forEach(k => { const t = TX('Mamão Formosa', prResultado(c0, 'lg06'), k) + ' | ' + prUnpMeta('Mamão Formosa', 50, 't/ha/ano', k).txt;
    if (prim[k] === undefined) prim[k] = t; else if (prim[k] !== t) deriva.push([i, k, t]); });
  ok('U20c K-U11 20 trocas Padrão → kg → sc60 → cx10: textos idênticos a cada volta e o cenário (JSON) igual byte a byte',
     !deriva.length && JSON.stringify(c0) === cj && prim.kg === '960,66 kg/ha | 50.000 kg/ha/ano' && prim.sc60.indexOf('833,33 sc60 eq./ha/ano') > 0, [deriva.slice(0, 3), prim]);
  // AC-d · culturas diferentes sem trava arbitrária; frutos sem massa (coco) indisponível com o motivo
  const cult = ['Soja', 'Milho', 'Mamão Formosa', 'Algodão em caroço', 'Algodão em pluma', 'Café']; const trava = cult.filter(cu => prUnpOpcoes(cu, 'base').some(o => !o.ok));
  const co = prUnpOpcoes('Coco', 'base'); const ci = prUnpInd('Coco', { kg: 12500, area: 1.25 }, 'kg');
  ok('U20d soja, milho, mamão, algodão (caroço e pluma) e café: todas as opções de massa valem no estágio de massa; coco em frutos: massa indisponível ("Falta peso ou conversão medida") e mostra o Padrão',
     !trava.length && co.filter(o => o.k !== 'padrao').every(o => !o.ok && o.motivo === 'Falta peso ou conversão medida') && prUnpTxt(ci) === '10,00 mil frutos/ha' && /kg\/ha indisponível para Coco verde: falta peso/.test(ci.motivo),
     [trava, co, prUnpTxt(ci), ci.motivo]);
  // AC-e · K-U10: zero medido ≠ não apurado; área 0 é pendência, sem divisão
  ok('U20e K-U10 0 kg em 10 ha = "0,00 kg/ha" (zero medido); 5.000 kg sem área = "sem área colhida apontada"; sem área e sem produção = "—"',
     TX('Soja', { kg: 0, area: 10 }, 'kg') === '0,00 kg/ha' && TX('Soja', { kg: 5000, area: 0 }, 'kg') === 'sem área colhida apontada' && TX('Soja', { kg: 0, area: 0 }, 't') === '—'
     && prUnpInd('Soja', { kg: 5000, area: 0 }, 'kg').st === 'pend' && prUnpInd('Soja', { kg: 5000, area: 0 }, 'kg').num === null,
     [TX('Soja', { kg: 0, area: 10 }, 'kg'), TX('Soja', { kg: 5000, area: 0 }, 'kg'), TX('Soja', { kg: 0, area: 0 }, 't')]);
  ok('U20e2 estimativa: origem com participação estimada leva " · estimativa" junto do número (D-U15)', TX('Soja', { kg: 60000, area: 10, estim: true }, 'kg') === '6.000,00 kg/ha · estimativa', TX('Soja', { kg: 60000, area: 10, estim: true }, 'kg'));
  // AC-f · K-U09: café da roça em L; com o fruto pesado, kg/t/sc60 eq. do fruto (nunca como beneficiado); sem peso, só L/ha; não há fator L→kg
  const CF = (area, semPeso) => { const c = cenClone(CEN0); OSX(c, 'OS-0930', 'C1', 'Em execução', area ? [['25/09', area]] : [], 'Colheita de café');
    MUD(c, x => prReceber(x, { os: 'OS-0930', ticket: 'TK-CF1', bruto: 9200, tara: 3200, litros: 12000, cond: 'Íntegra', dcol: '2026-09-25' }));
    if (semPeso) Object.values(c.producao.cargas).filter(g => g.cultura === 'Café').forEach(g => g.origem.forEach(x => { x.kg = 0; }));
    return prResultado(c, 'c9'); };
  const F = CF(5), FS = CF(5, true), F0 = CF(0); const iS = prUnpInd('Café', FS, 'kg');
  ok('U20f K-U09 café da roça (12.000 L, 6.000 kg pesados, 5 ha): Padrão "sc/ha a apurar · 2.400 L/ha de Café da roça"; kg "1.200,00 kg/ha de Café da roça"; sc60 "20,00 sc60 eq./ha de Café da roça"; sem área "sem área colhida apontada"',
     TX('Café', F, 'padrao') === 'sc/ha a apurar · 2.400 L/ha de Café da roça' && TX('Café', F, 'kg') === 'kg/ha a apurar · 1.200,00 kg/ha de Café da roça'
     && TX('Café', F, 't') === 't/ha a apurar · 1,20 t/ha de Café da roça' && TX('Café', F, 'sc60') === 'sc60 eq./ha a apurar · 20,00 sc60 eq./ha de Café da roça'
     && TX('Café', F0, 'padrao') === 'sc/ha a apurar · sem área colhida apontada' && F.litros === 12000 && F.liq === 6000 && F.kgOk === true,
     [TX('Café', F, 'padrao'), TX('Café', F, 'kg'), TX('Café', F, 'sc60'), TX('Café', F0, 'padrao'), F.litros, F.liq, F.kgOk]);
  ok('U20f2 sem peso do fruto: só L/ha e a massa indisponível com o motivo; não existe caminho de L para kg (L/ha não é massa)',
     prUnpTxt(iS) === 'kg/ha a apurar · 2.400 L/ha de Café da roça' && iS.motivo === 'kg/ha indisponível para Café da roça: falta peso ou conversão medida' && FS.kgOk === false
     && prUnpOpcoes('Café', 'campo', FS).filter(o => o.k !== 'padrao').every(o => !o.ok) && prUnpMassa('Café', 'L/ha') === null && /sem massa/.test(ERR(() => prUnpKgHa('Café', 1, 'L/ha')))
     && /sem massa/.test(ERR(() => prUnpKgHa('Coco', 10, 'mil frutos/ha'))),
     [prUnpTxt(iS), iS.motivo, FS.kgOk, prUnpMassa('Café', 'L/ha')]);
  // AC-i · contraprovas de agregação (contrato, item 6)
  const so = Object.keys(PRDC.cult).find(k => PRDC.cult[k].cultura === 'Soja' && !PRDC.cult[k].semanal); const ks = PRDC.cult[so];
  PRDC.cult.tu1 = Object.assign({}, ks, { id: 'tu1', area: 10, meta: 25, un_meta: 'sc/ha', prod: true });
  const c = cenClone(CEN0); OSX(c, 'OS-0971', ks.local, 'Em execução', [['25/09', 10]], 'Colheita de grãos'); OSX(c, 'OS-0972', ks.local, 'Em execução', [['26/09', 10]], 'Colheita de grãos');
  PRDC.osCult['OS-0971'] = 'tu1'; PRDC.osCult['OS-0972'] = 'tu1';
  const g1 = MUD(c, x => prReceber(x, { os: 'OS-0971', ticket: 'TK-U71', bruto: 25000, tara: 15000, u: '14', imp: '1', cond: 'Íntegra', dcol: '2026-09-25' }));
  const g2 = MUD(c, x => prReceber(x, { os: 'OS-0972', ticket: 'TK-U72', bruto: 20000, tara: 15000, u: '14', imp: '1', cond: 'Íntegra', dcol: '2026-09-26' }));
  const RT = prResultado(c, 'tu1'); const errado = prUnpDiv(RT.kg, prSoma(RT.passes.map(p => p.area)), 1);
  delete PRDC.cult.tu1; delete PRDC.osCult['OS-0971']; delete PRDC.osCult['OS-0972'];
  ok('U20i1 K-U07 mesmo cultivo de 10 ha, duas passagens nos mesmos 10 ha (10.000 + 5.000 kg): 1.500 kg/ha = 1,5 t/ha = 25 sc/ha (não 750 kg/ha somando 20 ha)',
     !g1.erro && !g2.erro && RT.kg === 15000 && RT.area === 10 && TX('Soja', RT, 'kg') === '1.500,00 kg/ha' && TX('Soja', RT, 't') === '1,50 t/ha' && TX('Soja', RT, 'padrao') === '25,00 sc/ha' && errado === 750,
     [g1.erro, g2.erro, RT.kg, RT.area, TX('Soja', RT, 'kg'), errado]);
  const P2 = prPonderada([{ k: { cultura: 'Soja' }, kg: 10000, area: 10 }, { k: { cultura: 'Soja' }, kg: 15000, area: 5 }]);
  ok('U20i2 K-U08 parcelas distintas 10 ha/10.000 kg e 5 ha/15.000 kg: 25.000 ÷ 15 = 1.666,67 kg/ha = 1,67 t/ha = 27,78 sc/ha (a média simples das taxas daria 2.000)',
     TX('Soja', P2, 'kg') === '1.666,67 kg/ha' && TX('Soja', P2, 't') === '1,67 t/ha' && TX('Soja', P2, 'padrao') === '27,78 sc/ha' && prDiv(prSoma([1000, 3000]), 2) === 2000,
     [TX('Soja', P2, 'kg'), TX('Soja', P2, 't'), TX('Soja', P2, 'padrao')]);
  const e1 = ERR(() => prPonderada([{ k: { cultura: 'Café' }, kg: 3000, area: 5 }, { k: { cultura: 'Café' }, kg: 6000, area: 5, estagio: 'campo' }]));
  const e2 = ERR(() => prPonderada([{ k: { cultura: 'Algodão em caroço' }, kg: 4526, area: 1 }, { k: { cultura: 'Algodão em pluma' }, kg: 2053, area: 1 }]));
  ok('U20i3 nunca agrega produtos ou estágios diferentes: café beneficiado × café da roça e algodão em caroço × pluma lançam o erro da R-U08',
     e1 === 'Produtos ou estágios diferentes não se agregam: Café beneficiado × Café da roça.' && e2 === 'Produtos ou estágios diferentes não se agregam: Algodão em caroço × Algodão em pluma.', [e1, e2]);
  // meta na unidade escolhida (R-U02, R-U06; K-U06, K-U13): a mesma unidade mostra o valor gravado; outra converte uma vez; até 2 casas
  const M = (cu, v, u, k) => prUnpMeta(cu, v, u, k).txt;
  ok('U20m K-U06/K-U13 meta: mamão 50 t/ha/ano = 50.000 kg/ha/ano = 833,33 sc60 eq./ha/ano = 5.000 cx10 eq./ha/ano; soja 64 sc/ha = 3.840 kg/ha = 3,84 t/ha; 3,85 t/ha gravado = 64,17 sc/ha no Padrão e 3,85 t/ha em t/ha',
     M('Mamão Formosa', 50, 't/ha/ano', 'padrao') === '50 t/ha/ano' && M('Mamão Formosa', 50, 't/ha/ano', 'kg') === '50.000 kg/ha/ano' && M('Mamão Formosa', 50, 't/ha/ano', 'sc60') === '833,33 sc60 eq./ha/ano'
     && M('Mamão Formosa', 50, 't/ha/ano', 'cx10') === '5.000 cx10 eq./ha/ano' && M('Soja', 64, 'sc/ha', 'kg') === '3.840 kg/ha' && M('Soja', 64, 'sc/ha', 't') === '3,84 t/ha' && M('Soja', 64, 'sc/ha', 'padrao') === '64 sc/ha'
     && M('Soja', 3.85, 't/ha', 'padrao') === '64,17 sc/ha' && M('Soja', 3.85, 't/ha', 't') === '3,85 t/ha' && prUnpMeta('Soja', 64, 'sc/ha', 't').kgHa === 3840,
     [M('Mamão Formosa', 50, 't/ha/ano', 'sc60'), M('Soja', 64, 'sc/ha', 't'), M('Soja', 3.85, 't/ha', 'padrao')]);
  // R-U12 · sem op, os textos de hoje (mensagens de comando); com op, o conversor (laranja: o "lado" t/ha só no Padrão)
  ok('U20n R-U12 sem op o texto de hoje; com op o conversor: laranja Padrão "300,00 cx/ha · 12,24 t/ha" e kg/ha "12.240,00 kg/ha" (o lado só no Padrão)',
     prPrtvTxt('Laranja', 24480, 2) === '300,00 cx/ha · 12,24 t/ha' && prPrtvTxt('Laranja', 24480, 2, 'padrao') === '300,00 cx/ha · 12,24 t/ha' && prPrtvTxt('Laranja', 24480, 2, 'kg') === '12.240,00 kg/ha'
     && prPrtvResTxt('Café', { apurar: true }) === 'sc/ha a apurar' && prPrtvResTxt('Café', { apurar: true }, 'kg') === 'kg/ha a apurar',
     [prPrtvTxt('Laranja', 24480, 2, 'padrao'), prPrtvTxt('Laranja', 24480, 2, 'kg')]);
  // a ponderada traz "apurar" como contagem dos talhões fora da conta: o indicador dela continua medido (revisão de 10/10, C01o)
  const pf = prPonderada([{ k: { cultura: 'Café' }, kg: 3000, area: 5 }, { k: { cultura: 'Café' }, kg: 0, area: 5, apurar: true }]);
  ok('U20p ponderada com 1 talhão a apurar fora da conta: indicador medido "10,00 sc/ha" (a contagem não vira estado a apurar)', pf.apurar === 1 && TX('Café', pf, 'padrao') === '10,00 sc/ha' && TX('Café', pf, 'kg') === '600,00 kg/ha', [pf, TX('Café', pf, 'padrao')]);
  // U24 · revisão adversarial v57 (S4): o número da tela sai da produção e da área com um arredondamento só (R-U02, PRD 10.0). Antes o conversor
  // arredondava para 6 casas e o texto de novo para 2: 8,0849995 → 8,085000 → "8,09", quando o certo é "8,08". A chave kgHa continua com 6 casas
  const X5 = { kg: '485.09997', area: '1' }; const L5 = TX('Laranja', { kg: '8084.9995', area: '1' }, 'padrao');
  const C5 = TX('Café', { apurar: true, litros: '16.169999', liq: 0, kgOk: false, area: '2' }, 'padrao');
  ok('U24a R-U02 um arredondamento: 485,09997 kg em 1 ha = 8,0849995 sc/ha → "8,08 sc/ha" (não "8,09"); a meta de 485,09997 kg/ha no Padrão "8,08 sc/ha"; o lado da laranja "8,08 t/ha"; café da roça 16,169999 L em 2 ha "8,08 L/ha"; kgHa com 6 casas',
     TX('Soja', X5, 'padrao') === '8,08 sc/ha' && M('Soja', 485.09997, 'kg/ha', 'padrao') === '8,08 sc/ha' && / · 8,08 t\/ha$/.test(L5) && C5 === 'sc/ha a apurar · 8,08 L/ha de Café da roça'
     && prUnpInd('Soja', X5, 'padrao').kgHa === 485.09997 && prUnpMeta('Soja', 485.09997, 'kg/ha', 'padrao').kgHa === 485.09997,
     [TX('Soja', X5, 'padrao'), M('Soja', 485.09997, 'kg/ha', 'padrao'), L5, C5]);
  ok('U20o o catálogo volta ao original depois dos casos injetados (tu1, OS-0971/0972)', !PRDC.cult.tu1 && !PRDC.osCult['OS-0971'] && !PRDC.osCult['OS-0972']); }
