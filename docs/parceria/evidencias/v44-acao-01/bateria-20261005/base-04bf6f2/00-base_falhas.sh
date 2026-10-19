# roda na base sem AÇÃO (sp-camada-sintetica, 04bf6f2) só os passos que falharam na AÇÃO, com o mesmo comando do log
G=/home/user/sp-camada-sintetica/tools/prototipo/v37/gen37; E=/tmp/base2; mkdir -p $E; cd $G || exit 1; mkdir -p _probe _probe/manut
export CHROME_BIN=/tmp/cloudchrome/chrome
git -C $G rev-parse --short HEAD > $E/commit.txt; date -u +%FT%TZ > $E/inicio.txt
for n in $(cat /tmp/falhas_acao2.txt); do
  cmd=$(head -1 /tmp/acao2/$n.log | sed 's/^\$ //'); case "$cmd" in *acoes_duplicadas*) cmd=$(echo "$cmd" | sed "s#/tmp/acao2#$E#");; esac
  echo "\$ $cmd" > $E/$n.log; ( eval "$cmd" ) >> $E/$n.log 2>&1; x=$?; echo "[exit $x]" >> $E/$n.log
  printf "%-40s base exit=%s  %s\n" $n $x "$(grep -E 'RESULTADO|ok ·|FALHAS' $E/$n.log | tail -1 | cut -c1-100)"
done; date -u +%FT%TZ > $E/fim.txt
