# V58 · composição, auditoria das tarefas e bateria completa

Autor e integrador: Claude. Revisor: Codex (regime rápido do protótipo, AGENTS §3.5; a revisão não bloqueia a publicação). Base: v57 publicada `3a76f79`. Dados sintéticos.

## O que entra
| Item | Origem | Testes de impacto (executados) |
|---|---|---|
| Gravação estrita do cenário | `fd0b1c4` (Codex 6150155986) | `cen_grava_test` 10/10 |
| INTEL-01: Inteligência de vendas e de compras (pedido do proprietário, 13/10) | `3574d9d` · `docs/inteligencia/INTEL-01.md` | `inteligencia_unit` 22/22, `inteligencia_nav` 17/17, `comercial_unit` 114/114 |
| Planejar safra sem caixas de seleção nos cultivos (pedido do proprietário, 13/10) | `3574d9d` | `ocupacao` 65/65, `saf_revisao` 42/42, `saf_operacoes` 87/87, `acao_unica` 10/10, `partest` 50/50 |
| Menu Manutenção: troca de visão não se perde com o painel da OM aberto (defeito da v57) | `3574d9d` | `ma_menu` 6/6. Contraprova na v57: 2 de 8 trocas perdidas |
| TABR-CTX-02 (aceito pelo Codex): o que faltava na v57 era o produto do `438abbb` (menu da coluna de capacidade só com a grandeza em vigor; foco do × da Classe só pelo teclado) e os testes C17b e C19b. O `irrColsFaz` já estava publicado (correção 6152345013 no PR #47) | `b3db295`, `d1f6dca`, `4f97d50` (de `c72e0b8`, `438abbb`, `97b9278`) | na bateria |
| PRs #57 e #58 do Codex (CONTROLE-02 F2): núcleo, consulta e comando, dormentes | merge `d81eb22` | `plano_referencia_unit` 41/41, `comando` 14/14 |
| Planejar safra, etapa 3: o Total soma Área trabalhada (ha-op), Horas-conjunto, Custo R$/ha e a coluna nova **Custo total** (pedido do proprietário, 13/10) | este commit | `saf_totais_test` 11/11 (oráculo em Decimal; contraprova na montagem anterior: reprova), `saf_operacoes` 87/87, `tabelas_saf` 24/24, `rend_multiconjuntos` 18/18, `saf_capacidade_simetrica` 38/38, `ocupacao` 65/65, `saf_revisao` 42/42, `partest` 50/50, `saf_c01` 68/68, `saf_cmp_continuidade` 31/31 |

**Conta do Total da etapa 3** (uma fonte só, ENG-011):
- **Custo total** = Σ custo de máquinas e pessoas das ocorrências; é o mesmo "Custo de operação" do topo.
- **Área trabalhada** = Σ ha-op, em que cada passada conta.
- **Custo R$/ha** = custo ÷ hectares dos talhões, com cada talhão contado uma vez: a mesma conta do Resumo da safra (`areaFisica`, em `safra.js`). Somar os R$/ha das linhas daria outro número, porque as operações cobrem áreas diferentes (soja × café).
- Com ocorrência pendente ou tarifa desconhecida, o R$/ha do Total mostra "parcial", como no Resumo.
- O Total segue a busca e os filtros da grade.
- A coluna nova alarga a grade: em 1440 px ela rola na horizontal (1.227 px para 1.116 visíveis), com a 1ª coluna presa, como já acontecia em 1024 px.

Vermelhos antigos corrigidos nesta versão: ver `bateria/vermelhos.md` §1 e §2.

## Fica para a v59 (não entra aqui)
- **UNID-PROD `9a0cd26` e VISOES-1 `2d40d0c`.** Partem de uma base anterior à v56 (`0139898`). A junção com a v58 deu 30 arquivos em conflito. Vão por rebase cuidadoso sobre a v58, com bateria própria.
- **Adaptador de impedimentos e AL-18 real**, para ligar a publicação da referência técnica. Mapa no PR #58 (6152055144).

## Auditoria das tarefas (AUDIT-TAREFAS-20261013-01, PR #47 6151725314)
**Método:**
- diário dos 85 fluxos de agentes da sessão;
- conteúdo de cada frente na ponta publicada (linhas adicionadas e marcadores);
- estado dos PRs.

**Achados:**
- 50 fluxos pararam no meio, quase todos no fim da cota.
- Corrigido depois (PR #47, 6152345013): "irrColsFaz ausente" foi erro meu de caminho. Do TABR-CTX-02, faltava só o produto do `438abbb` e dois testes. Proporção de linhas prova presença de código, não conclusão funcional.
- Ficaram pela metade sem refazer:
  - a lente de regressão da v56, que falhou em 3 execuções, e a lente da composição v55;
  - a composição da v57, que só levou a CONF;
  - o parecer de 09/10, que estava só em armazenamento efêmero.
- O parecer agora está versionado em `docs/auditoria/parecer-0910/`, com a triagem dos 38 S2: 9 cobertos, 6 parciais, 3 só especificados e 20 sem frente, com as frentes propostas.
- A bateria completa abaixo substitui a lente de regressão que faltou.

## Bateria completa (executada nesta candidata)
Saída bruta: `bateria/_resumo.txt` (uma linha por teste: código de saída, tempo e resultado). Classificação de cada vermelho: `bateria/vermelhos.md`.
