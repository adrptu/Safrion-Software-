// Fronteiras entre pacotes (ENG-012), sem dependência nova: usa o analisador de imports do próprio TypeScript.
// Falha quando: um pacote importa outro pacote que não declarou no package.json; um import relativo sai do src do
// pacote ou aponta para arquivo inexistente; há ciclo de imports dentro de um pacote.
// Uso: node tools/dev/fronteiras.mjs [raiz]
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { builtinModules } from 'node:module';
import { dirname, join, relative, resolve, sep } from 'node:path';

import ts from 'typescript';

const raiz = resolve(process.argv[2] ?? '.');
const pastaPacotes = join(raiz, 'packages');
const problemas = [];
const rel = (p) => relative(raiz, p);

function fontes(dir) {
  return readdirSync(dir).flatMap((nome) => {
    const p = join(dir, nome);
    if (statSync(p).isDirectory()) return fontes(p);
    return /\.(ts|mts|cts)$/.test(nome) && !nome.endsWith('.d.ts') ? [p] : [];
  });
}

function resolverRelativo(arquivo, especificador) {
  const alvo = resolve(dirname(arquivo), especificador);
  const candidatos = [
    alvo,
    alvo.replace(/\.js$/, '.ts'),
    alvo.replace(/\.mjs$/, '.mts'),
    alvo.replace(/\.cjs$/, '.cts'),
  ];
  return candidatos.find((c) => existsSync(c) && statSync(c).isFile()) ?? null;
}

function ciclos(grafo) {
  const cor = new Map();
  const achados = new Set();
  const pilha = [];
  const visitar = (no) => {
    cor.set(no, 'cinza');
    pilha.push(no);
    for (const prox of grafo.get(no) ?? []) {
      if (cor.get(prox) === 'cinza') {
        const ciclo = pilha.slice(pilha.indexOf(prox)).concat(prox);
        achados.add(ciclo.map(rel).join(' → '));
      } else if (!cor.has(prox)) {
        visitar(prox);
      }
    }
    pilha.pop();
    cor.set(no, 'preto');
  };
  for (const no of grafo.keys()) if (!cor.has(no)) visitar(no);
  return [...achados];
}

for (const nome of existsSync(pastaPacotes) ? readdirSync(pastaPacotes) : []) {
  const pacote = join(pastaPacotes, nome);
  const src = join(pacote, 'src');
  if (!existsSync(src)) continue;
  const manifesto = JSON.parse(readFileSync(join(pacote, 'package.json'), 'utf8'));
  const declarados = new Set([
    ...Object.keys(manifesto.dependencies ?? {}),
    ...Object.keys(manifesto.peerDependencies ?? {}),
  ]);
  const grafo = new Map();
  for (const arquivo of fontes(src)) {
    const { importedFiles } = ts.preProcessFile(readFileSync(arquivo, 'utf8'), true, true);
    const arestas = [];
    for (const { fileName: especificador } of importedFiles) {
      if (especificador.startsWith('.')) {
        const alvo = resolverRelativo(arquivo, especificador);
        if (!alvo)
          problemas.push(`${rel(arquivo)}: import "${especificador}" aponta para arquivo inexistente`);
        else if (!alvo.startsWith(src + sep))
          problemas.push(`${rel(arquivo)}: import "${especificador}" sai de ${rel(src)}`);
        else arestas.push(alvo);
        continue;
      }
      const base = especificador.startsWith('@')
        ? especificador.split('/').slice(0, 2).join('/')
        : especificador.split('/')[0];
      if (especificador.startsWith('node:') || builtinModules.includes(base)) continue;
      if (!declarados.has(base)) {
        problemas.push(
          `${rel(arquivo)}: "${base}" não está declarado em ${rel(join(pacote, 'package.json'))}`,
        );
      }
    }
    grafo.set(arquivo, arestas);
  }
  for (const c of ciclos(grafo)) problemas.push(`ciclo de imports: ${c}`);
}

if (problemas.length > 0) {
  for (const p of problemas) console.error(`ERRO ENG-012: ${p}`);
  process.exit(1);
}
console.log('OK: fronteiras entre pacotes sem ciclo e sem dependência não declarada.');
