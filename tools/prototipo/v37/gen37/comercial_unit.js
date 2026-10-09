/* Testes puros do Comercial e logística (docs/comercial/ESPECIFICACAO.md §8; contas em docs/comercial/verificacao/contas.py) · node, sem navegador.
   Carregado depois de: perfis + CEN0 + cenario.js + PRDC + producao.js (+ núcleo da carência quando NUCLEO) + PR_UI_JS + PR_PED_JS + COMC + comercial.js.
   Cada verificação vira uma linha do JSON final. Comentários só com barra-asterisco. */
const R = []; function ok(n, c, info) { R.push({ n, ok: !!c, info: c ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 700) }); }
function caso(nome, fn) { try { fn(); } catch (e) { ok(nome + ' (exceção)', false, String(e && e.stack || e).slice(0, 600)); } }
function MUD(c, fn) { const x = cenClone(c); try { const r = fn(x) || {}; Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); return r; } catch (e) { return { erro: String(e.message || e) }; } }
const NOVO = () => cenClone(CEN0);
/* A-17 (Codex 6070584991): a semente deixa a saca dos contratos de soja legados a conferir (VE-05 oculto: sc 50 kg; Colheita D-19: 60 kg).
   Os casos C01..C12 testam outras regras e partem da massa registrada com fonte, como a gestora faria na tela (comConverterSaca); C13 testa a
   semente crua, os 50 kg e a mudança do cadastro da cultura */
const LEGADO = ['PV-030', 'CT-203', 'CRE-0095', 'BT-090'];
function NOVO60() { const c = NOVO(); if (typeof comConverterSaca !== 'function') return c;
  LEGADO.forEach(id => { const r = MUD(c, x => comConverterSaca(x, { venda: id, fat: '60', fonte: 'Contrato ' + id + ' (teste)', ator: 'Ana', chave: 'T-SACA-' + id })); if (r.erro) throw new Error(id + ': ' + r.erro); }); return c; }
const MAM = 'Mamão Formosa · fruta de campo';
const TEM_COM = typeof comVender === 'function';

/* =====================================================================================================================
   R01..R05 · defeitos da base f4121bd reproduzidos antes da correção (sonda_base.py; CE-03, CE-10, R-C10, R-C11)
   ===================================================================================================================== */
if (NUCLEO) {
caso('R01', () => { const c = NOVO(); const n0 = c.producao.movs.length;
  const r = MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 7500 }));
  ok('R01 CE-10 reservar sem quem age (ator) é recusado e nada é gravado', !!r.erro && c.producao.movs.length === n0 && Object.keys(c.producao.reservas).length === 1, [r.erro || r.msg]);
  const r2 = MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 7500, ator: 'Caio' }));
  ok('R01b reservar com perfil sem o papel (Caio · PCP) é recusado: decisão do comercial ou da gestora', /decisão de/.test(r2.erro || '') && Object.keys(c.producao.reservas).length === 1, r2.erro || r2.msg); });
caso('R02', () => { const c = NOVO(); c.producao.movs.push({ id: 'MP-X', tipo: 'expedição', lote: 'L38-131', kg: -30040, pedido: 'PV-038', d: '2026-10-06' });
  const o = prOfertaSem(c, MAM, '2026-W41');
  ok('R02 CE-03 venda futura expedida acima da quantidade (30.040 de 30.000 kg): vendas futuras 0 kg, nunca −40, e a oferta livre não ganha 40 kg', o.futKg === 0 && o.livre === 0, [o.futKg, o.livre]); });
caso('R03', () => { const c = NOVO(); c.producao.movs.push({ id: 'MP-Y', tipo: 'devolução', lote: 'L39-999', kg: 400, pedido: 'PV-037', d: '2026-09-26' });
  ok('R03 R-C10 o expedido da venda desconta a devolução (30.490 − 400 = 30.090 kg)', prExpedido(c, 'PV-037') === 30090, prExpedido(c, 'PV-037')); });
caso('R04', () => { const c = NOVO(); c.producao.pedidos['PV-036'].enc = { motivo: 'cliente desistiu', quem: 'Ana (gestora)', d: '2026-09-26', qtd0: 10000 }; c.producao.pedidos['PV-036'].qtd = 0;
  ok('R04 R-C11 venda com saldo encerrado aparece "Encerrada" (não "Entregue" nem "Sem reserva")', prSitPed(c, c.producao.pedidos['PV-036']).t === 'Encerrada', prSitPed(c, c.producao.pedidos['PV-036']).t); });
caso('R05', () => { const c = NOVO(); const s = prSaldos(c, c.producao.lotes['L10-031']);
  const id = typeof prNovoLote === 'function' ? MUD(c, x => ({ id: prNovoLote(x, '2026-09-26') })).id : '';
  ok('R05 prNovoLote: o mesmo gerador L<semana>-<seq> do recebimento (26/09 = S39 → L39-133)', id === 'L39-133' && s.fis === 2305200, id); });
}

/* =====================================================================================================================
   C01..C12 · critérios de aceite (§8) com os números de contas.py (KC01..KC18). Helpers: a tarefa da Colheita (CG-2108 → L39-133,
   12.050 kg Liberado; RS-0002 de 10.000 kg ao PV-036) e a tarefa do proprietário (§8.1)
   ===================================================================================================================== */
const SC = x => prEstTxt('Soja', x);
function COLHEITA(c, reservar) { const g = MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra', chave: 'T-REC' }));
  if (g.erro) throw new Error('colheita: ' + g.erro); if (reservar !== false) { const r = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 10000, ator: 'Dora', chave: 'T-RS36' })); if (r.erro) throw new Error('reserva PV-036: ' + r.erro); } }
function TAREFA(c, ator) { ator = ator || 'Ana';
  const a = MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 7500, ator, chave: 'T-RS30' }));
  const b = MUD(c, x => comProgramar(x, { venda: 'PV-030', lotes: [{ lote: 'L10-031', prev: comSugPrev(x, 'PV-030', 'Bitrem graneleiro 37 t', 'L10-031') }], veic: 'Bitrem graneleiro 37 t', placa: 'qza1b23', dprev: '2026-09-26', ator, chave: 'T-PG' }));
  const s = MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '51.200', tara: '14.240', ator, chave: 'T-SAI' }));
  return { a, b, s }; }
function PROG(c, vid, lote, prev, veic, ator, chave, transp) { return MUD(c, x => comProgramar(x, { venda: vid, lotes: [{ lote, prev }], veic, transp: transp || 'Rota Sul Transportes', placa: 'ABC1D23', dprev: '2026-09-26', ator: ator || 'Ana', chave })); }
if (TEM_COM && NUCLEO) {
caso('C01', () => {
  ok('C01 AC-02 KC01 616 sc × R$ 128,00/sc = R$ 78.848,00 (36.960 kg)', comValor('Soja', 36960, '128') === 78848 && comTxt('Soja', 36960) === '616 sc' && comRS(comValor('Soja', 36960, '128')) === 'R$ 78.848,00', [comValor('Soja', 36960, '128'), comTxt('Soja', 36960)]);
  ok('C01b mamão em kg e R$/kg (10.000 kg × R$ 3,05/kg = R$ 30.500,00); coco em fruto', comTxt('Mamão Formosa', 10000) === '10.000 kg' && comPrecoTxt('Mamão Formosa', '3.05') === 'R$ 3,05/kg' && comValor('Mamão Formosa', 10000, '3.05') === 30500
     && comUn('Coco') === 'fruto' && comPrecoTxt('Coco', '1.5') === 'R$ 1,50/fruto' && comValor('Coco', 1000, '1.5') === 1500, [comPrecoTxt('Coco', '1.5'), comValor('Coco', 1000, '1.5')]);
  ok('C01c um arredondamento por valor (centavo, meio para cima): 3.333,3 kg × R$ 3,05 = R$ 10.166,57 (10.166,565)', comValor('Mamão Formosa', '3333.3', '3.05') === 10166.57, comValor('Mamão Formosa', '3333.3', '3.05'));
  ok('C01d condição com evento: à vista = 0 d; 28 d após a entrega; antecipado antes da saída', comVenc('À vista na entrega', '2026-09-26') === '2026-09-26' && comVenc('28 dias após a entrega comprovada', '2026-09-17') === '2026-10-15' && comCond('Antecipado').ant && comVenc('Antecipado', '2026-09-26') === '', comVenc('28 dias após a entrega comprovada', '2026-09-17')); });
caso('C02', () => { const c = NOVO60(); const base = { cliente: 'Coop Grão Sul', prod: 'Soja em grão', tipo: 'pronta', ini: '2026-09-28', fim: '2026-10-04', qtd: '1.000', preco: '130,00', ator: 'Dora', chave: 'T-V1' };
  const e0 = MUD(c, x => comVender(x, Object.assign({}, base, { cliente: '', chave: '' }))); const e1 = MUD(c, x => comVender(x, Object.assign({}, base, { qtd: '', chave: '' }))); const e2 = MUD(c, x => comVender(x, Object.assign({}, base, { preco: '0', chave: '' })));
  ok('C02 AC-03 obrigatórios: sem cliente, sem quantidade e preço zero recusados', /CD-05/.test(e0.erro || '') && /quantidade em sc/.test(e1.erro || '') && /preço em R\$\/sc/.test(e2.erro || ''), [e0.erro, e1.erro, e2.erro]);
  const a = MUD(c, x => comVender(x, base)); const v = c.producao.pedidos['PV-039'];
  ok('C02b PV-039: Coop Grão Sul, 1.000 sc (60.000 kg) a R$ 130,00/sc; condição herdada do CD-05 (à vista na entrega) e cliente retira; grava Dora (comercial)', !a.erro && v && v.qtd === 60000 && v.cond === 'À vista na entrega' && v.modal === 'retira' && v.quem === 'Dora (comercial)' && v.classe === 'Padrão' && v.saf === '2025/26' && /R\$ 130\.000,00/.test(a.msg), [a.erro || a.msg, v]);
  const b = MUD(c, x => comVender(x, base)); const d = MUD(c, x => comVender(x, Object.assign({}, base, { qtd: '1.100' })));
  ok('C02c mesma chave e mesmo conteúdo = mesma venda; outro conteúdo = conflito, nada gravado', b.repetido && /conflito/.test(d.erro || '') && Object.keys(c.producao.pedidos).filter(k => /^PV-039/.test(k)).length === 1 && c.producao.seq.pv === 39, [b.msg, d.erro]);
  const f = MUD(c, x => comVender(x, { cliente: 'Coop Grão Sul', prod: 'Soja em grão', tipo: 'futura', saf: '2026/27', qtd: '4000', preco: '133', ator: 'Ana', chave: 'T-V2' }));
  ok('C02d venda futura nova da soja 26/27: CT-205 (o CT-204 é o exemplo do VE-05 oculto)', !f.erro && f.v.id === 'CT-205' && f.v.janela === 'safra 2026/27', f.erro || f.v.id);
  const cz = MUD(c, x => comVender(x, Object.assign({}, base, { chave: 'T-V3', ator: 'Caio' }))); const rz = MUD(c, x => comVender(x, Object.assign({}, base, { chave: 'T-V4', ator: 'Rui' })));
  ok('C02e Caio (PCP) e Rui (almoxarife e expedição) não vendem: decisão do comercial ou da gestora', /Registrar venda: decisão de Ana \(gestora\) ou Dora \(comercial\)/.test(cz.erro || '') && /decisão de/.test(rz.erro || ''), [cz.erro, rz.erro]);
  const cp = comCp('Frutas Real'); const pr = comProdCp(cp);
  ok('C02f CE-06 produto do CD-05 "Mamão Formosa classe A/B" casado pela cultura com o do estado "Mamão Formosa · fruta de campo"; classe vem dos lotes (sem classe)', pr.join() === MAM && comClasse(c, MAM) === '', [cp.prod, pr]);
  const m = MUD(c, x => comVender(x, { cliente: 'Frutas Real', prod: MAM, tipo: 'futura', sem: '2026-W39', qtd: '20000', preco: '3,10', ator: 'Dora', chave: 'T-V5' }));
  const m2 = MUD(c, x => comVender(x, { cliente: 'Frutas Real', prod: MAM, tipo: 'futura', sem: '2026-W42', qtd: '20000', preco: '3,10', ator: 'Dora', chave: 'T-V6' }));
  ok('C02g CE-02 venda futura para a S39 (em curso) recusada; S42 aceita (CT-206, 28 d herdado, agricultor entrega, déficit é aviso)', /S39 já começou/.test(m.erro || '') && !m2.erro && m2.v.id === 'CT-206' && m2.v.cond === '28 dias após a entrega comprovada' && m2.v.modal === 'entrega' && /déficit/.test(m2.msg), [m.erro, m2.erro || m2.msg]);
  const n = MUD(c, x => comVender(x, Object.assign({}, base, { cond: 'Antecipado', chave: 'T-V7' }))); const n2 = MUD(c, x => comVender(x, Object.assign({}, base, { cond: 'Quando der', chave: 'T-V8' })));
  const cpr = MUD(c, x => comVender(x, { cliente: 'Coop Grão Sul', natureza: 'CPR', prod: 'Soja em grão', tipo: 'futura', saf: '2026/27', qtd: '100', preco: '120', ator: 'Ana', chave: 'T-V9' }));
  ok('C02h condição corrigível por toque (Antecipado aceito); condição sem evento recusada; CPR só com fornecedor', !n.erro && n.v.cond === 'Antecipado' && /evento do vencimento/.test(n2.erro || '') && /fornecedor/.test(cpr.erro || ''), [n.erro, n2.erro, cpr.erro]); });
caso('C03', () => { const c = NOVO60(); const T = SC; const of = prOfertaSafra(c, 'Soja em grão', '2026/27');
  ok('C03 AC-04 soja 26/27: oferta 68.180 sc · vendas futuras do estado (CT-203, CRE-0095, BT-090) 19.900 sc · livre 48.280 sc', T(of.pub) === '68.180 sc' && T(of.futKg) === '19.900 sc' && T(of.livre) === '48.280 sc' && of.fut.length === 3, [T(of.livre), of.fut.map(v => v.id)]);
  const f = MUD(c, x => comVender(x, { cliente: 'Coop Grão Sul', prod: 'Soja em grão', tipo: 'futura', saf: '2026/27', qtd: '4000', preco: '133', ator: 'Dora', chave: 'T-F1' }));
  const of2 = prOfertaSafra(c, 'Soja em grão', '2026/27'); const S = prSaldos(c, c.producao.lotes['L10-031']);
  ok('C03b CT-205 de 4.000 sc: livre 44.280 sc; o disponível do L10-031 não muda (34.545 sc)', !f.erro && T(of2.livre) === '44.280 sc' && T(S.disp) === '34.545 sc', [f.erro, T(of2.livre), T(S.disp)]);
  const g = MUD(c, x => comVender(x, { cliente: 'Coop Grão Sul', prod: 'Soja em grão', tipo: 'futura', saf: '2026/27', qtd: '50000', preco: '133', ator: 'Dora', chave: 'T-F2' }));
  ok('C03c acima da oferta livre: registrada com aviso de déficit (D-C16), não trava', !g.erro && /déficit de 5\.720 sc/.test(g.msg), g.erro || g.msg); });
caso('C04', () => { const c = NOVO60();
  const e1 = PROG(c, 'PV-036', 'L39-133', 1000, 'Baú refrigerado 12 t', 'Ana', 'T-P1');
  ok('C04 AC-05 programar sem reserva é recusado', /sem reserva ativa/.test(e1.erro || ''), e1);
  MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 7500, ator: 'Dora' }));
  ok('C04b KC11 previsto sugerido = mín(reserva não programada 240.000 kg, bitrem 37 t) = 37.000 kg = 616,67 sc', comSugPrev(c, 'PV-030', 'Bitrem graneleiro 37 t', 'L10-031') === 37000 && prFmt(prQ('Soja', 37000), 2) === '616,67', comSugPrev(c, 'PV-030', 'Bitrem graneleiro 37 t', 'L10-031'));
  const e2 = PROG(c, 'PV-030', 'L10-031', 240001, 'Bitrem graneleiro 37 t', 'Ana', 'T-P2'); const e3 = PROG(c, 'PV-030', 'L10-031', 37001, 'Bitrem graneleiro 37 t', 'Ana', 'T-P3');
  const e4 = PROG(c, 'PV-030', 'L10-031', 12000, 'Baú refrigerado 12 t', 'Ana', 'T-P4'); const e5 = MUD(c, x => comProgramar(x, { venda: 'PV-030', lotes: [{ lote: 'L10-031', prev: 37000 }], veic: 'Bitrem graneleiro 37 t', placa: '', ator: 'Ana', chave: 'T-P5' }));
  ok('C04c recusas: acima da reserva não programada, acima da capacidade, veículo incompatível (soja em baú refrigerado), sem placa', /acima da reserva ainda não programada/.test(e2.erro || '') && /acima da capacidade/.test(e3.erro || '') && /grão vai em graneleiro/.test(e4.erro || '') && /placa/.test(e5.erro || ''), [e2.erro, e3.erro, e4.erro, e5.erro]);
  const p = PROG(c, 'PV-030', 'L10-031', 37000, 'Bitrem graneleiro 37 t', 'Dora', 'T-P6'); const p2 = PROG(c, 'PV-030', 'L10-031', 37000, 'Bitrem graneleiro 37 t', 'Dora', 'T-P6');
  ok('C04d Dora programa a RM-0002 (cliente retira: transportador é o cliente); mesma chave = mesma carga; não programado cai para 203.000 kg', !p.erro && p.rm.id === 'RM-0002' && p.rm.transp === 'Coop Grão Sul' && p2.repetido && comNaoProg(c, 'PV-030', 'L10-031') === 203000, [p.erro, p2]); });
caso('C05', () => { const c = NOVO60(); const t = TAREFA(c); const P = c.producao; const S = prSaldos(c, P.lotes['L10-031']); const v = P.pedidos['PV-030']; const rm = P.expedicoes['RM-0002'];
  ok('C05 AC-06 KC04 saída da RM-0002 (51.200 − 14.240): 36.960 kg = 616 sc; L10-031 físico 37.804 sc · reservado 3.384 · disponível 34.420 sc (igual) · RS-0001 195.540 kg · falta 0',
     !t.s.erro && rm.saida.liq === 36960 && SC(S.fis) === '37.804 sc' && SC(S.res) === '3.384 sc' && SC(S.disp) === '34.420 sc' && P.reservas['RS-0001'].kg === 195540 && P.reservas['RS-0001'].exp === 36960 && prFalta(c, v) === 0 && SC(prExpedido(c, 'PV-030')) === '616 sc', [t.a.erro, t.b.erro, t.s.erro, S]);
  ok('C05b cliente retira: a saída é a entrega (Entregue); R$ 78.848,00 a receber até 26/09; lote de abertura sai com "origem anterior ao sistema"', rm.st === 'Entregue' && /R\$ 78\.848,00 a receber até 26\/09/.test(t.s.msg) && /origem anterior ao sistema/.test(JSON.stringify(rm.saida.aval)), [rm.st, t.s.msg, rm.saida.aval]);
  const n = P.movs.length; const r2 = MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '51.200', tara: '14.240', ator: 'Ana', chave: 'T-SAI' })); const r3 = MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '51.200', tara: '14.240', ator: 'Ana', chave: 'T-SAI-2' }));
  ok('C05c repetir a saída com a mesma chave não baixa de novo; outra chave na RM que já saiu é recusada', r2.repetido && /já confirmada/.test(r3.erro || '') && c.producao.movs.length === n && c.producao.movs.filter(m => m.tipo === 'expedição' && m.rm === 'RM-0002').length === 1, [r2.msg, r3.erro]);
  const c2 = NOVO60(); MUD(c2, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 7500, ator: 'Ana' })); PROG(c2, 'PV-030', 'L10-031', 37000, 'Bitrem graneleiro 37 t', 'Ana', 'T-Q');
  const z = MUD(c2, x => comSair(x, { rm: 'RM-0002', bruto: '14.240', tara: '14.240', ator: 'Ana', chave: 'T-Z' }));
  ok('C05d tara ≥ bruto é recusada, nada baixado', /maior que zero/.test(z.erro || '') && !c2.producao.expedicoes['RM-0002'].saida, z.erro);
  /* KC18 · excesso de 40 kg: 10.040 kg pesados para 10.000 reservados ao PV-036 */
  const c3 = NOVO60(); COLHEITA(c3); const ap = MUD(c3, x => comAprovarCredito(x, { venda: 'PV-036', ator: 'Ana', chave: 'T-CR' }));
  PROG(c3, 'PV-036', 'L39-133', 10000, 'Baú refrigerado 12 t', 'Dora', 'T-PX'); const k = { rm: 'RM-0002', bruto: '17.240', tara: '7.200' };
  const xr = MUD(c3, x => comSair(x, Object.assign({ ator: 'Rui', chave: 'T-X1' }, k))); const xd = MUD(c3, x => comSair(x, Object.assign({ ator: 'Dora', chave: 'T-X2' }, k)));
  const xa = MUD(c3, x => comSair(x, Object.assign({ ator: 'Ana', chave: 'T-X3' }, k)));
  ok('C05e KC18 excesso de 40 kg: Rui recusado (ajuste autorizado é da gestora), Dora recusada (não confirma saída); com Ana a aprovação de crédito (R$ 121.970) não cobre R$ 122.092',
     /Excesso de 40 kg no L39-133.*decisão de Ana \(gestora\)/.test(xr.erro || '') && /Confirmar saída da RM-0002: decisão de/.test(xd.erro || '') && /recusada no crédito/.test(xa.erro || '') && /122\.092/.test(xa.erro || '') && /121\.970/.test(xa.erro || '') && !ap.erro, [xr.erro, xd.erro, xa.erro, ap.erro]);
  const ap2 = MUD(c3, x => comAprovarCredito(x, { venda: 'PV-036', kg: 10040, ator: 'Ana', chave: 'T-CR2' })); const xb = MUD(c3, x => comSair(x, Object.assign({ ator: 'Ana', chave: 'T-X4' }, k)));
  const L = prSaldos(c3, c3.producao.lotes['L39-133']); const tt = comTitulos(c3, t => t.rm === 'RM-0002')[0] || {};
  ok('C05f Ana aprova de novo e a saída passa: 40 kg saem do disponível do L39-133 (2.050 → 2.010), físico 2.010 kg, falta 0, R$ 30.622,00; a reserva de outra venda não é tocada',
     !ap2.erro && !xb.erro && L.disp === 2010 && L.fis === 2010 && prFalta(c3, c3.producao.pedidos['PV-036']) === 0 && tt.valor === 30622 && c3.producao.expedicoes['RM-0002'].saida.exc.kg === 40 && c3.producao.expedicoes['RM-0002'].saida.exc.quem === 'Ana (gestora)', [ap2.erro, xb.erro, L, tt]);
  const c4 = NOVO60(); COLHEITA(c4); MUD(c4, x => prReservar(x, { pedido: 'PV-038', lote: 'L39-133', kg: 2050, ator: 'Ana' })); MUD(c4, x => comAprovarCredito(x, { venda: 'PV-036', kg: 10040, ator: 'Ana' }));
  PROG(c4, 'PV-036', 'L39-133', 10000, 'Baú refrigerado 12 t', 'Ana', 'T-PY'); const xs = MUD(c4, x => comSair(x, Object.assign({ ator: 'Ana', chave: 'T-X5' }, k)));
  ok('C05g sem disponível no lote (o resto é reserva do PV-038), o excesso é recusado até para a gestora: nunca sai da reserva de outra venda', /nunca sai da reserva de outra venda/.test(xs.erro || '') && prSaldos(c4, c4.producao.lotes['L39-133']).fis === 12050, xs.erro);
  /* excesso numa venda futura não vira oferta: CD Horti S42 1.000 kg, reserva 1.000, saída 1.040 com a gestora */
  const c5 = NOVO60(); COLHEITA(c5, false); const fv = MUD(c5, x => comVender(x, { cliente: 'CD Horti', prod: MAM, tipo: 'futura', sem: '2026-W42', qtd: '1000', preco: '3,10', ator: 'Ana', chave: 'T-F' })).v;
  MUD(c5, x => prReservar(x, { pedido: fv.id, lote: 'L39-133', kg: 1000, ator: 'Ana' })); const o0 = prOfertaSem(c5, MAM, '2026-W42');
  PROG(c5, fv.id, 'L39-133', 1000, 'Baú refrigerado 12 t', 'Ana', 'T-PZ'); const xf = MUD(c5, x => comSair(x, { rm: 'RM-0002', bruto: '8.240', tara: '7.200', ator: 'Ana', chave: 'T-XF' })); const o1 = prOfertaSem(c5, MAM, '2026-W42');
  ok('C05h excesso de 40 kg na venda futura (1.040 de 1.000 kg): vendas futuras da S42 vão a 0 kg e a oferta livre não aumenta', !xf.erro && o1.futKg === 0 && prCmp(o1.livre, o0.livre) === 0, [xf.erro, o0, o1]); });
caso('C06', () => { const c = NOVO60(); COLHEITA(c); MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', ator: 'Ana' })); PROG(c, 'PV-036', 'L39-133', 10000, 'Baú refrigerado 12 t', 'Ana', 'T-P');
  const L = c.producao.lotes['L39-133']; const v = c.producao.pedidos['PV-036']; const k = { rm: 'RM-0002', bruto: '17.200', tara: '7.200', ator: 'Ana' };
  const I0 = comImpede(c, v, L);
  ok('C06 AC-07 L39-133 apto: origem LC conforme no Mercado interno · Brasil, sem impedimento', !I0.imp.length && I0.aval.length === 1 && I0.aval[0].st === 'conforme', I0);
  const c1 = cenClone(c); c1.producao.lotes['L39-133'].q0 = 'Em inspeção'; const e1 = MUD(c1, x => comSair(x, Object.assign({ chave: 'T-E1' }, k)));
  ok('C06b lote Em inspeção: saída recusada com o dono (Qualidade)', /Saída recusada: L39-133 em inspeção/.test(e1.erro || '') && /Qualidade/.test(e1.erro), e1.erro);
  const c2 = cenClone(c); const P2 = 'Tebuconazol 200 EC'; OSX2(c2); const b = MUD(c2, x => carc_bula(x, P2, 'Mamão', 30)); const e2 = MUD(c2, x => comSair(x, Object.assign({ chave: 'T-E2' }, k)));
  const sv = comSitVenda(c2, c2.producao.pedidos['PV-036']);
  ok('C06c bula corrigida põe o lote na carência: saída recusada (bloqueado), venda "Em risco" pela mesma comImpede', !b.erro && /Saída recusada: L39-133 bloqueado/.test(e2.erro || '') && sv.t === 'Em risco', [b.erro, e2.erro, sv.t]);
  const c3 = cenClone(c); c3.car = c3.car || {}; c3.car.laudos = [{ id: 'LAB-T9', escopo: [I0.aval[0].lc], d: '2026-09-25', res: { tebuconazol: { v: 5, un: 'mg/kg', lq: 0.01 } } }];
  const e3 = MUD(c3, x => comSair(x, Object.assign({ chave: 'T-E3' }, k))); ok('C06d laudo acima do limite: Não conforme, saída recusada com quem decide', /Não conforme/.test(e3.erro || '') && /Qualidade/.test(e3.erro), e3.erro);
  const c4 = cenClone(c); c4.producao.pedidos['PV-036'].dest = 'EXP-UE'; const e4 = MUD(c4, x => comSair(x, Object.assign({ chave: 'T-E4' }, k)));
  ok('C06e destino pendente (regra não carregada): a recusa diz a falta e o dono', /Pendente/.test(e4.erro || '') && /Regra do destino não carregada/.test(e4.erro) && /Quem resolve: Qualidade · regulatório/.test(e4.erro), e4.erro);
  const c5 = cenClone(c); c5.producao.lotes['L39-133'].origem[0].dcol = '2026-09-24'; const I5 = comImpede(c5, v, c5.producao.lotes['L39-133']); const e5 = MUD(c5, x => comSair(x, Object.assign({ chave: 'T-E5' }, k)));
  ok('C06f origem sem lote de campo (colheita sem apontamento da data): impedido e recusado', I5.imp.some(i => /sem lote de campo/.test(i.t)) && !!e5.erro, [I5.imp, e5.erro]);
  ok('C06g a mesma recusa aparece "Em risco" na venda e impede a carga (mesma função)', comSitVenda(c1, c1.producao.pedidos['PV-036']).t === 'Em risco' && comImpede(c1, v, c1.producao.lotes['L39-133']).imp.length > 0); });
caso('C07', () => { const c = NOVO60(); COLHEITA(c); const v = c.producao.pedidos['PV-036'];
  const s0 = comSitVenda(c, v); const cr = comCredito(c, v, 10000);
  ok('C07 AC-08 KC09 Frutas Real: a receber R$ 91.470 + saída R$ 30.500 = R$ 121.970 > R$ 120.000 → PV-036 "Aguardando crédito"', s0.t === 'Aguardando crédito' && !cr.ok && cr.expo === 121970 && /121\.970,00, acima do limite de R\$ 120\.000,00/.test(cr.prob), [s0.t, cr]);
  PROG(c, 'PV-036', 'L39-133', 10000, 'Baú refrigerado 12 t', 'Dora', 'T-P'); const e = MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '17.200', tara: '7.200', ator: 'Rui', chave: 'T-S1' }));
  ok('C07b saída recusada com "decisão de Ana (gestora)"', /recusada no crédito/.test(e.erro || '') && /Aprovar crédito do PV-036: decisão de Ana \(gestora\)/.test(e.erro), e.erro);
  const ca = MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', ator: 'Caio', chave: 'T-A1' })); const aa = MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', ator: 'Ana', chave: 'T-A2' }));
  const ok2 = MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '17.200', tara: '7.200', ator: 'Rui', chave: 'T-S2' }));
  ok('C07c Caio não aprova; Ana aprova até R$ 121.970 e a saída passa (Rui · expedição); a carga registra a aprovação', /decisão de Ana \(gestora\)/.test(ca.erro || '') && !aa.erro && c.producao.pedidos['PV-036'].cred.ate === 121970 && !ok2.erro
     && c.producao.expedicoes['RM-0002'].saida.cred.quem === 'Ana (gestora)' && c.producao.expedicoes['RM-0002'].saida.quem === 'Rui (expedição)' && c.producao.expedicoes['RM-0002'].st === 'Em trânsito', [ca.erro, aa.erro, ok2.erro]);
  /* Rede Hortifrúti BA: limite vencido em 31/08/2026 */
  const c2 = NOVO60(); COLHEITA(c2, false); const rv = MUD(c2, x => comVender(x, { cliente: 'Rede Hortifrúti BA', prod: MAM, tipo: 'pronta', ini: '2026-09-26', fim: '2026-09-28', qtd: '1000', preco: '3,00', ator: 'Dora', chave: 'T-R' }));
  const sv0 = comSitVenda(c2, rv.v);
  ok('C07d sem reservado, limite vencido é aviso (no registro), não "Aguardando crédito"', !rv.erro && /vencido em 31\/08/.test(rv.msg) && sv0.t === 'Sem reserva', [rv.erro, rv.msg, sv0.t]);
  MUD(c2, x => prReservar(x, { pedido: rv.v.id, lote: 'L39-133', kg: 1000, ator: 'Dora' })); PROG(c2, rv.v.id, 'L39-133', 1000, 'Baú refrigerado 12 t', 'Dora', 'T-PR');
  const er = MUD(c2, x => comSair(x, { rm: 'RM-0002', bruto: '8.200', tara: '7.200', ator: 'Rui', chave: 'T-SR' }));
  ok('C07e Rede Hortifrúti (limite vencido) com reserva: "Aguardando crédito" e saída recusada com "decisão de Ana (gestora)"', comSitVenda(c2, c2.producao.pedidos[rv.v.id]).t === 'Aguardando crédito' && /vencido em 31\/08\/26/.test(er.erro || '') && /decisão de Ana \(gestora\)/.test(er.erro), er.erro);
  /* Antecipado: sem a gestora conferir o pagamento, não sai; depois sai e fica fora do a receber */
  const c3 = NOVO60(); COLHEITA(c3, false); const av = MUD(c3, x => comVender(x, { cliente: 'Rede Hortifrúti BA', prod: MAM, tipo: 'pronta', ini: '2026-09-26', fim: '2026-09-28', qtd: '1000', preco: '3,00', cond: 'Antecipado', ator: 'Dora', chave: 'T-AN' })).v;
  MUD(c3, x => prReservar(x, { pedido: av.id, lote: 'L39-133', kg: 1000, ator: 'Dora' })); PROG(c3, av.id, 'L39-133', 1000, 'Baú refrigerado 12 t', 'Dora', 'T-PA');
  const ea = MUD(c3, x => comSair(x, { rm: 'RM-0002', bruto: '8.200', tara: '7.200', ator: 'Rui', chave: 'T-SA' })); const conf = MUD(c3, x => comAprovarCredito(x, { venda: av.id, ator: 'Ana', chave: 'T-CA' }));
  const sa = MUD(c3, x => comSair(x, { rm: 'RM-0002', bruto: '8.200', tara: '7.200', ator: 'Rui', chave: 'T-SA2' }));
  ok('C07f CE-04 Antecipado não dispensa: sem conferir o pagamento a saída é recusada; Ana confere, a saída passa e a venda fica fora do a receber', /pagamento antecipado do .* não conferido/.test(ea.erro || '') && !conf.erro && /conferido/.test(conf.msg) && !sa.erro && !comTitulos(c3, t => t.venda === av.id).length, [ea.erro, conf.erro, sa.erro]); });
function OSX2(c) { /* aplicação de Tebuconazol em 15/09 no Pivô 19 (a bula de referência deixa a colheita de 22/09 fora da carência; a corrigida para 30 dias põe dentro) */
  c.ordens['OS-0990'] = { id: 'OS-0990', tipo: 'Pulverização · antracnose', talhao: 'Pivô 19', area: 75.11, etapa: 'Encerradas', versao: 'v1', realizado: 75.11, saldo: 0, resp: 'Wesley',
    ins: [{ p: 'Tebuconazol 200 EC', dose: 1, un: 'L', tot: 75.11 }], req: null, selos: [], ap: [{ d: '15/09', dia: 1, ha: 75.11, st: 'Conferido', sinc: true, origem: 'web' }], reservado: false, osc: {} }; }
caso('C08', () => { const c = NOVO60(); COLHEITA(c); MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', ator: 'Ana' })); PROG(c, 'PV-036', 'L39-133', 10000, 'Baú refrigerado 12 t', 'Dora', 'T-P');
  MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '17.200', tara: '7.200', ator: 'Rui', chave: 'T-S' }));
  const ed = MUD(c, x => comEntregar(x, { rm: 'RM-0002', d: '2026-09-25', ator: 'Rui', chave: 'T-E0' }));
  const en = MUD(c, x => comEntregar(x, { rm: 'RM-0002', d: '2026-09-26', dev: { kg: 400, motivo: 'Maturação avançada' }, ator: 'Rui', chave: 'T-E' }));
  const P = c.producao; const rm = P.expedicoes['RM-0002']; const dv = rm.devs[0] || {}; const L = P.lotes[dv.lote] || {}; const S = L.id ? prSaldos(c, L) : {}; const t = comTitulos(c, x => x.rm === 'RM-0002')[0] || {};
  ok('C08 AC-09 KC10 entrega com devolução de 400 kg: lote novo Em inspeção (origem sem carga e sem kg), entregue 9.600 kg, a receber R$ 29.280,00 vence 24/10, falta 400 kg',
     /antes da saída/.test(ed.erro || '') && !en.erro && rm.st === 'Entregue com devolução' && S.q === 'Em inspeção' && S.fis === 400 && L.cond === 'Devolvido' && L.origem.every(o => o.carga === undefined && o.kg === undefined && o.dev && o.dev.rm === 'RM-0002')
     && prExpedido(c, 'PV-036') === 9600 && t.valor === 29280 && t.venc === '2026-10-24' && prFalta(c, P.pedidos['PV-036']) === 400, [ed.erro, en.erro, S, t, L.origem]);
  const r = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: L.id, kg: 400, ator: 'Dora' })); const lb = MUD(c, x => prLiberarLote(x, L.id, 'Marta')); const r2 = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: L.id, kg: 400, ator: 'Dora' }));
  ok('C08b o lote de retorno não é reservável até a Qualidade liberar; depois de liberado, reserva', /não está apto/.test(r.erro || '') && !lb.erro && !r2.erro, [r.erro, lb.erro, r2.erro]);
  const d2 = MUD(c, x => comDevolver(x, { rm: 'RM-0002', kg: 9601, motivo: 'Avaria no transporte', ator: 'Rui', chave: 'T-D2' })); const d3 = MUD(c, x => comDevolver(x, { rm: 'RM-0002', kg: 100, motivo: '', ator: 'Rui', chave: 'T-D3' }));
  const d4 = MUD(c, x => comDevolver(x, { rm: 'RM-0002', kg: 100, motivo: 'Avaria no transporte', ator: 'Dora', chave: 'T-D4' }));
  ok('C08c devolver mais que o entregue, sem motivo ou por quem vende é recusado', /acima do entregue: no máximo 9\.600 kg/.test(d2.erro || '') && /motivo/.test(d3.erro || '') && /decisão de/.test(d4.erro || ''), [d2.erro, d3.erro, d4.erro]); });
caso('C09', () => { const c = NOVO60(); MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 7500, ator: 'Dora' })); PROG(c, 'PV-030', 'L10-031', 37000, 'Bitrem graneleiro 37 t', 'Dora', 'T-P');
  const e0 = MUD(c, x => comEncerrar(x, { venda: 'PV-030', motivo: '', ator: 'Dora' })); const e1 = MUD(c, x => comEncerrar(x, { venda: 'PV-030', motivo: 'cliente reduziu o contrato', ator: 'Dora' }));
  ok('C09 AC-10 encerrar sem motivo recusa; com carga programada recusa (cancele a carga antes)', /motivo/.test(e0.erro || '') && /RM-0002 programada/.test(e1.erro || ''), [e0.erro, e1.erro]);
  const cc = MUD(c, x => comCancelarCarga(x, { rm: 'RM-0002', motivo: 'caminhão não veio', ator: 'Dora' })); const en = MUD(c, x => comEncerrar(x, { venda: 'PV-030', motivo: 'cliente reduziu o contrato', ator: 'Dora', chave: 'T-EN' }));
  const v = c.producao.pedidos['PV-030']; const S = prSaldos(c, c.producao.lotes['L10-031']);
  ok('C09b cancelada a carga (reservas intactas), encerrar cancela RS-0001 e RS-0002 na mesma transação; quantidade vigente 0 sc; disponível do L10-031 volta a 38.420 sc; falta 0',
     !cc.erro && !en.erro && /RS-0001, RS-0002/.test(en.msg) && v.enc.qtd0 === 240000 && v.qtd === 0 && SC(S.disp) === '38.420 sc' && prFalta(c, v) === 0 && prSitPed(c, v).t === 'Encerrada', [cc.erro, en.erro || en.msg, SC(S.disp)]); });
caso('C10', () => { const c = NOVO60(); const rows = comPainel(c); const R_ = (p, per) => rows.find(r => r.prod === p && r.per === per) || {};
  const se = R_('Soja em grão', 'est:2025/26'), sf = R_('Soja em grão', '2026/27'), me = R_(MAM, 'est:'), m41 = R_(MAM, '2026-W41');
  ok('C10 AC-11 painel da semente: soja estoque 38.420 apto · 4.000 compromissos · 3.875 coberto · 34.420 sc livre; safra 26/27 68.180 · 19.900 · 48.280 sc',
     SC(se.oferta) === '38.420 sc' && SC(se.comp) === '4.000 sc' && SC(se.cob) === '3.875 sc' && SC(se.livre) === '34.420 sc' && SC(sf.oferta) === '68.180 sc' && SC(sf.comp) === '19.900 sc' && SC(sf.livre) === '48.280 sc', [se, sf]);
  ok('C10b mamão: estoque 0 apto, 10.000 kg do PV-036, déficit 10.000 kg; S41 sem versão publicada, 30.000 kg, déficit 30.000 kg; S40, S42 e S43 sem previsão nem venda não aparecem',
     me.oferta === 0 && me.comp === 10000 && me.livre === -10000 && me.sit === 'Déficit' && m41.tem === false && m41.comp === 30000 && m41.livre === -30000 && !rows.some(r => r.per === '2026-W40' || r.per === '2026-W42' || r.per === '2026-W43'), [me, m41, rows.map(r => r.id)]);
  const pr = comPrecos(c); const ps = pr.find(x => x.prod === 'Soja em grão'), pm = pr.find(x => x.prod === MAM); const ind = comIndicadores(c);
  ok('C10c preço médio contratado soja R$ 131,00/sc e mamão R$ 3,05/kg; realizado mamão R$ 3,00/kg; a receber R$ 91.470,00 (vence 15/10); vencido 0; CPR e barter fora',
     prFmt(ps.medC, 2) === '131,00' && prFmt(pm.medC, 2) === '3,05' && prFmt(pm.medR, 2) === '3,00' && ind.aRec === 91470 && ind.venc === 0 && comTitulos(c)[0].venc === '2026-10-15' && ps.liq.sort().join() === 'BT-090,CRE-0095', [ps, pm, ind]);
  const t = TAREFA(c); const pr2 = comPrecos(c).find(x => x.prod === 'Soja em grão'); const se2 = comPainel(c).find(r => r.per === 'est:2025/26');
  ok('C10d depois da tarefa (§6.5): soja realizado R$ 128,00/sc, entregue 616 sc; a receber R$ 170.318,00; estoque livre 34.420 sc (igual)', !t.s.erro && prFmt(pr2.medR, 2) === '128,00' && SC(pr2.ent) === '616 sc' && comIndicadores(c).aRec === 170318 && SC(se2.livre) === '34.420 sc', [t.s.erro, pr2, comIndicadores(c)]);
  /* KC16 · venda futura reservando estoque: PV-038 reserva os 2.050 kg livres do L39-133 */
  const c2 = NOVO60(); COLHEITA(c2); MUD(c2, x => prReservar(x, { pedido: 'PV-038', lote: 'L39-133', kg: 2050, ator: 'Dora' })); const e16 = comPainel(c2).find(r => r.prod === MAM && r.per === 'est:');
  ok('C10e KC16 linha Estoque fecha: oferta 12.050 − compromissos 12.050 (10.000 do PV-036 + 2.050 reservados ao PV-038) = livre 0', e16.oferta === 12050 && e16.comp === 12050 && e16.cob === 12050 && e16.livre === 0, e16);
  /* KC17 · em 05/10 a S41 começou: PV-038 no estoque; L39-133 vencido (29/09) fora do livre */
  const c3 = NOVO60(); COLHEITA(c3); const r17 = comPainel(c3, '2026-10-05'); const e17 = r17.find(r => r.prod === MAM && r.per === 'est:');
  ok('C10f KC17 comPainel(c, 05/10): PV-038 entra no estoque, vencido 12.050 kg à parte, 12.050 − 40.000 − 2.050 = déficit 30.000 kg; S41 sai da grade de semanas',
     e17.oferta === 12050 && e17.vencApto === 12050 && e17.dispVenc === 2050 && e17.comp === 40000 && e17.livre === -30000 && !r17.some(r => r.per === '2026-W41'), [e17, r17.map(r => r.id)]); });
caso('C11', () => { const c = NOVO60();
  const rd = MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 7500, ator: 'Rui', chave: 'T-R1' })); const dd = MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 7500, ator: 'Dora', chave: 'T-R2' }));
  const pd = PROG(c, 'PV-030', 'L10-031', 37000, 'Bitrem graneleiro 37 t', 'Dora', 'T-P1'); const sd = MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '51.200', tara: '14.240', ator: 'Dora', chave: 'T-S1' }));
  const sc = MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '51.200', tara: '14.240', ator: 'Caio', chave: 'T-S2' })); const cz = MUD(c, x => comCancelarCarga(x, { rm: 'RM-0002', motivo: 'x', ator: 'Caio' }));
  const sr = MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '51.200', tara: '14.240', ator: 'Rui', chave: 'T-S3' }));
  ok('C11 AC-12 R-C14: Rui não reserva; Dora reserva e programa carga mas não confirma a saída; Caio não age; Rui confirma a saída; cada registro grava quem agiu',
     /decisão de/.test(rd.erro || '') && !dd.erro && c.producao.reservas['RS-0002'].quem === 'Dora (comercial)' && !pd.erro && c.producao.expedicoes['RM-0002'].quem === 'Dora (comercial)'
     && /Confirmar saída da RM-0002: decisão de Ana \(gestora\) ou Rui \(expedição\)/.test(sd.erro || '') && /decisão de/.test(sc.erro || '') && !sr.erro && c.producao.expedicoes['RM-0002'].saida.quem === 'Rui (expedição)'
     && c.producao.movs.find(m => m.rm === 'RM-0002').quem === 'Rui (expedição)' && /decisão de/.test(cz.erro || ''), [rd.erro, dd.erro, pd.erro, sd.erro, sc.erro, sr.erro, cz.erro]);
  ok('C11b perfis: Dora · Comercial e Rui · Almoxarife e expedição no cadastro (rótulo de quem age: "Rui (almoxarife)" continua no estoque)', g2pf('Dora') && g2pf('Rui').t === 'Rui · Almoxarife e expedição' && g2ator('Rui', 'almoxarife') === 'Rui (almoxarife)' && g2quem('almoxarife') === 'Rui (almoxarife) ou Paula (almoxarife)', [g2pf('Rui')]); });
caso('C12', () => { const c = NOVO60(); COLHEITA(c); MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', ator: 'Ana' }));
  const qs = ['3.333,3', '3.333,3', '3.333,4']; const erros = [];
  qs.forEach((q, i) => { const p = PROG(c, 'PV-036', 'L39-133', prNum(q), 'Baú refrigerado 12 t', 'Ana', 'T-P' + i); if (p.erro) erros.push(p.erro);
    const s = MUD(c, x => comSair(x, { rm: p.rm ? p.rm.id : '', bruto: prFmtT(prSoma([prNum(q), 7200]), 1), tara: '7.200', ator: 'Rui', chave: 'T-S' + i })); if (s.erro) erros.push(s.erro); });
  const r = c.producao.reservas['RS-0002']; const vals = comTitulos(c, t => t.venda === 'PV-036').map(t => t.valor);
  ok('C12 AC-13 KC15 três saídas de 3.333,3 + 3.333,3 + 3.333,4 kg: reserva Expedida com 0 exato, físico 2.050 kg exato, a receber 10.166,57 + 10.166,57 + 10.166,87 = R$ 30.500,01 (centavo do arredondamento por evento); o crédito aprovado (R$ 121.970) cobre as três',
     !erros.length && r.st === 'Expedida' && r.kg === 0 && r.exp === 10000 && prFis(c, 'L39-133') === 2050 && vals.join() === '10166.57,10166.57,10166.87' && comAReceber(c, t => t.venda === 'PV-036') === 30500.01, [erros, r, vals]); });
}
/* C13 · A-17: massa da saca do compromisso preservada com a origem; legado ambíguo suspende só o que depende dela até a conversão registrada */
if (TEM_COM && NUCLEO) {
caso('C13', () => { const c = NOVO(); const P = c.producao; const v = P.pedidos['PV-030']; const L = P.lotes['L10-031'];
  const rows = comPainel(c); const se = rows.find(r => r.per === 'est:2025/26') || {}, sf = rows.find(r => r.per === '2026/27') || {}, me = rows.find(r => r.prod === MAM && r.per === 'est:') || {};
  ok('C13 semente: PV-030 "Saca a conferir" (VE-05 oculto sc 50 kg × Colheita 60 kg), quantidade do contrato 4.000 sc sem kg, falta suspensa; nada convertido em silêncio',
     prSitPed(c, v).t === 'Saca a conferir' && comSitVenda(c, v).t === 'Saca a conferir' && v.qtd === null && v.qc === 4000 && prFalta(c, v) === 0 && prQtdTxt(v) === '4.000 sc (saca de 50 ou 60 kg a conferir)' && /sc 50 kg/.test(v.fatOrig), [prSitPed(c, v).t, v.qtd, prQtdTxt(v)]);
  const r0 = MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 7500, ator: 'Ana' })); const p0 = PROG(c, 'PV-030', 'L10-031', 37000, 'Bitrem graneleiro 37 t', 'Ana', 'T-P0');
  ok('C13b reservar e programar carga para o PV-030 recusados até registrar a saca; a saída fica impedida pela mesma comImpede', /saca do contrato a conferir/.test(r0.erro || '') && /saca do contrato a conferir/.test(p0.erro || '') && /saca do contrato a conferir/.test((comImpede(c, v, L).imp[0] || {}).t || ''), [r0.erro, p0.erro]);
  ok('C13c Painel: soja Estoque e Safra 2026/27 "Suspenso" (livre null, não zero) com as vendas da saca a conferir; mamão segue calculado (déficit 10.000 kg)',
     se.livre === null && se.sit === 'Suspenso' && se.amb.join() === 'PV-030' && sf.livre === null && sf.sit === 'Suspenso' && sf.amb.join() === 'CT-203,CRE-0095,BT-090' && me.livre === -10000 && prOfertaSafra(c, 'Soja em grão', '2026/27').livre === null, [se, sf]);
  const ps = comPrecos(c).find(x => x.prod === 'Soja em grão');
  ok('C13d preço médio da soja não soma venda sem a massa: fora da média PV-030 e CT-203 (CPR e barter à parte)', ps.medC === null && ps.amb.join() === 'PV-030,CT-203', ps);
  const k = { venda: 'PV-030', fat: '60', fonte: 'Contrato CT-201, cláusula 2', ator: 'Ana', chave: 'T-SC1' };
  const er = MUD(c, x => comConverterSaca(x, Object.assign({}, k, { ator: 'Rui', chave: 'T-SCr' }))); const e5 = MUD(c, x => comConverterSaca(x, Object.assign({}, k, { fat: '55', chave: 'T-SC5' })));
  const ef = MUD(c, x => comConverterSaca(x, Object.assign({}, k, { fonte: ' ', chave: 'T-SCf' })));
  ok('C13e registrar a saca: Rui (expedição) recusado; massa fora do conflito (55 kg) recusada; sem fonte recusada; nada gravado', /decisão de Ana \(gestora\) ou Dora \(comercial\)/.test(er.erro || '') && /50 kg ou 60 kg/.test(e5.erro || '') && /Informe onde está a massa/.test(ef.erro || '') && !v.fatConf && !P.pedidos['PV-030'].fatConf, [er.erro, e5.erro, ef.erro]);
  const a = MUD(c, x => comConverterSaca(x, k)); const a2 = MUD(c, x => comConverterSaca(x, k)); const a3 = MUD(c, x => comConverterSaca(x, Object.assign({}, k, { fat: '50', chave: 'T-SC2' })));
  const v2 = c.producao.pedidos['PV-030']; const se2 = comPainel(c).find(r => r.per === 'est:2025/26');
  ok('C13f com 60 kg e a fonte: 4.000 sc = 240.000 kg, falta 7.500 kg (125 sc), quem e quando gravados; mesma chave repete sem gravar; outra massa depois é recusada; estoque livre 34.420 sc',
     !a.erro && /4\.000 sc = 240\.000 kg; falta 125 sc/.test(a.msg) && v2.qtd === 240000 && prFalta(c, v2) === 7500 && v2.fatConf.quem === 'Ana (gestora)' && v2.fatConf.fonte === 'Contrato CT-201, cláusula 2' && a2.repetido && /já registrada: 60 kg/.test(a3.erro || '')
     && comQtdTxt(v2) === '4.000 sc' && comPrecoTxtV(v2) === 'R$ 128,00/sc' && SC(se2.livre) === '34.420 sc', [a.erro || a.msg, a3.erro, se2]);
  /* 50 kg explícitos: reproduzíveis, sem reinterpretar pela unidade atual da cultura (60 kg) */
  const d = NOVO(); ['CT-203', 'CRE-0095', 'BT-090'].forEach(id => MUD(d, x => comConverterSaca(x, { venda: id, fat: '50', fonte: 'Contrato ' + id, ator: 'Dora', chave: 'T-50-' + id })));
  const o50 = prOfertaSafra(d, 'Soja em grão', '2026/27'); const ct = d.producao.pedidos['CT-203'];
  ok('C13g com 50 kg registrados nos três contratos 26/27: compromissos 995.000 kg (não 1.194.000), oferta livre 3.095.800 kg = 51.596,67 sc de 60 kg (+199.000 kg); CT-203 "12.000 sc 50 kg" a "R$ 132,00/sc 50 kg"',
     o50.futKg === 995000 && o50.livre === 3095800 && SC(o50.livre) === '51.596,67 sc' && comQtdTxt(ct) === '12.000 sc 50 kg' && comPrecoTxtV(ct) === 'R$ 132,00/sc 50 kg' && comValorQc(ct) === 1584000, [o50, comQtdTxt(ct)]);
  const e = NOVO(); const m = MUD(e, x => comConverterSaca(x, { venda: 'PV-030', fat: '50', fonte: 'Contrato CT-201', ator: 'Ana', chave: 'T-50' })); const ve = e.producao.pedidos['PV-030']; const sv = comSitVenda(e, ve);
  ok('C13h PV-030 com 50 kg: 200.000 kg e a RS-0001 (232.500 kg) fica acima da venda em 650 sc 50 kg: a mensagem e a situação "Em risco" pedem cancelar e reservar de novo; a saída fica impedida',
     !m.erro && ve.qtd === 200000 && /Reservado acima da venda em 650 sc 50 kg/.test(m.msg) && sv.t === 'Em risco' && /reservado acima da venda/.test(comImpede(e, ve, e.producao.lotes['L10-031']).imp[0].t), [m.erro || m.msg, sv.t]);
  /* cadastro da cultura muda (60 → 50): a venda registrada guarda a sua massa; nada é reinterpretado */
  const f = NOVO60(); const nv = MUD(f, x => comVender(x, { cliente: 'Coop Grão Sul', prod: 'Soja em grão', tipo: 'pronta', ini: '2026-09-28', fim: '2026-10-04', qtd: '1.000', preco: '130', ator: 'Dora', chave: 'T-NV' })).v;
  const m0 = PRDC.un['Soja'].massa; let fx = [];
  try { PRDC.un['Soja'].massa = 50; const w = f.producao.pedidos[nv.id]; const c203 = f.producao.pedidos['CT-203'];
    fx = [w.qtd, comTxtV(w, w.qtd), comValorV(w, w.qtd), prFalta(f, w), c203.qtd, comTxtV(c203, c203.qtd)]; } finally { PRDC.un['Soja'].massa = m0; }
  ok('C13i venda nova grava a massa da unidade no registro (sc de 60 kg) e a origem; se o cadastro da soja mudar para 50 kg, PV-039 continua 60.000 kg, "1.000 sc 60 kg", R$ 130.000,00, falta 60.000 kg; CT-203 continua 720.000 kg',
     nv.fat === '60' && /sc de 60 kg/.test(nv.fatOrig) && fx[0] === 60000 && fx[1] === '1.000 sc 60 kg' && fx[2] === 130000 && fx[3] === 60000 && fx[4] === 720000 && fx[5] === '12.000 sc 60 kg', [nv.fat, nv.fatOrig, fx]);
  /* encerrar o contrato sem registrar a saca: a quantidade vigente é o entregue (0 kg); a oferta deixa de esperar por ele e registrar depois é recusado */
  const g = NOVO(); const en = MUD(g, x => comEncerrar(x, { venda: 'CT-203', motivo: 'cliente desistiu', ator: 'Dora', chave: 'T-EN203' }));
  const og = prOfertaSafra(g, 'Soja em grão', '2026/27'); const rg = MUD(g, x => comConverterSaca(x, { venda: 'CT-203', fat: '60', fonte: 'Contrato CT-203', ator: 'Ana', chave: 'T-S203' }));
  ['CRE-0095', 'BT-090'].forEach(id => MUD(g, x => comConverterSaca(x, { venda: id, fat: '60', fonte: 'Contrato ' + id, ator: 'Ana', chave: 'T-60-' + id })));
  const og2 = prOfertaSafra(g, 'Soja em grão', '2026/27');
  ok('C13j CT-203 encerrado sem a saca: "Encerrada", 0 kg vigentes; a oferta 26/27 segue suspensa só por CRE-0095 e BT-090; registrar a saca depois é recusado; com as outras duas em 60 kg, livre 60.280 sc (68.180 − 7.900)',
     !en.erro && prSitPed(g, g.producao.pedidos['CT-203']).t === 'Encerrada' && g.producao.pedidos['CT-203'].qtd === 0 && og.amb.join() === 'CRE-0095,BT-090' && /está encerrada/.test(rg.erro || '') && !g.producao.pedidos['CT-203'].fatConf
     && og2.livre !== null && SC(og2.livre) === '60.280 sc' && comQtdTxt(g.producao.pedidos['CT-203']) === '0 kg', [en.erro, og.amb, rg.erro, og2.livre]); });
}
/* =====================================================================================================================
   RV · revisão adversarial de 09/10 (subagente revisor do workflow; não é o parecer do Codex) sobre o HEAD bdc5ca8 (A2..A12; A1 e A6 são de tela: comercial_revisao_test.py). Cada caso falha no
   código antes da correção e passa depois (sondas p3..p11 do revisor, executadas)
   ===================================================================================================================== */
/* carga entregue (mamão, agricultor entrega): Frutas Real com crédito aprovado, RM-0002 do L39-133 com 10.000 kg, saída por Rui */
function EMTRANSITO(c) { COLHEITA(c); MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', ator: 'Ana', chave: 'T-CR' })); const p = PROG(c, 'PV-036', 'L39-133', 10000, 'Baú refrigerado 12 t', 'Dora', 'T-P');
  const s = MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '22000', tara: '12000', ator: 'Rui', chave: 'T-S' })); if (p.erro || s.erro) throw new Error('em trânsito: ' + (p.erro || s.erro)); }
if (TEM_COM && NUCLEO) {
caso('RV-A2', () => { const c = NOVO60(); COLHEITA(c, false);
  MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 5000, ator: 'Dora', chave: 'A1' })); MUD(c, x => prReservar(x, { pedido: 'PV-038', lote: 'L39-133', kg: 7050, ator: 'Dora', chave: 'A2' }));
  const d = MUD(c, x => comProgramar(x, { venda: 'PV-036', lotes: [{ lote: 'L39-133', prev: 5000 }, { lote: 'L39-133', prev: 5000 }], veic: 'Baú refrigerado 12 t', transp: 'Rota Sul Transportes', placa: 'ABC1D23', dprev: '2026-09-26', ator: 'Dora', chave: 'A3' }));
  ok('RV-A2 S2 lote repetido na carga é recusado (o limite é por lote): nenhuma carga gravada', /Lote repetido na carga \(L39-133\)/.test(d.erro || '') && Object.keys(c.producao.expedicoes).length === 1, d.erro || d.msg);
  /* carga antiga com o lote repetido (gravada antes da correção): a saída soma por lote e o excesso não sai da reserva do PV-038 */
  c.producao.expedicoes['RM-0009'] = { id: 'RM-0009', pedido: 'PV-036', lotes: [{ lote: 'L39-133', prev: 5000, kg: 0 }, { lote: 'L39-133', prev: 5000, kg: 0 }], modal: 'entrega', local: '', transp: 'Rota Sul Transportes', veic: 'Baú refrigerado 12 t', placa: 'ABC1D23', dprev: '2026-09-26', st: 'Programada', saida: null, entrega: null, devs: [], canc: null, d: '2026-09-26', at: '08:00', quem: 'Dora (comercial)', chave: 'RM-0009', imp: '' };
  MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', kg: 10000, ator: 'Ana', chave: 'A5' }));
  const s = MUD(c, x => comSair(x, { rm: 'RM-0009', bruto: '22000', tara: '12000', kgs: { 'L39-133': '5000' }, ator: 'Rui', chave: 'A4' })); const S = prSaldos(c, c.producao.lotes['L39-133']);
  ok('RV-A2b carga antiga com o L39-133 em duas linhas: 10.000 kg contra 5.000 kg reservados ao PV-036 e 0 disponível são recusados; a reserva do PV-038 (7.050 kg) e o físico (12.050 kg) ficam intactos',
     /nunca sai da reserva de outra venda/.test(s.erro || '') && S.fis === 12050 && prResPed(c, 'PV-038')[0].kg === 7050, [s.erro || s.msg, S]);
  /* pós-condição: físico abaixo do reservado depois da saída recusa (defesa além do cálculo do excesso) */
  const c2 = NOVO60(); COLHEITA(c2, false); MUD(c2, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 5000, ator: 'Dora', chave: 'B1' })); MUD(c2, x => prReservar(x, { pedido: 'PV-038', lote: 'L39-133', kg: 7050, ator: 'Dora', chave: 'B2' }));
  MUD(c2, x => comAprovarCredito(x, { venda: 'PV-036', kg: 5000, ator: 'Ana', chave: 'B3' })); PROG(c2, 'PV-036', 'L39-133', 4000, 'Baú refrigerado 12 t', 'Dora', 'B4');
  c2.producao.movs.push({ id: 'MP-T', tipo: 'quebra (teste)', lote: 'L39-133', kg: -1000, d: '2026-09-26' });   /* físico 11.050 < reservado 12.050 (estado fora da regra, injetado) */
  const s2 = MUD(c2, x => comSair(x, { rm: 'RM-0002', bruto: '16000', tara: '12000', ator: 'Rui', chave: 'B5' }));
  ok('RV-A2c pós-condição: saída que deixaria o físico do lote abaixo do reservado é recusada, nada baixado', /abaixo do reservado/.test(s2.erro || '') && !c2.producao.expedicoes['RM-0002'].saida, s2.erro || s2.msg); });
caso('RV-A3', () => { const c = NOVO60(); EMTRANSITO(c); const PP = () => c.producao;
  MUD(c, x => comEntregar(x, { rm: 'RM-0002', d: '2026-09-26', dev: { kg: 400, motivo: 'Maturação avançada' }, ator: 'Rui', chave: 'T-E' })); const lid = PP().expedicoes['RM-0002'].devs[0].lote;
  const er = ['Dora', 'Rui', 'Caio', 'Paula', ''].map(a => MUD(c, x => prLiberarLote(x, lid, a)).erro || '');
  ok('RV-A3 S2 lote devolvido: Dora, Rui, Caio, Paula e ninguém não liberam ("decisão de Ana (agrônoma) ou Marta (qualidade)", a regra do BEN-1 (d)); continua Em inspeção', er.every(e => /Liberar o lote L39-134: decisão de Ana \(agrônoma\) ou Marta \(qualidade\)/.test(e)) && prSaldos(c, PP().lotes[lid]).q === 'Em inspeção', er);
  const m = MUD(c, x => prLiberarLote(x, lid, 'Marta'));
  ok('RV-A3b Marta (qualidade) libera e o registro grava quem agiu ("Marta (qualidade)"), não um nome fixo', !m.erro && PP().lotes[lid].lib.quem === 'Marta (qualidade)' && /liberado por Marta \(qualidade\)/.test(m.msg), [m.erro || m.msg, PP().lotes[lid].lib]);
  ok('RV-A3c perfis: Marta · Qualidade no cadastro, só com o papel qualidade', g2pf('Marta') && g2pf('Marta').t === 'Marta · Qualidade' && g2papel('Marta', 'qualidade') && !g2papel('Marta', 'gestor') && !g2papel('Marta', 'comercial'), g2pf('Marta')); });
caso('RV-A4', () => { const c = NOVO60(); EMTRANSITO(c); let v = c.producao.pedidos['PV-036'];
  const sit = comSitVenda(c, v).t; const ind = comIndicadores(c); const pz = comPrecos(c).find(x => x.cu === 'Mamão Formosa');
  ok('RV-A4 S3 venda com a carga em trânsito: situação "Em trânsito" (não "Entregue"); entregue 30 d e realizado contam só o entregue (RM-0001: R$ 91.470,00; 30.490 kg)', sit === 'Em trânsito' && ind.ent30 === 91470 && pz.ent === 30490, [sit, ind.ent30, pz.ent]);
  MUD(c, x => comEntregar(x, { rm: 'RM-0002', d: '2026-09-26', ator: 'Rui', chave: 'T-E' })); v = c.producao.pedidos['PV-036']; const ind2 = comIndicadores(c); const pz2 = comPrecos(c).find(x => x.cu === 'Mamão Formosa');
  ok('RV-A4b confirmada a entrega: "Entregue", entregue 30 d R$ 121.970,00 e realizado sobre 40.490 kg', comSitVenda(c, v).t === 'Entregue' && ind2.ent30 === 121970 && pz2.ent === 40490, [comSitVenda(c, v).t, ind2.ent30, pz2.ent]); });
caso('RV-A5', () => { const c = NOVO60(); COLHEITA(c); const PP = () => c.producao; MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', kg: 12050, ator: 'Ana', chave: 'C0' }));
  PROG(c, 'PV-036', 'L39-133', 6000, 'Baú refrigerado 12 t', 'Dora', 'C2'); PROG(c, 'PV-036', 'L39-133', 4000, 'Baú refrigerado 12 t', 'Dora', 'C3');
  const x0 = MUD(c, x => prCancelarReserva(x, 'RS-0002', 'cliente adiou', 'Dora'));
  ok('RV-A5 S3 cancelar a reserva de lote que está em carga programada da mesma venda é recusado (cancele a carga antes); a reserva continua Ativa', /Cancele a carga antes/.test(x0.erro || '') && PP().reservas['RS-0002'].st === 'Ativa', x0.erro || x0.msg);
  const d0 = [comRmDescoberto(c, PP().expedicoes['RM-0002']).length, comRmDescoberto(c, PP().expedicoes['RM-0003']).length];
  const s = MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '22000', tara: '12000', ator: 'Rui', chave: 'C4' })); const d1 = comRmDescoberto(c, PP().expedicoes['RM-0003']);
  ok('RV-A5b 1ª carga pesa 10.000 kg (previsto 6.000): a saída avisa que a RM-0003 fica sem reserva; a RM-0003 passa a "descoberta" (cobre 0 de 4.000 kg)',
     d0.join() === '0,0' && !s.erro && /Aviso: líquido 4\.000 kg acima do previsto \(6\.000 kg\): RM-0003 fica sem reserva/.test(s.msg) && d1.length === 1 && d1[0].cobre === 0 && d1[0].prev === 4000, [d0, s.erro || s.msg, d1]);
  const sv = comSitVenda(c, PP().pedidos['PV-036']).t; const en = MUD(c, x => comEncerrar(x, { venda: 'PV-036', motivo: 'teste', ator: 'Dora', chave: 'C6' }));
  ok('RV-A5c a venda fica "Em trânsito" (não "Entregue") com a carga que sobrou programada; encerrar o saldo sem reserva ativa e com a RM-0003 programada é recusado (M19)', sv === 'Em trânsito' && /RM-0003 programada/.test(en.erro || '') && !PP().pedidos['PV-036'].enc, [sv, en.erro || en.msg]); });
caso('RV-A7', () => { const c = NOVO();
  MUD(c, x => comConverterSaca(x, { venda: 'PV-030', fat: '50', fonte: 'Contrato CT-201 cl. 2', ator: 'Ana', chave: 'S50' })); MUD(c, x => prCancelarReserva(x, 'RS-0001', 'refazer com 50 kg', 'Ana'));
  let v = c.producao.pedidos['PV-030']; const f = prFormReserva({ state: {} }, c, null, v, 'ped', comLotesPara(c, v)); const q = f.fields[1];
  ok('RV-A7 S3 formulário de reserva da venda em saca de 50 kg: quantidade em "sc 50 kg" e sugestão 4.000 (200.000 kg), não 3.333,333 sc de 60 kg', q.u === 'sc 50 kg' && q.v === '4000' && /falta do pedido \(4\.000 sc 50 kg\)/.test(q.h), [q.u, q.v, q.h]);
  const r = MUD(c, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 30000, ator: 'Ana', chave: 'S1' }));
  PROG(c, 'PV-030', 'L10-031', 30000, 'Bitrem graneleiro 37 t', 'Ana', 'S2'); MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '44000', tara: '14000', ator: 'Ana', chave: 'S3' })); v = c.producao.pedidos['PV-030'];
  const dv = MUD(c, x => comDevolver(x, { rm: 'RM-0002', kg: comBaseV(v, 100), motivo: 'Fora do padrão contratado', ator: 'Rui', chave: 'S4' }));
  ok('RV-A7b reserva e devolução na massa da venda: "600 sc 50 kg" reservados; "100" digitado em sc 50 kg = 5.000 kg devolvidos ("100 sc 50 kg"), não 6.000 kg',
     /600 sc 50 kg do L10-031/.test(r.msg || '') && !dv.erro && dv.dev.kg === 5000 && /^100 sc 50 kg devolvidos/.test(dv.msg) && comUnV(v) === 'sc 50 kg', [r.erro || r.msg, dv.erro || dv.msg]); });
caso('RV-A8', () => { const c = NOVO60(); COLHEITA(c); MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', ator: 'Ana', chave: 'D0' }));
  PROG(c, 'PV-036', 'L39-133', 6000, 'Baú refrigerado 12 t', 'Dora', 'D2'); MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '18000', tara: '12000', ator: 'Rui', chave: 'D3' }));
  MUD(c, x => comEncerrar(x, { venda: 'PV-036', motivo: 'cliente reduziu', ator: 'Dora', chave: 'D4' })); MUD(c, x => comEntregar(x, { rm: 'RM-0002', d: '2026-09-26', dev: { kg: 1000, motivo: 'Avaria no transporte' }, ator: 'Rui', chave: 'D5' }));
  const v = c.producao.pedidos['PV-036'];
  ok('RV-A8 S3 venda encerrada com devolução de 1.000 kg: quantidade do contrato acompanha (5.000 kg) e o valor do acordo é R$ 15.250,00, igual ao a receber', v.qtd === 5000 && v.qc === 5000 && comValorQc(v) === 15250 && comAReceber(c, t => t.venda === 'PV-036') === 15250, [v.qtd, v.qc, comValorQc(v)]); });
caso('RV-A9', () => { const c = NOVO60(); COLHEITA(c); const P = () => c.producao; PROG(c, 'PV-036', 'L39-133', 10000, 'Baú refrigerado 12 t', 'Dora', 'E1');
  const a = MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', kg: 10000, ator: 'Ana', chave: 'W-RM-1-CR' })); const b = MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', kg: 10000, ator: 'Ana', chave: 'W-RM-1-CR' }));
  const d = MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', kg: 10040, ator: 'Ana', chave: 'W-RM-1-CR' }));
  ok('RV-A9 S3 aprovação de crédito: a mesma chave e o mesmo peso repetem sem gravar; a mesma chave com outro peso é conflito (não "já registrado" que não cobre)', !a.erro && b.repetido && /conflito/.test(d.erro || '') && P().pedidos['PV-036'].cred.ate === 121970, [a.erro, b.msg, d.erro || d.msg]);
  const e = MUD(c, x => comAprovarCredito(x, { venda: 'PV-036', kg: 10040, ator: 'Ana', chave: 'W-RM-1-CR-10040' })); const s = MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '17240', tara: '7200', ator: 'Ana', chave: 'W-RM-1' }));
  ok('RV-A9b com a chave do novo peso, a aprovação cobre R$ 122.092,00 e a saída de 10.040 kg passa', !e.erro && P().pedidos['PV-036'].cred.ate === 122092 && !s.erro, [e.erro, s.erro]); });
caso('RV-A10', () => { const c = NOVO60(); const P = c.producao; const pub = prOfertaSafra(c, 'Soja em grão', '2026/27').pub;
  P.lotes['L40-900'] = { id: 'L40-900', prod: 'Soja em grão', cultura: 'Soja', classe: 'Padrão', saf: '2026/27', faz: 'Santa Rita', local: Object.keys(PRDC.locais)[0], drec: '2026-09-26', dcol: '2026-09-26', validade: null, q0: 'Liberado', cond: 'Íntegra', origem: [{ carga: 'CG-9999', os: 'OS-X', dcol: '2026-09-26', kg: 30000 }], cargas: ['CG-9999'] };
  P.movs.push({ id: 'MP-9999', tipo: 'recebimento', lote: 'L40-900', kg: 30000, d: '2026-09-26' });
  const r = comPainel(c).find(x => x.prod === 'Soja em grão' && x.per === 'est:2026/27') || {};
  ok('RV-A10 S3 1º caminhão da soja 26/27 (30.000 kg): a safra fica "em colheita"; oferta = apto + previsão ainda não colhida (68.180 sc − 500 sc colhidos), livre sem o déficit falso',
     r.colh && r.colh.col === 30000 && r.oferta === prSoma([r.apto, prSub(pub, 30000)]) && r.sit === 'Livre' && /em colheita/.test(r.perT), [r.perT, r.oferta, r.livre, r.sit, r.colh]);
  const R0 = prResultado; let r2 = {}; try { prResultado = (x, cid) => Object.assign({}, R0(x, cid), { parcial: false }); r2 = comPainel(c).find(x => x.prod === 'Soja em grão' && x.per === 'est:2026/27') || {}; } finally { prResultado = R0; }
  ok('RV-A10b colheita fechada (todos os cultivos sem O.S. aberta nem carga a pesar): vale só o colhido apto, sem a previsão', !r2.colh && r2.oferta === r2.apto && r2.sit === 'Déficit', [r2.perT, r2.oferta, r2.sit]); });
caso('RV-A11', () => { const c = NOVO60();
  const a = MUD(c, x => comVender(x, { cliente: 'Coop Grão Sul', prod: 'Soja em grão', tipo: 'pronta', ini: '2026-09-28', fim: '2026-10-04', qtd: '100', preco: '130', modal: 'entrega', ator: 'Dora', chave: 'V1' }));
  const b = MUD(c, x => comVender(x, { cliente: 'Coop Grão Sul', prod: 'Soja em grão', tipo: 'pronta', ini: '2026-09-28', fim: '2026-10-04', qtd: '100', preco: '130', ator: 'Dora', chave: 'V2' }));
  ok('RV-A11 S4 venda com "Agricultor entrega" não grava o local "Retira no Armazém Sede" do CD-05; com a modalidade do cadastro, herda', !a.erro && a.v.local === '' && /^Retira no Armazém Sede/.test(b.v.local), [a.erro || a.v.local, b.v && b.v.local]); });
/* A12 · mutantes que sobreviviam (17 de 38): cada caso mata um */
caso('RV-A12', () => { const c = NOVO60(); EMTRANSITO(c); const P = () => c.producao;
  const m1 = MUD(c, x => comAprovarCredito(x, { venda: 'PV-030', ator: 'Dora', chave: 'M1' }));
  const m2 = MUD(c, x => comEntregar(x, { rm: 'RM-0002', d: '2026-09-26', ator: 'Dora', chave: 'M2' }));
  const m5 = MUD(c, x => comEntregar(x, { rm: 'RM-0002', d: '2026-09-27', ator: 'Rui', chave: 'M5' }));
  const m12 = MUD(c, x => comDevolver(x, { rm: 'RM-0002', kg: 100, motivo: 'Maturação avançada', ator: 'Rui', chave: 'M12' }));
  ok('RV-A12 M06 Dora não aprova crédito; M07 Dora não confirma entrega; M03 entrega com data futura recusada; M30 devolução de carga em trânsito recusada',
     /decisão de Ana \(gestora\)/.test(m1.erro || '') && /decisão de/.test(m2.erro || '') && /depois de hoje/.test(m5.erro || '') && /só de carga entregue/.test(m12.erro || '') && !P().expedicoes['RM-0002'].entrega, [m1.erro, m2.erro, m5.erro, m12.erro]);
  MUD(c, x => comEntregar(x, { rm: 'RM-0002', d: '2026-09-26', ator: 'Rui', chave: 'M4a' })); const m4 = MUD(c, x => comEntregar(x, { rm: 'RM-0002', d: '2026-09-26', ator: 'Rui', chave: 'M4b' }));
  const m11 = MUD(c, x => comDevolver(x, { rm: 'RM-0002', kg: 100, motivo: 'porque sim', ator: 'Rui', chave: 'M11' }));
  ok('RV-A12b M36 segunda entrega com outra chave recusada (a 1ª fica, com a chave dela); M35 motivo de devolução fora da lista recusado', /já confirmada/.test(m4.erro || '') && P().expedicoes['RM-0002'].entrega.chave === 'M4a' && /motivo da devolução/.test(m11.erro || ''), [m4.erro, m11.erro]);
  const c2 = NOVO60(); MUD(c2, x => prReservar(x, { pedido: 'PV-030', lote: 'L10-031', kg: 7500, ator: 'Dora' }));
  const m8 = MUD(c2, x => comProgramar(x, { venda: 'PV-030', lotes: [{ lote: 'L10-031', prev: 37000 }], veic: 'Bitrem graneleiro 37 t', placa: 'ABC1D23', dprev: '2026-09-25', ator: 'Dora', chave: 'M8' }));
  PROG(c2, 'PV-030', 'L10-031', 37000, 'Bitrem graneleiro 37 t', 'Dora', 'M8b');
  const m10 = MUD(c2, x => comCancelarCarga(x, { rm: 'RM-0002', motivo: '  ', ator: 'Dora', chave: 'M10' })); MUD(c2, x => comCancelarCarga(x, { rm: 'RM-0002', motivo: 'caminhão não veio', ator: 'Dora', chave: 'M10b' }));
  const m3 = MUD(c2, x => comSair(x, { rm: 'RM-0002', bruto: '51200', tara: '14240', ator: 'Rui', chave: 'M3' }));
  ok('RV-A12c M15 data prevista antes de hoje recusada; M10 cancelar carga sem motivo recusado; M02 carga cancelada não sai (nada baixado)',
     /antes de hoje/.test(m8.erro || '') && /motivo do cancelamento da carga/.test(m10.erro || '') && /só carga programada sai/.test(m3.erro || '') && !c2.producao.expedicoes['RM-0002'].saida, [m8.erro, m10.erro, m3.erro]);
  const c3 = NOVO60(); COLHEITA(c3);
  const m9 = MUD(c3, x => comProgramar(x, { venda: 'PV-036', lotes: [{ lote: 'L39-133', prev: 10000 }], veic: 'Baú refrigerado 12 t', placa: 'ABC1D23', dprev: '2026-09-26', ator: 'Dora', chave: 'M9' }));
  const lp = comLotesPara(c3, c3.producao.pedidos['PV-038']).map(L => L.id);
  const m7 = MUD(c3, x => comVender(x, { cliente: 'Coop Grão Sul', prod: 'Soja em grão', tipo: 'pronta', ini: '2026-09-20', fim: '2026-09-25', qtd: '100', preco: '130', ator: 'Dora', chave: 'M7' }));
  const m13 = MUD(c3, x => comConverterSaca(x, { venda: 'PV-030', fat: '60', fonte: 'outra fonte', ator: 'Ana', chave: 'T-SACA-PV-030' }));
  const m17 = ['Rui', 'Caio'].map(a => MUD(c3, x => prCancelarReserva(x, 'RS-0002', 'teste', a)).erro || '');
  const mf = MUD(c3, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 1, ator: 'Dora', chave: 'MF' }));
  ok('RV-A12f reservar acima da falta da venda (PV-036 coberto, falta 0) é recusado: nunca reserva mais que o vendido', /Acima da falta do PV-036: 0 kg/.test(mf.erro || '') && Object.keys(c3.producao.reservas).length === 2, mf.erro || mf.msg);
  ok('RV-A12d M17 entrega sem transportador recusada; M13 lote que vence antes da janela fora da lista (L39-133 vence 29/09, PV-038 começa 05/10); M14 janela passada recusada; M20 mesma chave da saca com outra fonte é conflito; P cancelar reserva por Rui ou Caio recusado',
     /transportador/.test(m9.erro || '') && lp.indexOf('L39-133') < 0 && /já passou/.test(m7.erro || '') && /conflito/.test(m13.erro || '') && m17.every(e => /decisão de/.test(e)) && c3.producao.reservas['RS-0002'].st === 'Ativa', [m9.erro, lp, m7.erro, m13.erro, m17]);
  /* M24 antecipado fora da exposição; M05 borda do limite (= limite passa); M28 janela de 30 dias do indicador */
  const c4 = NOVO60(); COLHEITA(c4); const P4 = c4.producao; const e0 = comExpo(c4, 'Frutas Real');
  P4.pedidos['PV-T9'] = Object.assign({}, P4.pedidos['PV-036'], { id: 'PV-T9', cond: 'Antecipado', chave: 'PV-T9' }); P4.movs.push({ id: 'MP-T9', tipo: 'expedição', lote: 'L38-131', kg: -1000, pedido: 'PV-T9', d: '2026-09-26' });
  const cp = COMC.cp['Frutas Real']; const lim0 = cp.lim; let b1, b2;
  try { cp.lim = 121970; b1 = comCredito(c4, P4.pedidos['PV-036'], 10000).ok; cp.lim = 121969.99; b2 = comCredito(c4, P4.pedidos['PV-036'], 10000).ok; } finally { cp.lim = lim0; }
  P4.expedicoes['RM-0001'].saida.d = '2026-08-17'; P4.expedicoes['RM-0001'].entrega.d = '2026-08-17'; const i40 = comIndicadores(c4).ent30;
  ok('RV-A12e M24 venda antecipada expedida não entra na exposição (R$ 91.470,00); M05 exposição igual ao limite passa e 1 centavo acima pede a gestora; M28 entrega de 40 dias atrás fora do "entregue nos últimos 30 dias"',
     e0 === 91470 && comExpo(c4, 'Frutas Real') === 91470 && b1 === true && b2 === false && i40 === 0, [e0, comExpo(c4, 'Frutas Real'), b1, b2, i40]); });
}
/* CE-01 · página montada sem o núcleo da carência */
if (TEM_COM && !NUCLEO) {
caso('C06h', () => { const c = NOVO(); const L = c.producao.lotes['L38-132']; const v = c.producao.pedidos['PV-036']; const S = prSaldos(c, L); const I = comImpede(c, v, L);
  ok('C06h AC-07 CE-01 sem o núcleo da carência, o L38-132 aparece Liberado em prSaldos, mas comImpede recusa a saída (não o dá por Liberado)', S.q === 'Liberado' && I.imp.length === 1 && /núcleo da carência ausente/.test(I.imp[0].t), [S.q, I]);
  c.producao.reservas['RS-T'] = { id: 'RS-T', pedido: 'PV-036', lote: 'L38-132', kg: 10000, kg0: 10000, exp: 0, st: 'Ativa', d: '2026-09-26', at: '08:00', quem: 'Dora (comercial)', chave: 'RS-T' };
  const p = PROG(c, 'PV-036', 'L38-132', 10000, 'Baú refrigerado 12 t', 'Ana', 'T-P'); const s = MUD(c, x => comSair(x, { rm: 'RM-0002', bruto: '17.200', tara: '7.200', ator: 'Ana', chave: 'T-S' }));
  ok('C06i sem o núcleo, a venda fica "Em risco" e a saída é recusada; nada baixado', comSitVenda(c, c.producao.pedidos['PV-036']).t === 'Em risco' && !p.erro && /núcleo da carência ausente/.test(s.erro || '') && prFis(c, 'L38-132') === 29830, [p.erro, s.erro]); });
}
