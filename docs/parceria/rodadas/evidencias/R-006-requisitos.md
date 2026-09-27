# F0 e F1: requisitos mínimos para a primeira homologação

Autor: Claude Code (subagente), 27/09/2026. Fontes: PRD v3.9 (`docs/PRD.md`), `AGENTS.md`, `docs/STATUS.md`, `docs/DECISIONS.md`, ADR 0001–0002, comando-mestre v2.1 do Codex, personas v1.1, rodadas R-002 e R-004, rascunho v3.10 do cap. 73 (73.3, 73.7–73.8: **em revisão, ainda não vigente**).
**Rótulos.** Tudo aqui é **especificado**: está escrito na fonte, mas nada foi implementado nem testado. **[verificado]** marca o que conferi agora, lendo arquivos. Quando falta fonte: "não verificado". Quando a fonte não traz ID: "sem ID no PRD".

**Situação [verificado].** O STATUS registra "Código de produto: Nenhum": não há backend, banco, integração nem implantação. A CI remota não executou porque a conta do GitHub está bloqueada. O protótipo WPDgqGvKX6CYTCdPjidBLo serve para validar o desenho e **não é homologação** (AGENTS §1).

## 1. F1: receber insumo por lote e local e ver o saldo

**Resultado útil.** O almoxarife registra a chegada de um insumo com documento, lote, validade e local e separa o apto do bloqueado. O gerente vê o saldo certo por lote e local, com a trilha de cada movimento.
**Origem.** Comando-mestre, "Fila inicial" item 2; R-002 §5, aceita pelo Codex; DEC-2609-13, prioridade 1 (PRD 72.2); telas SU-03, SU-06 e CD-06; formulários FO-18 e FO-25.

### 1.1 Personas (R-002 §4; personas-e-criterios.md)
| Persona | Papel na F1 | Como verificar (critério da persona) |
|---|---|---|
| PER-18 Almoxarife | Recebe, confere, segrega e libera | Não edita saldo diretamente; o saldo nasce do fato |
| PER-33 Gestor de cadastros | Cadastra o produto (unidade-base, embalagem, lote e validade) e o local | Cadastra uma vez, sem pedir campos de outras classes; o produto não tem saldo editável |
| PER-02 Gerente | Consulta saldo e trilha, sem receber | Não precisa de planilha paralela; vê cada pendência com o responsável |
Os acessos de teste vêm da carga sintética. A PER-34 (administrador) fica fora da tarefa.

### 1.2 Entidades e estados
| Entidade | Dados mínimos (fonte) | Estados na F1 | Ação primária por estado |
|---|---|---|---|
| Produto | Código e nome, categoria, unidade-base, unidades de compra e uso com conversão da embalagem, controle de lote e validade, local padrão (FO-25, CD-06) | Ativo/Inativo; sem máquina de estado no PRD (8.1 não inclui produto) | Ativo: Receber; Inativo: Reativar |
| Local de estoque | Nome, fazenda, proprietário, capacidade quando houver (CD-06, FO-25) | Sem ID e sem estados no PRD | Ver saldo do local |
| Lote | Produto, lote do fabricante, validade, proprietário (SU-03; 11.1) | 8.1: Recebido → Em inspeção → Liberado; Bloqueado. Em processo, Esgotado e Destinado ficam fora | Em inspeção: Liberar; Bloqueado: Ver motivo; Liberado: Ver movimentos |
| Documento de entrada | Número, data, emitente e linhas com item, lote, quantidade, unidade, validade, condição e local; quantidade aceita, bloqueada e recusada (FO-18, SU-06) | Rascunho → Confirmado; corrigir só por estorno vinculado (ENG-026, RN-044). Sem ID no PRD para esses estados | Rascunho: Confirmar recebimento; Confirmado: Ver saldo |
| Movimento | Tipo, item, lote, local, quantidade com unidade original e unidade-base, documento, autor, versão e correlação (SU-08; 11.2) | Imutável depois de confirmado (ENG-026) | Abrir o documento de origem |
| Saldo (calculado, não editável) | Por item, lote, local e proprietário: físico; bloqueado, quarentena e vencido sem sobreposição; utilizável (apto); reservado; disponível (livre); custódia (SU-03; glossário 21.1) | Na F1, reservado e custódia ficam em zero (entram na F2 e na F3) | Ver movimentos |

**Apto e não apto** (21.1; RN-015):
- O físico inclui o material apto e o não apto.
- Utilizável = físico menos a **união** de quarentena, bloqueio e vencimento. Um lote com duas restrições não é descontado duas vezes.
- O vencimento é avaliado na data de uso ou de consulta; não é um estado gravado.
- Disponível = utilizável menos as reservas ativas (RN-011).
- Quantidade recusada não entra no físico (FO-18; PRD, linha 4237).

### 1.3 Comandos
Todos usam o envelope de 8.2.1: organização tirada da sessão, ator, escopo, versão esperada e chave de idempotência. O retorno traz ID, versão, efeitos, pendências e próxima ação. Consultas não levam chave (IDEM-02, v3.10).
| Comando | ID | Pré-condição | Efeito confirmado |
|---|---|---|---|
| Confirmar recebimento | CMD-15, "Receber compra / almoxarife" | Origem e conferência válidas; produto ativo; lote e validade quando o produto os controla; local válido; permissão | Movimento físico, aceito ou bloqueado, por lote e local. SU-06 mostra o utilizável e a divergência. Documento repetido não gera segunda entrada (SU-06) |
| Liberar após inspeção (quarentena → apto) | Sem ID no PRD para material. O CMD-24 vale para lote de produção (CO-07); em SU-06 é o botão "Liberar qualidade" | Lote Em inspeção; responsável autorizado | Soma ao apto uma única vez (DEMO-02) |
| Bloquear ou segregar | Sem ID no PRD; botão "Segregar" em SU-06 | Motivo informado | Sai do apto; o físico não muda |
| Estornar recebimento com vínculo (recomendado) | Sem ID no PRD; botão "Estornar com vínculo" em SU-08 | Motivo; lote sem uso posterior | Movimento reverso vinculado; o original é preservado (ENG-026, RN-044) |
| Cadastrar produto ou local | Sem ID no PRD (FO-25) | Campos essenciais; duplicidade verificada | Cadastro versionado, sem saldo |
Motivo para incluir o estorno: na homologação, um erro de digitação precisa de correção, e saldo nunca se edita.

**Decisão a fechar na tarefa do Codex.** FO-18 pede "Pedido/origem", mas a F1 não tem pedido de compra (RF-SUP-006, onda E2). Proposta: a origem é o documento do fornecedor (número, data e emitente), sem pedido. É decisão técnica dos agentes e não muda regra de negócio.

### 1.4 Regras
- **RN-001:** repetir um comando não repete o efeito.
- **RN-003:** o documento guarda empresa, versão e origem; filtro de navegação não altera dados (AC-05).
- **RN-011:** reserva não altera o físico.
- **RN-015:** quarentena, bloqueio e vencimento ficam fora do utilizável.
- **RN-032:** dado ausente não é zero; validade não informada não quer dizer "sem validade".
- **RN-033:** toda quantidade tem unidade e base.
- **RN-044:** alteração material registra causa, autor e versão; comprovante confirmado não se edita.
- **RN-045:** função fora do escopo do perfil não aparece.
- **Saldo nasce de movimentos** (FO-25, FO-32, RF-SUP-003): produto sem saldo editável e nenhuma edição direta de saldo.
- **Documento não substitui conferência física** (RF-SUP-007). Aceite físico e aprovação financeira são estados distintos (SU-06).
- **Precisão** (10.0, ENG-013, 24.1): quantidade em decimal com escala interna de 6 casas, exibição de até 3, JSON com texto decimal e nenhum ponto flutuante binário.
- **Unidades** (CD-06, FO-25): insumo sem unidade implícita; conversão da embalagem versionada.
- **Preenchimento** (AGENTS §3.3; R-004 §3): produto por busca; unidade herdada; local sugerido, visível e corrigível; nunca o último valor para lote, quantidade ou validade.
- **Tela** (AGENTS §4; PRD 4.2–4.3): master-detail, uma ação primária por tela e estado sempre visível.

### 1.5 Aceites observáveis
| ID | Caso | Resultado esperado |
|---|---|---|
| RF-SUP-003 (P0/E1) | Abrir o saldo de um lote | Físico, bloqueado, utilizável, reservado, livre e custódia, todos explicados por movimentos; editar o total é impossível |
| RF-SUP-007 (P0/E1) | Receber 60, com 10 bloqueadas | 50 utilizáveis; o documento vinculado não substitui a inspeção |
| AC-14 | Recebimento de 60, com 10 em quarentena | Físico 60, apto 50 e os demais saldos separados |
| DEMO-02 (só a parte sem pedido) | Liberar as 10 em quarentena | O apto passa a 60 uma única vez; repetir não soma de novo |
| AC-20 (parte da F1) | Lote com validade vencida | Fica fora do apto na data consultada; a tarefa de destinação fica fora da F1 |
| AC-02 e AC-03 | Abrir linhas; filtrar, ordenar, agrupar e voltar | Cada linha abre o próprio ID; filtros e posição são mantidos |
| AC-04 | Gerente tenta receber pela URL ou pela API; usuário de outra organização consulta o lote | Acesso negado, sem revelar dados |
| AC-05 | Trocar a fazenda com um documento aberto | O documento não muda |
| AC-73, AC-74, AC-84 e AC-87 (v3.10, em revisão), aplicados ao CMD-15 | Resposta perdida seguida de reenvio; mesma chave com outro conteúdo; 10 envios simultâneos; recarregar a web | Um único movimento e o mesmo recibo; conflito `IDEMPOTENCY_KEY_REUSED` sem efeito; uma única execução; consulta pela chave antes de reenviar |
| NFR-04 | Auditoria do recebimento | Autor, antes e depois, versão, motivo e correlação |
| 29.3; PERF-02 e PROJ-06 (v3.10) | Tempo de resposta | Comando no servidor: p95 ≤600 ms. Do toque ao recibo: p95 ≤2 s e p99 ≤4 s. Lista e detalhe: p95 ≤2 s. A própria tela lê o que o commit gravou (classe 1); SU-03 em outra tela atualiza com p95 ≤5 s e p99 ≤15 s (classe 2) |
| NFR-09 | Acessibilidade | WCAG 2.2 AA na tarefa inteira, também pelo teclado |

### 1.6 Tarefa curta do proprietário em homologação
Base: R-002 §5 e comando-mestre F1. Os dados são fictícios; o galão de 5 L e o lote F26-02 vêm do AC-72-05, e o lote F26-03 foi criado para o teste.
1. Entrar como Almoxarife, com usuário de teste.
2. Receber o documento NF-TESTE-001: 3 galões de 5 L de Fungicida A, lote F26-02, validade futura, no Depósito Central, tudo apto. Conferir: físico 15 L, apto 15 L, bloqueado 0.
3. Receber o documento NF-TESTE-002: 2 galões do lote F26-03, um deles avariado. Aceitar 1 como apto e bloquear 1 com o motivo "avariado". Conferir o lote F26-03: físico 10 L, bloqueado 5 L, apto 5 L. Conferir o produto: físico 25 L, apto 20 L.
4. Abrir a trilha: 2 documentos e os movimentos, com autor e hora.
5. Tentar confirmar a NF-TESTE-001 de novo: o sistema mostra o recebimento que já existe e não soma.
6. Entrar como Gerente: aparecem os mesmos saldos, sem o botão de receber.

### 1.7 Fora da F1 (fatia de destino)
- **F2:** reserva (CMD-44, RF-SUP-008). Depende da v3.10 revisada, §§73.4–73.5.
- **F3:** entrega e custódia (CMD-16).
- **F4:** consumo, devolução e encerramento (CMD-17, CMD-45, CMD-10, CAL-02 completa, ESTOS).
- **F5:** offline, app de campo e `/sync` (RN-038, ENG-028, NFR-08).
- **Item 7 da fila:** pedido, cotação e recebimento parcial contra pedido (RF-SUP-004..006, FL-10).
- **Item 8 da fila:** título e financeiro (GE-04, RF-SUP-011). ERP Sankhya/TOTVS (cap. 66; RN-036); a integração real depende do proprietário (AGENTS §2).
- **Fatias posteriores, sem número definido:** transferência entre locais (RF-SUP-009) e inventário com ajuste (RF-SUP-010). As duas estão na prioridade 1 da DEC-2609-13, mas não na F1.
- **Sem fatia definida:**
  - consignação e estoque de terceiros (RN-014);
  - valor e custo do lote (SU-03, "valor/origem"; CAL-04);
  - necessidade líquida e projeção condicionada (CAL-01; 65.4);
  - leitura do XML da nota (R-004: melhoria medida depois);
  - anexos e fotos (ENG-046);
  - destinação de vencido;
  - portal, IA (CMD-38) e cobrança.
- **Captura de feedback no software** (print e comentário): o comando-mestre a exige "antes do primeiro piloto". Não está verificado se ela é exigida já na homologação da F1; decidir entre os agentes.

## 2. F0: o mínimo de que a F1 precisa
Regra de entrada (PRD 22.2): nenhuma rota que grava dados nasce antes de autorização, auditoria, isolamento, comando/evento, contrato de erro e convenção de unidades. A F0 não vai à homologação; prova-se na CI (R-002 §5).
| Item | Fonte | Por que a F1 depende | Na homologação da F1 |
|---|---|---|---|
| Monorepo pnpm, versões fixadas, TypeScript estrito, lint e formatação | ENG-006..010; 23.1–23.3; ADR 0001; `docs/architecture/versions.md` [verificado: o arquivo existe] | O candidato precisa de build reproduzível e da mesma imagem por digest (27.4) | Obrigatório |
| CI verde no commit candidato | 25.2; ADR 0002; comando-mestre, passo "Rodar CI" | Sem CI não há evidência para liberar a candidata | Obrigatório. **Bloqueado [verificado]:** CI remota parada pela conta. SonarQube (ENG-018): licença e custo não verificados; se ficar pendente, declarar qual controle, impacto, dono e condição de conclusão (31.5) |
| Identidade e papéis | ENG-042; 2 e 2.1; 11.1; CF-01 | O almoxarife recebe; o gerente só consulta | Obrigatório: login real com usuários de teste. Provedor OIDC e custo: não verificados. MFA de administrador: adiável só com dados fictícios, registrando exceção pela ENG-005 |
| Isolamento por organização | ENG-021, ENG-024, ENG-025 (RLS; credencial da aplicação sem `BYPASSRLS`); 24.1; NFR-02; AC-04 | Vazamento entre organizações é S1 | Obrigatório, com teste na credencial real da aplicação (Testcontainers) |
| Autorização no servidor | ENG-043; NFR-03; RN-045 | Botão oculto não é controle | Obrigatório |
| Envelope de comando e idempotência | 8.2.1; 12.2; 24.1; ENG-021; IDEM-01..18 (v3.10) | Sem isso, o reenvio do CMD-15 duplica a entrada (S2) | Obrigatório. A retenção por validade de pacote offline (IDEM-19, PEND-02) é adiável: a F1 não tem offline |
| Efeito, recibo e outbox atômicos | ENG-022; IDEM-16; INTEG-01 (v3.10) | Queda entre gravação e resposta não pode perder nem duplicar | Obrigatório gravar os três na mesma transação. Publicador ou worker da outbox: adiável até existir consumidor (proposta minha; PROJ-02 prefere consulta direta) |
| Movimento imutável e saldo calculado | ENG-026; RF-SUP-003; CAL-02 (fórmula do físico) | É o coração da F1 | Obrigatório, com testes de unidade e propriedade (fast-check) |
| Precisão e unidades | 10.0; ENG-013; NFR-14; RN-033; 24.1; FO-25 | Galão ↔ L e saldo em decimal | Obrigatório. A política de 10.0 é "proposta a homologar" antes do primeiro cálculo produtivo |
| Contrato de erro e validação de entrada | ENG-014 (Zod); ENG-015; 12.3 | Erro de validação, de permissão ou de conflito com mensagem útil | Obrigatório |
| Dados sintéticos e `pnpm demo:reset` | 16.1; ENG-017; 23.4; 27.4 | Tarefa repetível, sem dado real | Obrigatório (nomes e documentos fictícios) |
| Ambientes DEV e HML separados | 27.4; NFR-24; AGENTS §3.1 | "Homologação local não substitui a hospedada" (comando-mestre) | Obrigatório. HML hospedada exige conta e custo: **autorização do proprietário** com estimativa e fonte oficial. PROD: adiável |
| Observabilidade mínima | ENG-081; ENG-015; ENG-049; 30.2, painel "Integridade" | Diagnosticar falha e tentativa de duplicidade | Obrigatório: log estruturado com `correlation_id`, sem dados sensíveis. Adiável: painéis completos, alertas com plantão (ENG-083/084), SLO e error budget (29.5) |
| Backup e restauração | ENG-085; 30.5; IDEM-20 | Na HML os dados são fictícios e recriáveis | Adiável sem risco. Mínimo: migração do zero reproduzível. Exercício completo obrigatório antes da 1ª produção (30.5) |
| Segurança de aplicação | ENG-044, ENG-045, ENG-047 (Gitleaks e Trivy configurados, ainda não executados [verificado no STATUS]) | HML fica exposta na internet | Obrigatório: TLS, segredos fora do código e varreduras. Adiável: modelo de ameaças (ENG-041, "antes do piloto"), ZAP e intrusão (ENG-048, antes da produção) |
| Shell web e tokens do design system, sem menus vazios | Comando-mestre F0; cap. 74 (em revisão); AGENTS §4 | A tela da F1 nasce no padrão | Obrigatório: menu só com Estoque e Cadastros |
| Desempenho e carga | 29.3; 29.4; PERF-05 (v3.10) | Metas do item 1.5 | Medir na e2e: obrigatório. Ensaio de carga no envelope P1: adiável |
| Offline (Dexie/Workbox) | 23.1; NFR-08 | Não se aplica | Adiável (F5) |

## 3. Pronto para homologação da F1 (AGENTS §3.1/§3.2; comando-mestre, "Critério de pronto")
1. A tarefa do item 1.6 funciona do começo ao fim, com banco real, e não há S1 nem S2 conhecido (ENG-003).
2. Testes executados, com comando e saída registrados:
   - unidade e propriedade: saldo, união das restrições, decimal e conversão;
   - integração com PostgreSQL real: idempotência, mesma chave em paralelo, isolamento com a credencial da aplicação e permissões;
   - e2e no navegador: caminho normal, erro, permissão negada, repetição e documento duplicado;
   - migração do zero, acessibilidade, segredos e vulnerabilidades.
   Todo defeito corrigido ganha teste de regressão; nenhum teste instável fica escondido.
3. CI verde no commit candidato. Revisão do Codex registrada em `docs/parceria/rodadas/`, com autor, versão, data e parecer, e fluxos reproduzidos por ele.
4. Candidata em HML identificada por commit e digest; dados fictícios; e-mail, cobrança e integrações desligados ou em sandbox; faixa "Homologação" permanente (27.4).
5. Cliques e digitação da tarefa medidos na e2e (AGENTS §3.3), com as cinco referências do módulo Estoque registradas.
6. Mensagem ao Adrianus: link, versão, o que está pronto, a tarefa do item 1.6 e as limitações (o item 1.7). Nada de tela vazia nem pergunta de programação. `docs/STATUS.md` atualizado (AGENTS §6).
7. **Bloqueios externos [verificado]:** a CI remota depende da liberação da conta pelo titular. A hospedagem da HML exige autorização concreta de custo do proprietário (AGENTS §2; comando-mestre, passo 4). Enquanto os dois bloqueios existirem, a F1 só pode ser demonstrada em DEV, e isso não deve ser chamado de homologação.
