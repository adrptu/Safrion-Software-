// MAPA-FROTA F1 · regras puras de frota.js com os casos do oráculo docs/integracao/V71/mapa-frota/mapa_frota_chk.py (L1–L14, P1–P13, K1–K7, Z1–Z6)
// e as famílias de ícone (decisão 5). Uso: node frota_unit.js [caminho do frota.js]   (sai 0 com tudo OK)
'use strict';
const path = require('path');
const F = require(process.argv[2] ? path.resolve(process.argv[2]) : path.join(__dirname, 'frota.js'));
const R = []; const ok = (id, desc, c, info) => { R.push(!!c); console.log((c ? 'OK    ' : 'FALHA ') + id + ' · ' + desc + (c ? '' : ' · ' + JSON.stringify(info === undefined ? '' : info).slice(0, 400))); };
const ids = xs => xs.map(x => x.id);
const has = (recus, id, mot) => recus.some(r => r[0] === id && r[1] === mot);

// ---- L · leituras de uma fonte (base sintética no mar, latitude < −34, como o oráculo)
const BLAT = -34.629941, BLON = -47.122425, m10 = 0.0001, salto = 0.02;
const Rd = (id, obs, rec, dlat, o) => Object.assign({id, obs, rec, lat: BLAT + (dlat || 0), lon: BLON}, o || {});
const seq = [Rd('a', 0, 1), Rd('b', 10, 11, m10), Rd('c', 20, 21, 2 * m10)];
let r = F.frProcessar(seq);
ok('L1', 'sequência normal: atual = última observada; idade 5 s ≤ 60 s', r.atual.id === 'c' && JSON.stringify(F.frSituacao(r, 25, 60)) === '["Atual",5]');
r = F.frProcessar(seq.concat([Rd('b', 10, 30, m10)]));
ok('L2', 'duplicata ignorada, rastro intacto', ids(r.rastro).join() === 'a,b,c' && has(r.recus, 'b', 'duplicada'), r);
r = F.frProcessar(seq.concat([Rd('d', 15, 40, 1.5 * m10)]));
ok('L3', 'atrasada entra no rastro marcada; o marcador não volta', r.atual.id === 'c' && ids(r.rastro).join() === 'a,b,d,c' && r.rastro[2].atrasada, r);
r = F.frProcessar(seq.concat([Rd('f', 400, 30, 3 * m10)]));
ok('L4', 'futura recusada', r.atual.id === 'c' && has(r.recus, 'f', 'futura'), r);
r = F.frProcessar(seq.concat([Rd('g', 30, 31, 0, {lat: 95}), Rd('z', 31, 32, 0, {lat: 0, lon: 0})]));
ok('L5', 'inválida (95° ou 0,0) recusada', r.atual.id === 'c' && has(r.recus, 'g', 'inválida') && has(r.recus, 'z', 'inválida'), r);
r = F.frProcessar(seq);
ok('L6', 'fronteira inclusiva: 60 s Atual; 61 s Sem sinal há 1 min', JSON.stringify(F.frSituacao(r, 80, 60)) === '["Atual",60]' && F.frSituacao(r, 81, 60)[0] === 'Sem sinal há 1 min');
ok('L6b', 'idade: 1.145 s → há 19 min; 3.900 s → há 1 h 05 min', F.frIdadeTxt(1145) === 'há 19 min' && F.frIdadeTxt(3900) === 'há 1 h 05 min');
ok('L6c', 'idade abaixo de 1 min', F.frIdadeTxt(10) === 'há menos de 1 min');
ok('L7', 'nenhuma leitura: Posição indisponível', JSON.stringify(F.frSituacao(F.frProcessar([]), 100, 60)) === '["Posição indisponível",null]');
r = F.frProcessar(seq.concat([Rd('s', 30, 31, salto), Rd('t', 40, 41, salto + m10)]));
ok('L8', 'salto confirmado pela seguinte coerente', r.atual.id === 't' && ids(r.rastro).slice(-2).join() === 's,t', r);
r = F.frProcessar(seq.concat([Rd('s', 30, 31, salto), Rd('u', 40, 41, 3 * m10)]));
ok('L9', 'salto isolado descartado', r.atual.id === 'u' && has(r.recus, 's', 'salto descartado'), r);
r = F.frProcessar(seq.concat([Rd('c2', 20, 22, 5 * m10)]));
ok('L10', 'mesmo instante com outro id não troca a posição', r.atual.id === 'c' && has(r.recus, 'c2', 'mesmo instante'), r);
const s30 = Rd('s', 30, 31, salto);
let erro = ''; try { r = F.frProcessar(seq.concat([s30, Rd('t', 30, 32, salto + m10)])); } catch (e) { erro = String(e); }
ok('L11', 'mesmo instante da suspeita: sem divisão por zero; suspeita pendente', !erro && r.atual.id === 'c' && r.susp.id === 's' && has(r.recus, 't', 'mesmo instante da suspeita'), erro || r);
const L12 = seq.concat([s30, Rd('t', 25, 32, 2.5 * m10)]);
const r12 = F.frProcessar(L12);
ok('L12', 'leitura entre a aceita e a suspeita avança a aceita; s fora do rastro', r12.atual.id === 't' && r12.susp.id === 's' && ids(r12.rastro).join() === 'a,b,c,t', r12);
r = F.frProcessar(seq.concat([Rd('t', 25, 22, 2.5 * m10), s30]));
ok('L13', 'ordem de chegada invertida: mesmo estado final', r.atual.id === r12.atual.id && r.susp.id === r12.susp.id && ids(r.rastro).join() === ids(r12.rastro).join(), r);
r = F.frProcessar(L12.concat([Rd('u', 40, 41, salto + m10)]));
ok('L14', 'Δt = 10 s coerente confirma a suspeita', r.atual.id === 'u' && r.susp === null && ids(r.rastro).join() === 'a,b,c,t,s,u', r);

// ---- P · posição e estado por máquina
const pos = (f, ag) => JSON.stringify(F.frAvaliar(f, ag).posicao);
ok('P1', 'telemetria e app atuais: vale a telemetria', pos({telemetria: {obs: 100, limite: 60}, app: {obs: 100, limite: 120}}, 110) === '["telemetria","Atual"]');
ok('P2', 'telemetria velha e app atual: vale o app', pos({telemetria: {obs: 0, limite: 60}, app: {obs: 250, limite: 120}}, 300) === '["app","Atual"]');
ok('P3', 'as duas velhas: a mais recente, Sem sinal', pos({telemetria: {obs: 0, limite: 60}, app: {obs: 100, limite: 120}}, 300) === '["app","Sem sinal há 3 min"]');
ok('P4', 'desconectada sem app: Sem fonte', pos({telemetria: {obs: 0, limite: 60, conectada: false}}, 600) === '["telemetria","Sem fonte: telemetria desconectada · última há 10 min"]');
let a = F.frAvaliar({app: {obs: 0, limite: 120, online: true, estado: 'Parada · pausa desde 11:02'}}, 2400);
ok('P5', 'pausa há 40 min com o app conversando', a.estado === 'Parada · pausa desde 11:02 (app)' && JSON.stringify(a.posicao) === '["app","Última posição há 40 min · envio suspenso na pausa"]', a);
a = F.frAvaliar({app: {obs: 0, limite: 120, online: false, estado: 'Parada · pausa desde 11:02'}}, 2400);
ok('P6', 'pausa com o app sem sinal', JSON.stringify(a.posicao) === '["app","Sem sinal há 40 min"]' && a.estado === 'Última informação: Parada · pausa desde 11:02 (app) · sem sinal', a);
ok('P7', 'nenhuma fonte com leitura', pos({telemetria: {obs: null, limite: 60}}, 10) === '[null,"Posição indisponível"]');
a = F.frAvaliar({app: {obs: null, limite: 120, online: true, estado: 'Parada · pausa desde 11:02'}}, 2400);
ok('P8', 'pausa sem leitura: nada presumido', JSON.stringify(a.posicao) === '[null,"Posição indisponível"]' && a.estado === 'Parada · pausa desde 11:02 (app)', a);
ok('P9', 'desconectada com leitura de 10 s não é atual', pos({telemetria: {obs: 590, limite: 60, conectada: false}}, 600) === '["telemetria","Sem fonte: telemetria desconectada · última há menos de 1 min"]');
const pOn = pos({telemetria: {obs: 300, limite: 60, conectada: true, online: false}}, 600), pCx = pos({telemetria: {obs: 300, limite: 60, conectada: false, online: true}}, 600),
  p30 = pos({telemetria: {obs: 570, limite: 60, conectada: true, online: false}}, 600);
ok('P10', 'conectada e online são eixos distintos', pOn === '["telemetria","Sem sinal há 5 min"]' && pCx === '["telemetria","Sem fonte: telemetria desconectada · última há 5 min"]' && p30 === '["telemetria","Atual"]', [pOn, pCx, p30]);
a = F.frAvaliar({app: {obs: 590, limite: 120, revogada: true, estado: 'Trabalhando'}}, 600);
ok('P11', 'compartilhamento encerrado: dados da fonte retirados', JSON.stringify(a.posicao) === '[null,"Posição indisponível · compartilhamento encerrado"]' && a.estado === 'Desconhecido', a);
a = F.frAvaliar({}, 600, 'Impedida · ativo bloqueado');
ok('P12', 'O.S. impedida sem fonte: estado Desconhecido', a.estado === 'Desconhecido' && JSON.stringify(a.posicao) === '[null,"Posição indisponível"]', a);
a = F.frAvaliar({telemetria: {obs: 595, limite: 60, estado: 'Trabalhando'}}, 600, 'Impedida · ativo bloqueado');
ok('P13', 'leitura contradiz o impedimento: aviso, selo intacto', a.estado === 'Trabalhando (telemetria)' && a.aviso === 'Leitura contradiz o impedimento da O.S. · conferir' && JSON.stringify(a.posicao) === '["telemetria","Atual"]', a);

// ---- K · conflito por componente físico
const C = (m, i, prog, blocos) => ({maquina: m, implemento: i, prog: prog || 'alocacao', blocos: blocos || [[6, 11]]});
const EX2 = {'OS-0421': 'Em execução', 'OS-0424': 'Em execução', 'OS-0430': 'A liberar'};
const J = x => JSON.stringify(x);
ok('K1', 'PJ em duas O.S. Em execução: conflito', J(F.frConflitos({'OS-0421': C('T03', 'PJ'), 'OS-0424': C('T04', 'PJ'), 'OS-0430': C('T03', 'PJ')}, EX2, {})) === J({PJ: ['OS-0421', 'OS-0424']}));
const G1 = {G1: {ids: ['OS-0421', 'OS-0424'], maquina: 'T03', implemento: 'PJ'}};
const cjg = {'OS-0421': C('T03', 'PJ', 'grupo', [[6, 9]]), 'OS-0424': C('T04', 'PJ', 'grupo', [[9, 11]])};
ok('K2', 'mesmo PJ em dois tratores no mesmo grupo: conflito e dois marcadores', J(F.frConflitos(cjg, EX2, G1)) === J({PJ: ['OS-0421', 'OS-0424']}) && F.frMarcadores(cjg, EX2).length === 2);
ok('K3', 'A liberar não ocupa', J(F.frConflitos({'OS-0421': C('T03', 'PJ'), 'OS-0430': C('T03', 'PJ')}, {'OS-0421': 'Em execução', 'OS-0430': 'A liberar'}, {})) === '{}');
const cj4 = {'OS-0421': C('T03', 'PJ', 'grupo', [[6, 9]]), 'OS-0424': C('T03', 'PJ', 'grupo', [[9, 11]])};
ok('K4', 'mesmo conjunto, grupo, em sequência: sem conflito, um marcador', J(F.frConflitos(cj4, EX2, G1)) === '{}' && J(F.frMarcadores(cj4, EX2)) === J([['T03', 'PJ']]));
const k5 = F.frConflitos({'OS-0421': C('T03', 'PJ', 'grupo', [[6, 9]]), 'OS-0424': C('T03', 'PJ', 'alocacao', [[9, 11]])}, EX2, G1);
ok('K5', 'programação de outra fonte: conflito', J(k5) === J({T03: ['OS-0421', 'OS-0424'], PJ: ['OS-0421', 'OS-0424']}) || (J(k5.PJ) === J(['OS-0421', 'OS-0424']) && J(k5.T03) === J(['OS-0421', 'OS-0424']) && Object.keys(k5).length === 2), k5);
const k6 = F.frConflitos({'OS-0421': C('T03', 'PJ', 'grupo', [[6, 10]]), 'OS-0424': C('T03', 'PJ', 'grupo', [[9, 11]])}, EX2, G1);
ok('K6', 'blocos sobrepostos: conflito', J(k6.PJ) === J(['OS-0421', 'OS-0424']) && J(k6.T03) === J(['OS-0421', 'OS-0424']) && Object.keys(k6).length === 2, k6);
ok('K7', 'dois conjuntos distintos no mesmo grupo: dois marcadores', J(F.frMarcadores({'OS-0421': C('T03', 'PJ', 'grupo', [[6, 9]]), 'OS-0424': C('T04', 'DI', 'grupo', [[9, 11]])}, EX2)) === J([['T03', 'PJ'], ['T04', 'DI']]));

// ---- Z · pausa da animação e agrupamento
const cong = {fonte: 'simulação', obs: 1000}, corr = {fonte: 'simulação', obs: 1060};
let e = F.frExibir('ativo', cong, corr, 1065);
ok('Z1', 'modo ativo: mapa = lista', J(e.mapa) === J(e.lista));
e = F.frExibir('pausado', cong, corr, 1065);
ok('Z2', 'pausado: mapa congelado com a hora dele; lista corrente', e.mapa.hora === 1000 && e.mapa.selo === 'pausado' && e.lista.hora === 1060);
const e2 = F.frExibir('pausado', cong, corr, 1095);
ok('Z3', 'a idade da congelada continua crescendo', e.mapa.idade === 65 && e2.mapa.idade === 95);
e = F.frExibir('ativo', cong, corr, 1095);
ok('Z4', 'Retomar volta à leitura corrente', e.mapa.hora === 1060 && J(e.mapa) === J(e.lista));
const z1 = F.frExibir('pausado', cong, corr, 1095, false), z2 = F.frExibir('pausado', cong, corr, 1095, true, false);
ok('Z5', 'O.S. encerrada ou perfil revogado na pausa: sem dado, com recuperação', z1.mapa === null && z1.lista === null && /Abrir O\.S\./.test(z1.aviso) && z2.mapa === null && z2.lista === null && !!z2.aviso);
const pts = Array.from({length: 21}, (_, i) => ['m' + String(i).padStart(2, '0'), 100, 100]);
const [gs, soltos] = F.frAgrupar(pts, 'm07');
ok('Z6', '21 no mesmo ponto com foco no m07: grupo de 20 sem ele', gs.length === 1 && gs[0].length === 20 && gs[0].indexOf('m07') < 0 && J(soltos) === J(['m07']), [gs, soltos]);

// ---- I · família do ícone pela operação do catálogo (decisão 5)
const fam = t => F.frFamilia(t).familia;
ok('I1', 'famílias: pulverização, plantio, adubação, preparo, colheita, transporte, outra',
  fam('Pulverização') === 'Pulverização' && fam('Dessecação pré-plantio') === 'Pulverização' && fam('Plantio') === 'Plantio' && fam('Calagem') === 'Adubação e correção'
  && fam('Preparo do solo') === 'Preparo de solo' && fam('Colheita do café') === 'Colheita' && fam('Transporte interno') === 'Transporte' && fam('Roçada') === 'Outra'
  && F.frFamilia('Roçada').curto === 'Roçada', ['Pulverização', 'Dessecação pré-plantio', 'Plantio', 'Calagem', 'Preparo do solo', 'Colheita do café', 'Transporte interno', 'Roçada'].map(fam));

// ---- G · percurso sintético (decisão 7): passadas de 36 m com recuo de 18 m, dentro da geometria; nunca no centro sem leitura
const quad = [[-400, -300], [420, -280], [380, 310], [-390, 290]];   // convexo, em metros
const dentroPoli = (p, P) => { const sg = P.map((a, i) => { const b = P[(i + 1) % P.length]; return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]); }); return sg.every(x => x > 0) || sg.every(x => x < 0); };
const rq = F.frRotaPoligono(quad);
ok('G3', 'polígono: todos os vértices do percurso dentro e passadas a cada 36 m', rq.length > 30 && rq.every(p => dentroPoli(p, quad)) && Math.abs((rq[2][0] - rq[0][0]) - 36) < 1e-9, rq.length);
const rc = F.frRotaCirculo(488.96);
ok('G6', 'círculo (Pivô 19, raio 488,96 m): vértices dentro do círculo, com recuo de 18 m na cabeceira de cada passada (como o oráculo)', rc.length > 40 && rc.every(p => Math.hypot(p[0], p[1]) < 488.96 && Math.abs(Math.sqrt(488.96 ** 2 - p[0] ** 2) - Math.abs(p[1]) - 18) < 1e-6), rc.length);
const n0 = F.frNaRota(rq, 0), n1 = F.frNaRota(rq, 10);
ok('G7', 'posição na rota: começa no 1º vértice, anda 10 m e o rumo segue a passada', Math.abs(n0.x - rq[0][0]) < 1e-9 && Math.abs(Math.hypot(n1.x - n0.x, n1.y - n0.y) - 10) < 1e-6 && (n1.rumo === 0 || n1.rumo === 180));
const F0 = {intervalo_s: 10, demo: {'OS-0505': {componentes: [{id: 'LG01', papel: 'trator', nome: 'Trator LG-01'}, {id: 'CARLG', papel: 'implemento', nome: 'Carreta de colheita LG'}]}}};
const sim = {os: 'OS-0421', rota: rq, vel_kmh: 8, t0: 1000, lat0: -34.6, lon0: -47.1};
const ls = F.frSimular(sim, 1065, F0);
ok('S1', 'leituras simuladas a cada 10 s, a última no múltiplo de 10 anterior a agora, todas com Δt positivo', ls.length === 6 && ls[5].obs === 1060 && ls.every((x, i) => !i || x.obs - ls[i - 1].obs === 10), ls.map(x => x.obs));
const rs = F.frProcessar(ls);
ok('S2', 'a simulação a 8 km/h passa pelo contrato sem salto suspeito; posição atual = última leitura', rs.atual.id === 'OS-0421@1060' && !rs.susp && !rs.recus.length, rs.recus);
const lsCorte = F.frSimular(Object.assign({}, sim, {corte: 1005}), 1066, F0);
ok('S3', 'corte de sinal (fixture): sem leitura depois do corte; a idade cresce até "Sem sinal há 1 min" (M5)', lsCorte[lsCorte.length - 1].obs === 1000 && F.frSituacao(F.frProcessar(lsCorte), 1060, 60)[0] === 'Atual' && F.frSituacao(F.frProcessar(lsCorte), 1061, 60)[0] === 'Sem sinal há 1 min');
const col = F.frSimular({os: 'OS-0505', rota: rc, vel_kmh: 3, t0: 0, lat0: -34.6, lon0: -47.1, paradas: {anda_s: 90, para_s: 30}}, 100, F0, 3);
ok('S4', 'colheita a 3 km/h com paradas: na parada, velocidade 0, sem rumo e "Parada · carregando"', col.find(x => x.obs === 100).estado === 'Parada · carregando' && col.find(x => x.obs === 100).rumo === null && col.find(x => x.obs === 80).estado === 'Trabalhando', col);

// ---- C · conjuntos em execução (alVigente só leitura, fixture de demonstração, ativo fixo)
const T = {nome: {T03: 'Trator 03', PJ: 'Pulverizador PJ-3030 36 m', T02: 'Trator 02 MF 7719', PL: 'Plantadeira 24 linhas', T04: 'Trator 04', MAR: 'Marcos · operador', PAU: 'Paula · caldeiro', CAR: 'Carlos · operador'},
  tipo: {T03: 'Máquina', PJ: 'Implemento', T02: 'Máquina', PL: 'Implemento', T04: 'Máquina', MAR: 'Pessoa', PAU: 'Pessoa', CAR: 'Pessoa'}};
const A = [{r: 'T03', os: 'OS-0421', dia: '2026-09-26', ini: 6, fim: 12, sit: 'firme'}, {r: 'PJ', os: 'OS-0421', dia: '2026-09-26', ini: 6, fim: 12, sit: 'firme'},
  {r: 'MAR', os: 'OS-0421', dia: '2026-09-26', ini: 6, fim: 12, sit: 'firme'}, {r: 'T02', os: 'OS-0420', dia: '2026-09-26', ini: 6, fim: 16, sit: 'condicional'},
  {r: 'PL', os: 'OS-0420', dia: '2026-09-26', ini: 6, fim: 16, sit: 'condicional'}, {r: 'T04', os: 'OS-0424', dia: '2026-09-24', ini: 6, fim: 11, sit: 'firme'},
  {r: 'PJ', os: 'OS-0424', dia: '2026-09-24', ini: 6, fim: 11, sit: 'firme'}];
const ords = [{id: 'OS-0421', tal: ['T1', 'T2'], tipo: 'Pulverização · Fungicida 1ª aplicação', fase: 'Em execução', selos: []},
  {id: 'OS-0420', tal: ['T4'], tipo: 'Plantio · Soja 58 W', fase: 'Em execução', selos: [['Impedida · ativo bloqueado', 'red']]},
  {id: 'OS-0505', tal: ['PV19'], tipo: 'Colheita · semana 39', fase: 'Em execução', selos: []},
  {id: 'OS-0506', tal: ['PV4'], tipo: 'Fertirrigação NK', fase: 'Em execução', selos: []},
  {id: 'OS-0424', tal: ['T1-B'], tipo: 'Pulverização · Fungicida A', fase: 'Liberadas', selos: []}];
let cjs = F.frConjuntos(ords, {ordens: {}}, A, '2026-09-26', T, F0);
const por = id => cjs.find(x => x.os === id);
ok('C1', 'só Em execução entra; OS-0421 = Trator 03 + PJ-3030 pela programação, com o operador; OS-0420 condicional',
  cjs.map(x => x.os).join() === 'OS-0421,OS-0420,OS-0505,OS-0506' && por('OS-0421').vinculo === 'programacao' && por('OS-0421').maquina === 'T03' && por('OS-0421').implemento === 'PJ'
  && por('OS-0421').pessoas[0].nome === 'Marcos' && por('OS-0420').condicional === true, cjs.map(x => [x.os, x.vinculo, x.maquina, x.implemento]));
ok('C2', 'Lagoa Grande: OS-0505 com o conjunto de demonstração; OS-0506 (fertirrigação) é ativo fixo, sem conjunto móvel',
  por('OS-0505').vinculo === 'fixture' && por('OS-0505').maquina === 'LG01' && por('OS-0505').implemento === 'CARLG' && por('OS-0506').fixo === true && !por('OS-0506').vinculo);
const ords2 = ords.map(o => o.id === 'OS-0424' ? Object.assign({}, o, {fase: 'Em execução'}) : o);
cjs = F.frConjuntos(ords2, {ordens: {}}, A, '2026-09-26', T, F0);
const K = F.frConflitosDe(cjs, {}, T);
ok('C3', 'iniciar a OS-0424 (programada em 24/09 com o PJ): o PJ fica nas duas e as duas mostram o conflito (M8)',
  (K['OS-0421'] || []).some(x => x.ativo === 'PJ' && x.com.join() === 'OS-0424') && (K['OS-0424'] || []).some(x => x.ativo === 'PJ' && x.com.join() === 'OS-0421'), K);

console.log('RESULTADO: ' + R.filter(Boolean).length + '/' + R.length + ' ok');
process.exit(R.every(Boolean) ? 0 : 1);
