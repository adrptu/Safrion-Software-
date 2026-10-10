# -*- coding: utf-8 -*-
"""Sonda V55-RESP-01 (PR #47, comentários 6093961455 e 6096401790): geometria e acionamento real do avanço "Dimensionar operações ›"
do Planejar safra, etapa 2 (SAF #saf=S2627&etapa=2), com a busca focada e o aviso temporário REAL na tela (não se espera ele sumir
nem se esconde nada).
Dimensões: 360×420 (360×800 com a busca focada e a janela reduzida a 420 = teclado virtual aberto, como o caso 18 do
acao_unica_test.py responsivo), a mesma com env(safe-area-inset-bottom) = 34 px (Emulation.setSafeAreaInsetsOverride: barra de gesto
do iPhone) e as de controle 390×844 (toque) e 1440×900 (mouse), sem teclado.
Avisos reais da etapa 2:
  carga  "Safra aberta: Safra 2026/27 · Cultivos e planos" (ao abrir a tela; dura 4,5 s);
  longo  o mais longo que a etapa 2 produz: "Aplicar plano em 4 cultivos" com a P2 em sobreposição
         ("Soja alta tecnologia v6 aplicado a 4 cultivos. Com pendência: P2: sobreposição prevista de 11 dias. …", ~340 caracteres).
Para cada dimensão × aviso, em carga nova da tela:
  geo     antes e depois do scrollIntoView({block:'center'}) do avanço: retângulo do botão, viewport visual × de layout,
          elementFromPoint/elementsFromPoint no centro, aviso (limites, altura, linhas, texto), --aviso-h, safe-area, margem da
          área e margem de rolagem do botão, cadeia de rolagem (overflow, alturas, position) e elementos fixed/sticky;
  toque   toque real no centro do botão logo depois de rolar (Input.dispatchTouchEvent; mouse a 1440), com o aviso na tela;
  fim     rolagem da casca até o fim: o elemento no centro de cada controle da área (o aviso cobre algum?); depois cada controle levado
          à vista (scrollIntoView nearest, como o foco por Tab): livre?;
  tab     "T" digitado na busca (tecla real); Tab rápido da busca até o avanço (1ª passada conta as paradas, 2ª chega com o aviso
          na tela): controle focado, retângulo, elementFromPoint no centro, aviso no foco e no Enter; Enter (tecla real) → etapa;
          depois "‹ Cultivos e planos" volta à etapa 2: a busca e a tabela de cultivos e planos (rascunho da safra) iguais às de antes.
Uso (da pasta do gerador): python3 <esta sonda> <dir _render> <saída .json> [prefixo das capturas] [dims com captura, ex.: 360x420_teclado]
Chrome headless com emulação (largura × altura em px CSS, escala, toque): não é aparelho físico."""
import sys, os, time, json
GEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'tools', 'prototipo', 'v37', 'gen37')
sys.path.insert(0, os.path.abspath(GEN))
from comp_lib import Chrome, servir
RENDER = sys.argv[1]; SAIDA = sys.argv[2]; CAP = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(SAIDA)[0]
COM_CAP = (sys.argv[4].split(',') if len(sys.argv) > 4 else None)
p, srv = servir(RENDER); c = Chrome(); J = c.js
BTN = "document.querySelector('[data-acoes] [data-acao=avancar]')"
NOME = r"""(e=>e?(e.tagName.toLowerCase()+(e.id?'#'+e.id:'')+(e.className&&typeof e.className==='string'&&e.className.trim()?'.'+e.className.trim().split(/\s+/).join('.'):'')+(e.dataset&&e.dataset.acao?'[data-acao='+e.dataset.acao+']':'')+(e.getAttribute&&e.getAttribute('role')?'[role='+e.getAttribute('role')+']':'')).slice(0,90):null)"""
RET = "(e=>{ if(!e) return null; const r=e.getBoundingClientRect(); return {x:Math.round(r.left),y:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height),bottom:Math.round(r.bottom)}; })"
AVISO = f"""(()=>{{ const t=[...document.querySelectorAll('[role=status]')].find(x=>x.getClientRects().length&&x.getBoundingClientRect().height>2&&getComputedStyle(x).position==='fixed'); if(!t) return null;
  const rg=document.createRange(); rg.selectNodeContents(t); const linhas=new Set([...rg.getClientRects()].filter(r=>r.width>0).map(r=>Math.round(r.top))).size;
  return {{txt:t.innerText.trim(), car:t.innerText.trim().length, linhas, ret:({RET})(t), faixaDoPe:Math.round(innerHeight-t.getBoundingClientRect().top)}}; }})()"""
SAFE = "(()=>{ const d=document.createElement('div'); d.style.cssText='position:fixed;left:0;bottom:0;width:1px;height:0;padding-bottom:env(safe-area-inset-bottom,0px);visibility:hidden'; document.body.appendChild(d); const v=getComputedStyle(d).paddingBottom; d.remove(); return v; })()"
GEO = f"""((rotulo)=>{{ const nome={NOME}, R={RET};
 const a=document.querySelector('[data-acoes]'); const b={BTN};
 const vv=window.visualViewport; const out={{rotulo, inner:[innerWidth,innerHeight], docClient:[document.documentElement.clientWidth,document.documentElement.clientHeight],
   visual:vv?{{w:Math.round(vv.width),h:Math.round(vv.height),offsetTop:Math.round(vv.offsetTop),pageTop:Math.round(vv.pageTop),scale:vv.scale}}:null,
   foco:nome(document.activeElement), botao:b?{{txt:b.innerText.trim(),ret:R(b),margemRolagem:getComputedStyle(b).scrollMarginBottom}}:null,
   area:a?{{ret:R(a),pos:getComputedStyle(a).position,margemBaixo:getComputedStyle(a).marginBottom}}:null,
   aviso:{AVISO}, avisoH:getComputedStyle(document.documentElement).getPropertyValue('--aviso-h'), acoesH:getComputedStyle(document.documentElement).getPropertyValue('--acoes-h'), safe:{SAFE}}};
 if(b){{ const r=b.getBoundingClientRect(); const cx=r.left+r.width/2, cy=r.top+r.height/2; const h=document.elementFromPoint(cx,cy);
   out.centro=[Math.round(cx),Math.round(cy)]; out.noCentro=nome(h); out.noCentroEhBotao=!!h&&(h===b||b.contains(h));
   out.pilhaNoCentro=document.elementsFromPoint(cx,cy).slice(0,6).map(nome);
   const cad=[]; for(let e=b.parentElement;e;e=e.parentElement){{ const cs=getComputedStyle(e); if(cs.overflowY!=='visible'||cs.position!=='static'||e===document.documentElement||e.tagName==='MAIN') cad.push({{el:nome(e),overflowY:cs.overflowY,position:cs.position,height:cs.height,clientH:e.clientHeight,scrollH:e.scrollHeight,scrollTop:Math.round(e.scrollTop),scrollPaddingBottom:cs.scrollPaddingBottom,ret:R(e)}}); }}
   out.cadeia=cad; }}
 out.fixos=[...document.querySelectorAll('body *')].filter(e=>{{ const p=getComputedStyle(e).position; return (p==='fixed'||p==='sticky')&&e.getClientRects().length&&e.getBoundingClientRect().height>1&&!e.classList.contains('g2c0'); }}).map(e=>({{el:nome(e),pos:getComputedStyle(e).position,z:getComputedStyle(e).zIndex,ret:R(e)}})).slice(0,8);
 return out; }})"""
# controles da área com a casca (ou o main) rolada até o fim: quem está no centro de cada um
FIM = f"""(()=>{{ const nome={NOME}; const col=document.querySelector('.ml-tog+div'); const m=document.querySelector('main[data-scroll]');
 [col,m].forEach(x=>{{ if(x) x.scrollTop=x.scrollHeight; }});
 const a=document.querySelector('[data-acoes]'); const bs=[...a.querySelectorAll('button,a')].filter(x=>x.getClientRects().length);
 return {{aviso:{AVISO}, avisoH:getComputedStyle(document.documentElement).getPropertyValue('--aviso-h'), margemBaixo:getComputedStyle(a).marginBottom,
   controles:bs.map(b=>{{ const r=b.getBoundingClientRect(); const y=Math.min(r.top+r.height/2,innerHeight-1); const h=document.elementFromPoint(r.left+r.width/2,y);
     return {{txt:b.innerText.trim().slice(0,40), ret:[Math.round(r.top),Math.round(r.bottom)], noCentro:nome(h), livre:!!h&&(h===b||b.contains(h)), sobAviso:!!h&&!!h.closest('[role=status]')}}; }}),
   alcance:bs.map(b=>{{ b.scrollIntoView({{block:'nearest'}}); const r=b.getBoundingClientRect(); const h=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
     return {{txt:b.innerText.trim().slice(0,40), ret:[Math.round(r.top),Math.round(r.bottom)], livre:!!h&&(h===b||b.contains(h)), sobAviso:!!h&&!!h.closest('[role=status]')}}; }})}}; }})()"""
TABELA = "(()=>[...document.querySelectorAll('main [role=table]')].filter(t=>t.offsetParent).map(t=>[...t.querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim()).join(' | ')).join(' || '))()"
BUSCA = "(()=>{const i=document.querySelector('main input[type=search]'); return i?{valor:i.value, focada:document.activeElement===i}:null;})()"
def geo(rot): return J(f"({GEO})({json.dumps(rot)})")
def etapa(): return J("(()=>{const c=document.querySelector('.etp-ind [aria-current=step]'); return c?Number((c.innerText.match(/\\d+/)||[0])[0]):0;})()")
def tab_rapido(n):
    for _ in range(n):
        c.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'Tab', 'code': 'Tab', 'windowsVirtualKeyCode': 9})
        c.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'Tab', 'code': 'Tab', 'windowsVirtualKeyCode': 9})
def foca_busca(): J("(()=>{const i=document.querySelector('main input[type=search]'); i.scrollIntoView({block:'center'}); i.focus();})()")
def prepara(w, h, e, t, teclado, aviso, safe=0):
    c.aparelho(w, 800 if teclado else h, e, t); c.call('Emulation.setSafeAreaInsetsOverride', {'insets': {'bottom': safe, 'bottomMax': safe}})
    c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .2); J("localStorage.clear(); sessionStorage.clear()")
    c.goto(f'http://127.0.0.1:{p}/SAF.dc.html#saf=S2627&etapa=2', .6); time.sleep(.2)
    foca_busca()
    if teclado: c.aparelho(w, h, e, t); time.sleep(.5)
    if aviso == 'longo':   # o aviso mais longo da etapa: aplicar o plano aos 4 cultivos (a P2 recebe com pendência)
        r = J("(()=>{const b=document.querySelector('[data-acoes] [data-acao=resolver]'); if(!b) return 'sem resolver'; b.click(); return b.innerText.trim();})()"); time.sleep(.6)
        r2 = J("(()=>{const d=document.querySelector('aside[role=dialog]'); if(!d) return 'sem painel'; const b=[...d.querySelectorAll('button')].filter(b=>b.getClientRects().length).find(b=>b.innerText.trim().startsWith('Aplicar plano')); if(!b) return 'sem Aplicar'; b.click(); return b.innerText.trim();})()"); time.sleep(.5)
        foca_busca(); time.sleep(.2)
        return [r, r2]
    return []
def toca(x, y, toque):
    if toque: c.toque(x, y)
    else:
        c.mouse(x, y); c.mouse(x, y, 'mousePressed', 'left'); c.mouse(x, y, 'mouseReleased', 'left'); time.sleep(.35)
def shot(nome, tag):
    if COM_CAP is None or tag in COM_CAP: c.shot(nome)
DIMS = [('360x420_teclado', 360, 420, 3, True, True, 0), ('360x420_teclado_safe34', 360, 420, 3, True, True, 34), ('390x844', 390, 844, 3, True, False, 0), ('1440x900', 1440, 900, 1, False, False, 0)]
out = {'render': RENDER, 'dims': {}}
try:
    for tag, w, h, e, t, tecl, sf in DIMS:
        for av in ('carga', 'longo'):
            d = out['dims'][f'{tag} · {av}'] = {}
            cap = f'{CAP}_{tag}_{av}'
            # 1 · geometria antes/depois de rolar e toque logo depois de rolar (o aviso real na tela)
            d['preparo'] = prepara(w, h, e, t, tecl, av, sf); d['antes_rolar'] = geo('antes do scrollIntoView')
            J(BTN + ".scrollIntoView({block:'center'})")
            d['depois_rolar'] = g = geo('depois do scrollIntoView({block:center})'); shot(cap + '_b_depois_rolar.png', tag)
            e0 = etapa(); r = g['botao']['ret']; x = r['x'] + r['w'] / 2; y = r['y'] + r['h'] / 2
            toca(x, y, t); time.sleep(.6)
            d['toque'] = {'tipo': 'toque' if t else 'mouse', 'ponto': [round(x), round(y)], 'noCentro': g.get('noCentro'), 'aviso_no_toque': g['aviso'], 'etapa_antes': e0, 'etapa_depois': etapa()}
            # 2 · fim da rolagem com o aviso real na tela: nenhum controle da área sob o aviso
            prepara(w, h, e, t, tecl, av, sf); d['fim'] = J(FIM); shot(cap + '_d_fim_rolagem.png', tag)
            # 3 · teclado: "T" na busca (tecla real), Tab da busca até o avanço e Enter; busca e rascunho preservados
            def comeca():
                prepara(w, h, e, t, tecl, av, sf); c.call('Input.insertText', {'text': 'T'}); time.sleep(.35)
            comeca(); antes = {'busca': J(BUSCA), 'tabela': J(TABELA)}; n = 0; achou = False
            for k in range(200):
                tab_rapido(1); n += 1
                if J("(()=>{const a=document.activeElement; return !!a&&a.matches('[data-acoes] [data-acao=avancar]');})()"): achou = True; break
            comeca(); e0 = etapa(); t0 = time.time(); tab_rapido(n); time.sleep(.15)
            foc = J("(()=>{const a=document.activeElement; return !!a&&a.matches('[data-acoes] [data-acao=avancar]');})()")
            gk = geo('foco no avanço por Tab'); shot(cap + '_e_foco_tab.png', tag)
            busca_enter = J(BUSCA); av_enter = J(AVISO); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.7); e1 = etapa(); seg = round(time.time() - t0, 2)
            volta = J("(()=>{const b=document.querySelector('[data-acoes] [data-acao=voltar]'); if(!b) return ''; const t=b.innerText.trim(); b.click(); return t;})()"); time.sleep(.6)
            depois = {'etapa': etapa(), 'busca': J(BUSCA), 'tabela': J(TABELA)}
            d['teclado'] = {'tabs': n, 'achou_na_1a_passada': achou, 'focado_na_2a': foc, 'foco': gk['foco'], 'seg_ate_enter': seg, 'aviso_no_foco': gk['aviso'], 'aviso_no_enter': av_enter,
                            'botao_focado': gk['botao'], 'noCentro': gk.get('noCentro'), 'noCentroEhBotao': gk.get('noCentroEhBotao'), 'busca_no_enter': busca_enter,
                            'etapa_antes': e0, 'etapa_depois': e1, 'voltou_por': volta, 'antes': antes, 'depois_de_voltar': depois,
                            'busca_preservada': bool(antes['busca']) and depois['busca'] is not None and depois['busca']['valor'] == antes['busca']['valor'],
                            'rascunho_preservado': bool(antes['tabela']) and depois['tabela'] == antes['tabela']}
            ga = g['aviso'] or {}; fa = d['fim']['aviso'] or {}
            print(f'{tag} · {av}', json.dumps({'aviso': [ga.get('car'), ga.get('linhas'), (ga.get('ret') or {}).get('h'), ga.get('faixaDoPe')], 'avisoH': g['avisoH'], 'safe': g['safe'],
                  'margem': [g['area']['margemBaixo'], g['botao']['margemRolagem']], 'botao': [g['botao']['ret']['y'], g['botao']['ret']['bottom']], 'centro': g.get('noCentro'),
                  'toque': [d['toque']['etapa_antes'], d['toque']['etapa_depois']], 'fim': [[x['txt'][:14], x['livre'], x['sobAviso']] for x in d['fim']['controles']], 'alcance': [x['livre'] for x in d['fim']['alcance']], 'fim_aviso': bool(fa),
                  'tab': [n, foc, d['teclado']['noCentroEhBotao'], bool(gk['aviso']), bool(av_enter), e0, e1, seg], 'busca_rascunho': [d['teclado']['busca_preservada'], d['teclado']['rascunho_preservado'], (busca_enter or {}).get('valor')]},
                  ensure_ascii=False), flush=True)
finally:
    json.dump(out, open(SAIDA, 'w'), ensure_ascii=False, indent=1)
    c.close(); srv.terminate()
