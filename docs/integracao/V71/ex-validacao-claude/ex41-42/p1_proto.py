# -*- coding: utf-8 -*-
"""EX-42 · exercita o protótipo de referência pragas-no-tempo.html (insumo, dados sintéticos) a 1440 × 1000 e 390 × 844 (toque).
Duas cópias servidas do scratch: 'orig.html' (bytes iguais ao insumo, SHA-256 conferido) para a tela e 'instr.html' (mesmo arquivo + uma
linha que expõe os dados internos em window.__pdt) só para o dump de dados usado no recálculo independente (p2_recalculo.py).
Saídas: out/p1_proto.log, out/p1_proto.json, out/proto_dados.json, png/proto_*.png. Só leitura: não toca no repositório."""
import os, sys, json, time, hashlib, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import chrome, server, dump, log, OUT, PNG
INS = '/tmp/claude-0/ex42/docs/integracao/V71/insumos/pragas-no-tempo.html'
SHA = '8b9e105e7ee7e9f0692c2264b3f41fe45bcb3da1bec3916f23e8a0e72a717f15'
SERVE = os.environ.get('SERVE_DIR') or '/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/ex42_proto'
os.makedirs(SERVE, exist_ok=True)
raw = open(INS, 'rb').read(); assert hashlib.sha256(raw).hexdigest() == SHA, 'insumo mudou'
open(os.path.join(SERVE, 'orig.html'), 'wb').write(raw)
src = raw.decode('utf-8'); ANCORA = '\nrenderAll();\n})();'
assert src.count(ANCORA) == 1
EXPO = '\nwindow.__pdt={PEST,SAT,EVENTS,CLIMA,PIVOS,WATER,SCENES,SCENE_CLOUD,ALVOS,S,PROF,EQ,IDX,RAINMM,vigorEffect,pestAt,satAt,pestGlobal,satGlobal,DAYS};'
open(os.path.join(SERVE, 'instr.html'), 'w', encoding='utf-8').write(src.replace(ANCORA, EXPO + ANCORA))
# 'pub.html': o insumo dentro do esqueleto que o Artifact põe na publicação (doctype, charset e viewport); bytes do insumo intactos depois do esqueleto
ESQ = '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n'
open(os.path.join(SERVE, 'pub.html'), 'w', encoding='utf-8').write(ESQ + src)
L = open(os.path.join(OUT, 'p1_proto.log'), 'w', encoding='utf-8'); R = {}
port = server(SERVE, utf8=True); c = chrome(); J = c.js
U = lambda f: f'http://127.0.0.1:{port}/{f}'

def abre(f='pub.html', w=1440, h=1000, toque=False):
    c.aparelho(w, h, 1, toque); c.goto(U(f), .8); J("try{localStorage.clear()}catch(e){};1"); c.goto(U(f), 1.2)
def txt(sel): return J(f"(document.querySelector({json.dumps(sel)})||{{innerText:''}}).innerText.replace(/\\s+/g,' ').trim()") or ''
def dia(): return J("+document.getElementById('tl').getAttribute('aria-valuenow')")
def dval(): return J("document.getElementById('tl').getAttribute('aria-valuetext')")
def clica(sel, i=0): return J(f"(()=>{{const b=document.querySelectorAll({json.dumps(sel)})[{i}]; if(!b) return false; b.click(); return true;}})()")
def botao(texto, raiz='document'):
    return J(f"(()=>{{const b=[...{raiz}.querySelectorAll('button')].find(b=>b.innerText.replace(/\\s+/g,' ').trim()==={json.dumps(texto)}); if(!b) return false; b.click(); return true;}})()")
def foca_tl(): J("document.getElementById('tl').focus(); 1")
def tecla(k, shift=False):
    vk = {'ArrowLeft': 37, 'ArrowRight': 39, 'Home': 36, 'End': 35, 'PageUp': 33, 'PageDown': 34, 'Escape': 27}.get(k, 0)
    c.tecla(k, k, vk, mod=8 if shift else 0); time.sleep(.15)
def mapa_estados():
    return json.loads(J("JSON.stringify([...document.querySelectorAll('#map .pv')].map(b=>({id:b.querySelector('.id').innerText,cls:[...b.classList].filter(x=>x!=='pv').join(' '),bg:b.style.background,aria:b.getAttribute('aria-label'),w:Math.round(b.getBoundingClientRect().width)})))"))
def painel(): return txt('#panel')
def shot(n): c.shot(os.path.join(PNG, n)); log(L, '  captura', n)

# ---------- 0. dump dos dados internos (instr.html) ----------
abre('instr.html')
DADOS = json.loads(J(r"""JSON.stringify((()=>{const P=window.__pdt; const al={};
 P.ALVOS.forEach(a=>{ al[a.id]={nome:a.nome,nc:a.nc,un:a.un,med:a.med,piv:{}};
   Object.entries(P.PEST[a.id]).forEach(([pid,s])=>{ al[a.id].piv[pid]={obs:s.obs.map(o=>[o.day,o.v]),apps:s.apps.map(ap=>({day:ap.day,prod:ap.prod.c,nome:ap.prod.n,g:ap.prod.g,dose:ap.prod.dose,du:ap.prod.du,eq:ap.eq,entrada:ap.entrada,rep:ap.rep,consec:ap.consec,
     before:ap.before?[ap.before.day,ap.before.v]:null,after:ap.after?[ap.after.day,ap.after.v]:null,red:ap.red,backDay:ap.backDay}))}; }); });
 const sat={}; P.PIVOS.forEach(p=>{ sat[p.id]=P.SAT[p.id].scenes.map(s=>({day:s.day,cloud:s.cloud,ok:s.ok,NDVI:s.NDVI.med,NDRE:s.NDRE.med})); });
 const adub=P.EVENTS.filter(e=>e.kind==='adub').map(e=>({id:e.id,pid:e.pid,day:e.day,prog:e.prog,progNome:e.progNome,N:e.items.reduce((s,it)=>s+(it.nut.N||0),0),
   js:{NDVI:(x=>x?{b:x.before.day,a:x.after.day,d:x.d,dc:x.dc,rel:x.rel}:null)(P.vigorEffect(e,'NDVI')),NDRE:(x=>x?{b:x.before.day,a:x.after.day,d:x.d,dc:x.dc,rel:x.rel}:null)(P.vigorEffect(e,'NDRE'))}}));
 return {DAYS:P.DAYS,pivos:P.PIVOS.map(p=>({id:p.id,ha:p.ha,stage:p.stage,pestOff:p.pestOff})),clima:P.CLIMA,rain:P.RAINMM,water:Object.fromEntries(Object.entries(P.WATER).map(([k,v])=>[k,{suff:v.suff,irr:v.irr}])),
   prof:Object.fromEntries(Object.entries(P.PROF).map(([k,v])=>[k,{eq:v.eq,delay:v.delay,off:v.off}])),scenes:P.SCENES,sceneCloud:P.SCENE_CLOUD,idx:P.IDX,alvos:al,sat,adub,
   gAcaro:[...Array(P.DAYS+1).keys()].map(d=>{const g=P.pestGlobal(d); return [g.v,g.acima,g.sem,g.n];})};})())"""))
dump('proto_dados.json', DADOS); log(L, '0 dump: alvos', list(DADOS['alvos']), 'pivôs', len(DADOS['pivos']), 'adubações', len(DADOS['adub']))

# ---------- 1. 1440 × 1000 · pragas ----------
abre()
R['inicio'] = dict(crumb=txt('.crumb'), now=txt('#now'), measure=txt('#measure'), legend=txt('#legend'), keys=txt('#tlkeys'), toggles=txt('#toggles'),
                   painel=painel()[:1500], dia=dia(), valuetext=dval(), slider=J("(e=>({role:e.getAttribute('role'),label:e.getAttribute('aria-label'),tab:e.tabIndex}))(document.getElementById('tl'))"),
                   svg_aria=J("[...document.querySelectorAll('svg.chart')].map(s=>s.getAttribute('aria-hidden')+'|'+(s.getAttribute('role')||''))"),
                   tabela_equivalente=J("!!document.querySelector('#tlbox table, .time table')"), fonte_manrope=J("document.fonts.check('12px Manrope')"))
R['inicio']['mapa'] = mapa_estados(); log(L, '1 início', json.dumps({k: v for k, v in R['inicio'].items() if k != 'mapa'}, ensure_ascii=False)[:3000])
shot('proto_1440_pragas_hoje.png')
# teclado na barra de tempo
foca_tl(); seq = []
for k, sh in [('ArrowLeft', False), ('ArrowLeft', True), ('ArrowRight', False), ('PageUp', False), ('PageDown', False), ('Home', False), ('End', False)]:
    tecla(k, sh); seq.append([('Shift+' if sh else '') + k, dia(), dval()])
R['teclado'] = seq; log(L, '2 teclado', seq)
# arrastar (mouse): aperta a 60 % e arrasta até 40 % da largura do gráfico
r = json.loads(J("JSON.stringify(document.getElementById('tl').getBoundingClientRect())"))
y = r['y'] + r['height'] * .3; x1, x2 = r['x'] + r['width'] * .6, r['x'] + r['width'] * .4
c.mouse(x1, y, 'mousePressed', 'left'); d1 = dia(); traj = [d1]
for k in range(1, 6):
    c.mouse(x1 + (x2 - x1) * k / 5, y, 'mouseMoved', 'left'); traj.append(dia())
c.mouse(x2, y, 'mouseReleased', 'left'); R['arrasto'] = dict(trajetoria=traj, final=dia(), now=txt('#now')); log(L, '3 arrasto', R['arrasto'])
# passar o mouse (dica do dia)
c.mouse(r['x'] + r['width'] * .5, y); time.sleep(.3); R['dica_dia_apos_arrasto'] = txt('#tl .tip')
c.mouse(5, 5); time.sleep(.2); c.mouse(r['x'] + r['width'] * .5, y); time.sleep(.3); R['dica_dia'] = txt('#tl .tip')
log(L, '4 dica (após arrastar, sem sair):', repr(R['dica_dia_apos_arrasto']), '| depois de sair e voltar:', R['dica_dia'])
c.mouse(5, 5); time.sleep(.2)
# Reproduzir, Pausar, Hoje
J("document.getElementById('tl').focus();1"); tecla('Home'); [tecla('ArrowRight', True) for _ in range(10)]; d0 = dia()
botao('Reproduzir'); time.sleep(1.6); dp = dia(); btn_txt = txt('#play'); botao('Pausar'); time.sleep(.3); dpa = dia(); time.sleep(.6); dpa2 = dia()
botao('Hoje'); dh = dia()
R['reproduzir'] = dict(inicio=d0, apos_1_6s=dp, botao_durante=btn_txt, pausado=[dpa, dpa2], hoje=dh, valuetext_hoje=dval()); log(L, '5 reproduzir', R['reproduzir'])
c.call('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce'}]})
J("document.getElementById('tl').focus();1"); tecla('Home'); botao('Reproduzir'); time.sleep(1.35); R['reproduzir_menos_mov'] = dict(apos_1_35s=dia()); botao('Pausar')
c.call('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-motion', 'value': 'no-preference'}]}); botao('Hoje')
log(L, '5b menos movimento', R['reproduzir_menos_mov'])
# troca de alvo
R['alvos'] = {}
for a in ['Mosca-branca', 'Antracnose', 'Cochonilha', 'Ácaro-rajado']:
    botao(a); time.sleep(.3)
    R['alvos'][a] = dict(measure=txt('#measure'), now=txt('#now'), keys=txt('#tlkeys'), painel=painel()[:700])
log(L, '6 alvos', json.dumps(R['alvos'], ensure_ascii=False)[:2500])
# validade: dia em que um pivô mostra leitura com 8 a 14 dias (válida no protótipo, vencida pela PEND-13 de 7 dias)
J("document.getElementById('tl').focus();1"); tecla('End')
velhas = []
for k in range(0, 87):
    est = mapa_estados()
    for p in est:
        a = p['aria'] or ''
        if 'vistoria em' in a:
            velhas.append([dia(), p['id'], a])
    tecla('ArrowLeft')
    if dia() == 0: break
R['leituras_no_mapa'] = len(velhas); dump('proto_mapa_pragas_por_dia.json', velhas)
log(L, '7 rótulos de leitura no mapa (todos os dias, ácaro):', len(velhas))
# painel do talhão P4 · aplicação e janela
J("document.getElementById('tl').focus();1"); tecla('End')
J("[...document.querySelectorAll('#map .pv')].find(b=>b.querySelector('.id').innerText==='P4').click();1"); time.sleep(.4)
R['P4'] = dict(painel=painel()[:2500], primaria=J("[...document.querySelectorAll('#panel .btn.primary')].map(b=>b.innerText)")); shot('proto_1440_P4.png')
log(L, '8 P4', R['P4'])
clica('#panel .app', 0); time.sleep(.4); R['P4_pop'] = txt('.pop'); log(L, '9 pop P4', R['P4_pop']); shot('proto_1440_P4_pop.png')
R['pop_foco'] = J("document.activeElement.className+'|'+document.activeElement.getAttribute('aria-label')")
tecla('Escape'); R['esc1'] = dict(pop=J("!!document.querySelector('.pop')"), foco=J("document.activeElement.className"), sel=painel()[:40])
tecla('Escape'); R['esc2'] = dict(painel=painel()[:60]); log(L, '10 Esc', R['esc1'], R['esc2'])
# ícone com contagem na linha do tempo da fazenda
n_evt = J("document.querySelectorAll('#tlbox > .evt').length"); com_n = J("[...document.querySelectorAll('#tlbox > .evt')].filter(b=>b.querySelector('.n')).map(b=>b.getAttribute('aria-label'))")
R['icones_fazenda'] = dict(total=n_evt, com_contagem=com_n[:8], n_com_contagem=len(com_n))
i = J("[...document.querySelectorAll('#tlbox > .evt')].findIndex(b=>b.querySelector('.n')&&+b.querySelector('.n').innerText>=6)")
if i is not None and i >= 0:
    clica('#tlbox > .evt', i); time.sleep(.4); R['pop_contagem'] = txt('.pop'); shot('proto_1440_pop_contagem.png'); tecla('Escape')
log(L, '11 ícones', R['icones_fazenda'], (R.get('pop_contagem') or '')[:1500])
# o que funcionou: agrupamentos, hoje e no dia 50
R['oque'] = {}
for d in ['End', 50]:
    J("document.getElementById('tl').focus();1"); tecla('End')
    if d == 50:
        tecla('Home'); [tecla('ArrowRight', True) for _ in range(7)]; [tecla('ArrowRight') for _ in range(1)]
    for g in ['Produto', 'Produto e calda', 'Sequência', 'Clima da semana']:
        botao(g, "document.getElementById('panel')"); time.sleep(.25)
        R['oque'][f'{dia()}|{g}'] = dict(insights=J("[...document.querySelectorAll('#panel .insights li')].map(l=>l.innerText)"),
            linhas=J("[...document.querySelectorAll('#panel .tbl tbody tr')].map(r=>[...r.cells].map(c=>c.innerText.replace(/\\s+/g,' ').trim()))"),
            cab=J("[...document.querySelectorAll('#panel .tbl th')].map(t=>t.innerText+'|'+t.getAttribute('aria-sort'))"), rodape=J("[...document.querySelectorAll('#panel > .pb > .note')].map(n=>n.innerText).slice(-1)[0]||''"))
botao('Produto', "document.getElementById('panel')"); shot('proto_1440_oque_funcionou_dia50.png')
J("document.getElementById('tl').focus();1"); tecla('End'); botao('Produto', "document.getElementById('panel')"); shot('proto_1440_oque_funcionou_hoje.png')
log(L, '12 o que funcionou', json.dumps(R['oque'], ensure_ascii=False)[:6000])

# ---------- 2. 1440 · Satélite ----------
botao('Satélite'); time.sleep(.4)
R['sat'] = dict(measure=txt('#measure'), legend=txt('#legend'), now=txt('#now'), keys=txt('#tlkeys'), painel=painel()[:1500], contraste=J("[...document.querySelectorAll('#scale button')].map(b=>b.innerText)"),
               indices=J("[...document.querySelectorAll('#subs button')].map(b=>b.innerText)"))
shot('proto_1440_sat_hoje.png'); log(L, '13 sat', json.dumps(R['sat'], ensure_ascii=False)[:3000])
botao('NDRE'); time.sleep(.3); R['sat_ndre_legend'] = txt('#legend'); botao('Fazenda'); time.sleep(.3); R['sat_ndre_fazenda_legend'] = txt('#legend'); botao('Absoluto'); botao('NDVI')
log(L, '14 NDRE', R['sat_ndre_legend'], '| Fazenda:', R['sat_ndre_fazenda_legend'])
# varre todos os dias: nenhum pivô com nuvem ou sem imagem pode ter cor de índice
J("document.getElementById('tl').focus();1"); tecla('Home'); viol = []; cont = {'cloud': 0, 'nodata': 0, 'ok': 0}; dias_nuvem = []
for k in range(0, 87):
    est = mapa_estados(); dd = dia(); n_cl = 0
    for p in est:
        if 'cloud' in p['cls'] or 'nodata' in p['cls']:
            cont['cloud' if 'cloud' in p['cls'] else 'nodata'] += 1; n_cl += 'cloud' in p['cls']
            if 'var(--c' in (p['bg'] or ''): viol.append([dd, p['id'], p['cls'], p['bg']])
        elif 'nocrop' not in p['cls']: cont['ok'] += 1
    if n_cl: dias_nuvem.append([dd, n_cl])
    if dd == 86: break
    tecla('ArrowRight')
R['sat_varredura'] = dict(violacoes=viol, contagem=cont, dias_com_nuvem=dias_nuvem); log(L, '15 varredura sat', R['sat_varredura'])
# um dia com nuvem para a captura
if dias_nuvem:
    alvo_d = dias_nuvem[0][0]; J("document.getElementById('tl').focus();1"); tecla('Home'); [tecla('ArrowRight') for _ in range(alvo_d)]
    shot('proto_1440_sat_nuvem.png'); R['sat_nuvem'] = dict(dia=dia(), legend=txt('#legend'), pv=[p for p in mapa_estados() if 'cloud' in p['cls']][:4])
J("document.getElementById('tl').focus();1"); tecla('End')
J("[...document.querySelectorAll('#map .pv')].find(b=>b.querySelector('.id').innerText==='P9').click();1"); time.sleep(.4)
R['sat_P9'] = painel()[:2500]; shot('proto_1440_sat_P9.png'); log(L, '16 sat P9', R['sat_P9'])
clica('#panel .app', 0); time.sleep(.4); R['sat_P9_pop'] = txt('.pop'); log(L, '17 pop sat', R['sat_P9_pop']); tecla('Escape'); tecla('Escape')
R['oque_sat'] = {}
for g in ['Programa', 'Dose de N', 'Estádio', 'Calor e água']:
    botao(g, "document.getElementById('panel')"); time.sleep(.25)
    R['oque_sat'][g] = dict(insights=J("[...document.querySelectorAll('#panel .insights li')].map(l=>l.innerText)"),
        linhas=J("[...document.querySelectorAll('#panel .tbl tbody tr')].map(r=>[...r.cells].map(c=>c.innerText.replace(/\\s+/g,' ').trim()))"))
log(L, '18 o que melhorou o vigor', json.dumps(R['oque_sat'], ensure_ascii=False)[:4000])
R['erros_js_1440'] = J("window.__errs||[]")

# ---------- 3. 390 × 844 · toque ----------
abre(w=390, h=844, toque=True)
med = J(r"""(()=>{const sz=s=>[...document.querySelectorAll(s)].filter(e=>e.getClientRects().length).map(e=>{const r=e.getBoundingClientRect(); return [Math.round(r.width),Math.round(r.height)];});
 const mn=a=>a.length?[Math.min(...a.map(x=>x[0])),Math.min(...a.map(x=>x[1]))]:null;
 return {scrollW:document.documentElement.scrollWidth,innerW:innerWidth,pv:mn(sz('#map .pv:not(.nocrop)')),evt:mn(sz('#tlbox > .evt')),tg:mn(sz('.tg')),seg:mn(sz('.seg button')),btn:mn(sz('.btn')),tl:sz('#tl')[0],
  abaixo44:{pv:sz('#map .pv:not(.nocrop)').filter(x=>x[0]<44).length,pv_total:sz('#map .pv:not(.nocrop)').length,evt:sz('#tlbox > .evt').filter(x=>x[1]<44).length,evt_total:sz('#tlbox > .evt').length,seg:sz('.seg button').filter(x=>x[1]<44).length,tg:sz('.tg').filter(x=>x[1]<44).length,btn:sz('.btn').filter(x=>x[1]<44).length}};})()""")
R['m390'] = med; log(L, '19 390 medidas', med); shot('proto_390_inicio.png')
# arrastar com o dedo na linha do tempo
r = json.loads(J("JSON.stringify(document.getElementById('tl').getBoundingClientRect())")); J("window.scrollTo(0,0);1")
y = r['y'] + r['height'] * .3; d_ini = dia()
c.call('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': r['x'] + r['width'] * .7, 'y': y}]}); time.sleep(.1)
for k in range(1, 6):
    c.call('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': r['x'] + r['width'] * (.7 - .08 * k), 'y': y}]}); time.sleep(.08)
c.call('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); time.sleep(.3)
R['m390_arrasto_dedo'] = dict(antes=d_ini, depois=dia(), scrollY=J("scrollY")); log(L, '20 arrasto dedo', R['m390_arrasto_dedo'])
# tocar no P4 (de volta a hoje)
botao('Hoje'); time.sleep(.3)
b = json.loads(J("JSON.stringify((b=>{b.scrollIntoView({block:'center'}); const r=b.getBoundingClientRect(); return {x:r.x+r.width/2,y:r.y+r.height/2};})([...document.querySelectorAll('#map .pv')].find(b=>b.querySelector('.id').innerText==='P4')))"))
c.toque(b['x'], b['y']); time.sleep(.4)
R['m390_P4'] = dict(painel=painel()[:300], painel_top=J("Math.round(document.getElementById('panel').getBoundingClientRect().top)"), vh=844)
J("document.getElementById('panel').scrollIntoView();1"); time.sleep(.2); shot('proto_390_P4.png')
R['m390_P4']['app_btn'] = J("[...document.querySelectorAll('#panel .app')].slice(0,2).map(e=>{const r=e.getBoundingClientRect(); return [Math.round(r.width),Math.round(r.height)];})")
R['m390_P4']['evt_painel'] = J("[...document.querySelectorAll('#panel .evt')].map(e=>{const r=e.getBoundingClientRect(); return [Math.round(r.width),Math.round(r.height)];})")
clica('#panel .app', 0); time.sleep(.4)
R['m390_pop'] = dict(txt=txt('.pop')[:600], caixa=J("(p=>p?(r=>[Math.round(r.left),Math.round(r.width),Math.round(r.top),Math.round(r.height)])(p.getBoundingClientRect()):null)(document.querySelector('.pop'))"), innerW=390)
shot('proto_390_pop.png'); log(L, '21 390 P4', R['m390_P4'], R['m390_pop'])
R['erros_js_390'] = J("window.__errs||[]")
dump('p1_proto.json', R); log(L, 'FIM')
