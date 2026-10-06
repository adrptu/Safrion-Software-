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
  const rs = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 10000, chave: 'W-RS-1' }));
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
  const rs = MUD(c, x => prReservar(x, { pedido: 'PV-T1', lote: L.id, kg: 5000 }));
  const b = MUD(c, x => carc_bula(x, P, 'Mamão', 30)); const S1 = prSaldos(c, c.producao.lotes[L.id]); const sit = prSitPed(c, c.producao.pedidos['PV-T1']);
  ok('U07b bula corrigida para 30 dias DEPOIS do recebimento: o lote passa a Bloqueado (carência até 04/10) sem nada regravado', !rs.erro && !b.erro && S1.q === 'Bloqueado' && /carência até 04\/10/.test(S1.mot), [rs.erro, b.erro, S1]);
  ok('U07c a reserva já feita fica com a expedição impedida (pedido Em risco)', sit.t === 'Em risco' && sit.imp.length === 1, sit);
  const lb = MUD(c, x => prLiberarLote(x, L.id)); ok('U07d Liberar lote bloqueado por carência é recusado (só com laudo, fora)', /bloqueado por carência/.test(lb.erro || ''), lb);
  // dados insuficientes: aplicação em execução com saldo no talhão → Em inspeção, dono nomeado; Liberar recusa com a pendência
  const c2 = NOVO(); OSX(c2, 'OS-0922', 'Pivô 24', 'Em execução', [['20/09', 10]], 'Pulverização · ácaro', ['Abamectina 18 EC']); c2.ordens['OS-0922'].saldo = 24.37; c2.ordens['OS-0922'].resp = 'Wesley';
  OSX(c2, 'OS-0923', 'Pivô 24', 'Em execução', [['10/09', 10]], 'Colheita · semana 37');
  const r2 = MUD(c2, x => prReceber(x, { os: 'OS-0923', ticket: 'TK-C2', bruto: 17200, tara: 7200, cond: 'Íntegra', dcol: '2026-09-10' }));
  const S2 = prSaldos(c2, r2.L); const lb2 = MUD(c2, x => prLiberarLote(x, r2.L.id));
  ok('U07e carência sem dados (aplicação em execução sem apontamento completo) → Em inspeção com dono (Wesley)', !r2.erro && S2.q === 'Em inspeção' && /Wesley/.test(S2.dono), [r2.erro, S2]);
  ok('U07f Liberar lote (Qualidade) recusa enquanto a pendência existir, com o dono', /Liberar recusado/.test(lb2.erro || '') && /Wesley/.test(lb2.erro), lb2);
  // avaria: Em inspeção; a Qualidade libera; colheita sem ordem liberada (ordem cancelada depois) volta a Em inspeção
  const c3 = NOVO(); const r3 = MUD(c3, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Com avaria' }));
  const S3 = prSaldos(c3, r3.L); const l3 = MUD(c3, x => prLiberarLote(x, r3.L.id, 'Qualidade (Marta)')); const S3b = prSaldos(c3, c3.producao.lotes[r3.L.id]);
  ok('U07g Com avaria → Em inspeção (dono Qualidade); Liberar lote pela Qualidade → Liberado', S3.q === 'Em inspeção' && /Qualidade/.test(S3.dono) && !l3.erro && S3b.q === 'Liberado', [S3, l3.erro, S3b.q]);
  c3.ordens['OS-0505'].etapa = 'Canceladas'; ok('U07h colheita sem ordem liberada (O.S. cancelada) → Em inspeção', prSaldos(c3, c3.producao.lotes[r3.L.id]).q === 'Em inspeção', prSaldos(c3, c3.producao.lotes[r3.L.id])); }

// ---- U08 · saldos do L10-031 (AC-09) ----
{ const c = NOVO(); const S = prSaldos(c, c.producao.lotes['L10-031']); const T = x => prEstTxt('Soja', x);
  ok('U08 L10-031: físico 38.420 sc · bloqueado 0 · apto 38.420 · reservado 3.875 · disponível 34.545 sc', T(S.fis) === '38.420 sc' && S.blq === 0 && T(S.apto) === '38.420 sc' && T(S.res) === '3.875 sc' && T(S.disp) === '34.545 sc', S);
  ok('U08b PV-030: falta 7.500 kg depois da RS-0001 (4.000 sc = 240.000 kg)', prFalta(c, c.producao.pedidos['PV-030']) === 7500, prFalta(c, c.producao.pedidos['PV-030'])); }

// ---- U09 · reserva: recusas (AC-10) ----
{ const c = NOVO(); const e1 = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-131', kg: 1000 }));
  ok('U09a lote Em processo (CAR0: mistura LM-39-01) não reserva', /não está apto/.test(e1.erro || '') && /Em processo/.test(e1.erro), e1);
  const e2 = MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 7501 }));
  ok('U09b acima da falta do pedido (7.500 kg) é recusado', /Acima da falta/.test(e2.erro || ''), e2);
  MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' }));
  const e3 = MUD(c, x => prReservar(x, { pedido: 'PV-038', lote: 'L39-133', kg: 12051 }));
  ok('U09c acima do disponível do lote é recusado', /Acima do disponível/.test(e3.erro || ''), e3);
  const e4 = MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L39-133', kg: 100 }));
  ok('U09d produto diferente do pedido é recusado', /não atende o PV-030/.test(e4.erro || ''), e4);
  c.car = c.car || {}; c.car.laudos = [{ id: 'LAB-T9', escopo: ['LC-0505-2'], d: '2026-09-25', res: { tebuconazol: { v: 5, un: 'mg/kg', lq: 0.01 } } }];
  const e5 = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 1000 }));
  ok('U09e destino do pedido Não conforme (laudo acima do limite da ANVISA) recusa a reserva, com quem decide', /Reserva recusada/.test(e5.erro || '') && /Não conforme/.test(e5.erro) && /Qualidade/.test(e5.erro), e5);
  c.car.laudos = []; const ok1 = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 4000 }));
  const e6 = MUD(c, x => prCancelarReserva(x, ok1.rs.id, ''));
  const k6 = MUD(c, x => prCancelarReserva(x, ok1.rs.id, 'cliente adiou')); const S = prSaldos(c, c.producao.lotes['L39-133']);
  ok('U09f cancelar sem motivo é recusado; com motivo o disponível volta (12.050 kg)', /motivo/.test(e6.erro || '') && !k6.erro && S.disp === 12050, [e6, k6.erro, S.disp]);
  const k7 = MUD(c, x => prReservar(x, { pedido: 'PV-038', lote: 'L39-133', kg: 3000 }));
  ok('U09g venda futura (PV-038) aceita reserva de lote apto (R-15)', !k7.erro && prSaldos(c, c.producao.lotes['L39-133']).disp === 9050, k7); }

// ---- U10 · venda futura não muda o físico; oferta livre (AC-11, K10, K14) ----
{ const c = NOVO(); const of = prOfertaSafra(c, 'Soja em grão', '2026/27'); const T = x => prEstTxt('Soja', x);
  ok('U10a soja 26/27: oferta publicada 68.180 sc; obrigações do VE-05 (CT-203, CRE-0095, BT-090) 19.900 sc; oferta livre 48.280 sc', T(of.pub) === '68.180 sc' && T(of.futKg) === '19.900 sc' && T(of.livre) === '48.280 sc' && of.ob.length === 3, [T(of.pub), T(of.futKg), T(of.livre)]);
  ok('U10b o L10-031 continua com 34.545 sc disponíveis (a venda futura não desconta o físico)', T(prSaldos(c, c.producao.lotes['L10-031']).disp) === '34.545 sc');
  const s41 = prOfertaSem(c, MAM, '2026-W41'); ok('U10c S41 sem versão publicada: PV-038 aparece como déficit de 30.000 kg', s41.livre === -30000 && !s41.tem, s41);
  const pb = MUD(c, x => prPublicar(x, 'lg19', 'Ana (agrônoma)')); const s41b = prOfertaSem(c, MAM, '2026-W41');
  ok('U10d publicada a v2 do Pivô 19: oferta livre S41 = 57.337,908 kg (K14)', !pb.erro && s41b.livre === 57337.908 && pb.v.v === 2, [pb.erro, s41b]); }

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
  const r = MUD(c, x => prReceber(x, { os: 'OS-0930', ticket: 'TK-CF1', bruto: 9200, tara: 3200, litros: 12000, cond: 'Íntegra', dcol: '2026-09-25' }));
  const S = r.L && prSaldos(c, r.L); const R = prResultado(c, 'c9');
  ok('U12 café: lote "Café da roça" em L, Em processo; produção em sc a apurar (0 sc, 12.000 L)', !r.erro && r.L.prod === 'Café da roça' && S.q === 'Em processo' && S.fis === 12000 && R.kg === 0 && R.cafe === 12000, [r.erro, S, R && R.kg, R && R.cafe]);
  const e = MUD(c, x => prReceber(x, { os: 'OS-0930', ticket: 'TK-CF2', bruto: 9200, tara: 3200, cond: 'Íntegra', dcol: '2026-09-25' }));
  ok('U12b café sem litros é recusado', /litros/.test(e.erro || ''), e); }

// ---- U02e · grão: descontos na pesagem; umidade e impureza obrigatórias ----
{ const c = NOVO(); OSX(c, 'OS-0931', 'T1-A', 'Em execução', [['25/09', 20]], 'Colheita de grãos');
  const e = MUD(c, x => prReceber(x, { os: 'OS-0931', ticket: 'TK-S0', bruto: 45000, tara: 15000, cond: 'Íntegra', dcol: '2026-09-25' }));
  const r = MUD(c, x => prReceber(x, { os: 'OS-0931', ticket: 'TK-S1', bruto: 45000, tara: 15000, u: '16,5', imp: '2,0', cond: 'Íntegra', dcol: '2026-09-25' }));
  ok('U02e grão sem umidade é recusado; com 16,5 % e 2 %: comercial 28.836,627907 kg = 480,61 sc no lote do Silo 01 (bruto, descontos e comercial separados)', /umidade/.test(e.erro || '') && !r.erro && r.g.com === 28836.627907 && r.g.desc.dImp === 300 && r.L.local === 'l6' && prUnTxt('Soja', prFis(c, r.L.id)) === '480,61 sc', [e.erro, r.erro, r.g && r.g.desc]); }

// ---- U13 · estorno (AC-14, R-19) ----
{ const c = NOVO(); MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' }));
  MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 10000 }));
  const e = MUD(c, x => prEstornar(x, 'CG-2108', 'ticket trocado')); ok('U13a estorno que deixaria o lote abaixo do reservado é recusado', /abaixo do reservado/.test(e.erro || ''), e);
  const e0 = MUD(c, x => prEstornar(x, 'CG-2108', '')); ok('U13b estorno sem motivo é recusado', /motivo/.test(e0.erro || ''), e0);
  MUD(c, x => prCancelarReserva(x, 'RS-0002', 'refazer pesagem'));
  const ok1 = MUD(c, x => prEstornar(x, 'CG-2108', 'ticket trocado')); const g = c.producao.cargas['CG-2108'];
  ok('U13c estorno com motivo: lote volta a 0 kg, carga Estornada, produção do Pivô 19 volta a 36,42 t e o histórico fica', !ok1.erro && prFis(c, 'L39-133') === 0 && g.st === 'Estornada' && prResultado(c, 'lg19').kg === 36420 && c.producao.movs.some(m => m.tipo === 'estorno'), [ok1.erro, prFis(c, 'L39-133')]);
  const nv = MUD(c, x => prReceber(x, { os: 'OS-0505', ticket: 'TK-4520', bruto: 19200, tara: 7200, cond: 'Íntegra', dcol: '2026-09-22' }));
  ok('U13d o ticket estornado fica livre para novo registro', !nv.erro, nv); }

// ---- U14 · encerrar O.S. de colheita com carga a pesar (AC-15, R-18), pelo comando da O.S. ----
{ const c = NOVO(); c.ordens['OS-0505'].etapa = 'Em conferência'; c.ordens['OS-0505'].saldo = 0;
  const e = MUD(c, x => osc_encerrar(x, 'OS-0505'));
  ok('U14a Encerrar a OS-0505 com a CG-2108 a pesar é recusado com dono (Lúcia)', /Encerrar bloqueado/.test(e.erro || '') && /CG-2108/.test(e.erro) && /Lúcia/.test(e.erro), e);
  MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' }));
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
  const aptoM = prSoma(Object.values(L).filter(x => x.prod === MAM).map(x => q(x.id).apto)); const proc = prSoma(Object.values(L).filter(x => x.prod === MAM).map(x => q(x.id).proc));
  ok('U16b apto de mamão na semente = 0; 66.250 kg fora do acabado; L38-131 expedido ao PV-037 (físico 0, 30.490 kg)', aptoM === 0 && proc === 66250 && q('L38-131').fis === 0 && prExpedido(c, 'PV-037') === 30490, [aptoM, proc]);
  OSX(c, 'OS-0932', 'T7', 'Em execução', [['25/09', 6]], 'Colheita · semana 39');
  const r = MUD(c, x => prReceber(x, { os: 'OS-0932', ticket: 'TK-T7', bruto: 9400, tara: 3200, cond: 'Íntegra', dcol: '2026-09-25' }));
  ok('U16c carga do T7 vai ao l8 Packing (tipo Packing, D-24) e nasce Em processo', !r.erro && r.L.local === 'l8' && prSaldos(c, r.L).q === 'Em processo' && PRDC.locais.l8.tipo === 'Packing', [r.erro, r.L && r.L.local]);
  ok('U16d seq da semente: próxima carga CG-2109, próximo lote da S39 L39-133, próxima reserva RS-0002, próximo MP-1011', CEN0.producao.seq.cg === 2108 && CEN0.producao.seq.lote['39'] === 132 && CEN0.producao.seq.rs === 1 && CEN0.producao.seq.mp === 1010); }
