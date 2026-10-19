# V68 · VISOES-2 (V2-1) e pedidos do proprietário de 14/10/2026 (noite)

Dados sintéticos. Branch `claude/v44-visoes2`, juntada na linha publicada `claude/v44-v66`. Regime leve do protótipo (AGENTS §3.5).

| ID | Pedido | O que mudou | Prova (executado) |
|---|---|---|---|
| V2-1 | VISOES-2 ([pedido-1410](../VISOES-2/pedido-1410.md), [ESPEC](../VISOES-2/ESPEC.md)) | O.S. como piloto. Lista e agrupada viram uma **Tabela** só, com "Agrupar por", descer por nível e trilha. A trilha fica no endereço e aceita "/" no nome. A tabela abre só com as colunas essenciais e o seletor "Colunas +N" mostra as outras. Kanban, Calendário e Carga leem o mesmo recorte (trilha e filtros), mostrado em chips com "N de M ordens no recorte". No Kanban, as raias seguem o grupo; uma O.S. em duas raias mostra "Também na raia X". No Calendário, a O.S. de vários dias vira uma faixa só, sem botão repetido. O.S. sem talhão vai para o grupo "Sem talhão". Com a ponte do painel (`#painel=`), trilha e grupos ficam suspensos. | `visoes2_ag_unit` 9/9, `visoes2_agrupar` 3/3, `visoes2_colunas` 14/14, `visoes2_formas` 12/12, `visoes_unit` 24/24, `visoes` comp 9/9, celular 10/10, e2e 43/43, e7 2/2, `tabelas_os` 40/40, `ostest` 33/33, `os_cenario` 22/22 |
| PA-PILOTO | VISOES-2 §13 ("comece pelas Atividades do plano") | Atividades do plano no padrão visual: ícone da operação, só o número do gatilho, total da seção, menu ⋯ (Esc fecha e devolve o foco; setas entre itens) e Desfazer de 5 s. | `patest` 50+/50+ (ver bateria), `pa_regras` 18/18, `visual_corte` PA sem achado |
| PA-ENXUTO | "em planos agronomicos tire cultivos que usam esse plano e versoes. nao agregam quase nada" | Saíram os blocos "Cultivos que usam este plano" e "Versões". A regra continua: editar cria o rascunho, publicar não altera os cultivos, e a troca de versão é por cultivo no Planejar safra (aviso do rascunho). Com rascunho aberto, o selo diz também a versão que segue valendo: "Rascunho v7 · v6 em vigor". | `patest`, `pa_lista` L6/L14a/L17 |
| AGR-FLUXO | "faça um teste nesses sub menus como se fosse um fluxograma com setas de linhas curvas, separando em 3 fases/blocos (...) sem escrever isso" | A tela de entrada do Agrícola mostra os cartões em 3 blocos sem título, na ordem do processo, ligados por setas curvas: Agrofit → Análises de solo → Planos → Planejar safra → Orçamento · Pragas e doenças → Ordens de serviço → Irrigação → Colheita · Recebimento → Beneficiamento → Estoque de produto → Custos → Painel. Teste só no Agrícola; os outros módulos seguem em grade. | `mod_fluxo` 21/21, `visual_corte` MOD sem achado, `painel_modulos --ui` 61/61 |
| MENU-INICIO | "eliminar esse primeiro botão de inicio mapa porque faz a mesma funcao do icone do proprio mapa" | Saiu o bloco "Talhão à O.S." do topo da barra lateral; o Mapa continua no primeiro item. | `nav_modulos` N1/N5 |
| MENOS-TEXTO | "Termine de tirar essas descrições abaixo dos titulos e também textos soltos na tela. menos é mais." | Saíram: a linha "cultura · atividades · R$/ha · gatilhos" e "Editar cria o rascunho…" nos Planos; "<Módulo> · Todas as fazendas e safras · Estado atual" nos painéis; o rótulo "Módulo oculto no menu · preservado". | `textos_soltos` (frases tiradas acusadas se voltarem) |
| Codex 6168779649 | Achados S3 da V2-1 | Trilha com "/", filtro de Talhão limitando os grupos, Colunas no celular em grade de até 5 (4b92ea2). | aceite do Codex no PR #47 |
| Codex 6169663018 | PA-DESFAZER-01 (S2) e PA-DESFAZER-02 (S3) | Desfazer devolve só a atividade excluída e preserva o que mudou depois; o rascunho só sai quando fica igual à versão publicada; publicar ou descartar invalida o Desfazer. O Desfazer fica à vista quando a última atividade sai. | `patest` PA-DESFAZER-01/02 e controle |

## Decisões tomadas pelos agentes
- **Ordem do fluxo:** Análises de solo vem antes de Planos agronômicos (a análise alimenta a recomendação). Só a tela de entrada mudou; o menu e as telas seguem iguais.
- **Painel fecha o fluxo** no Agrícola; nos outros módulos continua o primeiro cartão.
- **Versões fora da tela, não fora do domínio:** rascunho, publicação e histórico continuam no cenário; quem precisa saber o que vale para as O.S. lê no selo.
- **Oráculos ajustados, sem afrouxar:** a linha da O.S. é achada pelo código visível (`OS-0000`), porque o estado curto em vermelho vem antes dele (C2). A tabela de O.S. com 6 colunas cabe na tela: N8 passa a exigir largura natural (nunca menor que o contêiner) e o selo de Fase em uma linha.

## Bateria

Resultado a preencher ao fim do reteste.

## Publicação

A preencher.
