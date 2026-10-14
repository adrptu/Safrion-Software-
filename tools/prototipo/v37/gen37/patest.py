# -*- coding: utf-8 -*-
"""Teste CDP · Planos agronômicos (PA.dc.html), reescrito para lista → detalhe (NAV-1, docs/navegacao/ESPECIFICACAO.md).
As regras são as mesmas do teste de etapas que ele substitui: biblioteca com um cartão por plano; o plano abre no detalhe; mudar
gatilho, dose ou insumo grava num rascunho v(n+1) sem mexer na versão publicada nem nos cultivos; excluir pede confirmação; o
gatilho antes do plantio não usa número negativo; as diferenças v7 × v6 aparecem antes de publicar; publicar cria a v7 e os
cultivos continuam na versão em que estão; descartar devolve a versão publicada; plano novo copiando de uma base nasce como
rascunho v1; nome repetido na cultura é recusado.
Uso (de gen37/): python3 patest.py [<_render>]   (sai 1 se algum caso falhar; capturas em _probe/pa_*.png)"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
import dados2 as D2
R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '_render')
PROBE = os.path.join(HERE, '_probe'); os.makedirs(PROBE, exist_ok=True)
p, srv = servir(R); c = Chrome(); J = c.js
CLK = """((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ '+root; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.getClientRects().length); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t))||els.find(x=>n(x.getAttribute('aria-label')).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
T = lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
DLG = lambda: J("!!document.querySelector('aside[role=dialog]')")
MAIN = lambda: J("document.querySelector('main').innerText")
FAIL = []; NOK = [0]
def clk(t, root=None, w=.4): r = J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(w); return r
def setv(sel, val): r = J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.25); return r
def check(nome, ok, info=''):
    print(('PASSOU ' if ok else 'FALHOU ') + nome, '' if ok else str(info)[:900], flush=True)
    if ok: NOK[0] += 1
    else: FAIL.append(nome)
def digita(txt): c.call('Input.insertText', {'text': txt}); time.sleep(.2)
def enter(): c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.45)
# VISOES-2 (padrão visual das Atividades do plano): o título expande os insumos; editar e excluir ficam no menu ⋯ da atividade
def mais(nome): J(f"[...document.querySelectorAll('main button.pa-titulo')].find(b=>b.innerText.trim()==={json.dumps(nome)}).closest('.pa-atividade').querySelector('.pa-mais').click()"); time.sleep(.3)
def atv(nome): mais(nome); clk('Editar atividade', 'main [role=menu]', w=.45)
def tem_atv(nome): return J(f"[...document.querySelectorAll('main button.pa-titulo')].some(b=>b.innerText.trim()==={json.dumps(nome)})")
def mostra(nome): clk('Mostrar insumos de ' + nome, w=.35)
def dose(prod, val):
    clk('Alterar a dose de ' + prod, w=.3); J("document.activeElement.select&&document.activeElement.select()"); digita(val); enter()
def gats(): return J("[...document.querySelectorAll('main .pa-gatilho')].map(g=>(g.getAttribute('title')||'').split(' · ')[0]).filter(t=>/^DAP /.test(t))")   # o texto inteiro fica na dica e no leitor
def gats_vis(): return J("[...document.querySelectorAll('main .pa-gatilho b')].map(b=>b.innerText.trim())")
def prims(): return J("[...document.querySelectorAll('header button,main button,[data-acoes] button')].filter(b=>b.getClientRects().length&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'&&b.getAttribute('aria-pressed')===null).map(b=>b.innerText.trim())")
try:
    c.aparelho(1440, 1000); c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .2); J("localStorage.clear()"); c.goto(f'http://127.0.0.1:{p}/PA.dc.html', .8)
    # ---- biblioteca
    cards = J("[...document.querySelectorAll('main .g2card')].map(b=>b.innerText.replace(/\\s+/g,' '))")
    check(f'biblioteca com um cartão por plano da fonte ({len(D2.PLANOS)}), sem faixa de etapas', len(cards) == len(D2.PLANOS) and not J("!!document.querySelector('.etp-ind')"), (len(cards), [x['nome'] for x in D2.PLANOS]))
    soja = [x for x in cards if x.startswith('Soja alta tecnologia')][0]
    check('cartão mostra versão, estado, atividades, gatilhos, custo e cultivos', all(k in soja for k in ['v6', 'Publicado', '8 atividades', 'DAP', 'R$ 2.099,90', 'Aplicado em 5 cultivos', '3 na v6 · 2 na v5']), soja)
    cafe = [x for x in cards if x.startswith('Café')][0]
    check('cartão do café com gatilhos Data e Após a colheita', 'Após a colheita' in cafe and 'Data' in cafe, cafe)
    # ---- detalhe
    J("document.querySelector('main .g2card[aria-label=\"Abrir plano Soja alta tecnologia\"]').click()"); time.sleep(.6)
    check('abrir o cartão leva ao detalhe do plano (#plano=SOJA-AT), sem primária enquanto não há rascunho', J("location.hash") == '#plano=SOJA-AT' and J("document.querySelector('main h2').innerText") == 'Soja alta tecnologia' and prims() == [], [J("location.hash"), prims()])
    check('gatilhos DAP em ordem numérica com negativos', gats() == ['DAP −20', 'DAP −1', 'DAP 0', 'DAP 20', 'DAP 25', 'DAP 45', 'DAP 60', 'DAP 118'], gats())
    # VISOES-2 "hoje × passa a ser": só o número na coluna (a seção já diz DAP), ícone do tipo, sem linha de operação, total da seção
    check('VISOES-2: só o número na coluna do gatilho; seção com "8 atividades · R$ 2.099,90/ha"; título sem sublinhado; ícone do tipo',
        gats_vis()[:3] == ['−20', '−1', '0'] and J("[...document.querySelectorAll('main .pa-grp-cab')].map(x=>x.innerText.replace(/\\s+/g,' ').trim())") == ['Dias após o plantio (DAP) ⓘ 8 atividades R$ 2.099,90/ha']
        and J("getComputedStyle(document.querySelector('main .pa-titulo')).textDecorationLine") == 'none' and J("document.querySelectorAll('main .pa-op-ico svg').length") >= 8,
        [gats_vis()[:3], J("[...document.querySelectorAll('main .pa-grp-cab')].map(x=>x.innerText.replace(/\\s+/g,' ').trim())"), J("document.querySelectorAll('main .pa-op-ico svg').length")])
    check('menos é mais (14/10): sem a linha "cultura · atividades · R$/ha · gatilhos" nem "Editar cria o rascunho" abaixo do título', 'Editar cria o rascunho' not in MAIN() and 'gatilhos: DAP' not in MAIN() and 'de insumos ·' not in MAIN(), MAIN()[:300])
    mostra('Fungicida 1ª aplicação'); txt = MAIN()
    check('a seta da atividade mostra os insumos sem abrir edição', not DLG() and 'Adjuvante espalhante' in txt and 'R$ 145,00/L' in txt and 'R$ 72,50/ha' in txt)
    atv('Fungicida 1ª aplicação')
    check('o nome da atividade abre o painel com o gatilho DAP 45 e o resumo dos 2 insumos', DLG() and J("document.querySelector('#fm_tipo').value") == 'DAP' and J("document.querySelector('#fm_dias').value") == '45' and '2 insumos' in J("document.querySelector('aside[role=dialog]').innerText"))
    setv('#fm_dias', '46'); clk('Cancelar', 'aside[role=dialog]')
    check('cancelar com alteração avisa antes de descartar', 'Há alterações não salvas' in J("document.querySelector('aside[role=dialog]').innerText"))
    clk('Continuar editando', 'aside[role=dialog]'); setv('#fm_dias', ''); clk('Salvar', 'aside[role=dialog]')
    check('erro junto ao campo, o resto do que foi preenchido fica', DLG() and 'Informe os dias' in J("document.querySelector('aside[role=dialog]').innerText") and J("document.querySelector('#fm_tipo').value") == 'DAP')
    clk('Cancelar', 'aside[role=dialog]'); clk('Descartar alterações', 'aside[role=dialog]')
    check('descartar a edição fecha o painel sem criar rascunho', not DLG() and prims() == [], prims())
    # ---- dose e insumo na tabela: rascunho v7
    dose('Fungicida A', '0,6'); t1 = T()
    check('mudar a dose na tabela cria o rascunho v7 sem mexer na v6', 'Rascunho v7 criado' in t1 and 'v6 publicada' in t1, t1)
    check('faixa amarela: aplicado em cultivos, que não serão alterados', 'Aplicado em 3 cultivos na v6 e 2 na v5 (safra encerrada) — não serão alterados' in MAIN())
    check('a dose fica marcada como alterada, com a versão publicada na dica', J("[...document.querySelectorAll('main span[title]')].some(s=>s.innerText==='dose alterada'&&/Na v6 publicada: 0,5 L\\/ha/.test(s.title))"))
    clk('Incluir insumo em Fungicida 1ª aplicação', w=.35); digita('Inseticida B'); enter(); digita('0,2'); enter(); t2 = T()
    check('incluir insumo pelo cadastro (busca, escolha, dose) grava no mesmo rascunho v7', 'Inseticida B incluído em Fungicida 1ª aplicação: 0,2 L/ha' in t2 and 'rascunho v7' in t2, t2)
    check('a atividade fica marcada como alterada', J("[...document.querySelectorAll('main span')].some(s=>s.innerText==='Alterada')"))
    # ---- excluir com desfazer (VISOES-2: sem janela de confirmação; o rascunho é recuperável)
    mais('Herbicida pós-emergente'); clk('Excluir atividade', 'main [role=menu]', w=.4)
    check('excluir tira a atividade na hora e oferece "Desfazer", sem janela de confirmação', not tem_atv('Herbicida pós-emergente') and 'excluída do rascunho' in MAIN() and not DLG(), MAIN()[:300])
    clk('Desfazer'); check('desfazer devolve a atividade ao rascunho', tem_atv('Herbicida pós-emergente'))
    mais('Herbicida pós-emergente'); clk('Excluir atividade', 'main [role=menu]', w=.4)
    check('excluir remove a atividade do rascunho', not tem_atv('Herbicida pós-emergente') and 'excluída do rascunho v7' in T(), T())
    # ---- incluir atividade nova (ancorada na colheita)
    clk('Incluir atividade')
    ordem = J("[...document.querySelectorAll('aside[role=dialog] label')].map(l=>l.innerText.trim()).slice(0,2).join(' → ')")
    check('o painel começa por Operação → Atividade, com o foco no 1º campo e o rodapé "Cancelar · Incluir atividade"', ordem == 'Operação → Atividade' and J("document.activeElement&&document.activeElement.id") == 'fm_op'
          and J("[...document.querySelectorAll('aside[role=dialog] .pe-form button')].map(b=>b.innerText.trim())") == ['Cancelar', 'Incluir atividade'], ordem)
    check('atividade desabilitada antes da operação', J("document.querySelector('#fm_atv').disabled") and 'Escolha a operação primeiro' in J("document.querySelector('#fm_atv').innerText"))
    setv('#fm_op', 'Adubação a lanço'); opts = J("[...document.querySelectorAll('#fm_atv option')].map(o=>o.innerText)")
    check('atividades filtradas pela operação (Adubação a lanço)', 'Calagem' in opts and 'Adubação de cobertura' in opts and 'Dessecação pré-plantio' not in opts and opts[-1] == 'Outra atividade…', opts)
    setv('#fm_atv', '__outra'); check('"Outra atividade…" abre o campo do nome', J("!!document.querySelector('#fm_nome')"))
    setv('#fm_op', 'Pulverização'); opts = J("[...document.querySelectorAll('#fm_atv option')].map(o=>o.innerText)")
    check('trocar a operação refiltra (Pulverização)', 'Dessecação pré-colheita' in opts and 'Calagem' not in opts, opts)
    setv('#fm_atv', 'Dessecação pré-colheita'); setv('#fm_tipo', 'DANC'); setv('#fm_dias', '5'); clk('Incluir atividade', 'aside[role=dialog]')
    grupos = J("[...document.querySelectorAll('main span')].map(s=>s.innerText).filter(t=>/^(Dias após o plantio|Em relação à colheita|Data do calendário)/.test(t))")
    check('a atividade nova entra no grupo "Em relação à colheita", com a inclusão de insumo pronta', not DLG() and 'Em relação à colheita' in grupos and '5 dias antes da colheita' in MAIN()
          and J("!!document.activeElement&&document.activeElement.getAttribute('role')==='combobox'"), grupos)
    digita('Diquat 200'); enter(); digita('2'); enter()
    check('o insumo da atividade nova entra pela tabela (Diquat 200, 2 L/ha)', 'Diquat 200 incluído em Dessecação pré-colheita: 2 L/ha' in T(), T())
    c.shot(os.path.join(PROBE, 'pa_detalhe_rascunho.png'))
    # ---- antes do plantio sem número negativo (39.6 · DAP-01)
    atv('Dessecação pré-plantio'); tipos = J("[...document.querySelectorAll('#fm_tipo option')].map(o=>o.innerText)")
    check('tipo "Dias antes do plantio" aparece antes do DAP', tipos[:2] == ['Dias antes do plantio', 'Dias após o plantio (DAP)'], tipos)
    ftxt = J("document.querySelector('aside[role=dialog]').innerText")
    check('DAP −20 abre como "Dias antes do plantio" com 20, sem sinal', J("document.querySelector('#fm_tipo').value") == 'DAPA' and J("document.querySelector('#fm_dias').value") == '20' and 'dias antes do plantio' in ftxt)
    check('ajuda sem pedir negativo: "Zero é o dia do plantio."', 'Zero é o dia do plantio.' in ftxt and 'negativo' not in ftxt)
    setv('#fm_dias', '-5'); clk('Salvar', 'aside[role=dialog]')
    check('número negativo é recusado: "Use zero ou mais: o sentido já está no tipo."', DLG() and 'Use zero ou mais: o sentido já está no tipo.' in J("document.querySelector('aside[role=dialog]').innerText"))
    setv('#fm_tipo', 'DAP')
    for s_ in ['−20', '–15']:
        setv('#fm_dias', s_); clk('Salvar', 'aside[role=dialog]')
        check(f'DAP com {s_} é recusado (não salva como DAP {s_[1:]})', DLG() and 'Use zero ou mais: o sentido já está no tipo.' in J("document.querySelector('aside[role=dialog]').innerText"))
    setv('#fm_tipo', 'DAPA'); setv('#fm_dias', '181'); clk('Salvar', 'aside[role=dialog]')
    check('antes do plantio limitado a 180 dias', 'Use de 0 a 180 dias.' in J("document.querySelector('aside[role=dialog]').innerText"))
    setv('#fm_dias', '25'); clk('Salvar', 'aside[role=dialog]')
    check('salvar 25 dias antes grava DAP −25', not DLG() and gats()[:2] == ['DAP −25', 'DAP −1'], gats())
    # ---- diferenças e publicar
    body = MAIN()
    check('o bloco de alterações v7 × v6 lista dose, inclusão, exclusão, atividade nova e gatilho', all(k in body for k in ['Alterações do rascunho v7 em relação à v6', 'Fungicida A: 0,5 → 0,6 L/ha', 'inclui Inseticida B', 'Excluída', 'Incluída', 'Dessecação pré-colheita', 'gatilho: DAP −20 → DAP −25']), body[-900:])
    check('antes de publicar, o bloco de alterações diz que os cultivos não mudam (3 na v6, 2 na v5)', 'Aplicado em 3 cultivos na v6 e 2 na v5 (safra encerrada): publicar não os altera' in body, body[-600:])
    check('uma primária: "Publicar versão v7"', prims() == ['Publicar versão v7'], prims())
    clk('Publicar versão v7', '[data-acoes]', .6)
    check('publicar cria a v7 e avisa que os cultivos ficam', 'Versão v7 publicada' in T() and '3 cultivos na v6' in T(), T())
    body = MAIN()
    # 14/10 (proprietário): Cultivos e Versões saíram do detalhe; o cabeçalho diz a versão em vigor
    check('depois de publicar: cabeçalho "Publicado · v7", sem os blocos Cultivos e Versões, sem primária',
          'Publicado · v7' in body and 'Cultivos que usam este plano' not in body and 'Mostrar as versões' not in body and prims() == [], [body[:300], prims()])
    clk('‹ Biblioteca de planos', '[data-acoes]', .6)
    soja = J("[...document.querySelectorAll('main .g2card')].map(b=>b.innerText.replace(/\\s+/g,' ')).find(t=>t.startsWith('Soja alta'))")
    check('o cartão passa à v7 publicada, com os cultivos ainda na v6 e na v5', 'v7' in soja and 'Publicado' in soja and '3 na v6 · 2 na v5' in soja and '8 atividades' in soja, soja)
    # ---- descartar o rascunho de um plano publicado
    J("document.querySelector('main .g2card[aria-label=\"Abrir plano Milho safrinha\"]').click()"); time.sleep(.6)
    mostra(J("[...document.querySelectorAll('main button.pa-titulo')].filter(b=>b.closest('.pa-atividade').querySelector('.pa-contagem').innerText!=='Só operação')[0].innerText"))
    J("document.querySelector('main button.pa-dose').click()"); time.sleep(.3); J("document.activeElement.select()"); digita('9'); enter()
    check('mudar a dose do milho cria o rascunho v5', 'Rascunho v5 criado' in T() and prims() == ['Publicar versão v5'], [T(), prims()])
    clk('Descartar rascunho'); clk('Descartar rascunho', 'main [role=alert]')
    check('descartar o rascunho volta à v4 publicada, sem primária', 'Rascunho v5 descartado. A v4 publicada continua valendo.' in T() and prims() == [] and 'Publicado · v4' in MAIN(), [T(), prims()])
    # ---- novo plano: copiar de uma base; nome repetido recusado
    clk('‹ Biblioteca de planos', '[data-acoes]', .6); clk('Criar plano', 'header')
    setv('#np_cult', 'Soja'); setv('#np_nome', 'Soja padrão'); clk('Criar plano', 'aside[role=dialog]')
    check('nome repetido na cultura é recusado', DLG() and 'Já existe um plano com este nome nesta cultura.' in J("document.querySelector('aside[role=dialog]').innerText"))
    setv('#np_nome', 'Soja teste'); setv('#np_base', 'SOJA-PD'); clk('Criar plano', 'aside[role=dialog]', .7)
    check('plano novo nasce como rascunho v1 com a cópia das atividades e abre no detalhe', 'rascunho v1' in T() and '4 atividades' in MAIN() and J("location.hash").startswith('#plano=NP') and prims() == ['Publicar versão v1'], [T(), prims()])
    clk('Descartar rascunho'); clk('Descartar rascunho', 'main [role=alert]')
    check('descartar o plano novo volta à biblioteca', J("location.hash") == '' and 'Plano novo descartado' in T() and J("document.querySelectorAll('main .g2card').length") == len(D2.PLANOS), T())
    check('sem erros JS', not J("window.__errs&&window.__errs.length"), J("window.__errs"))
    # ---- Desfazer a exclusão (Codex 6169663018): PA-DESFAZER-01 preserva o que mudou depois; PA-DESFAZER-02 recupera a última atividade
    def plano(nome):
        c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .2); J("localStorage.clear()"); c.goto(f'http://127.0.0.1:{p}/PA.dc.html', .8)
        J("document.querySelector('main .g2card[aria-label=\"Abrir plano %s\"]').click()" % nome); time.sleep(.6)
    def doses(): return J("[...document.querySelectorAll('main button.pa-dose')].map(b=>(b.getAttribute('aria-label')||'').replace('Alterar a dose de ','')+'='+b.innerText.trim())")
    plano('Soja alta tecnologia'); mostra('Fungicida 1ª aplicação')
    mais('Herbicida pós-emergente'); clk('Excluir atividade', 'main [role=menu]', w=.4); dose('Fungicida A', '0,6'); clk('Desfazer', w=.4)
    check('PA-DESFAZER-01: excluir (cria o rascunho) → mudar outra dose → Desfazer: a atividade volta uma vez e a dose nova (0,6) fica; o rascunho v7 continua',
          tem_atv('Herbicida pós-emergente') and J("[...document.querySelectorAll('main button.pa-titulo')].filter(b=>b.innerText.trim()==='Herbicida pós-emergente').length") == 1
          and any(x.split(', hoje')[0] == 'Fungicida A' and x.split('=')[-1].startswith('0,6') for x in doses()) and prims() == ['Publicar versão v7'], [doses(), prims()])
    plano('Soja alta tecnologia'); ordem0 = J("[...document.querySelectorAll('main button.pa-titulo')].map(b=>b.innerText.trim())")
    mais('Herbicida pós-emergente'); clk('Excluir atividade', 'main [role=menu]', w=.4); clk('Desfazer', w=.4)
    check('controle: excluir → Desfazer sem outra edição volta à v6 publicada (sem rascunho), na mesma posição; foco no nome da atividade',
          prims() == [] and J("[...document.querySelectorAll('main button.pa-titulo')].map(b=>b.innerText.trim())") == ordem0 and 'Publicado · v6' in MAIN()
          and J("(document.activeElement&&document.activeElement.innerText||'').trim()") == 'Herbicida pós-emergente', [prims(), J("document.activeElement&&document.activeElement.innerText")])
    menor = min(D2.PLANOS, key=lambda x: len(x.get('atividades') or []))
    plano(menor['nome']); nomes = J("[...document.querySelectorAll('main button.pa-titulo')].map(b=>b.innerText.trim())") or []
    for n in nomes: mais(n); clk('Excluir atividade', 'main [role=menu]', w=.4)
    vazio = 'Nenhuma atividade ainda' in MAIN(); des = J("[...document.querySelectorAll('main button')].filter(b=>b.getClientRects().length&&b.innerText.trim()==='Desfazer').length")
    clk('Desfazer', w=.4)
    check('PA-DESFAZER-02: excluir a última atividade mostra o estado vazio E o "Desfazer"; Desfazer devolve a atividade',
          bool(nomes) and vazio and des == 1 and tem_atv(nomes[-1]), [menor['nome'], nomes, vazio, des])
    # ---- celular (390 px, toque): a atividade em duas linhas (nome; gatilho · insumos · custo), nome com espaço útil, ⋯ visível sem hover
    c.aparelho(390, 844, 2, True); c.goto(f'http://127.0.0.1:{p}/PA.dc.html', .8)
    J("document.querySelector('main .g2card[aria-label=\"Abrir plano Soja alta tecnologia\"]').click()"); time.sleep(.6)
    m = J("""(()=>{const a=document.querySelector('main .pa-atividade'); const r=x=>a.querySelector(x).getBoundingClientRect();
      return {nome:Math.round(r('.pa-titulo').width), gy:Math.round(r('.pa-gatilho').top-r('.pa-titulo').top), ky:Math.round(r('.pa-custo').top-r('.pa-gatilho').top),
              op:getComputedStyle(a.querySelector('.pa-mais')).opacity, sw:document.documentElement.scrollWidth, w:innerWidth,
              tot:[...document.querySelectorAll('main .pa-grp-tot')].every(t=>t.getBoundingClientRect().right<=innerWidth)}})()""")
    check('celular: nome da atividade com ≥ 120 px, gatilho e custo na linha de baixo, ⋯ visível sem hover, sem rolagem lateral',
          m['nome'] >= 120 and m['gy'] > 0 and abs(m['ky']) <= 4 and m['op'] == '1' and m['sw'] == m['w'] and m['tot'], m)
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {NOK[0]} ok · ' + ('OK' if not FAIL else 'FALHAS: ' + '; '.join(FAIL)))
sys.exit(1 if FAIL else 0)
