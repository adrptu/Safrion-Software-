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
  ok('menu lateral: seletor com 5 perfis, Ana marcada', v.perfil_k === 'Ana' && (v.perfil_opts || []).length === 5, [v.perfil_k, (v.perfil_opts || []).length]);
  v.perfil_set({ target: { value: 'Caio' } });
  ok('trocar para Caio grava e avisa que não é segurança', __ls['safrion.perfilDemo'] === 'Caio' && g2perfil().k === 'Caio' && /Caio · PCP \(não é segurança de acesso\)/.test(self.state.g2toast || ''), self.state.g2toast);
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
  ini(); const KF = 'Fungicida A|F26-02'; cenMudar(null, c => cenDevolver(c, 'REQ-035', 'Fungicida A', 10, false)); const l = G().lotes[KF];
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
  const k3 = relato(75); cenMudar(null, c => cenEntregar(c, 'REQ-035', 'Fungicida A', 10)); const r3 = cenMudar(null, c => cenConciliar(c, k3.id, true, undefined, RUI));
  ok('coberto pela custódia (nada sai do lote): Rui aceita e fica gravado Rui', !r3.erro && G().confs[0].estado === 'Aceito' && G().confs[0].decisao === 'coberto pela custódia' && G().confs[0].por === 'Rui (almoxarife)', [r3.erro, G().confs[0].decisao]);
});

console.log('\n— R-D4 · checklist da manutenção (OM-0234 Revisão 250 h, 5 tarefas)');
ok('MA-04 sem a ação "Marcar pendentes como feitas" (pan_todas removido)', MA04_SRC_TODAS === '', MA04_SRC_TODAS.slice(0, 60));
caso('checklist', () => {
  let c = manClone(MAN0); const id = 'OM-0234'; manLiberar(c, id, true); manIniciar(c, id); const o = c.oms[id];
  manResp(c, id, 0, 'Feito', undefined, ZE); manResp(c, id, 1, 'Feito', undefined, ZE); manResp(c, id, 2, 'Feito', undefined, ANA); manResp(c, id, 3, 'Feito', undefined, ZE);
  ok('cada resposta grava quem (Zé (mecânico); Ana (gestora)) e a hora', o.chk[0].por === 'Zé (mecânico)' && /^\d\d:\d\d$/.test(o.chk[0].em || '') && o.chk[2].por === 'Ana (gestora)', o.chk.map(t => t.por));
  let e = ''; try { manConcluir(c, id, String(c.ativos[o.aid].leit.val + 8), '', false, {}); } catch (x) { e = x.message; }
  ok('NEGATIVO 4 de 5 respondidas: não conclui', e === 'Responda o checklist: 1 tarefa sem resposta.' && o.etapa === 'Em execução', e);
  manResp(c, id, 4, 'Não feito', undefined, ZE); e = ''; try { manConcluir(c, id, String(c.ativos[o.aid].leit.val + 8), '', false, {}); } catch (x) { e = x.message; }
  ok('NEGATIVO "Não feito" sem motivo: não conclui', e === 'Informe o motivo de “Lubrificar pontos de graxa”.', e);
  manResp(c, id, 1, '', undefined, ZE); ok('desmarcar apaga quem e hora (resposta volta a pendente)', o.chk[1].r === '' && o.chk[1].por === '' && o.chk[1].em === '', o.chk[1]);
  manResp(c, id, 1, 'Feito', undefined, ZE); manResp(c, id, 4, 'Feito', undefined, ZE);
  const r = manConcluir(c, id, String(c.ativos[o.aid].leit.val + 8), '', false, {}); ok('respondidas as 5, uma a uma: conclui e vai Em conferência', o.etapa === 'Em conferência' && /^OM-0234 em conferência/.test(r.msg), r.msg);
});

console.log('\nTOTAL · falhas ' + nfail);
if (nfail) process.exitCode = 1;
