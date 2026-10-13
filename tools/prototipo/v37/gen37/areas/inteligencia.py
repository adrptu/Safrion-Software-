# -*- coding: utf-8 -*-
"""INTEL-01 · inteligência comercial, específica de cada lado (pedido do proprietário, 13/10/2026; acordo 6150194122).
IV · Comercial › Inteligência de vendas: preço praticado × referência de mercado, safra comercializada e recebimento
     líquido por venda (preço − frete − custo do prazo). Lê o estado (vendas, previsão publicada, estoque) e COMC.
IC · Suprimentos › Inteligência de compras: preço por insumo (último pago × referência × melhor cotação), fornecedores
     (preço relativo, prazo e pontualidade) e custo de insumos por hectare da safra. Lê dados_inteligencia (INTC).
Fórmulas só em inteligencia.js (ENG-011). Telas só leem: nada é gravado aqui; a decisão é de quem vende ou compra.
Dados sintéticos; o histórico de preço pago é sintético e rotulado."""
import os
from engine import grid
from areas import vendas as V
from areas import producao as AP
import dados_inteligencia as DI

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = lambda k: '{{' + k + '}}'


def _ijs():
    return open(os.path.join(HERE, 'inteligencia.js'), encoding='utf-8').read() + '\n'


def _kpi(l, k, n):
    return (f'<div style="flex: 1 1 160px; min-width: 0; padding: 12px 16px; background: #FFFFFF; border: 1px solid {V.LINE}; border-radius: 14px; display: flex; flex-direction: column; gap: 4px;">'
            f'<div style="font-size: 11px; letter-spacing: .06em; text-transform: uppercase; color: {V.MUTED}; font-weight: 800;">{l}</div>'
            f'<div style="font-size: 22px; font-weight: 800; letter-spacing: -.01em;">{H(k)}</div><div style="font-size: 12px; color: {V.MUTED};">{H(n)}</div></div>')


def _ind(*ks):
    return '<div role="group" aria-label="Indicadores" style="display: flex; flex-wrap: wrap; gap: 10px;">' + ''.join(_kpi(*k) for k in ks) + '</div>'


# =====================================================================================================================
# IV · Inteligência de vendas
# =====================================================================================================================
IV_JS = r"""
const PR_GRIDS = { g_ivp: 1, g_ivs: 1, g_ivc: 1 };
const _g2rows0 = g2rows; g2rows = function (self, sp) { return PR_GRIDS[sp.id] ? sp.rows : _g2rows0(self, sp); };
const IV_SIT = { 'Abaixo da referência': 'red', 'Até 5% abaixo': 'gray', 'Na referência': 'green', 'Acima da referência': 'green', 'Sem cotação': 'gray', 'Saca a conferir': 'gray', 'Sem venda': 'gray' };
/* A-17: venda de saca sem a massa conferida fica fora da média; sem nenhuma venda conhecida, o preço fica suspenso (não vira zero) */
function ivSit(p) { return p.medC === null ? (p.amb.length ? 'Saca a conferir' : 'Sem venda') : p.spread === null ? 'Sem cotação' : p.abaixo ? 'Abaixo da referência' : (prCmp(p.spread, 0) > 0 ? 'Acima da referência' : prCmp(p.spread, 0) < 0 ? 'Até 5% abaixo' : 'Na referência'); }
function ivN(x) { return x === null || x === undefined ? -1e12 : Number(x); }
function ivPRow(p) { const R = y => y === null ? '—' : comPrecoTxt(p.cu, y); const sit = ivSit(p);
  return { id: 'p:' + p.prod, ro: true, v: { prod: p.prod, medc: ivN(p.medC), dif: ivN(p.spread), sit }, s: { prod: p.prod, medc: R(p.medC), ref: p.ref ? R(p.ref) : 'sem cotação', dif: intPct(p.spread), sit },
    p: { prod: [{ k: 'b', t: p.prod }], medc: [{ k: 'txt', t: R(p.medC) }].concat(p.amb.length ? [{ k: 'br' }, { k: 'mut', t: p.amb.length + ' venda(s) de saca a conferir fora da média' }] : []), ref: p.ref ? [{ k: 'txt', t: R(p.ref) }, { k: 'br' }, { k: 'mut', t: p.fonte }] : [{ k: 'mut', t: 'sem cotação (ausente ≠ zero)' }],
      dif: p.spread === null ? [{ k: 'mut', t: '—' }] : [{ k: p.abaixo ? 'cn' : 'txt', c: 'red', t: intPct(p.spread) }], sit: [{ k: 'chip', t: sit, c: IV_SIT[sit] }] } }; }
const IV_EST = { 'Dentro da oferta': 'green', 'Vendido acima da oferta': 'red', 'Sem previsão': 'gray', 'Suspenso': 'gray' };
function ivSRow(p) { const U = y => y === null ? '—' : comTxt(p.cu, y, 0); const sit = p.est;
  return { id: 's:' + p.prod, ro: true, v: { prod: p.prod, of: Number(p.oferta), comp: Number(p.comp), pos: ivN(p.pos), livre: ivN(p.livre), sit },
    s: { prod: p.prod, of: U(p.oferta), comp: U(p.comp), pos: p.pos === null ? '—' : prFmt(prMul(p.pos, 100), 0) + '%', livre: U(p.livre), sit },
    p: { prod: [{ k: 'b', t: p.prod }], of: [{ k: 'txt', t: U(p.oferta) }].concat(p.semPrev ? [{ k: 'br' }, { k: 'mut', t: 'há período com venda e sem previsão publicada' }] : []), comp: [{ k: 'txt', t: U(p.comp) }],
      pos: [{ k: 'b', t: p.pos === null ? '—' : prFmt(prMul(p.pos, 100), 0) + '%' }], livre: p.livre === null ? [{ k: 'mut', t: 'suspenso: ' + p.amb.length + ' venda(s) de saca a conferir' }] : prCmp(p.livre, 0) < 0 ? [{ k: 'chip', t: 'déficit ' + U(prSub(0, p.livre)), c: 'red' }] : [{ k: 'txt', t: U(p.livre) }],
      sit: [{ k: 'chip', t: sit, c: intRiscoOferta(p) ? 'red' : IV_EST[sit] }] } }; }
function ivCRow(x) { const R = y => comPrecoTxt(x.cu, y);
  return { id: 'c:' + x.id, ro: true, v: { id: x.id, cli: x.cliente, prod: x.prod, preco: Number(x.preco), frete: Number(x.frete), dias: x.dias, fin: Number(x.fin), liq: Number(x.liq) },
    s: { id: x.id, cli: x.cliente, prod: x.prod, preco: R(x.preco), frete: x.retira ? 'retira' : R(x.frete), dias: x.dias ? x.dias + ' d' : 'à vista', fin: R(x.fin), liq: R(x.liq) },
    p: { id: [{ k: 'b', t: x.id }], cli: [{ k: 'txt', t: x.cliente }], prod: [{ k: 'txt', t: x.prod }], preco: [{ k: 'txt', t: R(x.preco) }], frete: [{ k: x.retira ? 'mut' : 'txt', t: x.retira ? 'cliente retira' : R(x.frete) }],
      dias: [{ k: 'txt', t: x.dias ? x.dias + ' dias' : 'à vista' }], fin: [{ k: 'txt', t: R(x.fin) }], liq: [{ k: 'b', t: R(x.liq) }] } }; }
function PREVALS(self, v) { cenOuvir(self); prTopo(self, v); const c = cenGet(); self._c = c; const I = intVendas(c); self._iv = I;
  self.g2pick = (gid, rid) => self.setState({ pr_sel: { g: gid, id: rid }, pr_pan: { g: gid, id: rid } });
  GR('g_ivp').rows = I.prods.map(ivPRow); GR('g_ivs').rows = I.posicao.map(ivSRow);
  GR('g_ivc').rows = I.cli.slice().sort((a, b) => prCmp(b.liq, a.liq)).map(ivCRow);
  const ab = I.prods.filter(p => p.abaixo); v.k_ab = String(ab.length); v.k_abn = ab.length ? ab.map(p => p.prod.split(' ')[0] + ' ' + intPct(p.spread)).join(' · ') : 'nenhuma venda 5% abaixo da referência';
  const rk = I.posicao.filter(intRiscoOferta);
  v.k_rk = String(rk.length); v.k_rkn = rk.length ? rk.map(p => p.prod.split(' ')[0] + ': ' + (p.est === 'Sem previsão' ? 'vendido sem previsão' : 'acima da oferta')).join(' · ') : 'vendas cobertas pela oferta';
  const best = I.cli.slice().sort((a, b) => prCmp(b.liq, a.liq))[0]; v.k_liq = best ? comPrecoTxt(best.cu, best.liq) : '—'; v.k_liqn = best ? 'melhor líquido: ' + best.id + ' · ' + best.cliente : 'sem venda com preço'; }
function ivPan(self, c, pan) { const I = self._iv; const P = prP(c);
  if (pan.g === 'g_ivp') { const p = I.prods.find(x => 'p:' + x.prod === pan.id); if (!p) return null; const R = y => y === null ? '—' : comPrecoTxt(p.cu, y);
    const vs = p.vendas.map(id => P.pedidos[id]).filter(Boolean).map(x => ({ c: [[x.id, 'b'], x.cliente, comPrecoTxtV(x), intPct(intSpread(x.preco, p.ref))], l: { t: 'Abrir venda', h: 'VEN.dc.html#' + x.id } }));
    return { title: p.prod, chip: [ivSit(p), IV_SIT[ivSit(p)]], sub: 'Preço praticado × referência de mercado (média ponderada, só venda)',
      next: p.medC === null ? (p.amb.length ? 'Preço médio suspenso: ' + p.amb.length + ' venda(s) em saca sem a massa conferida (A-17) ficam fora da média. Confira a massa no contrato.' : 'Sem venda de ' + p.prod + ' com preço.') : p.spread === null ? 'Sem cotação de referência para ' + p.prod + ': a comparação fica em branco (ausente ≠ zero).' : 'Diferença = (preço médio ' + R(p.medC) + ' − referência ' + R(p.ref) + ') ÷ referência = ' + intPct(p.spread) + '.' + (p.abaixo ? ' Abaixo do limite de −5%: revise as próximas ofertas (Contratos e pedidos · Comercial).' : ''),
      kv: [{ l: 'Preço médio contratado', v: R(p.medC) }, { l: 'Referência', v: p.ref ? R(p.ref) + ' · ' + p.fonte : 'sem cotação' }, { l: 'Diferença', v: intPct(p.spread) }],
      secs: [{ t: 'Vendas e diferença de cada uma', rows: vs, vazio: 'Nenhuma venda.' }] }; }
  if (pan.g === 'g_ivs') { const p = I.posicao.find(x => 's:' + x.prod === pan.id); if (!p) return null; const U = y => y === null ? '—' : comTxt(p.cu, y, 0);
    const amb = p.amb.map(id => P.pedidos[id]).filter(Boolean).map(x => ({ c: [[x.id, 'b'], x.cliente, 'saca sem massa conferida'], l: { t: 'Abrir venda', h: 'VEN.dc.html#' + x.id } }));
    const next = p.est === 'Suspenso' ? 'Conta suspensa: ' + p.amb.length + ' venda(s) em saca sem a massa conferida (A-17). Confira a massa da saca de cada contrato para saber quanto da safra já está vendido.'
      : p.est === 'Sem previsão' ? 'Sem oferta publicada para ' + p.prod + ': vendido ' + U(p.comp) + ' sem previsão de colheita que cubra. Publique a previsão (Colheita) ou reveja as vendas.'
      : 'Comercializado = vendido ' + U(p.comp) + ' ÷ oferta ' + U(p.oferta) + ' = ' + prFmt(prMul(p.pos, 100), 1) + '%. Livre para vender ' + U(p.livre) + '.';
    return { title: p.prod + ' · safra comercializada', chip: [p.pos === null ? p.est : prFmt(prMul(p.pos, 100), 0) + '% vendido', intRiscoOferta(p) ? 'red' : IV_EST[p.est]], sub: 'Compromissos ÷ oferta (estoque apto + previsão publicada), pelas linhas do Painel comercial',
      next, kv: [{ l: 'Oferta', v: U(p.oferta) }, { l: 'Vendido', v: U(p.comp) }, { l: 'Livre', v: p.livre === null ? 'suspenso' : U(p.livre) }],
      secs: amb.length ? [{ t: 'Vendas com saca a conferir', rows: amb }] : [], prim: comPode('vender') && p.livre !== null && prCmp(p.livre, 0) > 0 ? { t: 'Vender ' + p.prod, h: 'VEN.dc.html#nova:' + p.prod } : null }; }
  if (pan.g === 'g_ivc') { const x = I.cli.find(y => 'c:' + y.id === pan.id); if (!x) return null; const R = y => comPrecoTxt(x.cu, y);
    return { title: x.id + ' · ' + x.cliente, chip: ['Líquido ' + R(x.liq), 'green'], sub: x.prod, next: 'Líquido = preço ' + R(x.preco) + ' − frete ' + (x.retira ? 'R$ 0 (cliente retira)' : R(x.frete) + ' (R$ ' + INT_FRETE_T + '/t)') + ' − custo do prazo ' + R(x.fin) + ' (' + x.dias + ' d × 1,2% a.m.) = ' + R(x.liq) + '.',
      kv: [{ l: 'Preço', v: R(x.preco) }, { l: 'Frete', v: x.retira ? 'cliente retira' : R(x.frete) }, { l: 'Prazo de recebimento', v: x.dias ? x.dias + ' dias' : 'à vista' }, { l: 'Custo do prazo', v: R(x.fin) }, { l: 'Recebimento líquido', v: R(x.liq) }],
      secs: [{ t: 'Origem', rows: [{ c: [[x.id, 'b'], x.cliente], l: { t: 'Abrir venda', h: 'VEN.dc.html#' + x.id } }] }] }; }
  return null; }
function EXTRAVALS(self, v) { prRst(self, v); const c = self._c || cenGet(); const I = self._iv || intVendas(c); const st = self.state;
  v.cards_ivp = prCards(self, v, 'g_ivp', id => { const p = I.prods.find(x => 'p:' + x.prod === id); return p ? prCard({ t1: p.prod, num: intPct(p.spread), t2: 'Contratado ' + (p.medC === null ? '—' : comPrecoTxt(p.cu, p.medC)) + ' · referência ' + (p.ref ? comPrecoTxt(p.cu, p.ref) : 'sem cotação'), chip: [ivSit(p), IV_SIT[ivSit(p)]] }) : null; });
  v.cards_ivs = prCards(self, v, 'g_ivs', id => { const p = I.posicao.find(x => 's:' + x.prod === id); return p ? prCard({ t1: p.prod, num: p.pos === null ? '—' : prFmt(prMul(p.pos, 100), 0) + '% vendido', t2: p.livre === null ? p.est : 'Livre ' + comTxt(p.cu, p.livre, 0), chip: [p.est, intRiscoOferta(p) ? 'red' : IV_EST[p.est]] }) : null; });
  v.cards_ivc = prCards(self, v, 'g_ivc', id => { const x = I.cli.find(y => 'c:' + y.id === id); return x ? prCard({ t1: x.id + ' · ' + x.cliente, num: comPrecoTxt(x.cu, x.liq) + ' líquido', t2: x.prod + ' · preço ' + comPrecoTxt(x.cu, x.preco) }) : null; });
  prStatus(v, [I.prods.filter(p => p.abaixo).length ? I.prods.filter(p => p.abaixo).length + ' produto(s) vendido(s) abaixo da referência' : 'nenhuma venda abaixo da referência', I.posicao.filter(intRiscoOferta).length ? I.posicao.filter(intRiscoOferta).length + ' produto(s) com venda sem oferta que cubra' : 'vendas cobertas pela oferta']);
  const pan = st.pr_pan; const PP = pan ? ivPan(self, c, pan) : null; comPrimPainel(v, PP && PP.prim ? PP.prim : null, PP); prPainel(self, v, PP); }
"""


def iv():
    fname = 'IV.dc.html'; V.E._reset_screen(fname)
    g_ivp = grid([dict(k='prod', l='Produto', w=210), dict(k='medc', l='Preço médio contratado', t='num', a='r', w=180), dict(k='ref', l='Referência de mercado', w=220),
                  dict(k='dif', l='Diferença', t='num', a='r', w=120), dict(k='sit', l='Sinal', w=190)],
                 [], edit=dict(m='pick'), gid='g_ivp', total=False, qf=dict(k='sit', l='Sinal', todas='Todos'))
    g_ivs = grid([dict(k='prod', l='Produto', w=210), dict(k='of', l='Oferta da safra', t='num', a='r', w=150), dict(k='comp', l='Vendido', t='num', a='r', w=140),
                  dict(k='pos', l='Comercializado', t='num', a='r', w=140), dict(k='livre', l='Livre para vender', t='num', a='r', w=160), dict(k='sit', l='Situação', w=190)],
                 [], edit=dict(m='pick'), gid='g_ivs', total=False)
    g_ivc = grid([dict(k='id', l='Venda', w=100), dict(k='cli', l='Cliente', w=170), dict(k='prod', l='Produto', w=170), dict(k='preco', l='Preço', t='num', a='r', w=130),
                  dict(k='frete', l='Frete', t='num', a='r', w=110), dict(k='dias', l='Prazo', t='num', a='r', w=90), dict(k='fin', l='Custo do prazo', t='num', a='r', w=130),
                  dict(k='liq', l='Líquido', t='num', a='r', w=130)],
                 [], edit=dict(m='pick'), gid='g_ivc', total=False)
    V.EXTRAJS[0] = V._js(_ijs() + IV_JS)
    corpo = (_ind(('Vendas abaixo da referência', 'k_ab', 'k_abn'), ('Venda sem oferta que cubra', 'k_rk', 'k_rkn'), ('Melhor recebimento líquido', 'k_liq', 'k_liqn'))
             + AP.bloco('Preço × mercado', 'Preço médio contratado (Σ valor ÷ Σ quantidade, só venda) × referência de mercado com fonte. Abaixo de −5% vira alerta; sem cotação, fica em branco.', g_ivp + AP.cartoes('cards_ivp'))
             + AP.bloco('Safra comercializada', 'Vendido ÷ oferta da safra (previsão publicada ou estoque apto, todas as fazendas). Acima de 100% é venda maior que a oferta.', g_ivs + AP.cartoes('cards_ivs'))
             + AP.bloco('Recebimento líquido por venda', 'Preço − frete (R$ 190/t; cliente que retira não paga) − custo de esperar o pagamento (1,2% a.m.). Compare clientes pelo que fica na fazenda.', g_ivc + AP.cartoes('cards_ivc')))
    V._shell('IV', 'Inteligência de vendas', 'A que preço estou vendendo em relação ao mercado, quanto da safra já vendi e que cliente deixa mais na fazenda.', corpo, fname, 1300,
             'Números lidos do estado (vendas, previsão publicada, estoque) e da referência de mercado sintética com fonte. Nada é gravado aqui; a decisão de vender é do Comercial.')


# =====================================================================================================================
# IC · Inteligência de compras
# =====================================================================================================================
IC_JS = r"""
const PR_GRIDS = { g_ici: 1, g_icf: 1, g_ich: 1 };
const _g2rows0 = g2rows; g2rows = function (self, sp) { return PR_GRIDS[sp.id] ? sp.rows : _g2rows0(self, sp); };
function icRS(x, d) { return x === null || x === undefined ? '—' : 'R$ ' + prFmt(x, d === undefined ? 2 : d); }
function icN(x) { return x === null || x === undefined ? -1e12 : Number(x); }
function icSit(i) { return !i.melhor ? (i.nVenc ? 'Cotação vencida' : 'Sem cotação') : i.acima ? 'Cotação acima da referência' : 'Dentro da referência'; }
const IC_SITC = { 'Sem cotação': 'gray', 'Cotação vencida': 'gray', 'Cotação acima da referência': 'red', 'Dentro da referência': 'green' };
function icIRow(i) { const P = y => y === null || y === undefined ? '—' : icRS(y) + '/' + i.un; const sit = icSit(i);
  return { id: 'i:' + i.nome, ro: true, v: { nome: i.nome, grupo: i.grupo, ult: icN(i.ult && i.ult.preco), ref: Number(i.ref), mel: icN(i.melhor && i.melhor.preco), vref: icN(i.vRef), vult: icN(i.vUlt), sit },
    s: { nome: i.nome, grupo: i.grupo, ult: i.ult ? P(i.ult.preco) : '—', ref: P(i.ref), mel: i.melhor ? P(i.melhor.preco) : (i.nVenc ? 'cotação vencida' : 'sem cotação'), vref: intPct(i.vRef), vult: intPct(i.vUlt), sit },
    p: { nome: [{ k: 'b', t: i.nome }], grupo: [{ k: 'txt', t: i.grupo }], ult: i.ult ? [{ k: 'txt', t: P(i.ult.preco) }, { k: 'br' }, { k: 'mut', t: prBr(i.ult.d) + ' · ' + i.ult.nome + (i.ult.orig === 'histórico sintético' ? ' · sintético' : '') }] : [{ k: 'mut', t: 'sem compra registrada' }],
      ref: [{ k: 'txt', t: P(i.ref) }], mel: i.melhor ? [{ k: 'b', t: P(i.melhor.preco) }, { k: 'br' }, { k: 'mut', t: i.melhor.nome + ' · ' + i.melhor.prazo + ' d · ' + i.melhor.frete }] : [{ k: 'mut', t: i.nVenc ? i.nVenc + ' cotação(ões) vencida(s): peça nova' : 'sem cotação (ausente ≠ zero)' }],
      vref: [{ k: i.acima ? 'cn' : 'txt', c: 'red', t: intPct(i.vRef) }], vult: [{ k: 'txt', t: intPct(i.vUlt) }], sit: [{ k: 'chip', t: sit, c: IC_SITC[sit] }] } }; }
function icFRow(f) { const pc = x => x === null ? '—' : prFmt(prMul(x, 100), 0) + '%';
  return { id: 'f:' + f.id, ro: true, v: { nome: f.nome, n: f.n, rel: icN(f.rel), prazo: icN(f.prazo), pont: icN(f.pont) },
    s: { nome: f.nome, n: String(f.n), rel: intPct(f.rel), prazo: f.prazo === null ? '—' : String(f.prazo).replace('.', ',') + ' d', pont: pc(f.pont) },
    p: { nome: [{ k: 'b', t: f.nome }].concat(f.ult ? [{ k: 'br' }, { k: 'mut', t: 'última: ' + f.ult.item + ' · ' + prBr(f.ult.d) }] : []), n: [{ k: 'txt', t: String(f.n) }], rel: [{ k: 'txt', t: intPct(f.rel) }],
      prazo: [{ k: 'txt', t: f.prazo === null ? '—' : String(f.prazo).replace('.', ',') + ' dias' }],
      pont: f.pont === null ? [{ k: 'mut', t: 'sem entrega' }] : [{ k: prCmp(f.pont, '0.8') < 0 ? 'cn' : 'txt', c: 'red', t: pc(f.pont) }, { k: 'br' }, { k: 'mut', t: f.atr + ' de ' + f.nEnt + ' com atraso' }] } }; }
function icHRow(g, area) { return { id: 'h:' + g.grupo, ro: true, v: { grupo: g.grupo, total: Number(g.total), rsha: icN(g.rsha) }, s: { grupo: g.grupo, total: icRS(g.total, 0), rsha: icRS(g.rsha) },
    p: { grupo: [{ k: 'b', t: g.grupo }], total: [{ k: 'txt', t: icRS(g.total, 0) }], rsha: [{ k: 'b', t: icRS(g.rsha) + '/ha' }] } }; }
function PREVALS(self, v) { cenOuvir(self); prTopo(self, v); const I = intCompras(INTC, prHoje()); self._ic = I;
  self.g2pick = (gid, rid) => self.setState({ pr_sel: { g: gid, id: rid }, pr_pan: { g: gid, id: rid } });
  GR('g_ici').rows = I.itens.slice().sort((a, b) => (b.acima - a.acima) || prCmp(icN(b.vRef), icN(a.vRef))).map(icIRow);
  GR('g_icf').rows = I.forn.slice().sort((a, b) => prCmp(icN(a.rel), icN(b.rel))).map(icFRow); GR('g_ich').rows = I.porHa.map(g => icHRow(g, I.area));
  v.k_ac = String(I.acima); v.k_acn = I.acima ? I.itens.filter(i => i.acima).map(i => i.nome).join(' · ') : 'nenhuma cotação 5% acima da referência';
  v.k_ec = icRS(I.economia, 0); v.k_ecn = 'comprando pela melhor cotação, contra a referência da safra';
  v.k_ha = icRS(I.rshaTot) + '/ha'; v.k_han = 'insumos orçados ÷ ' + prFmt(I.area, 0) + ' ha da safra ' + INTC.safra; }
function icPan(self, pan) { const I = self._ic;
  if (pan.g === 'g_ici') { const i = I.itens.find(x => 'i:' + x.nome === pan.id); if (!i) return null; const P = y => icRS(y) + '/' + i.un;
    const cs = i.cot.map(x => ({ c: [[x.nome, 'b'], P(x.preco), intPct(intRel(x.preco, i.ref)), x.prazo + ' d · ' + x.frete + ' · ' + x.pag, x.venc ? ['vencida em ' + x.validade, 'red'] : 'válida até ' + x.validade] }));
    const hs = i.hs.map(h => ({ c: [[prBr(h.d), 'b'], h.nome, P(h.preco), h.orig + (h.entregue ? (h.atraso > 0 ? ' · ' + h.atraso + ' d de atraso' : ' · no prazo') : ' · a entregar')] }));
    return { title: i.nome, chip: [icSit(i), IC_SITC[icSit(i)]], sub: i.grupo + ' · ' + prFmt(i.qtd, 0) + ' ' + i.un + ' na safra ' + INTC.safra,
      next: i.melhor ? 'Melhor cotação ' + P(i.melhor.preco) + ' (' + i.melhor.nome + '): ' + intPct(i.vRef) + ' contra a referência ' + P(i.ref) + (i.ult ? ' e ' + intPct(i.vUlt) + ' contra o último pago ' + P(i.ult.preco) : '') + '.' + (i.acima ? ' Acima de +5%: renegocie ou cote outro fornecedor (Compra de insumos).' : '') : (i.nVenc ? 'As ' + i.nVenc + ' cotação(ões) de ' + i.nome + ' venceram: o preço não vale para decidir. Peça nova cotação em Compra de insumos.' : 'Sem cotação para ' + i.nome + ': solicite em Compra de insumos.'),
      kv: [{ l: 'Referência da safra', v: P(i.ref) }, { l: 'Último pago', v: i.ult ? P(i.ult.preco) + ' · ' + prBr(i.ult.d) : '—' }, { l: 'Melhor cotação', v: i.melhor ? P(i.melhor.preco) + ' · ' + i.melhor.nome : '—' }, { l: 'Diferença à referência', v: intPct(i.vRef) }],
      secs: [{ t: 'Cotações', rows: cs, vazio: 'Sem cotação.' }, { t: 'Compras anteriores', rows: hs, vazio: 'Sem compra registrada.' }], prim: { t: 'Abrir Compra de insumos', h: 'CMP.dc.html' } }; }
  if (pan.g === 'g_icf') { const f = I.forn.find(x => 'f:' + x.id === pan.id); if (!f) return null;
    const hs = (INTC.hist || []).filter(h => h.f === f.id).map(h => ({ c: [[prBr(h.d), 'b'], h.item, h.orig, h.entregue ? (h.atraso > 0 ? [h.atraso + ' d de atraso', 'red'] : 'no prazo') : 'a entregar'] }));
    return { title: f.nome, chip: [f.pont === null ? 'Sem entrega' : prFmt(prMul(f.pont, 100), 0) + '% no prazo', f.pont !== null && prCmp(f.pont, '0.8') < 0 ? 'red' : 'green'], sub: 'Preço relativo = média de (cotação − referência) ÷ referência; pontualidade = entregas no prazo ÷ entregas',
      next: 'Preço ' + intPct(f.rel) + ' contra a referência em ' + f.n + ' cotação(ões); prazo médio ' + (f.prazo === null ? '—' : String(f.prazo).replace('.', ',') + ' dias') + '.', kv: [{ l: 'Cotações', v: String(f.n) }, { l: 'Preço vs referência', v: intPct(f.rel) }, { l: 'Pontualidade', v: f.pont === null ? 'sem entrega' : prFmt(prMul(f.pont, 100), 0) + '%' }],
      secs: [{ t: 'Compras', rows: hs, vazio: 'Sem compra registrada.' }] }; }
  if (pan.g === 'g_ich') { const g = I.porHa.find(x => 'h:' + x.grupo === pan.id); if (!g) return null; const its = I.itens.filter(i => i.grupo === g.grupo);
    return { title: g.grupo, chip: [icRS(g.rsha) + '/ha', 'green'], sub: 'Σ (quantidade da safra × referência) ÷ área', next: 'Total ' + icRS(g.total, 0) + ' ÷ ' + prFmt(I.area, 0) + ' ha = ' + icRS(g.rsha) + '/ha.',
      kv: [{ l: 'Total orçado', v: icRS(g.total, 0) }, { l: 'Área da safra', v: prFmt(I.area, 0) + ' ha' }],
      secs: [{ t: 'Insumos do grupo', rows: its.map(i => ({ c: [[i.nome, 'b'], prFmt(i.qtd, 0) + ' ' + i.un, icRS(i.ref) + '/' + i.un, icRS(prMul(i.qtd, i.ref), 0)] })) }] }; }
  return null; }
function EXTRAVALS(self, v) { prRst(self, v); const I = self._ic || intCompras(INTC, prHoje()); const st = self.state;
  v.cards_ici = prCards(self, v, 'g_ici', id => { const i = I.itens.find(x => 'i:' + x.nome === id); return i ? prCard({ t1: i.nome, num: i.melhor ? icRS(i.melhor.preco) + '/' + i.un : (i.nVenc ? 'cotação vencida' : 'sem cotação'), t2: 'Referência ' + icRS(i.ref) + ' · ' + intPct(i.vRef), chip: [icSit(i), IC_SITC[icSit(i)]] }) : null; });
  v.cards_icf = prCards(self, v, 'g_icf', id => { const f = I.forn.find(x => 'f:' + x.id === id); return f ? prCard({ t1: f.nome, num: intPct(f.rel), t2: 'pontualidade ' + (f.pont === null ? '—' : prFmt(prMul(f.pont, 100), 0) + '%') }) : null; });
  v.cards_ich = prCards(self, v, 'g_ich', id => { const g = I.porHa.find(x => 'h:' + x.grupo === id); return g ? prCard({ t1: g.grupo, num: icRS(g.rsha) + '/ha', t2: icRS(g.total, 0) }) : null; });
  prStatus(v, [I.acima ? I.acima + ' insumo(s) com cotação acima da referência' : 'cotações dentro da referência'].concat(I.vencidas ? [I.vencidas + ' insumo(s) só com cotação vencida'] : []).concat(['insumos ' + icRS(I.rshaTot) + '/ha']));
  const pan = st.pr_pan; const PP = pan ? icPan(self, pan) : null; comPrimPainel(v, PP && PP.prim ? PP.prim : null, PP); prPainel(self, v, PP); }
"""


def ic():
    fname = 'IC.dc.html'; V.E._reset_screen(fname)
    g_ici = grid([dict(k='nome', l='Insumo', w=190), dict(k='grupo', l='Grupo', w=120), dict(k='ult', l='Último pago', t='num', a='r', w=170), dict(k='ref', l='Referência', t='num', a='r', w=120),
                  dict(k='mel', l='Melhor cotação', t='num', a='r', w=190), dict(k='vref', l='vs referência', t='num', a='r', w=120), dict(k='vult', l='vs último', t='num', a='r', w=110),
                  dict(k='sit', l='Sinal', w=200)],
                 [], edit=dict(m='pick'), gid='g_ici', total=False, qf=dict(k='sit', l='Sinal', todas='Todos'))
    g_icf = grid([dict(k='nome', l='Fornecedor', w=220), dict(k='n', l='Cotações', t='num', a='r', w=100), dict(k='rel', l='Preço vs referência', t='num', a='r', w=160),
                  dict(k='prazo', l='Prazo de entrega', t='num', a='r', w=150), dict(k='pont', l='Pontualidade', t='num', a='r', w=170)],
                 [], edit=dict(m='pick'), gid='g_icf', total=False)
    g_ich = grid([dict(k='grupo', l='Grupo', w=200), dict(k='total', l='Total orçado', t='num', a='r', w=160), dict(k='rsha', l='R$/ha', t='num', a='r', w=140)],
                 [], edit=dict(m='pick'), gid='g_ich', total=False)
    V.EXTRAJS[0] = V._js(DI.js() + _ijs() + IC_JS)
    corpo = (_ind(('Cotações acima da referência', 'k_ac', 'k_acn'), ('Economia pela melhor cotação', 'k_ec', 'k_ecn'), ('Insumos por hectare', 'k_ha', 'k_han'))
             + AP.bloco('Preço por insumo', 'Último preço pago × referência da safra × melhor cotação atual. Cotação 5% acima da referência vira alerta. O histórico de preço é sintético e vem marcado.', g_ici + AP.cartoes('cards_ici'))
             + AP.bloco('Fornecedores', 'Preço relativo (média das cotações contra a referência), prazo de entrega cotado e pontualidade (entregas no prazo ÷ entregas).', g_icf + AP.cartoes('cards_icf'))
             + AP.bloco('Custo de insumos por hectare', 'Σ (quantidade da safra × referência) ÷ área da safra, por grupo. Use para comparar com o orçamento.', g_ich + AP.cartoes('cards_ich')))
    V._shell('IC', 'Inteligência de compras', 'Se o preço cotado está bom contra o mercado e o histórico, que fornecedor entrega melhor e quanto os insumos pesam por hectare.', corpo, fname, 1300,
             'Referência e quantidades da safra (Planejar safra), cotações dos fornecedores homologados e pedidos. Nada é gravado aqui; a decisão de comprar é de Suprimentos.')


def build():
    iv()
    ic()
