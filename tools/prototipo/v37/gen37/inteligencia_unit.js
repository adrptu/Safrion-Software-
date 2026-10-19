/* INTEL-01 · testes puros da Inteligência de vendas e de compras (inteligencia.js) · node, sem navegador.
   Carregado depois de: perfis + CEN0 + cenario.js + producao.js + PR_UI_JS + PR_PED_JS + comercial.js + INTC + inteligencia.js + ORA (oráculo Python).
   Cada verificação vira uma linha do JSON final. Comentários só com barra-asterisco. */
const R = []; function ok(n, c, info) { R.push({ n, ok: !!c, info: c ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 700) }); }
function caso(nome, fn) { try { fn(); } catch (e) { ok(nome + ' (exceção)', false, String(e && e.stack || e).slice(0, 600)); } }
const perto = (a, b, tol) => a !== null && a !== undefined && b !== null && b !== undefined && Math.abs(Number(a) - Number(b)) <= (tol || 1e-6);
function MUD(c, fn) { const x = cenClone(c); try { const r = fn(x) || {}; Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); return r; } catch (e) { return { erro: String(e.message || e) }; } }
const NOVO = () => cenClone(CEN0);
const LEGADO = ['PV-030', 'CT-203', 'CRE-0095', 'BT-090'];   /* contratos de soja com a saca a conferir na semente (A-17) */
const HOJE = '2026-09-26';

/* ---------- fórmulas (F) ---------- */
caso('F1', () => { const s = intSpread('2.90', '3.10');
  ok('F1 diferença à referência: (2,90 − 3,10) ÷ 3,10 = −6,45% sem alerta sem meta', perto(s, -0.0645161, 1e-6) && !intAbaixo(s) && intPct(s) === '−6,5%', [s, intPct(s)]); });   /* sinal de menos tipográfico, como na tela */
caso('F2', () => ok('F2 ausente ≠ zero: sem referência a diferença é null, sem alerta e "—" na tela', intSpread('2.90', null) === null && intSpread('2.90', '0') === null && !intAbaixo(null) && intPct(null) === '—', [intSpread('2.90', null)]));
caso('F3', () => ok('F3 posição: 25 ÷ 100 = 25%; oferta zero ou ausente não vira 0% (null)', perto(intPosicao(25, 100), 0.25) && intPosicao(30000, 0) === null && intPosicao(10, null) === null, [intPosicao(25, 100), intPosicao(30000, 0)]));
caso('F4', () => { const a = intLiquido('3.00', '0.19', 30, '0.012'), b = intLiquido('3.00', '0.19', 0, '0.012');
  ok('F4 líquido = preço − frete − preço × 1,2% × dias ÷ 30: 3,00 − 0,19 − 0,036 = 2,774 (30 d); à vista 2,81', perto(a, 2.774) && perto(b, 2.81), [a, b]); });
caso('F5', () => ok('F5 frete por unidade = R$ 190/t × kg da unidade ÷ 1000: caixa de 20 kg R$ 3,80; kg R$ 0,19', perto(intFreteUn(20), 3.8) && perto(intFreteUn(1), 0.19), [intFreteUn(20), intFreteUn(1)]));
caso('F6', () => ok('F6 pontualidade = no prazo ÷ entregas: 2 de 3 = 66,7%; sem entrega é null (não 0% nem 100%)', perto(intPontualidade([{ atraso: 0 }, { atraso: 3 }, { atraso: 0 }]), 2 / 3, 1e-5) && intPontualidade([]) === null, intPontualidade([{ atraso: 0 }, { atraso: 3 }, { atraso: 0 }])));
caso('F7', () => ok('F7 R$/ha = Σ(qtd × preço) ÷ área: (100 × 2,5 + 10 × 30) ÷ 50 = 11; área zero é null', perto(intRsHa([{ qtd: '100', preco: '2.5' }, { qtd: '10', preco: '30' }], '50'), 11) && intRsHa([{ qtd: '1', preco: '1' }], '0') === null));
caso('F8', () => ok('F8 sem meta: nenhum limiar percentual classifica desempenho', [null,undefined,'-0.9','-0.0501','0','0.05','0.0501','9'].every(x=>!intAcima(x)&&!intAbaixo(x))));

/* ---------- Vendas (V) sobre a semente ---------- */
caso('V1', () => { const I = intVendas(NOVO(), HOJE); const s = I.posicao.find(p => p.prod === 'Soja em grão'); const pr = I.prods.find(p => p.prod === 'Soja em grão');
  ok('V1 soja com 4 contratos de saca a conferir (A-17): posição "Suspenso", livre e % null (nunca 0%); no preço médio ficam fora as 2 vendas (PV-030, CT-203), pois CPR e troca comprometem a oferta mas não são venda',
    s && s.est === 'Suspenso' && s.pos === null && s.livre === null && LEGADO.every(id => s.amb.indexOf(id) >= 0) && pr && pr.medC === null && JSON.stringify(pr.amb.slice().sort()) === JSON.stringify(['CT-203', 'PV-030']), [s, pr && pr.amb]); });
caso('V2', () => { const I = intVendas(NOVO(), HOJE); const m = I.posicao.find(p => /^Mamão/.test(p.prod)); const mp = I.prods.find(p => /^Mamão/.test(p.prod));
  ok('V2 mamão vendido (40.000 kg) sem previsão publicada: "Sem previsão", risco de oferta e 1 alerta no total (o preço, −1,6%, não alerta)',
    m && m.est === 'Sem previsão' && Number(m.comp) === 40000 && m.pos === null && intRiscoOferta(m) && mp && !mp.abaixo && I.alertas === 1, [m, mp && mp.spread, I.alertas]); });
caso('V3', () => { const c = NOVO();
  LEGADO.forEach(id => { const r = MUD(c, x => comConverterSaca(x, { venda: id, fat: '60', fonte: 'Contrato ' + id + ' (teste)', ator: 'Ana', chave: 'T-INT-' + id })); if (r.erro) throw new Error(id + ': ' + r.erro); });
  const I = intVendas(c, HOJE); const s = I.posicao.find(p => p.prod === 'Soja em grão'); const pr = I.prods.find(p => p.prod === 'Soja em grão');
  ok('V3 com a massa da saca conferida (60 kg), a soja sai do "Suspenso": % = vendido ÷ oferta e o preço médio volta com a diferença à referência',
    s && s.est !== 'Suspenso' && s.amb.length === 0 && Number(s.comp) > 0 && perto(s.pos, Number(s.comp) / Number(s.oferta)) && pr && pr.medC !== null && perto(pr.spread, (Number(pr.medC) - Number(pr.ref)) / Number(pr.ref)),
    [s, pr && [pr.medC, pr.ref, pr.spread]]); });
caso('V4', () => { const I = intVendas(NOVO(), HOJE); const ruins = I.cli.filter(x => !perto(x.liq, Number(x.preco) - Number(x.frete) - Number(x.preco) * 0.012 * x.dias / 30) || (x.retira && Number(x.frete) !== 0));
  ok('V4 recebimento líquido de cada venda = preço − frete − custo do prazo (retirada: frete zero); só venda com preço', I.cli.length > 0 && !ruins.length && I.cli.every(x => x.preco !== null && x.preco !== undefined), ruins.slice(0, 2)); });

/* ---------- Compras (C) contra o oráculo Python ---------- */
caso('C1', () => { const I = intCompras(INTC, HOJE); const dif = I.itens.filter(i => { const o = ORA.itens[i.nome]; return !o || (o.melhor === null ? i.melhor !== null : !(i.melhor && perto(i.melhor.preco, o.melhor) && i.melhor.f === o.f)); });
  ok('C1 melhor cotação válida de cada insumo = menor preço entre as válidas (oráculo Python, ' + ORA.n_itens + ' insumos)', I.itens.length === ORA.n_itens && !dif.length, dif.map(i => [i.nome, i.melhor, ORA.itens[i.nome]]).slice(0, 3)); });
caso('C2', () => { const I = intCompras(INTC, HOJE); const dif = I.itens.filter(i => { const o = ORA.itens[i.nome]; return o.vref === null ? i.vRef !== null : !perto(i.vRef, o.vref); });
  ok('C2 diferença da melhor cotação à referência = (cotação − referência) ÷ referência, igual ao oráculo', !dif.length, dif.map(i => [i.nome, i.vRef, ORA.itens[i.nome].vref]).slice(0, 3)); });
caso('C3', () => { const I = intCompras(INTC, HOJE); ok('C3 economia = Σ qtd × (referência − melhor) só onde a melhor é menor, igual ao oráculo (R$ ' + ORA.eco + ')', perto(I.economia, ORA.eco, 0.01), [I.economia, ORA.eco]); });
caso('C4', () => { const I = intCompras(INTC, HOJE); ok('C4 R$/ha da safra = Σ qtd × referência ÷ área, igual ao oráculo', perto(I.rshaTot, ORA.rsha, 0.01), [I.rshaTot, ORA.rsha]); });
caso('C5', () => { const I = intCompras(INTC, HOJE); const dif = I.forn.filter(f => ORA.pont[f.id] === null ? f.pont !== null : !perto(f.pont, ORA.pont[f.id], 1e-5));
  ok('C5 pontualidade de cada fornecedor = entregas no prazo ÷ entregas (a entregar não conta), igual ao oráculo', I.forn.length > 0 && !dif.length, dif.map(f => [f.id, f.pont, ORA.pont[f.id]])); });
caso('C6', () => { const I = intCompras(INTC, '2026-10-13'); const comCot = I.itens.filter(i => i.cot.length);
  ok('C6 em 13/10/2026 todas as cotações (válidas até 02/10) venceram: nenhuma vira "melhor preço", economia zero e o insumo pede nova cotação',
    comCot.length > 0 && comCot.every(i => i.melhor === null && i.nVenc === i.cot.length && i.vRef === null && i.economia === null) && Number(I.economia) === 0 && I.vencidas === comCot.length && I.acima === 0, [I.economia, I.vencidas, comCot.length]); });
caso('C7', () => { const nome = INTC.itens[0].nome; const D2 = JSON.parse(JSON.stringify(INTC)); delete D2.cot[nome]; const i = intCompras(D2, HOJE).itens.find(x => x.nome === nome);
  ok('C7 insumo sem cotação: melhor, diferença e economia null (ausente ≠ zero) e não conta como vencida', i && i.melhor === null && i.vRef === null && i.economia === null && i.nVenc === 0, i); });
caso('C8', () => { const it = INTC.itens[0]; const mk = f => { const D2 = JSON.parse(JSON.stringify(INTC)); D2.cot[it.nome] = [{ f: 'F01', nome: 'Teste', preco: String(Number(it.ref) * f), prazo: 5, frete: 'CIF', pag: '30 dias', validade: '30/12/2026' }]; return intCompras(D2, HOJE).itens.find(x => x.nome === it.nome); };
  const a = mk(1.06), b = mk(1.05); ok('C8 sem meta: 6% e 5% preservados sem alerta', !a.acima && !b.acima && perto(a.vRef,0.06) && perto(b.vRef,0.05), [a.vRef, b.vRef]); });
caso('C9', () => { intCompras(INTC, '2026-10-13'); const algum = Object.values(INTC.cot).some(cs => cs.some(x => 'venc' in x));
  ok('C9 a conta não altera os dados de entrada (INTC sem campo novo depois de duas chamadas)', !algum); });

/* ---------- INTEL-02 · preço, tendência e melhor mês (P) contra o oráculo Python ---------- */
const PZ = intPrecos(INTP); const OP = ORA.precos;
const dif4 = (a, b) => !perto(a, b, 1e-4);
caso('P1', () => { const ruins = []; PZ.vendas.filter(v => !v.semSerie).concat(PZ.compras).forEach(x => { const o = (OP.vendas[x.prod] || OP.compras[x.nome]); x.z.idx.forEach((v, k) => { if (dif4(v, o.idx[k])) ruins.push([x.prod || x.nome, k, v, o.idx[k]]); }); });
  ok('P1 índice sazonal de cada mês = média, nas janelas de 12 meses, de preço ÷ média da janela (oráculo, ' + (PZ.vendas.length - 1 + PZ.compras.length) + ' séries)', !ruins.length, ruins.slice(0, 3)); });
caso('P2', () => { const ruins = PZ.vendas.filter(v => !v.semSerie && v.melhor !== OP.vendas[v.prod].melhor).map(v => v.prod).concat(PZ.compras.filter(c => c.melhor !== OP.compras[c.nome].melhor).map(c => c.nome));
  ok('P2 melhor mês: venda = o de maior índice; compra = o de menor (empate: o mais cedo), igual ao oráculo', !ruins.length, ruins); });
caso('P3', () => { const ruins = PZ.vendas.filter(v => !v.semSerie).concat(PZ.compras).filter(x => { const o = OP.vendas[x.prod] || OP.compras[x.nome]; return x.tend !== o.tend || dif4(x.tv, o.tv); }).map(x => [x.prod || x.nome, x.tend, x.tv]);
  const est = new Set(PZ.vendas.filter(v => !v.semSerie).concat(PZ.compras).map(x => x.tend));
  ok('P3 tendência sem a época (3 meses contra os 3 anteriores, preço ÷ índice) = oráculo; a semente mostra Alta, Queda e Estável', !ruins.length && est.has('Alta') && est.has('Queda') && est.has('Estável'), [ruins.slice(0, 3), [...est]]); });
caso('P4', () => { const ruins = PZ.vendas.filter(v => !v.semSerie).concat(PZ.compras).filter(x => { const o = OP.vendas[x.prod] || OP.compras[x.nome]; return dif4(x.norma.vs, o.vs) || !perto(x.norma.esp, o.esp, 0.01); }).map(x => x.prod || x.nome);
  ok('P4 normal do mês = média dos últimos 12 meses × índice do mês; agora vs normal = oráculo', !ruins.length, ruins); });
caso('P5', () => { const rv = PZ.vendas.filter(v => !v.semSerie && v.rec !== OP.vendas[v.prod].rec).map(v => [v.prod, v.rec, OP.vendas[v.prod].rec]);
  const rc = PZ.compras.filter(c => c.rec !== OP.compras[c.nome].rec || (OP.compras[c.nome].eco === null ? c.eco !== null : !perto(c.eco, OP.compras[c.nome].eco, 0.5))).map(c => [c.nome, c.rec, OP.compras[c.nome].rec, c.eco]);
  /* tolerância: o motor guarda a razão com 6 casas; em R$ 75 mil isso dá centavos (R$ 0,50 por linha, R$ 1 no total) */
  ok('P5 o que fazer e a economia de cada linha = oráculo; economia total R$ ' + Number(OP.economia).toFixed(2), !rv.length && !rc.length && perto(PZ.economia, OP.economia, 1), [rv, rc.slice(0, 3), PZ.economia]); });
caso('P6', () => { const f = PZ.vendas.find(v => v.prod === 'Feijão em grão');
  ok('P6 ausente ≠ zero: Feijão sem fonte de preço fica "sem série" (sem preço, sem melhor mês, sem recomendação inventada)', f && f.semSerie && f.atual === undefined && f.rec === undefined, f); });
/* série construída: jan–jun 5% abaixo da média, jul–dez 5% acima, sem tendência; termina em set */
const SZ = (() => { const s = []; for (let i = 0; i < 36; i++) { const a = 2023 + Math.floor((9 + i) / 12), m = (9 + i) % 12; s.push({ m: a + '-' + String(m + 1).padStart(2, '0'), p: m < 6 ? '95' : '105' }); } return s; })();
caso('P7', () => { const z = intSazonal(SZ); const t = intTendencia(SZ, z); const cru = intRel(intMedia(SZ.slice(-3).map(x => x.p)), intMedia(SZ.slice(-6, -3).map(x => x.p)));
  ok('P7 contraprova da tendência: série só com a época sai "Estável" sem a época; a conta crua (jul–set contra abr–jun) diria +10,5% (Alta)', t.est === 'Estável' && perto(t.v, 0, 1e-6) && perto(cru, 0.105263, 1e-5), [t, cru]); });
caso('P8', () => { const a = intMomentoCompra(SZ, '2026-09-30'), b = intMomentoCompra(SZ, '2027-01-20');
  ok('P8 contraprova do prazo: necessidade (menos a entrega) neste mês → "Comprar agora"; até jan → "Esperar" até jan, 9,5% mais barato', a.rec === 'Comprar agora' && b.rec === 'Esperar' && b.mesAlvo === 0 && perto(b.econ, 1 - 95 / 105, 1e-5), [a.rec, b.rec, b.mesAlvo, b.econ]); });
caso('P9', () => { const sv = SZ.slice(0, 33);   /* termina em jun: jul paga 10,5% a mais */ const n = intMomentoVenda(sv, false), p = intMomentoVenda(sv, true);
  ok('P9 perecível não espera: a mesma série que manda esperar o produto armazenável manda o perecível "Vender na colheita"', n.rec === 'Esperar' && p.rec === 'Vender na colheita', [n.rec, p.rec, n.liq]); });
/* P11–P13 · revisão Codex INTEL-02-LIQUIDO-01 (S2): série de 60 meses (out/2021–set/2026), 100 em todos os meses, outubro 110 e agosto 112; setembro é agora.
   Outubro (1 mês) paga 110/100 − 1 − 1,2 % = +8,8 % líquido; agosto (11 meses) 112/100 − 1 − 13,2 % = −1,2 %. O certo é esperar até outubro. */
const SL = (out, ago) => { const s = []; for (let i = 0; i < 60; i++) { const a = 2021 + Math.floor((9 + i) / 12), m = (9 + i) % 12; s.push({ m: a + '-' + String(m + 1).padStart(2, '0'), p: m === 9 ? out : m === 7 ? ago : '100' }); } return s; };
caso('P11', () => { const r = intMomentoVenda(SL('110', '112'), false); ok('P11 o mês que paga a espera vence o de maior preço bruto: Esperar até outubro (+8,8 % líquido), não "Sem ganho em esperar" por agosto', r.rec === 'Esperar' && r.mesAlvo === 9 && r.bd === 1 && Math.abs(Number(r.liq) - 0.088) <= 1e-5 && r.bdBruto === 11, [r.rec, r.mesAlvo, r.bd, String(r.liq), r.bdBruto]); });
caso('P12', () => { const r = intMomentoVenda(SL('102', '112'), false); ok('P12 sem ganho líquido em nenhum mês (outubro +0,8 %, agosto −1,2 %): continua "Sem ganho em esperar"', r.rec === 'Sem ganho em esperar' && Number(r.liq) < 0.03, [r.rec, String(r.liq), r.bd]); });
caso('P13', () => { const s = SL('100', '100'); s.forEach(x => { if (x.m.slice(5) === '11' || x.m.slice(5) === '12') x.p = x.m.slice(5) === '11' ? '110' : '111.2'; });
  const r = intMomentoVenda(s, false); ok('P13 empate de ganho líquido (novembro 2 meses +7,6 %, dezembro 3 meses +7,6 %): o mais cedo (novembro); perecível segue "Vender na colheita"', r.rec === 'Esperar' && r.mesAlvo === 10 && intMomentoVenda(s, true).rec === 'Vender na colheita', [r.rec, r.mesAlvo, String(r.liq)]); });
caso('P10', () => { const antes = JSON.stringify(INTP); intPrecos(INTP); intPrecos(INTP); ok('P10 a conta não altera a série de entrada (INTP igual depois de duas chamadas)', JSON.stringify(INTP) === antes); });
