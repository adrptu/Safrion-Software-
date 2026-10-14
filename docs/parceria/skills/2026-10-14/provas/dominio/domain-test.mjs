import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import ts from 'typescript';
import { fileURLToPath } from 'node:url';
const root = process.argv[2] || path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const doc = fs.readFileSync(
  path.join(root, 'shared/indicadores-satelite/assets/referencia-implementacao.md'),
  'utf8',
);
const code = [...doc.matchAll(/```ts\n([\s\S]*?)```/g)].map((m) => m[1]).join('\n');
const ctx = { exports: {} };
vm.createContext(ctx);
vm.runInContext(
  ts.transpileModule(code, { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText,
  ctx,
);
const api = ctx.exports;
const attempt = (fn) => {
  try {
    return fn();
  } catch {
    return undefined;
  }
};
let fail = 0,
  n = 0;
const check = (name, value) => {
  n++;
  if (!value) fail++;
  console.log((value ? 'PASS ' : 'FAIL ') + name);
};
const agr = fs.readFileSync(path.join(root, 'shared/agro-gestao-conhecimento/assets/agronomia.md'), 'utf8');
const numerator = Number(agr.match(/plantas\/ha = \(([\d ]+)/)[1].replaceAll(' ', ''));
check('10 plantas/m a 0,5m = 200000 plantas/ha', (numerator / 0.5) * 10 === 200000);
check('espaçamento 1m, 5 plantas/m = 50000/ha', numerator * 5 === 50000);
for (const [name, values] of [
  ['vazio', []],
  ['nodata', [NaN, Infinity]],
  ['único', [0.5, NaN]],
]) {
  const v = new Float32Array(values),
    scale = api.escalaRelativa(v),
    st = api.estatisticas(v);
  check(name + ': sem escala', scale === null);
  check(name + ': sem estatística', st === null);
  check(name + ': cor sem dado', attempt(() => api.corDoIndice(0.5, scale)) === '#9E9E9E');
  check(name + ': sem classe', api.classeDoIndice(0.5, scale) === null);
  check(name + ': máscara desconhecida', attempt(() => api.mascaraFraco(v, st)) === null);
}
let s = api.escalaRelativa(new Float32Array([0.5, 0.5, 0.5]));
check('uniforme tem escala finita não degenerada', s && Number.isFinite(s.min) && s.max > s.min);
check(
  'mínimo operacional configurado respeitado',
  api.escalaRelativa(new Float32Array([0.2, 0.5, 0.8]), undefined, 4) === null,
);
const st = api.estatisticas(new Float32Array([0.2, 0.4, 0.6]));
check('amostra válida mantém média', st && Math.abs(st.media - 0.4) < 1e-6);
const mask = api.mascaraFraco(new Float32Array([NaN, 0, 0.5]), { media: 0.5, dp: 0.1, p10: 0.2 });
check(
  'máscara é Uint8Array, ignora nodata',
  Object.prototype.toString.call(mask) === '[object Uint8Array]' && mask[0] === 0 && mask[1] === 1,
);
check('escala inválida não classifica', api.classeDoIndice(0.5, { min: NaN, max: 1 }) === null);
console.log(`${n - fail}/${n}`);
process.exitCode = fail ? 1 : 0;
