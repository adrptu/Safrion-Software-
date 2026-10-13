// A4 (S2 do Estoque; contrato do PR #47, comentário 6147474674) · node, sem navegador. Executor: est_a4_test.py.
// Aprovar ajuste de inventário revalida a contagem no instante da aprovação: movimento físico ou de qualidade do lote depois dela recusa
// sem efeito (o ajuste fica pendente, sem movimento e sem mudar o físico); contagem atual abaixo da reserva aplica e mostra "Reserva sem
// físico" com dono; contado abaixo da quarentena é recusado. Vale na tela (estAprovar) e na entrada direta do motor (cenAprovarAjuste).
// Cada caso parte do cenário inicial e grava pelo cenMudar (atômico: erro não grava nada), como a tela faz. Dados sintéticos.
(() => {   // escopo próprio: os nomes do teste não colidem com os do motor
let nfail = 0;
function ok(t, c, got) { if (c) console.log('OK    ' + t); else { nfail++; console.log('FALHA ' + t + (got === undefined ? '' : ' · ' + JSON.stringify(got).slice(0, 500))); } }
const caso = (t, f) => { console.log('\n— ' + t); try { f(); } catch (e) { ok('ERRO no caso "' + t + '": ' + String(e.message || e), false); } };
const P = k => G2_PERFIS.find(p => p.k === k);
const ANA = P('Ana'), RUI = P('Rui'), IGOR = P('Igor');
const G = () => cenGet();
const M = fn => cenMudar(null, fn);
const CX = BENC.cx.item, K02 = CX + '|CX26-02';
const lot = (k) => { const l = G().lotes[k || K02]; return l ? [l.fisico, l.quarentena, l.reservado] : null; };
const nAjMov = (lote) => G().movs.filter(m => m.tipo === 'ajuste' && m.lote === (lote || 'CX26-02')).length;
const snap = () => JSON.stringify(G());
// passos do roteiro (os mesmos comandos das telas)
const nf = (q, doc, lote, apto) => M(c => cenReceber(c, CX, lote || 'CX26-02', q, 'un', 'Packing', '—', doc, apto !== false, RUI));
const contar = (cont, lote, causa) => M(c => { const inv = enovoInv(c); const r = estContar(c, inv, CX + '|' + (lote || 'CX26-02'), cont, 'Paula (almoxarife)', causa || 'caixas amassadas descartadas', RUI); r.inv = inv; return r; });
const invDe = r => (String(r.msg || '').match(/INV-\d+/) || [''])[0];
const liberarOB = () => { const r = M(c => benNova(c, { lotes: [{ lote: 'L39-132', kg: prFis(c, 'L39-132') }] }, IGOR)); const id = r.id; M(c => benAutorizarLiberar(c, id, IGOR)); return { id, rid: G().ordens[id].req }; };
const entregar = (rid, q) => M(c => estEntregar(c, rid, CX, q, 'Igor', RUI));
const aprovar = (inv, ator) => M(c => estAprovar(c, inv, ator || ANA));
const ajDe = inv => (G().ajustes || []).find(a => a.inv === inv);
const DES = /está desatualizada/;

caso('A4 · roteiro do revisor: NF 1.200 → contagem 1.100 (pendente) → OB-0113 liberada e entregue com 1.169 → aprovar (Ana)', () => {
  cenReset(); nf(1200, 'NF 7731'); const inv = invDe(contar(1100)); const ob = liberarOB();
  ok('OB-0113 reservou 1.169 un do CX26-02 (físico 1.200)', JSON.stringify(lot()) === '[1200,0,1169]', lot());
  const re = entregar(ob.rid, 1169); ok('entrega de 1.169 un aceita (físico 31)', !re.erro && lot()[0] === 31, re.erro || lot());
  const s0 = snap(); const r = aprovar(inv);
  ok('aprovar é recusado: contagem desatualizada (1 movimento depois dela) e o caminho "Recontar"', DES.test(r.erro || '') && /1 movimento \(entrega de 1\.169 un · REQ-041\)/.test(r.erro || '') && /\(Recontar\)/.test(r.erro || ''), r.erro || r.msg);
  ok('recusa atômica: estado idêntico ao de antes (físico 31, nunca −69)', snap() === s0 && lot()[0] === 31, lot());
  ok('o ajuste continua pendente e não há movimento de ajuste', (ajDe(inv) || {}).estado === 'Aguardando gestor' && nAjMov() === 0, ajDe(inv));
  ok('a custódia da OB-0113 segue 1.169 un', G().reqs[ob.rid].itens.find(i => i.prod === CX).custodia === 1169);
  // entrada direta do motor (o servidor é a autoridade): a mesma regra
  const s1 = snap(); const rd = M(c => cenAprovarAjuste(c, ajDe(inv).id, true, ANA));
  ok('entrada direta cenAprovarAjuste: a mesma recusa, sem fabricar físico (nunca 1.100)', DES.test(rd.erro || '') && snap() === s1 && lot()[0] === 31, rd.erro || lot());
  const c2 = cenClone(G()); const antes = JSON.stringify(c2); let er = '';
  try { cenAprovarAjuste(c2, ajDe(inv).id, true, ANA); } catch (e) { er = String(e.message); }
  ok('o motor recusa antes de tocar o estado (chamado fora do cenMudar)', DES.test(er) && JSON.stringify(c2) === antes, er);
  // caminho de recuperação: recontar com outro contador e aprovar a nova diferença
  const rr = M(c => estRecontar(c, inv)); ok('Recontar abre a recontagem (o ajuste velho fica recusado, saldo intacto)', !rr.erro && (G().ajustes.find(a => a.inv === inv && a.estado === 'Recusado')) && lot()[0] === 31, rr.erro || rr.msg);
  const rc = M(c => estContar(c, inv, K02, 0, 'Rui (almoxarife)', 'recontagem: lote vazio', RUI)); const ra = aprovar(inv);
  ok('recontagem 0 e aprovação: físico 31 → 0, um movimento de ajuste −31', !rc.erro && !ra.erro && lot()[0] === 0 && nAjMov() === 1 && G().movs.find(m => m.tipo === 'ajuste').qtd === -31, [rc.erro, ra.erro || ra.msg, lot()]);
});

caso('A4 · entrada direta do motor primeiro (sem a tela): o mesmo roteiro e cenAprovarAjuste(AJ-71, Ana)', () => {
  cenReset(); nf(1200, 'NF 7731'); const inv = invDe(contar(1100)); const ob = liberarOB(); entregar(ob.rid, 1169); const s0 = snap();
  const rd = M(c => cenAprovarAjuste(c, ajDe(inv).id, true, ANA));
  ok('recusado; físico 31 (sem fabricar as 1.069 un que levariam o lote a 1.100) e nenhum movimento de ajuste', DES.test(rd.erro || '') && snap() === s0 && lot()[0] === 31 && nAjMov() === 0, rd.erro || [rd.msg, lot()]);
  const c = G(); const tot = Object.values(c.lotes).filter(l => l.prod === CX).reduce((a, l) => a + l.fisico, 0) + Object.values(c.reqs).reduce((a, r) => a + r.itens.filter(i => i.prod === CX).reduce((b, i) => b + i.custodia + i.consumido, 0), 0);
  const t0 = Object.values(CEN0.lotes).filter(l => l.prod === CX).reduce((a, l) => a + l.fisico, 0) + Object.values(CEN0.reqs).reduce((a, r) => a + r.itens.filter(i => i.prod === CX).reduce((b, i) => b + i.custodia + i.consumido, 0), 0);
  const aj = c.movs.filter(m => m.prod === CX && (m.tipo === 'recebimento-nf' || m.tipo === 'ajuste')).reduce((a, m) => a + m.qtd, 0);
  ok('conservação das caixas: físico + custódia + consumo = início + entradas + ajustes', Math.abs(tot - (t0 + aj)) < 1e-9, [tot, t0 + aj]);
});

caso('(a) contagem 1.100 → reserva 1.169 → aprovar: aplica 1.100, falta 69 com dono; a entrega de 1.169 continua recusada', () => {
  cenReset(); nf(1200, 'NF 7731'); const inv = invDe(contar(1100)); const ob = liberarOB(); const r = aprovar(inv);
  ok('aprovado: físico 1.100 e a reserva 1.169 preservada', !r.erro && JSON.stringify(lot()) === '[1100,0,1169]', r.erro || lot());
  ok('alerta "Reserva sem físico: 69 un" com a requisição, o dono e a recuperação', /Reserva sem físico: 69 un no lote CX26-02 \(REQ-041\) · Rui \(almoxarife\) ou Paula \(almoxarife\) confere o lote e recebe a reposição/.test(r.msg || ''), r.msg);
  ok('o disponível exibido não fica negativo (0)', cenDisp(G().lotes[K02]) === 0, cenDisp(G().lotes[K02]));
  const e1 = entregar(ob.rid, 1169); ok('entrega de 1.169 un recusada', /não tem 1\.169 un livres/.test(e1.erro || ''), e1.erro || e1.msg);
  const e2 = entregar(ob.rid, 1100); ok('entrega de 1.100 un aceita; o lote fica 0', !e2.erro && lot()[0] === 0, e2.erro || lot());
});

caso('(b) reserva 1.169 já existe → contagem 1.100 → aprovar', () => {
  cenReset(); nf(1200, 'NF 7731'); liberarOB(); const rc = contar(1100);
  ok('a contagem abaixo da reserva é aceita (sem isso recontar seria impossível) e avisa a falta', !rc.erro && /Se aprovado: Reserva sem físico: 69 un/.test(rc.msg || ''), rc.erro || rc.msg);
  const r = aprovar(invDe(rc)); ok('aprovado: físico 1.100, reserva 1.169, falta 69', !r.erro && JSON.stringify(lot()) === '[1100,0,1169]' && /Reserva sem físico: 69 un/.test(r.msg || ''), r.erro || r.msg);
});

caso('(c) 100 → contagem 90 → entrada de 50 → aprovar: recusado', () => {
  cenReset(); nf(100, 'NF 8001', 'CX26-09'); const inv = invDe(contar(90, 'CX26-09')); nf(50, 'NF 8002', 'CX26-09'); const s0 = snap();
  const r = aprovar(inv); ok('recusa na tela: 1 movimento (entrada de 50 un · NF 8002)', DES.test(r.erro || '') && /entrada de 50 un · NF 8002/.test(r.erro || '') && snap() === s0 && lot(CX + '|CX26-09')[0] === 150, r.erro || lot(CX + '|CX26-09'));
  const rd = M(c => cenAprovarAjuste(c, ajDe(inv).id, true, ANA)); ok('recusa no motor: o físico segue 150 (nunca 90, que apagaria a entrada)', DES.test(rd.erro || '') && lot(CX + '|CX26-09')[0] === 150, rd.erro || lot(CX + '|CX26-09'));
});

caso('(d) saída e retorno ao mesmo saldo → aprovar: recusado (a versão é a trilha, não a igualdade do físico)', () => {
  cenReset(); nf(1200, 'NF 7731'); const inv = invDe(contar(1100)); const ob = liberarOB(); entregar(ob.rid, 100);
  const rv = M(c => cenDevolver(c, ob.rid, CX, 100, true, RUI)); ok('entrega de 100 e devolução apta de 100: físico volta a 1.200', !rv.erro && lot()[0] === 1200, rv.erro || lot());
  const r = aprovar(inv); ok('aprovar recusado: 2 movimentos depois da contagem; nada muda', DES.test(r.erro || '') && /2 movimentos/.test(r.erro || '') && lot()[0] === 1200 && nAjMov() === 0, r.erro || r.msg);
});

caso('(e) mudança de qualidade sem mudança física → aprovar: recusado', () => {
  cenReset(); nf(150, 'NF 8101', 'CX26-08'); nf(50, 'NF 8102', 'CX26-08', false); const K = CX + '|CX26-08';
  const inv = invDe(contar(190, 'CX26-08')); const rl = M(c => cenLiberarQuarentena(c, K, 'LAB-77', ANA));
  ok('laudo libera os 50 un da quarentena (físico 200, sem mudança física)', !rl.erro && JSON.stringify(lot(K)) === '[200,0,0]', rl.erro || lot(K));
  const r = aprovar(inv); ok('aprovar recusado (laudo depois da contagem); físico 200, sem ajuste', DES.test(r.erro || '') && /laudo que liberou a quarentena/.test(r.erro || '') && lot(K)[0] === 200 && nAjMov('CX26-08') === 0, r.erro || r.msg);
});

caso('(f) contado abaixo da quarentena → recusa sem efeitos e sem liberar o bloqueado', () => {
  cenReset(); nf(150, 'NF 8101', 'CX26-08'); nf(50, 'NF 8102', 'CX26-08', false); const K = CX + '|CX26-08'; const s0 = snap();
  const rc = contar(40, 'CX26-08'); ok('contagem 200 → 40 com 50 bloqueados: recusada, nada gravado, os 50 seguem bloqueados', !!rc.erro && snap() === s0 && JSON.stringify(lot(K)) === '[200,50,0]', rc.erro || rc.msg);
  ok('o motivo pede a conferência da parcela bloqueada ou da perda, com responsável', /abaixo do bloqueado em quarentena \(50 un\)/.test(rc.erro || '') && /Rui \(almoxarife\) ou Paula \(almoxarife\) confere a parcela bloqueada ou a perda/.test(rc.erro || '') && /Ana \(gestora\)/.test(rc.erro || ''), rc.erro);
  // entrada direta do motor com um ajuste pendente atual de 40 un (gravado sem passar pela contagem da tela)
  M(c => { c.ajustes = c.ajustes || []; c.ajustes.push({ id: 'AJ-99', key: K, prod: CX, lote: 'CX26-08', un: 'un', sistema: 200, contado: 40, dif: -160, estado: 'Aguardando gestor', mv: c.movs.length }); return { msg: 'ok' }; });
  const s1 = snap(); const rd = M(c => cenAprovarAjuste(c, 'AJ-99', true, ANA));
  ok('motor: aprovar 40 com 50 bloqueados é recusado; físico 200 e quarentena 50 intactos', /abaixo do bloqueado em quarentena/.test(rd.erro || '') && snap() === s1 && JSON.stringify(lot(K)) === '[200,50,0]', rd.erro || lot(K));
});

caso('ajuste legítimo sem reserva: aplica e grava a trilha', () => {
  cenReset(); nf(1200, 'NF 7731'); const rc = contar(1100); const inv = invDe(rc); const r = aprovar(inv); const m = G().movs.find(x => x.tipo === 'ajuste');
  ok('aprovado: físico 1.200 → 1.100 e mensagem sem alerta', !r.erro && lot()[0] === 1100 && r.msg === 'Ajuste ' + inv + ' (AJ-71) aprovado por Ana (gestora): −100 un no lote CX26-02. Físico 1.200 un → 1.100 un.', r.erro || r.msg);
  ok('movimento de ajuste −100 un com o documento, o ajuste e o aprovador', m && m.qtd === -100 && m.doc === inv && m.aj === 'AJ-71' && m.quem === 'Ana (gestora)', m);
});

caso('papel: só o gestor aprova (a contagem atual ou desatualizada não muda isso)', () => {
  cenReset(); nf(1200, 'NF 7731'); const inv = invDe(contar(1100)); const s0 = snap();
  const r = aprovar(inv, RUI); ok('Rui não aprova; nada muda', r.erro === 'Aprovar o ajuste ' + inv + ': decisão de Ana (gestora). Nada foi alterado.' && snap() === s0, r.erro || r.msg);
  const ob = liberarOB(); entregar(ob.rid, 1169); const r2 = aprovar(inv, RUI);
  ok('com a contagem desatualizada, Rui recebe a recusa de papel (o papel vem antes)', /decisão de Ana \(gestora\)/.test(r2.erro || '') && lot()[0] === 31, r2.erro);
  const rf = aprovar(inv, { k: 'Rui', papeis: { gestor: 'gestora' } }); ok('perfil forjado como gestor não aprova', /decisão de Ana \(gestora\)/.test(rf.erro || ''), rf.erro);
});

caso('envio duplo: aplica uma vez', () => {
  cenReset(); nf(1200, 'NF 7731'); const inv = invDe(contar(1100)); aprovar(inv); const r2 = aprovar(inv);
  ok('repetir na tela: "já aprovado", físico 1.100 e um só movimento', r2.erro === 'Ajuste ' + inv + ' já aprovado · nada aplicado de novo.' && lot()[0] === 1100 && nAjMov() === 1, r2.erro);
  const r3 = M(c => cenAprovarAjuste(c, 'AJ-71', true, ANA)); ok('repetir no motor: "não está pendente", nada aplicado', r3.erro === 'Ajuste não está pendente.' && lot()[0] === 1100 && nAjMov() === 1, r3.erro);
  cenReset(); nf(1200, 'NF 7731'); const i1 = invDe(contar(1100)); const i2 = invDe(contar(1100)); const a1 = aprovar(i1); const a2 = aprovar(i2);
  ok('duas contagens da mesma falta: a segunda fica desatualizada pelo ajuste da primeira (nunca 1.000)', !a1.erro && DES.test(a2.erro || '') && lot()[0] === 1100 && nAjMov() === 1, [a1.erro, a2.erro, lot()]);
});

caso('sem travar a recuperação: contagem → reserva → entrega de 1.100 → aprovação recusada → recontagem 0 aceita com a reserva de 69', () => {
  cenReset(); nf(1200, 'NF 7731'); const inv = invDe(contar(1100)); const ob = liberarOB(); entregar(ob.rid, 1100);
  const r = aprovar(inv); ok('aprovação recusada (entrega depois da contagem); físico 100', DES.test(r.erro || '') && lot()[0] === 100, r.erro || lot());
  M(c => estRecontar(c, inv)); const rc = M(c => estContar(c, inv, K02, 0, 'Rui (almoxarife)', 'lote vazio na recontagem', RUI));
  ok('recontagem 0 com 69 reservados é aceita (antes era recusada e o lote ficava preso)', !rc.erro && /Reserva sem físico: 69 un/.test(rc.msg || ''), rc.erro || rc.msg);
  const ra = aprovar(inv); ok('aprovada: físico 0, reserva 69 preservada, alerta com dono', !ra.erro && JSON.stringify(lot()) === '[0,0,69]' && /Reserva sem físico: 69 un/.test(ra.msg || ''), ra.erro || ra.msg);
});

caso('contagem sem marcador confiável exige recontagem', () => {
  cenReset(); nf(1200, 'NF 7731'); const inv = invDe(contar(1100));
  M(c => { const a = c.ajustes.find(x => x.inv === inv); delete a.mv; return { msg: 'ok' }; });
  const r = aprovar(inv); ok('ajuste pendente sem marcador da trilha: recusado, físico 1.200', /não tem o marcador/.test(r.erro || '') && lot()[0] === 1200 && nAjMov() === 0, r.erro || r.msg);
});

caso('contagem de base (INV-2609, anterior à demonstração): marcador no início da trilha', () => {
  cenReset(); const K = 'MAP 11-52|M26-07'; M(c => estCausa(c, 'INV-2609', 'Sacaria rasgada na pilha 3'));
  const r = aprovar('INV-2609'); ok('lote sem movimento: aprova −600 kg (90.000 → 89.400)', !r.erro && G().lotes[K].fisico === 89400, r.erro || G().lotes[K].fisico);
  cenReset(); M(c => estCausa(c, 'INV-2609', 'Sacaria rasgada na pilha 3'));
  M(c => cenReceber(c, 'MAP 11-52', 'M26-07', 1000, 'kg', 'Galpão 2', '—', 'NF 9001', true, RUI));
  const s0 = snap(); const r2 = aprovar('INV-2609');
  ok('com entrada depois do início: recusado, sem criar ajuste nem mudar o físico (91.000)', DES.test(r2.erro || '') && snap() === s0 && G().lotes[K].fisico === 91000 && !(G().ajustes || []).length, r2.erro || r2.msg);
});

caso('A4 · quantidade contada finita (Codex 6148863313): Infinity, NaN e null recusados na contagem e na aprovação; 0 vale', () => {
  cenReset(); nf(1200, 'NF 7731');
  for (const [nome, v] of [['9…9 (309 dígitos) → Infinity', g2num('9'.repeat(309))], ['NaN', NaN], ['vazio', g2num('')], ['negativo', -1]]) {
    const s0 = snap(); const r = contar(v);
    ok('contagem ' + nome + ': recusada sem efeito (nenhum ajuste, físico 1.200)', !!r.erro && snap() === s0 && lot()[0] === 1200 && !(G().ajustes || []).length, r.erro || r.msg);
  }
  const inv = invDe(contar(1100)); ok('contagem 1.100 registrada (pendente)', (ajDe(inv) || {}).estado === 'Aguardando gestor', ajDe(inv));
  // contado corrompido depois de salvo (o Infinity vira null no JSON): a aprovação confere de novo, antes de qualquer mutação
  for (const [nome, v] of [['null', null], ['Infinity', Infinity], ['NaN', NaN], ['texto', '1100']]) {
    M(c => { c.ajustes.find(x => x.inv === inv).contado = v; return { msg: 'ok' }; });
    const s1 = snap(); const rt = aprovar(inv); const rd = M(c => cenAprovarAjuste(c, ajDe(inv).id, true, ANA));
    ok('aprovar com contado ' + nome + ': recusado pela tela e pelo motor, físico 1.200, ajuste pendente, sem movimento', /Contagem inválida/.test(rt.erro || '') && /Contagem inválida/.test(rd.erro || '') && snap() === s1 && lot()[0] === 1200 && ajDe(inv).estado === 'Aguardando gestor' && nAjMov() === 0, [rt.erro || rt.msg, rd.erro || rd.msg]);
  }
  M(c => { const a = c.ajustes.find(x => x.inv === inv); a.contado = 1100; a.dif = -100; return { msg: 'ok' }; });
  const ra = aprovar(inv); ok('contado 1.100 restaurado: aprova (físico 1.100)', !ra.erro && lot()[0] === 1100, ra.erro || lot());
  const i0 = invDe(contar(0)); const r0 = aprovar(i0); ok('contagem 0 continua válida: registrada e aprovada (físico 0)', !!i0 && !r0.erro && lot()[0] === 0, [i0, r0.erro || r0.msg, lot()]);
});

console.log('\nRESULTADO_JS ' + (nfail ? 'FALHA ' + nfail : 'OK'));
})();
