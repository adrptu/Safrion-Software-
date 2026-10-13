# -*- coding: utf-8 -*-
"""Teste de navegador · Planejar safra, etapa 2 "Talhões e cultivos" (ESPECIFICACAO etapa-2-talhoes §7.1, OC-01 a OC-23).
Fluxo principal do módulo em 1440 × 900 e em 390 × 844 (e 360 × 800 no layout): todos os talhões, Situação e faixa, Planejar › com os
padrões (normal), trava com fato, dano e saída sem gravar (erro/recusa), salvar duas vezes e reabrir (repetição), pendência que salva,
lote com pendência, edição entre safras, Vincular ciclo, safras novas separadas, Boa Vista e safra encerrada. Números comparados com
os da especificação (os mesmos do ocupacao_unit.py). Emulação no Chrome headless: não é aparelho físico.
Uso: python3 ocupacao_test.py [desktop|celular|tudo]   (padrão: tudo)"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome
MODO = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
PROBE = os.path.join(HERE, '_probe'); os.makedirs(PROBE, exist_ok=True)
import saf_nav_lib as L
from saf_nav_lib import *   # chk, rows, nivel0, faixa, chips, toast, nota, painel, campos, fset, botao, salvar, na_linha, abre, estado, linha, sit, nova_safra…
try:
    c = L.c = Chrome()
    if MODO in ('desktop', 'tudo'):
        # ---------- OC-14, OC-01, OC-03, OC-04, OC-02 (leitura) ----------
        for h in ('#saf=S2627&passo=cultivos', '#saf=S27SF&passo=cultivos', '#saf=S2526&passo=cultivos', '#saf=LG2627&passo=cultivos'):
            abre(h)
            chk('OC-14 sem "Adicionar cultivo" ' + h, c.js("document.querySelectorAll('[data-acao=adicionar]').length") == 0 and 'Adicionar cultivo' not in c.js("document.body.innerText"))
        abre('#saf=S27SF&passo=cultivos'); L0 = nivel0()
        chk('OC-01 S27SF: 8 talhões da Santa Rita, nenhum pivô', [r['TALHÃO OU PARCELA'].split(' ')[0] for r in L0] == ['T1', 'T2', 'T3', 'T4', 'P1', 'P2', 'T7', 'C1'], [r['TALHÃO OU PARCELA'] for r in L0])
        chk('OC-03 faixa S27SF (§3.4)', faixa() == FX27SF, faixa())
        chk('OC-04 chips S27SF pelo nível 0 (soma = Todas)', chips() == ['Todas 8', 'A conferir 4', 'Perene 2', 'Livre 1', 'Planejado 1'], chips())
        chk('§6.1 Situação, Área livre e Livre a partir de (S27SF)', [(r['TALHÃO OU PARCELA'].split(' ')[0], r['SITUAÇÃO'], r['ÁREA LIVRE'], r['LIVRE A PARTIR DE']) for r in L0] ==
            [('T1', 'Livre', '152 ha', '21/02/2027'), ('T2', 'Planejado', '—', '—'), ('T3', 'A conferir', '96 ha', '18/02/2027 est.'), ('T4', 'A conferir', '204 ha', '16/02/2027 est.'),
             ('P1', 'A conferir', '—', '—'), ('P2', 'A conferir', '80 ha', '24/03/2027 est.'), ('T7', 'Perene', '—', '—'), ('C1', 'Perene', '—', '—')],
            [(r['TALHÃO OU PARCELA'], r['SITUAÇÃO'], r['ÁREA LIVRE'], r['LIVRE A PARTIR DE']) for r in L0])
        t3 = linha('T3', L0)
        chk('OC-02 T3 é folha com a ocupação de fora esmaecida (Soja 62 X, 17/02/2027, Estimado, Safra 2026/27 ›)',
            (t3['CULTURA'], t3['OCUPA ATÉ'], t3['FIM POR'], t3['SAFRA']) == ('Soja', '17/02/2027', 'Estimado (ciclo)', 'Safra 2026/27 ›'), t3)
        chk('OC-18 Situação com texto e motivo do A conferir na dica', t3['SITUAÇÃO'] == 'A conferir' and 'saída da soja' in (t3['_dica'] or ''), t3.get('_dica'))
        chk('OC-18 motivo também no texto para leitor de tela', bool(c.js("!!document.querySelector('[role=row] .g2sr')")))
        T7 = linha('T7', L0); chk('OC-05 negativo: T7 e C1 Perene sem Planejar nem Vincular (a S2627 cruza)', 'Planejar' not in T7['TALHÃO OU PARCELA'] and 'Vincular' not in T7['TALHÃO OU PARCELA'] and T7['OCUPA ATÉ'] == 'sem fim', T7)
        todas = rows(); t1k = [r for r in todas if r['_kid'] and r['TALHÃO OU PARCELA'] in ('T1-A', 'T1-B')]
        chk('OC-02 grupo T1: c1 e c2 (Safra 2026/27) e d1 desta safra, por data de início', [(r['TALHÃO OU PARCELA'], r['CULTURA'], r['SAFRA']) for r in t1k] ==
            [('T1-A', 'Soja', 'Safra 2026/27 ›'), ('T1-B', 'Soja', 'Safra 2026/27 ›'), ('T1-A', 'Milho', '—')], t1k)
        chk('R-13 total da Área só desta safra (553 ha)', c.js("(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const r=t.querySelector('.g2tot'); return r?r.innerText.replace(/\\s+/g,' '):'';})()").find('553 ha') >= 0)
        chk('R-23 sem caixas de seleção nos cultivos (proprietário, 13/10/2026): o plano entra pela primária ou pela linha', c.js("document.querySelectorAll('[role=table] input[type=checkbox]').length") == 0)
        botao('Livre 1'); L = nivel0()
        chk('OC-04 chip Livre mostra só o T1 (com as filhas ao abrir)', [r['TALHÃO OU PARCELA'].split(' ')[0] for r in L] == ['T1'] and len(rows()) == 4, [r['TALHÃO OU PARCELA'] for r in rows()])
        botao('Todas 8')
        abre('#saf=S2627&passo=cultivos')
        chk('OC-03 faixa S2627 com "1 sucessão a conferir"', faixa() == FX2627, faixa())
        chk('OC-04 chips S2627', chips() == ['Todas 8', 'Planejado 7', 'A conferir 1'], chips())
        chk('§3.2 S2627 com 18 linhas de grupos abertos', len(rows()) == 18, len(rows()))
        n2627 = nota(); chk('§5.1 nota da S2627 cita a sucessão do P1 com a saída', 'P1: o Feijão da Safrinha 2027 começa em 15/04/2027; a saída da soja é estimada em 08/03/2027 (sem plano, CD-02).' in n2627 and 'Informar colheita de P1 ›' in n2627, n2627)
        abre('#saf=S2526&passo=cultivos'); L = rows()
        chk('OC-16 S2526 encerrada: 5 cultivos, sem Planejar nem Dividir, Situação "—"', len(L) == 5 and all(r['SITUAÇÃO'] == '—' for r in L) and not any('Planejar' in r['TALHÃO OU PARCELA'] or 'Dividir' in r['TALHÃO OU PARCELA'] for r in L), L[:2])
        chk('OC-20 lavouras em campo e4/e5 na S2526 com colheita informada', [(r['TALHÃO OU PARCELA'], r['OCUPA ATÉ'], r['FIM POR']) for r in L[3:]] == [('P1 lavoura em campo', '10/10/2026', 'Colheita informada'), ('P2 lavoura em campo', '15/11/2026', 'Colheita informada')], L[3:])
        abre('#saf=LG2627&passo=cultivos'); L = nivel0()
        chk('OC-01 LG2627: 23 pivôs, nunca o T1', len(L) == 23 and all(r['TALHÃO OU PARCELA'].startswith('Pivô') for r in L), len(L))
        # ---------- OC-06 normal: Planejar T1 com os padrões ----------
        abre('#saf=S27SF&passo=cultivos'); cliques = 0
        r = na_linha('T1', 'Planejar ›'); cliques += 1; f = campos('g_cult_S27SF')
        chk('OC-06 painel "Planejar T1" com contexto herdado', r == 'ok' and painel().startswith('Planejar T1') and 'Santa Rita · Safrinha 2027 · T1 312 ha. Livre: 152 ha a partir de 21/02/2027 (folga 1 dia).' in painel(), painel()[:300])
        chk('OC-06 padrões: 152 ha, 21/02/2027 (PlantioMin), T1-B; prévia 21/02/2027 a 11/07/2027', (f.get('area'), f.get('plantio'), f.get('local'), f.get('ocup_txt'), f.get('plano')) == ('152', '2027-02-21', 'T1-B', '21/02/2027 a 11/07/2027', 'MILHO-SF'), f)
        chk('OC-06 Plano antes de Plantio; Colheita prevista do plano só leitura; unidade da meta da cultura (DEC-0510-03)',
            list(f).index('plano') < list(f).index('plantio') and f.get('colh_txt') == '11/07/2027 · do plano' and f.get('unm_txt') == 'sc/ha · Padrão da cultura', list(f))
        chk('§0 campo numérico com teclado decimal', c.js("document.getElementById('fx_g_cult_S27SF_area').getAttribute('inputmode')") == 'decimal')
        fset('g_cult_S27SF', 'meta', '170'); cliques += 1; salvar(); cliques += 1; t = toast()
        chk('OC-06 salva: "Cultivo incluído como parcela T1-B"', 'Cultivo incluído como parcela T1-B' in t and not painel(), t)
        chk('OC-06 faixa "Nesta safra 705 · A conferir 380 · Perene 80"', faixa().startswith('Nesta safra 705 · A conferir 380 · Perene 80 · de 1.165 ha'), faixa())
        chk('OC-06 T1 passa a Planejado e perde o Planejar ›', sit('T1') == 'Planejado' and 'Planejar' not in linha('T1')['TALHÃO OU PARCELA'], linha('T1'))
        info('OC-19 toques no Planejar do T1 (1440): Planejar ›, Meta, Salvar', cliques)
        # repetição: salvar de novo não duplica; o T1 não oferece Planejar com área cheia
        n_antes = len([x for x in (estado('g_cult_S27SF') or []) for _ in [0]])
        chk('Repetição: Salvar com o painel fechado não cria outro cultivo', salvar().startswith('sem botão') and len(estado('g_cult_S27SF') or []) == n_antes)
        st = estado('g_cult_S27SF') or []
        def todos_ids(rs): return [x['id'] for r in rs for x in ([r] + (r.get('kids') or []))]
        chk('OC-13 estado sem linha de exibição (fora, livre, talhão)', not any(x.get('fora') or x.get('livre') or x.get('tal') for r in st for x in [r] + (r.get('kids') or [])) and all(not i.startswith('fora_') and not i.startswith('tal_') for i in todos_ids(st)), todos_ids(st))
        # ---------- OC-07 recusa: T1 312 ha em 21/02/2027 (M1), nada gravado ----------
        abre('#saf=S27SF&passo=cultivos'); na_linha('T1', 'Planejar ›'); fset('g_cult_S27SF', 'area', '312'); fset('g_cult_S27SF', 'plantio', '2027-02-21'); fset('g_cult_S27SF', 'meta', '170'); salvar()
        pn = painel()
        chk('OC-07 recusa M1 com fato e saída; painel continua aberto', 'De 21/02/2027 a 10/07/2027, 160 ha de T1 estão com Milho (T1-A, Safrinha 2027). Máximo 152 ha nesse período.' in pn, pn[:600])
        chk('OC-07 nada gravado (faixa igual)', faixa() == FX27SF, faixa())
        botao('Cancelar', "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent)||document"); time.sleep(.2)
        chk('OC-18 Esc/Cancelar com alteração pede confirmação', 'Há alterações não salvas' in painel(), painel()[-200:])
        botao('Descartar alterações'); time.sleep(.2)
        # ---------- OC-08 pendência que salva: T1-B em 20/02/2027 ----------
        na_linha('T1', 'Planejar ›'); fset('g_cult_S27SF', 'plantio', '2027-02-20'); fset('g_cult_S27SF', 'meta', '170'); salvar(); t = toast()
        chk('OC-08 T1-B em 20/02/2027 salva com pendência de 1 dia (folga 1)', 'Cultivo incluído como parcela T1-B' in t and 'sobreposição prevista de 1 dia' in t, t)
        chk('OC-08 T1 fica A conferir pela pendência', sit('T1') == 'A conferir', linha('T1'))
        # ---------- OC-11 recusa M2 e salva com aviso no dia seguinte ----------
        abre('#saf=S27SF&passo=cultivos'); na_linha('T3', 'Planejar ›'); fset('g_cult_S27SF', 'plantio', '2027-02-10'); fset('g_cult_S27SF', 'meta', '170'); salvar()
        chk('OC-11 milho no T3 em 10/02/2027 recusado (M2)', 'T3 está com Soja 62 X da Safra 2026/27, plantada em 22/10/2026: ocupa a área até pelo menos 10/02/2027 (ciclo mínimo da soja, 112 dias, CD-02).' in painel(), painel()[:500])
        fset('g_cult_S27SF', 'plantio', '2027-02-11'); salvar(); t = toast()
        chk('OC-11 em 11/02/2027 salva com o aviso "provável sobreposição (7 dias)"', 'Cultivo incluído: T3 inteiro' in t and 'provável sobreposição (7 dias)' in t, t)
        # ---------- OC-09 lote com pendência; OC-12 ----------
        abre('#saf=S2627&passo=cultivos')
        botao('Aplicar plano em 4 cultivos', "document.querySelector('[data-acoes]')"); time.sleep(.3)   # sem caixas de seleção (13/10): a primária leva os 4 sem plano (c4..c7)
        c.js("(()=>{const e=document.getElementById('ap_sel'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(e,'SOJA-AT'); e.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.4)
        pn = painel()
        chk('OC-09 R-16 o painel mostra antes quem recebe com pendência e o botão conta 4', 'P2 · Soja 62 X · 80 ha · recebe com pendência' in pn and 'Aplicar plano em 4 cultivos' in pn, pn[:700])
        botao('Aplicar plano em 4 cultivos', "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent)"); t = toast()
        chk('OC-09 aplica nos 4, P2 com pendência', 'aplicado a 4 cultivos' in t and 'sobreposição prevista de 11 dias' in t, t)
        p2 = linha('P2'); chk('OC-09 P2 A conferir com o ocupante (e5) visível na linha', p2['SITUAÇÃO'] == 'A conferir' and any(r['TALHÃO OU PARCELA'] == 'P2' and r['SAFRA'] == 'Safra 2025/26 ›' for r in rows()), p2)
        n = nota(); chk('OC-09 nota sem "sem plano" e com a pendência e as saídas', 'sem plano agronômico' not in n and 'P2: sobreposição prevista de 11 dias com o Milho da Safra 2025/26 (até 15/11/2026).' in n and 'Mudar plantio de P2 ›' in n and 'Ver P2 na Safra 2025/26 ›' in n, n)
        chk('OC-12 com plano no c6, P1 sai de A conferir na S2627', sit('P1') == 'Planejado', linha('P1'))
        # Mudar plantio › abre o cultivo com o plantio mínimo (06/12/2026)
        botao('Mudar plantio de P2 ›'); f = campos('g_cult_S2627')
        chk('R-17 "Mudar plantio ›" abre o P2 com o plantio mínimo 06/12/2026', f.get('plantio') == '2026-12-06', f)
        salvar(); time.sleep(.3)
        chk('§9.3 com 06/12/2026 a pendência some', sit('P2') == 'Planejado', linha('P2'))
        # ---------- OC-10 edição entre safras: plantio do c1 em 30/10/2026 ----------
        abre('#saf=S2627&passo=cultivos'); clica_linha('c1'); fset('g_cult_S2627', 'plantio', '2026-10-30'); salvar(); t = toast()
        chk('OC-10 c1 em 30/10/2026 salva com a pendência P2 no d1', 'T1-A: a colheita prevista da Soja passa para 25/02/2027, depois do plantio do Milho da Safrinha 2027 (20/02/2027). Sobreposição prevista de 6 dias.' in t, t)
        chk('OC-10 d1 visível no grupo T1', any(r['_kid'] and r['TALHÃO OU PARCELA'] == 'T1-A' and r['CULTURA'] == 'Milho' for r in rows()))
        # ---------- OC-22 colheita informada no c4 libera o T4 na Safrinha ----------
        abre('#saf=S2627&passo=cultivos'); clica_linha('c4'); fset('g_cult_S2627', 'colheita', '2027-02-10'); salvar()
        c.js("location.hash='#saf=S27SF&passo=cultivos'"); time.sleep(1.0); t4 = linha('T4')
        chk('OC-22 S27SF: T4 Livre 204 ha desde 11/02/2027', (t4['SITUAÇÃO'], t4['ÁREA LIVRE'], t4['LIVRE A PARTIR DE']) == ('Livre', '204 ha', '11/02/2027'), t4)
        chk('OC-22 chips "A conferir 3 · Livre 2 · Perene 2 · Planejado 1"', chips() == ['Todas 8', 'A conferir 3', 'Livre 2', 'Perene 2', 'Planejado 1'], chips())
        # link de outra safra abre a safra no passo cultivos com o painel do cultivo
        abre('#saf=S27SF&passo=cultivos')
        c.js("location.hash='#saf=S2627&passo=cultivos&cult=c5'"); time.sleep(1.2)
        chk('§5.1 endereço com &cult= abre a S2627 no passo cultivos com o painel do c5', 'Safra 2026/27' in c.js("document.body.innerText") and painel().startswith('Cultivo · T3'), painel()[:120])
        # ---------- OC-05 Vincular ciclo na 2027/28 ----------
        nova_safra('Safra 2027/28', '2027-09-01', '2028-08-31'); L0 = nivel0()
        chk('OC-05 2027/28: T7 e C1 com Vincular ciclo, sem Planejar; faixa "Livre 1.085 · Perene 80"', 'Vincular ciclo' in linha('C1', L0)['TALHÃO OU PARCELA'] and 'Planejar' not in linha('C1', L0)['TALHÃO OU PARCELA'] and faixa().startswith('Nesta safra 0 · Livre 1.085 · Perene 80'), (faixa(), linha('C1', L0)))
        na_linha('C1', 'Vincular ciclo ›'); f = campos('g_cult_NOVA')
        chk('OC-05 painel "Vincular ciclo C1" com o plantio real travado e sem plano', painel().startswith('Vincular ciclo C1') and f.get('plantio') == '2019-01-15' and f.get('plano') == '', f)
        fset('g_cult_NOVA', 'meta', '38'); salvar(); t = toast()
        chk('OC-05 vincular C1: faixa "Nesta safra 38 · Livre 1.085 · Perene 42"', 'Ciclo vinculado' in t and faixa().startswith('Nesta safra 38 · Livre 1.085 · Perene 42'), (t, faixa()))
        chk('OC-05 o cultivo vinculado nasce sem plano e C1 não oferece Vincular de novo', 'Vincular' not in linha('C1')['TALHÃO OU PARCELA'] and 'sem plano agronômico' in nota(), nota())
        # ---------- OC-15 safras novas separadas e Boa Vista ----------
        nova_safra('Nova Boa Vista', '2026-09-01', '2027-08-31', 'Boa Vista'); L0 = nivel0()
        chk('OC-15/R-01 Boa Vista nova: só o B1, Livre 120 ha desde 01/09/2026', [(r['TALHÃO OU PARCELA'], r['SITUAÇÃO'], r['ÁREA LIVRE'], r['LIVRE A PARTIR DE']) for r in L0] == [('B1 Planejar ›', 'Livre', '120 ha', '01/09/2026')], L0)
        chk('R-22 a safra nova não herda o cultivo vinculado da outra safra nova', faixa().startswith('Nesta safra 0 · Livre 120'), faixa())
        na_linha('B1', 'Planejar ›'); fset('g_cult_NOVA', 'cult', 'Soja'); fset('g_cult_NOVA', 'var', '58 W'); fset('g_cult_NOVA', 'meta', '60'); salvar(); time.sleep(.3)
        st = [x for r in (estado('g_cult_NOVA') or []) for x in [r] + (r.get('kids') or [])]
        b1 = [x for x in st if x['v'].get('talhao') == 'B1']
        chk('OC-15/R-21 cultivo da Boa Vista grava Boa Vista e a safra dele', len(b1) == 1 and b1[0]['v'].get('faz') == 'Boa Vista' and str(b1[0]['v'].get('saf', '')).startswith('n'), b1)
        chk('sem erro de JS (desktop)', erros() == '', erros())
    if MODO in ('celular', 'tudo'):
        # ---------- OC-17 layout 390 × 844 e 360 × 800; fluxo principal no celular ----------
        for w, h in ((390, 844), (360, 800)):
            abre('#saf=S27SF&passo=cultivos', w, h, True); time.sleep(.4)
            m = c.js(r"""(()=>{ const vw=innerWidth; const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const caixa=t.closest('.g2rola'); const q=caixa.getBoundingClientRect();
              const hs=[...t.querySelectorAll('[role=columnheader]')]; const iS=hs.findIndex(h=>/SITUAÇÃO/i.test(h.innerText)); const si=hs[iS].getBoundingClientRect();
              const chs=[...t.querySelectorAll('[role=row]')].slice(1).map(r=>r.querySelectorAll('[role=cell]')[iS]).filter(Boolean).map(c=>c.getBoundingClientRect());
              const pl=[...t.querySelectorAll('button')].find(b=>b.innerText.trim()==='Planejar ›'); const pr=pl?pl.getBoundingClientRect():null;
              return {pag:document.documentElement.scrollWidth>vw+1, caixas:t.querySelectorAll('input[type=checkbox]').length, sitIn:si.right<=q.left+caixa.clientWidth+1, chipsIn:chs.every(r=>r.right<=q.left+caixa.clientWidth+1),
                      planejar:!!pr&&pr.right<=q.left+caixa.clientWidth+1&&!!pl.closest('.g2c0'), grupos:[...t.querySelectorAll('[aria-expanded]')].filter(b=>b.offsetParent).every(b=>b.getAttribute('aria-expanded')==='false')}; })()""")
            chk(f'OC-17 {w}×{h}: sem rolagem lateral da página; sem caixas de seleção; Situação inteira sem rolar a caixa; Planejar › na coluna presa; grupos recolhidos', not m['pag'] and m['caixas'] == 0 and m['sitIn'] and m['chipsIn'] and m['planejar'] and m['grupos'], m)
            c.shot(os.path.join(PROBE, f'oc_etapa2_{w}.png'))
        abre('#saf=S27SF&passo=cultivos', 390, 844, True); cliques = 0
        na_linha('T1', 'Planejar ›'); cliques += 1
        pw = c.js("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); const r=a.getBoundingClientRect(); return [Math.round(r.left),Math.round(r.width)];})()")
        chk('OC-17 painel em tela cheia a 390', pw == [0, 390], pw)
        fset('g_cult_S27SF', 'meta', '170'); cliques += 1; salvar(); cliques += 1; t = toast()
        chk('390: Planejar T1 com os padrões salva (fluxo principal no celular)', 'Cultivo incluído como parcela T1-B' in t and faixa().startswith('Nesta safra 705'), (t, faixa()))
        info('OC-19 toques no Planejar do T1 (390): Planejar ›, Meta, Salvar', cliques)
        na_linha('T3', 'Planejar ›'); fset('g_cult_S27SF', 'plantio', '2027-02-10'); fset('g_cult_S27SF', 'meta', '170'); salvar()
        chk('390: recusa M2 visível no painel', 'ocupa a área até pelo menos 10/02/2027' in painel(), painel()[:300])
        c.shot(os.path.join(PROBE, 'oc_painel_390_recusa.png'))
        chk('sem erro de JS (celular)', erros() == '', erros())
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas ({MODO})')
for f in FAIL: print('  - ' + f)
sys.exit(1 if FAIL else 0)
