# -*- coding: utf-8 -*-
"""rev94 · sonda de navegador do AGRO-02 (revisão Claude do PR #94). Dados sintéticos.
Uso: python3 -B rev94_sonda.py <gen37 com _render montado> <pasta de saída>
A 1440 px (mouse e teclado) e a 390 px (toque emulado): abre a decisão da VIS-013 (feijão × mosca-branca), confere que nada vem marcado,
escolhe produto, digita a dose, troca de produto (a dose some), reclica o mesmo produto (a dose fica), dose fora da bula, trava de carência,
tenta emitir sem dose (bloqueado, com motivo), Esc e reabertura, ordem de Tab, árvore de acessibilidade e emissão com a dose digitada
(quantidade = dose × área, oráculo Decimal independente). Sai 1 se alguma verificação falhar (contraprova: deve reprovar em d995ded)."""
import sys, os, json, time, subprocess, urllib.request
from decimal import Decimal, ROUND_HALF_UP
G = os.path.abspath(sys.argv[1]); OUT = os.path.abspath(sys.argv[2]); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, G)
from cdp import Chrome
from journeys import free
import dados_mip as DM   # as funções do MIP não são globais na página: o dado vem da mesma derivação que alimenta o MIPD.agf
_v = DM.seed()['vis']['VIS-013']; PROT13 = _v['prot']; _p = DM.PROT[PROT13]
AGF13 = DM.AGF[_p['cultura'] + '|' + _p['chave']]
OK, FAIL, LOG = [], [], []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); linha = ('OK    ' if cond else 'FALHA ') + nome + ('' if cond else ' · ' + json.dumps(info, ensure_ascii=False)[:700])
    print(linha, flush=True); LOG.append(linha)
def br(x, casas=2):
    q = Decimal(str(x)).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP).normalize()
    s = format(q, 'f'); i, _, f = s.partition('.'); i = f'{int(i):,}'.replace(',', '.'); return i + (',' + f if f else '')
R = os.path.join(G, '_render'); porta = free()
srv = subprocess.Popen(['python3', '-m', 'http.server', str(porta), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
U = f'http://127.0.0.1:{porta}/'
fim = time.monotonic() + 20
while True:   # espera o servidor responder (condição observável, limite explícito)
    try: urllib.request.urlopen(U + 'Main.dc.html', timeout=2); break
    except Exception:
        if time.monotonic() > fim: raise RuntimeError('servidor http não respondeu em 20 s')
        time.sleep(0.1)
c = None; RES = {}
ESTADO = r"""(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return null;
 const rs=[...a.querySelectorAll('input[name=dc_prod]')]; const d=a.querySelector('#dc_dose');
 const b=[...a.querySelectorAll('button')].find(b=>b.innerText.trim()==='Emitir receituário e gerar O.S.');
 const ae=document.activeElement;
 return {n:rs.length, nomes:rs.map(r=>r.getAttribute('aria-label')), checked:rs.map(r=>r.checked), dose:d?d.value:null,
  lab:d?d.closest('label').querySelector('span').innerText:null, area:(a.querySelector('input[aria-label="Área em hectares"]')||{}).value,
  data:(a.querySelector('input[aria-label="Data da aplicação"]')||{}).value,
  emitir:b?{dis:b.disabled,title:b.title}:null, alerts:[...a.querySelectorAll('[role=alert]')].filter(x=>x.offsetParent!==null).map(x=>x.innerText.trim()),
  notes:[...a.querySelectorAll('[role=note]')].filter(x=>x.offsetParent!==null).map(x=>x.innerText.trim()),
  rows:[...a.querySelectorAll('[role=radiogroup][aria-label="Produto registrado"] > div')].map(x=>x.innerText.replace(/\s+/g,' ').trim()),
  form:!!a.querySelector('[role=group][aria-label="Decisão do agrônomo"]'),
  ativo:ae?(ae.id||ae.getAttribute('aria-label')||ae.tagName):null, sw:document.documentElement.scrollWidth, iw:innerWidth};})()"""
try:
    for _i in range(4):
        try: c = Chrome(port=free()); break
        except Exception: time.sleep(2)
    J = c.js
    def espera(js, limite=5.0, passo=0.05):
        fim = time.monotonic() + limite
        while time.monotonic() < fim:
            v = J(js)
            if v: return v
            time.sleep(passo)
        return None
    def st(): return J(ESTADO)
    TOQUE = [False]
    def alvo(sel_js):
        return J(f"(()=>{{const e={sel_js}; if(!e) return null; e.scrollIntoView({{block:'center'}}); const r=e.getBoundingClientRect(); return [r.x+r.width/2,r.y+r.height/2,r.width,r.height];}})()")
    def clique(sel_js):
        r = alvo(sel_js)
        if not r: return False
        x, y = r[0], r[1]
        if TOQUE[0]:
            c.call('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y}]})
            c.call('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        else:
            c.call('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': x, 'y': y})
            c.call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
            c.call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
        return True
    def tecla(key, code, vk, shift=False, texto=None):
        m = 8 if shift else 0
        c.call('Input.dispatchKeyEvent', dict({'type': 'keyDown' if texto else 'rawKeyDown', 'key': key, 'code': code, 'windowsVirtualKeyCode': vk, 'modifiers': m}, **({'text': texto} if texto else {})))
        c.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': key, 'code': code, 'windowsVirtualKeyCode': vk, 'modifiers': m})
    def digita(txt):   # foco no campo da dose com clique/toque real, seleciona o conteúdo e digita (insertText = teclado)
        clique("document.querySelector('aside #dc_dose')"); espera("document.activeElement&&document.activeElement.id==='dc_dose'", 2)
        J("document.activeElement.select()"); c.call('Input.insertText', {'text': txt})
        return espera(f"(document.querySelector('aside #dc_dose')||{{}}).value==={json.dumps(txt)}", 3)
    ROW = "[...document.querySelectorAll('aside [role=radiogroup][aria-label=\"Produto registrado\"] > div')][{i}].querySelector('b')"
    def escolhe(i):
        clique(ROW.format(i=i)); return espera(f"(()=>{{const r=[...document.querySelectorAll('aside input[name=dc_prod]')][{i}]; return !!r&&r.checked;}})()", 3)
    def ax():
        c.call('Accessibility.enable'); n = c.call('Accessibility.getFullAXTree').get('nodes', [])
        def prop(x, k): return next((p['value'].get('value') for p in x.get('properties', []) if p['name'] == k), None)
        nm = lambda x: (x.get('name') or {}).get('value')
        role = lambda x: (x.get('role') or {}).get('value')
        return {'radios': [[nm(x), prop(x, 'checked')] for x in n if role(x) == 'radio' and prop(x, 'checked') is not None and nm(x) and 'Controlar' not in nm(x) and 'localizado' not in nm(x) and 'monitorando' not in nm(x) and 'Não controlar' not in nm(x)],
                'grupo': [nm(x) for x in n if role(x) == 'radiogroup'],
                'dose': [[nm(x), (x.get('value') or {}).get('value'), prop(x, 'invalid'), prop(x, 'required')] for x in n if role(x) == 'textbox' and nm(x) == 'Dose por hectare'],
                'emitir': [[nm(x), prop(x, 'disabled'), (x.get('description') or {}).get('value')] for x in n if role(x) == 'button' and (nm(x) or '').startswith('Emitir receituário')]}
    def cenario(W, H):
        tag = f'{W}'; TOQUE[0] = W < 500
        c.size(W, H); c.call('Emulation.setTouchEmulationEnabled', {'enabled': TOQUE[0], 'maxTouchPoints': 5 if TOQUE[0] else 1})
        c.goto(U + 'Main.dc.html', wait=0.5); J("localStorage.removeItem('talhao-os-mip-v1'); localStorage.removeItem('talhao-os-cenario-v1'); sessionStorage.clear()")
        c.goto(U + 'AG-01.dc.html#VIS-013:decidir', wait=0.5)
        espera("!!document.querySelector('aside [role=radiogroup][aria-label=\"Produto registrado\"] input[name=dc_prod]')", 8); time.sleep(0.15)   # agFoco usa setTimeout(60 ms)
        P = [dict(nome=u['nome'], dmin=u['dmin'], dmax=u['dmax'], un=u['un'], sit=u['sit']) for u in AGF13]
        s1 = st(); a1 = ax(); RES[tag] = {'produtos': P, 'abertura': s1, 'ax_abertura': a1}
        c.shot(os.path.join(OUT, f'rev94_{tag}_1_abertura.png'))
        chk(f'{tag} S1 abertura: {s1 and s1["n"]} produtos, nenhum marcado, dose vazia, Emitir desligado com "Escolha um produto registrado." à vista',
            s1 and s1['n'] == 4 and not any(s1['checked']) and s1['dose'] == '' and s1['emitir']['dis'] is True and 'Escolha um produto registrado.' in s1['alerts'], s1)
        chk(f'{tag} S1a leitor de tela: 4 rádios com o nome do produto e checked=false; botão Emitir disabled com a descrição do motivo',
            len(a1['radios']) == 4 and all(r[1] in (False, 'false') for r in a1['radios']) and a1['emitir'] and a1['emitir'][0][1] is True, a1)
        nomes = s1['nomes']; info = {u['nome']: u for u in P}; p0, p1 = info[nomes[0]], info[nomes[1]]
        dose_ok = lambda u: br((Decimal(str(u['dmin'])) + Decimal(str(u['dmax']))) / 2, 3)
        # S2 · escolher o 1º produto: dose continua vazia (não vira a mínima da bula), unidade aparece, Emitir segue desligado com "Informe a dose."
        escolhe(0); s2 = st(); RES[tag]['escolhe0'] = s2
        chk(f'{tag} S2 escolher {nomes[0]}: marcado, dose vazia (não {br(p0["dmin"],3)}), rótulo "Dose ({p0["un"]}/ha)", Emitir desligado com "Informe a dose."',
            s2['checked'][0] and s2['dose'] == '' and s2['lab'] == f'Dose ({p0["un"]}/ha)' and s2['emitir']['dis'] is True and 'Informe a dose.' in s2['alerts'], s2)
        chk(f'{tag} S2a o selo do produto escolhido sem dose não diz "Conferido"', 'Conferido' not in s2['rows'][0], s2['rows'][0])
        # S9 · tentar emitir sem dose (clique/toque real no botão desligado): nada é gravado, motivo à vista
        clique("[...document.querySelectorAll('aside button')].find(b=>b.innerText.trim()==='Emitir receituário e gerar O.S.')"); time.sleep(0.3)   # ausência de efeito: janela curta explícita
        s9 = st(); os440 = J("(()=>{try{return !!JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'{}').ordens?.['OS-0440'];}catch(e){return 'erro';}})()")
        c.shot(os.path.join(OUT, f'rev94_{tag}_2_sem_dose.png'))
        em = (s9 or {}).get('emitir') or {}
        chk(f'{tag} S9 emitir sem dose: clique no botão não grava OS-0440; "Informe a dose." à vista; botão desligado (title "{em.get("title")}")',
            os440 is False and em.get('dis') is True and 'Informe a dose.' in (s9 or {}).get('alerts', []), [s9, os440])
        if not (s9 and s9['form']): raise RuntimeError('o clique em Emitir fechou a decisão (OS-0440 gravada: ' + str(os440) + ')')
        # S3 · digitar a dose e conferir a quantidade = dose × área com unidade (oráculo Decimal)
        d0 = dose_ok(p0); digita(d0); s3 = st(); area = Decimal(s3['area'].replace('.', '').replace(',', '.'))
        tot = br(Decimal(d0.replace(',', '.')) * area, 2); txt = ' '.join(s3['alerts'] + s3['notes'])
        RES[tag]['dose0'] = s3
        chk(f'{tag} S3 dose {d0} {p0["un"]}/ha × {s3["area"]} ha = {tot} {p0["un"]} na mensagem de estoque; sem trava de dose',
            s3['dose'] == d0 and f'{tot} {p0["un"]}' in txt and not any(x.startswith('Dose') or x == 'Informe a dose.' for x in s3['alerts']), [s3, tot])
        # S4 · trocar de produto: a dose some e o rótulo troca de unidade
        escolhe(1); s4 = st(); RES[tag]['troca'] = s4
        chk(f'{tag} S4 trocar para {nomes[1]}: dose digitada ({d0}) some, rótulo "Dose ({p1["un"]}/ha)", Emitir desligado',
            s4['checked'][1] and not s4['checked'][0] and s4['dose'] == '' and s4['lab'] == f'Dose ({p1["un"]}/ha)' and s4['emitir']['dis'] is True, s4)
        # S5 · reclicar o mesmo produto (clique/toque real) e Espaço no rádio marcado: a dose digitada fica
        d1 = dose_ok(p1); digita(d1); escolhe(1); time.sleep(0.2); s5a = st()
        if not TOQUE[0]:
            J(f"[...document.querySelectorAll('aside input[name=dc_prod]')][1].focus()"); tecla(' ', 'Space', 32, texto=' '); time.sleep(0.2)
        s5 = st(); RES[tag]['reclique'] = [s5a, s5]
        chk(f'{tag} S5 reclicar {nomes[1]}' + ('' if TOQUE[0] else ' e Espaço no rádio marcado') + f': dose {d1} preservada',
            s5a['checked'][1] and s5a['dose'] == d1 and s5['checked'][1] and s5['dose'] == d1, [s5a, s5])
        # S5b · voltar ao 1º: a dose do 2º não é herdada e a do 1º não volta sozinha
        escolhe(0); s5b = st()
        chk(f'{tag} S5b voltar a {nomes[0]}: dose vazia (nem {d1} do {nomes[1]} nem {d0} digitada antes)', s5b['checked'][0] and s5b['dose'] == '', s5b)
        # S7 · dose fora da bula e dose zero
        fora = br(Decimal(str(p0['dmax'])) * 3, 3); digita(fora); s7 = st(); digita('0'); s7z = st()
        chk(f'{tag} S7 dose {fora} fora da bula trava ("Dose fora da bula") e 0 trava ("Informe a dose."); Emitir desligado nos dois',
            any(x.startswith('Dose fora da bula') for x in s7['alerts']) and s7['emitir']['dis'] is True and 'Informe a dose.' in s7z['alerts'] and s7z['emitir']['dis'] is True, [s7, s7z])
        chk(f'{tag} S7a o selo do produto escolhido com dose 0 não diz "Conferido"', 'Conferido' not in s7z['rows'][0], s7z['rows'][0])
        # S8 · produto com trava legal (carência × colheita): Acaricida D em 28/09
        escolhe(1); digita(d1)
        J("""(()=>{const i=document.querySelector('aside input[aria-label="Data da aplicação"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'2026-09-28'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()""")
        espera("[...document.querySelectorAll('aside [role=alert]')].some(x=>x.innerText.indexOf('Carência')===0)", 3); s8 = st(); RES[tag]['carencia'] = s8
        chk(f'{tag} S8 {nomes[1]} em 28/09: trava de carência × colheita à vista, selo vermelho e Emitir desligado com dose válida',
            any(x.startswith('Carência de') for x in s8['alerts']) and s8['emitir']['dis'] is True and 'Carência × colheita' in s8['rows'][1], s8)
        J("""(()=>{const i=document.querySelector('aside input[aria-label="Data da aplicação"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'""" + s1['data'] + """'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()""")
        # S10 · Esc fecha a decisão e "Decidir controle" reabre sem nada marcado
        if not TOQUE[0]:
            clique("document.querySelector('aside #dc_dose')"); tecla('Escape', 'Escape', 27)
            fechou = espera("!document.querySelector('aside [role=group][aria-label=\"Decisão do agrônomo\"]')", 3)
        else:
            clique("[...document.querySelectorAll('aside button')].find(b=>b.innerText.trim()==='Cancelar')")
            fechou = espera("!document.querySelector('aside [role=group][aria-label=\"Decisão do agrônomo\"]')", 3)
        clique("document.getElementById('pan_prim')"); espera("!!document.querySelector('aside input[name=dc_prod]')", 3); time.sleep(0.15)
        s10 = st(); RES[tag]['reabre'] = s10
        chk(f'{tag} S10 ' + ('Esc' if not TOQUE[0] else 'Cancelar') + ' fecha a decisão e "Decidir controle" reabre sem produto nem dose; foco em ' + str(s10 and s10['ativo']),
            bool(fechou) and s10['form'] and not any(s10['checked']) and s10['dose'] == '' and s10['emitir']['dis'] is True, [fechou, s10])
        # S11 · ordem de Tab a partir do foco inicial (só 1440): quantos Tab até o 1º produto e até a dose; foco preso no diálogo
        if not TOQUE[0]:
            seq = []
            for _ in range(45):
                tecla('Tab', 'Tab', 9); time.sleep(0.03)
                d = J("(()=>{const e=document.activeElement; return [e.id||'', e.getAttribute('aria-label')||'', (e.innerText||'').trim().slice(0,28), e.name||'', !!e.closest('[role=dialog]')];})()")
                seq.append(d)
                if d[0] == 'pan_x': break
            i_rad = next((k + 1 for k, d in enumerate(seq) if d[3] == 'dc_prod'), None)
            RES[tag]['tab'] = seq
            chk(f'{tag} S11 Tab: foco preso no diálogo e o 1º produto é alcançado no Tab nº {i_rad} (a partir de "Fechar")',
                i_rad is not None and all(d[4] for d in seq), seq)
            # setas no grupo de rádios: ArrowDown troca de produto (é escolha explícita) e limpa a dose
            J("[...document.querySelectorAll('aside input[name=dc_prod]')][0].focus()"); tecla('ArrowDown', 'ArrowDown', 40)
            espera("[...document.querySelectorAll('aside input[name=dc_prod]')][1].checked", 2); s11 = st()
            chk(f'{tag} S11a seta para baixo no grupo marca {nomes[1]} com dose vazia', s11['checked'][1] and s11['dose'] == '', s11)
        # S12 · emissão com a dose digitada (≠ mínima): a O.S. e o receituário levam a dose do RT e o total = dose × área
        escolhe(0); d2 = dose_ok(p0); digita(d2); s12 = st()
        clique("[...document.querySelectorAll('aside button')].find(b=>b.innerText.trim()==='Emitir receituário e gerar O.S.')")
        o = espera("(()=>{try{const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'{}'); const o=Object.values(c.ordens||{}).find(o=>o.osc&&o.osc.novo&&(o.osc.novo.keys||[]).indexOf('mip|VIS-013|" + PROT13 + "')>=0); return o?JSON.stringify({id:o.id,etapa:o.etapa,ins:o.ins}):null;}catch(e){return null;}})()", 5)
        o = json.loads(o) if o else None; area = Decimal(s12['area'].replace('.', '').replace(',', '.'))
        tot = Decimal(d2.replace(',', '.')) * area; tot = float(tot.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        RES[tag]['emissao'] = [s12, o]
        chk(f'{tag} S12 emitir {nomes[0]} {d2} {p0["un"]}/ha × {s12["area"]} ha: O.S. em A liberar com dose {d2} (não a mínima {br(p0["dmin"],3)}) e total {br(tot)} {p0["un"]}',
            bool(o) and o['etapa'] == 'A liberar' and abs(o['ins'][0]['dose'] - float(d2.replace(',', '.'))) < 1e-9 and abs(o['ins'][0]['tot'] - tot) < 1e-9 and o['ins'][0]['un'] == p0['un'], [s12, o])
        # layout a 390: sem rolagem horizontal; alvo de toque da linha do produto
        if TOQUE[0]:
            J("history.replaceState(null,'',location.pathname+'#VIS-013'); location.hash='#VIS-013:decidir'")
            c.goto(U + 'Main.dc.html', wait=0.3); J("localStorage.removeItem('talhao-os-mip-v1'); localStorage.removeItem('talhao-os-cenario-v1'); sessionStorage.clear()")
            c.goto(U + 'AG-01.dc.html#VIS-013:decidir', wait=0.5); espera("!!document.querySelector('aside input[name=dc_prod]')", 8)
            hs = J("[...document.querySelectorAll('aside [role=radiogroup][aria-label=\"Produto registrado\"] > div label')].map(l=>Math.round(l.getBoundingClientRect().height))")
            sw = J("[document.documentElement.scrollWidth, innerWidth, Math.round(document.querySelector('aside[role=dialog]').scrollWidth), Math.round(document.querySelector('aside[role=dialog]').clientWidth)]")
            RES[tag]['layout'] = {'alturas_label': hs, 'scroll': sw}
            chk(f'{tag} L1 sem rolagem horizontal na página nem no painel {sw}', sw[0] <= sw[1] and sw[2] <= sw[3], sw)
            chk(f'{tag} L2 linha do produto (rótulo inteiro é alvo) com ≥ 44 px de altura: {hs}', all(h >= 44 for h in hs), hs)
    for W, H in ((1440, 900), (390, 844)):   # cada largura num bloco: na base (contraprova) a falha vira FALHA, não interrompe a outra largura
        try: cenario(W, H)
        except Exception as e: chk(f'{W} cenário completo sem exceção', False, repr(e)[:400])
finally:
    try:
        if c: c.close()
    finally:
        srv.terminate(); srv.wait(5)
json.dump(RES, open(os.path.join(OUT, 'rev94_sonda.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'RESULTADO {len(OK)}/{len(OK) + len(FAIL)}'); sys.exit(1 if FAIL else 0)
