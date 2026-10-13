// PCM S3 × O.S. (revisão 09/10, A5): a ordem que depende de um ativo da Manutenção lê a condição única; com a máquina apta sai só o impedimento e o
// dono volta ao normal da fase (a reprogramação pelo PCP só antes de liberar). Monta: perfis + cenário + O.S. (JS_NUCLEO) + regras da manutenção.
const R = []; const ok = (n, cond, info) => R.push({ n, ok: !!cond, info: cond ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 600) });
const caso = (n, fn) => { try { fn(); } catch (e) { R.push({ n: n + ' (exceção)', ok: false, info: String(e && e.stack || e).slice(0, 600) }); } };
const ZE = g2pf('Zé');
const os = (id) => ords().find(x => x.id === id);
caso('REV-A5 O.S. depois do apto', () => {
  cenReset(); try { cenSave(cenClone(CEN0)); } catch (e) {}
  const a0 = os('OS-0420'), b0 = os('OS-0431');
  ok('REV-A5 · antes: OS-0420 (Em execução) e OS-0431 (A liberar) impedidas pelo Trator T1 com o link da OM-0233', !!a0.bloq && !!b0.bloq && /OM-0233/.test(a0.bloq.t) && /OM-0233/.test(b0.bloq.t), [a0.bloq, b0.bloq]);
  const r1 = manMudar(null, (m) => { const t = m.oms['OM-0233'].chk.findIndex(x => x.tipo === 'Teste'); manTentativa(m, 'OM-0233', t, 'Aprovado', 'manômetro 190 bar', ZE); return manConcluir(m, 'OM-0233', '4320', '6,5', false, {}, ZE); });
  const r2 = manMudar(null, (m) => manDeclararApto(m, 'OM-0233', ZE));
  const a = os('OS-0420'), b = os('OS-0431');
  ok('REV-A5 (S3) · com o T1 apto, a OS-0420 em execução perde o impedimento e não vai para o PCP ("reprogramar" só antes de liberar)', !r1.erro && !r2.erro && !a.bloq && a.etapa === 'Em execução' && a.dono !== 'PCP' && !/reprogram/.test(a.prazo + ' ' + a.cond) && !(a.selos || []).some(s => /bloquead|Falta máquina/i.test(s.t)), [r2, a.dono, a.prazo, a.cond]);
  ok('REV-A5 · a OS-0431 (A liberar) perde o impedimento; o PCP reprograma uma vez e o texto diz quem libera depois', !b.bloq && b.etapa === 'A liberar' && b.dono === 'PCP' && /reprogram/.test(b.prazo) && /reprograma a máquina/.test(b.cond) && /confere e libera/.test(b.cond), [b.dono, b.prazo, b.cond]);
  cenMudar(null, (c) => { c.ordens['OS-0420'].etapa = 'Em conferência'; return {}; }); const e = os('OS-0420');
  ok('REV-A5 · em Em conferência a ordem volta ao dono da fase (quem confere), nunca "Pendência com PCP"', e.dono !== 'PCP' && e.prazo === 'conferir' && !/reprogram/.test(e.cond), [e.dono, e.prazo, e.cond]);
});
// V55-COMP-02 (S3): com a máquina apta, osManCond (último passo do osMerge) tira só o impedimento; a pendência específica que as regras do
// osMerge já calcularam (divergência de dose, saldo do Estoque…) fica com o dono e o prazo dela, como numa ordem sem o vínculo da máquina
// (osMerge({...b,bloq:null})). PCP ou o dono da fase só sem pendência mais específica (controle: estoque original continua PCP)
const D = (r) => ({ dono: r.dono, prazo: r.prazo, bloq: r.bloq, maq: (r.selos || []).filter(s => /bloquead|Falta máquina/i.test(s.t)).map(s => s.t), cond: String(r.cond || '').slice(0, 220) });
for (const et of ['Em execução', 'Em conferência']) caso('COMP-02 A ' + et, () => {
  const c = cenClone(CEN0); const o = c.ordens['OS-0420']; c.man.ativos.a01.cond = 'Apto'; o.etapa = et;
  const ap = o.ap.find(cenApSomado); ap.div = [{ p: o.ins[0].p, plan: 10, inf: 5, un: cenDivUn(c, o, o.ins[0].p) }]; delete ap.rev; cenSeloDiv(c, o.id);
  const b = OSD.ords.find(x => x.id === o.id); const r1 = osMerge(b, o, c), r0 = osMerge(Object.assign({}, b, { bloq: null }), o, c);
  const pz = et === 'Em execução' ? 'revisar a divergência de dose do dia 1' : 'revisar a divergência de dose';
  ok('COMP-02 A · OS-0420 ' + et + ' com divergência de dose aberta e o Trator T1 apto: dono e prazo iguais aos da ordem sem o vínculo da máquina ("Ana (agrônoma)" · "' + pz + '"), sem impedimento nem selo da máquina',
    !!b.bloq && r1.dono === r0.dono && r1.prazo === r0.prazo && r1.dono === 'Ana (agrônoma)' && r1.prazo === pz && !r1.bloq && !D(r1).maq.length && (r1.selos || []).some(s => /^Divergência de consumo\/dose/.test(s.t)), [D(r1), D(r0)]);
  if (et === 'Em conferência') ok('COMP-02 A · ativo apto não encerra a revisão agronômica: o encerramento continua bloqueado pela divergência (quem resolve: ' + OS_AGRO() + ')',
    String(r1.encM || '').indexOf(CEN_DIV) === 0 && /^Encerrar bloqueado: divergência/.test(osEncBloq(r1).t), [r1.encM, osEncBloq(r1)]);
});
caso('COMP-02 B', () => {
  const mk = (zera) => { const c = cenClone(CEN0); const o = c.ordens['OS-0431']; c.man.ativos.a01.cond = 'Apto'; const ps = o.ins.map(i => i.p);
    if (zera) Object.values(c.lotes).forEach(l => { if (ps.indexOf(l.prod) >= 0) { l.fisico = 0; l.quarentena = 0; } }); return [c, o]; };
  const b = OSD.ords.find(x => x.id === 'OS-0431');
  const [c, o] = mk(true); const e = osLibErro(o, c); const r1 = osMerge(b, o, c), r0 = osMerge(Object.assign({}, b, { bloq: null }), o, c);
  ok('COMP-02 B · OS-0431 A liberar, Trator T1 apto e estoque dos insumos zerado: osLibErro dá "Saldo insuficiente…"; dono e próximo passo os de Suprimentos (receber o insumo), iguais aos da ordem sem o vínculo, não PCP/reprogramar; o texto diz que a liberação aguarda o insumo',
    o.etapa === 'A liberar' && /^Saldo insuficiente/.test(e) && r1.dono === r0.dono && r1.prazo === r0.prazo && r1.dono === 'Suprimentos' && r1.prazo === 'receber o insumo no Estoque' && !r1.bloq && !D(r1).maq.length
    && /A liberação aguarda .+ no Estoque\./.test(r1.cond) && !/Próximo passo: liberar para execução/.test(r1.cond), [e, D(r1), D(r0)]);
  const [c2, o2] = mk(false); const r2 = osMerge(b, o2, c2);
  ok('COMP-02 controle · com o estoque original (sem pendência específica) a OS-0431 apta continua com o PCP: "reprogramar antes de liberar"',
    osLibErro(o2, c2) === '' && r2.dono === 'PCP' && r2.prazo === 'reprogramar antes de liberar' && /reprograma a máquina/.test(r2.cond) && /Próximo passo: liberar para execução\./.test(r2.cond) && !r2.bloq, D(r2));
});
print(JSON.stringify(R));
