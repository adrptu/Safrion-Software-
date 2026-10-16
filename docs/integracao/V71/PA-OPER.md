# PA-OPER · Plano agronômico seccionado por operação, uma operação por vez

> Proprietário, 16/10/2026: "Ao fazer planos agronômicos e planejar a safra, vamos tentar fazer algo mais seccionado por operação com suas especificidades e foco total uma coisa bem feita por vez. Chegue ao melhor método possível de fazer isso junto com Códex e Gemini e implemente."

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: PA-OPER / o agrônomo monta e confere o plano uma operação por vez, cada uma só com os campos que importam a ela; Planejar safra, O.S., fichas e demanda usam exatamente esses números (fonte única) / agrônomo RT; PCP, caldeiro e operador recebem o resultado
Requisitos do PRD e fora do escopo: AG-05, PL-02, FO-04/21/27/28, RF-AGR-004/007, RF-PLN-001, RN-007/016/017, CMD-02, AGR-013/015/016/025/027/028, FX-001..008, 39.1/39.3, 40 (AJUSTE), 41.3–41.6, APROV-02/04, 44.1 (PCP), 52 (REND), DEC-2609-02/07/10/14, DEC-1610-03; fora: §Fora do escopo
Autor / revisor / integrador: Claude / Codex (produto e QA) e Gemini (lente agronômica, pelo conector do Codex) / Codex (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: ponta de claude/v44-v69-mapa depois do PR #77 (EX-38) integrado, sem congelar a685f5e e sem recodificar os campos da EX-38; a combinação de arquivos com o Codex só depois da autoria dele entregue e revista / areas/processo_planos.py, dados2.py, dados_lagoa_safra.py, areas/cad_culturas.py (CD-08), dados_cad.py, operacoes.js (novo), safra.js, areas/processo_safra.py, areas/processo_os.py, areas/mobile.py, areas/os_campo.py, testes novos pa_oper_unit.js e pa_oper_test.py
Aceite e comando de verificação: P1–P19 e K1–K7 abaixo / node pa_oper_unit.js; python3 -B pa_oper_test.py; ANTES=<_render da ponta antes da F1, de árvore limpa> para a contraprova; mais os testes de §Testes
Estado / impedimento / próximo passo: especificado, sem código; revisado pelo Codex e pelo Gemini em 16/10 (§Revisão), achados tratados nesta versão; implementação em 4 fatias (decisão 10), a F1 depois da EX-38 integrada e da frente Cadastros
```

## Revisão (Codex e Gemini)

- **Codex:** produto, aceite, cliques e QA.
- **Gemini, pelo conector do Codex:** lente agronômica.
  - Campos de cada família.
  - O que é trava (lei, bula, dose) e o que é só aviso.
  - Fórmulas de sementes, cargas, nutrientes e concentração.
  - Operações que faltam.
- **Texto enviado:** este arquivo, na versão do envio. O Codex registra na rodada, no ato do envio:
  - o SHA-256 do texto exato (`sha256sum docs/integracao/V71/PA-OPER.md`);
  - data, modelo e parecer.
- **Peso das decisões abaixo:** são proposta do autor. Viram decisões dos agentes só depois dos dois pareceres escritos (§3). Cada achado é aceito, ajustado ou recusado com fundamento.

| Revisor | SHA-256 do texto revisado | Data | Parecer |
|---|---|---|---|
| Codex | `325a2bf096cd49014b166d4586630c6452cf53de1df45acd86cca49847f9d773` (d3b266f, 342 linhas) | 16/10/2026 | Direção aceita: operação como organização, herança, atividade como unidade da O.S., nenhuma aprovação automática da O.S. A F1 depende dos ajustes 1–8 abaixo, sem ampliar o escopo. Comentário 6219314422 no PR #47. |
| Gemini (conector do Codex) | o mesmo texto; requisição com SHA-256 `5dba573ea505a4134962a9da149a09bd8f9847cabaa32e475e4a5858957d391c` | 16/10/2026, 15:51:37Z | Modelo `gemini-3.1-pro-preview`, esforço HIGH; resposta `CkjSatGdKM-gn_APxo3L2AY`, fim STOP, 16.728 tokens. Uma consulta efetiva, sem ferramentas nem fontes externas, sem testes. Achados 1–4 incorporados pelo Codex (abaixo, itens 2, 3, 6 e 4); o 5 foi recusado. O tom de aprovação da resposta não conta como prova. Brutos com o Codex em `work/dupla-20261013/pa-oper-20261016/`. |

**Tratamento dos achados** (esta versão; os testes e as contraprovas continuam especificados, não executados):

| # | Achado (sev.) | Tratamento |
|---|---|---|
| 1 | "Salvar alterações" aprovava sem intenção explícita, e o impedimento bloqueava a única gravação (S2) | **Aceito.** O rascunho se guarda sozinho, mesmo incompleto ou inválido, com recibo. "Publicar versão vN" é ação separada, de quem tem o papel (AG-05, CMD-02). Pronta e Pendente falam de completude, não de aprovação. Decisões 5 e 9, telas, P7, P12 e P17. |
| 2 | TS por 100 mil sementes calculado como se fosse por 100 kg (S2) | **Aceito.** A conta se bifurca pela unidade da prescrição; contagem e massa ficam separadas. Sem PMS ainda se calcula a contagem; só a conversão para massa espera. TS industrial nunca entra duas vezes. Tabela de famílias e P6. |
| 3 | Vazão por bico: alvo e disponível são fontes distintas (S2) | **Aceito.** Alvo = volume × velocidade × espaçamento ÷ 600, com a velocidade do REND (sem campo duplicado); disponível vem da curva ponta × pressão; a tela compara. Sem velocidade ou curva: "desconhecido", nunca padrão. Fluxo O.S. e P18. Fonte: Embrapa, [ID10895](https://ainfo.cnptia.embrapa.br/digital/bitstream/doc/543661/1/ID10895.pdf), consultada pelo Codex em 16/10. |
| 4 | Instrução emitida e histórico mudavam ao editar cadastro; a migração inseria 100 L/ha (S2) | **Aceito.** A O.S. guarda o retrato dos parâmetros técnicos e das fontes. Só uma troca explícita de conjunto ou lote, dentro do envelope, refaz o preparo ainda não executado. Semente de demonstração ≠ migração de rascunho salvo. Fluxo O.S., Migração, P4, P13 e P19. |
| 5 | A F1 prometia a instrução vinda do plano, mas o transporte da versão ficava na F2 (S2) | **Aceito.** A F1 leva o transporte mínimo: o cultivo referencia a versão publicada e a geração da O.S. lê a instrução dela. A F2 fica com a etapa 2 e as sementes. Decisão 10. |
| 6 | Concentração: solução-estoque × tanque nominal; a mensagem mandava pôr 8.182 L num tanque de 2.000 L (S2) | **Aceito.** Nome "solução-estoque" (volume útil preparado). A saída divide em preparos dentro da capacidade, com RT, compatibilidade e condição da fonte explícitas; sem receita química universal. Tabela de famílias e P9. |
| 7 | Precisão e redação dos aceites | **Aceito.** P2 (a próxima de Pulverização é TS), P4 (5 de 30 ha + 1 de 10 ha), arredondar só na apresentação (9.035,294… kg, não 56,47 × 160), germinação 0, ausente ou fora de 0–100 nunca divide nem vira padrão. |
| 8 | UX e escopo: estado ao trocar operação, Esc, texto visível no toque, sem menu por família; ZARC não é proibição universal; não repassar perguntas antes de confrontar decisões existentes | **Aceito.** Decisão 6 e telas. ZARC vira aviso com a consequência para a elegibilidade (Proagro e subvenção), pela cobertura e portaria vigente, sem bloqueio. A pergunta 1 é resolvida pelo PRD (AG-05 e CMD-02: publicar exige o papel). A 2 passa a decisão dos agentes. A 3 só volta ao proprietário se a base for paga. |
| G5 | Gemini: assumir pureza de 100 % ou embuti-la no fator de estabelecimento | **Recusado** (Codex e Claude). Pureza e fator de campo são conceitos distintos; precisam de fonte e do RT. O fator de campo continua opcional e explícito, sem padrão. |

## Situação em 16/10 (lida no código em a685f5e)

| Parte | Hoje |
|---|---|
| **Plano** | Lista de atividades `{id, nome, op, gatilho, produtos (grupo, dose/ha, un, preço)}` (`dados2.py:22-61`, `dados_lagoa_safra.py:21-53`). Não tem máquina, janela, aprovador nem campo próprio por operação. |
| **Operação** | É só um nome. Vem de `D2.CONJ` (`dados2.py:89-98`; Lagoa em `dados_lagoa_safra.py:55-59`). O CD-08 guarda nome, processo e atividades usuais (`areas/cad_culturas.py:205-250`). `catalogo_operacoes.py` tem valores técnicos em texto e só é importado, sem uso (`engine.py:153`). |
| **Tela Planos agronômicos** | Lista → detalhe. Filtro por operação em chips com ícone (`areas/processo_planos.py:186-194, 273`). Cartões ou Tabela com DAP, Atividade, Insumos e Custo/ha (`:265`). Painel Operação → Atividade → gatilho (`:328-392`). Dose editada na tabela. Os campos são iguais para toda operação. |
| **Versão e aprovação** | O rascunho vira vN em "Salvar alterações" (`:428-458`). Não há aprovador. A versão não chega ao Planejar safra (`:460`, `PA_PROTO`). |
| **Planejar safra** | Quatro etapas (`areas/processo_safra.py:17`).<br>• Etapa 2: escolhe o plano (`:62-63`) e ajusta insumos por cultivo (`safra.js:1846-2010`).<br>• Etapa 3: árvore Operação › atividade › talhão e formulário Rendimento (`processo_safra.py:148-201`).<br>• Etapa 4: demanda (`:238-246`). |
| **Semente** | kg/ha digitado no plano (52 kg/ha em `dados2.py:28`), com o nome pela variedade do cultivo (`safra.js:20`). Sem população, PMS nem germinação. |
| **Campos por operação fora do plano** | • Cadastro: tanque e barra do pulverizador, linhas e espaçamento da plantadeira (`areas/cad_ativos_pessoas.py:79-82`); a05 tem 3.000 L e a06 tem 0,5 m (`dados_cad.py:74-75`).<br>• O.S.: cargas com 3.000 L e 100 L/ha fixos no código (`areas/processo_os.py:789-792`).<br>• App: 2.000 L e 120 L/ha digitados (`areas/mobile.py:72-73`).<br>• Ficha: tanque, vazão e bico digitados (`areas/os_campo.py:24`).<br>• Colheita: umidade e impureza só na carga (`areas/colheita.py:104`). Lâmina só na irrigação. |
| **Bula e carência** | Já existem, mas fora do plano: AG-07 tem registro, dose, carência, máximo de aplicações, reentrada e grupo de modo de ação, com os demonstrativos marcados (`agrofit_dados.py:26-37, 118`). O serviço de carência da colheita está em `dados_carencia.py`. O plano não consulta nenhum dos dois. |
| **Achado ligado** | EX-38 (S2): a mesma grandeza de execução sai de quatro fontes digitadas; calda e bico/pressão não têm fonte; MAP e KCl aparecem em duas instruções para a mesma ordem (`docs/integracao/V71/ex-validacao-claude/EX-38-39.md`). |

## Referências (AGENTS §3.3)

Estar no mercado não prova que a regra está certa. A decisão é por prática.

| Referência | Prática | Decisão | Conferência |
|---|---|---|---|
| John Deere Operations Center · Work Planner ([link](https://deere.com/en/technology-products/precision-ag-technology/operations-center/work-planner)) | Plano por tipo de operação (preparo, plantio, aplicação, colheita), enviado às máquinas | **Adotar** a seção por tipo de operação. **Adiar** o envio ao terminal, porque exige conta e contrato do proprietário. | Levantada em 16/10 pela sessão principal. Neste agente, a página trouxe só o título: reconferir. |
| Aegro · "Como planejar atividades" ([link](https://aegro.com.br/suporte/safras/como-planejar-atividades-no-aegro/)) | Tipo da atividade primeiro. Calculadora de sementes (plantas/ha, PMS, germinação e vigor → quantidade/ha e total) | **Adotar** o tipo primeiro (já é a DEC-2609-02) e a conta de sementes. **Adaptar:** o vigor não multiplica a conta automaticamente; o fator de campo vem do protocolo do RT, e o lote real refaz a conta na liberação. | Conferida em 16/10 (página atualizada em 21/09/2026). |
| Agworld Planning ([link](https://www.agworld.com/products/planning)) | Plano por talhão; modelos copiados entre talhões e safras; checklist por talhão; custos por categoria | **Adotar:** já existe como modelo → cultivo com ajuste local (cap. 40). **Adaptar** o checklist como estado calculado por operação. **Descartar** a edição colaborativa sem aprovação: a versão é do RT. | Conferida em 16/10. |
| xarvio · Seeding ([link](https://www.xarvio.com/ca/en/products/field-manager/seeding.html)) | População por zona e prescrição de semeadura | **Adiar** até o arquivo de prescrição homologado (SOLO-VRA). | Respondeu 404 em 16/10: reconferir. |
| Climate FieldView · fertilidade ([link](https://climate.com/features/nitrogen-monitoring)) | Monitoramento de N e taxa variável | **Adiar.** A adubação por zona segue a SOLO-VRA. | Respondeu 404 em 16/10: reconferir. |

## Decisões propostas (Claude; valem depois dos pareceres)

1. **A operação organiza o plano.**
   - O detalhe mostra uma seção por operação, na ordem em que cada uma começa no ciclo: pela primeira atividade e, no empate, pela fase do CD-08.
   - Dentro da seção, as atividades seguem a ordem do gatilho.
   - A atividade continua sendo a unidade que vira O.S. (DEC-2609-02, FL-AG-05).
2. **Família técnica no cadastro de operações (CD-08).**
   - Cada operação escolhe uma das 9 famílias da tabela abaixo. A família define os campos e as contas da seção.
   - "Outra operação…" exige escolher a família, do mesmo jeito que o APROV-04 exige a do aprovador.
   - A família é estrutura do produto. Valores e limites são dados.
3. **Campos em dois níveis.**
   - O **parâmetro da operação** vale para todas as atividades dela no plano e aparece como "da operação".
   - A **atividade** pode ter valor "próprio", visível e reversível.
   - Mudar o parâmetro uma vez muda todas as atividades herdeiras: é a ação em lote natural.
   - Não é "último valor" (§3.3): é uma decisão técnica gravada na versão.
4. **Nada normativo no código.**
   - **Vêm de cadastro com fonte, edição e vigência:**
     - dados de bula: registro cultura × alvo, dose máxima, carência, reentrada, máximo de aplicações, faixa de volume e condições de aplicação;
     - solubilidade e compatibilidade;
     - zoneamento (ZARC);
     - limites técnicos de referência.
   - No protótipo, esses valores aparecem marcados "demonstração", como a AG-07 já faz (campo `conferido`).
   - Sem dado, o campo fica "sem fonte" e só a ação que depende dele espera (FX-005).
   - Os textos de `catalogo_operacoes.py` (vento, umidade de colheita, 100–150 L/ha) não viram regra. O import sem uso sai de `engine.py:153`.
5. **Estado de cada operação, calculado.** Fala de completude, não de aprovação:
   - **Pronta ✓;**
   - **Pendente •:** faltam campos para gerar a O.S., e a lista diz quais;
   - **Com aviso ⚠;**
   - **Impedida ⛔:** lei ou bula. Impede publicar a versão, nunca guardar o rascunho.
   - O estado da versão ("Rascunho", "Em revisão", "Publicada v6") aparece separado, no cabeçalho.
   - Não há botão "concluir operação": é um clique a menos, e nada fica declarado sem conferência.
6. **Foco sem perder o mapa.**
   - A **faixa de operações** fica sempre no topo, com o estado de cada operação em texto visível, também no toque (não só na dica ou no `aria-label`). Ela reaproveita a peça de filtro por operação que já existe (`paOpChips`). Não há menu por família.
   - Tocar numa operação entra em foco. "Visão geral" volta à linha do tempo de hoje.
   - "‹ anterior" e "próxima ›" só ficam se o K5 provar que ajudam no teclado ou no celular; se duplicarem a faixa sem ganho, saem.
   - O endereço guarda a operação: `#plano=…&op=…`. Foco, rascunho e rolagem se mantêm ao trocar de operação, voltar e recarregar (F5).
   - Esc fecha primeiro o editor ou o painel aberto; só depois volta à visão geral.
7. **Ações em lote por operação,** no ⋯ da seção (MAIS-01), com prévia e Desfazer (AVI-01):
   - deslocar os gatilhos em ± N dias;
   - trocar o produto em todas as atividades da operação. A troca é explícita e confere a bula de novo (40.2).
8. **Um serviço para cada fórmula (ENG-011).**
   - No protótipo, `operacoes.js`; no software real, o pacote de domínio, com decimal (ENG-013).
   - **Contas:**
     - sementes e tratamento de sementes;
     - cargas (41.5) e vazão por bico;
     - nutrientes (AGR-015);
     - g/cova ↔ kg/ha;
     - concentração × solubilidade;
     - conferência de bula pelo gatilho.
   - Plano, Planejar safra, O.S., fichas, app e demanda chamam o mesmo serviço.
   - Cada número tem "Por quê" (fórmula, entradas e origem), com a peça já usada no SOLO.
9. **Rascunho guardado sozinho; publicação explícita (AG-05, CMD-02), sem tocar na aprovação da O.S.**
   - **Rascunho:** cada edição é guardada sozinha, inclusive incompleta ou inválida, com recibo e estado visíveis ("Rascunho guardado 14:32"). Sair e voltar reabre o rascunho com os mesmos erros. Guardar nunca publica.
   - **Publicar versão vN** é a ação explícita, de quem tem o papel com direito de publicar naquela fazenda (AG-05: "publicação exige direitos/papel, revisão e testes"; CMD-02). O papel é configuração por fazenda (P46); o texto não assume "qualquer agrônomo".
   - **Quem não tem o papel** vê "Submeter à revisão" (AG-05). A versão fica "Em revisão", e quem tem o papel tem "Publicar versão vN" e "Devolver". O servidor decide o papel, como no APROV-04.
   - A versão publicada anterior continua vigente até a nova ser publicada. A publicada é imutável. Os cultivos continuam na versão deles (40.3).
   - **Publicar o plano nunca aprova, libera nem pré-autoriza uma O.S.** (DEC-1610-03, FX-006, APROV-05). A revisão da O.S. mostra "igual ao plano vN" ou as diferenças, só como informação.
10. **Uma fatia por vez, também para nós** (§3.1):
    - **F1:** faixa, foco, estados, dois níveis, rascunho e publicação; Pulverização; serviço de cargas e de vazão.
      - **Transporte mínimo da versão:** o plano publicado vai para o cenário compartilhado, o cultivo guarda a referência à versão aplicada, e a geração da O.S. lê a instrução dessa versão (fim do `PA_PROTO` para a O.S.).
      - Só com isso a F1 resolve na origem a EX-38.1 e a R10. Sem isso, o aceite fica pendente e não se diz "resolvido".
      - Os campos que a EX-38 (PR #77) já criou são reaproveitados, não recodificados.
    - **F2:** Plantio e tratamento de sementes; etapa 2 do Planejar safra com o resumo por operação e o ajuste por talhão; demanda de semente.
    - **F3:** Adubação e correção (com a SOLO-VRA) e Fertirrigação.
    - **F4:** Colheita, Tratos e poda, Preparo do solo e Plantio de mudas.
    - A F1 entra depois da EX-38 integrada e da frente Cadastros. As demais respeitam o teto de três frentes (§3.6).

## Seções por operação

Níveis dos campos: **Op** = parâmetro da operação, herdado pelas atividades; **At** = campo da atividade. **Calc** = calculado pelo serviço único.

| Família (operações de hoje) | Campos da seção | Fonte | Trava (onde) · dano evitado |
|---|---|---|---|
| **Preparo do solo** (subsolagem, gradagem, escarificação, terraços) | **Op:** profundidade de trabalho (cm).<br>**At:** critério de execução (opcional). | Plano (RT) | Só a aprovação individual da O.S. (APROV-02) · operação mecânica no talhão sem decisão técnica. |
| **Tratamento de sementes** | **Op:** modalidade (na fazenda, industrial já tratada, sem TS).<br>**At:** produtos com dose e a unidade da prescrição: **por 100 kg de semente** ou **por 100 mil sementes**; ordem de mistura e volume de calda de TS como instrução do RT.<br>**Calc,** pela unidade da prescrição:<br>• por 100 kg: quantidade/ha = kg de semente/ha × dose ÷ 100;<br>• por 100 mil: quantidade/ha = sementes/ha × dose ÷ 100.000.<br>Contagem e massa ficam separadas. Sem PMS, a conta por 100 mil sai igual (só depende de população e germinação); só a por 100 kg espera.<br>TS industrial (semente já tratada) não gera produto de TS na demanda, e nada é contado duas vezes. | Plano; registro e dose da AG-07; kg de semente da seção Plantio. | Produto sem registro para TS na cultura, ou dose acima da bula → impede salvar a versão (RN-016) · uso ilegal na semente.<br>Sem instrução de mistura → a O.S. não libera o preparo (41.4) · mistura incompatível com o inoculante. |
| **Plantio** (sementes) | **Op:**<br>• população alvo (plantas/ha);<br>• espaçamento entre linhas (m);<br>• fator de estabelecimento de campo (%), opcional, do protocolo;<br>• germinação mínima do envelope (%);<br>• janela de semeadura;<br>• profundidade (cm), opcional.<br>**At:** adubação de base no sulco (produto e dose).<br>**Calc:** plantas/m, sementes/m, sementes/ha, kg/ha (ou mil sementes/ha, quando o item é vendido por sementes) e total do talhão. | Cultivar e semente vêm do cultivo (Planejar safra), sem repetir.<br>PMS e germinação vêm do lote previsto ou da referência do item, marcada "referência"; o lote real as substitui na liberação.<br>ZARC vem do cadastro, com fonte. | Germinação ausente, 0 ou fora de 0–100 %: nada é calculado e nenhum padrão entra; vale o kg/ha informado, com a origem "Informado" (FX-002) · número inventado. Fator de campo ausente: a conta não o usa e a premissa aparece no "Por quê".<br>Sem PMS: sementes/ha e sementes/m saem; só o kg/ha espera, e vale o informado.<br>Lote fora do envelope (germinação abaixo do mínimo ou outra cultivar) → volta ao agrônomo (41.3) · estande diferente do aprovado.<br>Conjunto com outro espaçamento → a O.S. não libera com ele · população fora da aprovada.<br>Fora do ZARC → aviso com a consequência para a cobertura declarada no cultivo (Proagro, subvenção), pela portaria vigente; sem bloqueio · plantar sem saber que perde a cobertura. |
| **Plantio de mudas** | **Op:** espaçamento entre linhas × entre plantas (m), mudas por cova, replantio previsto (%).<br>**At:** adubação de cova.<br>**Calc:** plantas/ha; g/cova ↔ kg/ha (uma base gravada, a outra calculada). | Plano; a muda vem do cadastro de produtos. | Nenhuma no plano. O valor por cova sai calculado · dose por cova errada no campo. |
| **Adubação e correção** (sólidos: calagem, gessagem, fosfatagem, base, cobertura; hoje "Adubação a lanço") | **Op:** modo (lanço total, faixa, sulco, cobertura em linha ou localizada por planta) e modalidade (uniforme ou zonas, pela SOLO-VRA).<br>**At:** produto e dose com base explícita (kg/ha, t/ha ou g/planta) e parcela.<br>**Calc:** nutrientes (N, P₂O₅, K₂O, Ca, Mg, S) em kg/ha, pela composição; PRNT aplicado uma vez só. | Plano. A dose sugerida pelo laudo e pela referência (SOLO-VRA) traz a origem. Composição, garantia e PRNT vêm do cadastro do produto, com versão. | Sem composição, só a conversão nutriente ↔ produto fica bloqueada, e nunca vira 0 nem 100 % (AGR-015) · dose de produto errada.<br>Zonas: topologia e limites (SOLO-VRA A5/A8) · dose fora da área.<br>Limite técnico da referência (ex.: K no sulco) → aviso. |
| **Pulverização** (terrestre; inclui dessecação e foliar) | **Op:** volume de calda (L/ha); ponta e pressão de referência, quando o RT definir; modalidade.<br>**At:**<br>• alvo(s);<br>• produtos e doses, com base por ha ou por 100 L;<br>• volume próprio (vazio herda o da operação).<br>**Calc:**<br>• dose/ha a partir da dose por 100 L;<br>• número de aplicações de cada produto no plano;<br>• folga da carência até a colheita do plano;<br>• **vazão alvo por bico** (L/min) = volume (L/ha) × velocidade (km/h) × espaçamento entre bicos (m) ÷ 600, com a velocidade do REND do conjunto (sem campo duplicado). A vazão **disponível** vem da curva ponta × pressão, que é outra fonte; a tela compara as duas. Sem velocidade ou sem curva: "desconhecido", nunca um padrão. | Plano. Da AG-07, só leitura: registro cultura × alvo, dose máxima, carência, reentrada, máximo de aplicações, intervalo, faixa de volume (quando a bula define), condições de aplicação e grupo IRAC/FRAC/HRAC. | **Impedem salvar a versão:** sem registro para cultura × alvo, dose acima da bula, aplicações acima do máximo, carência além da colheita do plano, volume fora da faixa da bula (RN-016, AGR-027/028) · receita ilegal repetida em toda O.S.<br>Sem alvo → pendente no plano; trava na aprovação da O.S. · receituário sem alvo.<br>Sem volume de calda → pendente; a O.S. não gera cargas nem libera (EX-38) · dose errada por carga.<br>Mesmo grupo de modo de ação em sequência → aviso (AGR-025). |
| **Fertirrigação** | **At:** produtos solúveis e dose com base (kg/ha por aplicação ou g/planta); momento da injeção na irrigação; lavagem depois da injeção (min).<br>**Calc:** massa por injeção; concentração da **solução-estoque** (g/L) = massa ÷ volume útil realmente preparado, que não é o tanque nominal, a água de irrigação nem a lâmina final; tempo de injeção. | Plano (RT). Sistema, injetor e tanque de diluição (capacidade útil) vêm do talhão e do equipamento, não do plano. Solubilidade e compatibilidade vêm do cadastro, com fonte e condição (temperatura, formulação, origem), como dado. A lâmina é a do balanço hídrico do dia (IR). | Concentração da solução-estoque acima da solubilidade → a ficha da O.S. é bloqueada e mostra o volume mínimo de solução. Se o volume mínimo passa da capacidade do tanque, a saída divide em preparos ou injeções separados, cada um dentro da capacidade, com a condição da fonte e a orientação do RT; nunca manda pôr no tanque mais do que ele comporta, e não dá receita química universal · precipitação, entupimento e dose não entregue.<br>Par sem informação de compatibilidade → injeções separadas ou orientação do agrônomo (41.4); nunca "compatível" · mistura incompatível.<br>Vai ao agrônomo (DEC-2609-10). |
| **Tratos culturais e poda** (desbaste, sexagem, desbrota, roçada, capina, poda) | **At:** tipo (da lista do CD-08), critério ou intensidade em texto curto (ex.: "1 planta por cova"; poda: tipo e altura em m) e destino dos restos (opcional). | Plano | Só a aprovação individual (APROV-02) · operação no talhão sem decisão técnica. |
| **Colheita** (grãos, café, frutas) | **Op:** umidade alvo (faixa %, nos grãos); perdas toleradas (kg/ha ou sc/ha); destino (local de recebimento do cadastro); padrão ou classes (frutas, café).<br>**At:** passada, quando a cultura colhe várias vezes. | A meta vem do cultivo, sem repetir. O destino vem do cadastro de locais. | Carência ainda correndo impede liberar a O.S. de colheita (serviço de carência existente, RN-016) · colher com resíduo.<br>Perda medida acima da tolerada → aviso na conferência. |

Irrigação só com água não entra no plano: a lâmina vem do balanço hídrico (DEC-2609-10).

**Migração das operações de hoje para as famílias:**

| Operação de hoje | Família |
|---|---|
| Pulverização | Pulverização |
| Plantio | Plantio |
| Plantio de mudas | Plantio de mudas |
| Tratamento de sementes | Tratamento de sementes |
| Adubação a lanço | Adubação e correção, com modo lanço |
| Fertirrigação | Fertirrigação |
| Poda e Tratos culturais | Tratos culturais e poda |
| Colheita de grãos, de café e de frutas | Colheita |

## Fluxo: plano → Planejar safra → O.S. → demanda

**Planejar safra**
- **Etapa 2.** O painel do cultivo mostra, abaixo do plano, uma linha por operação com os números que valem para aquele talhão.
  - Exemplo: "Plantio · 300 mil pl/ha · 0,50 m · 56,47 kg/ha de 58 W (PMS de referência)".
  - "Ajustar" abre a mesma seção com alcance "este talhão" e o botão "Salvar ajustes neste talhão" (cap. 40). O ajuste é por campo e não toca no resto.
  - O ajuste de insumos de hoje passa para dentro da operação de cada insumo.
- **Etapa 3.** A árvore Operação › atividade › talhão, que já existe, lê os parâmetros da operação.
  - Confere o conjunto com a operação: espaçamento da plantadeira, tanque útil e barra do pulverizador, carga do distribuidor.
  - Mostra, como informação e pelo mesmo serviço, cargas, reabastecimentos e água (L) por talhão.
  - Conjunto incompatível vira ⚠ na linha (TAB-06; REND-02 e 52.3).
- **Etapa 4.**
  - A semente sai da população, em kg ou em mil sementes conforme a unidade do item.
  - O tratamento de sementes sai dos kg de semente.
  - A fertirrigação sai da dose por aplicação. O resto não muda.
  - Cada quantidade guarda origem (operação, campo e versão) e entra uma vez só (RN-006, PCP-01).
- **Dependência imediata.** Hoje a versão salva na PA não chega ao Planejar safra (`processo_planos.py:460`).
  - A F1 grava o plano publicado no cenário compartilhado; o cultivo passa a guardar a versão aplicada, e a geração da O.S. lê dela (decisão 10).
  - A F2 mostra essa versão na etapa 2, com o ajuste por talhão.
  - A revisão a três versões, com conflito por campo (40.3, AJUSTE-05), é fatia própria.

**O.S.**
- **Nasce com a instrução da operação.** É o retrato da seção, com os números calculados e a origem de cada um. O retrato junta:
  - o plano vN;
  - o ajuste do talhão;
  - a recomendação, quando houver.
  - É isso que o agrônomo aprova (CMD-42). Os itens da O.S. são os itens da versão, numa instrução só (EX-38.2).
- **Tela de trabalho.** Ganha o bloco "Instrução", só leitura, com os campos da família.
  - Mudar dose, produto, volume, alvo, mistura, população ou método cria nova versão e volta ao agrônomo (41.3).
  - **Retrato, não ligação viva.** A instrução emitida guarda os parâmetros técnicos e as fontes do momento da emissão, inclusive o tanque útil e a velocidade do conjunto. Editar o cadastro (tanque, bico, PMS de referência) não muda a instrução emitida, as cargas já preparadas, os apontamentos nem a impressão histórica.
  - **Troca explícita dentro do envelope** (41.3): "Trocar conjunto" ou "Trocar lote" refaz só o preparo ainda não executado, sem nova revisão; as cargas preparadas e os apontamentos anteriores ficam. Na semente, a população e a cultivar não mudam, e a germinação fica no mínimo ou acima dele.
- **Fichas e app leem a mesma instrução e chamam o mesmo serviço.** Isso vale para caldeiro, operador, MB-02det e ficha impressa.
  - Saem o valor fixo de `processo_os.py:789-792`, o `CALDA` de `mobile.py:72` e o `EQ` de `os_campo.py:24` (EX-38 R1), reaproveitando os campos que a EX-38 (PR #77) já criou.
  - **Vazão (EX-38 R10):** a alvo vem do volume, da velocidade do REND e do espaçamento entre bicos (campo do pulverizador); a disponível vem da curva ponta × pressão. A ficha mostra as duas e pede o teste de calibração antes da 1ª carga. Faltando velocidade ou curva, aparece "desconhecido".
- O Kanban de 5 fases e a regra "aprovar não libera" (CMD-06) não mudam.

## Telas (master-detail, uma primária, DS do Agrícola)

**Caminho:** Lista de planos → Plano → Operação → Atividade (painel). Nenhuma tela nova.

**Lista de planos.** Mesmo desenho (VIS-06). O cartão ganha o estado só quando há algo a fazer: "1 operação pendente" ou "Aguardando agrônomo".

**Plano**
- **Cabeçalho:**
  - o selo diz "Publicada v6 · por Ana em 12/08/2026", "Rascunho v7 guardado 14:32 · v6 em vigor" ou "v7 em revisão · v6 em vigor";
  - a linha de resumo diz "Soja · 8 atividades · R$ …/ha · 5 operações: 3 prontas, 1 pendente, 1 com aviso".
- **Faixa de operações:** "Visão geral" e uma entrada por operação, com ícone, nome, número de atividades e marca de estado.
  - O estado aparece em texto visível na própria entrada (também no toque), e repetido na dica e no `aria-label` (VIS-04); nunca só na cor.
  - No SOJA-AT: Pulverização 4 · Tratamento de sementes 1 · Plantio 1 · Adubação e correção 1 · Colheita 1.
- **Visão geral:** a de hoje (Cartões ou Tabela, TAB-08 e VIS-06), com operação e estado na linha.

**Operação em foco** (sub-detalhe)
- **Parâmetros:** "Parâmetros de Pulverização", em linha, editados no lugar como a dose (tocar → campo → Enter), cada um com a origem. Os que vêm do cadastro ficam em leitura, com link à ficha da AG-07.
- **Atividades da operação:** com as colunas da família (TAB-08).
  - Em Pulverização: Gatilho · Atividade · Alvo · Produtos · Calda · Carência · Custo/ha.
  - ▸ abre os produtos com as conferências de bula.
  - ⚠ e ⛔ aparecem na linha (TAB-06).
- **Botões da seção:**
  - o ⋯ guarda as ações em lote (MAIS-01);
  - "Incluir atividade" (secundária com +, BOT-05) já vem com a operação escolhida;
  - no rodapé, se o K5 os mantiver (decisão 6), links para a operação anterior e a seguinte, não verdes. Em Tratamento de sementes: "‹ Pulverização" e "Plantio ›".

**Atividade.** É o painel lateral de hoje (operação → atividade → gatilho, DEC-2609-02), mais os campos da família: ex.: Alvo e Calda própria (vazia = da operação). A edição vai direto para o rascunho guardado (decisão 9); o painel fecha com "Concluir", sem segunda gravação.

**Primária da tela** (BOT-01, uma por contexto)
- O rascunho se guarda sozinho, com o recibo no cabeçalho; não há botão de salvar.
- A primária aparece só quando há rascunho ou revisão:
  - "Publicar versão vN" para quem tem o papel com direito de publicar na fazenda;
  - "Submeter à revisão" para quem não tem;
  - na versão em revisão, "Publicar versão vN" e, no ⋯, "Devolver".
- Com ⛔, "Publicar versão vN" fica desabilitada com o motivo, que diz a operação e a atividade (VIS-04). O rascunho continua guardado. Pendência não impede.

**Celular e teclado**
- **390 px:**
  - a faixa rola dentro dela, sem rolagem lateral da página;
  - alvos de 44 px;
  - o painel vira folha inferior.
- **Teclado:** setas andam na faixa e Enter entra na operação. Esc fecha primeiro o editor ou o painel aberto; com nada aberto, volta à visão geral.

**Padrão.** A faixa com estado e a seção por operação entram no catálogo como padrão novo (SEC-01), com varredura, contraprova e fotos (DEC-1610-12, skill `padrao-safrion`).

## Migração dos planos atuais

- **Abrem seccionados sem perder nada.** Os 8 planos (6 da Santa Rita e 2 da Lagoa Grande) mantêm atividades, produtos, doses, bases e gatilhos.
  - Cada operação vai para a família da tabela de migração acima.
  - Calagem e gessagem da Lagoa (i1, i2) entram em Adubação e correção, com modo lanço.
- **Nenhuma quantidade muda.**
  - Semente fica em "kg/ha informado" (52, 50, 20 e 70 kg/ha) até alguém preencher a população.
  - A demanda da etapa 4 fica idêntica, produto a produto, em todas as safras.
  - O ajuste c2 (`a6|0` = 0,60 L/ha) é preservado pela identidade do item (40.3).
- **Campos novos ficam vazios e marcados "Pendente".** O código não preenche nenhum por padrão.
  - **Semente de demonstração ≠ migração.** Só a semente sintética do protótipo (`dados2.py`, `dados_lagoa_safra.py`) traz valores marcados "demonstração", por exemplo SOJA-AT v6 com calda de 100 L/ha, para a OS-0421 manter os números de hoje. Esses valores são dado, não regra.
  - Um rascunho ou versão já guardado no navegador, sem o campo, continua sem ele depois da migração: o mesmo ID e vN nunca recebem por retroação o valor da semente. O campo aparece "Pendente".
- **Versão.** A migração estrutural não cria versão: o conteúdo técnico é o mesmo. A prova é a impressão digital de atividades, produtos, doses e gatilhos, igual antes e depois. Preencher um valor técnico que faltava não é migração: é edição de rascunho e segue a decisão 9.
- **O.S. já emitidas** mantêm os itens. A instrução delas aponta a versão do plano na emissão. Nenhuma muda sozinha (RN-019, 39.7).
- **No software real,** a migração é idempotente, usa o mesmo oráculo e gera um relatório de pendências por plano.

## Aceite

Os valores são sintéticos ou de demonstração, como aritmética de teste, nunca como recomendação. Os oráculos são calculados em decimal.

| ID | Fatia | Caso | Oráculo |
|---|---|---|---|
| P1 | F1 | SOJA-AT aberto | Faixa com Visão geral e as operações na ordem do ciclo: Pulverização (DAP −20), Tratamento de sementes (−1), Plantio (0), Adubação e correção (20), Colheita (118). Contagens 4/1/1/1/1 e estado em cada uma, calculados de `dados2.py`. |
| P2 | F1 | Tocar Pulverização | Só os parâmetros e as 4 atividades de pulverização, com as colunas da família. A seguinte é Tratamento de sementes (ordem do P1). `#plano=SOJA-AT&op=pulverizacao`. F5 reabre a mesma operação com o rascunho e a rolagem. Esc com um editor aberto fecha só o editor; o segundo Esc volta à visão geral, que fica a um toque. |
| P3 | F1 | Calda da operação 100 → 120 L/ha, com a Fungicida 2ª em 150 próprio | As 3 herdeiras mostram 120 "da operação"; a Fungicida 2ª mantém 150. As alterações do rascunho dizem "Pulverização · volume de calda 100 → 120 L/ha em 3 atividades". |
| P4 | F1 | **Fonte única de cargas (EX-38 R1).** OS-0421: T1-A 160 ha, Fungicida A 0,5 L/ha, plano v6 com 100 L/ha, PJ-3030 com tanque útil de 3.000 L no cadastro | Painel, MB-02det e ficha mostram iguais: 6 cargas, sendo 5 de 30 ha e 1 de 10 ha; 15 L por carga cheia e 5 L na última; total de 80 L e 16.000 L de calda.<br>**Tanque mudado no cadastro para 2.500 L:** a OS-0421 emitida e a impressão dela não mudam (retrato, P19). Uma O.S. emitida depois, ou a OS-0421 depois de "Trocar conjunto" explícito com nada preparado, mostra nas três telas 7 cargas, sendo 6 de 25 ha e 1 de 10 ha, com 12,5 L e 5 L. **Contraprova:** na ponta antes da F1, mudar a calda do plano não muda nenhuma das três telas.<br>**Unidade (41.5):** 12 ha, 100 L/ha, tanque de 500 L e 2 L/ha → cargas de 500 + 500 + 200 L, áreas de 5 + 5 + 2 ha e produto de 10 + 10 + 4 L, total de 24 L. |
| P5 | F2 | **Plantio:** 300.000 pl/ha, 0,50 m, PMS de referência 160 g, germinação 85 %, sem fator de campo | 15,0 pl/m; 17,6 sementes/m; 352.941,176… sementes/ha; 56,4706 kg/ha (mostrado 56,47); T1-A com 9.035,294… kg (mostrado 9.035,29), calculado sem arredondar no meio (56,47 × 160 = 9.035,20 é o mutante). O "Por quê" mostra fórmula, origens e a premissa "sem fator de campo".<br>Lote real com PMS 170 g e G 90 % → 56,67 kg/ha, sem nova aprovação (envelope com mínimo de 80 %). Lote com G 75 % → volta ao agrônomo com o motivo.<br>Item vendido por sementes → mil sementes/ha, sem PMS.<br>Sem PMS → sementes/ha e sementes/m saem; o kg/ha fica o informado.<br>Germinação ausente, 0 ou 120 % → nada calculado, nenhuma divisão, nenhum padrão. |
| P6 | F2 | **Tratamento de sementes** (doses de demonstração) | **100 mL/100 kg:** 56,4706 mL/ha; T1-A com 9,035 L (mostrado 9,04 L).<br>**100 mL/100 mil sementes:** 352,941 mL/ha, diferente dos 56,47 da prescrição por massa; T1-A com 56,47 L. Sem PMS, este caso calcula igual; o por 100 kg espera.<br>Mudar a população refaz uma vez só.<br>TS industrial → nenhum produto de TS na demanda, e a semente não é contada duas vezes.<br>Produto sem registro para TS na cultura → ⛔ com o motivo. |
| P7 | F1 | **Bula na versão** (base de demonstração da AG-07) | Carência de 30 dias na DAP 100, com colheita na DAP 118 → ⛔ "carência termina 12 dias depois da colheita prevista" e "Publicar versão" desabilitado com o motivo; o rascunho continua guardado, e a v6 segue vigente. Na DAP 85, a publicação volta.<br>Terceira aplicação de produto com máximo 2 → ⛔. Dose acima da bula → ⛔. Volume fora da faixa da bula (quando definida) → ⛔.<br>Mesmo grupo FRAC em sequência → só ⚠. |
| P8 | F3 | **Adubação e correção** | KCl 60 % a 120 kg/ha → 72 kg/ha de K₂O. MAP 11-52 a 250 kg/ha → 27,5 kg/ha de N e 130 kg/ha de P₂O₅.<br>Produto sem composição → "sem composição no cadastro", com a dose do produto mantida.<br>Dose sugerida pela SOLO-VRA mudada à mão → "Ajustada pelo usuário" (AJUSTE-07).<br>Lagoa i4: 400 kg/ha de superfosfato com 1.850 covas/ha → 216,2 g por cova na ficha. |
| P9 | F3 | **Fertirrigação**, pivô sintético de 20 ha, 45 kg/ha de sulfato de potássio, tanque de diluição de 2.000 L, solubilidade de demonstração de 110 g/L | O sistema vem do talhão (pivô, nunca "gotejo T7"). 900 kg num preparo de 2.000 L de solução-estoque → 450 g/L > 110 g/L → ficha bloqueada. Volume mínimo de solução 8.181,818 L (mostrado 8.182 L), maior que os 2.000 L do tanque: a ficha propõe preparos separados dentro da capacidade (no máximo 220 kg por preparo de 2.000 L, pela solubilidade de demonstração, portanto 5 preparos), com "conferir com o RT a condição da fonte (temperatura, formulação)". Nunca "dissolva 8.182 L no tanque".<br>Par sem dado de compatibilidade → "injetar separado ou pedir orientação", nunca "compatível".<br>Vai ao agrônomo. |
| P10 | F4 | **Colheita** | A meta vem do cultivo, sem ser pedida. Umidade alvo, perdas toleradas e destino aparecem na O.S. e no apontamento.<br>Perda medida de 75 kg/ha com tolerância de 60 → aviso na conferência, sem trava.<br>Carência correndo → liberar a colheita é recusado com dono e data (serviço existente). |
| P11 | F4 | **Tratos, poda e preparo** | Campos curtos; não pede insumo.<br>Roçada no talhão enviada como "Manutenção" continua O.S. agrícola e vai ao agrônomo (APROV-02/04). |
| P12 | F1 | **Publicação do plano** | Ana (papel com direito de publicar na Santa Rita) edita: o rascunho v7 se guarda sozinho e nada é publicado. Ela toca "Publicar versão v7" → "Publicada v7 · por Ana em 16/10/2026".<br>Caio (PCP, sem o papel) → "Submeter à revisão"; a v7 fica "Em revisão"; Ana publica ou devolve. Enquanto isso, a v6 segue vigente.<br>Publicar o plano não aprova a O.S.: a O.S. emitida da v7 fica "A liberar" e não libera sem a aprovação própria (DEC-1610-03).<br>Repetir o clique com a mesma chave não cria v8. |
| P13 | F1 | **Versão × O.S.** | A v7 muda a calda para 120 L/ha. A OS-0421 (em execução, v6) segue com 100 L/ha e 6 cargas (RN-019, 41.3).<br>A O.S. em A liberar, não aprovada, mostra "plano v7 difere: volume de calda" sem mudar sozinha (39.7). Os cultivos ficam na versão deles (40.3). |
| P17 | F1 | **Rascunho inválido persiste** | Ana digita uma dose acima da bula, sai da tela e volta (e também recarrega): o rascunho reabre com a mesma dose e o mesmo ⛔. A v6 continua vigente. Nenhuma ação de guardar publica ou aprova. |
| P18 | F1 | **Vazão alvo × disponível** (EX-38 R10) | 100 L/ha, bicos a 0,5 m: a 6 km/h, alvo 0,5 L/min por bico; a 12 km/h, 1,0 L/min. A vazão disponível vem da curva ponta × pressão, ao lado, com a diferença em %. Sem velocidade no REND, ou sem curva, aparece "desconhecido", e nenhum número padrão. |
| P19 | F1 | **Retrato da instrução** | Depois de emitida a OS-0421, o tanque do a05 muda no cadastro: a instrução, as cargas preparadas, os apontamentos e a impressão da ficha ficam iguais. "Trocar conjunto" refaz só as cargas ainda não preparadas.<br>Um rascunho salvo no navegador antes da F1, sem calda, abre com a calda "Pendente", e não com os 100 L/ha da semente de demonstração. |
| P14 | F2 | **Planejar safra** | **Etapa 2:** o painel do cultivo mostra o resumo por operação da versão aplicada. "Ajustar" Plantio em T1-A para 320 mil → 60,24 kg/ha só em T1-A; T1-B e o plano ficam intactos (AJUSTE-01).<br>**Etapa 3:** plantadeira de 0,45 m num plano de 0,50 m → ⚠ na linha, e a O.S. não libera com esse conjunto.<br>**Etapa 4:** semente = Σ área × kg/ha do cultivo; TS = Σ kg de semente × dose. Nenhum produto contado duas vezes. |
| P15 | F1 | **Migração** | Os 8 planos abrem seccionados. A impressão digital do conteúdo e a demanda de todas as safras ficam iguais antes e depois. O ajuste c2 é preservado. Os campos novos ficam "Pendente", sem valor de código. |
| P16 | F1–F4 | DS, celular e erros | 1440 e 390 px sem rolagem lateral; alvos de 44 px; teclado da faixa; estado em texto; uma primária verde por contexto; sem erro de JS; `ds_1610_test.py` verde. |

## Cliques e digitação (AGENTS §3.3)

Os cliques são medidos no mesmo teste e no mesmo cenário, na versão de antes (`ANTES=<_render da ponta antes da F1>`; os números da coluna "Antes" foram lidos em a685f5e e são medidos de novo nessa ponta) e na de depois. Nenhum cenário que já existe pode piorar.

| ID | Cenário | Antes (lido em a685f5e; medir na ponta) | Depois (teto) |
|---|---|---|---|
| K1 | Mudar uma dose (Fungicida A 0,5 → 0,6) e publicar | 4 cliques + "0,6" e Enter (medido no L12 de `pa_lista_test.py`) | ≤ 4 cliques, mesma digitação |
| K2 | Definir a calda das 4 pulverizações do SOJA-AT | Impossível: o valor é fixo no código | ≤ 4 cliques (abrir o plano, Pulverização, Volume de calda, Publicar versão) + 1 campo |
| K3 | Calda própria numa atividade | Não existe | ≤ 4 cliques + 1 campo |
| K4 | Definir a população e obter o kg/ha | Só kg/ha digitado, pelo caminho do K1 | ≤ 4 cliques + 1 campo; o kg/ha não é digitado |
| K5 | Percorrer as 5 operações uma por vez | 6 cliques pelos chips de filtro (a medir) | ≤ 6 cliques, 0 campos |
| K6 | Ajustar a população de um talhão no Planejar safra | Caminho de mudar dose no painel do cultivo (a medir; o registro em `diretrizes-ux.md` é de 4 cliques e 1 campo) | ≤ antes |
| K7 | Deslocar +5 dias os gatilhos das 4 pulverizações | Cerca de 14 cliques e 4 campos (estimativa do caminho atual; medir) | ≤ 6 cliques + 1 campo (plano, Pulverização, ⋯, Deslocar, Aplicar, Publicar versão) |

## Contraprova

- **A ponta antes da F1 reprova P1–P4, P7, P12 e P17–P19, e a antes da F2 reprova P5, P6 e P14** (lido em a685f5e; reconferir na ponta):
  - não tem faixa com estado nem parâmetros por operação;
  - as cargas são fixas no código, não mudam com o cadastro, e o app diverge;
  - a semente fica em 52 kg/ha fixos;
  - não há bloqueio de bula na versão nem aprovador.
- **P15 passa nas duas versões,** porque a demanda não muda.
  - O mutante obrigatório preenche calda ou população por código; ele muda a demanda ou a ficha e reprova P15.
- **Mutantes de cálculo no teste de unidade:**
  - última carga cheia: 30 L em vez de 24 L no exemplo do 41.5;
  - germinação ignorada: 48,00 kg/ha em vez de 56,47;
  - PRNT aplicado duas vezes;
  - concentração sem dividir pelo volume;
  - TS por 100 mil sementes calculado pela fórmula de massa: 56,47 mL/ha em vez de 352,941;
  - arredondamento no meio da conta: 9.035,20 kg em vez de 9.035,294…;
  - vazão alvo com velocidade padrão quando o REND não tem velocidade (deve dar "desconhecido");
  - germinação 0 ou ausente tratada como 100 %.
- **Mutantes de fluxo no navegador:**
  - guardar o rascunho publica a versão (reprova P12 e P17);
  - a migração injeta 100 L/ha no rascunho salvo (reprova P19);
  - editar o tanque no cadastro muda a ficha impressa de uma O.S. emitida (reprova P19).

## Testes (proporcionais ao risco: dose, lei, demanda e aprovação)

- **Unidade** (`node pa_oper_unit.js`), em decimal:
  - famílias, herança e estados;
  - cada fórmula com os oráculos de P4–P9;
  - conferências de bula pelo gatilho;
  - migração com demanda igual;
  - idempotência de "Salvar" e das ações em lote.
  - **Propriedade:** 1.000 casos com semente fixa, em que a soma da calda das cargas é área × volume, a soma do produto é dose × área e nenhuma carga passa do tanque.
- **Navegador** (`python3 -B pa_oper_test.py`), a 1440 e a 390 px, com toque e teclado:
  - os P da fatia;
  - K1–K7 com `ANTES`;
  - sem erro de JS.
- **Regressão:**
  - `pa_lista_test.py` (o K1 não piora), `pa_regras_test.py`, `saf_operacoes_test.py`, `os_cenario_test.py`, `carencia_test.py` e `ds_1610_test.py`;
  - os testes da SOLO-VRA na F3;
  - a galeria da skill `padrao-safrion`.

## Fora do escopo (com condição de retorno)

| Item | Volta quando |
|---|---|
| Irrigação só com água no plano | O proprietário pedir lâmina planejada; hoje vale a DEC-2609-10 (balanço hídrico). |
| Aplicação aérea e por drone, que têm regras próprias | Uma fazenda cadastrar operação aérea. |
| Taxa variável de semeadura e de pulverização | O arquivo de prescrição for homologado num monitor real (SOLO-VRA). |
| Plantio vegetativo (cana: gemas/m) e consórcio | Houver cultivo dessas culturas no cadastro. |
| Recorrência "a cada N dias" (39.3) para colheita e fertirrigação repetidas | Fatia própria; hoje é uma atividade por passada. |
| Revisão a três versões com conflito por campo (40.3, AJUSTE-05) | Fatia própria, depois da F2. |
| Sugestão automática de população, dose ou volume | O RT curar as fontes; a IA está desligada (DEC-1610-11). |
| Monitoramento, MIP e amostragem como seção do plano | AG-01 e FO-03 entrarem no plano. |
| Tabelas reais de bula, mistura, solubilidade e ZARC | Curadoria do RT com fonte e termos de uso conferidos (§Perguntas, item 3). |
| Envio do plano ao terminal ou ao Operations Center | O proprietário autorizar conta e contrato. |

## Perguntas ao proprietário

Nenhuma pergunta nova nesta versão. As três da versão anterior foram confrontadas com as decisões existentes, como pediu o Codex:

1. **Quem publica o plano em cada fazenda:** o PRD já decide. AG-05 diz que "publicação exige direitos/papel, revisão e testes", e CMD-02 é "Publicar plano operacional / responsável". O papel é configuração por fazenda (P46, CF-01). No protótipo, Ana na Santa Rita.
2. **Plantio fora do ZARC:** fica como decisão dos agentes. O ZARC não proíbe plantar; o MAPA o usa para a elegibilidade ao Proagro e à subvenção do seguro ([página do ZARC no MAPA](https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/programa-nacional-de-zoneamento-agricola-de-risco-climatico/zoneamento-agricola), consultada pelo Codex em 16/10).
   - O plano e o cultivo mostram um aviso com a consequência para a cobertura declarada no cultivo, pela portaria vigente e pelo cadastro com fonte. Não há bloqueio.
   - Volta ao proprietário só se ele quiser bloqueio.
3. **Fonte de bula no software real:** dados abertos do MAPA (Agrofit), com termos de uso conferidos e curadoria do RT. "Aberto" não dispensa licença nem curadoria.
   - Volta ao proprietário só se a escolha for uma base paga, com estimativa de custo.
