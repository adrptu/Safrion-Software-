# -*- coding: utf-8 -*-
"""Análise de solo · regressão no navegador da revisão adversarial do SOLO-01 (Codex, HEAD 9c1866c; ESPECIFICACAO §11). Desktop 1440 × 1000.
A1 calagem incluída: com a O.S. dela em A liberar, o laudo novo troca a dose, a O.S. antiga mostra o selo e a Nova ordem não emite segunda calagem;
   com a O.S. liberada, o laudo novo não oferece outra calagem.
A2 rascunho velho do painel (calagem do laudo substituído) salvo depois: recusado, nada gravado.
A3 laudo novo que dispensa a calagem e pede K: o painel do T2 oferece "retirar a Calagem incluída" e "Usar 180 kg/ha" na cobertura retirada.
A5 uso da análise com O.S. em execução: a dose fica travada no painel, com o motivo.
A6 O.S. com o plano mudado: Caio (PCP) vê o impedimento de quem decide e nenhum primário; Ana, com estoque que cobre, libera com a dose da O.S.;
   no Mapa (IN-04, Pivô 12) o ajuste é o link para a O.S.
A7 digitar de novo a dose do uso não o desfaz; salvar sem mudança diz que vale o uso da análise.
A8 AG-02: Caio não vê "Validar laudo".  MY: o lote apaga o ajuste manual da sessão na mesma chave (R14).
Uso: env CHROME_BIN=… flock /tmp/cdpC.lock env CDP_GL=1 timeout 900 python3 solo_rev_test.py. Dados sintéticos."""
import sys, os, time, json
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cadc_lib import T
PR = os.path.join(HERE, '_probe'); os.makedirs(PR, exist_ok=True)
t = T(); J = t.J
LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.TOP=()=>[...document.querySelectorAll('aside[role=dialog]')].filter(VIS).pop()||null;
window.CLK=(t,inPan)=>{ const r=inPan?TOP():document; if(!r) return 'SEM PAINEL'; const els=[...r.querySelectorAll('button,a,summary')].filter(VIS);
  const e=els.find(x=>N(x.innerText)===t)||els.find(x=>N(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok'; };
window.EXP=(local)=>{ const g=local.split('-')[0]; const gr=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>N(x.innerText).startsWith('▸ '+g+' ')); if(!gr) return false; const b=[...gr.querySelectorAll('button')].find(b=>N(b.innerText)==='▸'); if(b){ b.click(); return true; } return false; };
window.INS=(local)=>{ const row=[...document.querySelectorAll('[role=row]')].filter(VIS).find(x=>N(x.innerText).startsWith(local+' ')); if(!row) return 'sem linha '+local;
  (row.querySelector('.g2pw')||row).click(); return 'ok'; };
/* SAF-TAB: a ação de insumos pertence ao detalhe do cultivo, não à célula da listagem. */
window.INSA=(local)=>{ const a=TOP(); const b=a&&[...a.querySelectorAll('button')].filter(VIS).find(b=>['Ajustar insumos e doses de '+local,'Ver insumos e doses de '+local].includes(N(b.innerText))); if(!b) return 'sem ação de insumos '+local; b.click(); return 'ok'; };
window.PAN=()=>{ const a=TOP(); if(!a) return ''; [...a.querySelectorAll('section[aria-label] > button[aria-expanded="false"]')].forEach(b=>b.click()); return N(a.innerText); };
window.BTNS=()=>{ const a=TOP(); return a?[...a.querySelectorAll('button,a')].filter(e=>VIS(e)&&e.getAttribute('aria-disabled')!=='true').map(e=>N(e.innerText)):[]; };   /* acionáveis */
window.OFFS=()=>{ const a=TOP(); return a?[...a.querySelectorAll('button')].filter(e=>VIS(e)&&e.getAttribute('aria-disabled')==='true').map(e=>N(e.innerText)):[]; };   /* sem o papel: indisponíveis com motivo */
window.TOAST=()=>[...document.querySelectorAll('[role=status]')].map(x=>N(x.innerText)).filter(Boolean).join(' | ');
window.ALERT=()=>{ const a=TOP(); return a?[...a.querySelectorAll('[role=alert]')].filter(VIS).map(x=>N(x.innerText)).join(' | '):''; };
window.PRIMS=()=>{ const a=TOP(); return a?[...a.querySelectorAll('button,a')].filter(e=>VIS(e)&&e.getAttribute('aria-disabled')!=='true'&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)').map(e=>N(e.innerText)):[]; };
window.KCLI=()=>{ const a=TOP(); return a&&[...a.querySelectorAll('input')].find(x=>(x.getAttribute('aria-label')||'')==='Dose local de KCl 60%'); };
window.SETKCL=(v)=>{ const i=KCLI(); if(!i) return 'sem campo'; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,v); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; };
window.SETV=(sel,val)=>{ const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; };
window.OPT=(sel,txt)=>{ const s=document.querySelector(sel); if(!s) return 'sem select'; const o=[...s.options].find(o=>o.text.indexOf(txt)>=0); if(!o) return 'sem opção '+txt+' · '+[...s.options].map(o=>o.text).join(' | '); return SETV(sel,o.value); };
window.CENO=()=>JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null');
window.CENW=(f)=>{ const c=CENO(); f(c); localStorage.setItem('talhao-os-cenario-v1',JSON.stringify(c)); return 'ok'; };
window.ATIVOS=()=>Object.values(((CENO()||{}).solo||{}).aceites||{}).filter(a=>a.st==='ativo').map(a=>a.k+'='+a.dose);
'ok'"""
def lib(): J(LIB)
def ir(pg, limpa=False, perfil=None, espera=1.4):
    t.c.size(1440, 1000)
    if limpa or perfil:
        t.goto('Main.dc.html')
        if limpa: J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
        if perfil: J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)})")
    t.goto(pg); time.sleep(espera); lib()
def clk(x, pan=False, w=.6): r = J(f"CLK({json.dumps(x)},{'true' if pan else 'false'})"); time.sleep(w); return r
def ins(local):
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
def cen(expr): return J(f"(()=>{{ const c=CENO(); return ({expr}); }})()")
def dem(): return J("__solo.dem()") or {}
def bruta(d, n): return round((d.get(n) or {}).get('bruta', 0), 2)
def nova(saf, cult, atv, jan):
    clk('Criar ordem'); a = J(f"OPT('#nv_saf',{json.dumps(saf)})"); time.sleep(.3); b = J(f"OPT('#nv_cult',{json.dumps(cult)})"); time.sleep(.3)
    c = J(f"OPT('#nv_atv',{json.dumps(atv)})"); time.sleep(.3); d = J(f"SETV('#nv_jan',{json.dumps(jan)})"); time.sleep(.3); clk('Emitir ordem', True, .9)
    return [a, b, c, d]
def top_id(): return J("(()=>{ const a=TOP(); return a?(a.getAttribute('aria-label')||'').split(' · ')[0]:''; })()")
def laudo_t2(chave, ca='1.00', an=None, coleta='2026-09-21'):
    """o que outra aba (AG-02) grava: registra e valida um laudo mais novo do T2 (gancho de teste do SAF; o comando é o mesmo do AG-02)"""
    an = an or f"[{{a:'Ca',v:'{ca}',un:'cmolc/dm³'}},{{a:'Mg',v:'0.44',un:'cmolc/dm³'}},{{a:'K',v:'136.85',un:'mg/dm³'}},{{a:'H+Al',v:'3.06',un:'cmolc/dm³'}},{{a:'Al',v:'0.30',un:'cmolc/dm³'}}]"
    return J("(()=>{ const a=__solo.registrar({faz:'Santa Rita',tal:'T2',prof:'0–20',coleta:'" + coleta + "',lab:'Agrolab',ext:'Mehlich-1',area:298,an:" + an + "},'" + chave
             + "-R'); if(a.erro) return a.erro; const b=__solo.validar(a.id,'" + chave + "-V'); return b.erro||a.id; })()")
def shot(n): t.c.shot(os.path.join(PR, 'solo_rev_' + n + '.png'))

try:
    # ---- A1 · calagem incluída: O.S. em A liberar recebe a troca; a Nova ordem não emite outra; liberada, o laudo novo não oferece outra
    ir('SAF.dc.html#saf=S2627&passo=cultivos', limpa=True); ins('T2'); clk('Incluir calagem', True); clk('Salvar', True, 1.0)
    ir('OS.dc.html'); nova('Safra 2026/27', 'T2 ·', 'Calagem', '2026-09-30'); nid = top_id()
    t.chk('A1 base: O.S. da Calagem incluída pelo LAU-2063 no T2 em A liberar', cen(f"[c.ordens['{nid}'].etapa, c.ordens['{nid}'].osc.novo.keys]") == ['A liberar', ['c3|solo:LAU-2063:cal']], nid)
    ir('SAF.dc.html#saf=S2627&passo=cultivos'); l1 = laudo_t2('A1')
    ir('SAF.dc.html#saf=S2627&passo=cultivos')
    s = J("__solo.sugs().filter(s=>s.cid==='c3'&&s.tipo==='incluir').map(s=>[s.k,s.sug,s.ef,s.nega])") or []
    r = J("(()=>{ const s=__solo.sugs().filter(s=>s.cid==='c3'&&s.tipo==='incluir').map(x=>Object.assign({},x,{local:'T2'})); const r=__solo.aceitarLote(s,'LOTE-A1'); return r.erro||r.msg; })()")
    t.chk('A1 laudo novo do T2 (' + str(l1) + ') com a O.S. em A liberar: o lote oferece Calagem 1,32 t/ha (era 1,20) e grava; uma só calagem ativa',
          s == [['c3|solo:LAU-2073:cal|Calcário dolomítico', 1.32, 1.2, '']] and 'sugestão usada' in str(r) and J("ATIVOS()") == ['c3|solo:LAU-2073:cal|Calcário dolomítico=1.32'], [s, r, J("ATIVOS()")])
    ir('OS.dc.html#' + nid); p = pan()
    t.chk('A1 a O.S. da calagem antiga mostra "Plano mudou pela análise · 1,32 t/ha (O.S. 1,2)" e o ajuste abre com 1,32', 'Plano mudou pela análise · 1,32 t/ha (O.S. 1,2)' in p and J("PRIMS()") == ['Ajustar antes de liberar'], [J("PRIMS()"), p[:400]])
    clk('Ajustar antes de liberar', True); d0 = J("(document.getElementById('aj_d0')||{}).value"); clk('Salvar ajuste', True, 1.0)
    o = cen(f"[c.ordens['{nid}'].etapa, c.ordens['{nid}'].ins[0].dose, c.ordens['{nid}'].ins[0].tot]")
    t.chk('A1 "Salvar ajuste" grava a dose do laudo novo na mesma O.S. (1,32 t/ha × 298 ha = 393,36 t) e o selo some', d0 == '1,32' and o == ['A liberar', 1.32, 393.36] and 'Plano mudou' not in pan(), [d0, o, toast()])
    nova('Safra 2026/27', 'T2 ·', 'Calagem', '2026-09-30'); p = pan()
    n = cen("Object.values(c.ordens).filter(o=>o.talhao==='T2'&&/Calagem/.test(o.tipo||'')&&o.etapa!=='Canceladas').length")
    t.chk('A1 Nova ordem da Calagem do LAU-2073 no T2: recusada ("Já existe … para a calagem deste cultivo … ajuste a dose nela"); uma só O.S. de calagem',
          f'Já existe {nid} para a calagem deste cultivo (incluída pelo LAU-2063): ajuste a dose nela.' in p and n == 1, [n, p[:500]])
    clk('Cancelar', True); clk('Descartar', True)
    J(f"CENW(c=>{{ c.ordens['{nid}'].etapa='Liberadas'; }})"); ir('SAF.dc.html#saf=S2627&passo=cultivos'); l2 = laudo_t2('A1b', ca='0.80', coleta='2026-09-22')
    ir('SAF.dc.html#saf=S2627&passo=cultivos'); s = J("__solo.sugs().filter(s=>s.cid==='c3'&&(s.tipo==='incluir'||s.incl0)).length")
    ir('AG-02.dc.html#' + str(l2), espera=1.0); p = pan()
    t.chk('A1 com a O.S. da calagem liberada, o laudo mais novo (' + str(l2) + ') não oferece outra calagem; o AG-02 diz por quê',
          s == 0 and f'não aplicável: {nid} já liberada (calagem do LAU-2063)' in p, [s, p[p.find('USO NO PLANO'):][:400]])
    shot('a1')
    # ---- A2 · rascunho velho salvo depois de outra aba mudar a análise
    ir('SAF.dc.html#saf=S2627&passo=cultivos', limpa=True); ins('T2'); clk('Incluir calagem', True, .6)
    l1 = laudo_t2("A2"); time.sleep(.8)
    r = J("(()=>{ const s=__solo.sugs('S2627').filter(s=>s.atv.id.indexOf('LAU-2073')>=0).map(x=>Object.assign({},x,{local:'T2'})); const r=__solo.aceitarLote(s,'OUTRA-LOTE','Ana'); return r.erro||r.msg; })()")
    time.sleep(.6); clk('Salvar', True, 1.0); a = J("ALERT()") or ''
    t.chk('A2 a aba com o rascunho velho (Incluir calagem do LAU-2063) salva depois da outra: recusado ("a análise mudou: LAU-2063 substituído pelo LAU-2073 … Reabra o painel"), nada gravado',
          'a análise mudou: LAU-2063 substituído pelo LAU-2073' in a and 'Reabra o painel' in a and J("ATIVOS()") == ['c3|solo:LAU-2073:cal|Calcário dolomítico=1.32'], [r, a, J("ATIVOS()")])
    # ---- A3 · laudo novo que dispensa a calagem e pede K
    ir('SAF.dc.html#saf=S2627&passo=cultivos', limpa=True); k0 = bruta(dem(), 'KCl 60%')
    ins('T2'); clk('Incluir calagem', True); clk('Retirar pela análise', True); clk('Salvar', True, 1.0)
    l3 = laudo_t2('A3', an="[{a:'Ca',v:'4.00',un:'cmolc/dm³'},{a:'Mg',v:'1.50',un:'cmolc/dm³'},{a:'K',v:'30',un:'mg/dm³'},{a:'H+Al',v:'2.40',un:'cmolc/dm³'},{a:'Al',v:'0',un:'cmolc/dm³'}]")
    ir('SAF.dc.html#saf=S2627&passo=cultivos'); s = J("__solo.sugs().filter(s=>s.cid==='c3').map(s=>[s.tipo,!!s.incl0,s.prod,s.sug])") or []
    t.chk('A3 com o laudo novo do T2 (V 69,91 %, K 30): o lote tem "retirar a inclusão" da Calagem e KCl 180 kg/ha', s == [['retirar', True, 'Calcário dolomítico', 0], ['dose', False, 'KCl 60%', 180]], s)
    ins('T2'); p = pan()
    t.chk('A3 painel do T2: "Análise sugere retirar a Calagem incluída (V já atinge 60 %) · −357,6 t" e "Análise sugere 180 kg/ha · +53.640 kg no talhão" sob o KCl retirado',
          'Análise sugere retirar a Calagem incluída (V já atinge 60 %) · −357,6 t' in p and 'Análise sugere 180 kg/ha · +53.640 kg no talhão' in p, p[:900])
    clk('Retirar pela análise', True); clk('Usar 180 kg/ha', True); clk('Salvar', True, 1.0)
    st = cen("[c.solo.aceites['c3|solo:LAU-2063:cal|Calcário dolomítico'].st, (c.solo.aceites['c3|a4|KCl 60%']||{}).dose]"); d = dem()
    t.chk('A3 salvar: a calagem sai ("retirada pelo ' + str(l3) + '"), o T2 volta a ter KCl 180 pela análise; demanda: calcário 0 e KCl +17.880 kg sobre o padrão',
          st == ['retirada pelo ' + str(l3), 180] and bruta(d, 'Calcário dolomítico') == 0 and round(bruta(d, 'KCl 60%') - k0, 2) == 17880, [st, bruta(d, 'Calcário dolomítico'), bruta(d, 'KCl 60%') - k0, toast()])
    shot('a3')
    # ---- A5 · uso da análise com O.S. em execução fica travado no painel
    ir('SAF.dc.html#saf=S2627&passo=cultivos', limpa=True); ins('T1-A'); clk('Usar 150 kg/ha', True); clk('Salvar', True, 1.0)
    ir('OS.dc.html'); nova('Safra 2026/27', 'T1-A', 'Adubação de cobertura', '2026-11-04'); nid = top_id(); J(f"CENW(c=>{{ c.ordens['{nid}'].etapa='Em execução'; }})")
    ir('SAF.dc.html#saf=S2627&passo=cultivos'); ins('T1-A'); p = pan(); i = J("(()=>{ const i=KCLI(); return i?[i.readOnly,i.value]:null; })()"); b = J("BTNS()") or []
    t.chk('A5 com a ' + nid + ' em execução: KCl 150 travado ("pela análise · LAU-2061 · ' + nid + ' em execução: vale a dose da O.S."), sem Restaurar dose',
          i == [True, '150'] and f'pela análise · LAU-2061 · {nid} em execução: vale a dose da O.S.' in p and 'Restaurar dose' not in b, [i, b[:12], p[p.find('KCl'):][:200]])
    # ---- A6 · plano mudado: Caio vê quem decide; Ana com estoque que cobre libera com a dose da O.S.
    ir('SAF.dc.html#saf=LG2627&passo=cultivos', limpa=True); ins('Pivô 12'); clk('Usar 1.800 kg/ha', True); clk('Salvar', True, 1.0)
    J("sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Lagoa Grande',lay:'Integrado',tsel:['PV12'],flt:{},zoom:1,osel:{},px:null}))"); ir('IN-04.dc.html', espera=1.6)
    J("(()=>{ const b=[...document.querySelectorAll('aside[aria-label] button')].find(b=>N(b.innerText)==='Ver ordens'); if(b) b.click(); })()"); time.sleep(1.0)
    mp = J("[[...document.querySelectorAll('a')].filter(a=>VIS(a)&&N(a.innerText)==='Ajustar antes de liberar').map(a=>a.getAttribute('href')), [...document.querySelectorAll('button')].filter(b=>VIS(b)&&N(b.innerText)==='Ajustar antes de liberar').length]")
    t.chk('A6 Mapa (Pivô 12): o passo "Ajustar antes de liberar" da OS-0502 é o link que abre o ajuste na O.S., sem botão que só muda o estado do Mapa', mp and mp[0] == ['OS.dc.html#OS-0502:ajustar'] and mp[1] == 0, mp)
    ir('OS.dc.html#OS-0502', perfil='Caio'); p = pan(); pr = J("PRIMS()")
    t.chk('A6 Caio (PCP) na OS-0502 com o plano mudado: nenhum primário, o texto do plano mudado e o bloqueio de estoque com quem resolve (Suprimentos)',
          pr == [] and 'O plano mudou pela análise (LAU-2071)' in p and 'Liberar bloqueado: saldo insuficiente' in p and 'Quem resolve: Suprimentos' in p and 'Ajustar antes de liberar' not in (J("BTNS()") or []), [pr, p[p.find('PRÓXIMO'):][:400]])
    J("CENW(c=>{ c.lotes['Calcário dolomítico filler|LG26-03'].fisico=110000; })"); ir('OS.dc.html#OS-0502', perfil='Caio'); p = pan()
    t.chk('A6 Caio com o estoque coberto: o impedimento passa a ser de papel ("decisão de Ana …"), sem primário acionável; "Liberar para execução" indisponível com o motivo', J("PRIMS()") == [] and 'Liberar para execução: decisão de Ana' in p and 'Liberar para execução' in (J("OFFS()") or []) and 'troque no avatar do menu' in p, [J("PRIMS()"), J("OFFS()"), p[p.find('PRÓXIMO'):][:300]])
    ir('OS.dc.html#OS-0502', perfil='Ana'); p = pan()
    t.chk('A6 Ana com o estoque coberto: primário "Ajustar antes de liberar", secundário "Liberar com 2.000 kg/ha" e nenhum bloqueio',
          J("PRIMS()") == ['Ajustar antes de liberar'] and 'Liberar com 2.000 kg/ha' in p and 'Liberar bloqueado' not in p, [J("PRIMS()"), p[p.find('PRÓXIMO'):][:300]])
    clk('Liberar com 2.000 kg/ha', True); clk('Confirmar liberação', True, 1.0)
    ev = cen("((c.ordens['OS-0502'].osc||{}).ev||[]).map(e=>e.cmd+'|'+e.t)") or []
    t.chk('A6 "Liberar com 2.000 kg/ha" libera de fato (R20): CMD-42 grava 2.000 kg/ha e CMD-06', cen("c.ordens['OS-0502'].etapa") == 'Liberadas' and len(ev) == 2 and '2.000 kg/ha' in ev[0] and 'CMD-06' in ev[1], [ev, toast()])
    # ---- A7 · redigitar a dose do uso
    ir('SAF.dc.html#saf=S2627&passo=cultivos', limpa=True); k0 = bruta(dem(), 'KCl 60%'); ins('T1-A'); clk('Usar 150 kg/ha', True); clk('Salvar', True, 1.0)
    ins('T1-A'); J("SETKCL('15')"); time.sleep(.3); J("SETKCL('150')"); time.sleep(.3); clk('Salvar', True, 1.0); tt = toast()
    t.chk('A7 digitar 15 e depois 150 (a mesma dose do uso) e salvar: o uso continua ativo, sem "uso desfeito", e a demanda segue +4.800 kg',
          cen("c.solo.aceites['c1|a4|KCl 60%'].st") == 'ativo' and 'desfeito' not in tt and round(bruta(dem(), 'KCl 60%') - k0, 2) == 4800, [tt, cen("c.solo.aceites['c1|a4|KCl 60%'].st")])
    ins('T1-A'); clk('Salvar', True, 1.0); tt = toast()
    t.chk('A7 (S4) salvar sem mudança com o uso ativo: "Sem mudanças em T1-A: valem o plano padrão e 1 uso da análise."', 'Sem mudanças em T1-A: valem o plano padrão e 1 uso da análise.' in tt and 'vale o plano padrão' not in tt, tt)
    # ---- MY · o lote apaga o ajuste manual da sessão na mesma chave (R14)
    ir('SAF.dc.html#saf=S2627&passo=cultivos', limpa=True); k0 = bruta(dem(), 'KCl 60%'); ins('T1-A'); J("SETKCL('140')"); time.sleep(.3); clk('Salvar', True, 1.0); k1 = bruta(dem(), 'KCl 60%')
    clk('Sugestões pelas análises'); J("(()=>{ const a=TOP(); const r=[...a.querySelectorAll('[role=row]')].find(r=>/^T1-A /.test(N(r.innerText))); const i=r&&r.querySelector('input[type=checkbox]'); if(i&&!i.checked) i.click(); })()"); time.sleep(.4)
    clk('Usar 1 sugestão', True, 1.0); k2 = bruta(dem(), 'KCl 60%'); ins('T1-A'); p = pan()
    t.chk('MY lote com o T1-A em ajuste manual (140): usar a sugestão apaga o ajuste da sessão e vale 150 pela análise (demanda +3.200 → +4.800 kg)',
          round(k1 - k0, 2) == 3200 and round(k2 - k0, 2) == 4800 and 'pela análise · LAU-2061' in p and J("KCLI().value") == '150', [k1 - k0, k2 - k0, p[p.find('KCl'):][:160]])
    clk('Cancelar', True)
    # ---- A8 · AG-02: Caio não vê "Validar laudo"
    ir('AG-02.dc.html#LAU-2050', limpa=True, perfil='Caio', espera=1.0); p = pan(); b = J("BTNS()") or []
    t.chk('A8 AG-02 com o Caio: LAU-2050 aguardando validação sem "Validar laudo" e com "Decisão de Ana (agrônoma): só o agrônomo valida"', 'Validar laudo' not in b and 'Decisão de Ana (agrônoma): só o agrônomo valida' in p, [b, p[:300]])
    ir('AG-02.dc.html#LAU-2050', perfil='Ana', espera=1.0)
    t.chk('A8 com a Ana o primário "Validar laudo" continua', J("PRIMS()") == ['Validar laudo'], J("PRIMS()"))
    t.chk('nenhum erro de JS', not t.errs(), t.errs())
finally:
    t.fim()

