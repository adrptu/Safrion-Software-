# Brutos da revisão rev1 da frente CADASTROS-PADRAO

Revisão do Codex 6220145128 (PR #47), em 0d37cc1. Saídas sem edição, dados sintéticos.

- **Comando de cada teste** (de `tools/prototipo/v37/gen37/`, depois do build):
  ```
  env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico timeout 1500 python3 -B <teste>
  ```
- **`_resumo_*.txt`:** uma linha por teste, com o código de saída, o tempo e a linha RESULTADO.

| Pasta | O que tem |
|---|---|
| `0d37cc1/` | Bateria antes da correção. Os logs são da 3423212, que tem o mesmo código de produto da 0d37cc1 (a 0d37cc1 só mudou dois testes). `assinatura_test` e `botoes_retorno_test` rodaram na 0d37cc1. Inclui o 44/44 do `cadastros_padrao_test`. |
| `bb57b3b/` | Bateria depois da correção, inclusive o teste novo `cadastros_rev1_test` (14/14). |
| `contraprova/` | `cadastros_rev1_test` com `CONTRAPROVA=1` no `_render` da 0d37cc1: reprova R1a a R1f e R2a a R2e. Também o `cadastros_padrao_test` na base 6a23a88: reprova P1 a P6. |
| `fotos/` | 1440 e 390 px: "A resolver" com as fazendas pendentes, os documentos no Crédito depois da migração e o CD-01 da galeria. |

**Vermelho já existente, igual na 0d37cc1 e na ponta 1639ab3:**
- `getest`: GE-04 pc088_unico e GE-08 bloqueio_conferencia;
- `ds_test` 69/72: D13, D15 e E2, na O.S.;
- `tabelas_cad_irr_unit` 44/51.

**`visoes_v23_codex_test` 22/23:** o localizador do teste procura o chip do papel pelo texto antigo ("Fornecedores\n8"). O chip agora é o do motor ("Fornecedores 8").
