# Plano mínimo: F0 → F1 → homologação hospedada

Autor: Claude Code (subagente), 27/09/2026. Versão 2: achados de dois revisores adversariais decididos na seção 6. Revisor oficial: Codex (pendente). Fontes: `evidencias/R-006-requisitos.md`, `evidencias/R-006-hospedagem.md` e `evidencias/R-006-ambiente.md`; `AGENTS.md` §2, §3.1, §3.2 e §3.4; `docs/STATUS.md`; R-002 §5.
Rótulos: **[verificado]** = conferido nesta sessão, por leitura ou comando. **[especificado]** = escrito na fonte ou proposto aqui, ainda não executado. **não verificado** = sem fonte.

## 1. Resposta direta

**Hoje o Adrianus só pode abrir o protótipo** [verificado em 27/09/2026, leitura e listagem do artifact]:
- Link: https://claude.ai/artifact/WPDgqGvKX6CYTCdPjidBLo. Título "Do Talhão à O.S. · protótipo (PRD v3.9)". Versão publicada `1790515657-c71b`, atualizada em 27/09/2026. Privado, dono Adrianus: ele abre com a conta dele.
- É um canvas de desenho com 145 pranchas: 24 na página "Protótipo · menu vigente" e 121 em "Módulos ocultos (preservados)". Telas ligadas à F1: Suprimentos › Estoque (EST) e Cadastros › Produtos, unidades e locais (CD-06) no menu; SU-03, SU-06 e SU-08 na página de ocultos.
- Serve para validar telas e fluxo. Não tem software real por trás: sem banco, sem regra no servidor, sem usuários de teste.

**A homologação ainda não existe** [verificado no `docs/STATUS.md`]: código de produto "Nenhum" (sem backend, banco, integração ou implantação), e a CI remota nunca executou porque a conta do GitHub está bloqueada.
Pelo AGENTS §3.1, homologação é software real hospedado: candidata identificada por commit e imagem (digest), dados fictícios, serviços externos em sandbox, cobrança desligada e faixa "HOMOLOGAÇÃO" visível. O protótipo não cumpre nenhum desses itens e não será chamado de homologação.

**Próximo passo mínimo:** um único pedido ao Adrianus, com duas respostas de sim ou não, uma frase de autorização de gasto e um print (texto na seção 3). Até ele responder, os agentes só produzem documentos (passos 1, 3 e 5).

## 2. Passos até o link da homologação da F1

Tudo nesta seção é **[especificado]**: nada foi executado. Tamanho relativo: P (pequeno), M (médio), G (grande); não houve medição.
"A → B" = A é o autor, B é o revisor. Integrador: sempre quem não é autor (hoje o Codex, que tem credencial de push; o Claude não tem [verificado no STATUS]).

**Fase A: sem comando do proprietário (só documentos)**

| # | Entregável | Quem | Prova | Depende | Tam. |
|---|---|---|---|---|---|
| 1 | Revisão deste plano, com cada ajuste aceito ou recusado com motivo, em `docs/parceria/rodadas/R-006-...` | Claude → **Codex** | Rodada com autor, versão, data e parecer; `python3 tools/docs/checar_docs.py` com saída 0 | — | P |
| 2 | Um único pedido ao Adrianus com o texto da seção 3, em português simples, sem pergunta técnica | Claude → Codex | Resposta dele registrada em `docs/DECISIONS.md` | 1 | P |
| 3 | Tarefa da F0 no acordo curto (§3.4) e roteiro de verificação. Fecha também: login da HML (provedor OIDC com custo e fonte, ou alternativa que cumpra a ENG-042 com sessão revogável; preferir entrar com a conta Google dele e trocar de papel de teste só na HML; nenhuma senha no texto de mensagem, no seed ou no repositório); e registra na R-006 a antecipação da F0, que o STATUS previa só depois da CI verde, e as exceções da seção 4 | Codex → Claude | Seis campos preenchidos; comandos de aceite listados | 1 | P |
| 4 | Fundido ao passo 6 (achado 1-A6) | — | — | — | — |
| 5 | Tarefa da F1 e roteiro (escopo de `requisitos.md` §1). Fecha: origem = documento do fornecedor, sem pedido; chave natural do documento (proposta: organização + emitente + série + número) com restrição única no banco; corte do escopo, com motivo (proposta: cadastro de produto e local só por carga fictícia; estorno na fatia seguinte; Liberar fica se AC-14 e DEMO-02 ficarem), e o que ficar ganha passo na seção 5; itens da v3.10 usados pela F1 (73.3, 73.7–73.8) vigentes ou adotados por acordo registrado; cinco referências do módulo Estoque (§3.3); feedback por mensagem, fora do software, nesta homologação | Codex → Claude | Acordo curto aceito pelos dois na rodada | 3 | M |

**Fase B: F0, fundação verificável (depois de D1; não vai à homologação)**

| # | Entregável | Quem | Prova | Depende | Tam. |
|---|---|---|---|---|---|
| 6 | PR F0-a: `docs/architecture/versions.md` com fonte oficial e data no mesmo commit do lockfile (Node LTS, pnpm, TypeScript, Next, Prisma, Vitest, Playwright, Testcontainers, fast-check, Terraform e provedor Google; PostgreSQL e PostGIS num par oferecido pelo Cloud SQL, hoje PostGIS 3.5.2 no PG 15–17 e 3.6.0 no PG 18 [verificado 27/09/2026, página de extensões do Cloud SQL]); imagem de teste com o mesmo par, arm64 nativa verificada ou integração local declarada como emulada (`postgis/postgis` só sai para amd64 [verificado, Docker Hub]); monorepo pnpm, `.nvmrc`, `packageManager`, `engines.node`, scripts `format:check`, `lint`, `typecheck`, `test`, `build` e `pnpm doctor`; `packages/domain` com decimal (6 casas), unidades (galão de 5 L ↔ L) e saldo físico e utilizável | Claude → **Codex** | `python3 tools/ci/checar_contrato_codigo.py` = OK; `pnpm install --frozen-lockfile && pnpm check` com saída 0; propriedade (fast-check): utilizável ≤ físico, restrição dupla desconta uma vez, recusado fora do físico | D1, 3 | M |
| 7 | PR F0-b: `packages/db` com migração inicial (organização, usuário, papel, fazenda, local, produto, conversão de embalagem versionada, lote, movimento imutável com unidade original, unidade-base e versão da conversão, idempotência, auditoria, outbox) e RLS com `FORCE ROW LEVEL SECURITY`; dois papéis: `migrator` (dono das tabelas, só migração) e `app_runtime` (LOGIN, sem CREATEROLE, CREATEDB ou BYPASSRLS, não é dono; usado pela aplicação e pelo `demo:reset`); envelope de comando (chave, versão esperada; efeito, recibo, auditoria e outbox na mesma transação); contrato de erro (Zod); log com `correlation_id` | Claude → **Codex** | `pnpm test:integration` em PostgreSQL/PostGIS real (Testcontainers), com `app_runtime`: isolamento; duas organizações alternando na mesma conexão do pool, sem tenant residual; reenvio gera um movimento e o mesmo recibo; mesma chave com outro conteúdo gera `IDEMPOTENCY_KEY_REUSED` sem efeito; 10 envios simultâneos, uma execução; versão esperada desatualizada gera conflito sem efeito; auditoria com os campos da NFR-04; contrato recusa quantidade como número JSON e exige unidade; migração do zero | 6; D3 (sem D3, só na CI, após D2) | G |
| 8 | PR F0-c: shell web com os tokens, menu só com Estoque e Cadastros; login do passo 3; autorização no servidor; `pnpm demo:reset` só por comando explícito, com dados fictícios, conferindo a identidade do ambiente (23.4); página `/saude` com versão, commit e ambiente | Claude → **Codex** | `pnpm test:e2e` (Playwright): almoxarife entra; gerente não vê "Receber" e a API nega; outra organização não vê o lote; axe sem violação AA; `demo:reset` recusado fora de DEV e HML | 7 | M |
| 9 | Revisão por contraexemplo de cada PR, com reprodução em máquina própria; correções com teste de regressão | **Codex**; Claude corrige | Parecer na rodada com comandos e saídas, rotulado "executado localmente" | 6–8 | M |
| 10 | CI remota verde no commit da F0: código, documentação, Gitleaks e Trivy | Codex integra | Link da execução e SHA; quatro jobs verdes | D2, 9 | P |

**Fase C: ambiente de homologação (depois de D4; corre em paralelo com a Fase D)**

| # | Entregável | Quem | Prova | Depende | Tam. |
|---|---|---|---|---|---|
| 11 | ADR curta da região (`southamerica-east1`, exigida pela 28.1). `infra/terraform/bootstrap`: bucket do state, versionado e restrito; pool OIDC do GitHub com condição no repositório `adrptu/Safrion-Software-` e no ambiente `hml`; conta de serviço de deploy com papéis mínimos; orçamento com alertas em 70, 90 e 100% de US$ 25 (28.4). `infra/terraform/hml`: Cloud Run web (mínimo 0, máximo 2, pool de 3 conexões) e Cloud Run Job de migração (até 3 conexões): mesmo com duas revisões, 4 × 3 + 3 = 15 ≤ 18, que é 75% de 25 (28.3; 25 é o padrão para instâncias de ~0,5 GB [verificado, página de flags do Cloud SQL]); Cloud SQL `edition = ENTERPRISE`, `db-f1-micro`, `ZONAL` (PG 16+ nasce Enterprise Plus e o núcleo compartilhado só existe na Enterprise [verificado, página de edições]); `app_runtime` pelo Secret Manager; URL controlada (IAP ou equivalente, custo a conferir na fonte) ou exceção pela ENG-005 | Claude → **Codex** | `terraform fmt`, `validate`, TFLint e Trivy config sem achado alto, executados localmente | D4 | M |
| 12 | Bootstrap aplicado uma vez nesta máquina: o Adrianus só entra com a conta Google na janela que abrir; o state do bootstrap vai para o próprio bucket; depois, `gcloud auth revoke --all` e `gcloud auth application-default revoke` | Claude; Codex confere | Codex lê o plan num arquivo local fora do Git e registra na rodada só o hash e a contagem de recursos; após revogar: `gcloud auth list` sem conta e sem `~/.config/gcloud/application_default_credentials.json` | 11; conta criada | P |
| 13 | Pipeline da HML, só por OIDC: plan na CI guardado como artefato privado de retenção curta, e `apply` exatamente do plan cujo hash o Codex aprovou; imagem construída uma vez e publicada por digest; migração com `migrator`; `demo:reset` só na primeira carga e por comando explícito; faixa "HOMOLOGAÇÃO" permanente; e-mail e cobrança desligados | Claude → Codex | `curl <url>/saude` mostra o commit da CI e o digest publicado. Só a F0 no ar é infraestrutura pronta, não homologação: nenhum link vai ao Adrianus | 10, 12 | M |

**Fase D: F1, receber insumo por lote e local e ver o saldo**

| # | Entregável | Quem | Prova | Depende | Tam. |
|---|---|---|---|---|---|
| 14 | PRs da F1 (um ou dois), no escopo cortado no passo 5, sobre a F0 verificada localmente (branch empilhada se o merge esperar a CI): documento de entrada (Rascunho → Confirmado) com restrição única da origem; receber (CMD-15) com aceito, bloqueado e recusado; segregar; liberar, se mantido; saldo (SU-03) com trilha | Claude → **Codex** | TDD. `pnpm check`, `test:integration` e `test:e2e` cobrindo: caminho normal, erro, permissão negada, repetição, documento duplicado, troca de fazenda com documento aberto (AC-05), lote vencido fora do apto; disputas simultâneas com chaves diferentes (liberar a mesma quarentena duas vezes; segregar 5 L duas vezes com 5 L aptos; ENG-023 pede ao menos 100 disputas): apto ≥ 0, bloqueado ≤ físico, efeito único; duas confirmações simultâneas do mesmo documento geram uma entrada. p95 e cliques/digitação medidos na e2e | 5, 9 | G |
| 15 | Revisão por contraexemplo e reprodução da tarefa da seção 5 em DEV | **Codex**; Claude corrige | Parecer na rodada; nenhum S1 ou S2 aberto | 14 | M |
| 16 | Candidata: CI verde no commit; deploy na HML por digest; Codex executa a tarefa da seção 5 na HML antes do dono, cronometra e confere que os rótulos do texto batem com a tela; repete o AC-04 na HML e registra `SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user` feito com a credencial publicada | Codex integra e testa | Execução da CI e `/saude` com o mesmo SHA; roteiro com capturas; a consulta devolve `rolsuper = f` e `rolbypassrls = f` | 10, 13, 15 | P |
| 17 | Mensagem ao Adrianus: link, versão (commit e digest), o que está pronto, tarefa da seção 5 com o tempo medido, como entrar (sem senha no texto), limitações (seção 4); `docs/STATUS.md` atualizado | Claude → Codex | Mensagem registrada; STATUS no PR | 16 | P |
| 18 | Feedback vira casos rastreáveis; correção com regressão; ele retesta só os itens afetados | Codex registra; Claude corrige | Casos com ID e estado | 17 | P |

**Pontos de revisão do Codex:** plano (1); cada PR da F0 (6, 7, 8 → 9); Terraform e plans (11, 12, 13); F1 (14 → 15); ensaio na HML antes do dono (16); texto das mensagens ao dono (2, 17).
**Caminho crítico:** D1 → 6 → 7 (D3) → 9 → 14 → 15 → 16 → 17. Em paralelo, e prontos no passo 16: D2 → 10 → 13 e D4 → 11 → 12 → 13. A CI verde só é exigida da candidata (passo 16; `requisitos.md` §3 item 3).

## 3. Decisões e autorizações do proprietário

Pedir tudo de uma vez (passo 2). Os agentes não criam conta, não aceitam termos, não digitam cartão e não mudam plano do GitHub (AGENTS §2). A tabela é para os agentes; ao dono vai só o texto abaixo dela.

| D | Decisão | Proposta concreta | Custo estimado (fonte) | O que vale até ele decidir |
|---|---|---|---|---|
| D1 | Iniciar o software real (F0 e F1), só com dados fictícios; baixa as dependências do registro npm e a imagem do banco | Pergunta 1 do texto | Nuvem: zero na F0, que roda local e na CI [especificado]. Espaço em disco das dependências: não verificado | Só documentos (passos 1, 3 e 5). Nenhum `package.json` no repositório |
| D2 | Liberar a conta do GitHub `adrptu` (ação do titular) | Pedido 4: um print do aviso. Com ele, os agentes leem o motivo e devolvem de 1 a 3 cliques, com custo e fonte, se houver. A proteção da `main` (PEND-REPO-01) fica fora da mensagem; se exigir plano pago, vira pedido de custo separado, com preço e fonte | Não verificado: motivo do bloqueio e preço do plano não lidos | Checks locais apenas. Nada é chamado de "CI verde"; nenhuma candidata vai à HML |
| D3 | Programa de contêiner neste Mac, para testar com banco real local | Escolha dos agentes: Docker Desktop, gratuito para empresa com menos de 250 funcionários **e** faturamento anual abaixo de US$ 10 milhões, uso pessoal ou educação [verificado 27/09/2026, docs.docker.com/subscription/desktop-license]; a instalação recomendada pede a senha do Mac [verificado, guia de instalação para Mac]. Se a empresa for maior: Colima (licença não verificada; exige Homebrew, ausente), com nova pergunta | Zero, se ele se enquadrar. Tamanho: não verificado na fonte; conferir o arquivo antes e não instalar se sobrarem menos de 5 GiB livres [critério nosso]. Disco livre: 12 a 13 GiB [verificado, `df` em 27/09/2026]. A imagem oficial do PostGIS é só amd64: neste Mac arm64 roda emulada, mais lenta, salvo imagem arm64 do mesmo par (passo 6) | Claude avança só em `packages/domain`; banco só na CI, depois de D2. Não é opcional: tira o passo 7 da dependência de D2 |
| D4 | Conta e gasto da HML | Google Cloud em São Paulo: Cloud Run + Cloud SQL `db-f1-micro` com PostGIS, sem HA (topologia do PRD §28.1; região em ADR no passo 11). Aprovação agora; a conta ele cria só quando os agentes avisarem (passo 12), porque o crédito de 90 dias corre desde a criação. Autoriza baixar `gcloud` e Terraform, hoje ausentes [verificado] | ≈ US$ 16,32/mês ≈ R$ 87,84 com IOF [especificado: Cloud Run (F12) e Cloud SQL (F13b) verificados; PTAX de 25/09/2026 (F1); a reserva de US$ 2 não tem preço lido e a vigência do IOF de 3,5% não foi verificada]. **Orçamento de US$ 25/mês (≈ R$ 135) com aviso por e-mail em 70, 90 e 100%; o gasto não para sozinho** [verificado 27/09/2026: orçamento só de alerta não limita uso nem gasto, e o custo chega com atraso; docs.cloud.google.com/billing/docs/how-to/budgets]. Crédito de US$ 300 por 90 dias (F13); elegibilidade não verificada. Custo do login da HML: não verificado (passo 3) | A F1 só é demonstrável em DEV e não é chamada de homologação. O plano B (Fly.io + Neon ≈ US$ 7,85/mês; F3, F6) fica entre os agentes e só é oferecido, com ADR que altere a §28.1, se ele recusar o custo |

**Texto do pedido (passo 2), revisado pelo Codex antes de enviar:**
> 1. Posso começar o sistema de verdade do estoque (receber insumo e ver saldo), só com dados de teste? (sim ou não)
> 2. O ambiente de teste no Google custa cerca de R$ 88 por mês. O Google avisa por e-mail perto do limite, mas não corta o gasto sozinho. Se aprovar, responda: "Autorizo criar o ambiente de teste no Google, com gasto de até US$ 25 por mês (cerca de R$ 135)."
> 3. Posso instalar neste Mac o Docker Desktop, programa gratuito para empresa com menos de 250 funcionários e faturamento abaixo de US$ 10 milhões por ano? Ele pede a senha do Mac uma vez. (sim, não ou "a empresa é maior")
> 4. Me mande um print do aviso de bloqueio do GitHub (e-mail ou tela de entrada).
> Mais tarde, quando avisarmos: criar a conta Google Cloud, cadastrar o cartão, aceitar os termos e, num dia combinado, entrar com sua conta Google na janela que abrir no Mac.

**Depois, não agora:** domínio próprio (até lá, o endereço padrão do Cloud Run; não verificado nesta pesquisa); hospedagem do piloto, ≈ US$ 183/mês com HA dedicado ou ≈ US$ 112/mês com HA compartilhado sem SLA (`hospedagem.md`), decidida só após o aceite da F1; aceite de produção (AGENTS §3.1).

## 4. Fora da F1 e riscos

**Fica fora (motivo):**
- F2 a F5, pedido e cotação, financeiro e ERP, transferência, inventário, custo do lote, leitura do XML, anexos, portal e IA: não fazem parte da tarefa da F1 (`requisitos.md` §1.7).
- Projeto de produção e piloto: só depois do aceite dele sobre a candidata (AGENTS §3.1).
- Worker que publica a outbox: a F1 não tem consumidor. A outbox é gravada na transação e o publicador entra quando houver quem consuma.
- Exercício de backup e restauração: na HML os dados são fictícios e recriáveis; basta a migração do zero. Obrigatório antes da primeira produção (PRD 30.5).
- HA, SLO, alertas com plantão e painéis completos: a HML não tem SLA.
- Offline e app de campo: F5.
- SonarQube: licença e custo não verificados. Controle pendente (31.5): sem gate externo de qualidade; dono, Claude; conclui com a licença decidida. Exceção (ENG-005): aprovador, Codex, na R-006; vence antes do piloto.
- MFA de administrador: exceção (ENG-005) só com dados fictícios; compensação: nenhum dado real e nenhum acesso a produção; aprovador, Codex, na R-006; vence antes do primeiro dado real.
- Proteção imposta da `main` (22.2, 23.3, ENG-019): exceção (ENG-005) registrada na R-006 antes do passo 14. Escopo: HML com dados fictícios. Compensação: PR, CI verde na candidata e parecer escrito do outro agente. Aprovador: Codex. Vence quando a conta for liberada (aplicar, se o plano permitir) e sempre antes do primeiro dado real.
- Revisão humana qualificada (31.7; ENG-020: IA não é revisor independente): controle pendente (31.5). Impacto: sem ela não há piloto. Dono: Adrianus, na hora de decidir o piloto (custo não verificado). Conclui com parecer registrado antes do piloto.
- Ensaio de carga: na F1 basta medir o p95 na e2e.
- Modelo de ameaças, ZAP e teste de intrusão: antes do piloto e da produção (ENG-041, ENG-048).
- Captura de feedback dentro do software: nesta HML o retorno vem por mensagem; a captura entra antes do primeiro piloto (comando-mestre).

**Riscos e mitigação:**
| Risco | Mitigação |
|---|---|
| CI bloqueada por tempo indeterminado (D2): sem evidência remota nem deploy | Verificação local registrada; nada é chamado de "verde"; a F0 não é declarada pronta; o dono é avisado só do impedimento |
| Sem contêiner local (D3): RLS, idempotência e migração não testáveis na máquina | Começar pelo domínio; integração só na CI; nunca trocar o banco real por mock ou SQLite (ENG-034) |
| Disco com 12 a 13 GiB livres e 8 GiB de RAM | Conferir o tamanho antes de baixar; Playwright só com Chromium; limpar cache com critério |
| Um só agente com push e a mesma conta `adrptu` para os dois | Integrador é sempre quem não é autor; revisão registrada na rodada; não simular revisor no GitHub; revisão humana qualificada declarada pendente |
| Gasto acima do orçamento: o alerta do Google não corta o gasto [verificado] | Máximo de 2 instâncias, mínimo 0, banco pequeno, alertas em 70, 90 e 100%; se a HML ficar parada, propor ao dono desligá-la. Corte automático (orçamento → Pub/Sub → desligar o faturamento) não adotado: derruba a HML sem aviso (28.4) |
| Credencial pessoal do dono esquecida nesta máquina | Revogar a sessão e a credencial padrão do Google (ADC) e conferir que o arquivo sumiu (passo 12) |
| Confundir protótipo com homologação | Faixa "HOMOLOGAÇÃO" e `/saude` com commit e digest; toda mensagem diz qual dos dois é |
| Movimento duplicado (S2) ou vazamento entre organizações (S1) | Testes com `app_runtime`, 10 envios simultâneos, reenvio, troca de conteúdo, disputas com chaves diferentes e restrição única da origem; na HML, AC-04 repetido e papel conferido (passo 16) |
| Primeiro acesso lento (mínimo 0) e banco sem SLA | Aceitável em teste; avisar na mensagem ao dono |
| pnpm do runtime do Codex ignora divergência de `packageManager` | Versões fixadas; o `pnpm doctor` (a criar no passo 6) confere a versão exata |
| Itens da v3.10 ainda em revisão | A tarefa da F1 cita o que foi adotado; se a v3.10 mudar, o teste muda junto |

## 5. Tarefa curta do Adrianus na homologação da F1

Dados fictícios [especificado]; como entrar, conforme o passo 3, sem senha no texto. Tempo: medido no ensaio do passo 16 e informado na mensagem ("leva cerca de N min"). Antes de enviar, os rótulos abaixo são trocados pelos exatos da tela, conferidos no ensaio.

| Nota | Emitente | Data | Produto | Lote | Validade | Local | Quantidade | Condição |
|---|---|---|---|---|---|---|---|---|
| NF-TESTE-001, série 1 | Fornecedor Teste Ltda | dia do teste | Fungicida A, galão de 5 L | F26-02 | 30/06/2027 | Depósito Central | 3 galões | 3 aptos |
| NF-TESTE-002, série 1 | Fornecedor Teste Ltda | dia do teste | Fungicida A, galão de 5 L | F26-03 | 31/08/2027 | Depósito Central | 2 galões | 1 apto; 1 bloqueado, motivo "avariado" |

1. Entre como **Almoxarife**.
2. Receba a NF-TESTE-001 com os dados da tabela. Confira: físico 15 L, apto 15 L, bloqueado 0.
3. Receba a NF-TESTE-002 com os dados da tabela. Confira o lote F26-03: físico 10 L, bloqueado 5 L, apto 5 L. Confira o produto: físico 25 L, apto 20 L.
4. Abra a trilha: 2 documentos e os movimentos, com autor e hora.
5. Lance de novo a NF-TESTE-001, com o mesmo número, série e fornecedor: o sistema deve avisar que ela já foi recebida e não somar.
6. Entre como **Gerente**: os mesmos saldos, sem o botão de receber.
Se o corte do passo 5 mantiver Liberar ou outra ação, ela ganha aqui um passo com o saldo esperado.

Resposta esperada dele: "ok" ou o número do passo que falhou, com uma captura de tela.

## Suposições
- O Codex segue como integrador por ter a credencial de push; se isso mudar, a regra "ninguém integra o próprio PR" continua valendo.
- A divisão da F0 em três PRs (passos 6 a 8) é proposta; o corte final sai da tarefa do passo 3.
- Os números de custo valem para a data de leitura de `hospedagem.md` (27/09/2026) e mudam com o câmbio.
- As validades das notas de teste são datas fictícias escolhidas para ficar no futuro durante a HML; se o teste passar de 30/06/2027, trocar.
- Documentação do Google e do Docker citada como [verificado] foi lida em 27/09/2026 nesta revisão; os limites mudam e são relidos antes do passo 11.

## 6. Revisão adversarial

Dois revisores independentes, 27/09/2026. "1-Ax" = revisor 1; "2-Ax" = revisor 2. Conferido nos três arquivos da pasta, no PRD (22.2, 23.3, 23.4, 24.1, 25.1, 27.4, 28.1–28.4, 31.5, 31.7; ENG-005, 019, 020, 023, 024, 025, 042, 055, 062, 063, 066; NFR-04), no AGENTS e no STATUS, e nas páginas oficiais citadas, lidas hoje.

| ID | Decisão | Motivo |
|---|---|---|
| 1-A1 | Aceito com ajuste | Os agentes escolheram o Docker Desktop depois de ler a licença e o guia; ao dono vai um sim/não com o único fato que só ele sabe (porte da empresa). D3 deixou de ser opcional. Tamanho do programa segue não verificado (a fonte não informa); critério de 5 GiB livres. Disco: 12 a 13 GiB (o `df` variou entre leituras) |
| 1-A2 | Aceito, caminho (a) | "Teto" virou "orçamento com aviso; o gasto não para sozinho" [verificado]. Corte automático (b) recusado: a 28.4 não quer limite financeiro que derrube a gravação sem aviso, e o limite de gasto do Google está em prévia, só para serviços elegíveis. Reserva de US$ 2 rotulada sem fonte |
| 1-A3 | Aceito | D2 virou pedido de print; a PEND-REPO-01 saiu da mensagem (ver 2-A8) |
| 1-A4 | Aceito | Texto do pedido em português simples (seção 3); plano B só se ele recusar o custo. Ajuste: o gasto é aprovado por frase literal, como pede o 2-A1 |
| 1-A5 | Aceito com ajuste | Passo 14 depende de 5 e 9; passo 11 só de D4; CI verde exigida só no 16. O resto da HML é aplicado pela CI (2-A1), então o passo 13 ainda depende do 10, fora do caminho crítico |
| 1-A6 | Aceito | Passo 4 fundido ao 6; a AGENTS §5 manda fixar versões no primeiro commit executável |
| 1-A7 | Aceito | Tabela com valores exatos; passo 5 reescrito; rótulos e tempo conferidos no ensaio do passo 16. A condição "bloqueado" no recebimento é parte do CMD-15 (`requisitos.md` §1.3); "Segregar" é outra ação |
| 1-A8 | Aceito como proposta | O corte é do Codex, autor da tarefa (AGENTS §3.1), no passo 5, com motivo; o que ficar ganha passo na tarefa do dono |
| 2-A1 | Aceito com ajuste | Entram: state remoto, bootstrap separado (28.2), `fmt`/`validate`/TFLint/Trivy (ENG-063), plan revisado por hash sem colar (ENG-062), condição OIDC por repositório e ambiente, revogação da ADC com checagem do arquivo e frase literal na D4. Recusado: o bootstrap feito pelo próprio Adrianus no terminal ou no Cloud Shell, porque a 31.7 veda exigir que ele cole comandos administrativos e a AGENTS §3.2 veda passar programação a ele; ele só entra com a conta. A frase não cita hash: o hash é amarrado à autorização na rodada |
| 2-A2 | Aceito | Papéis `migrator` e `app_runtime`, FORCE RLS, teste de pool e consulta do papel na HML. Conferido: usuário criado pelo Cloud SQL entra no `cloudsqlsuperuser`, com CREATEROLE e CREATEDB; a página não cita BYPASSRLS, por isso a prova consulta o papel na HML |
| 2-A3 | Aceito | Sem "teto"; alertas em 70/90/100 (28.4); máximo de 2 instâncias e pool de 3, conta da 28.3 (15 ≤ 18); reserva e IOF rotulados; conta criada só quando avisarmos. Corte automático recusado (ver 1-A2) |
| 2-A4 | Aceito | Conferido hoje: PG 16+ nasce Enterprise Plus; núcleo compartilhado só na Enterprise; PostGIS 3.5.2 (PG 15–17) e 3.6.0 (PG 18); `postgis/postgis` só amd64. Passos 6 e 11 ajustados, ADR de região no 11, Terraform e provedor no `versions.md` |
| 2-A5 | Aceito com ajuste | Auditoria na transação, conversão versionada e contrato JSON entram no passo 7 (22.2). O documento de entrada vai para o primeiro PR da F1 (passo 14): é entidade da F1 e já nasce com auditoria; nenhuma rota grava antes dela |
| 2-A6 | Aceito | Disputas com chaves diferentes (passo 14), versão esperada desatualizada (passo 7), chave natural e restrição única (passos 5 e 14). O teste de estorno acompanha o estorno, se o corte do 1-A8 o adiar |
| 2-A7 | Aceito com ajuste | Login decidido no passo 3, com custo e fonte; URL controlada ou exceção ENG-005 no passo 11; nenhuma senha em mensagem, seed ou repositório; `demo:reset` só por comando explícito, com recusa testada fora de DEV e HML. Ajuste: em vez de senha por canal separado, preferir a conta Google dele com troca de papel de teste só na HML |
| 2-A8 | Aceito com ajuste | A PEND-REPO-01 não entra no pedido agora: plano e preço não verificados, e a AGENTS §3.1 exige estimativa com fonte (ver 1-A3). Em troca, exceção ENG-005 com escopo, compensação, aprovador e vencimento, exigida antes do passo 14. Revisão humana qualificada declarada pendente (31.5); MFA e SonarQube com aprovador e vencimento; antecipação da F0 registrada na R-006 (passo 3) |
