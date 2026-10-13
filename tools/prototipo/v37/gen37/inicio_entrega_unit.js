// FRENTE B · início com entrega parcial (PRD 42.2 l.7067; ESTOS-03 l.7103; 41.3 l.6864): web e app sobre o MESMO cenário
// (dois contextos com o mesmo localStorage, como dois quadros do Canvas). Uso: node inicio_entrega_unit.js <pasta com ini_web.js e ini_app.js>
const vm = require('vm'), fs = require('fs'), path = require('path');
const DIR = process.argv[2]; const LS = {};
const localStorage = { getItem: k => (k in LS ? LS[k] : null), setItem: (k, v) => { LS[k] = String(v); }, removeItem: k => { delete LS[k]; } };
function frame(f) { const ctx = { localStorage, console, Date, JSON, Math, Number, String, Object, Array, BigInt, Error, isFinite, RegExp };
  vm.createContext(ctx); vm.runInContext(fs.readFileSync(path.join(DIR, f), 'utf-8') + '\n;globalThis.__x=(s)=>eval(s);', ctx, { filename: f }); return ctx; }
const W = frame('ini_web.js'), A = frame('ini_app.js'); const w = s => W.__x(s), a = s => A.__x(s);
const R = []; const ok = (n, c, info) => R.push({ n, ok: !!c, info: c ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 700) });
const web = id => w(`(()=>{const c=cenGet(),o=c.ordens['${id}'];const e=osIniErro(o,o.req&&c.reqs[o.req]);return e?[e.t,e.q,e.h||'',e.hl||'']:null})()`);
const passo = id => a(`(()=>{const c=cenGet();const p=mbPasso(c,c.ordens['${id}']);return [p.k,p.chip[0]]})()`);
const iniApp = id => a(`(()=>{const r=cenMudar(null,c=>mbIniciar(c,'${id}'));return r.erro||''})()`);
const iniWeb = id => w(`(()=>{const r=cenMudar(null,c=>osc_iniciar(c,'${id}'));return r.erro||''})()`);
const mud = (X, s) => X.__x(`(()=>{const r=cenMudar(null,c=>{${s}});return r.erro||r.msg||''})()`);
const reset = () => { w('cenReset()'); a('cenReset()'); };   // os dois quadros voltam ao seed (cenReset limpa a memória de cada um)
const st = s => w(`(()=>{const c=cenGet();return (${s})})()`);
const lib0430 = () => { reset(); mud(W, "return osc_liberar(c,'OS-0430',false,'','Ana')"); return st("c.ordens['OS-0430'].req"); };
const ent = (rid, p, q) => mud(W, `return cenEntregar(c,'${rid}','${p}',${q},'Marcos','Rui')`);
const conf = rid => mud(A, `return cenConfirmarRecebimento(c,'${rid}')`);
const fechar = (ha, cons) => mud(A, `return cenFecharTurno(c,${ha},1,${cons ? JSON.stringify(cons) : 'null'},'')`);

// N1 · reprodução da auditoria: só o Glifosato entregue e confirmado → web e app recusam com o MESMO texto; nada é gravado
let rid = lib0430(); ent(rid, 'Glifosato 480', 320); conf(rid);
const T1 = 'Iniciar bloqueado: REQ-041 sem entrega · 2,4-D 806 160 L, Óleo mineral 80 L a entregar.', Q1 = 'Rui (almoxarife) entrega no Estoque; Marcos confirma o recebimento no app.';
let rev0 = st('c.rev'), mv0 = st('c.movs.length'); let e = web('OS-0430'), ea = iniApp('OS-0430'), ew = iniWeb('OS-0430');
ok('N1 web: entrega parcial bloqueia o início com dono e atalho Entregar no Estoque', JSON.stringify(e) === JSON.stringify([T1, Q1, 'EST.dc.html', 'Entregar no Estoque']), e);
ok('N1 web: osc_iniciar recusa com o mesmo texto', ew === T1, ew);
ok('N1 app: mbIniciar recusa com o texto da web + dono (uma regra, dois canais)', ea === T1 + ' ' + Q1, ea);
ok('N1 app: cartão pede retirada ("Entrega parcial · REQ-041"), não "Iniciar turno"', JSON.stringify(passo('OS-0430')) === JSON.stringify(['retirar', 'Entrega parcial · REQ-041']), passo('OS-0430'));
ok('N1 atômico: recusado não grava (rev, movimentos, fase e turno iguais)', st('c.rev') === rev0 && st('c.movs.length') === mv0 && st("c.ordens['OS-0430'].etapa") === 'Liberadas' && st('c.app.turno') === null, [st('c.rev'), rev0, st("c.ordens['OS-0430'].etapa")]);
mud(A, 'return cenSinal(c,false)');
ok('N1 app sem sinal: a mesma recusa (regra avaliada no aparelho)', iniApp('OS-0430') === T1 + ' ' + Q1, iniApp('OS-0430'));
mud(A, 'return cenSinal(c,true)');

// N2 · nada entregue (OS-0424 do seed, REQ-039 só reservada)
reset();
ok('N2 app: OS-0424 sem entrega recusa e o cartão segue "Reservado · REQ-039"', iniApp('OS-0424') === 'Iniciar bloqueado: REQ-039 sem entrega · Fungicida A 65 L a entregar. Rui (almoxarife) entrega no Estoque; Marcos confirma o recebimento no app.'
   && JSON.stringify(passo('OS-0424')) === JSON.stringify(['retirar', 'Reservado · REQ-039']), [iniApp('OS-0424'), passo('OS-0424')]);

// N3 · entregue e não confirmado
rid = lib0430(); ent(rid, 'Glifosato 480', 320); ent(rid, '2,4-D 806', 160); ent(rid, 'Óleo mineral', 80);
const T3 = 'Iniciar bloqueado: Glifosato 480 320 L, 2,4-D 806 160 L, Óleo mineral 80 L entregues a Marcos, aguardando confirmação no app.';
e = web('OS-0430'); ea = iniApp('OS-0430');
ok('N3 web: entregue sem confirmação bloqueia com atalho Ver no app', JSON.stringify(e) === JSON.stringify([T3, 'Marcos confirma o recebimento no app.', 'MB-05.dc.html', 'Ver no app']), e);
ok('N3 app: mesma recusa; o cartão pede Confirmar recebimento', ea === T3 + ' Marcos confirma o recebimento no app.' && passo('OS-0430')[0] === 'confirmar', [ea, passo('OS-0430')]);

// P1 · completo e confirmado → inicia nos dois canais
conf(rid);
ok('P1 web sem bloqueio e app oferece Iniciar turno', web('OS-0430') === null && passo('OS-0430')[0] === 'iniciar', [web('OS-0430'), passo('OS-0430')]);
ok('P1 app: inicia e a ordem vai a Em execução', iniApp('OS-0430') === '' && st("c.ordens['OS-0430'].etapa") === 'Em execução' && st('c.app.turno.os') === 'OS-0430', st("c.ordens['OS-0430'].etapa"));

// P2 · entrega fracionada (PRD l.1251): 40 + 20 + 10 L (20 ha de cada componente) inicia; o turno de 20 ha consome tudo
rid = lib0430(); ent(rid, 'Glifosato 480', 40); ent(rid, '2,4-D 806', 20); ent(rid, 'Óleo mineral', 10); conf(rid);
ok('P2 web: entrega fracionada com todos os componentes inicia (osc_iniciar)', iniWeb('OS-0430') === '' && st("c.ordens['OS-0430'].etapa") === 'Em execução', iniWeb('OS-0430'));
ok('P2 app: turno abre e fecha 20 ha (40/20/10 L baixados, custódia 0/0/0)', iniApp('OS-0430') === '' && /^Turno fechado: 20 ha/.test(fechar(20))
   && st(`c.reqs['${rid}'].itens.map(i=>i.consumido+'/'+i.custodia).join(' ')`) === '40/0 20/0 10/0' && st("c.ordens['OS-0430'].saldo") === 140, st(`c.reqs['${rid}'].itens.map(i=>i.consumido+'/'+i.custodia).join(' ')`));
// N4 · próximo turno sem material (nada mais com o operador)
ok('N4 app: próximo turno recusado: 280 + 140 + 70 L a entregar; cartão "Entrega parcial"', iniApp('OS-0430') === 'Iniciar bloqueado: REQ-041 sem entrega · Glifosato 480 280 L, 2,4-D 806 140 L, Óleo mineral 70 L a entregar. ' + Q1
   && JSON.stringify(passo('OS-0430')) === JSON.stringify(['retirar', 'Entrega parcial · REQ-041']), [iniApp('OS-0430'), passo('OS-0430')]);
// N4b · um componente acaba antes dos outros (Óleo 10 L para 20 ha; os outros com sobra)
ent(rid, 'Glifosato 480', 280); ent(rid, '2,4-D 806', 140); ent(rid, 'Óleo mineral', 10);
ok('R7 residual documentado: a 2ª entrega herda a confirmação da 1ª (cenEntregar não zera confirmado)', conf(rid) === 'Nada entregue para confirmar.' && st(`c.reqs['${rid}'].itens.every(i=>i.confirmado)`), conf(rid));
ok('N4b app: inicia com os três; fecha 20 ha e o Óleo zera', iniApp('OS-0430') === '' && /^Turno fechado: 20 ha/.test(fechar(20)) && st(`c.reqs['${rid}'].itens.map(i=>i.custodia).join(' ')`) === '240 120 0', st(`c.reqs['${rid}'].itens.map(i=>i.custodia).join(' ')`));
ok('N4b app: só o Óleo falta: "Óleo mineral 60 L a entregar"', iniApp('OS-0430') === 'Iniciar bloqueado: REQ-041 sem entrega · Óleo mineral 60 L a entregar. ' + Q1, iniApp('OS-0430'));

// N5 · componente esgotado: consumo acima da custódia aceito pela gestora (CTL-3, padrão 2) zera o saldo a entregar; a área continua → dono é a agrônoma
reset(); iniApp('OS-0421'); fechar(100, { 'Fungicida A': 80, 'Adjuvante espalhante': 0 }); mud(W, "return cenConciliar(c,'CC-301',true,undefined,'Ana')");
const it5 = st("(()=>{const i=c.reqs['REQ-035'].itens[0];return [i.solicitado,i.consumido,i.custodia,cenSaldoEntregar(i),c.ordens['OS-0421'].saldo]})()");
const T5 = 'Iniciar bloqueado: Fungicida A: todo o solicitado na REQ-035 já foi consumido e nada está com Marcos. Ana (agrônoma) decide a área restante: Dispensar saldo na O.S. e, se ainda precisar aplicar, emitir nova ordem.';
ok('N5 estado: 175 solicitados, 175 consumidos, custódia 0, nada a entregar, 60 ha de saldo', JSON.stringify(it5) === '[175,175,0,0,60]', it5);
ok('N5 app: recusa com dono Ana (agrônoma); cartão "Insumo esgotado", não "Retirar"', iniApp('OS-0421') === T5 && JSON.stringify(passo('OS-0421')) === JSON.stringify(['rever', 'Insumo esgotado · Ana (agrônoma)']), [iniApp('OS-0421'), passo('OS-0421')]);
const MG = id => w(`(()=>{const c=cenGet(),co=c.ordens['${id}'];const o=osMerge(Object.assign(cenClone(co),{selos:[]}),co,c);const pb=osProx(o);return [o.selos.map(s=>s.t+'/'+s.c).join(', '),o.dono,o.prazo,pb.P.btn,pb.b?pb.b.t+' | '+pb.b.q:null]})()`);
const mg5 = MG('OS-0421');
ok('N5 web: a dona vê a pendência na lista/Kanban/Mapa (selo vermelho "Insumo esgotado · Fungicida A", Ana, decidir a área restante; painel com o impedimento no lugar do primário)', JSON.stringify(mg5) === JSON.stringify(['Parcial · dia 4 de 7/yellow, Insumo esgotado · Fungicida A/red', 'Ana (agrônoma)', 'decidir a área restante', 'Registrar apontamento', 'Apontar bloqueado: Fungicida A: todo o solicitado na REQ-035 já foi consumido e nada está com Marcos. | Ana (agrônoma) decide a área restante: Dispensar saldo na O.S. e, se ainda precisar aplicar, emitir nova ordem.']), mg5);
ok('N5 Rui não resolve: entregar mais é recusado (saldo a entregar 0 L)', ent('REQ-035', 'Fungicida A', 1) === 'Acima do saldo a entregar: 0 L.', ent('REQ-035', 'Fungicida A', 1));

// P5 · caminho feliz: entrega completa, 160 ha num turno, custódia 0/0/0 → próximo passo é Enviar para conferência, sem selo vermelho
rid = lib0430(); ent(rid, 'Glifosato 480', 320); ent(rid, '2,4-D 806', 160); ent(rid, 'Óleo mineral', 80); conf(rid); iniApp('OS-0430'); fechar(160);
const m5 = MG('OS-0430');
ok('P5 web: ordem concluída com consumo exato fica sem "Insumo esgotado", sem dona Ana, primário Enviar para conferência', m5[0] === '' && m5[1] !== 'Ana (agrônoma)' && m5[3] === 'Enviar para conferência' && m5[4] === null, m5);
// P6 · o último turno ficou no aparelho (sem sinal): a web mostra "Aguardando sinal", não "Insumo esgotado"
rid = lib0430(); ent(rid, 'Glifosato 480', 320); ent(rid, '2,4-D 806', 160); ent(rid, 'Óleo mineral', 80); conf(rid); mud(A, 'return cenSinal(c,false)'); iniApp('OS-0430'); fechar(160);
const m6 = MG('OS-0430');
ok('P6 web: turno no aparelho consumiu tudo; a web segue "Aguardando sinal do app", sem "Insumo esgotado" nem dona Ana', m6[0] === 'Aguardando sinal do app/yellow' && m6[1] !== 'Ana (agrônoma)' && m6[4] === null, m6);
mud(A, 'return cenSinal(c,true)');
// P6b · o aparelho baixou todo o insumo em 100 de 160 ha (usado informado), sem sinal: a web lê o servidor (osReqVis), não a baixa local;
// com o sinal, o servidor vê o esgotado com 60 ha a fazer e a dona passa a ser Ana
rid = lib0430(); ent(rid, 'Glifosato 480', 320); ent(rid, '2,4-D 806', 160); ent(rid, 'Óleo mineral', 80); conf(rid); mud(A, 'return cenSinal(c,false)'); iniApp('OS-0430');
fechar(100, { 'Glifosato 480': 320, '2,4-D 806': 160, 'Óleo mineral': 80 }); const m6b = MG('OS-0430'); mud(A, 'return cenSinal(c,true)'); const m6c = MG('OS-0430');
ok('P6b web sem sinal: o consumo no aparelho não vira "Insumo esgotado" antes do envio; com o sinal vira, com Ana (60 ha a fazer)', !/Insumo esgotado/.test(m6b[0]) && m6b[1] !== 'Ana (agrônoma)'
   && /Insumo esgotado · Glifosato 480, 2,4-D 806, Óleo mineral\/red/.test(m6c[0]) && m6c[1] === 'Ana (agrônoma)', [m6b, m6c]);
// P3 · exceções legítimas: ordem sem insumo (inclui água sem produto, DEC-2609-10) não passa pela regra
reset(); mud(W, "return osc_liberar(c,'OS-0511',false,'','Ana')");
ok('P3 sem insumo: OS-0505 (Em execução) e OS-0511 (liberada sem requisição) iniciam', iniApp('OS-0505') === '' && mud(A, 'c.app.turno=null; return {msg:"x"}') === 'x' && iniApp('OS-0511') === '', [iniApp('OS-0505')]);
// P4 · residual registrado: componente fora da requisição (Adjuvante da OS-0421) não é coberto por esta correção
reset();
ok('P4 residual: OS-0421 (Adjuvante fora da REQ-035) inicia como hoje', iniApp('OS-0421') === '', iniApp('OS-0421'));
console.log(JSON.stringify(R));
