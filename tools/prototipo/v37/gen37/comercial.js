/* ===== Comercial e logística (docs/comercial/ESPECIFICACAO.md v1.1; decisões D-C01..D-C25 em docs/comercial/DECISOES.md) =====
   Regras e comandos com* sobre c.producao, o mesmo estado da Colheita: venda (pronta ou futura), crédito, carga de saída (RM),
   saída física única, entrega, devolução e painel. Uma venda é o mesmo registro do pedido que o Estoque de produto reserva (D-C03).
   Carregado só nas três telas do grupo Comercial (D-C15), depois de cenario.js_prefixo() e do núcleo da carência (CE-01).
   Decimal pelas funções pr* (BigInt, ENG-013); valor em R$ com um arredondamento por evento, só em comValor (R-C01).
   Comentários só com barra-asterisco: o arquivo também entra em strings Python. */

/* ---------- unidade, valor e condição ---------- */
function comCulturaProd(prod) { const k = Object.keys(PRDC.un).find(x => PRDC.un[x].prod === prod); return k || ''; }
function comCultura(v) { return v.cultura || comCulturaProd(v.prod) || prCult(v.prod); }
function comUn(cultura) { return prEstUn(cultura); }   /* unidade comercial = a do estoque e a do preço (D-C05) */
function comTxt(cultura, base, d) { return prEstTxt(cultura, base, d); }
function comMassa(cultura) { const u = prUn(cultura); return u.est ? '1' : u.massa; }
/* valor = quantidade na unidade comercial × preço, um arredondamento (centavo, meio para cima): base × preço × 100 ÷ massa da unidade */
function comValorF(fat, base, preco) { const cents = prRd(prM(base) * prM(preco) * 100n, prM(fat) * PR_S); return prN(cents * 10000n); }
function comValor(cultura, base, preco) { return comValorF(comMassa(cultura), base, preco); }
/* A-17 (Codex 6070584991; DEC-0510-03 dimensional): a venda guarda a massa da sua unidade (fat, kg) e a origem; quantidade, preço e valor da
   venda usam essa massa, nunca a unidade atual da cultura. Legado com a massa ambígua (fatAmb, sem fatConf) mostra a quantidade do contrato
   e o físico em kg, e suspende só o que depende da massa (falta, oferta, saída, crédito), até a conversão registrada (comConverterSaca) */
function comFat(v) { return prFatV(v); }   /* texto e massa na unidade do compromisso: fonte única em producao.js (prFatV, prUnV, prTxtV) */
function comUnV(v) { return prUnV(v); }
function comTxtV(v, kg, d) { return prTxtV(v, kg, d); }
function comQtdTxt(v) { return (prAmb(v) && !v.enc) ? prQtdTxt(v) : comTxtV(v, v.qtd || 0); }
function comPrecoTxtV(v, preco) { return 'R$ ' + prFmt(preco === undefined ? v.preco : preco, 2) + '/' + comUnV(v) + (prAmb(v) ? ' (saca a conferir)' : ''); }
/* quantidade digitada na unidade da venda → base (A7 da revisão: devolução, reserva e carga usam a massa da venda, não a da cultura) */
function comBaseV(v, q) { const f = comFat(v); return f ? prMul(q, f) : prEstBase(comCultura(v), q); }
function comValorV(v, base) { const f = comFat(v); return f ? comValorF(f, base, v.preco) : null; }
/* valor do acordo = quantidade na unidade do contrato × preço (não depende da massa); um arredondamento */
function comValorQc(v) { if (v.qc === undefined || v.qc === null) return comValorV(v, v.qtd); const cents = prRd(prM(v.qc) * prM(v.preco) * 100n, PR_S * PR_S); return prN(cents * 10000n); }
function comRS(v) { return 'R$ ' + prFmt(v, 2); }
function comPrecoTxt(cultura, preco) { return 'R$ ' + prFmt(preco, 2) + '/' + comUn(cultura); }
function comSemanal(cultura) { return Object.values(PRDC.cult).some(k => k.cultura === cultura && k.semanal); }
function comNat(v) { return v.natureza || 'Venda'; }
/* condição com o evento do vencimento (R-C02): à vista na entrega = 0 d; N dias após a entrega comprovada; antecipado = antes da saída */
function comCond(t) { t = String(t || '');
  if (t === 'Antecipado') return { ant: true, dias: null, ev: 'pagamento antes da saída' };
  if (/^À vista na entrega/.test(t)) return { dias: 0, ev: 'na entrega' };
  const m = /^(\d+) dias após a entrega/.exec(t); if (m) return { dias: Number(m[1]), ev: m[1] + ' d após a entrega comprovada' };
  if (/^Liquidação em produto/.test(t)) return { prod: true, dias: null, ev: 'liquidação em produto (GE-08)' };
  return null; }
function comVenc(cond, d) { const k = comCond(cond); if (!k || k.dias === null || !d) return ''; return prDiaMais(d, k.dias); }
function comCp(nome) { return (COMC.cp || {})[nome] || null; }
function comModalCp(cp) { return /^Retira/.test(String((cp && cp.entrega) || '')) ? 'retira' : 'entrega'; }
const COM_MODAL = { retira: 'Cliente retira na fazenda', entrega: 'Agricultor organiza a entrega' };

/* ---------- estado (leitura não cria nada; comando cria a parte comercial num estado antigo) ---------- */
function comP(c) { const P = prP(c, 1); P.expedicoes = P.expedicoes || {}; P.seq.rm = P.seq.rm || 1; P.seq.pv = P.seq.pv || 38; P.seq.ct = P.seq.ct || 204; return P; }
function comRms(c, f) { return Object.values(prP(c).expedicoes || {}).filter(r => !f || f(r)); }
function comRmsVenda(c, vid) { return comRms(c, r => r.pedido === vid); }
function comResKg(c, vid) { return prSoma(prResPed(c, vid).map(r => r.kg)); }
function comIni(v) { return v.ini || (v.sem ? prSemIni(v.sem) : ''); }
function comRmDev(rm, lote) { return prSoma((rm.devs || []).filter(d => !lote || d.de === lote).map(d => d.kg)); }
/* lotes da carga somados por lote (A2 da revisão): uma carga antiga com o mesmo lote em duas linhas nunca baixa duas vezes a reserva */
function comLotesRm(rm) { const o = []; (rm.lotes || []).forEach(l => { const x = o.find(y => y.lote === l.lote); if (x) x.prev = prSoma([x.prev, l.prev]); else o.push({ lote: l.lote, prev: l.prev }); }); return o; }
/* carga programada sem reserva que a cubra (A5 da revisão): por lote, a reserva ativa da venda menos o previsto das cargas programadas
   anteriores (ordem do id); previsto acima disso = impedida (reserva cancelada, consumida por outra carga ou trocada de venda) */
function comRmDescoberto(c, rm) { if (rm.st !== 'Programada') return []; const ant = comRmsVenda(c, rm.pedido).filter(r => r.st === 'Programada' && r.id < rm.id); const out = [];
  comLotesRm(rm).forEach(l => { const rv = prSoma(prResPed(c, rm.pedido).filter(r => r.lote === l.lote).map(r => r.kg));
    const antes = prSoma([].concat(...ant.map(r => r.lotes.filter(x => x.lote === l.lote).map(x => x.prev)))); const cobre = prCmp(rv, antes) > 0 ? prSub(rv, antes) : 0;
    if (prCmp(l.prev, cobre) > 0) out.push({ lote: l.lote, prev: l.prev, cobre, falta: prSub(l.prev, cobre) }); });
  return out; }
function comRmLiq(rm) { return rm.saida ? prSub(rm.saida.liq, comRmDev(rm)) : 0; }
/* evento do vencimento da carga: Cliente retira = a saída (ponto contratado, PRD 48.2); Agricultor entrega = a entrega confirmada */
function comRmEvento(rm) { if (!rm.saida) return ''; if (rm.modal === 'retira') return rm.saida.d; return rm.entrega ? rm.entrega.d : ''; }
const COM_SITCOR = { 'Programada': 'blue', 'Em trânsito': 'yellow', 'Entregue': 'green', 'Entregue com devolução': 'yellow', 'Cancelada': 'gray' };

/* ---------- a receber (R-C09) e exposição de crédito (R-C08) ---------- */
/* um título por saída confirmada da natureza Venda (Antecipado fora), líquido de devolução; sem baixa no protótipo (D-C07) */
function comTitulos(c, f) { const P = prP(c); const out = [];
  comRms(c, rm => !!rm.saida && rm.st !== 'Cancelada').forEach(rm => { const v = P.pedidos[rm.pedido]; if (!v || comNat(v) !== 'Venda' || (comCond(v.cond) || {}).ant) return;
    const kg = comRmLiq(rm); if (prCmp(kg, 0) <= 0) return; const cu = comCultura(v); const ev = comRmEvento(rm);
    const t = { rm: rm.id, venda: v.id, cliente: v.cliente, prod: v.prod, cultura: cu, kg, valor: comValorV(v, kg) || 0, ev, venc: ev ? comVenc(v.cond, ev) : '', transito: !ev, dias: (comCond(v.cond) || {}).dias };
    if (!f || f(t)) out.push(t); });
  return out.sort((a, b) => (a.venc || '9') < (b.venc || '9') ? -1 : 1); }
function comVencido(t, hoje) { return !!t.venc && t.venc < (hoje || prHoje()); }
function comAReceber(c, f) { return prSoma(comTitulos(c, f).map(t => t.valor)); }
/* exposição do cliente: por venda (Venda, não antecipada), valor do expedido líquido + o extra pedido; um arredondamento por venda,
   para o centavo do arredondamento por saída não mudar a decisão de crédito (AC-13; D-C26) */
function comExpo(c, cliente, extra) { extra = extra || {}; let s = 0n;
  Object.values(prP(c).pedidos).filter(v => v.cliente === cliente && comNat(v) === 'Venda' && !(comCond(v.cond) || {}).ant).forEach(v => {
    const kg = prSoma([prExpedido(c, v.id), extra[v.id] || 0]); if (prCmp(kg, 0) > 0) s += prM(comValorV(v, kg) || 0); });
  return prN(s); }
/* a saída de kg da venda passa no crédito? cliente sem limite, limite vencido ou exposição acima do limite pedem a aprovação da gestora */
function comCredito(c, v, kg, hoje) { hoje = hoje || prHoje(); const r = { ok: true, prob: '', expo: 0, lim: null, aprov: null, ant: false };
  if (comNat(v) !== 'Venda') return r;
  if ((comCond(v.cond) || {}).ant) { r.ant = true; if (v.cred && v.cred.ant) { r.aprov = v.cred; return r; } r.ok = false; r.prob = 'pagamento antecipado do ' + v.id + ' não conferido'; return r; }
  const L = comCp(v.cliente) || {}; r.lim = L.lim || null; r.expo = comExpo(c, v.cliente, { [v.id]: kg });
  if (!L.lim) r.prob = v.cliente + ' sem limite de crédito no cadastro (CD-05)';
  else if (L.limv && L.limv < hoje) r.prob = 'limite de crédito de ' + v.cliente + ' vencido em ' + prBr(L.limv) + '/' + L.limv.slice(2, 4);
  else if (prCmp(r.expo, L.lim) > 0) r.prob = 'a receber de ' + v.cliente + ' + esta saída = ' + comRS(r.expo) + ', acima do limite de ' + comRS(L.lim);
  if (!r.prob) return r;
  if (v.cred && !v.cred.ant && prCmp(r.expo, v.cred.ate) <= 0) { r.aprov = v.cred; return r; }
  r.ok = false; if (v.cred && !v.cred.ant) r.prob += ' (a aprovação de ' + v.cred.quem + ' cobre até ' + comRS(v.cred.ate) + ')'; return r; }
/* aviso de crédito do cliente (formulário e linha): limite vencido ou ausente sem reservado é aviso, não "Aguardando crédito" (CE-07) */
function comAvisoCred(cliente, hoje) { const L = comCp(cliente) || {}; hoje = hoje || prHoje();
  if (!L.lim) return cliente + ' sem limite de crédito no CD-05: a saída pede a gestora';
  if (L.limv && L.limv < hoje) return 'limite de ' + cliente + ' vencido em ' + prBr(L.limv) + '/' + L.limv.slice(2, 4) + ': a saída pede a gestora';
  return ''; }

/* ---------- impedimento da saída (R-C07): a mesma conta para a venda, a carga e a saída (CE-07) ---------- */
function comNucleo() { return typeof CARD !== 'undefined' && typeof carAvaliar === 'function'; }
function comImpede(c, v, L) { const out = { imp: [], aviso: [], aval: [] }; const qual = prQuem('qual'); const com = g2quemUm(['comercial', 'gestor']);
  if (v && prAmb(v)) out.imp.push({ t: v.id + ': saca do contrato a conferir (' + v.fatAmb.join(' ou ') + ' kg): valor, crédito e falta dependem dela', q: com });
  else if (v && !v.enc && v.qtd !== null && v.qtd !== undefined) { const acima = prSub(prSoma([prExpedido(c, v.id), comResKg(c, v.id)]), v.qtd);
    if (prCmp(acima, 0) > 0) out.imp.push({ t: v.id + ': reservado acima da venda em ' + comTxtV(v, acima) + ' (cancele a reserva e reserve de novo)', q: com }); }
  if (!L) { out.imp.push({ t: 'lote não encontrado', q: qual }); return out; }
  /* sem o núcleo da carência na página, nada passa por falta de dado (CE-01) */
  if (!comNucleo()) { out.imp.push({ t: 'avaliação de carência e destino indisponível nesta página (núcleo da carência ausente): a saída não é avaliada', q: 'Suporte do protótipo' }); return out; }
  const S = prSaldos(c, L); if (S.q !== 'Liberado') out.imp.push({ t: L.id + ' ' + S.q.toLowerCase() + ': ' + S.mot, q: S.dono || qual });
  const dest = (v && v.dest) || 'MI-BR'; const orig = (L.origem || []).filter(x => !x.est);
  if (!orig.length) { if (L.abertura) out.aval.push({ lc: '', st: 'abertura', rot: 'origem anterior ao sistema' }); else out.imp.push({ t: L.id + ' sem origem registrada', q: qual }); }
  orig.forEach(x => { const lc = prLc(c, x.os, x.dcol);
    if (!lc) { out.imp.push({ t: L.id + ': origem ' + (x.os || '—') + ' colhida em ' + prBr(x.dcol) + ' sem lote de campo (falta o apontamento da data)', q: prResp((c.ordens || {})[x.os]) }); return; }
    if (out.aval.some(a => a.lc === lc)) return;
    const a = carAvaliar(c, lc, dest); out.aval.push({ lc, st: a.st, rot: a.rot });
    if (a.st === 'nao_conforme') { const m = a.motivos[0] || {}; out.imp.push({ t: lc + ' ' + a.rot + ': ' + (m.t || ''), q: m.q || qual }); }
    else if (a.st !== 'conforme') { const f = a.faltas[0] || {}; out.imp.push({ t: lc + ' ' + a.rot + ': ' + (f.t || 'sem avaliação'), q: f.q || qual }); } });
  if (S.vencido) out.aviso.push(L.id + ' vencido em ' + prBr(L.validade) + ' (aviso, não trava)');
  return out; }

/* ---------- situação da venda (R-C13 de situação; precedência do §3.1) ---------- */
function comPeriodoComecou(c, v, hoje) { hoje = hoje || prHoje(); if (v.tipo !== 'futura') return true;
  if (v.sem) return prSemIni(v.sem) <= hoje; return comSafColhida(c, v.prod, v.saf, hoje); }
function comNaoProg(c, vid, lote) { const res = prSoma(prResPed(c, vid).filter(r => !lote || r.lote === lote).map(r => r.kg));
  const prog = prSoma([].concat(...comRmsVenda(c, vid).filter(r => r.st === 'Programada').map(r => r.lotes.filter(l => !lote || l.lote === lote).map(l => l.prev))));
  const z = prSub(res, prog); return prCmp(z, 0) > 0 ? z : 0; }
function comSitVenda(c, v, hoje) { hoje = hoje || prHoje(); const st = prSitPed(c, v); const P = prP(c); const rs = prResPed(c, v.id); const res = comResKg(c, v.id); const falta = prFalta(c, v);
  const z = { t: st.t, c: st.c, imp: [], res, falta, cred: null };
  /* A4 da revisão: expedido ≥ vendido com carga ainda em trânsito não é entregue (o vencimento e o realizado contam da entrega) */
  if (st.t === 'Entregue' && comRmsVenda(c, v.id).some(r => r.st === 'Em trânsito')) return Object.assign(z, { t: 'Em trânsito', c: 'yellow' });
  if (st.t === 'Encerrada' || st.t === 'Entregue' || st.t === 'Saca a conferir') return z;
  z.imp = rs.map(r => ({ r, I: comImpede(c, v, P.lotes[r.lote]) })).filter(x => x.I.imp.length);
  if (z.imp.length) return Object.assign(z, { t: 'Em risco', c: 'red' });
  if (prCmp(res, 0) > 0) { const cr = comCredito(c, v, res, hoje); if (!cr.ok) return Object.assign(z, { t: 'Aguardando crédito', c: 'yellow', cred: cr }); }
  if (st.t === 'Em risco') return Object.assign(z, { t: prCmp(falta, 0) <= 0 ? 'Coberto' : (rs.length ? 'Parcial' : 'Sem reserva'), c: prCmp(falta, 0) <= 0 ? 'green' : 'yellow' });
  return z; }
/* lotes que a venda pode reservar (R-C05): aptos, compatíveis, com disponível; o que vence antes do início da janela fica fora (CE-08) */
function comLotesPara(c, v) { const ini = comIni(v);
  return Object.values(prP(c).lotes).filter(L => prCompat(v, L) && prCmp(prSaldos(c, L).disp, 0) > 0 && !(L.validade && ini && L.validade < ini)).sort((a, b) => a.id.localeCompare(b.id)); }

/* ---------- produtos, períodos e classe (R-C02, CE-02, CE-06) ---------- */
function comProdutos(c) { const P = prP(c); const s = new Set(Object.values(P.lotes).map(L => L.prod));
  Object.keys(PRDC.cult).forEach(cid => { if ((P.previsoes[cid] || []).length) s.add(prUn(PRDC.cult[cid].cultura).prod); });
  return [...s].filter(p => comCulturaProd(p)).sort(); }
/* produto do estado casado com os do CD-05 pela cultura ("Mamão Formosa classe A" → "Mamão Formosa · fruta de campo"); a classe vem dos lotes */
function comProdCp(cp) { return [...new Set(((cp && cp.prod) || []).map(n => { const cu = prCult(n); return PRDC.un[cu] ? PRDC.un[cu].prod : ''; }).filter(Boolean))]; }
function comClasse(c, prod) { const L = Object.values(prP(c).lotes).find(x => x.prod === prod && !x.dev); if (L) return L.classe || ''; const cu = comCulturaProd(prod); return cu && prUn(cu).grao ? 'Padrão' : ''; }
function comSafColhida(c, prod, sf, hoje) { hoje = hoje || prHoje();
  if (Object.values(prP(c).lotes).some(L => L.prod === prod && L.saf === sf && (L.origem || []).some(x => x.carga))) return true;
  return Object.values(PRDC.cult).some(k => !k.semanal && prUn(k.cultura).prod === prod && (PRDC.safras[k.saf] || {}).mf === sf && k.colheita && k.colheita <= hoje); }
/* safra de grão em colheita (A10 da revisão, D-C29; revê a D-C24): começou a ser colhida e algum cultivo dela ainda não fechou a colheita
   (prResultado.parcial: O.S. de colheita aberta ou carga a pesar). Enquanto isso, a previsão publicada ainda não colhida continua oferta,
   na linha do estoque da safra; colheita fechada, vale só o realizado (PRD 49.2). Sem versão publicada, nada a somar */
function comSafCultivos(prod, sf) { return Object.keys(PRDC.cult).filter(cid => { const k = PRDC.cult[cid]; return !k.semanal && prUn(k.cultura).prod === prod && (PRDC.safras[k.saf] || {}).mf === sf; }); }
function comColhido(c, prod, sf) { const P = prP(c); const ids = Object.values(P.lotes).filter(L => L.prod === prod && L.saf === sf && !L.dev && !L.abertura).map(L => L.id);
  return prSoma(P.movs.filter(m => ids.indexOf(m.lote) >= 0 && (m.tipo === 'recebimento' || m.tipo === 'estorno')).map(m => m.kg)); }
function comPrevRestante(c, prod, sf) { if (!sf) return null; const cids = comSafCultivos(prod, sf); if (!cids.length) return null;
  if (!cids.some(cid => { const R = prResultado(c, cid); return !R || R.parcial; })) return null;
  const o = prOfertaSafra(c, prod, sf); if (!o.tem) return null; const col = comColhido(c, prod, sf); const r = prSub(o.pub, col);
  return { pub: o.pub, col, rest: prCmp(r, 0) > 0 ? r : 0 }; }
function comSafrasFut(c, prod, hoje) { const out = [];
  Object.values(PRDC.cult).forEach(k => { if (k.semanal || prUn(k.cultura).prod !== prod) return; const sf = (PRDC.safras[k.saf] || {}).mf; if (sf && out.indexOf(sf) < 0) out.push(sf); });
  return out.filter(sf => !comSafColhida(c, prod, sf, hoje)).sort(); }
function comSemanasFut(hoje, n) { const s0 = prSem(hoje || prHoje()); return [1, 2, 3, 4, 5, 6].slice(0, n || 4).map(i => prSemMais(s0, i)); }
function comSafLotes(c, prod) { const s = [...new Set(Object.values(prP(c).lotes).filter(L => L.prod === prod && prCmp(prSaldos(c, L).disp, 0) > 0).map(L => L.saf || ''))]; return s.length === 1 ? s[0] : ''; }

/* =====================================================================================================================
   Comandos (sempre dentro de cenMudar): chave de quem inicia; mesma chave e mesmo conteúdo = mesmo registro; outro conteúdo = conflito
   ===================================================================================================================== */
/* registrar venda (R-C02, R-C04): só dois números digitados (quantidade e preço); o resto herdado do CD-05 ou por toque */
function comVender(c, k) { const P = comP(c);
  const imp = JSON.stringify([k.cliente || '', k.natureza || 'Venda', k.prod || '', k.tipo || '', k.ini || '', k.fim || '', k.sem || '', k.saf || '', prNum(k.qtd), prNum(k.preco), k.cond || '', k.modal || '']);
  if (k.chave) { const ja = Object.values(P.pedidos).find(p => p.chave === k.chave); if (ja) { if (ja.imp !== imp) throw prConflito(k.chave, ja.id); return { msg: 'Venda ' + ja.id + ' já registrada: nada foi gravado de novo.', v: ja, repetido: true }; } }
  const quem = cenExigeUm(k.ator, ['comercial', 'gestor'], 'Registrar venda');
  const cp = comCp(k.cliente); const nat = k.natureza || 'Venda';
  if (!cp) throw new Error('Escolha o cliente no cadastro de parceiros (CD-05).');
  if (nat === 'Venda' && cp.papeis.indexOf('Cliente') < 0) throw new Error(k.cliente + ' não tem o papel Cliente no CD-05.');
  if (nat !== 'Venda' && cp.papeis.indexOf('Fornecedor') < 0) throw new Error(nat + ' é com fornecedor: ' + k.cliente + ' não tem o papel Fornecedor no CD-05.');
  const cu = comCulturaProd(k.prod); if (!cu || comProdutos(c).indexOf(k.prod) < 0) throw new Error('Escolha o produto (com lote ou previsão no estado).');
  const tipo = k.tipo === 'futura' ? 'futura' : (k.tipo === 'pronta' ? 'pronta' : ''); if (!tipo) throw new Error('Escolha Pronta entrega ou Venda futura.');
  const hoje = prHoje(); let ini = '', fim = '', sem = '', saf = '', janela = '';
  if (tipo === 'pronta') { ini = String(k.ini || ''); fim = String(k.fim || k.ini || ''); const iso = /^\d{4}-\d\d-\d\d$/;
    if (!iso.test(ini) || !iso.test(fim)) throw new Error('Escolha a janela de entrega.'); if (fim < ini) throw new Error('A janela termina antes de começar.');
    if (fim < hoje) throw new Error('A janela de entrega já passou (' + prBr(fim) + ').');
    janela = prBr(ini) + (fim !== ini ? '–' + prBr(fim) : ''); saf = k.saf || comSafLotes(c, k.prod); }
  else if (comSemanal(cu)) { sem = String(k.sem || ''); if (!/^\d{4}-W\d\d$/.test(sem)) throw new Error('Escolha a semana da venda futura.');
    if (prSemIni(sem) <= hoje) throw new Error('A ' + prSemTxt(sem) + ' já começou: o que é colhido nela está no estoque. Venda como pronta entrega (CE-02).');
    ini = prSemIni(sem); fim = prDiaMais(ini, 6); janela = prSemTxt(sem) + ' (' + prBr(ini) + '–' + prBr(fim) + ')'; }
  else { saf = String(k.saf || ''); if (comSafrasFut(c, k.prod).indexOf(saf) < 0) throw new Error('Venda futura só para safra ainda não colhida' + (saf ? ': a ' + saf + ' já começou a ser colhida (CE-02).' : '.'));
    janela = 'safra ' + saf; }
  const q = prNumOk(k.qtd) ? prNum(k.qtd) : NaN; if (!(q > 0)) throw new Error('Informe a quantidade em ' + comUn(cu) + '.');
  const pr = prNumOk(k.preco) ? prNum(k.preco) : NaN; if (!(pr > 0)) throw new Error('Informe o preço em R$/' + comUn(cu) + '.');
  const cond = nat === 'Venda' ? (k.cond || cp.cond || '') : 'Liquidação em produto';
  if (!comCond(cond) || (nat === 'Venda' && comCond(cond).prod)) throw new Error('Informe a condição de pagamento com o evento do vencimento.');
  const modal = k.modal === 'retira' || k.modal === 'entrega' ? k.modal : comModalCp(cp);
  const local = k.local || (modal === comModalCp(cp) ? (cp.entrega || '') : '');   /* A11 da revisão: "Agricultor entrega" não grava "Retira no armazém" do CD-05 */
  const id = tipo === 'pronta' ? 'PV-' + String(P.seq.pv = P.seq.pv + 1).padStart(3, '0') : 'CT-' + String(P.seq.ct = P.seq.ct + 1);
  const fat = comMassa(cu); const un = comUn(cu);   /* A-17: a massa da unidade fica gravada na venda (não muda se o cadastro da cultura mudar) */
  const v = P.pedidos[id] = { id, cliente: k.cliente, prod: k.prod, cultura: cu, classe: comClasse(c, k.prod), saf, tipo, janela, sem, ini, fim, qtd: prMul(q, fat), qc: q, un, fat,
    fatOrig: 'unidade da cultura no registro: ' + un + (prUn(cu).est ? '' : ' de ' + prFmtT(fat, 3) + ' kg'), dest: 'MI-BR',
    preco: String(pr), natureza: nat, cond, modal, local, d: hoje, at: cenAgora(), quem, chave: k.chave || id, imp, obs: k.obs || '' };
  if (!sem) delete v.sem;
  const av = []; const ac = nat === 'Venda' ? comAvisoCred(k.cliente) : ''; if (ac) av.push('Aviso: ' + ac + '.');
  if (tipo === 'futura') { const o = sem ? prOfertaSem(c, k.prod, sem) : prOfertaSafra(c, k.prod, saf);
    if (o.livre === null) av.push('Aviso: a oferta da ' + (sem ? prSemTxt(sem) : 'safra ' + saf) + ' está suspensa até registrar a saca de ' + o.amb.join(', ') + ' (A-17): o déficit não é calculado.');
    else if (prCmp(o.livre, 0) < 0) av.push('Aviso: oferta da ' + (sem ? prSemTxt(sem) : 'safra ' + saf) + ' em déficit de ' + comTxt(cu, prSub(0, o.livre)) + (o.tem ? '' : ' (sem versão publicada)') + ': venda adiantada é decisão do produtor (D-C16).'); }
  return { msg: id + ' registrada: ' + v.cliente + ' · ' + comTxtV(v, v.qtd) + ' de ' + v.prod + ' a ' + comPrecoTxtV(v) + ' = ' + comRS(comValorQc(v)) + ' · '
    + (tipo === 'futura' ? 'venda futura ' + janela + ' (não desconta o estoque)' : 'pronta entrega ' + janela) + ' · ' + cond + '.' + (av.length ? ' ' + av.join(' ') : ''), v }; }

/* encerrar saldo (R-C11): motivo; recusa com carga programada; cancela as reservas ativas na mesma transação; quantidade vigente = expedido */
function comEncerrar(c, k) { const P = comP(c); const v = P.pedidos[k.venda]; if (!v) throw new Error('Escolha a venda.');
  if (v.enc) { if (k.chave && v.enc.chave === k.chave) return { msg: v.id + ' já encerrada: nada foi alterado.', repetido: true }; throw new Error(v.id + ' já está encerrada.'); }
  const quem = cenExigeUm(k.ator, ['comercial', 'gestor'], 'Encerrar saldo do ' + v.id);
  const mot = String(k.motivo || '').trim(); if (!mot) throw new Error('Informe o motivo do encerramento.');
  const pg = comRmsVenda(c, v.id).filter(r => r.st === 'Programada'); if (pg.length) throw new Error('Encerrar recusado: ' + pg.map(r => r.id).join(', ') + ' programada para o ' + v.id + '. Cancele a carga antes.');
  const rs = prResPed(c, v.id).map(r => r.id); rs.forEach(id => prCancelarReserva(c, id, 'saldo do ' + v.id + ' encerrado: ' + mot, k.ator));
  const exp = prExpedido(c, v.id); const era = comQtdTxt(v);
  v.enc = { motivo: mot, quem, d: prHoje(), at: cenAgora(), qtd0: v.qtd, qc0: v.qc, chave: k.chave || '' }; v.qtd = prCmp(exp, 0) > 0 ? exp : 0;
  if (comFat(v)) v.qc = prDiv(v.qtd, comFat(v));
  return { msg: v.id + ' encerrada (' + mot + ') por ' + quem + ': quantidade vigente ' + comTxtV(v, v.qtd) + ' (era ' + era + ')' + (rs.length ? '; reservas canceladas: ' + rs.join(', ') : '') + '.' }; }

/* aprovar crédito (R-C08): só a gestora; vale até o valor coberto (a receber + reservado não expedido da venda, ou a saída pesada que a
   aprovação anterior não cobria, k.kg: excesso de peso, KC18); antecipado = pagamento conferido */
function comAprovarCredito(c, k) { const P = comP(c); const v = P.pedidos[k.venda]; if (!v) throw new Error('Escolha a venda.');
  const ant = !!(comCond(v.cond) || {}).ant; const acao = ant ? 'Conferir o pagamento antecipado do ' + v.id : 'Aprovar crédito do ' + v.id;
  const res = comResKg(c, v.id); const kg = prNumOk(k.kg) && prCmp(prNum(k.kg), res) > 0 ? prNum(k.kg) : res;
  /* A9 da revisão: a aprovação guarda o que cobre (venda e kg); a mesma chave com outro peso é conflito, nunca "já registrado" que não cobre */
  const imp = JSON.stringify([v.id, ant ? 'antecipado' : prNum(kg)]);
  if (k.chave && v.cred && v.cred.chave === k.chave) { if (v.cred.imp !== undefined && v.cred.imp !== imp) throw prConflito(k.chave, v.id);
    return { msg: acao + ': já registrado por ' + v.cred.quem + '; nada foi gravado de novo.', repetido: true }; }
  const quem = cenExige(k.ator, 'gestor', acao);
  if (comNat(v) !== 'Venda') throw new Error(v.id + ' é ' + comNat(v) + ': liquidação em produto, sem crédito a aprovar.');
  const ate = ant ? null : comExpo(c, v.cliente, { [v.id]: kg });
  const rev = cenRevisao(k.ator, v.quem, 'registrou a venda');
  v.cred = { quem, d: prHoje(), at: cenAgora(), ate, ant, rev, chave: k.chave || '', imp };
  return { msg: ant ? 'Pagamento antecipado do ' + v.id + ' conferido por ' + quem + ': a saída passa no crédito e a venda fica fora do a receber.' + (rev ? ' ' + rev + '.' : '')
                    : 'Crédito do ' + v.id + ' aprovado por ' + quem + ' até ' + comRS(ate) + ' (a receber de ' + v.cliente + ' + reservado não expedido).' + (rev ? ' ' + rev + '.' : '') }; }

/* registrar a saca do contrato (A-17): legado com a massa ambígua (fatAmb) ganha a conversão auditável (massa escolhida entre as do
   conflito, fonte, quem e quando); a quantidade do contrato (qc) fica e o kg nasce dela. Quem: comercial ou gestora (R-C14). Uma vez só:
   mudar depois pede encerrar e registrar outra venda (D-C21) */
function comConverterSaca(c, k) { const P = comP(c); const v = P.pedidos[k.venda]; if (!v) throw new Error('Escolha a venda.');
  const fat = String(k.fat || '').trim(); const fonte = String(k.fonte || '').trim(); const imp = JSON.stringify([v.id, fat, fonte]);
  if (v.fatConf) { if (k.chave && v.fatConf.chave === k.chave) { if (v.fatConf.imp !== imp) throw prConflito(k.chave, v.id); return { msg: 'Saca do ' + v.id + ' já registrada: nada foi alterado.', repetido: true }; }
    throw new Error('Saca do ' + v.id + ' já registrada: ' + v.fatConf.fat + ' kg, por ' + v.fatConf.quem + ' em ' + prBr(v.fatConf.d) + ' (' + v.fatConf.fonte + '). Nada foi alterado.'); }
  if (!v.fatAmb) throw new Error(v.id + ' já tem a massa da unidade gravada no registro (' + comUnV(v) + '): nada a converter.');
  if (v.enc) throw new Error(v.id + ' está encerrada: a quantidade vigente é o entregue (' + comTxtV(v, v.qtd || 0) + '). Nada foi alterado.');
  const quem = cenExigeUm(k.ator, ['comercial', 'gestor'], 'Registrar a saca do ' + v.id);
  if (v.fatAmb.indexOf(fat) < 0) throw new Error('Escolha a massa da saca escrita no contrato: ' + v.fatAmb.map(x => x + ' kg').join(' ou ') + '.');
  if (!fonte) throw new Error('Informe onde está a massa da saca (ex.: contrato ' + (v.ref || v.id) + ', cláusula da quantidade).');
  v.fatConf = { fat, fonte, quem, d: prHoje(), at: cenAgora(), chave: k.chave || ('W-SACA-' + v.id), imp }; v.fat = fat; v.qtd = prMul(v.qc, fat);
  const acima = prSub(prSoma([prExpedido(c, v.id), comResKg(c, v.id)]), v.qtd);
  const of = v.tipo === 'futura' ? (v.sem ? prOfertaSem(c, v.prod, v.sem) : prOfertaSafra(c, v.prod, v.saf)) : null;
  return { msg: v.id + ': saca de ' + fat + ' kg registrada por ' + quem + ' (' + fonte + '): ' + prFmtT(v.qc, 3) + ' ' + (v.un || 'sc') + ' = ' + prFmtT(v.qtd, 3) + ' kg'
    + (v.tipo === 'pronta' ? '; falta ' + comTxtV(v, prFalta(c, v)) : '')
    + (prCmp(acima, 0) > 0 ? '. Reservado acima da venda em ' + comTxtV(v, acima) + ': cancele a reserva e reserve de novo' : '')
    + (of ? (of.livre === null ? '; a oferta da ' + (v.sem ? prSemTxt(v.sem) : 'safra ' + v.saf) + ' continua suspensa até registrar ' + of.amb.join(', ') : '; oferta livre da ' + (v.sem ? prSemTxt(v.sem) : 'safra ' + v.saf) + ' ' + comTxt(comCultura(v), of.livre)) : '') + '.', v }; }

/* programar carga (R-C06): venda com reserva; previsto ≤ reserva ainda não programada; ≤ capacidade; veículo compatível */
function comVeic(t) { return (COMC.veic || []).find(x => x.t === t) || null; }
function comVeicOk(cultura, t) { const x = comVeic(t); if (!x) return false; const u = prUn(cultura); return u.vida ? x.tipo === 'refrigerado' : (u.grao ? x.tipo === 'graneleiro' : true); }
function comVeicsPara(cultura, transp) { const cp = comCp(transp); const base = (COMC.veic || []).filter(x => comVeicOk(cultura, x.t)).map(x => x.t);
  return (cp && cp.veic && cp.veic.length) ? base.filter(t => cp.veic.indexOf(t) >= 0) : base; }
/* previsto sugerido da carga: mín(reserva ainda não programada da venda, capacidade do veículo) (KC11) */
function comSugPrev(c, vid, veic, lote) { const np = comNaoProg(c, vid, lote); const x = comVeic(veic); return x && prCmp(np, x.cap) > 0 ? x.cap : np; }
function comTransps() { return Object.values(COMC.cp || {}).filter(p => p.papeis.indexOf('Transportador') >= 0).map(p => p.nome).concat(['Frota própria']); }
function comProgramar(c, k) { const P = comP(c);
  const ls0 = (k.lotes || []).map(l => ({ lote: l.lote, prev: prNumOk(l.prev) ? prNum(l.prev) : NaN }));
  const imp = JSON.stringify([k.venda, ls0.map(l => [l.lote, l.prev]), k.veic || '', k.transp || '', String(k.placa || '').trim().toUpperCase(), k.dprev || '']);
  if (k.chave) { const ja = Object.values(P.expedicoes).find(r => r.chave === k.chave); if (ja) { if (ja.imp !== imp) throw prConflito(k.chave, ja.id); return { msg: 'Carga ' + ja.id + ' já programada: nada foi gravado de novo.', rm: ja, repetido: true }; } }
  const quem = cenExigeUm(k.ator, ['comercial', 'expedicao', 'gestor'], 'Programar carga' + (k.venda ? ' do ' + k.venda : ''));
  const v = P.pedidos[k.venda]; if (!v) throw new Error('Escolha a venda.'); if (v.enc) throw new Error(v.id + ' está encerrada.');
  if (prAmb(v)) throw new Error(v.id + ': saca do contrato a conferir (' + v.fatAmb.join(' ou ') + ' kg): registre a massa com a fonte antes de programar a carga (A-17). Nada foi gravado.');
  const cu = comCultura(v); if (!prResPed(c, v.id).length) throw new Error(v.id + ' sem reserva ativa: reserve lote antes de programar a carga.');
  const ls = ls0.filter(l => !(prCmp(l.prev, 0) === 0)); if (!ls.length) throw new Error('Informe o previsto de ao menos um lote reservado.');
  /* A2 da revisão: o limite é por lote; o mesmo lote em duas linhas passaria duas vezes pela reserva e baixaria a de outra venda */
  const dupL = ls.map(l => l.lote).filter((x, i, a) => a.indexOf(x) !== i); if (dupL.length) throw new Error('Lote repetido na carga (' + dupL[0] + '): informe o previsto de cada lote uma vez. Nada foi gravado.');
  ls.forEach(l => { if (!(l.prev > 0)) throw new Error('Previsto do ' + l.lote + ' inválido.'); const np = comNaoProg(c, v.id, l.lote);
    if (prCmp(l.prev, np) > 0) throw new Error('Previsto do ' + l.lote + ' acima da reserva ainda não programada do ' + v.id + ' nesse lote (' + comTxtV(v, np) + ').'); });
  const x = comVeic(k.veic); if (!x) throw new Error('Escolha o veículo.');
  if (!comVeicOk(cu, k.veic)) throw new Error(k.veic + ' não serve para ' + v.prod + ': ' + (prUn(cu).vida ? 'fruta vai em baú refrigerado' : 'grão vai em graneleiro') + '.');
  const tot = prSoma(ls.map(l => l.prev)); if (prCmp(tot, x.cap) > 0) throw new Error('Previsto de ' + prFmtT(tot, 2) + ' kg acima da capacidade do ' + k.veic + ' (' + prFmtT(x.cap, 0) + ' kg).');
  const placa = String(k.placa || '').trim().toUpperCase(); if (!placa) throw new Error('Informe a placa do veículo.');
  const modal = v.modal || 'retira'; if (modal === 'entrega' && !k.transp) throw new Error('Escolha o transportador (ou Frota própria).');
  const dprev = k.dprev || prHoje(); if (dprev < prHoje()) throw new Error('A data prevista não pode ser antes de hoje.');
  P.seq.rm = P.seq.rm + 1; const id = 'RM-' + String(P.seq.rm).padStart(4, '0');
  const rm = P.expedicoes[id] = { id, pedido: v.id, lotes: ls.map(l => ({ lote: l.lote, prev: l.prev, kg: 0 })), modal, local: v.local || '', transp: modal === 'retira' ? v.cliente : k.transp,
    veic: k.veic, placa, dprev, st: 'Programada', saida: null, entrega: null, devs: [], canc: null, d: prHoje(), at: cenAgora(), quem, chave: k.chave || id, imp };
  return { msg: id + ' programada por ' + quem + ': ' + v.id + ' (' + v.cliente + ') · ' + rm.lotes.map(l => l.lote + ' ' + prFmtT(l.prev, 2) + ' kg').join(' + ') + ' = ' + comTxtV(v, tot) + ' · ' + k.veic + ' ' + placa
    + ' · ' + (modal === 'retira' ? 'cliente retira' : rm.transp) + ' · ' + prBr(dprev) + '. Próximo passo: confirmar a saída com a pesagem.', rm }; }
function comCancelarCarga(c, k) { const P = comP(c); const rm = P.expedicoes[k.rm]; if (!rm) throw new Error('Carga ' + k.rm + ' não encontrada.');
  if (rm.st === 'Cancelada' && k.chave && (rm.canc || {}).chave === k.chave) return { msg: rm.id + ' já cancelada: nada foi alterado.', repetido: true };
  if (rm.st !== 'Programada') throw new Error('Só carga programada é cancelada (' + rm.id + ' está ' + rm.st.toLowerCase() + ').');
  const quem = cenExigeUm(k.ator, ['comercial', 'expedicao', 'gestor'], 'Cancelar a ' + rm.id);
  const mot = String(k.motivo || '').trim(); if (!mot) throw new Error('Informe o motivo do cancelamento da carga.');
  rm.st = 'Cancelada'; rm.canc = { motivo: mot, quem, d: prHoje(), at: cenAgora(), chave: k.chave || '' };
  return { msg: rm.id + ' cancelada (' + mot + ') por ' + quem + ': as reservas do ' + rm.pedido + ' continuam; nada saiu do estoque.' }; }

/* confirmar saída (R-C07): uma vez, com pesagem; lote apto e destino conforme; até a reserva da venda no lote; excesso só do disponível com a gestora */
function comSair(c, k) { const P = comP(c); const rm = P.expedicoes[k.rm]; if (!rm) throw new Error('Carga ' + k.rm + ' não encontrada.');
  const kgs = k.kgs || null; const imp = JSON.stringify([k.rm, prNum(k.bruto), prNum(k.tara), kgs ? Object.keys(kgs).sort().map(l => [l, prNum(kgs[l])]) : null]);
  if (rm.saida) { if (k.chave && rm.saida.chave === k.chave) { if (rm.saida.imp !== imp) throw prConflito(k.chave, rm.id); return { msg: 'Saída da ' + rm.id + ' já confirmada: nada foi baixado de novo.', rm, repetido: true }; }
    throw new Error('Saída da ' + rm.id + ' já confirmada em ' + prBr(rm.saida.d) + ' ' + (rm.saida.at || '') + ' por ' + rm.saida.quem + ': nada foi baixado de novo.'); }
  if (rm.st !== 'Programada') throw new Error(rm.id + ' está ' + rm.st.toLowerCase() + ': só carga programada sai.');
  const quem = cenExigeUm(k.ator, ['expedicao', 'gestor'], 'Confirmar saída da ' + rm.id);
  const v = P.pedidos[rm.pedido]; const cu = comCultura(v);
  if (!prNumOk(k.bruto) || !(prNum(k.bruto) > 0)) throw new Error('Informe o peso bruto em kg.');
  if (!prNumOk(k.tara) || prNum(k.tara) < 0) throw new Error('Informe a tara em kg (0 ou mais).');
  const liq = prSub(prNum(k.bruto), prNum(k.tara)); if (prCmp(liq, 0) <= 0) throw new Error('Líquido (bruto − tara) tem de ser maior que zero: confira bruto e tara.');
  const lsR = comLotesRm(rm);   /* A2 da revisão: um lote, uma linha (carga antiga com lote repetido não baixa a reserva duas vezes) */
  let por; if (lsR.length === 1) por = [{ lote: lsR[0].lote, kg: liq }];
  else { if (!kgs) throw new Error('Informe os kg de cada lote (a soma é o líquido).'); por = lsR.map(l => ({ lote: l.lote, kg: prNumOk(kgs[l.lote]) ? prNum(kgs[l.lote]) : 0 })).filter(x => prCmp(x.kg, 0) > 0);
    const s = prSoma(por.map(x => x.kg)); if (prCmp(s, liq) !== 0) throw new Error('A soma dos lotes (' + prFmtT(s, 2) + ' kg) tem de ser o líquido pesado (' + prFmtT(liq, 2) + ' kg).'); }
  const exc = [];
  por.forEach(x => { const L = P.lotes[x.lote]; const I = comImpede(c, v, L);
    if (I.imp.length) throw new Error('Saída recusada: ' + I.imp[0].t + '. Quem resolve: ' + I.imp[0].q + '. Nada foi alterado.');
    const rv = prSoma(prResPed(c, v.id).filter(r => r.lote === x.lote).map(r => r.kg));
    if (prCmp(x.kg, rv) > 0) { const e = prSub(x.kg, rv); const S = prSaldos(c, L);
      if (prCmp(e, S.disp) > 0) throw new Error('Saída recusada: ' + comTxtV(v, x.kg) + ' do ' + x.lote + ' passam a reserva do ' + v.id + ' (' + comTxtV(v, rv) + ') em ' + comTxtV(v, e) + ' e o disponível do lote é ' + comTxtV(v, S.disp) + ': o excesso nunca sai da reserva de outra venda. Nada foi alterado.');
      exc.push({ lote: x.lote, kg: e }); } });
  let excQuem = '';
  if (exc.length) { if (!g2papel(k.ator, 'gestor')) throw new Error('Excesso de ' + exc.map(e => comTxtV(v, e.kg) + ' no ' + e.lote).join(', ') + ' sobre a reserva do ' + v.id + ' (ajuste autorizado, PRD 48.4): decisão de ' + g2quem('gestor') + '. Nada foi alterado.');
    excQuem = g2ator(k.ator, 'gestor'); }
  const cr = comCredito(c, v, liq); if (!cr.ok) throw new Error('Saída da ' + rm.id + ' recusada no crédito: ' + cr.prob + '. ' + (cr.ant ? 'Conferir o pagamento antecipado' : 'Aprovar crédito do ' + v.id) + ': decisão de ' + g2quem('gestor') + '. Nada foi alterado.');
  const d = prHoje(), at = cenAgora(); const aval = [];
  por.forEach(x => { const L = P.lotes[x.lote]; const I = comImpede(c, v, L); aval.push({ lote: x.lote, av: I.aval.map(a => (a.lc ? a.lc + ' ' : '') + a.rot), aviso: I.aviso });
    prMov(c, { tipo: 'expedição', lote: x.lote, kg: prSub(0, x.kg), pedido: v.id, rm: rm.id, quem, d, at });
    let f = x.kg; prResPed(c, v.id).filter(r => r.lote === x.lote).sort((a, b) => a.id.localeCompare(b.id)).forEach(r => { if (prCmp(f, 0) <= 0) return;
      const t = prCmp(r.kg, f) <= 0 ? r.kg : f; if (r.kg0 === undefined) r.kg0 = r.kg; r.kg = prSub(r.kg, t); r.exp = prSoma([r.exp || 0, t]); f = prSub(f, t);
      if (prCmp(r.kg, 0) <= 0) { r.kg = 0; r.st = 'Expedida'; } });
    const l = rm.lotes.find(y => y.lote === x.lote); if (l) l.kg = x.kg;
    /* pós-condição (A2 da revisão): o físico do lote nunca fica abaixo do reservado; se ficar, a saída comeu a reserva de outra venda */
    const fis = prFis(c, x.lote), res = prResLote(c, x.lote);
    if (prCmp(fis, res) < 0) throw new Error('Saída recusada: o ' + x.lote + ' ficaria com ' + comTxtV(v, fis) + ' de físico abaixo do reservado (' + comTxtV(v, res) + '): o que passa da reserva do ' + v.id + ' nunca sai da reserva de outra venda. Nada foi alterado.'); });
  rm.saida = { bruto: prNum(k.bruto), tara: prNum(k.tara), liq, d, at, quem, chave: k.chave || ('W-SAI-' + rm.id), imp, aval,
    cred: cr.aprov ? { quem: cr.aprov.quem, ate: cr.aprov.ate, ant: !!cr.aprov.ant } : null, exc: exc.length ? { kg: prSoma(exc.map(e => e.kg)), lotes: exc, quem: excQuem } : null };
  if (rm.modal === 'retira') { rm.st = 'Entregue'; rm.entrega = { d, at, quem, comp: 'retirada na fazenda (ponto contratado)', chave: rm.saida.chave, imp: '' }; } else rm.st = 'Em trânsito';
  const prevT = prSoma(rm.lotes.map(l => l.prev)); const outras = comRmsVenda(c, v.id).filter(r => r.st === 'Programada' && r.id !== rm.id && comRmDescoberto(c, r).length).map(r => r.id);
  const avPrev = prCmp(liq, prevT) > 0 ? ' Aviso: líquido ' + comTxtV(v, prSub(liq, prevT)) + ' acima do previsto (' + comTxtV(v, prevT) + ')' + (outras.length ? ': ' + outras.join(', ') + ' fica sem reserva que a cubra (reservar de novo ou cancelar a carga).' : '.') : '';   /* A5 da revisão */
  const val = comValorV(v, liq); const venc = rm.modal === 'retira' ? comVenc(v.cond, d) : ''; const S1 = por.map(x => x.lote + ' disponível ' + comTxt(cu, prSaldos(c, P.lotes[x.lote]).disp));
  const ant = (comCond(v.cond) || {}).ant;
  return { msg: rm.id + ': saída de ' + prFmtT(liq, 2) + ' kg (' + prFmtT(prNum(k.bruto), 2) + ' − ' + prFmtT(prNum(k.tara), 2) + ')' + (u => u.est ? '' : ' = ' + comTxtV(v, liq))(prUn(cu)) + ' para o ' + v.id + ' (' + v.cliente + ')'
    + (exc.length ? ', com ' + comTxtV(v, rm.saida.exc.kg) + ' de excesso autorizado por ' + excQuem : '') + '. '
    + (rm.modal === 'retira' ? 'Entregue na retirada' : 'Em trânsito: confirmar a entrega') + (comNat(v) !== 'Venda' ? ' · liquidação em produto.' : (ant ? ' · pagamento antecipado conferido.' : ' · ' + comRS(val) + ' a receber' + (venc ? ' até ' + prBr(venc) : ' (' + (comCond(v.cond) || {}).ev + ')') + '.'))
    + ' ' + S1.join(' · ') + '.' + avPrev, rm }; }

/* devolução (R-C10): lote novo Em inspeção, origem sem carga e sem kg (CE-11), MP de devolução; só a Qualidade libera */
function comDevolverEf(c, rm, lote, kg, motivo, quem, d, chave, imp) { const P = prP(c); const v = P.pedidos[rm.pedido]; const cu = comCultura(v);
  const l = lote ? rm.lotes.find(x => x.lote === lote) : rm.lotes.find(x => prCmp(x.kg, 0) > 0); if (!l) throw new Error('Escolha o lote da carga.');
  const q = prNumOk(kg) ? prNum(kg) : NaN; if (!(q > 0)) throw new Error('Informe a quantidade devolvida.');
  const max = prSub(l.kg, comRmDev(rm, l.lote)); if (prCmp(q, max) > 0) throw new Error('Devolução acima do entregue: no máximo ' + comTxtV(v, max) + ' do ' + l.lote + ' na ' + rm.id + '.');
  if ((COMC.motivos || []).indexOf(motivo) < 0) throw new Error('Escolha o motivo da devolução.');
  const L0 = P.lotes[l.lote]; const id = prNovoLote(c, d);
  const L = P.lotes[id] = { id, prod: L0.prod, cultura: L0.cultura, classe: L0.classe, saf: L0.saf, faz: L0.faz, local: L0.local, drec: d, dcol: L0.dcol, validade: L0.validade,
    q0: 'Em inspeção', cond: 'Devolvido', misto: !!L0.misto, origem: (L0.origem || []).filter(x => !x.est).map(x => ({ os: x.os, cult: x.cult, tal: x.tal, dcol: x.dcol, dev: { lote: L0.id, rm: rm.id } })),
    cargas: [], dev: { lote: L0.id, rm: rm.id, motivo } };
  if (L0.abertura) L.abertura = true;
  prMov(c, { tipo: 'devolução', lote: id, kg: q, pedido: v.id, rm: rm.id, quem, obs: motivo, d });
  const dv = { lote: id, de: l.lote, kg: q, motivo, d, at: cenAgora(), quem, chave: chave || ('W-DEV-' + id), imp: imp || '' }; rm.devs = (rm.devs || []).concat([dv]); rm.st = 'Entregue com devolução';
  if (v.enc) { v.qtd = prSub(v.qtd, q); if (comFat(v)) v.qc = prDiv(v.qtd, comFat(v)); }   /* venda encerrada: a quantidade vigente cai junto, sem reabrir falta (R-C10); a do contrato também (A8 da revisão: o valor do acordo segue o vigente) */
  return dv; }
function comEntregar(c, k) { const P = comP(c); const rm = P.expedicoes[k.rm]; if (!rm) throw new Error('Carga ' + k.rm + ' não encontrada.');
  const imp = JSON.stringify([k.rm, k.d || '', k.dev ? [prNum(k.dev.kg), k.dev.motivo || ''] : null]);
  /* COM-IDEM-01: a origem da devolução confere pela origem efetiva gravada (vale também para recibos antigos, cuja impressão não tem o lote):
     outro lote pedido com a mesma chave é conflito; sem lote (seleção automática) vale a origem gravada; sem a devolução gravada não há como provar: conflito */
  if (rm.entrega) { if (k.chave && rm.entrega.chave === k.chave) { if (rm.entrega.imp !== imp) throw prConflito(k.chave, rm.id);
      if (k.dev && k.dev.lote) { const dv0 = (rm.devs || []).find(x => x.chave === k.chave + '-DEV'); if (!dv0 || dv0.de !== k.dev.lote) throw prConflito(k.chave, rm.id + (dv0 ? ' com a devolução do ' + dv0.de : '')); }
      return { msg: 'Entrega da ' + rm.id + ' já confirmada: nada foi gravado de novo.', rm, repetido: true }; }
    throw new Error('Entrega da ' + rm.id + ' já confirmada em ' + prBr(rm.entrega.d) + ': nada foi gravado de novo.'); }
  if (rm.st !== 'Em trânsito') throw new Error(rm.id + ' está ' + rm.st.toLowerCase() + ': só carga em trânsito tem entrega a confirmar.');
  const quem = cenExigeUm(k.ator, ['expedicao', 'gestor'], 'Confirmar entrega da ' + rm.id);
  const d = String(k.d || ''); if (!/^\d{4}-\d\d-\d\d$/.test(d)) throw new Error('Escolha a data da entrega.');
  if (d < rm.saida.d) throw new Error('A entrega não pode ser antes da saída (' + prBr(rm.saida.d) + ').'); if (d > prHoje()) throw new Error('A entrega não pode ser depois de hoje (' + prBr(prHoje()) + ').');
  rm.entrega = { d, at: cenAgora(), quem, comp: String(k.comp || '').trim(), chave: k.chave || ('W-ENT-' + rm.id), imp }; rm.st = 'Entregue';
  const v = P.pedidos[rm.pedido]; const cu = comCultura(v); let dv = null;
  if (k.dev) dv = comDevolverEf(c, rm, k.dev.lote, k.dev.kg, k.dev.motivo, quem, d, k.chave ? k.chave + '-DEV' : '', imp);
  const liq = comRmLiq(rm); const venc = comVenc(v.cond, d);
  return { msg: rm.id + ' entregue em ' + prBr(d) + ' (' + quem + '): ' + comTxtV(v, liq) + ' aceitos' + (dv ? ', ' + comTxtV(v, dv.kg) + ' devolvidos (' + dv.motivo + ') no ' + dv.lote + ' Em inspeção: a Qualidade decide' : '')
    + (comNat(v) === 'Venda' && !(comCond(v.cond) || {}).ant ? ' · ' + comRS(comValorV(v, liq)) + ' a receber até ' + prBr(venc) : '') + '.', rm, dev: dv }; }
function comDevolver(c, k) { const P = comP(c); const rm = P.expedicoes[k.rm]; if (!rm) throw new Error('Carga ' + k.rm + ' não encontrada.');
  const imp = JSON.stringify([k.rm, k.lote || '', prNum(k.kg), k.motivo || '']);
  if (k.chave) { const ja = (rm.devs || []).find(x => x.chave === k.chave); if (ja) { if (ja.imp !== imp) throw prConflito(k.chave, ja.lote); return { msg: 'Devolução já registrada no ' + ja.lote + ': nada foi gravado de novo.', dev: ja, repetido: true }; } }
  if (rm.st !== 'Entregue' && rm.st !== 'Entregue com devolução') throw new Error('Devolução só de carga entregue (' + rm.id + ' está ' + rm.st.toLowerCase() + ').');
  const quem = cenExigeUm(k.ator, ['expedicao', 'gestor'], 'Registrar devolução da ' + rm.id);
  const dv = comDevolverEf(c, rm, k.lote, k.kg, k.motivo, quem, k.d || prHoje(), k.chave, imp); const v = P.pedidos[rm.pedido]; const cu = comCultura(v);
  return { msg: comTxtV(v, dv.kg) + ' devolvidos da ' + rm.id + ' (' + dv.motivo + '): lote ' + dv.lote + ' Em inspeção, só a Qualidade libera. ' + v.id + ': entregue ' + comTxtV(v, prExpedido(c, v.id)) + ', a receber da carga ' + comRS(comValorV(v, comRmLiq(rm))) + '.', dev: dv }; }

/* =====================================================================================================================
   Painel comercial (R-C13): só funções do estado; hoje padrão prHoje() (o teste muda a data)
   ===================================================================================================================== */
function comPainel(c, hoje, hz) { hoje = hoje || prHoje(); hz = hz || '4'; const P = prP(c); const rows = [];
  const prods = [...new Set(comProdutos(c).concat(Object.values(P.pedidos).map(v => v.prod)))].filter(p => comCulturaProd(p)).sort();
  prods.forEach(prod => { const cu = comCulturaProd(prod); const sem = comSemanal(cu); const vs = Object.values(P.pedidos).filter(v => v.prod === prod);
    const lots = Object.values(P.lotes).filter(L => L.prod === prod).map(L => ({ L, S: prSaldos(c, L), venc: !!(L.validade && L.validade < hoje), g: sem ? '' : (L.saf || '') }));
    const comecou = v => comPeriodoComecou(c, v, hoje);
    const gVenda = v => sem ? '' : (v.saf || lots.map(x => x.g).sort().slice(-1)[0] || '');
    const ambV = v => prAmb(v) && !v.enc;   /* A-17: venda sem a massa da saca suspende a conta do período dela */
    const grupos = new Set(lots.filter(x => !x.S.esgotado || prCmp(x.S.res, 0) > 0).map(x => x.g)); vs.filter(v => (v.tipo === 'pronta' || comecou(v)) && (prCmp(prSaldoFut(c, v), 0) > 0 || ambV(v))).forEach(v => grupos.add(gVenda(v)));
    [...grupos].sort().forEach(g => { const ls = lots.filter(x => x.g === g); const ids = ls.map(x => x.L.id);
      const pv = sem ? null : comPrevRestante(c, prod, g);   /* A10 da revisão: safra em colheita soma a previsão ainda não colhida */
      const oferta = prSoma(ls.map(x => x.S.apto).concat([pv ? pv.rest : 0])); const vencApto = prSoma(ls.filter(x => x.venc).map(x => x.S.apto)); const dispVenc = prSoma(ls.filter(x => x.venc).map(x => x.S.disp));
      const est = vs.filter(v => (v.tipo === 'pronta' || comecou(v)) && gVenda(v) === g); const futRes = vs.filter(v => v.tipo === 'futura' && !comecou(v));
      const resEm = (v, apto) => prSoma(prResPed(c, v.id).filter(r => ids.indexOf(r.lote) >= 0 && (!apto || (ls.find(x => x.L.id === r.lote) || {}).S.q === 'Liberado')).map(r => r.kg));
      const comp = prSoma(est.map(v => prSaldoFut(c, v)).concat(futRes.map(v => resEm(v)))); const cob = prSoma(est.concat(futRes).map(v => resEm(v, true)));
      const amb = est.filter(ambV).map(v => v.id); const livre = amb.length ? null : prSub(prSub(oferta, comp), dispVenc);
      rows.push({ id: 'e:' + prod + ':' + g, prod, cu, per: 'est:' + g, perT: 'Estoque' + (g ? ' (' + g + ')' : '') + (pv ? ' · em colheita' : ''), tipo: 'est', oferta, tem: true, vencApto, dispVenc, comp, cob, livre, amb,
        colh: pv, apto: prSoma(ls.map(x => x.S.apto)),
        vendas: est.filter(v => prCmp(prSaldoFut(c, v), 0) > 0 || ambV(v)).map(v => v.id).concat(futRes.filter(v => prCmp(resEm(v), 0) > 0).map(v => v.id)) }); });
    if (sem) { let ws = comSemanasFut(hoje, 4);
      if (hz === 's') { const all = new Set(ws); Object.keys(PRDC.cult).forEach(cid => { if (prUn(PRDC.cult[cid].cultura).prod !== prod) return; (P.previsoes[cid] || []).forEach(x => Object.keys(x.sem || {}).forEach(w => all.add(w))); });
        vs.filter(v => v.tipo === 'futura' && v.sem).forEach(v => all.add(v.sem)); ws = [...all].filter(w => prSemIni(w) > hoje).sort(); }
      ws.forEach(w => { const o = prOfertaSem(c, prod, w); if (!o.tem && !o.fut.some(v => prCmp(prSaldoFut(c, v), 0) > 0)) return; const ini = prSemIni(w);
        rows.push({ id: 's:' + prod + ':' + w, prod, cu, per: w, perT: prSemTxt(w) + ' (' + prBr(ini) + '–' + prBr(prDiaMais(ini, 6)) + ')', tipo: 'sem', oferta: o.pub, tem: o.tem, comp: o.futKg, cob: o.resKg, livre: o.livre, amb: o.amb, vencApto: 0, dispVenc: 0, vendas: o.fut.map(v => v.id) }); }); }
    else comSafrasFut(c, prod, hoje).forEach(sf => { const o = prOfertaSafra(c, prod, sf); if (!o.tem && !o.fut.length) return;
      rows.push({ id: 'f:' + prod + ':' + sf, prod, cu, per: sf, perT: 'Safra ' + sf, tipo: 'saf', oferta: o.pub, tem: o.tem, comp: o.futKg, cob: o.resKg, livre: o.livre, amb: o.amb, vencApto: 0, dispVenc: 0, vendas: o.fut.map(v => v.id) }); }); });
  rows.forEach(r => { r.sit = r.livre === null ? 'Suspenso' : (prCmp(r.livre, 0) > 0 ? 'Livre' : (prCmp(r.livre, 0) < 0 ? 'Déficit' : 'Sem saldo livre')); });
  return rows; }
/* preço e recebimento por produto: médias ponderadas (Σ valor ÷ Σ quantidade), só natureza Venda; realizado sobre o entregue líquido */
function comPrecos(c, hoje) { hoje = hoje || prHoje(); const P = prP(c); const out = [];
  const prods = [...new Set(Object.values(P.pedidos).map(v => v.prod))].filter(p => comCulturaProd(p)).sort();
  prods.forEach(prod => { const cu = comCulturaProd(prod); const vs = Object.values(P.pedidos).filter(v => v.prod === prod && comNat(v) === 'Venda');
    /* A-17: média só sobre vendas com a massa conhecida, em kg (conversão compatível) e mostrada na unidade atual da cultura; as de saca a conferir ficam à parte */
    const ok = vs.filter(v => !prAmb(v)); const amb = vs.filter(v => prAmb(v) && !v.enc).map(v => v.id);
    const vend = prSoma(ok.map(v => v.qtd)); const valC = prSoma(ok.map(v => comValorV(v, v.qtd)));
    const rms = comRms(c, rm => !!rm.saida && !!rm.entrega && rm.st !== 'Cancelada' && vs.some(v => v.id === rm.pedido));   /* realizado = entregue (A4 da revisão: em trânsito não conta) */
    const ent = prSoma(rms.map(comRmLiq)); const valR = prSoma(rms.map(rm => comValorV(P.pedidos[rm.pedido], comRmLiq(rm)) || 0));
    const tit = comTitulos(c, t => t.prod === prod); const prodV = Object.values(P.pedidos).filter(v => v.prod === prod && comNat(v) !== 'Venda');
    out.push({ prod, cu, vend, valC, medC: prCmp(vend, 0) > 0 ? prDiv(valC, prEstQ(cu, vend)) : null, ent, valR, medR: prCmp(ent, 0) > 0 ? prDiv(valR, prEstQ(cu, ent)) : null,
      ref: (COMC.ref || {})[prod] || null, aRec: prSoma(tit.filter(t => !comVencido(t, hoje)).map(t => t.valor)), venc: prSoma(tit.filter(t => comVencido(t, hoje)).map(t => t.valor)), tit,
      vendas: vs.map(v => v.id), liq: prodV.map(v => v.id), amb }); });
  return out; }
function comIndicadores(c, hoje) { hoje = hoje || prHoje(); const tit = comTitulos(c); const d30 = prDiaMais(hoje, -30); const P = prP(c);
  /* entregue nos últimos 30 dias pela data da entrega (retirada = a saída); carga em trânsito fica de fora (A4 da revisão) */
  const ent = comRms(c, rm => !!rm.saida && !!rm.entrega && rm.st !== 'Cancelada' && rm.entrega.d >= d30 && rm.entrega.d <= hoje).filter(rm => { const v = P.pedidos[rm.pedido]; return v && comNat(v) === 'Venda'; });
  return { aRec: prSoma(tit.filter(t => !comVencido(t, hoje)).map(t => t.valor)), venc: prSoma(tit.filter(t => comVencido(t, hoje)).map(t => t.valor)),
           ent30: prSoma(ent.map(rm => { const v = P.pedidos[rm.pedido]; return comValorV(v, comRmLiq(rm)) || 0; })), nTit: tit.length }; }
try { window.__com = { comVender, comConverterSaca, comEncerrar, comAprovarCredito, comProgramar, comCancelarCarga, comSair, comEntregar, comDevolver, comPainel, comPrecos, comCredito, comImpede, comSitVenda, comTitulos, comAReceber }; } catch (e) {}
