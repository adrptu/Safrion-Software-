#!/usr/bin/env bash
# Aplica a proteção da main (ruleset) no repositório remoto. Execute só depois de:
# 1) o repositório existir no GitHub e a CI ter rodado ao menos uma vez (os nomes dos checks precisam existir);
# 2) a revisão do pacote pelo Codex (docs/parceria/rodadas/R-001).
# Uso: tools/github/configurar_protecao.sh adrptu/do-talhao-a-os
# Requer gh autenticado com permissão de administração no repositório. Não imprime credenciais.
set -euo pipefail
REPO="${1:?informe dono/repositorio}"
DIR="$(cd "$(dirname "$0")" && pwd)"
command -v gh >/dev/null || { echo "gh não encontrado; aplique o JSON pela interface do GitHub (Settings › Rules) ou por outro cliente autenticado."; exit 2; }
gh api --method POST -H "Accept: application/vnd.github+json" "repos/$REPO/rulesets" --input "$DIR/protecao-main.json" >/dev/null
echo "Ruleset aplicado. Conferindo:"
gh api "repos/$REPO/rulesets" --jq '.[] | "\(.id)  \(.name)  \(.enforcement)"'
# Revisões obrigatórias (required_approving_review_count) ficam em 0 até decidir as identidades de revisão no GitHub
# (docs/STATUS.md, bloqueio 2). Revisão independente continua exigida pelo processo e registrada em docs/parceria/rodadas/.
