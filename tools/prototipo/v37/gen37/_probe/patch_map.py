p='areas/inicio.py'; s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)==1, a[:80]; s=s.replace(a,b)
# valores: funcionalidade ativa, botões da barra vertical e atalho da funcionalidade
rep("""  v.fonte=fonte(l,f); v.leg=legend(l,f); v.nums=strip(self,l,f);""",
"""  v.fonte=fonte(l,f); v.leg=legend(l,f); v.nums=strip(self,l,f); v.lay_t=l;
  const FL={'Integrado':['Abrir ordens','OS.dc.html'],'Satélite':['Ver histórico','AG-06.dc.html'],'Solo':['Ver recomendações','AG-04.dc.html'],'MIP/MID':['Criar vistoria','AG-01.dc.html'],
    'O.S./prazos':['Abrir ordens','OS.dc.html'],'Irrigação':['Irrigação de hoje','IR-03.dc.html'],'Estádio':['Abrir safra','SAF.dc.html'],'Colheita/produtividade':['Ver previsão','CO-01.dc.html'],'Custos':['Abrir custos','GE-03.dc.html']};
  v.flink=(FL[l]||['',''])[1]; v.flinkt=(FL[l]||['',''])[0]; v.hasFlink=!!FL[l];
  const lst=(on)=>'width:92px;box-sizing:border-box;padding:7px 4px;border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;cursor:pointer;font-family:inherit;color:#15201A;'+(on?'border:1px solid #1E7A4C;background:#E4F3E9;box-shadow:inset 3px 0 0 #1E7A4C;':'border:1px solid #E4E9E5;background:#FFFFFF;');
  M.lays.forEach((x,i)=>{ v['ly'+i+'_st']=lst(x===l); v['ly'+i+'_on']=(x===l)?'true':'false'; v['ly'+i+'_go']=()=>self.setState({lay:x}); });""")
rep("""  const rst=(on)=>'width:84px;box-sizing:border-box;padding:8px 4px;border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;cursor:pointer;text-decoration:none;font-family:inherit;color:#15201A;'+(on?'border:1px solid #1E7A4C;background:#E4F3E9;':'border:1px solid #E4E9E5;background:#FFFFFF;');""",
"""  const rst=(on)=>'display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:10px;cursor:pointer;font-family:inherit;font-size:12px;font-weight:700;color:#15201A;box-shadow:0 1px 3px rgba(21,32,26,.18);'+(on?'border:1px solid #1E7A4C;background:#E4F3E9;':'border:1px solid #E4E9E5;background:#FFFFFF;');""")
# cartão do mapa: barra horizontal = funcionalidade ativa + filtros + indicadores + atalho; ferramentas sobre o mapa; rodapé só com a legenda
i0=s.index("def _mapcard(h,full=False):"); i1=s.index("def _defs_body():")
new='''def _mapcard(h,full=False):
    fgroups=(f'<sc-for list="{H("flt")}" as="g" hint-placeholder-count="2"><span style="display: inline-flex; align-items: center; gap: 6px;">'
             f'<span style="font-size: 11.5px; font-weight: 700; color: {MUTED};">{H("g.l")}</span>'
             f'<span role="group" aria-label="{H("g.l")}" style="display: inline-flex; gap: 2px; padding: 2px; border-radius: 9px; background: {GRAYS};"><sc-for list="{H("g.opts")}" as="o" hint-placeholder-count="3">'
             f'<button type="button" aria-pressed="{H("o.on")}" onClick="{H("o.go")}" style="{H("o.st")}">{H("o.t")}</button></sc-for></span></span></sc-for>')
    nums=(f'<div role="group" aria-label="Indicadores de {H("lay_t")}" style="display: flex; gap: 14px; flex-wrap: wrap;"><sc-for list="{H("nums")}" as="n" hint-placeholder-count="4">'
          f'<span style="white-space: nowrap; font-size: 11.5px; color: {MUTED};">{H("n.k")} <b style="color: {INK}; font-size: 13.5px;">{H("n.val")}</b></span></sc-for></div>')
    tool=lambda ic,t,fn,st,tt: f'<button type="button" onClick="{H(fn)}" title="{tt}" aria-pressed="{H(st.replace("_st","_on"))}" style="{H(st)}">{icon(ic,15,INK)}{t}</button>'
    tools=(f'<div role="toolbar" aria-label="Ferramentas do mapa" style="position: absolute; right: 12px; top: 10px; display: flex; gap: 6px;">'
           + tool('grid','Selecionar área','r_selm','r_selm_st','Selecionar vários talhões') + tool('trend','Medir','r_medir','r_medir_st','Medir área e perímetro')
           + (tool('map','Sair da tela cheia','r_full','r_full_st','Sair da tela cheia') if full else tool('map','Tela cheia','r_full','r_full_st','Mapa em tela cheia')) + '</div>')
    return (f'<div style="height: {h}px; min-width: 0; flex-grow: 1; display: flex; flex-direction: column; background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; overflow: hidden;">'
      f'<div style="display: flex; align-items: center; gap: 10px 16px; padding: 10px 12px 8px; flex-wrap: wrap; border-bottom: 1px solid {LINE};">'
      f'<b style="font-size: 14px; white-space: nowrap;">{H("lay_t")}</b>{fgroups}<span style="flex-grow: 1;"></span>{nums}'
      f'<sc-if value="{H("hasFlink")}" hint-placeholder-val="{F()}"><a href="{H("flink")}" style="{_MINI} text-decoration: none; white-space: nowrap;">{H("flinkt")} ›</a></sc-if>'
      f'<div title="{H("fonte")}" style="flex-basis: 100%; font-size: 11px; color: {MUTED}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{H("fonte")}</div></div>'
      f'<div style="flex-grow: 1; min-height: 0; display: flex;">'
      f'<div style="flex-grow: 1; min-width: 0; position: relative; background: #DDE5D4;">{_mapsvg(defs=not full)}{tools}'
      f'<sc-if value="{H("has_modo")}" hint-placeholder-val="{F()}"><span role="status" style="position: absolute; left: 12px; top: 10px; padding: 5px 10px; border-radius: 999px; background: {INK}; color: #fff; font-size: 12px; font-weight: 700;">{H("modo")}</span></sc-if></div>'
      f'<sc-if value="{H("pan_open")}" hint-placeholder-val="{F()}">{_panel_html()}</sc-if></div>'
      f'<div style="display: flex; flex-wrap: wrap; gap: 4px 12px; padding: 7px 12px; border-top: 1px solid {LINE}; font-size: 11.5px; color: {MUTED}; min-width: 0;">'
      f'<sc-for list="{H("leg")}" as="x" hint-placeholder-count="5"><span style="{H("x.st")}"><span style="{H("x.dot")}"></span>{H("x.t")}</span></sc-for></div>'
      f'</div>')
'''
s=s[:i0]+new+s[i1:]
# barra vertical = funcionalidades
i0=s.index("def _rail():"); i1=s.index("def build_in04(")
ICON={'Integrado':'layers','Satélite':'grid','Solo':'lab','MIP/MID':'alert','O.S./prazos':'doc','Irrigação':'drop','Estádio':'leaf','Colheita/produtividade':'Colheita','Custos':'cash'}
new='''def _rail():
    ICON=%r
    items=[f'<button type="button" role="tab" aria-selected="{H("ly%%d_on" %% i)}" onClick="{H("ly%%d_go" %% i)}" title="Mostrar {esc(t)} no mapa" style="{H("ly%%d_st" %% i)}">'
           f'{icon(ICON[t],19,INK)}<span style="font-size: 11px; font-weight: 700; line-height: 1.15; text-align: center;">{esc(t.replace("/"," / ") if len(t)>14 else t)}</span></button>'
           for i,t in enumerate(MDATA['lays'])]
    return f'<nav role="tablist" aria-orientation="vertical" aria-label="Funcionalidades do mapa" style="display: flex; flex-direction: column; gap: 6px; flex-shrink: 0;">{"".join(items)}</nav>'

''' % ICON
s=s[:i0]+new+s[i1:]
rep("""    EXTRA.append(f'<sc-if value="{H("full")}" hint-placeholder-val="{F()}"><div role="dialog" aria-label="Mapa em tela cheia" style="position: fixed; inset: 0; z-index: 55; background: {BG}; padding: 14px; box-sizing: border-box; display: flex;">{_mapcard(872,full=True)}</div></sc-if>')""",
"""    EXTRA.append(f'<sc-if value="{H("full")}" hint-placeholder-val="{F()}"><div role="dialog" aria-label="Mapa em tela cheia" style="position: fixed; inset: 0; z-index: 55; background: {BG}; padding: 14px; box-sizing: border-box; display: flex; gap: 12px;">{_rail()}{_mapcard(872,full=True)}</div></sc-if>')""")
open(p,'w').write(s); print('patch mapa ok')
