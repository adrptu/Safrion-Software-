# VISOES-2 · versão enxuta

- **Pedido do proprietário (14/10/2026):** "Melhore isso juntamente com Codex para termos UX/UI perfeito para o usuário. Extremamente organizado e intuitivo. Essencialista e minimalista." O texto original está em [`pedido-1410.md`](pedido-1410.md).
- **Autor desta revisão:** Claude. **Revisor:** Codex, pelo lado do produto.
- **Estado:** especificado. Nada daqui está implementado ainda.
- **Base:** `visoes.py`, o desenho da VISOES-1 (`docs/integracao/VISOES/DESENHO.md`) e as regras da casa (`docs/claude/skills/ux-essencial`, `minimalismo-essencial` e `tabelas-interativas`).

## 1. O que o pedido acerta, e fica

1. **Toda listagem responde a perguntas fixas, sempre na mesma ordem e com o mesmo ícone:** o quê, quem, quando, onde. O usuário aprende uma vez e reconhece em toda tela.
2. **A tela só marca as colunas; o motor deduz o resto.** Acaba o trabalho tela a tela e a divergência entre telas.
3. **Lista e Tabela agrupada viram uma só, a Tabela.** Isso resolve o C6/VIS-D30, que estava pendente.
4. **Agrupar e descer:**
   - a seta expande o grupo no lugar;
   - o nome do grupo desce um nível e vira filtro;
   - a trilha mostra onde se está e vai no endereço;
   - Esc sobe um nível;
   - os totais fecham em cada nível.
5. **Situação sempre à vista:** chips com ícone e contagem.
6. **Padrão visual:**
   - texto só onde muda decisão;
   - ícone com função;
   - cor de estado sempre com ícone;
   - números à direita, em algarismos tabulares;
   - menos moldura.
   - O exemplo "hoje × passa a ser" das Atividades do plano fica inteiro.
7. **Celular:** um nível por vez, com a trilha. Agenda e carga viram cartões por dia ou por recurso.
8. **Correções de navegação:** os seletores próprios deixam de existir (COLH, AG-01, CD-01, BEN, MA) e as telas sem link de chegada são corrigidas.

## 2. O que muda, e por quê

Cada linha corta um controle, um conceito ou uma tela que não muda decisão (minimalismo-essencial §1).

| Pedido | Passa a ser | Motivo |
|---|---|---|
| Cinco focos, um deles **Quanto** | **Quatro dimensões** (O quê, Quem, Quando, Onde) e **uma medida** | Não se agrupa por R$. Quanto é o que se soma dentro do grupo. "Ver por Quanto" vira **ordenar pelo maior valor**: grupos e linhas do maior para o menor, o Pareto do gestor. A troca R$ ↔ R$/ha ↔ quantidade fica no cabeçalho da coluna da medida. A composição do custo (componente › natureza › documento) é a dimensão O quê das telas de custo. |
| Rótulo "Foco", com o nome da pergunta | Botão **"Agrupar por"**, com o **ícone da pergunta** e o **nome real da coluna**. Exemplos: Talhão, Responsável, Semana, Atividade. | Palavra do usuário, não do modelo (ux-essencial). O ícone mantém a pergunta reconhecível de tela em tela. |
| Barra com busca, filtros, foco, segundo foco, nível de partida, Ver como, ordenação e as trocas de DAP e de unidade | **Barra com 3 controles: Busca · Agrupar por · Ver como.** Filtro e ordenação no cabeçalho da coluna, como diz o tabelas-interativas. Troca de DAP/data e de unidade no menu da própria coluna. Nível de partida no próprio menu do Agrupar, só quando há mais de uma fazenda no recorte. | Oito controles numa barra competem pela atenção. A pessoa começa sempre pela pergunta. |
| Segundo foco opcional | Sai da barra. Só a Matriz tem dois eixos, e o segundo eixo é escolhido nela mesma. | Cruzamento é forma, não estado da barra. |
| 12 visões genéricas | **7 visões compartilhadas:** Tabela, Cartões, Kanban, Calendário, Carga, Linha do tempo e Mapa. Matriz só como visão na AG-01 (talhão × alvo). | Gráfico e Matriz de gestão vão para os **Painéis por módulo** (pedido de 14/10), onde está a decisão gerencial. Feed é Tabela agrupada por dia, com a hora na primeira coluna. Comparar é a forma própria de Propostas, Versões e Planos, sem seletor. Galeria espera foto real: o protótipo só conta fotos (DESENHO 1.4). |
| Até 4 formas por foco | Até 4 formas **por listagem**, sempre com a Tabela. **Com uma forma só, não há seletor.** | É a regra da VISOES-1. Seletor com uma opção é ruído. |
| O foco segue para a próxima tela | **Não segue.** A tela abre como a pessoa a deixou (preferência perfil × listagem). Na primeira vez, abre pelo padrão do perfil. Entre telas segue só o recorte: Fazenda, Safra e Talhão, que já existem. | Estado que chega de outra tela é causa invisível: a pessoa volta e a tela está agrupada diferente sem saber por quê. |
| Agrupamento só na Tabela e nos Cartões | **O agrupamento vale em toda visão que tem onde pôr grupo:** linhas na Tabela, seções nos Cartões, raias no Kanban. Calendário, Carga, Linha do tempo e Mapa têm eixo próprio e não agrupam, mas **respeitam a trilha**, que é um filtro. | Uma regra só, previsível em todas as visões. |
| Excluir com desfazer de 5 s em vez de confirmação | Desfazer **só para remover sem efeito**: rascunho, item do plano, insumo da atividade. Para o que tem efeito (reserva, movimento, O.S. liberada), não existe excluir: existe o comando próprio, cancelar com motivo. | Fato registrado não se desfaz calado (AGENTS §4, servidor como autoridade). |
| Menu ⋯ com editar e excluir em toda linha | ⋯ **só com 2 ou mais ações secundárias na linha.** Com uma ação só, ela fica visível como ícone com dica. Editar é clicar na linha. | Esconder a única ação custa um clique a mais. |
| Ícones Material Symbols Rounded | **Fica o conjunto atual, Lucide** (ISC, já embutido nas 155 páginas). Adota-se a **tabela semântica do pedido**: o mesmo conceito tem o mesmo ícone em toda tela. | Trocar de conjunto não muda decisão e mexe em todas as telas. Um conjunto só. |
| Esqueleto, tema escuro, transições | No protótipo: transição de 150 a 200 ms, respeitando "reduzir movimento". Esqueleto e tema escuro vão para o software real, com os tokens do cap. 74. | O protótipo não tem carregamento. O tema escuro depende do `tokens.json`, que ainda não está no repositório. |
| Crawler por papel em todos os focos, níveis e formas | **Invariantes gerados das marcas**, rodados com o perfil de todos os acessos e com um perfil restrito | Papel muda ações, não visões. A combinatória por papel só repete o mesmo teste. |
| DAP, DAE e data em todo Quando | Só onde a coluna é DAP e a conversão vale para todas as linhas: cultivo com plantio. No plano (modelo, sem plantio), só DAP. | Data inventada sem âncora é proibida (PRD 39.4). |
| Telas sem chegada, famílias duplicadas, menu de Finanças | **Fora desta frente**, numa frente de navegação própria. MB-08 primeiro: o irrigante não chega à tarefa dele. | É navegação, não visão. Misturar atrasa as duas. |

## 3. Especificação

### 3.1 Marcas nas colunas (fonte única)

Cada coluna de `GRIDS` recebe uma destas marcas:

**Dimensão**, `d`:
- valores: `oque`, `quem`, `quando` ou `onde`;
- pode ter níveis, `niveis`, do geral ao detalhe:
  - Fazenda › Talhão › Parcela;
  - Grupo › Insumo › Lote;
  - Equipe › Pessoa;
  - Classe › Máquina;
  - Componente › Natureza › Documento.
- No Quando, os níveis Safra › Mês › Semana › Dia **saem da data**, sem coluna nova.

**Medida**, `m`:
- unidade: `R$`, `R$/ha`, `ha`, `L`, `kg`, `sc` ou `h`;
- agregação: `soma`, `razao` (com numerador e denominador) ou `nenhuma`;
- em razão, nunca média simples (tabelas-interativas §3);
- quantidade em unidades diferentes **não soma**: o grupo mostra "—" e a dica "unidades diferentes". O dano evitado é um total falso de kg com L (ENG-013; DESENHO 1.3).

**Situação**, `s`:
- estados com ícone e cor;
- `fluxo` com fases fixas (Kanban).

**Tipo**:
- `data`;
- `intervalo` (início e fim);
- `dap`;
- `geometria` (do cadastro, nunca inventada).

O motor deduz três coisas:
- **Agrupar por:** as dimensões com 2 ou mais valores no recorte, na ordem O quê, Quem, Quando, Onde;
- **visões válidas:** pela tabela `EXIGE`, que já está em `visoes.py`, acrescida de Cartões (`filhos`);
- **Abre em:** o padrão da listagem e o do perfil (3.6).

A tabela "Telas e focos" do pedido continua sendo a fonte das marcas. A coluna Quanto vira medida.

### 3.2 Barra única (Tabela e Cartões)

`[Busca] [ícone Agrupar por: Talhão ▾] [Ver como: ícones, só com 2 ou mais formas]`, com `[Expandir tudo]` à direita só quando há grupo.

- **Abaixo da barra:** os chips de Situação, com ícone e contagem, e só quando a listagem tem estados. Os chips filtram; não agrupam.
- **Menu do Agrupar:**
  - "Sem agrupar";
  - as dimensões, cada uma com o ícone da pergunta e o nome da coluna;
  - o nível de partida, só quando há escolha. Exemplo: Fazenda ou Talhão, se o recorte tem mais de uma fazenda.
- **Ordenar** fica no cabeçalho.
- **"Maior valor primeiro"** é o atalho do menu da medida: ordena grupos e linhas pelo subtotal.

### 3.3 Agrupar e descer

| Gesto | Efeito |
|---|---|
| ▸ na linha do grupo | Expande ou recolhe no lugar. O nível não muda. |
| Nome do grupo, raia, mês do Calendário, polígono do Mapa, célula da Matriz | Desce: filtra pelo valor e passa ao próximo nível. A forma se mantém. Na Matriz, desce nos dois eixos. |
| Trilha ("Todas › Lagoa Grande › T4") | Volta a qualquer nível. Fica no endereço. |
| Esc | Sobe um nível. Antes disso, fecha o painel aberto. |
| Linha no último nível | Abre a ficha de sempre, com a **origem**: plano, recomendação, ocorrência ou alvo. |

**Invariante:** o total do nível de baixo é igual ao valor do grupo clicado em cima, para cada medida somável.

### 3.4 Visões compartilhadas

| Visão | Entra quando (`EXIGE`) | Não entra quando |
|---|---|---|
| Tabela | sempre; é o retorno de qualquer erro | — |
| Cartões | o item tem filhos a conferir (atividade › insumos) | não há filhos |
| Kanban | fluxo fixo com 3 ou mais fases | 1 ou 2 fases |
| Calendário | data única que decide a agenda | ordenar por data já resolve |
| Carga | recurso × dia ou hora, com disputa | não há disputa de recurso |
| Linha do tempo | início e fim, com sobreposição que importa | as durações não se sobrepõem |
| Mapa | geometria de cadastro em 3 ou mais locais, pelo componente único do IN-04 (DESENHO F3.0) | a camada do IN-04 já responde sem o recorte da lista |
| Matriz (só AG-01) | duas dimensões e uma medida comparável na mesma escala | um eixo com 1 ou 2 valores |

Regras gerais:
- toda visão lê o mesmo recorte e mostra os mesmos totais da Tabela;
- nenhuma visão grava dado;
- o clique abre a mesma ficha;
- os estados do §2.8 (vazio, filtro sem resultado, erro, sem permissão) valem em todas.

### 3.5 Padrão visual: rubrica conferida no teste

1. **Texto.**
   - Nenhuma frase fixa de instrução na tela: ela vai para o ⓘ da seção, como na TEXTO-2.
   - Nada repete o que a seção, o chip ou o ícone já dizem.
2. **Ícones.**
   - O tipo de operação e o estado têm ícone antes do título, o mesmo no chip, na linha, no cartão e no calendário.
   - Ícone sozinho só em ação óbvia (busca, ⋯), e sempre com dica.
3. **Cor.**
   - Verde da marca só na ação principal e na seleção.
   - Vermelho, âmbar e verde só para estado, sempre com ícone.
4. **Números.**
   - À direita, com `font-variant-numeric: tabular-nums` e unidade curta.
   - Total e subtotal sempre visíveis.
5. **Moldura.**
   - Divisória ou sombra, nunca as duas.
   - Espaço em múltiplos de 8.
   - Título sem sublinhado; a linha ou o cartão inteiro abre o registro.
6. **Ações.**
   - Uma principal por tela, no lugar do BOT-01.
   - Removível sem efeito: desfazer por 5 s.
   - Com efeito: o comando próprio.
7. **Movimento.** De 150 a 200 ms ao expandir, agrupar e trocar de visão, com `prefers-reduced-motion`.
8. **Toque e acessibilidade.**
   - Alvo de 44 px, foco visível, contraste AA.
   - A Tabela é o equivalente acessível de toda visão gráfica.

O piloto visual são as Atividades do plano, exatamente como na tabela "hoje × passa a ser" do pedido. Muda um ponto só: a lixeira vira ícone visível com desfazer, porque é a única ação secundária da linha (editar é clicar na atividade).

### 3.6 Estado, endereço e padrão por perfil

- **Endereço:**
  - `?ag=onde&trilha=LG/T4&view=tabela`;
  - `?view=lista` e `?view=agrupada` passam a abrir a Tabela;
  - precedência, como hoje: endereço › preferência › padrão.
- **Preferência por perfil × listagem:** agrupamento, trilha, visão, grupos recolhidos e rolagem. A chave `g2visaoChave` já existe.
- **Padrão na primeira vez:**
  - PCP: agrupar por Quem;
  - agrônomo: por O quê;
  - encarregado: por Onde;
  - gestor: por O quê, com o maior valor primeiro.

### 3.7 Celular (até 640 px)

- Um nível por vez, com a trilha no topo.
- Ver como mostra 3 formas, e o resto vai para "Mais".
- Mapa e Matriz rolam por dentro, com a legenda fixa.
- Calendário, Carga e Linha do tempo viram Cartões por dia ou por recurso.

## 4. O que cada listagem do menu recebe além da Tabela

Toda listagem do menu ganha a barra única, o Agrupar por (das marcas), o descer com trilha e a rubrica visual. A tabela abaixo mostra só as **formas a mais**. O que não aparece nela fica só com Tabela, sem seletor.

| Listagem | Formas além da Tabela | Abre em | Observação |
|---|---|---|---|
| OS · Ordens de serviço | Kanban (raias pelo agrupamento), Calendário, Carga | pelo perfil | As 5 visões de hoje viram 4: Lista e Agrupada se fundem. |
| PA · Atividades do plano | Cartões (forma própria, sem seletor) | Cartões, agrupados por Quando (DAP) | Piloto visual. |
| PA · Biblioteca de planos | — | Tabela | Os planos são poucos. A versão compara na forma própria. |
| SAF · Talhões e cultivos | Linha do tempo (ocupação) | Linha do tempo | A DESENHO F4. |
| SAF · Capacidade | (Matriz recurso × mês, forma própria) | — | Já existe como grade própria. |
| AG-01 · Vistorias | Matriz talhão × alvo, depois Mapa (F3.0) | Matriz | O "Agrupar vistorias por" vira o Agrupar por. |
| COLH · Previsão | — | Tabela, agrupada por Onde | "Por talhão / Por semana" vira Agrupar por Onde ou Quando. |
| BEN · Ordens de beneficiamento | Kanban | Kanban | O seletor próprio migra. |
| MA · Ordens | Kanban | Tabela | A Carga das máquinas é a da O.S., que já traz os blocos de manutenção (uma fonte só, `alocacao.py`). |
| MA (as 4 listagens) | abas: Sem ordem, Ordens, Ativos, Planos | — | O seletor "Visão" vira abas. |
| CD-01 · Talhões | Mapa (F3a) | Tabela | O `cdv` e o `cd_mtog` saem. |
| VEN · Contratos e pedidos | Kanban, se o fluxo tiver 3 ou mais fases | Tabela | |
| EST · Movimentos e CF-04 · Auditoria | — | Tabela agrupada por dia, com a hora na primeira coluna | É o "Feed", sem visão nova. |
| GE-03 · Custos | — | Tabela agrupada Componente › Natureza › Documento, maior valor primeiro | O Gráfico vai para o painel. |
| CMP · Propostas, PA · Versões, CF-05 · Planos | (Comparar, forma própria) | — | Só as linhas que diferem; melhor valor marcado. |
| CARGA · Cargas e recebimento | — | Tabela com chips | 2 estados não sustentam Kanban (regra do 3.4). |

Os gráficos e as matrizes de gestão do pedido entram nos **Painéis por módulo** (PAINEL-02), onde já está a decisão:
- PAGR: colheita prevista × recebida;
- GE-02: cronograma de caixa;
- IR-04: desempenho;
- IC: preço e melhor mês;
- PCOM: oferta livre;
- IV: preço × mercado.

## 5. Fatias e aceite

Uma fatia por vez (AGENTS §3.1). Cada uma é útil sozinha.

| Fatia | Entrega | Aceite (executado, por listagem) |
|---|---|---|
| **V2-1 · Motor e O.S.** | Marcas em `g_os`; barra única; Tabela única; descer com trilha, Esc e endereço; chips de Situação; raias no Kanban; preferência e padrão por perfil; rubrica na O.S. | (a) Σ grupos = total da Tabela, para cada dimensão e medida somável; unidades diferentes não somam. (b) Descer e voltar preserva os totais; o link com trilha abre no mesmo ponto. (c) Cada visão abre para cada agrupamento válido, e o clique abre a O.S. certa. (d) Trocar de agrupamento, visão ou tela e voltar preserva o estado. (e) `?view=lista` e `?view=agrupada` abrem a Tabela. (f) Nenhum seletor mostra "Lista" ou "Tabela agrupada". Medição (§3.3): cliques para chegar a "O.S. atrasadas do T4 por responsável", antes e depois. |
| **V2-2 · Atividades do plano e SAF** | Cartões compartilhado; o exemplo hoje × passa a ser; Linha do tempo da ocupação | (a)–(f) na PA e na SAF; rubrica visual da PA com captura antes e depois a 1440 e 390 px |
| **V2-3 · Todas as listagens do menu** | Marcas em todas as grades do menu; migração dos seletores próprios (COLH, AG-01, CD-01, BEN, MA em abas, AG-07 sem opções sai) | Invariantes (a)–(f) gerados das marcas para cada listagem; `paginas_scan` sem erro |
| **V2-4 · Formas onde se justificam** | Matriz da AG-01; Mapa (depois do mapa único, F3.0); Kanban de BEN, MA e VEN | (c) e (a) nas formas novas; Mapa só com geometria de cadastro |

O registro da matriz de aceite vai para o PRD na revisão final do conjunto (AGENTS §3.6). Até lá, fica nesta pasta.

## 6. Fora desta frente, com condição de volta

| Item | Volta quando |
|---|---|
| Tema escuro | `tokens.json` do cap. 74 no repositório |
| Troca para Material Symbols | o proprietário pedir a troca de conjunto, sabendo que mexe nas 155 páginas |
| Galeria | houver foto real como informação principal |
| Gráfico e Matriz como visão de listagem | um teste de uso mostrar que o Painel do módulo não responde |
| Foco que segue de uma tela para outra | um teste de uso mostrar a necessidade, sem o efeito surpresa |
| Telas sem chegada, famílias duplicadas, menu de Finanças | frente NAV própria, com MB-08 primeiro |
| Esqueleto de carregamento | software real |

## 7. Para o parecer do Codex (revisão por contraexemplo)

Peço que tente quebrar, como a persona faria, estas decisões:
- Quanto como medida e ordenação, não como agrupamento;
- o rótulo "Agrupar por" com o nome real da coluna;
- 7 visões compartilhadas, com Matriz só na AG-01;
- o agrupamento não segue de uma tela para outra;
- a Manutenção sem Carga própria;
- CARGA sem Kanban;
- Lucide mantido.

Cada achado é aceito, ajustado ou recusado com fundamento, nesta pasta.
