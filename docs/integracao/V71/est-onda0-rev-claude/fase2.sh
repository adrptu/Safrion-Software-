#!/bin/bash
# Fase 2 da regressão: partes longas separadas, testes ajustados (PR e base) e vermelhos do PR na base. Um por vez, timeout 900.
O=/tmp/claude-0/pr81/docs/integracao/V71/est-onda0-rev-claude; PR=/tmp/claude-0/pr81/tools/prototipo/v37/gen37; BA=/tmp/claude-0/pr81base/tools/prototipo/v37/gen37
mkdir -p $O/fase2; R=$O/fase2/_resumo.txt
roda(){ rot="$1"; dir="$2"; shift 2; ini=$(date +%s)
  ( cd "$dir" && timeout 900 env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico GEN="$dir" python3 -B "$@" ) > "$O/fase2/$rot.log" 2>&1; rc=$?
  res=$(grep -a "RESULTADO" "$O/fase2/$rot.log" | tail -n 1); [ -z "$res" ] && res="(sem RESULTADO) $(tail -n 1 "$O/fase2/$rot.log" | cut -c1-200)"
  echo "$rot | rc=$rc | $(( $(date +%s)-ini ))s | $res" | tee -a $R; }
# C · ajustes propostos, no PR e na base
roda pr_est_cenario_ajuste $PR $O/est_cenario_test_ajuste.py
roda base_est_cenario_ajuste $BA $O/est_cenario_test_ajuste.py
roda pr_est_sem_validade_ajuste $PR $O/est_sem_validade_nav_ajuste.py
roda base_est_sem_validade_ajuste $BA $O/est_sem_validade_nav_ajuste.py
roda pr_esttest_ajuste_p2 $PR $O/esttest_ajuste.py 2
roda base_esttest_ajuste_p2 $BA $O/esttest_ajuste.py 2
roda pr_map_decisoes_ajuste $PR $O/map_decisoes_test_ajuste.py
roda base_map_decisoes_ajuste $BA $O/map_decisoes_test_ajuste.py
# D · vermelhos do PR rodados na base (sem ajuste)
roda base_est_cenario $BA est_cenario_test.py
roda base_est_sem_validade_nav $BA est_sem_validade_nav.py
roda base_esttest $BA esttest.py
roda base_est_fix1 $BA est_fix1_test.py
roda base_verif_ce_est $BA verif_ce_est.py
roda base_map_aprov $BA map_aprov_test.py
roda base_map_decisoes $BA map_decisoes_test.py
# B · ben_fluxo: modos que o timeout de 900 s não alcançou, um por vez
for m in cadeia390 conferencia conferencia390 sobra sobra390 multilote multilote390 rodape manutencao; do roda pr_ben_$m $PR ben_fluxo_test.py $m; done
# A · config_test por parte
for p in cf01 cf04 cf03 cf05 rev rev2 m390; do roda pr_config_$p $PR config_test.py $p; done
# demanda_estado (longo): ajustado no PR e na base, e o original na base
roda pr_demanda_estado_ajuste $PR $O/demanda_estado_nav_test_ajuste.py
roda base_demanda_estado $BA demanda_estado_nav_test.py
roda base_demanda_estado_ajuste $BA $O/demanda_estado_nav_test_ajuste.py
echo FIM >> $R
