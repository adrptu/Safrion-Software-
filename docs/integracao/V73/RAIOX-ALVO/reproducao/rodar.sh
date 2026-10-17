#!/usr/bin/env bash
# Reproduz, sem navegador, os números do protótipo "Raio-X do alvo" (v3) e as contraprovas da crítica do Claude.
# Fonte versionada: docs/integracao/V73/pedidos-1610/raiox-pragas-no-tempo-v3.html, commit 529adf7
#   (branch claude/v44-v73-pedidos-1610), SHA-256 e7872cb02fc667330354560a6b88b82cd5485ab656b2d7546b2500d645805e5e, 151.382 bytes.
#   Conteúdo igual ao do artefato publicado 00b5d915…ed72e, salvo o invólucro de publicação.
# Uso: git show 529adf7:docs/integracao/V73/pedidos-1610/raiox-pragas-no-tempo-v3.html > /tmp/v3.html
#      bash rodar.sh /tmp/v3.html <pasta de saída> [origem] [nota]
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
HTML="$1"; OUT="$2"; ORIGEM="${3:-$1}"; NOTA="${4:-}"; mkdir -p "$OUT"
echo "sha256 do HTML: $(sha256sum "$HTML" | cut -d' ' -f1)"
node "$AQUI/raiox_repro.mjs" "$HTML" "$OUT/repro.json" "$ORIGEM" "$NOTA" > /dev/null
node "$AQUI/resumo.mjs" "$OUT/repro.json" > "$OUT/resumo.txt"
node "$AQUI/calor.mjs" "$OUT/repro.json" > "$OUT/calor.txt"
echo "ok: $OUT/repro.json, $OUT/resumo.txt, $OUT/calor.txt"
