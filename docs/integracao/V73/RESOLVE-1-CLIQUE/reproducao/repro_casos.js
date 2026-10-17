// RESOLVE-1-CLIQUE · casos de reprodução (Claude, 16/10/2026). Motor real do protótipo em Node (ver repro.py).
// Cada caso imprime o observado e uma linha "CONFIRMA"/"NÃO REPRODUZ" para a afirmação do anexo que ele testa.
// Casos "sintético derivado" mudam só o que está escrito no próprio caso, numa cópia do cenário.
const OUT = [];
const log = (...a) => { const t = a.join(' '); OUT.push(t); console.log(t); };
const veredito = (id, cond, txt) => log('  ' + (cond ? 'CONFIRMA' : 'NÃO REPRODUZ') + ' [' + id + '] ' + txt);
const caso = (n, fn) => { log('\n## ' + n); try { fn(); } catch (e) { log('  EXCEÇÃO ' + String(e && e.stack || e).slice(0, 500)); } };
const fzL = l => R1C_LOCFAZ[l.local] || 'Santa Rita';
const linha = (c, id) => osProjecao(c).find(x => x.id === id);
const OT = g2pf('Otávio'), ANA = g2pf('Ana'), RUI = g2pf('Rui');
const n = x => cenNum(x);
log('# RESOLVE-1-CLIQUE · reprodução no motor · ' + R1C_ROTULO + ' · CEN0.v=' + CEN0.v + ' · hoje do cenário=' + (R1C_OSB.hoje || ''));

caso('R0 · retrato: O.S. agrícolas em A liberar com insumo (medida "antes": % liberável sem falta)', () => {
  cenReset(); const c = cenGet(); let tot = 0, ok = 0, okOutra = 0;
  osProjecao(c).filter(o => /^OS-/.test(o.id) && o.etapa === 'A liberar' && (c.ordens[o.id].ins || []).length && !o.agua).forEach(o => {
    tot++; const e = osLibErro(o, c); const faz = (R1C_OSB.ords.find(x => x.id === o.id) || {}).faz;
    const fora = e ? [] : c.ordens[o.id].ins.filter(i => { const l = cenLote(c, i.p); return l && fzL(l) !== faz; }).map(i => i.p);
    if (!e && !fora.length) ok++; if (!e && fora.length) okOutra++;
    log('  ' + o.id + ' (' + faz + ') · ' + (e ? 'bloqueada: ' + e : 'liberável' + (fora.length ? ' só com lote de outra fazenda: ' + fora.join(', ') : '')));
  });
  log('  liberáveis sem falta e na própria fazenda: ' + ok + ' de ' + tot + ' · liberáveis só com estoque de outra fazenda: ' + okOutra);
  ['NPK 20-05-20|N26-03', 'Semente de soja 58 W|S58-0801'].forEach(k => { const l = c.lotes[k]; log('  lote ' + l.lote + ' no cenário vivo: físico ' + n(l.fisico) + ' · reservado ' + n(l.reservado) + ' (anexo A-02/A-03: telas estáticas mostram outro valor)'); });
});

caso('R1 · OS-0418 · Ureia 45% sem lote', () => {
  cenReset(); const c = cenGet(); const o = linha(c, 'OS-0418');
  const lotes = Object.values(c.lotes).filter(l => l.prod === 'Ureia 45%');
  log('  lotes de Ureia 45% no cenário: ' + lotes.length + ' · necessidade ' + n(c.ordens['OS-0418'].ins[0].tot) + ' kg · etapa ' + o.etapa);
  log('  osLibErro: "' + osLibErro(o, c) + '"');
  log('  linha da lista: selos=' + JSON.stringify((o.selos || []).map(s => s.t)) + ' · dono=' + o.dono + ' · prazo=' + o.prazo);
  log('  papel "Suprimentos" no catálogo G2_PAPEIS: ' + G2_PAPEIS.some(p => /suprimento|compra/i.test(p.k + p.t)) + ' · papéis: ' + G2_PAPEIS.map(p => p.k).join(','));
  veredito('A-08', lotes.length === 0 && /^Sem lote de Ureia 45%/.test(osLibErro(o, c)), 'OS-0418 recusa por falta de lote de Ureia');
  veredito('A-05', o.dono === 'Suprimentos' && /receber o insumo no Estoque/.test(o.prazo) && !G2_PAPEIS.some(p => /suprimento|compra/i.test(p.k + p.t)), 'dono "Suprimentos" que não é papel do catálogo');
});

caso('R2 · OS-0502 · calcário 96.940 kg × 60.000 kg', () => {
  cenReset(); const c = cenGet(); const o = linha(c, 'OS-0502'); const e = osLibErro(o, c);
  log('  necessidade ' + n(c.ordens['OS-0502'].ins[0].tot) + ' kg · osLibErro: "' + e + '"');
  log('  linha: dono=' + o.dono + ' · prazo=' + o.prazo + ' · janela ' + JSON.stringify(o.janela || ''));
  log('  situação do insumo na linha (texto semeado em dados_lagoa_safra.INS): "' + ((o.ins && o.ins[0] && o.ins[0].sit) || '') + '"');
  const osd = cenOsDem(c, R1C_OSB);
  const est = cenEstDem(c, 'Lagoa Grande', Object.assign({}, R1C_ESTB, { ofaz: cenOsFaz(c, R1C_OSB) }), osd);
  const rc = est.recebDt.filter(r => /Calcário/.test(r.item));
  log('  recebimentos previstos da demanda (cenEstDem, Lagoa Grande): ' + JSON.stringify(rc.map(r => [r.item, r.q, r.dt, r.ref, r.t])));
  const falta = c.ordens['OS-0502'].ins[0].tot - 60000;
  log('  falta numérica = ' + n(falta) + ' kg; pedido previsto ' + (rc[0] ? n(rc[0].q) + ' kg em ' + rc[0].dt : 'nenhum') + ' (depois da janela 25–27/09)');
  veredito('A-09a', /Saldo insuficiente de Calcário dolomítico filler: 60\.000 kg disponíveis para 96\.940 kg/.test(e), 'liberação recusa 60.000 para 96.940');
  veredito('A-09b', rc.length === 1 && !rc[0].ref, 'o "pedido de 50.000 kg em 30/09" EXISTE na demanda (recebimento previsto sem PC), mas a liberação não o lê: o anexo diz "não está no cenário" (confirma em parte)');
});

caso('R3 · OS-0501 (Lagoa Grande) reserva glifosato da Santa Rita sem aviso', () => {
  cenReset(); const c = cenGet(); const o = linha(c, 'OS-0501'); const e = osLibErro(o, c);
  log('  fazenda da ordem: ' + (R1C_OSB.ords.find(x => x.id === 'OS-0501') || {}).faz + ' · osLibErro: "' + e + '"');
  const k = cenClone(c); const r = osc_libEfeito(k, 'OS-0501', false, o.janela);
  const req = k.reqs[k.ordens['OS-0501'].req];
  log('  liberação (cópia): "' + r.msg + '"');
  req.itens.forEach(it => { const l = k.lotes[it.prod + '|' + it.lote]; log('   - ' + it.prod + ' ' + n(it.solicitado) + ' ' + it.un + ' no lote ' + it.lote + ' · ' + l.local + ' · fazenda ' + fzL(l)); });
  const cruz = req.itens.filter(it => fzL(k.lotes[it.prod + '|' + it.lote]) !== 'Lagoa Grande');
  const avisa = /fazenda|transfer|Santa Rita/i.test(r.msg);
  const dem = cenOsDem(c, R1C_OSB).find(x => x.id === 'OS-0501');
  log('  demanda única (DEM-07) antes de liberar: OS-0501 pede comprar ' + JSON.stringify(dem.itens.map(i => [i.p, i.q])) + ' na Lagoa Grande');
  veredito('A-10', e === '' && cruz.length === 2 && !avisa, 'liberação reservaria 2 itens em lote de outra fazenda, sem transferência nem aviso');
  veredito('A-10b', e === '' && dem.itens.every(i => i.q > 0), 'duas respostas para a mesma pergunta: a liberação diz "coberto"; a demanda única diz "falta comprar" (cenLote × cenOsDem)');
});

caso('R4 · OS-0425 · NPK 11.400 kg com lote de 8.000 kg ("parcial semeado")', () => {
  cenReset(); const c = cenGet(); const co = c.ordens['OS-0425']; const req = c.reqs[co.req];
  log('  etapa ' + co.etapa + ' · necessidade ' + n(co.ins[0].tot) + ' kg · reservado na ' + co.req + ': ' + n(req.itens[0].solicitado) + ' kg no ' + req.itens[0].lote);
  const o = linha(c, 'OS-0425'); let sit = '';
  try { sit = osInsSit(o, o.ins[0], req.itens[0]); } catch (e) { sit = '(osInsSit indisponível: ' + e.message + ')'; }
  log('  situação do insumo: "' + sit + '"');
  const k = cenClone(c); const kc = k.ordens['OS-0425']; kc.etapa = 'A liberar'; kc.reservado = false; delete k.reqs[kc.req]; kc.req = '';
  k.lotes['NPK 20-05-20|N26-03'].reservado = 0;
  const e = osLibErro(linha(k, 'OS-0425'), k);
  log('  contrafactual (mesma ordem em A liberar, sem a reserva semeada): osLibErro "' + e + '"');
  veredito('A-11', co.etapa === 'Liberadas' && req.itens[0].solicitado < co.ins[0].tot && /^Saldo insuficiente de NPK/.test(e), 'estado "liberada com falta" só existe na semente; a regra atual recusaria (tudo ou nada)');
});

caso('R5 · dois lotes que juntos cobrem ainda bloqueiam (sintético derivado: G26-14 com 200 L + lote G26-15 com 200 L)', () => {
  cenReset(); const k = cenClone(cenGet());
  k.lotes['Glifosato 480|G26-14'].fisico = 200;
  k.lotes['Glifosato 480|G26-15'] = Object.assign({}, k.lotes['Glifosato 480|G26-14'], { lote: 'G26-15', fisico: 200, reservado: 0 });
  const e = osLibErro(linha(k, 'OS-0430'), k);
  log('  OS-0430 pede 320 L; disponível 200 + 200 = 400 L · osLibErro "' + e + '"');
  veredito('A-12', /^Saldo insuficiente de Glifosato 480: 200 L disponíveis para 320 L/.test(e), 'reserva em um único lote (cenLote: maior disponível), sem divisão nem FEFO');
});

caso('R6 · corrida pela demanda futura + reserva entre fazendas (sintético derivado: G26-14 com 400 L)', () => {
  cenReset(); const k = cenClone(cenGet()); k.lotes['Glifosato 480|G26-14'].fisico = 400;
  const e430 = osLibErro(linha(k, 'OS-0430'), k), e501 = osLibErro(linha(k, 'OS-0501'), k);
  log('  antes: OS-0430 (Santa Rita, 320 L) "' + e430 + '" · OS-0501 (Lagoa Grande, 147,93 L) "' + e501 + '"');
  const r = osc_libEfeito(k, 'OS-0501', false, linha(k, 'OS-0501').janela);
  log('  libera OS-0501 primeiro: "' + r.msg + '"');
  const d = osLibErro(linha(k, 'OS-0430'), k);
  log('  depois: OS-0430 "' + d + '"');
  veredito('A-13', e430 === '' && e501 === '' && /^Saldo insuficiente de Glifosato 480/.test(d) && !/OS-0430/.test(r.msg), 'quem libera primeiro leva; a liberação da OS-0501 não avisa que deixa a OS-0430 (outra fazenda) sem saldo');
});

caso('R7 · padrão MA de 1 clique (OM-0235, filtro MF 4292)', () => {
  cenReset(); const m = manClone(MAN0); manGerarTodas(m, null, OT); const id = 'OM-0235'; const o = m.oms[id];
  log('  manFalta: ' + JSON.stringify(manFalta(m, o).map(p => [p.item, p.qtd, manLivreIt(m, p.item)])) + ' · criticidade da OM: ' + (o.crit || '—'));
  const r1 = manSolicitar(m, id, OT); const sc = o.sc.id; const q = cmmDe(m).reqs[sc];
  log('  1º clique "Solicitar compra": "' + r1.msg + '"');
  log('  SC na fila de Compras: orig=' + q.orig + ' · om=' + q.om + ' · ativo=' + q.aid + ' · urg=' + q.urg + ' · etapa=' + q.etapa + ' · qtd=' + q.itens[0].qtd + ' · motivo="' + q.motivo + '" · tem safra? ' + ('safra' in q));
  const r2 = manSolicitar(m, id, OT);
  log('  2º clique: ' + JSON.stringify({ nada: r2.nada, msg: r2.msg }) + ' · SCs da OM: ' + Object.values(cmmDe(m).reqs).filter(x => x.om === id).length);
  cmmCotar(m, sc, ANA); const ref = cmmSugerida(m, cmmDe(m).reqs[sc]); cmmPedir(m, sc, ref.f, '', ANA);
  const s0 = m.itens['FIL-MF4292'].saldo; const rc = cmmReceber(m, sc, RUI, undefined, 'REC-K1');
  log('  recebimento (Rui, chave REC-K1): "' + rc.msg + '"');
  log('  depois: saldo ' + s0 + '→' + m.itens['FIL-MF4292'].saldo + ' · reservado ' + m.itens['FIL-MF4292'].reservado + ' · peça da OM res=' + o.pecas.find(p => p.item === 'FIL-MF4292').res + ' · manFalta=' + manFalta(m, o).length);
  const rc2 = cmmReceber(m, sc, RUI, undefined, 'REC-K1');
  log('  repetir recebimento com a mesma chave: ' + JSON.stringify({ repetido: rc2.repetido, saldo: m.itens['FIL-MF4292'].saldo, reservado: m.itens['FIL-MF4292'].reservado }));
  let lib = ''; try { lib = manLiberar(m, id, true, OT).msg; } catch (e) { lib = 'ERRO ' + e.message; }
  log('  liberar a OM: "' + lib + '"');
  veredito('A-30', !!r1.msg && r2.nada && q.orig === 'om' && q.om === id && q.itens[0].qtd === 1 && m.itens['FIL-MF4292'].reservado === 1 && rc2.repetido && !/ERRO/.test(lib),
    '1 clique cria a SC só com a falta, não duplica, carrega OM e ativo; o recebido fica reservado para a OM (D5) e a mesma chave não soma de novo');
  veredito('A-31', q.urg !== 'Urgente', 'urgência vem da criticidade da OM (Alta→Alta, senão Normal), não de ativo parado');
  log('  papéis por passo: Solicitar=PCM · Cotar/Pedir=gestora ou direção · Receber=almoxarife ou gestora · Liberar=PCM (cmmPode, manPode)');
});

caso('R7b · segregação: a mesma pessoa pede, aprova (emite) e recebe a própria compra', () => {
  cenReset(); const m = manClone(MAN0);
  const a = cmmNova(m, { tipo: 'Material', nome: 'Material sintético', qtd: '2', un: 'un', preco: '100', destino: 'Oficina', urg: 'Urgente', motivo: 'teste de segregação' }, ANA);
  log('  Ana abre ' + a.id + ': "' + a.msg + '"');
  let r = []; try { r.push(cmmCotar(m, a.id, ANA).msg); const p = cmmSugerida(m, cmmDe(m).reqs[a.id]); r.push(cmmPedir(m, a.id, p.f, '', ANA).msg); r.push(cmmReceber(m, a.id, ANA, ['2'], 'SEG-K1').msg); } catch (e) { r.push('RECUSA ' + e.message); }
  r.forEach(t => log('   - ' + t));
  veredito('A-25', !r.some(t => /^RECUSA/.test(t)), 'nenhuma trava impede quem pediu de aprovar e receber a própria compra (alçada só por valor no pedido)');
});

caso('R7c · corrida do livre na OM: a SC pede nec − livre, o livre some, e a OM fica num beco (sintético derivado)', () => {
  cenReset(); const m = manClone(MAN0); manGerarTodas(m, null, OT); const A = m.oms['OM-0235'], B = m.oms['OM-0236'];
  m.itens['FIL-MF4292'].saldo = 1; A.pecas.find(p => p.item === 'FIL-MF4292').qtd = 2;
  const pb = Object.assign({}, A.pecas.find(p => p.item === 'FIL-MF4292'), { qtd: 1, res: 0 }); B.pecas = (B.pecas || []).concat([pb]);
  const s = manSolicitar(m, 'OM-0235', OT); log('  OM-0235 precisa 2, livre 1 → "' + s.msg + '"');
  let lb = ''; try { lb = manLiberar(m, 'OM-0236', true, OT).msg; } catch (e) { lb = 'ERRO ' + e.message; } log('  OM-0236 libera antes e leva o livre: "' + lb + '"');
  const sc = A.sc.id; cmmCotar(m, sc, ANA); const p = cmmSugerida(m, cmmDe(m).reqs[sc]); cmmPedir(m, sc, p.f, '', ANA); cmmReceber(m, sc, RUI, undefined, 'RC7C');
  log('  SC recebida: etapa ' + cmmDe(m).reqs[sc].etapa + ' · res na OM-0235 ' + A.pecas.find(x => x.item === 'FIL-MF4292').res + ' de 2 · manFalta ' + manFalta(m, A).length);
  const s2 = manSolicitar(m, 'OM-0235', OT); log('  "Solicitar compra" de novo: ' + JSON.stringify({ nada: s2.nada, msg: s2.msg }));
  let e = ''; try { manLiberar(m, 'OM-0235', true, OT); } catch (x) { e = x.message; } log('  liberar OM-0235: "' + e + '"');
  veredito('NOVO-1', s2.nada && /Aguarda o recebimento da SC/.test(e) && cmmDe(m).reqs[sc].etapa === 'Recebida', 'idempotência por "OM já tem SC" trava a 2ª compra; a mensagem manda aguardar uma SC já recebida (beco sem saída)');
});

caso('R8 · o único caminho avulso (SC de materiais) não resolve a falta de insumo da O.S.', () => {
  cenReset(); const k = cenClone(cenGet()); const m = k.man;
  log('  centros de custo da avulsa: ' + JSON.stringify(CMM.ccs) + ' · urgência: ' + JSON.stringify(CMM.urg) + ' · prazo por urgência ' + JSON.stringify(CMM.urgDias));
  const a = cmmNova(m, { tipo: 'Material', nome: 'Ureia 45%', qtd: '1140', un: 'kg', preco: '3', destino: 'Sede', urg: 'Urgente', motivo: 'Falta para a OS-0418' }, ANA);
  log('  ' + (a.erro ? 'RECUSA ' + a.erro : a.msg) + ' · grupo ' + (a.id ? cmmDe(m).reqs[a.id].itens[0].grupo : ''));
  let passos = []; try { passos.push(cmmCotar(m, a.id, ANA).msg); const p = cmmSugerida(m, cmmDe(m).reqs[a.id]); passos.push(cmmPedir(m, a.id, p.f, '', ANA).msg); passos.push(cmmReceber(m, a.id, RUI, ['1140'], 'R8').msg); } catch (e) { passos.push('PARA ' + e.message); }
  passos.forEach(t => log('   - ' + t));
  const lotes = Object.values(k.lotes).filter(l => l.prod === 'Ureia 45%').length; const e = osLibErro(linha(k, 'OS-0418'), k);
  log('  depois: lotes de Ureia ' + lotes + ' · OS-0418 osLibErro "' + e + '"');
  veredito('A-20', lotes === 0 && /^Sem lote de Ureia/.test(e), 'a avulsa aceita "Ureia" como material sem código (consumo direto no centro de custo) e não abastece o lote: a O.S. continua bloqueada; não há recusa explícita de insumo, a barreira é estrutural');
});

caso('R9 · idempotência: mesma chave, outro conteúdo', () => {
  cenReset(); const m = manClone(MAN0);
  const r = cmmRepor(m, 'GR-EP2', RUI); cmmCotar(m, r.id, ANA); const p = cmmSugerida(m, cmmDe(m).reqs[r.id]); cmmPedir(m, r.id, p.f, '', ANA);
  const a1 = cmmReceber(m, r.id, RUI, ['10'], 'K9'); const a2 = cmmReceber(m, r.id, RUI, ['12'], 'K9');
  log('  Compras (manCmd): 10 kg com K9 → "' + a1.msg.slice(0, 90) + '…" · 12 kg com K9 → ' + JSON.stringify({ repetido: a2.repetido, msg: a2.msg.slice(0, 120) }));
  const k = cenClone(cenGet()); let c2 = '';
  try { cenEntregar(k, 'REQ-039', 'Fungicida A', 5, 'Marcos', RUI, 'E9'); cenEntregar(k, 'REQ-039', 'Fungicida A', 6, 'Marcos', RUI, 'E9'); } catch (e) { c2 = e.message; }
  log('  Estoque (cenIdem): 5 L com E9 e 6 L com E9 → "' + c2 + '"');
  veredito('NOVO-2', a2.repetido && /conflito/.test(c2), 'duas regras de idempotência: Compras/MA (manCmd) aceita a mesma chave com outro conteúdo como "repetido"; o Estoque (cenIdem) acusa conflito (PRD 73.3: chave + hash do conteúdo)');
});

log('\nRESUMO ' + OUT.filter(t => /^  CONFIRMA/.test(t)).length + ' confirmações · ' + OUT.filter(t => /^  NÃO REPRODUZ/.test(t)).length + ' não reproduz · ' + OUT.filter(t => /EXCEÇÃO/.test(t)).length + ' exceções');
