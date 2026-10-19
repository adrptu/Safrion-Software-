# EX-53 M7a · backlog da oficina por especialidade (KPI-PCM-08), 19/10/2026

**Acordo:** PR #47, 6259217691. Autoria do Claude, revisão e integração do Codex.

**Resultado útil:** o PCM vê no Painel › Manutenção as horas previstas das ordens ainda não executadas, por especialidade e por situação. A situação é pronto, falta de peça, a liberar ou em execução.

**Dano evitado:** a carga do Kanban da MA mostrava "0 HH" para uma ordem sem tempo previsto, como se não houvesse trabalho.

## Mudança
- **`dados_manutencao.py`:**
  - `manHH` é a soma única de horas previstas: ordem sem tempo não vira 0 e conta em `semTempo`.
  - `manBacklog(c, aid)` monta o KPI-PCM-08 com as ordens Liberadas (pronto), A liberar (falta de peça ou a liberar) e Em execução. Em conferência a execução terminou e a ordem sai do backlog.
  - As semanas equivalentes ficam `null` enquanto não houver capacidade semanal configurada.
- **`areas/maquinas.py`:** a carga "Esta semana" e a do Kanban passam a usar `manHH`. Não há outra soma de `o.tempo` na MA.
- **`areas/painel_gestao.py`:** cartão novo "Backlog da oficina", fora do bloco do cartão M5.
  - O valor é o total em HH.
  - Na linha de baixo vêm as especialidades, da maior para a menor carga, e depois a situação.
  - A dica diz que a capacidade semanal não está configurada.
- **Fotos de 1440 e 390 px conferidas (`fotos/`), duas correções antes do commit:**
  - o primeiro texto ocupava 4 linhas e misturava especialidade com situação;
  - o separador "|" parecia um "I" nessa fonte.

## Testes executados (render sintético, `claude/v44-ex53-m7` sobre `262662af`)
| Teste | Resultado |
|---|---|
| `man_backlog_unit_test` (B0–B10; B0 e B10 com oráculo independente) | 12/12 |
| Mutante: em `manHH`, ordem sem tempo conta 0 | reprova B6 e B9, como esperado (`logs/mutante_sem_tempo_zero.log`) |
| `ma_backlog_test` (novo, navegador: cartão, 1440/390, Kanban, ordem sem tempo) | 5/5 |
| Contraprova: `ma_backlog_test` no render da v141 | 2/5. Não há cartão, e a coluna Liberadas mostra "0 HH" para a ordem sem tempo |
| `painel03` e `paginas_scan`, no build final | 54/54 e 5/5 (146 páginas) |
| Impacto, no build anterior ao ajuste do texto do cartão | `man_cumprimento_unit` 14/14, `ex53_m5_cartao` PASS, `ma_vinculo` 101/101, `ma_unica` 23/23, `ma_rastreio` 58/58, `ma_planos` 18/18, `man_limpa` 9/9, `ativo_unico` 7/7, `ds_man` 99/99, `ma_cumpr_ativo` 4/4, `ex53_metas` PASS |

**Fora desta fatia:**
- reincidência (KPI-PCM-07), que pede a janela definida;
- semanas equivalentes, que pedem a capacidade semanal por especialidade.

Os dois são itens seguintes da D11.
