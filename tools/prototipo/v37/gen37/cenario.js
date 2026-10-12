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
function cenDec(x) { const m = /^(-?)(\d+)(?:\.(\d+))?(?:e([+-]\d+))?$/.exec(String(Number(x))); if (!m) return null;   // NaN/Infinity: fora
  const f = m[3] || ''; let n = BigInt(m[1] + m[2] + f), e = f.length - Number(m[4] || 0); if (e < 0) { n *= 10n ** BigInt(-e); e = 0; }   // 1e-7, 1e+21
  return { n, e }; }
function cenQtd(dose, area) {
  const a = cenDec(dose), b = cenDec(area); if (!a || !b) throw new Error('Quantidade fora da faixa: ' + dose + ' × ' + area + '.');
  let n = a.n * b.n; const e = a.e + b.e; const neg = n < 0n; if (neg) n = -n;
  let c;   // centésimos, meio para cima
  if (e <= 2) c = n * (10n ** BigInt(2 - e)); else { const d = 10n ** BigInt(e - 2); c = (n * 2n + d) / (2n * d); }
  const t = c.toString().padStart(3, '0'); return (neg ? -1 : 1) * Number(t.slice(0, -2) + '.' + t.slice(-2)); }   // decimal exato → número mais próximo (= float(Decimal))
function cenQtdTrecho(dose, antes, ha) {
  const a0 = Number((antes || 0).toFixed(6)), a1 = Number(((antes || 0) + ha).toFixed(6));
  return Math.round((cenQtd(dose, a1) - cenQtd(dose, a0)) * 100) / 100; }
function cenNum(n, d) { return Number(n || 0).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: d === undefined ? 2 : d }); }
// ---------- regra legal de uso de agrotóxico (RN-016 · RF-EXT-002 · ENG-011): a mesma no receituário (AG-01) e na O.S. (liberar e ajustar) ----------
// us = usos da bula de referência do produto na cultura, com dose por ha (dados_mip.uso); no AG-01 só o uso do alvo escolhido.
// dose em un/ha; nap = aplicações do produto no talhão no ciclo, sem contar esta. Trava o que a lei proíbe; o resto é alerta.
function cenUsoLegal(us, rot, dose, un, nap, refs) {   // refs (opcional): o que foi contado, para a mensagem dizer com quem resolver
  const tr = [], al = []; us = us || [];
  if (!us.length) { tr.push('Sem registro para ' + rot + '.'); return { tr, al }; }
  if (us[0].sit === 'Cancelado') tr.push('Registro cancelado: uso proibido.');
  else if (us[0].sit === 'Em reavaliação') al.push('Produto em reavaliação na Anvisa.');
  const cmp = us.filter(u => !un || u.un === un), ok = cmp.filter(u => dose >= u.dmin - 1e-9 && dose <= u.dmax + 1e-9);
  const base = ok.length ? ok : (cmp.length ? cmp : us);
  const ft = (L) => L.map(u => cenNum(u.dmin, 3) + (u.dmax !== u.dmin ? '–' + cenNum(u.dmax, 3) : '') + ' ' + u.un + '/ha').filter((x, i, a) => a.indexOf(x) === i).join(' ou ') + (L.some(u => u.calda) ? ' (calda de 1.000 L/ha)' : '');
  if (base.every(u => !u.conf)) al.push('Uso não conferido na bula: confira antes de aplicar.');
  if (!(dose > 0 && isFinite(dose))) tr.push('Informe a dose.');
  else if (!cmp.length) tr.push('Dose em ' + un + '/ha e bula em ' + ft(us) + ': unidade diferente da bula, não dá para conferir a dose; corrija a unidade.');   // trava: dose sem comparação pode passar do máximo (CTL-1 rev. 1)
  else if (!ok.length) tr.push('Dose fora da bula: ' + ft(cmp) + '.');
  const mx = Math.max.apply(null, base.map(u => u.mx || Infinity));
  if (isFinite(mx) && nap >= mx) tr.push('Nº máximo de aplicações no ciclo atingido: ' + nap + ' de ' + mx + (refs && refs.length ? ' (' + refs.join(', ') + ')' : '') + '.');
  return { tr, al };
}
function cenLote(c, prod) { return Object.values(c.lotes).filter(l => l.prod === prod).sort((a, b) => (b.fisico - b.reservado - b.quarentena) - (a.fisico - a.reservado - a.quarentena))[0] || null; }
function cenDisp(l) { return Math.max(0, (l.fisico || 0) - (l.quarentena || 0) - (l.reservado || 0)); }
// ---------- CTL-4 (revisão do 853a6a8, achado 1, S2) · o que cada O.S. ainda precisa e o que já tem, por insumo, numa conta só (cenOsDem e cenEstDem).
// bruto = o que falta aplicar: A liberar, Liberadas e Em execução, quantidade(dose, saldo) (sem realizado, o total da versão); nas outras fases 0.
// cust = custódia da requisição. need = máx(0, bruto − cust): o que a ordem ainda tira do almoxarifado. sobra = máx(0, cust − bruto): material
// entregue que a ordem não vai usar (O.S. cancelada, em conferência, encerrada, ou excedente da ativa) — é suprimento, está com o operador e volta
// ao Estoque na devolução. Dano evitado: cancelar a OS-0425 com 8.000 kg entregues comprava 8.000 kg de NPK de novo (R$ 27.200) e devolver a sobra
// mudava a compra (MAP −500 kg da OS-0417). r = a requisição (padrão: a da ordem).
const CEN_FASES_PEND = ['A liberar', 'Liberadas', 'Em execução'];
function cenOsSup(c, co, r) { const out = {}; if (!co) return out; r = r || ((c && c.reqs) || {})[co.req || ''] || null;
  const P = (p) => out[p] || (out[p] = { bruto: 0, cust: 0, need: 0, sobra: 0 });
  if (CEN_FASES_PEND.indexOf(co.etapa) >= 0) { const real = co.realizado || 0; const saldo = real ? (co.saldo || 0) : (co.area || 0);
    (co.ins || []).forEach(i => { P(i.p).bruto += real ? cenQtd(i.dose, saldo) : (i.tot || 0); }); }
  ((r && r.itens) || []).forEach(it => { P(it.prod).cust += (it.custodia || 0); });
  Object.values(out).forEach(x => { x.need = Math.max(0, cenQtd(x.bruto - x.cust, 1)); x.sobra = Math.max(0, cenQtd(x.cust - x.bruto, 1)); });
  return out; }
// ---------- CTL-4 · o que cada O.S. ainda tira do almoxarifado (DEM-02), lido do cenário vivo: Planejar safra (etapa 4) e Mapa › Insumos usam
// na demanda única (demFazenda, cal01.js); espelho dados2.os_dem na semente. b (dados2.os_base): {ords:[{id,faz,saf,chaves,loc,ini,t}],
// safs:[{id,faz,nome}], cat:{insumo:{g,preco}}, hoje}. A liberar, Liberadas e Em execução: pendente = need de cenOsSup (máx(0, quantidade(dose,
// saldo) − custódia da requisição); sem realizado, o total da versão). Em conferência e Encerradas: pendente 0, mas a ordem continua cobrindo o
// plano (DEM-01). Canceladas não cobrem nada. A custódia que passa do pendente é suprimento (cenEstDem). Ordem nova emitida no cenário (osc.novo)
// entra com a chave, o talhão e a janela dela. Data = máx(hoje, início da janela).
function cenOsDem(c, b) { b = b || {}; const out = []; const vistos = {}; const hoje = b.hoje || ''; const cat = b.cat || {};
  const n2 = (x) => Number(x || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const na = (x) => Number(x || 0).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 2 });
  const safDe = (faz, lab) => ((b.safs || []).find(s => s.faz === faz && String(s.nome).endsWith(String(lab || ''))) || {}).id || '';
  const um = (x, co) => { if (!co || co.etapa === 'Canceladas') return;
    const itens = [];
    if (CEN_FASES_PEND.indexOf(co.etapa) >= 0) { const real = co.realizado || 0; const saldo = real ? (co.saldo || 0) : (co.area || 0); const S = cenOsSup(c, co);
      (co.ins || []).forEach(i => { const s = S[i.p] || { need: 0, cust: 0 }; const cust = Math.min(s.cust, s.bruto); const k = cat[i.p] || {};
        itens.push({ p: i.p, q: s.need, un: i.un, g: k.g || '', preco: k.preco || 0,
          calc: n2(i.dose) + ' ' + i.un + '/ha × ' + na(saldo) + ' ha' + (cust > 0 ? ' − ' + na(cust) + ' ' + i.un + ' em custódia' : '') }); }); }
    if (!(x.chaves || []).length && !itens.some(i => i.q > 0)) return;
    out.push({ id: x.id, faz: x.faz, saf: x.saf, chaves: (x.chaves || []).slice(), area: co.area || 0, dt: (x.ini && x.ini > hoje) ? x.ini : hoje, etapa: co.etapa, t: x.t, loc: (x.loc || []).slice(), itens }); };
  (b.ords || []).forEach(x => { vistos[x.id] = 1; um(x, ((c && c.ordens) || {})[x.id]); });
  Object.keys((c && c.ordens) || {}).forEach(k => { const co = c.ordens[k]; const no = co && co.osc && co.osc.novo; if (vistos[k] || !no) return;
    const faz = no.faz || 'Santa Rita'; const saf = safDe(faz, no.saf || ''); if (!saf) return;
    um({ id: k, faz, saf, chaves: (no.keys || []).slice(), loc: [no.talhao], ini: no.jan || '', t: no.talhao + ' · ' + k + ' · ' + (((no.atv || {}).nome) || no.tipo || '') }, co); });
  return out; }
// fazenda de cada O.S. (custódia é suprimento da fazenda da ordem): as do registro (dados2.os_base) e as emitidas no cenário (osc.novo)
function cenOsFaz(c, osb) { const f = {}; ((osb || {}).ords || []).forEach(x => { f[x.id] = x.faz; });
  Object.keys((c && c.ordens) || {}).forEach(k => { const no = c.ordens[k] && c.ordens[k].osc && c.ordens[k].osc.novo; if (no && !f[k]) f[k] = no.faz || 'Santa Rita'; });
  return f; }
// ---------- CTL-4 (revisão, achado 1, S2) · o estoque da demanda vem do MESMO cenário das ordens: físico apto da fazenda (lote − quarentena;
// inclui as reservas), quarentena, reservas ativas e recebimentos previstos sem o que o Estoque já conferiu da nota do pedido. Entregar move do
// lote para a custódia, devolver faz o inverso, cancelar solta a reserva e receber troca "a receber" por estoque: nada disso muda a compra
// (dano evitado: 8.000 kg de NPK a menos depois de uma entrega comum; 24,5 L de Fungicida A a mais depois de uma devolução). Espelho: dados2.est_dem.
// b (dados2.est_base): {rec:[{item,q,dt,ref,faz,t}] pedidos em aberto da semente, locFaz:{local: fazenda}, faz0 (local fora do mapa), hoje,
// ofaz:{O.S.: fazenda} (cenOsFaz)}. osd: cenOsDem do mesmo cenário (data da reserva = data da ordem). Reserva = a mesma conta do Estoque
// (cenResPropria), só de requisição não cancelada de O.S. em A liberar, Liberadas ou Em execução; chave = ID da O.S. (DEM-04: conta uma vez com
// a ordem). Recebido = o 1º registro de cada recebimento do Estoque (movimento recebimento-nf com estRec: pedido no rótulo "PC-090 · …" e
// quantidade conferida, apta + quarentena).
// Revisão do 853a6a8 (achado 1, S2): custódia que a ordem não vai usar (sobra de cenOsSup: ordem cancelada, em conferência, encerrada, ou o que
// passa do pendente da ativa) é suprimento da fazenda da ordem — sobra:[{item,q,t,chave}], somada ao estoque inicial em demFazenda. Assim
// cancelar com material entregue e devolver a sobra não mudam a compra.
function cenEstDem(c, faz, b, osd) { b = b || {}; const lf = b.locFaz || {}; const fz = (l) => lf[l.local] || b.faz0 || 'Santa Rita';
  const fisico = {}, quar = {}, reservas = [], recebDt = [], sobra = []; const lotes = (c && c.lotes) || {};
  Object.values(lotes).forEach(l => { if (fz(l) !== faz) return; fisico[l.prod] = (fisico[l.prod] || 0) + (l.fisico || 0) - (l.quarentena || 0);
    if ((l.quarentena || 0) > 0) quar[l.prod] = (quar[l.prod] || 0) + l.quarentena; });
  Object.keys((c && c.reqs) || {}).forEach(rid => { const r = c.reqs[rid]; const o = ((c && c.ordens) || {})[r.os]; if (!o) return;
    const l0 = (r.itens || []).map(it => lotes[it.prod + '|' + it.lote]).find(Boolean); const fo = (b.ofaz || {})[r.os] || (l0 ? fz(l0) : (b.faz0 || 'Santa Rita'));
    if (fo === faz) { const S = cenOsSup(c, o, r);
      Object.keys(S).forEach(p => { if (S[p].sobra > 1e-9) sobra.push({ item: p, q: S[p].sobra, t: rid + ' · ' + r.os + ' (' + (o.etapa === 'Canceladas' ? 'cancelada' : (CEN_FASES_PEND.indexOf(o.etapa) >= 0 ? 'sobra da ordem' : o.etapa.toLowerCase())) + ')', chave: r.os, faz }); }); }
    if (r.estado === 'Cancelada' || CEN_FASES_PEND.indexOf(o.etapa) < 0) return; const od = (osd || []).find(x => x.id === r.os);
    (r.itens || []).forEach(it => { const l = lotes[it.prod + '|' + it.lote]; if (!l || fz(l) !== faz) return; const q = cenResPropria(c, rid, it, l); if (!(q > 1e-9)) return;
      reservas.push({ item: it.prod, q, dt: od ? od.dt : (b.hoje || ''), t: 'Reserva ' + rid + ' · ' + r.os + (o.talhao ? ' (' + o.talhao + ')' : ''), chave: r.os, faz }); }); });
  const rc = {}, vis = {};
  ((c && c.movs) || []).forEach(m => { const e = m.tipo === 'recebimento-nf' && m.estRec; if (!e || vis[e.id]) return; vis[e.id] = 1;
    const p = String(e.ped || '').split(' · ')[0].trim(); if (p) rc[p] = (rc[p] || 0) + (Number(e.conf) || 0); });
  (b.rec || []).forEach(r => { if (r.faz !== faz) return; const q = Math.max(0, r.q - (r.ref ? (rc[r.ref] || 0) : 0)); if (q > 1e-9) recebDt.push(Object.assign({}, r, { q })); });
  return { fisico, quar, reservas, recebDt, sobra }; }
// entradas vivas da demanda única (Planejar safra, Mapa › Insumos e Compra de insumos): x = partes fixas (safra, fazenda, hoje, viavel, ordem e
// nomes das safras, ocorrências do plano); b = {osb: dados2.os_base, est: dados2.est_base}. Ordens, estoque, reservas e recebimentos: o cenário c.
function cenDemEntradas(c, x, b) { b = b || {}; const osd = cenOsDem(c, b.osb);
  return Object.assign({}, x, cenEstDem(c, x.faz, Object.assign({ hoje: x.hoje || (b.osb || {}).hoje || '' }, b.est, { ofaz: cenOsFaz(c, b.osb) }), osd), { osd }); }
function cenMov(c, m) { m.id = 'MV-' + (1000 + c.movs.length + 1); m.at = m.at || cenAgora(); c.movs.push(m); return m; }
// Decisão que exige papel (PRD 2.1; DEC-2609-13; CMD-47): o comando recebe quem age (no protótipo, o perfil de demonstração de g2lib.js;
// no software, o ator da sessão no servidor) e confere o papel no cadastro (g2pf). Sem o papel, recusa e nada muda (dano: decisão gravada
// em nome de quem não decidiu). Mesma pessoa no fato e na decisão: a decisão vale e fica "revisão posterior pendente" (padrão adotado em
// 05/10/2026; o proprietário pode mudar). Ação aberta a todos (cenQuem) também exige um perfil do cadastro: nenhum registro grava quem não agiu.
function cenExige(ator, papel, acao) { if (!g2papel(ator, papel)) throw new Error(acao + ': decisão de ' + g2quem(papel) + '. Nada foi alterado.'); return g2ator(ator, papel); }
function cenExigeUm(ator, papeis, acao) { const p = g2umPapel(ator, papeis); if (!p) throw new Error(acao + ': decisão de ' + g2quemUm(papeis) + '. Nada foi alterado.'); return g2ator(ator, p); }   // basta um dos papéis
function cenQuem(ator, papel, acao) { const q = g2ator(ator, papel); if (!q) throw new Error(acao + ': sem o perfil de quem age. Nada foi alterado.'); return q; }
function cenRevisao(ator, autor, fato) { const q = g2pf(ator); return q && g2mesma(q.k, autor) ? 'revisão posterior pendente (' + q.k + ' ' + fato + ' e decidiu)' : ''; }

// ---------- O.S. (web) ----------
// Liberar (agrônomo): reserva cada insumo no lote com saldo (a reserva nunca passa do disponível).
function cenLiberar(c, id) {
  const o = c.ordens[id]; if (!o) throw new Error('Ordem não encontrada.');
  if (o.etapa !== 'A liberar') throw new Error(id + ' não está em A liberar.');
  const rid = o.req || ('REQ-' + (41 + Object.keys(c.reqs).length));
  const req = c.reqs[rid] || (c.reqs[rid] = { id: rid, os: id, itens: [], estado: 'Reservada' });
  (o.ins || []).forEach(x => {
    if (x.dose > 0 && !(x.tot > 0)) throw new Error('Dose × área de ' + x.p + ' dá 0 ' + x.un + ': aumente a dose ou a área.');   // nunca entregaria nada
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
function cenEntregar(c, rid, prod, qtd, quem, ator) {   // ator: quem entrega (perfil); o movimento grava quem agiu, nunca um nome fixo
  const qa = cenQuem(ator, 'almoxarife', 'Entregar ' + prod + ' da ' + rid); const r = c.reqs[rid]; const o = r && c.ordens[r.os]; if (!r || !o) throw new Error('Requisição não encontrada.');
  if (['Liberadas', 'Em execução'].indexOf(o.etapa) < 0) throw new Error('Entregue só para O.S. liberada ou em execução (' + r.os + ' está em ' + o.etapa + ').');
  const it = r.itens.find(i => i.prod === prod); if (!it) throw new Error(prod + ' não está na ' + rid + '.');
  const l = c.lotes[prod + '|' + it.lote]; if (!l) throw new Error('Lote ' + it.lote + ' de ' + prod + ' não encontrado no Estoque.');
  if (!(qtd > 0)) throw new Error('Informe a quantidade.');
  if (qtd > cenSaldoEntregar(it) + 1e-9) throw new Error('Acima do saldo a entregar: ' + cenNum(cenSaldoEntregar(it)) + ' ' + it.un + '.');
  if (qtd > l.fisico - l.quarentena + 1e-9) throw new Error('O lote ' + it.lote + ' não tem ' + cenNum(qtd) + ' ' + it.un + ' livres.');
  l.fisico -= qtd; l.reservado = Math.max(0, l.reservado - qtd); it.entregue += qtd; it.custodia += qtd; it.quem = quem || o.resp;
  r.estado = 'Entregue'; cenMov(c, { tipo: 'entrega', req: rid, os: r.os, prod, lote: it.lote, qtd, un: it.un, quem: qa + ' → ' + (quem || o.resp), origem: 'web' });
  return { msg: cenNum(qtd) + ' ' + it.un + ' de ' + prod + ' entregues a ' + (quem || o.resp) + ' (' + r.os + '). Aguarda confirmação no app.' };
}
// Devolução conferida: só o recebido e conferido volta ao disponível; material bloqueado não volta.
function cenDevolver(c, rid, prod, qtd, apto, ator) {   // ator: quem recebe e confere a devolução (perfil)
  const qa = cenQuem(ator, 'almoxarife', 'Receber a devolução de ' + prod + ' da ' + rid); const r = c.reqs[rid]; const it = r && r.itens.find(i => i.prod === prod); if (!it) throw new Error('Item não encontrado.');
  if (!(qtd > 0) || qtd > it.custodia + 1e-9) throw new Error('Devolva até ' + cenNum(it.custodia) + ' ' + it.un + ' em custódia.');
  const l = c.lotes[prod + '|' + it.lote]; if (!l) throw new Error('Lote ' + it.lote + ' de ' + prod + ' não encontrado no Estoque.');
  it.custodia -= qtd; it.devolvido += qtd;
  if (apto) l.fisico += qtd; else { l.fisico += qtd; l.quarentena += qtd; }
  cenMov(c, { tipo: 'devolucao', req: rid, os: r.os, prod, lote: it.lote, qtd, un: it.un, quem: qa, origem: 'web', apto: !!apto });
  return { msg: cenNum(qtd) + ' ' + it.un + ' de ' + prod + ' devolvidos' + (apto ? ' ao disponível.' : ' e bloqueados para inspeção.') };
}

// Recebimento de fornecedor: conferido entra no lote (novo ou existente); com avaria ou sem laudo entra bloqueado (quarentena).
function cenReceber(c, prod, lote, qtd, un, local, validade, doc, apto, ator) {   // ator: quem confere o recebimento (perfil)
  const qa = cenQuem(ator, 'almoxarife', 'Receber ' + (prod || 'o produto') + ' (' + (doc || 'sem documento') + ')');
  if (!prod || !lote) throw new Error('Informe produto e lote.'); if (!(qtd > 0)) throw new Error('Informe a quantidade recebida.');
  if (!doc) throw new Error('Informe a nota fiscal ou o documento de entrada.');
  const k = prod + '|' + lote; const l = c.lotes[k] || (c.lotes[k] = { prod, lote, local: local || 'Almox. defensivos', un: un || 'L', fisico: 0, quarentena: 0, reservado: 0, validade: validade || '' });
  if (l.un !== (un || l.un)) throw new Error('Unidade diferente do lote ' + lote + ' (' + l.un + ').');
  l.fisico += qtd; if (!apto) l.quarentena += qtd;
  cenMov(c, { tipo: 'recebimento-nf', prod, lote, qtd, un: l.un, quem: qa, origem: 'web', doc, apto: !!apto });
  return { msg: cenNum(qtd) + ' ' + l.un + ' de ' + prod + ' recebidos no lote ' + lote + ' (' + l.local + ')' + (apto ? '.' : ' e bloqueados até a inspeção.') };
}
// Liberar quarentena (RN-015; SU-06 "Liberar qualidade"): só com o nº do laudo ou relatório de inspeção, pelo gestor (padrão adotado, igual ao ajuste)
function cenLiberarQuarentena(c, key, laudo, ator) { const l = c.lotes[key]; if (!l || !(l.quarentena > 0)) throw new Error('Nada bloqueado neste lote.');
  const quem = cenExige(ator, 'gestor', 'Liberar a quarentena do lote ' + l.lote); const doc = String(laudo || '').trim();
  if (!doc) throw new Error('Informe o nº do laudo ou relatório de inspeção do lote ' + l.lote + '. Sem laudo o lote continua bloqueado.');
  // acúmulo (padrão 2): quem registrou a entrada bloqueada (recebimento ou devolução) e libera fica com revisão posterior. Com a entrada gravando
  // quem agiu (revisão do CTL-3, achado 4), a gestora que recebe e libera deixou de ser invisível
  const rev = (c.movs || []).filter(m => m.prod === l.prod && m.lote === l.lote && (m.tipo === 'recebimento-nf' || m.tipo === 'devolucao') && !m.apto)
    .map(m => cenRevisao(ator, m.quem, 'registrou a entrada bloqueada')).find(Boolean) || '';
  const q = l.quarentena; l.quarentena = 0; cenMov(c, Object.assign({ tipo: 'inspecao', prod: l.prod, lote: l.lote, qtd: q, un: l.un, quem, origem: 'web', doc }, rev ? { rev } : {}));
  return { msg: cenNum(q) + ' ' + l.un + ' do lote ' + l.lote + ' liberados com o laudo ' + doc + ' por ' + quem + '.' + (rev ? ' Fica ' + rev + '.' : '') }; }
// Inventário: contagem cega por lote; diferença vira ajuste pendente (o saldo só muda com a aprovação do gestor).
function cenContar(c, key, contado) { const l = c.lotes[key]; if (!l) throw new Error('Lote não encontrado.');
  if (!(contado >= 0) || contado === '' || contado === null) throw new Error('Informe a quantidade contada.');
  const dif = contado - l.fisico; c.ajustes = c.ajustes || [];
  if (Math.abs(dif) < 1e-9) { cenMov(c, { tipo: 'contagem', prod: l.prod, lote: l.lote, qtd: 0, un: l.un, quem: 'Rui (almoxarife)', origem: 'web' }); return { msg: 'Contagem confere: ' + cenNum(contado) + ' ' + l.un + ' no lote ' + l.lote + '.' }; }
  if (contado + 1e-9 < l.reservado + l.quarentena) throw new Error('Contagem abaixo do reservado e bloqueado (' + cenNum(l.reservado + l.quarentena) + ' ' + l.un + '). Recontar antes de ajustar.');
  const aj = { id: 'AJ-' + (70 + c.ajustes.length + 1), key, prod: l.prod, lote: l.lote, un: l.un, sistema: l.fisico, contado, dif, estado: 'Aguardando gestor' }; c.ajustes.push(aj);
  return { msg: 'Divergência de ' + cenNum(dif) + ' ' + l.un + ' no lote ' + l.lote + ' · ' + aj.id + ' aguarda o gestor. O saldo não muda até a aprovação.' }; }
function cenAprovarAjuste(c, id, aprovar, ator) { const aj = (c.ajustes || []).find(a => a.id === id); if (!aj || aj.estado !== 'Aguardando gestor') throw new Error('Ajuste não está pendente.');
  const l = c.lotes[aj.key]; if (aprovar) { const quem = cenExige(ator, 'gestor', 'Aprovar o ajuste ' + (aj.inv || aj.id));
    l.fisico = aj.contado; aj.estado = 'Aprovado'; aj.por = quem; aj.em = cenAgora(); aj.rev = cenRevisao(ator, aj.reg, 'registrou a contagem');
    cenMov(c, { tipo: 'ajuste', prod: aj.prod, lote: aj.lote, qtd: aj.dif, un: aj.un, quem, origem: 'web', rev: aj.rev }); }
  else aj.estado = 'Recusado';   // recusar = recontar: não muda saldo, qualquer contador pede
  return { msg: aj.id + (aprovar ? ' aprovado por ' + aj.por + ': lote ' + aj.lote + ' passa a ' + cenNum(aj.contado) + ' ' + aj.un + '.' + (aj.rev ? ' Fica ' + aj.rev + '.' : '') : ' recusado: recontar o lote ' + aj.lote + '.') }; }

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
// Regra única de início (CMD-07) e de cada turno: todo componente da versão com o executor, entregue e confirmado (PRD 42.2 l.7067;
// ESTOS-03 l.7103; 41.3 l.6864). Dano evitado: aplicar mistura incompleta. Confirmação: a da 1ª entrega de cada item (R7). Entrega parcial da quantidade vale (PRD l.1251): aqui só
// se exige algo de cada componente. Usada pela web (osIniErro), pelo comando do app (cenIniciarTurno) e pelo cartão do app (mbPasso).
// Devolve null ou {k:'entregar'|'rever'|'confirmar', its, t, q}: t = o que falta, q = quem resolve.
function cenIniFalta(o, r) {
  const its = ((o.ins || []).length && r) ? r.itens.filter(i => o.ins.some(x => x.p === i.prod)) : []; if (!its.length) return null;
  const q = i => i.prod + ' ' + cenNum(i.custodia > 1e-6 ? i.custodia : cenSaldoEntregar(i)) + ' ' + i.un;
  const sem = its.filter(i => !(i.custodia > 1e-6)), fal = sem.filter(i => cenSaldoEntregar(i) > 1e-6), esg = sem.filter(i => !(cenSaldoEntregar(i) > 1e-6));
  if (fal.length) return { k: 'entregar', its: fal, t: r.id + ' sem entrega · ' + fal.map(q).join(', ') + ' a entregar.', q: 'Rui (almoxarife) entrega no Estoque; ' + (o.resp || 'o operador') + ' confirma o recebimento no app.' };
  if (esg.length) return { k: 'rever', its: esg, t: esg.map(i => i.prod).join(', ') + ': todo o solicitado na ' + r.id + ' já foi consumido e nada está com ' + (o.resp || 'o operador') + '.', q: 'Ana (agrônoma) decide a área restante: Dispensar saldo na O.S. e, se ainda precisar aplicar, emitir nova ordem.' };
  const nc = its.filter(i => !i.confirmado);
  if (nc.length) { const quem = nc.map(i => i.quem || o.resp).filter((v, k, a) => a.indexOf(v) === k).join(', ');
    return { k: 'confirmar', its: nc, t: nc.map(q).join(', ') + (nc.length > 1 ? ' entregues a ' : ' entregue a ') + quem + ', aguardando confirmação no app.', q: quem + ' confirma o recebimento no app.' }; }
  return null; }
function cenIniciarTurno(c, id) {
  const o = c.ordens[id]; if (!o) throw new Error('Ordem não encontrada.');
  if (['Liberadas', 'Em execução'].indexOf(o.etapa) < 0) throw new Error(id + ' não está liberada para execução.');
  if (c.app.turno && !c.app.turno.fim) throw new Error('Feche o turno aberto antes de iniciar outro.');
  { const f = cenIniFalta(o, o.req && c.reqs[o.req]); if (f) throw new Error('Iniciar bloqueado: ' + f.t + ' ' + f.q); }   // mesma regra da web
  c.app.nt = (c.app.nt || 0) + 1;   // chave do turno, gerada por quem inicia (o aparelho)
  c.app.turno = { os: id, ini: cenAgora(), d: cenDdMm(CEN_DIA_OP), chave: 'TU-' + id + '-' + c.app.nt, pausas: [], fim: null };
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
// quem concilia, texto único (O.S., Mapa, app e encerramento): o almoxarife confere ou recusa; o que passa da custódia é aceite do gestor (padrão 2;
// revisão do CTL-3, achado 7: o texto mandava o excedente para Rui)
function cenConcQuem(c, ks) { const exc = (ks || []).some(k => k.relatado - cenConfCust(c, k) > 1e-9);
  return CEN_CONC_RESP + (exc ? ' confere; ' + g2quem('gestor') + ' aceita o excedente' : ' concilia'); }
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
// ---------- Apontamento: comando único da web (O.S. e Mapa) e do app (PRD 8.5; OSDIA-03/04) ----------
// k = {os, d:'dd/mm' (data operacional), parc (talhão/parcela; vazio = a ordem toda), ha, h, cons {produto: usado informado},
//      est [produtos com a sugestão não editada], origem 'web'|'app', quem, chave (de quem inicia: formulário da web ou turno do app), obs}
// Consumo: informado é o fato; não informado = dose × área do trecho (SINT-C03), só estimativa (CONC-13): acima da custódia, estimativa é
// recusada e informado vai para conferência com o almoxarife (CONC-07). Mesma chave = mesmo apontamento, nada de novo (OSDIA-03).
// Duplicata provável (cenApDup) fica "Duplicidade a conferir": não soma área nem baixa consumo até a decisão (OSDIA-04; PRD 8.5).
const CEN_DIA_OP = '2026-09-26';   // data padrão do apontamento na demonstração: a mesma na O.S., no Mapa e no turno do app
const CEN_AP_DUP = 'Duplicidade a conferir', CEN_AP_DESC = 'Duplicidade · não somado', CEN_CC_AGUARDA = 'Aguarda duplicidade';
const CEN_CONF_AP = 'Paula (conferência)';   // quem confere os apontamentos (campo.QUEM: "Turno do dia 4 aguardando conferência · Paula")
function cenDdMm(iso) { const a = String(iso || '').split('-'); return a.length === 3 ? a[2] + '/' + a[1] : String(iso || ''); }
function cenApSomado(a) { return a.sinc !== false && (a.st === 'Provisório' || a.st === 'Conferido'); }   // entra no realizado, no custo e no acumulado
// duplicata provável: mesma O.S. e data, talhão sobreposto, já recebida pelo servidor, outra chave. Turnos do mesmo operador no app não
// são duplicata entre si (cada um foi aberto e fechado no aparelho, com chave própria).
function cenApDup(o, ap) { const sob = (x, y) => !x || !y || x === y;
  return (o.ap || []).filter(a => a !== ap && a.st !== 'Previsto' && a.st !== CEN_AP_DESC && a.sinc !== false && a.d === ap.d && sob(a.parc, ap.parc)
    && a.chave !== ap.chave && !(a.origem === 'app' && ap.origem === 'app' && a.quem && a.quem === ap.quem)); }
// relatos de dupDe que ainda valem ou aguardam decisão: o estornado ou guardado depois não conta (rótulo, "vale este" e mensagens)
function cenApDupVivos(o, ap) { return (ap.dupDe || []).map(d => (o.ap || []).find(a => a.dia === d)).filter(a => a && (cenApSomado(a) || a.st === CEN_AP_DUP)); }
// o que já foi feito sobre o relato somado K e impede estorná-lo por "vale este": consumo aceito pelo almoxarife (CMD-50) e lote de colheita
// com destino, liberação ou operação (carLoteUso, carência). Devolve o texto ou ''.
function cenApUsoK(c, o, K) {
  const acs = (c.confs || []).filter(k => k.os === o.id && k.dia === K.dia && k.estado === 'Aceito'), ac = acs.map(k => k.id);
  const por = acs.map(k => k.por || CEN_CONC_RESP).filter((x, i, a) => a.indexOf(x) === i).join(', ');   // quem aceitou de fato (padrão 2: o excedente é do gestor)
  const lid = typeof carLid === 'function' ? carLid(o.id, K.dia) : ''; const us = (lid && typeof carLoteUso === 'function') ? carLoteUso(c, lid) : [];
  return [ac.length ? 'consumo já aceito por ' + por + ' (' + ac.join(', ') + ')' : '', us.length ? 'lote ' + lid + ' com ' + us.join(', ') : ''].filter(Boolean).join('; '); }
// estado da decisão antes de gravar: realizado, saldo e custódia depois do estorno de K ("vale este"); pend = área no aparelho (conta no máximo)
function cenApDecBase(c, o, K) { const r = o.req && c.reqs[o.req]; const cust = {};
  if (r) r.itens.forEach(it => { cust[it.prod] = it.custodia + (K ? ((K.cons || {})[it.prod] || 0) : 0); });
  return { r, cust, real: (o.realizado || 0) - (K ? K.ha : 0), saldo: (o.saldo || 0) + (K ? K.ha : 0), pend: (o.ap || []).filter(a => a.sinc === false).reduce((s, a) => s + (a.ha || 0), 0) }; }
// consumo a gravar na decisão: o informado fica; a estimativa é refeita no acumulado de agora (SINT-C03) e, acima da custódia, é recusada como
// na captura (AP-04): falta = o que precisa do usado. us = {produto: usado} informado na conferência (vira informado).
function cenApDecCons(o, ap, b, us) { const cons = Object.assign({}, ap.cons || {}), inf = Object.assign({}, ap.inf || {}), falta = [];
  (o.ins || []).forEach(x => { const it = b.r && b.r.itens.find(i => i.prod === x.p); if (!(x.p in cons) || inf[x.p] || !it) return;
    const u = us ? us[x.p] : undefined; if (u !== undefined && u !== null && u !== '' && Number(u) >= 0) { cons[x.p] = Number(u); inf[x.p] = true; return; }
    const q = cenQtdTrecho(x.dose, b.real + b.pend, ap.ha); cons[x.p] = q; if (q > (b.cust[x.p] || 0) + 1e-9) falta.push({ p: x.p, q, un: it.un, cust: b.cust[x.p] || 0 }); });
  return { cons, inf, falta }; }
// impressão do conteúdo do comando (ENG-021): a mesma chave com outro conteúdo é conflito, não "já registrado"
function cenApImp(k) { const n = x => (x === undefined || x === null || x === '') ? null : Number(x);
  const cs = Object.keys(k.cons || {}).filter(p => k.cons[p] !== undefined && k.cons[p] !== null).sort().map(p => p + '=' + Number(k.cons[p]));
  return JSON.stringify([k.d || '', n(k.ha), n(k.h), k.parc || null, k.origem || 'web', k.quem || '', cs, (k.est || []).slice().sort()]); }
function cenApDupTxt(l) { return l.map(a => 'dia ' + a.dia + ', ' + cenNum(a.ha) + ' ha ' + (a.origem === 'app' ? 'pelo app' + (a.quem ? ' (' + a.quem + ')' : '') : 'pela web')).join('; '); }
function cenSeloAp(c, id) { const o = c.ordens[id]; if (!o) return; const t = 'Apontamento em conferência';
  o.selos = (o.selos || []).filter(s => s.t !== t); if ((o.ap || []).some(a => a.st === CEN_AP_DUP)) o.selos.push({ t, c: 'yellow' }); }
// baixa do consumo do apontamento, uma vez: até a custódia baixa; acima vira conferência com o almoxarife (CONC-07; CMD-50)
function cenApBaixa(c, o, ap) {
  const r = o.req && c.reqs[o.req]; const cons = ap.cons = ap.cons || {}; const inf = ap.inf || {}; const conf = {};
  if (r) for (const it of r.itens) { const q = cons[it.prod] || 0; if (q > it.custodia + 1e-9) conf[it.prod] = { q, it }; }
  Object.keys(inf).forEach(k => { if (!(r && r.itens.some(i => i.prod === k)) && cons[k] > 1e-9) conf[k] = { q: cons[k], it: null }; });
  if (r) r.itens.forEach(it => { if (conf[it.prod]) return; const q = cons[it.prod] || 0; it.consumido += q; it.custodia -= q; });
  Object.keys(cons).forEach(k => { if (conf[k] || !(cons[k] > 0)) delete cons[k]; });   // ap.cons = só o baixado; sem linha 0
  c.movs = c.movs || []; const det = Object.keys(cons).map(k => k + ' ' + cenNum(cons[k], 1)).join(', ');
  const m = (ap.mov && c.movs.find(x => x.id === ap.mov)) || cenMov(c, { tipo: 'consumo', os: o.id, req: o.req || '', qtd: 0, quem: ap.quem || 'web', origem: ap.origem, sinc: ap.sinc !== false, det });
  m.det = det; ap.mov = m.id;
  const ks = Object.keys(conf).map(k => { const x = conf[k]; c.confs = c.confs || [];
    const kc = { id: 'CC-' + (300 + c.confs.length + 1), os: o.id, req: o.req || '', prod: k, lote: x.it ? x.it.lote : '—', un: x.it ? x.it.un : ((o.ins || []).find(i => i.p === k) || {}).un || '',
      relatado: x.q, custodia: x.it ? x.it.custodia : 0, dia: ap.dia, at: ap.at, quem: ap.quem || 'web', resp: CEN_CONC_RESP, estado: 'Em conferência',
      motivo: x.it ? 'Consumo acima da custódia' : 'Consumo sem material em custódia', mov: m.id, sinc: ap.sinc !== false };
    c.confs.push(kc); return kc; });
  if (ks.length) { ap.conf = Object.assign(ap.conf || {}); ks.forEach(k => { ap.conf[k.prod] = k.relatado; }); m.conf = (m.conf || []).concat(ks.map(k => k.id)); cenSeloConf(c, o.id); }
  return ks; }
// chegada ao servidor (comando com sinal ou envio da fila): soma uma vez, ou retém a duplicata provável sem efeito
function cenApEntra(c, o, ap, baixado) {
  const dup = cenApDup(o, ap);
  if (dup.length) { ap.st = CEN_AP_DUP; ap.dupDe = dup.map(a => a.dia);
    if (baixado) { const r = o.req && c.reqs[o.req];   // o aparelho já tinha baixado: desfaz, o relato fica guardado no apontamento
      if (r) r.itens.forEach(it => { const q = (ap.cons || {})[it.prod] || 0; it.consumido -= q; it.custodia += q; });
      (c.confs || []).forEach(k => { if (k.os === o.id && k.dia === ap.dia && k.estado === 'Em conferência') k.estado = CEN_CC_AGUARDA; });
      const mv = ap.mov && (c.movs || []).find(x => x.id === ap.mov); if (mv) { mv.det = ''; mv.obs = 'Retido: mesma data do dia ' + ap.dupDe.join(', ') + '; nada baixado até a decisão de ' + CEN_CONF_AP + '.'; }
      cenSeloConf(c, o.id); }
    cenSeloAp(c, o.id); return { ap, ks: [], dup }; }
  const ks = baixado ? [] : cenApBaixa(c, o, ap);
  o.realizado += ap.ha; o.saldo = Math.max(0, o.saldo - ap.ha);
  return { ap, ks, dup: [] }; }
function cenApontar(c, k) {
  const o = c.ordens[k.os]; if (!o) throw new Error('Ordem não encontrada.');
  const ja = k.chave ? (o.ap || []).find(a => a.chave === k.chave) : null;
  if (ja) { if (ja.imp ? ja.imp !== cenApImp(k) : (ja.ha !== Number(k.ha) || ja.d !== k.d)) throw new Error('Este registro (' + k.chave + ') já foi gravado como dia ' + ja.dia + ' (' + cenNum(ja.ha) + ' ha em ' + ja.d + ') com outro conteúdo: conflito, nada gravado.');   // ENG-021
    return { ap: ja, repetido: true, ks: [], dup: [] }; }
  if (o.etapa !== 'Em execução') throw new Error(k.os + ' não está em execução.');
  if (!/^\d\d\/\d\d$/.test(k.d || '')) throw new Error('Informe a data do turno.');
  const ha = Number(k.ha); if (!(ha > 0)) throw new Error('Informe a área feita (maior que 0 ha).');
  const pend = (o.ap || []).filter(a => a.sinc === false).reduce((s, a) => s + (a.ha || 0), 0);   // no aparelho, ainda sem sinal
  if (ha > o.saldo - pend + 1e-9) throw new Error('Máximo ' + cenNum(Math.max(0, o.saldo - pend)) + ' ha: é o saldo da ordem' + (pend ? ' descontando ' + cenNum(pend) + ' ha ainda no aparelho.' : '.'));
  const cons = {}, es = k.est || [], inf = {};
  Object.keys(k.cons || {}).forEach(p => { const q = k.cons[p]; if (q === undefined || q === null) return; cons[p] = q; if (es.indexOf(p) < 0) inf[p] = true; });
  const r = o.req && c.reqs[o.req];   // não informado: dose × área do trecho para o que está com o operador; fora da requisição, 0 (como no MB-03)
  (o.ins || []).forEach(x => { if (cons[x.p] === undefined) cons[x.p] = (r && r.itens.some(i => i.prod === x.p)) ? cenQtdTrecho(x.dose, (o.realizado || 0) + pend, ha) : 0; });   // regra única (SINT-C03)
  if (r) for (const it of r.itens) { const q = cons[it.prod] || 0; if (q > it.custodia + 1e-9 && !inf[it.prod]) throw new Error('Consumo de ' + it.prod + ' (' + cenNum(q) + ' ' + it.un + ') acima do que está '
    + (k.origem === 'app' ? 'com você (' + cenNum(it.custodia) + ' ' + it.un + '). Confira a retirada.' : 'em custódia (' + cenNum(it.custodia) + ' ' + it.un + '). '
    + (k.cons ? 'Informe quanto foi usado ou confira a entrega no Estoque.' : 'Aponte pela O.S., informando quanto foi usado, ou confira a entrega no Estoque.'))); }
  const quem = k.quem || ((r && (r.itens.find(i => i.quem) || {}).quem) || o.resp || '');   // web: herda quem está com o material (AGENTS §3.3)
  const feitos = (o.ap || []).filter(a => a.st !== 'Previsto'); const dia = feitos.length + 1;
  // previstos são plano, não fato: a web mantém os próximos dias (renumerados) e o app não os guarda — o que cada tela já fazia
  const ap = { d: k.d, dia, ha, h: k.h || null, parc: k.parc || null, st: 'Provisório', cons, inf, obs: k.obs || '', origem: k.origem || 'web', quem,
    chave: k.chave || ((k.origem === 'app' ? 'TU-' : 'W-') + k.os + '-dia' + dia), imp: cenApImp(k), at: cenAgora(), sinc: k.origem === 'app' ? cenOnline(c) : true };
  const reter = ap.sinc && cenApDup(o, ap).length > 0;   // previsto só sai quando o apontamento soma
  const prev = k.origem === 'app' ? [] : (o.ap || []).filter(a => a.st === 'Previsto').slice(reter ? 0 : 1).map((x, i) => Object.assign({}, x, { dia: dia + 1 + i }));
  o.ap = feitos.concat([ap]).concat(prev);
  let R;
  if (ap.sinc) R = cenApEntra(c, o, ap, false);
  else { R = { ap, ks: cenApBaixa(c, o, ap), dup: [] }; c.app.fila.push('AP|' + k.os + '|' + dia); }   // no aparelho: baixa local; o servidor decide no envio
  if (!(o.saldo > 1e-9)) o.ap = o.ap.filter(a => a.st !== 'Previsto');
  return R; }
// decisão de quem confere (CMD-09; papel conferente, CTL-3 · ATOR: só quem tem o papel decide e só o nome dele é gravado). modo: 'somar' (outro turno: soma e baixa uma vez) · 'anterior' (mesmo turno: vale o já
// somado; este fica guardado como duplicidade) · 'este' (mesmo turno: vale este; o já somado é estornado e guardado). O relógio ou a ordem de
// chegada não define o vencedor (DEMO-11). Nenhum relato é apagado. true/false = 'somar'/'anterior' (chamadas antigas). us = usado informado
// na conferência para a estimativa que passou da custódia (AP-04). ator = quem decide (perfil). Tudo é conferido antes de gravar: recusa não muda nada.
function cenApDecidir(c, id, dia, modo, ator, us) {
  const quem = cenExige(ator, 'conferente', 'Decidir a duplicidade do dia ' + dia + ' da ' + id);   // dano evitado: decisão gravada em nome de Paula sem Paula
  modo = modo === true ? 'somar' : (modo === false ? 'anterior' : modo);
  const o = c.ordens[id]; const ap = o && (o.ap || []).find(a => a.dia === dia && a.st === CEN_AP_DUP);
  if (!ap) throw new Error('O apontamento do dia ' + dia + ' não está em conferência de duplicidade.');
  if (['anterior', 'este', 'somar'].indexOf(modo) < 0) throw new Error('Decisão desconhecida: ' + modo + '.');
  const viv = cenApDupVivos(o, ap); const de = viv.map(a => a.dia).join(', '), de0 = (ap.dupDe || []).join(', ');
  const ag = (c.confs || []).filter(k => k.os === id && k.dia === dia && k.estado === CEN_CC_AGUARDA);
  const r = o.req && c.reqs[o.req]; const mvOf = a => a.mov && (c.movs || []).find(x => x.id === a.mov);
  const guarda = (a, txt) => { a.st = CEN_AP_DESC; const m = mvOf(a); if (m) { m.det = ''; m.obs = txt; } };   // det vazio: o Estoque não lê item
  if (modo !== 'somar' && !viv.length) throw new Error('O dia ' + de0 + ' já não vale (estornado ou guardado): o dia ' + dia + ' só pode ser somado como outro turno.');
  if (modo === 'anterior') {
    ap.dec = { modo, quem, at: cenAgora() }; guarda(ap, 'Mesmo turno do dia ' + de + ': guardado como duplicidade, nada baixado.');
    ag.forEach(k => { k.estado = 'Recusado'; k.decisao = 'mesmo turno do dia ' + de; k.por = quem; }); cenSeloAp(c, id); cenSeloConf(c, id);
    return { msg: 'Dia ' + dia + ' guardado como duplicidade do dia ' + de + ': nada foi somado nem baixado; o relato fica no histórico.' }; }
  const K = modo === 'este' ? (viv.length === 1 && cenApSomado(viv[0]) ? viv[0] : null) : null;
  if (modo === 'este') { if (!K) throw new Error('"Vale este" só contra um apontamento já somado: decida antes o dia ' + (de || de0) + '.');
    const uso = cenApUsoK(c, o, K); if (uso) throw new Error('"Vale este" não desfaz o dia ' + K.dia + ': ' + uso + '. Escolha "Mesmo turno: vale o dia ' + K.dia + '".'); }
  const b = cenApDecBase(c, o, K);
  if (ap.ha > b.saldo - b.pend + 1e-9) throw new Error((K ? '"Vale este" com ' : 'Somar ') + cenNum(ap.ha) + ' ha passa do saldo da ordem (' + cenNum(Math.max(0, b.saldo - b.pend)) + ' ha'
    + (b.pend ? ', descontando ' + cenNum(b.pend) + ' ha ainda no aparelho' : '') + ')' + (K ? '.' : ': confira se é o mesmo turno do dia ' + (de || de0) + '.'));
  const dc = cenApDecCons(o, ap, b, us);
  if (dc.falta.length) throw new Error(dc.falta.map(f => f.p + ': a estimativa dose × área (' + cenNum(f.q) + ' ' + f.un + ') passa do que está em custódia (' + cenNum(f.cust) + ' ' + f.un + ')').join('; ')
    + '. Informe o usado' + (ap.quem ? ' (com ' + ap.quem + ')' : '') + ' e decida de novo.');
  ap.dec = { modo, quem, at: cenAgora() }; let est = '';
  if (K) { if (r) r.itens.forEach(it => { const q = (K.cons || {})[it.prod] || 0; it.consumido -= q; it.custodia += q; });   // estorno vinculado (RN-020)
    (c.confs || []).forEach(k => { if (k.os === id && k.dia === K.dia && k.estado === 'Em conferência') { k.estado = 'Recusado'; k.decisao = 'mesmo turno: vale o dia ' + dia; k.por = quem; } });
    o.realizado -= K.ha; o.saldo += K.ha; K.dec = { modo: 'estornado', quem, at: ap.dec.at, vale: dia };
    guarda(K, 'Estornado: mesmo turno do dia ' + dia + ', que ficou valendo.'); est = ' O dia ' + K.dia + ' foi estornado e fica guardado como duplicidade.'; }
  ap.st = 'Provisório'; ag.forEach(k => { k.estado = 'Em conferência'; }); ap.cons = dc.cons; ap.inf = dc.inf;
  const ks = cenApBaixa(c, o, ap); const m0 = mvOf(ap); if (m0) m0.obs = (K ? 'Mesmo turno: vale este dia' : 'Somado como outro turno') + ' · ' + quem + '.';
  o.realizado += ap.ha; o.saldo = Math.max(0, o.saldo - ap.ha); cenSeloAp(c, id); cenSeloConf(c, id);
  if (!(o.saldo > 1e-9)) o.ap = o.ap.filter(a => a.st !== 'Previsto');
  return { msg: 'Dia ' + dia + (K ? ' vale como o turno de ' + ap.d + ': ' : ' somado como outro turno: ') + cenNum(ap.ha) + ' ha · saldo ' + cenNum(o.saldo) + ' ha.' + est
    + (ks.length || ag.length ? ' Consumo em conferência: ' + cenConcQuem(c, ks.concat(ag)) + '.' : '') }; }
// Fechar turno (app): o mesmo comando da web, com a data e a chave do turno. Fechar o turno não encerra a O.S.
function cenFecharTurno(c, ha, horas, consumo, obs, est) {
  const t = c.app.turno; if (!t || t.fim) throw new Error('Nenhum turno aberto.');
  if (!(ha > 0)) throw new Error('Informe os hectares feitos.');
  if (!(horas > 0)) throw new Error('Informe as horas trabalhadas.');
  const R = cenApontar(c, { os: t.os, d: t.d || cenDdMm(CEN_DIA_OP), ha, h: horas, cons: consumo, est, obs, origem: 'app', quem: c.app.operador, chave: t.chave });
  t.fim = cenAgora(); c.app.turno = null; const ap = R.ap;
  if (R.repetido) return { msg: 'Turno já registrado como dia ' + ap.dia + ' (' + cenNum(ap.ha, 1) + ' ha): nada foi somado de novo.' };
  if (R.dup.length) return { msg: 'Turno fechado: ' + cenNum(ha, 1) + ' ha em ' + cenNum(horas, 1) + ' h, em conferência: já há ' + cenApDupTxt(R.dup) + ' em ' + ap.d
    + '. Nada foi somado nem baixado; ' + CEN_CONF_AP + ' decide se é outro turno.' };
  return { msg: 'Turno fechado: ' + cenNum(ha, 1) + ' ha em ' + cenNum(horas, 1) + ' h' + (ap.sinc ? '.' : ' · salvo no aparelho, envia quando houver sinal.') + ' A ordem continua em execução.'
    + (R.ks.length ? ' Consumo em conferência: ' + R.ks.map(k => cenConfTxt(k, c)).join('; ') + ' · ' + cenConcQuem(c, R.ks) + '.' : '') };
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
function cenConciliar(c, id, aceitar, motivo, ator) {
  const p = cenConcPrevia(c, id); const k = p.k, r = p.r, l = p.l; let it = p.it;
  // padrão (2) adotado em 05/10/2026, o proprietário pode mudar: o que passa da custódia sai do lote (como um ajuste) → aceite do gestor
  // coberto pela custódia: baixa a custódia como consumo, conferência física do almoxarife (PRD l.181) ou o gestor (revisão do CTL-3, achado 3;
  // dano evitado: custódia baixada como consumo sem conferência). Recusar não mexe no saldo: aberto, com autor
  const quem = (aceitar && !p.erro && p.falta > 1e-9) ? cenExige(ator, 'gestor', 'Aceitar ' + cenNum(p.falta) + ' ' + k.un + ' acima da custódia (' + k.id + ')')
    : aceitar ? cenExigeUm(ator, ['almoxarife', 'gestor'], 'Aceitar o relato ' + k.id) : cenQuem(ator, 'almoxarife', 'Recusar o relato ' + k.id);
  if (!aceitar) { k.estado = 'Recusado'; k.decisao = motivo || 'registro sem fato físico'; k.por = quem; cenSeloConf(c, k.os);
    return { msg: k.id + ' recusado (' + k.decisao + '): ' + k.prod + ' ' + cenNum(k.relatado) + ' ' + k.un + ' sem efeito no saldo' + (it && it.custodia > 1e-9 ? '; ' + cenNum(it.custodia) + ' ' + it.un + cenPl(it.custodia, ' segue', ' seguem') + ' em custódia com ' + k.quem + '.' : '.') }; }
  if (p.erro) throw new Error(p.erro);
  const falta = p.falta;
  if (falta > 1e-9) {
    l.fisico -= falta; l.reservado = Math.max(0, (l.reservado || 0) - p.res);   // a reserva da própria requisição não fica maior que a necessidade
    if (!it && r) { it = { prod: k.prod, lote: l.lote, un: k.un, emb: '', solicitado: 0, entregue: 0, consumido: 0, devolvido: 0, custodia: 0, confirmado: true }; r.itens.push(it); }
    if (it) { it.entregue += falta; it.custodia += falta; }
    cenMov(c, { tipo: 'entrega', req: k.req, os: k.os, prod: k.prod, lote: l.lote, qtd: falta, un: k.un, quem: quem + ' → ' + k.quem + ' · regularização ' + k.id, origem: 'web', conf: k.id });
  }
  if (it) { it.consumido += k.relatado; it.custodia = Math.max(0, it.custodia - k.relatado); }
  cenMov(c, { tipo: 'consumo', os: k.os, req: k.req, qtd: 0, quem: quem + ' · aceite ' + k.id, origem: 'web', sinc: true, det: k.prod + ' ' + cenNum(k.relatado, 1), conf: k.id });
  const de = falta > 1e-9 ? ' do lote ' + l.lote + (p.res > 1e-9 ? ' (reserva da ' + k.req + ')' : '') : '';
  k.estado = 'Aceito'; k.decisao = falta > 1e-9 ? 'origem ' + cenNum(falta) + ' ' + k.un + de : 'coberto pela custódia'; k.por = quem; cenSeloConf(c, k.os);
  return { msg: k.id + ' aceito: ' + k.prod + ' ' + cenNum(k.relatado) + ' ' + k.un + cenPl(k.relatado, ' baixado', ' baixados') + ' na ' + k.os
    + (falta > 1e-9 ? ' · ' + cenNum(falta) + ' ' + k.un + cenPl(falta, ' regularizado', ' regularizados') + de + '.' : '.') };
}
function cenOcorrencia(c, id, tipo, texto) { if (!texto) throw new Error('Descreva a ocorrência.');
  const oc = { id: 'OC-' + (500 + c.ocorr.length + 1), os: id, tipo, texto, at: cenAgora(), sinc: cenOnline(c) }; c.ocorr.push(oc); if (!oc.sinc) c.app.fila.push(oc.id);
  return { msg: 'Ocorrência ' + oc.id + ' registrada' + (oc.sinc ? '.' : ' no aparelho.') }; }
// Sinal: a fila vai uma vez só; cada apontamento passa pela mesma chegada ao servidor (soma ou fica em conferência de duplicidade).
function cenSinal(c, online) {
  c.app.online = !!online; if (!online) return { msg: 'Sem sinal: o app continua funcionando e guarda os registros.' };
  let n = 0; const ret = [];
  c.app.fila.forEach(k => { if (k.indexOf('AP|') === 0) { const [, id, dia] = k.split('|'); const o = c.ordens[id]; const ap = (o.ap || []).find(a => String(a.dia) === dia && !a.sinc);
      if (ap) { ap.sinc = true; n++;
        if (ap.mov) { const mv = c.movs.find(x => x.id === ap.mov); if (mv) mv.sinc = true; }
        if (ap.conf) (c.confs || []).forEach(q => { if (q.os === id && String(q.dia) === dia) q.sinc = true; });
        const e = cenApEntra(c, o, ap, true); if (e.dup.length) ret.push(id + ' dia ' + dia + ' (mesma data do ' + cenApDupTxt(e.dup) + ')');
        if (ap.conf) cenSeloConf(c, id); } }
    else { const P = c.producao || {}; const m = c.movs.find(x => x.id === k) || c.ocorr.find(x => x.id === k) || (P.cargas || {})[k] || (P.contagens || []).find(x => x.id === k);   // carga e contagem do app (colheita) entram uma vez
      if (m && !m.sinc) { m.sinc = true; n++; } } });
  c.app.fila = []; return { msg: (n ? (n + (n > 1 ? ' registros enviados' : ' registro enviado') + ' ao voltar o sinal.') : 'Sinal de volta. Nada pendente.')
    + (ret.length ? ' Em conferência de duplicidade: ' + ret.join('; ') + '. Nada foi somado; ' + CEN_CONF_AP + ' decide.' : '') };
}
// Encerrar exige apontamentos enviados e nada em custódia (sobra devolvida).
function cenPodeEncerrar(c, id) { const o = c.ordens[id]; const r = o.req && c.reqs[o.req];
  if ((o.ap || []).some(a => a.sinc === false)) return 'Há apontamentos no aparelho aguardando sinal.';
  const dp = (o.ap || []).filter(a => a.st === CEN_AP_DUP); if (dp.length) return 'Apontamento em conferência de duplicidade: ' + dp.map(a => 'dia ' + a.dia + ' (' + a.d + ', ' + cenNum(a.ha) + ' ha)').join(', ') + '. ' + CEN_CONF_AP + ' decide se é outro turno.';
  const cf = cenConfAbertas(c, id); if (cf.length) return 'Consumo em conferência: ' + cf.map(k => cenConfTxt(k, c)).join('; ') + '. No Estoque: ' + cenConcQuem(c, cf) + '.';
  const cust = r ? r.itens.filter(i => i.custodia > 0.001) : []; if (cust.length) return 'Sobra em custódia: ' + cust.map(i => i.prod + ' ' + cenNum(i.custodia) + ' ' + i.un).join(', ') + '. Receba a devolução no Estoque.';
  if (typeof prPodeEncerrar === 'function') { const pm = prPodeEncerrar(c, id); if (pm) return pm; }   // colheita: nenhuma carga a pesar ou sem sinal (R-18)
  return ''; }
