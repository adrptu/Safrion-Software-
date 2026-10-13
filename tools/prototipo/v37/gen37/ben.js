// ===== Beneficiamento · BEN-1 packing de mamão (docs/beneficiamento/ESPECIFICACAO.md v2; adaptações à base em DECISOES.md §12) =====
// A ordem de processo é c.ordens[OB] com fam 'BEN' (a mesma coleção da O.S.: cenLiberar, cenEntregar, cenDevolver e cenPodeEncerrar
// valem para ela; a tela da O.S. não a lista). Lote, movimento MP-, pedido e reserva são os da Produção (c.producao, producao.js): sem
// segundo estoque de produto e sem segunda reserva (reservar é prReservar). Massa em kg com 6 casas pelo decimal de producao.js.
// Fórmulas do beneficiamento só aqui (ENG-011): tara, caixas sugeridas, balanço, faixa, alçada, genealogia por rateio, horas de linha.
// Quem age vem do perfil (g2lib.js, cenExige): Igor (produção) cria, autoriza, executa e corrige; Paula (conferência) confere o balanço;
// Ana (gestora) decide acima da alçada; a Qualidade (Marta) ou a agrônoma registra resultado e decisão do lote; o Comercial reserva.
// Comentários só com /* */ ou // em linha própria: este arquivo também entra em strings Python.

/* ---------- PCMS-G04 mínimo (portão P3 dispensado em 05/10/2026): número sequencial por coleção; se o PCM integrar antes, vale o dele ---------- */
if (typeof cenProxId !== 'function') globalThis.cenProxId = function (c, col, pre, piso) {
  const re = new RegExp('^' + pre + '-(\\d+)$'); let n = (piso || 1) - 1;
  Object.keys(c[col] || {}).forEach(k => { const m = re.exec(k); if (m) n = Math.max(n, Number(m[1])); });
  return pre + '-' + String(n + 1).padStart(3, '0'); };
/* mudança atômica com recibo: recusa e recibo repetido não gravam nem sobem a revisão do cenário (PCMS-G04: r.nada) */
/* ordem de gravação para a trilha de Configurações (CONF R14, F1; merge CONF × BEN): o mesmo carimbo do cenMudar (confCarimbar) */
function benMudar(fn) { const c = cenClone(cenGet()); let r; const carimba = (typeof confCarimbar === 'function') ? confCarimbar : null; if (carimba) carimba(c, 0);
  try { r = fn(c) || {}; } catch (e) { r = { erro: String(e.message || e) }; }
  if (r.erro || r.nada) return r; c.rev = (c.rev || 0) + 1; if (carimba) carimba(c, c.rev); cenSave(c); return r; }

/* ---------- leitura ---------- */
const BEN_BLOCO = 'BEN-1';
const BEN_FASES = ['A liberar', 'Liberadas', 'Em execução', 'Em conferência', 'Encerradas'];
function benEh(o) { return !!o && o.fam === 'BEN'; }
function benOrdens(c) { return Object.values(c.ordens || {}).filter(benEh).sort((a, b) => a.id.localeCompare(b.id)); }
function benO(c, id) { const o = (c.ordens || {})[id]; if (!benEh(o)) throw new Error('Ordem de beneficiamento ' + id + ' não encontrada.'); return o; }
function benB(c, w) { const P = prP(c, w); if (P.ben) return P.ben; const e = { insp: {}, recibos: {}, seq: { insp: 105 } }; if (w) P.ben = e; return e; }
function benRota(k) { return (BENC.rotas || {})[k] || null; }
function benRotaTxt(r) { return r ? r.id + ' v' + r.v : '—'; }
function benQuem(papel) { const t = typeof g2quem === 'function' ? g2quem(papel) : ''; return t || ({ producao: BENC.quem.prod, qualidade: BENC.quem.qual }[papel] || papel); }
function benProdQ() { return benQuem('producao'); }
function benQualQ() { return benQuem('qualidade'); }
function benKg(x) { return prFmtT(x, 3) + ' kg'; }
function benPct(x) { return prFmt(x, 2) + ' %'; }
function benUn(n) { return prFmtT(n, 0) + ' un'; }
function benAbs(x) { return prCmp(x, 0) < 0 ? prSub(0, x) : prN(prM(x)); }
function benEm() { return prHoje() + ' ' + cenAgora(); }
/* versões aprovadas deste bloco para o produto e o estágio das entradas (R-A02): rascunho nunca; rota de bloco seguinte ainda não */
function benRotasPara(prod) { return Object.keys(BENC.rotas).filter(k => { const r = BENC.rotas[k]; return r.estado === 'Aprovada' && r.bloco === BEN_BLOCO && r.ent === prod; }); }
function benRotaErro(prod, k) {
  if (!k) { const ks = benRotasPara(prod); if (ks.length) return ks.length > 1 ? 'Escolha a rota de ' + prod + '.' : '';
    const fut = Object.keys(BENC.rotas).map(x => BENC.rotas[x]).find(r => r.estado === 'Aprovada' && r.ent === prod);
    return 'Sem rota aprovada para ' + prod + (fut ? ' no ' + BEN_BLOCO + ': a ' + benRotaTxt(fut) + ' entra no ' + fut.bloco : '') + '. Dono: ' + benProdQ() + '.'; }
  const r = benRota(k); if (!r) return 'Rota ' + k + ' não encontrada.';
  if (r.estado !== 'Aprovada') return benRotaTxt(r) + ' está em ' + String(r.estado).toLowerCase() + ': só versão aprovada é usada (dono: ' + benProdQ() + ').';
  if (r.ent !== prod) return benRotaTxt(r) + ' recebe ' + r.ent + ', não ' + prod + '.';
  if (r.bloco !== BEN_BLOCO) return benRotaTxt(r) + ' entra no ' + r.bloco + '.';
  return ''; }
function benEntrada(o) { return prSoma((o.ben.ent || []).map(e => e.kg)); }
function benValidos(o) { return (o.ben.sai || []).filter(s => !s.estorno); }
function benSoma(l) { return prSoma(l.map(s => s.kg)); }
function benOrdemAberta(c, lid, fora) { return benOrdens(c).find(o => o.id !== fora && o.etapa !== 'Encerradas' && o.etapa !== 'Canceladas' && (o.ben.ent || []).some(e => e.lote === lid)) || null; }
/* ordem que já prende o lote: liberada e ainda não fechada (a massa está no processo). Em A liberar a ordem é rascunho: tudo é conferido de
   novo na liberação (R-A03, R-A05) e no Fechar; depois de liberada, nada muda a massa da entrada por fora da ordem (revisão BEN-REV-01/02) */
function benPrende(c, L) { if (!L) return null; const ob = L.ordem && (c.ordens || {})[L.ordem]; if (ob && benEh(ob) && ['Encerradas', 'Canceladas', 'A liberar'].indexOf(ob.etapa) < 0) return ob;
  const o2 = benOrdemAberta(c, L.id); return o2 && o2.etapa !== 'A liberar' ? o2 : null; }
/* onde a ordem roda e de onde vem a fruta, quando diferem (BEN-D18): " · fruta da Lagoa Grande (Galpão de frutas Lagoa Grande) na Packing linha 1 · Packing (Santa Rita)" */
function benOndeTxt(o) { const r = benRota(o.ben.rota); const lc = PRDC.locais[o.ben.local] || {}; if (!lc.faz || lc.faz === o.ben.faz) return '';
  const a = (BENC.ativos || {})[(r && r.ativos || [])[0]]; return ' · fruta da ' + o.ben.faz + ' processada na ' + (a ? a.nome + ' · ' : '') + (lc.nome || o.ben.local) + ' (' + lc.faz + ')'; }
function benReqItem(c, o) { const r = o.req && c.reqs[o.req]; return r ? r.itens.find(i => i.prod === BENC.cx.item) || null : null; }
/* linhas de caixas da ordem, uma por lote (BEN-REV-20261009-03): a REQ da liberação e as do complemento em outro lote (o.ben.reqc), na
   ordem em que nasceram. Cada linha guarda o lote de onde as caixas saíram; o lote de uma linha nunca muda. Dano evitado: com um item só,
   o complemento trocava o lote do item e o estorno e a devolução das caixas antigas iam para o lote novo (saldo por lote corrompido) */
function benLinhas(c, o) { return [o.req].concat((o.ben && o.ben.reqc) || []).filter((k, i, a) => k && c.reqs[k] && a.indexOf(k) === i)
  .map(k => ({ rid: k, it: c.reqs[k].itens.find(i => i.prod === BENC.cx.item) })).filter(x => x.it); }
function benCxTot(c, o) { const L = benLinhas(c, o); const s = f => L.reduce((a, x) => a + (x.it[f] || 0), 0);
  return { n: L.length, L, sol: s('solicitado'), cust: s('custodia'), pend: L.reduce((a, x) => a + cenSaldoEntregar(x.it), 0), reqs: L.map(x => x.rid).join(' e ') }; }
/* custódia por linha, para a pessoa ver de que requisição e lote: "540 un (REQ-041)" ou "640 un (REQ-041 · CX26-01 540 un; REQ-042 · QA-CX-02 100 un)" */
function benCustTxt(c, o) { const T = benCxTot(c, o); return benUn(T.cust) + ' (' + (T.n > 1 ? T.L.map(x => x.rid + ' · ' + x.it.lote + ' ' + benUn(x.it.custodia)).join('; ') : T.reqs) + ')'; }

/* ---------- massa e embalagem (R-C01, R-C03): embalagem não é fruta ---------- */
function benTara(cx, pallets, r) { return prSoma([prMul(cx || 0, BENC.cx.tara), prMul(pallets || 0, r.par.tara_pallet)]); }
/* caixas sugeridas = ⌈entrada × fração vendável prevista ÷ conteúdo da caixa⌉, inteiro; confirmadas e editáveis, nunca o último valor */
function benCaixas(kg, r) { const N = prM(kg) * prM(r.par.frac_vend), D = prM(BENC.cx.massa) * PR_S; if (N <= 0n) return 0; return Number((N + D - 1n) / D); }
/* caixas livres para uma ordem: o mesmo lote e a mesma conta da liberação (cenLiberar reserva do cenLote; benImpedimentos confere cenDisp) */
function benCaixasLivres(c) { const l = cenLote(c, BENC.cx.item); return l ? Math.floor(cenDisp(l) + 1e-9) : 0; }
/* caixas da ordem nova: a necessidade da rota (a sugestão), nunca reduzida ao livre no Estoque (BEN-D23 supera a BEN-D21). Dano evitado
   (rodada 1 da integração): 540 caixas no L39-132 liberavam a ordem, embalavam 5.400 de 12.300 kg e o resto virava "diferença" no Fechar.
   A falta de caixa é impedimento da liberação, com a nota a conferir ou a sobra em custódia como saída (benCaixasRec) */
function benCaixasPadrao(c, kg, r) { const sug = benCaixas(kg, r), livre = benCaixasLivres(c); return { sug, livre, cx: sug }; }
/* notas de caixa a conferir no Estoque (BENC.nfcx): a conferida (movimento recebimento-nf com a conferência da nota) sai da lista */
function benNfCx(c) { const feitas = {}; (c.movs || []).forEach(m => { if (m.tipo === 'recebimento-nf' && m.estRec && m.estRec.id) feitas[m.estRec.id] = true; });
  return (BENC.nfcx || []).filter(n => !feitas[n.rid]); }
/* sobra de caixas de uma ordem, a única custódia que a falta de outra ordem pode pedir de volta (integração BEN, rodada 2): o que passa do
   máximo que ela ainda pode embalar, ⌈kg a embalar ÷ massa da caixa⌉ com toda a fruta em caixa (sem a fração vendável, para não subestimar
   o que ela usa). Liberada: a entrada inteira; em execução: o que falta registrar (benEmProc); enviada para conferência: nada, a custódia
   inteira é sobra (o selo "Sobra em custódia"). Dano evitado: o atalho "Receber a devolução" apontava as 1.169 caixas de uma ordem liberada;
   seguido, ela ficava sem caixa, sem cancelar (BEN-6) e com a fruta presa, e a falta só mudava de ordem (perda fictícia) */
function benCxSobra(c, o) { const cu = Math.floor(benCxTot(c, o).cust + 1e-9); if (!(cu > 0)) return 0;
  const kg = o.etapa === 'Liberadas' ? benEntrada(o) : (o.etapa === 'Em execução' ? benEmProc(o) : 0); const m = prM(BENC.cx.massa);
  const usa = prCmp(kg, 0) > 0 ? Number((prM(kg) + m - 1n) / m) : 0; return Math.max(0, cu - usa); }
/* de onde vêm as caixas que faltam (impedimento da liberação e recusa do "Pedir mais caixas"): a sobra de outra ordem (benCxSobra; Receba
   devoluções) e a nota de caixa a conferir (Confira recebimentos), o que cobrir a falta primeiro; sem nenhuma, a compra é do BEN-2: em A
   liberar a ordem pode ser cancelada (BEN-D22); liberada ou em execução não se cancela (BEN-6), e a nota que chegar é o caminho */
function benCaixasRec(c, o, d, tot) { const falta = Math.ceil(tot - d - 1e-9); const al = benQuem('almoxarife');
  const sob = benOrdens(c).filter(b => b.id !== (o && o.id)).map(b => ({ b, n: benCxSobra(c, b) })).filter(x => x.n > 0).sort((x, y) => y.n - x.n);
  const s0 = sob.find(x => x.n >= falta) || sob[0] || null; const cu = s0 ? s0.n : 0; const nf = benNfCx(c)[0] || null;
  const tDev = s0 ? 'A ' + s0.b.id + ' tem sobra de ' + prFmtT(cu, 0) + ' un em custódia (Receba devoluções).' : '';
  const tNf = nf ? 'A ' + nf.id + ' (' + nf.ped + ' · ' + nf.forn + ') traz ' + prFmtT(nf.qtd, 0) + ' un: ' + al + ' confere em Estoque › Confira recebimentos.' : '';
  const base = 'Faltam ' + prFmtT(falta, 0) + ' un. ';
  if (s0 && (cu >= falta || !nf)) return { t: 'Receber a devolução da ' + s0.b.id + ' no Estoque', h: 'EST.dc.html', why: base + tDev + (tNf ? ' ' + tNf : '') };
  if (nf) return { t: 'Conferir a ' + nf.id + ' das caixas no Estoque', h: 'EST.dc.html', why: base + tNf + (tDev ? ' ' + tDev : '') };
  const aLib = !o || o.etapa === 'A liberar';
  return { t: 'Ver saldo de caixas no Estoque', h: 'EST.dc.html', why: 'Faltam ' + prFmtT(falta, 0) + ' un e não há nota de caixas a conferir nem sobra em custódia: a compra de caixas entra no BEN-2.'
    + (aLib ? ' Sem caixa, Cancelar a ordem (nada foi reservado).' : ' Quando a nota das caixas chegar, ' + al + ' confere em Estoque › Confira recebimentos e você pede de novo (Pedir mais caixas).') }; }
/* texto curto do que traz as caixas (aviso da ordem nova): a nota a conferir e quem confere */
function benCaixasVem(c) { const nf = benNfCx(c)[0]; return nf ? nf.id + ' do ' + nf.ped + ', ' + benUn(nf.qtd) + ' a conferir · ' + benQuem('almoxarife') : benQuem('almoxarife') + ' · a compra de caixas entra no BEN-2'; }
/* faixa de conferência da parte pesada (R-F02): tol_pesado × processado, 6 casas */
function benFaixa(proc, r) { return prMul(proc, r.par.tol_pesado); }
/* balanço (R-F01): processado − (produto + outro destino + descarte + perdas identificadas), só registros válidos, base física sem tara */
function benBal(o) { const r = benRota(o.ben.rota); const v = benValidos(o); const proc = benEntrada(o); const by = f => benSoma(v.filter(s => s.fluxo === f));
  const prod = by('Produto'), outro = by('Outro destino'), desc = by('Descarte'), perda = by('Perda identificada');
  const sai = prSoma([prod, outro, desc, perda]); const dif = prSub(proc, sai); const faixa = benFaixa(proc, r); const ad = benAbs(dif);
  const pp = x => prCmp(proc, 0) > 0 ? prDiv(prMul(x, 100), proc) : 0;
  const cls = {}; v.filter(s => s.fluxo === 'Produto').forEach(s => { cls[s.classe] = prSoma([cls[s.classe] || 0, s.kg]); });
  return { proc, prod, outro, desc, perda, sai, dif, ad, pct: pp(dif), faixa, dentro: prCmp(ad, faixa) <= 0, ganho: prCmp(dif, 0) < 0, cls, rec: pp(prod), pp, r }; }
/* em processo (avanço no Concluir, R-A08): o que ainda não foi registrado entre o Iniciar e o Concluir; antes de iniciar nada está
   em processo na ordem, e depois do Concluir a ordem declara tudo processado */
function benEmProc(o) { if (o.etapa !== 'Em execução' || o.ben.conc) return 0; const x = prSub(benEntrada(o), benSoma(benValidos(o))); return prCmp(x, 0) > 0 ? x : 0; }
/* alçada de diferença (R-G06): % do processado e teto em kg da versão; vale o mais restritivo; a mensagem diz qual disparou */
function benAlcada(o, dif) { const r = benRota(o.ben.rota); const proc = benEntrada(o); const ad = benAbs(dif);
  const lp = prDiv(prMul(proc, r.par.alcada_pct), 100); const porPct = prCmp(lp, r.par.alcada_kg) <= 0; const lim = porPct ? lp : prN(prM(r.par.alcada_kg));
  const pct = prCmp(proc, 0) > 0 ? prDiv(prMul(ad, 100), proc) : 0; const passa = prCmp(ad, lim) > 0;
  const msg = !passa ? '' : (porPct ? prFmt(pct, 2) + ' % > alçada de ' + prFmtT(r.par.alcada_pct, 2) + ' %' : prFmtT(ad, 3) + ' kg > alçada de ' + prFmtT(r.par.alcada_kg, 3) + ' kg (' + benRotaTxt(r) + ', sintético)');
  return { lim, passa, msg, porPct, pct }; }
function benJustOk(o, b) { const j = (o.ben.just || []).filter(x => !x.caida); const u = j[j.length - 1]; return !!u && prCmp(u.dif, b.dif) === 0; }
/* horas de linha e HH pela capacidade nominal do ativo (R-F05): rótulo "estimado pela capacidade" */
function benHoras(o) { const r = benRota(o.ben.rota); const a = (BENC.ativos || {})[(r.ativos || [])[0]]; const proc = benEntrada(o);
  if (!a || !(a.kgh > 0)) return null; const h = prDiv(proc, a.kgh); const hh = prDiv(prMul(proc, r.equipe), a.kgh);
  return { ativo: a, h, hh, kghh: prCmp(hh, 0) > 0 ? prDiv(proc, hh) : 0, equipe: r.equipe }; }
/* condição do ativo lida da Manutenção (R-A13: só exibição no BEN-1; trava depois do PCM Bloco 2). man = estado da Manutenção ou nada */
function benCondAtivo(man, id) { const a = man && man.ativos && man.ativos[id]; const v = a ? String(a.cond || '') : String(((BENC.cond0 || {})[id]) || '');
  if (v === 'Apto') return { k: 'ok', t: 'Apto' };
  if (/^Restrito/.test(v)) return { k: 'aviso', t: v, msg: 'Restrito na Manutenção: capacidade reduzida não informada' };
  return { k: 'imped', t: v || 'sem condição informada', msg: (v || 'Sem condição') + ' na Manutenção' }; }

/* ---------- entradas: elegibilidade (R-A03) e impedimentos da liberação (R-A05) ---------- */
/* qualidade que vale fora do processo (a do lote recebido, com a carência ao vivo): a entrada da ordem tem de estar Liberada */
function benBase(c, L) { return prQualidade(c, L, { base: true }); }
function benElegErro(c, L, r, oid, kg) {
  if (!L) return { t: 'Lote não encontrado.', dono: '' };
  if (r && L.prod !== r.ent) return { t: L.id + ': ' + L.prod + ' não é a entrada da ' + benRotaTxt(r) + ' (' + r.ent + ').', dono: benProdQ() };
  const fis = prFis(c, L.id); if (prCmp(fis, 0) <= 0) return { t: L.id + ' sem saldo físico.', dono: '' };
  if (kg !== undefined && kg !== null && prCmp(kg, fis) > 0) return { t: L.id + ': ' + benKg(kg) + ' na ordem, ' + benKg(fis) + ' no lote.', dono: benProdQ() };
  const ob = L.ordem && (c.ordens || {})[L.ordem];
  if (ob && L.ordem !== oid && ['Encerradas', 'Canceladas'].indexOf(ob.etapa) < 0) return { t: L.id + ' em processo na ' + L.ordem + '.', dono: benProdQ() };
  if (prCmp(prResLote(c, L.id), 0) > 0) return { t: L.id + ' reservado para pedido: cancele a reserva antes de beneficiar.', dono: prQuem('com') };
  const Q = benBase(c, L);
  if (Q.q === 'Em inspeção') return { t: L.id + ' em inspeção' + (L.insp ? ' (' + L.insp + ')' : '') + ' · ' + (L.insp || !Q.dono || Q.dono === prQuem('qual') ? benQualQ() : Q.dono), dono: L.insp || !Q.dono || Q.dono === prQuem('qual') ? benQualQ() : Q.dono, insp: L.insp || '' };
  if (Q.q === 'Bloqueado') return { t: L.id + ' bloqueado: ' + Q.mot + ' · ' + (Q.dono || benQualQ()), dono: Q.dono || benQualQ() };
  if (Q.q !== 'Liberado') return { t: L.id + ' ' + String(Q.q).toLowerCase() + ': ' + Q.mot + '.', dono: Q.dono || '' };
  return null; }
/* lotes que podem abrir uma ordem nova: produto com rota aprovada deste bloco, elegíveis e fora de outra ordem aberta */
function benLotesAptos(c) { return Object.values(prP(c).lotes).filter(L => { const ks = benRotasPara(L.prod); return ks.length && !benElegErro(c, L, benRota(ks[0]), null) && !benOrdemAberta(c, L.id); })
  .sort((a, b) => (a.faz + a.id).localeCompare(b.faz + b.id)); }
function benImpedimentos(c, o) { const out = []; const r = benRota(o.ben.rota); const P = prP(c);
  const Ls = (o.ben.ent || []).map(e => P.lotes[e.lote]).filter(Boolean); const prods = Ls.map(L => L.prod).filter((x, i, a) => a.indexOf(x) === i);
  if (prods.length > 1) out.push({ t: 'Entradas de produtos diferentes: ' + prods.join(' e ') + '.', dono: benProdQ() });
  const re = benRotaErro(r ? r.ent : prods[0], o.ben.rota); if (re) out.push({ t: re, dono: benProdQ() });
  if (!(o.ben.ent || []).length || !(prCmp(benEntrada(o), 0) > 0)) out.push({ t: 'Informe a quantidade de entrada.', dono: benProdQ() });
  (o.ben.ent || []).forEach(e => { const x = benElegErro(c, P.lotes[e.lote], r, o.id, e.kg);
    if (x) out.push(Object.assign({ lote: e.lote, ret: (o.ben.ent || []).length > 1 }, x)); });
  (o.ins || []).forEach(x => { if (!(x.tot > 0)) return; const l = cenLote(c, x.p); const d = l ? cenDisp(l) : 0; if (d + 1e-9 >= x.tot) return;
    out.push({ t: x.p + ': ' + prFmtT(d, 0) + ' un disponíveis para ' + prFmtT(x.tot, 0) + ' un · Estoque', dono: benQuem('almoxarife'), cx: true, link: benCaixasRec(c, o, d, x.tot) }); });
  return out; }

/* próximo passo do lote de entrada em processo (Estoque de produto e Cargas): a ordem aberta ou o atalho da ordem nova (só navega) */
function benProxEntrada(c, L) { const S = prSaldos(c, L);
  if (S.ordem) return { t: 'em processo na ' + S.ordem + ' · ' + benProdQ(), h: 'BEN.dc.html#' + S.ordem, lk: 'Abrir a ' + S.ordem };
  const ob = benOrdemAberta(c, L.id); if (ob) return { t: 'na ' + ob.id + ' (' + ob.etapa + ') · ' + benProdQ(), h: 'BEN.dc.html#' + ob.id, lk: 'Abrir a ' + ob.id };
  if (benLotesAptos(c).some(x => x.id === L.id)) return { t: 'Abrir ordem de beneficiamento · ' + benProdQ(), h: 'BEN.dc.html#nova=' + L.id, lk: 'Abrir ordem de beneficiamento' };
  /* recebido com avaria no local de processo (BEN-REV-03): a Qualidade confere e libera a entrada; depois o lote abre ordem */
  if (typeof prLibProc === 'function' && prLibProc(c, L)) return { t: 'Liberar lote · ' + benQualQ(), h: 'PROD.dc.html#' + L.id, lk: 'Abrir no Estoque de produto', lib: true };
  const B = benBase(c, L); if (B.q !== 'Liberado' && B.dono) return { t: B.dono + ' resolve · ' + String(B.mot || '').split(':')[0] };
  return null; }
/* pendência das telas irmãs Cargas | Beneficiamento (faixa de Recebimento e beneficiamento, BEN-D14): só contagens, do mesmo estado */
function benPendRec(c, ok) { ok = ok || (() => true); const P = prP(c);
  const ap = Object.values(P.cargas || {}).filter(g => g.st === 'A pesar' && g.sinc !== false && ok(g.faz)).length;
  const os = benOrdens(c).filter(o => ok(o.ben.faz)); const n = f => os.filter(o => o.etapa === f).length; const lt = benLotesAptos(c).filter(L => ok(L.faz)).length;
  return { carga: ap ? ap + ' a pesar' : '',
    ben: [n('A liberar') ? n('A liberar') + ' a liberar' : '', n('Em conferência') ? n('Em conferência') + ' em conferência' : '', lt ? lt + (lt > 1 ? ' lotes a beneficiar' : ' lote a beneficiar') : ''].filter(Boolean).join(' · ') }; }

/* ---------- etapas da rota (R-A09): a aba Etapas e a trava do Fechar usam a mesma função ---------- */
function benEtapas(c, o) { const r = benRota(o.ben.rota); const v = benValidos(o); const pr = v.filter(s => s.fluxo === 'Produto');
  return ((r && r.etapas) || []).map(e => { if (e.pert !== 'Exigida') return { nome: e.nome, pert: e.pert, sit: 'Não se aplica', ev: e.mot || '' };
    let ok = false, ev = '';
    if (e.nome === 'Recepção') { ok = ['A liberar', 'Canceladas'].indexOf(o.etapa) < 0; ev = ok ? 'entradas ' + o.ben.ent.map(x => x.lote).join(', ') + ' liberadas para a ordem' : 'conferida na liberação'; }
    else if (e.nome === 'Triagem e classificação') { ok = pr.some(s => !!s.classe); ev = ok ? pr.map(s => s.id + ' classe ' + s.classe).join(', ') : 'nenhuma saída de Produto com classe'; }
    else if (e.nome === 'Embalagem') { ok = pr.length > 0 && pr.every(s => s.cx > 0 && prCmp(s.bruto || 0, 0) > 0); ev = ok ? pr.map(s => s.id + ' ' + s.cx + ' cx').join(', ') : 'saída de Produto sem caixas e bruto'; }
    else ev = 'sem evidência registrada';
    return { nome: e.nome, pert: 'Exigida', sit: ok ? 'Cumprida' : 'Pendente', ev }; }); }

/* ---------- próximo passo, selos e textos ---------- */
function benSelos(c, o) { const out = []; const b = benBal(o); const T = benCxTot(c, o);
  if (o.etapa === 'A liberar' && benImpedimentos(c, o).length) out.push({ t: 'Impedida', c: 'red' });
  if (o.ben.conc && o.etapa === 'Em conferência' && !b.dentro && !benJustOk(o, b)) out.push({ t: b.ganho ? 'Ganho aparente acima da faixa' : 'Diferença acima da faixa', c: 'red' });
  if (o.ben.corr && o.ben.corr.pend) out.push({ t: 'Correção aguarda a gestão', c: 'yellow' });
  if (o.ben.corrigido) out.push({ t: 'Corrigido na conferência', c: 'yellow' });
  if (o.etapa === 'Em conferência' && T.cust > 1e-9) out.push({ t: 'Sobra em custódia', c: 'yellow' });
  if (['Encerradas', 'Canceladas'].indexOf(o.etapa) < 0 && o.ben.fim && o.ben.fim < prHoje()) out.push({ t: 'Atrasada', c: 'red' });
  return out; }
function benProx(c, o) { const b = benBal(o); const T = benCxTot(c, o);
  if (o.etapa === 'A liberar') { const im = benImpedimentos(c, o);
    return im.length ? { t: 'Resolver ' + (im.length > 1 ? im.length + ' impedimentos' : '1 impedimento') + ' e autorizar a rota', quem: im.map(x => x.dono).filter(Boolean).filter((x, i, a) => a.indexOf(x) === i).join('; '), acao: 'liberar', imp: im, red: true,
        nota: 'Sem como resolver: Cancelar a ordem (nada foi reservado) e abrir outra · ' + benProdQ() }
      : { t: 'Autorizar rota e liberar', quem: benProdQ(), acao: 'liberar' }; }
  if (o.etapa === 'Canceladas') { const k = o.ben.canc || {}; return { t: 'Cancelada: ' + (k.motivo || '—'), quem: k.quem || '', acao: null, nota: 'Nada estava reservado; as entradas abrem outra ordem' }; }
  if (o.etapa === 'Liberadas') { const falta = T.n && T.pend > 1e-9 && !(T.cust > 1e-9);
    return { t: 'Iniciar processo', quem: benProdQ(), acao: 'iniciar', nota: falta ? 'Caixas da ' + T.reqs + ' ainda no Estoque: ' + benQuem('almoxarife') + ' entrega no balcão (' + benUn(T.pend) + ').' : '' }; }
  if (o.etapa === 'Em execução') { const pr = benValidos(o).some(s => s.fluxo === 'Produto');
    const ep = benEmProc(o); return pr ? { t: 'Enviar para conferência', quem: benProdQ(), acao: 'concluir', nota: prCmp(ep, 0) > 0 ? 'O que não foi registrado (' + benKg(ep) + ') vira diferença na conferência.' : '' } : { t: 'Registrar saída', quem: benProdQ(), acao: 'saida' }; }
  if (o.etapa === 'Em conferência') {
    if (o.ben.corr && o.ben.corr.pend) return { t: 'Confirmar correção', quem: benQuem('gestor'), acao: 'confirmar', nota: 'Correção na conferência ' + o.ben.corr.msg + ': decide ' + benQuem('gestor') + '.', red: true };
    if (o.ben.conf) { const pe = cenPodeEncerrar(c, o.id); return { t: 'Fechar processo', quem: benProdQ(), acao: 'fechar', nota: pe, red: !!pe, quemNota: pe ? benQuem('almoxarife') : '' }; }
    if (!b.dentro && !benJustOk(o, b)) { const al = benAlcada(o, b.dif); return { t: 'Justificar diferença', quem: al.passa ? benQuem('gestor') : benProdQ(), acao: 'justificar', red: true,
      nota: 'Diferença ' + benKg(b.dif) + ' (' + benPct(b.pct) + ') ' + (b.ganho ? 'de ganho aparente ' : '') + 'fora da faixa de ' + benKg(b.faixa) + (al.passa ? ': ' + al.msg + ', decide ' + benQuem('gestor') : '') + '.' }; }
    return { t: 'Conferir balanço', quem: benQuem('conferente'), acao: 'conferir' }; }
  if (o.etapa === 'Encerradas') { const I = o.ben.insp && benB(c).insp[o.ben.insp]; return { t: 'Encerrada · lotes com a Qualidade', quem: benQualQ(), acao: null, nota: I ? 'Inspeção ' + I.id + ' · prazo ' + prBr(I.prazo) + ': fechar não libera; a Qualidade libera em Estoque de produto.' : '' }; }
  return { t: o.etapa, quem: '', acao: null }; }

/* ---------- idempotência e versão esperada (R-A11, PCMS-G04) ---------- */
function benRecibo(c, k, nome, imp) { if (!k || !k.chave) return null; const ja = (benB(c).recibos || {})[k.chave]; if (!ja) return null;
  if (ja.nome !== nome || ja.imp !== imp) throw new Error('Este registro (' + k.chave + ') já foi gravado com outro conteúdo: conflito, nada gravado.');
  return { msg: 'Já feito: ' + ja.msg, nada: true, repetido: true, id: ja.id || '' }; }
function benGravaRecibo(c, k, nome, imp, msg, id) { if (!k || !k.chave) return; benB(c, 1).recibos[k.chave] = Object.assign({ nome, imp, msg, at: cenAgora() }, id ? { id } : {}); }
function benEstadoTxt(o) { const b = benBal(o); return o.etapa + ' · ' + benValidos(o).length + ' registros válidos · diferença ' + benKg(b.dif); }
/* ordem cancelada (BEN-D22): todo comando sobre ela é recusa com o motivo e o caminho, nunca aviso de sucesso "Já feito" (rodada 1, S4) */
function benViva(o, verbo) { if (o.etapa !== 'Canceladas') return; const k = o.ben.canc || {};
  throw new Error(o.id + ' cancelada' + (k.motivo ? ' (' + k.motivo + ')' : '') + ': nada a ' + verbo + '. As entradas abrem outra ordem.'); }
function benVer(o, k) { if (k && k.ver !== undefined && k.ver !== null && Number(k.ver) !== Number(o.ver || 1))
  throw new Error('A ' + o.id + ' mudou depois que você abriu: ' + benEstadoTxt(o) + '. Confira e registre de novo.'); }
function benToca(o) { o.ver = (o.ver || 1) + 1; }
function benHist(o, quem, ev, det, mov) { o.ben.hist.push({ d: prHoje(), at: cenAgora(), quem, ev, det: det || '', mov: mov || '' }); }
/* o balanço mudou: a conferência e a justificativa dadas sobre o balanço antigo caem, com linha no histórico (R-A15) */
function benBalMudou(o, quem) { const ca = [];
  if (o.ben.conf) { o.ben.conf = null; ca.push('conferência'); }
  (o.ben.just || []).forEach(j => { if (!j.caida) { j.caida = true; ca.push('justificativa de ' + j.quem); } });
  if (ca.length) benHist(o, quem, 'Caiu: ' + ca.join(' e '), 'dada sobre o balanço anterior'); }
/* correção na conferência (R-F07): grava antes → depois e o selo; se leva |dif| de fora para dentro da faixa e |dif₀| passa da alçada
   de quem corrige, só vale com a confirmação da gestão */
/* maior |dif₀| declarado na ordem: o do Concluir vigente e o de antes de cada Reabrir (o Reabrir derruba a declaração, não a alçada; BEN-D16) */
function benDif0(o) { const a = o.ben.conc ? o.ben.conc.dif0 : null, b = o.ben.dif0r; const ok = x => x !== null && x !== undefined;
  if (!ok(a)) return ok(b) ? b : null; if (!ok(b)) return a; return prCmp(benAbs(a), benAbs(b)) >= 0 ? a : b; }
function benCorrMsg(o, al, d0, onde) { const r = benRota(o.ben.rota); return 'acima da alçada de ' + (al.porPct ? prFmtT(r.par.alcada_pct, 2) + ' %' : prFmtT(r.par.alcada_kg, 3) + ' kg') + ' (diferença ' + onde + ' ' + benKg(d0) + ', ' + benPct(al.pct) + ')'; }
function benCorrecao(o, quem, ator, b0, b1, motivo) { o.ben.corrigido = true; const d0 = benDif0(o); const al = benAlcada(o, d0 !== null ? d0 : b1.dif);
  if (!b0.dentro && b1.dentro && al.passa && !(typeof g2papel === 'function' && g2papel(ator, 'gestor')))
    o.ben.corr = { pend: true, quem, em: benEm(), motivo, antes: b0.dif, depois: b1.dif, msg: benCorrMsg(o, al, d0, d0 === o.ben.dif0r && !(o.ben.conc && o.ben.conc.dif0 === d0) ? 'no envio para conferência antes de reabrir' : 'no envio para conferência') };
  else if (o.ben.corr && o.ben.corr.pend && !b1.dentro) o.ben.corr.pend = false; }

/* ---------- comandos (sempre dentro de cenMudar ou benMudar); quem age é o perfil (cenExige); recusa não grava nada ---------- */
function benProxOB(c) { let n = 100; Object.keys(c.ordens || {}).forEach(k => { const m = /^OB-(\d+)$/.exec(k); if (m) n = Math.max(n, Number(m[1])); }); return 'OB-' + String(n + 1).padStart(4, '0'); }
function benInspId(c) { const B = benB(c, 1); let n = B.seq.insp || 105; Object.keys(B.insp).forEach(k => { const m = /^INSP-(\d+)$/.exec(k); if (m) n = Math.max(n, Number(m[1])); }); B.seq.insp = n + 1; return 'INSP-' + (n + 1); }
function benNum(x) { return prNumOk(x) ? prNum(x) : NaN; }
/* nova ordem (A liberar): entradas, rota e caixas; não reserva nada (DEC-2609-13: a reserva nasce na liberação) */
function benNova(c, k, ator) { const quem = cenExige(ator, 'producao', 'Criar ordem de beneficiamento');
  const ents = (k.lotes || []).map(e => ({ lote: e.lote, kg: benNum(e.kg) }));
  const imp = JSON.stringify([ents.map(e => [e.lote, String(e.kg)]), k.rota || '', String(k.cx === undefined ? '' : k.cx), k.ini || '']);
  const ja = benRecibo(c, k, 'benNova', imp); if (ja) return ja;
  if (!ents.length || ents.some(e => !(isFinite(e.kg) && e.kg > 0))) throw new Error('Informe a quantidade de entrada.');
  const P = prP(c, 1); const Ls = ents.map(e => P.lotes[e.lote]); if (Ls.some(x => !x)) throw new Error('Lote de entrada não encontrado.');
  if (ents.some((e, i) => ents.findIndex(x => x.lote === e.lote) !== i)) throw new Error('Lote repetido nas entradas.');
  const prods = Ls.map(L => L.prod).filter((x, i, a) => a.indexOf(x) === i); if (prods.length > 1) throw new Error('Entradas de produtos diferentes: ' + prods.join(' e ') + '.');
  const fz = Ls.map(L => L.faz).filter((x, i, a) => a.indexOf(x) === i); if (fz.length > 1) throw new Error('Entradas de fazendas diferentes: ' + fz.join(' e ') + '. Uma ordem por fazenda.');
  const ks = benRotasPara(prods[0]); const rk = k.rota || (ks.length === 1 ? ks[0] : ''); const re = benRotaErro(prods[0], rk); if (re) throw new Error(re); const r = benRota(rk);
  Ls.forEach((L, i) => { const x = benElegErro(c, L, r, null, ents[i].kg); if (x) throw new Error(x.t); const ob = benOrdemAberta(c, L.id); if (ob) throw new Error(L.id + ' já está na ' + ob.id + ' (' + ob.etapa + ').');
    /* lote inteiro (BEN-D17): entrada parcial prenderia o resto do lote em processo até o Fechar, fora do vendável e de outra ordem */
    const fis = prFis(c, L.id); if (prCmp(ents[i].kg, fis) !== 0) throw new Error('A ordem leva o lote inteiro: ' + L.id + ' tem ' + benKg(fis) + ' (informado ' + benKg(ents[i].kg) + '). Entrada parcial prenderia o resto do lote até o Fechar.'); });
  const proc = prSoma(ents.map(e => e.kg)); const pad = benCaixasPadrao(c, proc, r); const sug = pad.sug;
  const cx = (k.cx === undefined || k.cx === null || k.cx === '') ? pad.cx : benNum(k.cx); if (!(Number.isInteger(cx) && cx >= 0)) throw new Error('Caixas: número inteiro de unidades (sugestão ' + sug + ').');
  /* dano evitado (BEN-REV-05): ordem liberada sem caixa não registra Produto nem conclui, e a entrada fica presa em processo */
  if (cx < 1 && (r.saidas || []).some(s => s.fluxo === 'Produto' && s.caixa)) throw new Error('Caixas: ao menos 1 un. O Produto da ' + benRotaTxt(r) + ' sai em caixa (sugestão ' + sug + ').');
  const ini = k.ini || prHoje(); if (!/^\d{4}-\d\d-\d\d$/.test(ini)) throw new Error('Informe o início da ordem.');
  /* a ordem roda onde a linha da rota está (BEN-D18): linha, balança e caixas são as desse local; a fazenda dona da fruta fica nos lotes */
  const lloc = ((BENC.linhas || {})[(r.ativos || [])[0]]) || Ls[0].local; const id = benProxOB(c); const loc = (PRDC.locais[lloc] || {}).nome || lloc;
  const o = c.ordens[id] = { id, fam: 'BEN', tipo: 'Beneficiamento · ' + (r.nome || r.id), talhao: loc, area: 0, etapa: 'A liberar', versao: 'v1', ver: 1, realizado: 0, saldo: 0,
    resp: (typeof g2pf === 'function' && g2pf(ator) ? g2pf(ator).k : quem), ins: cx > 0 ? [{ g: 'Embalagem', p: BENC.cx.item, dose: 0, un: 'un', tot: cx, emb: BENC.cx.emb }] : [], req: null, selos: [], ap: [], reservado: false,
    ben: { rota: rk, faz: Ls[0].faz, local: lloc, ini, fim: prDiaMais(ini, 1), cxSug: sug, insp: '', nsai: 0, ent: ents.map(e => ({ lote: e.lote, kg: prN(prM(e.kg)) })), sai: [], conc: null, conf: null, just: [], corr: null, hist: [] } };
  const det = benRotaTxt(r) + ' · ' + ents.map(e => e.lote).join(', ') + ' · ' + benKg(proc) + ' · ' + benUn(cx) + ' de caixa'
    + (cx === sug ? ' (sugestão confirmada)' : ' (sugestão ' + sug + ')') + benOndeTxt(o);
  benHist(o, quem, 'Ordem criada · v1', det);
  /* acima do livre a ordem nasce, mas a liberação fica impedida até o Estoque ter as caixas: o aviso diz isso agora, não na liberação */
  const av = cx > pad.livre ? ' Atenção: ' + benUn(pad.livre) + ' livres no Estoque para ' + benUn(cx) + ': a liberação fica impedida até o Estoque receber as caixas (' + benCaixasVem(c) + ').' : '';
  const msg = id + ' criada (A liberar): ' + det + '. Próximo passo: Autorizar rota e liberar.' + av; benGravaRecibo(c, k, 'benNova', imp, msg, id); return { msg, id }; }
/* retirar entrada antes de liberar (I3): grava a versão seguinte; a sugestão de caixas acompanha a entrada quando estava confirmada */
function benRetirar(c, id, lote, ator, k) { const quem = cenExige(ator, 'producao', 'Retirar ' + lote + ' da ' + id); const o = benO(c, id);
  const imp = JSON.stringify([id, lote]); const ja = benRecibo(c, k, 'benRetirar', imp); if (ja) return ja; benVer(o, k);
  if (o.etapa !== 'A liberar') throw new Error('Retirar entrada só em A liberar (' + id + ' está em ' + o.etapa + ').');
  const i = o.ben.ent.findIndex(e => e.lote === lote); if (i < 0) throw new Error(lote + ' não está na ' + id + '.');
  if (o.ben.ent.length === 1) throw new Error('A ' + id + ' ficaria sem entrada: inclua outro lote antes de retirar o ' + lote + '.');
  o.ben.ent.splice(i, 1); const r = benRota(o.ben.rota); const sug = benCaixas(benEntrada(o), r); const it = (o.ins || [])[0];
  if (it && it.tot === o.ben.cxSug) it.tot = sug; o.ben.cxSug = sug; o.versao = 'v' + (Number(String(o.versao).replace(/\D/g, '') || 1) + 1); benToca(o);
  const det = lote + ' sai da ordem: ' + benKg(benEntrada(o)) + ' · ' + benUn(it ? it.tot : 0) + ' de caixa (sugestão ' + sug + ')';
  benHist(o, quem, 'Entrada retirada · ' + o.versao, det); const msg = id + ' ' + o.versao + ': ' + det + '.'; benGravaRecibo(c, k, 'benRetirar', imp, msg); return { msg }; }
/* cancelar a ordem em A liberar (BEN-D22): rascunho, nada autorizado nem reservado (DEC-2609-13); sai do quadro para Canceladas com motivo,
   quem e quando, e as entradas voltam a abrir ordem. Dano evitado (integração BEN): ordem que não libera (caixas acima do livre; entrada que
   mudou com o estorno da carga, BEN-D19) prendia o lote perecível sem saída. Liberada em diante, cancelar mexe em reserva e entrega (BEN-6) */
function benCancelar(c, id, motivo, ator, k) { const quem = cenExigeUm(ator, ['producao', 'gestor'], 'Cancelar a ' + id); const o = benO(c, id);
  const mot = String(motivo || '').trim(); const imp = JSON.stringify([id, mot]); const ja = benRecibo(c, k, 'benCancelar', imp); if (ja) return ja;
  if (o.etapa === 'Canceladas') throw new Error('Já feito: ' + id + ' cancelada.'); benVer(o, k);
  if (o.etapa !== 'A liberar') throw new Error('Cancele só em A liberar (' + id + ' está em ' + o.etapa + '): depois da liberação há reserva e entrega, e o cancelamento entra no BEN-6.');
  if (!mot) throw new Error('Informe o motivo do cancelamento.');
  o.etapa = 'Canceladas'; o.ben.canc = { quem, em: benEm(), motivo: mot }; const ls = o.ben.ent.map(e => e.lote).join(', ');
  benHist(o, quem, 'Ordem cancelada · ' + o.versao, mot + ' · nada estava reservado; ' + ls + (o.ben.ent.length > 1 ? ' voltam' : ' volta') + ' a abrir ordem'); benToca(o);
  const msg = id + ' cancelada por ' + quem + ' (' + mot + '): nada estava reservado; ' + ls + (o.ben.ent.length > 1 ? ' podem' : ' pode') + ' abrir outra ordem.';
  benGravaRecibo(c, k, 'benCancelar', imp, msg); return { msg }; }
/* autorizar rota e liberar (R-A05): todas as causas de uma vez; sem causa, CMD-42 e CMD-06 em eventos separados no mesmo cenMudar */
function benAutorizarLiberar(c, id, ator, k) { const quem = cenExige(ator, 'producao', 'Autorizar rota e liberar a ' + id); const o = benO(c, id);
  benViva(o, 'liberar'); if (o.etapa !== 'A liberar') throw new Error('Já feito: ' + id + ' está em ' + o.etapa + '.'); benVer(o, k);
  const im = benImpedimentos(c, o);
  if (im.length) throw new Error('Liberação recusada · ' + (im.length > 1 ? im.length + ' causas: ' : '1 causa: ') + im.map(x => x.t + (x.dono ? ' (resolve: ' + x.dono + ')' : '')).join(' · ') + '. Nada foi gravado.');
  const r = benRota(o.ben.rota); const tot = (o.ins || []).reduce((a, x) => a + (x.tot || 0), 0);
  benHist(o, quem, 'Versão ' + o.versao + ' da ordem autorizada (CMD-42)', benRotaTxt(r) + ' · ' + o.ben.ent.map(e => e.lote).join(', ') + ' · ' + benKg(benEntrada(o)) + ' · ' + benUn(tot) + ' de caixa');
  if (tot > 0) { const rid = cenProxId(c, 'reqs', 'REQ', 41); o.req = rid; c.reqs[rid] = { id: rid, os: id, itens: [], estado: 'Reservada' }; cenLiberar(c, id); }
  else { o.etapa = 'Liberadas'; o.reservado = false; }   /* ordem sem material libera sem abrir requisição */
  o.ben.ent.forEach(e => { prP(c, 1).lotes[e.lote].ordem = id; });
  const det = o.req ? o.req + ' reservou ' + benUn(tot) + ' de ' + BENC.cx.item + '; entradas reservadas à ordem' : 'sem material; entradas reservadas à ordem';
  benHist(o, quem, 'Liberada (CMD-06)', det); benToca(o);
  return { msg: id + ' ' + o.versao + ' autorizada (CMD-42) e liberada (CMD-06) por ' + quem + ': ' + det + '.' + (o.req ? ' O Estoque entrega as caixas no balcão.' : '') }; }
function benIniciar(c, id, ator, k) { const quem = cenExige(ator, 'producao', 'Iniciar a ' + id); const o = benO(c, id);
  benViva(o, 'iniciar'); if (o.etapa !== 'Liberadas') throw new Error(o.etapa === 'A liberar' ? id + ' ainda não foi liberada: Autorizar rota e liberar.' : 'Já feito: ' + id + ' está em ' + o.etapa + '.'); benVer(o, k);
  o.etapa = 'Em execução'; const T = benCxTot(c, o); T.L.forEach(x => { if (x.it.custodia > 1e-9) x.it.confirmado = 'balcao'; });   /* recebida no balcão por quem executa (PCMS-M14) */
  benHist(o, quem, 'Iniciada', 'Entradas ' + o.ben.ent.map(e => e.lote).join(', ') + ' em processo'); benToca(o);
  return { msg: id + ' em execução: registre as saídas pesadas (produto com caixas e bruto, descarte, outro destino e perda identificada).' + (T.n && !(T.cust > 1e-9) ? ' Caixas da ' + T.reqs + ' ainda no Estoque.' : '') }; }
/* registrar saída, descarte, outro destino ou perda identificada (R-A07, R-C01, R-C02, R-F07, R-A12) */
const BEN_FLUXOS = ['Produto', 'Outro destino', 'Descarte', 'Perda identificada'];
function benSaida(c, id, k, ator) { const quem = cenExige(ator, 'producao', 'Registrar saída na ' + id); const o = benO(c, id); const r = benRota(o.ben.rota);
  const imp = JSON.stringify([id, k.fluxo || '', k.classe || '', k.destino || '', k.causa || '', String(k.cx === undefined ? '' : k.cx), String(k.pallets === undefined ? '' : k.pallets),
    String(k.bruto === undefined ? '' : k.bruto), String(k.kg === undefined ? '' : k.kg), String(k.ticket || '').trim(), k.subst || '', String(k.motivo || '').trim()]);
  const ja = benRecibo(c, k, 'benSaida', imp); if (ja) return ja; benVer(o, k);
  if (['Em execução', 'Em conferência'].indexOf(o.etapa) < 0) throw new Error(o.etapa === 'Encerradas' ? 'Correção de ordem encerrada é ajuste vinculado com alçada (BEN-7).' : 'Registre saídas só em Em execução (' + id + ' está em ' + o.etapa + ').');
  const conf = o.etapa === 'Em conferência'; const def = r.saidas.find(s => s.fluxo === k.fluxo);
  if (!def) throw new Error('Escolha o fluxo: ' + r.saidas.map(s => s.fluxo).join(', ') + '.');
  let sub = null;
  if (conf) { if (k.fluxo !== 'Perda identificada') { sub = o.ben.sai.find(s => s.id === k.subst && s.estorno && !o.ben.sai.some(x => x.subst === s.id && !x.estorno));
      if (!sub) throw new Error('Em conferência, nova saída só substitui registro estornado ou lança perda identificada. Para outra saída, reabra a execução.'); }
    if (!String(k.motivo || '').trim()) throw new Error('Correção na conferência: informe o motivo.'); }
  const s = { id: 'S-' + String(o.ben.nsai + 1).padStart(2, '0'), fluxo: k.fluxo, classe: '', destino: '', causa: '', prod: '', lote: '', cx: 0, pallets: 0, bruto: null, tara: null, kg: 0,
    orig: 'Pesado', ev: { ticket: '', balanca: r.par.balanca, em: benEm() }, d: prHoje(), at: cenAgora(), quem, chave: k.chave || '', estorno: null, subst: sub ? sub.id : '', motivo: String(k.motivo || '').trim() };
  let T = null, aviso = '';
  if (k.fluxo === 'Produto') {
    if ((def.classes || []).indexOf(k.classe) < 0) throw new Error('Escolha a classe: ' + def.classes.join(' ou ') + '.');
    const cx = benNum(k.cx), bruto = benNum(k.bruto);
    if (!(Number.isInteger(cx) && cx > 0) || !(isFinite(bruto) && bruto > 0)) throw new Error('Informe caixas e bruto.');
    let pal = 0; if (r.par.pesagem === 'pallet') { pal = benNum(k.pallets); if (!(Number.isInteger(pal) && pal >= 0)) throw new Error('Informe os pallets pesados (0 ou mais).'); }
    const tara = benTara(cx, pal, r); const liq = prSub(bruto, tara); if (prCmp(liq, 0) <= 0) throw new Error('Bruto ' + benKg(bruto) + ' não passa da tara ' + benKg(tara) + ': confira a pesagem.');
    T = benCxTot(c, o); const cust = T.cust, pend = T.pend; const mais = T.n > 1;
    /* a recusa diz a saída (rodada 1, S3): a entrega pendente no balcão, ou o complemento da mesma ordem quando a REQ já foi toda entregue */
    if (cx > cust + 1e-9) throw new Error('Caixas acima da custódia: ' + benUn(cust) + (pend > 1e-9 ? '. A ' + T.reqs + (mais ? ' têm ' : ' tem ') + benUn(pend) + ' a entregar: ' + benQuem('almoxarife') + ' entrega no balcão (Estoque › Entregue por O.S.).'
      : ', e a ' + (T.reqs || 'requisição') + (mais ? ' já foram todas entregues' : ' já foi toda entregue') + '. Peça mais caixas na ordem ("Pedir mais caixas"); ' + benQuem('almoxarife') + ' entrega no balcão.'));
    Object.assign(s, { classe: k.classe, prod: def.prod, cx, pallets: pal, bruto: prN(prM(bruto)), tara, kg: liq });
    const pc = prDiv(liq, cx); const nom = BENC.cx.massa; const desv = prDiv(prMul(prSub(pc, nom), 100), nom);
    if (prCmp(benAbs(prSub(pc, nom)), prMul(nom, r.par.aviso_cx)) > 0) aviso = ' Atenção: ' + prFmtT(pc, 3) + ' kg por caixa contra ' + prFmtT(nom, 3) + ' kg (' + (prCmp(desv, 0) > 0 ? '+' : '') + prFmt(desv, 2) + ' %): confira a contagem ou a pesagem.'; }
  else { const kg = benNum(k.kg); if (!(isFinite(kg) && kg > 0)) throw new Error('Informe o peso em kg.');
    if (k.fluxo === 'Perda identificada') { if ((def.causas || []).indexOf(k.causa) < 0) throw new Error('Escolha a causa da perda: ' + def.causas.join(', ') + '.');
      if (!String(k.ticket || '').trim()) throw new Error('Sem pesagem não é perda identificada. Justifique a diferença (alçada).');
      s.causa = k.causa; s.ev.ticket = String(k.ticket).trim(); }
    else { if ((def.destinos || []).indexOf(k.destino) < 0) throw new Error('Escolha o destino: ' + def.destinos.join(', ') + '.'); s.destino = k.destino; }
    s.kg = prN(prM(kg)); }
  /* R-A07: massa pesada não se cria (só a parte pesada; estimativa nunca recusa pesagem) */
  const proc = benEntrada(o), tol = benFaixa(proc, r); const tot = prSoma([benSoma(benValidos(o)), s.kg]);
  if (prCmp(tot, prSoma([proc, tol])) > 0) throw new Error('Saídas pesadas ' + benKg(tot) + ' > entrada ' + benKg(proc) + ' + tolerância ' + benKg(tol) + '. Confira a pesagem.');
  if (s.fluxo === 'Produto') { s.lote = (o.ben.sai.find(x => x.fluxo === 'Produto' && x.classe === s.classe && x.lote) || {}).lote || prProxLote(c, prHoje());   /* um lote por classe da ordem (R-A16) */
    /* consumo por linha (BEN-REV-20261009-03): sai da custódia da requisição mais antiga primeiro; cada parte grava a requisição, o lote e o
       movimento, para o estorno voltar ao mesmo lote. Quem embala tem as caixas: recebidas no balcão (PCMS-M14) */
    let rest = s.cx; s.cons = [];
    T.L.forEach(x => { const q = Math.min(rest, x.it.custodia); if (!(q > 1e-9)) return; x.it.consumido += q; x.it.custodia -= q; x.it.confirmado = 'balcao'; rest -= q;
      s.cons.push({ req: x.rid, lote: x.it.lote, qtd: q, mv: cenMov(c, { tipo: 'consumo', os: id, req: x.rid, prod: BENC.cx.item, lote: x.it.lote, qtd: q, un: 'un', quem, origem: 'web', sinc: true, det: BENC.cx.item + ' ' + q }).id }); });
    s.mv = s.cons[0].mv; }
  const b0 = benBal(o); o.ben.nsai += 1; o.ben.sai.push(s); const b1 = benBal(o);
  if (conf) { benBalMudou(o, quem); benCorrecao(o, quem, ator, b0, b1, s.motivo); }
  const det = s.fluxo + (s.classe ? ' ' + s.classe : '') + (s.destino ? ' · ' + s.destino : '') + (s.causa ? ' · ' + s.causa + ' · ticket ' + s.ev.ticket : '')
    + (s.cx ? ' · ' + s.cx + ' cx · bruto ' + benKg(s.bruto) + ' − tara ' + benKg(s.tara) + ' = ' + benKg(s.kg) + ' → ' + s.lote : ' · ' + benKg(s.kg)) + (s.subst ? ' · substitui ' + s.subst : '')
    + (conf ? ' · correção na conferência (' + s.motivo + '): diferença ' + benKg(b0.dif) + ' → ' + benKg(b1.dif) : '')
    + ((s.cons || []).length > 1 ? ' · caixas ' + s.cons.map(p => benUn(p.qtd) + ' do ' + p.lote + ' (' + p.req + ')').join(' + ') : '');
  benHist(o, quem, 'Saída ' + s.id + ' registrada', det, (s.cons || []).map(p => p.mv).join(', ')); benToca(o);
  const msg = s.id + ' registrada na ' + id + ': ' + det + '.' + (o.ben.corr && o.ben.corr.pend ? ' Correção ' + o.ben.corr.msg + ': decide ' + benQuem('gestor') + '.' : '') + aviso;
  benGravaRecibo(c, k, 'benSaida', imp, msg); return { msg, s }; }
/* pedir mais caixas (rodada 1 da integração, S3): falta de caixa na execução se resolve pelo mecanismo de requisição existente, o
   complemento da mesma ordem. Reserva no Estoque (movimento de reserva), soma às caixas da ordem; o Estoque entrega no balcão e as caixas
   viram custódia de quem executa; recibo pela chave de quem pede e versão esperada. Sai do lote de uma linha da ordem que tenha as caixas
   livres (a REQ da liberação primeiro); senão, do lote com caixas livres numa requisição própria da ordem (linha por lote,
   BEN-REV-20261009-03): o lote de uma linha nunca muda, e o estorno e a devolução voltam ao lote de onde as caixas saíram. Dano evitado:
   a ordem embalava só parte da fruta e o resto virava diferença no Fechar (perda fictícia) */
function benComplementar(c, id, qtd, ator, k) { const quem = cenExige(ator, 'producao', 'Pedir caixas para a ' + id); const o = benO(c, id); k = k || {};
  const n = benNum(qtd); const imp = JSON.stringify([id, String(qtd)]); const ja = benRecibo(c, k, 'benComplementar', imp); if (ja) return ja;
  benViva(o, 'pedir'); benVer(o, k);
  if (['Liberadas', 'Em execução'].indexOf(o.etapa) < 0 || o.ben.conc) throw new Error('Peça caixas com a ordem liberada ou em execução (' + id + ' está em ' + o.etapa + '): ' + (o.etapa === 'A liberar' ? 'antes de liberar, ajuste as caixas da ordem; a reserva nasce na liberação.' : 'na conferência não entra embalagem nova; reabra a execução se faltou registrar Produto.'));
  if (!(Number.isInteger(n) && n >= 1)) throw new Error('Caixas: número inteiro de unidades (ao menos 1).');
  const L = benLinhas(c, o); if (!L.length) throw new Error(id + ' sem requisição de caixas.');
  const livre = x => { const l = c.lotes[x.it.prod + '|' + x.it.lote]; return l ? Math.floor(cenDisp(l) + 1e-9) : 0; };
  let x = L.find(y => livre(y) >= n) || null; let troca = '';
  if (!x) { const b = cenLote(c, L[0].it.prod); const lb = b ? Math.floor(cenDisp(b) + 1e-9) : 0; const mx = Math.max(lb, ...L.map(livre));
    if (!b || lb < n) throw new Error('Pedir ' + benUn(n) + ': ' + benUn(mx) + ' livres no Estoque. ' + benCaixasRec(c, o, mx, n).why + ' Nada foi gravado.');
    const i0 = L[0].it; const rid = cenProxId(c, 'reqs', 'REQ', 41);
    c.reqs[rid] = { id: rid, os: id, itens: [{ prod: i0.prod, lote: b.lote, un: i0.un, emb: i0.emb || '', solicitado: 0, entregue: 0, consumido: 0, devolvido: 0, custodia: 0 }], estado: 'Reservada', comp: o.req };
    (o.ben.reqc = o.ben.reqc || []).push(rid); x = { rid, it: c.reqs[rid].itens[0] };
    troca = ' no ' + b.lote + ' (o ' + L.map(y => y.it.lote + ' da ' + y.rid).join(' e o ') + ' tinha' + (L.length > 1 ? 'm ' : ' ') + L.map(y => benUn(livre(y))).join(' e ') + ' livres: requisição própria, a devolução volta a cada lote)'; }
  const it = x.it; c.lotes[it.prod + '|' + it.lote].reservado += n; it.solicitado += n; const ins = (o.ins || []).find(y => y.p === it.prod); if (ins) ins.tot += n;
  const mv = cenMov(c, { tipo: 'reserva', req: x.rid, os: id, prod: it.prod, lote: it.lote, qtd: n, un: it.un, quem, origem: 'web', det: 'complemento da ' + id });
  const det = x.rid + ' ' + prFmtT(it.solicitado - n, 0) + ' → ' + benUn(it.solicitado) + ' · reserva' + (troca || ' no ' + it.lote) + ' · ' + benQuem('almoxarife') + ' entrega no balcão';
  benHist(o, quem, 'Caixas pedidas · ' + x.rid + ' +' + benUn(n), det, mv.id); benToca(o);
  const msg = benUn(n) + ' de ' + it.prod + ' pedidas para a ' + id + troca + ': ' + x.rid + ' com ' + benUn(it.solicitado) + '. ' + benQuem('almoxarife') + ' entrega no balcão (Estoque › Entregue por O.S.).';
  benGravaRecibo(c, k, 'benComplementar', imp, msg); return { msg }; }
/* estornar registro (R-A15): não apaga; o original fica riscado com quem, quando e motivo; caixas voltam à custódia (MV estorno-consumo) */
const BEN_MOT_EST = ['Erro de digitação', 'Pesagem refeita', 'Outro'];
function benPartes(c, o, s) { if ((s.cons || []).length) return s.cons; const m = s.mv && (c.movs || []).find(x => x.id === s.mv);
  if (m && m.req && m.lote) return [{ req: m.req, lote: m.lote, qtd: s.cx, mv: m.id }]; const it = benReqItem(c, o); return it ? [{ req: o.req, lote: it.lote, qtd: s.cx, mv: s.mv || '' }] : []; }
function benEstornar(c, id, sid, motivo, texto, ator, k) { const quem = cenExige(ator, 'producao', 'Estornar ' + sid + ' da ' + id); const o = benO(c, id);
  const imp = JSON.stringify([id, sid, motivo || '', String(texto || '').trim()]); const ja = benRecibo(c, k, 'benEstornar', imp); if (ja) return ja; benVer(o, k);
  if (o.etapa === 'Encerradas') throw new Error('Correção de ordem encerrada é ajuste vinculado com alçada (BEN-7).');
  if (['Em execução', 'Em conferência'].indexOf(o.etapa) < 0) throw new Error('Estorne só em Em execução ou Em conferência (' + id + ' está em ' + o.etapa + ').');
  const s = o.ben.sai.find(x => x.id === sid); if (!s) throw new Error(sid + ' não está na ' + id + '.'); if (s.estorno) throw new Error('Registro já estornado (' + sid + ').');
  if (BEN_MOT_EST.indexOf(motivo) < 0) throw new Error('Escolha o motivo do estorno: ' + BEN_MOT_EST.join(', ') + '.');
  const mot = motivo === 'Outro' ? String(texto || '').trim() : motivo; if (!mot) throw new Error('Descreva o motivo do estorno.');
  const b0 = benBal(o); s.estorno = { quem, em: benEm(), motivo: mot }; let mv = '';
  /* as caixas voltam à custódia da linha e do lote de cada parte do consumo (BEN-REV-20261009-03), com ref ao movimento original */
  if (s.cx > 0) { const P = benPartes(c, o, s).map(p => ({ p, it: (c.reqs[p.req] ? c.reqs[p.req].itens : []).find(i => i.prod === BENC.cx.item && i.lote === p.lote) }));
    const sem = P.find(x => !x.it); if (!P.length || sem) throw new Error('Estorno de ' + sid + ': a linha de caixas ' + (sem ? sem.p.req + ' · ' + sem.p.lote : '') + ' não está na ' + id + '. Nada foi gravado.');
    const ids = P.map(x => { x.it.consumido -= x.p.qtd; x.it.custodia += x.p.qtd;
      return cenMov(c, { tipo: 'estorno-consumo', os: id, req: x.p.req, prod: BENC.cx.item, lote: x.p.lote, qtd: x.p.qtd, un: 'un', quem, origem: 'web', sinc: true, det: BENC.cx.item + ' ' + x.p.qtd, ref: x.p.mv || '' }).id; });
    mv = ids.join(', '); s.estorno.mv = ids[0]; if (ids.length > 1) s.estorno.mvs = ids; }
  const b1 = benBal(o); benBalMudou(o, quem); if (o.etapa === 'Em conferência') benCorrecao(o, quem, ator, b0, b1, mot);
  const det = mot + ' · diferença ' + benKg(b0.dif) + ' (' + benPct(b0.pct) + ') → ' + benKg(b1.dif) + ' (' + benPct(b1.pct) + ')' + (s.cx ? ' · ' + benUn(s.cx) + ' de caixa voltam à custódia' + (benPartes(c, o, s).length > 1 ? ' (' + benPartes(c, o, s).map(p => benUn(p.qtd) + ' ao ' + p.lote + ' · ' + p.req).join(', ') + ')' : '') : '');
  benHist(o, quem, 'Estorno de ' + sid, det, mv); benToca(o); const msg = sid + ' estornado: ' + det + '.'; benGravaRecibo(c, k, 'benEstornar', imp, msg); return { msg }; }
/* enviar para conferência (R-A08; o comando era "Concluir execução": verbo do efeito na rodada 1, como a O.S.): ≥ 1 saída de Produto com classe;
   no avanço "no Concluir" da rota o não registrado vira diferença; grava dif₀ */
function benConcluir(c, id, ator, k) { const quem = cenExige(ator, 'producao', 'Enviar a ' + id + ' para conferência'); const o = benO(c, id);
  if (o.etapa !== 'Em execução') throw new Error(BEN_FASES.indexOf(o.etapa) > 2 ? 'Já feito: ' + id + ' está em ' + o.etapa + '.' : id + ' não está em execução.'); benVer(o, k);
  if (!benValidos(o).some(s => s.fluxo === 'Produto' && s.classe)) throw new Error('Registre ao menos uma saída de Produto com classe antes de enviar para conferência.');
  const b = benBal(o); o.ben.conc = { quem, em: benEm(), dif0: b.dif }; o.etapa = 'Em conferência';
  /* reaberta (BEN-REV-04, BEN-D16): se o Concluir anterior estava fora da faixa e acima da alçada de quem corrige e agora entra na faixa,
     a correção feita pelo Reabrir só vale com a confirmação da gestão, como a correção na conferência (R-F07) */
  const d0 = o.ben.dif0r; let pend = '';
  if (d0 !== undefined && d0 !== null && prCmp(benAbs(d0), b.faixa) > 0 && b.dentro) { const al = benAlcada(o, d0);
    if (al.passa && !(typeof g2papel === 'function' && g2papel(ator, 'gestor'))) { o.ben.corrigido = true;
      o.ben.corr = { pend: true, quem, em: benEm(), motivo: 'execução reaberta e concluída de novo', antes: d0, depois: b.dif, msg: benCorrMsg(o, al, d0, 'no envio para conferência antes de reabrir') }; pend = o.ben.corr.msg; } }
  benHist(o, quem, 'Enviada para conferência', 'Entrada declarada processada; diferença no envio ' + benKg(b.dif) + ' (' + benPct(b.pct) + '), faixa ' + benKg(b.faixa) + (pend ? '; correção ' + pend + ': decide ' + benQuem('gestor') : '')); benToca(o);
  return { msg: id + ' em conferência: diferença ' + benKg(b.dif) + ' (' + benPct(b.pct) + ') contra a faixa de ' + benKg(b.faixa) + '. ' + (pend ? 'Correção ' + pend + ': decide ' + benQuem('gestor') + '.' : (b.dentro ? benQuem('conferente') + ' confere o balanço.' : 'Fora da faixa: justifique (alçada) ou corrija.')) }; }
const BEN_MOT_JUST = ['Erro de medição', 'Perda não identificada', 'Outro'];
function benJustificar(c, id, motivo, texto, ator, k) { const o = benO(c, id);
  const imp = JSON.stringify([id, motivo || '', String(texto || '').trim()]); const ja = benRecibo(c, k, 'benJustificar', imp); if (ja) return ja; benVer(o, k);
  if (o.etapa !== 'Em conferência') throw new Error('Justifique a diferença em Em conferência (' + id + ' está em ' + o.etapa + ').');
  const b = benBal(o); if (b.dentro) throw new Error('Diferença ' + benKg(b.dif) + ' dentro da faixa de ' + benKg(b.faixa) + ': confira o balanço, sem justificativa.');
  if (benJustOk(o, b)) throw new Error('Já feito: diferença justificada.');
  if (BEN_MOT_JUST.indexOf(motivo) < 0) throw new Error('Escolha o motivo: ' + BEN_MOT_JUST.join(', ') + '.');
  const tx = String(texto || '').trim(); if (!tx) throw new Error('Descreva a justificativa.');
  const al = benAlcada(o, b.dif); let quem;
  if (al.passa) { if (!(typeof g2papel === 'function' && g2papel(ator, 'gestor'))) throw new Error(al.msg + ': decide ' + benQuem('gestor') + '. Nada foi alterado.'); quem = cenExige(ator, 'gestor', 'Justificar a diferença da ' + id); }
  else quem = cenExigeUm(ator, ['producao', 'gestor'], 'Justificar a diferença da ' + id);
  o.ben.just.push({ motivo, texto: tx, quem, em: benEm(), dif: b.dif, alcada: al.passa ? al.msg : '' });
  benHist(o, quem, 'Diferença justificada', motivo + ': ' + tx + ' · ' + benKg(b.dif) + ' (' + benPct(b.pct) + ')' + (al.passa ? ' · acima da alçada do responsável de produção (' + al.msg + ')' : '')); benToca(o);
  const msg = 'Diferença de ' + benKg(b.dif) + ' da ' + id + ' justificada por ' + quem + ' (' + motivo + '). ' + benQuem('conferente') + ' confere o balanço.'; benGravaRecibo(c, k, 'benJustificar', imp, msg); return { msg }; }
function benConfirmarCorrecao(c, id, ator) { const quem = cenExige(ator, 'gestor', 'Confirmar a correção na conferência da ' + id); const o = benO(c, id);
  benViva(o, 'confirmar'); if (!o.ben.corr || !o.ben.corr.pend) throw new Error('Já feito: nenhuma correção aguarda a gestão na ' + id + '.');
  o.ben.corr.pend = false; o.ben.corr.conf = { quem, em: benEm() };
  benHist(o, quem, 'Correção na conferência confirmada', o.ben.corr.msg + ' · ' + o.ben.corr.motivo + ' (' + o.ben.corr.quem + ')'); benToca(o);
  return { msg: 'Correção da ' + id + ' confirmada por ' + quem + '. ' + benQuem('conferente') + ' confere o balanço.' }; }
/* padrão 2 (revisão CONF 13/10): com o CF-01, produção e conferência (ou qualidade) podem estar na mesma pessoa; quem registrou a produção e decide
   fica com revisão posterior pendente (não trava; como AL-09, AL-11 e AL-12). Dano evitado: balanço ou lote aprovado por quem o produziu, sem outro olhar. */
function benRevProd(o, ator, fato) { return benValidos(o).map(s => s.quem).concat((o.ben.hist || []).filter(h => h.ev === 'Enviada para conferência').map(h => h.quem))
  .map(q => cenRevisao(ator, q, fato)).find(Boolean) || ''; }
function benRevLote(c, L, ator) { const o = L && L.benef && (c.ordens || {})[L.benef]; if (!o || !o.ben) return ''; const ids = L.saidas || [];
  return (o.ben.sai || []).filter(s => ids.indexOf(s.id) >= 0 && !s.estorno).map(s => cenRevisao(ator, s.quem, 'registrou a saída do ' + L.id)).find(Boolean) || ''; }
function benConferir(c, id, ator, k) { const quem = cenExige(ator, 'conferente', 'Conferir o balanço da ' + id); const o = benO(c, id);
  if (o.etapa !== 'Em conferência') throw new Error('Confira o balanço em Em conferência (' + id + ' está em ' + o.etapa + ').');
  if (o.ben.conf) throw new Error('Já feito: balanço conferido por ' + o.ben.conf.quem + '.'); benVer(o, k);   /* confere o balanço que viu */
  if (o.ben.corr && o.ben.corr.pend) throw new Error('Correção na conferência ' + o.ben.corr.msg + ': decide ' + benQuem('gestor') + ' antes da conferência.');
  const b = benBal(o); if (!b.dentro && !benJustOk(o, b)) throw new Error('Diferença ' + benKg(b.dif) + ' (' + benPct(b.pct) + ') fora da faixa de ' + benKg(b.faixa) + ': justifique (alçada) ou corrija antes de conferir.');
  const rev = benRevProd(o, ator, 'registrou a produção da ' + id);
  o.ben.conf = Object.assign({ quem, em: benEm(), dif: b.dif }, rev ? { rev } : {});
  benHist(o, quem, 'Balanço conferido', 'diferença ' + benKg(b.dif) + ' (' + benPct(b.pct) + ')' + (b.dentro ? (b.ganho ? ', ganho aparente' : '') + ' dentro da faixa de ' + benKg(b.faixa) : ', justificada') + (rev ? ' · ' + rev : '')); benToca(o);
  return { msg: 'Balanço da ' + id + ' conferido por ' + quem + ': diferença ' + benKg(b.dif) + ' (' + benPct(b.pct) + ').' + (rev ? ' Fica ' + rev + '.' : '') + ' Próximo passo: Fechar processo.' }; }
function benReabrir(c, id, motivo, ator) { const quem = cenExige(ator, 'producao', 'Reabrir a execução da ' + id); const o = benO(c, id);
  if (o.etapa !== 'Em conferência') throw new Error(o.etapa === 'Em execução' ? 'Já feito: ' + id + ' está em Em execução.' : 'Reabra só em Em conferência (' + id + ' está em ' + o.etapa + ').');
  const mot = String(motivo || '').trim(); if (!mot) throw new Error('Informe o motivo para reabrir a execução.');
  const d0 = benDif0(o); benBalMudou(o, quem); o.ben.dif0r = d0; o.ben.conc = null; o.ben.corr = null; o.etapa = 'Em execução';
  benHist(o, quem, 'Execução reaberta', mot + ' · a declaração do envio para conferência cai; a diferença declarada (' + benKg(d0) + ') segue valendo para a alçada da correção'); benToca(o); return { msg: id + ' volta a Em execução (' + mot + ').' }; }
/* fechar processo (CMD-23; R-A09, R-A10): conferido, sem custódia, etapas exigidas cumpridas; cria os lotes Em inspeção com a
   genealogia, abre a inspeção, esgota as entradas e destina descarte e outro destino. Fechar não libera (R-E01) */
function benFechar(c, id, ator, k) { const quem = cenExige(ator, 'producao', 'Fechar a ' + id); const o = benO(c, id);
  if (o.etapa === 'Encerradas') throw new Error('Já feito: ' + id + ' encerrada.'); benVer(o, k);
  if (o.etapa !== 'Em conferência') throw new Error('Feche só em Em conferência (' + id + ' está em ' + o.etapa + ').');
  if (!o.ben.conf) throw new Error('Balanço ainda não conferido: ' + benQuem('conferente') + ' confere antes do fechamento.');
  const pe = cenPodeEncerrar(c, id); if (pe) throw new Error(pe);
  const et = benEtapas(c, o).filter(e => e.pert === 'Exigida' && e.sit !== 'Cumprida'); if (et.length) throw new Error('Etapa exigida pendente: ' + et.map(e => e.nome + ' (' + e.ev + ')').join('; ') + '.');
  const P = prP(c, 1); const r = benRota(o.ben.rota); const v = benValidos(o); const ents = o.ben.ent; const pesos = ents.map(e => e.kg); const Ls = ents.map(e => P.lotes[e.lote]);
  /* defesa (BEN-REV-01/02): o físico de cada entrada ainda cobre o que a ordem consome; senão a mesma massa iria a dois destinos */
  ents.forEach(e => { const f = prFis(c, e.lote); if (prCmp(f, e.kg) < 0) throw new Error('Fechar recusado: o ' + e.lote + ' tem ' + benKg(f) + ' e a ' + id + ' consome ' + benKg(e.kg) + ' (o lote mudou depois da liberação). Nada foi gravado.'); });
  const cls = {}; v.filter(s => s.fluxo === 'Produto').forEach(s => { (cls[s.lote] = cls[s.lote] || []).push(s); });
  Object.keys(cls).forEach(lid => { const L = P.lotes[lid]; if (L && L.benef !== id) throw new Error('Lote ' + lid + ' já existe (' + (L.benef || 'outra origem') + '): registre de novo para gerar outro destino.'); });
  const inspId = o.ben.insp || benInspId(c); const prazo = prDiaMais(prHoje(), r.par.prazo_insp || 2);
  const validade = Ls.map(L => L && L.validade).filter(Boolean).sort()[0] || null; const dcol = Ls.map(L => L && L.dcol).filter(Boolean).sort()[0] || null;
  const novos = [], movs = [];
  Object.keys(cls).forEach(lid => { const ss = cls[lid]; const kg = benSoma(ss); const cx = ss.reduce((a, s) => a + (s.cx || 0), 0); const parts = prRateio(kg, pesos);
    P.lotes[lid] = { id: lid, prod: ss[0].prod, cultura: r.cultura, classe: ss[0].classe, saf: (Ls[0] && Ls[0].saf) || '', faz: o.ben.faz, local: o.ben.local, drec: prHoje(), dcol, validade,
      q0: 'Em inspeção', cond: '', origem: ents.map((e, i) => ({ lote: e.lote, kg: parts[i], modo: 'rateio' })), cargas: [], benef: id, cx, insp: inspId, saidas: ss.map(s => s.id) };
    movs.push(prMov(c, { tipo: 'produção', lote: lid, kg, ordem: id, quem, obs: ss.map(s => s.id).join(', ') + ' · ' + cx + ' cx · ' + benRotaTxt(r) }).id); novos.push(lid); });
  v.filter(s => s.fluxo === 'Descarte' || s.fluxo === 'Outro destino' || s.fluxo === 'Perda identificada').forEach(s => { const parts = prRateio(s.kg, pesos);
    movs.push(prMov(c, { tipo: s.fluxo === 'Perda identificada' ? 'perda identificada' : 'destinação', lote: '', kg: s.kg, ordem: id, saida: s.id, fluxo: s.fluxo, destino: s.destino || s.causa,
      origem: ents.map((e, i) => ({ lote: e.lote, kg: parts[i], modo: 'rateio' })), quem, obs: s.fluxo + ' · ' + (s.destino || s.causa) + (s.ev.ticket ? ' · ticket ' + s.ev.ticket : '') }).id); });
  ents.forEach(e => { movs.push(prMov(c, { tipo: 'consumo no processo', lote: e.lote, kg: prSub(0, e.kg), ordem: id, quem, obs: 'entrada da ' + id }).id); P.lotes[e.lote].esg = id; });
  const B = benB(c, 1); const I = B.insp[inspId] || (B.insp[inspId] = { id: inspId, lotes: [], ordem: id, padrao: benRotaTxt(r) + ' · classes ' + ((r.saidas.find(s => s.fluxo === 'Produto') || {}).classes || []).join(' e ') + ' (sintético)', resp: benQualQ(), prazo: '', estado: 'Planejada', res: {} });
  I.lotes = novos; I.prazo = prazo; I.estado = 'Aberta'; I.ordem = id; I.resp = benQualQ(); o.ben.insp = inspId; o.etapa = 'Encerradas'; o.ben.fech = { quem, em: benEm() };
  const b = benBal(o);
  const dst = [prCmp(b.desc, 0) > 0 ? 'descarte ' + benKg(b.desc) : '', prCmp(b.outro, 0) > 0 ? 'outro destino ' + benKg(b.outro) : ''].filter(Boolean);
  const det = novos.map(l => l + ' ' + benKg(prFis(c, l))).join(' e ') + ' Em inspeção (' + inspId + ' · ' + benQualQ() + ' · prazo ' + prBr(prazo) + '); entradas esgotadas' + (dst.length ? '; ' + dst.join(' e ') + ' destinados' : '') + '; diferença ' + benKg(b.dif);
  benHist(o, quem, 'Processo fechado (CMD-23)', det, movs.join(', ')); benToca(o);
  return { msg: id + ' fechada: ' + det + '. Fechar não libera: a Qualidade libera em Produção › Estoque de produto.', lotes: novos }; }

/* ---------- qualidade do lote de produção (R-E02, R-E03): resultado e decisão; aprovar rota ≠ liberar ordem ≠ liberar lote ---------- */
const BEN_QUAL = ['qualidade', 'agronomo'];
function benInspDe(c, L) { return L && L.insp ? (benB(c).insp || {})[L.insp] || null : null; }
function benClassesDe(L) { const o = Object.values(BENC.rotas).find(r => (r.saidas || []).some(s => s.fluxo === 'Produto' && s.prod === L.prod)); return o ? o.saidas.find(s => s.fluxo === 'Produto' && s.prod === L.prod).classes : []; }
/* decisões possíveis no estado do lote: as opções seguem a situação do resultado (R-E02) */
function benDecisoes(c, L) { const I = benInspDe(c, L); const res = I && I.res[L.id]; const S = prSaldos(c, L); if (!I || S.esgotado || L.q0 === 'Destinado') return [];
  if (benPrende(c, L)) return [];   /* em processo numa ordem liberada: a decisão vale para os lotes de saída, depois do Fechar (BEN-REV-01) */
  if (L.q0 === 'Liberado' && (S.q === 'Liberado' || benBase(c, L).q === 'Liberado')) return ['Bloquear'].concat(benClassesDe(L).filter(x => x !== L.classe).length ? ['Reclassificar'] : [], ['Destinar']);
  if (!res) return [];
  return res.sit === 'Conforme' ? ['Liberar', 'Manter bloqueio', 'Destinar'] : ['Liberar como classe atingida', 'Manter bloqueio', 'Destinar']; }
/* próximo passo do lote de produção no Estoque de produto (null = vale a regra geral: reservar ou disponível) */
function benProxLote(c, L, S) { const I = benInspDe(c, L); if (!I) return null; const res = I.res[L.id]; const q = benQualQ();
  if (L.q0 === 'Destinado') return { t: 'destinado · rastreio guardado' };
  if (L.q0 === 'Liberado') return null;
  /* prazo da inspeção à vista (I11): vencida ou vence hoje no próprio texto do passo */
  const pz = !I.prazo ? '' : (I.prazo < prHoje() ? ' · ' + I.id + ' vencida em ' + prBr(I.prazo) : (I.prazo === prHoje() ? ' · ' + I.id + ' vence hoje' : ' · ' + I.id + ' até ' + prBr(I.prazo)));
  if (!res) return { t: 'Registrar resultado · ' + q + pz, a: 'resultado', insp: I.id, prazo: I.prazo };
  return { t: 'Registrar decisão · ' + q + pz, a: 'decisao', insp: I.id, prazo: I.prazo }; }
function benResultado(c, lid, sit, obs, ator) { const quem = cenExigeUm(ator, BEN_QUAL, 'Registrar o resultado do ' + lid); const L = prP(c, 1).lotes[lid]; const I = benInspDe(c, L);
  if (!I) throw new Error((L ? lid : 'Lote') + ' sem inspeção aberta.');
  if (I.res[lid]) throw new Error('Já feito: resultado do ' + lid + ' registrado (' + I.res[lid].sit + ', ' + I.res[lid].quem + ').');
  if (['Conforme', 'Não conforme'].indexOf(sit) < 0) throw new Error('Escolha o resultado: Conforme ou Não conforme.');
  const ob = String(obs || '').trim(); if (sit === 'Não conforme' && !ob) throw new Error('Descreva o que não conformou (vai para a decisão).');
  const rev = benRevLote(c, L, ator);
  I.res[lid] = Object.assign({ sit, obs: ob, quem, d: prHoje(), at: cenAgora() }, rev ? { rev } : {}); if ((I.lotes || []).every(x => I.res[x])) I.estado = 'Resultado registrado';
  const m = prMov(c, { tipo: 'resultado', lote: lid, kg: 0, fis: false, quem, obs: I.id + ' · ' + sit + (ob ? ': ' + ob : '') + (rev ? ' · ' + rev : '') });
  return { msg: 'Resultado do ' + lid + ' (' + I.id + '): ' + sit + ' por ' + quem + ' (' + m.id + ').' + (rev ? ' Fica ' + rev + '.' : '') + ' Próximo passo: Registrar decisão.' }; }
function benDecidir(c, lid, dec, k, ator) { const quem = cenExigeUm(ator, BEN_QUAL, dec + ' · ' + lid); const P = prP(c, 1); const L = P.lotes[lid]; if (!L) throw new Error('Lote não encontrado.');
  const I = benInspDe(c, L); if (!I) throw new Error(lid + ' sem inspeção: a decisão do lote de produção registra o resultado antes.');
  const res = I.res[lid]; const S = prSaldos(c, L); k = k || {}; const mot = String(k.motivo || '').trim();
  if (S.esgotado || L.q0 === 'Destinado') throw new Error('Já feito: ' + lid + ' sem saldo (destinado ou esgotado).');
  /* dano evitado: a mesma massa em dois destinos (destinada pela Qualidade e embalada pela ordem) */
  const pr = benPrende(c, L); if (pr) throw new Error(lid + ' em processo na ' + pr.id + ' (' + pr.etapa + '): decida depois do Fechar, sobre os lotes de saída (nascem Em inspeção). Nada foi gravado.');
  const pode = benDecisoes(c, L); const rev = benRevLote(c, L, ator); const nm0 = P.movs.length;
  if (dec === 'Liberar' && res && res.sit !== 'Conforme') throw new Error('Resultado não conforme (' + I.id + '): libere como classe atingida, mantenha o bloqueio ou destine.');
  if (dec === 'Liberar' && !res) throw new Error('Registre o resultado (' + I.id + ').');
  if (dec === 'Liberar' && L.q0 === 'Liberado') throw new Error('Já feito: ' + lid + ' liberado.');
  if (pode.indexOf(dec) < 0) throw new Error(!res ? 'Registre o resultado (' + I.id + ').' : dec + ' não se aplica ao ' + lid + ' agora (' + S.q + (res ? ', resultado ' + res.sit : '') + ').');
  let txt = '';
  if (dec === 'Liberar') { L.q0 = 'Liberado'; L.bloq = null; L.lib = { quem, d: prHoje(), at: cenAgora() }; txt = 'liberado (CMD-24)';
    prMov(c, { tipo: 'liberação', lote: lid, kg: 0, fis: false, quem, obs: I.id + ' · Conforme · CMD-24' }); }
  else if (dec === 'Liberar como classe atingida' || dec === 'Reclassificar') { const cs = benClassesDe(L).filter(x => x !== L.classe);
    if (cs.indexOf(k.classe) < 0) throw new Error('Escolha a classe atingida: ' + (cs.join(' ou ') || 'sem outra classe na rota') + '.');
    if (dec === 'Reclassificar' && !mot) throw new Error('Informe o motivo da reclassificação.');
    const antes = L.classe; L.classe = k.classe; L.q0 = 'Liberado'; L.bloq = null; L.lib = { quem, d: prHoje(), at: cenAgora() };
    prMov(c, { tipo: 'reclassificação', lote: lid, kg: 0, fis: false, quem, obs: 'classe ' + antes + ' → ' + k.classe + ' · mesma massa' + (mot ? ' · ' + mot : '') });
    if (dec === 'Liberar como classe atingida') prMov(c, { tipo: 'liberação', lote: lid, kg: 0, fis: false, quem, obs: I.id + ' · liberado como classe ' + k.classe + ' · CMD-24' });
    txt = (dec === 'Reclassificar' ? 'reclassificado' : 'liberado como classe atingida') + ': classe ' + antes + ' → ' + k.classe + ' (' + benKg(S.fis) + ', a massa não muda)'; }
  else if (dec === 'Bloquear' || dec === 'Manter bloqueio') { if (!mot) throw new Error('Informe o motivo do bloqueio.');
    L.q0 = 'Bloqueado'; L.bloq = { motivo: mot, prazo: k.prazo || '', quem, d: prHoje() };
    prMov(c, { tipo: 'bloqueio', lote: lid, kg: 0, fis: false, quem, obs: mot + (k.prazo ? ' · prazo ' + prBr(k.prazo) : '') }); txt = 'bloqueado (' + mot + ')'; }
  else if (dec === 'Destinar') { if (!mot) throw new Error('Informe o motivo da destinação.');
    prMov(c, { tipo: 'destinação', lote: lid, kg: prSub(0, S.fis), quem, obs: mot }); L.q0 = 'Destinado'; L.dest = { motivo: mot, quem, d: prHoje() }; txt = 'destinado: ' + benKg(S.fis) + ' saem do físico (' + mot + '); o rastreio fica'; }
  else throw new Error('Decisão desconhecida: ' + dec + '.');
  if (rev) { P.movs.slice(nm0).forEach(m => { m.obs = (m.obs ? m.obs + ' · ' : '') + rev; }); [L.lib, L.bloq, L.dest].forEach(x => { if (x && x.quem === quem) x.rev = rev; }); txt += ' · ' + rev; }
  if (I.lotes.indexOf(lid) >= 0 && I.lotes.every(x => P.lotes[x] && P.lotes[x].q0 !== 'Em inspeção')) I.estado = 'Decidida';
  const imp = Object.values(P.reservas).filter(r => r.lote === lid && r.st === 'Ativa' && (prSaldos(c, L).q !== 'Liberado' || !prCompat(P.pedidos[r.pedido] || {}, L)));
  return { msg: lid + ' ' + txt + ' por ' + quem + '.' + (imp.length ? ' Reserva ' + imp.map(r => r.id + ' (' + r.pedido + ')').join(', ') + ' continua Ativa com expedição impedida: o Comercial troca o lote ou cancela.' : '') }; }
/* genealogia para frente (R-E07): lotes e destinos que saíram de um lote, também com saldo 0 */
function benParaFrente(c, lid) { const P = prP(c); const out = [];
  Object.values(P.lotes).forEach(L => (L.origem || []).forEach(x => { if (x.lote === lid) out.push({ lote: L.id, prod: L.prod + (L.classe ? ' ' + L.classe : ''), kg: x.kg, modo: x.modo }); }));
  P.movs.filter(m => !m.lote && (m.origem || []).some(x => x.lote === lid)).forEach(m => { const x = m.origem.find(y => y.lote === lid); out.push({ lote: '', prod: m.fluxo + ' · ' + m.destino, kg: x.kg, modo: x.modo, mov: m.id }); });
  return out; }
/* gancho de teste e inspeção (o script da tela roda isolado) */
try { window.__ben = { benBal, benImpedimentos, benProx, benNova, benSaida, benFechar, benDecidir, benResultado }; } catch (e) {}
