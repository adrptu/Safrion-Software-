// Resume a saída de raiox_repro.mjs em tabelas de texto. Uso: node resumo.mjs repro.json
import fs from 'node:fs';
const R = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const L = [];
const p = s => L.push(s);
p('fonte ' + (R.artefato.origem || R.artefato.arquivo) + ' · ' + R.artefato.bytes + ' bytes · sha256 ' + R.artefato.sha256 + ' · node ' + R.node + ' · ' + R.segundos + ' s');
if (R.artefato.nota) p('nota: ' + R.artefato.nota);
p('');
p('== 1. Semente original, dia 86 (25/09) ==');
let H = 0, T = 0, F = 0, Nz = 0;
for (const [alvo, o] of Object.entries(R.original)) {
  H += o.hit; T += o.tot; F += o.fp; Nz += o.ruido;
  p(`${alvo}: recuperados ${o.hit}/${o.tot} (só Forte/Moderada: ${o.hitFM}/${o.tot}) · falso positivo forte/moderado ${o.fp}/${o.ruido} · ruído exibido em qualquer nível: ${o.ruidoExibido.join(', ') || 'nenhum'} · a confirmar: ${o.aConfirmar.join(', ') || 'nenhum'} · pares ${o.pares} · talhões ${o.talhoes} · semanas ${o.semanas} · rxGet ${o.msRxGet} ms`);
  p(`   gate 3 semanas: ok=${o.gate.ok} Brier modelo ${o.gate.bm.toFixed(3)} × persistência ${o.gate.bp.toFixed(3)} · n=${o.gate.n} · eventos=${o.gate.ev}`);
  for (const t of o.tabela) {
    if (!t.plantado && !t.proxy && t.nivel === '-') continue;
    p(`   ${t.k.padEnd(6)} plantado=${String(t.plantado).padStart(2)} proxy=${(t.proxy || '-').padEnd(4)} nível=${String(t.nivel).padEnd(18)} efeito=${t.efeito == null ? '-' : t.efeito + ' %'} ic95=${t.ic95 ? '[' + t.ic95.join('; ') + ']' : '-'} janela=${t.janela ?? '-'} limiar=${t.limiar ?? '-'} casos=${t.nHi ?? '-'} talhões=${t.talhoes ?? '-'} semanas=${t.semanas ?? '-'} q=${t.qBH ?? '-'}`);
  }
  p(`   exibidos na tela: ${o.exibidos.join(' · ') || 'nenhum'}`);
  const b = o.backtest;
  p(`   origem móvel (cortes ${b.cortes.join(',')}; n=${b.n}; eventos=${b.ev}) Brier: modelo ${b.modelo} · modelo sem previsão ${b.modeloSemPrevisao} · nível+estádio ${b.nivelEstadio} · persistência 0/1 ${b.persistencia} · taxa-base ${b.taxaBase}`);
  p(`   resíduo: ${o.residuo.comResiduo} de ${o.residuo.pares} pares "sem controle" têm resíduo de aplicação ativo no início do par`);
  const c = o.controle, f = x => `${x.E ?? '-'} % (n=${x.n}${x.ic90 ? '; ic90 ' + x.ic90.join('–') : ''})`;
  p(`   leitura "antes" no próprio dia da aplicação: ${c.antesNoMesmoDia} de ${c.aplicacoesComAntesDepois} · voltas ao NC contadas: ${c.voltasAoNC}, das quais ${c.voltaSemNuncaFicarAbaixo} sem nenhuma leitura abaixo do NC antes e ${c.voltaContadaAntesDe5Dias} com menos de 5 dias`);
  p(`   controle: ${c.aplicacoesComAntesDepois} aplicações com antes/depois · ${c.semControleValido} sem controle válido · reaplicação antes de voltar ao NC: ${c.reaplicacaoAntesDeVoltarAoNC} · armadilha nº aplicações × nível: ρ=${c.armadilhaAplicacoesXNivel}`);
  p(`      dia quente e seco ${f(c.diaQuenteSeco.com)} × demais ${f(c.diaQuenteSeco.sem)}`);
  p(`      chuva até 1 dia   ${f(c.chuvaAte1Dia.com)} × sem chuva ${f(c.chuvaAte1Dia.sem)}`);
  p(`      barra 100 L/ha    ${f(c.barra100.com)} × atomizador ${f(c.barra100.sem)}`);
  p(`      mesmo grupo seguido ${f(c.mesmoGrupoSeguido.com)} × rotação ${f(c.mesmoGrupoSeguido.sem)}`);
}
p(`TOTAL semente original: recuperados ${H}/${T} (só Forte/Moderada: ${Object.values(R.original).reduce((s, o) => s + o.hitFM, 0)}/${T}) · falso positivo forte/moderado ${F}/${Nz}`);
p('');
p('== 2. Réplicas (20 sementes; chuva e ondas de calor fixas no gerador) ==');
const agg = {}; let tot = { hit: 0, tot: 0, fp: 0, noise: 0, shownNoise: 0, gateOk: 0, gateN: 0, conf: 0, frio: 0 };
const dist = [];
for (const [s, rr] of Object.entries(R.replicas)) {
  let h = 0, t = 0, fp = 0, sn = 0;
  for (const [alvo, o] of Object.entries(rr)) {
    if (o.frio) { tot.frio++; continue; }
    agg[alvo] = agg[alvo] || { hit: 0, hitFM: 0, tot: 0, fp: 0, noise: 0, shown: 0, gate: 0, n: 0, conf: 0, fpVars: {}, bt: { modelo: 0, semPrev: 0, nivel: 0, pers: 0, base: 0, venceNivel: 0, semPrevVencePers: 0 } };
    const A = agg[alvo]; A.hitFM += o.hitFM;
    o.exibidos.filter(x => x.endsWith('[ruído]')).forEach(x => { A.fpVars[x] = (A.fpVars[x] || 0) + 1; });
    const b = o.backtest; A.bt.modelo += b.modelo; A.bt.semPrev += b.modeloSemPrevisao; A.bt.nivel += b.nivelEstadio; A.bt.pers += b.persistencia; A.bt.base += b.taxaBase;
    A.bt.venceNivel += b.modelo < b.nivelEstadio ? 1 : 0; A.bt.semPrevVencePers += b.modeloSemPrevisao < b.persistencia ? 1 : 0;
    A.hit += o.hit; A.tot += o.tot; A.fp += o.fp; A.noise += o.ruido; A.shown += o.ruidoExibido.length; A.gate += o.gate && o.gate.ok ? 1 : 0; A.n++; A.conf += o.aConfirmar.length;
    h += o.hit; t += o.tot; fp += o.fp; sn += o.ruidoExibido.length;
  }
  dist.push(`${s}${h}/${t} fp=${fp} ruídoExibido=${sn}`);
  tot.hit += h; tot.tot += t; tot.fp += fp;
}
for (const [alvo, A] of Object.entries(agg)) p(`${alvo}: recuperados ${A.hit}/${A.tot} (${Math.round(100 * A.hit / A.tot)} %; só Forte/Moderada ${A.hitFM}/${A.tot} = ${Math.round(100 * A.hitFM / A.tot)} %) · falso positivo forte/moderado ${A.fp}/${A.noise} · ruído exibido (qualquer nível) ${A.shown} · "a confirmar" ${A.conf} · previsão venceu persistência em ${A.gate}/${A.n}`);
for (const [alvo, A] of Object.entries(agg)) { const n = A.n, f = v => (v / n).toFixed(3);
  p(`${alvo}: ruído exibido por variável/nível: ${Object.entries(A.fpVars).map(([k, v]) => k + '×' + v).join(', ') || 'nenhum'}`);
  p(`${alvo}: Brier médio em origem móvel — modelo ${f(A.bt.modelo)} · sem previsão ${f(A.bt.semPrev)} · nível+estádio ${f(A.bt.nivel)} · persistência 0/1 ${f(A.bt.pers)} · taxa-base ${f(A.bt.base)} · modelo vence nível+estádio em ${A.bt.venceNivel}/${n} · sem previsão vence persistência em ${A.bt.semPrevVencePers}/${n}`); }
p(`TOTAL réplicas: recuperados ${tot.hit}/${tot.tot} (${Math.round(100 * tot.hit / tot.tot)} %) · falso positivo forte/moderado ${tot.fp} · réplicas-alvo frias ${tot.frio}`);
p('por réplica: ' + dist.join(' | '));
p('');
p('== 3. Nulo do clima (série deslocada só na análise; toda variável de clima exibida é falsa) ==');
const CL = ['qs', 'tmax', 'ur', 'dpv', 'molh', 'chuva', 'lav', 'vento'];
for (const [k, rr] of Object.entries(R.nuloClima)) {
  const parts = [];
  for (const [alvo, o] of Object.entries(rr)) { if (o.frio) { parts.push(alvo + ': frio'); continue; } const cl = o.exibidos.filter(x => CL.includes(x.split(/[+-]/)[0])); const fm = cl.filter(x => /:(forte|moderada)/.test(x));
    parts.push(`${alvo}: clima exibido (todo falso) ${cl.join(',') || '-'} [Forte/Moderada: ${fm.length}] · outros ${o.exibidos.filter(x => !cl.includes(x)).join(',') || '-'} · gate ${o.gate && o.gate.ok}`); }
  p(k + ' → ' + parts.join(' || '));
}
const conta = blk => { let any = 0, fm = 0; for (const rr of Object.values(blk || {})) for (const o of Object.values(rr)) { if (o.frio) continue; const cl = o.exibidos.filter(x => CL.includes(x.split(/[+-]/)[0])); any += cl.length; fm += cl.filter(x => /:(forte|moderada)/.test(x)).length; } return { any, fm }; };
const n0 = conta(R.nuloClima), n1 = conta(R.nuloClimaSuave);
p(`Resumo do nulo (4 deslocamentos × 4 alvos): itens de clima exibidos (todos falsos) sem controle de época ${n0.any} (Forte/Moderada ${n0.fm}) · com tendência suave ${n1.any} (Forte/Moderada ${n1.fm})`);
p('');
p('== 4. Controle de época (lição: com 1 safra, controlar a época apaga o clima) ==');
for (const [ep, runs] of Object.entries(R.epoca || {})) {
  const A = {}; let H = 0, HFM = 0, T = 0, FP = 0, SH = 0;
  for (const [s, rr] of Object.entries(runs)) for (const [alvo, o] of Object.entries(rr)) { if (o.frio) continue; const a = A[alvo] = A[alvo] || { h: 0, fm: 0, t: 0, fp: 0, sh: 0, orig: null };
    a.h += o.hit; a.fm += o.hitFM; a.t += o.tot; a.fp += o.fp; a.sh += o.ruidoExibido.length; if (s === 'original') a.orig = `${o.hit}/${o.tot} (F/M ${o.hitFM}) · exibidos ${o.exibidos.join(' · ')}`;
    H += o.hit; HFM += o.hitFM; T += o.tot; FP += o.fp; SH += o.ruidoExibido.length; }
  p(`controle "${ep}" — 21 sementes: recuperados ${H}/${T} (${Math.round(100 * H / T)} %) · só Forte/Moderada ${HFM}/${T} (${Math.round(100 * HFM / T)} %) · falso positivo forte/moderado ${FP} · ruído exibido ${SH}`);
  for (const [alvo, a] of Object.entries(A)) p(`   ${alvo}: ${a.h}/${a.t} · F/M ${a.fm}/${a.t} · fp ${a.fp} · semente original: ${a.orig}`);
}
console.log(L.join('\n'));
