# Recibo da publicação do artefato v117 (17/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm. Versão 117, ID `1792231571-ff61`, num envio só. É o estado completo.
- **Origem:** prévia `f87ac32`, montada da composição `b6d4cfa` com o MA-VINCULO (PR #101, `04c88a7`, HEAD `8bdd6c3`).
  - O #101 ainda está em revisão do Codex e não foi integrado à composição. Isso segue o regime leve do protótipo (AGENTS §3.5) e o pedido do proprietário de pôr no artefato tudo o que estava em andamento.
  - A composição `b6d4cfa` traz o PR #104 (PAINEL-FIXO-2), integrado em `d432d8b`.
- **Branch única:** `claude/prototipo-v44` = `76e9466`, com a mesma árvore de `f87ac32`.
- **Provas na prévia:**
  - `ma_vinculo_test` U A B 101/101;
  - `painel_fixo_2_test` PASS;
  - `paginas_scan` 5 ok · 0 falhas (148 páginas).
  
  As provas do #101 na recomposição estão em `ma-vinculo/recomposicao-595f14e` (8 testes verdes). As do #104 estão em `comp104/`.
- **Conferência executada:** leitura de volta da v117 com sha256, 4 de 4 iguais ao render local. As páginas foram MA, CA-02, GE-08 e PL-04.
- **Manifesto:** as 59 páginas reenviadas. As outras 89 são as da v116 (`artefato-v115/manifesto.tsv`).
- **Por que 59 páginas:** o render das telas não tocadas também muda, porque a numeração interna dos botões do motor se desloca quando um painel sai. Não há mudança de comportamento nelas.
