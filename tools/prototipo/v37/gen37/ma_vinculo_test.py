# -*- coding: utf-8 -*-
"""MA-VINCULO (16/10/2026) · vincular ativo ↔ plano de manutenção (pedido do proprietário: "não consegui achar nada para vincular ativos a planos
de manutenção, faça algo bem melhor. E que seja intuitivo, rapido, facil e pratico"). Revisão do Codex 6226249749 incluída (base de contagem).

  U  regras sem navegador (ma_vinculo_unit.js no node): sem plano, sugestão, compatibilidade, base de contagem, prévia = gravado, lote tudo ou
     nada, chave, permissão, desvincular com OM aberta, revínculo preserva marco/ult/OM/ciclo, contraprova 1.000 h × 1.450 h, "Aplica a"
  A  1440 px: achar "Sem plano" (entrada do módulo e filtro da grade) · vincular 1 pela sugestão · prévia igual ao gravado · lote de 3 com a base
     de cada um · grupo incompatível recusado · modelo diferente com aviso · duplo clique · permissão · falha de armazenamento · recarregar ·
     desvincular com motivo e OM aberta preservada · revínculo mantém a contagem (Trator 03 continua Atrasado) · "Aplica a" com o efeito antes
     de salvar · CD-03 só leitura · teclado
  B  390 px (toque): o mesmo caminho curto, alvos de 44 px, primária alcançável, sem rolagem lateral
Uso (de gen37/, depois do build e do montar_render): python3 ma_vinculo_test.py [U] [A] [B]   (sem argumento: todas; sai 1 se algo falhar)
Contraprova: na pasta de symlinks com o _render da base, A e B reprovam (não há filtro, link, painel nem coluna Plano)."""
import os, sys, json, time, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
FAIL = []; N = [0]
PROBE = os.path.join(HERE, '_probe', 'ma_vinculo'); os.makedirs(PROBE, exist_ok=True)
def ok(cond, msg, extra=''):
    N[0] += 1; print(('  ok  ' if cond else '  FALHA ') + msg + ('' if cond else ' · ' + str(extra)[:400]), flush=True)
    if not cond: FAIL.append(msg)

def parte_U():
    print('U · regras (node)')
    import cenario, dados_manutencao as DM
    src = 'globalThis.print=(...a)=>console.log(...a);\n' + cenario.perfis_js() + DM.js_prefixo() + open(os.path.join(HERE, 'ma_vinculo_unit.js'), encoding='utf-8').read()
    p = os.path.join(HERE, '_probe', 'ma_vinculo_unit_all.js'); open(p, 'w', encoding='utf-8').write(src)
    r = subprocess.run(['node', p], capture_output=True, text=True, timeout=120); out = r.stdout.strip().splitlines()
    ok(r.returncode == 0 and out, 'U · motor JS executou sem erro', r.stderr[:400])
    for x in (json.loads(out[-1]) if out else []): ok(x['ok'], 'U · ' + x['n'], x['info'])

# ---------- navegador ----------
PAN = '#vl-painel'
def J_texto(m, sel): return m.J(f"(document.querySelector({json.dumps(sel)})||{{innerText:''}}).innerText.replace(/\\s+/g,' ')") or ''
def chip(m):   # filtro rápido "Sem plano" da barra da grade de ativos
    return m.J("(()=>{const b=[...document.querySelectorAll('main button[aria-pressed]')].find(b=>/^Sem plano/.test(b.innerText.trim())&&b.getClientRects().length); return b?{t:b.innerText.replace(/\\s+/g,' ').trim(),on:b.getAttribute('aria-pressed')}:null;})()")
def clica_chip(m):
    r = m.J("(()=>{const b=[...document.querySelectorAll('main button[aria-pressed]')].find(b=>/^Sem plano/.test(b.innerText.trim())&&b.getClientRects().length); if(!b) return false; b.click(); return true;})()"); time.sleep(.5); return r
def link_linha(m, rid, txt=None):
    return m.J(f"(()=>{{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==={json.dumps(rid)}&&r.getClientRects().length); if(!r) return null;"
               f" const a=[...r.querySelectorAll('a')].find(a=>/^Vincular ao |^Criar plano/.test(a.innerText.trim())); return a?a.innerText.trim():null;}})()")
def espera(m, cond, t=8):
    fim = time.time() + t
    while time.time() < fim:
        try:
            if m.J(cond): return True
        except Exception: pass
        time.sleep(.15)
    return False
def abre_link(m, rid):
    espera(m, f"[...document.querySelectorAll('[role=row][data-rid]')].some(r=>r.getAttribute('data-rid')==={json.dumps(rid)}&&r.getClientRects().length&&[...r.querySelectorAll('a')].some(a=>/^Vincular ao /.test(a.innerText.trim())))")
    r = m.J(f"(()=>{{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==={json.dumps(rid)}&&r.getClientRects().length); if(!r) return false;"
            f" const a=[...r.querySelectorAll('a')].find(a=>/^Vincular ao /.test(a.innerText.trim())); if(!a) return false; a.focus(); a.click(); return true;}})()")
    if r: espera(m, f"!!document.querySelector('{PAN} [data-aid]')")
    time.sleep(.3); return r
def pan(m): return J_texto(m, PAN)
def aberto(m): return bool(m.J(f"!!document.querySelector('{PAN}')"))
def prim(m):   # primária do painel (rodapé): texto, desligada, motivo
    return m.J(f"(()=>{{const b=document.querySelector('{PAN} .ma-rod button:last-child'); const w=document.querySelector('#vl-why'); return b?{{t:b.innerText.trim(),dis:b.disabled,why:w?w.innerText.trim():''}}:null;}})()") or {}
def marcado(m, aid): return m.J(f"(()=>{{const i=document.querySelector('{PAN} [data-aid=\"{aid}\"] input[type=checkbox]'); return i?{{on:i.checked,dis:i.disabled}}:null;}})()")
def linha_vl(m, aid): return m.J(f"(()=>{{const e=document.querySelector('{PAN} [data-aid=\"{aid}\"]'); return e?e.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def plano_ativo(m): return m.J(f"(()=>{{const b=[...document.querySelectorAll('{PAN} [role=radio]')].find(b=>b.getAttribute('aria-checked')==='true'); return b?b.innerText.replace(/\\s+/g,' ').trim():'';}})()") or ''
def botao(m, txt, root=PAN): return m.clk(txt, root, w=.5)
def salvar(m, w=.9):
    r = m.J(f"(()=>{{const b=document.querySelector('{PAN} .ma-rod button:last-child'); if(!b||b.disabled) return false; b.click(); return true;}})()"); time.sleep(w); return r
def foco(m): return m.J("(()=>{const a=document.activeElement; if(!a||a===document.body) return 'BODY'; return (a.getAttribute('data-rid')||a.id||a.innerText||a.tagName).replace(/\\s+/g,' ').slice(0,60);})()")
def plan_row(m, rid): return m.linha(rid)
def foto(m, nome): m.c.shot(os.path.join(PROBE, nome))
def vinc(m, k): return m.man(f"m.vinc[{json.dumps(k)}]||null")
def toast_ultimo(m): return m.toast()
def larg(m): return m.J("document.documentElement.scrollWidth-document.documentElement.clientWidth")
LS_FALHA = ("(()=>{ if(!window.__si0) window.__si0=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){ if(k==='talhao-os-cenario-v1') "
            "throw new DOMException('quota sintética','QuotaExceededError'); return window.__si0.call(this,k,v); }; return 1; })()")
LS_VOLTA = "(()=>{ if(window.__si0) Storage.prototype.setItem=window.__si0; return 1; })()"
# plano de teste (o seed não tem 3 ativos sem plano no mesmo grupo): PM-11 Tratores · lubrificação semanal, publicado, para os tratores 02, 03 e 04
PM11 = ("(()=>{ const M=window.__man; M.manMudar(null,(m)=>{ m.planos['PM-11']={id:'PM-11',nome:'Tratores · lubrificação semanal',grupo:'Tratores',aplica:{t:'ativos',v:['a02','a03','a04']},"
        "estado:'Ativo',versao:1,rasc:null,hist:[{v:1,at:'23/09/2026'}],servicos:[{id:'s1',nome:'Lubrificação semanal',gat:{h:50,d:7},tol:{h:5,d:1},base:'exec',cumpre:[],tempo:1,esp:'Lubrificador',"
        "tarefas:[{t:'Lubrificar pontos de graxa',tipo:'Serviço'}],pecas:[{item:'GR-EP2',qtd:0.5}]}]}; m.ordemPlanos.push('PM-11'); m.seqpm=12; return {msg:''}; }); return 1; })()")

def parte_A():
    print('A · 1440 px')
    from ma_lib import MA
    m = MA(1440, 1000); J = m.J; m.ok = ok
    try:
        # A1 · achar: a entrada do módulo diz "4 ativos sem plano" e leva à lista já filtrada, com a primária do lote
        m.ir('', perfil='Otávio', limpa=True, pagina='MOD-MAN.dc.html'); av = J("(()=>{const a=document.querySelector('a.mod-aviso'); return a?{t:a.innerText.replace(/\\s+/g,' ').trim(),h:a.getAttribute('href')}:null;})()")
        ok(av and '4 ativos sem plano de manutenção' in av['t'] and av['h'] == 'MA.dc.html#vis=ativos&pend=semplano', 'A1 · entrada do módulo: "4 ativos sem plano de manutenção · Vincular ›" leva a Ativos › Sem plano', av)
        foto(m, 'A1_entrada_1440.png')
        if av: J("document.querySelector('a.mod-aviso').click()"); time.sleep(1.6)
        else: m.ir('vis=ativos&pend=semplano')
        espera(m, "document.querySelectorAll('[role=row][data-rid]').length>0"); rows = m.linhas(0); ch = chip(m); hp = J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==='Vincular a plano'); return b?{dis:b.disabled}:null;})()")
        ok(sorted(rows) == ['a07', 'a09', 'a10', 'a12'] and ch and ch['on'] == 'true' and 'pend=semplano' in (m.hash() or '') and hp and not hp['dis'],
           'A1 · um toque: Ativos com o filtro rápido "Sem plano" ligado (4 linhas) e a primária "Vincular a plano" no cabeçalho', [rows, ch, m.hash(), hp])
        foto(m, 'A1_ativos_sem_plano_1440.png')
        cel = {r: link_linha(m, r) for r in rows}
        ok(cel == {'a07': 'Criar plano ›', 'a09': 'Vincular ao PM-08 ›', 'a10': 'Criar plano ›', 'a12': 'Vincular ao PM-07 ›'}, 'A1 · coluna Plano: sugestão explícita por linha (Gotejo T7 → PM-07; Máquina TSI → PM-08) ou Criar plano', cel)
        clica_chip(m); n_todos = len(m.linhas(0)); a03 = m.linha('a03'); a02 = m.linha('a02')
        ok(n_todos == 16 and 'PM-02' in a03 and 'Atrasado' in a03 and 'PM-01' in a02 and 'Vence em 55 h' in a02 and chip(m)['on'] == 'false',
           'A1 · sem o filtro: 16 ativos; a coluna Plano diz o plano e a situação (Trator 03 PM-02 Atrasado; Trator 02 PM-01 Vence em 55 h)', [n_todos, a03[:120], a02[:120]])
        hd = J("[...document.querySelectorAll('main [role=columnheader]')].filter(e=>e.getClientRects().length).map(e=>e.innerText.trim().toUpperCase())") or []
        ok(len(hd) > 1 and hd[1].startswith('PLANO'), 'A1 · "Plano" é a 2ª coluna, logo depois do ativo', hd[:4])
        m.sem_erro('A1')
        # A1b · a primária do lote: os 4 sem plano no painel, um plano por vez, quem não serve fica de fora com o motivo
        clica_chip(m); m.clk('Vincular a plano', 'header'); ops = J(f"[...document.querySelectorAll('{PAN} [role=radio]')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())") or []
        ms = {a: marcado(m, a) for a in ('a07', 'a09', 'a10', 'a12')}; l9 = linha_vl(m, 'a09')
        ok(len(ops) == 2 and ops[0].startswith('PM-07') and ops[1].startswith('PM-08') and ms['a12'] == {'on': True, 'dis': False} and ms['a09'] == {'on': False, 'dis': True}
           and 'Não serve: PM-07 é de Irrigação e Máquina TSI é de Beneficiamento' in l9 and 'Um plano por vez' in pan(m),
           'A1b · "Vincular a plano" com os 4 sem plano: opções PM-07 e PM-08; no PM-07 só o Gotejo T7 entra, os outros com o motivo', [ops, ms, l9[:160]])
        J(f"[...document.querySelectorAll('{PAN} [role=radio]')][1].click()"); time.sleep(.5); ms2 = {a: marcado(m, a) for a in ('a09', 'a12')}
        ok(ms2 == {'a09': {'on': True, 'dis': False}, 'a12': {'on': False, 'dis': True}} and plano_ativo(m).startswith('PM-08'), 'A1b · trocar para o PM-08 marca a Máquina TSI e tira o Gotejo T7', ms2)
        J("(()=>{const b=document.querySelector('#vl-painel button[aria-label=Fechar]'); if(b) b.click();})()"); time.sleep(.4); m.clk('Descartar alterações', PAN); time.sleep(.3)
        J("(()=>{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==='a07'); const a=r&&[...r.querySelectorAll('a')].find(a=>/^Criar plano/.test(a.innerText.trim())); if(a) a.click();})()"); time.sleep(.8)
        np = J("(()=>{const n=document.querySelector('#np_nome'); return n?n.value:null;})()"); J("(()=>{const b=document.querySelector('#np-painel button[aria-label=Fechar]'); if(b) b.click();})()"); time.sleep(.3)
        ok(np == 'Distribuidor 3 t · preventiva' and sorted(m.linhas(0)) == ['a07', 'a09', 'a10', 'a12'], 'A1b · "Criar plano ›" abre o Novo plano já com o Distribuidor; a lista filtrada continua', [np, m.linhas(0)])
        # A2 · um ativo pela sugestão: abrir (1) · contar de agora (2) · Vincular ao PM-07 (3)
        abre_link(m, 'a12')
        p0 = pan(m); pr = prim(m); mk = marcado(m, 'a12'); lv = linha_vl(m, 'a12')
        ok(aberto(m) and plano_ativo(m).startswith('PM-07') and mk == {'on': True, 'dis': False} and 'Modelo diferente: cabeçal + injetora de fertilizante' in lv,
           'A2 · o link abre o painel com o PM-07 já escolhido, Gotejo T7 marcado e o aviso de modelo diferente (permitido)', [plano_ativo(m), mk, lv[:200]])
        ok(pr.get('dis') and 'Escolha como contar' in pr.get('why', '') and 'Contar de agora' in p0 and 'Informar a última execução' in p0,
           'A2 · sem execução registrada a primária fica desligada até a pessoa escolher (nada é inferido)', [pr, p0[:300]])
        botao(m, 'Contar de agora'); lv = linha_vl(m, 'a12'); pr = prim(m)
        prev = J(f"(()=>{{const e=document.querySelector('{PAN} [data-aid=\"a12\"] .vl-prev'); return e?e.innerText.replace(/\\s+/g,' ').trim():'';}})()") or ''
        ok('contando de agora: 23/09 · 5.210 h (marco estimado)' in lv and prev.startswith('Preventiva mensal próxima em') and pr.get('t') == 'Vincular ao PM-07' and not pr.get('dis'),
           'A2 · contar de agora mostra a origem (23/09 · 5.210 h, estimado) e a prévia; primária "Vincular ao PM-07"', [lv[:240], prev, pr])
        foto(m, 'A2_painel_um_1440.png')
        rev0 = m.man("m.rev"); salvar(m); t2 = m.toast(); v12 = vinc(m, 'PM-07|a12'); fo = foco(m)
        ok(not aberto(m) and 'Gotejo T7 vinculado ao PM-07' in t2 and v12 and v12['marco']['leit'] == 5210 and v12['marco']['est'] is True and m.man("m.rev") == rev0 + 1,
           'A2 · Vincular grava uma vez (recibo depois da gravação): marco 23/09 · 5.210 h estimado', [t2[:160], v12, rev0, m.man("m.rev")])
        ok(sorted(m.linhas(0)) == ['a07', 'a09', 'a10'] and chip(m)['on'] == 'true' and fo in ('a07', 'a09', 'a10'),
           'A2 · volta à mesma lista filtrada (3 sem plano) com o foco numa linha dela', [m.linhas(0), fo])
        m.ir('plano=PM-07'); gr = m.linha('PM-07|a12')
        ok(prev.split('próxima em ')[1].split(' · ')[0] in gr and 'Preventiva mensal' in gr, 'A2 · prévia igual ao vencimento gravado (Ativos deste plano mostra a mesma data)', [prev, gr[:200]])
        m.sem_erro('A2')
        # A3 · lote: 3 tratores num plano (PM-11), a base de cada um pela leitura dele mesmo, prévia por ativo, tudo numa gravação
        J(PM11); m.ir('plano=PM-11'); sec = m.body()
        ok('ATIVOS DESTE PLANO · 0' in sec.upper() and 'Vincular ativos' in sec, 'A3 · detalhe do plano: seção "Ativos deste plano · 0" com "Vincular ativos" nela', sec[:200])
        m.clk('Vincular ativos', 'main'); ms = {a: marcado(m, a) for a in ('a02', 'a03', 'a04', 'a01')}
        ok(aberto(m) and ms['a02']['on'] and ms['a03']['on'] and ms['a04']['on'] and ms['a01'] and not ms['a01']['on'] and not ms['a01']['dis'],
           'A3 · lista já marcada com os do "Aplica a" (Trator 02, 03 e 04); Trator T1 (mesma classe) aparece desmarcado', ms)
        botao(m, 'Contar de agora'); ls = {a: linha_vl(m, a) for a in ('a02', 'a03', 'a04')}; pr = prim(m)
        ok('2.988 h' in ls['a02'] and '5.120 h' in ls['a03'] and '3.410 h' in ls['a04'] and all('Lubrificação semanal próxima em' in x for x in ls.values()) and pr.get('t') == 'Vincular 3 ativos ao PM-11',
           'A3 · cada ativo conta da própria leitura (2.988 · 5.120 · 3.410 h), com prévia por ativo; "Vincular 3 ativos ao PM-11"', [ls, pr])
        foto(m, 'A3_lote_1440.png')
        J(f"(()=>{{const b=document.querySelector('{PAN} .ma-rod button:last-child'); b.click(); b.click(); return 1;}})()"); time.sleep(1)   # duplo clique
        vs = {a: vinc(m, 'PM-11|' + a) for a in ('a02', 'a03', 'a04')}; rec = m.man("Object.values(m.recibos||{}).filter(r=>r.nome==='vincular').length")
        ok(all(vs.values()) and [vs[a]['marco']['leit'] for a in ('a02', 'a03', 'a04')] == [2988, 5120, 3410] and rec == 2 and '3 ativos vinculados ao PM-11' in m.toast(),
           'A3 · duplo clique grava uma vez só (2 recibos de vínculo na sessão: A2 e A3)', [vs, rec, m.toast()[:120]])
        sec = m.body()
        ok('ATIVOS DESTE PLANO · 3' in sec.upper() and 'Todos os ativos deste plano' not in sec, 'A3 · a seção mostra os 3 com a base e o próximo vencimento', sec[:300])
        m.sem_erro('A3')
        # A4 · grupo incompatível recusado (busca no painel) e "Informar a última execução" com atalhos e validação
        m.ir('plano=PM-08'); m.clk('Vincular ativos', 'main'); ms = marcado(m, 'a09')
        m.setv('#vl_q', 'Trator 02'); l2 = linha_vl(m, 'a02'); mk2 = marcado(m, 'a02')
        ok(ms == {'on': False, 'dis': False} and 'Não serve: PM-08 é de Beneficiamento e Trator 02 é de Tratores' in l2 and mk2 == {'on': False, 'dis': True},
           'A4 · no plano, a busca acha o trator e diz por que não serve (sem caixa para marcar); Máquina TSI é candidata (mesmo grupo)', [ms, l2[:200], mk2])
        m.J("(()=>{const b=document.querySelector('#vl-painel button[aria-label=Fechar]'); if(b) b.click();})()"); time.sleep(.4)
        m.ir('vis=ativos&pend=semplano'); abre_link(m, 'a09'); busca1 = m.J("!!document.querySelector('#vl_q')")
        botao(m, 'Informar a última execução'); salvar(m, .5); e0 = linha_vl(m, 'a09')
        ok(busca1 is False, 'A4 · painel de um ativo sem busca (lista curta: sem ruído)', busca1)
        ok(aberto(m) and 'Informe a data da última execução' in e0 and 'Informe a leitura' in e0, 'A4 · informar a última execução: data e leitura pedidas no campo', e0[:240])
        botao(m, 'Hoje'); m.setv('#vl_leit_a09', '-3'); salvar(m, .5); e1 = linha_vl(m, 'a09')
        botao(m, 'Atual · 720 h'); lv = J("document.querySelector('#vl_leit_a09').value"); dv = J("document.querySelector('#vl_data_a09').value")
        ok('Zero ou mais.' in e1 and lv == '720' and dv == '2026-09-23', 'A4 · atalhos "Hoje" e "Atual · 720 h" (a leitura do próprio ativo); leitura negativa recusada', [e1[:200], lv, dv])
        m.J("(()=>{const b=document.querySelector('#vl-painel button[aria-label=Fechar]'); if(b) b.click();})()"); time.sleep(.4); m.clk('Descartar alterações', PAN); time.sleep(.3)
        ok(not aberto(m), 'A4 · fechar com alteração pede confirmação e descarta')
        # A5 · permissão: Zé vê o motivo e a primária desligada (mesma regra do plano)
        m.ir('vis=ativos&pend=semplano', perfil='Zé'); hp = J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==='Vincular a plano'); return b?{dis:b.disabled,t:b.title}:null;})()")
        abre_link(m, 'a09'); botao(m, 'Contar de agora'); pr = prim(m)
        ok(hp and hp['dis'] and 'Ação do Otávio' in hp['t'] and pr.get('dis') and 'Ação do Otávio' in pr.get('why', ''), 'A5 · Zé: "Vincular a plano" e "Vincular ao PM-08" desligados com o motivo (Ação do Otávio)', [hp, pr])
        m.ir('plano=PM-07', perfil='Zé'); bz = J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.innerText.trim()==='Vincular ativos'); return b?b.disabled:'sem';})()")
        ok(bz is True or bz == 'sem', 'A5 · Zé no plano: "Vincular ativos" desligado (ou ausente sem candidato)', bz)
        # A6 · falha de armazenamento: nada grava, o painel fica com as escolhas; de volta, o mesmo toque grava
        m.ir('vis=ativos&pend=semplano', perfil='Otávio'); abre_link(m, 'a09'); botao(m, 'Contar de agora'); J(LS_FALHA); salvar(m); f = pan(m)
        ok(aberto(m) and 'Não foi possível gravar' in f and 'Suas escolhas continuam aqui' in f and J("document.querySelector('#vl-painel [aria-pressed=true]').innerText.trim()") == 'Contar de agora'
           and marcado(m, 'a09')['on'] and m.man("!!m.vinc['PM-08|a09']") is False, 'A6 · gravação recusada: nada vinculado, painel aberto com o plano, a escolha e a caixa marcada', f[:200])
        J(LS_VOLTA); salvar(m); ok(not aberto(m) and m.man("!!m.vinc['PM-08|a09']") is True and 'Máquina TSI vinculado ao PM-08' in m.toast(), 'A6 · gravação de volta: o mesmo toque vincula', m.toast()[:120])
        # A7 · recarregar preserva
        m.recarregar(); a09 = m.linha('a09'); a12 = m.linha('a12')
        m.ir('vis=ativos'); a09 = m.linha('a09'); a12 = m.linha('a12')
        ok('PM-08' in a09 and 'PM-07' in a12 and 'Sem plano' not in a12, 'A7 · recarregar: Gotejo T7 no PM-07 e Máquina TSI no PM-08', [a09[:120], a12[:120]])
        # A8 · desvincular com motivo: a OM aberta continua, o histórico também; revincular retoma a contagem (Trator 02 e OM-0234)
        u0 = vinc(m, 'PM-01|a02'); m.ir('plano=PM-01')
        J("(()=>{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==='PM-01|a02'); const b=r&&r.querySelector('button.g2mais'); if(b) b.click(); return !!b;})()"); time.sleep(.4)
        m.clk('Desvincular'); d = J_texto(m, '#dv-painel'); dp = J("(()=>{const b=document.querySelector('#dv-painel .ma-rod button:last-child'); return b?{t:b.innerText.trim(),dis:b.disabled}:null;})()")
        ok('OM-0234' in d and 'continua aberta' in d and 'ficam guardadas' in d and dp and dp['dis'], 'A8 · Desvincular (⋯ da linha) avisa da OM-0234 aberta e pede o motivo antes', [d[:300], dp])
        m.clk('Vínculo feito por engano', '#dv-painel'); J("document.querySelector('#dv-painel .ma-rod button:last-child').click()"); time.sleep(.9); td = m.toast(); u1 = vinc(m, 'PM-01|a02')
        ok('desvinculado do PM-01' in td and 'OM-0234 continua aberta' in td and m.man("m.oms['OM-0234'].etapa") == 'A liberar' and u1['fim']['mot'] == 'Vínculo feito por engano'
           and u1['ult'] == u0['ult'] and u1['marco'] == u0['marco'], 'A8 · desvinculado com motivo; OM-0234 continua em A liberar; marco e últimas execuções guardados', [td[:160], u1])
        m.ir('vis=ativos'); a02 = m.linha('a02')
        ok('PM-11' in a02 and 'PM-01' not in a02 and 'Sem plano' not in a02, 'A8 · Trator 02 segue no PM-11 (o outro plano dele): não fica "Sem plano" por desvincular um', a02[:160])
        m.ir('plano=PM-01'); m.clk('Vincular ativos', 'main'); lv = linha_vl(m, 'a02')
        ok('Retoma a contagem de antes' in lv and 'Vínculo feito por engano' in lv and 'Contar de agora' not in pan(m), 'A8 · revínculo: retoma a contagem de antes (sem escolher base de novo)', lv[:240])
        salvar(m); u2 = vinc(m, 'PM-01|a02'); om = m.man("(()=>{const l=window.__man.manLinhas(m,'PM-01').find(x=>x.aid==='a02'&&x.sid==='s1'); return l&&l.om?l.om.id:'';})()")
        ok(u2 and not u2.get('fim') and u2['ult'] == u0['ult'] and u2['marco'] == u0['marco'] and om == 'OM-0234' and len(u2.get('hist', [])) == 1,
           'A8 · revinculado: marco, últimas execuções e o ciclo da OM-0234 iguais (nenhuma ordem duplicada)', [u2, om])
        # A9 · contraprova Codex 6226249749 na tela: Trator 03 (PM-02, referência 4.840 h, leitura 5.120 h) continua Atrasado depois de desvincular e revincular
        m.ir('plano=PM-02'); J("(()=>{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==='PM-02|a03'); const b=r&&r.querySelector('button.g2mais'); if(b) b.click();})()"); time.sleep(.4)
        m.clk('Desvincular'); m.setv('#dv_mot', 'teste de revínculo'); J("document.querySelector('#dv-painel .ma-rod button:last-child').click()"); time.sleep(.8)
        m.clk('Vincular ativos', 'main'); l3 = linha_vl(m, 'a03'); salvar(m); m.ir('vis=ativos'); a03 = m.linha('a03')
        x3 = m.man("(()=>{const l=window.__man.manLinhas(m,'PM-02').find(x=>x.aid==='a03'); return l?{sit:l.x.sit,due:l.x.gats[0].due}:null;})()")
        ok('Retoma a contagem de antes' in l3 and x3 == {'sit': 'Vencida', 'due': 5090} and 'PM-02' in a03 and 'Atrasado' in a03, 'A9 · revincular não esconde atraso: Trator 03 segue Vencida em 5.090 h (Atrasado na coluna Plano)', [l3[:160], x3, a03[:160]])
        # A10 · "Aplica a": trocar para modelo mostra o efeito antes de salvar e não perde vínculo
        m.ir('plano=PM-07'); m.clk('Editar plano'); m.setv('#np_tipo', 'modelo'); m.setv('#np_modelo', 'motobomba 125 cv'); ef = J_texto(m, '#np-painel')
        ok('AO SALVAR' in ef.upper() and 'Vale para todos do modelo motobomba 125 cv (1 ativo)' in ef and 'Bomba do Pivô 2, Gotejo T7 seguem vinculados (outro modelo)' in ef,
           'A10 · Editar plano: o efeito de trocar "Aplica a" aparece antes de salvar', ef[-400:])
        m.clk('Salvar', '#np-painel'); ap = m.man("m.planos['PM-07'].aplica"); nv = m.man("Object.keys(m.vinc).filter(k=>k.indexOf('PM-07|')===0&&!m.vinc[k].fim).length")
        ok(ap == {'t': 'modelo', 'v': ['motobomba 125 cv'], 'x': ['a11', 'a12']} and nv == 3 and 'Todos do modelo motobomba 125 cv (1 ativo) + 2 ativos de outro modelo' in m.body(),
           'A10 · salvo: modelo + 2 de outro modelo; os 3 vínculos continuam', [ap, nv])
        m.sem_erro('A10')
        # A11 · teclado: Tab fica no painel, Esc fecha e o foco volta para quem abriu
        m.ir('plano=PM-11')
        bt = J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.innerText.trim()==='Vincular ativos'); if(!b) return false; b.focus(); b.click(); return true;})()"); time.sleep(.6)
        for _ in range(25): m.tecla('Tab', 'Tab', 9)
        dentro = J(f"!!(document.activeElement&&document.activeElement.closest('{PAN}'))"); m.tecla('Escape', 'Escape', 27); time.sleep(.5)
        ok(bt and dentro and not aberto(m) and foco(m) == 'Vincular ativos', 'A11 · teclado: Tab preso no painel, Esc fecha, foco volta a "Vincular ativos"', [bt, dentro, foco(m)])
        # A12 · inativo não é candidato nem "Sem plano"
        J("window.__man.manMudar(null,(m)=>{ m.ativos.a10.sit='Inativo'; return {msg:''}; })"); m.ir('vis=ativos'); ch = chip(m); a10 = m.linha('a10')
        ok(ch and ch['t'] == 'Sem plano 1' and 'Ativo inativo' in a10, 'A12 · Esqueletadeira inativa: fora do "Sem plano" (só o Distribuidor sobra) e sem sugestão', [ch, a10[:120]])
        # A13 · CD-03: "Plano: PM-01 ›" só leitura, com link para a Manutenção (um único lugar edita)
        m.ir('', pagina='CD-03.dc.html'); m.t.openrow(0, 'Trator 02'); time.sleep(.4)
        lk = J("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>[a.innerText.trim(),a.getAttribute('href')])") or []
        m.J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); if(b) b.click();})()"); time.sleep(.3); m.t.openrow(0, 'Distribuidor 3 t'); time.sleep(.4)
        lk7 = J("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>[a.innerText.trim(),a.getAttribute('href')])") or []
        ok(['Plano: PM-01 ›', 'MA.dc.html#plano=PM-01'] in lk and ['Plano: PM-11 ›', 'MA.dc.html#plano=PM-11'] in lk and ['Sem plano de manutenção · Vincular na Manutenção ›', 'MA.dc.html#vis=ativos&vincular=a07'] in lk7
           and not any('› ›' in x[0] for x in lk + lk7),
           'A13 · CD-03: "Plano: PM-01 ›" e "Plano: PM-11 ›" no Trator 02; Distribuidor: "Sem plano · Vincular na Manutenção ›"', [lk, lk7])
        m.sem_erro('A13')
        # A14 · revisão Codex 6229032017: quem rege o vínculo é a versão publicada (o rascunho só avisa) e publicar não deixa ativo sem gatilho
        PL = ("(()=>{ window.__man.manMudar(null,(m)=>{ const s=(g)=>({id:'s1',nome:'Revisão',gat:g,tol:{},base:'exec',cumpre:[],tempo:1,esp:'Mecânico',tarefas:[{t:'Revisar',tipo:'Serviço'}],pecas:[]});"
              " m.planos['PM-12']={id:'PM-12',nome:'Implementos · revisão',grupo:'Implementos',aplica:{t:'ativos',v:['a07']},estado:'Ativo',versao:1,hist:[{v:1,at:'23/09/2026'}],servicos:[s(%s)],rasc:{v:2,servicos:[s(%s)]}};"
              " if(m.ordemPlanos.indexOf('PM-12')<0) m.ordemPlanos.push('PM-12'); %s return {msg:''}; }); return 1; })()")
        m.ir('vis=ativos', perfil='Otávio', limpa=True); J(PL % ("{km:1000}", "{d:30}", "")); m.ir('plano=PM-12'); m.clk('Vincular ativos', 'main'); l7 = linha_vl(m, 'a07'); k7 = marcado(m, 'a07')
        ok('Não serve: Revisão conta só por 1.000 km e Distribuidor 3 t conta horas (horímetro): nenhum gatilho se aplica na v1 em vigor' in l7 and k7 == {'on': False, 'dis': True},
           'A14 · publicado só por km (rascunho por dias) num ativo por horímetro: recusado no painel com o motivo da versão em vigor', [l7[:220], k7])
        m.ir('vis=ativos', perfil='Otávio', limpa=True); J(PL % ("{d:30}", "{km:1000}", "m.vinc['PM-12|a07']={marco:{data:'2026-09-20',leit:600,om:null},ult:{}};")); m.ir('plano=PM-12')
        pb = J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>/^Publicar v2/.test(b.innerText.trim())); return b?{dis:b.disabled,t:b.title}:null;})()")
        a7 = m.linha('PM-12|a07')
        ok(pb and pb['dis'] and 'Ativo vinculado ficaria sem gatilho: Revisão conta só por 1.000 km e Distribuidor 3 t conta horas' in pb['t'] and 'Em dia' in a7,
           'A14 · publicado por dias e rascunho só por km: o vínculo vale pelo publicado (Em dia) e "Publicar v2" fica desligado com o motivo', [pb, a7[:160]])
        m.sem_erro('A14')
    finally:
        fecha(m)

def parte_B():
    print('B · 390 px (toque)')
    from ma_lib import MA
    m = MA(390, 844); J = m.J; m.ok = ok; m.c.call('Emulation.setTouchEmulationEnabled', {'enabled': True, 'maxTouchPoints': 5})
    try:
        m.ir('', perfil='Otávio', limpa=True, pagina='MOD-MAN.dc.html'); av = J("(()=>{const a=document.querySelector('a.mod-aviso'); if(!a) return null; const r=a.getBoundingClientRect(); return {h:r.height,w:r.right};})()")
        ok(av and av['h'] >= 44 and av['w'] <= 390 and larg(m) <= 0, 'B1 · entrada do módulo: aviso com 44 px de alvo, sem rolagem lateral', [av, larg(m)])
        foto(m, 'B1_entrada_390.png')
        if av: J("document.querySelector('a.mod-aviso').click()"); time.sleep(1.6)
        else: m.ir('vis=ativos&pend=semplano')
        espera(m, "document.querySelectorAll('[role=row][data-rid]').length>0"); rows = m.linhas(0)
        cartao = J("(()=>{const r=[...document.querySelectorAll('[data-rid=\"a12\"]')].find(e=>e.getClientRects().length); if(!r) return null; const a=[...r.querySelectorAll('a')].find(a=>/^Vincular ao/.test(a.innerText.trim())); const b=a&&a.getBoundingClientRect(); return b&&b.width>0?{h:b.height,r:b.right,t:a.innerText.trim()}:null;})()")
        ok(sorted(rows) == ['a07', 'a09', 'a10', 'a12'] and larg(m) <= 0 and cartao and cartao['h'] >= 44, 'B1 · Ativos › Sem plano no celular: 4 ativos, "Vincular ao PM-07 ›" à vista na linha (44 px), sem rolagem lateral da página', [rows, cartao, larg(m)])
        foto(m, 'B1_ativos_390.png')
        abre_link(m, 'a12'); botao(m, 'Contar de agora')
        g = J(f"(()=>{{const p=document.querySelector('{PAN}'); const b=p.querySelector('.ma-rod button:last-child'); const r=b.getBoundingClientRect(); const ck=p.querySelector('[data-aid=\"a12\"] .vl-ck').getBoundingClientRect();"
              " const op=p.querySelector('[role=radio]').getBoundingClientRect(); const ag=[...p.querySelectorAll('button')].find(x=>x.innerText.trim()==='Contar de agora').getBoundingClientRect();"
              " return {pw:p.getBoundingClientRect().width,bb:r.bottom,bh:r.height,ck:ck.height,op:op.height,ag:ag.height,vh:innerHeight};})()")
        ok(g and g['pw'] <= 390 and g['bb'] <= g['vh'] and g['bh'] >= 44 and g['ck'] >= 44 and g['op'] >= 44 and g['ag'] >= 44,
           'B2 · painel a 390 px: largura da tela, primária alcançável (sem rolar) e alvos de 44 px (caixa, plano, contar de agora, Vincular)', g)
        foto(m, 'B2_painel_390.png')
        salvar(m); ok(not aberto(m) and m.man("!!m.vinc['PM-07|a12']") is True and 'Gotejo T7 vinculado ao PM-07' in m.toast(), 'B2 · 3 toques: link, Contar de agora, Vincular ao PM-07', m.toast()[:120])
        J(PM11); m.ir('plano=PM-11'); m.clk('Vincular ativos', 'main'); botao(m, 'Informar a última execução')
        gi = J(f"(()=>{{const p=document.querySelector('{PAN}'); const d=p.querySelector('#vl_data_a02').getBoundingClientRect(), l=p.querySelector('#vl_leit_a02').getBoundingClientRect(); return {{d:d.height,l:l.height,dr:d.right,lr:l.right,im:p.querySelector('#vl_leit_a02').getAttribute('inputmode')}};}})()")
        ok(gi and gi['d'] >= 44 and gi['l'] >= 44 and gi['dr'] <= 390 and gi['lr'] <= 390 and gi['im'] == 'numeric', 'B3 · lote no celular: data e leitura com 44 px, teclado numérico, dentro da tela', gi)
        foto(m, 'B3_lote_390.png')
        m.sem_erro('B')
    finally:
        fecha(m)

def fecha(m):
    try: m.c.close()
    finally: m.t.srv.terminate()

if __name__ == '__main__':
    os.chdir(HERE); ps = [a for a in sys.argv[1:] if a in ('U', 'A', 'B')] or ['U', 'A', 'B']
    for p in ps:
        try: globals()['parte_' + p]()
        except Exception as e: ok(False, f'{p} · interrompida por exceção (o resto da parte não rodou)', repr(e)[:300])
    print(f'RESULTADO: {N[0] - len(FAIL)}/{N[0]} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
    sys.exit(1 if FAIL else 0)
