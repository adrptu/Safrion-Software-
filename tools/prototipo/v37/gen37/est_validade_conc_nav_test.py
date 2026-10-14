# -*- coding: utf-8 -*-
"""EST-1: recuperação da conciliação vencida, perfil sintético isolado."""
import time, json
from est_lib import Est
E=Est(copiar=False)
try:
    for w,h in [(1440,900),(390,844)]:
        E.c.size(w,h); E.abrir()
        E.J("localStorage.clear();sessionStorage.clear();localStorage.setItem('safrion.perfilDemo','Ana')")
        E.abrir()
        r=E.mudar("""const o=c.ordens['OS-0430'];cenLiberar(c,o.id);const r=c.reqs[o.req];
        for(const it of r.itens)cenEntregar(c,r.id,it.prod,1,'Marcos','Rui');
        cenConfirmarRecebimento(c,r.id);cenIniciarTurno(c,o.id);
        const it=r.itens[0];cenFecharTurno(c,1,1,Object.fromEntries(r.itens.map(x=>[x.prod,x===it?3:0])),'',[]);
        c.lotes[it.prod+'|'+it.lote].validade='01/2000';""")
        info=E.cen("(()=>{const r=c.reqs[c.ordens['OS-0430'].req],it=r.itens[0];return {rid:r.id,prod:it.prod,k:c.confs.find(x=>x.prod===it.prod).id}})()")
        before=E.cen("JSON.stringify({l:c.lotes,r:c.reqs,m:c.movs})")
        E.abrir()
        if w<900: E.J("document.querySelector('label[for=etp-c1].etp-atual').click()")
        print('NAV',w,E.clk('Receba devoluções'))
        E.ok(E.rowbtn([info['rid'],info['prod']],'Aceitar consumo')=='ok',f'{w}: abre prévia de aceite')
        row=E.rowtxt(info['rid'],info['prod']);print('PREVIA',w,row)
        E.ok('vencido em 01/2000' in row and 'custódia já entregue permanece preservada' in row and 'Confirmar aceite' not in row,f'{w}: motivo e recuperação, sem confirmação inválida',row)
        E.ok(E.cen("JSON.stringify({l:c.lotes,r:c.reqs,m:c.movs})")==before,f'{w}: prévia não altera físico, requisição ou movimentos')
        focused=E.J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.includes("""+json.dumps(info['rid'])+""" )&&r.innerText.includes("""+json.dumps(info['prod'])+"""));const b=r&&[...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Recusar relato');if(!b)return false;b.focus();return document.activeElement===b;})()""")
        E.c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Enter','code':'Enter','windowsVirtualKeyCode':13,'text':'\r'})
        E.c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Enter','code':'Enter','windowsVirtualKeyCode':13});time.sleep(.4)
        E.ok(focused and E.cen("c.confs.find(k=>k.id==="+json.dumps(info['k'])+").estado")=='Recusado',f'{w}: recuperação por teclado recusa relato')
        E.ok(E.cen("JSON.stringify({l:c.lotes,r:c.reqs,m:c.movs})")==before,f'{w}: recusa preserva físico, reserva e custódia')
        E.ok(not E.erros(),f'{w}: sem erro de execução',E.erros())
finally:
    ok=E.fim()
raise SystemExit(0 if ok else 1)
