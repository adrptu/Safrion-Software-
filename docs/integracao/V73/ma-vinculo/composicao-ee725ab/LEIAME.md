# MA-VINCULO na composição `ee725ab` (PRs #89, #95, #94, #93 e #99)

- **Árvore testada:** `4cd8efe`, o merge da composição `ee725ab` em `7488d5b`. O `7488d5b` já traz as duas correções pedidas pelo Codex: 6229032017 e o lote como conjunto marcado.
- **Merge:** sem conflito; o `areas/modulos.py` mesclou sozinho.
- **Testes pelo impacto:** dados sintéticos, navegador com portão de 1 Chrome. Os brutos estão nesta pasta.

| Teste | Resultado |
|---|---|
| ma_vinculo_test U A B (unidade, navegador e regressão) | 101/101 |
| ma_regras · ma_correcoes_pm · ma_unica | 150/150 · 12/12 · 23/23 |
| ma_rastreio · ma_revisao | 58/58 · 18/18 |
| cartoes_test (alterado pela frente e pelo #93) | 70/70 |
| rmenu_unit · rmenu_generator_test (#93) | OK · OK |

**Sobre o rc=1 do `ma_vinculo_unit`:** é erro do script da bateria, não do produto. O `ma_vinculo_unit.js` não roda sozinho no node: precisa do prefixo que o `ma_vinculo_test.py U` monta, e esse modo U está dentro do 101/101 acima.

**Correções do Codex**, com contraprova em `codex-lote-selecao/` e `codex-6229032017/`:
- na branch com as correções: U 42/42 e A 53/53;
- contraprova sobre o render anterior: A 47/53.
