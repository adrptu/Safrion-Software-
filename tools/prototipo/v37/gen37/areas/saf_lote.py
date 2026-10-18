# -*- coding: utf-8 -*-
"""EDL-01 · Editar talhões da fazenda (Planejar safra › Cultivos e planos), pedido do proprietário de 16/10/2026: "coloque um botao para
poder editar de uma vez todos talhoes de uma fazenda numa tela só. como no outro anexo. todos inputs do usuário no sistema devem ser mais
rápido e fácil." Painel largo, do mesmo desenho do "Dividir": uma linha por talhão (parcelas recuadas), colunas do Dividir e a Situação.
Os valores e as regras vêm de safra_lote.js (slVals, slGravar); este módulo só monta o HTML. Sem tabela própria (role=table): é uma grade
de edição, sem ordenar nem filtrar, como o Dividir; sem CSS sobre classe do motor (.g2…)."""
from engine import INK, MUTED, LINE, BG, SURF, RED, REDS, YEL, YELS, DISP, BTN_ST, _MINI, _MINIP
H = lambda s: '{{' + s + '}}'
F = lambda: H('false')
# desktop: seleção | talhão ou parcela | área | cultura | variedade | plantio | meta | unidade | plano | situação
COLS = '44px minmax(118px,1fr) 88px 128px minmax(112px,1fr) 142px 78px 72px minmax(160px,1.3fr) 156px'
ROTS = ['', 'Talhão ou parcela', 'Área (ha)', 'Cultura', 'Variedade', 'Plantio', 'Meta', 'Unidade', 'Plano agronômico', 'Situação']
CSS = ('<style>'
       f'.sl-gx{{min-width:1110px}}'
       f'.sl-l{{display:grid;grid-template-columns:{COLS};gap:6px 8px;align-items:center;padding:6px 0;border-top:1px solid {LINE}}}'
       f'.sl-cab{{font-size:10.5px;font-weight:700;letter-spacing:.03em;text-transform:uppercase;color:{MUTED};border-top:0;padding:0 0 4px}}'
       f'.sl-ap{{background:{BG};border:1px solid {LINE};border-radius:10px;padding:8px 0;margin-bottom:4px}}'
       '.sl-s{display:flex;align-items:center;justify-content:center;min-height:32px;cursor:pointer}'
       '.sl-s input{width:18px;height:18px;margin:0;accent-color:#1E7A4C;cursor:pointer}'
       '.sl-id{display:flex;flex-direction:column;min-width:0;font-size:13px}'
       f'.sl-sub{{font-size:11.5px;color:{MUTED};white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}'
       '.sl-c{display:flex;flex-direction:column;gap:2px;min-width:0;margin:0}'
       f'.sl-rot{{display:none;font-size:11px;font-weight:700;color:{MUTED}}}'
       f'.sl-un{{font-size:12.5px;color:{MUTED};white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}'
       '.sl-sit{display:flex;flex-wrap:wrap;align-items:center;gap:4px 8px;min-width:0}'
       '.sl-lk{border:0;background:transparent;padding:0;color:#1E7A4C;font-weight:700;cursor:pointer;font-family:inherit;font-size:12.5px;text-decoration:underline;text-underline-offset:3px;white-space:nowrap}'
       '.sl-tit>.sl-id{grid-column:2/10}.sl-tit .sl-sub{white-space:normal}'
       f'.sl-err{{font-size:12px;color:{RED};font-weight:700;padding:0 0 6px 52px}}'
       f'.sl-pe{{position:sticky;bottom:0;background:{SURF};display:flex;justify-content:flex-end;align-items:center;gap:8px;flex-wrap:wrap;padding:10px 0 14px;border-top:1px solid {LINE};margin-top:auto;z-index:2}}'
       '.sl-pn :is(input,select,button){min-height:var(--g2-alvo,0px)}'
       '@media (pointer:coarse){#sl-abrir{min-height:44px!important}}'
       # celular: cada linha vira um bloco com os mesmos campos em duas colunas, rótulo em cima; alvo de 44 px; sem rolagem de lado
       '@media (max-width:760px){'
       '.sl-pn{padding:14px 12px 0!important}'
       '.sl-gx{min-width:0}.sl-cab{display:none}'
       f'.sl-l{{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px 10px;padding:10px 12px;border:1px solid {LINE};border-radius:12px;margin-top:8px}}'
       '.sl-l>.sl-s{grid-area:1/1/2/2;justify-self:start;z-index:1;min-width:44px;min-height:44px}'
       '.sl-l>.sl-id{grid-area:1/1/2/3;padding-left:48px!important;min-height:44px;justify-content:center}'
       '.sl-l>.sl-id.sl-sem{padding-left:0!important}'
       '.sl-rot{display:block}.sl-c-plano,.sl-sit,.sl-apb,.sl-apl{grid-column:1/-1}'
       '.sl-ap .sl-un,.sl-ap .sl-c-area{display:none}'
       '.sl-un{align-self:end;padding-bottom:12px}'
       '.sl-l :is(input:not([type=checkbox]),select){min-height:44px;font-size:15px!important}'
       '.sl-lk{min-height:44px;display:inline-flex;align-items:center}'
       '.sl-err{padding-left:4px}'
       '.sl-ap[data-vazio="true"] :is(.sl-c,.sl-un,.sl-apb){display:none}'   # celular: os campos da faixa aparecem quando há linha marcada
       '.sl-pe button{min-height:44px;flex:1 1 0}'
       '}'
       '</style>')


def cel_txt(c, extra='', tipo='text'):
    """Célula de texto/número/data de uma linha (l.*): mesma peça nas linhas e no celular (rótulo só no estreito)."""
    im = ' inputMode="decimal"' if c in ('area', 'meta') else ''
    ls = f' list="{H("l.dl")}"' if c == 'var' else ''
    return (f'<label class="sl-c sl-c-{c}"><span class="sl-rot">{dict(area="Área (ha)", var="Variedade", plantio="Plantio", meta="Meta")[c]}</span>'
            f'<input type="{tipo}" data-l="{H("l.k")}" data-c="{c}"{im}{ls} autoComplete="off" spellCheck="false" aria-label="{H("l.al_" + c)}" title="{H("l.tt_" + c)}"'
            f' value="{H("l." + c)}" onChange="{H("l.s_" + c)}" readOnly="{H("l.ro_" + c)}" style="{H("l.st_" + c)}{extra}"></label>')


def cel_sel(c, lista, rot):
    return (f'<label class="sl-c sl-c-{c}"><span class="sl-rot">{rot}</span><select data-l="{H("l.k")}" data-c="{c}" aria-label="{H("l.al_" + c)}" title="{H("l.tt_" + c)}"'
            f' value="{H("l." + c)}" onChange="{H("l.s_" + c)}" disabled="{H("l.ro_" + c)}" style="{H("l.st_" + c)}">'
            f'<sc-for list="{H("l." + lista)}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label>')


SIT = (f'<span class="sl-sit"><span title="{H("l.sitDica")}" style="{H("l.sitSt")}">{H("l.sit")}</span>'
       f'<sc-if value="{H("l.temOs")}" hint-placeholder-val="{F()}"><button type="button" class="sl-lk" aria-label="{H("l.osAl")}" onClick="{H("l.osGo")}">{H("l.osT")}</button></sc-if>'
       f'<sc-if value="{H("l.temAc")}" hint-placeholder-val="{F()}"><button type="button" class="sl-lk" aria-label="{H("l.acAl")}" onClick="{H("l.acGo")}">{H("l.acT")}</button></sc-if></span>')
LINHA_ED = (f'<div class="sl-l" data-k="{H("l.k")}" style="{H("l.lnSt")}">'
            f'<label class="sl-s"><input type="checkbox" aria-label="{H("l.selAl")}" checked="{H("l.sel")}" onChange="{H("l.tog")}"></label>'
            f'<span class="sl-id" style="{H("l.lst")}"><b>{H("l.rot")}</b><span class="sl-sub">{H("l.sub")}</span></span>'
            + cel_txt('area') + cel_sel('cult', 'oc', 'Cultura') + cel_txt('var') + cel_txt('plantio', tipo='date') + cel_txt('meta')
            + f'<span class="sl-un" data-un="meta" title="Unidade da meta: a do seletor da tabela; o Padrão da cultura vem do CD-02">{H("l.unm")}</span>'
            + cel_sel('plano', 'op', 'Plano agronômico') + SIT + '</div>'
            f'<sc-if value="{H("l.hasErr")}" hint-placeholder-val="{F()}"><div role="alert" class="sl-err">{H("l.errMsg")}</div></sc-if>')
LINHA_TIT = (f'<div class="sl-l sl-tit"><span class="sl-s" aria-hidden="true"></span><span class="sl-id sl-sem" style="{H("l.lst")}"><b>{H("l.rot")}</b>'
             f'<span class="sl-sub">{H("l.sub")}{H("l.motivoSep")}{H("l.motivo")}</span></span>{SIT}</div>')


def mapa_dados():
    """SAF-MAPA: geometria (geo_talhoes, a mesma do IN-04) e índice dos talhões desenhados: um <g> fixo por talhão com contorno"""
    import geo_talhoes as GT, ocupacao_cen as OCEN
    geo = GT.mapa(); tal = OCEN.talhoes(); idx = []
    for faz, g in geo.items():
        for t, _ha in tal.get(faz, []):
            if t in g['t']:
                T = g['t'][t]; vb = g['vb']; fs = max(12.0, min(24.0, T['w'] / 5.5))
                # posição da 2ª linha em % do desenho: ela vai numa camada HTML (o motor envolve texto ligado em <span>, que o SVG não desenha)
                idx.append(dict(i=len(idx), faz=faz, t=t, px=round((T['lx'] - vb[0]) / vb[2] * 100, 2), py=round((T['ly'] + fs * 0.3 - vb[1]) / vb[3] * 100, 2)))
    fk = {f: 'f%d' % i for i, f in enumerate(geo)}
    return geo, idx, fk


def mapa_js():
    import json
    geo, idx, fk = mapa_dados()
    return ('const SM_GEO=' + json.dumps({f: dict(vb=g['vb']) for f, g in geo.items()}, ensure_ascii=False) + ', SM_IDX=' + json.dumps(idx, ensure_ascii=False)
            + ', SM_FK=' + json.dumps(fk, ensure_ascii=False) + ';\n')


def _mapa_html():
    from engine import esc
    geo, idx, fk = mapa_dados()
    svgs = ''
    for faz, g in geo.items():
        els = ''
        for x in idx:
            if x['faz'] != faz:
                continue
            T = g['t'][x['t']]; P = 'smt%d' % x['i']; fs = max(12.0, min(24.0, T['w'] / 5.5))
            els += (f'<g class="sm-t" role="button" tabindex="0" data-t="{esc(x["t"])}" aria-pressed="{H(P + "_sel")}" aria-label="{H(P + "_al")}" onClick="{H(P + "_go")}" onKeyDown="{H(P + "_key")}">'
                    f'<title>{H(P + "_al")}</title>'
                    f'<path d="{T["d"]}" fill="{H(P + "_fill")}" stroke="{H(P + "_stk")}" stroke-width="{H(P + "_sw")}" stroke-dasharray="{H(P + "_dash")}" vector-effect="non-scaling-stroke"></path>'
                    f'<text x="{T["lx"]}" y="{T["ly"] - fs * 0.25:.1f}" text-anchor="middle" font-size="{fs:.0f}" font-weight="800" fill="{H(P + "_tc")}" stroke="{H(P + "_th")}" stroke-width="3" paint-order="stroke" pointer-events="none">{esc(x["t"])}</text>'
                    f'<circle cx="{T["lx"] + fs * 1.6:.1f}" cy="{T["ly"] - fs * 0.9:.1f}" r="{fs * 0.32:.1f}" fill="#8A5A00" opacity="{H(P + "_mud")}" pointer-events="none"></circle></g>')
        vb = ' '.join(str(n) for n in g['vb'])
        W, Hh = g['vb'][2], g['vb'][3]
        svgs += (f'<sc-if value="{H("sm_f_" + fk[faz])}" hint-placeholder-val="{F()}"><div class="sm-box" style="aspect-ratio: {W:.0f} / {Hh:.0f}; max-width: min(100%, calc(64vh * {W / Hh:.4f}));"><svg class="sm-svg" viewBox="{vb}" preserveAspectRatio="xMidYMid meet" role="group" '
                 f'aria-label="Talhões da {esc(faz)} no mapa: toque ou Enter marca o talhão">{els}</svg>'
                 f'<sc-for list="{H("sm_lbl_" + fk[faz])}" as="q" hint-placeholder-count="0"><span class="sm-l2" aria-hidden="true" data-t="{H("q.k")}" style="{H("q.st")}">{H("q.t")}</span></sc-for></div></sc-if>')
    sem = (f'<sc-if value="{H("sm_temSem")}" hint-placeholder-val="{F()}"><div class="sm-sem"><span class="sm-rot">Sem contorno no mapa</span>'
           f'<div style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H("sm_sem")}" as="s" hint-placeholder-count="1"><button type="button" aria-pressed="{H("s.on")}" aria-label="{H("s.al")}" onClick="{H("s.go")}" style="{H("s.st")}"><b>{H("s.t")}</b> · {H("s.sub")}</button></sc-for>'
           f'<a href="{H("sm_desenhar")}" class="sl-lk" style="align-self: center;">Desenhar no Mapa ›</a></div></div></sc-if>')
    leg = (f'<div class="sm-leg" role="list" aria-label="Legenda"><sc-for list="{H("sm_leg")}" as="g" hint-placeholder-count="3"><span role="listitem" class="sm-li"><i style="{H("g.st")}"></i>{H("g.t")} <b>{H("g.ha")}</b></span></sc-for></div>')
    barra = (f'<div class="sm-barra"><div role="group" aria-label="Colorir por" class="sm-grp"><span class="sm-rot">Colorir por</span>'
             f'<sc-for list="{H("sm_cores")}" as="c" hint-placeholder-count="4"><button type="button" class="sm-bt" aria-pressed="{H("c.on")}" onClick="{H("c.go")}" style="{H("c.st")}">{H("c.t")}</button></sc-for></div>'
             f'<div class="sm-grp" aria-label="Marcar" role="toolbar"><span class="sm-rot">Marcar</span><sc-for list="{H("sm_atalhos")}" as="a" hint-placeholder-count="4"><button type="button" class="sm-at" aria-label="{H("a.al")}" onClick="{H("a.go")}">{H("a.t")}</button></sc-for></div>'
             f'<span role="status" class="sm-cont">{H("sm_cont")}</span></div>')
    campo = lambda rot, html: f'<label class="sm-c"><span class="sm-rot">{rot}</span>{html}</label>'
    inp = f'font-family: inherit; font-size: 13px; padding: 8px 10px; min-height: 40px; border-radius: 8px; border: 1px solid {LINE}; background: {SURF}; width: 100%; box-sizing: border-box;'
    erro = (f'<sc-if value="{H("sm_temErr")}" hint-placeholder-val="{F()}"><div role="alert" class="sm-err"><b>A corrigir antes de salvar</b>'
            f'<sc-if value="{H("sm_temGerr")}" hint-placeholder-val="{F()}"><span>{H("sm_gerr")}</span></sc-if>'
            f'<sc-for list="{H("sm_err")}" as="e" hint-placeholder-count="1"><button type="button" class="sl-lk" aria-label="{H("e.al")}" onClick="{H("e.go")}" style="text-align: left;"><b>{H("e.t")}</b> · {H("e.msg")} ›</button></sc-for></div></sc-if>')
    painel_lat = (f'<aside class="sm-pn" aria-label="{H("sm_tit")}"><h3 style="margin: 0; font-size: 15px;">{H("sm_tit")}</h3>' + erro +
                  f'<sc-if value="{H("sm_vazio")}" hint-placeholder-val="true"><p style="margin: 0; font-size: 13px; color: {MUTED};">Toque nos talhões no mapa ou use Marcar. Esc limpa a seleção.</p></sc-if>'
                  f'<sc-if value="{H("sm_tem")}" hint-placeholder-val="{F()}"><div role="list" aria-label="Talhões marcados" style="display: flex; flex-wrap: wrap; gap: 6px;">'
                  f'<sc-for list="{H("sm_selL")}" as="s" hint-placeholder-count="2"><span role="listitem" class="sm-chip"><span><b>{H("s.t")}</b> · {H("s.sub")}</span>'
                  f'<button type="button" aria-label="{H("s.al")}" onClick="{H("s.go")}">×</button></span></sc-for></div></sc-if>'
                  + campo('Cultura', f'<select aria-label="Cultura para os talhões marcados" value="{H("sl_apCult")}" onChange="{H("sl_apSetCult")}" style="{inp}"><sc-for list="{H("sl_apCults")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>')
                  + campo('Variedade', f'<input aria-label="Variedade para os talhões marcados" list="{H("sl_apDl")}" autoComplete="off" spellCheck="false" placeholder="Variedade" value="{H("sl_apVar")}" onChange="{H("sl_apSetVar")}" style="{inp}">')
                  + campo('Plano agronômico', f'<select aria-label="Plano para os talhões marcados" value="{H("sl_apPlano")}" onChange="{H("sl_apSetPlano")}" style="{inp}"><sc-for list="{H("sl_apPlanos")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>')
                  + campo('Plantio', f'<input type="date" aria-label="Plantio para os talhões marcados" value="{H("sl_apPlantio")}" onChange="{H("sl_apSetPlantio")}" style="{inp}">')
                  + campo(f'Meta {H("sl_apUn")}', f'<input aria-label="Meta para os talhões marcados" inputMode="decimal" autoComplete="off" placeholder="Meta" value="{H("sl_apMeta")}" onChange="{H("sl_apSetMeta")}" style="{inp}">')
                  + f'<button type="button" id="sm-aplicar" onClick="{H("sm_aplicar")}" style="{BTN_ST(True, True)} {H("sm_apSt")} width: 100%;">{H("sm_apT")}</button>'
                  f'<p style="margin: 0; font-size: 12px; color: {MUTED};">Só os campos preenchidos mudam; os outros ficam como estão em cada talhão. Nada é salvo antes de "Salvar alterações".</p>'
                  f'<sc-if value="{H("sm_um")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 6px; border-top: 1px solid {LINE}; padding-top: 10px;">'
                  f'<span class="sm-rot">{H("sm_umT")}</span><sc-for list="{H("sm_acoes")}" as="a" hint-placeholder-count="2"><button type="button" class="sl-lk" aria-label="{H("a.al")}" onClick="{H("a.go")}" style="text-align: left; min-height: 36px;">{H("a.t")}</button></sc-for></div></sc-if>'
                  f'</aside>')
    return (f'<div class="sm-wrap"><div class="sm-esq">{barra}<div class="sm-tela">{svgs}'
            f'<sc-if value="{H("!sm_temGeo")}" hint-placeholder-val="{F()}"><p style="margin: 0; padding: 18px; font-size: 13px; color: {MUTED};">Esta fazenda ainda não tem contorno de talhões no mapa.</p></sc-if></div>'
            f'{leg}{sem}</div>{painel_lat}</div>')


MAPA_CSS = ('<style>'
            '.sm-wrap{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:14px;align-items:start;min-width:0}'
            '.sm-esq{display:flex;flex-direction:column;gap:10px;min-width:0}'
            f'.sm-tela{{background:#EEF3EC;border:1px solid {LINE};border-radius:12px;padding:8px;min-width:0}}'
            '.sm-box{position:relative;width:100%;margin:0 auto}.sm-svg{display:block;width:100%;height:100%}'
            '.sm-l2{position:absolute;transform:translate(-50%,0);max-width:24%;font-size:12px;line-height:1.25;font-weight:600;text-align:center;pointer-events:none;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}'
            '.sm-t{cursor:pointer;outline:none}.sm-t:focus-visible path{stroke:#15201A!important;stroke-width:5!important}'
            '@media (hover:hover){.sm-t:hover path{filter:brightness(.93)}}'
            '.sm-barra{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;min-width:0}'
            '.sm-grp{display:flex;flex-wrap:wrap;align-items:center;gap:6px}'
            f'.sm-rot{{font-size:11px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:{MUTED}}}'
            f'.sm-at{{min-height:36px;padding:0 12px;border-radius:999px;border:1px solid {LINE};background:#FFFFFF;font:inherit;font-size:12.5px;font-weight:700;cursor:pointer}}'
            '.sm-cont{font-size:13px;font-weight:700;margin-left:auto}'
            # alvo de toque: 36 px no mouse, 44 px no toque ou a 600 px ou menos (saf_lote_test H2)
            '.sm-bt{min-height:36px}@media (max-width:600px),(pointer:coarse){.sm-bt,.sm-at{min-height:44px}}'
            '.sm-err{display:flex;flex-direction:column;gap:6px;padding:10px 12px;border-radius:10px;background:#FDE8E6;border:1px solid #F3B8B1;color:#7A1C12;font-size:13px}'
            '.sm-leg{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12.5px}'
            '.sm-li{display:inline-flex;align-items:center;gap:6px}'
            f'.sm-sem{{display:flex;flex-direction:column;gap:6px;padding:10px;border:1px dashed {LINE};border-radius:12px}}'
            f'.sm-pn{{position:sticky;top:0;display:flex;flex-direction:column;gap:10px;padding:14px;border:1px solid {LINE};border-radius:14px;background:{SURF}}}'
            '.sm-c{display:flex;flex-direction:column;gap:4px;margin:0}'
            f'.sm-chip{{display:inline-flex;align-items:center;gap:4px;padding:2px 2px 2px 10px;border-radius:999px;background:{BG};font-size:12.5px}}'
            '.sm-chip button{border:0;background:transparent;width:36px;height:36px;border-radius:999px;cursor:pointer;font-size:16px}'
            '@media (max-width:760px){.sm-wrap{grid-template-columns:1fr}.sm-pn{position:static}.sm-cont{margin-left:0}}'
            '@media (pointer:coarse){.sm-at,.sm-chip button{min-height:44px;min-width:44px}}'
            '</style>')


def painel():
    lab = ''.join(f'<span>{x}</span>' for x in ROTS)
    ap = (f'<div class="sl-l sl-ap" role="group" aria-label="Aplicar aos marcados" data-vazio="{H("sl_apVazio")}">'
          f'<label class="sl-s"><input type="checkbox" aria-label="Marcar todas as linhas" checked="{H("sl_todas")}" onChange="{H("sl_togTodas")}"></label>'
          f'<span class="sl-id sl-apl"><b style="font-size: 12.5px;">Aplicar aos marcados</b><span class="sl-sub">{H("sl_apSub")}</span></span>'
          f'<span class="sl-c sl-c-area" style="font-size: 12px; color: {MUTED};">—</span>'
          f'<label class="sl-c"><span class="sl-rot">Cultura</span><select aria-label="Cultura para os marcados" value="{H("sl_apCult")}" onChange="{H("sl_apSetCult")}" style="font-family: inherit; font-size: 13px; padding: 6px 8px; border-radius: 8px; border: 1px solid {LINE}; background: {SURF}; width: 100%; min-width: 0;"><sc-for list="{H("sl_apCults")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label>'
          f'<label class="sl-c"><span class="sl-rot">Variedade</span><input aria-label="Variedade para os marcados" list="{H("sl_apDl")}" autoComplete="off" spellCheck="false" placeholder="Variedade" value="{H("sl_apVar")}" onChange="{H("sl_apSetVar")}" style="font-family: inherit; font-size: 13px; padding: 6px 8px; border-radius: 8px; border: 1px solid {LINE}; width: 100%; min-width: 0; box-sizing: border-box;"></label>'
          f'<label class="sl-c"><span class="sl-rot">Plantio</span><input type="date" aria-label="Plantio para os marcados" value="{H("sl_apPlantio")}" onChange="{H("sl_apSetPlantio")}" style="font-family: inherit; font-size: 13px; padding: 6px 8px; border-radius: 8px; border: 1px solid {LINE}; width: 100%; min-width: 0; box-sizing: border-box;"></label>'
          f'<label class="sl-c"><span class="sl-rot">Meta {H("sl_apUn")}</span><input aria-label="Meta para os marcados" inputMode="decimal" autoComplete="off" placeholder="Meta" value="{H("sl_apMeta")}" onChange="{H("sl_apSetMeta")}" style="font-family: inherit; font-size: 13px; padding: 6px 8px; border-radius: 8px; border: 1px solid {LINE}; width: 100%; min-width: 0; box-sizing: border-box; text-align: right;"></label>'
          f'<span class="sl-un">{H("sl_apUn")}</span>'
          f'<label class="sl-c sl-c-plano"><span class="sl-rot">Plano agronômico</span><select aria-label="Plano para os marcados" value="{H("sl_apPlano")}" onChange="{H("sl_apSetPlano")}" style="font-family: inherit; font-size: 13px; padding: 6px 8px; border-radius: 8px; border: 1px solid {LINE}; background: {SURF}; width: 100%; min-width: 0;"><sc-for list="{H("sl_apPlanos")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label>'
          f'<span class="sl-apb"><button type="button" id="sl-aplicar" onClick="{H("sl_aplicar")}" style="{_MINI} {H("sl_apSt")} width: 100%;">{H("sl_apT")}</button></span></div>')
    dl = (f'<sc-for list="{H("sl_dl")}" as="d" hint-placeholder-count="2"><datalist id="{H("d.id")}"><sc-for list="{H("d.ops")}" as="o" hint-placeholder-count="2">'
          f'<option value="{H("o.t")}"></option></sc-for></datalist></sc-for>')
    return (CSS + MAPA_CSS +
            f'<sc-if value="{H("sl_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
            f'<button type="button" aria-label="Fechar" tabIndex="-1" onClick="{H("sl_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
            f'<aside role="dialog" aria-label="{H("sl_titulo")}" id="sl-painel" class="sl-pn" onKeyDown="{H("sl_key")}" style="position: relative; width: 1240px; max-width: 100%; height: 100%; overflow-y: auto; overflow-x: hidden; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px 0; box-sizing: border-box; display: flex; flex-direction: column; gap: 10px;">'
            f'<div style="display: flex; gap: 10px; align-items: flex-start;"><div style="flex-grow: 1; min-width: 0;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px;">{H("sl_titulo")}</h2>'
            f'<div style="font-size: 12.5px; color: {MUTED};">{H("sl_sub")}</div></div>'
            # SAF-MAPA (18/10): a mesma edição em Tabela ou Mapa (um estado só: seleção, rascunho e gravação)
            f'<div role="group" aria-label="Visão" style="display: flex; gap: 6px; flex-shrink: 0;"><sc-for list="{H("sl_vistas")}" as="w" hint-placeholder-count="2"><button type="button" class="sm-bt" aria-pressed="{H("w.on")}" aria-label="{H("w.al")}" onClick="{H("w.go")}" style="{H("w.st")}">{H("w.t")}</button></sc-for></div>'
            f'<button type="button" aria-label="Fechar" onClick="{H("sl_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
            f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 9px 12px; border-radius: 10px; background: {BG}; font-size: 13px;"><b>{H("sl_n")}</b><span style="color: {MUTED};">{H("sl_resumo")}</span><span role="status" id="sl-selo" style="{H("sl_selost")}">{H("sl_selo")}</span></div>'
            f'<sc-if value="{H("sl_hasg")}" hint-placeholder-val="{F()}"><div role="alert" id="sl-gerr" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("sl_gerr")}</div></sc-if>'
            f'<sc-if value="{H("sl_hasinfo")}" hint-placeholder-val="{F()}"><div role="status" id="sl-info" style="padding: 8px 12px; border-radius: 10px; background: #E3F0FB; color: #1E5F8F; font-size: 12.5px; font-weight: 600;">{H("sl_info")}</div></sc-if>'
            + dl +
            f'<sc-if value="{H("sl_vMapa")}" hint-placeholder-val="{F()}">' + _mapa_html() + '</sc-if>'
            f'<sc-if value="{H("sl_vTab")}" hint-placeholder-val="{H("true")}">'
            f'<div id="sl-grade" title="Tab anda nas colunas; Enter ou ↓ desce, ↑ sobe; cole um bloco do Excel a partir da célula" style="overflow-x: auto;" onKeyDown="{H("sl_nav")}" onPaste="{H("sl_colar")}"><div class="sl-gx">'
            f'<div class="sl-l sl-cab" aria-hidden="true">{lab}</div>' + ap +
            f'<sc-for list="{H("sl_lins")}" as="l" hint-placeholder-count="3">'
            f'<sc-if value="{H("l.ed")}" hint-placeholder-val="{H("true")}">{LINHA_ED}</sc-if>'
            f'<sc-if value="{H("l.grp")}" hint-placeholder-val="{F()}">{LINHA_TIT}</sc-if>'
            f'<sc-if value="{H("l.ro")}" hint-placeholder-val="{F()}">{LINHA_TIT}</sc-if>'
            f'</sc-for></div></div></sc-if>'
            f'<sc-if value="{H("sl_warn")}" hint-placeholder-val="{F()}"><div role="alert" class="saida" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.'
            f'<div style="display: flex; gap: 8px; flex-wrap: wrap;"><button type="button" onClick="{H("sl_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H("sl_keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
            f'<div class="sl-pe pe-form"><button type="button" onClick="{H("sl_close")}" style="{BTN_ST(False, True)}">Cancelar</button>'
            f'<button type="button" id="sl-salvar" aria-disabled="{H("sl_salvarDis")}" onClick="{H("sl_salvar")}" style="{BTN_ST(True, True)} {H("sl_salvarSt")}">{H("sl_salvarT")}</button></div>'
            f'</aside></div></sc-if>')
