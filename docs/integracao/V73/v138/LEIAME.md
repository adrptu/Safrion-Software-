# v138: o Mapa da fazenda mostra só as O.S. da safra escolhida (18/10/2026)

**O que muda.** Na camada Ordens de serviço, o Mapa da fazenda (IN-04) passa a mostrar só as O.S. da safra escolhida, como a lista da O.S.
- **Por quê:** o PRD 8.4 pede que lista, Kanban e mapa mostrem o mesmo conjunto. A decisão é do Codex (6255851566).
- **O que não muda:** os cultivos da safra atual continuam mostrando o que está no campo agora.
- **Código:** `osSaf` em `areas/inicio.py`.

**Efeito no cenário.** Sai só a OS-0415, da safra 2025/26 e encerrada, do T3 da Santa Rita. Nenhuma O.S. aberta de outra safra some do mapa.
- **Coleta A2 do IN-04 contra a v137:** 6 de 60 contextos mudam, todos no T3 (`A2_dif_v137_v138.txt`).

## Testes executados (render `SAFRION_DADOS=sintetico`)

| Teste | Resultado | Contraprova na v137 |
|---|---|---|
| `os_mapa_test` (M1 agora na safra 2026/27 nas duas telas) | 20/20 | 19/20: o M1 reprova no T3 (`logs/contraprova_v137.log`) |
| `map_irrig_filtro_test` | 15/15 | 14/15: a verificação 15 reprova (`logs/contraprova_map_irrig_v137.log`) |
| `mapa9`, `mapa_mux_f1`, `mapa_mux_f2`, `mapa_filtros`, `mapa_faixa` | 13/13, 43/43, 29/29, 7/7, 25/25 | — |
| `map_decisoes`, `map_aprov`, `map_trilha_icones`, `mapa_solo_texto` | 18/18, 5/5, 9/9, 9/9 | — |
| `visoes_test`, `paginas_scan_test` | 9/9, 5/5 (146 páginas) | — |

## Correção de registro da v137

`docs/mapa/EX-55-F1/LEIAME.md` dizia que o `map_irrig_filtro` estava "verde". O log da v137 mostra 14 ok e 1 falha; o processo saiu com 0 porque o teste não tinha proteção de saída.

A verificação 15 tinha um oráculo desatualizado. Ela lia o ID como a primeira palavra da linha da O.S., mas nas O.S. com selo ("Falta insumo", "Impedida") a primeira palavra é o selo. Com isso, a OS-0418, a OS-0420 e a OS-0431 ficavam fora da conta.

Agora o teste:
- lê o ID em qualquer coluna;
- usa a mesma safra do Mapa;
- tem a proteção de saída do PR #72.
