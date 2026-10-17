// CTL-4 S3 · Mapa › Insumos ignorava a dose atual (achado do Codex 6232261452, 17/10/2026): o cache de insFaz (areas/inicio.py) não
// invalidava quando só as ocorrências do plano (X.occ: dose, área, produtos) mudavam, com as mesmas ordens e o mesmo estoque.
// Teste de unidade, sem navegador: extrai insFaz do gerador e troca cal01/cenário por dublês que contam a dose.
//   C1 dose 1 → necessidade 1 × área; C2 a dose muda para 2 (mesmas O.S. e mesmo estoque) → a necessidade acompanha (2 × área);
//   C3 nada muda → o cache devolve o mesmo objeto (sem refazer a conta); C4 a O.S. muda → refaz (o que já valia continua valendo).
// Uso: node mapa_insfaz_unit.js [caminho do inicio.py]   (padrão: areas/inicio.py; contraprova: o inicio.py da base 0b3d0d4 reprova C2)
'use strict';
const fs = require('fs'), path = require('path');
const arq = process.argv[2] || path.join(__dirname, 'areas', 'inicio.py');
const src = fs.readFileSync(arq, 'utf8');
const a = src.indexOf('function insFaz(){'), b = src.indexOf('insFaz._k=k; insFaz._v=v; return v; }', a);
if (a < 0 || b < 0) throw new Error('insFaz não encontrada em ' + arq);
const corpo = src.slice(a, b + 'insFaz._k=k; insFaz._v=v; return v; }'.length);
// dublês: occ com uma ocorrência (T1, Ureia, dose × área); demFazenda soma dose × área por produto; a situação só repete a necessidade
const amb = { dose: 1, osd: [{ id: 'OS-1' }], contaFeita: 0 };
const M = { dem: { faz: { S1: { occ: null, areaT: {}, hoje: '2026-09-23', viavel: true } }, b: {}, tid: { T1: 'T1' } }, lim30: '2026-10-23' };
const cenGet = () => ({});
const cenDemEntradas = (c, F) => Object.assign({}, F, { occ: [{ k: 'T1|a1', local: 'T1', area: 10, prods: [{ nome: 'Ureia', dose: amb.dose, q: amb.dose * 10 }] }],
  osd: amb.osd, fisico: { Ureia: 0 }, reservas: {}, recebDt: {}, sobra: {}, quar: {}, quarRep: {} });
const demFazenda = (X) => { amb.contaFeita++; const m = {}; X.occ.forEach(o => o.prods.forEach(p => { m[p.nome] = (m[p.nome] || 0) + p.dose * o.area; })); return m; };
const demPorLocal = (m) => ({ T1: Object.keys(m).map(p => ({ p, q: m[p] })) });
const demSituacao = (m) => Object.fromEntries(Object.keys(m).map(p => [p, ['ok', 'ok', String(m[p])]]));
const demTal = (t) => t; const safK = () => 'S1';
const insFaz = new Function('M', 'cenGet', 'cenDemEntradas', 'demFazenda', 'demPorLocal', 'demSituacao', 'demTal', 'safK', corpo + '\nreturn insFaz;')(
  M, cenGet, cenDemEntradas, demFazenda, demPorLocal, demSituacao, demTal, safK);
let ok = 0, falha = 0;
const chk = (n, c, info) => { if (c) { ok++; console.log('OK    ' + n); } else { falha++; console.log('FALHA ' + n + ' · ' + JSON.stringify(info)); } };
const q = (v) => ((v.nec.T1 || [])[0] || {}).q;
const v1 = insFaz(); chk('C1 dose 1 × 10 ha: necessidade de 10 de Ureia no T1', q(v1) === 10, q(v1));
amb.dose = 2; const v2 = insFaz(); chk('C2 dose 2 com as mesmas O.S. e o mesmo estoque: a necessidade passa a 20 (o cache não segura a dose antiga)', q(v2) === 20, q(v2));
const n0 = amb.contaFeita; const v3 = insFaz(); chk('C3 nada mudou: o cache devolve a mesma conta, sem refazer', v3 === v2 && amb.contaFeita === n0, [v3 === v2, amb.contaFeita, n0]);
amb.osd = [{ id: 'OS-1' }, { id: 'OS-2' }]; insFaz(); chk('C4 a O.S. mudou: a conta é refeita', amb.contaFeita === n0 + 1, amb.contaFeita);
console.log('\nTOTAL ok ' + ok + ' · falha ' + falha + ' · fonte: ' + path.relative(process.cwd(), arq));
process.exit(falha ? 1 : 0);
