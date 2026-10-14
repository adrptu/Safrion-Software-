# V66 · Manutenção limpa e retorno visual dos botões

Autor e integrador: Claude. Revisor: Codex (regime leve do protótipo, AGENTS §3.5 e §3.6). Base: composição v65 (`int/v65`, `f6cf9ff`). Dados sintéticos.

## Pedido (proprietário, 14/10/2026)
"O backlog de manutenção que depois pode virar O.S. já está nas funcionalidades? A separação por filtros de corretiva, preventiva dos planos, inspeção etc. já está bem organizada para o foco do PCM? Em manutenção os filtros não estavam seguindo o padrão que definimos. Elimine também os cards de manutenção, vamos focar os cards na área de gráficos e relatórios. Telas principais mais clean… Botões como salvar, cancelar e outros estão com feedback visual?"

## Decisões (delegadas aos agentes; registro para o revisor)
| ID | Decisão | Por quê |
|---|---|---|
| MAN-LIMPA-D1 | "Cards de manutenção" são os cartões de indicador da tela de trabalho (Sem ordem, Ordens e Ativos). Saem. Os indicadores ficam no Painel de Manutenção. | O pedido diz para focar os cartões na área de gráficos e relatórios. Os cartões da tela de entrada (Painel, Sem ordem, Ordens, Ativos, Planos) são navegação, como nos outros módulos, e ficam. |
| MAN-LIMPA-D2 | A faixa Filtros com o funil é um componente comum (`ui37.faixa_filtros`, `MF_SEL`, `MF_LBL`), o mesmo da O.S. | É o padrão de 14/10 ("teste o símbolo de filtro… fica só o funil"); uma fonte só. |
| MAN-LIMPA-D3 | Tipo de PCM: Preventiva (vencimento de plano; ordem preventiva), Corretiva (relato de falha, alerta de condição; ordem corretiva), Inspeção (achado de inspeção ainda sem ordem). Em Ordens, só Preventiva e Corretiva. | São os tipos que existem nos dados. Preditiva e melhoria entram quando houver dado que as distinga. |
| MAN-LIMPA-D4 | Cada visão mostra só os filtros que valem para ela: Sem ordem e Ordens (Tipo, Criticidade, Grupo); Ativos (Grupo, Pendência); Planos (Grupo). No celular, a faixa é uma linha que rola de lado, sem o rótulo visível. As opções já dizem o que são ("Todos os tipos"), e o nome acessível continua no seletor. | Menos controles sem efeito; ≥ 5 linhas acima da dobra a 390 px (AC-PCM-22). |
| MAN-LIMPA-D5 | Saem o seletor de período (servia só aos cartões), o seletor de plano (a coluna Item filtra) e os chips Vencimentos e Achados (viraram o Tipo). "Espera por peça" vira filtro rápido de Ordens. | Nada que filtrava se perde; um controle por função. |
| MAN-LIMPA-D6 | Lista e Kanban das ordens são ícones com nome, como na O.S. | O mesmo padrão nas duas telas de ordens. |

## Pedidos seguintes do proprietário (14/10, na mesma rodada)
| ID | Pedido | Feito |
|---|---|---|
| SEM-VERCOMO-01 | "Tire das telas 'ver como simulação'" | A faixa sai da Manutenção e das 4 telas do app. Na web, quem age é o perfil do avatar do menu lateral (a mesma fonte, `g2perfil`), que já lista todos os perfis. No app, quem usa é escolhido no nome do cabeçalho do "Hoje no campo" (Marcos, Zé, João), com a mesma troca de antes (`c.app.usuario`). O menu ⋯ da Manutenção vai para o fim dos comandos do cabeçalho. |
| FILTRO-TITULO-01 | "Nos filtros não precisa repetir o texto tipo, criticidade" e, em seguida, "na verdade precisa manter o título de cada filtro para o usuário não se perder" | Prevalece a segunda: cada filtro mantém o título, também no celular. Os rótulos tirados por um instante voltaram antes de qualquer envio. |
| FAIXA-ALTURA-01 | "Trabalhando em… ficou muito estreito o componente visual" | A faixa ("Filtros" ou "Trabalhando em") tem o mesmo respiro com ou sem ação no fim: 8 px por 14 px, altura mínima de 48 px. Antes perdia o espaçamento quando tinha "Trocar safra". |

## Defeitos corrigidos
- O seletor Grupo das visões Ativos e Planos não filtrava: o estado só era aplicado à lista Sem ordem.
- Botão indisponível mostrava o cursor de "mão": o estilo do próprio botão vencia a regra comum. Agora vale o cursor de proibido.
- Aviso (UX-BEN35-AVISO-01, revisão Codex 6159767011): a primeira correção apagava a âncora inferior do aviso, que ia para o topo e cobria "‹ Suprimentos", "Início" e "Mapa". Regra agora:
  - fica centrado na área de conteúdo, nunca sobre o cabeçalho, o retorno do módulo ou a barra lateral;
  - a âncora do pé é guardada e restaurada;
  - se cobrir um controle visível, sobe até a primeira faixa livre da altura dele;
  - sem faixa livre (aviso de 4 linhas a 390 px sobre uma lista com um link a cada 44 px), fica no pé e some no primeiro toque, clique, tecla ou rolagem da pessoa; o mesmo texto depois volta a aparecer;
  - o fundo escuro de tela inteira atrás de um painel não conta como controle.

  Por que não "nunca sobre controle nenhum": a 390 px, um aviso de 94 px sobre uma lista densa não tem lugar livre, e qualquer aviso sobreposto cobriria algo. A alternativa sem sobreposição empurraria o conteúdo (o alvo muda de lugar sob o dedo). A verificação AV do `ben_fluxo` mede a cobertura pela ordem das camadas, não só pela geometria. Ela reprova:
  - a espera para tocar;
  - o aviso sobre o alvo, a navegação ou o cabeçalho, ou fora da tela;
  - o aviso sobre um controle quando havia faixa livre.
- MAN-LIMPA-GRUPO-01 (S3, revisão Codex 6160153073): em Ativos › Abastecimentos o seletor Grupo aparecia e as 8 linhas ficavam. Agora o Grupo filtra os lançamentos pelo ativo de cada um. Limpar o filtro restaura todos, e o grupo continua ao voltar a Ativos (`man_limpa` L8).

## Para o Painel (PAINEL-02, Codex, `areas/paineis.py`)
Indicadores que saíram da tela e devem aparecer no Painel de Manutenção, com a fórmula no ⓘ e a mesma fonte da tela:
- vencidas sem ordem e em breve sem ordem;
- achados críticos sem ação;
- ordens críticas abertas;
- backlog em HH (ordens abertas, soma do tempo previsto);
- sobras a receber e espera por peça;
- aptos agora (de N);
- cumprimento de preventiva;
- custo de manutenção do período;
- MTBF e MTTR (hoje "não estimável", sem histórico de falhas).

Divergência a alinhar: o Painel conta "Pendências sem ordem" com `manSemOm` (só serviços preventivos devidos; 3 na demonstração), e a tela conta Sem ordem com vencimentos até 10 dias mais achados de inspeção, relatos e alertas (6). O mesmo nome precisa da mesma conta.

## Testes (executados na v66 montada)
| Teste | Resultado | Contraprova (v65 montada) |
|---|---|---|
| `man_limpa_test` (novo) | 8/8 | 1/7 (sem o L8) |
| `botoes_retorno_test` (novo) | 6/6 | 5/6: o cursor do botão indisponível |
| `ben_fluxo sobra390 conferencia390` (AV) | 16/16 | aviso da v65 (`4f222e8`): 8/9, sobre "Início (Mapa)", "Mapa", "‹ Suprimentos" e o "×" do painel |
| `ben_fluxo sobra conferencia` (desktop) | 16/16 | — |
| Manutenção, navegação e filtros | ver `bateria.md` | — |

O hover (passar o mouse) é verificado pela regra que vale para cada botão. O Chrome sem janela não declara mouse com hover, e a emulação não muda isso. O "pressionar", o foco pelo teclado, o indisponível e o realce depois de Salvar são medidos no pixel.
