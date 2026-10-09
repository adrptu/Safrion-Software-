# Beneficiamento · v2 · Decisões

Complemento de `ESPECIFICACAO.md` (era o §14 do v1). Rótulo: especificado. O que diz "(executado)" saiu de comando rodado em 05/10/2026 (§8).

## 1. Assumi

- **O pedido de 05/10/2026 vale só para o Beneficiamento.** O resto de Colheita e pós-colheita segue oculto (portão P1).
- **Escala do PRD 10.0, sem exceção** (tabela única em ESPECIFICACAO.md §3.4, l.4186-4191). Motivo: o PRD exige a mesma string decimal no protótipo, no backend e na auditoria (l.4197). O BEN-03 (l.7561) mostra 4 casas no resultado do teste; não fixa a escala de persistência (conferência no K51). O R$/kg da tela é apresentação; o PRD deixa o preço unitário com até 8 casas (l.4185).
- **Água pela subtração depois da quantização** (R-B01; achado C-01): a forma direta, nos empates, faria est + água passar de m (K52).
- **Físico do lote de entrada:** fica o entregue à ordem até o Fechar (C-09). O "em processo" da ordem é explícito (BEN-R06): consumo declarado nas saídas das rotas por batelada; declaração de "tudo processado" no Concluir das rotas de linha. O PRD prevê "Registrar avanço e saídas" (l.1067) e o FO-14 "Registrar avanço" (l.2324).
- **Estorno sem MP-.** Os lotes de saída só nascem no Fechar (l.2794), então estornar um registro não move massa de lote. A trilha é o registro inverso com `ref`, o histórico e o MV de caixa (`estorno-consumo`).
- **Sequência de inspeção única** para Qualidade e Manutenção (`cenInspId`, §0.2), porque as duas usam o prefixo INSP- (`areas/maquinas.py:226, 252`). As inspeções já planejadas na semente ficam (K31).
- **REQ-030** para as caixas da OB-0110: a REQ-034 do v1 é do PCM (`pcm/` §10).
- **"Quebra técnica"** é água estimada + diferença; **"rebenefício"** é reprocesso por ordem vinculada. Nenhum dos dois termos existe no PRD.
- **Data de demonstração** é a do protótipo (`dados.py:5`; ESPECIFICACAO.md §10). Os IDs novos seguem a R-A16.
- **Comercial é papel simulado** (não há pessoa no cadastro). Reservar e cancelar gravam "Comercial".
- **Custo-hora de Igor e Marta** (§10.2) é sintético e só preenche o CD-04; a BEN não o usa.
- **Classes dos pedidos de café** são sintéticas: `areas/comercial.py:314` não traz o tipo do PV-028.
- **Marta (conferente) no SU-09 oculto** fica como dívida conhecida (opção b do achado C-03), porque a tela está oculta e não é fonte de dados.

## 2. Cortei

- Grão, café, trava do ativo, custo e compra de caixa no BEN-1 (achado BEN-R03; uma fatia por vez).
- O estado gravado "Suspensa" da reserva: a expedição impedida é derivada (BEN-PRD-06).
- "Ordens fechadas com material conciliado" (a R-A09 já garante) e a meta de perdas do packing (é o mesmo fato da recuperação) (BEN-R08).
- A coluna Validade da g_lp até o BEN-6 (coluna sempre vazia sai; BEN-R13).
- "Em manutenção" como valor do PCM e "1.200 kg/h em Restrito" (sem fonte; C-12, BEN-PRD-07).
- Teste que grava a condição do ativo no `localStorage` da manutenção (BEN-R04).
- O `'REQ-' + (41 + quantidade)` (C-13, BEN-R15).
- O estoque em processo inicial (EP₀) no balanço: nenhuma ordem o tem; volta com ordem contínua (FORA-DE-ESCOPO.md §4).
- Mantidos do v1: faixa "Próximas ações"; rotas no cenário; custo só da caixa; catálogo da fase 7; confirmação de recebimento de caixas no app para OB; mudança da unidade da caixa.

## 3. Parâmetros do dono, com default

Todos "sintético · vN", na versão da rota, e "a confirmar pelo proprietário" (RN-043 l.245). O valor real vem da política da organização ou de protocolo com fonte. Os valores padrão têm fonte única: ESPECIFICACAO.md §10.1 (por rota), §7 (metas) e §2.3 (quem decide). Aqui fica a lista do que o proprietário confirma.

| Parâmetro | Onde está o padrão |
|---|---|
| Tolerância da parte pesada (`tol_pesado`) | §10.1, todas as rotas |
| Incerteza da umidade e hipótese de conservação da matéria seca (`agua`) | §10.1, SEC-GRA v2 e CAF-NAT v1 |
| Alçada de diferença do responsável de produção: % e teto em kg; vale o mais restritivo (R-G06) | §10.1, por rota |
| Quem decide acima da alçada | §2.3 (Ana, como gestão) |
| Fração vendável prevista, equipe, caixas por caixa de Produto, onde se pesa e tara do pallet, aviso de líquido por caixa | §10.1, PACK-FRU v3 |
| Umidade de referência (só milho grão) | §10.1, SEC-GRA v2 |
| Prazo da inspeção aberta no Fechar | §10.1, todas as rotas |
| Custo-hora da equipe do packing (`custo_hh`, BEN-2) | §10.1, PACK-FRU v3 |
| Umidade máxima do café beneficiado (aviso) | §10.1, CAF-BEN v1 |
| Metas de recuperação, de ordens com justificativa e de inspeções vencidas | §7 |
| Horas disponíveis da linha por dia ou turno | sem padrão; definir antes do BEN-5 (I16) |
| Vida útil do mamão | 7 d, sintético; entra com a R-C06 no BEN-6 |

## 4. Pendente de decisão

Itens que dependem de dado real ou de decisão do proprietário (alçada real e quem é a gestão; umidades, incertezas, hipótese de matéria seca, capacidades e vida útil reais; padrão do MAPA; plausibilidade do L27-013) e lacunas de outros módulos (CMD-42 na O.S.; escala do insumo e da área; contrato de câmara fria): FORA-DE-ESCOPO.md §1 a §3, com o dono e a condição de volta em cada linha. Aqui ficam só as decisões de coordenação:

| Pendência | Dono |
|---|---|
| Registrar a decisão de 05/10 (P1) e o rótulo do menu: o PRD tem "Produção → Beneficiamento" (l.7405) e "Colheita e pós-colheita → Beneficiamento" (l.265) | Codex; v3.10 |
| Ordem da fila: TABELAS-FOCO 2b-2d → PCM 1a-1c → BEN-1 (P2, P3) | Codex |
| TABELAS-FOCO 2e "Colunas configuráveis na G2" ou plano B (P6) | Codex |
| Colheita = O.S. com massa (BEN-5) | Codex |
| Cinco referências do setor (P5) | Codex |
| Datas da OC-0501 contra as cargas do milho (ESPECIFICACAO.md §10.7) | Codex |
| Campo de limite autorizado e prazo na condição "Restrito"; contrato de valores da condição; uso de `cenInspId` pelo PCM | Autor do PCM, no acordo P4 |

## 5. Conflitos resolvidos

### 5.1 Entre os desenhos A e B do v1 (só os motivos que continuam valendo)

| Tema | Escolha e motivo |
|---|---|
| Responsável de produção | **Igor**: Helena é contato do P10 (`dados_cad.py:101`); Davi é usuário revogado em 15/09 (`areas/configuracoes.py:9, 110, 433`) |
| OB na O.S. | **Sai**: pelo l.2841, o CO-05 tem Lista, Kanban e Mapa próprios, como o IR-03 |
| Coleções | **`c.ben.*`**: uma chave só, sem poluir a raiz. *Superada pela BEN-D01 (§12): `c.producao`, colheita D-05* |
| Rotas | **Constante estática** até o editor (BEN-6): sem editor, não há estado a guardar |
| Seções | **2** no BEN-1. Uma grade de lotes serve à qualidade e ao estoque |
| Unidade da caixa | **`un`**: o cadastro não muda (`areas/cadastros.py:690`) |
| Massas da semente | **B**: 48.000 kg de milho e 438.600 kg de coco, na escala do texto existente |
| Lote do milho | **L38-120**: segue a regra semana + sequência |
| Conferente | **Rui**, que tem a habilidade "Conferir" |

### 5.2 Entre achados da revisão (resolvidos uma vez)

| Achados | Conflito | Solução |
|---|---|---|
| C-09 × BEN-R06 | C-09 mantém o físico do lote de entrada até o Fechar; BEN-R06 baixa o físico a cada saída | Fica a C-09 (a g_lp não perde massa antes de os lotes de saída nascerem). Da BEN-R06 fica o essencial: em processo explícito, nunca resíduo. Com o "mproc = líquido" da BEN-R06, na fruta o em processo seria a própria diferença e o Concluir travaria toda diferença; por isso a fruta declara o avanço no Concluir |
| BEN-R02 × BEN-PRD-12 (item 3) | Duas saídas para registro duplicado ou errado | Uma só: Estornar registro (R-A15) |
| BEN-R02 × C-09 | O estorno grava MP-, mas o lote ainda não existe | Sem MP-; trilha por registro inverso, histórico e MV de caixa |
| BEN-PRD-01 × BEN-PRD-05 × BEN-PRD-03 | Três formas de tolerância e de alçada | R-A07 só com massa pesada; R-F02 com a faixa (pesado + incerteza da água); R-G06 sobre \|dif\| na justificativa e sobre \|dif₀\| na correção (R-F07). A R-F07 vale também para estorno e relançamento na conferência: senão, estornar um registro certo e relançar com peso maior fecharia a diferença pela outra porta |
| BEN-PRD-05 (item 4) | Diz que a diferença de 0,49 % "é de Ana, porque fica abaixo da alçada de 0,5 %" | Contradição interna. Aplicado: decide Igor (0,49 % ≤ 0,5 % e 234,36 kg ≤ 500 kg; K63) |
| BEN-PRD-02 × BEN-PRD-05 | A faixa usa uma u_f, a fórmula usa várias | A faixa usa a umidade ponderada das saídas, sem quantizar |
| BEN-PRD-02 × R-B02 | Onde entra a impureza na matéria seca | Base por entrada = consumo − impureza da pré-limpeza daquela entrada |
| C-05 × BEN-PRD-04 × BEN-R01 | Três roteiros para o L27-013 | O da BEN-R01: "Liberar como COB tipo 7" e reserva para o PV-035 (tipo 7); da C-05, a recusa de classe vazia; da BEN-PRD-04, o mutante de classe. A "concessão" da BEN-PRD-04 vai para FORA-DE-ESCOPO.md |
| BEN-PRD-06 × BEN-PRD-04 | Os casos de bloqueio e reclassificação com reserva usavam o PV-028, que não recebe reserva | Passam para o L39-120 e o PV-031 no BEN-1 (K22-K24), como a própria BEN-PRD-04 admite |
| C-06 × BEN-R14 | Dois textos para a tarefa do proprietário | Um texto (ESPECIFICACAO.md §11.7), sem número que dependa de digitação e sem troca de papel |
| C-12 × BEN-R04 | A C-12 testa a trava por injeção; a BEN-R04 tira a trava do BEN-1 | Fica a BEN-R04. Da C-12 ficam a lista de valores e a classificação por prefixo, testadas na função pura (U18) |
| C-13 × BEN-R15 × PCM 1b | `cenReqId` novo contra o `cenProxId` do PCM | Uma regra: o `cenProxId` do PCM 1b. O BEN-1a só confere e acrescenta "sem material, sem REQ" ao `cenLiberar` |
| C-07 × BEN-R05 × PCMS-M14 | `cenCustodiaNaEntrega` novo contra o balcão do PCM | `cenBalcao` estende à OB a regra do balcão do PCM; o recebedor herdado é o do PCM, com `o.resp` para a OB |
| C-08 × BEN-R03 | Com o BEN-1 só de packing, o L39-122 deixa de ser do milho na semente do BEN-1 | No BEN-1 o primeiro lote novo é o L39-122 (K28); no BEN-3 ele é o destino da OB-0106; o café fica com o L39-123 (K70), como pede a C-08 |
| C-08 × sequência de inspeção | "INSP a partir de 95" colide com a Manutenção depois de nove inspeções | Gerador único (`cenInspId`); as inspeções planejadas na semente ficam |
| C-02 × BEN-R07 (refutado) | 99,39 % ou 99,37 % | 99,37 % (C-02): a mesma água do painel. A correção da BEN-R07 (igualar a base do painel) não foi aplicada |
| C-10 × BEN-PRD-09 | Bloqueado por produto ou por estágio | Por produto e estágio, sem somar estágios |
| BEN-R12 × renumeração | O custo ia para o bloco 2 do v1, depois do recebimento | BEN-2, logo depois do BEN-1, só para o packing, onde as três parcelas existem no cadastro |

### 5.3 Entre a revisão e as instruções desta rodada

| Tema | Revisão | Instrução | Solução |
|---|---|---|---|
| Portão do PCM | BEN-R03: decidir a ordem antes de editar | BEN-1 depois do PCM 1a | Portão no PCM 1c (P3): o BEN-1 reaproveita peças do PCM 1b e edita um arquivo do PCM 1c. O 1a é o mínimo pedido; o Codex decide a fila, e a regra `v = v(main) + 1` resolve qualquer ordem |
| Falta de caixa | BEN-R11: só atalho ao saldo; compra no bloco de custos | Compra com previsão | Atalho no BEN-1 (I4b, limitação declarada); compra real no BEN-2 (I17), sobre a compra do PCM 1c |
| Versão do cenário | v1: "quem integrar por último sobe para v=5" | Alinhar com o PCM | PCM 4 · 5 · 6; BEN 7 · 8 · 9; regra `v(main) + 1` (§0.2) |

## 6. Propostas ao PRD v3.10 (autor: Codex; revisor: Claude; entrada por PR)

1. Rótulo do menu: um só caminho para o Beneficiamento (l.265 × l.7405).
2. Reserva só Ativa ou Cancelada; "Expedição impedida" derivada; pedido "Em risco" (AC-49 l.4809; CO-06 l.1093; l.7995).
3. "Liberar como classe atingida" como decisão do CMD-24, ao lado de Liberar, Manter bloqueio e Destinar (FO-15 l.2325).
4. Faixa de conferência = tolerância da parte pesada + incerteza da umidade, separada da tolerância computacional (l.4197) e da contratual.
5. Avanço "no Concluir" (linha) e "por saída" (batelada) no FO-14 (l.2324).
6. Correção na conferência com alçada sobre a diferença do Concluir (l.2878; FL-18 l.10826).
7. Alçada de diferença com percentual e teto em kg por rota, no CF-02 (l.1818).
8. Selos "Ganho aparente acima da faixa", "Corrigido na conferência" e "Estornado".
9. Contrato de registro de câmara fria.
10. Confirmação da escala do PRD 10.0 para o protótipo, com as exceções existentes (insumo e área em 2 casas) registradas e versionadas.
11. Sequência única de inspeção para Qualidade e Manutenção.

## 7. Severidade proposta para o software real (o Codex confirma em QA)

| Defeito, se existisse | Severidade | Motivo |
|---|---|---|
| Recusar pesagem real por causa de estimativa | S2 | Fluxo essencial bloqueado; induz falsificação |
| Registro, movimento ou reserva duplicados | S2 | Movimento duplicado (AGENTS §3) |
| Reservar lote não conforme ou de outra classe | S2 | Cálculo material incorreto na promessa ao cliente |
| Liberar lote sem resultado ou com Não conforme | S2 | Venda fora do padrão |
| Perda sem prova fechando a diferença de quem executou | S2 | Integridade do fato; custo por kg errado |
| Sem estorno, ordem presa por digitação | S2 | Fluxo essencial bloqueado |
| LO-02 mostra o L39-120 "Pronta p/ carregar" (`areas/logistica.py:259-261`) | S2 | Expedição de lote não liberado |
| Colheita (OC-*) sem trava de carência | S1 | Lei (carência) |
| Processar com ativo bloqueado, quando a trava existir | candidato a S1 | Segurança (comando físico perigoso) |
| Rótulo "O.S." para a OB no EST; a13 em "Armazém Sede"; "Marta (conferente)" no SU-09 | S4 | Cosmético |

## 8. Evidência (executado em 05/10/2026)

- **Contas:** `verificacao/contas.py` (Python `decimal`, precisão 34, ROUND_HALF_UP, kg com 6 casas); saída em `verificacao/contas_saida.txt` (69 linhas). Todo número marcado "(executado)" na especificação está nessa saída.
- **Conferência da especificação:** `verificacao/confere.py` (saída em `verificacao/confere_saida.txt`) → 60 regras, 59 casos, 45 testes, 59 critérios; nenhuma referência sem alvo; nenhum AC duplicado; nenhuma regra com "Trava" sem "Dano".
- **Conferência independente das contas:** `verificacao/verifica.py` (outra implementação: `Decimal` e inteiro escalado por 10⁶, como o `BigInt` do JS; 126 conferências, com paridade e `est + água == base`); saída em `verificacao/verifica_saida.txt` → FALHAS: 0. Um mutante do próprio script (água do K57 trocada pela do K56; semana 38) dá FALHAS: 2.
- **Buscas no código e nos textos:** nomes (`grep -rlw`: Igor em 0 arquivos de `/home/user/sp-tab5`, `/home/user/Safrion-Software-` e `pcm/`; no `v37/`, Davi em 6, Marta em 37 e Helena em 5); IDs livres e herdados (lista em ESPECIFICACAO.md §10); `docs/DECISIONS.md` sem entrada de beneficiamento; regex de `acoes_duplicadas.py:15`; `TK-55xx` só o TK-5531; F10 livre em `dados2.py`.
- **Leitura:** linhas de código e do PRD citadas na especificação (incluindo PRD 10.0 l.4183-4197, 45.x, CMD, DEMO e RN); `pcm/` §3, §4, §10 e §11.
- **Não executado:** nenhum teste do protótipo, nenhum build, nenhum navegador. A simulação da O.S. sem a OB-0104 (log da revisão, fora do repositório) é da revisão, não desta síntese.

## 9. Revisão adversarial aplicada

Fonte: `docs/beneficiamento/verificacao/revisao.json` (42 confirmados; 2 refutados, BEN-R07 e BEN-R10, que não mudaram nada). "Spec" = ESPECIFICACAO.md.

| ID | O que mudou |
|---|---|
| C-01 | Água = base − `benEst`, depois da quantização (§3.4, R-B01); a forma direta nunca é calculada; empate refeito em 6 casas (K52); propriedade `benEst + benAgua == base` e mutante "`benAgua` devolve `benEst`" (§11.4, §11.8) |
| C-02 | Denominador da recuperação = processado − a água da R-F01 (§7); OB-0106 = 99,37 % (K57), com o fechamento na base da saída; KPI de perdas no processado físico |
| C-03 | Critério único de pessoa (§2.3); Davi trocado por Igor (zero ocorrências); Helena e Davi descartados com arquivo:linha; Marta reaproveitada; homônima externa e SU-09 registrados; AC-30 |
| C-04 | Lista dos testes da O.S. sem a OB-0104, com contagem tirada da fonte (§11.5); AC-02; juízo pela linha RESULTADO/FALHAS (§0.4); "(vazio)" testado em Condição (T01) |
| C-05 | L27-013 com o resultado da fonte (COB tipo 6; defeitos 103 > 86) e sem "fora da especificação do PV-028"; PV-028 com classe; classe vazia recusada (R-E05); roteiro do café com reclassificação e pedido tipo 7 (K72) |
| C-06 | Tarefa do proprietário com Concluir e Conferir e sem pedir 10 t (§11.7); roteiro da OB-0114 com Concluir e Conferir; negativo de reserva acima do disponível (K21) e mutante M23; I10 editável até o limite |
| C-07 | Mudanças no EST nomeadas (§0.3, §8): seção por endereço com `hashchange`, balcão para OB, recebedor herdado, link da OB; E02 e E11; mutante M22 |
| C-08 | `benLoteId` com destinos e `seq` (R-A16); `seq` na semente; recusa de ID de outra ordem; K28; café no L39-123 (K70); mutante M17 |
| C-09 | Lote de entrada mantém o físico até o Fechar (§3.5); L38-120 com 48.000 kg; painel "Em processo na <OB>"; U20 |
| C-10 | Lote bloqueado por produto e estágio (§7); "(executado)" só no que rodou |
| C-11 | REQ da OB-0110 com solicitado 600 = `ins.tot`, sugestão 570 confirmada em 600 no histórico (§10.2, K03); invariantes das REQs na U20 |
| C-12 | "Em manutenção" sai; classificação por prefixo (R-A13, U18); 1.200 kg/h sai; nenhuma gravação no `localStorage` da manutenção; dependência do PCM declarada |
| C-13 | Kanban de `processo_os.py:822-842` com `chip_hole`; `bloco` e `kline` de `:36-42`; cópias conhecidas listadas; número de REQ por regra única (U21) |
| C-14 | Caminhos `v37/ferramentas` e `v37/specs`; regex sem acrescentar INSP; `dados_cad.py:67-88`; PRD 4.3 l.289 |
| BEN-PRD-01 | R-A07 só com massa pesada e tolerância; R-F02 simétrica, com "ganho aparente"; S2 nomeado; K10, K61-K63; mutantes M02 e M09 |
| BEN-PRD-02 | Fórmula em matéria seca para várias saídas (R-B01); trava de u_s acima da mistura; K60; propriedade de ordem e de sinal (§11.8) |
| BEN-PRD-03 | Perda só com evidência; R-F07 com alçada sobre dif₀; I7 pergunta pela impureza sem mostrar alvo; ticket TK-5540; caminho legítimo (K57) e contraexemplo (K58); M12 e M13; 2 campos no atrito |
| BEN-PRD-04 | Classe declarada no lote e no pedido; Liberar só com Conforme; reserva por classe; mutantes M07 e M08; concessão em FORA-DE-ESCOPO.md |
| BEN-PRD-05 | `tol_pesado` e `agua` na versão; `benFaixa` (R-F02); CAF-NAT com hipótese não validada só avisa (K70); alçada de Igor em K59; K63; propriedade ±0,1 p.p. |
| BEN-PRD-06 | Reserva Ativa → Cancelada, impedimento derivado, pedido "Em risco", `benCancelarReserva` (R-E06); K22-K24; AC-20 |
| BEN-PRD-07 | Alçada com % e teto em kg por versão; mensagem com o limite que disparou (R-G06); K16 e K74; mutante M10; horas disponíveis como parâmetro do BEN-5 |
| BEN-PRD-08 | "Autorizar rota e liberar" com os eventos CMD-42 e CMD-06 (R-A05); versão da ordem; habilidades de Igor; semente com as duas linhas; mutante M20 |
| BEN-PRD-09 | Fator da saca pelo item do CD-06; saca só com fator (R-B05); "Milho em grão"; umidade medida separada da base comercial; K65 |
| BEN-PRD-10 | Umidade do coco herdada e do beneficiado obrigatória (R-B06); limite de 12 % como aviso; rendimento com umidades e base seca (R-D02, K71); coco a 11,4 % |
| BEN-PRD-11 | Escala do PRD 10.0 (§3.4, R-F04); `BigInt` no JS; BEN-03 conferido pela quantização a 4 do valor guardado; K53; decisão no §1 |
| BEN-PRD-12 | R-A11 com guarda por estado e `cmd` do PCM; reserva ≤ mín(disponível, falta); K30 com fixture; mutantes M06, M18 e M19 |
| BEN-PRD-13 | Rota por produto (código do CD-02), finalidade e estágio (R-A02); produtos misturados recusados; `u_ref` só do milho grão; I1 com produto e estágio; K68 |
| BEN-PRD-14 | Onde se pesa e tara do pallet na versão; `benTara` (R-C01); K19; coluna Pallets só com pesagem no pallet; "pallet de entrega de 60 caixas vazias" |
| BEN-PRD-15 | Fontes corrigidas (R-A03, R-G06, l.289); FL-18 e FL-BEN-01 a 03 citados (§2, §4) e um AC por fluxo; dano nomeado em toda trava (conferido por `confere.py`) |
| BEN-R01 | Situação na inspeção; "Liberar como classe atingida" (R-E02); PV-035 tipo 7; K72; mutantes M07 e M08 |
| BEN-R02 | R-A15 "Estornar registro" e "Corrigir registro"; K11 e K12; mutantes M14 a M16; U11 e U12; ordem encerrada só por ajuste vinculado no BEN-7 |
| BEN-R03 | BEN-1 só com o packing; BEN-2 a BEN-8; OB-0104 fora da O.S. já no BEN-1, com o café só em consulta (§5.3); trava do ativo fora; ordem das frentes e versões decididas antes (§0.1, §0.2); REQ-030 no lugar da REQ-034 |
| BEN-R04 | R-A13 só exibe no BEN-1; trava depois do PCM Bloco 2; I12 só consulta; teste lê `c.man`; Restaurar cobre a Manutenção |
| BEN-R05 | Recebedor da OB = responsável da ordem; balcão; texto do EST por família; E02 com o caso "Paula" |
| BEN-R06 | Em processo explícito (consumo por saída nas rotas por batelada; avanço no Concluir no packing); invariantes da U20; divergência do local do a13 no §10.7 |
| BEN-R08 | §7 com "Onde aparece" e "Bloco"; até quatro por contexto; dois indicadores cortados; descarte conta no indicador de perdas por causa e destino; T09 e AC-29 |
| BEN-R09 | `benEtapas` para a aba e a trava (R-A09); etapas por rota com evidência; U19; mutante M04; medição ao longo do processo como limitação |
| BEN-R11 | I4b com atalho ao saldo; compra com previsão no BEN-2 (I17, K42); LOCAIS do EST da fonte única |
| BEN-R12 | Custo provisório com três parcelas e duas bases (R-F06); K40 e K41; BEN-2 |
| BEN-R13 | Colunas iniciais (≤ 7) por grade e configuráveis (§5.2); "Quem resolve" separado de "Responsável"; Validade fora; planos A e B (P6); T07 e T08 |
| BEN-R14 | Tarefa do proprietário com as ações primárias, sem troca de papel e sem 10 t (§11.7); E01 segue a tarefa |
| BEN-R15 | Uma regra para o número da REQ; ordem sem material sem REQ (U21); mutante M21 |

## 10. Achados aplicados em parte, com motivo

| ID | O que ficou de fora | Motivo |
|---|---|---|
| BEN-R06 | Baixar o físico do lote de entrada a cada saída; mudar o local do a13 no cadastro | Conflito com a C-09 (§5.2). O local do a13 é S4 e a BEN mostra o local do lote; a própria BEN-R06 aceita registrar a divergência |
| BEN-R02 | MP- de estorno | O lote só nasce no Fechar (§1); a trilha fica no registro inverso, no histórico e no MV de caixa |
| BEN-PRD-05 | "Decide Ana" para a diferença de 0,49 % | Contradição interna do item; aplicado "decide Igor" (§5.2) |
| C-12 | Ajudante de teste que injeta a condição no armazenamento | Conflito resolvido no §5.2 (C-12 × BEN-R04) |
| C-07, C-13, BEN-R15 | Funções novas (`cenCustodiaNaEntrega`, `cenReqId`) | Conflito resolvido no §5.2 (uma solução por problema) |
| C-05 | Rastrear o pedido tipo 7 até a OF-100 e o CT-198 (`areas/comercial.py:243, 442`) | Não conferido nesta síntese; o PV-035 entra como sintético, ligado ao destino de `areas/colheita.py:580` |
| BEN-PRD-04 | Liberação por concessão | Política sem dono no PRD (FORA-DE-ESCOPO.md §1) |
| BEN-R13 | Colunas configuráveis como dependência obrigatória | É incremento da TABELAS-FOCO (P6); sem ele, plano B com o desvio registrado |
| BEN-R12 | Custo no bloco de "Recursos" depois do recebimento | Antecipado ao BEN-2, só para o packing |
| BEN-R11 | "Compra só no bloco de custos" | A instrução desta rodada pede compra com previsão; com o PCM 1c ela fica pequena e vai ao BEN-2 |

## 11. Conferência da v2 contra a revisão (05/10/2026)

Conferidos os 42 achados, as contas (§8) e a ordem com o PCM (`pcm/` §11). Na v2 recebida, 38 achados estavam resolvidos e 4 em parte: BEN-R01 (PV-030 sem classe), BEN-R03 (café do BEN-1 com decisão aberta), BEN-R08 (descarte no indicador) e C-06 (sem mutante do limite). As linhas 1, 4, 6 e 8 abaixo os completam. Falhas achadas e corrigidas nesta conferência:

| # | Falha | Correção |
|---|---|---|
| 1 | Reserva da soja (BEN-3) para o PV-030 sem produto, estágio nem classe: pela própria R-E05 seria "Classe não informada" e, pela R-E06, nasceria com expedição impedida | PV-030 com Soja · Grão seco · classe Padrão, da fonte (`areas/comercial.py:310`); reserva nomeada RS-0001; falta 7.500 kg (ESPECIFICACAO.md §10.5) |
| 2 | IDs e contagens do BEN-1 fixos no teste mudariam com as sementes do BEN-3 e do BEN-4 (K28 L39-122, RS-0001 do K21, Kanban da U20) | Expectativas tiradas da semente, com os valores de cada versão (§10.5, §10.6); Kanban do BEN-4 declarado |
| 3 | O F7 do PCM confere 14 requisições depois do restaurar; com a REQ-030 são 15 e o teste quebraria na bateria do §0.4 | F7 do PCM na lista de regressões do 1b (§11.5); `cadp_fix_test.py` 22 → 23 parceiros no BEN-2 (§11.8) |
| 4 | O BEN-1 prometia "café em consulta", mas o §5.3 oferecia Registrar decisão no L27-013 (caminho do BEN-4 sem teste no BEN-1); "grão em consulta" não existe no BEN-1 | Linha "Lote de rota que ainda não é do bloco" no §5.3; E05 confere; limitação reescrita (§11.7) |
| 5 | K15 (BEN-1) lança "Perda identificada" no packing, mas a PACK-FRU v3 não declarava causa de perda | Perda "Avaria no manuseio (pesada)" na rota (§2.4, §10.1) e no K15 |
| 6 | O indicador de perdas por causa ficava vazio no packing: o descarte não estava definido (pendência da BEN-R08) | Descarte e Perda identificada contam por causa e destino; outro destino não (§7, KPI-COM-02 l.4662) |
| 7 | CAF-NAT v1 e CAF-BEN v1 sem `prazo_insp`, que a R-A10 usa no Fechar (K70) | `prazo_insp` +2 d nas duas (§10.1) |
| 8 | Nenhum mutante derrubava o negativo "reserva acima do disponível" pedido pela C-06 | M23 (§11.4); AC-37 vai a M23 |
| 9 | Números e regras repetidos fora da fonte única: valores de §10.1 no §3 deste arquivo; pendências do §4 repetidas no FORA-DE-ESCOPO.md §1-§3; lista de blocos do FORA-DE-ESCOPO.md §4 igual ao ESPECIFICACAO.md §11.8; `v=7` em quatro lugares; escala, data, custo-hora e INSP do §1 repetidos; contagem de REQ no §0.2; regra de recusa no §12; números do K21 no E01; o Concluir no §3.5 (é da R-A08) e as 7 colunas no §5.2 (são da R-G04) | §3 aponta as fontes; §4 fica só com coordenação e aponta o FORA-DE-ESCOPO.md; FORA-DE-ESCOPO.md §4 só com o que não tem bloco (medições do secador foram para o BEN-5 do §11.8; condições do BEN-8 também); `v` só no §0.2; §1 com motivo e referência; demais trocados por referência |


## 12. Implementação do BEN-1 (06/10/2026, branch `claude/v44-beneficiamento`, base `f4121bd`)

Rótulo: **executado** (código, testes de unidade e de navegador; a lista de comandos e resultados está no relatório da rodada). Pedido do
proprietário (05/10/2026): "coloque também o módulo de beneficiamento (frutas, grãos e café) melhorado com tudo que aprendemos". A base mudou
depois da v2 desta especificação: a Colheita (docs/colheita) já cria o lote, o movimento MP-, o pedido e a reserva. Decisões tomadas sem o
proprietário; cada uma vale até ele mudar (AGENTS §2).

| ID | Decisão | Por quê | Como reverter |
|---|---|---|---|
| BEN-D01 | Lote, movimento MP-, pedido e reserva da BEN são os da Produção (`c.producao`, `producao.js`); `c.ben` da spec vira `c.producao.ben` só com inspeções, recibos e sequência de inspeção. Reservar é `prReservar`; o Estoque de produto (PROD) é a tela canônica do produto acabado (R-E08) | Pedido (a) da rodada: sem segundo estoque de produto e sem segunda reserva; um lote, um saldo | Nenhum caminho bom: dois estoques dariam duas verdades |
| BEN-D02 | A decisão do lote (resultado, liberar, liberar como classe atingida, bloquear, reclassificar, destinar) e a reserva ficam no Estoque de produto; a tela Beneficiamento fica só com as ordens. A seção "Decida e reserve os lotes" do §5.1 não nasce | Uma lista de lotes só (a do PROD já reserva); o painel da ordem encerrada leva ao lote | Mover os formulários de `prBenLote` para uma seção da BEN |
| BEN-D03 | *Superada pela BEN-D14 (09/10).* Menu: Produção com 4 itens, Beneficiamento entre Cargas e recebimento e Estoque de produto (ordem do fluxo). Supera o lugar do §0.3 (entre Manutenção e Suprimentos) e o limite de 3 itens da colheita D-01, que pedia decisão do proprietário para o 4º item: o pedido de 05/10 é essa decisão | Pedido explícito do proprietário; Produção já é o grupo do recebido ao estoque | Mover a tupla em `ui37.py` MENU2 |
| BEN-D04 | Caixa do packing com massa declarada: "Caixa de mamão Formosa 10 kg", tara 0,6 kg (sintética), fonte única `dados_cad.EMB_PACK` (o CD-06 lê dela). Substitui a "Caixa de mamão 20 kg" (tara 1,2 kg). Os casos K01-K18 foram refeitos com a caixa de 10 kg: a massa e o bruto não mudam; as caixas dobram (1.140/1.200 na OB-0110, 881 e 584 na OB-0112, CX26-01 com 540 un, custódia 60) | DEC-0510-03 e UNIDADES-DE-MERCADO: formosa em kg ao produtor, caixa de 10 kg no atacado (CEPEA/Ceagesp); a caixa de 20 kg não é unidade de mercado do mamão | Trocar a linha de `EMB_PACK` (as contas leem dela) |
| BEN-D05 | A ordem de processo fica em `c.ordens` com `fam:'BEN'` (como a spec): reaproveita `cenLiberar`, `cenEntregar`, `cenDevolver` e `cenPodeEncerrar`; a O.S. não a lista (ela lista as ordens do registro). O item de caixa leva o grupo Embalagem, e a regra legal de agrotóxico (`osUsoItem`) não se aplica | Uma solução por problema (AGENTS §3.4) | — |
| BEN-D06 | Portão P3 dispensado pelo proprietário para esta noite: `cenProxId(c, col, pre, piso)` é criado em `ben.js` só se o `cenario.js` não tiver (mesma semântica da PCMS-G04: maior + 1 com piso; REQ-041). O recibo da PCMS-G04 é `benMudar(fn)` + `benRecibo` (mesma chave e conteúdo devolve "Já feito" sem gravar nem subir `rev`; outro conteúdo é conflito) e a versão esperada é `o.ver` por ordem. O `cenMudar` do cenário não muda | Instrução (b) da rodada; não redefinir função de outra frente | Quando o PCM 1b integrar, `benMudar` vira `cenMudar(self, fn, cmd)` e a guarda do `cenProxId` some |
| BEN-D07 | ID de lote numa regra só, a da Colheita: `prProxLote` (sequência `c.producao.seq.lote`, piso 130, acima de qualquer lote ou destino de saída da semana). Na semente, o próximo é o **L39-133** (K28 dizia L39-122, antes da Colheita: colheita D-06) | R-A16 e colheita R-11 são o mesmo problema | — |
| BEN-D08 | Os lotes do packing da semente (L38-115 a L38-118, L39-117 a L39-119) entram como saldo de abertura do packing (`abertura`, como o L10-031 da colheita D-17), com a origem descrita em texto; o L26-118 é retorno de cliente bloqueado. O T7 não tem O.S. de colheita no sistema; o que o próprio sistema recebe no Packing pela CARGA entra com origem e carência ao vivo, e o lote em processo da Colheita (L38-132, L39-131, L39-132) abre ordem nova pelo atalho do Estoque de produto | Seed coerente sem inventar O.S. de colheita do T7 (mexeria na O.S. e na COLH) | Semear a O.S. de colheita do T7 e as cargas CG-1205..1207 |
| BEN-D09 | Carência e LC- do lote beneficiado são lidos pela genealogia (`prOrigCampo`): a bula corrigida depois do fechamento bloqueia o lote embalado como bloquearia o de campo (lei) | Colheita R-12: carência lida ao vivo | — |
| BEN-D10 | Quem age é o perfil (`g2perfil`, `cenExige`): Igor (produção) cria, autoriza e executa; Paula (conferência) confere o balanço; Ana (gestora) decide acima da alçada e confirma correção na conferência; Marta (qualidade) ou a agrônoma registra resultado e decide o lote. Novos perfis Igor e Marta em `G2_PERFIS` e no CD-04 (p12, p13, equipe e8). O "Liberar lote" da Colheita passa a exigir o mesmo perfil (Qualidade ou agrônoma) | Instrução (d) da rodada (CTL-3 integrado). A spec dava a conferência a Rui; no CTL-3 o papel de conferência é da Paula | Trocar o papel em `benConferir` |
| BEN-D11 | Data dos registros novos: `CEN_DIA_OP` (26/09/2026), como na Colheita (D-25). A semente foi deslocada para ela: OB-0110 em execução desde 26/09, OB-0112 para 27–28/09, INSP-93 vence hoje, prazo da inspeção do Fechar = 28/09 | Uma "hoje" só para lote, semana e prazo | — |
| BEN-D12 | Simplificações: o estorno não cria linha inversa; o original fica riscado com quem, quando, motivo e o MV `estorno-consumo` (a spec permitia as duas formas). Um lote por classe da ordem (saídas da mesma classe somam no mesmo lote). Custo, compra de caixa, grão, café e a OB-0104 em consulta ficam fora (BEN-2 a BEN-4) | Menos telas e menos registros sem perder rastro | — |
| BEN-D13 | Limitações do Estoque (arquivo em reescrita por outra frente; instrução (c)): a lista "Entregar a" do EST não tem o Igor e a linha da OB mostra o link da O.S.; a entrega no balcão é confirmada quando o Igor inicia a ordem (`confirmado:'balcao'`), não no app. O EST não abre seção pelo endereço: o atalho leva ao Estoque | Não editar `areas/processo_estoque.py` | `cenBalcao` e o recebedor herdado na frente Suprimentos simplificado |
| BEN-D14 | (09/10/2026, supera a BEN-D03) Produção com 3 itens: Previsão e colheita · **Recebimento e beneficiamento** · Estoque de produto. O item do meio abre Cargas; Cargas e Beneficiamento são telas irmãs ligadas pela faixa de telas (o componente da Irrigação: navegação, sem número de etapa, com a pendência escrita de cada tela: "1 a pesar", "1 a liberar · 3 lotes a beneficiar"). `MENU_OF` leva o `BEN.dc.html` ao mesmo item do menu | Alinhamento do Codex (ALINHAMENTOS-20261008 §3: "seção de página existente, máximo de três entradas") e colheita D-01 (o 4º item pedia decisão do proprietário; o pedido de 05/10 pede o módulo, não o 4º item). Recebimento e beneficiamento são a execução do packing; o Estoque de produto é o controle. Custo: um toque a mais na tarefa do proprietário (19 → 20, medido) | Voltar a tupla do BEN em `ui37.py` MENU2 e tirar a faixa (`faixa_rec`) |
| BEN-D15 | (09/10/2026) Balanço sem alarme antes da hora: em A liberar e Liberadas mostra "Entrada a processar" e "Diferença e recuperação: apuradas com as saídas pesadas, depois do Iniciar"; em execução com massa a registrar, "Em processo" e "Diferença: apurada no Concluir". `benEmProc` só conta entre o Iniciar e o Concluir. A etapa pendente só fica vermelha na conferência | Antes, a OB-0112 em A liberar mostrava "9.270 kg (100,00 %) acima da faixa" em vermelho: nada tinha sido pesado, o alarme era falso e o próximo passo ficava ambíguo (achado na captura a 390 px, reproduzido no `ben_fluxo_test`). A trava continua no Concluir e no Conferir (R-A08, R-F02) | — |
| BEN-D16 | (09/10/2026, revisão BEN-REV-04) O Reabrir derruba a declaração do Concluir, não a alçada: guarda o maior \|dif₀\| declarado (`o.ben.dif0r`, lido por `benDif0`). Se o Concluir seguinte entra na faixa e aquele \|dif₀\| passou da alçada de quem conclui, a correção fica pendente da gestão (`corr.pend`, "no concluir antes de reabrir"); a correção na conferência (R-F07) usa o mesmo maior \|dif₀\| | Sem isso, reabrir e lançar a perda com qualquer ticket fechava 600 kg (5 %) sem a Ana: a alçada da R-G06 virava opcional (dinheiro e estoque). Lacuna da R-A12 ("a declaração cai"); a decisão final é do revisor (Codex) | Apagar `dif0r` no `benReabrir` |
| BEN-D17 | (09/10/2026, revisão BEN-REV-09) A ordem leva o lote inteiro: a quantidade da entrada é o saldo físico do lote, sem campo a digitar (menos um campo por lote); `benNova` recusa entrada diferente do físico, e carga nova do mesmo dia não soma num lote que já está numa ordem (vira lote novo) | Entrada parcial deixava o lote inteiro "em processo" até o Fechar: o resto não era reservável nem entrava em outra ordem (estoque preso sem motivo). Dividir lote é transferência, fora do BEN-1 | Voltar o campo de kg e contar em processo só os kg da ordem (`prSaldos`) |
| BEN-D18 | (09/10/2026, revisão BEN-REV-08) A ordem roda onde a linha da rota está (`BENC.linhas`: a13 Packing linha 1 → l8 Packing, Santa Rita): local da ordem, balança, caixas (CX26-01) e lotes de saída são desse lugar; a fazenda dona da fruta fica na ordem e nos lotes, e o painel e o histórico dizem "fruta da Lagoa Grande processada na Packing linha 1 · Packing (Santa Rita)" | Antes a OB do L39-131 ficava no Galpão da Lagoa Grande usando a linha, a balança e as caixas da Santa Rita (evidência de pesagem de outro lugar). Recusar a fruta da Lagoa Grande quebraria a tarefa do proprietário (§11.7) sem dano evitado: a semente só tem uma linha. Linha nova por fazenda entra pelo CD-03 | Linha por fazenda em `dados_ben.linhas` |
| BEN-D19 | (09/10/2026, revisão BEN-REV-01/02) Lote de entrada numa ordem liberada e ainda não fechada fica preso a ela (`benPrende`): a Qualidade não decide (Liberar, Bloquear, Reclassificar, Destinar) e a carga que o alimenta não se estorna; o próximo passo aponta a ordem. Em A liberar a ordem é rascunho: a decisão e o estorno passam e a liberação confere de novo. Defesa no Fechar: recusa se o físico de alguma entrada não cobre o que a ordem consome | Dano evitado: a mesma massa em dois destinos (destinada à indústria e embalada; lote de entrada negativo; produto sem origem). Erro de pesagem da carga aparece no balanço da ordem e se justifica com alçada | Tirar `benPrende` de `benDecisoes`, `benDecidir` e `prEstornoImpede` |
| BEN-D20 | (09/10/2026, revisão BEN-REV-03) Carga com avaria (ou fora do íntegro) recebida no local de processo: o lote está em processo pelo local, mas a qualidade do recebimento espera a Qualidade. Sem ordem que o prenda, "Liberar lote · Marta" no Estoque de produto (`prLibProc`, `prLiberarLote` avalia a base) libera essa qualidade; o lote continua fora do vendável e passa a abrir ordem (R-A03). Ordem com Produto em caixa exige ao menos 1 caixa (BEN-REV-05) | Antes cada tela mandava para a outra e o mamão não íntegro da Santa Rita (sempre no l8) nunca chegava ao beneficiamento; ordem com 0 caixa liberava e ficava presa (sem Produto, sem Concluir, sem Cancelar) | Abrir inspeção no recebimento com avaria (alternativa da revisão) |
| BEN-D21 | *Superada pela BEN-D23 (rodada 1 da integração, 09/10): reduzir ao livre escondia a falta e quebrava o balanço.* (09/10/2026, integração na branch única) O valor inicial das caixas da ordem nova é a sugestão dentro do livre no Estoque (`benCaixasPadrao`: o mesmo lote e a mesma conta da liberação, `cenLote`/`cenDisp`); o campo diz a sugestão, o livre e quem traz mais caixas. Acima do livre a ordem nasce, com aviso no campo e na criação de que a liberação fica impedida até o Estoque ter as caixas | A sugestão do L39-132 (1.169 un) passava das 540 livres: a ordem criada com o valor inicial nunca liberava e o roteiro do proprietário falhava no passo 1 (achado da integração) | `benCaixasPadrao` devolve a sugestão |
| BEN-D22 | (09/10/2026, integração na branch única) "Cancelar a ordem" só em A liberar (rascunho: nada autorizado nem reservado, DEC-2609-13), por quem cria (Igor) ou pela gestão, com motivo; a ordem vai para Canceladas (fora do quadro de 5 fases, como a O.S.; na lista por último, só consulta), grava quem, quando e o motivo, e as entradas voltam a abrir ordem. Traz do BEN-6 só a Cancelada de A liberar; cancelar ordem liberada (reserva e entrega) continua no BEN-6 | Ordem em A liberar que não liberava (caixas acima do livre; entrada que mudou com o estorno da carga, que a BEN-D19 permite) prendia o lote perecível sem saída: sem Cancelar, sem editar e sem incluir entrada (achado da integração; mesma classe do BEN-REV-05) | Tirar `benCancelar` e a secundária do painel |
| BEN-D23 | (09/10/2026, rodada 1 da integração, direção do Codex 6089909749) As caixas da ordem nova são a **necessidade da rota** (⌈entrada × fração vendável ÷ massa da caixa⌉), nunca reduzidas ao livre: `benCaixasPadrao` devolve a sugestão. A falta de caixa é impedimento da liberação com quem resolve (almoxarife) e a saída real que cobrir a falta: a sobra em custódia de outra ordem (Receba devoluções) ou a nota de caixas a conferir (Confira recebimentos), `benCaixasRec`. Para o roteiro sintético, a semente do BEN traz o pedido PC-096 (Embalagens Açu, 1.200 un) e a NF 7731 que chegou ao packing (lote CX26-02, Packing), lidos pelo Estoque (`_pedidos`/`_notas`, unidade do pedido nos campos, Packing nos locais, embalagem sem validade, Igor no "Entregar a") e pelo BEN (`BENC.nfcx`; a nota conferida sai da lista). Sem nota nem sobra, a falta diz que a compra de caixa é do BEN-2 e oferece Cancelar a ordem (BEN-D22) | Com 540 caixas no L39-132 a OB liberava, embalava 5.400 de 12.300 kg, o Estoque recusava mais caixas e o Fechar zerava o lote com 6.900 kg de "diferença" (no L39-131, 99 %): perda fictícia no balanço e no estoque (S2 da reverificação). Evidência: `ben_unit.js` U39a-f, U25d, U40d; mutantes M58, M63, M64; `ben_fluxo_test.py roteiro` e `roteiro390` (1440 e 390 com toque real: criar com 1.169, impedimento com quem resolve, Rui confere a NF 7731, liberar, entregar, saídas, conferir e fechar 12.300 kg com diferença 0, sem justificativa nem perda). Compras e Suprimentos não listam o PC-096 (a compra de caixa é do BEN-2; não foi ampliado agora) | Voltar `cx: sug` para o livre em `benCaixasPadrao` (não recomendado: volta o S2); tirar `PEDIDOS_CX`/`NFS_CX` de `dados_ben.py` e `_pedidos`/`_notas` de `areas/processo_estoque.py` |
| BEN-D24 | (09/10/2026, rodada 1 da integração, S3) Falta de caixa durante a execução se resolve pelo mecanismo de requisição existente: **"Pedir mais caixas"** (secundária do painel em execução) faz o complemento da mesma REQ (`benComplementar`): reserva no Estoque com movimento de reserva, soma à REQ e às caixas da ordem, linha no histórico, recibo pela chave de quem pede e versão esperada; o Estoque entrega no balcão (Entregue por O.S.) e as caixas viram custódia. Sai do lote da REQ; se ele não tem caixa livre e a ordem não tem caixa em custódia nem a entregar, o item passa ao lote com caixas livres (a devolução volta a ele); com caixa em custódia, a recusa manda usá-la antes. A recusa por custódia diz a saída: a entrega pendente no balcão ou "Pedir mais caixas" | A recusa mandava "pedir no Estoque" e o Estoque recusava ("Acima do saldo a entregar: 0 un") mesmo com caixas livres: a fruta que rendeu mais ficava sem embalar e virava diferença (perda fictícia) ou justificativa. Evidência: `ben_unit.js` U41a-h, U23a; mutantes M65-M67; `ben_fluxo_test.py complemento` (recusa com a saída, complemento com toque duplo gravando uma vez, entrega no balcão e balanço com diferença 0). Não amplia o BEN-2 (compra) nem o BEN-6 (cancelar ordem liberada) | Tirar `benComplementar`, a secundária e o modo `caixas` do painel; voltar a recusa antiga (não recomendado: volta o beco sem saída) |
| BEN-D25 | (09/10/2026, rodada 1 da integração, S3) Repetição do toque absorvida no painel do Beneficiamento (`bnGuarda`): até 400 ms depois de uma ação do painel (ou com o contador de cliques do navegador em 2 ou mais), o toque seguinte não roda; o aviso repete o recibo do primeiro ("Já feito: …"). Vale para a primária, as secundárias, as ações das linhas, o fechar e a abertura da ordem | O 2º clique de um clique duplo em "Autorizar rota e liberar" caía na primária seguinte e iniciava o processo sem a pessoa decidir (e depois do "Criar ordem" cairia em "Autorizar rota e liberar"). O comando repetido já era "Já feito" pelo recibo; o defeito era o toque cair em outro comando. 400 ms fica abaixo do intervalo dos toques deliberados medidos nos testes (≥ 450 ms) e acima do toque duplo (≈ 120 ms). Evidência: `ben_fluxo_test.py duplo` (mouse a 1440 com clickCount 1 e 2, toque a 390): antes "Em execução" com "Iniciada" no histórico; agora Liberadas, uma liberação, o aviso repete o recibo | Tirar `bnGuarda` do `EXTRAVALS` e do `bnRun` |
