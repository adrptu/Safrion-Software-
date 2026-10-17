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
const PR_GRIDS = { g_ivm: 1, g_ivp: 1, g_ivs: 1, g_ivc: 1 };
/* INTEL-02 · leitura comum: preço com unidade, variação, tendência, sazonalidade em barras e últimos 12 meses */
function ipRS(x, un) { return x === null || x === undefined ? '—' : 'R$ ' + prFmt(x, 2) + (un ? '/' + un : ''); }
function ipPct(x) { return x === null || x === undefined ? '—' : intPct(x); }
const IP_TEND = { 'Alta': 'red', 'Queda': 'green', 'Estável': 'gray', 'Sem série': 'gray' };   /* cor do lado de quem compra; a venda inverte */
function ipTendChip(L, venda) { const c = L.tend === 'Alta' ? (venda ? 'green' : 'red') : L.tend === 'Queda' ? (venda ? 'red' : 'green') : 'gray';
  return [{ k: 'chip', t: L.tend, c }, { k: 'br' }, { k: 'mut', t: 'sem a época: ' + ipPct(L.tv) }]; }
function ipSaz(L, un, alvo) { const z = L.z; let mn = z.idx[0], mx = z.idx[0]; z.idx.forEach(x => { if (prCmp(x, mn) < 0) mn = x; if (prCmp(x, mx) > 0) mx = x; });
  const med = intMedia(L.s.slice(-12).map(x => x.p)); const amp = prSub(mx, mn);
  return z.idx.map((x, k) => { const n = prCmp(amp, 0) > 0 ? Math.round(Number(prDiv(prSub(x, mn), amp)) * 14) + 1 : 8; const tags = [];
    if (k === L.mesAtual) tags.push('agora'); if (k === L.melhor) tags.push(alvo);
    return { c: [[INT_MESES[k], k === L.melhor ? 'b' : undefined], ipRS(prMul(med, x), un), intPct(prSub(x, 1)), '▮'.repeat(n)].concat(tags.length ? [[tags.join(' · '), k === L.melhor ? 'green' : 'gray']] : []) }; }); }
function ipUlt(L, un) { return L.s.slice(-12).reverse().map(x => ({ c: [[INT_MESES[intMes(x.m)] + '/' + x.m.slice(2, 4), 'b'], ipRS(x.p, un)] })); }
const IP_NOTA = 'Série mensal sintética de 60 meses (demonstração): no software real, CEPEA/Esalq, CONAB, CEAGESP e as compras da fazenda. Histórico não é previsão.';

const IV_REC = { 'Vender agora': 'green', 'Esperar': 'yellow', 'Sem ganho em esperar': 'gray', 'Vender na colheita': 'gray', 'Sem série de preço': 'gray' };
function ivmRec(x) { if (x.semSerie) return 'Sem série de preço'; return x.rec; }
function ivmRecPart(x) { const r = ivmRec(x); const nota = x.semSerie ? 'sem fonte de preço: ausente ≠ zero'
    : r === 'Esperar' ? 'até ' + INT_MESES[x.mesAlvo] + ': +' + prFmt(prMul(x.ganho, 100), 1) + '% na época, ' + prFmt(prMul(x.liq, 100), 1) + '% depois do custo do dinheiro'
    : r === 'Vender agora' ? (x.bd === 0 ? 'este é o melhor mês dos próximos 12' : 'preço ' + ipPct(x.norma.vs) + ' acima do normal de ' + INT_MESES[x.mesAtual])
    : r === 'Vender na colheita' ? 'perecível: planeje a colheita para ' + INT_MESES[x.melhor]
    : 'melhor mês ' + INT_MESES[x.mesAlvo] + ' paga ' + ipPct(x.ganho) + ', menos ' + prFmt(prMul(INT_TAXA_MES, 100 * x.bd), 1) + '% de custo do dinheiro';
  return [{ k: 'chip', t: r, c: IV_REC[r] }, { k: 'br' }, { k: 'mut', t: nota }]; }
function ivmRow(x) { const un = x.un; const r = ivmRec(x);
  if (x.semSerie) return { id: 'm:' + x.prod, ro: true, v: { prod: x.prod, atual: -1e12, v1: -1e12, v12: -1e12, tend: 'Sem série', melhor: '', norma: -1e12, rec: r }, s: { prod: x.prod, atual: '—', v1: '—', v12: '—', tend: 'Sem série', melhor: '—', norma: '—', rec: r },
    p: { prod: [{ k: 'b', t: x.prod }], atual: [{ k: 'mut', t: 'sem cotação' }], v1: [{ k: 'mut', t: '—' }], v12: [{ k: 'mut', t: '—' }], tend: [{ k: 'chip', t: 'Sem série', c: 'gray' }], melhor: [{ k: 'mut', t: '—' }], norma: [{ k: 'mut', t: '—' }], rec: ivmRecPart(x) } };
  return { id: 'm:' + x.prod, ro: true, v: { prod: x.prod, atual: Number(x.atual), v1: Number(x.v1), v12: Number(x.v12), tend: x.tend, melhor: x.melhor + 1, norma: Number(x.norma.vs), rec: r },
    s: { prod: x.prod, atual: ipRS(x.atual, un), v1: ipPct(x.v1), v12: ipPct(x.v12), tend: x.tend, melhor: INT_MESES[x.melhor], norma: ipPct(x.norma.vs), rec: r },
    p: { prod: [{ k: 'b', t: x.prod }], atual: [{ k: 'b', t: ipRS(x.atual, un) }], v1: [{ k: 'txt', t: ipPct(x.v1) }], v12: [{ k: 'txt', t: ipPct(x.v12) }], tend: ipTendChip(x, true),
      melhor: [{ k: 'b', t: INT_MESES[x.melhor] }, { k: 'br' }, { k: 'mut', t: 'pior: ' + INT_MESES[intExtremo(x.z, false)] }], norma: [{ k: 'txt', t: ipPct(x.norma.vs) }, { k: 'br' }, { k: 'mut', t: 'normal ' + ipRS(x.norma.esp, un) }], rec: ivmRecPart(x) } }; }

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
function PREVALS(self, v) { cenOuvir(self); prTopo(self, v); const c = cenGet(); self._c = c; const I = intVendas(c); self._iv = I; const M = intPrecos(INTP); self._ivm = M;
  GR('g_ivm').rows = M.vendas.map(ivmRow);
  const al = M.vendas.filter(x => x.tend === 'Alta'), ag = M.vendas.filter(x => x.rec === 'Vender agora');
  v.k_al = String(al.length); v.k_aln = al.length ? al.map(x => x.prod.split(' ')[0] + ' ' + ipPct(x.tv)).join(' · ') : 'nenhum produto em alta (sem a época)';
  v.k_ag = String(ag.length); v.k_agn = ag.length ? ag.map(x => x.prod.split(' ')[0]).join(' · ') : 'nenhum no melhor momento agora';
  const ms = M.vendas.filter(x => !x.semSerie); v.k_mm = ms.map(x => x.prod.split(' ')[0] + ' ' + INT_MESES[x.melhor]).join(' · '); v.k_mmn = 'mês de melhor preço no histórico de 5 anos';
  self.g2pick = (gid, rid) => self.setState({ pr_sel: { g: gid, id: rid }, pr_pan: { g: gid, id: rid } });
  GR('g_ivp').rows = I.prods.map(ivPRow); GR('g_ivs').rows = I.posicao.map(ivSRow);
  GR('g_ivc').rows = I.cli.slice().sort((a, b) => prCmp(b.liq, a.liq)).map(ivCRow);
  const ab = I.prods.filter(p => p.abaixo); v.k_ab = String(ab.length); v.k_abn = ab.length ? ab.map(p => p.prod.split(' ')[0] + ' ' + intPct(p.spread)).join(' · ') : 'nenhuma venda 5% abaixo da referência';
  const rk = I.posicao.filter(intRiscoOferta);
  v.k_rk = String(rk.length); v.k_rkn = rk.length ? rk.map(p => p.prod.split(' ')[0] + ': ' + (p.est === 'Sem previsão' ? 'vendido sem previsão' : 'acima da oferta')).join(' · ') : 'vendas cobertas pela oferta';
  const best = I.cli.slice().sort((a, b) => prCmp(b.liq, a.liq))[0]; v.k_liq = best ? comPrecoTxt(best.cu, best.liq) : '—'; v.k_liqn = best ? 'melhor líquido: ' + best.id + ' · ' + best.cliente : 'sem venda com preço'; }
function ivPan(self, c, pan) { const I = self._iv; const P = prP(c);
  if (pan.g === 'g_ivm') { const x = (self._ivm || intPrecos(INTP)).vendas.find(y => 'm:' + y.prod === pan.id); if (!x) return null;
    if (x.semSerie) return { title: x.prod, chip: ['Sem série de preço', 'gray'], sub: 'Sem fonte de preço de mercado para este produto', next: 'Sem cotação de referência: a tela não inventa preço nem melhor mês (ausente ≠ zero). Cadastre a fonte de preço para ' + x.prod + '.', secs: [] };
    const r = ivmRec(x); const un = x.un;
    const next = r === 'Vender agora' ? (x.bd === 0 ? INT_MESES[x.mesAtual] + ' é o mês de melhor preço dos próximos 12 no histórico: vender agora aproveita a época.' : 'O preço está ' + ipPct(x.norma.vs) + ' acima do normal de ' + INT_MESES[x.mesAtual] + ' (' + ipRS(x.norma.esp, un) + '): bom momento para vender.')
      : r === 'Esperar' ? 'Historicamente ' + INT_MESES[x.mesAlvo] + ' paga ' + ipPct(x.ganho) + ' a mais que ' + INT_MESES[x.mesAtual] + '; descontado o custo do dinheiro (' + prFmt(prMul(INT_TAXA_MES, 100), 1) + '% a.m. × ' + x.bd + ' meses), sobram ' + ipPct(x.liq) + '. Some a armazenagem antes de decidir.'
      : r === 'Vender na colheita' ? 'Perecível: não dá para guardar e esperar. O melhor preço sai em ' + INT_MESES[x.melhor] + ' e o pior em ' + INT_MESES[intExtremo(x.z, false)] + ': use isso para planejar o plantio e a colheita.'
      : 'O mês melhor (' + INT_MESES[x.mesAlvo] + ') paga ' + ipPct(x.ganho) + ', mas o custo do dinheiro em ' + x.bd + ' meses come quase tudo (' + ipPct(x.liq) + '): venda conforme a necessidade de caixa.';
    return { title: x.prod, chip: [r, IV_REC[r]], sub: IP_NOTA + ' Referência atual: ' + x.fonte + '.', next,
      kv: [{ l: 'Preço agora', v: ipRS(x.atual, un) }, { l: 'Normal de ' + INT_MESES[x.mesAtual], v: ipRS(x.norma.esp, un) + ' (' + ipPct(x.norma.vs) + ')' }, { l: '1 mês · 12 meses', v: ipPct(x.v1) + ' · ' + ipPct(x.v12) },
        { l: 'Tendência sem a época', v: x.tend + ' (' + ipPct(x.tv) + ', 3 meses contra os 3 anteriores)' }, { l: 'Melhor e pior mês', v: INT_MESES[x.melhor] + ' · ' + INT_MESES[intExtremo(x.z, false)] }],
      secs: [{ t: 'Preço por mês no histórico (normal de cada mês sobre a média de 12 meses)', rows: ipSaz(x, un, 'melhor para vender') }, { t: 'Últimos 12 meses', rows: ipUlt(x, un) }] }; }
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
function EXTRAVALS(self, v) { prRst(self, v); const c = self._c || cenGet(); const I = self._iv || intVendas(c); const st = self.state; const M = self._ivm || intPrecos(INTP);
  v.cards_ivm = prCards(self, v, 'g_ivm', id => { const x = M.vendas.find(y => 'm:' + y.prod === id); return x ? prCard({ t1: x.prod, num: x.semSerie ? 'sem série' : ipRS(x.atual, x.un), t2: x.semSerie ? 'sem fonte de preço' : x.tend + ' · melhor mês ' + INT_MESES[x.melhor], chip: [ivmRec(x), IV_REC[ivmRec(x)]] }) : null; });
  v.cards_ivp = prCards(self, v, 'g_ivp', id => { const p = I.prods.find(x => 'p:' + x.prod === id); return p ? prCard({ t1: p.prod, num: intPct(p.spread), t2: 'Contratado ' + (p.medC === null ? '—' : comPrecoTxt(p.cu, p.medC)) + ' · referência ' + (p.ref ? comPrecoTxt(p.cu, p.ref) : 'sem cotação'), chip: [ivSit(p), IV_SIT[ivSit(p)]] }) : null; });
  v.cards_ivs = prCards(self, v, 'g_ivs', id => { const p = I.posicao.find(x => 's:' + x.prod === id); return p ? prCard({ t1: p.prod, num: p.pos === null ? '—' : prFmt(prMul(p.pos, 100), 0) + '% vendido', t2: p.livre === null ? p.est : 'Livre ' + comTxt(p.cu, p.livre, 0), chip: [p.est, intRiscoOferta(p) ? 'red' : IV_EST[p.est]] }) : null; });
  v.cards_ivc = prCards(self, v, 'g_ivc', id => { const x = I.cli.find(y => 'c:' + y.id === id); return x ? prCard({ t1: x.id + ' · ' + x.cliente, num: comPrecoTxt(x.cu, x.liq) + ' líquido', t2: x.prod + ' · preço ' + comPrecoTxt(x.cu, x.preco) }) : null; });
  /* selo do cabeçalho: texto único (prStatus recebe texto e cor; a lista colava as frases sem separador, defeito S4 da v58) */
  const ag = M.vendas.filter(x => x.rec === 'Vender agora'), ab = I.prods.filter(p => p.abaixo).length, rk = I.posicao.filter(intRiscoOferta).length;
  prStatus(v, [ag.length ? 'vender agora: ' + ag.map(x => x.prod.split(' ')[0]).join(', ') : 'nenhum produto no melhor momento de venda',
    ab ? ab + ' produto(s) vendido(s) abaixo da referência' : 'nenhuma venda abaixo da referência', rk ? rk + ' produto(s) com venda sem oferta que cubra' : 'vendas cobertas pela oferta'].join(' · '), (ab || rk) ? 'yellow' : 'green');
  const pan = st.pr_pan; const PP = pan ? ivPan(self, c, pan) : null; comPrimPainel(v, PP && PP.prim ? PP.prim : null, PP); prPainel(self, v, PP); }
"""


def iv():
    fname = 'IV.dc.html'; V.E._reset_screen(fname)
    g_ivm = grid([dict(k='prod', l='Produto', w=200), dict(k='atual', l='Preço agora', t='num', a='r', w=140), dict(k='v1', l='1 mês', t='num', a='r', w=90),
                  dict(k='v12', l='12 meses', t='num', a='r', w=100), dict(k='tend', l='Tendência', w=140), dict(k='melhor', l='Melhor mês para vender', t='num', w=150),
                  dict(k='norma', l='Agora vs normal do mês', t='num', a='r', w=150), dict(k='rec', l='O que fazer', w=280)],
                 [], edit=dict(m='pick'), gid='g_ivm', total=False, qf=dict(k='rec', l='O que fazer', todas='Todos'))
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
    V.EXTRAJS[0] = V._js(DI.js_precos() + _ijs() + IV_JS)
    # TAB-07 (DS-MODULOS-2, 17/10/2026): sem cartões de resumo sobre a 1ª lista; "em alta" e o melhor mês estão nas colunas Tendência e
    # Melhor mês, "Vender agora N" no filtro rápido de "O que fazer" e o resumo no selo do cabeçalho. Os indicadores dos blocos seguintes ficam
    # entre os blocos: são o painel do assunto desta tela de análise
    corpo = (AP.bloco('Preço e melhor mês para vender', 'Preço de agora, variação, tendência sem o efeito da época e o mês que historicamente paga mais. Esperar só aparece quando o ganho da época passa de 3% depois do custo do dinheiro (1,2% a.m.). Série sintética de 60 meses: histórico não é previsão.', g_ivm + AP.cartoes('cards_ivm'))
             + _ind(('Vendas abaixo da referência', 'k_ab', 'k_abn'), ('Venda sem oferta que cubra', 'k_rk', 'k_rkn'), ('Melhor recebimento líquido', 'k_liq', 'k_liqn'))
             + AP.bloco('Preço × mercado', 'Preço médio contratado (Σ valor ÷ Σ quantidade, só venda) × referência de mercado com fonte. Abaixo de −5% vira alerta; sem cotação, fica em branco.', g_ivp + AP.cartoes('cards_ivp'))
             + AP.bloco('Safra comercializada', 'Vendido ÷ oferta da safra (previsão publicada ou estoque apto, todas as fazendas). Acima de 100% é venda maior que a oferta.', g_ivs + AP.cartoes('cards_ivs'))
             + AP.bloco('Recebimento líquido por venda', 'Preço − frete (R$ 190/t; cliente que retira não paga) − custo de esperar o pagamento (1,2% a.m.). Compare clientes pelo que fica na fazenda.', g_ivc + AP.cartoes('cards_ivc')))
    V._shell('IV', 'Inteligência de vendas', 'Preço, tendência e o melhor mês para vender cada produto; abaixo, como estão as suas vendas contra o mercado.', corpo, fname, 1300,
             'Números lidos do estado (vendas, previsão publicada, estoque) e da referência de mercado sintética com fonte. Nada é gravado aqui; a decisão de vender é do Comercial.')


# =====================================================================================================================
# IC · Inteligência de compras
# =====================================================================================================================
IC_JS = r"""
const PR_GRIDS = { g_icm: 1, g_ici: 1, g_icf: 1, g_ich: 1 };
/* INTEL-02 · leitura comum: preço com unidade, variação, tendência, sazonalidade em barras e últimos 12 meses */
function ipRS(x, un) { return x === null || x === undefined ? '—' : 'R$ ' + prFmt(x, 2) + (un ? '/' + un : ''); }
function ipPct(x) { return x === null || x === undefined ? '—' : intPct(x); }
const IP_TEND = { 'Alta': 'red', 'Queda': 'green', 'Estável': 'gray', 'Sem série': 'gray' };   /* cor do lado de quem compra; a venda inverte */
function ipTendChip(L, venda) { const c = L.tend === 'Alta' ? (venda ? 'green' : 'red') : L.tend === 'Queda' ? (venda ? 'red' : 'green') : 'gray';
  return [{ k: 'chip', t: L.tend, c }, { k: 'br' }, { k: 'mut', t: 'sem a época: ' + ipPct(L.tv) }]; }
function ipSaz(L, un, alvo) { const z = L.z; let mn = z.idx[0], mx = z.idx[0]; z.idx.forEach(x => { if (prCmp(x, mn) < 0) mn = x; if (prCmp(x, mx) > 0) mx = x; });
  const med = intMedia(L.s.slice(-12).map(x => x.p)); const amp = prSub(mx, mn);
  return z.idx.map((x, k) => { const n = prCmp(amp, 0) > 0 ? Math.round(Number(prDiv(prSub(x, mn), amp)) * 14) + 1 : 8; const tags = [];
    if (k === L.mesAtual) tags.push('agora'); if (k === L.melhor) tags.push(alvo);
    return { c: [[INT_MESES[k], k === L.melhor ? 'b' : undefined], ipRS(prMul(med, x), un), intPct(prSub(x, 1)), '▮'.repeat(n)].concat(tags.length ? [[tags.join(' · '), k === L.melhor ? 'green' : 'gray']] : []) }; }); }
function ipUlt(L, un) { return L.s.slice(-12).reverse().map(x => ({ c: [[INT_MESES[intMes(x.m)] + '/' + x.m.slice(2, 4), 'b'], ipRS(x.p, un)] })); }
const IP_NOTA = 'Série mensal sintética de 60 meses (demonstração): no software real, CEPEA/Esalq, CONAB, CEAGESP e as compras da fazenda. Histórico não é previsão.';

const IC_REC = { 'Comprar agora': 'green', 'Esperar': 'yellow', 'Comprar até a necessidade': 'gray' };
function icmNota(x) { return x.rec === 'Esperar' ? 'até ' + INT_MESES[x.mesAlvo] + ' (pedir até ' + prBr(x.lim) + '): ' + prFmt(prMul(x.econ, 100), 1) + '% mais barato na época'
  : x.rec === 'Comprar agora' ? (x.D === 0 ? (x.lim ? 'para receber até ' + prBr(x.nec) + ' (entrega em ' + x.prazo + ' dias), peça agora' : 'peça agora') : x.bd === 0 ? 'este é o mês mais barato até a necessidade' : 'preço ' + ipPct(x.norma.vs) + ' abaixo do normal do mês')
  : 'até ' + prBr(x.lim) + ' a época barateia só ' + prFmt(prMul(x.econ, 100), 1) + '%'; }
function icmRow(x) { const un = x.un;
  return { id: 'm:' + x.nome, ro: true, v: { nome: x.nome, atual: Number(x.atual), v12: Number(x.v12), tend: x.tend, melhor: x.melhor + 1, nec: x.nec || '', rec: x.rec, eco: x.eco === null ? -1e12 : Number(x.eco) },
    s: { nome: x.nome, atual: ipRS(x.atual, un), v12: ipPct(x.v12), tend: x.tend, melhor: INT_MESES[x.melhor], nec: x.nec ? prBr(x.nec) : '—', rec: x.rec, eco: x.eco === null ? '—' : ipRS(x.eco) },
    p: { nome: [{ k: 'b', t: x.nome }, { k: 'br' }, { k: 'mut', t: x.grupo }], atual: [{ k: 'b', t: ipRS(x.atual, un) }], v12: [{ k: 'txt', t: ipPct(x.v12) }], tend: ipTendChip(x, false),
      melhor: [{ k: 'b', t: INT_MESES[x.melhor] }, { k: 'br' }, { k: 'mut', t: 'mais caro: ' + INT_MESES[intExtremo(x.z, true)] }],
      nec: x.nec ? [{ k: 'txt', t: prBr(x.nec) }, { k: 'br' }, { k: 'mut', t: 'pedir até ' + prBr(x.lim) }] : [{ k: 'mut', t: 'sem uso planejado' }],
      rec: [{ k: 'chip', t: x.rec, c: IC_REC[x.rec] }, { k: 'br' }, { k: 'mut', t: icmNota(x) }], eco: x.eco === null ? [{ k: 'mut', t: '—' }] : [{ k: 'b', t: ipRS(x.eco) }] } }; }

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
function PREVALS(self, v) { cenOuvir(self); prTopo(self, v); const I = intCompras(INTC, prHoje()); self._ic = I; const M = intPrecos(INTP); self._icm = M;
  GR('g_icm').rows = M.compras.slice().sort((a, b) => (({ 'Comprar agora': 0, 'Esperar': 1 })[a.rec] ?? 2) - (({ 'Comprar agora': 0, 'Esperar': 1 })[b.rec] ?? 2) || String(a.nec || '9').localeCompare(String(b.nec || '9'))).map(icmRow);
  const al = M.compras.filter(x => x.tend === 'Alta'), ag = M.compras.filter(x => x.rec === 'Comprar agora'), es = M.compras.filter(x => x.rec === 'Esperar');
  v.k_al = String(al.length); v.k_aln = al.length ? al.map(x => x.nome).join(' · ') : 'nenhum insumo em alta (sem a época)';
  v.k_ag = String(ag.length); v.k_agn = ag.length ? 'necessidade próxima: ' + ag.map(x => x.nome).join(' · ') : 'nada urgente';
  v.k_es = ipRS(M.economia); v.k_esn = es.length + ' insumo(s) mais baratos';   /* 14/10/2026: "esperando o mês certo, antes da necessidade" repetia o título do indicador */
  self.g2pick = (gid, rid) => self.setState({ pr_sel: { g: gid, id: rid }, pr_pan: { g: gid, id: rid } });
  GR('g_ici').rows = I.itens.slice().sort((a, b) => (b.acima - a.acima) || prCmp(icN(b.vRef), icN(a.vRef))).map(icIRow);
  GR('g_icf').rows = I.forn.slice().sort((a, b) => prCmp(icN(a.rel), icN(b.rel))).map(icFRow); GR('g_ich').rows = I.porHa.map(g => icHRow(g, I.area));
  v.k_ac = String(I.acima); v.k_acn = I.acima ? I.itens.filter(i => i.acima).map(i => i.nome).join(' · ') : 'nenhuma cotação 5% acima da referência';
  v.k_ec = icRS(I.economia, 0); v.k_ecn = 'contra a referência da safra';   /* 14/10/2026: "comprando pela melhor cotação" repetia o título do indicador */
  v.k_ha = icRS(I.rshaTot) + '/ha'; v.k_han = 'insumos orçados ÷ ' + prFmt(I.area, 0) + ' ha da safra ' + INTC.safra; }
function icPan(self, pan) { const I = self._ic;
  if (pan.g === 'g_icm') { const x = (self._icm || intPrecos(INTP)).compras.find(y => 'm:' + y.nome === pan.id); if (!x) return null; const un = x.un;
    const next = x.rec === 'Esperar' ? 'Historicamente ' + INT_MESES[x.mesAlvo] + ' sai ' + prFmt(prMul(x.econ, 100), 1) + '% mais barato que ' + INT_MESES[x.mesAtual] + ' e ainda chega antes da necessidade (' + prBr(x.nec) + '): peça até ' + prBr(x.lim) + ' (entrega em ' + x.prazo + ' dias). Economia estimada ' + ipRS(x.eco) + ' em ' + prFmt(x.qtd, 0) + ' ' + un + '.'
      : x.rec === 'Comprar agora' ? (x.D === 0 && x.lim ? 'A necessidade é em ' + prBr(x.nec) + ' e a entrega leva ' + x.prazo + ' dias: peça agora.' : x.bd === 0 ? INT_MESES[x.mesAtual] + ' é o mês mais barato até a necessidade.' : 'O preço está ' + ipPct(x.norma.vs) + ' abaixo do normal do mês: aproveite.')
      : 'Até ' + prBr(x.lim) + ' a época barateia só ' + prFmt(prMul(x.econ, 100), 1) + '% (menos de 3%): compre quando for melhor para o caixa, antes da necessidade.';
    return { title: x.nome, chip: [x.rec, IC_REC[x.rec]], sub: x.grupo + ' · ' + prFmt(x.qtd, 0) + ' ' + un + ' na safra ' + INTC.safra + '. ' + IP_NOTA, next,
      kv: [{ l: 'Preço agora', v: ipRS(x.atual, un) }, { l: 'Normal de ' + INT_MESES[x.mesAtual], v: ipRS(x.norma.esp, un) + ' (' + ipPct(x.norma.vs) + ')' }, { l: '1 mês · 12 meses', v: ipPct(x.v1) + ' · ' + ipPct(x.v12) },
        { l: 'Tendência sem a época', v: x.tend + ' (' + ipPct(x.tv) + ')' }, { l: 'Mês mais barato e mais caro', v: INT_MESES[x.melhor] + ' · ' + INT_MESES[intExtremo(x.z, true)] },
        { l: 'Próxima necessidade', v: x.nec ? prBr(x.nec) + ' (Planejar safra) · pedir até ' + prBr(x.lim) : 'sem uso planejado' }],
      secs: [{ t: 'Preço por mês no histórico (normal de cada mês sobre a média de 12 meses)', rows: ipSaz(x, un, 'mais barato') }, { t: 'Últimos 12 meses', rows: ipUlt(x, un) }], prim: { t: 'Abrir Compra de insumos', h: 'CMP.dc.html' } }; }
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
function EXTRAVALS(self, v) { prRst(self, v); const I = self._ic || intCompras(INTC, prHoje()); const st = self.state; const M = self._icm || intPrecos(INTP);
  v.cards_icm = prCards(self, v, 'g_icm', id => { const x = M.compras.find(y => 'm:' + y.nome === id); return x ? prCard({ t1: x.nome, num: ipRS(x.atual, x.un), t2: x.tend + ' · mais barato em ' + INT_MESES[x.melhor] + (x.nec ? ' · uso ' + prBr(x.nec) : ''), chip: [x.rec, IC_REC[x.rec]] }) : null; });
  v.cards_ici = prCards(self, v, 'g_ici', id => { const i = I.itens.find(x => 'i:' + x.nome === id); return i ? prCard({ t1: i.nome, num: i.melhor ? icRS(i.melhor.preco) + '/' + i.un : (i.nVenc ? 'cotação vencida' : 'sem cotação'), t2: 'Referência ' + icRS(i.ref) + ' · ' + intPct(i.vRef), chip: [icSit(i), IC_SITC[icSit(i)]] }) : null; });
  v.cards_icf = prCards(self, v, 'g_icf', id => { const f = I.forn.find(x => 'f:' + x.id === id); return f ? prCard({ t1: f.nome, num: intPct(f.rel), t2: 'pontualidade ' + (f.pont === null ? '—' : prFmt(prMul(f.pont, 100), 0) + '%') }) : null; });
  v.cards_ich = prCards(self, v, 'g_ich', id => { const g = I.porHa.find(x => 'h:' + x.grupo === id); return g ? prCard({ t1: g.grupo, num: icRS(g.rsha) + '/ha', t2: icRS(g.total, 0) }) : null; });
  const agc = M.compras.filter(x => x.rec === 'Comprar agora').length;
  prStatus(v, [agc ? agc + ' insumo(s) para comprar agora' : 'nada urgente para comprar', I.acima ? I.acima + ' insumo(s) com cotação acima da referência' : 'cotações dentro da referência']
    .concat(I.vencidas ? [I.vencidas + ' insumo(s) só com cotação vencida'] : []).join(' · '), (I.acima || I.vencidas) ? 'yellow' : 'green');
  const pan = st.pr_pan; const PP = pan ? icPan(self, pan) : null; comPrimPainel(v, PP && PP.prim ? PP.prim : null, PP); prPainel(self, v, PP); }
"""


def ic():
    fname = 'IC.dc.html'; V.E._reset_screen(fname)
    g_icm = grid([dict(k='nome', l='Insumo', w=190), dict(k='atual', l='Preço agora', t='num', a='r', w=130), dict(k='v12', l='12 meses', t='num', a='r', w=100),
                  dict(k='tend', l='Tendência', w=140), dict(k='melhor', l='Mês mais barato', t='num', w=130), dict(k='nec', l='Próxima necessidade', t='num', w=150),
                  dict(k='rec', l='O que fazer', w=280), dict(k='eco', l='Economia estimada', t='num', a='r', w=140)],
                 [], edit=dict(m='pick'), gid='g_icm', total=False, qf=dict(k='rec', l='O que fazer', todas='Todos'))
    g_ici = grid([dict(k='nome', l='Insumo', w=190), dict(k='grupo', l='Grupo', w=120), dict(k='ult', l='Último pago', t='num', a='r', w=170), dict(k='ref', l='Referência', t='num', a='r', w=120),
                  dict(k='mel', l='Melhor cotação', t='num', a='r', w=190), dict(k='vref', l='vs referência', t='num', a='r', w=120), dict(k='vult', l='vs último', t='num', a='r', w=110),
                  dict(k='sit', l='Sinal', w=200)],
                 [], edit=dict(m='pick'), gid='g_ici', total=False, qf=dict(k='sit', l='Sinal', todas='Todos'))
    g_icf = grid([dict(k='nome', l='Fornecedor', w=220), dict(k='n', l='Cotações', t='num', a='r', w=100), dict(k='rel', l='Preço vs referência', t='num', a='r', w=160),
                  dict(k='prazo', l='Prazo de entrega', t='num', a='r', w=150), dict(k='pont', l='Pontualidade', t='num', a='r', w=170)],
                 [], edit=dict(m='pick'), gid='g_icf', total=False)
    g_ich = grid([dict(k='grupo', l='Grupo', w=200), dict(k='total', l='Total orçado', t='num', a='r', w=160), dict(k='rsha', l='R$/ha', t='num', a='r', w=140)],
                 [], edit=dict(m='pick'), gid='g_ich', total=False)
    V.EXTRAJS[0] = V._js(DI.js() + DI.js_precos() + _ijs() + IC_JS)
    # TAB-07 (DS-MODULOS-2, 17/10/2026): sem cartões de resumo sobre a 1ª lista; "em alta" está na coluna Tendência e "Comprar agora N" no
    # filtro rápido de "O que fazer"; a economia esperando o mês certo é o total da lista e abre os indicadores entre os blocos
    corpo = (AP.bloco('Preço e melhor mês para comprar', 'Preço de agora, tendência sem o efeito da época, o mês mais barato no histórico e o que fazer até a próxima necessidade do Planejar safra, já descontado o prazo de entrega. Esperar só aparece quando a época barateia 3% ou mais. Série sintética de 60 meses: histórico não é previsão.', g_icm + AP.cartoes('cards_icm'))
             + _ind(('Economia esperando o mês certo', 'k_es', 'k_esn'), ('Cotações acima da referência', 'k_ac', 'k_acn'), ('Economia pela melhor cotação', 'k_ec', 'k_ecn'), ('Insumos por hectare', 'k_ha', 'k_han'))
             + AP.bloco('Preço por insumo', 'Último preço pago × referência da safra × melhor cotação atual. Cotação 5% acima da referência vira alerta. O histórico de preço é sintético e vem marcado.', g_ici + AP.cartoes('cards_ici'))
             + AP.bloco('Fornecedores', 'Preço relativo (média das cotações contra a referência), prazo de entrega cotado e pontualidade (entregas no prazo ÷ entregas).', g_icf + AP.cartoes('cards_icf'))
             + AP.bloco('Custo de insumos por hectare', 'Σ (quantidade da safra × referência) ÷ área da safra, por grupo. Use para comparar com o orçamento.', g_ich + AP.cartoes('cards_ich')))
    V._shell('IC', 'Inteligência de compras', 'Preço, tendência e o melhor mês para comprar cada insumo antes da necessidade; abaixo, cotações, fornecedores e custo por hectare.', corpo, fname, 1300,
             'Referência e quantidades da safra (Planejar safra), cotações dos fornecedores homologados e pedidos. Nada é gravado aqui; a decisão de comprar é de Suprimentos.')


def build():
    iv()
    ic()
