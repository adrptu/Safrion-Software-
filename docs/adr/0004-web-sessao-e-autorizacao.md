# ADR 0004: Aplicação web da F0-c — um caminho de comando, sessão no servidor e autorização por matriz

- **Situação:** proposta
- **Data:** 2026-09-27
- **Autor:** Claude Code
- **Revisores:** Codex e Gemini (validação tripla, protocolo v4.1)
- **Requisitos do PRD afetados:** 8.2.1, 12.1, 23.3, 23.4, 73.3; ENG-011, ENG-014, ENG-015, ENG-021, ENG-042, ENG-043, ENG-045, ENG-081; NFR-03, NFR-09
- **Depende de:** ADR 0001 (Next.js/React), ADR 0003 (SQL explícito), F0-b1 `2d085d5` e F0-b2 `24bef1c`. **O login da homologação não é decidido aqui:** é o passo 3 do plano R-006, com o Codex como autor. Preferência registrada: OIDC com a conta Google do Adrianus, troca de papel de teste só na homologação, nenhuma senha em mensagem, seed ou repositório.

## Contexto
A F0-c entrega a primeira tela de verdade (plano R-006, passo 8):
- casca web com os tokens do design system e menu só com Estoque e Cadastros;
- login, com autorização no servidor;
- página `/saude`;
- `pnpm demo:reset` com dados fictícios, conferindo a identidade do ambiente.

Três decisões precisam valer desde já, porque são caras de mudar depois: por onde passam os comandos, onde vive a sessão e quem decide a permissão.

## Decisão

1. **Um caminho só para comandos: rota HTTP explícita.** Todo comando entra por `POST /api/v1/comandos/{commandType}` (Route Handler do Next.js):
   - o corpo é validado pelo contrato `EsquemaPedidoComando` e pelo esquema dos dados do comando;
   - a execução passa pelo envelope `executarComando`, e a resposta sai como `EsquemaRecibo`, ou `respostaDeErro` com a mesma correlação;
   - **Server Actions não fazem mutação.** O app de campo offline (PWA, F5) vai reenviar a mesma intenção pela fila local. Ele precisa de um endpoint estável, com a chave de idempotência, igual ao da web, e não de uma função presa ao React;
   - leitura pode usar componentes de servidor, sempre pela mesma camada de autorização;
   - regra de negócio fica no domínio e no envelope (ENG-011); a rota só traduz o HTTP.
2. **Organização e ator vêm da sessão, nunca do corpo** (ENG-021). O contrato estrito já recusa `organizationId`, `actorId` e `initiatorKind` no pedido (F0-b2). A rota monta a intenção com a organização e o ator da sessão validada, `initiatorKind` = `web` e a correlação do cabeçalho `X-Correlation-Id`, quando válida, ou gerada no servidor.
3. **Sessão no servidor, revogável** (ENG-042).
   - Migração nova: sessão com identificador aleatório (só o hash é guardado), usuário, organização, papel ativo, criação, expiração e revogação; e vínculo entre identidade externa e usuário (provedor, sujeito).
   - Cookie `HttpOnly`, `Secure` e `SameSite=Lax`, sem dado pessoal.
   - Toda requisição relê a sessão no banco. Revogar tem efeito na próxima requisição, e trocar de papel cria sessão nova.
4. **Autorização por matriz, negando por padrão** (ENG-043; NFR-03).
   - Um módulo no servidor decide pela função, pelo objeto, pela ação e pela organização: papel → comandos e leituras permitidos.
   - Ação fora da matriz é negada. Esconder o botão na tela é conveniência, não controle: a mesma matriz responde à tela e à API.
   - A matriz é testada de forma automática: cada papel × cada comando, e acesso horizontal a outra organização.
   - O RLS da F0-b é a segunda barreira, não a primeira.
5. **Provedor de identidade atrás de uma interface.**
   - O provedor real (OIDC, passo 3) implementa `iniciar`, `concluir` e `revogar`.
   - Para DEV e para os testes ponta a ponta locais existe um **provedor de desenvolvimento**, com usuários fictícios. Ele só liga com trava dupla, e falha fechada se qualquer uma faltar: variável de ambiente `SAFRION_AMBIENTE=dev` **e** a identidade gravada no próprio banco dizendo `dev`.
   - Em HML e produção, ele não existe: o build de HML não o registra, e um teste prova que a rota dele responde 404 fora de DEV.
   - Não é atalho de login na homologação. O E2E hospedado usa contas de teste pelo provedor real, com os segredos da CI.
6. **Proteções da web (ENG-045).**
   - Mutação só por `POST` com `Content-Type: application/json` e checagem de `Origin` igual à origem da aplicação (defesa contra CSRF, junto com `SameSite`).
   - CSP restritiva, com `frame-ancestors 'none'`.
   - Sem `dangerouslySetInnerHTML`.
   - Limite de tamanho do corpo.
7. **Log e erro (ENG-081; ENG-015).** A rota registra com o registrador da F0-b2 (`criarRegistrador`, uma linha JSON por requisição e por comando). Erro inesperado responde `FALHA_INTERNA` genérica, com a correlação. O detalhe fica só no log.
8. **Identidade do ambiente e `demo:reset` (23.4).**
   - A identidade do ambiente (`dev`, `hml` ou `prod`) é gravada no banco no provisionamento e exibida em `/saude` junto com versão, commit e migração aplicada, sem segredo.
   - `pnpm demo:reset` só roda com a identidade `dev` ou `hml`, com o nome do ambiente repetido no comando (`--confirmar hml`) e só sobre organização marcada como fictícia.
   - Com identidade `prod`, ou ausente, recusa e não toca em nada.
9. **Casca e acessibilidade (cap. 74; NFR-09).**
   - Tokens do design system como variáveis CSS e menu Estoque e Cadastros no padrão Menu → Listagem → Detalhe.
   - Teste automático com axe (WCAG 2.2 AA) nas telas da F0-c.
   - Versões de Next.js, React, Playwright e axe fixadas no PR, com a quarentena de 7 dias.

## Alternativas consideradas
| Alternativa | Por que não |
|---|---|
| Server Actions para mutação | Ficam presas ao React; o app offline precisaria de um segundo caminho de comando, com duas validações e duas chances de divergir (73.3) |
| Sessão só em JWT assinado, sem banco | Revogar não teria efeito antes da expiração (ENG-042: sessões revogáveis) |
| Biblioteca de autenticação completa agora (NextAuth/Auth.js e similares) | O provedor da HML ainda está em decisão (passo 3); a interface permite encaixar a biblioteca ou o OIDC direto depois, sem mudar rota nem matriz |
| Autorização só pelo RLS | O RLS isola organização, não decide ação por papel (gerente × almoxarife); a ENG-043 exige a matriz por ação |
| Atalho de login para testes na HML | Enfraquece a autenticação do ambiente que o Adrianus usa; a verificação hospedada usa contas de teste reais (acordo do Codex, mensagem 83) |

## Consequências
- Web e app offline compartilham o mesmo endpoint, contrato, envelope e recibo, e o reenvio offline é o mesmo comando.
- A F0-c ganha uma migração (sessão e vínculo de identidade), com os mesmos testes de RLS e imutabilidade da F0-b.
- O provedor OIDC entra num PR próprio quando o passo 3 fechar; até lá, DEV e a CI usam o provedor de desenvolvimento, com trava dupla.

## Verificação (aceites da F0-c, plano R-006 passo 8)
- `pnpm test:e2e` (Playwright, banco real na CI):
  - o almoxarife entra e vê Estoque;
  - o gerente não vê "Receber", e a API nega o comando com 403;
  - outra organização não vê o lote, nem por URL nem pela API (404 como inexistente);
  - axe sem violação AA;
  - `demo:reset` recusado fora de DEV e HML.
- Matriz de autorização testada por papel e comando, com a negação por padrão provada por um comando fora da matriz.
- Provedor de desenvolvimento: a rota responde 404 com `SAFRION_AMBIENTE` diferente de `dev` ou com a identidade do banco diferente de `dev`.
- Sessão: expirada e revogada são recusadas na requisição seguinte; troca de papel cria sessão nova.
- `organizationId` no corpo é recusado pelo contrato, e uma sessão de A não executa comando em lote de B.
