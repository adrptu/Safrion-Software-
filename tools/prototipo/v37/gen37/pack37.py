# -*- coding: utf-8 -*-
"""PDF navegável v3.7: capa+índice, uma página por tela (tamanho do quadro), apêndice de formulários e ações; links internos + marcadores."""
import json, os, re, html, subprocess, shutil
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, ArrayObject, NullObject
from navdata import all_screens, CAT
HERE=os.path.dirname(os.path.abspath(__file__)); PROJ=os.path.join(HERE,'project')
PR=os.path.join(HERE,'_print'); PDFD=os.path.join(HERE,'_pdf'); os.makedirs(PR,exist_ok=True); os.makedirs(PDFD,exist_ok=True)
shutil.copy(os.path.join(HERE,'..','..','telas','pack','measure','support.js'),os.path.join(PR,'support.js'))
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
C=json.load(open(os.path.join(PROJ,'canvas.json'))); B=C['boards']; ORDER=[n for n in C['order'] if n in B]
D=all_screens()
rows=sorted([(v.get('page','menu'),v['y'],v['text']) for v in C['notes'].values() if v.get('kind')=='title1'])
def row_of(n):
    y=C['boards'][n]['y']; pg=C['boards'][n].get('page','menu'); t='Índice'
    for rp,ry,rt in rows:
        if rp==pg and y>=ry-300: t=rt
    return t
def pdf(src,out,force=False):
    if force or not os.path.exists(out):
        subprocess.run([CH,'--headless=new','--disable-gpu','--no-pdf-header-footer','--virtual-time-budget=9000','--run-all-compositor-stages-before-draw',f'--print-to-pdf={out}','file://'+src],capture_output=True,timeout=180)
    return os.path.exists(out)
import base64, time, socket
from cdp import Chrome
def _free():
    s=socket.socket(); s.bind(('127.0.0.1',0)); x=s.getsockname()[1]; s.close(); return x
FULL="(()=>{const st=document.createElement('style'); st.textContent='[data-root]{height:auto!important;overflow:visible!important} main[data-scroll=\\\"1\\\"]{overflow:visible!important;min-height:auto!important;flex-grow:0!important} *{box-shadow:none!important;break-inside:auto!important;break-before:auto!important;break-after:auto!important;page-break-inside:auto!important}'; document.head.appendChild(st); return 1;})()"
PRE_ETAPAS={'SAF.dc.html':"(()=>{const b=[...document.querySelectorAll('button')].find(b=>/^Abrir safra/.test(b.innerText.trim())); if(b) b.click();})()",
            'CMP.dc.html':"(()=>{const b=[...document.querySelectorAll('button,a')].find(b=>/SOL-2026-07|Abrir (a )?solicita|Escolher|Abrir safra/.test(b.innerText.trim())); if(b && b.tagName==='BUTTON') b.click();})()"}
PAGES=[]  # (nome_lógico, arquivo_pdf, tela)
port=_free(); srv=subprocess.Popen(['python3','-m','http.server',str(port),'--bind','127.0.0.1','--directory',os.path.join(HERE,'_render')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=_free())
def _print(n,out,w):
    c.js(FULL); time.sleep(.4)
    h=c.js("Math.ceil(Math.max(document.querySelector('[data-root]')?document.querySelector('[data-root]').scrollHeight:0, document.documentElement.scrollHeight))")
    c.size(w,min(h,14000)); time.sleep(.3)
    c.call('Emulation.setEmulatedMedia',{'media':'screen'})
    d=c.call('Page.printToPDF',{'printBackground':True,'paperWidth':w/96,'paperHeight':(min(h,14000)+24)/96,'marginTop':0,'marginBottom':0,'marginLeft':0,'marginRight':0,'preferCSSPageSize':False,'pageRanges':'1'},timeout=120)
    open(out,'wb').write(base64.b64decode(d['data']))
try:
    for n in ORDER:
        w=B[n]['w']; c.size(w,1000); c.goto(f'http://127.0.0.1:{port}/{n}',wait=1.3)
        k=c.js("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button').length") or 0
        if k:
            if n in PRE_ETAPAS: c.js(PRE_ETAPAS[n]); time.sleep(.5)
            for i in range(k):
                c.goto(f'http://127.0.0.1:{port}/{n}',wait=1.1)
                if n in PRE_ETAPAS and i>0: c.js(PRE_ETAPAS[n]); time.sleep(.5)
                c.js(f"document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[{i}].click()"); time.sleep(.5)
                out=os.path.join(PDFD,n.replace('.dc.html',f'__e{i+1}.pdf')); _print(n,out,w); PAGES.append((n if i==0 else f'{n}#e{i+1}',out,n))
        else:
            out=os.path.join(PDFD,n.replace('.dc.html','.pdf')); _print(n,out,w); PAGES.append((n,out,n))
finally:
    c.close(); srv.terminate()
print('páginas de tela impressas:',len(PAGES))
# ---- capa/índice e apêndice ----
PAGE={}; p=2
for nm,_,tela in PAGES:
    if tela not in PAGE: PAGE[tela]=p
    p+=1
CSS="""<style>@page{size:1440px 2200px;margin:0}html,body{margin:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:Manrope,Helvetica,Arial,sans-serif;color:#15201A;background:#F4F6F3}.w{padding:52px 60px}
h1{font-size:38px;margin:0 0 6px;letter-spacing:-.02em}h2{font-size:19px;margin:24px 0 8px}.sub{color:#5B6660;font-size:15px;line-height:1.5;margin-bottom:10px}
.grid{columns:4;column-gap:26px}.g{break-inside:avoid;margin:0 0 16px}.g b{display:block;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#1E7A4C;margin-bottom:5px}
.g a{display:block;color:#15201A;text-decoration:none;font-size:13px;padding:3px 0;border-bottom:1px solid #E3E7E2}.g a span{color:#8A948E;font-size:11.5px}
ul{margin:4px 0 0 18px;padding:0;font-size:13.5px;line-height:1.55;color:#33413A}
.f{break-inside:avoid;background:#fff;border:1px solid #DDE3DF;border-radius:12px;padding:10px 14px;margin:0 0 10px}.f h3{margin:0 0 2px;font-size:14px}
.f p{margin:0 0 4px;color:#5B6660;font-size:12px}.f .a{font-size:12.3px;margin:2px 0}.f .a i{color:#1E7A4C;font-style:normal;font-weight:700}</style>"""
groups={}
for n in ORDER: groups.setdefault(row_of(n),[]).append(n)
idx=''.join(f'<div class="g"><b>{html.escape(g)}</b>'+''.join(f'<a href="{n}">{html.escape(n.replace(".dc.html",""))} · {html.escape(D[n]["titulo"][:48])} <span>· p. {PAGE[n]}</span></a>' for n in ns)+'</div>' for g,ns in groups.items())
conv=['Uma página por tela, no estado inicial do cenário de demonstração. Botões e linhas que levam a outra tela são links: clique para pular à página daquela tela (como o Play do Canvas).',
 'Ações que executam (liberar, aprovar, receber devolução, chamar próximo caminhão…) mostram resultado na própria tela no protótipo interativo; aqui estão listadas no apêndice com o resultado exibido.',
 'Formulários (painéis laterais) também estão no apêndice, com campos e botão de confirmação.',
 'O PDF complementa o protótipo interativo do Canvas; não substitui suas ações e transições.',
 'Fonte oficial: PRD v3.7 — 23/09/2026. Dados fictícios: Fazenda Santa Rita, safra 2026/27, hoje = 23/09/2026.']
cover=f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">{CSS}</head><body><div class="w">
<h1>Do Talhão à O.S. · protótipo navegável v3.7</h1><div class="sub">{len(ORDER)} telas · 98 famílias do PRD v3.7 · etapa: validação do proprietário</div>
<ul>{''.join(f'<li>{html.escape(c)}</li>' for c in conv)}</ul>
<h2>Índice</h2><div class="grid">{idx}<div class="g"><b>Apêndice</b><a href="Apendice.dc.html">Ações com efeito e formulários, por tela <span>· p. {p}</span></a></div></div></div></body></html>"""
open(os.path.join(PR,'Capa.dc.html'),'w').write(cover)
blocks=[]
for n in ORDER:
    v=D[n]; fs=[f for f in v['formularios'] if f['titulo'] or f['campos']]
    if not v['acoes'] and not fs: continue
    a=''.join(f'<div class="a"><i>{html.escape(t)}</i> → {html.escape(m)}</div>' for t,m in v['acoes'])
    f=''.join(f'<div class="a"><i>Formulário: {html.escape(x["titulo"] or "(sem título)")}</i> — {html.escape(", ".join(x["campos"]) or "leitura")}{(" · confirmar: "+html.escape(x["confirmar"])) if x["confirmar"] else ""}</div>' for x in fs)
    blocks.append(f'<div class="f"><h3><a href="{n}" style="color:#15201A;text-decoration:none;">{html.escape(n.replace(".dc.html",""))} · {html.escape(v["titulo"])}</a></h3><p>p. {PAGE[n]}</p>{a}{f}</div>')
ap=f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">{CSS}</head><body><div class="w"><h1>Apêndice · ações com efeito e formulários</h1>
<div class="sub">O que cada botão que executa mostra como resultado no protótipo interativo, e os campos de cada painel de formulário.</div><div style="columns:2;column-gap:20px">{''.join(blocks)}</div></div></body></html>"""
open(os.path.join(PR,'Apendice.dc.html'),'w').write(ap)
pdf(os.path.join(PR,'Capa.dc.html'),os.path.join(PDFD,'_capa.pdf'),True); pdf(os.path.join(PR,'Apendice.dc.html'),os.path.join(PDFD,'_apendice.pdf'),True)
# ---- juntar ----
seq=[('Capa.dc.html',os.path.join(PDFD,'_capa.pdf'))]+[(nm,out) for nm,out,_ in PAGES]+[('Apendice.dc.html',os.path.join(PDFD,'_apendice.pdf'))]
w=PdfWriter(); start={}
for name,path in seq:
    start[name]=len(w.pages)
    rd=PdfReader(path)
    pages=rd.pages if name in ('Apendice.dc.html',) else rd.pages[:1]
    for pg in pages: w.add_page(pg)
ok=miss=0; missing=set()
for pg in w.pages:
    for a in (pg.get('/Annots') or []):
        ao=a.get_object(); act=ao.get('/A')
        if not act or '/URI' not in act: continue
        name=os.path.basename(str(act['/URI']).split('#')[0])
        if name in start:
            ao[NameObject('/Dest')]=ArrayObject([w.pages[start[name]].indirect_reference,NameObject('/XYZ'),NullObject(),NullObject(),NullObject()]); del ao['/A']; ok+=1
        elif name.endswith('.dc.html'): miss+=1; missing.add(name)
w.add_outline_item('Capa e índice',start['Capa.dc.html'])
for g,ns in groups.items():
    par=w.add_outline_item(g,start[ns[0]])
    for n in ns:
        it=w.add_outline_item(f'{n.replace(".dc.html","")} · {D[n]["titulo"][:60]}',start[n],parent=par)
        for nm,_,tela in PAGES:
            if tela==n and '#e' in nm: w.add_outline_item('Etapa '+nm.split('#e')[1],start[nm],parent=it)
w.add_outline_item('Apêndice · ações e formulários',start['Apendice.dc.html'])
w.page_mode='/UseOutlines'
w.add_metadata({'/Title':'Do Talhão à O.S. · protótipo navegável v3.7','/Subject':f'{len(ORDER)} telas com links internos, índice e apêndice'})
try: w.compress_identical_objects(remove_identicals=True,remove_orphans=True)
except Exception as e: print('compressão:',e)
out=os.path.join(HERE,'..','entrega','Do-talhao-a-OS_v3.7_prototipo-navegavel.pdf')
with open(out,'wb') as f: w.write(f)
print('páginas',len(w.pages),'| links internos',ok,'| para páginas inexistentes',miss,sorted(missing)[:5],'| MB',round(os.path.getsize(out)/1e6,1))
