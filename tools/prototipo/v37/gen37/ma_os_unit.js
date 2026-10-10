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
print(JSON.stringify(R));
