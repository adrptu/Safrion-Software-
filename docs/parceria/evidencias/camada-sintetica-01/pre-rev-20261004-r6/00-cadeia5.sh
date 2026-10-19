# cadeia completa na worktree da branch claude/camada-sintetica-01 (PRE-REV-20261004); navegador serializado pela trava da porta 9333
cd /home/user/sp-fix/tools/prototipo/v37/gen37 || exit 1
export CHROME_BIN=/tmp/cloudchrome/chrome
E=${E:-/tmp/evid7}; rm -rf $E; mkdir -p $E/capturas $E/lagoa; rm -rf project _render; date -u +%FT%TZ > $E/inicio.txt
run(){ n=$1; shift; echo "\$ $*" > $E/$n.log; ( eval "$*" ) >> $E/$n.log 2>&1; x=$?; echo "[exit $x]" >> $E/$n.log; printf "%-40s exit=%s  %s\n" $n $x "$(grep -E 'RESULTADO|ok ·|artboards|_render montado|TOTAL' $E/$n.log | tail -1 | cut -c1-140)"; }
L='flock /tmp/cdp9333.lock'
mkdir -p _probe   # pasta não rastreada que alguns testes usam (a worktree nova não tem)
run 01-build 'python3 build.py'
run 02-montar_render 'python3 montar_render.py'
run 03-camada_test 'python3 dados_lagoa_sintetico/camada_test.py'
run 04-talgeo_test 'node talgeo_test.js'
run 05-talmapa_test "CDP_GL=1 $L python3 talmapa_test.py $E/capturas"
run 06-varredura "$L python3 varredura.py"
run 07-decimais-crus 'python3 /tmp/decimais.py'
run 08-quantidade_test 'python3 quantidade_test.py'
for t in mip_unit_test.py carencia_test.py mip_correcoes_test.py mip_fluxo_test.py irr_estado_test.py irr_fluxo_test.py os_v39_liberar_test.py os_v39_bloq_test.py os_v39_selo_agua_test.py map_decisoes_test.py map_irrig_filtro_test.py; do run lagoa/$t "CDP_GL=1 timeout 900 $L python3 $t"; done
date -u +%FT%TZ > $E/fim.txt
