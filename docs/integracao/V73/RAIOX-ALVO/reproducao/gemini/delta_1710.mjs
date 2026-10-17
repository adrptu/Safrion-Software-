// Δ 17/10 · aritmética dos ajustes pedidos pelo Codex (PR #47, comentário 6227947437) ao contrato RX-0 proposto em 0de5a28.
// Uso: node delta_1710.mjs > delta_1710.txt   (sem dependências; dados sintéticos mínimos; não usa o v3)
//   A · ADV-01: ramos por data de corte (D = 10 e D = 12) e pela variante do controle depois (10 ou 30), sem ε.
//   B · ORA-05: cruzamentos do nível latente (queda, retorno após a queda, todos os cruzamentos para cima) em duas fixtures sem ruído.
//   C · K10: a identidade HT × contraste de logs só vale no domínio positivo.
const L = [], log = s => L.push(s), f10 = v => Number.isFinite(v) ? v.toFixed(10) : String(v);
const ht = (Ta0, Ta1, Ca0, Ca1) => 1 - (Ta1 / Ta0) / (Ca1 / Ca0);

log('== A · ADV-01: tratado d1 = 10 → d10 = 5; controles C1 e C2 com d1 = 10 e d12 = Cd (t_disp = t_evento); NC 10; sem ε');
for (const Cd of [10, 30]) for (const D of [10, 12]) {
  const temDepois = 12 <= D;   // a leitura d12 do controle só existe para o corte D se t_evento ≤ D e t_disp ≤ D (T1)
  log(`  Cd = ${Cd}, D = ${D}: ` + (temDepois ? `E = ${f10(ht(10, 5, 10, Cd))} (fator do controle ${Cd / 10})` : 'sem comparação válida: controle sem leitura depois até D'));
}
log('  Invariância: em D = 10 as duas variantes dão a mesma saída (a leitura d12 ainda não existe para o corte).');
log('  Em D = 12 a saída muda com Cd, como deve: 0,5 com Cd = 10 e 0,8333333333 com Cd = 30.');
log('  Contraprova (R-C1, executado no confronto): o rxHT do v3 já em D = 10 dá 0,4762 e 0,8197, porque lê o controle de d12.');

log('\n== B · ORA-05: nível latente sem ruído de medida; NC 10; aplicação em d2');
const cruz = (x, nc, tAp) => { // x: {dia: valor}; devolve queda, retorno após a queda, todos os cruzamentos para cima depois da queda e o 1º dia ≥ NC depois da aplicação
  const dias = Object.keys(x).map(Number).sort((a, b) => a - b).filter(d => d >= tAp);
  const prim = dias.find(d => d > tAp && x[d] >= nc) ?? null, queda = dias.find(d => x[d] < nc) ?? null; const sobe = [];
  if (queda != null) dias.forEach((d, i) => { if (d > queda && x[d] >= nc && x[dias[i - 1]] < nc) sobe.push(d); });
  return { primeiroDiaAcimaDepoisDaAplicacao: prim, queda, retornoAposQueda: sobe[0] ?? null, cruzamentosParaCimaAposQueda: sobe }; };
const s1 = (x, leituras, nc) => { const v = leituras.map(d => [d, x[d]]); for (let k = 1; k < v.length; k++) if (v[k - 1][1] < nc && v[k][1] >= nc) return [v[k - 1][0], v[k][0]]; return null; };
{ // B1: queda na aplicação e crescimento ×1,15 por dia; leituras d9 e d16
  const x = {}; for (let d = 1; d <= 16; d++) x[d] = d < 2 ? 12 : 3 * Math.pow(1.15, d - 2);
  const c = cruz(x, 10, 2), iv = s1(x, [1, 9, 16], 10);
  log(`  B1 crescimento ×1,15/dia desde 3 em d2: x(d10) = ${x[10].toFixed(4)}, x(d11) = ${x[11].toFixed(4)}; leituras d9 = ${x[9].toFixed(4)}, d16 = ${x[16].toFixed(4)}`);
  log(`     S1 = (d${iv[0]}, d${iv[1]}]; ${JSON.stringify(c)}`);
  log(`     retorno após queda dentro do intervalo de S1: ${c.retornoAposQueda > iv[0] && c.retornoAposQueda <= iv[1]}; algum cruzamento para cima no intervalo: ${c.cruzamentosParaCimaAposQueda.some(d => d > iv[0] && d <= iv[1])}`); }
{ // B2: excursão acima do NC entre leituras, não observada
  const x = { 1: 12, 2: 3, 3: 6, 4: 9, 5: 11, 6: 11, 7: 8, 8: 7, 9: 7, 10: 8, 11: 9, 12: 9.5, 13: 10.5, 14: 12, 15: 13, 16: 14 };
  const c = cruz(x, 10, 2), iv = s1(x, [1, 9, 16], 10);
  log(`  B2 excursão: x = ${JSON.stringify(x)}; leituras d9 = ${x[9]}, d16 = ${x[16]}`);
  log(`     S1 = (d${iv[0]}, d${iv[1]}]; ${JSON.stringify(c)}`);
  log(`     retorno após queda dentro do intervalo de S1: ${c.retornoAposQueda > iv[0] && c.retornoAposQueda <= iv[1]}; algum cruzamento para cima no intervalo: ${c.cruzamentosParaCimaAposQueda.some(d => d > iv[0] && d <= iv[1])}`); }
{ // B3: a aplicação não leva o latente abaixo do NC
  const x = { 1: 30, 2: 14, 3: 13, 4: 13, 5: 14, 6: 15, 7: 16, 8: 17, 9: 18 };
  const c = cruz(x, 10, 2);
  log(`  B3 sem queda: x = ${JSON.stringify(x)}; ${JSON.stringify(c)}`);
  log('     "primeiro dia acima depois da aplicação" existe (d3), mas não há queda nem retorno: S2 "retorno não demonstrado" é o estado certo.'); }
log('  Sem ruído de medida, a invariante é "algum cruzamento para cima em (t_(k−1), t_k]" (B1 e B2 verdadeiros).');
log('  "Retorno após queda dentro do intervalo" não é invariante (B2 falso): é medida de cobertura, como qualquer contenção com leitura ruidosa.');

log('\n== C · K10 fora do domínio positivo: ln(1 − E) × [ln T_depois − ln T_antes] − [ln C_depois − ln C_antes]');
[[10, 0, 10, 10], [0, 2, 10, 10], [10, 5, 0, 10], [10, 5, 10, 0]].forEach(([a, b, c, d]) => {
  const E = 1 - (b * c) / (a * d), lhs = Math.log(1 - E), rhs = (Math.log(b) - Math.log(a)) - (Math.log(d) - Math.log(c));
  log(`  T ${a} → ${b}, C ${c} → ${d}: E = ${E}; ln(1 − E) = ${lhs}; contraste de logs = ${rhs}`); });
log('  Com algum zero, um lado ou os dois saem infinitos ou NaN: a identidade de K10 só foi demonstrada para valores positivos.');
log('  Ela é álgebra de um par antes/depois: não prova identificação causal, tendência paralela, nem equivalência a qualquer estimador DiD.');
console.log(L.join('\n'));
