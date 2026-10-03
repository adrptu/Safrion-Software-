# -*- coding: utf-8 -*-
"""Mapa IN-04 · desenhar e importar talhões (talmapa.js) integrado ao cadastro de fazendas e talhões (CD-01/CD-01det).
Chrome headless com o MapLibre real da Lagoa Grande: cliques no mapa por eventos do próprio MapLibre."""
import time, json, os, shutil
os.environ['CDP_GL']='1'   # o mapa real precisa de WebGL (por software no Chrome headless)
from cadc_lib import T, HERE
shutil.copy(os.path.join(HERE,'teste_importacao.kml'),os.path.join(HERE,'_render','teste_importacao.kml'))
t=T(); J=t.J
CK='talhao-os-cd01-v1'
def st(): return J(f"JSON.parse(localStorage.getItem('{CK}')||'{{}}')") or {}
def B(txt,raiz=''): return J(f"(()=>{{const b=[...document.querySelectorAll('{raiz} button')].find(b=>b.innerText.trim().startsWith({json.dumps(txt)})); if(!b) return false; b.click(); return true;}})()")
def painel(): return J("(()=>{const a=document.querySelector('aside[aria-label]'); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def info(): return J("(document.querySelector('[aria-label=\"Desenho do talhão\"] [role=status]')||{}).innerText||''") or ''
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).join(' | ')") or ''
def clique(lon,lat): J(f"(()=>{{const m=__LGI.map; const cv=m.getCanvas(); m.fire('click',{{lngLat:{{lng:{lon},lat:{lat}}},point:m.project([{lon},{lat}]),originalEvent:{{target:cv,preventDefault(){{}},stopPropagation(){{}}}}}});}})()"); time.sleep(.15)
def pronto(n=60):
    for _ in range(n):
        if J("!!(window.__LGI&&__LGI.pronto&&__LGI.map&&__LGI.map.getSource('tu'))"): return True
        time.sleep(.25)
    return False
def setv(sel,val):
    return J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); if(!i) return false; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}})); return true;}})()""")
def quadrado(lon,lat,d):
    for p in [(lon,lat),(lon+d,lat),(lon+d,lat-d),(lon,lat-d)]: clique(*p)
try:
    t.goto('Main.dc.html'); J(f"localStorage.removeItem('{CK}'); sessionStorage.setItem('mapa-ctx',JSON.stringify({{mf_faz:'Lagoa Grande',lay:'Integrado',tsel:[]}}))")
    t.goto('IN-04.dc.html'); ok=pronto()
    t.chk('mapa real da Lagoa Grande pronto, com Desenhar e Importar na barra', ok and J("[...document.querySelectorAll('[aria-label=\"Ferramentas do mapa\"] button')].map(b=>b.innerText.trim()).join('|')").count('|')>=3
          and 'Desenhar' in J("document.querySelector('[aria-label=\"Ferramentas do mapa\"]').innerText") and 'Importar' in J("document.querySelector('[aria-label=\"Ferramentas do mapa\"]').innerText"))
    # 1 · desenhar um polígono num lugar vazio: medida ao vivo e formulário com o nome sugerido
    B('Desenhar'); time.sleep(.4); quadrado(-46.5930,-17.6990,0.004); time.sleep(.3); i1=info()
    t.chk('quatro cliques: medida ao vivo em ha e perímetro', i1.startswith('4 pontos') and ' ha · perímetro ' in i1, i1)
    B('Concluir'); time.sleep(.5); p=painel()
    t.chk('Concluir abre o formulário: Talhão novo, área do contorno e área cultivável', 'Talhão desenhado' in p and 'Usar o desenho como' in p and 'Área cultivável' in p, p[:200])
    # 2 · nome repetido (o Pivô 1 do KML) é recusado junto ao campo
    setv('aside input[aria-label="Nome do talhão"]','Pivô 1'); time.sleep(.3); B('Salvar no cadastro'); time.sleep(.4); p=painel()
    t.chk('nome igual ao de um talhão da fazenda é recusado e o desenho fica', 'Já existe Pivô 1 na Lagoa Grande' in p and 'Talhão desenhado' in p, p[:300])
    setv('aside input[aria-label="Nome do talhão"]','Talhão Teste'); time.sleep(.3); B('Salvar no cadastro'); time.sleep(.6); s=st()
    nov=[x for x in s.get('tal',[]) if x['v'].get('t')=='Talhão Teste']; vs=(s.get('vers') or {}).get(nov[0]['id'] if nov else '',[])
    t.chk('salvo no cadastro: talhão novo com área do contorno, versão v1 "Desenho no mapa" e geometria', len(nov)==1 and nov[0]['v']['faz']=='Lagoa Grande' and abs(nov[0]['v']['calc']-nov[0]['v']['decl'])<0.01 and vs and vs[0][0]=='v1' and vs[0][2]=='Desenho no mapa' and nov[0]['id'] in (s.get('geom') or {}), (nov,vs))
    p=painel(); t.chk('painel mostra o talhão salvo com Redesenhar, Abrir no cadastro e Planejar na safra', 'Talhão Teste' in p and 'Redesenhar contorno' in p and 'Abrir no cadastro' in p and 'Planejar na safra' in p, p[:300])
    # 3 · contorno que cruza a si mesmo e contorno sobre o Pivô 1 são recusados
    B('Desenhar'); time.sleep(.4)
    for q in [(-46.6010,-17.7000),(-46.5970,-17.7040),(-46.5970,-17.7000),(-46.6010,-17.7040)]: clique(*q)
    B('Concluir'); time.sleep(.4); B('Salvar no cadastro'); time.sleep(.4); p=painel()
    t.chk('contorno que cruza a si mesmo é recusado', 'cruza a si mesmo' in p, p[-250:])
    B('Descartar'); time.sleep(.3); B('Desenhar'); time.sleep(.4); quadrado(-46.5285,-17.7465,0.006); B('Concluir'); time.sleep(.4); B('Salvar no cadastro'); time.sleep(.4); p=painel()
    t.chk('contorno sobre o Pivô 1 é recusado com a área sobreposta', 'sobrepõe Pivô 1' in p, p[-250:])
    B('Descartar'); time.sleep(.3)
    # 4 · novo contorno de um pivô existente: diferença acima de 1 % pede o motivo (mesma regra do cadastro)
    t.goto('CD-01.dc.html'); t.goto('IN-04.dc.html#desenhar=PV18'); pronto(); time.sleep(.8); tx=toast(); i2=info()   # como o link do cadastro: página nova
    t.chk('atalho do cadastro (#desenhar=PV18) abre o desenho do Pivô 18 no modo pivô', 'Novo contorno de Pivô 18' in tx and 'centro' in i2.lower(), (tx[:120],i2))
    PV=json.load(open(os.path.join(HERE,'dados_lagoa','lagoa_s2_resumo.json'),encoding='utf-8'))['pivos']; c18=next((p['lon'],p['lat']) for p in PV if p['id']=='PV18'); clique(c18[0],c18[1]); setv('[aria-label="Área do pivô em hectares"]','16'); time.sleep(.5); p=painel()
    t.chk('pivô pela área (16 ha) abre o formulário de novo contorno do Pivô 18', 'Novo contorno · Pivô 18' in p, p[:160])
    B('Salvar no cadastro'); time.sleep(.4); p=painel()
    t.chk('área cultivável 18 ha × contorno 16 ha: pede o motivo antes de salvar', 'escolha o motivo' in p, p[-260:])
    setv('aside select[aria-label="Motivo da diferença"]','Carreador ou estrada'); time.sleep(.3); B('Salvar no cadastro'); time.sleep(.6); s=st()
    pv=[x for x in s.get('tal',[]) if x['id']=='PV18']
    t.chk('Pivô 18 salvo com contorno v1 de 16 ha e o motivo', pv and abs(pv[0]['v']['calc']-16)<0.3 and pv[0]['v']['motivo']=='Carreador ou estrada' and pv[0]['v']['ver']=='v1', pv)
    # 5 · importar KML: pivô novo (ponto + área), polígono novo, novo contorno do Pivô 1 (pelo nome) e reserva fora
    B('Importar'); time.sleep(.4)
    J("(async()=>{const txt=await (await fetch('teste_importacao.kml')).text(); const inp=document.querySelector('input[type=file]'); const dt=new DataTransfer(); dt.items.add(new File([txt],'teste_importacao.kml')); inp.files=dt.files; inp.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.2)
    sels=J("[...document.querySelectorAll('aside select[aria-label^=\"Destino de\"]')].map(s=>s.options[s.selectedIndex].text)"); p=painel()
    t.chk('prévia: PIVÔ 25 novo, PIVÔ 1 atualiza o Pivô 1, Talhão Norte novo, RL 1 fora', sels==['Talhão novo','Novo contorno de Pivô 1','Talhão novo','Não importar'] and '2 talhões novos · 1 contorno atualizado · 1 fora da importação' in p, (sels,p[:200]))
    B('Importar 3'); time.sleep(.8); tx=toast(); s=st()
    nomes=[x['v']['t'] for x in s.get('tal',[]) if x['id'].startswith('LGT')]
    pv1=[x for x in s.get('tal',[]) if x['id']=='PV01']
    t.chk('importado: Pivô 25 e Talhão Norte novos (nome do arquivo arrumado), Pivô 1 com contorno do KML', 'Pivô 25' in nomes and 'Talhão Norte' in nomes and pv1 and abs(pv1[0]['v']['calc']-60.94)<0.3 and (s.get('vers') or {}).get('PV01',[[0,0,'']])[-1][2]=='KML teste_importacao.kml', (nomes,pv1))
    t.chk('aviso diz o que mudou e que o Pivô 1 tem diferença a explicar no cadastro', 'Importado para o cadastro: 2 talhões novos · 1 contorno atualizado · 1 com diferença de área' in tx, tx[:200])
    # 6 · cadastro: os talhões do mapa aparecem e a regra da diferença vale
    t.goto('CD-01.dc.html'); time.sleep(.4); rows=J("[...document.querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\\s+/g,' '))") or []
    def row(p0): return next((r for r in rows if r.startswith(p0)),'')
    t.chk('CD-01 lista Talhão Teste, Pivô 25 e Talhão Norte na Lagoa Grande', row('Talhão Teste') and row('Pivô 25') and row('Talhão Norte') and any(r.startswith('▾ Lagoa Grande 26 talhões') for r in rows), [r for r in rows if 'Lagoa' in r][:2])
    t.chk('CD-01: Pivô 1 com contorno do KML pede o motivo da diferença (−4,8 %)', 'Informar motivo' in row('PV01') and '−4,8 %' in row('PV01'), row('PV01'))
    t.goto('CD-01det.dc.html#talhao=PV01'); time.sleep(.4); J("(()=>{const b=[...document.querySelectorAll('[role=tab]')].find(b=>/Geometria/.test(b.innerText)); b&&b.click();})()"); time.sleep(.4)
    lk=J("[...document.querySelectorAll('a')].filter(a=>/no mapa|KML/.test(a.innerText)).map(a=>a.innerText.trim()+'='+a.getAttribute('href'))") or []
    vtxt=J("document.body.innerText.replace(/\\s+/g,' ')") or ''
    t.chk('CD-01det do Pivô 1: versão v1 do KML e links Redesenhar, Ver no mapa e Importar', 'v1 · 60,9 ha' in vtxt and 'Redesenhar no mapa ›=IN-04.dc.html#desenhar=PV01' in lk and 'Ver no mapa ›=IN-04.dc.html#talhao=PV01' in lk and 'Importar KML ou GeoJSON ›=IN-04.dc.html#importar' in lk, lk)
    t.chk('sem erro de script', not t.errs(), t.errs())
finally:
    n=sum(t.ok); print(f'RESULTADO: {"OK" if all(t.ok) else "FALHOU"} {n}/{len(t.ok)}'); t.c.close() if hasattr(t.c,'close') else None; t.srv.terminate()
