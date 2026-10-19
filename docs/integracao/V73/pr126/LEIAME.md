# PR #126 (EX-53 M5, Codex): revisão do Claude no navegador (19/10/2026)

- **Render testado:** a composição local `cdc1ccde` + o PR #126 `aa14a0cb`, servido de `/tmp/claude-0/f1a/tools/prototipo/v37/gen37/_render`.
- **`painel03_test`:** 54/54.
- **Prova focal (`m5_focal.log`, 1440 e 390 px e teclado):** OK.
  - O cartão "Cumprimento de preventiva" está na aba Manutenção e mostra "0% · 0 de 3 preventivas · 12 m · 23/09/2025 a 23/09/2026 · Meta não configurada", em cinza.
  - Leva a `MA.dc.html#vis=ordens` e tem dica com a fórmula.
  - Não sai da largura, e o Tab chega ao link com contorno visível.
- **`ex53_m5_cartao_test`:** PASS, depois do ajuste do executor. Antes, no Linux, o `node -e` com o prelúdio inteiro dava `OSError: [Errno 7] Argument list too long`. O ajuste do integrador passa o código por arquivo temporário; a regra e as asserções não mudaram.
- **`ex53_metas_test`:** PASS.

**Fotos (`fotos/`):** cartão a 1440 e 390 px e foco pelo teclado, conferidas.
