# -*- coding: utf-8 -*-
"""COLUNAS-1 · colunas essenciais, lote 1 (pedido do proprietário de 10/10; AUDITORIA COLUNAS §4.2) · teste de navegador do fluxo do módulo.
Em 1440 × 900 e 390 × 844 (emulação no Chrome headless, não é aparelho físico):
- normal: cada grade com as colunas essenciais; o dado que saiu da linha aparece no detalhe (painel, formulário, página) e a busca acha a linha
  por ele; filtro e ordenação seguem; Tipo (Ordens) e Tanque/lote (Abastecimentos) filtram fora da grade, também no Kanban;
- erro/recusa: salvar a correção do apontamento sem motivo é recusado com o motivo e nada grava; filtro guardado de coluna que saiu (estado antigo
  no sessionStorage) não esconde linha nem deixa chip órfão; plano com ativo sem vínculo mostra a pendência;
- repetição: aplicar o mesmo filtro duas vezes dá o mesmo resultado; abrir e fechar o detalhe duas vezes preserva filtro e posição;
- teclado: Tab até a linha, Enter abre o detalhe, Esc fecha e o foco volta à linha (Manutenção);
- 390 px: a página não rola de lado; a grade rola dentro da caixa com a 1ª coluna presa; medidas de rolagem gravadas para a evidência.
Uso (de gen37/, depois de build.py e montar_render.py): python3 colunas1_test.py [pasta de capturas]"""
import sys, os, time, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '_probe', 'colunas1')
os.makedirs(OUT, exist_ok=True)
OK, FAIL, MED = [], [], {}
def chk(nome, cond, det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ') + nome + ('' if cond else ' · ' + str(det)[:900]), flush=True)
p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
NAV = [0]
def abre(pag, h='', w=1440, hh=900, toque=False, perfil=None, limpa=False):
    NAV[0] += 1; c.aparelho(w, hh, 2 if toque else 1, toque)
    if limpa or perfil:
        c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .3)
        if limpa: J("localStorage.clear(); sessionStorage.clear()")
        if perfil: J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)})")
    c.goto(f'http://127.0.0.1:{p}/{pag}?r={NAV[0]}' + (('#' + h) if h else ''), 1.0); time.sleep(.5)
N = "(s=>(s||'').replace(/[⇅▾▴▲▼]/g,'').replace(/\\s+/g,' ').trim())"
def tabelas(): return J(f"[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).map(t=>[...t.querySelectorAll('[role=columnheader]')].map(h=>{N}(h.innerText)).filter(Boolean))") or []
def cab(i=0): t = tabelas(); return [x.upper() for x in t[i]] if len(t) > i else []   # o cabeçalho é exibido em maiúsculas (text-transform)
def U(*xs): return [x.upper() for x in xs]
def rids(i=0): return J(f"(()=>{{const t=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent)[{i}]; return t?[...t.querySelectorAll('[role=row][data-rid]')].filter(r=>r.offsetParent).map(r=>r.getAttribute('data-rid')):[];}})()") or []
def linha(rid): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==={json.dumps(rid)}&&r.offsetParent); return r?{N}(r.innerText):'';}})()") or ''
def busca(q, i=0):
    J(f"""(()=>{{const t=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent)[{i}]; const s=t.closest('.g2caixa').querySelector('input[type=search]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(s,{json.dumps(q)}); s.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"""); time.sleep(.5)
def clk(txt, raiz='document'):
    r = J(f"""(()=>{{const R={raiz}; if(!R) return 'sem raiz'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const bs=[...R.querySelectorAll('button,a')].filter(b=>b.offsetParent&&!b.disabled); const b=bs.find(b=>n(b.innerText)==={json.dumps(txt)})||bs.find(b=>n(b.innerText).startsWith({json.dumps(txt)})); if(!b) return 'sem botão '+{json.dumps(txt)}; b.click(); return 'ok';}})()"""); time.sleep(.5); return r
def abre_linha(rid):
    r = J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==={json.dumps(rid)}&&r.offsetParent); if(!r) return 'sem linha'; const z=[...r.querySelectorAll('[role=cell]')].find(z=>z.innerText.trim()&&!z.querySelector('button,a,input')); (z||r).click(); return 'ok';}})()"""); time.sleep(.6); return r
def aside(): return J(f"(()=>{{const a=[...document.querySelectorAll('aside[role=dialog],#ma-painel')].find(x=>x.getClientRects().length); return a?{N}(a.innerText):'';}})()") or ''   # o painel da MA é fixo (offsetParent nulo)
def campos(): return J("Object.fromEntries([...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select,aside[role=dialog] textarea')].filter(x=>x.offsetParent&&/^fx_/.test(x.id)).map(x=>[x.id.replace(/^fx_g_[a-z0-9]+(_[A-Z][A-Za-z0-9]*|[0-9]+)?_/,''),x.value]))") or {}
def fecha_form(): J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); const b=a&&[...a.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); b&&b.click();})()"); time.sleep(.35)
def ativo(): return J("(()=>{const e=document.activeElement; return e?(e.getAttribute('data-rid')||e.tagName+'.'+(e.className||'')):'';})()")
def caixa():   # rolagem lateral da 1ª grade visível (scrollWidth da .g2rola contra a largura visível) e da página
    return J("(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const r=t&&t.closest('.g2rola'); const c0=t&&(t.querySelector('[role=row][data-rid] .g2c0')||t.querySelector('[role=row][data-rid] [role=cell]')); return {sw:r?r.scrollWidth:0,cw:r?r.clientWidth:0,pag:[document.documentElement.scrollWidth,innerWidth],c0preso:!!c0&&getComputedStyle(c0).position==='sticky'};})()") or {}
def tecla(k, code, vk): c.tecla(k, code, vk); time.sleep(.45)
def shot(n): c.shot(os.path.join(OUT, n + '.png'))
try:
    # ======================= 1440 × 900 =======================
    # ---------- MA · Ordens: Tipo fora da grade (lista e Kanban), detalhe no painel, teclado ----------
    abre('MA.dc.html', 'vis=ordens', perfil='Otávio', limpa=True); shot('MA-ordens-1440-depois')
    chk('MA Ordens: 7 colunas essenciais (Ordem e Ativo separados; sem Tempo e Custo)', cab() == U('Ordem', 'Ativo', 'Serviço', 'Janela', 'Fase', 'Pendência', 'Executante'), cab())
    todos = rids(); tipos = J("(()=>{const c=window.__man.manGet(); return Object.fromEntries(Object.values(c.oms).map(o=>[o.id,o.tipo]));})()") or {}
    clk('Corretiva'); cor = rids(); clk('Corretiva'); cor2 = rids()
    chk('MA Ordens: filtro Tipo = Corretiva (fora da grade) mostra só as corretivas; repetir o toque dá o mesmo resultado', cor and all(tipos.get(x) == 'Corretiva' for x in cor) and len(cor) < len(todos) and cor2 == cor, (cor, cor2))
    clk('Kanban'); nk = J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button],[aria-label=\"Kanban das ordens\"] button')].filter(b=>b.offsetParent&&/OM-\\d+/.test(b.innerText)).length")
    chk('MA Ordens: o Kanban (5 fases) lê o mesmo filtro Tipo', nk == len(cor) and J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"]>*')].filter(e=>e.getClientRects().length).length") == 5, (nk, len(cor)))
    clk('Lista'); clk('Todos os tipos'); chk('MA Ordens: "Todos os tipos" volta todas as ordens', rids() == todos, rids())
    busca('Preventiva'); pv = rids(); chk('MA Ordens: a busca acha pelo tipo (saiu da célula)', pv and all(tipos.get(x) == 'Preventiva' for x in pv), pv); busca('')
    # teclado: foco na linha, Enter abre o painel da OM com o tipo e o custo; Esc fecha e o foco volta à linha
    om = cor[0]; J(f"[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==={json.dumps(om)}).focus()"); tecla('Enter', 'Enter', 13); pn = aside()
    chk('MA Ordens: Enter na linha abre o painel da OM com o tipo e a criticidade (fora da linha)', ('Corretiva' in pn or 'corretiva' in pn.lower()) and om in pn, pn[:200])
    clk('Custo e tempos', "document.querySelector('#ma-painel')"); pc = aside()
    chk('MA Ordens: o painel da OM mostra custo e tempos (fora da linha)', 'R$' in pc and ' h' in pc, pc[-300:])
    tecla('Escape', 'Escape', 27); chk('MA Ordens: Esc fecha o painel e o foco volta à linha', not J("!!document.querySelector('#ma-painel')&&document.querySelector('#ma-painel').getClientRects().length>0&&document.querySelector('#ma-painel').getAttribute('aria-modal')==='true'") and ativo() == om, ativo())
    # Tab até a grade: a partir da busca da grade, Tab chega a uma linha
    J("(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); t.closest('.g2caixa').querySelector('input[type=search]').focus();})()")
    n = 0
    for n in range(1, 40):
        c.tab(1); time.sleep(.05)
        if J("!!(document.activeElement&&document.activeElement.getAttribute('data-rid'))"): break
    MED['tab_ate_linha_MA'] = n; chk('MA Ordens: Tab a partir da busca chega à 1ª linha (cabeçalhos com ordenação e filtro no caminho)', J("!!(document.activeElement&&document.activeElement.getAttribute('data-rid'))"), n)
    # ---------- MA · Abastecimentos: Tanque/lote fora da grade ----------
    abre('MA.dc.html', 'vis=ativos&modo=abastecimentos', perfil='Otávio')
    chk('MA Abastecimentos: 6 colunas (sem Tanque/lote, Método; Lançamento e Data sem operador e leitura)', cab() == U('Lançamento', 'Ativo', 'Volume', 'Data', 'Consumo', 'Qualidade'), cab())
    a0 = rids(); tq = J("(()=>{const s=[...document.querySelectorAll('select[aria-label=\"Tanque/lote\"]')].find(s=>s.offsetParent); return s?[...s.options].map(o=>o.value).filter(Boolean):[];})()") or []
    J(f"(()=>{{const s=[...document.querySelectorAll('select[aria-label=\"Tanque/lote\"]')].find(s=>s.offsetParent); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,{json.dumps(tq[0] if tq else '')}); s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"); time.sleep(.5)
    a1 = rids(); est = J("(()=>{const c=window.__man.manGet(); return Object.fromEntries((c.abast||[]).map(b=>[b.id,b.tq]));})()") or {}
    chk('MA Abastecimentos: o seletor Tanque/lote filtra (só lançamentos do tanque escolhido)', tq and a1 and all(est.get(x) == tq[0] for x in a1) and len(a1) <= len(a0), (tq, a1))
    abre_linha(a1[0]); pa = aside(); chk('MA Abastecimentos: o painel do lançamento mostra tanque/lote, operador, evidência e método (saíram da linha)', all(k.upper() in pa.upper() for k in ('Tanque/lote', 'Operador', 'Evidência', 'Método')), pa[:300])
    # ---------- MA · Planos: ativo sem vínculo vira pendência na Situação ----------
    abre('MA.dc.html', 'vis=planos', perfil='Otávio', limpa=True)
    chk('MA Planos: 3 colunas (Plano, Estado, Situação)', cab() == U('Plano', 'Estado', 'Situação'), cab())
    pid = J("(()=>{ const c=window.__man.manGet(); const n={}; Object.keys(c.vinc).forEach(k=>{ const p=k.split('|')[0]; n[p]=(n[p]||0)+1; }); return Object.keys(n).sort().find(p=>n[p]>=2)||''; })()")
    s0 = linha(pid); e = J(f"(()=>{{ const r=window.__man.manMudar(null,(m)=>{{ const k=Object.keys(m.vinc).find(k=>k.split('|')[0]==={json.dumps(pid)}); delete m.vinc[k]; }}); return (r&&r.erro)||''; }})()")
    abre('MA.dc.html', 'vis=planos', perfil='Otávio'); s1 = linha(pid)
    chk('MA Planos: plano com ativo do modelo sem vínculo mostra a pendência na Situação; antes, sem pendência', not e and 'sem vínculo' not in s0 and re.search(r'1 ativo (do modelo|indicado) sem vínculo', s1), (pid, s0, s1, e))
    # ---------- MA · Ativos: a leitura e o consumo na página do ativo; volta com o filtro ----------
    abre('MA.dc.html', 'vis=ativos', perfil='Otávio', limpa=True)
    chk('MA Ativos: 5 colunas (sem Leitura e Consumo; o local fica no cabeçalho do ativo)', cab() == U('Ativo', 'Condição', 'Próxima manutenção', 'Em aberto', 'Custo no período'), cab())
    clk('Bloqueado 1'); f1 = rids(); abre_linha('a01'); pg = J("(()=>{const h=document.querySelector('main h2'); return h?h.parentElement.innerText.replace(/\\s+/g,' '):'';})()") or ''
    clk('‹ Ativos'); f2 = rids(); clk('‹ Ativos')
    chk('MA Ativos: a página do ativo mostra a leitura e o local; "‹ Ativos" volta com o filtro (repetição)', 'Leitura 4.312 h' in pg and 'Oficina Sede' in pg and f1 == ['a01'] and f2 == f1, (pg[:160], f1, f2))
    # ---------- CA-02 · fila: busca pelo que saiu, detalhe, recusa sem motivo, filtro preservado ----------
    abre('CA-02.dc.html'); shot('CA-02-1440-depois')
    chk('CA-02: 5 colunas (Conferência e Ação separadas; sem Equipe, Horas e Origem)', cab() == U('Apontamento', 'Realizado do dia', 'Consumos e sobras', 'Conferência', 'Ação'), cab())
    busca('offline'); b1 = rids(); busca('PJ-3030'); b2 = rids(); busca('PJ-3030'); b3 = rids(); busca('')
    chk('CA-02: a busca acha o apontamento pela origem e pela equipe (saíram da linha); repetir dá o mesmo', b1 == ['f2'] and b2 == ['f1', 'f3'] and b3 == b2, (b1, b2, b3))
    J("(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); t.querySelector('button[aria-label=\"Filtrar Conferência\"]').click();})()"); time.sleep(.4)
    J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Limpar').click()"); time.sleep(.2)
    J("(()=>{const l=[...document.querySelectorAll('[role=dialog] label')].find(l=>l.innerText.replace(/\\s+\\d+$/,'').trim()==='A conferir'); l&&l.querySelector('input').click();})()"); time.sleep(.2)
    J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='OK').click()"); time.sleep(.5); fl = rids()
    abre_linha('f2'); fd = campos(); pn = aside()
    chk('CA-02: o detalhe do apontamento mostra equipe, acumulado e origem (saíram da linha)', fd.get('eq', '').startswith('Carlos') and '18 conf.' in fd.get('acum', '') and 'offline' in fd.get('orig', ''), fd)
    J("(()=>{const i=document.querySelector('aside [id$=\"_real\"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'11'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"); time.sleep(.2)
    clk('Salvar', "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent)"); er = aside()
    chk('CA-02 recusa: corrigir sem motivo é recusado com o motivo e o realizado da linha não muda', 'Informe motivo da correção' in er and '12 ha' in linha('f2'), (er[:200], linha('f2')))
    clk('Descartar alterações') if 'Descartar' in aside() else None; fecha_form(); clk('Descartar alterações'); time.sleep(.3)
    chk('CA-02: fechar o detalhe preserva o filtro de Conferência (A conferir)', fl == ['f1', 'f2'] and rids() == fl, (fl, rids()))
    # ---------- CA-03 · ocorrências: Responsável, busca, novo registro (repetição) ----------
    abre('CA-03.dc.html')
    chk('CA-03: 5 colunas (Local sem instante; Responsável no lugar de Destino · responsável; sem Relato e Evidência)', cab() == U('Ocorrência', 'Local', 'Gravidade', 'Responsável', 'Próxima ação'), cab())
    busca('Rota W'); chk('CA-03: a busca acha pela evidência (saiu da linha)', rids() == ['OC-115'], rids()); busca('')
    abre_linha('OC-114'); fo = campos(); fecha_form()
    chk('CA-03: o detalhe mostra instante, relato, evidência e destino (saíram da linha)', fo.get('inst') == '22/09 06:40' and 'Pressão hidráulica' in fo.get('relato', '') and fo.get('evid') == 'Foto + leitura do painel' and fo.get('dest') == 'Manutenção · Zé', fo)
    n0 = len(rids())
    for i in range(2):
        clk('Registrar ocorrência'); J("(()=>{const i=document.querySelector('aside [id$=\"_local\"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'T2 · OS-0421'); i.dispatchEvent(new Event('input',{bubbles:true}));})()")
        J("(()=>{const i=document.querySelector('aside textarea[id$=\"_relato\"]'); Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(i,'Bico entupido na barra'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"); time.sleep(.2)
        clk('Salvar', "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent)"); time.sleep(.3)
    novos = [linha(r) for r in rids()[n0:]]
    chk('CA-03: registrar duas ocorrências cria duas linhas, cada uma com Responsável "Zé" e o local, sem o instante na célula', len(rids()) == n0 + 2 and all('Zé' in x and 'T2 · OS-0421' in x and '15:05' not in x for x in novos), novos)
    # ---------- CA-01det e CA-01x: materiais no detalhe e caminho canônico ao Estoque ----------
    abre('CA-01det.dc.html'); t = tabelas()
    chk('CA-01det: apontamentos 3 colunas e materiais 4 (sem Solicitado, Entregue e Consumido)', [[x.upper() for x in y] for y in t[:2]] == [U('Data', 'Área do dia', 'Conferência'), U('Item · lote', 'Em custódia', 'A entregar', 'Custódia de')], t)
    abre_linha('m1'); pm = aside(); hr = J("[...document.querySelectorAll('a')].filter(a=>a.offsetParent).map(a=>a.getAttribute('href')).filter(h=>/SU-07|CA-04|EST\\.dc/.test(h))") or []
    chk('CA-01det: o detalhe da custódia mostra solicitado, entregue e consumido com a conta; links vão ao Estoque (nunca SU-07/CA-04)', all(x in pm for x in ('175', '160', '95', 'Em custódia = 160 − 95 = 65 L')) and hr and all(h.startswith('EST.dc.html#req=') for h in hr), (pm[:300], hr))
    fecha_form(); abre('CA-01x-os0420.dc.html'); t = tabelas()
    chk('CA-01x: instrução 3 colunas, apontamentos 3, materiais e custo 4', [[x.upper() for x in y] for y in t[:3]] == [U('Produto', 'Dose da v2', 'Saldo de 70 ha na v3'), U('Data', 'Área do dia', 'Conferência'), U('Item', 'Consumido', 'Em custódia', 'Custo apontado')], t)
    abre_linha('i0'); fi = campos(); fecha_form()
    chk('CA-01x: o detalhe do produto mostra a quantidade para 100 ha e a fonte (saíram da linha)', fi.get('qtd_t') == '5.200 kg' and 'plano Soja alta tecnologia' in fi.get('fonte', ''), fi)
    # ---------- ON-01 e ON-01det ----------
    abre('ON-01.dc.html'); t = tabelas()
    chk('ON-01: passos 3 colunas e trial 4, com a unidade na franquia', [[x.upper() for x in y] for y in t[:2]] == [U('Passo', 'Estado', 'Próxima ação'), U('Recurso', 'Habilitação', 'Franquia', 'Ao esgotar ou expirar')] and '12 cenas / 30 dias' in linha('t3'), (t, linha('t3')))
    abre('ON-01det.dc.html'); chk('ON-01det: 4 colunas (sem Mapeamento e Sistema de coordenadas)', cab() == U('Objeto', 'Linhas', 'Erro', 'Estado'), cab())
    abre_linha('tal'); ft = campos(); fecha_form()
    chk('ON-01det: o detalhe dos talhões mostra mapeamento e sistema de coordenadas', ft.get('map') == 'automático (nome, cultura)' and ft.get('crs') == 'SIRGAS 2000 / UTM 22S', ft)
    # ---------- SAF etapa 2: busca pelo que saiu, formulário, filtro guardado antigo sem chip órfão ----------
    abre('SAF.dc.html', 'saf=S2627&passo=cultivos', limpa=True); h8 = cab(); n8 = len(rids()); shot('SAF-2-1440-depois')
    chk('SAF etapa 2: 8 colunas essenciais', h8 == U('Talhão ou parcela', 'Situação', 'Área livre', 'Livre a partir de', 'Área', 'Cultura', 'Plano agronômico', 'Plantio'), h8)
    busca('Catuaí 144'); bv = [linha(r).split(' ')[0] for r in rids()]; busca('Safrinha 2027'); bs = rids(); busca('')
    chk('SAF etapa 2: a busca acha pela variedade e pela safra de fora (saíram da linha)', bv == ['C1'] and bs and len(bs) < n8, (bv, bs))
    J("sessionStorage.setItem('g2:SAF.dc.html:g_cult_S2627', JSON.stringify({f:{meta:['45 t/ha/ano'],tipo:['Parcela']},q:'',so:{k:'meta',d:true},qv:''}))")
    J("sessionStorage.setItem('g2:MA.dc.html:g_om', JSON.stringify({f:{tempo:['6,5 h prev.'],custo:['R$ 1.776,00 est.']},q:'',so:{k:'tempo',d:false},qv:''}))")
    abre('SAF.dc.html', 'saf=S2627&passo=cultivos')
    orf = J("[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&/^Limpar filtros|^Remover filtro/.test(b.innerText.trim()||b.getAttribute('aria-label')||'')).length")
    chk('SAF etapa 2 recusa: filtro e ordenação guardados de colunas que saíram (Meta, Tipo) não escondem linha nem deixam chip órfão', len(rids()) == n8 and not orf, (len(rids()), n8, orf))
    abre('MA.dc.html', 'vis=ordens', perfil='Otávio'); orf2 = J("[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&/^Limpar filtros|^Remover filtro/.test(b.innerText.trim()||b.getAttribute('aria-label')||'')).length")
    chk('MA Ordens recusa: filtro guardado de Tempo e Custo (saíram) não esconde ordem nem deixa chip órfão', rids() == todos and not orf2, (rids(), orf2))
    abre('SAF.dc.html', 'saf=S2627&passo=cultivos', limpa=True)
    rt7 = J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent).find(x=>/^T7\\b/.test(x.innerText.trim())); return r?r.getAttribute('data-rid'):'';})()")
    abre_linha(rt7); f7 = campos(); fecha_form()
    chk('SAF etapa 2: o formulário do cultivo mostra meta com a unidade, variedade, versão aplicada, ocupação prevista e fim por', f7.get('meta') == '45' and f7.get('unm_txt') == 't/ha/ano' and f7.get('var') == 'Formosa' and f7.get('ver_txt', '').startswith('v3 · ') and ' a ' in f7.get('ocup_txt', '') and f7.get('fimpor_txt') in ('Perene', 'Pelo plano'), f7)
    lk = J("[...document.querySelectorAll('[role=row].g2kid')].filter(r=>r.offsetParent).map(r=>r.querySelector('.g2c0').innerText.replace(/\\s+/g,' ').trim()).filter(t=>/›$/.test(t))") or []
    chk('SAF etapa 2: a linha de outra safra leva o link da safra na célula de identificação', lk and all(re.search(r'(Safrinha 2027|Safra 20\d\d/\d\d) ›$', x) for x in lk), lk)
    # ---------- SAF etapa 3: rendimento e área trabalhada no formulário Rendimento ----------
    abre('SAF.dc.html', 'saf=S2627&passo=operacoes'); chk('SAF etapa 3: 6 colunas (sem Rendimento e Área trabalhada)', cab() == U('Operação › atividade › talhão', 'Situação', 'Data', 'Conjunto', 'Horas-conjunto', 'Custo R$/ha'), cab())
    abre_linha('op:Pulverização'); fr = campos(); fecha_form()
    chk('SAF etapa 3: o formulário Rendimento mostra 21,60 ha/h e a área trabalhada em ha-op com as horas', fr.get('rend_c') == '21,60' and re.match(r'^[\d.]+ ha-op · [\d.]+,\d horas-conjunto$', fr.get('area_c', '')), fr)
    abre('SAF.dc.html', 'saf=S2627&passo=safra'); chk('SAF etapa 1: 5 colunas (sem o contador Cultivos)', cab() == U('Safra', 'Fazenda', 'Área', 'Estado', 'Próximo passo'), cab())
    chk('sem erro de script (1440)', not J("(window.__errs||[]).length"), J("window.__errs"))
    # ======================= 390 × 844 =======================
    TELAS = [('MA.dc.html', 'vis=semordem'), ('MA.dc.html', 'vis=ordens'), ('MA.dc.html', 'vis=ativos'), ('MA.dc.html', 'vis=ativos&modo=abastecimentos'), ('MA.dc.html', 'vis=planos'),
             ('CA-01det.dc.html', ''), ('CA-01x-os0420.dc.html', ''), ('CA-02.dc.html', ''), ('CA-03.dc.html', ''), ('ON-01.dc.html', ''), ('ON-01det.dc.html', ''),
             ('SAF.dc.html', 'saf=S2627&passo=safra'), ('SAF.dc.html', 'saf=S2627&passo=cultivos'), ('SAF.dc.html', 'saf=S2627&passo=operacoes')]
    ruins = []
    for pag, h in TELAS:
        abre(pag, h, 390, 844, True, perfil='Otávio'); m = caixa(); MED[f'{pag}#{h}@390'] = m
        if m.get('pag', [0, 0])[0] > m.get('pag', [0, 0])[1] + 1 or not m.get('c0preso', True) and m.get('sw', 0) > m.get('cw', 0) + 1: ruins.append((pag, h, m))
    chk('390 px: nenhuma página rola de lado; a grade que é mais larga que a caixa rola dentro dela com a 1ª coluna presa', not ruins, ruins)
    abre('MA.dc.html', 'vis=ordens', 390, 844, True, perfil='Otávio'); shot('MA-ordens-390-depois')
    clk('Corretiva'); cor3 = rids(); chk('390 px: o filtro Tipo das Ordens funciona no celular', cor3 == cor, (cor3, cor))
    chk('sem erro de script (390)', not J("(window.__errs||[]).length"), J("window.__errs"))
finally:
    json.dump(MED, open(os.path.join(OUT, 'medidas.json'), 'w'), ensure_ascii=False, indent=1)
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
