# VISOES-1 · seletor de visões na O.S.

A O.S. ganha um seletor por ícone com quatro visões: Lista, Tabela agrupada, Kanban e Carga por recurso. É o pedido do proprietário de 10/10/2026.

- **Branch:** `claude/v44-visoes`, na worktree `sp-vis`. Segue o regime leve do protótipo (AGENTS §3.5).
- **Base para classificar vermelhos:** `0139898`, o merge-base com `0c0931f`.
- **Desenho:** `docs/integracao/VISOES/DESENHO.md`. Ele está em `int/v55b` (`0c0931f`), não nesta branch. A volta do detalhe segue a regra 02 do §2.11.
- **Decisões:** [`DECISOES.md`](DECISOES.md).
- **Evidências:**
  - `revisao/`: o antes e o depois das correções, executados em 10/10 por quem corrigiu;
  - `conferencia-1310/`: a conferência de 13/10, executada.

## Achados da revisão independente (10/10, lentes A, B e C)

Cada achado tem uma linha. Achados repetidos entre as lentes aparecem uma vez só.

Como ler as colunas:
- **Commit:** onde está a correção.
- **Teste:** fica vermelho no `_render` de `c6061fd`, de antes das correções (`revisao/antes/`), e verde na candidata (`conferencia-1310/`).

| Achado | Sev. | Estado | Commit | Teste |
|---|---|---|---|---|
| C1 · na Tabela agrupada, o subtotal do talhão ignorava a fase e a busca, e a soma dos grupos desmentia o Total | S2 | corrigido | `d3202cd` | E1b (fase) e E1c (busca, acrescentado em 13/10) |
| A1 · a entrada por endereço (`#OS-…`, `#tal=…`) herdava a Safra guardada | S3 | corrigido | `d3202cd` | E6b |
| A2 · um recorte só com Canceladas ficava sem mensagem (Lista em branco, Kanban vazio) | S3 | corrigido | `d3202cd` | E3b2 |
| A3/C2 · o Voltar usava `history.back()` e aplicava contexto antigo, de outro perfil ou já usado | S3 | corrigido: regra 02, sempre o destino canônico | `cf3ef42`, `195a939` | U10–U10d; mutantes M5 e M6 (unidade); E3 (link, trilha, recusado: antigo, outro perfil, outra Safra, já usado) |
| A4 · na volta, um redesenho tomava o foco restaurado | S3 | corrigido: foco e rolagem reafirmados até a primeira interação | `cf3ef42`, `df0f272` | E3 (foco e rolagem conferidos de novo 2 s depois) |
| A5 · na Carga, os blocos não seguiam a Fazenda e a Safra do topo | S3 | corrigido | `d3202cd` | E8 (Fazenda) e E8b (Safra, acrescentado em 13/10) |
| C3 · a Carga não tinha a faixa "Sem alocação (n)" | S3 | corrigido | `d3202cd` | E8 |
| A6/B2 · depois de mudar a largura, a parada de Tab ficava num botão oculto | S3 | corrigido | `cf3ef42` | M6 |
| B1/C5 · a dica abria no clique e no toque e cobria "Nova ordem" e os chips | S3 | corrigido: só `:focus-visible` (o `g2dica` é da DS) | `cf3ef42` | C4b, M5 |
| B4/C4 · o foco caía no BODY depois de "Limpar filtros" e "Ver em lista" | S3 | corrigido | `cf3ef42` | E3d |
| B6 · o Kanban a 390 px apertava 5 colunas (pré-existente, S3 da base) | S3 | interino, já com commit: colunas de 148 px e rolagem do quadro. O definitivo fica na F2a (seletor das 5 etapas no celular) | `d3202cd` | M8 |
| A7 · o mutante `pushState` passava na bateria | S4 | corrigido (teste) | `2847a5b` | E5b; o mutante fica vermelho (`conferencia-1310/mut_push_E5.log`) |
| A8 · o `g2visaoUrl` recodificava a query | S4 | corrigido | `cf3ef42` | U6g |
| A9 · a checagem estática só pegava uma forma de escrita de URL | S4 | corrigido | `2847a5b`, `195a939` | B4b |
| B3 · em cores forçadas, o ativo ficava igual aos inativos | S4 | corrigido | `cf3ef42` | C7 |
| B5 · o menu do "mais" ficava solto ao passar de 640 px | S4 | corrigido | `cf3ef42` | M7 |
| C6 · minimalismo: um item só no "mais", o rótulo "Tabela agrupada" e três contadores | S4 | pendente: decisão do proprietário (VIS-D30); muda a regra literal do pedido de 10/10 | — | — |

As lacunas do desenho que ficam para outras fatias estão no fim da tabela de decisões, em `DECISOES.md`.
