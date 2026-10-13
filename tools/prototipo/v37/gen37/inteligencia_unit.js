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
  ok('F1 diferença à referência: (2,90 − 3,10) ÷ 3,10 = −6,45% e vira alerta (pior que −5%)', perto(s, -0.0645161, 1e-6) && intAbaixo(s) && intPct(s) === '−6,5%', [s, intPct(s)]); });   /* sinal de menos tipográfico, como na tela */
caso('F2', () => ok('F2 ausente ≠ zero: sem referência a diferença é null, sem alerta e "—" na tela', intSpread('2.90', null) === null && intSpread('2.90', '0') === null && !intAbaixo(null) && intPct(null) === '—', [intSpread('2.90', null)]));
caso('F3', () => ok('F3 posição: 25 ÷ 100 = 25%; oferta zero ou ausente não vira 0% (null)', perto(intPosicao(25, 100), 0.25) && intPosicao(30000, 0) === null && intPosicao(10, null) === null, [intPosicao(25, 100), intPosicao(30000, 0)]));
caso('F4', () => { const a = intLiquido('3.00', '0.19', 30, '0.012'), b = intLiquido('3.00', '0.19', 0, '0.012');
  ok('F4 líquido = preço − frete − preço × 1,2% × dias ÷ 30: 3,00 − 0,19 − 0,036 = 2,774 (30 d); à vista 2,81', perto(a, 2.774) && perto(b, 2.81), [a, b]); });
caso('F5', () => ok('F5 frete por unidade = R$ 190/t × kg da unidade ÷ 1000: caixa de 20 kg R$ 3,80; kg R$ 0,19', perto(intFreteUn(20), 3.8) && perto(intFreteUn(1), 0.19), [intFreteUn(20), intFreteUn(1)]));
caso('F6', () => ok('F6 pontualidade = no prazo ÷ entregas: 2 de 3 = 66,7%; sem entrega é null (não 0% nem 100%)', perto(intPontualidade([{ atraso: 0 }, { atraso: 3 }, { atraso: 0 }]), 2 / 3, 1e-5) && intPontualidade([]) === null, intPontualidade([{ atraso: 0 }, { atraso: 3 }, { atraso: 0 }])));
caso('F7', () => ok('F7 R$/ha = Σ(qtd × preço) ÷ área: (100 × 2,5 + 10 × 30) ÷ 50 = 11; área zero é null', perto(intRsHa([{ qtd: '100', preco: '2.5' }, { qtd: '10', preco: '30' }], '50'), 11) && intRsHa([{ qtd: '1', preco: '1' }], '0') === null));
caso('F8', () => ok('F8 limites de 5%: exatamente +5% ou −5% não alerta; +5,01% e −5,01% alertam', !intAcima('0.05') && intAcima('0.0501') && !intAbaixo('-0.05') && intAbaixo('-0.0501')));

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
  const a = mk(1.06), b = mk(1.05); ok('C8 cotação 6% acima da referência alerta; exatamente 5% acima não', a.acima && !b.acima, [a.vRef, b.vRef]); });
caso('C9', () => { intCompras(INTC, '2026-10-13'); const algum = Object.values(INTC.cot).some(cs => cs.some(x => 'venc' in x));
  ok('C9 a conta não altera os dados de entrada (INTC sem campo novo depois de duas chamadas)', !algum); });
