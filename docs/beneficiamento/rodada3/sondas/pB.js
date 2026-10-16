// B · a falta na execução depois da reposição (Pedir mais caixas): (1) sobra devolvida + estorno do descarte; (2) avaria de caixas em uso.
// (3) laudo reprovado da avaria e a fonte "quarentena" da recomendação
const out = { passos: [] }; let c;
const P = (n, x) => out.passos.push(Object.assign({ n }, x, { V: zOraculo(c) }));
function base() { c = cenClone(CEN0); zStep(c, 'NF 7731 1200', x => zNF(x, 'CX26-02', 1200, 'NF 7731', true, 'r7731'));
  const r = zStep(c, 'nova L39-132', x => benNova(x, { lotes: [{ lote: 'L39-132', kg: prFis(x, 'L39-132') }] }, IG)); const A = r.id;
  zStep(c, 'liberar A', x => benAutorizarLiberar(x, A, IG)); const ra = c.ordens[A].req; zStep(c, 'entregar A', x => cenEntregar(x, ra, CX, 1169, IG, RU));
  zStep(c, 'iniciar A', x => benIniciar(x, A, IG)); return { A, ra }; }
// (1) roteiro do limite adicional, com nota extra para o pedido caber
{ const { A, ra } = base(); zStep(c, 'NF-Y 1000 CX26-01', x => zNF(x, 'CX26-01', 1000, 'NF-Y', true));
  zStep(c, 'A: Produto 1000', x => zSP(x, A, 1000)); zStep(c, 'A: descarte 2000', x => zSD(x, A, 2000));
  const q = benDevPadrao(c, c.ordens[A], c.reqs[ra].itens[0], ra); zStep(c, 'A: devolver sobra ' + q, x => cenDevolver(x, ra, CX, q, true, RU));
  const sd = c.ordens[A].ben.sai.find(s => s.fluxo === 'Descarte').id; zStep(c, 'A: estornar descarte', x => benEstornar(x, A, sd, 'Pesagem refeita', '', IG));
  P('(1) após estorno', { est: zEst(c, A), A: zLin(c, A) });
  zStep(c, 'A: pedir 9', x => benComplementar(x, A, 9, IG)); P('(1) após pedir 9', { est: zEst(c, A), A: zLin(c, A) });
  zStep(c, 'A: pedir 130', x => benComplementar(x, A, 130, IG)); P('(1) após pedir 9+130 = 139', { est: zEst(c, A), A: zLin(c, A) });
  const f = benFaltaCx(c, c.ordens[A]); zStep(c, 'A: pedir a sugestão ' + f, x => benComplementar(x, A, f, IG)); P('(1) após pedir a nova sugestão', { est: zEst(c, A), A: zLin(c, A) }); }
// (2) avaria de 50 caixas em uso, sem sobra
{ const { A, ra } = base(); zStep(c, 'NF-Y 1000 CX26-01', x => zNF(x, 'CX26-01', 1000, 'NF-Y', true)); zStep(c, 'A: Produto 500', x => zSP(x, A, 500));
  zStep(c, 'A: devolver 50 avariadas', x => cenDevolver(x, ra, CX, 50, false, RU)); P('(2) após avaria', { est: zEst(c, A), A: zLin(c, A), cx02: zLot(c, 'CX26-02') });
  zStep(c, 'A: pedir 50', x => benComplementar(x, A, 50, IG)); P('(2) após pedir 50', { est: zEst(c, A), A: zLin(c, A) });
  benLinhas(c, c.ordens[A]).forEach(x => { const p = zPend(c, x.rid); if (p > 0) zStep(c, 'entregar ' + x.rid + ' ' + p, y => cenEntregar(y, x.rid, CX, p, IG, RU)); });
  P('(2) após entregar as 50', { est: zEst(c, A), A: zLin(c, A) });
  // segue até o fim com as caixas que tem: 669 de produto (6.690 kg) e 110 kg de descarte
  zStep(c, 'A: Produto 669', x => zSP(x, A, 669, 'B')); P('(2) após usar as 669', { est: zEst(c, A), A: zLin(c, A) });
  // (3) laudo reprovado das 50 avariadas e uma ordem nova sem caixas
  zStep(c, 'Ana reprova a quarentena do CX26-02', x => cenReprovarQuarentena(x, CX + '|CX26-02', 'LAUDO-REP-1', 'caixas quebradas', AN));
  P('(3) lote após reprovar', { cx02: zLot(c, 'CX26-02'), quar: benQuarCx(c) });
  const im = benImpedimentos(c, c.ordens['OB-0112']).find(x => x.cx); P('(3) recomendação da OB-0112', { t: im && im.t, falta: im && im.link.falta, fontes: im && im.link.fontes, cobre: im && im.link.cobre, why: im && im.link.why, h: im && im.link.h, bt: im && im.link.t });
  const lq = zStep(c, 'seguir a fonte quarentena (laudo que libera)', x => cenLiberarQuarentena(x, CX + '|CX26-02', 'LAUDO-OK', AN)); P('(3) seguir', { r: lq.erro || lq.msg }); }
out.log = LOG; out.violacoes = out.passos.filter(p => p.V.length).map(p => [p.n, p.V]); print(JSON.stringify(out, null, 1));
