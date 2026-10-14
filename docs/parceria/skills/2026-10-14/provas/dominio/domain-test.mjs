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
const absolute = { ...api.escalaAbsoluta };
for (const [v, expected] of [
  [0.299, 1],
  [0.3, 2],
  [0.449, 2],
  [0.45, 3],
  [0.46, 3],
  [0.6, 4],
  [0.72, 5],
  [0.82, 6],
  [1, 6],
]) {
  check(`classe absoluta ${v} → ${expected}`, api.classeDoIndice(v, absolute)?.id === expected);
}
const relative = api.escalaRelativa(new Float32Array([0.4, 0.5, 0.6, 0.7, 0.8, 0.9]));
check('relativa usa cortes da escala, não limites absolutos', api.classeDoIndice(0.46, relative)?.id === 1);
const valid = { diasDesdeCena: 1, nuvemPct: 0, areaFracaPct: 0, quedaPct: 0, maiorManchaNovaHa: 0 };
for (const key of Object.keys(valid))
  for (const bad of [NaN, Infinity, null]) {
    const state = api.estadoTalhao({ ...valid, [key]: bad });
    check(`${key} indisponível não é Normal`, state.estado !== 'Normal');
  }
check('válido mantém Normal', api.estadoTalhao(valid).estado === 'Normal');
check(
  'sem imagem precede outros estados',
  api.estadoTalhao({ ...valid, diasDesdeCena: null, nuvemPct: 90 }).estado === 'Sem imagem',
);
check(
  'nuvem precede estatística ausente',
  api.estadoTalhao({ ...valid, nuvemPct: 90, areaFracaPct: NaN }).estado === 'Nuvem',
);
check('crítico preservado', api.estadoTalhao({ ...valid, areaFracaPct: 20 }).estado === 'Crítico');
check('atenção preservada', api.estadoTalhao({ ...valid, quedaPct: 12 }).estado === 'Atenção');
const expressions = [...agr.matchAll(/`(P_(?:limpo|corrigido)_kg) = ([^`]+)`/g)];
function peso(bruto, imp, atual, padrao) {
  const values = { P_bruto_kg: bruto, I_pct: imp, U_atual_pct: atual, U_padrao_pct: padrao };
  for (const [, key, expression] of expressions)
    values[key] = vm.runInNewContext(expression.replaceAll('×', '*').replaceAll('−', '-'), values);
  return values.P_corrigido_kg;
}
check(
  '1000kg,2%impureza,20→14%umidade = 911,6279kg',
  Math.abs(peso(1000, 2, 20, 14) - 911.6279069767442) < 1e-8,
);
check('impureza zero e mesma umidade preservam massa', peso(1000, 0, 14, 14) === 1000);

console.log(`${n - fail}/${n}`);
process.exitCode = fail ? 1 : 0;
