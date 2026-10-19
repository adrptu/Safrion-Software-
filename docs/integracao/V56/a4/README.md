# A4 · aprovar ajuste de inventário revalida a contagem (S2 do Estoque)

- **Base:** 90e5f67 (candidata v56). **Branch:** `claude/v44-est-a4`. **Autor:** Claude. **Revisor:** Codex.
- **Fonte:** commits b1782f9, 859fee3 e c62f9a7 (`commits.txt`); o código está em `a4_90e5f67..c62f9a7.patch` (`git diff 90e5f67..c62f9a7 -- . ':!docs'`) e entra no commit único da v56.
- **Contrato:** PR #47, comentário **6147474674** (Codex). O achado é o do comentário 6147268439.
- **Defeito:** NF de 1.200 → contagem de 1.100 (AJ-71 pendente) → OB-0113 entrega 1.169 → aprovar o AJ-71.
  - Pela tela, o físico ia de 31 para −69.
  - Pela entrada direta do motor, o físico ia para 1.100: eram 1.069 caixas inventadas, e a conservação quebrava.

## O que mudou
- `cenario.js`:
  - A contagem grava o marcador da trilha do lote (`aj.mv`) e a data e hora.
  - `cenContagemVelha`: a contagem fica desatualizada se o lote teve movimento físico ou de qualidade depois dela. Reserva, desreserva, consumo na custódia, confirmação no app e contagem sem diferença não contam.
  - `cenAjusteDecisao` é a decisão única: contado abaixo da quarentena é recusado; contado abaixo da reserva é aplicado com o alerta "Reserva sem físico", que traz dono e recuperação. A constante `CEN_AJ_ABAIXO_RESERVA` troca o alerta por recusa.
  - `cenAprovarAjuste` confere, nesta ordem, o papel, a contagem atual e a decisão, e só então aplica, uma vez.
  - `cenContar` aceita contado abaixo da reserva.
- `areas/processo_estoque.py`:
  - `estAprovar` não aplica mais a diferença sobre um físico que mudou.
  - A INV-2609 tem o marcador no início da trilha.
  - A linha da contagem desatualizada mostra o selo "Desatualizada", o motivo e só a ação Recontar.
  - O lote mostra "Reserva sem físico · X" e quem confere.

## Aceites (executado; candidata 859fee3 × base 90e5f67)
| Aceite | Teste | Candidata | 90e5f67 |
|---|---|---|---|
| Roteiro A4 (recusa atômica, AJ pendente, físico 31, custódia 1.169, depois Recontar e aprovação) | `est_a4_test.py` | verde | físico −69 |
| Entrada direta do motor primeiro | `est_a4_test.py` | verde | 1.100, conservação 4.009 × 2.840 |
| (a) conta 1.100 → reserva 1.169 → aprova; falta 69; a entrega de 1.169 é recusada | `est_a4_test.py`, `est_a4_nav_test.py` T5 | verde | sem alerta |
| (b) reserva 1.169 → conta 1.100 → aprova | `est_a4_test.py` | verde | contagem recusada |
| (c) 100 → conta 90 → entrada de 50 → recusa | `est_a4_test.py` | verde | aplica (140) |
| (d) saída e volta ao mesmo saldo → recusa | `est_a4_test.py` | verde | aplica |
| (e) laudo sem mudança física → recusa | `est_a4_test.py` | verde | aplica |
| (f) contado abaixo da quarentena → recusa sem efeito (contagem e motor) | `est_a4_test.py` | verde | o motor aplica 40 com 50 bloqueados |
| Papel inválido, envio duplo, duas contagens da mesma falta, contagem sem marcador | `est_a4_test.py` | verde | duas contagens: 1.000; sem marcador: aplica |
| Recuperação sem travar (recontagem 0 com 69 reservados) | `est_a4_test.py` | verde | recontagem recusada |
| Tela a 1440 e a 390: Desatualizada + Recontar, recusa com motivo, recontagem | `est_a4_nav_test.py` | 15/15 | 3/15 |

## Números (executado)
- Testes novos:
  - `est_a4_test.py`: **42/42** na candidata e 18/42 no 90e5f67.
  - `est_a4_nav_test.py`: **15/15** na candidata e 3/15 no 90e5f67.
- Testes existentes, na candidata 859fee3, todos verdes:
  - `esttest.py`: partes 1 a 4 OK (24/24, 23/23, 19/19, 13/13);
  - `est_fix1_test.py`: 13/13;
  - `est_fix2_test.py`: 11/11;
  - `est_cenario_test.py`: 15/15;
  - `demanda_unica_test.py`: 71 ok, 0 falhas;
  - `cmptest.py`: 98 OK, sem falhas.
- Geração e varredura: `build.py` com 0 FALHA e `varredura.py` com 145/145 páginas sem erro.

## Limites
- Os tipos de movimento que não invalidam a contagem estão numa lista. Um tipo novo invalida por padrão.
- A contagem de base INV-2609 é tratada como feita no início da demonstração. O dado sintético é coerente com o cenário inicial. Se o revisor preferir, ela pode passar a exigir recontagem.
- "Reserva sem físico" aparece no aviso e no lote. Faltam o selo "Falta insumo" na O.S. e o prazo PEND-16 (RSV-10 completo), que ficam para o software real.
