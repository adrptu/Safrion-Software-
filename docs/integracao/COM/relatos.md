# Relatos da frente COM (Comercial e logística: VEN, EXPED e PCOM; P1–P7 e A-17)

Fonte: resultado do workflow `modulo-prototipo` da COM (run `wf_b1cf603b-990`, concluído em 09/10 às 22:52 UTC), o mesmo texto que os agentes devolveram no `journal.jsonl`.

A sequência de agentes foi:
- especificar e revisar a especificação, em 06/10;
- implementar, com três tentativas interrompidas antes da que concluiu;
- revisar, com duas interrompidas;
- corrigir, com três interrompidas.

O trabalho da última tentativa de correção, que fez o commit `29cdc6e`, retomou o da tentativa anterior. **A revisão foi adversarial, feita por um agente Claude separado. Não é o parecer do Codex, pedido em COM-REV-20261010-01.**

Rótulos:
- **executado:** a saída está em `brutos/`;
- **relatado:** o agente diz que rodou, mas a saída não está no pacote.

Os `brutos/*transcricao*.txt` são saídas copiadas do transcript do agente, para comandos que não gravaram arquivo. Nada foi reexecutado.

## Os quatro S2

O relato da revisão abre com "4 achados S2, 7 S3 e alguns S4", mas só A1, A2 e A3 levam o rótulo S2 no texto. O A1 junta dois danos diferentes do mesmo defeito: a entrega confirmada sem escolha, sem comando para desfazer, e a reserva criada sem escolha de lote. **Esta tabela trata os dois em linhas separadas. A separação é leitura de quem montou o pacote, não do revisor.**

| # | Achado (revisão sobre `bdc5ca8`) | Reprodução | Correção em `29cdc6e` | Prova depois da correção |
|---|---|---|---|---|
| S2-1 (A1, saída → entrega) | Duplo clique de mouse (120 ms) em "Confirmar saída da RM-0002" grava a saída e a **entrega** (26/09, Rui), sem ninguém escolher data nem "Recebido". Não existe comando para desfazer a entrega. | executado: `rev_COM-transcricao_sondas.txt`, bloco de 17:52, `dbl_test.py saida`. Saída: `entrega {'d': '2026-09-26', 'quem': 'Rui (expedição)'}` e título vencendo em 24/10 | `areas/producao.py`: `PR_TRAVA_MS=400` e `prGuarda`. O clique com `detail ≥ 2` e qualquer clique até 400 ms depois de gravar não agem. `areas/vendas.py`: "Confirmar entrega" abre sem data nem "Recebido" e recusa com "Escolha \"Recebido tudo\" ou \"Com devolução\"" | executado: `corr_COM-comercial_revisao_test.py.log` (33/33), modo `duplo`, 7 OK A1. Um deles: "a saída grava uma vez e a entrega NÃO é confirmada pelo 2º clique". Também `corr_COM-rev.log` (21:43, 33/33) e `corr_COM-rdc.log` (2/2) |
| S2-2 (A1, venda ou saca → reserva) | Duplo clique em "Registrar venda" cria o PV-039 **e** a RS-0002 (100 sc do L10-031). Em "Registrar a saca", cria a RS-0002 (125 sc), sem escolha de lote. | executado: `rev_COM-dbl_test_header_saca_venda.log`, modos `saca` e `venda` | mesma trava `prGuarda` / `PR_TRAVA_MS` | executado: mesmo log, OK A1 "Registrar venda: PV-039 gravada e nenhuma reserva feita pelo 2º clique", "Registrar a saca: … nenhuma reserva nova" e "passado o intervalo, o clique deliberado em Reservar age" |
| S2-3 (A2, "latente": só pelo comando, porque a tela remove duplicatas) | Lote repetido na carga: com `L39-133` duas vezes, a saída de 10.000 kg baixa 5.000 kg da reserva do PV-038. O físico fica em 2.050 kg contra 7.050 kg reservados. | executado: `rev_COM-transcricao_sondas.txt`, bloco de 17:49:21 (`p3.js`, `saldo depois {"fis":2050,"res":7050}`) | `comercial.js`: `comProgramar` recusa lote repetido ("Lote repetido na carga…"); `comLotesRm` agrega por lote; pós-condição em `comSair` recusa a saída se o físico ficar abaixo do reservado | executado: `corr_COM-unit.log` (105/105) com RV-A2, RV-A2b e RV-A2c. Vermelho no código da revisão: `corr1_COM-transcricao_testes.txt`, bloco de 18:32:25, FALHOU 87/103 com RV-A2, A2b e A2c em FALHA (1ª tentativa de correção, testes novos sobre `comercial.js`, `producao.js`, `g2lib.js`, `areas/producao.py` e `areas/vendas.py` de `bdc5ca8`). Mutante M01 morto: `corr_COM-mut1.log` |
| S2-4 (A3) | Lote devolvido liberado por qualquer perfil e gravado como "Qualidade (Marta)". Com a Dora, "Liberar L39-134" aparece verde e grava `quem: "Qualidade (Marta)"`. | executado: `rev_ui_test.log`, caso B1 | `producao.js`: `prLiberarLote(c, lid, ator)` exige o papel qualidade ou agrônomo (`cenExigeUm`) e grava quem agiu. `areas/producao.py`: `prPodeLote` só mostra o verde a quem pode e, aos outros, mostra quem decide. `g2lib.js`: perfil "Marta · Qualidade". **Ajuste:** a regra é a mesma do BEN integrado (qualidade ou agrônomo), não "qualidade ou gestor" como a revisão propôs | executado: `corr_COM-unit.log`, RV-A3, A3b e A3c (vermelhos no mesmo bloco de 18:32:25); `corr_COM-comercial_revisao_test.py.log`, modo `qualidade`, 4 OK A3; `corr_COM-producao_fluxo_test.py.log` (67/67), que grava "liberado por Ana (agrônoma)" |

Limites declarados pela correção:
- **relatado:** o toque duplo lento num celular real não foi testado;
- a trava é de 400 ms, contra os cerca de 800 ms sugeridos;
- `acoes_duplicadas.py` continua ignorando o painel lateral.

## Achados A1–A12 da revisão e o tratamento

| ID | Sev. | Achado | Reprodução (revisão) | Correção (`29cdc6e`) | Regressão |
|---|---|---|---|---|---|
| A1 | S2 | Duplo clique humano executa o próximo comando | executado (ver S2-1 e S2-2) | trava de 400 ms + entrega sem padrão | `comercial_revisao_test` `duplo` |
| A2 | S2 latente | Lote repetido na carga baixa a reserva de outra venda | executado (S2-3) | recusa de duplicata, agregação e pós-condição | RV-A2, A2b, A2c |
| A3 | S2 | Qualquer perfil libera o lote devolvido | executado (S2-4) | papel qualidade ou agrônomo, Marta | RV-A3 a A3c; `qualidade` |
| A4 | S3 | Venda com a carga em trânsito aparece "Entregue" | executado: `rev_ui_test.log` B3 | "Em trânsito"; o indicador de 30 dias conta pela entrega | RV-A4, A4b; `situacao` (2 OK A4) |
| A5 | S3 | Carga programada fica "Confirmar saída" sem reserva que a cubra | executado: sondas p4 e p5 (transcrição) | carga "impedida"; cancelar a reserva com carga programada é recusado; aviso de peso acima do previsto | RV-A5 a A5c; `situacao` (4 OK A5) |
| A6 | S3 | A primária do cabeçalho tem o rótulo da do painel e apaga o que foi digitado | executado: `rev_COM-dbl_test_header_saca_venda.log`, modo `header` | sem verde no cabeçalho com o painel aberto | `cabecalho` (5 OK A6); `comercial_fluxo_test` ajustado |
| A7 | S3 | Reserva, carga, saída e devolução na saca da cultura, não na da venda | executado: sonda p8 (transcrição) | massa gravada na venda (ex.: saca de 50 kg) | RV-A7, A7b; `unidade` (3 OK A7) |
| A8 | S3 | "Valor" errado depois de encerrar a venda e registrar devolução | executado: sonda p7 | `v.qc` acompanha a quantidade | RV-A8 |
| A9 | S3 | Mesma chave com outro peso responde "já registrado" | executado: sonda p11 | conflito; a tela gera a chave pelo peso | RV-A9, A9b |
| A10 | S3 (decisão de spec) | O 1º caminhão transforma a safra em "estoque" com déficit falso | executado: sonda p10 | estado "em colheita": apto + previsão não colhida (D-C29, decisão dos agentes) | RV-A10, A10b |
| A11 | S4 | "Abrir RM" verde; local errado em "Agricultor entrega"; "Reservar" verde para quem não pode; teclado numérico em data | executado: `rev_ui_test.log` B2 e sonda p9 (o teclado ficou como especificado) | os quatro corrigidos | RV-A11; `qualidade` e `unidade` (3 OK A11) |
| A12 | S4 | O relato fala em "17 de 38 mutantes vivos" (16 em `comercial.js` e 1 em `producao.js`). A saída registrada mostra 16 vivos de 38 em `comercial.js` e 2 vivos de 5 em `producao.js` | executado: `rev_COM-transcricao_sondas.txt` (blocos de 18:07 e 18:08) | casos novos | executado: 43/43 mortos (`corr_COM-mut1.log`, 38; `corr_COM-mut2.log`, 5) |

Nenhum achado foi recusado.

## Testes da correção (sobre a árvore que virou `29cdc6e` às 22:37)

| Comando | Resultado | Rótulo |
|---|---|---|
| `build.py` / `montar_render.py` | 143 artboards / 143 páginas | executado: `corr_COM-build.log`, `corr_COM-render.log` |
| `comercial_unit_test.py` | 105/105 | executado: `corr_COM-unit.log` e `corr_COM-transcricao_testes.txt` |
| `producao_unit_test.py` | 123/123 | executado: `corr_COM-prod-unit.log` |
| `docs/comercial/verificacao/contas.py` | FALHAS: 0 | executado: `corr_COM-transcricao_testes.txt` (21:38 e 22:27) |
| `aprova_quem_decide` 102/102, `os_aprov_lib` 45/0, `assinatura` 76/0, `legal` 35/35, `mip` 34/34 | sem falha | executado: `corr_COM-u-*.log` |
| mutantes da revisão | 43/43 mortos | executado: `corr_COM-mut1.log`, `corr_COM-mut2.log` |
| `comercial_revisao_test.py` (novo) | 33/33 | executado: `corr_COM-comercial_revisao_test.py.log` |
| `comercial_fluxo_test.py` / `producao_fluxo_test.py` | 72/72 / 67/67 | executado: `corr_COM-comercial_fluxo_test.py.log`, `corr_COM-producao_fluxo_test.py.log` |
| `reserva_duplo_clique_test.py` | 2/2 | executado: `corr_COM-rdc.log` (21:57) e `corr1_COM-reserva_duplo_clique_test.py.log` (19:01) |
| `lotest.py` / `varredura.py` / `acoes_duplicadas.py` | OK / 143/143 / 0 repetidas | executado: `corr_COM-lotest.py.log`, `corr_COM-varr.log`, `corr_COM-dup.log` (os dois últimos depois do commit) |
| `vetest.py` | 1 FALHA, "OF-103 editada" | executado: `corr_COM-vetest.py.log`. É igual à da base `f4121bd`: `base_COM-base-vetest.py.log` |

## Implementação (antes da revisão)
- **Tarefa do proprietário:** 10 cliques e 3 campos. executado: `impl3_COM-nav-comercial_fluxo_test_py.log`, 71/71.
- **Defeito de design system corrigido em `bdc5ca8`** ("Ver vendas de …" como primária): o vermelho antes da correção está em `impl3_COM-nav-painel-antes.log` (FALHOU 10/11).
- **Duplo clique da reserva:** na base deu FALHOU 1/2 (`impl1_COM-dup-base.log`); com a correção, OK 2/2 (`impl1_COM-dup-novo.log`).
- **`carencia_test`:** 91/91 (`impl3_…carencia…`), contra 87/91 na base (`base_COM-base-carencia_test.py.log`).
- **Testes de unidade da implementação** (`comercial_unit` 80/80, `producao_unit` 123/123 e outros): relatado.

## Pontos para o revisor (fila do integrador e pedido do Codex)
- **Tentar os S2 pela tela:**
  - A1: duplo clique ou clique até 400 ms depois de gravar;
  - A2: lote repetido;
  - A3: só Marta (qualidade) ou a agrônoma liberam, com o registro de quem liberou. A regra é a mesma do BEN integrado (`prLiberarLote` do BEN + `prPodeLote` do COM, uma solução só).
- **A-17 (Codex 6070584991):**
  - a massa e o fator do compromisso ficam preservados;
  - a soja com saca ambígua fica "Saca a conferir", sem conversão de 50/60 em silêncio.
- **Conflito esperado com o BEN em 10 arquivos** (`producao.js`, `g2lib.js`, `areas/producao.py`, `producao_unit.js`, `cenario.py`, `ui37.py`…):
  - preservar o `prLiberarLote` do BEN e o `prPodeLote` do COM;
  - unir os perfis (Rui com expedição, Dora, Igor e Marta uma vez só);
  - manter o grupo Comercial no menu;
  - a versão do estado salvo fica sendo a seguinte à da base.

  Depois do merge, rodar juntas as baterias do BEN, do DOM e do COM.
- **Decisão dos agentes sem o proprietário:** D-C29 (safra em colheita) revê a D-C24.

## implementacao

Retomada concluída. O módulo Comercial (P1 a P7 e A-17) estava todo commitado de antes e não havia nada pendente fora dos commits. Nesta retomada fiz três coisas: integrei a `claude/prototipo-v44` (9fb09a5), corrigi um desvio do design system de 09/10 no Painel comercial e rodei a bateria inteira. Tudo abaixo é **executado**, salvo onde digo outra coisa. Branch `claude/v44-comercial` em <sp-com>; não fiz push nem PR.

**Estado ao retomar:** o `git status` mostrava só saídas de build e de teste (`_probe/`, `project/`, `_render/`, `__pycache__`). A cópia temporária `.base-f4121bd` (um worktree de 152 MB que eu tinha criado para reproduzir defeitos na base) foi removida com `git worktree remove`.

##### Commits (desde a base f4121bd)
| Hash | Título |
|---|---|
| bdc5ca8 | COM: Painel comercial sem "Ver vendas de …" como primária na linha em déficit (BOT-03/BOT-08) — **novo nesta retomada** |
| c7d48e9 | Merge da `claude/prototipo-v44` (9fb09a5, SAF-C01), sem conflito — **novo nesta retomada** |
| d7b91ff | COM A-17: Estoque de produto diz o próximo passo do lote quando a venda está com a saca a conferir |
| d59fad0 | COM: teste de navegador do fluxo principal (menu, tarefa do proprietário, recusas e repetição, perfis, painel, 390 px, produção) |
| 4533879 | COM A-17: venda encerrada sem a saca não suspende a oferta |
| c6b17da | spec COM v1.2: A-17, D-C26, D-C27, KC19-KC20 |
| 3044c79 | COM A-17: a venda guarda a massa da sua unidade; soja com saca ambígua fica "Saca a conferir" |
| 16b3974 | COM: duplo clique sem erro, reservar antes de programar |
| f7d0fa6 | Merge da v44 (cdc185f) |
| d738678 | COM P7: Previsão e colheita sem as colunas comerciais |
| 5d84cc6 | COM P6: Estoque de produto só com lotes |
| 8231296 | COM P2-P5: telas VEN, EXPED e PCOM no grupo Comercial |
| 498104d | COM P1: regras e estado do comercial |
| 2fccd42 / 1e31c8e | spec COM e revisão por contraexemplo |

**O defeito novo (bdc5ca8, S4):** ao selecionar uma linha em déficit, o Painel comercial mostrava em verde "Ver vendas de S41", que só abria o painel que a própria seleção já abre. Isso vai contra o design system de 09/10: BOT-03 proíbe "Ver …" como primária e BOT-08 diz que troca de tela não é primária.
- Reproduzido antes da correção: `comercial_fluxo_test.py painel` deu FALHOU 10/11 no build anterior.
- Agora a linha em déficit fica sem primária. O painel da linha diz o passo, com o dono (por exemplo, "publicar a previsão de S41 · Produção") e lista as vendas.
- Registrado na especificação v1.3 (§3.3) e na decisão D-C28.

##### Testes (SAFRION_DADOS=sintetico; navegador um por vez com flock /tmp/cdpC.lock)
**Sem navegador:**
- `build.py`: 0 FALHA, 143 artboards.
- `montar_render.py`: 143 páginas.
- `comercial_unit_test.py`: 80/80.
- `producao_unit_test.py`: 123/123.
- `aprova_quem_decide_test.py`: 102/102.
- `os_aprov_lib_test.py`: 45/45.
- `assinatura_unit_test.py`: 76/0 falhas.
- `legal_unit_test.py`: 35/35.
- `links_ocultos_test.py`: 8/8.
- `ocupacao_unit.py`: 117 OK.
- `docs/comercial/verificacao/contas.py`: FALHAS 0.

**Navegador:**
- `comercial_fluxo_test.py`: OK 71/71. Tarefa do proprietário medida em 10 cliques e 3 campos (o limite é 16 e 3).
- `producao_fluxo_test.py`: 67/67.
- `reserva_duplo_clique_test.py`: 2/2.
- `varredura.py`: 143/143 páginas sem erro.
- `acoes_duplicadas.py . /tmp/COM-dup.json`: 0 páginas com ação repetida.
- `acao_unica_test.py`: modos v3 e saf, 10/10 cada.
- `lotest.py`: OK.
- `est_cenario_test.py`: 15/15.
- `app_cenario_test.py`: 15/15.
- `carencia_test.py`: 91/91 (na base f4121bd eram 87/91).
- `saf_c01_test.py`: 38/0 falhas.

**Ainda vermelhos, os mesmos da base:**
- `os_cenario_test.py`: 19/20, a mesma falha PEND-OS-01 já conhecida.
- `vetest.py`: 1 falha ("OF-103 editada"), idêntica no log da base f4121bd (`/tmp/COM-base-vetest.py.log`). Não vem do Comercial, mas não estava na sua lista de vermelhos conhecidos.

##### Expectativas de teste que mudaram (motivo escrito em cada commit)
- **`producao_unit.js`:**
  - As 19 chamadas de reserva agora passam o ator, porque o ator ficou obrigatório (CE-10).
  - U10a: as obrigações de soja entraram no estado; a oferta livre continua 48.280 sc.
  - U08b, U09 e U10a passam pela saca de 60 kg registrada (A-17).
- **`os_aprov_lib_unit.js` e `aprova_quem_decide_unit.js`:** usam o tamanho do cadastro de perfis em vez de 5 fixos, porque a Dora entrou.
- **`producao_fluxo_test.py`:** cancelar reserva e a linha do PV-030 passaram para Contratos e pedidos (P6). Na semente, o Estoque de produto fica sem primária e mostra o próximo passo do lote (A-17).
- **`comercial_fluxo_test.py painel`:** verificação nova para a linha em déficit.

##### Fora de escopo
Segue o §9 da especificação, cada item com sua condição de retorno:
- ofertas versionadas e portal do cliente;
- tolerância de peso por contrato;
- revisão de contrato;
- cotação em tempo real;
- nota fiscal e documentos fiscais;
- baixa de recebimento (por isso o "a receber" não cai na demonstração);
- destinação do lote devolvido (fica com o Beneficiamento);
- fila de caminhões e viagens;
- frete real;
- aba Motorista do app;
- exportação.

Também ficam com outras frentes: o COLH-C01 (café "sc a apurar"), que é da frente DOM e da Colheita, e os separadores, hover verde e retorno visual, que são da frente DS e não toquei.

##### Riscos
- **Conflitos na integração** (`git merge-tree` executado contra as outras frentes):
  - Beneficiamento: `producao.js`, `areas/producao.py`, `g2lib.js`, `cenario.py`, `ui37.py`, `acoes_duplicadas.py` e os testes de perfis.
  - DOM: `producao.js` e `areas/producao.py`.
  - PCM: `g2lib.js`, `cenario.py` e `ui37.py`.
  - Config: `g2lib.js`.
  - Suprimentos: `cenario.py`.
  - Solo: `ui37.py`.
  - O integrador precisa preservar o perfil Dora, o Rui com expedição, o grupo Comercial no menu e a versão do estado (hoje v5; se outra frente subir antes, vira a seguinte).
- **Sobreposição com o Beneficiamento:** a D-C02 tira "reserva e expedição reais" do BEN-8 e traz para o Comercial. Isso precisa do acordo de quem cuida do BEN-8.
- **Primárias que levam a outra tela:** "Programar carga do PV-xxx", "Vender … · período" e "Registrar a saca do PV-030" ficam como links verdes, o mesmo padrão do motor da Colheita. Se a frente DS de botões (#48) aplicar o BOT-08 literalmente, esses três mudam junto com os da Colheita.
- **Perguntas ao proprietário (5) ainda abertas** em `DECISOES.md`, entre elas a saca de 50 ou 60 kg dos contratos de soja e a tolerância de peso. Por isso a semente mostra a soja como "Saca a conferir" até alguém registrar a massa.
- **Ainda não feito:** `docs/STATUS.md` e o artefato (P8) não foram atualizados; ficam com o integrador. A revisão do Codex ainda não chegou.

Arquivos principais:
- <sp-com>/docs/comercial/ESPECIFICACAO.md
- <sp-com>/docs/comercial/DECISOES.md
- <sp-com>/tools/prototipo/v37/gen37/areas/vendas.py
- <sp-com>/tools/prototipo/v37/gen37/comercial.js
- <sp-com>/tools/prototipo/v37/gen37/dados_comercial.py
- <sp-com>/tools/prototipo/v37/gen37/comercial_unit.js
- <sp-com>/tools/prototipo/v37/gen37/comercial_fluxo_test.py

Logs do navegador em `/tmp/COM-nav-*.log`; o log da reprodução antes da correção está em `/tmp/COM-nav-painel-antes.log`.

## revisao

### Revisão adversarial do Comercial (VEN, EXPED, PCOM), branch `claude/v44-comercial`, HEAD bdc5ca8

Consegui quebrar o módulo em uso real: há 4 achados S2, 7 S3 e alguns S4, mais lacunas nos testes (17 de 38 mutantes sobreviveram). O pior é o duplo clique humano: o segundo clique confirma a entrega, sem a pessoa escolher nada. Tudo abaixo foi **executado**, salvo onde digo "especificado".

Trabalhei em cópias no scratchpad e não alterei nenhum arquivo versionado. O build na cópia deu 0 FALHA, 143 páginas, e `montar_render` passou. As sondas são JS no node sobre o motor do repositório e Chrome via CDP, com o mesmo flock. Os testes do implementador passaram na cópia: `comercial_unit_test` 80/80, `producao_unit_test` 123/123, `links_ocultos_test` 8/0 falhas e `contas.py` FALHAS 0.

Caminhos usados abaixo:
- `SP` = `<scratchpad>`
- `G` = `<sp-com>/tools/prototipo/v37/gen37`

Sondas no node: `cd SP/com && cat base.js helpers.js pN.js > runN.js && node runN.js`.

#### Achados

**A1 · S2 · Duplo clique humano executa o próximo comando**
- **Reprodução:** em `SP/proto/dbl_test.py`, dois cliques de mouse via CDP, com 120 ms entre eles, no mesmo ponto.
  - Modo `saida` (PV-036, agricultor entrega): Rui clica duas vezes em "Confirmar saída da RM-0002". O sistema grava a saída e também `entrega {d: 2026-09-26, quem: Rui, comp: ''}`, título vencendo em 24/10. Rui não escolheu data nem "Recebido tudo", e não existe comando para desfazer a entrega.
  - Modo `venda`: duplo clique em "Registrar venda" cria o PV-039 e também a RS-0002 (100 sc do L10-031), sem ninguém escolher o lote.
  - Modo `saca`: duplo clique em "Registrar a saca" cria a RS-0002 (125 sc do L10-031).
  - Log em `SP/../tasks/b9okovvt5.output`.
- **Causa:** depois do sucesso, o mesmo botão do painel passa a ser o comando seguinte, já com padrões preenchidos e chave nova.
  - `G/areas/vendas.py:357`: `pr_ch: prChave('W-RM')` após a saída.
  - `G/areas/vendas.py:359-360`: data pré-selecionada quando só há uma opção e `rc` padrão "tudo".
  - `G/areas/vendas.py:163` e `:197-201`: venda e saca levam direto ao formulário "Reservar", com a sugestão já preenchida.
- **Por que os testes não viram:** `comercial_fluxo_test.py` (erros e tarefa) e `reserva_duplo_clique_test.py` usam `e.click(); e.click()` em sequência, sem nova renderização no meio. Não testam o duplo clique real.
- **Correção proposta:**
  - No `prRun`, travar a primária do painel por cerca de 800 ms após o sucesso.
  - "Confirmar entrega" sem data nem "Recebido" pré-escolhidos.
  - Teste com `Input.dispatchMouseEvent` em cada primária do painel.

**A2 · S2 latente (só pelo comando; a tela remove duplicatas) · Lote repetido na carga baixa a reserva de outra venda**
- **Reprodução (`SP/com/p3.js`):**
  - L39-133 com 12.050 kg: 5.000 kg reservados ao PV-036 e 7.050 kg ao PV-038.
  - `comProgramar` com `lotes: [{L39-133, 5000}, {L39-133, 5000}]` é aceito.
  - Rui (sem ser gestor) confirma a saída de 10.000 kg.
  - Resultado: físico 2.050 kg contra 7.050 kg reservados ao PV-038, ou seja, 5.000 kg da reserva de outra venda saíram sem aviso de excesso.
- **Causa:**
  - `G/comercial.js:248`: o limite de cada lote é conferido linha a linha, sem somar as linhas repetidas.
  - `G/comercial.js:284-299`: o excesso é calculado por entrada de `por` antes de qualquer consumo.
- **Correção proposta:**
  - Recusar lote duplicado no `comProgramar`.
  - Agregar `por` por lote no `comSair`.
  - Pós-condição: `fis ≥ res` em cada lote, senão recusar.

**A3 · S2 · Lote devolvido é liberado por qualquer perfil, gravado em nome da Qualidade (Marta)**
- **Reprodução (`SP/proto/ui_test.py`, log em `SP/proto/ui_test.log`):** com o perfil Dora, em PROD#L39-134 (devolução da RM-0002), "Liberar L39-134" aparece verde. Ao clicar, grava `lib.quem = "Qualidade (Marta)"`.
- **Causa (na base da Colheita, mas o R-C10 depende dela):**
  - `G/areas/producao.py:302`: chama `prLiberarLote(x, L.id, prQuem('qual'))`.
  - `G/areas/producao.py:274`: não confere o perfil.
  - `G/producao.js:391`: não recebe quem age.
  - Resultado: "só a Qualidade libera" não vale, e o produto devolvido pode ser revendido sem conferência.
- **Correção proposta:**
  - `prLiberarLote(c, lid, ator)` exigindo o papel qualidade ou gestor e gravando `g2ator`.
  - Perfil Marta com papel qualidade.
  - Para quem não tem o papel, mostrar o dono em vez do botão (mesmo padrão já usado no Comercial).
  - Teste em que Dora e Rui são recusados.

**A4 · S3 · Venda com a carga em trânsito aparece "Entregue"**
- **Reprodução (`p2.js` e `ui_test.py` B3):**
  - Na VEN, a linha do PV-036 mostra "Entregue · entregue · R$ 30.500,00 a receber".
  - Na EXPED, a RM-0002 mostra "Em trânsito · Confirmar entrega".
  - O indicador "Entregue nos últimos 30 dias" e o "Entregue/realizado" do `comPrecos` contam o que está em trânsito.
- **Causa:**
  - `G/producao.js:221`: `exp ≥ qtd` já resulta em "Entregue".
  - `G/comercial.js:118`: `comSitVenda` retorna antes de olhar a carga.
  - `G/areas/vendas.py:88`.
  - `G/comercial.js:383-393`.
- **Correção proposta:** situação "Em trânsito", com próximo passo "Confirmar entrega da RM · Expedição", antes de "Entregue". O indicador passa a contar pela data da entrega ou muda o rótulo para "Saídas".

**A5 · S3 · Carga programada fica "Confirmar saída" mesmo sem reserva que a cubra**
- **Primeiro caso (`p4.js`):** Dora cancela a RS-0002 com a RM-0002 programada, e o lote é reservado ao PV-038. A carga continua azul, "Confirmar saída", com `comImpede` vazio. A venda mostra "Sem reserva · Confirmar saída da RM-0002". Só na balança Rui e Ana são recusados.
- **Segundo caso (`p5.js`):** duas cargas (previsto 6.000 + 4.000 kg). A primeira pesa 10.000 kg, dentro da reserva, sem aviso de que passou do previsto, e consome a reserva da segunda. A RM-0003 segue "Programada · Confirmar saída" numa venda "Entregue".
- **Causa:**
  - `G/areas/vendas.py:260-267`: `comRmSit` não confere previsto contra a reserva ativa.
  - `G/producao.js:423` e `G/areas/vendas.py:186-188`: cancelar a reserva não olha a carga programada.
  - `G/comercial.js:284-289`: não há aviso de líquido acima do previsto.
- **Correção proposta:** marcar a carga como "impedida: reserva do PV no lote menor que o previsto · Comercial". Recusar (ou avisar) o cancelamento da reserva com carga programada. Avisar quando o peso passar do previsto.

**A6 · S3 · A primária do cabeçalho tem o mesmo rótulo da do painel, mas apaga o que foi digitado**
- **Reprodução (`dbl_test.py` modo `header`):** com bruto 22000 e tara 12000 digitados, clicar no verde do cabeçalho "Confirmar saída da RM-0002" deixa os campos vazios e não grava nada. O mesmo padrão existe na VEN ("Aprovar crédito do PV-xxx", "Reservar lote para o PV-xxx", "Registrar a saca do PV-xxx").
- **Causa:**
  - `G/areas/vendas.py:375-376` e `:210-212`: o `go` faz apenas `pr_form: null`.
  - `G/../ferramentas/acoes_duplicadas.py`: exclui `aside[role=dialog]`, por isso não detecta o par cabeçalho/painel.
- **Correção proposta:** a primária do cabeçalho executa o mesmo `go` do painel, ou some enquanto o painel do registro estiver aberto.

**A7 · S3 (vale se o proprietário confirmar saca de 50 kg) · EXPED, reserva e devolução usam a saca da cultura (60 kg), e a venda usa a dela**
- **Reprodução (`p8.js`):** os mesmos 30.000 kg aparecem como "500 sc" na reserva, na carga e na EXPED, e como "600 sc 50 kg" na saída e na VEN. Digitar "100" em "Quantidade devolvida (sc)" grava 6.000 kg, e a mensagem diz "120 sc 50 kg devolvidos".
- **Causa:**
  - `G/areas/vendas.py:269`, `:315` (`comTxt(cu)`), `:343`, `:362`, `:366` (`comUn(cu)`, `prEstBase(cu)`).
  - `G/areas/producao.py:195-207` (`prFormReserva`).
  - Isso contraria o A-17 da própria spec.
- **Correção proposta:** `comTxtV(v)` e `comUnV(v)` em tudo que pertence à venda, conversão com `comFat(v)`, e teste com saca de 50 kg.

**A8 · S3 · "Valor" fica errado depois de encerrar a venda e registrar devolução**
- **Reprodução (`p7.js`):** PV-036 encerrado com 6.000 kg, devolução de 1.000 kg. Fica `qtd` 5.000 e `qc` 6.000, e o painel mostra Valor R$ 18.300,00 enquanto o a receber é R$ 15.250,00.
- **Causa:** `G/comercial.js:324` atualiza `v.qtd` e não `v.qc`.
- **Correção proposta:** recalcular `v.qc = prDiv(v.qtd, comFat(v))`.

**A9 · S3 · Mesma chave com outro peso: "Aprovar crédito" responde "já registrado" e não cobre o peso novo**
- **Reprodução (`p11.js`):** aprovação com a chave `W-RM-1-CR` para 10.000 kg, depois 10.040 kg com a mesma chave. Resposta "já registrado", e a saída de 10.040 kg é recusada pedindo nova aprovação. A Ana fica presa até reabrir a carga.
- **Causa:**
  - `G/comercial.js:202`: não compara o conteúdo.
  - `G/areas/vendas.py:354`: chave fixa `ch + '-CR'`.
- **Correção proposta:** guardar o conteúdo (venda e valor coberto) na aprovação: mesma chave com outro valor vira conflito ou nova aprovação. Na tela, usar uma chave nova a cada aprovação.

**A10 · S3 (decisão de spec) · Primeiro caminhão da safra de grão transforma a safra inteira em "estoque" com déficit**
- **Reprodução (`p10.js`):** um lote 26/27 recebido faz a "Safra 2026/27" (68.180 sc publicados) virar "Estoque (2026/27)". Com só o primeiro caminhão recebido, aparece déficit de cerca de 19.900 sc, e venda futura da 26/27 passa a ser recusada.
- **Causa:** `G/comercial.js:135-137` (`comSafColhida` = primeira carga) e `:358-361`.
- **Correção proposta:** um estado "em colheita", em que a oferta é o colhido apto mais o restante da previsão até a colheita fechar. Ou registrar como decisão a levar ao proprietário.

**A11 · S4**
- O painel da VEN usa "Abrir RM-0002" verde como primária (BOT-03/BOT-08), junto com "Abrir carga ›" para o mesmo destino: `G/areas/vendas.py:202`, executado em `ui_test.py` B2. É o mesmo defeito do "Ver vendas", que foi corrigido só no PCOM.
- Venda com "Agricultor entrega" grava o local "Retira no Armazém Sede (FOB)" (`p9.js`; `G/comercial.js:172`, `:177`).
- PROD mostra "Reservar …" verde a quem não tem o papel; o comando recusa depois.
- "Outras datas" em dd/mm usa teclado numérico, que não tem "/" (`G/areas/vendas.py:141`, especificado, não testei no celular).

**A12 · S4 (lacunas de teste; os mutantes 1, 2 e 4 da lista protegem regras S2) · 17 de 38 mutantes sobreviveram em `comercial.js`**
- Runner em `SP/com/mut.py`, mutantes em `mutantes.txt` e `mutantes2.txt`. Os que sobreviveram:
  1. Dora (comercial) aprova crédito.
  2. Comercial confirma a entrega.
  3. Carga cancelada sai.
  4. Segunda entrega com outra chave sobrescreve a primeira.
  5. Entrega com data futura.
  6. Filtro de validade antes da janela (R-C05).
  7. Janela já passada.
  8. Data prevista no passado.
  9. Entrega sem transportador.
  10. Cancelar carga sem motivo.
  11. Motivo de devolução livre.
  12. Devolução de carga em trânsito.
  13. Conflito no registro da saca.
  14. Antecipado entra na exposição de crédito.
  15. Borda do limite de crédito.
  16. 30 dias trocado por 60 no indicador.
  17. Em `producao.js`: `prCancelarReserva` aceitando qualquer perfil (CE-10). Todos os testes usam 'Ana'.

#### O que tentei e não quebrou
- **Excesso tirado da reserva de outra venda:** recusado, até para a Ana, quando o disponível é 0 (`p4.js`; mutante M01 morto).
- **Rollback:** entrega com devolução inválida não grava nada (`cenMudar` trabalha sobre clone).
- **Duas abas:** `cenGet` relê o localStorage a cada comando.
- **Saca a conferir (A-17):**
  - reservar, programar e dar saída são recusados;
  - a oferta fica suspensa, nunca 0;
  - venda encerrada sem saca não suspende nada.
- **Contas e regras de crédito e estoque:**
  - decimal exato nas três saídas do KC15;
  - KC09, KC16, KC17, KC18 (M26, M31, M38 mortos);
  - antecipado fica fora do a receber (M23 morto);
  - lote devolvido nasce Em inspeção e não é reservável (M11 morto);
  - a produção não conta a devolução de novo (M12 morto);
  - ator obrigatório ao reservar (morto).
- **Fora do módulo:**
  - telas O.S., Kanban e aprovação agronômica: nenhum arquivo delas mudou nos commits do Comercial;
  - `prNum` ("51.200" → 51200) já é comportamento da base.

#### Arquivos
- Sondas: `SP/com/` (`p2.js` a `p11.js`, `base.js`, `helpers.js`, `mk.py`, `mut.py`, `mutantes.txt`, `mutantes2.txt`)
- Testes de navegador: `SP/proto/dbl_test.py`, `SP/proto/ui_test.py`, `SP/proto/ui_test.log`
- Log do duplo clique: `<sessao-tmp>/tasks/b9okovvt5.output`
- Código revisado: `<sp-com>/tools/prototipo/v37/gen37/comercial.js`, `<sp-com>/tools/prototipo/v37/gen37/areas/vendas.py`, `<sp-com>/tools/prototipo/v37/gen37/producao.js`, `<sp-com>/tools/prototipo/v37/gen37/areas/producao.py`

## correcao

**Comercial: correções da revisão concluídas e commitadas**

Todos os achados S2, S3 e S4 foram corrigidos, e cada um tem teste de regressão. Nenhum foi recusado. Depois da queda da sessão, retomei o trabalho que não estava commitado: conferi, completei e commitei. Nada foi descartado. Não fiz push nem PR.

**Commit:** `29cdc6e` "COM: correções da revisão", na branch `claude/v44-comercial`, com 12 arquivos.
- **S2:**
  - **A1:** no painel, o segundo clique de um duplo clique, ou qualquer clique até 400 ms depois de gravar, não faz nada. "Confirmar entrega" agora abre sem data nem "Recebido" marcados.
  - **A2:** lote repetido na carga é recusado. A saída soma por lote e é recusada se o físico ficar abaixo do reservado.
  - **A3:** só Qualidade ou agrônoma libera lote, e o registro grava quem liberou. Criei o perfil Marta · Qualidade.
- **S3:**
  - **A4:** venda com carga a caminho aparece "Em trânsito", e o indicador de 30 dias conta pela entrega.
  - **A5:** carga sem reserva que a cubra fica impedida. Cancelar a reserva de uma carga programada é recusado, e peso acima do previsto gera aviso.
  - **A6:** com o painel aberto, o cabeçalho não repete o botão verde do painel.
  - **A7:** reserva, carga, saída e devolução usam a massa gravada na venda (por exemplo, saca de 50 kg).
  - **A8:** o valor do acordo acompanha a quantidade depois de devolução em venda encerrada.
  - **A9:** a mesma chave de crédito com outro peso dá conflito, e a tela gera a chave pelo peso.
  - **A10:** com a safra em colheita, a oferta passa a ser o apto mais a previsão ainda não colhida.
- **S4:**
  - **A11:** os quatro pontos foram corrigidos.
  - **A12:** os mutantes que sobreviviam agora são mortos pelos testes.
- **Documentos:** `docs/comercial/ESPECIFICACAO.md` passou à v1.4. Em `DECISOES.md` entraram as decisões D-C29 a D-C32 e a tabela da revisão.

**Ajuste no A3:** a branch única (`claude/prototipo-v44`, 2678481, frente do beneficiamento) já trazia a regra "Qualidade ou agrônoma libera". Adotei a mesma regra em vez de "qualidade ou gestor", para ficar uma solução só.

**Testes** (todos executados, depois do último build):

| Comando | Resultado |
|---|---|
| `python3 build.py` | 0 FALHA, 143 páginas |
| `montar_render.py` | 143 páginas |
| `comercial_unit_test.py` | 105/105 |
| `producao_unit_test.py` | 123/123 |
| `links_ocultos_test.py` | 8, 0 falhas |
| `docs/comercial/verificacao/contas.py` | FALHAS: 0 |
| `aprova_quem_decide_test.py` | 102/102 |
| `os_aprov_lib_test.py` | 45, 0 falhas |
| `assinatura_unit_test.py` | 76, 0 falhas |
| `legal_unit_test.py` | 35/35 |
| `mip_unit_test.py` | 34/34 |
| Mutantes do revisor, contra a suíte atual | 43/43 mortos (38 em `comercial.js`, 5 em `producao.js`) |
| Navegador: `comercial_revisao_test.py` (novo: duplo clique real, cabeçalho, qualidade, situação, unidade) | 33/33 |
| Navegador: `comercial_fluxo_test.py` | 72/72 |
| Navegador: `producao_fluxo_test.py` | 67/67 |
| Navegador: `reserva_duplo_clique_test.py` (antes do ajuste do A3) | 2/2 |
| Navegador: `lotest.py` | OK |
| `varredura.py` | 143/143 sem erro |
| `acoes_duplicadas.py` | 0 com ação repetida |

**Falhas e expectativas mudadas:**
- `vetest.py` tem 1 FALHA ("OF-103 editada"). É a mesma falha da base f4121bd, não vem deste trabalho.
- Mudei a expectativa de três testes antigos, com o motivo escrito no commit:
  - `comercial_fluxo_test.py`: a primária fica no painel aberto (A6);
  - `producao_fluxo_test.py`: grava "liberado por Ana (agrônoma)" (A3);
  - `producao_unit.js`: passa a pessoa que libera, como na branch única (A3).

**Riscos restantes:**
- **Conflitos na integração:** simulei o merge com `claude/prototipo-v44` (`git merge-tree`, sem gravar) e há conflito em 10 arquivos. Os principais são `producao.js`, `g2lib.js`, `areas/producao.py`, `producao_unit.js`, `cenario.py` e `ui37.py`. Na resolução:
  - manter o `prLiberarLote` do beneficiamento, que já é mais completo;
  - manter a minha checagem de quem pode liberar ou reservar (`prPodeLote`);
  - unir a lista de perfis: Rui com expedição, Dora, Igor e Marta uma vez só.
- **Duplo clique no celular:** a trava é de 400 ms (o revisor sugeriu cerca de 800 ms) mais o bloqueio do segundo clique. Um toque duplo lento num celular real não foi testado (especificado).
- **Lacuna no verificador:** `acoes_duplicadas.py` continua ignorando o painel lateral. O par cabeçalho/painel só está protegido no Comercial, pelo teste novo.
- **Decisão sem o proprietário:** a D-C29 (safra em colheita) revê a D-C24. É decisão dos agentes e vale até o proprietário mudar.
- **Revisão:** quem revisou foi um subagente do workflow. O parecer do Codex continua pendente.

**O que o proprietário pode conferir:** no perfil Rui, em Comercial › Expedição e entregas, dê duplo clique em "Confirmar saída" de uma carga do mamão. A saída grava uma vez e a carga fica "Em trânsito". A entrega só é confirmada depois de escolher a data e "Recebido tudo". Em Contratos e pedidos, a venda aparece "Em trânsito", não "Entregue".
