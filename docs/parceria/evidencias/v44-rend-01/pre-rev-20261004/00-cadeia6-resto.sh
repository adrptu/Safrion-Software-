# restante da cadeia da REND em 6afb511 (a execução de 00-cadeia6.sh foi cortada pelo limite de 30 min do executor em segundo plano enquanto
# lagoa/os_v39_bloq_test.py aguardava a trava do navegador, sem rodar); mesmos comandos, mesma worktree e mesmo commit
cd /home/user/sp-camada-sintetica/tools/prototipo/v37/gen37 || exit 1
export CHROME_BIN=/tmp/cloudchrome/chrome
E=${E:-/tmp/evid9}; echo "corte: $(date -u +%FT%TZ) · retomada dos passos restantes" > $E/retomada.txt
run(){ n=$1; shift; echo "\$ $*" > $E/$n.log; ( eval "$*" ) >> $E/$n.log 2>&1; x=$?; echo "[exit $x]" >> $E/$n.log; printf "%-40s exit=%s  %s\n" $n $x "$(grep -E 'RESULTADO|ok ·|artboards|_render montado|TOTAL' $E/$n.log | tail -1 | cut -c1-140)"; }
L='flock /tmp/cdp9333.lock'
git -C /home/user/sp-camada-sintetica rev-parse --short HEAD >> $E/retomada.txt; git -C /home/user/sp-camada-sintetica status --short | grep -v '^??' >> $E/retomada.txt
for t in os_v39_bloq_test.py os_v39_selo_agua_test.py map_decisoes_test.py map_irrig_filtro_test.py; do run lagoa/$t "CDP_GL=1 timeout 900 $L python3 $t"; done
date -u +%FT%TZ > $E/fim.txt
