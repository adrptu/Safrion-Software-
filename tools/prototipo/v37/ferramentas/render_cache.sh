#!/bin/bash
# render_cache.sh <commit> [gen37]
# Monta o protótipo de um commit UMA vez (build.py + montar_render.py) e guarda project/ e _render/ no cache; imprime o caminho
# do _render guardado. Chamadas seguintes com a mesma chave só conferem o artefato e imprimem o caminho.
# - Chave (AGENTS.md §3.6): <sha completo>-<SAFRION_DADOS>-<versão do gerador>. O sha é de um commit (árvore limpa por
#   definição: a montagem é numa worktree destacada desse commit, nunca na pasta de trabalho). A versão do gerador junta o que
#   muda a saída e não está no commit: o Python que roda o build e a receita desta montagem (RECEITA abaixo; mude-a quando mudar
#   o modo de montar). O build só usa a biblioteca padrão do Python. Dados: só "sintetico" (ENG-017; dados reais nunca).
# - Artefato imutável: depois de montado, grava MANIFESTO.sha256 (todos os arquivos de project/ e _render/) e tira a escrita.
#   Toda chamada confere o manifesto; artefato alterado é recusado (apague a pasta da chave para remontar).
# - flock por chave: duas chamadas ao mesmo tempo não montam duas vezes (a segunda espera e reaproveita).
# - Build que sai com erro ou com "FALHA" no log não entra no cache (sai 1 e mostra o log).
# - Com [gen37], copia project/ e _render/ do cache para essa pasta (substitui os que houver; a cópia é gravável), para rodar os
#   testes dela. Cada execução de teste continua com perfil novo do Chrome (cdp.py e comp_lib.py criam um a cada navegador).
# Cache: $SAFRION_RENDER_CACHE; sem ela, a pasta render-cache do rascunho desta sessão (se existir) ou ${TMPDIR:-/tmp}/safrion-render-cache.
set -euo pipefail
RECEITA=2   # 1: chave só pelo sha (até 13/10/2026); 2: chave com dados e gerador, manifesto e artefato só leitura
[ $# -ge 1 ] || { echo "uso: $0 <commit> [gen37]" >&2; exit 2; }
AQUI=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(git -C "$AQUI" rev-parse --show-toplevel)
SHA=$(git -C "$REPO" rev-parse --verify --quiet "$1^{commit}") || { echo "commit desconhecido: $1" >&2; exit 2; }
DADOS=${SAFRION_DADOS:-sintetico}
[ "$DADOS" = sintetico ] || { echo "render_cache.sh monta só com SAFRION_DADOS=sintetico (recebeu: $DADOS)" >&2; exit 2; }
PY=$(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')
GERADOR="py$PY-r$RECEITA"
PADRAO=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/render-cache
[ -d "$(dirname "$PADRAO")" ] || PADRAO="${TMPDIR:-/tmp}/safrion-render-cache"
C="${SAFRION_RENDER_CACHE:-$PADRAO}"; mkdir -p "$C"
CHAVE="$SHA-$DADOS-$GERADOR"; D="$C/$CHAVE"
pronto() { [ -f "$D/OK" ] && [ -f "$D/MANIFESTO.sha256" ] && [ -d "$D/_render" ] && [ -d "$D/project" ]; }

if ! pronto; then
  exec 9>"$C/$CHAVE.lock"; flock 9
  if ! pronto; then
    if [ -e "$D" ]; then chmod -R u+w "$D"; rm -rf "$D"; fi
    mkdir -p "$D"; WT="$D/wt"
    limpa() { git -C "$REPO" worktree remove --force "$WT" >/dev/null 2>&1 || rm -rf "$WT"; git -C "$REPO" worktree prune >/dev/null 2>&1 || true; }
    trap limpa EXIT
    git -C "$REPO" worktree add --detach --quiet "$WT" "$SHA" >&2
    G="$WT/tools/prototipo/v37/gen37"; t0=$(date +%s)
    ( cd "$G" && env SAFRION_DADOS="$DADOS" python3 build.py ) > "$D/build.log" 2>&1 \
      || { echo "build falhou em $SHA (log: $D/build.log)" >&2; tail -5 "$D/build.log" >&2; exit 1; }
    nf=$(grep -c FALHA "$D/build.log" || true)
    [ "$nf" = 0 ] || { echo "build com $nf FALHA em $SHA (log: $D/build.log)" >&2; exit 1; }
    ( cd "$G" && env SAFRION_DADOS="$DADOS" python3 montar_render.py ) > "$D/render.log" 2>&1 \
      || { echo "montar_render falhou em $SHA (log: $D/render.log)" >&2; tail -5 "$D/render.log" >&2; exit 1; }
    mv "$G/project" "$D/project"; mv "$G/_render" "$D/_render"
    limpa; trap - EXIT
    ( cd "$D" && find project _render -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum ) > "$D/MANIFESTO.sha256"
    printf 'commit %s\ndados %s\ngerador %s\nmontado %s em %ss\npaginas %s\n' "$SHA" "$DADOS" "$GERADOR" "$(date -Iseconds)" \
      "$(( $(date +%s) - t0 ))" "$(ls "$D/_render" | grep -c '\.dc\.html$')" > "$D/OK"
    chmod -R a-w "$D"
  fi
  flock -u 9
fi

# artefato imutável: confere o manifesto (e que nada entrou ou saiu) antes de entregar
( cd "$D" && sha256sum --quiet --strict -c MANIFESTO.sha256 >&2 \
  && [ "$(find project _render -type f | wc -l)" = "$(wc -l < MANIFESTO.sha256)" ] ) \
  || { echo "artefato do cache alterado: $D (apague a pasta para remontar)" >&2; exit 1; }

if [ $# -ge 2 ]; then
  DEST=$(cd "$2" && pwd)
  [ -f "$DEST/build.py" ] || { echo "$DEST não é a pasta gen37 (sem build.py)" >&2; exit 2; }
  rm -rf "$DEST/_render" "$DEST/project"; cp -R --no-preserve=mode,ownership "$D/_render" "$D/project" "$DEST/"
fi
echo "$D/_render"
