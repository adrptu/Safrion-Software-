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

**Imagem** (`Dockerfile` na raiz, base `node:24.21.0-bookworm-slim` fixada por digest):
- alvo padrão `web`: build standalone do Next, usuário `node`, porta `PORT` (8080), `HEALTHCHECK` em `/saude`;
- alvo `preparo`: o comando de preparo do banco, com só o pacote `@safrion/db` e as suas dependências de produção.

**Variáveis da web**, todas na execução e nunca na imagem:
- `DATABASE_URL`: papel `app_runtime`, vinda do cofre de segredos;
- `SAFRION_ORIGEM`: https;
- `SAFRION_AMBIENTE=hml`;
- `SAFRION_VERSAO` e `SAFRION_COMMIT`.

O login em HML depende do adaptador OIDC. O provedor de desenvolvimento fica fechado fora de `dev`.

**Preparo do banco** (alvo `preparo`, ou `node packages/db/dist/cli/preparar-banco.js --ambiente hml --banco <nome>` depois do build). Lê:
- `SAFRION_ADMIN_URL`: o administrador do servidor no banco `postgres`, sem superusuário no Cloud SQL;
- `SAFRION_SENHA_MIGRATOR` e `SAFRION_SENHA_APP_RUNTIME`: as mesmas senhas guardadas no cofre para o migrator e para a aplicação.

Em ordem, ele:
1. provisiona os papéis;
2. cria o banco com dono `migrator` (o administrador recebe só `SET` nesse papel, sem herança);
3. aplica as migrações;
4. grava a identidade do ambiente.

Repetir não muda nada. Produção é recusada na F0. Banco de outro dono e identidade divergente param antes de qualquer migração.

Saída:
- 0: preparado;
- 1: recusado;
- 2: uso incorreto;
- 3: falha de infraestrutura, relatada só por códigos, sem senha nem host.

**Limites conhecidos:**
- a imagem não foi construída nesta máquina, que não tem Docker. Foram verificados os passos da construção numa árvore limpa, o servidor standalone copiado para uma pasta isolada (bateria ponta a ponta completa) e o preparo a partir do pacote de produção isolado;
- a primeira construção real e a varredura da imagem ficam para a CI.
