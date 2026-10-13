# -*- coding: utf-8 -*-
"""Teste CDP · celular operável sem redesenho do desktop (revisão QUALIDADE-ARTEFATO-20261003-FLUXO, item 3).
Faixa de etapas em tela estreita: etapa atual em texto ("Etapa 2 de 6 · Confira a demanda"), ‹ › e lista completa sob demanda
(toque e teclado); título e comando principal na tela; tabela em região rolável; menu aberto passa por cima do conteúdo;
contexto e rascunho preservados ao trocar de etapa e de zoom; painel lateral cobre a faixa.
Larguras: 390 px (quadro de 390), 325 px (quadro do site com a janela de 390) e zoom de 200 % (1440 px → 720 px CSS, escala 2).
Uso: python3 etapas_celular_test.py              celular (≈ 50 s, capturas em _probe/q_celular_<TAG>_*.png, TAG=depois)
     python3 etapas_celular_test.py complemento  listas alcançáveis, títulos de bloco, CD-07, tela baixa, folha de etapas (≈ 60 s)
     python3 etapas_celular_test.py desktop A B  1440 px igual à base (ANTES_DIR, padrão ../gen37_antes/_render), menu aberto e
                                                 recolhido, nas telas A:B da lista ordenada de todas as telas (sem A B: todas)
     python3 etapas_celular_test.py faixa        varredura de largura (1400 → 300 px) em todas as telas com etapas
CDP_PORT=<porta> anexa a um Chrome já aberto (máquina carregada)."""
import sys, os, time, subprocess, json, glob
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import urllib.request, tempfile, shutil
from cdp import Chrome, WS, CH
from journeys import free
from cadc_lib import ERRS
# ---- medidas de tela estreita: sobreposição/vazamento entre etapas, título e comandos fora da tela, conteúdo cortado, painel sobre a faixa ----
MEDIR = r"""(()=>{
 const sr=document.createElement('style'); sr.textContent='.etp-sr{display:none!important}'; document.head.appendChild(sr);   // texto só para leitor de tela (recorte de 1 px) não conta como texto na tela
 try{
 const vw=innerWidth, vh=innerHeight, n=s=>(s||'').replace(/\s+/g,' ').trim();
 const vis=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'&&cs.opacity!=='0'; };
 const out={vw,vh,hscroll:document.documentElement.scrollWidth>vw+1};
 const nav=document.querySelector('.etp');
 out.temEtapas=!!nav;
 if(nav){
  const its=[...nav.querySelectorAll('.etp-itens>*')].filter(vis);
  const lst=nav.querySelector('.etp-itens'); const folha=!!lst&&getComputedStyle(lst).position==='fixed';
  const nr=(folha?lst:nav).getBoundingClientRect(); out.navH=Math.round(nav.getBoundingClientRect().height); out.navTxt=n(nav.innerText); out.folha=folha;
  const linhas=its.map(e=>{ const rg=document.createRange(); rg.selectNodeContents(e); return [...rg.getClientRects()].filter(r=>r.width>0.5&&r.height>0.5); });
  const box=its.map(e=>e.getBoundingClientRect());
  const vaza=[]; its.forEach((e,i)=>{ const b=box[i]; if(linhas[i].some(r=>r.right>b.right+1.5||r.left<b.left-1.5||r.bottom>b.bottom+1.5)||b.right>nr.right+1||b.left<nr.left-1) vaza.push(n(e.innerText).slice(0,40)); });
  let sob=0; for(let i=0;i<its.length;i++) for(let j=i+1;j<its.length;j++){ for(const a of linhas[i]) for(const b of linhas[j]){ const w=Math.min(a.right,b.right)-Math.max(a.left,b.left), h=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top); if(w>1&&h>1){ sob++; } } }
  out.etapasVis=its.length; out.vazam=vaza; out.sobrepoe=sob;
  const at=nav.querySelector('.etp-atual'); out.progresso=(at&&vis(at))?n(at.innerText):'';
  const setas=[...nav.querySelectorAll('[aria-label^="Etapa anterior"],[aria-label^="Próxima etapa"]')].filter(vis).map(e=>e.getAttribute("aria-label").split(":")[0]); out.setas=setas;
 }
 const h1=document.querySelector('header h1');
 if(h1){ const r=h1.getBoundingClientRect(); out.h1=n(h1.innerText); out.h1Cortado=(r.right>vw+1)||(h1.scrollWidth>h1.clientWidth+1); }
 const hd=document.querySelector('header');
 out.headerFora=hd?[...hd.querySelectorAll('*')].filter(e=>vis(e)&&e.children.length===0&&n(e.innerText||'')&&e.getBoundingClientRect().right>vw+1).map(e=>n(e.innerText).slice(0,30)).slice(0,6):[];
 const m=document.querySelector('main[data-scroll]');
 if(m){ const mr=m.getBoundingClientRect();
  // região rolável é uma caixa interna (tabela); o main rolando de lado não conta (senão tudo passa por vacuidade)
  const rolavel=e=>{ for(let p=e.parentElement;p&&p!==m;p=p.parentElement){ const ox=getComputedStyle(p).overflowX; if((ox==='auto'||ox==='scroll')&&p.scrollWidth>p.clientWidth) return true; } return false; };
  out.mainLado=m.scrollWidth>m.clientWidth+1;
  const corte=[...m.querySelectorAll('*')].filter(e=>vis(e)&&(e.children.length===0||e.matches('button,a,input,select,textarea'))&&(n(e.innerText||e.value||'')||e.matches('input,select,svg'))).filter(e=>{ const r=e.getBoundingClientRect(); return (r.right>mr.right+1||r.left<mr.left-1)&&!rolavel(e); });
  out.cortados=corte.length; out.cortadosEx=corte.slice(0,5).map(e=>n(e.innerText||e.value||e.tagName).slice(0,30));
  const tabs=[...m.querySelectorAll('[role=table]')].filter(vis); out.tabelas=tabs.length;
  const fol=[...m.querySelectorAll('*')].filter(e=>e.getClientRects().length&&[...e.childNodes].some(x=>x.nodeType===3&&x.textContent.trim())&&!e.closest('[role=table]'));
  const RR=fol.map(e=>{const rg=document.createRange(); rg.selectNodeContents(e); return [...rg.getClientRects()].filter(r=>r.width>1);}); const sm=[];
  for(let i=0;i<fol.length;i++) for(let j=i+1;j<fol.length;j++){ if(fol[i].contains(fol[j])||fol[j].contains(fol[i])) continue; for(const a of RR[i]) for(const b of RR[j]){ const w=Math.min(a.right,b.right)-Math.max(a.left,b.left), h=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top); if(w>2&&h>2) sm.push(n(fol[i].innerText).slice(0,25)+' × '+n(fol[j].innerText).slice(0,25)); } }
  out.textoSobreTexto=[...new Set(sm)].slice(0,4);
  out.tabelasRolam=tabs.map(t=>{ for(let p=t;p&&p!==m;p=p.parentElement){ const ox=getComputedStyle(p).overflowX; if(ox==='auto'||ox==='scroll') return true; } return false; });
 }
 return out; } finally { sr.remove(); } })()"""

# painel lateral aberto: o ponto central da faixa de etapas (ou do cabeçalho) deve cair no painel/fundo do painel, não na faixa
COBRE = r"""(()=>{ const d=[...document.querySelectorAll('aside[role=dialog]')].find(a=>a.getBoundingClientRect().width>0); if(!d) return 'sem painel';
 const nav=document.querySelector('.etp'); const alvo=nav||document.querySelector('header');
 const r=alvo.getBoundingClientRect(); const pts=[[r.left+8,r.top+r.height/2],[r.left+r.width/2,r.top+r.height/2],[r.right-8,r.top+r.height/2]];
 const fora=pts.filter(([x,y])=>{ const e=document.elementFromPoint(x,y); return e&&alvo.contains(e); });
 const ar=d.getBoundingClientRect(); return {painelW:Math.round(ar.width),painelX:Math.round(ar.left),faixaVisivelSobre:fora.length,vw:innerWidth}; })()"""
# ---- Chrome: anexa a um já aberto (CDP_PORT) ou abre um novo com espera longa (máquina carregada) ----
class ChromeAnexo(Chrome):
    def __init__(self,port=None,w=1440,h=900,espera=90):
        self.p=None; self.dir=None; self.alvo=None
        porta=os.environ.get('CDP_PORT')
        if porta: self.port=int(porta)
        else:
            from journeys import free
            self.port=port or free(); self.dir=tempfile.mkdtemp(prefix='cdp_')
            self.p=subprocess.Popen([CH,'--headless=new','--disable-gpu','--hide-scrollbars',f'--remote-debugging-port={self.port}',f'--user-data-dir={self.dir}',f'--window-size={w},{h}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        fim=time.time()+espera
        while True:
            try: urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json/version',timeout=5); break
            except Exception:
                if time.time()>fim: raise
                time.sleep(0.5)
        req=urllib.request.Request(f'http://127.0.0.1:{self.port}/json/new?about:blank',method='PUT')
        t=json.load(urllib.request.urlopen(req,timeout=30)); self.alvo=t['id']
        self.ws=WS(t['webSocketDebuggerUrl']); self.i=0
        self.call('Page.enable'); self.call('Runtime.enable')
    def close(self):
        try:
            if self.alvo: urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json/close/{self.alvo}',timeout=10)
        except Exception: pass
        if self.p:
            try: self.p.terminate(); self.p.wait(5)
            except Exception: pass
        if self.dir: shutil.rmtree(self.dir,ignore_errors=True)
TAG=os.environ.get('TAG','depois'); MODO=sys.argv[1] if len(sys.argv)>1 else 'celular'
PROBE=os.environ.get('PROBE_DIR') or os.path.join(HERE,'_probe'); os.makedirs(PROBE,exist_ok=True)
def serve(d):
    p=free(); s=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',d],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return p,s
OK=[]; FAIL=[]
def chk(nome,cond,info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,('' if cond else str(info)[:900]),flush=True)
p,srv=serve(os.path.join(HERE,'_render')); srv2=None; time.sleep(.6)
c=None
NOMES={'CMP':['Escolha a safra','Confira a demanda','Solicite cotações','Compare propostas','Aprove a compra','Acompanhe a entrega'],
       'SAF':['Escolha a safra'],'PA':['Escolha o plano'],'EST':['Confira recebimentos'],'IR-02':['Confira a necessidade','Programe a irrigação']}   # PCM simplificado (S1): MA-01 sai das faixas (tela única MA, sem etapas)
GUIADO=('CMP','SAF','PA')   # progresso informativo; EST, IR e MA são telas/seções de trabalho paralelo (navegação, sem número de etapa)
ATUAL={'CMP':(1,6),'SAF':(1,4),'PA':(1,3),'EST':(1,6),'IR-02':(2,4)}
P8=['CMP','SAF','PA','EST','OS','IR-02','MA','AG-07']   # MA: a tela única da Manutenção (sem faixa) segue nos itens 3 e 4
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a,label')].filter(e=>e.getClientRects().length); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
try:
    c=ChromeAnexo(); J=c.js; c.call('Page.addScriptToEvaluateOnNewDocument',{'source':ERRS})
    def vp(w,h,d=1): c.call('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':d,'mobile':False}); time.sleep(.25)
    def abre(pg,w=390,h=844,d=1,rec='1'):
        ERRL.extend(errs()); vp(w,h,d); J(f"localStorage.setItem('safrion.menuRecolhido','{rec}')"); c.goto(f'http://127.0.0.1:{p}/{pg}.dc.html',wait=.6); return J(MEDIR)
    ERRL=[]; errs=lambda: J("(window.__errs||[]).filter(e=>e.indexOf(\"reading 'g2toast'\")<0)") or []
    def shot(nome): c.shot(os.path.join(PROBE,f'q_celular_{TAG}_{nome}.png'))
    def clk(t,root=None,w=.45): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(w); return r
    vp(1440,900); c.goto(f'http://127.0.0.1:{p}/Main.dc.html',wait=.5)
    if MODO=='celular':
        # 1-3 · as oito telas a 390 px (menu recolhido, como na revisão)
        med={}
        for pg in P8: med[pg]=abre(pg); shot(f'{pg}_390')
        et=[pg for pg in P8 if med[pg]['temEtapas']]
        chk('1 390 px · nenhuma etapa sobrepõe ou vaza (CMP, SAF, PA, EST, IR-02)', all(med[g]['sobrepoe']==0 and not med[g]['vazam'] for g in et), {g:(med[g]['sobrepoe'],med[g]['vazam']) for g in et})
        exp={g:(f'Etapa {ATUAL[g][0]} de {ATUAL[g][1]} · {NOMES[g][ATUAL[g][0]-1]}' if g in GUIADO else NOMES[g][ATUAL[g][0]-1]) for g in et}
        chk('2 390 px · processo guiado com "Etapa i de n · Nome" e telas/seções com o nome da atual; lista recolhida; nenhuma seta ‹ › (UX-ACAO-UNICA)', all(med[g]['progresso'].startswith(exp[g]) and med[g]['etapasVis']==0 and not med[g]['setas'] for g in et), {g:(med[g]['progresso'],med[g]['etapasVis'],med[g]['setas']) for g in et})
        chk('3 390 px · título inteiro, situação e comando principal na tela, sem rolagem horizontal da página (8 telas)', all(not med[g]['h1Cortado'] and not med[g]['headerFora'] and not med[g]['hscroll'] for g in P8), {g:(med[g]['h1Cortado'],med[g]['headerFora']) for g in P8})
        inp={g:[x for x in med[g]['cortadosEx'] if x=='INPUT'] for g in P8}
        chk('4 390 px · tabelas em região rolável na horizontal; o conteúdo não rola de lado; nenhum texto ou comando cortado fora de região rolável nem texto sobre texto', all(all(med[g]['tabelasRolam']) and not med[g]['mainLado'] and med[g]['cortados']==len(inp[g]) and not med[g]['textoSobreTexto'] for g in P8), {g:(med[g]['tabelasRolam'],med[g]['mainLado'],med[g]['cortadosEx'],med[g]['textoSobreTexto']) for g in P8})
        print('     (informativo) campos cortados pela própria caixa da área:', {g:len(v) for g,v in inp.items() if v})
        # 5 · quadro do site (325 px), o caso da revisão
        m=abre('CMP',325,700); shot('CMP_325')
        chk('5 325 px (quadro do site) · Compras sem sobreposição, "Etapa 1 de 6 · Escolha a safra", título inteiro', m['sobrepoe']==0 and not m['vazam'] and m['progresso'].startswith(exp['CMP']) and not m['h1Cortado'] and not m['headerFora'], m)
        # 6 · menu aberto em 390: passa por cima, não espreme; recolher devolve. Desde 03/10 (verificação de componentes, item
        #     "menu aberto guardado") a tela estreita sempre começa com o menu recolhido, mesmo com "aberto" guardado: abre pelo botão
        abre('CMP',rec='0'); ini=J("Math.round(document.querySelector('.menu-lat').getBoundingClientRect().width)")
        J("document.querySelector('.menu-lat.rec')&&document.querySelector('.ml-tog').click()"); time.sleep(.4); shot('CMP_390_menu_aberto')
        g=lambda: J("(()=>{const m=document.querySelector('.menu-lat').getBoundingClientRect(); const col=document.querySelector('main[data-scroll]').getBoundingClientRect(); const t=document.querySelector('.ml-tog'); const r=t.getBoundingClientRect(); const e=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2); return [Math.round(m.width),Math.round(col.left),Math.round(col.width),t.contains(e)];})()")
        a=g(); J("document.querySelector('.ml-tog').click()"); time.sleep(.4); b=g()
        chk('6 390 px · com "aberto" guardado começa recolhido (68 px); aberto pelo botão passa por cima (conteúdo continua com 322 px) e o botão de recolher fica alcançável', ini==68 and a==[232,68,322,True] and b[:3]==[68,68,322], [ini,a,b])
        # 7-8 · zoom de 200 % (1440 px a 2×): menu recolhido nas telas com etapas e aberto em CMP e SAF
        # NAV-1 (integração V56, Codex NAV1-REV-20261010-01): a PA deixou de ter faixa de etapas (lista → detalhe) e sai SÓ desta asserção da
        # faixa; título, comando e rolagem da PA seguem nos itens 3 e 4 (P8) e o contexto, as ações e o teclado dela no pa_lista_test/patest
        z={}
        for pg in ['CMP','SAF','EST','IR-02']: z[pg]=abre(pg,720,450,2); shot(f'{pg}_zoom200')
        chk('7 zoom 200 % · sem sobreposição, etapa atual legível e comando principal na tela (4 telas com etapas)', all(z[g]['sobrepoe']==0 and not z[g]['vazam'] and not z[g]['headerFora'] and not z[g]['h1Cortado'] for g in z), {g:(z[g]['sobrepoe'],z[g]['vazam'],z[g]['progresso'],z[g]['headerFora']) for g in z})
        def abre_menu(pg): abre(pg,720,450,2,rec='0'); J("document.querySelector('.menu-lat.rec')&&document.querySelector('.ml-tog').click()"); time.sleep(.4); return J(MEDIR)
        za={pg:abre_menu(pg) for pg in ['CMP','SAF']}; zw=J("Math.round(document.querySelector('.menu-lat').getBoundingClientRect().width)"); shot('SAF_zoom200_menu_aberto')
        chk('8 zoom 200 % com menu aberto (pelo botão) · CMP e SAF sem sobreposição', zw==232 and all(za[g]['sobrepoe']==0 and not za[g]['vazam'] and za[g]['progresso'] for g in za), [zw,{g:(za[g]['sobrepoe'],za[g]['vazam'],za[g]['progresso']) for g in za}])
        # 9 · teclado: Tab chega à etapa atual, Espaço abre a lista com as 6 etapas; o próximo Tab entra na lista
        abre('CMP'); J("document.activeElement&&document.activeElement.blur()")
        def tab(): c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Tab','code':'Tab','windowsVirtualKeyCode':9}); c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Tab','code':'Tab','windowsVirtualKeyCode':9}); time.sleep(.05)
        k=0
        while k<60 and not J("document.activeElement&&document.activeElement.classList.contains('etp-chk')"): tab(); k+=1
        c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':' ','code':'Space','windowsVirtualKeyCode':32,'text':' '}); c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':' ','code':'Space','windowsVirtualKeyCode':32}); time.sleep(.3)
        m=J(MEDIR); tab(); dent=J("(()=>{const a=document.activeElement; return !!(a&&a.closest('.etp-itens'))&&a.innerText.replace(/\\s+/g,' ').trim();})()"); shot('CMP_390_lista_teclado')
        chk('9 teclado · Tab chega ao rótulo da etapa atual, Espaço abre a lista em folha (6 etapas, sem sobreposição) e o Tab seguinte não entra nela: a lista só informa (UX-ACAO-UNICA)', k<60 and m['folha'] and m['etapasVis']==6 and m['sobrepoe']==0 and not m['vazam'] and not dent, [k,m['folha'],m['etapasVis'],m['sobrepoe'],m['vazam'],dent])
        # 10 · toque: escolher a safra, abrir a lista, ir à etapa 3; a lista fecha sozinha e a safra continua no contexto
        abre('CMP'); clk('Abrir compra'); m1=J(MEDIR)
        clk('Etapa 2 de 6'); aberta=J(MEDIR)['etapasVis']; r=clk('3 Solicite cotações','.etp-itens'); m15=J(MEDIR)
        r2=J("(()=>{const b=document.querySelector('[data-acoes] [data-acao=avancar]'); if(!b) return 'sem avanço'; b.scrollIntoView({block:'center'}); b.click(); return b.innerText.trim();})()"); time.sleep(.5)
        m2=J(MEDIR); hd=J("document.querySelector('header').innerText.replace(/\\s+/g,' ')"); shot('CMP_390_etapa3')
        chk('10 toque · Abrir compra → "Etapa 2 de 6 · Confira a demanda"; a lista aberta só informa (a etapa 3 não é alvo de toque e a etapa não muda); o avanço "Solicitar cotações ›" da área de ações leva à etapa 3, sem texto sobre texto; Safra 2026/27 no contexto (UX-ACAO-UNICA)',
            m1['progresso'].startswith('Etapa 2 de 6 · Confira a demanda') and aberta==6 and r!='ok' and m15['progresso'].startswith('Etapa 2 de 6') and r2.startswith('Solicitar cotações') and m2['progresso'].startswith('Etapa 3 de 6 · Solicite cotações') and m2['etapasVis']==0 and not m2['textoSobreTexto'] and 'Safra 2026/27' in hd, [m1['progresso'],aberta,r,m15['progresso'],r2,m2['progresso'],m2['etapasVis'],m2['textoSobreTexto'],hd[:120]])
        # 11 · ‹ volta uma etapa; mudar de 390 para 1440 e voltar mantém etapa e safra (troca de zoom não perde contexto)
        J("document.querySelector('[data-acoes] [data-acao=voltar]').click()"); time.sleep(.4); m3=J(MEDIR)
        vp(1440,900); m4=J(MEDIR); cur=J("(document.querySelector('[aria-current=step]')||{innerText:''}).innerText.replace(/\\s+/g,' ')"); shot('CMP_1440_mesma_sessao')
        vp(390,844); m5=J(MEDIR); hd=J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
        chk('11 "‹ Demanda" (área de ações) volta à etapa 2; em 1440 a faixa completa mostra a etapa 2 e em 390 volta "Etapa 2 de 6", com a Safra 2026/27', m3['progresso'].startswith('Etapa 2 de 6') and m4['etapasVis']==6 and not m4['progresso'] and cur.startswith('2 Confira a demanda') and m5['progresso'].startswith('Etapa 2 de 6') and 'Safra 2026/27' in hd, [m3['progresso'],m4['etapasVis'],cur,m5['progresso']])
        # 12 · rascunho no painel lateral (IR-02 · Programar irrigação): cobre a faixa no celular e o texto digitado sobrevive à troca de zoom
        abre('IR-02'); r=clk('Programar irrigação'); cob=J(COBRE); shot('IR-02_390_painel')
        # painel novo da Irrigação (03/10) abre só com o Setor: escolhe o 1º setor e o rascunho passa a ter os demais campos
        sel=J("(()=>{const s=[...document.querySelectorAll('aside[role=dialog] select')].find(x=>x.getClientRects().length&&!x.disabled); if(!s||s.options.length<2) return null; const P=HTMLSelectElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(s,s.options[1].value); s.dispatchEvent(new Event('input',{bubbles:true})); s.dispatchEvent(new Event('change',{bubbles:true})); return [s.id,s.options[1].value];})()"); time.sleep(.5)
        campo=J("(()=>{const i=[...document.querySelectorAll('aside[role=dialog] input, aside[role=dialog] textarea')].find(x=>x.getClientRects().length&&!x.disabled&&!x.readOnly&&(x.type==='text'||x.tagName==='TEXTAREA'||!x.type)); if(!i) return null; i.focus(); return i.id||i.getAttribute('aria-label');})()")
        esc=None
        if campo: c.call('Input.insertText',{'text':'rascunho celular 03/10'}); time.sleep(.3)
        else:
            esc=J("(()=>{const s=[...document.querySelectorAll('aside[role=dialog] select')].find(x=>x.getClientRects().length&&!x.disabled&&x.options.length>1); if(!s) return null; const o=[...s.options].find(x=>x.value&&x.value!==s.value); if(!o) return null; const P=HTMLSelectElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(s,o.value); s.dispatchEvent(new Event('change',{bubbles:true})); if(!s.id) s.id='cel-sel'; return [s.id,o.value];})()"); time.sleep(.3)
            campo=esc[0] if esc else None
        vp(720,450,2); vp(390,844); val=J(f"(document.getElementById({json.dumps(campo)})||{{value:null}}).value") if campo else None
        selv=J(f"(document.getElementById({json.dumps(sel[0])})||{{value:null}}).value") if sel else None
        if not campo and sel and selv==sel[1]: val='rascunho celular 03/10 (setor escolhido mantido)'   # sem campo de texto: o rascunho é a escolha feita
        chk('12 painel lateral em 390 px · cobre a faixa e o cabeçalho (largura da tela) e o rascunho digitado sobrevive à troca de zoom', r=='ok' and isinstance(cob,dict) and cob['faixaVisivelSobre']==0 and cob['painelW']==390 and val and ((val==esc[1]) if esc else ('rascunho celular 03/10' in val)), [r,cob,campo,val])
        # 13 · O.S. no celular: o painel da ordem cobre o cabeçalho e não fica sob nada
        abre('OS'); J("(()=>{const r=document.querySelector('[role=row].g2ed'); (r.querySelector('[role=cell] b')||r.querySelector('[role=cell] span')||r).click();})()"); time.sleep(.5); cob2=J(COBRE); shot('OS_390_painel')
        chk('13 O.S. em 390 px · painel da ordem ocupa a largura e nada do cabeçalho fica por cima', isinstance(cob2,dict) and cob2['faixaVisivelSobre']==0 and cob2['painelW']==390, cob2)
        ERRL.extend(errs()); chk('14 sem erro de JS nas telas visitadas', not ERRL, ERRL[:5])
    elif MODO=='complemento':
        # revisão do item 3 (achados alta/média/baixa): listas alcançáveis, títulos de bloco, CD-07, tela baixa, folha de etapas
        LISTA=r"""(()=>{const t=[...document.querySelectorAll('main [role=table]')].find(t=>t.getClientRects().length); if(!t) return null;
          const cx=t.closest('.g2rola')||t.parentElement; const rows=[...t.querySelectorAll('[role=row]')]; const ult=rows[rows.length-1];
          const m=document.querySelector('main[data-scroll]'); const col=document.querySelector('.ml-tog+div');
          const out={alt:Math.round(cx.clientHeight),cont:cx.scrollHeight,linhas:rows.length,rolaTela:[m,col].some(s=>s.scrollHeight>s.clientHeight+1)};
          ult.scrollIntoView({block:'end'}); const r=ult.getBoundingClientRect(); const e=document.elementFromPoint(Math.max(2,Math.min(r.left+40,innerWidth-2)),r.top+r.height/2);
          out.ultNaJanela=r.bottom<=innerHeight+1&&r.top>=0; out.ultTocavel=!!e&&ult.contains(e); return out;})()"""
        ALC=r"""((txts)=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const m=document.querySelector('main[data-scroll]'); const mr=m.getBoundingClientRect(); const out={};
          for(const t of txts){ const cs=[...m.querySelectorAll('button,a,label,select')].filter(x=>x.getClientRects().length); const e=cs.find(x=>n(x.innerText).startsWith(t)||(x.getAttribute('aria-label')||'').startsWith(t))||cs.find(x=>n(x.innerText).includes(t));
            if(!e){ out[t]='não achei'; continue; } e.scrollIntoView({block:'center',inline:'nearest'}); const r=e.getBoundingClientRect();
            const h=document.elementFromPoint(Math.min(r.left+r.width/2,innerWidth-2),r.top+r.height/2);
            out[t]=(r.left>=mr.left-1&&r.right<=mr.right+1&&r.right<=innerWidth+1&&!!h&&(e.contains(h)||h.contains(e)))?'ok':[Math.round(r.left),Math.round(r.right),Math.round(mr.right)]; }
          out._lado=m.scrollWidth>m.clientWidth+1||m.scrollLeft>0; return out;})"""
        UTIL=r"""(()=>{const m=document.querySelector('main[data-scroll]'); const col=document.querySelector('.ml-tog+div'); const nav=document.querySelector('nav.etp');
          const navH=nav?Math.round(nav.getBoundingClientRect().height):0; const rc=col.scrollHeight>col.clientHeight+1;
          return {rolaColuna:rc, util: rc? innerHeight-navH : Math.round(m.getBoundingClientRect().height), navH};})()"""
        FOLHA=r"""(()=>{const l=document.querySelector('.etp-itens'); const cs=getComputedStyle(l); const its=[...l.children].filter(e=>e.getClientRects().length);
          if(cs.display==='none'||!its.length) return {aberta:false}; const u=its[its.length-1]; l.scrollTop=l.scrollHeight; const r=u.getBoundingClientRect();
          const e=document.elementFromPoint(r.left+r.width/2,Math.min(r.top+r.height/2,innerHeight-1));
          return {aberta:true,folha:cs.position==='fixed',n:its.length,ultTocavel:r.bottom<=innerHeight+1&&!!e&&u.contains(e),ultVisivel:r.bottom<=innerHeight+1&&r.top>=0,minAlt:Math.min(...its.map(x=>Math.round(x.getBoundingClientRect().height)))};})()"""
        ABERTA="(()=>{const l=document.querySelector('.etp-itens'); return !!l&&getComputedStyle(l).position==='fixed'&&getComputedStyle(l).display!=='none';})()"
        cen=lambda sel: J(f"(()=>{{const e={sel}; const r=e.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2];}})()")
        def toque(xy):
            c.call('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':xy[0],'y':xy[1]}]}); c.call('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]}); time.sleep(.4)
        # 17 · a lista da tela não fica espremida: caixa com a altura do conteúdo (ou ≥ 200 px) e a última linha alcançável rolando a tela
        res={}
        for pg,w,h,d in (('OS',390,844,1),('OS',720,450,2),('AG-07',390,844,1),('AG-07',720,450,2),('EST',320,700,1)):
            abre(pg,w,h,d); res[f'{pg} {w}x{h}@{d}']=J(LISTA); shot(f'{pg}_{w}x{h}_lista')
        chk('17 lista da tela alcançável (O.S. e AG-07 em 390 px e zoom de 200 %, EST em 320 px): caixa não espremida e última linha tocável rolando a tela',
            all(r and r['alt']>=min(r['cont'],200)-1 and r['ultNaJanela'] and r['ultTocavel'] for r in res.values()), res)
        # 18 · título de bloco com ação em 390 px (bloco em DIV): comandos dentro da largura, sem rolar o conteúdo de lado
        alvo={'CO-01':['Coletar contagem','Publicar versão']}   # PCM simplificado (S1): o seletor "Tarefa" do MA-01 saiu com os elegíveis (F40, D-25)   # MA-01 sem "Ver agenda" (PL-04 oculta e fixa · CTL-1, Frente F) · IR-02 da v43: o bloco "Agenda por captação" não tem ação própria (deriva do teste, não da tela)
        res={}
        for pg,t in alvo.items(): abre(pg); res[pg]=J(f"({ALC})({json.dumps(t)})")
        abre('IR-02'); lin=J("(()=>{const e=[...document.querySelectorAll('main *')].find(x=>x.children.length===0&&x.innerText.trim()==='Agenda por captação'); const lh=parseFloat(getComputedStyle(e).lineHeight)||19; return Math.round(e.getBoundingClientRect().height/lh);})()")
        shot('CO-01_390_titulo_bloco')
        chk('18 390 px · título de bloco com ação (CO-01): seletor e comandos dentro da largura e tocáveis; título "Agenda por captação" (IR-02) em até 2 linhas',
            all(all(v=='ok' for k,v in r.items() if k!='_lado') and not r['_lado'] for r in res.values()) and lin<=2, [res,lin])
        # 19 · CD-07 (regressão do patch anterior): comandos da área de dados aparecem e respondem ao toque em 390 e 600 px
        res={}
        for w in (390,600):
            abre('CD-07',w,844); res[w]=J(f"({ALC})({json.dumps(['Cadastrar código','Importar do ERP','Recolher tudo','Publicar estrutura','Traduzir no ERP'])})")
        shot('CD-07_600')
        chk('19 CD-07 em 390 e 600 px · Cadastrar código, Importar do ERP, Recolher tudo, Publicar estrutura e Traduzir no ERP na tela e tocáveis', all(all(v=='ok' for k,v in r.items() if k!='_lado') for r in res.values()), res)
        # 20 · tela baixa (celular deitado): a folha de etapas cabe e a última etapa é tocável; IR-02 com área útil e comando principal alcançável
        res={}
        for w,h in ((800,360),(568,320)):
            for pg in ('CMP','SAF','EST'):
                abre(pg,w,h); J("(()=>{const a=document.querySelector('.etp-atual'); a&&a.getClientRects().length&&a.click();})()"); time.sleep(.25); res[f'{pg} {w}x{h}']=J(FOLHA)
        shot('EST_568x320_folha')
        abre('IR-02',800,360); u=J(UTIL); pr=J("(()=>{const e=[...document.querySelectorAll('header a,header button')].find(x=>x.innerText.trim()==='Programar irrigação'); e.scrollIntoView({block:'center'}); const r=e.getBoundingClientRect(); const h=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2); return r.bottom<=innerHeight&&!!h&&e.contains(h);})()")
        shot('IR-02_800x360')
        chk('20 tela baixa (800×360 e 568×320) · folha com a última etapa à vista (CMP, SAF: só informa) ou tocável (EST: seções); IR-02 com ≥ 280 px úteis (cabeçalho rola, faixa fica) e "Programar irrigação" alcançável',
            all(r['aberta'] and r['folha'] and (r['ultTocavel'] or (k.split()[0] in GUIADO and r['ultVisivel'])) for k,r in res.items()) and u['rolaColuna'] and u['util']>=280 and pr, [res,u,pr])
        # 21 · zoom de 200 % nas telas de cabeçalho alto (antes 95–111 px de conteúdo)
        res={}
        for pg in ('CO-02','CO-02det','CO-06','CO-06det','LO-02det'): abre(pg,720,450,2); res[pg]=J(UTIL)
        chk('21 zoom 200 % · CO-02, CO-02det, CO-06, CO-06det e LO-02det com ≥ 300 px úteis (cabeçalho rola junto)', all(r['util']>=300 for r in res.values()), res)
        # 22 · folha de etapas por toque real: tocar fora fecha, tocar na etapa atual fecha, tocar em outra leva a ela
        abre('CMP'); clk('Abrir compra')
        c.call('Emulation.setTouchEmulationEnabled',{'enabled':True,'maxTouchPoints':5}); time.sleep(.2)
        toque(cen("document.querySelector('.etp-atual')")); a1=J(ABERTA); shot('CMP_390_folha')
        toque([230,110]); f1=not J(ABERTA)
        toque(cen("document.querySelector('.etp-atual')")); toque(cen("document.querySelector('.etp-itens [aria-current=step]')")); f2=not J(ABERTA); at2=J(MEDIR)['progresso']
        toque(cen("document.querySelector('.etp-atual')")); toque(cen("[...document.querySelectorAll('.etp-itens>*')][2]")); f3=not J(ABERTA); at3=J(MEDIR)['progresso']
        c.call('Emulation.setTouchEmulationEnabled',{'enabled':False}); time.sleep(.2)
        chk('22 toque · folha abre; tocar fora fecha; tocar na etapa atual fecha sem mudar; tocar na etapa 3 fecha sem navegar (a lista só informa · UX-ACAO-UNICA)', a1 and f1 and f2 and at2.startswith('Etapa 2 de 6') and f3 and at3.startswith('Etapa 2 de 6'), [a1,f1,f2,at2,f3,at3])
        # 23 · alvos de toque da faixa compacta ≥ 44 px (PRD: ações de campo); itens da folha também
        abre('IR-02'); al=J("(()=>{const r=e=>{const b=e.getBoundingClientRect(); return [Math.round(b.width),Math.round(b.height)];}; const nav=document.querySelector('nav.etp'); return {rotulo:r(nav.querySelector('.etp-atual')),setas:[...nav.querySelectorAll('[aria-label^=\"Etapa anterior\"],[aria-label^=\"Próxima etapa\"]')].filter(e=>e.getClientRects().length).map(r)};})()")
        J("document.querySelector('.etp-atual').click()"); time.sleep(.2); fo=J(FOLHA)
        chk('23 alvos de toque da faixa compacta ≥ 44 px (rótulo e telas da folha) e nenhuma seta ‹ › (UX-ACAO-UNICA)', al['rotulo'][1]>=44 and len(al['setas'])==0 and fo['minAlt']>=44, [al,fo])
        # 24 · situação do cabeçalho inteira em 390 px (antes cortada em CD-01, CD-03, CD-07 e SU-09)
        res={pg:abre(pg)['headerFora'] for pg in ('CD-01','CD-03','CD-07','SU-09')}
        chk('24 390 px · situação do cabeçalho inteira (CD-01, CD-03, CD-07, SU-09)', not any(res.values()), res)
        ERRL.extend(errs()); chk('25 sem erro de JS nas telas visitadas', not ERRL, ERRL[:5])
    elif MODO=='desktop':
        # 1440 px igual à base, menu aberto e recolhido, em todas as telas (fatias A:B para caber no tempo de um comando)
        AD=os.environ.get('ANTES_DIR',os.path.join(HERE,'..','gen37_antes','_render'))
        todas=sorted(os.path.basename(f)[:-8] for f in glob.glob(os.path.join(HERE,'_render','*.dc.html')))
        A,B=(int(sys.argv[2]),int(sys.argv[3])) if len(sys.argv)>3 else (0,len(todas))
        pags=todas[A:B]
        GEO=r"""(()=>{const vis=e=>{const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>0&&r.height>0&&cs.visibility!=='hidden'&&cs.display!=='none';};
          return [...document.querySelectorAll('body *')].filter(e=>!e.closest('.etp-chk,.etp-atual,.etp-fundo')&&!e.matches('style,script')&&vis(e)&&(e.children.length===0||e.matches('h1,h2,h3,button,a,input,select,label,nav,main,header,aside,section,[role=row]'))).map(e=>{const r=e.getBoundingClientRect(); return [e.tagName,(e.innerText||'').replace(/\s+/g,' ').trim().slice(0,24),Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)].join('|');});})()"""
        dif={}; mapa=[]
        if os.path.isdir(AD):
            p2,srv2=serve(AD); time.sleep(.6)
            vp(1440,900)
            for rec in ('0','1'):
                for porta in (p2,p):   # a escolha do menu fica no navegador por origem: gravar nas duas (base e atual)
                    c.goto(f'http://127.0.0.1:{porta}/Main.dc.html',wait=.4); J(f"localStorage.setItem('safrion.menuRecolhido','{rec}')")
                for pg in pags:
                    c.goto(f'http://127.0.0.1:{p2}/{pg}.dc.html',wait=.4); a=J(GEO)
                    c.goto(f'http://127.0.0.1:{p}/{pg}.dc.html',wait=.4); b=J(GEO)
                    if a!=b:
                        if set(a)==set(b): mapa.append(f'{pg}/{rec}'); continue   # mesmo conjunto de elementos (mapa repete peças): igual
                        dif[f'{pg}/{rec}']=[x for x in a if x not in b][:3]+['→']+[x for x in b if x not in a][:3]
            if mapa: print('     (informativo) mesmo conjunto de elementos, contagem do mapa varia:',mapa)
            chk(f'15 1440 px igual à base (menu aberto e recolhido) em {len(pags)} telas ({A}:{B} de {len(todas)})', not dif, dif)
        else: chk('15 1440 px igual à base', False, 'base ausente: '+AD)
    else:   # faixa: varredura de largura da faixa em todas as telas com etapas
        pags=sorted(os.path.basename(f)[:-8] for f in glob.glob(os.path.join(HERE,'_render','*.dc.html')) if 'class="etp etp-' in open(f).read())
        VAR=r"""(()=>{const nav=document.querySelector('.etp'); const out=[];
          for(let W=1400;W>=300;W-=20){ nav.style.width=W+'px'; const at=nav.querySelector('.etp-atual'); const comp=!!(at&&at.getClientRects().length);
            const its=[...nav.querySelectorAll('.etp-itens>*')].filter(e=>e.getClientRects().length); const nr=nav.getBoundingClientRect(); const lr=nav.querySelector('.etp-itens').getBoundingClientRect();
            let ruim=''; if(!comp){ for(const e of its){ const b=e.getBoundingClientRect(); const rg=document.createRange(); rg.selectNodeContents(e); if([...rg.getClientRects()].some(r=>r.width>.5&&(r.right>b.right+1.5||r.left<b.left-1.5))||b.right>lr.right+1.5) { ruim=e.innerText.replace(/\s+/g,' ').slice(0,30); break; } } }
            else if(its.length||at.getBoundingClientRect().right>nr.right) ruim='lista visível ou rótulo fora';
            if(ruim) out.push(W+':'+ruim); }
          nav.style.width=''; return out; })()"""
        ruins={}
        vp(1440,900)
        for pg in pags:
            c.goto(f'http://127.0.0.1:{p}/{pg}.dc.html',wait=.5); r=J(VAR)
            if r: ruins[pg]=r[:3]
        chk(f'16 varredura de largura (1400 → 300 px) em {len(pags)} telas com etapas: faixa completa sem sobreposição ou compacta', not ruins, ruins)
finally:
    if c: c.close()
    srv.terminate(); srv2 and srv2.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas ({MODO})'); [print('  -',f) for f in FAIL]
sys.exit(1 if FAIL else 0)
