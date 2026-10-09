#!/bin/bash
# Testes de navegador da integração BEN, um por vez no lock I.
L=<scratchpad>/integ/BEN-1711
cd <sp-proto>/tools/prototipo/v37/gen37 || exit 9
run(){ nome=$1; shift; log=$L/$nome.log
  env CHROME_BIN=<chrome> flock /tmp/cdpI.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 "$@" > "$log" 2>&1; rc=$?
  echo "$nome rc=$rc · $(grep -a -E 'RESULTADO|TOTAL|passou|falhas|[0-9]+/[0-9]+' "$log" | tail -1 | cut -c1-160)" >> $L/nav_resumo.txt; }
: > $L/nav_resumo.txt
run ben_fluxo_test ben_fluxo_test.py fluxo erros celular revisao
run tabelas_ben_test tabelas_ben_test.py
run producao_fluxo_test producao_fluxo_test.py
run tabelas_est_test tabelas_est_test.py
run cada_cd04_test cada_cd04_test.py
run est_cenario_test est_cenario_test.py
run os_cenario_test os_cenario_test.py
run cada_cd03_test cada_cd03_test.py
run cadc_cd06_test cadc_cd06_test.py
run app_cenario_test app_cenario_test.py
run acoes_duplicadas ../ferramentas/acoes_duplicadas.py . $L/acoes_duplicadas.json
echo FIM >> $L/nav_resumo.txt
