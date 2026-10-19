# -*- coding: utf-8 -*-
"""COLH-C01 · parte de navegador do cafe_apurar_test.py (Chrome real, mesmo cenário em localStorage; dados sintéticos).
Normal: a carga de café de 12.000 L é pesada pela tela Cargas e recebimento (O.S. de colheita de café do C1 com 5 ha apontados) e
Previsão e colheita mostra "12.000 L · sc a apurar" na linha, no total da cultura, no cartão (390 px) e no painel; Estoque de produto
mostra o lote em L. Erro/recusa: pesagem de café sem litros é recusada junto ao campo, nada gravado. Repetição: o mesmo ticket com o
mesmo conteúdo não soma de novo. Transição: o rendimento medido (gravado como o BEN-4 gravará) troca "a apurar" por sacas.
Capturas em _probe/cafe_apurar_*.png. Uso: python3 cafe_apurar_test.py nav   (compile antes: build.py && montar_render.py)"""
import os, re, time, json
from cadc_lib import T

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.CLK=(t,root)=>{ const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ '+root; const els=[...r.querySelectorAll('button,a,[role=tab]')].filter(VIS);
  const e=els.find(x=>N(x.innerText)===t)||els.find(x=>N(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok'; };
window.SETV=(sel,val)=>{ const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
  Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; };
window.ROWTXT=(t)=>{ const r=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>N(x.innerText).indexOf(t)>=0); return r?N(r.innerText):''; };
window.ROW=(t)=>{ const r=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>N(x.innerText).indexOf(t)>=0); if(!r) return 'sem linha '+t; (r.querySelector('.g2pw')||r).click(); return 'ok'; };
window.PAN=()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); return a?N(a.innerText):''; };
window.TOAST=()=>[...document.querySelectorAll('[role=status]')].map(x=>N(x.innerText)).filter(Boolean).join(' | ');
window.ALERTS=()=>[...document.querySelectorAll('[role=alert]')].filter(VIS).map(x=>N(x.innerText)).join(' | ');
window.CEN=()=>JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null');
'ok'"""
FALSO = re.compile(r'(^|[^\d.,])0 sc\b|0,00 sc/ha|−100,0 %')   # zero falso; "6.270 sc" não conta


def rodar():
    t = T(); J = t.J
    def lib(): J(LIB)
    def ir(pg, w=1440, h=1000):
        t.c.size(w, h); t.goto(pg); time.sleep(.4); lib()
    def clk(x, root=None): r = J(f"CLK({json.dumps(x)},{json.dumps(root)})"); time.sleep(.45); return r
    def setv(sel, val): r = J(f"SETV({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.25); return r
    def faz(f): J(f"SETV('select[aria-label=\"Filtrar por fazenda\"]',{json.dumps(f)})"); time.sleep(.45)
    def cen(expr): return J(f"(()=>{{ const c=CEN(); return ({expr}); }})()")
    def falso(s): return bool(FALSO.search(s))
    shot = lambda n: t.c.shot(os.path.join(HERE, '_probe', 'cafe_apurar_' + n + '.png'))
    try:
        t.c.size(1440, 1000); t.goto('Main.dc.html'); J("localStorage.clear(); sessionStorage.clear()")
        # preparo sintético: O.S. de colheita de café do C1 (Santa Rita) em execução, com 5 ha apontados em 25/09
        ir('CARGA.dc.html')
        J("window.__car.cenMudar(null,c=>{ c.ordens['OS-0930']={id:'OS-0930',tipo:'Colheita de café',talhao:'C1',area:0,etapa:'Em execução',versao:'v1',realizado:5,saldo:0,resp:'Sérgio',ins:[],req:null,selos:[],"
          "ap:[{d:'25/09',dia:1,ha:5,st:'Conferido',sinc:true,origem:'web'}],reservado:false,osc:{}}; return {msg:''}; })")
        # desde a CONF (v57) pesar e receber é decisão do almoxarife: a pesagem age como Rui (Ver como); a colheita volta ao perfil padrão
        J("localStorage.setItem('safrion.perfilDemo','Rui')"); ir('CARGA.dc.html'); faz('Santa Rita')
        # erro: café sem litros é recusado junto ao campo, nada gravado
        n0 = cen("Object.keys(c.producao.cargas).length")
        clk('Registrar pesagem'); clk('OS-0930 · C1', 'aside'); setv('#pf_dcol', '25/09'); setv('#pf_tk', 'TK-CF1'); setv('#pf_bruto', '9200'); setv('#pf_tara', '3200'); clk('Íntegra', 'aside')
        clk('Registrar pesagem', 'aside'); e = (J("ALERTS()") or '') + ' ' + (J("TOAST()") or '')
        t.chk('erro: pesagem de café sem litros é recusada ("Informe os litros de café da roça"), nada gravado', 'litros de café da roça' in e and cen("Object.keys(c.producao.cargas).length") == n0, e[:200])
        # normal: com 12.000 L a carga entra; o aviso não fala em 0 sc nem 0,00 sc/ha
        setv('#pf_lit', '12000'); clk('Registrar pesagem', 'aside'); ts = J("TOAST()") or ''
        g = cen("Object.values(c.producao.cargas).filter(g=>g.st==='Recebida'&&g.cultura==='Café').map(g=>g.id+' '+g.litros+' '+g.lote)")
        t.chk('pesagem de 12.000 L recebida pela tela; o aviso diz "sc/ha a apurar" no passe, sem zero falso', len(g or []) == 1 and ' 12000 ' in g[0] and 'sc/ha a apurar' in ts and not falso(ts), [g, ts[:220]])
        # repetição: o mesmo ticket com o mesmo conteúdo não soma de novo (comando direto, como um reenvio)
        rp = J("(()=>{ const r=window.__car.cenMudar(null,c=>window.__pr.prReceber(c,{os:'OS-0930',ticket:'TK-CF1',bruto:9200,tara:3200,litros:12000,cond:'Íntegra',dcol:'2026-09-25',local:c.producao.cargas[Object.keys(c.producao.cargas).find(k=>c.producao.cargas[k].ticket==='TK-CF1')].local})); return r.erro||r.msg; })()") or ''
        t.chk('repetição: o mesmo ticket com o mesmo conteúdo é a mesma carga, nada somado', 'nada foi somado de novo' in rp and cen("Object.values(c.producao.cargas).filter(g=>g.st==='Recebida'&&g.cultura==='Café').length") == 1, rp[:200])
        shot('1_carga'); J("localStorage.removeItem('safrion.perfilDemo')")
        # Previsão e colheita (1440 px): linha, total da cultura e painel
        ir('COLH.dc.html'); faz('Santa Rita'); lc = J("ROWTXT('C1')") or ''; gr = J("ROWTXT('Café 1 talhão')") or J("ROWTXT('Café')") or ''
        t.chk('COLH: linha do C1 "12.000 L · sc a apurar", "sc/ha a apurar", meta a apurar; nenhum 0 sc, 0,00 sc/ha ou −100,0 %',
              '12.000 L · sc a apurar' in lc and 'sc/ha a apurar' in lc and 'a apurar' in lc and not falso(lc), lc[:300])
        t.chk('COLH: total da cultura Café não soma o café a apurar como zero (12.000 L · sc a apurar; produtividade a apurar)', '12.000 L · sc a apurar' in gr and 'sc/ha a apurar' in gr and not falso(gr), gr[:300])
        J("ROW('C1')"); time.sleep(.5); p = J("PAN()") or ''
        t.chk('COLH: painel do C1 com colhido e produtividade a apurar e o passe da OS-0930 sem zero falso', re.search(r'colhido na safra 12\.000 L · sc a apurar', p, re.I) and 'sc/ha a apurar' in p and not falso(p), p[:400])
        shot('2_colh')
        # Estoque de produto: o lote Café da roça em L, sem saca derivada
        ir('PROD.dc.html'); faz('Santa Rita'); lt = J("ROWTXT('Café da roça')") or ''
        t.chk('PROD: lote Café da roça 12.000 L (Em processo), nunca "200 sc"', '12.000 L' in lt and '200 sc' not in lt and ' sc' not in lt, lt[:300])
        shot('3_prod')
        # 390 px: cartão do talhão sem zero falso e sem rolagem horizontal
        ir('COLH.dc.html', w=390, h=844); faz('Santa Rita'); m = J("N(document.querySelector('main').innerText)") or ''
        i = m.find('C1 · Café'); j = m.find('Sérgio', i); cd = m[i:j] if i >= 0 and j > i else ''   # só o cartão do C1
        t.chk('390 px: cartão do C1 "12.000 L · sc a apurar", sem zero falso e sem rolagem horizontal', '12.000 L · sc a apurar' in cd and not falso(cd) and J("document.documentElement.scrollWidth<=window.innerWidth+1"), cd[:260])
        shot('4_390')
        # transição: o beneficiamento mede o rendimento (o BEN-4 grava o beneficiado rateado na origem da carga) → sacas medidas
        J("window.__car.cenMudar(null,c=>{ Object.values(c.producao.cargas).filter(g=>g.cultura==='Café').forEach(g=>g.origem.forEach(x=>{ x.ben=3000; })); return {msg:''}; })")
        ir('COLH.dc.html'); faz('Santa Rita'); lc2 = J("ROWTXT('C1')") or ''
        t.chk('transição: rendimento medido 3.000 kg → "50 sc", "10,00 sc/ha · safra parcial" e desvio contra a meta (−73,7 %)', '50 sc' in lc2 and '10,00 sc/ha' in lc2 and '−73,7 %' in lc2 and 'a apurar' not in lc2, lc2[:300])
        t.chk('nenhuma página com erro de JS', not t.errs(), t.errs())
    finally:
        t.fim()
    return 0 if all(t.ok) else 1
