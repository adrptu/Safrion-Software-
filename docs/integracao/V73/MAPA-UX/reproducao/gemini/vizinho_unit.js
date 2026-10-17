// Teste de unidade da função pura vizinho() da g2_contraprova.html (extraída entre os marcadores <vizinho>).
// Uso: node vizinho_unit.js   (sem navegador; só a regra de vizinho espacial)
'use strict';
const fs = require('fs'), path = require('path');
const html = fs.readFileSync(path.join(__dirname, 'g2_contraprova.html'), 'utf8');
const a = html.indexOf('// <vizinho>'), b = html.indexOf('// </vizinho>');
if (a < 0 || b < 0) throw new Error('marcadores <vizinho> não encontrados');
const vizinho = new Function(html.slice(a, b) + '\nreturn vizinho;')();
let ok = 0, falha = 0;
const igual = (nome, obtido, esperado) => {
  if (obtido === esperado) { ok++; console.log(`ok    ${nome}: ${obtido}`); }
  else { falha++; console.log(`FALHA ${nome}: obtido ${obtido}, esperado ${esperado}`); }
};
// grade 2 × 2 da página: 0 NO, 1 NE, 2 SO, 3 SE (centros como no CSS: 200 px + 16 px de vão)
const g = [{ x: 100, y: 24 }, { x: 316, y: 24 }, { x: 100, y: 88 }, { x: 316, y: 88 }];
igual('NO → direita', vizinho(g, 0, 'ArrowRight'), 1);
igual('NO → baixo', vizinho(g, 0, 'ArrowDown'), 2);
igual('NO → esquerda (borda)', vizinho(g, 0, 'ArrowLeft'), -1);
igual('NO → cima (borda)', vizinho(g, 0, 'ArrowUp'), -1);
igual('SE → cima', vizinho(g, 3, 'ArrowUp'), 1);
igual('SE → esquerda', vizinho(g, 3, 'ArrowLeft'), 2);
igual('tecla que não é seta', vizinho(g, 0, 'Enter'), -1);
// desvio lateral pesa mais que a distância: o vizinho quase alinhado vence o mais perto e torto
const t = [{ x: 0, y: 0 }, { x: 100, y: 5 }, { x: 60, y: 50 }];
igual('alinhado vence torto', vizinho(t, 0, 'ArrowRight'), 1);
// empate exato: fica o menor índice (ordem do DOM = ordem da lista)
const e = [{ x: 0, y: 0 }, { x: 50, y: 10 }, { x: 50, y: -10 }];
igual('empate → menor índice', vizinho(e, 0, 'ArrowRight'), 1);
// propriedade, 2000 casos sintéticos: o escolhido está sempre no semiplano da direção, e só falta vizinho quando o semiplano está vazio
let semente = 7; const rnd = () => ((semente = (semente * 1103515245 + 12345) % 2147483648) / 2147483648);
let viol = 0;
for (let k = 0; k < 2000; k++) {
  const n = 2 + Math.floor(rnd() * 23);
  const c = Array.from({ length: n }, () => ({ x: Math.round(rnd() * 1000), y: Math.round(rnd() * 600) }));
  const i = Math.floor(rnd() * n);
  for (const [tecla, d] of [['ArrowRight', [1, 0]], ['ArrowLeft', [-1, 0]], ['ArrowDown', [0, 1]], ['ArrowUp', [0, -1]]]) {
    const j = vizinho(c, i, tecla);
    const algum = c.some((p, q) => q !== i && ((p.x - c[i].x) * d[0] + (p.y - c[i].y) * d[1]) > 0);
    if (j >= 0 && ((c[j].x - c[i].x) * d[0] + (c[j].y - c[i].y) * d[1]) <= 0) viol++;
    if ((j >= 0) !== algum) viol++;
  }
}
igual('propriedade (2000 casos × 4 setas): violações', viol, 0);
console.log(`\nTOTAL ok ${ok} · falha ${falha}`);
process.exit(falha ? 1 : 0);
