#!/bin/bash
# os 15 testes: antes (302b26f, wt-antes) e depois (sp-acel, esperas finais), um logo após o outro, na mesma trava (cdpA);
# a ordem alterna a cada teste (antes→depois, depois→antes) para dividir o ruído da máquina entre os dois lados
AN=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/wt-antes/tools/prototipo/v37/gen37; DE=/home/user/sp-acel/tools/prototipo/v37/gen37; O=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/14-medida
i=0
while IFS= read -r linha; do
  [ -z "$linha" ] && continue; i=$((i+1)); echo "$linha" > $O/um.txt
  if [ $((i % 2)) -eq 1 ]; then
    /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/bin/roda.sh $AN $O/antes $O/um.txt; /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/bin/roda.sh $DE $O/depois $O/um.txt
  else
    /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/bin/roda.sh $DE $O/depois $O/um.txt; /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/bin/roda.sh $AN $O/antes $O/um.txt
  fi
done < /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/bin/lista15.txt
echo FIM_MEDIDA
