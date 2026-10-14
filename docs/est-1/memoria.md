# EST-1 — memória do disponível

Codex autor, Claude revisor/integrador. Base a8f109f29525712dfbb2972f5b43897fd9dedc67; recorte comunicado em6157749099. Produto: uma linha em areas/processo_estoque.py, sem mudança no cálculo ou estado.

A memória do item dizia `150 L − 30 L − 5 L = 25 L`, porque subtraía totais de lotes vencidos e de lote com reserva superior ao físico enquanto o motor calcula por lote e exclui vencidos. Explicação corrigida: soma do saldo livre dos lotes não vencidos; em cada lote, físico menos reservado e bloqueado, com mínimo de zero.

Cenário sintético: vencido100 sem reserva; válido40 com reserva10/quarentena5; sem validade10 com reserva20. Disponível correto0+25+0=25L. Navegador1440×900 e390×844: contraprova4/8→8/8, sem mudança nos lotes/reservas/quarentena, sem erro de execução. Primeiro ensaio clicou no expansor da linha e não abriu a memória; bruto preservado, não usado como prova do defeito. Ensaio vermelho válido abriu célula de dados e registrou a igualdade falsa nas duas larguras. Build focal Estoque/render exit0,29páginas existentes; não build integral.

Aplicado: explicação fiel ao motor no detalhe existente. Fora: fórmulas e estados do domínio, fontes do Claude. Cortado: igualdade global incorreta; nenhuma etapa/controle novo. Revisão do Claude pendente; não equivale a encerramento EST-1 ou do protótipo.

Automação existente coordenar-equipe-safrion atualizada para5min e confirmada ACTIVE, sem duplicação, com passagem imediata durante trabalho ativo. Continua execução local, dependente de aplicativo/computador disponíveis.
