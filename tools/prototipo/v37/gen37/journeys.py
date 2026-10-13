# -*- coding: utf-8 -*-
"""Executa roteiros DEMO no protótipo servido localmente (Chrome headless via CDP) e registra evidência.
Uso: python3 journeys.py DEMO-13 [DEMO-15 ...]   (roteiros em ../validacao/roteiros/DEMO-xx.json)
Passos: ["abrir","X.dc.html"] · ["clicar","rótulo"] · ["ver","texto"] · ["nao_ver","texto"] · ["resultado","trecho do aviso exibido"]
        ["tela","X.dc.html"] · ["foto","nome"] · ["movel"] (390×844) · ["desktop"] · ["nota","observação livre"]"""
import sys, os, json, time, socket, subprocess, re, math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome, CONDICAO, _dormir
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(HERE,'_render'); V=os.path.join(HERE,'..','validacao')
def free():
    s=socket.socket(); s.bind(('127.0.0.1',0)); p=s.getsockname()[1]; s.close(); return p
CLICK=r"""(async (t)=>{const norm=s=>(s||'').replace(/\s+/g,' ').trim();
 const els=[...document.querySelectorAll('button, a[href]')].filter(e=>e.offsetParent!==null||e.getClientRects().length);
 let el=els.find(e=>norm(e.innerText)===t)||els.find(e=>norm(e.innerText).startsWith(t))||els.find(e=>norm(e.innerText).includes(t))||els.find(e=>norm(e.getAttribute('aria-label'))===t);
 if(!el) return {ok:false,why:'não encontrado'};
 const href=el.tagName==='A'?el.getAttribute('href'):null; el.scrollIntoView({block:'center'}); el.click();
 return {ok:true,tag:el.tagName,href,txt:norm(el.innerText).slice(0,80)};})"""
TOAST=r"""(()=>{const s=[...document.querySelectorAll('[role=status]')].map(e=>e.innerText.trim()).filter(Boolean);return s.join(' | ');})()"""
def run(demo):
    spec=json.load(open(os.path.join(V,'roteiros',demo+'.json')))
    out=os.path.join(V,demo); os.makedirs(out,exist_ok=True)
    for f in os.listdir(out):
        if f.endswith('.png') or f=='resultado.json': os.remove(os.path.join(out,f))
    port=free(); srv=subprocess.Popen(['python3','-m','http.server',str(port),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(0.8); c=Chrome(port=free()); base=f'http://127.0.0.1:{port}/'
    log=[]; ok_all=True; nfoto=0; movel=False
    try:
        c.size(1440,1100)
        for i,st in enumerate(spec['passos'],1):
            k=st[0]; arg=st[1] if len(st)>1 else None; r={'n':i,'passo':k,'arg':arg}
            try:
                if k=='abrir': c.goto(base+arg); r['ok']=True; r['obs']=c.js("document.title")
                elif k=='clicar':
                    res=c.js(f"({CLICK})({json.dumps(arg)})"); r['ok']=bool(res and res.get('ok')); r['obs']=res
                    if r['ok'] and res.get('href') and res['href'].endswith('.dc.html'):
                        if CONDICAO:
                            # ACELERA: espera o documento novo (caminho certo, completo, sem navegação pendente) e assenta, com o
                            # mesmo teto de antes: max(clique + 1,2 s, pronto) + 1,5 s
                            t0=time.monotonic(); pronto=None
                            while True:
                                try: ok=c.js(f"location.pathname.endsWith({json.dumps(res['href'])}) && document.readyState==='complete' && !!window.__sfq && !window.__sfq.nav")
                                except Exception: ok=False
                                if ok: pronto=time.monotonic(); break
                                if time.monotonic()>=t0+1.2+40*0.25: break
                                _dormir(.05)
                            if pronto is not None and pronto>t0+1.2: pronto=t0+1.2+math.ceil((pronto-t0-1.2)/0.25-1e-9)*0.25   # o laço antigo olhava a cada 0,25 s
                            c.settle(.3,max(t0+1.2,pronto or time.monotonic())+1.5-time.monotonic())
                        else:
                            _dormir(1.2)
                            for _ in range(40):
                                if c.js("location.pathname").endswith(res['href']) and c.js("document.readyState")=='complete': break
                                _dormir(0.25)
                            _dormir(1.5)
                    else: c.espera_acao(0.8)
                elif k=='ver':
                    body=c.js("document.body.innerText"); r['ok']=arg.lower() in body.lower(); r['obs']='encontrado' if r['ok'] else 'ausente'
                elif k=='nao_ver':
                    body=c.js("document.body.innerText"); r['ok']=arg.lower() not in body.lower(); r['obs']='ausente (ok)' if r['ok'] else 'PRESENTE'
                elif k=='resultado':
                    t=c.js(TOAST) or ''; r['ok']=arg.lower() in t.lower(); r['obs']=t[:400]
                elif k=='tela':
                    p=c.js("location.pathname"); r['ok']=p.endswith(arg); r['obs']=p
                elif k=='foto':
                    nfoto+=1; f=f'{nfoto:02d}_{arg}.png'
                    w=c.js("Math.max(document.documentElement.scrollWidth, 390)"); h=c.js("Math.min(Math.max(document.documentElement.scrollHeight, 600), 4000)")
                    c.size(w,h); c.espera_acao(0.3); c.shot(os.path.join(out,f)); c.size(390 if movel else 1440, 844 if movel else 1100)
                    r['ok']=True; r['obs']=f
                elif k=='movel': movel=True; c.size(390,844); r['ok']=True
                elif k=='desktop': movel=False; c.size(1440,1100); r['ok']=True
                elif k=='nota': r['ok']=True; r['obs']=arg
                else: r['ok']=False; r['obs']='passo desconhecido'
            except Exception as ex: r['ok']=False; r['obs']=f'erro: {ex}'
            if not r['ok']:
                ok_all=False; nfoto+=1; f=f'{nfoto:02d}_FALHA_passo{i}.png'
                try: c.shot(os.path.join(out,f)); r['evidencia']=f
                except Exception: pass
            log.append(r)
    finally:
        c.close(); srv.terminate()
    res={'demo':demo,'titulo':spec.get('titulo'),'perfil':spec.get('perfil'),'dados_iniciais':spec.get('dados_iniciais'),
         'esperado':spec.get('esperado'),'resultado':'passou' if ok_all else 'falhou','passos':log,
         'executado_em':time.strftime('%d/%m/%Y %H:%M'),'versao':'protótipo v3.7 (build local)'}
    json.dump(res,open(os.path.join(out,'resultado.json'),'w'),ensure_ascii=False,indent=1)
    falhas=[p for p in log if not p['ok']]
    print(f"{demo}: {res['resultado']} · {len(log)} passos · {len(falhas)} falha(s)")
    for p in falhas: print(f"   passo {p['n']} {p['passo']} {p['arg']!r} → {str(p['obs'])[:160]}")
    return res
if __name__=='__main__':
    for d in sys.argv[1:]: run(d)
