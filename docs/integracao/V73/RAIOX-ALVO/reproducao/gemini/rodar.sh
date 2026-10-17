#!/usr/bin/env bash
# Verificações da revisão da consolidação Gemini (bff2e0e) e do contrato RX-0 proposto, sem navegador.
#   1) q2_ht.mjs: aritmética do Henderson-Tilton nos casos de zero, notação e identidade com o contraste de logs, só para valores positivos (Δ 17/10-6; não usa o v3);
#   2) v3_verificacoes.mjs: rxHT do v3 nos mesmos casos, fatos do gerador e contraprova do N5 (original + 20 réplicas);
#   3) comparação com os brutos versionados nesta pasta (só o campo "node" pode diferir).
#   Δ 17/10: 4) delta_1710.mjs: ramos do ADV-01, cruzamentos do ORA-05 e domínio do K10 (não usa o v3).
# Uso: git show 529adf7:docs/integracao/V73/pedidos-1610/raiox-pragas-no-tempo-v3.html > /tmp/v3.html
#      bash rodar.sh /tmp/v3.html <pasta de saída>
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"; HTML="$1"; OUT="$2"; mkdir -p "$OUT"
ESPERADO=e7872cb02fc667330354560a6b88b82cd5485ab656b2d7546b2500d645805e5e
SHA="$(sha256sum "$HTML" | cut -d' ' -f1)"; [ "$SHA" = "$ESPERADO" ] || { echo "SHA-256 do HTML diferente do v3 versionado: $SHA" >&2; exit 1; }
echo "node $(node --version) · v3 sha256 $SHA"
node "$AQUI/q2_ht.mjs" > "$OUT/q2_ht.txt"
node "$AQUI/delta_1710.mjs" > "$OUT/delta_1710.txt"
node "$AQUI/v3_verificacoes.mjs" "$HTML" "$OUT/v3_verificacoes.json"
node "$AQUI/resumo.mjs" "$OUT/v3_verificacoes.json" > "$OUT/v3_verificacoes.txt"
cmp -s "$OUT/q2_ht.txt" "$AQUI/q2_ht.txt" && echo "  q2_ht.txt: igual ao versionado" || { echo "  q2_ht.txt: DIFERE do versionado"; exit 1; }
cmp -s "$OUT/delta_1710.txt" "$AQUI/delta_1710.txt" && echo "  delta_1710.txt: igual ao versionado" || { echo "  delta_1710.txt: DIFERE do versionado"; exit 1; }
node -e 'const f=require("fs"),a=JSON.parse(f.readFileSync(process.argv[1])),b=JSON.parse(f.readFileSync(process.argv[2]));delete a.node;delete b.node;a.artefato.arquivo=b.artefato.arquivo;
  if(JSON.stringify(a)!==JSON.stringify(b)){console.log("  v3_verificacoes.json: DIFERE do versionado");process.exit(1)} console.log("  v3_verificacoes.json: igual ao versionado (fora node e nome do arquivo)")' "$OUT/v3_verificacoes.json" "$AQUI/v3_verificacoes.json"
