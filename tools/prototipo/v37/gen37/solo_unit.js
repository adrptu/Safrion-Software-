/* Testes puros da análise de solo (docs/analise-solo/ESPECIFICACAO.md §8) · node, sem navegador.
   Carregado depois de: perfis + CEN0 + cenario.js + PRDC + producao.js + solo.js + SOLO0. Números: docs/analise-solo/verificacao/conta_semente.py. */
const R = []; function ok(n, c, info) { R.push({ n, ok: !!c, info: c ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 700) }); }
const TRY = (f) => { try { f(); return ''; } catch (e) { return String(e.message || e); } };
const RG = SOLO0.regra;
function MUD(c, fn) { const x = cenClone(c); try { const r = fn(x) || {}; Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); return r; } catch (e) { return { erro: String(e.message || e) }; } }
const NOVO = () => cenClone(CEN0);
const L = (id) => soloLaudos(NOVO(), SOLO0).find(l => l.id === id);
const CU = (c, cid) => soloCultivoBase(SOLO0, SOLO0.cult.find(x => x.id === cid));
const SG = (c, cid) => soloSugestoes(soloCtxBase(c, SOLO0), CU(c, cid));
const F2 = x => x === null ? null : prFmt(x, 2);

/* ---- AC-SOLO-01 · CAL-10 (AC-27) ---- */
{ const r = soloCalagem(5, 40, 60, 80); ok('AC-SOLO-01 V 40 → 60, T 5, PRNT 80: NC100 1,00 t/ha e dose 1,25 t/ha (PRNT uma vez)', r.nc === 1 && r.dose === 1.25, r);
  ok('AC-SOLO-01b V acima de V₂: NC = 0 (nunca negativa)', soloCalagem(5, 70, 60, 80).nc === 0, soloCalagem(5, 70, 60, 80)); }

/* ---- AC-SOLO-02 · índices (PRD 38.3) ---- */
{ const want = { 'LAU-2043': ['5,38', '9,20', '5,48', '58,48', '1,82'], 'LAU-2044': ['1,66', '4,66', '1,76', '35,62', '5,68'], 'LAU-2061': ['4,50', '7,50', '4,50', '60,00', '0,00'],
    'LAU-2063': ['2,04', '5,10', '2,34', '40,00', '12,82'], 'LAU-2071': ['4,05', '8,10', '4,25', '50,00', '4,71'], 'LAU-2072': ['0,58', '4,58', '1,18', '12,66', '50,85'] };
  Object.keys(want).forEach(id => { const x = L(id).idx; const got = ['SB', 'T', 't', 'V', 'm'].map(k => F2(x[k].v));
    ok('AC-SOLO-02 ' + id + ' SB/T/t/V/m = ' + want[id].join(' / '), JSON.stringify(got) === JSON.stringify(want[id]), got); });
  const c1 = L('LAU-2050').idx;
  ok('AC-SOLO-02 LAU-2050 sem H+Al: T e V "não calculável" (nunca 0); SB 4,75, t 4,75, m 0', c1.T.v === null && c1.V.v === null && /H\+Al não analisado/.test(c1.T.nc) && F2(c1.SB.v) === '4,75' && F2(c1.t.v) === '4,75' && F2(c1.m.v) === '0,00', c1);
  const lt = { an: [{ a: 'Ca', v: '2', un: 'cmolc/dm³' }, { a: 'Mg', v: '1', un: 'cmolc/dm³' }, { a: 'K', v: '39.1', un: 'mg/dm³' }, { a: 'H+Al', v: '3', un: 'cmolc/dm³' }, { a: 'Al', v: '0.1', un: 'cmolc/dm³', q: '<' }] };
  const ix = soloIdx(lt); ok('AC-SOLO-02 Al "< 0,1" (abaixo do limite): t e m "não calculável", nunca metade do limite; V calculado', ix.t.v === null && ix.m.v === null && /abaixo do limite/.test(ix.t.nc) && F2(ix.V.v) === '50,82', ix);
  ok('AC-SOLO-02 Na não analisado fica fora da soma e a fórmula diz', /Na não analisado/.test(ix.SB.f) && F2(ix.SB.v) === '3,10', ix.SB);
  const ln = { an: lt.an.slice(0, 4).concat([{ a: 'Na', v: '0.05', un: 'cmolc/dm³' }]) }; ok('AC-SOLO-02 Na analisado entra na soma', F2(soloIdx(ln).SB.v) === '3,15' && /\+ Na$/.test(soloIdx(ln).SB.f), soloIdx(ln).SB);
  const lu = { an: [{ a: 'Ca', v: '2', un: 'mg/kg' }, { a: 'Mg', v: '1', un: 'cmolc/dm³' }, { a: 'K', v: '39.1', un: 'mg/dm³' }, { a: 'H+Al', v: '3', un: 'cmolc/dm³' }, { a: 'Al', v: '0', un: 'cmolc/dm³' }] };
  ok('AC-SOLO-02 unidade incompatível (Ca em mg/kg) → "não calculável"', soloIdx(lu).SB.v === null && /incompatível/.test(soloIdx(lu).SB.nc), soloIdx(lu).SB);
  ok('AC-SOLO-02 mmolc/dm³ ÷ 10 e mg/dm³ (Ca ÷ 200,4; Mg ÷ 121,6)', soloCmolc({ a: 'Ca', v: '31', un: 'mmolc/dm³' }).v === 3.1 && soloCmolc({ a: 'Ca', v: '200.4', un: 'mg/dm³' }).v === 1 && soloCmolc({ a: 'Mg', v: '121.6', un: 'mg/dm³' }).v === 1);
  const v71 = L('LAU-2071').idx.V; ok('D-17 LAU-2071: V 50 % recalculado × 49 % do laboratório → "difere", a regra usa o recalculado', v71.difere === true && v71.lab === '49' && v71.v === 50, v71); }

/* ---- AC-SOLO-03 · limites ---- */
{ ok('AC-SOLO-03 classes de K: 39,99 baixo · 40 médio · 79,99 médio · 80 adequado · 119,99 adequado · 120 alto',
    ['39.99', '40', '79.99', '80', '119.99', '120'].map(k => soloClasseK(k, RG)).join(',') === 'baixo,médio,médio,adequado,adequado,alto', ['39.99', '40', '79.99', '80', '119.99', '120'].map(k => soloClasseK(k, RG)));
  const m = (x) => soloK2O('58.65', x, RG);
  ok('AC-SOLO-03 meta 2.399 e 4.801 kg/ha: fora da faixa, nada e "meta fora da faixa da regra"', /meta fora da faixa da regra/.test(m(2399).nc) && /meta fora da faixa/.test(m(4801).nc), [m(2399), m(4801)]);
  ok('AC-SOLO-03 meta 2.400 e 3.600 → linha até 3.600 (72); 3.601 e 4.800 → linha até 4.800 (90)', m(2400).k2o === '72' && m(3600).k2o === '72' && m(3601).k2o === '90' && m(4800).k2o === '90', [m(2400), m(3600), m(3601), m(4800)]);
  ok('AC-SOLO-03 V = V₂ → NC 0', soloCalagem('7.5', 60, 60, 85).nc === 0);
  ok('AC-SOLO-03 gesso com Ca 0,5 e m 20 % exatos → não indicado; Ca 0,49 → indicado', soloGesso(0.5, 20, 20, 'Anual', RG).gat === false && soloGesso(0.49, 0, 20, 'Anual', RG).gat === true && soloGesso(1, 20.01, 20, 'Anual', RG).gat === true);
  ok('R08 NG = k × argila: perene 75 × 20 = 1.500 kg/ha; anual 50 × 32 = 1.600', soloGesso(0.3, 50.85, 20, 'Perene', RG).ng === 1500 && soloGesso(0.3, 0, 32, 'Anual', RG).ng === 1600); }

/* ---- semente: sugestões da §6 ---- */
{ const c = NOVO(); const a = SG(c, 'c1').sug, b = SG(c, 'c2').sug, t2 = SG(c, 'c3').sug, p12 = SG(c, 'lg12').sug;
  const k1 = a.find(s => s.prod === 'KCl 60%'); ok('§6 T1-A: KCl 120 → 150 kg/ha · +4.800 kg · +R$ 11.520,00 · LAU-2061 · regra rotulada', k1 && k1.tipo === 'dose' && k1.sug === 150 && k1.padrao === 120 && k1.dif === 4800 && k1.custo === 11520 && k1.laudo.id === 'LAU-2061' && k1.rot === 'Demonstração — tabela regional a decidir pelo proprietário' && !k1.nega, k1);
  ok('§6 T1-A: conta passo a passo (médio · 3.840 kg/ha · 90 ÷ 0,6 = 150)', k1 && k1.conta.join(' ').indexOf('médio') >= 0 && k1.ent.join(' ').indexOf('3.840 kg/ha') >= 0 && k1.conta.join(' ').indexOf('90 ÷ 0,6 = 150') >= 0, k1 && k1.conta);
  ok('§6 T1-A: sem calagem (V 60 = V₂) e só 1 sugestão', a.length === 1, a.map(s => s.k));
  const k2 = b.find(s => s.prod === 'KCl 60%'); ok('§6 T1-B: KCl 150 kg/ha · +4.560 kg (meta 62 sc/ha = 3.720 kg/ha)', k2 && k2.sug === 150 && k2.dif === 4560, k2);
  const r2 = t2.find(s => s.tipo === 'retirar'); ok('§6 T2: KCl retirar (K alto) · −35.760 kg · −R$ 85.824,00 · único insumo da a4', r2 && r2.prod === 'KCl 60%' && r2.dif === -35760 && r2.custo === -85824 && r2.unico && r2.motivo === 'K alto', r2);
  const i2 = t2.find(s => s.tipo === 'incluir'); ok('§6 T2: incluir Calagem · Calcário dolomítico 1,20 t/ha em 30/09/2026 · +357,6 t · +R$ 64.368,00', i2 && i2.prod === 'Calcário dolomítico' && i2.sug === 1.2 && i2.un === 't' && i2.dt === '2026-09-30' && i2.dif === 357.6 && i2.custo === 64368 && i2.atv.id === 'solo:LAU-2063:cal', i2);
  ok('§6 T2: a data diz que o DAP −60 (19/08) já passou e vale a chegada viável', i2 && i2.conta.join(' ').indexOf('19/08/2026') >= 0 && i2.conta.join(' ').indexOf('chegada viável') >= 0, i2 && i2.conta);
  const cal = p12.find(s => s.regra === 'calagem'), ges = p12.find(s => s.regra === 'gessagem');
  ok('§6 Pivô 12: calagem 2.000 → 1.800 kg/ha (filler PRNT 90; V 50 → 70; T 8,10) · −9.694 kg · −R$ 1.744,92 · OS-0502 em A liberar', cal && cal.sug === 1800 && cal.padrao === 2000 && cal.dif === -9694 && cal.custo === -1744.92 && !cal.nega, cal);
  ok('§6 Pivô 12: gessagem 1.000 → 1.500 kg/ha (Ca 0,30 < 0,5; perene 75 × 20) · +24.235 kg · +R$ 5.331,70', ges && ges.sug === 1500 && ges.dif === 24235 && ges.custo === 5331.7, ges);
  ok('§6 sem sugestão: C1 (laudo aguardando validação) e T4 (laudo por zona e sem plano)', SG(c, 'c9').sug.length === 0 && !CU(c, 'c4'), SG(c, 'c9'));
  const sf = SG(c, 'd2'); ok('§6 R17: a Safrinha 2027 (T2) não recebe a calagem do LAU-2063; diz que foi para a Safra 2026/27', !sf.sug.length && sf.info.join(' ').indexOf('calagem pelo LAU-2063 na Safra 2026/27') >= 0, sf);
  ok('§6 MAP 11-52: sem regra de P (nenhuma sugestão de MAP)', ![].concat(a, b, t2).some(s => s.prod === 'MAP 11-52')); }

/* ---- AC-SOLO-04 · regra desligada ---- */
{ const old = RG.estado; RG.estado = 'desligada'; const c = NOVO(); const n = ['c1', 'c2', 'c3', 'lg12'].reduce((a, id) => a + SG(c, id).sug.length, 0); const vis = soloLaudos(c, SOLO0).filter(l => l.sit === 'Validado').length;
  RG.estado = old; ok('AC-SOLO-04 regra desligada → 0 sugestões; os laudos continuam visíveis', n === 0 && vis >= 6, [n, vis]); }

/* ---- AC-SOLO-06/07 · registrar, repetir, validar por papel, corrigir (comandos) ---- */
{ const c = NOVO(); const d = Object.assign({}, SOLO0.exemplo);
  const r1 = MUD(c, x => soloRegistrar(x, d, 'K-REG-1', 'Ana')); const l = soloLaudos(c, SOLO0).find(q => q.id === 'LAU-2073');
  ok('AC-SOLO-06 registrar o laudo do T7 → LAU-2073 em Aguardando validação', !r1.erro && r1.id === 'LAU-2073' && l && l.sit === 'Aguardando validação', [r1, l && l.sit]);
  const r1b = MUD(c, x => soloRegistrar(x, d, 'K-REG-1', 'Ana')); ok('R13 mesma chave e mesmo conteúdo: "já registrado", nada muda (1 laudo novo)', r1b.repetido && Object.keys(c.solo.laudos).length === 1, [r1b, Object.keys(c.solo.laudos)]);
  const r1c = MUD(c, x => soloRegistrar(x, Object.assign({}, d, { lab: 'Agrolab' }), 'K-REG-1', 'Ana')); ok('R13 mesma chave e outro conteúdo: conflito, nada gravado', /Conflito/.test(r1c.erro || '') && Object.keys(c.solo.laudos).length === 1, r1c);
  const r2 = MUD(c, x => soloRegistrar(x, d, 'K-REG-2', 'Ana')); ok('AC-SOLO-06 registrar de novo a mesma amostra (outra chave) → recusado: "já registrada como LAU-2073"', /já está registrada como LAU-2073/.test(r2.erro || ''), r2);
  ok('AC-SOLO-06 antes de validar, o T7 não tem sugestão', SG(c, 'c8').sug.length === 0);
  const r3 = MUD(c, x => soloValidar(x, 'LAU-2073', 'K-VAL-1', 'Caio')); ok('AC-SOLO-06 Caio não valida ("decisão de Ana (agrônoma)"); nada muda', /decisão de Ana \(agrônoma\)/.test(r3.erro || '') && soloLaudos(c, SOLO0).find(q => q.id === 'LAU-2073').sit === 'Aguardando validação', r3);
  const r4 = MUD(c, x => soloValidar(x, 'LAU-2073', 'K-VAL-2', 'Ana')); const t7 = SG(c, 'c8').sug;
  ok('AC-SOLO-06 Ana valida; só então o T7 mostra "incluir Calagem 0,40 t/ha" (+16,8 t, +R$ 3.024,00)', !r4.erro && t7.length === 1 && t7[0].tipo === 'incluir' && t7[0].sug === 0.4 && t7[0].dif === 16.8 && t7[0].custo === 3024, [r4, t7]);
  const r5 = MUD(c, x => soloValidar(x, 'LAU-2048', 'K-VAL-3', 'Ana')); ok('AC-SOLO-07 LAU-2048 (K sem unidade): Inconsistente, validar recusado', /inconsistente/.test(r5.erro || '') && soloLaudos(c, SOLO0).find(q => q.id === 'LAU-2048').sit === 'Inconsistente', r5);
  const r6 = MUD(c, x => soloCorrigir(x, 'LAU-2048', 'K', '17.4', 'g/kg', 'K-COR-1', 'Ana')); ok('AC-SOLO-07 corrigir K para g/kg → Aguardando validação; o original continua no laudo', !r6.erro && soloLaudos(c, SOLO0).find(q => q.id === 'LAU-2048').sit === 'Aguardando validação' && SOLO0.laudos.find(q => q.id === 'LAU-2048').an.find(a => a.a === 'K').un === '', r6);
  const r7 = MUD(c, x => soloCorrigir(x, 'LAU-2061', 'K', '58.65', 'mg/dm³', 'K-COR-2', 'Ana')); ok('§3.1 corrigir um laudo Validado o devolve a Aguardando validação (e ele deixa de sugerir)', !r7.erro && soloLaudos(c, SOLO0).find(q => q.id === 'LAU-2061').sit === 'Aguardando validação' && SG(c, 'c1').sug.length === 0, r7); }

/* ---- AC-SOLO-09 · lote: mesma chave, conflito, linha negada ---- */
{ const c = NOVO(); const its = ['c1', 'c2', 'c3'].reduce((a, id) => a.concat(SG(c, id).sug), []);
  ok('AC-SOLO-10 base: 4 sugestões na Safra 2026/27 (T1-A, T1-B, T2 KCl, T2 calagem)', its.length === 4, its.map(s => s.k));
  const r = MUD(c, x => soloAceitarLote(x, its, 'K-LOTE-1', 'Ana'));
  ok('AC-SOLO-10 lote: KCl −26.400 kg e Calcário dolomítico +357,6 t no aviso', !r.erro && r.msg.indexOf('KCl 60% −26.400 kg') >= 0 && r.msg.indexOf('Calcário dolomítico +357,6 t') >= 0, r);
  const n0 = Object.keys(c.solo.aceites).length; const r2 = MUD(c, x => soloAceitarLote(x, its, 'K-LOTE-1', 'Ana'));
  ok('AC-SOLO-09 a mesma chave duas vezes: "já registrado" e nenhum aceite a mais', r2.repetido && Object.keys(c.solo.aceites).length === n0 && n0 === 4, [r2, n0]);
  const outro = its.map(s => Object.assign({}, s, { sug: s.sug + 1 })); const r3 = MUD(c, x => soloAceitarLote(x, outro, 'K-LOTE-1', 'Ana'));
  ok('AC-SOLO-09 mesma chave e outra dose: conflito, nada gravado', /Conflito/.test(r3.erro || '') && c.solo.aceites['c1|a4|KCl 60%'].dose === 150, r3);
  ok('AC-SOLO-09 depois do lote, T1-A não sugere mais (aceite = sugestão)', SG(c, 'c1').sug.length === 0);
  const d = NOVO(); const p12 = SG(d, 'lg12').sug; d.ordens['OS-0502'].etapa = 'Liberadas';
  const r4 = MUD(d, x => soloAceitarLote(x, p12, 'K-LOTE-2', 'Ana'));
  ok('AC-SOLO-09/15 lote com uma linha negada pela R11 (OS-0502 já liberada): a gessagem grava, a calagem diz o motivo', !r4.erro && (r4.neg || []).length === 1 && /OS-0502 já liberada/.test(r4.neg[0].motivo) && d.solo.aceites['lg12|i2|Gesso agrícola'] && !d.solo.aceites['lg12|i1|Calcário dolomítico filler'], r4);
  ok('AC-SOLO-15 com a OS-0502 liberada a sugestão de calagem vem negada (o plano esconde a linha; o AG-02 diz por quê)', /OS-0502 já liberada/.test((SG(d, 'lg12').sug.find(s => s.regra === 'calagem') || {}).nega || ''), SG(d, 'lg12').sug);
  const e = NOVO(); const s1 = Object.assign({}, SG(e, 'c1').sug[0], { dt: '2026-09-20' }); ok('AC-SOLO-15 data passada: comando recusa', /data passada/.test(MUD(e, x => soloAceitar(x, { aceitar: [s1] }, 'K-A-1', 'Ana')).erro || '')); }

/* ---- AC-SOLO-12 · uma dose por chave (R14) ---- */
{ const c = NOVO(); const s = SG(c, 'c1').sug[0]; MUD(c, x => soloAceitar(x, { aceitar: [s] }, 'K-A-2', 'Ana'));
  const pl = SOLO0.planos['SOJA-AT']; const cu = { id: 'c1', plano: pl };
  const dose = (adj) => { const a = soloAtividades(cu, adj, c.solo.aceites).atvs.find(x => String(x.a.id) === 'a4'); return a ? a.prods[0] : null; };
  ok('R14 sem ajuste da sessão: vale o aceite (150, pela análise)', dose({}).dose === 150 && dose({}).orig === 'análise');
  ok('R14 ajuste manual da sessão (140) vence o aceite', dose({ 'a4|0': 140 }).dose === 140 && dose({ 'a4|0': 140 }).orig === 'sessão');
  MUD(c, x => soloDesfazer(x, 'c1|a4|KCl 60%', 'substituído por ajuste manual', 'K-D-1', 'Ana'));
  ok('AC-SOLO-12 desfazer (como de outra aba) → vale o padrão 120; nada ficou copiado na sessão', dose({}).dose === 120 && dose({}).orig === 'padrão' && c.solo.aceites['c1|a4|KCl 60%'].st === 'substituído por ajuste manual', c.solo.aceites['c1|a4|KCl 60%']);
  ok('AC-SOLO-12 a linha "Análise sugere 150" volta', SG(c, 'c1').sug.length === 1 && SG(c, 'c1').sug[0].sug === 150); }

/* ---- AC-SOLO-13 · identidade estável (R16) ---- */
{ const c = NOVO(); const t2 = SG(c, 'c3').sug; const s1 = SG(c, 'c1').sug[0]; MUD(c, x => soloAceitar(x, { aceitar: t2.concat([s1]) }, 'K-A-3', 'Ana'));
  const v6 = SOLO0.planos['SOJA-AT']; const v7 = cenClone(v6); v7.versao = 7; v7.atividades.find(a => a.id === 'a4').prods[0].dose = 110;
  const a1 = soloAtividades({ id: 'c1', plano: v7 }, {}, c.solo.aceites).atvs.find(x => x.a.id === 'a4').prods[0];
  ok('AC-SOLO-13 plano v7 com KCl padrão 110: aceite 150 mantido e padrão 110 como referência', a1.dose === 150 && a1.p.dose === 110 && a1.orig === 'análise', a1);
  const v7b = cenClone(v6); v7b.versao = 7; v7b.atividades.find(a => a.id === 'a4').prods = [{ grupo: 'Fertilizantes', prod: 'Sulfato de potássio', dose: 100, un: 'kg', preco: 4.8 }];
  const o = soloAtividades({ id: 'c1', plano: v7b }, {}, c.solo.aceites); const a4 = o.atvs.find(x => x.a.id === 'a4');
  ok('AC-SOLO-13 KCl fora do v7 → aceite órfão visível e o KCl não volta sozinho', o.orf.length === 1 && o.orf[0].prod === 'KCl 60%' && a4 && !a4.prods.some(p => p.p.prod === 'KCl 60%'), o.orf);
  const v7c = cenClone(v6); v7c.versao = 7; v7c.atividades.push({ id: 'a0', nome: 'Calagem', op: 'Adubação a lanço', g: { tipo: 'DAP', dias: -30 }, prods: [{ grupo: 'Corretivos', prod: 'Calcário dolomítico', dose: 1, un: 't', preco: 180 }] });
  const o3 = soloAtividades({ id: 'c3', plano: v7c }, {}, c.solo.aceites);
  ok('AC-SOLO-13 v7 com Calagem própria e a calagem incluída pela análise → uma só calagem no T2 (vale a incluída; a do padrão é referência)', o3.atvs.filter(x => soloTipoAtv(x.a) === 'cal').length === 1 && o3.atvs.find(x => soloTipoAtv(x.a) === 'cal').incl && o3.ref.length === 1, o3.atvs.map(x => x.a.id));
  const o4 = soloAtividades({ id: 'c3', plano: v6 }, {}, c.solo.aceites);
  ok('R07 retirada pela análise do único insumo: a Adubação de cobertura (a4) sai do T2; a calagem incluída entra', !o4.atvs.some(x => x.a.id === 'a4') && o4.atvs.some(x => x.a.id === 'solo:LAU-2063:cal'), o4.atvs.map(x => x.a.id));
  const pd = SOLO0.planos['SOJA-PD']; const o5 = soloAtividades({ id: 'c1', plano: pd }, {}, c.solo.aceites);
  ok('AC-SOLO-13 aceite do SOJA-AT com o cultivo em SOJA-PD → não vale e não é apagado', !o5.atvs.some(x => x.prods.some(p => p.orig === 'análise')) && c.solo.aceites['c1|a4|KCl 60%'].st === 'ativo'); }

/* ---- AC-SOLO-17 · R17 com um laudo sintético do T1 com V 50 % ---- */
{ const c = NOVO(); const S1 = cenClone(SOLO0); const l = S1.laudos.find(x => x.id === 'LAU-2061'); l.an.find(a => a.a === 'Ca').v = '2.35'; l.an.find(a => a.a === 'H+Al').v = '3.75';   /* SB 3,75 · T 7,50 · V 50 % */
  S1.cult = S1.cult.concat([{ id: 'dX', saf: 'S27SF', safNome: 'Safrinha 2027', faz: 'Santa Rita', local: 'T1-A', tal: 'T1', cultura: 'Soja', area: 160, meta: 64, unm: 'sc/ha', plano: 'SOJA-PD', plantio: '2027-02-20', colheita: '' }]);
  const ctx = soloCtxBase(c, S1); const g = (id) => soloSugestoes(ctx, soloCultivoBase(S1, S1.cult.find(x => x.id === id)));
  const a = g('c1').sug.find(s => s.regra === 'calagem'), b = g('c2').sug.find(s => s.regra === 'calagem'), x = g('dX');
  ok('AC-SOLO-17 laudo do T1 com V 50 % (T 7,50): 0,88 t/ha ao T1-A e ao T1-B na Safra 2026/27', a && b && a.sug === 0.88 && b.sug === 0.88 && a.tipo === 'incluir' && F2(soloLaudos(c, S1).find(q => q.id === 'LAU-2061').idx.V.v) === '50,00', [a, b]);
  ok('AC-SOLO-17 e nada à parcela do T1 na Safrinha 2027', !x.sug.some(s => s.regra === 'calagem') && x.info.join(' ').indexOf('na Safra 2026/27') >= 0, x); }

/* ---- AC-SOLO-21 · dois laudos validados do T2 a 0–20 cm ---- */
{ const c = NOVO(); const d = { faz: 'Santa Rita', tal: 'T2', prof: '0–20', coleta: '2026-09-21', lab: 'Agrolab', ext: 'Mehlich-1', area: 298, an: SOLO0.laudos.find(l => l.id === 'LAU-2063').an.map(a => a.a === 'Ca' ? Object.assign({}, a, { v: '2.25' }) : a) };
  MUD(c, x => soloRegistrar(x, d, 'K-R21-1', 'Ana')); MUD(c, x => soloValidar(x, 'LAU-2073', 'K-R21-2', 'Ana')); const ls = soloLaudos(c, SOLO0);
  const i2 = SG(c, 'c3').sug.find(s => s.tipo === 'incluir');
  ok('AC-SOLO-21 vale o de coleta mais recente (LAU-2073); o LAU-2063 fica Substituído e não sugere', ls.find(l => l.id === 'LAU-2063').sit === 'Substituído' && i2 && i2.laudo.id === 'LAU-2073' && i2.atv.id === 'solo:LAU-2073:cal', [ls.find(l => l.id === 'LAU-2063').sit, i2 && i2.laudo]); }

/* ---- R18 sem preço: nada incluído e o laudo diz por quê ---- */
{ const S1 = cenClone(SOLO0); delete S1.preco['Calcário dolomítico']; const ctx = soloCtxBase(NOVO(), S1); const r = soloSugestoes(ctx, soloCultivoBase(S1, S1.cult.find(x => x.id === 'c3')));
  ok('R18 Calcário sem preço de referência: nada incluído e o motivo aparece', !r.sug.some(s => s.tipo === 'incluir') && r.info.join(' ').indexOf('sem preço de referência') >= 0, r.info); }

/* ---- R22 · meta viva: T1-B de 62 para 60 sc/ha ---- */
{ const c = NOVO(); const S1 = cenClone(SOLO0); S1.cult.find(x => x.id === 'c2').meta = 60; const ctx = soloCtxBase(c, S1); const cu = soloCultivoBase(S1, S1.cult.find(x => x.id === 'c2'));
  ok('AC-SOLO-11 meta 60 sc/ha (3.600 kg/ha) → 72 ÷ 0,6 = 120 = padrão: a sugestão some', soloSugestoes(ctx, cu).sug.length === 0, soloSugestoes(ctx, cu).sug);
  const s = SG(c, 'c2').sug[0]; MUD(c, x => soloAceitar(x, { aceitar: [s] }, 'K-A-4', 'Ana')); const ctx2 = soloCtxBase(c, S1); const r = soloSugestoes(ctx2, cu).sug;
  ok('AC-SOLO-11 com o aceite de 150 feito, "Análise sugere 120" reaparece (−4.560 kg)', r.length === 1 && r[0].sug === 120 && r[0].ef === 150 && r[0].dif === -4560, r); }

/* ---- água no solo: CAD (fórmula única) ---- */
{ const A = SOLO0.agua; const cad = (id) => soloCAD(A.find(m => m.id === id));
  ok('CAD % volume: (32 − 18) ÷ 100 × 40 cm × 10 = 56 mm (T7)', cad('AGS-001').v === 56, cad('AGS-001'));
  ok('CAD % volume: (28 − 15) ÷ 100 × 30 cm × 10 = 39 mm (P1)', cad('AGS-002').v === 39, cad('AGS-002'));
  ok('CAD mm/cm: (3,1 − 1,6) × 30 cm = 45 mm (P2, zona)', cad('AGS-003').v === 45, cad('AGS-003'));
  ok('CAD só com a capacidade de campo (Pivô 12): "não calculável", sem lâmina inventada', cad('AGS-004').v === null && /ponto de murcha/.test(cad('AGS-004').nc), cad('AGS-004'));
  ok('CAD com unidade sem conversão (g/g) e PMP ≥ CC: não calculável', soloCAD({ cc: '0.3', pmp: '0.1', z: '30', un: 'g/g' }).v === null && soloCAD({ cc: '20', pmp: '25', z: '30', un: '% volume' }).v === null);
  const c = NOVO(); const d = { faz: 'Lagoa Grande', tal: 'Pivô 12', zona: '', data: '2026-09-22', prof: '0–40', z: '40', met: 'Curva de retenção (laboratório)', un: '% volume', cc: '30', pmp: '16', fonte: 'Agrolab', resp: 'Ana (agrônoma)' };
  const r = MUD(c, x => soloMedir(x, d, 'K-AG-1', 'Ana')); ok('medição nova AGS-005: CAD 56 mm no aviso; a mais recente do talhão passa a valer', !r.erro && r.id === 'AGS-005' && /CAD 56 mm/.test(r.msg) && soloAguaDo(SOLO0, c, 'Lagoa Grande', 'Pivô 12').id === 'AGS-005', r);
  const r2 = MUD(c, x => soloMedir(x, d, 'K-AG-2', 'Ana')); ok('medição repetida (mesmo talhão, data, profundidade e método) é recusada', /já está registrada como AGS-005/.test(r2.erro || ''), r2);
  const r3 = MUD(c, x => soloMedir(x, Object.assign({}, d, { cc: '' }), 'K-AG-3', 'Ana')); ok('medição sem capacidade de campo é recusada junto ao campo', /capacidade de campo/.test(r3.erro || ''), r3); }

/* ---- unidade de mercado da cultura: a regra não tem constante de saca (A10) ---- */
ok('A10 solo.js não define massa de saca nem aritmética decimal própria', typeof soloSugestoes === 'function' && !/\b60 ?kg|massa: ?60|BigInt\(/.test(String(soloSugestoes)));
