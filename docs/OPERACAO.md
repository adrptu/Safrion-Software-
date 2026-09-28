# Operação: publicação, retorno e responsabilidades

**Situação:** não há ambiente implantado. Este guia será preenchido junto com o primeiro incremento que tiver implantação, seguindo o PRD 27 (CI/CD, publicação e migrações), 28 (infraestrutura), 29 (desempenho) e 30 (observabilidade, incidentes, backup e continuidade).

Quando houver implantação, o guia precisa ter, testados e com evidência:
- ambientes DEV, HML e PROD isolados (PRD 27.4) e quem pode publicar em cada um;
- publicação pelo workflow protegido, com aprovação registrada;
- migrações compatíveis com a versão anterior e o procedimento de retorno;
- monitoramento, alertas e quem responde (PRD 30);
- backup e restauração testados, com a data do último ensaio;
- segredos: onde ficam, quem tem acesso e como revogar (ENG-017).

Nada disso está feito. Não afirme o contrário.

## Artefato de implantação da F0-c (preparado, ainda não implantado)

Nada abaixo foi executado em nuvem. Projeto, cobrança, banco hospedado e domínio são decisões do proprietário.

**Imagem** (`Dockerfile` na raiz):
- construção em `node:24.21.0-bookworm-slim`, fixada por digest;
- execução em `gcr.io/distroless/cc-debian13:nonroot`, fixada por digest, só com o binário `node` da construção: sem shell, sem gerenciador de pacotes e sem npm, corepack ou yarn;
- alvo padrão `web`: build standalone do Next, usuário 65532, porta `PORT` (8080), `HEALTHCHECK` em `/saude`;
- alvo `preparo`: o comando de preparo do banco, com só o pacote `@safrion/db` e as suas dependências de produção, também como usuário 65532.

Sem shell na imagem, diagnóstico é por log e por `/saude`, não por `docker exec … sh`.

**Variáveis da web**, todas na execução e nunca na imagem:
- `DATABASE_URL`: papel `app_runtime`, vinda do cofre de segredos;
- `SAFRION_ORIGEM`: https;
- `SAFRION_AMBIENTE=hml`;
- `SAFRION_VERSAO` e `SAFRION_COMMIT`;
- `SAFRION_OIDC_ISSUER` (https, sem `.well-known`), `SAFRION_OIDC_CLIENT_ID` e `SAFRION_OIDC_CLIENT_SECRET`, este vindo do cofre de segredos.

**Conexão ao banco em HML** ([ADR 0006](adr/0006-rede-privada-hml.md); especificado, nada implantado):
- o banco só tem IP privado. Web e jobs chegam a ele pela VPC (Direct VPC egress), com o conector oficial em `ipType PRIVATE`, que faz o TLS;
- `SAFRION_CLOUDSQL_INSTANCIA`: nome de conexão da instância (`<projeto>:southamerica-east1:safrion-hml`), posto pelo Terraform. Sem ela (desenvolvimento e CI), vale a URL comum;
- `DATABASE_URL` (web e `demo-reset`) é `postgresql://app_runtime@/safrion_hml`, e `SAFRION_ADMIN_URL` (preparo) é `postgresql://postgres@/postgres`: sem host e sem senha;
- `PGPASSWORD` vem do Secret Manager, em versão fixa;
- **o operador não conecta mais ao banco da HML pelo notebook.** Sem IP público, o Auth Proxy local não tem caminho, e o Cloud Shell não alcança IP privado;
- por isso, em HML, a concessão e a revogação de vínculo (abaixo) e a rotação de senhas ficam **a definir**. Dependem do job `safrion-vinculo` e de subcomandos de rotação, que são entrega à parte.

Login em HML (adaptador OIDC do Codex, ligado pela casca):
- o callback a cadastrar no provedor é `${SAFRION_ORIGEM}/entrar/retorno`; ele nunca vem da requisição;
- a descoberta acontece no primeiro login e vale para o processo inteiro; se falhar, o próximo login tenta de novo, sem reiniciar;
- sem as três variáveis, ou com configuração inválida, `/entrar` mostra "acesso indisponível". Com o provedor fora do ar, mostra "o serviço de acesso não respondeu";
- no log, `login.recusado` traz o motivo como código: `SEM_CONFIGURACAO`, `CONFIGURACAO_INVALIDA` ou `DESCOBERTA_FALHOU`. Nenhum segredo, código ou token é registrado;
- só entra quem tem vínculo explícito entre issuer + subject e um usuário da organização. O e-mail nunca vincula.

**Conceder acesso em HML** (ADR 0004 §11):
1. A pessoa entra pelo provedor. Sem vínculo, a tela mostra um código de referência, válido por 24 h. Um login novo troca o código.
2. Ela passa o código ao administrador.
3. **O código não prova quem é a pessoa.** O administrador confirma quem pediu por um canal autenticado independente, e confere organização, usuário e papel.
   Os ids vêm da última saída do `demo:reset`: `organizacao` e, em `usuarios`, o `usuario` de cada `papel`. Na HML, estão no log da execução do job `safrion-demo-reset`. São ids de usuários fictícios, não dado pessoal.
4. O administrador roda o comando no alvo `preparo` da imagem, com `SAFRION_ADMIN_URL` (administrador do servidor):
   `docker run --rm -it -e SAFRION_ADMIN_URL --entrypoint node <imagem-preparo> dist/cli/vincular-identidade.js conceder --ambiente hml --banco <nome> --organizacao <id> --usuario <id> --responsavel <quem autorizou> --motivo <texto curto>`.
   **O código é pedido no terminal e não aparece na tela.** Ele também pode vir por pipe, nunca como argumento.
   Na HML, o banco só tem IP privado, e este passo fica a definir (ver "Conexão ao banco em HML").
5. Repetir o mesmo comando devolve `mantido` e não muda nada.

Para tirar o acesso, use o mesmo comando com `revogar` no lugar de `conceder`, sem código:
- ele remove **todos os vínculos desse usuário nessa organização** e as sessões dele ali;
- a próxima requisição da pessoa já é negada;
- o código antigo não reabre o acesso: vincular de novo pede um código novo.

Saída do comando:
- 0: concedido, mantido, revogado ou sem vínculo;
- 1: recusado, com o código do motivo;
- 2: uso incorreto;
- 3: falha de infraestrutura, só com códigos.

Nenhuma saída traz código, subject ou hash.

**Registro e limites:**
- cada concessão e cada revogação ficam gravadas em `app.identity_link_event`, sem poder ser alteradas pela aplicação, com responsável, motivo e usuário do banco;
- o `migrator` lê esse registro;
- limites de HML: até 100 pedidos pendentes e 1000 guardados;
- depois de um `demo:reset` em HML, os acessos reais à geração anterior caem, e é preciso conceder de novo.

O provedor de desenvolvimento fica fechado fora de `dev`.

**Preparo do banco** (alvo `preparo`, ou `node packages/db/dist/cli/preparar-banco.js --ambiente hml --banco <nome>` depois do build). Lê:
- `SAFRION_ADMIN_URL`: o administrador do servidor no banco `postgres`, sem superusuário no Cloud SQL;
- `SAFRION_SENHA_MIGRATOR` e `SAFRION_SENHA_APP_RUNTIME`: as mesmas senhas guardadas no cofre para o migrator e para a aplicação.

Primeiro confere, sem alterar nada:
1. as opções, antes de abrir conexão: produção é recusada na F0;
2. o dono do banco, se ele já existe;
3. a identidade do banco existente, lida pelo administrador ao assumir o papel `migrator` só para ler;
4. as senhas informadas dos papéis que já existem: cada uma precisa autenticar.

Só então muda, em ordem:
1. provisiona os papéis, sem trocar senha em uso;
2. cria o banco com dono `migrator` (o administrador recebe só `SET` nesse papel, sem herança);
3. aplica as migrações;
4. grava a identidade do ambiente.

Repetir não muda nada. Qualquer conferência que falhe recusa o preparo sem alterar papel, senha, banco ou migração:
- banco de outro dono: `BANCO_DE_OUTRO_DONO`;
- identidade divergente: `IDENTIDADE_DIVERGENTE`;
- administrador que não pode assumir o `migrator` num banco existente: `IDENTIDADE_NAO_VERIFICAVEL`;
- senha informada que não é a atual: `CREDENCIAL_DIVERGENTE`.

O preparo nunca troca senha. Rotação é um procedimento à parte, ainda não escrito.

Saída:
- 0: preparado;
- 1: recusado;
- 2: uso incorreto;
- 3: falha de infraestrutura, relatada só por códigos, sem senha nem host.

**Limites conhecidos:**
- a imagem não foi construída nesta máquina, que não tem Docker. Foram verificados os passos da construção numa árvore limpa, o servidor standalone copiado para uma pasta isolada (bateria ponta a ponta completa) e o preparo a partir do pacote de produção isolado;
- a construção real, as provas de execução e a varredura da imagem são da CI (`imagem.yml`), que bloqueia achados HIGH e CRITICAL, com ou sem correção disponível.
