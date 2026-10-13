/* INTEL-01 · inteligência comercial de Vendas e de Compras (pedido do proprietário, 13/10/2026; acordo 6150194122).
   Fórmulas num lugar só (ENG-011), em decimal pelos pr* do producao.js (ENG-013). Cotação, referência ou previsão ausente
   não vira zero: o indicador fica null e a tela diz "sem cotação" ou "sem previsão". Só sinal com fonte e regra; a decisão
   de vender ou comprar é de quem vende ou compra. Dados sintéticos. */
const INT_TAXA_MES = '0.012';    // custo financeiro do prazo de recebimento: 1,2% ao mês (parâmetro sintético do proprietário)
const INT_LIM = '0.05';          // alerta: venda 5% abaixo da referência; cotação 5% acima da referência
const INT_FRETE_T = '190';       // frete de referência R$/t (Rota Sul, contrato vigente sintético; dados_comercial.FRETE)
function intOk(x) { return x !== null && x !== undefined && x !== '' && prCmp(x, 0) > 0; }
/* diferença relativa: (a − b) ÷ b; null se b ausente */
function intRel(a, b) { return (intOk(b) && a !== null && a !== undefined) ? prDiv(prSub(a, b), b) : null; }
function intSpread(preco, ref) { return intRel(preco, ref); }                 // venda: preço praticado × referência
function intVariacao(novo, antigo) { return intRel(novo, antigo); }           // compra: cotação × último preço pago
function intPosicao(vendido, oferta) { return intOk(oferta) ? prDiv(vendido || 0, oferta) : null; }   // safra comercializada
/* recebimento líquido por unidade: preço − frete − preço × taxa × dias ÷ 30 (custo de esperar o pagamento) */
function intLiquido(preco, frete, dias, taxa) { const fin = prMulDiv(prMul(preco, taxa === undefined ? INT_TAXA_MES : taxa), dias || 0, 30);
  return prSub(prSub(preco, frete || 0), fin); }
function intFreteUn(massaKg) { return prMulDiv(INT_FRETE_T, massaKg || 0, 1000); }   // R$/t × kg da unidade ÷ 1000
/* pontualidade: entregas no prazo ÷ entregas (null sem entrega) */
function intPontualidade(ents) { const n = (ents || []).length; if (!n) return null; return prDiv(ents.filter(e => !(e.atraso > 0)).length, n); }
function intRsHa(itens, area) { return intOk(area) ? prDiv(prSoma((itens || []).map(i => prMul(i.qtd, i.preco))), area) : null; }
function intPct(f, d) { if (f === null || f === undefined) return '—'; const t = prFmt(prMul(f, 100), d === undefined ? 1 : d); return (prCmp(f, 0) > 0 ? '+' : '') + t + '%'; }
function intAbaixo(f) { return f !== null && prCmp(f, prSub(0, INT_LIM)) < 0; }   // pior que −5%
function intAcima(f) { return f !== null && prCmp(f, INT_LIM) > 0; }               // pior que +5%

/* ---------- Vendas ---------- */
function intVendas(c, hoje) { hoje = hoje || prHoje(); const P = prP(c);
  const prods = comPrecos(c, hoje).map(x => { const ref = x.ref ? x.ref.p : null; const sp = x.medC === null ? null : intSpread(x.medC, ref);
    return { prod: x.prod, cu: x.cu, vend: x.vend, medC: x.medC, ref, fonte: x.ref ? x.ref.fonte : '', spread: sp, abaixo: intAbaixo(sp), vendas: x.vendas, amb: x.amb || [] }; });
  /* posição: compromissos ÷ oferta (estoque apto + previsão publicada), por produto, somando as linhas do Painel comercial (horizonte 's').
     Venda com saca a conferir (A-17) suspende a conta do produto, como no Painel; período com venda e sem versão publicada não vira oferta zero */
  const pos = {}; comPainel(c, hoje, 's').forEach(r => { const p = pos[r.prod] = pos[r.prod] || { prod: r.prod, cu: r.cu, oferta: 0, comp: 0, amb: [], semPrev: false };
    if (r.tipo === 'est' || r.tem) p.oferta = prSoma([p.oferta, r.oferta || 0]); else p.semPrev = true;
    p.comp = prSoma([p.comp, r.comp || 0]); (r.amb || []).forEach(id => { if (p.amb.indexOf(id) < 0) p.amb.push(id); }); });
  const posicao = Object.values(pos).map(p => { const susp = p.amb.length > 0; const pc = susp ? null : intPosicao(p.comp, p.oferta);
    const est = susp ? 'Suspenso' : (pc === null ? 'Sem previsão' : (prCmp(pc, 1) > 0 ? 'Vendido acima da oferta' : 'Dentro da oferta'));
    return Object.assign(p, { pos: pc, livre: susp ? null : prSub(p.oferta, p.comp), est }); });
  /* clientes: recebimento líquido por unidade (preço − frete − custo do prazo), só venda com preço e massa conhecida */
  const cli = Object.values(P.pedidos).filter(v => comNat(v) === 'Venda' && v.preco !== undefined && v.preco !== null && !prAmb(v)).map(v => {
    const cu = comCultura(v); const k = comCond(v.cond); const dias = k && k.dias !== null ? k.dias : 0; const retira = v.modal === 'retira';
    const frete = retira ? '0' : intFreteUn(comMassa(cu)); const liq = intLiquido(v.preco, frete, dias);
    return { id: v.id, cliente: v.cliente, prod: v.prod, cu, preco: v.preco, frete, dias, retira, fin: prSub(prSub(v.preco, frete), liq), liq }; });
  return { prods, posicao, cli, alertas: prods.filter(p => p.abaixo).length + posicao.filter(intRiscoOferta).length }; }
/* risco de oferta: vendido acima da oferta, ou venda sem oferta publicada */
function intRiscoOferta(p) { return p.est === 'Vendido acima da oferta' || (p.est === 'Sem previsão' && prCmp(p.comp, 0) > 0); }

/* ---------- Compras ---------- */
function intIsoBr(d) { const m = /^(\d\d)\/(\d\d)\/(\d{4})$/.exec(String(d || '')); return m ? m[3] + '-' + m[2] + '-' + m[1] : ''; }
/* cotação vencida (validade antes de hoje) não vira "melhor preço": fica listada, marcada, e pede nova cotação */
function intCompras(D, hoje) { hoje = hoje || prHoje(); const hist = D.hist || [];
  const itens = D.itens.map(i => { const cot = (D.cot[i.nome] || []).map(x => Object.assign({}, x, { venc: !!intIsoBr(x.validade) && intIsoBr(x.validade) < hoje })).sort((a, b) => prCmp(a.preco, b.preco));
    const melhor = cot.find(x => !x.venc) || null; const nVenc = cot.filter(x => x.venc).length;
    const hs = hist.filter(h => h.item === i.nome).sort((a, b) => a.d < b.d ? 1 : -1); const ult = hs[0] || null;
    const vRef = melhor ? intRel(melhor.preco, i.ref) : null; const vUlt = melhor && ult ? intVariacao(melhor.preco, ult.preco) : null;
    return { nome: i.nome, grupo: i.grupo, un: i.un, qtd: i.qtd, ref: i.ref, cot, melhor, nVenc, ult, hs, vRef, vUlt, acima: intAcima(vRef),
             economia: melhor ? prMul(i.qtd, prSub(i.ref, melhor.preco)) : null }; });
  const forn = D.forn.map(f => { const cs = []; itens.forEach(i => i.cot.filter(x => x.f === f.id && !x.venc).forEach(x => cs.push(intRel(x.preco, i.ref))));
    const hs = hist.filter(h => h.f === f.id); const ents = hs.filter(h => h.entregue).map(h => ({ atraso: h.atraso }));
    return { id: f.id, nome: f.nome, n: cs.length, rel: cs.length ? prDiv(prSoma(cs), cs.length) : null, prazo: f.prazo, pont: intPontualidade(ents), nEnt: ents.length,
             atr: ents.filter(e => e.atraso > 0).length, ult: hs.slice().sort((a, b) => a.d < b.d ? 1 : -1)[0] || null }; }).filter(f => f.n || f.nEnt);
  const grupos = {}; itens.forEach(i => { const g = grupos[i.grupo] = grupos[i.grupo] || { grupo: i.grupo, itens: [] }; g.itens.push({ qtd: i.qtd, preco: i.ref }); });
  const porHa = Object.values(grupos).map(g => ({ grupo: g.grupo, total: prSoma(g.itens.map(x => prMul(x.qtd, x.preco))), rsha: intRsHa(g.itens, D.area) }))
    .sort((a, b) => prCmp(b.total, a.total));
  return { itens, forn, porHa, area: D.area, rshaTot: intRsHa(itens.map(i => ({ qtd: i.qtd, preco: i.ref })), D.area),
           economia: prSoma(itens.filter(i => i.economia !== null && prCmp(i.economia, 0) > 0).map(i => i.economia)), acima: itens.filter(i => i.acima).length,
           vencidas: itens.filter(i => !i.melhor && i.nVenc).length }; }
try { window.__int = { intSpread, intVariacao, intPosicao, intLiquido, intPontualidade, intRsHa, intVendas, intCompras }; } catch (e) {}
