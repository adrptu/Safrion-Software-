# -*- coding: utf-8 -*-
"""Contrato6179422559: contraprovas V2-3 sobre758a396; autoria Codex.
Dados sintéticos, Chrome isolado1440/390. RENDER_DIR permite contraprova.
Verifica quadro inteiro no HTML; amostra UI CD04/CD05/IR01; fronteiras puras
de grupos/unidades. Não equivale a auditoria de todas as formas ou aparelho físico.
"""
import json
import os
import re
import sys
import time
from pathlib import Path
from visoes_marcas import QUADRO

HERE = Path(__file__).resolve().parent
R = Path(os.environ.get('RENDER_DIR', HERE / '_render'))
results = []
def check(name, ok, detail=None):
    results.append(dict(name=name, ok=bool(ok), detail=detail))
    print(('OK ' if ok else 'FALHA ') + name + ' ' + json.dumps(detail, ensure_ascii=False), flush=True)

# O oráculo é o quadro aprovado; nenhum caso ausente pode desaparecer da coleta.
errors = []
for (page, gid), expected in QUADRO.items():
    text = (R / page).read_text()
    match = re.search(r'const GRIDS = (\[.*?\]);\nconst NAV', text, re.S)
    grids = json.loads(match.group(1)) if match else []
    selected = [g for g in grids if g['id']==gid or gid.endswith('*') and g['id'].startswith(gid[:-1])]
    if not selected: errors.append([page,gid,'ausente'])
    for g in selected:
        got = [x['l'] for x in sorted((x for x in g['cols'] if x.get('ess')),key=lambda x:x['ess'])]
        if got != expected: errors.append([page,g['id'],got,expected])
check('Quadro completo: Abre com na ordem e nenhuma grade omitida', not errors, errors)
if '--quadro' in sys.argv: raise SystemExit(1 if errors else 0)

# O modo estático não exige navegador nem importa a descoberta do executável.
from comp_lib import Chrome, servir

p, server = servir(str(R))
c = Chrome()
J = c.js
def wait(expr, limit=3):
    end = time.monotonic()+limit
    while time.monotonic()<end:
        if J('(()=>{try{return !!('+expr+')}catch(e){return false}})()'): return True
        time.sleep(.08)
    return False
def select(css, value):
    J("(()=>{const e=document.querySelector("+json.dumps(css)+");e.value="+json.dumps(value)+";e.dispatchEvent(new Event('change',{bubbles:true}))})()")
    time.sleep(.25)
def click(expr):
    ok = J('(()=>{const e='+expr+';if(!e)return false;e.click();return true})()')
    time.sleep(.2)
    return ok
def query(css):
    return 'document.querySelector('+json.dumps(css)+')'
def text_button(text, scope='document'):
    return "[..."+scope+".querySelectorAll('button')].find(b=>b.innerText.trim()==="+json.dumps(text)+")"
def heads(gid):
    return J("[...document.querySelectorAll('[data-g2g="+gid+"] [role=columnheader]')].filter(e=>e.getClientRects().length).map(e=>e.innerText.replace(/[⇅▾▴▲▼]/g,'').replace(/\\s+/g,' ').trim().toLowerCase()).filter(Boolean)")
def rows(gid):
    return sorted(set(J("[...document.querySelectorAll('[data-g2g="+gid+"] [role=row][data-rid]')].filter(e=>e.getClientRects().length&&!e.dataset.rid.startsWith('grp@')).map(e=>e.dataset.rid.split('@')[0])")))
def goto(page, fresh=False, width=1440):
    c.aparelho(width,900 if width>400 else 844,1 if width>400 else 2,width<400)
    if fresh:
        c.goto(f'http://127.0.0.1:{p}/{page}.dc.html',.1)
        J('localStorage.clear();sessionStorage.clear()')
    c.goto(f'http://127.0.0.1:{p}/{page}.dc.html',.2)
def columns(gid):
    return click(query('[data-g2cvb='+gid+']'))
def toggle(gid,label):
    return click("[...document.querySelectorAll('[data-g2cv="+gid+"] label')].find(e=>e.innerText.trim()==="+json.dumps(label)+")?.querySelector('input')")
def close_columns(gid):
    click(text_button('Fechar',query('[data-g2cv='+gid+']')))
def group(gid,label):
    click(query('[data-g2agb='+gid+']'))
    return click("[...document.querySelectorAll('[data-g2agm="+gid+"] [role=menuitemradio]')].find(e=>e.innerText.trim().split('\\n')[0].trim()==="+json.dumps(label)+")")
def profile(name):
    select('select[aria-label="Trocar perfil de demonstração"]',name)
try:
    goto('CD-04',True)
    gid='g_pes'
    expected=[x.lower() for x in QUADRO[('CD-04.dc.html',gid)]]
    check('CD04 padrão renderizado',heads(gid)==expected,heads(gid))
    initial=rows(gid)
    columns(gid);toggle(gid,'Vínculo');close_columns(gid)
    custom=heads(gid)
    check('Mostrar coluna preserva registros', 'vínculo' in custom and rows(gid)==initial,custom)
    c.goto(f'http://127.0.0.1:{p}/CD-04.dc.html',.2)
    check('Escolha volta no próximo acesso',heads(gid)==custom,heads(gid))
    # Troca pela UI, sem apagar estado: detecta preferência do usuário anterior retida em memória.
    profile('Caio')
    check('Novo perfil recebe seu padrão, sem escolha alheia',heads(gid)==expected,heads(gid))
    profile('Ana')
    check('Perfil original recupera escolha',heads(gid)==custom,heads(gid))
    columns(gid);click(text_button('Restaurar padrão',query('[data-g2cv='+gid+']')));close_columns(gid)
    check('Restaurar padrão mantém registros',heads(gid)==expected and rows(gid)==initial,heads(gid))
    # Filtro pela coluna visível; ocultar depois não pode remover o recorte.
    click(query('[aria-label="Filtrar Equipe"]'))
    labels=J("[...document.querySelectorAll('[role=dialog] label')].map(e=>e.innerText)")
    inputs=J("[...document.querySelectorAll('[role=dialog] input[type=checkbox]')].length")
    if inputs:
        for i in range(inputs):
            click("[...document.querySelectorAll('[role=dialog] input[type=checkbox]')].filter((e,i)=>e.checked!==(i===0))[0]")
        click(text_button('OK'))
        subset=rows(gid)
        columns(gid);toggle(gid,'Equipe');close_columns(gid)
        chips=J("document.body.innerText")
        check('Filtro de coluna oculta preserva recorte e chip',len(subset)>0 and len(subset)<len(initial) and subset==rows(gid) and 'Equipe:' in chips,{'rows':subset,'labels':labels})
    else:
        check('Filtro de coluna oculta preserva recorte e chip',False,{'checkboxes':inputs,'labels':labels})

    goto('CD-05',True)
    gid='g_forn'
    base=rows(gid)
    spec=json.loads(re.search(r'const GRIDS = (\[.*?\]);\nconst NAV',(R/'CD-05.dc.html').read_text(),re.S).group(1))
    spec=next(g for g in spec if g['id']==gid)
    for dimension in spec.get('ag',[]):
        chosen=group(gid,dimension['l'])
        groups=J("[...document.querySelectorAll('[data-g2g=g_forn] [data-rid^=\"grp@\"]')].map(e=>({id:e.dataset.rid,text:e.innerText,n:(e.innerText.match(/(\\d+) (?:item|itens)\\b/)||[])[1]}))")
        # Conta membros distintos de cada grupo a partir do conjunto de linhas do DOM.
        counts=[int(g['n']) for g in groups if g.get('n')]
        if dimension['l']=='Papéis':
            check('Multivalor conta cada membro exatamente uma vez',sorted(counts)==[1,2,3,7,8] and sum(counts)==21 and len(base)==20,counts)
        multi=any(col.get('multi') and col['k']==dimension.get('ck',[None])[0] for col in spec['cols'])
        check('Grupos '+dimension['l']+' conservam contagem',chosen and groups and len(counts)==len(groups) and (sum(counts)>=len(base) if multi else sum(counts)==len(base)),groups)
        # AGR-02 (16/10): o grupo só recolhe; recorte é dos filtros, sem Descer/Esc/Trilha.
        # Ausência de trilha e preservação das linhas: visoes2_agrupar_test.py G1–G3;
        # varredura de todas as páginas: ds_1610_test.py S3. Não duplicar esses casos aqui.
        group(gid,'Sem agrupar')
    group(gid,'Papéis')
    c.goto(f'http://127.0.0.1:{p}/CD-05.dc.html',.2)
    check('Agrupamento volta sem depender da URL',J("document.querySelectorAll('[data-g2g=g_forn] [data-rid^=\"grp@\"]').length") == 5)
    profile('Caio')
    check('Agrupamento não atravessa perfil',J("document.querySelectorAll('[data-g2g=g_forn] [data-rid^=\"grp@\"]').length") == 0)
    profile('Ana')
    check('Perfil recupera seu agrupamento',J("document.querySelectorAll('[data-g2g=g_forn] [data-rid^=\"grp@\"]').length") == 5)
    group(gid,'Sem agrupar')
    # CD05 substitui sp.cols ao selecionar papel.
    for role in ['Clientes','Fornecedores','Todos']:
        click("[...document.querySelectorAll('button')].find(e=>e.innerText.trim().replace(/\\s+\\d+$/,'')==="+json.dumps(role)+")")
        h=heads(gid)
        expected_role=['parceiro','contato'] if role=='Fornecedores' else [x.lower() for x in QUADRO[('CD-05.dc.html',gid)]]
        check('CD05 papel '+role+' preserva marcas essenciais disponíveis',h==expected_role,h)
    goto('IR-01',True)
    select('select[aria-label="Filtrar por fazenda"]','Lagoa Grande')
    check('IR fazenda única preserva padrão',heads('g_set')==[x.lower() for x in QUADRO[('IR-01.dc.html','g_set')]],heads('g_set'))
    source=(HERE/'g2lib.js').read_text()
    prefix=source[:source.index('function g2agMenuVals(')]
    fixture=r'''
const rows=[{id:'a',v:{nome:'A',tipo:'I',qtd:2,un:'kg'}},{id:'b',v:{nome:'B',tipo:'I',qtd:3,un:'L'}}];
const sp={id:'probe',cols:[{k:'nome',l:'Item',ess:1},{k:'tipo',l:'Tipo',ess:2},{k:'qtd',l:'Quantidade'},{k:'un',l:'Unidade'}],ag:[{pq:'oque',l:'Tipo',niv:['Tipo'],ck:['tipo']}],tree:false};
const self={state:{g2:{probe:{ag:{d:'oque',t:[]},agpf:g2pfk(),f:{}}}}};
const result=g2agRows(self,sp,self.state.g2.probe,rows);
return {aggregate:result.rows[0].v.qtd??null,children:result.rows[0].kids.map(r=>[r.v.qtd,r.v.un])};
'''
    boundary=J('(function(){'+prefix+'\n'+fixture+'})()')
    check('Unidades mistas sem soma declarada não viram total numérico',boundary=={'aggregate':None,'children':[[2,'kg'],[3,'L']]},boundary)
    goto('CD-04',True,390)
    check('390 padrão usa três primeiras colunas',heads('g_pes')==expected[:3],heads('g_pes'))
    J(query('[data-g2cvb=g_pes]')+'.focus()');c.tecla('Enter','Enter',13,'\r')
    wait(query('[data-g2cv=g_pes]'))
    check('390 teclado abre seletor e foca opção',J("document.activeElement.closest('[data-g2cv=g_pes]')!==null"))
    c.tecla('Escape','Escape',27)
    check('390 Escape fecha e devolve foco',wait("document.activeElement.matches('[data-g2cvb=g_pes]')"))
    point=J("(()=>{const e=document.querySelector('[data-g2agb=g_pes]');e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()")
    c.toque(*point)
    check('390 toque abre Agrupar por dentro da janela',J("(()=>{const e=document.querySelector('[data-g2agm=g_pes]');if(!e)return false;const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight})()"))
finally:
    c.close();server.terminate();server.wait(timeout=5)
print(json.dumps(results,ensure_ascii=False,indent=2))
print(f'RESULTADO: {sum(x["ok"] for x in results)}/{len(results)}')
raise SystemExit(0 if all(x['ok'] for x in results) else 1)
