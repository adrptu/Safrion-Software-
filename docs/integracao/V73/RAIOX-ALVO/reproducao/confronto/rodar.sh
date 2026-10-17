#!/usr/bin/env bash
# Reproduz tudo do Raio-X do alvo, sem navegador, e confere com os brutos versionados:
#   1) a reprodução da crítica do Claude (../rodar.sh: original, 20 réplicas, nulo do clima, época);
#   2) as provas próprias do confronto (confronto.mjs → confronto.json, resumo.mjs → confronto.txt);
#   3) se o commit do Codex estiver no clone, os 3 harness dele (b291746), conferidos com os brutos dele;
#   4) a comparação de 1 e 2 com os arquivos versionados (conferir.mjs).
# Uso: git show 529adf7:docs/integracao/V73/pedidos-1610/raiox-pragas-no-tempo-v3.html > /tmp/v3.html
#      git fetch origin codex/raiox-avaliacao-20261017   # opcional, para o passo 3
#      bash rodar.sh /tmp/v3.html <pasta de saída>
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
HTML="$1"; OUT="$2"; mkdir -p "$OUT/critica" "$OUT/confronto" "$OUT/codex"
ESPERADO=e7872cb02fc667330354560a6b88b82cd5485ab656b2d7546b2500d645805e5e
SHA="$(sha256sum "$HTML" | cut -d' ' -f1)"
[ "$SHA" = "$ESPERADO" ] || { echo "SHA-256 do HTML diferente do v3 versionado: $SHA" >&2; exit 1; }
echo "node $(node --version) · v3 sha256 $SHA"
ORIGEM="docs/integracao/V73/pedidos-1610/raiox-pragas-no-tempo-v3.html @ 529adf7 (claude/v44-v73-pedidos-1610)"
NOTA="conteúdo igual ao do artefato publicado 00b5d915…ed72e (versão 1792193012-4fc4), salvo o invólucro de publicação"
echo "== 1. crítica"; bash "$AQUI/../rodar.sh" "$HTML" "$OUT/critica" "$ORIGEM" "$NOTA"
echo "== 2. confronto"; node "$AQUI/confronto.mjs" "$HTML" "$OUT/confronto/confronto.json"
node "$AQUI/resumo.mjs" "$OUT/confronto/confronto.json" > "$OUT/confronto/confronto.txt"
echo "== 3. harness do Codex (b291746)"
RAIZ="$(git -C "$AQUI" rev-parse --show-toplevel)"; C=b291746d27596f53d34e387c49fc1212ebcb3d9c; P=docs/integracao/V73/RAIOX/codex
if git -C "$RAIZ" cat-file -e "$C:$P/raiox-core.cjs" 2>/dev/null; then
  for f in raiox-core:raiox-core-result raiox-ht-futuro:raiox-ht-futuro raiox-forecast-futuro:raiox-forecast-futuro; do
    s="${f%%:*}"; e="${f##*:}"; git -C "$RAIZ" show "$C:$P/$s.cjs" > "$OUT/codex/$s.cjs"; git -C "$RAIZ" show "$C:$P/$e.json" > "$OUT/codex/$e.esperado.json"
    node "$OUT/codex/$s.cjs" > "$OUT/codex/$s.saida.json"
    node -e 'const f=require("fs"),a=JSON.parse(f.readFileSync(process.argv[1])),b=JSON.parse(f.readFileSync(process.argv[2]));console.log("  "+process.argv[3]+": "+(JSON.stringify(a)===JSON.stringify(b)?"igual ao bruto do Codex":"DIFERE do bruto do Codex"))' "$OUT/codex/$s.saida.json" "$OUT/codex/$e.esperado.json" "$s"
  done
else echo "  commit $C ausente neste clone: rode 'git fetch origin codex/raiox-avaliacao-20261017' para incluir este passo"; fi
echo "== 4. conferência com os brutos versionados"; node "$AQUI/conferir.mjs" "$AQUI/.." "$OUT"
