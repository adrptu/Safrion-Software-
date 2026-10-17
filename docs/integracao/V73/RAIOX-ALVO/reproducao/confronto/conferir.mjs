// Confere uma rodada nova (pasta de saída de rodar.sh) com os brutos versionados.
// Ignora só o que varia entre rodadas: tempo (quando, segundos, msRxGet, "rxGet … ms", 1ª linha do resumo da crítica) e
// o nome/origem do arquivo de entrada (arquivo, origem, nota). Números: tolerância relativa 1e-9 (versões de Node diferentes).
// Uso: node conferir.mjs <pasta reproducao/ versionada> <pasta de saída>
import fs from 'node:fs';
const [base, out] = process.argv.slice(2);
const VOL = new Set(['quando', 'segundos', 'msRxGet', 'arquivo', 'origem', 'nota']);
function cmp(a, b, p = '') {
  if (typeof a === 'number' && typeof b === 'number') return Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(a), Math.abs(b)) ? [] : [p];
  if (a === null || b === null || typeof a !== 'object' || typeof b !== 'object') return a === b ? [] : [p];
  if (Array.isArray(a) !== Array.isArray(b)) return [p];
  const d = []; for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) { if (VOL.has(k)) continue; if (!(k in a) || !(k in b)) { d.push(p + '/' + k); continue; } d.push(...cmp(a[k], b[k], p + '/' + k)); }
  return d;
}
const txt = (f, limpa) => limpa(fs.readFileSync(f, 'utf8'));
const semTempo = s => s.split('\n').slice(1).join('\n').replace(/rxGet [0-9.]+ ms/g, 'rxGet _ ms');
const id = s => s;
const casos = [
  ['crítica · repro.json', () => cmp(JSON.parse(fs.readFileSync(base + '/repro.json')), JSON.parse(fs.readFileSync(out + '/critica/repro.json')))],
  ['crítica · resumo.txt', () => txt(base + '/resumo.txt', semTempo) === txt(out + '/critica/resumo.txt', semTempo) ? [] : ['texto']],
  ['crítica · calor.txt', () => txt(base + '/calor.txt', id) === txt(out + '/critica/calor.txt', id) ? [] : ['texto']],
  ['confronto · confronto.json', () => cmp(JSON.parse(fs.readFileSync(base + '/confronto/confronto.json')), JSON.parse(fs.readFileSync(out + '/confronto/confronto.json')))],
  ['confronto · confronto.txt', () => txt(base + '/confronto/confronto.txt', id) === txt(out + '/confronto/confronto.txt', id) ? [] : ['texto']]];
let falhas = 0;
for (const [nome, fn] of casos) { const d = fn(); if (d.length) falhas++; console.log(nome + ': ' + (d.length ? 'DIFERE em ' + d.length + ' ponto(s): ' + d.slice(0, 8).join(', ') : 'igual ao versionado')); }
process.exit(falhas ? 1 : 0);
