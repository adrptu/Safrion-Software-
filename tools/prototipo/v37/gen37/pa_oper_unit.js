// PA-OPER F1 · regras puras de operacoes.js com os oráculos de docs/integracao/V71/PA-OPER.md (P1, P3, P4, P7, P12, P18 e a propriedade das cargas).
// Valores sintéticos ou de demonstração, como aritmética de teste. Uso: node pa_oper_unit.js [caminho do operacoes.js]   (sai 0 com tudo OK)
'use strict';
const path = require('path');
const O = require(process.argv[2] ? path.resolve(process.argv[2]) : path.join(__dirname, 'operacoes.js'));
const R = []; const ok = (id, desc, c, info) => { R.push(!!c); console.log((c ? 'OK    ' : 'FALHA ') + id + ' · ' + desc + (c ? '' : ' · ' + JSON.stringify(info === undefined ? '' : info).slice(0, 400))); };
const perto = (a, b) => Math.abs(a - b) < 1e-9 * Math.max(1, Math.abs(b));

// ---- P1 · seções na ordem do ciclo (SOJA-AT de dados2.py: DAP −20, −1, 0, 20, 118; contagens 4/1/1/1/1)
const SOJA = [
  {id: 'a1', op: 'Pulverização', dap: -20}, {id: 'a2', op: 'Tratamento de sementes', dap: -1}, {id: 'a3', op: 'Plantio', dap: 0},
  {id: 'a4', op: 'Adubação a lanço', dap: 20}, {id: 'a5', op: 'Pulverização', dap: 25}, {id: 'a6', op: 'Pulverização', dap: 45},
  {id: 'a7', op: 'Pulverização', dap: 70}, {id: 'a8', op: 'Colheita de grãos', dap: 118}];
let s = O.opSecoes(SOJA);
ok('P1', 'ordem do ciclo e contagens 4/1/1/1/1', s.map(x => x.op + ':' + x.atividades.length).join() === 'Pulverização:4,Tratamento de sementes:1,Plantio:1,Adubação a lanço:1,Colheita de grãos:1', s.map(x => x.op));
ok('P1b', 'famílias da migração', s.map(x => x.familia).join() === 'pulverizacao,ts,plantio,adubacao,colheita', s.map(x => x.familia));
ok('P1c', 'chave do endereço sem acento', O.opChave('Pulverização') === 'pulverizacao' && O.opChave('Tratamento de sementes') === 'tratamento-de-sementes');
ok('P1d', 'operação desconhecida exige família (null)', O.opFamilia('Outra coisa') === null);
s = O.opSecoes([{id: 'x', op: 'B', dap: 5}, {id: 'y', op: 'A', dap: 5}], op => ({A: 2, B: 1})[op]);
ok('P1e', 'empate de início resolvido pela fase do CD-08', s.map(x => x.op).join() === 'B,A');

// ---- P3 · herança e valor próprio
const pul = O.opSecoes(SOJA)[0];
pul.atividades.forEach(a => { a.nome = a.id; a.alvo = 'ferrugem'; });
pul.atividades[2].calda = 150;                                         // Fungicida 2ª com valor próprio
const p100 = {calda: 100}, p120 = {calda: 120};
ok('P3a', 'herdeiras mostram 120 "da operação"; a própria mantém 150',
  pul.atividades.map(a => O.opParam(a, p120, 'calda')).map(x => x.valor + '/' + x.origem).join() === '120/da operação,120/da operação,150/própria,120/da operação');
ok('P3b', 'alteração do rascunho em texto', O.opAlteracaoParam(pul, p100, p120, 'calda', 'volume de calda', 'L/ha') === 'Pulverização · volume de calda 100 → 120 L/ha em 3 atividades',
  O.opAlteracaoParam(pul, p100, p120, 'calda', 'volume de calda', 'L/ha'));
ok('P3c', 'sem valor na operação nem próprio: pendente, nenhum padrão', O.opParam({}, {}, 'calda').valor === null && O.opParam({}, {}, 'calda').origem === 'pendente');

// ---- P4 · cargas (EX-38 R1)
let c = O.opCargas(160, 100, 3000, [{id: 'fa', nome: 'Fungicida A', un: 'L', doseHa: 0.5}]);
ok('P4a', 'OS-0421 com tanque de 3.000 L: 6 cargas (5 de 30 ha + 1 de 10 ha), 15 L e 5 L, total 80 L e 16.000 L',
  c.cargas.length === 6 && c.cargas.slice(0, 5).every(x => perto(x.areaHa, 30) && perto(x.produtos[0].qtd, 15)) && perto(c.cargas[5].areaHa, 10) && perto(c.cargas[5].produtos[0].qtd, 5)
  && perto(c.total.produtos[0].qtd, 80) && perto(c.total.caldaL, 16000), c.cargas.map(x => [x.areaHa, x.produtos[0].qtd]));
c = O.opCargas(160, 100, 2500, [{id: 'fa', nome: 'Fungicida A', un: 'L', doseHa: 0.5}]);
ok('P4b', 'tanque de 2.500 L: 7 cargas (6 de 25 ha + 1 de 10 ha), 12,5 L e 5 L',
  c.cargas.length === 7 && c.cargas.slice(0, 6).every(x => perto(x.areaHa, 25) && perto(x.produtos[0].qtd, 12.5)) && perto(c.cargas[6].areaHa, 10) && perto(c.cargas[6].produtos[0].qtd, 5), c.cargas.map(x => [x.areaHa, x.produtos[0].qtd]));
c = O.opCargas(12, 100, 500, [{id: 'p', nome: 'P', un: 'L', doseHa: 2}]);
ok('P4c', 'unidade 41.5: 500 + 500 + 200 L, 5 + 5 + 2 ha, 10 + 10 + 4 L, total 24 L (mutante "última cheia" daria 30 L)',
  c.cargas.map(x => x.caldaL).join() === '500,500,200' && c.cargas.map(x => x.areaHa).join() === '5,5,2' && c.cargas.map(x => x.produtos[0].qtd).join() === '10,10,4' && perto(c.total.produtos[0].qtd, 24), c.cargas);
ok('P4d', 'sem volume de calda: não gera cargas', O.opCargas(160, null, 3000, []).estado === 'sem volume de calda' && O.opCargas(160, null, 3000, []).cargas.length === 0);
ok('P4e', 'área exata múltipla do tanque: sem carga vazia', O.opCargas(90, 100, 3000, []).cargas.length === 3);

// ---- P18 · vazão alvo × disponível
ok('P18a', '100 L/ha, 0,5 m, 6 km/h → 0,5 L/min; 12 km/h → 1,0 L/min', perto(O.opVazaoAlvo(100, 6, 0.5), 0.5) && perto(O.opVazaoAlvo(100, 12, 0.5), 1.0));
ok('P18b', 'sem velocidade: desconhecido (mutante com velocidade padrão reprova)', O.opVazaoAlvo(100, null, 0.5) === null && O.opVazaoAlvo(100, undefined, 0.5) === null);
const CURVA = {'leque 110-02': [{bar: 3, lmin: 0.8}]};
let v = O.opVazao(100, 6, 0.5, CURVA, 'leque 110-02', 3);
ok('P18c', 'disponível da curva ponta × pressão e diferença em %', v.alvo === 0.5 && v.disp === 0.8 && perto(v.difPct, 60), v);
v = O.opVazao(100, 6, 0.5, null, 'leque 110-02', 3);
ok('P18d', 'sem curva: disponível desconhecido, sem diferença', v.disp === null && v.difPct === null);

// ---- P7 · bula na versão (base de demonstração, no formato da AG-07: cultura × alvo)
const BULA = {'Fungicida A': {grupos: ['FRAC 3', 'FRAC 11'], usos: {Soja: {'ferrugem-asiática': {dmax: 0.5, un: 'L/ha', car: 30, mx: 2}, 'mancha-alvo': {dmax: 0.4, un: 'L/ha', car: 30, mx: 2}}}},
              'Fungicida B': {grupos: ['FRAC 3'], usos: {Soja: {'ferrugem-asiática': {dmax: 1, un: 'L/ha', car: 14, mx: 3}}}},
              'Acaricida': {grupos: ['IRAC 6'], usos: {Soja: {'ácaro': {dmax: 60, un: 'mL/100 L', car: 7, mx: 2, porCalda: true}}}},
              'Óleo mineral': {grupos: [], usos: {}}};
const at = (id, t, prods, o) => Object.assign({id, nome: id, t, alvo: 'ferrugem-asiática', produtos: prods}, o || {});
const fa = d => ({prod: 'Fungicida A', dose: d === undefined ? 0.5 : d, un: 'L'});
const ctx = {cultura: 'Soja', colheitaT: 118, params: p100};
let conf = O.opBula([at('f1', 100, [fa()])], BULA, ctx);
ok('P7a', 'carência de 30 dias na DAP 100 com colheita na 118 → ⛔ 12 dias depois', conf.some(x => x.nivel === 'impede' && x.motivo.includes('carência termina 12 dias depois da colheita prevista')), conf);
conf = O.opBula([at('f1', 85, [fa()])], BULA, ctx);
ok('P7b', 'na DAP 85 a carência cabe', !conf.some(x => x.nivel === 'impede'), conf);
conf = O.opBula([at('f1', 30, [fa()]), at('f2', 50, [fa()]), at('f3', 70, [fa()])], BULA, ctx);
ok('P7c', 'terceira aplicação com máximo 2 → ⛔', conf.filter(x => x.nivel === 'impede').map(x => x.ativ).join() === 'f3', conf);
conf = O.opBula([at('f1', 30, [fa(0.6)])], BULA, ctx);
ok('P7d', 'dose acima da bula → ⛔', conf.some(x => x.nivel === 'impede' && x.motivo.includes('acima da bula')), conf);
conf = O.opBula([at('f1', 30, [fa()], {calda: 250})], {'Fungicida A': {grupos: ['FRAC 3'], usos: {Soja: {'ferrugem-asiática': {dmax: 0.5, un: 'L/ha', car: 30, mx: 2, volMin: 80, volMax: 200}}}}}, ctx);
ok('P7e', 'volume fora da faixa da bula (quando definida) → ⛔', conf.some(x => x.nivel === 'impede' && x.motivo.includes('fora da faixa da bula')), conf);
conf = O.opBula([at('f1', 30, [fa()]), at('f2', 50, [{prod: 'Fungicida B', dose: 0.5, un: 'L'}])], BULA, ctx);
ok('P7f', 'mesmo grupo FRAC em sequência → só ⚠', conf.length === 1 && conf[0].nivel === 'aviso' && conf[0].ativ === 'f2', conf);
conf = O.opBula([at('f1', 30, [fa()], {alvo: 'percevejo'})], BULA, ctx);
ok('P7g', 'sem registro para cultura × alvo → ⛔', conf.some(x => x.nivel === 'impede' && x.motivo.includes('sem registro para Soja × percevejo')), conf);
conf = O.opBula([at('f1', 30, [fa()])], BULA, {cultura: 'Milho', colheitaT: 140, params: p100});
ok('P7h', 'sem registro para a cultura → ⛔', conf.some(x => x.nivel === 'impede' && x.motivo.includes('sem registro para Milho')), conf);
conf = O.opBula([at('f1', 30, [fa(0.45)], {alvo: ''})], BULA, ctx);
ok('P7i', 'sem alvo, 0,45 L/ha cabe em algum uso (o mais permissivo, 0,5) → sem ⛔', !conf.some(x => x.nivel === 'impede'), conf);
conf = O.opBula([at('f1', 30, [fa(0.45)], {alvo: 'mancha-alvo'})], BULA, ctx);
ok('P7j', 'com alvo mancha-alvo, 0,45 > 0,4 → ⛔', conf.some(x => x.nivel === 'impede' && x.motivo.includes('acima da bula')), conf);
conf = O.opBula([at('f1', 30, [{prod: 'Acaricida', dose: 0.07, un: 'L'}], {alvo: 'ácaro'})], {Acaricida: {grupos: ['IRAC 6'], usos: {Soja: {'ácaro': {dmax: 0.06, un: 'L/100 L', car: 7, mx: 2, porCalda: true}}}}}, ctx);
ok('P7k', 'dose por 100 L vira dose/ha pela calda (0,06 × 100/100 = 0,06 L/ha < 0,07) → ⛔', conf.some(x => x.nivel === 'impede' && x.motivo.includes('acima da bula')), conf);
conf = O.opBula([at('f1', 30, [{prod: 'Óleo mineral', dose: 0.5, un: 'L'}])], BULA, ctx);
ok('P7l', 'adjuvante sem modo de ação não é conferido', conf.length === 0, conf);

// ---- estados (decisão 5)
ok('E1', 'pendência sem impedimento → Pendente', O.opEstado([{}], []).cod === 'pendente');
ok('E2', 'impedimento vence pendência → Impedida', O.opEstado([{}], [{nivel: 'impede'}]).cod === 'impedida');
ok('E3', 'só aviso → Com aviso; nada → Pronta', O.opEstado([], [{nivel: 'aviso'}]).cod === 'aviso' && O.opEstado([], []).cod === 'pronta');
ok('E4', 'pendências da Pulverização: calda e alvo', O.opPendencias({familia: 'pulverizacao', atividades: [{id: 'q', nome: 'Q'}]}, {}).map(x => x.campo).join() === 'calda,alvo');

// ---- P12 · publicação explícita e idempotente
let pl = {versoes: [{v: 6, estado: 'publicada', por: 'Ana', em: '12/08/2026'}]};
let r = O.opPublicar(pl, {tipo: 'publicar', podePublicar: true, por: 'Ana', em: '16/10/2026', chave: 'k1'});
ok('P12a', 'Ana publica v7', r.v === 7 && r.plano.versoes.some(x => x.v === 7 && x.estado === 'publicada' && x.por === 'Ana'));
ok('P12b', 'mesma chave não cria v8', O.opPublicar(r.plano, {tipo: 'publicar', podePublicar: true, por: 'Ana', em: '16/10/2026', chave: 'k1'}).repetido === true);
r = O.opPublicar(pl, {tipo: 'publicar', podePublicar: false, por: 'Caio', chave: 'k2'});
ok('P12c', 'Caio sem o papel não publica', !!r.erro && r.plano === pl);
r = O.opPublicar(pl, {tipo: 'submeter', por: 'Caio', chave: 'k3'});
ok('P12d', 'Caio submete: v7 em revisão, v6 segue vigente', r.v === 7 && r.plano.versoes.some(x => x.v === 7 && x.estado === 'em revisão') && r.plano.versoes.some(x => x.v === 6 && x.estado === 'publicada'));
const r2 = O.opPublicar(r.plano, {tipo: 'publicar', podePublicar: true, por: 'Ana', chave: 'k4'});
ok('P12e', 'Ana publica a v7 em revisão (não pula para v8)', r2.v === 7 && r2.plano.versoes.filter(x => x.v === 7).length === 1 && r2.plano.versoes.find(x => x.v === 7).estado === 'publicada');
ok('P12f', 'impedimento recusa publicar', !!O.opPublicar(pl, {tipo: 'publicar', podePublicar: true, impedimentos: [{motivo: 'x'}], chave: 'k5'}).erro);

// ---- propriedade: 1.000 casos com semente fixa
let semente = 20261019; const rnd = () => (semente = (semente * 1103515245 + 12345) % 2147483648) / 2147483648;
let falhas = 0;
for (let i = 0; i < 1000; i++) {
  const area = Math.round((0.5 + rnd() * 400) * 100) / 100, vol = [50, 80, 100, 120, 150, 200][Math.floor(rnd() * 6)], tq = [500, 600, 2000, 2500, 3000][Math.floor(rnd() * 5)];
  const dose = Math.round(rnd() * 300) / 100;
  const k = O.opCargas(area, vol, tq, [{id: 'p', doseHa: dose || 0.01}]);
  const soma = k.cargas.reduce((a, x) => a + x.caldaL, 0), prod = k.cargas.reduce((a, x) => a + x.produtos[0].qtd, 0);
  if (!perto(soma, area * vol) || !perto(prod, (dose || 0.01) * area) || k.cargas.some(x => x.caldaL > tq + 1e-6) || k.cargas.some(x => !(x.areaHa > 0))) falhas++;
}
ok('PROP', '1.000 casos: Σ calda = área × volume, Σ produto = dose × área, nenhuma carga passa do tanque nem fica vazia', falhas === 0, falhas);

const n = R.filter(Boolean).length; console.log(`\n${n}/${R.length} OK`); process.exit(n === R.length ? 0 : 1);
