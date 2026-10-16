# Decisões

Índice das decisões do produto e da engenharia. **A regra completa está sempre no PRD** (`docs/PRD.md`); este arquivo só aponta para ela, para evitar texto duplicado e divergente. Exceção: a seção "Decisões delegadas de 09/10/2026" traz o texto das decisões, porque o PRD fica inalterado até a comparação final (DEC-0910-06).

## Decisões do proprietário (vigentes)

Registradas no capítulo 72 do PRD v3.9 (26/09/2026).

| ID | Tema | Onde ler |
|---|---|---|
| DEC-2609-01 | Parcelas sem limite | PRD 72.2 |
| DEC-2609-02 | Operação antes da atividade | PRD 72.2 |
| DEC-2609-03 | Rendimento por largura, velocidade e eficiência | PRD 72.2 |
| DEC-2609-04 | Tela de trabalho da O.S. | PRD 72.2 |
| DEC-2609-05 | Revisão separada da liberação | PRD 72.2 |
| DEC-2609-06 | Barras do mapa | PRD 72.2 |
| DEC-2609-07 | Retirada integrada e fichas de execução | PRD 72.2 |
| DEC-2609-08 | Painéis e tabelas sem corte | PRD 72.2 |
| DEC-2609-09 | Recursos da O.S. e alocação para o PCP | PRD 72.2 |
| DEC-2609-10 | Irrigação só com água sem aprovação do agrônomo | PRD 72.2 |
| DEC-2609-11 | Filtros de Fazenda e Safra no topo | PRD 72.2 |
| DEC-2609-12 | Nomes das funcionalidades do mapa | PRD 72.2 |
| DEC-2609-13 | Estoque e app de campo prontos para os primeiros testes com clientes | PRD 72.2 |
| DEC-2609-14 | Cadastros completos para a inteligência do sistema | PRD 72.2 |
| DEC-2709-01 | Início do software real (F0 e F1) só com dados fictícios; decisões técnicas delegadas a Claude e Codex juntos. Continuam com o proprietário: custo, conta e contrato, dados reais, ERP real, publicação a usuários reais e aceite da candidata antes da produção | `docs/parceria/rodadas/R-006-skills-ferramentas-plano.md` §7 |
| DEC-0510-01 | Protótipo em regime leve: branch única, sem PR por incremento, revisão sem bloqueio; rigor completo só no software real | `AGENTS.md` 3.5 |
| DEC-0510-02 | Unidade junto do valor, na célula ("62.500 kg", "160,00 ha"), sem coluna nem filtro de unidade; ordenação pelo número. Rótulos de custo: "Custo R$/h", "Custo R$/ha", "Custo R$/kg" | issue 1, comentário 5997108200 |
| DEC-0510-03 | Unidade de mercado configurada por cultura, distinguindo quantidade de produtividade: frutas e cana em t e t/ha; grãos/café em sc e sc/ha, com kg por saca explícito. O padrão sintético atual de 60 kg não altera o fator/massa de contratos históricos. Unidade e conversão têm fonte única; somas só após compatibilização dimensional. Demais culturas mantêm unidade e fonte cadastradas | Preferência: chat do proprietário de 05/10; qualificação dimensional: retorno Codex ALINHAMENTOS-20261008 na issue 1 |
| DEC-0510-04 | PCM integrado a suprimentos; Beneficiamento acessível em Produção; Planejar safra com todos os talhões na etapa 2 e etapas 3-4-5 reunidas; Suprimentos simplificado | issue 1, comentário 6001191813; contratos existentes desses módulos no protótipo |
| DEC-0510-05 | Executar a recomendação da auditoria CONTROLE-01, preservando os requisitos e os controles de integridade | issue 1, comentário 6001191813; plano corrente CTL-1 a CTL-5 no PR 47 |

## Decisões pendentes do proprietário

Até a decisão, vale o comportamento conservador descrito no próprio PRD. Quando a linha aponta para uma DEC-0910-xx, a pendência foi decidida pelos agentes sob a delegação de 09/10 (DEC-0910-03), **não é aprovação do proprietário** e continua aqui e no PRD até a comparação final (DEC-0910-06).

| ID | Tema | Onde ler |
|---|---|---|
| DEC-01 | Hectare ativo × área física produtiva contratada | PRD 70.4 |
| DEC-02 | Entrada por papel × mapa | PRD 70.4 |
| DEC-03 | Meta de previsão | PRD 70.4 |
| DEC-04 | Gates técnicos. Decidida pelos agentes: DEC-0910-38 (b) | PRD 70.4 |
| DEC-05 | Preços e trial dos parceiros | PRD 70.4 |
| DEC-06 | Distribuição de oportunidades | PRD 70.4 |
| DEC-07 | Tolerâncias e exposição de compras. Tolerâncias decididas pelos agentes: DEC-0910-25 (a); a exposição de compras continua pendente | PRD 70.4 |
| DEC-08 | Gessagem e subsuperfície | PRD 70.4 |
| DEC-09 | Trial do agricultor e franquias | PRD 70.4 |
| PEND-01.. | Pendências da revisão v3.10 (confiabilidade transacional, offline e desempenho), entre elas a proposta de pré-autorização por limiares, **não aprovada**. Decididas pelos agentes: PEND-06 e PEND-09 (DEC-0910-16 c, e), PEND-10 (DEC-0910-17) e PEND-13 (DEC-0910-13 b); fora de 73.12, a proposta PEND-17 (DEC-0910-18) | PRD 73.12; `docs/prd/v3_10-reconciliacao.md` |
| PEND-REPO-01 | Em 27/09 o proprietário informou "Fiz upgrade no git", e a CI remota voltou a rodar. Plano exato ainda não conferido; se permitir, aplicar a proteção da `main` (`tools/github/configurar_protecao.sh`). Texto anterior: **só se o plano da conta for Free** (ainda não verificado): proteção da `main` imposta pelo servidor em repositório privado exige GitHub Pro (custo mensal da conta). Opções: contratar o Pro; ou manter privado sem proteção imposta, com a disciplina de pull request, CI e parecer escrito. Tornar público só por decisão expressa. **Até decidir:** privado, sem proteção imposta, disciplina de processo. | `docs/STATUS.md`, bloqueio 2 |
| PEND-DS-01.. | Pendências do design system (modo escuro, marca, fontes de títulos e outras). Decididas pelos agentes: PEND-DS-02, 03, 06, 09, 10, 13 e 15 e, só quanto ao nome exibido, PEND-DS-04 (DEC-0910-39); marca, logotipo e INPI continuam com o proprietário | PRD 74.12 (em revisão) |
| PEND-OS-01 | O.S. sem etapa de revisão (pedido de 01/10) × DEC-2609-05. **Padrão adotado:** "Liberar para execução" é o "Aprovar e liberar" do PRD 41.3, gravando aprovado por (CMD-42) e liberado por (CMD-06) em separado. Decidida pelos agentes: DEC-0910-15 | issue 1, comentário 6001191813 |
| PEND-CTL-02 | Quem aprova ajuste de estoque e consumo acima da custódia. **Padrão adotado:** o gestor; se ele mesmo registrou a contagem, fica revisão posterior (PRD 2.1) | idem |
| PEND-CTL-03 | Entrada transversal de Controle (previsto × realizado). **Padrão adotado:** vem depois do CONTROLE-01 | idem |

## Alinhamentos técnicos de 08/10/2026

Retorno **ALINHAMENTOS-20261008**, na issue 1, aos comentários 6001191813 e 6003279115. Decisões técnicas do Codex dentro da delegação, sem atribuir ao proprietário aceite final dos padrões PEND. A implementação continua na autoria existente do Claude; parecer sobre os ajustes e aceite do software real permanecem separados.

| Referência existente | Alinhamento | Fonte de detalhe |
|---|---|---|
| CMD-06 / CTL-7-ATOR / PEND-OS-01 | Gestor libera na demonstração; agrônomo aprova no CMD-42; ator, permissão e recibo verdadeiros. Ação integrada quando há ambas as permissões. CTL-7 já absorvido no CTL-3. Pessoas distintas exigem o fluxo de aprovação e liberação separáveis antes de uso real; não reabrir tarefa já incorporada | CONTROLE-01 e retorno Codex na issue 1 |
| B-R8 / antigo CTL-11 | Severidade S2. Aceitar o fato do turno, sinalizar divergência de consumo/dose e manter revisão técnica pendente, sem ajustar o realizado para parecer conforme. A reprodução focal não demonstrou encerramento integral da O.S. | Retorno Codex: núcleo f4121bd, 08/10 às 15:54:46 UTC |
| Item 12 / PCM | Estoque paralelo tem severidade S2; priorizar 1a/1b respeitando as dependências de SUP e PCM simplificado. Horímetro/Gerar O.S. já constam do desenho vigente; não abrir segunda frente | Especificações existentes de PCM simplificado §7.2 e Suprimentos §9 |
| PEND-CTL-02 | Se quem decide também registrou a contagem, distinguir decisão do gestor registrada de revisão independente ainda pendente. Conciliar essa exceção explícita com o texto geral SUP, sem fingir revisão independente | Retorno Codex na issue 1 |
| SAF / ocupação | Ciclo mínimo é estimativa; período/safra encerrado não comprova desocupação física. Conservar fato, custo e ocorrências fora da janela no veredito pertinente. Perenes podem continuar ocupando após passes | Especificações SAF vigentes; retorno Codex na issue 1 |
| BEN / COLH / unidades | BEN reutiliza c.producao, CULTURA_UN/prUn e a O.S. de colheita. Fator histórico de contrato não muda com a preferência atual da cultura; massa já gravada em kg não é convertida de novo | Decisões COLH D-01/02/03/05 e retorno Codex na issue 1 |
| E3 / rede de pivôs | Premissa de rede compartilhada explicitamente sintética; conferir vínculo e capacidade por ponto antes de dados reais | CONTROLE-01 e retorno Codex na issue 1 |

**Ordem sem colisão de nomes:** S1/S2/S3/S4 em PCM simplificado §7.2 são IDs de etapas do **PCM**, não severidades nem etapas SUP. SUP-1 → SUP-2a → SUP-2b precedem PCM-1a/1b; PCM mantém S1 → S2 → 1a → S3 → 1b → 1c → S4. SUP-3 (tela) depende de SAF-única e PCM-1c-dados. Concluir frentes em curso e respeitar arquivos compartilhados; não reiniciar trabalho já incorporado.

### Pedidos do proprietário lidos na retomada de 08/10

| Tema | Registro e encaminhamento na mesma autoria | Estado |
|---|---|---|
| Separadores visuais | Padronizar no design system as linhas abaixo do título/ação superior e entre blocos pertinentes, conforme exemplo Nova safra, reutilizando o componente comum | Pedido lido no chat Claude; implementação não comprovada nesta retomada |
| Irrigação / ficha do pivô / solo | Ficha no detalhe do ativo de irrigação, acessível pelo fluxo Irrigação; teste de solo ligado ao talhão/zona com data, profundidade, método, unidade e fonte. Preservar a referência “lâmina 21 h” com o regime da ficha, sem presumir definição ou prescrição. Reutilizar frentes Irrigação/Solo existentes | Pedido lido no chat Claude; definição técnica e implementação seguem com o autor |

Os cortes técnicos da SAF-única (largura/velocidade só no formulário; custo por mês fora da etapa Planejar safra, preservado no orçamento — PRD 44.5/44.6) ficam ratificados, preservando rendimento e custos pertinentes. PCP, D7/VEN, contratos pendentes, C2 e Fase 1 comercial continuam no conjunto. Uma publicação parcial não encerra melhorias nem aciona auditoria integral. Os novos alinhamentos não autorizam produção ou gastos adicionais.

## Decisões de arquitetura (ADR)

Ficam em `docs/adr/`, uma por arquivo, no modelo `0000-modelo.md`. As escolhas já fixadas pelo PRD (caps. 12, 23 e 28) estão resumidas em `0001`. Mudar uma delas exige ADR nova que demonstre o mesmo requisito (PRD 12.1).

| ADR | Título | Situação |
|---|---|---|
| 0001 | Arquitetura e stack de referência adotadas pelo PRD | Aceita (origem: PRD 12.1, 23.1, 28) |
| 0002 | Repositório privado com documentação e CI antes do código de produto | Aceita (proprietário, 27/09/2026) |
| 0005 | Hospedar a HML em southamerica-east1 (São Paulo) | Proposta (revisão do Codex pendente) |
| 0006 | Ligar o banco da HML só por rede privada (PSA, Direct VPC e conector `PRIVATE`) | Proposta (revisão do Codex pendente) |

## Decisões de design do proprietário

| ID | Decisão | Fonte |
|---|---|---|
| DEC-0910-01 | Padronizar o design system para tudo o que existe e o que vier: botões (BOT-01 a BOT-09), seleção que abre detalhe (SEL-01/02), etapa futura neutra (ETP-01), separador, hover verde, retorno visual e dica (VIS-01 a VIS-04), conforme `docs/design-system/README.md`, refinando o PRD cap. 74 | Chat do proprietário, 09/10/2026: "ok, padronize todo esse design system para tudo que temos e faremos" |
| DEC-0910-02 | Merge na `main` feito pelos agentes: o revisor (Claude ou Codex) integra o PR do outro com CI verde no HEAD e parecer favorável escrito; o proprietário não é chamado para integrar; ninguém integra o próprio PR. Continuam com o proprietário custo, contrato ou conta, dados reais, ERP real, publicação a usuários reais e produção | Chat do proprietário, 09/10/2026: "Faça o merge entre voce e claude, nao quero trabalho pra mim" e, em seguida, "entre vc e codex" |

## Decisões do proprietário de 16/10/2026

Respondidas por Adrianus no canal do Claude, em lista de escolha, e pedidos dele feitos no mesmo dia. Valem como decisão dele (AGENTS §2). O detalhe está no protótipo, em `docs/integracao/V69/decisoes-proprietario-1610.md` e `docs/design-system/padroes-1610.md` (branch `claude/v44-v69-mapa`, commit 6b726d6).

| ID | Decisão | Fonte |
|---|---|---|
| DEC-1610-01 | **Peça comprada para manutenção fica reservada para a ordem que a pediu**, ao chegar no recebimento (D5) | Lista de escolha |
| DEC-1610-02 | **Teste com usuários reais** (3 a 5, 20 minutos) depois de terminar a melhoria dos demais módulos | Lista de escolha |
| DEC-1610-03 | **Mantida a aprovação agronômica individual de cada O.S.**; pré-autorização por limiares só se revê depois do piloto | PEND-01 (PRD 73.12) |
| DEC-1610-04 | **Só os valores numéricos de prazos e limites propostos ficam aceitos** como valores iniciais, configuráveis, a rever com os números do piloto: os de PEND-02, 04, 05, 06, 09, 11, 13, 14 e 16 e os prazos de reconhecimento de PEND-03. **Tudo o que não é número de prazo ou limite segue pendente**, no estado anterior, salvo decisão específica referenciada: quem trata, renova, publica, fica ciente ou recebe aviso; donos e escalonamento; fluxo, remédio, marcação, aviso ou bloqueio; alternativas. A pergunta só tratou de prazos e limites. Exemplos, sem lista fechada:<ul><li>PEND-03: quem trata cada tipo de chegada expirada;</li><li>PEND-04: destinatários do aviso;</li><li>PEND-05: quem renova ou vence manualmente e o encaminhamento acima do limite;</li><li>PEND-07: nota de leitura do 72.3;</li><li>PEND-08: escritor do abastecimento;</li><li>PEND-10: quem fica ciente;</li><li>PEND-11: donos e escalonamento;</li><li>PEND-12: marcação de confirmação do ERP;</li><li>PEND-13: quem publica a validade;</li><li>PEND-14: a alternativa de consolidação de menor custo;</li><li>PEND-15: aviso ou bloqueio no fechamento;</li><li>PEND-16: responsáveis e remédios.</li></ul>No protótipo, a proposta do PRD é só o padrão de demonstração | PEND-02 a PEND-16 (PRD 73.12), só os números de prazos e limites |
| DEC-1610-05 | **Nome exibido: Safrion**. "Do Talhão à O.S." fica como nome do PRD; logotipo em SVG quando houver | PEND-DS-04 (PRD 74.12) |
| DEC-1610-06 | **Propostas do design system aceitas**, sem modo escuro por enquanto. **Exceto a PEND-DS-04:** o nome exibido é o da DEC-1610-05 (Safrion), não o da proposta | PEND-DS-01 a 03 e 05 a 15 (PRD 74.12) |
| DEC-1610-07 | **Relato de problema:**<ul><li>alternativa "não consigo anexar a imagem";</li><li>prints guardados por 180 dias após o encerramento, ou apagados a pedido.</li></ul> | PEND-FB-01 e 02 (PRD 75.8) |
| DEC-1610-08 | **Equipe pequena com meta ligada a remuneração variável:** exceção permitida, com revisor posterior obrigatório antes do fechamento | PEND-18 (PRD 73.12) |
| DEC-1610-09 | **Barra do Mapa volta aos 9 nomes de 26/09:**<ul><li>Carência vira filtro de Colheita;</li><li>Insumos vira filtro de Ordens de serviço;</li><li>talhão sem laudo aparece "Sem laudo", em cinza.</li></ul> | DEC-0910-36 (PLA-01) |
| DEC-1610-10 | **Perfil do piloto aceito:**<ul><li>disponibilidade menor declarada;</li><li>atendimento em horário combinado;</li><li>alerta no celular do proprietário;</li><li>24×7 só na produção comercial.</li></ul> | PEND-OP-01 (PRD 75.8) |
| DEC-1610-11 | **Assistente de IA desligado** até a estimativa de custo por fazenda e mês, com provedores e local de processamento | PEND-IA-01 (PRD 75.8) |
| DEC-1610-12 | **Método obrigatório para tela e padrão.** Toda mudança de tela segue a skill `.claude/skills/padrao-safrion`: o pedido vale para todas as telas do mesmo tipo, corrige-se na peça comum, registra-se com ID, prova-se com varredura e contraprova e confere-se nas fotos antes de publicar | Pedido de 16/10: "crie uma skill e metodologia de trabalho melhor, porque toda hora eu preciso ficar te corrigindo, sobre padrões e outros" |
| DEC-1610-13 | **Padrões de lista** (TAB-08, VIS-06, AGR-02 em `padroes-1610.md`):<ul><li>tabela no visual das Atividades do plano, com seta de abrir e ícones de ordenar e filtrar em cada coluna;</li><li>cartões em linha com colunas alinhadas;</li><li>agrupar sem trilha.</li></ul> | Pedidos de 16/10 |
| DEC-1610-14 | **Cadastros no padrão comum:**<ul><li>formulários só com o essencial à gestão;</li><li>documentos para crédito no módulo Crédito;</li><li>fazendas e talhões numa lista só.</li></ul> | Pedidos de 16/10 |
| DEC-1610-15 | **Exceção exata no Gitleaks para 31 falsos positivos do histórico:**<ul><li>só os achados exatos (commit, arquivo, regra e linha) em `.gitleaksignore`, como a HML-SECRET-05;</li><li>são nomes de chave de localStorage do protótipo em commits antigos de branches de frente, não credenciais;</li><li>nada apagado do histórico; `.gitleaks.toml`, canários e escopo da varredura inalterados.</li></ul> | Pergunta do Claude ao proprietário em 16/10/2026, por volta das 14h UTC, na sessão [session_01Div8EjesSwVnpSUvYjZ7kh](https://claude.ai/code/session_01Div8EjesSwVnpSUvYjZ7kh), sobre a CI vermelha do PR #73 (achados no comentário 6217016316). Opções: exceção exata, reescrever o histórico das branches antigas ou apagá-las. Resposta escolhida por ele: "Exceção exata (Recomendado)" |

## Decisões delegadas de 09/10/2026 (Claude + Codex)

**Nada nesta seção é aprovação do proprietário**; a EXT-01 só registra, com a fonte, uma autorização anterior dele. São decisões dos dois agentes sob a delegação dele (DEC-0910-03); Adrianus pode mudar qualquer linha. Só entram como decididas as que têm acordo escrito do Codex, com o limite citado; as demais estão em "Pendentes de revisão do Codex", sem aprovação por silêncio. O PRD canônico fica inalterado até a conclusão de todas as implantações atuais; depois, compara-se e muda-se só o necessário, preservando IDs e requisitos (DEC-0910-06).

- **Recibos do Codex** no PR #47: [6091153950](https://github.com/adrptu/Safrion-Software-/pull/47#issuecomment-6091153950) (retorno inicial) e [6091443216](https://github.com/adrptu/Safrion-Software-/pull/47#issuecomment-6091443216) (DECISOES-REV-20261010-02, com oito esclarecimentos). Nenhum é prova de execução nem aceite dos IDs não revisados. "Frase geral" é a abertura de 6091443216: os ajustes de sequência, fontes, parâmetros, proteções em apuração e aceites delimitados atendem 6091153950, com os esclarecimentos. Nas linhas com acordo aos ajustes (6091443216), o Codex confere o texto final na revisão deste registro.
- **"Às fontes"** marca o acordo delimitado às fontes (6091153950): rastreabilidade, parâmetros e fontes versionadas, sem validar fórmula, norma, competência profissional ou interpretação legal ainda "a verificar". Referência candidata não vira regra certificada, e reverter não remove proteção obrigatória.
- **Detalhe por ID de origem** (padrão, dano evitado, base e reversão): [texto ao proprietário](https://github.com/adrptu/Safrion-Software-/blob/58fb55bdd3d758d20b26f2dad84b371b626344d3/docs/decisoes-delegadas/DECISOES-DELEGADAS.md), [entradas](https://github.com/adrptu/Safrion-Software-/blob/58fb55bdd3d758d20b26f2dad84b371b626344d3/docs/decisoes-delegadas/DECISIONS-entradas.md) e [inventário com as fontes](https://github.com/adrptu/Safrion-Software-/blob/58fb55bdd3d758d20b26f2dad84b371b626344d3/docs/decisoes-delegadas/INVENTARIO.md), e [confronto com o FOCO v2](https://github.com/adrptu/Safrion-Software-/blob/58fb55bdd3d758d20b26f2dad84b371b626344d3/docs/decisoes-delegadas/FOCO-v2-confronto.md), no commit `58fb55b`, que já traz os esclarecimentos de 6091443216. Onde diferirem, vale esta seção.
- **FOCO-APLICACAO-REAL v2:** fonte canônica na [issue #1, comentário 5974888468](https://github.com/adrptu/Safrion-Software-/issues/1#issuecomment-5974888468). Trechos e confronto com o checkpoint: [`docs/parceria/decisoes-delegadas-20261009.md`](parceria/decisoes-delegadas-20261009.md).

### Delegação (DEC-0910-03)

| Item | Registro |
|---|---|
| Canal do Claude | "voce e codex tomem todas deciões por mim, estarei fora." Chat do proprietário com o Claude, 09/10/2026, à noite (aproximado: entre ~21:40 e ~22:00 UTC), sem recibo de minuto |
| Canal do Codex | "Vc e o claude tomem todas decisões por mim, sempre na melhor prática. Vou esta fora, quando voltar não quero nada parado". Mensagem direta ao Codex, citada no PR #47 (comentário 6089857604, 09/10, 21:51 UTC); recebimento confirmado em 6091153950 e 6091443216 (item 8) |
| Cobre | Produto, regra, desenho, prioridade, sequência, escopo do protótipo e do software real, valores-padrão e parâmetros. Em segurança: decisão técnica interna, correção e teste dentro do acesso já concedido, com ADR quando material e revisão de outro autor (6091443216, item 7). Dado real desconhecido vira parâmetro explícito com padrão seguro, nunca inventado (6089857604) |
| Continua com o proprietário | Produção e publicação a usuários reais; dados reais; novos gastos, contratações, contas ou recursos de nuvem e efeitos externos (ERP real, mensagens reais) fora da autorização concreta (6091153950; AGENTS §2); alteração que exija consentimento específico; aceite da candidata. Não autorizado: reduzir ou contornar checks, proteções ou ruleset, ampliar privilégio, divulgar segredo novo ou mudar relação de confiança (6091443216, item 7) |
| Natureza | Delegação técnica, não aceite de candidata nem de produção (6091443216, item 8). Chegou direto a cada agente, no próprio canal: sem repasse entre agentes (AGENTS §2) e sem ratificação pendente (6091153950) |

### Decisões com acordo escrito do Codex

| ID (origem) | Decisão | Limite | Acordo | Implementação |
|---|---|---|---|---|
| DEC-0910-04 (PRC-01, PRC-02, PRC-03) | Sequência do protótipo por risco e dependência: concluir a correção BEN e a revisão DOM em curso; juntar as frentes prontas uma por vez, com os encaixes de cada uma logo depois da junção; depois, frentes novas uma por vez (3.1 aplicação segura e legal, 3.2 planejamento confiável, 3.3 irrigação medida, 3.4 cadastro que alimenta os processos). Aviso de demonstração nos cadastros que ainda não alimentam processos | Os passos são organização proposta, não lista exaustiva que exclua IDs existentes; onde divergem do checkpoint da issue #1, vale o checkpoint. BEN sem aceite global (S2 de origem por lote resolvido nos casos executados, parecer focal 6091321884). Nada publicado com risco impeditivo conhecido. Cada requisito fica no ID existente, sem outra fila | PRC-03: 6091153950 (delimitado). PRC-01/02: 6091153950 (ajuste) e 6091443216 (frase geral e item 5) | Em curso no protótipo; aviso pendente |
| DEC-0910-05 (PRC-06) | Passagem ao software real pelo FOCO-APLICACAO-REAL v2: concluir todo o conjunto vigente do protótipo, com candidata completa operável e validação e auditoria tripla; depois, transferir tela → domínio → banco → HML. Até lá, incrementos operáveis e revisados no protótipo, que segue acessível para comparação e sem evolução paralela depois da transferência. A C2 (PRs #32 a #35) fica preservada para a transição, sem interromper a autoria atual do protótipo | Conjunto vigente é todo o do checkpoint, não só os passos da DEC-0910-04. Frente isolada não libera a passagem. S2 escrito como caso de aceite não fica resolvido. A fatia real que liberar O.S. nasce com o CMD-42 por versão conferido no CMD-06, a família da operação e a habilitação; O.S. com agrotóxico é recusada até a fatia própria | 6091153950 (ajuste) e 6091443216 (item 5) | Pendente |
| DEC-0910-06 (PRC-04) | Registrar agora neste arquivo; PRD canônico inalterado até concluir todas as implantações atuais, com IDs, estados e provas conferidos; depois, comparar e mudar só o necessário, sem versão nova obrigatória | Só entra como decidido o que tem acordo escrito do Codex. Pendências do PRD não são antecipadas nem apagadas; IDs e requisitos ficam, mesmo com a implementação pendente | 6091153950 (ajuste) e 6091443216 (parágrafo final) | Este registro |
| DEC-0910-07 (PRC-05) | Reaproveitar as referências de mercado válidas (fonte oficial e data) e pesquisar só a lacuna concreta de módulo, sem repetir cinco pesquisas a cada teste ou correção | Nenhuma alegação de "acima do mercado" sem prova; referência de mercado não prova regra agronômica nem legal | 6091153950 e 6091443216 (frase geral) | Pendente |
| DEC-0910-09 (AGR-06) | Aplicação segura e legal: família da operação no catálogo; entre as operações agrícolas, dispensa do agrônomo só na irrigação sem produto, pela família e nunca pelo nome (manutenção e beneficiamento seguem com responsável próprio); reentrada conferida no CMD-06 e no CMD-07, salvo EPI permitido pela bula e registrado; O.S. não encerra com ocorrência de segurança sem destino | Às fontes: não valida a leitura da Lei 14.785/2023 nem da NR-31 (verificar vigência) | 6091153950 | Pendente (frente 3.1) |
| DEC-0910-10 (AGR-08) | Habilitação conferida no ato: CMD-42, receituário e publicação de plano conferem a credencial no servidor, na mesma transação; sem credencial válida, recusa com motivo; a decisão guarda o estado da credencial naquele momento | Às fontes: não valida competência profissional nem o alcance de cada habilitação; sem consulta automática ao conselho | 6091153950 | Pendente |
| DEC-0910-11 (OPE-07, OPE-18) | Carência e reentrada pela área e data realmente tratadas, para qualquer lavoura em pé ali. Aplicação relatada e ainda em conferência já protege, na união das áreas potencialmente afetadas, sem dupla contagem, marcada "preventiva · em apuração" | Sem geometria suficiente, vale a parcela ou o talhão identificável, com a incerteza à vista. O envelope preventivo nunca vira hectare executado, consumo ou custo; área só numérica não autoriza desenhar área exata. Nada aprova para trás; a apuração preserva o histórico. Testes especificados, não executados | 6091153950 e 6091443216 (item 3) | Pendente |
| DEC-0910-13 (b) (AGR-05) | Validade por fonte, com fonte, idade e expiração à vista (sonda e clima 24 h; previsão 12 h; telemetria 15 min; vistoria 7 dias; satélite ou drone 10 dias; solo 24 meses; foliar só na safra e no estádio da coleta). Dado vencido deixa de alimentar sugestão automática e não trava a decisão humana. Decide a PEND-13. **A exceção "12 meses se irrigado" foi substituída pela DEC-1610-04** (proprietário, 16/10/2026): vale o número proposto na PEND-13 (PRD 73.7.8), 24 meses da coleta, sem exceção para área irrigada; os demais números já eram os da PEND-13 | Valores marcados "proposta", parâmetros por fazenda, não recomendação certificada. A idade do dado, sozinha, não para a água sem produto e não passa por cima de segurança, equipamento, outorga ou permissão | 6091153950 (ajuste) e 6091443216 (frase geral) | Pendente |
| DEC-0910-14 (AGR-09) | Arrendamento vencido em renovação: a fazenda opera com aviso; o contrato ganha a situação Em renovação, Renovado ou Encerrado; só Encerrado trava abrir safra ou plantar cultura nova depois da data de saída | Às fontes: não valida a leitura do Estatuto da Terra nem do Decreto 59.566/1966 | 6091153950 | Pendente |
| DEC-0910-15 (OPE-01) | Quem libera: alçada AL-01 por fazenda, padrão "PCP ou gestor". Quem tem os dois papéis confirma uma vez, com texto que diz aprovar e liberar, e o sistema grava dois registros e dois recibos (CMD-42 e CMD-06). Decide a PEND-OS-01 | Versão, permissão e habilitação reconferidas no instante; quem só libera depende de aprovação válida da versão; sem sucesso parcial incoerente. Divergência do PRD abaixo | 6091153950 (delimitado) | Pendente |
| DEC-0910-16 (c, e) (OPE-04, OPE-06) | Mesmo fato só por identidade estável (mesmo recibo ou chave, ou relato que referencia o outro) ou prova inequívoca (mesmo medidor, mesma época sem zeragem, troca ou volta do contador, mesmo intervalo e mesmo contexto). Sobreposição parcial do totalizador, proximidade de volume, hora ou horímetro e o ramo ±0,2 h sem totalizador só apontam candidato à conferência, preservado e sem soma no saldo confirmado; trechos encostados são dois fatos. Decide a PEND-06 e a PEND-09 | "Vale o maior" só nos tipos com dois limites na CONC-10 (abastecimento e área), com o percentual sobre a fonte prevalecente (CONC-09); nenhum denominador inventado nem tolerância levada de um domínio a outro; prazos, limites e janelas marcados "proposta". Divergência do PRD abaixo. Testes de fronteira especificados, não executados | 6091153950 (ajuste) e 6091443216 (itens 1 e 2) | Pendente |
| DEC-0910-17 (OPE-07) | Fica ciente quem aprovou a versão quando o conferente aceita trabalho acima do autorizado ou fora dela; na irrigação só com água, o PCP. Decide a PEND-10 | Ciência não trava, não cria fila e não aprova para trás; divergência de dose segue na revisão técnica (B-R8); carência pela área na DEC-0910-11 | 6091153950 e 6091443216 (item 3) | Pendente |
| DEC-0910-18 (OPE-08) | O CMD-10 recusa encerrar enquanto um celular com a ordem informou registros não enviados. "Encerrar sem o aparelho" é ação do gestor, com motivo, autor, recibo e trilha; o que chegar depois entra como correção vinculada. A proposta PEND-17 da v3.10 vira regra | Nunca reescreve período fechado (entra como ajuste de competência anterior) nem presume consumo zero. Leitura delegada da DEC-2609-13, nas divergências abaixo | 6091153950 (delimitado) | Pendente |
| DEC-0910-19 (d) (MAN-08) | Na manutenção, abastecimento repetido só junta pela identidade da DEC-0910-16 (c); sobreposição parcial e candidatos próximos vão à conferência, sem soma nem junção silenciosa; dois abastecimentos legítimos próximos continuam dois | Entra depois da junção revisada da frente de manutenção; a regra de impedimento só é publicada depois da revisão do Codex | 6091153950 (ajuste) e 6091443216 (item 1) | Pendente |
| DEC-0910-21 (b) (OPE-18) | O ciclo perene termina com a O.S. de erradicação ou renovação encerrada, na data e na área reais. A safra 2025/26 continua Encerrada, com "2 cultivos em campo"; a sucessora sem colheita registrada da anterior gera aviso na liberação e no início e pendência ao PCP | Carência pela área na DEC-0910-11 | 6091153950 (área e data reais) e 6091443216 (item 3) | Pendente |
| DEC-0910-22 (OPE-17) | Talhão indisponível por período (tipo, início, fim, área e documento): embargo ambiental e área arrendada a terceiro travam o planejamento de cultivo e o CMD-06 até o desembargo ou o fim do contrato; pousio e reforma só avisam | Às fontes: não valida a leitura da Lei 9.605/1998 nem do Decreto 6.514/2008. A trava do embargo e do arrendado não se desliga por configuração; atividade exigida pelo órgão passa com documento, mantida a aprovação agronômica quando houver produto | 6091153950 | Pendente (frente 3.2) |
| DEC-0910-24 (c) (MAN-01) | Ordem de manutenção aprovada pelo responsável de manutenção, com alçada própria. Valores do protótipo rotulados "demonstração"; no real, sem política publicada, a autorização sobe ao nível mais alto | Ativo bloqueado nunca é programado nem liberado por alçada; registro de fato não é autorização para trás; o pedido de compra ligado à OM segue a alçada de compras | 6091153950 (delimitado) | Pendente |
| DEC-0910-25 (a) (SUP-04) | Recebimento com duas comparações separadas: comercial (contrato ou pedido e tolerância declarada por item; sem tolerância, 0 %) e metrológica (incerteza da balança só com origem técnica em CF-02; sem ela, "incerteza a conferir"). Decide a tolerância da DEC-07; a exposição de compras continua pendente | A metrológica não amplia o contrato, e a falta de incerteza não anula a tolerância contratada. Fora da faixa, o excedente fica bloqueado, pendente de decisão, e a falta preserva o saldo a receber. Nota, medido e pedido divergentes seguem a conferência, e incerteza presumida nunca dispensa a divergência. O físico medido não autoriza pagamento nem aceite financeiro; ±10 % não é padrão, e o 1 % como incerteza automática saiu (a tolerância de 1 % a granel da CONC-10, entre registros da mesma entrega, é outra coisa) | 6091153950 (ajuste) e 6091443216 (item 4) | Pendente |
| DEC-0910-27 (SUP-12) | Terra em linha própria, fora do custo operacional e dentro do custo total. Terra própria só com custo de oportunidade na visão econômica, marcado "estimativa"; formação do perene volta como depreciação | Às fontes: não valida a leitura dos CPC; política e vida útil com o contador | 6091153950 | Pendente (ajuda do cadastro no passo 1; linha própria com o CONTROLE-02) |
| DEC-0910-28 (a) (SUP-13) | Peça recondicionada entra pelo custo do recondicionamento, como item próprio ligado ao novo; a peça retirada vale zero antes do serviço | Às fontes: CPC 16 (R1) a conferir com o contador | 6091153950 | Pendente |
| DEC-0910-29 (a) (MAN-02) | Criticidade A, B ou C como atributo do ativo, dada pelo responsável de manutenção com motivo e revista a cada safra; sem classe, "A classificar", ordenado com a A | Classes da demonstração rotuladas sintéticas; nenhuma classe libera ativo bloqueado | 6091153950 (delimitado) | Pendente |
| DEC-0910-31 (PRO-01) | Massa da saca é dado de cada contrato, gravado com a fonte e nunca recalculado; contrato novo com campo obrigatório, sem valor pré-selecionado | No real, sem valor-padrão; 60 kg só nos quatro contratos sintéticos identificados; históricos nunca reinterpretados | 6091153950 (delimitado) | Pendente |
| DEC-0910-32 (c, d) (PRO-04, PRO-05) | Tabela de descontos por armazém, com documento e vigência; padrão de classificação cadastrado e versionado, ativo só depois de conferido na fonte oficial | Às fontes: IN citadas a verificar; tabela de referência não vira regra certificada; sem norma ativa, "a conferir" | 6091153950 | Pendente |
| DEC-0910-33 (IRR-01) | Outorga vencida "em renovação" só vale com protocolo no prazo e pedido não negado. No real, os parâmetros por órgão não têm padrão de fábrica; até serem cadastrados com norma e fonte, só vale com documento do protocolo que diga que a outorga continua válida. Conferida no CMD-06 e no CMD-07 | Às fontes: não valida a leitura da Lei 9.433/1997 nem a regra de cada órgão; a premissa do protótipo é rotulada "regra do órgão não conferida" | 6091153950 | Pendente |
| DEC-0910-34 (IRR-02) | Cada outorga limita o próprio ponto e o próprio ato; a rede declarada acrescenta o limite físico da bomba e da adutora; pivô sem vínculo a um ponto não libera | A rede não autoriza somar outorgas independentes; limite conjunto só com ato do órgão que cubra os pontos; reverter não remove o limite por ponto e por ato | 6091153950 (às fontes) e 6091443216 (frase geral) | Pendente |
| DEC-0910-38 (b) (PLA-05) | Nenhum controle técnico de qualidade e segurança é reduzido por prazo. Decisões técnicas internas, correções e testes dentro do acesso já concedido seguem delegados, com ADR quando material, análise de risco e revisão de outro autor. Decide a DEC-04 | Checks, proteções e ruleset se mantêm; nenhuma redução, bypass, ampliação de privilégio, nova divulgação de segredo ou mudança de confiança; "só por ADR" não autoriza enfraquecer controle; o que exige consentimento específico segue esse consentimento | 6091153950 (delimitado) e 6091443216 (item 7) | Regra de processo |
| DEC-0910-39 (PLA-06, DS02, DS03, DS04, DS09, DS15) | "Concluída" só com a condição cumprida e vermelho só para impedimento real (PLA-06); "Sobras a receber" (DS02); só tema claro (DS03); nome "Do Talhão à O.S." numa constante única (DS04); menu recolhido com 64 px (DS09); "Vencida · devolvida ao disponível" (DS15) | Controles mantidos, estado verdadeiro, vocabulário único, contexto e foco, origem da demonstração e aviso de ligação ausente; marca comercial e INPI com o proprietário | 6091153950 (delimitado) | Pendente |
| DEC-0910-39 (DS06, DS10, DS13) | Quebras de largura em < 768, 768–1279 e ≥ 1280 px, com cartão no celular só onde a tarefa ganha (DS06); rampa própria do NDMI do contrato C4, com nome, fórmula e fonte exatos (DS10); precisão por unidade e regra de domínio, igual no cálculo, nas tabelas e nos documentos (DS13) | O cartão não perde comparação nem ações da tabela; conferir leitura, teclado, foco e largura real, reaproveitando DS e NAV aceitos. O NDMI não é trocado pelo NDWI, e a rampa não diagnostica "seco" ou "úmido" nem comanda irrigação. Duas casas não apagam dose pequena, área, massa ou conversão; número compacto só onde não impede decisão, com o valor exato acessível | 6091153950 (ajuste) e 6091443216 (frase geral) | Pendente |
| EXT-01 | Registro de autorização anterior do proprietário, não decisão dos agentes: desenvolvimento, QA e HML já autorizados, com referência de US$ 30/mês antes de tributos (aceite de 29/09 em [R-006-hospedagem](parceria/rodadas/evidencias/R-006-hospedagem.md)) e US$ 10/mês de GitHub Actions. Não se pede de novo | Fonte do Actions: canal do proprietário com o Codex, citação atestada em 6091443216, sem link nem data da concessão original; o R-006 sustenta só a HML. O R-006 mantém o plano revisado antes de cada apply, com veto do proprietário, e alerta não é teto de cobrança. Antes de alegar bloqueio de login ou faturamento, conferir a conta; ato pendente fora da autorização é registrado com a prova, sem bloquear trabalho independente | 6091153950 e 6091443216 (item 6) | — |
| EXT-02 | US$ 15/mês no Cloud Run é proposta interna dos agentes | Não é teto aprovado nem garantia de cobrança limitada; alerta de orçamento não é teto de cobrança | 6091153950 e 6091443216 (item 6) | — |

### Divergências com o PRD, para a comparação final

O PRD não muda agora (DEC-0910-06). Até a comparação, vale a decisão, nos limites citados.

| Decisão | Texto atual | Diferença |
|---|---|---|
| DEC-0910-16 (c, e) e DEC-0910-19 (d) | A CONC-05 trata como o mesmo abastecimento os intervalos do totalizador sobrepostos e, sem totalizador, a mesma leitura do ativo (±0,2 h ou ±2 km). O exemplo da CONC-11 e os aceites AC-75 e AC-105 usam "mesmo horímetro" como identidade | Só identidade estável ou prova inequívoca juntam; sobreposição parcial e leitura próxima vão à conferência, sem soma (6091443216, item 1) |
| DEC-0910-15 | 73.1 (leitura da DEC-2609-05), APROV-09 e AC-142 retiram a ação composta "Aprovar e liberar", e a 74.8 a põe em "Não use" | Confirmação única para quem tem os dois papéis, com dois registros e dois recibos, pelo pedido mais novo do proprietário (01/10, PEND-OS-01) |
| DEC-0910-18 | DEC-2609-13: "Encerrar exige apontamentos enviados" | Exceção "Encerrar sem o aparelho", do gestor, com motivo e trilha; o fato tardio entra como correção vinculada |
| DEC-0910-39 (DS10) | 74.7.1 e PEND-DS-10 tratam a paleta do NDWI, com classes "muito seco" e "seco" | NDMI do contrato C4, sem trocar pelo NDWI e sem diagnóstico de seco ou úmido (6091153950) |

### Pendentes de revisão do Codex

Propostas do texto ao proprietário; **não são decisões**. Até o acordo escrito do Codex, vale o que já está no PRD e nas tabelas acima.

| Entrada (origem) | Tema | Pendência que toca |
|---|---|---|
| DEC-0910-08 (AGR-01) | Aprovação individual mantida; pré-autorização por limiares não adotada | PEND-01 |
| DEC-0910-12 (AGR-02, AGR-03) | Sugestão de gesso, calagem e adubação só com fonte publicada | DEC-08 |
| DEC-0910-13 (a, c) (AGR-04, AGR-07) | Laudo por zona; conferência de bula, alvo, carência e unidade no plano | — |
| DEC-0910-16 (a, b, d) (OPE-02, OPE-03, OPE-05) | Prazos do pacote sem sinal; envio expirado; nota de leitura em 72.3 | PEND-02, 03 e 07 |
| DEC-0910-19 (a, b, c) (OPE-09, OPE-10, OPE-11, SUP-11) | Correções S2 nas frentes de domínio, demanda e suprimentos, com severidade a confirmar | — |
| DEC-0910-20 (OPE-12 a OPE-15) | Planejamento confiável, tabela do Planejar safra, custo mensal no Orçamento e recurso que atende duas fazendas | PEND-CTL-03 |
| DEC-0910-21 (a) (OPE-16) | Folga de liberação do talhão | — |
| DEC-0910-23 (SUP-01) | Ajuste de inventário e revisão independente | PEND-CTL-02 |
| DEC-0910-24 (a, b) (SUP-02, SUP-03) | Alçada única de compra; sem teto por O.S. | — |
| DEC-0910-25 (b) (SUP-05) | Saída da quarentena | — |
| DEC-0910-26 (SUP-06 a SUP-10) | Validade, renovação e cota das reservas | PEND-04, 05, 15 e 16; proposta PEND-19 |
| DEC-0910-28 (b, c, d) (SUP-14, MAN-03, MAN-06) | Reposição, custo-hora e capacidade da oficina | — |
| DEC-0910-29 (b) (MAN-05) | Reserva de peças da OM | — |
| DEC-0910-30 (MAN-04, MAN-07, MAN-09) | Pneus, preventiva e abastecedor por ponto | PEND-08 |
| DEC-0910-32 (a, b, e a n) (PRO-02, PRO-03, PRO-06 a PRO-15) | Produção, crédito, entrega, unidades e previsão | DEC-03, DEC-06 |
| DEC-0910-35 (IRR-03, IRR-04) | Lâmina 21 h e origem do volume | — |
| DEC-0910-36 (PLA-01) | Barra do Mapa | — |
| DEC-0910-37 (PLA-02, PLA-03) | Cobrança pela área contratada e régua de atraso | DEC-01 |
| DEC-0910-38 (a) (PLA-04) | Entrada por papel | DEC-02 |
| DEC-0910-39 (DS01, DS05, DS07, DS08, DS11, DS12, DS14) | Cores das fases, fontes, barra do Mapa, estados da safra, Solo, satélite e sons | PEND-DS-01, 05, 07, 08, 11, 12 e 14 |
| DEC-0910-40 (PLA-07 a PLA-13) | Integração com ERP | PEND-11, 12, 14 e 18; propostas PEND-20 a 22 |
| DEC-0910-41 (PLA-14 a PLA-22) | Relatar problema e adoção | PEND-FB e PEND-USO (PRD 75.8) |
| DEC-0910-42 (PLA-23) | Papéis com vigência e exportação | — |
| DEC-0910-43 (PLA-24) | PEND-REPO-01 resolvida pelo fato conferido | PEND-REPO-01 |
