// I · caixas em uso devolvidas "bloqueadas para inspeção": a recomendação da outra ordem manda liberar a quarentena e a outra ordem leva as
// caixas de que a ordem em execução ainda precisa (ela fica com "Faltam N" e sem livre)
const out = { passos: [] }; let c = cenClone(CEN0); const P = (n, x) => out.passos.push(Object.assign({ n }, x, { V: zOraculo(c) }));
zStep(c, 'NF 7731 1200', x => zNF(x, 'CX26-02', 1200, 'NF 7731', true, 'r7731'));
let r = zStep(c, 'nova A L39-132', x => benNova(x, { lotes: [{ lote: 'L39-132', kg: prFis(x, 'L39-132') }] }, IG)); const A = r.id;
zStep(c, 'liberar A', x => benAutorizarLiberar(x, A, IG)); const ra = c.ordens[A].req; zStep(c, 'entregar A', x => cenEntregar(x, ra, CX, 1169, IG, RU)); zStep(c, 'iniciar A', x => benIniciar(x, A, IG));
zStep(c, 'A: Produto 500', x => zSP(x, A, 500));
r = zStep(c, 'Rui recebe 300 de A como bloqueadas para inspeção', x => cenDevolver(x, ra, CX, 300, false, RU));
P('A após a devolução bloqueada', { est: zEst(c, A), A: zLin(c, A), cx02: zLot(c, 'CX26-02'), cx01: zLot(c, 'CX26-01') });
// B: ordem nova de 881 (OB-0112 tem outra causa; criar a partir do L38-132 com 881 caixas digitadas)
r = zStep(c, 'nova B L38-132 com 800 cx', x => benNova(x, { lotes: [{ lote: 'L38-132', kg: prFis(x, 'L38-132') }], cx: 800 }, IG)); const B = r.id;
const im = benImpedimentos(c, c.ordens[B]).find(x => x.cx); P('recomendação de B', { t: im && im.t, why: im && im.link.why, fontes: im && im.link.fontes, cobre: im && im.link.cobre });
r = zStep(c, 'Ana libera a quarentena com laudo (segue a fonte)', x => cenLiberarQuarentena(x, CX + '|CX26-02', 'LAUDO-OK', AN)); P('após laudo', { r: r.erro || r.msg, cx02: zLot(c, 'CX26-02'), livre: benLivreCx(c), estA: zEst(c, A) });
r = zStep(c, 'liberar B', x => benAutorizarLiberar(x, B, IG)); P('após liberar B', { r: (r.erro || r.msg).slice(0, 300), estA: zEst(c, A), cx02: zLot(c, 'CX26-02') });
r = zStep(c, 'A: pedir a falta ' + benFaltaCx(c, c.ordens[A]), x => benComplementar(x, A, benFaltaCx(x, x.ordens[A]), IG)); P('A pede', { r: (r.erro || r.msg).slice(0, 400) });
out.log = LOG; out.violacoes = out.passos.filter(p => p.V.length).map(p => [p.n, p.V]); print(JSON.stringify(out, null, 1));
