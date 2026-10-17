// MUX-F1 · funções puras do mapa (areas/inicio.py, entre os marcadores <mux-puro>): vizinho pela seta, ordem da lista, endereço e busca.
// Sem navegador. Uso: node mapa_mux_unit.js [caminho do inicio.py]   (padrão: areas/inicio.py; contraprova: o inicio.py da base 0b3d0d4 não
// tem as funções e reprova U0).
//   U0 as funções existem no gerador (bloco <mux-puro>)
//   V  vizinho: direção certa, borda sem vizinho, alinhado vence torto, empate pela ordem do DOM e a propriedade do semiplano (2000 casos × 4 setas)
//   O  ordem da lista: a pior classe primeiro (ordem SEV), índice (satélite e solo) do pior ao melhor, sem dado no fim, empate pelo nome natural
//   H  endereço: lê e escreve #faz=&lay=&t=&dt=, ida e volta, chaves e valores desconhecidos ficam fora, sem chave do mapa → nada
//   B  busca: "P5", "PV05", "p05", "Pivô 5", "pivo 5" dão o mesmo pivô; "T4" e "Talhão 4" o mesmo talhão; ambíguo e inexistente → nada
'use strict';
const fs = require('fs'), path = require('path');
const arq = process.argv[2] || path.join(__dirname, 'areas', 'inicio.py');
const src = fs.readFileSync(arq, 'utf8');
let ok = 0, falha = 0;
const chk = (n, c, info) => { if (c) { ok++; console.log('OK    ' + n); } else { falha++; console.log('FALHA ' + n + (info === undefined ? '' : ' · ' + JSON.stringify(info))); } };
const a = src.indexOf('// <mux-puro>'), b = src.indexOf('// </mux-puro>');
chk('U0 bloco <mux-puro> no gerador (' + path.basename(arq) + ')', a >= 0 && b > a, [a, b]);
if (a < 0 || b < 0) { console.log('\nTOTAL ok ' + ok + ' · falha ' + falha); process.exit(1); }
const F = new Function(src.slice(a, b) + '\nreturn {muxVizinho, muxNome, muxRank, muxOrdem, muxHashLer, muxHashEscrever, muxChave, muxAcha};')();
const SEV = (src.match(/const SEV=(\[[^\]]*\]);/) || [])[1]; const sev = SEV ? JSON.parse(SEV.replace(/'/g, '"')) : null;
chk('U1 a ordem de gravidade é a SEV do mapa (fonte única, worstC)', Array.isArray(sev) && sev[0] === 'red' && sev.indexOf('none') === sev.length - 1, SEV);

// ---------- V · vizinho pela seta ----------
const V = F.muxVizinho;
const g = [{ x: 100, y: 24 }, { x: 316, y: 24 }, { x: 100, y: 88 }, { x: 316, y: 88 }];   // grade 2 × 2: 0 NO, 1 NE, 2 SO, 3 SE
chk('V1 NO → direita = NE', V(g, 0, 'ArrowRight') === 1); chk('V2 NO → baixo = SO', V(g, 0, 'ArrowDown') === 2);
chk('V3 NO → esquerda e cima: borda, sem vizinho', V(g, 0, 'ArrowLeft') === -1 && V(g, 0, 'ArrowUp') === -1);
chk('V4 SE → cima = NE; SE → esquerda = SO', V(g, 3, 'ArrowUp') === 1 && V(g, 3, 'ArrowLeft') === 2);
chk('V5 tecla que não é seta: nada', V(g, 0, 'Enter') === -1 && V(g, 0, 'Home') === -1);
chk('V6 o quase alinhado vence o mais perto e torto', V([{ x: 0, y: 0 }, { x: 100, y: 5 }, { x: 60, y: 50 }], 0, 'ArrowRight') === 1);
chk('V7 empate exato: o menor índice (ordem do DOM = ordem do nome)', V([{ x: 0, y: 0 }, { x: 50, y: 10 }, { x: 50, y: -10 }], 0, 'ArrowRight') === 1);
// a Santa Rita do protótipo (centros do SVG): T1 → direita = T2; T2 → direita = P1; T4 → cima = T1; C1 → esquerda = T7
const SR = { T1: [171, 157], T2: [453, 154], P1: [700, 158], P2: [902, 158], T4: [176, 471], T3: [453, 467], T7: [693, 470], C1: [893, 467] };
const ids = Object.keys(SR), cs = ids.map(k => ({ x: SR[k][0], y: SR[k][1] })); const nv = (t, k) => ids[V(cs, ids.indexOf(t), k)];
chk('V8 Santa Rita: T1→T2, T2→P1, T4↑T1, C1←T7, P2↓C1', nv('T1', 'ArrowRight') === 'T2' && nv('T2', 'ArrowRight') === 'P1' && nv('T4', 'ArrowUp') === 'T1' && nv('C1', 'ArrowLeft') === 'T7' && nv('P2', 'ArrowDown') === 'C1',
  [nv('T1', 'ArrowRight'), nv('T2', 'ArrowRight'), nv('T4', 'ArrowUp'), nv('C1', 'ArrowLeft'), nv('P2', 'ArrowDown')]);
let semente = 7; const rnd = () => ((semente = (semente * 1103515245 + 12345) % 2147483648) / 2147483648); let viol = 0;
for (let k = 0; k < 2000; k++) { const n = 2 + Math.floor(rnd() * 30); const c = Array.from({ length: n }, () => ({ x: Math.round(rnd() * 1000), y: Math.round(rnd() * 600) })); const i = Math.floor(rnd() * n);
  for (const [t, d] of [['ArrowRight', [1, 0]], ['ArrowLeft', [-1, 0]], ['ArrowDown', [0, 1]], ['ArrowUp', [0, -1]]]) { const j = V(c, i, t);
    const algum = c.some((p, q) => q !== i && ((p.x - c[i].x) * d[0] + (p.y - c[i].y) * d[1]) > 0);
    if (j >= 0 && ((c[j].x - c[i].x) * d[0] + (c[j].y - c[i].y) * d[1]) <= 0) viol++; if ((j >= 0) !== algum) viol++; } }
chk('V9 propriedade (2000 casos × 4 setas): o escolhido está sempre no semiplano da direção; só falta vizinho com o semiplano vazio', viol === 0, viol);

// ---------- O · ordem da lista ----------
const N = F.muxNome;
chk('O1 nome natural: P2 antes de P10; PV05 depois de PV04', ['P10', 'P2', 'P1'].sort(N).join() === 'P1,P2,P10' && N('PV04', 'PV05') < 0);
const rows = [{ nome: 'P10', c: { c: 'ok' } }, { nome: 'P2', c: { c: 'red' } }, { nome: 'P3', c: { c: 'none' } }, { nome: 'P1', c: { c: 'red' } }, { nome: 'P4', c: { c: 'yellow' } }, { nome: 'P5', c: { c: 'gray' } }];
const o1 = F.muxOrdem(rows, sev).map(r => r.nome);
chk('O2 a pior primeiro (vermelho, amarelo, verde, cinza, não se aplica); empate pelo nome', o1.join() === 'P1,P2,P4,P10,P5,P3', o1);
const sat = [{ nome: 'P1', c: { c: 'sat', k: 4 } }, { nome: 'P2', c: { c: 'cloud' } }, { nome: 'P3', c: { c: 'sat', k: 0 } }, { nome: 'P4', c: { c: 'gray' } }, { nome: 'P5', c: { c: 'sat', k: 2 } }];
const o2 = F.muxOrdem(sat, sev).map(r => r.nome);
chk('O3 satélite: do índice pior ao melhor, depois nuvem (sem leitura), depois sem cultura', o2.join() === 'P3,P5,P1,P2,P4', o2);
const solo = [{ nome: 'T1', c: { c: 'sat', solo: true, rk: 0.8 } }, { nome: 'T2', c: { c: 'sat', solo: true, rk: 0 } }, { nome: 'T3', c: { c: 'gray' } }];
chk('O4 solo: a classe pior (rk 0) primeiro; sem laudo no fim', F.muxOrdem(solo, sev).map(r => r.nome).join() === 'T2,T1,T3');
chk('O5 a ordem não altera a lista de entrada', rows[0].nome === 'P10');

// ---------- H · endereço ----------
const h1 = F.muxHashLer('#faz=LG&lay=sat&t=PV05&dt=25-09');
chk('H1 lê #faz=LG&lay=sat&t=PV05&dt=25-09', JSON.stringify(h1) === JSON.stringify({ faz: 'Lagoa Grande', lay: 'Satélite', t: 'PV05', dt: '25/09' }), h1);
chk('H2 escreve o mesmo endereço (ida e volta)', F.muxHashEscrever(h1) === '#faz=LG&lay=sat&t=PV05&dt=25-09', F.muxHashEscrever(h1));
const todas = ['Integrado', 'Satélite', 'Análises de solo', 'MIP/MID', 'O.S./prazos', 'Irrigação', 'Lavoura', 'Colheita', 'Custos'];
chk('H3 as 9 camadas e as 4 opções de fazenda vão e voltam', todas.every(l => ['Lagoa Grande', 'Santa Rita', 'Boa Vista', 'Todas'].every(f => {
  const o = F.muxHashLer(F.muxHashEscrever({ faz: f, lay: l })); return o && o.faz === f && o.lay === l; })));
const h4 = F.muxHashLer('#faz=XX&lay=nada&t=PV<05&dt=2025-09-25&foo=1');
chk('H4 valores desconhecidos ou fora do formato ficam fora (nada vira estado)', h4 === null, h4);
chk('H5 endereço de outra função (#talhao=PV05, #car:PV23, #desenhar=PV01) não é do mapa', F.muxHashLer('#talhao=PV05') === null && F.muxHashLer('#car:PV23') === null && F.muxHashLer('#desenhar=PV01') === null);
chk('H6 sem talhão e sem data: só fazenda e camada', F.muxHashEscrever({ faz: 'Santa Rita', lay: 'Irrigação', t: '', dt: '' }) === '#faz=SR&lay=irr');
chk('H7 minúsculas e %-codificação', JSON.stringify(F.muxHashLer('faz=sr&lay=PRAGAS&t=t4')) === JSON.stringify({ faz: 'Santa Rita', lay: 'MIP/MID', t: 'T4' }), F.muxHashLer('faz=sr&lay=PRAGAS&t=t4'));

// ---------- B · busca ----------
const L = [{ id: 'PV05', nome: 'P5', apelidos: ['Pivô 5'] }, { id: 'PV15', nome: 'P15', apelidos: ['Pivô 15'] }, { id: 'PV01', nome: 'P1', apelidos: ['Pivô 1'] }, { id: 'PV10', nome: 'P10', apelidos: ['Pivô 10'] }];
chk('B1 "P5", "PV05", "p05", "Pivô 5", "pivo 5", " p 5 " → PV05', ['P5', 'PV05', 'p05', 'Pivô 5', 'pivo 5', ' p 5 '].every(x => F.muxAcha(x, L) === 'PV05'), ['P5', 'PV05', 'p05', 'Pivô 5', 'pivo 5', ' p 5 '].map(x => F.muxAcha(x, L)));
chk('B2 "P1" é o P1 (exato vence o começo de P10 e P15)', F.muxAcha('P1', L) === 'PV01');
chk('B3 inexistente e vazio → nada', F.muxAcha('P99', L) === '' && F.muxAcha('', L) === '' && F.muxAcha('   ', L) === '');
const SRL = ['T1', 'T2', 'P1', 'P2', 'T4', 'T3', 'T7', 'C1'].map(t => ({ id: t, nome: t, apelidos: [] }));
chk('B4 Santa Rita: "T4", "t4" e "Talhão 4" → T4; "c1" → C1', F.muxAcha('T4', SRL) === 'T4' && F.muxAcha('t4', SRL) === 'T4' && F.muxAcha('Talhão 4', SRL) === 'T4' && F.muxAcha('c1', SRL) === 'C1');
chk('B5 ambíguo (só "T", que começa T1, T2…) → nada, nunca outro talhão em silêncio', F.muxAcha('T', SRL) === '');
console.log('\nTOTAL ok ' + ok + ' · falha ' + falha + ' · fonte: ' + path.basename(arq));
process.exit(falha ? 1 : 0);
