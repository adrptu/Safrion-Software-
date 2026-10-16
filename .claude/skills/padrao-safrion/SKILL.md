---
name: padrao-safrion
description: Use em QUALQUER mudança de tela, componente, texto de interface ou pedido visual/UX do proprietário no Safrion — protótipo (tools/prototipo) ou software real (apps/web, packages/ui) —, inclusive correção pontual numa só tela ou print. Transforma o pedido em padrão do design system aplicado a todas as telas do mesmo tipo, com inventário, varredura automática e conferência visual antes de entregar.
---

# Padrão Safrion: do pedido ao padrão em todas as telas

Pedido do proprietário em 16/10/2026: "crie uma skill e metodologia de trabalho melhor, porque toda hora eu preciso ficar te corrigindo, sobre padrões e outros".

Esta skill é o **método**. As regras ficam numa fonte única, que não se copia para cá:
- `AGENTS.md` §4;
- PRD cap. 74;
- `docs/design-system/` (na branch do protótipo `claude/v44-v69-mapa`, a partir de 05e3f99: `padroes-1510.md`, `padroes-1610.md`, `diretrizes-ux.md` e os demais; os scripts `ds_inventario.py`, `galeria.py` (com a cobertura conferida: falta de família reprova) e `ds_1610_test.py` ficam em `tools/prototipo/v37/gen37/` no mesmo commit).

## Por que o proprietário precisava corrigir (causas medidas em 16/10)

1. **Pedido aplicado só na tela do print.**
   - A seta de abrir entrou só nas Atividades do plano.
   - O "Agrupar por" do Agrofit ficou diferente das demais telas.
   - O "Expandir tudo" mudava de lado conforme a tela.
2. **Camada de estilo por área sobre o componente comum.**
   - O `CADX_CSS` dos Cadastros é de 01/10, anterior ao DS de 09/10.
   - Ele trocava o cabeçalho da tabela, tirava a moldura e punha o "Cadastrar" na barra da tabela.
   - Toda melhoria do motor ficava anulada nos Cadastros.
3. **Tabelas e listas próprias fora do motor.**
   - Atividades do plano e Agrofit são exemplos.
   - Elas não ganhavam ordenação, filtro, seta e visual que o motor já tinha, e o inverso também acontecia.
4. **Entrega só com teste verde.** Teste não vê poluição visual nem desalinhamento; ninguém olhava as telas antes de publicar.
5. **Fala do proprietário que não virava padrão escrito com teste.** O mesmo desvio voltava na tela seguinte.

## Regra de ouro

Pedido do proprietário sobre uma tela vale para **todas as telas do mesmo tipo**, salvo quando ele diz "só nesta".
- "Nessa e nas demais" é o padrão implícito, mesmo quando não está escrito.
- Na dúvida sobre o alcance, aplique a todas as do tipo e diga quais foram.

## Passo a passo obrigatório

1. **Ler a fonte.** Leia o catálogo do DS (padrões, IDs e referência visual aprovada) antes de tocar em tela.
2. **Classificar o pedido:**
   - padrão novo;
   - padrão existente violado;
   - exceção (só com fala explícita do proprietário).
3. **Inventariar todas as ocorrências.** Escreva a lista na rodada antes de editar. Procure:
   - telas que usam o componente comum (`E.grid`, `bloco`, `mais`, `modos_html`…);
   - telas com peça própria equivalente (tabela, cartão, barra ou botão feitos à mão);
   - CSS de área que mira classe do motor (`.cadx .g2…`, `.pa-…` imitando `.g2…`). No protótipo, `tools/prototipo/v37/gen37/ds_inventario.py` (branch do protótipo) lista esses casos; no software real, `rg` pelas classes e pelos componentes de `packages/ui`.
4. **Corrigir na fonte comum:**
   - no protótipo, `engine.py` e `g2lib.js`;
   - no software real, `packages/ui`.
   - **Peça própria:** migre para o componente comum ou chame a mesma função do motor (cabeçalho, menu, seletor). Nunca copie o estilo.
   - **CSS de área sobre classe do motor** só com exceção registrada no catálogo, citando a fala do proprietário.
5. **Registrar o padrão no mesmo dia.** Use um ID no catálogo (`padroes-AAAAMMDD.md`) com:
   - a fala do proprietário;
   - o dano que evita;
   - a referência visual;
   - o teste que o protege.
6. **Prova automática:**
   - verificação no varredor das páginas (ex.: `ds_1510_test.py` parte C ou `ds_conformidade_test.py`);
   - contraprova: a versão antiga reprova;
   - a contagem de desvios por padrão não sobe.
7. **Prova visual:**
   - No protótipo, `tools/prototipo/v37/gen37/galeria.py` (branch do protótipo) fotografa, em 1440 px e 390 px, uma tela de cada família: lista do motor, árvore, agrupada, cadastro, Atividades do plano, Kanban, formulário, mapa e app de campo.
   - No software real, a mesma prova sai do teste de navegador (`pnpm run test:e2e`, Playwright): uma captura por família de tela, nas duas larguras, anexada ao PR.
   - Olhe **cada foto** e compare com a referência aprovada.
   - Desalinhamento, poluição, peça fora do lugar ou estilo diferente do vizinho é achado, e se corrige antes de publicar.
8. **Entregar:**
   - publique o artefato;
   - responda em até 6 linhas: o que mudou, em quantas telas, testes com números, foto conferida e o que ficou fora (com motivo).

## Antes de dizer "pronto"

- Onde mais isso aparece? Se o inventário saiu vazio, procure de outro jeito.
- Alguma tela anula a mudança com CSS próprio?
- As peças próprias (Atividades do plano, Agrofit, Mapa, app de campo, Cadastros) ganharam o mesmo?
- Olhei as fotos de 1440 px e 390 px?
- O padrão tem ID, teste e contraprova?
- Mudou o oráculo de algum teste? Então explique por quê na rodada e no relatório.

## Referências visuais aprovadas pelo proprietário

| Família | Referência | Data |
|---|---|---|
| Tabela | Planos agronômicos › Atividades do plano, modo Tabela, com seta de abrir e ícones de ordenar e filtrar em cada coluna | 16/10 |
| Cartões | Atividades do plano, modo Cartões: um cartão por linha, com seta, colunas alinhadas e ⋯ | 16/10 |
| Cabeçalho de tela | Ordem de Serviço: título, estado e a primária verde à direita (BOT-01) | 09/10 |
| Barra da tabela | TAB-01 em `docs/design-system/padroes-1510.md`: a ordem vale como está lá e não se copia aqui | 15/10 |

## O que nunca fazer

- Corrigir só a tela do print.
- Criar estilo local que imita ou anula o componente comum.
- Publicar sem olhar as fotos.
- Mudar oráculo de teste para "passar" sem registrar o motivo.
- Perguntar ao proprietário o que o padrão já responde.
