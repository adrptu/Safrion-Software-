// Confere se o Node e o pnpm em uso são exatamente os fixados no repositório (PRD 23.1, ENG-006).
// Uso: pnpm run doctor   (o "pnpm doctor" sem "run" é um comando do próprio pnpm)
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';

const raiz = new URL('../../', import.meta.url);
const nodeFixado = readFileSync(new URL('.nvmrc', raiz), 'utf8').trim();
const pacote = JSON.parse(readFileSync(new URL('package.json', raiz), 'utf8'));
const pnpmFixado = String(pacote.packageManager ?? '')
  .replace(/^pnpm@/, '')
  .split('+')[0];
const consulta = spawnSync('pnpm', ['--version'], { encoding: 'utf8', shell: process.platform === 'win32' });
const pnpmEmUso = consulta.status === 0 ? consulta.stdout.trim() : 'não encontrado no PATH';
const nodeEmUso = process.version.replace(/^v/, '');

const problemas = [];
if (nodeEmUso !== nodeFixado)
  problemas.push(`Node ${nodeEmUso} em uso; o repositório fixa ${nodeFixado} (.nvmrc).`);
if (pnpmEmUso !== pnpmFixado)
  problemas.push(`pnpm ${pnpmEmUso} em uso; o repositório fixa ${pnpmFixado} (packageManager).`);

if (problemas.length > 0) {
  for (const p of problemas) console.error(`ERRO: ${p}`);
  process.exit(1);
}
console.log(`OK: Node ${nodeEmUso} e pnpm ${pnpmEmUso}, iguais aos fixados.`);
