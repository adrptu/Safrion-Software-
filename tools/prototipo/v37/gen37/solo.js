/* ===== Análise de solo e água no solo (SOLO-01 · docs/analise-solo/ESPECIFICACAO.md; decisões em docs/analise-solo/DECISOES.md) =====
   A análise não é fluxo paralelo: é uma camada de sugestão sobre as doses de correção e adubação do plano. Sem laudo vale a dose do plano.
   Fórmula num lugar só (ENG-011): índices (PRD 38.3), conversões, calagem (CAL-10), potássio, gessagem, água disponível (CAD) e a dose
   efetiva de cada chave (R14/R16). Decimal (ENG-013) pela aritmética pr* de producao.js; a unidade da cultura vem de prUn (DEC-0510-03).
   Entra no cenario.js_prefixo() depois de producao.js (só funções). Os dados (SOLO0: laudos da semente, regra de demonstração, produto
   padrão de correção, garantia, preço) vêm de dados_solo.js_prefixo(), só no AG-02 e no Planejar safra. A O.S. lê só os aceites gravados.
   Comentários só com bloco: este arquivo também entra em strings Python. */

/* ---------- utilitários ---------- */
const SOLO_PROFS = ['0–20', '20–40'];
const SOLO_SITC = { 'Validado': 'green', 'Aguardando validação': 'yellow', 'Inconsistente': 'red', 'Vencido': 'gray', 'Substituído': 'gray' };   /* cor da situação do laudo (AG-02, Planejar safra e Mapa) */
const SOLO_FASE = { 'Liberadas': 'já liberada', 'Em execução': 'em execução', 'Em conferência': 'em conferência', 'Encerradas': 'encerrada' };
function soloR2(x) { return prN(prRd(prM(x), 10000n) * 10000n); }   /* 2 casas, meio para cima, em decimal (R09) */
function soloNum(x) {   /* texto pt-BR ou ponto → texto decimal; vazio → null; inválido → NaN */
  if (x === null || x === undefined || String(x).trim() === '') return null;
  const t = String(x).trim().replace(/\s/g, ''); const s = t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : t;
  return /^-?\d+(\.\d+)?$/.test(s) ? s : NaN; }
function soloBr(iso) { const a = String(iso || '').slice(0, 10).split('-'); return a.length === 3 ? a[2] + '/' + a[1] + '/' + a[0] : '—'; }
function soloDdMm(iso) { const a = String(iso || '').slice(0, 10).split('-'); return a.length === 3 ? a[2] + '/' + a[1] : '—'; }
function soloF(x, d) { return (x === null || x === undefined) ? 'não calculável' : prFmtT(x, d === undefined ? 2 : d); }
function soloDoseTxt(d, un) { return (un === 't' ? prFmt(d, 2) : prFmtT(d, 2)) + ' ' + un + '/ha'; }
function soloQtdTxt(q, un, sinal) { const n = Number(q) || 0; return (sinal ? (n > 0 ? '+' : (n < 0 ? '−' : '')) : '') + cenNum(Math.abs(n), un === 't' ? 2 : 2) + ' ' + un; }
function soloHoje() { return (typeof SOLO0 !== 'undefined' && SOLO0.hoje) || '2026-09-23'; }   /* data do cenário (D2.HOJE) */
function soloAgora() { return soloHoje() + ' ' + cenAgora(); }
function soloMaisMeses(iso, n) { const d = new Date(String(iso).slice(0, 10) + 'T12:00:00Z'); d.setUTCMonth(d.getUTCMonth() + n); return d.toISOString().slice(0, 10); }
function soloMaisDias(iso, n) { const d = new Date(String(iso).slice(0, 10) + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); }
function soloAn(l, a) { return ((l && l.an) || []).find(x => x.a === a) || null; }

/* ---------- conversões (R05): 1 cmolc/dm³ = 10 mmolc/dm³; mg/dm³ → cmolc/dm³: K ÷ 391, Ca ÷ 200,4, Mg ÷ 121,6. mg/kg não se converte ---------- */
const SOLO_MG = { K: '391', Ca: '200.4', Mg: '121.6' };
function soloCmolc(x) {
  if (!x) return { v: null, nc: 'não analisado' };
  if (x.q === '<') return { v: null, nc: 'abaixo do limite de detecção' };   /* nunca metade do limite (38.3) */
  if (!x.un) return { v: null, nc: 'sem unidade' };
  if (x.un === 'cmolc/dm³') return { v: prN(prM(x.v)) };
  if (x.un === 'mmolc/dm³') return { v: prDiv(x.v, 10) };
  if (x.un === 'mg/dm³' && SOLO_MG[x.a]) return { v: prDiv(x.v, SOLO_MG[x.a]) };
  return { v: null, nc: 'unidade incompatível (' + x.un + ')' }; }
// indicadores do laudo (15/10/2026): valor do indicador (analito do laudo ou índice do soloIdx: V, T, SB, m) no laudo e num ponto da
// amostragem em grade (dados_solo.pontos). Fonte única do AG-02 (colunas) e do Mapa (mapa de calor). K sempre em mg/dm³ (soloKmg).
function soloIndVal(l, ind) {
  if (ind.idx) { const r = (l.idx || {})[ind.k]; return r && r.v !== null && r.v !== undefined ? Number(r.v) : null; }
  const x = soloAn(l, ind.k); if (!x || x.v === null || x.v === undefined) return null;
  if (ind.k === 'K') { const km = soloKmg(x); return km.v === null ? null : Number(km.v); } return Number(x.v);
}
function soloIndPt(l, ind, p) {
  if (ind.idx) { const pl = Object.assign({}, l, { an: l.an.map(x => (p.an[x.a] !== undefined) ? Object.assign({}, x, { v: p.an[x.a] }) : x) }); const r = soloIdx(pl, SOLO0.regra.tol)[ind.k];
    return r && r.v !== null && r.v !== undefined ? Number(r.v) : null; }
  if (p.an[ind.k] === undefined) return null;
  if (ind.k === 'K') { const km = soloKmg(Object.assign({}, soloAn(l, 'K'), { v: p.an.K })); return km.v === null ? null : Number(km.v); } return Number(p.an[ind.k]);
}
function soloKmg(x) {   /* K em mg/dm³ para a classe de teor (R07) */
  if (!x) return { v: null, nc: 'K não analisado' }; if (x.q === '<') return { v: null, nc: 'K abaixo do limite de detecção' }; if (!x.un) return { v: null, nc: 'K sem unidade' };
  if (x.un === 'mg/dm³') return { v: prN(prM(x.v)) }; if (x.un === 'cmolc/dm³') return { v: prMul(x.v, SOLO_MG.K) }; if (x.un === 'mmolc/dm³') return { v: prMulDiv(x.v, SOLO_MG.K, 10) };
  return { v: null, nc: 'K em unidade incompatível (' + x.un + ')' }; }

/* ---------- índices (PRD 38.3, R04): SB = Ca + Mg + K (+ Na só se analisado); T = SB + H+Al; t = SB + Al; V = 100·SB/T; m = 100·Al/t ---------- */
function soloIdx(l, tol) {
  const g = a => soloCmolc(soloAn(l, a)); const Ca = g('Ca'), Mg = g('Mg'), K = g('K'), HAl = g('H+Al'), Al = g('Al'); const naX = soloAn(l, 'Na'); const Na = naX ? soloCmolc(naX) : null;
  const falta = (pares) => { const f = pares.find(p => p[1] && p[1].v === null); return f ? f[0] + ' ' + f[1].nc : ''; };
  const n2 = x => prFmt(x, 2);
  const R = {};
  const sbF = falta([['Ca', Ca], ['Mg', Mg], ['K', K]].concat(Na ? [['Na', Na]] : []));
  R.SB = sbF ? { v: null, nc: sbF } : { v: prSoma([Ca.v, Mg.v, K.v].concat(Na ? [Na.v] : [])) };
  R.SB.f = 'SB = Ca + Mg + K' + (Na ? ' + Na' : ' (Na não analisado)');
  R.SB.e = sbF ? '' : 'Ca ' + n2(Ca.v) + ' + Mg ' + n2(Mg.v) + ' + K ' + n2(K.v) + (Na ? ' + Na ' + n2(Na.v) : '') + ' cmolc/dm³';
  const tF = R.SB.v === null ? R.SB.nc : falta([['H+Al', HAl]]);
  R.T = tF ? { v: null, nc: tF } : { v: prSoma([R.SB.v, HAl.v]), e: 'SB ' + n2(R.SB.v) + ' + H+Al ' + n2(HAl.v) + ' cmolc/dm³' }; R.T.f = 'T = SB + H+Al';
  const t2F = R.SB.v === null ? R.SB.nc : falta([['Al', Al]]);
  R.t = t2F ? { v: null, nc: t2F } : { v: prSoma([R.SB.v, Al.v]), e: 'SB ' + n2(R.SB.v) + ' + Al ' + n2(Al.v) + ' cmolc/dm³' }; R.t.f = 't = SB + Al';
  R.V = R.T.v === null ? { v: null, nc: R.T.nc } : (prCmp(R.T.v, 0) === 0 ? { v: null, nc: 'T igual a zero' } : { v: prMulDiv(100, R.SB.v, R.T.v), e: '100 × SB ' + n2(R.SB.v) + ' ÷ T ' + n2(R.T.v) }); R.V.f = 'V = 100 × SB ÷ T';
  R.m = R.t.v === null ? { v: null, nc: R.t.nc } : (prCmp(R.t.v, 0) === 0 ? { v: null, nc: 't igual a zero' } : { v: prMulDiv(100, Al.v, R.t.v), e: '100 × Al ' + n2(Al.v) + ' ÷ t ' + n2(R.t.v) }); R.m.f = 'm = 100 × Al ÷ t';
  /* índice do laboratório preservado ao lado; diferença acima da tolerância mostra "difere do laboratório", sem bloquear; a regra usa o recalculado (D-17) */
  const L = (l && l.lab_idx) || {}; tol = tol || { pp: '0.5', cmolc: '0.05' };
  ['SB', 'T', 't', 'V', 'm'].forEach(k => { if (L[k] === undefined || L[k] === '') return; R[k].lab = L[k];
    if (R[k].v !== null) { const d = prSub(R[k].v, L[k]); const ad = prCmp(d, 0) < 0 ? prSub(0, d) : d; R[k].difere = prCmp(ad, (k === 'V' || k === 'm') ? tol.pp : tol.cmolc) > 0; } });
  return R; }

/* ---------- regras de demonstração (R06–R08) ---------- */
function soloCalagem(T, V1, V2, prnt) {   /* CAL-10 (AC-27): NC100 = max(0, (V2 − V1)·T/100) t/ha; dose = NC100·100/PRNT, com o PRNT uma vez */
  const d = prSub(V2, V1); const nc = prCmp(d, 0) > 0 ? prMulDiv(d, T, 100) : 0;
  return { nc, dose: prMulDiv(nc, 100, prnt) }; }
function soloV2(R, cultura) { const k = prCult(cultura); return R.v2[k] !== undefined ? R.v2[k] : R.v2[cultura]; }   /* V₂ da cultura (R06, demonstração) */
function soloClasseK(kmg, R) { const c = R.k.cortes; for (let i = 0; i < c.length; i++) if (prCmp(kmg, c[i]) < 0) return R.k.classes[i]; return R.k.classes[c.length]; }
function soloK2O(kmg, metaKg, R) {   /* K₂O (kg/ha) pela classe de K e pela meta; fora da faixa da regra, nada (AGR-012: sem extrapolação silenciosa) */
  const f = R.k.faixa; if (prCmp(metaKg, f[0]) < 0 || prCmp(metaKg, f[1]) > 0) return { nc: 'meta fora da faixa da regra (' + cenNum(Number(f[0])) + ' a ' + cenNum(Number(f[1])) + ' kg/ha)' };
  const cl = soloClasseK(kmg, R); const lin = R.k.tabela.find(t => prCmp(metaKg, t[0]) <= 0);
  return { classe: cl, k2o: lin[1][cl], ate: lin[0] }; }
function soloGesso(ca, m, argila, classe, R) {   /* R08 (D-03, demonstração): Ca < 0,5 cmolc/dm³ ou m > 20 % no 20–40 cm; NG = k × argila (kg/ha); nunca da calagem */
  const G = R.gesso; const gat = (ca !== null && prCmp(ca, G.ca) < 0) || (m !== null && prCmp(m, G.m) > 0);
  if (!gat) return { gat: false }; const k = G.k[classe]; if (!k) return { gat: true, nc: 'sem fator para a classe ' + (classe || '—') };
  if (argila === null) return { gat: true, nc: 'argila não analisada' }; return { gat: true, k, ng: prMul(k, argila) }; }
/* água disponível (pedido do proprietário 05–09/10): CAD = (CC − PMP) × profundidade efetiva, em mm. Propriedade do solo: não é a capacidade
   do equipamento nem a lâmina recomendada (R24, ESPECIFICACAO §3.6). Este arquivo entra no prefixo do cenário de todas as telas, inclusive a
   O.S., que não fala de irrigação por política: o texto sobre de onde vem a lâmina fica só nas telas de Análises de solo e Irrigação. */
function soloCAD(m) {
  const cc = soloNum(m.cc), pmp = soloNum(m.pmp), z = soloNum(m.z);
  if (cc === null || (typeof cc !== 'string')) return { v: null, nc: 'sem capacidade de campo' };
  if (pmp === null || (typeof pmp !== 'string')) return { v: null, nc: 'sem ponto de murcha permanente medido' };
  if (z === null || (typeof z !== 'string') || !(prCmp(z, 0) > 0)) return { v: null, nc: 'sem profundidade efetiva' };
  if (prCmp(pmp, cc) >= 0) return { v: null, nc: 'ponto de murcha não é menor que a capacidade de campo' };
  const d = prSub(cc, pmp);
  if (m.un === '% volume') { const v = prMulDiv(d, prMul(z, 10), 100); return { v, f: 'CAD = (CC − PMP) ÷ 100 × z × 10 mm/cm', e: '(' + prFmtT(cc) + ' − ' + prFmtT(pmp) + ') % vol. ÷ 100 × ' + prFmtT(z) + ' cm × 10 = ' + prFmtT(v) + ' mm' }; }
  if (m.un === 'mm/cm') { const v = prMul(d, z); return { v, f: 'CAD = (CC − PMP) × z', e: '(' + prFmtT(cc) + ' − ' + prFmtT(pmp) + ') mm/cm × ' + prFmtT(z) + ' cm = ' + prFmtT(v) + ' mm' }; }
  return { v: null, nc: 'unidade sem conversão para lâmina (' + (m.un || 'sem unidade') + ')' }; }
function soloAguaDo(S0, c, faz, tal) {   /* medição de água mais recente do talhão (talhão inteiro antes de zona) */
  const S = (c && c.solo) || {}; const ls = ((S0 && S0.agua) || []).concat(Object.values(S.agua || {})).filter(m => m.faz === faz && m.tal === tal);
  return ls.sort((a, b) => (a.data < b.data ? 1 : (a.data > b.data ? -1 : (a.zona ? 1 : -1))))[0] || null; }

/* ---------- laudos: semente + estado, situação (R02, R03) ---------- */
function cenSolo(c) { const s = c.solo || (c.solo = {}); ['laudos', 'corr', 'st', 'aceites', 'agua', 'recibos'].forEach(k => { if (!s[k]) s[k] = {}; }); return s; }   /* D-05: sem subir a versão */
function soloLaudos(c, S0) {
  const S = (c && c.solo) || {}; const R = S0.regra; const hoje = S0.hoje || soloHoje();
  const ls = (S0.laudos || []).concat(Object.values(S.laudos || {})).map(l0 => {
    const l = cenClone(l0); const cr = (S.corr || {})[l.id] || {};
    l.an = (l.an || []).map(x => cr[x.a] ? Object.assign({}, x, { v: cr[x.a].v, un: cr[x.a].un, corrigido: cr[x.a] }) : x);
    const st = (S.st || {})[l.id]; if (st) { l.sit = st.sit; l.por = st.por || ''; l.em = st.em || ''; }
    const semUn = l.an.filter(x => !x.un).map(x => x.a);
    if (semUn.length) { l.sit = 'Inconsistente'; l.motivo = semUn.join(', ') + ' sem unidade'; }
    l.val = soloMaisMeses(l.coleta, R.validade.meses);   // DEC-1610-04: 24 meses para todo talhão, irrigado ou não
    if (l.sit === 'Validado' && l.val < hoje) { l.sit = 'Vencido'; l.motivo = 'validade até ' + soloBr(l.val); }
    if (l.tipo === 'solo') l.idx = soloIdx(l, R.tol);
    return l; });
  /* R02 (D-30): para o mesmo talhão e profundidade vale o laudo validado de coleta mais recente; o anterior fica Substituído */
  ls.forEach(l => { if (l.sit !== 'Validado' || l.tipo !== 'solo') return;
    const novo = ls.filter(x => x !== l && x.tipo === 'solo' && x.sit === 'Validado' && x.faz === l.faz && x.tal === l.tal && x.prof === l.prof && x.coleta > l.coleta).sort((a, b) => a.coleta < b.coleta ? 1 : -1)[0];
    if (novo) { l.subst = novo.id; } });
  ls.forEach(l => { if (l.subst) { l.sit = 'Substituído'; l.motivo = 'pelo ' + l.subst; } });
  return ls; }
function soloVigente(ls, faz, tal, prof) {   /* R02: solo, Validado, mesma fazenda e talhão, amostra única do talhão (zona não sugere, D-15) */
  return ls.find(l => l.tipo === 'solo' && l.sit === 'Validado' && l.faz === faz && l.tal === tal && l.prof === prof && !l.zona) || null; }

/* ---------- dose efetiva por chave (R14) e atividades efetivas do cultivo (R07, R16) ---------- */
function soloTipoAtv(a) { const n = String((a && a.nome) || ''); return /^Calagem/.test(n) ? 'cal' : (/^Gessagem/.test(n) ? 'ges' : ''); }
function soloAcAtivos(aceites, cid, planoId) { return Object.values(aceites || {}).filter(a => a.st === 'ativo' && a.cid === cid && (!planoId || !a.plano || a.plano.id === planoId)); }
/* cu: {id, plano}; adj: ajustes da sessão do cultivo ('A|i' = dose | '-'; 'A|+n' = insumo incluído); aceites: c.solo.aceites.
   Dose de cada produto: ajuste manual da sessão, senão aceite do cenário, senão padrão (R14). A atividade incluída pela análise substitui a
   mesma operação do padrão (R16, A3). Retirada pela análise do único insumo tira a atividade (R07) e a devolve em ret, para a regra de K ainda
   a ver quando o laudo vigente muda (R22; revisão A3). Aceite de produto que saiu do plano: órfão. */
function soloAtividades(cu, adj, aceites) {
  const pl = cu.plano; adj = adj || {}; const ac = soloAcAtivos(aceites, cu.id, pl.id); const out = [], orf = [], ref = [], ret = [];
  const incl = ac.filter(a => a.tipo === 'incluir' && a.incl); const temIncl = t => incl.some(a => soloTipoAtv(a.incl) === t);
  pl.atividades.forEach(a => {
    const t = soloTipoAtv(a); if (t && temIncl(t)) { ref.push(a); return; }
    const A = String(a.id);
    const prods = (a.prods || []).map((p, i) => { const key = A + '|' + i; const s = adj[key];
      const x = ac.find(q => q.tipo !== 'incluir' && q.atv && String(q.atv.id) === A && q.prod === p.prod);
      if (s !== undefined) return { p, i, key, dose: s, orig: 'sessão', ac: null, acSob: x || null };
      if (x) return { p, i, key, dose: x.dose, orig: 'análise', ac: x };
      return { p, i, key, dose: p.dose, orig: 'padrão', ac: null }; });
    const adds = Object.keys(adj).filter(k => k.indexOf(A + '|+') === 0).map(k => ({ p: adj[k], i: -1, key: k, dose: adj[k].dose, orig: 'sessão', ac: null, novo: true }));
    const vivos = prods.filter(x => x.dose !== '-').length + adds.length;
    if (!vivos && prods.some(x => x.dose === '-' && x.orig === 'análise' && x.ac.unico)) { ret.push({ a, prods: prods.concat(adds), incl: false }); return; }
    out.push({ a, prods: prods.concat(adds), incl: false }); });
  incl.forEach(x => out.push({ a: x.incl, prods: (x.incl.prods || []).map((p, i) => ({ p, i, key: x.incl.id + '|' + i, dose: x.dose, orig: 'análise', ac: x })), incl: true, ac: x }));
  ac.filter(a => a.tipo !== 'incluir').forEach(a => { const at = pl.atividades.find(q => String(q.id) === String(a.atv.id)); if (!at || !(at.prods || []).some(p => p.prod === a.prod)) orf.push(a); });
  return { atvs: out, orf, ref, ret }; }   /* ret: fora do plano pela análise, ainda lidas pela regra (R22) */

/* ---------- sugestões (a única fonte da linha, do lote, do Por quê e do "Uso no plano") ---------- */
/* ctx: {S0, ls (soloLaudos), aceites, c (cenário, para a fase da O.S.), adj (sessão do cultivo), alvo(faz, tal) → {saf, nome} (R17), todas (não omite a igual à efetiva)}
   cu: {id, saf, faz, local, tal, cultura, area, meta, plano (objeto), plantio, dt(a) → data ISO da atividade}
   Devolve {sug: [...], info: [...]}: cada sugestão diz o tipo (dose, retirar, incluir), a dose sugerida, a efetiva, a diferença no talhão,
   o laudo, a regra, as entradas e a conta; nega = motivo da R11 (a linha some no plano; o AG-02 diz por quê). */
function soloSugestoes(ctx, cu) {
  const S0 = ctx.S0, R = S0.regra, sug = [], info = []; if (!cu || !cu.plano || R.estado === 'desligada') return { sug, info };
  const pl = cu.plano, hoje = S0.hoje || soloHoje(), gar = S0.gar || {}, area = Number(cu.area) || 0;
  const L1 = soloVigente(ctx.ls, cu.faz, cu.tal, '0–20'), L2 = soloVigente(ctx.ls, cu.faz, cu.tal, '20–40');
  if (!L1 && !L2) return { sug, info };
  const SA = soloAtividades(cu, ctx.adj || {}, ctx.aceites || {});
  const alvo = ctx.alvo ? ctx.alvo(cu.faz, cu.tal) : null; const aqui = !alvo || alvo.saf === cu.saf;
  const lau = (l) => ({ id: l.id, tal: l.tal, prof: l.prof, coleta: l.coleta, lab: l.lab, ext: l.ext, por: l.por, em: l.em });
  const efDe = (x) => x ? x.dose : null;
  const vistos = {};   /* chaves que o laudo vigente calculou, mesmo iguais à efetiva; os outros usos de laudo que deixou de valer voltam ao padrão (R22) */
  const negaDe = (atvId, dt) => { if (dt && dt < hoje) return 'data passada (' + soloBr(dt) + ')'; const os = ctx.c ? soloOSDe(ctx.c, cu.id + '|' + atvId) : null;
    return (os && os.etapa !== 'A liberar') ? os.id + ' ' + (SOLO_FASE[os.etapa] || os.etapa.toLowerCase()) : ''; };
  const push = (s) => { s.k = cu.id + '|' + s.atv.id + '|' + s.prod; vistos[s.k] = 1; s.cid = cu.id; s.plano = { id: pl.id, versao: pl.versao };
    s.ef = s.efX === undefined ? null : s.efX; delete s.efX;
    const efN = (s.ef === null || s.ef === '-') ? 0 : s.ef; const sgN = s.tipo === 'retirar' ? 0 : s.sug;
    if (!ctx.todas && (s.tipo === 'retirar' ? s.ef === '-' : (s.ef !== null && s.ef !== '-' && prCmp(s.ef, s.sug) === 0))) return;   /* igual à efetiva: nada (37.2); todas: o painel compara com o rascunho */
    s.dif = (s.tipo === 'incluir' && s.ef === null) ? cenQtd(sgN, area) : prSub(cenQtd(sgN, area), cenQtd(efN, area));   /* decimal (ENG-013, revisão A9) */
    s.custo = soloR2(prMul(s.dif, Number(s.preco) || 0)); s.rot = R.rotulo;
    /* R11 na linha e, para incluir ou retirar uma correção, em qualquer calagem/gessagem já incluída no cultivo (revisão A1) */
    s.nega = negaDe(s.atv.id, s.dt) || ((s.tipo === 'incluir' || s.incl0) && ctx.c ? soloNegaCorr(ctx.c, cu.id, soloTipoAtv(s.atv), hoje) : ''); sug.push(s); };
  /* ---- calagem (R06), só com o 0–20 cm e T em cmolc/dm³ ---- */
  let fezL1 = false;
  if (L1) {
    const ix = L1.idx, V2 = soloV2(R, cu.cultura);
    if (V2 !== undefined && ix.T.v !== null && ix.V.v !== null) {
      const ents = (prod, prnt) => ['V ' + prFmtT(ix.V.v, 2) + ' % (' + ix.V.e + ')' + (ix.V.difere ? ' · laboratório ' + prFmtT(ix.V.lab, 2) + ' %: difere, vale o recalculado' : ''),
        'T ' + prFmt(ix.T.v, 2) + ' cmolc/dm³ (' + ix.T.e + ')', 'V₂ ' + V2 + ' % para ' + cu.cultura + ' (demonstração)', 'PRNT ' + prnt + ' % do ' + prod + ' (cadastro de produtos)'];
      const conta = (cal, prnt, un, dose) => ['NC = (' + V2 + ' − ' + prFmtT(ix.V.v, 2) + ') × ' + prFmt(ix.T.v, 2) + ' ÷ 100 = ' + prFmtT(cal.nc, 4) + ' t/ha',
        'Dose = ' + prFmtT(cal.nc, 4) + ' × 100 ÷ ' + prnt + ' = ' + prFmtT(cal.dose, 4) + ' t/ha' + (un === 'kg' ? ' × 1.000 = ' + prFmtT(dose, 2) + ' kg/ha' : ' → ' + prFmt(dose, 2) + ' t/ha')];
      const exCal = SA.atvs.find(x => soloTipoAtv(x.a) === 'cal');
      if (!aqui) { const c0 = soloCalagem(ix.T.v, ix.V.v, V2, 100); if (prCmp(c0.nc, 0) > 0) info.push('calagem pelo ' + L1.id + ' na ' + alvo.nome + '.'); fezL1 = true; }
      else if (exCal && !exCal.incl) {   /* plano com calagem: outra dose, ou retirar quando NC = 0 */
        exCal.prods.forEach(q => { const prnt = (gar[q.p.prod] || {}).prnt; if (!prnt || q.i < 0) return; const cal = soloCalagem(ix.T.v, ix.V.v, V2, prnt);
          const dose = soloR2(q.p.un === 'kg' ? prMul(cal.dose, 1000) : cal.dose); fezL1 = true;
          push({ tipo: prCmp(cal.nc, 0) > 0 ? 'dose' : 'retirar', regra: 'calagem', atv: { id: String(exCal.a.id), nome: exCal.a.nome, op: exCal.a.op }, i: q.i, prod: q.p.prod, un: q.p.un, grupo: q.p.grupo,
            preco: q.p.preco, padrao: q.p.dose, sug: dose, efX: efDe(q), efOrig: q.orig, laudo: lau(L1), ent: ents(q.p.prod, prnt), conta: conta(cal, prnt, q.p.un, dose), dt: cu.dt(exCal.a),
            unico: (exCal.a.prods || []).length === 1, motivo: prCmp(cal.nc, 0) > 0 ? '' : 'V já atinge ' + V2 + ' %' }); }); }
      else {   /* plano sem calagem e NC > 0: incluir (R18) com o produto padrão de correção da fazenda */
        const prod = ((S0.corr || {})[cu.faz] || {}).cal; const prnt = prod && (gar[prod] || {}).prnt; const preco = prod ? (S0.preco || {})[prod] : undefined; const it = prod ? (S0.itens || {})[prod] : null;
        const cal0 = soloCalagem(ix.T.v, ix.V.v, V2, prnt || 100);
        if (prCmp(cal0.nc, 0) > 0) { fezL1 = true;
          if (!prod || !prnt || !it) info.push(L1.id + ': calagem indicada, mas a fazenda não tem produto padrão de correção com PRNT no cadastro; nada é incluído.');
          else if (preco === undefined || preco === '') info.push(L1.id + ': ' + prod + ' sem preço de referência; nada é incluído (custo zero na safra e proposta de R$ 0 na Compra).');
          else { const cal = soloCalagem(ix.T.v, ix.V.v, V2, prnt); const dose = soloR2(it.un === 'kg' ? prMul(cal.dose, 1000) : cal.dose);
            const xa = exCal && exCal.incl ? exCal.ac : null;   /* inclusão já gravada (de qualquer laudo): data fixa e comparação (R22) */
            const porDAP = (pl.atividades || []).some(a => a.g && a.g.tipo === 'DAP'); const dap = porDAP && cu.plantio ? soloMaisDias(cu.plantio, -60) : '';
            const dt = xa ? xa.dt : (dap && dap >= hoje ? dap : (S0.viavel || hoje));
            const atv = { id: 'solo:' + L1.id + ':cal', nome: 'Calagem', op: 'Adubação a lanço', g: { tipo: 'DATA', dias: null, data: dt }, prods: [{ grupo: it.grupo, prod, dose, un: it.un, preco: Number(preco) }] };
            push({ tipo: 'incluir', regra: 'calagem', atv: { id: atv.id, nome: atv.nome, op: atv.op }, i: 0, prod, un: it.un, grupo: it.grupo, preco: Number(preco), padrao: null, sug: dose,
              efX: xa ? xa.dose : null, efOrig: xa ? 'análise' : '', substitui: xa && xa.k !== cu.id + '|' + atv.id + '|' + prod ? xa.k : '', laudo: lau(L1), ent: ents(prod, prnt), conta: conta(cal, prnt, it.un, dose).concat(
              [xa ? 'Data gravada na inclusão: ' + soloBr(dt) : (dap && dap >= hoje ? 'Data: DAP −60 = ' + soloBr(dt) : 'Data: DAP −60 ' + (dap ? '(' + soloBr(dap) + ') já passou' : 'não se aplica (plano sem DAP)') + '; vale a chegada viável de uma compra nova, ' + soloBr(dt))]),
              dt, incl: atv, unico: false }); } }
        else if (exCal && exCal.incl) { const xa = exCal.ac; const pr0 = (gar[xa.prod] || {}).prnt || prnt || 100; const cal = soloCalagem(ix.T.v, ix.V.v, V2, pr0); fezL1 = true;
          /* R22 (revisão A3): o laudo vigente dispensa a calagem incluída (NC = 0) → retirar a inclusão; aceitar desfaz o uso com o laudo no histórico */
          push({ tipo: 'retirar', incl0: true, regra: 'calagem', atv: { id: String(xa.atv.id), nome: xa.atv.nome, op: xa.atv.op }, i: 0, prod: xa.prod, un: xa.un, grupo: xa.grupo, preco: xa.preco, padrao: null, sug: 0,
            efX: xa.dose, efOrig: 'análise', laudo: lau(L1), ent: ents(xa.prod, pr0), conta: conta(cal, pr0, xa.un, 0).concat(['A Calagem incluída pelo ' + xa.laudo + ' (' + soloDoseTxt(xa.dose, xa.un) + ') deixa de ter base no ' + L1.id + ': retirar.']),
            dt: xa.dt, unico: true, motivo: 'V já atinge ' + V2 + ' %' }); } } }
    /* ---- potássio (R07), só Soja e Mehlich-1 ---- */
    const kr = R.k; const cul = prCult(cu.cultura);
    const kAtv = SA.atvs.concat(SA.ret).filter(x => !x.incl).map(x => ({ x, ps: x.prods.filter(q => q.i >= 0 && (gar[q.p.prod] || {}).k2o) })).filter(y => y.ps.length);
    if (kAtv.length) {
      if (kr.culturas.indexOf(cul) < 0) { if (!fezL1) info.push(L1.id + ' (' + cu.tal + ' · 0–20 cm): sem regra de demonstração para ' + cu.cultura + '; vale a dose do plano.'); }
      else if (L1.ext !== kr.ext) info.push(L1.id + ' (' + cu.tal + ' · 0–20 cm): extrator ' + L1.ext + ' sem regra de demonstração; vale a dose do plano.');
      else { const km = soloKmg(soloAn(L1, 'K')); let metaKg = null; try { metaKg = prMul(cu.meta, prUn(cu.cultura).massa); } catch (e) { metaKg = null; }
        if (km.v === null) info.push(L1.id + ': ' + km.nc + '; nada sugerido.');
        else if (metaKg === null) info.push(L1.id + ': ' + cu.cultura + ' sem unidade de mercado no cadastro; nada sugerido.');
        else { const r = soloK2O(km.v, metaKg, R);
          if (r.nc) info.push(L1.id + ': meta ' + prFmtT(cu.meta, 2) + ' ' + prUn(cu.cultura).prtv + ' = ' + cenNum(metaKg) + ' kg/ha, ' + r.nc + '; nada sugerido.');
          else { const nK = kAtv.reduce((n, y) => n + y.ps.length, 0); const sK = prSoma([].concat.apply([], kAtv.map(y => y.ps.map(q => prMul(q.p.dose, gar[q.p.prod].k2o)))));
            kAtv.forEach(y => y.ps.forEach(q => { const k2o = gar[q.p.prod].k2o;
              /* parcelamento (revisão A4): o K₂O da regra se reparte entre as linhas de K na proporção do K₂O do padrão; com uma linha, ela leva tudo */
              const kL = nK > 1 && prCmp(sK, 0) > 0 ? prMulDiv(r.k2o, prMul(q.p.dose, k2o), sK) : r.k2o; const dose = soloR2(prMulDiv(kL, 100, k2o));
              push({ tipo: prCmp(r.k2o, 0) > 0 ? 'dose' : 'retirar', regra: 'potássio', atv: { id: String(y.x.a.id), nome: y.x.a.nome, op: y.x.a.op }, i: q.i, prod: q.p.prod, un: q.p.un, grupo: q.p.grupo, preco: q.p.preco,
                padrao: q.p.dose, sug: dose, efX: efDe(q), efOrig: q.orig, laudo: lau(L1), dt: cu.dt(y.x.a), unico: (y.x.a.prods || []).length === 1, motivo: prCmp(r.k2o, 0) > 0 ? '' : 'K ' + r.classe,
                ent: ['K ' + prFmtT(km.v, 2) + ' mg/dm³ (' + L1.ext + ') → ' + r.classe, 'meta ' + prFmtT(cu.meta, 2) + ' ' + prUn(cu.cultura).prtv + ' = ' + cenNum(metaKg) + ' kg/ha (Planejar safra)', q.p.prod + ': ' + k2o + ' % de K₂O (cadastro de produtos)'],
                conta: ['Classe de K: ' + r.classe + ' (baixo < 40 ≤ médio < 80 ≤ adequado < 120 ≤ alto, mg/dm³)', 'Meta ' + cenNum(metaKg) + ' kg/ha → linha até ' + cenNum(Number(r.ate)) + ' kg/ha → ' + r.k2o + ' kg/ha de K₂O']
                  .concat(nK > 1 ? ['Parcelamento do plano: ' + y.x.a.nome + ' tem ' + prFmtT(prMulDiv(prMul(q.p.dose, k2o), 100, sK), 2) + ' % do K₂O do padrão → ' + prFmtT(kL, 2) + ' kg/ha de K₂O'] : [])
                  .concat([prFmtT(kL, 2) + ' ÷ ' + prFmtT(prDiv(k2o, 100), 2) + ' = ' + prFmtT(dose, 2) + ' ' + q.p.un + '/ha de ' + q.p.prod]) }); fezL1 = true; })); } } } }
    if (!fezL1 && !kAtv.length && V2 === undefined) info.push(L1.id + ' (' + cu.tal + ' · 0–20 cm): sem regra de demonstração para ' + cu.cultura + '; vale a dose do plano.');
    if (!fezL1 && V2 !== undefined && (ix.T.v === null || ix.V.v === null) && !info.length) info.push(L1.id + ' (' + cu.tal + ' · 0–20 cm): V não calculável (' + (ix.V.nc || '') + '); vale a dose do plano.');
  }
  /* ---- gessagem (R08), só com o 20–40 cm ---- */
  if (L2 && R.gesso.estado !== 'desligada') {
    const ix2 = L2.idx; const ca = soloCmolc(soloAn(L2, 'Ca')).v; const ar = soloAn(L2, 'Argila'); const argila = (ar && ar.un === '%') ? prN(prM(ar.v)) : (ar && ar.un === 'g/kg' ? prDiv(ar.v, 10) : null);
    const classe = (S0.classe || {})[prCult(cu.cultura)] || (S0.classe || {})[cu.cultura] || ''; const g = soloGesso(ca, ix2.m.v, argila, classe, R);
    if (g.gat && !aqui) info.push('gessagem pelo ' + L2.id + ' na ' + alvo.nome + '.');
    else if (g.gat && g.nc) info.push(L2.id + ': gessagem indicada, ' + g.nc + '; nada sugerido.');
    else if (g.gat) {
      const ents = ['Ca ' + (ca === null ? 'não calculável' : prFmt(ca, 2)) + ' cmolc/dm³ · m ' + soloF(ix2.m.v, 2) + ' % (20–40 cm)', 'argila ' + prFmtT(argila, 1) + ' %', cu.cultura + ': cultura ' + String(classe).toLowerCase()];
      const conta = (un, dose) => ['Gatilho: Ca < ' + prFmtT(R.gesso.ca, 2) + ' cmolc/dm³ ou m > ' + R.gesso.m + ' % → indicada', 'NG = ' + g.k + ' × ' + prFmtT(argila, 1) + ' = ' + prFmtT(g.ng, 2) + ' kg/ha' + (un === 't' ? ' = ' + prFmt(dose, 2) + ' t/ha' : '')];
      const exG = SA.atvs.find(x => soloTipoAtv(x.a) === 'ges');
      if (exG && !exG.incl) exG.prods.forEach(q => { if (q.i < 0 || !/^Gesso/.test(q.p.prod)) return; const dose = soloR2(q.p.un === 't' ? prDiv(g.ng, 1000) : g.ng);
        push({ tipo: 'dose', regra: 'gessagem', atv: { id: String(exG.a.id), nome: exG.a.nome, op: exG.a.op }, i: q.i, prod: q.p.prod, un: q.p.un, grupo: q.p.grupo, preco: q.p.preco, padrao: q.p.dose, sug: dose,
          efX: efDe(q), efOrig: q.orig, laudo: lau(L2), ent: ents, conta: conta(q.p.un, dose), dt: cu.dt(exG.a), unico: (exG.a.prods || []).length === 1 }); });
      else { const prod = ((S0.corr || {})[cu.faz] || {}).ges; const it = prod ? (S0.itens || {})[prod] : null; const preco = prod ? (S0.preco || {})[prod] : undefined;
        if (!prod || !it) info.push(L2.id + ': gessagem indicada, mas a fazenda não tem produto padrão de gesso; nada é incluído.');
        else if (preco === undefined || preco === '') info.push(L2.id + ': ' + prod + ' sem preço de referência; nada é incluído.');
        else { const xa = exG && exG.incl ? exG.ac : null; const dose = soloR2(it.un === 't' ? prDiv(g.ng, 1000) : g.ng); const dt = xa ? xa.dt : (S0.viavel || hoje);
          const atv = { id: 'solo:' + L2.id + ':ges', nome: 'Gessagem', op: 'Adubação a lanço', g: { tipo: 'DATA', dias: null, data: dt }, prods: [{ grupo: it.grupo, prod, dose, un: it.un, preco: Number(preco) }] };
          push({ tipo: 'incluir', regra: 'gessagem', atv: { id: atv.id, nome: atv.nome, op: atv.op }, i: 0, prod, un: it.un, grupo: it.grupo, preco: Number(preco), padrao: null, sug: dose, efX: xa ? xa.dose : null,
            efOrig: xa ? 'análise' : '', substitui: xa && xa.k !== cu.id + '|' + atv.id + '|' + prod ? xa.k : '', laudo: lau(L2), ent: ents, conta: conta(it.un, dose), dt, incl: atv, unico: false }); } } }
    else if (!g.gat && aqui) { const exG = SA.atvs.find(x => soloTipoAtv(x.a) === 'ges');
      if (exG && exG.incl) { const xa = exG.ac;   /* R22 (revisão A3): o 20–40 cm vigente não indica gessagem → retirar a gessagem incluída */
        push({ tipo: 'retirar', incl0: true, regra: 'gessagem', atv: { id: String(xa.atv.id), nome: xa.atv.nome, op: xa.atv.op }, i: 0, prod: xa.prod, un: xa.un, grupo: xa.grupo, preco: xa.preco, padrao: null, sug: 0,
          efX: xa.dose, efOrig: 'análise', laudo: lau(L2), ent: ['Ca ' + (ca === null ? 'não calculável' : prFmt(ca, 2)) + ' cmolc/dm³ · m ' + soloF(ix2.m.v, 2) + ' % (20–40 cm)'],
          conta: ['Gatilho: Ca < ' + prFmtT(R.gesso.ca, 2) + ' cmolc/dm³ ou m > ' + R.gesso.m + ' % → não indicada no ' + L2.id, 'A Gessagem incluída pelo ' + xa.laudo + ' (' + soloDoseTxt(xa.dose, xa.un) + ') deixa de ter base: retirar.'],
          dt: xa.dt, unico: true, motivo: 'gessagem não indicada' }); } } }
  /* R22 (revisão A3): uso da análise feito com um laudo que deixou de ser o vigente e sem conta no vigente para a mesma linha → voltar ao padrão */
  soloAcAtivos(ctx.aceites, cu.id, pl.id).filter(a => a.tipo !== 'incluir' && !vistos[a.k]).forEach(a => {
    const Lv = a.prof === '20–40' ? L2 : L1; if (!Lv || Lv.id === a.laudo) return;
    const at = (pl.atividades || []).find(q => String(q.id) === String(a.atv.id)); const i = at ? (at.prods || []).findIndex(p => p.prod === a.prod) : -1; if (i < 0) return;   /* órfão: fica com o aviso da R16 */
    if ((ctx.adj || {})[String(at.id) + '|' + i] !== undefined) return;   /* ajuste manual da sessão vale por cima (R14) */
    const p = at.prods[i]; const pq = info.find(t => t.indexOf(Lv.id) >= 0);
    push({ tipo: 'dose', desf: true, regra: a.regra, atv: { id: String(at.id), nome: at.nome, op: at.op }, i, prod: a.prod, un: p.un, grupo: p.grupo, preco: p.preco, padrao: p.dose, sug: p.dose,
      efX: a.dose, efOrig: 'análise', laudo: lau(Lv), dt: cu.dt(at), unico: (at.prods || []).length === 1, motivo: 'padrão do plano',
      ent: ['uso da análise: ' + (a.dose === '-' ? 'retirado' : soloDoseTxt(a.dose, a.un)) + ' pelo ' + a.laudo + ', que deixou de ser o laudo vigente (vale o ' + Lv.id + ')'],
      conta: [pq || (Lv.id + ': nenhuma conta para ' + a.prod + '.'), 'Sem conta no laudo vigente, vale a dose do plano: ' + soloDoseTxt(p.dose, p.un) + '.'] }); });
  return { sug, info }; }

/* ---------- O.S. de uma chave cultivo|atividade (R11): a ordem emitida pela tela (osc.novo.keys) ou a do registro (SOLO0.osChave) ---------- */
function soloOSQ(c, pred) { const os = (c && c.ordens) || {}; const out = []; const add = (id, k) => { if (id && os[id] && os[id].etapa !== 'Canceladas' && !out.some(x => x.id === id)) out.push({ id, etapa: os[id].etapa, k }); };
  for (const id in os) { const o = os[id]; ((o.osc && o.osc.novo && o.osc.novo.keys) || []).filter(pred).forEach(k => add(id, k)); }
  const oc = (typeof SOLO0 !== 'undefined' && SOLO0.osChave) || {}; Object.keys(oc).filter(pred).forEach(k => add(oc[k], k));
  if (typeof OSD !== 'undefined' && OSD.ords) OSD.ords.forEach(b => (b.keys || []).filter(pred).forEach(k => add(b.id, k)));
  return out; }
function soloOSDe(c, ck) { return soloOSQ(c, k => k === ck)[0] || null; }
function soloNega(c, it, hoje) { if (it.dt && it.dt < (hoje || soloHoje())) return 'data passada (' + soloBr(it.dt) + ')';
  const os = soloOSDe(c, it.cid + '|' + it.atv.id); return (os && os.etapa !== 'A liberar') ? os.id + ' ' + (SOLO_FASE[os.etapa] || os.etapa.toLowerCase()) : ''; }
/* R11 da correção incluída (revisão A1): com qualquer calagem (ou gessagem) incluída pela análise no cultivo, de qualquer laudo, já com O.S. fora de
   A liberar ou com a data passada, não se inclui outra, não se troca a dose e não se retira. Dano evitado: segunda calagem no mesmo talhão, ou trocar
   a que já foi aprovada, reservada ou feita. A chave da O.S. de uma correção incluída é cultivo|solo:<laudo>:cal (ou :ges). */
function soloKCorr(k, cid, tipo) { return String(k).indexOf(cid + '|solo:') === 0 && String(k).slice(-(tipo.length + 1)) === ':' + tipo; }
function soloNegaCorr(c, cid, tipo, hoje) { if (!tipo) return '';
  const os = soloOSQ(c, k => soloKCorr(k, cid, tipo)).find(o => o.etapa !== 'A liberar');
  if (os) return os.id + ' ' + (SOLO_FASE[os.etapa] || os.etapa.toLowerCase()) + ' (' + (tipo === 'ges' ? 'gessagem' : 'calagem') + ' do ' + String(os.k).split(':')[1] + ')';
  const a = soloAcAtivos(((c && c.solo) || {}).aceites, cid).find(x => x.tipo === 'incluir' && soloTipoAtv(x.incl) === tipo && x.dt && x.dt < (hoje || soloHoje()));
  return a ? 'data passada (' + soloBr(a.dt) + ', ' + (tipo === 'ges' ? 'gessagem' : 'calagem') + ' do ' + a.laudo + ')' : ''; }

/* ---------- comandos sobre c.solo (só dentro de cenMudar): chave de quem inicia (R13), papel conferido no cadastro (cenExige) ---------- */
function soloRecibo(c, chave, cont, fn) {
  const S = cenSolo(c); if (!chave) throw new Error('Comando sem chave de quem inicia: nada foi gravado.');
  const h = JSON.stringify(cont); const r0 = S.recibos[chave];
  if (r0) { if (r0.h === h) return { msg: 'Já registrado: ' + r0.r.msg + ' Nada mudou.', id: r0.r.id, repetido: true };
    throw new Error('Conflito: a chave ' + chave + ' já gravou outro conteúdo. Nada foi gravado.'); }
  const r = fn(S) || {}; S.recibos[chave] = { h, r: { msg: r.msg || '', id: r.id || '' }, em: soloAgora() }; return r; }
function soloTodosLaudos(c) { return ((typeof SOLO0 !== 'undefined' && SOLO0.laudos) || []).concat(Object.values(((c && c.solo) || {}).laudos || {})); }
function soloRegistrar(c, d, chave, ator) {   /* Registrar laudo: nasce Aguardando validação (o OCR nunca valida); amostra repetida é recusada */
  const quem = cenQuem(ator, null, 'Registrar laudo');
  return soloRecibo(c, chave, { cmd: 'registrar', d }, S => {
    const f = (k, t) => { if (!d[k] || !String(d[k]).trim()) throw new Error('Informe ' + t + '. Nada foi gravado.'); };
    f('faz', 'a fazenda'); f('tal', 'o talhão'); f('coleta', 'a data da coleta'); f('lab', 'o laboratório'); f('ext', 'o extrator');
    if (SOLO_PROFS.indexOf(d.prof) < 0) throw new Error('Informe a profundidade (0–20 ou 20–40 cm). Nada foi gravado.');
    if (d.coleta > soloHoje()) throw new Error('A coleta não pode ser depois de hoje (' + soloBr(soloHoje()) + '). Nada foi gravado.');
    const an = (d.an || []).filter(x => x && x.a && soloNum(x.v) !== null);
    if (!an.length) throw new Error('Informe os valores do laudo. Nada foi gravado.');
    an.forEach(x => { if (typeof soloNum(x.v) !== 'string') throw new Error('Valor de ' + x.a + ' inválido: use um número. Nada foi gravado.'); });
    const dup = soloTodosLaudos(c).find(l => l.faz === d.faz && l.tal === d.tal && l.prof === d.prof && l.coleta === d.coleta && l.lab === d.lab);
    if (dup) throw new Error('Esta amostra já está registrada como ' + dup.id + ' (mesmo talhão, profundidade, coleta e laboratório). Nada foi gravado.');
    const n = soloTodosLaudos(c).reduce((m, l) => Math.max(m, Number(String(l.id).replace(/\D/g, '')) || 0), 0) + 1; const id = 'LAU-' + n;
    S.laudos[id] = { id, tipo: 'solo', faz: d.faz, tal: d.tal, prof: d.prof, coleta: d.coleta, lab: d.lab, ext: d.ext, area: d.area || '', zona: '', lab_idx: {}, arq: d.arq || '',
      an: an.map(x => ({ a: x.a, v: soloNum(x.v), un: x.un || '', met: x.met || '', ld: x.ld || '', q: x.q || '' })), sit: 'Aguardando validação', por: '', em: '', reg: { por: quem, em: soloAgora() }, novo: true };
    return { msg: id + ' registrado por ' + quem + ': aguarda a validação do agrônomo.', id }; }); }
function soloCorrigir(c, id, a, v, un, chave, ator) {   /* corrige valor e unidade de um analito; o original do PDF não muda; o laudo volta a Aguardando validação */
  const quem = cenQuem(ator, null, 'Corrigir o ' + id);
  return soloRecibo(c, chave, { cmd: 'corrigir', id, a, v, un }, S => {
    const l = soloTodosLaudos(c).find(x => x.id === id); if (!l) throw new Error('Laudo ' + id + ' não encontrado.');
    if (!soloAn(l, a)) throw new Error(a + ' não está no ' + id + '.'); const n = soloNum(v); if (typeof n !== 'string') throw new Error('Informe o valor de ' + a + ' com um número.');
    if (!un) throw new Error('Informe a unidade de ' + a + '.');
    (S.corr[id] || (S.corr[id] = {}))[a] = { v: n, un, por: quem, em: soloAgora() }; S.st[id] = { sit: 'Aguardando validação' };
    return { msg: a + ' do ' + id + ' corrigido para ' + prFmtT(n, 3) + ' ' + un + ': o laudo volta a Aguardando validação; o PDF original não muda.', id }; }); }
function soloValidar(c, id, chave, ator) {   /* só o agrônomo valida (R03); analito sem unidade impede */
  const quem = cenExige(ator, 'agronomo', 'Validar o ' + id);
  return soloRecibo(c, chave, { cmd: 'validar', id }, S => {
    const l = soloLaudos(c, soloS0(true)).find(x => x.id === id); if (!l) throw new Error('Laudo ' + id + ' não encontrado.');
    if (l.sit === 'Inconsistente') throw new Error(id + ' inconsistente (' + l.motivo + '): corrija a unidade antes de validar. Nada foi alterado.');
    if (l.sit !== 'Aguardando validação') throw new Error(id + ' não está aguardando validação (' + l.sit + ').');
    S.st[id] = { sit: 'Validado', por: quem, em: soloAgora() };
    return { msg: id + ' validado por ' + quem + '.', id }; }); }
/* laudos como o comando os vê (o SOLO0 da tela + c.solo); sem SOLO0 (tela sem a análise), null: o comando de uso recusa em vez de confiar no item */
function soloS0(ok) { if (typeof SOLO0 === 'undefined') return ok ? { laudos: [], regra: { validade: { meses: 24 } }, hoje: soloHoje() } : null;
  return { laudos: SOLO0.laudos || [], regra: SOLO0.regra || { validade: { meses: 24 } }, hoje: soloHoje() }; }
/* o comando reconfere o item que a tela mandou (revisão A2: o servidor é a autoridade): R11 na chave e na correção incluída do cultivo, e o laudo
   do item tem de ser o vigente do talhão e da profundidade (R02). Devolve '' ou o motivo. Dano evitado: gravar dose de laudo substituído ou não
   validado, ou duas calagens vivas, a partir de um painel aberto antes da mudança. */
function soloConfere(c, it, ls) {
  const ng = soloNega(c, it); if (ng) return ng;
  if (it.tipo === 'incluir' || it.incl0) { const nc = soloNegaCorr(c, it.cid, soloTipoAtv(it.atv)); if (nc) return nc; }
  const id = (it.laudo || {}).id; const l = (ls || []).find(x => x.id === id); if (!l) return 'laudo ' + (id || '—') + ' não encontrado';
  const v = l.sit === 'Validado' ? soloVigente(ls, l.faz, l.tal, l.prof) : null; if (v && v.id === l.id) return '';
  return 'a análise mudou: ' + l.id + ' ' + (l.sit === 'Validado' ? (l.zona ? 'é laudo por zona' : 'não é o laudo vigente') : l.sit.toLowerCase() + (l.motivo ? (l.sit === 'Substituído' ? ' ' + l.motivo : ' (' + l.motivo + ')') : '')); }
function soloGrava(S, it, quem, em, chave) {
  if (it.incl0 || it.desf) return soloDesf(S, it.k, (it.incl0 ? 'retirada pelo ' : 'voltou ao padrão pelo ') + it.laudo.id, quem, em);   /* R22: retirar a inclusão ou voltar ao padrão desfaz o uso, com o laudo vigente no histórico */
  const a0 = S.aceites[it.k];
  if (a0 && a0.st === 'ativo' && a0.dose === (it.tipo === 'retirar' ? '-' : it.sug)) return false;   /* um aceite por chave: nunca soma */
  /* uma correção incluída por cultivo e tipo (revisão A2): a nova substitui toda outra ativa do mesmo tipo, sem depender do que a tela mandou */
  if (it.tipo === 'incluir') soloAcAtivos(S.aceites, it.cid).filter(a => a.k !== it.k && a.tipo === 'incluir' && soloTipoAtv(a.incl) === soloTipoAtv(it.incl)).forEach(a => soloDesf(S, a.k, 'substituída pelo ' + it.laudo.id, quem, em));
  const hist = a0 ? (a0.hist || []).concat([{ st: a0.st === 'ativo' ? 'substituído' : a0.st, dose: a0.dose, em }]) : [];
  S.aceites[it.k] = { k: it.k, cid: it.cid, tipo: it.tipo, atv: it.atv, prod: it.prod, un: it.un, grupo: it.grupo || '', preco: it.preco, dose: it.tipo === 'retirar' ? '-' : it.sug, unico: !!it.unico, padrao: it.padrao,
    incl: it.tipo === 'incluir' ? it.incl : null, plano: it.plano, laudo: it.laudo.id, prof: it.laudo.prof, regra: it.regra, ent: it.ent, conta: it.conta, dt: it.dt, st: 'ativo', por: quem, em, chave, hist };
  return true; }
function soloDesf(S, k, motivo, quem, em) { const a = S.aceites[k]; if (!a || a.st !== 'ativo') return false; a.st = motivo || 'desfeito'; a.hist = (a.hist || []).concat([{ st: a.st, por: quem, em }]); return true; }
function soloItemTxt(it) { return it.incl0 ? 'retirar a ' + it.atv.nome + ' incluída' : (it.tipo === 'retirar' ? it.prod + ' retirado' : (it.tipo === 'incluir' ? it.atv.nome + ' incluída (' + soloDoseTxt(it.sug, it.un) + ')' : it.prod + ' ' + soloDoseTxt(it.sug, it.un))); }
function soloAcTxt(a) { return a.tipo === 'incluir' ? a.atv.nome + ' incluída pelo ' + a.laudo : a.prod + ' ' + (a.dose === '-' ? 'retirado' : soloDoseTxt(a.dose, a.un)) + ' pelo ' + a.laudo; }
/* R11 também para desfazer (revisão A5): o uso com O.S. fora de A liberar ou data passada não se desfaz. Dano evitado: o plano e a demanda voltarem
   ao padrão enquanto a O.S. executa a dose da análise */
function soloNegaDesf(c, S, k) { const a = S.aceites[k]; const ng = (a && a.st === 'ativo') ? soloNega(c, a) : ''; return ng ? 'Desfazer o uso da análise (' + soloAcTxt(a) + '): não aplicável, ' + ng + '. Nada foi gravado.' : ''; }
/* Salvar do painel de insumos: grava os aceites e os desfeitos de um cultivo de uma vez (tudo ou nada). Usar não exige papel (D-07) e grava quem foi. */
function soloAceitar(c, d, chave, ator) {
  const quem = cenQuem(ator, null, 'Usar a sugestão da análise');
  return soloRecibo(c, chave, { cmd: 'aceitar', d }, S => { const em = soloAgora(); let n = 0, m = 0; const S0 = soloS0();
    if ((d.aceitar || []).length && !S0) throw new Error('A análise de solo não está carregada nesta tela: nada foi gravado.');
    const ls = S0 ? soloLaudos(c, S0) : [];
    (d.aceitar || []).forEach(it => { const ng = soloConfere(c, it, ls); if (ng) throw new Error(soloItemTxt(it) + ' no ' + (it.local || it.cid) + ': não aplicável, ' + ng + '. ' + (/^a análise mudou/.test(ng) ? 'Reabra o painel. ' : '') + 'Nada foi gravado.'); });
    (d.desfazer || []).forEach(x => { const ng = soloNegaDesf(c, S, x.k); if (ng) throw new Error(ng); });
    (d.desfazer || []).forEach(x => { if (soloDesf(S, x.k, x.motivo, quem, em)) m++; });
    (d.aceitar || []).forEach(it => { if (soloGrava(S, it, quem, em, chave)) n++; });
    return { msg: (n ? n + (n > 1 ? ' sugestões da análise usadas' : ' sugestão da análise usada') : '') + (n && m ? ' · ' : '') + (m ? m + (m > 1 ? ' usos desfeitos' : ' uso desfeito') : '') + (n || m ? '.' : 'Nada mudou.') }; }); }
/* lote (Sugestões pelas análises): cada linha que a R11 nega falha sozinha e diz o motivo; as outras gravam (uma chave para o lote) */
function soloAceitarLote(c, itens, chave, ator) {
  const quem = cenQuem(ator, null, 'Usar as sugestões da análise');
  return soloRecibo(c, chave, { cmd: 'lote', itens: (itens || []).map(it => [it.k, it.tipo, it.sug, (it.laudo || {}).id, !!(it.incl0 || it.desf)]) }, S => { const em = soloAgora(); const ok = [], neg = [];
    const S0 = soloS0(); if (!S0) throw new Error('A análise de solo não está carregada nesta tela: nada foi gravado.'); const ls = soloLaudos(c, S0);
    (itens || []).forEach(it => { const ng = soloConfere(c, it, ls); if (ng) { neg.push({ k: it.k, motivo: ng }); return; } soloGrava(S, it, quem, em, chave); ok.push(it); });
    if (!ok.length) throw new Error('Nenhuma sugestão gravada: ' + neg.map(x => x.motivo).join('; ') + '.');
    const ef = {}; ok.forEach(it => { const e = ef[it.prod] || (ef[it.prod] = { un: it.un, q: 0 }); e.q = prSoma([e.q, it.dif]); });
    return { msg: ok.length + (ok.length > 1 ? ' sugestões usadas' : ' sugestão usada') + ' · ' + Object.keys(ef).map(p => p + ' ' + soloQtdTxt(ef[p].q, ef[p].un, true)).join(' · ') + (neg.length ? '. Não gravadas (' + neg.length + '): ' + neg.map(x => x.motivo).join('; ') : '') + '.',
      neg }; }); }
function soloDesfazer(c, k, motivo, chave, ator) {
  const quem = cenQuem(ator, null, 'Desfazer o uso da análise');
  return soloRecibo(c, chave, { cmd: 'desfazer', k, motivo }, S => { const ng = soloNegaDesf(c, S, k); if (ng) throw new Error(ng);
    if (!soloDesf(S, k, motivo || 'desfeito', quem, soloAgora())) throw new Error('Nada a desfazer: o uso não está ativo.');
    return { msg: 'Uso da análise desfeito: vale a dose do plano.' }; }); }
/* água no solo: medição por talhão ou zona, com data, profundidade, método, unidade, fonte e responsável (sem cadastro paralelo) */
function soloMedir(c, d, chave, ator) {
  const quem = cenQuem(ator, null, 'Registrar medição de água no solo');
  return soloRecibo(c, chave, { cmd: 'medir', d }, S => {
    const f = (k, t) => { if (!d[k] || !String(d[k]).trim()) throw new Error('Informe ' + t + '. Nada foi gravado.'); };
    f('faz', 'a fazenda'); f('tal', 'o talhão'); f('data', 'a data'); f('prof', 'a profundidade amostrada'); f('met', 'o método'); f('un', 'a unidade'); f('fonte', 'a fonte ou o laboratório'); f('resp', 'o responsável');
    if (typeof soloNum(d.cc) !== 'string') throw new Error('Informe a capacidade de campo com um número. Nada foi gravado.');
    if (d.pmp !== '' && d.pmp !== undefined && typeof soloNum(d.pmp) !== 'string') throw new Error('Ponto de murcha inválido: use um número ou deixe vazio. Nada foi gravado.');
    if (typeof soloNum(d.z) !== 'string') throw new Error('Informe a profundidade efetiva das raízes (cm). Nada foi gravado.');
    if (d.data > soloHoje()) throw new Error('A medição não pode ser depois de hoje (' + soloBr(soloHoje()) + '). Nada foi gravado.');
    const todos = ((typeof SOLO0 !== 'undefined' && SOLO0.agua) || []).concat(Object.values(S.agua));
    const dup = todos.find(m => m.faz === d.faz && m.tal === d.tal && (m.zona || '') === (d.zona || '') && m.data === d.data && m.prof === d.prof && m.met === d.met);
    if (dup) throw new Error('Esta medição já está registrada como ' + dup.id + '. Nada foi gravado.');
    const id = 'AGS-' + String(todos.reduce((mx, m) => Math.max(mx, Number(String(m.id).replace(/\D/g, '')) || 0), 0) + 1).padStart(3, '0');
    S.agua[id] = { id, faz: d.faz, tal: d.tal, zona: d.zona || '', data: d.data, prof: d.prof, z: soloNum(d.z), met: d.met, un: d.un, cc: soloNum(d.cc), pmp: soloNum(d.pmp) || '', fonte: d.fonte, resp: d.resp, reg: { por: quem, em: soloAgora() } };
    const cad = soloCAD(S.agua[id]);
    return { msg: id + ' registrada: ' + (cad.v !== null ? 'CAD ' + prFmtT(cad.v, 1) + ' mm' : 'CAD não calculável (' + cad.nc + ')') + '. Referência para a Irrigação, não a lâmina.', id }; }); }

/* ---------- leitura para a O.S. e o Mapa (sem SOLO0): origem da dose e selo "Plano mudou" (R20, R21, A21) ---------- */
function soloAcDaChave(c, ck, prod) { const A = Object.values(((c && c.solo) || {}).aceites || {});
  const at = A.find(a => a.st === 'ativo' && a.cid + '|' + a.atv.id === ck && a.prod === prod); if (at) return at;
  const m = /^(.+)\|solo:[^|]+:(cal|ges)$/.exec(ck);   /* calagem/gessagem incluída substituída por laudo mais novo (revisão A1) */
  const nv = m ? A.find(a => a.st === 'ativo' && a.tipo === 'incluir' && a.cid === m[1] && soloTipoAtv(a.incl) === m[2] && a.prod === prod) : null; if (nv) return nv;
  const x = A.find(a => a.cid + '|' + a.atv.id === ck && a.prod === prod);   /* uso que a análise desfez: o plano voltou ao padrão ou a inclusão saiu (R22, revisão A3) */
  return (x && /^(voltou ao padrão|retirada) pelo /.test(x.st)) ? Object.assign({}, x, { dose: /^retirada/.test(x.st) ? '-' : x.padrao, laudo: x.st.split(' pelo ')[1] }) : null; }

/* ---------- contexto a partir dos dados gravados (AG-02 e testes): cultivos e planos do SOLO0 e aceites do cenário, sem a sessão do Planejar safra ---------- */
function soloDataAtv(x, a, pl) { const g = a.g || {}; if (g.tipo === 'DAP') return soloMaisDias(x.plantio, g.dias); if (g.tipo === 'DATA') return g.data;   /* a mesma regra de safra.js dataAtv */
  let col = x.colheita; if (!col) { const ca = (pl.atividades || []).find(q => /^Colheita/.test(q.op)); col = (ca && ca.g.tipo === 'DAP') ? soloMaisDias(x.plantio, ca.g.dias) : ((ca && ca.g.tipo === 'DATA') ? ca.g.data : x.plantio); }
  return soloMaisDias(col, g.tipo === 'DAPC' ? g.dias : -g.dias); }
function soloCultivoBase(S0, x) { const pl = (S0.planos || {})[x.plano]; if (!pl || pl.cultura !== x.cultura) return null;
  return Object.assign({}, x, { plano: pl, dt: a => soloDataAtv(x, a, pl) }); }
/* R17 (D-19): a correção de um laudo vai para os cultivos do talhão na primeira safra aberta que o tem, pela data de plantio */
/* o cultivo do talhão na primeira safra aberta, pela data de plantio (R17; também a cultura do V₂ no Mapa) */
function soloCultivoAlvo(cults, safras, faz, tal) { return (cults || []).filter(x => x.faz === faz && x.tal === tal && !((safras || {})[x.saf] || {}).ro).sort((a, b) => a.plantio < b.plantio ? -1 : (a.plantio > b.plantio ? 1 : 0))[0] || null; }
function soloAlvo(cults, safras) { return (faz, tal) => { const x = soloCultivoAlvo(cults, safras, faz, tal);
  return x ? { saf: x.saf, nome: ((safras || {})[x.saf] || {}).nome || x.saf } : null; }; }
function soloCtxBase(c, S0) { return { S0, ls: soloLaudos(c, S0), aceites: ((c && c.solo) || {}).aceites || {}, c, adj: {}, alvo: soloAlvo(S0.cult || [], S0.safras) }; }
/* "Uso no plano" de um laudo (AG-02): uma linha por sugestão dos cultivos do talhão, com o estado (em uso, disponível, não aplicável, sem regra) */
function soloUsoNoPlano(c, S0, l) { const ctx = soloCtxBase(c, S0); const out = []; const A = ctx.aceites;
  (S0.cult || []).filter(x => x.faz === l.faz && x.tal === l.tal).forEach(x => { const cu = soloCultivoBase(S0, x); if (!cu) return;
    const R = soloSugestoes(ctx, cu);
    R.sug.filter(s => s.laudo.id === l.id).forEach(s => out.push({ s, cu, st: s.nega ? 'não aplicável: ' + s.nega : 'disponível' }));
    Object.values(A).filter(a => a.st === 'ativo' && a.cid === cu.id && a.laudo === l.id).forEach(a => { if (out.some(o => o.s.k === a.k && o.st === 'disponível')) { const o = out.find(q => q.s.k === a.k); o.st = 'em uso (outra dose) desde ' + soloDdMm(a.em) + ' por ' + String(a.por).split(' ')[0]; o.ac = a; return; }
      out.push({ s: { k: a.k, tipo: a.tipo, atv: a.atv, prod: a.prod, un: a.un, padrao: a.padrao, sug: a.dose === '-' ? 0 : a.dose, ef: a.dose, laudo: { id: a.laudo }, regra: a.regra, ent: a.ent, conta: a.conta, dt: a.dt, dif: 0 }, cu, ac: a,
        st: 'em uso desde ' + soloDdMm(a.em) + ' por ' + String(a.por).split(' ')[0] }); });
    if (l.sit === 'Validado' && !R.sug.some(s => s.laudo.id === l.id)) R.info.filter(t => t.indexOf(l.id) >= 0).forEach(t => out.push({ s: null, cu, st: 'sem regra', info: t })); });
  return out; }
/* "No plano" do laudo (AG-02 e Mapa): sugestões disponíveis e em uso (a recomendação pendente é a disponível que ainda não está em uso) */
function soloUsoCont(u) { const n = u.filter(x => x.s && !/^não aplicável/.test(x.st)).length, e = u.filter(x => x.ac).length; return { n, e }; }
function soloNoPlano(l, u) { if (l.tipo !== 'solo' || l.sit !== 'Validado') return { t: '—', c: '' }; const k = soloUsoCont(u);
  if (!k.n && !k.e) return { t: 'sem sugestão', c: '' }; return { t: k.n + (k.n > 1 ? ' sugestões' : ' sugestão') + (k.e ? ' · ' + k.e + ' em uso' : ''), c: k.e ? 'green' : 'blue' }; }

/* ---------- Mapa (IN-04, camada Análises de solo · pedido do proprietário de 13/10/2026): a leitura essencial do talhão ----------
   Laudo do talhão: o de solo de 0–20 cm de coleta mais recente que não foi substituído (sem ele, o de 20–40 cm); o da outra profundidade
   vem junto (sub) e os demais (foliar, substituídos) só na lista. Sem laudo de solo: 'sem' (ausente não é zero; vale a dose do plano).
   k: 'corrigir' = validado, 0–20 cm e V abaixo do V₂ da cultura do próximo cultivo (a mesma conta da calagem, CAL-10: NC > 0);
   'dia' = validado (sem cultivo, sem V₂ ou sem V calculável não vira 'corrigir'); 'validar' = aguardando validação ou inconsistente;
   'vencida' = vencido. A cor e o texto da camada saem daqui; nenhuma regra nova. */
function soloLeituraTal(ls, S0, faz, tal) {
  const R = S0.regra; const doTal = ls.filter(l => l.faz === faz && l.tal === tal);
  const so = doTal.filter(l => l.tipo === 'solo' && l.sit !== 'Substituído');
  const rec = p => so.filter(l => l.prof === p).sort((a, b) => a.coleta < b.coleta ? 1 : (a.coleta > b.coleta ? -1 : 0))[0] || null;
  const l = rec('0–20') || rec('20–40'); const sub = l ? rec(l.prof === '0–20' ? '20–40' : '0–20') : null;
  const outros = doTal.filter(x => x !== l && x !== sub).sort((a, b) => a.coleta < b.coleta ? 1 : -1);
  const cu = soloCultivoAlvo(S0.cult, S0.safras, faz, tal); const V2 = cu ? soloV2(R, cu.cultura) : undefined;
  if (!l) return { k: 'sem', l: null, sub: null, outros, cu, V: null, V2, abaixo: null };
  const ix = l.idx || {}; const V = ix.V && ix.V.v !== null && ix.V.v !== undefined ? ix.V.v : null;
  /* abaixo: V do 0–20 cm abaixo do V₂ (NC da calagem > 0), em qualquer situação do laudo; null = não se compara (sem V, sem V₂ ou 20–40 cm) */
  const abaixo = (l.prof === '0–20' && V !== null && V2 !== undefined && ix.T && ix.T.v !== null) ? prCmp(soloCalagem(ix.T.v, V, V2, 100).nc, 0) > 0 : null;
  let k = l.sit === 'Validado' ? 'dia' : (l.sit === 'Vencido' ? 'vencida' : 'validar');
  if (k === 'dia' && abaixo) k = 'corrigir';
  return { k, l, sub, outros, cu, V, V2, abaixo }; }
