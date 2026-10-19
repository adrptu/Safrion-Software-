// MA-VINCULO (16/10/2026) · regras do vínculo ativo × plano sem navegador (ma_vinculo_test.py parte U monta: perfis do g2lib + dados_manutencao + este arquivo).
// Cada caso parte do seed (MAN0). Saída: uma linha JSON por execução. Inclui as contraprovas da revisão do Codex 6226249749.
// 19/10/2026 · LEVE-1 (leve, proprietário 19/10: "leve e fluido"): motivo opcional em desvincular, fechar achado sem serviço, cancelar OM e resposta fora de OK do checklist; quem e quando continuam gravados. V4 (sem escolha conta de agora) e V6 (desvincular sem motivo grava quem e quando) trocam o oráculo antigo.
const R = []; const ok = (n, cond, info) => R.push({ n, ok: !!cond, info: cond ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 600) });
const caso = (n, fn) => { try { fn(); } catch (e) { R.push({ n: n + ' (exceção)', ok: false, info: String(e && e.stack || e).slice(0, 600) }); } };
const S = () => manClone(MAN0);
const OT = g2pf('Otávio'), ZE = g2pf('Zé'), ANA = g2pf('Ana');
const run = (c, fn) => { const cc = manClone(c); let r; try { r = fn(cc) || {}; } catch (e) { r = { erro: String(e.message || e) }; } if (!r.erro && !r.nada) Object.assign(c, cc); return r; };
const nomes = (xs) => xs.map(a => a.nome);
const sitDe = (c, pid, aid, sid) => { const l = manLinhas(c, pid).find(x => x.aid === aid && x.sid === (sid || 's1')); return l ? l.x : null; };
// plano de teste no estado (o seed não tem 3 ativos sem plano no mesmo grupo): rascunho ou publicado, com um serviço
const plano = (c, id, o) => { c.planos[id] = { id, nome: o.nome || id, grupo: o.grupo, aplica: o.aplica, estado: 'Ativo', versao: o.versao === undefined ? 1 : o.versao, rasc: null, hist: [],
  servicos: [{ id: 's1', nome: o.serv || 'Lubrificação semanal', gat: o.gat || { d: 7 }, tol: o.tol || {}, base: 'exec', cumpre: [], tempo: 1, esp: 'Lubrificador', tarefas: [{ t: 'Lubrificar', tipo: 'Serviço' }], pecas: [] }] };
  if (c.ordemPlanos.indexOf(id) < 0) c.ordemPlanos.push(id); return c.planos[id]; };

caso('V1 sem plano e sugestão', () => {
  const c = S();
  ok('V1 · "Sem plano" no seed = Distribuidor 3 t, Máquina TSI, Esqueletadeira e Gotejo T7 (ativos em uso sem vínculo em plano ativo e publicado)',
    JSON.stringify(nomes(manSemPlano(c))) === JSON.stringify(['Distribuidor 3 t', 'Máquina TSI', 'Esqueletadeira', 'Gotejo T7']), nomes(manSemPlano(c)));
  const s12 = manVincSug(c, c.ativos.a12), s09 = manVincSug(c, c.ativos.a09);
  ok('V1 · sugestão: Gotejo T7 → PM-07 (mesma classe, Irrigação); Máquina TSI → PM-08 (mesmo grupo, Beneficiamento); Distribuidor e Esqueletadeira sem plano compatível',
    s12.length === 1 && s12[0].p.id === 'PM-07' && s12[0].cp.nivel === 'classe' && s09.length === 1 && s09[0].p.id === 'PM-08' && s09[0].cp.nivel === 'grupo'
    && !manVincSug(c, c.ativos.a07).length && !manVincSug(c, c.ativos.a10).length, [s12.map(x => [x.p.id, x.cp.nivel]), s09.map(x => [x.p.id, x.cp.nivel])]);
  ok('V1 · sugestão é opção, não vínculo: nada mudou no estado', JSON.stringify(c.vinc) === JSON.stringify(MAN0.vinc) && JSON.stringify(c.planos) === JSON.stringify(MAN0.planos));
});

caso('V2 compatibilidade', () => {
  const c = S();
  const g = manVincCompat(c, c.planos['PM-04'], c.ativos.a02);
  ok('V2 · plano de pulverizador num trator é recusado com o motivo (gera ordem e peças erradas)', /PM-04 é de Pulverizadores e Trator 02 é de Tratores/.test(g.erro), g);
  const m = manVincCompat(c, c.planos['PM-07'], c.ativos.a12);
  ok('V2 · modelo diferente no mesmo grupo é aviso e permite', !m.erro && /Modelo diferente: cabeçal \+ injetora de fertilizante/.test(m.avisos[0] || ''), m);
  const d = manVincCompat(c, c.planos['PM-01'], c.ativos.a03);
  ok('V2 · o mesmo serviço por dois planos é recusado (Revisão 250 h pelo PM-02)', /já faz Revisão 250 h pelo PM-02/.test(d.erro), d);
  plano(c, 'PM-11', { grupo: 'Irrigação', aplica: { t: 'ativos', v: [] }, serv: 'Revisão 1.000 km', gat: { km: 1000 } });
  const u = manVincCompat(c, c.planos['PM-11'], c.ativos.a12);
  plano(c, 'PM-12', { grupo: 'Irrigação', aplica: { t: 'ativos', v: [] }, serv: 'Revisão 1.000 km ou 30 dias', gat: { km: 1000, d: 30 } });
  const u2 = manVincCompat(c, c.planos['PM-12'], c.ativos.a12);
  ok('V2 · gatilho só por km num ativo com horímetro: recusado com o motivo (nunca "Sem gatilho" calado)', /conta só por 1.000 km e Gotejo T7 conta horas \(horímetro\): nenhum gatilho se aplica/.test(u.erro), u);
  ok('V2 · km + dias num ativo com horímetro: aviso dizendo que só os dias contam', !u2.erro && u2.avisos.some(x => /o gatilho de 1.000 km não vale .* vence só a cada 30 dias/.test(x)), u2);
  c.ativos.a10.sit = 'Inativo';
  ok('V2 · ativo inativo não é candidato nem "Sem plano"', /está inativo: não recebe plano/.test(manVincCompat(c, c.planos['PM-07'], c.ativos.a10).erro) && !nomes(manSemPlano(c)).includes('Esqueletadeira') && !manVincSug(c, c.ativos.a10).length);
});

caso('V3 contraprova 1.000 h × 1.450 h (revisão Codex 6226249749)', () => {
  const c = S(); const a = c.ativos.a07; a.leit = { val: 1450, data: c.hoje, origem: 'teste' }; a.ritmo = 10;
  plano(c, 'PM-11', { grupo: 'Implementos', aplica: { t: 'ativos', v: ['a07'] }, serv: 'Revisão 250 h', gat: { h: 250 }, tol: { h: 25 } });
  c.vinc['PM-11|a07'] = { marco: { data: '2026-01-10', leit: 600, om: null }, ult: { s1: { data: '2026-07-01', leit: 1000, om: 'OM-0900' } } };
  const x0 = sitDe(c, 'PM-11', 'a07'); const v0 = JSON.stringify(c.vinc['PM-11|a07']);
  ok('V3 · referência 1.000 h, leitura 1.450 h, intervalo 250 h → Vencida (vence em 1.250 h)', x0.sit === 'Vencida' && x0.gats[0].due === 1250, x0);
  const r1 = run(c, x => manVincular(x, 'PM-11', [{ aid: 'a07', base: { modo: 'agora' } }], OT, 'kv3a'));
  ok('V3 · vincular de novo (já vinculado) não muda nada: segue Vencida, marco e última execução intactos', r1.nada && sitDe(c, 'PM-11', 'a07').sit === 'Vencida' && JSON.stringify(c.vinc['PM-11|a07']) === v0, [r1, c.vinc['PM-11|a07']]);
  const r2 = run(c, x => manDesvincular(x, 'PM-11', 'a07', 'teste de revínculo', OT, 'kv3b'));
  ok('V3 · desvincular guarda o vínculo com fim (marco e última execução intactos) e tira o ativo dos vencimentos',
    !r2.erro && !!c.vinc['PM-11|a07'].fim && JSON.stringify(c.vinc['PM-11|a07'].ult) === JSON.stringify(JSON.parse(v0).ult) && !sitDe(c, 'PM-11', 'a07') && nomes(manSemPlano(c)).includes('Distribuidor 3 t'), [r2, c.vinc['PM-11|a07']]);
  ok('V3 · revínculo mostra a base de antes ("hist"), não a leitura atual', manVincBase(c, c.planos['PM-11'], a).modo === 'hist');
  const r3 = run(c, x => manVincular(x, 'PM-11', [{ aid: 'a07', base: { modo: 'agora' } }], OT, 'kv3c'));
  const x3 = sitDe(c, 'PM-11', 'a07');
  ok('V3 · revincular retoma a contagem: continua Vencida em 1.250 h; marco e última execução iguais aos de antes; histórico do período guardado',
    !r3.erro && x3 && x3.sit === 'Vencida' && x3.gats[0].due === 1250 && JSON.stringify(c.vinc['PM-11|a07'].marco) === JSON.stringify(JSON.parse(v0).marco)
    && JSON.stringify(c.vinc['PM-11|a07'].ult) === JSON.stringify(JSON.parse(v0).ult) && !c.vinc['PM-11|a07'].fim && c.vinc['PM-11|a07'].hist.length === 1, [r3, x3, c.vinc['PM-11|a07']]);
  // contraprova da regra: a leitura atual como referência esconderia o atraso (por isso nunca é automática)
  const esc = manVenc(c, c.planos['PM-11'].servicos[0], a, { data: c.hoje, leit: 1450 });
  ok('V3 · contraprova: com a leitura atual (1.450 h) como referência a mesma conta daria Em dia (vence em 1.700 h)', esc.sit === 'Em dia' && esc.gats[0].due === 1700, esc);
});

caso('V4 base de contagem e prévia', () => {
  const c = S(); const p = c.planos['PM-07'], a = c.ativos.a12;
  /* LEVE-1 (leve, proprietário 19/10): sem escolha, conta de agora (marco estimado, com selo); antes recusava "Escolha como contar" */
  const sx = manVincRef(c, p, a, {});
  ok('V4 · sem execução registrada e sem escolha: conta de agora (hoje e leitura atual 5.210 h, marco estimado), sem erro (LEVE-1)', manVincBase(c, p, a).modo === '' && !Object.keys(sx.errs).length && sx.ref && sx.ref.data === c.hoje && sx.ref.leit === 5210 && sx.ref.est === true, sx);
  const ag = manVincRef(c, p, a, { modo: 'agora' });
  ok('V4 · contar de agora: hoje e a leitura atual do próprio ativo (5.210 h), marcado como estimado', ag.ref && ag.ref.data === c.hoje && ag.ref.leit === 5210 && ag.ref.est === true, ag);
  const pv = manVincPrev(c, p, a, { marco: ag.ref, ult: {} });
  const r = run(c, x => manVincular(x, 'PM-07', [{ aid: 'a12', base: { modo: 'agora' } }], OT, 'kv4'));
  const l = manLinhas(c, 'PM-07').find(x => x.aid === 'a12' && x.sid === 's1');
  ok('V4 · prévia igual ao vencimento gravado (mesma conta: manRef + manVenc + manProxTxt)', !r.erro && l && pv[0].prox === manProxTxt(c, l.x) && pv[0].sit === l.x.sit && pv[0].de === '23/09 · 5.210 h', [pv[0], l && manProxTxt(c, l.x), r]);
  ok('V4 · vincular inclui o ativo em "Aplica a" (ativos escolhidos) e tira de "Sem plano"', c.planos['PM-07'].aplica.v.indexOf('a12') >= 0 && !nomes(manSemPlano(c)).includes('Gotejo T7') && /Ativos escolhidos \(3\)/.test(manAplTxt(c, c.planos['PM-07'])));
  // informar a última execução: data futura, leitura negativa ou maior que a atual são recusadas
  const c2 = S(); const p2 = c2.planos['PM-07'];
  const f = manVincRef(c2, p2, a, { modo: 'ult', data: '2026-12-01', leit: '100' }), n = manVincRef(c2, p2, a, { modo: 'ult', data: '2026-09-01', leit: '-5' }), m = manVincRef(c2, p2, a, { modo: 'ult', data: '2026-09-01', leit: '9.000' });
  const u = manVincRef(c2, p2, a, { modo: 'ult', data: '2026-09-01', leit: '5.100' });
  ok('V4 · última execução: data futura, leitura negativa e maior que a atual recusadas; 5.100 h em 01/09 aceita', /futura/.test(f.errs.data) && n.errs.leit === 'Zero ou mais.' && /Maior que a leitura atual/.test(m.errs.leit) && u.ref && u.ref.leit === 5100 && u.ref.est === false, [f.errs, n.errs, m.errs, u]);
  // contador ausente não vira zero
  const c3 = S(); plano(c3, 'PM-11', { grupo: 'Armazenagem', aplica: { t: 'ativos', v: [] }, gat: { d: 30 } });
  const s14 = manVincRef(c3, c3.planos['PM-11'], c3.ativos.a14, { modo: 'agora' });
  c3.ativos.a12.leit = null; const sl = manVincRef(c3, c3.planos['PM-07'], c3.ativos.a12, { modo: 'agora' });
  ok('V4 · ativo sem contador: a base fica sem leitura (nunca 0); ativo com horímetro sem leitura não "conta de agora"', s14.ref && s14.ref.leit === null && /não tem leitura registrada/.test(sl.errs.leit || ''), [s14, sl.errs]);
  // OM encerrada do mesmo serviço: base proposta, corrigível só com motivo
  const c4 = S(); delete c4.vinc['PM-03|a04']; const b4 = manVincBase(c4, c4.planos['PM-03'], c4.ativos.a04);
  const sm = manVincRef(c4, c4.planos['PM-03'], c4.ativos.a04, { corr: true, data: '2026-06-02', leit: '3300' }), cm = manVincRef(c4, c4.planos['PM-03'], c4.ativos.a04, { corr: true, data: '2026-06-02', leit: '3300', mot: 'horímetro trocado' });
  ok('V4 · com OM encerrada do mesmo serviço a base é a dela (OM-0205 · 02/06 · 3.300 h); corrigir pede motivo', b4.modo === 'om' && b4.om === 'OM-0205' && b4.data === '2026-06-02' && b4.leit === 3300 && /motivo da correção \(OM-0205\)/.test(sm.errs.mot || '') && cm.ref && cm.ref.mot === 'horímetro trocado', [b4, sm.errs, cm]);
});

caso('V5 lote, idempotência e permissão', () => {
  const c = S(); const v0 = JSON.stringify(c.vinc), p0 = JSON.stringify(c.planos);
  const r = run(c, x => manVincular(x, 'PM-07', [{ aid: 'a12', base: { modo: 'agora' } }, { aid: 'a02', base: { modo: 'agora' } }], OT, 'kv5a'));
  ok('V5 · lote com um inválido não grava metade (tudo ou nada) e diz o motivo', /^Nada foi vinculado: PM-07 é de Irrigação e Trator 02 é de Tratores/.test(r.erro || '') && JSON.stringify(c.vinc) === v0 && JSON.stringify(c.planos) === p0, r);
  plano(c, 'PM-11', { grupo: 'Tratores', aplica: { t: 'ativos', v: ['a02', 'a03', 'a04'] }, gat: { d: 7, h: 50 } });
  const its = ['a02', 'a03', 'a04'].map(aid => ({ aid, base: { modo: 'agora' } }));
  const r1 = run(c, x => manVincular(x, 'PM-11', its.concat([{ aid: 'a03', base: { modo: 'agora' } }]), OT, 'kv5b')); const v1 = JSON.stringify(c.vinc);
  const r2 = run(c, x => manVincular(x, 'PM-11', its, OT, 'kv5b'));
  const r3 = run(c, x => manVincular(x, 'PM-11', its, OT, 'kv5c'));
  ok('V5 · 3 ativos num lote (o repetido na lista conta uma vez); a mesma chave (duplo clique) não grava de novo; outra chave acha "já vinculados" e nada muda',
    !r1.erro && /^3 ativos vinculados ao PM-11/.test(r1.msg) && r2.nada && r2.repetido && r3.nada && /Já vinculados/.test(r3.msg) && JSON.stringify(c.vinc) === v1
    && ['a02', 'a03', 'a04'].every(a => c.vinc['PM-11|' + a] && c.vinc['PM-11|' + a].marco.est), [r1.msg, r2, r3]);
  ok('V5 · o ativo pode ter mais de um plano: Trator 02 no PM-01 e no PM-11 (nada é colapsado)', JSON.stringify(manPlanosDe(c, 'a02').map(p => p.id)) === JSON.stringify(['PM-01', 'PM-11']));
  let ez = ''; try { manVincular(S(), 'PM-07', [{ aid: 'a12', base: { modo: 'agora' } }], ZE, 'kv5d'); } catch (e) { ez = e.message; }
  let ea = ''; try { manDesvincular(S(), 'PM-01', 'a02', 'x', ANA, 'kv5e'); } catch (e) { ea = e.message; }
  ok('V5 · permissão pela mesma regra do plano (manExige "plano"): Zé e Ana recusados com o motivo', /Ação do Otávio/.test(ez) && /Ação do Otávio/.test(ea), [ez, ea]);
});

caso('V6 desvincular com OM aberta', () => {
  const c = S(); const v0 = JSON.stringify(c.vinc['PM-01|a02']);
  const cs = manClone(c); let em = ''; try { manDesvincular(cs, 'PM-01', 'a02', '  ', OT); } catch (e) { em = e.message; }
  const r = run(c, x => manDesvincular(x, 'PM-01', 'a02', 'Vínculo feito por engano', OT, 'kv6a'));
  /* LEVE-1 (proprietário 19/10): sem motivo também desvincula, com quem e quando */
  ok('V6 · desvincular sem motivo (LEVE-1) grava quem e quando; com motivo, avisa que a OM-0234 continua aberta e não a apaga', em === '' && cs.vinc['PM-01|a02'].fim && cs.vinc['PM-01|a02'].fim.mot === '' && /Otávio/.test(cs.vinc['PM-01|a02'].fim.por)
     && /OM-0234 continua aberta/.test(r.msg || '') && c.oms['OM-0234'] && c.oms['OM-0234'].etapa === 'A liberar', [em, cs.vinc['PM-01|a02'], r]);
  const v = c.vinc['PM-01|a02'];
  ok('V6 · histórico preservado: marco e últimas execuções intactos, fim com quem, quando e motivo', v.fim && v.fim.mot === 'Vínculo feito por engano' && v.fim.em === c.hoje && JSON.stringify(v.marco) === JSON.stringify(JSON.parse(v0).marco) && JSON.stringify(v.ult) === JSON.stringify(JSON.parse(v0).ult), v);
  let eg = ''; try { manGerar(manClone(c), 'PM-01|a02', 's1', OT); } catch (e) { eg = e.message; }
  ok('V6 · vínculo encerrado não gera ordem nem vencimento; o ativo fica "Sem plano"', /Vínculo não encontrado/.test(eg) && !manLinhas(c, 'PM-01').length && nomes(manSemPlano(c)).includes('Trator 02'), eg);
  const r2 = run(c, x => manVincular(x, 'PM-01', [{ aid: 'a02' }], OT, 'kv6b'));
  const l = manLinhas(c, 'PM-01').find(x => x.aid === 'a02' && x.sid === 's1');
  ok('V6 · revincular retoma o mesmo ciclo: a OM-0234 volta a ser a ordem do ciclo (nenhuma duplicada)', !r2.erro && l && l.om && l.om.id === 'OM-0234' && JSON.stringify(c.vinc['PM-01|a02'].ult) === JSON.stringify(JSON.parse(v0).ult), [r2, l && l.om]);
  const r3 = run(c, x => manDesvincular(x, 'PM-01', 'a02', 'motivo', OT, 'kv6b2')); const r4 = run(c, x => manDesvincular(x, 'PM-01', 'a02', 'motivo', OT, 'kv6c'));
  ok('V6 · desvincular de novo não muda nada', !r3.erro && r4.nada, r4);
});

caso('V7 "Aplica a" e situação', () => {
  const c = S(); plano(c, 'PM-11', { grupo: 'Tratores', aplica: { t: 'modelo', v: ['MF 7719'] }, gat: { d: 7 } });
  const r = run(c, x => manVincular(x, 'PM-11', [{ aid: 'a03', base: { modo: 'agora' } }], OT, 'kv7a'));
  ok('V7 · ativo de outro modelo num plano por modelo entra como exceção (aplica.x) e o texto diz isso', !r.erro && JSON.stringify(c.planos['PM-11'].aplica) === JSON.stringify({ t: 'modelo', v: ['MF 7719'], x: ['a03'] })
    && manAplTxt(c, c.planos['PM-11']) === 'Todos do modelo MF 7719 (1 ativo) + 1 ativo de outro modelo', [r, c.planos['PM-11'].aplica, manAplTxt(c, c.planos['PM-11'])]);
  const e1 = manAplicaNova(c, c.planos['PM-11'], { tipo: 'ativos', ativos: [] });
  ok('V7 · trocar para "Ativos escolhidos" sem marcar nada mantém o vinculado e diz o efeito', e1.aplica && JSON.stringify(e1.aplica) === JSON.stringify({ t: 'ativos', v: ['a03'] }) && e1.efeito.some(x => /Trator 03 segue vinculado/.test(x)) && e1.efeito.some(x => /Trator 02 deixa de ser candidato/.test(x)), e1);
  const e2 = manAplicaNova(c, c.planos['PM-11'], { tipo: 'modelo', modelo: 'Uniport 3030' });
  ok('V7 · trocar para um modelo de outro grupo é recusado (um plano, um grupo de máquina)', /um plano serve a um grupo de máquina/.test(e2.erro || ''), e2);
  const s = (pid, aid) => manPlSit(c, c.planos[pid], c.ativos[aid]).t;
  ok('V7 · situação na coluna Plano: Atrasado · Vence em 55 h · Vence em 8 dias · Em dia', s('PM-02', 'a03') === 'Atrasado' && s('PM-01', 'a02') === 'Vence em 55 h' && s('PM-07', 'a11') === 'Vence em 8 dias' && s('PM-03', 'a01') === 'Em dia',
    [s('PM-02', 'a03'), s('PM-01', 'a02'), s('PM-07', 'a11'), s('PM-03', 'a01')]);
  const c2 = S(); plano(c2, 'PM-11', { grupo: 'Implementos', aplica: { t: 'ativos', v: ['a07'] }, versao: 0 });
  run(c2, x => manVincular(x, 'PM-11', [{ aid: 'a07', base: { modo: 'agora' } }], OT, 'kv7b'));
  ok('V7 · vínculo só em rascunho continua "Sem plano" (distinto: a coluna diz Rascunho)', nomes(manSemPlano(c2)).includes('Distribuidor 3 t') && manPlSit(c2, c2.planos['PM-11'], c2.ativos.a07).t === 'Rascunho');
});

caso('V8 serviços publicados regem o vínculo (revisão Codex 6229032017)', () => {
  const rasc = (p, gat) => { p.rasc = { v: (p.versao || 0) + 1, servicos: [Object.assign(manClone(p.servicos[0]), { gat, tol: {} })] }; return p; };
  // 1 · publicado só por km + rascunho por dias, ativo por horímetro
  const c = S(); const p = rasc(plano(c, 'PM-11', { grupo: 'Implementos', aplica: { t: 'ativos', v: [] }, serv: 'Revisão', gat: { km: 1000 } }), { d: 30 });
  const k1 = manVincCompat(c, p, c.ativos.a07); const r1 = run(c, x => manVincular(x, 'PM-11', [{ aid: 'a07', base: { modo: 'agora' } }], OT, 'kv8a'));
  ok('V8.1 · publicado só por km e rascunho por dias, ativo por horímetro: recusado com o motivo (a v1 em vigor não tem gatilho que o ativo conte)',
    /Revisão conta só por 1\.000 km e Distribuidor 3 t conta horas \(horímetro\): nenhum gatilho se aplica na v1 em vigor/.test(k1.erro) && /^Nada foi vinculado/.test(r1.erro || '')
    && !c.vinc['PM-11|a07'] && nomes(manSemPlano(c)).includes('Distribuidor 3 t'), [k1, r1]);
  p.servicos = p.rasc.servicos; p.rasc = null; p.versao = 2;   // publicação compatível (dias)
  const r1b = run(c, x => manVincular(x, 'PM-11', [{ aid: 'a07', base: { modo: 'agora' } }], OT, 'kv8b')); const l1 = manLinhas(c, 'PM-11').find(x => x.aid === 'a07');
  ok('V8.1 · com a versão compatível publicada (dias), o mesmo vínculo passa e tem vencimento', !r1b.erro && l1 && l1.x.gats.length === 1 && l1.x.gats[0].u === 'd' && l1.x.sit !== 'Sem gatilho', [r1b, l1 && l1.x]);
  // 2 · inverso: publicado por dias + rascunho só por km
  const c2 = S(); const p2 = rasc(plano(c2, 'PM-11', { grupo: 'Implementos', aplica: { t: 'ativos', v: [] }, serv: 'Revisão', gat: { d: 30 } }), { km: 1000 });
  const k2 = manVincCompat(c2, p2, c2.ativos.a07); const r2 = run(c2, x => manVincular(x, 'PM-11', [{ aid: 'a07', base: { modo: 'agora' } }], OT, 'kv8c'));
  const l2 = manLinhas(c2, 'PM-11').find(x => x.aid === 'a07'); const pv2 = c2.vinc['PM-11|a07'] ? manVincPrev(c2, p2, c2.ativos.a07, c2.vinc['PM-11|a07']) : [];
  ok('V8.2 · publicado por dias e rascunho só por km: aceita pelo publicado (com vencimento) e avisa do rascunho',
    !k2.erro && k2.avisos.some(x => /^Rascunho v2 \(ainda não vale\): Revisão conta só por 1\.000 km; se for publicado assim, Distribuidor 3 t fica sem gatilho/.test(x))
    && !r2.erro && l2 && l2.x.gats.length === 1 && pv2[0] && pv2[0].prox !== '—', [k2, r2, l2 && l2.x, pv2]);
  const sg = manPubSemGatilho(c2, p2, manWork(p2));
  ok('V8.2 · com o ativo vinculado, o rascunho só por km não pode ser publicado (o motivo diz quem ficaria sem gatilho)', sg.length === 1 && /^Revisão conta só por 1\.000 km e Distribuidor 3 t conta horas/.test(sg[0]) && !manPubSemGatilho(c2, p2, manPub(p2)).length, sg);
  // 3 · plano ainda não publicado: regem os serviços do rascunho v1 (o que vale ao publicar), como antes, com o motivo à vista
  const c3 = S(); const p3 = plano(c3, 'PM-11', { grupo: 'Implementos', aplica: { t: 'ativos', v: [] }, serv: 'Revisão', gat: { km: 1000 }, versao: 0 }); const k3 = manVincCompat(c3, p3, c3.ativos.a07);
  const c4 = S(); const p4 = plano(c4, 'PM-11', { grupo: 'Implementos', aplica: { t: 'ativos', v: [] }, serv: 'Revisão', gat: { d: 30 }, versao: 0 });
  const r4 = run(c4, x => manVincular(x, 'PM-11', [{ aid: 'a07', base: { modo: 'agora' } }], OT, 'kv8d')); const pv4 = c4.vinc['PM-11|a07'] ? manVincPrev(c4, p4, c4.ativos.a07, c4.vinc['PM-11|a07']) : [];
  ok('V8.3 · sem versão publicada: km recusado com o motivo (rascunho v1 é o que vale ao publicar); dias aceita, a prévia diz que vence só depois de publicar e o ativo segue "Sem plano"',
    /nenhum gatilho se aplica \(rascunho v1: é o que vale ao publicar\)/.test(k3.erro) && !r4.erro && pv4[0] && /Rascunho: os vencimentos começam quando o PM-11 for publicado/.test(pv4[0].txt)
    && nomes(manSemPlano(c4)).includes('Distribuidor 3 t'), [k3, r4, pv4]);
});

print(JSON.stringify(R));
