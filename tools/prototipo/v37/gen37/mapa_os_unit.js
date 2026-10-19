// Mapa › Ordens de serviço: ordem Cancelada fora das abertas (revisão do Codex 6216014054 no MAPA-9). Sem navegador:
// node mapa_os_unit.js  — extrai de areas/inicio.py as funções reais osAb … osStrip e roda com dados sintéticos.
// MAPA_INICIO=<arquivo> roda contra outra versão do inicio.py (a anterior, para ver o vermelho).
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(process.env.MAPA_INICIO || path.join(__dirname, 'areas', 'inicio.py'), 'utf8');
const i = src.indexOf('function osAb('), j = src.indexOf('function osFonte(');
if (i < 0 || j < 0) { console.log('FALHOU extração (osAb … osFonte)'); process.exit(1); }
let ORDS = [];
const F = new Function('ordsOf', 'nfx', 'worstC', 'PZC', 'FASES', src.slice(i, j) + '\nreturn {osCls, osStrip, osAb};')(
  () => ORDS, (x, d) => Number(x).toFixed(d || 0), (cs) => cs[0], {}, ['A liberar', 'Liberadas', 'Em execução', 'Em conferência', 'Encerradas']);
const O = (id, fase, area, rz) => ({ id, fase, area, rz, selos: [], pz: '', saldo: area - rz });
let ok = 0, falhas = 0;
const chk = (n, c, x) => { if (c) { ok++; console.log('OK  ', n); } else { falhas++; console.log('FALHOU', n, '·', JSON.stringify(x)); } };
const av = (os) => { ORDS = os; return F.osCls('T', { ver: 'Avanço', fase: 'Todas' }); };
const im = (os) => { ORDS = os; return F.osCls('T', { ver: 'Impedimentos', fase: 'Todas' }); };
const st = (os) => F.osStrip({ ver: 'Avanço', fase: 'Todas' }, os).find(n => n.k === 'Avanço').val;
let r = av([O('OS-1', 'Em execução', 100, 30)]);
chk('M1 aberta 100 ha com 30 apontados: 30/100 ha · 30 %', /30\/100 ha · 30 %/.test(r.l), r);
r = av([O('OS-1', 'Em execução', 100, 30), O('OS-2', 'Canceladas', 100, 0)]);
chk('M2 aberta + cancelada de 100 ha: continua 30/100 ha · 30 % (a cancelada não entra)', /30\/100 ha · 30 %/.test(r.l) && !/ordens/.test(r.l), r);
const s2 = st([O('OS-1', 'Em execução', 100, 30), O('OS-2', 'Canceladas', 100, 0)]);
chk('M3 faixa de números do Avanço com a cancelada: 30 % (não 15 %)', s2 === '30 %', s2);
r = av([O('OS-2', 'Canceladas', 100, 0)]);
chk('M4 só cancelada: sem ordem aberta, rótulo "cancelada" (nunca 0/100 ha nem "não iniciada")', r.c === 'none' && r.l === 'cancelada', r);
r = av([O('OS-1', 'Em execução', 100, 30), O('OS-3', 'Encerradas', 80, 80)]);
chk('M5 controle: aberta + encerrada mantém 30 %', /30\/100 ha · 30 %/.test(r.l), r);
r = av([O('OS-3', 'Encerradas', 80, 80)]);
chk('M6 controle: só encerrada segue "encerrada"', r.c === 'none' && r.l === 'encerrada', r);
r = im([O('OS-2', 'Canceladas', 100, 0)]);
chk('M7 Impedimentos com só cancelada: "cancelada", sem ordem aberta', r.c === 'none' && r.l === 'cancelada', r);
console.log(`TOTAL ${ok + falhas} · OK ${ok} · FALHAS ${falhas}`);
process.exit(falhas ? 1 : 0);
