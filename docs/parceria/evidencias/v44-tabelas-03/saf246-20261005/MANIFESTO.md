# TABELAS-FOCO-20261004 v2 (5983172395) · incremento 2b: Planejar safra, etapas 2, 4 e 6 — evidência executada

- Branch `claude/v44-tabelas-03`, base `cb9eadf` (incremento 2a, PR #41), reserva `364f35b`. Dados sintéticos.
- `tabelas_saf_test.log` — `python3 tabelas_saf_test.py` → **25/25**:
  - os 14 casos da etapa 3;
  - etapa 2: colunas próprias; T7 com meta 45 | t/ha/ano | v3; filtros Unidade da meta e Tipo;
  - etapa 4: Gatilho | Data separados; filtro Talhão = T2;
  - etapa 6: MAP 11-52 = 62.500 | kg | 18/10/2026 | Em cotação | SOL-2026-07; nenhuma unidade colada; filtro Unidade = L; ordenação numérica da necessidade.
- `bateria/` + `00-bateria.sh` — bateria completa (101 passos; retomada depois de um reinício do contêiner, os passos concluídos foram reaproveitados). Mesmo conjunto de logs com saída ≠ 0 da bateria do incremento 2a (`v44-tabelas-02/saf3-20261005/bateria`).
- Testes que liam o texto composto passam a ler por coluna, com os mesmos valores:
  - `rend_multiconjuntos_test` (LEG estendido à etapa 4): 16/5/10/5;
  - `saf_cmp_continuidade_test` (helper `cel`): 31/31;
  - `partest` (LEGT, leitura da etapa 2): 43/44, igual à base; a falha "T1-C copia ajuste do T1-B" é anterior.
- Mudança de expectativa: a etapa 6 deixava de caber em 1.230 px; pelo item 6 do contrato, a tabela rola dentro da caixa e a página não. "1º uso" continua logo depois do insumo (v3.8).

## Limites
- A árvore da etapa 4 (operação › atividade › cultivo › configuração) fica numa coluna: cada linha é uma entidade do seu nível (exceção do item 7). O cultivo "T1-A · Soja 58 W" continua como rótulo da ocorrência, com Talhão em coluna própria para filtrar.
- A faixa de plantio do talhão dividido ("15/10 a 25/10/2026") é resumo do grupo.
- O texto de situação "Complemento: +X un" mantém a quantidade do complemento.
- Ficam para os próximos incrementos: etapa 5 (matriz recurso × mês) e as demais grades suspeitas do menu (Estoque, Compras, Manutenção, Cadastros, Irrigação).
