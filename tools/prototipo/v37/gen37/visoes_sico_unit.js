// V2-3 · ícone da situação oculta (g2sicoPart), sem navegador: node visoes_sico_unit.js (dados sintéticos)
// S1 parte com selo de estado (de): o ícone leva o significado e o próximo passo (G2_DICAS)
// S2 célula sem parte, cor pela coluna (chips): o bloqueio vira ícone vermelho com o texto curto (regressão do comentário de linha, Codex 6180855818)
// S3 estado normal (sem cor de atenção) não vira ícone · S4 várias colunas ocultas (ks): cada uma dá o seu ícone
// VISOES_G2LIB=<arquivo> roda contra outro g2lib (contraprova).
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(process.env.VISOES_G2LIB || path.join(__dirname, 'g2lib.js'), 'utf8');
const G = new Function('const G2_GLOSS=[]; var location={search:"",pathname:"/X.dc.html",hash:""};\n' + src + '\nreturn {g2sicoPart, G2_DICAS};')();
let ok = 0, falhas = 0;
const chk = (n, c, x) => { if (c) { ok++; console.log('OK  ' + n); } else { falhas++; console.log('FALHOU ' + n + ' · ' + JSON.stringify(x)); } };
const sp = { sico: { k: 'sit' }, cols: [{ k: 'id', l: 'Ordem' }, { k: 'sit', l: 'Situação', chips: { 'Impedida': 'red', 'Livre': 'green' } }, { k: 'pend', l: 'Pendência' }] };
const r1 = { id: 'a', v: { sit: 'x' }, p: { sit: [{ k: 'chip', t: 'Falta insumo · Ureia 45%', c: 'red', de: 1 }] } };
const p1 = G.g2sicoPart(r1, sp);
chk('S1 selo com de: ícone vermelho, texto curto e o próximo passo na dica', p1 && p1.c === 'red' && p1.curto === 'Falta insumo · Ureia 45%' && /Próximo passo/.test(p1.t) && /agrônomo/.test(p1.t), p1);
const r2 = { id: 'b', v: { sit: 'Impedida' } };
const p2 = G.g2sicoPart(r2, sp);
chk('S2 sem parte, cor pela coluna (chips): "Impedida" vira ícone vermelho', p2 && p2.c === 'red' && p2.curto === 'Impedida' && p2.t === 'Situação: Impedida', p2);
chk('S3 estado normal ("Livre", verde) não vira ícone', G.g2sicoPart({ id: 'c', v: { sit: 'Livre' } }, sp) === null);
const r4 = { id: 'd', v: {}, p: { pend: [{ k: 'chip', t: 'Conflito', c: 'red', dica: 'parada da B3' }] } };
const p4 = G.g2sicoPart(r4, sp, 'pend');
chk('S4 coluna pedida (ks): Pendência dá o próprio ícone com o detalhe', p4 && p4.t === 'Pendência: Conflito · parada da B3' && p4.curto === 'Conflito', p4);
console.log('TOTAL ' + (ok + falhas) + ' · OK ' + ok + ' · FALHAS ' + falhas);
process.exit(falhas ? 1 : 0);
