"""EX-55 F1 · mapa embutido nas telas: um desenho SVG por fazenda, um <g> por talhão, da mesma geometria do IN-04 (geo_talhoes.mapa()).
Cor, rótulo, dica, ação e teclado são ligados em JS (mapa_emb.js · meVals); a classificação vem do adaptador de cada tela, com as funções
do Mapa (mapa_camadas.js). O prefixo separa as telas (ex.: 'om' na O.S.). O Tab segue a ordem de leitura do desenho (de cima para baixo e
da esquerda para a direita), porque a ordem do DOM do SVG é fixa no build."""
import json
from engine import esc
import geo_talhoes as GT

H = lambda s: '{{' + s + '}}'
F = lambda: H('false')


def dados():
    geo = GT.mapa(); idx = []; fk = {}
    for fi, (faz, g) in enumerate(geo.items()):
        fk[faz] = 'f%d' % fi
        ts = sorted(g['t'], key=lambda t: (round(g['t'][t]['ly'] / max(1.0, g['vb'][3] / 12)), g['t'][t]['lx']))   # ordem de leitura
        vb = g['vb']
        for t in ts:
            T = g['t'][t]; fs = max(12.0, min(24.0, T['w'] / 5.5))
            idx.append(dict(i=len(idx), faz=faz, t=t, px=round((T['lx'] - vb[0]) / vb[2] * 100, 2), py=round((T['ly'] + fs * 0.25 - vb[1]) / vb[3] * 100, 2),
                            pw=round(T['w'] / vb[2] * 100, 2)))   # largura do talhão: a 2ª linha não passa da borda
    return geo, idx, fk


def js(pref):
    geo, idx, fk = dados()
    me = dict(geo={f: dict(vb=g['vb'], esq=not g.get('proj')) for f, g in geo.items()}, idx=idx, fk=fk)
    return 'const ME_%s = %s;\n' % (pref.upper(), json.dumps(me, ensure_ascii=False))


CSS = ('<style>.me-wrap{display:flex;flex-direction:column;gap:8px;min-width:0}.me-barra{display:flex;flex-wrap:wrap;gap:8px;align-items:center}'
       '.me-grp{display:flex;flex-wrap:wrap;gap:6px;align-items:center}.me-rot{font-size:12px;color:#5b6b60}'
       '.me-bt{min-height:36px;padding:0 12px;border-radius:999px;font:inherit;font-size:12.5px;font-weight:700;cursor:pointer;border:1px solid #E4E9E5;background:#fff;color:#15201A}'
       '.me-bt[aria-pressed=true]{border-color:#1E7A4C;background:#E4F3E9;color:#1E7A4C}.me-bt:hover{border-color:#1E7A4C}'
       '.me-cont{font-size:12.5px;color:#15201A}.me-lk{font-size:12.5px;color:#1E7A4C;font-weight:700;text-decoration:none}.me-lk:hover{text-decoration:underline}'
       '.me-box{position:relative;width:100%;margin:0 auto}.me-svg{display:block;width:100%;height:100%;background:#f3f6f3;border-radius:10px}'
       '.me-l2{position:absolute;transform:translate(-50%,0);max-width:24%;font-size:12px;line-height:1.25;font-weight:600;text-align:center;pointer-events:none;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}'
       '.me-t{cursor:pointer;outline:none}.me-t:focus-visible path:first-of-type{stroke:#1E7A4C;stroke-width:4}.me-t:hover path:first-of-type{stroke:#1E7A4C}'
       '.me-leg{display:flex;flex-wrap:wrap;gap:6px 12px}.me-li{display:inline-flex;align-items:center;gap:6px;font-size:12.5px}'
       '.me-esq{margin:0;font-size:12px;color:#8A5A00}.me-sem{display:flex;flex-wrap:wrap;gap:6px;align-items:center}'
       '.me-curta{display:flex;flex-direction:column;gap:6px;padding:10px 12px;border:1px solid #dce4dd;border-radius:10px;background:#fff}'
       '.me-curta button{min-height:44px;text-align:left}.me-x{align-self:flex-end}'
       '.me-rec{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center;font-size:12.5px}'
       '.me-chip{display:inline-flex;align-items:center;gap:2px;padding:2px 4px 2px 10px;border-radius:999px;background:#E4F3E9;color:#1E7A4C;font-size:12px;font-weight:700}'
       '.me-chip button{width:28px;height:28px;border:0;background:transparent;color:inherit;cursor:pointer;font-size:14px;border-radius:999px}'
       '@media (pointer:coarse){.me-chip button,.me-rec .me-bt{min-width:44px;min-height:44px}}</style>')


def html(pref, rotulo):
    """rotulo: aria-label do grupo (o que o clique faz). Ligações: {pref}_f_{fk}, {pref}t{i}_*, {pref}_vers, {pref}_fazs, {pref}_cont,
    {pref}_in04, {pref}_esq, {pref}_leg, {pref}_temRec/_rec/_recLimpar, {pref}_temCurta/_curtaT/_curta/_curtaX, {pref}_temSem/_sem."""
    geo, idx, fk = dados(); svgs = ''
    for faz, g in geo.items():
        els = ''; hid = '%s-hach-%s' % (pref, fk[faz])
        for x in idx:
            if x['faz'] != faz:
                continue
            T = g['t'][x['t']]; P = '%st%d' % (pref, x['i']); fs = max(12.0, min(24.0, T['w'] / 5.5))
            els += (f'<g class="me-t" role="button" tabindex="{H(P + "_tab")}" data-t="{esc(x["t"])}" data-c="{H(P + "_c")}" aria-label="{H(P + "_al")}" onClick="{H(P + "_go")}" onKeyDown="{H(P + "_key")}">'
                    f'<title>{H(P + "_al")}</title>'
                    f'<path d="{T["d"]}" fill="{H(P + "_fill")}" stroke="{H(P + "_stk")}" stroke-width="{H(P + "_sw")}" stroke-dasharray="{H(P + "_dash")}" vector-effect="non-scaling-stroke"></path>'
                    f'<path d="{T["d"]}" fill="url(#{hid})" opacity="{H(P + "_hach")}" pointer-events="none"></path>'
                    f'<text x="{T["lx"]}" y="{T["ly"] - fs * 0.25:.1f}" text-anchor="middle" font-size="{fs:.0f}" font-weight="800" fill="{H(P + "_tc")}" stroke="{H(P + "_th")}" stroke-width="3" paint-order="stroke" pointer-events="none">{esc(x["t"])}</text>'
                    '</g>')
        vb = ' '.join(str(n) for n in g['vb']); u = g['vb'][2] / 60
        defs = (f'<defs><pattern id="{hid}" patternUnits="userSpaceOnUse" width="{u:.1f}" height="{u:.1f}" patternTransform="rotate(45)">'
                f'<line x1="0" y1="0" x2="0" y2="{u:.1f}" stroke="#8A968E" stroke-width="{u * 0.18:.2f}"></line></pattern></defs>')
        W, Hh = g['vb'][2], g['vb'][3]
        svgs += (f'<sc-if value="{H(pref + "_f_" + fk[faz])}" hint-placeholder-val="{F()}"><div class="me-box" style="aspect-ratio: {W:.0f} / {Hh:.0f}; max-width: min(100%, calc(62vh * {W / Hh:.4f}));">'
                 f'<svg class="me-svg" viewBox="{vb}" preserveAspectRatio="xMidYMid meet" role="group" aria-label="{esc(rotulo)} · {esc(faz)}">{defs}{els}</svg>'
                 f'<sc-for list="{H(pref + "_lbl_" + fk[faz])}" as="q" hint-placeholder-count="0"><span class="me-l2" aria-hidden="true" data-t="{H("q.k")}" style="{H("q.st")}">{H("q.t")}</span></sc-for></div></sc-if>')
    barra = (f'<div class="me-barra"><div role="group" aria-label="Mostrar no mapa" class="me-grp"><span class="me-rot">Mostrar</span>'
             f'<sc-for list="{H(pref + "_vers")}" as="m" hint-placeholder-count="4"><button type="button" class="me-bt" aria-pressed="{H("m.on")}" onClick="{H("m.go")}">{H("m.t")}</button></sc-for></div>'
             f'<sc-if value="{H(pref + "_temFazs")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Fazenda no mapa" class="me-grp"><span class="me-rot">Fazenda</span>'
             f'<sc-for list="{H(pref + "_fazs")}" as="z" hint-placeholder-count="2"><button type="button" class="me-bt" aria-pressed="{H("z.on")}" onClick="{H("z.go")}">{H("z.t")}</button></sc-for></div></sc-if>'
             f'<span role="status" class="me-cont">{H(pref + "_cont")}</span>'
             f'<a class="me-lk" href="{H(pref + "_in04")}">Abrir no Mapa da fazenda ›</a></div>')
    # recorte da grade da tela (busca, filtro rápido e filtros de coluna) que o mapa também aplica: chips removíveis, para a busca da Tabela
    # não ficar escondida na visão Mapa (VISOES-2 §8); a O.S. usa a faixa de recorte dela (kb_nota) e não liga estes valores
    rec = (f'<sc-if value="{H(pref + "_temRec")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Recorte desta visão" data-me-recorte="1" class="me-rec">'
           f'<span class="me-rot">Recorte da tabela</span><sc-for list="{H(pref + "_rec")}" as="rc" hint-placeholder-count="1"><span class="me-chip">{H("rc.t")}'
           f'<button type="button" aria-label="{H("rc.lab")}" title="{H("rc.lab")}" onClick="{H("rc.rm")}">×</button></span></sc-for>'
           f'<button type="button" class="me-bt" onClick="{H(pref + "_recLimpar")}">Limpar filtros</button></div></sc-if>')
    esq = f'<sc-if value="{H(pref + "_esq")}" hint-placeholder-val="{F()}"><p class="me-esq">Posição esquemática: o desenho desta fazenda não tem escala.</p></sc-if>'
    leg = (f'<div class="me-leg" role="list" aria-label="Legenda do mapa"><sc-for list="{H(pref + "_leg")}" as="g" hint-placeholder-count="4">'
           f'<span role="listitem" class="me-li"><i style="{H("g.st")}"></i>{H("g.t")} <b>{H("g.n")}</b></span></sc-for></div>')
    curta = (f'<sc-if value="{H(pref + "_temCurta")}" hint-placeholder-val="{F()}"><div class="me-curta" role="group" aria-label="{H(pref + "_curtaT")}">'
             f'<b>{H(pref + "_curtaT")}</b><sc-for list="{H(pref + "_curta")}" as="o" hint-placeholder-count="2"><button type="button" class="me-bt" onClick="{H("o.go")}">{H("o.t")}</button></sc-for>'
             f'<button type="button" class="me-bt me-x" aria-label="Fechar a lista do talhão" onClick="{H(pref + "_curtaX")}">Fechar</button></div></sc-if>')
    sem = (f'<sc-if value="{H(pref + "_temSem")}" hint-placeholder-val="{F()}"><div class="me-sem"><span class="me-rot">Sem contorno no mapa</span>'
           f'<sc-for list="{H(pref + "_sem")}" as="s" hint-placeholder-count="1"><button type="button" class="me-bt" onClick="{H("s.go")}">{H("s.t")}</button></sc-for></div></sc-if>')
    return CSS + f'<div class="me-wrap" data-mapa-emb="{esc(pref)}">{barra}{rec}{esq}{svgs}{leg}{curta}{sem}</div>'
