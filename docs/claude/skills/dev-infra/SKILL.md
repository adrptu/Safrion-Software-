---
name: dev-infra
description: Configure e revise ambientes, CI/CD, hospedagem, observabilidade e recuperação conforme risco, carga e custo. Use em fundação, deploy, segurança operacional, incidentes e backups.
---

# Infra e operação — disponibilidade e recuperação verificáveis

Escolha a menor infraestrutura que cumpra requisitos, carga e orçamento. Exemplos de provedores, versões e assets não são contratação nem receita pronta; verificar suporte e configuração antes de usar. Haver monitoramento não significa haver plantão: nomear o responsável e testar o acionamento.

## Ambientes
| Ambiente | Para quê | Regra |
|---|---|---|
| **dev** | máquina do dev | comando reproduzível sobe apenas dependências usadas; dados sintéticos realistas |
| **preview** | cada PR | URL única por PR (Vercel/Fly/Cloud Run/ArgoCD), banco efêmero ou branch (Neon); destruído no merge |
| **staging** | validar candidato | mesma versão e contratos da produção, com contas, banco, segredos e integrações isolados; dados sintéticos por padrão; escala documentada |
| **prod** | usuários | só via pipeline; ninguém faz deploy manual nem edita servidor |

Promover o mesmo artefato de homologação para produção; configurações e escala podem diferir sem comprometer os testes relevantes. Nunca compartilhar credenciais ou destinos reais por conveniência. Validar a configuração no boot.

## Hospedagem (escolher pelo tamanho, não pela moda)
1. **Serviço gerenciado** quando atende requisitos e custo total; comparar limites, recuperação, regiões e carga medida. Número de usuários, sozinho, não determina capacidade nem provedor.
2. **Kubernetes** (GKE/EKS) só com motivo: muitos serviços, requisitos de rede/compliance, time de plataforma. Nunca "para o futuro".
3. TLS e proteções de acesso desde a exposição externa; CDN, WAF e failover conforme ameaças e carga, aproveitando o provedor escolhido sem duplicar camadas.

## Infra como código
- Tudo em código versionado: Terraform/OpenTofu ou Pulumi (cloud), ou config do PaaS no repositório (`fly.toml`, `vercel.json`). Nada criado à mão no console.
- Estado remoto com lock; `plan` no PR, `apply` só do trunk com aprovação; módulos reutilizáveis; tags de custo em todo recurso.

## Containers
- [assets/Dockerfile](assets/Dockerfile): multi-stage, imagem base pequena e fixada (`node:22-alpine`/distroless), usuário não-root, só artefatos de produção, `HEALTHCHECK`, sem segredo em layer, `.dockerignore`.
- [assets/docker-compose.yml](assets/docker-compose.yml) para dev com Postgres, Redis, Mailpit e healthchecks.
- Imagens escaneadas (Trivy) no CI; SBOM gerado; assinadas (cosign) quando houver exigência.

## CI/CD — [assets/ci.yml](assets/ci.yml)
Pipeline de todo PR (< 10 min, com cache):
`install → lint + format → typecheck → testes unit (cobertura) → build → testes integração (serviços via Docker) → E2E (sharded) → segurança (gitleaks, osv-scanner, Trivy, Semgrep) → deploy preview`

Trunk (`main`): checks aplicáveis → homologação → smoke tests e validação humana exigida pelo projeto → promoção do mesmo artefato à produção → verificação pós-deploy. No Safrion, produção exige o aceite explícito do proprietário sobre a versão. Recuperação automática só por procedimento previamente autorizado e testado, compatível com migrações e dados.

Regras:
- Trunk sempre deployável; proteção de branch com PR, CI verde, revisão e sem force-push quando o serviço/plano permitir. Se indisponível, registrar a disciplina de processo e o impedimento; não declarar proteção ou CI verde sem evidência nem tratar controle manual como equivalente técnico.
- **Migrações no pipeline**, antes do deploy da nova versão, compatíveis com a versão anterior (expand/contract) — permite rollback sem reverter banco.
- Estratégia: **rolling/blue-green** por padrão; **canary** (1 % → 10 % → 100 %) com métricas em sistemas de alto tráfego; feature flags para desligar sem deploy.
- **Rollback em um comando** (redeploy da imagem anterior) testado de verdade, documentado no runbook.
- Artefato construído uma vez e promovido (mesma imagem em staging e prod); versão/commit visível em `/health`.
- Atualizações por Renovate/Dependabot conforme a política do projeto; auto-merge não é autorizado apenas por este skill.

## Segredos e acesso
- Gerenciador de segredos (cloud Secret Manager, Doppler, 1Password, Vault); injetados em runtime; rotação documentada; nunca em imagem, repositório ou log.
- **Mínimo privilégio**: IAM por serviço, sem credencial pessoal em produção, MFA obrigatório, acesso a produção auditado e temporário; SSH desabilitado ou via bastion/IAP.
- Banco não exposto à internet; rede privada entre serviços; portas mínimas; firewall.

## Observabilidade e SLOs
- **Logs** estruturados centralizados (Loki/CloudWatch/Datadog/Axiom) com retenção definida; **métricas** (Prometheus/OTel → Grafana); **traces** (OTel → Tempo/Jaeger/Datadog); **erros** (Sentry); **uptime** externo (Better Stack/UptimeRobot) em `/health` a cada minuto.
- **SLOs** por serviço: disponibilidade (ex.: 99,9 %), latência p95, taxa de erro. Alertas em **sintoma que o usuário sente** (burn rate do error budget), não em CPU. Todo alerta tem runbook e dono; alerta que não gera ação é removido.
- Dashboards: RED por serviço, saturação (pool, fila, disco), negócio (pedidos/min). Pós-deploy compara antes/depois.
- Incidente: canal, comandante, comunicação de status, **post-mortem sem culpa** em 48 h com ações (teste + correção + alerta).

## Dados: backups e recuperação
- Backups automáticos criptografados; definir frequência, PITR, retenção e cópia isolada segundo RPO/RTO, custo e obrigações do projeto, sem inventar retenção universal.
- **Restauração testada** trimestralmente (exercício real, tempo medido). Backup não testado não existe.
- **RPO/RTO** definidos e medidos em restauração; redundância/multi-AZ quando necessários para cumpri-los, com custo conhecido; réplica de leitura só com demanda.
- Objetos (uploads) em S3/GCS com versionamento e lifecycle.

## Escalabilidade
- Serviços sem depender de memória volátil para estado durável; autoscaling e cache compartilhado quando a carga justificar; não adicionar Redis só por convenção.
- Banco: pool (PgBouncer), índices (`dev-backend`), réplicas de leitura, particionamento quando tabelas > dezenas de milhões; cache para leitura quente.
- Filas para picos e trabalho assíncrono; rate limiting; CDN e cache HTTP para conteúdo público.
- **Teste de carga** (k6) em staging antes de lançar e antes de eventos; capacidade planejada com margem 2×.
- Custo monitorado com alerta de orçamento; recursos ociosos removidos; rightsizing mensal.

## Checklist de lançamento
- [ ] Pipeline completo verde; imagem promovida de staging; migração compatível; rollback testado
- [ ] TLS, domínio, rate limiting e cabeçalhos; CDN/WAF conforme arquitetura e risco
- [ ] Segredos no cofre; acesso mínimo; banco em rede privada
- [ ] `/health` e `/ready`; monitoramento externo; rastreador de erros e telemetria adotados pelo projeto recebendo dados
- [ ] SLOs e alertas com runbook e dono; dashboard pós-deploy
- [ ] Backups e recuperação necessários às metas ativos; PITR quando exigido pelo RPO; restauração testada e RPO/RTO documentados
- [ ] Teste de carga em staging dentro da meta; capacidade e estratégia de escala verificadas, autoscaling quando adotado
- [ ] Runbook: como fazer deploy, rollback, restaurar, escalar, rotacionar segredo; contatos
- [ ] Custo estimado e alerta de orçamento
