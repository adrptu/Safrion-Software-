# Estado do projeto

Base do retrato histórico abaixo: 09/10/2026, Claude, `main` `266a682`. Estados e recibos posteriores estão no [checkpoint único](https://github.com/adrptu/Safrion-Software-/issues/1#issuecomment-5858061746). PR aberto não significa integrado; configuração só vale depois de lida no servidor.

**Prioridade de execução:** concluir e validar o conjunto vigente do protótipo, publicando incrementos operáveis conforme seus aceites. A reconciliação integral do PRD aguarda todas as implantações atuais. Após validação integral do protótipo, transferir para a aplicação existente por fatias tela → domínio → banco → HML. CMD-15, C2 e demais trabalhos reais permanecem preservados; F1 técnico de estoque não equivale à Fase 1 comercial.

PR #54, complemento VEL: revisão apontou lacuna em exceções concorrentes e harness ausente. Corrigidos com referência estrutural exata das cinco exceções, regra única sem sobrescritas, herança padrão intacta, fonte portátil e prova antes/depois (8 testes e 15 mutações recusadas; 16/16 execuções); aguardam revisão do Claude e checks da nova candidata. Sem alteração funcional do protótipo.

## Skills da equipe — incremento de 14/10/2026 (PR #67)

Pacote [SKILLS-20261014](parceria/skills/2026-10-14/revisao.md): 16 skills compartilhadas Codex/Claude e quatro específicas do Gemini, com fontes, diff e manifesto. Autoria Codex; Claude revisa e integra. Instalações locais foram conferidas; revisão/integração e distribuição/leitura na sessão Claude cloud continuam pendentes (recibos 6173812429/6173991485). O pacote no repositório não é carregado automaticamente. Claude confirmou em 6174440253 que estas 20 skills ainda não estão carregadas na sessão cloud; cópia e recibo de hashes ocorrerão após aceite. A rodada atual corrige os seis pedidos do revisor, as referências recuperáveis/legais e dois defeitos da biblioteca de tabelas apontados pelo bot. Contraprova no navegador: quatro cenários vermelhos antes, cinco verdes depois; teste portátil em provas/tabela/regression.html.

Validação: 20/20 skills, zero links locais ausentes; adaptador 17/17 sem rede/autenticação. Correção da revisão 4273864164: a suíte agora usa as raízes `shared/` e `gemini/` do próprio pacote, confere caminho/hash de cada seleção e passa 17/17 com diretório pessoal simulado inexistente; a versão anterior falhou nessa contraprova. Comando reproduzível: `python3 -m unittest -v docs/parceria/skills/2026-10-14/test_gemini_consult.py` (Python 3.11+; verificado em 3.11 pelo Claude e 3.12 pelo Codex). Próximo passo: Claude critica a candidata atual, integra após os checks e confirma os caminhos/hashes efetivamente disponíveis na sessão. Não altera autenticação, permissões, limites de consulta, produto, HML ou produção. Estado e instalação local não equivalem a distribuição remota concluída.


### Revisão devolvida 6177603041 — 14/10, Codex

Os seis pedidos anteriores foram aceitos pelo Claude. Esta rodada corrige os novos pontos: agg nulo por padrão (soma exige escolha explícita), autosave em fila com confirmação após save, outbox obrigatório nos comandos Safrion e modelo ESLint renomeado para eslint.config.exemplo.js. O teste portátil provas/correcoes/regression.html reproduziu quatro falhas antes; agora passa 7/7 (ordem, reversão, retry, duplicata e agregação). As regressões anteriores da tabela passam 5/5.

Renomear o modelo resolveu a procura indevida de sonarjs, mas o lint revelou 62 erros dos assets/modelos. Corrigidos os usos de expressões e deletes, e acrescentado ao eslint.config.js da raiz um override somente do pacote versionado: globais browser nos dois assets; modelos sem projeto TS usam lint sem verificação de tipos. Lint continua ativo; regras de produto e segurança não foram desabilitadas. ESLint 10.11.0 executado com configuração da raiz e dependências existentes: zero erros/avisos no pacote e config. Isso não substitui o CI integral.

Validação: 20/20 skills, 17/17 adaptador, 53 arquivos no manifesto; Gitleaks dir do pacote sem achado. Gitleaks histórico geral é pendência separada relatada por Claude, commit207f362; nenhuma allowlist/proteção/branch foi alterada. Revisão, integração e recibo cloud continuam pendentes.


### Complemento de saída e formatação
Achado4275898120 tratado: beforeunload não inicia save assíncrono; pede confirmação quando existe edição sem recibo ou gravação pendente. Teste do guard em eventos canceláveis no navegador: 10/10; a versão46e6ded falha nos dois casos de saída. Não prova comportamento de encerramento forçado/mobile, cujos limites estão na skill. Gatilho de persistência local depende da autorização e contrato do produto.
CI Código do46e6ded falhou em Prettier (log116086875772), no eslint.config.js: corrigido com .prettierrc.json canônico (singleQuote true, printWidth110). Prettier e lint do pacote/config executados com sucesso;20/20skills e17/17adaptador. Demais provas continuam válidas.

## Onde estamos

| Frente | Estado | Evidência |
|---|---|---|
| PRD | **v3.11** (27/09/2026), vigente desde o merge do #48 em 09/10/2026: 40.5 e 40.6, produto fixo ou troca de marca pelo mesmo ingrediente ativo; API de integração com credencial por integração; sobre a **v3.10**: caps. 73 (confiabilidade transacional, offline, desempenho), 74 (design system) e 75 (melhoria contínua), com as seções existentes reconciliadas. Decisões pendentes continuam pendentes em 73.12, 74.12 e 75.8 | `docs/PRD.md`; `docs/prd/v3_10-reconciliacao.md`; `docs/DECISIONS.md` |
| Fluxogramas | v3.10: 14 dos 63 fluxos alterados, mesmas raias; v3.9 mantida ao lado | `docs/prd/fluxogramas/` |
| Protótipo | Navegável, com dados sintéticos e sem banco ou login reais. Regime leve (AGENTS 3.5): branch única `claude/prototipo-v44`, PR #47 em rascunho; versão publicada, candidata em revisão e frentes pendentes identificadas separadamente no checkpoint; publicação parcial não encerra o conjunto | https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm |
| Design system | PRD cap. 74 e os padrões do proprietário de 09/10 (DEC-0910-01): botões BOT-01 a BOT-09, seleção que abre detalhe (SEL), etapa futura neutra (ETP) e separador, hover verde, retorno visual e dica (VIS). SEL-02, BOT-03 e BOT-07 precisados pela revisão do Codex no PR #50 (DS-NAV-20261009-02): registro indisponível com aviso e recuperação, Programar só para agendar execução e alvo único semântico na linha. No protótipo: componente comum e teste de conformidade em andamento; correção das telas depois da integração das frentes. No software real (`packages/ui`): pendente | `docs/design-system/README.md` |
| Merge na `main` | Feito pelos agentes: o revisor integra o PR do outro com CI verde e parecer escrito; ninguém integra o próprio (DEC-0910-02, 09/10) | `AGENTS.md` 2 e 3 |
| Decisões delegadas (09/10) | Delegação do proprietário aos dois agentes (DEC-0910-03) e 30 linhas com acordo escrito do Codex (recibos 6091153950 e 6091443216), cada uma com o seu limite; 24 entradas aguardam a revisão do Codex. Nada é aprovação do proprietário; o PRD fica inalterado até a comparação final; implementação pendente | `docs/DECISIONS.md`; `docs/parceria/decisoes-delegadas-20261009.md` |
| Repositório | Privado; PRs #2 a #31, #46 e #48 integrados | https://github.com/adrptu/Safrion-Software- |
| Fundação | Domínio (decimal, unidades e saldo por lote); PostgreSQL/PostGIS com RLS e isolamento entre organizações; login OIDC com sessões; concessão e revogação de acesso; primeira interface de estoque e cadastros; imagens de homologação verificadas na CI | PRs #5, #7, #8, #9, #10 e #11 |
| Homologação | Terraform, conexão ao banco por IP privado e fila de vínculo integrados e validados na CI, sem plan nem apply. **Nenhum ambiente hospedado ainda**: desenvolvimento, QA e HML já estão autorizados com referência de custo (EXT-01, R-006); falta provisionar e comprovar o ambiente, dentro dessas autorizações concretas (plano revisado antes de cada apply; alerta de orçamento não é teto) | PR #14; `infra/terraform/`; `docs/OPERACAO.md`; EXT-01 em `docs/DECISIONS.md` |
| Proteção da `main` | Ruleset `24154464` ativo, conferido na leitura do servidor (alterado em 29/09, 10:13 de Brasília): exclusão e force push bloqueados, pull request obrigatório e os 10 checks obrigatórios do app GitHub Actions, com branch atualizada antes do merge. Sem exceção de bypass. **Merge automático do revisor** (09/10): o portão "Revisão do Codex no commit atual" e a resolução obrigatória das conversas estão no arquivo do ruleset (PR #49), mas só valem depois que o proprietário autorizar aplicar o ruleset e ligar o auto-merge do repositório | PR #15; PR #49; `tools/github/`; AGENTS.md 3 |
| Produção | Não existe | — |

## Verificação executada e limite

- **VEL-20261013-01 (PR #53 integrado pelo Claude em `999b0d0`, autoria Codex):** autorização direta de Adrianus para a exceção da chave localStorage da ficha de pivô, limitada a um literal e dois arquivos, e para AGENTS §3.5/3.6. Gitleaks 8.30.1: 30/30 scans sintéticos executados; [fonte, brutos e reprodução](parceria/rodadas/VEL-20261013-01/README.md). Complemento em revisão: contrato dos limites na descoberta existente da CI (8/8 testes e 15 contraprovas recusadas; 16/16 execuções, incluindo path/regex da regra e disabledRules) e este registro. Próximo passo: Claude revisa/integra o complemento após os checks e confere a composição real antes de publicar suas branches. Sem custo novo, publicação de produto ou conclusão de CTL-4/v56 por este incremento. Estado posterior no checkpoint único.
- PR #14, candidata `a1c880e`: 10 checks com success; 247 testes unitários; integração com PostgreSQL real, 171 testes em 16 arquivos, nenhum pulado; jornadas de navegador no desktop e no celular; imagens com SBOM; Terraform validado sem credencial.
- PR #15, candidata `b300f6ad`: 10 checks com success, inclusive a regressão da proteção da `main` (`tools/ci/test_protecao_main.py`); simulação contra o GitHub real só com leitura.
- CI verde não prova operação hospedada, login com provedor real na homologação nem restauração de backup.

## Próximo passo e responsáveis

### Dependências de HML e registros históricos

A lista abaixo preserva dependências e recibos; não substitui a prioridade de execução indicada acima. Não reiniciar checks ou trabalhos já encerrados sem novo incidente ou mudança pertinente.

1. Feito em 29/09: os 10 checks obrigatórios estão no ruleset existente, conferidos na leitura do servidor.
2. Ensaio remoto da homologação, dentro das autorizações concretas já recebidas (EXT-01, R-006): restauração do backup em instância isolada, logs sem dados pessoais, acesso e revogação.
3. Antes do primeiro usuário externo: teste de todas as rotas com usuário de outra organização e inventário dos dados pessoais tratados.
4. Feito em 09/10: PRD v3.11 vigente (#48). As decisões pendentes (73.12, 74.12, 75.8) continuam com o proprietário.
5. Design system de 09/10: aplicar BOT, SEL, ETP e VIS no protótipo (componente comum, teste de conformidade e correção das telas depois da integração) e, ao passar para o software real, em `packages/ui`.
6. Codex e Claude conduzem a homologação técnica e funcional. Adrianus recebe a candidata verificada e dá feedback; produção exige o aceite explícito dele para a versão.

### Segurança estática — FERR-06

Semgrep CE 1.178.0 acrescenta duas regras locais: verificação TLS desabilitada e entrada de requisição usada no texto SQL. O alcance é intraprocedural; não certifica autorização, isolamento, fórmulas, migrações SQL ou todos os caminhos de injeção. Valores parametrizados são o contraexemplo seguro. Testes nativos `ruleid`/`ok` precisam detectar os positivos sem marcar os negativos. O guard rejeita relatório vazio, erro de parser reportado, regra ignorada, timeout de análise e inventário incompleto de JS/TS em `packages/*/src`, `apps/*/src` e na raiz desses pacotes (inclusive `next.config.ts`). Os pré-filtros do scanner podem dispensar o parse de arquivos sem padrões pertinentes: inventário não comprova sintaxe integral. A compilação TypeScript continua obrigatória em outro job.

Local: `python3 tools/ci/check_semgrep.py --semgrep /caminho/semgrep .` (mesma versão). CI: workflow próprio, imagem oficial por digest, código montado somente para leitura e rede desativada no container; sem login, métricas, regras remotas ou envio de achados. Os fixtures sintéticos são excluídos do lint tipado/formatação e verificados pelo scanner nativo. Resultados locais, CI e pareceres por versão ficam no PR e na issue #1; presença de configuração não equivale a gate executado/aprovado nem a proteção aplicada à main.

O Dependabot cobre GitHub Actions; pacotes, lockfile, imagens e ferramentas ficam com o Renovate (PR #12), cujo primeiro PR automático ainda não foi comprovado. Sonar (ENG-018) permanece pendente de consumidor/conta e comprovação do gate. Playwright e axe rodam na CI (jornadas de navegador). Terraform (formatação, init sem backend e validate) e TFLint rodam na CI de infraestrutura (`infra.yml`); plan, apply e hospedagem continuam pendentes. Testes de carga, ZAP e telemetria exigem alvos concretos. Nenhum item pendente é contado como ativo.

## Jornadas de navegador na CI

O workflow `.github/workflows/navegador.yml` executa as jornadas Playwright/axe existentes em runner Ubuntu 24.04, com Chrome do runner e PostgreSQL/PostGIS efêmero fixado pelo mesmo digest da integração. Não usa segredos, dados reais ou serviços GCP. A versão efetiva do navegador fica no log; ela acompanha a imagem do runner e não é fixada pelo projeto.

`tools/ci/conferir_e2e.py` exige no mínimo nove jornadas desktop e uma celular, incluindo a nova jornada do pedido de acesso, resultado real aprovado em uma tentativa, nenhum skip/falha esperada/erro global e totais coerentes. O recibo publicado contém só commit, nome e resultado dos casos; traces, cookies e relatórios brutos não são artefatos publicados. A regressão recusa o relatório antigo de oito desktop e uma celular. A execução remota e a revisão tripla por versão são registradas no PR correspondente e na issue #1.

Essa prova usa a aplicação e o banco reais em modo DEV, com identidades fictícias. Não demonstra autenticação com provedor real, hospedagem funcional nem autonomia remota dos agentes. Os serviços descartáveis pertencem somente ao job e são removidos pelo runner.

Referências consultadas em 28/09/2026: [Playwright na CI](https://playwright.dev/docs/ci-intro), [relatório JSON](https://playwright.dev/docs/test-reporters#json-reporter), [serviço PostgreSQL](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers) e [inventário do runner Ubuntu 24.04](https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md).

## Condições preservadas

- Segredos e dados reais nunca entram em código, testes ou logs (`AGENTS.md`, `SECURITY.md`).
- Conta, gastos, dados de clientes e produção dependem da autorização concreta do proprietário.
- Os agentes usam a mesma identidade GitHub; parecer independente precisa identificar agente, versão, testes e limites. Proteção efetiva da `main` deve ser comprovada pelo servidor; um arquivo de configuração não prova aplicação.
- Versões da fundação: `docs/architecture/versions.md`. Decisões materiais pendentes: `docs/DECISIONS.md`.


### Correção dimensional e nodata — 14/10, após 8d08d81
Achados 4275977677/4275977687: população agora usa 10 000 m²/ha e espaçamento em metros; exemplo 10 plantas/m a 0,50 m = 200 000 plantas/ha, massa de sementes expressa por hectare. Escala/estatística retornam null sem amostra suficiente; cor/classe/máscara preservam o estado desconhecido. Mínimo operacional é configurável e não implica validade agronômica. Máscara retorna Uint8Array real, sem cast enganoso.
Contraprova extraída das próprias referências: antes 2/22, depois 22/22; nodata, vazio, único, uniforme, mínimo configurado, escala inválida e conversão dimensional. Teste portátil em provas/dominio/; usa TypeScript já instalado, sem consulta paga ou dado real. 20/20 skills, 17/17 adaptador, 53 arquivos, 33 alterados versus origem. Manifesto d730419fce7bc2dfe105c8c370db0839f82dee0dee6e46852479d4adf47b2029.
CI Código no8d08d81 verde; Gitleaks histórico permanece separado, sem alteração de proteção/ignore/branches. Revisão crítica, integração e recibo de carregamento cloud pelo Claude continuam pendentes.


### Revisão dos limites e campos múltiplos — depois de7cbf30e
4276288655/8673/8682/8694 tratados: Escala declara modo absoluta/relativa, classificação absoluta usa os limites da paleta (superiores exclusivos, última classe inclui o final), estado derivado indisponível não vira Normal. Impurezas percentuais removidas da massa bruta antes da correção de umidade do grão limpo, com unidades, hipótese e referência Embrapa; descontos comerciais separados. Autosave mantém valores repetidos como arrays, sem perder alterações no primeiro valor; campo simples preserva string.
Contraprovas: domínio40/54 antes,54/54 depois; navegador11/14 antes,14/14 depois. As provas e teste portátil foram atualizados, sem repetir bateria não afetada. Lint do asset e do teste sem erros;20/20skills,17/17adaptador,53arquivos/33alterados. Manifestodfb5f405715d35910684fd6c3446b0466fb3fd83548da073b32fa939d015de12. Revisão crítica/integração pelo Claude e recibo cloud pendentes. Não houve mudança no produto ou nas proteções.


### Ciclo de vida e seleção completa — depois de 31c468f
Achados 4276380641/651/657 tratados: autosave oferece destroy(), remove os três ouvintes, cancela debounce e descarta envios ainda na fila; gravação já iniciada pode terminar, sem feedback na tela desmontada. A skill exige resolver antes salvar/preservar/descartar o rascunho. Selecionar tudo/resultados usa todo o universo correspondente, sem o limite de 500 opções exibidas. Checklist de satélite referencia a tabela de estados, incluindo Sem dado.
Contraprovas executadas: autosave/agregação 14/18 antes → 18/18 depois; tabela 7/9 antes → 9/9 depois, com 601 valores. Lint dos dois assets passou; 20/20 skills, 17/17 adaptador; provas de domínio 54/54 anteriores preservadas, sem mudança no domínio. Manifesto df191a04efd0348ac0ec067249aa701ac2dbb55c2732f41b1c922f9736ce3efa. Revisão final, integração pelo Claude e recibo cloud pendentes.


### Rodada Claude 6179132314 — falhas de autosave e cor/classe
AUTOSAVE-FALHA-01: flush retorna ok/reason, dirty/pending públicos, destroy recusa pendências sem decisão explícita e fecha o snackbar. AUTOSAVE-TRAVA-01: prazo finito e AbortSignal; timeout informa incerteza e libera as promessas da fila com falha, mas impede escrita concorrente até o transporte terminar. Preservação/reconciliação obrigatórias se não houver término; não fingir cancelamento remoto. AUTOSAVE-MULTI-01: checkbox e select múltiplo sempre arrays, inclusive vazio. SAT-COR-CLASSE-01: modo absoluto usa a própria cor da classe; relativo mantém rampa. Notas S4 relacionadas: contrato máscara/nodata→NaN, intervalo NDVI, minAmostra finito, misturaHex implementada. Filtro cruzado anterior ao delta permanece registrado pelo revisor, fora desta rodada.
Contraprovas executadas: navegador 17/30 → 30/30; domínio56/68→68/68. Corrige a menção oral31/31: são30 cenários. Validador 20/20 skills, 17/17 adaptador. Lint do asset no caminho real do pacote passou, sem alteração de config/ignore/regras. Manifesto 8a31a5b58a4c5b4d1be4132836398804f7decbeabe7e5003cacee93e1537c3eb. Testes equivalentes da tabela9/9 preservados, arquivo não alterado. Revisão/integração Claude e recibo cloud pendentes. CI do novo head pendente.

### Rodada R9 — abort local não prova término remoto (4276675196)
Corrigido P1 do autosave: rejeição após AbortSignal mantém estado incerto; reconcile exige resultado terminal da operação e snapshot confirmado. GET momentâneo não basta. Rascunho preservado, sem envio automático. Época invalida recibos tardios e readbacks ultrapassados. Contraprova inicial 30/34; final 36/36 no navegador. Validação 20/20 skills e 17/17 adaptador; lint do asset no caminho real passou. Domínio 68/68 e tabela 9/9 anteriores preservados, sem alteração. Manifesto 40ec0c53c4a29034f35688f9beaf5b31614f3ddd11f64c5468eee0b104408ff4. Revisão/integração Claude e recibo cloud pendentes.

### Rodada R10 — retorno observável e legibilidade (Claude 6179465714)
O ramo de gravação incerta renova o aviso a cada tentativa, mesmo após expiração, fechamento ou substituição do snackbar. Mantém o bloqueio da escrita e o rascunho; não afirma sucesso. Contraprova 36/37 antes, 37/37 depois. Validação 20/20 skills, 17/17 adaptador e lint passaram. Manifesto 9c4eb391308ca9d5c225eff4803b02288feb948d2d6754b129b22dccdce9b1b5. Textos correntes revisados e README distingue as contagens históricas das atuais. Revisão final Claude e recibo cloud pendentes.
