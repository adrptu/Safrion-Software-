# Produto, projeto e qualidade — Codex, Claude e Gemini

## Responsabilidades

- **Usuário e especialistas/usuários de campo:** definem objetivos do negócio, validam a realidade da operação e as regras de domínio; o usuário decide mudanças materiais de escopo, custo ou estratégia.
- **Codex:** lidera produto, prioridades, UX e QA; também implementa tarefas delimitadas de código, testes e correções. Revisa as entregas do Claude e recebe revisão dele sobre as próprias.
- **Claude Code:** lidera arquitetura, dados, contratos e integração; também implementa tarefas delimitadas. Revisa as entregas do Codex e recebe revisão dele sobre as próprias. Liderança não significa concentrar toda a execução.

Versão 4.2 · 29/09/2026. Autor: Codex. Esta migração preserva as regras vigentes de contribuição tripla, autoria delimitada e aceite por evidência. A fonte de trabalho anterior era local; após integração deste PR, este arquivo na `main` passa a ser a fonte canônica e a entrada local passa a apontar para ele. Até a integração, esta versão é candidata, sem presumir revisão ou aceite.

Histórico, revisores, versão aceita e limites de cada parecer ficam nas [rodadas](rodadas/) e nos PRs correspondentes. O [checkpoint da issue #1](https://github.com/adrptu/Safrion-Software-/issues/1#issuecomment-5858061746) contém a versão ativa, os impedimentos e o próximo passo. Não depender de histórico de chat ou caminhos pessoais para descobrir a regra vigente.

O usuário delegou a ambos as decisões técnicas em 27/09/2026 e pediu avanço rápido com qualidade, segurança e baixo custo. Decisões de implementação local seguem sem nova confirmação técnica. O acordo não inventa orçamento, credenciais, dados reais ou autorização para contratar. Acordo entre agentes precisa de justificativa e evidência, não apenas consenso.

Autorização posterior de Adrianus, 28/09/2026: instalar/configurar os plugins que Codex, Claude real e Gemini real considerarem necessários para o projeto, sem repetir a pergunta sobre essa intenção. Justificar a necessidade no registro existente, reutilizar capacidades disponíveis e verificar origem, permissões mínimas, custo e resultado antes de declarar adoção concluída. A autorização não define gasto ilimitado nem dispensa confirmações obrigatórias do provedor para contratação, termos ou ampliação sensível de acesso. Instalação em uma IA não comprova instalação nas outras; compartilhar artefatos e evidências quando o plugin for específico de uma plataforma. Serviços de infraestrutura, como Cloud Monitoring/Logging, seguem a entrega e os acessos da infraestrutura, sem criar plugin ou credencial duplicada.

Instrução posterior de 27/09: Codex e Claude também conduzem a homologação técnica e funcional; Adrianus recebe a versão verificada e dá feedback depois. Os critérios de entrega deste protocolo e as matérias reservadas ao proprietário no [AGENTS.md](../../AGENTS.md) mantêm essa separação; procedimentos de ambiente ficam em [Operação](../OPERACAO.md).

Os papéis são complementares. A avaliação de uma entrega considera a versão exata revisada e os testes efetivamente executados. A concordância entre agentes não substitui evidência nem validação com usuários reais.

Acompanhamento das três IAs: registrar entregas relevantes no PR ou no checkpoint existente. Preservar o pedido do proprietário de publicar um resumo curto das entregas verificadas na conversa Gemini já autorizada, com versão, contribuição real de cada IA, evidência, pendência e próximo passo. Essa conversa é uma janela de acompanhamento, não outra fila ou fonte de regras. Sem acesso ou com rascunho do proprietário, registrar envio pendente e preservar o rascunho; não presumir sincronização entre API e conversa, leitura ou aprovação. Canais autorizados, limites e confirmação de envio/recebimento acompanham o recibo da rodada; o acesso a um chat específico não é pré-requisito para recuperar as regras.

**Lean e Wu wei orientam a execução.** Lean: partir do valor para o agricultor, reduzir desperdício, manter fluxo, puxar trabalho pela necessidade e aprender com cada entrega ([referência](https://www.lean.org/lexicon-terms/lean-thinking-and-practice/), consultada em 27/09/2026). Wu wei é aplicado aqui no sentido solicitado pelo proprietário: preparar condições para agir com fluidez, preservar contexto e remover esforço evitável. A prioridade é concluir uma tarefa útil com qualidade, sem metas de ocupação ou volume de código. As regras abaixo concretizam essa direção; não criar outra metodologia paralela.

## Primeiro diagnóstico

1. Partir do PRD, do protótipo e das decisões vigentes. Identificar repositório, instruções locais, branch/commit, ambiente de teste, público e principal tarefa do usuário quando disponíveis.
2. Mapear funcionalidades existentes e fluxos críticos, aproveitando os padrões do projeto.
3. Executar as verificações disponíveis e registrar falhas anteriores às mudanças.
4. Avaliar o fluxo principal na interface e no código, incluindo erros e casos limites.
5. Produzir um backlog priorizado, separando defeitos comprovados, riscos a investigar e oportunidades de produto.

Antes de propor módulo novo fora do PRD, pesquisar cinco referências relevantes para o público e o domínio, com fontes e data. Não repetir pesquisa já incorporada à especificação. O benchmark informa prioridades; funcionalidades entram quando resolvem uma necessidade concreta.

O PRD é a fonte única. Claude redige a matriz de cobertura (definido / falta decidir / falta implementar / falta verificar); Codex a transforma em backlog, QA e critérios de pronto. Referenciar RN, CMD, CAL, AC, DS e as decisões aplicáveis, sem criar especificações concorrentes.

## Ciclo por entrega

**Definir resultado e responsável → autor implementa e testa → outro revisa → autor corrige → revisor verifica → integrar conforme as regras do projeto.** Codex e Claude alternam autoria e revisão conforme a tarefa.

### Contribuição e validação tripla

Pedido posterior do proprietário: GPT, Claude real e Gemini real contribuem e validam cada etapa substantiva da entrega, incluindo escopo/aceite, arquitetura, código/testes e candidata em homologação. Um autor por artefato permanece; o terceiro acrescenta contraexemplos, testes, código separado ou análise complementar. Não há edição simultânea nos mesmos arquivos nem três implementações concorrentes da mesma função.

Claude revisou este delta e o comando 2.4 na resposta à mensagem 92, com três ajustes incorporados: **substantiva** é uma mudança de comportamento/regra, cálculo, contrato/dado, segurança/permissão, arquitetura ou operação/liberação, incluindo testes que comprovam esses pontos; indisponibilidade do Gemini não interrompe trabalho independente, mas mantém o aceite triplo pendente; antes de cada envio externo, conferir conteúdo mínimo sem segredos/dados reais e registrar SHA-256 do payload para vincular o parecer. Hash não substitui inspeção de conteúdo nem autorização. Não criar serviço/ferramenta nova apenas para essa conferência.

- **Divisão concreta:** Claude lidera arquitetura e integração; Codex coordena fluxo, implementa e executa revisão/testes; Gemini pode escrever testes ou componentes delimitados, além de revisar. Autoria alterna conforme a tarefa e o acesso real. O conector de consulta Gemini gera texto/código; o piloto de executor restrito permite que o modelo solicite testes reais por ferramenta. Identificar separadamente autoria do teste, modelo solicitante, executor local e análise retornada. Estado comprovado e limites ficam no recibo do PR ou da rodada; não atribuir execução aos pareceres antigos apenas textuais.
- **Puxar trabalho sem espera evitável:** ao concluir um bloco, verificar a fila existente e assumir a próxima revisão ou dependência apta da mesma fatia. Se Claude estiver ocioso e houver tarefa pronta, enviar pedido concreto pelo canal autorizado, preservando rascunho, e verificar recebimento. Durante o turno, aproveitar eventos/resultados; evitar consultas repetidas sem mudança. Sem executor ativo, o acompanhamento agendado é a retomada disponível, não execução permanente.
- **Três pareceres sobre evidência:** registrar autor e versão, o que cada IA de fato analisou/executou, achados, decisão e próximo responsável no PR/rodada existente. Estados: em execução, em revisão, corrigir, bloqueado ou aceito no escopo. Parecer pendente nunca significa aprovação. Um agente revê o código de outro; correção material volta aos revisores afetados.
- **Fatos e execução pelas três IAs (reforço expresso de Adrianus, 28/09):** concordância sobre funcionamento só é aceita com teste ou reprodução real na candidata e ambiente identificados. Codex, Claude e Gemini devem acionar e analisar verificações complementares no sistema; apenas escrever um teste ou ler o resultado enviado por outro não conta como execução própria. Ferramenta local acionada pelo modelo pode executar o teste: registrar modelo solicitante, ferramenta/executor, hashes, comandos, resultado e limites. Hipótese/especificação sem execução permanece pendente; banco local não equivale a web/HML hospedada. Reutilizar evidência válida e evitar repetir a bateria inteira por agente, mantendo explícita a participação executada de cada um. O recibo do executor delimita os comandos autorizados e a evidência obtida. Uma execução não habilita automaticamente novos comandos nem comprova a web/HML.
- **Acordo técnico:** resolver divergências por requisito, reprodução, medição ou fonte. Sem S1/S2 conhecido, checks aplicáveis aprovados e os três pareceres pertinentes registrados para liberar a candidata da etapa; dúvida material impede só a parte dependente. Concordância por votação, quantidade de tokens ou três respostas semelhantes não comprovam correção.
- **Produtividade:** manter uma fatia ativa e uma tarefa de autoria por agente. Reutilizar evidência da mesma versão e dos trechos inalterados. Comandos auxiliares, mensagens e formatação sem efeito material ficam cobertos pelo parecer da entrega; não geram três consultas adicionais. Cada nova consulta Gemini deve produzir código, contraexemplo ou decisão útil, dentro do acesso e gasto autorizados.
- **Tempo do agricultor:** a equipe executa testes e homologação técnica/funcional. Adrianus recebe a versão verificada e decide o aceite de produção; sua experiência pode revelar necessidades que testes não antecipam. Não prometer ausência absoluta de defeitos nem impedir feedback por declarar perfeição.

A autoria da fatia atual é definida no checkpoint. Adrianus autorizou expressamente o envio à API Vertex AI do projeto dos trechos privados necessários de código/arquitetura/contratos para esta revisão e próximas revisões da equipe, excluindo senhas, tokens e dados reais de clientes. Estado operacional fica no PR/rodada e na issue #1, sem outro quadro paralelo.

- Codex prepara tarefas pequenas com problema, resultado esperado, escopo, dependências e critérios de aceite observáveis.
- Claude revisa as entregas substantivas do Codex antes de tratá-las como consolidadas: identifica omissões, incoerências, complexidade desnecessária e alternativas melhores, com justificativa.
- Codex incorpora os ajustes pertinentes e registra por que aceita ou rejeita cada recomendação. Alterações materiais voltam à revisão do Claude.
- O autor implementa e informa commit, arquivos, comandos de validação, resultados e limitações num PR pequeno; abre rascunho cedo quando já há algo concreto para revisar.
- O revisor lê o contexto do código, verifica os comportamentos e registra achados reproduzíveis. Revisões pendentes têm prioridade sobre iniciar outra tarefa independente; não é necessário interromper uma execução em curso.
- O autor corrige os achados e fornece evidência das diferenças.
- O revisor verifica o cenário original e a regressão afetada. Parecer anterior continua válido nas partes não alteradas; ninguém aprova ou integra o próprio PR.

Se houver trabalho simultâneo, usar branches e diretórios separados, com responsabilidade clara por tarefa. Correções de revisão permanecem focadas; refatorações maiores viram tarefas próprias.

### Padrão comum e melhoria contínua — 28/09/2026

Um método para as três IAs: **resultado/contrato → contribuição delimitada → implementação → prova → revisão independente → integração → aprendizado**. Usar os papéis e gates acima; uma fatia ativa e um autor por arquivo. A ordem é adaptada às dependências reais, sem três implementações concorrentes ou consultas por comando auxiliar.

- **Gemini desde o desenho quando houver ganho concreto:** assumir uma parte separável e testável (fixture com entrada/resultado esperado, teste, componente ou análise de contrato), com saída e arquivo definidos. O autor revisa e integra o código; o executor registra o que rodou. A revisão final usa a candidata e resultados reais. Não restringir Gemini ao papel de juiz final nem forçar contribuição de código em mudança pequena.
- **Um recibo no registro existente:** `versão/hash · arquivos · comando → resultado · limite · próximo responsável`. No limite, nomear o ambiente e escopo observado (fixture local, integração local, CI remota ou homologação); um não comprova o outro. Reutilizar prova válida; reabrir somente trecho/parecer afetado por mudança material, incluindo dependências transitivas: mudança de runtime exige verificação transversal, mesmo quando o diff é pequeno. Texto editorial e comandos auxiliares usam a evidência da entrega; uma mudança de regra não vira editorial só porque está em Markdown. Risco crítico fundamentado exige investigação mesmo sem reprodução completa; distinguir hipótese de defeito demonstrado.
- **Aprender em cada avanço, registrar só o que muda a prática:** ao fechar um bloco, verificar o que funcionou e o que causou falha, espera ou retrabalho. Se houver aprendizado útil, registrar uma linha no recibo com fato observado, ajuste, responsável e verificação do efeito. Erro relevante vira correção/regressão; acerto reutilizável entra no código, componente, teste ou trecho pertinente deste protocolo. Se nada mudou, não criar relato obrigatório. Medir tempo de conclusão, espera, repetição de teste e defeitos escapados quando os dados existirem; melhoria ou crescimento exponencial não são presumidos.
- **Alinhamento recíproco no trabalho real:** diante de atrito, cada IA aponta o fato, o ajuste que assume em si e a ajuda concreta que precisa das outras; confirmar recebimento e próximo responsável no mesmo registro. Trocar mensagens curtas com versão, evidência e decisão, mantendo o detalhe no artefato. Antecipar fixtures/contraexemplos do Gemini quando o contrato permitir; validar sua estrutura antes do repasse e entregar mudança com asserção, resultado e limite. Complementar as lentes especializadas com uma revisão geral da entrega para cobrir a integração entre partes. Não inventar hashes, horários, resultados ou métricas: extraí-los da evidência. Comparar rodadas até aceite e defeitos posteriores pelos registros existentes, sem limite artificial de rodadas que suprima achados. Experimento imediato: fixtures negativas Gemini antes do fechamento de rede/conector, executadas por Codex e incorporadas pelo autor Claude; depois avaliar se diminuiu a devolução por falha evitável.
- **Falha de ferramenta não é parecer:** marcar como não executado, preservar a tentativa e verificar contrato/precondições localmente antes de repetir chamada paga. Se faltar precondição remota, interromper a cadeia dependente e devolver causa segura, responsável e condição de retomada, sem simular resultado; seguir só no trabalho independente. Alterar a causa ou a abordagem; não repetir às cegas. Preferir corrigir a ferramenta existente a criar outra camada. Revisão independente permanece livre para discordar; incorporar prática por evidência e adequação ao contexto, não por maioria ou reputação do modelo.

### Começar certo: acordo curto antes da edição

Uma fila de trabalho vinculada ao PRD, com uma fatia funcional ativa. Cada agente assume no máximo uma tarefa de autoria por vez, em arquivos e branch separados. Duas tarefas da mesma fatia podem avançar em paralelo quando independentes ou quando compartilham um contrato já definido. Revisão tem prioridade para evitar fila de PRs. Se a tarefa não puder ser separada com clareza, trabalhar em sequência; não abrir enxames por padrão.

Puxar trabalho pela ordem: conter risco crítico → corrigir/revisar entrega pronta → resolver a dependência que impede o próximo resultado → iniciar o próximo item apto. Trabalho bloqueado continua visível na fila. Antes de abrir outra frente, identificar causa, responsável e condição de retomada; uma tarefa independente só entra conforme os limites acima. Ferramentas, documentos e consultas adicionais precisam remover um obstáculo concreto ou verificar um requisito.

Cada tarefa precisa apenas destes campos, no rastreador ou arquivo da rodada existente:

```text
ID / resultado útil / persona:
Requisitos do PRD e escopo excluído:
Autor / revisor / integrador:
Base (commit ou hashes) / arquivos sob responsabilidade:
Aceite e comando de verificação:
Estado / impedimento / próximo passo:
```

Antes de editar, confirmar a base, trabalho em curso, dependências e resultado esperado. Se o outro já implementou, revisar ou reaproveitar; não criar uma segunda solução. Decisão técnica reversível dentro do escopo é tomada pelos agentes. Dúvida de negócio material é isolada, com recomendação concreta para Adrianus, enquanto o trabalho independente continua.

Compartilhar apenas o contrato necessário à tarefa: entrada, saída, erros, permissões e um exemplo verificável, na fonte existente. Tipos/esquemas, regra de domínio e componentes já aprovados são reutilizados. Não antecipar arquitetura de módulos futuros. Simulação de API permite avançar na interface, mas não prova integração com banco ou serviço real.

### Trabalho individual: produzir uma entrega pequena e verificável

1. Ler os requisitos e os trechos relevantes, sem reler toda a documentação a cada ação. Preservar num checkpoint curto a versão, o que já foi verificado e o próximo passo; retomar daí. Agrupar leituras independentes e trabalhar em blocos de foco, com avisos de progresso e sem trocar de tarefa a cada mensagem de andamento.
2. Reproduzir defeito antes da correção quando viável. Separar problema do produto, expectativa desatualizada, teste frágil, compilado antigo e travamento de agente.
3. Fazer a menor mudança coerente. Reaproveitar componentes, regras, testes e benchmark existentes; abstrair somente quando houver necessidade real. Não antecipar módulos completos.
4. Executar testes relevantes e inspecionar o resultado real, não só o código de saída de um script que pode estar incorreto. Depois de corrigir o classificador, reaproveitar logs válidos; não repetir a bateria inteira sem mudança que justifique.
5. Fazer autorrevisão: diff, caminhos de erro, dados/permissões, compatibilidade, corte de UX e evidência. Entregar versão, diff, comandos, resultados e limites num único pacote curto.

### Trabalho conjunto: revisão que acrescenta valor

- O revisor procura contraexemplos e necessidades da persona; não reproduz toda a implementação nem aprova apenas por concordar. Verifica a base e os testes críticos; registra fatos separados de hipóteses e preferências.
- Cada achado é aceito, ajustado ou recusado com fundamento. Resolver primeiro riscos de dados, isolamento, cálculos e bloqueios do fluxo; polimento não reabre indefinidamente uma entrega aceita.
- Quem integra confere a versão e aplica o patch; quem propõe não sobrescreve o arquivo ativo do outro. Patch em cópia isolada e manifesto de hashes quando o protótipo ainda não está em Git. Nunca compartilhar sem coordenação perfil de navegador, porta de teste ou estado de demonstração.
- Fazer revisão independente do artefato integrado, não apenas do patch. Rodar a regressão afetada e registrar aceitação. Nova mudança material invalida o aceite do trecho afetado, não todo o trabalho já provado.
- Mensagem entre agentes contém pedido, caminho, versão, decisão necessária e impedimento. Contexto completo fica no artefato; atualizar o pedido existente quando só houver complemento. Comunicar mudança de estado, entrega ou bloqueio acionável; evitar mensagens repetidas, PRD colado e relato de cada comando. Confirmar recebimento/revisão pelos estados reais. Não confundir mensagem enviada com trabalho integrado.

### Destravar sem repetir o mesmo esforço

- Tarefa travada não equivale a bug. Preservar saídas parciais e retomar do último ponto verificável.
- Dois fracassos pelo mesmo motivo exigem mudar a hipótese, reduzir a tarefa ou corrigir a ferramenta antes de outra tentativa. Não autoriza abandonar a tarefa nem pedir ao usuário escolhas técnicas.
- Um bloqueio de publicação/CI não paralisa código local independente já autorizado. Preservar a evidência e continuar a tarefa delimitada; integração e homologação continuam exigindo os checks aplicáveis. Reexecutar somente o que uma correção ou nova evidência justificar.
- Usar o PR como canal da mudança: pedido publicado, recebido, em revisão e revisado são estados diferentes. Sem resposta, consultar outro canal autorizado quando houver acesso, registrar a pendência e executar trabalho independente. Não enviar lembretes idênticos nem presumir concordância. Revisão recebida encerra a espera; prazo decorrido não substitui parecer.
- Comandos demorados têm limite explícito, progresso visível e logs incrementais; comandos do protótipo respeitam os blocos curtos da sua spec. Processos longos necessários rodam com acompanhamento, sem ocupar o chat em espera muda. Encerrar somente processos de teste sob responsabilidade do autor.
- Após falha, registrar causa, o que foi preservado e a próxima verificação. Cada aprendizado relevante vira correção na ferramenta, teste de regressão ou instrução curta; não apenas mais uma rodada de explicações.

### Terminar certo e melhorar o método

Concluir somente com aceite do escopo, revisão recebida, evidência da versão, pendências classificadas e próximo passo. Para publicação, preservar a homologação técnica pela equipe e o aceite explícito do proprietário para a candidata de produção, conforme este protocolo e o AGENTS.md. Contador de tarefas, número de agentes e quantidade de testes não provam qualidade.

Ao fechar a fatia, escolher o principal desperdício observado e experimentar uma mudança pequena; comparar o resultado antes de mantê-la. Usar evidências existentes de tempo até entrega útil, espera por revisão/integração, defeitos após revisão, retrabalho e esforço humano de homologação. Não criar painel, cerimônia ou coleta extra apenas para medir a equipe. Sem metas numéricas inventadas antes da linha de base. Se não houver uma melhoria demonstrável, não criar uma regra nova.

### Corte de supérfluo em todos os artefatos

Pedido expresso do proprietário: simplificar PRD, código, fluxograma e comunicação sem perder a essência. Cada trecho deve ajudar a entender a tarefa, decidir, implementar, verificar ou operar. O que não cumpre função é removido; regra repetida vira referência à fonte única.

- **PRD:** manter resultado, regra, estados/exceções, permissões e aceite observável; eliminar prosa repetida e especificações concorrentes. Preservar IDs e rastreabilidade ao consolidar; não apagar requisito material para diminuir páginas.
- **Código:** menor solução legível que cumpre o contrato; reutilizar componentes e serviços de domínio. Sem configurações, dependências, camadas ou abstrações para necessidades imaginadas. Clareza e comportamento correto valem mais que menos linhas.
- **Fluxograma:** um fluxo útil por jornada, com decisões e exceções que mudam o caminho. Não espelhar cada botão nem desenhar variantes idênticas; referenciar subprocessos realmente reutilizados.
- **Testes:** cobrir comportamentos e riscos; remover redundância comprovada, nunca ocultar falhas nem trocar teste de regra por contagem de cobertura.
- **Documentos e mensagens:** registrar decisão na fonte canônica e comunicar a alteração com caminho, versão e próximo passo. Não criar relatório quando uma atualização curta na rodada existente basta.
- **Corte com evidência:** autor propõe, revisor verifica preservação de escopo, significado e referências; executar checks afetados. Mudança funcional segue homologação. Cada entrega diz brevemente o que ficou, o que foi adiado e o que foi cortado, com motivo.

### Regra permanente de revisão recíproca

A revisão do Claude sobre o trabalho do Codex foi expressamente solicitada pelo usuário, assim como a revisão do Codex sobre o trabalho do Claude. O pedido autoriza a comunicação necessária entre os dois para esta parceria.

- Cada entrega substantiva tem autor, revisor, versão e evidências. Revisão ainda não recebida fica como pendente.
- Os dois podem discordar: decidir por requisitos, evidência, testes e experiência de campo. Questões que mudem materialmente o negócio voltam ao usuário.
- Incorporar aprendizados às instruções compartilhadas e aos testes, com referência ao achado que motivou a mudança.
- Encerrar a rodada quando os critérios de aceite forem verificados e não houver bloqueadores abertos. Refinamentos opcionais entram no backlog.
- A falta de conexão com o outro agente não equivale a aprovação: preparar o pedido e informar o estado real.

## Definições necessárias além do PRD e design system

Verificar primeiro o que o PRD final já cobre. Referenciar a fonte existente e complementar lacunas, evitando documentos contraditórios.

1. **Escopo da versão e resultado esperado:** público, fluxos completos incluídos, itens fora, prioridades, dependências e medidas de sucesso.
2. **Regras de negócio:** entidades, estados, transições, unidades, fórmulas, fontes, exceções, cancelamentos e correções auditáveis.
3. **Dados:** relações, restrições, histórico, isolamento, importação, conciliação, migração e retenção.
4. **Jornadas e permissões:** quem pode fazer cada ação, em que estado e contexto; protótipos navegáveis com vazio, erro e recuperação.
5. **Arquitetura:** limites dos módulos, responsabilidades, contratos de API/eventos, decisões e dependências justificadas.
6. **Integrações e campo:** fontes e destinos, sincronização, repetição de operações, conflitos, indisponibilidade e rastreabilidade.
7. **Requisitos mensuráveis:** volumes, dispositivos, navegadores, desempenho, acessibilidade, segurança, disponibilidade e limites de custo.
8. **Plano de qualidade:** vínculo requisito → tarefa → teste → evidência, dados de teste realistas e critérios de aceite por fluxo e versão.
9. **Entrega e operação:** ambientes, pipeline, segredos, migrações, implantação, monitoramento, alertas, backup, restauração e retorno à versão anterior testados.
10. **Entrada em uso:** cadastros e importação iniciais, piloto acompanhado, suporte, responsáveis e rotina de evolução.

“Completo” significa que todos os fluxos do escopo acordado cumprem os critérios de aceite na versão e condições testadas. A avaliação declara seus limites; não promete ausência absoluta de defeitos.

## O que será avaliado

### Produto e gestão do projeto

- Problema concreto, público, benefício e frequência de uso.
- Prioridade por impacto no usuário, risco, alcance, esforço e dependências.
- Escopo de cada entrega, bloqueios, responsável e próximo passo explícitos.
- Hipóteses e decisões registradas; estimativas com incerteza declarada.
- Métricas escolhidas conforme o fluxo: taxa de conclusão, tempo da tarefa, erros, retrabalho e adoção. Levantar a situação inicial antes de estabelecer metas.

### Qualidade funcional e domínio agro

- Fluxos completos, persistência, validações, estados inválidos, concorrência e operações repetidas.
- Conforme os módulos existentes: safras, talhões, lotes, estoque, custos, produção, máquinas e animais.
- Unidades e conversões explícitas, cálculos e arredondamentos testados, origem dos indicadores e rastreabilidade até os registros.
- Relacionamentos e totais consistentes entre operação, estoque e custos, quando aplicável.
- Em uso no campo: perda de conexão, recuperação, sincronização, duplicação e conflitos de edição.
- Regras técnicas, fiscais ou legais verificadas em fontes pertinentes e atuais quando entrarem no escopo; dúvidas de domínio ficam identificadas para validação.

### UX

Autorização expressa de Adrianus em 28/09/2026: Codex, Claude e Gemini podem também melhorar o design system. Manter uma fonte única no PRD, autoria delimitada e componentes reutilizáveis; demonstrar mudanças em telas reais e validar clareza, beleza, acessibilidade, fluidez e prevenção de erro. A revisão tripla e os testes da etapa continuam necessários; a autorização não significa que todas as telas já foram validadas.

- Menu → Listagem → Detalhe → Sub-detalhe para entidades de gestão.
- Estado visível, próximo passo com verbo, uma ação primária e contexto preservado.
- Formulários essenciais, linguagem do usuário e proteção contra perda de dados.
- Estados vazio, carregando, erro e sucesso; teclado, foco, contraste e uso no celular.
- Tabelas seguem o contrato versionado do [PRD §4.3](../PRD.md#43-padrões-visuais-e-de-interação), incluindo filtros, ordenação, agrupamento e retorno com contexto. A skill tabelas-interativas auxilia a execução quando disponível; as regras necessárias são recuperáveis no repositório.
- Revisão de minimalismo com três listas: aplicado, deixado de fora e cortado, sempre com motivo.

Login, onboarding, landing pages, fluxos lineares e configurações simples seguem UX essencial, com uma frase explicando a exceção ao master-detail.

#### Aceite de design, UX e UI antes do agricultor

Reforço solicitado por Adrianus em 29/09/2026. Revisado por Claude real em 29/09, 11:54 UTC e por Gemini real Pro/HIGH (resposta tqa7apDYGdOWn_APhJySyAc, extrato documental; sem teste de software). Resoluções e limites no registro da rodada; não equivale à homologação de telas. O resultado esperado é concluir a tarefa agrícola com clareza, pouco esforço e recuperação segura. Beleza significa hierarquia, tipografia, espaçamento, alinhamento, densidade, legibilidade e estados coerentes com o design system; não quantidade de efeitos ou opinião sem tela observada.

1. **Projetar a jornada antes da tela.** Identificar persona, tarefa, entidade/nível, estados, próximo comando e informação já disponível. Codex propõe o fluxo mínimo e Claude verifica contratos, dados e componentes existentes; Gemini acrescenta contraexemplo ou simplificação concreta. Resolver dúvida material antes do trecho dependente. Usar protótipo apenas para a incerteza que ele resolve; reaproveitar padrões aprovados.
2. **Implementar um fluxo completo.** Um autor por componente. Usar tokens e componentes do design system, com estados vazio, processamento, pendência, sucesso real, erro e recuperação pertinentes. Revisão do design system demonstra o efeito em uma tela real e nas variantes afetadas; não duplicar componentes para uma exceção local.
3. **Ver e operar a candidata.** Antes de chamar Adrianus, a equipe percorre a jornada principal, retorno/correção e falha/recuperação nos dispositivos e papéis afetados. Conferir teclado/foco, toque/teclado virtual, zoom, contraste, conteúdo longo, preservação de contexto/rascunho e conexão intermitente quando aplicável. No app de campo, incluir legibilidade ao sol, alvos compatíveis com luva/mão suja e uso com uma mão; simulação em desktop não comprova condições físicas de campo. Quando houver operação offline, comprovar persistência local segura, reconciliação de conflitos e reenvio sem perda/sobrescrita silenciosa ou efeito duplicado, conforme o contrato vigente. Capturas ou gravação curta identificam versão, viewport e estado; o parecer visual exige acesso à tela renderizada. Leitura de código, screenshot isolado ou CI verde não prova a jornada inteira. As três IAs acionam e analisam provas complementares conforme o protocolo, sem repetir toda a bateria. Falta de acesso visual/teste permanece explícita, não vira aprovação. Automação de acessibilidade não comprova sozinha conformidade integral.
4. **Cortar esforço com evidência.** Para cada campo, clique, etapa e componente relevante, nomear a decisão, ação ou proteção que sustenta. Reutilizar contexto confiável e cálculos; remover repetição sem função, ou levar detalhe secundário para acesso sob demanda sem prejudicar sua descoberta. Comparar digitação, passos, tempo e erros no cenário verificado quando houver base; sem base, registrar a observação, não inventar ganho percentual. Preservar permissão, unidade, confirmação necessária, estado e recuperação. Cada trava/confirmação nomeia o dano concreto que evita; sem fundamento, simplificar para aviso/registro ou remover conforme o critério do proprietário. Medir primeiro nos testes e na observação; este aceite não exige novo rastreamento de usuários. Se telemetria for necessária depois, minimizar dados, rede, bateria e processamento. Entregar aplicado/deixado de fora/cortado no recibo existente, sem relatório separado.
5. **Corrigir antes de apresentar.** O autor aplica os achados e o revisor verifica o comportamento afetado. Não apresentar como pronta uma jornada com defeito conhecido que impeça sua conclusão, cause perda de trabalho, sucesso falso, erro de interpretação material ou barreira de acessibilidade, além dos bloqueadores já definidos. Preferência cosmética sem impacto comprovado não abre ciclos infinitos. Adrianus recebe link testado, versão, cenário útil preparado e limites relevantes; seu feedback valida a realidade agrícola e a percepção de uso. Reteste humano se limita ao que depende disso, sem transferir a bateria técnica ao proprietário.

O recibo da entrega acrescenta somente: **jornada/persona · versão/ambiente · prova visual e funcional · contribuição/parecer de cada IA · cortes e limites**. Medir conclusão, esforço e erros observados; não declarar excelência, zero retrabalho ou mínimo absoluto de tempo com base apenas em consenso. A melhoria deve aparecer no uso e permanecer protegida pelas regressões pertinentes.

### Código e operação

- Correção das regras, validação de entrada, autorização e isolamento de dados.
- Tratamento de falhas, transações, idempotência e compatibilidade com dados existentes.
- Duplicação, código morto, clareza, consultas, paginação e desempenho medido.
- Testes de comportamento e regressão proporcionais ao risco.
- Lint, tipos, testes e build conforme os comandos do projeto; falhas e verificações indisponíveis ficam explícitas.
- Migrações, observabilidade, recuperação e implantação quando a entrega envolver essas áreas.

## Formato de cada achado para o Claude

```text
ID e título:
Tipo: defeito comprovado | risco a investigar | melhoria de produto
Prioridade: P0 | P1 | P2 | P3
Severidade do defeito: S1 | S2 | S3 | S4, conforme PRD 22.1
Versão e ambiente:
Local: arquivo:linha, rota ou fluxo
Cenário e passos para reproduzir:
Resultado observado e evidência:
Resultado esperado e impacto para o usuário:
Correção ou investigação sugerida:
Critério de aceite e teste de regressão:
Dependências e estado:
```

- **S1:** perda/corrupção de dados, acesso indevido relevante, comando físico perigoso ou indisponibilidade crítica.
- **S2:** cálculo material incorreto, movimento/obrigação duplicado, fluxo essencial bloqueado ou desempenho que inviabiliza a tarefa.
- **S3:** problema limitado com alternativa segura.
- **S4:** cosmético ou melhoria.

P0–P3 expressam ordem de trabalho, considerando impacto, alcance, risco, esforço e dependências. Não substituem a severidade. Nenhuma liberação com S1 ou S2 conhecido no escopo.

Prioridade não substitui evidência. Uma hipótese permanece hipótese até ser verificada. Preferências estéticas não recebem a mesma prioridade de falhas de negócio.

## Encerramento e comunicação

Cada rodada entrega:

1. Parecer: **aprovado no escopo verificado**, **reprovado** ou **pendente de verificação**.
2. Achados priorizados e tarefas com autoria atribuída a Codex ou Claude.
3. Evidências dos testes e limitações da avaliação.
4. Estado das correções anteriores e próximo passo.

Não encerrar uma correção apenas porque o código mudou. Verificar o comportamento e registrar a versão testada. Não afirmar cobertura completa quando faltarem acesso, dados ou execução.

## Continuidade sem dependência de um computador

Diretriz expressa do proprietário em 29/09/2026: o projeto não deve depender deste Mac. Editor, terminal e chats locais são meios de acesso; não podem ser a única cópia das regras, das mudanças necessárias nem do estado operacional.

- Código, contratos, decisões e instruções necessários para retomar ficam versionados neste repositório. Trabalho em andamento recuperável usa branch/PR identificados; um commit apenas local não comprova preservação remota. Regras têm fonte única e links relativos quando internos ao repositório.
- Checkpoint, responsável, versão e evidências necessárias à revisão ficam acessíveis à equipe autorizada pelo GitHub. Recibos citam artefatos com acesso e retenção conhecidos; um caminho local sozinho não basta. Não copiar pastas de trabalho inteiras, credenciais, dados reais ou conversas privadas para cumprir esse requisito.
- Credenciais são fornecidas no ambiente autorizado, com privilégios mínimos e preferência por identidade federada; não copiar sessão desktop, tokens pessoais ou chaves do Mac. Transferência de dados e custos novos respeitam as autorizações concretas do proprietário.
- Comprovar separadamente: **recuperação por clone limpo**, **CI remota**, **execução remota das três IAs** e **aplicação/banco com backup e restauração**. Uma prova não substitui a outra. O acesso remoto a processo que continua rodando neste Mac também não comprova independência.
- A prova registra ambiente remoto, commit, comando/jornada, resultado, limites, responsável e artefatos recuperados. A alegação de independência exige executar a jornada pertinente sem ler arquivos, serviços ou sessões deste Mac; ambiente configurado ou CI verde sozinho não basta.
- Acompanhamento depende de um executor realmente ativo e recuperável. Não prometer plantão 24 horas, continuidade automática ou ausência absoluta de falhas por existir uma automação agendada.

Este documento define o modo de trabalho, não certifica o produto ou a operação remota. Consultar [STATUS](../STATUS.md), [Operação](../OPERACAO.md), PRs/CI e o checkpoint para o estado comprovado; não manter aqui uma cópia de status que envelhece.
