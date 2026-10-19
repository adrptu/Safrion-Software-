#!/bin/bash
# roda.sh <gen37> <tag> <dup.json> [teste ...]: roda os testes da v55 (navegador um por vez, trava /tmp/cdpW.lock), um log por teste
G="$1"; TAG="$2"; DUP="$3"; shift 3
S=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/v55
L="$S/log-$TAG"; mkdir -p "$L"; cd "$G" || exit 2
NAV="env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpW.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3"
SEM="env SAFRION_DADOS=sintetico timeout 900 python3"
TODOS=(links_ocultos producao_unit ben_unit varredura producao_fluxo tabelas_est tabelas_ben tabelas_os tabelas_saf esttest1 esttest2 esttest3 esttest4
       est_cenario est_fix1 est_fix2 cafe_apurar ma_unica acao_familias etapas_faixa acoes_dup ben_fluxo)
LISTA=("$@"); [ ${#LISTA[@]} -eq 0 ] && LISTA=("${TODOS[@]}")
for t in "${LISTA[@]}"; do
  case "$t" in
    links_ocultos) C="$SEM links_ocultos_test.py";;
    producao_unit) C="$SEM producao_unit_test.py";;
    ben_unit) C="$SEM ben_unit_test.py";;
    varredura) C="$NAV varredura.py";;
    producao_fluxo) C="$NAV producao_fluxo_test.py";;
    tabelas_est|tabelas_ben|tabelas_os|tabelas_saf) C="$NAV ${t}_test.py";;
    esttest1|esttest2|esttest3|esttest4) C="$NAV esttest.py ${t#esttest}";;
    est_cenario|est_fix1|est_fix2) C="$NAV ${t}_test.py";;
    cafe_apurar) C="$NAV cafe_apurar_test.py";;
    ma_unica) C="$NAV ma_unica_test.py";;
    acao_familias) C="$NAV acao_unica_test.py familias";;
    etapas_faixa) C="$NAV etapas_celular_test.py faixa";;
    acoes_dup) C="$NAV ../ferramentas/acoes_duplicadas.py . $DUP";;
    ben_fluxo) C="$NAV ben_fluxo_test.py";;
    *) echo "teste desconhecido: $t"; continue;;
  esac
  t0=$(date +%s); $C > "$L/$t.log" 2>&1; rc=$?; t1=$(date +%s)
  echo "$t rc=$rc $((t1-t0))s :: $(grep -E 'RESULTADO|TOTAL|falhas|ok ·|[0-9]+ ok|FALHA' "$L/$t.log" | tail -2 | tr '\n' ' ' | cut -c1-300)" | tee -a "$L/_resumo.txt"
done
