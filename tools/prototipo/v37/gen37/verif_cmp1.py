# -*- coding: utf-8 -*-
"""Verificador · Compra (itens 01): datas de falta de todos os insumos contra o cálculo em Python, escolha atrasada justificada até o pedido,
avisos da etapa 6 em pedidos novos e antigos (inclusive voltar a data), larguras da etapa 4."""
import time, dados2 as D
from verif_cmpest_lib import V
v=V('CMP.dc.html'); J=v.J
def br(iso): return '—' if not iso else iso[8:10]+'/'+iso[5:7]+'/'+iso[:4]
try:
    v.open(); v.chk('sem erro JS', J("window.__err||'nenhum'")=='nenhum', J("window.__err||''"))
    v.clk('Abrir compra'); v.clk('Expandir tudo')
    fal=D.faltas(); dem=D.demanda('S2627')
    for n in sorted(dem):
        t=v.rowtxt(n); exp=br(fal[n])
        v.chk(f'etapa 2 · {n}: falta {exp}', (exp in t) if fal[n] else ('/20' not in t.split(n,1)[1] if n in t else False), t[:160])
    # cabeçalho da coluna e ordenação por data
    v.shot('v_cmp_e2.png')
    # origem: data no início de cada linha, em ordem
    v.row('Óleo mineral'); a=v.aside(); print('  origem Óleo mineral:', a[:500].replace('\n',' / '))
    ds=[l[:10] for l in a.split('\n') if len(l)>10 and l[2]=='/' and l[5]=='/']
    v.chk('origens em ordem de data', ds==sorted(ds,key=lambda x:x[6:]+x[3:5]+x[:2]) and len(ds)>=4, ds)
    v.clk('Fechar','aside[role=dialog]')
    # ---- etapa 3 → 4 ----
    v.clk('Solicitar cotações'); v.clk('Enviar convites (simulado)'); time.sleep(7)
    v.clk('Comparar propostas'); v.clk('Expandir tudo')
    k4=J("document.body.innerText.match(/\\d+ propostas · custo total escolhido [^\\n]+/)"); print('  k4 inicial:', k4)
    v.chk('padrão sem justificativa pendente', k4 and 'sem justificativa' not in k4[0] and 'depois da falta' not in k4[0], k4)
    # larguras: nenhuma célula da etapa 4 com conteúdo cortado
    ov=J("""[...document.querySelectorAll('[role=row].g2r [role=cell]')].filter(c=>c.offsetParent&&c.scrollWidth>c.clientWidth+1).map(c=>c.innerText.replace(/\\s+/g,' ').slice(0,40))""")
    v.chk('etapa 4 sem célula cortada', not ov, ov[:8] if ov else '')
    tw=J("Math.max(...[...document.querySelectorAll('[role=table],[role=grid],[role=treegrid]')].filter(x=>x.offsetParent).map(x=>x.scrollWidth))"); print('  largura tabela etapa 4:', tw)
    hs=J("document.documentElement.scrollWidth>document.documentElement.clientWidth"); v.chk('sem rolagem horizontal da página', not hs)
    v.shot('v_cmp_e4.png')
    # Santa Rita para o 2,4-D com justificativa
    r=J("""(()=>{const rows=[...document.querySelectorAll('[role=row].g2ed')]; const i=rows.findIndex(r=>/2,4-D 806/.test(r.innerText)); const k=rows.slice(i+1).find(r=>/Santa Rita Insumos/.test(r.innerText)); if(!k) return 'sem proposta'; k.querySelector('[role=cell] span').click(); return 'ok';})()"""); time.sleep(.4)
    print('  ajuda:', v.J("[...document.querySelectorAll('aside [id$=_venc]')].map(x=>x.closest('label,div').innerText).join('|')")[:300])
    v.setv('#'+v.fid('just'),'Agro Norte sem estoque para entrega imediata'); v.clk('Salvar','aside[role=dialog]')
    t=v.rowtxt('2,4-D 806'); print('  2,4-D escolhido:', t)
    v.chk('2,4-D: Santa Rita justificada e com selo de atraso', 'Santa Rita' in t and 'Justificada' in t and 'Chega depois da falta (28/09)' in t, t)
    k4=J("document.body.innerText.match(/\\d+ propostas · custo total escolhido [^\\n]+/)"); print('  k4:', k4)
    v.chk('resumo da etapa 4 conta a escolha que chega depois da falta', k4 and '1 escolha chega depois da falta' in k4[0], k4)
    # MAP 40 t para ficar na alçada da Ana
    v.row('MAP 11-52'); v.setv('#'+v.fid('ped'),'40000'); v.clk('Salvar','aside[role=dialog]')
    v.clk('Revisar aprovação'); b=v.body(); print('  a5:', J("document.body.innerText.match(/Valor dentro[^\\n]+|Acima da sua[^\\n]+|Justifique[^\\n]+/)"))
    v.clk('Expandir tudo')
    t=v.after('Santa Rita','2,4-D 806'); print('  e5 2,4-D:', t)
    v.row('2,4-D 806'); a=v.aside(); print('  origem e5:', a.replace('\n',' / ')[:600])
    v.chk('etapa 5 mostra justificativa e datas', 'Escolha justificada: Agro Norte sem estoque' in a and 'Chega 30/09/2026 · falta a partir de 28/09/2026' in a, a[:300])
    v.clk('Fechar','aside[role=dialog]')
    v.clk('Aprovar compra'); v.clk('Confirmar aprovação'); print('  aprovada:', v.T())
    v.clk('Acompanhar entrega'); v.clk('Expandir tudo')
    peds=J("[...document.querySelectorAll('[role=row].g2r')].map(r=>r.innerText.replace(/\\s+/g,' ')).filter(t=>/PC-1\\d\\d/.test(t))"); print('  pedidos novos:'); [print('   ',x[:220]) for x in peds]
    sr=[x for x in peds if 'Santa Rita' in x]
    v.chk('pedido da Santa Rita avisa chegada depois da falta sem reprogramar', sr and 'Chega depois da falta (28/09)' in sr[0], sr)
    srid=sr[0].split()[0] if sr else ''
    # reprogramar para antes da falta: aviso some
    if srid:
        v.row(srid); v.setv('#'+v.fid('prev'),'2026-09-27'); v.clk('Salvar','aside[role=dialog]'); t=v.rowtxt(srid); print('  ',srid,'27/09:',t[:200])
        v.chk('reprogramado para antes da falta: sem aviso', 'depois da falta' not in t, t)
    # pedidos antigos
    v.row('PC-091'); v.setv('#'+v.fid('prev'),'2026-10-26'); v.clk('Salvar','aside[role=dialog]'); t=v.rowtxt('PC-091'); print('  PC-091:',t[:220], '|', v.T())
    v.chk('PC-091 depois de 25/10 avisa', 'Nova data depois da falta de 25/10' in t, t)
    v.row('PC-088'); v.setv('#'+v.fid('prev'),'2026-11-08'); v.clk('Salvar','aside[role=dialog]'); t=v.rowtxt('PC-088'); print('  PC-088:',t[:260])
    v.chk('PC-088 depois de 07/11 avisa', 'Nova data depois da falta de 07/11' in t, t)
    v.shot('v_cmp_e6.png')
    v.clk('2 Confira a demanda'); v.clk('Expandir tudo'); t=v.rowtxt('KCl 60%'); print('  KCl etapa 2:', t)
    v.chk('KCl passa a faltar em 07/11/2026', '07/11/2026' in t and 'chega depois da falta' in t, t)
    t=v.rowtxt('Semente de soja 62 X'); print('  62 X etapa 2:', t); v.chk('62 X passa a faltar em 25/10/2026', '25/10/2026' in t, t)
    v.clk('6 Acompanhe a entrega'); v.row('PC-088'); v.setv('#'+v.fid('prev'),'2026-10-02'); v.clk('Salvar','aside[role=dialog]'); t=v.rowtxt('PC-088')
    v.chk('PC-088 de volta a 02/10: aviso some', 'depois da falta' not in t, t)
    v.clk('2 Confira a demanda'); v.clk('Expandir tudo'); t=v.rowtxt('KCl 60%'); v.chk('KCl volta a —', '07/11' not in t, t)
    v.chk('sem erro JS no fim', J("window.__err||'nenhum'")=='nenhum', J("window.__err||''"))
finally:
    v.close()
