# Dados pessoais na HML

Inventário do que a homologação trata de dado pessoal: onde fica, para quê, quem acessa, por quanto tempo e como sai. Vale antes do 1º testador de fora (roteiro E21). Levantado em 29/09/2026 no código da `main`; nada foi implantado ainda, então os prazos são os configurados, não os observados.

**Quem é afetado:** os testadores (identidade do provedor OIDC e dados de acesso), o Adrianus como operador (e-mail em IAM, plan e state) e a conta Google dos agentes, se existir. Os usuários da demonstração são fictícios, mas a conta de demonstração não elimina o tratamento: o `subject` real de quem entra fica ligado a eles.

## Inventário

| Dado | Onde | Para quê | Quem acessa | Retenção hoje | Como sai |
|---|---|---|---|---|---|
| `issuer` e `subject` do provedor (identificador estável da pessoa no Google) | `app.identity_link`, `app.session`, `app.login_continuation`, `app.access_request`, `app.identity_link_event` | Ligar o login à pessoa e à organização; auditar concessão e revogação | Web (`app_runtime`), jobs de preparo e vínculo (`migrator`/`postgres`), quem restaura backup | Vínculo: até a revogação. Sessão: **sem limpeza** (vencidas e revogadas ficam). Continuação de login: apagada no login seguinte depois de vencer. Pedido: 24 h vivo; consumido, 30 dias. Evento de vínculo: **imutável, sem prazo** | Revogar pelo job `safrion-vinculo` apaga o vínculo e encerra as sessões; o evento e as sessões antigas ficam |
| Código de referência do pedido de acesso | Na tela da pessoa; no banco só o SHA-256 (`app.access_request`); em texto no segredo `hml-vinculo-pedido`, enquanto o pedido espera o job | Conferir o pedido pelo administrador | Administrador; job de vínculo (`sa-preparo`) | Versão do segredo destruída logo depois do job, sem adiamento; pedido inválido fica desativado até o dono destruir | `gcloud secrets versions destroy` pelo dono |
| `responsible` e `database_user` do vínculo | `app.identity_link_event` (os dois) e `app.vinculo_pedido_recibo` (só `database_user`) | Saber quem autorizou e por qual conexão | Mesmos do banco | Imutáveis (gatilho contra alteração, apagamento e `TRUNCATE` no recibo), sem prazo | Não saem sem desligar o gatilho (decisão abaixo) |
| E-mail e nome dos usuários da aplicação | `app.app_user` | Usuários da demonstração: nomes fixos e e-mails `@demonstracao.invalid`, fictícios | Web e jobs | Cada `demo:reset` cria uma geração nova; as antigas ficam | Não é dado real; usuário real exigiria entrada própria aqui |
| E-mail do operador (`user:` do Adrianus) | Variável `operador` do bootstrap e do `hml/`; plan, state (`<projeto>-tfstate-*`), JSON privado da fase 1 e IAM do projeto | Dar ao operador os papéis mínimos (logs, jobs) | Dono do projeto; `sa-infra-github` no state da HML | State versionado (11 versões anteriores); planos privados, 30 dias | Trocar o operador e aplicar; versões antigas expiram pela regra do bucket |
| E-mail da conta dos agentes | Variável `agentes` do bootstrap; state e IAM da `sa-agentes-leitura` | Personificação somente leitura | Dono do projeto | Enquanto a conta existir | Esvaziar a variável e aplicar |
| Grupo dos testadores | Variável `iap_permitidos` (`group:`); a lista de membros fica no Google Groups, fora do Terraform | Liberar a URL pelo IAP | Dono do grupo (Adrianus) | Enquanto a pessoa estiver no grupo | Tirar do grupo; sem apply |
| E-mail do testador no cabeçalho do IAP | Cabeçalho da requisição que o IAP injeta | Nenhum: dos cabeçalhos, a web só lê o de cookie, e não registra nenhum | Ninguém guarda | Não é guardado | — |
| IP e navegador (user agent) | Log de requisição do Cloud Run (plataforma), no Cloud Logging do projeto | Diagnóstico da plataforma | Dono do projeto; `sa-agentes-leitura` (`logging.viewer`), isto é, **os agentes** | Bucket `_Default` do Logging: 30 dias, o padrão (a confirmar na HML) | Expira sozinho; não há apagamento seletivo |
| Log da aplicação | stdout da web e dos jobs, no Cloud Logging | Diagnóstico com `correlation_id` e `usuario_id` (UUID) | Os mesmos do log de requisição | Mesmo bucket | Expira sozinho |
| Backups e PITR | Cloud SQL, em São Paulo | Recuperação (PRD 30.5) | Dono; `sa-infra-github` (`cloudsql.admin`) | 35 backups retidos e 7 dias de PITR: a identidade revogada ainda existe neles por esse tempo; mantidos se a instância for apagada | Expiram pela retenção |

O registrador da aplicação mascara chaves sensíveis (`e-mail`, `token`, `cookie`, `senha` e outras) em qualquer profundidade (`packages/contracts/src/log.ts`). A prova de que nenhum evento leva e-mail, `subject`, código, token, cookie ou IP é o teste do E19, ainda a fazer.

## Decisões do Adrianus

1. **Base legal** para tratar a identidade OIDC e o IP dos testadores (por exemplo, consentimento no convite ou execução do acordo de teste). Sem ela, não entra testador de fora.
2. **Retenção:** das sessões vencidas e revogadas (hoje ficam para sempre; sugestão técnica: apagar 30 dias depois de vencer), do evento de vínculo e do recibo da fila, imutáveis (hoje sem prazo; sugestão: manter enquanto durar a HML e apagar junto com ela) e dos logs (30 dias do padrão).
3. **Aviso aos testadores:** o que se guarda e por quanto tempo, incluindo que os agentes de IA leem os logs de requisição.

Até essas decisões, nada muda no código: são prazos e textos, não travas.

## Conferência automática

`tools/docs/checar_docs.py` roda `tools/docs/dados_pessoais.py`, que acha nas migrações toda coluna com `email`, `subject`, `ip`, `user_agent`, `responsible` ou `database_user` no nome, e no Terraform toda variável com `user:`, `group:` ou `e-mail`. Cada uma precisa estar na lista abaixo; item da lista que não existe mais também falha. Coluna ou variável nova com dado pessoal entra aqui no mesmo PR.

- `app.app_user.email`
- `app.app_user.name`
- `app.identity_link.subject`
- `app.session.subject`
- `app.login_continuation.subject`
- `app.access_request.subject`
- `app.identity_link_event.subject`
- `app.identity_link_event.responsible`
- `app.identity_link_event.database_user`
- `app.vinculo_pedido_recibo.database_user`
- `tf:bootstrap.operador`
- `tf:bootstrap.agentes`
- `tf:hml.operador`
- `tf:hml.iap_permitidos`
