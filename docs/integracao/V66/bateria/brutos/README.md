# Brutos da V66 (dados sintéticos)

Todos os testes rodaram na árvore de trabalho int/v66b (branch claude/v44-v66), com CHROME_BIN e SAFRION_DADOS=sintetico.

| Arquivo | Teste | Árvore no momento | rc | Resultado | sha256 |
|---|---|---|---|---|---|
| `talmapa_repeticao.log` | talmapa | a73c884 (14/10 05:33) | 0 | RESULTADO: 8/8 | `d6f018bdf1e5dfe1` |
| `mapa_solo_texto_repeticao.log` | mapa_solo_texto | a73c884 (05:35) | 0 | RESULTADO: 9 ok · 0 falhas | `e986ac3e96b8c8bb` |
| `ma_unica_repeticao.log` | ma_unica | a73c884 (05:37) | 0 | RESULTADO: 23/23 ok | `7a8326f87c9359d3` |
| `colheita_mapa_repeticao.log` | colheita_mapa | 340fd92 (05:43) | 0 | RESULTADO: 7 ok · 0 falhas | `d74dc6139a5af489` |
| `ben_fluxo_completo.log` | ben_fluxo, todos os modos | ae8ddf1 (07:08) | 0 | RESULTADO: OK 224/224 | `6acf9649d7b6f965` |
| `visual_corte_v66.log` | visual_corte completo | render de int/v66b, fim às 07:34 | 1 | RESULTADO: 76 achado(s) em 155 páginas + 7 visões × 3 tamanhos | `6d37d7e21840bb25` |

- `visual_corte_diff.txt`: v66 × v63. Os 10 C1 "só na v66" são os mesmos itens da v63 (o registro da v63 corta o texto em 40 caracteres). Único achado novo: C4 "· Santa Rita" no MB-01 (3 tamanhos), regressão minha; corrigido nesta entrega (MB-01: 0 achados; VE-04 segue com os mesmos 8, contraprova do detector).
- O excesso de C1 da bateria (108 achados) não se repete nesta varredura isolada (76): efeito de carga e fonte durante a bateria, não regressão.
- `vermelhos_antigos_v63_v66.txt`: os 9 vermelhos antigos com o mesmo resultado nas duas versões.
- `artefato_v70.sha256`: manifesto dos 181 arquivos publicados no artefato versão 70.
