# EX-53 · cumprimento de preventiva no detalhe do ativo pela regra única (19/10/2026)

**Achado do Codex (PR #47, 6258683205):** Manutenção › ativo › Custo e desempenho › "Cumprimento de preventiva" tinha uma conta própria (`ma_ativoV`, `areas/maquinas.py`). Ela contava só as preventivas encerradas, de todo o histórico. Uma preventiva vencida em aberto, ou vencida sem ordem, não entrava. O ativo com tudo atrasado aparecia "não calculável".

**Dano evitado:** dois números para o mesmo indicador (KPI-PCM-05). O painel mostra uma coisa e o detalhe do ativo outra, e o atraso some do detalhe.

**Correção (autoria Claude, revisão Codex):**
- `dados_manutencao.py`: `manCumprimento(c, k, aid)` ganha o filtro opcional por ativo nas ordens e nas linhas sem ordem. Sem `aid`, o resultado é o mesmo de antes. A função e `manPeriodo` entram no `window.__man`, o acesso dos testes de navegador.
- `areas/maquinas.py`: o detalhe do ativo chama `manCumprimento(c, período do painel, ativo)`. Mostra "k de n (p %) · período" ou "sem base no período", no mesmo período do bloco Custo e desempenho.

## Testes executados (render `SAFRION_DADOS=sintetico`, branch `claude/v44-ex53-ma-cumpr` sobre `4872d732`)

| Teste | Resultado | Bruto |
|---|---|---|
| `man_cumprimento_unit_test` (C11 filtro por ativo; C12 contraprova da conta antiga) | 14/14 | `logs/man_cumprimento_unit_test.log` |
| `ex53_m5_cartao_test` | PASS | `logs/ex53_m5_cartao_test.log` |
| `ma_cumpr_ativo_test` (novo, navegador, 16 ativos) | 4/4 | `logs/ma_cumpr_ativo_test.log` |
| Contraprova: `ma_cumpr_ativo_test` no render da v140 | 1/4: W1 e W2 reprovam (16 ativos "não calculável", 3 com preventiva vencida em aberto); W3 reprova porque a v140 não expõe a função | `logs/ma_cumpr_ativo_test_contraprova_v140.log` |
| Impacto: `ma_vinculo` 101/101, `ma_unica` 23/23, `ma_rastreio` 58/58, `ma_planos` 18/18, `man_limpa` 9/9, `ativo_unico` 7/7, `ds_man` 99/99, `painel03` 54/54, `ex53_metas` PASS | verdes | `logs/*_test.log` |

**`ma_cumpr_ativo_test`:**
- W1: o oráculo é a definição do KPI-PCM-05 refeita no teste sobre os dados crus. Não usa a função do produto.
- W3: a soma por ativo é igual ao total, no mês e em 12 m. O filtro reparte a base sem perder nem repetir.

**Não executado:** `ds_test` (varredura geral). A mudança é texto de uma célula do detalhe do ativo, coberto pelo `ds_man` e pelo novo teste.

**Em execução neste commit:** `paginas_scan`. O bruto entra no commit seguinte.
