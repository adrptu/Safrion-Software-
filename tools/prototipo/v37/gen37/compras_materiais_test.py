# -*- coding: utf-8 -*-
"""CMP-MAT (V69) · Compras de materiais, peças e serviços no navegador (CDP), como a pessoa faz. Dados sintéticos.
Pedido do proprietário (15/10/2026): "cadê as compras de materiais, peças, etc?" — lógica própria: OM, reposição e avulsa, sem safra.
 1 · Compras tem o seletor "Insumos da safra | Materiais, peças e serviços"; Materiais esconde a safra e as etapas dos insumos, mostra a faixa
     Filtros (Origem, Situação) e a fila com as três origens; o endereço #tipo=materiais reabre a mesma parte.
 2 · Peça de OM: Manutenção gera a OM-0235 (Falta peça) → Solicitar compra → Compras cota, emite o pedido e recebe → a peça entra no saldo
     para a OM-0235, que sai de "Falta peça" e libera na Manutenção (a reserva nasce na liberação, DEC-2609-13). Zé (mecânico) vê "Solicitar cotações" indisponível com o motivo.
 3 · Reposição: a Graxa EP2 abaixo do ponto de pedido aparece sem requisição; Rui abre a reposição; o recebimento entra no estoque.
 4 · Serviço: o aceite da SC-038 lança o valor do pedido como custo de terceiro da OM-0233 (custo da ordem na Manutenção).
 5 · Nova requisição avulsa sem safra nem cultura (nenhum campo pede); celular 390 px sem rolagem lateral.
Uso (de gen37/): env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico python3 -B compras_materiais_test.py
Contraprova: CM_RENDER=<pasta do _render da base> serve outra montagem (a base a0db53a precisa reprovar)."""
import os, sys, time, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ma_lib import MA

m = MA(1440, 1000); J = m.J
REND = os.environ.get('CM_RENDER')
if REND:   # contraprova: o mesmo teste sobre outra montagem, na mesma porta
    m.t.srv.terminate(); m.t.srv.wait(5); time.sleep(.3)
    m.t.srv = subprocess.Popen(['python3', '-m', 'http.server', str(m.t.p), '--bind', '127.0.0.1', '--directory', REND], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(.6)
PAN = '#cm-painel'
def pan(): return J("(document.querySelector('#cm-painel')||{}).innerText||''") or ''
def cmp(ancora='tipo=materiais', perfil=None, limpa=False): m.ir(ancora, perfil=perfil, limpa=limpa, pagina='CMP.dc.html')
def est(expr):
    try: return J(f"(()=>{{const c=window.__cmm.manGet(); return ({expr});}})()")
    except Exception as e: return 'ERRO ' + str(e)[:120]
def vis(sel): return J(f"[...document.querySelectorAll({json.dumps(sel)})].some(e=>e.getClientRects().length>0)")
def prim(): return J("(()=>{const b=document.querySelector('#cm-painel [data-cm-prim]'); if(!b||!b.getClientRects().length) return null; "
                    "const w=b.closest('.g2ind'); const mt=w&&w.querySelector('.g2motivo'); return {t:b.innerText.trim(),dis:b.getAttribute('aria-disabled')==='true',motivo:mt?mt.innerText.trim():''};})()")
def ids(): return J("[...document.querySelectorAll('[data-g2g=g_mat] [role=row][data-rid]')].filter(r=>r.getClientRects().length).map(r=>r.getAttribute('data-rid'))") or []

def secao(nome, fn):
    """cada parte roda sozinha: exceção (tela ou estado inexistente, como na base) vira FALHA com o motivo e o teste segue"""
    try: fn()
    except Exception as e: m.ok(False, nome + ' · exceção', str(e)[:200])

def parte1():   # 1 · o seletor e a fila
    cmp('', perfil='Ana', limpa=True); m.sem_erro('CMP · Insumos da safra')
    ins = J("[...document.querySelectorAll('[data-cmtipo]')].map(b=>b.innerText.trim()+':'+b.getAttribute('aria-pressed'))") or []
    m.ok(ins == ['Insumos da safra:true', 'Materiais, peças e serviços:false'] and vis('.etp') and vis('.mf-tela[aria-label="Trabalhando em"]'),
         '1a seletor "Insumos da safra | Materiais, peças e serviços" no cabeçalho; Insumos abre por padrão com as etapas e a safra', ins)
    m.clk('Materiais, peças e serviços'); time.sleep(.4)
    fx = J("[...document.querySelectorAll('[data-cm-mat] .mf-tela select')].filter(s=>s.getClientRects().length).map(s=>s.getAttribute('aria-label'))") or []
    r0 = ids()
    m.ok(m.hash() == '#tipo=materiais' and not vis('.etp') and not vis('.mf-tela[aria-label="Trabalhando em"]') and fx == ['Filtrar por origem', 'Filtrar por situação'],
         '1b Materiais: sem as etapas e a safra dos insumos; faixa Filtros com Origem e Situação; endereço #tipo=materiais', [m.hash(), fx])
    m.ok(r0 == ['SC-038', 'SC-040', 'REP:GR-EP2', 'SC-039'],
         '1c a fila mostra as três origens: serviço da OM-0233 (urgente), avulsa da oficina (alta), Graxa EP2 abaixo do ponto de pedido e a reposição SC-039', r0)
    l38 = m.linha('SC-038'); lrep = m.linha('REP:GR-EP2')
    m.ok('Ordem de manutenção' in l38 and 'OM-0233' in l38 and 'Pedido emitido' in l38 and 'Abaixo do ponto de pedido' in lrep and 'livre 18 kg' in lrep and 'ponto de pedido 20 kg' in lrep,
         '1d cada linha diz a origem e o próximo passo (SC-038 · OM-0233 · Pedido emitido; Graxa EP2 · livre 18 kg · ponto de pedido 20 kg)', [l38[:140], lrep[:140]])
    m.setv('[data-cm-mat] select[aria-label="Filtrar por origem"]', 'Avulsa'); time.sleep(.3)
    m.ok(ids() == ['SC-040'], '1e filtro Origem = Avulsa deixa só a SC-040', ids())
    m.setv('[data-cm-mat] select[aria-label="Filtrar por origem"]', 'Todas'); time.sleep(.2)
    cmp('tipo=materiais', perfil='Ana'); m.sem_erro('CMP · Materiais pelo endereço')
    m.ok(J("document.querySelector('[data-cmtipo=mat]').getAttribute('aria-pressed')") == 'true' and len(ids()) == 4, '1f o endereço #tipo=materiais reabre Materiais (F5 e link)', ids())
    m.clk('Insumos da safra'); time.sleep(.4)
    m.ok(vis('.etp') and not vis('[data-cm-mat]') and m.hash() == '', '1g voltar a Insumos da safra devolve as etapas e limpa o endereço', m.hash())

def parte2():   # 2 · peça da OM: requisição → cotação → pedido → recebimento reserva para a OM
    m.ir('vis=semordem', perfil='Otávio', limpa=True); m.clk('Gerar 3 ordens preventivas'); m.ir('om=OM-0235')
    m.clk('Solicitar compra', '#ma-painel'); s1 = m.toast()
    m.ok('SC-041' in s1 and 'Compras' in s1 and m.man("m.oms['OM-0235'].sc.id") == 'SC-041', '2a Manutenção: "Solicitar compra" da OM-0235 envia a SC-041 a Compras', s1[:140])
    cmp('tipo=materiais', perfil='Zé'); l41 = m.linha('SC-041')
    m.ok('Ordem de manutenção' in l41 and 'OM-0235' in l41 and 'A cotar' in l41 and 'Filtro de óleo MF 4292' in l41,
         '2b a SC-041 chega na fila de Compras com a origem OM-0235 e o filtro em falta (sem safra)', l41[:160])
    m.abre('SC-041'); pz = prim()
    m.ok(m.hash() == '#tipo=materiais&sc=SC-041' and pz and pz['t'] == 'Solicitar cotações (simulado)' and pz['dis'] and 'quem compra' in pz['motivo'],
         '2c Zé (mecânico) vê "Solicitar cotações" indisponível, com o motivo em texto (só quem compra)', pz)
    cmp('tipo=materiais&sc=SC-041', perfil='Ana'); p0 = pan()
    m.ok('Ordem de manutenção · OM-0235' in p0 and 'Apropriação' in p0 and 'Trator 03' in p0 and 'rateio pelo uso do ativo' in p0 and 'Safra' not in p0.replace('safra', ''),
         '2d detalhe (F5 reabre): origem OM-0235, apropriação no ativo Trator 03, "rateio pelo uso do ativo", nada de safra', p0[:400])
    m.clk('Solicitar cotações (simulado)', PAN); t1 = m.toast(); p1 = pan()
    m.ok('2 fornecedores homologados' in t1 and 'Rondon Peças Agrícolas' in p1 and 'menor custo a tempo' in p1 and 'chega depois de 24/09' in p1 and est("c.cmp.reqs['SC-041'].etapa") == 'Em cotação',
         '2e cotação simulada: os 2 homologados de Peças; a referência é a de menor custo que chega a tempo da janela da OM (24/09)', [t1[:120], p1[-500:]])
    m.clk('Rondon Peças Agrícolas', PAN); time.sleep(.3); pj = pan(); m.clk('Emitir pedido', PAN); tj = m.toast()
    m.ok('Justificativa da escolha' in pj and 'Justifique' in tj and est("c.cmp.reqs['SC-041'].etapa") == 'Em cotação',
         '2f escolher a mais barata que chega depois da janela pede justificativa (recusa sem pedido)', [tj[:140]])
    m.clk('Agro Peças Centro-Oeste', PAN); time.sleep(.3); pz = prim(); m.clk('Emitir pedido', PAN); t2 = m.toast()
    m.ok(pz and pz['t'] == 'Emitir pedido · R$ 160,00' and 'PC-202' in t2 and est("c.cmp.reqs['SC-041'].ped.id") == 'PC-202',
         '2g Ana emite o PC-202 (R$ 160,00, Agro Peças Centro-Oeste) vinculado à SC-041 e à OM-0235', [pz, t2[:140]])
    f0 = est("[c.itens['FIL-MF4292'].saldo,c.itens['FIL-MF4292'].reservado]")
    cmp('tipo=materiais&sc=SC-041', perfil='Rui'); m.clk('Registrar recebimento', PAN); t3 = m.toast()
    f1 = est("[c.itens['FIL-MF4292'].saldo,c.itens['FIL-MF4292'].reservado,c.oms['OM-0235'].pecas.find(p=>p.item==='FIL-MF4292').res,c.cmp.reqs['SC-041'].etapa]")
    m.ok('para a OM-0235' in t3 and 'pronta para liberar' in t3 and f1 == [f0[0] + 1, f0[1], 0, 'Recebida'],
         '2h Rui recebe: +1 un no saldo para a OM-0235, que fica pronta para liberar; a reserva espera a liberação (DEC-2609-13); SC Recebida', [t3[:160], f0, f1])
    m.clk('Registrar recebimento', PAN); m.ok(not prim() and est("c.itens['FIL-MF4292'].saldo") == f0[0] + 1, '2i recebida não oferece receber de novo (nada soma)', prim())
    m.ir('om=OM-0235', perfil='Otávio'); m.bloco('Peças'); po = m.pan()
    m.ok('Livre 1 un' in po and 'Liberar serviço' in po and 'Falta peça' not in po, '2j na Manutenção a OM-0235 sai de "Falta peça": o filtro aparece "Livre 1 un" e a primária é "Liberar serviço"', po[:300])
    m.clk('Liberar serviço', '#ma-painel'); t4 = m.toast()
    m.ok('liberada' in t4 and m.man("m.oms['OM-0235'].etapa") == 'Liberadas' and m.man("m.itens['FIL-MF4292'].reservado") == f0[1] + 1,
         '2k liberar a OM-0235 reserva o filtro que chegou (reservado +1)', [t4[:140], m.man("m.itens['FIL-MF4292']")])
    m.sem_erro('MA depois do recebimento')

def parte3():   # 3 · reposição abaixo do ponto de pedido
    cmp('tipo=materiais', perfil='Rui'); m.abre('REP:GR-EP2'); pr = pan()
    m.ok('Saldo livre' in pr and '18 kg' in pr and 'Ponto de pedido' in pr and '22 kg' in pr and (prim() or {}).get('t') == 'Abrir requisição de reposição',
         '3a Graxa EP2: saldo livre 18 kg, ponto de pedido 20 kg, sugere 22 kg; primária "Abrir requisição de reposição"', pr[:300])
    m.clk('Abrir requisição de reposição', PAN); t5 = m.toast(); rid = est("Object.keys(c.cmp.reqs).find(k=>c.cmp.reqs[k].orig==='rep'&&c.cmp.reqs[k].itens[0].item==='GR-EP2')")
    m.ok(rid == 'SC-042' and 'SC-042' in t5 and 'REP:GR-EP2' not in ids() and 'SC-042' in ids(), '3b Rui abre a SC-042 de reposição; a sugestão sai da fila e a requisição entra', [t5[:120], ids()])
    cmp('tipo=materiais&sc=SC-042', perfil='Ana'); m.clk('Solicitar cotações (simulado)', PAN); m.clk('Emitir pedido', PAN)
    g0 = est("c.itens['GR-EP2'].saldo"); cmp('tipo=materiais&sc=SC-042', perfil='Rui'); m.clk('Registrar recebimento', PAN); t6 = m.toast()
    m.ok('estoque da oficina' in t6 and est("c.itens['GR-EP2'].saldo") == g0 + 22 and est("c.itens['GR-EP2'].reservado") == 0,
         '3c a reposição recebida entra no estoque da oficina (+22 kg, sem reserva)', [t6[:140], g0, est("c.itens['GR-EP2']")])

def parte4():   # 4 · serviço: aceite vira custo de terceiro da OM
    cmp('tipo=materiais&sc=SC-038', perfil='Otávio'); ps = pan()
    m.ok('Serviço não tem estoque' in ps and (prim() or {}).get('t') == 'Registrar aceite do serviço', '4a serviço da OM-0233: sem recebimento de estoque; primária "Registrar aceite do serviço"', ps[-300:])
    m.clk('Registrar aceite do serviço', PAN); t7 = m.toast()
    m.ok('custo de terceiro da OM-0233' in t7 and est("c.oms['OM-0233'].terc") == 1843 and est("c.cmp.reqs['SC-038'].etapa") == 'Aceita',
         '4b aceite da SC-038: R$ 1.843,00 como custo de terceiro da OM-0233; SC Aceita', t7[:180])
    m.ok('R$ 8.023,00' in t7, '4c o custo estimado da OM-0233 passa a R$ 8.023,00 (peças 4.100 + 6,5 h × 320 + terceiro 1.843), pela função única', t7[-120:])
    m.ir('vis=ordens', perfil='Otávio'); l33 = m.linha('OM-0233')
    m.ok('8.023' in l33, '4d na Manutenção a linha da OM-0233 mostra o custo com o serviço aceito', l33[:200])

def parte5():   # 5 · avulsa sem safra nem cultura; celular
    cmp('tipo=materiais', perfil='Zé'); m.clk('Nova requisição'); time.sleep(.3)
    labs = J("[...document.querySelectorAll('#cm-painel label, #cm-painel [role=group]')].map(e=>(e.getAttribute('aria-label')||e.firstChild&&e.firstChild.textContent||'').trim()).filter(Boolean)") or []
    m.ok(not any('safra' in x.lower() or 'cultura' in x.lower() for x in labs) and any('Destino' in x for x in labs) and 'Urgência' in labs,
         '5a o formulário de requisição avulsa não tem campo de safra nem de cultura (destino é ativo ou centro de custo)', labs)
    m.clk('Serviço', PAN); m.setv('#cmn-nome', 'Troca de lâmpadas do galpão'); m.setv('#cmn-qtd', '1'); m.setv('#cmn-preco', '300')
    m.setv('#cmn-dest', 'Armazém e beneficiamento'); m.clk('Normal', PAN); m.setv('#cmn-motivo', 'iluminação da área de embalagem'); m.clk('Abrir requisição', PAN); t8 = m.toast()
    nid = est("Object.keys(c.cmp.reqs).find(k=>c.cmp.reqs[k].orig==='avulsa'&&/lâmpadas/.test(c.cmp.reqs[k].itens[0].nome))")
    m.ok(nid == 'SC-043' and 'SC-043' in t8 and est("JSON.stringify(c.cmp.reqs['SC-043'])").find('safra') < 0 and est("c.cmp.reqs['SC-043'].cc") == 'Armazém e beneficiamento',
         '5b Zé abre a SC-043 (serviço avulso no centro de custo Armazém e beneficiamento) sem safra nem cultura', [t8[:140], nid])
    m.c.size(390, 844); cmp('tipo=materiais', perfil='Ana'); m.abre('SC-040'); time.sleep(.3)
    m.ok(m.largura() <= 0 and J("(()=>{const a=document.querySelector('#cm-painel'); if(!a) return false; const r=a.getBoundingClientRect(); return r.left>=-1&&r.right<=innerWidth+1;})()") and (prim() or {}).get('t') == 'Solicitar cotações (simulado)',
         '5c celular 390 px: sem rolagem lateral; o painel cabe na tela com a primária', m.largura())
    m.sem_erro('CMP · celular')

try:
    secao('1 · o seletor e a fila', parte1)
    secao('2 · peça da OM: requisição → cotação → pedido → recebimento reserva para a OM', parte2)
    secao('3 · reposição abaixo do ponto de pedido', parte3)
    secao('4 · serviço: aceite vira custo de terceiro da OM', parte4)
    secao('5 · avulsa sem safra nem cultura; celular', parte5)
finally:
    sys.exit(m.fim())
