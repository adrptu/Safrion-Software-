# Aviso de retorno, ⋯ da linha e alertas na tabela

Pedidos do proprietário de 15/10/2026:

- "quando salva uma alteração, o feedback é em preto com letras brancas, e cheio de texto; deveria ser uma caixa pequena, pouco texto, e com cores mais adequadas, como um verdinho leve e um ícone intuitivo".
- "em vez desses botões soltos na tabela, coloque os 3 pontinhos e coloque todos botões de ação ali com ícones intuitivos".
- "esses avisos e alertas deixe apenas dentro da tabela de forma visual, não fora dela, temos que ser clean".
- "botão de incluir insumo não deveria ficar verde, mais intuitivo?"

Vale para o protótipo e para o software real (AGENTS §4, design system único). Catálogo dos padrões do dia: [padroes-1510.md](padroes-1510.md).

## 1. Aviso de retorno (toast) · AVI-01

- Componente único: `engine.G2_TOAST`. O tom sai do próprio texto, por `G2_TOAST_TOM`:
  - **Feito** (salvo, incluído, liberado e afins): fundo verde-claro, ✓ verde.
  - **Impedido ou a corrigir** ("Não…", "Informe…", "Conclua…" e afins): fundo âmbar-claro, ⚠.
  - **O resto informa**: fundo branco, ⓘ.
- Caixa pequena: até 420 px, 13 px de texto e ícone de 18 px. O ícone fica fora da leitura; o texto continua sendo o anúncio.
- Pouco texto: diz o que aconteceu e, se preciso, o próximo passo em poucas palavras. Exemplo nos Planos: "Plano salvo · v7".

## 2. ⋯ da linha de tabela · TAB-05

- Opção da grade: `engine.grid(..., menu_linha=True)`. Os botões de ação das células (`k:'act'`) saem da célula e vão para o ⋯ da linha, com ícone pelo verbo (`g2acaoIco`). "Excluir" vem por último, em vermelho, com a mesma confirmação de antes.
- O menu fica preso à janela, no lugar do botão, porque a tabela rola e cortaria o menu. Ele fecha ao rolar. Teclado igual ao "⋯ Mais ações".
- Aplicado em: Planejar safra › Talhões e cultivos (Dividir, Aplicar plano, Excluir).

## 3. Alertas só na tabela · TAB-06

- Planejar safra › Operações e recursos: a frase do veredito e os atalhos de recurso saíram de cima da tabela.
  - O veredito continua para o leitor de tela (`role=status`).
  - O recurso em falta aparece só como ⚠ na linha, com o detalhe na dica: `grid(..., sico_so_icone=True)`.

## 4. Ação da linha de inclusão · BOT-10

- "Incluir" na linha de inclusão de insumo (Planos) é a primária daquele contexto: verde, como no Planejar safra.
