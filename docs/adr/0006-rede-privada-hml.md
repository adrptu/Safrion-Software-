# ADR 0006: Ligar o banco da HML só por rede privada

- **Situação:** proposta
- **Data:** 2026-09-28
- **Autor:** Claude Code
- **Revisor:** Codex (pendente)
- **Requisitos do PRD afetados:** 28.1 (serviços gerenciados na HML), 27.4 (HML equivalente à produção), ENG-005 (exceções), ENG-017 (segredos), ENG-061 a ENG-064

## Contexto
O Trivy acusa o GCP-0017 (HIGH) no Cloud SQL da HML, que tinha IP público sem redes autorizadas. O check acusa IP público ligado ou rede autorizada pública. Ele lê o `ipv4_enabled` ausente ou não resolvido como `true`, então o achado só fecha com `ipv4_enabled = false` literal. O `SECURITY.md` não aceita exceção para risco real.

A comparação, com fontes e custos, está no R-006 (`docs/hml-custo-infra`, `894ef4d`, seção "GCP-0017: IP privado × concessão fora da máquina do operador"). Nada está provisionado.

## Decisão
- **Rede, no bootstrap (sessão do dono), aplicada antes da 1ª instância:**
  - VPC custom;
  - sub-rede /24 RFC 1918 em southamerica-east1, com Private Google Access e sem flow logs;
  - faixa /20 do Private Service Access (PSA) com endereço RFC 1918 explícito, sem sobrepor a sub-rede;
  - conexão PSA com `deletion_policy = "PREVENT"`.
- **Cloud SQL:**
  - `ipv4_enabled = false` literal, com `private_network` e `allocated_ip_range` vindos das saídas do bootstrap;
  - sem redes autorizadas e com `data_api_access = "DISALLOW_DATA_API"`;
  - `connector_enforcement = "REQUIRED"` e `ssl_mode = "ENCRYPTED_ONLY"`, como antes.
- **Cloud Run:** web e jobs com Direct VPC egress `PRIVATE_RANGES_ONLY`. Só destinos RFC 1918 passam pela VPC; OIDC e APIs do Google seguem direto para a internet. Sem volume `/cloudsql`.
- **Conexão:**
  - conector Node.js oficial com `ipType PRIVATE`, ligado por `SAFRION_CLOUDSQL_INSTANCIA`. Ele faz o TLS e respeita o `REQUIRED`;
  - URLs do banco sem host, senha por `PGPASSWORD`;
  - sem a variável, desenvolvimento e CI seguem com a URL comum;
  - retentativa só na abertura inicial, com prazo de 10 s por tentativa: até 4 para as opções do conector (no pior caso, 47 s) e até 6 para o `SELECT 1` (120 s). Somadas, 167 s, dentro da sonda de inicialização da web (18 × 10 s);
  - o `SELECT 1` usa clientes só da sonda, nunca o pool nem o cliente de trabalho, e cada tentativa destrói o transporte no fim ou no prazo. Assim, um banco que autentica e não responde não deixa conexão viva nem prende o encerramento (revisão do Codex, CONEXAO-01);
  - um conector novo por tentativa. O 1.12.0 guarda a carga que falhou e, fechado com ela, solta uma rejeição com a URL da API. Nos comandos, uma rejeição solta termina o processo com saída 3 e uma linha só com códigos;
  - **patch local do conector 1.12.0** (`patches/`, `patchedDependencies` no `pnpm-workspace.yaml`): a renovação do certificado que falha antes da 1ª conexão deixava promessas rejeitadas sem consumidor, que o Next imprimia com a URL da API, e depois dela o conector não renovava mais. O patch consome essas promessas, libera o ciclo que falhou e mantém o erro para quem abre a próxima conexão. Com versão nova do pacote, o pnpm recusa instalar até o patch ser revisto;
  - no pool da web, o limite de 10 s para abrir a conexão vale também para a espera por uma vaga: na HML, a requisição que espera mais que isso falha, em vez de esperar sem fim como em desenvolvimento e na CI;
  - **nunca se repete uma transação com commit incerto.**
- **Travas propostas para a CI** (o passo no `ci.yml` é do Codex; até lá, rodam só localmente): o `checar_travas.py` exige tudo isso no código e no plan (`ipv4_enabled`, `private_network`, `data_api_access`, `psc_config` e `egress`) e recusa `ignore_changes` sobre esses campos.
- **Fora desta decisão:** a concessão de vínculo em HML, que passa pelo job `safrion-vinculo` (R-006 3c; fluxo no [OPERACAO.md](../OPERACAO.md)), e a rotação de senhas no banco, que fica a definir, porque o notebook do operador deixa de alcançar o banco.

## Alternativas consideradas
| Alternativa | Por que não |
|---|---|
| Manter o IP público com exceção | O GCP-0017 continua HIGH, e a política não aceita exceção para risco real. Exigiria categoria nova no `SECURITY.md`, renovada a cada 30 dias |
| Private Service Connect | Também fecha o achado, mas o endpoint custa US$ 0,01/h (≈ US$ 7,30/mês), contra zero da conexão PSA |
| IP privado com Cloud SQL Studio (`ALLOW_DATA_API`) | Reabre o banco pela internet por `executeSql`, sem barreira de rede, e o Trivy não olha o campo. Contorna a política sem tirar o risco. Põe código ou hash no texto SQL, que um erro de sintaxe grava no `postgres.log` |

## Consequências
- **Mais fácil:** o GCP-0017 fecha sem exceção nem renovação (a confirmar pelo Trivy do revisor). Custo incremental de US$ 0,00 a 0,05/mês, só tráfego (R-006). O teto de 0,11 do R-006 somava 0,06 do segredo do job de vínculo, que fica fora desta decisão.
- **Irreversível:**
  - o IP privado não sai mais da instância, e a faixa só se atribui na criação. Por isso a rede vem antes;
  - numa instância existente, ligar o IP privado a reinicia;
  - o PSA impede apagar a rede enquanto o Cloud SQL guardar recursos nela.
- **Mais lento:** o Direct VPC pode levar 1 min ou mais para conectar na subida, e a partida a frio fica mais lenta. A sonda da web passa de 6 para 18 tentativas.
- **Conta padrão do Compute:** ligar a API do Compute cria essa conta, que pode receber Editor. O dono roda o procedimento do bootstrap depois do apply e confere a rede `default`.
- **Operação:** o operador não conecta mais ao banco da HML pelo notebook e perde o `cloudsql.client`, que servia ao Auth Proxy. A concessão de vínculo e a rotação de senhas ficam sem caminho até o job existir. Até lá, não há concessão real na HML.
- **Achados abaixo do gate:** GCP-0076 (MEDIUM) e GCP-0029 (LOW), de flow logs desligados por custo.
- **Reversão:** HML sem dado real pode ser recriada com IP público por ADR nova, instância nova e novo preparo. A rede fica até o Cloud SQL liberar a faixa.

## Verificação
- `python3 infra/terraform/checar_travas.py` e as regressões em `infra/terraform/test_checar_travas.py`, no código e no plan (`--plano`). Só depois do passo no workflow e de uma execução verde registrada elas passam a valer como trava da CI.
- Testes da conexão (`packages/db/test/conexao.test.ts`: o conector real contra uma API falsa local, a renovação que falha com o patch e a sonda com o driver `pg` real sobre um transporte PostgreSQL em memória) e da subida da web (`apps/web/test/servidor-ambiente.test.ts`).
- Trivy do revisor sobre `infra/terraform`, sem GCP-0017.
- No 1º plan e na 1ª publicação:
  - permissões da `sa-infra-github` para `private_network` e da `sa-deploy-github` para `vpc_access`;
  - `network` e `subnetwork` sem diferença permanente.
- Antes da 1ª subida, ensaio do conector `PRIVATE` com Direct VPC numa instância descartável, sem dado real (R-006).
