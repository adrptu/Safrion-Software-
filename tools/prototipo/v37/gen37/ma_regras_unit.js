// PCM simplificado v2 · regras da manutenção sem navegador (ma_regras_test.py monta: perfis do g2lib + dados_manutencao.JS + este arquivo).
// Cada caso parte do seed (MAN0) e confere o observável do aceite (AC-PCM-nn da ESPECIFICACAO §9). Saída: uma linha JSON por execução.
const R = []; const ok = (n, cond, info) => R.push({ n, ok: !!cond, info: cond ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 600) });
const caso = (n, fn) => { try { fn(); } catch (e) { R.push({ n: n + ' (exceção)', ok: false, info: String(e && e.stack || e).slice(0, 600) }); } };
const S = () => manClone(MAN0);
const OT = g2pf('Otávio'), ZE = g2pf('Zé'), ANA = g2pf('Ana'), RUI = g2pf('Rui');
const run = (c, fn) => { const cc = manClone(c); let r; try { r = fn(cc) || {}; } catch (e) { r = { erro: String(e.message || e) }; } if (!r.erro && !r.nada) Object.assign(c, cc); return r; };
const feitas = (c, id, pf) => { c.oms[id].chk.forEach((t, i) => { if (t.tipo === 'Serviço' && !t.r) manResp(c, id, i, 'Feito', undefined, pf); if (t.tipo === 'Verificação' && !t.r) manResp(c, id, i, 'Conforme', undefined, pf); }); };

caso('AC-PCM-32 estado', () => {
  ok('AC-PCM-32 · estado v=4 com achados, leituras, abastecimentos e recibos (c.achados substitui c.ach)', MAN0.v === 4 && MAN0.achados && Array.isArray(MAN0.leituras) && Array.isArray(MAN0.abast) && MAN0.recibos && !('ach' in MAN0) && !('prop' in MAN0), Object.keys(MAN0));
  ok('AC-PCM-32 · o.ver continua a versão do plano (OM-0234 = 3) e a versão do registro é o.rv', MAN0.oms['OM-0234'].ver === 3 && MAN0.oms['OM-0234'].rv === 0, MAN0.oms['OM-0234']);
  const enc = Object.values(MAN0.oms).filter(o => o.etapa === 'Encerradas').map(o => o.id).sort();
  ok('D-43 · histórico encerrado sintético (OM-0102 … OM-0231) com custo pela função única', enc.length === 12 && enc[0] === 'OM-0102' && manCustoFinal(MAN0, MAN0.oms['OM-0219']) === 690 + 16 * 28 + 40 * 24 + 8 * 320, [enc, manCustoFinal(MAN0, MAN0.oms['OM-0219'])]);
  ok('D-43 · OM-0221 (concessionária): peças + terceiro = R$ 3.800,00', manCustoFinal(MAN0, MAN0.oms['OM-0221']) === 3800, manCustoFinal(MAN0, MAN0.oms['OM-0221']));
});

caso('AC-PCM-08 gerar', () => {
  const c = S(); const r = manGerarTodas(c, null, OT);
  const o = c.oms;
  ok('AC-PCM-08 · gerar do seed cria OM-0235, OM-0236 e OM-0237 em A liberar, sem reserva, janelas 24/09, 24/09, 01/10', JSON.stringify(r.ids) === JSON.stringify(['OM-0235', 'OM-0236', 'OM-0237'])
    && ['OM-0235', 'OM-0236', 'OM-0237'].every(id => o[id].etapa === 'A liberar' && o[id].pecas.every(p => !p.res)) && o['OM-0235'].janIso === '2026-09-24' && o['OM-0236'].janIso === '2026-09-24' && o['OM-0237'].janIso === '2026-10-01', [r, o['OM-0235'] && o['OM-0235'].janIso, o['OM-0237'] && o['OM-0237'].janIso]);
  const r2 = manGerarTodas(c, null, OT);
  ok('AC-PCM-08 · gerar de novo não duplica (Nada a gerar)', r2.nada && Object.keys(c.oms).length === Object.keys(MAN0.oms).length + 3, r2);
  ok('D-11 · a preventiva gerada traz as tarefas do plano com tipo (Serviço) e nenhuma respondida', o['OM-0235'].chk.length === 5 && o['OM-0235'].chk.every(t => t.tipo === 'Serviço' && !t.r), o['OM-0235'].chk);
  let e = ''; try { manGerarTodas(S(), null, ZE); } catch (x) { e = x.message; }
  ok('AC-PCM-19 · gerar é do Otávio: Zé é recusado com o motivo', /Ação do Otávio/.test(e), e);
});

caso('AC-PCM-30 conflito', () => {
  const c = S(); manGerarTodas(c, null, OT);
  const cf = id => manConflito(c, c.oms[id]);
  ok('AC-PCM-30 · conflito calculado sobre AL: OM-0234 (28/09) e OM-0236 (24/09) com conflito; OM-0235 (5 h livres ≥ 4 h) e OM-0237 sem', !!cf('OM-0234') && !!cf('OM-0236') && !cf('OM-0235') && !cf('OM-0237'),
    [cf('OM-0234'), cf('OM-0236'), cf('OM-0235'), cf('OM-0237')]);
  ok('AC-PCM-30 · selo "Conflito · OS-0420 28/09"; OM-0236 com OS-0420 e OS-0431', cf('OM-0234').t === 'Conflito · OS-0420 28/09' && cf('OM-0236').os.join() === 'OS-0420,OS-0431', [cf('OM-0234').t, cf('OM-0236').os]);
  ok('AC-PCM-30 · "Próxima sem conflito" da OM-0234 = 29/09', manProxLivre(c, c.oms['OM-0234']) === '2026-09-29', manProxLivre(c, c.oms['OM-0234']));
  const r = run(c, x => manMover(x, 'OM-0234', '2026-09-29', '', OT));
  ok('AC-PCM-30 · mover dentro da tolerância: sem motivo, sem conflito, vencOrig preservado (28/09)', !r.erro && !r.nada && c.oms['OM-0234'].janIso === '2026-09-29' && !manConflito(c, c.oms['OM-0234']) && c.oms['OM-0234'].vencOrig === '2026-09-28' && /dentro da tolerância/.test(r.msg), [r, c.oms['OM-0234']]);
  const r2 = run(c, x => manMover(x, 'OM-0234', '2026-10-05', '', OT));
  ok('AC-PCM-30 · fora da tolerância pede motivo (até o 1b) e não grava', r2.nada && r2.avisoTol && /fora da tolerância/.test(r2.msg) && c.oms['OM-0234'].janIso === '2026-09-29', r2);
  const r3 = run(c, x => manMover(x, 'OM-0234', '2026-10-05', 'oficina parada até 05/10', OT));
  ok('AC-PCM-30 · com motivo move e registra (motivo, quem)', !r3.erro && c.oms['OM-0234'].janIso === '2026-10-05' && c.oms['OM-0234'].movs.slice(-1)[0].motivo === 'oficina parada até 05/10' && /Otávio/.test(c.oms['OM-0234'].movs.slice(-1)[0].por), [r3, c.oms['OM-0234'].movs]);
  const r4 = run(c, x => manMover(x, 'OM-0236', '2026-09-29', '', OT));
  ok('AC-PCM-30 · preventiva já vencida (OM-0236) pede motivo para mover', r4.nada && r4.avisoTol && /venceu/.test(r4.msg), r4);
  const r5 = run(c, x => manMover(x, 'OM-0235', '2026-09-26', '', ZE));
  ok('AC-PCM-19 · "Mover janela" é do Otávio (Zé recusado)', /Ação do Otávio/.test(r5.erro || ''), r5);
});

caso('AC-PCM-31 executante', () => {
  const c = S(); manGerarTodas(c, null, OT);
  ok('AC-PCM-31 · uma pessoa habilitada vem pré-escolhida: Zé (NR-12) para Mecânico; João (NR-10) para Eletricista', manExecSug(c.oms['OM-0234']) === 'Zé' && manExecSug(c.oms['OM-0237']) === 'João' && manExecCands('Eletricista').join() === 'João', [manExecSug(c.oms['OM-0234']), manExecSug(c.oms['OM-0237'])]);
  c.oms['OM-0234'].esp = 'Terceiro (concessionária)';
  const r = run(c, x => manLiberar(x, 'OM-0234', true, OT));
  ok('AC-PCM-31 · sem executante: "Falta: executante" e nada liberado', /Falta: executante/.test(r.erro || '') && c.oms['OM-0234'].etapa === 'A liberar', r);
  const r2 = run(c, x => manLiberar(x, 'OM-0234', true, OT, { executante: 'Concessionária MF' }));
  ok('AC-PCM-31 · com o executante informado libera', !r2.erro && c.oms['OM-0234'].etapa === 'Liberadas' && c.oms['OM-0234'].executante === 'Concessionária MF', r2);
});

caso('AC-PCM-09 achado', () => {
  const c = S();
  const op = id => manAchOpcoes(c, id);
  ok('AC-PCM-09 · INSP-104 (Média, Trator 02 com OM-0234 aberta) → primária "Vincular à OM-0234"', op('INSP-104').prim.t === 'Vincular à OM-0234', op('INSP-104'));
  ok('AC-PCM-09 · SM-0150 (colhedora sem OM e sem vencimento devido) → "Criar ordem corretiva"; Fechar sem serviço entre as secundárias', op('SM-0150').prim.k === 'corretiva' && op('SM-0150').sec.some(x => x.k === 'fechar'), op('SM-0150'));
  ok('AC-PCM-09 · NC-0912 (Plantadeira, PM-05 vencida sem OM) → "Gerar ordem preventiva com NC-0912"', op('NC-0912').prim.t === 'Gerar ordem preventiva com NC-0912', op('NC-0912'));
  // achado Alta → Criar corretiva mesmo com OM aberta
  const rA = run(c, x => manAchRegistrar(x, { aid: 'a02', origem: 'Relato', comp: 'Motor', sint: 'Fumaça preta', crit: 'Alta', sug: 'Restrito' }, OT, 'k-a1'));
  ok('AC-PCM-09 · achado Alta no Trator 02 → primária "Criar ordem corretiva" (vincular só com janela até amanhã)', rA.id === 'SM-0153' && op('SM-0153').prim.k === 'corretiva' && op('SM-0153').sec.some(x => x.k === 'vincular') === false, [rA, op('SM-0153')]);
  // Vincular não oferecido para OM em Em conferência (OM-0230, Pulverizador)
  run(c, x => manAchRegistrar(x, { aid: 'a05', origem: 'Inspeção', comp: 'Hidráulico', sint: 'Gotejamento no bico', crit: 'Média', sug: 'Apto' }, OT));
  const idp = Object.keys(c.achados).find(k => c.achados[k].aid === 'a05');
  ok('AC-PCM-09 · Vincular não é oferecido para a OM-0230 (Em conferência)', idp === 'INSP-106' && ![op(idp).prim].concat(op(idp).sec).some(x => x.om === 'OM-0230'), [idp, op(idp)]);
  // Criar corretiva herda e repetir devolve a mesma
  const c2 = S(); const r1 = run(c2, x => manAchCorretiva(x, 'SM-0150', OT, 'k1')); const o = c2.oms[r1.id];
  ok('AC-PCM-09 · Criar ordem corretiva: 1 OM em A liberar com ativo, componente, sintoma e criticidade herdados; o selo "Nova" sai', r1.id === 'OM-0235' && o.etapa === 'A liberar' && o.aid === 'a08' && o.comp === 'Órgão de trabalho' && /Ruído intermitente/.test(o.serv) && o.crit === 'Baixa'
    && c2.achados['SM-0150'].estado === 'Na OM' && !c2.achados['SM-0150'].nova && o.chk.some(t => t.tipo === 'Verificação' && (t.ach || []).indexOf('SM-0150') >= 0), [r1, o]);
  const n0 = Object.keys(c2.oms).length; const r2 = run(c2, x => manAchCorretiva(x, 'SM-0150', OT, 'k1')); const r3 = run(c2, x => manAchCorretiva(x, 'SM-0150', OT, 'k2'));
  ok('AC-PCM-09 · repetir (mesma chave ou outra) devolve a mesma OM, sem ordem nova', r2.nada && r2.id === 'OM-0235' && r3.nada && r3.id === 'OM-0235' && Object.keys(c2.oms).length === n0, [r2, r3]);
  // Gerar com o achado: 1 OM + vínculo numa transação
  const c3 = S(); const g = run(c3, x => manAchGerar(x, 'NC-0912', OT, 'k3'));
  ok('AC-PCM-09 · Gerar com o achado: 1 OM preventiva + vínculo (NC-0912 vira Verificação da OM-0235)', g.id === 'OM-0235' && c3.oms['OM-0235'].pid === 'PM-05' && c3.achados['NC-0912'].om === 'OM-0235' && c3.oms['OM-0235'].chk.some(t => t.tipo === 'Verificação' && /Disco de corte/.test(t.t)), [g, c3.oms['OM-0235'] && c3.oms['OM-0235'].chk.slice(-1)]);
  // Fechar sem serviço exige motivo
  const f0 = run(c3, x => manAchFechar(x, 'SM-0150', '', OT)); const f1 = run(c3, x => manAchFechar(x, 'SM-0150', 'ruído normal do elevador novo', OT));
  ok('AC-PCM-09 · Fechar sem serviço exige motivo', /motivo/.test(f0.erro || '') && !f1.erro && c3.achados['SM-0150'].estado === 'Fechado sem serviço', [f0, f1]);
  // Somar: mesmo ativo e componente oferece Somar; componente diferente não
  const c4 = S(); const s1 = run(c4, x => manAchRegistrar(x, { aid: 'a02', origem: 'Relato', comp: 'Hidráulico', sint: 'Mangueira molhada', crit: 'Média', sug: 'Apto' }, ZE));
  const s2 = run(c4, x => manAchRegistrar(x, { aid: 'a02', origem: 'Relato', comp: 'Elétrico', sint: 'Farol queimado', crit: 'Baixa', sug: 'Apto' }, ZE));
  const s3 = run(c4, x => manAchRegistrar(x, { aid: 'a02', origem: 'Relato', comp: 'Hidráulico', sint: 'Mangueira molhada', crit: 'Média', sug: 'Apto', rep: 'somar' }, ZE));
  ok('AC-PCM-09 · mesmo ativo e mesmo componente oferece Somar (INSP-104); componente diferente registra novo; Somar soma a ocorrência', s1.nada && s1.rep === 'INSP-104' && s2.id === 'SM-0153' && s3.id === 'INSP-104' && c4.achados['INSP-104'].oc.length === 2, [s1, s2, s3]);
  ok('D-48 · prefixo por origem e número = maior + 1 (Inspeção → INSP-106; Relato → SM-0153)', manAchProx(S(), 'INSP') === 'INSP-106' && manAchProx(S(), 'SM') === 'SM-0153' && manAchProx(S(), 'NC') === 'NC-0913', [manAchProx(S(), 'INSP'), manAchProx(S(), 'NC')]);
  // volta do achado
  const c5 = S(); run(c5, x => manAchVincular(x, 'INSP-104', 'OM-0234', OT)); run(c5, x => manLiberar(x, 'OM-0234', true, OT)); run(c5, x => manIniciar(x, 'OM-0234', ZE));
  const it = c5.oms['OM-0234'].chk.findIndex(t => t.tipo === 'Verificação');
  feitas(c5, 'OM-0234', ZE); run(c5, x => manResp(x, 'OM-0234', it, 'Não se aplica', 'não deu tempo', ZE));
  const cc = run(c5, x => manConcluir(x, 'OM-0234', '2995', '5', true, {}, ZE)); const en = run(c5, x => manEncerrar(x, 'OM-0234', OT));
  ok('AC-PCM-09 · OM encerrada sem Conforme devolve o achado a Sem ordem com "Voltou da OM-0234"', !cc.erro && !en.erro && c5.achados['INSP-104'].estado === 'Sem ordem' && c5.achados['INSP-104'].voltou === 'OM-0234', [cc, en, c5.achados['INSP-104']]);
});

caso('AC-PCM-10/11 tarefas', () => {
  ok('AC-PCM-10 · nenhuma tarefa nasce respondida nas OMs abertas que não começaram', Object.values(MAN0.oms).filter(o => o.etapa === 'A liberar' || o.etapa === 'Liberadas').every(o => o.chk.every(t => !t.r)), '');
  ok('AC-PCM-11 · OM-0228: "Medir pressão de recalque" é Medição; as outras duas, Verificação', MAN0.oms['OM-0228'].chk.map(t => t.tipo).join() === 'Medição,Verificação,Verificação', MAN0.oms['OM-0228'].chk);
  // Não feito → Pendência (com o executante herdado)
  const c = S(); run(c, x => manLiberar(x, 'OM-0234', true, OT)); run(c, x => manIniciar(x, 'OM-0234', ZE)); feitas(c, 'OM-0234', ZE);
  run(c, x => manResp(x, 'OM-0234', 4, 'Não feito', 'sem graxa', ZE)); const r = run(c, x => manConcluir(x, 'OM-0234', '2995', '5', false, {}, ZE));
  const pend = c.oms['OM-0234'].pend || [];
  ok('AC-PCM-11 · "Não feito" abre OM de Pendência com o executante da origem', !r.erro && pend.length === 1 && c.oms[pend[0]].tipo === 'Pendência' && c.oms[pend[0]].executante === 'Zé', [r, pend]);
  // Não conforme → achado (Medição da OM-0228)
  const c2 = S(); const z = run(c2, x => manIniciar(x, 'OM-0228', ZE));
  run(c2, x => manIniciar(x, 'OM-0228', { k: 'João', papeis: { mecanico: 'irrigante' } }));
  run(c2, x => manResp(x, 'OM-0228', 0, 'Não conforme', 'pressão 2,1 bar', { k: 'João', papeis: { mecanico: 'irrigante' } }, '2,1'));
  run(c2, x => manResp(x, 'OM-0228', 1, 'Conforme', undefined, { k: 'João', papeis: { mecanico: 'irrigante' } })); run(c2, x => manResp(x, 'OM-0228', 2, 'Não foi possível verificar', 'painel sem acesso', { k: 'João', papeis: { mecanico: 'irrigante' } }));
  const r2 = run(c2, x => manConcluir(x, 'OM-0228', '8930', '3', false, {}, { k: 'João', papeis: { mecanico: 'irrigante' } }));
  ok('AC-PCM-19 · Zé não inicia a OM-0228 (executante João): "Ação de João, executante"', /Ação de João, executante/.test(z.erro || ''), z);
  ok('AC-PCM-11 · "Não conforme" e "Não foi possível verificar" somam no achado do ativo e componente (SM-0152 · Hidráulico) ou abrem NC', !r2.erro && c2.achados['SM-0152'].oc.length >= 4, [r2, c2.achados['SM-0152']]);
  ok('AC-PCM-11 · achado de origem só fica Resolvido com teste válido: Medição Não conforme não resolve o SM-0152', c2.achados['SM-0152'].estado === 'Na OM', c2.achados['SM-0152']);
});

caso('AC-PCM-12 teste', () => {
  const c = S(); const o = c.oms['OM-0233'];
  ok('AC-PCM-12 · a OM-0233 já traz a 1ª tentativa Reprovada (23/09 09:00)', o.chk[3].tipo === 'Teste' && o.chk[3].tent.length === 1 && o.chk[3].tent[0].r === 'Reprovado' && /09:00/.test(o.chk[3].tent[0].em), o.chk[3]);
  const r0 = run(c, x => manConcluir(x, 'OM-0233', '4313', '6,5', false, {}, ZE));
  ok('AC-PCM-12 · Concluir é recusado sem a última tentativa Aprovada', /teste aprovado/.test(r0.erro || '') && c.oms['OM-0233'].etapa === 'Em execução', r0);
  const rr = run(c, x => manTentativa(x, 'OM-0233', 3, 'Reprovado', 'foto (simulada) · 150 bar', ZE));
  ok('AC-PCM-12 · Reprovado deixa a OM Em execução e o ativo Bloqueado, sem OM nova', !rr.erro && c.oms['OM-0233'].etapa === 'Em execução' && c.ativos.a01.cond === 'Bloqueado' && Object.keys(c.oms).length === Object.keys(MAN0.oms).length, rr);
  const ra = run(c, x => manTentativa(x, 'OM-0233', 3, 'Aprovado', 'foto (simulada) · 185 bar', ZE));
  ok('AC-PCM-12 · depois de Reprovado e Aprovado, as tentativas ficam por acréscimo (3, a última Aprovada)', !ra.erro && c.oms['OM-0233'].chk[3].tent.length === 3 && c.oms['OM-0233'].chk[3].tent[2].r === 'Aprovado' && c.oms['OM-0233'].chk[3].tent[0].r === 'Reprovado', c.oms['OM-0233'].chk[3].tent);
  const ro = run(S(), x => manTentativa(x, 'OM-0233', 3, 'Aprovado', 'foto', OT));
  ok('AC-PCM-12 · sem a habilitação (Otávio não é o executante nem tem "Testar reparo"): Teste recusado com o motivo', /executante|Testar reparo/.test(ro.erro || ''), ro);
  const zeSem = { k: 'Zé', papeis: { mecanico: 'mecânico' } }; const cc = S(); const pes = MAN_PES.find(p => p.k === 'Zé'); const h0 = pes.hab.slice(); pes.hab = pes.hab.filter(h => h !== 'Testar reparo');
  const rz = run(cc, x => manTentativa(x, 'OM-0233', 3, 'Aprovado', 'foto', zeSem)); pes.hab = h0;
  ok('AC-PCM-12 · Zé sem a habilidade "Testar reparo" no CD-04: Teste desabilitado com o motivo', /Testar reparo/.test(rz.erro || ''), rz);
  const re = run(S(), x => manTentativa(x, 'OM-0233', 3, 'Aprovado', '', ZE));
  ok('AC-PCM-12 · tentativa sem evidência é recusada', /evidência/.test(re.erro || ''), re);
});

caso('AC-PCM-13/26 condição e encerrar', () => {
  const c = S(); run(c, x => manTentativa(x, 'OM-0233', 3, 'Aprovado', 'foto (simulada)', ZE));
  const r1 = run(c, x => manConcluir(x, 'OM-0233', '4313', '6,5', false, {}, ZE));
  ok('C · concluir a OM-0233 com teste aprovado: Em conferência; SM-0147 e INSP-105 resolvidos pelo Teste (D-31)', !r1.erro && c.oms['OM-0233'].etapa === 'Em conferência' && c.achados['SM-0147'].estado === 'Resolvido' && c.achados['INSP-105'].estado === 'Resolvido', [r1, c.achados['SM-0147'].estado]);
  const e1 = run(c, x => manEncerrar(x, 'OM-0233', OT));
  ok('AC-PCM-13/26 · Encerrar é recusado na OM que trata a condição sem "Declarar apto"/"Manter" e com a bomba "A definir"', /Declarar Trator T1 apto/.test(e1.erro || '') && /Bomba hidráulica usada/.test(e1.erro || ''), e1);
  const a1 = run(c, x => manDeclararApto(x, 'OM-0233', ANA));
  ok('AC-PCM-19 · Ana não declara apto (não é Otávio nem o responsável técnico)', /responsável técnico/.test(a1.erro || ''), a1);
  const a2 = run(c, x => manDeclararApto(x, 'OM-0233', ZE));
  ok('AC-PCM-13 · Zé (responsável técnico do T1) declara apto: condição Apto com histórico, por e data', !a2.erro && c.ativos.a01.cond === 'Apto' && c.ativos.a01.condHist.slice(-1)[0].om === 'OM-0233' && /Zé/.test(c.ativos.a01.condHist.slice(-1)[0].por), [a2, c.ativos.a01]);
  const e2 = run(c, x => manEncerrar(x, 'OM-0233', OT));
  ok('AC-PCM-26 · Encerrar segue recusado com a peça retirada "A definir" (dano: perder peça recuperável)', /Bomba hidráulica usada/.test(e2.erro || '') && !/Declarar/.test(e2.erro || ''), e2);
  const d1 = run(c, x => manRetirada(x, 'OM-0233', 0, 'Recondicionar', 'Zé (mecânico)', ZE));
  const e3 = run(c, x => manEncerrar(x, 'OM-0233', OT));
  ok('AC-PCM-26 · destino com responsável e nenhum movimento de lote; depois disso encerra com o custo (R$ 4.100 de peças + 6,5 h)', !d1.erro && !e3.erro && c.oms['OM-0233'].etapa === 'Encerradas' && c.oms['OM-0233'].custo === 3600 + 500 + 6.5 * 320 && JSON.stringify(c.itens) === JSON.stringify(MAN0.itens), [d1, e3, c.oms['OM-0233'].custo]);
  // Encerrar restrição: OM-0228 trata a restrição → "Encerrar restrição" recusado; Medição Conforme devolve a Bomba do Pivô 2 a Apto
  const b = S(); const JO = g2pf('João');   // A8 (revisão 09/10): o João do cadastro de perfis (G2_PERFIS), não um perfil inventado no teste
  const er = run(b, x => manCondicao(x, 'a11', 'encerrar', { motivo: 'x', evid: 'y' }, OT));
  ok('AC-PCM-13 · "Encerrar restrição" recusado enquanto a OM-0228 trata a restrição', /OM-0228 trata a restrição/.test(er.erro || ''), er);
  run(b, x => manIniciar(x, 'OM-0228', JO)); run(b, x => manResp(x, 'OM-0228', 0, 'Conforme', undefined, JO, '3,4')); run(b, x => manResp(x, 'OM-0228', 1, 'Conforme', undefined, JO)); run(b, x => manResp(x, 'OM-0228', 2, 'Conforme', undefined, JO));
  const rc = run(b, x => manConcluir(x, 'OM-0228', '8930', '3', false, {}, JO)); const ap = run(b, x => manDeclararApto(x, 'OM-0228', OT)); const en = run(b, x => manEncerrar(x, 'OM-0228', OT));
  ok('AC-PCM-13 · OM-0228 (Medição Conforme) devolve a Bomba do Pivô 2 a Apto; SM-0152 resolvido pela Medição', !rc.erro && !ap.erro && !en.erro && b.ativos.a11.cond === 'Apto' && b.achados['SM-0152'].estado === 'Resolvido', [rc, ap, en, b.ativos.a11.cond, b.achados['SM-0152'].estado]);
  // corretiva criada de achado bloqueante ganha Teste do reparo e chega a Apto
  const d = S(); const ra = run(d, x => manAchRegistrar(x, { aid: 'a03', origem: 'Inspeção', comp: 'Rodado e freios', sint: 'Freio sem ação', crit: 'Alta', sug: 'Bloqueado', bloquear: true }, OT, 'k9'));
  const rco = run(d, x => manAchCorretiva(x, ra.id, OT, 'k10')); const o = d.oms[rco.id];
  ok('AC-PCM-13 · "Registrar e bloquear" + corretiva: a OM trata a condição e ganha "Teste do reparo · Freio sem ação"', d.ativos.a03.cond === 'Bloqueado' && o.trata && o.chk.some(t => t.tipo === 'Teste' && t.fixo && /Teste do reparo · Freio sem ação/.test(t.t)) && d.ativos.a03.condInfo.om === o.id, [ra, rco, o && o.chk]);
  run(d, x => manLiberar(x, o.id, true, OT, { tempo: '2' })); run(d, x => manIniciar(x, o.id, ZE)); run(d, x => manTentativa(x, o.id, 0, 'Aprovado', 'foto', ZE));
  run(d, x => manConcluir(x, o.id, '5125', '2', false, {}, ZE)); run(d, x => manDeclararApto(x, o.id, OT)); const ee = run(d, x => manEncerrar(x, o.id, OT));
  ok('AC-PCM-13 · …e chega a Apto, encerrada', !ee.erro && d.ativos.a03.cond === 'Apto' && d.oms[o.id].etapa === 'Encerradas', [ee, d.ativos.a03.cond]);
  // Manter desfaz o vínculo; Encerrar restrição sem OM exige motivo e evidência
  const m = S(); run(m, x => manTentativa(x, 'OM-0233', 3, 'Aprovado', 'foto', ZE)); run(m, x => manConcluir(x, 'OM-0233', '4313', '6,5', false, {}, ZE));
  const m0 = run(m, x => manManter(x, 'OM-0233', '', OT)); const m1 = run(m, x => manManter(x, 'OM-0233', 'vazamento residual', OT));
  ok('AC-PCM-13 · "Manter bloqueado" exige motivo e desfaz o vínculo (o ativo pede Criar ordem corretiva)', /motivo/.test(m0.erro || '') && !m1.erro && m.ativos.a01.cond === 'Bloqueado' && !m.ativos.a01.condInfo.om, [m0, m1, m.ativos.a01.condInfo]);
  const rs = S(); const q1 = run(rs, x => manCondicao(x, 'a04', 'restringir', { motivo: 'folga no eixo', lim: 'sem implemento pesado', ate: '2026-09-30' }, OT));
  const q2 = run(rs, x => manCondicao(x, 'a04', 'encerrar', { motivo: 'medida ok', evid: '' }, OT)); const q3 = run(rs, x => manCondicao(x, 'a04', 'encerrar', { motivo: 'medida ok', evid: 'folga 0,2 mm' }, OT));
  ok('AC-PCM-13 · Restringir grava condição, motivo, prazo, por e data; "Encerrar restrição" sem OM exige motivo e evidência', !q1.erro && /evidência/.test(q2.erro || '') && !q3.erro && rs.ativos.a04.cond === 'Apto' && rs.ativos.a04.condHist.length === 2 && rs.ativos.a04.condHist[0].ate === '2026-09-30', [q1, q2, q3]);
  const bz = run(S(), x => manCondicao(x, 'a03', 'bloquear', { motivo: 'x' }, ZE));
  const bz2 = run(S(), x => manCondicao(x, 'a02', 'bloquear', { motivo: 'freio' }, ZE));
  ok('AC-PCM-19 · Bloquear: Zé só onde é o responsável técnico (Trator 02 sim; Trator 03 não)', /responsável técnico/.test(bz.erro || '') && !bz2.erro, [bz, bz2]);
});

caso('AC-PCM-15 leitura', () => {
  const c = S(); run(c, x => manLiberar(x, 'OM-0234', true, OT)); run(c, x => manIniciar(x, 'OM-0234', ZE)); feitas(c, 'OM-0234', ZE);
  const v0 = JSON.stringify(c.vinc['PM-01|a02']); const r = run(c, x => manConcluir(x, 'OM-0234', '150', '5', false, {}, ZE));
  ok('AC-PCM-15 · regressão: concluir com 150 h no Trator 02 é recusado e não fecha o ciclo nem desloca referências', /menor que a última/.test(r.erro || '') && /Falta: decidir a leitura/.test(r.erro || '') && JSON.stringify(c.vinc['PM-01|a02']) === v0 && c.oms['OM-0234'].etapa === 'Em execução', r);
  const r2 = run(c, x => manConcluir(x, 'OM-0234', '29.950', '5', false, {}, ZE));
  ok('AC-PCM-15 · leitura implausível na conclusão dá aviso (não grava)', r2.nada && r2.avisoLeit && c.oms['OM-0234'].etapa === 'Em execução', r2);
  const r3 = run(c, x => manConcluir(x, 'OM-0234', '2995', '', false, {}, ZE));
  ok('D-18 · horas de oficina obrigatórias (sem valor implícito)', /horas de oficina/.test(r3.erro || ''), r3);
  const c2 = S(); const l1 = manLeitura(c2, 'a02', 2900, 'Leitura avulsa', OT, '2026-09-23');
  ok('AC-PCM-15 · fora da conclusão, leitura menor vira troca a confirmar; vencimentos seguem a anterior', l1.sus === 'menor' && c2.ativos.a02.leit.val === 2988 && c2.ativos.a02.suspeita.val === 2900, l1);
  const c3 = S(); const l2 = manLeitura(c3, 'a02', 2980, 'Tíquete atrasado', OT, '2026-09-22');
  ok('AC-PCM-15 · tíquete com data anterior entra no histórico sem pedir troca e sem mudar a leitura atual', !l2.sus && l2.qual === 'Confirmada' && c3.ativos.a02.leit.val === 2988 && !c3.ativos.a02.suspeita && c3.leituras.some(x => x.val === 2980 && x.antiga), l2);
  const l3 = manLeitura(c3, 'a02', 3500, 'Tíquete atrasado', OT, '2026-09-22');
  ok('AC-PCM-15 · data anterior fora das vizinhas fica "a confirmar" (ainda sem troca)', l3.qual === 'A confirmar' && !c3.ativos.a02.suspeita, l3);
  const c4 = S(); const k = manLeitura(c4, 'a04', 3530, 'Abastecimento', OT);
  ok('AC-PCM-15 · leitura de hoje coerente recalcula (Trator 04 vence em breve)', /vence em breve/.test(k.msg) && c4.ativos.a04.leit.val === 3530, k);
});

caso('AC-PCM-16 abastecimento', () => {
  const c = S();
  ok('D-19 · operador da alocação do ativo no dia (Trator 03 em 23/09 → Marcos; Trator 02 em 23/09 sem alocação → nenhum)', manOperadorDia(c, 'a03', '2026-09-23') === 'Marcos' && manOperadorDia(c, 'a02', '2026-09-23') === '', [manOperadorDia(c, 'a03', '2026-09-23'), manOperadorDia(c, 'a02', '2026-09-23')]);
  ok('D-19 · lote pré-escolhido só com 1 elegível (Trator 02 no campo: só o comboio; Trator 03 no galpão: dois)', manTanques(c, 'a02').length === 1 && manTanques(c, 'a03').length === 2, [manTanques(c, 'a02'), manTanques(c, 'a03')]);
  const t = [['a03', '120', '5130'], ['a04', '80', '3420'], ['a05', '200', '1550']]; const ids = [];
  t.forEach(([aid, vol, leit], i) => { const r = run(c, x => manAbastecer(x, { aid, tq: 'Comboio CB-01 · D-118', vol, leit, op: 'Marcos' }, OT, 'kb' + i)); ids.push(r.id); });
  ok('AC-PCM-16 · "Registrar outro" com 3 tíquetes (chave nova por registro) cria 3 lançamentos', ids.join() === 'AB-1043,AB-1044,AB-1045' && c.abast.length === MAN0.abast.length + 3, ids);
  const r2 = run(c, x => manAbastecer(x, { aid: 'a03', tq: 'Comboio CB-01 · D-118', vol: '120', leit: '5130', op: 'Marcos' }, OT, 'kb0'));
  ok('AC-PCM-16 · duplo toque (mesma chave) cria 1 e devolve o recibo', r2.nada && r2.repetido && r2.id === 'AB-1043' && c.abast.length === MAN0.abast.length + 3, r2);
  const e = run(c, x => manEstornar(x, 'AB-1043', 'volume errado', OT, 'ke1'));
  ok('AC-PCM-16 · estorno cria lançamento novo e mantém o original (Estornado)', e.id === 'ES-0089' && c.abast.find(b => b.id === 'AB-1043').qual === 'Estornado' && c.abast.find(b => b.id === 'ES-0089').vol === -120, e);
  const lh = manLh(MAN0, MAN0.abast.find(b => b.id === 'AB-1042')); const lh2 = manLh(MAN0, MAN0.abast.find(b => b.id === 'AB-1041'));
  ok('AC-PCM-16 · L/h só com método (tanque cheio a tanque cheio): AB-1042 = 180 L ÷ 11 h; AB-1041 sem método', lh && Math.abs(lh.lh - 180 / 11) < 1e-9 && lh2 === null, [lh, lh2]);
  const sem = run(c, x => manAbastecer(x, { aid: 'a03', tq: '', vol: '', leit: '', op: '' }, OT, 'kz'));
  ok('AC-PCM-16 · campos obrigatórios: tanque/lote, volume, leitura e operador', /tanque\/lote, volume em L, leitura \(h\), operador/.test(sem.erro || ''), sem);
});

caso('AC-PCM-19 matriz', () => {
  const c = S(); const o = c.oms['OM-0233'];
  const linhas = [['registrar', [OT, ZE, ANA], [RUI]], ['decidir', [OT], [ZE, ANA]], ['gerar', [OT], [ZE, ANA]], ['liberar', [OT], [ZE, ANA]], ['encerrar', [OT], [ZE, ANA]], ['ponte', [OT], [ZE, ANA]], ['plano', [OT], [ZE, ANA]]];
  linhas.forEach(([cmd, sim, nao]) => ok('AC-PCM-19 · matriz "' + cmd + '": habilitado só para ' + sim.map(p => p.k).join(', '), sim.every(p => !manPode(c, p, cmd)) && nao.every(p => !!manPode(c, p, cmd)), cmd));
  ok('AC-PCM-19 · executar a OM-0233: só Zé (executante)', !manPode(c, ZE, 'executar', { o }) && !!manPode(c, OT, 'executar', { o }) && !!manPode(c, ANA, 'executar', { o }), '');
  ok('AC-PCM-19 · executar a OM-0228: só João; Zé recebe "Ação de João, executante"', manPode(c, ZE, 'executar', { o: c.oms['OM-0228'] }) === 'Ação de João, executante', manPode(c, ZE, 'executar', { o: c.oms['OM-0228'] }));
  ok('AC-PCM-19 · Incluir tarefa: Otávio até Liberadas; Zé Em execução quando executante', !manPode(c, OT, 'incluir', { o: c.oms['OM-0228'] }) && !manPode(c, ZE, 'incluir', { o }) && !!manPode(c, OT, 'incluir', { o }), '');
  ok('AC-PCM-19 · condição: Otávio sempre; Zé no T1, Trator 02 e Pulverizador; Ana não', !manPode(c, OT, 'condicao', { aid: 'a11' }) && !manPode(c, ZE, 'condicao', { aid: 'a05' }) && !!manPode(c, ZE, 'condicao', { aid: 'a11' }) && !!manPode(c, ANA, 'condicao', { aid: 'a01' }), '');
  const s0 = JSON.stringify(c); g2pf('Zé'); ok('AC-PCM-19 · consultar a matriz não muda o estado', JSON.stringify(c) === s0, '');
});

caso('AC-PCM-23 vínculo', () => {
  const c = S(); c.planos['PM-11'] = { id: 'PM-11', nome: 'Colhedora · 250 h', grupo: 'Colhedoras', aplica: { t: 'ativos', v: ['a08'] }, estado: 'Ativo', versao: 0, servicos: [{ id: 's1', nome: 'Revisão 250 h', gat: { h: 250 }, tol: {}, tarefas: [{ t: 'x', tipo: 'Serviço' }], pecas: [], tempo: 2, esp: 'Mecânico' }], rasc: null, hist: [] };
  ok('AC-PCM-23 · a corretiva OM-0221 não serve de marco para a Colhedora (serviço diferente e corretiva)', manMarcoSug(c, c.planos['PM-11'], 'a08') === null, manMarcoSug(c, c.planos['PM-11'], 'a08'));
  c.planos['PM-12'] = Object.assign({}, c.planos['PM-11'], { id: 'PM-12', servicos: [Object.assign({}, c.planos['PM-11'].servicos[0], { nome: 'Revisão 500 h' })] });
  const m = manMarcoSug(c, c.planos['PM-12'], 'a08');
  ok('AC-PCM-23 · marco pré-preenchido da última OM encerrada do mesmo serviço (OM-0102 · 15/10/2025 · 1.800 h)', m && m.om === 'OM-0102' && m.leit === 1800, m);
  c.planos['PM-13'] = { id: 'PM-13', nome: 'MF 7719 · 250 h', grupo: 'Tratores', aplica: { t: 'ativos', v: ['a02'] }, estado: 'Ativo', versao: 0, servicos: [Object.assign({}, c.planos['PM-11'].servicos[0], { nome: 'Revisão 250 h' })], rasc: null, hist: [] };
  const m2 = manMarcoSug(c, c.planos['PM-13'], 'a02');
  ok('D-41 · …ou de um serviço que o "cumpre também" (OM-0219, Revisão 500 h, cumpre a 250 h)', m2 && m2.om === 'OM-0219', m2);
});

caso('C1 e recibos', () => {
  const c = S(); run(c, x => manLiberar(x, 'OM-0234', true, OT)); run(c, x => manIniciar(x, 'OM-0234', ZE)); feitas(c, 'OM-0234', ZE);
  run(c, x => manConcluir(x, 'OM-0234', '2995', '5', false, { 1: '12' }, ZE)); run(c, x => manSobras(x, 'OM-0234', OT)); const r = run(c, x => manEncerrar(x, 'OM-0234', OT));
  ok('PCMS §10 C1 · OM-0234 encerra a R$ 2.626,00 (690 + 12 L × 28 + 5 h × 320)', !r.erro && c.oms['OM-0234'].custo === 2626 && /R\$\s2\.626,00/.test(r.msg), r);
  ok('PCMS §10 C2 · a estimativa da OM-0235 (gerada) é R$ 1.776,00', (() => { const d = S(); manGerarTodas(d, null, OT); return manCusto(d, d.oms['OM-0235'], 'est') === 1776; })(), '');
  const d = S(); const a = run(d, x => manLeituraAvulsa(x, 'a04', '3420', '', OT, 'kl')); const b = run(d, x => manLeituraAvulsa(x, 'a04', '3420', '', OT, 'kl'));
  ok('D-30 · a mesma chave devolve o recibo sem gravar de novo', !a.erro && b.nada && b.repetido && d.leituras.filter(x => x.val === 3420).length === 1, [a, b]);
  const v = S(); const o = v.oms['OM-0234']; let e = ''; try { manRv(o, 7); } catch (x) { e = x.message; }
  ok('D-46 · comando com versão do registro diferente é recusado ("Mudou desde que você abriu")', /Mudou desde que você abriu/.test(e), e);
});

caso('Propor substituto (ponte até o 1b)', () => {
  const c = S(); const r = run(c, x => manPropor(x, 'OM-0233', OT)); const r2 = run(c, x => manPropor(x, 'OM-0233', OT)); const z = run(S(), x => manPropor(x, 'OM-0233', ZE));
  ok('§0.1 · "Propor substituto" (sai no 1b): Otávio registra Trator 02 para as O.S. alocadas ao T1 desde o bloqueio (OS-0420 e OS-0431); repetir não duplica; Zé recusado',
    !r.erro && c.prop['OM-0233'].sub === 'a02' && c.prop['OM-0233'].os.join() === 'OS-0420,OS-0431' && r2.nada && /Ação do Otávio/.test(z.erro || ''), [r, r2, z, c.prop]);
  const d = S(); const e = run(d, x => manPropor(x, 'OM-0234', OT));
  ok('§0.1 · só para ativo bloqueado com ordem aberta (Trator 02 apto: recusado)', e.erro && /bloqueado/.test(e.erro), e);
});

// Item 12 (Codex 6064114787 §2, S2): receber, aplicar, devolver e estornar material da manutenção sem saldo nem custo duplicado.
// O 1a garante um estado, um saldo por item e um custo; os movimentos em c.movs sobre lotes do Almox. oficina são o 1b (DECISOES §7).
caso('Item 12 · 1a: um saldo, um custo, conservação e repetição', () => {
  const nomes = Object.values(MAN0.itens).map(x => x.nome), lotes = Object.values(CEN0.lotes).map(l => l.prod);
  ok('Item 12 · 1a · um estado: a manutenção vive em CEN0.man (sem chave própria) e manGet lê o cenário único', MAN0 === CEN0.man && manGet() === cenGet().man && !/talhao-os-manutencao/.test(String(manGet) + String(manMudar)), Object.keys(CEN0));
  ok('Item 12 · 1a · um saldo por item: nenhum item da manutenção tem lote no estoque geral (c.lotes) até o 1b', nomes.every(n => lotes.indexOf(n) < 0), nomes.filter(n => lotes.indexOf(n) >= 0));
  const c = S(); manGerarTodas(c, null, OT); const id = 'OM-0235'; const s0 = JSON.parse(JSON.stringify(c.itens)); const fil = 'FIL-MF4292', ol = 'OL-1540';
  const sc = run(c, x => manSolicitar(x, id, OT)); const rc = run(c, x => manReceber(x, id, OT)); const rc2 = run(c, x => manReceber(x, id, OT));
  ok('Item 12 · receber (ponte simulada): +1 un do filtro uma vez só; repetir não soma de novo', !sc.erro && !rc.erro && rc2.nada && c.itens[fil].saldo === s0[fil].saldo + 1 && /simulado/.test(rc.msg), [sc, rc, rc2, c.itens[fil]]);
  const lb = run(c, x => manLiberar(x, id, false, OT, {})); const lb2 = run(c, x => manLiberar(x, id, false, OT, {}));
  ok('Item 12 · liberar reserva 100 % (1 un + 12 L) uma vez; repetir é recusado sem reservar de novo', !lb.erro && /não está em A liberar/.test(lb2.erro || '') && c.itens[fil].reservado === s0[fil].reservado + 1 && c.itens[ol].reservado === s0[ol].reservado + 12, [lb, lb2]);
  run(c, x => manIniciar(x, id, ZE)); feitas(c, id, ZE);
  const cc = run(c, x => manConcluir(x, id, '5124', '4', false, { 1: '9' }, ZE));
  ok('Item 12 · aplicar 9 L de 12: a reserva sai, o saldo baixa o entregue e a sobra de 3 L fica a devolver', !cc.erro && c.itens[ol].reservado === s0[ol].reservado && c.itens[ol].saldo === s0[ol].saldo - 12 && c.oms[id].pecas[1].sob === 3 && c.oms[id].pecas[1].apl === 9, [cc, c.itens[ol]]);
  const dv = run(c, x => manSobras(x, id, OT)); const dv2 = run(c, x => manSobras(x, id, OT));
  ok('Item 12 · devolver: +3 L uma vez só; repetir não soma de novo', !dv.erro && dv2.nada && c.itens[ol].saldo === s0[ol].saldo - 9, [dv, dv2, c.itens[ol]]);
  const cp0 = manCustoPeriodo(c, 'mes'); const en = run(c, x => manEncerrar(x, id, OT)); const cp1 = manCustoPeriodo(c, 'mes');
  const conserva = Object.keys(s0).every(k => { const rec = k === fil ? 1 : 0; const apl = k === fil ? 1 : (k === ol ? 9 : 0); return c.itens[k].saldo === s0[k].saldo + rec - apl && c.itens[k].reservado === s0[k].reservado; });
  ok('Item 12 · conservação: saldo final = inicial + recebido − aplicado em todo item; reservado volta ao inicial', !en.erro && conserva, [en, c.itens]);
  ok('Item 12 · um custo: OM-0235 encerra a R$ 1.692,00 (1 × 160 + 9 L × 28 + 4 h × 320), pela função única, e entra uma vez no custo do período', c.oms[id].custo === 1692 && manCusto(c, c.oms[id]) === 1692
    && Math.abs(cp1.enc - cp0.enc - 1692) < 1e-9 && Math.abs(cp0.and - cp1.and - manCusto(c, c.oms[id], 'est')) < 1e-9, [c.oms[id].custo, cp0, cp1]);
  const it0 = JSON.stringify(c.itens); const ab = run(c, x => manAbastecer(x, { aid: 'a03', tq: 'Comboio CB-01 · D-118', vol: '120', leit: '5130', op: 'Marcos' }, OT, 'k12')); const es = run(c, x => manEstornar(x, ab.id, 'volume errado', OT, 'k12e'));
  ok('Item 12 · abastecimento e estorno não mexem em saldo de peça nem de lote (diesel como lote é o Bloco 6)', !ab.erro && !es.erro && JSON.stringify(c.itens) === it0, [ab, es]);
});

// CTL-01 PLANO (d) e Codex 6064114787 §3: "Horímetro único" e "Gerar ordem" sem repetição, confirmados no código.
caso('CTL-01 (d) horímetro único e Gerar ordem', () => {
  const c = S();
  run(c, x => manAbastecer(x, { aid: 'a04', tq: 'Comboio CB-01 · D-118', vol: '80', leit: '3420', op: 'Marcos' }, OT, 'h1'));
  run(c, x => manAchRegistrar(x, { aid: 'a04', origem: 'Relato', comp: 'Motor', sint: 'Fumaça preta', crit: 'Média', sug: 'Apto', leit: '3425' }, OT, 'h2'));
  run(c, x => manLeituraAvulsa(x, 'a04', '3430', '', OT, 'h3'));
  run(c, x => manLiberar(x, 'OM-0234', true, OT)); run(c, x => manIniciar(x, 'OM-0234', ZE)); feitas(c, 'OM-0234', ZE); run(c, x => manConcluir(x, 'OM-0234', '2995', '5', false, {}, ZE));
  const org = c.leituras.slice(MAN0.leituras.length).map(l => (l.origem || '').split(' ')[0]);
  ok('Horímetro único · abastecimento, achado, leitura avulsa e conclusão gravam pela mesma função no histórico c.leituras (4 origens)', ['Abastecimento', 'Achado', 'Leitura', 'Conclusão'].every(o => org.indexOf(o) >= 0) && c.ativos.a04.leit.val === 3430 && c.ativos.a02.leit.val === 2995, org);
  const g = S(); const r = manGerarTodas(g, null, OT); const l = manLinhas(g, null).find(x => x.om && x.om.id === 'OM-0235'); const r2 = l ? run(g, x => manGerar(x, l.pid + '|' + l.aid, l.sid, OT)) : { erro: 'sem linha' };
  ok('Gerar ordem · lote (Sem ordem) e painel do vencimento usam a mesma regra: gerar de novo o ciclo do Trator 03 devolve a OM-0235, sem OM nova', r.ids.length === 3 && r2.nada && r2.id === 'OM-0235' && /Já existe a OM-0235/.test(r2.msg) && Object.keys(g.oms).length === Object.keys(MAN0.oms).length + 3, [r, r2]);
});

// ===== Revisão adversarial de 09/10 (A1–A11 e S4): cada achado corrigido ganha proteção de regressão =====
const JOAO = g2pf('João');
caso('REV-A1 motivos da condição', () => {
  const c = S();
  const r = run(c, x => manAchRegistrar(x, { aid: 'a01', origem: 'Inspeção', comp: 'Rodado e freios', sint: 'Freio de serviço sem ação no pedal', crit: 'Alta', sug: 'Bloqueado', bloquear: true }, ZE, 'ra1'));
  ok('REV-A1 · "Registrar e bloquear" no Trator T1 já bloqueado acrescenta o motivo (2) e diz "segue bloqueado"', !r.erro && c.ativos.a01.cond === 'Bloqueado' && manMots(c.ativos.a01).length === 2 && manMots(c.ativos.a01)[1].achado === r.id && /segue bloqueado · motivo acrescentado \(2 motivos\)/.test(r.msg), [r, c.ativos.a01.condInfo]);
  const co = run(c, x => manAchCorretiva(x, r.id, OT, 'ra2')); const o2 = c.oms[co.id];
  ok('REV-A1 · a corretiva do achado novo trata o motivo dele e ganha "Teste do reparo · Freio…"', !!o2 && o2.trata && manMots(c.ativos.a01)[1].om === co.id && o2.chk.some(t => t.tipo === 'Teste' && /Teste do reparo · Freio de serviço/.test(t.t)), [co, o2 && o2.chk]);
  const t = c.oms['OM-0233'].chk.findIndex(x => x.tipo === 'Teste');
  run(c, x => manTentativa(x, 'OM-0233', t, 'Aprovado', 'manômetro 190 bar', ZE)); run(c, x => manConcluir(x, 'OM-0233', '4320', '6,5', false, {}, ZE));
  ok('REV-A1 · o comando de aptidão da OM-0233 diz que o T1 segue bloqueado', /^Encerrar o motivo da OM-0233 · Trator T1 segue bloqueado$/.test(manAptoRot(c, c.oms['OM-0233'])), manAptoRot(c, c.oms['OM-0233']));
  const ap = run(c, x => manDeclararApto(x, 'OM-0233', ZE));
  ok('REV-A1 (S1) · "Declarar apto" na OM-0233 encerra só o motivo dela: o T1 segue Bloqueado · Falta: ' + r.id + ' · ' + co.id, !ap.erro && c.ativos.a01.cond === 'Bloqueado' && manMots(c.ativos.a01).length === 1 && c.ativos.a01.condInfo.achado === r.id && ap.msg.indexOf('Falta: ' + r.id + ' · ' + co.id) >= 0 && !!c.oms['OM-0233'].aptidao && !manSelos(c, c.oms['OM-0233']).some(x => /Decidir aptidão/.test(x.t)), [ap, c.ativos.a01]);
  run(c, x => manLiberar(x, co.id, true, OT, { tempo: '2' })); run(c, x => manIniciar(x, co.id, ZE));
  const t2 = c.oms[co.id].chk.findIndex(x => x.tipo === 'Teste'); run(c, x => manTentativa(x, co.id, t2, 'Aprovado', 'freio ok na rampa', ZE));
  run(c, x => manConcluir(x, co.id, '4322', '2', false, {}, ZE)); ok('REV-A1 · o último motivo pede "Declarar Trator T1 apto"', manAptoRot(c, c.oms[co.id]) === 'Declarar Trator T1 apto', manAptoRot(c, c.oms[co.id]));
  const ap2 = run(c, x => manDeclararApto(x, co.id, ZE));
  ok('REV-A1 · resolvido o último motivo, o T1 fica Apto (sem motivo)', !ap2.erro && c.ativos.a01.cond === 'Apto' && !c.ativos.a01.condInfo, [ap2, c.ativos.a01]);
  const p = S(); const r2 = run(p, x => manAchRegistrar(x, { aid: 'a01', origem: 'Relato', comp: 'Elétrico', sint: 'Curto no painel', crit: 'Alta', sug: 'Bloqueado', bloquear: true }, OT, 'ra3'));
  ok('REV-A1 · o achado novo vira motivo da condição (antes só a mensagem dizia "bloqueado")', manMots(p.ativos.a01).some(m => m.achado === r2.id) && p.ativos.a01.condHist.length === 2, [r2, p.ativos.a01]);
  const b = S(); const rb = run(b, x => manAchRegistrar(x, { aid: 'a11', origem: 'Inspeção', comp: 'Elétrico', sint: 'Cabo do motor com isolamento rompido', crit: 'Alta', sug: 'Bloqueado', bloquear: true }, OT, 'rb1'));
  ok('REV-A1 · bloquear a Bomba do Pivô 2 restrita põe o bloqueio à frente e guarda a restrição tratada pela OM-0228', !rb.erro && b.ativos.a11.cond === 'Bloqueado' && manMots(b.ativos.a11).length === 2 && manMots(b.ativos.a11)[0].achado === rb.id && manMots(b.ativos.a11)[1].om === 'OM-0228', [rb, b.ativos.a11.condInfo]);
  run(b, x => manIniciar(x, 'OM-0228', JOAO)); run(b, x => manResp(x, 'OM-0228', 0, 'Conforme', undefined, JOAO, '3,4')); run(b, x => manResp(x, 'OM-0228', 1, 'Conforme', undefined, JOAO)); run(b, x => manResp(x, 'OM-0228', 2, 'Conforme', undefined, JOAO));
  run(b, x => manConcluir(x, 'OM-0228', '8930', '3', false, {}, JOAO)); const ab = run(b, x => manDeclararApto(x, 'OM-0228', JOAO));
  ok('REV-A1 · João (responsável técnico) encerra a restrição na OM-0228; a bomba segue Bloqueada pelo motivo novo', !ab.erro && b.ativos.a11.cond === 'Bloqueado' && manMots(b.ativos.a11).length === 1 && b.ativos.a11.condInfo.achado === rb.id, [ab, b.ativos.a11]);
  const m = S(); const nb = run(m, x => manCorretivaAtivo(x, 'a03', OT, 'rc1'));
  ok('REV-A1 · "Criar ordem corretiva" pela condição num ativo apto é recusada (nada a tratar)', /apto: nenhuma condição/.test(nb.erro || ''), nb);
});
caso('REV-A2 somar mais grave', () => {
  const c = S(); const d = { aid: 'a02', origem: 'Relato', comp: 'Hidráulico', sint: 'Mangueira estourou, óleo no motor', crit: 'Alta', sug: 'Bloqueado' };
  const r0 = run(c, x => manAchRegistrar(x, Object.assign({}, d), OT, 's0'));
  ok('REV-A2 · a repetição avisa que a ocorrência nova é mais grave', r0.nada && r0.rep === 'INSP-104' && /mais grave: somar eleva criticidade Média → Alta e sugestão Apto → Bloqueado/.test(r0.msg), r0);
  const r1 = run(c, x => manAchRegistrar(x, Object.assign({ rep: 'somar' }, d), OT, 's1')); const q = c.achados['INSP-104'];
  ok('REV-A2 (S2) · somar eleva criticidade e sugestão para a mais grave e guarda cada ocorrência (criticidade, sugestão e autor)', !r1.erro && q.crit === 'Alta' && q.sug === 'Bloqueado' && q.ocd.length === 2 && q.ocd[0].crit === 'Média' && q.ocd[1].crit === 'Alta' && q.ocd[1].sug === 'Bloqueado' && /Otávio/.test(q.ocd[1].por), [r1, q]);
  ok('REV-A2 · com a gravidade somada, a primária do achado é "Criar ordem corretiva" (não vincula à preventiva de 28/09)', manAchOpcoes(c, 'INSP-104').prim.k === 'corretiva', manAchOpcoes(c, 'INSP-104'));
  const c2 = S(); const r2 = run(c2, x => manAchRegistrar(x, Object.assign({ rep: 'somar', bloquear: true }, d), ZE, 's2'));
  ok('REV-A2 · "Somar e bloquear" (Zé, responsável técnico do Trator 02) bloqueia com o INSP-104 como motivo', !r2.erro && c2.ativos.a02.cond === 'Bloqueado' && c2.ativos.a02.condInfo.achado === 'INSP-104' && /Trator 02 bloqueado/.test(r2.msg), [r2, c2.ativos.a02]);
  const c3 = S(); const r3 = run(c3, x => manAchRegistrar(x, Object.assign({ rep: 'somar', bloquear: true }, d), ANA, 's3'));
  ok('REV-A2 · sem a competência (Ana) "Somar e bloquear" é recusado e nada grava', /responsável técnico/.test(r3.erro || '') && c3.achados['INSP-104'].oc.length === 1, r3);
});
// integração COMP (10/10): o REV-A4 falhava entre 00:00 e 06:40 (hora do relógio com a data congelada do protótipo). Relógio fixo de madrugada:
caso('REV-A4 de madrugada', () => {
  const hr0 = manHr; manHr = () => '00:40';
  try { const c = S(); run(c, x => manAbastecer(x, { aid: 'a02', tq: 'Comboio CB-01 · D-118', vol: '100', leit: '2.994', op: 'Beto', cheio: false }, OT, 'n1'));
    const f = run(c, x => manAbastecer(x, { aid: 'a02', tq: 'Comboio CB-01 · D-118', vol: '90', leit: '3.000', op: 'Beto', cheio: true }, OT, 'n2'));
    const b = c.abast.find(x => x.id === f.id); const lh = manLh(c, b);
    ok('REV-A4 às 00:40 · o lançamento novo fica depois do AB-1042 (06:40) do mesmo dia e o consumo segue (100 + 90) L ÷ 12 h = 15,8 L/h, desde o AB-1042', !!b && b.hora >= '06:40' && !!lh && lh.de === 'AB-1042' && Math.abs(lh.lh - 190 / 12) < 1e-9 && /15,8 L\/h/.test(f.msg), [b && b.hora, lh, f.msg]);
    const e = run(c, x => manEstornar(x, f.id, 'teste de madrugada', OT, 'n3')); const es = c.abast.find(x => x.tipo === 'Estorno' && x.ref === f.id);
    ok('REV-A4 às 00:40 · o estorno também fica depois do que já está gravado no dia (não antes do AB-1042 das 06:40)', !e.erro && !!es && es.hora >= '06:40' && es.hora >= b.hora, [e, es]);
  } finally { manHr = hr0; }
});
caso('REV-A3 estorno da leitura', () => {
  const c = S(); const r1 = run(c, x => manAbastecer(x, { aid: 'a02', tq: 'Sede · D-118', vol: '150', leit: '3.010', op: 'Beto', cheio: false }, OT, 'e1'));
  const r2 = run(c, x => manEstornar(x, r1.id, 'leitura digitada errada (era 2.995)', OT, 'e2')); const lt = c.leituras.find(x => x.ab === r1.id);
  ok('REV-A3 (S2) · o estorno marca a leitura do lançamento como Estornada e o Trator 02 volta a 2.988 h', !r2.erro && c.ativos.a02.leit.val === 2988 && lt && lt.qual === 'Estornada' && /volta a 2\.988 h/.test(r2.msg), [r2, c.ativos.a02.leit, lt]);
  const r3 = run(c, x => manAbastecer(x, { aid: 'a02', tq: 'Sede · D-118', vol: '150', leit: '2.995', op: 'Beto', cheio: false }, OT, 'e3'));
  ok('REV-A3 · o lançamento certo (2.995 h) entra Confirmado, sem troca de contador nem deslocar marco e últimas execuções', !r3.erro && c.ativos.a02.leit.val === 2995 && !c.ativos.a02.suspeita && c.vinc['PM-01|a02'].ult.s1.leit === 2793 && c.leituras.slice(-1)[0].qual === 'Confirmada', [r3, c.ativos.a02, c.vinc['PM-01|a02'].ult]);
});
caso('REV-A4/A10 consumo', () => {
  const c = S(); run(c, x => manAbastecer(x, { aid: 'a02', tq: 'Comboio CB-01 · D-118', vol: '100', leit: '2.994', op: 'Beto', cheio: false }, OT, 'p1'));
  const f = run(c, x => manAbastecer(x, { aid: 'a02', tq: 'Comboio CB-01 · D-118', vol: '90', leit: '3.000', op: 'Beto', cheio: true }, OT, 'p2'));
  const lh = manLh(c, c.abast.find(x => x.id === f.id));
  ok('REV-A4 (S2) · tanque cheio a tanque cheio soma o parcial do meio: (100 + 90) L ÷ 12 h = 15,8 L/h', !!lh && Math.abs(lh.lh - 190 / 12) < 1e-9 && lh.un === 'L/h' && /15,8 L\/h/.test(f.msg), [lh, f.msg]);
  const k = S(); run(k, x => manAbastecer(x, { aid: 'cb01', tq: 'Sede · D-118', vol: '200', leit: '48.300', op: 'Beto', cheio: true }, OT, 'c1'));
  const g = run(k, x => manAbastecer(x, { aid: 'cb01', tq: 'Sede · D-118', vol: '60', leit: '48.500', op: 'Beto', cheio: true }, OT, 'c2'));
  const lk = manLh(k, k.abast.find(x => x.id === g.id));
  ok('REV-A10 · o comboio (odômetro) mostra km/L: 200 km ÷ 60 L = 3,3 km/L, nunca "L/h"', !!lk && lk.un === 'km/L' && Math.abs(lk.lh - 200 / 60) < 1e-9 && /3,3 km\/L/.test(g.msg) && !/L\/h/.test(g.msg) && manConsTxt(lk) === '3,3 km/L', [lk, g.msg]);
});
caso('REV-A9 mensagem do bloqueio', () => {
  const r = run(S(), x => manCondicao(x, 'a02', 'bloquear', { motivo: 'freio' }, OT));
  ok('REV-A9 · bloquear o Trator 02 não promete impedir as O.S.: avisa a alocada (OS-0420) para o PCP', !r.erro && !/ficam impedidas/.test(r.msg) && /alocado em OS-0420: avise o PCP/.test(r.msg), r);
});
caso('REV-A11 versão do registro', () => {
  const c = S(); const rv = c.oms['OM-0234'].rv; run(c, x => manAchVincular(x, 'INSP-104', 'OM-0234', OT)); let e = '';
  try { manRv(c.oms['OM-0234'], rv); } catch (x) { e = x.message; }
  ok('REV-A11 · a OM mudou depois de aberta: o comando com a versão lida é recusado "Mudou desde que você abriu"', /Mudou desde que você abriu: OM-0234/.test(e) && c.oms['OM-0234'].rv === rv + 1, e);
});
caso('REV-S4 encerrar, autor e conflito aceito', () => {
  const c = S(); c.appConf = [{ id: 'CA-001', chave: 'z', cmd: 'retirada', args: { om: 'OM-0230' }, por: 'Zé', om: 'OM-0230', estado: 'A resolver', desc: 'x', mot: 'y' }]; c.oms['OM-0230'].conflitoApp = 1;
  run(c, x => manSobras(x, 'OM-0230', OT)); const e = run(c, x => manEncerrar(x, 'OM-0230', OT));
  ok('REV-S4 · Encerrar é recusado com registro do app "A resolver" (o fato do campo não fica para trás)', /resolver 1 registro do app/.test(e.erro || '') && c.oms['OM-0230'].etapa === 'Em conferência', e);
  const d = S(); run(d, x => manLiberar(x, 'OM-0234', true, OT, { executante: 'Zé', tempo: '5' })); run(d, x => manIniciar(x, 'OM-0234', ZE));
  ok('REV-S4 · Iniciar grava quem iniciou (Zé) além da data', /Zé/.test(d.oms['OM-0234'].iniPor || '') && d.oms['OM-0234'].ini === d.hoje, d.oms['OM-0234']);
  const g = S(); manGerarTodas(g, null, OT); run(g, x => manSolicitar(x, 'OM-0235', OT)); run(g, x => manReceber(x, 'OM-0235', OT)); run(g, x => manAchCrit(x, 'SM-0150', 'Média', OT));
  const f = S(); run(f, x => manSobras(x, 'OM-0230', OT));
  ok('REV-S4 · solicitar compra, registrar recebimento, resolver sobras e mudar criticidade gravam o autor', /Otávio/.test((g.oms['OM-0235'].sc || {}).por || '') && /Otávio/.test((g.oms['OM-0235'].sc || {}).recPor || '') && /Otávio/.test(((f.oms['OM-0230'].devPor) || {}).por || '') && /Otávio/.test(((g.achados['SM-0150'].critHist || [])[0] || {}).por || ''), [g.oms['OM-0235'].sc, f.oms['OM-0230'].devPor, g.achados['SM-0150'].critHist]);
  const m = S(); run(m, x => manLiberar(x, 'OM-0234', true, OT, { executante: 'Zé', tempo: '5' })); run(m, x => manMover(x, 'OM-0234', '2026-09-29', '', OT)); const mv = run(m, x => manMover(x, 'OM-0234', '2026-09-25', '', OT, true));
  ok('REV-S4 · "Mover mesmo assim" para dia com conflito guarda o conflito aceito (selo amarelo, não volta a vermelho)', !mv.erro && m.oms['OM-0234'].conflitoAceito === true && manSelos(m, m.oms['OM-0234']).some(x => /^Conflito aceito/.test(x.t)), [mv, manSelos(m, m.oms['OM-0234'])]);
});
caso('REV-S4 travas sem proteção (mutantes vivos M18 M21 M24 M30 M31 M36 M37 M39 M40)', () => {
  const a = S(); const t = a.oms['OM-0233'].chk.findIndex(x => x.tipo === 'Teste'); run(a, x => manTentativa(x, 'OM-0233', t, 'Aprovado', 'foto', ZE)); const m18 = run(a, x => manDeclararApto(x, 'OM-0233', ZE));
  ok('M18 · "Declarar apto" fora de Em conferência é recusado (o T1 segue bloqueado)', /só em Em conferência/.test(m18.erro || '') && a.ativos.a01.cond === 'Bloqueado', m18);
  const m21 = run(S(), x => manIncluir(x, 'OM-0234', 'Serviço', 'Trocar correia', OT));
  ok('M21 · incluir tarefa em preventiva é recusado (segue a versão do plano)', /preventiva segue a versão do plano/.test(m21.erro || ''), m21);
  const m24 = run(S(), x => manCondicao(x, 'a04', 'restringir', { motivo: 'folga', lim: 'sem implemento', ate: '' }, OT));
  ok('M24 · restringir sem prazo é recusado', /prazo da restrição/.test(m24.erro || ''), m24);
  const b = S(); run(b, x => manLiberar(x, 'OM-0234', true, OT, { executante: 'Zé', tempo: '5' })); run(b, x => manIniciar(x, 'OM-0234', ZE)); run(b, x => manResp(x, 'OM-0234', 0, 'Não feito', 'faltou filtro', ZE));
  const t0 = Object.assign({}, b.oms['OM-0234'].chk[0]); run(b, x => manResp(x, 'OM-0234', 0, 'Não feito', 'faltou o filtro no almoxarifado', undefined));
  const t1 = b.oms['OM-0234'].chk[0];
  ok('M30 · editar só o motivo não troca o autor nem a hora da resposta', t1.por === t0.por && t1.em === t0.em && /Zé/.test(t1.por) && t1.mot === 'faltou o filtro no almoxarifado', [t0, t1]);
  const m31 = run(S(), x => manResp(x, 'OM-0233', 0, 'Não feito', 'x', ANA));
  ok('M31 · quem não é o executante não responde tarefa (Ana na OM-0233 do Zé)', /Ação de Zé, executante/.test(m31.erro || ''), m31);
  const c = S(); run(c, x => manLiberar(x, 'OM-0234', true, OT, { executante: 'Zé', tempo: '5' })); run(c, x => manIniciar(x, 'OM-0234', ZE)); c.oms['OM-0234'].chk.forEach((tk, i) => run(c, x => manResp(x, 'OM-0234', i, 'Feito', undefined, ZE)));
  const m36 = run(c, x => manConcluir(x, 'OM-0234', '2995', '5', false, { 0: '5' }, ZE));
  ok('M36 · aplicar acima do planejado sem saldo livre é recusado e nada baixa', /Saldo insuficiente de Kit filtros MF 7719/.test(m36.erro || '') && c.itens['KIT-MF7719'].saldo === 2, [m36, c.itens['KIT-MF7719']]);
  const m37 = run(S(), x => manGerar(x, 'PM-03|a01', 's1', OT));
  ok('M37 · gerar ordem de vencimento em dia é recusado', /está em dia/.test(m37.erro || ''), m37);
  const d = S(); const ra = run(d, x => manAchRegistrar(x, { aid: 'a05', origem: 'Inspeção', comp: 'Motor', sint: 'Ruído', crit: 'Média', sug: 'Apto' }, OT, 'v1')); const m39 = run(d, x => manAchVincular(x, ra.id, 'OM-0230', OT));
  ok('M39 · vincular achado a OM Em conferência é recusado', /Em conferência: vincule só/.test(m39.erro || '') && d.achados[ra.id].estado === 'Sem ordem', m39);
  const m40 = run(S(), x => manEncerrar(x, 'OM-0230', OT));
  ok('M40 · encerrar com sobra a resolver é recusado', /resolver sobras/.test(m40.erro || ''), m40);
});

print(JSON.stringify(R));
