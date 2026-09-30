# -*- coding: utf-8 -*-
"""Verificador independente (frente os) · 2: jornada OS-0430 com Estoque (EST.dc.html) e App (MB-02.dc.html) em abas reais.
A aba da O.S. não recarrega (marcador window.__mk) e não recebe StorageEvent sintético."""
import sys, os, time, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '_probe'))
from os_lib import Os
from ver_os_tab import Tab
T = Os(copiar=False); J = T.J; OS = 'OS-0430'
def kb(): return J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > div')].map(d=>d.innerText.split('\\n').slice(0,3).join(' | '))")
def hdr(): return J("(()=>{const h=document.querySelector('header h1'); const s=h&&h.nextElementSibling; return s?s.innerText.trim():'';})()")
def chips(): return J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())")
try:
    T.abrir(wait=1.3); J("window.__mk=1")
    est = Tab(T.c, f'http://127.0.0.1:{T.p}/EST.dc.html'); app = Tab(T.c, f'http://127.0.0.1:{T.p}/MB-02.dc.html')
    print('abas extras ok', est.js("!!window.__cen"), app.js("!!window.__cen"))
    T.ordem(OS); T.btn('Revisar versão'); T.btn('Aprovar versão'); print('1 toast', T.toast())
    T.btn('Liberar para execução'); T.btn('Confirmar liberação'); print('2 toast', T.toast())
    RQ = T.cen(f"c.ordens['{OS}'].req"); print('   REQ', RQ, '| linha', T.linha(OS))
    # Estoque (outra aba) entrega
    for prod, q in (('Glifosato 480', 320), ('2,4-D 806', 160), ('Óleo mineral', 80)):
        print('   EST', est.mudar(f"return cenEntregar(c,'{RQ}','{prod}',{q},'Marcos');"))
    time.sleep(.6)
    print('3 ins OS (sem recarregar)', T.ins()[:420], '| mk', J("window.__mk"))
    # App (outra aba): confirma, turno sem sinal
    print('   APP', app.mudar(f"cenConfirmarRecebimento(c,'{RQ}'); cenIniciarTurno(c,'{OS}'); cenSinal(c,false); return cenFecharTurno(c,60,5);")); time.sleep(.6)
    print('4 linha', T.linha(OS)); print('   aps', T.aps()); print('   pan acum', [x for x in T.pan().split('Acumulado')[1:2]])
    print('   hdr', hdr(), '| chips', chips())
    print('   APP', app.mudar("return cenSinal(c,true);")); time.sleep(.6)
    print('5 linha', T.linha(OS), '| aps', T.aps())
    print('   APP', app.mudar(f"cenIniciarTurno(c,'{OS}'); return cenFecharTurno(c,100,8,{{'Glifosato 480':180}});")); time.sleep(.6)
    print('6 linha', T.linha(OS), '| btn Enviar?', T.temb('Enviar para conferência'))
    T.btn('Enviar para conferência'); T.btn('Confirmar envio'); p = T.pan()
    print('7 passo', p[p.find('PRÓXIMO'):][:330], '| link', T.link('Receber devolução no Estoque'))
    print('   selos linha', T.linha(OS))
    print('   EST', est.mudar(f"return cenDevolver(c,'{RQ}','Glifosato 480',20,true);")); time.sleep(.6)
    p = T.pan(); print('8 passo', p[p.find('PRÓXIMO'):][:260], '| btn', T.temb('Conferir e encerrar'), '| linha', T.linha(OS))
    T.btn('Conferir e encerrar'); T.btn('Confirmar encerramento'); print('9 toast', T.toast(), '| linha', T.linha(OS))
    T.fechar()
    J("(()=>{const b=[...document.querySelectorAll('button,[role=tab]')].find(b=>b.innerText.trim()==='Kanban'); b&&b.click();})()"); time.sleep(.4)
    print('10 kanban', kb(), '| hdr', hdr(), '| chips', chips())
    T.shot('ver_os2_kanban_fim.png')
    # a outra aba do Estoque vê a OS-0430 encerrada? (conferência de coerência)
    print('11 cen EST', est.js("(()=>{const c=window.__cen.cenGet(); return [c.ordens['OS-0430'].etapa, JSON.stringify(c.reqs['" + RQ + "'].itens.map(i=>[i.prod,i.custodia,i.devolvido]))];})()"))
    print('   mk', J("window.__mk"), '| erros', T.erros())
finally:
    T.fim()
