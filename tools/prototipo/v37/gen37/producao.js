// ===== Produção · colheita de ponta a ponta (docs/colheita/ESPECIFICACAO.md v1.1; decisões em docs/colheita/DECISOES.md) =====
// Regras e comandos pr* sobre o cenário compartilhado (c.producao). Fórmula num lugar só (ENG-011): unidade da cultura, descontos de
// grão, matéria seca, rateio da mistura, área colhida, produtividade, qualidade efetiva do lote, saldos, oferta e previsão.
// Decimal (ENG-013): quantidade na base do lote (kg, frutos ou L) com 6 casas, meio para cima, por BigInt; nunca soma de float.
// Carregado por cenario.js_prefixo() depois de cenario.js (D-22): toda página do estado tem as regras. O que lê a carência (CARD) só
// roda onde o núcleo da carência existe (Produção, O.S., Mapa, VE-04); o app tem o núcleo leve e não decide qualidade de lote.
// Comentários só com /* */ ou // em linha própria: este arquivo também entra em strings Python.

/* ---------- decimal: micro-unidades (10^-6) em BigInt ---------- */
const PR_S = 1000000n;
function prM(x) {   /* número ou texto → BigInt em milionésimos, meio para cima */
  if (typeof x === 'bigint') return x;
  const d = cenDec(x); if (!d) throw new Error('Número inválido: ' + x + '.');
  let n = d.n; const e = d.e; if (e <= 6) return n * (10n ** BigInt(6 - e));
  const k = 10n ** BigInt(e - 6); const neg = n < 0n; if (neg) n = -n; const q = (n * 2n + k) / (2n * k); return neg ? -q : q; }
function prN(m) { const neg = m < 0n; const a = (neg ? -m : m).toString().padStart(7, '0'); return Number((neg ? '-' : '') + a.slice(0, -6) + '.' + a.slice(-6)); }
function prRd(num, den) {   /* num ÷ den arredondado (meio para cima, simétrico) */
  if (den === 0n) throw new Error('Divisão por zero.'); if (den < 0n) { num = -num; den = -den; }
  const neg = num < 0n; if (neg) num = -num; const q = (num * 2n + den) / (2n * den); return neg ? -q : q; }
function prSoma(xs) { return prN((xs || []).reduce((a, x) => a + prM(x || 0), 0n)); }
function prSub(a, b) { return prN(prM(a) - prM(b)); }
function prMul(a, b) { return prN(prRd(prM(a) * prM(b), PR_S)); }
function prDiv(a, b) { return prN(prRd(prM(a) * PR_S, prM(b))); }
function prMulDiv(a, b, c) { return prN(prRd(prM(a) * prM(b), prM(c))); }   /* a × b ÷ c com um arredondamento só */
function prCmp(a, b) { const x = prM(a), y = prM(b); return x < y ? -1 : (x > y ? 1 : 0); }
/* texto pt-BR com d casas fixas (prFmt) ou até d casas sem zeros à direita (prFmtT); arredondamento decimal, não de float */
function prFmt(x, d) { d = d === undefined ? 2 : d; const m = prRd(prM(x), 10n ** BigInt(6 - d)); const neg = m < 0n;
  const s = (neg ? -m : m).toString().padStart(d + 1, '0'); const ip = (d ? s.slice(0, -d) : s).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); const fp = d ? s.slice(-d) : '';
  return (neg ? '−' : '') + ip + (fp ? ',' + fp : ''); }
function prFmtT(x, d) { const t = prFmt(x, d === undefined ? 3 : d); return t.indexOf(',') < 0 ? t : t.replace(/0+$/, '').replace(/,$/, ''); }

/* ---------- unidade da cultura (DEC-0510-03; fonte única: CULTURA_UN em dados_cad.py, D-03) ---------- */
function prCult(nome) { const C = PRDC.un; if (C[nome]) return nome; const k = Object.keys(C).find(x => String(nome || '').indexOf(x) === 0); return k || String(nome || ''); }
function prUn(cultura) { const u = PRDC.un[prCult(cultura)]; if (!u) throw new Error('Cultura sem unidade de mercado no cadastro: ' + cultura + '.'); return u; }
/* base (kg, frutos) → unidade de produção da cultura: 2.305.200 kg de soja = 38.420 sc; 60.320 kg de mamão = 60,32 t */
function prQ(cultura, base) { return prDiv(base, prUn(cultura).massa); }
function prUnTxt(cultura, base, d) { const u = prUn(cultura); return prFmtT(prQ(cultura, base), d === undefined ? 2 : d) + ' ' + u.un; }
/* estoque e pedido: unidade de estoque (est) quando a cultura tem uma (mamão em kg, coco em fruto); senão a de produção */
function prEstUn(cultura) { const u = prUn(cultura); return u.est || u.un; }
function prEstQ(cultura, base) { const u = prUn(cultura); return u.est ? prN(prM(base)) : prQ(cultura, base); }
function prEstTxt(cultura, base, d) { return prFmtT(prEstQ(cultura, base), d === undefined ? 2 : d) + ' ' + prEstUn(cultura); }
function prEstBase(cultura, q) { const u = prUn(cultura); return u.est ? prN(prM(q)) : prMul(q, u.massa); }   /* quantidade digitada na unidade de estoque → base */
/* produtividade = produção na base física ÷ área colhida, na unidade da cultura (R-04); laranja mostra t/ha ao lado */
function prPrtv(cultura, base, ha) { if (!(Number(ha) > 0)) return null; return prDiv(prQ(cultura, base), ha); }
function prPrtvTxt(cultura, base, ha) { const u = prUn(cultura); const p = prPrtv(cultura, base, ha); if (p === null) return '—';
  return prFmt(p, 2) + ' ' + u.prtv + (u.lado ? ' · ' + prFmt(prDiv(prDiv(base, 1000), ha), 2) + ' ' + u.lado : ''); }

/* ---------- grão: descontos (R-08) e matéria seca (função única, a mesma da BEN-3 como benEst) ---------- */
function prMs(kg, u, up) { const U = prM(u), UP = prM(up); const H = 100n * PR_S; return prN(prRd(prM(kg) * (H - U), H - UP)); }
function prCorrigir(liq, u, imp, up, ip) {   /* impureza acima do padrão primeiro; umidade sobre o limpo; sem bônus abaixo do padrão (D-07) */
  const L = prM(liq), I = prM(imp), IP = prM(ip); const H = 100n * PR_S; const d = I > IP ? I - IP : 0n;
  const limpo = prN(prRd(L * (H - d), H)); const com = prCmp(u, up) > 0 ? prMs(limpo, u, up) : limpo;
  return { liq: prN(L), limpo, com, dImp: prSub(liq, limpo), dUmid: prSub(limpo, com) }; }
/* rateio acumulado da mistura (BEN §3.3): kg_i = q6(S·acum_i/E) − q6(S·acum_{i−1}/E); o último leva o resto, a soma fecha em S */
function prRateio(S, pcts) { const s = prM(S); const P = (pcts || []).map(prM); const E = P.reduce((a, b) => a + b, 0n);
  if (E <= 0n) throw new Error('Participação sem total.'); let acc = 0n, prev = 0n;
  return P.map(p => { acc += p; const cur = prRd(s * acc, E); const k = cur - prev; prev = cur; return prN(k); }); }

/* ---------- semana ISO (lote, previsão, passe) ---------- */
function prSem(iso) { const d = new Date(String(iso).slice(0, 10) + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 6) % 7) + 3);
  const y = d.getUTCFullYear(); const w = Math.floor((d - Date.UTC(y, 0, 1, 12)) / 86400000 / 7) + 1; return y + '-W' + String(w).padStart(2, '0'); }
function prSemN(k) { return Number(String(k).slice(-2)); }
function prSemTxt(k) { return 'S' + String(k).slice(-2); }
function prSemIni(k) { const y = Number(String(k).slice(0, 4)), w = prSemN(k); const j4 = new Date(Date.UTC(y, 0, 4, 12));
  j4.setUTCDate(j4.getUTCDate() - ((j4.getUTCDay() + 6) % 7) + (w - 1) * 7); return j4.toISOString().slice(0, 10); }
function prSemMais(k, n) { const d = new Date(prSemIni(k) + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + 7 * n); return prSem(d.toISOString().slice(0, 10)); }
function prDiaMais(iso, n) { const d = new Date(String(iso).slice(0, 10) + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); }
function prBr(iso) { const a = String(iso || '').split('-'); return a.length === 3 ? a[2] + '/' + a[1] : String(iso || '—'); }
