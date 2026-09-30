# Cabeçalho: filtros de Fazenda e Safra só onde se aplicam e funcionando; contexto só de leitura onde a escolha é feita no processo.
p = 'ui37.py'; s = open(p).read()
def rep(a, b, tag):
    global s
    n = s.count(a); assert n == 1, f'{tag}: {n}'
    s = s.replace(a, b)

# aplicabilidade por tela (menu vigente). Ausente = sem filtro nem contexto no cabeçalho.
rep("def shell37(fid,title,body,", '''# Filtros do topo por tela: 'filtro' = seletor que muda os dados da tela; 'contexto' = só leitura (escolhido no próprio processo).
MACRO = {
    'IN-04.dc.html': dict(faz='filtro'),
    'OS.dc.html': dict(faz='filtro', saf='filtro'),
    'SAF.dc.html': dict(faz='contexto', saf='contexto'),
    'CMP.dc.html': dict(faz='contexto', saf='contexto'),
    'EST.dc.html': dict(faz='filtro'),
}
FAZENDAS = ['Santa Rita', 'Boa Vista']
SAFRAS_MF = ['2026/27', 'Safrinha 2027', '2025/26']
def _macro_html(fname, ctx):
    cfg = MACRO.get(fname)
    sel = ('font-family: inherit; font-size: 12px; font-weight: 700; padding: 4px 26px 4px 10px; border-radius: 999px; border: 1px solid {LINE}; background: {SURF}; color: {INK}; cursor: pointer;')
    lab = f'display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; background: {GRAYS}; font-weight: 700; font-size: 11.5px;'
    if cfg is None:
        return ''
    out = ''
    if cfg.get('faz') == 'filtro':
        out += (f'<label style="display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; color: {MUTED}; font-weight: 700;">Fazenda'
                f'<select aria-label="Filtrar por fazenda" value="{{{{mf_faz}}}}" onChange="{{{{mf_setfaz}}}}" style="' + sel.format(LINE=LINE, SURF=SURF, INK=INK) + '">'
                + ''.join(f'<option value="{f}">{f}</option>' for f in ['Todas'] + FAZENDAS) + '</select></label>')
    elif cfg.get('faz') == 'contexto':
        out += f'<span title="Fazenda da safra aberta" style="{lab}">{esc(ctx[0]) if ctx and ctx[0] else "Fazenda Santa Rita"}</span>'
    if cfg.get('saf') == 'filtro':
        out += (f'<label style="display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; color: {MUTED}; font-weight: 700;">Safra'
                f'<select aria-label="Filtrar por safra" value="{{{{mf_saf}}}}" onChange="{{{{mf_setsaf}}}}" style="' + sel.format(LINE=LINE, SURF=SURF, INK=INK) + '">'
                + ''.join(f'<option value="{f}">{f}</option>' for f in ['Todas'] + SAFRAS_MF) + '</select></label>')
    elif cfg.get('saf') == 'contexto':
        out += (f'<span style="{lab}">{ctx[1] if ctx and len(ctx) > 1 and ctx[1] else ""}</span>'
                f'<button type="button" onClick="{{{{mf_trocar}}}}" title="Voltar à etapa 1 para escolher outra safra" style="border: 0; background: transparent; color: {ACC}; font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; text-decoration: underline; text-underline-offset: 3px;">Trocar safra</button>')
    return out + f'<span style="width: 1px; height: 18px; background: {LINE};"></span>'

def shell37(fid,title,body,''', 'MACRO')
rep("""    if oculto(fname): ctx=tuple(ctx)+('Módulo oculto no menu · preservado',)
    ctxp=''.join(f'<span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; background: {GRAYS}; font-weight: 700; font-size: 11.5px;">{esc(c)}</span>' for c in ctx if c)""",
"""    if oculto(fname):
        ctxp=''.join(f'<span style="font-size: 11.5px; color: {MUTED}; font-weight: 600;">{esc(c)}</span>' for c in (tuple(ctx)+('Módulo oculto no menu · preservado',)) if c)
        ctxp+=f'<span style="width: 1px; height: 18px; background: {LINE};"></span>'
    else:
        ctxp=_macro_html(fname,ctx)
        search=False""", 'ctxp')
rep("""<div style="display: flex; align-items: center; gap: 10px; font-size: 12.5px; font-weight: 500;">{ctxp}<span style="width: 1px; height: 18px; background: {LINE};"></span><span>{crumb}</span>{srch}</div>""",
    """<div style="display: flex; align-items: center; gap: 10px; font-size: 12.5px; font-weight: 500;">{ctxp}<span>{crumb}</span>{srch}</div>""", 'header-line')
open(p, 'w').write(s)

# motor: estado e ações dos filtros do topo, disponíveis a todas as telas (a tela que filtra lê self.state.mf_faz / mf_saf)
p = 'engine.py'; s = open(p).read()
rep("""    v.g2toast = this.state.g2toast || ''; v.g2toastst = this.state.g2toast ? '' : 'display: none;';""",
    """    v.g2toast = this.state.g2toast || ''; v.g2toastst = this.state.g2toast ? '' : 'display: none;';
    v.mf_faz = this.state.mf_faz || 'Santa Rita'; v.mf_saf = this.state.mf_saf || 'Todas';
    v.mf_setfaz = (e) => this.setState({ mf_faz: e.target.value, g2toast: 'Fazenda: ' + e.target.value });
    v.mf_setsaf = (e) => this.setState({ mf_saf: e.target.value, g2toast: 'Safra: ' + e.target.value });
    if (!v.mf_trocar) v.mf_trocar = () => this.setState({ step: 1, g2toast: 'Escolha a safra na etapa 1.' });""", 'engine-mf')
open(p, 'w').write(s)
print('patch macro ok')
