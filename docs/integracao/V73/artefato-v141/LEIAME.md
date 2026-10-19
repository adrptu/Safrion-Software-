# Artefato v141 (versão 153, 19/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm
- **Versão:** 153 (`1792380971-b127`), um lote com 15 páginas: MA, PG, CMP, SU-01 e as 11 telas do app de campo (MB-*). Todas carregam o código da Manutenção.
- **Fonte:** `3389c1c4` em `claude/v44-v135-osagrupa`.
- **PR #128:** autoria do Claude, com parecer favorável do Codex (review 5566621657) e integração do Codex.

## O que mudou
- **Manutenção › ativo › Custo e desempenho › "Cumprimento de preventiva":** passa a usar a mesma regra do cartão do Painel (KPI-PCM-05).
  - A base são as preventivas do ativo com vencimento original no período, e inclui as vencidas em aberto e as vencidas sem ordem.
  - Mostra "k de n (p %) · período" ou "sem base no período".
  - Antes, a tela contava só as encerradas de todo o histórico, e o ativo atrasado aparecia "não calculável".
- **Demais 14 páginas:** só o código compartilhado (`manCumprimento` com filtro por ativo). Não há mudança de tela.

## Como conferir
1. Abra **Manutenção › Ativos**, depois o "Pulverizador PJ-3030" e o bloco **Custo e desempenho**. Deve aparecer "Cumprimento de preventiva: 0 de 1 (0 %) · set/2026", porque a preventiva venceu e a ordem está em aberto. No "Trator 03" e na "Plantadeira 24 linhas" aparece o mesmo, porque a preventiva venceu sem ordem.
2. Um ativo sem preventiva vencida no mês mostra "sem base no período".

## Conferência (executada)
- **Build limpo:** o build do `3389c1c4` é idêntico ao render testado (179 arquivos, 0 diferenças).
- **Diferença para a v140:** as 15 páginas acima, comparadas com o build limpo da v140 publicada. Nas 14 fora do MA, a diferença é só a função compartilhada.
- **Leitura de volta:** as 15 páginas da versão 153 são idênticas ao build limpo por sha256 (`sha256.txt`).
- **Testes:** em `../ex53-ma-cumpr/`.
