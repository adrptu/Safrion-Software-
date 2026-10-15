# Fluxo de etapas do processo (cartões com seta)

Pedidos do proprietário de 15/10/2026:

- "esses ícones e setas para fluxo de processos ficou melhor, mais intuitivo, torne mais bonito com nosso design system e substitua o atual fluxo de processos visual".
- "E no fluxo de processos permita clicar diretamente na etapa do fluxo de processos desejado e ir para a tela."

Vale para toda tela de processo em etapas (hoje: Planejar safra e Compras de insumos), no protótipo e no software real. Revoga a regra de 03/10 de que a faixa "só informa" (UX-ACAO-UNICA-20261003).

## Regras

- Componente único: `ui37.steps_state` com os buracos de `g2lib.g2steps`. Nenhuma tela monta faixa própria.
- Cada etapa é um cartão: número (✓ feita, ! impedida), nome, situação em texto curto e contagem opcional. Seta › entre os cartões.
- Etapa atual com fundo verde-claro e borda verde; futura neutra (ETP-01); impedida com borda vermelha-clara.
- O cartão inteiro é um botão que leva à etapa. A etapa atual não faz nada.
- Etapa travada (por exemplo, "Escolha a safra") não navega: `aria-disabled`, cursor de proibido e o motivo em dica e aviso. Ela protege a ordem do dado, não esconde o caminho.
- Hover verde só nos cartões que levam a algum lugar (VIS-02).
- Na faixa estreita, a lista abre como folha. Tocar numa etapa leva a ela, fecha a folha e devolve o foco ao rótulo.
- O avanço e o retorno continuam na área de ações. A primária é uma só.

## Verificação

- `acao_unica_test.py` 1: cartões-botão, clique na etapa 1 e volta à 2, etapa travada com motivo e o Tab passa pela faixa.
- `componentes_test.py` 14 e 17: hover verde e cursor de ação; teclado na folha (Enter leva à etapa e devolve o foco).
- `etapas_celular_test.py` 9, 10, 20 e 22: teclado, toque, tela baixa e folha.
