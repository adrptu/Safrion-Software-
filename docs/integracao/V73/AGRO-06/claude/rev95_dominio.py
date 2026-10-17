# -*- coding: utf-8 -*-
"""rev95: contraexemplos de domínio (Node, sem navegador) sobre os helpers reais do PR #95 + solo.js real. Dados sintéticos.
Uso: SAFRION_DADOS=sintetico python3 -B rev95_dominio.py <gen37> [analise_solo.py alternativo]"""
import os, sys, subprocess, json, tempfile
GEN = os.path.abspath(sys.argv[1]); sys.path.insert(0, GEN); os.chdir(GEN)
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
import cenario, dados_solo
src_ui = open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(GEN, 'areas/analise_solo.py'), encoding='utf-8').read()
b = src_ui.index('const SO_UN='); e = src_ui.index('function soFazOk', b); helpers = src_ui[b:e]
PROBE = r"""
const OUT = {}; const NOVO = () => cenClone(CEN0);
function MUD(c, fn) { const x = cenClone(c); try { const r = fn(x) || {}; Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); return r; } catch (e) { return { erro: String(e.message || e) }; } }
const HAS = typeof soRlAnalito === 'function';
OUT.helpers = HAS;
const CU = (cid) => soloCultivoBase(SOLO0, SOLO0.cult.find(x => x.id === cid));
const SG = (c, cid) => soloSugestoes(soloCtxBase(c, SOLO0), CU(cid));
const cT1 = SOLO0.cult.find(x => x.tal === 'T1' && x.faz === 'Santa Rita'); OUT.cT1 = cT1 ? [cT1.id, cT1.cultura] : null;
/* linhas da tela -> envio -> comando real */
function reg(c, rows, ext, extra, chave) { const an = HAS ? soRlEnviarAnalitos(rows.map(r => soRlAnalito(r.a, r)), ext) : rows;
  const d = Object.assign({ faz: 'Santa Rita', tal: 'T1', prof: '0–20', coleta: '2026-09-22', lab: 'Agrolab', ext, arq: '', area: 312, an }, extra || {});
  return MUD(c, x => soloRegistrar(x, d, chave, 'Ana')); }
function lau(c, id) { return soloLaudos(c, SOLO0).find(l => l.id === id); }
/* C1 · 15 analitos com um 0 (Al), um vazio (Zn), LD = 0 numérico (Cu), vírgula e unidades trocadas */
{ const c = NOVO(); const rows = [ {a:'pH',v:'5,4',un:'CaCl₂'}, {a:'P',v:'14',un:'mg/dm³'}, {a:'MO',v:'28',un:'g/dm³'}, {a:'Ca',v:'39',un:'mmolc/dm³'}, {a:'Mg',v:'1,40',un:'cmolc/dm³'},
    {a:'K',v:'0,08',un:'cmolc/dm³'}, {a:'H+Al',v:'3,82',un:'cmolc/dm³'}, {a:'Al',v:0,un:'cmolc/dm³',ld:'0,1'}, {a:'S',v:'9',un:'mg/dm³'}, {a:'B',v:'0,32',un:'mg/dm³'},
    {a:'Cu',v:'1,1',un:'mg/dm³',ld:0}, {a:'Fe',v:'38',un:'mg/dm³'}, {a:'Mn',v:'6,5',un:'mg/dm³'}, {a:'Zn',v:'',un:'mg/dm³',met:'Mehlich-1',ld:'0,1'}, {a:'Argila',v:'380',un:'g/kg'} ];
  const r = reg(c, rows, 'Mehlich-1', null, 'R95-C1'); const l = r.id ? lau(c, r.id) : null;
  OUT.C1 = { res: r.erro || r.id, sit: l && l.sit, n: l && l.an.length, nomes: l && l.an.map(x => x.a).join(','),
    Al: l && l.an.find(x => x.a === 'Al'), Zn: l && l.an.find(x => x.a === 'Zn') || null, Cu: l && l.an.find(x => x.a === 'Cu'), P: l && l.an.find(x => x.a === 'P'), K: l && l.an.find(x => x.a === 'K'), MO: l && l.an.find(x => x.a === 'MO'),
    idx: l && ['SB','T','t','V','m'].map(k => l.idx[k].v === null ? 'nc:' + l.idx[k].nc : prFmt(l.idx[k].v, 2)) };
  const r2 = reg(c, rows, 'Mehlich-1', null, 'R95-C1b'); OUT.C1dup = r2.erro || r2.id; }
/* C2 · qualificador: '<' (vocabulário do domínio) contra o texto que o placeholder sugere ("abaixo do limite") */
{ const k = (q) => soloKmg({ a: 'K', v: '1', un: 'mg/dm³', q }); const al = (q) => soloCmolc({ a: 'Al', v: '0.1', un: 'cmolc/dm³', q });
  OUT.C2 = { K_lt: k('<'), K_txt: k('abaixo do limite'), K_ltLD: k('< LD'), Al_lt: al('<'), Al_txt: al('abaixo do limite') };
  /* fluxo completo no T1: laudo novo validado com K "< 1" escrito como o placeholder sugere → sugestão de K₂O */
  const base = (lau0) => lau0.an.filter(x => x.a !== 'K').map(x => ({ a: x.a, v: x.v, un: x.un, met: x.met, ld: x.ld, q: x.q }));
  const L61 = SOLO0.laudos.find(l => l.id === 'LAU-2061');
  ['<', 'abaixo do limite'].forEach((q, i) => { const c = NOVO(); const rows = base(L61).concat([{ a: 'K', v: '1', un: 'mg/dm³', ld: '1', q }]);
    const r = reg(c, rows, 'Mehlich-1', null, 'R95-C2-' + i); const v = MUD(c, x => soloValidar(x, r.id, 'R95-V2-' + i, 'Ana'));
    const s = cT1 ? SG(c, cT1.id) : { sug: [], info: [] }; const kk = s.sug.filter(x => x.regra === 'potássio');
    const L = lau(c, r.id);
    OUT['C2_fluxo_' + (i ? 'texto' : 'lt')] = { reg: r.erro || r.id, val: v.erro || v.msg, qGravado: L.an.find(x => x.a === 'K').q,
      k: kk.map(x => x.tipo + ' ' + x.prod + ' ' + x.padrao + '→' + x.sug + ' | ' + (x.ent || [])[0]), info: s.info.filter(t => /K /.test(t)) }; }); }
/* C3 · método de K diferente do extrator do laudo (o PR deixa o informado prevalecer) */
{ const L61 = SOLO0.laudos.find(l => l.id === 'LAU-2061');
  const rows = L61.an.map(x => x.a === 'K' ? { a: 'K', v: '58.65', un: 'mg/dm³', met: 'Resina', ld: '1' } : { a: x.a, v: x.v, un: x.un, met: x.met, ld: x.ld });
  const c = NOVO(); const r = reg(c, rows, 'Mehlich-1', null, 'R95-C3'); MUD(c, x => soloValidar(x, r.id, 'R95-V3', 'Ana'));
  const L = lau(c, r.id); const s = cT1 ? SG(c, cT1.id) : { sug: [] };
  OUT.C3 = { ext: L.ext, Kmet: L.an.find(x => x.a === 'K').met, k: s.sug.filter(x => x.regra === 'potássio').map(x => x.sug + ' | ' + (x.ent || [])[0]) };
  /* exemplo carregado (K met Mehlich-1) e extrator trocado para Resina depois */
  if (HAS) { const ex = SOLO0.exemplo; const rr = SO_AN.map(a => soRlAnalito(a, ex.an.find(z => z.a === a))); OUT.C3ex = soRlEnviarAnalitos(rr, 'Resina').filter(x => x.a === 'K' || x.a === 'P'); } }
/* C4 · interpretação (soloIndVal) ignora a unidade/meio: pH em água e Ca em mmolc (este anterior ao PR) */
{ const ind = k => SOLO0.ind.find(i => i.k === k); const lf = { an: [{ a: 'pH', v: '5.8', un: 'H₂O' }, { a: 'Ca', v: '39', un: 'mmolc/dm³' }, { a: 'MO', v: '2.8', un: '%' }] };
  OUT.C4 = { pH_H2O: soloIndVal(lf, ind('pH')), Ca_mmolc: soloIndVal(lf, ind('Ca')), pHcortes: ind('pH').cortes }; }
/* C5 · vazio só com metadados (Al "< 0,1" digitado só no qualificador e no LD) e valor negativo */
if (HAS) { OUT.C5 = { soMeta: soRlEnviarAnalitos([soRlAnalito('Al', { v: '', un: 'cmolc/dm³', ld: '0,1', q: '<' })], 'Mehlich-1'),
  neg: (() => { const c = NOVO(); const L61 = SOLO0.laudos.find(l => l.id === 'LAU-2061'); const rows = L61.an.map(x => x.a === 'Ca' ? { a: 'Ca', v: '-3,1', un: 'cmolc/dm³' } : { a: x.a, v: x.v, un: x.un });
    const r = reg(c, rows, 'Mehlich-1', { tal: 'T3', area: 96 }, 'R95-C5'); return r.erro || (r.id + ' Ca ' + lau(c, r.id).an.find(x => x.a === 'Ca').v); })() }; }
/* C6 · analito fora da lista (Na entra no SB do domínio) */
if (HAS) { OUT.C6 = { naNaLista: SO_AN.indexOf('Na') >= 0, dominioUsaNa: /Na/.test(String(soloIdx)) }; }
console.log(JSON.stringify(OUT, null, 1));
"""
js = 'globalThis.print=(...a)=>console.log(...a);\n' + cenario.perfis_js() + cenario.js_prefixo() + dados_solo.js_prefixo() + helpers + '\n' + PROBE
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); fn = f.name
r = subprocess.run(['node', fn], capture_output=True, text=True); os.unlink(fn)
print(r.stdout); print(r.stderr[-1500:]); sys.exit(r.returncode)
