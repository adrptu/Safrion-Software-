#!/bin/bash
# Portão: só inicia um teste de navegador com no máximo 1 navegador rodando (contagem pedida). Um teste por vez.
S=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/pr89
CAND=/tmp/claude-0/pr89/tools/prototipo/v37/gen37
BASE=$S/base/tools/prototipo/v37/gen37
TRI=$S/tab11/tools/prototipo/v37/gen37
conta(){ ps -eo args | grep -E '/chrome-linux/chrome ' | grep -v -- '--type=' | grep -v grep | wc -l; }
gate(){ while :; do n=$(conta); [ "$n" -le 1 ] && break; sleep 0.5; done; }
run(){ local label=$1 dir=$2; shift 2
  gate; echo "$(date -u +%FT%TZ) INICIO $label navegadores=$(conta)" >> $S/runner.log
  ( cd "$dir" && env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico "$@" ) > $S/$label.log 2>&1
  local rc=$?; echo "$(date -u +%FT%TZ) FIM $label exit=$rc $(grep -E 'RESULTADO|"ok":|^# ' $S/$label.log | tail -1)" >> $S/runner.log; }
for t in "$@"; do
  case $t in
    C1) run visoes2_formas_candidata $CAND python3 -B visoes2_formas_test.py ;;
    B1) run visoes2_formas_novo_sobre_base $CAND env RENDER_DIR=$BASE/_render python3 -B visoes2_formas_test.py ;;
    B1o) run visoes2_formas_antigo_base $BASE python3 -B visoes2_formas_test.py ;;
    C2) run tabelas_os_candidata $CAND python3 -B tabelas_os_test.py ;;
    B2) run tabelas_os_base $BASE python3 -B tabelas_os_test.py ;;
    C3) run os_cenario_candidata $CAND python3 -B os_cenario_test.py ;;
    B3) run os_cenario_base $BASE python3 -B os_cenario_test.py ;;
    C4) run os_lote_candidata $CAND env RENDER_DIR=$CAND/_render OS_LOTE_EVIDENCIA=$S/oslote_c python3 -B os_lote_test.py ;;
    B4) run os_lote_base $BASE env RENDER_DIR=$BASE/_render OS_LOTE_EVIDENCIA=$S/oslote_b python3 -B os_lote_test.py ;;
    C5) run ds_modulos_catraca_candidata $CAND env DS_MOD_JSON=$S/ds_modulos_candidata.json python3 -B ds_modulos.py --catraca ;;
    B5) run ds_modulos_catraca_base $BASE env DS_MOD_JSON=$S/ds_modulos_base.json python3 -B ds_modulos.py --catraca ;;
    R1) run visoes2_formas_rev_candidata $CAND python3 -B visoes2_formas_test_rev.py ;;
    R2) run visoes2_formas_rev_sobre_base $CAND env RENDER_DIR=$BASE/_render python3 -B visoes2_formas_test_rev.py ;;
    P1) run sonda_raia_candidata $CAND env GEN=$CAND RENDER_DIR=$CAND/_render SHOTS=$S/shots_c python3 -B $S/sonda_raia.py ;;
    P2) run sonda_raia_base $CAND env GEN=$CAND RENDER_DIR=$BASE/_render SHOTS=$S/shots_b python3 -B $S/sonda_raia.py ;;
    T1) run seta_padrao_OS_tab11_adaptada $TRI env SPT_SO=OS.dc.html python3 -B seta_padrao_test.py ;;
    T2) run sonda_raia_tab11_adaptada $TRI env GEN=$TRI RENDER_DIR=$TRI/_render SHOTS=$S/shots_t LAB_FECHADA=Abrir python3 -B $S/sonda_raia.py ;;
    T3) run visoes2_formas_rev_tab11_adaptada $TRI python3 -B visoes2_formas_test_rev.py ;;
    T4) run seta_padrao_OS_tab11_sem_adaptacao $TRI env SPT_SO=OS.dc.html python3 -B seta_padrao_test.py ;;
  esac
done
echo "$(date -u +%FT%TZ) LOTE FIM $*" >> $S/runner.log
