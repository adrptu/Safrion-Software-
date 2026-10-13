# -*- coding: utf-8 -*-
"""Teste CDP · Planos agronômicos (PA.dc.html): abrir plano, expandir sem editar, nome abre edição, alterar dose,
cancelar com aviso, salvar (rascunho v7), excluir com confirmação, publicar versão (cultivos continuam na v6)."""
import sys, os, time, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE = os.path.dirname(os.path.abspath(__file__)); R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '_render'); p = free()
srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = Chrome(port=free()); J = c.js
CLK = """((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ '+root; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t))||els.find(x=>n(x.getAttribute('aria-label'))===t); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
T = lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
DLG = lambda: J("!!document.querySelector('aside[role=dialog]')")
FAIL = []
def clk(t, root=None): r = J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.4); return r
from comp_lib import IR_ETAPA
def ir_etapa(n): r = J(f"({IR_ETAPA})({n})"); time.sleep(.4); return r   # a faixa só informa: anda pela área de ações
def setv(sel, val): r = J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.25); return r
def check(nome, ok, info=''):
    print(('PASSOU ' if ok else 'FALHOU ') + nome, info if info else '')
    if not ok: FAIL.append(nome)
try:
    c.size(1440, 1100); c.goto(f'http://127.0.0.1:{p}/PA.dc.html')
    J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(String(e.message)));")
    cur = lambda: J("(document.querySelector('[aria-current=step]')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
    check('começa na etapa 1 sem plano escolhido', '1' in cur() and 'Escolha o plano' in cur(), cur())
    steps = J("[...document.querySelectorAll('.etp-ind .etp-itens>li')].map(b=>b.innerText.replace(/\\s+/g,' '))")
    check('etapas 2 e 3 mostram impedimento', all('Escolha um plano' in s for s in steps[1:]), steps)
    cards = J("[...document.querySelectorAll('button[aria-label^=\"Abrir plano\"]')].map(b=>b.innerText.replace(/\\s+/g,' '))")
    import dados2 as _D2   # um card por plano da fonte (a camada sintética acrescentou os 2 planos irrigados do mamão)
    check(f'biblioteca com um card por plano ({len(_D2.PLANOS)})', len(cards) == len(_D2.PLANOS), (len(cards), [p['nome'] for p in _D2.PLANOS]))
    soja = [x for x in cards if x.startswith('Soja alta tecnologia')][0]
    check('card mostra versão, estado, atividades, gatilhos, custo e cultivos', all(k in soja for k in ['v6', 'Publicado', '8 atividades', 'DAP', 'R$ 2.099,90', 'Aplicado em 5 cultivos', '3 na v6 · 2 na v5']), soja)
    cafe = [x for x in cards if x.startswith('Café')][0]
    check('card do café com gatilhos Data e Após a colheita', 'Após a colheita' in cafe and 'Data' in cafe, cafe)
    ir_etapa(3); check('etapa 3 sem plano é bloqueada', '1' in cur(), T())
    # abrir plano
    J("document.querySelector('button[aria-label=\"Abrir plano Soja alta tecnologia\"]').click()"); time.sleep(.5)
    check('abrir plano leva à etapa 2', '2' in cur() and 'Edite' in cur(), cur())
    gats = J("[...document.querySelectorAll('main b')].map(b=>b.innerText).filter(t=>/^DAP /.test(t))")
    check('gatilhos DAP em ordem numérica com negativos', gats == ['DAP −20', 'DAP −1', 'DAP 0', 'DAP 20', 'DAP 25', 'DAP 45', 'DAP 60', 'DAP 118'], gats)
    check('faixa informa que editar cria rascunho v7', 'Editar cria o rascunho v7' in J("document.body.innerText"))
    # expandir/recolher gatilho sem abrir edição
    J("document.querySelector('button[aria-label=\"Recolher DAP 45\"]').click()"); time.sleep(.3)
    check('recolher gatilho não abre edição', not DLG() and not J("[...document.querySelectorAll('main button')].some(b=>b.innerText==='Fungicida 1ª aplicação')"))
    J("document.querySelector('button[aria-label=\"Expandir DAP 45\"]').click()"); time.sleep(.3)
    J("document.querySelector('button[aria-label=\"Expandir Fungicida 1ª aplicação\"]').click()"); time.sleep(.3)
    txt = J("document.querySelector('main').innerText")
    check('expandir atividade mostra produtos sem abrir edição', not DLG() and 'Adjuvante espalhante' in txt and 'R$ 145,00/L' in txt and 'R$ 72,50/ha' in txt)
    # clicar no nome abre edição imediatamente
    J("[...document.querySelectorAll('main button')].find(b=>b.innerText==='Fungicida 1ª aplicação').click()"); time.sleep(.4)
    check('clicar no nome abre formulário lateral', DLG() and 'Fungicida 1ª aplicação' in J("document.querySelector('aside[role=dialog] h2').innerText"))
    check('formulário traz gatilho DAP 45 e 2 produtos', J("document.querySelector('#fm_tipo').value") == 'DAP' and J("document.querySelector('#fm_dias').value") == '45' and J("document.querySelectorAll('aside select[id^=fm_prod_]').length") == 2)
    # alterar dose, cancelar com aviso
    setv('#fm_dose_0', '0,6')
    check('custo da linha recalcula', 'R$ 87,00/ha' in J("document.querySelector('aside[role=dialog]').innerText"))
    clk('Cancelar', 'aside[role=dialog]')
    check('cancelar com alteração mostra aviso', 'Há alterações não salvas' in J("document.querySelector('aside[role=dialog]').innerText"))
    clk('Continuar editando', 'aside[role=dialog]')
    # erro junto ao campo preservando o digitado
    setv('#fm_dias', '')
    clk('Salvar', 'aside[role=dialog]')
    check('validação junto ao campo', DLG() and 'Informe os dias' in J("document.querySelector('aside[role=dialog]').innerText") and J("document.querySelector('#fm_dose_0').value") == '0,6')
    setv('#fm_dias', '45')
    # incluir produto na atividade
    clk('+ Incluir produto', 'aside[role=dialog]')
    setv('#fm_prod_2', 'Inseticida B'); setv('#fm_dose_2', '0,2')
    clk('Salvar', 'aside[role=dialog]')
    check('salvar cria rascunho v7 sem mexer na v6', not DLG() and 'Rascunho v7 criado' in T() and 'v6 publicada' in T(), T())
    check('faixa amarela: aplicado em cultivos, não serão alterados', 'Aplicado em 3 cultivos na v6 e 2 na v5 (safra encerrada) — não serão alterados' in J("document.body.innerText"))
    check('atividade marcada como alterada', J("[...document.querySelectorAll('main span')].some(s=>s.innerText==='Alterada')"))
    # excluir com confirmação
    J("document.querySelector('button[aria-label=\"Excluir atividade Herbicida pós-emergente\"]').click()"); time.sleep(.3)
    check('excluir pede confirmação', 'Excluir “Herbicida pós-emergente” do rascunho v7?' in J("document.body.innerText") and not DLG())
    clk('Manter'); check('manter não exclui', J("[...document.querySelectorAll('main button')].some(b=>b.innerText==='Herbicida pós-emergente')"))
    J("document.querySelector('button[aria-label=\"Excluir atividade Herbicida pós-emergente\"]').click()"); time.sleep(.3)
    clk('Excluir atividade'); check('excluir confirmado remove a atividade', not J("[...document.querySelectorAll('main button')].some(b=>b.innerText==='Herbicida pós-emergente')") and 'excluída do rascunho v7' in T(), T())
    # incluir atividade nova (ancorada na colheita, sem misturar com DAP)
    clk('Incluir atividade')
    ordem = J("[...document.querySelectorAll('aside[role=dialog] label')].map(l=>l.innerText.trim()).slice(0,2).join(' → ')")
    check('formulário começa por Operação → Atividade', ordem == 'Operação → Atividade', ordem)
    check('atividade desabilitada antes da operação', J("document.querySelector('#fm_atv').disabled") and 'Escolha a operação primeiro' in J("document.querySelector('#fm_atv').innerText"))
    setv('#fm_op', 'Adubação a lanço')
    opts = J("[...document.querySelectorAll('#fm_atv option')].map(o=>o.innerText)")
    check('atividades filtradas pela operação (Adubação a lanço)', 'Calagem' in opts and 'Adubação de cobertura' in opts and 'Dessecação pré-plantio' not in opts and opts[-1] == 'Outra atividade…', opts)
    setv('#fm_atv', '__outra'); check('"Outra atividade…" abre o campo do nome', J("!!document.querySelector('#fm_nome')"))
    setv('#fm_op', 'Pulverização')
    opts = J("[...document.querySelectorAll('#fm_atv option')].map(o=>o.innerText)")
    check('trocar a operação refiltra (Pulverização)', 'Dessecação pré-colheita' in opts and 'Calagem' not in opts, opts)
    setv('#fm_atv', 'Dessecação pré-colheita'); setv('#fm_tipo', 'DANC'); setv('#fm_dias', '5')
    clk('+ Incluir produto', 'aside[role=dialog]'); setv('#fm_prod_0', 'Diquat 200'); setv('#fm_dose_0', '2')
    clk('Salvar', 'aside[role=dialog]')
    grupos = J("[...document.querySelectorAll('main h3')].map(h=>h.innerText)")
    check('nova atividade entra no grupo "Em relação à colheita"', 'Em relação à colheita' in grupos and '5 dias antes da colheita' in J("document.querySelector('main').innerText"), grupos)
    c.shot(os.path.join(HERE, '_probe', 'pa_e2.png'))
    # clicar na linha (fora da seta) também abre; seta não abre
    J("[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Adubação de cobertura/.test(r.innerText)).querySelector('button.g2car').click()"); time.sleep(.3)
    check('seta da atividade só expande', not DLG())
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Adubação de cobertura/.test(r.innerText)); r.focus(); r.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));})()"); time.sleep(.3)
    check('Enter na linha abre edição', DLG())
    clk('Cancelar', 'aside[role=dialog]'); check('cancelar sem alteração fecha', not DLG())
    # antes do plantio sem número negativo (39.6 · DAP-01)
    J("[...document.querySelectorAll('main button')].find(b=>b.innerText==='Dessecação pré-plantio').click()"); time.sleep(.4)
    tipos = J("[...document.querySelectorAll('#fm_tipo option')].map(o=>o.innerText)")
    check('tipo "Dias antes do plantio" aparece antes do DAP', tipos[:2] == ['Dias antes do plantio', 'Dias após o plantio (DAP)'], tipos)
    ftxt = J("document.querySelector('aside[role=dialog]').innerText")
    check('DAP −20 abre como "Dias antes do plantio" com 20, sem sinal', J("document.querySelector('#fm_tipo').value") == 'DAPA' and J("document.querySelector('#fm_dias').value") == '20' and 'dias antes do plantio' in ftxt, (J("document.querySelector('#fm_tipo').value"), J("document.querySelector('#fm_dias').value")))
    check('ajuda sem pedir negativo: "Zero é o dia do plantio."', 'Zero é o dia do plantio.' in ftxt and 'negativo' not in ftxt)
    setv('#fm_dias', '-5'); clk('Salvar', 'aside[role=dialog]')
    check('número negativo é recusado: "Use zero ou mais: o sentido já está no tipo."', DLG() and 'Use zero ou mais: o sentido já está no tipo.' in J("document.querySelector('aside[role=dialog]').innerText"))
    # sinal de menos tipográfico (−, como na lista 'DAP −20') e meia-risca (–) não podem virar DAP positivo
    setv('#fm_tipo', 'DAP')
    for s_ in ['−20', '–15']:
        setv('#fm_dias', s_); clk('Salvar', 'aside[role=dialog]')
        check(f'DAP com {s_} é recusado (não salva como DAP {s_[1:]})', DLG() and 'Use zero ou mais: o sentido já está no tipo.' in J("document.querySelector('aside[role=dialog]').innerText"))
    setv('#fm_tipo', 'DAPA'); d0 = J("document.querySelector('#fm_dose_0').value")
    setv('#fm_dias', '20'); setv('#fm_dose_0', '−2'); clk('Salvar', 'aside[role=dialog]')
    check('dose com − é recusada: "Informe a dose por hectare (maior que zero)."', DLG() and 'Informe a dose por hectare (maior que zero).' in J("document.querySelector('aside[role=dialog]').innerText"))
    setv('#fm_dose_0', d0)
    setv('#fm_dias', '181'); clk('Salvar', 'aside[role=dialog]')
    check('antes do plantio limitado a 180 dias', 'Use de 0 a 180 dias.' in J("document.querySelector('aside[role=dialog]').innerText"))
    setv('#fm_dias', '25'); clk('Salvar', 'aside[role=dialog]')
    gats = J("[...document.querySelectorAll('main b')].map(b=>b.innerText).filter(t=>/^DAP /.test(t))")
    check('salvar 25 dias antes grava DAP −25', not DLG() and gats[:2] == ['DAP −25', 'DAP −1'], gats)
    # publicar
    clk('Revisar e publicar ›')
    body = J("document.querySelector('main').innerText")
    check('etapa 3 lista diferenças', all(k in body for k in ['Alterações do rascunho v7 em relação à v6', 'Fungicida A: 0,5 → 0,6 L/ha', 'inclui Inseticida B', 'Excluída', 'Incluída', 'Dessecação pré-colheita']), body[:600])
    check('diferença mostra o gatilho DAP −20 → DAP −25', 'gatilho: DAP −20 → DAP −25' in body, body[:400])
    check('cultivos continuam na v6 ao publicar', 'Continua na v6 ao publicar' in body and 'Safra encerrada · fica na v5' in body)
    prim = J("[...document.querySelectorAll('header button')].map(b=>b.innerText).join('|')")
    check('ação primária Publicar versão v7', 'Publicar versão v7' in prim, prim)
    c.shot(os.path.join(HERE, '_probe', 'pa_e3.png'))
    clk('Publicar versão v7')
    check('publicar cria v7 e avisa que cultivos ficam', 'Versão v7 publicada' in T() and '3 cultivos na v6' in T(), T())
    body = J("document.querySelector('main').innerText")
    check('após publicar: v7 em vigor, v6 substituída com 3 cultivos, decidir em Planejar safra', 'Em vigor' in body and 'Substituída' in body and 'Na v6 · decidir adoção da v7' in body and 'Decidir em Planejar safra' in body)
    check('nada mais a publicar', 'Nada a publicar' in body)
    ir_etapa(1)
    soja = J("[...document.querySelectorAll('button[aria-label^=\"Abrir plano\"]')].map(b=>b.innerText.replace(/\\s+/g,' ')).find(t=>t.startsWith('Soja alta'))")
    check('card atualizado para v7 publicada, cultivos na v6', 'v7' in soja and 'Publicado' in soja and '3 na v6 · 2 na v5' in soja and '8 atividades' in soja, soja)
    # novo plano
    clk('Novo plano'); setv('#np_cult', 'Soja'); setv('#np_nome', 'Soja teste'); setv('#np_base', 'SOJA-PD'); clk('Salvar', 'aside[role=dialog]')
    check('novo plano nasce como rascunho v1 com cópia', 'rascunho v1' in T() and '4 atividades' in J("document.querySelector('main').innerText"), T())
    clk('Descartar rascunho'); clk('Descartar rascunho', 'main [role=alert]')
    check('descartar plano novo volta à biblioteca', '1' in cur() and 'Plano novo descartado' in T(), T())
    check('sem erros JS', not J("window.__errs.length"), J("window.__errs"))
finally:
    c.close(); srv.terminate()
print('\nRESULTADO:', 'OK' if not FAIL else 'FALHAS: ' + '; '.join(FAIL))
