// B-R8 · divergência de consumo/dose no fecho do turno (revisão Codex 6064114787 §2 e "Prova focal recuperável B-R8") · node, sem navegador.
// Carregado depois de: g2num + perfis + CEN0 + cenario.js + OSD + núcleo da O.S. (dose_divergente_test.py). Dados sintéticos.
// Regra: o consumo informado diferente do planejado para a área apontada (dose × área pela regra única, centésimo da unidade) é gravado
// como informado, marca o apontamento e a O.S. ("Divergência de consumo/dose", por produto, planejado × informado com unidade) e abre
// revisão técnica do agrônomo, resolvida (aceitar com motivo ou registrar a correção) antes do encerramento final. Dano evitado: subdose
// ou superdose aplicada sem decisão do agrônomo passar por execução conforme (resultado técnico da lavoura e receituário).
const R = []; function ok(n, c, info) { R.push({ n, ok: !!c, info: c ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 900) }); }
const TRY = (f) => { try { return { r: f() }; } catch (e) { return { erro: String(e.message || e) }; } };
const SELO = 'Divergência de consumo/dose';
const temSelo = (o) => (o.selos || []).filter(s => String(s.t).indexOf(SELO) === 0);
const MUD = (c, fn) => { const x = cenClone(c); try { const r = fn(x) || {}; Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); return r; } catch (e) { return { erro: String(e.message || e) }; } };
const ABERTAS = (o) => (typeof cenDivAbertas === 'function') ? cenDivAbertas(o) : [];
const REVER = (c, id, dia, dec, txt, ator) => MUD(c, x => cenDivRever(x, id, dia, dec, txt, ator));
// a mesma preparação do harness Codex: OS-0430 aprovada e liberada por Ana, três insumos entregues a Marcos e confirmados, turno iniciado
function prep() { const c = cenClone(CEN0), id = 'OS-0430';
  const lib = osc_liberar(c, id, false, '', 'Ana'); const o = c.ordens[id], rid = o.req;
  c.reqs[rid].itens.forEach(i => cenEntregar(c, rid, i.prod, i.solicitado, 'Marcos', 'Rui'));
  cenConfirmarRecebimento(c, rid); cenIniciarTurno(c, id); return { c, id, o, rid, lib }; }
const IT = (c, rid, p) => c.reqs[rid].itens.find(i => i.prod === p);

// ---- D01 · reprodução Codex (B-R8): 10 ha, informado 20 / 0 / 0 contra 20 / 10 / 5 planejado ----
{ const { c, id, o, rid } = prep();
  const esperado = Object.fromEntries(o.ins.map(i => [i.p, cenQtdTrecho(i.dose, o.realizado, 10)]));
  const ret = TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 0, 'Óleo mineral': 0 }, 'Contraprova sintética Codex B-R8', []));
  const ap = o.ap.filter(a => a.st !== 'Previsto').slice(-1)[0] || {};
  console.log('REPRO B-R8 ' + JSON.stringify({ esperado, retorno: ret, realizado: o.realizado, saldo: o.saldo, st: ap.st, div: ap.div || null, selos: o.selos }));
  ok('D01a planejado do trecho pela regra única: 20 / 10 / 5 L para 10 ha', esperado['Glifosato 480'] === 20 && esperado['2,4-D 806'] === 10 && esperado['Óleo mineral'] === 5, esperado);
  ok('D01b o fato fica como informado: 10 ha realizados, apontamento Provisório, Glifosato 20 L baixado e 2,4-D e Óleo sem baixa (nada forçado à dose)',
     !ret.erro && o.realizado === 10 && ap.st === 'Provisório' && IT(c, rid, 'Glifosato 480').consumido === 20 && IT(c, rid, '2,4-D 806').consumido === 0 && IT(c, rid, 'Óleo mineral').consumido === 0,
     [ret, o.realizado, ap.st, c.reqs[rid].itens.map(i => [i.prod, i.consumido, i.custodia])]);
  const dv = (ap.div || []).map(d => d.p + ':' + d.plan + '>' + d.inf + ' ' + d.un).join(' | ');
  ok('D01c o apontamento guarda a divergência por produto, planejado × informado com unidade (2,4-D 806 10 → 0 L; Óleo mineral 5 → 0 L)',
     dv === '2,4-D 806:10>0 L | Óleo mineral:5>0 L', ap.div);
  const s = temSelo(o);
  ok('D01d a O.S. ganha o selo vermelho "Divergência de consumo/dose · 2,4-D 806, Óleo mineral"',
     s.length === 1 && s[0].t === SELO + ' · 2,4-D 806, Óleo mineral' && s[0].c === 'red', o.selos);
  ok('D01e revisão técnica pendente do agrônomo (uma, do dia 1)', ABERTAS(o).length === 1 && ABERTAS(o)[0].dia === 1, ABERTAS(o).map(a => a.dia));
  ok('D01f o fecho do turno diz o que divergiu e quem revisa, sem "S2"',
     !ret.erro && ret.r.msg === 'Turno fechado: 10 ha em 1 h. A ordem continua em execução. Divergência de consumo/dose: 2,4-D 806 planejado 10 L × informado 0 L; Óleo mineral planejado 5 L × informado 0 L · revisão técnica de Ana (agrônoma).'
     && !/S2/.test(ret.r.msg), ret); }

// ---- D02 · controle Codex: informado = planejado (20 / 10 / 5) não abre nada; mensagem de sempre ----
{ const { c, o } = prep();
  const ret = TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 10, 'Óleo mineral': 5 }, '', []));
  const ap = o.ap.filter(a => a.st !== 'Previsto').slice(-1)[0] || {};
  ok('D02 controle 20 / 10 / 5: sem divergência, sem selo, sem revisão; mesma mensagem de fecho',
     !ret.erro && ret.r.msg === 'Turno fechado: 10 ha em 1 h. A ordem continua em execução.' && !(ap.div || []).length && !temSelo(o).length && !ABERTAS(o).length
     && JSON.stringify(ap.cons) === JSON.stringify({ 'Glifosato 480': 20, '2,4-D 806': 10, 'Óleo mineral': 5 }), [ret, ap.div, o.selos, ap.cons]); }

// ---- D03 · sugestão não editada (est) é estimativa, não fato informado: não abre divergência ----
{ const { c, o } = prep();
  const ret = TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 10, 'Óleo mineral': 5 }, '', ['Glifosato 480', '2,4-D 806', 'Óleo mineral']));
  ok('D03 sugestão dose × área não editada: sem divergência nem selo', !ret.erro && !temSelo(o).length && !ABERTAS(o).length, [ret, o.selos]); }

// ---- D04 · precisão: centésimo da unidade (a da regra de quantidade, cenQtd); nenhuma tolerância inventada ----
{ const a = prep(); TRY(() => cenFecharTurno(a.c, 10, 1, { 'Glifosato 480': 20.004, '2,4-D 806': 10, 'Óleo mineral': 5 }, '', []));
  const b = prep(); TRY(() => cenFecharTurno(b.c, 10, 1, { 'Glifosato 480': 20.01, '2,4-D 806': 10, 'Óleo mineral': 5 }, '', []));
  const db = (b.o.ap.slice(-1)[0] || {}).div || [];
  ok('D04 20,004 L arredonda para 20,00 (igual ao planejado); 20,01 L diverge (centésimo, sem tolerância)',
     !temSelo(a.o).length && db.length === 1 && db[0].p === 'Glifosato 480' && db[0].plan === 20 && db[0].inf === 20.01, [a.o.selos, db]); }
// ---- D04b · revisão DOM achado 2: a comparação usa a regra de quantidade (decimal, meio para cima), não o arredondamento do float ----
{ const F = (q) => { const x = prep(); const r = TRY(() => cenFecharTurno(x.c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': q, 'Óleo mineral': 5 }, '', [])); return { r, div: (x.o.ap.slice(-1)[0] || {}).div || [], selo: temSelo(x.o).length }; };
  const a = F(9.995), b = F(10.005), d = F(10.0049);
  ok('D04b 9,995 L = 10,00 L (cenQtd) não diverge do planejado 10 L; 10,005 L = 10,01 L diverge e o texto mostra 10,01 L; 10,0049 L não diverge',
     !a.div.length && !a.selo && b.div.length === 1 && b.r.r && /2,4-D 806 planejado 10 L × informado 10,01 L/.test(b.r.r.msg) && !d.div.length && !d.selo, [a, b, d]); }

// ---- D05 · revisão: só o agrônomo; motivo obrigatório; recusa não muda nada ----
{ const { c, id, o } = prep(); TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 0, 'Óleo mineral': 0 }, '', []));
  const antes = JSON.stringify(c);
  const r1 = REVER(c, id, 1, 'aceitar', 'chuva lavou a calda', 'Rui');
  ok('D05a Rui (almoxarife) não revisa: recusado com quem decide, nada muda',
     r1.erro === 'Revisar a divergência de consumo/dose do dia 1 da OS-0430: decisão de Ana (agrônoma). Nada foi alterado.' && JSON.stringify(c) === antes, r1);
  const r2 = REVER(c, id, 1, 'aceitar', '   ', 'Ana');
  ok('D05b aceitar sem motivo é recusado, nada muda', r2.erro === 'Informe o motivo para aceitar a divergência do dia 1 da OS-0430. Nada foi alterado.' && JSON.stringify(c) === antes, r2);
  const r3 = REVER(c, id, 2, 'aceitar', 'x', 'Ana');
  ok('D05c dia sem divergência em revisão é recusado', /não tem divergência de consumo\/dose em revisão/.test(r3.erro || '') && JSON.stringify(c) === antes, r3);
  const r4 = REVER(c, id, 1, 'aceitar', 'Mistura sem 2,4-D por deriva no vizinho; controle conferido em campo', 'Ana');
  const ap = o.ap.find(a => a.dia === 1) || {}; const ap2 = c.ordens[id].ap.find(a => a.dia === 1) || {};
  ok('D05d Ana (agrônoma) aceita com motivo: revisão gravada com autor, selo sai, consumo informado continua como está',
     !r4.erro && ap2.rev && ap2.rev.dec === 'Aceita' && ap2.rev.quem === 'Ana (agrônoma)' && /deriva/.test(ap2.rev.txt) && !temSelo(c.ordens[id]).length && !ABERTAS(c.ordens[id]).length
     && IT(c, c.ordens[id].req, '2,4-D 806').consumido === 0 && r4.msg === 'Divergência de consumo/dose do dia 1 da OS-0430 aceita por Ana (agrônoma): Mistura sem 2,4-D por deriva no vizinho; controle conferido em campo. O consumo informado fica como está.',
     [r4, ap2.rev, c.ordens[id].selos]);
  // repetição (mesmo conteúdo) não grava de novo; outro conteúdo é conflito
  const depois = JSON.stringify(c);
  const r5 = REVER(c, id, 1, 'aceitar', 'Mistura sem 2,4-D por deriva no vizinho; controle conferido em campo', 'Ana');
  const r6 = REVER(c, id, 1, 'corrigir', 'Reaplicar', 'Ana');
  ok('D05e repetir a mesma revisão não grava de novo; outra decisão no mesmo dia é conflito, nada muda',
     !r5.erro && r5.repetido && /já revisada/.test(r5.msg) && /conflito/.test(r6.erro || '') && JSON.stringify(c) === depois, [r5, r6]); }

// ---- D06 · registrar correção/reaplicação decidida pelo agrônomo ----
{ const { c, id } = prep(); TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 0, 'Óleo mineral': 0 }, '', []));
  const r0 = REVER(c, id, 1, 'corrigir', '', 'Ana');
  const r = REVER(c, id, 1, 'corrigir', 'Reaplicar 2,4-D 806 1 L/ha e Óleo mineral 0,5 L/ha nos 10 ha em nova O.S.', 'Ana'); const ap = c.ordens[id].ap.find(a => a.dia === 1) || {};
  ok('D06 correção sem texto é recusada; com o texto, gravada como "Correção decidida" por Ana e o selo sai',
     r0.erro === 'Descreva a correção ou reaplicação decidida para o dia 1 da OS-0430. Nada foi alterado.' && !r.erro && ap.rev && ap.rev.dec === 'Correção decidida' && !temSelo(c.ordens[id]).length
     && r.msg === 'Correção registrada por Ana (agrônoma) para o dia 1 da OS-0430: Reaplicar 2,4-D 806 1 L/ha e Óleo mineral 0,5 L/ha nos 10 ha em nova O.S. O consumo informado fica como está.'
     && !/sai em nova ordem/.test(r.msg),   /* revisão DOM achado 5: nada cria a ordem sozinho; a mensagem não promete */
     [r0, r, ap.rev]); }

// ---- D07 · encerramento final exige a revisão resolvida (conferência, painel e Kanban leem o mesmo estado) ----
{ const { c, id, rid } = prep();
  // 160 ha num turno com 2,4-D abaixo do planejado (100 L × 160 L); o resto conforme; sobra devolvida
  TRY(() => cenFecharTurno(c, 160, 8, { 'Glifosato 480': 320, '2,4-D 806': 100, 'Óleo mineral': 80 }, '', []));
  const dv = IT(c, rid, '2,4-D 806').custodia; MUD(c, x => cenDevolver(x, rid, '2,4-D 806', dv, true, 'Rui'));
  const cf = MUD(c, x => osc_conferencia(x, id));
  const o = c.ordens[id]; const pe = cenPodeEncerrar(c, id);
  ok('D07a enviada para conferência, o selo continua e o encerramento diz a divergência e quem revisa',
     !cf.erro && o.etapa === 'Em conferência' && temSelo(o).length === 1 && temSelo(o)[0].t === SELO + ' · 2,4-D 806'
     && pe === 'Divergência de consumo/dose em revisão técnica: dia 1 · 2,4-D 806 planejado 160 L × informado 100 L. Ana (agrônoma) aceita com motivo ou registra a correção na linha do apontamento.',
     [cf, o.etapa, o.selos, pe]);
  const en = MUD(c, x => osc_encerrar(x, id));
  ok('D07b encerrar é recusado e nada muda', /^Encerrar bloqueado: Divergência de consumo\/dose em revisão técnica/.test(en.erro || '') && c.ordens[id].etapa === 'Em conferência', en);
  const OS0 = (OSD.ords || []).find(b => b.id === id); const m = osMerge(Object.assign(cenClone(OS0), { selos: [] }), c.ordens[id], c); const pb = osProx(m, g2pf('Ana'));
  ok('D07c O.S./Kanban (osMerge): selo, dono Ana (agrônoma) e próximo passo bloqueado com quem resolve; sem "Sobras a receber"',
     m.selos.some(s => s.t === SELO + ' · 2,4-D 806' && s.c === 'red') && !m.selos.some(s => s.t === 'Sobras a receber') && m.dono === 'Ana (agrônoma)' && m.prazo === 'revisar a divergência de dose'
     && pb.b && pb.b.t === 'Encerrar bloqueado: divergência de consumo/dose em revisão técnica · dia 1 · 2,4-D 806 planejado 160 L × informado 100 L.'
     && pb.b.q === 'Ana (agrônoma), na linha do apontamento: aceita com motivo ou registra a correção ou reaplicação.', [m.selos, m.dono, m.prazo, pb.b]);
  const rv = REVER(c, id, 1, 'aceitar', 'Subdose de 2,4-D compensada pelo glifosato; sem rebrote na vistoria', 'Ana');
  // CONTROLE-02: revisão agronômica não substitui conferência diária por Paula.
  const diario=MUD(c,x=>cdConferir(x,id,1,'conferir','Execução e evidência técnica conferidas',cdReferencia(x,id,1),'Paula'));
  const en2 = MUD(c, x => osc_encerrar(x, id));
  ok('D07d revisada, o encerramento passa e o apontamento fica Conferido com a revisão', !rv.erro && !diario.erro && !en2.erro && c.ordens[id].etapa === 'Encerradas'
     && c.ordens[id].ap.find(a => a.dia === 1).st === 'Conferido' && c.ordens[id].ap.find(a => a.dia === 1).rev.dec === 'Aceita', [rv, en2, c.ordens[id].etapa]); }

// ---- D08 · sem sinal: a divergência fica no apontamento do aparelho; selo e revisão só quando chega ao servidor, uma vez ----
{ const { c, id, o } = prep(); cenSinal(c, false);
  TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 0, 'Óleo mineral': 5 }, '', []));
  const s0 = [temSelo(o).length, ABERTAS(o).length, ((o.ap.slice(-1)[0] || {}).div || []).length];
  cenSinal(c, true); cenSinal(c, true);
  const s1 = [temSelo(o).length, ABERTAS(o).length, (temSelo(o)[0] || {}).t];
  ok('D08 sem sinal: divergência gravada no apontamento, sem selo; ao voltar o sinal (dois envios) o selo e a revisão aparecem uma vez',
     s0.join() === '0,0,1' && s1[0] === 1 && s1[1] === 1 && s1[2] === SELO + ' · 2,4-D 806', [s0, s1]); }

// ---- D09 · apontamento pela web (O.S. e Mapa): o mesmo comando, a mesma regra ----
{ const { c, id, o } = prep(); c.app.turno = null;
  const r = TRY(() => osc_apontar(c, id, '26/09', 10, { 'Glifosato 480': 20, '2,4-D 806': 12, 'Óleo mineral': 5 }, [], 'W-OS-0430-teste'));
  const ap = o.ap.filter(a => a.st !== 'Previsto').slice(-1)[0] || {};
  ok('D09 web: 2,4-D 12 L contra 10 L planejado abre a divergência (superdose) e a mensagem diz quem revisa',
     !r.erro && (ap.div || []).length === 1 && ap.div[0].p === '2,4-D 806' && ap.div[0].plan === 10 && ap.div[0].inf === 12 && temSelo(o).length === 1
     && /Divergência de consumo\/dose: 2,4-D 806 planejado 10 L × informado 12 L · revisão técnica de Ana \(agrônoma\)\.$/.test(r.r.msg), [r, ap.div]); }

// ---- D10 · duplicidade retida não abre revisão até a decisão de quem confere; somada, abre ----
{ const { c, id, o } = prep(); c.app.turno = null;
  TRY(() => osc_apontar(c, id, '26/09', 10, { 'Glifosato 480': 20, '2,4-D 806': 10, 'Óleo mineral': 5 }, [], 'W-A'));
  TRY(() => cenIniciarTurno(c, id)); c.app.operador = 'Marcos';
  const f = TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 0, 'Óleo mineral': 5 }, '', []));
  const dup = o.ap.find(a => a.st === CEN_AP_DUP);
  const s0 = [!!dup, temSelo(o).length];
  const d = MUD(c, x => cenApDecidir(x, id, dup ? dup.dia : 0, 'somar', 'Paula'));
  const o2 = c.ordens[id];
  ok('D10 duplicidade retida: sem selo; somada como outro turno por Paula, a divergência do turno abre a revisão',
     s0.join() === 'true,0' && !d.erro && temSelo(o2).length === 1 && ABERTAS(o2).length === 1, [f, s0, d, o2.selos]); }

// ---- D11 · revisão DOM achado 1: produto da ordem fora da requisição — nada esteve com o operador, o 0 é fato e diverge do planejado ----
{ const c = cenClone(CEN0), id = 'OS-0421'; const o = c.ordens[id]; const r = c.reqs[o.req]; r.itens.forEach(i => { i.confirmado = true; }); TRY(() => cenIniciarTurno(c, id));
  const sug = cenQtdTrecho(0.5, o.realizado, 10); const cust0 = r.itens.map(i => i.custodia).join();
  const ret = TRY(() => cenFecharTurno(c, 10, 1, { 'Fungicida A': sug, 'Adjuvante espalhante': 0 }, '', ['Fungicida A', 'Adjuvante espalhante']));   // MB-03 sem editar nada
  const ap = o.ap.filter(a => a.st !== 'Previsto' && a.dia === Math.max.apply(null, o.ap.filter(x => x.st !== 'Previsto').map(x => x.dia)))[0] || {};
  ok('D11a app (OS-0421, campo do Adjuvante sem edição): selo "Divergência de consumo/dose · Adjuvante espalhante", planejado 2,5 L × informado 0 L, revisão de Ana; a sugestão do Fungicida não diverge',
     !ret.erro && temSelo(o).length === 1 && temSelo(o)[0].t === SELO + ' · Adjuvante espalhante' && (ap.div || []).length === 1 && ap.div[0].p === 'Adjuvante espalhante' && ap.div[0].plan === 2.5 && ap.div[0].inf === 0 && ap.div[0].un === 'L'
     && /Adjuvante espalhante planejado 2,5 L × informado 0 L · revisão técnica de Ana \(agrônoma\)\.$/.test(ret.r.msg), [ret, ap.div, o.selos]);
  ok('D11b a baixa não muda: só o Fungicida sai da custódia, sem conferência nem linha 0 do Adjuvante',
     !(c.confs || []).some(k => k.os === id) && JSON.stringify(ap.cons) === JSON.stringify({ 'Fungicida A': sug }) && r.itens[0].custodia === Number(cust0) - sug, [ap.cons, c.confs, cust0, r.itens]);
  // web (O.S. e Mapa): o mesmo formulário (osApIns/osApColeta) sem editar nada → o mesmo fato
  const c2 = cenClone(CEN0); c2.reqs[c2.ordens[id].req].itens.forEach(i => { i.confirmado = true; }); const o2 = c2.ordens[id];
  const k = osApColeta(osApIns(c2, o2, 10, {})); const w = TRY(() => osc_apontar(c2, id, '26/09', 10, k.cons, k.est, 'W-D11'));
  const apw = o2.ap.find(a => a.chave === 'W-D11') || {};
  ok('D11c web (formulário sem edição): a mesma divergência do Adjuvante e a mensagem diz quem revisa',
     !w.erro && (apw.div || []).map(d => d.p + ':' + d.plan + '>' + d.inf).join() === 'Adjuvante espalhante:2.5>0' && /revisão técnica de Ana \(agrônoma\)\.$/.test(w.r.msg), [k, w, apw.div]); }

// ---- D12 · revisão DOM achado 4: relato recusado no Estoque — a divergência passa a planejado × baixado (0) e a revisão já feita é reaberta ----
function prep150() { const P = prep(); TRY(() => cenFecharTurno(P.c, 150, 8, { 'Glifosato 480': 300, '2,4-D 806': 150, 'Óleo mineral': 75 }, '', [])); cenIniciarTurno(P.c, P.id); return P; }
{ const { c, id, o } = prep150();
  TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 15, 'Óleo mineral': 5 }, '', []));
  const cc = (c.confs || []).find(k => k.os === id && k.dia === 2) || {}; const d0 = JSON.stringify((o.ap.find(a => a.dia === 2) || {}).div);
  const rc = MUD(c, x => cenConciliar(x, cc.id, false, 'digitação errada: usou 10 L, a sobra está no tanque', 'Rui')); const ap = c.ordens[id].ap.find(a => a.dia === 2) || {}; const dv = (ap.div || [])[0] || {};
  ok('D12a recusado o relato de 15 L (CC-301): a divergência do dia 2 vira "2,4-D 806 planejado 10 L × baixado 0 L (informado 15 L, relato CC-301 recusado no Estoque)", selo e revisão seguem',
     d0 === '[{"p":"2,4-D 806","un":"L","plan":10,"inf":15}]' && !rc.erro && (ap.div || []).length === 1 && dv.plan === 10 && dv.inf === 0 && dv.rec && dv.rec.rel === 15
     && cenDivTxt(dv) === '2,4-D 806 planejado 10 L × baixado 0 L (informado 15 L, relato CC-301 recusado no Estoque)' && temSelo(c.ordens[id]).length === 1 && ABERTAS(c.ordens[id]).length === 1
     && /Divergência de consumo\/dose do dia 2 da OS-0430: 2,4-D 806 planejado 10 L × baixado 0 L .* · revisão técnica de Ana \(agrônoma\)\.$/.test(rc.msg), [d0, rc, ap.div]); }
{ const { c, id } = prep150();
  TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 15, 'Óleo mineral': 5 }, '', []));
  const rv = REVER(c, id, 2, 'aceitar', 'Superdose de 2,4-D aceita: sem fitotoxidez na vistoria', 'Ana'); const s1 = temSelo(c.ordens[id]).length;
  const cc = (c.confs || []).find(k => k.os === id && k.dia === 2) || {}; const rc = MUD(c, x => cenConciliar(x, cc.id, false, 'digitação errada', 'Rui'));
  const ap = c.ordens[id].ap.find(a => a.dia === 2) || {};
  ok('D12b revisada sobre os 15 L e depois recusado o relato: a revisão anterior vai para o histórico (reaberta, com quem recusou) e a do dia volta a pendente',
     !rv.erro && s1 === 0 && !rc.erro && !ap.rev && (ap.revAnt || []).length === 1 && ap.revAnt[0].dec === 'Aceita' && /relato CC-301 recusado no Estoque por Rui \(almoxarife\)/.test(ap.revAnt[0].reaberta)
     && ABERTAS(c.ordens[id]).length === 1 && temSelo(c.ordens[id]).length === 1 && /A revisão anterior fica no histórico e a do dia é reaberta\.$/.test(rc.msg), [rv, rc, ap.rev, ap.revAnt]);
  const OS0 = (OSD.ords || []).find(b => b.id === id); const m = osMerge(Object.assign(cenClone(OS0), { selos: [], orig: [] }), c.ordens[id], c);
  ok('D12c a Origem da O.S. guarda a revisão reaberta', (m.orig || []).some(t => /Dia 2 · Divergência de consumo\/dose aceita por Ana \(agrônoma\).*reaberta: relato CC-301 recusado no Estoque/.test(t)), m.orig); }
{ const { c, id, rid } = prep150(); MUD(c, x => cenDevolver(x, rid, '2,4-D 806', 5, true, 'Rui'));   // custódia de 2,4-D: 5 L
  TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 10, 'Óleo mineral': 5 }, '', []));   // informado = planejado, acima da custódia
  const ap0 = c.ordens[id].ap.find(a => a.dia === 2) || {}; const s0 = [(ap0.div || []).length, temSelo(c.ordens[id]).length];
  const cc = (c.confs || []).find(k => k.os === id && k.dia === 2) || {}; const rc = MUD(c, x => cenConciliar(x, cc.id, false, 'não usou', 'Rui'));
  const ap = c.ordens[id].ap.find(a => a.dia === 2) || {};
  ok('D12d informado igual ao planejado mas acima da custódia: sem divergência; recusado o relato, nada foi baixado e a divergência abre (planejado 10 L × baixado 0 L)',
     s0.join() === '0,0' && !rc.erro && (ap.div || []).length === 1 && ap.div[0].plan === 10 && ap.div[0].inf === 0 && temSelo(c.ordens[id]).length === 1, [s0, rc, ap.div]); }
{ const { c, id, o } = prep150();
  TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 15, 'Óleo mineral': 5 }, '', []));
  const cc = (c.confs || []).find(k => k.os === id && k.dia === 2) || {}; const a = MUD(c, x => cenConciliar(x, cc.id, true, '', 'Ana'));
  ok('D12e aceito o relato (baixa os 15 L): a divergência continua a do informado', !a.erro && JSON.stringify(c.ordens[id].ap.find(x => x.dia === 2).div) === '[{"p":"2,4-D 806","un":"L","plan":10,"inf":15}]', [a, c.ordens[id].ap.find(x => x.dia === 2).div]); }

// ---- D13 · revisão DOM achado 8 (mutante B7): produto fora da ordem informado sai com unidade ----
{ const { c, o } = prep(); const ret = TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 10, 'Óleo mineral': 5, 'Adjuvante espalhante': 5 }, '', []));
  const ap = o.ap.filter(a => a.st !== 'Previsto').slice(-1)[0] || {};
  ok('D13 produto fora da ordem (Adjuvante 5 L): divergência planejado 0 L × informado 5 L, com unidade',
     !ret.erro && (ap.div || []).length === 1 && ap.div[0].un === 'L' && cenDivTxt(ap.div[0]) === 'Adjuvante espalhante planejado 0 L × informado 5 L', [ret, ap.div]); }

// ---- D14 · mutante B6: na decisão da duplicidade, o usado informado vira fato e a divergência é recalculada ----
{ const { c, id, o, rid } = prep(); c.app.turno = null;
  TRY(() => osc_apontar(c, id, '26/09', 150, { 'Glifosato 480': 300, '2,4-D 806': 150, 'Óleo mineral': 75 }, [], 'W-A')); TRY(() => cenIniciarTurno(c, id));
  TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 10, 'Óleo mineral': 5 }, '', ['Glifosato 480', '2,4-D 806', 'Óleo mineral']));
  const dup = o.ap.find(a => a.st === CEN_AP_DUP); const s0 = dup ? (dup.div || []).length : -1;
  MUD(c, x => cenDevolver(x, rid, '2,4-D 806', 5, true, 'Rui'));
  const d = MUD(c, x => cenApDecidir(x, id, dup ? dup.dia : 0, 'somar', 'Paula', { '2,4-D 806': 5 })); const ap = c.ordens[id].ap.find(a => a.dia === (dup || {}).dia) || {};
  ok('D14 sugestão retida sem divergência; somada por Paula com o usado de 2,4-D 5 L (planejado 10 L), a divergência abre', s0 === 0 && !d.erro && (ap.div || []).length === 1 && ap.div[0].plan === 10 && ap.div[0].inf === 5 && temSelo(c.ordens[id]).length === 1, [s0, d, ap.div]); }

// ---- D15 · mutante B11: o planejado do trecho desconta a área ainda no aparelho (mesma base da sugestão) ----
{ const { c, o } = prep(); cenSinal(c, false); const Q = (d, a) => cenQtdTrecho(d, a, 0.333);
  TRY(() => cenFecharTurno(c, 0.333, 1, { 'Glifosato 480': Q(2, 0), '2,4-D 806': Q(1, 0), 'Óleo mineral': Q(0.5, 0) }, '', [])); cenIniciarTurno(c, 'OS-0430');
  TRY(() => cenFecharTurno(c, 0.333, 1, { 'Glifosato 480': Q(2, 0.333), '2,4-D 806': Q(1, 0.333), 'Óleo mineral': Q(0.5, 0.333) }, '', []));
  const aps = o.ap.filter(a => a.st !== 'Previsto');
  ok('D15 dois turnos de 0,333 ha sem sinal, cada um com o trecho exato (Óleo 0,17 e 0,16 L): nenhuma divergência; base do 2º = 0,333 ha no aparelho',
     aps.length === 2 && aps.every(a => !(a.div || []).length) && aps[1].ant === 0.333 && Q(0.5, 0) !== Q(0.5, 0.333), aps.map(a => [a.dia, a.ant, a.div])); }

// ---- D16 · mutante B12: em execução, a O.S. com revisão aberta tem dona Ana (lista e Kanban) ----
{ const { c, id } = prep(); TRY(() => cenFecharTurno(c, 10, 1, { 'Glifosato 480': 20, '2,4-D 806': 0, 'Óleo mineral': 5 }, '', []));
  const OS0 = (OSD.ords || []).find(b => b.id === id); const m = osMerge(Object.assign(cenClone(OS0), { selos: [] }), c.ordens[id], c);
  ok('D16 Em execução: selo, dona Ana (agrônoma) e próxima ação "revisar a divergência de dose do dia 1"',
     m.etapa === 'Em execução' && m.selos.some(s => s.t === SELO + ' · 2,4-D 806') && m.dono === 'Ana (agrônoma)' && m.prazo === 'revisar a divergência de dose do dia 1', [m.etapa, m.selos, m.dono, m.prazo]); }

console.log(JSON.stringify(R));
