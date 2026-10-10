// CTL-3 · Frente D (aprova quem decide, R-D0..R-D5; desenho CONTROLE-01-D corrigido) · node, sem navegador. Executor: aprova_quem_decide_test.py.
// Cada caso parte do cenário inicial e grava pelo cenMudar (atômico: erro não grava nada), como a tela faz. NEGATIVO = a decisão é recusada.
// Padrão (2) adotado em 05/10/2026 (o proprietário pode mudar): o gestor aprova ajuste e consumo acima da custódia; se quem decide registrou a
// contagem, a decisão vale e fica "revisão posterior pendente" (PRD 2.1). Nenhum registro grava o nome de quem não agiu.
let nfail = 0;
function ok(t, c, got) { if (c) console.log('OK    ' + t); else { nfail++; console.log('FALHA ' + t + (got === undefined ? '' : ' · ' + JSON.stringify(got).slice(0, 400))); } }
const caso = (t, f) => { try { f(); } catch (e) { ok('ERRO no caso "' + t + '": ' + String(e.message || e), false); } };
const P = k => G2_PERFIS.find(p => p.k === k);
const ANA = P('Ana'), RUI = P('Rui'), PAULA = P('Paula'), CAIO = P('Caio'), ZE = P('Zé');
const ini = () => { cenReset(); };
const G = () => cenGet();
const disp = k => cenDisp(G().lotes[k]);

console.log('— R-D0 · perfil de demonstração (g2lib.js) e decisão com papel');
caso('perfil', () => {
  ok('sem escolha: Ana (padrão de hoje, "Ana · Gestora")', g2perfil().k === 'Ana', g2perfil().k);
  __ls['safrion.perfilDemo'] = 'Rui'; ok('escolha gravada no navegador: Rui', g2perfil().k === 'Rui');
  __ls['safrion.perfilDemo'] = 'Xyz'; ok('perfil desconhecido volta a Ana', g2perfil().k === 'Ana');
  delete __ls['safrion.perfilDemo'];
  ok('quem aprova ajuste, quarentena e excedente: Ana (gestora)', g2quem('gestor') === 'Ana (gestora)', g2quem('gestor'));
  ok('agrônomo: Ana (agrônoma), o mesmo rótulo das telas da O.S. (OS_AGRO)', g2quem('agronomo') === 'Ana (agrônoma)' && g2quem('agronomo') === OS_AGRO, g2quem('agronomo'));
  ok('dispensa: os dois papéis (só Ana)', g2quem(['gestor', 'agronomo']) === 'Ana (gestora e agrônoma)' && !g2papel(CAIO, ['gestor', 'agronomo']) && g2papel(ANA, ['gestor', 'agronomo']), g2quem(['gestor', 'agronomo']));
  ok('almoxarifes: Rui ou Paula', g2quem('almoxarife') === 'Rui (almoxarife) ou Paula (almoxarife)', g2quem('almoxarife'));
  ok('mesma pessoa pelo nome (Ana × "Ana (gestora)")', g2mesma('Ana', 'Ana (gestora)') && !g2mesma('Ana', 'Paula (almoxarife)') && !g2mesma('', ''));
  ok('papel vem do cadastro: objeto forjado {k:"Caio", papeis:{gestor}} não vira gestor; chave "Ana" vale', !g2papel({ k: 'Caio', papeis: { gestor: 'gestora' } }, 'gestor') && g2papel('Ana', 'gestor') && !g2papel({ k: 'Xyz', papeis: { gestor: 'g' } }, 'gestor'));
  const self = { state: {}, setState(o) { Object.assign(this.state, o); } }; const v = {}; g2navvals(self, v, []);
  ok('menu lateral: seletor com todos os perfis do cadastro (Otávio e João da manutenção; Igor e Marta do beneficiamento), Ana marcada', v.perfil_k === 'Ana' && (v.perfil_opts || []).length === G2_PERFIS.length && ['Otávio', 'João', 'Igor', 'Marta'].every(k => (v.perfil_opts || []).some(o => o.v === k)), [v.perfil_k, (v.perfil_opts || []).map(o => o.v)]);
  self.g2perfilFecha = { pa: null }; self.state.pa = { id: 'OS-0430', fn: 'liberar' };   // confirmação aberta pela Ana
  v.perfil_set({ target: { value: 'Caio' } });
  ok('trocar para Caio grava e avisa que não é segurança', __ls['safrion.perfilDemo'] === 'Caio' && g2perfil().k === 'Caio' && /Caio · PCP \(não é segurança de acesso\)/.test(self.state.g2toast || ''), self.state.g2toast);
  ok('revisão do CTL-3, achado 1: trocar o perfil fecha o que a tela declarou em g2perfilFecha (a confirmação aberta pela Ana)', self.state.pa === null, self.state.pa);
  delete __ls['safrion.perfilDemo']; G2_PERFIL_MEM = '';
});

console.log('\n— R-D1 · ajuste de estoque (INV-2611: Glifosato 480 G26-14, sistema 1.200 L, contado 1.180 L por Paula)');
const KG = 'Glifosato 480|G26-14';
const contar = (n, quem, ator) => cenMudar(null, c => estContar(c, 'INV-2611', KG, n, quem, 'bombona avariada', ator));
for (const [ator, nome] of [[RUI, 'Rui (almoxarife)'], [PAULA, 'Paula (almoxarife), quem contou'], [CAIO, 'Caio (PCP)'], [undefined, 'sem ator'], [{ k: 'Caio', papeis: { gestor: 'gestora' } }, 'Caio forjado como gestor']]) caso('ajuste ' + nome, () => {
  ini(); contar(1180, 'Paula (almoxarife)', RUI); const r = cenMudar(null, c => estAprovar(c, 'INV-2611', ator));
  ok('NEGATIVO ' + nome + ' não aprova; físico segue 1.200 L, ajuste aguardando e nenhum movimento de ajuste',
    r.erro === 'Aprovar o ajuste INV-2611: decisão de Ana (gestora). Nada foi alterado.' && G().lotes[KG].fisico === 1200 && G().ajustes[0].estado === 'Aguardando gestor' && !G().movs.some(m => m.tipo === 'ajuste'), r.erro || r.msg);
});
caso('ajuste Ana', () => {
  ini(); contar(1180, 'Paula (almoxarife)', RUI);
  const r = cenMudar(null, c => estAprovar(c, 'INV-2611', ANA)); const c = G(); const aj = c.ajustes[0]; const m = c.movs.find(x => x.tipo === 'ajuste');
  ok('Ana (gestora) aprova: físico 1.200 → 1.180 L', c.lotes[KG].fisico === 1180, c.lotes[KG].fisico);
  ok('ajuste grava aprovador, hora, contador e quem registrou (Rui); sem revisão posterior', aj.por === 'Ana (gestora)' && /^\d\d:\d\d$/.test(aj.em || '') && aj.contador === 'Paula (almoxarife)' && aj.reg === 'Rui (almoxarife)' && aj.rev === '', aj);
  ok('movimento de ajuste −20 L por Ana (gestora), documento INV-2611', m && m.quem === 'Ana (gestora)' && m.qtd === -20 && m.doc === 'INV-2611', m);
  ok('trilha: "ajuste de inventário INV-2611 aprovado por Ana (gestora): −20 L"', m && emovTxt(m) === 'ajuste de inventário INV-2611 aprovado por Ana (gestora): −20 L', m && emovTxt(m));
  ok('mensagem da tela', r.msg === 'Ajuste INV-2611 (AJ-71) aprovado por Ana (gestora): −20 L no lote G26-14. Físico 1.200 L → 1.180 L.', r.msg || r.erro);
  const r2 = cenMudar(null, c => estAprovar(c, 'INV-2611', ANA));
  ok('NEGATIVO repetir a aprovação não aplica de novo (1.180 L)', r2.erro === 'Ajuste INV-2611 já aprovado · nada aplicado de novo.' && G().lotes[KG].fisico === 1180, r2.erro);
});
caso('acúmulo', () => {
  ini(); contar(1185, 'Paula (almoxarife)', ANA);
  const r = cenMudar(null, c => estAprovar(c, 'INV-2611', ANA)); const c = G(); const aj = c.ajustes[0]; const m = c.movs.find(x => x.tipo === 'ajuste');
  ok('acúmulo: Ana registra 1.185 L (declarando Paula) e aprova: a decisão vale (físico 1.185 L)', c.lotes[KG].fisico === 1185 && aj.estado === 'Aprovado' && aj.reg === 'Ana (gestora)', [c.lotes[KG].fisico, aj.reg]);
  ok('acúmulo grava a revisão posterior no ajuste e no movimento (declarar outro contador não esconde o acúmulo)', aj.rev === 'revisão posterior pendente (Ana registrou a contagem e decidiu)' && m && m.rev === aj.rev, aj.rev);
  ok('acúmulo aparece na mensagem e na trilha', /Fica revisão posterior pendente \(Ana registrou a contagem e decidiu\)\.$/.test(r.msg || '') && m && / · revisão posterior pendente/.test(emovTxt(m)), r.msg || r.erro);
});
caso('Rui registra, Ana aprova', () => {
  ini(); contar(1180, 'Paula (almoxarife)', RUI); cenMudar(null, c => estAprovar(c, 'INV-2611', ANA)); const aj = G().ajustes[0];
  ok('Rui registra a contagem de Paula, Ana aprova: sem revisão posterior', aj.reg === 'Rui (almoxarife)' && aj.rev === '' && G().lotes[KG].fisico === 1180, [aj.reg, aj.rev]);
});
caso('recontar', () => {
  ini(); contar(1180, 'Paula (almoxarife)', ANA); cenMudar(null, c => estRecontar(c, 'INV-2611'));
  const rec = einvRec(G(), 'INV-2611'); ok('recontar limpa quem registrou e passa a outro contador', rec.reg === '' && rec.contador === 'Rui (almoxarife)', [rec.reg, rec.contador]);
  ini(); contar(1180, 'Paula (almoxarife)', RUI); const r = cenMudar(null, c => estRecontar(c, 'INV-2611'));
  ok('Recontar (sem papel de gestor) recusa o ajuste pendente sem mudar o saldo', !r.erro && G().ajustes[0].estado === 'Recusado' && G().lotes[KG].fisico === 1200, r);
});
caso('INV-2609', () => {
  ini(); const K = 'MAP 11-52|M26-07'; cenMudar(null, c => estCausa(c, 'INV-2609', 'Sacaria rasgada na pilha 3'));
  const rn = cenMudar(null, c => estAprovar(c, 'INV-2609', RUI));
  ok('NEGATIVO INV-2609 (contagem de base): Rui não aprova; nenhum ajuste criado; MAP segue 90.000 kg', !!rn.erro && G().lotes[K].fisico === 90000 && !(G().ajustes || []).length, [rn.erro, (G().ajustes || []).length]);
  cenMudar(null, c => estAprovar(c, 'INV-2609', ANA)); const aj = G().ajustes[0];
  ok('INV-2609: Ana aprova −600 kg, MAP 90.000 → 89.400 kg; contador Rui; sem revisão', G().lotes[K].fisico === 89400 && aj.contador === 'Rui (almoxarife)' && aj.rev === '', [G().lotes[K].fisico, aj.contador, aj.rev]);
});
ok('contadores sem mudança (est_fix1_test.py:56)', JSON.stringify(E2.contadores) === JSON.stringify(['Paula (almoxarife)', 'Rui (almoxarife)']), E2.contadores);

console.log('\n— R-D2 · quarentena (KCl 60% K26-11: 10.000 kg em quarentena, disponível 50.000 kg)');
const KK = 'KCl 60%|K26-11';
for (const [ator, nome] of [[RUI, 'Rui (almoxarife)'], [PAULA, 'Paula (almoxarife)'], [CAIO, 'Caio (PCP)'], [undefined, 'sem ator']]) caso('quarentena ' + nome, () => {
  ini(); const r = cenMudar(null, c => cenLiberarQuarentena(c, KK, 'LAB-0917', ator));
  ok('NEGATIVO ' + nome + ' não libera, mesmo com laudo; disponível segue 50.000 kg', r.erro === 'Liberar a quarentena do lote K26-11: decisão de Ana (gestora). Nada foi alterado.' && G().lotes[KK].quarentena === 10000 && disp(KK) === 50000, r.erro || r.msg);
});
for (const laudo of ['', '   ', undefined]) caso('laudo ' + JSON.stringify(laudo), () => {
  ini(); const r = cenMudar(null, c => cenLiberarQuarentena(c, KK, laudo, ANA));
  ok('NEGATIVO Ana sem laudo (' + JSON.stringify(laudo) + '): continua bloqueado', r.erro === 'Informe o nº do laudo ou relatório de inspeção do lote K26-11. Sem laudo o lote continua bloqueado.' && G().lotes[KK].quarentena === 10000, r.erro || r.msg);
});
caso('quarentena Ana', () => {
  ini(); const r = cenMudar(null, c => cenLiberarQuarentena(c, KK, ' LAB-0917 ', ANA)); const m = G().movs[G().movs.length - 1];
  ok('Ana com o laudo LAB-0917: quarentena 10.000 → 0; disponível 50.000 → 60.000 kg', G().lotes[KK].quarentena === 0 && disp(KK) === 60000, disp(KK));
  ok('movimento grava laudo, quem e quantidade', m.tipo === 'inspecao' && m.doc === 'LAB-0917' && m.quem === 'Ana (gestora)' && !('rev' in m) && m.qtd === 10000, m);
  ok('trilha com laudo e quem', emovTxt(m) === 'quarentena liberada com o laudo LAB-0917 por Ana (gestora): 10.000 kg passam a disponível', emovTxt(m));
  ok('mensagem', r.msg === '10.000 kg do lote K26-11 liberados com o laudo LAB-0917 por Ana (gestora).', r.msg || r.erro);
  const r2 = cenMudar(null, c => cenLiberarQuarentena(c, KK, 'LAB-0917', ANA));
  ok('NEGATIVO repetir não soma de novo (60.000 kg)', r2.erro === 'Nada bloqueado neste lote.' && disp(KK) === 60000, r2.erro);
});
caso('devolução bloqueada', () => {
  ini(); const KF = 'Fungicida A|F26-02'; cenMudar(null, c => cenDevolver(c, 'REQ-035', 'Fungicida A', 10, false, RUI)); const l = G().lotes[KF];
  ok('devolução bloqueada de 10 L (REQ-035): F26-02 físico 555, quarentena 10, disponível 480 L', l.fisico === 555 && l.quarentena === 10 && disp(KF) === 480, [l.fisico, l.quarentena, disp(KF)]);
  const rn = cenMudar(null, c => cenLiberarQuarentena(c, KF, 'INSP-0042', RUI)); ok('NEGATIVO Rui, que recebeu a devolução, não libera (480 L)', !!rn.erro && disp(KF) === 480, rn.erro || rn.msg);
  cenMudar(null, c => cenLiberarQuarentena(c, KF, 'INSP-0042', ANA)); const m = G().movs[G().movs.length - 1];
  ok('Ana libera com INSP-0042: disponível 480 → 490 L', disp(KF) === 490 && !('rev' in m), [disp(KF), m.rev]);
});

console.log('\n— R-D3 · dispensa de saldo (OS-0421: 350 ha, realizado 190, saldo 160; limite 20 % = 70 ha)');
for (const [ator, nome] of [[CAIO, 'Caio (PCP)'], [RUI, 'Rui (almoxarife)'], [ZE, 'Zé (mecânico)'], [undefined, 'sem ator']]) caso('dispensa ' + nome, () => {
  ini(); const r = cenMudar(null, c => osc_dispensar(c, 'OS-0421', 40, 'faixa já tratada', ator)); const o = G().ordens['OS-0421'];
  ok('NEGATIVO ' + nome + ' não dispensa; saldo segue 160 ha', r.erro === 'Dispensar saldo da OS-0421: decisão de Ana (gestora e agrônoma). Nada foi alterado.' && o.saldo === 160 && !(o.osc && o.osc.disp), r.erro || r.msg);
});
caso('dispensa Ana', () => {
  ini(); const r = cenMudar(null, c => osc_dispensar(c, 'OS-0421', 40, 'faixa já tratada', ANA)); const o = G().ordens['OS-0421'];
  ok('Ana (gestora e agrônoma) dispensa 40 ha: saldo 160 → 120; realizado 190 preservado', o.saldo === 120 && o.realizado === 190 && o.osc.disp === 40, [o.saldo, o.realizado, o.osc && o.osc.disp]);
  ok('grava quem decidiu e a hora', o.osc.dispPor === 'Ana (gestora e agrônoma)' && /^\d\d:\d\d$/.test(o.osc.dispEm || ''), o.osc);
  ok('texto da ordem nomeia a decisão e a validação', /^Saldo de 40 ha dispensado: faixa já tratada · decisão gerencial e validação agronômica de Ana \(gestora e agrônoma\) às \d\d:\d\d\. Realizado de 190 ha preservado\.$/.test(o.osc.cond || ''), o.osc.cond);
  ok('mensagem', r.msg === 'Dispensados 40 ha da OS-0421 por Ana (gestora e agrônoma) · realizado 190 ha preservado · saldo 120 ha.', r.msg || r.erro);
});
caso('alçada 20 %', () => {
  ini(); const r = cenMudar(null, c => osc_dispensar(c, 'OS-0421', 71, 'x', ANA));
  ok('NEGATIVO comando direto com 71 ha (> 70 ha = 20 % de 350): exige Direção; saldo segue 160 (antes: passava)', r.erro === '71 ha = 20,3 % acima de 20 % · exige Direção.' && G().ordens['OS-0421'].saldo === 160, [r.erro, G().ordens['OS-0421'].saldo]);
  cenMudar(null, c => osc_dispensar(c, 'OS-0421', 40, 'x', ANA)); const r2 = cenMudar(null, c => osc_dispensar(c, 'OS-0421', 31, 'y', ANA));
  ok('NEGATIVO acumulado 40 + 31 = 71 ha: exige Direção; saldo segue 120', r2.erro === '71 ha = 20,3 % acima de 20 % · exige Direção.' && G().ordens['OS-0421'].saldo === 120, [r2.erro, G().ordens['OS-0421'].saldo]);
  const r3 = cenMudar(null, c => osc_dispensar(c, 'OS-0421', 30, 'z', ANA));
  ok('limite exato 40 + 30 = 70 ha: aceita (saldo 90)', !r3.erro && G().ordens['OS-0421'].saldo === 90 && G().ordens['OS-0421'].osc.disp === 70, [r3.erro, G().ordens['OS-0421'].saldo]);
  ini(); const r4 = cenMudar(null, c => osc_dispensar(c, 'OS-0424', 10, 'x', ANA)); ok('NEGATIVO OS-0424 (Liberadas): não dispensa', r4.erro === 'OS-0424 não está em execução.', r4.erro || r4.msg);
});

console.log('\n— R-D5 · consumo acima da custódia (OS-0421 · REQ-035 · Fungicida A: custódia 65 L; lote F26-02 físico 545 L)');
const KF = 'Fungicida A|F26-02';
function relato(q) { ini(); cenMudar(null, c => cenIniciarTurno(c, 'OS-0421')); cenMudar(null, c => cenFecharTurno(c, 10, 2, { 'Fungicida A': q }, '', [])); return G().confs[0]; }
for (const [ator, nome] of [[RUI, 'Rui (almoxarife)'], [CAIO, 'Caio (PCP)'], [undefined, 'sem ator (chamada direta)']]) caso('excedente ' + nome, () => {
  const k = relato(85); const r = cenMudar(null, c => cenConciliar(c, k.id, true, undefined, ator));
  ok('NEGATIVO ' + nome + ' não aceita os 20 L acima da custódia; F26-02 segue 545 L (antes: baixava para 525 e gravava Rui)',
    r.erro === 'Aceitar 20 L acima da custódia (CC-301): decisão de Ana (gestora). Nada foi alterado.' && G().lotes[KF].fisico === 545 && G().confs[0].estado === 'Em conferência', r.erro || r.msg);
});
caso('excedente Ana', () => {
  const k = relato(85); const r = cenMudar(null, c => cenConciliar(c, k.id, true, undefined, ANA)); const c = G(); const ms = c.movs.slice(-2);
  ok('Ana (gestora) aceita: F26-02 545 → 525 L; caso Aceito por Ana (gestora)', r.msg === 'CC-301 aceito: Fungicida A 85 L baixados na OS-0421 · 20 L regularizados do lote F26-02.' && c.lotes[KF].fisico === 525 && c.confs[0].por === 'Ana (gestora)', [r.msg || r.erro, c.lotes[KF].fisico, c.confs[0].por]);
  ok('movimentos com quem decidiu', ms[0].quem === 'Ana (gestora) → Marcos · regularização CC-301' && ms[1].quem === 'Ana (gestora) · aceite CC-301', ms.map(m => m.quem));
});
caso('recusa e coberto', () => {
  const k = relato(85); const r = cenMudar(null, c => cenConciliar(c, k.id, false, 'registro sem fato físico', RUI));
  ok('Rui recusa o relato (sem efeito no saldo): vale e grava Rui', !r.erro && G().confs[0].estado === 'Recusado' && G().confs[0].por === 'Rui (almoxarife)' && G().lotes[KF].fisico === 545, [r.erro, G().confs[0].por]);
  const k2 = relato(85); const r2 = cenMudar(null, c => cenConciliar(c, k2.id, false, 'registro sem fato físico'));
  ok('NEGATIVO recusa sem perfil de quem age: recusada e nada gravado (antes: gravava "Rui (almoxarife)" sem Rui agir)', r2.erro === 'Recusar o relato CC-301: sem o perfil de quem age. Nada foi alterado.' && G().confs[0].estado === 'Em conferência' && !G().confs[0].por, r2.erro || r2.msg);
  const k3 = relato(75); cenMudar(null, c => cenEntregar(c, 'REQ-035', 'Fungicida A', 10, undefined, RUI)); const r3 = cenMudar(null, c => cenConciliar(c, k3.id, true, undefined, RUI));
  ok('coberto pela custódia (nada sai do lote): Rui aceita e fica gravado Rui', !r3.erro && G().confs[0].estado === 'Aceito' && G().confs[0].decisao === 'coberto pela custódia' && G().confs[0].por === 'Rui (almoxarife)', [r3.erro, G().confs[0].decisao]);
});

console.log('\n— R-D4 · checklist da manutenção (OM-0234 Revisão 250 h, 5 tarefas)');
ok('Manutenção (MA) sem a ação "Marcar pendentes como feitas" (pan_todas removido)', MA04_SRC_TODAS === '', MA04_SRC_TODAS.slice(0, 60));
caso('checklist', () => {   // PCM simplificado (05/10, D-33/D-18): só o executante responde; horas de oficina obrigatórias; "Falta: …" com a tarefa
  let c = manClone(MAN0); const id = 'OM-0234'; manLiberar(c, id, true); manIniciar(c, id); const o = c.oms[id];
  manResp(c, id, 0, 'Feito', undefined, ZE); manResp(c, id, 1, 'Feito', undefined, ZE); manResp(c, id, 3, 'Feito', undefined, ZE);
  let ea = ''; try { manResp(c, id, 2, 'Feito', undefined, ANA); } catch (x) { ea = x.message; }
  ok('NEGATIVO Ana (gestora) não responde a tarefa do Zé (executante): recusado e nada gravado', /^Ação de Zé, executante/.test(ea) && !o.chk[2].r, ea);
  manResp(c, id, 2, 'Feito', undefined, ZE);
  ok('cada resposta grava quem (Zé (mecânico)) e a hora', o.chk[0].por === 'Zé (mecânico)' && /^\d\d:\d\d$/.test(o.chk[0].em || '') && o.chk[2].por === 'Zé (mecânico)', o.chk.map(t => t.por));
  let e = ''; try { manConcluir(c, id, String(c.ativos[o.aid].leit.val + 8), '5', false, {}); } catch (x) { e = x.message; }
  ok('NEGATIVO 4 de 5 respondidas: não conclui', e === 'Falta: responder “Lubrificar pontos de graxa”.' && o.etapa === 'Em execução', e);
  manResp(c, id, 4, 'Não feito', undefined, ZE); e = ''; try { manConcluir(c, id, String(c.ativos[o.aid].leit.val + 8), '5', false, {}); } catch (x) { e = x.message; }
  ok('NEGATIVO "Não feito" sem motivo: não conclui', e === 'Falta: motivo de “Lubrificar pontos de graxa”.', e);
  manResp(c, id, 1, '', undefined, ZE); ok('desmarcar apaga quem e hora (resposta volta a pendente)', o.chk[1].r === '' && o.chk[1].por === '' && o.chk[1].em === '', o.chk[1]);
  manResp(c, id, 1, 'Feito', undefined, ZE); manResp(c, id, 4, 'Feito', undefined, ZE);
  const r = manConcluir(c, id, String(c.ativos[o.aid].leit.val + 8), '5', false, {}); ok('respondidas as 5, uma a uma: conclui e vai Em conferência', o.etapa === 'Em conferência' && /^OM-0234 em conferência/.test(r.msg), r.msg);
});

console.log('\n— Revisão do CTL-3 (achados 2, 3, 4, 6 e 7)');
// achado 3 · CMD-50: aceitar o consumo coberto pela custódia baixa a custódia como consumo: almoxarife ou gestor (recusar segue aberto, com autor)
const coberto = () => { const k = relato(75); cenMudar(null, c => cenEntregar(c, 'REQ-035', 'Fungicida A', 10, undefined, RUI)); return k; };   // custódia 65 + 10 = 75 L
for (const [ator, nome] of [[CAIO, 'Caio (PCP)'], [ZE, 'Zé (mecânico)'], [undefined, 'sem ator'], [{ k: 'Caio', papeis: { almoxarife: 'almoxarife' } }, 'Caio forjado como almoxarife']]) caso('coberto ' + nome, () => {
  const k = coberto(); const it0 = Object.assign({}, G().reqs['REQ-035'].itens[0]); const r = cenMudar(null, c => cenConciliar(c, k.id, true, undefined, ator)); const it = G().reqs['REQ-035'].itens[0];
  ok('NEGATIVO ' + nome + ' não aceita os 75 L cobertos pela custódia: custódia 75 L e consumido 95 L sem mudança, caso Em conferência (antes: aceitava, baixava 75 → 0 e gravava quem clicou)',
    r.erro === 'Aceitar o relato CC-301: decisão de Ana (gestora) ou Rui (almoxarife) ou Paula (almoxarife). Nada foi alterado.' && it0.custodia === 75 && it.custodia === 75 && it.consumido === it0.consumido && G().confs[0].estado === 'Em conferência' && !G().confs[0].por, r.erro || r.msg);
});
for (const [ator, nome, q] of [[PAULA, 'Paula', 'Paula (almoxarife)'], [ANA, 'Ana', 'Ana (gestora)']]) caso('coberto ' + nome, () => {
  const k = coberto(); const r = cenMudar(null, c => cenConciliar(c, k.id, true, undefined, ator)); const it = G().reqs['REQ-035'].itens[0];
  ok(nome + ' aceita o coberto pela custódia: custódia 75 → 0, consumido 95 → 170, caso Aceito por ' + q, !r.erro && it.custodia === 0 && it.consumido === 170 && G().confs[0].estado === 'Aceito' && G().confs[0].por === q, [r.erro, it.custodia, it.consumido, G().confs[0].por]);
});
caso('recusa aberta', () => { const k = relato(85); const r = cenMudar(null, c => cenConciliar(c, k.id, false, 'registro sem fato físico', ZE));
  ok('Recusar relato segue aberto (não mexe no saldo): Zé recusa e fica gravado Zé (mecânico)', !r.erro && G().confs[0].estado === 'Recusado' && G().confs[0].por === 'Zé (mecânico)' && G().lotes[KF].fisico === 545, [r.erro, G().confs[0].por]); });
// achado 4 · entrega, devolução e recebimento gravam quem agiu (perfil), nunca "Rui (almoxarife)" fixo; CMD-46 exige o gestor (AL-04) e grava quem cancelou
caso('entrega e devolução', () => {
  ini(); cenMudar(null, c => osc_liberar(c, 'OS-0430', false, '', ANA)); const rq = G().ordens['OS-0430'].req; const last = () => G().movs[G().movs.length - 1];
  const r1 = cenMudar(null, c => cenEntregar(c, rq, 'Glifosato 480', 100, 'Marcos', PAULA)); const m1 = last();
  ok('Paula entrega 100 L de Glifosato 480: o movimento grava "Paula (almoxarife) → Marcos" (antes: "Rui (almoxarife) → Marcos" com qualquer perfil)', !r1.erro && m1.tipo === 'entrega' && m1.quem === 'Paula (almoxarife) → Marcos', [r1.erro, m1.quem]);
  const r2 = cenMudar(null, c => cenDevolver(c, rq, 'Glifosato 480', 20, true, PAULA)); const m2 = last();
  ok('Paula recebe a devolução de 20 L: o movimento grava "Paula (almoxarife)"', !r2.erro && m2.tipo === 'devolucao' && m2.quem === 'Paula (almoxarife)', [r2.erro, m2.quem]);
  const r3 = cenMudar(null, c => cenEntregar(c, rq, 'Glifosato 480', 10, 'Marcos', CAIO)); const m3 = last();
  ok('entrega segue aberta e grava quem agiu: "Caio (PCP) → Marcos"', !r3.erro && m3.quem === 'Caio (PCP) → Marcos', [r3.erro, m3.quem]);
  const n = G().movs.length, it = JSON.stringify(G().reqs[rq].itens[0]);
  const r4 = cenMudar(null, c => cenEntregar(c, rq, 'Glifosato 480', 10, 'Marcos')), r5 = cenMudar(null, c => cenDevolver(c, rq, 'Glifosato 480', 5, true));
  ok('NEGATIVO entrega e devolução sem o perfil de quem age: recusadas e nada gravado',
    r4.erro === 'Entregar Glifosato 480 da ' + rq + ': sem o perfil de quem age. Nada foi alterado.' && r5.erro === 'Receber a devolução de Glifosato 480 da ' + rq + ': sem o perfil de quem age. Nada foi alterado.'
    && G().movs.length === n && JSON.stringify(G().reqs[rq].itens[0]) === it, [r4.erro, r5.erro]);
  const r6 = cenMudar(null, c => cenReceber(c, 'Ureia 45%', 'U26-01', 100, 'kg', 'Galpão 1', '12/2027', 'NF-9001', true, PAULA)); const m6 = last();
  const r7 = cenMudar(null, c => cenReceber(c, 'Ureia 45%', 'U26-01', 100, 'kg', 'Galpão 1', '12/2027', 'NF-9002', true));
  ok('recebimento grava quem conferiu ("Paula (almoxarife)"); sem perfil é recusado e o lote fica com 100 kg', !r6.erro && m6.tipo === 'recebimento-nf' && m6.quem === 'Paula (almoxarife)'
    && r7.erro === 'Receber Ureia 45% (NF-9002): sem o perfil de quem age. Nada foi alterado.' && G().lotes['Ureia 45%|U26-01'].fisico === 100, [r6.erro, m6.quem, r7.erro]);
});
caso('quarentena com acúmulo', () => {
  const KU = 'Ureia 45%|U26-09'; const rec = (ator, doc) => cenMudar(null, c => cenReceber(c, 'Ureia 45%', 'U26-09', 500, 'kg', 'Galpão 1', '12/2027', doc, false, ator));
  ini(); rec(ANA, 'NF-7001'); const r = cenMudar(null, c => cenLiberarQuarentena(c, KU, 'LAB-1', ANA)); const m = G().movs[G().movs.length - 1];
  ok('Ana registra o recebimento bloqueado e libera a quarentena: a decisão vale e fica revisão posterior (padrão 2; antes a entrada gravava "Rui (almoxarife)" e o acúmulo não aparecia)',
    !r.erro && G().lotes[KU].quarentena === 0 && m.rev === 'revisão posterior pendente (Ana registrou a entrada bloqueada e decidiu)' && / Fica revisão posterior pendente \(Ana registrou a entrada bloqueada e decidiu\)\.$/.test(r.msg)
    && / · revisão posterior pendente/.test(emovTxt(m)), [r.erro || r.msg, m.rev]);
  ini(); rec(RUI, 'NF-7002'); const r2 = cenMudar(null, c => cenLiberarQuarentena(c, KU, 'LAB-2', ANA)); const m2 = G().movs[G().movs.length - 1];
  ok('Rui recebe bloqueado e Ana libera: sem revisão posterior', !r2.erro && !('rev' in m2) && !/revisão/.test(r2.msg), [r2.erro || r2.msg, m2.rev]);
});
for (const [ator, nome] of [[CAIO, 'Caio (PCP)'], [RUI, 'Rui (almoxarife)'], [undefined, 'sem ator']]) caso('cancelar ' + nome, () => {
  ini(); cenMudar(null, c => osc_liberar(c, 'OS-0430', false, '', ANA)); const rev = G().rev;
  const r = cenMudar(null, c => osc_cancelar(c, 'OS-0430', 'teste', ['', '', ''], ator)); const o = G().ordens['OS-0430'];
  ok('NEGATIVO ' + nome + ' não cancela a OS-0430 aprovada e liberada (CMD-46, AL-04): segue Liberadas, 320 L reservados (antes: cancelava sem autor e soltava a reserva)',
    r.erro === 'Cancelar a OS-0430 sem execução (CMD-46): decisão de Ana (gestora). Nada foi alterado.' && o.etapa === 'Liberadas' && G().lotes[KG].reservado === 320 && G().rev === rev, r.erro || r.msg);
});
caso('cancelar Ana', () => {
  ini(); cenMudar(null, c => osc_liberar(c, 'OS-0430', false, '', ANA)); const r = cenMudar(null, c => osc_cancelar(c, 'OS-0430', 'plantio adiado', ['', 'Reserva liberada no Estoque.', ''], ANA)); const o = G().ordens['OS-0430'];
  ok('Ana (gestora) cancela: Canceladas, reserva solta, e grava quem cancelou e a hora', !r.erro && o.etapa === 'Canceladas' && G().lotes[KG].reservado === 0 && o.osc.canPor === 'Ana (gestora)' && /^\d\d:\d\d$/.test(o.osc.canEm || '')
    && /^Cancelada sem execução por Ana \(gestora\) às \d\d:\d\d: plantio adiado\. Reserva liberada no Estoque\.$/.test(o.osc.cond || '') && r.msg === 'OS-0430 cancelada sem execução. Reserva liberada no Estoque. Cancelada por Ana (gestora).', [r.erro || r.msg, o.osc]);
});
// achado 6 · papéis em pessoas diferentes (cadastro injetado e retirado): a dispensa exige os DOIS papéis (g2papel com lista = todos)
caso('dispensa com papéis separados', () => {
  const n0 = G2_PERFIS.length; G2_PERFIS.push({ k: 'Beto', t: 'Beto · Agrônomo', papeis: { agronomo: 'agrônomo' } }, { k: 'Gil', t: 'Gil · Gestor', papeis: { gestor: 'gestor' } });
  try { for (const k of ['Beto', 'Gil']) { ini(); const r = cenMudar(null, c => osc_dispensar(c, 'OS-0421', 40, 'x', k)); const o = G().ordens['OS-0421'];
      ok('NEGATIVO ' + k + ' (só ' + (k === 'Beto' ? 'agrônomo' : 'gestor') + ') não dispensa: exige os dois papéis; saldo segue 160 ha', r.erro === 'Dispensar saldo da OS-0421: decisão de Ana (gestora e agrônoma). Nada foi alterado.' && o.saldo === 160 && !(o.osc && o.osc.disp), r.erro || r.msg); } }
  finally { G2_PERFIS.splice(n0); }
  ok('cadastro restaurado: ' + n0 + ' perfis', G2_PERFIS.length === n0 && !G2_PERFIS.some(p => p.k === 'Beto' || p.k === 'Gil'));   /* sem número fixo: outra frente pode acrescentar perfil (revisão BEN, S4) */
});
// achado 2 · checklist: editar o motivo não troca o autor da resposta
caso('motivo editado', () => {   // PCM simplificado (05/10, D-33): só o executante edita; o autor da resposta segue de quem respondeu
  let c = manClone(MAN0); const id = 'OM-0234'; manLiberar(c, id, true); manIniciar(c, id); const t = c.oms[id].chk[4];
  manResp(c, id, 4, 'Não feito', 'sem graxa', ZE); const em = t.em;
  let ea = ''; try { manResp(c, id, 4, 'Não feito', 'sem graxa no almoxarifado', ANA); } catch (x) { ea = x.message; }
  ok('Ana (gestora) não edita o motivo da resposta do Zé (não é a executante): recusado; resposta e motivo seguem de Zé (antes: o autor virava Ana)',
    /^Ação de Zé, executante/.test(ea) && t.r === 'Não feito' && t.por === 'Zé (mecânico)' && t.em === em && t.mot === 'sem graxa', [ea, t]);
  manResp(c, id, 4, 'Não feito', 'sem graxa no almoxarifado', ZE);
  ok('editar só o motivo não troca o autor da resposta; a edição fica à parte, com quem e hora', t.r === 'Não feito' && t.por === 'Zé (mecânico)' && t.em === em && t.mot === 'sem graxa no almoxarifado' && t.motPor === 'Zé (mecânico)' && /^\d\d:\d\d$/.test(t.motEm || ''), t);
  manResp(c, id, 3, 'Não feito', undefined, ZE); manResp(c, id, 3, 'Não feito', 'peça em falta', ZE); const t3 = c.oms[id].chk[3];
  ok('o próprio Zé escreve o motivo: autor e editor iguais', t3.por === 'Zé (mecânico)' && t3.motPor === 'Zé (mecânico)', t3);
});
// achado 7 · com excedente, o texto diz quem confere e quem aceita o excedente (o excedente é do gestor, padrão 2)
caso('textos de quem concilia', () => {
  ini(); cenMudar(null, c => cenIniciarTurno(c, 'OS-0421')); const r = cenMudar(null, c => cenFecharTurno(c, 10, 2, { 'Fungicida A': 85 }, '', []));
  ok('fechar o turno com 85 L (65 L em custódia): "· Rui (almoxarife) confere; Ana (gestora) aceita o excedente." (antes: "· Rui (almoxarife) concilia.")', /· Rui \(almoxarife\) confere; Ana \(gestora\) aceita o excedente\.$/.test(r.msg || ''), r.msg || r.erro);
  ok('encerramento impedido: "No Estoque: Rui (almoxarife) confere; Ana (gestora) aceita o excedente."', /\. No Estoque: Rui \(almoxarife\) confere; Ana \(gestora\) aceita o excedente\.$/.test(cenPodeEncerrar(G(), 'OS-0421') || ''), cenPodeEncerrar(G(), 'OS-0421'));
  coberto();
  ok('coberto pela custódia (75 L relatados com 75 L em custódia): "Rui (almoxarife) concilia"', cenConcQuem(G(), G().confs) === 'Rui (almoxarife) concilia', cenConcQuem(G(), G().confs));
  ini(); const rw = cenMudar(null, c => osc_apontar(c, 'OS-0421', '28/09', 10, { 'Fungicida A': 80 }, [], 'W-rev7'));
  ok('apontamento da web com 80 L (65 L em custódia): o mesmo texto', /· Rui \(almoxarife\) confere; Ana \(gestora\) aceita o excedente\.$/.test(rw.msg || ''), rw.msg || rw.erro);
  ini(); cenMudar(null, c => osc_apontar(c, 'OS-0421', '26/09', 50, undefined, undefined, 'W-1')); cenMudar(null, c => cenIniciarTurno(c, 'OS-0421')); cenMudar(null, c => cenFecharTurno(c, 50, 8, { 'Fungicida A': 60 }, '', []));
  const rd = cenMudar(null, c => cenApDecidir(c, 'OS-0421', 6, 'somar', PAULA));
  ok('Paula soma o dia 6 com 60 L (40 L em custódia): "Consumo em conferência: Rui (almoxarife) confere; Ana (gestora) aceita o excedente." (antes: "com Rui (almoxarife)")', /Consumo em conferência: Rui \(almoxarife\) confere; Ana \(gestora\) aceita o excedente\.$/.test(rd.msg || ''), rd.msg || rd.erro);
});

console.log('\nTOTAL · falhas ' + nfail);
if (nfail) process.exitCode = 1;
