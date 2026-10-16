# -*- coding: utf-8 -*-
"""Análise de solo no Planejar safra (SOLO-01 · docs/analise-solo/ESPECIFICACAO.md §3.2–§3.4 e §8) · teste de navegador.
Modos (um por vez, cada um abre o Chrome headless do cadc_lib.T):
  desktop  1440 × 1000: AC-SOLO-05 sem laudo nada pede laudo e o link some com 0 sugestões; AC-SOLO-08 linha "Análise sugere", Por quê,
           Usar, Cancelar não grava, Salvar grava (+4.800 kg de KCl); AC-SOLO-12 uma dose por chave (manual desfaz o aceite, Restaurar,
           reabrir e salvar sem mudar, desfazer em outra aba); AC-SOLO-11 meta viva; AC-SOLO-09 lote com a mesma chave e conflito;
           AC-SOLO-10 lote das 4 sugestões (KCl −26.400 kg, calcário +357,6 t, +R$ 1.008,00; o T2 perde a cobertura e ganha a calagem);
           lote com uma linha negada pela R11; "Ver no plano" do AG-02 abre o lote.
  celular  390 × 844: painel de insumos e lote em tela cheia, linha da sugestão em até 3 linhas com botões de 44 px, sem rolagem lateral.
Uso: env CHROME_BIN=… flock /tmp/cdpC.lock env CDP_GL=1 timeout 900 python3 solo_saf_test.py [desktop|celular]
Capturas em _probe/solo_saf_*.png. Dados sintéticos."""
import sys, os, time, json
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
window.CLK=(t,inPan)=>{ const r=inPan?TOP():document; if(!r) return 'SEM PAINEL'; const els=[...r.querySelectorAll('button,a,summary')].filter(VIS);
  const e=els.find(x=>N(x.innerText)===t)||els.find(x=>N(x.innerText).startsWith(t))||els.find(x=>(x.getAttribute('aria-label')||'')===t); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok'; };
window.EXP=(local)=>{ const g=local.split('-')[0]; const F='button.g2car[aria-expanded=false]';   /* TAB-11: o grupo fechado é o da seta com aria-expanded=false (antes o texto "▸ T1 …") */
  const gr=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>x.querySelector(F)&&N(x.innerText).startsWith(g+' ')); if(!gr) return false; const b=gr.querySelector(F); if(b){ b.click(); return true; } return false; };
window.INS=(local)=>{ let row=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>N(x.innerText).startsWith(local+' ')); if(!row) return 'sem linha '+local;
  (row.querySelector('.g2pw')||row).click(); return 'ok'; };
/* SAF-TAB: a ação de insumos pertence ao detalhe do cultivo, não à célula da listagem. */
window.INSA=(local)=>{ const a=TOP(); const b=a&&[...a.querySelectorAll('button')].filter(VIS).find(b=>['Ajustar insumos e doses de '+local,'Ver insumos e doses de '+local].includes(N(b.innerText))); if(!b) return 'sem ação de insumos '+local; b.click(); return 'ok'; };
window.LINHA=(local)=>{ const row=[...document.querySelectorAll('[role=row].g2ed')].filter(VIS).find(x=>N(x.innerText).startsWith(local+' ')); if(!row) return 'sem linha '+local; (row.querySelector('.g2pw')||row).click(); return 'ok'; };
window.PAN=()=>{ const a=TOP(); return a?N(a.innerText):''; };
window.TOAST=()=>[...document.querySelectorAll('[role=status]')].map(x=>N(x.innerText)).filter(Boolean).join(' | ');
window.ALERT=()=>{ const a=TOP(); return a?[...a.querySelectorAll('[role=alert]')].filter(VIS).map(x=>N(x.innerText)).join(' | '):''; };
window.KCL=()=>{ const a=TOP(); const i=a&&[...a.querySelectorAll('input')].find(x=>(x.getAttribute('aria-label')||'')==='Dose local de KCl 60%'); return i?i.value:null; };
window.SETKCL=(v)=>{ const a=TOP(); const i=a&&[...a.querySelectorAll('input')].find(x=>(x.getAttribute('aria-label')||'')==='Dose local de KCl 60%'); if(!i) return 'sem campo';
  Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,v); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; };
window.AC=(k)=>{ const c=__solo.cen(); return ((c.solo||{}).aceites||{})[k]||null; };
'ok'"""
def lib(): J(LIB)
def ir(pg, w=1440, h=1000, limpa=False, perfil='Ana', espera=1.4):
    t.c.size(w, h)
    if limpa:
        t.goto('Main.dc.html'); J("localStorage.clear(); sessionStorage.clear()"); J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)})")
    t.goto(pg); time.sleep(espera); lib()
def clk(x, pan=False, w=.5): r = J(f"CLK({json.dumps(x)},{'true' if pan else 'false'})"); time.sleep(w); return r
def ins(local, w=.7):
    r = J(f"INS({json.dumps(local)})")
    if str(r).startswith('sem linha') and J(f"EXP({json.dumps(local)})"): time.sleep(.5); r = J(f"INS({json.dumps(local)})")
    if r == 'ok':
        limite = time.monotonic() + 3
        while time.monotonic() < limite:
            r = J(f"INSA({json.dumps(local)})")
            if r == 'ok': break
            time.sleep(.05)
    if r != 'ok': raise AssertionError('Abrir insumos de '+local+': '+str(r))
    limite = time.monotonic() + 3
    while time.monotonic() < limite:
        if J("!!(TOP()&&TOP().querySelector('input[aria-label^=\"Dose local de \"]'))"): return r
        time.sleep(.05)
    raise AssertionError('Painel de insumos não ficou pronto: '+local)
def pan(): return J("PAN()") or ''
def toast(): return J("TOAST()") or ''
def dem(saf=None): return J(f"__solo.dem({json.dumps(saf) if saf else ''})") or {}
def bruta(d, n): return round((d.get(n) or {}).get('bruta', 0), 2)
def shot(n): t.c.shot(os.path.join(PR, 'solo_saf_' + n + '.png'))
def salvar(w=.8): return clk('Salvar', True, w)

try:
    if 'desktop' in MODOS:
        print('== desktop · Planejar safra com a análise de solo')
        ir('SAF.dc.html#saf=S2627&passo=cultivos', limpa=True)
        d0 = dem(); k0, c0 = bruta(d0, 'KCl 60%'), bruta(d0, 'Calcário dolomítico')
        t.chk('base: demanda bruta de KCl 60% da Safra 2026/27 lida do mesmo cálculo da etapa 4 (sem aceite)', k0 > 70000 and c0 == 0, [k0, c0])
        # ---- AC-SOLO-05: sem laudo nada pede laudo; o link só com sugestão
        lnk = J("(document.getElementById('sg_lnk')||{}).innerText||''")
        t.chk('link "Sugestões pelas análises · 4" na etapa 2 da Safra 2026/27', lnk == 'Sugestões pelas análises · 4', lnk)
        ins('T7'); p = pan()
        t.chk('AC-SOLO-05 T7 (sem laudo validado): painel sem "sem análise"/"sem laudo" e sem sugestão', 'sem análise' not in p.lower() and 'sem laudo' not in p.lower() and 'Análise sugere' not in p, p[:300])
        J("(()=>{ const a=TOP(); const i=[...a.querySelectorAll('input')].find(x=>(x.getAttribute('aria-label')||'')==='Dose local de Nitrato de cálcio'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'45'); i.dispatchEvent(new Event('change',{bubbles:true})); })()"); time.sleep(.3)
        salvar()
        t.chk('AC-SOLO-05 o T7 salva dose manual sem nada pedir', '1 dose alterada em T7' in toast() and not J("TOP()"), toast())
        txt = J("document.querySelector('main').innerText") or ''
        for passo in ('operacoes', 'demanda'):
            ir('SAF.dc.html#saf=S2627&passo=' + passo); txt += J("document.querySelector('main').innerText") or ''
        t.chk('AC-SOLO-05 etapas 2 a 4 sem "sem análise" ou "sem laudo"', 'sem análise' not in txt.lower() and 'sem laudo' not in txt.lower())
        ir('SAF.dc.html#saf=S27SF&passo=cultivos')
        t.chk('AC-SOLO-05 Safrinha 2027 (0 sugestões: a calagem do T2 ficou na Safra 2026/27): o link não aparece', not J("!!document.getElementById('sg_lnk')"), J("(document.getElementById('sg_lnk')||{}).innerText"))
        # ---- AC-SOLO-08: linha, Por quê, Usar, Cancelar, Salvar
        ir('SAF.dc.html#saf=S2627&passo=cultivos', limpa=True); ins('T1-A'); p = pan()
        t.chk('AC-SOLO-08 T1-A: "Análise sugere 150 kg/ha · +4.800 kg no talhão · Por quê · Usar 150 kg/ha" sob o KCl', 'Análise sugere 150 kg/ha · +4.800 kg no talhão · Por quê · Usar 150 kg/ha' in p, p[p.find('KCl'):p.find('KCl') + 200])
        t.chk('uma só primária no painel de insumos (Salvar)', J("(()=>{ const a=TOP(); return [...a.querySelectorAll('button')].filter(b=>VIS(b)&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').map(b=>N(b.innerText)); })()") == ['Salvar'])
        clk('Por quê', True); q = pan()
        t.chk('AC-SOLO-08 Por quê: laudo, profundidade, método, regra rotulada e conta', all(x in q for x in ['LAU-2061 · T1 · 0–20 cm', 'Mehlich-1', 'Demonstração — tabela regional a decidir pelo proprietário', '90 ÷ 0,6 = 150', '3.840 kg/ha', '+4.800 kg']), q[:700])
        clk('Usar 150 kg/ha', True); p = pan()
        t.chk('"Usar" no Por quê preenche o rascunho (150) e fecha o Por quê; chip "pela análise · LAU-2061"', J("KCL()") == '150' and 'pela análise · LAU-2061' in p and 'Por quê ·' not in p.split('KCl 60%')[1][:60], [J("KCL()"), p[p.find('KCl'):p.find('KCl') + 160]])
        clk('Cancelar', True); clk('Descartar alterações', True)
        t.chk('AC-SOLO-08 Cancelar antes de salvar → nada gravado', not J("AC('c1|a4|KCl 60%')") and bruta(dem(), 'KCl 60%') == k0, J("AC('c1|a4|KCl 60%')"))
        ins('T1-A'); clk('Usar 150 kg/ha', True); salvar()
        a = J("AC('c1|a4|KCl 60%')"); k1 = bruta(dem(), 'KCl 60%')
        t.chk('AC-SOLO-08 Salvar grava o aceite (pela análise, LAU-2061, quem e quando) e a demanda bruta de KCl sobe 4.800 kg exatos', a and a['dose'] == 150 and a['laudo'] == 'LAU-2061' and a['por'].startswith('Ana') and round(k1 - k0, 2) == 4800, [a and (a['dose'], a['por'], a['em']), k1 - k0, toast()])
        ins('T1-A'); p = pan()
        t.chk('reabrir: chip "pela análise · LAU-2061", padrão 120,00 kg/ha visível e sem linha de sugestão', 'pela análise · LAU-2061' in p and '120,00 kg/ha' in p and 'Análise sugere' not in p, p[p.find('KCl'):p.find('KCl') + 200])
        mem = (dem().get('KCl 60%') or {}).get('memo') or []
        t.chk('R21 memória da demanda diz a origem da dose (pela análise · LAU-2061)', any('pela análise · LAU-2061' in m for m in mem), mem[:4])
        # ---- AC-SOLO-12: uma dose por chave
        J("SETKCL('140')"); time.sleep(.3); salvar()
        a = J("AC('c1|a4|KCl 60%')"); ins('T1-A'); p = pan()
        t.chk('AC-SOLO-12 mudar à mão para 140 e salvar → "ajustado pelo usuário"; "Análise sugere 150 · Usar" volta; aceite "substituído por ajuste manual"; demanda com 140',
              'ajustado pelo usuário' in p and 'Análise sugere 150 kg/ha' in p and a['st'] == 'substituído por ajuste manual' and round(bruta(dem(), 'KCl 60%') - k0, 2) == 3200, [a['st'], bruta(dem(), 'KCl 60%') - k0, p[p.find('KCl'):p.find('KCl') + 200]])
        clk('Restaurar dose', True); salvar()
        t.chk('AC-SOLO-12 Restaurar → 120 (demanda de volta à base)', round(bruta(dem(), 'KCl 60%'), 2) == k0, bruta(dem(), 'KCl 60%') - k0)
        ins('T1-A'); clk('Usar 150 kg/ha', True); salvar(); ins('T1-A'); salvar()
        a = J("AC('c1|a4|KCl 60%')"); ins('T1-A'); p = pan(); clk('Cancelar', True)
        t.chk('AC-SOLO-12 Usar 150 e salvar; reabrir e salvar sem mudar → continua "pela análise" (nada vira ajuste da sessão)', a['st'] == 'ativo' and a['dose'] == 150 and 'pela análise · LAU-2061' in p and round(bruta(dem(), 'KCl 60%') - k0, 2) == 4800, [a['st'], p[p.find('KCl'):p.find('KCl') + 120]])
        r = J("__solo.desfazer('c1|a4|KCl 60%','K-OUTRA-ABA-1')"); time.sleep(.5)
        t.chk('AC-SOLO-12 desfazer como de outra aba → demanda volta a 120 (nenhuma cópia na sessão)', round(bruta(dem(), 'KCl 60%'), 2) == k0 and J("AC('c1|a4|KCl 60%')")['st'] == 'desfeito', [r, bruta(dem(), 'KCl 60%') - k0])
        # ---- AC-SOLO-11: meta viva (T1-B de 62 para 60 sc/ha)
        J("LINHA('T1-B')"); time.sleep(.5); t.fset('meta', '60'); t.btn('Salvar'); time.sleep(.6)
        ins('T1-B'); p = pan(); clk('Cancelar', True)
        t.chk('AC-SOLO-11 meta do T1-B 62 → 60 sc/ha (3.600 kg/ha): a sugestão some (120 = padrão)', 'Análise sugere' not in p, p[p.find('KCl'):p.find('KCl') + 160])
        J("LINHA('T1-B')"); time.sleep(.5); t.fset('meta', '62'); t.btn('Salvar'); time.sleep(.6)
        ins('T1-B'); clk('Usar 150 kg/ha', True); salvar()
        J("LINHA('T1-B')"); time.sleep(.5); t.fset('meta', '60'); t.btn('Salvar'); time.sleep(.6)
        ins('T1-B'); p = pan(); clk('Cancelar', True)
        t.chk('AC-SOLO-11 com o aceite de 150 feito, "Análise sugere 120 kg/ha · −4.560 kg" reaparece', 'Análise sugere 120 kg/ha · −4.560 kg no talhão' in p, p[p.find('KCl'):p.find('KCl') + 200])
        # ---- AC-SOLO-09: lote com a mesma chave e conflito (gancho de teste)
        ir('SAF.dc.html#saf=S2627&passo=cultivos', limpa=True)
        r1 = J("(()=>{ const it=__solo.sugs(); const a=__solo.aceitarLote(it,'K-LOTE-X'); return [it.length,a.msg||a.erro]; })()"); d1 = dem()
        t.chk('AC-SOLO-09 base do lote: 4 sugestões gravadas com uma chave', r1 and r1[0] == 4 and '4 sugestões usadas' in r1[1], r1)
        ir('SAF.dc.html#saf=S2627&passo=cultivos')
        t.chk('depois do lote o link some (0 sugestões)', not J("!!document.getElementById('sg_lnk')"))
        # ---- AC-SOLO-10: o lote pela tela (nada marcado; marcar as 4)
        ir('SAF.dc.html#saf=S2627&passo=cultivos', limpa=True)
        clk('Sugestões pelas análises · 4'); p = pan()
        sel0 = J("(()=>{ const a=TOP(); return [...a.querySelectorAll('input[type=checkbox]')].filter(i=>i.checked).length; })()")
        pd = J("(()=>{ const a=TOP(); const b=[...a.querySelectorAll('button')].find(b=>/^Usar \\d+ sugest/.test(N(b.innerText))); return b?[N(b.innerText),b.getAttribute('aria-disabled')]:null; })()")
        t.chk('AC-SOLO-10 lote: nenhuma linha vem marcada e "Usar 0 sugestões" fica desabilitado', sel0 == 0 and pd and pd[0] == 'Usar 0 sugestões' and pd[1] == 'true', [sel0, pd])
        t.chk('AC-SOLO-18 lote com busca, filtro rápido por tipo e controles de coluna acessíveis', J("(()=>{ const a=TOP(); if(!a) return false; const hs=[...a.querySelectorAll('[role=columnheader]')].filter(h=>N(h.innerText)); const qs=[...a.querySelectorAll('button')].filter(b=>b.getClientRects().length).map(b=>N(b.innerText).replace(/\\s+\\d+$/,'')); return !!a.querySelector('input[placeholder^=\"Buscar\"]') && ['Outra dose','Incluir','Retirar'].every(t=>qs.includes(t)) && hs.length>=5 && hs.every(h=>{const b=h.querySelector('button[aria-label^=\"Ordenar por \"]'); return !!b&&!!h.querySelector('button[aria-label=\"Filtrar '+b.getAttribute('aria-label').slice(12)+'\"]');}); })()"))
        t.chk('rodapé "Os demais talhões seguem a dose do plano."', 'Os demais talhões seguem a dose do plano.' in p)
        J("(()=>{ const a=TOP(); [...a.querySelectorAll('input[type=checkbox]')].filter(i=>/^Selecionar (?!as )/.test(i.getAttribute('aria-label')||'')&&!i.checked).forEach(i=>i.click()); })()"); time.sleep(.5)
        clk('Usar 4 sugestões', True, 1.0); d2 = dem()
        dk, dc = round(bruta(d2, 'KCl 60%') - k0, 2), round(bruta(d2, 'Calcário dolomítico') - c0, 2)
        t.chk('AC-SOLO-10 aviso com o efeito e demanda bruta: KCl 60% −26.400 kg e Calcário dolomítico +357,6 t',
              '4 sugestões usadas · KCl 60% −26.400 kg · Calcário dolomítico +357,6 t' in toast() and dk == -26400 and dc == 357.6, [toast(), dk, dc])
        t.chk('AC-SOLO-10 custo de insumos +R$ 1.008,00 (−26.400 × 2,40 + 357,6 × 180,00)', round(dk * 2.4 + dc * 180, 2) == 1008, round(dk * 2.4 + dc * 180, 2))
        oc = J("__solo.ocorr().filter(o=>o.cid==='c3').map(o=>[o.atv,o.nome,o.dt,o.op,o.horas>0])") or []
        t.chk('AC-SOLO-10 etapa 3: o T2 perde a Adubação de cobertura de 07/11 e ganha a Calagem de 30/09 (com horas de máquina)',
              not any(x[0] == 'a4' for x in oc) and any(x[0] == 'solo:LAU-2063:cal' and x[2] == '2026-09-30' and x[3] == 'Adubação a lanço' and x[4] for x in oc), oc)
        ins('T2'); p = pan(); clk('Cancelar', True)
        t.chk('painel do T2: Calagem "incluída pela análise · LAU-2063" no topo e o KCl "retirado pela análise"', 'incluída pela análise · LAU-2063' in p and 'retirado pela análise · LAU-2063' in p, p[:600])
        # mesma chave duas vezes e conflito (AC-SOLO-09)
        r3 = J("(()=>{ const it=Object.values(__solo.cen().solo.aceites).map(a=>({k:a.k,cid:a.cid,tipo:a.tipo,atv:a.atv,prod:a.prod,un:a.un,sug:a.dose==='-'?0:a.dose,dif:0,laudo:{id:a.laudo,prof:a.prof},plano:a.plano,dt:a.dt,incl:a.incl,unico:a.unico,grupo:a.grupo,preco:a.preco,padrao:a.padrao,ent:a.ent,conta:a.conta,regra:a.regra,i:0}));"
               " const a=__solo.aceitarLote(it,'K-REP-1'); const b=__solo.aceitarLote(it,'K-REP-1'); const it2=it.map(x=>Object.assign({},x,{sug:x.sug+1})); const c=__solo.aceitarLote(it2,'K-REP-1'); return [a.msg||a.erro,b.msg||b.erro,c.erro||c.msg]; })()")
        t.chk('AC-SOLO-09 mesma chave duas vezes → "Já registrado" e a demanda não muda; mesma chave e outra dose → conflito, nada gravado',
              r3 and str(r3[1]).startswith('Já registrado') and 'Conflito' in str(r3[2]) and round(bruta(dem(), 'KCl 60%') - k0, 2) == -26400, [r3, bruta(dem(), 'KCl 60%') - k0])
        # ---- lote com uma linha negada pela R11 (OS-0502 liberada entre abrir e usar)
        ir('SAF.dc.html#saf=LG2627&passo=cultivos', limpa=True)
        clk('Sugestões pelas análises · 2'); J("(()=>{ const a=TOP(); [...a.querySelectorAll('input[type=checkbox]')].filter(i=>/^Selecionar (?!as )/.test(i.getAttribute('aria-label')||'')&&!i.checked).forEach(i=>i.click()); })()"); time.sleep(.4)
        J("(()=>{ const c=JSON.parse(JSON.stringify(__solo.cen())); c.ordens['OS-0502'].etapa='Liberadas'; localStorage.setItem('talhao-os-cenario-v1',JSON.stringify(c)); })()")
        clk('Usar 2 sugestões', True, 1.0); p = pan()
        t.chk('AC-SOLO-09 lote com uma linha negada pela R11: a gessagem grava; a calagem mostra "não gravada: OS-0502 já liberada" na própria linha',
              'Não gravadas (1)' in toast() and 'não gravada: OS-0502 já liberada' in p and J("!!AC('lg12|i2|Gesso agrícola')") and not J("!!AC('lg12|i1|Calcário dolomítico filler')"), [toast(), p[-500:]])
        clk('Fechar', True)
        # ---- AG-02 → Ver no plano abre o lote
        ir('AG-02.dc.html#LAU-2063', limpa=True, espera=1.0); clk('Ver no plano', True, 0.3)
        t0 = time.time()   # espera a condição observável (painel das sugestões aberto na SAF), até 12 s; sob carga 2 s fixos não bastavam
        def pan_ok():
            try: return 'Sugestões pelas análises' in (pan() or '')
            except RuntimeError: return False   # página nova ainda sem as funções do teste
        while time.time() - t0 < 12 and not pan_ok(): time.sleep(.25)
        lib(); p = pan()
        t.chk('"Ver no plano" do AG-02 abre o Planejar safra na etapa 2 com as Sugestões pelas análises', 'Sugestões pelas análises · Safra 2026/27' in p, p[:200])
        shot('desktop')
        t.chk('nenhum erro de JS (desktop)', not t.errs(), t.errs())
    if 'celular' in MODOS:
        print('== celular · 390 × 844')
        ir('SAF.dc.html#saf=S2627&passo=cultivos', 390, 844, limpa=True)
        ins('T1-A')
        g = J("(()=>{ const a=TOP(); const r=a.getBoundingClientRect(); const s=a.querySelector('.so-sug'); if(!s) return null; s.scrollIntoView({block:'center'}); const lh=parseFloat(getComputedStyle(s).lineHeight)||19;"
              " const bs=[...s.querySelectorAll('button')].map(b=>Math.round(b.getBoundingClientRect().height)); return [Math.round(r.width), Math.round(s.getBoundingClientRect().height), bs]; })()")
        t.chk('painel de insumos em tela cheia; a linha da sugestão cabe em até 3 linhas e os botões têm 44 px', g and g[0] >= 388 and g[1] <= 3 * 44 + 16 and all(b >= 44 for b in g[2]), g)
        shot('celular_insumos')
        clk('Cancelar', True); clk('Sugestões pelas análises · 4')
        g = J("(()=>{ const a=TOP(); if(!a) return null; const b=[...a.querySelectorAll('.so-pe button')].filter(VIS).map(e=>{ const q=e.getBoundingClientRect(); return [N(e.innerText), q.bottom<=innerHeight+1]; }); return [Math.round(a.getBoundingClientRect().width), b, document.documentElement.scrollWidth<=innerWidth+1]; })()")
        t.chk('lote em tela cheia, com a primária presa no rodapé, e sem rolagem lateral da página', g and g[0] >= 388 and any(x[0].startswith('Usar') and x[1] for x in g[1]) and g[2], g)
        shot('celular_lote')
        t.chk('nenhum erro de JS (celular)', not t.errs(), t.errs())
finally:
    t.fim()

