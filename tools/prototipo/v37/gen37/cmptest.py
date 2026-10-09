# -*- coding: utf-8 -*-
"""Teste CDP de Compras (CMP.dc.html) com a SOL-2026-07, na forma do SUP (docs/suprimentos-simplificado §5 e §9.3): lista de solicitações →
detalhe na fase (Cote → Decida) → Direção → Acompanhe pedidos. A forma mudou (eram 6 etapas numeradas); ficam as regras: só homologado
recebe convite, canal só entre os autorizados, justificativa da escolha que não é a de menor custo a tempo, quantidade até a necessidade,
convite adicional sem duplicar, sig (mudar depois do envio invalida), navegar não aprova, aprovar não duplica pedido, reprogramar com motivo.
Uso: python3 cmptest.py"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est

a = Est(copiar=False); J = a.J; FAL = []; NOK = [0]


def chk(nome, cond, extra=''):
    print(('OK   ' if cond else 'FALHA') + ' · ' + nome + (' · ' + str(extra)[:300] if extra != '' and not cond else ''))
    if not cond: FAL.append(nome)
    else: NOK[0] += 1


def ir(h='', wait=1.4):
    a.c.goto('about:blank', wait=.1)   # recarrega sempre: o mesmo endereço duas vezes não dispara hashchange
    a.c.goto(f'http://127.0.0.1:{a.p}/CMP.dc.html{h}', wait=wait)
    J("window.__errs=window.__errs||[]; if(!window.__ouve){ window.__ouve=1; window.addEventListener('error',e=>window.__errs.push(e.message)); }"); time.sleep(.3)


T = a.toast
body = lambda: J("document.body.innerText")
prim = lambda: J("(()=>{const b=[...document.querySelectorAll('.acoes-prim')].find(b=>b.offsetParent); return b?b.innerText.trim():'';})()")
faixa = lambda: J("(document.querySelector('[aria-label=\"Situação da solicitação\"]')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
reg = lambda: J("(()=>{ try{ return JSON.parse(localStorage.getItem('talhao-os-compras-v1')||'null')||{}; }catch(e){ return {}; } })()") or {}
aprov = lambda: ((reg().get('proc') or {}).get('S2627') or {}).get('aprov') or {}
opts = lambda k: J(f"[...document.querySelectorAll('[id$=_{k}] option')].map(o=>o.value)")
fid = lambda k: J(f"(document.querySelector('[id$=_{k}]')||{{id:''}}).id")
sub = lambda: a.aside()


def clk_prim():
    r = J("(()=>{const b=[...document.querySelectorAll('.acoes-prim')].find(b=>b.offsetParent); if(!b) return 'sem primária'; b.click(); return 'ok';})()"); time.sleep(.6); return r


def kid(g, t, click=False):
    """Linha-filha t no grupo g da grade de convites (Grupo › fornecedor) visível: texto ou clique."""
    r = J(f"""(()=>{{const tb=[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).find(t=>/^Grupo › fornecedor/i.test(((t.querySelector('[role=columnheader]')||{{}}).innerText||'').trim()))||document; const rows=[...tb.querySelectorAll('[role=row]')].filter(r=>r.offsetParent); const i=rows.findIndex(r=>!r.classList.contains('g2kid')&&r.innerText.replace(/\\s+/g,' ').replace(/^[\\s▾▸]+/,'').startsWith({json.dumps(g)})); if(i<0) return 'sem grupo';
      for(let k=i+1;k<rows.length&&rows[k].classList.contains('g2kid');k++){{ const x=rows[k]; if(x.innerText.indexOf({json.dumps(t)})>=0){{ if({json.dumps(click)}){{ (x.querySelector('[role=cell] b')||x.querySelector('[role=cell] span')).click(); return 'ok'; }} return x.innerText.replace(/\\s+/g,' '); }} }} return 'sem linha'; }})()""")
    if click: time.sleep(.4)
    return r


def expandir():
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&/^Expandir tudo/.test(b.innerText.trim())); if(b) b.click();})()"); time.sleep(.3)


def esperar(t=12):
    for _ in range(int(t / .5)):
        if 'Em cotação' not in faixa(): break
        time.sleep(.5)
    time.sleep(.4)


def env_n():
    return len((((reg().get('proc') or {}).get('S2627') or {}).get('env') or {}).get('conv') or [])


try:
    ir('', 1.8)
    chk('sem erro JS', not a.erros(), a.erros())
    # ---- lista: SOL-2026-07 da Safra 2026/27; a origem leva ao Planejar safra ----
    chk('lista abre com a SOL-2026-07 "A cotar" e o valor de referência do Planejar safra', a.cel('SOL-2026-07', 'Situação') == 'A cotar' and a.cel('SOL-2026-07', 'Valor ref.') == 'R$ 379.580,00',
        [a.cel('SOL-2026-07', 'Situação'), a.cel('SOL-2026-07', 'Valor ref.')])
    a.row('SOL-2026-07'); f = faixa()
    chk('detalhe: Veio de → Está → Falta → Próxima, com a origem no Planejar safra', 'Veio de' in f and J("[...document.querySelectorAll('[aria-label=\"Situação da solicitação\"] a')].some(x=>(x.getAttribute('href')||'').startsWith('SAF.dc.html#saf=S2627'))"), f)
    # ---- só homologado recebe convite ----
    J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.offsetParent&&/Química Centro-Oeste/.test(r.innerText)); r&&(r.querySelector('[role=cell] b')||r.querySelector('[role=cell] span')).click();})()"); time.sleep(.4)
    chk('não homologado não abre edição; o aviso diz como homologar', not a.aberto() and 'não é homologado' in T(), T())
    # ---- canal só entre os autorizados; destinatário e escopo no subtítulo ----
    kid('Fertilizantes', 'Casa do Adubo', True); o = opts('canal'); s = sub()
    chk('Casa do Adubo só com E-mail autorizado', o == ['E-mail'], o)
    chk('subtítulo mostra destinatário e itens do convite', 'Destinatário: e-mail vendas@casadoadubo.com.br' in s and 'Itens do convite (Fertilizantes)' in s and 'MAP 11-52 · 62.500 kg' in s and 'simulado' in s, s[:300])
    a.clk('Cancelar', 'aside[role=dialog]')
    kid('Fertilizantes', 'Coop. Vale', True)
    chk('Coop. Vale tem E-mail e WhatsApp autorizados', opts('canal') == ['E-mail', 'WhatsApp'], opts('canal'))
    a.setv('#' + fid('canal'), 'WhatsApp'); chk('destinatário acompanha o canal escolhido', 'Destinatário: WhatsApp 65 99466-7788' in sub(), sub()[:160])
    a.setv('#' + fid('prazo'), '29/09/2026'); a.clk('Salvar convite', 'aside[role=dialog]')
    chk('convite salvo', 'Convite atualizado' in T(), T())
    # ---- convite adicional: Fungicidas só com a Coop. Vale; depois do envio, Agro Norte entra sem reenviar a quem já recebeu ----
    for fz in ['Agro Norte', 'Santa Rita Insumos']:
        kid('Fungicidas', fz, True); a.setv('#' + fid('conv'), 'Não convidar'); a.clk('Salvar convite', 'aside[role=dialog]')
    chk('Fungicidas só com a Coop. Vale convidada', 'Não convidar' in kid('Fungicidas', 'Agro Norte') and 'Convidar' in kid('Fungicidas', 'Coop. Vale'), kid('Fungicidas', 'Agro Norte'))
    p0 = prim(); clk_prim(); t = T(); n0 = env_n()
    chk('enviar: aviso simulado, nenhuma mensagem real', p0.startswith('Enviar ') and 'nenhuma mensagem real foi enviada' in t, [p0, t])
    esperar()
    chk('respostas trocam para Decida sem clique', 'Em cotação' not in faixa() and 'A cotar' not in faixa(), faixa()[:200])
    expandir(); t = a.rowtxt('Fungicida A'); chk('Fungicida A sem proposta (Fungicidas só com a Coop. Vale)', 'sem proposta' in t.lower(), t)
    a.clk('Convidar outro fornecedor'); kid('Fungicidas', 'Agro Norte', True)
    chk('não convidado abre o formulário depois do envio (convite adicional)', 'Convite adicional' in sub(), sub()[:160])
    a.setv('#' + fid('conv'), 'Convidar'); a.clk('Salvar convite', 'aside[role=dialog]')
    chk('primária vira "Enviar 1 convite adicional (simulado)"', prim() == 'Enviar 1 convite adicional (simulado)', prim())
    clk_prim(); t = T(); time.sleep(2.5); n1 = env_n()
    chk('envio adicional simulado, sem reenviar a quem já recebeu; só 1 convite a mais', 'Quem já recebeu não recebe de novo' in t and n1 == n0 + 1, [t, n0, n1])
    expandir(); t = a.rowtxt('Fungicida A'); chk('Fungicida A agora tem proposta da Agro Norte', 'Agro Norte' in t, t)
    # ---- escolha: quantidade até a necessidade; justificativa da escolha que chega depois da falta ----
    a.row('MAP 11-52'); chk('formulário da escolha abre pela linha do insumo', 'Proposta escolhida' in a.aside(), a.aside()[:80])
    a.setv('#' + fid('ped'), '70000'); a.clk('Salvar escolha', 'aside[role=dialog]')
    chk('quantidade acima da necessidade é recusada no campo', 'Máximo 62.500 kg' in a.err(), a.err())
    a.setv('#' + fid('ped'), '62500'); a.clk('Salvar escolha', 'aside[role=dialog]')
    r = J("""(()=>{const rows=[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent); const i=rows.findIndex(r=>/2,4-D 806/.test(r.innerText)); const k=rows.slice(i+1).find(r=>/Santa Rita Insumos/.test(r.innerText)); if(!k) return 'sem proposta'; (k.querySelector('[role=cell] b')||k.querySelector('[role=cell] span')).click(); return 'ok';})()""")
    time.sleep(.4); s = a.aside()
    chk('escolher a proposta que chega depois da falta pede justificativa com as datas', r == 'ok' and 'depois da falta de 28/09/2026' in s, [r, s[:300]])
    a.clk('Salvar escolha', 'aside[role=dialog]'); chk('sem justificativa não salva', a.err() != '' and a.aberto(), a.err())
    a.setv('#' + fid('just'), 'Entrega única com o restante do pedido'); a.clk('Salvar escolha', 'aside[role=dialog]')
    chk('escolha justificada salva', 'Escolha salva' in T() and not a.aberto(), T())
    # ---- navegar não aprova; Ana acima da alçada envia à Direção; sig invalida o envio ----
    a.clk('Acompanhe pedidos'); a.clk('Atenda solicitações'); ir('#sol=SOL-2026-07&saf=S2627', 1.4)
    chk('navegar não aprova nem emite pedido', not aprov() and not (reg().get('ped') or {}), aprov())
    p = prim(); chk('acima de R$ 300.000: a primária é "Enviar à Direção"', p.startswith('Enviar à Direção · R$') and 'Aprovar e emitir' not in body(), p)
    clk_prim(); chk('enviada: Aguardando Direção', aprov().get('estado') == 'pendente' and 'Aguardando Direção' in faixa(), faixa()[:120])
    expandir(); a.row('MAP 11-52'); a.setv('#' + fid('ped'), '40000'); a.clk('Salvar escolha', 'aside[role=dialog]')
    chk('mudar depois do envio invalida o envio (sig)', 'perdeu a validade' in T() or 'a compra mudou' in faixa(), [T(), faixa()[:160]])
    # MAP 40 t: total dentro da alçada da Ana → ela aprova e emite; tocar de novo não duplica
    p = prim(); chk('dentro da alçada da Ana: "Aprovar e emitir N pedidos · R$ …"', p.startswith('Aprovar e emitir'), p)
    chk('prévia dos pedidos visível antes do toque', 'PEDIDOS QUE SERÃO EMITIDOS' in body().upper())
    clk_prim(); ap = aprov(); pcs = (ap.get('emi') or {}).get('pcs') or []
    chk('aprovada gera os pedidos com a decisão e a emissão registradas', ap.get('estado') == 'aprovada' and bool(pcs) and str((ap.get('dec') or {}).get('por', '')).startswith('Ana'), [ap.get('estado'), pcs])
    J("(()=>{const b=[...document.querySelectorAll('.acoes-prim,.acoes-sec')].find(b=>b.offsetParent&&/^Aprovar e emitir/.test(b.innerText)); if(b) b.click();})()"); time.sleep(.4)
    chk('sem pedido duplicado', ((aprov().get('emi') or {}).get('pcs') or []) == pcs, aprov().get('emi'))
    # ---- Acompanhe pedidos: confirmar (simulado), reprogramar com motivo ----
    a.clk('Acompanhe pedidos'); time.sleep(.3); pc = pcs[-1] if pcs else 'PC-?'
    a.row(pc); chk(f'{pc} abre o painel do pedido', f'Pedido · {pc}' in a.aside(), a.aside()[:80])
    a.clk('Confirmar com', 'aside[role=dialog]'); t = T(); chk('confirmação simulada', 'simulada' in t and pc in t, t)
    a.row(pc); a.clk(f'Reprogramar {pc} ›', 'aside[role=dialog]'); a.setv('#' + fid('prev'), '2026-09-01'); a.clk(f'Reprogramar {pc}', 'aside[role=dialog]')
    chk('data passada recusada', 'a partir de hoje' in a.err(), a.err())
    a.setv('#' + fid('prev'), '2026-12-20'); a.clk(f'Reprogramar {pc}', 'aside[role=dialog]'); chk('motivo obrigatório', 'motivo' in a.err().lower(), a.err())
    a.setv('#' + fid('obs'), 'fornecedor sem caminhão'); a.clk(f'Reprogramar {pc}', 'aside[role=dialog]'); t = T()
    pv = (reg().get('ped') or {}).get(pc) or {}
    chk('reprogramada: versão anterior guardada com o motivo', pv.get('prev') == '2026-12-20' and len(pv.get('prevs') or []) == 1 and pv['prevs'][0].get('motivo') == 'fornecedor sem caminhão', pv)
    a.shot('cmp_pedidos.png')
    chk('sem erro JS no fim', not a.erros(), a.erros())
finally:
    try: a.c.close()
    finally: a.srv.terminate()
print(f'\nRESULTADO: {NOK[0]}/{NOK[0] + len(FAL)} ok · FALHAS:', FAL if FAL else 'nenhuma')
sys.exit(1 if FAL else 0)
