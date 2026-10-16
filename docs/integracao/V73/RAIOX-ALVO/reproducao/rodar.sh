#!/usr/bin/env bash
# Reproduz, sem navegador, os números do protótipo "Raio-X do alvo" (artefato v3) e as contraprovas da crítica do Claude.
# Uso: bash rodar.sh <HTML do artefato v3> <pasta de saída>
# O HTML do artefato é privado e não é versionado. SHA-256 conferido nesta crítica:
#   00b5d915221eda4c789ec8f7ee8eeb6e526086815de136ace62e023ef10ed72e (151.928 bytes, versão 1792193012-4fc4)
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
HTML="$1"; OUT="$2"; mkdir -p "$OUT"
echo "sha256 do HTML: $(sha256sum "$HTML" | cut -d' ' -f1)"
node "$AQUI/raiox_repro.mjs" "$HTML" "$OUT/repro.json" > /dev/null
node "$AQUI/resumo.mjs" "$OUT/repro.json" > "$OUT/resumo.txt"
node "$AQUI/calor.mjs" "$OUT/repro.json" > "$OUT/calor.txt"
echo "ok: $OUT/repro.json, $OUT/resumo.txt, $OUT/calor.txt"
