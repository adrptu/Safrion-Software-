# TABELAS-FOCO-20261004 v2 (5983172395) · incremento 1: O.S. por talhão — evidência executada

- Branch `claude/v44-tabelas-01`, base `3d8b3e4` (AÇÃO + REND D-01 R3), reserva `4f0f27a`. Dados: camada sintética (`dados_lagoa_sintetico/saida`), sem dado real.
- Ambiente: contêiner da nuvem, Chrome headless (`/tmp/cloudchrome/chrome`), testes serializados por `flock /tmp/cdp9333.lock`.

## Arquivos
- `tabelas_os_test.log` — `python3 tabelas_os_test.py` → **37/37 ok** (TF01–TF04, TF06; 1440 e 390 px; teclado e toque).
- `capturas/` — antes/depois a 1440 e 390 px, detalhe a 390 px e agrupado por talhão.
- `tf05-inventario.md` / `.json` — `python3 tabelas_inventario.py`: 123 páginas, 260 grades, 1505 colunas; 363 colunas com suspeita de variável composta em 168 grades; 6 tabelas manuais em 2 páginas. Triagem heurística para o incremento 2: suspeita não é defeito e ausência não é conformidade.
- `bateria/` + `00-bateria.sh` — bateria completa (100 passos), 02:45–03:49 UTC. Comparada com a base `v44-acao-01/bateria-20261005`: os mesmos 13 logs com saída ≠ 0 nas duas, sem falha nova. Diferenças: `cadp_fix_test` 11/15 (base 10/15: o item 8 passou, porque o filtro rápido sem linhas já não cai para todas) e `tabelas_os_test` novo.

## Limites
- TF06: o oráculo do Gemini (OS100/101/102) não existe nos dados; a mesma propriedade foi provada nos dados da demonstração (OS-0421 em T1 e T2; 10 O.S. distintas, não 11; T1 ou T2 = 2 O.S. · 452 ha).
- Nomes iguais em fazendas diferentes não ocorrem nos dados: provado no componente G2 com linhas sintéticas (node).
- Sem exportação na O.S. hoje; sem ação em lote na grade da O.S.
- Ficam para o incremento 2: as outras 167 grades suspeitas (por exemplo, CA-01 `g_os` "Realizado · saldo") e as tabelas manuais.
