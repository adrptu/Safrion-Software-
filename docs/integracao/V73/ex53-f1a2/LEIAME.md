# EX-53 F1a parte 2: provas (19/10/2026)

**Código:** `aa32012e` e `b5180a6f` em `claude/v44-ex53-f1a2`, sobre a composição `d491c55e`. O render testado saiu da árvore com o código igual ao `b5180a6f`.

## O que muda
- **% do orçado numa conta só:** o `custo_dominio.py` entrega `consumo_orc_pct`, e o Painel só lê. Prioridades e Alavancas mostram o mesmo número.
- **KPI-PCM-05 (`manCumprimento`):** a base são as preventivas com vencimento original no período, até hoje. A aberta vencida conta, e base vazia dá `null`, nunca 100%. Ainda não há cartão na tela.
- **Revisão do PR #122 (6258085103):**
  - "Meta não configurada" aparece uma vez no título das Alavancas; o "Indicador parcial" continua por célula;
  - impacto, dono e verbo alinham entre as linhas das listas do Painel.
- **Achado do Codex (6258137889):** o executor do KPI-PCM-05 funciona no jsc do Mac. O Codex rodou 12/12 no jsc real (6258182710).

## Testes executados (render `SAFRION_DADOS=sintetico`, brutos em `logs/`)

| Teste | Resultado |
|---|---|
| `painel03_test` | 54/54, com o P7g novo (alinhamento a 1440 nas 6 abas) |
| Contraprova do P7g no render da composição `d491c55e` | reprova nas 4 abas com lista (50/54) |
| `painel_agricola_test` | 81/81 |
| `ds_test` | 72/72 |
| `ex53_metas_test` | PASS; o `painel_gestao.py` de `aa32012e` reprova ("o aviso de meta vem uma vez no bloco") |
| `man_cumprimento_unit_test` (node) | 12/12; o C10 é a contraprova da regra antiga (50% contra 33%) |
| `compras_materiais_unit_test` | 41/41 |
| Prova focal do Painel (1440 e 390 px, teclado) | OK |

**Fotos (`fotos/`), conferidas uma a uma:**
- Prioridades e Manutenção, em 1440 e 390 px.
- Em 390 px, o aviso "Meta não configurada" desce para a linha abaixo do título. As listas mantêm a grade própria do celular.
