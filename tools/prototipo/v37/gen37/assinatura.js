// ===== Plataforma de assinaturas (PLAT-01) · cobrança SIMULADA: nenhum provedor, nenhuma credencial, nenhum campo de cartão =====
// Estado único: c.assin do cenário salvo (talhao-os-cenario-v1); ausente, vale ASSIN0 (dados_assinatura.py). Este arquivo entra UMA vez
// em toda tela (engine) e não declara nenhum nome de cenario.js: tudo com prefixo assin/ASSIN (RV-01). Página com cenario.js lê por
// cenGet() e grava por cenMudar(); página sem ele só lê (assinLer), com a mesma regra de versão do cenGet (c.v === ASSIN_CENV).
// Preços, mínimo, franquias, trial e régua são exemplo, a decidir pelo proprietário (DEC-01/05/09): vêm de ASSIN_PAR.
// O estado salvo só vale com a versão do seed deste build (ASSIN0.v = versão + resumo do seed, dados_assinatura.py): um estado de outro
// build ou de outro cadastro (KML real no Mac) volta ao seed, como o cenGet faz com o cenário (revisão PLAT, achado 7).
const ASSIN_KEY = 'talhao-os-cenario-v1';
const ASSIN_CADKEY = 'talhao-os-cd01-v1';
let ASSIN_RAW, ASSIN_LIDO = null;
function assinClone(o) { return JSON.parse(JSON.stringify(o)); }
function assinValido(a) { return !!(a && a.v === ASSIN0.v); }
// ---------- leitura do estado (qualquer tela) ----------
function assinLer() {
  if (typeof cenGet === 'function') { const c = cenGet(); return (c && assinValido(c.assin)) ? c.assin : ASSIN0; }
  let raw = null; try { raw = localStorage.getItem(ASSIN_KEY); } catch (e) { raw = null; }
  if (raw !== ASSIN_RAW) { ASSIN_RAW = raw; let c = null; try { c = raw ? JSON.parse(raw) : null; } catch (e) { c = null; }
    ASSIN_LIDO = (c && c.v === ASSIN_CENV && assinValido(c.assin)) ? c.assin : null; }
  return ASSIN_LIDO || ASSIN0; }
// toda gravação começa aqui: o cenário salvo sem assinatura (ou com a de outro build) ganha a cópia do seed
function assinGarante(c) { if (!assinValido(c.assin)) c.assin = assinClone(ASSIN0); return c.assin; }
// Outras telas (quadros do Canvas) redesenham só quando muda o que mostram (achado 11): a faixa muda com estado, dias e data;
// o cadastro só interessa a quem mede a área (CF-05, BO-01, BO-02: cad = true). As telas com cenario.js já ouvem o cenário por cenOuvir.
function assinSig() { const A = assinLer(); const org = A.orgs[A.demo]; const e = assinEstado(org, A.hoje); return [e.t, e.dias, A.hoje, e.fat ? e.fat.comp : ''].join('|'); }
function assinOuvir(self, cad) { if (!self) return; if (cad) self.__assinCad = true; if (self.__assinOuv) return; self.__assinOuv = true;
  try { window.addEventListener('storage', (e) => {
    if (e.key === ASSIN_CADKEY && self.__assinCad) self.setState({ assinrev: Date.now() });
    else if (e.key === ASSIN_KEY && assinSig() !== self.__assinSig) self.setState({ assinrev: Date.now() }); }); } catch (e) {} }
// quem age (achado 4): o perfil da casca (CF-05 "Ana · Gestora"; plataforma "Admin plataforma"); depois, o g2perfil da frente D
function assinQuem(por) { const p = String(por || '').trim(); if (!p) throw new Error('Quem age não foi identificado: reabra a tela.'); return p; }
// ---------- datas (ISO aaaa-mm-dd) e formatos ----------
const ASSIN_MES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
function assinD(iso) { const a = String(iso).split('-').map(Number); return Date.UTC(a[0], a[1] - 1, a[2] || 1); }
function assinDias(de, ate) { return Math.round((assinD(ate) - assinD(de)) / 864e5); }
function assinIso(ms) { const d = new Date(ms); return d.getUTCFullYear() + '-' + String(d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(d.getUTCDate()).padStart(2, '0'); }
function assinMais(iso, n) { return assinIso(assinD(iso) + n * 864e5); }
function assinMesSeg(iso) { const a = String(iso).split('-').map(Number); return assinIso(Date.UTC(a[1] === 12 ? a[0] + 1 : a[0], a[1] === 12 ? 0 : a[1], 1)); }
function assinFimMes(comp) { return assinMais(assinMesSeg(comp + '-01'), -1); }
function assinBr(iso) { if (!iso) return '—'; const a = String(iso).split('-'); return a[2] + '/' + a[1] + '/' + a[0]; }
function assinBrC(iso) { if (!iso) return '—'; const a = String(iso).split('-'); return a[2] + '/' + a[1]; }
function assinComp(comp) { const a = String(comp).split('-'); return ASSIN_MES[Number(a[1]) - 1] + '/' + a[0]; }
function assinNf(n, dmin, dmax) { return Number(n || 0).toLocaleString('pt-BR', { minimumFractionDigits: dmin, maximumFractionDigits: dmax }); }
function assinR(x) { return 'R$ ' + assinNf(x, 2, 2); }
function assinHa(x) { return assinNf(x, 0, 2) + ' ha'; }
function assinNum(s) { if (typeof s === 'number') return s; let t = String(s == null ? '' : s).trim().replace(/\s|ha$/gi, ''); if (!t) return NaN;
  if (t.indexOf(',') >= 0) t = t.replace(/\./g, '').replace(',', '.'); else if (/^\d{1,3}(\.\d{3})+$/.test(t)) t = t.replace(/\./g, '');
  return /^-?\d+(\.\d+)?$/.test(t) ? Number(t) : NaN; }
// centavos (ou centésimos de ha) inteiros: totais e rodapés somam inteiros, nunca ponto flutuante (R3)
function assinCent(x) { return Math.round(Number(x || 0) * 100); }
// ---------- planos e mensalidade (R2, R3: uma função para CF-05, BO-01, BO-02 e prévia) ----------
function assinPlano(id) { return ASSIN_PAR.planos.find(p => p.id === id) || null; }
function assinMensalidade(plano, medida, contratada, credito) {
  const P = typeof plano === 'string' ? assinPlano(plano) : plano; if (!P) throw new Error('Plano desconhecido: ' + plano + '.');
  const med = Number(medida) || 0; const temC = !(contratada === null || contratada === undefined || contratada === '');
  const cobrada = ASSIN_PAR.base === 'contratada' && temC ? Number(contratada) : (temC ? Math.min(med, Number(contratada)) : med);   // R2 (DEC-01)
  if (!P.pago) return { cobrada, bruto: 0, minimo: 0, minimoAplicado: false, credito: 0, sobra: assinCent(credito) / 100, valor: 0 };
  const bruto = cenQtd(P.preco, cobrada);                     // decimal exato, 2 casas, meio para cima (regra única, cenario.js)
  const base = Math.max(P.minimo, bruto);                     // o mínimo é o maior, não se soma (PRECO-03)
  const cred = Math.min(assinCent(base), assinCent(credito)); // crédito do período nunca deixa o valor negativo; o que sobra segue (achado 2)
  return { cobrada, bruto, minimo: P.minimo, minimoAplicado: P.minimo > bruto, credito: cred / 100, sobra: (assinCent(credito) - cred) / 100, valor: (assinCent(base) - cred) / 100 }; }
// R7: área contratada no aceite ≥ medida do dia e ≤ limite do plano
function assinSugere(medida) { return Math.min(Math.ceil((Number(medida) || 0) / 100) * 100, ASSIN_PAR.limite_ha); }   // medida arredondada à centena, no teto do plano
function assinValidaArea(ha, medida) { const n = assinNum(ha);
  if (!(n > 0)) return 'Informe a área contratada em ha (ex.: ' + assinNf(assinSugere(medida), 0, 0) + ').';
  if (assinCent(n) < assinCent(medida)) return 'A área contratada (' + assinHa(n) + ') não pode ficar abaixo da medida hoje (' + assinHa(medida) + ').';
  if (n > ASSIN_PAR.limite_ha) return 'Acima de ' + assinNf(ASSIN_PAR.limite_ha, 0, 0) + ' ha: proposta empresarial, a decidir pelo proprietário.';
  return ''; }
// ---------- medição (R1): mesma regra de mescla do tmBase (talmapa.js): o salvo primeiro, a base para os ids que faltam ----------
function assinCadSalvo() { try { return JSON.parse(localStorage.getItem(ASSIN_CADKEY) || 'null'); } catch (e) { return null; } }
function assinMedir(cad0, salvo) { const st = salvo || {}; const cp = x => ({ id: x.id, v: Object.assign({}, x.v) });
  const faz = (st.faz || []).map(cp), tal = (st.tal || []).map(cp);
  (cad0.faz || []).forEach(f => { if (!faz.some(x => x.id === f.id)) faz.push(cp(f)); });
  (cad0.tal || []).forEach(t => { if (!tal.some(x => x.id === t.id)) tal.push(cp(t)); });
  const inat = {}; faz.forEach(f => { if (f.v.sit === 'Inativa') inat[f.v.nome] = true; });
  let cent = 0, n = 0; const linhas = tal.map(t => { const d = assinNum(t.v.decl); const ok = t.v.sit !== 'Inativo' && !inat[t.v.faz] && d > 0;
    if (ok) { cent += assinCent(d); n++; }
    return { id: t.id, faz: t.v.faz || '', t: t.v.t || t.id, decl: isNaN(d) ? 0 : d, conta: ok, contorno: t.v.geo === 'poly' || (t.v.calc !== '' && t.v.calc !== undefined && t.v.calc !== null),
      sit: ok ? 'Conta na medição' : (t.v.sit === 'Inativo' ? 'Inativo · fora' : (inat[t.v.faz] ? 'Fazenda inativa · fora' : 'Sem área · fora')) }; });
  return { ha: cent / 100, cent, n, linhas }; }
function assinOrgMedida(org, cad0, salvo) { return org.demo ? assinMedir(cad0, salvo).ha : Number(org.medida_inf) || 0; }
// ---------- contrato, faturas e estado (R6, R9, R10) ----------
function assinContrato(org, dia) { const ks = (org.contratos || []).filter(k => assinD(k.desde) <= assinD(dia)).sort((a, b) => a.v - b.v); return ks[ks.length - 1] || (org.contratos || [])[0]; }
function assinAgendado(org, hoje) { return (org.contratos || []).filter(k => assinD(k.desde) > assinD(hoje)).sort((a, b) => b.v - a.v)[0] || null; }
function assinFatEstado(f, hoje) { if (f.st === 'paga') return 'Paga'; if (f.st === 'pendente') return 'Pendente'; if (f.st === 'contestada') return 'Em contestação';
  if (f.st === 'medicao') return 'Em medição'; return assinDias(f.venc, hoje) > 0 ? 'Vencida' : 'A vencer'; }
const ASSIN_FCOR = { 'Paga': 'green', 'Pendente': 'gray', 'Em contestação': 'yellow', 'Em medição': 'gray', 'A vencer': 'yellow', 'Vencida': 'red' };
function assinAtraso(f, hoje) { return f.st === 'aberta' ? Math.max(0, assinDias(f.venc, hoje)) : 0; }   // Pendente e Em contestação não contam dias
function assinAberta(org) { return (org.faturas || []).filter(f => f.st === 'aberta').sort((a, b) => (a.comp < b.comp ? -1 : 1))[0] || null; }
function assinEstado(org, hoje) {
  if (org.cancelada && assinD(org.cancelada) < assinD(hoje)) return { t: 'Cancelada', c: 'gray', dias: 0, fat: null };
  const k = assinContrato(org, hoje); if (k && k.plano === 'aval') return { t: 'Em avaliação', c: 'gray', dias: 0, fat: null };
  let pior = null; (org.faturas || []).forEach(f => { const d = assinAtraso(f, hoje); if (d > 0 && (!pior || d > pior.dias)) pior = { dias: d, fat: f }; });
  if (!pior) return { t: 'Ativa', c: 'green', dias: 0, fat: null };
  return pior.dias > ASSIN_PAR.dias_aviso ? { t: 'Inadimplente', c: 'red', dias: pior.dias, fat: pior.fat } : { t: 'Em atraso', c: 'yellow', dias: pior.dias, fat: pior.fat }; }
// R14: uma primária no CF-05; medida acima do teto dos planos → proposta empresarial (achado 10: ampliar ali seria recusado sempre)
function assinPrimaria(org, hoje, medida) { if (assinAberta(org)) return 'pagar'; if (assinCent(medida) > assinCent(ASSIN_PAR.limite_ha)) return 'proposta';
  const k = assinContrato(org, hoje); const ag = assinAgendado(org, hoje);
  if (k && assinCent(medida) > assinCent((ag || k).ha)) return 'ampliar'; return 'alterar'; }
function assinCreditoDe(org, comp) { return (org.creditos || []).filter(x => x.comp === comp).reduce((s, x) => s + assinCent(x.valor), 0) / 100; }
function assinPor(por) { return por ? ' · por ' + por : ''; }
// medida do período (achado 3): a maior entre a da abertura do período (gravada quando ele abre) e a do fechamento (ou de hoje, na prévia).
// Inativar um talhão antes do fechamento não reduz o mês em curso; reativá-lo depois do fechamento entra no mês seguinte.
function assinMedPeriodo(org, comp, med) { const ab = (org.aberturas || {})[comp] || null; const piso = !!ab && assinCent(ab.ha) > assinCent(med.ha);
  return { ha: piso ? ab.ha : med.ha, n: piso ? ab.n : med.n, piso, abertura: ab ? ab.ha : null, abertura_d: ab ? ab.d : null, fech: med.ha }; }
// período aberto (Em medição): prévia ao vivo, nunca gravada até fechar
function assinPrevia(org, hoje, medida, ntal) { const comp = String(hoje).slice(0, 7); const k = assinContrato(org, assinFimMes(comp));
  const mp = assinMedPeriodo(org, comp, { ha: medida, n: ntal });
  const m = assinMensalidade(k.plano, mp.ha, k.plano === 'aval' ? null : k.ha, assinCreditoDe(org, comp));
  return { id: org.id + '-' + comp, comp, st: 'medicao', valor: m.valor, emitida: assinMesSeg(hoje), venc: assinMesSeg(hoje), previa: true, eventos: [],
    copia: { medida: mp.ha, ntal: mp.n, contratada: k.ha, cobrada: m.cobrada, plano: k.plano, preco: (assinPlano(k.plano) || {}).preco, minimo: m.minimo, versao: 'v' + k.v,
      aceite_por: k.por || null, fechamento: assinFimMes(comp), credito: m.credito, saldo: m.sobra, saldo_comp: assinMesSeg(comp + '-01').slice(0, 7), bruto: m.bruto,
      abertura: mp.abertura, abertura_d: mp.abertura_d, fech: mp.fech, piso: mp.piso, hoje } }; }
// ---------- comandos (gravam por cenMudar; idempotência pela chave de quem inicia, R8) ----------
function assinChave(p) { return p + '-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8); }
function assinRecibo(A, pre) { A.seq = Object.assign({}, A.seq); A.seq[pre] = (A.seq[pre] || 0) + 1; return pre + '-' + String(A.seq[pre]).padStart(4, '0'); }   // uma sequência por tipo de recibo
function assinFechar(A, org, comp, med) {
  const id = org.id + '-' + comp; if ((org.faturas || []).some(f => f.id === id)) return null;   // fechada uma vez; nunca recalculada (R4)
  const fim = assinFimMes(comp), emis = assinMesSeg(comp + '-01'); const k = assinContrato(org, fim); const P = assinPlano(k.plano);
  const mp = assinMedPeriodo(org, comp, med); const prox = assinMesSeg(comp + '-01').slice(0, 7);
  const cred = assinCreditoDe(org, comp); const m = assinMensalidade(k.plano, mp.ha, k.plano === 'aval' ? null : k.ha, cred);
  const f = { id, comp, st: 'aberta', valor: m.valor, emitida: emis, venc: assinMais(emis, ASSIN_PAR.dia_venc - 1), paga: null, evt: null, forma: null, recibo: null, tent: [], contest: null,
    copia: { medida: mp.ha, ntal: mp.n, contratada: k.ha, cobrada: m.cobrada, plano: k.plano, preco: P.preco, minimo: P.minimo, versao: 'v' + k.v, aceite_por: k.por || null,
      fechamento: fim, credito: m.credito, saldo: m.sobra, saldo_comp: prox, bruto: m.bruto, abertura: mp.abertura, abertura_d: mp.abertura_d, fech: mp.fech, piso: mp.piso },
    eventos: [{ d: emis, t: 'Emitida · ' + assinR(m.valor) + (m.credito ? ' (crédito de ' + assinR(m.credito) + ' aplicado' + (m.sobra ? '; saldo de ' + assinR(m.sobra) + ' para ' + assinComp(prox) : '') + ')' : '') }] };
  // o crédito que passa da fatura não some: vira saldo da competência seguinte (achado 2)
  if (m.sobra > 0) org.creditos = (org.creditos || []).concat([{ comp: prox, valor: m.sobra, saldo_de: id }]);
  // fatura de R$ 0,00 (crédito cobriu tudo) nasce quitada: não pede pagamento nem conta atraso
  if (assinCent(m.valor) === 0) { f.st = 'paga'; f.paga = emis; f.forma = m.credito ? 'crédito' : '—'; f.eventos.push({ d: emis, t: m.credito ? 'Quitada pelo crédito · nada a pagar' : 'Sem valor a pagar' }); }
  org.faturas.push(f); return f; }
// painel Demonstração: avança só a data da cobrança (PLAT-D13); cada mês que termina fecha com a medição do momento (med = {ha, n})
function assinAvancar(c, data, med) { const A = assinGarante(c);
  if (assinD(data) <= assinD(A.hoje)) throw new Error('A data simulada só avança: a cobrança já está em ' + assinBr(A.hoje) + '.');
  const org = A.orgs[A.demo]; const novas = []; let comp = A.hoje.slice(0, 7);
  while (assinD(assinMesSeg(comp + '-01')) <= assinD(data)) { const f = assinFechar(A, org, comp, med); if (f) novas.push(f); comp = assinMesSeg(comp + '-01').slice(0, 7);
    org.aberturas = Object.assign({}, org.aberturas); if (!org.aberturas[comp]) org.aberturas[comp] = { ha: med.ha, n: med.n, d: comp + '-01' }; }   // piso do período que abre (achado 3)
  A.hoje = data;
  return { msg: 'Data simulada da cobrança: ' + assinBr(data) + (novas.length ? ' · ' + novas.map(f => assinComp(f.comp) + ' fechou com ' + assinHa(f.copia.medida) + (f.copia.piso ? ' (medida da abertura, ' + assinHa(f.copia.fech) + ' no fechamento)' : '') + ' → ' + assinR(f.valor) + ', vence ' + assinBrC(f.venc)).join(' · ') : '') + '.', novas }; }
// Todo comando recusa sem chave (idempotência de quem inicia, R8) e sem quem age (achado 4); a chave repetida devolve o mesmo recibo.
function assinIni(c, chave, por, oque) { const A = assinGarante(c); if (!chave) throw new Error(oque + ' sem chave: reabra o painel.'); return { A, por: assinQuem(por), r0: (A.recibos || {})[chave] || null }; }
function assinPagar(c, fatId, forma, chave, por) { const { A, por: q, r0 } = assinIni(c, chave, por, 'Pagamento');
  if (r0) return { msg: 'Pagamento já registrado · recibo ' + r0.id + ' · nada foi cobrado de novo.', recibo: r0, repetido: true };
  const org = A.orgs[A.demo]; const f = (org.faturas || []).find(x => x.id === fatId); if (!f) throw new Error('Fatura não encontrada.');
  if (f.st === 'paga') throw new Error('A fatura de ' + assinComp(f.comp) + ' já está paga (' + (f.recibo || f.evt) + '): nada foi cobrado de novo.');
  if (f.st === 'contestada') throw new Error('Fatura de ' + assinComp(f.comp) + ' em contestação: aguarde a resolução da plataforma.');
  if (f.st !== 'aberta') throw new Error('A fatura de ' + assinComp(f.comp) + ' não está aberta para pagamento.');
  if (ASSIN_PAR.formas.indexOf(forma) < 0) throw new Error('Escolha a forma de pagamento.');
  const rid = assinRecibo(A, 'PAG'); const evt = 'evt_sim_' + rid.slice(4);
  f.st = 'paga'; f.paga = A.hoje; f.evt = evt; f.forma = forma; f.recibo = rid; f.paga_por = q; A.vistos.push(evt);
  f.eventos.push({ d: A.hoje, t: 'Paga · ' + evt + ' · ' + forma + ' (simulado) · recibo ' + rid + assinPor(q) });
  const rec = { id: rid, fat: f.id, valor: f.valor, forma, evt, d: A.hoje, por: q }; A.recibos[chave] = rec;
  return { msg: 'Pagamento simulado confirmado: ' + assinComp(f.comp) + ' · ' + assinR(f.valor) + ' · ' + forma + ' · recibo ' + rid + '. Nenhum valor foi cobrado de verdade.', recibo: rec }; }
// aceite de mudança de plano ou área: vale do dia 1 do próximo ciclo, nunca retroage (R6); substitui a mudança agendada
function assinMudar(c, plano, ha, medida, chave, por) { const { A, por: q, r0 } = assinIni(c, chave, por, 'Aceite');
  if (r0) return { msg: (r0.desfeito ? 'Mudança já desfeita · ' : 'Aceite já registrado · ') + r0.id + ' · nada mudou de novo.', recibo: r0, repetido: true };
  const P = assinPlano(plano); if (!P || !P.pago) throw new Error('Escolha o plano: Essencial ou Completo.');
  const e = assinValidaArea(ha, medida); if (e) throw new Error(e);
  const n = assinNum(ha); const org = A.orgs[A.demo]; const atual = assinContrato(org, A.hoje); const ag = assinAgendado(org, A.hoje);
  if (ag && ag.plano === plano && assinCent(ag.ha) === assinCent(n)) throw new Error('Esta mudança já está agendada para ' + assinBr(ag.desde) + '.');
  if (atual.plano === plano && assinCent(atual.ha) === assinCent(n)) { if (!ag) throw new Error('Nada muda: plano e área iguais aos de hoje.'); return assinDesfazer(c, chave, q); }   // a chave guarda o recibo (achado 6)
  const desde = assinMesSeg(A.hoje); org.contratos = org.contratos.filter(k => assinD(k.desde) <= assinD(A.hoje));
  const v = Math.max.apply(null, org.contratos.map(k => k.v)) + 1; const rid = assinRecibo(A, 'ACE');
  org.contratos.push({ v, plano, ha: n, desde, aceite: A.hoje, recibo: rid, por: q });
  const m = assinMensalidade(plano, medida, n, 0); A.recibos[chave] = { id: rid, v, plano, ha: n, desde, por: q };
  return { msg: 'Aceite registrado (' + rid + '): contrato v' + v + ' · ' + P.nome + ' · ' + assinHa(n) + ' a partir de ' + assinBr(desde) + ' · ' + assinR(m.valor) + '/mês com a área medida hoje.', recibo: A.recibos[chave] }; }
// desfazer guarda o contrato desfeito (nada se apaga) e quem desfez
function assinDesfazer(c, chave, por) { const { A, por: q, r0 } = assinIni(c, chave, por, 'Desfazer');
  if (r0) return { msg: 'Mudança já desfeita · ' + r0.id + ' · nada mudou de novo.', recibo: r0, repetido: true };
  const org = A.orgs[A.demo]; const ag = assinAgendado(org, A.hoje);
  if (!ag) throw new Error('Não há mudança agendada para desfazer.');
  const rid = assinRecibo(A, 'DES'); org.desfeitos = (org.desfeitos || []).concat(org.contratos.filter(k => assinD(k.desde) > assinD(A.hoje)).map(k => Object.assign({}, k, { desfeito: A.hoje, desfeito_por: q, desfeito_recibo: rid })));
  org.contratos = org.contratos.filter(k => assinD(k.desde) <= assinD(A.hoje)); const k = assinContrato(org, A.hoje);
  A.recibos[chave] = { id: rid, desfeito: true, v: ag.v, por: q };
  return { msg: 'Mudança desfeita (' + rid + '): segue ' + (assinPlano(k.plano) || {}).nome + ' · ' + assinHa(k.ha) + ' (contrato v' + k.v + ').', recibo: A.recibos[chave] }; }
// medida acima do teto dos planos: pedido de proposta empresarial (registro; nenhuma mensagem real é enviada)
function assinProposta(c, medida, chave, por) { const { A, por: q, r0 } = assinIni(c, chave, por, 'Pedido');
  if (r0) return { msg: 'Pedido já registrado · ' + r0.id + ' · nada mudou de novo.', recibo: r0, repetido: true };
  const org = A.orgs[A.demo];
  if (org.proposta) throw new Error('Proposta empresarial já pedida em ' + assinBr(org.proposta.d) + ' (' + org.proposta.recibo + '): a plataforma responde.');
  if (!(assinCent(medida) > assinCent(ASSIN_PAR.limite_ha))) throw new Error('Até ' + assinNf(ASSIN_PAR.limite_ha, 0, 0) + ' ha os planos cobrem a área: use Alterar plano ou área.');
  const rid = assinRecibo(A, 'PRO'); org.proposta = { d: A.hoje, ha: Number(medida), por: q, recibo: rid }; A.recibos[chave] = { id: rid, por: q };
  return { msg: 'Pedido de proposta empresarial registrado (' + rid + '): ' + assinHa(medida) + ' medidos, acima de ' + assinNf(ASSIN_PAR.limite_ha, 0, 0) + ' ha. A cobrança segue o contrato de hoje até o aceite da proposta. Nenhuma mensagem real foi enviada.', recibo: A.recibos[chave] }; }
// plataforma: processa os eventos do provedor (simulado) uma vez cada (R9)
function assinConciliar(c, chave, por) { const { A, por: q, r0 } = assinIni(c, chave, por, 'Conciliação');
  if (r0) return { msg: 'Conciliação já registrada (' + r0.id + '): nada novo.', recibo: r0, repetido: true };
  let ok = 0, rec = 0;
  (A.fila || []).forEach(ev => { if (A.vistos.indexOf(ev.evt) >= 0) return; A.vistos.push(ev.evt); const org = A.orgs[ev.org]; const f = org && (org.faturas || []).find(x => x.id === ev.fat); if (!f) return;
    if (ev.ok) { if (f.st !== 'paga') { f.st = 'paga'; f.paga = ev.d; f.evt = ev.evt; f.forma = ev.forma; f.paga_por = q; f.eventos.push({ d: ev.d, t: 'Paga · ' + ev.evt + ' · ' + ev.forma + ' (simulado) · conciliado em ' + assinBrC(A.hoje) + assinPor(q) }); } ok++; }
    else { f.eventos.push({ d: ev.d, t: 'Pagamento avulso recusado · ' + ev.evt + ' · ' + ev.forma + ' · ' + ev.motivo + ' · conciliado em ' + assinBrC(A.hoje) + assinPor(q) }); rec++; } });
  if (!ok && !rec) return { msg: 'Nenhum evento novo do provedor (simulado): nada mudou.' };
  const rid = assinRecibo(A, 'CON'); A.recibos[chave] = { id: rid, ok, rec, por: q };
  return { msg: 'Conciliado (' + rid + '): ' + ok + (ok === 1 ? ' pagamento aprovado' : ' pagamentos aprovados') + ' · ' + rec + (rec === 1 ? ' recusa registrada' : ' recusas registradas') + ' · cada evento conta uma vez.', recibo: A.recibos[chave] }; }
// contestação mínima (R16): uma por fatura (achado 1); congela a régua da fatura; a fatura contestada nunca é reescrita
function assinPodeContestar(f) { return !!f && f.st === 'aberta' && !(f.contest && f.contest.resolvida); }
function assinContestar(c, fatId, motivo, chave, por) { const { A, por: q, r0 } = assinIni(c, chave, por, 'Contestação');
  if (r0) return { msg: 'Contestação já registrada (' + r0.id + ').', recibo: r0, repetido: true };
  const org = A.orgs[A.demo]; const f = (org.faturas || []).find(x => x.id === fatId); if (!f) throw new Error('Fatura não encontrada.');
  if (f.contest && f.contest.resolvida) throw new Error('A fatura de ' + assinComp(f.comp) + ' já foi contestada e resolvida (' + f.contest.res + ' em ' + assinBrC(f.contest.resolvida) + '): uma contestação por fatura.');
  if (f.st !== 'aberta') throw new Error('Só fatura a vencer ou vencida pode ser contestada.');
  const m = String(motivo || '').trim(); if (m.length < 5) throw new Error('Escreva o motivo da contestação.');
  const rid = assinRecibo(A, 'CTS'); f.st = 'contestada'; f.contest = { motivo: m, d: A.hoje, recibo: rid, por: q };
  f.eventos.push({ d: A.hoje, t: 'Contestada (' + rid + ')' + assinPor(q) + ': ' + m + ' · régua congelada até a resolução' }); A.recibos[chave] = { id: rid, fat: f.id, por: q };
  return { msg: 'Contestação registrada (' + rid + '): a fatura de ' + assinComp(f.comp) + ' não conta atraso nem restringe nada até a plataforma resolver.' }; }
function assinResolver(c, orgId, fatId, decisao, credito, chave, por) { const { A, por: q, r0 } = assinIni(c, chave, por, 'Resolução');
  if (r0) return { msg: 'Resolução já registrada (' + r0.id + ').', recibo: r0, repetido: true };
  const org = A.orgs[orgId]; const f = org && (org.faturas || []).find(x => x.id === fatId); if (!f) throw new Error('Fatura não encontrada.');
  if (f.st !== 'contestada') throw new Error('A fatura não está em contestação.');
  const venc = assinMais(A.hoje, ASSIN_PAR.contest_dias); let txt, cr = 0;
  if (decisao === 'creditar') { cr = assinNum(credito);
    if (!(cr > 0)) throw new Error('Informe o crédito em R$.');
    const ja = (org.creditos || []).filter(x => x.origem === f.id).reduce((s, x) => s + assinCent(x.valor), 0);   // teto pelo total já creditado desta fatura (achado 1)
    if (ja + assinCent(cr) > assinCent(f.valor)) throw new Error('O crédito não pode passar do valor da fatura (' + assinR(f.valor) + (ja ? '; já creditado ' + assinR(ja / 100) : '') + ').');
    const prox = String(A.hoje).slice(0, 7); org.creditos = (org.creditos || []).concat([{ comp: prox, valor: assinCent(cr) / 100, origem: f.id }]);
    txt = 'crédito de ' + assinR(cr) + ' na fatura de ' + assinComp(prox) + ' (o que passar dela segue para o mês seguinte)'; }
  else if (decisao === 'manter') txt = 'valor mantido';
  else throw new Error('Escolha a decisão: manter o valor ou creditar no próximo período.');
  const rid = assinRecibo(A, 'RES'); f.st = 'aberta'; f.venc = venc; f.contest = Object.assign({}, f.contest, { decisao, credito: cr ? assinCent(cr) / 100 : 0, resolvida: A.hoje, res: rid, res_por: q });
  f.eventos.push({ d: A.hoje, t: 'Contestação resolvida (' + rid + ')' + assinPor(q) + ': ' + txt + ' · novo vencimento ' + assinBr(venc) + ' · fatura não reescrita' });
  A.recibos[chave] = { id: rid, fat: f.id, por: q };
  return { msg: 'Contestação de ' + org.nome + ' resolvida (' + rid + '): ' + txt + ' · novo vencimento ' + assinBr(venc) + '.' }; }
// carteira da plataforma (BO-02): mensalidade vigente (contrato de hoje, sem crédito), estados, faturas abertas e área cobrada;
// a organização da demonstração é medida ao vivo pela mesma função do CF-05, nunca copiada do seed (RV-04)
function assinCarteira(A, cad0, salvo) { const med0 = assinMedir(cad0, salvo); const o = { vig: 0, n: {}, abertas: 0, abertasV: 0, cobrada: 0, medida: 0, linhas: [], porFaz: [] };
  Object.keys(A.orgs).forEach(id => { const org = A.orgs[id]; const e = assinEstado(org, A.hoje); const k = assinContrato(org, A.hoje);
    const med = org.demo ? med0.ha : (Number(org.medida_inf) || 0); const pag = e.t !== 'Cancelada' && k.plano !== 'aval';
    const m = pag ? assinMensalidade(k.plano, med, k.ha, 0) : null; o.n[e.t] = (o.n[e.t] || 0) + 1;
    if (pag) { o.vig += assinCent(m.valor); o.cobrada += assinCent(m.cobrada); o.medida += assinCent(med); }
    const ab = (org.faturas || []).filter(f => f.st === 'aberta' || f.st === 'pendente' || f.st === 'contestada');
    ab.forEach(f => { o.abertas++; o.abertasV += assinCent(f.valor); });
    o.linhas.push({ org, e, k, med, m, ab, ag: assinAgendado(org, A.hoje), ntal: org.demo ? med0.n : null }); });
  const pf = {}; med0.linhas.filter(l => l.conta).forEach(l => { const x = pf[l.faz] || (pf[l.faz] = { faz: l.faz, cent: 0, n: 0 }); x.cent += assinCent(l.decl); x.n++; });
  o.porFaz = Object.values(pf).map(x => ({ faz: x.faz, ha: x.cent / 100, n: x.n }));
  o.vig /= 100; o.cobrada /= 100; o.medida /= 100; o.abertasV /= 100; return o; }
// dia do trial pela data simulada da cobrança (PLAT-D19): ON-01 e BO-02 leem daqui
function assinTrial(org, hoje) { const t = (org && org.trial) || {}; const dia = assinDias(t.inicio, hoje) + 1;
  return { dia, dias: t.dias, fim: t.fim, acabou: dia > t.dias, t: dia > t.dias ? 'avaliação terminou em ' + assinBr(t.fim) : 'dia ' + dia + ' de ' + t.dias }; }
// fatura em CSV (gerada no navegador a partir da cópia da fatura; Baixar dados do PRD CF-05)
function assinCsv(org, f) { const C = f.copia || {}; const P = assinPlano(C.plano) || {}; const q = s => '"' + String(s == null ? '' : s).replace(/"/g, '""') + '"';
  const L = [['Organização', org.nome], ['Competência', assinComp(f.comp)], ['Estado', f.previa ? 'Em medição (prévia)' : assinFatEstado(f, (assinLer() || {}).hoje || f.venc)],
    ['Plano', P.nome + ' · contrato ' + C.versao + (C.aceite_por ? ' · aceite por ' + C.aceite_por : '')], ['Área medida (ha)', assinNf(C.medida, 2, 2)], ['Talhões medidos', C.ntal == null ? 'informada' : C.ntal]]
    .concat(C.abertura == null ? [] : [['Medida na abertura (ha)', assinNf(C.abertura, 2, 2)], [f.previa ? 'Medida hoje (ha)' : 'Medida no fechamento (ha)', assinNf(C.fech, 2, 2)]]).concat([
    ['Área contratada (ha)', assinNf(C.contratada, 2, 2)], ['Área cobrada (ha)', assinNf(C.cobrada, 2, 2)], ['Preço (R$/ha·mês)', assinNf(C.preco, 2, 2)],
    ['Mínimo (R$/mês)', assinNf(C.minimo, 2, 2)], ['Crédito (R$)', assinNf(C.credito, 2, 2)]])
    .concat(C.saldo ? [['Saldo de crédito para ' + assinComp(C.saldo_comp) + ' (R$)', assinNf(C.saldo, 2, 2)]] : [])
    .concat([['Valor (R$)', assinNf(f.valor, 2, 2)], ['Fechamento', assinBr(C.fechamento)], ['Vencimento', assinBr(f.venc)], ['Cobrança', 'simulada · nenhum valor foi cobrado']]);
  (f.eventos || []).forEach(e => L.push(['Evento ' + assinBr(e.d), e.t]));
  return L.map(r => r.map(q).join(';')).join('\r\n') + '\r\n'; }
// ---------- trava de inadimplência (R12) e faixa de cobrança (R11) ----------
function assinTrava(acao) { const A = assinLer(); if ((ASSIN_PAR.restricoes || []).indexOf(acao) < 0) return '';
  const org = A.orgs[A.demo]; const e = assinEstado(org, A.hoje); if (e.t !== 'Inadimplente') return '';
  return 'Fatura de ' + assinComp(e.fat.comp) + ' vencida há ' + e.dias + ' dias (data simulada da cobrança: ' + assinBrC(A.hoje) + '): talhão novo ou reativado fica suspenso até o pagamento. '
    + 'Pague a fatura de ' + assinComp(e.fat.comp) + ' em Configurações › Assinatura e cobrança. Nada foi apagado; editar talhões, O.S., estoque e irrigação seguem.'; }
function assinAvisoVals(self, v) { assinOuvir(self); const A = assinLer(); const org = A.orgs[A.demo]; const e = assinEstado(org, A.hoje);
  if (self) self.__assinSig = [e.t, e.dias, A.hoje, e.fat ? e.fat.comp : ''].join('|');
  const on = e.t === 'Em atraso' || e.t === 'Inadimplente'; v.assin_fx = on;
  if (!on) { v.assin_fx_t = ''; v.assin_fx_m = ''; v.assin_fx_st = ''; return; }
  const red = e.t === 'Inadimplente'; const venc = 'Fatura de ' + assinComp(e.fat.comp) + ' vencida há ' + e.dias + (e.dias === 1 ? ' dia' : ' dias');
  v.assin_fx_t = venc + ' (data simulada da cobrança: ' + assinBrC(A.hoje) + ')'
    + (red ? ' · talhão novo ou reativado está suspenso até o pagamento; nada foi apagado e o trabalho de campo segue.' : ' · nada está restrito.');
  v.assin_fx_m = venc + (red ? ' · talhão novo suspenso' : '');   // celular: só o essencial (achado 12)
  v.assin_fx_st = 'display:flex;align-items:center;flex-wrap:wrap;gap:6px 12px;padding:7px 12px;border-radius:10px;font-size:12.5px;font-weight:700;line-height:1.35;'
    + (red ? 'background:#FDE8E6;color:#B42318;border:1px solid #F4C7C2;' : 'background:#FFF3D6;color:#8A5A00;border:1px solid #F1DDA8;'); }
