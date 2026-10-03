# -*- coding: utf-8 -*-
"""MB-03 · fechar turno (Chrome real, ≤ 15 verificações): limite de hectares desconta os turnos no aparelho (sem sinal);
insumo fora da requisição (Adjuvante na OS-0421) sem pré-cálculo e sem baixa (informado, avisa que fecha em conferência); resumo do turno fechado com ordem, dia, ha e horas;
um único acesso a Envios e recibos. Uso: python3 app_mb03_turno_test.py   (compile antes: areas.mobile.build())"""
from app_lib import App

a = App(['MB-01', 'MB-02det', 'MB-03', 'MB-03x-recibo'])
ALR = "[...document.querySelectorAll('main [role=alert]')].map(x=>x.innerText).join(' | ')"
CORTE = """(()=>{const m=document.querySelector('main'); const mr=m.getBoundingClientRect(); const pb=parseFloat(getComputedStyle(m).paddingBottom)||0; let b=0;
 m.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect(); if(r.height>0&&r.width>0&&r.bottom>b) b=r.bottom;}); return Math.round(b-(mr.bottom-pb));})()"""
HINT = "(()=>{const i=document.querySelector('#ft_c1'); return i?i.parentElement.innerText.replace(/\\n/g,' / '):'-';})()"
try:
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
    a.mudar("return cenLiberar(c,'OS-0430');")   # 3 ordens na fila (pior caso de altura)
    a.abrir('MB-03')
    a.ok(a.J("document.querySelectorAll('main a[href=\"MB-03x-recibo.dc.html\"]').length") == 1, 'MB-03: um único link para Envios e recibos')
    a.clk_sel('main button[title="Iniciar turno na OS-0421"]'); a.setv('#ft_ha', '20'); a.setv('#ft_h', '3')
    h = a.J(HINT)
    a.ok(a.J("document.querySelector('#ft_c0').value") == '10' and a.J("document.querySelector('#ft_c1').value") == '' and 'Fora da REQ-035 · nada com você' in h,
         'consumo: Fungicida A pré-calculado 10 L; Adjuvante (fora da REQ-035) vazio com dica: ' + h[:80])
    a.setv('#ft_c1', '5'); w = a.J(HINT)   # CONC-07: acima do que está com você não é recusado; o turno fecha com o fato Em conferência
    a.ok('Acima do que está com você (0 L): fecha em conferência com Rui (almoxarife).' in w and a.J(ALR) == '' and a.cen("!!c.app.turno"),
         'Adjuvante 5 L: aviso de conferência junto ao campo, sem erro e nada gravado antes de fechar: ' + w[-90:])
    a.setv('#ft_c1', ''); a.clk('Fechar turno')
    det = a.cen("c.movs.filter(m=>m.tipo==='consumo').slice(-1)[0].det")
    a.ok(a.cen("!c.app.turno") and det == 'Fungicida A 10' and a.cen("Object.keys(c.ordens['OS-0421'].ap.slice(-1)[0].cons).join()") == 'Fungicida A',
         'fechar: movimento e apontamento só com o consumido (' + str(det) + ')')
    b = a.body()
    a.ok('Turno fechado · OS-0421 · dia 5 · 20 ha em 3 h' in b and 'Enviado · a ordem continua aberta' in b and 'Consumo: Fungicida A 10 L' in b,
         'resumo: ordem, dia, hectares e horas no título; selo de envio separado')
    k = a.J(CORTE); a.ok(k <= 0, f'MB-03 com resumo do turno e 3 ordens cabe na altura (excesso {k} px)')
    # sem sinal: o segundo turno respeita saldo − hectares no aparelho
    a.clk('Sem sinal'); a.clk_sel('main button[title="Iniciar turno na OS-0421"]'); a.setv('#ft_ha', '120'); a.setv('#ft_h', '8'); a.setv('#ft_c0', '50'); a.clk('Fechar turno')
    a.clk_sel('main button[title="Iniciar turno na OS-0421"]')
    hint = a.J("document.querySelector('#ft_ha').parentElement.innerText")
    a.ok('Máximo 20 ha: saldo 140 ha menos 120 ha no aparelho' in hint, 'dica do campo desconta o que está no aparelho: ' + hint.replace('\n', ' / ')[:90])
    a.setv('#ft_ha', '100'); a.setv('#ft_h', '7'); a.clk('Fechar turno')
    a.ok('Máximo 20 ha: é o saldo da ordem menos 120 ha no aparelho.' in a.J(ALR) and a.cen("c.app.fila.length") == 1,
         'fechar 100 ha sem sinal recusado junto ao campo; fila segue com 1')
    a.setv('#ft_ha', '20'); a.setv('#ft_h', '2'); a.setv('#ft_c0', '5'); a.clk('Fechar turno')
    a.abrir('MB-01'); b = a.body(); i = b.find('OS-0421 ·')
    a.ok('Área feita · aguardando sinal' in b[i:i + 400] and 'Ver envios' in b[i:i + 400] and 'Iniciar turno' not in b[i:i + 400],
         'MB-01: área toda no aparelho → passo "Ver envios", sem Iniciar turno')
    a.clk('Com sinal')
    a.ok(a.cen("c.ordens['OS-0421'].realizado") == 350 and a.cen("c.ordens['OS-0421'].saldo") == 0 and a.cen("c.app.fila.length") == 0,
         'sinal volta: realizado 350 de 350 ha, sem passar da área')
    a.ok(not a.erros(), 'sem erros JS ' + str(a.erros()))
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
finally:
    a.fim()
