# -*- coding: utf-8 -*-
"""Verificador (rodada 4) · F: sem sinal/sinal vindo do app (outro documento), Fazenda Boa Vista/Todas em todas as etapas, Restaurar demonstração."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V
IFR = "(()=>{const f=document.createElement('iframe'); f.id='ifr'; f.style='width:10px;height:10px;position:fixed;bottom:0;right:0'; f.src=location.href; document.body.appendChild(f);})()"
def app(v, body):
    return v.J(f"(()=>{{const X=document.getElementById('ifr').contentWindow.__cen; with(X){{ const r=cenMudar(null,c=>{{{body}}}); return r.erro||r.msg; }} }})()")
v = V()
import threading
def _wd():
    print('WATCHDOG: travou', flush=True)
    try: v.c.p.kill(); v.srv.kill()
    finally: os._exit(3)
threading.Timer(75, _wd).start()
try:
    v.abrir(); v.etapa(6)
    v.J(IFR); time.sleep(1.5)
    print(app(v, "c.ordens['OS-0430'].aprov=true; cenLiberar(c,'OS-0430'); const r=c.ordens['OS-0430'].req; c.reqs[r].itens.forEach(i=>cenEntregar(c,r,i.prod,i.solicitado,'Marcos')); return cenConfirmarRecebimento(c,r);")); time.sleep(.6)
    print('k6:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
    print(app(v, "cenSinal(c,false); cenIniciarTurno(c,'OS-0430'); return cenFecharTurno(c,10,1.5);")); time.sleep(.6)
    for x in v.rows()[:3]: print('   ', x[:260])
    print('k6:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
    v.ok('Aguardando sinal' in v.rows()[0], 'consumo sem sinal aparece Aguardando sinal sem recarregar', v.rows()[0])
    v.shot('ver_est_r4_f6a.png')
    print(app(v, "return cenSinal(c,true);")); time.sleep(.6)
    for x in v.rows()[:2]: print('   ', x[:260])
    print('k6:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
    v.ok('Aguardando sinal' not in v.rows()[0], 'sinal de volta tira o Aguardando sinal', v.rows()[0])
    v.etapa(3); print('e3 REQ-47:', [x[:220] for x in v.rows() if 'REQ-47' in x])
    # Boa Vista
    sel = "select[aria-label='Filtrar por fazenda']"
    v.setv(sel, 'Boa Vista'); time.sleep(.3)
    for i in range(1, 7):
        v.etapa(i); m = v.main(); print(f'BV etapa {i}:', m[:160].replace('\n', ' '), '| prim:', repr(v.prim()), '| rows:', len(v.rows()))
    v.shot('ver_est_r4_fbv.png')
    v.clk('Ver Santa Rita'); print('volta:', v.J(f"document.querySelector(\"{sel}\").value"), v.toast(), '| rows:', len(v.rows()))
    v.setv(sel, 'Todas'); time.sleep(.3); print('Todas:', len(v.rows()), v.prim())
    v.setv(sel, 'Santa Rita'); time.sleep(.3)
    # Restaurar com filtro de local e formulário aberto
    v.etapa(4); v.clk('Galpão 1'); v.clk('Restaurar demonstração'); print('pede:', v.J("[...document.querySelectorAll('main button,main span')].filter(e=>e.offsetParent&&/Restaurar|Manter|Volta O.S./.test(e.innerText)).map(e=>e.innerText.trim())"))
    v.clk('Manter'); print('manter → movs:', v.cen("c.movs.length"))
    v.clk('Restaurar demonstração'); v.clk('Restaurar', 'main'); print('toast:', v.toast())
    print('após:', v.cen("[Object.keys(c.reqs).length, c.movs.length, c.ordens['OS-0430'].etapa, c.app.online]"), '| filtro:', v.J("(main=>[...main.querySelectorAll('button[aria-pressed=true]')].map(b=>b.innerText))(document.querySelector('main'))"), '| rows:', len(v.rows()))
    print('erros:', v.erros())
finally:
    v.fim(); os._exit(0)
