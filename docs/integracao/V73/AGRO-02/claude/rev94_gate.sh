#!/bin/bash
# portão do navegador: espera até haver no máximo 1 Chrome principal
n(){ ps -eo args | grep -E '/chrome-linux/chrome ' | grep -v -- '--type=' | grep -v grep | wc -l; }
until [ "$(n)" -le 1 ]; do sleep 5; done
echo "gate ok: $(n) chrome principal"
