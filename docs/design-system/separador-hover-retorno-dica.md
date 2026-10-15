# Separador, hover verde, retorno visual e dica

Quatro padrões do design system do protótipo, pedidos pelo proprietário (Adrianus) e entregues pelo estilo e pelos componentes comuns do gerador (`engine.py`, `ui37.py`, `g2lib.js`). Nenhum deles é desenhado tela a tela.

Proposta para o capítulo 74 do PRD, que está em revisão. Os tokens abaixo são a fonte em uso no protótipo (`engine.DS_SEP`, `engine.DS_HOVER`, `engine.DS_RETORNO`, `engine.DS_DICA`). Os quatro padrões são os VIS-01 a VIS-04 dos padrões do proprietário de 09/10/2026 (`docs/design-system/README.md` do PR #50, ainda fora desta branch).

| Padrão | ID | Pedido | Onde vive | Teste |
|---|---|---|---|---|
| Separador | VIS-01 | 05/10/2026 | `engine.SEP_CSS` (dentro de `G2_CSS`), header da casca (`ui37.shell37`, `engine.mobile`), `.g2-cab` | `ds_test.py` A |
| Hover verde | VIS-02 | 05/10/2026 | `engine.INTERACAO_CSS` (`DS_HOVER`) | `ds_test.py` B, `ds_unit.js` 3 |
| Retorno visual | VIS-03 | 09/10/2026 | `g2lib.js` (`g2flash`, `g2vivo`, `g2carga`, `g2montou`, `g2mudou`) chamado pelo motor (`engine.ENGINE_JS2`) | `ds_test.py` C e E |
| Dica | VIS-04 | 09/10/2026 | `g2lib.js` (`g2dica`, `G2_DICAS`), `engine.GLOSSARIO`, `engine.acao_motivo` | `ds_test.py` D, E e G, `ds_unit.js` 1 e 2 |

## 1. Separador

**Pedido:** «tem telas sem essas linhas separadoras visuais que ficam abaixo do título e do botão no topo à direita como no caso nova safra. [...] acho melhor ter para organizar a visão e a mente em blocos. Faça em todas telas e padronize no design system.»

**Revisão de 15/10/2026** (proprietário: «retire em todas telas onde tem excesso de linhas separadoras visuais, deixe somente as que geram efetiva organização visual e intuitividade»). Fica a linha que separa duas zonas que nada mais separa; sai a que repete um espaço, um título, um fundo ou outra borda.

**Regra.** Ficam:

1. **Cabeçalho da página** (título e ação do topo à direita): a borda inferior do `header` da casca, em todas as telas. O índice e a ficha impressa, que não usam a casca, usam `.g2-cab`.
2. **Painel lateral** (`aside[role=dialog]`): abaixo do título e do × do topo à direita (formulário «Nova safra»).
3. **Linhas da própria tabela**: cabeçalho, entre linhas e a linha do total.
4. **Linha de título do bloco** (`section` com título e ação à direita), recuada 12 px dos lados, **só quando logo abaixo vem conteúdo solto** (texto, formulário, botões, lista ou ficha sem moldura).

Saem, pelo componente comum (`engine.SEP_CSS`, `engine.section`, `engine.grid`, `ui37`) e pelas fichas e estados vazios das áreas:

| | Linha que sai | No lugar |
|---|---|---|
| a | colada (≤ 16 px) em outra linha, borda ou mudança de fundo (faixa de etapas, pé fixo do app, barra do Mapa, 1ª linha de lista que abre uma caixa) | fundo; sombra na barra presa |
| b | do título, quando abaixo já vem tabela, caixa, cartões, faixa com fundo, gráfico/mapa ou a barra de modos de visão | o próprio conteúdo |
| c | entre a barra da tabela (busca, chips, Colunas, Agrupar por) e o cabeçalho, que já tem fundo | fundo do cabeçalho |
| d | borda da caixa de dentro (tabela em bloco com borda; memória de cálculo, indicadores, dias da agenda) | espaço e fundo |
| e | entre pares rótulo × valor e entre itens de lista curta (2 a 3 itens, contados na hora) | espaço |
| f | tracejada decorativa (estados vazios, aviso, estado da visão) | fundo `#F4F6F3` |

Continuam, por proteger algo concreto: borda colorida de estado (aviso, etapa atual, carga parcial), selos e campos, cartões clicáveis, a tracejada que separa a lista do «Incluir produto», a linha do pé fixo de ações do painel quando o fundo é o mesmo e a ficha impressa.

| Token | Valor |
|---|---|
| cor | `#E4E9E5` (a mesma linha de tabelas e cartões) |
| recuo no bloco | 12 px de cada lado |
| espaço depois da linha | 10 px no bloco, 12 px no painel, 14 px em `.g2-cab` |
| espaço onde a linha saiu | 10 a 14 px (o espaçamento do bloco; o título do `engine.section` perde o respiro de baixo) |

**Amostra** (o bloco não precisa de nada além da estrutura comum):

```html
<section>                                  <!-- bloco -->
  <div>                                    <!-- linha de título: a linha vem do CSS comum, só com conteúdo solto abaixo -->
    <div><h3>Crédito solicitado pelo caso RC-12</h3></div>
  </div>
  <div>… pares rótulo × valor …</div>      <!-- com <div class="g2caixa"> aqui, a linha não é traçada -->
</section>
<header class="g2-cab">…</header>          <!-- tela fora da casca -->
```

![Separador abaixo do título do bloco com conteúdo solto (GE-05)](amostras/separador-bloco.png)

## 2. Hover verde

**Pedido:** «Padronize o hover verdinho em vez do cinza.»

**Regra.** O realce passageiro do ponteiro é o verde-claro do sistema, igual ao do `.g2card`, e nunca cinza. Só vale onde há ponteiro com hover (`@media (hover:hover)`); no toque nada fica «grudado». O menu lateral escuro mantém a regra própria (clareia). Cada família de controle tem um hover:

| Família | Exemplos | Hover |
|---|---|---|
| Claro | secundário, opção de visão, aba, item de lista, chip, cartão clicável, link com cara de botão | camada `rgba(30,122,76,.07)` sobre o fundo (dá `#EFF6F2` no branco) e borda neutra `#E4E9E5` → `#9DBFAA` |
| Linha de tabela | `.g2ed`, linhas do Cadastro | fundo `#F2F8F4`; linha de grupo `#E8F3EC` |
| Cheio | primária verde, botão escuro, destrutivo cheio | só escurece (`brightness(.92)`); sem camada clara sobre o texto branco |
| Destrutivo claro | texto vermelho | camada vermelha `rgba(180,35,24,.06)`: o hover não diz «seguro» num comando que apaga |

Pressionado: camada verde `.14` no claro e `brightness(.86)` no cheio.

**Contraste AA medido** (`ds_unit.js`): texto `#15201A`, apagado `#65736A`, ação `#1E7A4C` e amarelo `#8A5A00` sobre o hover passam de 4,5:1. Branco sobre a primária escurecida também passa.

A camada é `background-image`, porque o estilo inline dos componentes não define imagem de fundo. Por isso o matiz do estado continua visível (tonal, amarelo, vermelho) e nada muda de tamanho.

![Hover verde no botão secundário](amostras/hover-secundario.png)

## 3. Retorno visual de mudança

**Pedido:** «quando muda de tela e avança no processo não está dando aquele feedback ao usuário em tempo real como se fosse um flash de atualização e mudança de contexto.»

**Regra.** Uma só função de realce, `g2flash(el, msg)`. Ela é chamada só pelos pontos centrais do motor, nunca por tela:

| Quando | Ponto central | Realce | Anúncio (aria-live polite) |
|---|---|---|---|
| Abrir uma tela | `componentDidMount` → `g2montou` | título da tela (`h1`); a barra de carga termina; vindo de um link do protótipo, o foco vai ao título | `Tela: <título> · <estado>`; com o foco no título, só `<estado>` (o leitor de tela já lê o título) |
| Voltar ou avançar pelo navegador (a tela volta da memória, sem montar de novo) | `pageshow` com `persisted` no `g2lib` | a barra ligada no clique termina | — |
| Clicar num link de outra tela | ouvinte de clique do `g2lib` | barra fina no topo (`#g2-carga`) do clique até a tela nova | — |
| Avançar ou voltar etapa, trocar seção (SAF, Compras, Planos, Manutenção, Estoque) | `componentDidUpdate` → `g2mudou`, lendo a faixa de progresso | bloco do novo contexto (o mesmo cujo título o `g2etapa` foca); se o botão que trocou a etapa saiu da tela, o foco vai ao título desse bloco | `Etapa i de n: <nome>` ou `Seção: <nome>` |
| Gravar, aprovar, liberar, mover cartão (todo comando que mostra aviso) | `componentDidUpdate` → `g2mudou`, quando o aviso (`g2toast`) é novo | o que mudou: linha da tabela, cartão do Kanban, região rotulada, estado do cabeçalho; sem nada mais fino, o bloco | o próprio aviso |
| Clicar num botão indisponível | ouvinte do `g2lib` | o motivo em texto junto do botão (`acao_motivo`); a dica do botão abre com o porquê | `Indisponível: <motivo>` |

Para achar o que mudou, o motor compara uma foto da tela antes e depois, por chaves estáveis: `data-g2g` + `data-rid` nas linhas, o código do cartão e a coluna do Kanban, regiões rotuladas, o estado do cabeçalho e os blocos. Uma tela nova não precisa fazer nada. Uma tela pode marcar um elemento com `data-g2k="chave"` para ele entrar na comparação.

| Token | Valor |
|---|---|
| realce | `#EDF7F0` → `#F2F8F4` com anel `rgba(30,122,76,.38)`, 520 ms, `ease-out` |
| menos movimento | sem animação; realce estático `#EDF7F0` com anel `#1E7A4C` por 600 ms |
| barra de carga | 3 px, `#1E7A4C`, até 82 % durante a navegação; completa e some em 0,5 s |
| região viva | `#g2-vivo`, `aria-live="polite"`, `aria-atomic="true"`, visualmente oculta |

O realce nunca atrasa a ação nem esconde o resultado: o desenho novo já está na tela e o realce é uma camada passageira por cima. O aviso visível (`role="status"`) fica com `aria-live="off"`, para que o leitor de tela ouça a mensagem uma vez, pela região viva. Duas frases no mesmo instante (o resultado e a recusa do segundo clique) saem juntas.

![Realce estático (menos movimento) no bloco da etapa nova](amostras/realce-etapa.png)

## 4. Dica (tooltip)

**Pedido:** «coloque tooltip onde for necessária para melhorar feedback ao usuário.»

**Regra.** Um componente comum, `g2dica`, com um só elemento `role="tooltip"` (`#g2-dica`):

- **Abre** com o ponteiro parado sobre o gatilho (300 ms), no foco de teclado (na hora), com toque longo (500 ms) ou ao tocar no ícone ⓘ (`.g2dica-i`).
- **Fecha** com Esc, ao tirar o ponteiro do gatilho e da dica, ao perder o foco ou ao tocar fora.
- **Leitor de tela:** enquanto a dica está aberta, o gatilho ganha `aria-describedby="g2-dica"`. A dica não repete o nome acessível.
- **Não depende do `title`**, que não aparece no teclado nem no toque. Se a tela já tinha `title`, ele sai de cima durante o hover e volta depois. O `title` igual ao rótulo visível (item do menu aberto) também sai enquanto o ponteiro está em cima, para o navegador não mostrar a dica nativa repetida; com o menu recolhido ele é a dica do item.
- **Selo dentro de linha ou cartão:** o selo não recebe foco. Com foco de teclado na linha da tabela ou no cartão do Kanban, a dica é a do selo mais grave de dentro dele (vermelho, depois amarelo), com o nome do selo à frente, e descreve a linha ou o cartão (`aria-describedby`). O clique do ponteiro na linha não abre a dica.

**Texto, nesta ordem:**

1. `data-dica="…"`: texto explícito. Vazio quer dizer sem dica.
2. `data-dica-de="<texto do selo>"` (ou a parte de célula `{k:'chip', …, de:1}`): significado e próximo passo do estado, buscados no dicionário único `G2_DICAS`.
3. `title` que acrescenta algo ao rótulo visível.
4. Nome do comando, em ícone sem texto.

Nada de dica que repita o rótulo visível.

**Onde se aplica.** Só onde ajuda a decidir ou entender:

| Caso | Como | Onde está hoje |
|---|---|---|
| Botão indisponível ou ação recusada | `engine.acao_motivo(botão, dis, motivo)`: o botão com `aria-disabled="true"` + `data-dica` e, só enquanto indisponível, o **motivo em texto visível** logo abaixo (`.g2motivo`, texto secundário `#65736A`, 12,5 px). O motivo não depende de ponteiro, foco ou dica (PRD DS-06 e 74.5.0; VIS-04): a dica complementa junto do ponteiro, do foco e do toque longo. O botão continua focável; o `g2lib` recusa o clique, realça o motivo e anuncia `Indisponível: …`. O comando também confere de novo. | CF-05 (Pedir proposta empresarial), BO-02 (Conciliar pagamentos) |
| Selo e chip de estado | `data-dica-de` no selo ou `{k:'chip', …, de:1}` na célula da tabela. O dicionário só vale onde a tela pede, porque o mesmo texto noutro contexto pode significar outra coisa. | O.S.: 5 fases do Kanban (título da coluna, cartão, painel e lista) e selos de bloqueio (Falta insumo, Fora do registro, Total 0, Sobras a receber, Aguardando sinal do app, Apontamento em conferência, Insumo esgotado). A dica de «A liberar» já diz as exceções da aprovação: irrigação só com água, manutenção e beneficiamento liberam pelo responsável próprio. O selo do bloqueio do encerramento em conferência (Carga a pesar, Sobras a receber, Aguardando sinal do app, Apontamento em conferência) leva o texto do próprio bloqueio, o mesmo do painel e do comando (`osSeloDica` ← `osEncBloq`), com quem resolve. O dicionário não cita caminho de menu. |
| Sigla e unidade | `engine.GLOSSARIO` vira a dica do cabeçalho da coluna, quando a coluna não traz ajuda própria: pelo rótulo (`_ajuda_auto`) ou, quando a sigla ou a unidade está na célula junto do valor («62,4 sc/ha», «DAP +20»), pelas células (`g2glossCol`, em ao menos 30 % das células com texto; código como COT-0031 não conta). R$/ha·mês e R$/ha·ano têm entrada própria | rótulo: NC (AG-01, AG-01det), R$/ha·mês (CF-05, BO-01), R$/ha·ano (BO-01), lâmina (IR-02, IR-03, IR-03det), ha/h e R$/h onde a coluna aparecer; célula: sc/ha (GE-02, GE-08, PL-01, COLH), DAP (AG-05, PL-02, PL-02det, PL-05), NC (AG-03, AG-03det, AG-06), ETo/ETc (IR-04, conforme o estado) |
| Valor calculado | fórmula curta da coluna calculada (`edit.calc`), com os rótulos | colunas calculadas da grade (ex.: PT-02det: Quantidade × Preço; CO-03: Peso bruto − Tara) |
| Ícone sem texto | nome do comando (só visual: o leitor de tela já lê o nome) | botão do menu, ×, setas, filtro da coluna, menu recolhido |
| Texto de ajuda que já existia | `title` que acrescenta ao rótulo vira dica acessível | em todas as telas, sem marcação nova |

| Token | Valor |
|---|---|
| fundo / texto | `#15201A` / `#FFFFFF` (16,7:1) |
| largura máxima | 320 px (cabe em 390 px com 8 px de margem) |
| raio, fonte | 9 px; Manrope 12,5 px 600 |
| atraso | 300 ms no hover, 0 ms no foco, 500 ms no toque longo |
| ícone ⓘ (`.g2dica-i`) | 18 px desenhado; 44 px de alvo com ponteiro grosso; disponível, ainda sem uso (no toque, o toque longo já abre a dica) |
| termo com dica (`span[data-dica]` no texto) | sublinhado pontilhado `#8A968E` e cursor de ajuda; disponível para as telas, ainda sem uso |

**Amostras:**

```html
<!-- botão indisponível com motivo (continua focável): engine.acao_motivo(botão, '{{dis}}', '{{motivo}}') -->
<span class="g2ind">
  <button aria-disabled="{{dis}}" data-dica="{{motivo}}">Conciliar pagamentos</button>
  <sc-if value="{{dis}}"><span class="g2motivo">{{motivo}}</span></sc-if>   <!-- motivo visível, sem depender da dica -->
</span>
<!-- selo de estado: o significado vem do dicionário único -->
<span data-dica-de="{{fase}}">{{fase}}</span>
<!-- sigla ou unidade no texto -->
<span data-dica="DAP: dias após o plantio, contados da data de plantio do talhão.">DAP 25</span>
<!-- caminho no celular -->
<button type="button" class="g2dica-i" aria-label="Mais informação" data-dica="…">i</button>
```

![Motivo visível e dica no botão indisponível](amostras/dica-indisponivel.png)

## Verificação

| Comando | O que confere |
|---|---|
| `node ds_unit.js` | regra do texto da dica, dicionário de estados e contraste AA |
| `python3 ds_unit_test.py` | CSS comum, ausência de hover cinza, pontos centrais do motor, glossário e fórmula, tokens e páginas geradas |
| `python3 ds_test.py` | navegador: separador nas páginas a 1440 e a 390 px (A2: linha do título só com conteúdo solto; A2b: sem linha dupla; A2c: sem linha antes de tabela, caixa, faixa, gráfico ou visões; A7: barra da tabela sem linha; A8: tabela dentro de caixa sem moldura), hover computado, realce e anúncio (tela, etapa, O.S. no Kanban, BO-02), barra de carga que termina (também ao voltar pelo navegador), foco no título da etapa nova, menos movimento, dica (hover, foco, Esc, aria-describedby, toque longo, linha e cartão focados, selo do bloqueio, sigla na célula, title redundante), motivo do indisponível visível em texto a 1440 e 390 px (G) e, com `DS_ANTES=<_render da base>`, capturas antes/depois a 1440 e 390 px de OS, PA, PM, AG-01, AG-01det e AG-07 em `_probe/ds/` (telas onde faltava a linha; o teste confere que antes ≠ depois) |
