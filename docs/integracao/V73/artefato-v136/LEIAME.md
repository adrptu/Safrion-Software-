# Artefato v136 (versão 146, 18/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm
- **Versão:** 146 (`1792356309-bb6f`), um lote com 4 páginas.
- **Fonte:** `61cd6e4c` em `claude/v44-v135-osagrupa`. O render é o build `SAFRION_DADOS=sintetico` desse commit.
- **O que mudou:** 4 páginas em relação à v135, e nenhuma entrou ou saiu.
  - `OS.dc.html`: EX-32 v2, a aprovação em lote no diálogo do grupo.
  - `IN-04.dc.html`: a classificação do Mapa passa a vir de `mapa_camadas.js` (EX-55 D2), com a mesma saída (paridade 60/60).
  - `PG.dc.html` e `LO-02det.dc.html`: carregam o mesmo código da O.S.
  - O `index.html` fica igual.

## Como conferir

1. Escolha o perfil **Caio (PCP)**.
2. Abra Ordens de serviço › visão Frentes, com a fazenda Santa Rita.
3. Abra a frente do Glifosato e use "Agrupar 2 O.S. desta calda".
4. "Conferir agrupamento" e depois "Confirmar agrupamento" criam o GRP-1.
5. Troque para o perfil **Ana (gestora e RT)** e reabra o botão "GRP-1 · …" na mesma visão.
6. O botão principal passa a ser "Conferir aprovação das 2 pendentes". Ele mostra a prévia. Em seguida, "Aprovar as 2" grava um registro (CMD-42) por O.S.
7. Confira que as duas O.S. continuam "A liberar" e sem reserva. Liberar é a ação seguinte, com o papel de quem libera.

São os passos do `os_lote_test`.

## Conferência (executada)

- **Render:** o do commit limpo é idêntico ao testado (180 arquivos por sha256, 0 diferenças). Os testes estão em `docs/integracao/V73/v136/`.
- **Espelho:** o espelho local é igual ao render em todos os arquivos do render.
- **Leitura de volta** da versão 146, comparada com o espelho:

| Página | sha256 |
|---|---|
| OS.dc.html | `b25c8883edb0ce7454db15c56ea98db46a3ed9a676d093c7f59d0319fd728018` |
| IN-04.dc.html | `840617ede8c257f4e9f37d0476f6843c6013086ebb7e482d3f1a65af09a6874b` |
| PG.dc.html | `c0293d758899b02b6e40b45a8d8f3617a645896a3dc38a1c1fe321f00e0174fd` |
| LO-02det.dc.html | `3773091f9c252609bdd3fc1dd273f8d42ce1fc9d1a6b8cc19106977110427cbd` |

4/4 iguais.
