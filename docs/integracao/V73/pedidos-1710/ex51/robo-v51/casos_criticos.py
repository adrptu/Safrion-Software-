# -*- coding: utf-8 -*-
"""Casos dirigidos dos percursos críticos do EX-51 com o oráculo do robô v5.1 (revisor Claude).

A amostra do robô (até 3 registros e 9 passagens por tela) não garante cobrir os percursos críticos do contrato
(PR #47, 6241229682 item 4). Este script percorre TODOS os registros das telas de origem, lista as passagens de cada
detalhe e da tela com o passEls() do robô e roda, para as que pertencem a um percurso crítico, a mesma passage() do
robô v5.1 (alvo capturado na origem, chegada por título/seleção, Voltar). Nada do oráculo é reescrito aqui.

Única adição no robô, em tempo de execução: load() aceita um hash de visão por tela (window.__HASH), para abrir a
Manutenção na visão de ordens (MA#vis=ordens). O hash vai depois do ?r= de load(), como o endereço real.

Uso: python3 -I casos_criticos.py --rodar <robo-v51/rodar.py> --trabalho <trabalho já preparado> --saida <arquivo.json>
"""
import argparse, importlib.util, json, os, re, sys, time

ap = argparse.ArgumentParser()
ap.add_argument('--rodar', required=True)
ap.add_argument('--trabalho', required=True)
ap.add_argument('--saida', required=True)
ap.add_argument('--chrome', default=None)
ap.add_argument('--max-linhas', type=int, default=1000)
ap.add_argument('--max-por-grupo', type=int, default=1000)
ap.add_argument('--por-endereco', action='store_true', help='origens abertas pelo endereço do registro (painel aberto pelo hash)')
a = ap.parse_args()

spec = importlib.util.spec_from_file_location('rodar51', a.rodar)
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

trab = os.path.abspath(a.trabalho)
robo = os.path.join(trab, 'robo-v5-isolado.html')
assert os.path.exists(robo), 'rode antes a fase robo do v5.1 (gera robo-v5-isolado.html)'

ORIGENS = [('OS', ''), ('IN-02', ''), ('MA', '#vis=ordens'), ('AG-01', ''), ('AG-01det', ''), ('AG-04', ''), ('AG-04det', '')]
if a.por_endereco:
    ORIGENS = [('OS', '#OS-0504'), ('OS', '#OS-0508'), ('OS', '#OS-0420'), ('OS', '#OS-0431'), ('OS', '#OS-0507'), ('MA', '#om=OM-0233'), ('MA', '#om=OM-0228'), ('MA', '#om=OM-0219')]
RECEIT = {'AG-01', 'AG-01det', 'AG-04', 'AG-04det'}

SETUP = r"""(() => {
  if (window.__fr) return 1;
  localStorage.setItem('safrion.perfilDemo', 'Proprietário'); BASE_LS = {};
  for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); BASE_LS[k] = localStorage.getItem(k); }
  load = async function (fr, url) {   // igual ao load() do robô, com o hash de visão opcional por tela
    restoreLS(); try { fr.contentWindow && fr.contentWindow.sessionStorage.clear(); } catch (e) {}
    const hv = (window.__HASH || {})[scr(url).split('/').pop()] || '';
    const u = url + (url.includes('?') ? '&' : '?') + 'r=' + (++LOADN) + hv;
    await new Promise(res => { let done = false; const fin = () => { if (!done) { done = true; res(); } };
      fr.onload = () => { try { if (fr.contentWindow.location.href !== 'about:blank') fin(); } catch (e) { fin(); } }; fr.src = u; setTimeout(fin, 20000); });
    await settle(fr);
  };
  window.__openRowOrig = openRow;
  openRow = async function (fr, idx) { if (!window.__ROWHASH) return window.__openRowOrig(fr, idx);
    await sleep(650); const d = topDlg(fr.contentDocument); if (!d) return { row: null, d: null }; await expandAll(fr.contentDocument, d); return { row: null, d: topDlg(fr.contentDocument) }; };
  const f = document.createElement('iframe'); document.getElementById('frames').appendChild(f); window.__fr = f; return 1; })()"""

ENUM = r"""(async (tela, hv, maxl) => {
  window.__HASH = {}; window.__HASH[tela] = hv; window.__ROWHASH = POR_END; const fr = window.__fr, url = '/v3/' + tela + '.dc.html';
  await load(fr, url); const doc0 = fr.contentDocument; const n = rowsAll(doc0).length;
  const land = passEls(doc0, doc0.body, false); const det = [];
  for (let i = 0; i < (POR_END ? 1 : Math.min(n, maxl)); i++) { await load(fr, url); const o = await openRow(fr, i);
    if (!o || !o.d) { det.push({ linha: i, titulo: null, sigs: [] }); continue; }
    const doc = fr.contentDocument; const tx = o.d.innerText || '';
    det.push({ linha: i, titulo: dTitle(doc, o.d), impedida: /impedid/i.test(tx), sigs: passEls(doc, o.d, true) }); }
  return { tela, hv, landed: cur(fr), linhas: n, land, det }; })"""

PASS = r"""(async (tela, hv, row, sig) => { window.__HASH = {}; window.__HASH[tela] = hv; window.__ROWHASH = POR_END;
  try { return await passage(window.__fr, { n: tela }, { row }, sig); } catch (e) { return { r: 'erro', e: String(e) }; } })"""


def destino(sig):
    return (sig.get('h') or '').split('#')[0].split('?')[0].replace('.dc.html', '')


def classe(org, sig, det):
    t, h = sig['t'], sig.get('h') or ''
    d = destino(sig)
    th = t + ' ' + h
    if org == 'OS':
        if d == 'EST' or re.search(r'estoque', t, re.I):
            sub = 'entregar' if re.search(r'entreg', t, re.I) else 'devolver' if re.search(r'devol', t, re.I) else 'saldo' if re.search(r'saldo', t, re.I) else 'outro'
            return 'OS→EST', sub
        if d in RECEIT or re.search(r'\b(VIS|RA|REC)-\d', th):
            return 'OS→receituário', d or 'botão'
        if d == 'MA' or re.search(r'\bOM-\d', th):
            return 'OS impedida→OM' if (det or {}).get('impedida') else 'OS→OM', d or 'botão'
    if org in RECEIT and (d == 'OS' or re.search(r'\bOS-\d', th)):
        return 'receituário→OS', org
    if org == 'IN-02' and (d == 'OS' or re.search(r'\bOS-\d', th)):
        return 'Aprovações→OS', ''
    if org == 'MA' and d == 'OS':
        return 'OM→OS', ''
    return None, None


R.esperar_vaga()
srvs = R.Servidores()
c = None
out = {'quando': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'origens': [], 'casos': []}
t0 = time.time()
try:
    c = R.Chrome(a.chrome or R.CHROME)
    base = srvs.subir(trab, robo, os.path.join(trab, 'robot3', 'screens.json'), os.path.join(trab, 'saida-criticos'))
    aba = c.abas[0]
    R.limpar_origem(aba, base)
    if not aba.goto(base + '/anexo-robo-v5.html', espera_corpo=False):
        raise RuntimeError('robô não carregou')
    aba.js(SETUP)
    ENUM_ = ENUM.replace('POR_END', 'true' if a.por_endereco else 'false'); PASS_ = PASS.replace('POR_END', 'true' if a.por_endereco else 'false')
    grupos = {}
    for tela, hv in ORIGENS:
        e = aba.js(f'({ENUM_})({json.dumps(tela)}, {json.dumps(hv)}, {a.max_linhas})', timeout=900)
        out['origens'].append(e)
        R.log(f'{tela}{hv}: {e["linhas"]} linhas, {sum(len(x["sigs"]) for x in e["det"])} passagens em detalhes, {len(e["land"])} na tela')
        cands = ([] if a.por_endereco else [(None, s, None) for s in e['land']]) + [(x['linha'], s, x) for x in e['det'] for s in x['sigs']]
        for row, sig, det in cands:
            cl, sub = classe(tela, sig, det)
            if not cl:
                continue
            k = (cl, sub)
            lst = grupos.setdefault(k, [])
            chave = (tela + hv, row, sig['k'], sig['t'], sig.get('h'))
            if any(x[:5] == chave for x in lst):
                continue
            lst.append(chave + (hv, (det or {}).get('titulo'), (det or {}).get('impedida')))
    for (cl, sub), lst in sorted(grupos.items()):
        for tela, row, k, t, h, hv, tit, imp in lst[:a.max_por_grupo]:
            tela = tela[:len(tela) - len(hv)] if hv and tela.endswith(hv) else tela
            sig = {'k': k, 't': t, 'h': h or ''}
            r = aba.js(f'({PASS_})({json.dumps(tela)}, {json.dumps(hv)}, {json.dumps(row)}, {json.dumps(sig)})', timeout=120)
            c.fechar_extras()
            caso = {'percurso': cl, 'sub': sub, 'tela': tela, 'visao': hv, 'linha': row, 'detalhe': tit, 'impedida': imp, 'el': sig, 'res': r}
            out['casos'].append(caso)
            R.log(f"{cl}/{sub} {tela}[{row}] {t[:40]!r} → r={r.get('r')} alvo={r.get('alvo')!r} abriu={r.get('abriu')} destacou={r.get('destacou')}")
        out.setdefault('naoRodados', []).extend([{'percurso': cl, 'sub': sub, 'tela': x[0], 'linha': x[1], 't': x[3], 'h': x[4]} for x in lst[a.max_por_grupo:]])
finally:
    if c:
        c.close()
        R.log(f'Chrome PID {c.p.pid} encerrado')
    srvs.parar()
out['min'] = round((time.time() - t0) / 60, 1)
json.dump(out, open(a.saida, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
R.log(f'casos críticos: {len(out["casos"])} em {out["min"]} min → {a.saida}')

