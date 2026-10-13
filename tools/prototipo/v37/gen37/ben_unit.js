// Testes puros do Beneficiamento BEN-1 (docs/beneficiamento/ESPECIFICACAO.md §10.3, com a caixa de 10 kg do DECISOES §12) · node, sem navegador.
// Carregado depois de: perfis (g2lib) + CEN0 + cenario.js + PRDC + producao.js + BENC + ben.js (+ núcleo da O.S. com CARD e o motor de carência).
// Cada verificação vira uma linha do JSON final. Quem age é o perfil (Igor produção, Paula conferência, Ana gestora, Marta qualidade, Rui almoxarife).
const R = []; function ok(n, c, info) { R.push({ n, ok: !!c, info: c ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 700) }); }
function MUD(c, fn) { const x = cenClone(c); try { const r = fn(x) || {}; if (!r.nada) { Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); } return r; } catch (e) { return { erro: String(e.message || e) }; } }
const NOVO = () => cenClone(CEN0);
const IG = 'Igor', PA = 'Paula', AN = 'Ana', MA = 'Marta', RU = 'Rui', CX = BENC.cx.item;   // integração V56: reservas com ator (Comercial CE-10: comercial ou gestor), aqui a Ana
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
  const r1 = MUD(c3, x => prReservar(x, { ator: AN, pedido: 'PV-T9', lote: 'L39-120', kg: 1000, chave: 'W-RS-T9a' })); const r2 = MUD(c3, x => prReservar(x, { ator: AN, pedido: 'PV-T9', lote: 'L39-120', kg: 500, chave: 'W-RS-T9b' }));
  ok('U14e reservar 1.000 e depois 500 para um pedido de 1.000 kg: a segunda é recusada pela falta (0 kg); disponível 8.600', !r1.erro && /Acima da falta do PV-T9: 0 kg/.test(r2.erro || '') && prSaldos(c3, LT(c3, 'L39-120')).disp === 8600, [r1.erro, r2.erro]); }

// ---- U15 · R-E04, R-E05 · K21 reserva do PV-031 (prReservar, a mesma da Colheita) ----
{ const c = NOVO(); fechar110(c);
  const ei = MUD(c, x => prReservar(x, { ator: AN, pedido: 'PV-031', lote: 'L39-120', kg: 9600 }));
  ok('U15a K21 L39-120 Em inspeção: reserva recusada', /L39-120 não está apto \(Em inspeção/.test(ei.erro || ''), ei);
  MUD(c, x => benResultado(x, 'L39-120', 'Conforme', '', MA)); MUD(c, x => benDecidir(x, 'L39-120', 'Liberar', {}, MA));
  const S = prSaldos(c, LT(c, 'L39-120')); const f0 = prFalta(c, c.producao.pedidos['PV-031']);
  const ac = MUD(c, x => prReservar(x, { ator: AN, pedido: 'PV-031', lote: 'L39-120', kg: 10000 }));
  ok('U15b K21 liberado: disponível 9.600, falta 10.000 → sugestão mín = 9.600; 10.000 recusado ("Acima do disponível do L39-120: 9.600 kg.")', S.disp === 9600 && f0 === 10000 && ac.erro === 'Acima do disponível do L39-120: 9.600 kg.', [S.disp, f0, ac]);
  const rs = MUD(c, x => prReservar(x, { ator: AN, pedido: 'PV-031', lote: 'L39-120', kg: 9600 }));
  ok('U15c K21 reservado 9.600; falta 400 kg; disponível 0; RS-0002 (a RS-0001 é da soja)', !rs.erro && rs.rs.id === 'RS-0002' && prFalta(c, c.producao.pedidos['PV-031']) === 400 && prSaldos(c, LT(c, 'L39-120')).disp === 0, rs);
  MUD(c, x => benResultado(x, 'L39-121', 'Conforme', '', MA)); MUD(c, x => benDecidir(x, 'L39-121', 'Liberar', {}, MA));
  const cb = MUD(c, x => prReservar(x, { ator: AN, pedido: 'PV-031', lote: 'L39-121', kg: 100 }));
  c.producao.pedidos['PV-T0'] = Object.assign({}, c.producao.pedidos['PV-031'], { id: 'PV-T0', classe: '' }); const cv = MUD(c, x => prReservar(x, { ator: AN, pedido: 'PV-T0', lote: 'L39-121', kg: 100 }));
  ok('U15d classe diferente recusada ("Classe B ≠ A do PV-031"); classe vazia no pedido recusada ("Classe não informada")', cb.erro === 'Classe B ≠ A do PV-031.' && /^Classe não informada \(PV-T0\)/.test(cv.erro || ''), [cb, cv]); }

// ---- U16 · R-E03, R-E06 · K22, K23, K24 bloqueio, reclassificação e cancelamento com reserva ----
{ const c = NOVO(); fechar110(c); MUD(c, x => benResultado(x, 'L39-120', 'Conforme', '', MA)); MUD(c, x => benDecidir(x, 'L39-120', 'Liberar', {}, MA));
  MUD(c, x => prReservar(x, { ator: AN, pedido: 'PV-031', lote: 'L39-120', kg: 9600 })); const ped = () => prSitPed(c, c.producao.pedidos['PV-031']);
  const bs = MUD(c, x => benDecidir(x, 'L39-120', 'Bloquear', {}, MA)); const bl = MUD(c, x => benDecidir(x, 'L39-120', 'Bloquear', { motivo: 'reclamação de transporte' }, MA));
  ok('U16a K22 bloquear exige motivo; bloqueado: RS-0002 continua Ativa com expedição impedida; PV-031 Em risco; falta 400; disponível 0', /motivo do bloqueio/.test(bs.erro || '') && !bl.erro && c.producao.reservas['RS-0002'].st === 'Ativa' && ped().t === 'Em risco' && prFalta(c, c.producao.pedidos['PV-031']) === 400 && prSaldos(c, LT(c, 'L39-120')).disp === 0, [bs, bl.erro, ped().t]);
  MUD(c, x => benDecidir(x, 'L39-120', 'Liberar', {}, MA));
  ok('U16b K22 liberar de novo: o impedimento some sem reativar nada; nova reserva recusada (disponível 0)', ped().t === 'Parcial' && /Acima do disponível do L39-120: 0 kg/.test(MUD(c, x => prReservar(x, { ator: AN, pedido: 'PV-031', lote: 'L39-120', kg: 1 })).erro || ''), ped().t);
  const f0 = prFis(c, 'L39-120'); const tot0 = prSoma(Object.values(c.producao.lotes).filter(L => L.cultura === 'Mamão Formosa').map(L => prFis(c, L.id)));
  const rc = MUD(c, x => benDecidir(x, 'L39-120', 'Reclassificar', { classe: 'B', motivo: 'calibre menor na reinspeção' }, MA));
  const tot1 = prSoma(Object.values(c.producao.lotes).filter(L => L.cultura === 'Mamão Formosa').map(L => prFis(c, L.id)));
  ok('U16c K23 reclassificar A → B: físico 9.600 antes e depois; Σ do mamão igual; RS-0002 Ativa com expedição impedida (classe B ≠ A); PV-031 Em risco', !rc.erro && f0 === 9600 && prFis(c, 'L39-120') === 9600 && tot0 === tot1 && LT(c, 'L39-120').classe === 'B' && ped().t === 'Em risco' && /expedição impedida/.test(rc.msg), [rc, ped().t]);
  const cs = MUD(c, x => prCancelarReserva(x, 'RS-0002', '', AN)); const cc = MUD(c, x => prCancelarReserva(x, 'RS-0002', 'cliente quer só classe A', AN));   /* integração V56: o Comercial exige quem age na reserva e no cancelamento (CE-10); Ana é gestora */
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
  ok('U23a K17 saída antes de iniciar recusada; depois da entrega de 584: 585 cx → "Caixas acima da custódia: 584 un, e a REQ-041 já foi toda entregue. Peça mais caixas na ordem"; 500 cx baixam a custódia com MV consumo',
     /Registre saídas só em Em execução/.test(sem.erro || '') && a.erro === 'Caixas acima da custódia: 584 un, e a REQ-041 já foi toda entregue. Peça mais caixas na ordem ("Pedir mais caixas"); Rui (almoxarife) ou Paula (almoxarife) entrega no balcão.' && !b.erro && REQ(c, 'REQ-041').custodia === 84 && c.movs[n0].tipo === 'consumo' && c.movs[n0].det === CX + ' 500', [sem, a, b.erro]);
  ok('U23b a entrega no balcão fica confirmada ao iniciar (sem "aguardando confirmação no app" para a ordem de processo)', REQ(c, 'REQ-041').confirmado === 'balcao', REQ(c, 'REQ-041'));
  const av = MUD(c, x => benSaida(x, 'OB-0112', { fluxo: 'Produto', classe: 'B', cx: 80, bruto: 948 }, IG));
  ok('U23c K18 líquido por caixa fora de ±5 % gera aviso, não trava (900 kg em 80 cx = 11,25 kg/cx, +12,5 %)', !av.erro && /11,25 kg por caixa contra 10 kg \(\+12,50 %\)/.test(av.msg), av); }

// ---- U24 · K31 inspeção nova pela sequência única (INSP-105 é a maior da Manutenção) ----
{ const c = NOVO(); const x = cenClone(c); ok('U24 primeira inspeção gerada no cenário limpo: INSP-106', benInspId(x) === 'INSP-106', benInspId(cenClone(c))); }

// ---- U25 · R-A03, R-A05 · K06, K07, K08 impedimentos, retirar entrada e liberar ----
{ const c = NOVO(); const im = benImpedimentos(c, O(c, 'OB-0112'));
  ok('U25a K06 duas causas juntas, cada uma com dono e atalho: "L39-119 em inspeção (INSP-94) · Marta (qualidade)" e "…: 540 un disponíveis para 881 un · Estoque" (I4: devolução da OB-0110)',
     im.length === 2 && im[0].t === 'L39-119 em inspeção (INSP-94) · Marta (qualidade)' && im[1].t === CX + ': 540 un disponíveis para 881 un · Estoque' && /OB-0110 tem sobra de 60 un em custódia/.test(im[1].link.why), im);
  const r0 = MUD(c, x => benAutorizarLiberar(x, 'OB-0112', IG)); const an = MUD(c, x => benAutorizarLiberar(x, 'OB-0112', AN));
  ok('U25b liberar com causas: recusa com as duas e nada gravado; Ana não autoriza (decisão do responsável de produção)', /^Liberação recusada · 2 causas/.test(r0.erro || '') && O(c, 'OB-0112').etapa === 'A liberar' && /decisão de Igor \(responsável de produção\)/.test(an.erro || ''), [r0, an]);
  const rt = MUD(c, x => benRetirar(x, 'OB-0112', 'L39-119', IG)); const im2 = benImpedimentos(c, O(c, 'OB-0112'));
  ok('U25c K07 retirar o L39-119: v2, 6.140 kg, 584 un (sugestão acompanha); ainda recusa 540 de 584 com a I4', !rt.erro && O(c, 'OB-0112').versao === 'v2' && benEntrada(O(c, 'OB-0112')) === 6140 && O(c, 'OB-0112').ins[0].tot === 584 && im2.length === 1 && /540 un disponíveis para 584 un/.test(im2[0].t) && /devolução da OB-0110/.test(im2[0].link.t), [rt, im2]);
  const c2 = NOVO(); MUD(c2, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)); const im3 = benImpedimentos(c2, O(c2, 'OB-0112'));
  /* rodada 1 da integração (BEN-D23): sem sobra em custódia, a saída da falta é a NF 7731 de caixas a conferir no Estoque (antes: "Ver saldo", sem saída) */
  ok('U25d K07 depois da devolução e sem retirar: as duas causas, agora "600 un disponíveis para 881 un", e a saída é conferir a NF 7731 (sem sobra em custódia)', im3.length === 2 && /600 un disponíveis para 881 un/.test(im3[1].t) && im3[1].link.t === 'Conferir a NF 7731 das caixas no Estoque' && /^Faltam 281 un\. A NF 7731/.test(im3[1].link.why) && !/custódia/.test(im3[1].link.why), im3);
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
     !rb.erro && !co.erro && o.ben.corr && o.ben.corr.pend && /diferença no envio para conferência antes de reabrir 600 kg, 5,00 %/.test(o.ben.corr.msg) && benProx(c, o).acao === 'confirmar' && /decide Ana \(gestora\) antes da conferência/.test(cf.erro || '') && benSelos(c, o).some(s => s.t === 'Corrigido na conferência'), [co, o.ben.corr, cf]);
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
  const S = prSaldos(c, LT(c, 'LX-3')); const rs = MUD(c, x => prReservar(x, { ator: AN, pedido: 'PV-T3', lote: 'LX-3', kg: 500 })); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'LX-3', kg: 1000 }] }, IG));
  ok('U37 lote reservado para pedido não entra na ordem ("LX-3 reservado para pedido: cancele a reserva antes de beneficiar")', S.q === 'Liberado' && !rs.erro && n.erro === 'LX-3 reservado para pedido: cancele a reserva antes de beneficiar.', [S.q, rs, n]); }

// ---- U38 · S4 da revisão · a recusa do Liberar lote diz de onde vem a inspeção (fruta de campo não é "lote do beneficiamento") ----
{ const c = NOVO(); const a = MUD(c, x => prLiberarLote(x, 'L39-119', MA)); fechar110(c); const b = MUD(c, x => prLiberarLote(x, 'L39-120', MA));
  ok('U38 S4 Liberar lote: o L39-119 (fruta de campo, INSP-94) "tem a inspeção INSP-94"; o L39-120 "é lote do beneficiamento (OB-0110)" e fechar não libera',
     a.erro === 'L39-119 tem a inspeção INSP-94: registre o resultado da inspeção INSP-94 e a decisão.' && /^L39-120 é lote do beneficiamento \(OB-0110\): registre o resultado da inspeção INSP-\d+ e a decisão \(fechar o processo não libera\)\.$/.test(b.erro || ''), [a, b]); }

// ===== Integração BEN na branch única (09/10/2026): achados dos revisores, cada um com proteção de regressão =====
// ---- U39 · caixas da ordem nova = a necessidade da rota (rodada 1 da integração, S2 do bc0e76f): a falta de caixa aparece como impedimento
//      com recuperação real (NF de caixas a conferir no Estoque); recebida a nota, a ordem libera e o balanço fecha os 12.300 kg sem perda fictícia ----
/* Rui confere a NF 7731 no Estoque: o mesmo cenReceber do estReceber (Confira recebimentos), com a conferência gravada no movimento */
/* livre de caixas: o total dos lotes elegíveis (rodada 3, BEN-D34); no código anterior, o lote de maior livre */
const LIVRE = c => typeof benLivreCx === 'function' ? benLivreCx(c) : benCaixasLivres(c);
function RECEBE_NF(c, conf) { const r = MUD(c, x => { const n0 = x.movs.length; const m = cenReceber(x, CX, 'CX26-02', conf, 'un', 'Packing', '—', 'NF 7731', true, RU);
  x.movs[n0].estRec = { id: 'r7731', nf: 'NF 7731', ped: 'PC-096 · ' + CX + ' · Embalagens Açu', conf, apto: conf, quar: 0, lote: 'CX26-02' }; return m; }); return r; }
{ const c = NOVO(); const r = benRota('PACK-FRU|3'); const pd = benCaixasPadrao(c, 12300, r);
  ok('U39a L39-132 (12.300 kg): o valor inicial é a necessidade da rota, 1.169 un, mesmo com só 540 livres no Estoque (CX26-01)', pd.sug === 1169 && pd.livre === 540 && pd.cx === 1169 && LIVRE(c) === 540, pd);
  const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG)); const o = O(c, n.id || 'OB-0113') || { ins: [{}], ben: { hist: [{}] } };
  ok('U39b criar sem informar caixas: 1.169 un (sugestão confirmada) e o aviso diz que a liberação fica impedida até o Estoque receber as caixas, com a NF 7731 e quem confere',
     !n.erro && o.ins[0].tot === 1169 && /1\.169 un de caixa \(sugestão confirmada\)/.test(o.ben.hist[0].det)
     && /Atenção: 540 un livres no Estoque para 1\.169 un: a liberação fica impedida até o Estoque receber as caixas \(NF 7731 do PC-096, 1\.200 un a conferir · Rui \(almoxarife\) ou Paula \(almoxarife\)\)\./.test(n.msg || ''), [n, o.ins, o.ben.hist]);
  const im = n.id ? benImpedimentos(c, o) : []; const x = im.find(y => y.cx) || {}; const r0 = c.rev || 0; const l = MUD(c, y => benAutorizarLiberar(y, n.id, IG));
  ok('U39c impedimento das caixas com quem resolve e a recuperação real (conferir a NF 7731 no Estoque); a liberação é recusada e nada é gravado',
     x.t === CX + ': 540 un disponíveis para 1.169 un · Estoque' && x.dono === 'Rui (almoxarife) ou Paula (almoxarife)' && x.link && x.link.t === 'Conferir a NF 7731 das caixas no Estoque' && x.link.h === 'EST.dc.html'
     && /Faltam 629 un\. A NF 7731 \(PC-096 · Embalagens Açu\) traz até 1\.200 un: Rui \(almoxarife\) ou Paula \(almoxarife\) confere em Estoque › Confira recebimentos\./.test(x.link.why || '')
     && /540 un disponíveis para 1\.169 un/.test(l.erro || '') && O(c, n.id).etapa === 'A liberar' && !O(c, n.id).req && (c.rev || 0) === r0, [x, l]);
  const rc = RECEBE_NF(c, 1200); const im2 = benImpedimentos(c, O(c, n.id)); const l2 = MUD(c, y => benAutorizarLiberar(y, n.id, IG)); const o2 = O(c, n.id) || {};
  ok('U39d recebida a NF 7731 (1.200 un no CX26-02): sem impedimento; a ordem libera com a necessidade inteira (REQ-041 1.169 un do CX26-02) e o L39-132 preso à ordem',
     !rc.erro && !im2.length && !l2.erro && o2.etapa === 'Liberadas' && o2.req === 'REQ-041' && REQ(c, 'REQ-041').solicitado === 1169 && REQ(c, 'REQ-041').lote === 'CX26-02' && LT(c, 'L39-132').ordem === n.id, [rc, im2, l2]);
  const id = n.id; const st = [MUD(c, y => cenEntregar(y, 'REQ-041', CX, 1169, null, RU)), MUD(c, y => benIniciar(y, id, IG)),
    MUD(c, y => benSaida(y, id, { fluxo: 'Produto', classe: 'A', cx: 1000, bruto: 10600 }, IG)), MUD(c, y => benSaida(y, id, { fluxo: 'Produto', classe: 'B', cx: 169, bruto: 1791.4 }, IG)),
    MUD(c, y => benSaida(y, id, { fluxo: 'Descarte', destino: 'Compostagem', kg: 610 }, IG)), MUD(c, y => benConcluir(y, id, IG)), MUD(c, y => benConferir(y, id, PA)), MUD(c, y => benFechar(y, id, IG))];
  const of = O(c, id); const b = benBal(of); const nv = Object.values(c.producao.lotes).filter(L => L.benef === id);
  ok('U39e execução e balanço fecham os 12.300 kg: A 10.000 + B 1.690 + descarte 610, diferença 0, sem justificativa nem perda; custódia 0; Encerradas; L39-132 esgotado',
     st.every(y => !y.erro) && of.etapa === 'Encerradas' && b.dif === 0 && b.proc === 12300 && b.prod === 11690 && b.desc === 610 && b.perda === 0 && !(of.ben.just || []).length
     && REQ(c, 'REQ-041').custodia === 0 && REQ(c, 'REQ-041').consumido === 1169 && prFis(c, 'L39-132') === 0 && prSoma(nv.map(L => prFis(c, L.id))) === 11690, [st.map(y => y.erro || ''), b, REQ(c, 'REQ-041')]);
  const c4 = NOVO(); c4.lotes[CX + '|CX26-01'].reservado = c4.lotes[CX + '|CX26-01'].fisico; const p4 = benCaixasPadrao(c4, 12300, r);
  const c5 = NOVO(); RECEBE_NF(c5, 1200); MUD(c5, y => cenDevolver(y, 'REQ-030', CX, 60, true, RU)); const n5 = MUD(c5, y => benNova(y, { lotes: [{ lote: 'L39-131', kg: 24120 }] }, IG)); const x5 = benImpedimentos(c5, O(c5, n5.id)).find(y => y.cx) || {};
  ok('U39f sem caixa livre a necessidade continua inteira; com a NF já conferida e sem sobra em custódia, a falta (2.292 para 1.800 em dois lotes, rodada 3) diz que a compra de caixas é do BEN-2 e que a ordem pode ser cancelada',
     p4.livre === 0 && p4.cx === 1169 && n5.id && O(c5, n5.id).ins[0].tot === 2292 && x5.link && x5.link.t === 'Ver saldo de caixas no Estoque'
     && x5.t === CX + ': 1.800 un disponíveis para 2.292 un · Estoque' && /Faltam 492 un e não há nota de caixas a conferir nem sobra em custódia: a compra de caixas entra no BEN-2\. Sem caixa, Cancelar a ordem \(nada foi reservado\)\./.test(x5.link.why || ''), [p4, n5, x5]); }

// ---- U40 · BEN-D22 · ordem em A liberar que não libera tem saída: Cancelar a ordem (motivo; rascunho, nada reservado) ----
{ const c = NOVO(); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }], cx: 1169 }, IG)); const id = n.id || 'OB-0113';
  const l = MUD(c, x => benAutorizarLiberar(x, id, IG)); const r0 = c.rev || 0;
  const sm = MUD(c, x => benCancelar(x, id, '  ', IG, { chave: 'W-BNC-T1' })); const pa = MUD(c, x => benCancelar(x, id, 'caixas insuficientes', PA)); const vv = MUD(c, x => benCancelar(x, id, 'caixas insuficientes', IG, { ver: 0 }));
  ok('U40a 1.169 caixas: liberação recusada; cancelar sem motivo, com o perfil da conferência ou com a versão velha é recusado e nada muda',
     /540 un disponíveis para 1\.169 un/.test(l.erro || '') && sm.erro === 'Informe o motivo do cancelamento.' && /^Cancelar a OB-0113: decisão de Ana \(gestora\) ou Igor \(responsável de produção\)\. Nada foi alterado\.$/.test(pa.erro || '') && /A OB-0113 mudou depois que você abriu/.test(vv.erro || '') && O(c, id).etapa === 'A liberar' && (c.rev || 0) === r0, [l, sm, pa, vv]);
  const k = { chave: 'W-BNC-T2', ver: O(c, id).ver }; const cc = MUD(c, x => benCancelar(x, id, 'caixas insuficientes', IG, k)); const rp = MUD(c, x => benCancelar(x, id, 'caixas insuficientes', IG, k)); const r2 = MUD(c, x => benCancelar(x, id, 'outro', IG));
  const o = O(c, id); const h = o.ben.hist[o.ben.hist.length - 1];
  ok('U40b Igor cancela com motivo: Canceladas, quem e quando gravados, uma linha no histórico; nada reservado (sem REQ) e o L39-132 sem ordem; o toque repetido é "Já feito" sem gravar',
     !cc.erro && o.etapa === 'Canceladas' && o.ben.canc.quem === 'Igor (responsável de produção)' && o.ben.canc.motivo === 'caixas insuficientes' && /^\d{4}-\d\d-\d\d \d\d:\d\d$/.test(o.ben.canc.em) && /^Ordem cancelada · v1$/.test(h.ev)
     && !o.req && !LT(c, 'L39-132').ordem && rp.nada && /^Já feito/.test(rp.msg || '') && r2.erro === 'Já feito: OB-0113 cancelada.' && o.ben.hist.filter(x => /cancelada/.test(x.ev)).length === 1, [cc, rp, r2, o.ben.canc, h]);
  const ap = benLotesAptos(c).map(L => L.id); const p = benProx(c, o); const ss = benSelos(c, Object.assign({}, o, { ben: Object.assign({}, o.ben, { fim: '2026-01-01' }) }));
  const et = benEtapas(c, o).find(e => e.nome === 'Recepção'); const pr = benPendRec(c);
  ok('U40c cancelada: o L39-132 volta aos aptos; sem passo (acao null) com o motivo à vista; nunca "Atrasada"; Recepção não cumprida; a faixa não conta a cancelada',
     ap.indexOf('L39-132') >= 0 && p.acao === null && p.t === 'Cancelada: caixas insuficientes' && !ss.some(x => x.t === 'Atrasada') && et && et.sit !== 'Cumprida' && /^1 a liberar/.test(pr.ben), [ap, p, ss, et, pr]);
  const n2 = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG)); const l1 = MUD(c, x => benAutorizarLiberar(x, n2.id, IG)); RECEBE_NF(c, 1200); const l2 = MUD(c, x => benAutorizarLiberar(x, n2.id, IG));
  ok('U40d a ordem nova do L39-132 (OB-0114) vem com a necessidade (1.169 un): impedida até a NF 7731 ser conferida; depois libera', n2.id === 'OB-0114' && O(c, 'OB-0114').ins[0].tot === 1169 && /540 un disponíveis para 1\.169 un/.test(l1.erro || '') && !l2.erro && O(c, 'OB-0114').etapa === 'Liberadas' && LT(c, 'L39-132').ordem === 'OB-0114', [n2, l1, l2]);
  const fx = MUD(c, x => benCancelar(x, 'OB-0110', 'teste', IG)); const fl = MUD(c, x => benCancelar(x, 'OB-0114', 'teste', IG)); const an = MUD(c, x => benCancelar(x, 'OB-0112', 'rota trocada', AN));
  ok('U40e só em A liberar: OB-0110 (Em execução) e OB-0114 (Liberadas) recusadas ("o cancelamento entra no BEN-6"); a OB-0112 (A liberar) a Ana (gestora) cancela',
     /^Cancele só em A liberar \(OB-0110 está em Em execução\)/.test(fx.erro || '') && /^Cancele só em A liberar \(OB-0114 está em Liberadas\)/.test(fl.erro || '') && !an.erro && O(c, 'OB-0112').etapa === 'Canceladas' && O(c, 'OB-0112').ben.canc.quem === 'Ana (gestora)', [fx, fl, an]); }
{ /* carga estornada com a ordem em A liberar (BEN-D19 deixa: rascunho): a entrada não confere; uma entrada só, sem Retirar; Cancelar solta o lote */
  const c = NOVO(); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 24120 }], cx: 500 }, IG)); const e = MUD(c, x => prEstornar(x, 'CG-2106', 'ticket trocado na balança', 'Lúcia'));
  const im = benImpedimentos(c, O(c, n.id)); const pr = benProx(c, O(c, n.id));
  ok('U40f CG-2106 estornada com a OB-0113 em A liberar: impedimento "24.120 kg na ordem, 12.180 kg no lote" sem Retirar, e o próximo passo oferece cancelar',
     !e.erro && im.some(x => x.t === 'L39-131: 24.120 kg na ordem, 12.180 kg no lote.' && !x.ret) && /Sem como resolver: Cancelar a ordem \(nada foi reservado\) e abrir outra/.test(pr.nota || ''), [e, im, pr]);
  MUD(c, x => benCancelar(x, n.id, 'carga CG-2106 estornada', IG)); const n2 = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 12180 }] }, IG));
  ok('U40g cancelada a ordem, o L39-131 abre outra com o saldo de agora (12.180 kg)', O(c, n.id).etapa === 'Canceladas' && !n2.erro && benEntrada(O(c, n2.id)) === 12180, [n2]); }

// ---- U41 · rodada 1 (S3): falta de caixa durante a execução tem saída pelo mecanismo de requisição existente: complemento da mesma ordem
//      (Pedir mais caixas), com recibo, reserva no Estoque, entrega no balcão e custódia; sem perda fictícia ----
/* OB-0113 do L39-132 liberada com a NF 7731 conferida, entregue (1.169 un) e iniciada */
/* custódia somada das linhas de caixa da ordem e o texto por linha (guardas: o teste roda também no código anterior à linha por lote) */
function CUST(c, o) { return typeof benCxTot === 'function' ? benCxTot(c, o).cust : NaN; }
function CUSTX(c, o) { return typeof benCustTxt === 'function' ? benCustTxt(c, o) : ''; }
function OB113(c) { const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG)); RECEBE_NF(c, 1200); MUD(c, x => benAutorizarLiberar(x, n.id, IG));
  MUD(c, x => cenEntregar(x, 'REQ-041', CX, 1169, null, RU)); MUD(c, x => benIniciar(x, n.id, IG)); return n.id; }
{ const c = NOVO(); const id = OB113(c);
  const a = MUD(c, x => benSaida(x, id, { fluxo: 'Produto', classe: 'A', cx: 1100, bruto: 11660 }, IG)); const b = MUD(c, x => benSaida(x, id, { fluxo: 'Produto', classe: 'B', cx: 69, bruto: 731.4 }, IG));
  const f = MUD(c, x => benSaida(x, id, { fluxo: 'Produto', classe: 'B', cx: 20, bruto: 212 }, IG));
  ok('U41a fruta rendeu mais: com as 1.169 caixas usadas, mais 20 cx de B são recusadas com a saída escrita (Pedir mais caixas na ordem; quem entrega)',
     !a.erro && !b.erro && f.erro === 'Caixas acima da custódia: 0 un, e a REQ-041 já foi toda entregue. Peça mais caixas na ordem ("Pedir mais caixas"); Rui (almoxarife) ou Paula (almoxarife) entrega no balcão.', [a, b, f]);
  const r0 = c.rev || 0; const pa = MUD(c, x => benComplementar(x, id, 20, PA, { chave: 'W-BNX-T0' })); const z = MUD(c, x => benComplementar(x, id, 0, IG, { chave: 'W-BNX-T1' }));
  const fr = MUD(c, x => benComplementar(x, id, 1.5, IG, { chave: 'W-BNX-T2' })); const vv = MUD(c, x => benComplementar(x, id, 20, IG, { chave: 'W-BNX-T3', ver: 1 }));
  ok('U41b pedir caixas: perfil sem papel, 0, fração e versão antiga recusados sem gravar', /decisão de Igor \(responsável de produção\)/.test(pa.erro || '') && /número inteiro de unidades \(ao menos 1\)/.test(z.erro || '') && /número inteiro/.test(fr.erro || '')
     && /mudou depois que você abriu/.test(vv.erro || '') && (c.rev || 0) === r0, [pa, z, fr, vv]);
  const k = { chave: 'W-BNX-T4', ver: O(c, id).ver }; const l0 = c.lotes[CX + '|CX26-02'].reservado; const cp = MUD(c, x => benComplementar(x, id, 20, IG, k)); const rp = MUD(c, x => benComplementar(x, id, 20, IG, k));
  const it = REQ(c, 'REQ-041'); const mv = c.movs.filter(m => m.tipo === 'reserva' && m.req === 'REQ-041');
  ok('U41c complemento de 20 un: a REQ-041 passa de 1.169 a 1.189 un (reserva no CX26-02, movimento de reserva, linha no histórico); o toque repetido devolve o mesmo recibo sem gravar',
     !cp.erro && it.solicitado === 1189 && cenSaldoEntregar(it) === 20 && c.lotes[CX + '|CX26-02'].reservado === l0 + 20 && mv.length === 2 && mv[1].qtd === 20 && mv[1].lote === 'CX26-02'
     && O(c, id).ins[0].tot === 1189 && /Caixas pedidas · REQ-041 \+20 un/.test(O(c, id).ben.hist.slice(-1)[0].ev) && rp.nada && rp.msg === 'Já feito: ' + cp.msg, [cp, rp, it, mv]);
  const e = MUD(c, x => cenEntregar(x, 'REQ-041', CX, 20, null, RU)); const g = MUD(c, x => benSaida(x, id, { fluxo: 'Produto', classe: 'B', cx: 20, bruto: 212 }, IG));
  const d = MUD(c, x => benSaida(x, id, { fluxo: 'Descarte', destino: 'Compostagem', kg: 410 }, IG));
  const fim = [MUD(c, x => benConcluir(x, id, IG)), MUD(c, x => benConferir(x, id, PA)), MUD(c, x => benFechar(x, id, IG))]; const bb = benBal(O(c, id));
  ok('U41d o Estoque entrega as 20 un no balcão (custódia), o Igor embala, e o balanço fecha 12.300 kg (A 11.000 + B 890 + descarte 410) com diferença 0, sem perda nem justificativa; custódia 0 no Fechar',
     !e.erro && !g.erro && !d.erro && fim.every(x => !x.erro) && O(c, id).etapa === 'Encerradas' && bb.dif === 0 && bb.prod === 11890 && bb.desc === 410 && bb.perda === 0 && !(O(c, id).ben.just || []).length
     && REQ(c, 'REQ-041').custodia === 0 && REQ(c, 'REQ-041').consumido === 1189, [e, g, d, fim, bb]); }
{ /* o lote da REQ sem caixa livre bastante: o complemento sai do lote com caixas livres numa requisição própria da ordem (linha por lote,
     BEN-REV-20261009-03), mesmo com caixa em custódia; o item da REQ-041 nunca troca de lote (a trava "use a custódia antes" protegia só o
     item único e caiu com a linha por lote) */
  const c = NOVO(); const id = OB113(c); MUD(c, x => benSaida(x, id, { fluxo: 'Produto', classe: 'A', cx: 1159, bruto: 12285.4 }, IG));
  const m1 = MUD(c, x => benComplementar(x, id, 40, IG, { chave: 'W-BNX-T5' })); const it = REQ(c, 'REQ-041'), i2 = c.reqs['REQ-042'] ? REQ(c, 'REQ-042') : null;
  ok('U41e com 10 un em custódia e 31 livres no CX26-02, pedir 40: saem do CX26-01 (540 livres) na REQ-042, requisição própria da ordem; a REQ-041 continua no CX26-02 com as 10 un e a mensagem diz o porquê',
     !m1.erro && it.lote === 'CX26-02' && it.solicitado === 1169 && it.custodia === 10 && !!i2 && i2.lote === 'CX26-01' && i2.solicitado === 40 && c.reqs['REQ-042'].os === id
     && c.lotes[CX + '|CX26-01'].reservado === 40 && c.lotes[CX + '|CX26-02'].reservado === 0 && O(c, id).ins[0].tot === 1209
     && /pedidas para a OB-0113 no CX26-01 \(o CX26-02 da REQ-041 tinha 31 un livres: requisição própria, a devolução volta a cada lote\): REQ-042 com 40 un\./.test(m1.msg || ''), [m1, it, i2]);
  const e = MUD(c, x => cenEntregar(x, 'REQ-042', CX, 40, null, RU)); const l1 = c.lotes[CX + '|CX26-01'];
  ok('U41g a entrega das 40 un da REQ-042 baixa o CX26-01 (físico 500, reserva 0) e vira custódia da ordem (10 da REQ-041 + 40 da REQ-042)',
     !e.erro && l1.fisico === 500 && l1.reservado === 0 && REQ(c, 'REQ-042').custodia === 40 && CUST(c, O(c, id)) === 50 && CUSTX(c, O(c, id)) === '50 un (REQ-041 · CX26-02 10 un; REQ-042 · CX26-01 40 un)', [e, l1, CUSTX(c, O(c, id))]);
  const c2 = NOVO(); const n2 = MUD(c2, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG)); const a2 = MUD(c2, x => benComplementar(x, n2.id, 10, IG, { chave: 'W-BNX-T7' }));
  ok('U41h ordem em A liberar: pedir caixas é recusado (as caixas da ordem se ajustam antes de liberar; a reserva nasce na liberação)', /^Peça caixas com a ordem liberada ou em execução \(OB-0113 está em A liberar\)/.test(a2.erro || ''), a2); }

// ---- U42 · rodada 1 (S3): o recibo da ordem nova guarda o número; o toque repetido devolve a mesma ordem (a tela abre a criada) ----
{ const c = NOVO(); const k = { lotes: [{ lote: 'L39-132', kg: 12300 }], chave: 'W-BNN-T42' }; const a = MUD(c, x => benNova(x, k, IG)); const b = MUD(c, x => benNova(x, k, IG));
  ok('U42a criar com a mesma chave: a 2ª vez é "Já feito" sem gravar e devolve o mesmo número (OB-0113), sem OB-0114', a.id === 'OB-0113' && b.nada && b.id === 'OB-0113' && /^Já feito: OB-0113 criada/.test(b.msg) && !c.ordens['OB-0114'], [a, b]); }

// ---- U43 · rodada 1 (NAV-CLAREZA 3): o verbo do efeito — "Enviar para conferência", como a O.S.; nada de "Concluir" na tela ----
{ const c = NOVO(); const p = benProx(c, O(c, 'OB-0110')); const an = MUD(c, x => benConcluir(x, 'OB-0110', AN)); const c2 = NOVO(); MUD(c2, x => benEstornar(x, 'OB-0110', 'S-01', 'Erro de digitação', '', IG)); MUD(c2, x => benEstornar(x, 'OB-0110', 'S-02', 'Erro de digitação', '', IG));
  const sp = MUD(c2, x => benConcluir(x, 'OB-0110', IG)); const ok1 = MUD(c, x => benConcluir(x, 'OB-0110', IG)); const h = O(c, 'OB-0110').ben.hist.slice(-1)[0];
  const rb = MUD(c, x => benReabrir(x, 'OB-0110', 'faltou a classe B', IG)); const h2 = O(c, 'OB-0110').ben.hist.slice(-1)[0];
  ok('U43a OB-0110 em execução: próximo passo "Enviar para conferência"; sem papel: "Enviar a OB-0110 para conferência: decisão de Igor"; sem Produto: "antes de enviar para conferência"; histórico "Enviada para conferência"; o Reabrir fala do envio',
     p.t === 'Enviar para conferência' && p.acao === 'concluir' && /^Enviar a OB-0110 para conferência: decisão de Igor/.test(an.erro || '') && /antes de enviar para conferência\.$/.test(sp.erro || '')
     && !ok1.erro && h.ev === 'Enviada para conferência' && /diferença no envio 0 kg/.test(h.det) && !rb.erro && /a declaração do envio para conferência cai/.test(h2.det), [p, an, sp, h, h2]); }

// ---- U44 · rodada 1 (S4): comando sobre ordem Cancelada é recusa (com o motivo), não aviso de sucesso "Já feito" ----
{ const c = NOVO(); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG)); const v0 = O(c, n.id).ver; MUD(c, x => benCancelar(x, n.id, 'caixas insuficientes', IG)); const r0 = c.rev || 0;
  const r = [MUD(c, x => benAutorizarLiberar(x, n.id, IG, { ver: v0 })), MUD(c, x => benIniciar(x, n.id, IG)), MUD(c, x => benConfirmarCorrecao(x, n.id, AN))];
  ok('U44a liberar (outra aba), iniciar e confirmar correção numa ordem Cancelada: recusa com o motivo e o caminho (nunca "Já feito"); nada gravado',
     r.every(x => x.erro && !/^Já feito/.test(x.erro) && /^OB-0113 cancelada \(caixas insuficientes\): nada a /.test(x.erro) && /As entradas abrem outra ordem\.$/.test(x.erro)) && (c.rev || 0) === r0 && O(c, n.id).etapa === 'Canceladas', r); }

// ---- U45 · BEN-REV-20261009-03 (S2): complemento em outro lote não muda a origem das caixas. Linha própria por lote (REQ do complemento);
//      consumo, estorno e devolução no lote de origem; saldos, reservas e trilha por lote fecham; recibo, versão e perfil continuam valendo ----
const LOT = (c, l) => c.lotes[CX + '|' + l] || {};
/* trilha do lote de caixa: físico = físico inicial + recebido − entregue + devolvido; entregue, devolvido e consumido líquido dos movimentos
   = o que as linhas desse lote mudaram desde a semente; custódia de cada linha = entregue − devolvido − consumido; reserva = o "a entregar" das linhas
   de ordem aberta (solicitado − dispensado − consumido − custódia: a caixa em uso devolvida volta reservada; rodada 3, BEN-D33) */
function TRILHA(c, lote) { const ini = LOT(CEN0, lote).fisico || 0; const mv = c.movs.filter(m => m.prod === CX && m.lote === lote); const S = t => mv.filter(m => m.tipo === t).reduce((a, m) => a + m.qtd, 0);
  const lin = x => Object.values(x.reqs).reduce((a, r) => a.concat(r.itens.filter(i => i.prod === CX && i.lote === lote)), []); const L = lin(c), L0 = lin(CEN0);
  const D = f => L.reduce((a, i) => a + (i[f] || 0), 0) - L0.reduce((a, i) => a + (i[f] || 0), 0);
  const r = { fis: ini + S('recebimento-nf') - S('entrega') + S('devolucao') === LOT(c, lote).fisico, ent: S('entrega') === D('entregue'), dev: S('devolucao') === D('devolvido'),
    cons: S('consumo') - S('estorno-consumo') === D('consumido'), cust: L.every(i => i.entregue - i.devolvido - i.consumido === i.custodia),
    res: (LOT(c, lote).reservado || 0) === Object.values(c.reqs).reduce((a, r) => a + r.itens.filter(i => i.prod === CX && i.lote === lote && ['Encerradas', 'Canceladas'].indexOf((c.ordens[r.os] || {}).etapa) < 0)
      .reduce((b, i) => b + Math.max(0, i.solicitado - (i.dispensado || 0) - i.consumido - i.custodia), 0), 0) };
  r.ok = Object.values(r).every(Boolean); return r; }
/* a reprodução do Codex: ordem do L39-132 com 540 caixas explícitas, entregues do CX26-01 e usadas na S-01; 1.000 caixas novas no QA-CX-02 */
function OB540(c) { const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }], cx: 540 }, IG)); MUD(c, x => benAutorizarLiberar(x, n.id, IG)); const rid = O(c, n.id).req;
  MUD(c, x => cenEntregar(x, rid, CX, 540, 'Igor', RU)); MUD(c, x => benIniciar(x, n.id, IG)); MUD(c, x => benSaida(x, n.id, { fluxo: 'Produto', classe: 'A', cx: 540, bruto: 5724 }, IG));
  MUD(c, x => cenReceber(x, CX, 'QA-CX-02', 1000, 'un', 'Packing', '', 'NF-QA-02', true, RU)); return { id: n.id, rid }; }
{ const c = NOVO(); const z = OB540(c); const it1 = () => REQ(c, z.rid);
  const cp = MUD(c, x => benComplementar(x, z.id, 100, IG, { chave: 'W-BNX-45A', ver: O(c, z.id).ver })); const o = O(c, z.id); const r2 = (o.ben.reqc || [])[0]; const it2 = r2 ? REQ(c, r2) : null;
  const mr = c.movs.filter(m => m.tipo === 'reserva' && m.os === z.id).slice(-1)[0] || {};
  ok('U45a sem caixa livre no CX26-01 (lote da REQ-041), 100 un saem do QA-CX-02 numa requisição própria (REQ-042, linha por lote); a REQ-041 continua no CX26-01 com o consumo dela; reserva 100 no QA-CX-02',
     !cp.erro && z.rid === 'REQ-041' && it1().lote === 'CX26-01' && it1().solicitado === 540 && it1().consumido === 540 && r2 === 'REQ-042' && !!it2 && it2.lote === 'QA-CX-02' && it2.solicitado === 100
     && c.reqs[r2].os === z.id && LOT(c, 'QA-CX-02').reservado === 100 && mr.req === 'REQ-042' && mr.lote === 'QA-CX-02' && mr.qtd === 100 && o.ins[0].tot === 640 && /REQ-042 com 100 un/.test(cp.msg || ''), [cp, it1(), it2, mr]);
  const e = MUD(c, x => benEstornar(x, z.id, 'S-01', 'Pesagem refeita', '', IG, { chave: 'W-BNE-45A', ver: O(c, z.id).ver })); const s = O(c, z.id).ben.sai.find(y => y.id === 'S-01');
  const m0 = c.movs.find(m => m.id === s.mv) || {}, m1 = c.movs.find(m => m.id === (s.estorno || {}).mv) || {};
  ok('U45b estorno da S-01 (Pesagem refeita): o estorno-consumo volta ao CX26-01 e à REQ-041 (o lote e a requisição do consumo, ref ao movimento original); a REQ-042 fica intacta',
     !e.erro && m0.lote === 'CX26-01' && m1.tipo === 'estorno-consumo' && m1.lote === 'CX26-01' && m1.req === 'REQ-041' && m1.ref === m0.id && it1().custodia === 540 && it1().consumido === 0
     && !!it2 && REQ(c, 'REQ-042').custodia === 0 && REQ(c, 'REQ-042').solicitado === 100, [e, m0, m1, it1()]);
  const d = MUD(c, x => cenDevolver(x, z.rid, CX, 540, true, RU));
  ok('U45c devolvidas as 540 un da REQ-041: o CX26-01 volta a 540 e o QA-CX-02 continua com 1.000 (reserva 100 da REQ-042); a trilha de cada lote fecha',
     !d.erro && LOT(c, 'CX26-01').fisico === 540 && LOT(c, 'QA-CX-02').fisico === 1000 && LOT(c, 'QA-CX-02').reservado === 100 && TRILHA(c, 'CX26-01').ok && TRILHA(c, 'QA-CX-02').ok,
     [d, LOT(c, 'CX26-01'), LOT(c, 'QA-CX-02'), TRILHA(c, 'CX26-01'), TRILHA(c, 'QA-CX-02')]); }
{ /* caixas novas e antigas misturadas na custódia, até o Fechar dos 12.300 kg */
  const c = NOVO(); const z = OB540(c); const V = ch => ({ chave: ch, ver: O(c, z.id).ver });
  MUD(c, x => benComplementar(x, z.id, 100, IG, V('W-BNX-45D'))); MUD(c, x => cenEntregar(x, 'REQ-042', CX, 100, null, RU)); MUD(c, x => benEstornar(x, z.id, 'S-01', 'Pesagem refeita', '', IG, V('W-BNE-45D')));
  const g = MUD(c, x => benSaida(x, z.id, { fluxo: 'Produto', classe: 'A', cx: 600, bruto: 6360, chave: 'W-BNS-45D', ver: O(c, z.id).ver }, IG)); const s2 = O(c, z.id).ben.sai.find(y => y.id === 'S-02') || {};
  const mv2 = (s2.cons || []).map(p => [p.req, p.lote, p.qtd, (c.movs.find(m => m.id === p.mv) || {}).lote]);
  ok('U45d caixas misturadas (540 do CX26-01 de volta pelo estorno + 100 do QA-CX-02): 600 cx consomem por lote, a requisição mais antiga primeiro (REQ-041 540 · CX26-01, REQ-042 60 · QA-CX-02), um movimento por lote',
     !g.erro && JSON.stringify(mv2) === JSON.stringify([['REQ-041', 'CX26-01', 540, 'CX26-01'], ['REQ-042', 'QA-CX-02', 60, 'QA-CX-02']]) && REQ(c, 'REQ-041').custodia === 0 && REQ(c, 'REQ-042').custodia === 40, [g, mv2]);
  const e2 = MUD(c, x => benEstornar(x, z.id, 'S-02', 'Erro de digitação', '', IG, V('W-BNE-45E'))); const es = c.movs.filter(m => m.tipo === 'estorno-consumo' && (s2.cons || []).some(p => p.mv === m.ref));
  ok('U45e estorno da saída misturada: cada parte volta ao seu lote e à sua requisição (540 → CX26-01 · REQ-041, 60 → QA-CX-02 · REQ-042), com ref ao movimento de cada parte',
     !e2.erro && es.length === 2 && es.every(m => { const p = s2.cons.find(q => q.mv === m.ref); return !!p && m.lote === p.lote && m.req === p.req && m.qtd === p.qtd; })
     && REQ(c, 'REQ-041').custodia === 540 && REQ(c, 'REQ-042').custodia === 100 && /540 un ao CX26-01 · REQ-041, 60 un ao QA-CX-02 · REQ-042/.test(O(c, z.id).ben.hist.slice(-1)[0].det), [e2, es, O(c, z.id).ben.hist.slice(-1)[0]]);
  const a = MUD(c, x => benSaida(x, z.id, { fluxo: 'Produto', classe: 'A', cx: 540, bruto: 5724 }, IG)); const p = MUD(c, x => benComplementar(x, z.id, 600, IG, V('W-BNX-45F')));
  const en = MUD(c, x => cenEntregar(x, 'REQ-042', CX, 600, null, RU)); const b = MUD(c, x => benSaida(x, z.id, { fluxo: 'Produto', classe: 'B', cx: 690, bruto: 7314 }, IG));
  const f0 = [MUD(c, x => benConcluir(x, z.id, IG)), MUD(c, x => benConferir(x, z.id, PA))]; const fr = MUD(c, x => benFechar(x, z.id, IG)); const nx = benProx(c, O(c, z.id));
  ok('U45f o complemento seguinte cabe no QA-CX-02 e soma à REQ-042 (sem REQ nova); com 10 un dela em custódia o Fechar é recusado com a REQ e o lote, e o próximo passo diz o mesmo',
     !a.erro && !p.erro && !en.erro && !b.erro && f0.every(x => !x.erro) && !c.reqs['REQ-043'] && REQ(c, 'REQ-042').solicitado === 700
     && fr.erro === 'Sobra em custódia: Caixa de mamão Formosa 10 kg 10 un (REQ-042 · QA-CX-02). Receba a devolução no Estoque.' && nx.red && /REQ-042 · QA-CX-02/.test(nx.nota || ''), [a, p, en, b, f0, fr, nx]);
  const dv = MUD(c, x => cenDevolver(x, 'REQ-042', CX, 10, true, RU)); const fe = MUD(c, x => benFechar(x, z.id, IG)); const bb = benBal(O(c, z.id));
  ok('U45g devolvidas as 10 un ao QA-CX-02, o Fechar encerra os 12.300 kg (A 5.400 + B 6.900) com diferença 0, sem perda nem justificativa; CX26-01 0 e QA-CX-02 310 sem reserva; a trilha de cada lote fecha',
     !dv.erro && !fe.erro && O(c, z.id).etapa === 'Encerradas' && bb.dif === 0 && bb.prod === 12300 && bb.perda === 0 && !(O(c, z.id).ben.just || []).length
     && LOT(c, 'CX26-01').fisico === 0 && LOT(c, 'QA-CX-02').fisico === 310 && LOT(c, 'QA-CX-02').reservado === 0 && TRILHA(c, 'CX26-01').ok && TRILHA(c, 'QA-CX-02').ok,
     [dv, fe, bb, LOT(c, 'QA-CX-02'), TRILHA(c, 'CX26-01'), TRILHA(c, 'QA-CX-02')]); }
{ /* recibo, versão e perfil no complemento em outro lote */
  const c = NOVO(); const z = OB540(c); const a = MUD(c, x => benComplementar(x, z.id, 100, IG, { chave: 'W-BNX-45H', ver: O(c, z.id).ver })); const j0 = JSON.stringify(c);
  const b = MUD(c, x => benComplementar(x, z.id, 100, IG, { chave: 'W-BNX-45H' })); const d = MUD(c, x => benComplementar(x, z.id, 101, IG, { chave: 'W-BNX-45H' }));
  const v = MUD(c, x => benComplementar(x, z.id, 100, IG, { chave: 'W-BNX-45V', ver: O(c, z.id).ver - 1 })); const pr = MUD(c, x => benComplementar(x, z.id, 100, RU, { chave: 'W-BNX-45P' }));
  ok('U45h complemento em outro lote: o toque repetido devolve o mesmo recibo (sem REQ-043), conteúdo diferente com a mesma chave é conflito; versão vencida e perfil sem papel recusados; nada gravado',
     !a.erro && !!c.reqs['REQ-042'] && b.nada && b.msg === 'Já feito: ' + a.msg && /conflito, nada gravado/.test(d.erro || '') && /mudou depois que você abriu/.test(v.erro || '') && /decisão de Igor/.test(pr.erro || '')
     && JSON.stringify(c) === j0 && !c.reqs['REQ-043'], [a, b, d, v, pr]); }

// ---- U46 · integração BEN, rodada 2 (S2 da reverificação): a recuperação da falta de caixas nunca tira as caixas que outra ordem liberada
//      ou em execução ainda vai usar. Sobra = custódia acima do máximo que ela ainda pode embalar (⌈kg a embalar ÷ 10 kg⌉); em conferência,
//      a custódia inteira. Antes: a OB-0112 mandava receber a "devolução" das 1.169 caixas da OB-0113 liberada; seguida, a OB-0113 ficava
//      com 919 de 1.169 caixas, sem cancelar e com ~2.500 kg sem caixa (perda fictícia ou destinação forçada) ----
const SOB = (c, id) => typeof benCxSobra === 'function' ? benCxSobra(c, O(c, id)) : 'sem benCxSobra';
function CADEIA(c) { const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG)); RECEBE_NF(c, 1200);
  const st = [MUD(c, x => benAutorizarLiberar(x, n.id, IG)), MUD(c, x => cenEntregar(x, 'REQ-041', CX, 1169, null, RU)), MUD(c, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)),
    MUD(c, x => benResultado(x, 'L39-119', 'Conforme', '', MA)), MUD(c, x => benDecidir(x, 'L39-119', 'Liberar', {}, MA))]; return { id: n.id, st }; }
const CXIMP = (c, id) => benImpedimentos(c, O(c, id)).find(y => y.cx) || {};
{ const c = NOVO(); const z = CADEIA(c); const im = CXIMP(c, 'OB-0112'); const l = im.link || {};
  ok('U46a OB-0113 liberada com as 1.169 caixas do L39-132: a falta da OB-0112 (631 para 881, os dois lotes) não aponta a custódia dela; sem nota nem sobra, a saída é a compra (BEN-2) ou Cancelar a ordem em A liberar',
     z.id === 'OB-0113' && z.st.every(y => !y.erro) && O(c, 'OB-0113').etapa === 'Liberadas' && REQ(c, 'REQ-041').custodia === 1169 && SOB(c, 'OB-0113') === 0
     && /631 un disponíveis para 881 un/.test(im.t || '') && l.t === 'Ver saldo de caixas no Estoque' && !/OB-0113/.test(l.why || '') && /^Faltam 250 un e não há nota/.test(l.why || '') && /Cancelar a ordem/.test(l.why || ''), [z.st.map(y => y.erro || ''), SOB(c, 'OB-0113'), im]);
  const i0 = MUD(c, x => benIniciar(x, 'OB-0113', IG)); const imx = CXIMP(c, 'OB-0112'); const s0 = SOB(c, 'OB-0113');
  const a = MUD(c, x => benSaida(x, 'OB-0113', { fluxo: 'Produto', classe: 'A', cx: 1100, bruto: 11660 }, IG)); const s1 = SOB(c, 'OB-0113'); const ima = CXIMP(c, 'OB-0112');
  ok('U46b em execução a OB-0113 guarda as caixas que ainda pode usar: antes das saídas (1.169 un para 12.300 kg) e com 1.300 kg a registrar e 69 un em custódia (até 130 cx), sobra 0 e nenhuma recomendação de devolução',
     !i0.erro && !a.erro && s0 === 0 && s1 === 0 && REQ(c, 'REQ-041').custodia === 69 && (imx.link || {}).t === 'Ver saldo de caixas no Estoque' && (ima.link || {}).t === 'Ver saldo de caixas no Estoque'
     && !/OB-0113/.test((imx.link || {}).why || '') && !/OB-0113/.test((ima.link || {}).why || ''), [i0, a, s0, s1, imx, ima]);
  const d = MUD(c, x => benSaida(x, 'OB-0113', { fluxo: 'Descarte', destino: 'Compostagem', kg: 1300 }, IG)); const imd = CXIMP(c, 'OB-0112');
  const e = MUD(c, x => benConcluir(x, 'OB-0113', IG)); const ime = CXIMP(c, 'OB-0112');
  ok('U46c com tudo registrado (nada a embalar) as 69 un são sobra, e em conferência também: a OB-0112 recebe o atalho "Receber a devolução da OB-0113" com a sobra (69 un)',
     !d.erro && !e.erro && (imd.link || {}).t === 'Receber a devolução da OB-0113 no Estoque' && /^Faltam 250 un\. A OB-0113 tem sobra de 69 un em custódia \(Receba devoluções\)\. Ainda faltam 181 un/.test((imd.link || {}).why || '')
     && O(c, 'OB-0113').etapa === 'Em conferência' && SOB(c, 'OB-0113') === 69 && (ime.link || {}).t === 'Receber a devolução da OB-0113 no Estoque', [d, e, imd, ime]); }
{ /* a OB-0113 liberada com caixas acima do que pode usar (1.300 un para 12.300 kg, até 1.230 cx): só as 70 un acima contam como sobra */
  const c = NOVO(); RECEBE_NF(c, 1400); MUD(c, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }], cx: 1300 }, IG));
  const l = MUD(c, x => benAutorizarLiberar(x, n.id, IG)); const rid = O(c, n.id).req; const en = MUD(c, x => cenEntregar(x, rid, CX, 1300, null, RU));
  const n2 = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 24120 }] }, IG)); const im = CXIMP(c, n2.id);
  ok('U46d ordem liberada com 1.300 caixas para 12.300 kg (no máximo 1.230 cx): sobra 70 un, e a OB-0114 do L39-131 vê só essa sobra (nunca as 1.300)',
     !l.erro && !en.erro && SOB(c, n.id) === 70 && /A OB-0113 tem sobra de 70 un em custódia/.test((im.link || {}).why || ''), [l, en, SOB(c, n.id), im]); }
{ /* falta de caixa na execução sem nota nem sobra: a recusa do "Pedir mais caixas" não manda cancelar (a ordem liberada não se cancela, BEN-6) */
  const c = NOVO(); RECEBE_NF(c, 1200); MUD(c, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG));
  const st = [MUD(c, x => benAutorizarLiberar(x, n.id, IG)), MUD(c, x => cenEntregar(x, 'REQ-041', CX, 1169, null, RU)), MUD(c, x => benIniciar(x, n.id, IG)),
    MUD(c, x => benSaida(x, n.id, { fluxo: 'Produto', classe: 'A', cx: 1169, bruto: 12391.4 }, IG))]; const j0 = JSON.stringify(c);
  const p = MUD(c, x => benComplementar(x, n.id, 700, IG, { chave: 'W-BNX-46E', ver: O(c, n.id).ver }));
  ok('U46e em execução, pedir 700 com 631 livres (dois lotes) e sem nota nem sobra: recusa sem gravar que diz a compra (BEN-2) e o caminho da nota no Estoque, sem "Cancelar a ordem"',
     st.every(y => !y.erro) && /^Pedir 700 un: 631 un livres no Estoque\. Faltam 69 un e não há nota de caixas a conferir nem sobra em custódia: a compra de caixas entra no BEN-2\./.test(p.erro || '')
     && /Confira recebimentos/.test(p.erro || '') && /Pedir mais caixas/.test(p.erro || '') && !/Cancelar a ordem/.test(p.erro || '') && JSON.stringify(c) === j0, [st.map(y => y.erro || ''), p]); }

// ===== Integração BEN, rodada 3 (10/10/2026): recuperação de caixas entre ordens e lotes (BEN-D33..D36). Cada achado da rodada 2 tem um
//       teste que reprova no 0139898; as funções novas são lidas com guarda (typeof) para o teste rodar também no código anterior =====
function T3(nome, fn) { try { fn(); } catch (e) { ok(nome + ' (exceção no teste)', false, String((e && e.stack) || e).slice(0, 400)); } }
/* oráculo independente das funções sob teste: livre total, "a entregar" com o termo da sobra devolvida, reserva própria */
const LIVRETOT = c => Object.values(c.lotes).filter(l => l.prod === CX).reduce((a, l) => a + Math.floor(Math.max(0, l.fisico - l.quarentena - l.reservado) + 1e-9), 0);
const PEND = it => Math.max(0, it.solicitado - (it.dispensado || 0) - it.consumido - it.custodia);
const OWN = (c, rid) => { const it = REQ(c, rid); return cenResPropria(c, rid, it, c.lotes[CX + '|' + it.lote]); };
const FALTA = (c, id) => typeof benFaltaCx === 'function' ? benFaltaCx(c, O(c, id)) : 'sem benFaltaCx';
const DEVP = (c, id, rid) => typeof benDevPadrao === 'function' ? benDevPadrao(c, O(c, id), REQ(c, rid), rid) : 'sem benDevPadrao';
const LINHAS = (c, id) => benLinhas(c, O(c, id)).map(x => [x.rid, x.it.lote, x.it.solicitado]);
const SOMA = (c, id, f) => benLinhas(c, O(c, id)).reduce((a, x) => a + f(x), 0);
/* a cadeia da rodada 2 (OB-0113 liberada com 1.169 caixas do CX26-02 entregues; OB-0110 devolveu 60 ao CX26-01; L39-119 liberado: a OB-0112
   só fica impedida pelas caixas) seguida do início e de saídas */
function CAD(c, sai) { const z = CADEIA(c); const st = z.st.concat([MUD(c, x => benIniciar(x, z.id, IG))]).concat((sai || []).map(k => MUD(c, x => benSaida(x, z.id, k, IG)))); return { id: z.id, st }; }
const SA = (cx, br, cl) => ({ fluxo: 'Produto', classe: cl || 'A', cx, bruto: br }), SD = kg => ({ fluxo: 'Descarte', destino: 'Compostagem', kg });

// ---- U47 · S2-1: em conferência a sobra é a custódia acima do teto do kg ainda aberto (entrada − saídas válidas, com ou sem conferência
//      dada); antes a custódia inteira virava sobra e a OB-0112 levava as caixas que a OB-0113 precisa para relançar o estornado ----
T3('U47a', () => { const c = NOVO(); const z = CAD(c, [SA(1000, 10600), SA(169, 1791.4, 'B'), SD(610)]); const id = z.id;
  const st = z.st.concat([MUD(c, x => benConcluir(x, id, IG)), MUD(c, x => benConferir(x, id, PA))]); const e = MUD(c, x => benEstornar(x, id, 'S-01', 'Pesagem refeita', '', IG));
  const l = CXIMP(c, 'OB-0112').link || {};
  ok('U47a OB-0113 conferida com diferença 0; estorno da S-01 na conferência: as 1.000 caixas voltam à custódia e a sobra é 0 (10.000 kg a registrar); a OB-0112 não aponta a OB-0113',
     st.every(y => !y.erro) && !e.erro && O(c, id).etapa === 'Em conferência' && REQ(c, 'REQ-041').custodia === 1000 && SOB(c, id) === 0 && !/OB-0113/.test(l.why || '') && !/OB-0113/.test(l.t || ''), [st.map(y => y.erro || ''), e, SOB(c, id), l]); });
T3('U47b', () => { const c = NOVO(); const z = CAD(c, [SA(1000, 10600), SD(610)]); const cc = MUD(c, x => benConcluir(x, z.id, IG)); const l = CXIMP(c, 'OB-0112').link || {};
  ok('U47b "faltou a classe B": enviada para conferência com 1.690 kg sem registro e 169 caixas em custódia, a sobra é 0 (antes 169) e a OB-0112 não as aponta',
     z.st.every(y => !y.erro) && !cc.erro && REQ(c, 'REQ-041').custodia === 169 && SOB(c, z.id) === 0 && !/OB-0113/.test(l.why || ''), [cc, SOB(c, z.id), l]); });
T3('U47c', () => { const c = NOVO(); const o = O(c, 'OB-0110'); o.ben.ent = [{ lote: o.ben.ent[0].lote, kg: 600 }];
  o.ben.sai = [{ id: 'S-01', fluxo: 'Descarte', destino: 'Compostagem', kg: 10, cx: 0, estorno: { quem: IG, em: '', motivo: 'Pesagem refeita' }, ev: {} }]; o.ben.nsai = 1; o.etapa = 'Em conferência'; o.ben.conc = { quem: IG, em: '', dif0: 600 };
  ok('U47c reprodução 1 do Codex: OB-0110 em conferência com 600 kg de entrada, a única saída (10 kg) estornada e 60 caixas em custódia: sobra 0 (antes 60)', REQ(c, 'REQ-030').custodia === 60 && SOB(c, 'OB-0110') === 0, SOB(c, 'OB-0110')); });
T3('U47d', () => { const c = NOVO(); const a = MUD(c, x => benConcluir(x, 'OB-0110', IG));
  ok('U47d controle: OB-0110 em conferência com tudo registrado (diferença 0): a sobra é a custódia inteira (60)', !a.erro && SOB(c, 'OB-0110') === 60, [a, SOB(c, 'OB-0110')]); });
T3('U47e', () => { const c = NOVO(); const z = CAD(c, [SA(1000, 10600), SA(160, 1696, 'B'), SD(695)]); const id = z.id; const cc = MUD(c, x => benConcluir(x, id, IG));
  const b = benBal(O(c, id)); const q = DEVP(c, id, 'REQ-041'); const L0 = LIVRETOT(c); const r0 = (LOT(c, 'CX26-02').reservado || 0);
  const d = MUD(c, x => cenDevolver(x, 'REQ-041', CX, typeof q === 'number' ? q : REQ(c, 'REQ-041').custodia, true, RU));
  const f = [MUD(c, x => benConferir(x, id, PA)), MUD(c, x => benFechar(x, id, IG))];
  ok('U47e conferência com +5 kg dentro da faixa (12,3 kg): custódia 9, sobra 8, o Estoque traz 9; recebidas, 8 ficam livres e 1 volta reservada à linha; o Fechar encerra e baixa a reserva numa visita só',
     z.st.every(y => !y.erro) && !cc.erro && b.dif === 5 && b.dentro && REQ(c, 'REQ-041').custodia === 0 && q === 9 && SOB(c, id) === 0 && !d.erro && LIVRETOT(c) - L0 >= 8
     && f.every(y => !y.erro) && O(c, id).etapa === 'Encerradas' && (LOT(c, 'CX26-02').reservado || 0) === 0 && PEND(REQ(c, 'REQ-041')) === 0, [cc, b.dif, q, d, f, L0, LIVRETOT(c), r0, LOT(c, 'CX26-02')]); });

// ---- U48 · S2-2: sobra parcial em execução. A devolução se divide: a sobra volta livre (dispensada); a caixa em uso volta reservada à
//      própria linha. Sem "a entregar" fantasma, e a entrega baixa só a reserva própria (nunca a de outra requisição) ----
function PARCIAL(c) { return CAD(c, [SA(300, 3180), SD(2000)]); }   /* OB-0113 em execução: 869 caixas em custódia e 7.300 kg a registrar (até 730 cx): sobra 139 */
T3('U48a', () => { const c = NOVO(); const z = PARCIAL(c); const L0 = LIVRETOT(c), s0 = SOB(c, z.id); const d = MUD(c, x => cenDevolver(x, 'REQ-041', CX, 869, true, RU)); const it = REQ(c, 'REQ-041');
  ok('U48a devolvidas as 869 caixas da OB-0113 em execução (sobra 139): o livre total sobe só 139; 730 voltam reservadas à REQ-041 (a entregar = reserva própria = 730); a mensagem diz as duas partes',
     z.st.every(y => !y.erro) && s0 === 139 && !d.erro && LIVRETOT(c) - L0 === 139 && LOT(c, 'CX26-02').fisico === 900 && LOT(c, 'CX26-02').reservado === 730 && PEND(it) === 730 && OWN(c, 'REQ-041') === 730
     && cenSaldoEntregar(it) === 730 && /139 un ao disponível \(sobra da OB-0113\)/.test(d.msg || '') && /730 un voltam reservadas à OB-0113/.test(d.msg || ''), [s0, d, L0, LIVRETOT(c), LOT(c, 'CX26-02'), PEND(it), OWN(c, 'REQ-041'), cenSaldoEntregar(it)]); });
T3('U48b', () => { const c = NOVO(); const z = PARCIAL(c); MUD(c, x => cenDevolver(x, 'REQ-041', CX, 869, true, RU)); const im0 = CXIMP(c, 'OB-0112');
  const nf = MUD(c, x => cenReceber(x, CX, 'QA-CX-02', 120, 'un', 'Packing', '—', 'NF-QA-120', true, RU)); const lv = MUD(c, x => benAutorizarLiberar(x, 'OB-0112', IG));
  const own2 = () => O(c, 'OB-0112').req ? SOMA(c, 'OB-0112', x => cenResPropria(c, x.rid, x.it, c.lotes[CX + '|' + x.it.lote])) : -1;
  const a0 = own2(); const e = MUD(c, x => cenEntregar(x, 'REQ-041', CX, 730, null, RU)); const a1 = own2();
  ok('U48b com a sobra recebida (livre 770 < 881) a OB-0112 continua impedida; recebidas mais 120 un, ela libera; a entrega das 730 un da REQ-041 baixa só a reserva dela e a OB-0112 continua com 881 reservadas',
     /770 un disponíveis para 881 un/.test(im0.t || '') && !nf.error && !lv.erro && O(c, 'OB-0112').etapa === 'Liberadas' && SOMA(c, 'OB-0112', x => x.it.solicitado) === 881 && a0 === 881 && !e.erro && a1 === 881
     && REQ(c, 'REQ-041').custodia === 730 && OWN(c, 'REQ-041') === 0, [im0.t, lv, a0, e, a1, LINHAS(c, 'OB-0112')]); });
T3('U48c', () => { const c = NOVO(); const z = PARCIAL(c); const q = DEVP(c, z.id, 'REQ-041'); const L0 = LIVRETOT(c);
  const d = MUD(c, x => cenDevolver(x, 'REQ-041', CX, typeof q === 'number' && q > 0 ? q : REQ(c, 'REQ-041').custodia, true, RU)); const it = REQ(c, 'REQ-041');
  ok('U48c devolução guiada: o Estoque traz 139 (a sobra, nunca a custódia 869); recebida, a REQ-041 fica sem "a entregar" (0) e a sugestão do Pedir mais caixas é 0 (antes 1)',
     q === 139 && !d.erro && it.custodia === 730 && PEND(it) === 0 && cenSaldoEntregar(it) === 0 && FALTA(c, z.id) === 0 && LIVRETOT(c) - L0 === 139 && (LOT(c, 'CX26-02').reservado || 0) === 0, [q, d, it, FALTA(c, z.id)]); });
T3('U48d', () => { /* reprodução 3 do Codex (O.S.): QA-A solicitou, recebeu e devolveu 60 (custódia 0); o lote tem 100 físicos e 80 reservados à QA-B */
  const c = NOVO(); const P = 'Insumo QA'; c.lotes[P + '|QA-L1'] = { prod: P, lote: 'QA-L1', local: 'Galpão 1', un: 'un', fisico: 100, quarentena: 0, reservado: 80, validade: '—' };
  ['QA-OA', 'QA-OB'].forEach(id => { c.ordens[id] = { id, tipo: 'teste', talhao: 'T', area: 0, etapa: 'Em execução', versao: 'v1', realizado: 0, saldo: 0, resp: 'Sérgio', ins: [], req: id === 'QA-OA' ? 'QA-A' : 'QA-B', selos: [], ap: [] }; });
  c.reqs['QA-A'] = { id: 'QA-A', os: 'QA-OA', estado: 'Entregue', itens: [{ prod: P, lote: 'QA-L1', un: 'un', solicitado: 60, entregue: 60, consumido: 0, devolvido: 60, custodia: 0 }] };
  c.reqs['QA-B'] = { id: 'QA-B', os: 'QA-OB', estado: 'Reservada', itens: [{ prod: P, lote: 'QA-L1', un: 'un', solicitado: 80, entregue: 0, consumido: 0, devolvido: 0, custodia: 0 }] };
  c.movs.push({ id: 'MV-QA1', tipo: 'reserva', req: 'QA-A', os: 'QA-OA', prod: P, lote: 'QA-L1', qtd: 60 }, { id: 'MV-QA2', tipo: 'reserva', req: 'QA-B', os: 'QA-OB', prod: P, lote: 'QA-L1', qtd: 80 });
  const e = MUD(c, x => cenEntregar(x, 'QA-A', P, 60, null, RU)); const l = c.lotes[P + '|QA-L1']; const e0 = JSON.stringify(l);
  const e2 = MUD(c, x => cenEntregar(x, 'QA-A', P, 20, null, RU)); const l2 = c.lotes[P + '|QA-L1'];
  ok('U48d reprodução 3 do Codex: entregar de novo 60 à QA-A (reserva própria 0, livre 20) é recusado e a QA-B continua com as 80 reservadas (antes: aceito, físico 40 e reserva 20); 20 saem do livre sem tocar na reserva da QA-B',
     !!e.erro && e0 === JSON.stringify({ prod: P, lote: 'QA-L1', local: 'Galpão 1', un: 'un', fisico: 100, quarentena: 0, reservado: 80, validade: '—' }) && !e2.erro && l2.fisico === 80 && l2.reservado === 80, [e, e0, e2, l2]); });
T3('U48e', () => { /* sobra de 150 em duas linhas (REQ-041 100 e REQ-042 100 em custódia; teto 50): a fonte traz as duas linhas e Σ = 150 */
  const c = NOVO(); const z = OB540(c); const id = z.id;
  const st = [MUD(c, x => benEstornar(x, id, 'S-01', 'Pesagem refeita', '', IG)), MUD(c, x => benSaida(x, id, SA(440, 4664), IG)), MUD(c, x => benComplementar(x, id, 100, IG, { chave: 'W-BNX-48E' })),
    MUD(c, x => cenEntregar(x, 'REQ-042', CX, 100, null, RU)), MUD(c, x => benSaida(x, id, SD(7400), IG))];
  const sl = typeof benSobraLinhas === 'function' ? benSobraLinhas(c, O(c, id)) : null; const L0 = LIVRETOT(c);
  const tem = () => SOMA(c, id, x => x.it.custodia + cenResPropria(c, x.rid, x.it, c.lotes[CX + '|' + x.it.lote]));
  (sl || []).forEach(p => MUD(c, x => cenDevolver(x, p.rid, CX, p.qtd, true, RU)));
  ok('U48e sobra de 150 em duas linhas (100 + 100 em custódia, 500 kg a registrar): as linhas da fonte são REQ-042 100 e REQ-041 50 (Σ 150); seguidas, o livre total sobe 150 e a ordem fica com 50 (custódia + reserva própria)',
     st.every(y => !y.erro) && SOB(c, id) === 0 && !!sl && JSON.stringify(sl.map(p => [p.rid, p.qtd])) === '[["REQ-042",100],["REQ-041",50]]' && LIVRETOT(c) - L0 === 150 && tem() === 50, [st.map(y => y.erro || ''), sl, LIVRETOT(c) - L0, tem()]); });

// ---- U49 · S2-3: caixas em mais de um lote. Liberação, impedimento e complemento contam e reservam no mesmo conjunto de lotes elegíveis,
//      uma linha por lote, tudo ou nada; a quarentena é citada com quem libera ----
function NF_PARTE(c, apto, quar) { return MUD(c, x => { const n0 = x.movs.length; if (apto > 0) cenReceber(x, CX, 'CX26-02', apto, 'un', 'Packing', '—', 'NF 7731', true, RU); if (quar > 0) cenReceber(x, CX, 'CX26-02', quar, 'un', 'Packing', '—', 'NF 7731', false, RU);
  x.movs[n0].estRec = { id: 'r7731', nf: 'NF 7731', ped: 'PC-096 · ' + CX + ' · Embalagens Açu', conf: apto + quar, apto, quar, lote: 'CX26-02' }; }); }
T3('U49a', () => { const c = NOVO(); MUD(c, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG)); NF_PARTE(c, 1100, 100);
  const im = CXIMP(c, n.id); const lv = MUD(c, x => benAutorizarLiberar(x, n.id, IG));
  ok('U49a NF 7731 conferida com 1.100 aptas e 100 em quarentena, CX26-01 com 600: 1.700 livres no total, sem impedimento; a liberação grava REQ-041 1.100 (CX26-02) e REQ-042 69 (CX26-01)',
     !im.t && !lv.erro && O(c, n.id).etapa === 'Liberadas' && JSON.stringify(LINHAS(c, n.id)) === '[["REQ-041","CX26-02",1100],["REQ-042","CX26-01",69]]' && LOT(c, 'CX26-02').reservado === 1100 && LOT(c, 'CX26-01').reservado === 69, [im.t, lv, O(c, n.id).req && LINHAS(c, n.id)]); });
T3('U49b', () => { const c = NOVO(); const z = CAD(c, [SA(800, 8480), SD(3500)]); const s = SOB(c, z.id); const d = MUD(c, x => cenDevolver(x, 'REQ-041', CX, typeof s === 'number' ? s : 0, true, RU));
  const im = CXIMP(c, 'OB-0112'); const lv = MUD(c, x => benAutorizarLiberar(x, 'OB-0112', IG));
  ok('U49b a sobra de 289 da OB-0113 recebida volta ao CX26-02 (o lote de origem) e o livre total chega a 920 ≥ 881: a OB-0112 libera (antes: recusa, o lote do CX26-01 só tinha 600)',
     s === 289 && !d.erro && !im.t && !lv.erro && O(c, 'OB-0112').etapa === 'Liberadas' && SOMA(c, 'OB-0112', x => x.it.solicitado) === 881, [s, d, im.t, lv]); });
T3('U49c', () => { const c = NOVO(); RECEBE_NF(c, 1200); MUD(c, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 24120 }] }, IG)); const im = CXIMP(c, n.id);
  ok('U49c L39-131 (2.292 un) com 600 + 1.200 livres em dois lotes: "1.800 un disponíveis" e "Faltam 492" (antes 1.200 e 1.092)', /1\.800 un disponíveis para 2\.292 un/.test(im.t || '') && /^Faltam 492 un/.test((im.link || {}).why || ''), im); });
T3('U49d', () => { const mk = cx => { const c = NOVO(); c.lotes[CX + '|CX26-01'].fisico = 500; MUD(c, x => cenReceber(x, CX, 'QA-CX-02', 420, 'un', 'Packing', '—', 'NF-QA-420', true, RU)); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }], cx }, IG)); return { c, id: n.id }; };
  const a = mk(900); const lt0 = LIVRE(a.c); const la = MUD(a.c, x => benAutorizarLiberar(x, a.id, IG)); const b = mk(921); const r0 = JSON.stringify(b.c.lotes); const lb = MUD(b.c, x => benAutorizarLiberar(x, b.id, IG));
  ok('U49d reprodução 2 do Codex (500 + 420 livres): livre total 920; liberar 900 grava as linhas 500 (CX26-01) e 400 (QA-CX-02); liberar 921 é recusado sem nenhuma reserva',
     lt0 === 920 && !la.erro && JSON.stringify(LINHAS(a.c, a.id)) === '[["REQ-041","CX26-01",500],["REQ-042","QA-CX-02",400]]' && !!lb.erro && JSON.stringify(b.c.lotes) === r0 && !O(b.c, b.id).req, [lt0, la, O(a.c, a.id).req && LINHAS(a.c, a.id), lb]); });
T3('U49e', () => { /* a ordem do L39-132 com 540 caixas do CX26-01, todas usadas (como a OB540, sem as 1.000 do QA-CX-02) */
  const c = NOVO(); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }], cx: 540 }, IG)); const z = { id: n.id };
  [x => benAutorizarLiberar(x, n.id, IG), x => cenEntregar(x, 'REQ-041', CX, 540, 'Igor', RU), x => benIniciar(x, n.id, IG), x => benSaida(x, n.id, SA(540, 5724), IG)].forEach(f => MUD(c, f));
  const g = [MUD(c, x => cenReceber(x, CX, 'QA-CX-02', 540, 'un', 'Packing', '—', 'NF-QA-540', true, RU)), MUD(c, x => cenReceber(x, CX, 'QA-CX-03', 100, 'un', 'Packing', '—', 'NF-QA-100', true, RU))];
  const p = MUD(c, x => benComplementar(x, z.id, 600, IG, { chave: 'W-BNX-49E' }));
  ok('U49e complemento de 600 com 640 livres em dois lotes (QA-CX-02 540, QA-CX-03 100; nenhum cobre sozinho): duas linhas novas, 540 + 60 (antes: "Pedir 600 un: 540 un livres")',
     g.every(y => !y.erro) && LOT(c, 'CX26-01').fisico === 0 && !p.erro && JSON.stringify(LINHAS(c, z.id)) === '[["REQ-041","CX26-01",540],["REQ-042","QA-CX-02",540],["REQ-043","QA-CX-03",60]]' && O(c, z.id).ins[0].tot === 1140 && LOT(c, 'QA-CX-02').reservado === 540 && LOT(c, 'QA-CX-03').reservado === 60, [p, LINHAS(c, z.id)]); });
T3('U49f', () => { const c = NOVO(); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG)); NF_PARTE(c, 500, 600); const im = CXIMP(c, n.id); const l = im.link || {};
  const lq = MUD(c, x => cenLiberarQuarentena(x, CX + '|CX26-02', 'LAUDO-49F', AN)); const im2 = CXIMP(c, n.id); const lv = MUD(c, x => benAutorizarLiberar(x, n.id, IG));
  ok('U49f 600 caixas em quarentena no CX26-02: a falta (1.040 para 1.169) cita o lote, a quantidade e quem libera (Ana, com o laudo); liberada a quarentena, a ordem libera',
     /1\.040 un disponíveis para 1\.169 un/.test(im.t || '') && /600 un em quarentena no CX26-02: se a inspeção aprovar, Ana \(gestora\) libera com o laudo em Estoque › Confira saldos/.test(l.why || '') && !lq.erro && !im2.t && !lv.erro, [im, lq, im2.t, lv]); });

// ---- U50 · S4: mutantes da rodada 2 que sobreviviam (A1 piso no teto, A6 a própria ordem como fonte) e as fontes estruturadas (I-f1) ----
T3('U50a', () => { const c = NOVO(); const z = CAD(c, [SA(300, 3180), SD(1995)]);
  ok('U50a 7.305 kg a registrar: o teto é ⌈730,5⌉ = 731 caixas e a sobra de 869 é 138 (com o piso seria 139)', z.st.every(y => !y.erro) && SOB(c, z.id) === 138, SOB(c, z.id)); });
T3('U50b', () => { const c = NOVO(); MUD(c, x => cenReceber(x, CX, 'QA-CX-02', 1200, 'un', 'Packing', '—', 'NF-QA-1200', true, RU)); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG));
  const st = [MUD(c, x => benAutorizarLiberar(x, n.id, IG)), MUD(c, x => cenEntregar(x, 'REQ-041', CX, 1169, null, RU)), MUD(c, x => benIniciar(x, n.id, IG)), MUD(c, x => benSaida(x, n.id, SA(1100, 11660), IG)), MUD(c, x => benSaida(x, n.id, SD(1300), IG))];
  const k1 = CXIMP(c, 'OB-0112').link || {}; const tp = f => (f || []).map(x => x.tipo + ':' + (x.os || x.id || x.lote) + ':' + x.qtd);
  const n2 = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-131', kg: 24120 }] }, IG)); const k3 = CXIMP(c, n2.id).link || {};
  MUD(c, x => benRetirar(x, 'OB-0112', 'L39-119', IG)); const k2 = CXIMP(c, 'OB-0112').link || {};
  ok('U50b fontes estruturadas: falta 310 com sobras de 69 (OB-0113) e 60 (OB-0110) e a NF de 1.200: vale a nota, que cobre sozinha; falta 13: vale a maior sobra (OB-0113), com o atalho guiado; falta 1.721: todas (cobre = não, "Ainda faltam 392 un")',
     st.every(y => !y.erro) && k1.falta === 310 && JSON.stringify(tp(k1.fontes)) === '["nf:NF 7731:1200"]' && k1.cobre === true && k1.t === 'Conferir a NF 7731 das caixas no Estoque'
     && k2.falta === 13 && JSON.stringify(tp(k2.fontes)) === '["sobra:OB-0113:69"]' && k2.cobre === true && /^EST\.dc\.html#dev=REQ-041&para=OB-0112&ver=\d+&sob=69$/.test(k2.h || '')
     && k3.falta === 1721 && JSON.stringify(tp(k3.fontes)) === '["sobra:OB-0113:69","sobra:OB-0110:60","nf:NF 7731:1200"]' && k3.cobre === false && /Ainda faltam 392 un/.test(k3.why || ''),
     [st.map(y => y.erro || ''), [k1.falta, tp(k1.fontes), k1.t], [k2.falta, tp(k2.fontes), k2.h], [k3.falta, tp(k3.fontes), k3.cobre, k3.why]]); });
T3('U50c', () => { const c = NOVO(); const p = MUD(c, x => benComplementar(x, 'OB-0110', 700, IG, { chave: 'W-BNX-50C' }));
  ok('U50c a OB-0110 (sobra 60) pede 700 com 540 livres: recusado, e a recusa não cita a própria ordem como fonte', /^Pedir 700 un: 540 un livres no Estoque/.test(p.erro || '') && !/OB-0110 tem sobra/.test(p.erro || ''), p); });

// ---- U51 · rodada 1 (S3, relacionado): o Fechar baixa a reserva não entregue (antes ficava presa no lote) ----
T3('U51', () => { const c = NOVO(); const id = OB113(c); const st = [MUD(c, x => benComplementar(x, id, 5, IG, { chave: 'W-BNX-51' })), MUD(c, x => benSaida(x, id, SA(1000, 10600), IG)), MUD(c, x => benSaida(x, id, SA(169, 1791.4, 'B'), IG)),
    MUD(c, x => benSaida(x, id, SD(610), IG)), MUD(c, x => benConcluir(x, id, IG)), MUD(c, x => benConferir(x, id, PA)), MUD(c, x => benFechar(x, id, IG))];
  const mv = c.movs.filter(m => m.tipo === 'reserva-baixa' && m.req === 'REQ-041');
  ok('U51 pedir 5, usar as 1.169 entregues e fechar: a reserva das 5 não entregues é baixada (movimento reserva-baixa), CX26-02 com reserva 0 e a REQ-041 sem "a entregar" (antes: físico 31, reserva 5)',
     st.every(y => !y.erro) && O(c, id).etapa === 'Encerradas' && LOT(c, 'CX26-02').reservado === 0 && PEND(REQ(c, 'REQ-041')) === 0 && OWN(c, 'REQ-041') === 0 && mv.length === 1 && mv[0].qtd === 5, [st.map(y => y.erro || ''), LOT(c, 'CX26-02'), REQ(c, 'REQ-041'), mv]); });

// ---- U52 · limite adicional do Codex: devolução válida → outra ordem reserva → estorno do descarte. O estorno passa, a outra ordem fica
//      intacta e a falta nasce na própria ordem, com a recuperação da fase (Pedir mais caixas; em conferência, Reabrir a execução) ----
T3('U52a', () => { const c = NOVO(); const z = PARCIAL(c); const id = z.id; const q = DEVP(c, id, 'REQ-041');
  const d = MUD(c, x => cenDevolver(x, 'REQ-041', CX, typeof q === 'number' && q > 0 ? q : REQ(c, 'REQ-041').custodia, true, RU)); const nf = MUD(c, x => cenReceber(x, CX, 'QA-CX-02', 120, 'un', 'Packing', '—', 'NF-QA-120', true, RU));
  const lv = MUD(c, x => benAutorizarLiberar(x, 'OB-0112', IG)); const b0 = JSON.stringify(LINHAS(c, 'OB-0112')); const e = MUD(c, x => benEstornar(x, id, 'S-02', 'Pesagem refeita', '', IG));
  const nx = benProx(c, O(c, id)); const ss = benSelos(c, O(c, id)).map(s => s.t); const f0 = FALTA(c, id);
  const p1 = MUD(c, x => benComplementar(x, id, 139, IG, { chave: 'W-BNX-52A' })); const p2 = MUD(c, x => benComplementar(x, id, 9, IG, { chave: 'W-BNX-52B' })); const f1 = FALTA(c, id);
  ok('U52a sobra de 139 recebida, a OB-0112 libera com ela, e a OB-0113 estorna o descarte de 2.000 kg: o estorno passa, a OB-0112 fica intacta, a OB-0113 mostra "Faltam 139 caixas" com Pedir mais caixas; pedir 139 com 9 livres é recusado, pedir 9 é aceito',
     q === 139 && !d.erro && !lv.erro && !e.erro && JSON.stringify(LINHAS(c, 'OB-0112')) === b0 && f0 === 139 && /Faltam 139 caixas/.test(nx.nota || '') && /Pedir mais caixas/.test(nx.nota || '')
     && ss.indexOf('Faltam 139 caixas') >= 0 && !!p1.erro && !p2.erro, [q, d, lv, e, f0, nx, ss, p1, p2]);
  /* revisão A1 (S2): a reposição baixa a falta. Antes, pedir 9 deixava 139 e pedir a falta inteira deixava "Faltam 61" (o pedido entrava no planejado) */
  const nfy = MUD(c, x => cenReceber(x, CX, 'CX26-01', 1000, 'un', 'Packing', '—', 'NF-Y', true, RU)); const p3 = MUD(c, x => benComplementar(x, id, 130, IG, { chave: 'W-BNX-52C' })); const f2 = FALTA(c, id);
  const s2 = benSelos(c, O(c, id)).map(s => s.t); const n2 = benProx(c, O(c, id)).nota || ''; const p4 = MUD(c, x => benComplementar(x, id, 10, IG, { chave: 'W-BNX-52D' })); const f3 = FALTA(c, id);
  ok('U52a2 revisão A1: pedir 9 baixa a falta a 130; pedir as 130 a zera (sem selo nem nota "Faltam"); um pedido acima da falta (10) é planejamento e não recria falta',
     f1 === 130 && !nfy.erro && !p3.erro && f2 === 0 && !s2.some(t => /Faltam/.test(t)) && !/Faltam/.test(n2) && !p4.erro && f3 === 0, [f1, nfy.erro, p3.erro, f2, s2, n2, p4.erro, f3]); });
T3('U52c', () => { /* revisão A1: avaria de caixas em uso → pedir a falta → zero, também depois de usar as caixas com o descarte ainda por pesar (o caso da C-1) */
  const c = NOVO(); const z = CAD(c, [SA(500, 5300)]); const id = z.id; const d = MUD(c, x => cenDevolver(x, 'REQ-041', CX, 50, false, RU)); const f0 = FALTA(c, id);
  const p = MUD(c, x => benComplementar(x, id, f0, IG, { chave: 'W-BNX-52E' })); const f1 = FALTA(c, id);
  const en = benLinhas(c, O(c, id)).map(x => { const q = cenSaldoEntregar(x.it); return q > 0 ? MUD(c, y => cenEntregar(y, x.rid, CX, q, null, RU)) : {}; }); const f2 = FALTA(c, id);
  const u = MUD(c, x => benSaida(x, id, SA(669, 7091.4, 'B'), IG)); const f3 = FALTA(c, id); const ss = benSelos(c, O(c, id)).map(s => s.t);
  ok('U52c avaria de 50 caixas em uso: falta 50; pedir 50 a zera; entregues, 0; usadas as 669 com 610 kg ainda por pesar, 0 (antes: "Faltam 50 caixas")',
     z.st.every(y => !y.erro) && !d.erro && f0 === 50 && !p.erro && f1 === 0 && en.every(y => !y.erro) && f2 === 0 && !u.erro && f3 === 0 && !ss.some(t => /Faltam/.test(t)), [z.st.map(y => y.erro || ''), d, f0, p.erro, f1, en, f2, u.erro, f3, ss]); });
T3('U52b', () => { const c = NOVO(); const z = PARCIAL(c); const id = z.id; const cc = MUD(c, x => benConcluir(x, id, IG)); const q = DEVP(c, id, 'REQ-041');
  const d = MUD(c, x => cenDevolver(x, 'REQ-041', CX, typeof q === 'number' && q > 0 ? q : REQ(c, 'REQ-041').custodia, true, RU)); const e = MUD(c, x => benEstornar(x, id, 'S-02', 'Pesagem refeita', '', IG));
  const nx = benProx(c, O(c, id)); const sx = MUD(c, x => benSaida(x, id, Object.assign(SA(800, 8480), { motivo: 'teste', subst: 'S-02' }), IG));
  ok('U52b o mesmo em conferência: o Estoque traz a sobra (139, o kg aberto passa da faixa); o estorno do descarte passa; o painel mostra "Faltam 139 caixas" com Reabrir a execução; a recusa da saída acima da custódia manda reabrir',
     !cc.erro && q === 139 && !d.erro && !e.erro && FALTA(c, id) === 139 && /Faltam 139 caixas/.test(nx.nota || '') && /Reabrir a execução/.test(nx.nota || '') && /Reabrir a execução/.test(sx.erro || '') && !/entrega no balcão/.test(sx.erro || ''), [cc, q, d, e, FALTA(c, id), nx, sx]); });

// ---- U54 · o falso alarme da crítica (C-1): no roteiro do proprietário e na cadeia não falta caixa em nenhum passo ----
T3('U54', () => { const c = NOVO(); const id = OB113(c); const f = [], sel = [], nt = [];
  [SA(1000, 10600), SA(169, 1791.4, 'B')].forEach(k => { MUD(c, x => benSaida(x, id, k, IG)); f.push(FALTA(c, id)); sel.push(benSelos(c, O(c, id)).map(s => s.t).join('|')); nt.push(benProx(c, O(c, id)).nota || ''); });
  const c2 = NOVO(); const z = CAD(c2, [SA(1100, 11660)]); f.push(FALTA(c2, z.id));
  ok('U54 roteiro do proprietário depois da S-01 (A 1.000 cx) e da S-02 (B 169 cx), e a cadeia depois do A 1.100 cx: nenhuma falta (0, 0, 0; com a fórmula pela necessidade da rota daria 50, 58 e 55)',
     JSON.stringify(f) === '[0,0,0]' && sel.every(s => !/Faltam/.test(s)) && nt.every(s => !/Faltam/.test(s)), [f, sel, nt]); });

// ---- U55 · C-2: ajuste de inventário aprovado depois da reserva (físico 1.100, reserva 1.169): a trava física continua (nunca estoque negativo)
//      e o painel avisa a reserva sem físico ----
T3('U55', () => { const c = NOVO(); const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG)); RECEBE_NF(c, 1200); const K2 = CX + '|CX26-02';
  const ct = MUD(c, x => cenContar(x, K2, 1100)); const lv = MUD(c, x => benAutorizarLiberar(x, n.id, IG)); const aj = (c.ajustes || []).slice(-1)[0] || {}; const ap = MUD(c, x => cenAprovarAjuste(x, aj.id, true, AN));
  const e = MUD(c, x => cenEntregar(x, 'REQ-041', CX, 1169, null, RU)); const nx = benProx(c, O(c, n.id));
  ok('U55 contagem de 1.100 aprovada depois da reserva de 1.169: a entrega de 1.169 é recusada e o físico fica em 1.100 (sem a trava física iria a −69); o painel diz "Reserva sem físico: 69 caixas da REQ-041"',
     !ct.erro && !lv.erro && !ap.erro && LOT(c, 'CX26-02').fisico === 1100 && !!e.erro && LOT(c, 'CX26-02').fisico === 1100 && /Reserva sem físico: 69 caixas da REQ-041/.test(nx.nota || ''), [ct, lv, ap, e, LOT(c, 'CX26-02'), nx]); });

// ---- U56 · C-10: o gancho da devolução falha fechado: sem a regra do beneficiamento na página, a linha BEN não é devolvida (nada gravado) ----
T3('U56', () => { /* o cenDevolver da página sem o ben.js: a mesma função, montada num escopo em que benSobraDev não existe */
  const c = NOVO(); const semBen = new Function('cenQuem', 'cenNum', 'cenMov', 'benAposDevolver', 'benSobraDev', 'return ' + cenDevolver.toString())(cenQuem, cenNum, cenMov, typeof benAposDevolver === 'function' ? benAposDevolver : undefined, undefined);
  const r = MUD(c, x => semBen(x, 'REQ-030', CX, 60, true, RU));
  ok('U56 sem benSobraDev a devolução da REQ-030 (OB-0110) é recusada sem gravar ("regra do beneficiamento ausente")', !!(r && r.erro) && /beneficiamento/.test(r.erro) && REQ(c, 'REQ-030').custodia === 60 && LOT(c, 'CX26-01').fisico === 540, r); });

// ---- U57 · rodada 3, integração na v56: regras do desenho que nenhum teste de unidade prendia (sonda de mutantes X10-X24 sobreviveu). Cada
//      caso reprova no 3f9e4f6 e mata um mutante novo (M96-M102) ----
T3('U57a', () => { /* I-e4/I-a4: a reserva baixada no Fechar não volta como reserva própria da linha encerrada quando outra ordem reserva no lote */
  const c = NOVO(); const id = OB113(c); const st = [MUD(c, x => benComplementar(x, id, 5, IG, { chave: 'W-BNX-57A' })), MUD(c, x => benSaida(x, id, SA(1000, 10600), IG)), MUD(c, x => benSaida(x, id, SA(169, 1791.4, 'B'), IG)),
    MUD(c, x => benSaida(x, id, SD(610), IG)), MUD(c, x => benConcluir(x, id, IG)), MUD(c, x => benConferir(x, id, PA)), MUD(c, x => benFechar(x, id, IG))];
  const rt = cenResTot(c, 'REQ-041', CX);
  const lib = [MUD(c, x => benResultado(x, 'L39-119', 'Conforme', '', MA)), MUD(c, x => benDecidir(x, 'L39-119', 'Liberar', {}, MA)), MUD(c, x => cenReceber(x, CX, 'CX26-02', 1000, 'un', 'Packing', '—', 'NF-QA-57A', true, RU)),
    MUD(c, x => benAutorizarLiberar(x, 'OB-0112', IG))];
  ok('U57a pedir 5, usar 1.169 e fechar (reserva-baixa de 5): a reserva total da REQ-041 é 1.169 (1.174 reservadas − 5 baixadas); a OB-0112 reserva 881 no CX26-02 e a REQ-041 encerrada continua sem reserva própria (0)',
     st.every(y => !y.erro) && rt === 1169 && lib.every(y => !y.erro) && LOT(c, 'CX26-02').reservado === 881 && OWN(c, 'REQ-041') === 0, [st.map(y => y.erro || ''), rt, lib.map(y => y.erro || ''), LOT(c, 'CX26-02'), OWN(c, 'REQ-041')]); });
T3('U57b', () => { /* I-d2 na REQ da semente (REQ-030 Entregue, 1.200): a caixa em uso devolvida volta reservada a ela, e a entrega seguinte baixa essa reserva */
  const c = NOVO(); const e = MUD(c, x => benEstornar(x, 'OB-0110', 'S-03', 'Pesagem refeita', '', IG)); const s = SOB(c, 'OB-0110');
  const d = MUD(c, x => cenDevolver(x, 'REQ-030', CX, 60, true, RU)); const it = REQ(c, 'REQ-030'); const p = PEND(it), w = OWN(c, 'REQ-030'); const l0 = JSON.stringify([LOT(c, 'CX26-01').fisico, LOT(c, 'CX26-01').reservado]);
  const en = MUD(c, x => cenEntregar(x, 'REQ-030', CX, 60, null, RU));
  ok('U57b OB-0110 estorna o descarte de 600 kg (sobra 0) e devolve as 60 caixas em uso: voltam reservadas à REQ-030 (a entregar = reserva própria = 60; CX26-01 físico 600, reserva 60); entregues de novo, a reserva volta a 0',
     !e.erro && s === 0 && !d.erro && p === 60 && w === 60 && l0 === '[600,60]' && !en.erro && LOT(c, 'CX26-01').fisico === 540 && LOT(c, 'CX26-01').reservado === 0 && OWN(c, 'REQ-030') === 0,
     [e, s, d, p, w, l0, en, LOT(c, 'CX26-01')]); });
T3('U57c', () => { /* regra de divisão, avaria: tudo à quarentena e fora do "a entregar"; a falta nasce como benFaltaCx (Pedir mais caixas), nunca como entrega sem reserva */
  const c = NOVO(); const z = PARCIAL(c); const L0 = LIVRETOT(c); const q0 = LOT(c, 'CX26-02').quarentena || 0;
  const d = MUD(c, x => cenDevolver(x, 'REQ-041', CX, 200, false, RU)); const it = REQ(c, 'REQ-041'); const en = MUD(c, x => cenEntregar(x, 'REQ-041', CX, 61, null, RU));
  ok('U57c 200 caixas avariadas da OB-0113 em execução (custódia 869, teto 730): vão à quarentena, saem do "a entregar" (0 = reserva própria), o livre não muda e a falta é 61; entregar 61 sem reserva é recusado',
     !d.erro && it.custodia === 669 && (LOT(c, 'CX26-02').quarentena || 0) - q0 === 200 && LIVRETOT(c) === L0 && PEND(it) === 0 && OWN(c, 'REQ-041') === 0 && FALTA(c, z.id) === 61 && !!en.erro,
     [d, it, LOT(c, 'CX26-02'), PEND(it), OWN(c, 'REQ-041'), FALTA(c, z.id), en]); });
T3('U57d', () => { /* I-f2: em conferência não entra caixa; a recuperação sem fonte que cubra manda Reabrir a execução, nunca Cancelar */
  const c = NOVO(); const z = PARCIAL(c); const cc = MUD(c, x => benConcluir(x, z.id, IG)); const w = benCaixasRec(c, O(c, z.id), 0, 10000).why || '';
  ok('U57d recuperação de uma ordem em conferência sem fonte que cubra: diz "Reabrir a execução" e não "Cancelar a ordem"', !cc.erro && O(c, z.id).etapa === 'Em conferência' && /Reabrir a execução/.test(w) && !/Cancelar a ordem/.test(w), [cc, w]); });
T3('U57e', () => { /* I-a1 no selo: "Sobra em custódia" só com sobra provada */
  const c = NOVO(); const z = CAD(c, [SA(1000, 10600), SA(169, 1791.4, 'B'), SD(610)]); const id = z.id;
  const st = [MUD(c, x => benConcluir(x, id, IG)), MUD(c, x => benConferir(x, id, PA)), MUD(c, x => benEstornar(x, id, 'S-01', 'Pesagem refeita', '', IG))]; const s1 = benSelos(c, O(c, id)).map(s => s.t);
  const c2 = NOVO(); const a = MUD(c2, x => benConcluir(x, 'OB-0110', IG)); const s2 = benSelos(c2, O(c2, 'OB-0110')).map(s => s.t);
  ok('U57e selo "Sobra em custódia": a OB-0113 em conferência com a S-01 estornada (1.000 em custódia, sobra 0) não o mostra; a OB-0110 com tudo registrado (sobra 60) mostra',
     st.every(y => !y.erro) && REQ(c, 'REQ-041').custodia === 1000 && s1.indexOf('Sobra em custódia') < 0 && !a.erro && s2.indexOf('Sobra em custódia') >= 0, [st.map(y => y.erro || ''), s1, a, s2]); });
T3('U57f', () => { /* I-a1 com a conferência dada: o kg aberto continua valendo (um estorno derruba a conferência e a ordem volta a precisar das caixas) */
  const c = NOVO(); const z = CAD(c, [SA(1000, 10600), SD(610)]); const id = z.id;
  const st = [MUD(c, x => benConcluir(x, id, IG)), MUD(c, x => benJustificar(x, id, 'Perda não identificada', 'teste U57f', AN)), MUD(c, x => benConferir(x, id, PA))];
  const l = CXIMP(c, 'OB-0112').link || {}; const q = DEVP(c, id, 'REQ-041');
  ok('U57f "faltou a classe B" justificada e conferida (1.690 kg abertos, 169 caixas em custódia): a sobra continua 0 e a OB-0112 não aponta a OB-0113; para o Fechar o Estoque traz a custódia inteira (169)',
     st.every(y => !y.erro) && !!O(c, id).ben.conf && SOB(c, id) === 0 && !/OB-0113/.test((l.why || '') + (l.t || '')) && q === 169, [st.map(y => y.erro || ''), SOB(c, id), l, q]); });
T3('U57g', () => { /* I-f1: todas as notas a conferir são fontes (nenhuma cobre sozinha: entram todas, com a sobra) */
  const nf0 = BENC.nfcx; try { BENC.nfcx = [{ id: 'NF 9101', rid: 'r9101', ped: 'PC-201', forn: 'Embalagens Teste', qtd: 200, lote: 'QA-CX-02' }, { id: 'NF 9102', rid: 'r9102', ped: 'PC-202', forn: 'Embalagens Teste', qtd: 200, lote: 'QA-CX-03' }];
    const c = NOVO(); const l = CXIMP(c, 'OB-0112').link || {}; const tp = (l.fontes || []).map(f => f.tipo + ':' + (f.os || f.id) + ':' + f.qtd);
    ok('U57g duas notas de caixa a conferir (200 + 200) e a sobra de 60 da OB-0110 para a falta de 341 da OB-0112: nenhuma cobre sozinha e a recomendação traz as três (Σ 460, cobre)',
       l.falta === 341 && JSON.stringify(tp) === '["sobra:OB-0110:60","nf:NF 9101:200","nf:NF 9102:200"]' && l.cobre === true, [l.falta, tp, l.cobre]); } finally { BENC.nfcx = nf0; } });

// ---- U58 · revisão A2 (S2): caixas em uso devolvidas "bloqueadas para inspeção" continuam da ordem. Não viram fonte de outra ordem; se o
//      laudo aprova, voltam reservadas à linha até a falta dela. Antes: a OB-0114 era mandada liberar a quarentena e levava as caixas da OB-0113 ----
function QUAR300(c) { const id = OB113(c); const st = [MUD(c, x => benSaida(x, id, SA(500, 5300), IG)), MUD(c, x => cenDevolver(x, 'REQ-041', CX, 300, false, RU))]; return { id, st }; }
T3('U58a', () => { const c = NOVO(); const z = QUAR300(c); const id = z.id; const f0 = FALTA(c, id);
  const nb = MUD(c, x => benNova(x, { lotes: [{ lote: 'L38-132', kg: prFis(x, 'L38-132') }], cx: 800 }, IG)); const im = CXIMP(c, nb.id); const l = im.link || {};
  const lq = MUD(c, x => cenLiberarQuarentena(x, CX + '|CX26-02', 'LAUDO-58A', AN)); const it = REQ(c, 'REQ-041'); const f1 = FALTA(c, id); const im2 = CXIMP(c, nb.id);
  const lb = MUD(c, x => benAutorizarLiberar(x, nb.id, IG));
  ok('U58a OB-0113 devolve 300 caixas em uso bloqueadas: falta 300; a OB-0114 (800) não recebe a quarentena como fonte; com o laudo, as 300 voltam reservadas à REQ-041 (falta 0, a entregar = reserva própria = 300) e a OB-0114 continua impedida',
     z.st.every(y => !y.erro) && f0 === 300 && !!im.t && !(l.fontes || []).some(f => f.tipo === 'quarentena') && !/quarentena no CX26-02/.test(l.why || '') && !lq.erro && /300 un voltam reservadas à OB-0113/.test(lq.msg || '')
     && f1 === 0 && PEND(it) === 300 && OWN(c, 'REQ-041') === 300 && LOT(c, 'CX26-02').reservado === 300 && !!im2.t && !!lb.erro && !O(c, nb.id).req,
     [z.st.map(y => y.erro || ''), f0, l.fontes, l.why, lq, f1, PEND(it), OWN(c, 'REQ-041'), LOT(c, 'CX26-02'), im2.t, lb.erro]); });
T3('U58b', () => { const c = NOVO(); const z = QUAR300(c); const id = z.id; const p = MUD(c, x => benComplementar(x, id, 300, IG, { chave: 'W-BNX-58B' })); const f0 = FALTA(c, id); const L0 = LIVRETOT(c);
  const lq = MUD(c, x => cenLiberarQuarentena(x, CX + '|CX26-02', 'LAUDO-58B', AN)); const f1 = FALTA(c, id);
  const c2 = NOVO(); QUAR300(c2); const rp = MUD(c2, x => cenReprovarQuarentena(x, CX + '|CX26-02', 'LAUDO-REP-58', 'caixas quebradas', AN)); const qu = REQ(c2, 'REQ-041').quarUso || 0;
  ok('U58b a OB-0113 já pediu as 300 antes do laudo: o laudo solta as 300 no livre (nada volta reservado, falta 0); com o laudo reprovado, o vínculo com a linha se desfaz',
     !p.erro && f0 === 0 && !lq.erro && !/voltam reservadas/.test(lq.msg || '') && f1 === 0 && LIVRETOT(c) - L0 === 300 && !rp.erro && qu === 0, [p.erro, f0, lq, f1, LIVRETOT(c) - L0, rp, qu]); });

// ---- U59 · revisão A3 (S3): quarentena reprovada (quarRep, CTL-4) não é fonte. Antes: "700 un em quarentena: se a inspeção aprovar…", cobre,
//      e o Estoque recusava liberar ("só tem material reprovado") ----
T3('U59', () => { const NFQ = NF_PARTE;   /* a NF 7731 conferida com parte apta e parte em quarentena */
  const c = NOVO(); NFQ(c, 500, 700); const rp = MUD(c, x => cenReprovarQuarentena(x, CX + '|CX26-02', 'LAUDO-REP', 'caixas mofadas', AN));
  const n = MUD(c, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG)); const l = CXIMP(c, n.id).link || {};
  const c2 = NOVO(); NFQ(c2, 500, 200); MUD(c2, x => cenReprovarQuarentena(x, CX + '|CX26-02', 'LAUDO-REP', 'mofo', AN)); const d2 = MUD(c2, x => cenDevolver(x, 'REQ-030', CX, 30, false, RU));
  const n2 = MUD(c2, x => benNova(x, { lotes: [{ lote: 'L39-132', kg: 12300 }] }, IG)); const l2 = CXIMP(c2, n2.id).link || {}; const q2 = (l2.fontes || []).filter(f => f.tipo === 'quarentena').map(f => f.lote + ':' + f.qtd);
  ok('U59 com as 700 un do CX26-02 reprovadas, a recomendação não cita a quarentena nem leva a "Ver a quarentena" (cobre só com fonte real); com 200 reprovadas no CX26-02 e 30 pendentes no CX26-01, a fonte é só CX26-01 30',
     !rp.erro && !(l.fontes || []).some(f => f.tipo === 'quarentena') && !/quarentena no CX26-02/.test(l.why || '') && l.t !== 'Ver a quarentena das caixas no Estoque' && l.cobre === false
     && !d2.erro && JSON.stringify(q2) === '["CX26-01:30"]', [rp.erro, l.fontes, l.t, l.cobre, d2.erro, q2]); });

// ---- U60 · revisão A7 (S4): a mensagem da devolução segue a fase. Ordem conferida (perda justificada): o que volta reservado fica até o Fechar,
//      não é "caixas em uso"; em execução o texto continua "caixas em uso" ----
T3('U60', () => { const c = NOVO(); const z = CAD(c, [SA(1100, 11660)]); const id = z.id;
  const st = [MUD(c, x => benConcluir(x, id, IG)), MUD(c, x => benJustificar(x, id, 'Perda não identificada', 'fruta mole retirada', AN)), MUD(c, x => benConferir(x, id, PA))];
  const q = DEVP(c, id, 'REQ-041'); const d = MUD(c, x => cenDevolver(x, 'REQ-041', CX, q, true, RU)); const mv = c.movs.filter(m => m.tipo === 'reserva' && m.req === 'REQ-041').pop() || {};
  const c2 = NOVO(); const z2 = PARCIAL(c2); const d2 = MUD(c2, x => cenDevolver(x, 'REQ-041', CX, 869, true, RU));
  ok('U60 conferida com 1.200 kg justificados: devolvidas as 69, "69 un ficam reservadas à OB-0113 até o Fechar" (sem "caixas em uso"); em execução a mensagem continua "caixas em uso"',
     st.every(y => !y.erro) && q === 69 && !d.erro && /69 un ficam reservadas à OB-0113 até o Fechar/.test(d.msg || '') && !/caixas em uso/.test(d.msg || '') && !/caixas em uso/.test(mv.det || '')
     && !d2.erro && /730 un voltam reservadas à OB-0113 \(caixas em uso\)/.test(d2.msg || ''), [st.map(y => y.erro || ''), q, d, mv.det, d2.msg]); });

print(JSON.stringify(R));
