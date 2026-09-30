# -*- coding: utf-8 -*-
"""CD-07 · defeitos do verificador (12 verificações no Chrome): excluir um código entra no rascunho e só sai na publicação;
excluir um código novo do rascunho só o tira do rascunho; 'Importar do ERP' não duplica código que já está na dimensão;
selo na cor de concluído quando não há rascunho nem pendência."""
from cadc_lib import T
import time
t=T(); J=t.J
PV="(document.querySelector('[aria-label=\"Prévia da importação do ERP\"]')||{}).innerText||''"
NCOD="(c)=>[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')].filter(r=>r.innerText.trim().split(/\\s+/)[0]===c).length"
try:
    t.goto('CD-07.dc.html')
    # defeito 4 · exclusão entra no rascunho
    t.clk('Publicar estrutura'); time.sleep(.2)
    t.chk('publicada a v6: selo amarelo pela tradução pendente', 'v6 em vigor · 1 tradução pendente' in t.header() and t.chipcor()=='yellow', [t.header(),t.chipcor()])
    ok=t.delrow(0,'PRJ-PIVO3'); r=t.rowtxt(0,'PRJ-PIVO3') or ''
    t.chk('excluir PRJ-PIVO3 entra no rascunho v7 e o código continua visível até publicar',
          ok and 'rascunho v7 com 1 alteração' in t.header() and 'Excluído sai na v7' in r and 'rascunho v7' in t.toast(), [ok,t.header(),r,t.toast()])
    t.chk('código marcado para exclusão não oferece a lixeira de novo', not J(f"(()=>{{const r={t.ROW(0,'PRJ-PIVO3')}; return !!(r&&r.querySelector('button.g2del'));}})()"), r)
    t.openrow(0,'PRJ-PIVO3'); d=t.dlg(); ro=t.fdis('conta')
    t.chk('código excluído abre só em consulta, dizendo quando sai', 'Excluído no rascunho v7' in d and ro and 'Salvar' not in d, d[:200])
    t.cancel()
    t.clk('Publicar estrutura'); time.sleep(.2); ts=t.toast()
    t.chk('publicar a v7 tira o código excluído e preserva a v6',
          'estrutura v7 publicada' in ts and '1 código excluído' in ts and 'v6 preservada' in ts and not t.rowtxt(0,'PRJ-PIVO3') and 'v7 em vigor' in t.header() and 'rascunho' not in t.header(), [ts,t.header()])
    t.chk('sem rascunho e sem pendência: selo verde', t.chipcor()=='green', [t.header(),t.chipcor()])
    # código novo no rascunho: excluir só o tira do rascunho
    t.clk('Cadastrar código')
    for k,v in [('dim','Projeto'),('cod','PRJ-X'),('nome','Teste'),('ini','2026-10-01'),('conta','proj 9')]: t.fset(k,v)
    t.btn('Salvar'); time.sleep(.2); h1=t.header(); t.delrow(0,'PRJ-X')
    t.chk('código novo excluído sai do rascunho na hora', 'rascunho v8 com 1 alteração' in h1 and not t.rowtxt(0,'PRJ-X') and 'rascunho' not in t.header(), [h1,t.header(),t.toast()])
    # defeito 5 · Importar do ERP com o código já na dimensão
    t.goto('CD-07.dc.html'); t.clk('Cadastrar código')
    for k,v in [('cod','3.1.07'),('nome','Serviços de terceiros'),('sup','3.1'),('ini','2026-07-01'),('conta','4.1.1.07')]: t.fset(k,v)
    t.btn('Salvar'); time.sleep(.2); t.clk('Importar do ERP'); pv=J(PV)
    nov=pv.split('NOVOS NO ERP')[1].split('ALTERADO NO ERP')[0] if 'NOVOS NO ERP' in pv and 'ALTERADO NO ERP' in pv else pv
    t.chk('prévia não lista como novo o 3.1.07 já cadastrado', '3.1.07' not in nov and 'CC-ARM' in nov, pv[:400])
    t.clk('Trazer'); time.sleep(.2); n=J(f"({NCOD})('3.1.07')")
    t.chk('importação mantém um só 3.1.07 na Natureza e traz o CC-ARM', n==1 and t.rowtxt(0,'CC-ARM'), [n,t.toast()])
    t.clk('Importar do ERP')
    t.chk('segunda importação não repete as mudanças', 'não tem mudanças novas' in t.toast(), t.toast())
    t.chk('nenhum erro de JS', not t.errs(), t.errs())
    t.shot('cadc_fix_cd07.png')
finally:
    t.fim()
