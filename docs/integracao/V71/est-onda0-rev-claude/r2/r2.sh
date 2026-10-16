#!/bin/bash
# Reconferência R2 do PR #81 (HEAD 50af2ae): navegador só depois do FIM da bateria do coordenador; um Chrome por vez.
R2=/tmp/claude-0/pr81/docs/integracao/V71/est-onda0-rev-claude/r2; C=/tmp/claude-0/pr81b/tools/prototipo/v37/gen37; BA=/tmp/claude-0/pr81base/tools/prototipo/v37/gen37
REV=/tmp/claude-0/pr81/docs/integracao/V71/est-onda0-rev-claude/est_onda0_rev_test.py; S=$R2/_resumo.txt
until grep -q FIM /tmp/claude-0/q27.out 2>/dev/null; do sleep 20; done
echo "início $(date -u +%H:%M:%S) (q27 com FIM)" >> $S
roda(){ rot="$1"; lim="$2"; dir="$3"; shift 3; ini=$(date +%s)
  ( cd "$dir" && timeout "$lim" env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico GEN="$dir" "$@" ) > "$R2/$rot.log" 2>&1; rc=$?
  res=$(grep -a "RESULTADO" "$R2/$rot.log" | tail -n 1); [ -z "$res" ] && res="(sem RESULTADO) $(tail -n 1 "$R2/$rot.log" | cut -c1-200)"
  echo "$rot | rc=$rc | $(( $(date +%s)-ini ))s | $res" | tee -a $S; }
roda cand_rev 900 $C env ROTULO=cand LEGADO_DIR=$BA/_render python3 -B $REV $C
roda base_rev 900 $BA env ROTULO=base RENDER_DIR=$BA/_render python3 -B $REV $BA
for t in est_cenario_test.py esttest.py est_sem_validade_nav.py map_decisoes_test.py; do roda cand_${t%.py} 900 $C python3 -B $t; done
roda cand_demanda_estado_nav_test 1200 $C python3 -B demanda_estado_nav_test.py
for m in fluxo lotes cadeia cadeia390 conferencia conferencia390 sobra sobra390; do roda cand_ben_$m 900 $C python3 -B ben_fluxo_test.py $m; done
for t in est_a4_test.py consumo_divergente_test.py os_cenario_test.py paginas_scan_test.py; do roda cand_${t%.py} 900 $C python3 -B $t; done
echo FIM >> $S
