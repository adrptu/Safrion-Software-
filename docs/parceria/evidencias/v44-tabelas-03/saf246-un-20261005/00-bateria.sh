# bateria completa na sp-tab (gen37), TABELAS-FOCO incremento 2b (unidade junto do valor); logs em /tmp/tab5/<passo>.log
G=/home/user/sp-tab3/tools/prototipo/v37/gen37; E=${E:-/tmp/tab11}
cd "$G" || exit 1
mkdir -p $E _probe _probe/manut
[ -f $E/inicio.txt ] || { date -u +%FT%TZ > $E/inicio.txt; git -C "$G" rev-parse --short HEAD > $E/commit.txt; git -C "$G" status --short | grep -v '^??' > $E/sujos.txt; }
run(){ n=$1; shift; if [ -f $E/$n.log ] && grep -q '^\[exit ' $E/$n.log; then return; fi; echo "\$ $*" > $E/$n.log; ( eval "$*" ) >> $E/$n.log 2>&1; x=$?; echo "[exit $x]" >> $E/$n.log; printf "%-44s exit=%s  %s\n" $n $x "$(grep -E 'RESULTADO|ok ·|FALHAS|artboards|_render montado|TOTAL|OK$|verificações' $E/$n.log | tail -1 | cut -c1-120)"; }
L='CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdp9333.lock'
run 00-build 'python3 build.py'
run 00-montar 'python3 montar_render.py'
run 01-varredura "$L python3 varredura.py"
run 02-duplicadas "$L python3 ../ferramentas/acoes_duplicadas.py . $E/duplicadas.json"
for m in saf familias responsivo gemini v3; do run 03-acao_$m "$L timeout 1200 python3 acao_unica_test.py $m"; done
for m in matriz rotacao interacao ajustes ajustes2; do run 04-componentes_$m "$L timeout 900 python3 componentes_test.py $m"; done
for m in celular complemento desktop; do run 04-etapas_$m "$L timeout 900 python3 etapas_celular_test.py $m"; done
for m in fluxo telas bordas bordas2; do run 04-rend_$m "$L timeout 900 python3 rend_multiconjuntos_test.py $m"; done
for t in $(ls *test*.py | grep -v -E '^(acao_unica_test|componentes_test|etapas_celular_test|rend_multiconjuntos_test|cadc_test)\.py$'); do run 05-$t "$L env CDP_GL=1 timeout 900 python3 $t"; done
run 06-rend_unit "python3 rend_multiconjuntos_unit.py"
run 06-camada "python3 dados_lagoa_sintetico/camada_test.py"
run 06-talgeo "node talgeo_test.js"
run 06-decimais "python3 /tmp/decimais.py"
date -u +%FT%TZ > $E/fim.txt
