# Artefato v132 (versões 137 e 138, 18/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm
- **Versões:** 137 (`1792329537-6894`, lote 1, 30 páginas) e 138 (`1792329558-1f0c`, lote 2, 29 páginas).
- **Fonte:** `f6a9374a` em `claude/v44-v69-mapa` (v131 `8dcf39d4` + Q5-AMB). Render do build `SAFRION_DADOS=sintetico` desse commit.
- **O que mudou:** 59 páginas, todas as que embutem o `cenario.js`. As outras 89 páginas e os arquivos de apoio são iguais aos da v131.
- **Conteúdo:** Q5-AMB. A nota antiga sem unidade ou sem linha só baixa a linha única do pedido em que cabe; com mais de uma linha possível, a previsão sai do suprimento com aviso (`docs/integracao/V73/q5-amb/LEIAME.md`).

## Conferência (executada)

Leitura de volta da versão 138, comparada com o espelho local por sha256:

| Página | sha256 |
|---|---|
| CMP.dc.html | `8c490063e3f9c26ccb9b906e6d047d7a1be3e1e93206fe14856489b519a5cf79` |
| EST.dc.html | `ba188fe10fa240ac7aadf36efed4a00b425e7e936d65bc20f4f867c2444df88c` |
| SAF.dc.html | `43f7536508860945ba166d2219e0e8a41ab0eb7cbc942a0fb81fd38fb7dc9372` |
| OS.dc.html | `065228ef92cc494170a596c279e7056fb6fd6bead0b05c857f7dada56debc5af` |

4/4 iguais. A regra nova (`cenCompOutra`) está presente em CMP e EST.
