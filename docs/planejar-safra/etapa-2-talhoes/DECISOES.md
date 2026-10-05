# Decisões · etapa 2 "Talhões e cultivos" (v2)

Acompanha [`ESPECIFICACAO.md`](ESPECIFICACAO.md). Autor: Claude. Revisor: Codex. Nada aqui é aprovação do proprietário.

## 1. Assumi (técnicas e de produto delegadas; o Codex revisa)

1. "Adicionar cultivo" sai sem substituto genérico; planeja-se pela linha (Planejar ›, Dividir, Vincular ciclo ›).
2. Uma linha por talhão; datas em colunas próprias; a faixa gráfica de área × tempo fica para depois.
3. **Previsão não trava, o certo trava.** Trava só com: área desta safra acima do talhão (regra de hoje), núcleo (plantio até o ciclo mínimo da cultura ou o fim previsto, o que vier antes) com plano em uma das duas, perene, e colheita real registrada. Cruzamento de previsões vira pendência visível e o plano entra na demanda (R-14, R-15).
4. **Ciclo mínimo da cultura** (menor ciclo das cultivares no CD-02) como fim certo da lavoura plantada: soja 112, milho 140, feijão 90 dias.
5. **Fim estimado** = plantio + o maior entre o ciclo da cultivar e a última atividade relativa dos planos publicados da cultura. **Pior caso** P(o) = o maior entre o fim da safra e o fim estimado.
6. Rótulos de fonte do fim: Pelo plano · Colheita informada · Observado · Estimado (ciclo) · Sem ciclo · Perene. Só "Observado" é fato.
7. Esta safra reserva a sua área pelo período inteiro para a Área livre; trava e pendência usam os períodos reais.
8. Ocupação de fora aparece quando está em faixa não usada por esta safra ou quando é a antecessora/sucessora imediata de um cultivo desta safra (a causa fica visível). A S2627 ganha linhas de fora, fora das contas; os números dela não mudam.
9. Talhão sem cultivo desta safra e com uma só ocupação de fora é folha: a própria linha mostra a ocupação.
10. Situação existe no nível 0; nas filhas só o alerta próprio. Filtro rápido só no nível 0. Faixa com parcela Perene separada de Ocupado e o complemento "N sucessão(ões) a conferir".
11. **Vincular ciclo** entra nesta fatia (PR-B3), com a trava "nenhuma safra que contém o ciclo cruza este período"; o vínculo nasce sem plano. A Lagoa Grande entra no formulário de safra junto com ele.
12. e4/e5 entram na S2526 como lavoura em campo, provisórios até a decisão da S2526; o serviço lê ocupação por faixa e período.
13. Identidade do ciclo: `v.ciclo`; sem ele, no protótipo, fazenda + faixa + cultura + plantio. Em produção, id do ciclo com vigência própria.
14. Gatilho DATA fora da safra do cultivo não muda início nem fim; vira aviso na linha.
15. Painel: Plano antes de Plantio; Plantio padrão = PlantioMin; Colheita prevista editável sem plano. Cultura e Variedade continuam listas, como hoje; só entra `inputmode="decimal"`.
16. `g2lib.presa()` com `fit-content(vis)` em todas as colunas não presas.
17. Estado `g_cult_*` guarda só cultivos desta safra; exibição montada sobre cópia; `cultsDe` e `soDaSafra` como fontes únicas.
18. Área no formato vigente da grade ("152 ha", até 2 casas).
19. PRs: contrato primeiro; PR-A só serviço; g2lib em PR próprio; PR-B em quatro partes; PR-C por último; homologação depois do PR-C.

## 2. Cortei

- Faixa gráfica SVG na linha (custo a 390 px; decidir depois que o dono vir a tabela).
- Linhas "Livre" por janela de tempo.
- Coluna separada "Ocupação" para a natureza da filha (Safra e Fim por já dizem).
- Sétimo valor de Situação ("Sucessão a conferir", "Sobreposição prevista"): tudo cabe em "A conferir" com motivo na dica e na nota.
- Campo "Fim do ciclo (erradicação prevista)" do perene: regra nova sem PRD, e estimativa não trava.
- Chips de Cultura, sugestões de Variedade e atalho "Quando liberar" no painel (o PlantioMin já preenche a data).
- Duplicidade "plantio na 1ª metade do ciclo" e a recusa de planos com data fixa fora da safra (rascunho anterior, `../rev/v2_rascunho_anterior/`): substituídas pelo núcleo e pelo filtro de DATA da R-03.
- Scripts `v1/` do autor (`ocup.py` usava o fim da safra como pior caso; folga só no fim confirmado): descartados a favor de `verificacao/ocupacao_v2.py`.

## 3. Parâmetros do dono, com padrão

| Parâmetro | Padrão | Pergunta ao proprietário (realidade da fazenda) |
|---|---|---|
| Folga de liberação | **1 dia** (dia seguinte) | "Depois da colheita de um talhão, a próxima cultura pode ser plantada no mesmo dia (atrás da colhedora), no dia seguinte, ou a fazenda precisa de alguns dias para limpeza e preparo? Quantos?" |
| Indisponibilidade por período | não existe; talhão aparece Livre | "Que situações deixam um talhão indisponível por um tempo (pousio, reforma, arrendado a terceiro, área embargada)? Elas devem impedir o planejamento ou só avisar?" |

Com a resposta da segunda, decidir entre aviso e trava pelo AGENTS §4, nomeando o dano evitado, e registrar em `docs/DECISIONS.md` antes de implementar.

## 4. Pendente

- **Registro da decisão de 05/10** em `docs/DECISIONS.md` e revisão do PRD (39.2, PL-01, UX-01, 71.6). Codex escreve, Claude revisa. Pré-requisito do PR-B.
- **S2526 "Encerrada" com lavoura em campo** (PRD.md:563): reabrir a safra ou mover os ciclos. Decisão do Codex; pré-requisito do PR-C. A ocupação vale nos dois casos (OC-U7).
- **Ciclo mínimo como fim certo:** revisão técnica do Codex (pode trocar por outro mínimo derivado de dado conhecido).
- **Encerramento do ciclo perene** (erradicação/renovação) e **indisponibilidade**: mesma decisão de regra, registrada no PRD/DECISIONS antes de código. Ideia a avaliar: a O.S. de erradicação encerrada (ex.: OS-0509) fecha a ocupação, com data real e sem apagar a genealogia.
- **Proteção física na liberação (CMD-06):** sucessora só libera O.S. com colheita real da antecessora.
- **Registro de colheita real** (fonte do "Observado") e **duração da colheita** na ocupação (CAL-14).

## 5. Revisão aplicada

Fonte: os 30 achados confirmados da revisão de `../especificacao.md` (v1, 16:53). "Conflito" = dois achados com correções incompatíveis; diz qual prevaleceu.

| ID | O que mudou na v2 |
|---|---|
| OC-R1 | P(o) = máx(fim da safra, fim estimado) (R-08); usado em R-09, R-10, R-12 e no aviso da R-15. Teste (a) virou recusa, não aviso: com núcleo (OC-R5) o milho sem colheita ocupa certo até 27/12/2026. (b) e (c) em OC-U8/OC-U9. |
| OC-R2 | Fim estimado com o plano mais longo da cultura (R-04 e): c5 17/02, c7 23/03/2027. "Confirmado" virou "Pelo plano"/"Colheita informada". PlantioMin olha também a sucessora; sem janela, mensagem P3 com saída dupla. OC-23. |
| OC-R3 | Livre = Ocupa até + folga, padrão 1; folga 0 permite plantar no dia da colheita (OC-08). Pergunta ao dono reescrita. Saiu "152 ha não se colhem em um dia… lado seguro". Duração da colheita em Pendente. |
| OC-R4 | R-12: ocupação de fora de talhão inteiro continua visível enquanto esta safra só tem parcelas; c4 continua visível depois do T4-A (OC-02, `partest.py:132-137`). |
| OC-R5 | Núcleo pelo ciclo mínimo (R-14). Conflito com REG-02: prevaleceu a síntese "o certo trava, a previsão vira pendência"; o núcleo só trava com plano em uma das duas. Casos (a)-(d) no §7.3. OC-11 passou de 10/02 (aviso) para 10/02 recusado e 11/02 com aviso. |
| OC-R6 | Gravidade baixa. R-04(a): o perene não termina nesta fatia; encerramento em FORA-DE-ESCOPO e Pendente. Campo de erradicação prevista descartado. |
| OC-R7 | Vincular ciclo nesta fatia (R-24), sem copiar plano. Conflito com REG-01 (opção A) e DONO-01 (com plano no painel): o painel pede Plano opcional, Meta e Unidade, escolhidos na hora; a trava de período do DONO-01 vale. |
| OC-R8 | DATA fora da safra do cultivo não muda início nem fim, com aviso (R-03, R-04 c). Café e mamão em 2027/28 começam em 01/11/2027 sem conflito. |
| OC-R9 | Uma função `liberacao(o, modo)` e `ativo(o, x, modo)` para R-09, R-14, R-15 e PlantioMin. Folga 3: T1 23/02, T3 20/02/2027 (fórmula da OC-R3, não a +1+folga da OC-R9). |
| OC-R10 | Período da mensagem = interseção: M1 "21/02/2027 a 10/07/2027". Negativo: 312 ha em 11/07/2027 salva. |
| OC-R11 | R-10.2 nos dois sentidos; faixa com "N sucessão(ões) a conferir"; chip A conferir = área a conferir + sucessão. |
| DONO-01 | Vincular ciclo com a condição de período (R-24); OC-05 negativo na S27SF e positivo na 2027/28 e na Lagoa 2027/28. |
| DONO-02 | `presa()` com `fit-content`; layout 390 redesenhado com o trilho; OC-17 medido a 390 e 360. |
| DONO-03 | Ordem das colunas: Cultura, Ocupa até, Fim por e Safra antes de Variedade; Safra "—" nas linhas desta safra; OC-17 a 1440 até Safra. |
| DONO-04 | Faixa com Perene separado; chips só pelo nível 0 (`qf.nivel0`); explicação hectares × talhões no §3.4. |
| DONO-05 | Plano antes de Plantio; PlantioMin (R-17); OC-21 (13/03/2027 com SOJA-AT). |
| DONO-06 | OC-19 compara com o "Planejar talhão ›" de hoje. Saída (b) com `inputmode="decimal"`; chips de cultura, sugestões e atalho de data cortados. |
| DONO-07 | Colheita prevista editável sem plano; ação "Informar colheita de <talhão> ›" com `&cult=`; OC-22. |
| DONO-08 | Folha com uma ocupação de fora; motivo do A conferir na nota em qualquer estado e na dica. O item "manter a S2627 com a mesma forma" foi superado pela REG-05. |
| DONO-09 | Limitações no §9.3; segunda pergunta ao dono; homologação depois do PR-C. |
| REG-01 | Resolvido pela opção B (Vincular ciclo) em conjunto com OC-R7/DONO-01; a Lagoa só entra no formulário com o PR-B3. R-25 para a Lagoa nova que cruza a LG2627. |
| REG-02 | R-14 só com o certo; R-15 "Sobreposição prevista" como pendência; lote aplica nos 4 (P2 com pendência de 11 dias, R$ 167.992,00 na demanda); tarefa do dono reescrita. |
| REG-03 | Gravidade baixa. e4/e5 com `origem`, OC-U7, decisão S2526 antes do PR-C, nota da chave heurística na R-07. |
| REG-05 | R-12 mostra antecessora e sucessora imediatas; S2627 passa de 10 para 18 linhas, fora das contas; testes por inclusão. |
| REG-06 | Situação só no nível 0; filtro `qf.nivel0`; faixa com Perene. |
| REG-07 | `dcol` com chave de ordenação/filtro; coluna "Fim por" filtrável. |
| REG-08 | `cultsDe`; `v.saf` em `cultAfter`, `dvSave` e `grp_`; OC-15 com N1/N2. |
| REG-09 | Estado só com cultivos desta safra; exibição sobre cópia; `soDaSafra` nos três gravadores; `normCult` não promove filha de fora; OC-13. |
| REG-10 | `partest.py:26` (LEGT) e `saftest.py` adaptados. Conflito com REG-02: "aplicado a 3" virou "aplicado a 4 com pendência", e `testes_pedido` t02 continua igual. |
| REG-12 | §8 reescrito: contrato → PR-A sem `dados2.py` → etapa única → PR-G → B1-B4 → PR-C; links `passo=cultivos`. |

**Números que mudaram da v1 para a v2 (exec.):** P2 na S27SF de 18/03 para 24/03/2027; T3 de 12/02 para 18/02/2027; c7 de 17/03 para 23/03/2027; faixa S27SF "Ocupado 80" virou "Perene 80"; chips S27SF de 10 para 8 (A conferir 4 · Perene 2 · Livre 1 · Planejado 1); linhas S27SF 15 e S2627 18; lote S2627 de 3 para 4 cultivos.
