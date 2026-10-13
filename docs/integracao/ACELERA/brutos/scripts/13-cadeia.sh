#!/bin/bash
# espera a prova na versão com defeito; depois a bateria completa da V56 com as esperas finais (8bdf790) e os testes de unidade
while ! grep -q FIM_DEFEITO /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/11-defeito.out 2>/dev/null; do sleep 20; done
/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/bin/roda.sh /home/user/sp-acel/tools/prototipo/v37/gen37 /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/13-bateria/nav /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/13-bateria/lista_nav.txt
/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/bin/roda_unit.sh /home/user/sp-acel/tools/prototipo/v37/gen37 /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/13-bateria/unit /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/13-bateria/lista_unit.txt
echo FIM_BATERIA
