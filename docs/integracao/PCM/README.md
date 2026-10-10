# Pacote de revisão da frente PCM (Manutenção simplificada: S1, S2, 1a, S3 e S4)

Fonte recuperável para a revisão isolada, antes da integração. Nada aqui é código integrado: a frente ainda não entrou na branch única.

- **Frente:** branch local `claude/v44-pcm` (worktree `<sp-pcm>`). Commit final: `ba03515` ("PCM: correções da revisão").
- **Base:** `cdc185f`, o merge-base com `claude/prototipo-v44`, que já está em `origin/claude/prototipo-v44`.
  - A frente nasceu em `99537ca`.
  - Recebeu a branch única por dois merges: `562bc23` (ecc8b00) e `6af8486` (cdc185f).
- **`commits.txt`:** os 12 commits de `cdc185f..ba03515`, entre eles os 2 merges.
- **`diff-cdc185f-ba03515.patch` e `diffstat.txt`:** o diff inteiro, com 47 arquivos (+3993 −1687). É a contribuição líquida do PCM sobre `cdc185f`, porque os merges só trouxeram a base.
- **Sem `patches/`:** como a faixa tem merges, um `git format-patch` não reproduz a história. O `pcm.bundle` faz esse papel.
- **`pcm.bundle` (213 KB):** a história `cdc185f..ba03515` inteira, com o ref `refs/heads/claude/v44-pcm` apontando para `ba03515`.
  - Pré-requisitos: `99537ca`, `ecc8b00` e `cdc185f`, todos ancestrais de `cdc185f`.
- **`relatos.md`:**
  - resumo da implementação, da revisão adversarial (A1–A11 e S4) e da correção;
  - tabela de testes rotulada "executado" (saída em `brutos/`) ou "relatado" (sem saída no pacote);
  - relatos completos dos três agentes.
- **`brutos/`:** 192 logs já executados pela frente, descritos abaixo. Nada foi reexecutado para montar o pacote.
- **`verificacao-pacote.txt`:** saída das verificações deste pacote.

A revisão que consta aqui foi feita por um agente Claude separado, no papel de revisor. **A revisão do Codex continua pendente.**

## Como reproduzir

Pelo diff, sobre `cdc185f`:
```
git checkout --detach cdc185f
git apply docs/integracao/PCM/diff-cdc185f-ba03515.patch
```

Pelo bundle, que traz a história com os merges:
```
git bundle verify docs/integracao/PCM/pcm.bundle
git fetch docs/integracao/PCM/pcm.bundle ba035151dd66f28fa569bd221e6f85324dd8b20c
git checkout --detach FETCH_HEAD
# alternativa: git fetch docs/integracao/PCM/pcm.bundle claude/v44-pcm:refs/heads/pcm
```

Com o sha curto, `git fetch pcm.bundle ba03515` falha com "couldn't find remote ref". Use o sha completo ou o nome do ref.

## Verificação do pacote (executada em 09/10 às 23:57 UTC)
- **Diff, numa worktree temporária em `cdc185f`:**
  - `git apply --check` deu rc 0;
  - depois de aplicado, os 47 caminhos ficaram iguais, byte a byte, aos de `ba03515`;
  - revertido com `git apply -R`, a worktree voltou limpa e foi removida.
- **Bundle:** `git bundle verify` deu ok.
  - O teste foi num repositório novo, só com a história até `cdc185f`, como o origin.
  - `git fetch` pelo sha completo e pelo nome do ref trouxe `ba03515`.
  - `git fsck --connectivity-only` não acusou erro, e o diff contra a base deu os mesmos 47 arquivos.
  - O teste também registra a falha do sha curto.

## Brutos

Os caminhos da máquina foram trocados por `<scratchpad>`, `<sp-pcm>`, `<chrome>` e `<sessao>`. Os dados são sintéticos.

| Arquivos | Fase | Código |
|---|---|---|
| `PCM-now_*` | Implementação, bateria de 06/10 (os `PCM-now_u*` são de 09/10, 11:18) | PCM antes das junções |
| `PCM-base_*` | Base | 06/10: `99537ca`. 09/10, 12:17–12:31 (`PCM-base_resumo.txt`): `ecc8b00` |
| `PCM-base-build.log`, `PCM-base2_cmptest.log` | Base | `ecc8b00` |
| `PCM-r1_*`, `PCM-r2_*`, `PCM-r3_*` | Implementação, 09/10, 11:25–12:56 | `98c214f` |
| `PCM-ma_regras.log`, `PCM-ma_app_test.py.log`, `PCM-os_aprov_lib_test.py.log`, `PCM-aqd.log`, `PCM-r4_*` | Implementação, depois da junção com cdc185f | `6af8486` |
| `PCM-r5_*` | Implementação | `21c0e51` |
| `PCM-rev_*` | Revisão adversarial: sondas no navegador (`b1`–`b4`), base do `ma_unica` e mutantes de navegador | `21c0e51` |
| `PCM-rev_transcricao_sondas_e_mutantes.txt` | Revisão: sondas P1–P20, entre elas P3 (reprodução do S1), e os 40 mutantes de regra | `21c0e51` |
| `PCM-r6_*` … `PCM-r9_*`, `PCM-build.log`, `PCM-render.log`, `PCM-mut-build.log` | Correção, 09/10, 16:59–18:42 | árvore que virou `ba03515` às 18:48 |
| `PCM-corr_transcricao_unidade.txt` | Correção: testes de regra, vermelho no código antigo e verde final às 18:08 | idem |
| `PCM-varredura1.log` | Varredura de 06/10 | PCM antes das junções |

O rótulo "dados reais locais: 5/5" que o `montar_render.py` imprime em `PCM-render.log` é enganoso, como apontou a V3-3 da SAF-C02. A worktree não tem `dados_lagoa/` nem `dados_lagoa_kml.py`, e o `_render` usa a camada sintética (`REAL=False`).

## Para a integração
- **Aceite do antigo S1 (A1):** tentar de novo pela tela e pela regra (`relatos.md`, "Pontos para o revisor").
- **Conflitos prováveis:**
  - **`g2lib.js` (G2_PERFIS):** o PCM acrescenta o João (7 perfis), e a branch única já mudou esse arquivo depois de `cdc185f`. Preserve todos os perfis de todos os lados. Ajuste com motivo as contagens dos testes que contam perfis (`aprova_quem_decide_unit.js`, `os_aprov_lib_unit.js`).
  - **`acao_unica_test.py` e `componentes_test.py`:** a NAV1 também mexe neles.
  - **`etapas_celular_test.py`:** o PCM tira `MA-01` da linha 142 e passa o rótulo do item 7 para "5 telas". A correção do integrador da NAV1 tira `PA` da mesma linha (ver `../NAV1/README.md`).
  - **`areas/planejamento.py`:** a SAF-C02 troca os links "Ver capacidade" em linhas vizinhas.
- **Estado salvo:** o cenário subiu para a versão 5 (D-53). Confirme que as frentes já integradas continuam lendo o estado.
- **Vermelhos que a frente atribui à base:**
  - `ostest` 32/33, `osacoes` 5 falhas;
  - `acao_unica` responsivo 2 falhas;
  - `componentes` ajustes, `etapas_celular` complemento e `etapas_celular` desktop.

  Confira no pré-merge.
