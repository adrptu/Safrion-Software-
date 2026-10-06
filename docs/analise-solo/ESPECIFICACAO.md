# Análise de solo e recomendação · sugestão opcional nas doses do plano (SOLO-01)

**Pedido do proprietário (05/10/2026), literal:** «análise de solo e recomendação é opcional o produtor/agronomo usar, ele pode se quiser, apenas usar a dose fixa padrão do plano agronomico. Como plano agronomico tbm tem adubo, como essa funcionalidade de analise de solo e recomendação vai encaixar da melhor forma possível?»

**Desenho já respondido a ele no chat, seguido aqui:** a análise não é um fluxo paralelo. É uma camada de sugestão sobre as linhas de correção e adubação do plano. Sem laudo, vale a dose do plano e nada pede laudo.

**Rótulos.**
- **Executado** (nesta sessão, sobre `ecc8b00`): contas da semente em `decimal`, com cultivos, metas, áreas e datas lidos de `dados2` (`verificacao/conta_semente.py`); 0 colisões de nome entre `cenario.js_prefixo()` e os scripts do SAF (168 × 239 nomes).
- **Executado na revisão por contraexemplo (06/10/2026, feita pelo autor):** leitura do código em `ecc8b00` para cada achado do §10. Exemplos: lote LG26-03 com 60.000 kg no cenário; `CARD.prod` sem o "Calcário dolomítico"; `PROPOSTAS` sem o grupo Corretivos; testes do CD-02 e do CD-06 que leem o calcário sem preço. **A revisão independente do Codex continua pendente.**
- **Especificado:** proposta, ainda sem código.
- Dados sintéticos, inclusive os da Lagoa Grande (Pivô 12 = 48,47 ha na base sintética da nuvem). Decisões tomadas sem o proprietário: [DECISOES.md](DECISOES.md) (D-nn); nenhuma é aprovação dele.

```text
ID / resultado útil / persona: SOLO-01 / quem tem laudo vê, na dose do plano, o que a análise indica, com a conta, e usa com um toque; quem não tem segue a dose do plano sem aviso / agrônomo e gestor da fazenda
Requisitos do PRD e fora do escopo: 37 (FX-001…008, ACFX-01…08), 38.3 e 38.5 (SOLO-01…06, parcial), 40 (AJUSTE-01…10, parcial), CAL-10 (AC-27), AGR-010/011/012 (ACAG-07/08), 41; fora: §9
Autor / revisor / integrador: Claude / Codex / integrador da branch do protótipo (claude/prototipo-v44)
Base / arquivos: ecc8b00 / gen37: solo.js e dados_solo.py (novos), agronomia.py (AG-02; AG-03 e AG-04 no §0), safra.js (ocorr, doseEf, painel de insumos, doApply, abrirHash), processo_safra.py, processo_os.py (origem, Nova ordem, selo, osc_nova), cenario.py (prefixo), dados_cad.py e cad_produtos_estrutura.py (garantia e preço), dados_carencia.py (corretivo novo), dados_lagoa_safra.py:157, inicio.py (IN-01 e IN-03), ui37.py:39, testes do §8
Aceite e verificação: §8; solo_unit.js + build com 0 FALHA + varredura + acoes_duplicadas + testes do módulo, sem vermelho novo contra os vermelhos conhecidos da base
Estado / impedimento / próximo passo: especificado; revisado por contraexemplo pelo autor (§10); revisão do Codex pendente / P4 toca ocorr e o painel de insumos, também editados pelas frentes do Planejar safra (reserva por função) / P1
```

## 0. Mapa do que fica, muda, sai e entra

| Fica (sem mudar a lógica) | Onde |
|---|---|
| O.S.: aprovação individual, "Liberar" = Aprovar e liberar (CMD-42 + CMD-06), "Ajustar antes de liberar", 5 fases | `areas/processo_os.py:370` (`osc_ajustar`), `:473` (`osc_nova`) |
| Quantidade = dose × área em decimal (SINT-C03) | `cenario.js:29-38` (`cenQtd`) |
| Unidade de mercado da cultura (massa da saca) e aritmética decimal | `PRDC.un`, `prUn`, `prMul`, `prDiv` (`producao.js`, já no `cenario.js_prefixo()`) |
| Motor de rendimento e capacidade; `ocorr` como fonte única da quantidade | `safra.js:59-350`, `:529-543` |
| Ajuste manual do talhão, só na sessão (`adjOf` = `self.state.adj`) | `safra.js:528` |
| Painel "Insumos e doses de <talhão>" (ajuste local, PRD 40) e "Aplicar plano", que descarta os ajustes com aviso | `safra.js:1404-1484`; `processo_safra.py:306-342` |
| Cadeia do MIP: o DIA-007 cita o LAU-2043/2044; a REC-014 é registro aprovado, com números gravados e não recalculados | `agronomia.py:253-254`, `:323-390` |
| Camada Solo do Mapa, oculta (Fase 2), com dados locais que não são fonte | `areas/inicio.py:100`, `:164-182` |
| Compra: grupo sem fornecedor homologado fica "Sem fornecedor homologado", com link para o CD-05. O Calcário dolomítico (Corretivos) cai nesse caso | `processo_compras.py:330`, `:377` |

| Muda | Onde | Para |
|---|---|---|
| Menu Agrícola | `ui37.py:39` | + "Análises de solo" (AG-02), entre Planos agronômicos e Planejar safra (D-01) |
| AG-02 | `agronomia.py:145-196` | Lista de laudos, painel do laudo e "Registrar laudo" (§3.1). Ganha o prefixo do cenário, `SOLO0` e os dados do `D2`. A correção de unidade do LAU-2048 continua |
| AG-03 | `agronomia.py:207` | a ajuda "Ex.: VIS-017 · PLA-104" passa a "Ex.: VIS-017 · LAU-2063" (o PLA-104 sai) |
| Dose efetiva | `safra.js:528-531` | `adjOf` continua só da sessão. A nova `doseEf` (R14) devolve o ajuste manual da sessão; sem ele, o aceite do cenário; sem os dois, o padrão. `ocorr` lê `doseEf`, concatena as atividades incluídas (`solo:<laudo>:cal` e `solo:<laudo>:ges`) e deixa fora a atividade retirada pela análise (R07) |
| `openLP`, `lp_save`, `doApply` | `safra.js:1424`, `:1473`, `:1404` | Nunca copiam aceites para a sessão. `lp_save` grava no cenário os aceites e os desfeitos (R14, R15). `doApply` conta os aceites que deixam de valer (R16) |
| Linha de produto e topo do painel de insumos | `processo_safra.py:306-316`; `safra.js:1429-1484` | linha "Análise sugere" e a inclusão, com ações secundárias que preenchem o rascunho (§3.2) |
| Memória da demanda | `safra.js:549` | diz a origem da dose (R21) |
| Script do SAF | `processo_safra.py:230`; `safra.js:1276` | + `cenario.js_prefixo()` (0 colisões, executado) e `cenOuvir(self)`; `abrirHash` lê `sug=1` |
| O.S. | `processo_os.py:197-215`, `:233`, `:473`, `:484` (`osProx`) | origem por insumo; Nova ordem com a dose efetiva e as atividades incluídas; `osc_nova` guarda o grupo do insumo; selo e primário da §3.5 |
| Garantia (PRNT, % K₂O) e preço de referência | `cad_produtos_estrutura.py:36-44`, `:68-70` | `dados_cad.GARANTIA` e `dados_cad.preco_ref()`, uma fonte para o CD-06 e para a regra (D-10, D-11) |
| Registro legal dos produtos | `dados_carencia.py:123-144` | `_produtos()` lê também `dados_cad.ITENS_NOVOS`, com o grupo declarado. O Calcário dolomítico entra como corretivo e fica fora da trava de agrotóxico (§3.5) |
| Texto da OS-0502 | `dados_lagoa_safra.py:157` | "Calagem pela análise de solo" passa a "Calagem · dose do plano 2 t/ha". Hoje a origem é falsa (FX-002) |
| Prefixo do cenário | `cenario.py:87-90` | concatena `solo.js` (só as funções) depois de `cenario.js`, como o `producao.js`. `SOLO0` e `SOLO_REGRA` entram só no AG-02 e no SAF |
| Testes | `agtest.py:47-50`; `links_ocultos_test.py:34`, `:39`; `cadc_fix_cd06.py:12-22`; `cadc_cd06_test.py:11`, `:26-29`; `cadc_cd02_test.py:67` | AG-02 em painel. O AG-02 sai da lista de ocultos, e o par AG-02 → AG-03det (DIA-007) entra no residual "cadeia MIP". O calcário passa a ter preço e data (§7 P1) |
| Fluxo | `fluxos37_md.py:11` | `FL-AG-02`: `['AG-02','SAF']`; `FL-AG-05`: + `'SAF'`. A etapa "RT aprova versão?" do FL-AG-02 fica a cargo do agrônomo, que aprova na O.S. (desenho do proprietário) |

| Sai | Onde | Por quê |
|---|---|---|
| Planos de amostragem PLA-104/105, "Planejar coleta" e "Coletar" | `agronomia.py:159-169` | A amostragem é uma operação do plano (`catalogo_operacoes.py:17-19`) (D-13). O PLA-105 (cistos no C1) é do MIP, e o AG-01 já programa a vistoria de nematoide |
| "Abrir diagnóstico" como próximo passo do laudo | `agronomia.py:151`, `:153` | O diagnóstico não é obrigatório para fertilidade; o DIA-007 aparece como registro vinculado |
| REC-018 (calagem do T2 "aguarda laudo"), as opções Calagem e Gessagem e o campo "Dose informada" (t/ha, "Sugerida 2,1 t/ha (aguarda laudo)") no formulário do AG-04 | `agronomia.py:283-285`, `:292-294` | A calagem do T2 passa a vir do LAU-2063 no plano: um lugar por fato (D-14). Sem a REC-018, o `g_rec` não tem linha editável e fica só em consulta |
| Tarefa "Amostragem de solo · T2" nas telas ocultas IN-01 (f8) e IN-03 (g5) | `inicio.py:1375`, `:1409` | O T2 já tem o LAU-2063. A tarefa pedia um laudo que existe e apontava para o PLA-104, que sai (R01) |

**Novo** (`gen37/`): `solo.js` (regras puras e comandos sobre `c.solo`, com a aritmética `pr*` e o `prUn` do prefixo); `dados_solo.py` (semente de laudos, regra de demonstração e produto padrão de correção por fazenda); testes `solo_unit.js` (node), `solo_ag02_test.py`, `solo_saf_test.py` e `solo_os_test.py` (navegador).

## 1. Missão e princípios
**Missão.** O produtor planeja com a dose do plano. Quem tem laudo vê, na própria linha da dose, o que a análise indica e por quê, e decide com um toque. A fazenda ganha correção e adubação ajustadas ao solo sem tela nova, sem segunda demanda e sem segunda aprovação.

**Princípios.**
1. Opcional e silencioso: sem laudo, nenhum aviso.
2. Sugestão, nunca decisão automática.
3. Um lugar por fato: laudo no AG-02, dose no plano, aprovação na O.S.
4. Conta à vista: laudo, profundidade, método, regra e conta.
5. Só o futuro.
6. Uma fórmula (`solo.js`), em decimal (`pr*`), com a unidade da cultura vinda do `PRDC` e a unidade junto do valor.
7. Uma dose por chave: nunca dois valores vivos para o mesmo produto do mesmo cultivo.

## 2. Menu e telas, antes e depois

| Antes | Depois | Natureza |
|---|---|---|
| Agrícola com 6 itens; AG-02 oculto (laudos, planos de amostragem, "Abrir diagnóstico") | Agrícola com 7 itens: **Análises de solo** (AG-02) | planejamento (entrada técnica) |
| Recomendação de fertilidade no AG-04/AG-04det | Linha da dose no painel de insumos do talhão (etapa 2 do Planejar safra) com "Análise sugere"; painel **Por quê** | planejamento |
| — | Painel **Sugestões pelas análises** na etapa 2 (o link só aparece com 1 sugestão ou mais) | planejamento |
| O.S. sem a origem da dose | O.S. mostra a origem e avisa quando o plano mudou | execução (aprovação) |
| — | Origem na memória da demanda (etapa 4) e "Uso no plano" do laudo | controle |

Telas novas: 0. Painéis novos: 2. O AG-03 e o AG-04 continuam no item Pragas e doenças (MIP).

## 3. Telas

### 3.1 AG-02 · Análises de solo
**Pergunta:** que laudos tenho, estão conferidos e o que mudam no plano?

**Listagem `g_lau`** (G2):

| # | Coluna | Célula |
|---|---|---|
| 1 | Laudo | **LAU-2063** + "solo" ou "folha" |
| 2 | Fazenda · talhão | "T2 · 298 ha"; parcela herda o laudo do talhão |
| 3 | Profundidade | "0–20 cm" |
| 4 | Coleta | 18/09/2026 (data) |
| 5 | V % | "40 %"; "não calculável" (cinza) |
| 6 | K | "136,85 mg/dm³" |
| 7 | Situação | chip: Validado (verde), Aguardando validação (amarelo), Inconsistente (vermelho, mais o motivo), Vencido (cinza), Substituído (cinza, por laudo mais novo da mesma profundidade, R02) |
| 8 | No plano | "2 sugestões · 1 em uso"; "sem sugestão"; "—" |

**Filtros e ordem.** Fazenda (filtro do topo), busca por laudo ou talhão, chips de Situação, filtro e ordenação por coluna. Ordem padrão: Coleta, da mais recente para a mais antiga.

**Fonte da coluna No plano.** Cultivos e planos gravados (`D2`) mais os aceites do cenário. Mudança não salva da sessão do Planejar safra, como uma meta editada, não aparece aqui.

**Ação primária: Registrar laudo.** Formulário lateral com:
- Fazenda (herdada do topo), Talhão (busca), Profundidade (0–20 ou 20–40, um toque), Coleta (atalhos), Laboratório (lista curta), Extrator de P e K (Mehlich-1 ou Resina) e Arquivo (PDF).
- A grade "Valores do laudo": analito, valor, unidade e qualificador.
- No protótipo, "Preencher com o laudo de exemplo" carrega o LAU-2073 (§6).

O laudo nasce **Aguardando validação**; o OCR nunca valida. Se já existe laudo com o mesmo talhão, profundidade, coleta e laboratório, o registro é recusado e o aviso aponta o LAU existente (R13).

**Detalhe** (painel lateral, aberto pela linha):
- **Cabeçalho:** laudo, talhão, profundidade, situação, laboratório, coleta, área representada e quem validou.
- **Original** e **Extraído** lado a lado a partir de 900 px. O Extraído é uma G2 com busca de atributo, filtro e ordenação. Colunas:
  - Atributo.
  - Valor com a unidade na célula ("58,65 mg/dm³"; "17,4 · sem unidade" em vermelho).
  - Método/extrator.
  - Qualificador/LD.
  - Origem (medido ou calculado).
- **Correção:** valor e unidade se corrigem no formulário da linha. Corrigir um laudo Validado o devolve a Aguardando validação; aceites já feitos ficam, e a R22 mostra a diferença.
- **Índices calculados:** SB, T, t, V e m, com a fórmula e as entradas no `title`/`aria-label`. O índice do laboratório aparece ao lado quando existe (R04). Valor com qualificador "<" (abaixo do limite) torna "não calculável" o índice que o usa; nunca vira metade do limite (38.3).
- **Uso no plano** (G2 com filtro e ordenação): uma linha por sugestão, com safra · talhão, item, padrão → sugestão e estado. Estados: "em uso desde 23/09 por Ana" (data do cenário, R12), "disponível", "não aplicável: OS-0502 já liberada", "sem regra: Café".
- **Registros vinculados:** DIA-007 (link para o AG-03det), quando houver.

| Situação | Ação primária do painel |
|---|---|
| Aguardando validação | **Validar laudo** (só agrônomo, R03) |
| Inconsistente | nenhuma: corrigir a unidade na linha → o laudo volta a Aguardando validação |
| Validado com sugestão | **Ver no plano** (`SAF.dc.html#saf=<safra>&passo=cultivos&sug=1`) |
| Validado sem sugestão, Vencido ou Substituído | nenhuma (consulta) |

**Celular, 390 px.** A grade rola por dentro, com a 1ª coluna presa (até 45 %). O painel abre em tela cheia; o Original fica abaixo do Extraído, recolhido ("Ver original"); a ação primária fica presa na área de ações.

### 3.2 A dose no painel "Insumos e doses de <talhão>"
- **Sem sugestão aplicável:** igual a hoje.
- **Com sugestão:** abaixo da linha do produto, uma linha discreta em texto cinza, sem cor de alerta: "Análise sugere **150 kg/ha** · +4.800 kg no talhão · Por quê · Usar 150 kg/ha".
- **Retirada:** "Análise sugere retirar (K alto) · −35.760 kg · a Adubação de cobertura sai do T2 (único insumo) · Por quê · Retirar pela análise".
- **Inclusão** (topo do painel, acima dos grupos de gatilho): "Análise sugere incluir **Calagem** · Calcário dolomítico 1,20 t/ha em 30/09/2026 · +357,6 t · Por quê · Incluir calagem".
- **Uma ação primária:** "Usar", "Retirar pela análise" e "Incluir calagem" são ações secundárias, no estilo de link. Elas preenchem o rascunho do painel, como "Restaurar" e "Retirar" fazem hoje. O primário continua **Salvar**, que grava tudo com uma chave (R13). Cancelar descarta o rascunho, com o aviso de alterações não salvas.
- **Depois de salvar:** chip "pela análise · LAU-2061" no lugar de "dose deste talhão"; a coluna Padrão continua "120,00 kg/ha"; "Restaurar dose" desfaz. A atividade incluída entra no grupo "Data do calendário" com o chip "incluída pela análise".
- **Dose da análise mudada à mão:** chip "ajustado pelo usuário". A linha "Análise sugere 150 kg/ha · Usar" volta e serve de comparação (R15).
- **Laudo validado sem regra:** uma frase no subtítulo do painel, só ali. Exemplo com o LAU-2050 já validado: "LAU-2050 (C1 · 0–20 cm): sem regra de demonstração para Café; vale a dose do plano. Ver laudo ›". Quando a correção do laudo foi para outra safra (R17), a frase diz "calagem pelo LAU-2063 na Safra 2026/27".
- **Celular, 390 px:** a linha da sugestão quebra em até 3 linhas; os botões têm 44 px de altura.

### 3.3 Painel "Por quê" (memória, que antes ficava no AG-04det)
- **Abertura:** sobre o painel em que está (`aside` de 440 px; tela cheia no celular). Esc e Fechar devolvem o foco ao "Por quê".
- **Blocos:**
  1. Laudo: ID, talhão, profundidade, coleta, laboratório, extrator, validado por e em, "Ver laudo ›".
  2. Entradas usadas, com valor, unidade e classe ("K 58,65 mg/dm³ (Mehlich-1) → médio"; "meta 64 sc/ha = 3.840 kg/ha (Planejar safra)").
  3. Regra, com o rótulo fixo "Demonstração — tabela regional a decidir pelo proprietário".
  4. Conta, passo a passo.
  5. Efeito: dose, quantidade, custo e O.S. afetada.
- **Ação primária, pelo contexto:**
  - No painel de insumos: "Usar X". Preenche o rascunho e fecha o Por quê.
  - No lote: "Marcar esta sugestão".
  - No AG-02: nenhuma; fica só o link "Ver no plano".
  - Não aparece quando a R11 nega.

### 3.4 Painel "Sugestões pelas análises" (safra)
- **Entrada:** link na linha de título da etapa 2, "Sugestões pelas análises · 4", só quando há 1 sugestão aplicável ou mais. Com 0, o link não aparece (R01).
- **Grade `g_sug`.** Colunas:
  - Talhão ("T1-A · 160 ha").
  - Atividade · produto ("Adubação de cobertura · KCl 60%").
  - Padrão ("120 kg/ha").
  - Sugestão ("150 kg/ha", "retirar", "incluir 1,20 t/ha").
  - Diferença no talhão ("+4.800 kg").
  - Laudo (LAU-2061, abre o Por quê).
  - Caixa ✓.
- **Filtros e ordem:** busca, chips Tipo (Outra dose · Retirar · Incluir) e ordenação.
- **Seleção:** nenhuma linha vem marcada (D-16); o cabeçalho tem "Marcar todas".
- **Ação primária:** **Usar N sugestões**, desabilitada com 0. É um comando de lote com uma chave só (R13).
  - O aviso diz o efeito: "4 sugestões usadas · KCl 60% −26.400 kg · Calcário dolomítico +357,6 t".
  - Uma linha que a R11 nega falha sozinha e mostra o motivo na própria linha; as outras gravam.
  - Repetir a mesma chave devolve o mesmo resultado. Para tentar de novo a linha que falhou, marque-a outra vez; o novo envio leva outra chave.
- **Rodapé:** "Os demais talhões seguem a dose do plano." Não cria pendência.
- **Celular, 390 px:** a grade rola por dentro e o primário fica preso na área de ações.

### 3.5 Ordem de Serviço (o Kanban continua com 5 fases)
- **Painel da ordem, bloco Insumos:** cada linha mostra a origem da dose (R21).
- **O.S. em A liberar com aceite de outra dose** (exemplo: OS-0502 depois de "Usar 1.800"):
  - **Selo:** amarelo, "Plano mudou pela análise · 1.800 kg/ha (O.S. 2.000)". Vem do aceite gravado no cenário, sem recalcular a regra, e some quando a dose da O.S. fica igual à do plano.
  - **Primário:** **Ajustar antes de liberar**, que abre com 1.800 no campo e mostra "O.S. 2.000 → plano 1.800".
  - **Secundário:** "Liberar com 2.000 kg/ha", a dose da O.S. (R20). Sem selo, o painel segue como hoje.
- **Estoque da OS-0502:** o lote LG26-03 tem 60.000 kg, e a ordem precisa de 87.246 kg (1.800 × 48,47) ou 96.940 kg (2.000 × 48,47). "Salvar e liberar" recusa pelo estoque. "Salvar ajuste" grava a v2 com 1.800 kg/ha, sem liberar. A liberação fica para depois do recebimento de 30/09, como hoje.
- **Nova ordem:**
  - Usa a dose efetiva e a origem, e lista também as atividades incluídas pela análise, com a chave `cultivo|solo:<laudo>:cal`.
  - `osc_nova` guarda o grupo de cada insumo (`g`). O Calcário dolomítico vai como corretivo, e a regra legal não o trava como agrotóxico sem registro.
  - Sem lote na Santa Rita, o liberar fica bloqueado por estoque, e o dono é Suprimentos.

## 4. Regras (testáveis; o dano que cada trava evita)
- **R01 Sem laudo.** Vale a dose do plano. Nenhuma tela do Planejar safra ou da O.S. mostra "sem análise" ou "sem laudo"; nada bloqueia (FX-005, ACFX-01/04). *Dano evitado: ruído repetido que ensina a ignorar avisos reais.*
- **R02 Elegível.** A sugestão só sai de laudo que cumpra tudo isto:
  - laudo **de solo**, **Validado**;
  - da mesma fazenda e do mesmo talhão (a parcela herda, pelo mapa talhão ↔ parcela que já existe, `CARD.nomes`);
  - dentro da validade: 24 meses, ou 12 em talhão irrigado (setor do módulo Irrigação, `dados_irrigacao`; `catalogo_operacoes.py:17`);
  - com amostra única do talhão. O laudo por zona, como o LAU-2043, não sugere.

  Para o mesmo talhão e profundidade, vale o laudo validado de coleta mais recente; o anterior fica "Substituído". *Dano evitado: dose calculada de dado não conferido, de outro lugar ou velho, com adubação e compra erradas.*
- **R03 Validar.** Só o agrônomo valida (`cenExige(ator,'agronomo')`). Analito sem unidade deixa o laudo Inconsistente e impede validar. *Dano evitado: conversão errada vira dose errada.*
- **R04 Índices** (PRD 38.3).
  - Fórmulas: SB = Ca + Mg + K (+ Na, só se analisado); T = SB + H+Al; t = SB + Al; V = 100·SB/T; m = 100·Al/t.
  - Entrada ausente, entrada abaixo do limite ("<") ou divisor zero dá "não calculável", nunca 0. Na não analisado aparece na fórmula como "Na não analisado".
  - O valor do laboratório fica preservado. Diferença acima de 0,5 p.p. (V, m) ou de 0,05 cmolc/dm³ (SB, T, t) mostra o chip "difere do laboratório", sem bloquear, e a regra usa o recalculado (D-17).
- **R05 Conversões** (só em `solo.js`, com `pr*`). 1 cmolc/dm³ = 10 mmolc/dm³. De mg/dm³ para cmolc/dm³: K ÷ 391, Ca ÷ 200,4, Mg ÷ 121,6. mg/kg e mg/dm³ não se convertem: unidade incompatível dá "não calculável".
- **R06 Calagem** (CAL-10, AC-27), só com laudo de 0–20 cm e T em cmolc/dm³.
  - NC100 = max(0, (V2 − V1)·T/100) t/ha; dose = NC100·100/PRNT, com o PRNT **uma vez**, vindo de `GARANTIA`.
  - V2 por cultura (demonstração): Soja, Milho, Feijão e Café 60 %; Mamão Formosa 70 %.
  - Item do plano em kg: × 1.000.
  - Plano com calagem: outra dose, ou "retirar" quando NC = 0. Plano sem calagem e NC > 0: incluir (R18).
- **R07 Adubação potássica** (demonstração, só Soja e só Mehlich-1).
  - Classes de K em mg/dm³: baixo < 40 ≤ médio < 80 ≤ adequado < 120 ≤ alto.
  - Meta do cultivo em kg/ha = `prMul(meta, prUn(cultura).massa)`, a unidade da cultura no `PRDC` (DEC-0510-03). Nenhuma constante de saca no `solo.js`.
  - Faixa de meta da regra: 2.400 a 4.800 kg/ha. Fora dela, nada é sugerido, e a memória diz "meta fora da faixa da regra" (AGR-012, ACAG-08: sem extrapolação silenciosa).

  | K₂O (kg/ha) | baixo | médio | adequado | alto |
  |---|---|---|---|---|
  | 2.400 ≤ meta ≤ 3.600 kg/ha | 90 | 72 | 48 | 0 |
  | 3.600 < meta ≤ 4.800 kg/ha | 108 | 90 | 60 | 0 |

  - Produto = K₂O ÷ fração de K₂O (`GARANTIA`; KCl 60% → 0,60).
  - 0 → retirar. Se o produto é o único insumo da atividade, a atividade sai daquele cultivo (sem horas, custo ou O.S.). *Dano evitado: horas de trator, custo de operação e O.S. para espalhar nada.*
  - Outra cultura, outro extrator ou outro nutriente (P, N, micros): sem regra; o laudo aparece e nada é sugerido.
- **R08 Gessagem** (demonstração; D-03), só com laudo de **20–40 cm** validado.
  - Indicada se Ca < 0,5 cmolc/dm³ ou m > 20 %.
  - NG = k·argila (%) kg/ha, com k = 50 para cultura anual e 75 para perene (classe do CD-02, `dados_cad.CULTURAS`).
  - Nunca deriva da calagem (AGR-011).
  - Sem laudo de 20–40 cm, ou sem gatilho, nada é sugerido. A regra não sugere retirar uma gessagem do plano.
- **R09 Arredondamento.** Dose com 2 casas na unidade do item, meio para cima, em decimal. Quantidade = `cenQtd(dose, área)`; a diferença no talhão é `cenQtd(sugerida, área) − cenQtd(efetiva, área)`. Dose sugerida igual à efetiva não mostra nada (37.2: sem ruído).
- **R10 Rótulo e chave da regra.** Toda memória diz "Demonstração — tabela regional a decidir pelo proprietário". `SOLO_REGRA.estado` vale `'demonstração'` ou `'desligada'`; desligada, zero sugestões e o laudo continua visível.
- **R11 Só o futuro.** O comando só é oferecido se a data da ocorrência é ≥ hoje e a O.S. do `cultivo|atividade` não existe ou está em **A liberar**. Senão a linha some e o AG-02 diz por quê. *Dano evitado: reescrever consumo executado ou dose já aprovada e reservada (ACFX-05, AJUSTE-09).*
- **R12 Usar.** Grava um ajuste local só daquele cultivo (PRD 40) com:
  - origem "pela análise", laudo, regra e entradas (inclusive a meta);
  - o plano (id e versão);
  - autor e data do cenário (`D2.hoje`, 23/09/2026) com a hora.

  O padrão fica como referência. Ignorar não grava nada nem pede motivo.
- **R13 Idempotência.** Todo comando sobre `c.solo` leva a chave de quem inicia: Registrar, Corrigir, Validar, Aceitar, Aceitar em lote e Desfazer. A chave nasce ao abrir o formulário, o painel de insumos ou o lote.
  - `c.solo.recibos[chave]` guarda o conteúdo e o resultado. Mesma chave e mesmo conteúdo: "já registrado", nada muda. Mesma chave e outro conteúdo: conflito, nada é gravado.
  - Um aceite por (cultivo, atividade, produto): o novo substitui o anterior, com histórico, e nunca soma.
  - Laudo com o mesmo talhão, profundidade, coleta e laboratório: recusado.

  *Dano evitado: clique duplo dobrando a dose, a demanda ou o laudo.*
- **R14 Uma dose por chave.** A dose efetiva de (cultivo, atividade, produto) é, nesta ordem, o ajuste manual da sessão, o aceite do cenário ou o padrão.
  - Gravar um aceite apaga o ajuste manual da sessão naquela chave.
  - Salvar ajuste manual numa chave com aceite desfaz o aceite. O histórico registra "substituído por ajuste manual".
  - `adjOf` continua só da sessão; `openLP`, `lp_save` e `doApply` nunca copiam aceites para ela. O rascunho do painel marca a origem de cada dose: salvar sem mudar uma dose "pela análise" não a transforma em ajuste manual.
  - A dose efetiva passa por `ocorr` e de lá para demanda, cobertura, etapa 3 e Compra. A linha de necessidade é a mesma (`cultivo|atividade|produto`); não nasce segunda demanda (ACFX-03/05, AJUSTE-03/10).

  *Dano evitado: desfazer o aceite e a demanda continuar com a dose da análise.*
- **R15 Mudança manual.** Dose da análise alterada à mão desfaz o aceite (R14), e o chip passa a "ajustado pelo usuário". A linha "Análise sugere 150 kg/ha · Usar" volta e é a comparação de 40.2. Como todo ajuste manual de hoje, o valor fica na sessão (§9). "Restaurar dose" volta ao padrão.
- **R16 Identidade estável.** A chave do aceite é (cultivo, id da atividade, nome do produto), não a posição.
  - Nova versão do padrão mantém o aceite e mostra o novo padrão como referência.
  - Produto que saiu do padrão deixa um aceite órfão visível ("KCl 60% saiu do plano v7: manter como incluído ou descartar") e nunca volta sozinho (40.3, AJUSTE-05).
  - Se a nova versão passa a ter a operação incluída pela análise (Calagem, Gessagem), vale só a incluída. A do padrão aparece como referência ("o plano v7 passou a ter Calagem 1 t/ha"), nunca as duas.
  - O aceite vale só enquanto o cultivo usa o plano gravado nele. Trocar o plano em "Aplicar plano", que é da sessão, faz o aceite deixar de valer sem apagá-lo; o aviso que já existe conta os aceites como "deixam de valer".

  *Dano evitado: calcário duas vezes no mesmo talhão; apagar no cenário uma decisão por causa de uma troca que some ao recarregar.*
- **R17 Uma correção por laudo e talhão.** A calagem ou o gesso de um laudo vai para os cultivos do talhão, todas as parcelas, na primeira safra aberta que tem o talhão, pela data de plantio. Nas safras seguintes, não. Exemplo: T1-A e T1-B na Safra 2026/27 recebem; a Safrinha 2027 não. *Dano evitado: calcário aplicado duas vezes pelo mesmo laudo, ou só em parte do talhão.*
- **R18 Operação incluída.** Atividade "Calagem" ou "Gessagem", da operação Adubação a lanço, com:
  - id `solo:<laudo>:cal` ou `solo:<laudo>:ges` e grupo do insumo Corretivos;
  - o produto padrão de correção da fazenda (`dados_solo`, D-12);
  - rendimento da linha "Adubação a lanço · Calagem" que já existe na etapa 3.

  O gatilho fica gravado no aceite como data fixa: DAP −60, se o plano é por DAP e essa data ainda não passou; senão, a chegada viável de uma compra nova (`D2.viavel`, hoje + `PRAZO_REPOSICAO` = 30/09/2026). A memória diz qual das duas.

  Produto sem preço de referência: nada é incluído, e o laudo diz o motivo. *Dano evitado: custo zero na safra e proposta de R$ 0 na Compra.*
- **R19 Trocar produto** nunca é sugestão. É ação explícita (retirar + incluir) no painel.
- **R20 Aprovação única.** Aceitar não cria recomendação, diagnóstico nem aprovação. A O.S. continua com a aprovação individual do agrônomo (CMD-42) e o liberar (CMD-06). A O.S. em A liberar com dose diferente da do plano recebe o selo da §3.5. Liberar com a dose da O.S. registra a decisão do agrônomo (o CMD-42 grava a dose). *Dano evitado: mudar uma dose aprovada ou reservada sem o agrônomo (S1).*
- **R21 Origem visível.** A linha de insumo da O.S., a memória da demanda e o "Uso no plano" dizem uma destas: "padrão do plano vN", "pela análise · LAU-xxxx", "ajustado pelo usuário" ou "ajustado pelo agrônomo na O.S. vN". Sem análise, nada de selo científico (FX-002, AJUSTE-07).
- **R22 Meta viva.** A regra de K lê a meta do cultivo (etapa 2). A linha "Análise sugere" volta a aparecer quando a sugestão atual difere do aceite, porque a meta, o laudo ou o laudo vigente (R02) mudou.

## 5. Integração com o estado único e os outros módulos

| Quem | Lê | Grava |
|---|---|---|
| `c.solo` no cenário (`talhao-os-cenario-v1`; o acessor `cenSolo(c)` cria o que faltar, sem subir versão, D-05) | — | `laudos` (novos e correções), `val` (validações), `aceites[cid\|atv\|prod]` = {dose \| '-' \| atividade incluída, plano, laudo, regra, entradas, por, em, chave, hist}, `recibos[chave]` |
| AG-02 | `SOLO0` (`dados_solo`), `c.solo`, cultivos e planos (`D2`), ordens (fase por chave) | `soloRegistrar`, `soloCorrigir`, `soloValidar` |
| Planejar safra (etapa 2 e painéis) | `c.solo`, cultivo (área, meta, plantio, plano), plano (dose padrão, versão), `GARANTIA`, `preco_ref`, `PRDC`, fase da O.S.; `cenOuvir`; a leitura de `c.solo` é uma por `cenrev`, não uma por chamada de `ocorr` | `soloAceitar` (Salvar do painel de insumos), `soloAceitarLote`, `soloDesfazer` |
| Etapas 3 e 4 | `ocorr` com a dose efetiva | nada novo |
| O.S. e Mapa (`JS_NUCLEO`) | aceites gravados (Nova ordem, origem, selo); sem `SOLO0` e sem recalcular a regra | nada novo: `osc_ajustar`, `osc_liberar` e `osc_nova` (agora com `g`) |
| Regra legal (`CARD`) | o grupo de cada produto, inclusive `dados_cad.ITENS_NOVOS` | — |
| Compra de insumos | a mesma demanda e a mesma solicitação; o Calcário dolomítico aparece como "Sem fornecedor homologado em Corretivos", com link para o CD-05 (comportamento de hoje) | — |
| MIP (AG-03/AG-04) | DIA-007 → LAU-2043/2044 (link para o AG-02) | — |
| CD-06 | `GARANTIA` e `preco_ref` (fonte única) | — |

## 6. Semente sintética (executado: `verificacao/conta_semente.py`)
**Laudos.** Cátions em cmolc/dm³; K em mg/dm³, com cmolc/dm³ entre parênteses. Validados por Ana (agrônoma) em 20/09/2026, salvo indicação.

| Laudo | Fazenda · talhão | Prof. | Coleta · lab · extrator | Entradas | Calculado | Situação |
|---|---|---|---|---|---|---|
| LAU-2043 | SR · T4 (Z2 de 3 zonas) | 0–20 | 12/09 · Lab Solo Vale · Mehlich-1 | Ca 3,90 · Mg 1,40 · K 31,28 (0,08) · H+Al 3,82 · Al 0,10 | SB 5,38 · T 9,20 · t 5,48 · V 58,48 % · m 1,82 % | Validado · por zona: não sugere |
| LAU-2044 | SR · T4 | 20–40 | idem | Ca 1,10 · Mg 0,50 · K 23,46 (0,06) · H+Al 3,00 · Al 0,10 · argila 32 % | SB 1,66 · T 4,66 · t 1,76 · V 35,62 % · m 5,68 % | Validado · sem gatilho de gesso |
| LAU-2048 | SR · P1 (folha) | — | 18/09 · Agrolab · nítrico-perclórica | N 48,2 g/kg · P 3,1 g/kg · K 17,4 (sem unidade) · B 42 mg/kg | — | Inconsistente |
| LAU-2050 | SR · C1 | 0–20 | 19/09 · Agrolab · Resina | Ca 3,40 · Mg 1,10 · K 97,75 (0,25) · Al 0 · H+Al não analisado | SB 4,75 · t 4,75 · m 0 % · T e V não calculáveis | Aguardando validação |
| LAU-2061 | SR · T1 (T1-A e T1-B) | 0–20 | 18/09 · Lab Solo Vale · Mehlich-1 | Ca 3,10 · Mg 1,25 · K 58,65 (0,15) · H+Al 3,00 · Al 0 | SB 4,50 · T 7,50 · V 60,00 % · m 0 % | Validado |
| LAU-2063 | SR · T2 | 0–20 | 18/09 · Lab Solo Vale · Mehlich-1 | Ca 1,25 · Mg 0,44 · K 136,85 (0,35) · H+Al 3,06 · Al 0,30 | SB 2,04 · T 5,10 · t 2,34 · V 40,00 % · m 12,82 % | Validado |
| LAU-2071 | LG · Pivô 12 | 0–20 | 15/09 · Agrolab · Mehlich-1 | Ca 2,90 · Mg 0,95 · K 78,20 (0,20) · H+Al 4,05 · Al 0,20 · lab V 49 % | SB 4,05 · T 8,10 · V 50,00 % (difere do lab) · m 4,71 % | Validado |
| LAU-2072 | LG · Pivô 12 | 20–40 | idem | Ca 0,30 · Mg 0,20 · K 31,28 (0,08) · H+Al 4,00 · Al 0,60 · argila 20 % | SB 0,58 · T 4,58 · V 12,66 % · m 50,85 % | Validado |
| LAU-2073 (exemplo) | SR · T7 | 0–20 | 22/09 · Lab Solo Vale · Mehlich-1 | Ca 3,90 · Mg 1,30 · K 160,31 (0,41) · H+Al 2,89 · Al 0 | SB 5,61 · T 8,50 · V 66,00 % | nasce Aguardando validação |

**Produtos e preços.** `GARANTIA`: KCl 60% → 60 % K₂O; Calcário dolomítico → PRNT 85 % (o mesmo texto de hoje no CD-06); Calcário dolomítico filler → PRNT 90 % (sintético). Preço de referência do Calcário dolomítico: R$ 180,00/t (sintético, D-10). Produto padrão de correção: Santa Rita, Calcário dolomítico; Lagoa Grande, Calcário dolomítico filler e Gesso agrícola.

**Sugestões.** A semente não tem nenhum aceite, então os números atuais das outras frentes ficam iguais. Metas da R07, todas na faixa de 2.400 a 4.800 kg/ha: T1-A 3.840, T1-B 3.720 e T2 3.780 kg/ha.

| Safra · talhão | Atividade · produto · data | Padrão | Sugestão | No talhão | Custo | Conta |
|---|---|---|---|---|---|---|
| S2627 · T1-A 160 ha, meta 64 sc/ha | Adubação de cobertura · KCl 60% · 04/11/2026 | 120 kg/ha | 150 kg/ha | +4.800 kg | +R$ 11.520,00 | K médio; 3.840 > 3.600 → 90 K₂O ÷ 0,60 |
| S2627 · T1-B 152 ha, 62 sc/ha | idem · 14/11/2026 | 120 kg/ha | 150 kg/ha | +4.560 kg | +R$ 10.944,00 | idem (3.720) |
| S2627 · T2 298 ha, 63 sc/ha | idem · 07/11/2026 | 120 kg/ha | retirar; a atividade a4 sai do T2 (único insumo) | −35.760 kg | −R$ 85.824,00 | K alto → 0 |
| S2627 · T2 | **incluir** Calagem · Calcário dolomítico · 30/09/2026 (DAP −60 = 19/08 já passou; vale a chegada viável) | — | 1,20 t/ha | +357,6 t | +R$ 64.368,00 | (60 − 40)·5,10/100 = 1,02 ÷ 0,85 |
| LG2627 · Pivô 12, 48,47 ha | Calagem · filler · 25/09/2026 · OS-0502 em A liberar | 2.000 kg/ha | 1.800 kg/ha | −9.694 kg | −R$ 1.744,92 | (70 − 50)·8,10/100 = 1,62 ÷ 0,90 |
| LG2627 · Pivô 12 | Gessagem · Gesso agrícola · 10/10/2026 | 1.000 kg/ha | 1.500 kg/ha | +24.235 kg | +R$ 5.331,70 | Ca 0,30 < 0,5; m 50,85 % > 20 % → 75 × 20 |
| S2627 · T7 42 ha (depois de registrar e validar o LAU-2073) | **incluir** Calagem · Calcário dolomítico · 30/09/2026 | — | 0,40 t/ha | +16,8 t | +R$ 3.024,00 | (70 − 66)·8,50/100 = 0,34 ÷ 0,85 |

**Sem sugestão:**
- calagem no T1: V 60 = V2, limite da regra;
- C1: V não calculável; Café sem regra de K; extrator Resina;
- T4: laudo por zona; sem plano;
- MAP 11-52: sem regra de P;
- S27SF: Milho sem regra de K; a calagem do T2 já está na S2627 pela R17.

**S2627 com as 4 sugestões usadas** (demanda bruta): KCl 60% −26.400 kg (−R$ 63.360,00); Calcário dolomítico +357,6 t (+R$ 64.368,00).

**OS-0502:** o lote LG26-03 tem 60.000 kg; a ordem precisa de 96.940 kg com 2.000 kg/ha e de 87.246 kg com 1.800 kg/ha (executado, mesmo script).

## 7. Passos de implementação (cada um deixa o protótipo funcionando)
1. **P1 · Regras puras.**
   - `solo.js` com R04–R10, R16–R18 e `soloSugestoes(ctx, cultivo)`, a única fonte da linha, do lote, do Por quê e do "Uso no plano". Usa `pr*` e `prUn` do prefixo; não define constante de unidade nem aritmética decimal própria.
   - `dados_solo.py` com a semente e `SOLO_REGRA`.
   - `GARANTIA` e `preco_ref` em `dados_cad.py`, lidos pelo CD-06.
   - `dados_carencia._produtos()` lê `ITENS_NOVOS`.
   - Testes:
     - `solo_unit.js`.
     - `cadc_fix_cd06.py`: o selo de abertura passa a "1 item sem preço · 1 item sem embalagem". O caso "item sem preço" e o "Cadastro completo" usam só a "Semente de soja 64 Z".
     - `cadc_cd06_test.py:11`: deixa de esperar "1 item sem preço" (o selo abre sem pendência de preço).
     - `cadc_cd06_test.py:26-29`: "preço sem data é barrado" passa a limpar a data do calcário antes de salvar.
     - `cadc_cd02_test.py:67`: "3 itens sem preço" passa a "2 itens sem preço".
     - Motivo de todos: o calcário ganha preço e data (D-10).
2. **P2 · Estado e comandos.**
   - `cenSolo` e `soloRegistrar/Corrigir/Validar/Aceitar/AceitarLote/Desfazer` com `cenMudar` e `recibos`.
   - `solo.js` no `cenario.js_prefixo()`.
   - Gancho `window.__solo` para os testes.
   - Unitários de idempotência, conflito, laudo duplicado, papel e lote parcial.
3. **P3 · AG-02.**
   - Tela da §3.1 e item no menu.
   - `agtest.py`: a correção do K passa ao painel do LAU-2048, com o mesmo resultado.
   - `links_ocultos_test.py`: o AG-02 sai da lista de ocultos (`:34`), e o par (AG-02, AG-03det) entra no residual "cadeia MIP" (`:39`).
   - `inicio.py`: sem a f8 e a g5. `agronomia.py:207`: ajuda nova.
   - Novo: `solo_ag02_test.py`.
4. **P4 · Plano.**
   - Prefixo do cenário e `cenOuvir` no SAF.
   - `doseEf`. Atividades incluídas e retiradas em `ocorr`.
   - `openLP`, `lp_save` e `doApply` pela R14 e pela R16.
   - Linha da §3.2 e painel Por quê.
   - Testes: `solo_saf_test.py`. Sem aceite, devem continuar iguais: `quantidade_test` 14/14, `rend_multiconjuntos_unit` 106/106, `capacidade_unit`, `saf_operacoes_test` e `tabelas_saf_test`. O espelho Python (`dados2._ocorr_py`) não muda: a semente não tem aceite e o Python não lê o cenário do navegador.
5. **P5 · Sugestões pelas análises.** Painel da §3.4 com lote; `abrirHash` lê `sug=1`. Teste no `solo_saf_test.py`.
6. **P6 · O.S.**
   - Origem, selo e primário da §3.5, Nova ordem com as incluídas e `osc_nova` com `g`.
   - Texto de `dados_lagoa_safra.py:157`.
   - Testes: `solo_os_test.py`, `os_cenario_test` (sem vermelho novo além do 19/20 conhecido), `os_v39_liberar_test`, `aprova_quem_decide_test`, `acao_unica_test` e `links_ocultos_test` (E3).
7. **P7 · Limpeza e artefato.**
   - Limpeza: REC-018, opções e campo do AG-04; `fluxos37_md.py`.
   - Depois:
     - `python3 build.py > /tmp/SOLO-build.log; grep -c FALHA` = 0;
     - `montar_render.py`;
     - `varredura.py`;
     - `../ferramentas/acoes_duplicadas.py . /tmp/SOLO-dup.json` (0 duplicatas novas);
     - bateria do módulo.

## 8. Critérios de aceite (o teste que prova cada um)

| ID | Critério | Teste |
|---|---|---|
| AC-SOLO-01 | AC-27: V 40 → 60, T 5, PRNT 80 → NC100 1,00 e 1,25 t/ha; PRNT entra uma vez | `solo_unit.js` |
| AC-SOLO-02 | Índices da §6 iguais à verificação. Sem H+Al, T e V ficam "não calculável" (nunca 0). Al "< 0,1" deixa t e m "não calculável". Na ausente fica fora da soma. Unidade incompatível → "não calculável" | `solo_unit.js` |
| AC-SOLO-03 | Limites: K 39,99/40/79,99/80/119,99/120 mg/dm³; meta 2.399/2.400, 3.600/3.601 e 4.800/4.801 kg/ha (fora da faixa: nada e "meta fora da faixa da regra"); V = V2 → nada; gesso com Ca 0,5 e m 20 % exatos → não indicado | `solo_unit.js` |
| AC-SOLO-04 | Regra desligada → 0 sugestões; laudo visível | `solo_unit.js`, `solo_saf_test.py` |
| AC-SOLO-05 | Sem laudo: nenhum texto "sem análise"/"sem laudo" no SAF (etapas 1–4 e painéis) e na O.S. Com 0 sugestões, o link "Sugestões pelas análises" não aparece. O T7 salva dose manual sem nada pedir | `solo_saf_test.py` |
| AC-SOLO-06 | Registrar o LAU-2073 → Aguardando validação. Registrar de novo a mesma amostra → recusado ("já registrado como LAU-2073"). Caio não valida ("decisão de Ana (agrônoma)"); Ana valida. Só então o T7 mostra "incluir Calagem 0,40 t/ha" | `solo_ag02_test.py` |
| AC-SOLO-07 | LAU-2048: K sem unidade → Inconsistente, sem "Validar"; corrigir para g/kg → Aguardando validação | `solo_ag02_test.py`, `agtest.py` |
| AC-SOLO-08 | T1-A: linha "Análise sugere 150 kg/ha · +4.800 kg". Por quê com laudo, profundidade, método, regra (rótulo demo) e conta. "Usar" preenche o rascunho; Salvar → chip "pela análise · LAU-2061", padrão 120 visível. Demanda bruta de KCl +4.800 kg exatos. Cancelar antes de salvar → nada gravado | `solo_saf_test.py` |
| AC-SOLO-09 | `__solo.aceitarLote` duas vezes com a mesma chave → demanda inalterada e "já registrado". Mesma chave e outra dose → conflito, nada gravado. Lote com uma linha negada pela R11 → as outras gravam e a negada mostra o motivo | `solo_unit.js`, `solo_saf_test.py` |
| AC-SOLO-10 | Lote sem nada marcado. Marcar T1-A, T1-B, T2 KCl e T2 calagem → demanda bruta de KCl −26.400 kg e de Calcário +357,6 t; custo de insumos +R$ 1.008,00. Na etapa 3, o T2 perde a Adubação de cobertura de 07/11 e ganha a Calagem de 30/09 | `solo_saf_test.py` |
| AC-SOLO-11 | Meta do T1-B de 62 para 60 sc/ha → a sugestão some (120 = padrão); com aceite feito, "Análise sugere 120" reaparece | `solo_saf_test.py` |
| AC-SOLO-12 | Com o aceite de 150, mudar à mão para 140 e salvar → "ajustado pelo usuário"; a linha "Análise sugere 150 · Usar" volta; o histórico do aceite diz "substituído por ajuste manual"; demanda bruta com 140. Restaurar → 120. Usar 150 e salvar; reabrir e salvar o painel sem mudar nada → a dose continua "pela análise"; `__solo.desfazer` (como de outra aba) → demanda com 120 (nenhuma cópia na sessão) | `solo_saf_test.py` |
| AC-SOLO-13 | Plano v7 com KCl padrão 110 → aceite 150 mantido e padrão 110 exibido. KCl fora do v7 → aceite órfão, sem reaparecer sozinho. v7 com Calagem própria e calagem incluída pela análise → uma só ocorrência de calagem no T2. Aceite de SOJA-AT com o cultivo em SOJA-PD → não vale e não é apagado | `solo_unit.js` |
| AC-SOLO-14 | OS-0502: Usar 1.800 → selo "Plano mudou…" em A liberar, 5 colunas no Kanban, primário "Ajustar antes de liberar" (um só). Ajustar abre com 1.800. "Salvar e liberar" recusa pelo estoque (60.000 kg para 87.246 kg). "Salvar ajuste" grava a v2 com 1.800 kg/ha, e o selo some. Com o lote elevado no teste a 110.000 kg (recebimento de 30/09), Ana libera: CMD-42 + CMD-06 com 1.800 kg/ha. A origem aparece na linha de insumo. Nenhuma REC/DIA nova | `solo_os_test.py` |
| AC-SOLO-15 | O.S. Liberada, em execução ou data passada → sem "Usar"; o AG-02 diz "não aplicável: …" | `solo_unit.js`, `solo_ag02_test.py` |
| AC-SOLO-16 | Nova ordem do T1-A · Adubação de cobertura com aceite → KCl 150 kg/ha × 160 ha = 24.000 kg, "pela análise · LAU-2061" | `solo_os_test.py` |
| AC-SOLO-17 | R17: a S27SF não recebe a calagem do T2. Um laudo sintético do T1 com V 50 % (T 7,50) dá 0,88 t/ha ao T1-A e ao T1-B na S2627 e nada ao T1-A da S27SF | `solo_unit.js` |
| AC-SOLO-18 | Tabelas `g_lau`, `g_sug`, Extraído e Uso no plano com busca, filtro e ordenação; unidade na célula; 390 px sem rolagem horizontal da página; uma ação primária por tela e por painel (no painel de insumos, só Salvar) | `solo_ag02_test.py`, `solo_saf_test.py`, `acoes_duplicadas.py` |
| AC-SOLO-19 | Build com 0 FALHA; varredura sem erro; vermelhos só os conhecidos da base | comandos do P7 |
| AC-SOLO-20 | Nova ordem da Calagem incluída no T2 → OS em A liberar com Calcário dolomítico (grupo Corretivos), 1,20 t/ha × 298 ha = 357,6 t. A regra legal não trava. O liberar fica bloqueado só por estoque ("Sem lote de Calcário dolomítico"), e o dono é Suprimentos | `solo_os_test.py` |
| AC-SOLO-21 | Dois laudos validados do T2 a 0–20 cm → vale o de coleta mais recente; o outro aparece "Substituído" e não sugere | `solo_unit.js` |

## 9. Fora de escopo e condição de retorno

| Fora | Volta quando |
|---|---|
| Tabela regional validada (classes, V2, doses por cultura, faixa de meta, P, N, micros) | o proprietário decidir a tabela (fonte, edição, cultura, região); entra em `SOLO_REGRA` sem mudar tela |
| Gessagem fora da demonstração (PRD B-05, curadoria de subsuperfície) | a curadoria entregar fonte e casos; até lá a regra de gesso é só demonstração |
| AG-02 comparativo completo (todos os atributos, presets, exportação; PRD 38.4) e OCR real | pedido do proprietário ou software real |
| Camada Solo do Mapa (IN-04) | pedido do proprietário; lerá `dados_solo` (fonte única), não `inicio.py:164-182` |
| Laudo por zona, taxa variável e prescrição (cap. 36, FX-008) | pedido do proprietário; o LAU-2043 já tem as zonas |
| Planos de amostragem e coleta no app | pedido; entra como operação "Amostragem" do plano |
| Análise foliar com regra | protocolo por cultura decidido |
| "Revisar atualização do padrão" em três versões (40.3 completo) e "Adicionar operação" manual (40.2) | frente Planos agronômicos ou Planejar safra; o formato `solo:<laudo>:<cal\|ges>` já serve |
| Ajuste manual do talhão gravado no estado único (hoje fica só na tela) | frente Planejar safra; os aceites da análise já ficam no cenário, e a R14 já define a precedência |
| Retirada manual do único insumo de uma atividade (hoje a operação fica "Sem insumos · só operação") | frente Planejar safra; a retirada pela análise já tira a atividade (R07) |
| Fornecedor homologado e propostas de Corretivos na Compra | pedido do proprietário ou semente da Compra; até lá o calcário aparece "Sem fornecedor homologado" |
| Demanda do Planejar safra lendo a dose da O.S. depois de liberada (o plano com 1.800 e a O.S. liberada com 2.000 divergem até lá) | CTL-4 (demanda única lendo o realizado das O.S.) |

## 10. Revisão por contraexemplo (06/10/2026)
Autor: Claude, sobre `ea130ca`. Rótulo: cada achado foi conferido no código e no PRD (executado); as correções estão nas seções acima (especificado). A revisão independente do Codex continua pendente.

| # | S | Contraexemplo | O que mudou |
|---|---|---|---|
| A1 | S2 | O `adjOf` mesclado (sessão ⊕ aceites) é copiado por `openLP`/`lp_save`/`doApply` para a sessão. Desfazer o aceite no cenário deixa 150 na sessão, e a demanda fica +4.800 kg | R14: uma dose por chave, com precedência sessão → aceite → padrão; `adjOf` só sessão; nunca copiar; o rascunho marca a origem. Sai o `soloManual`. AC-SOLO-12 |
| A2 | S2 | Laudo do T1 com V baixo: a R17 ("primeiro cultivo por data") dá calcário só ao T1-A (160 ha), e o T1-B (152 ha) fica sem correção | R17 por safra: todas as parcelas do talhão na primeira safra aberta. AC-SOLO-17 |
| A3 | S2 | O plano v7 passa a ter Calagem, e o T2 já tem a Calagem incluída pela análise: as duas entram (2,2 t/ha) e a demanda dobra | R16: vale só a incluída; a do padrão vira referência. AC-SOLO-13 |
| A4 | S2 | Nova ordem da Calagem incluída: `osc_nova` perde o `g`, e o "Calcário dolomítico" não está no `CARD.prod` (`dados_carencia.py:123-144`). A regra legal o trata como agrotóxico sem registro e nunca libera | `_produtos()` lê `ITENS_NOVOS`; `osc_nova` guarda `g`. AC-SOLO-20 |
| A5 | S3 | AC-SOLO-14 ("Ana libera") não passa: o lote LG26-03 tem 60.000 kg para 87.246 kg, e `cenLiberar` recusa | §3.5 e AC-SOLO-14: "Salvar ajuste" sem liberar; a liberação é testada com o lote elevado |
| A6 | S3 | O P1 (calcário com preço) quebra `cadc_cd06_test.py:11` e `:26-29` e `cadc_cd02_test.py:67`, que não estavam listados | P1 lista os três, com o motivo |
| A7 | S3 | O P3 põe o AG-02 no menu com o link DIA-007 → AG-03det (oculto): o L2 de `links_ocultos_test` falha | O par entra no residual "cadeia MIP" (`:39`) |
| A8 | S3 | "Usar" na linha × "Salvar" do painel: não estava definido se "Usar" grava na hora; um rascunho com 130 e o aceite de 150 ficavam vivos juntos | Ações da linha são secundárias e preenchem o rascunho; o Salvar grava. §3.2, §3.3 |
| A9 | S3 | Retirar o único insumo (KCl no T2) deixava a Adubação de cobertura com horas, custo e O.S. para espalhar nada | R07: a atividade sai do cultivo. AC-SOLO-10 |
| A10 | S3 | `sc = 60 kg` dentro do `solo.js` duplica o `PRDC.un`/`prUn`, e a aritmética decimal duplicaria os `pr*` (ENG-011/013) | R07 e P1 usam `prMul(meta, prUn(cultura).massa)` e `pr*` |
| A11 | S3 | Meta de 10.800 kg/ha (180 sc/ha, erro de digitação) ainda dá 108 kg de K₂O: extrapolação silenciosa (AGR-012, ACAG-08) | R07: faixa de 2.400 a 4.800 kg/ha. AC-SOLO-03 |
| A12 | S3 | Clique duplo em "Registrar laudo" cria LAU-2073 e LAU-2074 da mesma amostra; dois laudos validados do T2, sem regra de qual vale | R13 para todos os comandos, `recibos`, recusa de amostra repetida; R02: vale o mais recente. AC-SOLO-06/21 |
| A13 | S3 | "Aplicar plano", que é da sessão, apagava no cenário os aceites; ao recarregar, o plano volta e os aceites já sumiram | R16: o aceite guarda o plano e deixa de valer sem ser apagado |
| A14 | S3 | OS-0502 com selo: "próximo passo Ajustar" e o primário de hoje "Liberar" — duas ações primárias ou primário ambíguo | §3.5: primário "Ajustar antes de liberar" e secundário "Liberar com 2.000 kg/ha"; o selo some quando a dose da O.S. fica igual à do plano |
| A15 | S4 | O link "Sugestões pelas análises · 0" ficaria sempre visível para quem não usa análise, e o rodapé "Sem laudo validado: …" contradiz o AC-SOLO-05 | O link só aparece com 1 sugestão ou mais; o rodapé passa a "Os demais talhões seguem a dose do plano." |
| A16 | S4 | A tarefa "Amostragem de solo · T2" (IN-01/IN-03, ocultas) pede um laudo que já existe e aponta para o PLA-104, que sai; a ajuda do AG-03 cita o PLA-104; o campo "Dose informada … aguarda laudo" do AG-04 era só da REC-018 | §0 Sai e Muda |
| A17 | S4 | "hoje + 7" repete `PRAZO_REPOSICAO`, e o gatilho calculado se moveria com o dia | R18: `D2.viavel`, gravado como data fixa no aceite |
| A18 | S4 | O espelho Python do `ocorr` mudaria sem consumidor: a semente não tem aceite e o Python não lê o cenário | P4: o espelho não muda |
| A19 | S4 | "em uso desde 20/09" é impossível: a semente não tem aceite e o protótipo vive em 23/09 | R12: data do cenário; exemplo da §3.1 |
| A20 | S4 | "Repetir o lote com a mesma chave" não é reproduzível pela tela; falha parcial do lote sem regra | Gancho `__solo`; lote parcial com resultado por linha. AC-SOLO-09 |
| A21 | S4 | Selo da O.S. dito "de `soloSugestoes`" exigiria `SOLO0` e `D2` em toda tela do cenário | Selo e origem vêm do aceite gravado; `SOLO0` só no AG-02 e no SAF |
| A22 | S4 | Fonte de "talhão irrigado" (validade de 12 meses) e do mapa parcela → talhão não nomeadas; "<LD" sem regra; correção de laudo validado sem efeito definido | R02, R04 e §3.1 |
| A23 | S4 | A R09 citava ACFX-02 (conta de 10 ha × 200 kg/ha), que não trata de sugestão igual à efetiva | R09 cita 37.2 (sem ruído) |
| A24 | S4 | A R08 não dizia o que fazer com uma gessagem do plano quando o 20–40 cm não tem gatilho | R08: nada é sugerido, nem retirar |
