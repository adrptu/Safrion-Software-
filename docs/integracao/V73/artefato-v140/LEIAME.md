# Artefato v140 (versão 152, 19/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm
- **Versão:** 152 (`1792379001-2aca`), um lote com 4 páginas: IC, IN-04, IV e PG.
- **Fonte:** `1802dec2` em `claude/v44-v135-osagrupa`.
- **Pareceres do Claude:** PR #124 em 6258694829 e PR #126 em 6258723545, os dois com integração e ajuste de executor ou oráculo do integrador.

## O que mudou
- **PR #124 (EX-53 F1c, Codex):** sem meta configurada, a cor de desempenho sai em dois lugares.
  - **Mapa › Custos (Realizado × previsto):** sai a régua fixa de 0,5% e 10%. O talhão mostra o valor e a diferença, e a legenda diz "Meta não configurada".
  - **Inteligência de vendas e de compras:** sai o alerta fixo de ±5%. "Abaixo/acima da referência" é só a diferença, com o mesmo número no selo e no indicador.
- **PR #126 (EX-53 M5, Codex):** o Painel › Manutenção ganha o cartão "Cumprimento de preventiva". A base são as preventivas com vencimento original nos últimos 12 meses, contando as vencidas abertas e as sem ordem. Na semente: 0% (0 de 3).

## Como conferir
1. **Painel › Manutenção › Ordens de manutenção:** o cartão "Cumprimento de preventiva" aparece em cinza, com o período e "Meta não configurada".
2. **Comercial › Inteligência de vendas:** o selo e o indicador "Vendas abaixo da referência" dizem o mesmo (1, Mamão −1,6%).

## Conferência (executada)
- **Build limpo:** o build do `1802dec2` é idêntico ao render testado (0 diferenças).
- **Diferença para a v139:** as 4 páginas acima, comparadas com o build limpo da v139 publicada.
- **Leitura de volta:** as 4 páginas da versão 152 são idênticas por sha256 ao espelho e ao build limpo (`sha256.txt`).
- **Testes:** em `../pr124/` e `../pr126/`.
