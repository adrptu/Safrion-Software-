# Brutos da revisão rev2 da frente CADASTROS-PADRAO

Revisão do Codex 6221423767 (PR #47), em 16ffe95. Saídas sem edição, dados sintéticos.

- **Comando de cada teste** (de `tools/prototipo/v37/gen37/`, depois do build):
  ```
  env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico timeout 1500 python3 -B <teste>
  ```
- **Bateria da 16ffe95:** o "antes" de cada teste está em `../cadastros-rev1/bb57b3b/`, com o mesmo código de produto (a 16ffe95 só juntou brutos).

| Pasta | O que tem |
|---|---|
| `43f8246/` | Bateria pedida, depois da correção: `tabelas_cad`, `ds_1610`, `cadastros_padrao`, `credito_menu`, `cad_gravacao_falha`, `cad_inicio` e também `getest`, `cadf_*` e `assinatura`. |
| `a8f815e/` | Repetição depois do ajuste de texto, que deixa a dica do documento automático aparecer uma vez: `cadastros_rev1_test` (19/19), `cadastros_padrao`, `credito_menu`, `getest` e `cad_gravacao_falha`. |
| `contraprova/` | `cadastros_rev1_test` no `_render` da 16ffe95, com `CONTRAPROVA=1 CONTRA_ESPERA=R3a,R3b,R4a,R4b`: reprova os quatro casos. Forçar a troca de fazenda deixa 0 CAR na Santa Rita e 2 na Fazenda Teste, como na prova do Codex. |
| `fotos/` | `r3_nao_salvo_1440` (formulário aberto com o rascunho e o motivo), `r4_automatico_so_leitura_1440`, mais as de R1 e R2. |

**`credito_menu_test` instável sob carga** (média de carga 36 na máquina compartilhada, 4 núcleos):
- 43f8246: 14/16. Faltou o vínculo "‹ Crédito" em C2 depois da espera fixa de 1,2 s.
- a8f815e, 1ª execução: caiu com "Inspected target navigated or closed" no meio de uma navegação.
- a8f815e, repetição: 16/16 (`credito_menu_test.py.repeticao.log`). Nenhuma das falhas toca nos documentos.

**Vermelho já existente:** `getest` (GE-04 pc088_unico e GE-08 bloqueio_conferencia), igual na 0d37cc1 e na ponta 1639ab3.
