// Resumo legível de confronto.json (saída de confronto.mjs). Uso: node resumo.mjs <confronto.json>
import fs from 'node:fs';
const j = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const A = ['acaro', 'mosca', 'antrac', 'cochon'], o = j.original, reps = Object.values(j.replicas), todas = [o, ...reps];
const L = []; const p = s => L.push(s);
const soma = (fn) => todas.reduce((s, x) => s + fn(x), 0);
p(`fonte v3 · ${j.artefato.bytes} bytes · sha256 ${j.artefato.sha256} · node ${j.node}`);
p(`autoconferência: rxHT instrumentado igual ao do v3 (E e nCtrl em D = 30, 50, 70, 86): ${j.autoconferencia.rxHTigualSemInstrumentacao}`);
p(`semente original: gabarito ${A.map(a => a + ' ' + o.gabarito[a].hit + '/' + o.gabarito[a].tot).join(' · ')} · gate ${A.map(a => a + ' ' + o.gabarito[a].gate.bm + '×' + o.gabarito[a].gate.bp).join(' · ')}`);

p('\n== C1 · controle lido depois de D (contraprova 1 do Codex) ==');
p('fixture do Codex no rxHT extraído do v3 (D = 10):');
const f = o.c1Fixture; p(`  controles D1 = 10 e D12 = 10: E = ${f.controlesD1e12_iguais.E} com ${f.controlesD1e12_iguais.controlesComLeituraDepoisDeD} controles lidos depois de D`);
p(`  controles só com leitura até D: E = ${f.controlesSoAteD.E} (sem comparação válida)`);
p(`  só a leitura de D12 dos controles muda para 30: E = ${f.controlesD12triplicado.E}`);
p('dados do v3, toda data D de 1 a 86 da linha do tempo, rxHT × rxHT só com dados até D (semente original):');
A.forEach(a => { const c = o.c1Dados[a]; p(`  ${a}: ${c.eMudaComDadosAteD}/${c.itensData} item-data mudam E (${c.aplicacoesAfetadas} aplicações, ${c.datasAfetadas} datas) · viram "sem comparação" ${c.viraSemComparacaoValida} · maior |ΔE| ${c.maxDeltaEpp} p.p. · em D = 86: ${c.emD86}`); });
p(`21 sementes: item-data com controle lido depois de D ${soma(x => A.reduce((s, a) => s + x.c1Dados[a].usaControleLidoDepoisDeD, 0))} · E muda ${soma(x => A.reduce((s, a) => s + x.c1Dados[a].eMudaComDadosAteD, 0))} · em D = 86 ${soma(x => A.reduce((s, a) => s + x.c1Dados[a].emD86, 0))} · maior |ΔE| ${Math.max(...todas.flatMap(x => A.map(a => x.c1Dados[a].maxDeltaEpp)))} p.p.`);

p('\n== C3 · nível de pareamento usado pelo rxHT em D = 86 (contraprova 3 do Codex) ==');
A.forEach(a => { const c = o.c3[a]; p(`  ${a}: ${c.aplicacoesComAntesDepois} aplicações · nível 1 (estádio e nível) ${c.nivel1_estadioENivel} · nível 2 (só estádio) ${c.nivel2_soEstadio} · nível 3 (qualquer candidato) ${c.nivel3_qualquerCandidato} · sem comparação ${c.semComparacaoValida} · regra estrita da crítica: válidas ${c.regraEstritaClaude_valida}, sem comparação ${c.regraEstritaClaude_semComparacao}, leitura do dia excluída ${c.antesNoMesmoDia_excluidas}`); });
const t3 = x => A.reduce((s, a) => s + x.c3[a].nivel3_qualquerCandidato, 0), tt = x => A.reduce((s, a) => s + x.c3[a].aplicacoesComAntesDepois, 0), t0 = x => A.reduce((s, a) => s + x.c3[a].semComparacaoValida, 0);
p(`semente original: ${t3(o)}/${tt(o)} aplicações só chegam a 2 controles pelo nível 3; sem comparação ${t0(o)}`);
p(`21 sementes: nível 3 ${soma(t3)}/${soma(tt)} · sem comparação ${soma(t0)} · regra estrita sem comparação ${soma(x => A.reduce((s, a) => s + x.c3[a].regraEstritaClaude_semComparacao, 0))}`);

p('\n== C4 · seguimento do NC (EX-42 §8) × "dias de proteção" do v3, D = 86 ==');
A.forEach(a => { const c = o.c4[a]; p(`  ${a}: ${c.itens} itens · v3 eventos ${c.v3_eventos}, censurados ${c.v3_censurados} · retorno demonstrado ${c.retornoDemonstrado} (intervalo ${c.larguraDoIntervaloDeRetorno_dias.min}–${c.larguraDoIntervaloDeRetorno_dias.max} dias) · 1ª leitura pós já acima ${c.v3EventoSemLeituraAbaixo} · seguiu abaixo até a última leitura ${c.seguiuAbaixoAteUltimaLeitura} (v3 acrescenta ${c.diasAcrescidosPorCensurarEmD.min}–${c.diasAcrescidosPorCensurarEmD.max} dias, média ${c.diasAcrescidosPorCensurarEmD.media}) · outra aplicação no seguimento ${c.outraAplicacaoNoSeguimento}`); });
p(`21 sementes: 1ª leitura pós já acima do NC ${soma(x => A.reduce((s, a) => s + x.c4[a].v3EventoSemLeituraAbaixo, 0))} · outra aplicação no seguimento ${soma(x => A.reduce((s, a) => s + x.c4[a].outraAplicacaoNoSeguimento, 0))} de ${soma(x => A.reduce((s, a) => s + x.c4[a].itens, 0))} itens`);

p('\n== C2 · teste da previsão (contraprova 2 do Codex), desenho do gate do v3: corte D − 21, D = 86 ==');
A.forEach(a => { const c = o.c2Gate[a]; p(`  ${a}: n ${c.n}, eventos ${c.eventos} · variáveis de janela no teste com dias depois da 1ª vistoria: ${c.comDiasDepoisDaOrigem}/${c.variaveisDeJanela}`);
  ['v3_climaRealizado', 'climaPosCorteTrocadoPor35DiasAntes', 'honesto_tempoDosDiasAntesDaOrigem', 'climatologia4Semanas', 'previsaoMetadeDosDiasCerta'].forEach(k => p(`     ${k.padEnd(36)} Brier modelo ${c[k].brierModelo} × persistência ${c[k].brierPersistencia} → ${c[k].ok ? 'vence' : 'perde'}`)); });
p('21 sementes, quantas vezes o modelo vence a persistência no gate do v3:');
['v3_climaRealizado', 'honesto_tempoDosDiasAntesDaOrigem', 'climatologia4Semanas', 'previsaoMetadeDosDiasCerta'].forEach(k => p(`  ${k.padEnd(36)} ${A.map(a => a + ' ' + todas.filter(x => x.c2Gate[a] && x.c2Gate[a][k] && x.c2Gate[a][k].ok).length + '/' + todas.filter(x => x.c2Gate[a] && x.c2Gate[a][k]).length).join(' · ')}`));
p('conjunto de teste condicionado ao futuro (pares candidatos com fim no teste, excluídos por aplicação entre as vistorias):');
A.forEach(a => { const c = o.c2SelecaoTeste[a]; p(`  ${a}: ${c.excluidosPorAplicacaoDepoisDaOrigem}/${c.paresCandidatos} excluídos por aplicação depois da 1ª vistoria (com nível ≥ 90 % do NC na origem: ${c.dessesComNivelNaOrigemAcimaDe90pctNC}; abaixo do NC: ${c.dessesAbaixoDoNCnaOrigem}) · ${c.excluidosPorAplicacaoAteOrigem} por aplicação até a origem`); });
p(`21 sementes: excluídos por aplicação depois da origem ${soma(x => A.reduce((s, a) => s + x.c2SelecaoTeste[a].excluidosPorAplicacaoDepoisDaOrigem, 0))}/${soma(x => A.reduce((s, a) => s + x.c2SelecaoTeste[a].paresCandidatos, 0))}, desses abaixo do NC na origem ${soma(x => A.reduce((s, a) => s + x.c2SelecaoTeste[a].dessesAbaixoDoNCnaOrigem, 0))}`);
p('"Próximos 7 dias" numa data passada (semente original): trocar só o clima depois de D pelo de 35 dias antes:');
A.forEach(a => p(`  ${a}: ` + o.c2Tela[a].map(c => `D${c.D} ${c.probMudouTrocandoSoClimaDepoisDeD}/${c.talhoesComRisco} talhões mudam, até ${c.maxDeltaPp} p.p.`).join(' · ')));
const m = o.c2Manejo; p(`manejo depois da origem (D = ${m.origem}, ${m.talhao}): +70 mm de irrigação no dia ${m.depoisDeSomar70mmNoDia} muda a irrigação da janela de ${m.irrigacaoJanela0_antes} para ${m.irrigacaoJanela0_depois} mm/semana · ${m.adubacoesNos7DiasSeguintes} adubações em ${m.talhoesComAdubacao} talhões caem na janela (D, D + 7]`);

p('\n== C5 · seleção refeita em cada uma de 200 reamostras (semente original, D = 86) ==');
A.forEach(a => { o.c5[a].linhas.filter(l => l.plantado).forEach(l => p(`  ${a} ${l.k.padEnd(5)} plantado ${l.plantado > 0 ? 'sobe' : 'desce'} · v3 ${String(l.nivelV3).padEnd(20)} IC95 v3 [${l.ic95v3_fixo}] · com seleção refeita [${l.ic95_selecaoRefeita}] → exclui zero com o sinal certo: ${l.excluiZeroComSinalCerto ? 'sim' : 'não'}`)); });
const ex = o => A.reduce((s, a) => s + o.c5[a].linhas.filter(l => l.plantado && l.excluiZeroComSinalCerto).length, 0);
const ruidoEx = A.reduce((s, a) => s + o.c5[a].linhas.filter(l => !l.plantado && !l.proxy && l.excluiZero).length, 0);
p(`efeitos plantados com IC95 (seleção refeita) sem o zero e sinal certo: ${ex(o)}/14 · variáveis de ruído com IC95 sem o zero: ${ruidoEx}`);

p('\n== C6 · o "nulo do clima" da crítica: clima deslocado × clima verdadeiro (Spearman) ==');
Object.entries(o.c6Nulo.diario).forEach(([k, v]) => p(`  diário ${k}: tmax ${v.tmax} · ur ${v.ur} · chuva ${v.chuva}`));
Object.entries(o.c6Nulo.janela0).forEach(([k, v]) => p(`  janela 0 ${k}: ` + A.map(a => a + ' qs ' + v[a].qs + ' tmax ' + v[a].tmax + ' lav ' + v[a].lav).join(' | ')));

p('\n== C7 · contrato do backtest em origem móvel da crítica (raiox_repro.mjs, backtest) ==');
A.forEach(a => { const c = o.c7Backtest[a]; p(`  ${a}: ${c.paresDeTeste} pares de teste · 1ª vistoria depois da origem ${c.d1DepoisDaOrigem} · horizonte (2ª vistoria − origem) em dias: ${Object.entries(c.horizonteD2menosOrigem).map(([h, n]) => h + 'd ' + n).join(', ')}`); });
console.log(L.join('\n'));
