# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO-20261004 v2 (5983172395), Cadastros (CD-01..CD-07 e CD-01det): uma variável por coluna.
TF03 por grade: colunas próprias (sem rótulo composto), unidade junto do valor nas colunas com data-un ("160,0 ha", "R$ 14,49/ha"),
"Custo R$/h" e "Custo R$/ha", filtro e ordenação em todas as colunas, filtro pelo texto da célula, ordem pelo número e pela data,
Situação em chip; 390 px rolando dentro da caixa. Defeitos reproduzidos: outorga aparecia como "Certidão" (CD-01 Água) e a Safra Mamão
da Lagoa Grande aparecia nas parcelas de talhão da Santa Rita (CD-01det). Fluxo do cadastro na grade (CD-03), a 1440 e a 390 px (toque): normal
(salvar o custo e a célula/ordem acompanham), recusa (número inválido não grava) e repetição (salvar de novo não duplica). Vazio continua vazio.
Revisão TABR (09/10/2026): a Situação logo depois da identificação, à vista sem rolar a 1440 e a 1280 px, e as grades cabem na caixa a
1440 px (A1; CD-05 rola só os contatos); capacidade só numa grandeza (CD-03 pelo filtro de Classe, CD-06 pelo filtro Tanque/Silo; A4);
o filtro marcado continua no menu do papel (A5); motivo e verbo da pessoa não alocável e o "Disponível até" vencido em vermelho (A3);
"No rascunho" só com rascunho (A8); calibração a vencer no chip (A10); fonte do rendimento em texto, não chip de estado (A11); a vazão
ordena em m³/h (mutante M-a: tabelas_cad_irr_unit B1 e B1b; a ordem na tela não distingue com os valores do cenário) e a capacidade da classe Irrigação aparece (mutante M-k);
o detalhe do PV01 (Lagoa Grande) mostra a parcela que a lista conta (pré-existente). Colunas que entram e saem (CD-05 papel, CD-03 Classe,
CD-06 Tanque/Silo) ficam sob os cabeçalhos e o cabeçalho não quebra linha (mutante M-e: sem ncol_dinamico a trilha fica menor e cabeçalho e
células quebram juntos; desalinhadas() pega pela ordem das bordas, sonda de 10/10/2026).
TABR-CTX-01 (revisão do Codex, 10/10/2026): a coluna de capacidade muda de grandeza com o filtro; o filtro, a ordem e o menu de filtro dela
saem quando a grandeza muda ou a coluna sai (CD-03: Trator · Potência 78 cv → limpar só Classe → Irrigação; CD-06: Tanque · 15.000 L → Silo →
Todos) e ficam com a mesma grandeza (Tratamento de sementes → Beneficiamento, kg/h); busca, outros filtros e foco ficam. A 1440 e a 390 px,
por clique e só pelo teclado (Tab, Enter e Espaço no menu de filtro e nos chips). Revisão do TABR-CTX-01 (10/10/2026): a cada vez que a
coluna de capacidade entra, muda ou sai, a grade tem uma trilha por cabeçalho e nenhuma linha fora dela (a 390 px a 1ª coluna presa do
g2lib guardava o nº de colunas da abertura e a última coluna caía para a linha de baixo; a 1440 px não há coluna presa).
TABR-CTX-02 (reverificação do TABR-CTX-01, 10/10/2026): o menu de filtro da coluna de capacidade só oferece números da grandeza dela (CD-03
Trator, Irrigação e Armazenagem; CD-06 Tanque e Silo) e escolher cada um mostra a linha dele (antes "300 cv", a vazão da bomba, e a lista vazia);
mesmo rótulo com outra unidade (Armazenagem, Capacidade em sc de 60 kg → Tratamento de sementes, em kg/h) tira o filtro e a ordem; o × da
Classe leva o foco à busca só pelo teclado (no toque e no mouse, não: no celular abriria o teclado).
Uso: python3 tabelas_cad_test.py [pasta de capturas]   (~6 min) · python3 tabelas_cad_test.py --ctx [pasta]: só o TABR-CTX-01 e o TABR-CTX-02"""
import sys, os, re, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, cv_todas_sempre
from tabelas_lib import Grade, limpa, num, un_ok, instante, crescente
CTX = '--ctx' in sys.argv; ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = ARGS[0] if ARGS else None
if OUT: os.makedirs(OUT, exist_ok=True)
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ') + n + (' · ' + str(info)[:300] if info != '' else ''), flush=True)

p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js; cv_todas_sempre(c)   # V2-3: a tabela completa como foi desenhada (TABELAS-FOCO); o padrão é conferido na VISOES-2
def shot(n):
    if OUT: c.shot(os.path.join(OUT, n + '.png'))
ERRS = []
def abre(pg, w=1.4):
    try: e = J("window.__errs") or []
    except Exception: e = []
    ERRS.extend(e); c.goto(f'http://127.0.0.1:{p}/{pg}', w)
def aba(nome):
    r = J(f"(()=>{{const b=[...document.querySelectorAll('[role=tab]')].find(b=>b.offsetParent&&b.innerText.trim().startsWith({json.dumps(nome)})); if(!b) return false; b.click(); return true;}})()"); time.sleep(.6); return r
def grupos(g):
    """linhas da árvore com a marca de grupo (linha com seta)."""
    return J(f"[...([...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent))[{g.i}].querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).map(r=>[!!r.querySelector('button[aria-label^=\"Expandir\"],button[aria-label^=\"Recolher\"]'),[...r.querySelectorAll('[role=cell]')].map(x=>x.innerText.replace(/\\s+/g,' ').replace(/^[▸▾]\\s*/,'').trim())])") or []
def por_grupo(g, col):
    """valores da coluna nas folhas, um bloco por grupo (a árvore ordena dentro do nível)."""
    hs = g.labels(); k = hs.index(col); out = []; cur = None
    for grp, cells in grupos(g):
        if grp: cur = []; out.append(cur)
        elif cur is not None: cur.append(cells[k])
    return [b for b in out if len(b) > 1]
def tf03(nome, g, esperado, ficha=False, extra=()):
    """TF03 da grade: colunas exatas, uma variável por coluna, filtro e ordem em todas, unidade junto do valor, situação em chip."""
    hs = g.heads(); ls = [h for h, _ in hs]
    chk(f'{nome}: colunas {" | ".join(esperado)}', ls == esperado, ls)
    chk(f'{nome}: nenhum rótulo composto (" · ", " / ") e custo como "Custo R$/h"/"Custo R$/ha"',
        not any(' · ' in h or ' / ' in h for h in ls) and all(h.startswith('Custo R$/') for h, u in hs if u.startswith('R$/')), ls)
    if not ficha:
        m = g.com_menu(); chk(f'{nome}: filtro (▾) e ordenação no título em todas as {len(m)} colunas', m and all(m), m)
    d = g.dicts(); ruins = [(h, r.get(h)) for h, u in hs if u for r in d if not un_ok(r.get(h, ''), u, extra)]
    chk(f'{nome}: unidade junto do valor nas colunas com unidade ({", ".join(h + " " + u for h, u in hs if u) or "nenhuma"})', not ruins, ruins[:4])
    if 'Situação' in ls or 'Situação do papel' in ls:
        col = 'Situação' if 'Situação' in ls else 'Situação do papel'; ch = [x for x in g.chips(col) if x is not None]
        chk(f'{nome}: {col} em chip em todas as linhas com valor ({len(ch)})', ch and all(ch), g.chips(col)[:6])
    return d

def fluxo_custo(g, tam, val, cel):
    """CD-03: salvar o custo do Trator 03 → célula e ordem por custo acompanham (normal); "abc" mostra "Use um número" e não grava (recusa);
    salvar de novo sem mudar não duplica a linha nem muda o valor (repetição)."""
    def abre_linha(nome): J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf({json.dumps(nome)})===0); r&&r.querySelector('[role=cell] span').click();}})()"); time.sleep(.5)
    def campo(fid, v): J(f"""(()=>{{const i=document.querySelector('#{fid}'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(v)}); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"""); time.sleep(.2)
    def salvar(): J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); time.sleep(.6)
    linha = lambda: next((r for r in g.dicts() if r.get('Máquina ou instalação') == 'Trator 03'), {})
    abre_linha('Trator 03'); campo('fx_g_atv_custo_h', val); salvar(); t3 = linha()
    g.ordena('Custo R$/h', desc=True); ordem = [r.get('Máquina ou instalação') for r in g.dicts()]; ch = [num(x) for x in g.col('Custo R$/h') if x != '—']
    chk(f'CD-03 fluxo {tam} (normal): salvar {val} → célula "{cel}" e a ordem por custo põe o Trator 03 entre os de 180 e os de 150',
        t3.get('Custo R$/h') == cel and crescente(ch, True) and ordem.index('Trator 03') == ordem.index('Trator 02') + 1, (t3.get('Custo R$/h'), ordem[:6]))
    abre_linha('Trator 03'); campo('fx_g_atv_custo_h', 'abc'); salvar()
    err = J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or ''
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Descartar alterações'); b&&b.click();})()"); time.sleep(.3)
    chk(f'CD-03 fluxo {tam} (recusa): custo "abc" mostra "Use um número" e não grava (célula segue {cel})', 'Use um número' in err and linha().get('Custo R$/h') == cel, (err[-160:], linha().get('Custo R$/h')))
    abre_linha('Trator 03'); salvar(); n3 = [r.get('Máquina ou instalação') for r in g.dicts()].count('Trator 03')
    chk(f'CD-03 fluxo {tam} (repetição): salvar de novo sem mudar não duplica a linha nem muda o valor', n3 == 1 and linha().get('Custo R$/h') == cel, n3)

# ---------- TABR-CTX-01: a coluna de capacidade muda de grandeza; o filtro, a ordem e o menu dela não sobram (clique e teclado) ----------
RF = 'button[aria-label="Remover filtro"]'
def fchips():
    return J(f"[...document.querySelectorAll('{RF}')].filter(b=>b.offsetParent).map(b=>b.parentElement.innerText.replace(/\\s*×\\s*$/,'').trim())") or []
def foco():
    """[aria-label, texto] do elemento com foco (do chip, quando é o × de um filtro); BODY quando o foco se perdeu."""
    return J("""(()=>{const a=document.activeElement; if(!a||a===document.body) return ['BODY',''];
      const l=a.getAttribute('aria-label')||''; return [l,(l==='Remover filtro'?a.parentElement.innerText.replace(/\\s*×\\s*$/,''):(a.innerText||a.value||'')).replace(/\\s+/g,' ').trim()];})()""") or ['', '']
def menu_aberto():
    return J("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].find(d=>/^Filtrar /.test(d.getAttribute('aria-label')||'')); return d?[d.getAttribute('aria-label'),[...d.querySelectorAll('label')].map(l=>[l.innerText.replace(/\\s+\\d+$/,'').trim(),l.querySelector('input').checked])]:null;})()")
def seta(col):
    return J(f"(()=>{{const b=[...document.querySelectorAll('button[aria-label=\"Ordenar por {col}\"]')].find(x=>x.offsetParent); const sp=b&&b.querySelector('span[aria-hidden=true]'); return sp?sp.innerText.trim():'';}})()") or ''
def busca_val():
    return J("(([...document.querySelectorAll('input[aria-label=\"Buscar nesta tabela\"]')].find(x=>x.offsetParent))||{}).value") or ''
ENTER = lambda: c.tecla('Enter', 'Enter', 13, text='\r')
ESPACO = lambda: c.tecla(' ', 'Space', 32, text=' ')
def digita(t):
    for ch in t: c.tecla(ch, ('Key' + ch.upper()) if ch.isalpha() else (('Digit' + ch) if ch.isdigit() else ch), 0, text=ch)
def foca(sel):
    """ponto de partida da navegação por teclado (o resto anda com Tab, Enter e Espaço)."""
    J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps(sel)})].find(x=>x.offsetParent); b&&b.focus();}})()"); time.sleep(.1)
def tab_ate(pred, shift=False, n=30):
    for _ in range(n):
        c.tab(1, shift)
        if J(f"(()=>{{const a=document.activeElement; return !!a&&a!==document.body&&({pred})(a);}})()"): return True
    return False
def menu_tecla(col, busca, valor):
    """filtro pelo menu da coluna só com o teclado: Enter no ▾ abre com o foco na pesquisa; Shift+Tab até "Limpar" e Espaço desmarca tudo;
    Tab volta à pesquisa e digita; Tab vai ao valor e Espaço marca; Shift+Tab e Enter na pesquisa aplicam (é o OK)."""
    foca(f'button[aria-label="Filtrar {col}"]'); ENTER(); time.sleep(.45)
    c.tab(1, True); ESPACO(); time.sleep(.2); c.tab(); digita(busca); time.sleep(.3); c.tab()
    lab = J("(()=>{const l=document.activeElement&&document.activeElement.closest('label'); return l?l.innerText.replace(/\\s+\\d+$/,'').trim():'';})()")
    ESPACO(); time.sleep(.2); c.tab(1, True); ENTER(); time.sleep(.5); return lab == valor
def ordena_tecla(col):
    """↓ maior para menor pelo teclado: Enter no ▾, Shift+Tab até "↓ Classificar…" (no máximo 6; a V2-3 pôs "Ocultar coluna" no caminho) e Espaço
    (Enter no menu é o OK do filtro)."""
    foca(f'button[aria-label="Filtrar {col}"]'); ENTER(); time.sleep(.45)
    for _ in range(6):
        c.tab(1, True)
        if (J("document.activeElement.innerText") or '').startswith('↓'): break
    ok = (J("document.activeElement.innerText") or '').startswith('↓'); ESPACO(); time.sleep(.5); return ok
def tira_chip(pref, tec):
    """o × do chip do filtro (Classe): pelo teclado, Tab a partir da busca até ele e Enter; por clique, o clique nele."""
    if tec:
        foca('input[aria-label="Buscar nesta tabela"]')
        ok = tab_ate(f"a=>a.getAttribute('aria-label')==='Remover filtro'&&a.parentElement.innerText.trim().startsWith({json.dumps(pref)})"); ENTER(); time.sleep(.5); return ok
    J(f"(()=>{{const b=[...document.querySelectorAll('{RF}')].find(b=>b.offsetParent&&b.parentElement.innerText.trim().startsWith({json.dumps(pref)})); b&&b.click();}})()"); time.sleep(.5); return True
def qf(t, tec, shift=False):
    """filtro rápido (Tanque, Silo, Todos): pelo teclado, Tab (ou Shift+Tab, de dentro do menu aberto) até o botão e Enter; por clique, o clique."""
    pred = f"a=>!!a.closest('[role=group][aria-label^=\"Filtro rápido\"]')&&a.innerText.trim().startsWith({json.dumps(t)})"
    if tec:
        if not shift: foca('input[aria-label="Buscar nesta tabela"]')
        ok = tab_ate(pred, shift); ENTER(); time.sleep(.5); return ok
    J(f"[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"] button')].filter(b=>b.offsetParent).find(b=>b.innerText.trim().startsWith({json.dumps(t)})).click()"); time.sleep(.5); return True
def trilha(g, estado):
    """[estado, trilhas do grid, cabeçalhos, linhas fora da trilha (desalinhadas)] da grade g: a trilha acompanha a coluna que entra e sai.
    Mede com a caixa no início da rolagem lateral (com ela rolada, a 1ª coluna presa fica à esquerda das outras e desalinhadas() contaria o
    cabeçalho; o teclado rola a caixa até o controle focado) e devolve a rolagem como estava."""
    T_ = f"([...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent))[{g.i}]"
    t = J(f"(()=>{{const t={T_}; const r=t.closest('.g2rola'); window.__sl=r?r.scrollLeft:0; if(r) r.scrollLeft=0; return [getComputedStyle(t).gridTemplateColumns.split(' ').length, t.querySelector('[role=row]').querySelectorAll('[role=columnheader]').length];}})()") or [0, -1]
    time.sleep(.15); d = g.desalinhadas(); J(f"(()=>{{const r={T_}.closest('.g2rola'); if(r) r.scrollLeft=window.__sl||0;}})()"); time.sleep(.1)
    return [estado] + t + [d]
def ctx01(tam, tec):
    """TABR-CTX-01 no CD-03 e no CD-06 (roteiro do Codex). tec: só teclado; senão, clique (toque a 390 px)."""
    m = f'TABR-CTX-01 {tam} ' + ('teclado' if tec else 'clique')
    def busca(t):
        if tec: foca('input[aria-label="Buscar nesta tabela"]'); digita(t); time.sleep(.4); return
        J(f"""(()=>{{const i=[...document.querySelectorAll('input[aria-label="Buscar nesta tabela"]')].find(x=>x.offsetParent); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(t)});
          i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.4)
    def filtra(col, busca_, val):
        return menu_tecla(col, busca_, val) if tec else g.filtra(col, [val])
    def ordena(col):
        return ordena_tecla(col) if tec else g.ordena(col, desc=True)
    nomes = lambda: [r.get(g.labels()[0]) for r in g.dicts()]
    # ---- CD-03: Trator · Potência = 78 cv (busca "o" e Situação = Apta) → limpar só Classe → Irrigação ----
    abre('CD-03.dc.html'); g = Grade(J, 0); CD3 = ['Máquina ou instalação', 'Situação', 'Classe', 'Custo R$/h', 'Conjuntos', 'Próxima calibração']
    busca('o'); prep = [filtra('Situação', 'Apta', 'Apta'), filtra('Classe', 'Trator', 'Trator'), filtra('Potência', '78', '78 cv'), ordena('Potência')]
    r0, c0 = nomes(), fchips(); al3 = [trilha(g, 'Trator')]
    chk(f'{m} CD-03: Situação Apta + Trator + Potência 78 cv (↓) → só o Trator 04, com os três chips', all(prep) and r0 == ['Trator 04'] and c0 == ['Situação: Apta', 'Classe: Trator', 'Potência: 78 cv'] and seta('Potência') == '▼', (prep, r0, c0))
    tira_chip('Classe:', tec); c1, l1, f1, r1 = fchips(), g.labels(), foco(), nomes(); al3.append(trilha(g, 'sem Classe'))
    chk(f'{m} CD-03: limpar só a Classe tira a coluna e o filtro da Potência (sem chip "capn: 78 cv"); a busca "o" e a Situação ficam'
        + ('; o foco fica no chip que sobra (Situação), não se perde' if tec else ''),
        c1 == ['Situação: Apta'] and l1 == CD3 and busca_val() == 'o' and 'Gotejo T7' in r1 and 'Trator 02' in r1 and (not tec or f1 == ['Remover filtro', 'Situação: Apta']), (c1, l1, busca_val(), f1, len(r1)))
    filtra('Classe', 'Irriga', 'Irrigação'); c2, h2, r2 = fchips(), g.heads(), nomes(); al3.append(trilha(g, 'Irrigação'))
    chk(f'{m} CD-03: Classe = Irrigação → coluna Vazão em m³/h sem filtro nem ordem de outra grandeza (antes "Vazão: 78 cv" e lista vazia); as bombas/setores aptos à vista',
        sorted(c2) == ['Classe: Irrigação', 'Situação: Apta'] and [h for h, _ in h2] == CD3[:3] + ['Vazão'] + CD3[3:] and dict(h2).get('Vazão') == 'm³/h'
        and r2 == ['Bomba do Pivô 1', 'Gotejo T7'] and seta('Vazão') == '⇅' and busca_val() == 'o', (c2, h2, r2, seta('Vazão')))
    shot(f'ctx01-cd03-{tam.split()[0]}-{"teclado" if tec else "clique"}')
    # ---- CD-03: mesma grandeza (Capacidade kg/h): Tratamento de sementes · 2.400 kg/h (↓) → Beneficiamento mantém filtro e ordem ----
    abre('CD-03.dc.html'); g = Grade(J, 0)
    prep = [filtra('Classe', 'Tratamento', 'Tratamento de sementes'), filtra('Capacidade', '2.400', '2.400 kg/h'), ordena('Capacidade')]; r3 = nomes(); al3.append(trilha(g, 'Tratamento de sementes'))
    filtra('Classe', 'Benefic', 'Beneficiamento'); c4, h4, r4 = fchips(), g.heads(), nomes(); al3.append(trilha(g, 'Beneficiamento'))
    chk(f'{m} CD-03: mesma grandeza e unidade (kg/h): Tratamento de sementes · 2.400 kg/h → Beneficiamento mantém o filtro e a ordem (Packing linha 1)',
        all(prep) and r3 == ['Máquina TSI'] and sorted(c4) == ['Capacidade: 2.400 kg/h', 'Classe: Beneficiamento'] and dict(h4).get('Capacidade') == 'kg/h' and r4 == ['Packing linha 1'] and seta('Capacidade') == '▼',
        (prep, r3, c4, h4, r4, seta('Capacidade')))
    # ---- CD-03: mesmo rótulo, outra unidade (TABR-CTX-02): Armazenagem · 60.000 sc de 60 kg (↓) → Tratamento de sementes (Capacidade kg/h) ----
    prep = [filtra('Classe', 'Armaze', 'Armazenagem'), filtra('Capacidade', '60.000', '60.000 sc de 60 kg'), ordena('Capacidade')]; r5, c5 = nomes(), fchips(); al3.append(trilha(g, 'Armazenagem'))
    filtra('Classe', 'Tratamento', 'Tratamento de sementes'); c6, h6, r6 = fchips(), g.heads(), nomes(); al3.append(trilha(g, 'Tratamento de sementes (de sc)'))
    chk(f'{m} CD-03: mesmo rótulo com outra unidade: Armazenagem · Capacidade 60.000 sc de 60 kg (↓) → Tratamento de sementes tira o filtro e a ordem em sc '
        '(Capacidade em kg/h e a Máquina TSI à vista; sem "Capacidade: 60.000 sc de 60 kg" e lista vazia)',
        all(prep) and r5 == ['Silo 01'] and sorted(c5) == ['Capacidade: 60.000 sc de 60 kg', 'Classe: Armazenagem'] and c6 == ['Classe: Tratamento de sementes']
        and dict(h6).get('Capacidade') == 'kg/h' and r6 == ['Máquina TSI'] and seta('Capacidade') == '⇅', (prep, r5, c5, c6, h6, r6, seta('Capacidade')))
    chk(f'{m} CD-03: a coluna de capacidade entra (Trator), sai (sem Classe), muda (Irrigação) e volta (kg/h) com uma trilha por cabeçalho e cada célula sob o seu cabeçalho'
        + (' (antes, a 390 px, 6 trilhas para 7 cabeçalhos e a Próxima calibração na linha de baixo)' if tam != '1440' else ''),
        all(x[1] == x[2] and x[3] == 0 for x in al3), al3)
    # ---- CD-06 Locais: Tanque · 15.000 L (↓) → Silo (pelo teclado, com o menu da Capacidade aberto e o rascunho desmarcado) → 60.000 sc → Todos ----
    abre('CD-06.dc.html'); aba('Locais'); g = Grade(J, 0)
    busca('Santa'); prep = [filtra('Fazenda', 'Santa', 'Santa Rita'), qf('Tanque', tec), filtra('Capacidade', '15.000', '15.000 L'), ordena('Capacidade')]
    r5, c5 = nomes(), fchips(); al6 = [trilha(g, 'Tanque')]
    chk(f'{m} CD-06: Santa Rita + Tanque + Capacidade 15.000 L (↓) → só o Tanque Sede', all(prep) and r5 == ['Tanque Sede'] and c5 == ['Fazenda: Santa Rita', 'Capacidade: 15.000 L'], (prep, r5, c5))
    if tec:   # o menu da Capacidade aberto com o rascunho desmarcado; Shift+Tab sai do menu até o "Silo" do filtro rápido e Enter
        foca('button[aria-label="Filtrar Capacidade"]'); ENTER(); time.sleep(.45); c.tab(1, True); ESPACO(); time.sleep(.2)
        ok = qf('Silo', True, shift=True)
    else: ok = qf('Silo', False)
    c6, h6, r6, mn, f6 = fchips(), g.heads(), nomes(), menu_aberto(), foco(); al6.append(trilha(g, 'Silo'))
    chk(f'{m} CD-06: Tanque → Silo tira o filtro e a ordem em L (antes "Capacidade: 15.000 L" e lista vazia); Silo 01 em sc de 60 kg; Fazenda e busca ficam'
        + ('; o menu da Capacidade com o rascunho de L fecha e o foco fica no "Silo"' if tec else ''),
        ok and c6 == ['Fazenda: Santa Rita'] and dict(h6).get('Capacidade') == 'sc de 60 kg' and r6 == ['Silo 01'] and seta('Capacidade') == '⇅' and busca_val() == 'Santa'
        and (not tec or (mn is None and f6[1].startswith('Silo'))), (ok, c6, h6, r6, mn, f6))
    filtra('Capacidade', '60.000', '60.000 sc de 60 kg'); r7 = nomes(); qf('Todos', tec); c8, l8, r8 = fchips(), g.labels(), nomes(); al6.append(trilha(g, 'Todos'))
    chk(f'{m} CD-06: Silo · 60.000 sc → Todos tira a coluna sem chip órfão ("capn: …"); Tanque Sede e Silo 01 voltam com a Fazenda e a busca',
        r7 == ['Silo 01'] and c8 == ['Fazenda: Santa Rita'] and 'Capacidade' not in l8 and {'Tanque Sede', 'Silo 01'} <= set(r8) and busca_val() == 'Santa', (r7, c8, l8, r8))
    chk(f'{m} CD-06 Locais: a Capacidade entra (Tanque), muda (Silo) e sai (Todos) com uma trilha por cabeçalho e cada célula sob o seu cabeçalho'
        + (' (antes, a 390 px, 4 trilhas para 5 cabeçalhos e "Itens com este local padrão" na linha de baixo)' if tam != '1440' else ''),
        all(x[1] == x[2] and x[3] == 0 for x in al6), al6)
    shot(f'ctx01-cd06-{tam.split()[0]}-{"teclado" if tec else "clique"}')

# ---------- TABR-CTX-02: o menu de filtro da coluna de capacidade só oferece valores da grandeza dela; cada um mostra a sua linha ----------
def ctx02_menu(tam, tec):
    """Antes (a2e9a9b): com Classe = Trator o menu da Potência oferecia 11 números ("300 cv" é a vazão da bomba, "60.000 cv" as sacas do silo),
    e no CD-06 Tanque o da Capacidade oferecia "60.000 L" (o silo); escolher um deles dava "0 de 15" e a lista vazia. Agora o menu só tem os
    números das linhas da classe (ou do tipo) da coluna; nas outras linhas a célula é vazia ("(vazio)", como em qualquer coluna sem valor).
    Escolher cada número, pelo clique ou só pelo teclado, mostra a linha dele."""
    m = f'TABR-CTX-02 {tam} ' + ('teclado' if tec else 'clique')
    def vals(col):
        if not tec: return g.rotulos(col)
        foca(f'button[aria-label="Filtrar {col}"]'); ENTER(); time.sleep(.45); r = menu_aberto(); c.tecla('Escape', 'Escape', 27); time.sleep(.35)
        return [x for x, _ in (r[1] if r else [])]
    def filtra(col, val):
        return menu_tecla(col, 'vazio' if val == '(vazio)' else val.split(' ')[0], val) if tec else g.filtra(col, [val])
    nomes = lambda: [r.get(g.labels()[0]) for r in g.dicts()]
    def cada(onde, col, esperado):
        """os números do menu da coluna são exatamente os esperados; escolher cada número oferecido mostra só a linha dele, nunca a lista vazia."""
        vs = [x for x in vals(col) if x != '(vazio)']; res = []
        for x in vs: ok = filtra(col, x); res.append((x, ok, nomes()))
        chk(f'{m} {onde}: o menu {col} oferece só {", ".join(esperado)} (sem número de outra grandeza com a unidade da coluna) e cada um mostra a sua linha',
            vs == list(esperado) and all(ok and r == [esperado.get(x)] for x, ok, r in res), (vs, [r for r in res if not (r[1] and r[2] == [esperado.get(r[0])])][:4]))
    sel_classe = lambda cl: menu_tecla('Classe', cl[:6], cl) if tec else g.filtra('Classe', [cl])
    # ---- CD-03: Trator (Potência cv), Irrigação (Vazão m³/h), Armazenagem (Capacidade sc de 60 kg) ----
    abre('CD-03.dc.html'); g = Grade(J, 0)
    sel_classe('Trator'); cada('CD-03 Classe = Trator', 'Potência', {'78 cv': 'Trator 04', '110 cv': 'Trator 03', '155 cv': 'Trator T1', '190 cv': 'Trator 02'})
    # vazões da fonte única da Irrigação desde a v56 (dados_cad.py: Pivô 1 = 540, Pivô 2 = a da ficha do pivô, Gotejo T7 = 838,8 m³/h)
    sel_classe('Irrigação'); cada('CD-03 Classe = Irrigação', 'Vazão', {'540 m³/h': 'Bomba do Pivô 1', '597,6 m³/h': 'Bomba do Pivô 2', '838,8 m³/h': 'Gotejo T7'})
    sel_classe('Armazenagem'); cada('CD-03 Classe = Armazenagem', 'Capacidade', {'60.000 sc de 60 kg': 'Silo 01'})
    shot(f'ctx02-cd03-{tam.split()[0]}-{"teclado" if tec else "clique"}')
    # ---- CD-06 Locais: Tanque (Capacidade L), Silo (Capacidade sc de 60 kg) ----
    abre('CD-06.dc.html'); aba('Locais'); g = Grade(J, 0)
    qf('Tanque', tec); cada('CD-06 Locais · Tanque', 'Capacidade', {'15.000 L': 'Tanque Sede'})
    qf('Silo', tec); cada('CD-06 Locais · Silo', 'Capacidade', {'60.000 sc de 60 kg': 'Silo 01'})
    shot(f'ctx02-cd06-{tam.split()[0]}-{"teclado" if tec else "clique"}')

def toca(expr, toque):
    """toque real (CDP touch) ou clique real do mouse no centro do elemento: o botão recebe o foco como no aparelho (o .click() do JS não foca)."""
    r = J(f"(()=>{{const e=({expr}); if(!e) return null; e.scrollIntoView({{block:'center',inline:'nearest'}}); const r=e.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2];}})()")
    if not r: return False
    time.sleep(.15); x, y = r
    if toque: c.toque(x, y)
    else: c.mouse(x, y); c.mouse(x, y, 'mousePressed', 'left'); c.mouse(x, y, 'mouseReleased', 'left')
    time.sleep(.5); return True
def ctx02_foco(tam):
    """TABR-CTX-02 (S4 da reverificação): tirar a Classe pelo × quando só havia ela e o filtro de capacidade (os dois chips somem). Pelo teclado o
    foco vai à busca da grade (não se perde no corpo da página); pelo toque ou pelo mouse ele não vai ao campo de texto (no celular, o foco
    programático num campo de texto abre o teclado sem a pessoa pedir). Antes (a2e9a9b) ia à busca também no toque e no clique."""
    toque = tam != '1440'; m = f'TABR-CTX-02 {tam}'
    def prep():
        abre('CD-03.dc.html'); g = Grade(J, 0); ok = g.filtra('Classe', ['Trator']) and g.filtra('Potência', ['78 cv'])
        J("document.activeElement&&document.activeElement.blur()"); time.sleep(.1); return bool(ok) and fchips() == ['Classe: Trator', 'Potência: 78 cv']
    tag = lambda: J("(document.activeElement||document.body).tagName")
    X = f"[...document.querySelectorAll('{RF}')].find(b=>b.offsetParent&&b.parentElement.innerText.trim().startsWith('Classe:'))"
    p1 = prep(); t = toca(X, toque); time.sleep(.3); c1, f1, t1 = fchips(), foco(), tag()
    chk(f'{m} CD-03: Classe = Trator + Potência 78 cv; o × da Classe pelo {"toque" if toque else "mouse"} tira os dois chips e não leva o foco ao campo "Buscar nesta tabela"',
        p1 and t and c1 == [] and f1[0] != 'Buscar nesta tabela' and t1 not in ('INPUT', 'TEXTAREA'), (p1, t, c1, f1, t1))
    p2 = prep(); ok = tira_chip('Classe:', True); time.sleep(.3); c2, f2 = fchips(), foco()
    chk(f'{m} CD-03: o mesmo × pelo teclado (Tab e Enter) leva o foco à busca da grade, sem se perder no corpo da página',
        p2 and ok and c2 == [] and f2[0] == 'Buscar nesta tabela', (p2, ok, c2, f2))

class _SoCtx(Exception): pass   # --ctx: só o TABR-CTX-01 e o TABR-CTX-02 (os dois tamanhos, clique e teclado)
try:
    if CTX:
        for w, h, e, t, tam in ((1440, 900, 1, False, '1440'), (390, 844, 2, True, '390 px')):
            c.aparelho(w, h, e, t); abre('Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
            ctx01(tam, False); ctx01(tam, True); ctx02_menu(tam, False); ctx02_menu(tam, True); ctx02_foco(tam)
        ERRS.extend(J("window.__errs") or []); chk('sem erro de script (TABR-CTX-01 e TABR-CTX-02)', not ERRS, ERRS[:3]); raise _SoCtx
    c.aparelho(1440, 900, 1, False)
    abre('Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
    # ================= CD-01 Talhões =================
    # 16/10/2026 (proprietário: "fazendas e talhoes na mesma tela, conectados e intuitivos"): uma árvore só, com a fazenda na linha-pai; as
    # colunas da fazenda (posse, área total, talhões ativos) entram ao lado das do talhão
    abre('CD-01.dc.html'); aba('Fazendas e talhões'); g = Grade(J, 0)
    d = tf03('CD-01 Fazendas e talhões', g, ['Fazenda › talhão', 'Situação', 'Posse', 'Área total', 'Área cultivável', 'Talhões', 'Sistema', 'Polígono', 'Diferença', 'Parcelas na safra 2026/27'])
    t1 = next((r for r in d if r.get('Fazenda › talhão') == 'T1'), {}); p1 = next((r for r in d if r.get('Fazenda › talhão') == 'P1'), {})
    pv = next((r for r in d if r.get('Fazenda › talhão', '').startswith('PV')), {})
    chk('CD-01: T1 Sequeiro | 312,0 ha | 312,4 ha | +0,1 % | 2 parcelas (número) | Em dia; P1 Pivô central',
        [t1.get(k) for k in ('Sistema', 'Área cultivável', 'Polígono', 'Diferença', 'Parcelas na safra 2026/27', 'Situação')] == ['Sequeiro', '312,0 ha', '312,4 ha', '+0,1 %', '2', 'Em dia'] and p1.get('Sistema') == 'Pivô central', (t1, p1))
    chk('CD-01: pivô da Lagoa Grande (círculo do KML) dito uma vez, na Situação; Polígono fica "—"', pv.get('Polígono') == '—' and pv.get('Situação') == 'Círculo do KML', pv)
    g.ordena('Área cultivável', desc=True); bl = por_grupo(g, 'Área cultivável')
    chk('CD-01: ordenar Área cultivável (decrescente) pelo número dentro de cada fazenda', bl and all(crescente([num(x) for x in b], True) for b in bl), [b[:4] for b in bl])
    g.filtra('Sistema', ['Pivô central']); s1 = {r.get('Sistema') for r in g.dicts(True)}
    chk('CD-01: filtro Sistema = Pivô central (texto da célula) deixa só pivôs', s1 == {'Pivô central'}, s1)
    limpa(J); shot('cd01-talhoes-1440')
    # ================= CD-01 Água =================
    aba('Água'); g = Grade(J, 0)
    d = tf03('CD-01 Água', g, ['Ponto de água', 'Situação', 'Fazenda', 'Documento', 'Uso', 'Curso d’água', 'Vazão', 'Vencimento'])
    a1 = next((r for r in d if r.get('Ponto de água', '').startswith('Ponto de água 1 ')), {}); a6 = next((r for r in d if r.get('Ponto de água', '').startswith('Ponto de água 6 ')), {})
    chk('CD-01 Água (defeito): a outorga do ponto 1 aparece como Outorga (antes "Certidão"); o ponto 6 é Certidão', a1.get('Documento') == 'Outorga' and a6.get('Documento') == 'Certidão', (a1, a6))
    chk('CD-01 Água: ponto 1 = Captação superficial | Rio A | 180 m³/h | 30/04/2031 | Vigente',
        [a1.get(k) for k in ('Uso', 'Curso d’água', 'Vazão', 'Vencimento', 'Situação')] == ['Captação superficial', 'Rio A (demonstração)', '180 m³/h', '30/04/2031', 'Vigente'], a1)
    # 16/10/2026 (padrão comum, TAB-06/07): a faixa "precisa de atenção" saiu; o documento a renovar fica na linha (Documento e Situação)
    # a Situação traz, depois de " : ", a dica do selo (texto do leitor de tela) com o número e o vencimento do documento a renovar
    fx = J("document.querySelectorAll('.cadx-faixa,.cadx-aviso').length"); ren = [r for r in d if r.get('Situação', '').split(' : ')[0] in ('Vencida', 'Vence em 90 dias', 'Em renovação')]
    chk('CD-01 Água: sem faixa fora da tabela; as outorgas a renovar aparecem na linha com o documento e a situação', fx == 0 and ren and all(r.get('Documento') in ('Outorga', 'Certidão')
        and (' : ' + r.get('Documento') + ' SINT-') in r.get('Situação', '') for r in ren), (fx, ren[:2]))
    g.ordena('Vazão'); vz = [x for x in g.col('Vazão') if x != '—']; m3 = [num(x) * (3.6 if x.endswith('L/s') else 1) for x in vz]
    chk('CD-01 Água: ordenar Vazão pelo valor em m³/h (L/s × 3,6), com a unidade do documento na célula', crescente(m3) and any(x.endswith('L/s') for x in vz), vz)
    g.ordena('Vencimento'); vc = [instante(x) for x in g.col('Vencimento') if x != '—']
    chk('CD-01 Água: ordenar Vencimento por data (anos diferentes)', crescente(vc) and len({x[0] for x in vc}) > 2, g.col('Vencimento')[:6])
    g.filtra('Documento', ['Certidão']); dc = g.dicts()
    chk('CD-01 Água: filtro Documento = Certidão → só certidões (4)', len(dc) == 4 and all(r.get('Documento') == 'Certidão' for r in dc), [r.get('Ponto de água') for r in dc])
    limpa(J)
    aba('Ambiental'); tf03('CD-01 Ambiental', Grade(J, 0), ['Área ambiental', 'Fazenda', 'Tipo', 'Área'])
    # ================= CD-01det =================
    abre('CD-01det.dc.html#talhao=T1'); gi, gp = Grade(J, 0), Grade(J, 1)
    di = tf03('CD-01det ficha', gi, ['Fazenda', 'Sistema', 'Setor de irrigação', 'Área cultivável', 'Polígono', 'Versão', 'Diferença ha', 'Diferença %', 'Situação'], ficha=True)
    f0 = di[0] if di else {}
    chk('CD-01det ficha: T1 = Santa Rita | Sequeiro | — | 312,0 ha | 312,4 ha | v3 | +0,4 ha | +0,1 % | Ativo',
        [f0.get(k) for k in ('Fazenda', 'Sistema', 'Setor de irrigação', 'Área cultivável', 'Polígono', 'Versão', 'Diferença ha', 'Diferença %', 'Situação')] == ['Santa Rita', 'Sequeiro', '—', '312,0 ha', '312,4 ha', 'v3', '+0,4 ha', '+0,1 %', 'Ativo'], f0)
    dp = tf03('CD-01det parcelas', gp, ['Safra › parcela', 'Situação', 'Tipo', 'Cultura', 'Cultivar', 'Área', 'Livre', 'Plantio'])
    gs = [cells[0] for grp, cells in grupos(gp) if grp]
    chk('CD-01det (defeito): T1 da Santa Rita só com safras da Santa Rita (sem a Safra Mamão da Lagoa Grande)', gs and not any('Mamão' in x for x in gs) and 'Safra 2026/27' in gs, gs)
    t1b = next((r for r in dp if r.get('Safra › parcela') == 'T1-B'), {}); sfr = next((r for r in dp if r.get('Safra › parcela') == 'Safrinha 2027'), {})
    chk('CD-01det: T1-B Parcela | Soja | 62 X | 152,0 ha | 25/10/2026 | Sem polígono; Safrinha 2027 livre 152 ha (número)',
        [t1b.get(k) for k in ('Tipo', 'Cultura', 'Cultivar', 'Área', 'Plantio', 'Situação')] == ['Parcela', 'Soja', '62 X', '152,0 ha', '25/10/2026', 'Sem polígono'] and sfr.get('Livre') == '152 ha' and sfr.get('Situação') == 'Rascunho', (t1b, sfr))
    # pré-existente (revisão TABR): a lista conta 1 parcela no PV01 da Lagoa Grande; o detalhe mostra a mesma (antes a Safra Mamão com 0 ha e 29,9 ha livres)
    abre('Main.dc.html', .3); abre('CD-01det.dc.html#talhao=PV01'); dl = Grade(J, 1).dicts();   # outra página antes: só trocar o # não recarrega
    pv1 = next((r for r in dl if r.get('Safra › parcela') == 'Pivô 1'), {})
    sm = next((r for r in dl if r.get('Safra › parcela', '').startswith('Safra Mamão')), {})
    lv = num(sm.get('Livre') or 'x')
    chk('CD-01det PV01 (Lagoa Grande): a parcela Pivô 1 da Safra Mamão aparece (Mamão Formosa | 29,9 ha) e a safra fica sem área livre',
        pv1.get('Cultura') == 'Mamão Formosa' and pv1.get('Área') == '29,9 ha' and lv is not None and abs(lv) < 0.05, (pv1.get('Cultura'), pv1.get('Área'), sm.get('Livre'), sm.get('Situação')))
    abre('Main.dc.html', .3); abre('CD-01det.dc.html#talhao=T1')
    shot('cd01det-1440')
    # ================= CD-02 =================
    abre('CD-02.dc.html'); aba('Culturas'); g = Grade(J, 0)
    d = tf03('CD-02 Culturas', g, ['Cultura › cultivar', 'Situação', 'Tipo de ciclo', 'Unidade de produtividade', 'Ciclo', 'Item de semente', 'Cultivos'])
    w58 = next((r for r in d if r.get('Cultura › cultivar') == '58 W'), {}); mam = next((r for r in d if r.get('Cultura › cultivar', '').startswith('Mamão Formosa')), {})
    chk('CD-02: 58 W = Anual | sc de 60 kg/ha | 118 dias | 6 cultivos (número); Mamão Formosa em t/ha/ano (DEC-0510-03)',
        [w58.get(k) for k in ('Tipo de ciclo', 'Unidade de produtividade', 'Ciclo', 'Cultivos')] == ['Anual', 'sc de 60 kg/ha', '118 dias', '6'] and mam.get('Unidade de produtividade') == 't/ha/ano', (w58, mam))
    g.filtra('Unidade de produtividade', ['t/ha/ano']); fl = [r.get('Cultura › cultivar') for r in g.dicts()]
    chk('CD-02: filtro Unidade de produtividade = t/ha/ano vale na cultivar (Mamão Formosa › Formosa)', len(fl) == 2 and fl[0].startswith('Mamão Formosa') and fl[1] == 'Formosa', fl)
    limpa(J); g.ordena('Ciclo', desc=True); bl = por_grupo(g, 'Ciclo')
    chk('CD-02: ordenar Ciclo (dias) pelo número dentro da cultura', bl and all(crescente([num(x) for x in b], True) for b in bl), bl[:2])
    # 13/10/2026 (proprietário: "tire cadastro de operações de culturas e cultivares"): os rendimentos estão no CD-08, não numa aba do CD-02
    abre('CD-08.dc.html'); g = Grade(J, 0)
    d = tf03('CD-08 Rendimentos', g, ['Operação › conjunto', 'Fonte', 'Processo', 'Cultura', 'Rendimento', 'Custo R$/h', 'Custo R$/ha'])
    pz = next((r for r in d if r.get('Operação › conjunto', '').startswith('Trator 02')), {})
    chk('CD-08: pulverização Medição local | Tratos culturais | 21,60 ha/h | R$ 313,00/h | R$ 14,49/ha',
        [pz.get(k) for k in ('Fonte', 'Processo', 'Rendimento', 'Custo R$/h', 'Custo R$/ha')] == ['Medição local', 'Tratos culturais', '21,60 ha/h', 'R$ 313,00/h', 'R$ 14,49/ha'], pz)
    fch = [(r.get('Operação › conjunto'), c) for r, c in zip(g.dicts(), g.chips('Fonte')) if c]
    chk('CD-08 (A11): a Fonte é texto; só a premissa a validar é chip (pendência com "Validar ›")', [x for x, _ in fch] == ['Derriçadeiras portáteis · equipe de 6'], fch)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf('Trator 02')===0); r&&r.querySelector('[role=cell] span').click();})()"); time.sleep(.5)
    fv = lambda k: J(f"(document.querySelector('#fx_g_rend_{k}')||{{}}).value") or ''
    chk('CD-08 (A1): largura 36 m, velocidade 8 km/h e eficiência 75 % no painel do rendimento (saíram da grade)', [fv('larg'), fv('vel'), fv('efic')] == ['36', '8', '75'], [fv('larg'), fv('vel'), fv('efic')])
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    g.filtra('Processo', ['Colheita']); fl = {r.get('Processo') for r in g.dicts(True)}
    chk('CD-08: filtro Processo = Colheita vale no conjunto', fl == {'Colheita'} and len(g.dicts(True)) == 2, [r.get('Operação › conjunto') for r in g.dicts(True)])
    limpa(J)
    # ================= CD-03 =================
    abre('CD-03.dc.html'); g = Grade(J, 0)
    CD3 = ['Máquina ou instalação', 'Situação', 'Classe', 'Custo R$/h', 'Conjuntos', 'Próxima calibração']
    d = tf03('CD-03 Máquinas', g, CD3)
    pv = next((r for r in d if r.get('Máquina ou instalação') == 'Pulverizador PJ-3030'), {}); pk = next((r for r in d if r.get('Máquina ou instalação') == 'Packing linha 1'), {})
    chk('CD-03: pulverizador Apta | Pulverizador | R$ 95,00/h | 14/12/2026 (modelo e largura no painel)',
        [pv.get(k) for k in ('Situação', 'Classe', 'Custo R$/h', 'Próxima calibração')] == ['Apta', 'Pulverizador', 'R$ 95,00/h', '14/12/2026'], pv)
    chk('CD-03 (A10): calibração que vence em 15 dias diz isso no chip (Packing linha 1: "Calibração a vencer" e "Registrar calibração"; antes "Apta" verde e só a data em amarelo)',
        pk.get('Situação') == 'Calibração a vencer Registrar calibração ›' and pk.get('Próxima calibração') == '01/10/2026', pk)
    # A4: a capacidade muda de grandeza com a classe; a coluna entra quando o filtro de Classe deixa uma só (rótulo e unidade da classe)
    g.filtra('Classe', ['Irrigação']); hs = g.heads(); vz = g.col('Vazão'); al3 = g.desalinhadas()
    chk('CD-03 (A4, M-k): Classe = Irrigação → coluna Vazão em m³/h depois da Classe, com a vazão das 3 instalações', [h for h, _ in hs] == CD3[:3] + ['Vazão'] + CD3[3:] and dict(hs).get('Vazão') == 'm³/h'
        and len(vz) == 3 and all(un_ok(x, 'm³/h') and x != '—' for x in vz), (hs, vz))
    chk('CD-03 (A4): com a coluna de capacidade (7 colunas) cada célula fica sob o seu cabeçalho (a trilha do grid acompanha a coluna que entra)', len(hs) == 7 and al3 == 0, (len(hs), al3))
    g.ordena('Vazão', desc=True); vz2 = [num(x) for x in g.col('Vazão')]
    chk('CD-03 (A4): ordenar a Vazão pelo número', crescente(vz2, True), g.col('Vazão'))
    g.filtra('Classe', ['Trator', 'Pulverizador']); hs2 = g.labels()
    g.filtra('Classe', ['Trator']); pt = g.col('Potência'); hs3 = g.labels()
    chk('CD-03 (A4): Trator + Pulverizador (cv e L) → sem coluna de capacidade; só Trator → Potência em cv', hs2 == CD3 and hs3 == CD3[:3] + ['Potência'] + CD3[3:] and pt and all(x.endswith(' cv') for x in pt), (hs2, hs3, pt))
    limpa(J); chk('CD-03 (A4): Limpar filtros tira a coluna de capacidade', g.labels() == CD3, g.labels())
    g.ordena('Custo R$/h', desc=True); ch = [num(x) for x in g.col('Custo R$/h') if x != '—']
    chk('CD-03: ordenar Custo R$/h (decrescente) pelo número', crescente(ch, True), g.col('Custo R$/h')[:5])
    g.ordena('Próxima calibração'); cl = g.col('Próxima calibração'); dv = [instante(x) for x in cl if x != '—']
    chk('CD-03: ordenar Próxima calibração por data; sem data no fim', crescente(dv) and cl[len(dv):] == ['—'] * (len(cl) - len(dv)), cl)
    g.filtra('Classe', ['Irrigação']); fl = [r.get('Máquina ou instalação') for r in g.dicts()]
    chk('CD-03: filtro Classe = Irrigação → as 3 bombas/setores', len(fl) == 3 and all(r.get('Classe') == 'Irrigação' for r in g.dicts()), fl)
    # recusa e repetição do filtro: vazio continua vazio; o mesmo filtro duas vezes dá o mesmo recorte
    J("""(()=>{const i=document.querySelector('input[aria-label="Buscar nesta tabela"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'Silo');
      i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.5)
    vaz = J("[...document.querySelectorAll('main div')].some(x=>x.offsetParent&&/^Nenhuma linha corresponde aos filtros/.test(x.innerText.trim()))")
    chk('CD-03 (recusa): Classe = Irrigação + busca "Silo" → nenhuma linha e o aviso "Nenhuma linha corresponde aos filtros" (sem voltar a todas)', g.dicts() == [] and vaz, len(g.dicts()))
    limpa(J); n0 = len(g.dicts()); g.filtra('Classe', ['Trator']); a1 = [r.get('Máquina ou instalação') for r in g.dicts()]; g.filtra('Classe', ['Trator']); a2 = [r.get('Máquina ou instalação') for r in g.dicts()]
    chk('CD-03 (repetição): o mesmo filtro duas vezes dá o mesmo recorte; Limpar filtros volta às 15', a1 == a2 and len(a1) == 4 and n0 == 15, (a1, a2, n0))
    abre('CD-03.dc.html'); g = Grade(J, 0); base = [r.get('Máquina ou instalação') for r in g.dicts()]   # sem ordem aplicada
    g.cabecalho_ordena('Custo R$/h'); cr = [num(x) for x in g.col('Custo R$/h') if x != '—']
    chk('CD-03: um clique no título Custo R$/h ordena crescente pelo número', crescente(cr), g.col('Custo R$/h')[:6])
    for _ in range(2): g.cabecalho_ordena('Custo R$/h')
    chk('CD-03 (repetição): três cliques no título (crescente → decrescente → sem ordem) voltam à ordem original', [r.get('Máquina ou instalação') for r in g.dicts()] == base, base[:4])
    # fluxo do cadastro na grade: salvar o custo do Trator 03 → célula e ordem acompanham; número inválido não grava; salvar de novo não duplica
    fluxo_custo(g, '1440', '172,5', 'R$ 172,50/h')
    shot('cd03-1440')
    # ================= CD-04 =================
    abre('CD-04.dc.html'); aba('Pessoas'); g = Grade(J, 0)
    d = tf03('CD-04 Pessoas', g, ['Pessoa', 'Situação', 'Equipe', 'Habilidades', 'Vínculo', 'Disponível até', 'Custo R$/h', 'Habilitação', 'Validade da habilitação'], extra=())
    lu = next((r for r in d if r.get('Pessoa') == 'Lucas'), {})
    chk('CD-04 (A3): Lucas Não alocável em O.S. (motivo na dica: NR-31 vencida) · Renovar NR-31 | Campo 2 | Safrista | 31/07/2027 | R$ 38,00/h | NR-31 | 15/08/2026',
        [lu.get(k) for k in ('Situação', 'Equipe', 'Vínculo', 'Disponível até', 'Custo R$/h', 'Habilitação', 'Validade da habilitação')] == ['Não alocável em O.S. : NR-31 vencida em 15/08/2026 Renovar NR-31 ›', 'Campo 2', 'Safrista', '31/07/2027', 'R$ 38,00/h', 'NR-31', '15/08/2026'], lu)
    # A3: contrato encerrado (Disponível até no passado) diz o motivo e o próximo passo, e a data fica em vermelho (a reprodução do revisor: Carlos até 01/09/2026)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf('Carlos')===0); r&&r.querySelector('[role=cell] span').click();})()"); time.sleep(.5)
    J("""(()=>{const i=document.querySelector('#fx_g_pes_ate'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'2026-09-01'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.2)
    J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); time.sleep(.7)
    ca = next((r for r in g.dicts() if r.get('Pessoa') == 'Carlos'), {})
    cor = J("""(()=>{const t=([...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent))[0]; const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.textContent.replace(/[⇅▾▴▼▲]/g,'').trim());
      const r=[...t.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Carlos')===0); const c=r.querySelectorAll('[role=cell]')[hs.indexOf('Disponível até')]; const sp=[...c.querySelectorAll('span')].filter(s=>s.innerText.trim()==='01/09/2026').pop(); return sp?getComputedStyle(sp).color:'';})()""") or ''
    chk('CD-04 (A3): Carlos com "Disponível até" 01/09/2026 → "Não alocável em O.S." com o motivo (contrato encerrado) e "Renovar contrato ›"; a data em vermelho',
        ca.get('Situação') == 'Não alocável em O.S. : Contrato encerrado em 01/09/2026 Renovar contrato ›' and ca.get('Disponível até') == '01/09/2026' and cor == 'rgb(180, 35, 24)', (ca.get('Situação'), ca.get('Disponível até'), cor))
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf('Carlos')===0); r&&r.querySelector('[role=cell] span').click();})()"); time.sleep(.5)
    cal = [J("(document.querySelector('#fx_g_pes_cal')||{}).value"), J("!!document.querySelector('#fx_g_pes_acesso')"),
           J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); return a?a.innerText.replace(/\\s+/g,' '):'';})()") or '']
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    # acesso ao app: só leitura no painel, gerido em Configurações (CONF-D05, v57); antes da CONF era um campo do formulário
    # 16/10/2026 (proprietário: "elimine campos dos formularios de cadastro que não sejam essenciais", CAD-02): o calendário da pessoa saiu do
    # formulário (nenhuma tela o lia; jornada e capacidade usam o da equipe)
    chk('CD-04 (A1): calendário fora da grade e do painel da pessoa (vale o da equipe); acesso ao app no painel; o acesso só se lê aqui e se gerencia em Configurações',
        cal[0] is None and cal[1] is False and 'Acesso ao app: ' in cal[2] and 'gerenciar em Configurações › Usuários e alçadas' in cal[2], [cal[0], cal[1], cal[2][-300:]])
    rr = g.rotulos('Habilidades')
    chk('CD-04: o filtro de Habilidades oferece cada habilidade (não a lista inteira da célula)', rr and 'Operar trator' in rr and not any(',' in x for x in rr), rr)
    g.filtra('Habilidades', ['Operar trator']); fl = sorted(r.get('Pessoa') for r in g.dicts())
    chk('CD-04: filtro Habilidades = Operar trator → Beto, Carlos, Lucas, Marcos (pertinência, não texto)', fl == ['Beto', 'Carlos', 'Lucas', 'Marcos'], fl)
    limpa(J); g.ordena('Validade da habilitação'); vh = [instante(x) for x in g.col('Validade da habilitação') if instante(x)]
    chk('CD-04: ordenar Validade da habilitação por data', crescente(vh), g.col('Validade da habilitação'))
    # ================= CD-05 =================
    abre('CD-05.dc.html'); aba('Parceiros'); g = Grade(J, 0)
    d = tf03('CD-05 Parceiros', g, ['Parceiro', 'Situação do papel', 'CPF/CNPJ', 'Papéis', 'Contato', 'WhatsApp', 'E-mail', 'Canais autorizados'])
    sv = next((r for r in d if r.get('Parceiro') == 'Sementes Vale'), {}); cv = next((r for r in d if r.get('Parceiro') == 'Coop. Vale'), {})
    chk('CD-05: Sementes Vale WhatsApp 65 99555-6677 "não autorizado" (Canais = E-mail); Coop. Vale com dois papéis e dois estados',
        sv.get('WhatsApp') == '65 99555-6677 não autorizado' and sv.get('Canais autorizados') == 'E-mail' and cv.get('Papéis') == 'Fornecedor, Cliente' and cv.get('Situação do papel') == 'Homologado Limite vigente', (sv, cv))
    g.filtra('Canais autorizados', ['WhatsApp']); fl = g.dicts()
    chk('CD-05: filtro Canais autorizados = WhatsApp (por item da lista)', fl and all('WhatsApp' in r.get('Canais autorizados', '') for r in fl) and len(fl) < len(d), len(fl))
    limpa(J)
    J("[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].find(b=>b.innerText.trim().startsWith('Clientes')).click()"); time.sleep(.6)
    dc = tf03('CD-05 Clientes', g, ['Parceiro', 'Situação do papel', 'CPF/CNPJ', 'Papéis', 'Limite de crédito', 'Validade da análise de crédito', 'Contato', 'WhatsApp', 'E-mail', 'Canais autorizados'])
    chk('CD-05 Clientes (M-e): com 10 colunas (2 a mais que em Todos) cada célula fica sob o seu cabeçalho', len(g.labels()) == 10 and g.desalinhadas() == 0, (len(g.labels()), g.desalinhadas()))
    rh = next((r for r in dc if r.get('Parceiro') == 'Rede Hortifrúti BA'), {})
    chk('CD-05 Clientes: Rede Hortifrúti BA R$ 40.000 | 31/08/2026 | Limite vencido', [rh.get(k) for k in ('Limite de crédito', 'Validade da análise de crédito', 'Situação do papel')] == ['R$ 40.000', '31/08/2026', 'Limite vencido'], rh)
    g.ordena('Limite de crédito', desc=True); lc = [num(x) for x in g.col('Limite de crédito')]
    chk('CD-05 Clientes: ordenar Limite de crédito pelo número', crescente(lc, True), g.col('Limite de crédito'))
    J("[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].find(b=>b.innerText.trim().startsWith('Todos')).click()"); time.sleep(.5)
    # A5: em Todos, Papéis = Cliente; em Transportadores (0 linhas) o menu de Papéis continua com "Cliente" marcado (antes sumia do menu)
    papel = lambda t: (J(f"[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].find(b=>b.innerText.trim().startsWith({json.dumps(t)})).click()"), time.sleep(.6))
    g.filtra('Papéis', ['Cliente']); papel('Transportadores'); n0 = len(g.dicts())
    g._menu('Papéis'); mm = J("[...document.querySelectorAll('[role=dialog] label')].map(l=>[l.innerText.replace(/\\s+/g,' ').trim(), l.querySelector('input').checked])") or []
    J("(()=>{const b=[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    chk('CD-05 (A5): Papéis = Cliente e depois Transportadores → 0 linhas e o menu de Papéis mostra "Cliente 0" marcado', n0 == 0 and ['Cliente 0', True] in mm, (n0, mm))
    limpa(J); papel('Todos')
    aba('Cobertura'); g = Grade(J, 0)
    d = tf03('CD-05 Cobertura', g, ['Grupo de insumo', 'Fornecedores que recebem cotação', 'Situação'])
    se = next((r for r in d if r.get('Grupo de insumo') == 'Sementes'), {}); co = next((r for r in d if r.get('Grupo de insumo') == 'Combustível'), {})
    chk('CD-05 Cobertura: a Situação diz o estado (o número fica ao lado): Sementes 2 Com concorrência; Combustível 0 Sem fornecedor',
        [se.get('Fornecedores que recebem cotação'), se.get('Situação')] == ['2', 'Com concorrência'] and co.get('Fornecedores que recebem cotação') == '0' and co.get('Situação', '').startswith('Sem fornecedor'), (se, co))
    # ================= CD-06 =================
    abre('CD-06.dc.html'); aba('Itens'); g = Grade(J, 0)
    d = tf03('CD-06 Itens', g, ['Grupo › item', 'Situação', 'Natureza de custo', 'Unidade', 'Embalagem', 'Preço de referência', 'Data do preço'])
    ds = next((r for r in d if r.get('Grupo › item') == 'Diesel S10'), {}); ca = next((r for r in d if r.get('Grupo › item') == 'Calcário dolomítico'), {})
    # integração V56 (SOLO-01, D-10): o Calcário dolomítico ganhou preço de referência (R$ 180,00/t, sintético) e não é mais o item sem preço do
    # cenário; o "—" com o chip "Sem preço" segue conferido nas sementes criadas pelas cultivares (cadc_cd02_test, linha "Semente de soja 64 Z")
    chk('CD-06: Diesel S10 L | granel | R$ 6,19/L | 15/09/2026; Calcário dolomítico t | granel | R$ 180,00/t | 15/09/2026, Em dia (SOLO-01 D-10)',
        [ds.get(k) for k in ('Unidade', 'Embalagem', 'Preço de referência', 'Data do preço')] == ['L', 'granel', 'R$ 6,19/L', '15/09/2026']
        and [ca.get(k) for k in ('Unidade', 'Embalagem', 'Preço de referência', 'Data do preço', 'Situação')] == ['t', 'granel', 'R$ 180,00/t', '15/09/2026', 'Em dia'], (ds, ca))
    pr = [x for x in g.col('Preço de referência', True) if x.startswith('R$')]
    chk('CD-06: preço com a unidade do item na célula ("R$ 22,00/L", "R$ 2,40/kg")', pr and all(re.fullmatch(r'R\$ [\d.]+,\d{2}/(L|kg|un|t|sc 60 kg)', x) for x in pr), pr[:5])
    g.filtra('Natureza de custo', ['3.1.02 · Defensivos']); fl = {r.get('Natureza de custo') for r in g.dicts(True)}
    chk('CD-06: filtro Natureza de custo vale no item', fl == {'3.1.02 · Defensivos'} and len(g.dicts(True)) > 5, len(g.dicts(True)))
    limpa(J); g.ordena('Preço de referência', desc=True); bl = por_grupo(g, 'Preço de referência')
    chk('CD-06: ordenar Preço de referência pelo número dentro do grupo', bl and all(crescente([num(x) for x in b if x != '—'], True) or len([x for x in b if x != '—']) < 2 for b in bl), bl[:2])
    aba('Locais'); g = Grade(J, 0)
    d = tf03('CD-06 Locais', g, ['Local', 'Fazenda', 'Tipo', 'Itens com este local padrão'])
    # A4: L (tanque) e sc de 60 kg (silo) são grandezas diferentes: a capacidade entra com o filtro Tanque ou Silo, com a unidade dele
    qtipo = lambda t: (J(f"[...document.querySelectorAll('[role=group][aria-label^=\"Filtro rápido\"] button')].filter(b=>b.offsetParent).find(b=>b.innerText.trim().startsWith({json.dumps(t)})).click()"), time.sleep(.5))
    qtipo('Tanque'); ht = g.heads(); ct = g.col('Capacidade'); al6 = g.desalinhadas(); qtipo('Silo'); hsl = g.heads(); cs_ = g.col('Capacidade'); qtipo('Todos')
    chk('CD-06 Locais (A4): sem coluna de capacidade em Todos; Tanque → Capacidade em L (15.000 L); Silo → em sc de 60 kg (60.000 sc de 60 kg)',
        'Capacidade' not in g.labels() and dict(ht).get('Capacidade') == 'L' and ct == ['15.000 L'] and dict(hsl).get('Capacidade') == 'sc de 60 kg' and cs_ == ['60.000 sc de 60 kg'], (ht, ct, hsl, cs_))
    chk('CD-06 Locais (A4): com a Capacidade (5 colunas) cada célula fica sob o seu cabeçalho', len(ht) == 5 and al6 == 0, (len(ht), al6))
    # ================= CD-07 =================
    abre('CD-07.dc.html'); g = Grade(J, 0)
    CD7 = ['Dimensão › código', 'Situação', 'Nome', 'Início da vigência', 'Fim da vigência', 'Conta no ERP (Sankhya)', 'No rascunho']
    d = tf03('CD-07 Estrutura', g, CD7)
    n1 = next((r for r in d if r.get('Dimensão › código') == '3.1.01'), {}); e2 = next((r for r in d if r.get('Dimensão › código') == '02'), {})
    chk('CD-07: 3.1.01 Mapeado | Fertilizantes e corretivos | 01/07/2026 | 30/06/2027 | 4.1.1.01; 02 Novo no rascunho',
        [n1.get(k) for k in ('Situação', 'Nome', 'Início da vigência', 'Fim da vigência', 'Conta no ERP (Sankhya)')] == ['Mapeado', 'Fertilizantes e corretivos', '01/07/2026', '30/06/2027', '4.1.1.01'] and e2.get('No rascunho') == 'Novo', (n1, e2))
    def painel7(cod):
        J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf({json.dumps(cod)})===0); r&&r.querySelector('[role=cell] span').click();}})()"); time.sleep(.5)
        out = [J(f"(document.querySelector('#fx_g_dim_{k}')||{{}}).value") or '' for k in ('origT', 'vincT', 'top')]
        J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3); return out
    p31, pso = painel7('3.1.01'), painel7('SOJA')
    chk('CD-07 (A1): origem, vínculos e TOP no painel do código (3.1.01 Estrutura gerencial · grupos … · TOP 1201; SOJA Culturas e cultivares)', p31[0] == 'Estrutura gerencial' and p31[2] == '1201' and p31[1] and pso[0] == 'Culturas e cultivares', (p31, pso))
    g.ordena('Início da vigência', desc=True); bl = por_grupo(g, 'Início da vigência')
    chk('CD-07: ordenar Início da vigência por data dentro da dimensão', bl and all(crescente([instante(x) for x in b], True) or len(set(b)) < 2 for b in bl), bl[:2])
    g.filtra('Situação', ['Dimensão própria']); fl = {r.get('Situação') for r in g.dicts(True)}
    chk('CD-07: filtro Situação = Dimensão própria → culturas e processos (9)', fl == {'Dimensão própria'} and len(g.dicts(True)) == 9, len(g.dicts(True)))
    limpa(J); shot('cd07-1440')
    # A8: depois de publicar, "No rascunho" sai (não fica uma coluna vazia em todas as linhas); com rascunho novo, volta
    J("(()=>{const c=[...document.querySelectorAll('header button')].find(c=>c.innerText.indexOf('Publicar versão')>=0); c&&c.click();})()"); time.sleep(.6)   # 16/10: no cabeçalho (antes na faixa)
    h_pub = g.labels(); al7 = g.desalinhadas()
    chk('CD-07 (A8): depois de "Publicar estrutura", a coluna "No rascunho" sai e as células seguem sob os cabeçalhos', h_pub == CD7[:-1] and al7 == 0, (h_pub, al7))
    # A1: a Situação à vista sem rolar a grade a 1440 e 1280 px; a 1440 px as grades cabem na caixa (o CD-05 rola só os contatos, no fim)
    MED = """(()=>[...document.querySelectorAll('.g2rola')].filter(r=>r.offsetParent).map(r=>{const R=r.getBoundingClientRect(); const hs=[...r.querySelectorAll('[role=table]>[role=row] [role=columnheader]')];
      const lab=h=>h.textContent.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim(); return {sobra:r.scrollWidth-r.clientWidth, fora:hs.filter(h=>h.getBoundingClientRect().right>R.right+1).map(lab)};}))()"""
    larg = []
    for w in (1440, 1280):
        c.aparelho(w, 900, 1, False)
        for pg, tabs in (('CD-01.dc.html', ['Fazendas e talhões', 'Água']), ('CD-01det.dc.html#talhao=T1', ['']), ('CD-02.dc.html', ['Culturas', 'Operações']), ('CD-03.dc.html', ['']),
                         ('CD-04.dc.html', ['Pessoas']), ('CD-05.dc.html', ['Parceiros']), ('CD-06.dc.html', ['Itens', 'Locais']), ('CD-07.dc.html', [''])):
            abre(pg)
            for tb in tabs:
                if tb: aba(tb)
                for i, m in enumerate(J(MED) or []):
                    ruim = sorted({'Situação', 'Situação do papel', 'Fonte'} & set(m['fora'])) + (['rola %d px' % m['sobra']] if (w == 1440 and m['sobra'] > 1 and not pg.startswith('CD-05')) else [])
                    if ruim: larg.append((w, pg.split('.')[0], tb, i, ruim))
    chk('CD (A1): Situação à vista sem rolar a 1440 e 1280 px; a 1440 px as grades cabem na caixa (o CD-05 rola só os contatos)', not larg, larg)
    c.aparelho(1440, 900, 1, False); ctx01('1440', False); ctx01('1440', True); ctx02_menu('1440', False); ctx02_menu('1440', True); ctx02_foco('1440')
    ERRS.extend(J("window.__errs") or []); chk('sem erro de script (1440)', not ERRS, ERRS[:3])
    # ================= 390 px =================
    c.aparelho(390, 844, 2, True); r390 = []
    for pg, tabs in (('CD-01.dc.html', ['Fazendas e talhões', 'Água']), ('CD-01det.dc.html#talhao=T1', ['']), ('CD-02.dc.html', ['Culturas', 'Operações']), ('CD-03.dc.html', ['']),
                     ('CD-04.dc.html', ['Pessoas']), ('CD-05.dc.html', ['Parceiros', 'Cobertura']), ('CD-06.dc.html', ['Itens', 'Locais']), ('CD-07.dc.html', [''])):
        abre(pg)
        for tb in tabs:
            if tb: aba(tb)
            n = J("[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).length") or 0
            for i in range(n):
                q = Grade(J, i).rola_dentro(); r390.append((pg.split('.')[0] + (' ' + tb if tb else '') + f' #{i}', q.get('pagina'), q.get('cabe') or q.get('rola'), q.get('c0'), q.get('rola')))
        if pg.startswith('CD-03'): shot('cd03-390')
    ruim = [x for x in r390 if not (x[1] and x[2] and x[3])]
    chk(f'390 px: {len(r390)} grades sem rolagem lateral da página; cada grade cabe ou rola dentro da caixa, com a 1ª coluna à vista', r390 and not ruim, ruim or r390[:3])
    chk('390 px: as grades largas rolam dentro da caixa (pelo menos as de muitas colunas)', sum(1 for x in r390 if x[4]) >= len(r390) - 3, [x[0] for x in r390 if not x[4]])
    # fluxo a 390 px, com toque: o mesmo cadastro na grade (normal, recusa, repetição) e o filtro pelo menu da coluna
    abre('CD-03.dc.html'); g = Grade(J, 0); fluxo_custo(g, '390 px', '165', 'R$ 165,00/h'); limpa(J)
    n0 = len(g.dicts()); g.filtra('Classe', ['Irrigação']); a1 = [r.get('Máquina ou instalação') for r in g.dicts()]
    J("""(()=>{const i=[...document.querySelectorAll('input[aria-label="Buscar nesta tabela"]')].find(x=>x.offsetParent); if(!i) return; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'Silo');
      i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.5)
    vaz = J("[...document.querySelectorAll('main div')].some(x=>x.offsetParent&&/^Nenhuma linha corresponde aos filtros/.test(x.innerText.trim()))")
    chk('CD-03 390 px (filtro): Classe = Irrigação → 3 linhas; + busca "Silo" → nenhuma linha e o aviso; Limpar filtros volta a todas',
        len(a1) == 3 and g.dicts() == [] and vaz and (limpa(J) or True) and len(g.dicts()) == n0, (a1, n0))
    ctx01('390 px', False); ctx01('390 px', True); ctx02_menu('390 px', False); ctx02_menu('390 px', True); ctx02_foco('390 px')
    ERRS.extend(J("window.__errs") or []); chk('sem erro de script (390)', not ERRS, ERRS[:3])
except _SoCtx: pass
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
