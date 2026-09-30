# -*- coding: utf-8 -*-
"""MB-03x-recibo · envios e recibos (Chrome real, ≤ 15 verificações): a tela cabe na altura do quadro com muitos registros no aparelho
e recibos longos (listas com teto e contagem do resto); a barra de sinal não aponta para a própria tela.
Uso: python3 app_mb03x_test.py   (compile antes: areas.mobile.build())"""
from app_lib import App

# corte: maior bottom de qualquer descendente visível de <main> contra a borda interna (mesma medida do verificador)
CORTE = """(()=>{const m=document.querySelector('main'); const mr=m.getBoundingClientRect(); const pb=parseFloat(getComputedStyle(m).paddingBottom)||0; let b=0;
 m.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect(); if(r.height>0&&r.width>0&&r.bottom>b) b=r.bottom;}); return Math.round(b-(mr.bottom-pb));})()"""
OC = "return cenOcorrencia(c,'OS-0421','Falha de aplicação','Seção 3 da barra falhou; troquei o bico e segui.');"
a = App(['MB-01', 'MB-03x-recibo'])
try:
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
    for _ in range(2):   # dois envios com 4 registros cada → recibos REC-7742 e REC-7743
        a.mudar("return cenSinal(c,false);")
        for _ in range(4): a.mudar(OC)
        a.abrir('MB-03x-recibo'); a.clk('Com sinal')
    a.mudar("return cenSinal(c,false);"); a.mudar("return cenIniciarTurno(c,'OS-0421');"); a.mudar("return cenFecharTurno(c,20,3,null,'');")
    for _ in range(7): a.mudar(OC)
    a.abrir('MB-03x-recibo'); b = a.body(); k = a.J(CORTE)
    a.ok(a.cen("c.app.fila.length") == 8 and '8 registros aguardando sinal' in b, 'pré-carga: 8 registros no aparelho e 2 recibos')
    a.ok(k <= 0, f'8 no aparelho + 2 recibos de 4 itens cabem na altura (excesso {k} px)')
    a.ok('+ 5 outros registros' in b and '+ 2 outros registros' in b and 'REC-7743' in b and 'REC-7742' in b,
         'listas com teto: 3 no aparelho + "+ 5 outros registros"; recibos com 2 itens + "+ 2 outros registros"')
    a.ok(a.J("document.querySelectorAll('main a[href=\"MB-03x-recibo.dc.html\"]').length") == 0, 'sem link para a própria tela')
    a.ok(a.foot() == 'Reenviar pendentes', 'rodapé: Reenviar pendentes (' + a.foot() + ')')
    a.clk('Com sinal'); b = a.body(); k = a.J(CORTE)
    a.ok('REC-7744' in b and 'Nada aguardando sinal' in b and a.foot() == 'Voltar à fila' and k <= 0,
         f'sinal volta: REC-7744 com 8 registros, rodapé Voltar à fila e cabe (excesso {k} px)')
    a.ok(not a.erros(), 'sem erros JS ' + str(a.erros()))
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
finally:
    a.fim()
