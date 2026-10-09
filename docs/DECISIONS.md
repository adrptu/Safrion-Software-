# Decisões

Índice das decisões do produto e da engenharia. **A regra completa está sempre no PRD** (`docs/PRD.md`); este arquivo só aponta para ela, para evitar texto duplicado e divergente.

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

Até a decisão, vale o comportamento conservador descrito no próprio PRD.

| ID | Tema | Onde ler |
|---|---|---|
| DEC-01 | Hectare ativo × área física produtiva contratada | PRD 70.4 |
| DEC-02 | Entrada por papel × mapa | PRD 70.4 |
| DEC-03 | Meta de previsão | PRD 70.4 |
| DEC-04 | Gates técnicos | PRD 70.4 |
| DEC-05 | Preços e trial dos parceiros | PRD 70.4 |
| DEC-06 | Distribuição de oportunidades | PRD 70.4 |
| DEC-07 | Tolerâncias e exposição de compras | PRD 70.4 |
| DEC-08 | Gessagem e subsuperfície | PRD 70.4 |
| DEC-09 | Trial do agricultor e franquias | PRD 70.4 |
| PEND-01.. | Pendências da revisão v3.10 (confiabilidade transacional, offline e desempenho), entre elas a proposta de pré-autorização por limiares, **não aprovada** | PRD 73.12 |
| PEND-REPO-01 | Em 27/09 o proprietário informou "Fiz upgrade no git", e a CI remota voltou a rodar. Plano exato ainda não conferido; se permitir, aplicar a proteção da `main` (`tools/github/configurar_protecao.sh`). Texto anterior: **só se o plano da conta for Free** (ainda não verificado): proteção da `main` imposta pelo servidor em repositório privado exige GitHub Pro (custo mensal da conta). Opções: contratar o Pro; ou manter privado sem proteção imposta, com a disciplina de pull request, CI e parecer escrito. Tornar público só por decisão expressa. **Até decidir:** privado, sem proteção imposta, disciplina de processo. | `docs/STATUS.md`, bloqueio 2 |
| PEND-DS-01.. | Pendências do design system (modo escuro, marca, fontes de títulos e outras) | PRD 74.12 (em revisão) |
| PEND-OS-01 | O.S. sem etapa de revisão (pedido de 01/10) × DEC-2609-05. **Padrão adotado:** "Liberar para execução" é o "Aprovar e liberar" do PRD 41.3, gravando aprovado por (CMD-42) e liberado por (CMD-06) em separado | issue 1, comentário 6001191813 |
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
