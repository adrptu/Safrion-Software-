// Q2 · conferência numérica da ressalva 2 da consolidação do Codex (bff2e0e) sobre o Henderson-Tilton (HT).
// Uso: node q2_ht.mjs > q2_ht.txt   (sem dependências; aritmética IEEE-754 do Node; dados sintéticos mínimos)
// Nomes sem letra ambígua: T_antes, T_depois (talhão tratado), C_antes, C_depois (controle).
//   PED:121 (pedido, 529adf7):      E = 1 − (Td × Ca) ÷ (Ta × Cd), com a = ANTES e d = depois.
//   Consolidação (bff2e0e, item 2): E = 1 − (Ta × Cb) ÷ (Tb × Ca), com a = AFTER (depois) e b = before (antes).
//   A mesma letra "Ca" é o controle ANTES no pedido e o controle DEPOIS na consolidação.
const L = [], log = s => L.push(s);
const f = v => Number.isNaN(v) ? 'NaN (0 ÷ 0)' : v === Infinity ? '+Infinito (÷ 0)' : v === -Infinity ? '−Infinito (÷ 0)' : (Math.round(v * 1e6) / 1e6).toString();
// Forma de produto (a escrita do PED:121 e da consolidação)
const htProduto = ({ Ta0, Ta1, Ca0, Ca1 }) => 1 - (Ta1 * Ca0) / (Ta0 * Ca1);
// Forma de razão de fatores: o estimando "fator do tratado ÷ fator do controle"
const fatorT = ({ Ta0, Ta1 }) => Ta1 / Ta0, fatorC = ({ Ca0, Ca1 }) => Ca1 / Ca0;
const htRazao = k => 1 - fatorT(k) / fatorC(k);
// v3 (ART:628 e :631): ε = 5 % do NC somado a cada leitura; o controle só entra se C_antes ≥ 10 % do NC (o tratado não tem piso)
const htEps = (k, eps) => 1 - ((k.Ta1 + eps) / (k.Ta0 + eps)) / ((k.Ca1 + eps) / (k.Ca0 + eps));
const abbott = ({ Ta1, Ca1 }) => 1 - Ta1 / Ca1;
const caso = (nome, k, nc) => { const eps = nc ? .05 * nc : null;
  log(`${nome}: T ${k.Ta0} → ${k.Ta1}; C ${k.Ca0} → ${k.Ca1}`);
  log(`  produto: E = ${f(htProduto(k))} · fator do tratado = ${f(fatorT(k))} · fator do controle = ${f(fatorC(k))} · razão: E = ${f(htRazao(k))}`);
  if (eps != null) log(`  com ε = ${eps} (5 % de NC ${nc}, como o v3): E = ${f(htEps(k, eps))}`); };

log('== K1 · contraprova da consolidação (item 2): T_antes 10, T_depois 5, C_antes 0, C_depois 10');
caso('K1', { Ta0: 10, Ta1: 5, Ca0: 0, Ca1: 10 }, 10);
log('  Leitura: na forma de produto C_antes está no numerador e E = 1 (100 %), sem divisão por zero, como diz a consolidação.');
log('  Na forma de razão, que é o estimando (fator do tratado ÷ fator do controle), o fator do controle é 10 ÷ 0: divisão por zero.');

log('\n== K2 · com C_antes = 0, E não depende do tratado (não identificação)');
[0, 5, 10, 50, 1000].forEach(t => { const k = { Ta0: 10, Ta1: t, Ca0: 0, Ca1: 10 }; log(`  T 10 → ${t}: E produto = ${f(htProduto(k))}`); });
log('  O tratado sobe 100 vezes (10 → 1000) e E continua 100 %. O resultado não carrega informação sobre o tratado.');

log('\n== K3 · exemplo do pacote ao Gemini (Q2): tratado 0 → 2, controles 10 → 10 (o zero é T_antes, não C_antes)');
caso('K3', { Ta0: 0, Ta1: 2, Ca0: 10, Ca1: 10 }, 10);

log('\n== K4 · C_depois = 0');
caso('K4a', { Ta0: 10, Ta1: 5, Ca0: 10, Ca1: 0 }, 10);
caso('K4b', { Ta0: 10, Ta1: 0, Ca0: 10, Ca1: 0 }, 10);

log('\n== K5 · controle zerado antes e depois');
caso('K5', { Ta0: 10, Ta1: 5, Ca0: 0, Ca1: 0 }, 10);

log('\n== K6 · caso regular do pacote: tratado 10 → 5, controles 10 → 10');
caso('K6', { Ta0: 10, Ta1: 5, Ca0: 10, Ca1: 10 }, 10);

log('\n== K7 · tratado zerado depois (resultado legítimo de 100 %, que o ε rebaixa)');
caso('K7', { Ta0: 10, Ta1: 0, Ca0: 10, Ca1: 10 }, 10);

log('\n== K8 · a frase "Ca = 0 é divisor" muda de verdade conforme a notação');
{ const kCod = { Ta0: 10, Ta1: 5, Ca0: 10, Ca1: 0 }, kPed = { Ta0: 10, Ta1: 5, Ca0: 0, Ca1: 10 };
  log(`  notação da consolidação (Ca = controle depois) com Ca = 0: E = ${f(htProduto(kCod))} → divisor, verdadeiro`);
  log(`  notação do PED:121 (Ca = controle antes) com Ca = 0: E = ${f(htProduto(kPed))} → não é divisor; E = 100 % para qualquer tratado`); }

log('\n== K9 · C_antes perto de zero (sem ser zero): o tratado quintuplica e E sai alto');
caso('K9', { Ta0: 10, Ta1: 50, Ca0: 0.1, Ca1: 10 }, null);
log('  Zero exato é regra estrutural; "perto de zero" é precisão e pede piso do protocolo (pendente). O v3 tem piso de 10 % do NC só no controle (ART:628).');

log('\n== K10 · HT é diferença de diferenças em escala log: ln(1 − E) = [ln T_depois − ln T_antes] − [ln C_depois − ln C_antes]');
{ let s = 2463534242, mx = 0; const rnd = () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
  for (let i = 0; i < 1000; i++) { const k = { Ta0: .01 + 100 * rnd(), Ta1: .01 + 100 * rnd(), Ca0: .01 + 100 * rnd(), Ca1: .01 + 100 * rnd() };
    const lhs = Math.log(1 - htProduto(k)), rhs = (Math.log(k.Ta1) - Math.log(k.Ta0)) - (Math.log(k.Ca1) - Math.log(k.Ca0)); mx = Math.max(mx, Math.abs(lhs - rhs)); }
  log(`  1000 quádruplas positivas sorteadas (xorshift, semente fixa): maior |diferença| = ${mx.toExponential(2)}`);
  log('  Logo o HT já pressupõe tendências paralelas na escala log (mesmo fator de mudança sem a aplicação). "Migrar para DiD" não troca de pressuposto.'); }

log('\n== K11 · com T_antes = C_antes, HT coincide com Abbott (HT generaliza Abbott a níveis de partida diferentes)');
[[10, 4, 10, 8], [3, 1, 3, 6], [7, 0, 7, 5]].forEach(([a, b, c, d]) => { const k = { Ta0: a, Ta1: b, Ca0: c, Ca1: d };
  log(`  T ${a} → ${b}, C ${c} → ${d}: HT = ${f(htProduto(k))} · Abbott = ${f(abbott(k))}`); });
{ const k = { Ta0: 20, Ta1: 10, Ca0: 5, Ca1: 10 }; log(`  níveis de partida diferentes, T 20 → 10, C 5 → 10: HT = ${f(htProduto(k))} · Abbott = ${f(abbott(k))} (Abbott ignora que o tratado partiu do quádruplo)`); }

log('\n== Regra que decorre (especificada no RX-0, EST-3a): T_antes > 0, C_antes > 0 em cada controle e C_depois > 0 no agregado;');
log('   senão "sem comparação válida" com o motivo (tratado zerado antes · controle zerado antes · controle zerado depois). T_depois = 0 é válido (E = 100 %, "zero observado depois").');
console.log(L.join('\n'));
