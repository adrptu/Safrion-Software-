# Mapa: barra vertical limpa (ativo preenchido), nomes claros, etiqueta da funcionalidade sobre o mapa, zoom e tela cheia,
# cores sóbrias nas camadas operacionais (Satélite e Solo mantêm a paleta viva de índices), bordas brancas, estradas e grade, legenda flutuante.
import re
p = 'areas/inicio.py'; s = open(p).read()
def rep(a, b, tag, n=1):
    global s
    c = s.count(a); assert c == n, f'{tag}: {c}'
    s = s.replace(a, b)

# paleta operacional sóbria (mesmo significado de cor, menos saturada)
rep("MDATA=dict(tal=", "LCOR_OP={'ok':('#7FAE68','#FFFFFF'),'good':('#5F8F55','#FFFFFF'),'lime':('#A9C06A','#FFFFFF'),'yellow':('#D4B25A','#FFFFFF'),'orange':('#D98A4E','#FFFFFF'),"
    "'red':('#C8553D','#FFFFFF'),'gray':('#C9CFCB','#FFFFFF'),'blue':('#6E9FC6','#FFFFFF'),'navy':('#44739A','#FFFFFF'),'none':('#E4E9DF','#FFFFFF'),'cloud':('#C9CFCB','#FFFFFF'),'purple':('#9B8BC4','#FFFFFF')}\n"
    "NOME_LAY={'MIP/MID':'Pragas e doenças','O.S./prazos':'Ordens de serviço','Colheita/produtividade':'Colheita e produtividade'}\n"
    "MDATA=dict(tal=", 'paleta')
rep("prox=_proxima(),geo=_geo(),lc=LCOR)", "prox=_proxima(),geo=_geo(),lc=LCOR,lcop=LCOR_OP,nome=NOME_LAY)", 'mdata')
# JS: paleta por camada, nomes claros, subtítulo do talhão, zoom, dica
rep("function legend(l,f){", "function PAL(l){ return (l==='Satélite'||l==='Solo')?M.lc:M.lcop; }\nfunction legend(l,f){", 'PAL')
seg = s[s.index("function legend(l,f){"):s.index("function strip(")]
seg2 = seg.replace("M.lc[", "PAL(l)[")
s = s.replace(seg, seg2)
rep("const lc=M.lc[c.c]||M.lc.none;", "const pl=PAL(l); const lc=pl[c.c]||pl.none;", 'mapvals-pal')
rep("v.lay_t=l;", "v.lay_t=(M.nome[l]||l); v.hint=v.lay_t+' · clique no talhão para ver detalhes e ações'; const z=st.zoom||1; v.zst='transform:scale('+z+');transform-origin:50% 50%;transition:transform .2s;width:100%;height:100%;'; v.zin=()=>self.setState({zoom:Math.min(2,(self.state.zoom||1)+0.25)}); v.zout=()=>self.setState({zoom:Math.max(1,(self.state.zoom||1)-0.25)});", 'lay_t')
# contorno: branco no normal, escuro e grosso quando selecionado
rep("v['sk_'+t]=on?'#15201A':lc[1]; v['sw_'+t]=on?'6':'2';", "v['sk_'+t]=on?'#15201A':'#FFFFFF'; v['sw_'+t]=on?'6':'4'; v['sub_'+t]=M.tal[t].cult+' · '+nfx(M.tal[t].ha)+' ha';", 'stroke')
# barra vertical: ativo preenchido, demais sem moldura
old = s[s.index("  const lst=(on)=>"):s.index("\n", s.index("  const lst=(on)=>"))]
rep(old, "  const lst=(on)=>'width:96px;box-sizing:border-box;padding:9px 4px;border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;cursor:pointer;font-family:inherit;border:0;'+(on?'background:#1E6B47;color:#FFFFFF;':'background:transparent;color:#4B5A51;');", 'rail-style')
rep("f'{icon(ICON[t],19,INK)}<span style=\"font-size: 11px; font-weight: 700; line-height: 1.15; text-align: center;\">{esc(t.replace(\"/\",\" / \") if len(t)>14 else t)}</span></button>'",
    "f'{icon(ICON[t],20,\"currentColor\")}<span style=\"font-size: 11.5px; font-weight: 700; line-height: 1.15; text-align: center;\">{esc(NOME_LAY.get(t,t))}</span></button>'", 'rail-label')
rep("title=\"Mostrar {esc(t)} no mapa\"", "title=\"Mostrar {esc(NOME_LAY.get(t,t))} no mapa\"", 'rail-title')
# SVG: grade, estradas brancas, nome + cultura · área + situação da camada
rep("""            + defs + '<path d="M0 314 C 250 308, 520 320, 1000 314" stroke="#B9C6AE" stroke-width="12" fill="none"/>' + ''.join(g) + '</svg>')""",
    """            + defs + '<rect width="1000" height="620" fill="url(#grade)"/><path d="M0 314 C 250 308, 520 320, 1000 314" stroke="#FFFFFF" stroke-width="10" fill="none" opacity=".9"/>'
            + '<path d="M318 0 L322 620" stroke="#FFFFFF" stroke-width="7" fill="none" opacity=".8"/>' + ''.join(g) + '</svg>')""", 'svg-road')
rep("""    defs=('<defs><pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#C9CFCB"/>'
          '<line x1="0" y1="0" x2="0" y2="10" stroke="#9E9E9E" stroke-width="4"/></pattern></defs>') if defs else ''""",
    """    defs=('<defs><pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#C9CFCB"/>'
          '<line x1="0" y1="0" x2="0" y2="10" stroke="#9E9E9E" stroke-width="4"/></pattern>'
          '<pattern id="grade" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0 L0 0 0 40" fill="none" stroke="#D3DDCB" stroke-width="1"/></pattern></defs>') if defs else ''""", 'defs')
rep("""        g.append(f'<foreignObject x="{cx-lw/2:.0f}" y="{cy+13:.0f}" width="{lw}" height="46" style="pointer-events: none;"><div xmlns="http://www.w3.org/1999/xhtml" style="{_LBL}">{H("lab_"+tid)}</div></foreignObject>')""",
    """        g.append(f'<foreignObject x="{cx-lw/2:.0f}" y="{cy+12:.0f}" width="{lw}" height="20" style="pointer-events: none;"><div xmlns="http://www.w3.org/1999/xhtml" style="{_SUB}">{H("sub_"+tid)}</div></foreignObject>')
        g.append(f'<foreignObject x="{cx-lw/2:.0f}" y="{cy+32:.0f}" width="{lw}" height="46" style="pointer-events: none;"><div xmlns="http://www.w3.org/1999/xhtml" style="{_LBL}">{H("lab_"+tid)}</div></foreignObject>')""", 'svg-sub')
rep("def _mapsvg(defs=True):", "_SUB=('font-family: Manrope, sans-serif; font-size: 13px; font-weight: 700; color: #15201A; text-align: center; line-height: 1.2; opacity: .85; '\n      'text-shadow: 0 0 3px #fff, 0 0 3px #fff, 0 0 4px #fff;')\ndef _mapsvg(defs=True):", 'sub-style')
# cartão do mapa: etiqueta, zoom, ferramentas e legenda flutuante
rep("""    tools=(f'<div role="toolbar" aria-label="Ferramentas do mapa" style="position: absolute; right: 12px; top: 10px; display: flex; gap: 6px;">'""",
    """    sq=lambda t,fn,lab: f'<button type="button" onClick="{H(fn)}" aria-label="{lab}" title="{lab}" style="width: 36px; height: 36px; border: 0; border-radius: 10px; background: #FFFFFF; box-shadow: 0 1px 4px rgba(21,32,26,.18); font-family: inherit; font-size: 18px; font-weight: 700; color: {INK}; cursor: pointer;">{t}</button>'
    zoom=(f'<div role="group" aria-label="Zoom" style="position: absolute; right: 12px; top: 56px; display: flex; flex-direction: column; gap: 6px;">'
          + sq('+','zin','Aproximar') + sq('−','zout','Afastar') + '</div>')
    tools=(f'<div role="toolbar" aria-label="Ferramentas do mapa" style="position: absolute; right: 12px; top: 10px; display: flex; gap: 6px;">'""", 'zoom')
rep("""      f'<div style="flex-grow: 1; min-width: 0; position: relative; background: #DDE5D4;">{_mapsvg(defs=not full)}{tools}'""",
    """      f'<div style="flex-grow: 1; min-width: 0; position: relative; background: #E3EADB; overflow: hidden;"><div style="{H("zst")}">{_mapsvg(defs=not full)}</div>{tools}{zoom}'
      f'<sc-if value="{H("has_modo")}" hint-placeholder-val="{T()}"><span style="position: absolute; left: 12px; top: 10px; padding: 7px 12px; border-radius: 10px; background: #FFFFFF; box-shadow: 0 1px 4px rgba(21,32,26,.18); font-size: 12.5px;"><b>{H("lay_t")}</b> <span style="color: {MUTED};">· clique no talhão para ver detalhes e ações</span></span></sc-if>'
      f'<div style="position: absolute; left: 12px; bottom: 12px; right: 12px; display: flex; flex-wrap: wrap; align-items: center; gap: 4px 12px; padding: 8px 12px; border-radius: 10px; background: rgba(255,255,255,.94); box-shadow: 0 1px 4px rgba(21,32,26,.14); font-size: 11.5px; color: {MUTED};">'
      f'<sc-for list="{H("leg")}" as="x" hint-placeholder-count="5"><span style="{H("x.st")}"><span style="{H("x.dot")}"></span>{H("x.t")}</span></sc-for><span style="flex-grow: 1;"></span><span>Geometria e valores demonstrativos.</span></div>'""", 'mapcard-overlay')
# a dica aparece quando não há modo ativo; o selo de modo continua no mesmo lugar
s = s.replace('<sc-if value="{H("has_modo")}" hint-placeholder-val="{T()}"><span style="position: absolute; left: 12px; top: 10px; padding: 7px 12px;',
              '<sc-if value="{H("sem_modo")}" hint-placeholder-val="{T()}"><span style="position: absolute; left: 12px; top: 10px; padding: 7px 12px;', 1)
rep("v.has_modo=!!(st.selm||st.medir||st.", "v.sem_modo=!(st.selm||st.medir||st.cvis); v.has_modo=!!(st.selm||st.medir||st.", 'sem_modo')
# rodapé antigo com a legenda sai (a legenda agora flutua sobre o mapa)
old = s[s.index("""      f'<div style="display: flex; flex-wrap: wrap; gap: 4px 12px; padding: 7px 12px; border-top: 1px solid {LINE}; font-size: 11.5px; color: {MUTED}; min-width: 0;">'"""):]
old = old[:old.index("</sc-for></div>'") + len("</sc-for></div>'")]
rep(old + "\n", "", 'rodape')
open(p, 'w').write(s); print('patch mapa visual ok')
