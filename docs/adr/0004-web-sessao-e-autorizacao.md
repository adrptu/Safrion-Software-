# ADR 0004: Aplicação web da F0-c — um caminho de comando, sessão no servidor e autorização por matriz

- **Situação:** contrato de tipos aceito pelo Codex em 28/09; revisão 2, com a continuação depois do callback (§5) pedida na aceitação. O §11 (vínculo de identidade em HML) foi proposto em 28/09, revisado pelo Codex e pelo Gemini, e implementado na F1 (migração `0005`)
- **Data:** 2026-09-28. A revisão 1 é de 2026-09-27 (`c02bced`).
- **Autor:** Claude Code
- **Revisores:** Codex e Gemini (validação tripla, protocolo v4.1)
  - A revisão 2 incorpora os 5 pontos da revisão do Codex com o Gemini (`outputs/revisao-f0a.md`, "Dependência de login"): LOG-ADR, SESSÃO, RESOLUÇÃO, OIDC e CORPO.
  - Incorpora também a fronteira de autoria confirmada pelo Codex (§10).
- **Requisitos do PRD afetados:** 8.2.1, 12.1, 23.3, 23.4, 73.3; ENG-011, ENG-014, ENG-015, ENG-021, ENG-042, ENG-043, ENG-045, ENG-081; NFR-03, NFR-09.
- **Depende de:**
  - ADR 0001 (Next.js/React) e ADR 0003 (SQL explícito);
  - a F0-b e a F0-b2, com as correções F0B2-01 (log sem texto livre) e A1 (papéis no Cloud SQL).

  O login da homologação é o passo 3 do plano R-006, com o Codex como autor. Este ADR fixa só o contrato entre o adaptador OIDC e o resto da aplicação.

## Contexto
A F0-c entrega a primeira tela de verdade (plano R-006, passo 8):
- casca web com os tokens do design system e menu só com Estoque e Cadastros;
- login, com autorização no servidor;
- página `/saude`;
- `pnpm demo:reset` com dados fictícios, conferindo a identidade do ambiente (já entregue na F0-c parte 1).

Três decisões precisam valer desde já, porque são caras de mudar depois: por onde passam os comandos, onde vive a sessão e quem decide a permissão.

## Decisão

1. **Um caminho só para comandos: rota HTTP explícita.** Todo comando entra por `POST /api/v1/comandos/{commandType}` (Route Handler do Next.js):
   - o corpo é validado pelo contrato `EsquemaPedidoComando` e pelo esquema dos dados do comando;
   - a execução passa pelo envelope `executarComando`, e a resposta sai como `EsquemaRecibo`, ou `respostaDeErro` com a mesma correlação;
   - **Server Actions não fazem mutação.** O app de campo offline (PWA, F5) vai reenviar a mesma intenção pela fila local. Ele precisa de um endpoint estável, com a chave de idempotência, igual ao da web;
   - leitura pode usar componentes de servidor, sempre pela mesma camada de autorização;
   - regra de negócio fica no domínio e no envelope (ENG-011); a rota só traduz o HTTP.

2. **Organização e ator vêm da sessão, nunca do corpo** (ENG-021). O contrato estrito já recusa `organizationId`, `actorId` e `initiatorKind` no pedido (F0-b2). A rota monta a intenção com a organização e o ator da sessão resolvida, `initiatorKind` = `web` e a correlação do cabeçalho `X-Correlation-Id`, quando tem formato de identificador, ou gerada no servidor.

3. **Sessão no servidor, revogável e resolvida antes do RLS** (ENG-042; pontos SESSÃO e RESOLUÇÃO).
   - O cookie leva só um identificador aleatório de 256 bits (`HttpOnly`, `Secure`, `SameSite=Lax`, sem dado pessoal). O banco guarda apenas o hash SHA-256 desse identificador.
   - A migração `0003` cria quatro tabelas:
     - `app.identity_link` (issuer, subject, usuário e organização);
     - `app.session` (hash, usuário, organização, papel ativo, criação, expiração, revogação e sessão de origem na troca de papel);
     - a transação de login do §5 (antes do callback);
     - a continuação depois do callback (§5): hash do ticket, identidade validada, destino, expiração e consumo.
   - **O `app_runtime` não tem SELECT, INSERT, UPDATE nem DELETE nessas tabelas.** Tudo passa por funções `SECURITY DEFINER` com dono próprio `NOLOGIN` (nem `migrator` nem `app_runtime`), `SET search_path` fixo, `EXECUTE` revogado de `PUBLIC` e concedido só ao `app_runtime`:
     - `resolver_sessao(hash)`: devolve usuário, organização, papel e expiração **só** de uma sessão não revogada, não expirada, cujo usuário está ativo (`app_user.active`) e ainda tem aquele papel na organização (`user_role`). Caso contrário, não devolve nada;
     - `abrir_transacao_login` e `consumir_transacao_login`: a porta do §5;
     - `abrir_continuacao(issuer, subject, destino)`, `vinculos_da_continuacao(hash)` e `concluir_continuacao(hash, organização, papel)`: a continuação do §5, **o único caminho que cria sessão**;
     - `revogar_sessao(hash)` e `trocar_papel(hash, papel)`. A troca só aceita papel vinculado, revoga a sessão antiga e devolve uma nova.
   - **Toda requisição resolve a sessão junto com o vínculo vivo.** Usuário desativado, papel removido, sessão revogada ou expirada: a próxima requisição é negada.
   - A organização só entra no contexto do RLS (`emOrganizacao`) **depois** da resolução, e a transação seguinte não herda organização da anterior (já provado na F0-b).
   - A consulta de recibo é leitura autorizada à parte, e nunca reexecuta o efeito.

4. **Autorização por matriz, negando por padrão** (ENG-043; NFR-03).
   - Um módulo no servidor decide pela função, pelo objeto, pela ação e pela organização: papel → comandos e leituras permitidos.
   - Ação fora da matriz é negada. Esconder o botão na tela é conveniência, não controle: a mesma matriz responde à tela e à API.
   - A matriz é testada de forma automática: cada papel × cada comando, e acesso horizontal a outra organização.
   - O RLS da F0-b é a segunda barreira, não a primeira.

5. **Identidade externa atrás de uma interface; o adaptador autentica, não autoriza** (ponto OIDC).
   - **Identidade = `issuer` + `subject`** (o `sub` do OIDC).
     - O vínculo com cada organização é explícito, em `app.identity_link`. O e-mail nunca associa uma identidade a uma organização nem a um usuário, nem quando coincide.
     - A mesma identidade pode ter vínculos legítimos com mais de uma organização; havendo mais de um, o usuário escolhe na tela.
   - **O adaptador OIDC (autoria Codex) faz a parte do protocolo:**
     - valida `state`, `nonce` e PKCE;
     - valida assinatura, `issuer`, `audience` e expiração do ID token;
     - devolve só `{ issuer, subject }` validados.
     - Não escreve SQL, não escolhe organização e não cria sessão.
   - **Transação de login com uso único:** o adaptador guarda `state`, `nonce` e o verificador PKCE por uma **porta de armazenamento** implementada pelo Claude.
     - A porta devolve um ticket aleatório, que vai num cookie do navegador, com validade curta.
     - O callback consome o ticket de forma atômica: a segunda tentativa não acha nada.
   - **Continuação depois do callback (Claude; pedido do Codex de 28/09).** Com o `ResultadoLogin` de sucesso, a casca não confia em nada que venha depois do navegador:
     1. `abrir_continuacao` guarda no servidor a identidade validada e o destino e devolve um ticket opaco de 256 bits. O banco guarda só o hash; o ticket vai num cookie `HttpOnly` do navegador, com validade curta.
     2. A tela de escolha lista as organizações e os papéis por `vinculos_da_continuacao(hash)`, nunca por issuer, subject ou usuário vindos do navegador.
     3. O POST da escolha informa **só** a organização e o papel escolhidos. Qualquer campo de identidade no corpo é recusado pelo contrato.
     4. `concluir_continuacao` faz tudo numa transação:
        - consome o ticket de forma atômica (uso único, só se não expirado);
        - **revalida** o vínculo vivo naquele momento: identidade ligada à organização, usuário ativo e papel atribuído;
        - cria a sessão.

        Se qualquer passo falha, não há sessão.
     - Com um só vínculo e um só papel, a casca pode concluir sem mostrar a tela, pela mesma função.
   - **O issuer, o client id e a URL de callback vêm de configuração confiável**, nunca de parâmetro da requisição. O destino depois do login é só um caminho interno validado, nunca uma URL livre.
   - **Provedor de desenvolvimento**, para DEV e para os testes ponta a ponta locais: usuários fictícios, e só liga com trava dupla, falhando fechado se qualquer uma faltar:
     - `SAFRION_AMBIENTE=dev`;
     - a identidade gravada no próprio banco dizendo `dev`.

     Em HML e produção ele não existe: o build não o registra, e um teste prova que a rota dele responde 404 fora de DEV. Não é atalho de login na homologação; o E2E hospedado usa contas de teste pelo provedor real.
   - **Os tipos do contrato ficam em `apps/web/src/identidade/provedor.ts`** (§10).

6. **Proteções da web (ENG-045; ponto CORPO).**
   - Mutação só por `POST` com `Content-Type: application/json` e checagem de `Origin` igual à origem configurada da aplicação (defesa contra CSRF, junto com `SameSite`).
   - CSP restritiva, com `frame-ancestors 'none'`.
   - Sem `dangerouslySetInnerHTML`.
   - **Limite de corpo contado em bytes durante a leitura, antes do parse:**
     - a leitura para ao passar do limite e responde 413;
     - vale também sem `Content-Length`, ou com `Content-Length` menor que o corpo real.
     - O valor sai do maior comando da F1, com margem declarada no código; nada de número arbitrário.

7. **Log e erro sem texto livre (ENG-081; ENG-015; ponto LOG-ADR).** A rota registra com o registrador da F0-b2 (`criarRegistrador`, uma linha JSON por requisição e por comando). O log leva:
   - **só** códigos, correlação e metadados com formato conferido;
   - **nunca** mensagem, stack ou causa de exceção, URL do OAuth, corpo da requisição, `code`, verificador PKCE, `nonce`, token, cookie ou hash de sessão (a mesma regra do F0B2-01).

   Erro inesperado responde `FALHA_INTERNA` genérica, com a correlação. Uma falha do próprio registrador não muda a resposta nem um efeito já confirmado.

8. **Identidade do ambiente e `demo:reset` (23.4).** Já entregues na F0-c parte 1:
   - a identidade (`dev`, `hml` ou `prod`) é gravada no banco no provisionamento e mostrada em `/saude` junto com versão, commit e migração, sem segredo;
   - `pnpm demo:reset` só roda com a identidade `dev` ou `hml`, o processo dizendo o mesmo ambiente e o nome repetido no comando;
   - uma falha de infraestrutura sai com código 3, só com códigos.

9. **Casca e acessibilidade (cap. 74; NFR-09).**
   - Tokens do design system como variáveis CSS e menu Estoque e Cadastros no padrão Menu → Listagem → Detalhe.
   - Teste automático com axe (WCAG 2.2 AA) nas telas da F0-c.
   - Versões de Next.js, React, Playwright e axe fixadas no PR, com a quarentena de 7 dias.

10. **Fronteira de autoria (confirmada pelo Codex em 28/09).** Nenhum arquivo tem dois autores.

    | Autor | Arquivos |
    |---|---|
    | Claude | Este ADR; `apps/web/src/identidade/provedor.ts` (só tipos, revisado pelo Codex antes de qualquer implementação); a migração `0003` (vínculo, sessão, transação de login e funções `SECURITY DEFINER`); `packages/db/src/sessao-web.ts`; a casca `apps/web` (rotas, `/saude`, comandos, matriz, proteções, provedor de desenvolvimento); e os testes disso tudo |
    | Codex | `apps/web/src/identidade/oidc/*`, o adaptador que implementa `ProvedorIdentidade` com a validação OIDC, e os testes dele |

    Se o adaptador precisar de outro dado persistido, o Codex especifica e o Claude põe na migração. A sequência de migrações tem um só autor.

11. **Vínculo de identidade em HML (implementado na F1, migração `0005`; revisão do Codex de 28/09 incorporada).** Até aqui, o único vínculo que o sistema criava era o das identidades fictícias de desenvolvimento (`vincular_demonstracao`, migração `0004`). Para alguém entrar em HML pelo OIDC, um administrador concede o vínculo da identidade que o provedor verificou.
    - **A identidade vem de um login validado, nunca de digitação nem de e-mail.**
      1. A pessoa entra pelo provedor. O adaptador valida o ID token e a casca não acha vínculo (`SEM_VINCULO`).
      2. Só nesse caso, e só com o provedor OIDC (nunca com o de desenvolvimento), a casca chama `registrar_pedido_acesso(issuer, subject, hash)`.
         - A aplicação gera um **código de referência** de 10 caracteres (Crockford base32, 50 bits aleatórios); o banco guarda só o SHA-256 dele.
         - O código vai num cookie `__Host-` do utilitário existente (`HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/`), com 10 minutos.
      3. A tela "Sua conta ainda não tem acesso" mostra o código lido desse cookie, em dois grupos, com a renderização do React. A página não vai para cache (`no-store`). O código nunca vai para a URL nem para o log.
      4. A pessoa passa o código ao administrador.
    - **O código só localiza o pedido; ele não prova ao administrador quem é a pessoa.** Antes de conceder, o administrador confirma por um canal autenticado independente quem pediu, e confere organização, usuário e papel. Ele registra responsável e motivo.
    - **O pedido não concede nada.**
      - Há um pedido vivo por identidade: um novo login sem vínculo troca o código (o anterior deixa de existir) e renova o prazo de 24 h.
      - Limites operacionais de HML: **no máximo 100 pedidos vivos e 1000 retidos.** Uma trava consultiva serializa os registros, então a cota vale também com registros simultâneos.
      - A limpeza é oportunista, na própria transação do registro, sem serviço à parte:
        - pendente vencido sai;
        - consumido sai depois de 30 dias, o mínimo para a idempotência;
        - consumido mais novo nunca sai para abrir espaço.
      - Acima da cota, não há código novo, e o log registra o motivo `PEDIDOS_ESGOTADOS`. Não é proteção total contra abuso de quem autentica no provedor; é teto de HML.
      - O pedido guarda só issuer, subject, hash do código e datas: nem e-mail nem nome (o escopo é só `openid`).
      - Sem código novo, o cookie anterior é apagado. Ele também é apagado ao entrar, e a tela nunca mostra o código de outra pessoa que usou o mesmo navegador.
    - **Concessão: comando do administrador, explícita e auditável.**
      - `vincular-identidade.js conceder --ambiente hml --banco <nome> --organizacao <id> --usuario <id> --responsavel <quem autorizou> --motivo <texto curto>`, no alvo `preparo` da imagem.
      - **O código entra pela entrada padrão, sem eco no terminal, nunca por argumento**, que ficaria no histórico e no `ps`. Um `--codigo` é recusado como uso incorreto.
      - O administrador do servidor assume o `migrator` no banco-alvo, que precisa estar identificado como `hml`. `dev` e `prod` são recusados antes de ler o código e de abrir conexão.
      - A função `conceder_vinculo` é `SECURITY DEFINER` (dono `app_sessao`), com `EXECUTE` revogado de `PUBLIC` e concedido só ao `migrator`. **O `app_runtime` não concede nem revoga.** Ela também recusa banco que não seja `hml`.
      - Numa transação, com a trava por organização e usuário:
        - confere o pedido pelo hash, o usuário ativo com papel na organização e que o issuer não é o de desenvolvimento;
        - revoga qualquer sessão que tenha sobrado dessa identidade nessa organização;
        - grava o vínculo, consome o pedido guardando o destino, e registra o evento.
      - **Idempotência:** o mesmo pedido, já consumido para o mesmo destino e com a concessão ainda vigente, devolve `mantido`, sem evento novo.
      - **Depois de uma revogação, o código antigo não reabre o acesso** (`PEDIDO_CONSUMIDO`).
      - Recusas sem efeito: pedido para outro destino, ou identidade já ligada a outro usuário na mesma organização (`VINCULO_CONFLITANTE`); pedido vencido (`PEDIDO_VENCIDO`); inexistente (`PEDIDO_INEXISTENTE`); usuário inválido (`USUARIO_INVALIDO`).
      - Saída como no preparo: 0 concedido ou mantido; 1 recusado, com o código do motivo; 2 uso incorreto; 3 infraestrutura, só com códigos. Nunca imprime subject, código de referência ou hash.
    - **Revogação:** `vincular-identidade.js revogar … --organizacao <id> --usuario <id> --responsavel … --motivo …`.
      - Remove **todos os vínculos desse usuário nessa organização**, com um evento por vínculo, e revoga as sessões dele ali. Outras organizações não mudam.
      - Repetir não muda nada (`sem_vinculo`).
      - Vincular de novo exige um pedido novo, e **nenhuma sessão anterior volta a valer.**
      - **Concorrência:** concessão, revogação, `concluir_continuacao` e `trocar_papel` usam a mesma trava por organização e usuário. Uma sessão criada no meio da revogação é revogada por ela, ou a conclusão espera e já não acha o vínculo. Mesmo sem a trava, a sessão só resolve com o vínculo vivo (§3), e a concessão seguinte revoga a sessão que tiver sobrado.
    - **Auditoria:** tabela `app.identity_link_event` com:
      - organização, momento, ação (`concedido` ou `revogado`), issuer, subject e usuário;
      - o `session_user` do banco (quem estava conectado, não o dono da função);
      - responsável e motivo.

      Ela é imutável para os papéis da aplicação: RLS com FORCE, o `app_sessao` só insere e lê, o `app_runtime` não tem privilégio, e um gatilho recusa UPDATE e DELETE. Não é promessa absoluta contra o administrador do banco. O `migrator` lê a auditoria. O `app.audit_log` não serve, porque exige um usuário da aplicação como autor.
    - **Demonstração em HML:** o `demo:reset` revoga, na mesma transação, os vínculos reais e as sessões que apontam para gerações anteriores da organização fictícia, com evento `revogado` e motivo `demo_reset`. Falha no reset desfaz tudo junto. Nada passa para a geração nova sem concessão explícita. Em `dev`, a função não faz nada, e o vínculo sintético da `0004` continua como antes.
    - **Limite conhecido:** uma identidade já vinculada a alguma organização entra por ela e não gera pedido. Vincular a mesma identidade a uma segunda organização pede um caminho próprio (por exemplo, a partir de uma sessão), fora deste recorte.
    - **Fora deste recorte:** tela de acessos na web (depende de um papel administrador na matriz), produção, convite por e-mail e autoinscrição.
    - **Autoria:** Claude (migração `0005`, `vinculo.ts`, comando, casca e testes); revisão Codex e Gemini. O adaptador OIDC não muda.

## Alternativas consideradas
| Alternativa | Por que não |
|---|---|
| Server Actions para mutação | Ficam presas ao React; o app offline precisaria de um segundo caminho de comando, com duas validações e duas chances de divergir (73.3) |
| Sessão só em JWT assinado, sem banco | Revogar não teria efeito antes da expiração (ENG-042: sessões revogáveis) |
| `app_runtime` com SELECT na tabela de sessão, ou BYPASSRLS para resolver sem organização | Permitiria enumerar sessões e ler hashes de outras organizações; a função `SECURITY DEFINER` devolve só a linha válida do hash apresentado |
| Associar usuário pelo e-mail do provedor | O e-mail muda e pode coincidir entre pessoas; só `issuer` + `sub` identifica, e o vínculo com a organização é explícito |
| ROPC (senha do usuário enviada pela aplicação ao provedor) | Vedado pela RFC 9700 §2.4; o fluxo é o de código de autorização com PKCE |
| Biblioteca de autenticação completa agora (NextAuth/Auth.js e similares) | O provedor da HML é do passo 3; a interface permite usar a biblioteca dentro do adaptador sem mudar rota, sessão nem matriz |
| Autorização só pelo RLS | O RLS isola organização, não decide ação por papel (gerente × almoxarife); a ENG-043 exige a matriz por ação |
| Atalho de login para testes na HML | Enfraquece a autenticação do ambiente que o Adrianus usa; a verificação hospedada usa contas de teste reais |
| Administrador digita o `sub` visto no console do provedor (§11) | Em provedores com `sub` por aplicação (pairwise) o valor nem aparece no console; digitado à mão, um erro vincula outra pessoa sem que ninguém perceba |
| Convite por link ou autoinscrição no primeiro login (§11) | Concede acesso a quem tiver o link ou uma conta no provedor; a concessão deixa de ser um ato explícito do administrador |
| Concessão pela tela da web já na F0-c (§11) | Exige papel de administrador na matriz e abre mais superfície na aplicação; o comando do operador cobre a HML pela mesma função, que a tela pode chamar depois |
| Registrar a concessão no `app.audit_log` (§11) | A tabela exige um usuário da aplicação como autor; o operador não é um, e um autor fictício quebraria a auditoria |

## Consequências
- Web e app offline compartilham o mesmo endpoint, contrato, envelope e recibo, e o reenvio offline é o mesmo comando.
- A F0-c ganha a migração `0003` (vínculo, sessão e transação de login), com os mesmos testes de RLS, privilégio e imutabilidade da F0-b. O `app_runtime` continua sem filiação a papel algum.
- O adaptador OIDC entra num PR próprio do Codex quando o passo 3 fechar; até lá, DEV e a CI usam o provedor de desenvolvimento, com trava dupla.

## Verificação (aceites da F0-c, plano R-006 passo 8)
- **`pnpm test:e2e`** (Playwright, banco real na CI):
  - o almoxarife entra e vê Estoque;
  - o gerente não vê "Receber", e a API nega o comando com 403;
  - outra organização não vê o lote, nem por URL nem pela API (404 como inexistente);
  - axe sem violação AA;
  - `demo:reset` recusado fora de DEV e HML.
- **Matriz:** testada por papel e comando, com a negação por padrão provada por um comando fora da matriz.
- **Sessão, com testes de integração em banco real:**
  - hash aleatório, revogado ou expirado não resolve;
  - usuário desativado ou papel removido entre duas requisições bloqueia a seguinte;
  - a troca de papel só vale para papel vinculado, e a sessão antiga deixa de valer;
  - o `app_runtime` não consegue ler nem enumerar a tabela de sessão;
  - a transação seguinte não herda a organização;
  - o reenvio de um comando devolve o recibo sem novo efeito.
- **Transação de login:**
  - ticket inexistente, expirado ou já consumido não devolve nada;
  - duas tentativas simultâneas com o mesmo ticket: só uma consome.
- **Continuação depois do callback:**
  - sem continuação válida, nenhuma sessão é criada;
  - identidade no corpo da escolha é recusada;
  - organização sem vínculo é recusada;
  - ticket expirado ou já usado, ou duas escolhas simultâneas, nunca geram duas sessões;
  - vínculo revogado, usuário desativado ou papel removido entre o callback e a escolha impedem o acesso.
- **OIDC (testes do Codex no adaptador):**
  - callback repetido;
  - `state` ou `nonce` inválidos;
  - `issuer` ou `audience` errados;
  - mesmo e-mail com outro `sub` não entra;
  - troca de e-mail com o mesmo `sub` continua entrando;
  - vários vínculos organizacionais legítimos funcionam.
- **Corpo:** acima do limite responde 413, também sem `Content-Length` ou com `Content-Length` menor; a memória lida fica limitada ao limite.
- **Log:** falha HTTP e falha OIDC com canário registram um evento útil sem o canário, com a correlação preservada e a resposta original intacta.
- **Provedor de desenvolvimento:** a rota responde 404 com `SAFRION_AMBIENTE` diferente de `dev` ou com a identidade do banco diferente de `dev`.
- **Contrato:** `organizationId` no corpo é recusado, e uma sessão de A não executa comando em lote de B.
- **Vínculo em HML (§11)** (`packages/db/test/vinculo.int.test.ts`, `apps/web/test/rotas.int.test.ts`, `apps/web/e2e/acesso.spec.ts`):
  - código inexistente, vencido ou já consumido para outro destino é recusado, sem vínculo nem evento;
  - a concessão cria o vínculo, consome o pedido e grava um evento; repetir devolve `mantido` sem evento novo;
  - identidade ligada a outro usuário na mesma organização é recusada com `VINCULO_CONFLITANTE`;
  - o `app_runtime` não executa concessão nem revogação: a casca só registra pedido;
  - nenhum pedido nasce do provedor ou do issuer de desenvolvimento;
  - e-mail igual ao de um usuário não muda nada, porque o pedido não tem e-mail;
  - depois da revogação, a próxima requisição com a sessão existente é negada, e o evento fica gravado;
  - o `demo:reset` em HML revoga os vínculos reais da geração anterior, com evento;
  - um pedido vivo por identidade, com teto, validade e limpeza provados;
  - a saída do comando e o log não trazem subject, código de referência nem hash;
  - depois da revogação, o código antigo não reabre o acesso (`PEDIDO_CONSUMIDO`);
  - revogação ao mesmo tempo que a conclusão do login ou a troca de papel nunca deixa sessão válida, nem depois de uma concessão nova;
  - duas concessões simultâneas do mesmo pedido: uma concede, a outra mantém, com um evento só;
  - falha na mesma transação desfaz concessão, consumo e evento, e também a revogação feita pelo `demo:reset`;
  - o comando recusa `dev` e `prod` antes de ler o código e de conectar, e recusa `--codigo` como argumento;
  - a página mostra o código só vindo do cookie, sem cache, nunca o da URL nem um cookie repetido.
