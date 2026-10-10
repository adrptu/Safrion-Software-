# Pacote de revisão da frente NAV1 (NAV-1: Planos agronômicos em lista → detalhe)

Fonte recuperável para a revisão isolada, antes da integração. Nada aqui é código integrado.

- **Frente:** branch local `claude/v44-nav` (worktree `<sp-nav>`). Commit final: `a7023ca` ("NAV1: clique do pa_lista_test espera o alvo livre e evidência das correções (§7.1)"). A correção da revisão é o `7b7d260`.
- **Base:** `cdc185f`, o merge-base com `claude/prototipo-v44`, já em `origin/claude/prototipo-v44`.
- **`commits.txt`:** os 5 commits de `cdc185f..a7023ca`, todos sem merge.
- **`patches/`:** um `git format-patch` por commit. Para reproduzir: `git am patches/*.patch` sobre `cdc185f`.
- **`diff-cdc185f-a7023ca.patch` e `diffstat.txt`:** o diff inteiro, com 8 arquivos (+1353 −247).
- **`relatos.md`:**
  - resumo da implementação, da revisão adversarial (R1 S2, R2–R5 S3, R6–R8 S4, T1–T3) e da correção, com testes rotulados "executado" ou "relatado";
  - relatos completos dos agentes.
- **`brutos/`:** 91 logs já executados, descritos abaixo. Nada foi reexecutado para montar o pacote.
- **`verificacao-pacote.txt`:** saída das verificações deste pacote.

A revisão foi feita por um agente Claude separado, que se identifica "no papel do Codex". **A revisão do Codex continua pendente.**

## Nota de integração: `etapas_celular_test.py` (correção do integrador, já combinada)

A frente não podia editar esse arquivo. Na `a7023ca`, ele quebra no item 7 com `KeyError: 'sobrepoe'` (log em `brutos/NAV1-corr_log_etapas_celular.txt`), porque a PA deixou de ter faixa de etapas. O integrador faz a troca depois do merge:

- **Sobre a base atual:**
  - linha 142: `for pg in ['CMP','SAF','PA','EST','IR-02','MA-01']` passa a `['CMP','SAF','EST','IR-02','MA-01']`;
  - linha 143: o rótulo "(6 telas)" passa a "(5 telas)".
- **Se o PCM já tiver entrado:** o PCM já tira `MA-01` dessa linha e muda o rótulo para "5 telas" (ver `../PCM/README.md`). Aí a lista fica `['CMP','SAF','EST','IR-02']` e o rótulo vira "(4 telas)".
- **Esperado:** `etapas_celular_test.py` com 14 ok · 0.
  - Com a troca feita em memória, sem `PA`, deu 14 ok · 0 (executado antes da correção: `brutos/NAV1-impl_r2_etapas_sem_pa.log`).
  - A revisão propôs outra saída: `z[g].get('sobrepoe',0)` e `z[g].get('vazam')` na linha 143, mantendo a PA. Também deu 14 ok · 0 (executado numa cópia: `brutos/NAV1-corr_log_etapas_celular_alt.txt`).
  - A fila de integração registra a primeira opção.

Outros pontos para a integração:
- **Vermelho conhecido:** `componentes_test interacao` dá 8 ok e 2 falhas (itens 10 e 14, hover no headless), igual à base.
- **Conflito provável com a DS** no item 14 do `componentes_test.py`, porque a DS ainda não foi integrada.
- **`acao_unica_test.py` e `componentes_test.py`** também são alterados pelo PCM.

## Como reproduzir
```
git checkout --detach cdc185f
git am docs/integracao/NAV1/patches/*.patch        # ou: git apply docs/integracao/NAV1/diff-cdc185f-a7023ca.patch
```

## Verificação do pacote (executada em 09/10 às 23:57 UTC)

Tudo numa worktree temporária em `cdc185f`, removida no fim:
- `git apply --check` do diff deu rc 0;
- depois de aplicado, os 8 caminhos ficaram iguais, byte a byte, aos de `a7023ca`;
- revertido, a worktree voltou limpa;
- os 5 patches, aplicados em sequência com `git apply --check` e `git apply`, deram rc 0 e a mesma árvore de `a7023ca`.

`git am` não foi rodado, para não criar commits.

## Brutos

Os caminhos da máquina foram trocados por `<scratchpad>`, `<sp-nav>`, `<chrome>` e `<sessao>`. Os dados são sintéticos.

| Arquivos | Fase | Código |
|---|---|---|
| `NAV1-impl_base_*`, `NAV1-impl_pa_lista_base.log`, `NAV1-build-base.log` | Implementação, controle na base | `cdc185f` |
| `NAV1-impl_dep_*`, `NAV1-impl_r2_*`, `NAV1-impl_run_*.out` | Implementação, 09/10, 14:31–17:02 | árvore de `19aeb94`..`0e1c368` |
| `NAV1-rev_*`, `NAV1-rev_transcricao_sondas.txt` | Revisão adversarial: bateria, sondas A–L, base_A e mutantes | `0e1c368` |
| `NAV1-corr1_transcricao_regras.txt` | 1ª tentativa de correção, interrompida | antes de `7b7d260` |
| `NAV1-corr_*` (`bateria.idx`), `NAV1-build.log`, `NAV1-render.log` | Correção, 18:46–19:29 | `7b7d260` |
| `NAV1-corr_*` (`bateria2.idx`), `NAV1-corr_transcricao_regras.txt` | Correção, 21:20–21:42 | `a7023ca` |
