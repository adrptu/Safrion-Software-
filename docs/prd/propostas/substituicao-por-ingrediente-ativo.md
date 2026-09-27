# Proposta: troca de marca pelo mesmo ingrediente ativo (plano → compra → O.S.)

27/09/2026 · Autor: Claude · Revisores: Codex e Gemini (validação tripla, protocolo v4.1). Base: PRD v3.10 (`docs/prd-v3-10`, `f498ab4`).
Pedido do Adrianus: o plano prevê a marca A; a compra escolhe a marca B com o mesmo ingrediente ativo, com concentração igual ou diferente. Como planejamento, compras e O.S. se conectam, com foco técnico no ingrediente ativo.
**Situação:** proposta. Nada foi aplicado ao PRD; aplico depois dos três pareceres.

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

## 2. Parecer sobre a proposta do Codex

Concordo com a estrutura:
- necessidade técnica separada da marca que a atende;
- composição versionada no catálogo;
- equivalência contextual, sem tabela global por nome do ativo;
- simulação dimensional sem presumir dose;
- regra determinística calcula, IA só propõe com fonte;
- agrônomo decide, compras só aprova preço;
- custo por hectare;
- uma necessidade gera uma demanda;
- saldo pelo produto real;
- troca sem efeito retroativo.

Proponho seis ajustes:

1. **A aceitação técnica vem antes da contratação, não só na aprovação da O.S.** Se compras contrata B e o agrônomo depois recusa, sobra estoque sem destino técnico e dinheiro comprometido. Por isso, "Aprovar contratação" de produto diferente do atendimento vigente exige, antes, a aceitação técnica de B para aquela necessidade. A aprovação individual de cada O.S. (41; APROV-05) continua.
2. **Sem entidade nova.** A "necessidade" já existe no domínio Plano (11.1). Ela ganha dois campos: **atendimento vigente** (produto, versão da composição e dose da bula) e **alternativas aceitas** (produto, dose, contexto, quem aceitou e quando).
3. **Dose de B vem da bula de B, sempre.** A simulação por ingrediente mostra a dose de B que daria a mesma quantidade de ingrediente por hectare. Isso é **referência**, não dose autorizada. Se a simulação cair fora da faixa da bula de B para aquela cultura e alvo, a alternativa aparece como "fora da bula" e não pode ser aceita.
4. **Base de expressão explícita.** Sal e equivalente ácido só se comparam com o fator declarado na bula. Sem fator, não há simulação.
5. **Mistura de ativos se compara ingrediente a ingrediente.** Proporção diferente, ingrediente a mais ou a menos: nenhuma simulação única; revisão técnica completa. Biológico e fertilizante seguem as regras próprias da categoria, sem simulação por ingrediente ativo.
6. **Mesmo ingrediente e outra formulação mudam o preparo.** Exemplos: concentrado emulsionável × suspensão concentrada. A troca revalida a ordem de mistura e a compatibilidade (41.4), a carência e a reentrada da bula de B (RF-AGR-006) e as datas de colheita afetadas.

## 3. Delta mínimo do PRD (5 pontos, âncoras exatas da v3.10)

| # | Onde | Âncora | Mudança |
|---|---|---|---|
| D1 | 11.1, linha Materiais, coluna de entidades | `Item, unidade, conversão, lote, proprietário, local,` | Incluir "produto comercial registrado com composição versionada: ingredientes, concentração e base de expressão, formulação, registro e bula". Na coluna da relação: "saldo, reserva e entrega pelo produto comercial e lote reais, nunca por ingrediente". |
| D2 | CAL-11, depois do parágrafo que começa por `O limite da dose aplicada permanece válido.` | idem | Parágrafo novo, **Comparação por ingrediente ativo**: `ia_ha = dose × concentração` (mesma base de expressão); `dose_simulada_B = ia_ha_A ÷ concentração_B`. É simulação, não dose autorizada; a dose autorizada vem da bula de B para a cultura e o alvo. `custo_ha = dose_autorizada × preço por unidade-base`; custo da área = custo_ha × área coberta + frete e demais condições de SU-04. |
| D3 | 40.1, tabela, linha `\| Trocar produto \|` | fim da célula | Acrescentar "; troca de marca pelo mesmo ingrediente ativo segue 40.5". |
| D4 | Nova 40.5, antes de `## 41.` | — | **40.5 Troca de marca pelo mesmo ingrediente ativo:** as regras dos ajustes 1 a 6 acima, em até 8 parágrafos curtos, e os aceites SUBST-01 a SUBST-08. |
| D5 | SU-04, "Continuidade e estados" | `Comparar qualidade/especificação, frete, prazo,` | Acrescentar: "Proposta de produto diferente do atendimento vigente mostra a necessidade afetada e o custo por hectare tratado da alternativa. Só alternativa aceita tecnicamente para aquela necessidade pode ter a contratação aprovada; as demais aparecem como 'Requer revisão agronômica' (40.5)." |

## 4. Aceites (vão para 40.5)

- **SUBST-01:** plano com A. A cotação de B, com o mesmo ingrediente e a mesma concentração, mostra "Requer revisão agronômica" até o agrônomo aceitar B para aquela necessidade. Aceita, a necessidade passa a ter B como atendimento, com a quantidade recalculada pela dose da bula de B. O total segue uma única demanda: nunca A + B.
- **SUBST-02:** B com concentração diferente. A simulação mostra ingrediente por hectare, dose simulada e faixa da bula de B; a dose autorizada é escolhida pelo agrônomo dentro da bula. Simulação fora da faixa: alternativa "Fora da bula", sem aceitação possível.
- **SUBST-03:** a comparação de compra ordena as alternativas aceitas por custo por hectare tratado e custo total da área coberta (com frete, prazo e embalagem), não por R$/L. Uma alternativa mais barata por litro que custa mais por hectare aparece como mais cara.
- **SUBST-04:** a aceitação de B invalida a aprovação das O.S. futuras afetadas (41.3). O.S. em execução é pausada e só o saldo recebe nova versão. Calda preparada, entregas feitas e realizado mantêm o produto real; nada é convertido retroativamente.
- **SUBST-05:** estoque de B só atende O.S. cuja versão aprovada cita B. Recebimento de produto diferente do pedido (registro, formulação ou concentração) fica em divergência (SU-06) e não atende O.S. até decisão de compras e do agrônomo.
- **SUBST-06:** mistura com proporção diferente, sal × equivalente ácido sem fator declarado, biológico ou fertilizante: nenhuma simulação automática; a alternativa pede revisão técnica completa.
- **SUBST-07:** troca de formulação com o mesmo ingrediente revalida mistura e preparo (41.4), carência e reentrada da bula de B e datas de colheita afetadas; um conflito bloqueia a aceitação.
- **SUBST-08:** a IA pode sugerir alternativas com fonte (AGROFIT, bula e versão consultada), mas não aceita nem aprova. Alternativa aceita no plano não dispensa a aprovação individual de cada O.S. (41; APROV-05). Compras aprova preço e condições, nunca a aceitação técnica.

## 5. Fora desta proposta (de propósito)

- Catálogo de alternativas pré-aceitas para vários contextos: fica para depois, com evidência de repetição real. SUBST-01 já permite aceitar B para uma necessidade sem refazer o plano.
- Integração automática com o AGROFIT: 38/60 já tratam licença, frequência e cobertura antes de prometer sincronização.
- Implementação: nenhuma. Os aceites entram nos testes da fatia de agricultura (etapa 04) e de compras (etapa 10) do plano de execução.

## 6. Pedido ao Gemini (contraexemplos)

Tentar quebrar os aceites com casos reais:
- mesmo ingrediente com registros diferentes por cultura ou alvo;
- genérico com carência maior;
- concentração em equivalente ácido × sal;
- mistura pronta × produtos separados;
- embalagem que força compra acima da necessidade;
- entrega do fornecedor com marca trocada.

Não aprovar pela semelhança das respostas; cada contraexemplo precisa apontar o aceite que falha.
