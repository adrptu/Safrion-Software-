---
name: ux-essencial
description: Desenhe e revise interfaces e fluxos simples, acessíveis e rápidos, com contexto confiável e prevenção de erro. Use em telas, formulários, navegação, microcopy e retorno visual; preserve comandos e aprovações necessários.
---

# UX Essencial — o sistema como braço direito

**Norte:** o usuário chega, faz o que veio fazer no menor tempo possível, sem pensar, sem medo de errar, e sai com a sensação de que o sistema trabalhou por ele.

Teste de cada tela: **"Qual é a única coisa que a pessoa veio fazer aqui? Ela consegue fazer isso agora, com o mínimo de passos?"** Se não, redesenhe antes de codar.

---

## 1. Processo — pensar antes de desenhar
1. **Tarefa principal** de cada tela em uma frase ("Registrar pedido de um cliente conhecido").
2. **Fluxo mínimo**: conte passos/campos e reduza esforço sem perder compreensão, acessibilidade, segurança e controles do processo.
3. **O que o sistema pode fazer pelo usuário?** Reutilizar contexto confiável e sugerir valores editáveis; inferência não substitui aprovação nem inventa dose, quantidade, identidade ou responsável.
4. Construir com o design system vigente; usar os exemplos deste guia quando não houver um padrão do projeto.
5. Revisar com o **checklist final**. Em projeto real, medir com HEART (Felicidade, Engajamento, Adoção, Retenção, **Sucesso na tarefa**: taxa de conclusão, tempo, erros).

## 2. Leis da fricção zero
**Menos passos**
- **Uma ação primária por tela**, óbvia (botão preenchido ou FAB). Secundárias discretas (tonal/texto). Nunca duas primárias.
- A tarefa mais frequente fica **na primeira tela, sem navegar**. Nada de "home" decorativa: a home é o trabalho (lista, caixa de entrada, próximo passo).
- **Padrões inteligentes**: lembrar escolhas no contexto correto de pessoa, empresa, fazenda e safra; mostrar o valor e permitir revisão. Data atual e usuário logado não são necessariamente data da operação e executor.
- **Autocompletar com fonte**: cadastro autorizado → entidade/unidade/preço vigente; quantidade × preço → total calculado. Não inferir nome/identidade pelo e-mail. Seleções mostram dados suficientes para distinguir homônimos.
- **Criação rápida inline**: campo "Adicionar…" + Enter. Detalhes opcionais depois, na própria linha.
- **Edição inline** (clicar no valor e editar). Modal só para fluxo realmente separado.
- **Ações em massa** quando há tarefa real repetitiva, permissões verificadas e efeito claro.
- Autenticação antes de acessar dados protegidos; duração de sessão conforme risco e contexto. Não enfraquecer segurança para reduzir cliques.
- **Sem tour/onboarding de slides**: estado vazio ensina com uma ação ("Nenhum cliente ainda · Importar planilha · Adicionar cliente").

**Sem medo, sem burocracia**
- **Desfazer** para operações reversíveis de baixo risco. Ações irreversíveis ou de impacto material mostram consequência e confirmação apropriada. A IA respeita toda aprovação específica exigida pelo usuário/projeto.
- **Salvamento automático de rascunhos**, com estado verdadeiro. Confirmar recebimento, movimentar estoque, publicar, pagar ou executar uma ordem são comandos explícitos; não disparam ao sair de um campo.
- **Nunca perder o que foi digitado** (rascunho local, erro de rede não limpa o formulário, voltar mantém o estado).
- **Validação inline** ao sair do campo, com mensagem que diz **como corrigir** ("Use 11 dígitos: DDD + número"). Máscaras que aceitam colar em qualquer formato. Nunca bloquear o botão sem dizer o porquê.

**Formulários**
- Campos da mesma tarefa compartilham contexto e sequência natural de teclado/toque; autocomplete e cálculos dependentes atualizam no lugar, sem perda de foco. Não exigir salvar cada campo/seção para concluir uma única operação.
- Uma confirmação clara para a operação completa; itens interdependentes exigem atomicidade no servidor. Etapas separadas só quando representam estados, permissões ou operações reais, com continuidade visível. Ações em lote seguem a semântica do domínio; sucesso parcial identifica itens concluídos e pendentes.
- Uma coluna, ordem lógica da vida real, rótulos sempre visíveis (sem placeholder como rótulo).
- Só o essencial; o resto em "Mais opções" (divulgação progressiva).
- `type`, `inputmode` e `autocomplete` corretos. Enter seleciona sugestão aberta ou executa a ação previsível; nunca confirma transação por acidente.
- Datas com atalhos ("Hoje", "Amanhã", "+7 dias"); selects longos viram busca com autocompletar.

**Encontrar e agir rápido**
- Busca contextual acessível; busca global e paleta Ctrl/⌘+K quando reduzem esforço real. Atalhos complementam controles visíveis.
- **Atalhos de teclado** para as ações frequentes (N = novo, / = buscar, E = editar, Esc = fechar), exibidos nos tooltips e na paleta.
- **URL reflete o estado** (filtros, aba, item aberto): dá para compartilhar, recarregar e voltar sem perder nada.
- Navegação: **3 a 5 destinos principais**, profundidade máxima de 3 níveis, caminho sempre visível.
- **Organização das telas** segue a skill **`master-detail-ux`** (Menu → Listagem → Detalhe → Sub-detalhe; estado visível, próximo passo nomeado, uma ação primária por tela).
- **Tabelas** seguem a skill **`tabelas-interativas`** (filtro e ordenação no cabeçalho, agrupamento, drill-down).

**Notificações e mensagens**
- Só notifica o que exige ação, com a ação no próprio aviso.
- Erros: o que houve + o que fazer, em linguagem humana, sem códigos. Sucesso discreto (snackbar), nunca modal.

## Continuidade sem esforço — Wu wei

No Safrion, fluidez significa continuidade da tarefa, não movimento decorativo. O usuário deve entender onde está, o estado do trabalho e o próximo passo sem depender de explicação do agente.

- Herdar fazenda, safra, talhão e tarefa quando o contexto for confiável; não perguntar de novo nem trocar contexto silenciosamente.
- Preservar busca, filtros, rolagem, seleção, rascunho e foco no retorno; ao reabrir o app, recuperar o ponto de trabalho dentro da sessão e do escopo autorizados. Após salvar, atualizar no lugar e oferecer o próximo passo pertinente; não redirecionar nem executar uma nova ação sem intenção.
- Evitar saltos de layout, modais em sequência e recarregamentos que apagam o trabalho. Responder ao toque de imediato e mostrar junto do objeto processamento, pendência, conclusão real ou erro com o que fazer. Usar as palavras de estado do design system (Safrion: PRD 74.4.3), com texto e sinal visual, sem depender só de cor ou aviso temporário. Impedir repetição do comando em processamento sem bloquear trabalho independente; erro mantém os dados e uma saída clara. Salvo no aparelho não significa aceito pelo servidor.
- Autocomplete distingue entidades semelhantes, funciona com teclado/toque e informa ausência de resultado. Não exigir sintaxe técnica para pesquisar ou filtrar.
- No campo, priorizar a tarefa da persona, legibilidade sob sol, alvos acessíveis, pouca digitação e conexão intermitente. Testar no dispositivo e nas condições-alvo; desktop rápido não comprova fluidez no campo.
- Som e movimento são discretos e dispensáveis; respeitar preferências, redução de movimento e o vocabulário do design system. Não emitir som repetido em sincronização de fundo nem depender de áudio para comunicar sucesso/erro.
- Antes do aceite, verificar uma jornada principal, retorno/correção e erro/recuperação por persona afetada. Usar automação para regressões e observação humana para entendimento. Medir tempo, sucesso, erros e esforço com contexto; não afirmar superioridade sem comparação.

Texto ambíguo que provoca erro, perda de contexto/rascunho, confirmação falsa de sucesso e caminho sem recuperação são defeitos de usabilidade, não mero polimento. Não retirar aprovações ou controles necessários para reduzir cliques; torná-los claros e proporcionais.

## 3. Resposta imediata (performance é UX)

| Momento | Regra |
|---|---|
| < 100 ms | Todo clique dá retorno visual imediato (camada de estado, item muda na hora) |
| Ações do usuário | Retorno visual imediato; UI otimista só quando o efeito é reversível e o estado pendente é claro. Não mostrar aceite do servidor antes do recibo |
| > 300 ms | **Skeleton** no formato do conteúdo (nunca spinner de tela cheia) |
| > 1 s | Progresso/estado explícito; > 10 s: roda em segundo plano e avisa quando terminar |
| Web Vitals (Google) | **LCP < 2,5 s · INP < 200 ms · CLS < 0,1** no percentil 75 |

Técnicas: pré-carregar a próxima tela provável, cache local (stale-while-revalidate), paginação/virtualização acima de ~200 itens, debounce 150–300 ms em buscas, imagens com dimensão definida (sem pulos de layout), carregar o que está acima da dobra primeiro, JS mínimo.

## 4. Visual — referência Material Design 3
O design system do projeto prevalece; os padrões M3 desta seção e as sugestões de plataforma abaixo valem somente na ausência dele. Não substituir tokens, tipografia ou componentes já definidos.

Exemplos: **[assets/m3.css](assets/m3.css)**, **[assets/m3-kit.js](assets/m3-kit.js)** e **[assets/exemplo.html](assets/exemplo.html)**. Inspecione acessibilidade, segurança e compatibilidade antes de reutilizar; não são componentes certificados nem substituem o design system vigente. Respeite a política de recursos externos do ambiente.

- **Cor por papéis** (`primary`, `on-primary`, `secondary-container`, `surface-container-*`, `on-surface-variant`, `outline`, `error`) — nunca hex solto no componente. Paleta padrão GM3 azul; para a marca, gerar o esquema no Material Theme Builder e trocar só os tokens. **Uma cor de destaque**; o resto são superfícies neutras. Claro e escuro sempre.
- **Tipografia**: escala M3 (Display, Headline, Title, Body, Label); Roboto Flex/Roboto; **sentence case** em títulos e botões ("Criar pedido", não "CRIAR PEDIDO" nem "Criar Pedido"). Máx. 2–3 tamanhos por tela.
- **Espaço**: grade de 4/8 px; respiro generoso separa grupos melhor que linhas e caixas.
- **Forma**: 4 (campos) · 8 (chips) · 12 (cards) · 16 (FAB) · 28 (diálogos) · pílula (botões).
- **Elevação** tonal (superfícies mais claras/escuras); sombra só em elementos flutuantes (FAB, menu, snackbar).
- **Movimento** funcional: 150–400 ms, easing *emphasized*; respeitar `prefers-reduced-motion`.
- **Ícones**: Material Symbols Rounded, sempre com rótulo ou tooltip; preenchido = ativo.
- **Componentes**: botão filled (primária) · tonal (secundária importante) · outlined/text (demais) · FAB (criar) · chips (filtros) · snackbar (retorno) · cards só quando agrupam algo clicável · diálogos raros.
- **Layout adaptativo (classes de janela M3)**: compacto < 600 px → barra de navegação inferior; médio 600–839 → navigation rail; expandido ≥ 840 → rail/drawer + painéis lista-detalhe lado a lado. Densidade maior em desktop para dados.

## 5. Minimalismo e essencialismo
A lei de corte completa (5 testes de essencialidade, orçamentos por tela, lista de proibidos, procedimento de corte e lista de cortes na entrega) está na skill **`minimalismo-essencial`** — aplicar sempre, ao fechar toda tela.
- Para cada elemento: **"se eu remover, alguém sente falta?"** Se não, remove.
- Nada decorativo: sem ilustrações de enfeite, gradientes, sombras gratuitas, textos de boas-vindas, ícones sem função.
- **Hierarquia clara**: o olho cai primeiro na informação/ação principal; secundário em `on-surface-variant`.
- **Divulgação progressiva**: avançado escondido até ser necessário, mas a um clique.
- **Microcopy**: frases curtas, voz ativa, palavras do usuário (não do banco de dados), botões com verbo + objeto, números formatados em pt-BR, datas relativas quando úteis ("há 5 min", "amanhã").

## 6. Acessibilidade e inclusão (WCAG 2.2 AA)
Contraste ≥ 4,5:1 (texto) e 3:1 (componentes) · foco sempre visível · tudo operável por teclado · alvos de toque conforme o design system e a plataforma; na ausência de padrão, ≥ 48×48 px · rótulos e `aria-*` corretos · não depender só de cor · `lang="pt-BR"` · zoom 200% sem quebrar.

## 7. Plataformas
Na ausência de design system do projeto, usar as referências abaixo, respeitando a stack e as convenções já adotadas.
- **Web (HTML/React/Vue/Next)**: `m3.css` + `m3-kit.js` ou tokens M3 mapeados no Tailwind/CSS do projeto. Evite `@material/web` (em modo de manutenção). MUI só se já existir no projeto, ajustando tema para M3.
- **Android**: Jetpack Compose Material 3. **Multiplataforma**: Flutter com `useMaterial3: true` e `ColorScheme.fromSeed`.
- **iOS**: manter os princípios deste guia, respeitando convenções nativas (navegação, gestos).

---

## Checklist final (toda entrega)
- [ ] Tarefa principal identificável em 1 segundo; **uma** ação primária
- [ ] Fluxo mínimo preserva significado, controles, unidades e aprovações
- [ ] Contexto e sugestões confiáveis, visíveis e revisáveis
- [ ] Rascunho preservado; autosave/desfazer só onde apropriados; comandos de negócio explícitos
- [ ] Validação inline com instrução de correção; tarefa com vários campos, correção de erro e retorno à lista verificados sem fragmentar a operação nem perder contexto
- [ ] Busca/atalhos pertinentes e estado de navegação preservado sem dados sensíveis na URL
- [ ] Retorno imediato; estado local/pendente/aceito correto; desempenho medido contra as metas do projeto
- [ ] Tokens do design system vigente e temas previstos pelo projeto
- [ ] Layout adaptativo compacto/médio/expandido
- [ ] Estados vazio, carregando, erro e sucesso desenhados
- [ ] Procedimento de corte de `minimalismo-essencial` executado; lista de cortes entregue; microcopy curta, com verbo, pt-BR
- [ ] Acessível (contraste, teclado, foco não encoberto, alvos conforme design system/plataforma)
- [ ] Telas de gestão/cadastro conforme `master-detail-ux` (listagem + detalhe, estado, próximo passo, ação primária única)
- [ ] Tabelas conforme `tabelas-interativas`
