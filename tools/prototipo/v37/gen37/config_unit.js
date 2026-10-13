// CONF-01 · Configurações sem navegador (executor: config_unit_test.py). Cada caso parte do cenário inicial (cenReset) e grava pelo cenMudar,
// como a tela faz (erro não grava nada). NEGATIVO = recusado. Critérios: docs/configuracoes/ESPECIFICACAO.md §8 (A1..A19).
let nfail = 0;
function ok(t, c, got) { if (c) console.log('OK    ' + t); else { nfail++; console.log('FALHA ' + t + (got === undefined ? '' : ' · ' + JSON.stringify(got).slice(0, 500))); } }
const caso = (t, f) => { try { f(); } catch (e) { ok('ERRO no caso "' + t + '": ' + String(e.message || e), false); } };
const G = () => cenGet();
const M = (f) => cenMudar(null, f);
const ini = () => { cenReset(); delete __ls['safrion.perfilDemo']; G2_PERFIL_MEM = ''; };
const trilha = () => confTrilha(G(), assinLer());
const nT = () => trilha().length;
const pid = k => confP(k).id;

console.log('— A1 · padrão: sem c.conf o efetivo é exatamente G2_PERFIS; estado de outra versão volta ao padrão');
caso('A1', () => { ini();
  ok('A1 sem c.conf: g2perfis() = G2_PERFIS (7 perfis com Igor e Marta do BEN-1, mesma ordem e mesmos papéis)', g2perfis() === G2_PERFIS && g2perfis().map(p => p.k).join() === 'Ana,Caio,Rui,Paula,Zé,Igor,Marta', g2perfis().map(p => p.k));
  ok('A1b CD-04 (R1): 13 pessoas, Caio (p11, PCP, Agronomia) entra, Igor e Marta (BEN-1) também; 12 com acesso, Beto sem; só Ana com CREA válido',
    CONF0.pessoas.length === 13 && confP('Caio').id === 'p11' && confP('Caio').equipe === 'Agronomia' && confComAcesso() === 12 && confAcessoDe('Beto').a === 'sem'
    && CONF0.pessoas.filter(p => confCrea(p)).map(p => p.k).join() === 'Ana', [CONF0.pessoas.length, confComAcesso()]);
  ok('A1c perfil desativado ou desconhecido guardado no navegador cai no 1º efetivo (Ana)', (() => { __ls['safrion.perfilDemo'] = 'Xyz'; const k = g2perfil().k; delete __ls['safrion.perfilDemo']; return k === 'Ana'; })());
  const r = M(c => confPapeis(c, 'p7', ['almoxarife', 'conferente'], 'k-a1', 'Ana'));
  ok('A1d com c.conf (Rui ganha conferência): o efetivo muda na hora, sem recarregar', !r.erro && g2papel('Rui', 'conferente') && g2perfis().length === 7, r);
  const c = JSON.parse(__ls['talhao-os-cenario-v1']); c.conf.v = 'CONF-0-velho'; __ls['talhao-os-cenario-v1'] = JSON.stringify(c);
  ok('A1e c.conf de outra versão (outro build ou outro G2_PERFIS): volta ao padrão', !g2papel('Rui', 'conferente') && g2perfis() === G2_PERFIS);
  ok('A1f a versão do CONF0 inclui o resumo do bloco <perfis> (outra frente que mude G2_PERFIS invalida o salvo)', /^CONF-1-[0-9a-f]{8}$/.test(CONF0.v), CONF0.v); });

console.log('\n— A2 · conceder conferência a Rui vale para o CMD-09 na hora; retirar recusa; idempotência pela chave (R12)');
const dup = (c) => { osc_apontar(c, 'OS-0421', '26/09', 50, undefined, undefined, 'W-1'); cenIniciarTurno(c, 'OS-0421'); cenFecharTurno(c, 50, 8, undefined, '', []); return { msg: 'dup' }; };
caso('A2', () => { ini(); M(dup);
  const r0 = M(c => cenApDecidir(c, 'OS-0421', 6, 'somar', 'Rui'));
  ok('A2a NEGATIVO antes: Rui decide a duplicidade → recusado, decisão de Paula (conferência)', /decisão de Paula \(conferência\)/.test(r0.erro || ''), r0);
  const k = 'k-a2'; const r1 = M(c => confPapeis(c, 'p7', ['almoxarife', 'conferente'], k, 'Ana')); const rev1 = G().rev;
  const r2 = M(c => confPapeis(c, 'p7', ['almoxarife', 'conferente'], k, 'Ana'));
  ok('A2b mesma chave e mesmo conteúdo 2×: 1 evento, mesmo recibo', !r1.erro && r2.repetido && r2.recibo.id === r1.recibo.id && confLer().ev.length === 1, [r1, r2]);
  const r3 = M(c => confPapeis(c, 'p7', ['almoxarife'], k, 'Ana'));
  ok('A2c mesma chave com outro conteúdo: conflito, nada gravado', /conflito, nada gravado/.test(r3.erro || '') && g2papel('Rui', 'conferente') && confLer().ev.length === 1, r3);
  const d = M(c => cenApDecidir(c, 'OS-0421', 6, 'somar', 'Rui')); const ap = G().ordens['OS-0421'].ap.find(a => a.dia === 6);
  ok('A2d com o papel, Rui decide e o registro grava "Rui (conferência)"', !d.erro && ap.dec && ap.dec.quem === 'Rui (conferência)', [d, ap.dec]);
  ini(); M(dup); M(c => confPapeis(c, 'p7', ['almoxarife', 'conferente'], 'k-a2e', 'Ana')); M(c => confPapeis(c, 'p7', ['almoxarife'], 'k-a2f', 'Ana'));
  const rv = G().rev; const r4 = M(c => cenApDecidir(c, 'OS-0421', 6, 'somar', 'Rui'));
  ok('A2e retirado o papel, Rui é recusado sem gravar', !!r4.erro && G().rev === rv && G().ordens['OS-0421'].ap.find(a => a.dia === 6).st === CEN_AP_DUP, r4);
  const r5 = M(c => confPapeis(c, 'p7', ['almoxarife'], '', 'Ana')); const r6 = M(c => confPapeis(c, 'p7', ['almoxarife', 'conferente'], 'k-a2g', null));
  ok('A2f sem chave ou sem perfil: recusa', /sem chave/.test(r5.erro || '') && /decisão de Ana \(gestora\)/.test(r6.erro || ''), [r5, r6]); });

console.log('\n— A3 · travas com dano nomeado (R3, R4, R5): recusam com o motivo e c.rev igual');
caso('A3', () => { ini(); const rv = G().rev;
  const a = M(c => confPapeis(c, 'p11', ['pcp', 'agronomo'], 'k1', 'Ana'));
  const b = M(c => confPapeis(c, 'p1', ['gestor', 'agronomo', 'direcao'], 'k2', 'Ana'));
  const d = M(c => confPapeis(c, 'p1', ['agronomo'], 'k3', 'Ana'));
  const e = M(c => confAcesso(c, 'p1', false, 'k4', 'Ana'));
  const f = M(c => confPapeis(c, 'p7', ['almoxarife', 'conferente'], 'k5', 'Rui'));
  ok('A3a R4 agrônomo sem CREA (Caio): recusado com o motivo (lei)', /Agrônomo só com CREA válido no cadastro em 26\/09\/2026: Caio não tem CREA/.test(a.erro || ''), a);
  ok('A3b R3 Ana concede direção a si mesma: recusado (RF-GOV-002)', /Ninguém concede papel a si mesmo/.test(b.erro || ''), b);
  ok('A3c R5 Ana retira o próprio gestor (última gestora): recusado (organização trancada)', /última pessoa ativa com o papel de gestor/.test(d.erro || ''), d);
  ok('A3d R5 desativar a última gestora: recusado', /última pessoa ativa com o papel de gestor e não pode ser desativada/.test(e.erro || ''), e);
  ok('A3e quem não é gestor não muda papel (AL-13): Rui recusado, decisão de Ana (gestora)', /decisão de Ana \(gestora\)/.test(f.erro || ''), f);
  ok('A3f nada gravado: c.rev igual e trilha com 16 registros', G().rev === rv && nT() === 16, [G().rev, rv, nT()]); });

console.log('\n— A17 · Restaurar demonstração volta acessos, alçadas, conexões e trilha ao seed');
caso('A17', () => { ini(); M(c => confPapeis(c, 'p7', ['almoxarife', 'conferente'], 'k1', 'Ana')); M(c => confAcesso(c, 'p6', false, 'k2', 'Ana'));
  const antes = nT(); cenReset();
  ok('A17 cenReset: g2perfis() = G2_PERFIS, Paula volta, trilha 16 (antes ' + antes + ')', g2perfis() === G2_PERFIS && g2papel('Paula', 'conferente') && nT() === 16 && antes === 18, [antes, nT()]); });

console.log('\n— A10 (seed) · trilha lida dos registros: 14 no início');
caso('A10 seed', () => { ini(); const L = trilha(); const mes = {}; L.forEach(r => { const m = r.d.slice(0, 7); mes[m] = (mes[m] || 0) + 1; });
  const aut = {}; L.forEach(r => { aut[r.k] = (aut[r.k] || 0) + 1; });
  ok('A10a 16 registros: jun 2 · jul 10 · ago 3 · set 1', L.length === 16 && mes['2026-06'] === 2 && mes['2026-07'] === 10 && mes['2026-08'] === 3 && mes['2026-09'] === 1, mes);
  ok('A10b autores pelo 1º nome: Ana 13, Plataforma 1, Provedor 2 (3 autores)', aut.Ana === 13 && aut.Plataforma === 1 && aut.Provedor === 2 && Object.keys(aut).length === 3, aut);
  ok('A10c nenhuma linha sem autor, data ou objeto', L.every(r => r.quem && r.d && r.obj && r.oq), L.filter(r => !(r.quem && r.d && r.obj)));
  ok('A10d fatura paga pelo provedor aparece "Provedor (simulado)"; contrato v1 por "Ana · Gestora"', L.some(r => r.quem === 'Provedor (simulado)' && /jul\/2026/.test(r.obj)) && L.some(r => r.quem === 'Ana · Gestora' && r.obj === 'Contrato v1'), L.map(r => r.quem + '|' + r.obj)); });

console.log('\n— A4 · cada alçada é lida pelo comando real: perfil com os papéis passa, sem eles recusa sem gravar (níveis base e acima)');
const KG = 'Glifosato 480|G26-14';
const KQ = () => Object.keys(G().lotes).find(k => G().lotes[k].quarentena > 0);
const dupDia = () => { M(dup); return 6; };
const ccAcima = () => M(c => osc_apontar(c, 'OS-0421', '26/09', 50, { 'Fungicida A': 80, 'Adjuvante espalhante': 0 }, [], 'W-cc'));
const CASOS = {
  'AL-01': [() => {}, ator => M(c => osc_liberar(c, 'OS-0430', false, '', ator)), 'Ana', 'Caio'],
  'AL-02': [() => {}, ator => M(c => osc_ajustar(c, 'OS-0430', 150, {}, '', [], [], false, ator)), 'Ana', 'Rui'],
  'AL-04': [() => {}, ator => M(c => osc_cancelar(c, 'OS-0430', 'teste', ['', '', ''], ator)), 'Ana', 'Caio'],
  'AL-05': [() => {}, ator => M(c => osc_dispensar(c, 'OS-0421', 10, 'teste', ator)), 'Ana', 'Rui'],
  'AL-09': [() => M(c => estContar(c, 'INV-2611', KG, 1180, 'Paula (almoxarife)', 'bombona avariada', 'Rui')), ator => M(c => estAprovar(c, 'INV-2611', ator)), 'Ana', 'Rui'],
  'AL-10': [() => { ccAcima(); M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 15, 'Marcos', 'Rui')); }, ator => M(c => cenConciliar(c, G().confs[0].id, true, undefined, ator)), 'Rui', 'Caio'],
  'AL-11': [() => {}, ator => M(c => cenLiberarQuarentena(c, KQ(), 'LAUDO-1', ator)), 'Ana', 'Rui'],
  'AL-12': [dupDia, ator => M(c => cenApDecidir(c, 'OS-0421', 6, 'somar', ator)), 'Paula', 'Rui'],
  'AL-13': [() => {}, ator => M(c => confPapeis(c, 'p7', ['almoxarife', 'conferente'], confChave('t'), ator)), 'Ana', 'Rui'],
  'AL-14': [() => {}, ator => M(c => confAlcMudar(c, 'AL-05', { lim: 15 }, 'safra curta', confChave('t'), ator)), 'Ana', 'Caio'],
  /* AL-15 (P7): conferida no CF-05 dentro do cenMudar (cfPor da tela), antes do comando da assinatura; o backoffice não passa por ela */
  'AL-15': [() => M(c => assinAvancar(c, '2026-10-01', { ha: 2570.23, n: 30 })), ator => M(c => { const f = assinAberta(assinGarante(c).orgs.sr); return assinPagar(c, f.id, 'Pix', confChave('pag'), cenExigeAlc(ator, 'AL-15', 'Pagar a fatura')); }), 'Ana', 'Rui'],
  /* AL-17 (integração com a Colheita): publicar previsão lê a alçada com o perfil de quem age */
  'AL-17': [() => {}, ator => M(c => prPublicar(c, 'lg19', ator)), 'Ana', 'Rui'] };
G2_ALCADAS.forEach(a => caso('A4 ' + a.id, () => { const X = CASOS[a.id]; if (!X) { ok('A4 ' + a.id + ' tem caso de teste', false); return; }
  ini(); X[0](); const rv = G().rev; const rn = X[1](X[3]);
  ok('A4 ' + a.id + ' NEGATIVO sem o papel (' + X[3] + '): recusado "decisão de …", nada gravado', !!rn.erro && /decisão de|exige Direção|Aprovação agronômica/.test(rn.erro) && G().rev === rv, rn.erro || rn.msg);
  const rp = X[1](X[2]); ok('A4 ' + a.id + ' com o papel (' + X[2] + '): passa', !rp.erro, rp.erro); }));
caso('A4 acima', () => { ini(); ccAcima(); const rv = G().rev; const id = G().confs[0].id;
  const r1 = M(c => cenConciliar(c, id, true, undefined, 'Rui'));
  ok('A4 AL-10 acima NEGATIVO: Rui (almoxarife) não aceita o excedente; decisão de Ana (gestora)', /acima da custódia .*decisão de Ana \(gestora\)/.test(r1.erro || '') && G().rev === rv, r1.erro);
  const r2 = M(c => cenConciliar(c, id, true, undefined, 'Ana')); ok('A4 AL-10 acima: Ana (gestora) aceita', !r2.erro && G().confs[0].por === 'Ana (gestora)', r2.erro);
  ini(); const r3 = M(c => osc_dispensar(c, 'OS-0421', 71, 'chuva', 'Ana'));
  ok('A4 AL-05 acima (71 ha = 20,3 %) sem direção: recusa com a mensagem de hoje', r3.erro === '71 ha = 20,3 % acima de 20 % · exige Direção.', r3.erro); });
caso('A4 literais', () => {
  const pap = /cenExige(Um)?\(\s*ator\s*,\s*\[?\s*'(gestor|agronomo|conferente|almoxarife|pcp|direcao)'/;
  ok('A4 nenhum comando confere papel literal (cenExige com papel fixo): tudo por cenExigeAlc', !pap.test(FONTES.cenario) && !pap.test(FONTES.os) && !pap.test(FONTES.est), [pap.exec(FONTES.cenario), pap.exec(FONTES.os), pap.exec(FONTES.est)].map(x => x && x[0]));
  const tel = /g2(papel|quem|quemUm|umPapel)\([^)]*'(gestor|agronomo|conferente|pcp|direcao)'/;
  ok('A4 telas da O.S. e do Estoque não testam papel literal (g2papel/g2quem com papel fixo)', !tel.test(FONTES.os) && !tel.test(FONTES.est), [tel.exec(FONTES.os), tel.exec(FONTES.est)].map(x => x && x[0]));
  const lit = /const\s+(OS_AGRO|OS_LIB|CEN_CONF_AP|CEN_CONC_RESP|LIM_DISP)\s*=|q:\s*'(Rui \(almoxarife\)|Ana \(agrônoma\))|'Rui \(almoxarife\) (entrega|recebe)|o\.dono='Rui/;
  ok('A4 nenhuma pessoa fixa como "quem decide" (OS_AGRO, CEN_CONF_AP, CEN_CONC_RESP, LIM_DISP viraram funções da alçada)', !lit.test(FONTES.cenario) && !lit.test(FONTES.os) && !lit.test(FONTES.est), [lit.exec(FONTES.cenario), lit.exec(FONTES.os), lit.exec(FONTES.est)].map(x => x && x[0]));
  ok('A4 AL-16 mostra os níveis de dados2.ALCADA (R$ 50.000 · R$ 300.000 · Direção), sem edição', CONF0.compras.length === 3 && CONF0.compras[0].ate === 50000 && CONF0.compras[1].ate === 300000 && CONF0.compras[2].ate === null && !G2_ALCADAS.some(a => a.id === 'AL-16'), CONF0.compras); });

console.log('\n— A5 · AL-01 → PCP (CONF-D10): Ana aprova (só CMD-42), Caio libera (só CMD-06); 5 fases; Salvar ajuste não aprova (R13)');
const evs = id => ((G().ordens[id].osc || {}).ev || []);
const vw = id => osMerge(OSD.ords.find(x => x.id === id), G().ordens[id], G());
caso('A5', () => { ini(); const n0 = nT(); M(c => confAlcMudar(c, 'AL-01', { papel: 'pcp' }, 'decisão do proprietário', 'k5a', 'Ana'));
  const pa = osProx(vw('OS-0430'), g2pf('Ana')), pc = osProx(vw('OS-0430'), g2pf('Caio'));
  ok('A5a com AL-01 = PCP: Ana vê "Aprovar v1"; Caio vê a aprovação pendente (sem botão)', pa.P.btn === 'Aprovar v1' && !pa.b && !!pc.b && /Aprovação agronômica da v1 pendente: decisão de Ana \(agrônoma\)/.test(pc.b.t), [pa.P.btn, pc.b]);
  const rv = G().rev; const r0 = M(c => osc_liberar(c, 'OS-0430', false, '', 'Caio'));
  ok('A5b NEGATIVO Caio antes da aprovação: recusado, nada gravado', /Aprovação agronômica da v1 da OS-0430 pendente/.test(r0.erro || '') && G().rev === rv && evs('OS-0430').length === 0, r0.erro);
  const ra = M(c => osc_aprovar(c, 'OS-0430', 'Ana')); const v1 = vw('OS-0430');
  ok('A5c Ana aprova: só CMD-42 por Ana (agrônoma), A liberar com o selo "Aprovada v1 · aguarda liberação"', !ra.erro && evs('OS-0430').length === 1 && evs('OS-0430')[0].por === 'Ana (agrônoma)' && v1.etapa === 'A liberar' && v1.selos.some(x => x.t === 'Aprovada v1 · aguarda liberação'), [ra, v1.selos]);
  const ra2 = M(c => osc_aprovar(c, 'OS-0430', 'Ana')); ok('A5d NEGATIVO aprovar de novo: recusado', /já está aprovada/.test(ra2.erro || ''), ra2.erro);
  const rl = M(c => osc_liberar(c, 'OS-0430', false, '', 'Caio')); const e = evs('OS-0430');
  ok('A5e Caio libera: só CMD-06 por Caio (PCP); Liberadas; REQ reservada', !rl.erro && e.length === 2 && e[1].cmd === 'CMD-06' && e[1].por === 'Caio (PCP)' && G().ordens['OS-0430'].etapa === 'Liberadas' && G().ordens['OS-0430'].reservado, [rl, e]);
  ok('A5f trilha +3: AL-01 v1 → v2, CMD-42 por Ana (agrônoma), CMD-06 por Caio (PCP)', nT() === n0 + 3 && trilha().some(r => r.cmd === 'CMD-06' && r.quem === 'Caio (PCP)'), nT() - n0);
  ok('A5g Kanban segue com 5 fases (FASES da tela da O.S.)', /const FASES=\['A liberar','Liberadas','Em execução','Em conferência','Encerradas'\];/.test(FONTES.ostela), (FONTES.ostela.match(/const FASES=[^;]*;/) || [''])[0]);
  ini(); M(c => confAlcMudar(c, 'AL-01', { papel: 'pcp' }, 'decisão do proprietário', 'k5b', 'Ana'));
  const rn = M(c => osc_ajustar(c, 'OS-0430', 150, {}, '', [], [], false, 'Ana'));
  ok('A5h "Salvar ajuste" (sem aprovar) não grava CMD-42 (N5)', !rn.erro && evs('OS-0430').length === 0, [rn, evs('OS-0430')]);
  const rs = M(c => { const r1 = osc_ajustar(c, 'OS-0430', 140, {}, '', [], [], false, 'Ana'); const r2 = osc_aprovar(c, 'OS-0430', 'Ana'); return { msg: r1.msg + ' ' + r2.msg }; });
  ok('A5i "Salvar e aprovar v3": grava a v3 e o CMD-42 da v3 no mesmo comando', !rs.erro && evs('OS-0430').length === 1 && evs('OS-0430')[0].v === 'v3', [rs, evs('OS-0430')]);
  ini(); const rA = M(c => osc_liberar(c, 'OS-0430', false, '', 'Ana'));
  ok('A5j com AL-01 = gestor (padrão), Ana segue numa confirmação: CMD-42 e CMD-06', !rA.erro && evs('OS-0430').map(x => x.cmd).join() === 'CMD-42,CMD-06', rA); });

console.log('\n— A6 · AL-05: limite pela regra decimal única; ampliar o próprio poder espera o 2º aprovador (R10); uma pendência por alçada (R8)');
caso('A6', () => { ini();
  const L = [350, 100, 75.11, 73.18, 71.11].map(a => osLimDisp({ area: a }).ha);
  ok('A6a limite de 20 %: 70 / 20 / 15,02 / 14,64 / 14,22 ha (cenQtd, decimal)', L.join('|') === '70|20|15.02|14.64|14.22', L);
  let r = M(c => confAlcMudar(c, 'AL-05', { lim: 25 }, 'safra com chuva', 'k6a', 'Ana'));
  ok('A6b 20 → 25 % por Ana (quem dispensa): fica pendente, vale a v1 (70 ha na OS-0421)', r.pendente && g2alc('AL-05').lim === 20 && osLimDisp(G().ordens['OS-0421']).ha === 70 && /aguarda confirmação/.test(r.msg), r);
  const r71 = M(c => osc_dispensar(c, 'OS-0421', 71, 'chuva', 'Ana')); ok('A6c enquanto pendente, 71 ha segue recusado (20 %)', /acima de 20 %/.test(r71.erro || ''), r71);
  r = M(c => confAlcMudar(c, 'AL-05', { lim: 30 }, 'outra', 'k6b', 'Ana')); ok('A6d NEGATIVO outra proposta para a AL-05 antes de confirmar: recusada (R8)', /já tem mudança aguardando confirmação/.test(r.erro || ''), r);
  r = M(c => confAlcConfirmar(c, 'AL-05', 'k6c', 'Ana')); ok('A6e NEGATIVO Ana não confirma a própria', /Quem propôs não confirma/.test(r.erro || ''), r);
  r = M(c => confPapeis(c, 'p11', ['gestor', 'pcp'], 'k6d', 'Ana')); ok('A6f Ana concede gestor a Caio', !r.erro, r);
  r = M(c => confAlcConfirmar(c, 'AL-05', 'k6e', 'Caio')); ok('A6g Caio (gestor) confirma: vigente v2 = 25 %, 87,5 ha na OS-0421', !r.erro && g2alc('AL-05').lim === 25 && g2alc('AL-05').v === 2 && osLimDisp(G().ordens['OS-0421']).ha === 87.5, [r, g2alc('AL-05')]);
  r = M(c => osc_dispensar(c, 'OS-0421', 80, 'chuva', 'Ana')); ok('A6h com 25 %, dispensar 80 ha passa', !r.erro, r.erro);
  ini(); r = M(c => confAlcMudar(c, 'AL-05', { lim: 15 }, 'safra curta', 'k6f', 'Ana'));
  ok('A6i 20 → 15 % por Ana vale na hora (reduz): 52,5 ha', !r.erro && !r.pendente && g2alc('AL-05').lim === 15 && osLimDisp(G().ordens['OS-0421']).ha === 52.5, r);
  r = M(c => osc_dispensar(c, 'OS-0421', 53, 'chuva', 'Ana')); ok('A6j com 15 %, 53 ha recusa com o limite vigente na mensagem', r.erro === '53 ha = 15,1 % acima de 15 % · exige Direção.', r.erro);
  r = M(c => confAlcMudar(c, 'AL-05', { lim: 0 }, 'x', 'k6g', 'Ana')); ok('A6k limite fora de 1-100 % recusado', /de 1 a 100 %/.test(r.erro || ''), r); });

console.log('\n— A7 · R9: alçada só aponta para papel que alguém ativo tem; AL-01 → PCP vale na hora (reduz o poder da gestora)');
caso('A7', () => { ini(); let r = M(c => confAlcMudar(c, 'AL-09', { papel: 'direcao' }, 'auditoria pediu', 'k7a', 'Ana'));
  ok('A7a NEGATIVO AL-09 → direção (ninguém tem): recusado, nada gravado', /Ninguém ativo tem o papel direção/.test(r.erro || '') && g2alc('AL-09').papeis.join() === 'gestor', r);
  r = M(c => confAlcMudar(c, 'AL-10', { papel: 'direcao' }, 'auditoria', 'k7b', 'Ana')); ok('A7b NEGATIVO AL-10 excedente → direção: recusado', /Ninguém ativo/.test(r.erro || ''), r);
  r = M(c => confAlcMudar(c, 'AL-02', { papel: 'gestor' }, 'x', 'k7c', 'Ana')); ok('A7c NEGATIVO AL-02 é fixa (lei)', /AL-02 é fixa: lei/.test(r.erro || ''), r);
  r = M(c => confAlcMudar(c, 'AL-01', { papel: 'pcp' }, 'decisão do proprietário', 'k7d', 'Ana'));
  ok('A7d AL-01 → PCP por Ana: vale na hora (v2), CMD-06 passa a ser do PCP', !r.erro && !r.pendente && g2alc('AL-01').papeis.join() === 'pcp' && g2alc('AL-01').v === 2, r);
  r = M(c => confAlcMudar(c, 'AL-01', { papel: 'gestor' }, 'voltar', 'k7e', 'Ana'));
  ok('A7e AL-01 PCP → gestor por Ana amplia o poder dela: aguarda 2º aprovador (CONF-D10, como reverter)', r.pendente && g2alc('AL-01').papeis.join() === 'pcp', r);
  r = M(c => confAlcDesistir(c, 'AL-01', 'k7f', 'Ana')); ok('A7f quem propôs desiste: segue PCP', !r.erro && !confLer().pend['AL-01'] && g2alc('AL-01').papeis.join() === 'pcp', r); });

console.log('\n— A8 · desativar Paula: some do Ver como; AL-12 sem titular; textos dizem onde conceder; registros antigos intactos');
caso('A8', () => { ini(); M(dup); M(c => cenApDecidir(c, 'OS-0421', 6, 'somar', 'Paula'));
  const r = M(c => confAcesso(c, 'p6', false, 'k8a', 'Ana'));
  ok('A8a Paula desativada: fora do Ver como e de g2quem; aviso de AL-12 sem titular', !r.erro && !g2perfis().some(p => p.k === 'Paula') && /AL-12 fica sem titular/.test(r.msg) && confSemTitular(confLer()).join() === 'AL-12', [r, confSemTitular(confLer())]);
  ok('A8b quem decide a duplicidade: "conferência sem titular: conceda em Configurações" (não "Paula (conferência)")', CEN_CONF_AP() === 'conferência sem titular: conceda em Configurações › Usuários e alçadas', CEN_CONF_AP());
  ok('A8c registro antigo intacto: o dia 6 segue decidido por "Paula (conferência)"', G().ordens['OS-0421'].ap.find(a => a.dia === 6).dec.quem === 'Paula (conferência)');
  const c0 = G(); osc_apontar(c0, 'OS-0421', '25/09', 10, undefined, undefined, 'W-x'); osc_apontar(c0, 'OS-0421', '25/09', 10, undefined, undefined, 'W-y');
  const v = osMerge(OSD.ords.find(x => x.id === 'OS-0421'), c0.ordens['OS-0421'], c0);
  ok('A8d na O.S., o dono da duplicidade diz que a conferência está sem titular', /conferência sem titular/.test(v.dono || ''), v.dono);
  const r2 = M(c => confPapeis(c, 'p7', ['almoxarife', 'conferente'], 'k8b', 'Ana'));
  ok('A8e Conceder conferência a Rui: AL-12 volta a ter titular', !r2.erro && confSemTitular(confLer()).length === 0 && CEN_CONF_AP() === 'Rui (conferência)', [r2, CEN_CONF_AP()]);
  const r3 = M(c => confAcesso(c, 'p6', true, 'k8c', 'Ana')); ok('A8f reativar Paula: volta com os papéis', !r3.erro && g2papel('Paula', 'conferente'), r3); });

console.log('\n— A19 · o app de campo respeita o acesso desativado (R2, CONF-D24)');
caso('A19', () => { ini(); M(c => { cenSinal(c, false); cenIniciarTurno(c, 'OS-0421'); return cenFecharTurno(c, 20, 4, undefined, '', []); });
  const fila0 = G().app.fila.length; const r = M(c => confAcesso(c, 'p2', false, 'k19', 'Ana'));
  const a = M(c => cenIniciarTurno(c, 'OS-0421')), b = M(c => cenOcorrencia(c, 'OS-0421', 'Outro', 'teste')), d = M(c => cenConfirmarRecebimento(c, 'REQ-035'));
  const fe = M(c => { c.app.turno = { os: 'OS-0421', ini: '07:00', d: '26/09', chave: 'TU-x', pausas: [], fim: null }; return cenFecharTurno(c, 5, 1, undefined, '', []); });
  ok('A19a Marcos desativado: iniciar, ocorrência, confirmar recebimento e fechar turno recusam com o motivo do acesso', !r.erro && [a, b, d, fe].every(x => /Acesso de Marcos desativado em Configurações/.test(x.erro || '')), [a, b, d, fe].map(x => x.erro));
  const s = M(c => cenSinal(c, true)); ok('A19b o que já estava na fila do aparelho envia', fila0 === 1 && !s.erro && G().app.fila.length === 0 && /enviado/.test(s.msg), [fila0, s]);
  M(c => confAcesso(c, 'p2', true, 'k19b', 'Ana')); const e = M(c => cenOcorrencia(c, 'OS-0421', 'Outro', 'teste'));
  ok('A19c reativado, volta a registrar', !e.erro, e.erro); });

console.log('\n— A10 (parte 1) · dispensa e decisão de duplicidade na trilha, uma linha por ato');
caso('A10 dispensa', () => { ini(); const n0 = nT(); M(c => osc_dispensar(c, 'OS-0421', 10, 'chuva', 'Ana')); M(c => osc_dispensar(c, 'OS-0421', 5, 'falha de máquina', 'Ana'));
  const L = trilha().filter(r => r.cmd === 'CMD-47');
  ok('A10e duas dispensas na mesma O.S. = 2 linhas CMD-47 (antes a 2ª sobrescrevia dispPor)', nT() === n0 + 2 && L.length === 2 && L.every(r => r.quem === 'Ana (gestora e agrônoma)'), L); });
caso('A10 vale este', () => { ini(); M(c => { osc_apontar(c, 'OS-0421', '26/09', 50, { 'Fungicida A': 80, 'Adjuvante espalhante': 0 }, [], 'W-1'); cenIniciarTurno(c, 'OS-0421'); return cenFecharTurno(c, 50, 8, { 'Fungicida A': 25 }, '', []); });
  const n0 = nT(); const d = M(c => cenApDecidir(c, 'OS-0421', 6, 'este', 'Paula')); const L = trilha().slice();
  ok('A10f "vale este" = 1 linha CMD-09 e nenhuma CMD-50 (o caso CC fechado pela decisão leva via CMD-09)', !d.erro && nT() === n0 + 1 && L.filter(r => r.cmd === 'CMD-09').length === 1 && !L.some(r => r.cmd === 'CMD-50')
    && G().confs.some(k => k.via === 'CMD-09'), [d, L.filter(r => /CMD-(09|50)/.test(r.cmd)).map(r => r.oq)]); });
caso('A10 recontagem', () => { ini(); M(c => estContar(c, 'INV-2611', KG, 1180, 'Paula (almoxarife)', 'bombona avariada', 'Rui')); const n0 = nT();
  const r = M(c => estRecontar(c, 'INV-2611', 'Rui')); const L = trilha().filter(x => x.cmd === 'Ajuste');
  ok('A10g pedir recontagem grava quem recusou o ajuste (Rui) e entra na trilha', !r.erro && nT() === n0 + 1 && L.length === 1 && L[0].quem === 'Rui (almoxarife)' && /Recusar ajuste/.test(L[0].oq), [r, L]); });

console.log('\n— A10 (roteiro da §6) · cada item parte do seed e acrescenta exatamente o "trilha +n" dele, cada ato uma vez com autor, data e objeto');
const mais = (f) => { ini(); const n0 = nT(); f(); return nT() - n0; };
caso('A10 roteiro', () => {
  ok('A10h AL-05 20 → 15 % por Ana: +1', mais(() => M(c => confAlcMudar(c, 'AL-05', { lim: 15 }, 'safra curta', 'k1', 'Ana'))) === 1);
  ok('A10i AL-05 20 → 25 % (proposta), gestor a Caio (concessão), Caio confirma: +3', mais(() => { M(c => confAlcMudar(c, 'AL-05', { lim: 25 }, 'chuva', 'k1', 'Ana')); M(c => confAlcMudar(c, 'AL-05', { lim: 30 }, 'outra', 'k2', 'Ana'));
    M(c => confAlcConfirmar(c, 'AL-05', 'k3', 'Ana')); M(c => confPapeis(c, 'p11', ['gestor', 'pcp'], 'k4', 'Ana')); M(c => confAlcConfirmar(c, 'AL-05', 'k5', 'Caio')); }) === 3);
  ok('A10j recusas (agrônomo sem CREA, autoconcessão, último gestor): +0', mais(() => { M(c => confPapeis(c, 'p11', ['pcp', 'agronomo'], 'k1', 'Ana')); M(c => confPapeis(c, 'p1', ['gestor', 'agronomo', 'direcao'], 'k2', 'Ana')); M(c => confPapeis(c, 'p1', ['agronomo'], 'k3', 'Ana')); }) === 0);
  ok('A10k desativar Paula e conceder conferência a Rui: +2', mais(() => { M(c => confAcesso(c, 'p6', false, 'k1', 'Ana')); M(c => confPapeis(c, 'p7', ['almoxarife', 'conferente'], 'k2', 'Ana')); }) === 2);
  ok('A10l convidar Beto: +1 e CF-05 contaria 13 com acesso', mais(() => M(c => confConvidar(c, 'p9', 'k1', 'Ana'))) === 1 && confComAcesso() === 13);
  ok('A10m desativar Marcos (só app): +1', mais(() => M(c => confAcesso(c, 'p2', false, 'k1', 'Ana'))) === 1);
  let fila = []; const n = mais(() => { M(c => osc_liberar(c, 'OS-0430', false, '', 'Ana')); M(c => cenEntregar(c, 'REQ-041', 'Glifosato 480', 20, 'Marcos', 'Rui'));
    fila.push(confErpFila(G()).length); const s1 = M(c => confSincronizar(c, 'k-s1', 'Ana')); fila.push(s1.n, confErpFila(G()).length); const s2 = M(c => confSincronizar(c, 'k-s2', 'Ana')); fila.push(s2.n); });
  ok('A10n Ana libera a OS-0430 (3 reservas fora da fila), Rui entrega Glifosato 480: fila do ERP 1; sincronizar envia 1; de novo 0; trilha +5 (CMD-42, CMD-06, entrega, 2 sincronizações)', n === 5 && fila.join() === '1,1,0,0', [n, fila]);
  const L = trilha(); const e = L.find(r => r.oq === 'Entregar insumo');
  ok('A10o a entrega aparece com autor Rui (almoxarife) e o destinatário no efeito (autor = o campo até " → ")', !!e && e.quem === 'Rui (almoxarife)' && /para Marcos/.test(e.ef), e); });
caso('A10 filtros', () => { ini(); M(c => confAlcMudar(c, 'AL-05', { lim: 15 }, 'safra curta', 'k1', 'Ana')); const L = trilha();
  ok('A10p filtrar pela pessoa pelo 1º nome junta "Ana · Gestora" e "Ana (gestora)"; por mês, set tem 2 (fatura de ago e a mudança da AL-05)', L.filter(r => r.k === 'Ana').length === 14 && L.filter(r => r.d.slice(0, 7) === '2026-09').length === 2, [L.filter(r => r.k === 'Ana').length]); });

console.log('\n— A11 · CSV = linhas filtradas, sem segredo; a exportação vira registro (R15)');
const SEGREDO = /(senha|token|secret|apikey)\s*[:=]|[A-Za-z0-9_-]{24,}/i;
caso('A11', () => { ini(); const L = trilha().filter(r => r.k === 'Ana'); const csv = confCsv(L);
  ok('A11a CSV com cabeçalho e uma linha por registro filtrado (13 da Ana), separador ";", CRLF', csv.split('\r\n').filter(Boolean).length === 14 && /^"Quando";"Quem";"O quê"/.test(csv), csv.slice(0, 200));
  ok('A11b nenhum texto com cara de segredo no CSV', !SEGREDO.test(csv), (csv.match(SEGREDO) || [])[0]);
  const n0 = nT(); const r = M(c => confExportar(c, 11, 'pessoa: Ana', 'k-exp', 'Ana')); const r2 = M(c => confExportar(c, 11, 'pessoa: Ana', 'k-exp', 'Ana'));
  ok('A11c a exportação grava "Exportação · 11 registros · pessoa: Ana" (+1); a mesma chave não grava de novo', !r.erro && r2.repetido && nT() === n0 + 1 && trilha().some(x => /^Exportação · 11 registros · pessoa: Ana/.test(x.ef)), [r, r2]); });

console.log('\n— A12 · integrações só de demonstração; fila do ERP uma vez por conteúdo; estorno depois de enviado volta uma vez (R16, R17)');
caso('A12', () => { ini(); const X = confConexoes(G());
  ok('A12a 5 conexões (ERP, estação, telemetria, laboratório, app); fila do ERP 0 no seed; app "Com sinal (simulado)"', X.length === 5 && X[0].pend === 0 && /Com sinal \(simulado\)/.test(X[4].estado), X.map(x => x.t + ':' + x.estado));
  ok('A12b nenhum texto com cara de segredo nas conexões nem na trilha', !SEGREDO.test(JSON.stringify(X)) && !SEGREDO.test(JSON.stringify(trilha().map(r => [r.quem, r.oq, r.obj, r.ef, r.src]))));
  M(c => { osc_apontar(c, 'OS-0421', '26/09', 50, { 'Fungicida A': 25, 'Adjuvante espalhante': 0 }, [], 'W-1'); return { msg: '' }; });
  const f1 = confErpFila(G()); M(c => confSincronizar(c, 'k1', 'Ana')); const f2 = confErpFila(G());
  M(c => { cenIniciarTurno(c, 'OS-0421'); return cenFecharTurno(c, 50, 8, { 'Fungicida A': 25 }, '', []); }); M(c => cenApDecidir(c, 'OS-0421', 6, 'este', 'Paula'));
  const f3 = confErpFila(G()); const est = f3.filter(x => x.estorno);
  const s3 = M(c => confSincronizar(c, 'k2', 'Ana')); const f4 = confErpFila(G()); const s4 = M(c => confSincronizar(c, 'k3', 'Ana'));
  ok('A12c consumo da web na fila (1), enviado; "vale este" estorna o dia 5 enviado: volta uma vez como estorno (junto com o consumo novo); depois de enviar, nada; de novo, 0',
    f1.length === 1 && f2.length === 0 && est.length === 1 && est[0].m.id === f1[0].m.id && s3.n === f3.length && f4.length === 0 && s4.n === 0, [f1.length, f2.length, f3.map(x => x.m.id + (x.estorno ? '(estorno)' : '')), s3.n, f4.length, s4.n]);
  ok('A12d reserva, contagem, inspeção e confirmação no app nunca entram na fila', G().movs.filter(m => ['reserva', 'contagem', 'inspecao', 'recebimento'].indexOf(m.tipo) >= 0).every(m => !confErpFila(G()).some(x => x.m.id === m.id))); });

console.log('\n— A18 · CF-05 no mesmo estado (P7): AL-15 pelo Ver como; o backoffice segue com "Admin plataforma"');
caso('A18', () => { ini(); M(c => assinAvancar(c, '2026-10-01', { ha: 2570.23, n: 30 }));
  const pagar = (ator, k) => M(c => { const f = assinAberta(assinGarante(c).orgs.sr); return assinPagar(c, f.id, 'Pix', k, cenExigeAlc(ator, 'AL-15', 'Pagar a fatura de ' + assinComp(f.comp))); });
  const rv = G().rev; const r1 = pagar('Rui', 'k1');
  ok('A18a Rui (almoxarife) paga: recusado "decisão de Ana (gestora)", nada gravado', /Pagar a fatura de set\/2026: decisão de Ana \(gestora\)/.test(r1.erro || '') && G().rev === rv, r1);
  const r2 = pagar('Ana', 'k2'); const f = G().assin.orgs.sr.faturas.find(x => x.comp === '2026-09');
  ok('A18b Ana paga: grava "Ana (gestora)" (o formato dos outros comandos)', !r2.erro && f.paga_por === 'Ana (gestora)' && trilha().some(x => x.oq === 'Pagar fatura (simulado)' && x.quem === 'Ana (gestora)'), [r2, f.paga_por]);
  __ls['safrion.perfilDemo'] = 'Rui'; const r3 = M(c => assinConciliar(c, 'k3', 'Admin plataforma'));
  ok('A18c com o Ver como em Rui, o backoffice concilia como "Admin plataforma" (assinIni não confere AL-15)', !r3.erro && /Conciliado/.test(r3.msg), r3); delete __ls['safrion.perfilDemo'];
  ok('A18d CF-05 conta as pessoas com acesso do c.conf: 12 no seed', confComAcesso() === 12); });

console.log('\n— REV · correções da revisão adversarial (F1..F16, 09/10): cada caso falha no HEAD 9f49bf0 e passa depois');
const idx = (L, f) => L.findIndex(f);
caso('F1 ordem', () => { ini(); M(c => confAlcMudar(c, 'AL-01', { papel: 'pcp' }, 'decisão do proprietário', 'f1a', 'Ana'));
  M(c => osc_aprovar(c, 'OS-0430', 'Ana')); M(c => osc_liberar(c, 'OS-0430', false, '', 'Caio')); const L = trilha();
  const ia = idx(L, r => r.cmd === 'Configurações' && r.obj === 'AL-01' && !/^CFG-000/.test(r.src) && /v1 → v2/.test(r.ef)), i42 = idx(L, r => r.cmd === 'CMD-42' && /OS-0430/.test(r.obj)), i06 = idx(L, r => r.cmd === 'CMD-06' && /OS-0430/.test(r.obj));
  ok('F1a mesmo minuto: Alterar AL-01 → CMD-42 → CMD-06 na ordem em que foram gravados (antes: CMD-42 e CMD-06 vinham antes da alçada)', ia >= 0 && ia < i42 && i42 < i06, [ia, i42, i06]);
  const rq = G().ordens['OS-0430'].req; M(c => cenEntregar(c, rq, 'Glifosato 480', 20, 'Marcos', 'Rui'));
  M(c => estContar(c, 'INV-2611', KG, 1170, 'Paula (almoxarife)', 'bombona avariada', 'Rui')); M(c => estAprovar(c, 'INV-2611', 'Ana')); const L2 = trilha();
  const ie = idx(L2, r => r.oq === 'Entregar insumo'), ij = idx(L2, r => r.cmd === 'Ajuste');
  ok('F1b a entrega gravada antes da aprovação do ajuste vem antes dela na trilha', ie >= 0 && ij > ie, [ie, ij]);
  const sqs = G().ordens['OS-0430'].osc.ev.map(e => e.sq), sa = confLer().ev[0].sq;
  ok('F1c cada registro novo leva a ordem de gravação (sq = c.rev do comando) e ela não muda depois', sa === 1 && sqs[0] === 2 && sqs[1] === 3 && G().rev >= 6, [sa, sqs, G().rev]); });
caso('F2 R12', () => { ini(); const r1 = M(c => confAlcMudar(c, 'AL-05', { lim: 15 }, 'safra curta', 'kx', 'Ana', 1)), r2 = M(c => confAlcMudar(c, 'AL-05', { lim: 15 }, 'safra curta', 'kx', 'Ana', 1));
  ok('F2a Salvar alçada 2× com a mesma chave e o mesmo pedido: mesmo recibo, nenhum "conflito"', !r1.erro && r2.repetido && r2.recibo.id === r1.recibo.id && confLer().ev.length === 1, [r1, r2]);
  const r3 = M(c => confAlcMudar(c, 'AL-05', { lim: 12 }, 'safra curta', 'kx', 'Ana', 1)); ok('F2b mesma chave com outro pedido: conflito', /conflito/.test(r3.erro || ''), r3);
  const r4 = M(c => confAlcMudar(c, 'AL-05', { lim: 12 }, 'outra', 'ky', 'Ana', 1)); ok('F2c pedido feito sobre a v1 quando a vigente é a v2: recusa "reabra e confira"', /mudou para a v2 enquanto o painel mostrava a v1/.test(r4.erro || ''), r4);
  ini(); M(c => confPapeis(c, 'p11', ['pcp', 'gestor'], 'g', 'Ana')); M(c => confAlcMudar(c, 'AL-05', { lim: 25 }, 'chuva', 'p', 'Ana', 1));
  const c1 = M(c => confAlcConfirmar(c, 'AL-05', 'kc', 'Caio', 2)), c2 = M(c => confAlcConfirmar(c, 'AL-05', 'kc', 'Caio', 2));
  ok('F2d Confirmar 2× com a mesma chave: mesmo recibo, uma confirmação', !c1.erro && c2.repetido && c2.recibo.id === c1.recibo.id && confLer().ev.filter(e => e.tipo === 'alc-conf').length === 1, [c1, c2]);
  ini(); M(c => confAlcMudar(c, 'AL-05', { lim: 25 }, 'chuva', 'p', 'Ana', 1)); const d1 = M(c => confAlcDesistir(c, 'AL-05', 'kd', 'Ana', 2)), d2 = M(c => confAlcDesistir(c, 'AL-05', 'kd', 'Ana', 2));
  ok('F2e Desistir 2× com a mesma chave: mesmo recibo', !d1.erro && d2.repetido && d2.recibo.id === d1.recibo.id, [d1, d2]); });
const dupM = (c) => { osc_apontar(c, 'OS-0421', '26/09', 50, undefined, undefined, 'W-1'); cenIniciarTurno(c, 'OS-0421'); cenFecharTurno(c, 50, 8, undefined, '', []); return { msg: 'dup' }; };
caso('F3 AL-12', () => { ini(); M(dupM); const d = G().ordens['OS-0421'].ap.find(a => a.st === CEN_AP_DUP);
  M(c => confPapeis(c, 'p2', ['conferente'], 'k1', 'Ana')); const r = M(c => cenApDecidir(c, 'OS-0421', d.dia, 'somar', 'Marcos')); const ap = G().ordens['OS-0421'].ap.find(a => a.dia === d.dia);
  ok('F3a Marcos (apontou o dia ' + d.dia + ') decide a própria duplicidade: vale, com revisão posterior pendente no registro, no aviso e na trilha', d.quem === 'Marcos' && !r.erro && /revisão posterior pendente \(Marcos apontou o dia/.test(ap.dec.rev || '')
    && /revisão posterior/.test(r.msg) && trilha().some(x => x.cmd === 'CMD-09' && /revisão posterior pendente/.test(x.ef)), [d.quem, r, ap.dec]);
  ini(); M(dupM); const r2 = M(c => cenApDecidir(c, 'OS-0421', d.dia, 'somar', 'Paula')); const ap2 = G().ordens['OS-0421'].ap.find(a => a.dia === d.dia);
  ok('F3b Paula (não apontou) decide: sem revisão', !r2.erro && !ap2.dec.rev, ap2.dec);
  ok('F3c AL-12 diz a regra que o comando aplica', /revisão posterior/.test(G2_ALCADAS.find(a => a.id === 'AL-12').fixa)); });
caso('F4 aprovar com impedimento', () => { ini(); M(c => confAlcMudar(c, 'AL-01', { papel: 'pcp' }, 'decisão do proprietário', 'f4', 'Ana'));
  const R = ['OS-0502', 'OS-0418', 'OS-0431'].map(id => { const x = osProx(vw(id), g2pf('Ana')); return [id, x.P.btn, !!x.b, /A liberação aguarda/.test(x.P.t)]; });
  ok('F4a com AL-01 = PCP, Ana (só AL-02) vê "Aprovar vN" nas 3 ordens com estoque ou máquina impedindo a liberação; o impedimento segue no texto', R.every(x => /^Aprovar v\d+$/.test(x[1]) && !x[2] && x[3]), R);
  const a = M(c => osc_aprovar(c, 'OS-0502', 'Ana')); ok('F4b e o comando aprova (só CMD-42; a liberação continua impedida)', !a.erro && evs('OS-0502').length === 1 && G().ordens['OS-0502'].etapa === 'A liberar', a);
  M(c => { const o = c.ordens['OS-0430']; o.ins[0].dose = 7.5; return { msg: '' }; }); const x = osProx(vw('OS-0430'), g2pf('Ana'));
  ok('F4c a regra legal segue segurando a aprovação (sem "Aprovar")', !!x.b && x.b.legal && !/^Aprovar/.test(x.P.btn || ''), [x.P.btn, x.b]); });
caso('F5 CSV', () => { ini(); const L = [{ d: '2026-09-26', at: '10:00', quem: '=cmd|"/c calc"!A1', oq: '+SOMA(1,2)', obj: '-2+3', ef: '=HYPERLINK("http://exemplo.invalid","ver")', origem: '@web', src: '-5', ds: '\tx' }];
  const cel = confCsv(L).split('\r\n')[1].split(';');
  ok('F5a trilha: célula que começa com = + - @ ou tab vira texto (\' na frente); número puro (-5) fica', cel.slice(1, 6).concat(cel[7]).every(x => /^"'/.test(x)) && cel[6] === '"-5"', cel);
  M(c => assinAvancar(c, '2026-10-06', { ha: 2570.23, n: 30 })); const f = assinAberta(assinLer().orgs.sr) || assinLer().orgs.sr.faturas.slice(-1)[0];
  const csv = assinCsv(assinLer().orgs.sr, Object.assign({}, f, { eventos: [{ d: '2026-10-06', t: '=HYPERLINK("http://exemplo.invalid","ver")' }] }));
  ok('F5b fatura (assinCsv): o evento com fórmula também vira texto', /"'=HYPERLINK/.test(csv) && !/;"=/.test(csv), csv.split('\r\n').slice(-2)); });
caso('F6 contador', () => { ini(); ok('F6a seed: contadores = pessoas ativas com almoxarife (Paula, Rui); 1ª opção vazia, sem padrão', estContadores().join() === 'Paula (almoxarife),Rui (almoxarife)' && estContOpts({})[0].v === '', estContOpts({}));
  M(c => confAcesso(c, 'p6', false, 'k1', 'Ana')); const r = M(c => estContar(c, 'INV-2611', KG, 1180, 'Paula (almoxarife)', 'x', 'Rui'));
  ok('F6b Paula desativada: sai da lista e contar em nome dela é recusado, nada gravado', estContadores().join() === 'Rui (almoxarife)' && /Contador: escolha quem contou/.test(r.erro || '') && !(G().ajustes || []).length, r);
  M(c => estContar(c, 'INV-2611', KG, 1180, 'Rui (almoxarife)', 'x', 'Rui')); M(c => estRecontar(c, 'INV-2611', 'Rui')); const rec = (G().inv || {})['INV-2611'] || einvRec(G(), 'INV-2611');
  ok('F6c recontagem sem outro almoxarife ativo: contador fica vazio (a pessoa escolhe), nunca a desativada', rec && rec.contador === '', rec && rec.contador); });
caso('F7 recusar', () => { ini(); M(c => confPapeis(c, 'p11', ['pcp', 'gestor'], 'g', 'Ana')); M(c => confAlcMudar(c, 'AL-05', { lim: 25 }, 'chuva', 'p', 'Ana'));
  const r0 = M(c => confAlcRecusar(c, 'AL-05', 'r0', 'Ana')); ok('F7a quem propôs não recusa (desiste)', /use Desistir/.test(r0.erro || ''), r0);
  const n0 = nT(); const r = M(c => confAlcRecusar(c, 'AL-05', 'r1', 'Caio'));
  ok('F7b Caio (gestor) recusa: proposta sai, vigente v1 (20 %), recusa na trilha', !r.erro && !confLer().pend['AL-05'] && g2alc('AL-05').lim === 20 && nT() === n0 + 1 && trilha().some(x => x.oq === 'Recusar mudança de alçada'), r);
  ini(); M(c => confPapeis(c, 'p11', ['pcp', 'gestor'], 'g', 'Ana')); M(c => confAlcMudar(c, 'AL-05', { lim: 25 }, 'chuva', 'p', 'Ana')); const d = M(c => confAcesso(c, 'p1', false, 'k', 'Caio'));
  ok('F7c Caio desativa Ana (proponente): a proposta sai junto e a alçada não fica presa; Caio propõe outra', !d.erro && !confLer().pend['AL-05'] && /Proposta da AL-05 v2 retirada/.test(d.msg) && !M(c => confAlcMudar(c, 'AL-05', { lim: 15 }, 'reduzir', 'k2', 'Caio')).erro, d); });
caso('F8 ERP', () => { ini(); const l = G().lotes[KG]; M(c => estContar(c, 'INV-2611', KG, l.fisico - 5, 'Paula (almoxarife)', 'quebra', 'Rui')); M(c => estAprovar(c, 'INV-2611', 'Ana'));
  const t = confErpFila(G()).map(confErpT).join(' | '); ok('F8 ajuste de −5 L leva o sinal na fila do ERP', /ajuste de inventário · Glifosato 480 −5 L/.test(t), t); });
caso('F10 mutantes', () => { ini(); M(c => confAlcMudar(c, 'AL-05', { lim: 25 }, 'chuva', 'p', 'Ana'));
  const rr = ['Rui', 'Paula', 'Zé'].map(k => M(c => confAlcConfirmar(c, 'AL-05', 'c' + k, k)));
  ok('F10 M26 Rui, Paula e Zé (sem gestor nem direção) não confirmam; nada muda', rr.every(x => /decisão de/.test(x.erro || '')) && g2alc('AL-05').lim === 20 && !!confLer().pend['AL-05'], rr.map(x => x.erro));
  M(c => confPapeis(c, 'p11', ['pcp', 'gestor'], 'g', 'Ana')); const ds = M(c => confAlcDesistir(c, 'AL-05', 'd', 'Caio'));
  ok('F10 M25 outra pessoa não desiste da proposta de Ana', /Só quem propôs/.test(ds.erro || '') && !!confLer().pend['AL-05'], ds);
  ini(); M(c => confAcesso(c, 'p6', false, 'k', 'Ana')); const pa = M(c => confPapeis(c, 'p6', ['almoxarife', 'conferente', 'pcp'], 'k2', 'Ana'));
  ok('F10 M11 dar papel a pessoa desativada: recusado', /está com o acesso desativado/.test(pa.erro || ''), pa);
  ini(); M(c => confPapeis(c, 'p11', ['pcp', 'gestor'], 'g', 'Ana')); M(c => confAcesso(c, 'p1', false, 'k', 'Caio')); const crea = confP('Ana').crea; confP('Ana').crea = '2026-01-31';
  try { const ra = M(c => confAcesso(c, 'p1', true, 'k2', 'Caio')); ok('F10 M09 reativar Ana com CREA vencido: volta sem agrônomo (R4)', !ra.erro && /Volta sem o papel de agrônomo/.test(ra.msg) && confLer().pessoas.p1.papeis.indexOf('agronomo') < 0, ra); } finally { confP('Ana').crea = crea; }
  ini(); const mk = (f) => M(c => { f(c); return { msg: '' }; });
  mk(c => { c.ordens['OS-0430'].ins[0].dose = 7.5; }); const l1 = M(c => osc_aprovar(c, 'OS-0430', 'Ana'));
  ok('F10 M17 aprovar versão fora da bula: recusado, sem CMD-42', /fora da bula/.test(l1.erro || '') && !evs('OS-0430').length, l1);
  ini(); mk(c => { const x = c.ordens['OS-0430'].ins[0]; x.tot = 0; }); const l2 = M(c => osc_aprovar(c, 'OS-0430', 'Ana'));
  ok('F10 M17b aprovar com dose × área = 0: recusado', /dá 0/.test(l2.erro || '') && !evs('OS-0430').length, l2);
  ini(); mk(c => { c.ordens['OS-0511'].tipo = 'Irrigação · lâmina 12 mm'; }); const l3 = M(c => osc_aprovar(c, 'OS-0511', 'Ana'));
  ok('F10 M33 aprovar irrigação só com água: recusado (libera pela prontidão)', /só com água/.test(l3.erro || '') && !evs('OS-0511').length, l3);
  ini(); const l4 = M(c => osc_aprovar(c, 'OS-0421', 'Ana')); ok('F10 M34 aprovar ordem fora de A liberar: recusado', /não está em A liberar/.test(l4.erro || ''), l4);
  ini(); mk(c => { cenMov(c, { tipo: 'entrega', prod: 'Glifosato 480', qtd: 1, un: 'L', origem: 'web' }); }); const sem = trilha().find(r => r.oq === 'Entregar insumo' && !r.quem);
  ok('F10 M31 registro sem autor: a trilha não infere autor ("autor não registrado" no CSV)', !!sem && sem.k === '' && /"autor não registrado"/.test(confCsv([sem])), sem);
  ini(); const cv = cenClone(G()); cv.conf = confBase(); cv.conf.v = 'CONF-0-velho'; cv.conf.pessoas.p7.papeis = ['almoxarife', 'conferente'];
  ok('F10 M32 c.conf de outra versão: confLer volta ao padrão e confGarante troca pelo novo', confLer(cv) !== cv.conf && confLer(cv).pessoas.p7.papeis.indexOf('conferente') < 0 && confGarante(cv).v === CONF0.v && cv.conf.pessoas.p7.papeis.indexOf('conferente') < 0); });
caso('F11 desativar a si', () => { ini(); M(c => confPapeis(c, 'p11', ['pcp', 'gestor'], 'g', 'Ana')); const rv = G().rev; const r = M(c => confAcesso(c, 'p11', false, 'k', 'Caio'));
  ok('F11 Caio (gestor) não desativa o próprio acesso; nada gravado', /Ninguém desativa o próprio acesso/.test(r.erro || '') && G().rev === rv, r); });
caso('F12 quem confirma', () => { ini(); M(c => confAlcMudar(c, 'AL-05', { lim: 25 }, 'chuva', 'p', 'Ana')); const K = confLer();
  const r = M(c => confAlcConfirmar(c, 'AL-05', 'c', 'Rui'));
  ok('F12a sem outro gestor: o texto não manda à própria proponente', !/Ana/.test(confQuemConf(K, K.pend['AL-05'])) && !/Ana/.test(r.erro || '') && /ninguém ativo além de quem propôs/.test(r.erro || ''), [confQuemConf(K, K.pend['AL-05']), r.erro]);
  M(c => confPapeis(c, 'p11', ['pcp', 'gestor'], 'g', 'Ana')); const r2 = M(c => confAlcConfirmar(c, 'AL-05', 'c2', 'Rui'));
  ok('F12b com Caio gestor: "decisão de Caio (gestor)", sem Ana', /decisão de Caio \(gestor\)\./.test(r2.erro || ''), r2.erro); });
caso('F15 sincronização', () => { ini(); const h0 = cenAgora; cenAgora = () => '05:00';
  try { M(c => confSincronizar(c, 's1', 'Ana')); const K = confLer(); ok('F15 relógio antes do seed (05:00 < 06:40): a última sincronização do ERP não volta no tempo', K.sinc.erp === '2026-09-26 06:40' && K.sinc.lab === '2026-09-26 05:00', K.sinc); } finally { cenAgora = h0; } });
caso('F16 pausar', () => { ini(); M(c => { cenIniciarTurno(c, 'OS-0421'); return { msg: '' }; }); M(c => confAcesso(c, 'p2', false, 'k', 'Ana'));
  const r = M(c => cenPausar(c)); ok('F16 Marcos desativado: pausar o turno é recusado', /Acesso de Marcos desativado/.test(r.erro || ''), r); });

console.log('\n— INT · integração com a Colheita (merge de claude/prototipo-v44) e textos por papel (F14, 09/10): os casos (fora as referências INT1a, INT3a, F14a) falham no 3d76176 e passam aqui');
caso('INT1 app da colheita respeita o acesso', () => { ini();
  const ok0 = M(c => prContar(c, { cult: 'lg19', plantas: 20, pintado: 10, devez: 10, verde: 10, peso: '1,2', quem: 'Marcos', via: 'app', chave: 'm7-0' }));
  ok('INT1a referência: com acesso, Marcos conta pelo app (CNT-0002)', !ok0.erro && ok0.cnt.id === 'CNT-0002', ok0);
  ini(); M(c => confAcesso(c, 'p2', false, 'k', 'Ana')); const rv = G().rev; const n0 = G().producao.contagens.length;
  const a = M(c => prContar(c, { cult: 'lg19', plantas: 20, pintado: 10, devez: 10, verde: 10, peso: '1,2', quem: 'Marcos', via: 'app', chave: 'm7-1' }));
  const b = M(c => prCarga(c, { os: 'OS-0505', cx: 10, via: 'app', quem: 'Marcos', chave: 'cg-1' }));
  const d = M(c => prDescartarCarga(c, 'CG-2108', 'registro em dobro', 'Marcos', 'app'));
  ok('INT1b Marcos desativado: contagem, carga e descarte pelo app recusados "Acesso de Marcos desativado"; nada gravado', [a, b, d].every(r => /Acesso de Marcos desativado/.test(r.erro || ''))
    && G().rev === rv && G().producao.contagens.length === n0 && G().producao.cargas['CG-2108'].st === 'A pesar', [a.erro, b.erro, d.erro]);
  const w = M(c => prDescartarCarga(c, 'CG-2108', 'registro em dobro', prRec('Lagoa Grande')));
  ok('INT1c pela web (recebimento) o descarte segue', !w.erro && G().producao.cargas['CG-2108'].st === 'Descartada', w); });
caso('INT2 AL-17 publicar previsão pelo papel', () => { ini();
  ok('INT2a texto "quem publica" vem da AL-17 (Ana (agrônoma) no seed), não de nome fixo', prQuem('ag') === 'Ana (agrônoma)' && g2alc('AL-17').papeis.join() === 'agronomo', prQuem('ag'));
  M(c => confAlcMudar(c, 'AL-17', { papel: 'pcp' }, 'PCP publica a previsão de fruta', 'k17', 'Ana'));
  const r0 = M(c => prPublicar(c, 'lg19', 'Ana')); const r1 = M(c => prPublicar(c, 'lg19', 'Caio')); const v = (G().producao.previsoes.lg19 || []).slice(-1)[0];
  ok('INT2b AL-17 → PCP: Ana recusada "decisão de Caio (PCP)"; Caio publica e o registro grava "Caio (PCP)"; o texto passa a Caio', /decisão de Caio \(PCP\)/.test(r0.erro || '') && !r1.erro && v.por === 'Caio (PCP)' && prQuem('ag') === 'Caio (PCP)', [r0.erro, r1.erro, v && v.por]);
  ini(); const r2 = M(c => prPublicar(c, 'lg19', 'Ana (agrônoma)'));
  ok('INT2c o nome do registro ("Ana (agrônoma)") vira o perfil pelo 1º nome e passa pela alçada', !r2.erro && G().producao.previsoes.lg19.slice(-1)[0].por === 'Ana (agrônoma)', r2); });
caso('INT3 produção na trilha', () => { ini(); const n0 = nT();
  ok('INT3a o seed da produção (cargas, previsões, reserva) é histórico anterior: a trilha segue com 16', n0 === 16 && !trilha().some(r => r.cmd === 'Colheita'), n0);
  M(c => prPublicar(c, 'lg19', 'Ana'));
  const rc = M(c => prReceber(c, { carga: 'CG-2108', ticket: 'TK-4600', bruto: '18000', tara: '6000', cond: 'Com avaria', quem: prRec('Lagoa Grande'), chave: 'rc1' }));
  const lid = rc.L && rc.L.id; const lb = M(c => prLiberarLote(c, lid, 'Marta'));
  const es = M(c => prEstornar(c, 'CG-2107', 'ticket errado', prRec('Lagoa Grande')));
  const L = trilha().filter(r => r.cmd === 'Colheita');
  ok('INT3b publicar, pesar, liberar e estornar: +4 linhas com autor e objeto, lidas do registro', !rc.erro && !lb.erro && !es.erro && L.length === 4 && nT() === n0 + 4
    && L.map(r => r.oq).join('|') === 'Publicar previsão de colheita · AL-17|Pesar e receber carga|Liberar lote de produto|Estornar carga'
    && L[0].quem === 'Ana (agrônoma)' && L[1].quem === 'Lúcia' && L[2].quem === 'Marta (qualidade)' && /^MP-\d+ · CG-2108 · L\d\d-\d+$/.test(L[1].obj) && /^−/.test(L[3].ef), [rc.erro, lb.erro, es.erro, L.map(r => [r.oq, r.quem, r.obj, r.ef])]);
  ok('INT3c ordem de gravação no mesmo minuto (sq): publicar antes de pesar, pesar antes de liberar', L.every((r, i) => !i || r.sq > L[i - 1].sq), L.map(r => r.sq));
  ok('INT3d filtro por pessoa: Lúcia tem a pesagem e o estorno', L.filter(r => r.k === 'Lúcia').length === 2, L.map(r => r.k)); });
caso('INT4 texto de quem recebe pelo almoxarife ativo', () => { ini(); M(c => confAcesso(c, 'p7', false, 'k', 'Ana'));
  /* reverificação 10/10: prRec é só o TEXTO de quem deve pesar; o autor do ato é quem age (REV1) */
  ok('INT4 Rui desativado: o texto "quem pesa" na Santa Rita é o almoxarife ativo (Paula), não o nome fixo; o autor do ato não sai daqui (REV1)', prRec('Santa Rita') === 'Paula (almoxarife)' && prRec('Lagoa Grande') === 'Lúcia', [prRec('Santa Rita'), prRec('Lagoa Grande')]); });
caso('F14 textos da O.S. pela alçada', () => { ini();
  ok('F14a padrão (Ana nas duas alçadas): "Ana (agrônoma) confere, ajusta se precisar e libera"', /^Ana \(agrônoma\) confere, ajusta se precisar e libera\./.test(vw('OS-0430').cond), vw('OS-0430').cond);
  M(c => confAlcMudar(c, 'AL-01', { papel: 'pcp' }, 'decisão do proprietário', 'kf14', 'Ana'));
  ok('F14b AL-01 → PCP: OS-0430 diz "… e aprova; Caio (PCP) libera"', /^Ana \(agrônoma\) confere, ajusta se precisar e aprova; Caio \(PCP\) libera\./.test(vw('OS-0430').cond), vw('OS-0430').cond);
  const r = M(c => osc_nova(c, { id: 'OS-0498', tipo: 'Teste', talhao: 'T1', area: 1, versao: 'v1', resp: '—', ins: [], selos: [] }));
  ok('F14c ordem nova: a mensagem nomeia quem aprova e quem libera', /Ana \(agrônoma\) confere, ajusta se precisar e aprova; Caio \(PCP\) libera para execução\./.test(r.msg || ''), r);
  const ir = (String(FONTES.irr).match(/cond: '(Produto na água:[^']*)'/) || [])[1] || '';
  ok('F14g v2 da irrigação (produto na água, irrReclassCen): o texto genérico também nomeia quem aprova e quem libera', /^Produto na água: Ana \(agrônoma\) confere, ajusta se precisar e aprova; Caio \(PCP\) libera; /.test(osCondLib(ir)), [ir, osCondLib(ir)]); });
caso('F14 almoxarife nos textos do app', () => { ini();
  ok('F14d padrão: almoxarife Rui, "ao Rui"; entrega sem registro: Rui', cenAlmoxNome() === 'Rui' && cenAoAlmox() === 'ao Rui' && cenEntPor(G(), 'REQ-035') === 'Rui', [cenAlmoxNome(), cenAoAlmox()]);
  M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 5, 'Marcos', 'Paula'));
  ok('F14e quem entregou vem do movimento (Paula)', cenEntPor(G(), 'REQ-035') === 'Paula', cenEntPor(G(), 'REQ-035'));
  M(c => confAcesso(c, 'p7', false, 'k', 'Ana'));
  ok('F14f Rui desativado: o almoxarife dos textos é Paula ("à Paula")', cenAlmoxNome() === 'Paula' && cenAoAlmox() === 'à Paula', [cenAlmoxNome(), cenAoAlmox()]); });

console.log('\n— INT5 · beneficiamento (merge de claude/prototipo-v44 0644b1b, CONF-D43): atos da ordem e decisões da Qualidade na trilha, com autor e ordem de gravação');
caso('INT5 beneficiamento na trilha', () => { ini(); const n0 = nT(); const s0 = trilha().some(x => /^BEN:/.test(x.id) || x.cmd === 'Beneficiamento'); const B = f => benMudar(f);
  const a = B(c => benConcluir(c, 'OB-0110', 'Igor')); const b = B(c => benConferir(c, 'OB-0110', 'Paula'));
  const d = M(c => cenDevolver(c, 'REQ-030', BENC.cx.item, 60, true, 'Rui')); const f = B(c => benFechar(c, 'OB-0110', 'Igor'));
  const lid = (f.lotes || [])[0]; const r = B(c => benResultado(c, lid, 'Conforme', '', 'Marta')); const l = B(c => benDecidir(c, lid, 'Liberar', {}, 'Marta'));
  const T = trilha(); const H = T.filter(x => /^BEN:OB-0110:/.test(x.id)); const Q = T.filter(x => x.cmd === 'Beneficiamento' && /^MP-/.test(x.id));
  const er = [a, b, d, f, r, l].map(x => x.erro).filter(Boolean);
  ok('INT5a o histórico das OB-0110 e OB-0112 que veio do seed não entra: a trilha do seed segue com 16', n0 === 16 && !s0, [n0, s0]);
  ok('INT5b enviar para conferência (Igor; era "Execução concluída" antes do faa47c7), conferir (Paula) e fechar (Igor, CMD-23): linhas do histórico da OB-0110 com autor, lidas do registro', !er.length
    && JSON.stringify(H.map(x => [x.oq.replace(/ ·.*$/, ''), x.k, x.cmd]).filter(x => /^(Enviada para conferência|Balanço conferido|Processo fechado)/.test(x[0])))
       === JSON.stringify([['Enviada para conferência', 'Igor', 'Beneficiamento'], ['Balanço conferido', 'Paula', 'Beneficiamento'], ['Processo fechado (CMD-23)', 'Igor', 'CMD-23']]), [er, H.map(x => [x.oq, x.k, x.cmd])]);
  ok('INT5c resultado e liberação do lote de produção pela Qualidade: 2 linhas "Beneficiamento" por Marta (qualidade)', Q.map(x => x.oq).join('|') === 'Registrar resultado da inspeção|Liberar lote de produto'
    && Q.every(x => x.quem === 'Marta (qualidade)' && x.obj.indexOf(lid) >= 0), Q.map(x => [x.oq, x.quem, x.obj]));
  const S = H.filter(x => /^(Enviada para conferência|Balanço conferido|Processo fechado)/.test(x.oq)).concat(Q).map(x => x.sq);
  ok('INT5d ordem de gravação (benMudar carimba como o cenMudar): concluir < conferir < fechar < resultado < liberar', S.length === 5 && S.every((v, i) => v > 0 && (!i || v > S[i - 1])), S);
  ok('INT5e filtro por pessoa: Marta tem as duas decisões; Igor, concluir e fechar', T.filter(x => x.k === 'Marta').length === 2 && T.filter(x => x.k === 'Igor').length >= 2, T.filter(x => x.k === 'Marta' || x.k === 'Igor').map(x => x.oq)); });

caso('INT5 cancelar ordem de beneficiamento (a47578f, BEN-D22)', () => { ini(); const n0 = nT();
  const r = benMudar(c => benCancelar(c, 'OB-0112', 'entrada mudou com o estorno', 'Igor', 'k-canc')); const T = trilha().filter(x => /^BEN:OB-0112:/.test(x.id));
  ok('INT5f cancelar a OB-0112 em A liberar (Igor): +1 linha "Ordem cancelada · v1" com autor Igor e o motivo no efeito', !r.erro && nT() === n0 + 1 && T.length === 1
    && /^Ordem cancelada/.test(T[0].oq) && T[0].k === 'Igor' && /entrada mudou com o estorno/.test(T[0].ef), [r.erro, T.map(x => [x.oq, x.quem, x.ef])]);
  ini(); M(c => confAcesso(c, pid('Igor'), false, 'k-d', 'Ana')); const rv = G().rev; const r2 = benMudar(c => benCancelar(c, 'OB-0112', 'teste', 'Igor', 'k-canc2'));
  ok('INT5g NEGATIVO Igor desativado no CF-01 não cancela (acesso pelo estado de Configurações): recusado com "decisão de Ana (gestora)", nada gravado', /decisão de Ana \(gestora\)/.test(r2.erro || '') && G().rev === rv && G().ordens['OB-0112'].etapa === 'A liberar', [r2, G().rev, rv]); });

caso('INT5 pedir mais caixas (3b1e7e2, complemento da mesma REQ)', () => { ini(); const n0 = nT();
  const r = benMudar(c => benComplementar(c, 'OB-0110', 1, 'Igor', { chave: 'k-cx' })); const T = trilha().filter(x => /^BEN:OB-0110:/.test(x.id) && /^Caixas pedidas/.test(x.oq));
  ok('INT5h pedir 1 caixa na OB-0110 (Igor): +1 linha "Caixas pedidas" com autor Igor, lida do histórico da ordem', !r.erro && nT() === n0 + 1 && T.length === 1 && T[0].k === 'Igor', [r.erro || r.msg, T.map(x => [x.oq, x.quem])]);
  const r2 = benMudar(c => benComplementar(c, 'OB-0110', 1, 'Igor', { chave: 'k-cx' }));
  ok('INT5i a mesma chave repetida não grava outra linha (recibo da ordem)', !r2.erro && nT() === n0 + 1, [r2, nT() - n0]);
  ini(); M(c => confAcesso(c, pid('Igor'), false, 'k-d', 'Ana')); const rv = G().rev; const r3 = benMudar(c => benComplementar(c, 'OB-0110', 1, 'Igor', { chave: 'k-cx2' }));
  ok('INT5j NEGATIVO Igor desativado no CF-01 não pede caixas: recusado, nada gravado', !!r3.erro && G().rev === rv, [r3, G().rev, rv]); });

console.log('\n— REV · reverificação adversarial do 8be23d8 (10/10): cada caso, fora as referências, reprova no 8be23d8 (REV2: no mutante M9)');
/* O.S. de colheita sintética na Santa Rita (cultivo c8, onde o almoxarife recebe), liberada por Ana; Ver como = perfil guardado (a web passa g2perfil()) */
const osSR = () => { M(c => osc_nova(c, { id: 'OS-0599', tipo: 'Colheita · semana 39 · Mamão', talhao: 'T-SR', area: 10, versao: 'v1', resp: 'Marcos', ins: [], selos: [], cult: 'c8' }));
  return M(c => osc_liberar(c, 'OS-0599', false, '', 'Ana')); };
const kSR = (tk, ch, quem) => ({ os: 'OS-0599', ticket: tk, bruto: '5000', tara: '1000', cond: 'Íntegra', frutos: '4000', dcol: '2026-09-25', chave: ch, quem });
const verComo = k => { __ls['safrion.perfilDemo'] = k; };
caso('REV1 colheita pela web confere quem age', () => { ini(); const l0 = osSR(); const fz = prFazDaOS(G(), G().ordens['OS-0599']);
  ok('REV1 referência: OS-0599 de colheita na Santa Rita liberada por Ana', !l0.erro && fz === 'Santa Rita' && G().ordens['OS-0599'].etapa === 'Liberadas', [l0.erro, fz]);
  verComo('Zé'); const rv = G().rev; const n0 = Object.keys(G().producao.cargas).length;
  const a = M(c => prReceber(c, kSR('TK-9001', 'W-REC-z1', g2perfil()))); const b = M(c => prReceber(c, kSR('TK-9001', 'W-REC-z2')));
  ok('REV1a NEGATIVO Ver como Zé (mecânico) pesa e recebe na Santa Rita (perfil passado pela tela ou o da sessão): recusado "decisão de Rui (almoxarife)…", nada gravado',
    [a, b].every(r => /Pesar e receber .*: decisão de Rui \(almoxarife\)/.test(r.erro || '')) && G().rev === rv && Object.keys(G().producao.cargas).length === n0, [a.erro, b.erro]);
  verComo('Rui'); const r = M(c => prReceber(c, kSR('TK-9001', 'W-REC-r1', g2perfil()))); const gid = r.g && r.g.id;
  ok('REV1b Ver como Rui (almoxarife): pesa e o registro grava "Rui (almoxarife)", lido pela trilha', !r.erro && G().producao.cargas[gid].quemRec === 'Rui (almoxarife)'
    && trilha().some(x => x.oq === 'Pesar e receber carga' && x.quem === 'Rui (almoxarife)' && x.obj.indexOf(gid) >= 0), r.erro);
  verComo('Zé'); const rv2 = G().rev; const e = M(c => prEstornar(c, gid, 'ticket trocado', g2perfil()));
  ok('REV1c NEGATIVO Zé estorna a carga recebida: recusado, a carga segue Recebida e nada é gravado', /Estornar a .*: decisão de Rui \(almoxarife\)/.test(e.erro || '') && G().rev === rv2 && G().producao.cargas[gid].st === 'Recebida', e.erro);
  verComo('Rui'); const e2 = M(c => prEstornar(c, gid, 'ticket trocado', g2perfil()));
  ok('REV1d Rui estorna: o estorno grava "Rui (almoxarife)" (movimento e carga)', !e2.erro && G().producao.cargas[gid].estorno.quem === 'Rui (almoxarife)'
    && G().producao.movs.some(m => m.tipo === 'estorno' && m.carga === gid && m.quem === 'Rui (almoxarife)'), e2.erro); });
caso('REV1 almoxarife desativado não vira autor', () => { ini(); osSR(); M(c => confAcesso(c, 'p7', false, 'k', 'Ana')); verComo('Zé');
  const rv = G().rev; const a = M(c => prReceber(c, kSR('TK-9002', 'W-REC-z3', g2perfil()))); const b = M(c => prReceber(c, kSR('TK-9002', 'W-REC-r3', 'Rui (almoxarife)')));
  ok('REV1e NEGATIVO Rui desativado: Zé não pesa em nome de Paula, e o nome "Rui (almoxarife)" não passa; nada gravado', /decisão de Paula \(almoxarife\)/.test(a.erro || '') && /decisão de Paula \(almoxarife\)/.test(b.erro || '') && G().rev === rv, [a.erro, b.erro]);
  verComo('Paula'); const p = M(c => prReceber(c, kSR('TK-9002', 'W-REC-p3', g2perfil())));
  const T = trilha().filter(x => x.k === 'Paula' && x.cmd === 'Colheita');
  ok('REV1f Paula pesa: o filtro "Paula" do CF-04 tem só o ato que ela fez (1 pesagem)', !p.erro && T.length === 1 && T[0].oq === 'Pesar e receber carga' && T[0].quem === 'Paula (almoxarife)', [p.erro, T.map(x => [x.oq, x.quem])]); });
caso('REV1 descartar carga a pesar na Santa Rita', () => { ini(); osSR(); const cg = M(c => prCarga(c, { os: 'OS-0599', cx: 50, via: 'app', quem: 'Marcos', chave: 'APP-SR-1' })); const id = cg.g && cg.g.id;
  verComo('Zé'); const rv = G().rev; const d0 = M(c => prDescartarCarga(c, id, 'registro em dobro', g2perfil()));
  ok('REV1g NEGATIVO Zé descarta pela web a carga a pesar da Santa Rita: recusado, nada gravado', !cg.erro && /Descartar a .*: decisão de Rui \(almoxarife\)/.test(d0.erro || '') && G().rev === rv && G().producao.cargas[id].st === 'A pesar', [cg.erro, d0.erro]);
  verComo('Rui'); const d1 = M(c => prDescartarCarga(c, id, 'registro em dobro', g2perfil()));
  ok('REV1h Rui descarta: grava "Rui (almoxarife)" e a trilha mostra o autor', !d1.erro && G().producao.cargas[id].descarte.quem === 'Rui (almoxarife)' && trilha().some(x => x.oq === 'Descartar carga a pesar' && x.quem === 'Rui (almoxarife)'), d1.erro);
  ini(); verComo('Zé'); const lg = M(c => prEstornar(c, 'CG-2107', 'ticket errado', g2perfil()));
  ok('REV1i risco declarado (CONF-D41), agora com o perfil passado pela tela: na Lagoa Grande quem recebe é Lúcia, fora do CD-04; o estorno segue gravado como "Lúcia" até ela entrar no cadastro', !lg.erro && G().producao.cargas['CG-2107'].estorno.quem === 'Lúcia', lg.erro); });
caso('REV2 aprovar (CMD-42) confere a AL-02', () => { ini(); const rv = G().rev;
  const n = ['Caio', 'Rui', 'Paula', 'Zé', 'Igor', 'Marta'].map(k => M(c => osc_aprovar(c, 'OS-0430', k)));
  ok('REV2a NEGATIVO quem não tem a AL-02 (Caio, Rui, Paula, Zé, Igor, Marta) não aprova a v1: "decisão de Ana (agrônoma)", nada gravado, sem CMD-42',
    n.every(r => /Aprovar a v1 da OS-0430 \(CMD-42\): decisão de Ana \(agrônoma\)/.test(r.erro || '')) && G().rev === rv && !evs('OS-0430').length, n.map(r => r.erro));
  M(c => confAlcMudar(c, 'AL-01', { papel: 'pcp' }, 'decisão do proprietário', 'k-rev2', 'Ana')); const rv2 = G().rev;
  const a = M(c => osc_aprovar(c, 'OS-0430', 'Caio')); const l = M(c => osc_liberar(c, 'OS-0430', false, '', 'Caio'));
  ok('REV2b NEGATIVO com a AL-01 no PCP, Caio não aprova nem libera sozinho (cenário do mutante M9): nada gravado', /decisão de Ana \(agrônoma\)/.test(a.erro || '') && /Aprovação agronômica da v1 da OS-0430 pendente/.test(l.erro || '')
    && G().rev === rv2 && !evs('OS-0430').length && G().ordens['OS-0430'].etapa === 'A liberar', [a.erro, l.erro]);
});
caso('REV3 ajuste de inventário: quem contou e a causa', () => { ini();
  const k = M(c => estContar(c, 'INV-2611', KG, 1180, 'Paula (almoxarife)', 'bombona avariada', 'Rui')); const a = M(c => estAprovar(c, 'INV-2611', 'Ana'));
  const r = trilha().find(x => x.oq === 'Aprovar ajuste de inventário');
  ok('REV3a contou Paula, registrou Rui: a trilha diz "contou: Paula (almoxarife)", "registrou: Rui (almoxarife)" e a causa; nunca "contou: Rui"', !k.erro && !a.erro && !!r
    && /contou: Paula \(almoxarife\)/.test(r.ef) && /registrou: Rui \(almoxarife\)/.test(r.ef) && /causa: bombona avariada/.test(r.ef) && !/contou: Rui/.test(r.ef), [k.erro, a.erro, r && r.ef]);
  const csv = confCsv([r]); ok('REV3b o CSV repete o mesmo efeito (contou: Paula; causa)', /contou: Paula \(almoxarife\)/.test(csv) && /causa: bombona avariada/.test(csv) && !/contou: Rui/.test(csv), csv.slice(0, 400));
  ini(); M(c => estContar(c, 'INV-2611', KG, 1180, 'Paula (almoxarife)', 'bombona avariada', 'Rui')); M(c => estRecontar(c, 'INV-2611', 'Rui'));
  const q = trilha().find(x => x.oq === 'Recusar ajuste (recontar)');
  ok('REV3c recontagem pedida por Rui: autor Rui; quem contou segue Paula, com a causa', !!q && q.quem === 'Rui (almoxarife)' && /contou: Paula \(almoxarife\)/.test(q.ef) && /causa: bombona avariada/.test(q.ef) && !/contou: Rui/.test(q.ef), q && q.ef);
  ini(); M(c => estContar(c, 'INV-2611', KG, 1180, 'Rui (almoxarife)', 'bombona avariada', 'Rui')); M(c => estAprovar(c, 'INV-2611', 'Ana'));
  const s = trilha().find(x => x.oq === 'Aprovar ajuste de inventário');
  ok('REV3d referência: contou e registrou a mesma pessoa (Rui): "contou: Rui (almoxarife)" uma vez, sem "registrou"', !!s && /contou: Rui \(almoxarife\)/.test(s.ef) && !/registrou/.test(s.ef), s && s.ef); });
caso('REV4 enviar para conferência e encerrar gravam quem agiu', () => { ini(); const n0 = nT(); verComo('Zé'); const rv = G().rev;
  const e = M(c => osc_encerrar(c, 'OS-0508', g2perfil())); const T = trilha().filter(x => x.obj === 'OS-0508');
  ok('REV4a Zé encerra a OS-0508 (Em conferência): +1 linha "Encerrar O.S. · CMD-10" por "Zé (mecânico)", Em conferência → Encerradas', !e.erro && G().rev === rv + 1 && nT() === n0 + 1
    && T.length === 1 && T[0].oq === 'Encerrar O.S. · CMD-10' && T[0].quem === 'Zé (mecânico)' && T[0].ef === 'Em conferência → Encerradas' && /por Zé \(mecânico\)/.test(e.msg || ''), [e.erro || e.msg, T.map(x => [x.oq, x.quem])]);
  ini(); M(c => confAcesso(c, pid('Zé'), false, 'k', 'Ana')); const rv2 = G().rev; const d = M(c => osc_encerrar(c, 'OS-0508', 'Zé'));
  ok('REV4b NEGATIVO Zé desativado: encerrar recusa "sem o perfil de quem age", nada gravado', /sem o perfil de quem age/.test(d.erro || '') && G().rev === rv2 && G().ordens['OS-0508'].etapa === 'Em conferência', d.erro);
  ini(); M(c => { c.ordens['OS-0421'].saldo = 0; return { msg: '' }; }); verComo('Paula');
  const k = M(c => osc_conferencia(c, 'OS-0421')); const f = M(c => osc_encerrar(c, 'OS-0508', 'Ana')); const U = trilha().filter(x => /CMD-(08|10)/.test(x.oq));
  ok('REV4c enviar a OS-0421 para conferência sem ator explícito usa o da sessão (Paula); encerrar a OS-0508 por Ana: CMD-08 e CMD-10 com autor e na ordem de gravação', !k.erro && !f.erro && U.length === 2
    && U[0].oq === 'Enviar para conferência · CMD-08' && U[0].quem === 'Paula (almoxarife)' && U[1].oq === 'Encerrar O.S. · CMD-10' && U[1].quem === 'Ana (gestora)' && U[1].sq > U[0].sq, [k.erro, f.erro, U.map(x => [x.oq, x.quem, x.sq])]); });
caso('REV5 identidade estável da linha da trilha', () => { ini(); const T0 = trilha(); const lu = T0.find(x => x.obj === 'Lucas');
  M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 5, 'Marcos', 'Rui')); const T1 = trilha(); const lu1 = T1.find(x => x.uid === (lu || {}).uid);
  ok('REV5a toda linha tem uid único (antes e depois de gravar)', [T0, T1].every(T => T.every(x => !!x.uid) && new Set(T.map(x => x.uid)).size === T.length), T1.map(x => x.uid).slice(0, 5));
  ok('REV5b outra fonte grava (entrega no Estoque): o uid da linha de Lucas continua apontando para Lucas, embora a posição (seq) tenha mudado', !!lu && !!lu1 && lu1.obj === 'Lucas' && lu1.oq === lu.oq && lu1.d === lu.d
    && (T1.find(x => x.seq === lu.seq) || {}).obj !== 'Lucas', [lu && lu.uid, lu1 && lu1.obj, (T1.find(x => x.seq === (lu || {}).seq) || {}).obj]); });
caso('REV6 ninguém retira todos os próprios papéis', () => { ini(); M(c => confPapeis(c, 'p11', ['pcp', 'gestor'], 'k1', 'Ana')); verComo('Ana'); const rv = G().rev; const n0 = confLer().ev.length;
  const r = M(c => confPapeis(c, 'p1', [], 'k2', g2perfil()));
  ok('REV6a NEGATIVO Ana (com Caio gestor) retira os próprios gestora e agrônoma: recusado com o motivo; nada gravado; o Ver como segue Ana', /Ninguém retira todos os próprios papéis/.test(r.erro || '') && G().rev === rv && confLer().ev.length === n0 && g2perfil().k === 'Ana', [r.erro, g2perfil().k]);
  ini(); M(c => confPapeis(c, 'p11', ['pcp', 'gestor'], 'k1', 'Ana')); verComo('Ana'); const ok1 = M(c => confPapeis(c, 'p1', ['gestor'], 'k3', 'Ana'));
  ok('REV6b referência (R3): retirar parte dos próprios papéis segue valendo (Ana fica só gestora) e o Ver como segue Ana', !ok1.erro && g2perfil().k === 'Ana' && !g2papel('Ana', 'agronomo'), ok1.erro);
  ini(); M(c => confPapeis(c, 'p11', ['pcp', 'gestor'], 'k1', 'Ana')); const c2 = M(c => confPapeis(c, 'p1', [], 'k4', 'Caio'));
  ok('REV6c referência: outra pessoa (Caio, gestor) retira os papéis de Ana: vale (não é o próprio)', !c2.erro && !g2pf('Ana'), c2.erro); });

console.log('\n— REV2 · rodada de 13/10: achados S3/S4 restantes da reverificação e os de base pequenos (cada caso, fora as referências, reprova no 8be23d8 ou no mutante)');
caso('REV7 sincronizar e exportar conferem quem age (mutante M13)', () => { ini(); M(c => confAcesso(c, pid('Paula'), false, 'k-p', 'Ana')); const rv = G().rev; const n0 = confLer().ev.length;
  const s = M(c => confSincronizar(c, 'k-s1', 'Paula')); const e = M(c => confExportar(c, 3, 'sem filtros', 'k-e1', 'Paula'));
  const f = M(c => confExportar(c, 3, 'sem filtros', 'k-e2', { k: 'Xyz', papeis: { gestor: 'gestor' } }));
  ok('REV7a NEGATIVO Paula desativada (e um perfil forjado fora do cadastro) não sincroniza nem baixa a trilha: "sem o perfil de quem age", nada gravado',
    [s, e, f].every(r => /sem o perfil de quem age/.test(r.erro || '')) && G().rev === rv && confLer().ev.length === n0, [s.erro, e.erro, f.erro]);
  const r = M(c => confSincronizar(c, 'k-s2', 'Rui')); const ev = confLer().ev.slice(-1)[0] || {};
  ok('REV7b referência: Rui (ativo) sincroniza e o evento grava "Rui (almoxarife)"', !r.erro && ev.quem === 'Rui (almoxarife)', [r.erro, ev.quem]); });
caso('REV8 a mesma chave de quem inicia não duplica dispensa, entrega nem recebimento (ENG-021/022)', () => { ini(); const n0 = nT(); const o = () => G().ordens['OS-0421'];
  const d1 = M(c => osc_dispensar(c, 'OS-0421', 5, 'chuva', 'Ana', 'W-DSP-1')); const s1 = o().saldo; const d2 = M(c => osc_dispensar(c, 'OS-0421', 5, 'chuva', 'Ana', 'W-DSP-1'));
  ok('REV8a dispensa 2× com a mesma chave: 1 CMD-47, o saldo baixa uma vez, 1 linha na trilha; a 2ª responde "já registrado"', !d1.erro && !!d2.repetido && o().osc.disps.length === 1 && o().saldo === s1 && nT() === n0 + 1,
    [d1.erro, d2.erro || d2.msg, o().osc.disps.length, nT() - n0]);
  const d3 = M(c => osc_dispensar(c, 'OS-0421', 3, 'chuva', 'Ana', 'W-DSP-1'));
  ok('REV8b NEGATIVO mesma chave com outro conteúdo (3 ha): conflito, nada gravado', /conflito, nada gravado/.test(d3.erro || '') && o().osc.disps.length === 1 && o().saldo === s1, d3.erro);
  const nm = G().movs.length; const ne = trilha().filter(x => x.oq === 'Entregar insumo').length;
  const e1 = M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 5, 'Marcos', 'Rui', 'W-ENT-1')); const e2 = M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 5, 'Marcos', 'Rui', 'W-ENT-1'));
  ok('REV8c entrega 2× com a mesma chave: 1 movimento e 1 linha "Entregar insumo" na trilha', !e1.erro && !!e2.repetido && G().movs.length === nm + 1 && trilha().filter(x => x.oq === 'Entregar insumo').length === ne + 1,
    [e1.erro, e2.erro || e2.msg, G().movs.length - nm]);
  const lk = 'Ureia 45%|U26-01'; const f0 = (G().lotes[lk] || { fisico: 0 }).fisico;
  const r1 = M(c => cenReceber(c, 'Ureia 45%', 'U26-01', 100, 'kg', 'Galpão 1', '12/2027', 'NF-9001', true, 'Rui', 'W-RNF-1'));
  const r2 = M(c => cenReceber(c, 'Ureia 45%', 'U26-01', 100, 'kg', 'Galpão 1', '12/2027', 'NF-9001', true, 'Rui', 'W-RNF-1'));
  ok('REV8d recebimento 2× com a mesma chave: 1 movimento e o lote soma 100 kg uma vez', !r1.erro && !!r2.repetido && G().movs.length === nm + 2 && G().lotes[lk].fisico === f0 + 100, [r1.erro, r2.erro || r2.msg, G().lotes[lk].fisico - f0]);
  /* as funções da tela do Estoque (o formulário passa a chave): entregar e receber */
  const rq = 'REQ-035'; const n1 = G().movs.length;
  const w1 = M(c => estEntregar(c, rq, 'Fungicida A', 4, 'Marcos', 'Rui', 'W-ENT-2')); const w2 = M(c => estEntregar(c, rq, 'Fungicida A', 4, 'Marcos', 'Rui', 'W-ENT-2'));
  const d = { id: 'rT1', nf: 'NF 7001', data: '', ped: '', item: 'Ureia 45%', un: 'kg', qtd_nf: 50, conf: 50, apto: 50, quar: 0, lote: 'U26-01', val: '12/2027', local: 'Galpão 1', div: 'Sem divergência', obs: '' };
  const f1 = G().lotes[lk].fisico; const x1 = M(c => estReceber(c, d, 'Rui', 'W-REC-2')); const x2 = M(c => estReceber(c, d, 'Rui', 'W-REC-2'));
  ok('REV8e tela do Estoque: entregar e receber 2× com a chave do formulário = 1 entrega e 1 recebimento', !w1.erro && !!w2.repetido && !x1.erro && !!x2.repetido && G().movs.length === n1 + 2 && G().lotes[lk].fisico === f1 + 50,
    [w1.erro, w2.erro || w2.msg, x1.erro, x2.erro || x2.msg, G().movs.length - n1]); });
caso('REV9 registro de origem único por ato', () => { ini(); M(c => osc_dispensar(c, 'OS-0421', 5, 'chuva', 'Ana')); M(c => osc_dispensar(c, 'OS-0421', 3, 'máquina', 'Ana'));
  const D = trilha().filter(x => x.cmd === 'CMD-47');
  ok('REV9a duas dispensas da OS-0421: "Registro de origem" diferente em cada uma (nº 1 e nº 2), no detalhe e no CSV', D.length === 2 && D[0].src !== D[1].src && /nº 1$/.test(D[0].src) && /nº 2$/.test(D[1].src)
    && confCsv(D).indexOf(D[0].src) >= 0 && confCsv(D).indexOf(D[1].src) >= 0, D.map(x => x.src));
  M(c => osc_liberar(c, 'OS-0430', false, '', 'Ana')); M(c => cenEntregar(c, 'REQ-035', 'Fungicida A', 5, 'Marcos', 'Rui'));
  benMudar(c => benConcluir(c, 'OB-0110', 'Igor')); benMudar(c => benConferir(c, 'OB-0110', 'Paula'));
  const T = trilha().filter(x => x.src); const dup = T.map(x => x.src).filter((s, i, a) => a.indexOf(s) !== i);
  ok('REV9b trilha com O.S., Estoque e beneficiamento: nenhum "Registro de origem" repetido', !dup.length, dup.slice(0, 5)); });
caso('REV10 irrigação só com água: o CMD-06 tem autor', () => { ini();   /* a semente não tem irrigação só com água em A liberar: emite uma, como a tela */
  M(c => osc_nova(c, { id: 'OS-0598', tipo: 'Irrigação · lâmina 12 mm', talhao: 'P1', area: 10, versao: 'v1', resp: 'Marcos', ins: [], selos: [] })); const W = G().ordens['OS-0598'];
  M(c => confAcesso(c, pid('Paula'), false, 'k-p', 'Ana')); const rv = G().rev;
  const a = M(c => osc_liberar(c, W.id, true, '', { k: 'Paula' }));
  ok('REV10a NEGATIVO Paula desativada libera a irrigação só com água: recusado "sem o perfil de quem age", segue em A liberar, nada gravado',
    !!W && /sem o perfil de quem age/.test(a.erro || '') && G().rev === rv && G().ordens[W.id].etapa === 'A liberar', [W && W.id, a.erro]);
  const n0 = nT(); const b = M(c => osc_liberar(c, W.id, true, '', 'Caio')); const o = G().ordens[W.id]; const T = trilha().filter(x => x.cmd === 'CMD-06' && x.obj.indexOf(W.id) === 0);
  ok('REV10b Caio libera pela prontidão: CMD-06 gravado com "Caio (PCP)", sem CMD-42; a trilha ganha 1 linha "irrigação só com água"', !b.erro && o.etapa === 'Liberadas' && nT() === n0 + 1 && T.length === 1
    && T[0].quem === 'Caio (PCP)' && /só com água/.test(T[0].ef) && !(o.osc.ev || []).some(e => e.cmd === 'CMD-42') && /por Caio \(PCP\)/.test(b.msg || ''), [b.erro || b.msg, T.map(x => [x.quem, x.ef])]); });
caso('REV11 BEN: a mesma pessoa no fato e na decisão fica com revisão posterior (padrão 2)', () => { ini(); M(c => confPapeis(c, pid('Igor'), ['producao', 'conferente'], 'k1', 'Ana'));
  const a = benMudar(c => benConcluir(c, 'OB-0110', 'Igor')); const b = benMudar(c => benConferir(c, 'OB-0110', 'Igor')); const o = G().ordens['OB-0110']; const h = o.ben.hist.slice(-1)[0] || {};
  ok('REV11a Igor (produção e conferência) confere o próprio balanço: vale, com "revisão posterior pendente" no registro, no histórico, no aviso e na trilha',
    !a.erro && !b.erro && /revisão posterior pendente \(Igor/.test((o.ben.conf || {}).rev || '') && /revisão posterior pendente/.test(h.det || '') && /revisão posterior pendente/.test(b.msg || '')
    && trilha().some(x => /^Balanço conferido/.test(x.oq) && /revisão posterior pendente/.test(x.ef)), [a.erro, b.erro, o.ben.conf, h.det]);
  ini(); benMudar(c => benConcluir(c, 'OB-0110', 'Igor')); const c2 = benMudar(c => benConferir(c, 'OB-0110', 'Paula'));
  ok('REV11b referência: Paula confere a ordem que Igor produziu, sem revisão posterior', !c2.erro && !(G().ordens['OB-0110'].ben.conf || {}).rev, c2.erro);
  ini(); M(c => confPapeis(c, pid('Igor'), ['producao', 'qualidade'], 'k2', 'Ana')); const B = f => benMudar(f);
  B(c => benConcluir(c, 'OB-0110', 'Igor')); B(c => benConferir(c, 'OB-0110', 'Paula')); M(c => cenDevolver(c, 'REQ-030', BENC.cx.item, 60, true, 'Rui')); const f = B(c => benFechar(c, 'OB-0110', 'Igor'));
  const lid = (f.lotes || [])[0]; const r = B(c => benResultado(c, lid, 'Conforme', '', 'Igor')); const l = B(c => benDecidir(c, lid, 'Liberar', {}, 'Igor'));
  const L = G().producao.lotes[lid] || {}; const mv = G().producao.movs.filter(m => m.lote === lid && (m.tipo === 'resultado' || m.tipo === 'liberação'));
  ok('REV11c Igor (produção e qualidade) registra o resultado e libera o lote que ele produziu: vale, com revisão posterior no aviso, nos movimentos e na liberação',
    !f.erro && !r.erro && !l.erro && /revisão posterior pendente/.test(r.msg || '') && /revisão posterior pendente/.test(l.msg || '') && mv.length === 2 && mv.every(m => /revisão posterior pendente/.test(m.obs || ''))
    && /revisão posterior pendente/.test((L.lib || {}).rev || ''), [f.erro, r.erro, l.erro, mv.map(m => m.obs)]);
  ini(); B(c => benConcluir(c, 'OB-0110', 'Igor')); B(c => benConferir(c, 'OB-0110', 'Paula')); M(c => cenDevolver(c, 'REQ-030', BENC.cx.item, 60, true, 'Rui')); const f2 = B(c => benFechar(c, 'OB-0110', 'Igor'));
  const l2 = (f2.lotes || [])[0]; const r2 = B(c => benResultado(c, l2, 'Conforme', '', 'Marta'));
  ok('REV11d referência: Marta (só qualidade) registra o resultado do lote do Igor, sem revisão posterior', !r2.erro && !/revisão posterior/.test(r2.msg || ''), r2.erro || r2.msg); });

console.log('\nTOTAL · falhas ' + nfail);
