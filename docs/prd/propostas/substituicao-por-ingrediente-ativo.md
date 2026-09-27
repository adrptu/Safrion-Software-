# Proposta: produto fixo ou troca de marca pelo mesmo ingrediente ativo (plano → compra → O.S.)

27/09/2026 · Autor: Claude · Revisores: Codex e Gemini (validação tripla, protocolo v4.1). Base: PRD v3.10 (`docs/prd-v3-10`, `f498ab4`).
Pedidos do Adrianus: (1) o plano prevê a marca A; a compra escolhe a marca B com o mesmo ingrediente ativo, com concentração igual ou diferente. Como planejamento, compras e O.S. se conectam, com foco técnico no ingrediente ativo. (2) Alguns clientes só querem comprar e usar o produto comercial da preferência deles; o sistema precisa oferecer essa opção.
**Situação:** proposta, revisão 4 (dois esclarecimentos do Codex; parecer do Gemini sobre o modo fixo em `gemini-pro-produto-fixo.json`, que analisou os trechos enviados e não executou testes). Aceite do Codex: especificação no escopo, sem prescrição nem homologação de produto.
- A revisão 2 (`73806ac`) teve os trechos de interface e cálculo aceitos pelo Gemini 3.1 Pro, com três correções do Codex (registro no espaço de trabalho do Codex: `gemini-pro-ux-substituicao-final.json`). Isso é aceite de texto, não teste de produto nem homologação agronômica.
- A revisão 3 incorporou essas três correções e o modo de produto fixo pedido pelo Adrianus.
- Nada foi aplicado ao PRD.

## 1. O que o PRD já garante (não duplicar)

| Regra vigente | Onde |
|---|---|
| Produto com o mesmo ingrediente não é automaticamente substituível | AG-07 (continuidade, "Produto equivalente por ingrediente…") |
| Substituição de produto exige revisão técnica e histórico | RF-AGR-006; 40.1 "Trocar produto"; 65.5 |
| Mudança de produto, formulação, dose ou concentração invalida a aprovação da versão futura; calda preparada fica segregada e não é recalculada | 41.3 |
| Almoxarife, caldeiro e operador não trocam produto nem dose | 41.3; 42.1 |
| Entrega só do produto, formulação e concentração autorizados; troca de produto volta ao agrônomo | 42.1 |
| Proposta tecnicamente incompatível não vence só pelo preço | RF-SUP-005; SU-04 |
| Quantidade = dose autorizada × área; margem de compra não eleva a dose | CAL-11 |
| Restrição de registro/bula, receituário, carência e reentrada não aceita justificativa | RN-016; RF-EXT-002 |
| Base legal vigente: Lei 14.785/2023 | Fonte S7 do PRD (arts. 22, 39 e 43 verificados pelo Codex em 27/09) |

**Lacuna:** não existe o fio que liga a necessidade do plano à marca que a compra escolhe. Também faltam a regra de dose quando a concentração muda, a comparação de preço por hectare tratado e o destino do que já foi comprado ou recebido de outra marca.

## 2. Decisão

Estrutura aceita pelas três IAs:
- a necessidade técnica fica separada da marca que a atende;
- o catálogo guarda a composição versionada (ingredientes, concentração e base, formulação, registro e bula);
- a equivalência é contextual, nunca uma tabela global por nome do ativo;
- regra determinística calcula e confere; IA só propõe, com fonte;
- o profissional habilitado define a dose, dentro da bula; compras aprova preço e condições, sem poder técnico;
- o saldo é sempre pelo produto comercial e lote reais;
- nada muda retroativamente.

Regras:

1. **Modo do item: "Usar somente este produto" ou "Permitir alternativas com aprovação técnica".** A escolha fica no item do plano e segue a herança do plano padrão para os talhões (40.3): marcada no padrão, vale para todos os talhões que herdam, sem nível novo de configuração. O produto planejado é preservado até uma escolha explícita. O modo acompanha a necessidade até compra, recebimento, reserva e O.S.
2. **Modo fixo = produto exato.** Mesmo registro, formulação e concentração.
   - Embalagens diferentes do mesmo produto são o mesmo produto.
   - O código do fornecedor é só um de-para para o produto do catálogo, nunca a identidade comercial.
   - Não há sugestão de outra marca, nem pela IA, nem substituição por preço ou por falta de estoque.
   - Fornecedores e preços **do mesmo produto** continuam comparáveis.
   - Falta de estoque vira pendência com ação clara.
   - Entrega de outro produto fica registrada pelo produto real, em divergência, e nunca atende O.S. do item fixo.
3. **A preferência não passa por cima de restrição técnica** (RN-016). Se o produto fixo deixar de ser regular para aquela cultura e alvo (registro, bula ou restrição), o item fica bloqueado para decisão técnica. A preferência nunca obriga a usar produto irregular.
4. **Mudar o modo** usa a permissão que já existe para alterar o item do plano (40.1). É uma revisão explícita e versionada do escopo futuro, com as revalidações pertinentes.
   - De "permitir" para "fixo" com alternativa já adotada no escopo: a mesma revisão diz qual produto fica fixo e mostra o impacto nas alocações.
   - Sem alçada nova.
5. **Aceitar não é adotar** (modo com alternativas). Aceitar B só o torna elegível. **Adotar** B num escopo futuro (área, data, versão) é o que cria a alocação, muda o atendimento ali e invalida só as O.S. futuras desse escopo (41.3).
6. **Contratação só com alocação aprovada.** "Aprovar contratação" de B exige B aceito **e** adotado num escopo que ainda precise do produto. Assim não se comprometem duas compras para a mesma parcela (A e B).
7. **Necessidade raiz com alocações parciais.** A necessidade existente (domínio Plano, 11.1; sem entidade nova) pode ser atendida em partes: por área, data, produto, dose e versão. Exemplo: A do estoque numa parte e B comprado no restante. A soma das alocações é a necessidade, sem demanda nem reserva duplicada, inclusive entre safras. Uma O.S. pode ter vários produtos legítimos, e retirada parcial autorizada continua valendo.
8. **Dose da bula de B, definida pelo habilitado.** A referência por ingrediente é só comparação. Fora da faixa da bula, fica invalidada aquela equivalência e aquela dose, não a marca B. Nova recomendação dentro da bula é caminho próprio, com versão própria.
9. **Unidades e bases sem atalho.**
   - g de ativo/ha ÷ g de ativo/L = L de produto/ha; g de ativo/ha ÷ g de ativo/kg = kg de produto/ha, sem densidade. Densidade só converte massa e volume do mesmo material.
   - Sal e equivalente ácido só se comparam com fator declarado.
   - Dose por 100 L de calda, por planta ou por massa de semente tem base própria (41.5). Só vira valor por hectare com o contexto que falta: volume de calda por hectare, plantas por hectare ou semente por hectare. Sem esse contexto, a situação é **"Dose técnica pendente"**.
10. **Categorias com regra própria.** Mistura de ativos se compara ingrediente a ingrediente e não é proibida. Biológico e fertilizante seguem a regra da categoria. Outra formulação com o mesmo ingrediente revalida mistura e preparo (41.4), carência, reentrada e datas de colheita.

Sugestões do Gemini que continuam rejeitadas:
- NoSQL ou hash como autoridade do dado;
- proibição universal de mistura;
- conversão manual que contorne unidade ou bula.

## 3. Delta mínimo do PRD (6 pontos, âncoras exatas da v3.10)

| # | Onde | Âncora | Mudança |
|---|---|---|---|
| D1 | 11.1, linha Materiais, coluna de entidades | `Item, unidade, conversão, lote, proprietário, local,` | Incluir "produto comercial registrado com composição versionada: ingredientes, concentração e base de expressão, formulação, registro e bula; de-para do código do fornecedor". Na coluna da relação: "saldo, reserva e entrega pelo produto comercial e lote reais, nunca por ingrediente nem por código de fornecedor". |
| D2 | CAL-11, depois do parágrafo que começa por `O limite da dose aplicada permanece válido.` | idem | Parágrafo **Comparação por ingrediente ativo e custo por hectare**, com três regras. (a) `ativo_ha = dose_ha × concentração`, na mesma base de expressão, e `dose_referencia_B = ativo_ha ÷ concentração_B`, na unidade resultante, sem densidade; é referência, não dose autorizada. (b) `custo_ha = dose_ha × preço por unidade-base`, **só** com dose normalizada por hectare: base por 100 L, planta ou semente exige o contexto de 41.5. (c) Antes da dose autorizada, mostrar faixa **só** quando a bula tem faixa explícita aplicável e o contexto dimensional está completo; senão, "Dose técnica pendente", sem custo e sem ordenar pelo limite inferior. |
| D3 | 40.1, tabela, linha `\| Trocar produto \|` | fim da célula | Acrescentar "; modo do item (produto fixo ou alternativas) e troca de marca pelo mesmo ingrediente ativo seguem 40.5". |
| D4 | Nova 40.5, antes de `## 41.` | — | **40.5 Produto fixo ou troca de marca pelo mesmo ingrediente ativo:** regras 1 a 10 da seção 2, interface da seção 5 e aceites SUBST-01 a SUBST-15. |
| D5 | SU-04, "Continuidade e estados" | `Comparar qualidade/especificação, frete, prazo,` | Acrescentar: "No item com produto fixo, só propostas do mesmo produto (registro, formulação e concentração) são comparáveis; as demais aparecem como 'Fora do produto fixado'. No item com alternativas, a proposta de outro produto aparece na linha da necessidade, com planejado → candidato (40.5), e só tem a contratação aprovada se estiver aceita e adotada num escopo que ainda precise dela." |
| D6 | 11.1, linha Plano, coluna da relação | `Modelo + ajustes não perde sua origem` | Acrescentar "; necessidade tem modo (produto fixo ou alternativas) e pode ter alocações parciais por área, data, produto, dose e versão, cuja soma é a necessidade, sem duplicar demanda nem reserva". |

## 4. Aceites (vão para 40.5)

**Troca de marca (item com alternativas)**
- **SUBST-01 · aceitar não é adotar:** B aceito continua fora do plano e das O.S. até ser adotado. Aceitar não muda quantidade, demanda, reserva nem aprovação de O.S.
- **SUBST-02 · adoção por escopo:** adotar B numa área e período futuros cria a alocação e troca o atendimento só ali. A quantidade vem da dose definida dentro da bula de B. A demanda total é a soma das alocações, sem duplicar nem reservar duas vezes. Só as O.S. futuras do escopo perdem a aprovação (41.3).
- **SUBST-03 · contratação:** "Aprovar contratação" de B só existe com B aceito e adotado num escopo que ainda precise do produto. Com B só aceito, compras compara, mas não contrata. A contratação não excede nem duplica a necessidade líquida do mesmo escopo; pedidos parciais legítimos continuam possíveis.
- **SUBST-04 · dose e unidade:** a comparação mostra ativo por hectare, dose de referência e faixa da bula de B na unidade resultante, sem densidade. A dose autorizada é do habilitado, dentro da bula. Referência fora da faixa invalida aquela equivalência; nova recomendação tem versão própria.
- **SUBST-05 · custo:** ordenação por custo por hectare e custo total da área coberta (frete, prazo e embalagem), não por R$/L. Custo por hectare só com dose normalizada por hectare. Antes da dose autorizada, faixa só se a bula tiver faixa explícita aplicável e o contexto dimensional estiver completo. Senão, "Dose técnica pendente", sem custo e fora da ordenação por preço.
- **SUBST-06 · sem efeito retroativo:** calda preparada, entregas feitas e realizado mantêm o produto real. O.S. em execução é pausada e só o saldo recebe nova versão.
- **SUBST-07 · estoque e recebimento:** B só atende O.S. cuja versão aprovada cita B. A mesma O.S. pode ter A e B em linhas ou parcelas diferentes. Recebimento de produto diferente do pedido fica em divergência (SU-06).
- **SUBST-08 · categorias:** mistura com proporção diferente, sal × equivalente ácido sem fator, biológico ou fertilizante não têm simulação automática. Mistura não é proibida por ser mistura.
- **SUBST-09 · formulação:** adoção de outra formulação revalida mistura e preparo, carência, reentrada e datas de colheita; um conflito bloqueia a adoção.
- **SUBST-10 · papéis:** a IA sugere candidatos com fonte e não aceita, não adota nem aprova. Compras aprova preço e condições. Aceite e adoção são do habilitado. Nada disso dispensa a aprovação de cada O.S. (41; APROV-05).

**Produto fixo**
- **SUBST-11 · escolha e herança:** um item novo nasce com o produto planejado preservado. "Usar somente este produto" marcado no plano padrão vale para os talhões que herdam; o ajuste local segue 40.3. Um item fixo não sugere candidatos, nem pela IA, nem troca por preço ou falta. A revisão técnica não altera a preferência comercial em silêncio: mudar o modo usa a permissão de alteração do plano (SUBST-15).
- **SUBST-12 · identidade exata:** fixo significa mesmo registro, formulação e concentração. Outra embalagem ou qualquer lote apto do mesmo produto atende. Código de fornecedor diferente para o mesmo produto do catálogo atende. Proposta divergente já recebida na cotação fica visível só como ocorrência "Fora do produto fixado", sem recomendação e sem seleção. Preço e prazo entre fornecedores do mesmo produto continuam comparáveis.
- **SUBST-13 · falta de estoque:** sem saldo nem entrega prevista a tempo, o item mostra a pendência "Falta [produto] para [necessidade]", com a ação de cada papel: compras "Cotar este produto", PCP "Reprogramar", habilitado "Revisar modo do item". Nada troca de produto sozinho.
- **SUBST-14 · entrega diferente:** produto diferente do fixado fica registrado pelo produto real, em divergência (SU-06), e nunca atende O.S. do item fixo. O destino do material segue a decisão explícita de SU-06, nunca uma baixa ou entrada automática. Pode atender outra necessidade só se for o produto dela, depois de resolvida a divergência.
- **SUBST-15 · mudança de modo e regularidade:** mudar o modo exige a permissão que já existe para alterar o item, com revisão versionada do escopo futuro e revalidação. Com alternativa adotada no escopo, a revisão diz qual produto fica fixo e mostra o impacto. Cada mudança de modo fica no histórico versionado do item, com autor, motivo e escopo. Produto fixo que deixa de ser regular para a cultura e o alvo bloqueia o item para decisão técnica, sem forçar o uso.

## 5. Interface: comparação na própria linha (Codex; aceita pelo Gemini com correções)

É um componente do design system, sem tela nova nem modal. Aparece na linha do insumo no plano (PL-02, 40.x) e na linha da necessidade na cotação (SU-04).

- **Modo do item** na própria linha: "Usar somente este produto" ou "Permitir alternativas com aprovação técnica". Mudar abre a revisão do escopo futuro (regra 4) na própria linha.
- **Item fixo:** só a linha do produto, com fornecedores e preços do mesmo produto. Falta de estoque aparece como pendência com a ação do papel (SUBST-13).
- **Item com alternativas:** linha planejada (marca A · dose e base · quantidade · custo/ha · total) e, abaixo, a linha do candidato (marca B · dose e base · quantidade · custo/ha · total · diferença). Onde não há dose normalizada nem faixa aplicável, aparece "Dose técnica pendente", sem custo.
- **Composição como fato:** "Mesmo ingrediente: glifosato 480 g e.a./L". Nenhum selo "Equivalente" só pelo ativo.
- **Bula, carência, reentrada e registro** num detalhe que abre na própria linha, sem perder filtro nem posição.

Situação técnica sempre em texto, com uma ação primária por estado e papel:

| Situação | Compras vê | Habilitado vê |
|---|---|---|
| Requer revisão agronômica | Pedir revisão | Revisar candidato |
| Dose técnica pendente | sem ação; motivo em texto | Completar contexto da dose |
| Fora da bula (aquela dose) | sem ação; motivo em texto | Nova recomendação |
| Aceito para esta necessidade | Comparar (sem contratar) | Adotar no saldo futuro |
| Adotado (escopo) | Aprovar contratação | Ver O.S. afetadas |
| Recusado | sem ação; motivo em texto | Reabrir revisão |
| Fora do produto fixado (ocorrência) | sem ação; motivo em texto | Revisar modo do item |

Regras de interface:
- compras nunca vê "Aceitar" nem "Adotar";
- as situações usam as mesmas palavras em plano, cotação e O.S., com as cores do design system (cap. 74) e sempre com texto;
- a linha abre, fecha e age pelo teclado, com o foco preservado.

## 6. Fora desta proposta (de propósito)

- Catálogo de alternativas pré-aceitas para vários contextos: fica para depois, com evidência de repetição real.
- Integração automática com o AGROFIT: 38/60 já tratam licença, frequência e cobertura antes de prometer sincronização.
- Nível novo de configuração ou de alçada para o modo do item: a herança do plano padrão (40.3) cobre o cliente que quer tudo fixo.
- Implementação: nenhuma. Os aceites entram nos testes da agricultura essencial (etapa 04) e de compras (etapa 10) do plano de execução.
- Legalidade integral: a equipe não substitui responsável técnico nem parecer jurídico. As regras seguem RN-016, a bula e a Lei 14.785/2023 como referências verificadas.
