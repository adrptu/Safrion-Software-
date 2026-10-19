# Pacote de revisão da frente COM (Comercial e logística: VEN, EXPED e PCOM)

Atende o pedido do Codex COM-REV-20261010-01 (comentário 6091755808 no PR #47). É fonte recuperável para a revisão isolada, antes da integração. Nada aqui é código integrado.

- **Candidata:** `29cdc6e82ebc67e7449800f45f7a674f764ffda0` ("COM: correções da revisão"), branch local `claude/v44-comercial`, worktree `<sp-com>`.
- **Base:** `9fb09a50851d6c897d8ea5eb234047994a86a429`, o merge-base com `claude/prototipo-v44` ("Integra SAF-C01 (ef0d7b2) na branch única…").
  - A frente nasceu em `f4121bd`.
  - Recebeu a branch única por dois merges: `f7d0fa6` (cdc185f, com resolução em `g2lib.js`) e `c7d48e9` (9fb09a5, sem conflito).
  - **A base não está no origin.** A cópia local do `origin/claude/prototipo-v44` aponta para `cdc185f`, e o `9fb09a5` só existe na branch local. O `com.bundle` traz a base junto (ver abaixo).
- **Estado da worktree ao montar o pacote:**
  - não há commit depois de `29cdc6e` na `claude/v44-comercial`;
  - não há alteração rastreada nem stash;
  - só há arquivos gerados e não versionados: `_render/`, `project/`, `_probe/` (60 itens) e `__pycache__/`. Não fazem parte do pacote, e nada foi tocado.

## Conteúdo
- **`commits.txt`:** os 16 commits de `9fb09a5..29cdc6e`, entre eles os 2 merges.
- **`arquivos.txt`:** os arquivos efetivamente alterados, em três partes:
  - o efeito líquido, 25 arquivos;
  - commit a commit, com autor, data e pais. Nos merges, só aparece o que o merge mudou em relação a todos os pais; no `f7d0fa6`, é só `g2lib.js`;
  - os autores: os 16 commits são de `Claude <noreply@anthropic.com>`.
- **`diff-9fb09a5-29cdc6e.patch` e `diffstat.txt`:** o diff inteiro, com 25 arquivos (+2617 −136). É a contribuição líquida da frente sobre a base.
- **Sem `patches/`:** como a faixa tem merges, um `git format-patch` não reproduz a história. O bundle faz esse papel.
- **`com.bundle` (220 KB):**
  - foi criado pelo nome da branch: `git bundle create com.bundle cdc185f..claude/v44-comercial`;
  - o único ref é `refs/heads/claude/v44-comercial`, conferido em `29cdc6e82ebc…`;
  - pré-requisitos: `ecc8b00`, `f4121bd` e `cdc185f`, todos no origin;
  - traz os 16 commits da frente, a base `9fb09a5` e o `ef0d7b2`.
- **`relatos.md`:**
  - os quatro S2 com achado → correção no commit → teste que prova, rotulados "executado" ou "relatado";
  - a tabela A1–A12, os testes da correção e os pontos para o revisor;
  - os relatos completos de implementação, revisão e correção.
- **`brutos/`:** 85 saídas já executadas, descritas abaixo. Nada foi reexecutado.
- **`verificacao-pacote.txt`:** saída das verificações deste pacote.

A revisão que consta aqui foi feita por um agente Claude separado. **O parecer do Codex é o pedido COM-REV-20261010-01.**

## Como reproduzir

Pelo diff, num clone que tenha a base `9fb09a5`:
```
git checkout --detach 9fb09a5
git apply docs/integracao/COM/diff-9fb09a5-29cdc6e.patch
```

Pelo bundle, que funciona com o origin atual e traz também a base:
```
git bundle verify docs/integracao/COM/com.bundle
git fetch docs/integracao/COM/com.bundle 29cdc6e82ebc67e7449800f45f7a674f764ffda0
git checkout --detach FETCH_HEAD                 # candidata
git checkout --detach 9fb09a5                    # base, que veio junto
# alternativa: git fetch docs/integracao/COM/com.bundle claude/v44-comercial:refs/heads/com
```

Com o sha curto, `git fetch com.bundle 29cdc6e` falha com "couldn't find remote ref". Use o sha completo ou o nome do ref.

## Verificação do pacote (executada em 10/10 às 00:46 UTC)
- **Diff, numa worktree temporária em `9fb09a5`** (criada com `git -C <sp-proto> worktree add --detach` e removida no fim):
  - `git apply --check` deu rc 0;
  - depois de aplicado, os 25 caminhos ficaram iguais, byte a byte, aos de `29cdc6e`;
  - revertido, a worktree voltou limpa.
- **Bundle:** `git bundle verify` deu ok.
  - O teste foi num repositório novo, só com a história até `cdc185f`, no qual o `9fb09a5` não existia.
  - `git fetch` pelo sha completo e pelo nome do ref trouxe `29cdc6e`, e `fsck --connectivity-only` deu rc 0.
  - O `9fb09a5` passou a existir como ancestral, e `git diff --stat 9fb09a5 com` deu os mesmos 25 arquivos.
  - O teste também registra a falha do sha curto.

## Brutos

Os caminhos da máquina foram trocados por `<scratchpad>`, `<sp-com>`, `<chrome>` e `<sessao>`. Os dados são sintéticos (`SAFRION_DADOS=sintetico`). O prefixo de cada arquivo diz a fase; o resto é o nome original do log.

| Prefixo | Fase | Código |
|---|---|---|
| `base_` | Base da frente: 06/10 e o `.base-f4121bd` de 09/10 | `f4121bd` |
| `impl1_` | Implementação, 09/10, 11:13–13:05 (fluxo, duplo clique da reserva antes e depois) | `d738678`..`16b3974` |
| `impl2_` | Implementação, 09/10, 13:28–14:45 (bateria do A-17) | `3044c79`..`d7b91ff` |
| `impl3_` | Implementação retomada, 09/10, 16:43–17:43: bateria completa e `painel-antes` (vermelho do `bdc5ca8`) | `c7d48e9` e `bdc5ca8` |
| `rev_` | Revisão adversarial: sondas no node (p2–p11), duplo clique e tela via CDP, mutantes | `bdc5ca8` |
| `corr1_` | 1ª tentativa de correção, interrompida: testes novos, entre eles o vermelho no código da revisão | árvore em edição sobre `bdc5ca8` |
| `corr_` | Correção que fez o commit, 21:37–22:51 | `29cdc6e` (22:37). `dup`, `vetest` e `lotest` rodaram depois do commit |

Os `*transcricao*.txt` são saídas copiadas do transcript do agente, para comandos que não gravaram arquivo. O `rev_COM-dbl_test_header_saca_venda.log` é a saída gravada pelo comando do revisor que foi para segundo plano.

O rótulo "dados reais locais: 5/5" que o `montar_render.py` imprime (`base_COM-base-render.log`, `corr_COM-render.log`) é enganoso, como apontou a V3-3 da SAF-C02. A worktree não tem `dados_lagoa/` e usa a camada sintética.

**Não incluídos:** os scripts de sonda e de mutação (só as saídas entram no pacote), as capturas `.png` e as cópias de código do scratchpad.
