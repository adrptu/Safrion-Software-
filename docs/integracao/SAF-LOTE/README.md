# Pacote de revisão do lote SAF (SAF-C01b e SAF-C02)

Fonte recuperável para a revisão isolada das duas candidatas do Planejar safra, antes da integração. Nada aqui é código integrado na branch única. Cada candidata tem a sua base e a sua subpasta.

| Candidata | Branch local (worktree) | Base (merge-base com `claude/prototipo-v44`) | Commits | Diff |
|---|---|---|---|---|
| **SAF-C01b**: 2ª entrega da SAF-C01 | `claude/v44-saf-c01` (`<sp-safc01>`) | `ef0d7b2`, a 1ª entrega, já integrada em `9fb09a5` | `d1b81f4` (correções da verificação), `64a3041` (saídas brutas) | 45 arquivos, +4398 −93 |
| **SAF-C02**: capacidade simétrica entre safras abertas | `claude/v44-saf-c02` (`<sp-safc02>`) | `16d6734` | `62b0904`, `f52fa09` (correções da verificação), `1671671` (saídas brutas) | 50 arquivos, +2018 −50 |

Nenhuma das duas faixas tem merge. Cada subpasta tem:
- `commits.txt`;
- `diff-<base>-<candidata>.patch` e `diffstat.txt`;
- `patches/`, com um `git format-patch` por commit;
- `relatos.md`: resumo dos achados, do fechamento e dos testes rotulados "executado" ou "relatado", e os relatos completos;
- `brutos/`: logs já executados fora do repositório.

Parte da evidência entra pelo próprio diff, nos commits de saídas brutas:
- `docs/planejar-safra/verificacao-saf-c01/correcoes/`, pelo `64a3041`;
- `docs/planejar-safra/verificacao-saf-c02/saidas/` e o `LEIA-ME.md` dela, pelo `1671671`.

As verificações registradas são de três lentes, cada uma um agente Claude separado do autor. **A revisão do Codex sobre as duas candidatas continua pendente.**

## Composição do lote (ainda não terminada)

O lote está em teste na worktree `<sp-intsaf>`, branch local `int/saf-lote`, HEAD `d6d33eb`. A história é:
- `2678481`: BEN pós-correção, onde o lote nasceu;
- `a8df160`: integra a SAF-C01b (`64a3041`);
- `d6d33eb`: integra a SAF-C02 (`1671671`).

Depois de `2678481`, a branch única recebeu as correções seguintes da integração do BEN, de `e24b22d` até `1440889` (BEN-REV-20261009-03), e mais documentos. Quando este pacote foi montado, ela estava em `64040f8`. O lote não contém nada disso. **A composição do lote com o BEN corrigido ainda vai acontecer.** As saídas da integração do lote não estão neste pacote porque o lote continua em teste.

Pontos de conflito:
- **`tools/prototipo/v37/gen37/safra.js`:** é o único arquivo que as duas candidatas alteram, além dos documentos do planejar-safra. Preserve as duas mudanças.
- **`areas/planejamento.py`:** a SAF-C02 troca os links "Ver capacidade" em linhas vizinhas às alteradas pela SUP e pelo PCM.

## Como reproduzir

SAF-C02, base `16d6734`, já no origin:
```
git checkout --detach 16d6734
git am docs/integracao/SAF-LOTE/C02/patches/*.patch     # ou: git apply docs/integracao/SAF-LOTE/C02/diff-16d6734-1671671.patch
```

SAF-C01b, base `ef0d7b2`:
```
git checkout --detach ef0d7b2
git am docs/integracao/SAF-LOTE/C01b/patches/*.patch    # ou: git apply docs/integracao/SAF-LOTE/C01b/diff-ef0d7b2-64a3041.patch
```

O `ef0d7b2` está na `claude/prototipo-v44` local, pelo merge `9fb09a5`. Na cópia local do `origin/claude/prototipo-v44`, porém, o ref ainda aponta para `cdc185f`, que não contém o `ef0d7b2`. Se a base não estiver disponível, use `C01b/c01b.bundle` (116 KB). Ele traz o `ef0d7b2` e os dois commits da candidata, com o ref `refs/heads/claude/v44-saf-c01` apontando para `64a3041`. O único pré-requisito é `ecc8b00`, que já está no origin.
```
git bundle verify docs/integracao/SAF-LOTE/C01b/c01b.bundle
git fetch docs/integracao/SAF-LOTE/C01b/c01b.bundle 64a30418d8e9a7eca8dd3d0884b51b608fad52d3
git checkout --detach FETCH_HEAD          # a base fica em FETCH_HEAD~2 (ef0d7b2)
```

## Verificação do pacote (executada em 09/10 às 23:57 UTC; saída em `verificacao-pacote.txt`)

Cada candidata foi verificada numa worktree temporária na sua base, removida no fim:
- `git apply --check` do diff deu rc 0;
- depois de aplicado, todos os caminhos ficaram iguais, byte a byte, aos da candidata (45 e 50 caminhos);
- revertido, a worktree voltou limpa;
- os patches, aplicados em sequência, deram a mesma árvore da candidata.

Os avisos "trailing whitespace" vêm de linhas de log dentro das saídas brutas versionadas e não impedem a aplicação.

`git am` não foi rodado, para não criar commits.

O `c01b.bundle` passou no `git bundle verify`. Num repositório novo, só com a história até `cdc185f`, o `git fetch` pelo sha completo e pelo nome do ref trouxe `64a3041`. O `ef0d7b2` veio junto, e o diff `ef0d7b2..64a3041` deu os mesmos 45 arquivos.

## Brutos

Os caminhos da máquina foram trocados por `<scratchpad>`, `<sp-safc01>`, `<sp-safc02>`, `<chrome>` e `<sessao>`. Os dados são sintéticos (`SAFRION_DADOS=sintetico`; `REAL=False`).

| Arquivos | Fase |
|---|---|
| `C01b/brutos/C01b-ver-oraculo_*` | Verificação de `ef0d7b2`, lente oráculo: comparações com o oráculo, harness e roteiros do ADENDO na tela |
| `C01b/brutos/C01b-ver-ui_*` | Verificação de `ef0d7b2`, lente tela: fluxos A–F, base e correção |
| `C01b/brutos/C01b-ver-regressao_*` | Verificação de `ef0d7b2`, lente regressão: unidade e navegador, base e HEAD; desempenho com histórico longo |
| `C01b/brutos/C01b-fech_*`, `SAFC01-build.log` | Fechamento (`d1b81f4`): unidade antes e depois, harness, bateria (`bat_*`) e sementes |
| `C02/brutos/C02-autor_*`, `SAFC02-*` (salvo `SAFC02-build.log`) | Autor (`62b0904`), base e depois |
| `C02/brutos/C02-ver-simetria_*` | Verificação de `62b0904`, lente simetria |
| `C02/brutos/C02-ver-regressao_*` | Verificação de `62b0904`, lente regressão: bateria na base e no HEAD e sonda R5 → R4 |
| `C02/brutos/C02-fech_*`, `SAFC02-build.log` | Fechamento (`f52fa09`): bateria, propriedade e simetria, camada sintética e rodada final |

Ficaram de fora:
- a lente de tela da SAF-C02 não gravou log de texto, só capturas e JSON das vistas;
- as duas tentativas interrompidas da lente de regressão da SAF-C02 (`c02/` e `safc02-reg/` no scratchpad) não entraram no parecer, por isso não estão aqui;
- os scripts de sonda e de propriedade das lentes continuam no scratchpad, porque o pacote leva só saídas.
