// COLH-APONT F1 (docs/gestao/GESTAO-1810.md §2 e §6) · regras do apontamento da colheita pela web, no node, sem navegador.
// Carregado por colh_apont_test.py depois de: perfis + CEN0 + cenario.js + PRDC + producao.js (o mesmo prefixo do producao_unit_test.py).
// Oráculos independentes da regra testada: números da semente (OS-0505: 75,11 ha, 50 ha feitos, saldo 25,11 ha; passe S39 com 36.420 kg).
const R = []; function ok(n, c, info) { R.push({ n, ok: !!c, info: c ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 700) }); }
function MUD(c, fn) { const x = cenClone(c); try { const r = fn(x) || {}; Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); return r; } catch (e) { return { erro: String(e.message || e) }; } }
const NOVO = () => cenClone(CEN0);
const AP = (c) => (c.ordens['OS-0505'].ap || []).filter(a => a.st !== 'Previsto');
const K1 = { os: 'OS-0505', d: '26/09', ha: '20', h: '', umid: '', perda: '1,5', obs: 'talhão úmido de manhã', chave: 'W-COLH-u1', por: 'Ana (agrônoma)' };

// UA1 · C1 no comando: 20 ha hoje entram provisórios, pela regra única (cenApontar, origem web); o saldo cai 20 ha
{ const c = NOVO(); const n0 = AP(c).length; const r = MUD(c, x => prApontarColheita(x, K1)); const o = c.ordens['OS-0505']; const a = AP(c).find(x => x.chave === 'W-COLH-u1');
  ok('UA1 20 ha em 26/09 na OS-0505: um apontamento novo, Provisório, origem web, chave do formulário; saldo 25,11 → 5,11 ha; realizado 70 ha',
     !r.erro && AP(c).length === n0 + 1 && a && a.st === 'Provisório' && a.origem === 'web' && a.ha === 20 && a.d === '26/09' && prCmp(o.saldo, 5.11) === 0 && o.realizado === 70, [r, a, o.saldo, o.realizado]);
  const g = (c.producao.apont || {})['W-COLH-u1'];
  ok('UA1b umidade e perdas ficam no registro da colheita pela chave (nunca no ap); a observação vai no ap; quem registrou fica guardado',
     g && g.perda === 1.5 && g.umid === null && g.por === 'Ana (agrônoma)' && g.dia === a.dia && a.perda === undefined && a.umid === undefined && a.obs === 'talhão úmido de manhã', [g, a]);
  ok('UA1c o previsto do dia 3 (24/09) sai quando o apontamento soma, como na web da O.S.', !(c.ordens['OS-0505'].ap || []).some(x => x.st === 'Previsto'), c.ordens['OS-0505'].ap);
  // UA2 · C2 no comando: a mesma chave com o mesmo conteúdo é o mesmo registro
  const r2 = MUD(c, x => prApontarColheita(x, K1));
  ok('UA2 C2 repetir (mesma chave e conteúdo) não duplica: "já registrado", 1 apontamento, saldo 5,11 ha', !r2.erro && r2.repetido && AP(c).filter(x => x.chave === 'W-COLH-u1').length === 1 && prCmp(c.ordens['OS-0505'].saldo, 5.11) === 0, [r2, c.ordens['OS-0505'].saldo]);
  // UA3 · mesma chave, outro conteúdo: conflito, nada grava
  const ant = JSON.stringify(c); const r3 = MUD(c, x => prApontarColheita(x, Object.assign({}, K1, { ha: '21' }))); const r4 = MUD(c, x => prApontarColheita(x, Object.assign({}, K1, { perda: '2' })));
  ok('UA3 mesma chave com outra área ou outra perda = conflito; o estado não muda', /conflito/.test(r3.erro || '') && /conflito/.test(r4.erro || '') && JSON.stringify(c) === ant, [r3, r4]);
  // UA4 · R-02: a área do passe usa o apontamento; a produção não muda sem carga
  const p = prResultado(c, 'lg19').passes.find(x => x.os === 'OS-0505');
  ok('UA4 R-02 passe S39 do Pivô 19: 70 ha apontados; produção 36.420 kg (sem carga nova); produtividade 36,42 t ÷ 70 ha = 0,52 t/ha', p.area === 70 && p.kg === 36420 && prFmt(p.prtv, 2) === '0,52', [p.area, p.kg, p.prtv]);
  // UA5 · lista do talhão: o novo no topo, com o registro
  const L = prApLista(c, 'lg19');
  ok('UA5 lista do Pivô 19 do mais recente ao mais antigo: 26/09 (web, provisório, perdas 1,5) · 22/09 · 21/09; sem o previsto', L.map(x => x.a.d).join(' ') === '26/09 22/09 21/09' && L[0].r && L[0].r.perda === 1.5 && L.every(x => x.a.st !== 'Previsto'), L.map(x => [x.a.d, x.a.st])); }

// UA6 · recusas (o erro vem antes de gravar; uma regra para a tela e o comando: prApValida)
{ const c = NOVO(); const ant = JSON.stringify(c); const T = (o) => MUD(c, x => prApontarColheita(x, Object.assign({}, K1, { chave: 'W-COLH-r' + Math.random() }, o))).erro || '';
  const e = { fut: T({ d: '27/09' }), inv: T({ d: '31/02' }), vaz: T({ d: '' }), ha0: T({ ha: '' }), haN: T({ ha: 'abc' }), sal: T({ ha: '26' }), h0: T({ h: '0' }), um: T({ umid: '120' }), pe: T({ perda: '-1' }) };
  ok('UA6 recusas sem gravar: data futura, data inexistente, sem data, sem área, área não numérica, acima do saldo (máximo 25,11 ha), horas 0, umidade 120 %, perdas negativas',
     /futura/.test(e.fut) && /Informe a data/.test(e.inv) && /Informe a data/.test(e.vaz) && /área colhida/.test(e.ha0) && /área colhida/.test(e.haN) && /Máximo 25,11 ha/.test(e.sal)
     && /Horas/.test(e.h0) && /Umidade/.test(e.um) && /Perdas/.test(e.pe) && JSON.stringify(c) === ant, e);
  const v = prApValida({ d: '26/09', ha: '20,5', h: '8', umid: '14,5', perda: '0' });
  ok('UA6b o mesmo formulário válido (vírgula decimal, perdas 0) não tem erro; ontem também vale', !Object.keys(v).length && !Object.keys(prApValida({ d: '25/09', ha: '1' })).length, v); }

// UA7 · a regra do comando único não muda: O.S. só liberada não soma
{ const c = NOVO(); c.ordens['OS-0505'].etapa = 'Liberadas'; const r = MUD(c, x => prApontarColheita(x, Object.assign({}, K1, { chave: 'W-COLH-lib' })));
  ok('UA7 O.S. Liberada: recusado pelo cenApontar ("não está em execução"), nada gravado', /não está em execução/.test(r.erro || '') && !AP(c).some(a => a.chave === 'W-COLH-lib'), r); }

// UA8 · duplicidade com o app na mesma data: a mesma regra de hoje (retém, não soma)
{ const c = NOVO(); MUD(c, x => cenApontar(x, { os: 'OS-0505', d: '26/09', ha: 10, h: 4, origem: 'app', quem: 'Marcos', chave: 'APC-OS-0505-9' }));
  const s0 = c.ordens['OS-0505'].saldo; const r = MUD(c, x => prApontarColheita(x, Object.assign({}, K1, { ha: '10', chave: 'W-COLH-dup' }))); const a = AP(c).find(x => x.chave === 'W-COLH-dup');
  ok('UA8 web na mesma data de um apontamento do app: retido como "' + CEN_AP_DUP + '", saldo não muda, a mensagem diz quem decide', !r.erro && a && a.st === CEN_AP_DUP && c.ordens['OS-0505'].saldo === s0 && /Retido/.test(r.msg), [r, a && a.st, s0, c.ordens['OS-0505'].saldo]); }

// UA9 · C1/C3 na fonte única (prTal: Colheita e Mapa): quem tem a primária e o motivo de quem não tem
{ const c = NOVO(); const x19 = prTal(c, 'lg19'), x6 = prTal(c, 'lg06'), xc1 = prTal(c, 'c1');
  ok('UA9 Pivô 19 (OS-0505 em execução): primária "Apontar colheita" na OS-0505; o passo da previsão (Publicar previsão) fica em ac0', x19.ac.k === 'apontar' && x19.ac.t === 'Apontar colheita' && x19.ac.os === 'OS-0505' && x19.ac0 && x19.ac0.k === 'publicar', [x19.ac, x19.ac0]);
  const m1 = prApMotivo(c, xc1), m6 = prApMotivo(c, x6);
  ok('UA9b C3 T1-A soja (sem O.S.) e Pivô 6 (só O.S. encerrada): sem apontar; motivo e "Programar colheita" com cultivo, atividade e janela',
     xc1.ac === null && x6.ac.k !== 'apontar' && !xc1.apo && !x6.apo && /Sem O\.S\. de colheita liberada ou em execução/.test(m1.t) && m1.l && m1.l.t === 'Programar colheita' && m1.l.h === 'OS.dc.html#nova:c1:a8:2027-02-12'
     && m6.l && m6.l.h === 'OS.dc.html#nova:lg06:q3:2026-09-28', [xc1.ac, x6.ac, m1, m6]);
  c.ordens['OS-0505'].etapa = 'Liberadas'; const xl = prTal(c, 'lg19');
  ok('UA9c O.S. só Liberada: a primária continua "Apontar colheita" e o próximo passo é iniciar a ordem', xl.ac.k === 'apontar' && xl.apo.etapa === 'Liberadas' && /^Iniciar a OS-0505 para apontar/.test(xl.nx), xl.nx); }
