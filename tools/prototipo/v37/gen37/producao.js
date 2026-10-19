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
/* estoque e pedido: unidade de estoque (est) quando a cultura tem uma (mamão em kg, coco em fruto); senão a de produção.
   prod (opcional, o produto do lote): o estágio de campo (café da roça, u.proc) fica na unidade de campo (L), sem saca derivada:
   a saca só sai do rendimento medido no beneficiamento (R-09; COLH-C01: 12.000 L não são "200 sc") */
function prCampo(cultura, prod) { const u = prUn(cultura); return !!(u.campo && prod && prod === u.proc); }
function prEstUn(cultura, prod) { const u = prUn(cultura); return prCampo(cultura, prod) ? u.campo : (u.est || u.un); }
function prEstQ(cultura, base, prod) { const u = prUn(cultura); return (u.est || prCampo(cultura, prod)) ? prN(prM(base)) : prQ(cultura, base); }
function prEstTxt(cultura, base, d, prod) { return prFmtT(prEstQ(cultura, base, prod), d === undefined ? 2 : d) + ' ' + prEstUn(cultura, prod); }
function prLoteTxt(L, base, d) { return prEstTxt(L.cultura, base, d, L.prod); }   /* quantidade de um lote, na unidade do estágio dele */
function prEstBase(cultura, q) { const u = prUn(cultura); return u.est ? prN(prM(q)) : prMul(q, u.massa); }   /* quantidade digitada na unidade de estoque → base */
/* produtividade = produção na base física ÷ área colhida, na unidade da cultura (R-04); laranja mostra t/ha ao lado.
   op (UNID-PROD, opcional): a unidade escolhida na tela (prUnpOpcoes); com op o texto sai do conversor único (prUnpTxt). Sem op, o texto
   de hoje: as mensagens de comando não leem preferência de tela (R-U12) */
function prPrtv(cultura, base, ha) { if (!(Number(ha) > 0)) return null; return prDiv(prQ(cultura, base), ha); }
function prPrtvTxt(cultura, base, ha, op) { if (op !== undefined) return prUnpTxt(prUnpInd(cultura, { kg: base, area: ha }, op));
  const u = prUn(cultura); const p = prPrtv(cultura, base, ha); if (p === null) return '—';
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
/* quem age (integração CONF × COLH): o que tem papel no catálogo de Configurações vem do papel vigente, nunca de nome fixo (CONF R2, R7):
   publicar previsão = AL-17 (texto pelo g2alcQuem); receber na fazenda onde recebe o almoxarife = o almoxarife ativo (cenAlmox). Qualidade, Comercial
   e Lúcia ainda não estão no CD-04 nem no catálogo de papéis: seguem o registro da colheita (PRDC.quem) até entrarem (CONF-D41). */
function prQuem(k) { if (k === 'ag' && typeof g2alcQuem === 'function') { const q = g2alcQuem('AL-17'); if (q) return q; } return (PRDC.quem || {})[k] || ''; }
function prRec(faz) { const r = ((PRDC.quem || {}).rec || {})[faz] || 'Recebimento'; return (/\(almoxarife\)$/.test(r) && typeof cenAlmox === 'function') ? cenAlmox() : r; }
/* quem pesa, estorna e descarta (revisão CONF 10/10, R14): onde quem recebe é um papel (almoxarife: Santa Rita e Boa Vista), grava o perfil de quem age
   (Ver como; omitido, o da sessão; "Rui (almoxarife)" vale pelo 1º nome) e recusa sem gravar se ele não tem o papel. Nunca o almoxarife deduzido:
   o texto "quem recebe" (prRec) diz quem deve agir, não quem agiu. Lúcia (Lagoa Grande) segue o registro da colheita até entrar no CD-04 (CONF-D41).
   Sem o bloco de perfis (página sem g2lib), o nome recebido. Dano evitado: carga pesada, estornada ou descartada em nome de quem não agiu. */
function prAtorRec(faz, quem, acao) { const r = ((PRDC.quem || {}).rec || {})[faz] || 'Recebimento';
  if (!/\(almoxarife\)$/.test(r) || typeof cenExige !== 'function' || typeof g2perfil !== 'function') return (typeof quem === 'string' && quem) || prRec(faz);
  const P = (quem && typeof quem === 'object') ? quem : (quem ? String(quem).split(/[\s(]/)[0] : g2perfil()); return cenExige(P, 'almoxarife', acao); }
/* ator de comando com alçada (publicar previsão, AL-17): o perfil de quem age (Ver como; "Ana (agrônoma)" ou {k:'Ana'} pelo 1º nome); sem papel, recusa sem gravar.
   Sem o bloco de alçadas (página sem g2lib), o nome recebido. */
function prAtorAlc(quem, al, acao) { if (typeof cenExigeAlc !== 'function' || typeof g2alc !== 'function' || !g2alc(al)) return (typeof quem === 'string' && quem) || prQuem('ag');
  const P = (quem && typeof quem === 'object') ? quem : (quem ? String(quem).split(/[\s(]/)[0] : g2perfil()); return cenExigeAlc(P, al, acao); }
/* app de campo respeita o acesso (CONF R2): operador desativado não grava contagem nem carga; o que já está na fila do aparelho envia */
function prAppAtivo(c, via) { if (via === 'app' && typeof cenAppAtivo === 'function') cenAppAtivo(c); }
function prEhColheita(o) { return /^Colheita/.test(String((o && o.tipo) || '')); }
/* cultivo da O.S.: a ordem nova guarda o cultivo (#nova:); a semente vem do registro; senão o 1º cultivo aberto do talhão */
function prCultDaOS(c, o) { if (!o) return ''; const nv = o.osc && o.osc.novo; if (nv && nv.cult) return nv.cult;
  if ((PRDC.osCult || {})[o.id]) return PRDC.osCult[o.id]; return ((PRDC.cultDe || {})[o.talhao] || [])[0] || ''; }
function prFazDaOS(c, o) { const k = PRDC.cult[prCultDaOS(c, o)]; return (o && o.osc && o.osc.novo && o.osc.novo.faz) || (k && k.faz) || ''; }
function prOsCult(c, cid) { return Object.keys(c.ordens || {}).map(k => c.ordens[k]).filter(o => prEhColheita(o) && o.etapa !== 'Canceladas' && prCultDaOS(c, o) === cid); }
function prDdMm(iso) { const a = String(iso || '').split('-'); return a.length === 3 ? a[2] + '/' + a[1] : ''; }
/* dd/mm → ISO no ano de hoje; mais de 180 dias à frente é do ano anterior (30/12 lido em 02/01); 1 dia à frente continua futuro e é recusado */
function prIsoDe(ddmm, hoje) { const m = /^(\d\d)\/(\d\d)$/.exec(String(ddmm || '').trim()); if (!m) return ''; const h = hoje || prHoje(); let y = Number(h.slice(0, 4));
  if (y + '-' + m[2] + '-' + m[1] > prDiaMais(h, 180)) y -= 1; return y + '-' + m[2] + '-' + m[1]; }
/* semana N sem ano (tipo "Colheita · semana 2"): o ano que põe a semana mais perto de hoje (S02 lida em 26/09/2026 = 2027-W02) */
function prSemAno(n, hoje) { const h = hoje || prHoje(); const y = Number(h.slice(0, 4)); const t = Date.parse(h + 'T12:00:00Z');
  return [y - 1, y, y + 1].map(a => a + '-W' + String(n).padStart(2, '0')).sort((a, b) => Math.abs(Date.parse(prSemIni(a) + 'T12:00:00Z') - t) - Math.abs(Date.parse(prSemIni(b) + 'T12:00:00Z') - t))[0]; }
/* responsável da O.S. (ordem nova nasce com '—' até liberar): senão quem colhe (Sérgio, D-14) */
function prResp(o) { return (o && o.resp && o.resp !== '—') ? o.resp : prQuem('colh'); }
/* dia da colheita confirmado pela O.S.: apontamento somado (enviado, Provisório ou Conferido) na mesma data */
function prApDia(o, dcol) { return !!dcol && (o.ap || []).some(a => a.d === prDdMm(dcol) && cenApSomado(a)); }
/* lote de campo (R-06): O.S. + dia do apontamento da mesma data (o mesmo id do motor de carência, carLid); sem apontamento, vazio */
function prLc(c, osId, dcol) { const o = (c.ordens || {})[osId]; if (!o || !dcol) return '';
  const a = (o.ap || []).find(x => x.d === prDdMm(dcol) && x.st !== 'Previsto' && x.st !== CEN_AP_DESC && x.st !== CEN_AP_DUP); if (!a) return '';
  if (typeof carLid === 'function') return carLid(osId, a.dia); const m = /^OS-(\d+)$/.exec(osId); return 'LC-' + (m ? m[1] : osId.replace(/[^A-Za-z0-9]/g, '')) + '-' + a.dia; }
/* semana do passe: "Colheita · semana 39" no tipo; senão a janela da ordem nova; senão o 1º apontamento */
function prSemDaOS(o) { const jn = o.osc && o.osc.novo && o.osc.novo.jan; if (/^\d{4}-\d\d-\d\d$/.test(String(jn || ''))) return prSem(jn);   /* ordem nova guarda a janela ISO (com ano) */
  const m = /semana (\d+)/.exec(String(o.tipo || '')); if (m) return prSemAno(Number(m[1]));
  const j = /(\d\d)\/(\d\d)/.exec(String((o.osc && o.osc.novo && o.osc.novo.janela) || o.janela || '')); if (j) return prSem(prIsoDe(j[1] + '/' + j[2]));
  const a = (o.ap || []).find(x => x.st !== 'Previsto'); return a ? prSem(prIsoDe(a.d)) : prSem(prHoje()); }

/* ---------- cargas, produção e área colhida (R-02 a R-04) ---------- */
function prCargas(c, f) { return Object.values(prP(c).cargas).filter(g => !f || f(g)); }
function prCargasOS(c, osId) { return prCargas(c, g => (g.origem || []).some(x => x.os === osId)); }
/* pendentes da O.S.: carga a pesar (com ou sem sinal) */
function prAPesar(c, osId) { return prCargas(c, g => g.st === 'A pesar' && (g.origem || []).some(x => x.os === osId)); }
/* produção na base física da cultura (R-04): grão = comercial corrigido; fruta e cana = massa líquida; coco e abacaxi = frutos.
   Café (base beneficiado, R-09): a origem da carga guarda os litros; a produção é o café beneficiado medido e rateado a ela pelo
   beneficiamento (x.ben, kg; BEN-4 · R-D02). Sem x.ben a origem está "a apurar" (estado próprio, COLH-C01): não entra como zero na
   produção, na produtividade nem no desvio; x.ben = 0 é zero medido (real). Função única do estado de apuração: prApurado. */
function prApurado(x, cultura) { return prUn(cultura).base !== 'beneficiado' || (x.ben !== undefined && x.ben !== null && x.ben !== '' && isFinite(Number(x.ben))); }
function prProdOrig(x, cultura) { const u = prUn(cultura); if (u.base === 'beneficiado') return prApurado(x, cultura) ? Number(x.ben) : 0; return u.base === 'comercial' ? (x.com || 0) : (x.kg || 0); }
/* UNID-PROD: litros = todos os L de café da roça (medidos ou a apurar); kgOk = toda origem com peso líquido > 0 (o kg do fruto vale);
   estim = alguma origem com participação estimada (COLH R-06). cafe (só os L a apurar) e liq não mudam */
function prProdOS(c, osId) { const out = { kg: 0, liq: 0, com: 0, cafe: 0, apurar: false, litros: 0, kgOk: false, estim: false, n: 0 }; let semPeso = false;
  prCargas(c, g => g.st === 'Recebida').forEach(g => (g.origem || []).filter(x => x.os === osId).forEach(x => {
    out.n++; out.litros = prSoma([out.litros, x.litros || 0]); if (!(Number(x.kg) > 0)) semPeso = true; if (x.modo === 'estimada') out.estim = true;
    out.liq = prSoma([out.liq, x.kg || 0]); out.com = prSoma([out.com, x.com || 0]);
    if (prApurado(x, g.cultura)) out.kg = prSoma([out.kg, prProdOrig(x, g.cultura)]);
    else { out.apurar = true; out.cafe = prSoma([out.cafe, x.litros || 0]); } }));
  out.kgOk = out.n > 0 && !semPeso; return out; }
function prAreaOS(o) { return prSoma((o.ap || []).filter(a => cenApSomado(a)).map(a => a.ha)); }
/* versão publicada que vale como referência do passe: a última publicada ANTES do início da semana (R-05, R-17) */
function prVersaoRef(c, cid, sem) { const ini = prSemIni(sem); const vs = (prP(c).previsoes[cid] || []).filter(v => v.d < ini && v.sem && v.sem[sem] !== undefined); return vs[vs.length - 1] || null; }
/* versão vigente de uma semana para oferta (a última publicada que traz a semana) */
function prVersaoSem(c, cid, sem) { const vs = (prP(c).previsoes[cid] || []).filter(v => v.sem && v.sem[sem] !== undefined); return vs[vs.length - 1] || null; }
function prPasse(c, o) { const cid = prCultDaOS(c, o); const k = PRDC.cult[cid] || {}; const sem = prSemDaOS(o); const p = prProdOS(c, o.id);
  const area = prAreaOS(o); const ap = prAPesar(c, o.id); const final = o.etapa === 'Encerradas' && !ap.length;
  const ref = prVersaoRef(c, cid, sem); const refKg = ref ? ref.sem[sem] : null;
  const desv = (final && refKg && !p.apurar) ? prDiv(prMul(prSub(p.kg, refKg), 100), refKg) : null;
  return { os: o.id, o, cid, cultura: k.cultura, sem, fase: o.etapa, area, kg: p.kg, liq: p.liq, com: p.com, cafe: p.cafe, apurar: p.apurar, aPesar: ap, final, ref, refKg, desv,
           litros: p.litros, kgOk: p.kgOk, estim: p.estim, n: p.n,
           prtv: p.apurar ? null : prPrtv(k.cultura || 'Mamão Formosa', p.kg, area) }; }
/* resultado do cultivo: passes (perene semanal), ciclo (área do cultivo, R-02 e D-11) ou safra (anual: mín(área, Σ ha)) */
function prResultado(c, cid) { const k = PRDC.cult[cid]; if (!k) return null; const u = prUn(k.cultura); const oss = prOsCult(c, cid);
  const passes = oss.map(o => prPasse(c, o)).sort((a, b) => a.sem < b.sem ? -1 : (a.sem > b.sem ? 1 : 0));
  const kg = prSoma(passes.map(p => p.kg)); const haSom = prSoma(passes.map(p => p.area)); const aPesar = [].concat(...passes.map(p => p.aPesar));
  const apurar = passes.some(p => p.apurar); const cafe = prSoma(passes.map(p => p.cafe || 0));   /* café: litros ainda sem rendimento medido */
  const comecou = apurar || passes.some(p => prCmp(p.area, 0) > 0 || prCmp(p.kg, 0) > 0);
  /* UNID-PROD (R-U05): todos os L e o peso líquido do fruto; o kg do fruto só vale com peso em todas as origens */
  const litros = prSoma(passes.map(p => p.litros || 0)), liq = prSoma(passes.map(p => p.liq || 0)); const comOrig = passes.filter(p => p.n > 0);
  const kgOk = comOrig.length > 0 && comOrig.every(p => p.kgOk), estim = passes.some(p => p.estim);
  /* desvio contra a meta na base por ha, os dois pelo conversor e com a unidade gravada na meta (R-U09) */
  let area, parcial, ref = null, desv = null;
  if (k.semanal) { area = comecou ? k.area : 0; const fim = (PRDC.safras[k.saf] || {}).fim || ''; parcial = !(fim && prHoje() > fim);
    if (!parcial && k.meta && !apurar) { ref = k.meta; desv = prUnpDesv(k.cultura, kg, area, k.meta, k.un_meta); } }
  else { area = prCmp(haSom, k.area) > 0 ? k.area : haSom; parcial = !oss.length || oss.some(o => o.etapa !== 'Encerradas') || aPesar.length > 0;
    ref = k.meta || null; if (ref && area > 0 && !apurar) desv = prUnpDesv(k.cultura, kg, area, ref, k.un_meta); }
  return { cid, k, u, passes, kg, area, parcial, ref, desv, aPesar, cafe, apurar, prtv: (area > 0 && !apurar) ? prPrtv(k.cultura, kg, area) : null, comecou, litros, liq, kgOk, estim }; }
/* textos do resultado (linha, grupo, painel, passe, cartão e recebimento): com parte a apurar nunca "0 sc", "0,00 sc/ha" nem desvio (COLH-C01).
   X = resultado do talhão (prResultado) ou passe (prPasse): kg medido, cafe (L a apurar), apurar, area, comecou */
function prProdTxt(cultura, X) { if (X.apurar) return (prCmp(X.kg, 0) > 0 ? prUnTxt(cultura, X.kg) + ' + ' : '') + prFmtT(X.cafe, 0) + ' L · ' + prUn(cultura).un + ' a apurar';
  return (X.comecou === undefined || X.comecou) ? prUnTxt(cultura, X.kg) : '—'; }
/* carga de café: os litros e, medido o rendimento de todas as origens, as sacas medidas; senão "sc a apurar" */
function prCargaCafeTxt(g) { const os = g.origem || []; const ok = os.length > 0 && os.every(x => prApurado(x, g.cultura));
  return prFmtT(g.litros, 0) + ' L · ' + (ok ? prUnTxt(g.cultura, prSoma(os.map(x => Number(x.ben)))) : prUn(g.cultura).un + ' a apurar'); }
function prPrtvResTxt(cultura, X, op) { if (op !== undefined) return prUnpTxt(prUnpInd(cultura, X, op));
  if (X.apurar) return prUn(cultura).prtv + ' a apurar'; return (X.prtv !== null && X.prtv !== undefined && X.area > 0) ? prPrtvTxt(cultura, X.kg, X.area) : '—'; }
/* cultura (ou fazenda): Σ produção ÷ Σ área, ponderada; nunca média de médias (R-04, K07). Talhão a apurar fica fora da conta
   (a área sem produção medida não entra como zero, COLH-C01); apurar conta os que ficaram fora.
   UNID-PROD R-U08: só soma o mesmo produto do mesmo estágio (chave = u.prod no estágio-base, u.proc no campo, r.estagio === 'campo');
   produtos ou estágios diferentes (café da roça × beneficiado, algodão em caroço × pluma) lançam erro, nunca somam */
function prAgrChave(r) { const u = prUn(r.k.cultura); return r.estagio === 'campo' ? (u.proc || u.prod) : u.prod; }
function prPonderada(rs) { const v = rs.filter(r => r && r.area > 0 && !r.apurar); const fora = rs.filter(r => r && r.apurar).length; if (!v.length) return null; const cultura = v[0].k.cultura;
  const k0 = prAgrChave(v[0]); const dif = v.find(r => prAgrChave(r) !== k0); if (dif) throw new Error('Produtos ou estágios diferentes não se agregam: ' + k0 + ' × ' + prAgrChave(dif) + '.');
  const kg = prSoma(v.map(r => r.kg)), ha = prSoma(v.map(r => r.area));
  return { kg, area: ha, prtv: prPrtv(cultura, kg, ha), parcial: v.some(r => r.parcial) || fora > 0, apurar: fora, cultura, estim: v.some(r => r.estim) }; }

/* ---------- unidade de produtividade selecionável (UNID-PROD · docs/unidades-produtividade/ESPECIFICACAO.md v1.1, D-U01..D-U21) ----------
   Conversor único (ENG-011, R-U01): toda tela que mostra produtividade ou meta em outra unidade passa por aqui; nenhuma multiplica por conta própria.
   A base do indicador em massa é kg/ha (6 casas); o número na unidade escolhida sai de produção ÷ (área × massa da unidade), um arredondamento (R-U02).
   Massa só converte massa (R-U05): L do café da roça e frutos (coco, abacaxi) nunca viram kg; o kg do fruto só vale com peso líquido em todas as origens.
   A escolha é exibição: nada aqui lê ou grava o cenário nem a preferência (a preferência fica na tela, g2unidPref no bloco <perfis>). */
const PR_UNP_FIX = [{ k: 'kg', un: 'kg/ha', rot: 'kg/ha', massa: '1' }, { k: 't', un: 't/ha', rot: 't/ha', massa: '1000' },
  { k: 'sc60', un: 'sc60 eq./ha', rot: 'sc 60 kg/ha (equivalência)', massa: '60', eq: true }];
const PR_UNP_SEMPESO = 'Falta peso ou conversão medida';
function prUnpPesa(u) { return u.base !== 'frutos'; }   /* estágio-base pesado na balança (grão, café beneficiado, fruta, cana) */
function prUnpAlt(cultura) { return (PRDC.unAlt || {})[prCult(cultura)] || []; }   /* massa declarada do produto (caixa do packing, D-U08) */
function prUnpPadrao(cultura, estagio) { const u = prUn(cultura);
  if (estagio === 'campo') return { k: 'padrao', un: u.campo + '/ha', rot: 'Padrão do estágio · ' + u.campo + '/ha', massa: null, div: '1', ok: true, motivo: '', L: true };
  const m = prUnpPesa(u); const kg = (m && u.un !== 't' && u.un !== 'kg') ? ' (' + prFmtT(u.massa, 3) + ' kg)' : '';
  return { k: 'padrao', un: u.prtv, rot: 'Padrão da cultura · ' + u.prtv + kg, massa: m ? u.massa : null, div: u.massa, ok: true, motivo: '', lado: u.lado || '' }; }
/* opções do estágio ('base' ou 'campo'): Padrão, kg/ha, t/ha, sc 60 kg/ha (equivalência) e as de massa declarada; sai a opção igual ao Padrão em
   todos os estágios (D-U03). X (opcional) é o resultado lido: no campo do café, sem peso em todas as origens as de massa ficam indisponíveis */
function prUnpOpcoes(cultura, estagio, X) { const u = prUn(cultura); const est = (estagio === 'campo' && u.campo) ? 'campo' : 'base';
  const P = prUnpPadrao(cultura, est); const pesa = est === 'campo' ? !(X && X.kgOk === false) : prUnpPesa(u);
  const igual = (o) => !u.campo && prUnpPesa(u) && prCmp(o.massa, u.massa) === 0;
  return [P].concat(PR_UNP_FIX.concat(prUnpAlt(cultura)).filter(o => !igual(o))
    .map(o => ({ k: o.k, un: o.un, rot: o.rot, massa: o.massa, div: o.massa, eq: !!o.eq, ok: pesa, motivo: pesa ? '' : PR_UNP_SEMPESO }))); }
/* unidade em texto (meta gravada ou opção) → massa da unidade em kg e o período; null se não é massa. Reconhece o un das opções e o texto do Padrão */
function prUnpMassa(cultura, unTxt) { const u = prUn(cultura); const t = String(unTxt || '').trim(); const per = /\/ano$/.test(t) ? '/ano' : ''; const s = per ? t.slice(0, -4) : t;
  if (!s || s === u.prtv) return prUnpPesa(u) ? { massa: u.massa, per, k: 'padrao' } : null;
  const o = PR_UNP_FIX.concat(prUnpAlt(cultura)).find(x => x.un === s); return (o && prUnpPesa(u)) ? { massa: o.massa, per, k: o.k } : null; }
/* valor por ha na unidade informada → base física por ha (kg; frutos no coco), multiplicação exata; unidade desconhecida é recusada */
function prUnpQHa(cultura, valor, unTxt) { const u = prUn(cultura); const s = String(unTxt || '').trim().replace(/\/ano$/, '');
  if (!s || s === u.prtv) return prMul(valor, u.massa); const m = prUnpMassa(cultura, unTxt);
  if (!m) throw new Error('Unidade sem massa para ' + cultura + ': ' + unTxt + '.'); return prMul(valor, m.massa); }
function prUnpKgHa(cultura, valor, unTxt) { if (!prUnpPesa(prUn(cultura))) throw new Error('Unidade sem massa para ' + cultura + ': ' + unTxt + '.'); return prUnpQHa(cultura, valor, unTxt); }
/* q ÷ (área × div), um arredondamento (prM em milionésimos: q·10^12 ÷ (área·div·10^12)) */
function prUnpDiv(q, area, div) { return prN(prRd(prM(q) * PR_S * PR_S, prM(area) * prM(div))); }
/* o mesmo quociente direto em d casas, para a tela: um arredondamento só (R-U02, PRD 10.0). O de 6 casas fica para kgHa e a chave r.ordk;
   arredondar o de 6 casas de novo para 2 dava 8,0849995 → 8,085 → "8,09" (revisão v57, S4) */
function prUnpDivD(q, area, div, d) { const e = 10n ** BigInt(d); return prN(prRd(prM(q) * PR_S * e, prM(area) * prM(div)) * (PR_S / e)); }
/* desvio % contra a meta na base por ha: (q ÷ área − meta) ÷ meta × 100, um arredondamento; meta com a unidade gravada (R-U09) */
function prUnpDesv(cultura, q, area, meta, unMeta) { const Q = prM(prUnpQHa(cultura, meta, unMeta)), A = prM(area); const den = Q * A; if (den === 0n) return null;
  return prN(prRd((prM(q) * PR_S - den) * 100n * PR_S, den)); }
/* indicador (R-U07): X de prResultado, prPasse ou prPonderada; k = chave da opção escolhida. st: medido | apurar | pend | vazio.
   kgHa = base por ha com 6 casas (a chave de ordenação e de filtro, igual em qualquer unidade); num = o número na unidade escolhida */
function prUnpInd(cultura, X, k) { const u = prUn(cultura); const ops = prUnpOpcoes(cultura, 'base'); const ped = ops.find(o => o.k === k);
  const o = (ped && ped.ok) ? ped : ops[0]; const temArea = prCmp(X.area || 0, 0) > 0;
  const ind = { st: '', kgHa: null, num: null, un: o.un, prod: '', estagio: 'base', estim: !!X.estim, op: o.k, campo: null, lado: '',
                motivo: (ped && !ped.ok) ? ped.rot + ' indisponível para ' + u.prod + ': ' + ped.motivo.toLowerCase() : '' };
  if (X.apurar === true) { ind.st = 'apurar';   /* café beneficiado sem rendimento medido: nunca "0"; ao lado, o indicador medido do fruto (D-U11).
    Na ponderada, apurar é a contagem dos talhões fora da conta (não o estado): ela é sempre medida */
    if (u.campo && prCmp(X.litros || 0, 0) > 0) {
      if (!temArea) ind.campo = { st: 'pend' };
      else { const oc = prUnpOpcoes(cultura, 'campo', X); const pc = oc.find(x => x.k === o.k); const c = (pc && pc.ok) ? pc : oc[0];
        if (pc && !pc.ok) ind.motivo = pc.rot + ' indisponível para ' + u.proc + ': ' + pc.motivo.toLowerCase();
        ind.campo = { st: 'medido', estagio: 'campo', prod: u.proc, un: c.un, L: !!c.L, kgHa: c.massa ? prUnpDiv(X.liq, X.area, 1) : null, lHa: prUnpDiv(X.litros, X.area, 1),
                      num: prUnpDiv(c.massa ? X.liq : X.litros, X.area, c.div), n2: prUnpDivD(c.massa ? X.liq : X.litros, X.area, c.div, 2) }; } }
    return ind; }
  if (!temArea) { ind.st = prCmp(X.kg || 0, 0) > 0 ? 'pend' : 'vazio'; return ind; }
  ind.st = 'medido'; ind.kgHa = prUnpDiv(X.kg, X.area, 1); ind.num = prUnpDiv(X.kg, X.area, o.div); ind.n2 = prUnpDivD(X.kg, X.area, o.div, 2);
  if (o.eq) ind.prod = u.prod; if (o.k === 'padrao' && u.lado) ind.lado = prFmt(prUnpDivD(X.kg, X.area, 1000, 2), 2) + ' ' + u.lado;
  return ind; }
/* número da tela com 2 casas (n2: um arredondamento só, R-U02) */
function prUnpNum(x) { const n = x.n2 !== undefined ? x.n2 : x.num; return (x.L ? prFmtT(n, 2) : prFmt(n, 2)) + ' ' + x.un; }
/* texto da célula (R-U03): "‹número› ‹un›" [· lado] [de ‹produto› quando é equivalência ou outro estágio] [· estimativa] */
function prUnpTxt(ind) { if (!ind || ind.st === 'vazio') return '—'; if (ind.st === 'pend') return 'sem área colhida apontada'; const est = ind.estim ? ' · estimativa' : '';
  if (ind.st === 'apurar') { const c = ind.campo; return ind.un + ' a apurar' + (c ? ' · ' + (c.st === 'pend' ? 'sem área colhida apontada' : prUnpNum(c) + ' de ' + c.prod) : '') + est; }
  return prUnpNum(ind) + (ind.lado ? ' · ' + ind.lado : '') + (ind.prod ? ' de ' + ind.prod : '') + est; }
/* meta (valor e unidade gravados) na unidade escolhida: a mesma unidade mostra o valor gravado; outra converte uma vez; até 2 casas (R-U02).
   Unidade gravada sem conversão: mostra como foi gravada (ok: false) */
function prUnpMeta(cultura, valor, unTxt, k) { const ops = prUnpOpcoes(cultura, 'base'); const o = ops.find(x => x.k === k && x.ok) || ops[0];
  const per = /\/ano$/.test(String(unTxt || '').trim()) ? '/ano' : ''; let q;
  try { q = prUnpQHa(cultura, valor, unTxt); } catch (e) { return { txt: prFmtT(valor, 2) + ' ' + (unTxt || ''), kgHa: null, ok: false, un: unTxt || '' }; }
  const m = prUnpMassa(cultura, unTxt); const mesma = m ? m.k === o.k : o.k === 'padrao';
  const num = mesma ? prN(prM(valor)) : prUnpDiv(q, 1, o.div); const n2 = mesma ? num : prUnpDivD(q, 1, o.div, 2);   /* n2: o texto com um arredondamento só (R-U02) */
  return { txt: prFmtT(n2, 2) + ' ' + o.un + per, num, n2, kgHa: q, ok: true, un: o.un + per }; }

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
    if (!k.meta) return null; const S = prSem(prHoje()); const kg = prMulDiv(k.area, prUnpQHa(k.cultura, k.meta, k.un_meta), 52); const sem = {};   /* meta pelo conversor (RC-09) */
    [1, 2, 3].forEach(i => { sem[prSemMais(S, i)] = kg; }); return { base: 'meta', sem, par: P }; }
  if (!k.meta) return null; return { base: 'meta', safra: prMul(k.area, prUnpQHa(k.cultura, k.meta, k.un_meta)) }; }
function prSemComecou(sem) { return prSemIni(sem) <= prHoje(); }
/* semanas publicáveis do rascunho: só as que ainda não começaram e mudam o que está publicado */
function prPublicavel(c, cid, par) { const r = prRascunho(c, cid, par); if (!r) return null; const vs = prP(c).previsoes[cid] || []; const ult = vs[vs.length - 1] || null;
  if (r.safra !== undefined) { const ini = (PRDC.cult[cid].colheita || ''); if (ult && ult.safra !== undefined && prCmp(ult.safra, r.safra) === 0) return null; if (ini && ini <= prHoje()) return null; return { safra: r.safra, base: r.base }; }
  const sem = {}; Object.keys(r.sem).filter(s => !prSemComecou(s)).forEach(s => { const v = prVersaoSem(c, cid, s); if (!v || prCmp(v.sem[s], r.sem[s]) !== 0) sem[s] = r.sem[s]; });
  return Object.keys(sem).length ? { sem, base: r.base, par: r.par, cnt: r.cnt ? r.cnt.id : '' } : null; }

/* ---------- lotes: qualidade efetiva e saldos (R-10, R-12, R-14) ---------- */
function prFis(c, lid) { return prSoma(prP(c).movs.filter(m => m.lote === lid && m.fis !== false).map(m => m.kg)); }
function prResLote(c, lid) { return prSoma(Object.values(prP(c).reservas).filter(r => r.lote === lid && r.st === 'Ativa').map(r => r.kg)); }
/* origens de campo do lote (carga → O.S. e dia da colheita); o lote do beneficiamento herda as das entradas pela genealogia (BEN-1, R-E07) */
function prOrigCampo(c, L, vis) { const P = prP(c); vis = vis || {}; if (!L || vis[L.id]) return []; vis[L.id] = 1; const out = [];
  (L.origem || []).forEach(x => { if (x.est) return; if (x.lote) out.push.apply(out, prOrigCampo(c, P.lotes[x.lote], vis)); else if (x.os) out.push(x); }); return out; }
/* lotes de campo de origem (vivos: o LC- entra quando o apontamento da data existe) */
function prLcs(c, L) { const out = []; prOrigCampo(c, L).forEach(x => { const lc = prLc(c, x.os, x.dcol); if (lc && out.indexOf(lc) < 0) out.push(lc); }); return out; }
/* pós-colheita registrado no motor de carência (CAR0) sobre o lote de campo, na data do recebimento ou depois: fruta fora do vendável (D-23) */
function prOpPos(c, L) { if (typeof carOps !== 'function' || typeof CARD === 'undefined') return null; const lcs = prLcs(c, L);
  for (const op of carOps(c)) { const d = op.d || ''; if (d < (L.drec || '')) continue;
    if (op.k === 'pos' && lcs.indexOf(op.lote) >= 0) return { t: op.p + ' em ' + prBr(d) + ' (' + op.lote + ')', op };
    if ((op.k === 'mistura' || op.k === 'divisao') && (op.de || []).some(x => lcs.indexOf(x) >= 0)) {
      const de = (op.de || []).filter(x => lcs.indexOf(x) >= 0).join(', '); const nv = (op.novos || []).map(n => n.id).join(', ');
      return { t: (op.k === 'mistura' ? 'Misturado no ' + nv : 'Dividido em ' + nv) + ' em ' + prBr(d) + ' (' + de + ')', op }; } }
  return null; }
/* opt.base (BEN-1, R-A03): a qualidade que vale fora do processo, para conferir a entrada de uma ordem de beneficiamento: sem a regra
   do local de processo, do pós-colheita do CAR0 e da ordem que já reservou o lote */
function prQualidade(c, L, opt) { const base = !!(opt && opt.base);
  const loc = PRDC.locais[L.local] || {}; const u = prUn(L.cultura);
  if (u.campo && !L.benef) return { q: 'Em processo', mot: 'Café da roça em L: a saca sai do rendimento medido no beneficiamento (sc a apurar)', dono: 'Beneficiamento' };
  if (!base) { const ob = L.ordem && (c.ordens || {})[L.ordem];   /* entrada liberada para uma ordem de beneficiamento: em processo nela até o Fechar */
    if (ob && ['Encerradas', 'Canceladas'].indexOf(ob.etapa) < 0) return { q: 'Em processo', mot: 'Em processo na ' + L.ordem + ' (beneficiamento, ' + ob.etapa + ')', dono: (typeof BENC !== 'undefined' && BENC.quem.prod) || 'Beneficiamento', ordem: L.ordem };
    if (!L.benef) { if ((PRDC.proc || []).indexOf(loc.tipo) >= 0) return { q: 'Em processo', mot: 'Recebido no ' + loc.nome + ' (' + loc.tipo + '): beneficiamento antes de vender', dono: 'Beneficiamento' };
      const op = prOpPos(c, L); if (op) return { q: 'Em processo', mot: op.t + ': fora do vendável até a ordem de processo', dono: 'Beneficiamento' }; } }
  let pior = null;
  if (typeof CARD !== 'undefined' && typeof carEstado === 'function') {
    prOrigCampo(c, L).forEach(x => { const o = (c.ordens || {})[x.os];
      if (!o || PR_FEZ.indexOf(o.etapa) < 0) { if (!pior) pior = { q: 'Em inspeção', mot: 'Colheita sem ordem liberada (' + x.os + (o ? ' em ' + o.etapa : ' sem registro') + ')', dono: CARD.quem.ag }; return; }
      carTals(o.talhao).forEach(t => { const e = carEstado(c, t.tid, x.dcol, t.parc, x.dcol);
        if (e.k === 'curso') { const r = e.ativos[0]; pior = { q: 'Bloqueado', mot: 'Colhido em ' + prBr(x.dcol) + ' dentro da carência de ' + r.p + ' (' + r.os + ', aplicado em ' + carBr(r.d) + ', carência até ' + carAte(r.fim) + ')', dono: CARD.quem.ag, fim: r.fim }; }
        else if (e.k === 'insuf' && !(pior && pior.q === 'Bloqueado')) { const p = e.pend[0]; pior = { q: 'Em inspeção', mot: 'Carência sem dados suficientes: ' + p.t, dono: p.q || CARD.quem.ag }; } });
      /* R-12 (revisão A-01): a carência é lida no dia da colheita; dia sem apontamento somado na O.S. não é fato confirmado (data digitada ou padrão errada) */
      if (!pior && !prApDia(o, x.dcol)) pior = { q: 'Em inspeção', mot: 'Colhido em ' + prBr(x.dcol) + ' sem apontamento de área da ' + x.os + ' nesse dia: confirme o dia da colheita ou aponte a área do dia', dono: prResp(o) }; }); }
  if (pior) return pior;
  /* decisões da Qualidade sobre o lote de produção (BEN-1, R-E03): destinado e bloqueado com motivo */
  if (L.q0 === 'Destinado') return { q: 'Destinado', mot: 'Destinado' + (L.dest ? ' por ' + L.dest.quem + ' em ' + prBr(L.dest.d) + ': ' + L.dest.motivo : ''), dono: '' };
  if (L.q0 === 'Bloqueado') return { q: 'Bloqueado', mot: (L.bloq && L.bloq.motivo) || 'Bloqueado pela Qualidade', dono: prQuem('qual'), fim: L.bloq && L.bloq.prazo };
  if (L.q0 === 'Liberado') return { q: 'Liberado', mot: L.lib ? 'Liberado por ' + L.lib.quem + ' em ' + prBr(L.lib.d) : 'Íntegro no recebimento', dono: '' };
  if (L.insp) return { q: 'Em inspeção', mot: 'Inspeção ' + L.insp + ': fechar o processo não libera; a Qualidade registra o resultado e decide', dono: prQuem('qual') };
  return { q: 'Em inspeção', mot: 'Recebido ' + String(L.cond || '').toLowerCase() + ': a Qualidade confere e libera', dono: prQuem('qual') }; }
function prSaldos(c, L) { const Q = prQualidade(c, L); const fis = prFis(c, L.id); const res = prResLote(c, L.id); const z = { fis, res, q: Q.q, mot: Q.mot, dono: Q.dono, fim: Q.fim, blq: 0, apto: 0, proc: 0, disp: 0 };
  if (Q.q === 'Em processo') z.proc = fis; else if (Q.q === 'Liberado') { z.apto = fis; z.disp = prCmp(fis, res) > 0 ? prSub(fis, res) : 0; } else z.blq = fis;
  z.esgotado = prCmp(fis, 0) <= 0; z.vencido = !!(L.validade && L.validade < prHoje()); z.ordem = Q.ordem || ''; return z; }

/* ---------- pedidos, reservas e oferta (R-15, R-16) ---------- */
/* expedido da venda, líquido de devolução (Comercial R-C10): a devolução entra como lote novo com +kg e o mesmo pedido */
function prExpedido(c, pid) { return prSoma(prP(c).movs.filter(m => (m.tipo === 'expedição' || m.tipo === 'devolução') && m.pedido === pid).map(m => -m.kg)); }
/* fator do compromisso (Comercial A-17; DEC-0510-03 dimensional): a venda guarda a quantidade na unidade do contrato (qc), a massa dessa
   unidade (fat, kg) e a origem; legado com a massa ambígua (sc 50 × 60 kg, fatAmb) fica sem kg (qtd null) até a conversão registrada
   (fatConf): falta, saldo, oferta e saída que dependem dela ficam suspensos; nada é convertido em silêncio pela unidade atual da cultura */
function prAmb(p) { return !!(p && p.fatAmb && !p.fatConf && !p.enc); }   /* encerrada: a quantidade vigente é o expedido em kg, nada a conferir */
/* texto na unidade do compromisso (fonte única; o Comercial usa as mesmas): massa gravada na venda, nunca a do cadastro atual; com a massa
   igual à da cultura, o rótulo é o de sempre ("616 sc"); diferente, vai junto ("12.000 sc 50 kg"); sem massa conhecida, só kg */
function prFatV(p) { return p.fatConf ? p.fatConf.fat : (p.fat || null); }
function prUnV(p) { const u = prUn(p.cultura); const un = p.un || prEstUn(p.cultura); const f = prFatV(p);
  return (u.est || !f || prCmp(f, u.massa) === 0) ? un : un + ' ' + prFmtT(f, 3) + ' kg'; }
function prTxtV(p, kg, d) { const f = prFatV(p); if (!f) return prFmtT(kg, 3) + ' kg'; return prFmtT(prDiv(kg, f), d === undefined ? 2 : d) + ' ' + prUnV(p); }
/* pedido sem massa gravada (pedido de teste da Colheita): a unidade de estoque da cultura; com massa: a do compromisso (Comercial A7 da revisão) */
function prTxtP(p, kg) { return prFatV(p) ? prTxtV(p, kg) : prEstTxt(p.cultura, kg); }
function prUnP(p) { return prFatV(p) ? prUnV(p) : prEstUn(p.cultura); }
function prQP(p, kg) { const f = prFatV(p); return f ? prDiv(kg, f) : prEstQ(p.cultura, kg); }
function prBaseP(p, q) { const f = prFatV(p); return f ? prMul(q, f) : prEstBase(p.cultura, q); }
function prQtdTxt(p) { return prAmb(p) ? prFmtT(p.qc, 3) + ' ' + (p.un || '') + ' (saca de ' + p.fatAmb.join(' ou ') + ' kg a conferir)' : ((prFatV(p) || p.fatAmb) ? prTxtV(p, p.qtd || 0) : prEstTxt(p.cultura, p.qtd)); }
function prResPed(c, pid) { return Object.values(prP(c).reservas).filter(r => r.pedido === pid && r.st === 'Ativa'); }
function prFalta(c, ped) { if (prAmb(ped)) return 0; const f = prSub(prSub(ped.qtd, prExpedido(c, ped.id)), prSoma(prResPed(c, ped.id).map(r => r.kg))); return prCmp(f, 0) > 0 ? f : 0; }
/* produto classificado (BEN-1, R-E05): a classe é obrigatória nos dois e igual; vazio igual a vazio nunca passa. Os demais seguem a regra da colheita */
function prClassificado(prod) { return typeof BENC !== 'undefined' && Object.values(BENC.rotas).some(r => (r.saidas || []).some(s => s.fluxo === 'Produto' && s.prod === prod && (s.classes || []).length)); }
function prCompatErro(ped, L) { if (!ped || !L) return 'Pedido ou lote não encontrado.';
  if (ped.prod !== L.prod) return L.id + ' (' + L.prod + (L.classe ? ' · ' + L.classe : '') + (L.saf ? ' ' + L.saf : '') + ') não atende o ' + ped.id + ' (' + ped.prod + (ped.classe ? ' · ' + ped.classe : '') + (ped.saf ? ' ' + ped.saf : '') + ').';
  if (prClassificado(L.prod)) { if (!ped.classe || !L.classe) return 'Classe não informada (' + (!L.classe ? L.id : ped.id) + ').';
    if (ped.classe !== L.classe) return 'Classe ' + L.classe + ' ≠ ' + ped.classe + ' do ' + ped.id + '.'; }
  else if (ped.classe && L.classe && ped.classe !== L.classe) return L.id + ' (' + L.prod + ' · ' + L.classe + ') não atende o ' + ped.id + ' (' + ped.prod + ' · ' + ped.classe + ').';
  if (ped.saf && L.saf && ped.saf !== L.saf) return L.id + ' (' + L.prod + ' ' + L.saf + ') não atende o ' + ped.id + ' (' + ped.prod + ' ' + ped.saf + ').';
  return ''; }
function prCompat(ped, L) { return !prCompatErro(ped, L); }
/* situação do pedido: Encerrada · Entregue · Coberto · Parcial · Sem reserva · Em risco (reserva com expedição impedida) · Futura: compromete a previsão */
function prSitPed(c, ped) { const rs = prResPed(c, ped.id); const exp = prExpedido(c, ped.id); const falta = prFalta(c, ped);
  const imp = rs.filter(r => { const L = prP(c).lotes[r.lote]; return !L || prSaldos(c, L).q !== 'Liberado' || !prCompat(ped, L); });   /* bloqueado ou reclassificado depois da reserva (R-E06) */
  if (ped.enc) return { t: 'Encerrada', c: 'gray', imp };   /* saldo encerrado com motivo (Comercial R-C11) */
  if (prAmb(ped)) return { t: 'Saca a conferir', c: 'red', imp };   /* Comercial A-17: sem a massa do contrato, nada se compara */
  if (prCmp(exp, ped.qtd) >= 0) return { t: 'Entregue', c: 'gray', imp };
  if (imp.length) return { t: 'Em risco', c: 'red', imp };
  if (prCmp(falta, 0) <= 0) return { t: 'Coberto', c: 'green', imp };
  if (ped.tipo === 'futura') return { t: rs.length ? 'Futura: parcial' : 'Futura: compromete a previsão', c: 'yellow', imp };
  return { t: rs.length ? 'Parcial' : 'Sem reserva', c: rs.length ? 'yellow' : 'yellow', imp }; }
/* oferta publicada × vendas futuras (R-16): por semana (fruta) ou por safra (grão); o físico nunca entra aqui */
/* saldo da venda futura = máx(0, quantidade − expedido): excesso pesado na saída não vira oferta (Comercial CE-03, D-C23) */
function prSaldoFut(c, p) { if (prAmb(p)) return 0; const s = prSub(p.qtd, prExpedido(c, p.id)); return prCmp(s, 0) > 0 ? s : 0; }
function prOfertaSem(c, prod, sem) { let pub = 0, tem = false; Object.keys(PRDC.cult).forEach(cid => { const k = PRDC.cult[cid]; if (prUn(k.cultura).prod !== prod) return;
    const v = prVersaoSem(c, cid, sem); if (v) { pub = prSoma([pub, v.sem[sem]]); tem = true; } });
  const fut = Object.values(prP(c).pedidos).filter(p => p.tipo === 'futura' && p.prod === prod && p.sem === sem);
  const futKg = prSoma(fut.map(p => prSaldoFut(c, p))); const resKg = prSoma([].concat(...fut.map(p => prResPed(c, p.id))).map(r => r.kg));
  const amb = fut.filter(prAmb).map(p => p.id);   /* Comercial A-17: oferta suspensa (livre null) enquanto um compromisso não tem a massa */
  return { pub, tem, fut, futKg, resKg, amb, livre: amb.length ? null : prSub(pub, prSub(futKg, resKg)) }; }
function prOfertaSafra(c, prod, saf) { let pub = 0, tem = false; Object.keys(PRDC.cult).forEach(cid => { const k = PRDC.cult[cid]; if (prUn(k.cultura).prod !== prod || (PRDC.safras[k.saf] || {}).mf !== saf) return;
    const vs = (prP(c).previsoes[cid] || []).filter(v => v.safra !== undefined); const v = vs[vs.length - 1]; if (v) { pub = prSoma([pub, v.safra]); tem = true; } });
  const cultura = (Object.values(PRDC.cult).find(k => prUn(k.cultura).prod === prod) || {}).cultura || 'Soja';
  /* CT-203, CRE-0095 e BT-090 são vendas futuras do estado (Comercial D-C04): o catálogo não tem mais obrigações (P7) */
  const fut = Object.values(prP(c).pedidos).filter(p => p.tipo === 'futura' && p.prod === prod && p.saf === saf);
  const futKg = prSoma(fut.map(p => prSaldoFut(c, p))); const resKg = prSoma([].concat(...fut.map(p => prResPed(c, p.id))).map(r => r.kg));
  const amb = fut.filter(prAmb).map(p => p.id);   /* Comercial A-17 */
  return { pub, tem, fut, futKg, resKg, amb, livre: amb.length ? null : prSub(pub, prSub(futKg, resKg)), cultura }; }

/* ---------- encerrar a O.S. de colheita (R-18): presente em toda página do estado (cenPodeEncerrar chama) ---------- */
function prPodeEncerrar(c, id) { const o = (c.ordens || {})[id]; if (!o || !prEhColheita(o)) return '';
  const ap = prAPesar(c, id); if (!ap.length) return ''; const sem = ap.filter(g => g.sinc === false), pes = ap.filter(g => g.sinc !== false);
  return [pes.length ? 'Carga a pesar: ' + pes.map(g => g.id).join(', ') + '. ' + prRec(prFazDaOS(c, o)) + ' pesa em Agrícola › Recebimento antes de encerrar a colheita.' : '',
          sem.length ? 'Carga no aparelho aguardando sinal: ' + sem.map(g => g.id).join(', ') + '.' : ''].filter(Boolean).join(' '); }

/* =====================================================================================================================
   Comandos (sempre dentro de cenMudar): chave de quem inicia; mesma chave e mesmo conteúdo = mesmo registro; outro conteúdo = conflito
   ===================================================================================================================== */
function prMov(c, m) { const P = prP(c, 1); P.seq.mp = (P.seq.mp || 1000) + 1; m.id = 'MP-' + P.seq.mp; m.d = m.d || prHoje(); m.at = m.at || cenAgora(); P.movs.push(m); return m; }
function prConflito(id, ja) { return new Error('Este registro (' + id + ') já foi gravado' + (ja ? ' como ' + ja : '') + ' com outro conteúdo: conflito, nada gravado.'); }
function prLocalRec(faz, cultura) { const m = (PRDC.recLocal || {})[faz] || {}; return m[cultura] || m['*'] || ''; }
/* número digitado (pt-BR): a mesma regra do g2num (vírgula decimal; "19.250" e "1.234.567" com ponto de milhar), sem aceitar letra */
function prNum(x) { if (typeof x === 'number') return x; let t = String(x === null || x === undefined ? '' : x).replace(/\s/g, ''); if (!/^-?[\d.,]+$/.test(t)) return NaN;
  if (t.indexOf(',') >= 0) t = t.replace(/\./g, '').replace(',', '.'); else if ((t.match(/\./g) || []).length > 1 || /^-?\d{1,3}(\.\d{3})+$/.test(t)) t = t.replace(/\./g, ''); return Number(t); }
function prNumOk(x) { return x !== '' && x !== null && x !== undefined && isFinite(prNum(x)); }
/* ticket da balança comparável: maiúsculas, sem espaço, hífen, ponto ou barra, sem o prefixo TK ("tk-4520", "TK 4520" e "4520" são o mesmo) */
function prTk(x) { return String(x || '').toUpperCase().replace(/[\s\-_.\/]/g, '').replace(/^TK/, ''); }
/* ID de lote (Colheita R-11; BEN R-A16): L<semana ISO do fato>-<n>, sequência única c.producao.seq.lote (piso 130), nunca reaproveitada;
   também acima de qualquer lote ou destino de saída do beneficiamento já gravado na semana (um ID de saída estornada não volta) */
function prProxLote(c, iso) { const P = prP(c, 1); const w = String(prSemN(prSem(iso))).padStart(2, '0'); const re = new RegExp('^L' + w + '-(\\d+)$'); let n = P.seq.lote[w] || 130;
  const ve = id => { const m = re.exec(String(id || '')); if (m) n = Math.max(n, Number(m[1])); };
  Object.keys(P.lotes).forEach(ve); Object.values(c.ordens || {}).forEach(o => ((o.ben && o.ben.sai) || []).forEach(s => ve(s.lote)));
  P.seq.lote[w] = n + 1; return 'L' + w + '-' + (n + 1); }
/* arredonda para baixo em d casas (sugestão que nunca passa do disponível) */
function prPiso(x, d) { const k = 10n ** BigInt(6 - d); const m = prM(x); const q = m >= 0n ? m / k : -((-m + k - 1n) / k); return prN(q * k); }

/* contagem de frutos (MB-07): grava a amostra; não publica (R-17) */
function prContar(c, k) { prAppAtivo(c, k.via); const P = prP(c, 1); const kk = PRDC.cult[k.cult];
  if (!kk || !kk.semanal) throw new Error('Escolha um talhão de fruta em produção.');
  const n = Number(k.plantas); const e = ['pintado', 'devez', 'verde'].map(x => Number(k[x] || 0)); const peso = prNumOk(k.peso) ? String(prNum(k.peso)) : String(k.peso === undefined ? '' : k.peso);
  const imp = JSON.stringify([k.cult, n, e, peso, k.d || prHoje()]);
  if (k.chave) { const ja = P.contagens.find(x => x.chave === k.chave); if (ja) { if (ja.imp !== imp) throw prConflito(k.chave, ja.id); return { msg: 'Contagem ' + ja.id + ' já registrada: nada foi gravado de novo.', cnt: ja, repetido: true }; } }
  if (!(n > 0) || Math.floor(n) !== n) throw new Error('Conte ao menos uma planta.');
  if (e.some(x => !(x >= 0) || Math.floor(x) !== x)) throw new Error('Frutos por estádio: números inteiros, 0 ou mais.');
  if (!prNumOk(peso) || !(prNum(peso) > 0 && prNum(peso) < 20)) throw new Error('Informe o peso médio do fruto da amostra em kg (ex.: 1,20).');
  P.seq.cnt = (P.seq.cnt || 0) + 1; const id = 'CNT-' + String(P.seq.cnt).padStart(4, '0'); const on = k.via === 'app' ? cenOnline(c) : true;
  const x = { id, cult: k.cult, tal: kk.local, d: k.d || prHoje(), at: cenAgora(), quem: k.quem || '', plantas: n, pintado: e[0], devez: e[1], verde: e[2], peso, chave: k.chave || id, imp, sinc: on, via: k.via || 'web' };
  P.contagens.push(x); if (!on) c.app.fila.push(id);
  const r = prRascunho(c, k.cult); const sems = Object.keys(r.sem).filter(s => !prSemComecou(s));
  return { msg: 'Contagem ' + id + ' do ' + kk.local + ' gravada: ' + n + (n > 1 ? ' plantas' : ' planta') + ', peso médio ' + prFmtT(peso, 2) + ' kg. Rascunho: ' + sems.map(s => prSemTxt(s) + ' ' + prUnTxt(kk.cultura, r.sem[s])).join(' · ')
    + '. A previsão só muda quando ' + prQuem('ag') + ' publicar.' + (on ? '' : ' Salvo no aparelho; envia quando houver sinal.'), cnt: x }; }

/* publicar previsão (Ana): congela a versão nova só das semanas que ainda não começaram (R-17) */
function prPublicar(c, cid, quem, par) { const kk = PRDC.cult[cid]; if (!kk) throw new Error('Cultivo não encontrado.'); const por = prAtorAlc(quem, 'AL-17', 'Publicar a previsão do ' + kk.local); const P = prP(c, 1);
  if (par) { const ph = prNum(par.plantas_ha), pe = prNumOk(par.perda) ? String(prNum(par.perda)) : String(par.perda === undefined ? '' : par.perda);
    if (!(ph > 0 && ph < 10000) || Math.floor(ph) !== ph) throw new Error('Plantas vivas por hectare: número inteiro maior que zero.');
    if (!prNumOk(pe) || prNum(pe) < 0 || prNum(pe) >= 1) throw new Error('Perda entre 0 e 100 %.'); par = { plantas_ha: ph, perda: pe }; }
  const pb = prPublicavel(c, cid, par); if (!pb) throw new Error('Nada novo a publicar no ' + kk.local + ': a versão vigente já tem as semanas que ainda não começaram.');
  const vs = P.previsoes[cid] = P.previsoes[cid] || []; const v = { v: vs.length + 1, d: prHoje(), at: cenAgora(), por, base: pb.base, cnt: pb.cnt || '' };
  if (pb.safra !== undefined) v.safra = pb.safra; else { v.sem = pb.sem; v.plantas_ha = pb.par.plantas_ha; v.perda = pb.par.perda; }
  vs.push(v);
  const txt = v.safra !== undefined ? 'safra ' + prUnTxt(kk.cultura, v.safra, 0) : Object.keys(v.sem).map(s => prSemTxt(s) + ' ' + prUnTxt(kk.cultura, v.sem[s])).join(' · ');
  const cur = pb.sem ? prRascunho(c, cid) : null; const s0 = prSem(prHoje()); const os0 = prOsCult(c, cid).find(o => prSemDaOS(o) === s0);
  return { msg: kk.local + ' · previsão v' + v.v + ' publicada por ' + v.por + ': ' + txt + '.' + (cur && cur.sem && cur.sem[s0] !== undefined ? ' A semana em curso (' + prSemTxt(s0) + ') não muda' + (os0 ? ': orienta a ' + os0.id + '.' : '.') : ''), v }; }

/* carga do campo (MB-10 · aba Colheita): a pesar na balança; caixas ou kg estimados nunca somam (R-03) */
function prCarga(c, k) { prAppAtivo(c, k.via || 'app'); const P = prP(c, 1); const mix = (k.mix && k.mix.length) ? k.mix : [{ os: k.os, pct: 100, modo: 'medida' }];
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
  const out = mix.map(x => { const o = (c.ordens || {})[x.os]; if (!o || !prEhColheita(o)) throw new Error('Origem sem O.S. de colheita (' + (x.os || 'vazia') + ').');
    if (PR_FASES_COLH.indexOf(o.etapa) < 0) throw new Error(x.os + ' está em ' + o.etapa + ': a carga sai de O.S. de colheita liberada, em execução ou em conferência.');
    if (!(Number(x.pct) > 0)) throw new Error('Informe a participação de ' + o.talhao + '.');
    return { os: x.os, cult: prCultDaOS(c, o), tal: o.talhao, pct: Number(x.pct), modo: x.modo || 'medida', cultura: (PRDC.cult[prCultDaOS(c, o)] || {}).cultura || '', faz: prFazDaOS(c, o) }; });
  /* revisão A-08: uma carga é de um produto e de uma fazenda; mistura de culturas ou fazendas poria massa de uma cultura na produção da outra */
  const d = out.find(x => x.cultura !== out[0].cultura || x.faz !== out[0].faz);
  if (d) throw new Error('Mistura recusada: ' + d.tal + ' (' + d.os + ', ' + d.cultura + ', ' + d.faz + ') não é da mesma cultura e fazenda de ' + out[0].tal + ' (' + out[0].cultura + ', ' + out[0].faz + '). Registre uma carga por cultura.');
  return out.map(x => ({ os: x.os, cult: x.cult, tal: x.tal, pct: x.pct, modo: x.modo })); }
/* O.S. que podem dividir a carga com a primeira: colheita na fase de origem, mesma cultura e mesma fazenda (a mesma regra da recusa) */
function prMixCompat(c, os1) { const o1 = (c.ordens || {})[os1]; if (!o1) return []; const cu = (PRDC.cult[prCultDaOS(c, o1)] || {}).cultura, fz = prFazDaOS(c, o1);
  return Object.values(c.ordens || {}).filter(o => o.id !== os1 && prEhColheita(o) && PR_FASES_COLH.indexOf(o.etapa) >= 0 && (PRDC.cult[prCultDaOS(c, o)] || {}).cultura === cu && prFazDaOS(c, o) === fz).sort((a, b) => a.id.localeCompare(b.id)); }

/* id do lote novo: L<semana do dia>-<seq da semana> (o mesmo gerador do recebimento e da devolução do Comercial, R-C10) */
function prNovoLote(c, dia) { return prProxLote(c, dia); }   /* integração V56: um gerador só (prProxLote do BEN, que também olha os lotes e as saídas do beneficiamento já gravados) */
/* pesar e receber (CARGA): ticket, bruto e tara; descontos de grão; lote por produto + local + dia + origem (R-07, R-08, R-10, R-11) */
const PR_CONDS = ['Íntegra', 'Com avaria', 'Fora do padrão'];
function prReceber(c, k) { const P = prP(c, 1); const g0 = k.carga ? P.cargas[k.carga] : null;
  if (k.carga && (!g0 || g0.sinc === false)) throw new Error('Carga ' + k.carga + ' não encontrada (no aparelho, sem sinal?).');
  const mix = g0 ? g0.origem.map(x => ({ os: x.os, pct: x.pct, modo: x.modo })) : ((k.mix && k.mix.length) ? k.mix : [{ os: k.os, pct: 100, modo: 'medida' }]);
  const osId = mix[0].os; const o = (c.ordens || {})[osId]; if (!o || !prEhColheita(o)) throw new Error('Escolha a O.S. de colheita de origem.');
  const tk = String(k.ticket || '').trim(); const tkn = prTk(tk); const dcol = (g0 && g0.dcol) || k.dcol || prHoje();
  const imp = JSON.stringify([mix.map(x => [x.os, Number(x.pct)]), tkn, prNum(k.bruto), prNum(k.tara), k.u === undefined ? null : String(k.u), k.imp === undefined ? null : String(k.imp), prNum(k.litros) || 0, prNum(k.frutos) || 0, k.cond || '', k.local || '', dcol]);
  if (k.chave) { const ja = Object.values(P.cargas).find(g => g.chaveRec === k.chave); if (ja) { if (ja.impRec !== imp) throw prConflito(k.chave, ja.id); return { msg: 'Pesagem já registrada (' + ja.id + ' · ticket ' + ja.ticket + '): nada foi somado de novo.', g: ja, repetido: true }; } }
  if (g0 && g0.st !== 'A pesar') throw new Error(g0.id + ' já está ' + g0.st.toLowerCase() + '.');
  const faz = prFazDaOS(c, o); const quemRec = prAtorRec(faz, k.quem, 'Pesar e receber ' + (g0 ? 'a ' + g0.id : 'a carga da ' + osId));
  const kk = PRDC.cult[prCultDaOS(c, o)] || {}; const cultura = kk.cultura || (g0 && g0.cultura); const u = prUn(cultura);
  if (!tkn) throw new Error('Informe o ticket da balança.');
  const dupT = Object.values(P.cargas).find(g => g.st === 'Recebida' && g.faz === faz && prTk(g.ticket) === tkn);
  if (dupT) { if (dupT.impRec === imp) return { msg: 'Ticket ' + tk + ' já recebido na ' + dupT.id + ' com o mesmo conteúdo: é a mesma carga, nada foi somado de novo.', g: dupT, repetido: true };
    throw new Error('Ticket ' + tk + ' já recebido na ' + dupT.id + (dupT.ticket !== tk ? ' (como ' + dupT.ticket + ')' : '') + ' (' + prFmtT(dupT.liq, 2) + ' kg líquidos) com outro conteúdo: conflito, nada gravado. Confira o ticket.'); }
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
  const q0 = k.cond === 'Íntegra' ? 'Liberado' : 'Em inspeção';
  /* revisão A-05: lote liberado depois pela Qualidade não recebe carga nova com avaria (ela nasceria apta sem conferência) */
  /* BEN-1 (BEN-REV-09): lote que entrou numa ordem de beneficiamento (mesmo em A liberar) não recebe carga nova; a ordem leva o lote inteiro */
  let L = misto ? null : Object.values(P.lotes).find(x => !x.misto && x.prod === prod && x.local === local && x.drec === drec && x.cond === k.cond && x.q0 === q0 && !x.lib && !x.ordem && !x.esg
    && !(typeof benOrdemAberta === 'function' && benOrdemAberta(c, x.id)) && (x.origem || []).length && x.origem.every(y => y.os === osId && y.dcol === dcol));
  const novo = !L;
  if (!L) { const id = prProxLote(c, drec);
    L = P.lotes[id] = { id, prod, cultura, classe: u.grao ? 'Padrão' : '', saf: (PRDC.safras[kk.saf] || {}).mf || '', faz, local, drec, dcol, validade: u.vida ? prDiaMais(dcol, u.vida) : null,
      q0, cond: k.cond, misto, origem: [], cargas: [] }; }
  const g = g0 || (P.seq.cg = (P.seq.cg || 2100) + 1, P.cargas['CG-' + P.seq.cg] = { id: 'CG-' + P.seq.cg, os: osId, dcol, via: 'web', sinc: true, chave: k.chave || ('W-CG-' + P.seq.cg), hora: cenAgora() });
  Object.assign(g, { ticket: tk, faz, cultura, os: osId, dcol, drec, bruto: prNum(k.bruto), tara: prNum(k.tara), liq, com, u: u.grao ? String(prNum(k.u)) : null, imp: g.imp,
    impG: u.grao ? String(prNum(k.imp)) : null, desc, litros: u.campo ? prNum(k.litros) : null, frutos: u.base === 'frutos' ? prNum(k.frutos) : null, cond: k.cond, local, st: 'Recebida', lote: L.id,
    origem: orig.map((x, i) => Object.assign({}, x, { kg: pLiq[i], com: pCom[i], base: pBase[i], litros: u.campo ? pBase[i] : 0 })), quemRec, chaveRec: k.chave || ('W-' + g.id), impRec: imp, horaRec: cenAgora() });
  orig.forEach((x, i) => L.origem.push({ carga: g.id, os: x.os, cult: x.cult, tal: x.tal, dcol, kg: pBase[i], modo: x.modo }));
  L.cargas.push(g.id); if (L.validade && u.vida) L.validade = [L.validade, prDiaMais(dcol, u.vida)].sort()[0];
  prMov(c, { tipo: 'recebimento', lote: L.id, kg: base, carga: g.id, quem: g.quemRec });
  const S = prSaldos(c, L); const R = prResultado(c, prCultDaOS(c, o)); const pa = R && R.passes.find(p => p.os === osId);
  return { msg: g.id + ' recebida: ' + prFmtT(liq, 2) + ' kg líquidos (' + prFmtT(prNum(k.bruto), 2) + ' − ' + prFmtT(prNum(k.tara), 2) + ')' + (u.grao ? ' · comercial ' + prFmtT(com, 2) + ' kg = ' + prUnTxt(cultura, com) : '')
    + ' no ' + L.id + (novo ? ' (novo)' : '') + ' · ' + PRDC.locais[local].nome + ' · ' + S.q + '.' + (pa && pa.area > 0 ? ' ' + o.talhao + ': passe ' + prSemTxt(pa.sem) + ' ' + prPrtvResTxt(cultura, pa) + (pa.final || pa.apurar ? '.' : ' (parcial).') : ''), g, L }; }

/* carga cujo lote está em processo numa ordem de beneficiamento liberada (BEN-REV-02): o estorno tiraria do lote a massa que a ordem já
   consome no Fechar (lote negativo e produto sem origem). Em A liberar a ordem é rascunho: o estorno passa e a liberação confere de novo */
function prEstornoImpede(c, g) { const L = g && prP(c).lotes[g.lote]; const ob = L && typeof benPrende === 'function' ? benPrende(c, L) : null; if (!ob) return '';
  return g.id + ' alimenta o ' + L.id + ', em processo na ' + ob.id + ' (' + ob.etapa + '): estorno recusado. Erro de pesagem aparece no balanço da ordem: justifique a diferença na conferência (alçada).'; }
/* estornar carga recebida (R-19): motivo; devolve o efeito; recusa se o lote ficar abaixo do reservado; o ticket fica livre */
function prEstornar(c, id, motivo, quem) { const P = prP(c, 1); const g = P.cargas[id]; if (!g || g.st !== 'Recebida') throw new Error('Só carga recebida é estornada.');
  const por = prAtorRec(g.faz, quem, 'Estornar a ' + id);
  const mot = String(motivo || '').trim(); if (!mot) throw new Error('Informe o motivo do estorno.');
  const imp = prEstornoImpede(c, g); if (imp) throw new Error(imp);
  const L = P.lotes[g.lote]; const mv = P.movs.find(m => m.tipo === 'recebimento' && m.carga === id); const kg = mv ? mv.kg : 0;
  const fis = prFis(c, L.id), res = prResLote(c, L.id); const fica = prSub(fis, kg);
  if (prCmp(fica, res) < 0) throw new Error('Estorno recusado: o ' + L.id + ' ficaria com ' + prLoteTxt(L, fica) + ', abaixo do reservado (' + prLoteTxt(L, res) + '). Cancele ou reduza a reserva antes.');
  prMov(c, { tipo: 'estorno', lote: L.id, kg: -kg, carga: id, quem: por, obs: mot });
  (L.origem || []).forEach(x => { if (x.carga === id) x.est = true; }); g.st = 'Estornada'; g.estorno = { motivo: mot, quem: por, d: prHoje(), at: cenAgora() }; g.ticketLivre = g.ticket;
  return { msg: id + ' estornada (' + mot + '): ' + prLoteTxt(L, kg) + ' saem do ' + L.id + '. O ticket ' + g.ticket + ' fica livre para novo registro; o histórico continua.' }; }

/* descartar carga A pesar (revisão A-06): registro do app em dobro ou carga que não saiu; nada pesado, nada a estornar; motivo e trilha ficam */
function prDescartarCarga(c, id, motivo, quem, via) { prAppAtivo(c, via); const P = prP(c, 1); const g = P.cargas[id]; if (!g) throw new Error('Carga ' + id + ' não encontrada.');
  if (g.st !== 'A pesar') throw new Error(id + ' está ' + String(g.st).toLowerCase() + ': só carga a pesar é descartada' + (g.st === 'Recebida' ? ' (carga recebida: estorne com motivo).' : '.'));
  const mot = String(motivo || '').trim(); if (!mot) throw new Error('Informe o motivo do descarte.');
  const por = via === 'app' ? (quem || (c.app && c.app.operador) || '') : prAtorRec(g.faz, quem, 'Descartar a ' + id);   /* app: o operador do aparelho (cenAppAtivo acima) */
  g.st = 'Descartada'; g.descarte = { motivo: mot, quem: por, d: prHoje(), at: cenAgora(), via: via || 'web' };
  if (c.app && Array.isArray(c.app.fila)) c.app.fila = c.app.fila.filter(x => x !== id);
  return { msg: id + ' descartada (' + mot + '): a carga sai da fila de pesagem; nada entra na produção. O registro e o motivo ficam no histórico.' }; }

/* liberar lote (Qualidade, R-13): reavalia carência e ordem; recusa com a pendência e o dono. Quem age (Comercial A3 da revisão, R-C10):
   o perfil com o papel qualidade ou agrônomo (a mesma regra do BEN-1 (d) na branch única); grava g2ator, nunca um nome fixo
   (lote devolvido não volta à venda sem conferência) */
/* ator = perfil de quem age (CTL-3): só a Qualidade ou a agrônoma libera lote (BEN-1 (d)); dano evitado: liberação gravada em nome de quem não decidiu */
/* recebido fora do íntegro num local de processo ou com pós-colheita (BEN-REV-03): o lote está "em processo" pelo local, mas a qualidade do
   recebimento (a que vale para entrar numa ordem, R-A03) ainda espera a Qualidade. Sem ordem que o prenda, a Qualidade confere e libera essa
   qualidade; o lote continua fora do vendável e vai ao beneficiamento */
function prLibProc(c, L) { if (!L || L.insp || L.benef || L.q0 === 'Liberado') return false; if (L.ordem && (c.ordens || {})[L.ordem] && ['Encerradas', 'Canceladas'].indexOf(c.ordens[L.ordem].etapa) < 0) return false;
  const S = prSaldos(c, L); if (S.q !== 'Em processo' || S.esgotado) return false; const B = prQualidade(c, L, { base: true }); return B.q === 'Em inspeção' && (!B.dono || B.dono === prQuem('qual')); }
function prLiberarLote(c, lid, ator) { const quem = cenExigeUm(ator, ['qualidade', 'agronomo'], 'Liberar o lote ' + lid); const P = prP(c, 1); const L = P.lotes[lid]; if (!L) throw new Error('Lote não encontrado.'); const S = prSaldos(c, L);
  if (L.insp) throw new Error(lid + (L.benef ? ' é lote do beneficiamento (' + L.benef + ')' : ' tem a inspeção ' + L.insp) + ': registre o resultado da inspeção ' + L.insp + ' e a decisão' + (L.benef ? ' (fechar o processo não libera).' : '.'));
  if (S.q === 'Liberado') throw new Error(lid + ' já está liberado.');
  const proc = S.q === 'Em processo' && prLibProc(c, L);
  if (S.q === 'Em processo' && !proc) throw new Error(lid + ' está em processo (' + S.mot + '): ' + (L.q0 === 'Liberado' ? 'já liberado para o beneficiamento; ' : '') + 'o beneficiamento libera o lote de saída.');
  if (S.q === 'Bloqueado') throw new Error('Liberar recusado: ' + S.mot + '. Lote bloqueado por carência só sai pela Qualidade com laudo (fora desta etapa). Quem decide: ' + S.dono + '.');
  const Q = prQualidade(c, Object.assign({}, L, { q0: 'Liberado' }), proc ? { base: true } : undefined); if (Q.q !== 'Liberado') throw new Error('Liberar recusado: ' + Q.mot + '. Quem resolve: ' + Q.dono + '.');
  L.q0 = 'Liberado'; L.lib = { quem, d: prHoje(), at: cenAgora() }; prMov(c, { tipo: 'liberação', lote: lid, kg: 0, fis: false, quem: L.lib.quem, obs: proc ? 'qualidade do recebimento; segue em processo (' + S.mot + ')' : '' });
  return { msg: lid + ' liberado por ' + L.lib.quem + ': ' + prLoteTxt(L, S.fis) + (proc ? ' seguem para o beneficiamento; ' + ((typeof BENC !== 'undefined' && BENC.quem.prod) || 'o beneficiamento') + ' abre a ordem.' : ' aptos para reserva e venda.') }; }

/* reservar lote apto para pedido (R-15): mesma classe, avaliação do destino, ≤ disponível e ≤ falta; dedução única.
   Quem age (Comercial R-C05, R-C14, CE-10): ator obrigatório com papel comercial ou gestor; a reserva grava g2ator, nunca um nome fixo */
function prReservar(c, k) { const P = prP(c, 1); const kg = prNumOk(k.kg) ? prNum(k.kg) : NaN; const imp = JSON.stringify([k.pedido, k.lote, kg]);
  if (k.chave) { const ja = Object.values(P.reservas).find(r => r.chave === k.chave); if (ja) { if (ja.imp && ja.imp !== imp) throw prConflito(k.chave, ja.id); return { msg: 'Reserva ' + ja.id + ' já registrada: nada foi deduzido de novo.', rs: ja, repetido: true }; } }
  const quem = cenExigeUm(k.ator, ['comercial', 'gestor'], 'Reservar lote' + (k.pedido ? ' para o ' + k.pedido : ''));
  const ped = P.pedidos[k.pedido]; if (!ped) throw new Error('Escolha o pedido.'); const L = P.lotes[k.lote]; if (!L) throw new Error('Escolha o lote.');
  if (prAmb(ped)) throw new Error(ped.id + ': saca do contrato a conferir (' + ped.fatAmb.join(' ou ') + ' kg). A reserva fica suspensa até registrar a massa da saca em Comercial › Contratos e pedidos. Nada foi alterado.');
  const ce = prCompatErro(ped, L); if (ce) throw new Error(ce);
  const S = prSaldos(c, L); if (S.q !== 'Liberado') throw new Error(L.id + ' não está apto (' + S.q + ': ' + S.mot + '). Quem resolve: ' + (S.dono || prQuem('qual')) + '.');
  const dest = ped.dest || 'MI-BR'; let pend = [];
  if (typeof carAvaliar === 'function' && typeof CARD !== 'undefined') for (const lc of prLcs(c, L)) { const a = carAvaliar(c, lc, dest);
    if (a.st === 'nao_conforme') { const x = a.motivos[0] || {}; throw new Error('Reserva recusada: ' + lc + ' ' + a.rot + ' · ' + (x.t || '') + (x.q ? ' (quem decide: ' + x.q + ')' : '') + '.'); }
    if (a.st === 'pendente') pend = pend.concat(a.faltas.map(f => f.t + ' (' + f.q + ')')); }
  if (!(kg > 0)) throw new Error('Informe a quantidade a reservar.');
  if (prCmp(kg, S.disp) > 0) throw new Error('Acima do disponível do ' + L.id + ': ' + prLoteTxt(L, S.disp) + '.');
  const falta = prFalta(c, ped); if (prCmp(kg, falta) > 0) throw new Error('Acima da falta do ' + ped.id + ': ' + prTxtP(ped, falta) + '.');
  const ini = ped.ini || (ped.sem ? prSemIni(ped.sem) : ''); const venceAntes = !!(L.validade && ini && L.validade < ini);   /* aviso, não trava (D-21 da Colheita; Comercial R-C05) */
  P.seq.rs = (P.seq.rs || 0) + 1; const id = 'RS-' + String(P.seq.rs).padStart(4, '0');
  const rs = P.reservas[id] = { id, pedido: ped.id, lote: L.id, kg, kg0: kg, exp: 0, st: 'Ativa', d: prHoje(), at: cenAgora(), quem, chave: k.chave || id, imp };
  prMov(c, { tipo: 'reserva', lote: L.id, kg, fis: false, reserva: id, pedido: ped.id, quem: rs.quem });
  const S2 = prSaldos(c, L); const sit = prSitPed(c, ped);
  return { msg: id + ': ' + prTxtP(ped, kg) + ' do ' + L.id + ' reservados para o ' + ped.id + ' (' + ped.cliente + '). ' + L.id + ' disponível ' + prLoteTxt(L, S2.disp) + ' · ' + ped.id + ' ' + sit.t.toLowerCase() + '.'
    + (pend.length ? ' Destino ' + (PRDC.dest[dest] || dest) + ' pendente: ' + pend[0] + '; a saída só passa com o destino conforme.' : '')
    + (venceAntes ? ' Aviso: o ' + L.id + ' vence ' + prBr(L.validade) + ', antes do início da janela do ' + ped.id + ' (' + prBr(ini) + ').' : ''), rs }; }
function prCancelarReserva(c, id, motivo, ator) { const P = prP(c, 1); const r = P.reservas[id]; if (!r || r.st !== 'Ativa') throw new Error('Reserva não está ativa.');
  const quem = cenExigeUm(ator, ['comercial', 'gestor'], 'Cancelar a ' + id);   /* ator obrigatório (Comercial CE-10) */
  /* Comercial A5 da revisão: a reserva de lote que está numa carga programada da mesma venda não se cancela sozinha (a carga ficaria
     sem reserva e o caminhão sairia do disponível ou da reserva de outro): cancele a carga antes, como no encerrar saldo (R-C11) */
  const pg = Object.values(P.expedicoes || {}).filter(x => x.st === 'Programada' && x.pedido === r.pedido && (x.lotes || []).some(l => l.lote === r.lote)).map(x => x.id);
  if (pg.length) throw new Error('Cancelar a ' + id + ' recusado: ' + pg.join(', ') + ' programada com o ' + r.lote + ' para o ' + r.pedido + '. Cancele a carga antes (Expedição e entregas). Nada foi alterado.');
  const mot = String(motivo || '').trim(); if (!mot) throw new Error('Informe o motivo do cancelamento da reserva.');
  r.st = 'Cancelada'; r.canc = { motivo: mot, quem, d: prHoje(), at: cenAgora() };
  prMov(c, { tipo: 'cancelamento de reserva', lote: r.lote, kg: -r.kg, fis: false, reserva: id, pedido: r.pedido, quem: r.canc.quem, obs: mot });
  const L = P.lotes[r.lote]; return { msg: id + ' cancelada (' + mot + '): ' + prLoteTxt(L, r.kg) + ' voltam ao disponível do ' + r.lote + '.' }; }
/* gancho de teste/inspeção (o script da tela roda isolado) */
try { window.__pr = { prResultado, prSaldos, prQualidade, prOfertaSem, prOfertaSafra, prReceber, prReservar, prCancelarReserva, prEstornar, prLiberarLote, prPublicar, prContar, prCarga, prPodeEncerrar, prDescartarCarga, prApontarColheita, prApLista }; } catch (e) {}

/* ---------- situação do talhão na colheita (COLH, spec §3.1) · fonte única da tela Previsão e colheita e da camada Colheita do Mapa (14/10/2026) ---------- */
const PR_SITORD={'Em colheita':0,'Programada':1,'Prevista':2,'Colhida':3,'Sem previsão':4};
const PR_SITCOR={'Em colheita':'green','Programada':'blue','Prevista':'gray','Colhida':'gray','Sem previsão':'yellow'};
/* janela de colheita do cultivo anual: a data do cultivo ou plantio + 120 dias */
function prJanAnual(k){ return k.colheita||(k.plantio?prDiaMais(k.plantio,120):''); }
/* situação, próximo passo e ação do talhão (spec §3.1): perene manda a próxima semana ainda sem ordem; anual, a safra */
function prTal(c,cid){ const k=PRDC.cult[cid]; const R=prResultado(c,cid); const oss=prOsCult(c,cid); const vs=prP(c).previsoes[cid]||[]; const ult=vs[vs.length-1]||null;
  const abertas=oss.filter(o=>o.etapa!=='Encerradas'); const exec=abertas.find(o=>o.etapa==='Em execução'||o.etapa==='Em conferência'); const prog=abertas.find(o=>o.etapa==='A liberar'||o.etapa==='Liberadas');
  let sit; if(exec) sit='Em colheita'; else if(prog) sit='Programada'; else if(R.passes.some(p=>p.final)&&!(ult&&Object.keys(ult.sem||{}).some(w=>!prSemComecou(w)))) sit='Colhida'; else if(ult) sit='Prevista'; else sit='Sem previsão';
  const cnt=k.semanal?prContagem(c,cid):null; const pub=prPublicavel(c,cid); const ag=prQuem('ag'); const agO=g2alcQuem('AL-02')||ag; let ac=null;   /* publicar: AL-17; emitir a O.S. e acompanhar: o agrônomo da O.S. (AL-02) */
  if(k.semanal){ let w=prSemMais(prSem(prHoje()),1); while(oss.some(o=>prSemDaOS(o)===w)) w=prSemMais(w,1);
    const atv=(PRDC.colhAtv||{})[k.plano];
    if(!cnt) ac={k:'contar',t:'Coletar contagem',h:'MB-07.dc.html#'+cid,q:'equipe de colheita (app)',x:'contar os frutos de 20 plantas'};
    else if(pub) ac={k:'publicar',t:'Publicar previsão',q:ag,x:'publicar '+Object.keys(pub.sem).map(prSemTxt).join(' e ')};
    else if(atv&&prVersaoSem(c,cid,w)) ac={k:'programar',t:'Programar colheita '+prSemTxt(w),h:'OS.dc.html#nova:'+cid+':'+atv+':'+prSemIni(w),q:agO,x:'emitir a O.S. da '+prSemTxt(w)};
    else if(exec||prog) ac={k:'abrir',t:'Abrir '+(exec||prog).id,h:'OS.dc.html#'+(exec||prog).id,q:(exec||prog).resp||agO,x:(exec?'acompanhar a '+exec.id:'liberar a '+prog.id)}; }
  else { const jan=prJanAnual(k); const perto=jan&&jan<=prDiaMais(prHoje(),30); const atv=(PRDC.colhAtv||{})[k.plano];
    if(pub&&!(R.comecou)) ac={k:'publicar',t:'Publicar previsão',q:ag,x:'publicar a previsão da safra pela meta'};
    else if(exec||prog) ac={k:'abrir',t:'Abrir '+(exec||prog).id,h:'OS.dc.html#'+(exec||prog).id,q:(exec||prog).resp||agO,x:'acompanhar a '+(exec||prog).id};
    else if(perto&&atv) ac={k:'programar',t:'Programar colheita',h:'OS.dc.html#nova:'+cid+':'+atv+':'+jan,q:agO,x:'emitir a O.S. de colheita'}; }
  /* COLH-APONT (GESTAO-1810 §2, C1): com O.S. de colheita Em execução (ou só Liberada) a primária do talhão é "Apontar colheita"; o passo da
     previsão que valeria (contar, publicar, programar) fica em ac0, como secundária do painel. Dano evitado: colheita do dia sem registro */
  const apo=abertas.find(o=>o.etapa==='Em execução')||abertas.find(o=>o.etapa==='Liberadas')||null; let ac0=null;
  if(apo){ ac0=ac&&ac.k!=='abrir'?ac:null; ac={k:'apontar',t:'Apontar colheita',os:apo.id,q:prResp(apo),x:apo.etapa==='Em execução'?'apontar a colheita do dia na '+apo.id:'iniciar a '+apo.id+' para apontar a colheita'}; }
  const nx=ac?(ac.x.charAt(0).toUpperCase()+ac.x.slice(1)+' · '+ac.q):(k.semanal?'acompanhar':(prJanAnual(k)?'colheita a partir de '+prBr(prJanAnual(k))+'/'+prJanAnual(k).slice(2,4)+' · nada a fazer agora':'sem janela de colheita'));
  return {k,R,sit,ac,ac0,apo,nx,ult,cnt,pub,exec,prog,oss}; }
/* previsão vigente na linha: semana em curso ou a próxima publicada; anual, a safra */
function prPrevTxt(c,X){ const k=X.k; const vs=prP(c).previsoes[k.id]||[];
  if(!k.semanal){ const v=vs.filter(x=>x.safra!==undefined).slice(-1)[0]; return v?{t:prUnTxt(k.cultura,v.safra,0)+' · safra (v'+v.v+')',v:v.safra}:{t:'sem previsão publicada',v:null}; }
  const s0=prSem(prHoje()); const ws=[...new Set([].concat(...vs.map(v=>Object.keys(v.sem||{}))))].sort(); const w=ws.find(x=>x>=s0)||ws[ws.length-1];
  if(!w) return {t:X.cnt?'rascunho pela contagem':'sem previsão publicada',v:null}; const v=prVersaoSem(c,k.id,w); return {t:prUnTxt(k.cultura,v.sem[w],1)+' · '+prSemTxt(w)+' (v'+v.v+')',v:v.sem[w]}; }

/* ---------- COLH-APONT · apontamento da colheita pela web (docs/gestao/GESTAO-1810.md §2, F1) ----------
   Área, data, horas e observação gravam pelo comando único do apontamento (cenApontar, origem web, chave do formulário): a mesma duplicidade,
   o mesmo saldo da ordem e a mesma conferência do app (R-02, R-07; ENG-021). Umidade média e perdas são só registro da colheita: ficam em
   c.producao.apont, pela chave do apontamento, nunca por cima do ap. Quantidade nunca vem do último valor (AGENTS §3.3). */
/* saldo a colher da ordem: o mesmo do app (MB-10) e do comando, descontando o que ainda está no aparelho sem sinal */
function prApSaldo(o) { return Math.max(0, (o.saldo || 0) - (typeof cenApPend === 'function' ? cenApPend(o) : 0)); }
/* validação do formulário (uma regra, dois usos: o erro junto do campo na tela e a recusa do comando). Devolve {campo: mensagem} */
function prApValida(k, hoje) { const e = {}; const h0 = hoje || prHoje(); const vazio = x => x === undefined || x === null || String(x).trim() === '';
  const iso = prIsoDe(k.d, h0); const real = iso && new Date(iso + 'T12:00:00Z').toISOString().slice(0, 10) === iso;
  if (!real) e.d = 'Informe a data (dd/mm) ou toque num atalho.'; else if (iso > h0) e.d = 'Data futura: aponte só o que já foi colhido (hoje é ' + prDdMm(h0) + ').';
  if (vazio(k.ha) || !prNumOk(k.ha) || !(prNum(k.ha) > 0)) e.ha = 'Informe a área colhida (maior que 0 ha).';
  if (!vazio(k.h) && !(prNumOk(k.h) && prNum(k.h) > 0)) e.h = 'Horas: número maior que 0 (ex.: 8).';
  if (!vazio(k.umid) && !(prNumOk(k.umid) && prNum(k.umid) > 0 && prNum(k.umid) < 100)) e.umid = 'Umidade: número entre 0 e 100 (ex.: 14,5).';
  if (!vazio(k.perda) && !(prNumOk(k.perda) && prNum(k.perda) >= 0)) e.perda = 'Perdas: número igual ou maior que 0.';
  return e; }
/* k = {os, d (dd/mm), ha, h?, umid?, perda?, obs?, chave, por (quem registrou)} · mesma chave e mesmo conteúdo = o mesmo registro; outro = conflito */
function prApontarColheita(c, k) { const o = (c.ordens || {})[k.os]; if (!o || !prEhColheita(o)) throw new Error('O.S. de colheita não encontrada.');
  const e = prApValida(k); const m = Object.keys(e); if (m.length) throw new Error(e[m[0]]);
  const num = x => (x === undefined || x === null || String(x).trim() === '') ? null : prNum(x); const reg = { umid: num(k.umid), perda: num(k.perda) };
  const R = cenApontar(c, { os: k.os, d: k.d, ha: prNum(k.ha), h: num(k.h) === null ? undefined : num(k.h), obs: String(k.obs || '').trim(), origem: 'web', chave: k.chave });
  const P = prP(c, 1); P.apont = P.apont || {}; const ja = P.apont[k.chave];
  if (R.repetido) { if (ja && (ja.umid !== reg.umid || ja.perda !== reg.perda)) throw prConflito(k.chave, 'dia ' + R.ap.dia + ' da ' + k.os);
    return { msg: 'Apontamento já registrado (' + k.os + ' · ' + prFmtT(R.ap.ha, 2) + ' ha em ' + R.ap.d + '): nada somado de novo.', ap: R.ap, repetido: true }; }
  P.apont[k.chave] = { os: k.os, dia: R.ap.dia, d: k.d, umid: reg.umid, perda: reg.perda, por: k.por || '', at: R.ap.at };
  let conf = ''; try { conf = CEN_CONF_AP(); } catch (x) { conf = ''; }
  if (R.ap.st === CEN_AP_DUP) return { msg: 'Retido como duplicidade a conferir: a ' + k.os + ' já tem apontamento em ' + k.d + ' (' + cenApDupTxt(cenApDupVivos(o, R.ap)) + '). Nada somado' + (conf ? ' até a decisão de ' + conf : '') + '.', ap: R.ap };
  return { msg: 'Colheita apontada: ' + prFmtT(R.ap.ha, 2) + ' ha em ' + k.d + ' na ' + k.os + ', provisório' + (conf ? ' até ' + conf + ' conferir' : '') + '. Saldo a colher: ' + prFmtT(prApSaldo(o), 2) + ' ha. A produção só muda com a carga pesada.', ap: R.ap }; }
/* apontamentos do cultivo, do dia mais recente ao mais antigo: todo relato das O.S. de colheita menos o previsto (plano, não fato), com o
   registro da colheita (umidade, perdas, quem registrou na web) pela chave */
function prApLista(c, cid) { const A = prP(c).apont || {}; const out = [];
  prOsCult(c, cid).forEach(o => (o.ap || []).filter(a => a.st !== 'Previsto').forEach(a => out.push({ o, a, iso: prIsoDe(a.d), r: (a.chave && A[a.chave]) || null })));
  return out.sort((x, y) => (x.iso < y.iso ? 1 : (x.iso > y.iso ? -1 : (y.a.dia - x.a.dia)))); }
/* por que o talhão não aponta agora e o próximo passo com verbo (C3): sem O.S. de colheita liberada ou em execução */
function prApMotivo(c, X) { const k = X.k; const ab = X.oss.filter(o => o.etapa !== 'Encerradas'); const alib = ab.find(o => o.etapa === 'A liberar'), conf = ab.find(o => o.etapa === 'Em conferência');
  if (alib) return { t: alib.id + ' ainda a liberar: libere a ordem para apontar a colheita.', l: { t: 'Abrir ' + alib.id, h: 'OS.dc.html#' + alib.id } };
  const atv = (PRDC.colhAtv || {})[k.plano]; let h = '';
  if (atv) { let jan; if (k.semanal) { let w = prSemMais(prSem(prHoje()), 1); while (X.oss.some(o => prSemDaOS(o) === w)) w = prSemMais(w, 1); jan = prSemIni(w); } else jan = prJanAnual(k) || prHoje();
    h = 'OS.dc.html#nova:' + k.id + ':' + atv + ':' + jan; }
  const t = (conf ? conf.id + ' em conferência: a colheita dela terminou. ' : '') + 'Sem O.S. de colheita liberada ou em execução neste talhão: programe a colheita para apontar.';
  return { t, l: h ? { t: 'Programar colheita', h } : null, sem: !h ? 'O plano do cultivo não tem atividade de colheita: inclua-a no plano agronômico.' : '' }; }
