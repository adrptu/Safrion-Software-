# -*- coding: utf-8 -*-
"""Verificador · Compra (item 02): devolução e recusa da Direção digitando o motivo de verdade (teclado), Voltar, estados nas etapas 1, 2 e 6,
desfazer a mudança depois da devolução, e recusa seguida de nova proposta de compra."""
import time, json
from verif_cmpest_lib import V
v=V('CMP.dc.html'); J=v.J
TA='textarea[aria-label="Motivo da decisão"]'
try:
    v.open(); v.clk('Abrir compra'); v.clk('3 Solicite cotações'); v.clk('Enviar convites (simulado)'); time.sleep(7)
    v.clk('Comparar propostas'); v.clk('Revisar aprovação'); print('  primário e5:', v.prim())
    v.clk('Enviar à Direção'); print('  primário pendente:', v.prim())
    v.chk('pendente: primário continua Registrar aprovação da Direção', 'Registrar aprovação da Direção' in v.prim(), v.prim())
    v.clk('Registrar devolução'); v.chk('painel de devolução aberto', 'Confirmar devolução' in v.body())
    v.clk('Voltar'); v.chk('Voltar fecha o painel sem registrar', 'Confirmar devolução' not in v.body() and 'Registrar devolução' in v.body() and 'Aguardando Direção' in v.body())
    v.clk('Registrar devolução'); v.typ(TA,'Rever prazo do MAP'); print('  valor digitado:', J(f"document.querySelector({json.dumps(TA)}).value"))
    v.clk('Confirmar devolução'); b=v.body(); print('  toast:', v.T())
    v.chk('devolução registrada com motivo digitado', 'Devolvida · Rever prazo do MAP' in b, J("(document.body.innerText.match(/DOCUMENTOS DA COMPRA[^\\n]*/)||[''])[0]"))
    print('  primário devolvida:', v.prim())
    v.clk('1 Escolha a safra'); t=v.rowtxt('Safra 2026/27'); print('  etapa 1:', t); v.chk('etapa 1: devolvida', 'Devolvida pela Direção' in t, t)
    v.clk('2 Confira a demanda'); v.clk('Expandir tudo'); t=v.rowtxt('MAP 11-52'); print('  etapa 2 MAP:', t)
    v.clk('4 Compare propostas'); b=v.body(); v.chk('etapa 4: banner com o motivo', 'Devolvida pela Direção (simulado): Rever prazo do MAP' in b)
    # muda e desfaz: sem mudança líquida
    v.row('MAP 11-52'); v.setv('#'+v.fid('ped'),'62000'); v.clk('Salvar','aside[role=dialog]'); print('  toast mudança:', v.T())
    v.clk('5 Aprove a compra'); print('  primário depois da mudança:', v.prim())
    v.clk('4 Compare propostas'); v.row('MAP 11-52'); v.setv('#'+v.fid('ped'),'62500'); v.clk('Salvar','aside[role=dialog]')
    v.clk('5 Aprove a compra'); print('  primário depois de desfazer:', v.prim(), '| a5:', J("(document.body.innerText.match(/Devolvida pela[^\\n]+|Compra ajustada[^\\n]+/)||[''])[0]"))
    # muda de verdade e reenvia; depois recusa
    v.clk('4 Compare propostas'); v.row('MAP 11-52'); v.setv('#'+v.fid('ped'),'62000'); v.clk('Salvar','aside[role=dialog]')
    v.clk('5 Aprove a compra'); v.clk('Reenviar à Direção'); print('  reenviado:', v.T()[:120])
    v.clk('Registrar recusa'); v.clk('Confirmar recusa'); v.chk('recusa exige motivo', 'Informe o motivo da recusa' in v.body())
    v.typ(TA,'Sem caixa nesta safra'); v.clk('Confirmar recusa'); b=v.body()
    v.chk('recusa registrada', 'Recusada · Sem caixa nesta safra' in b and 'Não contratado' in b)
    print('  primário recusada:', v.prim())
    v.clk('6 Acompanhe a entrega'); k6=J("(document.body.innerText.match(/Nenhum pedido[^\\n]*|\\d+ pedidos da SOL[^\\n]*/)||[''])[0]"); print('  k6:', k6)
    v.chk('recusada: etapa 6 sem pedido novo', 'Nenhum pedido da SOL-2026-07 aprovado' in k6 and 'PC-101' not in v.body(), k6)
    v.clk('3 Solicite cotações'); print('  primário e3 recusada:', v.prim())
    # nova proposta depois da recusa
    v.clk('4 Compare propostas'); print('  banner e4:', J("(document.body.innerText.match(/Recusada pela[^\\n]+/)||[''])[0]"))
    v.row('MAP 11-52'); v.setv('#'+v.fid('ped'),'61000'); v.clk('Salvar','aside[role=dialog]')
    v.clk('5 Aprove a compra'); print('  primário depois de mudar:', v.prim(), '| a5:', J("(document.body.innerText.match(/Acima da sua[^\\n]+/)||[''])[0]"))
    v.chk('nova proposta depois da recusa pode ser enviada', 'Enviar à Direção' in v.prim(), v.prim())
    trail=J("(document.body.innerText.match(/DOCUMENTOS DA COMPRA[^\\n]*/)||[''])[0]"); print('  trilha:', J("document.querySelector('main').innerText.split('\\n').slice(0,20).join(' / ')")[:600])
    v.clk('1 Escolha a safra'); t=v.rowtxt('Safra 2026/27'); print('  etapa 1 depois de mudar:', t)
    v.chk('sem erro JS no fim', J("window.__err||'nenhum'")=='nenhum', J("window.__err||''"))
finally:
    v.close()
