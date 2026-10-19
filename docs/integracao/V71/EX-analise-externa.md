# Análise externa do protótipo (16/10/2026): EX-01 a EX-31

## Origem e limites

O proprietário colou em 16/10/2026, no canal do Claude, uma análise feita por uma sessão do Claude fora do repositório.

**Objeto analisado:** o artefato publicado, versão 1792123204-c09d (fonte a156f83), com 148 telas abertas no estado inicial.

**Limites declarados pela própria análise:**
- modais e passos seguintes não foram abertos;
- cliques e campos são estimativas, salvo onde aparece "linha de base";
- os dados sintéticos foram tratados como intencionais;
- o repositório pode estar à frente da versão publicada.

**Como esta análise entra no trabalho:** é insumo, não requisito. Prevalecem o PRD, o NAV/DS, o protocolo e as decisões registradas.

**Método pedido pelo proprietário:**
1. O Claude valida cada item no código, no PRD e no NAV/DS: Confirmado, Refutado ou Já resolvido.
2. Para cada item confirmado, o Claude decide: Adotar, Adaptar ou Rejeitar.
3. O Codex classifica de forma independente, sem ver a classificação do Claude, e aponta o que a análise errou ou deixou de fora.
4. Divergência se resolve por fonte ou por reprodução. O Codex decide o escopo e o registra no checkpoint.

**Critério para entrar (os quatro):**
- ganho de gestão ou menos cliques, digitação, etapas e retrabalho em tarefa frequente, com medida antes/depois;
- preserva estado, unidade, aprovação, rastreabilidade, acessibilidade e as decisões fixas;
- cabe no escopo vigente, ou justifica a mudança de PRD com evidência;
- custo proporcional ao ganho.

## Diagnóstico da análise (nota de valor de gestão / simplicidade, 0 a 5)

| Área | Notas |
|---|---|
| Agronomia | 4 / 2,5 |
| Cadastros | 3,5 / 4 |
| Planejamento | 4 / 2 |
| Entrada e pendências | 3 / 3 |
| Painéis | 3 / 2 |
| Execução de O.S. | 3 / 2 |
| App de campo | 3 / 3 |
| Irrigação | 4 / 3 |
| Suprimentos e compras | 3,5 / 2 |
| Estoque | 4 / 2,5 |
| Manutenção | 2 / 3 |
| Colheita e pós-colheita | 3 / 2 |
| Comercial e logística | 3 / 2 |
| Gestão e finanças | 3,5 / 3 |
| Plataforma | 3 / 3 |

**Pontos fracos apontados:**
- (a) duas gerações de telas convivendo;
- (b) dados que se contradizem entre telas;
- (c) poucos indicadores de resultado;
- (d) digitação de dados que o sistema já tem;
- (e) cerca de 20 telas sem primária, e outras com uma primária que não resolve o estado mostrado no topo.

## Preservar

- **Faixa de contexto do detalhe:** "VEIO DE → ESTÁ AQUI → FALTA → PRÓXIMA AÇÃO".
- **Próximo passo:** com verbo e responsável.
- **Automação como proposta,** nunca execução sem a pessoa.
- **Idempotência e rastreio.**
- **Cálculo com origem visível.**
- **Honestidade do dado:** ausente ≠ zero, parcial, hipótese.
- **Cadeia de decisão:** VIS → DIA → REC → NEC → OS → EF, com trava legal que já mostra a alternativa.
- **Offline com recibo em três estados** e custódia.

## Itens

### Onda A · Fundação

**EX-01 · Dados coerentes entre telas.** Corrigir as contradições e criar um teste que compare contadores e valores da mesma entidade em todas as telas, com aceite em 0 divergências. Contradições citadas:

- **Colheita:** previsão de soja 26/27 em 68.180 sc na COLH × 51.280 sc em GE-01, VE-05 e GE-08. O IV soma safras: 106.600 = 38.420 + 68.180.
- **O.S.:**
  - OS-0430 aparece como "Falta máquina" × "Sem pendência";
  - contador "3 impedidas" × "2" (OS × CA-01).
- **Manutenção:** MA mostra "Ordens 0" com 4 OMs na lista.
- **Estoque:**
  - PSUP "quarentena 1" × SU-03 "retidos 3";
  - SU-03 mostra "conflito de reserva 0" e tem uma linha "Reserva em conflito";
  - OS-0417 aparece com lote M26-05 × M26-07.
- **Compras:**
  - SOL-2026-07 em três estados (CMP, SU-04, SU-01);
  - "pedir até" diverge entre SU-01 e IC;
  - MAP em 62.500 × 79.500 kg;
  - alçada "até R$ 300 mil" numa compra de R$ 360.905.
- **Vendas:**
  - recebíveis divergem entre VE-04 e GE-05;
  - PV-037 entregue, mas ausente em GE-05;
  - VD-2101 sem venda.
- **Irrigação:**
  - IR-02 e IR-03 dizem "sem pendências", mas IR-03det mostra "1 conflito";
  - Pivô 2 com 9,8 × 11,2 mm;
  - OS-0601 × OS-0419.
- **Máquinas:**
  - PJ-3030 com tanque de 3.000 × 2.000 L;
  - OS-0424 com Trator 04 × 03.
- **Laudos e talhões:**
  - K do LAU-2043 em mg/dm³ (AG-02) × cmolc/dm³ (AG-03det);
  - "Pivô 22" × "PV22".
- **Cabeçalho × chip:** divergem em PROD, BEN e EST.
- **Gestão:** GE-01 mostra R$ 3,67 × 3,68 mi.

**EX-02 · Uma entidade, uma listagem e um detalhe.** Consolidar telas com redirecionamento, como já foi feito em MA-01..05 → MA:

- **Colheita:** CO-01..05 e CO-07 → COLH, CARGA, BEN e PROD. CO-05det vira detalhe de BEN; CO-06 e CO-06det viram seção de qualidade do lote.
- **Vendas:** VE-01, 02, 04 e 05 → VEN e IV, com VE-04det como detalhe. Antes, migrar PV-026..029 e PV-032..034.
- **Logística:** LO-01..03 → EXPED (agenda, fila, docas), com LO-02det como detalhe.
- **Estoque:** SU-03 e SU-06..09 → EST, com abas por entidade.
- **Compras:** CMP, SU-01, SU-04, SU-05 e IC → Compras (solicitações por estado; detalhe com Demanda, Comparação, Pedido e Cargas; "quando comprar" vira coluna). SU-02 vai para configuração.
- **Planejamento:** SAF e PL-01 → uma listagem de safras, com PL-02, 03 e 06 como seções do detalhe.
- **O.S.:** OS e CA-01 → uma listagem com visões.
- **Entrada:** IN-01 e IN-03 → Meu dia (Lista | Semana).
- **Irrigação:** IR-01..03 → uma listagem por setor.
- **App de campo:** MB-02 e a abertura do MB-03 deixam de repetir os cartões do MB-01.

Antes de remover qualquer tela, confirmar no registro que ela é versão antiga, e não variante deliberada.

**EX-03 · Vocabulário único** (complementa UX-01):
- um verbo por ação (apontamento e avanço);
- "Próxima ação" em todas as listagens;
- ciclo do plano com no máximo 4 estados;
- siglas sem colisão: PV, OC, ROM × RM, COT × NEG;
- nenhum código interno na tela (CMD-06, DEC-09, RN-039, PRD 41, PR #58, "(VE-04)");
- nome do menu = título = trilha, com raiz única.

**EX-04 · Contexto Fazenda · Safra herdado em toda tela** (P27).
- Hoje abrem em "Todas", "Nenhuma safra escolhida" ou outra fazenda: IN-04, PAGR, PCOM, PMAN, PSUP, SAF, PA, AG-02..04, COLH, CMP e MB-07.
- A etapa "Escolha a safra" sai do CMP e do SAF.

**EX-05 · A primária resolve o estado mostrado no topo** (UX-02).
- **Sem primária:** IN-04, AG-03, AG-05, AG-06, IN-02, PAGR, SAF, PL-05, MA, CMP, IC, CO-04, BEN, PROD, IV, VE-03, GE-01, GE-06det, IR-03, IR-04, MB-02, MB-05, MB-07, PT-02, PT-04..07.
- **Primária que não resolve o estado:** SU-02, SU-03, SU-08, VEN, VE-01, VE-06, CO-02, CO-06, CD-07, CA-01x, GE-08, ON-01, PT-02det, PT-04det.
- **Ação ativa mesmo com bloqueio:** GE-03 "Fechar competência", CA-04 "Encerrar OS-0417", SU-07 "Confirmar entrega" em REQ impedida.
- **Decisão neutra:** CO-06det tem Liberar e Bloquear com o mesmo peso.

### Onda B · Entrada mínima

**EX-06 · Turno por exceção** (MB-03, MB-10).
- O turno abre preenchido.
- "Fechar turno como previsto" em 1 toque.
- GPS ou telemetria em contradição com o apontado é sinalizado.
- Medida: de 4 toques e 2 números para 2 toques e 0 números.

**EX-07 · Paradas com causa** (MB-03, MB-08, CA-02).
- Chip de motivo, com início e fim.
- A parada vira ocorrência ligada à O.S. e à máquina.
- O sistema propõe "Reprogramar saldo".
- Resultado: ha/h real, eficiência de campo e Pareto de paradas. A CA-02 mostra cerca de 19 % (5,6 × 28,8 ha/h), número que não aparece em nenhuma tela.

**EX-08 · Condições de aplicação e calibração** (OS-0424-app, MB-02det, MB-03, AG-04, AG-04det).
- Na ficha: vento, temperatura, UR, Delta T, reentrada e carência.
- Checagem ao iniciar o turno, com alerta ou bloqueio e exceção pelo RT.
- Calibração: vazão por bico × taxa. Na OS-0424, cerca de −11 % de calda.

**EX-09 · Abastecer com 1 número** (MB-09). O horímetro vem da telemetria ou do turno; tanque e lote vêm do último uso. Hoje são 5 toques e 2 números.

**EX-10 · Conferência por exceção** (CA-02; P39).
- Conferir em massa o que está dentro da tolerância.
- Turno divergente destacado, com Aceitar ou Devolver.
- "Liberar" e o roteiro vão para a fila do UX-06.

**EX-11 · Recebimento de NF** (SU-06/EST): UX-09 mais a prévia do XML (item, lote, validade, preço × pedido), aceita com "Confere com a NF".

**EX-12 · Romaneio de entrada** (CARGA).
- Pesagem → Classificar → Fechar.
- Bruto e tara automáticos; a pessoa digita só umidade e impureza.
- Líquido corrigido com a origem à vista.
- Medida: de 12 cliques e 5 campos para cerca de 4 toques e 2 números.

**EX-13 · Laudo importado** (AG-02): prévia antes de gravar e conversão visível. Os campos digitados por laudo passam de 12 a 15 para 0. Ler laudo em PDF depende de IA.

**EX-14 · Nascer do anterior** (SAF, PL-01, PA): "Copiar safra 2025/26", com rotação e meta pela média, e "Duplicar plano".

**EX-15 · MIP até a decisão** (AG-01..04).
- Vistoria acima do NC gera rascunho de recomendação e de O.S.
- O produto sugerido traz mecanismo de ação diferente do último aplicado, saldo em estoque, dose de bula e carência.
- Mapa de calor na AG-01.
- Pós-aplicação agendada (7 DAA).
- A aprovação individual se mantém.

**EX-16 · Rascunhos automáticos em suprimentos e manutenção.**
- Falta firme ou mínimo/máximo gera solicitação, e o "Comprar agora" do IC também.
- O horímetro projetado gera OM preventiva com kit reservado.
- Achado crítico nasce como OM.
- O.S. concluída sugere a devolução.
- FEFO pré-selecionado na separação.

**EX-17 · Um lançamento produz todos os efeitos.**
- A entrega baixa o contrato e cria o título a receber.
- A medição de frete cria o título a pagar.
- Conciliação bancária por arquivo de retorno ou extrato.
- A unidade da saca vem do contrato.
- Proposta aceita vira pedido.

### Onda C · Gestão que gera resultado

**EX-18 · Janela agronômica como eixo do PCP** (PL-02..04, PAGR): folga por operação, capacidade semanal, % de área dentro da janela, término pelo ha/h real e reprogramação sugerida.

**EX-19 · Custo por saca e margem por hectare por talhão,** do plano ao realizado (PL-01, PA, GE-01, PCOM).

**EX-20 · Previsão móvel única de produção** (COLH).

**EX-21 · Política de comercialização** (IV, VEN): % vendido × custo coberto, gatilho de preço gera rascunho de oferta, trava e basis. Fechar preço continua humano.

**EX-22 · Caixa de 13 semanas** (GE-04).

**EX-23 · Suprimentos com indicadores de resultado:** lead time, cobertura antes da janela, ruptura, economia, validade, capital sem demanda e inventário cíclico ABC.

**EX-24 · PCM com indicadores de resultado** (MA): disponibilidade na janela, MTBF/MTTR, % de preventiva, backlog em horas, custo por hora e kit por plano.

**EX-25 · Irrigação:** chuva no balanço, fora da ponta respeitando a outorga, alerta de pressão e vazão.

**EX-26 · Painéis por exceção** (PAGR, PMAN, PSUP, IN-04): número que abre a lista, sem somas repetidas nem linhas "nada a fazer", e cerca de 6 indicadores com meta e tendência.

**EX-27 · Talhão como centro** (CD-01det): seções Operações, Monitoramento, Solo, Custo e margem e Linha do tempo.

**EX-28 · Insumo ligado ao registro do Agrofit** (CD-06 → AG-07/AG-04): registro, concentração, ingrediente ativo, mecanismo de ação, carência e dose de bula; alerta de repetição de mecanismo; preço da última NF.

**EX-29 · Cadastros alimentados pelo realizado** (CD-03, CD-08): ha/h e R$/h recalculados; desvio vira proposta.

**EX-30 · Plataforma** (CF-01, CF-04, ON-01det, ON-01, BO-01):
- escopo por fazenda e alçadas;
- auditoria com antes → depois;
- "Importar os prontos";
- tirar "Assistente de IA · 200 interações".

**EX-31 · Fila e entrada** (IN-01, IN-02): idade e prioridade por impacto; Aprovações como caixa única, sem seleção em lote; visões salvas.

## Decisões do proprietário apontadas pela análise (não implantar sem aceite registrado)

1. Aceite automático do turno dentro da tolerância (EX-10).
2. IR-03det mostra uma O.S. de irrigação "liberada sem toque humano" e o MB-08x mostra "encerrada automaticamente": isso é compatível com a aprovação individual?
3. PL-04 "Liberar prontas" não pode embutir aprovação em lote.
4. Bloqueio por clima: alerta ou bloqueio, e quem libera a exceção (EX-08).
5. Alçada mínima para perda pequena (PE-012, cerca de R$ 195) e "Aprovar e emitir pedido" em uma ação abaixo da alçada.
6. Automações que dependem de IA ficam desligadas até a estimativa de custo (DEC-1610-11).
