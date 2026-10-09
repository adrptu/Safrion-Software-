# -*- coding: utf-8 -*-
"""Regressão (Comercial, 09/10): dois cliques seguidos em "Reservar" (Estoque de produto, formulário prFormReserva) não podem gravar duas
reservas nem trocar a mensagem de sucesso por um erro. Defeito da base f4121bd: o 2º clique lia a chave do estado já limpo pelo 1º
sucesso (pr_ch null), nascia com chave nova, era recusado com "Acima da falta do PV-036: 0 kg" e o erro apagava a confirmação.
Correção: quantidade e chave lidas no desenho do formulário; o 2º clique repete a mesma chave e o mesmo conteúdo e volta "já registrada".
Roda também na base (falha lá: é o defeito reproduzido). Dados sintéticos (SAFRION_DADOS=sintetico; a Lagoa Grande é sintética).
Uso: env CHROME_BIN=… flock /tmp/cdpC.lock env CDP_GL=1 timeout 900 python3 reserva_duplo_clique_test.py"""
import sys, os, time, json
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cadc_lib import T
t = T(); J = t.J
LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.CLK=(t,root)=>{ const r=root?document.querySelector(root):document; const els=[...r.querySelectorAll('button,a')].filter(VIS);
  const e=els.find(x=>N(x.innerText)===t)||els.find(x=>N(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok'; };
window.CLK2=(t,root)=>{ const r=root?document.querySelector(root):document; const e=[...r.querySelectorAll('button,a')].filter(VIS).find(x=>N(x.innerText)===t); if(!e) return 'NÃO ACHEI: '+t; e.click(); e.click(); return 'ok'; };
window.ROW=(t)=>{ const r=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>N(x.innerText).indexOf(t)>=0); if(!r) return 'sem linha '+t; (r.querySelector('.g2pw')||r).click(); return 'ok'; };
window.PAN=()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); return a?N(a.innerText):''; };
window.TOAST=()=>[...document.querySelectorAll('[role=status]')].map(x=>N(x.innerText)).filter(Boolean).join(' | ');
window.CEN=()=>JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null')||((window.__car&&window.__car.cenGet)?window.__car.cenGet():null);
'ok'"""
try:
    t.c.size(1440, 1000)
    t.c.goto(f'http://127.0.0.1:{t.p}/Main.dc.html', wait=.4); J("localStorage.clear(); sessionStorage.clear()")
    t.goto('PROD.dc.html'); time.sleep(.5); J(LIB)
    # colheita da semente (CG-2108 → L39-133, 12.050 kg Liberado) pelo mesmo motor da página
    r = J("(()=>{ const {prReceber}=window.__pr; const x=window.__car.cenMudar(null,c=>prReceber(c,{carga:'CG-2108',ticket:'TK-4520',bruto:19250,tara:7200,cond:'Íntegra',chave:'T-REC'})); return x.erro||'ok'; })()")
    t.goto('PROD.dc.html'); time.sleep(.5); J(LIB)
    a = J("ROW('L39-133')"); time.sleep(.45)
    b = 'ok' if J("!![...document.querySelectorAll('aside[role=dialog] input')].find(i=>i.id.indexOf('pf_q_L39-133_PV-036')===0)") else J("CLK('Reservar L39-133 para pedido','aside[role=dialog]')"); time.sleep(.45)   # o formulário pode abrir já no clique da linha
    c = J("CLK2('Reservar','aside[role=dialog]')"); time.sleep(.9)
    n = J("(()=>{ const c=CEN(); return Object.values(c.producao.reservas).filter(r=>r.pedido==='PV-036'&&r.st==='Ativa').length; })()")
    p = J("PAN()") or ''; m = J("TOAST()") or ''
    t.chk('dois cliques seguidos em "Reservar" (L39-133 → PV-036): uma reserva só, nenhum erro no painel e a confirmação continua à vista',
          r == 'ok' and a == 'ok' and b == 'ok' and c == 'ok' and n == 1 and 'Acima da falta' not in p and 'conflito' not in p and 'RS-0002' in m, [r, a, b, c, n, m, [x for x in ('Acima da falta', 'conflito') if x in p]])
    t.chk('nenhuma página com erro de JS', not t.errs(), t.errs())
finally:
    t.fim()
sys.exit(0 if all(t.ok) else 1)
