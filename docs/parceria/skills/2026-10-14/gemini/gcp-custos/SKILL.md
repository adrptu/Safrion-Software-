---
name: gcp-custos
description: Estime e revise custos do Google Cloud e da IA no Safrion usando consumo, preços datados e cenários explícitos, preservando os requisitos de segurança e recuperação.
---

# Custos verificáveis

## Custo da decisão e limites de execução

Use a autorização vigente por ambiente, preservando sua referência e exclusões; não duplique valores de orçamento mutáveis nesta skill. Consulta adicional ao modelo precisa resolver decisão material, não repetir parecer por rotina. Inclua tokens, execução e custos indiretos pertinentes e diferencie limite do adaptador, cota técnica, alerta e cobrança possível. Prontidão comercial e política de mídia ficam nas fontes de negócio; custo técnico baixo não libera campanha.


Diferencie fatura observada, consumo medido, estimativa e hipótese. Use serviço/SKU, região, unidade, quantidade, período, preço e data. Sem preço atual fornecido ou verificável, mostre a fórmula e as variáveis faltantes; não invente uma cotação.

Inclua componentes materiais: processamento e tempo ocioso mínimo, banco/armazenamento, backup, rede/saída, logs, licenças e tokens de IA. Não some dólares e reais, mensal e horário, GB e GiB sem explicitar conversão. Indique impostos, câmbio, créditos e descontos como aplicáveis ou desconhecidos. Crédito promocional não é custo sustentável.

Priorize desperdício comprovado e configuração reversível. Compare economia esperada com impacto em latência, disponibilidade, perda de trabalho e esforço operacional. Instância Spot/preemptível exige tolerância a interrupção; escala a zero exige tolerância a inicialização; compromisso de longo prazo exige base de consumo e autorização de gasto. Não remover backup ou isolamento para caber numa estimativa.

Orçamento/alerta de faturamento não é limite rígido nem autorização de cobrança. Uma estimativa pequena não prova viabilidade nem autorização: confira o orçamento e o escopo já autorizados, sem pedir aprovação de novo quando a execução estiver coberta. Quotas e limites locais também não garantem teto financeiro global. Recomende observar custo por tarefa e por ambiente; apresente no máximo as mudanças de maior valor para a pergunta.

Para uma conta de tokens, mostre a aritmética e solicite que o chamador a confira de forma determinística. Não apresente o cálculo do modelo como validação independente. Entregue premissas, total ou intervalo, risco e próxima medição.

Base: dev-infra. Fontes consultadas em 27/09/2026: https://docs.cloud.google.com/architecture/framework/cost-optimization e https://docs.cloud.google.com/billing/docs/how-to/budgets .
