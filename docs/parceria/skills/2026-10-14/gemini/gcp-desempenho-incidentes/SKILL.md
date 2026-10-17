---
name: gcp-desempenho-incidentes
description: Analise lentidão, indisponibilidade e recuperação no Safrion a partir de evidências, propondo investigação e mitigação compatíveis com dados, versões e aprovações.
---

# Desempenho e incidentes

## Retomada sem repetição cega

Identifique executor local/remoto e distinga timeout de transporte, cota/permissão, falha de ferramenta, relato e prova. Antes de reenviar mutação incerta, peça readback do estado/recibo. Duas falhas pela mesma causa exigem outra hipótese/abordagem ou bloqueio com gatilho. Preserve rascunhos, dados e brutos; verificação encerrada só reabre por novo indício. Reteste a jornada e o delta afetados, reutilizando provas válidas.


Comece pelo impacto no usuário, início/duração, ambiente/versão e mudanças recentes. Separe fato observado, hipótese e causa comprovada. Correlacione latência p95/p99, erros e volume com traces, consultas lentas, pool de conexões e saturação disponíveis; média isolada não representa a experiência.

Proponha a menor próxima verificação que diferencia hipóteses. Sem logs/métricas, formule o plano sem alegar inspeção. Evite reinícios e aumentos de capacidade em sequência sem diagnóstico ou critério de parada. Não atribua correção a uma mudança só porque ocorreu antes da melhora.

Mitigação deve indicar pré-condição, risco, responsável, teste de sucesso e interrupção. Rollback de aplicação precisa ser compatível com migrações e dados; não apagar fatos, reaplicar comandos não idempotentes nem restaurar banco sobre gravações válidas sem plano específico. Em produção, só recomendar execução conforme runbook previamente autorizado ou aprovação concreta disponível; não simular autorização do proprietário.

Depois da mitigação, conferir a jornada afetada, integridade e duplicidade, filas/pendências e regressão pertinente. Backup concluído não prova restauração; recuperação exige medir perda de dados e tempo. SLO, RPO e RTO vêm do requisito ou de hipótese explicitamente identificada. Monitoramento e conversa por API não equivalem a plantão humano ou atuação 24×7.

Para desempenho, compare antes/depois com mesma carga e cenário. Índice, cache e escala devem responder a um gargalo ou requisito demonstrado. Proponha teste proporcional, com dados sintéticos e ambiente indicado; não sugerir carga destrutiva em produção por conveniência.

Bases: dev-infra e dev-testes. Fontes consultadas em 27/09/2026: https://docs.cloud.google.com/architecture/framework/reliability e https://docs.cloud.google.com/architecture/framework/performance-optimization .
