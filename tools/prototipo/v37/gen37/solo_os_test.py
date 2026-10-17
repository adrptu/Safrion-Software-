# -*- coding: utf-8 -*-
"""Análise de solo na Ordem de Serviço (SOLO-01 · docs/analise-solo/ESPECIFICACAO.md §3.5 e §8) · teste de navegador, desktop e 390 px.
AC-SOLO-14: "Usar 1.800" no Planejar safra → OS-0502 em A liberar com o selo "Plano mudou pela análise", Kanban com 5 fases, primário
"Ajustar antes de liberar" (um só), o bloqueio de estoque visível e sem "Liberar com 2.000 kg/ha" (revisão A6); ajustar abre com 1.800; "Salvar e liberar" recusa pelo
estoque; "Salvar ajuste" grava a v2 e o selo some; com o lote elevado Ana aprova e libera (CMD-42 + CMD-06 com 1.800); nenhuma REC/DIA nova.
AC-SOLO-16: Nova ordem do T1-A com o uso da análise → KCl 150 kg/ha × 160 ha = 24.000 kg, origem "pela análise · LAU-2061".
AC-SOLO-20: Nova ordem da Calagem incluída no T2 → Calcário dolomítico (Corretivos) 1,2 t/ha × 298 ha = 357,6 t; a regra legal não trava;
o liberar fica bloqueado só por estoque e o dono é Suprimentos.
celular (390 × 844): OS-0502 com o selo, um só primário, painel em tela cheia e sem rolagem lateral da página.
Uso: env CHROME_BIN=… flock /tmp/cdpC.lock env CDP_GL=1 timeout 900 python3 solo_os_test.py [desktop|celular]
Capturas em _probe/solo_os_*.png. Dados sintéticos."""
import sys, os, time, json, re
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cadc_lib import T
MODOS = [a for a in sys.argv[1:] if a in ('desktop', 'celular')] or ['desktop', 'celular']
PR = os.path.join(HERE, '_probe'); os.makedirs(PR, exist_ok=True)
t = T(); J = t.J
LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.TOP=()=>[...document.querySelectorAll('aside[role=dialog]')].filter(VIS).pop()||null;
window.CLK=(t,inPan)=>{ const r=inPan?TOP():document; if(!r) return 'SEM PAINEL'; const els=[...r.querySelectorAll('button,a')].filter(VIS);
  const e=els.find(x=>N(x.innerText)===t)||els.find(x=>N(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok'; };
window.EXP=(local)=>{ const g=local.split('-')[0]; const F='button.g2car[aria-expanded=false]';   /* TAB-11: o grupo fechado é o da seta com aria-expanded=false (antes o texto "▸ T1 …") */
  const gr=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>x.querySelector(F)&&N(x.innerText).startsWith(g+' ')); if(!gr) return false; const b=gr.querySelector(F); if(b){ b.click(); return true; } return false; };
/* TAB-11: a linha do cultivo, não a linha-grupo do talhão (com a seta de abrir): antes, o texto da linha-grupo começava pelo glifo ▾/▸ */
window.INS=(local)=>{ const row=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>!x.querySelector('button.g2car')&&N(x.innerText).startsWith(local+' ')); if(!row) return 'sem linha '+local;
  (row.querySelector('.g2pw')||row).click(); return 'ok'; };
/* SAF-TAB: a ação de insumos pertence ao detalhe do cultivo, não à célula da listagem. */
window.INSA=(local)=>{ const a=TOP(); const b=a&&[...a.querySelectorAll('button')].filter(VIS).find(b=>['Ajustar insumos e doses de '+local,'Ver insumos e doses de '+local].includes(N(b.innerText))); if(!b) return 'sem ação de insumos '+local; b.click(); return 'ok'; };
window.ORD=(id)=>{ const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>N(r.innerText).startsWith(id)); if(!r) return 'sem '+id; r.click(); return 'ok'; };
window.PAN=()=>{ const a=TOP(); if(!a) return ''; [...a.querySelectorAll('section[aria-label] > button[aria-expanded="false"]')].forEach(b=>b.click()); return N(a.innerText); };
/* TAB-12 (17/10/2026): a faixa da fazenda (Planejar safra › etapa 2) e os grupos e atividades do ajuste local nascem recolhidos; a pessoa abre */
window.FAIXA=()=>{ const b=[...document.querySelectorAll('[role=row].g2fgrp button.g2car[aria-expanded=false]')].find(VIS); if(!b) return false; b.click(); return true; };
window.ABRE_LP=()=>{ const a=TOP(); const b=a&&[...a.querySelectorAll('button.g2car[aria-expanded=false]')].find(VIS); if(!b) return false; b.click(); return true; };
window.TOAST=()=>[...document.querySelectorAll('[role=status]')].map(x=>N(x.innerText)).filter(Boolean).join(' | ');
window.PRIMS=()=>{ const a=TOP(); return a?[...a.querySelectorAll('button,a')].filter(e=>VIS(e)&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)').map(e=>N(e.innerText)):[]; };
window.SETV=(sel,val)=>{ const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; };
window.OPT=(sel,txt)=>{ const s=document.querySelector(sel); if(!s) return 'sem select'; const o=[...s.options].find(o=>o.text.indexOf(txt)>=0); if(!o) return 'sem opção '+txt+' · '+[...s.options].map(o=>o.text).join(' | '); return SETV(sel,o.value); };
window.CENO=()=>JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null');
'ok'"""
def lib(): J(LIB)
def ir(pg, limpa=False, espera=1.4, w=1440, h=1000):
    t.c.size(w, h)
    if limpa:
        t.goto('Main.dc.html'); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    t.goto(pg); time.sleep(espera); lib()
def clk(x, pan=False, w=.6): r = J(f"CLK({json.dumps(x)},{'true' if pan else 'false'})"); time.sleep(w); return r
def ins(local):
    for _ in range(4):   # TAB-12: a pessoa abre a faixa da fazenda (uma por vez: cada clique redesenha a tabela)
        if not J("FAIXA()"): break
        time.sleep(.4)
    r = J(f"INS({json.dumps(local)})")
    if str(r).startswith('sem linha') and J(f"EXP({json.dumps(local)})"): time.sleep(.5); r = J(f"INS({json.dumps(local)})")
    if r == 'ok':
        limite = time.monotonic() + 3
        while time.monotonic() < limite:
            r = J(f"INSA({json.dumps(local)})")
            if r == 'ok': break
            time.sleep(.05)
    if r != 'ok': raise AssertionError('Abrir insumos de '+local+': '+str(r))
    time.sleep(.3)
    for _ in range(80):   # TAB-12: grupos e atividades do ajuste local nascem recolhidos; a pessoa abre o que vai ajustar (aqui, tudo)
        if not J("ABRE_LP()"): break
        time.sleep(.12)
    limite = time.monotonic() + 3
    while time.monotonic() < limite:
        if J("!!(TOP()&&TOP().querySelector('input[aria-label^=\"Dose local de \"]'))"): return r
        time.sleep(.05)
    raise AssertionError('Painel de insumos não ficou pronto: '+local)
def pan(): return J("PAN()") or ''
def toast(): return J("TOAST()") or ''
def cen(expr): return J(f"(()=>{{ const c=CENO(); return ({expr}); }})()")
def nova(saf, cult, atv, jan):
    clk('Criar ordem'); a = J(f"OPT('#nv_saf',{json.dumps(saf)})"); time.sleep(.3); b = J(f"OPT('#nv_cult',{json.dumps(cult)})"); time.sleep(.3)
    c = J(f"OPT('#nv_atv',{json.dumps(atv)})"); time.sleep(.3); d = J(f"SETV('#nv_jan',{json.dumps(jan)})"); time.sleep(.3); clk('Emitir ordem', True, .9)
    return [a, b, c, d]
def shot(n): t.c.shot(os.path.join(PR, 'solo_os_' + n + '.png'))

try:
    if 'desktop' in MODOS:
        print('== desktop · O.S. com a análise de solo')
        # ---- AC-SOLO-14: Usar 1.800 no Pivô 12 (Planejar safra) → OS-0502
        ir('SAF.dc.html#saf=LG2627&passo=cultivos', limpa=True)
        mip0 = J("localStorage.getItem('talhao-os-mip-v1')")
        r = ins('Pivô 12'); clk('Usar 1.800 kg/ha', True); clk('Salvar', True, 1.0)
        t.chk('Planejar safra: "Usar 1.800" grava o uso da análise na calagem do Pivô 12', cen("((c.solo||{}).aceites||{})['lg12|i1|Calcário dolomítico filler']") and cen("c.solo.aceites['lg12|i1|Calcário dolomítico filler'].dose") == 1800, [r, toast()])
        ir('OS.dc.html#OS-0502'); p = pan()
        t.chk('AC-SOLO-14 OS-0502 em A liberar com o selo "Plano mudou pela análise · 1.800 kg/ha (O.S. 2.000)"', 'Plano mudou pela análise · 1.800 kg/ha (O.S. 2.000)' in p and 'A liberar' in p, p[:500])
        kb = J("(()=>{ const hs=[...document.querySelectorAll('main span')].map(s=>N(s.innerText)).filter(x=>['A LIBERAR','LIBERADAS','EM EXECUÇÃO','EM CONFERÊNCIA','ENCERRADAS','A liberar','Liberadas','Em execução','Em conferência','Encerradas'].indexOf(x)>=0); return [...new Set(hs.map(x=>x.toUpperCase()))]; })()")
        t.chk('Kanban com as 5 fases (sem coluna nova)', kb == ['A LIBERAR', 'LIBERADAS', 'EM EXECUÇÃO', 'EM CONFERÊNCIA', 'ENCERRADAS'], kb)
        # revisão A6 (10/10): o lote LG26-03 (60.000 kg) não cobre os 96.940 kg da O.S.; o bloqueio de estoque fica visível e "Liberar com 2.000" sai
        # (o comando recusaria). Com estoque que cobre, o secundário volta: solo_rev_test.py (A6)
        t.chk('AC-SOLO-14 primário "Ajustar antes de liberar" (um só); com o estoque curto, "Liberar bloqueado: saldo insuficiente" visível e sem "Liberar com 2.000 kg/ha"',
              J("PRIMS()") == ['Ajustar antes de liberar'] and 'Liberar bloqueado: saldo insuficiente de Calcário dolomítico filler: 60.000 kg disponíveis' in p and 'Liberar com 2.000 kg/ha' not in p, [J("PRIMS()"), p[p.find('PRÓXIMO'):][:400]])
        t.chk('AC-SOLO-14 a origem da dose aparece na linha do insumo (padrão do plano v1)', 'padrão do plano v1' in p, p[p.find('INSUMOS'):][:300])
        clk('Ajustar antes de liberar', True); p = pan()
        d0 = J("(document.getElementById('aj_d0')||{}).value")
        t.chk('AC-SOLO-14 ajustar abre com 1.800 no campo e mostra "O.S. 2.000 → plano 1.800"', d0 == '1.800' and 'O.S. 2.000 → plano 1.800' in p, [d0, p[p.find('Dose'):][:300]])
        clk('Salvar e liberar', True); p = pan()
        t.chk('AC-SOLO-14 "Salvar e liberar" recusa pelo estoque (60.000 kg para 87.246 kg)', '60.000 kg disponíveis no lote LG26-03 para 87.246 kg' in p and cen("c.ordens['OS-0502'].etapa") == 'A liberar', p[p.find('Dose'):][:400])
        clk('Salvar ajuste', True, 1.0); p = pan()
        o = cen("[c.ordens['OS-0502'].etapa, c.ordens['OS-0502'].versao, c.ordens['OS-0502'].ins[0].dose, c.ordens['OS-0502'].ins[0].tot]")
        t.chk('AC-SOLO-14 "Salvar ajuste" grava a v2 com 1.800 kg/ha, sem liberar, e o selo some', o and o[0] == 'A liberar' and o[1].endswith('v2') and o[2] == 1800 and o[3] == 87246 and 'Plano mudou' not in p, [o, toast(), p[:300]])
        t.chk('R21 a linha do insumo diz "ajustado pelo agrônomo na O.S. v2"', 'ajustado pelo agrônomo na O.S. v2' in p, p[p.find('INSUMOS'):][:300])
        # lote elevado no teste (recebimento de 30/09) e Ana libera
        J("(()=>{ const c=CENO(); c.lotes['Calcário dolomítico filler|LG26-03'].fisico=110000; localStorage.setItem('talhao-os-cenario-v1',JSON.stringify(c)); })()")
        ir('OS.dc.html#OS-0502'); clk('Liberar para execução', True); clk('Confirmar liberação', True, 1.0)
        ev = cen("((c.ordens['OS-0502'].osc||{}).ev||[]).map(e=>e.cmd+'|'+e.t)") or []
        t.chk('AC-SOLO-14 com o lote elevado a 110.000 kg, Ana libera: CMD-42 com 1.800 kg/ha e CMD-06', cen("c.ordens['OS-0502'].etapa") == 'Liberadas' and len(ev) == 2 and 'CMD-42' in ev[0] and '1.800 kg/ha' in ev[0] and 'CMD-06' in ev[1], [ev, toast()])
        t.chk('AC-SOLO-14 nenhuma REC/DIA nova (o uso da análise não cria recomendação nem diagnóstico)', J("localStorage.getItem('talhao-os-mip-v1')") == mip0, (mip0 or '')[:80])
        shot('os0502')
        # ---- AC-SOLO-16: Nova ordem do T1-A com o uso da análise
        ir('SAF.dc.html#saf=S2627&passo=cultivos', limpa=True); ins('T1-A'); clk('Usar 150 kg/ha', True); clk('Salvar', True, 1.0)
        ir('OS.dc.html'); r = nova('Safra 2026/27', 'T1-A', 'Adubação de cobertura', '2026-11-04'); p = pan()
        nid = J("(()=>{ const a=TOP(); return a?(a.getAttribute('aria-label')||'').split(' · ')[0]:''; })()")
        o = cen(f"(()=>{{ const o=c.ordens[{json.dumps(nid)}]; return o?[o.etapa,o.ins.map(x=>[x.p,x.dose,x.tot,x.un,x.orig,x.g])]:null; }})()")
        t.chk('AC-SOLO-16 Nova ordem do T1-A · Adubação de cobertura → KCl 150 kg/ha × 160 ha = 24.000 kg, "pela análise · LAU-2061"',
              o and o[0] == 'A liberar' and o[1] == [['KCl 60%', 150, 24000, 'kg', 'pela análise · LAU-2061', 'Fertilizantes']] and 'pela análise · LAU-2061' in p, [r, nid, o, p[p.find('INSUMOS'):][:300]])
        # ---- AC-SOLO-20: Nova ordem da Calagem incluída no T2
        ir('SAF.dc.html#saf=S2627&passo=cultivos', limpa=True); ins('T2'); clk('Incluir calagem', True); clk('Retirar pela análise', True); clk('Salvar', True, 1.0)
        ir('OS.dc.html'); r = nova('Safra 2026/27', 'T2 ·', 'Calagem', '2026-09-30'); p = pan()
        opts = J("[...document.querySelectorAll('#nv_atv option')].map(o=>o.text)")
        nid = J("(()=>{ const a=TOP(); return a?(a.getAttribute('aria-label')||'').split(' · ')[0]:''; })()")
        o = cen(f"(()=>{{ const o=c.ordens[{json.dumps(nid)}]; return o?[o.etapa,o.tipo,o.ins.map(x=>[x.p,x.dose,x.tot,x.un,x.g]),o.osc.novo.keys]:null; }})()")
        t.chk('AC-SOLO-20 Nova ordem da Calagem incluída no T2 → A liberar, Calcário dolomítico (Corretivos) 1,2 t/ha × 298 ha = 357,6 t',
              o and o[0] == 'A liberar' and o[2] == [['Calcário dolomítico', 1.2, 357.6, 't', 'Corretivos']] and o[3] == ['c3|solo:LAU-2063:cal'], [r, nid, o])
        t.chk('AC-SOLO-20 a regra legal não trava (corretivo fora do registro de agrotóxico); o liberar fica bloqueado só por estoque e o dono é Suprimentos',
              'Fora do registro' not in p and 'sem lote de Calcário dolomítico' in p.lower().replace('calcário','Calcário') and 'Suprimentos' in p and 'Falta insumo · Calcário dolomítico' in p, p[:700])
        t.chk('a Adubação de cobertura do T2 saiu do cultivo (único insumo retirado pela análise): não aparece na Nova ordem', not any('Adubação de cobertura' in x for x in (opts or [])), opts)
        shot('nova_calagem')
        t.chk('nenhum erro de JS (desktop)', not t.errs(), t.errs())
    if 'celular' in MODOS:
        print('== celular · 390 × 844')
        ir('SAF.dc.html#saf=LG2627&passo=cultivos', limpa=True)
        ins('Pivô 12'); clk('Usar 1.800 kg/ha', True); clk('Salvar', True, 1.0)
        ir('OS.dc.html#OS-0502', w=390, h=844); p = pan()
        g = J("(()=>{ const a=TOP(); if(!a) return null; return [Math.round(a.getBoundingClientRect().width), PRIMS(), document.documentElement.scrollWidth<=innerWidth+1]; })()")
        t.chk('390 px: OS-0502 com o selo "Plano mudou pela análise", um só primário (Ajustar antes de liberar), painel em tela cheia e sem rolagem lateral',
              'Plano mudou pela análise · 1.800 kg/ha (O.S. 2.000)' in p and g and g[0] >= 388 and g[1] == ['Ajustar antes de liberar'] and g[2], [g, p[:300]])
        shot('celular_os0502')
        t.chk('nenhum erro de JS (celular)', not t.errs(), t.errs())
finally:
    t.fim()

