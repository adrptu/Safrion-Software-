# -*- coding: utf-8 -*-
"""Teste CDP do Mapa IN-04 na Lagoa Grande com talmapa.js (CAMADA-SINTETICA-01; refeito sem coordenada real: tudo vem de
dados_lagoa_fonte, sintético fora do Mac). Confere: mapa MapLibre carregado sem erro, rótulo "Demonstração sintética" no lugar dos
textos de dado real, 23 pivôs iguais aos da fonte, contornos (tmAneis) com a área, sobreposição (tmSobrepoe), validação e gravação de
talhão novo desenhado (tmValida/tmSalvar), pixels do satélite coerentes com a renovação do Pivô 12, e capturas desktop e celular.
Uso (de gen37/, depois de build.py e montar_render.py): CHROME_BIN=… python3 talmapa_test.py [pasta-das-capturas]"""
import sys, os, time, json, math
os.environ.setdefault('CDP_GL', '1')     # WebGL por software para o MapLibre
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cadc_lib import T
import dados_lagoa_fonte as F
SH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '_probe'); os.makedirs(SH, exist_ok=True)
PV = [dict(id=p[0], ha=p[2], lon=p[3], lat=p[4]) for p in F.LG_PIVOS]
t = T(); J = t.J
QUAD = "((lon,lat,L)=>{const k=111320*Math.cos(lat*Math.PI/180),h=L/2; return tgFechado([[lon-h/k,lat-h/110540],[lon+h/k,lat-h/110540],[lon+h/k,lat+h/110540],[lon-h/k,lat+h/110540]]);})"
def espera(expr, s=45):
    fim = time.time() + s
    while time.time() < fim:
        if J(expr): return True
        time.sleep(0.5)
    return False
try:
    t.goto('Main.dc.html'); J("localStorage.removeItem('talhao-os-cd01-v1'); sessionStorage.setItem('mapa-ctx','{\"mf_faz\":\"Lagoa Grande\"}')")
    t.c.size(1440, 900); t.goto('IN-04.dc.html')
    pronto = espera("!!(window.__LGI&&window.__LGI.pronto)")
    t.chk('1 IN-04 na Lagoa Grande: mapa MapLibre pronto, sem erro de JavaScript', pronto and t.errs() == '', [pronto, J("window.__LGI&&window.__LGI.erro"), t.errs()])
    # o código da página roda dentro do runtime (fora do escopo global; só window.__LGI é exposto): o teste lê o mesmo M da página
    # renderizada e avalia talgeo.js e talmapa.js no escopo global sobre ele (nfx: formatador mínimo, só para mensagens)
    J("""(async()=>{const h=await (await fetch('IN-04.dc.html')).text(); const i=h.indexOf('const M = '); const j=h.indexOf(';\\n',i);
        window.__M=JSON.parse(h.slice(i+10,j)); return 1;})()""")
    J("var M=window.__M, LGI=window.__LGI, FAZ='Lagoa Grande'; function isLG(t){ return String(t).indexOf('PV')===0; } "
      "function nfx(n,d){ return Number(n).toFixed(d===undefined?1:d).replace('.',','); }\n"
      + open(os.path.join(HERE, 'talgeo.js'), encoding='utf-8').read() + '\n' + open(os.path.join(HERE, 'talmapa.js'), encoding='utf-8').read() + '\n;1')
    corpo = J("document.body.innerText") or ''
    t.chk('2 rótulo visível "Demonstração sintética · pivôs, imagem e índices fictícios"; mapa rotulado; sem "imagem real", "Sentinel-2 real" nem "KML do proprietário"',
          'Demonstração sintética · pivôs, imagem e índices fictícios' in corpo and 'Demonstração sintética' in (J("document.getElementById('mapa-real').getAttribute('aria-label')") or '')
          and not any(x in corpo for x in ('imagem real', 'Sentinel-2 real', 'KML do proprietário')) and J("window.__M.lg.rot") == F.ROTULO, corpo[:300])
    pg = J("M.lg.pivos.map(p=>({id:p.id,ha:p.ha,lon:p.lon,lat:p.lat}))")
    t.chk('3 23 pivôs no mapa = dados_lagoa_fonte (id, ha, lon, lat) e 23 marcadores', pg == PV and J("Object.keys(window.__LGI.markers).length") == 23, [len(pg or []), J("Object.keys(window.__LGI.markers).length")])
    an = J("tmAneis('Lagoa Grande').map(a=>[a.id,a.nome,tgAreaHa(a.ring)])") or []
    err = max((abs(a[2] - p['ha']) / p['ha'] for a, p in zip(an, PV)), default=1)
    t.chk('4 tmAneis: 23 contornos (círculos), nome "Pivô n", área ≈ ha (< 1 %)', len(an) == 23 and err < 0.01 and an[0][1] == 'Pivô 1', [len(an), err, an[:1]])
    p5 = PV[4]
    s_in = J(f"tmSobrepoe({QUAD}({p5['lon']},{p5['lat']},200),'Lagoa Grande','novo')"); s_out = J(f"tmSobrepoe({QUAD}({p5['lon']},{p5['lat']}+0.012,200),'Lagoa Grande','novo')")
    t.chk('5 tmSobrepoe: quadrado de 200 m no centro do Pivô 5 acusa o Pivô 5; ao norte, fora da grade, nada', bool(s_in) and s_in[0].startswith('Pivô 5 (') and s_out == [], [s_in, s_out])
    novo = f"{QUAD}({PV[0]['lon']},{PV[0]['lat']}+0.012,150)"; ha = J(f"tgAreaHa({novo})")
    dec = f'{ha:.2f}'.replace('.', ',')   # como o formulário envia (vírgula decimal; o ponto é separador de milhar no tmNum)
    e_ok = J(f"tmValida({{ring:{novo},alvo:'novo',nome:'Talhão sintético 1',decl:'{dec}'}},'Lagoa Grande')")
    e_dup = J(f"tmValida({{ring:{QUAD}({p5['lon']},{p5['lat']},200),alvo:'novo',nome:'Pivô 1',decl:'4'}},'Lagoa Grande')") or {}
    sv = J(f"tmSalvar({{ring:{novo},alvo:'novo',nome:'Talhão sintético 1',decl:'{dec}',faz:'Lagoa Grande',origem:'Desenho no mapa'}})") or {}
    t.chk('6 talhão novo desenhado fora dos pivôs: tmValida sem erro, grava LGT01 com a área; nome repetido e sobreposição são recusados; 24 contornos',
          e_ok == {} and sv.get('id') == 'LGT01' and abs(sv.get('ha', 0) - ha) < 0.01 and 'nome' in e_dup and 'Pivô 5' in e_dup.get('geo', '')
          and J("tmAneis('Lagoa Grande').length") == 24 and 'LGT01' in (J("Object.keys(JSON.parse(localStorage.getItem('talhao-os-cd01-v1')).geom)") or []), [e_ok, sv, e_dup])
    # camada Satélite pela barra do mapa: a página carrega lagoa_s2.json em __LGI.px e escreve a legenda da cena
    J("[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')].find(b=>(b.getAttribute('title')||'').startsWith('Mostrar Satélite')).click()")
    espera("!!(window.__LGI.px)", 30); time.sleep(1); sat = J("document.body.innerText") or ''
    J("window.__pxok=1")
    px = J("""(()=>{const P=window.__LGI.px; const k=M.lg.ids.indexOf('PV12'); const m=(dt)=>{let s=0,n=0; const q=P.cen[dt].NDVI; for(let i=0;i<q.length;i++){ if(P.dono[i]===k&&q[i]!==255){ s+=q[i]/125-1; n++; } } return n?s/n:null; };
      return {ok:window.__pxok,n:P.dono.length,a:m('10/09'),b:m('25/09'),proc:M.sat['25/09'].proc};})()""") or {}
    t.chk('7 camada Satélite: legenda sintética; pixels (lagoa_s2.json): Pivô 12 com lavoura velha em 10/09 (NDVI > 0,5) e solo exposto em 25/09 (< 0,25); cena rotulada sintética',
          px.get('ok') == 1 and px.get('n', 0) > 1000 and (px.get('a') or 0) > 0.5 and (px.get('b') or 1) < 0.25 and px.get('proc', '').startswith('Demonstração sintética')
          and 'Demonstração sintética · imagem e índices fictícios' in sat and 'imagem real' not in sat, [px, sat[:200]])
    t.c.shot(os.path.join(SH, 'talmapa_desktop.png'))
    t.c.size(390, 844); t.goto('IN-04.dc.html'); cel = espera("!!(window.__LGI&&window.__LGI.pronto)")
    t.c.shot(os.path.join(SH, 'talmapa_celular.png'))
    t.chk('8 celular 390 px: mapa pronto, rótulo visível, sem rolagem horizontal, sem erro', cel and 'Demonstração sintética' in (J("document.body.innerText") or '')
          and J("document.documentElement.scrollWidth<=window.innerWidth+1") and t.errs() == '', [cel, t.errs()])
    print(f'RESULTADO: {sum(t.ok)}/{len(t.ok)}')
finally:
    t.c.close(); t.srv.terminate()
sys.exit(0 if t.ok and all(t.ok) else 1)
