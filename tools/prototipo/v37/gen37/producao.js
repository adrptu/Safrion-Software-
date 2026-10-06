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

/* =====================================================================================================================
   Estado c.producao (§5) · leitura
   ===================================================================================================================== */
const PR_FASES_COLH = ['Liberadas', 'Em execução', 'Em conferência'];   /* origem de carga (R-06) */
const PR_FEZ = ['Liberadas', 'Em execução', 'Em conferência', 'Encerradas'];  /* ordem de colheita autorizada na data (R-12) */
/* leitura não cria nada no estado; comando (w) cria a parte da produção num estado antigo que não a tinha */
function prP(c, w) { if (c.producao) return c.producao; const e = { contagens: [], previsoes: {}, cargas: {}, lotes: {}, pedidos: {}, reservas: {}, movs: [], seq: { cg: 2100, lote: {}, rs: 0, mp: 1000, cnt: 0 } }; if (w) c.producao = e; return e; }
function prHoje() { return typeof CEN_DIA_OP !== 'undefined' ? CEN_DIA_OP : '2026-09-26'; }
function prQuem(k) { return (PRDC.quem || {})[k] || ''; }
function prRec(faz) { return ((PRDC.quem || {}).rec || {})[faz] || 'Recebimento'; }
function prEhColheita(o) { return /^Colheita/.test(String((o && o.tipo) || '')); }
/* cultivo da O.S.: a ordem nova guarda o cultivo (#nova:); a semente vem do registro; senão o 1º cultivo aberto do talhão */
function prCultDaOS(c, o) { if (!o) return ''; const nv = o.osc && o.osc.novo; if (nv && nv.cult) return nv.cult;
  if ((PRDC.osCult || {})[o.id]) return PRDC.osCult[o.id]; return ((PRDC.cultDe || {})[o.talhao] || [])[0] || ''; }
function prFazDaOS(c, o) { const k = PRDC.cult[prCultDaOS(c, o)]; return (o && o.osc && o.osc.novo && o.osc.novo.faz) || (k && k.faz) || ''; }
function prOsCult(c, cid) { return Object.keys(c.ordens || {}).map(k => c.ordens[k]).filter(o => prEhColheita(o) && o.etapa !== 'Canceladas' && prCultDaOS(c, o) === cid); }
function prDdMm(iso) { const a = String(iso || '').split('-'); return a.length === 3 ? a[2] + '/' + a[1] : ''; }
function prIsoDe(ddmm) { const m = /^(\d\d)\/(\d\d)$/.exec(String(ddmm || '')); return m ? prHoje().slice(0, 4) + '-' + m[2] + '-' + m[1] : ''; }
/* lote de campo (R-06): O.S. + dia do apontamento da mesma data (o mesmo id do motor de carência, carLid); sem apontamento, vazio */
function prLc(c, osId, dcol) { const o = (c.ordens || {})[osId]; if (!o || !dcol) return '';
  const a = (o.ap || []).find(x => x.d === prDdMm(dcol) && x.st !== 'Previsto' && x.st !== CEN_AP_DESC && x.st !== CEN_AP_DUP); if (!a) return '';
  if (typeof carLid === 'function') return carLid(osId, a.dia); const m = /^OS-(\d+)$/.exec(osId); return 'LC-' + (m ? m[1] : osId.replace(/[^A-Za-z0-9]/g, '')) + '-' + a.dia; }
/* semana do passe: "Colheita · semana 39" no tipo; senão a janela da ordem nova; senão o 1º apontamento */
function prSemDaOS(o) { const m = /semana (\d+)/.exec(String(o.tipo || '')); if (m) return prHoje().slice(0, 4) + '-W' + String(Number(m[1])).padStart(2, '0');
  const j = /(\d\d)\/(\d\d)/.exec(String((o.osc && o.osc.novo && o.osc.novo.janela) || o.janela || '')); if (j) return prSem(prHoje().slice(0, 4) + '-' + j[2] + '-' + j[1]);
  const a = (o.ap || []).find(x => x.st !== 'Previsto'); return a ? prSem(prIsoDe(a.d)) : prSem(prHoje()); }

/* ---------- cargas, produção e área colhida (R-02 a R-04) ---------- */
function prCargas(c, f) { return Object.values(prP(c).cargas).filter(g => !f || f(g)); }
function prCargasOS(c, osId) { return prCargas(c, g => (g.origem || []).some(x => x.os === osId)); }
/* pendentes da O.S.: carga a pesar (com ou sem sinal) */
function prAPesar(c, osId) { return prCargas(c, g => g.st === 'A pesar' && (g.origem || []).some(x => x.os === osId)); }
/* produção na base física da cultura (R-04): grão = comercial corrigido; fruta e cana = massa líquida; coco e abacaxi = frutos; café = a apurar */
function prProdOrig(x, cultura) { const u = prUn(cultura); if (u.base === 'beneficiado') return 0; return u.base === 'comercial' ? (x.com || 0) : (x.kg || 0); }
function prProdOS(c, osId) { const out = { kg: 0, liq: 0, com: 0, cafe: 0 }; let cult = '';
  prCargas(c, g => g.st === 'Recebida').forEach(g => (g.origem || []).filter(x => x.os === osId).forEach(x => { cult = g.cultura;
    out.kg = prSoma([out.kg, prProdOrig(x, g.cultura)]); out.liq = prSoma([out.liq, x.kg || 0]); out.com = prSoma([out.com, x.com || 0]); if (prUn(g.cultura).base === 'beneficiado') out.cafe = prSoma([out.cafe, x.litros || 0]); }));
  return out; }
function prAreaOS(o) { return prSoma((o.ap || []).filter(a => cenApSomado(a)).map(a => a.ha)); }
/* versão publicada que vale como referência do passe: a última publicada ANTES do início da semana (R-05, R-17) */
function prVersaoRef(c, cid, sem) { const ini = prSemIni(sem); const vs = (prP(c).previsoes[cid] || []).filter(v => v.d < ini && v.sem && v.sem[sem] !== undefined); return vs[vs.length - 1] || null; }
/* versão vigente de uma semana para oferta (a última publicada que traz a semana) */
function prVersaoSem(c, cid, sem) { const vs = (prP(c).previsoes[cid] || []).filter(v => v.sem && v.sem[sem] !== undefined); return vs[vs.length - 1] || null; }
function prPasse(c, o) { const cid = prCultDaOS(c, o); const k = PRDC.cult[cid] || {}; const sem = prSemDaOS(o); const p = prProdOS(c, o.id);
  const area = prAreaOS(o); const ap = prAPesar(c, o.id); const final = o.etapa === 'Encerradas' && !ap.length;
  const ref = prVersaoRef(c, cid, sem); const refKg = ref ? ref.sem[sem] : null;
  const desv = (final && refKg) ? prDiv(prMul(prSub(p.kg, refKg), 100), refKg) : null;
  return { os: o.id, o, cid, cultura: k.cultura, sem, fase: o.etapa, area, kg: p.kg, liq: p.liq, com: p.com, aPesar: ap, final, ref, refKg, desv,
           prtv: prPrtv(k.cultura || 'Mamão Formosa', p.kg, area) }; }
/* resultado do cultivo: passes (perene semanal), ciclo (área do cultivo, R-02 e D-11) ou safra (anual: mín(área, Σ ha)) */
function prResultado(c, cid) { const k = PRDC.cult[cid]; if (!k) return null; const u = prUn(k.cultura); const oss = prOsCult(c, cid);
  const passes = oss.map(o => prPasse(c, o)).sort((a, b) => a.sem < b.sem ? -1 : (a.sem > b.sem ? 1 : 0));
  const kg = prSoma(passes.map(p => p.kg)); const haSom = prSoma(passes.map(p => p.area)); const aPesar = [].concat(...passes.map(p => p.aPesar));
  const comecou = passes.some(p => prCmp(p.area, 0) > 0 || prCmp(p.kg, 0) > 0);
  let area, parcial, ref = null, desv = null;
  if (k.semanal) { area = comecou ? k.area : 0; const fim = (PRDC.safras[k.saf] || {}).fim || ''; parcial = !(fim && prHoje() > fim);
    if (!parcial && k.meta) { ref = k.meta; desv = prDiv(prMul(prSub(prPrtv(k.cultura, kg, area), k.meta), 100), k.meta); } }
  else { area = prCmp(haSom, k.area) > 0 ? k.area : haSom; parcial = !oss.length || oss.some(o => o.etapa !== 'Encerradas') || aPesar.length > 0;
    ref = k.meta || null; if (ref && area > 0) desv = prDiv(prMul(prSub(prPrtv(k.cultura, kg, area), ref), 100), ref); }
  const cafe = u.base === 'beneficiado' ? prSoma([].concat(...oss.map(o => [prProdOS(c, o.id).cafe]))) : 0;
  return { cid, k, u, passes, kg, area, parcial, ref, desv, aPesar, cafe, prtv: area > 0 ? prPrtv(k.cultura, kg, area) : null, comecou }; }
/* cultura (ou fazenda): Σ produção ÷ Σ área, ponderada; nunca média de médias (R-04, K07) */
function prPonderada(rs) { const v = rs.filter(r => r && r.area > 0); if (!v.length) return null; const cultura = v[0].k.cultura;
  const kg = prSoma(v.map(r => r.kg)), ha = prSoma(v.map(r => r.area)); return { kg, area: ha, prtv: prPrtv(cultura, kg, ha), parcial: v.some(r => r.parcial) }; }

/* ---------- previsão (R-17) ---------- */
function prContagem(c, cid) { const l = (prP(c).contagens || []).filter(x => x.cult === cid && x.sinc !== false); return l[l.length - 1] || null; }
function prParam(c, cid) { const v = (prP(c).previsoes[cid] || []).slice(-1)[0]; return { plantas_ha: (v && v.plantas_ha) || PRDC.fruta.plantas_ha, perda: (v && v.perda !== undefined ? v.perda : PRDC.fruta.perda) }; }
/* kg da semana pela contagem: área × plantas vivas/ha × (frutos do estádio ÷ plantas da amostra) × peso médio × (1 − perda), um arredondamento */
function prKgEstadio(area, plantasHa, frutos, plantas, peso, perda) { if (!(Number(plantas) > 0)) return 0;
  return prN(prRd(prM(area) * BigInt(Math.round(plantasHa)) * BigInt(Math.round(frutos)) * prM(peso) * (PR_S - prM(perda)), BigInt(Math.round(plantas)) * PR_S * PR_S)); }
function prRascunho(c, cid, par) { const k = PRDC.cult[cid]; if (!k) return null; const P = Object.assign(prParam(c, cid), par || {});
  if (k.semanal) { const n = prContagem(c, cid);
    if (n) { const S = prSem(n.d); const sem = {}; [['pintado', 0], ['devez', 1], ['verde', 2]].forEach(([e, i]) => { sem[prSemMais(S, i)] = prKgEstadio(k.area, P.plantas_ha, n[e], n.plantas, n.peso, P.perda); });
      return { base: 'contagem', cnt: n, sem, par: P }; }
    if (!k.meta) return null; const S = prSem(prHoje()); const kg = prDiv(prMul(prMul(k.area, k.meta), 1000), 52); const sem = {};
    [1, 2, 3].forEach(i => { sem[prSemMais(S, i)] = kg; }); return { base: 'meta', sem, par: P }; }
  if (!k.meta) return null; return { base: 'meta', safra: prMul(prMul(k.area, k.meta), prUn(k.cultura).massa) }; }
function prSemComecou(sem) { return prSemIni(sem) <= prHoje(); }
/* semanas publicáveis do rascunho: só as que ainda não começaram e mudam o que está publicado */
function prPublicavel(c, cid, par) { const r = prRascunho(c, cid, par); if (!r) return null; const vs = prP(c).previsoes[cid] || []; const ult = vs[vs.length - 1] || null;
  if (r.safra !== undefined) { const ini = (PRDC.cult[cid].colheita || ''); if (ult && ult.safra !== undefined && prCmp(ult.safra, r.safra) === 0) return null; if (ini && ini <= prHoje()) return null; return { safra: r.safra, base: r.base }; }
  const sem = {}; Object.keys(r.sem).filter(s => !prSemComecou(s)).forEach(s => { const v = prVersaoSem(c, cid, s); if (!v || prCmp(v.sem[s], r.sem[s]) !== 0) sem[s] = r.sem[s]; });
  return Object.keys(sem).length ? { sem, base: r.base, par: r.par, cnt: r.cnt ? r.cnt.id : '' } : null; }

/* ---------- lotes: qualidade efetiva e saldos (R-10, R-12, R-14) ---------- */
function prFis(c, lid) { return prSoma(prP(c).movs.filter(m => m.lote === lid && m.fis !== false).map(m => m.kg)); }
function prResLote(c, lid) { return prSoma(Object.values(prP(c).reservas).filter(r => r.lote === lid && r.st === 'Ativa').map(r => r.kg)); }
/* lotes de campo de origem (vivos: o LC- entra quando o apontamento da data existe) */
function prLcs(c, L) { const out = []; (L.origem || []).forEach(x => { if (x.est) return; const lc = prLc(c, x.os, x.dcol); if (lc && out.indexOf(lc) < 0) out.push(lc); }); return out; }
/* pós-colheita registrado no motor de carência (CAR0) sobre o lote de campo, na data do recebimento ou depois: fruta fora do vendável (D-23) */
function prOpPos(c, L) { if (typeof carOps !== 'function' || typeof CARD === 'undefined') return null; const lcs = prLcs(c, L);
  for (const op of carOps(c)) { const d = op.d || ''; if (d < (L.drec || '')) continue;
    if (op.k === 'pos' && lcs.indexOf(op.lote) >= 0) return { t: op.p + ' em ' + prBr(d) + ' (' + op.lote + ')', op };
    if ((op.k === 'mistura' || op.k === 'divisao') && (op.de || []).some(x => lcs.indexOf(x) >= 0)) {
      const de = (op.de || []).filter(x => lcs.indexOf(x) >= 0).join(', '); const nv = (op.novos || []).map(n => n.id).join(', ');
      return { t: (op.k === 'mistura' ? 'Misturado no ' + nv : 'Dividido em ' + nv) + ' em ' + prBr(d) + ' (' + de + ')', op }; } }
  return null; }
function prQualidade(c, L) {
  const loc = PRDC.locais[L.local] || {}; const u = prUn(L.cultura);
  if (u.campo && !L.benef) return { q: 'Em processo', mot: 'Café da roça em L: a saca sai do rendimento medido no beneficiamento (sc a apurar)', dono: 'Beneficiamento' };
  if ((PRDC.proc || []).indexOf(loc.tipo) >= 0) return { q: 'Em processo', mot: 'Recebido no ' + loc.nome + ' (' + loc.tipo + '): beneficiamento antes de vender', dono: 'Beneficiamento' };
  const op = prOpPos(c, L); if (op) return { q: 'Em processo', mot: op.t + ': fora do vendável até a ordem de processo', dono: 'Beneficiamento' };
  let pior = null;
  if (typeof CARD !== 'undefined' && typeof carEstado === 'function') {
    (L.origem || []).filter(x => !x.est).forEach(x => { const o = (c.ordens || {})[x.os];
      if (!o || PR_FEZ.indexOf(o.etapa) < 0) { if (!pior) pior = { q: 'Em inspeção', mot: 'Colheita sem ordem liberada (' + x.os + (o ? ' em ' + o.etapa : ' sem registro') + ')', dono: CARD.quem.ag }; return; }
      carTals(o.talhao).forEach(t => { const e = carEstado(c, t.tid, x.dcol, t.parc, x.dcol);
        if (e.k === 'curso') { const r = e.ativos[0]; pior = { q: 'Bloqueado', mot: 'Colhido em ' + prBr(x.dcol) + ' dentro da carência de ' + r.p + ' (' + r.os + ', aplicado em ' + carBr(r.d) + ', carência até ' + carAte(r.fim) + ')', dono: CARD.quem.ag, fim: r.fim }; }
        else if (e.k === 'insuf' && !(pior && pior.q === 'Bloqueado')) { const p = e.pend[0]; pior = { q: 'Em inspeção', mot: 'Carência sem dados suficientes: ' + p.t, dono: p.q || CARD.quem.ag }; } }); }); }
  if (pior) return pior;
  if (L.q0 === 'Liberado') return { q: 'Liberado', mot: L.lib ? 'Liberado por ' + L.lib.quem + ' em ' + prBr(L.lib.d) : 'Íntegro no recebimento', dono: '' };
  return { q: 'Em inspeção', mot: 'Recebido ' + String(L.cond || '').toLowerCase() + ': a Qualidade confere e libera', dono: prQuem('qual') }; }
function prSaldos(c, L) { const Q = prQualidade(c, L); const fis = prFis(c, L.id); const res = prResLote(c, L.id); const z = { fis, res, q: Q.q, mot: Q.mot, dono: Q.dono, fim: Q.fim, blq: 0, apto: 0, proc: 0, disp: 0 };
  if (Q.q === 'Em processo') z.proc = fis; else if (Q.q === 'Liberado') { z.apto = fis; z.disp = prCmp(fis, res) > 0 ? prSub(fis, res) : 0; } else z.blq = fis;
  z.esgotado = prCmp(fis, 0) <= 0; z.vencido = !!(L.validade && L.validade < prHoje()); return z; }

/* ---------- pedidos, reservas e oferta (R-15, R-16) ---------- */
function prExpedido(c, pid) { return prSoma(prP(c).movs.filter(m => m.tipo === 'expedição' && m.pedido === pid).map(m => -m.kg)); }
function prResPed(c, pid) { return Object.values(prP(c).reservas).filter(r => r.pedido === pid && r.st === 'Ativa'); }
function prFalta(c, ped) { const f = prSub(prSub(ped.qtd, prExpedido(c, ped.id)), prSoma(prResPed(c, ped.id).map(r => r.kg))); return prCmp(f, 0) > 0 ? f : 0; }
function prCompat(ped, L) { return ped.prod === L.prod && (!ped.classe || !L.classe || ped.classe === L.classe) && (!ped.saf || !L.saf || ped.saf === L.saf); }
/* situação do pedido: Entregue · Coberto · Parcial · Sem reserva · Em risco (reserva com expedição impedida) · Futura: compromete a previsão */
function prSitPed(c, ped) { const rs = prResPed(c, ped.id); const exp = prExpedido(c, ped.id); const falta = prFalta(c, ped);
  const imp = rs.filter(r => { const L = prP(c).lotes[r.lote]; return !L || prSaldos(c, L).q !== 'Liberado'; });
  if (prCmp(exp, ped.qtd) >= 0) return { t: 'Entregue', c: 'gray', imp };
  if (imp.length) return { t: 'Em risco', c: 'red', imp };
  if (prCmp(falta, 0) <= 0) return { t: 'Coberto', c: 'green', imp };
  if (ped.tipo === 'futura') return { t: rs.length ? 'Futura: parcial' : 'Futura: compromete a previsão', c: 'yellow', imp };
  return { t: rs.length ? 'Parcial' : 'Sem reserva', c: rs.length ? 'yellow' : 'yellow', imp }; }
/* oferta publicada × vendas futuras (R-16): por semana (fruta) ou por safra (grão); o físico nunca entra aqui */
function prOfertaSem(c, prod, sem) { let pub = 0, tem = false; Object.keys(PRDC.cult).forEach(cid => { const k = PRDC.cult[cid]; if (prUn(k.cultura).prod !== prod) return;
    const v = prVersaoSem(c, cid, sem); if (v) { pub = prSoma([pub, v.sem[sem]]); tem = true; } });
  const fut = Object.values(prP(c).pedidos).filter(p => p.tipo === 'futura' && p.prod === prod && p.sem === sem);
  const futKg = prSoma(fut.map(p => prSub(p.qtd, prExpedido(c, p.id)))); const resKg = prSoma([].concat(...fut.map(p => prResPed(c, p.id))).map(r => r.kg));
  return { pub, tem, fut, futKg, resKg, livre: prSub(pub, prSub(futKg, resKg)) }; }
function prOfertaSafra(c, prod, saf) { let pub = 0, tem = false; Object.keys(PRDC.cult).forEach(cid => { const k = PRDC.cult[cid]; if (prUn(k.cultura).prod !== prod || (PRDC.safras[k.saf] || {}).mf !== saf) return;
    const vs = (prP(c).previsoes[cid] || []).filter(v => v.safra !== undefined); const v = vs[vs.length - 1]; if (v) { pub = prSoma([pub, v.safra]); tem = true; } });
  const cultura = (Object.values(PRDC.cult).find(k => prUn(k.cultura).prod === prod) || {}).cultura || 'Soja';
  const ob = (PRDC.obrig || []).filter(x => x.prod === prod && x.saf === saf).map(x => ({ id: x.id, tipo: x.tipo, kg: prMul(x.sc, prUn(cultura).massa), cont: x.cont }));
  const fut = Object.values(prP(c).pedidos).filter(p => p.tipo === 'futura' && p.prod === prod && p.saf === saf);
  const futKg = prSoma(ob.map(x => x.kg).concat(fut.map(p => prSub(p.qtd, prExpedido(c, p.id))))); const resKg = prSoma([].concat(...fut.map(p => prResPed(c, p.id))).map(r => r.kg));
  return { pub, tem, ob, fut, futKg, resKg, livre: prSub(pub, prSub(futKg, resKg)), cultura }; }

/* ---------- encerrar a O.S. de colheita (R-18): presente em toda página do estado (cenPodeEncerrar chama) ---------- */
function prPodeEncerrar(c, id) { const o = (c.ordens || {})[id]; if (!o || !prEhColheita(o)) return '';
  const ap = prAPesar(c, id); if (!ap.length) return ''; const sem = ap.filter(g => g.sinc === false), pes = ap.filter(g => g.sinc !== false);
  return [pes.length ? 'Carga a pesar: ' + pes.map(g => g.id).join(', ') + '. ' + prRec(prFazDaOS(c, o)) + ' pesa em Produção › Cargas e recebimento antes de encerrar a colheita.' : '',
          sem.length ? 'Carga no aparelho aguardando sinal: ' + sem.map(g => g.id).join(', ') + '.' : ''].filter(Boolean).join(' '); }

/* =====================================================================================================================
   Comandos (sempre dentro de cenMudar): chave de quem inicia; mesma chave e mesmo conteúdo = mesmo registro; outro conteúdo = conflito
   ===================================================================================================================== */
function prMov(c, m) { const P = prP(c, 1); P.seq.mp = (P.seq.mp || 1000) + 1; m.id = 'MP-' + P.seq.mp; m.d = m.d || prHoje(); m.at = m.at || cenAgora(); P.movs.push(m); return m; }
function prConflito(id, ja) { return new Error('Este registro (' + id + ') já foi gravado' + (ja ? ' como ' + ja : '') + ' com outro conteúdo: conflito, nada gravado.'); }
function prLocalRec(faz, cultura) { const m = (PRDC.recLocal || {})[faz] || {}; return m[cultura] || m['*'] || ''; }
function prNumOk(x) { return x !== '' && x !== null && x !== undefined && isFinite(Number(String(x).replace(',', '.'))); }
function prNum(x) { return Number(String(x).replace(',', '.')); }

/* contagem de frutos (MB-07): grava a amostra; não publica (R-17) */
function prContar(c, k) { const P = prP(c, 1); const kk = PRDC.cult[k.cult];
  if (!kk || !kk.semanal) throw new Error('Escolha um talhão de fruta em produção.');
  const n = Number(k.plantas); const e = ['pintado', 'devez', 'verde'].map(x => Number(k[x] || 0)); const peso = String(k.peso === undefined ? '' : k.peso).replace(',', '.');
  const imp = JSON.stringify([k.cult, n, e, peso, k.d || prHoje()]);
  if (k.chave) { const ja = P.contagens.find(x => x.chave === k.chave); if (ja) { if (ja.imp !== imp) throw prConflito(k.chave, ja.id); return { msg: 'Contagem ' + ja.id + ' já registrada: nada foi gravado de novo.', cnt: ja, repetido: true }; } }
  if (!(n > 0) || Math.floor(n) !== n) throw new Error('Conte ao menos uma planta.');
  if (e.some(x => !(x >= 0) || Math.floor(x) !== x)) throw new Error('Frutos por estádio: números inteiros, 0 ou mais.');
  if (!prNumOk(peso) || !(Number(peso) > 0 && Number(peso) < 20)) throw new Error('Informe o peso médio do fruto da amostra em kg (ex.: 1,20).');
  P.seq.cnt = (P.seq.cnt || 0) + 1; const id = 'CNT-' + String(P.seq.cnt).padStart(4, '0'); const on = k.via === 'app' ? cenOnline(c) : true;
  const x = { id, cult: k.cult, tal: kk.local, d: k.d || prHoje(), at: cenAgora(), quem: k.quem || '', plantas: n, pintado: e[0], devez: e[1], verde: e[2], peso, chave: k.chave || id, imp, sinc: on, via: k.via || 'web' };
  P.contagens.push(x); if (!on) c.app.fila.push(id);
  const r = prRascunho(c, k.cult); const sems = Object.keys(r.sem).filter(s => !prSemComecou(s));
  return { msg: 'Contagem ' + id + ' do ' + kk.local + ' gravada: ' + n + (n > 1 ? ' plantas' : ' planta') + ', peso médio ' + prFmtT(peso, 2) + ' kg. Rascunho: ' + sems.map(s => prSemTxt(s) + ' ' + prUnTxt(kk.cultura, r.sem[s])).join(' · ')
    + '. A previsão só muda quando ' + prQuem('ag') + ' publicar.' + (on ? '' : ' Salvo no aparelho; envia quando houver sinal.'), cnt: x }; }

/* publicar previsão (Ana): congela a versão nova só das semanas que ainda não começaram (R-17) */
function prPublicar(c, cid, quem, par) { const kk = PRDC.cult[cid]; if (!kk) throw new Error('Cultivo não encontrado.'); const P = prP(c, 1);
  if (par) { const ph = Number(par.plantas_ha), pe = String(par.perda === undefined ? '' : par.perda).replace(',', '.');
    if (!(ph > 0 && ph < 10000) || Math.floor(ph) !== ph) throw new Error('Plantas vivas por hectare: número inteiro maior que zero.');
    if (!prNumOk(pe) || Number(pe) < 0 || Number(pe) >= 1) throw new Error('Perda entre 0 e 100 %.'); par = { plantas_ha: ph, perda: pe }; }
  const pb = prPublicavel(c, cid, par); if (!pb) throw new Error('Nada novo a publicar no ' + kk.local + ': a versão vigente já tem as semanas que ainda não começaram.');
  const vs = P.previsoes[cid] = P.previsoes[cid] || []; const v = { v: vs.length + 1, d: prHoje(), at: cenAgora(), por: quem || prQuem('ag'), base: pb.base, cnt: pb.cnt || '' };
  if (pb.safra !== undefined) v.safra = pb.safra; else { v.sem = pb.sem; v.plantas_ha = pb.par.plantas_ha; v.perda = pb.par.perda; }
  vs.push(v);
  const txt = v.safra !== undefined ? 'safra ' + prUnTxt(kk.cultura, v.safra, 0) : Object.keys(v.sem).map(s => prSemTxt(s) + ' ' + prUnTxt(kk.cultura, v.sem[s])).join(' · ');
  const cur = pb.sem ? prRascunho(c, cid) : null; const s0 = prSem(prHoje()); const os0 = prOsCult(c, cid).find(o => prSemDaOS(o) === s0);
  return { msg: kk.local + ' · previsão v' + v.v + ' publicada por ' + v.por + ': ' + txt + '.' + (cur && cur.sem && cur.sem[s0] !== undefined ? ' A semana em curso (' + prSemTxt(s0) + ') não muda' + (os0 ? ': orienta a ' + os0.id + '.' : '.') : ''), v }; }

/* carga do campo (MB-10 · aba Colheita): a pesar na balança; caixas ou kg estimados nunca somam (R-03) */
function prCarga(c, k) { const P = prP(c, 1); const mix = (k.mix && k.mix.length) ? k.mix : [{ os: k.os, pct: 100, modo: 'medida' }];
  const imp = JSON.stringify([k.os, k.dcol || prHoje(), Number(k.cx) || 0, Number(k.kg) || 0, k.veic || '', mix.map(x => [x.os, Number(x.pct), x.modo || 'medida'])]);
  if (k.chave) { const ja = Object.values(P.cargas).find(g => g.chave === k.chave); if (ja) { if (ja.imp !== imp) throw prConflito(k.chave, ja.id); return { msg: 'Carga ' + ja.id + ' já registrada: nada foi gravado de novo.', g: ja, repetido: true }; } }
  const o = (c.ordens || {})[k.os]; if (!o || !prEhColheita(o)) throw new Error('Escolha a O.S. de colheita da carga.');
  const orig = prMixOrig(c, mix); const cid = prCultDaOS(c, o); const kk = PRDC.cult[cid] || {}; const faz = prFazDaOS(c, o);
  P.seq.cg = (P.seq.cg || 2100) + 1; const id = 'CG-' + P.seq.cg; const on = k.via === 'web' ? true : cenOnline(c);
  const g = { id, ticket: '', faz, cultura: kk.cultura || '', os: k.os, dcol: k.dcol || prHoje(), drec: null, hora: cenAgora(), bruto: null, tara: null, liq: null, com: null, cond: '',
    local: prLocalRec(faz, kk.cultura), st: 'A pesar', lote: '', est_cx: Number(k.cx) || null, est_kg: Number(k.kg) || null, origem: orig, quem: k.quem || '', veic: k.veic || '', chave: k.chave || id, imp, sinc: on, via: k.via || 'app' };
  P.cargas[id] = g; if (!on) c.app.fila.push(id);
  return { msg: 'Carga ' + id + ' registrada (' + orig.map(x => x.tal + (orig.length > 1 ? ' ' + x.pct + ' %' : '')).join(' + ') + (g.est_cx ? ', ~' + g.est_cx + ' caixas' : '') + '): a pesar na balança. A estimativa não soma na produção.'
    + (on ? '' : ' Salvo no aparelho; envia quando houver sinal.'), g }; }
/* origem da carga (R-06): O.S. de colheita Liberadas, Em execução ou Em conferência; mistura com participação % somando 100 */
function prMixOrig(c, mix) { const tot = prSoma(mix.map(x => x.pct || 0)); if (prCmp(tot, 100) !== 0) throw new Error('A participação dos talhões tem de somar 100 % (está em ' + prFmtT(tot, 2) + ' %).');
  return mix.map(x => { const o = (c.ordens || {})[x.os]; if (!o || !prEhColheita(o)) throw new Error('Origem sem O.S. de colheita (' + (x.os || 'vazia') + ').');
    if (PR_FASES_COLH.indexOf(o.etapa) < 0) throw new Error(x.os + ' está em ' + o.etapa + ': a carga sai de O.S. de colheita liberada, em execução ou em conferência.');
    if (!(Number(x.pct) > 0)) throw new Error('Informe a participação de ' + o.talhao + '.');
    return { os: x.os, cult: prCultDaOS(c, o), tal: o.talhao, pct: Number(x.pct), modo: x.modo || 'medida' }; }); }

/* pesar e receber (CARGA): ticket, bruto e tara; descontos de grão; lote por produto + local + dia + origem (R-07, R-08, R-10, R-11) */
const PR_CONDS = ['Íntegra', 'Com avaria', 'Fora do padrão'];
function prReceber(c, k) { const P = prP(c, 1); const g0 = k.carga ? P.cargas[k.carga] : null;
  if (k.carga && (!g0 || g0.sinc === false)) throw new Error('Carga ' + k.carga + ' não encontrada (no aparelho, sem sinal?).');
  const mix = g0 ? g0.origem.map(x => ({ os: x.os, pct: x.pct, modo: x.modo })) : ((k.mix && k.mix.length) ? k.mix : [{ os: k.os, pct: 100, modo: 'medida' }]);
  const osId = mix[0].os; const o = (c.ordens || {})[osId]; if (!o || !prEhColheita(o)) throw new Error('Escolha a O.S. de colheita de origem.');
  const tk = String(k.ticket || '').trim(); const dcol = (g0 && g0.dcol) || k.dcol || prHoje();
  const imp = JSON.stringify([mix.map(x => [x.os, Number(x.pct)]), tk, Number(k.bruto), Number(k.tara), k.u === undefined ? null : String(k.u), k.imp === undefined ? null : String(k.imp), Number(k.litros) || 0, Number(k.frutos) || 0, k.cond || '', k.local || '', dcol]);
  if (k.chave) { const ja = Object.values(P.cargas).find(g => g.chaveRec === k.chave); if (ja) { if (ja.impRec !== imp) throw prConflito(k.chave, ja.id); return { msg: 'Pesagem já registrada (' + ja.id + ' · ticket ' + ja.ticket + '): nada foi somado de novo.', g: ja, repetido: true }; } }
  if (g0 && g0.st !== 'A pesar') throw new Error(g0.id + ' já está ' + g0.st.toLowerCase() + '.');
  const faz = prFazDaOS(c, o); const kk = PRDC.cult[prCultDaOS(c, o)] || {}; const cultura = kk.cultura || (g0 && g0.cultura); const u = prUn(cultura);
  if (!tk) throw new Error('Informe o ticket da balança.');
  const dupT = Object.values(P.cargas).find(g => g.st === 'Recebida' && g.faz === faz && g.ticket === tk);
  if (dupT) { if (dupT.impRec === imp) return { msg: 'Ticket ' + tk + ' já recebido na ' + dupT.id + ' com o mesmo conteúdo: é a mesma carga, nada foi somado de novo.', g: dupT, repetido: true };
    throw new Error('Ticket ' + tk + ' já recebido na ' + dupT.id + ' (' + prFmtT(dupT.liq, 2) + ' kg líquidos) com outro conteúdo: conflito, nada gravado. Confira o ticket.'); }
  const orig = prMixOrig(c, mix);
  if (!prNumOk(k.bruto) || !(prNum(k.bruto) > 0)) throw new Error('Informe o peso bruto em kg.');
  if (!prNumOk(k.tara) || prNum(k.tara) < 0) throw new Error('Informe a tara em kg (0 ou mais).');
  const liq = prSub(prNum(k.bruto), prNum(k.tara)); if (prCmp(liq, 0) <= 0) throw new Error('Líquido (bruto − tara) tem de ser maior que zero.');
  let com = liq, desc = null;
  if (u.grao) { if (!prNumOk(k.u) || prNum(k.u) < 0 || prNum(k.u) > 40) throw new Error('Informe a umidade % do grão.');
    if (!prNumOk(k.imp) || prNum(k.imp) < 0 || prNum(k.imp) > 100) throw new Error('Informe a impureza % do grão.');
    desc = prCorrigir(liq, String(prNum(k.u)), String(prNum(k.imp)), u.u, u.imp); com = desc.com; }
  if (u.campo && !(prNum(k.litros) > 0)) throw new Error('Informe os litros de café da roça.');
  if (u.base === 'frutos' && !(prNum(k.frutos) > 0 && Math.floor(prNum(k.frutos)) === prNum(k.frutos))) throw new Error('Informe os frutos contados na carga.');
  if (PR_CONDS.indexOf(k.cond) < 0) throw new Error('Informe a condição da carga: Íntegra, Com avaria ou Fora do padrão.');
  if (dcol > prHoje()) throw new Error('A colheita não pode ser depois de hoje (' + prBr(prHoje()) + ').');
  const local = k.local || prLocalRec(faz, cultura); if (!PRDC.locais[local]) throw new Error('Escolha o local de recebimento.');
  /* quantidade do lote na base da cultura: grão comercial; fruta e cana líquido; café L; coco e abacaxi frutos */
  const base = u.campo ? prNum(k.litros) : (u.base === 'frutos' ? prNum(k.frutos) : com);
  const pcts = orig.map(x => x.pct); const pLiq = prRateio(liq, pcts), pCom = prRateio(com, pcts), pBase = prRateio(base, pcts);
  const prod = u.campo ? u.proc : u.prod; const drec = prHoje(); const misto = orig.length > 1;
  let L = misto ? null : Object.values(P.lotes).find(x => !x.misto && x.prod === prod && x.local === local && x.drec === drec && x.cond === k.cond && (x.origem || []).length && x.origem.every(y => y.os === osId && y.dcol === dcol));
  const novo = !L;
  if (!L) { const w = String(prSemN(prSem(drec))).padStart(2, '0'); P.seq.lote[w] = (P.seq.lote[w] || 130) + 1; const id = 'L' + w + '-' + P.seq.lote[w];
    L = P.lotes[id] = { id, prod, cultura, classe: u.grao ? 'Padrão' : '', saf: (PRDC.safras[kk.saf] || {}).mf || '', faz, local, drec, dcol, validade: u.vida ? prDiaMais(dcol, u.vida) : null,
      q0: k.cond === 'Íntegra' ? 'Liberado' : 'Em inspeção', cond: k.cond, misto, origem: [], cargas: [] }; }
  const g = g0 || (P.seq.cg = (P.seq.cg || 2100) + 1, P.cargas['CG-' + P.seq.cg] = { id: 'CG-' + P.seq.cg, os: osId, dcol, via: 'web', sinc: true, chave: k.chave || ('W-CG-' + P.seq.cg), hora: cenAgora() });
  Object.assign(g, { ticket: tk, faz, cultura, os: osId, dcol, drec, bruto: prNum(k.bruto), tara: prNum(k.tara), liq, com, u: u.grao ? String(prNum(k.u)) : null, imp: g.imp,
    impG: u.grao ? String(prNum(k.imp)) : null, desc, litros: u.campo ? prNum(k.litros) : null, frutos: u.base === 'frutos' ? prNum(k.frutos) : null, cond: k.cond, local, st: 'Recebida', lote: L.id,
    origem: orig.map((x, i) => Object.assign({}, x, { kg: pLiq[i], com: pCom[i], base: pBase[i], litros: u.campo ? pBase[i] : 0 })), quemRec: k.quem || prRec(faz), chaveRec: k.chave || ('W-' + g.id), impRec: imp, horaRec: cenAgora() });
  orig.forEach((x, i) => L.origem.push({ carga: g.id, os: x.os, cult: x.cult, tal: x.tal, dcol, kg: pBase[i], modo: x.modo }));
  L.cargas.push(g.id); if (L.validade && u.vida) L.validade = [L.validade, prDiaMais(dcol, u.vida)].sort()[0];
  prMov(c, { tipo: 'recebimento', lote: L.id, kg: base, carga: g.id, quem: g.quemRec });
  const S = prSaldos(c, L); const R = prResultado(c, prCultDaOS(c, o)); const pa = R && R.passes.find(p => p.os === osId);
  return { msg: g.id + ' recebida: ' + prFmtT(liq, 2) + ' kg líquidos (' + prFmtT(prNum(k.bruto), 2) + ' − ' + prFmtT(prNum(k.tara), 2) + ')' + (u.grao ? ' · comercial ' + prFmtT(com, 2) + ' kg = ' + prUnTxt(cultura, com) : '')
    + ' no ' + L.id + (novo ? ' (novo)' : '') + ' · ' + PRDC.locais[local].nome + ' · ' + S.q + '.' + (pa && pa.area > 0 ? ' ' + o.talhao + ': passe ' + prSemTxt(pa.sem) + ' ' + prPrtvTxt(cultura, pa.kg, pa.area) + (pa.final ? '.' : ' (parcial).') : ''), g, L }; }

/* estornar carga recebida (R-19): motivo; devolve o efeito; recusa se o lote ficar abaixo do reservado; o ticket fica livre */
function prEstornar(c, id, motivo, quem) { const P = prP(c, 1); const g = P.cargas[id]; if (!g || g.st !== 'Recebida') throw new Error('Só carga recebida é estornada.');
  const mot = String(motivo || '').trim(); if (!mot) throw new Error('Informe o motivo do estorno.');
  const L = P.lotes[g.lote]; const mv = P.movs.find(m => m.tipo === 'recebimento' && m.carga === id); const kg = mv ? mv.kg : 0;
  const fis = prFis(c, L.id), res = prResLote(c, L.id); const fica = prSub(fis, kg);
  if (prCmp(fica, res) < 0) throw new Error('Estorno recusado: o ' + L.id + ' ficaria com ' + prEstTxt(L.cultura, fica) + ', abaixo do reservado (' + prEstTxt(L.cultura, res) + '). Cancele ou reduza a reserva antes.');
  prMov(c, { tipo: 'estorno', lote: L.id, kg: -kg, carga: id, quem: quem || prRec(g.faz), obs: mot });
  (L.origem || []).forEach(x => { if (x.carga === id) x.est = true; }); g.st = 'Estornada'; g.estorno = { motivo: mot, quem: quem || prRec(g.faz), d: prHoje(), at: cenAgora() }; g.ticketLivre = g.ticket;
  return { msg: id + ' estornada (' + mot + '): ' + prEstTxt(L.cultura, kg) + ' saem do ' + L.id + '. O ticket ' + g.ticket + ' fica livre para novo registro; o histórico continua.' }; }

/* liberar lote (Qualidade, R-13): reavalia carência e ordem; recusa com a pendência e o dono */
function prLiberarLote(c, lid, quem) { const P = prP(c, 1); const L = P.lotes[lid]; if (!L) throw new Error('Lote não encontrado.'); const S = prSaldos(c, L);
  if (S.q === 'Liberado') throw new Error(lid + ' já está liberado.');
  if (S.q === 'Em processo') throw new Error(lid + ' está em processo (' + S.mot + '): o beneficiamento libera o lote de saída.');
  if (S.q === 'Bloqueado') throw new Error('Liberar recusado: ' + S.mot + '. Lote bloqueado por carência só sai pela Qualidade com laudo (fora desta etapa). Quem decide: ' + S.dono + '.');
  const Q = prQualidade(c, Object.assign({}, L, { q0: 'Liberado' })); if (Q.q !== 'Liberado') throw new Error('Liberar recusado: ' + Q.mot + '. Quem resolve: ' + Q.dono + '.');
  L.q0 = 'Liberado'; L.lib = { quem: quem || prQuem('qual'), d: prHoje(), at: cenAgora() }; prMov(c, { tipo: 'liberação', lote: lid, kg: 0, fis: false, quem: L.lib.quem });
  return { msg: lid + ' liberado por ' + L.lib.quem + ': ' + prEstTxt(L.cultura, S.fis) + ' aptos para reserva e venda.' }; }

/* reservar lote apto para pedido (R-15): mesma classe, avaliação do destino, ≤ disponível e ≤ falta; dedução única */
function prReservar(c, k) { const P = prP(c, 1); const kg = prNumOk(k.kg) ? prNum(k.kg) : NaN; const imp = JSON.stringify([k.pedido, k.lote, kg]);
  if (k.chave) { const ja = Object.values(P.reservas).find(r => r.chave === k.chave); if (ja) { if (ja.imp && ja.imp !== imp) throw prConflito(k.chave, ja.id); return { msg: 'Reserva ' + ja.id + ' já registrada: nada foi deduzido de novo.', rs: ja, repetido: true }; } }
  const ped = P.pedidos[k.pedido]; if (!ped) throw new Error('Escolha o pedido.'); const L = P.lotes[k.lote]; if (!L) throw new Error('Escolha o lote.');
  if (!prCompat(ped, L)) throw new Error(L.id + ' (' + L.prod + (L.classe ? ' · ' + L.classe : '') + (L.saf ? ' ' + L.saf : '') + ') não atende o ' + ped.id + ' (' + ped.prod + (ped.classe ? ' · ' + ped.classe : '') + (ped.saf ? ' ' + ped.saf : '') + ').');
  const S = prSaldos(c, L); if (S.q !== 'Liberado') throw new Error(L.id + ' não está apto (' + S.q + ': ' + S.mot + '). Quem resolve: ' + (S.dono || prQuem('qual')) + '.');
  const dest = ped.dest || 'MI-BR'; let pend = [];
  if (typeof carAvaliar === 'function' && typeof CARD !== 'undefined') for (const lc of prLcs(c, L)) { const a = carAvaliar(c, lc, dest);
    if (a.st === 'nao_conforme') { const x = a.motivos[0] || {}; throw new Error('Reserva recusada: ' + lc + ' ' + a.rot + ' · ' + (x.t || '') + (x.q ? ' (quem decide: ' + x.q + ')' : '') + '.'); }
    if (a.st === 'pendente') pend = pend.concat(a.faltas.map(f => f.t + ' (' + f.q + ')')); }
  if (!(kg > 0)) throw new Error('Informe a quantidade a reservar.');
  if (prCmp(kg, S.disp) > 0) throw new Error('Acima do disponível do ' + L.id + ': ' + prEstTxt(L.cultura, S.disp) + '.');
  const falta = prFalta(c, ped); if (prCmp(kg, falta) > 0) throw new Error('Acima da falta do ' + ped.id + ': ' + prEstTxt(L.cultura, falta) + '.');
  P.seq.rs = (P.seq.rs || 0) + 1; const id = 'RS-' + String(P.seq.rs).padStart(4, '0');
  const rs = P.reservas[id] = { id, pedido: ped.id, lote: L.id, kg, st: 'Ativa', d: prHoje(), at: cenAgora(), quem: k.quem || prQuem('com'), chave: k.chave || id, imp };
  prMov(c, { tipo: 'reserva', lote: L.id, kg, fis: false, reserva: id, pedido: ped.id, quem: rs.quem });
  const S2 = prSaldos(c, L); const sit = prSitPed(c, ped);
  return { msg: id + ': ' + prEstTxt(L.cultura, kg) + ' do ' + L.id + ' reservados para o ' + ped.id + ' (' + ped.cliente + '). ' + L.id + ' disponível ' + prEstTxt(L.cultura, S2.disp) + ' · ' + ped.id + ' ' + sit.t.toLowerCase() + '.'
    + (pend.length ? ' Destino ' + (PRDC.dest[dest] || dest) + ' pendente: ' + pend[0] + '; a expedição exige a liberação comercial.' : ''), rs }; }
function prCancelarReserva(c, id, motivo, quem) { const P = prP(c, 1); const r = P.reservas[id]; if (!r || r.st !== 'Ativa') throw new Error('Reserva não está ativa.');
  const mot = String(motivo || '').trim(); if (!mot) throw new Error('Informe o motivo do cancelamento da reserva.');
  r.st = 'Cancelada'; r.canc = { motivo: mot, quem: quem || prQuem('com'), d: prHoje(), at: cenAgora() };
  prMov(c, { tipo: 'cancelamento de reserva', lote: r.lote, kg: -r.kg, fis: false, reserva: id, pedido: r.pedido, quem: r.canc.quem, obs: mot });
  const L = P.lotes[r.lote]; return { msg: id + ' cancelada (' + mot + '): ' + prEstTxt(L.cultura, r.kg) + ' voltam ao disponível do ' + r.lote + '.' }; }
/* gancho de teste/inspeção (o script da tela roda isolado) */
try { window.__pr = { prResultado, prSaldos, prQualidade, prOfertaSem, prOfertaSafra, prReceber, prReservar, prEstornar, prLiberarLote, prPublicar, prContar, prCarga, prPodeEncerrar }; } catch (e) {}
