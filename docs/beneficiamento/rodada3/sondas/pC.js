// C · laudo reprovado: a recomendação da ordem impedida cita a quarentena reprovada como fonte ("se a inspeção aprovar … libera"), e o
// "cobre" conta essas caixas; seguir a fonte é recusado pelo Estoque
const out = { passos: [] }; let c = cenClone(CEN0); const P = (n, x) => out.passos.push(Object.assign({ n }, x, { V: zOraculo(c) }));
// NF de 1.200 com 400 em quarentena (o recebimento parcial do U49a) e a gestora reprova a quarentena
zStep(c, 'NF 7731: 500 aptas + 700 em quarentena', x => { zNF(x, 'CX26-02', 500, 'NF 7731', true, 'r7731'); return zNF(x, 'CX26-02', 700, 'NF 7731', false); });
zStep(c, 'Ana reprova a quarentena (LAUDO-REP)', x => cenReprovarQuarentena(x, CX + '|CX26-02', 'LAUDO-REP', 'caixas mofadas', AN));
let r = zStep(c, 'nova L39-132 (1.169 cx)', x => benNova(x, { lotes: [{ lote: 'L39-132', kg: prFis(x, 'L39-132') }] }, IG)); const A = r.id;
const o = c.ordens[A]; const im = benImpedimentos(c, o).find(x => x.cx);
P('impedimento', { lote: zLot(c, 'CX26-02'), livre: benLivreCx(c), t: im && im.t, falta: im && im.link.falta, fontes: im && im.link.fontes, cobre: im && im.link.cobre, why: im && im.link.why, link: im && [im.link.t, im.link.h], prox: benProx(c, o).t });
r = zStep(c, 'seguir a fonte indicada (liberar a quarentena com laudo)', x => cenLiberarQuarentena(x, CX + '|CX26-02', 'LAUDO-2', AN)); P('seguir', { r: r.erro || r.msg });
r = zStep(c, 'liberar ' + A, x => benAutorizarLiberar(x, A, IG)); P('liberar', { r: r.erro || r.msg });
// variante: parte reprovada e parte pendente no mesmo lote
let c2 = cenClone(CEN0); c = c2; zStep(c, 'NF: 500 aptas + 200 quar', x => { zNF(x, 'CX26-02', 500, 'NF 7731', true, 'r7731'); return zNF(x, 'CX26-02', 200, 'NF 7731', false); });
zStep(c, 'reprova 200', x => cenReprovarQuarentena(x, CX + '|CX26-02', 'LAUDO-REP', 'mofo', AN)); zStep(c, 'devolução bloqueada de 30 da OB-0110 (nova quarentena pendente)', x => cenDevolver(x, 'REQ-030', CX, 30, false, RU));
r = zStep(c, 'nova L39-132', x => benNova(x, { lotes: [{ lote: 'L39-132', kg: prFis(x, 'L39-132') }] }, IG)); const A2 = r.id; const im2 = benImpedimentos(c, c.ordens[A2]).find(x => x.cx);
P('impedimento (parte reprovada, parte pendente)', { cx01: zLot(c, 'CX26-01'), cx02: zLot(c, 'CX26-02'), livre: benLivreCx(c), fontes: im2 && im2.link.fontes, cobre: im2 && im2.link.cobre, why: im2 && im2.link.why });
out.log = LOG; out.violacoes = out.passos.filter(p => p.V.length).map(p => [p.n, p.V]); print(JSON.stringify(out, null, 1));
