// PLAT-01 · unitário sem navegador das regras da assinatura (assinatura.js). Executor: assinatura_unit_test.py, que roda este arquivo
// duas vezes: (A) com cenario.js + talgeo.js + talmapa.js na página (como CF-05/BO-02/Mapa) e (B) sem cenario.js (como CD-01, CMP, PA).
// EXP vem do executor: expectativas calculadas em Python com Decimal a partir das mesmas linhas do cadastro (vale também no Mac).
const R = []; function ok(n, c, info) { R.push(!!c); print((c ? 'OK   ' : 'FALHA') + ' ' + n + (c ? '' : ' · ' + JSON.stringify(info === undefined ? '' : info).slice(0, 600))); }
const T = (f) => { try { f(); return ''; } catch (e) { return String(e.message || e); } };
const CHAVE = (p) => p + '-' + (++T.n);
T.n = 0;
const ANA = 'Ana · Gestora', ADM = 'Admin plataforma';   // quem age (revisão PLAT, achado 4)
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
  ok('A11 faixa 06/10: amarela, "vencida há 5 dias (data simulada da cobrança: 06/10)"; no celular só "Fatura de set/2026 vencida há 5 dias"', v6.assin_fx === true && /vencida há 5 dias \(data simulada da cobrança: 06\/10\) · nada está restrito/.test(v6.assin_fx_t) && v6.assin_fx_m === 'Fatura de set/2026 vencida há 5 dias' && /FFF3D6/.test(v6.assin_fx_st), v6);
  dep('2026-10-16'); A = A0(); sr = A.orgs[A.demo]; e = assinEstado(sr, A.hoje);
  ok('A7f 16/10: Inadimplente há 15 dias; trava de ampliar área com motivo e caminho', e.t === 'Inadimplente' && e.dias === 15 && /Configurações › Assinatura e cobrança/.test(assinTrava('ampliar_area')) && assinTrava('liberar_os') === '', [e, assinTrava('ampliar_area')]);
  const v16 = {}; assinAvisoVals(null, v16);
  ok('A11b faixa 16/10: vermelha, cita o que está suspenso e que nada foi apagado; no celular "… vencida há 15 dias · talhão novo suspenso"', v16.assin_fx && /FDE8E6/.test(v16.assin_fx_st) && /suspenso/.test(v16.assin_fx_t) && /nada foi apagado/.test(v16.assin_fx_t) && v16.assin_fx_m === 'Fatura de set/2026 vencida há 15 dias · talhão novo suspenso', v16);
  // A3 · fatura fechada não muda com o cadastro
  localStorage.setItem('talhao-os-cd01-v1', JSON.stringify({ faz: M.cad0.faz, tal: M.cad0.tal.concat([{ id: 'TN01', v: { t: 'T9', faz: 'Santa Rita', decl: 50, sit: 'Ativo' } }]).map(t => t.id === 'T3' ? { id: t.id, v: Object.assign({}, t.v, { decl: 90 }) } : t) }));
  A = A0(); sr = A.orgs[A.demo]; fset = sr.faturas.find(f => f.comp === '2026-09');
  ok('A3 fatura fechada não muda depois de criar e editar talhão (cópia da medição)', fset.valor === Number(EXP.comp) && fset.copia.medida === Number(EXP.med) && M0().ha === Number(EXP.med) + 50 - 6, [fset.copia, M0().ha]);
  localStorage.removeItem('talhao-os-cd01-v1');
  // A6 · pagar: mesma chave → mesmo recibo; outra chave → não paga de novo
  const ch = CHAVE('pag'); r = mud(k => assinPagar(k, fset.id, 'Pix', ch, ANA)); const r2 = mud(k => assinPagar(k, fset.id, 'Pix', ch, ANA)); A = A0(); sr = A.orgs[A.demo]; fset = sr.faturas.find(f => f.comp === '2026-09');
  ok('A6a mesma chave de pagamento: um efeito, mesmo recibo', r.recibo && r2.repetido && r2.recibo.id === r.recibo.id && fset.eventos.filter(x => /^Paga/.test(x.t)).length === 1, [r, r2]);
  const r3 = mud(k => assinPagar(k, fset.id, 'Boleto', CHAVE('pag'), ANA));
  ok('A6b fatura paga não paga de novo com outra chave', /já está paga/.test(r3.erro || ''), r3);
  ok('A7g pagar volta a Ativa e tira a trava', assinEstado(sr, A.hoje).t === 'Ativa' && assinTrava('ampliar_area') === '');
  ok('A6c forma fora da lista é recusada (nenhum campo de cartão)', /forma de pagamento/.test(T(() => { const c = cenClone(cenGet()); c.assin.orgs.sr.faturas.push({ id: 'z', st: 'aberta', comp: '2026-10', eventos: [] }); assinPagar(c, 'z', 'Cartão 1234 5678', 'k2', ANA); })));
  // A4/A5 · mudança agendada (de volta a 23/09)
  cenReset(); A = A0(); sr = A.orgs[A.demo];
  const k1 = CHAVE('ace'); r = mud(k => assinMudar(k, 'ess', EXP.v2, M0().ha, k1, ANA)); A = A0(); sr = A.orgs[A.demo];
  ok('A4a aceite agenda o Essencial para 01/10 (contrato v3); set fecha no Completo', /v3 · Essencial/.test(r.msg) && assinAgendado(sr, A.hoje).desde === '2026-10-01' && assinContrato(sr, '2026-09-30').plano === 'comp', r);
  ok('A6d mesma chave de aceite: um contrato só', mud(k => assinMudar(k, 'ess', EXP.v2, M0().ha, k1, ANA)).repetido && A0().orgs.sr.contratos.length === 3);
  ok('A4b prévia de set segue ' + EXP.comp + '; a de out (Essencial) dá ' + EXP.ess, assinPrevia(sr, A.hoje, M0().ha, M0().n).valor === Number(EXP.comp) && assinPrevia(sr, '2026-10-02', M0().ha, M0().n).valor === Number(EXP.ess));
  r = mud(k => assinDesfazer(k, CHAVE('des'), ANA)); A = A0(); sr = A.orgs[A.demo];
  ok('A4c desfazer antes de 01/10 volta ao contrato v2', !assinAgendado(sr, A.hoje) && sr.contratos.length === 2 && /segue Completo/.test(r.msg), r);
  mud(k => assinMudar(k, 'ess', EXP.v2, M0().ha, CHAVE('ace'), ANA)); dep('2026-10-01'); A = A0(); sr = A.orgs[A.demo]; fset = sr.faturas.find(f => f.comp === '2026-09');
  ok('A4d em 01/10 set/2026 fecha no Completo (' + EXP.comp + ') e out/2026 já está no Essencial', fset.copia.plano === 'comp' && fset.valor === Number(EXP.comp) && assinContrato(sr, A.hoje).plano === 'ess' && assinPrevia(sr, A.hoje, M0().ha, M0().n).valor === Number(EXP.ess));
  cenReset();
  const ab = mud(k => assinMudar(k, 'comp', 100, M0().ha, CHAVE('ace'), ANA)), ac = mud(k => assinMudar(k, 'comp', 9000, M0().ha, CHAVE('ace'), ANA));
  ok('A5 área abaixo da medida e acima de 5.000 ha recusadas com o motivo, sem gravar', /abaixo da medida/.test(ab.erro || '') && /Acima de 5\.000 ha: proposta empresarial/.test(ac.erro || '') && A0().orgs.sr.contratos.length === 2, [ab, ac]);
  ok('A5b nada muda: mesmo plano e área é recusado', /Nada muda/.test(mud(k => assinMudar(k, 'comp', EXP.v2, M0().ha, CHAVE('ace'), ANA)).erro || ''));
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
  const kc = CHAVE('con'); r = mud(k => assinConciliar(k, kc, ADM)); const rr = mud(k => assinConciliar(k, kc, ADM)); const rn = mud(k => assinConciliar(k, CHAVE('con'), ADM));
  A = A0(); cart = assinCarteira(A, ASSIN_CAD0, null); const fbv = A.orgs.bv.faturas[0], fau = A.orgs.aurora.faturas[0];
  ok('A12b conciliar: Bela Vista paga (evt_1JKT5), recusa da Aurora registrada, Aurora segue Vencida; 1 fatura aberta R$ 299,00',
    fbv.st === 'paga' && fbv.evt === 'evt_1JKT5' && fau.st === 'aberta' && fau.eventos.some(x => /evt_1JKR9/.test(x.t)) && cart.abertas === 1 && cart.abertasV === 299, [r, cart.abertas]);
  ok('A12c conciliar de novo: mesma chave devolve o recibo; outra chave não acha evento novo; nada duplica',
    rr.repetido && /Nenhum evento novo/.test(rn.msg) && fbv.eventos.filter(x => /^Paga/.test(x.t)).length === 1 && fau.eventos.filter(x => /evt_1JKR9/.test(x.t)).length === 1, [rr, rn]);
  // A17 · contestação congela a régua; resolver com crédito vai para a fatura seguinte
  cenReset(); dep('2026-10-06'); A = A0(); sr = A.orgs[A.demo]; fset = sr.faturas.find(f => f.comp === '2026-09');
  ok('A17a motivo curto recusado', /motivo/.test(mud(k => assinContestar(k, fset.id, 'x', CHAVE('cts'), ANA)).erro || ''));
  r = mud(k => assinContestar(k, fset.id, 'Área do T9 contada antes do aceite', CHAVE('cts'), ANA)); dep('2026-10-16'); A = A0(); sr = A.orgs[A.demo];
  ok('A17b contestada: em 16/10 a assinatura segue Ativa (régua congelada) e nada é restrito', assinEstado(sr, A.hoje).t === 'Ativa' && assinTrava('ampliar_area') === '' && assinFatEstado(sr.faturas.find(f => f.comp === '2026-09'), A.hoje) === 'Em contestação', r);
  ok('A17c pagar fatura em contestação é recusado', /contestação/.test(mud(k => assinPagar(k, fset.id, 'Pix', CHAVE('pag'), ANA)).erro || ''));
  ok('A17d crédito maior que a fatura é recusado', /não pode passar/.test(mud(k => assinResolver(k, 'sr', fset.id, 'creditar', '9.999,00', CHAVE('res'), ADM)).erro || ''));
  r = mud(k => assinResolver(k, 'sr', fset.id, 'creditar', '100,00', CHAVE('res'), ADM)); A = A0(); sr = A.orgs[A.demo]; fset = sr.faturas.find(f => f.comp === '2026-09');
  const pv = assinPrevia(sr, A.hoje, M0().ha, M0().n);
  ok('A17e resolver com crédito: set volta a A vencer (vence 21/10), valor não reescrito; out/2026 mostra o crédito de R$ 100,00',
    fset.st === 'aberta' && fset.venc === '2026-10-21' && fset.valor === Number(EXP.comp) && pv.copia.credito === 100 && pv.valor === Math.round(Number(EXP.comp) * 100 - 10000) / 100, [fset, pv.valor]);
  // CSV
  const csv = assinCsv(sr, fset);
  ok('A18 CSV da fatura traz os números da cópia (medida, cobrada, valor) e diz que a cobrança é simulada', csv.indexOf(assinNf(EXP.med, 2, 2)) >= 0 && csv.indexOf(assinNf(EXP.comp, 2, 2)) >= 0 && /simulada/.test(csv), csv.slice(0, 300));
  // ================= revisão PLAT (06/10): um caso por achado e por mutante que sobrevivia =================
  // achado 1 · uma contestação por fatura; teto do crédito pelo total já creditado; quem contestou e quem resolveu
  cenReset(); localStorage.clear(); dep('2026-10-01'); A = A0(); fset = A.orgs.sr.faturas.find(f => f.comp === '2026-09');
  mud(k => assinContestar(k, fset.id, 'Lagoa contada antes do aceite', CHAVE('cts'), ANA));
  mud(k => assinResolver(k, 'sr', fset.id, 'creditar', assinNf(EXP.comp, 2, 2), CHAVE('res'), ADM));
  const re = mud(k => assinContestar(k, fset.id, 'contestação repetida', CHAVE('cts'), ANA));
  A = A0(); sr = A.orgs.sr; fset = sr.faturas.find(f => f.comp === '2026-09');
  ok('R1a fatura resolvida não é contestada de novo: a recusa cita o RES- que resolveu; um crédito só; contestou Ana · Gestora, resolveu Admin plataforma',
    /já foi contestada e resolvida \(RES-0001 em 01\/10\): uma contestação por fatura/.test(re.erro || '') && sr.creditos.filter(x => x.origem === fset.id).length === 1
    && assinCreditoDe(sr, '2026-10') === Number(EXP.comp) && !assinPodeContestar(fset) && fset.contest.por === ANA && fset.contest.res_por === ADM, [re, sr.creditos, fset.contest]);
  const cx = cenClone(cenGet()); const fx = cx.assin.orgs.sr.faturas.find(f => f.comp === '2026-09'); fx.st = 'contestada'; fx.contest = { motivo: 'teste', d: '2026-10-01', recibo: 'CTS-9' };
  cx.assin.orgs.sr.creditos = [{ comp: '2026-10', valor: 5000, origem: fx.id }];
  const tc = T(() => assinResolver(cx, 'sr', fx.id, 'creditar', '200,00', 'k-tc', ADM));
  ok('R1b teto do crédito pelo total já creditado da fatura: R$ 5.000,00 + R$ 200,00 > ' + EXP.comp + ' é recusado', /não pode passar do valor da fatura .*já creditado R\$ 5\.000,00/.test(tc), tc);
  cenReset(); dep('2026-10-06'); A = A0(); fset = A.orgs.sr.faturas.find(f => f.comp === '2026-09');
  mud(k => assinContestar(k, fset.id, 'primeira contestação', CHAVE('cts'), ANA)); mud(k => assinResolver(k, 'sr', fset.id, 'manter', '', CHAVE('res'), ADM));
  const re2 = mud(k => assinContestar(k, fset.id, 'segunda contestação', CHAVE('cts'), ANA)); dep('2026-10-16'); A = A0(); e = assinEstado(A.orgs.sr, A.hoje);
  ok('R1c manter o valor e contestar de novo: recusado; em 16/10 a régua corre do novo vencimento (11/10): Em atraso há 5 dias', /uma contestação por fatura/.test(re2.erro || '') && e.t === 'Em atraso' && e.dias === 5, [re2, e]);
  // achado 2 · crédito maior que a fatura do período: aplica o que cabe e lança o saldo no mês seguinte
  cenReset(); localStorage.clear(); mud(k => assinMudar(k, 'ess', EXP.v2, M0().ha, CHAVE('ace'), ANA)); dep('2026-10-01');
  A = A0(); fset = A.orgs.sr.faturas.find(f => f.comp === '2026-09');
  mud(k => assinContestar(k, fset.id, 'Lagoa contada antes do aceite', CHAVE('cts'), ANA)); mud(k => assinResolver(k, 'sr', fset.id, 'creditar', assinNf(EXP.comp, 2, 2), CHAVE('res'), ADM));
  A = A0(); sr = A.orgs.sr; const pvs = assinPrevia(sr, A.hoje, M0().ha, M0().n);
  const sobra = (Math.round(Number(EXP.comp) * 100) - Math.round(Number(EXP.ess) * 100)) / 100;
  ok('R2a crédito de ' + EXP.comp + ' numa prévia de ' + EXP.ess + ': aplica ' + EXP.ess + ', prévia R$ 0,00 e mostra saldo de ' + sobra + ' para nov/2026',
    pvs.valor === 0 && pvs.copia.credito === Number(EXP.ess) && pvs.copia.saldo === sobra && pvs.copia.saldo_comp === '2026-11', pvs.copia);
  dep('2026-11-01'); A = A0(); sr = A.orgs.sr; const fout = sr.faturas.find(f => f.comp === '2026-10');
  ok('R2b out/2026 fecha com o crédito de ' + EXP.ess + ' e lança o saldo de ' + sobra + ' em nov/2026: crédito usado + saldo = crédito dado (nada some)',
    fout.valor === 0 && fout.copia.credito === Number(EXP.ess) && fout.copia.saldo === sobra && assinCreditoDe(sr, '2026-11') === sobra
    && Math.round(fout.copia.credito * 100) + Math.round(assinCreditoDe(sr, '2026-11') * 100) === Math.round(Number(EXP.comp) * 100) && /saldo de R\$ [\d.,]+ para nov\/2026/.test(fout.eventos[0].t), [fout.copia, sr.creditos]);
  ok('R2c fatura de R$ 0,00 nasce quitada pelo crédito: estado Paga, não pede pagamento (a aberta é a de set/2026), não conta atraso', fout.st === 'paga' && assinFatEstado(fout, A.hoje) === 'Paga'
    && assinAberta(sr).comp === '2026-09' && fout.eventos.some(x => /Quitada pelo crédito/.test(x.t)) && assinAtraso(fout, '2026-12-31') === 0, fout);
  const pnov = assinPrevia(sr, A.hoje, M0().ha, M0().n);
  ok('R2d prévia de nov/2026 desconta o saldo: ' + EXP.ess + ' − ' + sobra, pnov.copia.credito === sobra && pnov.valor === (Math.round(Number(EXP.ess) * 100) - Math.round(sobra * 100)) / 100, pnov.copia);
  const csv2 = assinCsv(sr, fout);
  ok('R2e CSV de out/2026 traz o saldo de crédito para nov/2026', /Saldo de crédito para nov\/2026/.test(csv2), csv2.slice(0, 400));
  // achado 3 · medida do período = maior entre a abertura e o fechamento
  cenReset(); localStorage.clear();
  localStorage.setItem('talhao-os-cd01-v1', JSON.stringify({ faz: M.cad0.faz, tal: M.cad0.tal.map(t => t.id === 'B1' ? { id: t.id, v: Object.assign({}, t.v, { sit: 'Inativo' }) } : t) }));
  A = A0(); sr = A.orgs.sr; const m23 = M0(); const pv3 = assinPrevia(sr, A.hoje, m23.ha, m23.n);
  ok('R3a 23/09 com B1 (120 ha) inativo: medida hoje ' + m23.ha + ' ha, mas a prévia de set/2026 usa a abertura (' + EXP.med + ' ha): inativar não reduz o mês em curso',
    m23.cent === Math.round(Number(EXP.med) * 100) - 12000 && pv3.copia.medida === Number(EXP.med) && pv3.copia.piso === true && pv3.valor === Number(EXP.comp), pv3.copia);
  r = dep('2026-10-01'); A = A0(); sr = A.orgs.sr; fset = sr.faturas.find(f => f.comp === '2026-09');
  ok('R3b 01/10: set/2026 fecha com a abertura (' + EXP.med + ' ha → ' + EXP.comp + '); a cópia guarda abertura e fechamento; out/2026 abre com ' + m23.ha + ' ha',
    fset.copia.medida === Number(EXP.med) && fset.valor === Number(EXP.comp) && fset.copia.fech === m23.ha && fset.copia.abertura === Number(EXP.med) && /medida da abertura/.test(r.msg) && sr.aberturas['2026-10'].ha === m23.ha, [r.msg, fset.copia]);
  localStorage.removeItem('talhao-os-cd01-v1');   // reativa o B1 depois do fechamento
  dep('2026-11-01'); A = A0(); const fo3 = A.orgs.sr.faturas.find(f => f.comp === '2026-10');
  ok('R3c B1 reativado em 01/10: out/2026 fecha com ' + EXP.med + ' ha (vale o fechamento; a abertura era ' + m23.ha + ')', fo3.copia.medida === Number(EXP.med) && fo3.copia.abertura === m23.ha && fo3.copia.piso === false, fo3.copia);
  // achado 4 · quem age: recusa sem autor; grava no contrato, no recibo, na fatura e no evento
  cenReset(); localStorage.clear();
  ok('R4a ato sem quem age é recusado sem gravar (aceite e conciliação)', /Quem age não foi identificado/.test(mud(k => assinMudar(k, 'ess', EXP.v2, M0().ha, CHAVE('ace'), '')).erro || '')
    && /Quem age não foi identificado/.test(mud(k => assinConciliar(k, CHAVE('con'))).erro || '') && A0() === ASSIN0);
  mud(k => assinMudar(k, 'ess', EXP.v2, M0().ha, CHAVE('ace'), ANA)); dep('2026-10-01'); mud(k => assinConciliar(k, CHAVE('con'), ADM));
  A = A0(); fset = A.orgs.sr.faturas.find(f => f.comp === '2026-09'); const kpg = CHAVE('pag'); mud(k => assinPagar(k, fset.id, 'Pix', kpg, ANA));
  A = A0(); sr = A.orgs.sr; fset = sr.faturas.find(f => f.comp === '2026-09'); const fbv2 = A.orgs.bv.faturas[0];
  ok('R4b quem age fica no contrato, no recibo, na fatura e no evento: aceite e pagamento por Ana · Gestora, conciliação por Admin plataforma; a fatura copia quem aceitou o contrato',
    assinContrato(sr, A.hoje).por === ANA && A.recibos[kpg].por === ANA && fset.paga_por === ANA && /recibo PAG-0001 · por Ana · Gestora$/.test(fset.eventos.slice(-1)[0].t)
    && fset.copia.aceite_por === ANA && fbv2.paga_por === ADM && /por Admin plataforma$/.test(fbv2.eventos.slice(-1)[0].t), [fset.eventos, fbv2.eventos]);
  // achado 5 · mutantes que sobreviviam (M03/M04 régua 10/11 dias, M05, M06, M07, M20) e a defesa do tmSalvar
  const orgR = { contratos: [{ v: 1, plano: 'comp', ha: 100, desde: '2026-01-01' }], faturas: [{ id: 'x', comp: '2026-09', st: 'aberta', venc: '2026-10-01' }] };
  ok('R5a régua no limite: 10 dias Em atraso; 11 dias Inadimplente', assinEstado(orgR, '2026-10-11').t === 'Em atraso' && assinEstado(orgR, '2026-10-11').dias === 10
    && assinEstado(orgR, '2026-10-12').t === 'Inadimplente' && assinEstado(orgR, '2026-10-12').dias === 11);
  ok('R5b R7 no limite: contratada igual à medida aceita; 5.000 ha aceita; 5.000,01 ha recusada', assinValidaArea(assinNf(2570.23, 2, 2), 2570.23) === '' && assinValidaArea('5.000', 4999) === ''
    && /Acima de 5\.000 ha/.test(assinValidaArea('5.000,01', 4999)));
  const orgP = { contratos: [{ v: 2, plano: 'comp', ha: 2600, desde: '2026-09-01' }, { v: 3, plano: 'comp', ha: 2700, desde: '2026-10-01' }], faturas: [] };
  ok('R5c primária com ampliação agendada que cobre a medida (2.620,23 ≤ 2.700): Alterar plano ou área; sem a agendada, Ampliar', assinPrimaria(orgP, '2026-09-23', 2620.23) === 'alterar'
    && assinPrimaria({ contratos: [orgP.contratos[0]], faturas: [] }, '2026-09-23', 2620.23) === 'ampliar');
  cenReset(); dep('2026-10-01'); A = A0(); fset = A.orgs.sr.faturas.find(f => f.comp === '2026-09'); mud(k => assinPagar(k, fset.id, 'Pix', CHAVE('pag'), ANA));
  ok('R5d fatura paga não é contestada', /Só fatura a vencer ou vencida/.test(mud(k => assinContestar(k, fset.id, 'paga e contestada', CHAVE('cts'), ANA)).erro || ''));
  ok('R5e estado da fatura: pendente = "Pendente" e não conta atraso; contestada = "Em contestação"', assinFatEstado({ st: 'pendente', venc: '2026-09-01' }, '2026-10-16') === 'Pendente'
    && assinAtraso({ st: 'pendente', venc: '2026-09-01' }, '2026-10-16') === 0 && assinFatEstado({ st: 'contestada', venc: '2026-09-01' }, '2026-10-16') === 'Em contestação');
  cenReset(); localStorage.clear(); dep('2026-10-16');
  const tmx = T(() => tmSalvar({ alvo: 'novo', nome: 'T10', faz: 'Santa Rita', sis: 'Sequeiro', decl: 10, motivo: 'Documento desatualizado', ring: anel, origem: 'Desenho no mapa' }));
  ok('R5f defesa do tmSalvar: talhão novo com a assinatura inadimplente é recusado mesmo sem passar pelo botão (nada gravado)', /suspenso até o pagamento/.test(tmx) && !assinCadSalvo(), tmx);
  // achado 6 · voltar ao contrato de hoje com clique duplo; contestar sem chave
  cenReset(); mud(k => assinMudar(k, 'ess', EXP.v2, M0().ha, CHAVE('ace'), ANA)); const kv = CHAVE('ace');
  const v1 = mud(k => assinMudar(k, 'comp', EXP.v2, M0().ha, kv, ANA)), v2b = mud(k => assinMudar(k, 'comp', EXP.v2, M0().ha, kv, ANA));
  ok('R6a voltar ao contrato de hoje pelo aceite, clique duplo: o 1º desfaz (DES-0001), o 2º devolve o mesmo recibo sem erro; o contrato desfeito fica guardado com quem desfez',
    /Mudança desfeita \(DES-0001\)/.test(v1.msg || '') && v2b.repetido && /DES-0001/.test(v2b.msg || '') && !v2b.erro && A0().orgs.sr.desfeitos.length === 1 && A0().orgs.sr.desfeitos[0].desfeito_por === ANA, [v1, v2b]);
  cenReset(); dep('2026-10-01'); A = A0(); fset = A.orgs.sr.faturas.find(f => f.comp === '2026-09');
  const sc = mud(k => assinContestar(k, fset.id, 'sem chave nenhuma', undefined, ANA)), sr2 = mud(k => assinResolver(k, 'sr', fset.id, 'manter', '', undefined, ADM));
  ok('R6b contestar ou resolver sem chave é recusado e não grava recibo "undefined"', /sem chave/.test(sc.erro || '') && /sem chave/.test(sr2.erro || '') && !('undefined' in (A0().recibos || {}))
    && A0().orgs.sr.faturas.find(f => f.comp === '2026-09').st === 'aberta', [sc, sr2]);
  // achado 7 · estado salvo de outra versão do seed
  cenReset(); mud(k => { assinGarante(k); k.assin.orgs.sr.contratos[1].ha = 1234; k.assin.v = 0; return { msg: 'estado de outro build' }; });
  ok('R7a estado salvo com outra versão da assinatura (v=0, contrato v2 de 1.234 ha): vale o seed; a próxima gravação recomeça do seed', A0() === ASSIN0
    && (() => { dep('2026-10-01'); return A0().orgs.sr.contratos[1].ha === EXP.v2 && A0().v === ASSIN0.v; })());
  ok('R7b ASSIN0.v = versão + resumo do seed ("' + ASSIN0.v + '")', /^\d+-[0-9a-f]{8}$/.test(ASSIN0.v));
  // achado 8 · dia do trial pela data simulada (ON-01 e BO-02 leem assinTrial)
  ok('R8 trial da Boa Esperança: 23/09 dia 5 de 30; 16/10 dia 28 de 30', assinTrial(ASSIN0.orgs.boaesp, '2026-09-23').t === 'dia 5 de 30' && assinTrial(ASSIN0.orgs.boaesp, '2026-10-16').t === 'dia 28 de 30');
  // achado 10 · medida acima do teto dos planos
  cenReset(); localStorage.setItem('talhao-os-cd01-v1', JSON.stringify({ faz: M.cad0.faz, tal: M.cad0.tal.concat([{ id: 'TNX', v: { t: 'Grande', faz: 'Santa Rita', decl: 2600, sit: 'Ativo' } }]) }));
  A = A0(); sr = A.orgs.sr; const mg = M0();
  ok('R10a medida acima de 5.000 ha (' + mg.ha + '): primária Pedir proposta empresarial; a sugestão de área fica no teto', mg.ha > 5000 && assinPrimaria(sr, A.hoje, mg.ha) === 'proposta'
    && assinSugere(mg.ha) === 5000 && assinSugere(2620.23) === 2700);
  const kpro = CHAVE('pro'); const p1 = mud(k => assinProposta(k, mg.ha, kpro, ANA)), p2 = mud(k => assinProposta(k, mg.ha, kpro, ANA)), p3 = mud(k => assinProposta(k, mg.ha, CHAVE('pro'), ANA));
  ok('R10b pedido de proposta: registrado uma vez (PRO-0001, por Ana · Gestora); a mesma chave devolve o recibo; outra chave é recusada', /PRO-0001/.test(p1.msg || '') && p2.repetido && /já pedida/.test(p3.erro || '')
    && A0().orgs.sr.proposta.por === ANA, [p1, p2, p3]);
  localStorage.removeItem('talhao-os-cd01-v1'); cenReset();
  ok('R10c abaixo do teto o pedido é recusado (use Alterar plano ou área)', /Até 5\.000 ha/.test(mud(k => assinProposta(k, M0().ha, CHAVE('pro'), ANA)).erro || ''));
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
  const st2 = assinClone(st); st2.v = 'outro-build'; localStorage.setItem(ASSIN_KEY, JSON.stringify({ v: ASSIN_CENV, assin: st2 }));
  ok('B6 assinatura salva com outra versão do seed (outro build, outro cadastro): vale o seed', assinLer() === ASSIN0 && assinTrava('ampliar_area') === '');
  // achado 11 · redesenho só quando a faixa muda; cadastro só nas telas que medem
  const LS = []; window.addEventListener = (t, f) => LS.push(f); const tela = { n: 0, setState() { this.n++; } };
  localStorage.setItem(ASSIN_KEY, JSON.stringify({ v: ASSIN_CENV, assin: st })); assinAvisoVals(tela, {});
  LS.forEach(f => f({ key: ASSIN_CADKEY })); const n1 = tela.n;
  const st3 = assinClone(st); st3.recibos = { x: { id: 'PAG-9' } }; localStorage.setItem(ASSIN_KEY, JSON.stringify({ v: ASSIN_CENV, assin: st3, outra: 1 })); LS.forEach(f => f({ key: ASSIN_KEY })); const n2 = tela.n;
  const st4 = assinClone(st); st4.orgs.sr.faturas.find(f => f.id === 'sr-2026-09').st = 'paga'; localStorage.setItem(ASSIN_KEY, JSON.stringify({ v: ASSIN_CENV, assin: st4 })); LS.forEach(f => f({ key: ASSIN_KEY })); const n3 = tela.n;
  ok('B7 tela sem medição: o cadastro não redesenha; gravação que não muda estado, dias nem data não redesenha; pagar redesenha', n1 === 0 && n2 === 0 && n3 === 1, [n1, n2, n3]);
  const tela2 = { n: 0, setState() { this.n++; } }; assinOuvir(tela2, true); LS.slice(-1)[0]({ key: ASSIN_CADKEY });
  ok('B7b tela que mede a área (CF-05, BO-01, BO-02) redesenha quando o cadastro muda', tela2.n === 1);
}
print('TOTAL ' + R.length + ' · falhas ' + R.filter(x => !x).length);
