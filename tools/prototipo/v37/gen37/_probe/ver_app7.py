# -*- coding: utf-8 -*-
"""Verificador App 7: OS-0424-app x REQ-039 (confirmar pelo MB-05), atualização entre quadros abertos (storage), MB-02det da OS-0430 em A liberar."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
try:
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
    # OS-0430 em A liberar no detalhe
    v.abrir('MB-02'); v.clk_sel('main a[title^="Abrir a OS-0430"]'); time.sleep(1.2)
    b = v.J("document.querySelector('main').innerText").replace('\n', ' / ')
    print('   MB-02det OS-0430:', v.hdr(), '| foot:', v.foot()); print('   ', b[:700])
    v.ok('OS-0430' in v.hdr() and v.foot() == 'Voltar às ordens' and 'Aguarda liberação no escritório' in b, 'MB-02det OS-0430 em A liberar: selo e rodapé Voltar às ordens')
    # quadros abertos ao mesmo tempo (Canvas): MB-01 com MB-05 num iframe; confirmar no iframe deve atualizar MB-01
    v.mudar("return cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos');")
    v.abrir('MB-01'); print('   antes:', v.foot())
    v.J(f"(()=>{{const f=document.createElement('iframe'); f.id='fx'; f.src='MB-05.dc.html'; f.style='position:fixed;left:600px;top:0;width:400px;height:900px'; document.body.appendChild(f);}})()")
    time.sleep(2.5)
    print('   iframe foot:', v.J("(()=>{const d=document.getElementById('fx').contentDocument; const m=d.querySelector('main'); return m.nextElementSibling.innerText.trim();})()"))
    v.J("document.getElementById('fx').contentDocument.querySelector('main').nextElementSibling.querySelector('button,a').click()"); time.sleep(1.0)
    print('   depois (sem recarregar):', v.foot(), '| cen confirmado:', v.cen("c.reqs['REQ-039'].itens[0].confirmado"))
    b = v.J("document.querySelector('main').innerText"); i = b.find('OS-0424 ·')
    print('   cartão OS-0424:', b[i:i + 250].replace('\n', ' / '))
    v.ok('com você 65 L' in b[i:i + 400] and v.foot() == 'Iniciar turno · OS-0421', 'MB-01 aberto atualiza sozinho quando outro quadro confirma (cenOuvir)')
    v.J("document.getElementById('fx').remove()")
    v.abrir('OS-0424-app'); b = v.body()
    print('   OS-0424-app:', v.J("document.querySelector('main').innerText").split('\n')[:3], '| foot:', v.foot())
    v.ok('Recebido · 65 L com Marcos · conferido com Rui' in b and v.foot() == 'Carga 1 preparada', 'OS-0424-app mostra o recebimento feito no MB-05 e segue para as cargas')
    # turno na OS-0424 consome; ficha do app mostra o que resta
    v.mudar("return cenIniciarTurno(c,'OS-0424');"); v.mudar("return cenFecharTurno(c,80,6,null,'');")
    v.abrir('OS-0424-app'); print('   após turno de 80 ha:', v.J("document.querySelector('main').innerText").split('\n')[:3])
    v.abrir('MB-01'); b = v.body(); i = b.find('OS-0424 ·'); print('   MB-01 após 80 ha na OS-0424:', b[i:i + 60].replace('\n', ' / ') if i >= 0 else 'OS-0424 fora da fila', '| foot:', v.foot())
    v.abrir('MB-02'); b = v.body(); i = b.find('OS-0424 ·'); print('   MB-02 OS-0424:', b[i:i + 330].replace('\n', ' / '))
    v.J("localStorage.setItem('talhao-os-mb-os','OS-0424')"); v.abrir('MB-02det'); b = v.J("document.querySelector('main').innerText").replace('\n', ' / ')
    print('   MB-02det OS-0424 concluída em campo:', v.hdr(), '| foot:', v.foot()); print('   ', b[:600])
    v.ok(not v.erros(), 'sem erros JS ' + str(v.erros()))
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
finally:
    v.fim()
