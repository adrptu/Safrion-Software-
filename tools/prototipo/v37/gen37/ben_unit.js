// Testes puros do Beneficiamento BEN-1 (docs/beneficiamento/ESPECIFICACAO.md §10.3, com a caixa de 10 kg do DECISOES §12) · node, sem navegador.
// Carregado depois de: perfis (g2lib) + CEN0 + cenario.js + PRDC + producao.js + BENC + ben.js (+ núcleo da O.S. com CARD e o motor de carência).
// Cada verificação vira uma linha do JSON final. Quem age é o perfil (Igor produção, Paula conferência, Ana gestora, Marta qualidade, Rui almoxarife).
const R = []; function ok(n, c, info) { R.push({ n, ok: !!c, info: c ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 700) }); }
function MUD(c, fn) { const x = cenClone(c); try { const r = fn(x) || {}; if (!r.nada) { Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); } return r; } catch (e) { return { erro: String(e.message || e) }; } }
const NOVO = () => cenClone(CEN0);
const IG = 'Igor', PA = 'Paula', AN = 'Ana', MA = 'Marta', RU = 'Rui', CX = BENC.cx.item;
const O = (c, id) => c.ordens[id]; const LT = (c, id) => c.producao.lotes[id]; const REQ = (c, rid) => c.reqs[rid].itens.find(i => i.prod === CX);
const K = (x) => prFmtT(x, 3);
/* OB-0110 da semente até Encerradas: concluir (Igor), conferir (Paula), devolver a sobra (Rui) e fechar (Igor) */
function fechar110(c) { const a = MUD(c, x => benConcluir(x, 'OB-0110', IG)); const b = MUD(c, x => benConferir(x, 'OB-0110', PA));
  const d = MUD(c, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)); const f = MUD(c, x => benFechar(x, 'OB-0110', IG)); return [a, b, d, f]; }

// ---- U01 · R-A04 · K27 entrada inválida: 0, NaN e 1e999 recusados, nada gravado ----
{ const c = NOVO(); const r = ['0', 'NaN', '1e999', 0, NaN].map(v => MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: v }] }, IG)));
  ok('U01 K27 entrada 0, NaN e 1e999: "Informe a quantidade de entrada" e nenhuma ordem nova', r.every(x => /Informe a quantidade de entrada/.test(x.erro || '')) && !c.ordens['OB-0113'], r.map(x => x.erro)); }

// ---- U02 · R-A02 · K26 rota aprovada e compatível; rascunho nunca; outra fruta sem rota; grão no BEN-3 ----
{ const c = NOVO();
  ok('U02a fruta de campo: só a PACK-FRU v3 é oferecida (a v4 é rascunho)', JSON.stringify(benRotasPara('Mamão Formosa · fruta de campo')) === '["PACK-FRU|3"]', benRotasPara('Mamão Formosa · fruta de campo'));
  const v4 = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 24120 }], rota: 'PACK-FRU|4' }, IG));
  ok('U02b criar com a PACK-FRU v4 (Rascunho) é recusado', /PACK-FRU v4 está em rascunho/.test(v4.erro || ''), v4);
  c.producao.lotes['LX-1'] = Object.assign({}, LT(c, 'L39-131'), { id: 'LX-1', prod: 'Laranja · fruta de campo', cultura: 'Laranja', origem: [] });
  c.producao.movs.push({ id: 'MP-T1', tipo: 'abertura', lote: 'LX-1', kg: 1000, d: '2026-09-25' });
  const lr = MUD(c, x => benNova(x, { lotes: [{ lote: 'LX-1', kg: 1000 }] }, IG));
  ok('U02c outra fruta: "Sem rota aprovada para Laranja · fruta de campo. Dono: Igor"', /^Sem rota aprovada para Laranja · fruta de campo\. Dono: Igor/.test(lr.erro || ''), lr);
  c.producao.lotes['LX-2'] = Object.assign({}, LT(c, 'L39-131'), { id: 'LX-2', prod: 'Milho em grão · úmido', cultura: 'Milho', origem: [] });
  c.producao.movs.push({ id: 'MP-T2', tipo: 'abertura', lote: 'LX-2', kg: 1000, d: '2026-09-25' });
  const mi = MUD(c, x => benNova(x, { lotes: [{ lote: 'LX-2', kg: 1000 }] }, IG));
  ok('U02d grão já tem rota como dado, mas entra no BEN-3 (uma fatia por vez)', /no BEN-1: a SEC-GRA v2 entra no BEN-3/.test(mi.erro || ''), mi);
  const mx = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 1000 }, { lote: 'LX-1', kg: 1000 }] }, IG));
  ok('U02e produtos diferentes na mesma ordem são recusados', /Entradas de produtos diferentes/.test(mx.erro || ''), mx); }

// ---- U03 · R-C01, R-F01, §7 · K01 balanço da OB-0110 (caixa de 10 kg, tara 0,6 kg) ----
{ const c = NOVO(); const b = benBal(O(c, 'OB-0110')); const s = O(c, 'OB-0110').ben.sai;
  ok('U03a K01 tara A 960 × 0,6 = 576 → 9.600 kg; tara B 180 × 0,6 = 108 → 1.800 kg; pela fórmula única (benTara)', benTara(960, 0, benRota('PACK-FRU|3')) === 576 && benTara(180, 0, benRota('PACK-FRU|3')) === 108 && s[0].kg === 9600 && s[1].kg === 1800, s.map(x => x.kg));
  ok('U03b K01 Σ 12.000 kg; diferença 0; recuperação 95,00 %; A 80,00 %; B 15,00 %; descarte 5,00 %', b.sai === 12000 && b.dif === 0 && prFmt(b.rec, 2) === '95,00' && prFmt(b.pp(b.cls.A), 2) === '80,00' && prFmt(b.pp(b.cls.B), 2) === '15,00' && prFmt(b.pp(b.desc), 2) === '5,00', b); }

// ---- U04 · R-C01, R-C04 · K19 pesagem no pallet ----
{ const r = Object.assign({}, benRota('PACK-FRU|3')); r.par = Object.assign({}, r.par, { pesagem: 'pallet' });
  const t = benTara(960, 8, r); const liq = prSub(10376, t); const sem = prSub(10376, benTara(960, 0, r)); const pc = prDiv(sem, 960);
  ok('U04 K19 960 cx e 8 pallets, bruto 10.376: tara 576 + 200 = 776, líquido 9.600; sem o pallet daria 9.800 (10,208333 kg/cx, +2,08 %), dentro do aviso de ±5 % (a R-C04 não pega)',
     t === 776 && liq === 9600 && sem === 9800 && pc === 10.208333 && prCmp(benAbs(prSub(pc, 10)), prMul(10, r.par.aviso_cx)) <= 0, [t, liq, sem, pc]); }

// ---- U05 · R-C03 · K03, K06, K07 caixas sugeridas ----
{ const r = benRota('PACK-FRU|3');
  ok('U05 K03/K06/K07 caixas: ⌈12.000 × 0,95 ÷ 10⌉ = 1.140; ⌈9.270 × 0,95 ÷ 10⌉ = 881; ⌈6.140 × 0,95 ÷ 10⌉ = 584', benCaixas(12000, r) === 1140 && benCaixas(9270, r) === 881 && benCaixas(6140, r) === 584, [benCaixas(12000, r), benCaixas(9270, r), benCaixas(6140, r)]);
  const c = NOVO(); ok('U05b semente: OB-0110 com 1.200 un (1.140 sugeridas e confirmadas em 1.200); OB-0112 com 881 (sugestão)', O(c, 'OB-0110').ins[0].tot === 1200 && O(c, 'OB-0110').ben.cxSug === 1140 && O(c, 'OB-0112').ins[0].tot === 881, [O(c, 'OB-0110').ins, O(c, 'OB-0112').ins]); }

// ---- U06 · R-E07 · K02 genealogia por rateio acumulado; propriedade com semente fixa ----
{ const p = [3010, 2980, 2990, 3020];
  ok('U06a K02 L39-120 = 2.408 + 2.384 + 2.392 + 2.416; L39-121 = 451,5 + 447 + 448,5 + 453; descarte = 150,5 + 149 + 149,5 + 151',
     JSON.stringify(prRateio(9600, p)) === '[2408,2384,2392,2416]' && JSON.stringify(prRateio(1800, p)) === '[451.5,447,448.5,453]' && JSON.stringify(prRateio(600, p)) === '[150.5,149,149.5,151]', [prRateio(9600, p), prRateio(1800, p)]);
  let seed = 7, bad = []; const rnd = () => (seed = (seed * 48271) % 2147483647) / 2147483647;
  for (let i = 0; i < 300; i++) { const n = 1 + Math.floor(rnd() * 5); const ps = Array.from({ length: n }, () => Math.round(rnd() * 5000 * 1000) / 1000 + 1); const S = Math.round(rnd() * 20000 * 1000) / 1000;
    const parts = prRateio(S, ps); if (prCmp(prSoma(parts), S) !== 0) bad.push([S, ps, parts]); }
  ok('U06b propriedade (300 casos, semente fixa): Σ genealogia = saída válida em 6 casas, sem tolerância', !bad.length, bad.slice(0, 2)); }

// ---- U08 · R-A07, R-F02 · K09 massa pesada não se cria; K10 ganho dentro da faixa ----
{ const c = NOVO(); const n0 = c.movs.length;
  const a = MUD(c, x => benSaida(x, 'OB-0110', { fluxo: 'Produto', classe: 'A', cx: 10, bruto: 106 }, IG));
  ok('U08a K09 +100 kg de A: Σ 12.100 > 12.000 + 12 → recusa com as parcelas; nada gravado (sem MV de caixa)', a.erro === 'Saídas pesadas 12.100 kg > entrada 12.000 kg + tolerância 12 kg. Confira a pesagem.' && c.movs.length === n0 && O(c, 'OB-0110').ben.sai.length === 3, a);
  MUD(c, x => benEstornar(x, 'OB-0110', 'S-01', 'Pesagem refeita', '', IG));
  const b = MUD(c, x => benSaida(x, 'OB-0110', { fluxo: 'Produto', classe: 'A', cx: 960, bruto: 10177 }, IG)); const bl = benBal(O(c, 'OB-0110'));
  ok('U08b K10 A com bruto 10.177: líquido 9.601; diferença −1 kg (−0,01 %); faixa 12 kg → dentro, "ganho aparente"', !b.erro && b.s.kg === 9601 && bl.dif === -1 && prFmt(bl.pct, 2) === '−0,01' && bl.dentro && bl.ganho, [b.erro, bl.dif]);
  const tol = MUD(c, x => benSaida(x, 'OB-0110', { fluxo: 'Descarte', destino: 'Compostagem', kg: 11 }, IG));
  ok('U08c a tolerância vale: +11 kg ainda cabe (Σ 12.012 ≤ 12.012); mais 2 kg não (12.014)', !tol.erro && /Saídas pesadas 12.014 kg/.test(MUD(c, x => benSaida(x, 'OB-0110', { fluxo: 'Descarte', destino: 'Compostagem', kg: 2 }, IG)).erro || ''), tol); }

// ---- U08d · R-F02 ganho aparente fora da faixa (o valor absoluto conta nos dois sinais) ----
/* na fruta a R-A07 usa a mesma tolerância da faixa, então o ganho fora da faixa não nasce de um registro novo: fixture da função pura com
   a entrada declarada menor que as saídas (ordem de 11.950 kg com as saídas da OB-0110) */
{ const c = NOVO(); const o = O(c, 'OB-0110'); o.ben.ent[3].kg = 2970; o.ben.conc = { quem: 'Igor', em: '', dif0: -50 }; o.etapa = 'Em conferência'; const b = benBal(o);
  const cf = MUD(c, x => benConferir(x, 'OB-0110', PA));
  ok('U08d ganho de 50 kg (−0,42 %) passa da faixa de 11,95 kg: selo "Ganho aparente acima da faixa", conferir recusado; Igor justifica "Erro de medição" (50 ≤ 59,75 kg)', b.dif === -50 && !b.dentro && b.ganho
     && benSelos(c, O(c, 'OB-0110')).some(s => s.t === 'Ganho aparente acima da faixa') && /fora da faixa/.test(cf.erro || '') && !MUD(c, x => benJustificar(x, 'OB-0110', 'Erro de medição', 'balança da linha descalibrada', IG)).erro, [b.dif, b.faixa, cf]); }

// ---- U09 · R-F02, R-F03, R-G06 · K13, K14, K16 faixa e alçada ----
{ const c = NOVO(); MUD(c, x => benEstornar(x, 'OB-0110', 'S-02', 'Pesagem refeita', '', IG));
  MUD(c, x => benSaida(x, 'OB-0110', { fluxo: 'Produto', classe: 'B', cx: 180, bruto: 1868 }, IG)); MUD(c, x => benConcluir(x, 'OB-0110', IG)); const b = benBal(O(c, 'OB-0110'));
  ok('U09a K13 bruto 1.868: líquido 1.760; diferença 40 kg (0,333333 %) > faixa 12 kg; limite do Igor = mín(60; 100) = 60 kg', b.dif === 40 && b.pct === 0.333333 && !b.dentro && benAlcada(O(c, 'OB-0110'), 40).lim === 60, [b.dif, b.pct]);
  const cf = MUD(c, x => benConferir(x, 'OB-0110', PA)); const j = MUD(c, x => benJustificar(x, 'OB-0110', 'Perda não identificada', 'fruta caída na esteira', IG));
  ok('U09b fora da faixa: conferir recusado antes; Igor justifica dentro da alçada; depois a Paula confere', /fora da faixa/.test(cf.erro || '') && !j.erro && !MUD(c, x => benConferir(x, 'OB-0110', PA)).erro, [cf, j]);
  const c2 = NOVO(); MUD(c2, x => benEstornar(x, 'OB-0110', 'S-02', 'Pesagem refeita', '', IG)); MUD(c2, x => benSaida(x, 'OB-0110', { fluxo: 'Produto', classe: 'B', cx: 180, bruto: 1808 }, IG)); MUD(c2, x => benConcluir(x, 'OB-0110', IG));
  const ji = MUD(c2, x => benJustificar(x, 'OB-0110', 'Perda não identificada', 'x', IG)); const ja = MUD(c2, x => benJustificar(x, 'OB-0110', 'Perda não identificada', 'fruta caída na esteira', AN));
  ok('U09c K14 diferença 100 kg (0,83 %): Igor recusado "0,83 % > alçada de 0,5 %: decide Ana (gestora)"; Ana justifica', ji.erro === '0,83 % > alçada de 0,5 %: decide Ana (gestora). Nada foi alterado.' && !ja.erro && O(c2, 'OB-0110').ben.just[0].quem === 'Ana (gestora)', [ji, ja]);
  const o = { ben: { rota: 'PACK-FRU|3', ent: [{ lote: 'X', kg: 40000 }] } }; const al = benAlcada(o, 150);
  ok('U09d K16 teto: 40.000 kg e diferença 150 kg (0,375 %): o % permitiria 200; o teto de 100 kg dispara e a mensagem diz qual', al.passa && !al.porPct && al.msg === '150 kg > alçada de 100 kg (PACK-FRU v3, sintético)' && benFaixa(40000, benRota('PACK-FRU|3')) === 40, al); }

// ---- U10 · R-F07 · K15 correção na conferência com a alçada de dif₀ ----
{ const c = NOVO(); MUD(c, x => benEstornar(x, 'OB-0110', 'S-02', 'Pesagem refeita', '', IG)); MUD(c, x => benSaida(x, 'OB-0110', { fluxo: 'Produto', classe: 'B', cx: 180, bruto: 1808 }, IG)); MUD(c, x => benConcluir(x, 'OB-0110', IG));
  const sp = MUD(c, x => benSaida(x, 'OB-0110', { fluxo: 'Perda identificada', causa: 'Avaria no manuseio', kg: 100, motivo: 'perda pesada na esteira' }, IG));
  ok('U10a perda sem ticket: "Sem pesagem não é perda identificada. Justifique a diferença (alçada)."', sp.erro === 'Sem pesagem não é perda identificada. Justifique a diferença (alçada).', sp);
  const p = MUD(c, x => benSaida(x, 'OB-0110', { fluxo: 'Perda identificada', causa: 'Avaria no manuseio', kg: 100, ticket: 'TK-5560', motivo: 'perda pesada na esteira' }, IG)); const o = O(c, 'OB-0110');
  ok('U10b perda com ticket por Igor: diferença 0, mas a correção aguarda a gestão (dif₀ 100 kg = 0,83 % > 0,5 %); selo "Corrigido na conferência"', !p.erro && benBal(o).dif === 0 && o.ben.corr.pend && /acima da alçada de 0,5 %/.test(o.ben.corr.msg) && benSelos(c, o).some(s => s.t === 'Corrigido na conferência'), [p.erro, o.ben.corr]);
  const cf = MUD(c, x => benConferir(x, 'OB-0110', PA)); const ci = MUD(c, x => benConfirmarCorrecao(x, 'OB-0110', IG)); const ca = MUD(c, x => benConfirmarCorrecao(x, 'OB-0110', AN));
  ok('U10c conferir antes da gestão é recusado; Igor não confirma a própria correção; Ana confirma e a Paula confere', /decide Ana \(gestora\) antes da conferência/.test(cf.erro || '') && /decisão de Ana \(gestora\)/.test(ci.erro || '') && !ca.erro && !MUD(c, x => benConferir(x, 'OB-0110', PA)).erro, [cf, ci, ca]); }

// ---- U11 · R-A15 · K11 e K12 estornos (caixas, MV, conferência derrubada) e recusas ----
{ const c = NOVO(); const it = () => REQ(c, 'REQ-030'); const n0 = c.movs.length;
  const e1 = MUD(c, x => benEstornar(x, 'OB-0110', 'S-02', 'Erro de digitação', '', IG));
  ok('U11a K11 estornar S-02: em processo 1.800 kg; custódia 60 → 240 un; MV estorno-consumo; S-02 fica riscada (não some)', !e1.erro && benEmProc(O(c, 'OB-0110')) === 1800 && it().custodia === 240 && it().consumido === 960 && c.movs[c.movs.length - 1].tipo === 'estorno-consumo' && O(c, 'OB-0110').ben.sai.length === 3 && O(c, 'OB-0110').ben.sai[1].estorno, [e1, it()]);
  MUD(c, x => benSaida(x, 'OB-0110', { fluxo: 'Produto', classe: 'B', cx: 90, bruto: 954 }, IG)); const ep = benEmProc(O(c, 'OB-0110'));
  MUD(c, x => benEstornar(x, 'OB-0110', 'S-04', 'Pesagem refeita', '', IG)); MUD(c, x => benSaida(x, 'OB-0110', { fluxo: 'Produto', classe: 'B', cx: 180, bruto: 1908 }, IG));
  const tipos = c.movs.slice(n0).map(m => m.tipo);
  ok('U11b relançar B 90 cx (bruto 954 → 900 kg): em processo 900; estornar e relançar 1.908: em processo 0, custódia 60; 4 MV (estorno, consumo, estorno, consumo)', ep === 900 && benEmProc(O(c, 'OB-0110')) === 0 && it().custodia === 60 && JSON.stringify(tipos) === '["estorno-consumo","consumo","estorno-consumo","consumo"]', [ep, tipos]);
  const de = MUD(c, x => benEstornar(x, 'OB-0110', 'S-02', 'Erro de digitação', '', IG)); const so = MUD(c, x => benEstornar(x, 'OB-0110', 'S-03', 'Outro', '  ', IG));
  ok('U11c recusas: registro já estornado; "Outro" sem texto', /Registro já estornado \(S-02\)/.test(de.erro || '') && /Descreva o motivo/.test(so.erro || ''), [de, so]);
  const c2 = NOVO(); MUD(c2, x => benConcluir(x, 'OB-0110', IG)); MUD(c2, x => benConferir(x, 'OB-0110', PA));
  const e3 = MUD(c2, x => benEstornar(x, 'OB-0110', 'S-03', 'Pesagem refeita', '', IG)); const o = O(c2, 'OB-0110'); const b = benBal(o);
  ok('U11d K12 estornar S-03 na conferência: diferença 600 kg (5,00 %), conferência derrubada, primária "Justificar diferença"; a ordem continua Em conferência', !e3.erro && b.dif === 600 && prFmt(b.pct, 2) === '5,00' && !o.ben.conf && benProx(c2, o).acao === 'justificar' && o.etapa === 'Em conferência', [e3, b.dif, benProx(c2, o)]);
  const nv = MUD(c2, x => benSaida(x, 'OB-0110', { fluxo: 'Descarte', destino: 'Compostagem', kg: 600, motivo: 'pesagem refeita' }, IG));
  const rl = MUD(c2, x => benSaida(x, 'OB-0110', { fluxo: 'Descarte', destino: 'Compostagem', kg: 600, subst: 'S-03', motivo: 'pesagem refeita' }, IG));
  ok('U11e na conferência, saída nova só substitui o estornado (sem subst: recusa); relançado: diferença 0, sem alçada (dif₀ = 0), "Conferir balanço" de novo', /só substitui registro estornado/.test(nv.erro || '') && !rl.erro && benBal(O(c2, 'OB-0110')).dif === 0 && !O(c2, 'OB-0110').ben.corr && benProx(c2, O(c2, 'OB-0110')).acao === 'conferir', [nv, rl]);
  MUD(c2, x => benConferir(x, 'OB-0110', PA)); MUD(c2, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)); const f = MUD(c2, x => benFechar(x, 'OB-0110', IG));
  const dest = c2.producao.movs.filter(m => m.ordem === 'OB-0110' && m.tipo === 'destinação');
  ok('U11f K12 o Fechar destina só o descarte relançado (S-04), sem a linha estornada', !f.erro && dest.length === 1 && dest[0].saida === 'S-04' && dest[0].kg === 600, [f.erro, dest]);
  const c3 = NOVO(); ok('U11g recusas por fase: A liberar e Encerradas ("ajuste vinculado com alçada (BEN-7)")', /Estorne só em Em execução/.test(MUD(c3, x => benEstornar(x, 'OB-0112', 'S-01', 'Erro de digitação', '', IG)).erro || '')
     && (fechar110(c3), /ajuste vinculado com alçada \(BEN-7\)/.test(MUD(c3, x => benEstornar(x, 'OB-0110', 'S-01', 'Erro de digitação', '', IG)).erro || '')), ''); }

// ---- U12 · R-A15 · propriedade: lançar X e estornar X devolve balanço, custódia e consumido ----
{ let seed = 11, bad = []; const rnd = () => (seed = (seed * 48271) % 2147483647) / 2147483647;
  for (let i = 0; i < 40; i++) { const c = NOVO(); MUD(c, x => benEstornar(x, 'OB-0110', 'S-01', 'Pesagem refeita', '', IG)); const o0 = O(c, 'OB-0110'); const b0 = benBal(o0), it0 = Object.assign({}, REQ(c, 'REQ-030'));
    const cx = 1 + Math.floor(rnd() * 900); const bruto = Math.round((cx * 10.6 - 50 + rnd() * 100) * 1000) / 1000;
    const s = MUD(c, x => benSaida(x, 'OB-0110', { fluxo: 'Produto', classe: rnd() < .5 ? 'A' : 'B', cx, bruto }, IG)); if (s.erro) { bad.push(['saida', s.erro]); continue; }
    MUD(c, x => benEstornar(x, 'OB-0110', s.s.id, 'Erro de digitação', '', IG)); const b1 = benBal(O(c, 'OB-0110')), it1 = REQ(c, 'REQ-030');
    if (b1.dif !== b0.dif || it1.custodia !== it0.custodia || it1.consumido !== it0.consumido) bad.push([cx, bruto, b0.dif, b1.dif]); }
  ok('U12 propriedade (40 casos, semente fixa): lançar X e estornar X devolve diferença, custódia e consumido', !bad.length, bad.slice(0, 3)); }

// ---- U13 · R-A16 · K28 ID de lote único (sequência da Produção, piso 130) ----
{ const c = NOVO(); const x = cenClone(c);
  ok('U13a próximo ID da semana 39 na semente: L39-133 (a Colheita já usou até L39-132; a sequência é única)', prProxLote(x, '2026-09-26') === 'L39-133', prProxLote(cenClone(c), '2026-09-26'));
  // saída da OB-0112 antes do Fechar da OB-0110: destino novo; o Fechar da OB-0110 continua com L39-120 e L39-121
  MUD(c, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)); MUD(c, x => benRetirar(x, 'OB-0112', 'L39-119', IG)); MUD(c, x => benAutorizarLiberar(x, 'OB-0112', IG));
  MUD(c, x => cenEntregar(x, 'REQ-041', CX, 584, 'Igor', RU)); MUD(c, x => benIniciar(x, 'OB-0112', IG));
  const s = MUD(c, x => benSaida(x, 'OB-0112', { fluxo: 'Produto', classe: 'A', cx: 400, bruto: 4240 }, IG)); const f = fechar110b(c);
  function fechar110b(c) { MUD(c, x => benConcluir(x, 'OB-0110', IG)); MUD(c, x => benConferir(x, 'OB-0110', PA)); return MUD(c, x => benFechar(x, 'OB-0110', IG)); }
  ok('U13b saída da OB-0112 vai ao L39-133; o Fechar da OB-0110 cria L39-120 e L39-121 (sem colisão)', !s.erro && s.s.lote === 'L39-133' && !f.erro && LT(c, 'L39-120') && LT(c, 'L39-121') && !LT(c, 'L39-133'), [s.erro, s.s && s.s.lote, f.erro]);
  const e = MUD(c, x => benEstornar(x, 'OB-0112', s.s.id, 'Erro de digitação', '', IG)); const s2 = MUD(c, x => benSaida(x, 'OB-0112', { fluxo: 'Produto', classe: 'B', cx: 10, bruto: 106 }, IG));
  ok('U13c ID de saída estornada não volta: a classe B nova ganha o L39-134', !e.erro && s2.s.lote === 'L39-134', s2.s && s2.s.lote);
  const c4 = NOVO(); c4.ordens['OB-0110'].ben.sai[0].lote = 'L39-140'; const x4 = cenClone(c4);
  ok('U13e K28 gerador que olha só os lotes falha: um destino de saída ainda sem lote (L39-140) também conta; o próximo é L39-141', prProxLote(x4, '2026-09-26') === 'L39-141', prProxLote(cenClone(c4), '2026-09-26'));
  const c2 = NOVO(); c2.producao.lotes['L39-120'] = Object.assign({}, LT(c2, 'L39-117'), { id: 'L39-120' }); const ff = fechar110(c2)[3];
  ok('U13d Fechar com ID que já existe para outra origem é recusado', /Lote L39-120 já existe/.test(ff.erro || ''), ff); }

// ---- U14 · R-A11 · K30 repetição: chave, versão, reserva e Fechar/Autorizar repetidos ----
{ cenReset(); const k = { fluxo: 'Descarte', destino: 'Compostagem', kg: 5, chave: 'W-SAI-T1' };
  const rev0 = cenGet().rev; const a = benMudar(x => benSaida(x, 'OB-0110', k, IG)); const rev1 = cenGet().rev; const b = benMudar(x => benSaida(x, 'OB-0110', k, IG)); const c = cenGet();
  ok('U14a mesma chave e mesmo conteúdo: 1 registro, rev +1; a segunda resposta é "Já feito" sem gravar', !a.erro && b.nada && /^Já feito: S-04 registrada/.test(b.msg) && rev1 === rev0 + 1 && c.rev === rev1 && O(c, 'OB-0110').ben.sai.length === 4, [a, b, rev0, c.rev]);
  const d = benMudar(x => benSaida(x, 'OB-0110', Object.assign({}, k, { kg: 6 }), IG));
  ok('U14b mesma chave com outro conteúdo: conflito, nada gravado', /conflito, nada gravado/.test(d.erro || '') && cenGet().rev === rev1, d);
  const v = O(cenGet(), 'OB-0110').ver; benMudar(x => benSaida(x, 'OB-0110', { fluxo: 'Descarte', destino: 'Compostagem', kg: 1, chave: 'W-SAI-T2', ver: v }, IG));
  const q2 = benMudar(x => benSaida(x, 'OB-0110', { fluxo: 'Descarte', destino: 'Compostagem', kg: 1, chave: 'W-SAI-T3', ver: v }, IG));
  ok('U14c dois quadros abertos na mesma versão: o segundo recebe conflito de versão', /A OB-0110 mudou depois que você abriu/.test(q2.erro || ''), q2);
  const c2 = NOVO(); fechar110(c2); const rf = MUD(c2, x => benFechar(x, 'OB-0110', IG)); const ra = MUD(c2, x => benAutorizarLiberar(x, 'OB-0110', IG));
  ok('U14d Fechar e Autorizar e liberar repetidos: "Já feito"', /^Já feito: OB-0110 encerrada/.test(rf.erro || '') && /^Já feito/.test(ra.erro || ''), [rf, ra]);
  /* fixture: lote liberado de 2.000 kg classe A e pedido de 1.000 kg A: 1.000 e depois 500 → falta 0, disponível 1.000 */
  const c3 = NOVO(); fechar110(c3); MUD(c3, x => benResultado(x, 'L39-120', 'Conforme', '', MA)); MUD(c3, x => benDecidir(x, 'L39-120', 'Liberar', {}, MA));
  c3.producao.pedidos['PV-T9'] = { id: 'PV-T9', cliente: 'Teste', prod: 'Mamão Formosa · fruta embalada', cultura: 'Mamão Formosa', classe: 'A', saf: '', tipo: 'pronta', janela: '—', qtd: 1000, dest: 'MI-BR' };
  const r1 = MUD(c3, x => prReservar(x, { pedido: 'PV-T9', lote: 'L39-120', kg: 1000, chave: 'W-RS-T9a' })); const r2 = MUD(c3, x => prReservar(x, { pedido: 'PV-T9', lote: 'L39-120', kg: 500, chave: 'W-RS-T9b' }));
  ok('U14e reservar 1.000 e depois 500 para um pedido de 1.000 kg: a segunda é recusada pela falta (0 kg); disponível 8.600', !r1.erro && /Acima da falta do PV-T9: 0 kg/.test(r2.erro || '') && prSaldos(c3, LT(c3, 'L39-120')).disp === 8600, [r1.erro, r2.erro]); }

// ---- U15 · R-E04, R-E05 · K21 reserva do PV-031 (prReservar, a mesma da Colheita) ----
{ const c = NOVO(); fechar110(c);
  const ei = MUD(c, x => prReservar(x, { pedido: 'PV-031', lote: 'L39-120', kg: 9600 }));
  ok('U15a K21 L39-120 Em inspeção: reserva recusada', /L39-120 não está apto \(Em inspeção/.test(ei.erro || ''), ei);
  MUD(c, x => benResultado(x, 'L39-120', 'Conforme', '', MA)); MUD(c, x => benDecidir(x, 'L39-120', 'Liberar', {}, MA));
  const S = prSaldos(c, LT(c, 'L39-120')); const f0 = prFalta(c, c.producao.pedidos['PV-031']);
  const ac = MUD(c, x => prReservar(x, { pedido: 'PV-031', lote: 'L39-120', kg: 10000 }));
  ok('U15b K21 liberado: disponível 9.600, falta 10.000 → sugestão mín = 9.600; 10.000 recusado ("Acima do disponível do L39-120: 9.600 kg.")', S.disp === 9600 && f0 === 10000 && ac.erro === 'Acima do disponível do L39-120: 9.600 kg.', [S.disp, f0, ac]);
  const rs = MUD(c, x => prReservar(x, { pedido: 'PV-031', lote: 'L39-120', kg: 9600 }));
  ok('U15c K21 reservado 9.600; falta 400 kg; disponível 0; RS-0002 (a RS-0001 é da soja)', !rs.erro && rs.rs.id === 'RS-0002' && prFalta(c, c.producao.pedidos['PV-031']) === 400 && prSaldos(c, LT(c, 'L39-120')).disp === 0, rs);
  MUD(c, x => benResultado(x, 'L39-121', 'Conforme', '', MA)); MUD(c, x => benDecidir(x, 'L39-121', 'Liberar', {}, MA));
  const cb = MUD(c, x => prReservar(x, { pedido: 'PV-031', lote: 'L39-121', kg: 100 }));
  c.producao.pedidos['PV-T0'] = Object.assign({}, c.producao.pedidos['PV-031'], { id: 'PV-T0', classe: '' }); const cv = MUD(c, x => prReservar(x, { pedido: 'PV-T0', lote: 'L39-121', kg: 100 }));
  ok('U15d classe diferente recusada ("Classe B ≠ A do PV-031"); classe vazia no pedido recusada ("Classe não informada")', cb.erro === 'Classe B ≠ A do PV-031.' && /^Classe não informada \(PV-T0\)/.test(cv.erro || ''), [cb, cv]); }

// ---- U16 · R-E03, R-E06 · K22, K23, K24 bloqueio, reclassificação e cancelamento com reserva ----
{ const c = NOVO(); fechar110(c); MUD(c, x => benResultado(x, 'L39-120', 'Conforme', '', MA)); MUD(c, x => benDecidir(x, 'L39-120', 'Liberar', {}, MA));
  MUD(c, x => prReservar(x, { pedido: 'PV-031', lote: 'L39-120', kg: 9600 })); const ped = () => prSitPed(c, c.producao.pedidos['PV-031']);
  const bs = MUD(c, x => benDecidir(x, 'L39-120', 'Bloquear', {}, MA)); const bl = MUD(c, x => benDecidir(x, 'L39-120', 'Bloquear', { motivo: 'reclamação de transporte' }, MA));
  ok('U16a K22 bloquear exige motivo; bloqueado: RS-0002 continua Ativa com expedição impedida; PV-031 Em risco; falta 400; disponível 0', /motivo do bloqueio/.test(bs.erro || '') && !bl.erro && c.producao.reservas['RS-0002'].st === 'Ativa' && ped().t === 'Em risco' && prFalta(c, c.producao.pedidos['PV-031']) === 400 && prSaldos(c, LT(c, 'L39-120')).disp === 0, [bs, bl.erro, ped().t]);
  MUD(c, x => benDecidir(x, 'L39-120', 'Liberar', {}, MA));
  ok('U16b K22 liberar de novo: o impedimento some sem reativar nada; nova reserva recusada (disponível 0)', ped().t === 'Parcial' && /Acima do disponível do L39-120: 0 kg/.test(MUD(c, x => prReservar(x, { pedido: 'PV-031', lote: 'L39-120', kg: 1 })).erro || ''), ped().t);
  const f0 = prFis(c, 'L39-120'); const tot0 = prSoma(Object.values(c.producao.lotes).filter(L => L.cultura === 'Mamão Formosa').map(L => prFis(c, L.id)));
  const rc = MUD(c, x => benDecidir(x, 'L39-120', 'Reclassificar', { classe: 'B', motivo: 'calibre menor na reinspeção' }, MA));
  const tot1 = prSoma(Object.values(c.producao.lotes).filter(L => L.cultura === 'Mamão Formosa').map(L => prFis(c, L.id)));
  ok('U16c K23 reclassificar A → B: físico 9.600 antes e depois; Σ do mamão igual; RS-0002 Ativa com expedição impedida (classe B ≠ A); PV-031 Em risco', !rc.erro && f0 === 9600 && prFis(c, 'L39-120') === 9600 && tot0 === tot1 && LT(c, 'L39-120').classe === 'B' && ped().t === 'Em risco' && /expedição impedida/.test(rc.msg), [rc, ped().t]);
  const cs = MUD(c, x => prCancelarReserva(x, 'RS-0002', '')); const cc = MUD(c, x => prCancelarReserva(x, 'RS-0002', 'cliente quer só classe A'));
  ok('U16d K24 cancelar sem motivo recusado; com motivo: Cancelada, L39-120 disponível 9.600 (classe B), PV-031 falta 10.000, MP de cancelamento', /motivo/.test(cs.erro || '') && !cc.erro && c.producao.reservas['RS-0002'].st === 'Cancelada' && prSaldos(c, LT(c, 'L39-120')).disp === 9600 && prFalta(c, c.producao.pedidos['PV-031']) === 10000 && c.producao.movs.some(m => m.tipo === 'cancelamento de reserva' && m.reserva === 'RS-0002'), [cs, cc]); }

// ---- U17 · R-E02, R-E03 · K20 e K25 resultado e decisão ----
{ const c = NOVO(); fechar110(c);
  const l0 = MUD(c, x => benDecidir(x, 'L39-120', 'Liberar', {}, MA)); const ig = MUD(c, x => benResultado(x, 'L39-120', 'Conforme', '', IG)); const pl = MUD(c, x => prLiberarLote(x, 'L39-120', MA));
  ok('U17a K20 liberar sem resultado recusado ("Registre o resultado (INSP-92)"); Igor não registra resultado; o "Liberar lote" da Colheita não pula a inspeção', l0.erro === 'Registre o resultado (INSP-92).' && /decisão de Ana \(agrônoma\) ou Marta \(qualidade\)/.test(ig.erro || '') && /registre o resultado da inspeção INSP-92/.test(pl.erro || ''), [l0, ig, pl]);
  const r = MUD(c, x => benResultado(x, 'L39-120', 'Conforme', '', MA)); const d = MUD(c, x => benDecidir(x, 'L39-120', 'Liberar', {}, MA));
  ok('U17b K20 resultado Conforme e Liberar (Marta): L39-120 Liberado; a OB-0110 continua Encerradas (a decisão não reabre a ordem)', !r.erro && !d.erro && prSaldos(c, LT(c, 'L39-120')).q === 'Liberado' && O(c, 'OB-0110').etapa === 'Encerradas' && /Marta \(qualidade\)/.test(d.msg), [r, d]);
  const lb = MUD(c, x => benDecidir(x, 'L26-118', 'Liberar', {}, MA)); const ds = MUD(c, x => benDecidir(x, 'L26-118', 'Destinar', {}, MA));
  const dd = MUD(c, x => benDecidir(x, 'L26-118', 'Destinar', { motivo: 'maturação avançada: indústria de polpa' }, MA)); const S = prSaldos(c, LT(c, 'L26-118'));
  ok('U17c K25 L26-118 não conforme: Liberar recusado com as três saídas; destinar sem motivo recusado; com motivo: físico 0, Destinado, MP destinação, rastreio fica', lb.erro === 'Resultado não conforme (INSP-93): libere como classe atingida, mantenha o bloqueio ou destine.' && /motivo da destinação/.test(ds.erro || '') && !dd.erro && S.fis === 0 && LT(c, 'L26-118').q0 === 'Destinado' && c.producao.movs.some(m => m.lote === 'L26-118' && m.tipo === 'destinação' && m.kg === -300), [lb, ds, dd, S]);
  const c5 = NOVO(); fechar110(c5); MUD(c5, x => benResultado(x, 'L39-120', 'Conforme', '', MA));
  ok('U17e as opções da decisão seguem o resultado: Não conforme sem "Liberar"; Conforme sem "Liberar como classe atingida"', JSON.stringify(benDecisoes(c5, LT(c5, 'L26-118'))) === '["Liberar como classe atingida","Manter bloqueio","Destinar"]'
     && JSON.stringify(benDecisoes(c5, LT(c5, 'L39-120'))) === '["Liberar","Manter bloqueio","Destinar"]' && JSON.stringify(benDecisoes(c5, LT(c5, 'L39-121'))) === '[]', [benDecisoes(c5, LT(c5, 'L26-118')), benDecisoes(c5, LT(c5, 'L39-120'))]);
  const c6 = NOVO(); const rv = MUD(c6, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Com avaria' })); const li = MUD(c6, x => prLiberarLote(x, rv.L.id, IG)); const lm = MUD(c6, x => prLiberarLote(x, rv.L.id, MA));
  ok('U17f "Liberar lote" da Colheita: Igor (produção) recusado ("decisão de Ana (agrônoma) ou Marta (qualidade)"); Marta libera e o nome gravado é o do perfil', /decisão de Ana \(agrônoma\) ou Marta \(qualidade\)/.test(li.erro || '') && !lm.erro && LT(c6, rv.L.id).lib.quem === 'Marta (qualidade)', [li, lm]);
  const c2 = NOVO(); const ca = MUD(c2, x => benDecidir(x, 'L26-118', 'Liberar como classe atingida', { classe: 'B' }, MA));
  ok('U17d "Liberar como classe atingida" (B): grava a classe e o MP de reclassificação sem mudar a massa, e libera', !ca.erro && LT(c2, 'L26-118').classe === 'B' && prSaldos(c2, LT(c2, 'L26-118')).q === 'Liberado' && prFis(c2, 'L26-118') === 300 && c2.producao.movs.some(m => m.lote === 'L26-118' && m.tipo === 'reclassificação' && m.kg === 0), ca); }

// ---- U18 · R-A13 · K29 condição do ativo (função pura, sem tocar no armazenamento) ----
ok('U18 K29 condição do a13: "Apto" da semente; "Restrito · monitorado" → aviso; "Bloqueado" e "Aguardando teste" → impedimento com o texto literal',
   benCondAtivo(null, 'a13').k === 'ok' && benCondAtivo({ ativos: { a13: { cond: 'Restrito · monitorado' } } }, 'a13').k === 'aviso' && benCondAtivo({ ativos: { a13: { cond: 'Bloqueado' } } }, 'a13').k === 'imped'
   && benCondAtivo({ ativos: { a13: { cond: 'Aguardando teste' } } }, 'a13').t === 'Aguardando teste', [benCondAtivo(null, 'a13')]);

// ---- U19 · R-A09, R-A10 · K04, K05 fechar: custódia, etapas, lotes, inspeção, genealogia ----
{ const c = NOVO(); MUD(c, x => benConcluir(x, 'OB-0110', IG)); MUD(c, x => benConferir(x, 'OB-0110', PA)); const f0 = MUD(c, x => benFechar(x, 'OB-0110', IG));
  ok('U19a K04 Fechar recusado pela custódia: "Sobra em custódia: Caixa de mamão Formosa 10 kg 60 un. Receba a devolução no Estoque."', f0.erro === 'Sobra em custódia: Caixa de mamão Formosa 10 kg 60 un. Receba a devolução no Estoque.', f0);
  MUD(c, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU));
  ok('U19b K04 devolução apta de 60 → CX26-01 com 600 un', c.lotes[CX + '|CX26-01'].fisico === 600, c.lotes[CX + '|CX26-01']);
  const n0 = c.producao.movs.length; const f = MUD(c, x => benFechar(x, 'OB-0110', IG)); const mv = c.producao.movs.slice(n0).map(m => m.tipo);
  const L20 = LT(c, 'L39-120'), L21 = LT(c, 'L39-121'); const I = c.producao.ben.insp['INSP-92'];
  ok('U19c K05 L39-120 9.600 kg 960 cx e L39-121 1.800 kg 180 cx Em inspeção; INSP-92 aberta (Marta, prazo 28/09)', !f.erro && prFis(c, 'L39-120') === 9600 && L20.cx === 960 && prFis(c, 'L39-121') === 1800 && L21.cx === 180
     && prSaldos(c, L20).q === 'Em inspeção' && I.estado === 'Aberta' && I.prazo === '2026-09-28' && JSON.stringify(I.lotes) === '["L39-120","L39-121"]' && /Marta/.test(I.resp), [f.erro, I]);
  ok('U19d K05 MP: 2 produção, 1 destinação, 4 consumo no processo; L38-115..118 esgotados; descarte destinado com rastreio; disponível 0', mv.filter(t => t === 'produção').length === 2 && mv.filter(t => t === 'destinação').length === 1 && mv.filter(t => t === 'consumo no processo').length === 4
     && ['L38-115', 'L38-116', 'L38-117', 'L38-118'].every(id => prSaldos(c, LT(c, id)).esgotado) && prSaldos(c, L20).disp === 0, mv);
  const fr = benParaFrente(c, 'L38-118');
  ok('U19e K02 genealogia: L39-120 vem dos 4 lotes (2.408 + 2.384 + 2.392 + 2.416); para frente de L38-118 (saldo 0): L39-120, L39-121 e descarte', JSON.stringify(L20.origem.map(x => x.kg)) === '[2408,2384,2392,2416]' && fr.length === 3 && fr.map(x => x.lote || x.prod).join('|') === 'L39-120|L39-121|Descarte · Compostagem' && prCmp(prSoma(fr.map(x => x.kg)), 3020) === 0, fr);
  ok('U19f K05 etapas exigidas cumpridas; as não pertinentes dizem por quê', benEtapas(c, O(c, 'OB-0110')).every(e => e.pert !== 'Exigida' || e.sit === 'Cumprida') && benEtapas(c, O(c, 'OB-0110')).find(e => e.nome === 'Paletização').ev === 'pallet no BEN-8', benEtapas(c, O(c, 'OB-0110')));
  const c2 = NOVO(); MUD(c2, x => benConcluir(x, 'OB-0110', IG)); MUD(c2, x => benConferir(x, 'OB-0110', PA)); MUD(c2, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU));
  c2.ordens['OB-0110'].ben.sai.forEach(s => { if (s.fluxo === 'Produto') s.classe = ''; });
  const fe = MUD(c2, x => benFechar(x, 'OB-0110', IG)); ok('U19g fixture com etapa exigida pendente (Produto sem classe): Fechar recusado', /Etapa exigida pendente: Triagem e classificação/.test(fe.erro || ''), fe);
  const c3 = NOVO(); MUD(c3, x => benConcluir(x, 'OB-0110', IG)); const fc = MUD(c3, x => benFechar(x, 'OB-0110', IG));
  ok('U19h Fechar sem conferência recusado; e só em Em conferência', /ainda não conferido/.test(fc.erro || '') && /Feche só em Em conferência/.test(MUD(NOVO(), x => benFechar(x, 'OB-0112', IG)).erro || ''), fc); }

// ---- U20 · semente coerente (REQ, físico, Kanban) ----
{ const c = NOVO(); const bad = [];
  Object.values(c.reqs).forEach(r => r.itens.forEach(i => { if (Math.abs((i.entregue - i.devolvido) - (i.consumido + i.custodia)) > 1e-6 || i.consumido + i.custodia > i.solicitado + 1e-6) bad.push([r.id, i.prod]); }));
  const it = REQ(c, 'REQ-030'); const fases = BEN_FASES.map(f => benOrdens(c).filter(o => o.etapa === f).length).join('·');
  ok('U20a todo item de requisição: entregue − devolvido = consumido + custódia ≤ solicitado', !bad.length, bad);
  ok('U20b REQ-030: solicitado = ins.tot = 1.200, entregue 1.200, consumido 1.140 (960 + 180), custódia 60, a entregar 0', it.solicitado === O(c, 'OB-0110').ins[0].tot && it.entregue === 1200 && it.consumido === 1140 && it.custodia === 60 && cenSaldoEntregar(it) === 0, it);
  ok('U20c físico de cada entrada Em processo = o entregue à ordem; Σ 12.000', O(c, 'OB-0110').ben.ent.every(e => prFis(c, e.lote) === e.kg && prSaldos(c, LT(c, e.lote)).q === 'Em processo') && benEntrada(O(c, 'OB-0110')) === 12000, O(c, 'OB-0110').ben.ent);
  ok('U20d Kanban da semente (só ordens de beneficiamento): A liberar 1 · Liberadas 0 · Em execução 1 · Em conferência 0 · Encerradas 0', fases === '1·0·1·0·0', fases);
  const tot = x => prSoma(Object.values(x.producao.lotes).filter(L => L.cultura === 'Mamão Formosa').map(L => prFis(x, L.id)));
  const c2 = NOVO(); const t0 = tot(c2); const f = fechar110(c2)[3]; const t1 = tot(c2); const b = benBal(O(c2, 'OB-0110'));
  ok('U20e Fechar: o físico do mamão muda só pelo que saiu do vendável (descarte e diferença): Σ antes − Σ depois = descarte + perdas + diferença', !f.erro && prCmp(prSub(t0, t1), prSoma([b.desc, b.outro, b.perda, b.dif])) === 0, [t0, t1]); }

// ---- U21 · R-A05 · uma regra para o número da REQ; ordem sem material sem REQ ----
{ const c = NOVO(); MUD(c, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)); MUD(c, x => benRetirar(x, 'OB-0112', 'L39-119', IG)); const l = MUD(c, x => benAutorizarLiberar(x, 'OB-0112', IG));
  ok('U21a K08 liberar a OB-0112 (com a REQ-030 na semente): REQ-041 (maior + 1, piso 41) com 584 un reservadas; CX26-01 disponível 16', !l.erro && O(c, 'OB-0112').req === 'REQ-041' && REQ(c, 'REQ-041').solicitado === 584 && cenDisp(c.lotes[CX + '|CX26-01']) === 16, [l, O(c, 'OB-0112').req]);
  ok('U21b a O.S. segue a mesma sequência: osc_reqId → REQ-042', typeof osc_reqId !== 'function' || osc_reqId(c) === 'REQ-042', typeof osc_reqId === 'function' ? osc_reqId(c) : 'sem osc_reqId');
  /* BEN-REV-05 (09/10): a expectativa antiga ("0 caixa libera sem REQ") prendia a ordem: liberada sem caixa, o Produto é recusado pela custódia
     e o Concluir exige Produto. Agora 0 caixa é recusado na criação; "sem material libera sem REQ" segue valendo para rota sem caixa (U21d) */
  const c2 = NOVO(); const n = MUD(c2, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 24120 }], cx: 0 }, IG));
  ok('U21c BEN-REV-05 0 caixa na PACK-FRU v3: "Caixas: ao menos 1 un. O Produto da PACK-FRU v3 sai em caixa (sugestão 2292)." e nenhuma ordem nova', n.erro === 'Caixas: ao menos 1 un. O Produto da PACK-FRU v3 sai em caixa (sugestão 2292).' && !O(c2, 'OB-0113'), n);
  const n2 = MUD(c2, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 24120 }] }, IG)); (c2.ordens[n2.id] || {}).ins = [];   /* fixture: rota sem material (a SEC-GRA entra no BEN-3) */
  const lr = MUD(c2, x => benAutorizarLiberar(x, n2.id, IG));
  ok('U21d ordem sem material libera sem abrir requisição e sem prometer entrega de caixa; todo ID de REQ casa com /^REQ-\\d{3}$/', !n2.erro && !lr.erro && !(O(c2, n2.id) || {}).req && Object.keys(c2.reqs).length === Object.keys(CEN0.reqs).length && !/entrega as caixas/.test(lr.msg) && Object.keys(c.reqs).every(k => /^REQ-\d{3}$/.test(k)), [n2, lr]); }

// ---- U22 · R-G01, R-G02 · parâmetros com fonte; nada real; nenhuma constante de saca ou rendimento ----
{ const src = JSON.stringify(BENC) + JSON.stringify(CEN0.producao.ben);
  ok('U22a todo parâmetro de rota tem fonte "sintético · vN"', Object.values(BENC.rotas).every(r => /^sintético · v\d+$/.test((r.par || {}).fonte || '')), Object.values(BENC.rotas).map(r => (r.par || {}).fonte));
  ok('U22b semente sem CPF, CNPJ, e-mail ou telefone', !/\d{3}\.\d{3}\.\d{3}-\d{2}|\d{2}\.\d{3}\.\d{3}\/\d{4}|@[a-z]|\(\d{2}\) ?\d{4,5}-\d{4}/.test(src), '');
  ok('U22c caixa com massa declarada da fonte única (dados_cad.EMB_PACK): formosa 10 kg, tara 0,6 kg', BENC.cx.massa === '10' && BENC.cx.tara === '0.6' && /CEPEA\/Ceagesp/.test(BENC.cx.fonte), BENC.cx); }

// ---- U23 · R-C02 · K17 caixas acima da custódia; consumo grava MV; estorno grava estorno-consumo ----
{ const c = NOVO(); MUD(c, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)); MUD(c, x => benRetirar(x, 'OB-0112', 'L39-119', IG)); MUD(c, x => benAutorizarLiberar(x, 'OB-0112', IG));
  const sem = MUD(c, x => benSaida(x, 'OB-0112', { fluxo: 'Produto', classe: 'A', cx: 10, bruto: 106 }, IG));
  MUD(c, x => cenEntregar(x, 'REQ-041', CX, 584, 'Igor', RU)); MUD(c, x => benIniciar(x, 'OB-0112', IG));
  const a = MUD(c, x => benSaida(x, 'OB-0112', { fluxo: 'Produto', classe: 'A', cx: 585, bruto: 6201 }, IG)); const n0 = c.movs.length;
  const b = MUD(c, x => benSaida(x, 'OB-0112', { fluxo: 'Produto', classe: 'A', cx: 500, bruto: 5300 }, IG));
  ok('U23a K17 saída antes de iniciar recusada; depois da entrega de 584: 585 cx → "Caixas acima da custódia: 584 un. Peça a entrega no Estoque."; 500 cx baixam a custódia com MV consumo',
     /Registre saídas só em Em execução/.test(sem.erro || '') && a.erro === 'Caixas acima da custódia: 584 un. Peça a entrega no Estoque.' && !b.erro && REQ(c, 'REQ-041').custodia === 84 && c.movs[n0].tipo === 'consumo' && c.movs[n0].det === CX + ' 500', [sem, a, b.erro]);
  ok('U23b a entrega no balcão fica confirmada ao iniciar (sem "aguardando confirmação no app" para a ordem de processo)', REQ(c, 'REQ-041').confirmado === 'balcao', REQ(c, 'REQ-041'));
  const av = MUD(c, x => benSaida(x, 'OB-0112', { fluxo: 'Produto', classe: 'B', cx: 80, bruto: 948 }, IG));
  ok('U23c K18 líquido por caixa fora de ±5 % gera aviso, não trava (900 kg em 80 cx = 11,25 kg/cx, +12,5 %)', !av.erro && /11,25 kg por caixa contra 10 kg \(\+12,50 %\)/.test(av.msg), av); }

// ---- U24 · K31 inspeção nova pela sequência única (INSP-105 é a maior da Manutenção) ----
{ const c = NOVO(); const x = cenClone(c); ok('U24 primeira inspeção gerada no cenário limpo: INSP-106', benInspId(x) === 'INSP-106', benInspId(cenClone(c))); }

// ---- U25 · R-A03, R-A05 · K06, K07, K08 impedimentos, retirar entrada e liberar ----
{ const c = NOVO(); const im = benImpedimentos(c, O(c, 'OB-0112'));
  ok('U25a K06 duas causas juntas, cada uma com dono e atalho: "L39-119 em inspeção (INSP-94) · Marta (qualidade)" e "…: 540 un disponíveis para 881 un · Estoque" (I4: devolução da OB-0110)',
     im.length === 2 && im[0].t === 'L39-119 em inspeção (INSP-94) · Marta (qualidade)' && im[1].t === CX + ': 540 un disponíveis para 881 un · Estoque' && /OB-0110 tem 60 un em custódia/.test(im[1].link.why), im);
  const r0 = MUD(c, x => benAutorizarLiberar(x, 'OB-0112', IG)); const an = MUD(c, x => benAutorizarLiberar(x, 'OB-0112', AN));
  ok('U25b liberar com causas: recusa com as duas e nada gravado; Ana não autoriza (decisão do responsável de produção)', /^Liberação recusada · 2 causas/.test(r0.erro || '') && O(c, 'OB-0112').etapa === 'A liberar' && /decisão de Igor \(responsável de produção\)/.test(an.erro || ''), [r0, an]);
  const rt = MUD(c, x => benRetirar(x, 'OB-0112', 'L39-119', IG)); const im2 = benImpedimentos(c, O(c, 'OB-0112'));
  ok('U25c K07 retirar o L39-119: v2, 6.140 kg, 584 un (sugestão acompanha); ainda recusa 540 de 584 com a I4', !rt.erro && O(c, 'OB-0112').versao === 'v2' && benEntrada(O(c, 'OB-0112')) === 6140 && O(c, 'OB-0112').ins[0].tot === 584 && im2.length === 1 && /540 un disponíveis para 584 un/.test(im2[0].t) && /devolução da OB-0110/.test(im2[0].link.t), [rt, im2]);
  const c2 = NOVO(); MUD(c2, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)); const im3 = benImpedimentos(c2, O(c2, 'OB-0112'));
  ok('U25d K07 depois da devolução e sem retirar: as duas causas, agora "600 un disponíveis para 881 un" e a I4b (sem sobra em custódia)', im3.length === 2 && /600 un disponíveis para 881 un/.test(im3[1].t) && im3[1].link.t === 'Ver saldo de caixas no Estoque', im3);
  MUD(c2, x => benRetirar(x, 'OB-0112', 'L39-119', IG)); const l = MUD(c2, x => benAutorizarLiberar(x, 'OB-0112', IG)); const h = O(c2, 'OB-0112').ben.hist.slice(-2); const hr = benHoras(O(c2, 'OB-0112'));
  ok('U25e K08 liberar: 2 eventos (CMD-42: v2, 6.140 kg, 584 un, PACK-FRU v3; CMD-06: REQ-041); L39-117 e L39-118 reservados à ordem; h-linha 2,56; HH 15,35',
     !l.erro && /\(CMD-42\)$/.test(h[0].ev) && /PACK-FRU v3 · L39-117, L39-118 · 6.140 kg · 584 un/.test(h[0].det) && /\(CMD-06\)$/.test(h[1].ev) && /^REQ-041 reservou 584 un/.test(h[1].det)
     && ['L39-117', 'L39-118'].every(id => prSaldos(c2, LT(c2, id)).ordem === 'OB-0112') && prFmt(hr.h, 2) === '2,56' && prFmt(hr.hh, 2) === '15,35', [l, h, hr]); }

// ---- U26 · integração com a Colheita: o lote recebido "em processo" entra na ordem; saídas no mesmo modelo de lote; carência herdada ----
{ const c = NOVO();
  ok('U26a lotes da Colheita em processo (L38-132, L39-131, L39-132: pós-colheita do CAR0) aparecem como entrada possível; os do packing já estão em ordem ou em inspeção', benLotesAptos(c).map(L => L.id).join(',') === 'L38-132,L39-131,L39-132', benLotesAptos(c).map(L => L.id));
  MUD(c, x => cenReceber(x, CX, 'CX26-02', 3000, 'un', 'Packing', '—', 'NF-90011', true, RU));
  const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 24120 }] }, IG)); const id = n.id || 'OB-0113';
  ok('U26b ordem nova do L39-131 (Colheita, Lagoa Grande): OB-0113, PACK-FRU v3 (única aprovada, I1), 2.292 caixas sugeridas; nada reservado antes de liberar', !n.erro && id === 'OB-0113' && O(c, id).ben.rota === 'PACK-FRU|3' && O(c, id).ins[0].tot === 2292 && !LT(c, 'L39-131').ordem, n);
  MUD(c, x => benAutorizarLiberar(x, id, IG)); MUD(c, x => cenEntregar(x, O(c, id).req, CX, 2292, 'Igor', RU)); MUD(c, x => benIniciar(x, id, IG));
  MUD(c, x => benSaida(x, id, { fluxo: 'Produto', classe: 'A', cx: 2000, bruto: 21200 }, IG)); MUD(c, x => benSaida(x, id, { fluxo: 'Descarte', destino: 'Compostagem', kg: 4000 }, IG));
  const dup = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 100 }] }, IG));
  ok('U26c o lote em processo numa ordem não entra em outra', /L39-131 em processo na OB-0113/.test(dup.erro || ''), dup);
  MUD(c, x => benConcluir(x, id, IG)); const ji = MUD(c, x => benJustificar(x, id, 'Perda não identificada', 'fruta mole retirada sem pesar', IG));
  const j = MUD(c, x => benJustificar(x, id, 'Perda não identificada', 'fruta mole retirada sem pesar', AN));   /* 120 kg: o % (0,5 % = 120,6 kg) permitiria; o teto de 100 kg manda à gestão */ MUD(c, x => benConferir(x, id, PA));
  const it = REQ(c, O(c, id).req); MUD(c, x => cenDevolver(x, O(c, id).req, CX, it.custodia, true, RU)); const f = MUD(c, x => benFechar(x, id, IG));
  const lid = f.lotes ? f.lotes[0] : 'L39-131'; const L = LT(c, lid); const lcs = L ? prLcs(c, L) : [];
  ok('U26c2 diferença 120 kg sobre 24.120 kg: Igor recusado pelo teto ("120 kg > alçada de 100 kg (PACK-FRU v3, sintético)"); Ana justifica', ji.erro === '120 kg > alçada de 100 kg (PACK-FRU v3, sintético): decide Ana (gestora). Nada foi alterado.' && !j.erro, [ji, j]);
  ok('U26d fechar: lote L39-133 (mesmo modelo e sequência da Colheita) Em inspeção na INSP-106; genealogia até a carga da O.S. de colheita (LC- herdado para a avaliação do destino)',
     !j.erro && !f.erro && L && L.id === 'L39-133' && L.insp === 'INSP-106' && prSaldos(c, L).q === 'Em inspeção' && L.origem[0].lote === 'L39-131' && lcs.length > 0 && prOrigCampo(c, L).every(x => x.os === 'OS-0505'), [j, f, L && L.id, lcs]);
  ok('U26d2 BEN-REV-08 a ordem do L39-131 (Lagoa Grande) rodou na linha da rota, no Packing (Santa Rita): o lote embalado fica no l8 e continua da Lagoa Grande', L && L.local === 'l8' && L.faz === 'Lagoa Grande' && O(c, id).talhao === 'Packing', L && [L.local, L.faz, O(c, id).talhao]);
  const rr = MUD(c, x => benResultado(x, L.id, 'Conforme', '', MA)); const dd = MUD(c, x => benDecidir(x, L.id, 'Liberar', {}, MA));
  const L2 = () => LT(c, lid);   /* MUD troca os objetos do estado: reler o lote depois de cada comando */
  ok('U26e liberado pela Qualidade: apto no Estoque de produto (prSaldos) e entrada esgotada', prSaldos(c, L2()).q === 'Liberado' && prSaldos(c, L2()).disp === 20000 && prSaldos(c, LT(c, 'L39-131')).esgotado, [rr, dd, prSaldos(c, L2()), prSaldos(c, LT(c, 'L39-131'))]);
  /* carência ao vivo herdada (R-12 da Colheita): aplicação de 10 dias de carência no Pivô 19 em 18/09 → a colheita de 21/09 estava na carência → o lote embalado fica Bloqueado */
  if (typeof carc_bula === 'function' && typeof CARD !== 'undefined') {
    c.ordens['OS-0998'] = { id: 'OS-0998', tipo: 'Pulverização · antracnose', talhao: 'Pivô 19', area: 75.11, etapa: 'Encerradas', versao: 'v1', realizado: 75.11, saldo: 0, resp: 'Wesley',
      ins: [{ p: 'Tebuconazol 200 EC', dose: 1, un: 'L', tot: 75.11 }], req: null, selos: [], ap: [{ d: '05/09', dia: 1, ha: 75.11, st: 'Conferido', sinc: true, origem: 'web' }], reservado: false, osc: {} };
    const Q0 = prSaldos(c, L2()); const b = MUD(c, x => carc_bula(x, 'Tebuconazol 200 EC', 'Mamão', 30)); const Q = prSaldos(c, L2());
    ok('U26f carência herdada pela genealogia (lei): aplicação no Pivô 19 em 05/09 e bula corrigida para 30 dias depois do fechamento → o lote embalado passa a Bloqueado, como o de campo', Q0.q === 'Liberado' && !b.erro && Q.q === 'Bloqueado' && /carência/.test(Q.mot), [Q0.q, b.erro, Q]); }
  else ok('U26f motor de carência carregado no teste', false, 'sem carc_bula/CARD'); }

// ---- U27 · quem age (CTL-3): cada decisão só com o papel; nada é gravado em nome de quem não decidiu ----
{ const c = NOVO(); const a = MUD(c, x => benConcluir(x, 'OB-0110', AN)); MUD(c, x => benConcluir(x, 'OB-0110', IG)); const b = MUD(c, x => benConferir(x, 'OB-0110', IG)); const d = MUD(c, x => benConferir(x, 'OB-0110', RU));
  ok('U27 Ana não conclui (produção); Igor e Rui não conferem (conferência: Paula)', /decisão de Igor/.test(a.erro || '') && /decisão de Paula \(conferência\)/.test(b.erro || '') && /decisão de Paula/.test(d.erro || ''), [a, b, d]); }

// ---- U28 · R-A08 reabrir a execução: motivo obrigatório, só produção; conferência e Concluir caem; repetido é "Já feito" sem gravar ----
{ const c = NOVO(); MUD(c, x => benConcluir(x, 'OB-0110', IG)); MUD(c, x => benConferir(x, 'OB-0110', PA));
  const s0 = MUD(c, x => benReabrir(x, 'OB-0110', '', IG)); const a = MUD(c, x => benReabrir(x, 'OB-0110', 'faltou a classe B da tarde', AN));
  const r = MUD(c, x => benReabrir(x, 'OB-0110', 'faltou a classe B da tarde', IG)); const o = O(c, 'OB-0110'); const ev = o.ben.hist.slice(-2).map(h => h.ev); const n = o.ben.hist.length;
  const rep = MUD(c, x => benReabrir(x, 'OB-0110', 'faltou a classe B da tarde', IG));
  ok('U28 reabrir: sem motivo recusado; Ana (sem papel de produção) recusada; Igor reabre → Em execução, conferência e Concluir caem com linha no histórico; repetido "Já feito" sem gravar',
     /Informe o motivo/.test(s0.erro || '') && /decisão de Igor/.test(a.erro || '') && !r.erro && o.etapa === 'Em execução' && !o.ben.conf && !o.ben.conc
     && JSON.stringify(ev) === '["Caiu: conferência","Execução reaberta"]' && /^Já feito: OB-0110 está em Em execução/.test(rep.erro || '') && O(c, 'OB-0110').ben.hist.length === n, [s0, a, r, ev, rep]); }

// ---- U29 · BEN-D15 e BEN-D14: em processo só entre Iniciar e Concluir; próximo passo do lote de entrada e pendências da faixa, do mesmo estado ----
{ const c = NOVO(); const ep12 = benEmProc(O(c, 'OB-0112')); const pr0 = benPendRec(c); const px = benProxEntrada(c, LT(c, 'L39-131'));
  const nv = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 24120 }] }, IG)); const px2 = benProxEntrada(c, LT(c, 'L39-131')); const pr1 = benPendRec(c);
  ok('U29 OB-0112 (A liberar) com 0 kg em processo; L39-131 aponta "Abrir ordem de beneficiamento" (#nova=L39-131) e, criada a OB-0113, "na OB-0113 (A liberar)"; faixa "1 a pesar" e "1 a liberar · 3 lotes a beneficiar" → "2 a liberar · 2 lotes a beneficiar"',
     ep12 === 0 && px && px.h === 'BEN.dc.html#nova=L39-131' && px2 && /^na OB-0113 \(A liberar\)/.test(px2.t) && px2.h === 'BEN.dc.html#OB-0113'
     && pr0.carga === '1 a pesar' && pr0.ben === '1 a liberar · 3 lotes a beneficiar' && pr1.ben === '2 a liberar · 2 lotes a beneficiar', [ep12, px, px2, pr0, pr1, nv.erro]); }

// ===== Revisão adversarial do BEN-1 (BEN-REV-01..09, 09/10/2026): cada achado com proteção de regressão =====
function OSX(c, id, tal, etapa, ap) { c.ordens[id] = { id, tipo: 'Colheita · semana 39', talhao: tal, area: 0, etapa, versao: 'v1', realizado: 0, saldo: 0, resp: 'Sérgio', ins: [], req: null, selos: [],
  ap: (ap || []).map((a, i) => ({ d: a[0], dia: i + 1, ha: a[1], st: 'Conferido', sinc: true, origem: 'web' })), reservado: false, osc: {} }; const o = c.ordens[id]; o.realizado = o.ap.reduce((s, a) => s + a.ha, 0); return o; }
/* carga do T7 (Santa Rita) recebida no Packing (l8) por uma O.S. de colheita sintética (a semente não tem colheita do T7) */
function T7(c, cond, tk) { if (!c.ordens['OS-0932']) OSX(c, 'OS-0932', 'T7', 'Em execução', [['25/09', 6]]); return MUD(c, x => prReceber(x, { os: 'OS-0932', ticket: tk || 'TK-T7A', bruto: 9400, tara: 3200, cond, dcol: '2026-09-25' })); }

// ---- U30 · BEN-REV-01 · lote de entrada numa ordem liberada: sem decisão da Qualidade (a massa iria a dois destinos); defesa no Fechar ----
{ const c = NOVO(); const L = 'L39-119';
  MUD(c, x => benRetirar(x, 'OB-0112', L, IG)); MUD(c, x => benResultado(x, L, 'Conforme', '', MA)); MUD(c, x => benDecidir(x, L, 'Liberar', {}, MA));
  const n = MUD(c, x => benNova(x, { lotes: [{ lote: L, kg: 3130 }] }, IG)); const d0 = benDecisoes(c, LT(c, L));
  const l = MUD(c, x => benAutorizarLiberar(x, n.id, IG)); const d1 = benDecisoes(c, LT(c, L)); const n0 = c.producao.movs.length;
  const ds = MUD(c, x => benDecidir(x, L, 'Destinar', { motivo: 'indústria de polpa' }, MA)); const bq = MUD(c, x => benDecidir(x, L, 'Bloquear', { motivo: 'suspeita de avaria' }, MA));
  ok('U30a BEN-REV-01 L39-119 liberado e na OB-0113: em A liberar (rascunho) a Qualidade ainda decide (Bloquear, Destinar); liberada a ordem, nenhuma decisão e Destinar/Bloquear recusados sem gravar (3.130 kg no físico)',
     !n.erro && !l.erro && JSON.stringify(d0) === '["Bloquear","Destinar"]' && JSON.stringify(d1) === '[]'
     && ds.erro === 'L39-119 em processo na OB-0113 (Liberadas): decida depois do Fechar, sobre os lotes de saída (nascem Em inspeção). Nada foi gravado.' && /em processo na OB-0113/.test(bq.erro || '') && prFis(c, L) === 3130 && c.producao.movs.length === n0, [n, l, d0, d1, ds, bq]);
  const req = O(c, n.id).req; MUD(c, x => cenEntregar(x, req, CX, 298, 'Igor', RU)); MUD(c, x => benIniciar(x, n.id, IG));
  MUD(c, x => benSaida(x, n.id, { fluxo: 'Produto', classe: 'A', cx: 290, bruto: 3074 }, IG)); MUD(c, x => benSaida(x, n.id, { fluxo: 'Descarte', destino: 'Compostagem', kg: 230 }, IG));
  MUD(c, x => benConcluir(x, n.id, IG)); MUD(c, x => benConferir(x, n.id, PA)); MUD(c, x => cenDevolver(x, req, CX, 8, true, RU));
  /* fixture: massa tirada por fora das regras (movimento gravado direto); o Fechar não pode consumir de novo o que já saiu */
  c.producao.movs.push({ id: 'MP-T30', tipo: 'destinação', lote: L, kg: -3130, d: '2026-09-26', quem: 'fixture' }); const f = MUD(c, x => benFechar(x, n.id, IG));
  ok('U30b defesa no Fechar: entrada com 0 kg para 3.130 kg consumidos → "Fechar recusado: o L39-119 tem 0 kg e a OB-0113 consome 3.130 kg…"; segue Em conferência e nenhum lote nasce',
     f.erro === 'Fechar recusado: o L39-119 tem 0 kg e a OB-0113 consome 3.130 kg (o lote mudou depois da liberação). Nada foi gravado.' && O(c, n.id).etapa === 'Em conferência' && !LT(c, 'L39-133'), f); }

// ---- U31 · BEN-REV-02 · estorno de carga com o lote numa ordem liberada; BEN-REV-09 · carga nova não soma no lote da ordem ----
{ const c = NOVO(); const r = T7(c, 'Íntegra'); const L = r.L.id; const cg = r.g.id;
  const n = MUD(c, x => benNova(x, { lotes: [{ lote: L, kg: 6200 }], cx: 500 }, IG)); const r2 = T7(c, 'Íntegra', 'TK-T7C');
  ok('U31a BEN-REV-09 carga nova do mesmo dia não soma no lote que já está numa ordem (A liberar): vira lote novo; o da ordem continua com 6.200 kg', !n.erro && !r2.erro && r2.L.id !== L && prFis(c, L) === 6200, [n, r2.erro, r2.L && r2.L.id]);
  MUD(c, x => benAutorizarLiberar(x, n.id, IG)); const imp = prEstornoImpede(c, c.producao.cargas[cg]); const e = MUD(c, x => prEstornar(x, cg, 'ticket errado', 'Rui'));
  ok('U31b BEN-REV-02 OB-0113 liberada: estornar a CG-2109 é recusado com o caminho (diferença no balanço, alçada); L39-133 segue com 6.200 kg e a carga Recebida',
     e.erro === 'CG-2109 alimenta o L39-133, em processo na OB-0113 (Liberadas): estorno recusado. Erro de pesagem aparece no balanço da ordem: justifique a diferença na conferência (alçada).' && imp === e.erro && prFis(c, L) === 6200 && c.producao.cargas[cg].st === 'Recebida', [e, imp]);
  const c2 = NOVO(); const q = T7(c2, 'Íntegra'); const n2 = MUD(c2, x => benNova(x, { lotes: [{ lote: q.L.id, kg: 6200 }], cx: 500 }, IG));
  const e2 = MUD(c2, x => prEstornar(x, q.g.id, 'ticket errado', 'Rui')); const l2 = MUD(c2, x => benAutorizarLiberar(x, n2.id, IG));
  ok('U31c em A liberar (rascunho) o estorno passa e a liberação recusa a entrada sem saldo, sem reservar nada', !e2.erro && /L39-133 sem saldo físico/.test(l2.erro || '') && O(c2, n2.id).etapa === 'A liberar' && !O(c2, n2.id).req, [e2, l2]); }

// ---- U32 · BEN-REV-03 · carga com avaria no Packing: a Qualidade libera a entrada e o lote chega ao beneficiamento ----
{ const c = NOVO(); const r = T7(c, 'Com avaria'); const L = r.L.id; const S = prSaldos(c, LT(c, L)); const px = benProxEntrada(c, LT(c, L));
  const ig = MUD(c, x => prLiberarLote(x, L, IG)); const n0 = MUD(c, x => benNova(x, { lotes: [{ lote: L, kg: 6200 }] }, IG));
  ok('U32a BEN-REV-03 avaria no Packing: L39-133 em processo pelo local e entrada em inspeção; o próximo passo é "Liberar lote · Marta (qualidade)"; Igor não libera; a ordem é recusada com a causa e o dono',
     S.q === 'Em processo' && prLibProc(c, LT(c, L)) && px && px.lib && px.t === 'Liberar lote · Marta (qualidade)' && /decisão de Ana \(agrônoma\) ou Marta \(qualidade\)/.test(ig.erro || '') && n0.erro === 'L39-133 em inspeção · Marta (qualidade)', [S.q, px, ig, n0]);
  const lm = MUD(c, x => prLiberarLote(x, L, MA)); const S2 = prSaldos(c, LT(c, L)); const px2 = benProxEntrada(c, LT(c, L));
  ok('U32b Marta libera a entrada: segue em processo (fora do vendável, disponível 0) e abre ordem ("Abrir ordem de beneficiamento · Igor")', !lm.erro && /seguem para o beneficiamento; Igor \(responsável de produção\) abre a ordem/.test(lm.msg) && S2.q === 'Em processo' && S2.disp === 0 && benLotesAptos(c).some(x => x.id === L) && px2 && /^Abrir ordem de beneficiamento/.test(px2.t), [lm, S2.q, px2]);
  const n = MUD(c, x => benNova(x, { lotes: [{ lote: L, kg: 6200 }], cx: 500 }, IG)); const l2 = MUD(c, x => prLiberarLote(x, L, MA));
  ok('U32c a ordem nasce; "Liberar lote" de novo é recusado (já liberado para o beneficiamento)', !n.erro && /já liberado para o beneficiamento/.test(l2.erro || ''), [n, l2]); }

// ---- U33 · BEN-REV-04 · o Reabrir não contorna a alçada da correção (R-F07, R-G06; BEN-D16) ----
{ const c = NOVO(); MUD(c, x => benEstornar(x, 'OB-0110', 'S-03', 'Erro de digitação', '', IG)); MUD(c, x => benConcluir(x, 'OB-0110', IG));
  const rb = MUD(c, x => benReabrir(x, 'OB-0110', 'pesagem refeita', IG)); MUD(c, x => benSaida(x, 'OB-0110', { fluxo: 'Perda identificada', causa: 'Avaria no manuseio', kg: 600, ticket: 'TK-9' }, IG));
  const co = MUD(c, x => benConcluir(x, 'OB-0110', IG)); const o = O(c, 'OB-0110'); const cf = MUD(c, x => benConferir(x, 'OB-0110', PA));
  ok('U33a BEN-REV-04 600 kg (5 %) no Concluir, reabre, lança a perda e conclui com 0 kg → a correção aguarda Ana ("antes de reabrir"); a Paula não confere antes',
     !rb.erro && !co.erro && o.ben.corr && o.ben.corr.pend && /diferença no concluir antes de reabrir 600 kg, 5,00 %/.test(o.ben.corr.msg) && benProx(c, o).acao === 'confirmar' && /decide Ana \(gestora\) antes da conferência/.test(cf.erro || '') && benSelos(c, o).some(s => s.t === 'Corrigido na conferência'), [co, o.ben.corr, cf]);
  const ca = MUD(c, x => benConfirmarCorrecao(x, 'OB-0110', AN)); const cf2 = MUD(c, x => benConferir(x, 'OB-0110', PA));
  ok('U33b Ana confirma e a Paula confere; Ana fica no histórico', !ca.erro && !cf2.erro && O(c, 'OB-0110').ben.hist.some(h => /^Ana/.test(h.quem) && h.ev === 'Correção na conferência confirmada'), [ca, cf2]);
  const c2 = NOVO(); MUD(c2, x => benEstornar(x, 'OB-0110', 'S-03', 'Erro de digitação', '', IG)); MUD(c2, x => benConcluir(x, 'OB-0110', IG)); MUD(c2, x => benReabrir(x, 'OB-0110', 'pesagem refeita', IG));
  MUD(c2, x => benSaida(x, 'OB-0110', { fluxo: 'Descarte', destino: 'Compostagem', kg: 550 }, IG)); MUD(c2, x => benConcluir(x, 'OB-0110', IG)); const o2 = () => O(c2, 'OB-0110');
  const p0 = !!(o2().ben.corr && o2().ben.corr.pend);
  MUD(c2, x => benSaida(x, 'OB-0110', { fluxo: 'Perda identificada', causa: 'Avaria no manuseio', kg: 50, ticket: 'TK-10', motivo: 'perda pesada' }, IG));
  ok('U33c reaberta e concluída com 50 kg (fora da faixa de 12, dentro da alçada de 60): sem confirmação no Concluir; a perda de 50 na conferência leva a 0 e pede Ana pelo |dif₀| de 600 kg de antes de reabrir',
     !p0 && o2().ben.corr && o2().ben.corr.pend && /antes de reabrir 600 kg/.test(o2().ben.corr.msg), [p0, o2().ben.corr]); }

// ---- U34 · BEN-REV-08 · a ordem roda onde a linha da rota está; a fazenda da fruta fica na ordem e nos lotes ----
{ const c = NOVO(); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 24120 }] }, IG)); const o = O(c, n.id);
  ok('U34 BEN-REV-08 L39-131 (Lagoa Grande) entra na ordem da Packing linha 1: local Packing (l8, Santa Rita), fazenda Lagoa Grande, e o histórico diz onde', !n.erro && o.talhao === 'Packing' && o.ben.local === 'l8' && o.ben.faz === 'Lagoa Grande'
     && /fruta da Lagoa Grande processada na Packing linha 1 · Packing \(Santa Rita\)/.test(o.ben.hist[0].det), [n, o.talhao, o.ben.local, o.ben.hist[0].det]); }

// ---- U35 · BEN-REV-09 · a ordem leva o lote inteiro; a liberação confere a entrada de novo ----
{ const c = NOVO(); const p = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 1000 }] }, IG)); const g = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 999999 }] }, IG));
  ok('U35a BEN-REV-09 entrada parcial recusada ("A ordem leva o lote inteiro: L39-131 tem 24.120 kg (informado 1.000 kg)…"); acima do físico, a causa do saldo', p.erro === 'A ordem leva o lote inteiro: L39-131 tem 24.120 kg (informado 1.000 kg). Entrada parcial prenderia o resto do lote até o Fechar.' && g.erro === 'L39-131: 999.999 kg na ordem, 24.120 kg no lote.' && !O(c, 'OB-0113'), [p, g]);
  const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 24120 }] }, IG)); c.producao.movs.push({ id: 'MP-T35', tipo: 'ajuste', lote: 'L39-131', kg: -100, d: '2026-09-26' });   /* fixture: ajuste gravado por fora */
  const im = n.id ? benImpedimentos(c, O(c, n.id)) : [n.erro];
  ok('U35b a liberação confere a entrada de novo: "L39-131: 24.120 kg na ordem, 24.020 kg no lote."', im.some(x => x.t === 'L39-131: 24.120 kg na ordem, 24.020 kg no lote.'), im); }

// ---- U36 · BEN-REV-07 · regras que não tinham proteção (perfil, ordem, fazenda, versão, motivos, fase, tara e classe) ----
{ const c = NOVO(); fechar110(c); MUD(c, x => benResultado(x, 'L39-120', 'Conforme', '', MA)); MUD(c, x => benDecidir(x, 'L39-120', 'Liberar', {}, MA)); const n0 = c.producao.movs.length;
  const di = MUD(c, x => benDecidir(x, 'L26-118', 'Destinar', { motivo: 'x' }, IG)); const dp = MUD(c, x => benDecidir(x, 'L26-118', 'Destinar', { motivo: 'x' }, PA));
  const rc = MUD(c, x => benDecidir(x, 'L39-120', 'Reclassificar', { classe: 'B' }, MA));
  ok('U36a a decisão do lote é da Qualidade ou da agrônoma: Igor e Paula recusados sem gravar; reclassificar sem motivo recusado', /decisão de Ana \(agrônoma\) ou Marta \(qualidade\)/.test(di.erro || '') && /decisão de Ana \(agrônoma\) ou Marta \(qualidade\)/.test(dp.erro || '') && rc.erro === 'Informe o motivo da reclassificação.' && c.producao.movs.length === n0 && LT(c, 'L26-118').q0 === 'Bloqueado' && LT(c, 'L39-120').classe === 'A', [di, dp, rc]);
  const c2 = NOVO(); MUD(c2, x => benConcluir(x, 'OB-0110', IG)); MUD(c2, x => benConferir(x, 'OB-0110', PA)); MUD(c2, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU));
  const fp = MUD(c2, x => benFechar(x, 'OB-0110', PA)); const jd = MUD(c2, x => benJustificar(x, 'OB-0110', 'Erro de medição', 'balança', IG));
  ok('U36b Paula não fecha (produção); justificar com a diferença dentro da faixa é recusado', /decisão de Igor/.test(fp.erro || '') && O(c2, 'OB-0110').etapa === 'Em conferência' && /dentro da faixa/.test(jd.erro || ''), [fp, jd]);
  const c3 = NOVO(); const a = MUD(c3, x => benNova(x, { lotes: [{ lote: 'L39-117', kg: 2960 }] }, IG)); const fz = MUD(c3, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 24120 }, { lote: 'L39-117', kg: 2960 }] }, IG));
  const ini = MUD(c3, x => benIniciar(x, 'OB-0112', IG)); const rv = MUD(c3, x => benRetirar(x, 'OB-0112', 'L39-119', IG, { ver: 0 }));
  ok('U36c lote já numa ordem (L39-117 na OB-0112) não entra em outra; fazendas misturadas recusadas; Iniciar em A liberar recusado; Retirar com a versão velha é conflito, nada gravado',
     a.erro === 'L39-117 já está na OB-0112 (A liberar).' && /^Entradas de fazendas diferentes/.test(fz.erro || '') && /ainda não foi liberada/.test(ini.erro || '') && /A OB-0112 mudou depois que você abriu/.test(rv.erro || '') && O(c3, 'OB-0112').ben.ent.length === 3, [a, fz, ini, rv]);
  const c4 = NOVO(); MUD(c4, x => benEstornar(x, 'OB-0110', 'S-01', 'Pesagem refeita', '', IG)); MUD(c4, x => benEstornar(x, 'OB-0110', 'S-02', 'Pesagem refeita', '', IG));
  const cs = MUD(c4, x => benConcluir(x, 'OB-0110', IG)); const sc = MUD(c4, x => benSaida(x, 'OB-0110', { fluxo: 'Produto', classe: '', cx: 10, bruto: 106 }, IG)); const bt = MUD(c4, x => benSaida(x, 'OB-0110', { fluxo: 'Produto', classe: 'A', cx: 10, bruto: 6 }, IG));
  ok('U36d Concluir sem Produto válido recusado; Produto sem classe e bruto ≤ tara recusados', /Registre ao menos uma saída de Produto com classe/.test(cs.erro || '') && sc.erro === 'Escolha a classe: A ou B.' && bt.erro === 'Bruto 6 kg não passa da tara 6 kg: confira a pesagem.', [cs, sc, bt]);
  const c5 = NOVO(); MUD(c5, x => benEstornar(x, 'OB-0110', 'S-03', 'Erro de digitação', '', IG)); MUD(c5, x => benConcluir(x, 'OB-0110', IG));
  const sm = MUD(c5, x => benSaida(x, 'OB-0110', { fluxo: 'Perda identificada', causa: 'Avaria no manuseio', kg: 600, ticket: 'TK-1' }, IG)); const nc = MUD(c5, x => benResultado(x, 'L39-119', 'Não conforme', '  ', MA));
  ok('U36e correção na conferência sem motivo recusada; resultado "Não conforme" sem observação recusado', sm.erro === 'Correção na conferência: informe o motivo.' && nc.erro === 'Descreva o que não conformou (vai para a decisão).' && !c5.producao.ben.insp['INSP-94'].res['L39-119'], [sm, nc]);
  /* versão esperada nos comandos sem formulário (S4 da revisão): a Paula confere o balanço que viu; o toque repetido continua "Já feito" */
  const c6 = NOVO(); MUD(c6, x => benConcluir(x, 'OB-0110', IG)); const v = O(c6, 'OB-0110').ver;
  MUD(c6, x => benSaida(x, 'OB-0110', { fluxo: 'Perda identificada', causa: 'Avaria no manuseio', kg: 5, ticket: 'TK-2', motivo: 'perda pesada' }, IG));
  const cv = MUD(c6, x => benConferir(x, 'OB-0110', PA, { ver: v })); const ck = MUD(c6, x => benConferir(x, 'OB-0110', PA, { ver: O(c6, 'OB-0110').ver })); const cd = MUD(c6, x => benConferir(x, 'OB-0110', PA, { ver: v }));
  ok('U36f Conferir com a versão que a Paula abriu: o balanço mudou (perda de 5 kg) → conflito, nada gravado; com a versão atual confere; o toque repetido é "Já feito"', /A OB-0110 mudou depois que você abriu/.test(cv.erro || '') && !ck.erro && /^Já feito: balanço conferido/.test(cd.erro || ''), [cv, ck, cd]); }

// ---- U37 · BEN-REV-07 · lote reservado para pedido não entra na ordem (cancelar a reserva antes) ----
{ const c = NOVO(); c.producao.lotes['LX-3'] = Object.assign({}, LT(c, 'L38-131'), { id: 'LX-3', origem: [], abertura: true }); c.producao.movs.push({ id: 'MP-T3', tipo: 'abertura', lote: 'LX-3', kg: 1000, d: '2026-09-25' });
  c.producao.pedidos['PV-T3'] = { id: 'PV-T3', cliente: 'Teste', prod: LT(c, 'LX-3').prod, cultura: 'Mamão Formosa', classe: '', saf: '', tipo: 'pronta', janela: '—', qtd: 500, dest: 'MI-BR' };
  const S = prSaldos(c, LT(c, 'LX-3')); const rs = MUD(c, x => prReservar(x, { pedido: 'PV-T3', lote: 'LX-3', kg: 500 })); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'LX-3', kg: 1000 }] }, IG));
  ok('U37 lote reservado para pedido não entra na ordem ("LX-3 reservado para pedido: cancele a reserva antes de beneficiar")', S.q === 'Liberado' && !rs.erro && n.erro === 'LX-3 reservado para pedido: cancele a reserva antes de beneficiar.', [S.q, rs, n]); }

// ---- U38 · S4 da revisão · a recusa do Liberar lote diz de onde vem a inspeção (fruta de campo não é "lote do beneficiamento") ----
{ const c = NOVO(); const a = MUD(c, x => prLiberarLote(x, 'L39-119', MA)); fechar110(c); const b = MUD(c, x => prLiberarLote(x, 'L39-120', MA));
  ok('U38 S4 Liberar lote: o L39-119 (fruta de campo, INSP-94) "tem a inspeção INSP-94"; o L39-120 "é lote do beneficiamento (OB-0110)" e fechar não libera',
     a.erro === 'L39-119 tem a inspeção INSP-94: registre o resultado da inspeção INSP-94 e a decisão.' && /^L39-120 é lote do beneficiamento \(OB-0110\): registre o resultado da inspeção INSP-\d+ e a decisão \(fechar o processo não libera\)\.$/.test(b.erro || ''), [a, b]); }

// ===== Integração BEN na branch única (09/10/2026): achados dos revisores, cada um com proteção de regressão =====
// ---- U39 · caixas da ordem nova dentro do livre no Estoque: o roteiro do proprietário (L39-132 com o valor inicial) libera ----
{ const c = NOVO(); const r = benRota('PACK-FRU|3'); const pd = benCaixasPadrao(c, 12300, r);
  ok('U39a L39-132 (12.300 kg): sugestão 1.169 un, 540 livres no Estoque (CX26-01), valor inicial 540', pd.sug === 1169 && pd.livre === 540 && pd.cx === 540 && benCaixasLivres(c) === 540, pd);
  const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG)); const o = O(c, n.id || 'OB-0113') || { ins: [{}], ben: { hist: [{}] } };
  ok('U39b criar sem informar caixas usa o valor inicial: 540 un, o histórico diz a sugestão e o livre, sem aviso de impedimento',
     !n.erro && o.ins[0].tot === 540 && /540 un de caixa \(sugestão 1169; 540 un livres no Estoque\)/.test(o.ben.hist[0].det) && !/Atenção/.test(n.msg), [n, o.ins, o.ben.hist]);
  const im = n.id ? benImpedimentos(c, o) : ['sem ordem']; const l = MUD(c, x => benAutorizarLiberar(x, n.id, IG));
  const o2 = O(c, n.id) || {}; ok('U39c a ordem criada com o valor inicial libera: sem impedimento, REQ-041 com 540 un, L39-132 preso à ordem', !im.length && !l.erro && o2.etapa === 'Liberadas' && o2.req === 'REQ-041' && REQ(c, 'REQ-041').solicitado === 540 && LT(c, 'L39-132').ordem === n.id, [im, l]);
  const c2 = NOVO(); const a = MUD(c2, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }], cx: 1169 }, IG));
  ok('U39d acima do livre a ordem nasce com o aviso de que a liberação fica impedida e quem resolve', !a.erro && /Atenção: 540 un livres no Estoque para 1\.169 un: a liberação fica impedida até o Estoque ter as caixas \(Rui \(almoxarife\) ou Paula \(almoxarife\)\)\./.test(a.msg), a);
  const c3 = NOVO(); MUD(c3, x => cenReceber(x, CX, 'CX26-02', 3000, 'un', 'Packing', '—', 'NF-90011', true, RU)); const p3 = benCaixasPadrao(c3, 12300, r);
  const c4 = NOVO(); c4.lotes[CX + '|CX26-01'].reservado = c4.lotes[CX + '|CX26-01'].fisico; const p4 = benCaixasPadrao(c4, 12300, r);
  ok('U39e com caixas suficientes vale a sugestão (3.000 un recebidas); sem caixa livre fica a sugestão (a liberação mostra a falta)', p3.cx === 1169 && p3.livre === 3000 && p4.livre === 0 && p4.cx === 1169, [p3, p4]); }

print(JSON.stringify(R));
