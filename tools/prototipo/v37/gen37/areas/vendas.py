# -*- coding: utf-8 -*-
"""Comercial (grupo do menu logo depois de Produção, D-C01) · comercial e logística (docs/comercial/ESPECIFICACAO.md v1.1).
Três telas ligadas ao mesmo estado da Colheita (c.producao; regras em comercial.js e producao.js), sem redigitar:
  VEN.dc.html    Contratos e pedidos    planejamento: venda pronta ou futura, preço, condição, crédito, reserva de lote
  EXPED.dc.html  Expedição e entregas   execução: carga de saída (romaneio), pesagem, saída única, entrega, devolução
  PCOM.dc.html   Painel comercial       controle: oferta × compromissos × livre por período; preço médio e a receber
Mesmo motor da Colheita (areas/producao.py: painel, cartões, bloco, PR_UI_JS) e o mesmo script _js(), com o núcleo da carência (CE-01).
Uma ação primária por tela, escolhida pelo registro selecionado; sem o papel do comando, a primária mostra o dono (R-C14).
VE-01..VE-06 e LO-01..LO-04 continuam ocultos e intocados (D-C02). Dados sintéticos (a Lagoa Grande é sintética)."""
from engine import (grid, esc, MUTED, LINE, BTN_ST, EXTRA, EXTRAJS)
import engine as E
from ui37 import shell37, HEIGHTS37
import dados_comercial as DCOM
from areas import producao as AP

H = AP.H; F = AP.F; IF = AP.IF


def prim_html():
    """primária do cabeçalho (link ou botão, AP.prim_html) ou, sem o papel do comando, o próximo passo com o dono (texto, não botão)"""
    return (AP.prim_html() + f'<sc-if value="{H("prim_isT")}" hint-placeholder-val="{F()}"><span role="note" class="com-dono" style="display: inline-flex; align-items: center; '
            f'font-size: 13px; font-weight: 700; color: {MUTED}; padding: 8px 12px; border: 1px dashed {LINE}; border-radius: 10px; white-space: normal;">{H("prim_tt")}</span></sc-if>')


def _shell(fid, title, sub, corpo, fname, altura, foot):
    EXTRA.append('<style>' + AP.CSS + '</style>'); EXTRA.append(AP.painel()); corpo = corpo + AP.restaurar()
    HEIGHTS37[fname] = altura
    shell37(fid, title, corpo, fname=fname, subtitle=sub, status=(H('st_t'), 'yellow'), primary_html=prim_html(), search=False, footer=foot)
    AP._status(fname)


def _js(tela):
    """cenário + núcleo da carência + telas da Produção (PR_UI_JS, PR_PED_JS) + COMC e comercial.js + o comum do Comercial + a tela"""
    return AP._js(AP.PR_PED_JS + DCOM.js_regras() + COM_UI_JS + tela)


# =====================================================================================================================
# JS comum das três telas do Comercial (leitura e montagem; regras e comandos em comercial.js)
# =====================================================================================================================
COM_UI_JS = r'''
/* ===== Comercial · telas (VEN, EXPED, PCOM): só montam a tela; regras e comandos em comercial.js ===== */
const COM_TEM_EXPED = true, COM_TEM_PCOM = true;
const COM_PAP = { vender: ['comercial', 'gestor'], carga: ['comercial', 'expedicao', 'gestor'], saida: ['expedicao', 'gestor'], credito: ['gestor'] };
function comPode(k) { return !!g2umPapel(g2perfil(), COM_PAP[k]); }
function comDono(k) { return g2quemUm(COM_PAP[k]); }
const COM_PAPT = { vender: 'Comercial', carga: 'Comercial ou expedição', saida: 'Expedição', credito: 'Ana (gestora)' };
/* primária: com o papel, botão ou link; sem o papel, o próximo passo com o dono (padrão da O.S., CTL-3) */
function comPrim(v, p) { const pode = !!(p && (!p.papel || comPode(p.papel)));
  prPrim(v, pode ? p : null); v.prim_isT = !!(p && !pode); v.prim_tt = (p && !pode) ? (p.donoT || (comDono(p.papel) + ': ' + p.t.charAt(0).toLowerCase() + p.t.slice(1))) : ''; }
/* A6 da revisão: com o painel aberto e a ação dele à vista (rodapé, BOT-02), o cabeçalho não repete o verde com o mesmo rótulo e outro
   efeito (abrir de novo e apagar o que foi digitado); sem o papel, o cabeçalho continua dizendo o dono */
function comPrimPainel(v, prim, PP) { comPrim(v, PP && PP.prim ? null : prim); }
/* fazenda de uma venda (D-C22): a dos lotes reservados ou expedidos; sem lote, toda fazenda que tem o produto */
function comFazes(c, v) { const P = prP(c); const s = new Set();
  Object.values(P.reservas).filter(r => r.pedido === v.id).forEach(r => { const L = P.lotes[r.lote]; if (L) s.add(L.faz); });
  P.movs.filter(m => m.pedido === v.id && m.tipo === 'expedição').forEach(m => { const L = P.lotes[m.lote]; if (L) s.add(L.faz); });
  if (!s.size) { Object.values(P.lotes).filter(L => L.prod === v.prod).forEach(L => s.add(L.faz)); Object.values(PRDC.cult).filter(k => prUn(k.cultura).prod === v.prod).forEach(k => s.add(k.faz)); }
  return [...s]; }
function comFazVendaOk(self, c, v) { const f = self.state.mf_faz || 'Todas'; return f === 'Todas' || comFazes(c, v).indexOf(f) >= 0; }
function comSafVendaOk(self, v) { return prSafOk(self, v.saf || ''); }
function comVendaTipo(v) { return v.tipo === 'futura' ? 'Venda futura' : 'Pronta entrega'; }
function comNatTxt(v) { return comNat(v) === 'Venda' ? 'Venda' : comNat(v) + ' · liquidação em produto'; }
'''

# =====================================================================================================================
# VEN · Contratos e pedidos
# =====================================================================================================================
def ven():
    fname = 'VEN.dc.html'; E._reset_screen(fname)
    g = grid([dict(k='ven', l='Venda · cliente', w=210), dict(k='prod', l='Produto', w=180), dict(k='tipo', l='Tipo · janela', w=170),
              dict(k='qtd', l='Quantidade', t='num', a='r'), dict(k='preco', l='Preço', t='num', a='r', w=120), dict(k='ent', l='Entregue', t='num', a='r'),
              dict(k='res', l='Reservado', t='num', a='r'), dict(k='falta', l='Falta', t='num', a='r'), dict(k='sit', l='Situação · próximo passo', w=250)],
             [], edit=dict(m='pick'), gid='g_ven', total=False, qf=dict(k='sit', cut=' · ', l='Situação', todas='Todas'))
    EXTRAJS[0] = _js(VEN_JS)
    corpo = AP.bloco('Vendas', 'Pronta entrega reserva lote apto; venda futura compromete a previsão do período, não o estoque. Clique numa venda para reservar, aprovar crédito, programar carga ou encerrar o saldo.',
                     g + AP.cartoes('cards_ven'))
    _shell('VEN', 'Contratos e pedidos', 'O que vendi, a quem, a que preço, para quando, e o que falta cobrir com lote.', corpo, fname, 1100,
           'Uma venda é um registro só, do acordo à entrega: cliente e condição vêm do CD-05, o lote do estoque de produto; venda futura não desconta o físico (D-C03).')


VEN_JS = r'''
const PR_GRIDS = { g_ven: 1 };
const _g2rows0 = g2rows; g2rows = function (self, sp) { return PR_GRIDS[sp.id] ? sp.rows : _g2rows0(self, sp); };
/* próximo passo da venda (linha e painel): texto curto, texto longo com o dono e a ação da primária */
function comProx(c, v, st) { const P = prP(c); const cu = comCultura(v); const U = x => comTxtV(v, x); const hoje = prHoje();
  const rms = comRmsVenda(c, v.id); const prog = rms.find(r => r.st === 'Programada'); const tran = rms.find(r => r.st === 'Em trânsito');
  const venc = (v.fim && v.fim < hoje) ? ' · janela vencida em ' + prBr(v.fim) : '';
  if (st.t === 'Encerrada') return { t: 'saldo encerrado · ' + v.enc.motivo, p: 'Saldo encerrado em ' + prBr(v.enc.d) + ' por ' + v.enc.quem + ': ' + v.enc.motivo + '. Quantidade vigente ' + U(v.qtd) + ' (era ' + (v.enc.qtd0 === null || v.enc.qtd0 === undefined ? prFmtT(v.enc.qc0, 3) + ' ' + (v.un || '') : U(v.enc.qtd0)) + ').' };
  /* A-17: sem a massa da saca, nada que dependa dela anda; o próximo passo é registrar a massa com a fonte */
  if (st.t === 'Saca a conferir') return { t: 'Registrar a saca · ' + COM_PAPT.vender, p: 'Saca do contrato a conferir (' + v.fatAmb.map(x => x + ' kg').join(' ou ') + '): até registrar a massa com a fonte, falta, oferta, saída e crédito ficam suspensos. Nada é convertido sem esse registro.', a: 'saca', at: 'Registrar a saca do ' + v.id, red: true };
  /* A5 da revisão: venda já entregue com carga ainda programada (o 1º caminhão levou tudo): o passo é cancelar a carga que sobrou */
  if (st.t === 'Entregue' && prog) return { t: 'Cancelar a ' + prog.id + ' (venda entregue) · ' + COM_PAPT.carga, p: v.id + ' já entregue: a ' + prog.id + ' ficou programada sem saldo a entregar. ' + comDono('carga') + ' cancela a carga com o motivo em Expedição e entregas.', rm: prog.id, red: true };
  if (st.t === 'Entregue') { const tt = comTitulos(c, t => t.venda === v.id); const ar = prSoma(tt.map(t => t.valor)); const vn = tt.filter(t => comVencido(t));
    if (comNat(v) !== 'Venda') return { t: 'entregue · liquidação em produto', p: 'Entregue: liquidação em produto (GE-08).' };
    if (!tt.length) return { t: 'entregue', p: 'Entregue.' };
    return { t: 'entregue · ' + comRS(ar) + (vn.length ? ' vencido · cobrar' : ' a receber' + (tt[tt.length - 1].venc ? ' até ' + prBr(tt[tt.length - 1].venc) : '')), p: 'Entregue. A receber ' + comRS(ar) + ': ' + tt.map(t => t.rm + ' ' + comRS(t.valor) + (t.venc ? (comVencido(t) ? ' vencido em ' : ' vence ') + prBr(t.venc) : ' (em trânsito)')).join(' · ') + '. Recebimento é do Financeiro (fora desta etapa).' }; }
  if (st.t === 'Em risco') { const x = st.imp[0]; const i = x.I.imp[0];
    return { t: 'expedição impedida: ' + x.r.lote + ' · ' + i.q + ' resolve', p: 'Expedição impedida no ' + x.r.lote + ': ' + i.t + '. Quem resolve: ' + i.q + '. Se não resolver a tempo, ' + comDono('vender') + ' troca o lote ou cancela a reserva.', red: true }; }
  if (st.t === 'Aguardando crédito') { const ant = st.cred.ant; const t = ant ? 'Conferir pagamento antecipado do ' + v.id : 'Aprovar crédito do ' + v.id;
    return { t: (ant ? 'Conferir pagamento' : 'Aprovar crédito') + ' · Ana (gestora)' + venc, p: 'Crédito: ' + st.cred.prob + '. ' + comDono('credito') + (ant ? ' confere o pagamento antecipado antes da saída.' : ' aprova o crédito antes da saída (vale até o valor coberto).'), a: 'credito', at: t, red: true }; }
  if (tran) return { t: 'Confirmar entrega da ' + tran.id + ' · Expedição', p: tran.id + ' em trânsito: ' + comDono('saida') + ' confirma a entrega (data e devolução, se houver).', rm: tran.id };
  const np = comNaoProg(c, v.id); const ls = prCmp(st.falta, 0) > 0 ? comLotesPara(c, v) : [];
  /* A5 da revisão: carga programada sem reserva que a cubra não é "Confirmar saída"; o passo é reservar de novo (ou cancelar a carga) */
  const dz = prog ? comRmDescoberto(c, prog) : [];
  if (prog && dz.length) { const d0 = dz[0]; const tx = prog.id + ' programada com ' + U(d0.prev) + ' do ' + d0.lote + ', mas a reserva do ' + v.id + ' nesse lote cobre ' + U(d0.cobre);
    if (prCmp(st.falta, 0) > 0 && ls.length) return { t: 'Reservar lote para a ' + prog.id + ' · ' + COM_PAPT.vender + venc, p: tx + ': reservar lote apto (' + ls.map(L => L.id + ' ' + U(prSaldos(c, L).disp)).join(', ') + ') ou cancelar a carga em Expedição e entregas.', a: 'reservar', at: 'Reservar lote para o ' + v.id, red: true };
    return { t: prog.id + ' sem reserva · reservar ou cancelar a carga', p: tx + '. Sem lote apto com disponível: ' + comDono('carga') + ' cancela a carga em Expedição e entregas.', rm: prog.id, red: true }; }
  if (prog) return { t: 'Confirmar saída da ' + prog.id + ' · Expedição' + venc, p: prog.id + ' programada para ' + prBr(prog.dprev) + ': ' + comDono('saida') + ' confirma a saída com a pesagem.', rm: prog.id };
  /* ordem do §3.1: reservar o que falta antes de programar a carga (a carga sai cheia, um romaneio a menos) */
  if (prCmp(st.falta, 0) > 0 && ls.length) return { t: 'Reservar lote · ' + COM_PAPT.vender + venc, p: 'Falta ' + U(st.falta) + ': reservar lote apto (' + ls.map(L => L.id + ' ' + U(prSaldos(c, L).disp)).join(', ') + ').' + (prCmp(np, 0) > 0 ? ' Depois, programar a carga de ' + U(prSoma([np, st.falta])) + '.' : ''), a: 'reservar', at: 'Reservar lote para o ' + v.id };
  if (prCmp(np, 0) > 0 && (v.tipo === 'pronta' || comPeriodoComecou(c, v))) { const pp = { t: 'Programar carga · ' + COM_PAPT.carga + venc, p: U(np) + ' reservados sem carga: ' + comDono('carga') + ' programa a carga (veículo, placa e data).', a: 'programar', at: 'Programar carga do ' + v.id };
    if (!COM_TEM_EXPED) { pp.t = 'aguardar programação da carga' + venc; pp.a = ''; } return pp; }
  if (prCmp(st.falta, 0) > 0) {
    if (v.tipo === 'futura') return { t: 'compromete a previsão · reservar na colheita', p: 'Venda futura: compromete a oferta da ' + (v.sem ? prSemTxt(v.sem) : 'safra ' + v.saf) + '; reservar lote quando houver colheita apta (o físico não muda antes).' };
    return { t: 'sem lote apto · aguardar colheita ou liberação' + venc, p: 'Falta ' + U(st.falta) + ' e nenhum lote apto do produto tem disponível' + (v.ini ? ' que não vença antes de ' + prBr(v.ini) : '') + '.', red: !!venc }; }
  if (prCmp(np, 0) > 0) return { t: 'coberto · programar carga na janela', p: 'Coberto por reserva; a carga sai no período da venda futura (' + v.janela + ').' };
  return { t: 'aguardar a saída', p: 'Coberto: aguardar a saída.' }; }
function comVenRow(c, v) { const cu = comCultura(v); const U = x => comTxtV(v, x); const st = comSitVenda(c, v); const nx = comProx(c, v, st);
  const ent = prExpedido(c, v.id); const pz = comPrecoTxtV(v); const amb = prAmb(v) && !v.enc; const nota = v.obs || (v.ref ? 'saldo do ' + v.ref : ''); const tp = comVendaTipo(v) + ' · ' + (v.janela || '') + (nota ? ' · ' + nota : '');
  const ac = comNat(v) === 'Venda' ? comAvisoCred(v.cliente) : '';
  return { id: v.id, ro: true, v: { ven: v.id, prod: v.prod, tipo: comVendaTipo(v), qtd: amb ? -1 : (v.qtd || 0), preco: Number(v.preco), ent, res: st.res, falta: amb ? -1 : st.falta, sit: st.t },
    s: { ven: v.id + ' ' + v.cliente, prod: v.prod, tipo: tp, qtd: comQtdTxt(v), preco: pz, ent: U(ent), res: U(st.res), falta: amb ? 'suspensa' : U(st.falta), sit: st.t + ' · ' + nx.t },
    p: { ven: [{ k: 'b', t: v.id }, { k: 'mut', t: ' · ' + v.cliente }].concat(comNat(v) !== 'Venda' ? [{ k: 'br' }, { k: 'mut', t: comNat(v) + ' · liquidação em produto' }] : []),
      prod: [{ k: 'txt', t: v.prod }].concat(v.classe || v.saf ? [{ k: 'br' }, { k: 'mut', t: [v.classe, v.saf].filter(Boolean).join(' ') }] : []),
      tipo: [{ k: 'txt', t: comVendaTipo(v) }, { k: 'br' }, { k: 'mut', t: (v.janela || '') + (nota ? ' · ' + nota : '') }],
      qtd: amb ? [{ k: 'txt', t: prFmtT(v.qc, 3) + ' ' + (v.un || '') }, { k: 'br' }, { k: 'cn', c: 'red', t: 'saca de ' + v.fatAmb.join(' ou ') + ' kg?' }] : prTx(comQtdTxt(v)), preco: [{ k: 'txt', t: pz }], ent: prTx(U(ent)), res: prTx(U(st.res)),
      falta: amb ? [{ k: 'mut', t: 'suspensa' }] : [{ k: 'b', t: U(st.falta) }],
      sit: [{ k: 'chip', t: st.t, c: st.c }, { k: 'br' }, { k: 'mut', t: nx.t }].concat(ac && st.t !== 'Entregue' && st.t !== 'Encerrada' ? [{ k: 'br' }, { k: 'cn', c: 'red', t: 'aviso: ' + ac }] : []) } }; }
function PREVALS(self, v) { cenOuvir(self); prTopo(self, v); const c = cenGet(); self._c = c; const P = prP(c);
  self.g2perfilFecha = { pr_modo: null, pr_form: null, pr_err: '' };
  self.g2pick = (gid, rid) => self.setState({ pr_sel: { g: gid, id: rid }, pr_pan: { g: gid, id: rid }, pr_form: null, pr_err: '', pr_ferr: null, pr_modo: null, pr_cx: null, pr_ch: prChave('W-RS') });
  const vs = Object.values(P.pedidos).filter(x => comFazVendaOk(self, c, x) && comSafVendaOk(self, x)).sort((a, b) => a.id.localeCompare(b.id));
  GR('g_ven').rows = vs.map(x => comVenRow(c, x)); self._vs = vs; }
/* formulário Registrar venda (§3.1): só quantidade e preço digitados; cliente, produto, tipo, janela, condição e modalidade por toque */
function comFormVenda(self, c) { const FS = Object.assign({}, self.state.pr_form || {}); const fv = (k, d) => FS[k] !== undefined ? FS[k] : (d === undefined ? '' : String(d)); const ch0 = self.state.pr_ch;   /* valores do formulário e chave lidos no desenho: o 2º clique repete o mesmo conteúdo e a mesma chave (R-C03) */
  const hoje = prHoje(); const nat = fv('nat', 'Venda'); const papel = nat === 'Venda' ? 'Cliente' : 'Fornecedor';
  const cps = Object.values(COMC.cp).filter(p => p.papeis.indexOf(papel) >= 0).sort((a, b) => a.nome.localeCompare(b.nome));
  const cli = fv('cli', ''); const cp = comCp(cli); const prods = comProdutos(c); const doCli = comProdCp(cp).filter(p => prods.indexOf(p) >= 0);
  const ordP = doCli.concat(prods.filter(p => doCli.indexOf(p) < 0)); const pro = fv('pro', doCli[0] || (ordP.length === 1 ? ordP[0] : '')); const cu = comCulturaProd(pro);
  const tipo = fv('tipo', 'pronta'); const fs = [];
  fs.push(prFld(self, 'nat', 'Natureza', { t: 'opts', v: nat, opts: [{ v: 'Venda', t: 'Venda' }, { v: 'CPR', t: 'CPR' }, { v: 'Barter', t: 'Barter' }], h: nat === 'Venda' ? '' : 'CPR e barter: com fornecedor, liquidação em produto (sem a receber).' }));
  fs.push(prFld(self, 'cli', nat === 'Venda' ? 'Cliente (CD-05)' : 'Fornecedor (CD-05)', { t: 'opts', v: cli, opts: cps.map(p => ({ v: p.nome, t: p.nome })),
    h: cp ? [cp.cond ? 'condição ' + cp.cond : '', cp.lim ? 'limite ' + comRS(cp.lim) + (cp.limv ? ' até ' + prBr(cp.limv) + '/' + cp.limv.slice(2, 4) : '') : '', cp.entrega].filter(Boolean).join(' · ') : 'Cliente novo: cadastre no CD-05 (Parceiros e fornecedores).' }));
  fs.push(prFld(self, 'pro', 'Produto', { t: 'opts', v: pro, opts: ordP.map(p => ({ v: p, t: p + (doCli.indexOf(p) >= 0 ? ' · do cliente' : '') })), h: cu ? 'Unidade ' + comUn(cu) + '; classe ' + (comClasse(c, pro) || 'sem classe (fruta de campo)') + '; destino ' + (PRDC.dest['MI-BR']) + '.' : '' }));
  fs.push(prFld(self, 'tipo', 'Tipo', { t: 'opts', v: tipo, opts: [{ v: 'pronta', t: 'Pronta entrega' }, { v: 'futura', t: 'Venda futura' }], h: tipo === 'futura' ? 'Compromete a previsão do período; não desconta o estoque até reservar lote.' : 'Sai do estoque: reserva lote apto.' }));
  let jan = { ini: '', fim: '', sem: '', saf: '' };
  if (tipo === 'pronta') { const s0 = prSem(hoje); const fimS = prDiaMais(prSemIni(s0), 6); const p1 = prSemIni(prSemMais(s0, 1));
    const op = [{ v: 'esta', t: 'Esta semana · ' + prBr(hoje) + '–' + prBr(fimS), ini: hoje, fim: fimS }, { v: 'prox', t: 'Próxima semana · ' + prBr(p1) + '–' + prBr(prDiaMais(p1, 6)), ini: p1, fim: prDiaMais(p1, 6) }, { v: 'datas', t: 'Outras datas' }];
    const j = fv('jan', ''); fs.push(prFld(self, 'jan', 'Janela de entrega', { t: 'opts', v: j, opts: op.map(o => ({ v: o.v, t: o.t })) }));
    const o = op.find(x => x.v === j); if (o && o.ini) { jan.ini = o.ini; jan.fim = o.fim; }
    if (j === 'datas') { fs.push(prFld(self, 'di', 'De', { t: 'txt', im: 'numeric', u: 'dd/mm', ph: 'ddmm', h: 'Só os números: 2809 = 28/09.' })); fs.push(prFld(self, 'df', 'Até', { t: 'txt', im: 'numeric', u: 'dd/mm', ph: 'ddmm' }));
      jan.ini = prIsoFut(fv('di', '')); jan.fim = prIsoFut(fv('df', '')) || jan.ini; } }
  else if (cu && comSemanal(cu)) { const ws = comSemanasFut(hoje, 4);
    fs.push(prFld(self, 'sem', 'Semana (ainda não começou)', { t: 'opts', v: fv('sem', ''), opts: ws.map(w => { const o = prOfertaSem(c, pro, w); return { v: w, t: prSemTxt(w) + ' · ' + (o.livre === null ? 'oferta suspensa (saca a conferir: ' + o.amb.join(', ') + ')' : (o.tem ? 'livre ' + comTxt(cu, o.livre) : 'sem versão publicada')) }; }),
      h: 'A semana em curso já está no estoque: venda como pronta entrega.' })); jan.sem = fv('sem', ''); }
  else if (cu) { const sfs = comSafrasFut(c, pro);
    fs.push(prFld(self, 'saf', 'Safra (ainda não colhida)', { t: 'opts', v: fv('saf', sfs.length === 1 ? sfs[0] : ''), opts: sfs.map(sf => { const o = prOfertaSafra(c, pro, sf); return { v: sf, t: 'Safra ' + sf + ' · ' + (o.livre === null ? 'oferta suspensa (saca a conferir: ' + o.amb.join(', ') + ')' : (o.tem ? 'livre ' + comTxt(cu, o.livre) : 'sem versão publicada')) }; }) }));
    jan.saf = fv('saf', sfs.length === 1 ? sfs[0] : ''); }
  const ref = (COMC.ref || {})[pro];
  fs.push(prFld(self, 'q', 'Quantidade', { t: 'txt', u: cu ? comUn(cu) : '', h: cu ? 'Na unidade comercial (' + comUn(cu) + ').' : '' }));
  fs.push(prFld(self, 'pr', 'Preço', { t: 'txt', u: cu ? 'R$/' + comUn(cu) : 'R$', h: ref ? 'Referência de mercado: ' + comPrecoTxt(cu, ref.p) + ' · ' + ref.fonte + '.' : (pro ? 'Sem cotação de referência (ausente ≠ zero).' : '') }));
  if (nat === 'Venda') { const cd = fv('cond', cp ? cp.cond : '');
    fs.push(prFld(self, 'cond', 'Condição de pagamento', { t: 'opts', v: cd, opts: COMC.cond.map(x => ({ v: x.t, t: x.t })), h: cd ? 'Vencimento: ' + ((comCond(cd) || {}).ev || '') + '.' + (cd === 'Antecipado' ? ' A saída exige a gestora conferir o pagamento.' : '') : 'Herdada do CD-05; o acordo manda (corrija por toque).' })); }
  const md = fv('mod', cp ? comModalCp(cp) : '');
  fs.push(prFld(self, 'mod', 'Modalidade', { t: 'opts', v: md, opts: [{ v: 'retira', t: COM_MODAL.retira }, { v: 'entrega', t: COM_MODAL.entrega }], h: cp && cp.entrega ? 'Local: ' + cp.entrega : '' }));
  /* avisos ao vivo: crédito do cliente e déficit da oferta do período */
  const av = []; if (cp && nat === 'Venda') { const a = comAvisoCred(cli); if (a) av.push('Aviso de crédito: ' + a + '.'); }
  if (tipo === 'futura' && cu && (jan.sem || jan.saf) && prNumOk(fv('q', ''))) { const o = jan.sem ? prOfertaSem(c, pro, jan.sem) : prOfertaSafra(c, pro, jan.saf); if (o.livre === null) av.push('Aviso: a oferta da ' + (jan.sem ? prSemTxt(jan.sem) : 'safra ' + jan.saf) + ' está suspensa até registrar a saca de ' + o.amb.join(', ') + ': o déficit não é calculado.');
    const liv = o.livre === null ? 0 : prSub(o.livre, prEstBase(cu, prNum(fv('q', ''))));
    if (prCmp(liv, 0) < 0) av.push('Aviso: com esta venda a oferta da ' + (jan.sem ? prSemTxt(jan.sem) : 'safra ' + jan.saf) + ' fica em déficit de ' + comTxt(cu, prSub(0, liv)) + ' (não trava, D-C16).'); }
  return { fields: fs, av, go: () => { const ch = ch0 || prChave('W-VEN'); const r = prRun(self, x => comVender(x, { cliente: cli, natureza: nat, prod: pro, tipo, ini: jan.ini, fim: jan.fim, sem: jan.sem, saf: jan.saf, qtd: fv('q', ''), preco: fv('pr', ''),
      cond: nat === 'Venda' ? fv('cond', cp ? cp.cond : '') : '', modal: md, ator: g2perfil(), chave: ch }), { pr_form: null, pr_ch: null });
    if (!r.erro && r.v) self.setState({ pr_sel: { g: 'g_ven', id: r.v.id }, pr_pan: { g: 'g_ven', id: r.v.id }, pr_ch: prChave('W-RS') }); } }; }
/* dd/mm → ISO a partir de hoje (janela de venda: data de hoje em diante; 1 dia antes de hoje é do ano seguinte só se passar de 180 dias) */
function prIsoFut(t) { const m = /^(\d\d)\/?(\d\d)$/.exec(String(t || '').trim());   /* "2809" ou "28/09": o teclado numérico do celular não tem barra (A11 da revisão) */ if (!m) return ''; const h = prHoje(); let y = Number(h.slice(0, 4)); const d = y + '-' + m[2] + '-' + m[1]; return d < prDiaMais(h, -180) ? (y + 1) + '-' + m[2] + '-' + m[1] : d; }
function comPanVenda(self, c, v) { const FS = Object.assign({}, self.state.pr_form || {}); const fv = (k, d) => FS[k] !== undefined ? FS[k] : (d === undefined ? '' : String(d)); const ch0 = self.state.pr_ch;   /* valores do formulário e chave lidos no desenho: o 2º clique repete o mesmo conteúdo e a mesma chave (R-C03) */
  const P = prP(c); const cu = comCultura(v); const U = x => comTxtV(v, x); const st = comSitVenda(c, v); const nx = comProx(c, v, st); const md = self.state.pr_modo; const cx = self.state.pr_cx;
  const cp = comCp(v.cliente) || {}; const tt = comTitulos(c, t => t.venda === v.id); const k = comCond(v.cond) || {};
  const ar = comAReceber(c, t => t.cliente === v.cliente); const cred = comNat(v) !== 'Venda' ? 'liquidação em produto' : ((cp.lim ? 'limite ' + comRS(cp.lim) + (cp.limv ? ' até ' + prBr(cp.limv) + '/' + cp.limv.slice(2, 4) : '') : 'sem limite') + ' · a receber ' + comRS(ar)
    + (v.cred ? ' · ' + (v.cred.ant ? 'pagamento antecipado conferido' : 'aprovado até ' + comRS(v.cred.ate)) + ' por ' + v.cred.quem + (v.cred.rev ? ' (' + v.cred.rev + ')' : '') : ''));
  const rs = Object.values(P.reservas).filter(r => r.pedido === v.id).map(r => { const L = P.lotes[r.lote]; const I = r.st === 'Ativa' ? comImpede(c, v, L) : { imp: [] };
    return { c: [[r.id, 'b'], r.lote, U(r.kg) + (r.exp ? ' (expedido ' + U(r.exp) + ')' : ''), r.st, I.imp.length ? ['saída impedida: ' + I.imp[0].q + ' resolve', 'red'] : '', r.canc ? 'motivo: ' + r.canc.motivo : '', r.quem || ''].filter(Boolean),
      a: (r.st === 'Ativa' && comPode('vender')) ? { t: 'Cancelar reserva', go: () => self.setState({ pr_cx: r.id, pr_modo: null, pr_form: null, pr_err: '' }) } : null, l: { t: 'Abrir lote', h: 'PROD.dc.html#' + r.lote } }; });
  const cg = comRmsVenda(c, v.id).map(r => ({ c: [[r.id, 'b'], [r.st, r.st === 'Cancelada' ? 'mut' : ''], r.saida ? U(r.saida.liq) + ' saída ' + prBr(r.saida.d) : 'previsto ' + U(prSoma(r.lotes.map(l => l.prev))) + ' · ' + prBr(r.dprev), r.lotes.map(l => l.lote).join(', '), r.hist ? 'registro da Colheita' : (r.veic || '')].filter(Boolean),
    l: COM_TEM_EXPED ? { t: 'Abrir carga', h: 'EXPED.dc.html#' + r.id } : null }));
  const fin = tt.map(t => ({ c: [[t.rm, 'b'], U(t.kg), comRS(t.valor), t.venc ? (comVencido(t) ? ['vencido em ' + prBr(t.venc) + ' · cobrar', 'red'] : 'vence ' + prBr(t.venc)) : 'vence ' + (k.dias || 0) + ' d após a entrega'] }));
  const mv = P.movs.filter(m => m.pedido === v.id).slice().reverse().map(m => ({ c: [[m.id, 'b'], prBr(m.d) + ' ' + (m.at || ''), m.tipo, m.fis === false ? ['sem efeito no físico', 'mut'] : U(m.kg), m.lote, m.rm || m.reserva || '', m.quem || ''].filter(Boolean) }));
  const PPx = { title: v.id + ' · ' + v.cliente, chip: [st.t, st.c], sub: v.prod + ' · ' + comVendaTipo(v).toLowerCase() + ' · ' + (v.janela || '') + (v.ref ? ' · saldo do ' + v.ref : ''),
    next: nx.p, nred: !!nx.red,
    kv: [{ l: 'Quantidade', v: comQtdTxt(v) }, { l: 'Preço', v: comPrecoTxtV(v) }, { l: 'Valor', v: comRS(comValorQc(v)) },
      { l: 'Unidade do contrato', v: v.fatConf ? 'saca de ' + v.fatConf.fat + ' kg · ' + v.fatConf.fonte + ' · registrada por ' + v.fatConf.quem + ' em ' + prBr(v.fatConf.d) : (v.fatAmb ? 'a conferir · ' + v.fatOrig : comUnV(v) + (v.fatOrig ? ' · ' + v.fatOrig : '')) }, { l: 'Entregue', v: U(prExpedido(c, v.id)) },
      { l: 'Reservado', v: U(st.res) }, { l: 'Falta', v: prAmb(v) && !v.enc ? 'suspensa (saca a conferir)' : U(st.falta) }, { l: 'Natureza', v: comNatTxt(v) }, { l: 'Condição', v: v.cond + (k.ev ? ' · ' + k.ev : '') },
      { l: 'Modalidade · local', v: (COM_MODAL[v.modal] || '') + (v.local ? ' · ' + v.local : '') }, { l: 'Destino', v: PRDC.dest[v.dest || 'MI-BR'] || v.dest }, { l: 'Crédito do cliente', v: cred },
      { l: 'Registrada', v: (v.quem || '—') + (v.d ? ' · ' + prBr(v.d) : '') + (v.obs ? ' · ' + v.obs : '') }],
    secs: [{ t: 'Atendimento · reservas por lote', rows: rs, vazio: 'Nenhuma reserva.' }, { t: 'Cargas de saída', rows: cg, vazio: 'Nenhuma carga.' }, { t: 'Financeiro · a receber', rows: fin, vazio: comNat(v) === 'Venda' ? 'Nada a receber ainda (nasce na saída).' : 'Liquidação em produto (GE-08).' },
      { t: 'Movimentos', rows: mv, vazio: 'Nenhum movimento.' }], err: self.state.pr_err };
  if (cx) { PPx.form = { t: 'Cancelar ' + cx, h: 'O motivo fica no histórico; o disponível do lote volta.', fields: [prFld(self, 'mot', 'Motivo do cancelamento', { t: 'txt', im: 'text', ph: 'ex.: cliente adiou a retirada' })] };
    PPx.prim = { t: 'Cancelar ' + cx, go: () => prRun(self, x => prCancelarReserva(x, cx, fv('mot', ''), g2perfil()), { pr_cx: null, pr_form: null }) }; PPx.sec = [{ t: 'Manter reserva', go: () => self.setState({ pr_cx: null, pr_err: '' }) }]; return PPx; }
  if (md === 'encerrar') { PPx.form = { t: 'Encerrar saldo do ' + v.id + ' · ' + COM_PAPT.vender, h: 'A quantidade vigente passa ao entregue; as reservas ativas são canceladas na mesma operação. Carga programada: cancele antes.', fields: [prFld(self, 'mot', 'Motivo', { t: 'txt', im: 'text', ph: 'ex.: cliente reduziu o contrato' })] };
    PPx.prim = { t: 'Encerrar saldo', go: () => prRun(self, x => comEncerrar(x, { venda: v.id, motivo: fv('mot', ''), ator: g2perfil(), chave: ch0 }), { pr_modo: null, pr_form: null }) };
    PPx.sec = [{ t: 'Manter venda', go: () => self.setState({ pr_modo: null, pr_err: '' }) }]; return PPx; }
  if (nx.a === 'saca' && comPode('vender')) { const fk = fv('fat', ''); const fo0 = 'Contrato ' + (v.ref || v.id);
    PPx.form = { t: 'Registrar a saca do ' + v.id + ' · ' + COM_PAPT.vender, h: 'Confira a massa da saca no contrato. A quantidade do contrato (' + prFmtT(v.qc, 3) + ' ' + (v.un || '') + ') fica; o kg nasce da massa escolhida.',
      fields: [prFld(self, 'fat', 'Massa da saca no contrato', { t: 'opts', v: fk, opts: v.fatAmb.map(x => ({ v: x, t: x + ' kg' })), h: fk ? prFmtT(v.qc, 3) + ' ' + (v.un || '') + ' × ' + fk + ' kg = ' + prFmtT(prMul(v.qc, fk), 3) + ' kg' : '' }),
               prFld(self, 'fonte', 'Fonte', { t: 'txt', im: 'text', v: fo0, h: 'Onde a massa está escrita (contrato e cláusula).' })] };
    PPx.prim = { t: 'Registrar a saca', go: () => prRun(self, x => comConverterSaca(x, { venda: v.id, fat: fk, fonte: fv('fonte', fo0), ator: g2perfil(), chave: ch0 || prChave('W-SACA') }), { pr_form: null, pr_ch: prChave('W-RS') }) }; }
  else if (nx.a === 'credito' && comPode('credito')) { PPx.form = { t: nx.at + ' · Ana (gestora)', h: st.cred.ant ? 'Confirme que o pagamento antecipado entrou: a saída fica liberada no crédito e a venda não entra no a receber.' : 'A aprovação vale até ' + comRS(comExpo(c, v.cliente, { [v.id]: st.res })) + ' (a receber de ' + v.cliente + ' + reservado não expedido do ' + v.id + ').', fields: [] };
    PPx.prim = { t: nx.at, go: () => prRun(self, x => comAprovarCredito(x, { venda: v.id, ator: g2perfil(), chave: ch0 || prChave('W-CRED') }), { pr_form: null, pr_ch: prChave('W-CRED') }) }; }
  else if (nx.a === 'reservar' && comPode('vender')) { const f = prFormReserva(self, c, null, v, 'ped', comLotesPara(c, v));
    PPx.form = { t: 'Reservar lote para o ' + v.id + ' · ' + COM_PAPT.vender, h: 'Só lote apto, do mesmo produto e classe, que não vence antes do início da janela' + (comIni(v) ? ' (' + prBr(comIni(v)) + ')' : '') + '.', fields: f.fields }; PPx.prim = { t: 'Reservar', go: f.go }; }
  else if (nx.a === 'programar' && comPode('carga')) PPx.prim = { t: nx.at, h: 'EXPED.dc.html#nova:' + v.id };
  if (st.t !== 'Encerrada' && st.t !== 'Entregue' && comPode('vender')) PPx.sec = [{ t: 'Encerrar saldo', go: () => self.setState({ pr_modo: 'encerrar', pr_form: null, pr_err: '', pr_ch: prChave('W-ENC') }) }];
  return PPx; }
function EXTRAVALS(self, v) { prRst(self, v); const c = self._c || cenGet(); const P = prP(c); const st = self.state;
  v.cards_ven = prCards(self, v, 'g_ven', id => { const x = P.pedidos[id]; if (!x) return null; const s = comSitVenda(c, x); const nx = comProx(c, x, s); const cu = comCultura(x);
    return prCard({ t1: x.id + ' · ' + x.cliente, num: prAmb(x) && !x.enc ? prFmtT(x.qc, 3) + ' ' + (x.un || '') + ' · saca a conferir' : comQtdTxt(x) + ' · ' + comPrecoTxtV(x), t2: x.prod + ' · ' + comVendaTipo(x).toLowerCase() + ' · ' + (x.janela || '') + ' · falta ' + (prAmb(x) && !x.enc ? 'suspensa' : comTxtV(x, s.falta)), chip: [s.t, s.c], nx: nx.t, go: () => self.g2pick('g_ven', id) }); });
  const sel = st.pr_sel; const x = sel && P.pedidos[sel.id]; let prim = null;
  if (x) { const s = comSitVenda(c, x); const nx = comProx(c, x, s);
    if (nx.a === 'saca') prim = { t: nx.at, papel: 'vender', go: () => self.setState({ pr_pan: { g: 'g_ven', id: x.id }, pr_form: null, pr_err: '', pr_modo: null, pr_cx: null, pr_ch: prChave('W-SACA') }) };
    else if (nx.a === 'credito') prim = { t: nx.at, papel: 'credito', go: () => self.setState({ pr_pan: { g: 'g_ven', id: x.id }, pr_form: null, pr_err: '', pr_modo: null, pr_ch: prChave('W-CRED') }) };
    else if (nx.a === 'reservar') prim = { t: nx.at, papel: 'vender', go: () => self.setState({ pr_pan: { g: 'g_ven', id: x.id }, pr_form: null, pr_err: '', pr_modo: null, pr_cx: null, pr_ch: prChave('W-RS') }) };
    else if (nx.a === 'programar') prim = { t: nx.at, papel: 'carga', h: 'EXPED.dc.html#nova:' + x.id }; }
  else prim = { t: 'Registrar venda', papel: 'vender', go: () => self.setState({ pr_pan: { g: 'nova' }, pr_sel: null, pr_form: null, pr_err: '', pr_modo: null, pr_ch: prChave('W-VEN') }) };
  const vs = self._vs || []; const n = t => vs.filter(y => comSitVenda(c, y).t === t).length; const sc = n('Sem reserva') + n('Parcial'), cr = n('Aguardando crédito'), rk = n('Em risco'), sa = n('Saca a conferir');
  prStatus(v, [sc ? sc + (sc > 1 ? ' vendas sem cobertura' : ' venda sem cobertura') : 'vendas cobertas', cr ? cr + ' aguardando crédito' : '', rk ? rk + ' em risco' : '', sa ? sa + ' com a saca a conferir' : ''].filter(Boolean).join(' · '), rk || sa ? 'red' : (sc || cr ? 'yellow' : 'green'));
  const pan = st.pr_pan; let PP = null;
  if (pan && pan.g === 'nova') { const f = comFormVenda(self, c);
    PP = { title: 'Registrar venda', chip: ['Nova venda', 'gray'], sub: 'Pronta entrega ou venda futura · cliente do CD-05, produto do estado', next: f.av.join(' '), nred: f.av.length > 0,
      form: { t: 'Registrar venda · ' + COM_PAPT.vender, h: 'Toque nas opções; digite só a quantidade e o preço. Destino: ' + PRDC.dest['MI-BR'] + '.', fields: f.fields }, err: st.pr_err, prim: comPode('vender') ? { t: 'Registrar venda', go: f.go } : null }; }
  else if (pan && P.pedidos[pan.id]) PP = comPanVenda(self, c, P.pedidos[pan.id]);
  comPrimPainel(v, prim, PP); prPainel(self, v, PP); }
/* entrada por link: VEN.dc.html#PV-036 abre a venda; #nova:<produto>:<período> abre o formulário com produto, tipo e período herdados (Painel) */
function comHashVen(self) { if (self.__ch) return; self.__ch = 1; const ab = () => { let h = ''; try { h = decodeURIComponent(location.hash || '').slice(1); } catch (e) {} const P = prP(cenGet());
  if (P.pedidos[h]) { setTimeout(() => self.g2pick('g_ven', h), 0); return; }
  const m = /^nova:([^:]+):(.+)$/.exec(h); if (m) { const pro = m[1], per = m[2]; const f = { pro };
    if (/^est:/.test(per)) f.tipo = 'pronta'; else if (/^\d{4}-W\d\d$/.test(per)) { f.tipo = 'futura'; f.sem = per; } else { f.tipo = 'futura'; f.saf = per; }
    setTimeout(() => self.setState({ pr_pan: { g: 'nova' }, pr_sel: null, pr_form: f, pr_err: '', pr_modo: null, pr_ch: prChave('W-VEN') }), 0); } };
  ab(); try { window.addEventListener('hashchange', ab); } catch (e) {} }
const _EXV = EXTRAVALS; EXTRAVALS = function (self, v) { comHashVen(self); _EXV(self, v); };
'''


# =====================================================================================================================
# EXPED · Expedição e entregas
# =====================================================================================================================
def exped():
    fname = 'EXPED.dc.html'; E._reset_screen(fname)
    g = grid([dict(k='rm', l='Carga · romaneio', w=150), dict(k='ven', l='Venda · cliente', w=200), dict(k='prod', l='Produto · lotes', w=210),
              dict(k='prev', l='Previsto', t='num', a='r'), dict(k='sai', l='Saída', t='num', a='r'), dict(k='mod', l='Modalidade · veículo', w=190),
              dict(k='dt', l='Data', t='date', w=110), dict(k='sit', l='Situação · próximo passo', w=260)],
             [], edit=dict(m='pick'), gid='g_rm', total=False, qf=dict(k='sit', cut=' · ', l='Situação', todas='Todas'), so=dict(k='dt', d=True),
             tools=(f'<span role="group" aria-label="Período" style="display: inline-flex; gap: 6px;">'
                    f'<button type="button" aria-pressed="{H("dh_on")}" onClick="{H("dh")}" style="{H("dh_st")}">Hoje</button>'
                    f'<button type="button" aria-pressed="{H("ds_on")}" onClick="{H("ds")}" style="{H("ds_st")}">Esta semana</button>'
                    f'<button type="button" aria-pressed="{H("dt_on")}" onClick="{H("dtt")}" style="{H("dt_st")}">Todas as datas</button></span>'))
    EXTRAJS[0] = _js(EXPED_JS)
    corpo = AP.bloco('Cargas de saída', 'O que sai, de que lote, para quem, quanto pesou e o que já foi entregue. Clique numa carga para confirmar a saída com a pesagem, a entrega ou registrar devolução.',
                     g + AP.cartoes('cards_rm'))
    _shell('EXPED', 'Expedição e entregas', 'Carga de saída a partir da venda com lote reservado: pesagem, saída única do estoque, entrega e devolução.', corpo, fname, 1100,
           'A saída baixa o lote uma vez, só de lote apto e com o destino conforme (carência e LMR); repetir não baixa de novo. Devolução volta como lote em inspeção (R-C07, R-C10).')


EXPED_JS = r"""
const PR_GRIDS = { g_rm: 1 };
const _g2rows0 = g2rows; g2rows = function (self, sp) { return PR_GRIDS[sp.id] ? sp.rows : _g2rows0(self, sp); };
function comRmData(rm) { return (rm.entrega && rm.entrega.d) || (rm.saida && rm.saida.d) || rm.dprev || ''; }
/* situação e próximo passo da carga: impedimento (comImpede, a mesma da venda e da saída) e crédito do previsto, com o dono */
function comRmSit(c, rm) { const P = prP(c); const v = P.pedidos[rm.pedido] || {}; const cu = comCultura(v);
  if (rm.st === 'Cancelada') return { t: 'Cancelada', c: 'gray', nx: 'motivo: ' + ((rm.canc || {}).motivo || '') };
  if (rm.st === 'Entregue' || rm.st === 'Entregue com devolução') { const tt = comTitulos(c, t => t.rm === rm.id)[0];
    return { t: rm.st, c: COM_SITCOR[rm.st], nx: comNat(v) !== 'Venda' ? 'liquidação em produto' : (tt ? comRS(tt.valor) + (comVencido(tt) ? ' vencido em ' + prBr(tt.venc) + ' · cobrar' : ' a receber até ' + prBr(tt.venc)) : ((comCond(v.cond) || {}).ant ? 'pagamento antecipado conferido' : 'nada a receber')) }; }
  if (rm.st === 'Em trânsito') return { t: 'Em trânsito', c: 'yellow', nx: 'Confirmar entrega · Expedição', a: 'entregar' };
  const imp = []; rm.lotes.forEach(l => { const I = comImpede(c, v, P.lotes[l.lote]); I.imp.forEach(i => imp.push(Object.assign({ lote: l.lote }, i))); });
  if (imp.length) return { t: 'Programada', c: 'red', imp, nx: 'impedida: ' + imp[0].q + ' resolve (' + imp[0].lote + ')' };
  /* A5 da revisão: previsto sem reserva da venda que o cubra (reserva cancelada ou consumida por outra carga) não é "Confirmar saída" */
  const dz = comRmDescoberto(c, rm).map(d => ({ lote: d.lote, t: 'reserva do ' + v.id + ' no ' + d.lote + ' (' + comTxtV(v, d.cobre) + ') menor que o previsto da carga (' + comTxtV(v, d.prev) + '): reservar de novo ou cancelar a carga', q: comDono('vender') }));
  if (dz.length) return { t: 'Programada', c: 'red', imp: dz, nx: 'impedida: reserva menor que o previsto · ' + COM_PAPT.vender + ' (' + dz[0].lote + ')' };
  const cr = comCredito(c, v, prSoma(rm.lotes.map(l => l.prev))); if (!cr.ok) return { t: 'Programada', c: 'red', cred: cr, nx: 'impedida: crédito · Ana (gestora) aprova no ' + v.id };
  return { t: 'Programada', c: 'blue', nx: 'Confirmar saída · Expedição', a: 'sair' }; }
function comRmRow(c, rm) { const P = prP(c); const v = P.pedidos[rm.pedido] || {}; const U = x => comTxtV(v, x); const s = comRmSit(c, rm);   /* A7 da revisão: unidade da venda */
  const prev = prSoma(rm.lotes.map(l => l.prev)); const sai = rm.saida ? comRmLiq(rm) : null; const dt = comRmData(rm);
  const mod = (rm.modal === 'retira' ? 'Cliente retira' : 'Agricultor entrega') + ' · ' + (rm.hist ? 'registro da Colheita' : [rm.veic, rm.placa].filter(Boolean).join(' '));
  return { id: rm.id, ro: true, v: { rm: rm.id, ven: rm.pedido, prod: v.prod, prev, sai: sai === null ? -1 : sai, dt, sit: s.t },
    s: { rm: rm.id, ven: rm.pedido + ' ' + (v.cliente || ''), prod: v.prod + ' ' + rm.lotes.map(l => l.lote).join(' '), prev: U(prev), sai: sai === null ? '—' : U(sai), mod, dt: prBr(dt), sit: s.t + ' · ' + s.nx },
    p: { rm: [{ k: 'b', t: rm.id }], ven: [{ k: 'link', t: rm.pedido, h: 'VEN.dc.html#' + rm.pedido }, { k: 'mut', t: ' · ' + (v.cliente || '') }],
      prod: [{ k: 'txt', t: v.prod || '' }, { k: 'br' }].concat(rm.lotes.reduce((a, l, i) => a.concat((i ? [{ k: 'mut', t: ' + ' }] : []).concat([{ k: 'link', t: l.lote, h: 'PROD.dc.html#' + l.lote }])), [])),
      prev: prTx(U(prev)), sai: sai === null ? [{ k: 'mut', t: '—' }] : [{ k: 'b', t: U(sai) }].concat(rm.devs && rm.devs.length ? [{ k: 'br' }, { k: 'mut', t: 'devolvido ' + U(comRmDev(rm)) }] : []),
      mod: [{ k: 'txt', t: rm.modal === 'retira' ? 'Cliente retira' : 'Agricultor entrega' }, { k: 'br' }, { k: 'mut', t: rm.hist ? 'registro da Colheita' : [rm.transp, rm.veic, rm.placa].filter(Boolean).join(' · ') }],
      dt: [{ k: 'txt', t: prBr(dt) }], sit: [{ k: 'chip', t: s.t, c: s.c }, { k: 'br' }, { k: s.c === 'red' ? 'cn' : 'mut', c: 'red', t: s.nx }] } }; }
function comRmFaz(c, rm) { const P = prP(c); return rm.lotes.map(l => (P.lotes[l.lote] || {}).faz).filter(Boolean); }
function PREVALS(self, v) { cenOuvir(self); prTopo(self, v); const c = cenGet(); self._c = c; const P = prP(c); const hoje = prHoje();
  self.g2perfilFecha = { pr_modo: null, pr_form: null, pr_err: '' };
  self.g2pick = (gid, rid) => self.setState({ pr_sel: { g: gid, id: rid }, pr_pan: { g: gid, id: rid }, pr_form: null, pr_err: '', pr_ferr: null, pr_modo: null, pr_ch: prChave('W-RM') });
  const dq = self.state.pr_dq || 't'; const s0 = prSem(hoje);
  v.dh_on = String(dq === 'h'); v.ds_on = String(dq === 's'); v.dt_on = String(dq === 't'); v.dh_st = prPill(dq === 'h'); v.ds_st = prPill(dq === 's'); v.dt_st = prPill(dq === 't');
  v.dh = () => self.setState({ pr_dq: 'h' }); v.ds = () => self.setState({ pr_dq: 's' }); v.dtt = () => self.setState({ pr_dq: 't' });
  const f = self.state.mf_faz || 'Todas';
  const rms = Object.values(P.expedicoes || {}).filter(rm => (f === 'Todas' || comRmFaz(c, rm).indexOf(f) >= 0) && prSafOk(self, ((P.lotes[(rm.lotes[0] || {}).lote] || {}).saf) || '')
    && (dq === 't' || (dq === 'h' ? comRmData(rm) === hoje : prSem(comRmData(rm)) === s0))).sort((a, b) => b.id.localeCompare(a.id));
  GR('g_rm').rows = rms.map(rm => comRmRow(c, rm)); self._rms = rms; }
/* formulário Programar carga (§3.2): venda com reserva não programada; veículo por toque; placa; data; previsto pré-preenchido */
/* vendas com reserva ainda sem carga (as que o "Programar carga" oferece): sem nenhuma, a tela não oferece a ação */
function comVendasProg(c) { return Object.values(prP(c).pedidos).filter(x => !x.enc && !prAmb(x) && prCmp(comNaoProg(c, x.id), 0) > 0 && (x.tipo === 'pronta' || comPeriodoComecou(c, x))).sort((a, b) => a.id.localeCompare(b.id)); }
function comFormProg(self, c, vid0) { const FS = Object.assign({}, self.state.pr_form || {}); const fv = (k, d) => FS[k] !== undefined ? FS[k] : (d === undefined ? '' : String(d)); const ch0 = self.state.pr_ch;   /* valores do formulário e chave lidos no desenho: o 2º clique repete o mesmo conteúdo e a mesma chave (R-C03) */
  const P = prP(c); const hoje = prHoje();
  const vs = comVendasProg(c);
  const vid = fv('ven', vid0 || (vs.length === 1 ? vs[0].id : '')); const v = P.pedidos[vid]; const fs = [];
  fs.push(prFld(self, 'ven', 'Venda com reserva sem carga', { t: 'opts', v: vid, opts: vs.map(x => ({ v: x.id, t: x.id + ' · ' + x.cliente + ' · ' + comTxtV(x, comNaoProg(c, x.id)) })), h: vs.length ? '' : 'Nenhuma venda com reserva sem carga: reserve lote em Contratos e pedidos.' }));
  if (!v) return { fields: fs, go: () => self.setState({ pr_err: 'Escolha a venda.' }) };
  const cu = comCultura(v); const modal = v.modal || 'retira'; let transp = '';
  if (modal === 'entrega') { transp = fv('tr', ''); fs.push(prFld(self, 'tr', 'Transportador (CD-05)', { t: 'opts', v: transp, opts: comTransps().map(t => ({ v: t, t })), h: transp ? 'Frete de referência: ' + ((COMC.frete || {})[transp] || 'sem cotação registrada') + '.' : 'Agricultor organiza a entrega.' })); }
  const vcs = comVeicsPara(cu, modal === 'entrega' ? transp : ''); const veic = fv('vc', vcs.length === 1 ? vcs[0] : '');
  fs.push(prFld(self, 'vc', 'Veículo' + (modal === 'retira' ? ' do cliente' : ''), { t: 'opts', v: veic, opts: vcs.map(t => ({ v: t, t })), h: (prUn(cu).vida ? 'Fruta: só baú refrigerado.' : 'Grão: só graneleiro.') + (modal === 'retira' ? ' Frete do cliente (retira na fazenda).' : '') }));
  fs.push(prFld(self, 'pl', 'Placa', { t: 'txt', im: 'text', ph: 'ex.: QZA1B23' }));
  const dts = [{ v: hoje, t: 'Hoje ' + prBr(hoje) }, { v: prDiaMais(hoje, 1), t: 'Amanhã ' + prBr(prDiaMais(hoje, 1)) }];
  fs.push(prFld(self, 'dp', 'Data prevista', { t: 'opts', v: fv('dp', hoje), opts: dts }));
  const ls = [...new Set(prResPed(c, v.id).map(r => r.lote))].filter(l => prCmp(comNaoProg(c, v.id, l), 0) > 0); const x = comVeic(veic); let cap = x ? x.cap : null; const sug = {};
  ls.forEach(l => { const np = comNaoProg(c, v.id, l); const s0 = cap === null ? np : (prCmp(np, cap) > 0 ? cap : np); sug[l] = s0; if (cap !== null) cap = prSub(cap, s0); });
  ls.forEach(l => fs.push(prFld(self, 'pv_' + l + '_' + (veic || 'x'), 'Previsto do ' + l, { t: 'txt', u: 'kg', v: prFmtT(sug[l], 3).replace(/\./g, ''), h: 'Reserva sem carga ' + comTxtV(v, comNaoProg(c, v.id, l)) + (x ? ' · capacidade ' + prFmtT(x.cap, 0) + ' kg' : '') + ' · sugestão = ' + prFmtT(sug[l], 2) + ' kg (' + comTxtV(v, sug[l]) + '). 0 tira o lote.' })));
  const ch = ch0 || prChave('W-PG');
  const go = () => { const lotes = ls.map(l => { const t = fv('pv_' + l + '_' + (veic || 'x'), prFmtT(sug[l], 3).replace(/\./g, '')); return { lote: l, prev: t === prFmtT(sug[l], 3).replace(/\./g, '') ? sug[l] : (prNumOk(t) ? prNum(t) : t) }; });
    const r = prRun(self, y => comProgramar(y, { venda: v.id, lotes, veic, transp, placa: fv('pl', ''), dprev: fv('dp', hoje), ator: g2perfil(), chave: ch }), { pr_form: null, pr_ch: null });
    if (!r.erro && r.rm) { self.setState({ pr_sel: { g: 'g_rm', id: r.rm.id }, pr_pan: { g: 'g_rm', id: r.rm.id }, pr_ch: prChave('W-RM') }); try { history.replaceState(null, '', '#' + r.rm.id); } catch (e) {} } };
  return { fields: fs, go, v }; }
function comPanRm(self, c, rm) { const FS = Object.assign({}, self.state.pr_form || {}); const fv = (k, d) => FS[k] !== undefined ? FS[k] : (d === undefined ? '' : String(d)); const ch0 = self.state.pr_ch;   /* valores do formulário e chave lidos no desenho: o 2º clique repete o mesmo conteúdo e a mesma chave (R-C03) */
  const P = prP(c); const v = P.pedidos[rm.pedido] || {}; const cu = comCultura(v); const U = x => comTxtV(v, x); const s = comRmSit(c, rm); const md = self.state.pr_modo; const hoje = prHoje();   /* A7 da revisão: unidade da venda */
  const ch = ch0 || prChave('W-RM'); const kgT = x => prFmtT(x, 2) + ' kg';
  const lotes = rm.lotes.map(l => { const rv = prSoma(prResPed(c, v.id).filter(r => r.lote === l.lote).map(r => r.kg)); return { c: [[l.lote, 'b'], 'previsto ' + U(l.prev), 'reservado da venda ' + U(rv), rm.saida ? 'saída ' + U(l.kg) : ''].filter(Boolean), l: { t: 'Abrir lote', h: 'PROD.dc.html#' + l.lote } }; });
  const ver = []; if (rm.st === 'Programada') { rm.lotes.forEach(l => { const I = comImpede(c, v, P.lotes[l.lote]);
      I.imp.forEach(i => ver.push({ c: [[l.lote, 'b'], ['impede: ' + i.t, 'red'], 'quem resolve: ' + i.q], l: { t: 'Abrir lote', h: 'PROD.dc.html#' + l.lote } }));
      I.aval.forEach(a => ver.push({ c: [[l.lote, 'b'], [(a.lc ? a.lc + ' ' : '') + a.rot, a.st === 'conforme' || a.st === 'abertura' ? 'ok' : 'red']] }));
      if (!I.imp.length) ver.push({ c: [[l.lote, 'b'], ['apto · ' + (P.lotes[l.lote] ? prSaldos(c, P.lotes[l.lote]).q : ''), 'ok']].concat(I.aviso.length ? [I.aviso.join(' · ')] : []) }); });
    comRmDescoberto(c, rm).forEach(d => ver.push({ c: [[d.lote, 'b'], ['impede: reserva do ' + v.id + ' ' + U(d.cobre) + ' menor que o previsto ' + U(d.prev), 'red'], 'quem resolve: ' + comDono('vender')], l: { t: 'Abrir ' + v.id, h: 'VEN.dc.html#' + v.id } }));
    const cr = comCredito(c, v, prSoma(rm.lotes.map(l => l.prev))); ver.push({ c: [['Crédito', 'b'], cr.ok ? [comNat(v) !== 'Venda' ? 'liquidação em produto' : (cr.aprov ? (cr.aprov.ant ? 'pagamento antecipado conferido' : 'aprovado até ' + comRS(cr.aprov.ate) + ' por ' + cr.aprov.quem) : 'dentro do limite'), 'ok'] : [cr.prob + ' · Ana (gestora) aprova', 'red']], l: !cr.ok ? { t: 'Abrir ' + v.id, h: 'VEN.dc.html#' + v.id } : null }); }
  else if (rm.saida) (rm.saida.aval || []).forEach(a => ver.push({ c: [[a.lote, 'b'], 'avaliado na saída: ' + (a.av || []).join(' · ')].concat((a.aviso || []).length ? [a.aviso.join(' · ')] : []) }));
  const pes = rm.saida ? [{ c: rm.hist ? [['Saída histórica', 'b'], 'registrada pela Colheita (MP-1008) sem pesagem: vale o movimento de expedição'] : [['Bruto', 'b'], kgT(rm.saida.bruto), ['Tara', 'b'], kgT(rm.saida.tara), ['Líquido', 'b'], kgT(rm.saida.liq) + (prUn(cu).est ? '' : ' = ' + U(rm.saida.liq))] },
    { c: ['saída ' + prBr(rm.saida.d) + ' ' + (rm.saida.at || '') + ' · ' + rm.saida.quem].concat(rm.saida.exc ? [['excesso ' + U(rm.saida.exc.kg) + ' autorizado por ' + rm.saida.exc.quem, 'red']] : []).concat(rm.saida.cred ? ['crédito: ' + (rm.saida.cred.ant ? 'pagamento antecipado conferido' : 'aprovado por ' + rm.saida.cred.quem)] : []) }] : [];
  const ent = rm.entrega ? [{ c: [['Entrega', 'b'], prBr(rm.entrega.d) + ' ' + (rm.entrega.at || ''), rm.entrega.quem || '', rm.entrega.comp || ''].filter(Boolean) }] : [];
  const devs = (rm.devs || []).map(d => ({ c: [[d.lote, 'b'], U(d.kg) + ' de ' + d.de, d.motivo, prBr(d.d) + ' · ' + d.quem, P.lotes[d.lote] ? prSaldos(c, P.lotes[d.lote]).q : ''].filter(Boolean), l: { t: 'Abrir lote', h: 'PROD.dc.html#' + d.lote } }));
  const mv = P.movs.filter(m => m.rm === rm.id).map(m => ({ c: [[m.id, 'b'], prBr(m.d) + ' ' + (m.at || ''), m.tipo, U(m.kg), m.lote, m.quem || '', m.obs || ''].filter(Boolean) }));
  const prev = prSoma(rm.lotes.map(l => l.prev));
  const PPx = { title: rm.id + ' · ' + rm.pedido + ' · ' + (v.cliente || ''), chip: [s.t, s.c], sub: (COM_MODAL[rm.modal] || '') + (rm.local ? ' · ' + rm.local : '') + (rm.hist ? '' : ' · ' + [rm.veic, rm.placa].filter(Boolean).join(' ')),
    next: s.imp ? 'Saída impedida: ' + s.imp[0].t + '. Quem resolve: ' + s.imp[0].q + '.' : (s.cred ? 'Saída impedida no crédito: ' + s.cred.prob + '. ' + (s.cred.ant ? 'Ana (gestora) confere o pagamento' : 'Ana (gestora) aprova o crédito') + ' no ' + v.id + '.' : (s.a === 'sair' ? 'Pese o caminhão e confirme a saída: baixa o lote uma vez, só o reservado do ' + v.id + '.' : (s.a === 'entregar' ? 'Confirme a entrega quando o cliente receber (data e devolução, se houver).' : s.nx + '.'))),
    nred: s.c === 'red',
    kv: [{ l: 'Venda', v: rm.pedido + ' · ' + (v.cliente || '') }, { l: 'Produto', v: v.prod || '' }, { l: 'Destino', v: PRDC.dest[v.dest || 'MI-BR'] || v.dest }, { l: 'Modalidade', v: COM_MODAL[rm.modal] || '' },
      { l: 'Transportador', v: rm.transp || '—' }, { l: 'Veículo · placa', v: [rm.veic, rm.placa].filter(Boolean).join(' · ') || '—' }, { l: 'Data prevista', v: prBr(rm.dprev) }, { l: 'Previsto', v: U(prev) },
      { l: 'Saída', v: rm.saida ? U(rm.saida.liq) : '—' }, { l: 'Recibo (chave)', v: rm.saida ? rm.saida.chave : rm.chave }],
    secs: [{ t: 'Lotes', rows: lotes }, { t: rm.st === 'Programada' ? 'Verificação da saída (ao vivo)' : 'Avaliação gravada na saída', rows: ver, vazio: '—' }, { t: 'Pesagem', rows: pes, vazio: 'Pesagem na saída.' },
      { t: 'Entrega', rows: ent, vazio: rm.modal === 'retira' ? 'Cliente retira: a saída é a entrega.' : 'Entrega a confirmar.' }, { t: 'Devoluções', rows: devs, vazio: 'Nenhuma devolução.' }, { t: 'Movimentos', rows: mv, vazio: 'Nenhum movimento.' }],
    err: self.state.pr_err };
  if (md === 'cancelar') { PPx.form = { t: 'Cancelar ' + rm.id, h: 'As reservas do ' + rm.pedido + ' continuam; nada sai do estoque.', fields: [prFld(self, 'mot', 'Motivo', { t: 'txt', im: 'text', ph: 'ex.: caminhão não veio' })] };
    PPx.prim = { t: 'Cancelar carga', go: () => prRun(self, x => comCancelarCarga(x, { rm: rm.id, motivo: fv('mot', ''), ator: g2perfil(), chave: ch }), { pr_modo: null, pr_form: null }) };
    PPx.sec = [{ t: 'Manter carga', go: () => self.setState({ pr_modo: null, pr_err: '' }) }]; return PPx; }
  if (md === 'devolver') { const fs = []; if (rm.lotes.length > 1) fs.push(prFld(self, 'dl', 'Lote', { t: 'opts', v: fv('dl', rm.lotes[0].lote), opts: rm.lotes.map(l => ({ v: l.lote, t: l.lote })) }));
    fs.push(prFld(self, 'dq', 'Quantidade devolvida', { t: 'txt', u: comUnV(v) })); fs.push(prFld(self, 'dm', 'Motivo', { t: 'opts', opts: COMC.motivos.map(t => ({ v: t, t })) }));
    PPx.form = { t: 'Registrar devolução · ' + COM_PAPT.saida, h: 'Volta como lote novo Em inspeção; só a Qualidade libera. O entregue e o a receber caem.', fields: fs };
    PPx.prim = { t: 'Registrar devolução', go: () => prRun(self, x => comDevolver(x, { rm: rm.id, lote: fv('dl', rm.lotes[0].lote), kg: prNumOk(fv('dq', '')) ? comBaseV(v, prNum(fv('dq', ''))) : fv('dq', ''), motivo: fv('dm', ''), ator: g2perfil(), chave: ch }), { pr_modo: null, pr_form: null }) };
    PPx.sec = [{ t: 'Voltar', go: () => self.setState({ pr_modo: null, pr_err: '' }) }]; return PPx; }
  if (s.a === 'sair' && comPode('saida')) { const fs = [prFld(self, 'br', 'Peso bruto', { t: 'txt', u: 'kg' }), prFld(self, 'ta', 'Tara', { t: 'txt', u: 'kg' })];
    const b = fv('br', ''), t = fv('ta', ''); let liq = null; if (prNumOk(b) && prNumOk(t)) liq = prSub(prNum(b), prNum(t));
    if (rm.lotes.length > 1) rm.lotes.forEach(l => fs.push(prFld(self, 'kl_' + l.lote, 'kg do ' + l.lote, { t: 'txt', u: 'kg', v: prFmtT(l.prev, 3).replace(/\./g, ''), h: 'A soma dos lotes é o líquido.' })));
    const h = []; if (liq !== null && prCmp(liq, 0) > 0) { h.push('Líquido ' + kgT(liq) + (prUn(cu).est ? '' : ' = ' + U(liq)) + '.');
      const kl = rm.lotes.length === 1 ? [{ lote: rm.lotes[0].lote, kg: liq }] : rm.lotes.map(l => ({ lote: l.lote, kg: prNum(fv('kl_' + l.lote, prFmtT(l.prev, 3).replace(/\./g, ''))) || 0 }));
      kl.forEach(x => { const rv = prSoma(prResPed(c, v.id).filter(r => r.lote === x.lote).map(r => r.kg)); if (prCmp(x.kg, rv) > 0) h.push('Excesso de ' + U(prSub(x.kg, rv)) + ' sobre a reserva no ' + x.lote + ': sai do disponível do lote com ' + g2quem('gestor') + ' (ajuste autorizado).'); });
      /* A5 da revisão: peso acima do previsto consome a reserva prevista de outra carga da mesma venda: avisa antes de gravar */
      const pv0 = prSoma(rm.lotes.map(l => l.prev)); const oc = comRmsVenda(c, v.id).filter(r => r.st === 'Programada' && r.id !== rm.id).map(r => r.id);
      if (prCmp(liq, pv0) > 0) h.push('Líquido ' + U(prSub(liq, pv0)) + ' acima do previsto (' + U(pv0) + ')' + (oc.length ? ': a diferença sai da reserva prevista para a ' + oc.join(', ') + ', que fica sem cobertura.' : '.'));
      const cr = comCredito(c, v, liq); if (!cr.ok) { h.push('Crédito: ' + cr.prob + ' · decisão de ' + g2quem('gestor') + '.');
        /* A9 da revisão: a chave da aprovação leva o peso (outro peso = outra aprovação; o mesmo, repetido, não grava de novo) */
        if (comPode('credito')) PPx.sec = [{ t: 'Aprovar crédito desta saída', go: () => prRun(self, x => comAprovarCredito(x, { venda: v.id, kg: liq, ator: g2perfil(), chave: ch + '-CR-' + prM(liq).toString() }), {}) }]; } }
    PPx.form = { t: 'Confirmar saída da ' + rm.id + ' · ' + COM_PAPT.saida, h: 'Bruto e tara da balança em kg, sem valor anterior. ' + (h.length ? h.join(' ') : 'O líquido sai do ' + rm.lotes.map(l => l.lote).join(' + ') + ' uma única vez.'), fields: fs };
    const kgs = () => { if (rm.lotes.length < 2) return null; const o = {}; rm.lotes.forEach(l => { o[l.lote] = fv('kl_' + l.lote, prFmtT(l.prev, 3).replace(/\./g, '')); }); return o; };
    PPx.prim = { t: 'Confirmar saída da ' + rm.id, go: () => prRun(self, x => comSair(x, { rm: rm.id, bruto: fv('br', ''), tara: fv('ta', ''), kgs: kgs(), ator: g2perfil(), chave: ch }), { pr_form: null, pr_ch: prChave('W-RM') }) }; }
  else if (s.a === 'entregar' && comPode('saida')) { const dts = [{ v: hoje, t: 'Hoje ' + prBr(hoje) }, { v: prDiaMais(hoje, -1), t: 'Ontem ' + prBr(prDiaMais(hoje, -1)) }].filter(x => x.v >= rm.saida.d && x.v <= hoje);
    /* A1 da revisão: entrega não tem desfazer e conta o vencimento; data e "Recebido" são escolhidos por quem confirma (um toque cada), nunca padrão */
    const rc = fv('rc', ''); const dv = rc === 'dev'; const fs = [prFld(self, 'de', 'Data da entrega', { t: 'opts', v: fv('de', ''), opts: dts }),
      prFld(self, 'rc', 'Recebido', { t: 'opts', v: rc, opts: [{ v: 'tudo', t: 'Recebido tudo' }, { v: 'dev', t: 'Com devolução' }] })];
    if (dv) { if (rm.lotes.length > 1) fs.push(prFld(self, 'dl', 'Lote', { t: 'opts', v: fv('dl', rm.lotes[0].lote), opts: rm.lotes.map(l => ({ v: l.lote, t: l.lote })) }));
      fs.push(prFld(self, 'dq', 'Quantidade devolvida', { t: 'txt', u: comUnV(v) })); fs.push(prFld(self, 'dm', 'Motivo', { t: 'opts', opts: COMC.motivos.map(t => ({ v: t, t })) })); }
    fs.push(prFld(self, 'cp', 'Comprovante (opcional)', { t: 'txt', im: 'text', ph: 'ex.: canhoto assinado' }));
    PPx.form = { t: 'Confirmar entrega da ' + rm.id + ' · ' + COM_PAPT.saida, h: 'O vencimento conta da data da entrega (' + ((comCond(v.cond) || {}).ev || '') + '). Devolução volta como lote em inspeção.', fields: fs };
    PPx.prim = { t: 'Confirmar entrega da ' + rm.id, go: () => { if (!rc) { self.setState({ pr_err: 'Escolha "Recebido tudo" ou "Com devolução".' }); return; } prRun(self, x => comEntregar(x, { rm: rm.id, d: fv('de', ''), comp: fv('cp', ''), ator: g2perfil(), chave: ch,
      dev: dv ? { lote: fv('dl', rm.lotes[0].lote), kg: prNumOk(fv('dq', '')) ? comBaseV(v, prNum(fv('dq', ''))) : fv('dq', ''), motivo: fv('dm', '') } : null }), { pr_form: null, pr_ch: prChave('W-RM') }); } }; }
  if (rm.st === 'Programada' && comPode('carga') && !PPx.sec) PPx.sec = [{ t: 'Cancelar carga', go: () => self.setState({ pr_modo: 'cancelar', pr_form: null, pr_err: '' }) }];
  if ((rm.st === 'Entregue' || rm.st === 'Entregue com devolução') && comPode('saida') && prCmp(comRmLiq(rm), 0) > 0) PPx.sec = [{ t: 'Registrar devolução', go: () => self.setState({ pr_modo: 'devolver', pr_form: null, pr_err: '' }) }];
  return PPx; }
function EXTRAVALS(self, v) { prRst(self, v); const c = self._c || cenGet(); const P = prP(c); const st = self.state;
  v.cards_rm = prCards(self, v, 'g_rm', id => { const rm = (P.expedicoes || {})[id]; if (!rm) return null; const x = P.pedidos[rm.pedido] || {}; const cu = comCultura(x); const s = comRmSit(c, rm);
    return prCard({ t1: rm.id + ' · ' + rm.pedido + ' · ' + (x.cliente || ''), num: rm.saida ? comTxtV(x, comRmLiq(rm)) : 'previsto ' + comTxtV(x, prSoma(rm.lotes.map(l => l.prev))), t2: (x.prod || '') + ' · ' + rm.lotes.map(l => l.lote).join(' + ') + ' · ' + prBr(comRmData(rm)), chip: [s.t, s.c], nx: s.nx, go: () => self.g2pick('g_rm', id) }); });
  const sel = st.pr_sel; const rm = sel && (P.expedicoes || {})[sel.id]; let prim = null;
  if (rm) { const s = comRmSit(c, rm);
    if (s.a === 'sair') prim = { t: 'Confirmar saída da ' + rm.id, papel: 'saida', go: () => self.setState({ pr_pan: { g: 'g_rm', id: rm.id }, pr_form: null, pr_err: '', pr_modo: null }) };
    else if (s.a === 'entregar') prim = { t: 'Confirmar entrega da ' + rm.id, papel: 'saida', go: () => self.setState({ pr_pan: { g: 'g_rm', id: rm.id }, pr_form: null, pr_err: '', pr_modo: null }) }; }
  else if (comVendasProg(c).length) prim = { t: 'Programar carga', papel: 'carga', go: () => self.setState({ pr_pan: { g: 'nova' }, pr_sel: null, pr_form: null, pr_err: '', pr_modo: null, pr_ch: prChave('W-PG') }) };
  const rms = self._rms || []; const sits = rms.map(x => comRmSit(c, x)); const np = sits.filter(x => x.t === 'Programada').length, nt = sits.filter(x => x.t === 'Em trânsito').length, ni = sits.filter(x => x.c === 'red').length;
  prStatus(v, [np ? np + (np > 1 ? ' programadas' : ' programada') : (comVendasProg(c).length ? 'nada programado' : 'nada a programar: reserve lote em Contratos e pedidos'), nt ? nt + ' em trânsito' : '', ni ? ni + (ni > 1 ? ' impedidas' : ' impedida') : ''].filter(Boolean).join(' · '), ni ? 'red' : (np || nt ? 'yellow' : 'green'));
  const pan = st.pr_pan; let PP = null;
  if (pan && pan.g === 'nova') { const f = comFormProg(self, c, pan.ven);
    PP = { title: 'Programar carga', chip: ['Nova carga', 'gray'], sub: f.v ? f.v.id + ' · ' + f.v.cliente + ' · ' + (COM_MODAL[f.v.modal] || '') + (f.v.local ? ' · ' + f.v.local : '') : 'Venda com lote reservado',
      form: { t: 'Programar carga · ' + COM_PAPT.carga, h: 'Toque nas opções; digite só a placa. Previsto pré-preenchido: o menor entre a reserva sem carga e a capacidade do veículo.', fields: f.fields }, err: st.pr_err, prim: comPode('carga') ? { t: 'Programar carga', go: f.go } : null }; }
  else if (pan && (P.expedicoes || {})[pan.id]) PP = comPanRm(self, c, P.expedicoes[pan.id]);
  comPrimPainel(v, prim, PP); prPainel(self, v, PP); }
/* entrada por link: EXPED.dc.html#RM-0002 abre a carga; #nova:PV-030 abre "Programar carga" com a venda herdada */
function comHashRm(self) { if (self.__ch) return; self.__ch = 1; const ab = () => { let h = ''; try { h = decodeURIComponent(location.hash || '').slice(1); } catch (e) {} const P = prP(cenGet());
  if ((P.expedicoes || {})[h]) { setTimeout(() => self.g2pick('g_rm', h), 0); return; }
  const m = /^nova:(.+)$/.exec(h); if (m && P.pedidos[m[1]]) setTimeout(() => self.setState({ pr_pan: { g: 'nova', ven: m[1] }, pr_sel: null, pr_form: null, pr_err: '', pr_modo: null, pr_ch: prChave('W-PG') }), 0); };
  ab(); try { window.addEventListener('hashchange', ab); } catch (e) {} }
const _EXV = EXTRAVALS; EXTRAVALS = function (self, v) { comHashRm(self); _EXV(self, v); };
"""


# =====================================================================================================================
# PCOM · Painel comercial
# =====================================================================================================================
def pcom():
    fname = 'PCOM.dc.html'; E._reset_screen(fname)
    g_of = grid([dict(k='per', l='Produto › período', w=230), dict(k='of', l='Oferta', t='num', a='r', w=150), dict(k='comp', l='Compromissos', t='num', a='r', w=140),
                 dict(k='cob', l='Coberto por lote', t='num', a='r', w=140), dict(k='livre', l='Livre para vender', t='num', a='r', w=160), dict(k='sit', l='Situação', w=200)],
                [], edit=dict(m='pick'), tree=True, gid='g_of', total=False, qf=dict(k='sit', cut=' · ', l='Situação', todas='Todas'),
                tools=(f'<span role="group" aria-label="Horizonte" style="display: inline-flex; gap: 6px;"><button type="button" aria-pressed="{H("hz4_on")}" onClick="{H("hz4")}" style="{H("hz4_st")}">4 semanas</button>'
                       f'<button type="button" aria-pressed="{H("hzs_on")}" onClick="{H("hzs")}" style="{H("hzs_st")}">Safra</button></span>'))
    g_pr = grid([dict(k='prod', l='Produto', w=200), dict(k='vend', l='Vendido', t='num', a='r'), dict(k='medc', l='Preço médio contratado', t='num', a='r', w=170),
                 dict(k='ent', l='Entregue', t='num', a='r'), dict(k='medr', l='Preço médio realizado', t='num', a='r', w=170), dict(k='ref', l='Referência de mercado', w=190),
                 dict(k='arec', l='A receber', t='num', a='r', w=140), dict(k='venc', l='Vencido', t='num', a='r', w=130)],
                [], edit=dict(m='pick'), gid='g_pr', total=False)
    EXTRAJS[0] = _js(PCOM_JS)
    kpi = lambda l, k, n: (f'<div style="flex: 1 1 160px; min-width: 0; padding: 12px 16px; background: #FFFFFF; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; gap: 4px;">'
                           f'<div style="font-size: 11px; letter-spacing: .06em; text-transform: uppercase; color: {MUTED}; font-weight: 800;">{l}</div>'
                           f'<div style="font-size: 22px; font-weight: 800; letter-spacing: -.01em;">{H(k)}</div><div style="font-size: 12px; color: {MUTED};">{H(n)}</div></div>')
    ind = (f'<div role="group" aria-label="Indicadores" style="display: flex; flex-wrap: wrap; gap: 10px;">' + kpi('A receber (a vencer)', 'k_ar', 'k_arn') + kpi('Vencido (cobrar)', 'k_vn', 'k_vnn')
           + kpi('Entregue nos últimos 30 dias', 'k_en', 'k_enn') + '</div>')
    corpo = (ind + AP.bloco('Oferta e compromissos', 'Produto › período: oferta (estoque apto ou previsão publicada) × compromissos (vendas) × livre para vender. Negativo é déficit. Soma de todas as fazendas: a venda é da empresa (D-C22).',
                            g_of + AP.cartoes('cards_of'))
             + AP.bloco('Preço e recebimento', 'Médias ponderadas (Σ valor ÷ Σ quantidade), só venda; CPR e barter liquidam em produto, à parte. Recebimento é do Financeiro: o a receber não baixa nesta etapa.',
                        g_pr + AP.cartoes('cards_pr')))
    _shell('PCOM', 'Painel comercial', 'Quanto ainda posso vender de cada produto em cada período, quanto está comprometido, a que preço vendi e quanto vou receber.', corpo, fname, 1250,
           'Números lidos do estado (estoque, previsão publicada, vendas e cargas): nada digitado aqui. Período em curso entra pelo estoque; previsão publicada só para período futuro (PRD 49.2).')


PCOM_JS = r"""
const PR_GRIDS = { g_of: 1, g_pr: 1 };
const _g2rows0 = g2rows; g2rows = function (self, sp) { return PR_GRIDS[sp.id] ? sp.rows : _g2rows0(self, sp); };
const COM_SITC = { 'Livre': 'green', 'Sem saldo livre': 'gray', 'Déficit': 'red', 'Suspenso': 'yellow' };
function comLivreTem(r) { return r.livre !== null && prCmp(r.livre, 0) > 0; }   /* A-17: livre suspenso (null) não é zero nem positivo */
function comSusp(r) { return 'saca a conferir: ' + (r.amb || []).join(', '); }
function comOfRow(r) { const U = x => comTxt(r.cu, x, r.tipo === 'saf' ? 0 : 2);
  const of = r.tipo === 'est' ? (r.colh ? U(r.apto) + ' apto + ' + U(r.colh.rest) + ' a colher' : U(r.oferta) + ' apto') : (r.tem ? U(r.oferta) + ' publicada' : 'sem versão publicada');   /* A10 da revisão: safra em colheita */
  const sit = r.sit + (r.tipo === 'est' && prCmp(r.vencApto, 0) > 0 ? ' · vencido ' + U(r.vencApto) + ' (aviso)' : '');
  const su = r.livre === null;
  return { id: r.id, ro: true, v: { per: r.perT, of: r.oferta, comp: r.comp, cob: r.cob, livre: su ? -1e12 : r.livre, sit: r.sit },
    s: { per: r.prod + ' ' + r.perT, of, comp: U(r.comp) + (su ? ' + ' + comSusp(r) : ''), cob: U(r.cob), livre: su ? 'suspenso' : U(r.livre), sit },
    p: { per: [{ k: 'txt', t: r.perT }], of: [{ k: r.tipo !== 'est' && !r.tem ? 'mut' : 'txt', t: of }].concat(r.tipo === 'est' && prCmp(r.vencApto, 0) > 0 ? [{ k: 'br' }, { k: 'cn', c: 'red', t: 'vencido ' + U(r.vencApto) + ' · aviso' }] : []),
      comp: [{ k: 'txt', t: U(r.comp) + (su ? ' + saca a conferir' : '') }].concat(r.vendas.length ? [{ k: 'br' }, { k: 'mut', t: r.vendas.join(', ') }] : []), cob: prTx(U(r.cob)),
      livre: su ? [{ k: 'chip', t: 'suspenso', c: 'yellow' }, { k: 'br' }, { k: 'mut', t: comSusp(r) }] : prCmp(r.livre, 0) < 0 ? [{ k: 'chip', t: 'déficit ' + U(prSub(0, r.livre)), c: 'red' }] : [{ k: 'b', t: U(r.livre) }], sit: [{ k: 'chip', t: r.sit, c: COM_SITC[r.sit] }] } }; }
function comPrRow(x) { const U = y => comTxt(x.cu, y); const R = y => y === null ? '—' : comPrecoTxt(x.cu, y);
  return { id: 'p:' + x.prod, ro: true, v: { prod: x.prod, vend: x.vend, medc: x.medC === null ? -1 : x.medC, ent: x.ent, medr: x.medR === null ? -1 : x.medR, arec: x.aRec, venc: x.venc },
    s: { prod: x.prod, vend: U(x.vend), medc: R(x.medC), ent: U(x.ent), medr: R(x.medR), ref: x.ref ? comPrecoTxt(x.cu, x.ref.p) : 'sem cotação', arec: comRS(x.aRec), venc: comRS(x.venc) },
    p: { prod: [{ k: 'b', t: x.prod }].concat(x.liq.length ? [{ k: 'br' }, { k: 'mut', t: 'à parte: ' + x.liq.join(', ') + ' (liquidação em produto)' }] : []).concat((x.amb || []).length ? [{ k: 'br' }, { k: 'cn', c: 'red', t: 'fora da média: ' + x.amb.join(', ') + ' (saca a conferir)' }] : []), vend: prTx(U(x.vend)), medc: [{ k: 'b', t: R(x.medC) }], ent: prTx(U(x.ent)), medr: [{ k: 'b', t: R(x.medR) }],
      ref: x.ref ? [{ k: 'txt', t: comPrecoTxt(x.cu, x.ref.p) }, { k: 'br' }, { k: 'mut', t: x.ref.fonte }] : [{ k: 'mut', t: 'sem cotação (ausente ≠ zero)' }], arec: prTx(comRS(x.aRec)), venc: prCmp(x.venc, 0) > 0 ? [{ k: 'chip', t: comRS(x.venc), c: 'red' }] : prTx(comRS(x.venc)) } }; }
function PREVALS(self, v) { cenOuvir(self); prTopo(self, v); const c = cenGet(); self._c = c; const hz = self.state.pr_hz || '4';
  self.g2pick = (gid, rid) => { if (String(rid).indexOf('grp:') === 0) return; self.setState({ pr_sel: { g: gid, id: rid }, pr_pan: { g: gid, id: rid }, pr_form: null, pr_err: '' }); };
  v.hz4_on = String(hz === '4'); v.hzs_on = String(hz === 's'); v.hz4_st = prPill(hz === '4'); v.hzs_st = prPill(hz === 's'); v.hz4 = () => self.setState({ pr_hz: '4' }); v.hzs = () => self.setState({ pr_hz: 's' });
  const rows = comPainel(c, prHoje(), hz); self._of = rows; const por = {}; rows.forEach(r => { (por[r.prod] = por[r.prod] || []).push(r); });
  GR('g_of').rows = Object.keys(por).sort().map(pr => { const rs = por[pr]; const def = rs.filter(r => r.sit === 'Déficit').length; const sus = rs.filter(r => r.sit === 'Suspenso').length;
    const gt = [def ? def + (def > 1 ? ' períodos em déficit' : ' período em déficit') : '', sus ? sus + (sus > 1 ? ' suspensos (saca a conferir)' : ' suspenso (saca a conferir)') : ''].filter(Boolean).join(' · ');
    return { id: 'grp:' + pr, ro: true, v: { per: pr, sit: def ? 'Déficit' : (sus ? 'Suspenso' : 'Livre') }, s: { per: pr, sit: '' },   /* o resumo do grupo não vira chip do filtro rápido */
      p: { per: [{ k: 'b', t: pr }], of: [{ k: 'mut', t: '' }], comp: [{ k: 'mut', t: '' }], cob: [{ k: 'mut', t: '' }], livre: [{ k: 'mut', t: '' }], sit: [{ k: 'mut', t: gt }] },
      kids: rs.map(comOfRow) }; });
  const x0 = {}; Object.keys(por).forEach(pr => { x0['grp:' + pr] = true; }); GR('g_of').x0 = x0;
  const pz = comPrecos(c); self._pz = pz; GR('g_pr').rows = pz.map(comPrRow);
  const ind = comIndicadores(c); v.k_ar = comRS(ind.aRec); v.k_vn = comRS(ind.venc); v.k_en = comRS(ind.ent30);
  const tt = comTitulos(c); const prox = tt.filter(t => !comVencido(t) && t.venc)[0]; v.k_arn = prox ? 'próximo: ' + prox.cliente + ' ' + comRS(prox.valor) + ' em ' + prBr(prox.venc) : 'nada a vencer';
  const vn = tt.filter(t => comVencido(t)); v.k_vnn = vn.length ? vn.length + (vn.length > 1 ? ' títulos' : ' título') + ' · cobrar' : 'nada vencido'; v.k_enn = 'saídas de venda desde ' + prBr(prDiaMais(prHoje(), -30)); }
function comPanOf(self, c, r) { const P = prP(c); const U = x => comTxt(r.cu, x);
  const vs = r.vendas.map(id => P.pedidos[id]).filter(Boolean).map(v => ({ c: [[v.id, 'b'], v.cliente, comVendaTipo(v).toLowerCase() + ' · ' + (v.janela || ''), 'saldo ' + (prAmb(v) ? 'saca a conferir' : comTxtV(v, prSaldoFut(c, v))), comNatTxt(v)], l: { t: 'Abrir venda', h: 'VEN.dc.html#' + v.id } }));
  const ls = r.tipo === 'est' ? Object.values(P.lotes).filter(L => L.prod === r.prod && (r.per === 'est:' || 'est:' + (L.saf || '') === r.per)).map(L => ({ L, S: prSaldos(c, L) })).filter(x => !x.S.esgotado)
    .map(x => ({ c: [[x.L.id, 'b'], x.S.q, 'apto ' + U(x.S.apto), 'reservado ' + U(x.S.res), 'disponível ' + U(x.S.disp), x.L.validade ? (x.L.validade < prHoje() ? ['vencido ' + prBr(x.L.validade), 'red'] : 'vence ' + prBr(x.L.validade)) : '', x.L.faz].filter(Boolean), l: { t: 'Abrir lote', h: 'PROD.dc.html#' + x.L.id } })) : [];
  const conta = r.livre === null ? 'Livre suspenso: ' + r.amb.join(', ') + ' com a saca do contrato a conferir (' + 'VE-05 oculto diz sc 50 kg; a Colheita contou 60 kg). Registre a massa com a fonte em Contratos e pedidos; nenhuma conversão é feita sem esse registro.'
    : r.tipo === 'est' && r.colh ? 'Safra em colheita: oferta = apto ' + U(r.apto) + ' + previsão ainda não colhida ' + U(r.colh.rest) + ' (publicada ' + U(r.colh.pub) + ' − colhido ' + U(r.colh.col) + '). Livre = ' + U(r.oferta) + ' − compromissos ' + U(r.comp) + (prCmp(r.dispVenc, 0) > 0 ? ' − disponível vencido ' + U(r.dispVenc) : '') + ' = ' + U(r.livre) + '. Fechada a colheita, vale só o colhido.'
    : r.tipo === 'est' ? 'Livre = oferta apta ' + U(r.oferta) + ' − compromissos ' + U(r.comp) + (prCmp(r.dispVenc, 0) > 0 ? ' − disponível vencido ' + U(r.dispVenc) : '') + ' = ' + U(r.livre) + '.'
    : 'Livre = ' + (r.tem ? 'previsão publicada ' + U(r.oferta) : 'sem versão publicada (0)') + ' − (vendas futuras ' + U(r.comp) + ' − já cobertas por lote ' + U(r.cob) + ') = ' + U(r.livre) + '.';
  /* próximo passo com verbo e dono quando falta produto (o déficit é aviso, D-C16: nada trava) */
  const passo = r.sit !== 'Déficit' ? '' : r.tipo === 'est' ? ' Para cobrir: liberar ou colher lote apto (Estoque de produto · Qualidade) ou encerrar o saldo das vendas abaixo (Contratos e pedidos · Comercial).'
    : !r.tem ? ' Para cobrir: publicar a previsão de ' + r.perT + ' (Previsão e colheita · Produção) ou renegociar as vendas abaixo (Contratos e pedidos · Comercial).'
    : ' Para cobrir: rever a previsão publicada (Previsão e colheita · Produção) ou renegociar as vendas abaixo (Contratos e pedidos · Comercial).';
  return { title: r.prod + ' › ' + r.perT, chip: [r.sit, COM_SITC[r.sit]], sub: r.tipo === 'est' ? (r.colh ? 'Estoque apto de todas as fazendas + previsão publicada ainda não colhida' : 'Estoque apto de todas as fazendas; período em curso entra aqui') : 'Período futuro: previsão publicada × vendas futuras',
    next: conta + passo, nred: r.sit === 'Déficit' || r.sit === 'Suspenso', kv: [{ l: 'Oferta', v: r.tipo === 'est' || r.tem ? U(r.oferta) : 'sem versão publicada' }, { l: 'Compromissos', v: U(r.comp) }, { l: 'Coberto por lote', v: U(r.cob) }, { l: 'Livre para vender', v: r.livre === null ? 'suspenso (' + comSusp(r) + ')' : U(r.livre) }],
    secs: [{ t: 'Vendas do período', rows: vs, vazio: 'Nenhuma venda.' }].concat(r.tipo === 'est' ? [{ t: 'Lotes', rows: ls, vazio: 'Nenhum lote com saldo.' }] : []),
    prim: r.livre === null && comPode('vender') ? { t: 'Registrar a saca do ' + r.amb[0], h: 'VEN.dc.html#' + r.amb[0] } : comLivreTem(r) && comPode('vender') ? { t: 'Vender ' + r.prod + ' · ' + r.perT, h: 'VEN.dc.html#nova:' + r.prod + ':' + r.per } : null }; }
function comPanPr(self, c, x) { const U = y => comTxt(x.cu, y); const P = prP(c);
  const tt = x.tit.map(t => ({ c: [[t.rm, 'b'], t.cliente, U(t.kg), comRS(t.valor), t.venc ? (comVencido(t) ? ['vencido em ' + prBr(t.venc), 'red'] : 'vence ' + prBr(t.venc)) : 'vence após a entrega'], l: { t: 'Abrir carga', h: 'EXPED.dc.html#' + t.rm } }));
  const vs = x.vendas.concat(x.liq).map(id => P.pedidos[id]).map(v => ({ c: [[v.id, 'b'], v.cliente, comNatTxt(v), comQtdTxt(v), comPrecoTxtV(v) + (comNat(v) !== 'Venda' ? ' equivalente' : ''), 'entregue ' + comTxtV(v, prExpedido(c, v.id))], l: { t: 'Abrir venda', h: 'VEN.dc.html#' + v.id } }));
  return { title: x.prod, chip: [prCmp(x.venc, 0) > 0 ? 'Vencido a cobrar' : 'Em dia', prCmp(x.venc, 0) > 0 ? 'red' : 'green'], sub: 'Preço e recebimento · médias ponderadas, só venda',
    next: 'A receber ' + comRS(x.aRec) + (prCmp(x.venc, 0) > 0 ? ' · vencido ' + comRS(x.venc) + ': cobrar (Financeiro)' : '') + '. Recebimento e baixa são do Financeiro (fora desta etapa).',
    kv: [{ l: 'Vendido', v: U(x.vend) }, { l: 'Preço médio contratado', v: x.medC === null ? '—' : comPrecoTxt(x.cu, x.medC) }, { l: 'Entregue', v: U(x.ent) }, { l: 'Preço médio realizado', v: x.medR === null ? '—' : comPrecoTxt(x.cu, x.medR) },
      { l: 'Referência de mercado', v: x.ref ? comPrecoTxt(x.cu, x.ref.p) + ' · ' + x.ref.fonte : 'sem cotação' }, { l: 'A receber · vencido', v: comRS(x.aRec) + ' · ' + comRS(x.venc) }],
    secs: [{ t: 'Entregas a receber', rows: tt, vazio: 'Nada a receber.' }, { t: 'Vendas (CPR e barter: liquidação em produto, GE-08)', rows: vs }] }; }
function EXTRAVALS(self, v) { prRst(self, v); const c = self._c || cenGet(); const st = self.state; const rows = self._of || []; const pz = self._pz || [];
  v.cards_of = prCards(self, v, 'g_of', id => { if (String(id).indexOf('grp:') === 0) return prCard({ grp: true, t1: id.slice(4), num: '' }); const r = rows.find(x => x.id === id); if (!r) return null; const U = x => comTxt(r.cu, x, r.tipo === 'saf' ? 0 : 2);
    return prCard({ t1: r.perT, num: (r.livre === null ? 'livre suspenso' : (prCmp(r.livre, 0) < 0 ? 'déficit ' + U(prSub(0, r.livre)) : U(r.livre) + ' livre')), t2: 'Oferta ' + (r.tipo === 'est' || r.tem ? U(r.oferta) : 'sem versão publicada') + ' · compromissos ' + U(r.comp) + ' · coberto ' + U(r.cob), chip: [r.sit, COM_SITC[r.sit]], nx: '', go: () => self.g2pick('g_of', id) }); });
  v.cards_pr = prCards(self, v, 'g_pr', id => { const x = pz.find(y => 'p:' + y.prod === id); if (!x) return null;
    return prCard({ t1: x.prod, num: comRS(x.aRec) + ' a receber', t2: 'Contratado ' + (x.medC === null ? '—' : comPrecoTxt(x.cu, x.medC)) + ' · realizado ' + (x.medR === null ? '—' : comPrecoTxt(x.cu, x.medR)) + ' · vencido ' + comRS(x.venc), chip: [prCmp(x.venc, 0) > 0 ? 'Vencido' : 'Em dia', prCmp(x.venc, 0) > 0 ? 'red' : 'green'], nx: '', go: () => self.g2pick('g_pr', id) }); });
  /* primária: da linha selecionada; sem seleção, a 1ª linha com livre > 0 */
  const sel = st.pr_sel; let r = sel && sel.g === 'g_of' ? rows.find(x => x.id === sel.id) : null; let prim = null;
  if (!r && !(sel && sel.g === 'g_pr')) r = rows.find(comLivreTem) || rows.find(x => x.livre === null) || null;
  /* A-17: período suspenso → o passo que destrava é registrar a saca da 1ª venda sem a massa (na venda, com a fonte) */
  if (r && r.livre === null) prim = { t: 'Registrar a saca do ' + r.amb[0], papel: 'vender', h: 'VEN.dc.html#' + r.amb[0] };
  /* linha em déficit ou sem saldo livre: nenhuma primária (BOT-03/BOT-08 do design system de 09/10: "Ver …" e troca de tela não são
     primária); o painel da linha, aberto pela seleção, diz o passo que cobre o déficit e lista as vendas com o elo para cada uma */
  else if (r && comLivreTem(r)) prim = { t: 'Vender ' + r.prod + ' · ' + r.perT, papel: 'vender', h: 'VEN.dc.html#nova:' + r.prod + ':' + r.per };
  const def = rows.filter(x => x.sit === 'Déficit'); const sus = rows.filter(x => x.sit === 'Suspenso'); const ind = comIndicadores(c);
  prStatus(v, [def.length ? def.map(x => x.prod.split(' ')[0] + ' ' + x.perT.replace(/ \(.*\)$/, '')).join(', ') + ' em déficit' : 'sem déficit', sus.length ? sus.length + (sus.length > 1 ? ' períodos suspensos' : ' período suspenso') + ' (saca a conferir)' : '', prCmp(ind.venc, 0) > 0 ? comRS(ind.venc) + ' vencido' : ''].filter(Boolean).join(' · '), def.length || prCmp(ind.venc, 0) > 0 ? 'red' : (sus.length ? 'yellow' : 'green'));
  const pan = st.pr_pan; let PP = null;
  if (pan && pan.g === 'g_of') { const x = rows.find(y => y.id === pan.id); if (x) PP = comPanOf(self, c, x); }
  else if (pan && pan.g === 'g_pr') { const x = pz.find(y => 'p:' + y.prod === pan.id); if (x) PP = comPanPr(self, c, x); }
  comPrimPainel(v, prim, PP); prPainel(self, v, PP); }
"""


def build():
    ven()
    exped()
    pcom()
