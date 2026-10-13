"""Consulta F2 no SAF real a1440/390. Histórico injetado só para testar apresentação.
Não prova publicação, idempotência, reload de versões ou teclado virtual.
Depois de gerar SAF.dc.html e montar_render.py: python3 plano_referencia_nav.py.
"""
import json
import time
from pathlib import Path
from est_lib import Est, CLK, SETV

E=Est(copiar=False)
try:
    for w,h in [(1440,1000),(390,844)]:
        E.c.size(w,h)
        E.c.goto(f'http://127.0.0.1:{E.p}/SAF.dc.html')
        E.J("localStorage.clear(); sessionStorage.clear()")
        E.c.goto(f'http://127.0.0.1:{E.p}/SAF.dc.html')
        E.ok(not E.J("!!document.querySelector('#pr_abrir')"),f'{w}: listagem não mostra consulta de safra não escolhida')
        # Preparação do contexto pela mesma ação da linha; a consulta seguinte usa botão real.
        E.J("window.__safSelf.__v.pick('S2627')")
        time.sleep(.25)
        antes=E.J("JSON.stringify({g2:window.__safSelf.state.g2,saf:window.__safSelf.state.saf,step:window.__safSelf.state.step,ls:{...localStorage}})")
        E.J("document.querySelector('#pr_abrir').click()")
        time.sleep(.3)
        texto=E.J("document.querySelector('[role=dialog]').innerText")
        E.ok('Sem referência registrada' in texto and 'ainda não publicado' in texto and 'Santa Rita' in texto,f'{w}: legado sem aprovação fictícia e contexto visível')
        E.ok(E.J("document.activeElement.id")=='pr_x',f'{w}: foco entra no painel')
        E.J(f"({SETV})('#pr_busca','Área')")
        time.sleep(.25)
        E.ok(E.J("document.querySelector('#pr_busca').value")=='Área' and E.J("document.querySelectorAll('[role=dialog] li').length")>0,f'{w}: busca filtra conteúdo')
        E.ok(E.J("document.documentElement.scrollWidth<=innerWidth+1"),f'{w}: sem rolagem horizontal')
        E.shot(f'f2_{w}_consulta.png')
        E.J("document.querySelector('#pr_x').focus()")
        E.c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Tab','code':'Tab','modifiers':8})
        E.c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Tab','code':'Tab','modifiers':8})
        E.ok(E.J("document.activeElement.innerText")=='Voltar ao plano',f'{w}: Shift+Tab contém foco no painel')
        E.c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Escape','code':'Escape'})
        E.c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Escape','code':'Escape'})
        time.sleep(.25)
        depois=E.J("JSON.stringify({g2:window.__safSelf.state.g2,saf:window.__safSelf.state.saf,step:window.__safSelf.state.step,ls:{...localStorage}})")
        E.ok(E.J("document.activeElement.id")=='pr_abrir' and not E.J("!!document.querySelector('[role=dialog]')"),f'{w}: Escape fecha e devolve foco')
        E.ok(antes==depois,f'{w}: consulta preserva rascunho, contexto e armazenamento')
        # Fixture explícita: retrato anterior com área diferente; não grava nem simula publicação.
        E.J("""(()=>{const r=JSON.parse(JSON.stringify(window.__planoRef.projetar()));
          r.entidades.find(e=>e.tipo==='cultivo').campos.area.valor-=1;
          window.__planoRef.abrir([{id:'R-teste',em:'13/10/2026',por:'Perfil sintético',retrato:r}]);})()""")
        time.sleep(.25)
        texto=E.J("document.querySelector('[role=dialog]').innerText")
        E.ok('Comparando R-teste' in texto and 'alterado' in texto and 'Área' in texto and E.J("document.querySelectorAll('[role=dialog] li').length")==1,f'{w}: fixture histórica compara só a área alterada')
        E.J(f"({CLK})('Consultar conteúdo completo','[role=dialog]')")
        time.sleep(.25)
        E.ok(E.J("document.querySelectorAll('[role=dialog] li').length")>1,f'{w}: consulta conteúdo completo sem substituir o plano')
        E.J(f"({CLK})('Consultar versão selecionada','[role=dialog]')")
        time.sleep(.2)
        E.ok('Consultando R-teste' in E.J("document.querySelector('[role=dialog]').innerText"),f'{w}: conteúdo histórico consultável sem restaurar versão')
        E.J(f"({CLK})('Voltar ao plano','[role=dialog]')")
        time.sleep(.25)
        E.ok(E.J("document.activeElement.id")=='pr_abrir',f'{w}: primária volta ao contexto')
    E.ok(not E.erros(),'sem erro de script na tela',E.erros())
finally:
    ok=E.fim()
raise SystemExit(0 if ok else 1)
