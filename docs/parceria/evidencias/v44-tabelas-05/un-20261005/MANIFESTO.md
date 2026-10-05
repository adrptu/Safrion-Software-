# TABELAS-FOCO-20261004 v2 (5983172395) · incremento 2d: unidade fixa na célula em todas as grades G2 — evidência executada

- Branch `claude/v44-tabelas-05`, base `cb3f3fe` (2c + 2b corrigido), reserva `1fbb354`, commit `0cf6f90`. A bateria rodou em `0cf6f90` sem alteração local (`bateria/sujos.txt` vazio). Dados sintéticos.
- Decisões do proprietário (Adrianus, chat, 05/10/2026): "sim" à unidade fixa também na célula; "Custo R$/h e R$/ha é melhor e mais intuitivo".
- `tabelas_saf_test.log` **28/28** (etapa 3: "36 m", "21,60 ha/h", "R$ 109,40/ha", "R$ 313,00/h"; filtro Largura = "36 m"; ordem numérica 6 m antes de 12 m; Calagem editada → 12 m, 9,00 ha/h, R$ 25,89/ha). `tabelas_os_test.log` **38/38** (Área, Realizado, Saldo, Dispensado e Progresso com a unidade na célula; cabeçalho sem "(ha)"; sem a coluna Lâmina).
- REND `rend_multiconjuntos_test` fluxo 16/16, telas 5/5, bordas 10/10, bordas2 5/5 (o adaptador LEG tira a unidade só das colunas com `data-un`). `saf_cmp_continuidade` 31/31. `partest` 43/44 e `os_cenario` 14/15, iguais à base. `cmptest` e `saftest` sem falha.
- `capturas/`: etapas 3, 4 e 5 do Planejar safra a 1440 e 390 px, em `0cf6f90`.
- `bateria/` + `00-bateria.sh`: bateria completa, 102 passos (retomada uma vez depois do limite de tempo). Comparada com a do 2c (`v44-tabelas-04/est-20261005/bateria`): o mesmo conjunto de 11 vermelhos anteriores, nenhuma falha nova.
- `SHA256SUMS`: hash de cada arquivo deste pacote.
