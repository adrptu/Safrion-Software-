// COLUNAS-1 · colunas essenciais, lote 1 (pedido do proprietário de 10/10): regras das linhas da Manutenção e da busca da SAF, sem navegador.
// colunas1_unit_test.py monta: perfis do g2lib + cenário único e regras da manutenção (dados_manutencao) + MA_JS e PM_JS (areas/maquinas.py)
// + cultBusca, e3Busca e e3Achar (safra.js) + este arquivo. Cada caso parte do seed (MAN0). Saída: uma linha JSON.
const R = []; const ok = (n, cond, info) => R.push({ n, ok: !!cond, info: cond ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 600) });
const caso = (n, fn) => { try { fn(); } catch (e) { R.push({ n: n + ' (exceção)', ok: false, info: String(e && e.stack || e).slice(0, 600) }); } };
const S = () => manClone(MAN0);
const txt = (ps) => (ps || []).filter(p => p.t).map(p => p.t).join(' ');

caso('g_om', () => {
  const c = S(); const o = c.oms['OM-0234']; const r = ma_linhaOm(c, o);
  ok('MA Ordens · a célula Ordem só tem o ID (link #om=); o Ativo vai para coluna própria (R-01)', r.p.om.length === 1 && r.p.om[0].k === 'link' && r.p.om[0].t === 'OM-0234' && txt(r.p.ativo) === c.ativos[o.aid].nome, [r.p.om, r.p.ativo]);
  ok('MA Ordens · Serviço sem o tipo; tipo, plano e versão vão ao painel e ao d_om (Serviço · tipo)', txt(r.p.serv) === o.serv && txt(r.p.servt) === o.serv + ' Preventiva · ' + o.pid + ' v' + o.ver, [r.p.serv, r.p.servt]);
  ok('MA Ordens · a busca acha a OM pelo ativo, pelo tipo e pelo plano (saíram da célula)', r.s.om.indexOf(c.ativos[o.aid].nome) >= 0 && r.s.om.indexOf('Preventiva · ' + o.pid + ' v' + o.ver) >= 0, r.s.om);
  ok('MA Ordens · Tempo e Custo fora da linha (sem partes); o custo segue no valor para o d_om', !('tempo' in r.p) && typeof r.v.custo === 'number' && txt(r.p.custo).indexOf('R$') === 0, Object.keys(r.p));
  const cor = Object.values(c.oms).find(x => x.tipo === 'Corretiva'); const rc = ma_linhaOm(c, cor);
  ok('MA Ordens · corretiva: tipo e criticidade só no texto de busca e no d_om', rc.s.om.indexOf('Corretiva · ' + cor.crit) >= 0 && txt(rc.p.servt).indexOf('Corretiva · ' + cor.crit) >= 0 && txt(rc.p.serv) === cor.serv, [rc.s.om, rc.p.servt]);
});
caso('tipo', () => {
  const c = S(); const os = Object.values(c.oms);
  const por = {}; os.forEach(o => { const t = ma_tipoOm(o); (por[t] = por[t] || []).push(o.id); });
  ok('MA Ordens · filtro Tipo fora da grade: toda OM cai em Preventiva, Corretiva ou Pendência (nenhuma some)', Object.keys(por).every(t => MA_TIPOS.indexOf(t) >= 0) && Object.values(por).reduce((a, l) => a + l.length, 0) === os.length, por);
  ok('MA Ordens · filtro Tipo = Corretiva deixa só as corretivas (o mesmo critério do painel)', (por['Corretiva'] || []).length > 0 && por['Corretiva'].every(id => c.oms[id].tipo === 'Corretiva'), por['Corretiva']);
  ok('MA Ordens · filtro Tipo = Preventiva deixa só as preventivas', (por['Preventiva'] || []).length > 0 && por['Preventiva'].every(id => c.oms[id].tipo === 'Preventiva'), por['Preventiva']);
});
caso('g_at', () => {
  const c = S(); const a = c.ativos.a02; const r0 = ma_linhaAtv(c, a, 'mes');
  ok('MA Ativos · Leitura e Consumo fora da linha (sem partes); o local sai da célula Ativo', !('leit' in r0.p) && !('cons' in r0.p) && txt(r0.p.ativo).indexOf(a.local) < 0 && txt(r0.p.ativo).indexOf(a.modelo) >= 0, r0.p);
  ok('MA Ativos · a busca segue achando pelo local, pela leitura e pelo consumo', r0.s.ativo.indexOf(a.local) >= 0 && r0.s.ativo.indexOf(manLeitTxt(a)) >= 0, r0.s.ativo);
  a.suspeita = { val: 3140, data: c.hoje, origem: 'Abastecimento', tipo: 'alta' }; const r1 = ma_linhaAtv(c, a, 'mes');
  ok('MA Ativos · leitura a confirmar sobe para Em aberto, em 1º lugar (à vista também a 390 px)', r1.p.ab[0].k === 'chip' && r1.p.ab[0].t === 'Leitura a confirmar' && r1.s.ab.indexOf('Leitura a confirmar') >= 0 && r1.pend.indexOf('Leitura a confirmar') >= 0, r1.p.ab);
  delete a.suspeita; a.lh = 10; const r2 = ma_linhaAtv(c, a, 'mes'); const cons = ma_consumo(c, a);
  ok('MA Ativos · desvio de consumo ≥ 15 % sobe para Em aberto com o valor (o consumo fica na página do ativo)', cons && cons.desvio >= 15 && r2.p.ab.some(p => p.k === 'chip' && p.t === 'Desvio de consumo +' + manN(cons.desvio) + ' %'), [cons, r2.p.ab]);
  const todos = c.ordem.map(id => ma_linhaAtv(S(), S().ativos[id], 'mes')).filter(Boolean); const vaz = todos.filter(r => r.s.ab === '—');
  ok('MA Ativos · sem pendência nem ordem aberta, Em aberto mostra "—" (nunca célula vazia)', vaz.length > 0 && vaz.every(r => txt(r.p.ab) === '—'), todos.map(r => [r.id, r.s.ab]));
});
caso('g_ab', () => {
  const c = S(); const b = c.abast.find(x => !x.tipo && x.evid) || c.abast[0]; const r = ma_linhaAb(c, b);
  ok('MA Abastecimentos · Lançamento só com o ID; operador, evidência, tanque/lote, método e leitura fora da linha', r.p.id.length === 1 && r.p.id[0].t === b.id && !('tq' in r.p) && !('met' in r.p) && txt(r.p.data) === manBr(b.data) + ' ' + (b.hora || ''), r.p);
  ok('MA Abastecimentos · a busca acha o lançamento pelo operador, pelo tanque e pelo método', r.s.id.indexOf(b.op) >= 0 && r.s.id.indexOf(b.tq) >= 0 && /Tanque cheio|Estimada|Estorno/.test(r.s.id), r.s.id);
  const tqs = [...new Set(c.abast.map(x => x.tq))]; const um = c.abast.filter(x => x.tq === tqs[0]);
  ok('MA Abastecimentos · o filtro Tanque/lote (fora da grade) separa os lançamentos de um tanque', tqs.length >= 1 && um.length >= 1 && um.every(x => x.tq === tqs[0]), tqs);
});
caso('g_pl', () => {
  const c = S(); const ls = pmPlans(c).map(p => ma_linhaPl(c, p));
  ok('MA Planos · Aplica-se a, Serviços e Ativos fora da linha; seed sem pendência de vínculo (todos os candidatos vinculados)', ls.every(r => !('apl' in r.p) && !('svs' in r.p) && !('atv' in r.p) && !/sem vínculo/.test(txt(r.p.sit))), ls.map(r => [r.id, txt(r.p.sit)]));
  const p = pmPlans(c).find(x => pmVincs(c, x.id).length >= 2) || pmPlans(c).find(x => pmVincs(c, x.id).length >= 1);
  ok('MA Planos · a busca acha o plano pelo Aplica-se a e pelos serviços', ls.find(r => r.id === p.id).s.nome.indexOf(manAplTxt(c, p)) >= 0 && manWork(p).every(s => ls.find(r => r.id === p.id).s.nome.indexOf(s.nome) >= 0), ls.find(r => r.id === p.id).s.nome);
  const ks = pmVincs(c, p.id); delete c.vinc[ks[0]]; const r1 = ma_linhaPl(c, p); const n = pmCands(c, p).length;
  ok('MA Planos · ativo que o plano alcança sem vínculo vira pendência na Situação ("1 ativo … sem vínculo")', ks.length >= 2 ? (n === 1 && txt(r1.p.sit).indexOf(ma_semVincTxt(p, 1)) >= 0 && /^1 ativo (do modelo|indicado) sem vínculo$/.test(ma_semVincTxt(p, 1))) : true, [p.id, ks, txt(r1.p.sit)]);
  ks.slice(1).forEach(k => delete c.vinc[k]); const r2 = ma_linhaPl(c, p);
  ok('MA Planos · sem nenhum vínculo, a Situação diz "Sem ativos vinculados" e não repete a pendência', /Sem ativos vinculados/.test(txt(r2.p.sit)) && !/sem vínculo/.test(txt(r2.p.sit)), txt(r2.p.sit));
});
caso('g_so', () => {
  const c = S(); const rs = ma_linhasSemOrdem({}, c, { prazo: '30', tipo: '' }); const v = rs.find(r => r.k === 'venc'); const a = rs.find(r => r.k === 'achado');
  ok('MA Sem ordem · Item sem a versão do plano (vai ao painel do vencimento); a busca acha pela versão', v && !/ v\d/.test(txt(v.p.item)) && / v\d+ vencimento$/.test(v.s.item), v && [v.p.item, v.s.item]);
  ok('MA Sem ordem · O que sem a periodicidade (painel: Periodicidade); a busca acha por ela', v && v.p.oque.length === 1 && /a cada /.test(v.s.oque), v && [v.p.oque, v.s.oque]);
  const semLeit = rs.every(r => !r.p.ativo.some(p => p.k === 'mut' && / · \d/.test(p.t)));
  ok('MA Sem ordem · Ativo sem a leitura e a data (vão ao painel); os selos do ativo ficam (R-13)', semLeit && rs.every(r => r.p.ativo[0].k === 'b'), rs.map(r => r.p.ativo));
  ok('MA Sem ordem · o selo "Ativo bloqueado" continua na célula Ativo quando o ativo está bloqueado', rs.some(r => r.p.ativo.some(p => p.t === 'Ativo bloqueado')) || !Object.values(c.ativos).some(x => x.cond === 'Bloqueado'), rs.map(r => txt(r.p.ativo)));
  ok('MA Sem ordem · achado também sem a leitura na célula Ativo; a busca acha pela leitura', !a || (a.s.ativo.indexOf(' · ') > 0 && !a.p.ativo.some(p => p.k === 'mut')), a && [a.p.ativo, a.s.ativo]);
});
caso('SAF busca', () => {
  const rows = [{ id: 'c1', v: { local: 'T2', var: '58 W', aj: 2 }, s: { local: 'T2', meta: '62,5 sc/ha', ver: 'v3', tipo: 'Talhão inteiro', ate: '15/02/2027', fimpor: 'Pelo plano', saf: '' } },
    { id: 'g', v: { local: 'T1' }, s: { local: 'T1', tipo: '2 parcelas', ver: '' }, kids: [{ id: 'fora_x', v: { local: 'T1-A', var: 'Híbrido AG 8700' }, s: { local: 'T1-A', saf: 'Safrinha 2027', ate: 'sem fim', fimpor: 'Perene' } }] }];
  cultBusca(rows);
  ok('SAF etapa 2 · a busca acha o cultivo pela variedade, meta, versão, tipo, ajustes, ocupa até e fim por (saíram da linha)', ['58 W', '62,5 sc/ha', 'v3', 'Talhão inteiro', '2 ajustes locais', 'até 15/02/2027', 'Pelo plano'].every(t => rows[0].s.local.indexOf(t) >= 0) && rows[0].s.local.indexOf('T2 · ') === 0, rows[0].s.local);
  ok('SAF etapa 2 · a linha de outra safra é achada pela safra e pela variedade (sublinhas também)', ['Safrinha 2027', 'Híbrido AG 8700', 'Perene'].every(t => rows[1].kids[0].s.local.indexOf(t) >= 0), rows[1].kids[0].s.local);
  ok('SAF etapa 2 · valor vazio ou "—" não entra na busca', rows[1].s.local === 'T1 · 2 parcelas', rows[1].s.local);
  const op = [{ id: 'op:A', s: { nome: 'Adubação', area: '2.520 ha-op', rend: '18,00 ha/h' }, kids: [{ id: 'at:A|B', s: { nome: 'Cobertura', area: '350 ha', rend: '' } }] }];
  e3Busca(op);
  ok('SAF etapa 3 · a busca da g_op acha a operação pela área trabalhada e pelo rendimento (saíram da linha)', op[0].s.nome === 'Adubação · 2.520 ha-op · 18,00 ha/h' && op[0].kids[0].s.nome === 'Cobertura · 350 ha', [op[0].s.nome, op[0].kids[0].s.nome]);
  ok('SAF etapa 3 · e3Achar encontra a linha da árvore que abriu o formulário (a área trabalhada vem dela)', e3Achar(op, 'at:A|B') === op[0].kids[0] && e3Achar(op, 'x') === null);
});
print(JSON.stringify(R));
