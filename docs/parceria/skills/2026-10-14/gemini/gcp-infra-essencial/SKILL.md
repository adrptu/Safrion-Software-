---
name: gcp-infra-essencial
description: Revise decisões de infraestrutura e acesso no Google Cloud para a fatia ativa do Safrion, com a menor solução que atende aos requisitos.
---

# Infraestrutura essencial

## Reutilizar a base comprovada

Confira executor, ambiente e versão antes de sugerir nova infraestrutura. Independência do Mac requer prova remota de aplicação/banco; agendamento local não a fornece. Reutilize autorizações e verificações equivalentes já válidas. Não reabra inspeção encerrada sem incidente ou delta novo e não altere controles para destravar ferramenta. Uma falha de transporte não é defeito da aplicação; duas falhas pela mesma causa exigem nova abordagem ou impedimento explícito.


Parta do PRD, ADR e implementação fornecidos; não substitua a stack por preferência. Identifique ambiente, fluxo crítico, dependências, carga prevista ou medida e requisitos de recuperação. Na falta de dados, declare a hipótese e a evidência que muda a decisão; não bloqueie a análise inteira por ausência de previsão exata.

- Compare a solução atual com a menor alternativa que atende à tarefa. Não acrescente Kubernetes, microserviços, cache, filas, réplicas ou múltiplas regiões sem motivo demonstrado. Backup, isolamento e integridade necessários não são supérfluos.
- Confirme endpoint, identidade efetiva, projeto, API, permissão exigida e erro completo antes de recomendar IAM. Autenticação, autorização, faturamento, cota e elegibilidade são causas diferentes. Cloud Assist, Code Assist e Gemini via Vertex são serviços distintos; não extrapole papéis de um para outro.
- Para CI e produção, prefira identidade específica, credencial temporária/federação quando suportada e escopo mínimo. Não recomendar Owner, Editor ou chave JSON persistente como correção genérica. Acesso pessoal local não vira identidade de produção. Não invente que um teste local ocorre em produção nem classifique OAuth pessoal como violação de conformidade sem requisito e contexto que sustentem isso. Controles adicionais de acesso dependem do risco demonstrado, não de serem mais sofisticados.
- Revise o plano de infraestrutura como código, separação de ambientes/segredos, custo e recuperação. Validação sintática não prova provisionamento; plan não prova apply; endpoint respondendo não prova jornada funcional.

Devolva decisão ou hipótese, evidência, risco e teste de aceite. Valores, recursos e versões atuais precisam de documentação oficial fornecida ou verificada por quem consulta; sem navegação, declare o que falta confirmar. Sua saída é consultiva: não afirma execução nem aprovação de outro agente.

Base reutilizada: skill dev-infra da equipe. Referência: https://docs.cloud.google.com/architecture/framework (consultada em 27/09/2026). Não carregue um manual inteiro para responder uma pergunta localizada.
