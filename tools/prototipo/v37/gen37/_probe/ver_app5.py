# -*- coding: utf-8 -*-
"""Verificador App 5: altura/corte e largura das 7 telas do cenário num estado carregado (3 ordens, 8 registros no aparelho, turno aberto com erros, recibos)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
def medir(t, rot=''):
    v.abrir(t); c = v.corte(); w = [x for x in v.larg() if 'registrad' not in x and 'recibo' not in x.lower()]
    print(f'   {t:14s} {rot:28s} corte {c["excesso"]:5d} ({c["who"][:30]!r}) larg {w} foot {v.foot()!r}')
    v.ok(c['excesso'] <= 0 and not w, f'{t} {rot}: sem corte/estouro (excesso {c["excesso"]})')
    return c
try:
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
    v.mudar("c.ordens['OS-0430'].aprov=true; return cenLiberar(c,'OS-0430');"); rid = v.cen("c.ordens['OS-0430'].req")
    for prod, q in (('Glifosato 480', 320), ('2,4-D 806', 160), ('Óleo mineral', 80)): v.mudar(f"return cenEntregar(c,'{rid}','{prod}',{q},'Marcos');")
    v.mudar("return cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos');")
    v.mudar("return cenSinal(c,false);")
    v.mudar("return cenConfirmarRecebimento(c,'REQ-039');"); v.mudar(f"return cenConfirmarRecebimento(c,'{rid}');")
    for os_ in ('OS-0421', 'OS-0424', 'OS-0430'):
        v.mudar(f"return cenIniciarTurno(c,'{os_}');"); v.mudar("return cenFecharTurno(c,10,2,null,'');")
    for i in range(3): v.mudar(f"return cenOcorrencia(c,'OS-0430','Clima','Vento forte no talhão T1-A às 10:{i}0; parei a barra por vinte minutos e retomei.');")
    v.mudar("return cenIniciarTurno(c,'OS-0430');"); v.mudar("return cenPausar(c);")
    print('   fila:', v.cen('c.app.fila.length'), 'turno:', v.cen('c.app.turno.os'))
    medir('MB-01', 'fila 8 + turno pausado')
    medir('MB-02', 'fila 8 + turno pausado')
    for o in ('OS-0421', 'OS-0424', 'OS-0430'):
        v.J(f"localStorage.setItem('talhao-os-mb-os','{o}')"); medir('MB-02det', o)
    v.abrir('MB-03'); v.setv('#ft_ha', '999'); v.setv('#ft_h', '99')
    for i in range(3): v.setv(f'#ft_c{i}', '9999')
    v.clk('Fechar turno'); print('   alerts:', v.alerts()[:200]); c = v.corte(); print('   MB-03 turno + erros corte', c, v.larg())
    v.ok(c['excesso'] <= 0, 'MB-03 turno com 3 consumos e todos os erros cabe ' + str(c)); v.shot('ver_app5_mb03_erros.png')
    medir('MB-03x-recibo', '8 registros no aparelho'); v.shot('ver_app5_mb03x.png')
    medir('MB-04', 'lista com 3')
    medir('MB-05', 'tudo com você')
    v.abrir('MB-01'); v.clk('Com sinal'); print('   sinal:', v.toast()[:80])
    medir('MB-03x-recibo', 'recibo com 8 itens'); v.shot('ver_app5_mb03x_rec.png')
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
finally:
    v.fim()
