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

## Verificação

- `solo_mapa_calor_test.py` e `mapa_filtros_test.py` cobrem o Mapa.
- `acao_unica_test.py`, `saf_tab_test.py` e `ocupacao_test.py` cobrem a barra do Planejar safra: sem nota visível, atalho no "⋯" e dica no botão principal.
- A auditoria de conformidade do design system (lote "⋯") aplica a regra às demais telas.
