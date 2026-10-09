// Roda o serviço da tela (ocupacao.js, base ou novo) sobre as fixtures. Uso: node roda_servico.js <ocupacao.js> <fixtures.json> [semmsg]
// semmsg: não chama ocMsgTrava (a base faz laço dia a dia até 10^8 com perenes e congela).
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
eval(src + '\n;globalThis.OCX={ocCtx,ocOcupacoes,ocTabela,ocChecar,ocMsgTrava,ocMsgPend,ocFaixaTxt};');
const X = globalThis.OCX;
const dados = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const semmsg = process.argv[4] === 'semmsg';
const out = {};
let tTot = 0;
for (const f of dados.fixtures) {
  const c = f.ctx || dados.ctx;
  const ctx = X.ocCtx(c.culturas, c.cultivares, c.planos, f.folga);
  const t0 = process.hrtime.bigint();
  const r = X.ocChecar(ctx, f.safras, f.antes, f.depois, f.sid, f.alvo, f.T);
  const t1 = process.hrtime.bigint();
  const o = { trav: r.trav, pend: r.pend, aviso: r.aviso.map(y => y.id), ms_chk: Number(t1 - t0) / 1e6 };
  if (r.o && !semmsg) {
    o.mt = r.trav.length ? X.ocMsgTrava(ctx, r, f.sid, f.T, null) : '';
    o.mp = X.ocMsgPend(ctx, r, f.sid, null);
  }
  const occ = X.ocOcupacoes(ctx, f.safras, f.depois);
  const tal = [['T1', f.T], ['T2', f.T2]];
  const [L, band] = X.ocTabela(ctx, f.safras[f.sid], occ, tal, f.safras);
  const L1 = L.find(v => v.t === 'T1');
  o.tab = { trav: L1.trav, pend: L1.pend, sit: L1.sit, exc: L1.exc === undefined ? null : L1.exc, band, own: L1.own.map(x => x.id), fora: L1.fora.map(x => x.id),
    faixa: X.ocFaixaTxt(band, L, f.T + f.T2) };
  tTot += Number(process.hrtime.bigint() - t0) / 1e6;
  out[f.id] = o;
}
process.stdout.write(JSON.stringify({ src: process.argv[2], ms_total: tTot, res: out }));
