# -*- coding: utf-8 -*-
"""SUP · atrito antes × depois no Estoque (AGENTS §3.3; docs/suprimentos-simplificado §8, AC-SUP-14) · navegador, 1440 px.
Mede, no mesmo cenário (semente do protótipo) e com a mesma régua, os cliques e os campos de cada tarefa do almoxarife e da gestora:
  clique = botão, linha, chip, link ou escolha numa lista; campo = valor digitado.
  Não contam: abrir o Estoque pelo menu (igual nos dois), a preparação do cenário (cenMudar, igual nos dois) e o perfil de quem age
  (menu lateral: no software real é o login, CF-02).
Cada tarefa confere o efeito no cenário (quem conta cliques de um caminho que não grava não mede nada).
Uso (de gen37/, depois do build):
  python3 sup_atrito_test.py                      mede o depois (build atual) e compara com o antes guardado em ANTES (medido no 99537ca)
  python3 sup_atrito_test.py --base <gen37>       mede o antes de novo numa cópia da base 99537ca com _render montado e compara
Sai 1 se uma tarefa não gravar o efeito esperado, se o antes medido divergir do guardado, ou se o depois piorar sem dano nomeado (PIORA_OK):
piora = mais cliques + campos no total, ou mais campos (digitar custa mais que tocar)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import est_lib
from est_lib import Est

# antes medido com --base na cópia do 99537ca (base desta frente), 09/10/2026: {tarefa: [cliques, campos]}
ANTES = {'ent39': [3, 0], 'ent21': [5, 0], 'dev31': [3, 0], 'aceitar': [3, 0], 'recusar': [2, 0], 'excedente': [3, 0], 'nf4533': [2, 4],
         'laudo': [3, 1], 'contar0': [3, 1], 'contar1': [5, 2], 'ajuste': [2, 0], 'os2est': [3, 0]}
NOME = {'ent39': 'Entregar REQ-039 (1 item) · Rui', 'ent21': 'Entregar REQ-021 (2 itens) a Renato · Rui', 'dev31': 'Receber a sobra da REQ-031 (500 kg) · Rui',
        'aceitar': 'Aceitar consumo coberto pela custódia · Rui', 'recusar': 'Recusar relato de consumo · Rui',
        'excedente': 'Consumo acima da custódia (almoxarife + gestora)', 'nf4533': 'Receber a NF 4533 prevista (semente) · Rui',
        'laudo': 'Liberar a quarentena do K26-11 com laudo · Ana', 'contar0': 'Contar INV-2611 sem diferença · Paula',
        'contar1': 'Contar INV-2611 com diferença e causa · Paula', 'ajuste': 'Aprovar o ajuste do INV-2609 · Ana',
        'os2est': 'Da O.S. (OS-0417) à sobra no Estoque · Rui'}
# pioras permitidas, com o dano que evitam (SUP §8): o campo a mais é de propósito
PIORA_OK = {'dev31': 'quantidade conferida digitada em branco (PRD 42.4; CMD-45): devolução não conferida virava saldo apto',
            'recusar': 'motivo digitado (N7: a recusa sem motivo some o porquê do relato) e a recusa como secundária do painel do aceite (uma primária por painel)',
            'laudo': 'resultado do laudo escolhido (Aprovado ou Reprovado, RF-SUP-007): o reprovado ficava fora do registro',
            'ajuste': 'a linha não carrega comando (PADRÃO:69-71: o toque duplo na linha caía no registro seguinte); o ajuste é aprovado no painel, com a conta e as O.S. atingidas à vista antes do toque'}


class Conta:
    """Envolve o Est e conta cliques e campos do caminho de uma tarefa."""
    def __init__(self, E): self.E = E; self.cl = 0; self.ca = 0; self.passos = []

    def _p(self, t, n=1, campo=False):
        if campo: self.ca += n
        else: self.cl += n
        self.passos.append(('campo ' if campo else '') + t)

    def secao(self, nome):
        if self.E.secao() == nome: return 'já aberta'   # quem já está na seção não clica
        self._p('seção ' + nome); return self.E.ir_secao(nome)

    def clk(self, t, root=None): self._p(t); return self.E.clk(t, root)
    def row(self, *ts): self._p('linha ' + ' '.join(ts)); return self.E.row(*ts)
    def rowbtn(self, ts, b): self._p('linha › ' + b); return self.E.rowbtn(ts, b)
    def salvar(self): self._p('Salvar'); return self.E.salvar()
    def prim(self): self._p('primária ' + self.E.prim_painel()); return self.E.clk_prim()
    def fazenda(self, f): self._p('fazenda ' + f); return self.E.fazenda(f)
    def escolher(self, sel, v): self._p('escolher ' + v); return self.E.setv(sel, v)
    def digitar(self, sel, v): self._p(sel + '=' + v, campo=True); return self.E.setv(sel, v)

    def vazio(self, i): return str(self.E.val(i) or '').strip() == ''


def abrir(E, h='', perfil='Rui', prep=None):
    """Estoque com o cenário do início (+ preparação), no perfil de quem age; nada disso conta."""
    E.c.goto('about:blank', wait=.1); E.c.goto(f'http://127.0.0.1:{E.p}/EST.dc.html', wait=1.2)
    E.J("window.__cen.cenReset()")
    if prep: r = E.mudar(prep); print('    preparação:', str(r)[:140])
    E.perfil(perfil); E.c.goto('about:blank', wait=.1); E.c.goto(f'http://127.0.0.1:{E.p}/EST.dc.html{h}', wait=1.4)
    E.J("window.__errs=window.__errs||[]; if(!window.__ouve){ window.__ouve=1; window.addEventListener('error',e=>window.__errs.push(e.message)); }"); time.sleep(.4)


def link_os(E, os_id, rot):
    """href do atalho da O.S. ao Estoque (o link real da tela O.S.), aberto pelo endereço da O.S."""
    E.c.goto('about:blank', wait=.1); E.c.goto(f'http://127.0.0.1:{E.p}/OS.dc.html#{os_id}', wait=1.8); time.sleep(.6)
    return E.J(f"(()=>{{const a=[...document.querySelectorAll('a[href]')].find(a=>a.offsetParent&&a.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(rot)})); return a?a.getAttribute('href'):'';}})()")


# 75 L relatados com 65 L em custódia abrem a conferência; a entrega dos 15 L que faltavam leva a custódia a 80 L: o relato fica coberto
REL_COB = "cenIniciarTurno(c,'OS-0421'); cenFecharTurno(c,10,2,{'Fungicida A':75},''); return cenEntregar(c,'REQ-035','Fungicida A',15,'Marcos','Rui').msg;"
REL_EXC = "cenIniciarTurno(c,'OS-0421'); return cenFecharTurno(c,10,2,{'Fungicida A':85},'');"     # 85 L relatados, 65 L em custódia: 20 L além
CONF = "(c.confs||[]).filter(k=>k.os==='OS-0421'&&k.prod==='Fungicida A').map(k=>[k.estado,k.por||''])"


# ---------------- antes (99537ca: 6 seções, botão na linha, formulário pré-preenchido) ----------------
def a_ent39(E, K):
    abrir(E); K.secao('Entregue por O.S.'); K.row('REQ-039')
    if K.vazio('fx_g_ent_qtd'): K.digitar('fx_g_ent_qtd', '65')
    K.salvar(); return E.cen("c.reqs['REQ-039'].itens[0].entregue") == 65


def a_ent21(E, K):
    abrir(E); K.secao('Entregue por O.S.')
    for it in ('Muda de mamão', 'Superfosfato'):
        K.row('REQ-021', it)
        if K.vazio('fx_g_ent_quem'):   # o seletor fixo não tem Renato (SUP §3): escolhe quem houver
            op = E.J("([...document.querySelectorAll('#fx_g_ent_quem option')].map(o=>o.value).filter(Boolean)[0]||'')"); K.escolher('#fx_g_ent_quem', op)
        K.salvar()
    return E.cen("c.reqs['REQ-021'].itens.map(i=>i.entregue)") == [92500, 20000]


def a_dev31(E, K):
    abrir(E); K.secao('Receba devoluções'); K.row('REQ-031')
    if K.vazio('fx_g_dev_qtd'): K.digitar('fx_g_dev_qtd', '500')
    K.salvar(); return E.cen("c.reqs['REQ-031'].itens[0].custodia") == 0


def a_aceitar(E, K):
    abrir(E, prep=REL_COB); K.secao('Receba devoluções'); K.rowbtn(['REQ-035', 'Fungicida A'], 'Aceitar consumo'); K.rowbtn(['REQ-035', 'Fungicida A'], 'Confirmar aceite')
    return E.cen(CONF)[:1] == [['Aceito', 'Rui (almoxarife)']]


def a_recusar(E, K):
    abrir(E, prep=REL_COB); K.secao('Receba devoluções'); K.rowbtn(['REQ-035', 'Fungicida A'], 'Recusar relato')
    return E.cen(CONF)[:1] == [['Recusado', 'Rui (almoxarife)']]


def a_excedente(E, K):
    abrir(E, perfil='Ana', prep=REL_EXC); K.secao('Receba devoluções'); K.rowbtn(['REQ-035', 'Fungicida A'], 'Aceitar consumo'); K.rowbtn(['REQ-035', 'Fungicida A'], 'Confirmar aceite')
    return E.cen(CONF)[:1] == [['Aceito', 'Ana (gestora)']]


def a_nf4533(E, K):
    abrir(E); K.secao('Confira recebimentos'); K.row('NF 4533')
    K.digitar('fx_g_rec_conf', '20000'); K.digitar('fx_g_rec_apto', '20000')
    if K.vazio('fx_g_rec_quar'): K.digitar('fx_g_rec_quar', '0')
    K.digitar('fx_g_rec_val', '03/2027'); K.salvar()
    return E.cen("(c.lotes['Semente de soja 58 W|S58-0926']||{}).fisico") == 20000


def a_laudo(E, K):
    abrir(E, perfil='Ana'); K.secao('Confira saldos'); K.rowbtn('K26-11', 'Liberar após inspeção'); K.digitar('est-laudo', 'LAB-0917'); K.clk('Liberar com o laudo')
    return E.cen("c.lotes['KCl 60%|K26-11'].quarentena") == 0


def a_contar0(E, K):
    abrir(E, perfil='Paula'); K.secao('Faça contagens'); K.clk('Contar INV-2611'); K.digitar('fx_g_cnt_cont', '1200'); K.salvar()
    return E.cen("(c.movs||[]).filter(m=>m.tipo==='contagem'&&m.lote==='G26-14').length") == 1


def a_contar1(E, K):
    abrir(E, perfil='Paula'); K.secao('Faça contagens'); K.clk('Contar INV-2611'); K.digitar('fx_g_cnt_cont', '1180'); K.salvar()
    K.row('INV-2611'); K.digitar('fx_g_cnt_causa', 'Bombona com vazamento'); K.salvar()
    return 'Bombona com vazamento' in (E.toast() + E.rowtxt('INV-2611') + E.main())


def a_ajuste(E, K):
    abrir(E, perfil='Ana'); K.secao('Faça contagens'); K.rowbtn('INV-2609', 'Aprovar ajuste')
    return E.cen("(c.movs||[]).filter(m=>m.tipo==='ajuste').length") == 1


def a_os2est(E, K):
    abrir(E, prep="return cenLiberar(c,'OS-0430')||'ok';")
    h = link_os(E, 'OS-0417', 'Receber devolução no Estoque'); print('    link da O.S.:', h)
    K._p('link ' + h); E.c.goto(f'http://127.0.0.1:{E.p}/{h}', wait=1.6); time.sleep(.4)
    if 'REQ-031' not in E.aside(): K.secao('Receba devoluções'); K.row('REQ-031')
    return 'REQ-031' in E.aside()


# ---------------- depois (Etapas SUP-1/2a/2b: 4 seções, a linha identifica, o painel resolve) ----------------
def d_ent39(E, K):
    abrir(E); K.secao('Atenda requisições'); K.row('REQ-039'); K.prim()
    return E.cen("c.reqs['REQ-039'].itens[0].entregue") == 65


def d_ent21(E, K):
    abrir(E); K.secao('Atenda requisições'); K.fazenda('Lagoa Grande'); K.row('REQ-021'); K.prim()
    return E.cen("[c.reqs['REQ-021'].itens.map(i=>i.entregue),c.movs.filter(m=>m.req==='REQ-021').map(m=>m.quem)]") == [[92500, 20000], ['Rui (almoxarife) → Renato'] * 2]


def d_dev31(E, K):
    abrir(E); K.secao('Atenda requisições'); K.row('REQ-031'); K.digitar('fx_g_req_dqtd', '500'); K.prim()
    return E.cen("c.reqs['REQ-031'].itens[0].custodia") == 0


def d_aceitar(E, K):
    # sem nada a entregar, a linha da REQ-035 abre direto no consumo em conferência (eModoReq)
    abrir(E, prep=REL_COB); K.secao('Atenda requisições'); K.row('REQ-035'); K.prim()
    return E.cen(CONF)[:1] == [['Aceito', 'Rui (almoxarife)']]


def d_recusar(E, K):
    abrir(E, prep=REL_COB); K.secao('Atenda requisições'); kid = E.cen("(c.confs.find(k=>k.prod==='Fungicida A')||{}).id")
    K.row('REQ-035'); K.clk('Recusar relato ' + kid + ' ›', 'aside[role=dialog]'); K.digitar('#fx_g_req_mot', 'operador não aplicou'); K.prim()
    return E.cen(CONF)[:1] == [['Recusado', 'Rui (almoxarife)']]


def d_excedente(E, K):
    # o almoxarife não precisa enviar: o relato acima da custódia já fica "Aguardando gestora" (est.js estSitCf) e conta para a gestora.
    # A REQ-035 ainda tem 15 L a entregar: a linha abre na entrega e a gestora passa ao consumo pela ação "Conciliar CC-… ›" do painel
    abrir(E, perfil='Ana', prep=REL_EXC); K.secao('Atenda requisições'); kid = E.cen("(c.confs.find(k=>k.prod==='Fungicida A')||{}).id")
    K.row('REQ-035'); K.clk('Conciliar ' + kid + ' (Fungicida A) ›', 'aside[role=dialog]'); K.prim()
    return E.cen(CONF)[:1] == [['Aceito', 'Ana (gestora)']]


def d_nf4533(E, K):
    abrir(E); K.secao('Receba e inspecione'); K.row('NF 4533'); K.digitar('fx_g_rec_conf', '20000'); K.digitar('fx_g_rec_val', '03/2027'); K.prim()
    return E.cen("(c.lotes['Semente de soja 58 W|S58-0926']||{}).fisico") == 20000


def d_laudo(E, K):
    abrir(E, perfil='Ana'); K.secao('Receba e inspecione'); K.row('NF 4501'); K.digitar('fx_g_rec_laudo', 'LAB-0917'); K.escolher('#fx_g_rec_res', 'Aprovado'); K.prim()
    return E.cen("c.lotes['KCl 60%|K26-11'].quarentena") == 0


def d_contar0(E, K):
    abrir(E, perfil='Paula'); K.secao('Faça contagens'); K.row('INV-2611'); K.digitar('fx_g_cnt_cont', '1200'); K.prim()
    return E.cen("(c.movs||[]).filter(m=>m.tipo==='contagem'&&m.lote==='G26-14').length") == 1


def d_contar1(E, K):
    abrir(E, perfil='Paula'); K.secao('Faça contagens'); K.row('INV-2611'); K.digitar('fx_g_cnt_cont', '1180'); K.prim(); K.digitar('fx_g_cnt_causa', 'Bombona com vazamento'); K.prim()
    return E.cen("(c.ajustes||[]).filter(a=>a.lote==='G26-14').map(a=>[a.estado,a.contador])") == [['Aguardando gestor', 'Paula (almoxarife)']]


def d_ajuste(E, K):
    abrir(E, perfil='Ana'); K.secao('Faça contagens'); K.row('INV-2609'); K.prim()
    return E.cen("(c.movs||[]).filter(m=>m.tipo==='ajuste').length") == 1


def d_os2est(E, K):
    abrir(E)
    h = link_os(E, 'OS-0417', 'Receber devolução no Estoque'); print('    link da O.S.:', h)
    K._p('link ' + h); E.c.goto(f'http://127.0.0.1:{E.p}/{h}', wait=1.6); time.sleep(.4)
    if 'REQ-031' not in E.aside(): K.secao('Atenda requisições'); K.row('REQ-031')
    return 'REQ-031' in E.aside() and 'Devolução' in E.aside()


TAREFAS = list(NOME)
FLUXO = {'antes': {k: globals()['a_' + k] for k in TAREFAS}, 'depois': {k: globals()['d_' + k] for k in TAREFAS}}


R0 = est_lib.R


def medir(qual, render):
    est_lib.R = render or R0   # a base serve o seu próprio _render (não copia project/ por cima); o depois, o _render desta árvore
    E = Est(copiar=not render); res = {}
    try:
        for k in TAREFAS:
            K = Conta(E)
            try: efeito = bool(FLUXO[qual][k](E, K))
            except Exception as ex: efeito = False; K.passos.append('ERRO ' + str(ex)[:160])
            er = E.erros(); res[k] = dict(cl=K.cl, ca=K.ca, efeito=efeito, passos=K.passos, erros=er)
            print(f"  {qual:6} {k:10} {K.cl} cliques + {K.ca} campos · efeito {'ok' if efeito else 'NÃO GRAVOU'} · {' › '.join(K.passos)}" + (f' · erros JS {er}' if er else ''))
    finally:
        E.c.close(); E.srv.terminate()
    return res


if __name__ == '__main__':
    base = sys.argv[sys.argv.index('--base') + 1] if '--base' in sys.argv else ''
    FAIL = []; n = 0

    def ok(cond, msg, extra=''):
        global n; n += 1
        print(('  OK  ' if cond else '  FALHA ') + msg + ((' · ' + str(extra)[:300]) if (extra != '' and not cond) else ''))
        if not cond: FAIL.append(msg)
    antes = ANTES
    if base:
        print('===== antes (base) =====')
        ma = medir('antes', os.path.join(os.path.abspath(base), '_render'))
        for k in TAREFAS:
            ok(ma[k]['efeito'], f'antes {k}: o caminho grava o efeito')
            ok([ma[k]['cl'], ma[k]['ca']] == ANTES[k], f'antes {k}: medido igual ao guardado {ANTES[k]}', [ma[k]['cl'], ma[k]['ca']])
        antes = {k: [ma[k]['cl'], ma[k]['ca']] for k in TAREFAS}
    print('===== depois (build atual) =====')
    md = medir('depois', '')
    print('\n| Tarefa | Antes | Depois |\n|---|---|---|')
    for k in TAREFAS:
        a, d = antes[k], [md[k]['cl'], md[k]['ca']]
        print(f"| {NOME[k]} | {a[0]} cliques + {a[1]} campos | {d[0]} cliques + {d[1]} campos |")
    print()
    for k in TAREFAS:
        a, d = antes[k], [md[k]['cl'], md[k]['ca']]
        ok(md[k]['efeito'], f'depois {k}: o caminho grava o efeito ({NOME[k]})', md[k]['passos'])
        ok(not md[k]['erros'], f'depois {k}: sem erro de JavaScript', md[k]['erros'])
        pior = d[0] + d[1] > a[0] + a[1] or d[1] > a[1]   # piora: mais passos no total, ou mais digitação (um campo custa mais que um toque)
        ok(not pior or k in PIORA_OK, f'depois {k}: {d[0]}+{d[1]} contra {a[0]}+{a[1]}' + (f' (piora com dano nomeado: {PIORA_OK[k]})' if pior and k in PIORA_OK else ''), [a, d])
    tot_a = sum(antes[k][0] + antes[k][1] for k in TAREFAS); tot_d = sum(md[k]['cl'] + md[k]['ca'] for k in TAREFAS)
    ok(tot_d < tot_a, f'total das {len(TAREFAS)} tarefas: {tot_a} → {tot_d} cliques + campos', [tot_a, tot_d])
    print(f'RESULTADO: {n - len(FAIL)}/{n} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
    sys.exit(0 if not FAIL else 1)
