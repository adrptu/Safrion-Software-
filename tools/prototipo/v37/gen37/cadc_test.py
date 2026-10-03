# -*- coding: utf-8 -*-
"""Testes da frente Cadastros · CD-02, CD-06 e CD-07 — uma tela por execução (≤ 15 verificações cada, < 30 s no Chrome headless).
Uso: python3 cadc_test.py cd02 | cd06 | cd07 | cd0102a | cd0102b | fix02 | fix06 | fix07
  cd02     cadc_cd02_test.py    culturas e operações cadastráveis, semente vinculada (e o item chegando ao CD-06), rendimento por cultura
  cd06     cadc_cd06_test.py    grupo com natureza, preço com data, embalagem, controle, situação, unidade travada, locais com fazenda
  cd07     cadc_cd07_test.py    árvore Dimensão → código, Cultura/Processo do CD-02, vínculos, versão, Importar do ERP, Publicar
  cd0102a  cadc_cd0102_a.py     parte CD-02 do cd0102test.py (lista e cálculo ao vivo), adaptada às abas e à árvore
  cd0102b  cadc_cd0102_b.py     parte CD-02 do cd0102test.py (salvar, modo Informado, mesmos campos no Planejar safra)
  fix02    cadc_fix_cd02.py     defeitos do verificador no CD-02 (cultura padrão renomeada, Operação do rendimento, selo verde, folga do artboard)
  fix06    cadc_fix_cd06.py     defeitos do verificador no CD-06 (item sem preço, grupo padrão renomeado, selo verde, Local padrão dos locais)
  fix07    cadc_fix_cd07.py     defeitos do verificador no CD-07 (exclusão no rascunho, Importar do ERP sem duplicar, selo verde)
Grade G2 nas três telas: python3 g2test.py CD-02.dc.html CD-06.dc.html CD-07.dc.html e python3 cadc_g2arvore.py (mesmas telas)."""
import sys, os, runpy
ARQ={'cd02':'cadc_cd02_test.py','cd06':'cadc_cd06_test.py','cd07':'cadc_cd07_test.py','cd0102a':'cadc_cd0102_a.py','cd0102b':'cadc_cd0102_b.py',
     'fix02':'cadc_fix_cd02.py','fix06':'cadc_fix_cd06.py','fix07':'cadc_fix_cd07.py'}
if __name__=='__main__':
    if len(sys.argv)<2 or sys.argv[1] not in ARQ: print(__doc__); sys.exit(0)
    runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)),ARQ[sys.argv[1]]),run_name='__main__')
