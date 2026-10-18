"""OS-LOTE-F1 A2/A8: navegador real, dados sintéticos e perfil Chrome descartável.
Proposto para execução por Claude; não confundir teste salvo com teste executado.
RENDER_DIR deve apontar para o render da candidata (não para uma publicação anterior).
"""
import json, os, sys, time
from pathlib import Path
from comp_lib import Chrome, servir

if os.environ.get('CDP_PORT'):
    raise SystemExit('Use perfil descartável próprio; não anexar esta prova a uma sessão existente.')
R=os.environ.get('RENDER_DIR')
if not R or not (Path(R)/'OS.dc.html').is_file():
    raise SystemExit('RENDER_DIR da candidata é obrigatório, com OS.dc.html renderizado.')
saida=Path(os.environ.get('OS_LOTE_EVIDENCIA','_shots/os-lote'));saida.mkdir(parents=True,exist_ok=True)
result=[]

def verificar(nome,valor):
    result.append(dict(nome=nome,ok=bool(valor)))
    print(('OK ' if valor else 'FALHA ')+nome,flush=True)

def aguardar(c,expr,seg=6):
    fim=time.monotonic()+seg
    while time.monotonic()<fim:
        if c.js(expr):return True
        time.sleep(.1)
    return False

porta,srv=servir(R);c=None
try:
    for largura in (1440,390):
        c=Chrome();c.aparelho(largura,900 if largura==1440 else 844,1,largura==390)
        url=f'http://127.0.0.1:{porta}/OS.dc.html'
        c.goto(url);c.js("localStorage.setItem('safrion.perfilDemo','Caio')");c.goto(url)
        def click(texto,dialogo=False):
            esc='aside[aria-label="Agrupamento de operações"] ' if dialogo else ''
            return c.js("(()=>{const b=[...document.querySelectorAll(%s)].find(x=>x.offsetParent&&x.innerText.trim()===%s&&!x.disabled);if(!b)return false;b.click();return true})()"%(json.dumps(esc+'button'),json.dumps(texto)))
        def campo(seletor,valor):
            return c.js("(()=>{const e=document.querySelector(%s);if(!e)return false;const p=e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(p,'value').set.call(e,%s);e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));return true})()"%(json.dumps(seletor),json.dumps(valor)))
        dialog='document.querySelector(\'aside[aria-label="Agrupamento de operações"]\')'
        prefix=f'{largura}px · '
        verificar(prefix+'contexto Santa Rita disponível',campo('select[aria-label="Filtrar por fazenda"]','Santa Rita'))
        verificar(prefix+'O.S. comuns da seed aparecem',aguardar(c,"document.body.innerText.includes('OS-0595')&&document.body.innerText.includes('OS-0598')"))
        # EX-54 (patch do integrador, Claude): a entrada é a visão Frentes; "Agrupar N O.S. desta calda" abre esta conferência com a seleção explícita
        c.js("(()=>{const b=document.querySelector('[data-visao=frentes]')||document.querySelector('[data-visao-menu=frentes]');if(b)b.click()})()");time.sleep(.6)
        if not c.js("!!document.querySelector('[data-os-frentes]')&&document.querySelector('[data-os-frentes]').offsetParent!==null"):
            c.goto(url+'?view=frentes',1.6);campo('select[aria-label="Filtrar por fazenda"]','Santa Rita');time.sleep(.8)
        c.js("(()=>{const b=[...document.querySelectorAll('[data-os-frentes] .fr-card')].find(x=>x.innerText.includes('Glifosato'));if(b)b.click()})()");time.sleep(.5)
        verificar(prefix+'P1 sem vazão fica na frente com o motivo',c.js("(()=>{const t=document.querySelector('[data-os-frentes]').innerText;return t.includes('OS-0597')&&t.includes('Definir vazão')})()"))
        abre="(()=>{const b=[...document.querySelectorAll('[data-os-frentes] .fr-acoes button')].find(x=>x.innerText.startsWith('Agrupar 2 O.S. desta calda'));if(b)b.focus();return !!b})()"
        c.js(abre);c.tecla('Enter','Enter',13,text='\r')
        verificar(prefix+'abre por teclado',aguardar(c,'!!'+dialog))
        verificar(prefix+'abre só com as O.S. da calda escolhida',c.js(f"{dialog}.innerText.includes('2 selecionadas')&&{dialog}.innerText.includes('OS-0595')&&{dialog}.innerText.includes('OS-0596')&&!{dialog}.innerText.includes('OS-0597')"))
        verificar(prefix+'insumos e datas visíveis antes de conferir',aguardar(c,f"{dialog}.innerText.includes('total 304 L')&&{dialog}.innerText.includes('30/09/2026')"))
        verificar(prefix+'escolhe calda proposta',c.js(f"{dialog}.innerText.includes('Conferir agrupamento')"))
        dica0=c.js("(()=>{const d=document.getElementById('g2-dica');return !!(d&&!d.hidden)})()")
        c.tecla('Escape',vk=27)
        if dica0: c.tecla('Escape',vk=27)   # WCAG 1.4.13: com a dica do × aberta, o 1º Esc fecha só a dica
        verificar(prefix+'Escape fecha sem perder a tela',aguardar(c,f"!{dialog}&&!!document.querySelector('[data-os-frentes]')"))
        c.js(abre);c.tecla('Enter','Enter',13,text='\r');aguardar(c,'!!'+dialog)
        verificar(prefix+'reabrir conserva seleção das duas O.S.',c.js(f"{dialog}.innerText.includes('OS-0595')&&{dialog}.innerText.includes('OS-0596')&&{dialog}.innerText.includes('2 selecionadas')"))
        click('Conferir agrupamento',True)
        verificar(prefix+'prévia 248 ha e 496 L de glifosato preserva alocação',aguardar(c,f"{dialog}.innerText.includes('248 ha')&&{dialog}.innerText.includes('496 L')&&{dialog}.innerText.includes('Recursos da alocação')"))
        verificar(prefix+'uma primária alcançável sem cobrir conteúdo',c.js(f"(()=>{{const b=[...{dialog}.querySelectorAll('button')].find(x=>x.innerText==='Confirmar agrupamento'),r=b&&b.getBoundingClientRect();return r&&r.height>=44&&r.left>=0&&r.right<=innerWidth&&r.bottom<=innerHeight&&b.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))}})()"))
        for _ in range(8):c.tab()
        verificar(prefix+'Tab permanece no diálogo',c.js(f"{dialog}.contains(document.activeElement)"))
        verificar(prefix+'sem overflow horizontal',c.js('document.documentElement.scrollWidth<=innerWidth+1'))
        c.shot(str(saida/f'previa-{largura}.png'))
        click('Confirmar agrupamento',True)
        verificar(prefix+'recibo das duas O.S.',aguardar(c,f"{dialog}.innerText.includes('GRP-1 confirmado')&&{dialog}.innerText.includes('OS-0596 · Vinculada')"))
        verificar(prefix+'confirmação não aprova nem libera nem reserva',c.js("(()=>{const c=window.__cen.cenGet();return ['OS-0595','OS-0596'].every(id=>c.ordens[id].etapa==='A liberar'&&!c.ordens[id].reservado&&!(c.ordens[id].osc.ev||[]).length)&&Object.keys(c.gruposExec).length===1})()"))
        # WCAG 1.4.13 (g2lib, dica explícita): se o foco está num controle com dica aberta, o 1º Esc fecha só a dica e o 2º fecha o modal
        dica=c.js("(()=>{const d=document.getElementById('g2-dica');return !!(d&&!d.hidden)})()")
        c.tecla('Escape',vk=27)
        # verificação sempre registrada (total fixo): com dica aberta, o 1º Esc a esconde e mantém o modal; sem dica, nada a conferir aqui
        verificar(prefix+'Esc respeita a dica (1º fecha só a dica e mantém o modal)',(not dica) or c.js(f"(()=>{{const d=document.getElementById('g2-dica');return !!{dialog}&&(!d||d.hidden)}})()"))
        if dica: c.tecla('Escape',vk=27)
        verificar(prefix+'grupo persistido reabre sem perder vínculo',aguardar(c,f"!{dialog}") and c.js("(()=>{const b=[...document.querySelectorAll('button')].find(x=>x.offsetParent&&x.innerText.startsWith('GRP-1 ·'));if(!b)return false;b.click();return true})()") and aguardar(c,f"{dialog}&&{dialog}.innerText.includes('OS-0596')"))
        c.shot(str(saida/f'recibo-{largura}.png'))
        # EX-32 v2 (proprietário, 18/10): a agrônoma aprova em lote, com prévia; um CMD-42 por O.S.; aprovar não libera
        c.js("localStorage.setItem('safrion.perfilDemo','Ana')");c.goto(url+'?view=frentes',1.6);campo('select[aria-label="Filtrar por fazenda"]','Santa Rita');time.sleep(.8)
        reab=c.js("(()=>{const b=[...document.querySelectorAll('button')].find(x=>x.offsetParent&&x.innerText.startsWith('GRP-1 ·'));if(!b)return false;b.click();return true})()") and aguardar(c,'!!'+dialog)
        verificar(prefix+'EX-32 agrônoma vê "Conferir aprovação das 2 pendentes" como próximo passo',reab and aguardar(c,f"{dialog}.innerText.includes('Conferir aprovação das 2 pendentes')"))
        click('Conferir aprovação das 2 pendentes',True)
        verificar(prefix+'EX-32 prévia diz um registro por O.S. e que aprovar não libera',aguardar(c,f"{dialog}.innerText.includes('Cada O.S. recebe o próprio registro (CMD-42)')&&{dialog}.innerText.includes('Aprovar não libera')&&{dialog}.innerText.includes('Aprovar as 2')"))
        click('Aprovar as 2',True)
        verificar(prefix+'EX-32 recibo por O.S.: as duas aprovadas, aguardando liberação',aguardar(c,f"{dialog}.innerText.includes('OS-0595 · Aprovada · aguarda liberação')&&{dialog}.innerText.includes('OS-0596 · Aprovada · aguarda liberação')"))
        verificar(prefix+'EX-32 um CMD-42 por O.S., nenhum CMD-06, nada reservado, seguem em A liberar',c.js("(()=>{const c=window.__cen.cenGet();return ['OS-0595','OS-0596'].every(id=>{const o=c.ordens[id],ev=(o.osc||{}).ev||[];return o.etapa==='A liberar'&&!o.reservado&&ev.filter(e=>e.cmd==='CMD-42').length===1&&!ev.some(e=>e.cmd==='CMD-06')})})()"))
        c.js("localStorage.setItem('safrion.perfilDemo','Caio')")
        verificar(prefix+'sem exceções JavaScript',not c.js('(window.__errs||[]).length'))
        c.close();c=None
finally:
    if c:c.close()
    srv.terminate()
    (saida/'resultado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(f'RESULTADO {sum(r["ok"] for r in result)}/{len(result)}')
sys.exit(0 if len(result)==44 and all(r['ok'] for r in result) else 1)   # 36 + 4 do EX-32 v2 em cada largura
