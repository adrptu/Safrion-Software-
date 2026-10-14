# -*- coding: utf-8 -*-
"""Contrato Codex 6178891896: integração SAF-TAB sobre c8fe804; dados sintéticos.
Complementa saf_fazendas_test (criar/remover/envio parcial) sem editar autoria Claude.
Executar: python3 saf_faz2_integracao_codex_test.py; RENDER_DIR escolhe contraprova.
Emulação Chrome a 1440/390; não comprova aparelho físico. Sem hook de todas as colunas.
"""
import json
import os
import time
from pathlib import Path
from comp_lib import Chrome, servir

HERE = Path(__file__).resolve().parent
R = os.environ.get('RENDER_DIR', str(HERE / '_render'))
results = []
p, srv = servir(R)
c = Chrome()
c.call("Page.addScriptToEvaluateOnNewDocument", {"source": "try{localStorage.clear();sessionStorage.clear()}catch(e){}"})
J = c.js
G = '[data-g2g=g_cult_S2627]'
ROW = "[...document.querySelectorAll('%s [role=row].g2ed')].find(r=>/^T7(?:\\s|$)/.test(r.innerText))" % G

def check(name, ok, detail=None):
    results.append(dict(name=name, ok=bool(ok), detail=detail))
    print(('OK ' if ok else 'FALHA ') + name + ' ' + json.dumps(detail, ensure_ascii=False), flush=True)

def wait(expr, limit=5):
    until = time.monotonic() + limit
    while time.monotonic() < until:
        if J('(()=>{try{return !!(' + expr + ')}catch(e){return false}})()'):
            return True
        time.sleep(.1)
    return False

case_id = 0
def open_seed(width):
    global case_id
    case_id += 1
    c.aparelho(width, 950 if width > 400 else 844, 1 if width > 400 else 2, width < 400)
    c.goto(f'http://127.0.0.1:{p}/SAF.dc.html?codex_case={case_id}#saf=S2627&etapa=2', .3)
    assert wait(ROW), 'Tabela não abriu'

def click(expr):
    return J('(()=>{const e=' + expr + ';if(!e)return false;e.click();return true})()')

try:
    for width in (1440, 390):
        open_seed(width)
        heads = J("[...document.querySelectorAll('%s [role=columnheader]')].filter(e=>e.getClientRects().length).map(e=>e.innerText).filter(t=>t.trim())" % G)
        check(f'{width}: conjunto essencial de colunas', len(heads) == (5 if width > 400 else 3), heads)
        pending = J("[...document.querySelectorAll('%s [role=img]')].map(e=>e.getAttribute('aria-label')).filter(t=>t&&t.startsWith('Situação:'))" % G)
        check(f'{width}: pendência tem nome acessível independente de cor', any('A conferir' in x for x in pending), pending)
        text = J("document.querySelector('main').innerText")
        check(f'{width}: pendência tem destino visível sem hover', 'a conferir' in text.lower(), text[-550:])
        # O teclado chega à linha e ao botão oculto por hover, sem chamar click no botão.
        J('(()=>{const r=' + ROW + ';r.scrollIntoView({block:"center"});r.focus()})()')
        c.tab()
        wait("document.activeElement.innerText==='Dividir'&&getComputedStyle(document.activeElement).opacity==='1'")
        focused = J("({text:document.activeElement.innerText,opacity:getComputedStyle(document.activeElement).opacity})")
        check(f'{width}: Tab alcança Dividir visível', focused.get('text') == 'Dividir' and focused.get('opacity') == '1', focused)
        if width == 1440:
            c.tecla('Enter', 'Enter', 13, '\r')
        else:
            point = J("(()=>{const b=document.activeElement; b.scrollIntoView({block:'center'});const r=b.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2,r.width,r.height]})()")
            c.toque(point[0], point[1])
        check(f'{width}: ativar Dividir abre diálogo', wait("document.querySelector('aside[role=dialog]')"), J("(document.querySelector('aside[role=dialog]')||{}).getAttribute?.('aria-label')"))
        # Nova entrada limpa: painel por Enter na linha, depois rascunho sem salvar.
        open_seed(width)
        J('('+ROW+').focus()')
        c.tecla('Enter', 'Enter', 13, '\r')
        panel = wait("document.getElementById('fx_g_cult_S2627_var')")
        check(f'{width}: Enter na linha abre detalhe do cultivo', panel)
        if not panel:
            continue
        J("(()=>{const e=document.getElementById('fx_g_cult_S2627_var');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,'Formosa rascunho Codex');e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))})()")
        draft = J('JSON.stringify(window.__safSelf.state.g2.g_cult_S2627.fm.draft)')
        # Abrir seletor durante um rascunho é contraprova de estado por eventos DOM, não gesto de toque atrás do modal.
        click("document.querySelector('[data-g2cvb=g_cult_S2627]')")
        if wait("document.querySelector('[data-g2cv=g_cult_S2627]')"):
            click("[...document.querySelectorAll('[data-g2cv=g_cult_S2627] label')].find(e=>e.innerText.trim()==='Meta').querySelector('input')")
            same = J('JSON.stringify(window.__safSelf.state.g2.g_cult_S2627.fm.draft)')
            check(f'{width}: escolha de colunas preserva rascunho', draft == same and 'rascunho Codex' in same, {'before':draft,'after':same})
            click("[...document.querySelectorAll('[data-g2cv=g_cult_S2627] button')].find(e=>e.innerText.trim()==='Fechar')")
            focus = wait("document.activeElement?.getAttribute('data-g2cvb')==='g_cult_S2627'")
            check(f'{width}: fechar seletor devolve foco ao acionador', focus)
        else:
            check(f'{width}: escolha de colunas preserva rascunho', False, 'seletor indisponível')
        open_seed(width)
        # Busca real persiste ao mostrar coluna; área exibida conserva unidade.
        search = "[...document.querySelectorAll('main input[type=search]')].find(e=>e.getClientRects().length)"
        J('(()=>{const e='+search+';Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value").set.call(e,"T7");e.dispatchEvent(new Event("input",{bubbles:true}));e.dispatchEvent(new Event("change",{bubbles:true}))})()')
        wait("document.querySelectorAll('%s [role=row].g2ed').length===1" % G)
        click("document.querySelector('[data-g2cvb=g_cult_S2627]')")
        wait("document.querySelector('[data-g2cv=g_cult_S2627]')")
        label = J("[...document.querySelectorAll('[data-g2cv=g_cult_S2627] label')].map(e=>e.innerText)") or []
        area_label = next((x for x in label if x.strip() in ('Área', 'Área (ha)')), '')
        if area_label:
            J("(()=>{const l=[...document.querySelectorAll('[data-g2cv=g_cult_S2627] label')].find(e=>e.innerText==="+json.dumps(area_label)+");const i=l.querySelector('input');if(!i.checked)i.click()})()")
        filtered = J("[...document.querySelectorAll('%s [role=row].g2ed')].map(e=>e.innerText).filter(t=>t.trim())" % G)
        check(f'{width}: colunas preservam busca e unidade da área', len(filtered)==1 and 'T7' in filtered[0] and '42 ha' in filtered[0], filtered)
    # Contrato de leitura na fronteira tela→domínio, extraído das fontes reais (não é E2E).
    source = (HERE / 'safra.js').read_text()
    info_fn = source[source.index('function sgInfo('):source.index('// envio das fazendas', source.index('function sgInfo('))]
    domain = (HERE / 'safra_grupo.js').read_text()
    boundary = """const G={mae:'M',nome:'Teste',subs:[{id:'A',faz:'Fazenda A',estado:'Rascunho'},{id:'B',faz:'Fazenda B',estado:'Em planejamento'}]};
const cultsDe=(self,id)=>id==='A'?[{v:{area:''}}]:[{v:{area:5}}];const solMap=()=>({});
const I=sgInfo({},G,false);const L=sgLeitura(G,I);
const U=sgLeitura(G,{A:{area_ha:null,demanda:[{insumo:'X',un:'kg',qtd:2}]},B:{area_ha:5,demanda:[{insumo:'X',un:'L',qtd:3}]}});
return {I,L,U};"""
    boundary_result = J('(function(){'+domain+'\n'+info_fn+'\n'+boundary+'})()')
    check('Fronteira tela-domínio: área ausente não vira total completo',
          boundary_result['L']['area']['completa'] is False, boundary_result['L']['area'])
    sums=boundary_result['U']['demanda']['porInsumo']
    check('Leitura mantém unidades separadas e estados por fazenda',
          sorted((x['un'], x['qtd']) for x in sums)==[('L',3),('kg',2)] and len(boundary_result['L']['estados'])==2,
          {'somas':sums,'estados':boundary_result['L']['estados']})
finally:
    c.close()
    srv.terminate()
    srv.wait(timeout=5)
print(json.dumps(results, ensure_ascii=False, indent=2))
print(f'RESULTADO: {sum(x["ok"] for x in results)}/{len(results)}')
raise SystemExit(0 if all(x['ok'] for x in results) else 1)
