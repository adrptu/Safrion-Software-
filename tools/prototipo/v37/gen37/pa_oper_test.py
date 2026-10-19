# -*- coding: utf-8 -*-
"""PA-OPER F1 · planos por operação no navegador (docs/integracao/V71/PA-OPER.md, aceites da F1), no Chrome headless:
  P1  SOJA-AT: faixa "Visão geral" + operações na ordem do ciclo (Pulverização, TS, Plantio, Adubação, Colheita), contagens 4/1/1/1/1,
      estado em texto visível em cada uma; alvo em branco não deixa a Pulverização "Pendente" (alvo opcional, proprietário 19/10)
  P2  tocar Pulverização: só as 4 atividades, os parâmetros da operação; #plano=SOJA-AT&op=pulverizacao; F5 reabre a operação;
      Esc com o editor aberto fecha só o editor; o 2º Esc volta à visão geral; o 3º, à biblioteca
  P3  Fungicida 2ª com calda própria de 150 e a calda da operação 100 → 120: as 3 herdeiras mostram 120 "da operação", a 2ª mantém 150;
      o aviso diz "Pulverização · volume de calda 100 → 120 L/ha em 3 atividades"
  P7  bula na versão: Fungicida 1ª com alvo ferrugem-asiática na DAP 100 (colheita na 118, carência de 30 dias) → ⛔ e "Salvar e publicar"
      desabilitado com o motivo; na DAP 85 volta
  P17 rascunho inválido persiste: o ⛔ e a dose voltam depois do F5; a v6 segue em vigor
  P12 sem ciclo de revisão (proprietário 19/10: "leve e fluido"): Caio (PCP) edita e o rascunho fica guardado, sem botão de submeter;
      Ana abre e publica ("Publicada v7 · por Ana"), sem "Devolver"; sem v8 no 2º clique
  P13 O.S. nova do cultivo T1-A emitida da v6 leva a calda do plano (100 L/ha) na instrução; publicada a v7 com 120 L/ha, a O.S. em
      A liberar mostra "Plano v7 difere: volume de calda" e não muda sozinha; a OS-0421 (em execução) segue com 100 L/ha e 6 cargas
  P19 tanque do PJ editado no cadastro (2.500 L): a OS-0421 emitida segue com 6 cargas de 3.000 L; a O.S. emitida depois leva 2.500 L
  K2/K3/K5/K7 cliques: calda das 4 pulverizações (≤ 4 + 1 campo), calda própria numa atividade (≤ 4 + 1 campo), percorrer as 5 operações (≤ 6),
      deslocar +5 dias os gatilhos das 4 pulverizações e publicar (≤ 6 + 1 campo)
  P15e/P15f os 8 planos abrem seccionados; calda nova "Pendente" sem valor de código; P19b rascunho antigo sem calda abre "Pendente"
  P16 390 px: sem rolagem lateral na operação em foco; alvos da faixa ≥ 44 px de altura útil; sem erro de JavaScript
Uso (de gen37/): python3 -B pa_oper_test.py            (RENDER_DIR=<outro _render> roda contra outro build; sai 1 se falhar)
                 ANTES=<_render da base> python3 -B pa_oper_test.py   (contraprova: os mesmos casos na base)
Emulação no Chrome headless; não é aparelho físico."""
import sys, os, time, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from contextlib import contextmanager
R = os.environ.get('ANTES') or os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
PROBE = os.path.join(HERE, '_probe'); os.makedirs(PROBE, exist_ok=True)
OK = []; FAIL = []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'), nome, ('' if cond else str(info)[:1200]), flush=True)
@contextmanager
def secao(nome):
    try: yield
    except Exception as ex: chk(nome + ' · o roteiro não chegou ao fim do trecho', False, repr(ex)[:300])
p, srv = servir(R); c = None; ERRL = []
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
def J(x): return c.js(x)
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def errs(): return [e for e in (J("window.__errs||[]") or []) if "reading 'g2toast'" not in e]
def espera(cond, limite=6.0, passo=.15):
    fim = time.time() + limite
    while time.time() < fim:
        try:
            if J(cond): return True
        except Exception: pass
        time.sleep(passo)
    return False
def abre(url, w=1440, h=900, e=1, t=False, limpa=True, perfil=None, espera_s=.8):
    if c.alvo: ERRL.extend(errs())
    c.aparelho(w, h, e, t); base = f'http://127.0.0.1:{p}/'
    if limpa: c.goto(base + 'Main.dc.html', .2); J("localStorage.clear(); sessionStorage.clear()")
    if perfil: J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)})")
    c.goto(base + url, espera_s)
def recarrega():
    c.call('Page.reload', {'ignoreCache': False}); time.sleep(.6)
    for _ in range(60):
        try:
            if J("document.readyState")=='complete' and J("!!document.body && document.body.innerText.length>50"): break
        except Exception: pass
        time.sleep(.2)
    time.sleep(.7)
CLIQUES = [0]
def centro(sel, limite=2.0):
    fim = time.time() + limite
    while True:
        r = J(f"(()=>{{const e={sel}; if(!e) return null; e.scrollIntoView({{block:'center',inline:'nearest'}}); const r=e.getBoundingClientRect(); const x=r.left+r.width/2, y=r.top+r.height/2; const t=document.elementFromPoint(x,y); return [x,y,!!t&&(e===t||e.contains(t))];}})()")
        if not r or r[2] or time.time() >= fim: return r[:2] if r else None
        time.sleep(.15)
def clique(sel, toque=False, w=.45):
    xy = centro(sel)
    if not xy: return 'NÃO ACHEI: ' + sel[:90]
    CLIQUES[0] += 1
    if toque: c.toque(*xy)
    else: c.mouse(*xy); c.mouse(*xy, 'mousePressed', 'left'); c.mouse(*xy, 'mouseReleased', 'left')
    time.sleep(w); return 'ok'
def btnc(txt): return f"[...document.querySelectorAll('button,a')].find(b=>b.getClientRects().length&&{N}(b.innerText).startsWith({json.dumps(txt)}))"
def lab(txt): return f"[...document.querySelectorAll('button')].find(b=>b.getClientRects().length&&(b.getAttribute('aria-label')||'').startsWith({json.dumps(txt)}))"
def chip(txt): return f"[...document.querySelectorAll('button.pa-opf')].find(b=>b.getClientRects().length&&{N}(b.innerText).startsWith({json.dumps(txt)}))"
def digita(txt): c.call('Input.insertText', {'text': txt}); time.sleep(.15)
def enter(): c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.45)
def esc(): c.tecla('Escape', 'Escape', 27); time.sleep(.35)
def seleciona_tudo(): J("document.activeElement&&document.activeElement.select&&document.activeElement.select()")
CHIPS = f"[...document.querySelectorAll('button.pa-opf')].filter(b=>b.getClientRects().length).map(b=>{N}(b.innerText))"
ATVS = f"[...document.querySelectorAll('main .pa-atividade')].filter(b=>b.getClientRects().length).map(a=>{N}((a.querySelector('.pa-titulo')||{{}}).innerText))"
INFO = lambda nome: f"(()=>{{const a=[...document.querySelectorAll('main .pa-atividade')].find(x=>x.getClientRects().length&&{N}((x.querySelector('.pa-titulo')||{{}}).innerText)==={json.dumps(nome)}); const i=a&&a.querySelector('.pa-op-info'); return i?{N}(i.innerText):'';}})()"
PRIM = "(()=>{const b=document.querySelector('[data-acoes] [data-acao=comando]'); const n=document.querySelector('[data-acoes] .acoes-nota'); return {t:b?b.innerText.replace(/\\s+/g,' ').trim():'',dis:!!(b&&b.disabled),nota:n?n.innerText.replace(/\\s+/g,' ').trim():''};})()"
SELO = "(()=>{const h=document.querySelector('#pa-det-tit'); const s=h&&h.nextElementSibling; return s?s.innerText.replace(/\\s+/g,' ').trim():'';})()"
def editar_atividade(nome):
    """⋯ da atividade → Editar atividade (painel lateral)"""
    clique(f"(()=>{{const a=[...document.querySelectorAll('main .pa-atividade')].find(x=>x.getClientRects().length&&{N}((x.querySelector('.pa-titulo')||{{}}).innerText)==={json.dumps(nome)}); return a&&a.querySelector('.pa-mais');}})()", w=.35)
    clique(btnc('Editar atividade'), w=.5)
def campo_painel(fid, val, select=False):
    if select:
        J(f"(()=>{{const s=document.getElementById({json.dumps(fid)}); const pr=Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value'); pr.set.call(s,{json.dumps(val)}); s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"); time.sleep(.25)
    else:
        clique(f"document.getElementById({json.dumps(fid)})", w=.15); seleciona_tudo(); digita(val); time.sleep(.2)
def salvar_painel(): clique("[...document.querySelectorAll('aside[role=dialog] .pe-form button')].pop()", w=.6)
try:
    c = Chrome()
    # ---------------- P1 · faixa na ordem do ciclo, com estado ----------------
    with secao('P1'):
        abre('PA.dc.html#plano=SOJA-AT'); espera("document.querySelectorAll('button.pa-opf').length>1", 5)
        ch = J(CHIPS)
        chk('P1 faixa: Visão geral + Pulverização 4, Tratamento de sementes 1, Plantio 1, Adubação a lanço 1, Colheita de grãos 1 (ordem do ciclo), estado em texto',
            [re.sub(r' · .*', '', x) for x in ch] == ['Visão geral 8', 'Pulverização 4', 'Tratamento de sementes 1', 'Plantio 1', 'Adubação a lanço 1', 'Colheita de grãos 1']
            and all(re.search(r'· (✓ Pronta|• Pendente|⚠ Com aviso|⛔ Impedida)$', x) for x in ch[1:]) and 'Pulverização 4 · ⚠ Com aviso' in ch, ch)
    # ---------------- P2 · foco, endereço, F5 e Esc ----------------
    with secao('P2'):
        clique(chip('Pulverização'), w=.5); h = J("location.hash"); at = J(ATVS)
        foco = J(f"{N}((document.querySelector('.pa-op-foco')||{{}}).innerText||'')")
        chk('P2a Pulverização em foco: 4 atividades, "Parâmetros de Pulverização" com o volume de calda; #plano=SOJA-AT&op=pulverizacao',
            h == '#plano=SOJA-AT&op=pulverizacao' and at == ['Dessecação pré-plantio', 'Herbicida pós-emergente', 'Fungicida 1ª aplicação', 'Fungicida 2ª aplicação + inseticida']
            and 'Parâmetros de Pulverização' in foco and '100 L/ha' in foco, [h, at, foco[:200]])
        recarrega(); espera("!!document.querySelector('.pa-op-foco')", 5)
        chk('P2b F5 reabre o mesmo plano com Pulverização em foco', J("location.hash") == '#plano=SOJA-AT&op=pulverizacao' and len(J(ATVS)) == 4, [J("location.hash"), J(ATVS)])
        clique(lab('Alterar o volume de calda da operação'), w=.3); aberto = J("document.activeElement&&document.activeElement.id")
        esc(); f1 = [J("!!document.getElementById('pa-calda-op')"), len(J(ATVS)), J("location.hash")]
        esc(); f2 = [len(J(ATVS)), J("location.hash")]
        esc(); f3 = [J("document.querySelectorAll('main .g2card').length"), J("location.hash")]
        chk('P2c Esc: 1º fecha só o editor da calda; 2º volta à visão geral; 3º volta à biblioteca',
            aberto == 'pa-calda-op' and f1 == [False, 4, '#plano=SOJA-AT&op=pulverizacao'] and f2 == [8, '#plano=SOJA-AT'] and f3[0] == 8 and f3[1] == '', [aberto, f1, f2, f3])
    # ---------------- P3 · dois níveis ----------------
    with secao('P3'):
        abre('PA.dc.html#plano=SOJA-AT&op=pulverizacao'); espera("!!document.querySelector('.pa-op-foco')", 5)
        clique(lab('Alterar a calda de Fungicida 2ª aplicação + inseticida'), w=.3); seleciona_tudo(); digita('150'); enter()
        clique(lab('Alterar o volume de calda da operação'), w=.3); seleciona_tudo(); digita('120'); enter(); t3 = toast()
        infos = {n: J(INFO(n)) for n in ['Dessecação pré-plantio', 'Herbicida pós-emergente', 'Fungicida 1ª aplicação', 'Fungicida 2ª aplicação + inseticida']}
        chk('P3 calda da operação 100 → 120 com a Fungicida 2ª em 150 própria: 3 herdeiras em 120 "da operação", a 2ª em 150; aviso com o texto do P3',
            'Pulverização · volume de calda 100 → 120 L/ha em 3 atividades' in t3 and all('Calda 120 L/ha da operação' in infos[n] for n in ['Dessecação pré-plantio', 'Herbicida pós-emergente', 'Fungicida 1ª aplicação'])
            and 'Calda 150 L/ha própria' in infos['Fungicida 2ª aplicação + inseticida'] and re.search(r'Rascunho v7( guardado \d\d:\d\d)? · v6 em vigor', J(SELO)), [t3, infos, J(SELO)])
    # ---------------- P7 e P17 · bula na versão; rascunho inválido persiste ----------------
    with secao('P7'):
        abre('PA.dc.html#plano=SOJA-AT&op=pulverizacao'); espera("!!document.querySelector('.pa-op-foco')", 5)
        editar_atividade('Fungicida 1ª aplicação'); campo_painel('fm_alvo', 'ferrugem-asiática', select=True); campo_painel('fm_dias', '100'); salvar_painel()
        pr = J(PRIM); conf = J(f"{N}((document.querySelector('.pa-op-foco')||{{}}).innerText||'')")
        chk('P7a alvo ferrugem-asiática na DAP 100 (colheita na 118, carência de 30 dias): ⛔ "carência termina 12 dias depois da colheita prevista"; "Salvar e publicar v7" desabilitado com o motivo',
            pr['dis'] and 'carência termina 12 dias depois da colheita prevista' in pr['nota'] and pr['t'] == 'Salvar e publicar v7' and 'carência termina 12 dias' in conf and 'Pulverização 4 · ⛔ Impedida' in J(CHIPS), [pr, conf[:300], J(CHIPS)])
        recarrega(); espera("!!document.querySelector('.pa-op-foco')", 5); pr2 = J(PRIM)
        chk('P17 F5: o rascunho reabre com o mesmo ⛔ e a v6 segue em vigor (guardar não publica)', pr2['dis'] and 'carência termina 12 dias' in pr2['nota'] and re.search(r'Rascunho v7( guardado \d\d:\d\d)? · v6 em vigor', J(SELO)), [pr2, J(SELO)])
        editar_atividade('Fungicida 1ª aplicação'); campo_painel('fm_dias', '85'); salvar_painel(); pr3 = J(PRIM)
        chk('P7b na DAP 85 a carência cabe: "Salvar e publicar v7" volta', not pr3['dis'] and pr3['t'] == 'Salvar e publicar v7', pr3)
    # ---------------- P12 · publicação sem ciclo de revisão; P13 · O.S. × versão ----------------
    with secao('P12'):
        abre('PA.dc.html#plano=SOJA-AT&op=pulverizacao', perfil='Caio'); espera("!!document.querySelector('.pa-op-foco')", 5)
        clique(lab('Alterar o volume de calda da operação'), w=.3); seleciona_tudo(); digita('120'); enter()
        pc = J(PRIM); s1 = J(SELO); sub = J("[...document.querySelectorAll('button,a')].some(b=>b.getClientRects().length&&/Submeter|revisão/i.test(b.innerText))")
        chk('P12a Caio (sem o papel de agrônomo): sem primária e sem "Submeter"; nota "Rascunho v7 guardado. O agrônomo publica ao abrir o plano."; a v6 segue em vigor',
            pc['t'] == '' and pc['nota'] == 'Rascunho v7 guardado. O agrônomo publica ao abrir o plano.' and not sub and re.search(r'Rascunho v7( guardado \d\d:\d\d)? · v6 em vigor', s1), [pc, s1, sub])
        J("localStorage.setItem('safrion.perfilDemo','Ana')"); recarrega(); espera("!!document.querySelector('.pa-op-foco')", 5)
        pa = J(PRIM); dev = J("[...document.querySelectorAll('button,a')].some(b=>b.getClientRects().length&&b.textContent.includes('Devolver'))")
        clique("document.querySelector('[data-acoes] [data-acao=comando]')", w=.7); t12 = toast(); s2 = J(SELO); pa2 = J(PRIM)
        chk('P12b Ana: "Salvar e publicar v7", sem "Devolver"; publica: "Publicada v7 · por Ana"; sem primária depois (o 2º clique não cria v8)',
            pa['t'] == 'Salvar e publicar v7' and not pa['dis'] and not dev and t12.startswith('Publicada v7 · por Ana') and s2.startswith('Publicada v7 · por Ana') and pa2['t'] == '', [pa, dev, t12, s2, pa2])
        cen = J("(()=>{const c=JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>/cenario-v1$/.test(k)))||'{}'); const p=(c.pa||{})['SOJA-AT']||{}; return {versao:p.versao,vs:Object.keys(p.versoes||{}),cal:(((p.versoes||{})[7]||{}).params||{})['Pulverização']};})()")
        chk('P12c a v7 publicada vai para o cenário compartilhado (imutável, com os parâmetros da operação)', cen.get('versao') == 7 and cen.get('vs') == ['7'] and (cen.get('cal') or {}).get('calda') == 120, cen)
    with secao('P13'):
        CEN = "JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>/cenario-v1$/.test(k)))||'{}')"
        def escolhe(fid, trecho):
            r = J(f"""(()=>{{const s=document.getElementById({json.dumps(fid)}); if(!s) return 'sem campo'; const o=[...s.options].find(x=>x.text.includes({json.dumps(trecho)})); if(!o) return 'sem opção: '+[...s.options].map(x=>x.text).join(' | ');
              const pr=Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value'); pr.set.call(s,o.value); s.dispatchEvent(new Event('change',{{bubbles:true}})); return 'ok';}})()"""); time.sleep(.35); return r
        def abre_os(oid):
            """abre o painel da O.S. pela linha (ou cartão) da lista e expande as seções recolhidas"""
            J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed,.g2card,[data-os]')].find(r=>r.getClientRects().length&&((r.innerText.match(/\\bO[SB]-\\d+/)||[''])[0])==={json.dumps(oid)}); r&&r.click();}})()"); time.sleep(.6)
            J("[...document.querySelectorAll('aside[role=dialog] section[aria-label] > button[aria-expanded=\"false\"]')].forEach(b=>b.click())"); time.sleep(.4)
        def emite(atv, cult='T1-A'):
            clique(btnc('Criar ordem'), w=.6); r = [escolhe('nv_saf', 'Safra 2026/27'), escolhe('nv_cult', cult), escolhe('nv_atv', atv)]
            J("(()=>{const s=document.getElementById('nv_jan'); const pr=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value'); pr.set.call(s,'2026-11-20'); s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
            clique(btnc('Emitir ordem'), w=.8); r.append(J("[...document.querySelectorAll('[role=alert]')].map(x=>x.innerText).join(' | ')")); return r
        abre('OS.dc.html', limpa=True); time.sleep(.6)
        r1 = emite('Herbicida pós-emergente')
        o1 = J(f"(()=>{{const c={CEN}; const os=Object.values(c.ordens||{{}}).filter(o=>o.instrucao&&o.instrucao.plano==='SOJA-AT'&&o.etapa==='A liberar'); return os.map(o=>({{id:o.id,i:o.instrucao}}));}})()")
        ok1 = len(o1) == 1 and o1[0]['i'].get('vazao') == 100 and o1[0]['i'].get('planoVer') == 6 and o1[0]['i'].get('tanque') == 3000
        chk('P13a O.S. nova de T1-A (cultivo na v6), Herbicida pós-emergente: a instrução vem do plano v6 (100 L/ha, da operação) com o retrato do tanque (3.000 L)', ok1, [r1, o1])
        # P19: o tanque do PJ editado no cadastro (2.500 L) vale para a O.S. emitida depois; a OS-0421 segue com o retrato de 3.000 L
        J("(()=>{const k=Object.keys(localStorage).find(k=>/cenario-v1$/.test(k)).replace('cenario','cadastros'); const o=JSON.parse(localStorage.getItem(k)||'{}'); o.ativos=[{id:'a05',nome:'Pulverizador PJ-3030 36 m',classe:'Pulverizador',tanque:2500}]; localStorage.setItem(k,JSON.stringify(o));})()")
        recarrega(); r2 = emite('Herbicida pós-emergente', 'T1-B')
        o2 = J(f"(()=>{{const c={CEN}; return Object.values(c.ordens||{{}}).filter(o=>o.instrucao&&o.instrucao.plano==='SOJA-AT'&&o.etapa==='A liberar').map(o=>({{id:o.id,tq:o.instrucao.tanque,vz:o.instrucao.vazao}}));}})()")
        abre_os('OS-0421'); prep = J(f"{N}((document.querySelector('aside[role=dialog]')||document.body).innerText)")
        chk('P19 tanque do PJ mudado no cadastro para 2.500 L: a O.S. emitida depois leva 2.500 L; a OS-0421 (emitida antes) segue com 3.000 L e 6 cargas',
            any(x['tq'] == 2500 for x in o2) and any(x['tq'] == 3000 for x in o2) and '3.000 L · 100 L/ha · 30 ha por carga · 6 cargas' in prep, [r2, o2, re.findall(r'[\d.]+ L · [\d,]+ L/ha[^·]*·[^·]*·[^·]*', prep)[:3]])
        # P13b: publicada a v7 com 120 L/ha, a O.S. em A liberar mostra a diferença e não muda sozinha
        abre('PA.dc.html#plano=SOJA-AT&op=pulverizacao', limpa=False, perfil='Ana'); espera("!!document.querySelector('.pa-op-foco')", 5)
        clique(lab('Alterar o volume de calda da operação'), w=.3); seleciona_tudo(); digita('120'); enter()
        clique("document.querySelector('[data-acoes] [data-acao=comando]')", w=.7); t13 = toast()
        abre('OS.dc.html', limpa=False); time.sleep(.6); oid = o1[0]['id'] if o1 else 'OS-0440'
        abre_os(oid)
        nota = J("[...document.querySelectorAll('[role=note]')].map(x=>x.innerText.replace(/\\s+/g,' ').trim()).join(' | ')")
        o3 = J(f"(()=>{{const c={CEN}; const o=(c.ordens||{{}})[{json.dumps(oid)}]; return o&&o.instrucao?[o.instrucao.vazao,o.instrucao.planoVer]:null;}})()")
        chk('P13b publicada a v7 (120 L/ha), a O.S. em A liberar emitida da v6 mostra "Plano v7 difere: volume de calda" e continua com 100 L/ha',
            t13.startswith('Publicada v7') and 'Plano v7 difere: volume de calda 100 L/ha nesta O.S. (v6) × 120 L/ha na v7' in nota and o3 == [100, 6], [t13, nota, o3, oid, J("((document.querySelector('aside[role=dialog]')||{}).innerText||'').slice(0,400)"), J(f"(()=>{{const c={CEN}; return Object.keys(c.pa||{{}}).map(k=>k+':'+(c.pa[k].versao));}})()")])
    # ---------------- P18 · ficha: vazão por bico alvo × disponível ----------------
    with secao('P18'):
        abre('OS-0424-ficha.dc.html'); time.sleep(.5); fx = J(f"{N}(document.body.innerText)")
        m = re.search(r'Vazão por bico ?(alvo [^·]+· disponível [^·]+·[^·]+)', fx, re.I)
        chk('P18 ficha da OS-0424: vazão por bico alvo 0,67 L/min (100 L/ha × 8 km/h × 0,5 m ÷ 600) × disponível 0,59 L/min da curva da ponta, com a diferença',
            bool(m) and 'alvo 0,67 L/min' in m.group(1) and 'disponível 0,59 L/min' in m.group(1) and 'diferença -11,5 %' in fx, m.group(1) if m else fx[:400])
    # ---------------- K2 · K3 · K5 · cliques ----------------
    with secao('K'):
        CARDP = "document.querySelector('main .g2card[aria-label=\"Abrir plano Soja alta tecnologia\"]')"
        abre('PA.dc.html'); espera(f"!!{CARDP}", 5); CLIQUES[0] = 0
        clique(CARDP, w=.7); clique(chip('Pulverização'), w=.5); clique(lab('Alterar o volume de calda da operação'), w=.3); seleciona_tudo(); digita('110'); enter()
        clique("document.querySelector('[data-acoes] [data-acao=comando]')", w=.7); k2 = (CLIQUES[0], toast())
        abre('PA.dc.html'); espera(f"!!{CARDP}", 5); CLIQUES[0] = 0
        clique(CARDP, w=.7); clique(lab('Alterar a calda de Fungicida 1ª aplicação'), w=.3); seleciona_tudo(); digita('130'); enter()
        clique("document.querySelector('[data-acoes] [data-acao=comando]')", w=.7); k3 = (CLIQUES[0], toast())
        abre('PA.dc.html#plano=SOJA-AT'); espera("document.querySelectorAll('button.pa-opf').length>1", 5); CLIQUES[0] = 0
        vistas = []
        for op in ['Pulverização', 'Tratamento de sementes', 'Plantio', 'Adubação a lanço', 'Colheita de grãos']:
            clique(chip(op), w=.35); vistas.append(len(J(ATVS)))
        k5 = (CLIQUES[0], vistas)
        abre('PA.dc.html'); espera(f"!!{CARDP}", 5); CLIQUES[0] = 0
        APL = "[...document.querySelectorAll('.pa-op-foco button')].find(b=>b.innerText.trim()==='Aplicar')"
        clique(CARDP, w=.7); clique(chip('Pulverização'), w=.5); clique(lab('Deslocar os gatilhos'), w=.3); digita('x'); clique(APL, w=.3)
        k7err = J(f"{N}((document.querySelector('.pa-op-foco [role=alert]')||{{}}).innerText||'')"); CLIQUES[0] -= 1
        J("(()=>{const e=document.getElementById('pa-desl'); e.focus(); e.select();})()"); digita('5'); clique(APL, w=.5)
        clique("document.querySelector('[data-acoes] [data-acao=comando]')", w=.7); k7 = (CLIQUES[0], toast())
        g7 = J("(()=>{const c=JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>/cenario-v1$/.test(k)))||'{}'); const v=((c.pa||{})['SOJA-AT']||{}).versoes||{}; return ((v[7]||{}).atividades||[]).map(a=>[a.nome,a.op,a.g&&a.g.dias]);})()") or []
        print(f'MEDIDA cliques · K2 {k2[0]} · K3 {k3[0]} · K5 {k5[0]} · K7 {k7[0]}', flush=True)
        chk('K2 calda das 4 pulverizações e publicar: ≤ 4 cliques (abrir o plano, Pulverização, Volume de calda, Salvar e publicar) + 1 campo', k2[0] <= 4 and k2[1].startswith('Publicada v7'), k2)
        chk('K3 calda própria numa atividade e publicar: ≤ 4 cliques + 1 campo', k3[0] <= 4 and k3[1].startswith('Publicada v7'), k3)
        chk('K5 percorrer as 5 operações uma por vez: ≤ 6 cliques, 0 campos', k5[0] <= 6 and k5[1] == [4, 1, 1, 1, 1], k5)
        chk('K7 deslocar +5 dias os gatilhos das 4 pulverizações e publicar: ≤ 6 cliques + 1 campo; DAP −20/25/45/60 → −15/30/50/65; as demais operações intactas; "x" recusado com o motivo',
            k7[0] <= 6 and k7[1].startswith('Publicada v7') and [x[2] for x in g7 if x[1] == 'Pulverização'] == [-15, 30, 50, 65]
            and [x[2] for x in g7 if x[1] != 'Pulverização'] == [-1, 0, 20, 118] and 'número inteiro' in k7err, [k7, k7err, g7])
    # ---------------- P16 · 390 px ----------------
    with secao('P16'):
        abre('PA.dc.html#plano=SOJA-AT&op=pulverizacao', w=390, h=844, e=2, t=True); espera("!!document.querySelector('.pa-op-foco')", 5)
        lado = J("document.documentElement.scrollWidth>innerWidth+1"); alt = J("[...document.querySelectorAll('button.pa-opf')].filter(b=>b.getClientRects().length).map(b=>Math.round(b.getBoundingClientRect().height))")
        clique("document.querySelector('.pa-desl')", toque=True, w=.4); alt += J("[...document.querySelectorAll('.pa-op-foco input,.pa-op-foco button')].filter(b=>b.getClientRects().length).map(b=>Math.round(b.getBoundingClientRect().height))") or [0]
        c.shot(os.path.join(PROBE, 'pa_oper_390_foco.png'))
        chk('P16 390 px (toque): sem rolagem lateral com a operação em foco; faixa, calda e deslocar (campo, Aplicar, Cancelar) com alvos de 44 px', not lado and alt and min(alt) >= 44, [lado, alt])
    # ---------------- P15 · migração na tela (a demanda e a impressão digital estão no pa_oper_p15_test.py) ----------------
    with secao('P15'):
        sys.path.insert(0, HERE); import dados2; ids = [x['id'] for x in dados2.PLANOS]; sec = {}; pend = {}; abre('PA.dc.html')
        for pid in ids:
            abre(f'PA.dc.html#plano={pid}'); espera("document.querySelectorAll('button.pa-opf').length>1", 5)   # carga nova por plano (troca só de # não recarrega)
            ch = J(CHIPS); sec[pid] = ch
            if pid != 'SOJA-AT' and any(x.startswith('Pulverização') for x in ch):
                r = clique(chip('Pulverização'), w=.3); espera("!!document.querySelector('.pa-op-foco')", 4)
                pend[pid] = J(f"{N}((document.querySelector('.pa-op-foco')||{{}}).innerText||'')") or [r, J('location.hash'), ch]
        chk(f'P15e os {len(ids)} planos abrem seccionados: "Visão geral" e ao menos uma operação, cada uma com o estado em texto',
            len(ids) == 8 and all(v and v[0].startswith('Visão geral') and len(v) > 1 and all(re.search(r'· (✓ Pronta|• Pendente|⚠ Com aviso|⛔ Impedida)$', x) for x in v[1:]) for v in sec.values()), sec)
        chk(f'P15f campo novo sem valor de código: a calda de Pulverização fica "Pendente" nos planos sem semente de demonstração ({", ".join(pend)})',
            pend and all(isinstance(t, str) and re.search(r'Volume de calda\s*Pendente', t, re.I) and '100 L/ha' not in t for t in pend.values()), pend)
        # P19 (2ª parte): rascunho guardado antes da F1, sem o campo, abre "Pendente", e não com os 100 L/ha da semente
        abre('PA.dc.html#plano=SOJA-AT&op=pulverizacao'); espera("!!document.querySelector('.pa-op-foco')", 5)
        editar_atividade('Fungicida 1ª aplicação'); campo_painel('fm_dias', '85'); salvar_painel()   # um rascunho v7 válido; tira-se o campo novo dele
        J("(()=>{const k=Object.keys(localStorage).find(k=>/cenario-v1$/.test(k)); const c=JSON.parse(localStorage.getItem(k)); delete c.pa['SOJA-AT'].rasc.params; localStorage.setItem(k,JSON.stringify(c));})()")
        recarrega(); espera("!!document.querySelector('.pa-op-foco')", 5)
        f19 = J(f"{N}((document.querySelector('.pa-op-foco')||{{}}).innerText||'')"); pv = J(PRIM)
        chk('P19b rascunho antigo sem calda (guardado antes da F1): Pulverização abre com a calda "Pendente", sem os 100 L/ha da semente; a v6 segue vigente',
            bool(re.search(r'Volume de calda\s*Pendente', f19, re.I)) and '100 L/ha' not in f19 and re.search(r'Rascunho v7( guardado \d\d:\d\d)? · v6 em vigor', J(SELO)), [f19[:300], J(SELO), pv])
except Exception as ex:
    chk('roteiro', False, repr(ex))
finally:
    try:
        if c and c.alvo: ERRL.extend(errs())
    except Exception: pass
    chk('P16 sem erro de JavaScript nas telas abertas', not ERRL, ERRL[:5])
    try:
        if c: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas', flush=True); sys.exit(1 if FAIL else 0)
