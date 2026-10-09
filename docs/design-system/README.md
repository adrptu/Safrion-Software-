
## Padrões do proprietário de 09/10/2026 (valem para tudo o que existe e o que vier)

Decisão do proprietário no chat em 09/10/2026: "ok, padronize todo esse design system para tudo que temos e faremos". Os padrões abaixo refinam o capítulo 74 do PRD (DS-02, DS-17, DS-31, DS-33 e DS-61), sem contrariá-lo. Valem para o protótipo e para o software real (`packages/ui`). Tela nova já nasce assim, e tela existente é corrigida na varredura de conformidade.

### Botões e ações

| ID | Regra | Por quê |
|---|---|---|
| BOT-01 | **Um verde por contexto.** Os contextos são: cabeçalho da página (tela do menu), bloco "Próximo passo" (detalhe), fim da etapa (processo), rodapé de painel e faixa inferior do app. Bloco comum de conteúdo não tem verde | O olho acha a próxima ação sem comparar dois verdes |
| BOT-02 | **Lugar por tipo de tela.** <ul><li>Tela do menu: no cabeçalho, à direita do título.</li><li>Processo em etapas: no fim da etapa, como "verbo do próximo passo ›"; o cabeçalho fica sem verde.</li><li>Detalhe: no "Próximo passo"; o cabeçalho fica sem outro verde.</li><li>Painel: no rodapé, com o verbo do efeito.</li></ul> | Mesma ação, mesmo lugar, em todas as telas |
| BOT-03 | **Verbos fixos.** <ul><li>**Criar:** registro novo e independente (safra, ordem, plano, talhão).</li><li>**Incluir:** item dentro de outro registro (atividade no plano, insumo na atividade).</li><li>**Programar:** quando a finalidade é agendar uma execução (ordem, irrigação, manutenção). Ter um campo de data não muda a finalidade: um formulário com data de compra continua sendo Criar ou Registrar compra.</li><li>Nos demais casos, o verbo do efeito: Liberar, Publicar versão v7, Aprovar e emitir.</li></ul> Nunca "Novo/Nova", "OK", "Confirmar" sozinho ou "Ver …" como primário | O rótulo diz o que acontece (DS-33) |
| BOT-04 | **Tamanho por lugar.** <ul><li>Padrão: cabeçalho da página e fim da etapa.</li><li>Compacto: cabeçalho de bloco, "Próximo passo" e rodapé de painel.</li><li>Mini: linha de tabela e painel do mapa.</li><li>Grande: ação de campo no app, com 44 px ou mais (DS-15).</li></ul> | Hierarquia visual coerente com o lugar |
| BOT-05 | **Ícone consistente.** "+" em todo Criar e Incluir; ícone do efeito quando ajuda (calendário em Programar); sempre com rótulo; nunca só em parte dos botões do mesmo papel | Reconhecimento rápido sem ambiguidade |
| BOT-06 | **Secundário (branco).** Para criar ou incluir dentro de um bloco e para ações menos frequentes. Até duas secundárias visíveis por contexto; o resto vai para um menu | Não compete com a primária |
| BOT-07 | **Linha de tabela com uma ação só.** A linha tem um alvo único que abre o registro, num painel ou num detalhe: um link ou botão semântico, com nome acessível e acionável pelo teclado. Não depende de clique na linha (`tr`), e os controles de uma tabela editável não abrem o registro. A coluna "Próximo passo" é texto. Editar e excluir ficam no painel, exceto o ícone de excluir linha em tabela editável | Evita o mesmo comando duas vezes no mesmo alvo e o toque duplo que cai na linha seguinte |
| BOT-08 | **Navegação não é primária.** Botão que só troca de tela vira link ou "Voltar". A exceção é o avanço de etapa do processo (BOT-02) | Verde só para decisão |
| BOT-09 | **Componente único.** Todo botão sai do componente comum: no protótipo, o do `engine`; no software real, `packages/ui`. Nada de estilo escrito à mão | A regra se mantém sozinha; o teste de conformidade confere |

### Seleção, estados e retorno

| ID | Regra | Por quê |
|---|---|---|
| SEL-01 | **Seleção abre detalhe.** Lista com busca e filtro. Ao tocar uma linha, o detalhe abre ao lado no computador e em tela cheia no celular, e os itens filhos aparecem já listados e selecionáveis. Exemplos: fazenda → talhões (mapa e tabela sincronizados) → talhão; cultura → cultivares → operações; máquina → implementos; produto → embalagens e locais | Hierarquia visível sem trocar de tela (pedido de 09/10 para os Cadastros) |
| SEL-02 | **Endereço e retorno.** A seleção vai para o endereço (`#reg=`, `#faz=`, `#tal=`…). Voltar preserva filtro, posição e foco. Registro indisponível (inexistente ou fora da permissão) abre a lista com aviso visível e acessível e uma opção de recuperação; nunca seleciona outro registro em silêncio, não revela se um registro fora da permissão existe e não se apresenta como navegação bem-sucedida. Teclado: setas, Enter e Esc | Voltar e compartilhar sem refazer o caminho |
| ETP-01 | **Etapa futura neutra.** Quando só falta o passo anterior ou não há nada a fazer, a etapa não fica vermelha. Vermelho só para impedimento real, com motivo e quem resolve (DS-17, DS-31) | Vermelho continua significando "algo impede" |
| VIS-01 | **Separador** abaixo do cabeçalho (título e ação) e entre blocos pertinentes, pelo componente comum | Organiza a leitura em blocos |
| VIS-02 | **Hover verde-claro** (não cinza) em linhas, opções, abas e botões secundários, só onde há ponteiro; contraste AA | Coerência com a cor de ação |
| VIS-03 | **Retorno visual de mudança.** Ao abrir uma tela, avançar de etapa, gravar, aprovar ou mover um cartão: realce breve no que mudou, barra fina durante a navegação e anúncio para leitor de tela. Sem animação com `prefers-reduced-motion`. Nunca atrasa a ação | A pessoa vê na hora que a ação valeu e onde está |
| VIS-04 | **Dica (tooltip) só como complemento.** O motivo de uma ação bloqueada (causa, quem resolve e próximo passo) continua **visível em texto** junto ao controle ou no "Próximo passo", sem depender de ponteiro ou foco (DS-06, 74.5.0); a dica pode detalhar, nunca substituir. Use dica em selo de estado (o que significa e o próximo passo), siglas, unidades, valores calculados (fórmula e fonte) e ícones sem texto. Abre no hover e no foco, fecha com Esc, é lida por leitor de tela (`aria-describedby`) e nunca repete o rótulo visível | Quem usa toque ou não acha o controle desabilitado continua sabendo o que falta |
# Design system

**Situação:** o design system é o **capítulo 74** do PRD (v3.10, vigente na v3.11). Ainda faltam neste repositório:
- `tokens.json`: fonte única dos tokens, para gerar variáveis CSS e o tema do código;
- a página de espécime visual, gerada dos mesmos tokens;
- a tabela de contraste medida (WCAG 2.2 AA).

**Referência até lá:**
- os princípios do PRD 4.2 e 4.3 (padrões visuais e de interação) e 20.2;
- os tokens em uso no protótipo validado. O gerador do protótipo não faz parte deste repositório.

**Regras que já valem:**
- cor sempre acompanhada de texto;
- verde para ação principal e condição favorável;
- uma ação primária por tela;
- alvo de toque de 44 × 44 px;
- WCAG 2.2 AA nos fluxos críticos (NFR-09).
