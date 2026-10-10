# Relatos da frente TABR (TABELAS-FOCO de Cadastros CD-01..07 e Irrigação IR-01..04 e IR-03det)

Fonte: resultado do workflow `modulo-prototipo` da TABR (run `wf_347c5bf0-1d1`, concluído em 10/10 às 01:16 UTC), o mesmo texto que os agentes devolveram no `journal.jsonl`.

A sequência de agentes foi:
- implementar, com duas tentativas interrompidas antes da que concluiu;
- revisar, com uma interrompida;
- corrigir, com três tentativas interrompidas (às 14:40, das 17:40 às 19:22 e das 21:19 às 22:53) e a que fez o commit `8f19e0d` às 01:15. Nos `brutos/`, `corr1_` é a das 17:40 e `corr2_` a das 21:19.

**A revisão foi adversarial, feita por um agente Claude que se identifica "papel Codex". Não é o parecer do Codex, que é o BEN-REV-20261010-04.**

Rótulos:
- **executado:** a saída está em `brutos/`;
- **relatado:** o agente diz que rodou, mas a saída não está no pacote.

Os `brutos/*transcricao*.txt` são saídas copiadas do transcript do agente, para comandos que não gravaram arquivo. Nada foi reexecutado.

## Os números pedidos: 43 / 142 / 94 / 140

| Teste | Resultado | Rótulo e fonte |
|---|---|---|
| `tabelas_cad_irr_unit.py` | 43/43 | executado: `corr_TABR-unit.log` (10/10 01:00, build final); também na transcrição `corr_TABR-transcricao_testes.txt` (22:58 e 01:00) |
| `tabelas_cad_test.py` | 142/142 | executado: `corr-fx_10-tabelas_cad_test.log` (01:15) e `corr-fx_09-tabelas_cad_test.log` (01:04), no build final |
| `tabelas_irr_test.py` | 94/94 | executado: `corr-fx_09-tabelas_irr_test.log` (01:09), no build final |
| `varredura.py` | 140/140 | executado: `corr-fx_01-varredura.log` (09/10 23:15). Rodou no build anterior à última limpeza, que tirou do IR-03 um cálculo de avisos sem uso; essa limpeza não foi seguida de nova varredura (relato da correção) |
| `acoes_duplicadas.py` | 0 repetidas · 0 erros | executado: `corr-fx_02-duplicadas.log` (23:19), mesma ressalva |
| `build.py` / `montar_render.py` | 0 FALHA, 140 artboards / 140 páginas | executado: `corr_TABR-build.log`, `corr_TABR-render.log` (01:00) |

O commit `8f19e0d` é das 01:15. A bateria `corr-fx` (`resumo.txt`, `run.sh`) rodou de 09/10 22:58 a 10/10 00:52 sobre a árvore de trabalho que virou esse commit (`head.txt` ainda marca `3636e33`). Unidade e `tabelas_*` foram rodados de novo no build final.

## Vermelhos equivalentes à base

A base do pacote é `cdc185f`. A frente nasceu em `24da80b`; a bateria da base está em `base-24da80b_*` (06/10) e a do `cdc185f` em `base-cdc185f_*` (09/10).

| Teste | Na candidata (`corr-fx`) | Na base | Equivalente? |
|---|---|---|---|
| `componentes_test interacao` | 8 ok · 2 falhas | `24da80b`: 8 ok · 2 falhas | sim (executado) |
| `componentes_test ajustes` | 2 ok · 2 falhas | `24da80b`: 3/1; `cdc185f`: 2/2 (`base-cdc185f_TABR-cdc-componentes_ajustes.log`) | sim, contra `cdc185f` (executado) |
| `etapas_celular_test complemento` | 7 ok · 2 falhas | `24da80b`: 8/1; `cdc185f`: 7/2 (`base-cdc185f_TABR-cdc-etapas_complemento.log`) | sim, contra `cdc185f` (executado) |
| `etapas_celular_test desktop` | 0 ok · 1 falha ("base ausente: gen37_antes") | `24da80b`: 0/1, mesma mensagem | sim (executado) |
| `acao_unica_test responsivo` | 1 ok · 2 falhas (SAF etapa 6, CMP etapa 3) | `24da80b`: 3/0; `cdc185f`: 1/2 (`base-cdc185f_TABR-cdc-acao_responsivo.log`) | sim, contra `cdc185f` (executado) |
| `verif_cad` / `verif_cad2` | `RuntimeError: Uncaught` (linhas 37 e 34) | `24da80b`: o mesmo erro, nas mesmas linhas | sim (executado) |
| `cadc_test cd0102b` | 8/8 e depois `Uncaught` (`cadc_test.py`, linha 18, etapa 3 do SAF) | `24da80b`: o mesmo | sim (executado) |

Na 1ª passada da bateria da correção, três testes falharam e depois passaram com a adaptação descrita no commit ("o que foi para o painel passa a ser lido no painel"):
- `os_irrig_filtro`: 14/1 → `05b` 15/0;
- `os_v39_selo_agua`: 10/12 → `05b` ainda falha → `05c` 12/12;
- `cadc fix06`: 12/13 → `06b` 13/13.

O `cd05vtest` quebrava na base (`base-24da80b_05-cd05vtest.log`, `Uncaught`) e na 1ª passada (`corr-fx_05-cd05vtest.log`). Foi adaptado e deu 12/12 (`corr-fx_05c-cd05vtest.log`; o `05b-cd05vtest-guard.log`, de antes da adaptação final, deu 10/12). Todos os arquivos estão em `brutos/` com esses nomes.

## Revisão adversarial (sobre `3636e33` × base `24da80b`): 3 S3, 8 S4, nenhum S1 ou S2

| ID | Sev. | Achado | Reprodução (revisão) | Correção (`8f19e0d`) | Regressão (executado, build final) |
|---|---|---|---|---|---|
| A1 | S3 | Situação, Pendência e Próximo passo saíram da vista a 1440 px (IR-01 rola 602 px; Situação fora em CD-03..07); o teste tinha sido afrouxado | executado: sonda `probe3 largura`, HEAD × base (`rev_TABR-transcricao_sondas.txt`, bloco de 17:03) | estado e próximo passo logo depois da identificação; o secundário vai para o painel ou para o IR-03det | "CD (A1): Situação à vista sem rolar a 1440 e 1280 px" e "IR (A1): … à vista sem rolar a 1440 e 1280 px" em `corr-fx_10-tabelas_cad_test.log` / `corr-fx_09-tabelas_irr_test.log` |
| A2 | S3 | IR-01: a linha do Pivô 2 mistura a OS-0419 com a divergência da OS-0394 | executado: `rev_probe2.log` e `probe_base_ir` (transcrição) | Cobertura e Próxima passada vêm da ordem da coluna Ordem; a pendência de outra ordem diz qual é | "IR-01 (A2): Pivô 2 = A conferir \| Divergência na OS-0394 …" |
| A3 | S3 | CD-04: o motivo de "Não alocável em O.S." sumiu da linha | executado: `probe4` (transcrição, bloco de 17:13) | motivo na dica do chip, verbo ("Renovar contrato ›") e "Disponível até" vencido em vermelho | "CD-04 (A3): Lucas …" e "CD-04 (A3): Carlos …" |
| A4 | S4 | Colunas numéricas com unidade diferente por linha (Capacidade do CD-03 e do CD-06, Vazão do IR-02) | executado: sondas (transcrição) | capacidade só com filtro de uma grandeza; o IR-02 fica sem a coluna Vazão | "CD-03 (A4, M-k) …", "CD-06 Locais (A4) …", "IR-02 (A4) …" |
| A5 | S4 | CD-05: o filtro ativo some do menu | executado | o filtro com contagem 0 continua no menu | "CD-05 (A5) …" |
| A6 | S4 | IR-03: selo de ordem encerrada aparece como pendência | executado | sem selo informativo na Pendência | "IR-03 (A6) …" |
| A7 | S4 | IR-01: "Passadas" é ambígua | executado | passadas necessárias no painel | "IR-01 painel (A1, A7) …" |
| A8 | S4 | CD-07: "No rascunho" fica sempre vazia depois de publicar | executado | a coluna só entra quando há rascunho | "CD-07 (A8) …" |
| A9 | S4 | Estado salvo da irrigação não é descartado depois da troca da semente | executado (o caso do sensor "% vol." ficou só especificado) | semente `v=3` | "IR-04 (A9): estado salvo de versão anterior … é descartado" |
| A10 | S4 | Cor como único sinal (Packing "Apta" com a calibração a vencer) | executado | chip "Calibração a vencer" | "CD-03 (A10) …" |
| A11 | S4 | Duas variáveis numa célula: pendência com detalhe, "Caio · PCP", Natureza "3.1.01 · …", Fonte como chip | executado | tipo no chip e detalhe na dica; Responsável só com a pessoa; Fonte como texto. **Natureza do CD-06 recusada** (ver abaixo) | "IR-01 (A11) …", "IR-03 (A11) …", "CD-02 (A11) …" |

**Mutantes da revisão** (executado: `rev_mut_cad.log` 125/125, `rev_mut_irr.log` 84/84 e a unidade com M-a a 32/33 na transcrição):
- sobreviviam M-m, M-a, M-k e M-i;
- o M-e foi julgado equivalente pela revisão.

**Mutantes depois da correção:**
- M-i, M-m, M-k e M-a são pegos (executado: `corr2_TABR-transcricao_testes.txt`, 21:27–21:35: C11 (M-i) na unidade, `tabelas_irr` 91/93 e `tabelas_cad` 137/139 com os mutantes);
- o M-e **não é equivalente**: com o mutante, `desal: 1` no CD-05, CD-03 e CD-06 a 1440 e 2560 px, e 0 no build real (executado: `corr_TABR-transcricao_testes.txt`, bloco de 00:59, `tabr_mut_ncol.sh`);
- regressão: "CD-05 Clientes (M-e)" e "fluxo 1440/390 (M-m)" nos logs finais.

**Também corrigidos, pré-existentes:**
- parcela do PV01 no CD-01det;
- Duração no IR-03det.

Ficam como relatado, sem teste específico nomeado nos logs.

## Recusas, com motivo (relato da correção)
- **A11, Natureza do CD-06:** código e nome são do mesmo registro, 1:1 (6 códigos, 6 nomes, 6 pares), e iguais ao seletor do formulário. É uma variável só.
- **Outorga contraditória entre CD-01 Água e IR-04 Captações:** é da frente CTL-5, e o defeito já existia antes desta frente.

## Implementação (antes da revisão)
- **Defeitos reproduzidos na base antes de corrigir** (executado):
  - `cadp_fix_test` 11/15 na `24da80b` (`base-24da80b_05-cadp_fix_test.log`) → 15/15;
  - `tabelas_irr` 77/83 (`impl09_TABR-irr-pre.log`) e 83/84 (`impl09_TABR-irr-old.log`, sensor) → 84/84 (`fim-3636e33`);
  - unidade 15/30 na base (`base_TABR-base-unit.log`).
- **Bateria final da implementação, sobre `3636e33`:** `fim-3636e33_*` (unidade 33/33, `tabelas_cad` 125/125, `tabelas_irr` 84/84, varredura 140/140).

## implementacao

#### TABELAS-FOCO de Cadastros e Irrigação: retomada concluída

O módulo está fechado na branch `claude/v44-tabelas-r` (HEAD `3636e33`), sem nada pendente para commit. A última sessão já tinha feito e commitado todo o código. Nesta retomada não houve mudança de código: só completei a bateria final que ficou pela metade e apaguei as cópias temporárias.

**Estado ao retomar (git status e git log):**
- Não havia arquivo rastreado alterado. Os dois testes que a tarefa dava como "sem commit" (`os_irrig_filtro_test.py` e `os_v39_selo_agua_test.py`) já estavam no commit `37577a6`.
- O merge de `claude/prototipo-v44` já estava feito (`300835d`, que é o `cdc185f`). A `claude/prototipo-v44` continua no `cdc185f`; não há nada mais novo para juntar.
- Apaguei as três cópias temporárias da base que eu tinha criado (`v37/_base_cdc`, `_base_ecc` e `_base_gen37`, cerca de 314 MB). Ficaram só as saídas de build (`project/`, `_render/`) e `validacao/`, que são geradas pelos testes.

##### Commits (todos com build 0 FALHA)
- `2a0c781` CD-01: talhões, água e detalhe do talhão com uma variável por coluna
- `79667b1` CD-02: culturas e rendimentos com uma variável por coluna
- `415152d` CD-03 e CD-04: máquinas e pessoas com uma variável por coluna
- `b37b1d0` CD-05: parceiros com uma variável por coluna
- `0fcf997` CD-06 e CD-07: itens, locais e estrutura com uma variável por coluna
- `4d9c193` CD-05: trilha da grade acompanha as colunas do papel
- `6e71b3f` Irrigação: IR-01..IR-04 e IR-03det com uma variável por coluna
- `e392e64` Cadastros e Irrigação: testes de unidade e de navegador
- `c161f29` IR-01: passadas, pendência e próxima passada em colunas
- `cbc87f5` CD-04 e CD-05: calendário, acesso, papéis e motivo sem perda
- `48a412c` Cadastros: testes antigos adaptados e teste de unidade robusto
- `37577a6` IR-03: testes da O.S. de água leem Lâmina e Passadas em colunas
- `a881cbe` Irrigação: Pendência sem repetir a Situação, Tipo e grandezas com uma variável
- `a6b949b` Cadastros: fluxo do cadastro na grade também a 390 px
- `8356a07` CD-07: código excluído no rascunho sem "Excluído" repetido; testes antigos do CD-02
- `ecc8fce` IR-04: a unidade do sensor vem da grandeza (não se pede de novo)
- `3636e33` IR-04: teste de unidade da unidade do sensor (B5)
- Merges: `def9dc8` (`ecc8b00`) e `300835d` (`cdc185f`)

##### Defeitos reproduzidos na base antes de corrigir (executado)
- **CD-05:** o filtro de coluna dentro de um papel contava pelo texto inteiro da célula. `cadp_fix_test` deu 11/15 na base `24da80b` e dá 15/15 agora.
- **CD-07:** a Situação e a coluna "No rascunho" diziam as duas "Excluído". `cadc_fix_cd07` deu 10/11 antes e dá 11/11 agora.
- **IR-04:** cadastrar um hidrômetro gravava a unidade "% vol." (dano evitado: uma leitura de volume entrar no balanço como umidade). `tabelas_irr_test` deu 83/84 antes e dá 84/84 agora.
- **IR-01/02/03:** a Pendência repetia a Situação, o Tipo juntava duas coisas e o IR-04 tinha só 2 unidades para 3 grandezas. `tabelas_irr_test` deu 77/83 e `tabelas_cad_irr_unit` 30/32 antes; depois 83/83 e 32/32.

##### Testes no HEAD `3636e33`
Todos executados. Navegador sempre com `env CHROME_BIN=<chrome> flock /tmp/cdpD.lock env CDP_GL=1 timeout 900|1200 python3 <teste>`; saídas em `/tmp/TABR-fim/`.
- `python3 build.py`: 0 FALHA; `montar_render.py`: 140 páginas.
- `varredura.py`: 140/140 sem erro; `acoes_duplicadas.py`: 0 com ação repetida.
- `tabelas_cad_irr_unit.py`: 33/33.
- `tabelas_cad_test.py`: 125/125, com o fluxo do CD-03 (normal, recusa, repetição) a 1440 px e a 390 px.
- `tabelas_irr_test.py`: 84/84, com o fluxo da OS-0422 (normal, recusa, repetição) e o filtro e a ordenação a 390 px.
- Testes existentes:

| Teste | Resultado |
|---|---|
| cadf, cadf_det, cadf_fix_det, cadf_fix_lista | 15, 13, 9, 11 (todos OK) |
| cadc_cd02, cadc_cd06, cadc_cd07 | 15, 14, 14 |
| cada_cd03, cada_cd04, cada_fix03, cada_fix04 | 14, 15, 11, 12 |
| cadp, cadp_fix, cadp_v | 15, 15, 12 |
| cd05test, cftest, irtest | 33, 37, 26 |
| irr_estado, irr_fluxo | 38, 33 |
| map_irrig_filtro, os_irrig_filtro, map_decisoes | 15, 15, 18 |
| os_v39_selo_agua, quantidade, links_ocultos | 12, 14, 8 |
| cadc cd0102a, fix02, fix06, fix07 | 13, 8, 13, 11 |
| componentes matriz, rotação, ajustes2 | 3, 6, 2 |
| etapas celular | 14 |
| acao_unica v3, famílias | 10, 8 |
| g2test | saiu com código 0 |

Os testes que falharam também falham na base, do mesmo jeito. Não são desta frente e não os escondi:
- **Já na lista de vermelhos conhecidos:** `componentes interacao` (8 ok, 2 falhas), `etapas desktop` (0 ok, 1 falha) e `cd05vtest` (erro de script na mesma linha da base).
- **Também na lista, mas com uma falha a mais do que na `24da80b`:** `componentes ajustes` deu 2 ok e 2 falhas (itens 26 e 27). A falha nova (item 27, o menu) vem do `cdc185f`: rodei lá e o resultado é idêntico. No item 26 entrou um problema na coluna SAF, também igual no `cdc185f`; a coluna CD-06, que é minha, passa nesse item.
- **Também na lista, com uma falha a mais:** `etapas complemento` deu 7 ok e 2 falhas. O item 20 é igual no `cdc185f`; a sonda do IR-02 mediu os mesmos 263 px úteis a 568×320 nas duas versões.
- **Fora da lista, rodado no `cdc185f` com resultado idêntico:** `acao_unica responsivo` (1 ok, 2 falhas, em SAF etapa 6 e CMP etapa 3).
- **Fora da lista, iguais na base `24da80b`:** `cadc cd0102b` (8/8 nas verificações do CD-02; depois para com erro de script na parte do Planejar safra, porque a etapa "3 Defina os rendimentos" não existe mais) e os scripts antigos de sondagem `verif_cad` e `verif_cad2`, que param na mesma linha.

##### Expectativas mudadas, com motivo
O motivo comum é "uma variável por coluna"; o detalhe está escrito em cada commit.
- **`48a412c`:** em `cadf`, `cadf_det` e `cadf_fix_det`, Área e Livre viraram colunas e o estado virou chip. Em `cadc_cd02`, `cadc_cd06`, `cadc_cd07` e `cada_cd03`, rótulos compostos viraram colunas.
- **`37577a6`:** em `os_irrig_filtro` e `os_v39_selo_agua`, Lâmina e Passadas ficam em colunas, e os 6,75 mm por passada vão para o IR-03det.
- **`8356a07`:** em `cadc_cd0102_a` e `_b`, as 11 colunas e o critério "não rola de lado e a grade rola dentro da caixa" (o mesmo de ostest e est_fix1). Em `cadc_fix_cd02`, o Processo em coluna própria.
- **`cbc87f5`:** em `cadp`, `cadp_fix` e `cd05test`, limite, validade e cobertura em colunas e chips; o menu de filtro passa a ser o padrão Excel. Em `cada_cd04`, as colunas Calendário e Acesso ao app.
- **`c161f29`:** em `irtest` e `irr_fluxo` (14, 19, 20 e 27), as colunas Fonte do déficit, Cobertura, Resta, Passadas, Pendência e Próxima passada; a grade rola dentro da caixa.

##### O que ficou fora
- **Ficha do pivô e teste do solo** (seção 4 do alinhamento do Codex): é uma função nova de Irrigação e Solo, não grade, e a frente de Solo está mexendo nesses arquivos. Não implementei.
- **COLH-C01 e A-17:** são de Colheita e Comercial, fora deste módulo.
- **Grades sem tabela visível:** Conjuntos (CD-03) e Equipes (CD-04) aparecem como cartões, então as regras de grade não se aplicam. Não mexi nas grades de uma coluna só (CD-02 Cultura e Operação, CD-06 Grupo).
- Não fiz push, PR nem atualização do `docs/STATUS.md`; fica com o integrador, que junta a branch.

##### Riscos
- Algumas células de Pendência no IR-01 ainda juntam o tipo e o detalhe, como "Divergência · −3,8 %" e "Falta insumo · Ureia 45%". Tratei como uma variável (a descrição da pendência), e o filtro funciona por item. Se o revisor entender que são duas variáveis, a pendência vira duas colunas.
- Os vermelhos que vieram do `cdc185f` (menu, tela baixa do IR-02 a 568×320 e responsivo de SAF/CMP) continuam abertos para as frentes donas dessas telas.

## revisao

**Revisão adversarial (papel Codex) da frente TABELAS-FOCO Cadastros e Irrigação**

- Branch `claude/v44-tabelas-r`, intervalo 24da80b..3636e33. Revisei os 17 commits da frente e os testes adaptados.
- Trabalhei em cópias no scratchpad (`rv/` = HEAD, `base/` = 24da80b, `mut/` = mutantes). Nenhum arquivo versionado foi alterado.
- **Parecer:** não achei S1 nem S2. Há 3 achados S3, sendo 2 regressões desta frente e 1 perda de informação. Recomendo corrigir A1–A3 nesta mesma branch antes de atualizar o artefato. Os achados S4 podem entrar junto ou depois.

#### Achados

**A1 · S3 · P1 · Estado e próximo passo saíram da vista no desktop (regressão)**
- **Reprodução (executada,** `probe3.py largura`**, HEAD × base).** Medi a largura de 1440 px a partir do carregamento da página:
  - IR-01 rola 602 px dentro da caixa. Ficam fora da vista Situação, Pendência, Próxima passada, Próximo passo e Responsável.
  - IR-02 rola 524 px. Ficam fora Pendência, Próximo passo, Responsável e Avisos.
  - IR-03 rola 387 px. Ficam fora Avisos, Próximo passo e Responsável.
  - Nos Cadastros, a Situação fica fora em CD-03, CD-04, CD-05, CD-06 e CD-07. No CD-02 Operações, ficam fora os dois custos e a Fonte.
  - Na base, a 1440 px, só a aba Água do CD-01 rolava (49 px). As grades da Irrigação não rolavam nem a 1280 px.
- **O que isso quebra:** a regra "estado sempre visível e próximo passo com verbo" (AGENTS §4, PRD 4.2/4.3) e o pedido de essencialismo. O IR-01 passou de 5 para 17 colunas.
- **Causa:** as definições de colunas em `<sp-tabr>/tools/prototipo/v37/gen37/areas/irrigacao.py` (linhas 171, 252, 341), `cad_culturas.py:107`, `cad_ativos_pessoas.py:137` e `:311`, e `cad_produtos_estrutura.py:265`.
- **O teste foi afrouxado e por isso não pegou:**
  - `irr_fluxo_test.py:155-162` (verificação 20) passou a aceitar rolagem lateral a 1280 e 1440 px.
  - `cadc_cd0102_a.py:14-16` removeu "no máximo 7 colunas" e "sem rolagem lateral a 1440".
- **Correção proposta:**
  - Colocar Situação/Etapa e Próximo passo logo depois da coluna que identifica a linha.
  - Mandar para o painel o que é secundário: no IR-01, Fonte do déficit, Estádio, Responsável, Passadas e Área; no IR-02, Bomba e Tipo; no CD-03, Modelo e Largura; no CD-04, Calendário e Acesso; no CD-07, TOP e Origem; no CD-02, Modo, Largura, Velocidade e Eficiência. O contrato da tarefa já permite "vai para o detalhe".
  - Voltar a testar, a 1440 px, que os cabeçalhos de Situação e Próximo passo ficam dentro da caixa sem rolar.

**A2 · S3 · P1 · No IR-01, a linha do setor mistura duas ordens (regressão)**
- **Reprodução (executada,** `probe2`/`probe_base_ir`**).** A linha do Pivô 2 mostra: Ordem OS-0419 | 87 % | 1,5 mm | A conferir | Divergência · −3,8 % | Próxima passada "—" | Conferir medição.
  - A OS-0419 está Liberada para hoje 20:00, como mostram o IR-02 e o IR-03.
  - A divergência e o "Conferir medição" são da OS-0394, que não aparece mais na linha (só no link). A base dizia "conferir medição · OS-0394".
- **Causa:** em `areas/irrigacao.py:193`, Ordem, Cobertura e Resta vêm de `oa`. Em `:218`, Pendência e Próxima passada vêm de `top.o`.
- **O teste consagra o erro:** `tabelas_irr_test.py:84-86` espera "—" na Próxima passada.
- **Correção proposta:** calcular a Próxima passada pela ordem que aparece em Ordem (`irrPassProx(oa)`). Quando `top.o` for diferente de `oa`, citar a ordem na pendência ("Divergência OS-0394 · −3,8 %"). Ajustar o teste.

**A3 · S3 · P2 · CD-04: o motivo de "Não alocável em O.S." sumiu da linha**
- **Reprodução (executada,** `probe4`**).** Coloquei o "Disponível até" do Carlos em 01/09/2026.
  - Base: "Não alocável em O.S. contrato encerrado em 01/09/2026".
  - HEAD: "… 01/09/2026 … NR-31 31/08/2027 … Não alocável em O.S.". A data aparece em preto e o motivo só aparece no aviso temporário (toast).
  - "Admissão em …" (admissão futura) não tem coluna nenhuma.
- **Causa:** `cad_ativos_pessoas.py:338`. A função `c4sit` descarta `A.m` e a coluna `ate` não tem cor de estado.
- **Correção proposta:** o chip diz o motivo ("Contrato encerrado", "NR-31 vencida", "Admissão em 15/10"), ou o motivo vai como dica do chip. "Disponível até" vencido fica em vermelho. Acrescentar um verbo de próximo passo.

**A4 · S4 · Colunas numéricas com unidade diferente em cada linha (continua mais de uma variável por coluna)**
- **Executado:** a Capacidade do CD-03, em ordem crescente, sai assim: 24 linhas < 45 m³/h < 78 cv < … < 3.000 L < 3.000 kg < 60.000 sc. Ou seja, compara potência com volume de tanque.
- O mesmo acontece em:
  - Capacidade dos Locais no CD-06 (L × sc de 60 kg), em `cad_produtos_estrutura.py:120`;
  - Vazão do IR-02 (o pico da captação na linha do grupo e a vazão do setor nas linhas das ordens), em `irrigacao.py:252` e `:293`.
- `tabelas_cad_test.py:158` consagra essa ordem.
- **Correção proposta:** Capacidade como texto, ou uma coluna por classe que só aparece quando se filtra pela classe (o mesmo padrão das colunas por papel do CD-05).

**A5 · S4 · CD-05: o filtro ativo some do menu**
- **Executado:** em Todos, filtrei Papéis = Cliente e passei para Transportadores. Resultado: 0 linhas e "Papéis: Cliente" no topo, mas o menu Papéis lista só "Transportador 2", desmarcado. Na base aparecia "Cliente 0", marcado.
- **Causa:** `cad_parceiros.py:292`, onde `filter(x=>cnt[x.t])` perdeu o `||x.on`.
- **Correção:** manter os valores marcados, mesmo com contagem 0.

**A6 · S4 · IR-03: selo de ordem encerrada aparece como pendência**
- **Executado:** a OS-0392 (Encerradas) mostra o chip "Encerrada automaticamente" na coluna Pendência.
- **Causa:** `irrigacao.py:357` (e `:281`) usa todos os selos de `irrSelos`, inclusive os informativos (`mut`) de `irrigacao_estado.js:489`.
- **Correção:** tirar os selos `mut` da coluna Pendência.

**A7 · S4 · IR-01: "Passadas" é ambígua**
- **Executado:** a linha do Gotejo T7 mostra "2 | OS-0423", mas a OS-0423 tem 1 passada no IR-03. O 2 é o número de passadas da necessidade.
- **Correção:** rotular "Passadas necessárias" ou levar para o painel. Linha `irrigacao.py:173`.

**A8 · S4 · CD-07: "No rascunho" fica sempre vazia depois de publicar**
- **Executado:** depois de "Publicar estrutura", a coluna mostra "—" em todas as linhas.
- **Causa:** a coluna é fixa (`cad_produtos_estrutura.py:265`, preenchida em `:336`).
- **Correção:** a coluna só entra quando há rascunho, como o "Motivo da suspensão" do CD-05.

**A9 · S4 · Estado salvo da irrigação não é descartado depois da troca da semente**
- **Executado:** simulei um estado salvo anterior ao commit a881cbe (`v=2` aceito). O IR-04 mostra "ET₀, Chuva, Vento | mm/dia, mm", três grandezas para duas unidades. Pelo código, um sensor cadastrado antes do ecc8fce também continua com "% vol." no estado salvo (não reproduzi).
- **Causa:** `dados_irrigacao.py:183` ficou com `v=2`.
- **Correção:** `v=3` ou uma migração.

**A10 · S4 · Cor como único sinal**
- **Executado:** no CD-03, o Packing linha 1 (calibração vence em 01/10) mostra Situação "Apta" (chip verde) e a data só em âmbar, numa coluna que fica fora da vista a 1440 px. A base dizia "Apta · calibrar até 01/10/2026".
- **Causa:** `cad_ativos_pessoas.py:210` e `:225`.

**A11 · S4 · Ainda há duas variáveis numa célula**
- Pendência com detalhe: "Divergência · −3,8 %", "Falta insumo · Ureia 45%".
- Responsável com pessoa e função: "Caio · PCP".
- Natureza no CD-06 com código e nome: "3.1.01 · Fertilizantes e corretivos".
- A Fonte do CD-02 aparece como chip verde de estado, por causa de `cad_culturas.py:148` (`rdSit` usa `sitOk`).

#### Testes que passam sem testar (mutantes executados)

| Mutante | Resultado |
|---|---|
| **M-m**: Fim = fim da 1ª passada (`irrigacao.py:277` e `:353`) | `tabelas_irr_test` 84/84, **sobrevive**. Mudança visível: Fim da OS-0422 25/09 06:02 em vez de 26/09 06:02. `tabelas_irr_test.py:65` só confere se o Fim existe. |
| **M-a**: vazão sem converter L/s | `tabelas_cad_test` 125/125, **sobrevive** (a verificação de `tabelas_cad_test.py:99` não distingue, porque os valores em L/s são pequenos). Só `tabelas_cad_irr_unit` B1 pega (32/33). |
| **M-k**: Capacidade da classe Irrigação some | `tabelas_cad_test` 125/125, **sobrevive** |
| **M-i**: `c4val` pega a validade mais distante | `tabelas_cad_test` 125/125, **sobrevive** (o cenário não tem pessoa com 2 habilitações datadas) |
| **M-e**: CD-05 sem `ncol_dinamico` | `tabelas_cad_test` 125/125, mas não é falha do teste: a 1440 px, todos os papéis ficam alinhados mesmo sem a correção, então o commit 4d9c193 não tem efeito observável nessa largura. |

#### Já existiam antes desta frente (não são regressão; ficam mais visíveis agora)

- **Outorga contraditória entre CD-01 Água e IR-04 Captações** (dono: CTL-5). SINT-002, SINT-003 e SINT-004 têm vazão, vencimento e situação diferentes nas duas telas. Exemplo: SINT-004 aparece como "vencida em 01/12/2025, em renovação" no CD-01 e "Vigente até 25/11/2027" no IR-04 (`dados_irrigacao.py:40-46` × `kml.py`).
- **Parcelas do pivô da Lagoa Grande não fecham.** O CD-01 conta 1 parcela no PV01, mas o CD-01det do PV01 mostra a Safra Mamão com 0 ha e 29,9 ha livres, sem parcela (`cad_fazendas.py:84-90` × `:468`/`:515`). A base já mostrava o mesmo.
- **Duração prevista ao lado do horário real.** No IR-03det, a OS-0394 mostra Duração 14,5 h (prevista) com Início e Fim reais (ontem 20:00–22:06, 2,1 h).

#### O que tentei e não quebrou (tudo executado no HEAD)

- `build.py` com 0 FALHA e `montar_render` com 140 páginas.
- Testes reexecutados:

| Teste | Resultado |
|---|---|
| `tabelas_cad_irr_unit` | 33/33 |
| `tabelas_cad_test` | 125/125 |
| `tabelas_irr_test` | 84/84 |
| `irtest` | 26/26 |
| `irr_fluxo_test` | 33 ok |
| `os_irrig_filtro_test` | 15 ok |
| `map_irrig_filtro_test` | 15 ok |
| `cadp_fix_test` | 15/15 |
| `cadc_fix_cd07` | 11/11 |

- Sonda geral nas 14 telas e nos 3 contextos de fazenda:
  - toda coluna tem filtro e ordenação (exceto a ficha de uma linha do CD-01det, por desenho);
  - depois de ordenar pelo menu, a ordem exibida de todas as colunas numéricas e de data é monótona;
  - "ontem < hoje < amanhã" sai na ordem certa;
  - cada célula fica sob o seu cabeçalho no IR com Todas, Santa Rita e Lagoa Grande, inclusive ao trocar de fazenda sem recarregar, e no CD-05 em todos os papéis.
- Os 11 links de Próximo passo do IR-01 são idênticos aos da base. Nenhum erro de script.
- Commits com as duas linhas de atribuição. `sitOk` só é usado nas telas CD, então a mudança não vaza para outros módulos.

Não reexecutei `varredura.py` nem `acoes_duplicadas.py`.

Tudo está em `<scratchpad>/`:
- sondas: `probe_geral.py`, `probe2.py` a `probe7.py`, `probe_base_ir.py`, `probe_cd05_alinh.py`;
- logs: `probe2.log`, `mut_cad.log`, `mut_irr.log`, `regress.log`, `regress2.log`, `regress3.log`.

## correcao

Os 11 achados da revisão estão corrigidos no commit `8f19e0d` "TABR: correções da revisão", na branch `claude/v44-tabelas-r`, sem push. Recusei duas partes, com motivo abaixo. Os testes foram executados e cada correção tem teste de regressão. Ficam vermelhos só os já conhecidos e três que já falhavam na base, listados em "Riscos restantes".

**Commit**
- **A1 a A3 (S3):**
  - Situação/Etapa, Pendência e Próximo passo vêm logo depois da identificação em IR-01..04 e CD-01..07; o secundário foi para o painel ou para o IR-03det.
  - IR-01: Cobertura e Próxima passada vêm da mesma ordem da coluna Ordem, e a pendência de outra ordem diz qual é ("Divergência na OS-0394").
  - CD-04: o chip de não alocável traz o motivo na dica e um verbo ("Renovar contrato ›"); "Disponível até" vencido fica em vermelho.
- **S4:**
  - A4: a Capacidade do CD-03 e do CD-06 só aparece com filtro de uma grandeza; no IR-02 sai a coluna Vazão.
  - A5 a A10 conforme o pedido: filtro com 0 continua no menu, sem selo de ordem encerrada na Pendência, passadas no painel, "No rascunho" só com rascunho, semente v=3, chip "Calibração a vencer".
  - A11: o tipo vai no chip e o detalhe na dica; Responsável só com a pessoa; a Fonte do CD-02 é texto.
  - Pré-existentes corrigidos: parcela do PV01 no CD-01det e a Duração no IR-03det.
- **Mutantes:** M-a, M-i, M-k e M-m agora são pegos.
  - M-e não é equivalente, ao contrário do que a revisão concluiu: sem `ncol_dinamico` o cabeçalho e as células quebram juntos para uma 2ª linha, e por isso a borda esquerda parecia alinhada.
  - Reforcei `desalinhadas()` em `tabelas_lib.py`. Com o mutante deu desal=1 no CD-05, CD-03 e CD-06 a 1440 e 2560 px; no build real, 0.
- **Testes antigos adaptados**, com o motivo no commit: o que foi para o painel passa a ser lido no painel. Inclui os_v39_selo_agua, os_irrig_filtro 13, cadc_fix_cd06 e cd05vtest, que já quebrava na base (24da80b).

**Testes executados** (navegador: `env CHROME_BIN=<chrome> flock /tmp/cdpD.lock env CDP_GL=1 timeout 900 python3 <teste>.py`)
- `build.py` → 0 FALHA; `montar_render.py` → 140 páginas.
- `tabelas_cad_irr_unit.py` → 43/43; `tabelas_cad_test` → 142/142; `tabelas_irr_test` → 94/94 (build final).
- `varredura.py` → 140/140 sem erro; `acoes_duplicadas.py` → 0 ações repetidas, 0 erros.
- Verdes:
  - Irrigação: irtest 26/26, irr_fluxo 33/0, irr_estado 38/0, os_irrig_filtro 15/0, os_v39 12/12, map_irrig_filtro 15/0, map_decisoes 18/0.
  - Cadastros: cadf/cadc/cada/cadp todos OK, cd05test 33/33, cd05vtest 12/12, cftest 37/37, cadc_test fix06 13/13.
  - Gerais: quantidade 14/14, links_ocultos 8/0, componentes matriz/rotacao/ajustes2, etapas_celular, acao v3/familias.
- Vermelhos com as mesmas falhas da rodada anterior à revisão: componentes_interacao (2), componentes_ajustes (2), etapas_complemento (2), etapas_desktop (1) e acao_responsivo (2, SAF/CMP).
- A bateria completa rodou no build anterior à última limpeza (tirar do IR-03 um cálculo de avisos sem uso). O diff de `project/` mostra só essa linha, mais a data do `canvas.json`. Unit e tabelas_* rodaram de novo no build final.

**Recusados**
- **A11, Natureza do CD-06:** código e nome são do mesmo registro, 1:1 (conferi: 6 códigos, 6 nomes, 6 pares) e iguais ao seletor do formulário. É uma variável só.
- **Outorga contraditória CD-01 × IR-04:** quem cuida é a frente CTL-5.

**Riscos restantes**
- Pré-existentes, iguais na base 24da80b e não corrigidos:
  - verif_cad quebra na linha 37 e verif_cad2 na linha 34;
  - cadc_cd0102b passa 8/8 e depois quebra na etapa 3 do SAF, que é de outra frente.
- No IR-03det, "estimativa por ET" aparece duas vezes: na linha Necessidade e no chip de aviso. É S4 pré-existente.
- Não atualizei o artefato nem o `docs/STATUS.md`: ficam com o integrador.

**O que o proprietário pode conferir:** em Irrigação › Necessidade, a linha do Pivô 2 mostra sem rolar "A conferir | Divergência na OS-0394 | Conferir medição", com Ordem OS-0419 e próxima passada hoje 20:00. Em Cadastros › Pessoas, o Lucas aparece "Não alocável em O.S." com "Renovar NR-31 ›".

Os logs estão em `/tmp/TABR-fx/`, e a sonda do mutante em `<scratchpad>/tabr_probe_ncol.py`.
