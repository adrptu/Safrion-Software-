# -*- coding: utf-8 -*-
"""D5 · peça comprada para a manutenção fica reservada para a ordem que pediu (decisão do proprietário, 16/10/2026;
docs/integracao/V69/decisoes-proprietario-1610.md). Dano evitado: máquina parada esperando uma peça que foi usada noutro lugar.
No navegador (CDP), como a pessoa faz, com o estado lido do cenário único. Dados sintéticos.
 1 · Recebimento parcial da SC-041 (OM-0235, filtro 3 un): Rui recebe 2 un (duplo toque) → 2 un reservadas para a OM-0235, o livre não
     cresce, um recebimento só; Compras mostra "Reservado para OM-0235" e a origem PC-202 › PC-202/1.
 2 · A mesma chave de novo não reserva de novo; o resto (1 un) completa a reserva e a SC fica Recebida.
 3 · Na OM-0235: "Peça chegou · reservada", com a origem (pedido › recebimento › reserva › ordem), e a primária "Liberar serviço".
 4 · Outra ordem (OM-0236 com o mesmo filtro) não usa a reserva: "Falta" com o motivo e a liberação recusada; nada muda.
 5 · Cancelar a OM-0235 devolve a reserva ao livre, com registro na ordem e em Compras; a OM-0236 deixa de ter falta.
 6 · Reposição (Graxa EP2, sem ordem) continua indo ao estoque livre.
Uso (de gen37/): env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico python3 -B d5_reserva_test.py
Contraprova: D5_RENDER=<pasta do _render da base> serve outra montagem (na base df7de98 a peça entra no livre: 1b reprova com livre 3)."""
import os, sys, time, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ma_lib import MA

m = MA(1440, 1000); J = m.J
REND = os.environ.get('D5_RENDER')
if REND:
    m.t.srv.terminate(); m.t.srv.wait(5); time.sleep(.3)
    m.t.srv = subprocess.Popen(['python3', '-m', 'http.server', str(m.t.p), '--bind', '127.0.0.1', '--directory', REND], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(.6)
PAN = '#cm-painel'; F = 'FIL-MF4292'
def cpan(): return J("(document.querySelector('#cm-painel')||{}).innerText||''") or ''
def cmp(ancora, perfil): m.ir(ancora, perfil=perfil, pagina='CMP.dc.html')
def mut(js): return m.J(f"window.__man.manMudar(null,(m)=>{{ {js}; return {{msg:''}}; }})")
def fil(): return m.man(f"(()=>{{const it=m.itens['{F}']; const o=m.oms['OM-0235']; const p=o.pecas.find(x=>x.item==='{F}'); const r=(m.cmp||{{reqs:{{}}}}).reqs['SC-041']||{{}};"
                        f" return {{saldo:it.saldo,res:it.reservado,livre:it.saldo-it.reservado,om:p.res||0,recs:(r.recs||[]).length,etapa:r.etapa||''}};}})()") or {}
def prim(): return J("(()=>{const b=document.querySelector('#cm-painel [data-cm-prim]'); return b&&b.getClientRects().length?{t:b.innerText.trim(),dis:b.getAttribute('aria-disabled')==='true'}:null;})()")
def secao(nome, fn):
    try: fn()
    except Exception as e: m.ok(False, nome + ' · exceção', str(e)[:200])

def espera(js, limite=15):   # condição observável, com limite explícito (AGENTS §3.6)
    for _ in range(int(limite / .2)):
        try:
            if J(js): return True
        except Exception: pass
        time.sleep(.2)
    return False

def preparo():   # OM-0235 precisa de 3 filtros (fixture sintética), Solicitar compra, cotação e PC-202
    m.ir('vis=semordem', perfil='Otávio', limpa=True)
    m.ok(espera("[...document.querySelectorAll('button')].some(b=>/^Gerar 3 ordens preventivas/.test(b.innerText.trim())&&!b.disabled)"), '0 · "Gerar 3 ordens preventivas" à vista (limite 15 s)')
    m.clk('Gerar 3 ordens preventivas'); espera("!!window.__man.manGet().oms['OM-0235']", 5)
    mut(f"m.oms['OM-0235'].pecas.find(p=>p.item==='{F}').qtd=3")
    m.ir('om=OM-0235', perfil='Otávio'); m.clk('Solicitar compra', '#ma-painel')
    cmp('tipo=materiais&sc=SC-041', 'Ana'); m.clk('Solicitar cotações (simulado)', PAN); m.clk('Emitir pedido', PAN)
    m.ok(m.man("m.cmp.reqs['SC-041'].ped.id") == 'PC-202' and m.man("m.cmp.reqs['SC-041'].itens[0].qtd") == 3,
         '0 · preparo: OM-0235 pede 3 filtros pela SC-041; Ana emite o PC-202', m.man("m.cmp.reqs['SC-041']"))

def parte1():
    f0 = fil(); cmp('tipo=materiais&sc=SC-041', 'Rui')
    m.setv('#cm-painel input[data-cmrec="0"]', '2'); p = prim()
    J("(()=>{const b=document.querySelector('#cm-painel [data-cm-prim]'); b.click(); b.click();})()"); time.sleep(.6)
    t = m.toast(); f1 = fil(); pn = cpan()
    m.ok(p and p['t'] == 'Registrar recebimento · 2 un' and f1['saldo'] == f0['saldo'] + 2 and f1['res'] == f0['res'] + 2 and f1['om'] == 2 and f1['recs'] == 1,
         '1a recebimento parcial com duplo toque: entra 2 un, as 2 ficam reservadas para a OM-0235, um recebimento só', [p, f0, f1])
    m.ok(f1['livre'] == f0['livre'], '1b o livre não cresce com a peça da OM (antes ' + str(f0.get('livre')) + ' un, depois ' + str(f1.get('livre')) + ' un)', [f0, f1])
    m.ok('Reservado para OM-0235' in t and 'Reservado para OM-0235' in pn and 'Recebido em parte' in pn and 'PC-202/1' in pn and 'PC-202 ·' in pn,
         '1c Compras mostra "Reservado para OM-0235", "Recebido em parte" e a origem PC-202 › recebimento PC-202/1', [t[:200], pn[:700]])
    m.ir('om=OM-0235', perfil='Otávio'); m.bloco('Peças'); po = m.pan()
    m.ok('Peça chegou · reservada' in po and 'Reservada 2 de 3 un · falta 1 un (SC-041)' in po and 'Liberar serviço' not in m.prims(),
         '1d na OM-0235 o parcial aparece: "Peça chegou · reservada", "Reservada 2 de 3 un · falta 1 un (SC-041)"; ainda não libera', [po[-700:], m.prims()])

def parte2():
    f1 = fil(); rk = lambda: m.J("window.__man.manMudar(null,(m)=>window.__cmm.cmmReceber(m,'SC-041','Rui',['1'],'d5-chave-1'))") or {}
    a = rk(); f2 = fil(); b = rk(); f3 = fil()
    m.ok(not a.get('erro') and b.get('repetido') and f2['om'] == 3 and f2['res'] == f1['res'] + 1 and f3 == f2 and f3['etapa'] == 'Recebida' and f3['recs'] == 2,
         '2 · a mesma chave de novo não soma nem reserva de novo; o resto (1 un) completa a reserva e a SC-041 fica Recebida', [a, b, f1, f2, f3])

def parte3():
    m.ir('om=OM-0235', perfil='Otávio'); m.bloco('Peças'); po = m.pan()
    m.ok('Peça chegou · reservada' in po and 'Reservada' not in po and 'PC-202 › recebimento PC-202/1' in po and '› OM-0235' in po and 'Falta peça' not in po and 'Liberar serviço' in m.prims(),
         '3 · na OM-0235: "Peça chegou · reservada" (as 3 un), a origem (pedido › recebimento › reserva › ordem) e a primária "Liberar serviço"', [po[:600], m.prims()])

def parte4():
    mut(f"m.oms['OM-0236'].pecas.push({{item:'{F}',nome:'Filtro de óleo MF 4292',un:'un',qtd:1,res:0,apl:0,sob:0,preco:160}})")   # outra ordem pede o mesmo filtro
    f0 = fil(); m.ir('om=OM-0236', perfil='Otávio'); m.bloco('Peças'); po = m.pan()
    lb = m.J("window.__man.manMudar(null,(m)=>window.__man.manLiberar(m,'OM-0236',true,'Otávio',{executante:'Zé',tempo:'2'}))") or {}
    m.ok('Falta 1 un' in po and '3 un reservadas para a OM-0235' in po and 'Liberar serviço' not in m.prims() and 'reservadas para a OM-0235' in (lb.get('erro') or '')
         and fil() == f0 and m.man("m.oms['OM-0236'].etapa") == 'A liberar',
         '4 · outra ordem (OM-0236) não usa a reserva: "Falta 1 un · 3 un reservadas para a OM-0235" e a liberação é recusada com o motivo; nada muda', [po[:500], lb, fil()])

def parte5():
    f0 = fil(); m.ir('om=OM-0235', perfil='Otávio'); m.clk('Cancelar ordem · motivo', '#ma-painel'); m.setv('#ma-av-in', 'trator vendido')
    m.clk('Cancelar a OM-0235', '#ma-painel'); t = m.toast() + ' ' + m.pan(); f1 = fil(); cc = m.man("m.oms['OM-0235'].canc") or {}
    m.ok(m.man("m.oms['OM-0235'].etapa") == 'Canceladas' and f1['res'] == f0['res'] - 3 and f1['livre'] == f0['livre'] + 3 and f1['om'] == 0
         and cc.get('motivo') == 'trator vendido' and (cc.get('dev') or [{}])[0].get('qtd') == 3 and 'PC-202/1' in (cc.get('dev') or [{}])[0].get('orig', '') and 'reserva devolvida ao estoque livre' in t,
         '5a cancelar a OM-0235 (motivo) devolve as 3 un ao livre, com registro na ordem (quem, quando, motivo, origem do recebimento)', [t[:300], f0, f1, cc])
    m.bloco('Peças'); po = m.pan(); m.ir('om=OM-0236', perfil='Otávio'); m.bloco('Peças'); p36 = m.pan()
    cmp('tipo=materiais&sc=SC-041', 'Ana'); pn = cpan()
    f36 = m.man("window.__man.manFalta(m,m.oms['OM-0236']).length")
    m.ok('Reserva de 3 un devolvida ao livre' in po and 'trator vendido' in po and f36 == 0 and 'Livre 3 un' in p36 and 'devolvido ao livre' in pn and 'OM-0235 cancelada' in pn,
         '5b a OM-0235 mostra "Reserva de 3 un devolvida ao livre" com o motivo; a OM-0236 sai de Falta; Compras registra "devolvido ao livre (OM-0235 cancelada)"', [po[-300:], f36, p36[:300], pn[-500:]])

def parte6():
    cmp('tipo=materiais', 'Rui'); m.abre('REP:GR-EP2'); m.clk('Abrir requisição de reposição', PAN)
    rid = m.man("Object.keys(m.cmp.reqs).find(k=>m.cmp.reqs[k].orig==='rep'&&m.cmp.reqs[k].itens[0].item==='GR-EP2')")
    cmp('tipo=materiais&sc=' + str(rid), 'Ana'); m.clk('Solicitar cotações (simulado)', PAN); m.clk('Emitir pedido', PAN)
    g0 = m.man("[m.itens['GR-EP2'].saldo,m.itens['GR-EP2'].reservado]"); cmp('tipo=materiais&sc=' + str(rid), 'Rui')
    m.clk('Tudo', PAN); m.clk('Registrar recebimento', PAN); t = m.toast(); g1 = m.man("[m.itens['GR-EP2'].saldo,m.itens['GR-EP2'].reservado]")
    m.ok(g1 == [g0[0] + 22, g0[1]] and 'estoque da oficina' in t and 'Reservado' not in t,
         '6 · reposição sem ordem: a Graxa EP2 recebida (22 kg) entra no estoque livre, sem reserva', [rid, g0, g1, t[:200]])
    m.sem_erro('D5 · fim')

try:
    secao('0 · preparo', preparo)
    secao('1 · recebimento parcial reserva só o que chegou', parte1)
    secao('2 · mesma chave não reserva de novo', parte2)
    secao('3 · peça chegou reservada na OM', parte3)
    secao('4 · outra ordem não usa a reserva', parte4)
    secao('5 · cancelar devolve ao livre', parte5)
    secao('6 · reposição no livre', parte6)
finally:
    sys.exit(m.fim())
