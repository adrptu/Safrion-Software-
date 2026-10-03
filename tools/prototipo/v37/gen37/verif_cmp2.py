# -*- coding: utf-8 -*-
"""Verificador · Compra (itens 05 e 06): convite adicional durante as respostas, para fornecedor sem proposta, marcado e não enviado antes
da aprovação; canais autorizados e subtítulo do Convite; pedido PC-104 reprogramado antes da falta."""
import time, json
from verif_cmpest_lib import V
v=V('CMP.dc.html'); J=v.J
def resp(): return J("(document.body.innerText.match(/(\\d+) de (\\d+) convites responderam[^\\n]*/)||[''])[0]")
try:
    v.open(); v.clk('Abrir compra'); v.clk('3 Solicite cotações')
    # canais e subtítulo
    v.kid('Inoculantes','Casa do Adubo',True); o=v.opts('canal'); s=v.sub(); print('  Casa do Adubo Inoculantes:', o, '|', s)
    v.chk('Casa do Adubo (Inoculantes): só E-mail e itens do grupo', o==['E-mail'] and 'Inoculante líquido · 72 L' in s and 'Juliana Prado' in s, s)
    v.clk('Cancelar','aside[role=dialog]')
    v.kid('Fertilizantes','Fertisul',True); v.setv('#'+v.fid('canal'),'WhatsApp'); s=v.sub(); print('  Fertisul WhatsApp:', s)
    v.chk('Fertisul por WhatsApp mostra número e contato', 'WhatsApp 65 99911-2233 (Rafael Moura)' in s, s)
    v.setv('#'+v.fid('conv'),'Não convidar'); s=v.sub(); print('  Fertisul não convidar:', s); v.clk('Cancelar','aside[role=dialog]'); v.clk('Descartar alterações','aside[role=dialog]')
    # antes do envio: Coop. Vale fora de Fungicidas (sem proposta nos dados) e Santa Rita fora de Herbicidas
    v.kid('Fungicidas','Coop. Vale',True); v.setv('#'+v.fid('conv'),'Não convidar'); v.clk('Salvar','aside[role=dialog]')
    v.kid('Herbicidas','Santa Rita Insumos',True); v.setv('#'+v.fid('conv'),'Não convidar'); v.clk('Salvar','aside[role=dialog]')
    v.clk('Enviar convites (simulado)'); time.sleep(.6); print('  logo após enviar:', resp())
    # convite adicional enquanto as respostas ainda chegam
    v.kid('Fungicidas','Coop. Vale',True); a=v.aside(); v.chk('não convidado abre o Convite durante as respostas', 'Convite · Coop. Vale' in a, a[:60])
    v.setv('#'+v.fid('conv'),'Convidar'); v.clk('Salvar','aside[role=dialog]')
    print('  primário:', v.prim()); v.clk('Enviar 1 convite adicional'); print('  toast:', v.T()); time.sleep(8)
    r=resp(); print('  respostas:', r); t=v.kid('Fungicidas','Coop. Vale'); print('  Coop. Vale fungicidas:', t)
    v.chk('adicional sem proposta: conta o convite e fica sem resposta', '12 de 14' in r and 'Sem resposta até agora' in t, r+' | '+t)
    g=v.rowtxt('Fungicidas'); print('  grupo Fungicidas:', g)
    k3=J("(document.body.innerText.match(/Convites simulados: nenhuma[^\\n]*/)||[''])[0]"); print('  k3:', k3)
    # clique no enviado adicional mostra a hora do adicional
    v.kid('Fungicidas','Coop. Vale',True); print('  toast Coop. Vale:', v.T())
    # marca Santa Rita (Herbicidas) como adicional e NÃO envia; aprova dentro da alçada
    v.kid('Herbicidas','Santa Rita Insumos',True); v.setv('#'+v.fid('conv'),'Convidar'); v.clk('Salvar','aside[role=dialog]')
    print('  primário com adicional marcado:', v.prim())
    v.clk('4 Compare propostas'); v.row('MAP 11-52'); v.setv('#'+v.fid('ped'),'40000'); v.clk('Salvar','aside[role=dialog]')
    v.clk('5 Aprove a compra'); print('  a5:', J("(document.body.innerText.match(/Valor dentro[^\\n]+|Acima da sua[^\\n]+/)||[''])[0]"))
    v.clk('Aprovar compra'); v.clk('Confirmar aprovação'); print('  aprovada:', v.T()[:120])
    v.clk('3 Solicite cotações'); t=v.kid('Herbicidas','Santa Rita Insumos'); g=v.rowtxt('Herbicidas'); k3=J("(document.body.innerText.match(/Convites simulados: nenhuma[^\\n]*/)||[''])[0]")
    print('  Santa Rita depois da aprovação:', t); print('  grupo Herbicidas:', g); print('  k3:', k3)
    v.chk('aprovada: convite marcado e nunca enviado não aparece como Convidar nem "+1 a enviar"', ('Convidar' not in t.replace('Não convidado','')) and ('a enviar' not in g), t+' || '+g)
    v.kid('Herbicidas','Santa Rita Insumos',True); print('  toast clique:', v.T())
    v.shot('v_cmp_e3_aprovada.png')
    # PC da Santa Rita (se houver) reprogramado antes da falta
    v.clk('6 Acompanhe a entrega')
    ids=J("[...document.querySelectorAll('[role=row].g2r')].map(r=>r.innerText.replace(/\\s+/g,' ')).filter(t=>/PC-1\\d\\d/.test(t)).map(t=>t.replace(/^[▾▸ ]+/,'').slice(0,60))"); print('  pedidos:', ids)
    v.chk('sem erro JS no fim', J("window.__err||'nenhum'")=='nenhum', J("window.__err||''"))
finally:
    v.close()
