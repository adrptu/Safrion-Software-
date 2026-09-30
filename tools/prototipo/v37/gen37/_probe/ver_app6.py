# -*- coding: utf-8 -*-
"""Verificador App 6: limiar de corte com textos curtos (MB-03x-recibo por nº de registros, MB-04 com 3 ocorrências, MB-02det OS-0430, MB-03 com 200 ha)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
try:
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
    v.mudar("c.ordens['OS-0430'].aprov=true; return cenLiberar(c,'OS-0430');"); rid = v.cen("c.ordens['OS-0430'].req")
    for prod, q in (('Glifosato 480', 320), ('2,4-D 806', 160), ('Óleo mineral', 80)): v.mudar(f"return cenEntregar(c,'{rid}','{prod}',{q},'Marcos');")
    v.mudar(f"return cenConfirmarRecebimento(c,'{rid}');")
    # MB-03: turno na OS-0430, 200 ha (acima do saldo) e 5 h
    v.mudar("return cenIniciarTurno(c,'OS-0430');")
    v.abrir('MB-03'); v.setv('#ft_ha', '200'); v.setv('#ft_h', '5'); v.clk('Fechar turno')
    c = v.corte(); print('   MB-03 200 ha:', c, '| alerts:', v.alerts()[:160])
    v.ok(c['excesso'] <= 0, 'MB-03 OS-0430 com 200 ha e 5 h (erro de saldo + 3 de consumo) cabe: ' + str(c))
    v.J("(()=>{const m=document.querySelector('main'); m.parentElement.scrollIntoView(); })()")
    v.c.size(1440, 1600); time.sleep(.3); v.shot('ver_app6_mb03_200ha.png'); v.c.size(1440, 1000)
    # MB-02det OS-0430: 1 turno sem sinal + k ocorrências curtas
    v.mudar("return cenSinal(c,false);")
    v.mudar("return cenFecharTurno(c,40,4,null,'');")
    v.J("localStorage.setItem('talhao-os-mb-os','OS-0430')")
    for k in range(1, 4):
        v.mudar("return cenOcorrencia(c,'OS-0430','Clima','Vento forte; parei 20 min.');")
        v.abrir('MB-02det'); c = v.corte(); print(f'   MB-02det OS-0430 com {k} ocorrência(s) curtas:', c)
        if k == 2: v.ok(c['excesso'] <= 0, 'MB-02det OS-0430 com 1 apontamento e 2 ocorrências curtas cabe: ' + str(c))
    v.c.size(1440, 1700); time.sleep(.3); v.shot('ver_app6_mb02det.png'); v.c.size(1440, 1000)
    # MB-04 com 3 ocorrências curtas (formulário aberto)
    v.abrir('MB-04'); c = v.corte(); print('   MB-04 form + 3 curtas:', c)
    v.ok(c['excesso'] <= 0, 'MB-04 com formulário e 3 ocorrências curtas cabe: ' + str(c))
    v.c.size(1440, 1300); time.sleep(.3); v.shot('ver_app6_mb04.png'); v.c.size(1440, 1000)
    # MB-03x-recibo: registros no aparelho (1 apontamento + 3 ocorrências = 4, depois +1 a +3)
    for extra in range(0, 4):
        if extra: v.mudar("return cenOcorrencia(c,'OS-0421','Outro','Teste.');")
        v.abrir('MB-03x-recibo'); c = v.corte(); n = v.cen('c.app.fila.length'); print(f'   MB-03x-recibo com {n} no aparelho:', c)
        if n == 5: v.ok(c['excesso'] <= 0, f'MB-03x-recibo com {n} registros no aparelho cabe: ' + str(c))
    v.c.size(1440, 1400); time.sleep(.3); v.shot('ver_app6_mb03x.png'); v.c.size(1440, 1000)
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
finally:
    v.fim()
