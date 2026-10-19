// CMP-MAT (V69) · regras de Compras de materiais, peças e serviços sem navegador (compras_materiais_unit_test.py monta: perfis do g2lib +
// cenário + regras da manutenção, que trazem as de dados_compras_mat.js). Cada caso parte da semente (MAN0). Saída: uma linha JSON.
const R = []; const ok = (n, cond, info) => R.push({ n, ok: !!cond, info: cond ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 600) });
const caso = (n, fn) => { try { fn(); } catch (e) { R.push({ n: n + ' (exceção)', ok: false, info: String(e && e.stack || e).slice(0, 600) }); } };
const S = () => manClone(MAN0);
const OT = g2pf('Otávio'), ZE = g2pf('Zé'), ANA = g2pf('Ana'), RUI = g2pf('Rui'), CAIO = g2pf('Caio');
const run = (c, fn) => { const cc = manClone(c); let r; try { r = fn(cc) || {}; } catch (e) { r = { erro: String(e.message || e) }; } if (!r.erro && !r.nada) Object.assign(c, cc); return r; };
const foto = c => JSON.stringify([c.itens, c.oms, c.cmp, c.seqsc]);

caso('semente', () => {
  const q = MAN0.cmp.reqs;
  ok('S1 · três requisições, uma por origem e por etapa: SC-038 serviço da OM-0233 (Pedido emitido), SC-039 reposição (Em cotação), SC-040 avulsa (A cotar)',
    q['SC-038'].orig === 'om' && q['SC-038'].tipo === 'Serviço' && q['SC-038'].om === 'OM-0233' && q['SC-038'].etapa === 'Pedido emitido'
    && q['SC-039'].orig === 'rep' && q['SC-039'].etapa === 'Em cotação' && q['SC-040'].orig === 'avulsa' && q['SC-040'].etapa === 'A cotar', Object.values(q).map(r => [r.id, r.orig, r.etapa]));
  ok('S2 · nenhuma requisição de material, peça ou serviço tem safra ou cultura', Object.values(q).every(r => !('safra' in r) && !('cultura' in r) && !('saf' in r)), Object.keys(q['SC-040']));
  const c = S(); const p39 = cmmProps(c, c.cmp.reqs['SC-039']);
  ok('S3 · paridade Python × JS: as propostas da semente (SC-039) são as mesmas da regra cmmProps', JSON.stringify(p39.map(p => [p.f, p.valor, p.prazo])) === JSON.stringify(c.cmp.reqs['SC-039'].cot.props.map(p => [p.f, p.valor, p.prazo])), [p39, c.cmp.reqs['SC-039'].cot.props]);
  ok('S4 · cotação só a homologado do grupo: o serviço convida F08 e F10; F11 (não homologado) fica fora', JSON.stringify(c.cmp.reqs['SC-038'].cot.conv) === JSON.stringify(['F08', 'F10']) && cmmForaRegra(c.cmp.reqs['SC-038']).map(f => f.id).join() === 'F11', c.cmp.reqs['SC-038'].cot);
  ok('S5 · grupos dos itens: filtro em Peças, graxa e óleos em Lubrificantes (grupos de dados2.GRUPOS e de docs/pcm-suprimentos)', cmmGrupoItem('FIL-MF4292') === 'Peças' && cmmGrupoItem('GR-EP2') === 'Lubrificantes' && c.cmp.reqs['SC-039'].itens[0].grupo === 'Peças', [cmmGrupoItem('FIL-MF4292'), cmmGrupoItem('GR-EP2')]);
  ok('S6 · pedido da semente na série de manutenção PC-2nn (PC-201) e próximo PC-202', c.cmp.reqs['SC-038'].ped.id === 'PC-201' && c.cmp.seqpc === 202, [c.cmp.reqs['SC-038'].ped, c.cmp.seqpc]);
});

caso('reposição', () => {
  const c = S(); const rp = cmmRepos(c);
  ok('R1 · abaixo do ponto de pedido na semente: só a Graxa EP2 (livre 18 kg < 20 kg), repõe até 40 kg = 22 kg; o filtro MF 4292 (0 un) já está pedido na SC-039',
    rp.length === 1 && rp[0].k === 'GR-EP2' && rp[0].livre === 18 && rp[0].qtd === 22 && !rp.some(x => x.k === 'FIL-MF4292'), rp);
  const a = foto(c); const n = run(c, x => cmmRepor(x, 'GR-EP2', CAIO));
  ok('R2 · NEGATIVO Caio (PCP) não abre reposição: recusa com o motivo e nada muda', /almoxarife/.test(n.erro || '') && foto(c) === a, n);
  const r = run(c, x => cmmRepor(x, 'GR-EP2', RUI)); const q = c.cmp.reqs[r.id];
  ok('R3 · Rui abre a SC-041 de reposição: 22 kg de Lubrificantes, Almoxarifado da oficina, A cotar, por Rui (almoxarife); a sugestão some', r.id === 'SC-041' && q.orig === 'rep' && q.itens[0].qtd === 22 && q.itens[0].grupo === 'Lubrificantes' && q.cc === 'Almoxarifado da oficina' && q.etapa === 'A cotar' && /Rui \(almoxarife\)/.test(q.por) && !cmmRepos(c).length, [r, q]);
  const r2 = run(c, x => cmmRepor(x, 'GR-EP2', RUI));
  ok('R4 · repetir não abre outra requisição', r2.nada && Object.keys(c.cmp.reqs).length === 4, r2);
  run(c, x => cmmCotar(x, 'SC-041', ANA)); const p = cmmSugerida(c, c.cmp.reqs['SC-041']); run(c, x => cmmPedir(x, 'SC-041', p.f, '', ANA));
  const s0 = c.itens['GR-EP2'].saldo; const rc = run(c, x => cmmReceber(x, 'SC-041', RUI));
  ok('R5 · receber a reposição: +22 kg no saldo da oficina (estoque, sem reserva) e a requisição fica Recebida', !rc.erro && c.itens['GR-EP2'].saldo === s0 + 22 && c.itens['GR-EP2'].reservado === 0 && c.cmp.reqs['SC-041'].etapa === 'Recebida' && /estoque da oficina/.test(rc.msg), rc);
  const rc2 = run(c, x => cmmReceber(x, 'SC-041', RUI));
  ok('R6 · receber de novo não soma (recibo)', rc2.nada && c.itens['GR-EP2'].saldo === s0 + 22, rc2);
});

caso('peça da OM', () => {
  const c = S(); manGerarTodas(c, null, OT); const id = 'OM-0235';
  ok('O1 · OM-0235 (Trator 03) gerada com Falta peça: Filtro de óleo MF 4292', manFalta(c, c.oms[id]).map(p => p.item).join() === 'FIL-MF4292', manFalta(c, c.oms[id]));
  const sc = run(c, x => manSolicitar(x, id, OT)); const q = c.cmp.reqs['SC-041'];
  ok('O2 · "Solicitar compra" da OM cria a SC-041 na fila de Compras: origem OM, ativo a03, 1 un, A cotar, sem safra', !sc.erro && q && q.orig === 'om' && q.om === id && q.aid === 'a03' && q.itens[0].qtd === 1 && q.etapa === 'A cotar' && !('safra' in q), [sc, q]);
  const a = foto(c); const nc = run(c, x => cmmCotar(x, 'SC-041', ZE));
  ok('O3 · NEGATIVO Zé (mecânico) não cota: recusa com o motivo, nada muda', /quem compra/.test(nc.erro || '') && foto(c) === a, nc);
  const ct = run(c, x => cmmCotar(x, 'SC-041', ANA)); const props = c.cmp.reqs['SC-041'].cot.props;
  ok('O4 · Ana cota: os 2 homologados de Peças (F08 e F09), propostas na hora', !ct.erro && props.map(p => p.f).join() === 'F08,F09' && c.cmp.reqs['SC-041'].etapa === 'Em cotação', [ct, props]);
  const ref = cmmSugerida(c, c.cmp.reqs['SC-041']);
  ok('O5 · referência = menor custo que chega a tempo da janela da OM (24/09): F08, R$ 160,00, 1 dia (F09 é R$ 4,80 mais barata e chega em 29/09)', ref.f === 'F08' && ref.valor === 160 && ref.chega === '2026-09-24' && props.find(p => p.f === 'F09').valor === 155.2 && props.find(p => p.f === 'F09').chega === '2026-09-29', [ref, props]);
  const sj = run(c, x => cmmPedir(x, 'SC-041', 'F09', '', ANA));
  ok('O6 · NEGATIVO escolher a F09 (mais barata e atrasada) sem justificativa é recusado', /Justifique/.test(sj.erro || '') && c.cmp.reqs['SC-041'].etapa === 'Em cotação', sj);
  const pd = run(c, x => cmmPedir(x, 'SC-041', 'F08', '', ANA)); const ped = c.cmp.reqs['SC-041'].ped;
  ok('O7 · pedido PC-202 (a semente já tem a PC-201) para F08, R$ 160,00, previsão 24/09, por Ana (gestora)', !pd.erro && ped.id === 'PC-202' && ped.f === 'F08' && ped.valor === 160 && ped.prev === '2026-09-24' && /Ana \(gestora\)/.test(ped.por), [pd, ped]);
  const pd2 = run(c, x => cmmPedir(x, 'SC-041', 'F08', '', ANA));
  ok('O8 · emitir de novo não cria outro pedido', pd2.nada && c.cmp.seqpc === 203, pd2);
  const f0 = manClone(c.itens['FIL-MF4292']); const rc = run(c, x => cmmReceber(x, 'SC-041', RUI)); const p0 = c.oms[id].pecas.find(p => p.item === 'FIL-MF4292');
  ok('O9 · receber a peça da OM (D5, proprietário 16/10): +1 un no saldo e reservado +1 para a OM-0235 (o livre não cresce); SC Recebida e o.sc.rec',
    !rc.erro && c.itens['FIL-MF4292'].saldo === f0.saldo + 1 && c.itens['FIL-MF4292'].reservado === f0.reservado + 1 && p0.res === 1 && c.cmp.reqs['SC-041'].etapa === 'Recebida' && c.cmp.reqs['SC-041'].rec.dest === 'om'
    && c.oms[id].sc.rec === c.hoje && /Reservado para OM-0235/.test(rc.msg) && /pronta para liberar/.test(rc.msg), [rc, c.itens['FIL-MF4292'], p0]);
  ok('O10 · com a peça no saldo, a OM-0235 não tem mais Falta peça', !manFalta(c, c.oms[id]).length, manFalta(c, c.oms[id]));
  const ol0 = c.itens['OL-1540'].reservado; const lb = run(c, x => manLiberar(x, id, false, OT, {}));
  ok('O11 · liberar a OM-0235 não reserva o filtro de novo (segue +1, do recebimento) e reserva o óleo (12 L) uma vez', !lb.erro && c.oms[id].etapa === 'Liberadas' && c.itens['FIL-MF4292'].reservado === f0.reservado + 1 && c.itens['OL-1540'].reservado === ol0 + 12, [lb, c.itens['FIL-MF4292'], c.itens['OL-1540']]);
  ok('O12 · o filtro reservado não conta como livre: segue coberto pela SC-039 (livre 0 + 4 pedidos ≥ 2)', !cmmRepos(c).some(x => x.k === 'FIL-MF4292'), cmmRepos(c));
  const mr = run(c, x => manReceber(x, id, OT));
  ok('O13 · a ponte da Manutenção (Registrar recebimento) depois de Compras não soma de novo', mr.nada && c.itens['FIL-MF4292'].saldo === f0.saldo + 1, mr);
});

caso('ponte da Manutenção primeiro', () => {
  const c = S(); manGerarTodas(c, null, OT); run(c, x => manSolicitar(x, 'OM-0235', OT)); const f0 = manClone(c.itens['FIL-MF4292']);
  const mr = run(c, x => manReceber(x, 'OM-0235', OT));
  ok('P1 · receber pela ponte da Manutenção deixa a SC-041 Recebida em Compras (uma função só) e o saldo +1', !mr.erro && c.cmp.reqs['SC-041'].etapa === 'Recebida' && c.itens['FIL-MF4292'].saldo === f0.saldo + 1, [mr, c.cmp.reqs['SC-041']]);
  const rc = run(c, x => cmmReceber(x, 'SC-041', RUI));
  ok('P2 · Compras não recebe de novo (recibo)', rc.nada && c.itens['FIL-MF4292'].saldo === f0.saldo + 1, rc);
});

caso('serviço', () => {
  const c = S(); const o0 = manCusto(c, c.oms['OM-0233'], 'est'); const a = foto(c);
  const nr = run(c, x => cmmReceber(x, 'SC-038', RUI));
  ok('V1 · NEGATIVO serviço não tem recebimento de estoque', /aceite/.test(nr.erro || '') && foto(c) === a, nr);
  const nz = run(c, x => cmmAceitar(x, 'SC-038', ZE));
  ok('V2 · NEGATIVO Zé não aceita o serviço (PCM ou gestora)', /PCM/.test(nz.erro || '') && foto(c) === a, nz);
  const ac = run(c, x => cmmAceitar(x, 'SC-038', OT)); const o = c.oms['OM-0233']; const v = c.cmp.reqs['SC-038'].ped.valor;
  ok('V3 · Otávio aceita: SC-038 Aceita; o valor do PC-201 (R$ 1.843,00, F10) vira custo de terceiro da OM-0233 e entra no custo pela função única',
    !ac.erro && c.cmp.reqs['SC-038'].etapa === 'Aceita' && v === 1843 && c.cmp.reqs['SC-038'].ped.f === 'F10' && o.terc === 1843 && Math.abs(manCusto(c, o, 'est') - (o0 + 1843)) < 1e-9 && o.servs[0].sc === 'SC-038', [ac, o.terc, manCusto(c, o, 'est'), o0]);
  ok('V4 · o serviço não mexe em saldo de peça', JSON.stringify(c.itens) === JSON.stringify(MAN0.itens), '');
  const ac2 = run(c, x => cmmAceitar(x, 'SC-038', OT));
  ok('V5 · aceitar de novo não lança o custo duas vezes', ac2.nada && c.oms['OM-0233'].terc === 1843, ac2);
});

caso('avulsa', () => {
  const c = S(); const a = foto(c);
  const e = run(c, x => cmmNova(x, { tipo: 'Material', nome: '', qtd: '0', destino: '', urg: '', motivo: '' }, ZE));
  ok('A1 · NEGATIVO avulsa vazia: erros por campo (item, quantidade, estimativa, destino, urgência, motivo) e nada é gravado; safra e cultura não são pedidas',
    e.erro && ['nome', 'qtd', 'preco', 'destino', 'urg', 'motivo'].every(k => e.err[k]) && !('safra' in e.err) && !('cultura' in e.err) && foto(c) === a, e);
  const r = run(c, x => cmmNova(x, { tipo: 'Material', nome: 'Luva de PVC 100 mm', un: 'un', qtd: '6', preco: '42,50', destino: 'a11', urg: 'Urgente', motivo: 'vazamento na adutora' }, g2pf('João')));
  const q = c.cmp.reqs[r.id];
  ok('A2 · João (irrigante) abre a SC-041 avulsa para o ativo a11 (Bomba do Pivô 2), urgente, precisa até 24/09, Materiais gerais, sem safra',
    !r.erro && r.id === 'SC-041' && q.aid === 'a11' && q.urg === 'Urgente' && q.ate === '2026-09-24' && q.itens[0].grupo === 'Materiais gerais' && q.itens[0].preco === 42.5 && !('safra' in q), [r, q]);
  run(c, x => cmmCotar(x, r.id, ANA)); const ref = cmmSugerida(c, c.cmp.reqs[r.id]); run(c, x => cmmPedir(x, r.id, ref.f, '', ANA));
  const it0 = JSON.stringify(c.itens); const rc = run(c, x => cmmReceber(x, r.id, ANA));
  ok('A3 · material sem código: recebimento vai direto ao destino (consumo), sem mexer no saldo da oficina', !rc.erro && JSON.stringify(c.itens) === it0 && /consumo direto/.test(rc.msg) && c.cmp.reqs[r.id].rec.dest === 'cc', rc);
  const sv = run(c, x => cmmNova(x, { tipo: 'Serviço', nome: 'Limpeza do ar-condicionado do escritório', qtd: '1', preco: '450', destino: 'Sede', urg: 'Normal', motivo: 'manutenção anual' }, ANA));
  ok('A4 · serviço avulso num centro de custo (Sede), sem data pela urgência Normal', !sv.erro && c.cmp.reqs[sv.id].cc === 'Sede' && c.cmp.reqs[sv.id].ate === '' && c.cmp.reqs[sv.id].itens[0].un === 'serv', sv);
});

caso('alçada', () => {
  const c = S(); const r = run(c, x => cmmNova(x, { tipo: 'Serviço', nome: 'Retífica do motor da colhedora', qtd: '1', preco: '62000', destino: 'a08', urg: 'Normal', motivo: 'perda de compressão' }, OT));
  run(c, x => cmmCotar(x, r.id, ANA)); const ref = cmmSugerida(c, c.cmp.reqs[r.id]);
  ok('L1 · R$ 60.140,00 (> R$ 50.000) é do 2º nível: Ana (gerente da fazenda) emite', cmmNivel(ref.valor) === 1 && cmmAlcIdx(ANA) === 1, [ref, cmmNivel(ref.valor)]);
  c.cmp.reqs[r.id].cot.props.forEach(p => { p.valor = 320000; }); const pd = run(c, x => cmmPedir(x, r.id, ref.f, '', ANA));
  ok('L2 · NEGATIVO acima de R$ 300.000 é da Direção: recusado com o motivo, sem pedido', /Direção/.test(pd.erro || '') && !c.cmp.reqs[r.id].ped, pd);
});

caso('estado salvo antes da V69', () => {
  const c = S(); delete c.cmp; Object.values(c.itens).forEach(it => { delete it.min; delete it.max; });
  ok('E1 · sem c.cmp e sem min/max a leitura usa a semente (reposição e fila não quebram)', cmmRepos(c).map(x => x.k).join() === 'GR-EP2' && Object.keys(cmmDe(c).reqs).length === 3, cmmRepos(c));
  const r = run(c, x => cmmRepor(x, 'GR-EP2', RUI));
  ok('E2 · a primeira escrita cria c.cmp a partir da semente', !r.erro && c.cmp && Object.keys(c.cmp.reqs).length === 4, r);
});

print(JSON.stringify(R));
