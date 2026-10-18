# PAINEL-03 · Painel de gestão único

**Pedido do proprietário (18/10/2026):** "melhore também todos os painéis em todos módulos para que sejam mais cirurgicamente úteis para uma gestão estratégica, tática e operacional do mais alto nível... mostrando com clareza os pontos chave a serem atacados, decididos, etc nas alavancas que mais são importantes para cada processo e resultado final. No painel de cada módulo, colocar em abas ou outro tipo, indicadores chave de cada submenu/funcionalidade do módulo, ou veja se fazemos um painel só que navega pelos módulos e depois na funcionalidade/submenu escolhido, para centralizar e unificar o painel de gestão de tudo que importa num só lugar. Melhore esse prompt para si mesmo e junto com o Codex definam o melhor jeito possível de fazer isso, e implantem."

**O pedido, melhorado (é o contrato desta frente):** em um lugar só, quem dirige a fazenda deve saber em 30 segundos:
1. como está o resultado contra o plano e qual alavanca explica a diferença;
2. o que atacar e o que decidir agora, por quem e até quando, na ordem do dano que se evita;
3. em cada módulo e funcionalidade, os 2 a 5 números que movem o resultado, cada um com:
   - referência;
   - desvio;
   - origem de um toque, que leva ao lugar onde se age.

O painel lê das contas canônicas (fonte única). O que falta aparece como "Sem dados" e nunca como zero. O painel não grava nada e não recomenda nada que não seja regra determinística e explicável.

| Campo | Valor |
|---|---|
| ID / resultado útil / persona | PAINEL-03. Um painel de gestão que substitui os quatro painéis de módulo (PAGR, PMAN, PSUP e o cartão Painel do Comercial). Personas: Paulo (proprietário: resultado e decisões), Ana (gestora: atacar e decidir na semana), Rui (RT: o que é dele decidir) |
| Requisitos e fora do escopo | Continua o PAINEL-01 e o PAINEL-02 (Codex): mesmas contas e mesma regra de que ausente não é zero. Fora: meta cadastrável por indicador (F3), alerta por e-mail ou celular, IA generativa, O.S. ou compra automática |
| Autor / revisor / integrador | Claude (autor) · Codex (revisor de produto, critérios e QA; a revisão não bloqueia no protótipo, AGENTS §3.5) · Claude (integrador) |
| Base | composição `claude/v44-v69-mapa` depois da v133 |

## 1. Decisão: um painel só, com duas portas

**Escolha:** um painel único (`PG.dc.html`) com uma fileira de abas, **Prioridades · Agrícola · Manutenção · Suprimentos · Comercial · Crédito**. Ele tem duas portas:
- o item **Painel** na barra lateral, logo depois do Mapa, abre na aba Prioridades;
- o cartão **Painel** de cada módulo abre o mesmo painel já na aba do módulo (`PG.dc.html#mod=agr`).

**Por quê:**
- **Uma fonte.** Hoje são 4 páginas com contas e estilos próprios. Um painel por módulo repetiria a moldura 5 vezes e esconderia o que cruza os módulos, como uma O.S. impedida por falta de insumo, com uma compra atrasada por trás.
- **A pergunta do dono atravessa os módulos.** "O que mais pesa no resultado agora?" Só um painel único consegue ordenar os pontos a atacar de todos os módulos numa lista só.
- **Quem trabalha num módulo continua com o atalho dele:** o cartão Painel do módulo leva à aba certa. Não existe um segundo caminho para o mesmo conteúdo.

**Funcionalidades dentro do módulo:** são **blocos com título**, na ordem do processo, e não uma segunda fileira de abas. O padrão ABA-01 pede uma fileira só, e assim tudo do módulo fica à vista sem clique a mais. Cada bloco leva o nome do item do menu e um "Abrir ›" para a tela.

**Número da aba (ABA-02):** é a quantidade de itens a atacar ou decidir naquele módulo. Só aparece quando é maior que zero.

## 2. O que cada aba mostra

### 2.1 Prioridades

1. **Alavancas do resultado** (estratégico). Uma linha por cultura da safra do recorte, com:
   - **custo:** R$/ha real × orçado;
   - **preço:** R$/unidade vendido × referência;
   - **comercialização:** % da produção já vendida;
   - **produtividade:** colhida × prevista.

   Cada célula traz o desvio colorido pela regra do §4 e leva à origem.
   - A margem prevista por cultura, que é receita menos custo, com a cascata das diferenças ao orçamento (área, produtividade, preço e custo), entra na F2, depois do aceite da conta pelo Codex (§7, pergunta 2).
2. **Atacar agora** (operacional e tático). Uma lista única de todos os módulos, ordenada pelo dano evitado (§3). Cada item traz:
   - o quê;
   - onde (módulo › funcionalidade);
   - impacto, na unidade dele;
   - dono;
   - desde quando ou até quando;
   - o verbo que leva à origem: Liberar, Comprar, Cobrar, Programar…

   Mostra 7 itens; "Ver todos" abre o resto. O mesmo item nunca aparece duas vezes (§3).
3. **Decidir** (tático e estratégico). O que espera a decisão de quem tem a alçada:
   - vistoria acima do nível de controle (RT);
   - quarentena a liberar ou reprovar;
   - ajuste de inventário a aprovar;
   - venda presa por crédito;
   - pedido de alçada.

   Cada item traz quem decide e há quantos dias espera. Decidir acontece na tela de origem, nunca no painel.

### 2.2 Abas de módulo

Cada aba tem um bloco por funcionalidade, com cartões de indicador e, logo abaixo, o que atacar e decidir naquela funcionalidade (o mesmo item e a mesma ordem da aba Prioridades). O detalhe que já existia no PAINEL-02 (O.S. por causa e dono, execução, MIP e custos) fica em "Detalhe", recolhido, dentro do bloco dele. Cada cartão traz:
  - **nível**, numa palavra: **Resultado** (estratégico), **Plano** (tático, plano × real) ou **Hoje** (operacional);
  - o número com a unidade;
  - a referência ("orçado", "previsto", "referência de preço", "prazo") e o desvio;
  - a dica ⓘ, que diz fórmula, fonte e dono;
  - o toque, que abre a origem já filtrada.

Indicadores da F1, todos de contas que já existem (nenhuma fórmula nova além da ordem do §3):

| Módulo › funcionalidade | Indicadores | Fonte canônica |
|---|---|---|
| Agrícola › Ordem de Serviço | O.S. por fase (as 5 do kanban); atrasadas (dias); impedidas por causa; execução em ha realizada × prevista | `pnValores` (PAGR), `agrPainelRef().os`, `agrExecucao` |
| Agrícola › Pragas e doenças | vistorias acima do NC (decidir); vistorias atrasadas; coleta pendente | `agrMip` |
| Agrícola › Previsão e colheita | colheita por cultivo e período (a seção do PAINEL-02) | `painel_agricola.secao` / `pnaVals` |
| Agrícola › Custos e fechamento | custo real × orçado por cultura (R$/ha e %) e o que está parcial | `agrCustoRef` |
| Manutenção › Pendências sem ordem | pendências (vencidas e na janela) | `manSemOrdem` |
| Manutenção › Ordens | abertas; em execução; ordens por fase | `manAberta`, `pnValores` (PMAN) |
| Manutenção › Ativos | ativos bloqueados | `pnValores` (PMAN) |
| Suprimentos › Estoque | lotes com saldo, com reserva e em quarentena; requisições a entregar | `pnValores` (PSUP), `cenSaldoEntregar` |
| Comercial › Contratos e pedidos | preço médio vendido × referência, por produto; vendas de saca a conferir | `comPrecos` |
| Comercial › Recebíveis | a receber; vencido; entregue nos últimos 30 dias | `comIndicadores` |
| Crédito › Ficha do grupo | bens com valor pendente; declarações com mais de 365 dias | `credFichaLinha` |

## 3. Ordem de "Atacar agora" (regra única, explicável na dica)

1. **Classe do dano**, na ordem da trava do AGENTS §4:
   1. lei e segurança: receituário divergente, carência ou reentrada, quarentena;
   2. resultado técnico da lavoura: vistoria acima do NC, O.S. atrasada na janela, O.S. impedida;
   3. dinheiro e estoque: falta de insumo antes da necessidade, título vencido, requisição a entregar;
   4. prazo e ativos: ativo bloqueado, pendência de manutenção sem ordem.
2. **Dentro da classe:** primeiro o impacto em R$, depois em ha, depois em dias. Entre iguais, o mais antigo primeiro.
3. **Sem duplicar:** a O.S. impedida por insumo aparece uma vez, na O.S., com a causa "Insumo no Estoque". A requisição dela não aparece de novo.
4. A regra é a mesma em todas as abas. A aba do módulo só filtra.

## 4. Cor do desvio (uma régua para todos os cartões)

- **Verde:** dentro da referência.
- **Amarelo:** até 10% pior, ou item que espera há até 7 dias.
- **Vermelho:** mais de 10% pior, vencido, ou classe 1 do §3.
- **Cinza:** "Sem dados" ou parcial, com o motivo na dica.

A régua serve a todos até haver meta por indicador (F3). "Pior" depende do sentido de cada indicador: custo acima é pior, preço abaixo é pior.

## 5. Regras de leitura

- **Ausente não é zero:** coleção inválida ou recorte sem dado mostra "Sem dados" no cartão e no total, como no PAINEL-01.
- **Lê e não grava:** o cenário é igual antes e depois de usar o painel.
- **Recorte:**
  - na F1, todas as fazendas e safras, como nos painéis PAINEL-01 e PAINEL-02;
  - na F2, a faixa padrão (Fazenda e Safra) vale para todas as abas, com as contas já preparadas para isso (`agrPainelRef(c, rec)`);
  - um indicador que não tem safra no registro (vistoria do MIP) mostra "Sem dados" com recorte de safra, como no PAINEL-02.
- **Unidades:** não soma culturas nem unidades diferentes. Dinheiro e quantidade em decimal, com a unidade escrita.

## 6. Aceite (medido)

| ID | Aceite | Prova |
|---|---|---|
| P1 | O item Painel da barra abre Prioridades. O Painel de cada módulo abre a aba dele. As 4 páginas antigas saem, e nenhum link fica apontando para elas | `painel03_test` P1, `links_ocultos`, `paginas_scan` |
| P2 | Os indicadores das abas de módulo têm os mesmos números dos painéis antigos sobre a mesma semente: mesma contagem por fase, mesmas impedidas, atrasadas, MIP, custo e colheita | `painel03_test` P2 contra `pnValores`/`agrPainelRef`; a contraprova no render da v132 reprova P1 e P2 |
| P3 | "Atacar agora" segue a ordem do §3: classe e impacto, sem item duplicado | `painel03_test` P3, com casos montados |
| P4 | Coleção ausente mostra "Sem dados", nunca 0 | `painel03_test` P4; `painel_modulos` (MIP ilegível = "Sem dados") |
| P5 | O painel lê e não grava | `painel03_test` P5: instantâneo do cenário antes e depois |
| P6 | Número da aba = itens a atacar e decidir do módulo; some quando é 0 | `painel03_test` P6 |
| P7 | 1440 e 390 px: nada cortado; abas com teclado (setas, Home, End); toque de 44 px; dica ⓘ | `painel03_test` P7, `ds_test`, `textos_soltos` |
| P8 | Os testes dos painéis antigos migram para o painel único: `painel_agricola_test` (todas as opções), `nav_modulos`, `ma_*`, `ds_man`, `mod_fluxo`, `man_limpa`, `textos_soltos` e `links_ocultos`. Comercial: o Painel do módulo é a aba; a tela de oferta passa a se chamar "Oferta e compromissos" | os mesmos casos no painel único; `painel03_test` P8 |

## 7. Para o Codex (revisão pedida, não bloqueia)

1. **Um painel com abas por módulo e blocos por funcionalidade** atende melhor que um painel por módulo com abas por funcionalidade? O critério é a pergunta transversal do dono e o padrão ABA-01.
2. **Margem prevista na F2:** receita prevista = vendido × preço contratado + não vendido × preço de referência; custo previsto = orçado, ou real mais o saldo orçado a executar. A cascata ao orçamento usa área → produtividade → preço → custo. Prefere a ordem fixa ou a média das ordens (Shapley), como na INTEL-03?
3. **A ordem do §3** (classe do dano antes do impacto) evita que um título vencido de R$ 50 mil passe na frente de um receituário divergente? Algum caso em que a ordem induz a decisão errada?
4. **Faltou algum indicador** que mova resultado e já tenha conta canônica? Exemplos: disponibilidade da frota, falta de insumo antes da necessidade pelo `cenEstDem`, momento de compra e venda da INTEL-02.

## 8. Fatias

- **F1:** painel único com as 6 abas, os indicadores da tabela do §2.2, "Atacar agora" e "Decidir" pela regra do §3, e a migração dos 4 painéis e dos seus testes.
- **F2:** margem prevista por cultura com a cascata ao orçamento; falta de insumo antes da necessidade (`cenEstDem`); disponibilidade da frota; momento de compra e venda (INTEL-02 e INTEL-03).
- **F3:** meta por indicador, cadastrada pelo gestor com dono e ritmo; tendência das últimas semanas.
