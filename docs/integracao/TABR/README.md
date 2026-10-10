# Pacote de revisão da frente TABR (TABELAS-FOCO de Cadastros e Irrigação)

Atende o pedido do Codex BEN-REV-20261010-04 (comentário 6092086431 no PR #47): pacote mínimo com fonte, base, diff, brutos e lentes, com os 43/142/94/140 relatados e os vermelhos equivalentes à base. É fonte recuperável para a revisão isolada. Nada aqui é código integrado.

- **Candidata:** `8f19e0d6bd27e2aaa5805d1f628459190db4e919` ("TABR: correções da revisão", 10/10 01:15 UTC), branch local `claude/v44-tabelas-r`, worktree `<sp-tabr>`.
- **Base:** `cdc185f551a9513d72734b18e4a869f921917c00`, o merge-base com `claude/prototipo-v44`. **Está no origin** (`origin/claude/prototipo-v44` contém `cdc185f`).
  - A frente nasceu em `24da80b`, que também está no origin.
  - Recebeu a branch única por dois merges: `def9dc8` (ecc8b00) e `300835d` (cdc185f).
- **Estado da worktree ao montar o pacote:**
  - não há commit depois de `8f19e0d` na `claude/v44-tabelas-r`;
  - não há alteração rastreada nem stash;
  - só há arquivos não versionados: as saídas de build e de teste (`_render/`, `project/`, `_probe/`, `__pycache__/`) e a pasta `tools/prototipo/v37/validacao/` (de 06/10), que fica fora do pacote. Nada foi tocado.

## Conteúdo
- **`commits.txt`:** os 20 commits de `cdc185f..8f19e0d`, entre eles os 2 merges.
- **`arquivos.txt`:** os arquivos efetivamente alterados, em três partes:
  - o efeito líquido, 34 arquivos;
  - commit a commit, com autor, data e pais. Nos merges, só aparece o que o merge mudou em relação a todos os pais;
  - os autores: os 20 commits são de `Claude <noreply@anthropic.com>`.
- **`diff-cdc185f-8f19e0d.patch` e `diffstat.txt`:** o diff inteiro, com 34 arquivos (+1597 −328).
- **Sem `patches/`:** como a faixa tem merges, o bundle faz esse papel.
- **`tabr.bundle` (108 KB):**
  - foi criado pelo nome da branch: `git bundle create tabr.bundle cdc185f..claude/v44-tabelas-r`;
  - o único ref é `refs/heads/claude/v44-tabelas-r`, conferido em `8f19e0d6bd27…`;
  - pré-requisitos: `24da80b`, `ecc8b00` e `cdc185f`, todos no origin.
- **`relatos.md`:**
  - os números 43/142/94/140 com a fonte de cada um;
  - a tabela de vermelhos equivalentes à base;
  - a revisão A1–A11 (3 S3 e 8 S4) com correção e regressão, os mutantes e as recusas com motivo;
  - os relatos completos de implementação, revisão e correção.
- **`brutos/`:** 344 saídas já executadas, descritas abaixo. Nada foi reexecutado.
- **`verificacao-pacote.txt`:** saída das verificações deste pacote.

A revisão que consta aqui foi feita por um agente Claude separado ("papel Codex"). **O parecer do Codex é o BEN-REV-20261010-04.**

## Como reproduzir

Pelo diff, sobre `cdc185f`:
```
git checkout --detach cdc185f
git apply docs/integracao/TABR/diff-cdc185f-8f19e0d.patch
```

Pelo bundle, que traz a história com os merges:
```
git bundle verify docs/integracao/TABR/tabr.bundle
git fetch docs/integracao/TABR/tabr.bundle 8f19e0d6bd27e2aaa5805d1f628459190db4e919
git checkout --detach FETCH_HEAD
# alternativa: git fetch docs/integracao/TABR/tabr.bundle claude/v44-tabelas-r:refs/heads/tabr
```

Com o sha curto, `git fetch tabr.bundle 8f19e0d` falha com "couldn't find remote ref". Use o sha completo ou o nome do ref.

## Verificação do pacote (executada em 10/10 às 01:19 UTC)
- **Diff, numa worktree temporária em `cdc185f`** (criada com `git -C <sp-proto> worktree add --detach` e removida no fim):
  - `git apply --check` deu rc 0;
  - depois de aplicado, os 34 caminhos ficaram iguais, byte a byte, aos de `8f19e0d`;
  - revertido, a worktree voltou limpa.
- **Bundle:** `git bundle verify` deu ok.
  - Num repositório novo, só com a história até `cdc185f`, o `git fetch` pelo sha completo e pelo nome do ref trouxe `8f19e0d`.
  - `fsck --connectivity-only` deu rc 0, e o diff deu os mesmos 34 arquivos.
  - O teste também registra a falha do sha curto.
- **Gitleaks 8.30.1** (o binário conferido da CI), com `gitleaks dir --config <repo>/.gitleaks.toml --redact` sobre esta pasta: **nenhum achado**.
  - O diff tem três linhas com o nome da chave de localStorage `talhao-os-irrigacao-v1` (em `irr_fluxo_test.py`), e a regra não as acusou.
  - Por isso o diff texto fica inteiro e continua aplicável com `git apply`.
  - O bundle é binário e não é varrido como texto; ele contém o mesmo conteúdo do diff.

## Brutos

Os caminhos da máquina foram trocados por `<scratchpad>`, `<sp-tabr>`, `<chrome>`, `<sessao>` e `<sessao-tmp>`. Os dados são sintéticos. O prefixo de cada arquivo diz a origem; o resto é o nome original.

| Prefixo | Origem | Código |
|---|---|---|
| `base-24da80b_` | bateria da base da frente (`/tmp/TABR-base/`, 06/10) | `24da80b` |
| `base_` | testes novos e antigos rodados na base: `TABR-base-*` (06/10 e 09/10) | `24da80b` |
| `base-cdc185f_`, `base-ecc8b00_` | vermelhos e build rodados nas bases das junções (09/10) | `cdc185f`, `ecc8b00` |
| `impl06-cur_`, `impl06_` | implementação de 06/10 (`/tmp/TABR-cur/`, `TABR-fix-*`) | antes das junções |
| `impl09_` | implementação de 09/10, 11:21–13:33: vermelhos antes das correções do IR e testes antigos | `37577a6`..`ecc8fce` |
| `fim-3636e33_` | bateria final da implementação (`/tmp/TABR-fim/`, 09/10 13:41–16:03) | `3636e33` |
| `rev_` | revisão adversarial: `probe_geral.log`, `probe2.log`, `mut_cad.log`, `mut_irr.log`, `regress*.log` e a transcrição das sondas (largura, A1–A11, mutantes) | `3636e33` × `24da80b` |
| `corr1_` | 1ª tentativa de correção, interrompida (17:40–19:22): unidade antes e depois e lotes | árvore em edição |
| `corr2-rv_`, `corr2_` | 2ª tentativa, interrompida (21:19–22:53): `/tmp/TABR-rv/` e mutantes M-a, M-i, M-k e M-m pegos (transcrição) | árvore em edição |
| `corr-fx_`, `corr_` | correção que fez o commit: `/tmp/TABR-fx/` (09/10 22:58 a 10/10 01:15), build, unidade 43/43 e render finais, transcrição (mutante M-e, finais) | árvore que virou `8f19e0d` |

Os `*transcricao*.txt` são saídas copiadas do transcript do agente, para comandos que não gravaram arquivo. Em `corr_TABR-transcricao_testes.txt` há também trechos de leitura do código dos testes.

O rótulo "dados reais locais: 5/5" que o `montar_render.py` imprime é enganoso, como apontou a V3-3 da SAF-C02: a worktree usa a camada sintética.

**Não incluídos:**
- os scripts de sonda e de mutação, porque o pacote leva só saídas;
- as cópias `snap/project` de `/tmp/TABR-fx/`;
- as listas `TABR-ours.txt` e `TABR-theirs.txt` (arquivos de uma junção);
- o JSON do `acoes_duplicadas`.

## Para a integração (fila do integrador)
- **Conflito provável:**
  - com a DS em `engine.py` e `g2lib.js`;
  - com a CTL-5 em irrigação e outorga;
  - com a SOLO em irrigação.
- **A1, o antigo S3:** a 1440 px, Situação, Pendência e Próximo passo ficam visíveis sem rolar nas grades IR-01..04 e CD-03..07. O teste não pode ser afrouxado.
