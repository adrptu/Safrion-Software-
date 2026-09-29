#!/usr/bin/env bash
# Atualiza o ruleset existente da main (PUT no mesmo id) a partir de protecao-main.json. Nunca cria outro ruleset.
# Uso: tools/github/configurar_protecao.sh dono/repositorio [--aplicar]
#   Sem --aplicar (padrão): lê o ruleset atual, valida o arquivo contra ele e contra os jobs reais dos workflows
#   e mostra a diferença. Não altera nada.
#   --aplicar: depois da mesma validação, grava por PUT e confere a leitura de volta; qualquer diferença sai com erro.
# O arquivo só acrescenta os checks obrigatórios (app GitHub Actions, strict); nome, alvo, bypass e as demais
# regras precisam ser iguais aos do ruleset atual. Renomear um job exige mudar o arquivo na mesma mudança:
# tools/ci/test_protecao_main.py falha na CI enquanto nomes e jobs divergirem.
# Requer gh autenticado com permissão de administração. O GitHub pode pedir Confirm access ao dono; não contornar.
# Não imprime credenciais.
set -euo pipefail
REPO="${1:?informe dono/repositorio}"
MODO="${2:-}"
case "$MODO" in "" | --aplicar) ;; *) echo "opção desconhecida: $MODO" >&2; exit 2 ;; esac
DIR="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$DIR/../.." && pwd)"
PAYLOAD="$DIR/protecao-main.json"
command -v gh >/dev/null || { echo "gh não encontrado; nada foi alterado." >&2; exit 2; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

gh api "repos/$REPO/rulesets" >"$TMP/lista.json"
ID="$(python3 "$DIR/protecao.py" escolher-id --lista "$TMP/lista.json" --payload "$PAYLOAD")"
gh api "repos/$REPO/rulesets/$ID" >"$TMP/atual.json"
python3 "$DIR/protecao.py" verificar --payload "$PAYLOAD" --atual "$TMP/atual.json" --raiz "$RAIZ"
if [ "$MODO" != --aplicar ]; then
  echo "Simulação: ruleset $ID não foi alterado. Use --aplicar para gravar."
  exit 0
fi
gh api --method PUT -H "Accept: application/vnd.github+json" "repos/$REPO/rulesets/$ID" --input "$PAYLOAD" >/dev/null
gh api "repos/$REPO/rulesets/$ID" >"$TMP/retorno.json"
python3 "$DIR/protecao.py" conferir-retorno --payload "$PAYLOAD" --atual "$TMP/retorno.json"
echo "Ruleset $ID atualizado e conferido."
