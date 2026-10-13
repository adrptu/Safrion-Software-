#!/bin/bash
# Seleção pelo impacto: para cada vermelho de integração (V56 e CTL-4), a lista da mudança que o causou tem de incluir o teste
# que pegou o vermelho. Uma linha por caso: base → cabeça, testes esperados, presença, tamanho da lista. Ferramentas finais.
O=$(dirname "$0"); T=/home/user/sp-acel/tools/prototipo/v37/ferramentas/testes_afetados.py
caso() {  # nome base cabeça testes...
  n=$1; b=$2; c=$3; shift 3
  python3 $T $b $c --motivos > $O/$n.txt 2> $O/$n.err; rc=$?
  tam=$(head -1 $O/$n.err | grep -o '[0-9]* de [0-9]* testes')
  res=""; for t in "$@"; do if grep -q "^$t  ::" $O/$n.txt; then res="$res $t=SIM[$(grep "^$t  ::" $O/$n.txt | sed 's/.*:: //' | cut -c1-90)]"; else res="$res $t=NAO"; fi; done
  echo "$n rc=$rc $b→$c ($tam):$res"
}
caso DSxTABR_490301f        d30f30b 4afd477 tabelas_irr_test.py
caso TABRxBEN_1e847eb       d30f30b 4afd477 tabelas_cad_test.py
caso TABRxSOLO_8245911      7cd0082 afc38fa tabelas_cad_test.py cadc_cd02_test.py
caso CTL5xTABR_885a68c      4afd477 7cd0082 ctl5_test.py ficha_pivo_test.py
caso CTL5xSOLO_885a68c      7cd0082 afc38fa ficha_pivo_test.py
caso COMxBEN_1f83eee_juncao a676ac0 e9670f0 comercial_fluxo_test.py
caso COMxBEN_1f83eee_pv031  ab25ec2 0ad2d0d comercial_fluxo_test.py
caso CTL4_78711bb           853a6a8 4130972 saf_cmp_continuidade_test.py esttest.py
# mudanças pequenas (o próprio commit de correção) e só documentação
caso fix_490301f 5d2119c 490301f tabelas_irr_test.py
caso fix_1e847eb 490301f 1e847eb tabelas_cad_test.py
caso fix_8245911 1e847eb 8245911 tabelas_cad_test.py
caso fix_885a68c 8245911 885a68c ctl5_test.py ficha_pivo_test.py
caso fix_1f83eee 885a68c 1f83eee comercial_fluxo_test.py
caso fix_93ca16c e9670f0 93ca16c ds_unit_test.py
caso fix_ab25ec2 93ca16c ab25ec2 tabelas_cad_irr_unit.py
caso fix_78711bb 6202376 78711bb saf_cmp_continuidade_test.py esttest.py
caso so_docs     1f83eee 302b26f
echo FIM_VALIDA
