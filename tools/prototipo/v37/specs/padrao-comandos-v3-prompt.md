# PADRAO-COMANDOS-20261003-v3 — prompt melhorado (Adrianus → Claude e Codex)

**Origem:** pedido direto do Adrianus em 03/10, ainda sem resposta do Codex: "os botões na tela têm que ficar na posição perfeita e mais intuitiva de acordo com sua função [...] somente um botão para fazer a mesma coisa [...] quais ficam dentro da tabela ou componente e quais ficam fora [...] padronize em todas as telas, tabelas e componentes, hoje e no futuro, no design system [...] melhore esse prompt para si mesmo e para o Claude e façam acontecer juntos".
**Base:** `padrao-comandos-prd-v2.patch` do Codex (DS-02/26/29/31/33/36/40/53/54/61/63, DS-AC-08/17), sha256 c691c431…. Esta v3 **não substitui** a v2. Ela acrescenta quatro coisas: tipo de botão por função, a matriz dentro × fora do componente, unicidade verificável por máquina e uma garantia para telas futuras.

## Prompt (para os dois agentes)

> Em toda tela, tabela e componente do Safrion, cada comando tem **uma função**, **um lugar**, **um peso visual** e **uma única instância**. O usuário encontra o que fazer sem procurar e faz uma coisa de cada vez.
>
> 1. **Classifique cada comando pela função** (tabela 1). Função ambígua é defeito de rótulo; renomeie com verbo + objeto do domínio.
> 2. **Coloque e pese pela função**, não pela conveniência da tela (tabelas 1 e 2). Só a tarefa ativa usa botão preenchido. Preferência de visualização, filtro e expandir nunca usam o peso da primária.
> 3. **Uma instância por efeito.** Mesmo efeito sobre o mesmo alvo aparece **uma vez** na tela, contando cabeçalho, conteúdo, painel, faixa, cartão e rodapé. Exceções:
>    - a ação por linha, que é uma por registro;
>    - o link de identificação que abre o detalhe do próprio registro.
>
>    Rodapé fixo que repete a primária está **proibido**. Se precisar ficar alcançável, a própria área de ações é que fica presa, sem cópia.
> 4. **Dentro × fora do componente de dados** (tabela 2). Atua sobre a coleção ou sobre itens dela: dentro. Atua sobre a tela, o processo ou o registro principal: fora.
> 5. **Codifique no gerador, não tela a tela.** Os componentes do design system expõem posições nomeadas, e uma tela nova só consegue pôr um comando passando por elas:
>    - coleção: busca, filtros, visão, expandir global, seleção/lote, ação por linha;
>    - seção: título e adicionar;
>    - área de ações: voltar à esquerda, primária à direita;
>    - próximo passo do detalhe.
>
>    Uma verificação na varredura reprova duplicata, primária a mais e comando fora da posição em **todas** as páginas e estados.
> 6. **Prove** em repouso, vazio, seleção ativa, painel aberto, impedimento, somente consulta, celular 360–390 px, tablet e zoom de 200 %, com teclado e toque. Mostre o número de duplicatas por tela antes e depois: a meta é 0. Registre também o máximo de primárias por tarefa ativa (meta: 1; 0 em consulta).
> 7. **Separe** protótipo (agora, Claude), software real (componentes da fatia, depois) e HML (nada declarado). Sem reabrir decisões de negócio: posição e peso, não regra.

## Tabela 1 — função → tipo de botão → posição

| Função | Tipo (peso) | Posição | Observação |
|---|---|---|---|
| Avançar no processo guiado | **Primário** (preenchido), verbo + destino ("Definir rendimentos") | Área de ações **ao fim do conteúdo da etapa**, à direita; "Voltar a {etapa}" secundário à esquerda | A faixa de etapas só informa: sem clique, sem setas, sem Tab. No celular, primária em largura cheia após a secundária. |
| Próximo passo de um registro (detalhe/mapa) | **Primário** | Bloco "Próximo passo" do detalhe ou painel do talhão | Sem cópia no cabeçalho, na faixa ou no cartão. |
| Criar registro principal | **Primário** só se criar é a tarefa da tela; senão secundário com "+" | À direita do **título da listagem** | No vazio, reutiliza o mesmo controle ("Nenhum X · Criar X"), sem segundo botão. |
| Incluir item/filho (formulário de linha, adicionar cultivo/insumo) | **Tonal/secundário** com "+" | No **cabeçalho da seção** à direita; em entrada repetitiva, uma única instância logo após o último item | Foco vai para o novo item. Nunca compete com o avanço. |
| Salvar/confirmar formulário ou painel | **Primário** (verbo do efeito); Cancelar secundário | **Rodapé do formulário/painel**, Cancelar à esquerda e primário à direita | Sem cópia no cabeçalho do painel. Saída com alteração: "Continuar editando" primário e "Descartar alterações" separado. |
| Busca da coleção | Campo com ícone e rótulo acessível | **Início da barra da coleção** (dentro do componente) | "N de M" ao lado. |
| Filtros rápidos | **Chips** (estado selecionado tonal, nunca preenchido como primário), com contagem | Logo após a busca, ou na linha seguinte, **dentro** do componente | Mesmo filtro da coluna (sem filtros paralelos conflitantes). "Limpar filtros" só com filtro ativo. |
| Modos de visão (Lista / Kanban / Recursos / Mapa) | **Seletor segmentado** único, com a visão atual evidente | **Fim da barra da coleção**, à direita | Preserva filtros e contexto. Nunca executa comando nem muda fase. |
| Expandir/recolher | **Chevron** antes do nome (grupo, linha ou seção) + um único controle global discreto (link de texto) | Chevron no próprio grupo; global na barra da coleção | Não seleciona, não abre detalhe, não muda seleção. |
| Ação de um registro | **Link de ação/ícone rotulado**; ocasionais em "Mais ações" com o nome do registro | **Na linha/cartão**, junto ao dado que resolve ou no fim da linha | Uma por registro. Abrir pela identificação; o clique na linha leva ao mesmo destino sem ser outro botão. |
| Ação em lote (selecionados) | Barra contextual (quantidade + ação + Limpar seleção) | **Dentro da coleção**, substitui **só a região de ações** da coleção enquanto há seleção; busca, filtros, resumo, IDs selecionados e foco continuam disponíveis e estáveis | Escopo por IDs, com prévia quando há ocultos. Sem botões de lote inativos sem seleção. Aceite (Codex v3.1): selecionar → buscar outro registro → somar à seleção → abrir detalhe e voltar preserva seleção e contexto. |
| Escopo da tela (fazenda, safra, período) | Seletor de contexto | **Cabeçalho da página** (fora) | Muda tudo que a tela governa, preservando ou tratando rascunho. |
| Exportar, imprimir, configurar | Item de "Mais ações" do **objeto afetado** | Exportar a coleção filtrada e configurar colunas **dentro da coleção**; imprimir o registro **no detalhe**; só a saída/configuração da página inteira vai ao menu da página | Só onde há uso real. Aceite (Codex v3.1): com duas coleções na tela, exportar uma não usa filtros/seleção da outra. |
| Destrutivo | Contornado vermelho, em "Mais ações" ou na linha | Nunca ao lado da primária | Consequência concreta antes de confirmar; desfazer quando reversível. |

## Tabela 2 — dentro × fora do componente de dados (tabela, kanban, grade, mapa)

| Dentro do componente (atua sobre a coleção ou seus itens) | Fora do componente (atua sobre a tela, o processo ou o registro) |
|---|---|
| busca, "N de M", filtros rápidos e de coluna, ordenar/agrupar | escopo da tela (fazenda/safra/período) no cabeçalho da página |
| seletor de visão (fim da barra) | criar o registro principal (ao lado do título da listagem) |
| expandir/recolher (chevron no grupo + global na barra) | avançar no processo (área de ações ao fim do conteúdo) |
| ação por linha/cartão e "Mais ações" do registro | salvar/confirmar formulário (rodapé do painel/formulário) |
| barra contextual de seleção/lote | próximo passo do detalhe (bloco Próximo passo) |
| adicionar item quando a lista é a entrada (uma instância, no cabeçalho da seção ou após o último item) | — (exportar/imprimir seguem o objeto afetado: ver a linha abaixo) |
| totais/subtotais e "Mostrar mais" | voltar/trilha (cabeçalho) |
| exportar a coleção filtrada, configurar colunas (no "Mais ações" da coleção) | imprimir o registro (no detalhe); saída/configuração da página inteira (menu da página) |

## Aceite (DS-AC-08/17 + estes)
- **Varredura de duplicatas** (`acoes_duplicadas.py`, a estender a estados e celular): **0** em todas as páginas e estados. Linha de base v43 (só repouso, desktop): **23 de 145** páginas com ação repetida.
- **Máximo de primárias** por tarefa ativa = 1 (0 em consulta), medido por página e estado.
- **Posição:** cada comando classificado está na sua região (verificação por seletor na varredura).
- **Gerador:** componentes com posições nomeadas. Uma página de prova que tente duplicar ou pôr um comando fora da posição precisa reprovar na verificação.
- **Mac:** um trabalho pesado por vez (`pesado.sh`), um agente por vez.

## v3.1 — precisões do parecer Codex (RETOMADA-ORDENS-20261003/445f3c77, sobre a v3 sha 0787943a), incorporadas
1. **Seleção em lote** troca só a região de ações da coleção. Busca, filtros, resumo, IDs selecionados e foco ficam onde estão e estáveis. Nunca trocar a barra inteira.
2. **Duplicata = comando + alvo/escopo + tarefa ativa**, não só o mesmo texto.
   - A mesma ação em registros diferentes não é duplicata.
   - A mesma ação duas vezes para o mesmo alvo é duplicata, inclusive na mesma linha.
   - Teclado e toque são formas de operar o mesmo controle.
   - Um modal deixa o fundo inerte e devolve o foco ao fechar; o verificador não exige apagar os comandos do fundo.
   - A varredura `acoes_duplicadas.py` deve agrupar por (rótulo normalizado + destino/alvo) dentro da tarefa ativa e visitar os estados, não só a página inicial.
3. **Exportar, imprimir e configurar seguem o objeto afetado:**
   - exportar a coleção filtrada e configurar as colunas ficam dentro da coleção;
   - imprimir o registro fica no detalhe;
   - só a saída ou configuração da página inteira fica no menu da página.

Posição esquerda/direita e tipo tonal são convenções do Safrion adaptadas à responsividade, não verdades universais.
