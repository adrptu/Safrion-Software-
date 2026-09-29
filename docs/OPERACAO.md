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
- `DATABASE_URL` (web e `demo-reset`) é `postgresql://app_runtime@/safrion_hml`, e `SAFRION_ADMIN_URL` (preparo e vínculo) é `postgresql://postgres@/postgres`: sem host e sem senha;
- `PGPASSWORD` vem do Secret Manager, em versão fixa;
- **o operador não conecta mais ao banco da HML pelo notebook.** Sem IP público, o Auth Proxy local não tem caminho, e o Cloud Shell não alcança IP privado;
- por isso, em HML, a concessão e a revogação de vínculo passam pelo job `safrion-vinculo` (abaixo). A rotação de senhas fica **a definir**: depende de subcomandos de rotação, entrega à parte.

Login em HML (adaptador OIDC do Codex, ligado pela casca):
- o callback a cadastrar no provedor é `${SAFRION_ORIGEM}/entrar/retorno`; ele nunca vem da requisição;
- a descoberta acontece no primeiro login e vale para o processo inteiro; se falhar, o próximo login tenta de novo, sem reiniciar;
- sem as três variáveis, ou com configuração inválida, `/entrar` mostra "acesso indisponível". Com o provedor fora do ar, mostra "o serviço de acesso não respondeu";
- no log, `login.recusado` traz o motivo como código: `SEM_CONFIGURACAO`, `CONFIGURACAO_INVALIDA` ou `DESCOBERTA_FALHOU`. Nenhum segredo, código ou token é registrado;
- só entra quem tem vínculo explícito entre issuer + subject e um usuário da organização. O e-mail nunca vincula.

**Conceder acesso em HML** (ADR 0004 §11; job `safrion-vinculo`, R-006 3c; especificado, nada implantado):
1. A pessoa entra pelo provedor. Sem vínculo, a tela mostra um código de referência, válido por 24 h. Um login novo troca o código.
2. Ela passa o código ao administrador.
3. **O código não prova quem é a pessoa.** O administrador confirma quem pediu por um canal autenticado independente, e confere organização, usuário e papel.
   Os ids vêm da última saída do `demo:reset`: `organizacao` e, em `usuarios`, o `usuario` de cada `papel`. Na HML, estão no log da execução do job `safrion-demo-reset`. São ids de usuários fictícios, não dado pessoal.
4. O administrador grava o pedido no segredo `hml-vinculo-pedido` e executa o job, no terminal dele ou no Cloud Shell (que aqui só chama APIs), com o gcloud na conta do operador e no projeto da HML:
   ```sh
   read -rs CODIGO
   PEDIDO_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
   printf '{"pedido_id":"%s","acao":"conceder","organizacao":"%s","usuario":"%s","responsavel":"%s","motivo":"%s","codigo":"%s"}' \
     "$PEDIDO_ID" '<organizacao>' '<usuario>' '<quem autorizou>' '<motivo curto>' "$CODIGO" \
     | gcloud secrets versions add hml-vinculo-pedido --data-file=-
   unset CODIGO
   gcloud run jobs execute safrion-vinculo --region southamerica-east1
   ```
   - **O código nunca vai para argumento de programa.** O `read -rs` o lê sem eco e fora do histórico (nunca `export`), o `printf` é do próprio shell, e o gcloud lê o pedido da entrada padrão.
   - Cada pedido tem um `pedido_id` novo, do `uuidgen`.
   - Nada de comentário `#` nas linhas do bloco: o zsh interativo, por padrão, não aceita comentário (`interactivecomments` desligado), o `#` vira comando e o `PEDIDO_ID` sai vazio.
   - `responsavel` é um identificador de quem autorizou, não o nome. Em `responsavel` e `motivo`, nada de aspas nem barra invertida: o JSON quebrado ou com chave repetida sai `PEDIDO_INVALIDO`.
   - O job roda sem overrides (`--args`, `--update-env-vars`), que o operador nem tem permissão de usar. Execute em até 60 min depois de gravar; depois disso, o pedido sai `PEDIDO_ATRASADO`.
5. Leia o resultado no Logging da execução, por exemplo `gcloud logging read 'resource.type="cloud_run_job" AND resource.labels.job_name="safrion-vinculo"' --freshness=1h`. Há uma linha por pedido, com `pedido_id`, `versao`, `resultado` e `repetido`.
   - O job grava um recibo no banco e **destrói a versão** logo depois, sem destruição adiada.
   - `PEDIDO_INVALIDO` e `PEDIDO_ID_REUTILIZADO` só **desativam** a versão, para o dono do projeto conferir e destruir: `gcloud secrets versions destroy <versao> --secret hml-vinculo-pedido`.
6. Com saída 3, execute de novo: a versão que ficou devolve o recibo já gravado (`repetido`), sem reaplicar. Conceder de novo o mesmo destino, com pedido novo, devolve `mantido`.

Para tirar o acesso, use o mesmo fluxo com `"acao":"revogar"` e sem a chave `codigo` (e sem o `read`):
```sh
printf '{"pedido_id":"%s","acao":"revogar","organizacao":"%s","usuario":"%s","responsavel":"%s","motivo":"%s"}' \
  "$(uuidgen | tr '[:upper:]' '[:lower:]')" '<organizacao>' '<usuario>' '<quem autorizou>' '<motivo curto>' \
  | gcloud secrets versions add hml-vinculo-pedido --data-file=-
gcloud run jobs execute safrion-vinculo --region southamerica-east1
```

A revogação:
- remove **todos os vínculos desse usuário nessa organização** e as sessões dele ali;
- a próxima requisição da pessoa já é negada;
- o código antigo não reabre o acesso: vincular de novo pede um código novo.

Saída do job:
- 0: todos os pedidos concedidos, mantidos, revogados ou sem vínculo;
- 1: algum pedido recusado, com o código do motivo, ou outra execução em andamento (`OCUPADO`: execute de novo depois);
- 2: uso incorreto;
- 3: falha de infraestrutura, só com códigos. A fila para, e as versões não processadas ficam para a próxima execução.

Nenhuma saída traz código, subject, hash ou o conteúdo do pedido.

**Registro e limites:**
- a execução pode continuar até cerca de 31 s depois da última linha de resultado: é o limitador de renovação do conector do Cloud SQL encerrando (ADR 0006). O resultado e o código de saída já valem; não é travamento;
- cada concessão e cada revogação ficam gravadas em `app.identity_link_event`, sem poder ser alteradas pela aplicação, com responsável, motivo e usuário do banco;
- o `migrator` lê esse registro;
- limites de HML: até 100 pedidos pendentes e 1000 guardados;
- depois de um `demo:reset` em HML, os acessos reais à geração anterior caem, e é preciso conceder de novo;
- o recibo da fila (`app.vinculo_pedido_recibo`) recusa UPDATE, DELETE e TRUNCATE por gatilho. Não é promessa contra o dono do banco (`migrator`, ou o administrador que o assume), que pode desativar o gatilho. Sem o recibo, uma versão que ficou ENABLED seria reaplicada. Nos outros registros imutáveis (`app.identity_link_event` inclusive), o gatilho não cobre TRUNCATE, e o dono consegue esvaziá-los;
- `OCUPADO` que se repete, ou saída 3 com `55P03` (espera de trava estourada), pode ser uma trava consultiva da fila ou do pedido presa por outra sessão. Qualquer papel do banco consegue tomá-la, inclusive o `app_runtime`; não forja efeito nem recibo, só impede a fila. Diagnóstico: `pg_locks` com `locktype = 'advisory'` e a sessão dona em `pg_stat_activity`. Na HML, sem conexão do notebook ao banco, como rodar esse diagnóstico fica a definir, como a rotação de senhas;
- a `sa-preparo` tem `secretVersionManager` no `hml-vinculo-pedido`, que dá também `versions.add` e `versions.enable`. Com o `secretAccessor`, quem roda como ela (o `safrion-vinculo`, o `safrion-preparo` e a CI por override) reativa e lê uma versão desativada, que ainda tem o código, e grava pedidos. Não amplia o que ela já pode: ela lê a senha do administrador do banco.

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
