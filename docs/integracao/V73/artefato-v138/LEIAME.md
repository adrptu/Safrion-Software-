# Artefato v138 (versão 148, 18/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm
- **Versão:** 148 (`1792366332-c88f`), um lote com 1 página.
- **Fonte:** `13b8614a` em `claude/v44-v135-osagrupa`. O render é o build `SAFRION_DADOS=sintetico` desse commit.
- **O que mudou:** só o `IN-04.dc.html`. A camada O.S. do Mapa da fazenda passou a mostrar só a safra escolhida, como a lista da O.S. (`../v138/LEIAME.md`).

## Como conferir

1. Abra o Mapa da fazenda na Santa Rita, camada Ordens de serviço, "Mostrar" Fases.
2. O T3 mostra só a OS-0596 (a liberar). A OS-0415, encerrada na safra 2025/26, não aparece mais.
3. Abra Ordens de serviço, Safra 2026/27, visão Mapa: o T3 mostra a mesma coisa.

## Conferência (executada)

- **Render:** o build do commit limpo (`git worktree` em `13b8614a`) é idêntico ao render testado: 179 arquivos por sha256, 0 diferenças.
- **Leitura de volta:** `IN-04.dc.html` tem sha256 `93ad8aa0e1def2049a396b588830413468ecee0a3502112a02a06797a9e0c2ee`, igual no espelho, no render limpo e na versão 148.
