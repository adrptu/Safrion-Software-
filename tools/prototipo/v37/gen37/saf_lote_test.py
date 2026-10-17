# -*- coding: utf-8 -*-
"""EDL-01 · "Editar talhões" da fazenda no Planejar safra (proprietário, 16/10/2026: "coloque um botao para poder editar de uma vez todos
talhoes de uma fazenda numa tela só. como no outro anexo. todos inputs do usuário no sistema devem ser mais rápido e fácil."). Dados sintéticos.
A abrir pelo título do bloco (uma fazenda) e pela faixa de cada fazenda (várias), também no modo Cartões
B planilha: Tab, Enter/↓, ↑, foco que seleciona o número, contador e destaque das células alteradas
C aplicar aos marcados (cultura + plano), com a recusa da O.S. em execução
D colar bloco do Excel (TSV) com datas dd/mm, vírgula decimal e recusas (O.S., cultura fora do cadastro, plano de outra cultura, área acima)
E recusas no Salvar: soma das parcelas acima do talhão (SAF-C01) e campos obrigatórios; nada gravado; O.S. liberada trava a célula com link
F salvar: a grade mostra os valores, a demanda é recalculada e o resumo da fazenda muda; duplo clique não duplica (linhas livres da Safrinha)
G perene de outra safra só leitura com "Vincular ciclo ›"; Esc com alteração pede confirmação; conflito (outra aba liberou uma O.S.);
  falha no meio da gravação conserva o rascunho e os dados; Dividir pelo link da linha
H 390 px: alvos de 44 px, sem rolagem de lado, barra de salvar à vista, faixa "Aplicar" só com linha marcada
I INP no motor: número do formulário selecionado ao receber o foco e sem corretor (g2lib, g2inp)
Uso: python3 -B saf_lote_test.py  ·  contraprova: RENDER_DIR=<_render da base> (sem o botão: reprova em A)."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
PROBE = os.path.join(HERE, '_probe'); os.makedirs(PROBE, exist_ok=True)
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK    ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:700], flush=True)
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda x: f'http://127.0.0.1:{p}/{x}'
q = json.dumps
def esp(t=.5): time.sleep(t)
def abrir_saf(hash_, w=1440):
    c.aparelho(w, 900 if w > 400 else 844, 1 if w > 400 else 2, w < 400); c.call('Page.bringToFront')   # janela com o foco, como a de quem usa
    c.goto(U('Main.dc.html'), .2); J("localStorage.clear();sessionStorage.clear()")
    c.goto(U('SAF.dc.html#' + hash_), 1.6); esp(1.0)
def painel(): return J("(()=>{const a=document.getElementById('sl-painel'); return a&&a.offsetParent!==null?a.innerText.replace(/\\s+/g,' '):'';})()") or ''
def linhas(): return J("[...document.querySelectorAll('#sl-grade .sl-l:not(.sl-cab):not(.sl-ap) .sl-id b')].map(b=>b.innerText.trim())") or []
def cel(k, col): return f"document.querySelector('#sl-grade [data-l=\"{k}\"][data-c=\"{col}\"]')"
def val(k, col): return J(f"(()=>{{const e={cel(k,col)}; return e?e.value:null;}})()")
def foca(k, col): return J(f"(()=>{{const e={cel(k,col)}; if(!e) return false; if(document.activeElement) document.activeElement.blur(); e.focus(); return true;}})()")   # chegar à célula (de novo) como a pessoa: o foco seleciona o número
def ativo(): return J("(()=>{const e=document.activeElement; return e?[e.getAttribute('data-l'),e.getAttribute('data-c'),e.value,e.selectionStart,e.selectionEnd]:null;})()")
def poe(k, col, v):   # escolha numa lista ou data: como a pessoa escolhe (o valor muda e o evento sai)
    r = J(f"""(()=>{{const e={cel(k,col)}; if(!e||e.disabled||e.readOnly) return false; const P=e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(P,'value').set.call(e,{q(v)}); e.dispatchEvent(new Event('input',{{bubbles:true}})); e.dispatchEvent(new Event('change',{{bubbles:true}})); return true;}})()"""); esp(.45); return r
def digita(txt): c.call('Input.insertText', {'text': txt}); esp(.45)
def tecla(k, shift=False):
    vk = {'Enter': 13, 'Tab': 9, 'ArrowDown': 40, 'ArrowUp': 38, 'Escape': 27}[k]
    p0 = {'type': 'keyDown', 'key': k, 'code': k, 'windowsVirtualKeyCode': vk, 'modifiers': 8 if shift else 0}
    if k == 'Enter': p0['text'] = '\r'
    c.call('Input.dispatchKeyEvent', p0); c.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': k, 'code': k, 'windowsVirtualKeyCode': vk, 'modifiers': 8 if shift else 0}); esp(.4)
def botao(txt, raiz='#sl-painel'):
    r = J(f"(()=>{{const b=[...document.querySelectorAll('{raiz} button')].find(b=>b.offsetParent&&b.innerText.replace(/\\s+/g,' ').trim().startsWith({q(txt)})); if(!b) return false; b.click(); return true;}})()"); esp(.6); return r
def marca(k): r = J(f"(()=>{{const e=document.querySelector('#sl-grade .sl-l[data-k=\"{k}\"] .sl-s input'); if(!e) return false; e.click(); return true;}})()"); esp(.35); return r
def ap(col, v):
    sel = {'cult': 'Cultura para os marcados', 'var': 'Variedade para os marcados', 'plantio': 'Plantio para os marcados', 'meta': 'Meta para os marcados', 'plano': 'Plano para os marcados'}[col]
    r = J(f"""(()=>{{const e=document.querySelector('#sl-grade [aria-label="{sel}"]'); if(!e) return false; const P=e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(P,'value').set.call(e,{q(v)}); e.dispatchEvent(new Event('input',{{bubbles:true}})); e.dispatchEvent(new Event('change',{{bubbles:true}})); return true;}})()"""); esp(.4); return r
def cola(k, col, txt):   # colar (Ctrl+V) na célula focada: o evento de colar do navegador com o texto da planilha
    r = J(f"""(()=>{{const e={cel(k,col)}; if(!e) return false; e.focus(); const dt=new DataTransfer(); dt.setData('text/plain',{q(txt)});
      e.dispatchEvent(new ClipboardEvent('paste',{{clipboardData:dt,bubbles:true,cancelable:true}})); return true;}})()"""); esp(.6); return r
def info(): return J("(document.getElementById('sl-info')||{}).innerText||''") or ''
def gerr(): return J("(document.getElementById('sl-gerr')||{}).innerText||''") or ''
def salvarT(): return J("(document.getElementById('sl-salvar')||{}).innerText||''") or ''
def toast(): return J("[...document.querySelectorAll('.g2toast')].map(x=>x.innerText).join(' | ')") or ''
def cultivos(saf): return {x['local']: x for x in (J(f"window.__safRef.cultivos({q(saf)})") or [])}
def estilo(k, col): return J(f"(()=>{{const e={cel(k,col)}; return e?getComputedStyle(e).borderTopColor:null;}})()")
def erros(): return J("(window.__errs||[]).join(' | ')") or ''
try:
    # ---------------- A · abrir ----------------
    abrir_saf('saf=S2627&passo=cultivos')
    lk = J("(()=>{const b=document.getElementById('sl-abrir'); return b&&b.offsetParent?b.innerText.trim():null;})()")
    chk('A1 Safra 2026/27 (uma fazenda): "Editar talhões…" no título do bloco Talhões e cultivos, ao lado de "Planejar talhões livres…"', lk == 'Editar talhões…', lk)
    if lk != 'Editar talhões…':
        print('RESULTADO: FALHOU (sem o botão; o resto não se executa)'); raise SystemExit(1)
    J("document.getElementById('sl-abrir').click()"); esp(1.2)
    pn = painel(); ls = linhas()
    chk('A2 abre "Editar talhões da Santa Rita" com uma linha por talhão (T1 com as parcelas recuadas embaixo), resumo da área e selo "Tudo salvo"; Salvar com contador 0',
        pn.startswith('Editar talhões da Santa Rita') and ls == ['T1', 'T1-A', 'T1-B', 'T2', 'T3', 'T4', 'P1', 'P2', 'T7', 'C1'] and 'Área 1.165 ha · planejada 1.165 ha' in pn and 'Tudo salvo' in pn and salvarT() == 'Salvar alterações (0)', [pn[:200], ls, salvarT()])
    a0 = ativo()
    chk('A3 no computador o foco já está na 1ª célula editável (área de T1-A) com o número selecionado (digitar substitui)', a0 and a0[0] == 'c1' and a0[1] == 'area' and a0[3] == 0 and a0[4] == len(a0[2]), a0)
    # ---------------- B · planilha ----------------
    foca('c5', 'meta'); a1 = ativo(); digita('70'); v1 = val('c5', 'meta'); tecla('Enter'); a2 = ativo(); digita('68'); tecla('ArrowUp'); a3 = ativo()
    chk('B1 foco no número seleciona o conteúdo (INP-04): "70" substitui 62 em T3; Enter desce para a meta de T4 já selecionada; "68"; ↑ volta para T3',
        a1[3] == 0 and a1[4] == 2 and v1 == '70' and a2[:2] == ['c4', 'meta'] and a2[3] == 0 and a2[4] == 2 and val('c4', 'meta') == '68' and a3[:2] == ['c5', 'meta'], [a1, v1, a2, a3])
    foca('c5', 'var'); tecla('Tab'); b1 = ativo(); tecla('Tab', shift=True); b2 = ativo(); tecla('ArrowDown'); b3 = ativo()
    chk('B2 Tab anda para a coluna seguinte (variedade → plantio de T3), Shift+Tab volta; ↓ desce na mesma coluna (também na célula travada, que só se lê)', b1[:2] == ['c5', 'plantio'] and b2[:2] == ['c5', 'var'] and b3[:2] == ['c4', 'var'], [b1, b2, b3])
    st = estilo('c5', 'meta'); st0 = estilo('c7', 'meta')
    chk('B3 células alteradas destacadas (borda âmbar) e contador "Salvar alterações (2)"; selo "2 alterações não salvas"', st == 'rgb(138, 90, 0)' and st0 != st and salvarT() == 'Salvar alterações (2)' and '2 alterações não salvas' in painel(), [st, st0, salvarT()])
    sp = J(f"(()=>{{const e={cel('c5','meta')}; return [e.getAttribute('spellcheck'),e.getAttribute('inputmode'),e.getAttribute('autocomplete')];}})()")
    chk('B4 meta com teclado decimal, sem corretor e sem autocompletar; unidade à vista ao lado (sc/ha; mamão t/ha/ano)', sp == ['false', 'decimal', 'off'] and
        J("[...document.querySelectorAll('#sl-grade .sl-l[data-k=c5] .sl-un, #sl-grade .sl-l[data-k=c8] .sl-un')].map(e=>e.innerText.trim())") == ['sc/ha', 't/ha/ano'], sp)
    # ---------------- E2 · O.S. liberada ou em execução trava cultura, variedade e plano ----------------
    t2 = J(f"(()=>{{const c={cel('c3','cult')}, v={cel('c3','var')}, p={cel('c3','plano')}, m={cel('c3','meta')}; return [c.disabled,v.readOnly,p.disabled,m.readOnly,c.title];}})()")
    lkos = J("(()=>{const r=document.querySelector('#sl-grade .sl-l[data-k=c3]'); return [...new Set([...r.querySelectorAll('.sl-sit span,.sl-sit button')].map(x=>x.innerText.trim()))];})()")
    chk('E2 T2 com a OS-0421 em execução: cultura, variedade e plano travados na célula com o motivo; meta e plantio editáveis; Situação "Bloqueado · OS-0421" com o link OS-0421 ›',
        t2[:4] == [True, True, True, False] and 'OS-0421 em execução' in t2[4] and lkos == ['Bloqueado · OS-0421', 'OS-0421 ›'], [t2, lkos])
    # ---------------- C · aplicar aos marcados ----------------
    for k in ('c5', 'c6', 'c7', 'c4'): marca(k)
    ap('cult', 'Milho'); ap('plano', 'MILHO-SF'); botao('Aplicar a 4 marcados'); inf = info()
    chk('C1 Aplicar aos 4 marcados (cultura Milho e plano Milho safrinha): T3, P1 e P2 recebem; T4 recusa os dois pela OS-0420 e o resumo diz quantos e por quê',
        [val(k, 'cult') for k in ('c5', 'c6', 'c7', 'c4')] == ['Milho', 'Milho', 'Milho', 'Soja'] and [val(k, 'plano') for k in ('c5', 'c6', 'c7')] == ['MILHO-SF'] * 3
        and 'Aplicado em 6 células de 4 linhas' in inf and '2 recusados (T4 · Cultura: OS-0420' in inf, [inf, [val(k, 'cult') for k in ('c5', 'c6', 'c7', 'c4')]])
    chk('C2 trocar a cultura limpa a variedade que era da soja (62 X, 58 W): nada fica com variedade de outra cultura', [val(k, 'var') for k in ('c5', 'c6', 'c7')] == ['', '', ''], [val(k, 'var') for k in ('c5', 'c6', 'c7')])
    cv0 = cultivos('S2627'); botao('Salvar alterações'); g1 = gerr(); cv1 = cultivos('S2627')
    chk('C3 salvar com variedade vazia: recusa atômica nas células (Variedade: Informe a variedade), nada gravado, o digitado fica',
        'precisam de correção' in g1 and 'Nada foi gravado' in g1 and cv1 == cv0 and cv1['T3']['cult'] == 'Soja' and val('c5', 'cult') == 'Milho'
        and J("[...document.querySelectorAll('#sl-grade .sl-err')].map(e=>e.innerText).join(' | ')").count('Variedade: Informe a variedade') == 3, [g1, J("[...document.querySelectorAll('#sl-grade .sl-err')].map(e=>e.innerText).join(' | ')")])
    ap('var', 'Híbrido AG 8700'); ap('cult', ''); ap('plano', ''); botao('Aplicar a 4 marcados')
    chk('C4 variedade aplicada aos marcados; T4 recusa (OS-0420)', [val(k, 'var') for k in ('c5', 'c6', 'c7', 'c4')] == ['Híbrido AG 8700'] * 3 + ['58 W'] and 'T4 · Variedade: OS-0420' in info(), info())
    er4 = J("[...document.querySelectorAll('#sl-grade .sl-err')].map(e=>e.innerText).join(' | ')") or ''
    chk('C5 (revisão do app do Codex, #98 P2) a variedade aplicada aos marcados apaga o erro "Informe a variedade" dessas linhas e a mensagem geral da recusa',
        'Informe a variedade' not in er4 and not gerr(), [er4, gerr()])
    ap('cult', 'Soja'); ap('var', '58 W'); ap('cult', 'Milho'); vf = J("(document.querySelector('#sl-grade [aria-label=\"Variedade para os marcados\"]')||{}).value")
    chk('C6 (revisão do app do Codex, #98 P2) na faixa, trocar Soja por Milho tira do campo Variedade a cultivar de soja (58 W)', vf == '', vf)
    ap('cult', ''); ap('var', '')
    for k in ('c5', 'c6', 'c7', 'c4'): marca(k)
    # ---------------- D · colar bloco ----------------
    cola('c5', 'plantio', '05/11/2026\t181\n06/11\t62\n07/11/2026\t183,5\n')
    chk('D1 colar 3 × 2 a partir do plantio de T3: datas dd/mm (o ano da safra) e vírgula decimal; "Colados 3 × 2: 6 células"; nada salvo',
        [val(k, 'plantio') for k in ('c5', 'c4', 'c6')] == ['2026-11-05', '2026-11-06', '2026-11-07'] and [val(k, 'meta') for k in ('c5', 'c4', 'c6')] == ['181', '62', '183,5']
        and info().startswith('Colados 3 × 2: 6 células') and 'Nada foi salvo' in info(), [info(), [val(k, 'plantio') for k in ('c5', 'c4', 'c6')], [val(k, 'meta') for k in ('c5', 'c4', 'c6')]])
    cola('c5', 'cult', 'Milho\tHíbrido AG 8700\nSoja\t64 Z\nTrigo\tBRS 1\n')
    inf = info()
    chk('D2 colar com recusas: T4 (OS-0420) recusa cultura e variedade; "Trigo" fora do cadastro recusado; o resto colado',
        inf.startswith('Colados 3 × 2: 3 células; 3 recusados') and 'T4 · Cultura: OS-0420' in inf and 'cultura "Trigo" não está no cadastro' in inf and val('c6', 'var') == 'BRS 1' and val('c6', 'cult') == 'Milho', inf)
    cola('c5', 'plano', 'Feijão pivô')
    chk('D3 colar um plano de outra cultura (Feijão pivô em T3 de milho): recusado com o motivo; o plano fica', 'plano de Feijão não serve para Milho' in info() and val('c5', 'plano') == 'MILHO-SF', info())
    cola('c1', 'area', '400\n')
    chk('D4 colar área acima do talhão na parcela: recusada (acima dos 312 ha do talhão)', 'acima dos 312 ha do talhão' in info() and val('c1', 'area') == '160', info())
    poe('c6', 'var', 'Híbrido AG 8700')
    # ---------------- E1 · soma das parcelas acima do talhão ----------------
    foca('c1', 'area'); digita('200'); botao('Salvar alterações'); g2 = gerr(); er = J("[...document.querySelectorAll('#sl-grade .sl-err')].map(e=>e.innerText).join(' | ')")
    chk('E1 T1-A com 200 ha (T1-B 152): Salvar recusa com a conta do Dividir ("As parcelas somam 352 ha; o talhão tem 312 ha"), nada gravado, o rascunho fica',
        'precisa de correção' in g2 and 'As parcelas somam 352 ha; o talhão tem 312 ha' in er and cultivos('S2627') == cv0 and val('c1', 'area') == '200', [g2, er])
    foca('c1', 'area'); digita('150')
    # ---------------- F · salvar ----------------
    dem0 = J("(()=>{const d=window.__solo.dem('S2627'); return [(d['Atrazina 500']||{}).bruta||0,(d['Glifosato 480']||{}).bruta||0];})()")
    n_alt = salvarT(); botao('Salvar alterações'); esp(.6); t1 = toast(); cv2 = cultivos('S2627')
    chk('F1 salvar: um aviso de sucesso com as alterações; o painel fecha; os cultivos mudaram (T3, P1, P2 milho; T1-A 150 ha; metas e plantios colados)',
        not painel() and 'Santa Rita:' in t1 and 'salvos' in t1 and 'Plano operacional, recursos e demanda recalculados' in t1
        and [cv2[t]['cult'] for t in ('T3', 'P1', 'P2', 'T4', 'T2')] == ['Milho', 'Milho', 'Milho', 'Soja', 'Soja'] and cv2['T1-A']['area'] == 150 and cv2['T3']['plantio'] == '2026-11-05'
        and cv2['T3']['plano'] == 'MILHO-SF' and cv2['T4']['plantio'] == '2026-11-06', [n_alt, t1, gerr(), J("[...document.querySelectorAll('#sl-grade .sl-err')].map(e=>e.innerText).join(' | ')"), {k: (v['cult'], v['area'], v['plantio'], v['plano']) for k, v in cv2.items()}])
    dem1 = J("(()=>{const d=window.__solo.dem('S2627'); return [(d['Atrazina 500']||{}).bruta||0,(d['Glifosato 480']||{}).bruta||0];})()")
    chk('F2 demanda recalculada pela mesma conta: Atrazina 500 (só no plano do milho) passa a ter demanda; Glifosato (só no da soja de T1/T2) não cresce', dem0[0] == 0 and dem1[0] > 0 and dem1[1] <= dem0[1], [dem0, dem1])
    tab = J("[...document.querySelectorAll('[role=table] [role=row]')].filter(r=>r.offsetParent).map(r=>r.innerText.replace(/\\s+/g,' ')).filter(t=>/^.?\\s?(T3|P2) /.test(t))")
    chk('F3 a tabela mostra os valores novos (T3 e P2 com milho e Milho safrinha)', any('Milho' in t and 'Milho safrinha' in t for t in tab) and len(tab) >= 2, tab)
    J("document.getElementById('sl-abrir').click()"); esp(1.2)
    chk('F4 reabrir mostra o salvo (T3 milho, meta 181) e o resumo com 1.155 ha planejados (T1-A 150)', val('c5', 'cult') == 'Milho' and val('c5', 'meta') == '181' and 'planejada 1.155 ha' in painel() and salvarT() == 'Salvar alterações (0)', [val('c5', 'cult'), val('c5', 'meta'), painel()[:160]])
    # ---------------- G · Esc, conflito, falha, Dividir ----------------
    foca('c7', 'meta'); digita('77'); tecla('Escape'); w1 = J("!!document.querySelector('#sl-painel .saida')"); botao('Continuar editando'); w2 = J("!!document.querySelector('#sl-painel .saida')")
    tecla('Escape'); botao('Descartar alterações'); cv3 = cultivos('S2627')
    chk('G1 Esc com alteração pede confirmação ("Há alterações não salvas"); Continuar editando fica; Descartar fecha sem gravar', w1 and not w2 and not painel() and cv3['P2']['meta'] == cv2['P2']['meta'] and 'Alterações descartadas' in toast(), [w1, w2, cv3['P2']])
    J("document.getElementById('sl-abrir').click()"); esp(1.2); foca('c7', 'meta'); digita('77')
    J("(()=>{const c=window.__solo.cen(); c.ordens['OS-0430'].etapa='Liberadas'; localStorage.setItem('talhao-os-cenario-v1',JSON.stringify(c));})()")   # outra aba libera a OS-0430 (T1-A)
    botao('Salvar alterações'); g3 = gerr()
    chk('G2 conflito: outra aba liberou a OS-0430 (T1-A) depois de abrir; Salvar recusa com o motivo, nada gravado, o rascunho fica', 'mudaram depois que você abriu' in g3 and val('c7', 'meta') == '77' and cultivos('S2627')['P2']['meta'] == cv2['P2']['meta'], g3)
    botao('Cancelar'); botao('Descartar alterações')
    J("document.getElementById('sl-abrir').click()"); esp(1.2)
    chk('G3 reaberto, T1-A passa a travar cultura, variedade e plano pela OS-0430 (a fase vem do cenário compartilhado)', J(f"{cel('c1','cult')}.disabled") is True and 'OS-0430' in (J(f"{cel('c1','cult')}.title") or ''), J(f"{cel('c1','cult')}.title"))
    foca('c7', 'meta'); digita('79')
    J("""(()=>{const s=window.__safSelf; const v=s.state.adj; Object.defineProperty(s.state,'adj',{configurable:true,get(){ Object.defineProperty(s.state,'adj',{configurable:true,writable:true,value:v}); throw new Error('falha simulada'); }});})()""")
    botao('Salvar alterações'); g4 = gerr()
    chk('G4 falha no meio da gravação: "Não foi possível salvar (falha simulada)", nada gravado, painel aberto com o rascunho', 'Não foi possível salvar (falha simulada)' in g4 and val('c7', 'meta') == '79' and cultivos('S2627')['P2']['meta'] == cv2['P2']['meta'], g4)
    botao('Salvar alterações'); esp(.4)
    chk('G5 repetir depois grava uma vez (P2 meta 79)', not painel() and cultivos('S2627')['P2']['meta'] == 79, [painel()[:80], cultivos('S2627')['P2']])
    J("document.getElementById('sl-abrir').click()"); esp(1.2); foca('c5', 'meta'); digita('1'); botao('Dividir T1'); w3 = J("!!document.querySelector('#sl-painel .saida')")
    botao('Descartar alterações'); esp(.6); dvt = J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); return a?a.getAttribute('aria-label'):'';})()")
    chk('G6 "Dividir T1" na linha: com alteração pergunta antes; descartado, abre o painel Dividir existente', w3 and dvt == 'Dividir T1 em parcelas', [w3, dvt])
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); if(b) b.click();})()"); esp(.5)
    chk('G7 sem erro de JavaScript até aqui', not erros(), erros())
    # ---------------- F5 · linhas livres da Safrinha: planejar e duplo clique ----------------
    abrir_saf('saf=S27SF&passo=cultivos')
    J("document.getElementById('sl-abrir').click()"); esp(1.2); pn = painel()
    ro = J("[...document.querySelectorAll('#sl-grade .sl-tit')].map(r=>r.innerText.replace(/\\s+/g,' '))")
    chk('G8 Safrinha 2027: perenes de outra safra (T7 mamão e C1 café) só leitura, com o motivo; talhões livres com a área livre calculada (não digitada)',
        any(t.startswith('T7') and 'Perene · só leitura' in t and 'Mamão Formosa' in t for t in ro) and any(t.startswith('C1') and 'Perene · só leitura' in t and 'Café' in t for t in ro)
        and J(f"{cel('novo:T3','area')}.readOnly") is True and val('novo:T3', 'area') == '96', [ro, val('novo:T3', 'area')])
    cv0 = cultivos('S27SF'); res0 = J("(document.querySelector('#sl-painel b')||{}).innerText") ; r0 = painel()
    marca('novo:T3'); marca('novo:T4'); ap('cult', 'Milho'); ap('var', 'Híbrido AG 8700'); ap('plantio', '2027-03-01'); ap('meta', '175'); ap('plano', 'MILHO-SF'); botao('Aplicar a 2 marcados')
    chk('F5 duas linhas livres marcadas recebem os 5 campos de uma vez; Salvar alterações (10)', salvarT() == 'Salvar alterações (10)' and val('novo:T4', 'plantio') == '2027-03-01', [salvarT(), info()])
    J("(()=>{const b=document.getElementById('sl-salvar'); b.click(); b.click();})()"); esp(1.0); cv1 = cultivos('S27SF')
    novos = [k for k in cv1 if k not in cv0]
    chk('F6 duplo clique no Salvar: grava uma vez (2 cultivos novos, T3 e T4, não 4)', sorted(novos) == ['T3', 'T4'] and len(cv1) == len(cv0) + 2 and cv1['T3']['cult'] == 'Milho' and cv1['T3']['area'] == 96, [novos, len(cv0), len(cv1)])
    J("document.getElementById('sl-abrir').click()"); esp(1.2)
    chk('F7 o resumo da fazenda muda (planejados e livres) e as linhas planejadas passam a cultivo', r0 != painel() and val('novo:T3', 'cult') is None and len([l for l in linhas() if l == 'T3']) == 1, [r0[:200], painel()[:200]])
    botao('Cancelar')
    # ---------------- A4 · várias fazendas e Cartões ----------------
    abrir_saf('saf=S2627&passo=cultivos')
    J("document.getElementById('sfz-add').click()"); esp(.6)
    J("(()=>{const l=[...document.querySelectorAll('#sfz-pop label,#sfz-pop [role=option],#sfz-pop button')].find(x=>/Lagoa Grande/.test(x.innerText)); if(l) l.click();})()"); esp(1.4)
    J("(()=>{const b=[...document.querySelectorAll('#sfz-pop button')].find(b=>b.innerText.trim()==='Fechar'); if(b) b.click();})()"); esp(.5)
    fg = J("[...document.querySelectorAll('[role=row].g2fgrp')].filter(r=>r.offsetParent).map(r=>r.innerText.replace(/\\s+/g,' ').trim())")
    hd = J("!!(document.getElementById('sl-abrir')&&document.getElementById('sl-abrir').offsetParent)")
    chk('A4 com Santa Rita e Lagoa Grande: cada faixa de fazenda tem "Editar talhões ›" (e o título do bloco não repete a ação)', len(fg) == 2 and all(t.endswith('Editar talhões ›') for t in fg) and not hd, [fg, hd])
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2fgrp')].find(r=>/Lagoa Grande/.test(r.innerText)); [...r.querySelectorAll('button')].find(b=>/Editar talhões/.test(b.innerText)).click();})()"); esp(1.8)
    pn = painel(); ro = J("[...document.querySelectorAll('#sl-grade .sl-tit')].map(r=>r.innerText.replace(/\\s+/g,' '))")
    chk('A5 a da Lagoa Grande abre "Editar talhões da Lagoa Grande" na sub-safra dela, com os 23 pivôs; ocupados pelo mamão de outra safra só leitura, com o motivo',
        pn.startswith('Editar talhões da Lagoa Grande') and '23 talhões' in pn and len(ro) == 23 and all('Perene · só leitura' in t and 'Mamão Formosa' in t for t in ro), [pn[:160], ro[:2]])
    botao('Cancelar')
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2fgrp')].find(r=>/Santa Rita/.test(r.innerText)); [...r.querySelectorAll('button')].find(b=>/Editar talhões/.test(b.innerText)).click();})()"); esp(1.8)
    foca('c1', 'area'); digita('150'); botao('Salvar alterações'); esp(.6)
    fg2 = J("[...document.querySelectorAll('[role=row].g2fgrp')].filter(r=>r.offsetParent).map(r=>r.innerText.replace(/\\s+/g,' ').trim())")
    chk('A6 salvar pela faixa da Santa Rita atualiza a faixa da fazenda (1.155 ha · 8 de 8)', bool(fg2) and 'Santa Rita 1.155 ha · 8 de 8 talhões planejados' in fg2[0], fg2)
    J("(()=>{const b=[...document.querySelectorAll('button[aria-label=\"Cartões\"]')].find(b=>b.offsetParent); if(b) b.click();})()"); esp(1.0)
    cl = J("[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&/^Editar talhões/.test(b.innerText.trim())).map(b=>b.innerText.trim())")
    chk('A7 no modo Cartões a faixa de cada fazenda continua com "Editar talhões ›"', J("!!document.querySelector('button[aria-label=\"Cartões\"][aria-pressed=true]')") and cl == ['Editar talhões ›', 'Editar talhões ›'], cl)
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&/^Editar talhões/.test(b.innerText.trim())); b.click();})()"); esp(1.6)
    chk('A8 e abre o mesmo painel pelos Cartões', painel().startswith('Editar talhões da Santa Rita'), painel()[:80])
    c.shot(os.path.join(PROBE, 'saf_lote_1440_painel.png'))
    J("(()=>{const b=[...document.querySelectorAll('button[aria-label=\"Tabela\"]')].find(b=>b.offsetParent); if(b) b.click();})()")
    botao('Cancelar')
    # ---------------- I · INP no motor (formulário do cultivo) ----------------
    abrir_saf('saf=S2627&passo=cultivos')
    J("(()=>{const r=document.querySelector('[role=row][data-rid=c5]')||[...document.querySelectorAll('[role=row].g2ed')].find(r=>/^.?\\s?T3\\b/.test(r.innerText.trim())); (r.querySelector('.g2pw')||r).click();})()"); esp(.8)
    mi = J("(()=>{const e=document.getElementById('fx_g_cult_S2627_meta'); if(!e) return null; e.blur(); e.focus(); return [e.value,e.selectionStart,e.selectionEnd,e.getAttribute('spellcheck'),e.getAttribute('inputmode')];})()")
    chk('I1 formulário do motor: o campo numérico (Meta) recebe o foco com o número selecionado e sem corretor (INP-04, INP-07 no g2lib, todas as telas)', mi and mi[1] == 0 and mi[2] == len(mi[0]) and mi[0] != '' and mi[3] == 'false' and mi[4] == 'decimal', mi)
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); if(b) b.click();})()"); esp(.4)
    # ---------------- H · 390 px ----------------
    abrir_saf('saf=S2627&passo=cultivos', 390)
    hl = J("(()=>{const b=document.getElementById('sl-abrir'); const r=b.getBoundingClientRect(); return [Math.round(r.height),!!b.offsetParent];})()")
    J("document.getElementById('sl-abrir').click()"); esp(1.6)
    m = J("""(()=>{const a=document.getElementById('sl-painel'); const vis=e=>e.offsetParent!==null&&getComputedStyle(e).display!=='none';
      const alvos=[...a.querySelectorAll('input:not([type=checkbox]),select,button,label.sl-s')].filter(vis).map(e=>{const r=e.getBoundingClientRect(); return [e.getAttribute('aria-label')||e.innerText.trim().slice(0,24),Math.round(r.height)];});
      const pe=a.querySelector('.sl-pe').getBoundingClientRect(); return {pag:[document.documentElement.scrollWidth,innerWidth],pn:[a.scrollWidth,a.clientWidth],menores:alvos.filter(x=>x[1]<44),n:alvos.length,cab:getComputedStyle(a.querySelector('.sl-cab')).display,
        pe:[Math.round(pe.bottom),innerHeight],apCampos:[...a.querySelectorAll('.sl-ap .sl-c')].filter(vis).length,ativo:document.activeElement&&document.activeElement.tagName};})()""")
    chk('H1 390 px: "Editar talhões…" com 44 px; painel sem rolagem de lado (página e painel), cabeçalho de colunas trocado por rótulos em cada campo, foco não abre o teclado',
        hl == [44, True] and m['pag'][0] <= m['pag'][1] and m['pn'][0] <= m['pn'][1] and m['cab'] == 'none' and m['ativo'] != 'INPUT', [hl, m])
    chk('H2 390 px: todo campo, lista, botão e caixa de marcar com alvo de 44 px ou mais', m['n'] > 40 and not m['menores'], m['menores'][:8])
    J("document.getElementById('sl-painel').scrollTop=900"); esp(.4)
    pe2 = J("(()=>{const r=document.querySelector('#sl-painel .sl-pe').getBoundingClientRect(); return [Math.round(r.top),Math.round(r.bottom),innerHeight];})()")
    chk('H3 390 px: barra de salvar fixa à vista no meio da lista; faixa "Aplicar" sem campos até marcar uma linha', pe2[1] <= pe2[2] and pe2[0] < pe2[2] and m['apCampos'] == 0, [pe2, m['apCampos']])
    c.shot(os.path.join(PROBE, 'saf_lote_390_lista.png'))
    J("document.getElementById('sl-painel').scrollTop=0"); marca('c5'); n1 = J("[...document.querySelectorAll('#sl-painel .sl-ap .sl-c')].filter(e=>e.offsetParent).length")
    chk('H4 390 px: marcada uma linha, a faixa mostra os campos (cultura, variedade, plantio, meta e plano)', n1 == 5, n1)
    c.shot(os.path.join(PROBE, 'saf_lote_390_aplicar.png'))
    foca('c5', 'meta'); digita('71'); botao('Salvar alterações'); esp(.6)
    chk('H5 390 px: editar e salvar pelo celular', cultivos('S2627')['T3']['meta'] == 71 if cultivos('S2627') else False, cultivos('S2627').get('T3'))
    J("document.getElementById('sfz-add').click()"); esp(.6)
    J("(()=>{const l=[...document.querySelectorAll('#sfz-pop label,#sfz-pop [role=option],#sfz-pop button')].find(x=>/Lagoa Grande/.test(x.innerText)); if(l) l.click();})()"); esp(1.4)
    J("(()=>{const b=[...document.querySelectorAll('#sfz-pop button')].find(b=>b.innerText.trim()==='Fechar'); if(b) b.click();})()"); esp(.5)
    mm = J("""(()=>{const r=[...document.querySelectorAll('[role=row].g2fgrp')].find(r=>r.offsetParent&&/Lagoa Grande/.test(r.innerText)); if(!r) return null;
      const lk=[...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Editar talhões ›'); const m=r.querySelector('[aria-label^="Mais ações"]'); const q=m?m.getBoundingClientRect():null;
      const lq=lk?lk.getBoundingClientRect():null; return {lk:!!(lk&&lk.offsetParent),lkAlt:lq?Math.round(lq.height):null,mais:m?[Math.round(q.width),Math.round(q.height)]:null};})()""")
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2fgrp')].find(r=>r.offsetParent&&/Lagoa Grande/.test(r.innerText)); r.scrollIntoView({block:'center'});})()"); esp(.3); c.shot(os.path.join(PROBE, 'saf_lote_390_faixa.png'))
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2fgrp')].find(r=>r.offsetParent&&/Lagoa Grande/.test(r.innerText)); r.querySelector('[aria-label^=\"Mais ações\"]').click();})()"); esp(.5)
    it = J("[...document.querySelectorAll('[role=menuitem]')].filter(x=>x.offsetParent).map(x=>x.innerText.trim())")
    J("(()=>{const b=[...document.querySelectorAll('[role=menuitem]')].find(x=>x.offsetParent&&/^Editar talhões/.test(x.innerText.trim())); if(b) b.click();})()"); esp(1.8)
    # o link da linha e o ⋯ são peças do motor (estilo de link da célula e menu da linha, TAB-05): a altura é medida e registrada, não exigida aqui
    print(f"     (medido) 390 px, faixa da fazenda: link 'Editar talhões ›' {mm and mm.get('lkAlt')} px de altura; ⋯ {mm and mm.get('mais')} px", flush=True)
    chk('H7 390 px com duas fazendas: "Editar talhões ›" à vista na faixa e também no ⋯ da faixa ("Editar talhões da Lagoa Grande"), que abre o painel da fazenda', mm and mm['lk'] and mm['mais']
        and any(x.startswith('Editar talhões') for x in (it or [])) and painel().startswith('Editar talhões da Lagoa Grande'), [mm, it, painel()[:60]])
    chk('H6 sem erro de JavaScript', not erros(), erros())
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {"OK" if not falhas else "FALHOU"} {ok_n}/{ok_n + len(falhas)}' + (' · falhas: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
