"""Composição v59 54086e8 + Codex add2a219. Adaptador/AL18 reais; dados sintéticos.
Não valida CF04 composto, candidato publicado ou dados de fazenda reais.
"""
import tempfile, shutil, time, json, os
os.environ["SAFRION_DADOS"]="sintetico"
import engine as EN
from areas import processo_safra as SAF
SAF.shell37=lambda *a,**k:None
SAF.build()
GRID=next(g for g in EN.GRIDS if g["id"]=="g_cult_S2627")
from pathlib import Path
import est_lib
from est_lib import Est
root=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='f2-previa-ui-') as td:
    destino=Path(td)/'render';shutil.copytree(root/'_render',destino)
    html=destino/'SAF.dc.html';s=html.read_text()
    marker='function planoRefPublicacaoPronta() {'
    # Fonte renderizada intacta: adaptador e AL18 reais da v59.
    est_lib.R=str(destino)
    E=Est(copiar=False)
    try:
        E.c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__errs=[];window.addEventListener('error',e=>window.__errs.push(e.message));"})
        for w,h in [(1440,1000),(390,844)]:
            E.c.size(w,h);url=f'http://127.0.0.1:{E.p}/SAF.dc.html'
            E.c.goto(url);E.J("localStorage.clear();sessionStorage.clear()");E.c.goto(url)
            E.J("window.__safSelf.__v.pick('S2627')");time.sleep(.3)
            draft=E.J("JSON.stringify(window.__safSelf.state.g2)")
            E.J("document.querySelector('#pr_abrir').click()");time.sleep(.2)
            antes=E.J("JSON.stringify({...localStorage})")
            E.clk('Conferir publicação','[role=dialog]')
            txt=E.J("document.querySelector('[role=dialog]').innerText")
            E.ok('Ana' in txt and 'cultivos sem plano ficam fora da referência' in txt and 'Não aprova orçamento' in txt,f'{w}: prévia mostra autor, aviso e consequência',txt[:300])
            E.ok(antes==E.J("JSON.stringify({...localStorage})"),f'{w}: prévia não escreve')
            E.ok(E.J("document.activeElement.id")=='pr_publicar',f'{w}: foco vai à confirmação')
            E.ok(E.J("(()=>{const r=document.querySelector('[role=dialog] h2').getBoundingClientRect();return r.top>=0&&r.bottom<innerHeight})()"),f'{w}: foco preserva cabeçalho e contexto visíveis')
            E.ok(E.J("(()=>{const b=document.querySelector('#pr_publicar').getBoundingClientRect();return b.top>=0&&b.bottom<=innerHeight&&document.documentElement.scrollWidth<=innerWidth+1})()"),f'{w}: ação alcançável e sem excesso horizontal')
            E.shot(f'f2_publicar_{w}.png')
            E.J("document.querySelector('#pr_publicar').click();document.querySelector('#pr_publicar')?.click()");time.sleep(.3)
            E.ok(E.J("JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).planoReferencias[0].versoes.length")==1,f'{w}: confirmação repetida grava só R1')
            E.ok('Registro #' in E.J("document.querySelector('[role=dialog]').innerText"),f'{w}: sucesso tem sequência persistida')
            E.clk('Voltar ao plano','[role=dialog]')
            E.ok(draft==E.J("JSON.stringify(window.__safSelf.state.g2)") and E.J('document.activeElement.id')=='pr_abrir',f'{w}: volta preserva rascunho e foco')
            E.c.goto(url);E.J("window.__safSelf.__v.pick('S2627')");time.sleep(.2);E.J("document.querySelector('#pr_abrir').click()");time.sleep(.2)
            E.ok('Comparando R1' in E.J("document.querySelector('[role=dialog]').innerText"),f'{w}: recarga recupera publicação feita pela UI')
            E.J("(()=>{const x=window.__safSelf,g=x.state.g2.g_cult_S2627||"+json.dumps(GRID)+";const rows=JSON.parse(JSON.stringify(g.rows));const w=r=>{if(r.kids)r.kids.forEach(w);else if(r.v&&r.v.area)r.v.area=99999};rows.forEach(w);x.setState({g2:{...x.state.g2,g_cult_S2627:{...g,rows}}});})()");E.clk('Conferir publicação','[role=dialog]');antes=E.J("JSON.stringify({...localStorage})")
            E.ok(E.J("document.querySelector('#pr_publicar').disabled") and 'Sobreposição em' in E.J("document.querySelector('[role=dialog]').innerText"),f'{w}: impedimento visível bloqueia confirmar')
            E.c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Escape','code':'Escape'});E.c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Escape','code':'Escape'});time.sleep(.2)
            E.ok(antes==E.J("JSON.stringify({...localStorage})") and E.J('document.activeElement.id')=='pr_abrir',f'{w}: Escape cancela prévia sem escrever e devolve foco')
            E.ok(not E.J('window.__errs.length'),f'{w}: sem erro JS',E.J('window.__errs'))
    finally: ok=E.fim()
raise SystemExit(0 if ok else 1)
