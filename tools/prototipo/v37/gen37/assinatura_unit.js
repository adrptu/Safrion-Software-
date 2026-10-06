// PLAT-01 · unitário sem navegador das regras da assinatura (assinatura.js). Executor: assinatura_unit_test.py, que roda este arquivo
// duas vezes: (A) com cenario.js + talgeo.js + talmapa.js na página (como CF-05/BO-02/Mapa) e (B) sem cenario.js (como CD-01, CMP, PA).
// EXP vem do executor: expectativas calculadas em Python com Decimal a partir das mesmas linhas do cadastro (vale também no Mac).
const R = []; function ok(n, c, info) { R.push(!!c); print((c ? 'OK   ' : 'FALHA') + ' ' + n + (c ? '' : ' · ' + JSON.stringify(info === undefined ? '' : info).slice(0, 600))); }
const T = (f) => { try { f(); return ''; } catch (e) { return String(e.message || e); } };
const CHAVE = (p) => p + '-' + (++T.n);
T.n = 0;
if (typeof cenGet === 'function') {
  // ================= (A) página com cenario.js =================
  const A0 = () => assinLer(); const M0 = () => assinMedir(ASSIN_CAD0, assinCadSalvo());
  const mud = (fn) => cenMudar(null, fn);
  const dep = (c) => mud(k => assinAvancar(k, c, { ha: M0().ha, n: M0().n }));
  cenReset(); localStorage.clear();
  // A1 · medição
  const m = M0();
  ok('A1a medida = soma decimal da área cultivável dos talhões ativos (base): ' + EXP.med + ' ha em ' + EXP.n + ' talhões', m.ha === Number(EXP.med) && m.n === EXP.n, [m.ha, m.n]);
  const flo = ASSIN_CAD0.tal.reduce((s, t) => s + Number(t.v.decl), 0);
  ok('A1b soma em ponto flutuante seria ' + flo + ' (por isso centésimos inteiros); a medida é exata', m.cent === Math.round(Number(EXP.med) * 100) && String(m.ha) === String(Number(EXP.med)), [flo, m.ha]);
  // mesma regra do tmBase (talmapa.js) sobre o mesmo dado salvo: inativar T3, inativar a Boa Vista e o B1, criar talhão novo de 50 ha pelo tmSalvar
  const anel = [[-47.2, -34.6], [-47.19, -34.6], [-47.19, -34.594], [-47.2, -34.594], [-47.2, -34.6]];
  const salvo0 = { faz: M.cad0.faz.map(f => ({ id: f.id, v: Object.assign({}, f.v, f.id === 'BV' ? { sit: 'Inativa' } : {}) })),
    tal: M.cad0.tal.map(t => ({ id: t.id, v: Object.assign({}, t.v, t.id === 'T3' || t.id === 'B1' ? { sit: 'Inativo' } : {}) })) };
  localStorage.setItem('talhao-os-cd01-v1', JSON.stringify(salvo0));
  const novo = tmSalvar({ alvo: 'novo', nome: 'T9', faz: 'Santa Rita', sis: 'Sequeiro', decl: 50, motivo: 'Documento desatualizado', ring: anel, origem: 'Desenho no mapa' });
  const tb = tmBase(); const inF = {}; tb.faz.forEach(f => { if (f.v.sit === 'Inativa') inF[f.v.nome] = 1; });
  const tbCent = tb.tal.filter(t => t.v.sit !== 'Inativo' && !inF[t.v.faz]).reduce((s, t) => s + Math.round(Number(t.v.decl) * 100), 0);
  const m2 = M0();
  ok('A1c mesma regra de mescla do tmBase (salvo primeiro, base nos ids que faltam): inativo, fazenda inativa e talhão novo do Mapa (tmSalvar ' + novo.id + ')',
    m2.cent === tbCent && m2.cent === Math.round((Number(EXP.med) - 96 - 120 + 50) * 100), [m2.cent, tbCent]);
  ok('A1d situação por linha: T3 "Inativo · fora", B1 "Inativo · fora"; o novo conta', (m2.linhas.find(l => l.id === 'T3') || {}).sit === 'Inativo · fora' && (m2.linhas.find(l => l.id === novo.id) || {}).conta === true, m2.linhas.filter(l => !l.conta));
  localStorage.setItem('talhao-os-cd01-v1', JSON.stringify({ faz: salvo0.faz.map(f => ({ id: f.id, v: Object.assign({}, f.v, { sit: 'Ativa' }) })), tal: salvo0.tal.map(t => ({ id: t.id, v: Object.assign({}, t.v, { sit: 'Ativo' }) })) }));
  ok('A1e fazenda inativa tira os talhões dela mesmo com o talhão Ativo', (() => { const s = JSON.parse(localStorage.getItem('talhao-os-cd01-v1')); s.faz.find(f => f.id === 'BV').v.sit = 'Inativa'; localStorage.setItem('talhao-os-cd01-v1', JSON.stringify(s)); const x = M0(); return x.cent === Math.round((Number(EXP.med) - 120) * 100) && x.linhas.find(l => l.id === 'B1').sit === 'Fazenda inativa · fora'; })());
  localStorage.removeItem('talhao-os-cd01-v1');
  // A2 · mensalidade
  const V = (p, med, con, cr) => assinMensalidade(p, med, con, cr).valor;
  const tab = [['comp', EXP.med, EXP.v2, EXP.comp], ['ess', EXP.med, EXP.v2, EXP.ess], ['comp', EXP.med50, EXP.v2, EXP.comp50], ['comp', EXP.med50, EXP.v2 + 100, EXP.amp],
    ['ess', 149.5, null, 224.25], ['comp', 20, null, 299], ['ess', 20, null, 199], ['comp', 333, 320, 640], ['comp', 35, 60, 299], ['comp', 100, null, 299],
    ['comp', 500, null, 1000], ['ess', 500, null, 750], ['comp', 1000, null, 2000], ['ess', 1000, null, 1500], ['comp', 5000, null, 10000], ['ess', 5000, null, 7500]];
  const tf = tab.filter(x => V(x[0], x[1], x[2]) !== Number(x[3]));
  ok('A2a assinMensalidade: ' + tab.length + ' casos (inclui ' + EXP.comp + ', ' + EXP.ess + ', 224,25 e a simulação do BO-01)', !tf.length, tf.map(x => [x, V(x[0], x[1], x[2])]));
  ok('A2b ponto flutuante daria 2570.23*1.5 = ' + (2570.23 * 1.5) + '; a regra decimal dá 3855.35', 2570.23 * 1.5 !== 3855.35 && V('ess', 2570.23, null) === 3855.35);
  ok('A2c mínimo é o maior, não se soma: Completo 100 ha = R$ 299,00 (não R$ 499,00); Essencial 149,5 ha = R$ 224,25 (passou do mínimo)', V('comp', 100, null) === 299 && V('ess', 149.5, null) === 224.25);
  ok('A2d crédito nunca deixa o valor negativo e sai em centavos', V('comp', 2570.23, 2600, 100) === Math.round(Number(EXP.comp) * 100 - 10000) / 100 && V('comp', 20, null, 1000) === 0);
  const fs = []; Object.values(ASSIN0.orgs).forEach(o => o.faturas.forEach(f => { const C = f.copia; const x = assinMensalidade(C.plano, C.medida, C.contratada, C.credito); if (x.valor !== f.valor || x.cobrada !== C.cobrada) fs.push([f.id, f.valor, x]); }));
  ok('A2e cada fatura do seed confere com assinMensalidade dos seus dados', !fs.length, fs);
  // A7 · estados por data simulada
  let A = A0(); let sr = A.orgs[A.demo];
  ok('A7a 23/09: Ativa, sem fatura aberta, set/2026 em medição com ' + EXP.comp, assinEstado(sr, A.hoje).t === 'Ativa' && !assinAberta(sr) && assinPrevia(sr, A.hoje, M0().ha, M0().n).valor === Number(EXP.comp));
  ok('A7b primária 23/09: Alterar plano ou área', assinPrimaria(sr, A.hoje, M0().ha) === 'alterar');
  let r = dep('2026-10-01'); A = A0(); sr = A.orgs[A.demo]; let fset = sr.faturas.find(f => f.comp === '2026-09');
  ok('A7c 01/10: set/2026 fecha com ' + EXP.med + ' ha → ' + EXP.comp + ', A vencer, vence 01/10; assinatura Ativa; primária Pagar fatura',
    fset && fset.valor === Number(EXP.comp) && fset.copia.medida === Number(EXP.med) && fset.copia.ntal === EXP.n && assinFatEstado(fset, A.hoje) === 'A vencer' && assinEstado(sr, A.hoje).t === 'Ativa' && assinPrimaria(sr, A.hoje, M0().ha) === 'pagar', [r, fset]);
  ok('A7d data só avança', /só avança/.test(dep('2026-09-23').erro || ''));
  dep('2026-10-06'); A = A0(); sr = A.orgs[A.demo]; let e = assinEstado(sr, A.hoje);
  ok('A7e 06/10: Em atraso há 5 dias; nada restrito', e.t === 'Em atraso' && e.dias === 5 && assinTrava('ampliar_area') === '', e);
  const v6 = {}; assinAvisoVals(null, v6);
  ok('A11 faixa 06/10: amarela, "vencida há 5 dias (data simulada da cobrança: 06/10)"', v6.assin_fx === true && /vencida há 5 dias \(data simulada da cobrança: 06\/10\)/.test(v6.assin_fx_t) && /FFF3D6/.test(v6.assin_fx_st), v6);
  dep('2026-10-16'); A = A0(); sr = A.orgs[A.demo]; e = assinEstado(sr, A.hoje);
  ok('A7f 16/10: Inadimplente há 15 dias; trava de ampliar área com motivo e caminho', e.t === 'Inadimplente' && e.dias === 15 && /Configurações › Assinatura e cobrança/.test(assinTrava('ampliar_area')) && assinTrava('liberar_os') === '', [e, assinTrava('ampliar_area')]);
  const v16 = {}; assinAvisoVals(null, v16);
  ok('A11b faixa 16/10: vermelha, cita o que está suspenso e que nada foi apagado', v16.assin_fx && /FDE8E6/.test(v16.assin_fx_st) && /suspenso/.test(v16.assin_fx_t) && /nada foi apagado/.test(v16.assin_fx_t), v16);
  // A3 · fatura fechada não muda com o cadastro
  localStorage.setItem('talhao-os-cd01-v1', JSON.stringify({ faz: M.cad0.faz, tal: M.cad0.tal.concat([{ id: 'TN01', v: { t: 'T9', faz: 'Santa Rita', decl: 50, sit: 'Ativo' } }]).map(t => t.id === 'T3' ? { id: t.id, v: Object.assign({}, t.v, { decl: 90 }) } : t) }));
  A = A0(); sr = A.orgs[A.demo]; fset = sr.faturas.find(f => f.comp === '2026-09');
  ok('A3 fatura fechada não muda depois de criar e editar talhão (cópia da medição)', fset.valor === Number(EXP.comp) && fset.copia.medida === Number(EXP.med) && M0().ha === Number(EXP.med) + 50 - 6, [fset.copia, M0().ha]);
  localStorage.removeItem('talhao-os-cd01-v1');
  // A6 · pagar: mesma chave → mesmo recibo; outra chave → não paga de novo
  const ch = CHAVE('pag'); r = mud(k => assinPagar(k, fset.id, 'Pix', ch)); const r2 = mud(k => assinPagar(k, fset.id, 'Pix', ch)); A = A0(); sr = A.orgs[A.demo]; fset = sr.faturas.find(f => f.comp === '2026-09');
  ok('A6a mesma chave de pagamento: um efeito, mesmo recibo', r.recibo && r2.repetido && r2.recibo.id === r.recibo.id && fset.eventos.filter(x => /^Paga/.test(x.t)).length === 1, [r, r2]);
  const r3 = mud(k => assinPagar(k, fset.id, 'Boleto', CHAVE('pag')));
  ok('A6b fatura paga não paga de novo com outra chave', /já está paga/.test(r3.erro || ''), r3);
  ok('A7g pagar volta a Ativa e tira a trava', assinEstado(sr, A.hoje).t === 'Ativa' && assinTrava('ampliar_area') === '');
  ok('A6c forma fora da lista é recusada (nenhum campo de cartão)', /forma de pagamento/.test(T(() => { const c = cenClone(cenGet()); c.assin.orgs.sr.faturas.push({ id: 'z', st: 'aberta', comp: '2026-10', eventos: [] }); assinPagar(c, 'z', 'Cartão 1234 5678', 'k2'); })));
  // A4/A5 · mudança agendada (de volta a 23/09)
  cenReset(); A = A0(); sr = A.orgs[A.demo];
  const k1 = CHAVE('ace'); r = mud(k => assinMudar(k, 'ess', EXP.v2, M0().ha, k1)); A = A0(); sr = A.orgs[A.demo];
  ok('A4a aceite agenda o Essencial para 01/10 (contrato v3); set fecha no Completo', /v3 · Essencial/.test(r.msg) && assinAgendado(sr, A.hoje).desde === '2026-10-01' && assinContrato(sr, '2026-09-30').plano === 'comp', r);
  ok('A6d mesma chave de aceite: um contrato só', mud(k => assinMudar(k, 'ess', EXP.v2, M0().ha, k1)).repetido && A0().orgs.sr.contratos.length === 3);
  ok('A4b prévia de set segue ' + EXP.comp + '; a de out (Essencial) dá ' + EXP.ess, assinPrevia(sr, A.hoje, M0().ha, M0().n).valor === Number(EXP.comp) && assinPrevia(sr, '2026-10-02', M0().ha, M0().n).valor === Number(EXP.ess));
  r = mud(k => assinDesfazer(k)); A = A0(); sr = A.orgs[A.demo];
  ok('A4c desfazer antes de 01/10 volta ao contrato v2', !assinAgendado(sr, A.hoje) && sr.contratos.length === 2 && /segue Completo/.test(r.msg), r);
  mud(k => assinMudar(k, 'ess', EXP.v2, M0().ha, CHAVE('ace'))); dep('2026-10-01'); A = A0(); sr = A.orgs[A.demo]; fset = sr.faturas.find(f => f.comp === '2026-09');
  ok('A4d em 01/10 set/2026 fecha no Completo (' + EXP.comp + ') e out/2026 já está no Essencial', fset.copia.plano === 'comp' && fset.valor === Number(EXP.comp) && assinContrato(sr, A.hoje).plano === 'ess' && assinPrevia(sr, A.hoje, M0().ha, M0().n).valor === Number(EXP.ess));
  cenReset();
  const ab = mud(k => assinMudar(k, 'comp', 100, M0().ha, CHAVE('ace'))), ac = mud(k => assinMudar(k, 'comp', 9000, M0().ha, CHAVE('ace')));
  ok('A5 área abaixo da medida e acima de 5.000 ha recusadas com o motivo, sem gravar', /abaixo da medida/.test(ab.erro || '') && /Acima de 5\.000 ha: proposta empresarial/.test(ac.erro || '') && A0().orgs.sr.contratos.length === 2, [ab, ac]);
  ok('A5b nada muda: mesmo plano e área é recusado', /Nada muda/.test(mud(k => assinMudar(k, 'comp', EXP.v2, M0().ha, CHAVE('ace'))).erro || ''));
  // R14 · talhão novo de 50 ha: aviso de área acima do contratado e primária Ampliar (2.700 ha → valor da tabela)
  localStorage.setItem('talhao-os-cd01-v1', JSON.stringify({ faz: M.cad0.faz, tal: M.cad0.tal.concat([{ id: 'TN01', v: { t: 'T9', faz: 'Santa Rita', decl: 50, sit: 'Ativo' } }]) }));
  A = A0(); sr = A.orgs[A.demo];
  ok('A10a 50 ha a mais: medida ' + EXP.med50 + ', cobrada ' + EXP.v2 + ' (sem cobrança-surpresa) → ' + EXP.comp50 + '; primária Ampliar área contratada',
    M0().ha === Number(EXP.med50) && assinPrevia(sr, A.hoje, M0().ha, M0().n).valor === Number(EXP.comp50) && assinPrimaria(sr, A.hoje, M0().ha) === 'ampliar');
  let cart = assinCarteira(A, ASSIN_CAD0, assinCadSalvo());
  ok('A10b BO-02 mede ao vivo: Santa Rita ' + EXP.med50 + ' ha e mensalidades vigentes ' + EXP.vig50, cart.linhas.find(l => l.org.id === 'sr').med === Number(EXP.med50) && cart.vig === Number(EXP.vig50), [cart.vig]);
  localStorage.removeItem('talhao-os-cd01-v1');
  // A12 · carteira e conciliação
  cenReset(); A = A0(); cart = assinCarteira(A, ASSIN_CAD0, null);
  ok('A12a BO-02 em 23/09: vigentes ' + EXP.vig + ' · Ativa 3 · Em avaliação 1 · Inadimplente 1 · Cancelada 1 · 2 faturas abertas R$ 939,00 · cobrada ' + EXP.cob + ' · medida ' + EXP.medT,
    cart.vig === Number(EXP.vig) && cart.n['Ativa'] === 3 && cart.n['Em avaliação'] === 1 && cart.n['Inadimplente'] === 1 && cart.n['Cancelada'] === 1 && cart.abertas === 2 && cart.abertasV === 939 && cart.cobrada === Number(EXP.cob) && cart.medida === Number(EXP.medT), cart);
  const kc = CHAVE('con'); r = mud(k => assinConciliar(k, kc)); const rr = mud(k => assinConciliar(k, kc)); const rn = mud(k => assinConciliar(k, CHAVE('con')));
  A = A0(); cart = assinCarteira(A, ASSIN_CAD0, null); const fbv = A.orgs.bv.faturas[0], fau = A.orgs.aurora.faturas[0];
  ok('A12b conciliar: Bela Vista paga (evt_1JKT5), recusa da Aurora registrada, Aurora segue Vencida; 1 fatura aberta R$ 299,00',
    fbv.st === 'paga' && fbv.evt === 'evt_1JKT5' && fau.st === 'aberta' && fau.eventos.some(x => /evt_1JKR9/.test(x.t)) && cart.abertas === 1 && cart.abertasV === 299, [r, cart.abertas]);
  ok('A12c conciliar de novo: mesma chave devolve o recibo; outra chave não acha evento novo; nada duplica',
    rr.repetido && /Nenhum evento novo/.test(rn.msg) && fbv.eventos.filter(x => /^Paga/.test(x.t)).length === 1 && fau.eventos.filter(x => /evt_1JKR9/.test(x.t)).length === 1, [rr, rn]);
  // A17 · contestação congela a régua; resolver com crédito vai para a fatura seguinte
  cenReset(); dep('2026-10-06'); A = A0(); sr = A.orgs[A.demo]; fset = sr.faturas.find(f => f.comp === '2026-09');
  ok('A17a motivo curto recusado', /motivo/.test(mud(k => assinContestar(k, fset.id, 'x', CHAVE('cts'))).erro || ''));
  r = mud(k => assinContestar(k, fset.id, 'Área do T9 contada antes do aceite', CHAVE('cts'))); dep('2026-10-16'); A = A0(); sr = A.orgs[A.demo];
  ok('A17b contestada: em 16/10 a assinatura segue Ativa (régua congelada) e nada é restrito', assinEstado(sr, A.hoje).t === 'Ativa' && assinTrava('ampliar_area') === '' && assinFatEstado(sr.faturas.find(f => f.comp === '2026-09'), A.hoje) === 'Em contestação', r);
  ok('A17c pagar fatura em contestação é recusado', /contestação/.test(mud(k => assinPagar(k, fset.id, 'Pix', CHAVE('pag'))).erro || ''));
  ok('A17d crédito maior que a fatura é recusado', /não pode passar/.test(mud(k => assinResolver(k, 'sr', fset.id, 'creditar', '9.999,00', CHAVE('res'))).erro || ''));
  r = mud(k => assinResolver(k, 'sr', fset.id, 'creditar', '100,00', CHAVE('res'))); A = A0(); sr = A.orgs[A.demo]; fset = sr.faturas.find(f => f.comp === '2026-09');
  const pv = assinPrevia(sr, A.hoje, M0().ha, M0().n);
  ok('A17e resolver com crédito: set volta a A vencer (vence 21/10), valor não reescrito; out/2026 mostra o crédito de R$ 100,00',
    fset.st === 'aberta' && fset.venc === '2026-10-21' && fset.valor === Number(EXP.comp) && pv.copia.credito === 100 && pv.valor === Math.round(Number(EXP.comp) * 100 - 10000) / 100, [fset, pv.valor]);
  // CSV
  const csv = assinCsv(sr, fset);
  ok('A18 CSV da fatura traz os números da cópia (medida, cobrada, valor) e diz que a cobrança é simulada', csv.indexOf(assinNf(EXP.med, 2, 2)) >= 0 && csv.indexOf(assinNf(EXP.comp, 2, 2)) >= 0 && /simulada/.test(csv), csv.slice(0, 300));
  cenReset();
} else {
  // ================= (B) página sem cenario.js (CD-01, CMP, PA…) =================
  localStorage.clear();
  ok('B1 sem cenario.js e sem nada salvo: assinLer() devolve o seed, sem ReferenceError', assinLer() === ASSIN0 && typeof cenQtd === 'undefined');
  const st = assinClone(ASSIN0); st.hoje = '2026-10-16';
  st.orgs.sr.faturas.push({ id: 'sr-2026-09', comp: '2026-09', st: 'aberta', valor: 5140.46, emitida: '2026-10-01', venc: '2026-10-01', eventos: [], copia: {} });
  localStorage.setItem(ASSIN_KEY, JSON.stringify({ v: ASSIN_CENV, assin: st }));
  ok('B2 cenário salvo com a versão vigente: lê a assinatura (16/10, inadimplente) e trava ampliar a área', assinLer().hoje === '2026-10-16' && /suspenso/.test(assinTrava('ampliar_area')), assinTrava('ampliar_area'));
  const v = {}; assinAvisoVals(null, v);
  ok('B3 faixa vermelha também na tela sem cenario.js', v.assin_fx === true && /FDE8E6/.test(v.assin_fx_st));
  localStorage.setItem(ASSIN_KEY, JSON.stringify({ v: ASSIN_CENV - 1, assin: st }));
  ok('B4 cenário salvo com outra versão: vale o seed (mesma regra do cenGet)', assinLer().hoje === ASSIN0.hoje && assinTrava('ampliar_area') === '');
  localStorage.setItem(ASSIN_KEY, '{quebrado');
  ok('B5 cenário ilegível: vale o seed, sem erro', assinLer() === ASSIN0);
}
print('TOTAL ' + R.length + ' · falhas ' + R.filter(x => !x).length);
