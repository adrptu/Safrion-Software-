# Artefato v143 (versão 157, 19/10/2026)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm
- **Versão:** 157 (`1792388687-4229`), com uma página, o Painel (`PG.dc.html`).
- **Fonte:** `883f4d70` em `claude/v44-v135-osagrupa`. É o PR #131 (Alavancas com meta), de autoria do Claude e integrado pelo Codex com o parecer `5567333255`, sem achados das revisões automáticas.

## O que mudou
- **Painel:** com a meta gravada em Configurações › Metas e limites, as Alavancas do resultado ("Custo da execução" e "Preço médio vendido") e os cartões de custo (Agrícola) e de preço médio (Comercial) mostram a cor e o resultado da meta: "Meta atendida", "Atenção à meta" ou "Fora da meta".
- **Contas:** são as mesmas do Mapa › Custos e da Inteligência de vendas.
- **Sem meta:** tudo continua cinza, com o aviso uma vez só no título, dizendo qual meta falta.

## Como conferir
1. Em **Configurações › Metas e limites**, grave "Custo realizado × previsto da execução" com 5 % e atenção de 10 %. Grave também "Preço de venda × referência" com 0 % e atenção de −2 %.
2. Abra o **Painel**. Nas Alavancas, o Mamão de Lagoa Grande fica verde no custo (0,0 %, "Meta atendida") e amarelo no preço (−1,6 %, "Atenção à meta"). A Soja, parcial, e o Café, sem referência, ficam cinza.

## Conferência (executada)
- **Diferença para a v142:** só o `PG.dc.html`, comparado com o build limpo da v142 publicada.
- **Página composta (Alavancas + M7a), testada no build limpo do `883f4d70`:**
  - `ex53_alav_meta` 5/5, `ma_backlog` 5/5, `painel03` 54/54;
  - `ex53_metas` PASS, `man_backlog_unit` 16/16.
  - Brutos nesta pasta.
- **Leitura de volta:** o `PG.dc.html` da versão 157 é idêntico ao build limpo por sha256 (`sha256.txt`).
