# -*- coding: utf-8 -*-
"""Shell v3.7: menu de 13 áreas do cap. 4.1, contexto do cap. 4.2, faixa de continuidade e rodapé de demonstração."""
import json, os
from engine import (INK,MUTED,LINE,BG,SURF,ACC,ACCS,SH,SIDE,SIDE_TX,SIDE_MUTED,DISP,FONT,YEL,YELS,RED,REDS,GRAY,GRAYS,
                    icon,esc,chip,btn,act,chev,engine,extra_html,wid,reg,wget,_reset_screen,FIRST_TBL,CHIP_ON,CHIP_OFF,HL)
import engine as E

V37=os.path.dirname(os.path.abspath(__file__))
CAT=json.load(open(os.path.join(V37,'..','catalogo.json')))
MENU=json.load(open(os.path.join(V37,'..','menu.json')))
MAPA=json.load(open(os.path.join(V37,'..','menu_map.json')))

AREA_ICON={'Início':'Início','Agronomia':'Agronomia','Planejamento':'calendar','Campo':'Campo','Irrigação':'Irrigação',
 'Máquinas e manutenção':'wrench','Colheita e pós-colheita':'Colheita','Suprimentos':'cart','Comercial':'Vendas',
 'Logística':'truck','Gestão e resultados':'trend','Cadastros':'layers','Configurações':'grid'}
PREF_AREA={'IN':'Início','AG':'Agronomia','PL':'Planejamento','CA':'Campo','IR':'Irrigação','MA':'Máquinas e manutenção',
 'CO':'Colheita e pós-colheita','SU':'Suprimentos','VE':'Comercial','LO':'Logística','GE':'Gestão e resultados',
 'CD':'Cadastros','CF':'Configurações','PT':'Portal do parceiro','BO':'Backoffice da plataforma','ON':'Onboarding','MB':'App móvel'}
EXTERNOS={'PT':('Portal do parceiro','tag'),'BO':('Backoffice da plataforma','card'),'ON':('Onboarding','users')}

def ffile(fid): return f'{fid}.dc.html'
def area_of(fid): return PREF_AREA.get(fid[:2])

HEIGHTS37={}
_OVR_P=os.path.join(V37,'heights_override.json')
H_OVR=json.load(open(_OVR_P)) if os.path.exists(_OVR_P) else {}  # alturas medidas pelo qa37 (overflow real)
def _h(fname,H): return H_OVR.get(fname) or HEIGHTS37.get(fname,H)
PRIMHREF={}   # fid -> destino do botão primário
PARENT37={}   # fname -> fname de volta

# Menu vigente por decisão do proprietário (25/09/2026): Mapa · Cadastros · Agrícola · Suprimentos.
# Os demais módulos ficam ocultos do menu, preservados no canvas (página "Módulos ocultos").
MENU2=[('Mapa','map',[('Mapa','IN-04.dc.html')]),
 ('Cadastros','layers',[('Fazendas, áreas e talhões','CD-01.dc.html'),('Culturas, cultivares e operações','CD-02.dc.html'),('Máquinas, instalações e setores','CD-03.dc.html'),
   ('Pessoas e equipes','CD-04.dc.html'),('Parceiros e fornecedores','CD-05.dc.html'),('Produtos, unidades e locais','CD-06.dc.html'),('Estrutura gerencial','CD-07.dc.html')]),
 ('Agrícola','leaf',[('Planos agronômicos','PA.dc.html'),('Planejar safra','SAF.dc.html'),('Ordem de Serviço','OS.dc.html')]),
 ('Suprimentos','cart',[('Compra de insumos','CMP.dc.html'),('Estoque','EST.dc.html')])]
MENU_OF={'CA-01det.dc.html':'OS.dc.html','CA-02.dc.html':'OS.dc.html','CA-01x-os0420.dc.html':'OS.dc.html'}  # detalhes que pertencem a um item do menu
def menu_item(fname):
    f=MENU_OF.get(fname,fname)
    for i,(nome,ic,items) in enumerate(MENU2):
        for lab,h in items:
            if h==f or (f.startswith(h.replace('.dc.html','')) and f!=h and h not in ('IN-04.dc.html',) and f[:len(h)-8]==h[:-8]): return i,h
    return None,None
def oculto(fname):
    return menu_item(fname)[0] is None and fname!='Main.dc.html'
def navbar(fid,fname=None):
    """Barra lateral: macro menus expansíveis (estado real na tela); item ativo destacado."""
    import engine as _E
    fname=fname or ffile(fid)
    act_i,act_h=menu_item(fname)
    out=[]
    for i,(nome,ic,items) in enumerate(MENU2):
        on=(i==act_i)
        if len(items)==1:
            h=items[0][1]
            st=(f'display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-radius: 10px; font-size: 13.5px; font-weight: 700; text-decoration: none; '
                + (f'background: {ACC}; color: #fff;' if on else f'color: {SIDE_TX};'))
            out.append(f'<a href="{h}" style="{st}">{icon(ic,16,"#fff" if on else SIDE_TX)}{esc(nome)}</a>')
            continue
        _E.NAVSPEC.append({'open':on})
        k=len(_E.NAVSPEC)-1
        out.append(f'<button type="button" aria-expanded="{{{{nav{k}_open}}}}" onClick="{{{{nav{k}_tog}}}}" style="display: flex; align-items: center; gap: 10px; width: 100%; padding: 8px 12px; border: 0; border-radius: 10px; font-family: inherit; font-size: 13.5px; font-weight: 700; text-align: left; cursor: pointer; background: {"rgba(255,255,255,.10)" if on else "transparent"}; color: {"#fff" if on else SIDE_TX};">'
                   f'{icon(ic,16,"#fff" if on else SIDE_TX)}<span style="flex-grow: 1;">{esc(nome)}</span><span aria-hidden="true" style="font-size: 11px; color: {SIDE_MUTED};">{{{{nav{k}_sym}}}}</span></button>')
        subs=''
        for lab,h in items:
            cur=(h==act_h)
            s2=('display: block; margin-left: 30px; padding: 5px 10px; border-radius: 8px; font-size: 12.8px; text-decoration: none; '
                + (f'background: {ACC}; color: #fff; font-weight: 700;' if cur else f'color: {SIDE_MUTED}; font-weight: 500;'))
            subs+=f'<a href="{h}" style="{s2}">{esc(lab)}</a>'
        out.append(f'<sc-if value="{{{{nav{k}_open}}}}" hint-placeholder-val="{{{{{"true" if on else "false"}}}}}"><div style="display: flex; flex-direction: column; gap: 1px; margin-bottom: 4px;">{subs}</div></sc-if>')
    return ''.join(out)

def steps_bar(steps,current=None,label='Etapas do processo'):
    """Faixa de etapas por links (módulos sequenciais): colunas iguais que sempre cabem; nome quebra em até 2 linhas.
    steps: [dict(t, href=None, fn=None, why='', cur=bool, tip)]"""
    n=len(steps); items=''
    for i,s in enumerate(steps,1):
        cur=s.get('cur',False) if current is None else (i==current)
        why=s.get('why') or ''
        badge=(f'background: {ACC}; color: #fff;' if cur else (f'background: {REDS}; color: {RED};' if why else f'background: {GRAYS}; color: {INK};'))
        num=f'<span style="width: 22px; height: 22px; border-radius: 999px; display: inline-flex; align-items: center; justify-content: center; font-size: 11.5px; font-weight: 800; flex-shrink: 0; {badge}">{i}</span>'
        whyh=(f'<span style="display: block; font-size: 11px; font-weight: 700; color: {RED}; line-height: 1.2;">{why}</span>' if why else '')
        inner=f'{num}<span style="display: flex; flex-direction: column; min-width: 0;"><span style="font-size: 12.5px; line-height: 1.2; font-weight: {800 if cur else 600};">{esc(s["t"])}</span>{whyh}</span>'
        st=('display: flex; align-items: center; gap: 7px; padding: 5px 8px; border-radius: 10px; text-decoration: none; color: '+INK+'; font-family: inherit; border: 0; cursor: pointer; text-align: left; min-width: 0; '
            + (f'background: {ACCS}; box-shadow: inset 0 -2px 0 {ACC};' if cur else 'background: transparent;'))
        aria=' aria-current="step"' if cur else ''
        if s.get('fn'): items+=f'<button type="button" onClick="{{{{{s["fn"]}}}}}" title="{esc(s.get("tip") or s["t"])}"{aria} style="{st}">{inner}</button>'
        else: items+=f'<a href="{s.get("href","#")}" title="{esc(s.get("tip") or s["t"])}"{aria} style="{st}">{inner}</a>'
    return (f'<nav aria-label="{esc(label)}" style="position: sticky; top: 0; z-index: 30; background: {SURF}; border-bottom: 1px solid {LINE}; box-shadow: 0 6px 12px -10px rgba(21,32,26,.25); padding: 5px 24px 6px;">'
            f'<div style="font-size: 10px; font-weight: 800; letter-spacing: .08em; color: {MUTED}; text-transform: uppercase; padding: 0 8px 3px;">{esc(label)}</div>'
            f'<div style="display: grid; grid-template-columns: repeat({n}, minmax(0, 1fr)); gap: 4px;">{items}</div></nav>')

def continuity(veio,aqui,falta,proxima):
    """Faixa do cap. 4.2: Veio de → Está aqui → Falta → Próxima ação."""
    def cell(lbl,val,strong=False):
        return (f'<span style="display: inline-flex; flex-direction: column; gap: 1px; min-width: 0;">'
                f'<span style="font-size: 10.5px; font-weight: 700; letter-spacing: .06em; color: {MUTED};">{lbl}</span>'
                f'<span style="font-size: 12.5px; font-weight: {700 if strong else 600}; color: {ACC if strong else INK}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{val}</span></span>')
    arrow=f'<span style="color: {MUTED}; flex-shrink: 0;">→</span>'
    return (f'<div style="display: flex; align-items: center; gap: 12px; padding: 8px 14px; background: {ACCS}; border: 1px solid {LINE}; border-radius: 12px;">'
            + cell('VEIO DE',veio)+arrow+cell('ESTÁ AQUI',f'<b>{aqui}</b>')+arrow+cell('FALTA',falta)+arrow+cell('PRÓXIMA AÇÃO',proxima,strong=True)+'</div>')

def demo_badge():
    return (f'<div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; margin: 4px 0; border-radius: 10px; background: rgba(255,255,255,.06); color: {SIDE_MUTED}; font-size: 11px; font-weight: 700; letter-spacing: .05em;">'
            f'<span style="width: 7px; height: 7px; border-radius: 999px; background: {YEL};"></span>DEMONSTRAÇÃO · dados fictícios</div>')

def perfil_pill(perfil):
    ini=perfil[0].upper()
    return (f'<div style="display: flex; align-items: center; gap: 10px; padding: 10px 12px; font-size: 12.5px; color: {SIDE_TX}; border-top: 1px solid rgba(255,255,255,.08);">'
            f'<span style="width: 26px; height: 26px; border-radius: 999px; background: {ACC}; color: #fff; font-weight: 700; font-size: 12px; display: inline-flex; align-items: center; justify-content: center;">{ini}</span>'
            f'<span style="display: flex; flex-direction: column; line-height: 1.2;"><span style="font-weight: 700; color: #fff;">{esc(perfil)}</span><span style="color: {SIDE_MUTED}; font-size: 11.5px;">Trocar perfil de demonstração ▾</span></span></div>')

# Filtros do topo por tela: 'filtro' = seletor que muda os dados da tela; 'contexto' = só leitura (escolhido no próprio processo).
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

def shell37(fid,title,body,subtitle='',status=None,primary=None,primary_href=None,crumbs_extra=None,
            ctx=('Fazenda Santa Rita','Safra 2026/27',None),cont=None,chipsrow='',footer=None,
            fname=None,W=1440,H=880,perfil='Ana · Gestora',search=True,steps=None,primary_html=None):
    fname=fname or ffile(fid)
    H=_h(fname,H)
    if steps: H=max(900,min(H,1000))  # processos: tela de trabalho com rolagem interna; faixa de etapas sempre visível
    mi,mh=menu_item(fname)
    if mi is not None:
        m={'area':MENU2[mi][0],'submenu':next(l for l,h in MENU2[mi][2] if h==mh)}
    else:
        m=MAPA.get(fid) or {'area':area_of(fid) or 'Módulo oculto','submenu':CAT.get(fid,{}).get('titulo',fid)}
    crumbs=[m['area'],m['submenu']]+(crumbs_extra or [])
    back=PARENT37.get(fname) or ffile(fid) if crumbs_extra else (PARENT37.get(fname) or fname)
    first=(MENU2[mi][2][0][1].replace('.dc.html','') if mi is not None else next((f for f in MAPA if MAPA[f]['area']==m['area']),fid))
    _sep=f' <span style="color: {MUTED};">›</span> '
    parts=[]
    for i,c in enumerate(crumbs):
        if i==0 and ffile(first)!=fname: parts.append(f'<a href="{ffile(first)}" style="color: {MUTED}; text-decoration: none;">{esc(c)}</a>')
        elif i==1 and crumbs_extra: parts.append(f'<a href="{(mh or ffile(fid))}" style="color: {MUTED}; text-decoration: none;">{esc(c)}</a>')
        elif i<len(crumbs)-1: parts.append(f'<span style="color: {MUTED};">{esc(c)}</span>')
        else: parts.append(f'<span>{esc(c)}</span>')
    crumb=_sep.join(parts)
    if oculto(fname):
        ctxp=''.join(f'<span style="font-size: 11.5px; color: {MUTED}; font-weight: 600;">{esc(c)}</span>' for c in (tuple(ctx)+('Módulo oculto no menu · preservado',)) if c)
        ctxp+=f'<span style="width: 1px; height: 18px; background: {LINE};"></span>'
    else:
        ctxp=_macro_html(fname,ctx)
        search=False
    st=chip(status[0],status[1]) if status else ''
    srch=(f'<span style="flex-grow: 1;"></span><span style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border: 1px solid {LINE}; border-radius: 999px; background: {SURF}; color: {MUTED}; font-size: 12.5px; min-width: 220px;">'
          f'{icon("lista",13,MUTED)}Buscar ID, talhão, ativo, lote, pessoa…</span>') if search else '<span style="flex-grow: 1;"></span>'
    prim=primary_html or (btn(primary,True,href=primary_href) if primary else '')
    controw=cont if cont else ''
    foot=f'<div style="display: flex; align-items: center; gap: 10px; padding: 12px 32px; border-top: 1px solid {LINE}; background: {SURF};"><span style="width: 8px; height: 8px; border-radius: 999px; background: {ACC};"></span><div style="font-size: 13px; color: {MUTED};">{esc(footer)}</div></div>' if footer else ''
    voltar=f'<a href="{back}" aria-label="Voltar" style="text-decoration: none; display: inline-flex; align-items: center;">{chev()}</a>' if crumbs_extra else ''
    html=f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&amp;family=Sora:wght@600;700&amp;display=swap">
<style>
body{{margin:0;font-family:{FONT};color:{INK};background:{BG}}}
a{{color:{ACC}}}a:hover{{color:#15603a}}
{E.G2_CSS}
</style>
</helmet>
<div data-root="1" style="position: relative; width: {W}px; height: {H}px; box-sizing: border-box; display: flex; background: {BG}; font-family: {FONT}; color: {INK}; overflow: clip;">
<nav aria-label="Menu" style="width: 232px; flex-shrink: 0; background: {SIDE}; display: flex; flex-direction: column; padding: 16px 12px 12px; gap: 2px; box-sizing: border-box; overflow: clip;">
<a href="Main.dc.html" aria-label="Índice do protótipo" style="display: flex; align-items: center; gap: 10px; padding: 2px 12px 8px; font-family: {DISP}; font-weight: 700; font-size: 15px; letter-spacing: -.01em; color: #fff; text-decoration: none;"><span style="width: 28px; height: 28px; border-radius: 9px; background: {ACC}; display: inline-flex; align-items: center; justify-content: center;">{icon("Agronomia",16,"#fff")}</span>Talhão à O.S.</a>
{navbar(fid,fname)}
<div style="flex-grow: 1;"></div>
{demo_badge()}
{perfil_pill(perfil)}
</nav>
<div style="flex-grow: 1; display: flex; flex-direction: column; min-width: 0; min-height: 0;">
<header style="padding: 14px 32px 14px; background: {SURF}; border-bottom: 1px solid {LINE}; display: flex; flex-direction: column; gap: 10px;">
<div style="display: flex; align-items: center; gap: 10px; font-size: 12.5px; font-weight: 500;">{ctxp}<span>{crumb}</span>{srch}</div>
<div style="display: flex; align-items: center; gap: 12px;">
{voltar}<h1 style="margin: 0; font-family: {DISP}; font-size: 23px; font-weight: 700; letter-spacing: -.02em; white-space: nowrap; flex-shrink: 0;">{esc(title)}</h1>
<span style="flex-shrink: 0; max-width: 300px;">{st}</span>
<span style="flex-grow: 1;"></span>
{prim}
</div>
{f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.35; max-width: 900px; margin-top: -4px;">{esc(subtitle)}</div>' if subtitle else ''}
{controw}
{chipsrow}
</header>
{steps or ''}
<main data-scroll="{"1" if steps else "0"}" style="flex-grow: 1; padding: 18px 32px 22px; {"overflow-y: auto; min-height: 0;" if steps else ""} display: grid; grid-template-columns: minmax(0, 1fr); grid-auto-rows: max-content; align-content: start; gap: 18px; box-sizing: border-box; min-width: 0;">
{body}
</main>
{foot}
</div>
{extra_html()}
{E.G2_TOAST}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
{engine()}
</script>
</body>
</html>
'''
    open(os.path.join(E.P,fname),'w').write(html)
    _reset_screen(fname)  # engine() NÃO limpa o registro; sem isto, widgets/drawers vazam para a tela seguinte
    return fname

def mobile37(fid,title,sub,status,primary,body,fname=None,H=844,back='MB-01.dc.html',primary_href=None):
    """Tela móvel MB: cabeçalho simples, CTA grande, badge de demonstração; reseta o registro após gravar."""
    fname=fname or ffile(fid)
    E.HEIGHTS[fname]=_h(fname,H)
    E.MPARENT[fname]=back
    if primary_href: E.PHREF[fname]=primary_href
    E.mobile(fname,title,sub,status,primary,body)
    _reset_screen(fname)
    return fname

# ---------- vocabulário visual único ----------
_RED_WORDS=('impedid','bloquead','atrasad','conflito','vencid','reprovad','rejeitad','falha')
def selo(texto):
    """Condição (selo) de uma ordem/objeto: vermelho para impedimento/bloqueio/atraso/conflito; amarelo para o resto."""
    if not texto: return '—'
    t=texto.lower()
    return chip(texto,'red' if any(w in t for w in _RED_WORDS) else 'yellow')
ETAPA_COR={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray'}
def etapa(nome): return chip(nome,ETAPA_COR.get(nome,'gray'))

def farm_map(h=460,camada='Integrado',sel=None):
    """Mapa da fazenda em largura total: talhões (polígonos) e pivôs (círculos) com rótulo grande, cor e legenda pela camada."""
    GEO=[('T1','poly','30,30 290,22 300,205 40,215'),('T2','poly','315,22 560,28 555,200 318,206'),
         ('T4','poly','40,250 300,240 305,430 45,438'),('T3','poly','320,240 555,236 560,430 325,434'),
         ('P1','circ','685,118,88'),('P2','circ','890,118,82'),
         ('T7','poly','590,245 780,240 785,430 595,434'),('C1','poly','800,240 970,236 975,430 805,434')]
    L=LAYERS.get(camada,LAYERS['Integrado'])
    g=[]
    for tid,tp,geo in GEO:
        ck,leg=L['v'].get(tid,('none',''))
        fill,stroke=LCOR[ck]
        hatch=(ck=='cloud')
        wsel=' stroke-width="4"' if sel==tid else ' stroke-width="2"'
        fillattr=f'fill="url(#hatch)"' if hatch else f'fill="{fill}" fill-opacity="{".8" if ck not in ("none",) else "1"}"'
        if tp=='poly':
            pts=[tuple(map(float,p.split(','))) for p in geo.split()]
            cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
            g.append(f'<polygon points="{geo}" {fillattr} stroke="{stroke}"{wsel}/>')
        else:
            cx,cy,r=map(float,geo.split(','))
            g.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" {fillattr} stroke="{stroke}"{wsel}/>')
            g.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+r*0.7}" y2="{cy-r*0.7}" stroke="{stroke}" stroke-width="2"/>')
        g.append(f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-family="Sora, Manrope, sans-serif" font-size="34" font-weight="700" fill="#15201A" stroke="#fff" stroke-width="5" paint-order="stroke">{tid}</text>')
        if leg: g.append(f'<text x="{cx}" y="{cy+28}" text-anchor="middle" font-family="Manrope, sans-serif" font-size="12.5" font-weight="700" fill="#15201A" stroke="#fff" stroke-width="3.5" paint-order="stroke">{esc(leg)}</text>')
    svg=(f'<svg viewBox="0 0 1000 460" width="100%" height="{h}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Mapa da fazenda Santa Rita, camada {esc(camada)}" style="display: block; background: #DDE5D4; border-radius: 14px;">'
         '<defs><pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#C9CFCB"/><line x1="0" y1="0" x2="0" y2="10" stroke="#9E9E9E" stroke-width="4"/></pattern></defs>'
         '<rect x="0" y="0" width="1000" height="460" fill="#DDE5D4"/>'
         '<path d="M0 225 C 250 219, 520 231, 1000 225" stroke="#B9C6AE" stroke-width="10" fill="none"/>'
         + ''.join(g) + '</svg>')
    return svg
def map_legend(camada):
    L=LAYERS.get(camada,LAYERS['Integrado'])
    itens=' · '.join(f'<span style="color:{LCOR[k][1]}; font-weight:700;">■ {esc(t)}</span>' for k,t in L['leg'])
    return f'<div style="font-size: 11.5px; color: {MUTED};"><b style="color:{INK};">{esc(camada)}</b> · {esc(L["fonte"])} · {itens}</div>'
# cores por classe (paleta viva; nuvem hachurada, sem dado neutro)
LCOR={'ok':('#3FBF2A','#1E7A4C'),'good':('#0B7A1E','#0B5A16'),'lime':('#B5E61D','#5F7A0E'),'yellow':('#FFD500','#8A5A00'),
      'orange':('#FF6A00','#9A3F00'),'red':('#E4002B','#9E0A1F'),'gray':('#C9CFCB','#5B6660'),'blue':('#4FA3E0','#1E5F8F'),
      'navy':('#1E5F8F','#123A57'),'none':('#E9EEE6','#8A968E'),'cloud':('#C9CFCB','#6B6B6B'),'purple':('#9B7BD4','#5B3E94')}
LAYERS={
 'Integrado':{'fonte':'O.S. (PCP, 23/09 06:40), satélite 21/09 (nuvem 4%), solo campanha 2026',
   'v':{'T1':('ok','OS-0421 · 190/350 ha'),'T2':('ok','OS-0421 · mesma ordem'),'T4':('red','OS-0420 · impedida'),'T3':('gray','OS-0415 · encerrada'),
        'P1':('yellow','2 ordens · atenção'),'P2':('blue','água por política'),'T7':('none','mamão · sem ordem'),'C1':('none','café · granação')},
   'leg':[('ok','em execução/no prazo'),('yellow','atenção'),('red','impedida'),('blue','água por política'),('gray','encerrada'),('none','sem ordem aberta')]},
 'Satélite':{'fonte':'NDVI Sentinel-2 · cena 21/09 · nuvem 4% (C1 com nuvem) · escala da fazenda',
   'v':{'T1':('gray','pré-plantio · solo exposto'),'T2':('gray','pré-plantio · solo exposto'),'T4':('gray','pré-plantio'),'T3':('gray','colhido'),
        'P1':('good','NDVI 0,84 · vigor alto'),'P2':('ok','NDVI 0,76 · bom'),'T7':('lime','NDVI 0,66 · mancha 1,2 ha'),'C1':('cloud','nuvem · sem leitura')},
   'leg':[('good','> 0,82 vigor alto'),('ok','0,72–0,82 bom'),('lime','0,60–0,72 médio'),('yellow','0,45–0,60 atenção'),('red','< 0,30 falha'),('gray','sem cultura'),('cloud','nuvem (hachurado)')]},
 'Solo':{'fonte':'saturação por bases V% · 0–20 cm · campanha 2026 · laboratório Lab Solo Vale',
   'v':{'T1':('yellow','V 48%'),'T2':('ok','V 55%'),'T4':('red','V 41% · abaixo da meta'),'T3':('good','V 62%'),
        'P1':('ok','V 58%'),'P2':('good','V 60%'),'T7':('good','V 66%'),'C1':('yellow','V 52%')},
   'leg':[('red','< 45%'),('yellow','45–55%'),('ok','55–60%'),('good','≥ 60%')]},
 'MIP/MID':{'fonte':'vistorias de 20–22/09 · contagem × nível de controle da cultura',
   'v':{'T1':('none','sem cultura'),'T2':('none','sem cultura'),'T4':('orange','nematoide · VIS-011'),'T3':('none','colhido'),
        'P1':('red','percevejo 2,1/pano · NC 2'),'P2':('ok','abaixo do nível'),'T7':('yellow','ácaro · atenção'),'C1':('ok','abaixo do nível')},
   'leg':[('red','acima do nível de controle'),('orange','foco em investigação'),('yellow','atenção'),('ok','abaixo do nível'),('none','sem registro')]},
 'O.S./prazos':{'fonte':'O.S. do PCP · hoje 23/09',
   'v':{'T1':('ok','no prazo'),'T2':('ok','no prazo'),'T4':('red','atrasada · ativo bloqueado'),'T3':('gray','encerrada'),
        'P1':('orange','vence hoje'),'P2':('blue','irrigando hoje 18h'),'T7':('none','sem ordem'),'C1':('none','sem ordem')},
   'leg':[('red','atrasada'),('orange','vence hoje'),('yellow','até 3 dias'),('ok','no prazo'),('blue','irrigando'),('gray','encerrada')]},
 'Irrigação':{'fonte':'balanço hídrico 23/09 06:00 · sensores P1/P2 · estação Sede',
   'v':{'T1':('none','sequeiro'),'T2':('none','sequeiro'),'T4':('none','sequeiro'),'T3':('none','sequeiro'),
        'P1':('yellow','déficit 18 mm'),'P2':('blue','lâmina 10,81 mm · 62%'),'T7':('ok','gotejo em dia'),'C1':('none','sequeiro')},
   'leg':[('red','déficit crítico'),('yellow','déficit'),('ok','em dia'),('blue','irrigando'),('none','sequeiro')]},
 'Estádio':{'fonte':'ocupações e fenologia apontadas · variedade por parcela',
   'v':{'T1':('gray','pré-plantio · 58 W e 62 X'),'T2':('gray','pré-plantio · 58 W'),'T4':('gray','pré-plantio'),'T3':('none','colhido 12/09'),
        'P1':('purple','Feijão BRS · R5'),'P2':('ok','Milho · V10'),'T7':('yellow','Mamão · produção'),'C1':('orange','Café · granação')},
   'leg':[('gray','pré-plantio'),('ok','vegetativo'),('purple','reprodutivo'),('yellow','produção contínua'),('orange','enchimento/maturação'),('none','colhido')]},
 'Colheita/produtividade':{'fonte':'romaneios conferidos e previsões publicadas · safra 2026/27',
   'v':{'T1':('none','—'),'T2':('none','—'),'T4':('none','—'),'T3':('good','142 sc/ha · realizado'),
        'P1':('lime','previsto 48 sc/ha'),'P2':('lime','previsto 180 sc/ha'),'T7':('ok','9,6 t A/semana'),'C1':('lime','previsto 38 sc/ha')},
   'leg':[('good','realizado acima da meta'),('ok','realizado na meta'),('lime','previsão'),('red','abaixo da meta'),('none','sem dado')]},
 'Custos':{'fonte':'custo realizado R$/ha × orçado · fechamento parcial 22/09',
   'v':{'T1':('ok','R$ 1.240/ha · no orçado'),'T2':('ok','R$ 1.180/ha'),'T4':('red','R$ 2.050/ha · +18%'),'T3':('ok','R$ 3.960/ha · fechado'),
        'P1':('yellow','R$ 3.900/ha · +6%'),'P2':('ok','R$ 3.400/ha'),'T7':('ok','R$ 21 mil/ha/ano'),'C1':('ok','R$ 9,8 mil/ha')},
   'leg':[('ok','dentro do orçado'),('yellow','até +10%'),('red','acima de +10%')]},
}

def tabs(opts,contents,active=0,label='Visão',chips=False):
    """Abas reais: devolve (barra, painéis). Cada painel só aparece com sua aba ativa (sc-if sobre o estado do seg)."""
    from engine import seg_buttons, SEG_ON, SEG_OFF
    on=off=None
    if chips:
        on=f'font-family: inherit; font-size: 11.5px; font-weight: 700; padding: 5px 11px; border-radius: 999px; border: 1px solid {INK}; background: {INK}; color: #fff; cursor: pointer; white-space: nowrap;'
        off=f'font-family: inherit; font-size: 11.5px; font-weight: 700; padding: 5px 11px; border-radius: 999px; border: 1px solid {LINE}; background: {SURF}; color: {INK}; cursor: pointer; white-space: nowrap;'
    s,bs=seg_buttons(opts,active,on=on,off=off)
    bar=(f'<div role="tablist" aria-label="{esc(label)}" style="display: inline-flex; flex-wrap: wrap; gap: {6 if chips else 2}px; '
         + ('' if chips else f'padding: 3px; border-radius: 999px; background: {GRAYS};') + '">' + ''.join(bs) + '</div>')
    panes=''.join(f'<sc-if value="{HL(s+"_v"+str(i))}" hint-placeholder-val="{HL("true") if i==active else HL("false")}">{c}</sc-if>' for i,c in enumerate(contents))
    return bar,panes


def steps_state(names,pre='stp',label='Etapas do processo'):
    """Faixa de etapas (estado da tela): colunas iguais que sempre cabem na largura; destaque, impedimento e navegação vêm do JS (g2steps)."""
    n=len(names); items=''
    for i,t in enumerate(names,1):
        items+=(f'<button type="button" onClick="{{{{{pre}{i}_go}}}}" aria-current="{{{{{pre}{i}_cur}}}}" title="{esc(t)}" style="{{{{{pre}{i}_st}}}}">'
                f'<span style="{{{{{pre}{i}_bst}}}}">{i}</span><span style="display: flex; flex-direction: column; min-width: 0;"><span style="{{{{{pre}{i}_tst}}}}">{esc(t)}</span>'
                f'<sc-if value="{{{{{pre}{i}_hasWhy}}}}" hint-placeholder-val="{{{{false}}}}"><span style="font-size: 11px; font-weight: 700; color: {RED}; line-height: 1.2;">{{{{{pre}{i}_why}}}}</span></sc-if></span></button>')
    return (f'<nav aria-label="{esc(label)}" style="position: sticky; top: 0; z-index: 30; background: {SURF}; border-bottom: 1px solid {LINE}; box-shadow: 0 6px 12px -10px rgba(21,32,26,.25); padding: 5px 24px 6px;">'
            f'<div style="font-size: 10px; font-weight: 800; letter-spacing: .08em; color: {MUTED}; text-transform: uppercase; padding: 0 8px 3px;">{esc(label)}</div>'
            f'<div style="display: grid; grid-template-columns: repeat({n}, minmax(0, 1fr)); gap: 4px;">{items}</div></nav>')
