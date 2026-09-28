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
| PEND-01.. | Pendências da revisão v3.10 (confiabilidade transacional, offline e desempenho), entre elas a proposta de pré-autorização por limiares, **não aprovada** | PRD 73.12 (em revisão) |
| PEND-REPO-01 | Em 27/09 o proprietário informou "Fiz upgrade no git", e a CI remota voltou a rodar. Plano exato ainda não conferido; se permitir, aplicar a proteção da `main` (`tools/github/configurar_protecao.sh`). Texto anterior: **só se o plano da conta for Free** (ainda não verificado): proteção da `main` imposta pelo servidor em repositório privado exige GitHub Pro (custo mensal da conta). Opções: contratar o Pro; ou manter privado sem proteção imposta, com a disciplina de pull request, CI e parecer escrito. Tornar público só por decisão expressa. **Até decidir:** privado, sem proteção imposta, disciplina de processo. | `docs/STATUS.md`, bloqueio 2 |
| PEND-DS-01.. | Pendências do design system (modo escuro, marca, fontes de títulos e outras) | PRD 74.12 (em revisão) |

## Decisões de arquitetura (ADR)

Ficam em `docs/adr/`, uma por arquivo, no modelo `0000-modelo.md`. As escolhas já fixadas pelo PRD (caps. 12, 23 e 28) estão resumidas em `0001`. Mudar uma delas exige ADR nova que demonstre o mesmo requisito (PRD 12.1).

| ADR | Título | Situação |
|---|---|---|
| 0001 | Arquitetura e stack de referência adotadas pelo PRD | Aceita (origem: PRD 12.1, 23.1, 28) |
| 0002 | Repositório privado com documentação e CI antes do código de produto | Aceita (proprietário, 27/09/2026) |
| 0005 | Hospedar a HML em southamerica-east1 (São Paulo) | Proposta (revisão do Codex pendente) |
