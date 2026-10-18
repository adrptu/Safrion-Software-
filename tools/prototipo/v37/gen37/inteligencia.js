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

/* ---------- INTEL-02 · preço, tendência e melhor mês (pedido do proprietário, 13/10/2026) ----------
   Série mensal (INTP, sintética e rotulada). Índice sazonal do mês = média, nas janelas de 12 meses que terminam no mês mais
   recente, de (preço do mês ÷ média da janela); só janelas completas. Tendência = média dos 3 últimos meses contra os 3
   anteriores, sem o efeito da época (preço ÷ índice do mês; ±3% muda o sinal). Normal do mês = média dos últimos 12 meses ×
   índice do mês. Histórico não é previsão. */
const INT_MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
const INT_TEND = '0.03';   // tendência: ±3%
const INT_SAZ = '0.03';    // vantagem sazonal mínima para recomendar esperar (venda: já descontado o custo do dinheiro)
const INT_NORMA = '0.05';  // preço fora do normal do mês: ±5%
function intMes(m) { return Number(String(m).slice(5, 7)) - 1; }
function intMesTxt(i) { return INT_MESES[((i % 12) + 12) % 12]; }
function intMedia(xs) { return xs && xs.length ? prDiv(prSoma(xs), xs.length) : null; }
function intSazonal(s) { const n = Math.floor((s || []).length / 12); if (n < 2) return null; const acc = Array.from({ length: 12 }, () => []);
  for (let w = 0; w < n; w++) { const jan = s.slice(s.length - 12 * (w + 1), s.length - 12 * w); const med = intMedia(jan.map(x => x.p)); jan.forEach(x => acc[intMes(x.m)].push(prDiv(x.p, med))); }
  return { idx: acc.map(intMedia), anos: n }; }
function intTendencia(s, z) { if (!s || s.length < 6 || !z) return { v: null, est: 'Sem série' }; const ds = x => prDiv(x.p, z.idx[intMes(x.m)]);   // sem o efeito da época
  const v = intRel(intMedia(s.slice(-3).map(ds)), intMedia(s.slice(-6, -3).map(ds)));
  return { v, est: prCmp(v, INT_TEND) > 0 ? 'Alta' : prCmp(v, prSub(0, INT_TEND)) < 0 ? 'Queda' : 'Estável' }; }
function intVarK(s, k) { return s && s.length > k ? intRel(s[s.length - 1].p, s[s.length - 1 - k].p) : null; }
function intNorma(s, z) { const m = intMes(s[s.length - 1].m); const esp = prMul(intMedia(s.slice(-12).map(x => x.p)), z.idx[m]); return { esp, vs: intRel(s[s.length - 1].p, esp) }; }
function intExtremo(z, maior) { let b = 0; for (let k = 1; k < 12; k++) { const c = prCmp(z.idx[k], z.idx[b]); if (maior ? c > 0 : c < 0) b = k; } return b; }   // empate: o mês mais cedo
/* comum aos dois lados: preço de agora, variações, tendência, sazonalidade e normal do mês */
/* INTEL-03 (18/10/2026): com o IPCA da série (INTP.ipca), o índice do mês é o mesmo do bloco "Mercado e momento": sem inflação e sem a tendência
   do histórico (int3Real + int3SemTendencia + int3Sazonal). Antes, o índice nominal e com tendência favorecia o último mês de cada janela (a soja
   saía "melhor mês: set" = o mês de agora). Sem IPCA (séries montadas nos testes), segue o índice nominal de sempre */
function intZ(s, ipca) { if (!ipca) return intSazonal(s); const r = int3Real(s, ipca), sem = r && int3SemTendencia(r), z = sem && int3Sazonal(sem); return z && z.N >= 2 ? { idx: z.idx, anos: z.N } : null; }
function intLinhaPreco(s, ipca) { if (!s || !s.length) return null; const z = intZ(s, ipca); const ult = s[s.length - 1]; const t = intTendencia(s, z);
  return { s, z, atual: ult.p, mesAtual: intMes(ult.m), ref: ult.m, v1: intVarK(s, 1), v12: intVarK(s, 12), tend: t.est, tv: t.v, norma: z ? intNorma(s, z) : null }; }
/* venda: melhor mês dos próximos 12; esperar só compensa se o ganho histórico menos o custo do dinheiro (1,2% a.m.) passar de 3%.
   Perecível não espera: a época boa orienta o plantio e a colheita, e a venda acompanha a colheita */
function intMomentoVenda(s, perecivel, ipca) { const L = intLinhaPreco(s, ipca); if (!L || !L.z) return L; const z = L.z, m0 = L.mesAtual; let bdB = 0;
  for (let d = 1; d < 12; d++) if (prCmp(z.idx[(m0 + d) % 12], z.idx[(m0 + bdB) % 12]) > 0) bdB = d;   // melhor mês bruto à frente (0 = agora)
  /* revisão Codex INTEL-02-LIQUIDO-01 (S2): o mês-alvo é o de maior ganho LÍQUIDO nos próximos 11 meses (índice do mês ÷ agora − 1 − custo do
     dinheiro × meses de espera); empate: o mais cedo (não esperar sem benefício). Antes o alvo era o maior índice bruto, e um mês próximo que
     pagava a espera ficava de fora ("Sem ganho em esperar" falso). */
  let bd = 0, liq = 0, ganho = 0;
  if (bdB > 0) { liq = null; for (let d = 1; d < 12; d++) { const g = intRel(z.idx[(m0 + d) % 12], z.idx[m0]), l = prSub(g, prMul(INT_TAXA_MES, d)); if (liq === null || prCmp(l, liq) > 0) { liq = l; bd = d; ganho = g; } } }
  const rec = perecivel ? 'Vender na colheita' : (bdB === 0 || prCmp(L.norma.vs, INT_NORMA) >= 0) ? 'Vender agora' : prCmp(liq, INT_SAZ) >= 0 ? 'Esperar' : 'Sem ganho em esperar';
  return Object.assign(L, { melhor: intExtremo(z, true), bdBruto: bdB, bd, mesAlvo: (m0 + bd) % 12, ganho, liq, rec, perecivel: !!perecivel }); }
/* compra: melhor mês entre agora e o último dia para pedir e receber antes da necessidade (Planejar safra − prazo de entrega) */
function intMesesAte(de, ate) { return (Number(ate.slice(0, 4)) - Number(de.slice(0, 4))) * 12 + Number(ate.slice(5, 7)) - Number(de.slice(5, 7)); }
function intMomentoCompra(s, lim, ipca) { const L = intLinhaPreco(s, ipca); if (!L || !L.z) return L; const z = L.z, m0 = L.mesAtual;
  const D = lim ? Math.max(0, Math.min(11, intMesesAte(L.ref, lim))) : 11; let bd = 0;
  for (let d = 1; d <= D; d++) if (prCmp(z.idx[(m0 + d) % 12], z.idx[(m0 + bd) % 12]) < 0) bd = d;
  const econ = prSub(1, prDiv(z.idx[(m0 + bd) % 12], z.idx[m0]));
  const rec = (D === 0 || bd === 0 || prCmp(L.norma.vs, prSub(0, INT_NORMA)) <= 0) ? 'Comprar agora' : prCmp(econ, INT_SAZ) >= 0 ? 'Esperar' : 'Comprar até a necessidade';
  return Object.assign(L, { melhor: intExtremo(z, false), D, bd, mesAlvo: (m0 + bd) % 12, econ, rec, lim }); }
function intPrecos(P) { P = P || {};
  const vendas = (P.vendas || []).map(v => Object.assign({ prod: v.prod, un: v.un, fonte: v.fonte }, v.serie && v.serie.length ? intMomentoVenda(v.serie, v.perecivel, P.ipca) : { semSerie: true }));
  const compras = (P.compras || []).map(c => { const M = intMomentoCompra(c.serie, c.lim, P.ipca); const eco = M && M.rec === 'Esperar' ? prMul(prMul(c.qtd, M.atual), M.econ) : null;
    return Object.assign({ nome: c.nome, grupo: c.grupo, un: c.un, qtd: c.qtd, nec: c.nec, prazo: c.prazo }, M, { eco }); });
  return { vendas, compras, economia: prSoma(compras.map(c => c.eco || 0)) }; }

/* ---------- INTEL-03 · mercado e momento por período (pedido do proprietário, 18/10/2026; docs/inteligencia/INTEL-03.md) ----------
   Preço real = nominal × IPCA(último mês) ÷ IPCA(mês): as comparações entre anos ficam sem inflação; a tela mostra o nominal e diz isso.
   Janela de n meses (12, 24, 36 ou 48) que termina no mês mais recente; N = n ÷ 12 anos completos.
   Índice do mês m: preço real sem a tendência do período (reta de mínimos quadrados); em cada ano da janela, o de m ÷ a média daquele ano; o índice
   é a média desses N valores, com a faixa (menor e maior).
   Melhor mês: venda, o maior índice; compra, o menor; empate, o mais cedo. Acerto: anos em que o índice do melhor mês ficou do lado bom de 1.
   Evidência: Forte com N ≥ 3, acerto ≥ N − 1 e amplitude (maior − menor índice) ≥ 3%; Sem padrão com N = 1 (um ano é um exemplo) ou
   amplitude < 3%; senão Fraca. Selo só com evidência (nunca com 12 meses): pela posição do preço de agora no período (percentil).
   Histórico não é previsão; nada aqui é cotação real (séries sintéticas e rotuladas). */
const INT3_PER = [12, 24, 36, 48];
const INT3_AMP = '0.03';
const INT3_ALTO = 70, INT3_BAIXO = 30;   // percentil do preço de agora no período: acima de 70 é caro, abaixo de 30 é barato (parâmetro, default)
function int3Real(s, ipca) { if (!s || !s.length || !ipca) return null; const ult = ipca[s[s.length - 1].m]; if (!intOk(ult)) return null; const out = [];
  for (const x of s) { const i = ipca[x.m]; if (!intOk(i)) return null; out.push({ m: x.m, p: prMulDiv(x.p, ult, i), nom: x.p }); } return out; }
function int3Percentil(xs, p) { if (!xs || xs.length < 2) return null; return Math.round(xs.filter(x => prCmp(x, p) < 0).length / (xs.length - 1) * 100); }
function int3Sazonal(js) { const N = Math.floor(js.length / 12); if (N < 1) return null; const anos = [];
  for (let w = 0; w < N; w++) { const jan = js.slice(js.length - 12 * (w + 1), js.length - 12 * w), med = intMedia(jan.map(x => x.p)), r = Array(12).fill(null);
    jan.forEach(x => { r[intMes(x.m)] = prDiv(x.p, med); }); anos.push(r); }
  const idx = [], min = [], max = [];
  for (let k = 0; k < 12; k++) { const v = anos.map(a => a[k]); idx.push(intMedia(v)); min.push(v.reduce((a, b) => prCmp(b, a) < 0 ? b : a)); max.push(v.reduce((a, b) => prCmp(b, a) > 0 ? b : a)); }
  return { N, anos, idx, min, max }; }
/* tendência linear do período (mínimos quadrados, em decimal): preço sem a tendência = preço real ÷ reta do período. Sem isso, um período em
   alta favorece sempre o último mês de cada ano da janela (achado do próprio teste A4, 18/10). Reta ≤ 0 em algum mês = sem leitura */
function int3SemTendencia(js) { const n = js.length, mt = (n - 1) / 2, mp = intMedia(js.map(x => x.p)); let sxy = '0', sxx = '0';
  js.forEach((x, t) => { const dt = String(t - mt); sxy = prSoma([sxy, prMul(dt, prSub(x.p, mp))]); sxx = prSoma([sxx, prMul(dt, dt)]); });
  const b = prCmp(sxx, 0) > 0 ? prDiv(sxy, sxx) : '0', out = [];
  for (let t = 0; t < n; t++) { const tr = prSoma([mp, prMul(b, String(t - mt))]); if (prCmp(tr, 0) <= 0) return null; out.push({ m: js[t].m, p: prDiv(js[t].p, tr) }); }
  return out; }
function int3Leitura(serie, ipca, n, lado) { const real = int3Real(serie, ipca); if (!real) return null;
  if (real.length < n) return { n, falta: true, lado };   // período maior que a série: sem leitura (ausente ≠ zero)
  const js = real.slice(real.length - n), sem = int3SemTendencia(js); if (!sem) return null;
  const z = int3Sazonal(sem), hoje = js[js.length - 1], med = intMedia(js.map(x => x.p)), venda = lado === 'venda';
  const melhor = intExtremo(z, venda), bom = a => venda ? prCmp(a[melhor], 1) > 0 : prCmp(a[melhor], 1) < 0, acerto = z.anos.filter(bom).length;
  const hi = z.idx.reduce((a, b) => prCmp(b, a) > 0 ? b : a), lo = z.idx.reduce((a, b) => prCmp(b, a) < 0 ? b : a), amp = prSub(hi, lo);
  const ev = (z.N === 1 || prCmp(amp, INT3_AMP) < 0) ? 'Sem padrão' : (z.N >= 3 && acerto >= z.N - 1 ? 'Forte' : 'Fraca');
  const pct = int3Percentil(js.map(x => x.p), hoje.p), vsMed = intRel(hoje.p, med);
  const selo = ev === 'Sem padrão' ? null : venda ? (pct >= INT3_ALTO ? 'Bom momento para vender' : pct <= INT3_BAIXO ? 'Abaixo do normal' : 'Neutro')
    : (pct <= INT3_BAIXO ? 'Bom momento para comprar' : pct >= INT3_ALTO ? 'Acima do normal' : 'Neutro');
  return { n, N: z.N, lado, js, z, hoje, med, pct, vsMed, melhor, ganho: prSub(z.idx[melhor], 1), acerto, amp, ev, selo }; }
try { window.__int3 = { int3Real, int3Percentil, int3Sazonal, int3SemTendencia, int3Leitura }; } catch (e) {}
