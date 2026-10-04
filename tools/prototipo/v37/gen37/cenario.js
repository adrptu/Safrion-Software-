// ===== Cenário compartilhado de demonstração (O.S. ↔ Estoque ↔ App de campo) =====
// Um único estado gravado no navegador (localStorage), lido e alterado pelas telas O.S., Estoque e App.
// Sem localStorage (janela privada, pré-visualização) o cenário vale só para a tela aberta.
// Regras: PRD 41 (liberação e fichas), 42 (almoxarifado: reserva ao liberar, entrega só do saldo elegível, consumo pelo apontamento,
// sobra devolvida e conferida), 64 (app de campo: fila, turno, apontamento offline sem duplicar), 72 (DEC-2609-04/05/07).
const CEN_KEY = 'talhao-os-cenario-v1';
let CEN_MEM = null;
function cenClone(o) { return JSON.parse(JSON.stringify(o)); }
function cenLoad() { try { const t = localStorage.getItem(CEN_KEY); return t ? JSON.parse(t) : null; } catch (e) { return null; } }
function cenSave(c) { CEN_MEM = c; try { localStorage.setItem(CEN_KEY, JSON.stringify(c)); } catch (e) {} }
function cenGet() { const c = cenLoad() || CEN_MEM; if (c && c.v === CEN0.v) return c; CEN_MEM = cenClone(CEN0); return CEN_MEM; }
function cenReset() { CEN_MEM = cenClone(CEN0); try { localStorage.removeItem(CEN_KEY); } catch (e) {} }
function cenAgora() { const d = new Date(); return ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2); }
// Mudança atômica: aplica fn numa cópia, grava e devolve a mensagem (ou o erro, sem gravar nada).
function cenMudar(self, fn) {
  const c = cenClone(cenGet()); let r;
  try { r = fn(c) || {}; } catch (e) { r = { erro: String(e.message || e) }; }
  if (r.erro) { if (self) self.setState({ g2toast: r.erro }); return r; }
  c.rev = (c.rev || 0) + 1; cenSave(c); if (self) self.setState({ cenrev: c.rev, g2toast: r.msg || '' }); return r;
}
// Outras telas (outros quadros do Canvas) atualizam quando o cenário muda.
function cenOuvir(self) {
  if (self.__cenOuvindo) return; self.__cenOuvindo = true;
  try { window.addEventListener('storage', (e) => { if (e.key === CEN_KEY) self.setState({ cenrev: Date.now() }); }); } catch (e) {}
}
// Regra única de quantidade de insumo (SINT-C03; mesma de quantidade.py): dose × área em DECIMAL exato (forma decimal mais curta
// de cada número), 2 casas, meio para cima. Consumo de um apontamento = quantidade(acumulado depois) − quantidade(acumulado antes):
// a soma dos apontamentos fecha no total da ordem e a custódia zera, sem tolerância.
function cenDec(x) { const s = String(Number(x)); if (!/^-?\d+(\.\d+)?$/.test(s)) return null; const p = s.split('.'); const f = p[1] || '';
  return { n: BigInt(p[0] + f), e: f.length }; }
function cenQtd(dose, area) {
  const a = cenDec(dose), b = cenDec(area); if (!a || !b) throw new Error('Quantidade fora da faixa: ' + dose + ' × ' + area + '.');
  let n = a.n * b.n; const e = a.e + b.e; const neg = n < 0n; if (neg) n = -n;
  let c;   // centésimos, meio para cima
  if (e <= 2) c = n * (10n ** BigInt(2 - e)); else { const d = 10n ** BigInt(e - 2); c = (n * 2n + d) / (2n * d); }
  return (neg ? -1 : 1) * Number(c) / 100; }
function cenQtdTrecho(dose, antes, ha) {
  const a0 = Number((antes || 0).toFixed(6)), a1 = Number(((antes || 0) + ha).toFixed(6));
  return Math.round((cenQtd(dose, a1) - cenQtd(dose, a0)) * 100) / 100; }
function cenNum(n, d) { return Number(n || 0).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: d === undefined ? 2 : d }); }
function cenLote(c, prod) { return Object.values(c.lotes).filter(l => l.prod === prod).sort((a, b) => (b.fisico - b.reservado - b.quarentena) - (a.fisico - a.reservado - a.quarentena))[0] || null; }
function cenDisp(l) { return Math.max(0, (l.fisico || 0) - (l.quarentena || 0) - (l.reservado || 0)); }
function cenMov(c, m) { m.id = 'MV-' + (1000 + c.movs.length + 1); m.at = m.at || cenAgora(); c.movs.push(m); return m; }

// ---------- O.S. (web) ----------
// Liberar (agrônomo): reserva cada insumo no lote com saldo (a reserva nunca passa do disponível).
function cenLiberar(c, id) {
  const o = c.ordens[id]; if (!o) throw new Error('Ordem não encontrada.');
  if (o.etapa !== 'A liberar') throw new Error(id + ' não está em A liberar.');
  const rid = o.req || ('REQ-' + (41 + Object.keys(c.reqs).length));
  const req = c.reqs[rid] || (c.reqs[rid] = { id: rid, os: id, itens: [], estado: 'Reservada' });
  (o.ins || []).forEach(x => {
    const l = cenLote(c, x.p); if (!l) throw new Error('Sem lote de ' + x.p + ' no Estoque.');
    if (cenDisp(l) + 1e-9 < x.tot) throw new Error('Saldo insuficiente de ' + x.p + ': ' + cenNum(cenDisp(l)) + ' ' + x.un + ' disponíveis para ' + cenNum(x.tot) + ' ' + x.un + '.');
    l.reservado += x.tot;
    req.itens.push({ prod: x.p, lote: l.lote, un: x.un, emb: x.emb || '', solicitado: x.tot, entregue: 0, consumido: 0, devolvido: 0, custodia: 0 });
    cenMov(c, { tipo: 'reserva', req: rid, os: id, prod: x.p, lote: l.lote, qtd: x.tot, un: x.un, quem: 'Sistema', origem: 'web' });
  });
  o.req = rid; o.reservado = true; o.etapa = 'Liberadas';
  return { msg: id + ' liberada. ' + rid + ' reservou no Estoque: ' + req.itens.map(i => i.prod + ' ' + cenNum(i.solicitado) + ' ' + i.un).join(', ') + '.' };
}

// ---------- Estoque (almoxarife) ----------
// Saldo a entregar = solicitado − consumido − em custódia (PRD 42.1); só para O.S. Liberadas ou Em execução.
function cenSaldoEntregar(it) { return Math.max(0, it.solicitado - it.consumido - it.custodia); }
function cenEntregar(c, rid, prod, qtd, quem) {
  const r = c.reqs[rid]; const o = r && c.ordens[r.os]; if (!r || !o) throw new Error('Requisição não encontrada.');
  if (['Liberadas', 'Em execução'].indexOf(o.etapa) < 0) throw new Error('Entregue só para O.S. liberada ou em execução (' + r.os + ' está em ' + o.etapa + ').');
  const it = r.itens.find(i => i.prod === prod); if (!it) throw new Error(prod + ' não está na ' + rid + '.');
  const l = c.lotes[prod + '|' + it.lote]; if (!l) throw new Error('Lote ' + it.lote + ' de ' + prod + ' não encontrado no Estoque.');
  if (!(qtd > 0)) throw new Error('Informe a quantidade.');
  if (qtd > cenSaldoEntregar(it) + 1e-9) throw new Error('Acima do saldo a entregar: ' + cenNum(cenSaldoEntregar(it)) + ' ' + it.un + '.');
  if (qtd > l.fisico - l.quarentena + 1e-9) throw new Error('O lote ' + it.lote + ' não tem ' + cenNum(qtd) + ' ' + it.un + ' livres.');
  l.fisico -= qtd; l.reservado = Math.max(0, l.reservado - qtd); it.entregue += qtd; it.custodia += qtd; it.quem = quem || o.resp;
  r.estado = 'Entregue'; cenMov(c, { tipo: 'entrega', req: rid, os: r.os, prod, lote: it.lote, qtd, un: it.un, quem: 'Rui (almoxarife) → ' + (quem || o.resp), origem: 'web' });
  return { msg: cenNum(qtd) + ' ' + it.un + ' de ' + prod + ' entregues a ' + (quem || o.resp) + ' (' + r.os + '). Aguarda confirmação no app.' };
}
// Devolução conferida: só o recebido e conferido volta ao disponível; material bloqueado não volta.
function cenDevolver(c, rid, prod, qtd, apto) {
  const r = c.reqs[rid]; const it = r && r.itens.find(i => i.prod === prod); if (!it) throw new Error('Item não encontrado.');
  if (!(qtd > 0) || qtd > it.custodia + 1e-9) throw new Error('Devolva até ' + cenNum(it.custodia) + ' ' + it.un + ' em custódia.');
  const l = c.lotes[prod + '|' + it.lote]; if (!l) throw new Error('Lote ' + it.lote + ' de ' + prod + ' não encontrado no Estoque.');
  it.custodia -= qtd; it.devolvido += qtd;
  if (apto) l.fisico += qtd; else { l.fisico += qtd; l.quarentena += qtd; }
  cenMov(c, { tipo: 'devolucao', req: rid, os: r.os, prod, lote: it.lote, qtd, un: it.un, quem: 'Rui (almoxarife)', origem: 'web', apto: !!apto });
  return { msg: cenNum(qtd) + ' ' + it.un + ' de ' + prod + ' devolvidos' + (apto ? ' ao disponível.' : ' e bloqueados para inspeção.') };
}

// Recebimento de fornecedor: conferido entra no lote (novo ou existente); com avaria ou sem laudo entra bloqueado (quarentena).
function cenReceber(c, prod, lote, qtd, un, local, validade, doc, apto) {
  if (!prod || !lote) throw new Error('Informe produto e lote.'); if (!(qtd > 0)) throw new Error('Informe a quantidade recebida.');
  if (!doc) throw new Error('Informe a nota fiscal ou o documento de entrada.');
  const k = prod + '|' + lote; const l = c.lotes[k] || (c.lotes[k] = { prod, lote, local: local || 'Almox. defensivos', un: un || 'L', fisico: 0, quarentena: 0, reservado: 0, validade: validade || '' });
  if (l.un !== (un || l.un)) throw new Error('Unidade diferente do lote ' + lote + ' (' + l.un + ').');
  l.fisico += qtd; if (!apto) l.quarentena += qtd;
  cenMov(c, { tipo: 'recebimento-nf', prod, lote, qtd, un: l.un, quem: 'Rui (almoxarife)', origem: 'web', doc, apto: !!apto });
  return { msg: cenNum(qtd) + ' ' + l.un + ' de ' + prod + ' recebidos no lote ' + lote + ' (' + l.local + ')' + (apto ? '.' : ' e bloqueados até a inspeção.') };
}
function cenLiberarQuarentena(c, key) { const l = c.lotes[key]; if (!l || !(l.quarentena > 0)) throw new Error('Nada bloqueado neste lote.');
  const q = l.quarentena; l.quarentena = 0; cenMov(c, { tipo: 'inspecao', prod: l.prod, lote: l.lote, qtd: q, un: l.un, quem: 'Rui (almoxarife)', origem: 'web' });
  return { msg: cenNum(q) + ' ' + l.un + ' do lote ' + l.lote + ' liberados após inspeção.' }; }
// Inventário: contagem cega por lote; diferença vira ajuste pendente (o saldo só muda com a aprovação do gestor).
function cenContar(c, key, contado) { const l = c.lotes[key]; if (!l) throw new Error('Lote não encontrado.');
  if (!(contado >= 0) || contado === '' || contado === null) throw new Error('Informe a quantidade contada.');
  const dif = contado - l.fisico; c.ajustes = c.ajustes || [];
  if (Math.abs(dif) < 1e-9) { cenMov(c, { tipo: 'contagem', prod: l.prod, lote: l.lote, qtd: 0, un: l.un, quem: 'Rui (almoxarife)', origem: 'web' }); return { msg: 'Contagem confere: ' + cenNum(contado) + ' ' + l.un + ' no lote ' + l.lote + '.' }; }
  if (contado + 1e-9 < l.reservado + l.quarentena) throw new Error('Contagem abaixo do reservado e bloqueado (' + cenNum(l.reservado + l.quarentena) + ' ' + l.un + '). Recontar antes de ajustar.');
  const aj = { id: 'AJ-' + (70 + c.ajustes.length + 1), key, prod: l.prod, lote: l.lote, un: l.un, sistema: l.fisico, contado, dif, estado: 'Aguardando gestor' }; c.ajustes.push(aj);
  return { msg: 'Divergência de ' + cenNum(dif) + ' ' + l.un + ' no lote ' + l.lote + ' · ' + aj.id + ' aguarda o gestor. O saldo não muda até a aprovação.' }; }
function cenAprovarAjuste(c, id, aprovar) { const aj = (c.ajustes || []).find(a => a.id === id); if (!aj || aj.estado !== 'Aguardando gestor') throw new Error('Ajuste não está pendente.');
  const l = c.lotes[aj.key]; if (aprovar) { l.fisico = aj.contado; aj.estado = 'Aprovado'; cenMov(c, { tipo: 'ajuste', prod: aj.prod, lote: aj.lote, qtd: aj.dif, un: aj.un, quem: 'Ana (gestora)', origem: 'web' }); }
  else aj.estado = 'Recusado';
  return { msg: aj.id + (aprovar ? ' aprovado: lote ' + aj.lote + ' passa a ' + cenNum(aj.contado) + ' ' + aj.un + '.' : ' recusado: recontar o lote ' + aj.lote + '.') }; }

// ---------- App de campo ----------
function cenOnline(c) { return c.app.online !== false; }
function cenConfirmarRecebimento(c, rid) {
  const r = c.reqs[rid]; if (!r) throw new Error('Requisição não encontrada.');
  const pend = r.itens.filter(i => i.custodia > 0 && !i.confirmado); if (!pend.length) throw new Error('Nada entregue para confirmar.');
  pend.forEach(i => { i.confirmado = true; });
  const m = cenMov(c, { tipo: 'recebimento', req: rid, os: r.os, qtd: 0, quem: c.app.operador, origem: 'app', sinc: cenOnline(c),
    itens: pend.map(i => ({ prod: i.prod, lote: i.lote, qtd: i.custodia, un: i.un })) });
  if (!m.sinc) c.app.fila.push(m.id);
  return { msg: 'Recebimento confirmado: ' + pend.map(i => i.prod + ' ' + cenNum(i.custodia) + ' ' + i.un).join(', ') + (m.sinc ? '.' : '. Salvo no aparelho; envia quando houver sinal.') };
}
function cenIniciarTurno(c, id) {
  const o = c.ordens[id]; if (!o) throw new Error('Ordem não encontrada.');
  if (['Liberadas', 'Em execução'].indexOf(o.etapa) < 0) throw new Error(id + ' não está liberada para execução.');
  if (c.app.turno && !c.app.turno.fim) throw new Error('Feche o turno aberto antes de iniciar outro.');
  c.app.turno = { os: id, ini: cenAgora(), pausas: [], fim: null };
  if (o.etapa === 'Liberadas') { o.etapa = 'Em execução'; }
  return { msg: 'Turno iniciado em ' + id + ' às ' + c.app.turno.ini + '.' };
}
function cenPausar(c) { const t = c.app.turno; if (!t || t.fim) throw new Error('Nenhum turno aberto.');
  const p = t.pausas[t.pausas.length - 1]; if (p && !p.fim) { p.fim = cenAgora(); return { msg: 'Turno retomado.' }; }
  t.pausas.push({ ini: cenAgora(), fim: null }); return { msg: 'Turno pausado.' }; }
// Consumo informado acima da custódia (RN-018; CONC-07): o fato fica gravado Em conferência, sem baixa nem custódia negativa,
// e o almoxarife concilia (CMD-50). A dose × área é só estimativa (CONC-13): nunca troca o consumo informado nem abre conferência
// sozinha; a sugestão não editada acima da custódia (est) segue recusada como antes, para o executor informar quanto usou.
const CEN_CONC_RESP = 'Rui (almoxarife)';
function cenConfAbertas(c, os) { return (c.confs || []).filter(k => k.estado === 'Em conferência' && k.sinc && (!os || k.os === os)); }
function cenSeloConf(c, os) { const o = c.ordens[os]; if (!o) return; const t = 'Consumo em conferência';
  o.selos = (o.selos || []).filter(s => s.t !== t); if (cenConfAbertas(c, os).length) o.selos.push({ t, c: 'yellow' }); }
function cenPl(n, s, p) { return Math.abs(Number(n) || 0) >= 2 ? p : s; }
// custódia mostrada no caso: a atual enquanto está aberto (outra entrega ou outro aceite a mudam); a do relato depois de resolvido
function cenConfCust(c, k) { if (!c || k.estado !== 'Em conferência') return k.custodia;
  const r = k.req && c.reqs && c.reqs[k.req]; const it = r && r.itens.find(i => i.prod === k.prod); return it ? it.custodia : 0; }
function cenConfTxt(k, c) { const cu = cenConfCust(c, k);
  return k.prod + ' ' + cenNum(k.relatado) + ' ' + k.un + cenPl(k.relatado, ' relatado', ' relatados') + ', ' + (cu > 1e-9 ? cenNum(cu) + ' ' + k.un + ' em custódia' : 'nada em custódia'); }
// reserva feita para o item (na liberação da O.S. ou no início da demonstração); a mesma conta do Estoque (eresTot)
function cenResTot(c, rid, prod) { const s0 = (typeof CEN0 !== 'undefined' && CEN0 && CEN0.reqs) ? CEN0.reqs[rid] : null;
  if (s0 && s0.estado === 'Reservada') { const i = s0.itens.find(x => x.prod === prod); return i ? i.solicitado : 0; }
  return (c.movs || []).filter(m => m.tipo === 'reserva' && m.req === rid && m.prod === prod).reduce((a, m) => a + (m.qtd || 0), 0); }
function cenResPropria(c, rid, it, l) { return (l && it) ? Math.max(0, Math.min(l.reservado || 0, cenResTot(c, rid, it.prod) - (it.entregue || 0))) : 0; }
// Fechar turno: registra hectares, horas e consumo (dose × área, ajustável). Fechar o turno não encerra a O.S.
function cenFecharTurno(c, ha, horas, consumo, obs, est) {
  const t = c.app.turno; if (!t || t.fim) throw new Error('Nenhum turno aberto.');
  const o = c.ordens[t.os]; if (!(ha > 0)) throw new Error('Informe os hectares feitos.');
  const haPend = (o.ap || []).filter(a => a.sinc === false).reduce((s, a) => s + (a.ha || 0), 0);   // apontado no aparelho, ainda sem sinal
  const saldoApp = Math.max(0, o.saldo - haPend);
  if (ha > saldoApp + 1e-9) throw new Error('Máximo ' + cenNum(saldoApp) + ' ha: é o saldo da ordem' + (haPend ? ' descontando ' + cenNum(haPend) + ' ha ainda no aparelho.' : '.'));
  if (!(horas > 0)) throw new Error('Informe as horas trabalhadas.');
  t.fim = cenAgora();
  const cons = consumo || {}; const es = est || []; const inf = {};   // informado pelo executor (a estimativa não editada não conta como informada)
  Object.keys(cons).forEach(k => { if (cons[k] !== undefined && cons[k] !== null && es.indexOf(k) < 0) inf[k] = true; });
  (o.ins || []).forEach(x => { if (cons[x.p] === undefined) cons[x.p] = cenQtdTrecho(x.dose, (o.realizado || 0) + haPend, ha); });   // regra única (SINT-C03)
  const r = o.req && c.reqs[o.req]; const conf = {};
  if (r) for (const it of r.itens) { const q = cons[it.prod] || 0; if (q > it.custodia + 1e-9) {
    if (!inf[it.prod]) throw new Error('Consumo de ' + it.prod + ' (' + cenNum(q) + ' ' + it.un + ') acima do que está com você (' + cenNum(it.custodia) + ' ' + it.un + '). Confira a retirada.');
    conf[it.prod] = { q, it }; } }
  Object.keys(inf).forEach(k => { if (!(r && r.itens.some(i => i.prod === k)) && cons[k] > 1e-9) conf[k] = { q: cons[k], it: null }; });   // nada dele com o executor
  if (r) r.itens.forEach(it => { if (conf[it.prod]) return; const q = cons[it.prod] || 0; it.consumido += q; it.custodia -= q; });
  Object.keys(conf).forEach(k => { delete cons[k]; });   // ap.cons = só o consumo baixado; o relatado em conferência fica em ap.conf
  const dia = (o.ap || []).filter(a => a.st !== 'Previsto').length + 1;
  const ap = { d: new Date().toLocaleDateString('pt-BR').slice(0, 5), dia, ha, h: horas, st: 'Provisório', cons, obs: obs || '', origem: 'app', sinc: cenOnline(c) };
  o.ap = (o.ap || []).filter(a => a.st !== 'Previsto').concat([ap]);
  if (ap.sinc) { o.realizado += ha; o.saldo = Math.max(0, o.saldo - ha); } else { c.app.fila.push('AP|' + t.os + '|' + dia); }
  const m = cenMov(c, { tipo: 'consumo', os: t.os, req: o.req || '', qtd: 0, quem: c.app.operador, origem: 'app', sinc: ap.sinc, det: Object.keys(cons).map(k => k + ' ' + cenNum(cons[k], 1)).join(', ') });
  ap.mov = m.id;
  const ks = Object.keys(conf).map(k => { const x = conf[k]; c.confs = c.confs || [];
    const kc = { id: 'CC-' + (300 + c.confs.length + 1), os: t.os, req: o.req || '', prod: k, lote: x.it ? x.it.lote : '—', un: x.it ? x.it.un : ((o.ins || []).find(i => i.p === k) || {}).un || '',
      relatado: x.q, custodia: x.it ? x.it.custodia : 0, dia, at: t.fim, quem: c.app.operador, resp: CEN_CONC_RESP, estado: 'Em conferência',
      motivo: x.it ? 'Consumo acima da custódia' : 'Consumo sem material em custódia', mov: m.id, sinc: ap.sinc };
    c.confs.push(kc); return kc; });
  if (ks.length) { ap.conf = {}; ks.forEach(k => { ap.conf[k.prod] = k.relatado; }); m.conf = ks.map(k => k.id); cenSeloConf(c, t.os); }
  c.app.turno = null;
  return { msg: 'Turno fechado: ' + cenNum(ha, 1) + ' ha em ' + cenNum(horas, 1) + ' h' + (ap.sinc ? '.' : ' · salvo no aparelho, envia quando houver sinal.') + ' A ordem continua em execução.'
    + (ks.length ? ' Consumo em conferência: ' + ks.map(k => cenConfTxt(k, c)).join('; ') + ' · ' + CEN_CONC_RESP + ' concilia.' : '') };
}
// Conciliar o consumo em conferência (CMD-50, almoxarife). Prévia = efeito: aceitar baixa o relatado uma vez; o que passa da custódia
// sai do lote do item (primeiro a reserva da própria requisição, depois o livre) como entrega a regularizar; sem origem no lote é
// recusado com o motivo (nada é fabricado). Recusar deixa o relato sem efeito. Nenhum relato é apagado.
function cenConcPrevia(c, id) {
  const k = (c.confs || []).find(x => x.id === id); if (!k || k.estado !== 'Em conferência') throw new Error('Este consumo não está em conferência.');
  if (!k.sinc) throw new Error('O apontamento de ' + k.os + ' ainda está no aparelho, aguardando sinal.');
  const r = (k.req && c.reqs[k.req]) || null; const it = (r && r.itens.find(i => i.prod === k.prod)) || null;
  const l = it ? (c.lotes[k.prod + '|' + it.lote] || null) : cenLote(c, k.prod); const un = k.un;
  const cust = it ? it.custodia : 0; const falta = Math.max(0, k.relatado - cust);
  const own = falta > 1e-9 ? cenResPropria(c, k.req, it, l) : 0; const res = Math.min(falta, own); const livre = falta - res;
  let erro = '';
  if (falta > 1e-9 && (!l || cenDisp(l) + 1e-9 < livre)) erro = 'Sem origem física para ' + cenNum(falta) + ' ' + un + ' de ' + k.prod
    + (l ? ': o lote ' + l.lote + ' tem ' + cenNum(cenDisp(l) + own) + ' ' + un + ' para esta O.S.' : ': sem lote no Estoque') + '. Conte o lote ou recuse o relato.';
  const ori = (!(falta > 1e-9) || !l) ? '' : cenNum(falta) + ' ' + un + cenPl(falta, ' sai', ' saem') + ' do lote ' + l.lote
    + ' (' + (res > 1e-9 ? (livre > 1e-9 ? cenNum(res) + ' ' + un + ' da reserva da ' + k.req + ' e ' + cenNum(livre) + ' ' + un + ' do livre' : 'reserva da ' + k.req) : 'livre') + ')';
  const txt = 'Baixa ' + cenNum(k.relatado) + ' ' + un + ' na ' + k.os + ': ' + [cust > 1e-9 ? cenNum(Math.min(cust, k.relatado)) + ' ' + un + ' da custódia de ' + k.quem : '', ori].filter(Boolean).join(' · ') + '.';
  return { k, r, it, l, cust, falta, res, livre, erro, txt };
}
function cenConciliar(c, id, aceitar, motivo) {
  const p = cenConcPrevia(c, id); const k = p.k, r = p.r, l = p.l; let it = p.it;
  if (!aceitar) { k.estado = 'Recusado'; k.decisao = motivo || 'registro sem fato físico'; k.por = CEN_CONC_RESP; cenSeloConf(c, k.os);
    return { msg: k.id + ' recusado (' + k.decisao + '): ' + k.prod + ' ' + cenNum(k.relatado) + ' ' + k.un + ' sem efeito no saldo' + (it && it.custodia > 1e-9 ? '; ' + cenNum(it.custodia) + ' ' + it.un + cenPl(it.custodia, ' segue', ' seguem') + ' em custódia com ' + k.quem + '.' : '.') }; }
  if (p.erro) throw new Error(p.erro);
  const falta = p.falta;
  if (falta > 1e-9) {
    l.fisico -= falta; l.reservado = Math.max(0, (l.reservado || 0) - p.res);   // a reserva da própria requisição não fica maior que a necessidade
    if (!it && r) { it = { prod: k.prod, lote: l.lote, un: k.un, emb: '', solicitado: 0, entregue: 0, consumido: 0, devolvido: 0, custodia: 0, confirmado: true }; r.itens.push(it); }
    if (it) { it.entregue += falta; it.custodia += falta; }
    cenMov(c, { tipo: 'entrega', req: k.req, os: k.os, prod: k.prod, lote: l.lote, qtd: falta, un: k.un, quem: CEN_CONC_RESP + ' → ' + k.quem + ' · regularização ' + k.id, origem: 'web', conf: k.id });
  }
  if (it) { it.consumido += k.relatado; it.custodia = Math.max(0, it.custodia - k.relatado); }
  cenMov(c, { tipo: 'consumo', os: k.os, req: k.req, qtd: 0, quem: CEN_CONC_RESP + ' · aceite ' + k.id, origem: 'web', sinc: true, det: k.prod + ' ' + cenNum(k.relatado, 1), conf: k.id });
  const de = falta > 1e-9 ? ' do lote ' + l.lote + (p.res > 1e-9 ? ' (reserva da ' + k.req + ')' : '') : '';
  k.estado = 'Aceito'; k.decisao = falta > 1e-9 ? 'origem ' + cenNum(falta) + ' ' + k.un + de : 'coberto pela custódia'; k.por = CEN_CONC_RESP; cenSeloConf(c, k.os);
  return { msg: k.id + ' aceito: ' + k.prod + ' ' + cenNum(k.relatado) + ' ' + k.un + cenPl(k.relatado, ' baixado', ' baixados') + ' na ' + k.os
    + (falta > 1e-9 ? ' · ' + cenNum(falta) + ' ' + k.un + cenPl(falta, ' regularizado', ' regularizados') + de + '.' : '.') };
}
function cenOcorrencia(c, id, tipo, texto) { if (!texto) throw new Error('Descreva a ocorrência.');
  const oc = { id: 'OC-' + (500 + c.ocorr.length + 1), os: id, tipo, texto, at: cenAgora(), sinc: cenOnline(c) }; c.ocorr.push(oc); if (!oc.sinc) c.app.fila.push(oc.id);
  return { msg: 'Ocorrência ' + oc.id + ' registrada' + (oc.sinc ? '.' : ' no aparelho.') }; }
// Sinal: sem sinal tudo vai para a fila; ao voltar, a fila é enviada uma vez só (sem duplicar).
function cenSinal(c, online) {
  c.app.online = !!online; if (!online) return { msg: 'Sem sinal: o app continua funcionando e guarda os registros.' };
  let n = 0; c.app.fila.forEach(k => { if (k.indexOf('AP|') === 0) { const [, id, dia] = k.split('|'); const o = c.ordens[id]; const ap = (o.ap || []).find(a => String(a.dia) === dia && !a.sinc);
      if (ap) { ap.sinc = true; o.realizado += ap.ha; o.saldo = Math.max(0, o.saldo - ap.ha); n++;
        if (ap.mov) { const mv = c.movs.find(x => x.id === ap.mov); if (mv) mv.sinc = true; }
        if (ap.conf) { (c.confs || []).forEach(k => { if (k.os === id && String(k.dia) === dia) k.sinc = true; }); cenSeloConf(c, id); } } }
    else { const m = c.movs.find(x => x.id === k) || c.ocorr.find(x => x.id === k); if (m && !m.sinc) { m.sinc = true; n++; } } });
  c.app.fila = []; return { msg: n ? (n + (n > 1 ? ' registros enviados' : ' registro enviado') + ' ao voltar o sinal.') : 'Sinal de volta. Nada pendente.' };
}
// Encerrar exige apontamentos enviados e nada em custódia (sobra devolvida).
function cenPodeEncerrar(c, id) { const o = c.ordens[id]; const r = o.req && c.reqs[o.req];
  if ((o.ap || []).some(a => a.sinc === false)) return 'Há apontamentos no aparelho aguardando sinal.';
  const cf = cenConfAbertas(c, id); if (cf.length) return 'Consumo em conferência: ' + cf.map(k => cenConfTxt(k, c)).join('; ') + '. ' + CEN_CONC_RESP + ' concilia no Estoque.';
  const cust = r ? r.itens.filter(i => i.custodia > 0.001) : []; if (cust.length) return 'Sobra em custódia: ' + cust.map(i => i.prod + ' ' + cenNum(i.custodia) + ' ' + i.un).join(', ') + '. Receba a devolução no Estoque.';
  return ''; }
