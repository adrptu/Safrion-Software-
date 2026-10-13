# -*- coding: utf-8 -*-
import json, os, datetime, importlib, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import engine as E
from ui37 import CAT, MAPA, ffile, BEN_PUBLICADO
AREAS=['indice','inicio']+sorted(f[:-3] for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'areas'))
        if f.endswith('.py') and f[:-3] not in ('indice','inicio','__init__'))
ORDEM_LINHAS=[('Início',0),('Agronomia',1),('Planejamento',2),('Campo',3),('Irrigação',4),('Máquinas e manutenção',5),
 ('Colheita e pós-colheita',6),('Suprimentos',7),('Comercial',8),('Logística',9),('Gestão e resultados',10),
 ('Cadastros',11),('Configurações',12),('App móvel',13),('Portal do parceiro',14),('Onboarding e Backoffice',15),('Produção',16)]   # Produção: o BEN fora da navegação (v55)
BOARD_META={}  # fname -> (title, W, H, row)
def registrar(fname,title,W,H,row): BOARD_META[fname]=(title,W,H,row)
import traceback
FALHAS=[]
for a in AREAS:
    try:
        m=importlib.import_module(f'areas.{a}')
        if hasattr(m,'build'): m.build()   # módulos auxiliares (ex.: cad_*, chamados por cadastros.build) não têm build próprio
    except Exception as ex:
        FALHAS.append((a,repr(ex))); traceback.print_exc()
if FALHAS: print('MÓDULOS COM FALHA:',FALHAS)
# telas que deixaram de ser geradas (01/10: O.S. sem revisão; o agrônomo libera na tela O.S.): o arquivo de um build anterior sai do project/ e do canvas
# 06/10 (colheita, D-16): MB-10det sai; pesar e receber ficam em Produção › Cargas e recebimento (CARGA)
# 06/10 (PLAT-01, PLAT-D02): CF-05det, BO-01det, BO-02det, BO-03 e BO-03det viram o detalhe da linha; BO-04 sai. A tela antiga sai também do _render/ (o montar_render só copia)
# 06/10 (CONF-01, CONF-D01, CONF-D20): CF-02 e CF-02det saem (o bloco Alçadas fica no CF-01); CF-03det sai (o conflito é o CMD-09 da O.S.)
for _f in ('IN-02det.dc.html','IN-02x-os0420.dc.html','CF-05det.dc.html','CF-02.dc.html','CF-02det.dc.html','CF-03det.dc.html','BO-01det.dc.html','BO-02det.dc.html','BO-03.dc.html','BO-03det.dc.html','BO-04.dc.html','MB-10det.dc.html'):
    for _d in (E.P,os.path.join(os.path.dirname(E.P),'_render')):
        if os.path.exists(os.path.join(_d,_f)): os.remove(os.path.join(_d,_f))
# tudo que foi escrito no project/ com meta conhecida entra no canvas
from ui37 import HEIGHTS37, _h
from ui37 import menu_item, MENU2
def _wh(fname):
    import re as _re
    s=open(os.path.join(E.P,fname)).read()
    m=_re.search(r'"\$preview":\{"width":(\d+),"height":(\d+)\}',s)
    return int(m.group(1)),int(m.group(2))
def _interactive(fname):
    s=open(os.path.join(E.P,fname)).read(); return ('onClick=' in s) or ('href=' in s)
# páginas de redirecionamento (PCM simplificado, D-24): PM, MA-01..05 e MA-04det levam ao endereço novo da tela MA; ficam fora do canvas e do Índice
from areas.maquinas import REDIRECIONA
files=sorted(f for f in os.listdir(E.P) if f.endswith('.dc.html') and f not in REDIRECIONA)
boards={}; order=[]; notes={}
# ---- página 1 · menu vigente ----
VIS_ROWS=[('Índice',['Main.dc.html']),('Mapa',['IN-04.dc.html'])]+[(nome,list(dict.fromkeys(h.split('#')[0] for _,h in items))) for nome,ic,items in MENU2 if nome!='Mapa']   # visões da mesma tela (Manutenção) = um quadro
# App de campo (prioridade de teste com os primeiros clientes, DEC-2609-13): mesmo cenário da O.S. e do Estoque
# PCM S4 (§1, §3.7): MB-09 "Máquina" e MB-09det "Ordem de manutenção" deixam de ser ocultos: ligados ao MB-01, gravam no cenário e funcionam sem sinal
VIS_ROWS.append(('App de campo',['MB-01.dc.html','MB-02.dc.html','MB-03.dc.html','MB-04.dc.html','MB-05.dc.html','MB-07.dc.html','MB-10.dc.html',
                                 'MB-09.dc.html','MB-09det.dc.html']))   # MB-07 e MB-10 no estado (colheita, 06/10)
detalhes={'Agrícola':['CA-01det.dc.html','CA-01x-os0420.dc.html','OS-0424-app.dc.html','OS-0424-ficha.dc.html','AG-01det.dc.html','IR-02.dc.html','IR-03.dc.html','IR-03det.dc.html','IR-04.dc.html'],
          'Produção':['BEN.dc.html'] if BEN_PUBLICADO else [],'Cadastros':[f for f in files if f.startswith('CD-') and 'det' in f]}   # v55: BEN só publicado (ui37.BEN_PUBLICADO)
y=0; placed=set()
for nome,fs in VIS_ROWS:
    fs=[f for f in fs+detalhes.get(nome,[]) if f in files]
    if not fs: continue
    x=0; hmax=0
    notes['v_'+str(len(notes))]={'x':0,'y':y-240,'text':nome,'kind':'title1','maxW':1840,'page':'menu'}
    for f in fs:
        w,h=_wh(f); boards[f]={'x':x,'y':y,'w':w,'h':h,'title':CAT.get(f[:5],{}).get('titulo',f.replace('.dc.html','')) if f[:5] in CAT else f.replace('.dc.html',''),'is_interactive':_interactive(f),'page':'menu'}
        if f=='Main.dc.html': boards[f]['title']='Índice central · comece aqui'
        if f=='OS-0424-app.dc.html': boards[f]['title']='Agrícola › Ordem de Serviço › OS-0424 · ficha no app (funciona sem internet)'
        if f=='OS-0424-ficha.dc.html': boards[f]['title']='Agrícola › Ordem de Serviço › OS-0424 · ficha impressa'
        if f=='BEN.dc.html': boards[f]['title']='Produção › Recebimento e beneficiamento › Beneficiamento'   # tela irmã de Cargas (BEN-D14)
        if nome=='App de campo': boards[f]['title']='App de campo › '+boards[f]['title']
        for nm,ic,items in MENU2:
            for l,hh in items:
                if hh==f: boards[f]['title']=f'{nm} › {l}'
        order.append(f); placed.add(f); x+=w+80; hmax=max(hmax,h)
    y+=hmax+120+260
# ---- página 2 · módulos ocultos (preservados) ----
rows={}
for fname in files:
    if fname in placed: continue
    base=fname[:5]
    area=(MAPA.get(base) or {}).get('area') or {'MB':'App móvel','PT':'Portal do parceiro','ON':'Onboarding e Backoffice','BO':'Onboarding e Backoffice'}.get(base[:2],'Outros')
    if fname=='BEN.dc.html': area='Produção'   # v55: Beneficiamento fora da navegação até a rodada 3 (BEN_PUBLICADO=False em ui37); fora do catálogo, ganha linha própria
    rows.setdefault(area,[]).append(fname)
y=0
for n,r in ORDEM_LINHAS:
    fs=rows.get(n)
    if not fs: continue
    x=0; hmax=0; nid=f'o_{r}'
    notes[nid]={'x':0,'y':y-240,'text':n+' · oculto no menu','kind':'title1','maxW':1840,'page':'ocultos'}
    for f in fs:
        w,h=_wh(f); base=f[:5]; tt=CAT.get(base,{}).get('titulo',base); suf=f[5:].replace('.dc.html','')
        boards[f]={'x':x,'y':y,'w':w,'h':h,'title':f'{base}{(" · "+suf) if suf else ""} · {tt}','is_interactive':_interactive(f),'page':'ocultos'}
        if f=='BEN.dc.html': boards[f]['title']='Produção › Beneficiamento · fora da navegação até a rodada 3 do BEN (BEN_PUBLICADO)'
        order.append(f); x+=w+80; hmax=max(hmax,h)
    notes[nid]['maxW']=max(x-80,800)
    y+=hmax+120+260
canvas={'v':3,'createdOnFiles':{'v':1,'at':datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')},
 'title':'Do Talhão à O.S. · protótipo (PRD v3.9)','launch':{'view':'canvas','page':'menu'},
 'pages':[{'id':'menu','name':'Protótipo · menu vigente'},{'id':'ocultos','name':'Módulos ocultos (preservados)'}],
 'boards':boards,'order':order,'notes':notes,'designSystems':[]}
json.dump(canvas,open(os.path.join(E.P,'canvas.json'),'w'),ensure_ascii=False,indent=1)
print(len(boards),'artboards →',E.P,'· menu vigente:',len(placed),'· ocultos:',len(boards)-len(placed))
if FALHAS: sys.exit(1)   # build com módulo falho não sai com 0 (portabilidade/CI)
