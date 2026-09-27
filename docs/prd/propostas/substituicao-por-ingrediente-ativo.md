# Proposta: troca de marca pelo mesmo ingrediente ativo (plano → compra → O.S.)

27/09/2026 · Autor: Claude · Revisores: Codex e Gemini (validação tripla, protocolo v4.1). Base: PRD v3.10 (`docs/prd-v3-10`, `f498ab4`).
Pedido do Adrianus: o plano prevê a marca A; a compra escolhe a marca B com o mesmo ingrediente ativo, com concentração igual ou diferente. Como planejamento, compras e O.S. se conectam, com foco técnico no ingrediente ativo.
**Situação:** proposta, revisão 2. A revisão 1 (`069ecb6`) recebeu parecer do Codex, com ajustes materiais, e do Gemini, que concordou depois da revisão do Codex. Nada foi aplicado ao PRD; aplico depois dos aceites.

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

## 2. Decisão (revisão 2, com os ajustes do Codex e do Gemini)

Estrutura aceita pelas três IAs:
- a necessidade técnica fica separada da marca que a atende;
- o catálogo guarda a composição versionada (ingredientes, concentração e base, formulação, registro e bula);
- a equivalência é contextual, nunca uma tabela global por nome do ativo;
- regra determinística calcula e confere; IA só propõe, com fonte;
- o profissional habilitado decide a dose, dentro da bula; compras aprova preço e condições, sem poder técnico;
- o saldo é sempre pelo produto comercial e lote reais;
- nada muda retroativamente.

Regras decididas:

1. **Aceitar não é adotar.** Aceitar tecnicamente B para uma necessidade só torna B **elegível**. Não troca o atendimento nem invalida O.S. **Adotar** B num escopo futuro (área, data, versão) é o que muda o atendimento. Só as O.S. futuras desse escopo perdem a aprovação (41.3).
2. **Contratação depois do aceite técnico.** "Aprovar contratação" de produto diferente do atendimento vigente exige B aceito para aquela necessidade. Isso evita dinheiro comprometido em estoque sem destino técnico.
3. **Necessidade raiz com alocações parciais.** A necessidade existente (domínio Plano, 11.1; sem entidade nova) pode ser atendida em partes: por área, data, produto, dose e versão. Por exemplo, A do estoque em parte da área e B comprado no restante. A soma das alocações é a necessidade: nenhuma demanda duplicada, nenhum estoque reservado duas vezes, inclusive entre safras. Uma O.S. pode ter vários produtos legítimos; retirada parcial autorizada continua valendo.
4. **Dose da bula de B, definida pelo habilitado.** A simulação por ingrediente é só referência. Se cair fora da faixa da bula de B para a cultura e o alvo, fica invalidada **aquela equivalência e aquela dose**, não a marca B. Uma nova recomendação contextual dentro da bula é caminho próprio, com versão própria, e não aproveita a proposta irregular.
5. **Unidades sem atalho.** g de ativo/ha ÷ g de ativo/L = L de produto/ha; g de ativo/ha ÷ g de ativo/kg = kg de produto/ha, sem densidade. Densidade só converte massa e volume **do mesmo material**. Sal e equivalente ácido só se comparam com o fator declarado na bula; sem fator, não há simulação.
6. **Categorias com regra própria.** Mistura de ativos se compara ingrediente a ingrediente: proporção diferente não tem simulação única, mas mistura não é proibida. Biológico e fertilizante seguem a regra da categoria.
7. **Outra formulação com o mesmo ingrediente muda o preparo.** A adoção revalida mistura e preparo (41.4), carência e reentrada da bula de B e as datas de colheita afetadas.

Sugestões do Gemini rejeitadas pelo Codex, e confirmo a rejeição:
- NoSQL ou hash como autoridade do dado;
- proibição universal de mistura;
- conversão manual que contorne unidade ou bula.

## 3. Delta mínimo do PRD (6 pontos, âncoras exatas da v3.10)

| # | Onde | Âncora | Mudança |
|---|---|---|---|
| D1 | 11.1, linha Materiais, coluna de entidades | `Item, unidade, conversão, lote, proprietário, local,` | Incluir "produto comercial registrado com composição versionada: ingredientes, concentração e base de expressão, formulação, registro e bula". Na coluna da relação: "saldo, reserva e entrega pelo produto comercial e lote reais, nunca por ingrediente". |
| D2 | CAL-11, depois do parágrafo que começa por `O limite da dose aplicada permanece válido.` | idem | Parágrafo **Comparação por ingrediente ativo**: `ativo_ha = dose × concentração`, na mesma base de expressão; `dose_referencia_B = ativo_ha ÷ concentração_B`, com a unidade que resulta (L/ha ou kg/ha), sem densidade; densidade só converte massa e volume do mesmo material. A referência não é dose autorizada. `custo_ha = dose_autorizada × preço por unidade-base`; antes da dose autorizada, o custo aparece como faixa da bula. Custo da área = custo_ha × área coberta + frete e demais condições de SU-04. |
| D3 | 40.1, tabela, linha `\| Trocar produto \|` | fim da célula | Acrescentar "; troca de marca pelo mesmo ingrediente ativo segue 40.5". |
| D4 | Nova 40.5, antes de `## 41.` | — | **40.5 Troca de marca pelo mesmo ingrediente ativo:** regras 1 a 7 da seção 2, interface da seção 5 e aceites SUBST-01 a SUBST-10. |
| D5 | SU-04, "Continuidade e estados" | `Comparar qualidade/especificação, frete, prazo,` | Acrescentar: "Proposta de produto diferente do atendimento vigente aparece na linha da necessidade, com planejado → candidato, custo por hectare e total (40.5). Só candidato aceito tecnicamente para aquela necessidade pode ter a contratação aprovada; os demais mostram a situação técnica e a ação de quem decide." |
| D6 | 11.1, linha Plano, coluna da relação | `Modelo + ajustes não perde sua origem` | Acrescentar "; necessidade pode ter alocações parciais por área, data, produto, dose e versão, cuja soma é a necessidade, sem duplicar demanda nem reserva". |

## 4. Aceites (vão para 40.5)

- **SUBST-01 · aceitar não é adotar:** B aceito para uma necessidade continua fora do plano e das O.S. até ser adotado num escopo. Aceitar não muda quantidade, demanda, reserva nem aprovação de O.S.
- **SUBST-02 · adoção por escopo:** adotar B numa área e período futuros troca o atendimento só ali. A quantidade é recalculada pela dose definida dentro da bula de B. A demanda total é a soma das alocações (A em estoque + B comprado, por exemplo), sem duplicar nem reservar duas vezes. Só as O.S. futuras do escopo perdem a aprovação (41.3); as demais seguem intactas.
- **SUBST-03 · contratação:** "Aprovar contratação" de B para a necessidade só fica disponível com B aceito. Antes disso, compras vê a situação "Requer revisão agronômica" e a ação "Pedir revisão".
- **SUBST-04 · dose e unidade:** com concentração diferente, a comparação mostra ativo por hectare, dose de referência e faixa da bula de B, em L/ha ou kg/ha conforme a concentração, sem densidade. A dose autorizada é definida pelo habilitado dentro da bula. Referência fora da faixa invalida aquela equivalência; nova recomendação dentro da bula tem versão própria e não reaproveita a proposta irregular.
- **SUBST-05 · custo:** a comparação ordena por custo por hectare e custo total da área coberta (com frete, prazo e embalagem), não por R$/L. Antes da dose autorizada, o custo por hectare aparece como faixa da bula, nunca como número único.
- **SUBST-06 · sem efeito retroativo:** calda preparada, entregas feitas e realizado mantêm o produto real. O.S. em execução é pausada e só o saldo recebe nova versão.
- **SUBST-07 · estoque e recebimento:** B só atende O.S. cuja versão aprovada cita B; a mesma O.S. pode ter A e B em linhas ou parcelas diferentes. Recebimento de produto diferente do pedido (registro, formulação ou concentração) fica em divergência (SU-06) e não atende O.S. até decisão.
- **SUBST-08 · categorias:** mistura com proporção diferente, sal × equivalente ácido sem fator declarado, biológico ou fertilizante não têm simulação automática; seguem revisão técnica da categoria. Mistura não é proibida por ser mistura.
- **SUBST-09 · formulação:** adoção de outra formulação com o mesmo ingrediente revalida mistura e preparo (41.4), carência, reentrada e datas de colheita; um conflito bloqueia a adoção.
- **SUBST-10 · papéis:** a IA sugere candidatos com fonte (AGROFIT, bula e versão consultada) e não aceita, não adota nem aprova. Compras aprova preço e condições. Aceite e adoção são do profissional habilitado. Aceite ou adoção no plano não dispensam a aprovação de cada O.S. (41; APROV-05).

## 5. Interface: comparação na própria linha (proposta do Codex, com correções)

Aparece na linha do insumo no plano (PL-02, 40.x) e na linha da necessidade na cotação (SU-04). É o mesmo componente do design system, sem tela nova e sem modal.

- **Linha planejada:** marca A · dose e base · quantidade · custo/ha · total.
- **Linha do candidato, logo abaixo:** marca B · dose e base (ou faixa da bula) · quantidade · custo/ha · total · diferença em relação ao planejado.
- **Composição como fato:** "Mesmo ingrediente: glifosato 480 g e.a./L". **Nenhum selo "Equivalente"** só pelo ativo.
- **Bula, carência, reentrada e registro** num detalhe que abre na própria linha, sem perder filtro nem posição.
- **Situação técnica em texto e uma ação primária por estado e papel:**

| Situação | Compras vê | Habilitado vê |
|---|---|---|
| Requer revisão agronômica | Pedir revisão | Revisar candidato |
| Fora da bula (aquela dose) | sem ação; motivo em texto | Nova recomendação |
| Aceito para esta necessidade | Selecionar proposta | Adotar no saldo futuro |
| Adotado (escopo) | Aprovar contratação | Ver O.S. afetadas |
| Recusado | sem ação; motivo em texto | Reabrir revisão |

Correções à proposta de interface do Codex:
1. Antes da dose autorizada, custo/ha e quantidade aparecem como **faixa da bula**, para não parecer dose aprovada.
2. A ação primária depende do **papel**: compras nunca vê "Aceitar" nem "Adotar".
3. As situações usam as mesmas palavras em plano, cotação e O.S., com as cores de estado do design system (cap. 74) e texto sempre presente, nunca só cor.
4. A linha abre, fecha e age pelo teclado, com o foco preservado depois da ação.

## 6. Fora desta proposta (de propósito)

- Catálogo de alternativas pré-aceitas para vários contextos: fica para depois, com evidência de repetição real. SUBST-01 e SUBST-02 já cobrem uma necessidade por vez.
- Integração automática com o AGROFIT: 38/60 já tratam licença, frequência e cobertura antes de prometer sincronização.
- Implementação: nenhuma. Os aceites entram nos testes da agricultura essencial (etapa 04) e de compras (etapa 10) do plano de execução.
- Legalidade integral: a equipe não substitui responsável técnico nem parecer jurídico. As regras seguem RN-016, a bula e a Lei 14.785/2023 como referências verificadas.
