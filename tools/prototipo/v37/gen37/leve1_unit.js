// LEVE-1 · regras sem navegador (proprietário 19/10: "Não quero um sistema travado e burocrático, quero leve e fluido"; AGENTS §4).
// Executor: leve1_unit_test.py, que monta o JS real das telas em três partes (PARTE = 'os', 'man' ou 'mapa') e roda no node.
// Cada verificação reprova a versão de antes da LEVE-1 (contraprova: o mesmo arquivo sobre a árvore cbe4cd38).
const R = []; function ok(n, c, info) { R.push(!!c); print((c ? 'OK    ' : 'FALHA ') + n + (c ? '' : ' · ' + JSON.stringify(info === undefined ? '' : info).slice(0, 600))); }
const TRY = (f) => { try { return { v: f(), e: '' }; } catch (x) { return { v: null, e: String(x.message || x) }; } };
const HM = (m) => { const d = new Date(Date.now() - m * 60000); return ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2); };
if (PARTE === 'os') {
  // ---------- I2 · horas do turno (cenario.js): agora − início − pausas, 1 casa; virada de dia; pausa aberta; sem início = NaN ----------
  const H = (t, a) => (typeof cenHorasTurno === 'function') ? cenHorasTurno(t, a) : 'sem cenHorasTurno';
  ok('U2a cenHorasTurno: 06:10 → 15:00 com pausa de 20 min = 8,5 h', H({ ini: '06:10', pausas: [{ ini: '10:00', fim: '10:20' }] }, '15:00') === 8.5, H({ ini: '06:10', pausas: [{ ini: '10:00', fim: '10:20' }] }, '15:00'));
  ok('U2b virada de dia: 22:00 → 01:30 = 3,5 h; pausa ainda aberta (14:00) conta até agora: 12:00 → 15:00 = 2 h', H({ ini: '22:00', pausas: [] }, '01:30') === 3.5 && H({ ini: '12:00', pausas: [{ ini: '14:00', fim: null }] }, '15:00') === 2, [H({ ini: '22:00', pausas: [] }, '01:30'), H({ ini: '12:00', pausas: [{ ini: '14:00', fim: null }] }, '15:00')]);
  ok('U2c sem início registrado (ou ilegível): NaN, nada inventado', Number.isNaN(H({ ini: '', pausas: [] }, '15:00')) && Number.isNaN(H({ ini: 'x', pausas: [] }, '15:00')) && Number.isNaN(H(null, '15:00')), [H({ ini: '', pausas: [] }, '15:00')]);
  cenReset(); localStorage.setItem('safrion.perfilDemo', 'Ana');
  cenMudar(null, c => cenIniciarTurno(c, 'OS-0421'));
  const fx = cenMudar(null, c => { c.app.turno.ini = HM(185); c.app.turno.pausas = [{ ini: HM(70), fim: HM(45) }]; return cenFecharTurno(c, 5, undefined, { 'Fungicida A': 2.5 }); });
  ok('U2d cenFecharTurno sem horas: o comando calcula as do turno (2,7 h) e grava o apontamento', /^Turno fechado: 5 ha em 2,7 h/.test(fx.msg || '') && cenGet().ordens['OS-0421'].ap.some(a => a.h === 2.7), fx.erro || fx.msg);
  cenMudar(null, c => cenIniciarTurno(c, 'OS-0421'));
  const fz = cenMudar(null, c => { c.app.turno.ini = ''; return cenFecharTurno(c, 5, undefined, { 'Fungicida A': 2.5 }); });
  const f0 = cenMudar(null, c => { c.app.turno.ini = HM(60); return cenFecharTurno(c, 5, 0, { 'Fungicida A': 2.5 }); });
  ok('U2e sem início, ou com horas 0 informadas, continua pedindo "Informe as horas trabalhadas."', /Informe as horas trabalhadas/.test(fz.erro || '') && /Informe as horas trabalhadas/.test(f0.erro || ''), [fz, f0]);
  // ---------- I1 · Iniciar e Enviar no clique (núcleo da O.S.) ----------
  cenReset(); localStorage.setItem('safrion.perfilDemo', 'Ana');
  cenMudar(null, c => { cenEntregar(c, 'REQ-039', 'Fungicida A', 65, 'Marcos', 'Rui'); return cenConfirmarRecebimento(c, 'REQ-039'); });
  const D = typeof osDireto === 'function';
  const i1 = D ? cenMudar(null, osDireto('OS-0424', 'iniciar', 'Liberadas')) : cenMudar(null, c => osc_iniciar(c, 'OS-0424'));
  ok('U1a Iniciar (osDireto → osc_iniciar): OS-0424 Em execução e o recibo diz com quem estão os insumos', D && cenGet().ordens['OS-0424'].etapa === 'Em execução' && /^OS-0424 em execução: insumos com Marcos, confirmados no app\. Registre o apontamento/.test(i1.msg || ''), [D, i1]);
  const i2 = D ? cenMudar(null, osDireto('OS-0424', 'iniciar', 'Liberadas')) : { erro: 'sem osDireto' };
  ok('U1b toque duplo: a 2ª chamada do mesmo clique não faz nada de novo e não vira erro', !i2.erro && /já está em Em execução: nada foi feito de novo/.test(i2.msg || ''), i2);
  cenMudar(null, c => { const o = c.ordens['OS-0424']; o.realizado = o.area; o.saldo = 0; return { msg: '' }; });
  const e1 = D ? cenMudar(null, osDireto('OS-0424', 'conferencia', 'Em execução')) : { erro: 'sem osDireto' };
  const e2 = D ? cenMudar(null, osDireto('OS-0424', 'conferencia', 'Em execução')) : { erro: 'sem osDireto' };
  const fim = ((cenGet().ordens['OS-0424'].osc || {}).fim || []).filter(x => x.cmd === 'CMD-08');
  ok('U1c Enviar para conferência no clique grava CMD-08 com quem e quando uma vez; o toque duplo não grava de novo', /OS-0424 enviada para conferência por Ana/.test(e1.msg || '') && /já está em Em conferência/.test(e2.msg || '') && fim.length === 1 && !!fim[0].at, [e1, e2, fim]);
  cenReset(); const c0 = cenClone(cenGet()); const ix = TRY(() => (D ? osDireto('OS-0424', 'iniciar', 'Liberadas') : (c => osc_iniciar(c, 'OS-0424')))(c0));
  ok('U1d o comando continua validando: OS-0424 liberada sem o insumo entregue e confirmado não inicia ("Iniciar bloqueado") e nada muda', /Iniciar bloqueado/.test(ix.e) && c0.ordens['OS-0424'].etapa === 'Liberadas', [ix, c0.ordens['OS-0424'].etapa]);
  // ---------- I9 · alçada AL-05 sem motivo (configuracoes.js); o 2º aprovador continua ao ampliar o próprio poder ----------
  cenReset();
  const a1 = cenMudar(null, c => confAlcMudar(c, 'AL-05', { lim: 15 }, '', confChave('t'), 'Ana'));
  ok('U9a AL-05 20 → 15 % sem motivo: vale na hora (v2), o evento grava quem e não tem "motivo:" vazio', !a1.erro && /AL-05 v2 vigente/.test(a1.msg || '') && !/motivo: *$/.test(((cenGet().conf || {}).ev || []).slice(-1).map(e => e.t)[0] || 'x'), [a1, ((cenGet().conf || {}).ev || []).slice(-1)]);
  const a2 = cenMudar(null, c => confAlcMudar(c, 'AL-05', { lim: 30 }, '', confChave('t'), 'Ana'));
  ok('U9b ampliar o próprio poder sem motivo continua aguardando o 2º aprovador (segurança mantida)', !a2.erro && a2.pendente === true && /aguarda confirmação/.test(a2.msg || ''), a2);
}
if (PARTE === 'man') {
  const OT = g2pf('Otávio');
  const run = (c, fn) => { const cc = manClone(c); let r; try { r = fn(cc) || {}; } catch (e) { r = { erro: String(e.message || e) }; } if (!r.erro && !r.nada) Object.assign(c, cc); return r; };
  // ---------- I9 · cancelar OM sem motivo (dados_manutencao.js) ----------
  const c = manClone(MAN0); manGerarTodas(c, null, OT);
  const r = run(c, x => manCancelar(x, 'OM-0234', '', OT, 'T-L1'));
  const o = c.oms['OM-0234'];
  ok('U9c cancelar a OM-0234 sem motivo: Canceladas, quem e quando gravados, motivo vazio e o recibo sem "motivo:"', !r.erro && o.etapa === 'Canceladas' && o.canc.motivo === '' && /Otávio/.test(o.canc.por) && !!o.canc.em && !/motivo:/.test(r.msg || ''), [r, o.canc]);
  // ---------- I5 · vincular sem escolha conta de agora ----------
  const p = c.planos['PM-07'], a = c.ativos.a12; const v = manVincRef(c, p, a, {});
  const rv = run(c, x => manVincular(x, 'PM-07', [{ aid: 'a12', base: {} }], OT, 'T-L2'));
  ok('U5 vincular o Gotejo T7 (sem execução registrada) sem escolher a base: conta de agora, marco estimado (selo)', !rv.erro && c.vinc['PM-07|a12'] && c.vinc['PM-07|a12'].marco.est === true && c.vinc['PM-07|a12'].marco.data === c.hoje && v.ref && v.ref.est === true, [rv, v]);
  // ---------- I4 · liberar com o executante sugerido e o tempo do serviço (já era assim; regressão) ----------
  const c2 = manClone(MAN0); manGerarTodas(c2, null, OT); const ol = c2.oms['OM-0234'];
  const rl = run(c2, x => manLiberar(x, 'OM-0234', true, OT, { executante: manExecSug(ol), tempo: String(ol.tempo) }));
  ok('U4 (regressão) OM-0234 libera com a sugestão (Zé, única pessoa habilitada) e o tempo do serviço (5 h)', !rl.erro && c2.oms['OM-0234'].etapa === 'Liberadas' && c2.oms['OM-0234'].executante === 'Zé' && c2.oms['OM-0234'].tempo === 5, [rl, manExecSug(ol), ol.tempo]);
  // ---------- I9 · checklist: resposta fora de OK sem motivo não segura a conclusão ----------
  ok('U9d manFaltaConcluir não pede "motivo de" para resposta fora de OK', !manFaltaConcluir(c2, Object.assign({}, c2.oms['OM-0234'], { chk: [{ t: 'Lubrificar', tipo: 'Serviço', r: 'Não feito', mot: '' }] }), '1', '1').some(x => /motivo/.test(x)),
     manFaltaConcluir(c2, Object.assign({}, c2.oms['OM-0234'], { chk: [{ t: 'Lubrificar', tipo: 'Serviço', r: 'Não feito', mot: '' }] }), '1', '1'));
}
if (PARTE === 'mapa') {
  // ---------- I10 · talmapa.js: soma acima da fazenda e diferença sem motivo viram aviso; sobreposição e cruzamento continuam travando ----------
  localStorage.clear();
  const anel = [[-47.2, -34.6], [-47.19, -34.6], [-47.19, -34.594], [-47.2, -34.594], [-47.2, -34.6]];
  const ha = tgAreaHa(anel);
  const e = tmValida({ alvo: 'novo', nome: 'T99', decl: '9000', motivo: '', ring: anel }, 'Santa Rita');
  const av = typeof tmAvisos === 'function' ? tmAvisos({ alvo: 'novo', nome: 'T99', decl: '9000', motivo: '', ring: anel }, 'Santa Rita') : null;
  ok('U10a desenho de 9.000 ha declarados (polígono de ' + nfx(ha, 2) + ' ha) na Santa Rita: sem erro de área nem de motivo; os dois viram aviso', !e.decl && !e.motivo && Array.isArray(av) && av.length === 2 && /somam/.test(av.join(' ')) && /sem motivo/.test(av.join(' ')), [e, av]);
  const cruz = tmValida({ alvo: 'novo', nome: 'T98', decl: '10', motivo: '', ring: [[-47.2, -34.6], [-47.19, -34.594], [-47.19, -34.6], [-47.2, -34.594], [-47.2, -34.6]] }, 'Santa Rita');
  ok('U10b contorno que cruza a si mesmo continua barrado (integridade da área)', !!cruz.geo, cruz);
}
print('TOTAL ' + R.length + ' · falhas ' + R.filter(x => !x).length);
