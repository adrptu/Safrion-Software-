// ===== Configurações (CONF-01) · usuários e papéis, alçadas, integrações simuladas e trilha de auditoria =====
// Estado único: c.conf do cenário salvo (talhao-os-cenario-v1); ausente ou de outra versão vale o padrão (CONF0 + G2_PERFIS + G2_ALCADAS).
// Este arquivo entra UMA vez em toda tela (engine, depois do da assinatura) e só declara nomes conf*/CONF* (RV-13): não colide com cenario.js.
// Grava só por cenMudar (CF-01, CF-03 e CF-04 carregam cenario.js); CD-04 e CF-05 só leem (confAcessoDe, confComAcesso).
// Os comandos calculam R3, R5, R9 e R10 sobre o c da transação, nunca sobre o salvo. Nenhuma credencial existe no protótipo (ENG-017).
// Rótulos: decisões tomadas sem o proprietário em docs/configuracoes/DECISOES.md (CONF-D01..D24).
const CONF_ERP_TIPOS = ['recebimento-nf', 'entrega', 'devolucao', 'ajuste', 'consumo'];   // movimentos que mudam o físico (R17)
const CONF_SEM = 'sem titular: conceda em Configurações › Usuários e alçadas';
function confClone(o) { return JSON.parse(JSON.stringify(o)); }
function confBr(iso) { if (!iso) return '—'; const a = String(iso).slice(0, 10).split('-'); return a.length === 3 ? a[2] + '/' + a[1] + '/' + a[0] : String(iso); }
function confAgora() { if (typeof cenAgora === 'function') return cenAgora(); const d = new Date(); return ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2); }
function confChave(p) { return (p || 'cfg') + '-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8); }
function confP(x) { return CONF0.pessoas.find(p => p.id === x || p.k === x) || null; }
function confRot(papel, p) { return g2papRot(p ? p.k : '', papel, !!(p && p.fem)); }
function confCrea(p) { return !!(p && p.crea && p.crea >= CONF0.hoje); }   // R4: CREA válido na data operacional
// ---------- estado ----------
// padrão materializado: acesso inicial do CONF0 e papéis de G2_PERFIS (sem c.conf, o efetivo é exatamente G2_PERFIS)
function confBase() { const ps = {};
  CONF0.pessoas.forEach(x => { const d = G2_PERFIS.find(q => q.k === x.k);
    ps[x.id] = { a: x.acesso, desde: x.desde || '', ate: '', papeis: d ? G2_PAPEIS.filter(y => d.papeis[y.k]).map(y => y.k) : [] }; });
  return { v: CONF0.v, pessoas: ps, alc: {}, pend: {}, erp: {}, sinc: {}, ev: [], recibos: {}, seq: CONF0.ev.length }; }
function confValido(k) { return !!k && k.v === CONF0.v; }
function confGarante(c) { if (!confValido(c.conf)) c.conf = confBase(); return c.conf; }
function confLer(c) { if (c) return confValido(c.conf) ? c.conf : confBase(); return g2conf() || confBase(); }   // só leitura (telas)
function confAcessoDe(k) { const p = confP(k); if (!p) return null; const e = confLer().pessoas[p.id] || {}; return { a: e.a || 'sem', desde: e.desde || '', ate: e.ate || '', papeis: e.papeis || [] }; }
function confComAcesso(K) { K = K || confLer(); return Object.keys(K.pessoas).filter(id => K.pessoas[id].a === 'ativo').length; }
function confAcessoT(e) { return e.a === 'ativo' ? 'Ativo desde ' + confBr(e.desde) : (e.a === 'desativado' ? 'Desativado em ' + confBr(e.ate) : 'Sem acesso'); }
// ---------- quem decide, sobre o estado da transação ----------
function confAtor(K, ator) { const k = (typeof ator === 'string') ? ator : (ator && ator.k); return g2perfisDe(K).find(x => x.k === k) || null; }
function confPodeA(P, a) { return !!P && !!a && (a.modo === 'um' ? a.papeis.some(x => P.papeis[x]) : a.papeis.every(x => !!P.papeis[x])); }
function confAtorT(P, a) { const n = a.papeis.filter(x => P.papeis[x]).map(x => P.papeis[x]); return P.k + ' (' + (a.modo === 'um' ? n[0] : n.join(' e ')) + ')'; }
function confQuemA(K, a) { const L = g2perfisDe(K).filter(P => confPodeA(P, a)).map(P => confAtorT(P, a)); return L.join(' ou ') || (g2papT(a.papeis) + ' ' + CONF_SEM); }
function confExigeA(K, ator, a, acao) { const P = confAtor(K, ator); if (!confPodeA(P, a)) throw new Error(acao + ': decisão de ' + confQuemA(K, a) + '. Nada foi alterado.'); return confAtorT(P, a); }
function confExigeK(K, ator, id, acao, nivel) { return confExigeA(K, ator, g2alcN(g2alcDe(K, id), nivel), acao); }
function confQuemAge(K, ator, acao) { const P = confAtor(K, ator); if (!P) throw new Error(acao + ': sem o perfil de quem age. Nada foi alterado.'); return P.k + ' (' + Object.values(P.papeis)[0] + ')'; }
// alçadas sem titular ativo (R6): o nível acima da AL-05 não conta (sem titular, o que passa do limite é só recusado, R9)
function confSemTitular(K) { const P = g2perfisDe(K); const out = [];
  G2_ALCADAS.forEach(b => { const a = g2alcDe(K, b.id); if (!P.some(x => confPodeA(x, a))) out.push(b.id);
    else if (a.acima && b.id !== 'AL-05' && !P.some(x => confPodeA(x, a.acima))) out.push(b.id); });
  return out; }
function confDecide(K, k) { const P = confAtor(K, k); if (!P) return [];   // alçadas que a pessoa decide (base ou acima)
  return G2_ALCADAS.filter(b => { const a = g2alcDe(K, b.id); return confPodeA(P, a) || (b.id !== 'AL-05' && a.acima && confPodeA(P, a.acima)); }).map(b => b.id); }
// ---------- idempotência (R12): mesma chave + mesmo conteúdo = mesmo recibo; outro conteúdo = conflito ----------
function confRepete(K, chave, imp, oque) { if (!chave) throw new Error(oque + ' sem chave de quem inicia: reabra o painel. Nada foi alterado.');
  const r0 = (K.recibos || {})[chave]; if (!r0) return null;
  if (r0.imp !== imp) throw new Error('Este registro (' + chave + ') já foi gravado como ' + r0.id + ' com outro conteúdo: conflito, nada gravado.');
  return { msg: oque + ' já registrada · ' + r0.id + ' · nada mudou de novo.', recibo: r0, repetido: true }; }
function confEv(K, chave, imp, ev) { K.seq = (K.seq || CONF0.ev.length) + 1; const id = 'CFG-' + String(K.seq).padStart(4, '0');
  const e = Object.assign({ id, d: CONF0.hoje, at: confAgora(), origem: 'web' }, ev); K.ev.push(e); K.recibos[chave] = { id, imp }; return e; }
function confPapT(lista, p) { return lista.map(x => confRot(x, p)).join(' e '); }
function confSemT(ids) { return ids.length ? ' Atenção: ' + ids.join(', ') + (ids.length > 1 ? ' ficam' : ' fica') + ' sem titular; resolva em Usuários e alçadas.' : ''; }
// R3 · ninguém concede papel nem reativa acesso a si mesmo (RF-GOV-002) · R5 · o último gestor ativo não sai (organização trancada)
function confR3(ator, p, oque) { const k = (typeof ator === 'string') ? ator : (ator && ator.k);
  if (k && k === p.k) throw new Error('Ninguém ' + oque + ' a si mesmo: peça a outra pessoa com o papel de gestor (RF-GOV-002). Nada foi alterado.'); }
function confR5(K, pid, p, oque) { const outros = Object.keys(K.pessoas).filter(id => id !== pid && K.pessoas[id].a === 'ativo' && K.pessoas[id].papeis.indexOf('gestor') >= 0);
  if (!outros.length) throw new Error(p.k + ' é a última pessoa ativa com o papel de gestor e não pode ' + oque + ': sem gestor, ninguém concede papel de novo. Conceda gestor a outra pessoa antes. Nada foi alterado.'); }
// ---------- comandos do CF-01 (dentro de cenMudar) ----------
function confPapeis(c, pid, papeis, chave, ator) { const K = confGarante(c); const p = confP(pid); if (!p) throw new Error('Pessoa não encontrada no cadastro (CD-04).');
  const novo = G2_PAPEIS.map(x => x.k).filter(k => [].concat(papeis || []).indexOf(k) >= 0); const imp = JSON.stringify(['papeis', p.id, novo]);
  const r0 = confRepete(K, chave, imp, 'Mudança de papéis'); if (r0) return r0;
  const quem = confExigeK(K, ator, 'AL-13', 'Mudar os papéis de ' + p.k); const e = K.pessoas[p.id];
  if (!e || e.a !== 'ativo') throw new Error(p.k + (e && e.a === 'desativado' ? ' está com o acesso desativado: reative antes de mudar papéis.' : ' está sem acesso: convide antes de dar papel.') + ' Nada foi alterado.');
  const ganha = novo.filter(x => e.papeis.indexOf(x) < 0), perde = e.papeis.filter(x => novo.indexOf(x) < 0);
  if (!ganha.length && !perde.length) throw new Error('Nada mudou nos papéis de ' + p.k + '.');
  if (ganha.length) confR3(ator, p, 'concede papel');
  if (ganha.indexOf('agronomo') >= 0 && !confCrea(p)) throw new Error('Agrônomo só com CREA válido no cadastro em ' + confBr(CONF0.hoje) + ': ' + p.k + (p.crea ? ' tem CREA vencido em ' + confBr(p.crea) : ' não tem CREA')
    + '. Cadastre a habilitação em Cadastros › Pessoas e equipes. Nada foi alterado.');   // R4 (lei: receituário e aprovação agronômica)
  if (perde.indexOf('gestor') >= 0) confR5(K, p.id, p, 'perder o papel de gestor');
  /* revisão CONF 10/10 (extensão da CONF-D34): ninguém retira todos os próprios papéis; o Ver como passaria em silêncio a outra pessoa (R2) e o
     próximo ato sairia em nome e com o poder dela. Retirar parte dos próprios papéis segue valendo (R3) */
  const k0 = (typeof ator === 'string') ? ator : (ator && ator.k);
  if (!novo.length && k0 && k0 === p.k) throw new Error('Ninguém retira todos os próprios papéis: sem papel, o perfil de demonstração passaria a outra pessoa e o próximo ato sairia em nome dela. Peça a outra pessoa com o papel de gestor. Nada foi alterado.');
  const antes = confSemTitular(K); e.papeis = novo; const sem = confSemTitular(K).filter(x => antes.indexOf(x) < 0);
  const mud = ganha.map(x => '+ ' + confRot(x, p)).concat(perde.map(x => '− ' + confRot(x, p))).join(' · ');
  const dec = confDecide(K, p.k); const ev = confEv(K, chave, imp, { tipo: 'papel', quem, alvo: p.k, t: 'Papéis de ' + p.k + ': ' + mud,
    ef: (novo.length ? 'decide ' + (dec.length ? dec.join(', ') : 'nenhuma alçada') : 'só app de campo') + (sem.length ? ' · sem titular: ' + sem.join(', ') : '') });
  return { msg: 'Papéis de ' + p.k + ': ' + mud + ' (' + ev.id + '). Vale para o próximo comando.' + confSemT(sem), recibo: K.recibos[chave] }; }
// convite simulado, aceito na hora (CONF-D07): nenhum dado de contato, nenhuma mensagem real
function confConvidar(c, pid, chave, ator) { const K = confGarante(c); const p = confP(pid); if (!p) throw new Error('Pessoa não encontrada no cadastro (CD-04).');
  const imp = JSON.stringify(['convite', p.id]); const r0 = confRepete(K, chave, imp, 'Convite'); if (r0) return r0;
  const quem = confExigeK(K, ator, 'AL-13', 'Convidar ' + p.k); const e = K.pessoas[p.id];
  if (e.a === 'ativo') throw new Error(p.k + ' já tem acesso (' + confAcessoT(e) + ').');
  if (e.a === 'desativado') throw new Error(p.k + ' teve o acesso desativado em ' + confBr(e.ate) + ': use Reativar acesso.');
  confR3(ator, p, 'convida');
  Object.assign(e, { a: 'ativo', desde: CONF0.hoje, ate: '', papeis: [] });
  const ev = confEv(K, chave, imp, { tipo: 'convite', quem, alvo: p.k, t: 'Convite (simulado) aceito · acesso de ' + p.k + ' · só app de campo', ef: 'Sem acesso → Ativo desde ' + confBr(CONF0.hoje) });
  return { msg: p.k + ' convidado (simulado, nenhuma mensagem real enviada): acesso Ativo desde ' + confBr(CONF0.hoje) + ', só app de campo (' + ev.id + '). Dê papel no painel se ' + p.k + ' decidir algo.', recibo: K.recibos[chave] }; }
// desativar não apaga histórico: os registros antigos guardam o nome; reativar confere CREA de novo (R4) e nunca a si mesmo (R3)
function confAcesso(c, pid, ativar, chave, ator) { const K = confGarante(c); const p = confP(pid); if (!p) throw new Error('Pessoa não encontrada no cadastro (CD-04).');
  const imp = JSON.stringify(['acesso', p.id, !!ativar]); const r0 = confRepete(K, chave, imp, ativar ? 'Reativação' : 'Desativação'); if (r0) return r0;
  const quem = confExigeK(K, ator, 'AL-13', (ativar ? 'Reativar' : 'Desativar') + ' o acesso de ' + p.k); const e = K.pessoas[p.id];
  const antes = confSemTitular(K); let nota = '';
  if (ativar) { if (e.a !== 'desativado') throw new Error(p.k + (e.a === 'ativo' ? ' já está com acesso Ativo.' : ' nunca teve acesso: use Convidar.'));
    confR3(ator, p, 'reativa acesso');
    if (e.papeis.indexOf('agronomo') >= 0 && !confCrea(p)) { e.papeis = e.papeis.filter(x => x !== 'agronomo'); nota = ' Volta sem o papel de agrônomo: CREA não está válido no cadastro.'; }
    Object.assign(e, { a: 'ativo', desde: CONF0.hoje, ate: '' }); }
  else { if (e.a !== 'ativo') throw new Error(p.k + ' não está com acesso Ativo.');
    if (e.papeis.indexOf('gestor') >= 0) confR5(K, p.id, p, 'ser desativada');
    const k0 = (typeof ator === 'string') ? ator : (ator && ator.k);   /* revisão F11: o Ver como trocaria de pessoa sem aviso e o próximo ato sairia em nome de outra */
    if (k0 && k0 === p.k) throw new Error('Ninguém desativa o próprio acesso: peça a outra pessoa com o papel de gestor. Nada foi alterado.');
    Object.assign(e, { a: 'desativado', ate: CONF0.hoje });
    /* revisão F7: proposta de alçada de quem perde o acesso sai junto (ninguém mais a desistiria; a alçada ficaria presa) */
    Object.keys(K.pend).filter(id => K.pend[id].k === p.k).forEach(id => { nota += ' Proposta da ' + id + ' v' + K.pend[id].v + ' retirada: quem propôs perdeu o acesso.'; delete K.pend[id]; }); }
  const sem = confSemTitular(K).filter(x => antes.indexOf(x) < 0);
  const ev = confEv(K, chave, imp, { tipo: 'acesso', quem, alvo: p.k, t: 'Acesso de ' + p.k + (ativar ? ' reativado' : ' desativado') + (e.papeis.length ? ' · ' + confPapT(e.papeis, p) : ''),
    ef: (ativar ? 'Desativado → Ativo desde ' : 'Ativo → Desativado em ') + confBr(CONF0.hoje) + (sem.length ? ' · sem titular: ' + sem.join(', ') : '') + nota });
  return { msg: 'Acesso de ' + p.k + (ativar ? ' reativado' : ' desativado: sai dos perfis de demonstração e não decide mais; os registros antigos ficam') + ' (' + ev.id + ').' + nota + confSemT(sem), recibo: K.recibos[chave] }; }
// ---------- alçadas (R8, R9, R10): mudança com motivo vale para comandos novos; ampliar o próprio poder espera o 2º aprovador ----------
function confAlcT(a, nivel) { const n = g2alcN(a, nivel); return n ? g2papT(n.papeis) : ''; }
function confAlcNova(b, cur, mud) { mud = mud || {};
  if (b.edita === 'papel') { const x = mud.papel; if ((b.opc || []).indexOf(x) < 0) throw new Error('Escolha o papel da ' + b.id + ': ' + b.opc.map(y => g2papT(y)).join(', ') + '.');
    return cur.papeis.join() === x ? null : { papeis: [x], modo: 'todos' }; }
  if (b.edita === 'lim') { const n = Number(String(mud.lim == null ? '' : mud.lim).replace(',', '.'));
    if (!(Number.isInteger(n) && n >= b.faixa[0] && n <= b.faixa[1])) throw new Error('Informe o limite da ' + b.id + ' em % inteiro, de ' + b.faixa[0] + ' a ' + b.faixa[1] + ' %.');
    return n === cur.lim ? null : { lim: n }; }
  if (b.edita === 'acima') { const x = mud.papel; if ((b.opc || []).indexOf(x) < 0) throw new Error('Escolha quem aceita o excedente da ' + b.id + ': ' + b.opc.map(y => g2papT(y)).join(', ') + '.');
    return (cur.acima && cur.acima.papeis.join() === x) ? null : { acima: { papeis: [x], modo: 'todos' } }; }
  throw new Error(b.id + ' é fixa: ' + b.fixa + '.'); }
function confAlcMudT(b, cur, nv) { if (nv.lim !== undefined) return 'limite ' + cur.lim + ' % → ' + nv.lim + ' % da área da ordem';
  if (nv.acima) return 'excedente: ' + confAlcT(cur, 'acima') + ' → ' + g2papT(nv.acima.papeis); return confAlcT(cur) + ' → ' + g2papT(nv.papeis); }
// R10: depois da mudança, quem altera decide um comando ou uma faixa de valor que antes não decidia?
function confAmplia(b, P, cur, nv) { if (b.edita === 'acima') return !confPodeA(P, cur.acima) && confPodeA(P, nv.acima);
  if (b.edita === 'lim') return nv.lim > cur.lim && confPodeA(P, nv); return !confPodeA(P, cur) && confPodeA(P, nv); }
function confR9(K, b, nv) { const need = b.edita === 'acima' ? nv.acima.papeis : nv.papeis; if (b.edita === 'lim') return;
  if (!g2perfisDe(K).some(P => need.every(x => P.papeis[x]))) throw new Error('Ninguém ativo tem o papel ' + g2papT(need) + ': a ' + b.id + ' ficaria sem quem decida e o fluxo pararia. Conceda o papel antes, no painel da pessoa. Nada foi alterado.'); }
function confAlcAplica(K, b, cur, mud) { K.alc[b.id] = Object.assign({}, K.alc[b.id] || {}, mud, { v: cur.v + 1 }); }
// R12 (revisão F2): o conteúdo comparado vem do PEDIDO (o que a pessoa escolheu, o motivo e a versão que o painel mostrava), nunca do estado
// depois de gravar: o reenvio do mesmo pedido devolve o mesmo recibo; outro pedido com a mesma chave é conflito.
function confAlcPed(b, mud) { mud = mud || {}; return b && b.edita === 'lim' ? { lim: String(mud.lim == null ? '' : mud.lim).trim().replace(',', '.') } : { papel: mud.papel == null ? '' : String(mud.papel) }; }
function confVEsp(v) { return (v == null || v === '') ? null : Number(v); }
function confAlcMudar(c, id, mud, motivo, chave, ator, vEsp) { const K = confGarante(c); const b = G2_ALCADAS.find(a => a.id === id); if (!b) throw new Error('Alçada não encontrada: ' + id + '.');
  if (!b.edita) throw new Error(id + ' é fixa: ' + b.fixa + '.'); const ve = confVEsp(vEsp);
  const mot = String(motivo || '').trim(); const imp = JSON.stringify(['alc', id, confAlcPed(b, mud), mot, ve]); const r0 = confRepete(K, chave, imp, 'Mudança da ' + id); if (r0) return r0;
  const quem = confExigeK(K, ator, 'AL-14', 'Alterar a ' + id); const cur = g2alcDe(K, id);
  if (ve != null && cur.v !== ve) throw new Error(id + ' mudou para a v' + cur.v + ' enquanto o painel mostrava a v' + ve + ': reabra e confira. Nada foi alterado.');
  const novo = confAlcNova(b, cur, mud);
  if (!novo) throw new Error('Nada muda na ' + id + ': é o valor vigente (v' + cur.v + ').');
  /* LEVE-1 (proprietário 19/10: "leve e fluido"): o motivo é opcional; quem e quando ficam no evento. O 2º aprovador continua quando a mudança
     amplia o poder de quem propõe (R10, abaixo): é segurança, não burocracia */
  const pd = K.pend[id]; if (pd) throw new Error(id + ' já tem mudança aguardando confirmação (v' + pd.v + ' por ' + pd.por + '): confirme ou desista antes de propor outra. Nada foi alterado.');
  const nv = Object.assign({}, cur, novo); confR9(K, b, nv); const P = confAtor(K, ator); const txt = confAlcMudT(b, cur, novo);
  if (confAmplia(b, P, cur, nv)) { K.pend[id] = { v: cur.v + 1, mud: novo, por: quem, k: P.k, motivo: mot, d: CONF0.hoje, at: confAgora() };
    const ev = confEv(K, chave, imp, { tipo: 'alc-prop', quem, alvo: id, t: id + ' v' + cur.v + ' → v' + (cur.v + 1) + ' proposta: ' + txt + (mot ? ' · motivo: ' + mot : ''), ef: 'aguarda 2º aprovador (amplia o poder de quem propôs); vale a v' + cur.v });
    return { msg: id + ' v' + (cur.v + 1) + ' aguarda confirmação (' + ev.id + '): ' + txt + ' amplia o seu poder; confirma ' + confQuemConf(K, K.pend[id]) + '. Até lá vale a v' + cur.v + '.', recibo: K.recibos[chave], pendente: true }; }
  confAlcAplica(K, b, cur, novo);
  const ev = confEv(K, chave, imp, { tipo: 'alc', quem, alvo: id, t: id + ' v' + cur.v + ' → v' + (cur.v + 1) + ': ' + txt + (mot ? ' · motivo: ' + mot : ''), ef: 'vale para comandos novos; registros antigos guardam quem decidiu sob a v' + cur.v });
  return { msg: id + ' v' + (cur.v + 1) + ' vigente (' + ev.id + '): ' + txt + '. Vale para o próximo comando.', recibo: K.recibos[chave] }; }
// quem confirma ou recusa a proposta (R10): gestor ou direção, nunca quem propôs (revisão F12: o texto não manda à própria proponente)
function confQuemConf(K, pd) { const a = g2alcDe(K, 'AL-14').conf; const L = g2perfisDe(K).filter(P => confPodeA(P, a) && (!pd || P.k !== pd.k)).map(P => confAtorT(P, a));
  return L.join(' ou ') || ('outra pessoa com ' + g2papT(a.papeis).replace(' e ', ' ou ') + ' (ninguém ativo além de quem propôs: conceda o papel em Configurações › Usuários e alçadas)'); }
function confPendDe(K, id, ve, oque) { const pd = K.pend[id]; if (!pd) throw new Error('Nada aguarda confirmação na ' + id + '.');
  if (ve != null && pd.v !== ve) throw new Error(oque + ': a proposta da ' + id + ' mudou (agora v' + pd.v + '); reabra e confira. Nada foi alterado.'); return pd; }
function confExigeConf(K, ator, pd, id, acao) { const P = confAtor(K, ator);
  if (P && P.k === pd.k) throw new Error('Quem propôs não ' + (acao === 'Recusar' ? 'recusa' : 'confirma') + ' a própria mudança (R10): ' + (acao === 'Recusar' ? 'use Desistir da mudança.' : 'outra pessoa com gestor ou direção confirma.') + ' Nada foi alterado.');
  const a = g2alcDe(K, 'AL-14').conf; if (!confPodeA(P, a)) throw new Error(acao + ' a ' + id + ': decisão de ' + confQuemConf(K, pd) + '. Nada foi alterado.'); return confAtorT(P, a); }
function confAlcConfirmar(c, id, chave, ator, vEsp) { const K = confGarante(c); const b = G2_ALCADAS.find(a => a.id === id); const ve = confVEsp(vEsp);
  const imp = JSON.stringify(['alc-conf', id, ve]); const r0 = confRepete(K, chave, imp, 'Confirmação da ' + id); if (r0) return r0;
  if (!b) throw new Error('Nada aguarda confirmação na ' + id + '.'); const pd = confPendDe(K, id, ve, 'Confirmar');
  const quem = confExigeConf(K, ator, pd, id, 'Confirmar'); const cur = g2alcDe(K, id); const nv = Object.assign({}, cur, pd.mud); confR9(K, b, nv);
  confAlcAplica(K, b, cur, pd.mud); delete K.pend[id]; const txt = confAlcMudT(b, cur, pd.mud);
  const ev = confEv(K, chave, imp, { tipo: 'alc-conf', quem, alvo: id, t: id + ' v' + (cur.v + 1) + ' confirmada: ' + txt + ' · proposta por ' + pd.por + (pd.motivo ? ' · motivo: ' + pd.motivo : ''), ef: 'vale para comandos novos' });
  return { msg: id + ' v' + (cur.v + 1) + ' confirmada por ' + quem + ' (' + ev.id + '): ' + txt + '. Vale para o próximo comando.', recibo: K.recibos[chave] }; }
function confAlcDesistir(c, id, chave, ator, vEsp) { const K = confGarante(c); const ve = confVEsp(vEsp);
  const imp = JSON.stringify(['alc-des', id, ve]); const r0 = confRepete(K, chave, imp, 'Desistência da ' + id); if (r0) return r0;
  const pd = confPendDe(K, id, ve, 'Desistir'); const P = confAtor(K, ator);
  if (!P || P.k !== pd.k) throw new Error('Só quem propôs (' + pd.por + ') desiste da mudança da ' + id + (P && confPodeA(P, g2alcDe(K, 'AL-14').conf) ? ': use Recusar mudança.' : '.') + ' Nada foi alterado.');
  delete K.pend[id]; const ev = confEv(K, chave, imp, { tipo: 'alc-des', quem: pd.por, alvo: id, t: id + ' v' + pd.v + ' retirada por quem propôs', ef: 'segue a vigente' });
  return { msg: 'Mudança da ' + id + ' retirada (' + ev.id + '): segue a vigente.', recibo: K.recibos[chave] }; }
// recusar (revisão F7): quem pode confirmar também pode recusar; a proposta sai, a vigente segue e a recusa fica na trilha
function confAlcRecusar(c, id, chave, ator, vEsp) { const K = confGarante(c); const b = G2_ALCADAS.find(a => a.id === id); const ve = confVEsp(vEsp);
  const imp = JSON.stringify(['alc-rec', id, ve]); const r0 = confRepete(K, chave, imp, 'Recusa da ' + id); if (r0) return r0;
  if (!b) throw new Error('Nada aguarda confirmação na ' + id + '.'); const pd = confPendDe(K, id, ve, 'Recusar');
  const quem = confExigeConf(K, ator, pd, id, 'Recusar'); const cur = g2alcDe(K, id); const txt = confAlcMudT(b, cur, pd.mud); delete K.pend[id];
  const ev = confEv(K, chave, imp, { tipo: 'alc-rec', quem, alvo: id, t: id + ' v' + pd.v + ' recusada: ' + txt + ' · proposta por ' + pd.por + (pd.motivo ? ' · motivo da proposta: ' + pd.motivo : ''), ef: 'segue a vigente v' + cur.v });
  return { msg: 'Mudança da ' + id + ' recusada por ' + quem + ' (' + ev.id + '): segue a vigente v' + cur.v + '.', recibo: K.recibos[chave] }; }
// ---------- integrações (R16, R17): só demonstração; a fila do ERP são os movimentos do cenário, enviados uma vez por conteúdo ----------
function confErpImp(m) { return JSON.stringify([m.tipo, m.prod || '', m.lote || '', Number(m.qtd) || 0, m.det || '']); }
function confErpFila(c) { const env = (confValido(c.conf) && c.conf.erp) || {};
  return (c.movs || []).filter(m => m.sinc !== false && CONF_ERP_TIPOS.indexOf(m.tipo) >= 0).map(m => { const imp = confErpImp(m), ant = env[m.id];
    if (m.tipo === 'consumo' && !m.det) return (ant && ant !== imp) ? { m, imp, estorno: true } : null;   // estornado depois de enviado: volta uma vez
    return ant === imp ? null : { m, imp, estorno: false }; }).filter(Boolean); }
function confErpQ(m) { const n = Number(m.qtd) || 0; return (m.tipo === 'ajuste' ? (n < 0 ? '−' : '+') : '') + cenNum(Math.abs(n)); }   /* ajuste leva o sinal (revisão F8): −5 L é perda, +5 L é sobra */
function confErpT(x) { const m = x.m; const q = m.det ? m.det : ((m.prod || '') + (m.qtd ? ' ' + confErpQ(m) + ' ' + (m.un || '') : ''));
  return m.id + ' · ' + (x.estorno ? 'estorno do consumo' : ({ 'recebimento-nf': 'recebimento de NF', entrega: 'entrega', devolucao: 'devolução', ajuste: 'ajuste de inventário', consumo: 'consumo' }[m.tipo] || m.tipo))
    + (m.os ? ' · ' + m.os : '') + (q ? ' · ' + q : ''); }
function confSincronizar(c, chave, ator) { const K = confGarante(c); const imp = JSON.stringify(['sinc', chave]); const r0 = confRepete(K, chave, imp, 'Sincronização'); if (r0) return r0;
  const quem = confQuemAge(K, ator, 'Sincronizar'); const fila = confErpFila(c); const hr = confAgora();
  fila.forEach(x => { K.erp[x.m.id] = x.imp; }); const est = fila.filter(x => x.estorno).length;
  const t = CONF0.hoje + ' ' + hr, mx = (id) => { const a = (K.sinc || {})[id] || ((CONF0.conexoes.find(x => x.id === id) || {}).ult) || ''; return a > t ? a : t; };   /* revisão F15: a hora do relógio com a data operacional pode ser anterior à do seed; a última nunca volta */
  K.sinc = Object.assign({}, K.sinc, { erp: mx('erp'), est: mx('est'), tel: mx('tel'), lab: mx('lab') });
  const ev = confEv(K, chave, imp, { tipo: 'sinc', quem, alvo: 'ERP · Sankhya', t: 'Sincronização simulada · ERP: ' + fila.length + (fila.length === 1 ? ' movimento enviado' : ' movimentos enviados') + (est ? ' (' + est + (est > 1 ? ' estornos' : ' estorno') + ')' : ''),
    ef: (fila.length ? fila.map(confErpT).join('; ') : 'nada novo na fila') + ' · estação, telemetria e laboratório em dia (simulado)' });
  return { msg: 'Sincronização simulada (' + ev.id + '): ' + (fila.length ? fila.length + (fila.length === 1 ? ' movimento enviado' : ' movimentos enviados') + ' ao ERP' + (est ? ', ' + est + (est > 1 ? ' estornos' : ' estorno') : '') : 'nada novo na fila do ERP; nada foi reenviado') + '. Nenhuma conexão real.', recibo: K.recibos[chave], n: fila.length }; }
function confConexoes(c) { const K = confLer(c); const fila = confErpFila(c); const dup = Object.values(c.ordens || {}).reduce((s, o) => s + (o.ap || []).filter(a => a.st === CEN_AP_DUP).length, 0);
  const nap = ((c.app && c.app.fila) || []).length; const on = !c.app || c.app.online !== false;
  return CONF0.conexoes.map(x => { const ult = (K.sinc || {})[x.id] || x.ult; const r = Object.assign({}, x, { ult, pend: 0, pendT: '', estado: 'Em dia (simulado)', cor: 'green' });
    if (x.id === 'erp') { r.pend = fila.length; r.pendT = fila.length ? fila.map(confErpT).join('; ') : ''; if (fila.length) { r.estado = fila.length + (fila.length === 1 ? ' na fila (simulado)' : ' na fila (simulado)'); r.cor = 'yellow'; } }
    if (x.id === 'app') { r.ult = ''; r.pend = dup; r.pendT = dup ? dup + (dup > 1 ? ' duplicidades' : ' duplicidade') + ' de apontamento: decide a conferência na O.S. (CMD-09)' : '';
      r.estado = on ? 'Com sinal (simulado)' + (nap ? ' · ' + nap + ' no aparelho' : '') : 'Sem sinal · ' + nap + ' no aparelho'; r.cor = on && !dup ? 'green' : 'yellow'; }
    return r; }); }
// realce da linha gravada nas grades do CF-01, CF-03 e CF-04 (revisão F13, pedido do proprietário 09/10/2026: retorno visual ao gravar): o mesmo
// fl da grade que o g2save usa (classe g2flash), num só setState com o aviso (dois g2set seguidos perderiam o 1º). pares = [[grade, id da linha]]
function confFl(self, pares) { const all = Object.assign({}, (self && self.state && self.state.g2) || {}); (pares || []).forEach(([g, id]) => { all[g] = Object.assign({}, all[g] || {}, { fl: id }); }); return { g2: all }; }
// ---------- exportação da trilha (R15): o arquivo vem das linhas filtradas; a exportação vira registro ----------
function confExportar(c, n, filtros, chave, ator) { const K = confGarante(c); const imp = JSON.stringify(['export', n, filtros || '']); const r0 = confRepete(K, chave, imp, 'Exportação'); if (r0) return r0;
  const quem = confQuemAge(K, ator, 'Baixar a trilha');
  const ev = confEv(K, chave, imp, { tipo: 'export', quem, alvo: 'Trilha de auditoria', t: 'Exportação · ' + n + (n === 1 ? ' registro' : ' registros') + ' · ' + (filtros || 'sem filtros'), ef: 'CSV gerado no navegador' });
  return { msg: 'Trilha baixada em CSV: ' + n + (n === 1 ? ' registro' : ' registros') + ' (' + ev.id + ', a exportação também fica na trilha).', recibo: K.recibos[chave] }; }
/* duplo clique real (revisão CONF 13/10): a tela troca a chave depois de gravar e redesenha entre os dois cliques. O 2º clique de um duplo clique
   (e.detail > 1, contado pelo navegador) ou um 2º clique antes de a tela redesenhar (mesmo desenho r) repete o MESMO pedido (mesma chave e conteúdo)
   e recebe o mesmo recibo; um clique depois do redesenho é outro pedido. Sem janela de tempo: um clique deliberado logo depois não se perde. */
function confRepJanela(u, e, r) { return !!u && ((!!e && e.detail > 1) || u.r === r); }
function confCsv(rows) { const q = s => '"' + assinCelCsv(s).replace(/"/g, '""') + '"';   /* revisão F5: injeção de fórmula */
  const L = [['Quando', 'Quem', 'O quê', 'Objeto', 'Antes → depois / efeito', 'Origem', 'Registro de origem', 'Data']]
    .concat(rows.map(r => [confBr(r.d) + (r.at ? ' ' + r.at : ''), r.quem || 'autor não registrado', r.oq, r.obj, r.ef, r.origem, r.src, r.ds]));
  return L.map(r => r.map(q).join(';')).join('\r\n') + '\r\n'; }
// ---------- ordem de gravação (R14, revisão F1): o registro guarda só HH:MM; cenMudar carimba sq = c.rev do comando em cada registro novo ----------
// (ato, decisão e movimento sem sq). A trilha ordena por data, sq e hora: dentro do mesmo minuto vale a ordem em que o servidor gravou.
function confCarimbar(c, n) { const sq = (x, k) => { if (x && typeof x === 'object' && x[k || 'sq'] == null) x[k || 'sq'] = n; };
  Object.values(c.ordens || {}).forEach(o => { const x = o.osc || {}; (x.aj || []).forEach(a => sq(a)); (x.ev || []).forEach(e => sq(e)); (x.disps || []).forEach(d => sq(d)); (x.fim || []).forEach(f => sq(f));
    if (x.canPor) sq(x, 'canSq'); (o.ap || []).forEach(a => { if (a.dec) sq(a.dec); }); if (o.ben && o.ben.hist) o.ben.hist.forEach(e => sq(e)); });
  (c.confs || []).forEach(k => { if (k.por) sq(k, 'sqd'); });
  (c.ajustes || []).forEach(a => { if (a.por && (a.estado === 'Aprovado' || a.estado === 'Recusado')) sq(a, 'sqd'); });
  (c.movs || []).forEach(m => sq(m)); if (c.conf && c.conf.ev) c.conf.ev.forEach(e => sq(e));
  const PP = c.producao; if (PP) { (PP.movs || []).forEach(m => sq(m)); Object.values(PP.previsoes || {}).forEach(vs => (vs || []).forEach(v => sq(v)));
    Object.values(PP.cargas || {}).forEach(g => { if (g.descarte) sq(g.descarte); }); }
  const A = c.assin; if (A && A.orgs) Object.values(A.orgs).forEach(org => { (org.contratos || []).forEach(k => { if (k.aceite) sq(k); });
    (org.desfeitos || []).forEach(k => { if (k.aceite) sq(k); if (k.desfeito) sq(k, 'sqd'); });
    (org.faturas || []).forEach(f => { if (f.st === 'paga' && f.paga) sq(f, 'sqPaga'); if (f.contest) { sq(f.contest); if (f.contest.resolvida) sq(f.contest, 'sqRes'); } });
    if (org.proposta) sq(org.proposta); }); }
// ---------- produção na trilha (integração CONF × COLH, CONF-D40): atos com autor dos comandos da colheita, lidos do c.producao. O que veio do seed
// (CEN0.producao) é histórico anterior ao cenário (§9) e fica no domínio; contagem de frutos e carga a pesar são fato de campo (como o apontamento)
// e entram pelo que decidem: a previsão publicada e a pesagem. Data e hora do próprio registro. ----------
const CONF_PMV = { recebimento: 'Pesar e receber carga', estorno: 'Estornar carga', 'liberação': 'Liberar lote de produto', reserva: 'Reservar lote para pedido',
  'cancelamento de reserva': 'Cancelar reserva de produto', 'expedição': 'Expedir lote',
  /* decisões da Qualidade sobre o lote de produção (beneficiamento, BEN-1 R-E02/R-E03; CONF-D43). A destinação do Fechar (sem lote) é efeito do CMD-23 */
  resultado: 'Registrar resultado da inspeção', 'reclassificação': 'Reclassificar lote de produto', bloqueio: 'Bloquear lote de produto', 'destinação': 'Destinar lote de produto' };
const CONF_PMV_OBS = { resultado: 1, 'reclassificação': 1, bloqueio: 1 };   /* sem massa: o efeito é a observação do registro */
function confTrilhaProd(c, add) { const PP = c.producao; if (!PP) return; const S0 = (typeof CEN0 !== 'undefined' && CEN0.producao) || {};
  const mv0 = {}, pv0 = {}; (S0.movs || []).forEach(m => { mv0[m.id] = 1; }); Object.keys(S0.previsoes || {}).forEach(k => (S0.previsoes[k] || []).forEach(v => { pv0[k + ':' + v.v] = 1; }));
  const K = (typeof PRDC !== 'undefined' && PRDC.cult) || {}; const qt = (lid, kg) => { const L = (PP.lotes || {})[lid]; return L && typeof prEstTxt === 'function' ? prEstTxt(L.cultura, Math.abs(kg)) : cenNum(Math.abs(kg)) + ' kg'; };
  Object.keys(PP.previsoes || {}).sort().forEach(cid => (PP.previsoes[cid] || []).forEach(v => { if (pv0[cid + ':' + v.v]) return; const k = K[cid] || {};
    const txt = v.safra !== undefined ? 'safra ' + (typeof prUnTxt === 'function' ? prUnTxt(k.cultura, v.safra, 0) : v.safra) : Object.keys(v.sem || {}).map(w => (typeof prSemTxt === 'function' ? prSemTxt(w) : w) + ' ' + (typeof prUnTxt === 'function' ? prUnTxt(k.cultura, v.sem[w]) : v.sem[w])).join(' · ');
    add({ id: 'PRV:' + cid + ':' + v.v, d: v.d, at: v.at, sq: v.sq, quem: v.por, cmd: 'Colheita', oq: 'Publicar previsão de colheita · AL-17', obj: (k.local || cid) + ' · previsão v' + v.v, h: 'COLH.dc.html',
      ef: txt + (v.cnt ? ' · base ' + v.cnt : ''), src: 'previsão v' + v.v + ' · ' + cid, ds: CONF_DS.reg }); }));
  (PP.movs || []).forEach(m => { if (mv0[m.id] || !CONF_PMV[m.tipo] || (m.tipo === 'destinação' && !m.lote)) return; const neg = m.tipo === 'estorno' || m.tipo === 'cancelamento de reserva' || m.tipo === 'destinação';
    const ben = !!(m.ordem || CONF_PMV_OBS[m.tipo] || m.tipo === 'destinação' || /CMD-24/.test(m.obs || ''));
    add({ id: m.id, d: m.d, at: m.at, sq: m.sq, quem: m.quem, cmd: ben ? 'Beneficiamento' : 'Colheita', oq: CONF_PMV[m.tipo], obj: [m.id, m.carga, m.lote, m.reserva, m.pedido].filter(Boolean).join(' · '),
      h: (m.tipo === 'recebimento' || m.tipo === 'estorno') ? 'CARGA.dc.html' : 'PROD.dc.html',
      ef: m.tipo === 'liberação' ? 'Em inspeção → Liberado' + (m.obs ? ' · ' + m.obs : '') : CONF_PMV_OBS[m.tipo] ? String(m.obs || '')
        : ((neg ? '−' : '') + qt(m.lote, m.kg) + (m.pedido && m.tipo !== 'cancelamento de reserva' ? ' para ' + m.pedido : '') + (m.obs ? ' · ' + m.obs : '')), src: m.id, ds: CONF_DS.reg }); });
  /* ordens de beneficiamento (BEN-1): o histórico da ordem já é uma linha por ato com autor (benHist); o do seed é anterior ao cenário (CONF-D43) */
  const O0 = (typeof CEN0 !== 'undefined' && CEN0.ordens) || {};
  Object.keys(c.ordens || {}).sort().forEach(id => { const o = c.ordens[id]; if (!o || o.fam !== 'BEN' || !o.ben || !Array.isArray(o.ben.hist)) return;
    const n0 = (((O0[id] || {}).ben || {}).hist || []).length;
    o.ben.hist.slice(n0).forEach((e, i) => { const cm = (String(e.ev || '').match(/\((CMD-\d+)\)/) || [])[1];
      add({ id: 'BEN:' + id + ':' + (n0 + i), d: e.d, at: e.at, sq: e.sq, quem: e.quem, cmd: cm || 'Beneficiamento', oq: String(e.ev || ''), obj: id + ' · ' + String(o.tipo || '').replace(/^Beneficiamento · /, ''),
        h: CONF_BEN_H ? CONF_BEN_H + id : 'CARGA.dc.html', ef:   /* sem o BEN publicado, a ordem aparece em texto em Cargas */ String(e.det || '') + (e.mov ? ' · ' + e.mov : ''), src: id + ' · histórico da ordem', ds: CONF_DS.reg }); }); });
  Object.values(PP.cargas || {}).forEach(g => { if (!g.descarte) return;
    add({ id: 'DCG:' + g.id, d: g.descarte.d, at: g.descarte.at, sq: g.descarte.sq, quem: g.descarte.quem, cmd: 'Colheita', oq: 'Descartar carga a pesar', obj: g.id + (g.os ? ' · ' + g.os : ''), h: 'CARGA.dc.html',
      origem: g.descarte.via || 'web', ef: 'sai da fila de pesagem; nada entra na produção · ' + g.descarte.motivo, src: g.id, ds: CONF_DS.reg }); }); }
// ---------- trilha (R14): uma linha por ato, lida dos registros que os comandos gravam; nada é digitado e nenhum autor é inferido ----------
const CONF_DS = { op: 'data operacional da demonstração (o registro guarda só a hora)', reg: 'data do registro', cob: 'data simulada da cobrança' };
function confK(quem) { return String(quem || '').split(/[\s(·]/)[0] || ''; }
/* uid (revisão CONF 10/10): identidade estável da linha = o id do registro de origem, único na trilha (repetição ganha sufixo). A posição de inserção
   (seq) muda quando outra aba grava um ato de uma fonte lida antes; o detalhe aberto e o realce do CF-04 guardam o uid. */
function confTrilha(c, A) { const L = []; let n = 0; const op = CONF0.hoje; const vis = {};
  const add = (r) => { n++; const b = String(r.id || 'linha'); const u = vis[b] ? b + '~' + (++vis[b]) : (vis[b] = 1, b);
    L.push(Object.assign({ seq: n, sq: 0, at: '', origem: 'web', ds: CONF_DS.op, h: '', ef: '' }, r, { uid: u, sq: Number(r.sq) || 0, k: confK(r.quem) })); };
  Object.keys(c.ordens || {}).sort().forEach(id => { const o = c.ordens[id]; const x = o.osc || {}; const h = 'OS.dc.html#' + id;
    (x.aj || []).forEach(a => add({ id: 'AJV:' + id + ':' + a.v, d: op, at: a.at, sq: a.sq, quem: a.por, cmd: 'Nova versão', oq: 'Ajustar a O.S. (nova versão)', obj: id + ' ' + a.v, h, ef: a.t, src: id + ' · histórico de versões' }));
    (x.ev || []).forEach(e => add({ id: e.cmd + ':' + id + ':' + e.v, d: op, at: e.at, sq: e.sq, quem: e.por, cmd: e.cmd, oq: e.cmd === 'CMD-42' ? 'Aprovar a versão · CMD-42' : 'Liberar O.S. · CMD-06', obj: id + ' ' + e.v, h,
      ef: e.cmd === 'CMD-06' ? 'A liberar → Liberadas' + (/reservada/.test(e.t) ? ' · requisição reservada no Estoque' : '') + (/só com água/.test(e.t) ? ' · irrigação só com água, sem aprovação agronômica (DEC-2609-10)' : '') : 'versão aprovada · ' + String(e.t).replace(/^.*? · /, '').replace(/ \(CMD-42\)$/, ''), src: e.cmd + ' · ' + id }));
    if (x.canPor) add({ id: 'CMD-46:' + id, d: op, at: x.canEm, sq: x.canSq, quem: x.canPor, cmd: 'CMD-46', oq: 'Cancelar sem execução · CMD-46', obj: id, h, ef: '→ Canceladas · ' + String(x.cond || '').replace(/^Cancelada sem execução por .*? às \d\d:\d\d: /, ''), src: 'CMD-46 · ' + id });
    /* enviar para conferência (CMD-08) e encerrar (CMD-10), com quem agiu (revisão CONF 10/10); o encerramento do seed fica na O.S. (§9) */
    (x.fim || []).forEach((f, i) => add({ id: f.cmd + ':' + id + ':' + (i + 1), d: op, at: f.at, sq: f.sq, quem: f.por, cmd: f.cmd, oq: f.cmd === 'CMD-10' ? 'Encerrar O.S. · CMD-10' : 'Enviar para conferência · CMD-08',
      obj: id, h, ef: f.cmd === 'CMD-10' ? 'Em conferência → Encerradas' : 'Em execução → Em conferência', src: f.cmd + ' · ' + id }));
    (x.disps || []).forEach((d, i) => add({ id: 'CMD-47:' + id + ':' + (i + 1), d: op, at: d.at, sq: d.sq, quem: d.por, cmd: 'CMD-47', oq: 'Dispensar saldo · CMD-47', obj: id, h, ef: cenNum(d.ha) + ' ha dispensados (total ' + cenNum(d.tot) + ' ha) · ' + d.mot, src: 'CMD-47 · ' + id }));
    (o.ap || []).forEach(a => { if (!a.dec || a.dec.modo === 'estornado') return;
      add({ id: 'CMD-09:' + id + ':' + a.dia, d: op, at: a.dec.at, sq: a.dec.sq, quem: a.dec.quem, cmd: 'CMD-09', oq: 'Decidir duplicidade · CMD-09', obj: id + ' dia ' + a.dia, h,
        ef: ({ anterior: 'mesmo turno: vale o dia ' + (a.dupDe || []).join(', ') + '; este guardado', este: 'mesmo turno: vale este dia; o anterior foi estornado', somar: 'outro turno: somado (' + cenNum(a.ha) + ' ha)' }[a.dec.modo] || a.dec.modo) + (a.dec.rev ? ' · ' + a.dec.rev : ''), src: 'CMD-09 · ' + id }); }); });
  (c.confs || []).forEach(k => { if (!k.por || k.via) return;
    add({ id: 'CMD-50:' + k.id, d: op, at: k.em || '', sq: k.sqd, quem: k.por, cmd: 'CMD-50', oq: (k.estado === 'Aceito' ? 'Aceitar consumo' : 'Recusar relato') + ' · CMD-50', obj: k.id + ' · ' + k.os, h: 'EST.dc.html',
      ef: k.prod + ' ' + cenNum(k.relatado) + ' ' + k.un + ' · ' + (k.decisao || k.estado), src: 'CMD-50 · ' + k.id }); });
  (c.ajustes || []).forEach(a => { if (!a.por || (a.estado !== 'Aprovado' && a.estado !== 'Recusado')) return;
    add({ id: 'AJ:' + a.id, d: op, at: a.em || '', sq: a.sqd, quem: a.por, cmd: 'Ajuste', oq: a.estado === 'Aprovado' ? 'Aprovar ajuste de inventário' : 'Recusar ajuste (recontar)', obj: (a.inv ? a.inv + ' · ' : '') + a.id, h: 'EST.dc.html',
      /* revisão CONF 10/10: quem contou é o contador (a.contador); quem registrou (a.reg, o perfil) só quando foi outra pessoa; a causa vai junto */
      ef: 'lote ' + a.lote + ': ' + cenNum(a.sistema) + ' → ' + cenNum(a.contado) + ' ' + a.un + (a.estado === 'Aprovado' ? '' : ' · saldo não muda') + (a.contador ? ' · contou: ' + a.contador : '')
        + (a.reg && !g2mesma(a.reg, a.contador) ? ' · registrou: ' + a.reg : '') + (a.causa ? ' · causa: ' + a.causa : '') + (a.rev ? ' · ' + a.rev : ''), src: a.id }); });
  const MV = { 'recebimento-nf': 'Receber nota fiscal', entrega: 'Entregar insumo', recebimento: 'Confirmar recebimento no app', devolucao: 'Receber devolução', inspecao: 'Liberar quarentena com laudo · CMD-24' };
  (c.movs || []).forEach(m => { if (!MV[m.tipo] || (m.tipo === 'entrega' && m.conf)) return; const q = String(m.quem || ''); const qi = q.split(' → ');
    const itens = m.tipo === 'recebimento' ? (m.itens || []).map(i => i.prod + ' ' + cenNum(i.qtd) + ' ' + (i.un || '')).join(', ') : (m.prod || '') + (m.qtd ? ' ' + cenNum(m.qtd) + ' ' + (m.un || '') : '');
    add({ id: m.id, d: op, at: m.at, sq: m.sq, quem: qi[0], cmd: m.tipo === 'inspecao' ? 'CMD-24' : 'Estoque', oq: MV[m.tipo], obj: m.id + (m.req ? ' · ' + m.req : '') + (m.doc ? ' · ' + m.doc : ''), h: m.tipo === 'recebimento' ? 'MB-05.dc.html' : 'EST.dc.html',
      origem: m.origem || 'web', ef: itens + (qi[1] ? ' · para ' + qi[1] : '') + (m.tipo === 'devolucao' || m.tipo === 'recebimento-nf' ? (m.apto ? ' · ao disponível' : ' · bloqueado para inspeção') : ''), src: m.id }); });
  confTrilhaProd(c, add);
  /* CONTROLE-02 F2 (CF04, contrato do PR #58): cada recibo completo da referência técnica publicada vira uma linha, pelo adaptador do Codex
     (PlanoReferencia.trilha: id PLANO:…, sq real, autor e data do registro); recibo incompleto o adaptador recusa e não derruba as outras linhas */
  if (typeof CONF_PLANO_REF !== 'undefined') (c.planoReferencias || []).forEach(x => { let ls = []; try { ls = CONF_PLANO_REF.trilha((x && x.versoes) || []); } catch (e) { ls = []; } ls.forEach(r => add(r)); });
  if (A && A.orgs && A.orgs[A.demo]) { const org = A.orgs[A.demo]; const cob = (r) => add(Object.assign({ ds: CONF_DS.cob, h: 'CF-05.dc.html', cmd: 'Assinatura' }, r));
    (org.contratos || []).concat((org.desfeitos || []).map(k => Object.assign({ des: true }, k))).filter(k => k.aceite).forEach(k => {
      cob({ id: 'ACE:' + k.v + (k.des ? 'd' : ''), d: k.aceite, sq: k.sq, quem: k.por || '', oq: 'Aceitar contrato da assinatura', obj: 'Contrato v' + k.v, ef: ((assinPlano(k.plano) || {}).nome || k.plano) + ' · ' + assinHa(k.ha) + ' a partir de ' + confBr(k.desde) + (k.recibo ? ' · ' + k.recibo : ''), src: k.recibo || 'contrato v' + k.v });
      if (k.des) cob({ id: 'DES:' + k.v, d: k.desfeito, sq: k.sqd, quem: k.desfeito_por || '', oq: 'Desfazer mudança de plano', obj: 'Contrato v' + k.v, ef: 'mudança agendada desfeita', src: k.desfeito_recibo || '' }); });
    (org.faturas || []).forEach(f => { if (f.st === 'paga' && f.paga && (f.paga_por || f.evt)) cob({ id: 'PAG:' + f.id, d: f.paga, sq: f.sqPaga, quem: f.paga_por || 'Provedor (simulado)', oq: 'Pagar fatura (simulado)', obj: 'Fatura ' + assinComp(f.comp),
        origem: f.paga_por ? 'web' : 'provedor simulado', ef: assinR(f.valor) + ' · ' + (f.forma || '') + (f.recibo ? ' · ' + f.recibo : '') + (f.evt ? ' · ' + f.evt : ''), src: f.recibo || f.evt });
      if (f.contest) cob({ id: 'CTS:' + f.id, d: f.contest.d, sq: f.contest.sq, quem: f.contest.por || '', oq: 'Contestar fatura', obj: 'Fatura ' + assinComp(f.comp), ef: f.contest.motivo, src: f.contest.recibo });
      if (f.contest && f.contest.resolvida) cob({ id: 'RES:' + f.id, d: f.contest.resolvida, sq: f.contest.sqRes, quem: f.contest.res_por || '', oq: 'Resolver contestação', obj: 'Fatura ' + assinComp(f.comp), origem: 'plataforma', ef: f.contest.decisao === 'creditar' ? 'crédito de ' + assinR(f.contest.credito) : 'valor mantido', src: f.contest.res }); });
    if (org.proposta) cob({ id: 'PRO', d: org.proposta.d, sq: org.proposta.sq, quem: org.proposta.por || '', oq: 'Pedir proposta empresarial', obj: 'Assinatura', ef: assinHa(org.proposta.ha) + ' medidos', src: org.proposta.recibo }); }
  const TIPO = { acesso: 'Conceder ou desativar acesso', convite: 'Convidar pessoa (simulado)', papel: 'Conceder ou retirar papel', alc: 'Alterar alçada', 'alc-prop': 'Propor mudança de alçada', 'alc-conf': 'Confirmar mudança de alçada',
    'alc-des': 'Desistir de mudança de alçada', 'alc-rec': 'Recusar mudança de alçada', sinc: 'Sincronizar integrações (simulado)', export: 'Baixar trilha (CSV)' };
  const K = confLer(c); CONF0.ev.map(e => Object.assign({ semente: true }, e)).concat(K.ev || []).forEach(e => add({ id: e.id, d: e.d, at: e.at, sq: e.sq, quem: e.quem, cmd: 'Configurações', oq: TIPO[e.tipo] || e.tipo, obj: e.alvo,
    h: /^AL-/.test(e.alvo) ? 'CF-01.dc.html#alc=' + e.alvo : (e.tipo === 'sinc' ? 'CF-03.dc.html' : (e.tipo === 'export' ? 'CF-04.dc.html' : 'CF-01.dc.html#pessoa=' + encodeURIComponent(e.alvo))),
    origem: e.origem || 'web', ef: e.t + (e.ef ? ' · ' + e.ef : ''), src: e.id, ds: e.semente ? CONF_DS.reg : CONF_DS.op }));
  /* registro de origem único (revisão CONF 13/10): dois atos da mesma fonte (duas dispensas, CMD-42 de v1 e v2, histórico da mesma ordem) ganham
     o nº na ordem da própria fonte, que não muda quando outra fonte grava. Dano evitado: o auditor não consegue citar um ato específico. */
  const nsrc = {}, isrc = {}; L.forEach(r => { if (r.src) nsrc[r.src] = (nsrc[r.src] || 0) + 1; });
  L.forEach(r => { if (r.src && nsrc[r.src] > 1) { isrc[r.src] = (isrc[r.src] || 0) + 1; r.src = r.src + ' · nº ' + isrc[r.src]; } });
  const cmp = (x, y) => (x < y ? -1 : (x > y ? 1 : 0));   /* data · ordem de gravação (sq; seed = 0) · hora · ordem da fonte */
  return L.sort((a, b) => cmp(a.d, b.d) || (a.sq - b.sq) || cmp(a.at || '', b.at || '') || (a.seq - b.seq)); }
