# Barra de ações limpa e "⋯ Mais ações"

Pedidos do proprietário de 15/10/2026:

- "tire todos esses avisos chatos da barra de ações que fica embaixo na tela. deixar tudo clean e minimalista."
- "gostei desses 3 pontinhos... gerando várias opções de ações, deixando a tela mais clean. igual o google faz."

Vale para o protótipo e para o software real (AGENTS §4, design system único).

## 1. Barra de ações do processo (rodapé da etapa)

Componente único: `engine.area_acoes` com os buracos de `g2lib.g2acoes`. Nenhuma tela monta barra própria.

- A barra mostra só botões: retorno e troca de contexto à esquerda; à direita, o "⋯", o avanço secundário e uma ação primária verde.
- A nota (causa da pendência, contexto) não aparece na barra. Ela vira a dica do botão principal (`data-dica`) e a descrição dele para o leitor de tela (`aria-describedby`).
- Atalhos (`lnks`) e a correção contextual (`ctx`) vão para o menu "⋯ Mais ações".
- Exceção: a decisão do momento fica à vista (`decide: true`), por exemplo "sair sem salvar" (Descartar ou Continuar editando). Ela trava um dano concreto, que é perder o que foi digitado.

## 2. "⋯ Mais ações"

- Uma ação primária visível por contexto: cabeçalho da tela, cartão ou seção, e linha de tabela. As outras ações daquele contexto vão para o "⋯".
- O botão "⋯" tem `aria-label` e dica "Mais ações" (ou "Mais ações de <contexto>"). O menu tem `role=menu`, itens com verbo, alvo de toque de pelo menos 40 px e hover verde.
- Na barra de ações, o menu abre para cima, alinhado à direita (`details.acoes-mais`). Fecha ao clicar de novo, e Esc devolve o foco.
- **Componente único** (15/10/2026): `engine.mais(contexto, itens)`, promovido do ⋯ da atividade da Biblioteca de planos. Botão com nome e dica "Mais ações de <contexto>", `aria-haspopup=menu` e `aria-expanded`; itens `role=menuitem`. O comportamento é do `g2lib` (`g2mais*`): ↓ ↑ Home End andam entre os itens, Esc fecha e devolve o foco ao ⋯, clicar fora, sair com Tab ou escolher um item fecha. No toque, ⋯ e itens com 44 px.
- `engine.recolhe_acoes(contexto, ações)` aplica a regra num contexto: a primária e uma secundária ficam à vista, as outras vão para o ⋯. Já passa por ele o cabeçalho de `engine.section` e dos blocos das áreas. A confirmação de um item destrutivo (Restaurar demonstração) aparece fora do menu e fica à vista até a resposta.

## 3. MAIS-02 · Ações do cabeçalho da tela

Pedido do proprietário de 17/10/2026, sobre Manutenção › Planos (no alto, à direita: o verde "Criar plano" e o "⋯"):

> "os 3 pontinhos no topo da tela a direita em criar plano.... é uma boa, toda tela que tiver mais ações pode ter esses 3 pontinhos nesses botões dessa região da tela."

- **Regra.** Na região de ações do cabeçalho da tela (à direita do título) fica à vista no máximo **uma primária verde**. Todas as outras ações daquele contexto vão para o "⋯ Mais ações", logo à direita da primária, como em Manutenção › Planos ("Criar plano" + ⋯).
  - Sem primária, fica à vista a 1ª secundária e as demais vão para o ⋯.
  - Se a tela já tem um ⋯ no cabeçalho, as ações recolhidas entram nele: um ⋯ só.
- **Substitui**, só no cabeçalho da tela, o "a primária e uma secundária ficam à vista" da MAIS-01. Nos blocos, cartões e linhas a MAIS-01 continua igual.
- **Exceções** (ficam à vista):
  - o "‹ Módulo" de voltar (CAB-1);
  - a troca de visão (Tabela | Cartões);
  - a decisão do momento (`decide: true` ou `data-decide`, por exemplo Descartar / Continuar editando).
- **Componente único.** `engine.recolhe_cabecalho(contexto, ações)`, aplicado pelo `ui37.shell37` a toda tela; usa o mesmo `engine.mais` e o mesmo `item_menu` da MAIS-01. Não há componente paralelo.
- **Medição.** `ds_modulos.py`, regra MAIS-02: conta como desvio o cabeçalho com mais de uma ação à vista à direita do título, fora o ⋯, o ⓘ, o "‹ Módulo", a troca de visão e a decisão do momento.
- **Dano evitado:** fileira de botões no topo, que esconde qual é o comando da vez e cresce a cada tela nova.
- **Aplicado em 17/10:** a única tela fora da regra era Cadastros › Estrutura gerencial ("Publicar versão v6" à vista ao lado de "Criar código"): o "Publicar versão" foi para o ⋯, que só aparece com rascunho.

## 4. TAB-05 no motor: ⋯ da linha por padrão

- Desde 17/10/2026 (DS-MODULOS-2) o `engine.grid` liga o ⋯ da linha (`menu_linha`) por padrão: todo botão de ação com texto da célula vai para o ⋯ da linha, com o ícone do verbo.
- Ficam na célula: o atalho de navegação ("Planejar ›"), o link que abre o registro, a célula inteira tocável (`full`), o "Incluir" da linha de inclusão ou da mãe vazia (BOT-10 e CAD-03, por exemplo "Incluir talhão" na fazenda sem talhão) e a pergunta da linha (`decide: true`, por exemplo "Confirmar aceite" / "Voltar" no consumo em conferência do Estoque).
- A grade com lixeira (`dele=True`) segue com a lixeira até pedir `menu_linha=True`.
- Telas da frente aberta do Codex (PAINEL-FIXO-2: CA-02, GE-02det, GE-03, GE-08) ficam fora até a frente fechar (`engine.TAB05_FORA`).

## Verificação

- `solo_mapa_calor_test.py` e `mapa_filtros_test.py` cobrem o Mapa.
- `acao_unica_test.py`, `saf_tab_test.py` e `ocupacao_test.py` cobrem a barra do Planejar safra: sem nota visível, atalho no "⋯" e dica no botão principal.
- A auditoria de conformidade do design system (lote "⋯") aplica a regra às demais telas.
- `ds_padrao_test.py` (partes M e M7) confere o componente e a regra MAIS-01 em 6 telas.
- `ds_modulos.py` (regra MAIS-02, com catraca) confere o cabeçalho das 148 telas; `cadc_cd07_test.py` confere o ⋯ da Estrutura gerencial.
