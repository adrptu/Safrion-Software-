# Relatos da SAF-C01b (SAF-C01, segunda entrega: `d1b81f4` + `64a3041`)

Fonte: resultado do workflow `saf-c01` (run `wf_5992b62f-e4c`, concluído em 09/10 às 17:36 UTC), o mesmo texto do `journal.jsonl`.

As fases foram:
1. **autor:** a 1ª entrega, `ef0d7b2`, que é a base deste pacote. Ela já está integrada (`9fb09a5`) e foi confirmada pelo Codex em 6086012087.
2. **verificação:** três lentes sobre `ef0d7b2` (oráculo, tela e regressão). São agentes Claude separados; **não é a revisão do Codex**.
3. **fechamento:** as correções (`d1b81f4`) e as saídas brutas (`64a3041`).

Rótulos:
- **executado:** a saída está no pacote, no diff (pasta `docs/planejar-safra/verificacao-saf-c01/correcoes/`, que entra pelo `64a3041`) ou em `brutos/`;
- **relatado:** o agente diz que rodou, mas a saída não está no pacote.

## Resumo

### Achados da verificação de `ef0d7b2` e o que o fechamento fez

| Lente | Sev. | Achado | Fechamento |
|---|---|---|---|
| oráculo | S3 | Área livre do aviso do Planejar, do painel Dividir e do aviso do Dividir ignora a perene sem fim (ADENDO 6079770308). Brutos: `C01b-ver-oraculo_ui_adendo_*.txt`, `C01b-ver-oraculo_ui_livre_dividir.txt` | corrigido: `livreDepois` e `dvCap` |
| oráculo | S3 | Par antigo na mesma faixa desliga a T-soma do dia (anterior à frente). Brutos: `C01b-ver-oraculo_compara*.txt` | corrigido nesta frente (adaptado): área física; o dia só sai da soma quando o alvo está na mesma área de outra ocupação com plano |
| oráculo | S3 | M1 com 3 ou mais ocupações mostra período invertido e um "Máximo" que não destrava (anterior) | corrigido: pior dia pelo núcleo do alvo; "Máximo" arredondado para baixo |
| oráculo | S4 | Pista "Plantio a partir de" diz "sem janela" quando o problema é a área | corrigido: "reduza a área: máximo X ha" |
| oráculo | S4 | Folga 0 com cultura sem ciclo: núcleo de um dia some na T-faixa | corrigido: `ocNucFim` |
| tela | S3 | Aviso de área livre depois de gravar ou dividir ignora o café de outra safra. Brutos: `C01b-ver-ui_ui_fix*.txt`, `C01b-ver-ui_ui_base.txt` | corrigido (mesmo ponto do 1º achado) |
| tela | S3 | O Dividir propõe uma divisão que a trava recusa e a marca como "Área conferida". Brutos: `C01b-ver-ui_ui_fix_E*.txt` | corrigido: capacidade do Dividir, recusa agregada, nome que não colide |
| tela | S3 | Perene nova numa safra antiga: a parcela sugerida colide e a mensagem entra em laço (anterior). Brutos: `C01b-ver-ui_ui_fix_F.txt`, `C01b-ver-ui_ui_base_F.txt` | corrigido: `faixasEmUso`; "use outra parcela (ex.: B1-B)" |
| regressão | S3 | `ocPlantioMin` O(n²) com histórico longo: de ~0,3 s a ~15 s. Brutos: `C01b-ver-regressao_hist_escala.txt` | corrigido: pré-filtro com equivalência testada; 91 ocupações em 15 a 30 ms (indicativo) |
| regressão | S3 | O aviso "N ha livres" depois de gravar ignora a perene de outra safra (mesmo ponto). Brutos: `C01b-ver-regressao_adendo_*.txt` | corrigido |

Nenhum achado foi recusado. Dois foram adaptados, com motivo registrado no fechamento:
- **nome da parcela:** evita só as faixas ainda ocupadas, para que a sucessão R-19 continue reaproveitando nomes;
- **par antigo:** corrigido nesta frente, e não em tarefa separada.

### Testes do fechamento (sobre a árvore de `d1b81f4`)

| Comando | Resultado | Rótulo |
|---|---|---|
| `ocupacao_unit.py` | 130 OK · 0 FALHA | executado: `correcoes/testes/ocupacao_unit.txt` (no diff) |
| `ocupacao_unit.py` contra `ef0d7b2` | 120 OK · 10 FALHA | executado: `correcoes/ocupacao_unit_contra_ef0d7b2.txt` |
| `saf_c01_test.py tudo` | 66 ok · 0 | executado: `correcoes/testes/saf_c01_test.txt` |
| `saf_c01_test.py` no render de `ef0d7b2` | 34 ok · 32 falhas | executado: `correcoes/testes/saf_c01_test_ANTES_ef0d7b2.txt` |
| `ocupacao_test` 65/0, `saf_revisao` 42/0, `saf_operacoes` 87/0, `tabelas_saf` 24/24, `saf_cmp_continuidade` 31/0, `etapas_celular` 14/0, `capacidade_unit` 76/0, `rend_multiconjuntos_unit` 106/106, `varredura` 140/140 | sem falha | executado: `correcoes/testes/*.txt` e `resumo.txt` |
| `partest` | 46 ok · 1 falha ("T1-C copia ajuste do T1-B", vermelho conhecido da base) | executado: `correcoes/testes/partest.txt` |
| harness do Codex | `ecc8b00` 2/1; `ef0d7b2` 3/3; final 3/3 | executado: `correcoes/harness_ef0d7b2.json`, `depois.json`; `brutos/C01b-fech_harness_*.json` |
| oráculo v2 (3203 + 1204 casos) | 0 divergências em JS e Python | executado: `correcoes/oraculo/compara2*.txt` |
| 4 mutantes do serviço | todos detectados | executado: `correcoes/oraculo/mutante_*.txt` |
| dados da demonstração (sementes) | iguais, salvo 2 mensagens M1 que saíam com período invertido | executado: `correcoes/sementes_*.txt` |
| desempenho (3 rodadas) | ver tabela do fechamento | executado: `correcoes/desempenho_rodada*.json`; máquina com carga, números indicativos |
| `build.py` | 0 FALHA | executado: `brutos/SAFC01-build.log` (16:43) |
| `montar_render.py` | 140 páginas | relatado (o log não ficou) |

### O que o revisor precisa provar (fila do integrador)
- **As regras novas são decisão do autor e precisam de prova adversarial:**
  - área física: numa mesma faixa conta a maior área, e o talhão inteiro cobre o talhão;
  - o dia só sai da soma quando o próprio alvo está na mesma área de outra ocupação com plano.

  Tente quebrar com faixas repetidas em safras diferentes, com talhão inteiro + parcela e com a sucessão R-19. Compare com a R-14 (ESPECIFICACAO §3.4).
- **Limites declarados pelo autor:**
  - tela testada só em emulação no Chrome headless, sem 360 px nem aparelho físico;
  - Aplicar plano e Vincular ciclo só por leitura de código;
  - "Máximo" conservador quando o alvo divide a faixa com uma ocupação sem plano;
  - capacidade do Dividir abaixo do real com plantios em datas diferentes (não testado na tela);
  - o aviso diz "0 ha livres" em vez de omitir o trecho.

## autor

Corrigi o SAF-C01 (resposta a PR #47, comentário 6079770308), com o commit **ef0d7b2** na branch `claude/v44-saf-c01` (worktree `<sp-safc01>`, base ecc8b00). Não fiz push nem abri PR. Agora o serviço trava os 110 ha em 100 ha com o café de 2020, também pela tela, e os três casos do Codex passam.

No caminho apareceram dois problemas a mais:
- **O defeito é mais largo que a perene.** Qualquer ocupação antiga no talhão escondia a soma, porque o `ocChecar` usa as ocupações de todas as safras. Exemplo: uma soja de 2020 em T1-C deixava gravar 40 + 70 ha em 2027. Agora esse caso é teste.
- **A mensagem de trava podia congelar a tela por cerca de 50 s.** Com duas perenes acima da área, a mensagem contava dia a dia até 10^8: medi 50 s no node já na base (`mensagem_perene_perene.txt`). A correção da soma deixava esse caso mais frequente; corrigi junto.

**O que mudou**
- **Soma no tempo** (`ocupacao.js:68-92`, espelho `ocupacao.py:190-233`): a varredura vai de evento em evento (plantio, plantio + 1, fim do núcleo com folga, início e liberação). Não há mais o teto d0 + 900 nem laço até `OC_INF`. A pendência R-15 de soma usa a mesma varredura. Os dias, a contagem e a ordem saem iguais aos do laço dia a dia sem teto; um teste compara os dois.
- **Mensagem M1** (`ocupacao.js:172-176`, `ocupacao.py:406-414`): o pior dia sai pelos mesmos eventos. Quando o período não tem fim, a mensagem diz "A partir de dd/mm/aaaa, …".
- **"Perene 30"**: é o cálculo da R-09 (a Perene vai só até o que sobra do talhão), então a conta está certa, mas escondia o excesso. Mantive essa divisão, que soma a área do talhão, e a linha ganhou `exc` (`ocupacao.js:126`, `ocupacao.py:293`). A faixa passa a mostrar "· 10 ha em sobreposição" (`ocupacao.js:136`, `ocupacao.py:317`). A Situação vira "Sobreposição" pela própria trava.
- **Teste de unidade** (`ocupacao_unit.py:283-404`):
  - os 3 casos do Codex, rodados no JS e no Python;
  - 4 casos meus: anual antiga, perene + perene antiga e recente, e o controle de mesma faixa (continua travando pela faixa, com 30 ha);
  - comparação com o laço dia a dia na base e em 300 conjuntos aleatórios;
  - o oráculo de soma das propriedades (`:435`) deixou de olhar só 400 dias.
- **Teste de navegador novo** `saf_c01_test.py`, em 1440 e 390 px:
  - `fluxo_gravar_editar` (`:48`) e `fluxo_dividir` (`:64`); o café de 2020 é criado pela própria tela, numa parcela do B1 da Boa Vista;
  - gravar, editar e dividir com excesso são recusados com a mensagem da trava, e o limite (soma = 120 ha) grava;
  - só a checagem da tabela injeta estado de dado antigo, como o S3.4 já fazia.
- **Especificação**: `docs/planejar-safra/etapa-2-talhoes/ESPECIFICACAO.md`, seção 3.4, R-14 (T-soma e mensagem).
- **Brutos** em `<sp-safc01>/docs/planejar-safra/verificacao-saf-c01/`:
  - `antes.json` (sha256 ca30613…, 2 passam, 1 falha) e `depois.json` (sha256 e5c3759…, 3/3), saídas do harness do Codex;
  - `harness_codex_6079770308.js`, `bateria.txt`;
  - `ocupacao_unit_antes.txt` / `ocupacao_unit_depois.txt` e `navegador_antes.txt` / `navegador_depois.txt`;
  - `desempenho.js`, `desempenho_fixture.py`, `desempenho.json`, `mensagem_perene_perene.txt`.

**Testes (todos executados)**

| Comando | Resultado |
|---|---|
| harness do Codex na base | 2 passam, 1 falha (PERENE-ANTIGO-EXCESSO não trava) |
| harness do Codex depois | 3/3 passam; trava `[["soma","cafe","soja",20970,110]]`, pendência de 9 dias igual ao controle recente |
| `python3 build.py`, `grep -c FALHA` | 0 falhas; 140 telas |
| `python3 montar_render.py` | 140 páginas montadas |
| `ocupacao_unit.py` na base | 109 OK, 5 FALHA (o teste pega o defeito) |
| `ocupacao_unit.py` depois | 117 OK, 0 FALHA (9 s; antes 19 s) |
| `saf_c01_test.py` com o serviço da base | 16 ok, 22 falhas: a tela grava 90 ha |
| `saf_c01_test.py` depois | 38 ok, 0 falhas (1440 e 390) |
| `varredura.py` | 140/140 páginas sem erro |
| `ocupacao_test.py` | 65 ok, 0 falhas |
| `saf_revisao_test.py` | 42 ok, 0 falhas |
| `saf_operacoes_test.py` | 87 ok, 0 falhas |
| `tabelas_saf_test.py` | 24/24 ok |
| `capacidade_unit.py` | 76 OK, 0 FALHA |
| `rend_multiconjuntos_unit.py` | 106/106 OK |
| `partest.py` | 46 ok, 1 falha: é o vermelho conhecido da base "T1-C copia ajuste do T1-B" (o teste sai com código 0 mesmo assim) |

**Desempenho** (mediana de 50 execuções com `process.hrtime`, 3 rodadas no mesmo processo alternando base e correção, em ms)

| Medida | Base (3 rodadas) | Correção (3 rodadas) |
|---|---|---|
| Lagoa Grande `ocTabela` LG2627 | 16,80 / 16,06 / 15,53 | 6,10 / 3,76 / 3,70 |
| Lagoa Grande `ocTabela` nova 2027/28 | 22,64 / 15,67 / 20,93 | 4,65 / 4,09 / 4,15 |
| Lagoa Grande `ocChecar` lg01 | 2,51 / 1,70 / 2,27 | 0,87 / 0,83 / 0,85 |
| Santa Rita `ocTabela` S27SF | 3,37 / 3,06 / 3,12 | 1,23 / 1,19 / 1,39 |
| Santa Rita `ocChecar` T1-B | 2,68 / 2,40 / 2,37 | 0,89 / 1,07 / 1,55 |
| Santa Rita `ocPlantioMin` T1-B | 2,55 / 2,93 / 1,83 | 0,28 / 0,23 / 0,17 |
| Extremo (perene de 1996 + 20) `ocChecar` | 7,95 / 5,21 / 4,80 | 2,23 / 2,05 / 1,87 |
| Extremo `ocTabela` | 1,53 / 0,97 / 1,00 | 0,32 / 0,34 / 0,33 |

No caso extremo, a base não trava 510 ha em 500 ha; a correção trava, e o limite de 500 ha passa. Mensagem perene + perene: 50.034 ms na base, 1 ms depois.

**O que ficou fora**
- **Nome sugerido no Dividir:** a parcela nova vem como B1-A, que é a parcela do café de outra safra. A trava de faixa recusa, então não há dano, mas confunde quem usa. Fica em `safra.js`, fora desta frente; no teste renomeei para B1-C.
- **Dividir com perene não vinculada:** com o café só na safra de 2020, o B1 oferece "Vincular ciclo ›" em vez de "Dividir". Por isso o teste de dividir registra o café de 2020 numa safra 2026/27, que cruza a de 2027.
- **`docs/STATUS.md`** não foi atualizado, para não conflitar com as outras frentes; fica com o integrador.
- **Desempenho do Gemini:** a alegação dele continua não medida. Os números acima são da correção por eventos, não da proposta `o.ini + 900`.
- O navegador é emulação no Chrome headless, não aparelho físico.

## verificacao

Três lentes independentes (agentes Claude separados do autor; não é a revisão do Codex). Texto de cada achado como a lente registrou; "executado"/"especificado" são da própria lente.

### Lente oraculo

#### oraculo-1 · S3 · A área livre do toast do Planejar, do painel Dividir e do toast do Dividir ignora a perene sem fim. O pedido do ADENDO do Codex (6079770308) não foi atendido nem citado no relato.
- **reproducao:** Executado no Chrome headless, contra o _render da worktree em ef0d7b2, que já contém a varredura por eventos. Comando: env PYTHONDONTWRITEBYTECODE=1 CHROME_BIN=<chrome> flock /tmp/cdpF.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 <scratchpad>/safc01-oraculo/ui_adendo_codex.py 1440 900 0 (e também com 390 844 1). Roteiro do ADENDO: C1 tem café de 2019 reduzido a 20 ha, safra 2028, soja em C1-B. A trava está certa: 30 e 19 ha são recusados com 'Máximo 18 ha', e 18 ha grava. Depois de gravar os 18 ha, o toast diz 'Cultivo incluído como parcela C1-B · 20 ha livres em C1 · plano Soja alta tecnologia.' A área livre real é 38 − 20 − 18 = 0, e a própria tabela mostra ÁREA LIVRE '—'. Segundo roteiro, ui_livre_dividir.py: café de 2020 com 40 ha no B1 da Boa Vista (120 ha) e soja de 80 ha. O toast do Planejar diz '40 ha livres em B1'. O painel Dividir com 50 + 30 mostra 'Talhão 120 ha · alocado 80 ha · livre 40 ha · 40 ha livres'. Com 50 + 70, o selo fica verde em 'Área conferida' ao lado da recusa vermelha 'A divisão travaria a área… Nada foi gravado'. O toast do Dividir 50 + 30 diz 'B1 dividido em 2 parcelas · 40 ha livres'. A área livre real nos dois casos é 0. Saídas brutas: ui_adendo_1440.txt, ui_adendo_390.txt e ui_livre_dividir.txt.
- **causa:** tools/prototipo/v37/gen37/safra.js:797-799 (cultAfter: livre = T − Σ só desta safra). safra.js:860 (dvSave: toast com T − A). safra.js:864-865 (divVals: dv_resumo e dv_selo com L = T − A). Nenhum desses pontos usa a ocupação de fora que o serviço já calcula: ocTabela, L.area_livre e mfirst 'pior'. A observação do integrador no ADENDO pede que toast, painel e tabela saiam da mesma fonte da trava, incluindo a perene sem fim. O commit ef0d7b2 não mexe em safra.js, e o relato não menciona o assunto.
- **correcao:** Tirar a área livre de uma função única do serviço, por exemplo ocLivre(ctx, safra, occ, t, T), extraída do mfirst de ocTabela: a área livre do talhão descontando as ocupações de fora em modo pior. Usar essa função no toast do cultAfter, no toast do dvSave e em dv_resumo e dv_selo. No Dividir, comparar o total alocado com T − pior das ocupações de fora no período das partes, e não com T. Selo 'Área conferida' só quando nenhuma parte trava. Regressão: no saf_c01_test.py e no roteiro do ADENDO, conferir o toast '0 ha livres' (ou a ausência de área livre) depois do limite e o selo ≠ 'Área conferida' quando o Salvar é recusado.

#### oraculo-2 · S3 · Defeito pré-existente, não é regressão: um par antigo na mesma faixa (dado antigo) desliga a T-soma do dia inteiro. É um contraexemplo à nova frase da R-14 de que uma ocupação antiga não encurta a soma.
- **reproducao:** Executado: node <scratchpad>/safc01-oraculo/repro_cruz.js. Talhão de 100 ha com café de 1998 (40 ha, T1-A), café de 2015 (40 ha, também em T1-A: Sobreposição antiga) e soja nova de 2027 (70 ha, T1-B, com plano). Área física: 40 + 70 = 110 > 100. Saída: 'novo com perene duplicada: trav [] · tabela Sobreposição [["faixa","cafe98","cafe15",16495]]'. Controle só com o café de 1998: 'trav [["soma","cafe98","soja",20970,110]]'. O Python dá o mesmo: 'py novo [] | controle [(soma…110.0)]'. A base também dá trav [] (pelo teto). No oráculo, 109 de 3203 fixtures têm excesso físico com o alvo e nenhuma trava, sempre com um par antigo na mesma área. As 3203 também passam pelo ramo cruz do serviço, idêntico na base.
- **causa:** tools/prototipo/v37/gen37/ocupacao.js:86 ('&&!cruz(nu)') e :89 ('&&!cruz(pv)'); espelho em ocupacao.py:217 e :225. Basta um par ativo na mesma faixa ou no talhão inteiro, mesmo que não envolva o alvo, para o dia sair inteiro da soma. Em ocChecar com alvo, o par antigo não gera trava de faixa (ocupacao.js:74 pula pares sem o alvo). Assim, nenhuma regra cobre a soja nova. A R-10 admite que esse dado antigo existe ('Só acontece com dado antigo').
- **correcao:** Abrir em tarefa separada, porque está fora do SAF-C01. Na varredura, trocar o descarte do dia por uma soma física: Σ por faixa da maior área ativa, com talhão inteiro valendo T. Pares cruzados que envolvem o alvo continuam com a T-faixa. Acrescentar a fixture do repro_cruz.js ao ocupacao_unit.py e ao oráculo. Até lá, a frase nova da R-14 na ESPECIFICACAO.md §R-14 deveria ressalvar o caso de faixa com sobreposição antiga.

#### oraculo-3 · S3 · Defeito pré-existente, não é regressão: com três ou mais ocupações, a mensagem M1 mostra período invertido e um 'Máximo X ha' que não destrava. A correção torna a M1 alcançável em mais casos.
- **reproducao:** Executado: node <scratchpad>/safc01-oraculo/repro_m1.js. Talhão de 100 ha: soja de 40 ha em T1-A (plantio 28/03/2030), soja de 25 ha em T1-B (plantio 21/10/2030) e milho alvo de 61 ha em T1-D (plantio 10/06/2030), todos com plano, folga 0. A base e o novo dão o mesmo: 'msg: De 01/10/2030 a 26/07/2030, 25 ha de T1 estão com Soja (T1-A…) e Soja (T1-B…). Máximo 75 ha nesse período. | com o Máximo (75 ha) trav [["soma","soja40","milho",22075,115]] | com 60 ha trav []'. Na amostra aleatória (saida_m1b.js), 2 de 100 travas só de soma têm um Máximo que não resolve. F1925.0 falha na base e no novo. F1756.0 só ficou alcançável com a correção: semdata com folga 0, que fica fora de 'outros'.
- **causa:** tools/prototipo/v37/gen37/ocupacao.js:171: ini = máx dos inícios de todos e fim = mín dos fins de todos. Com três ou mais ocupações, ini pode ficar maior que fim. As linhas :173-174 calculam o pior dia só nessa janela, que pode excluir o dia da trava. Espelho em ocupacao.py:406-411. A janela segue o texto da R-14 ('interseção dos dois períodos'), pensado para duas ocupações.
- **correcao:** Calcular o pior dia nos dias de núcleo do alvo, que é o critério da própria trava, pelos mesmos pontos de evento. Citar o período desses dias. Máximo = T − maior Σ dos núcleos dos outros nesses dias. Propriedade de regressão: regravar com o Máximo não deixa trava de soma, como em saida_m1b.js. Abrir em tarefa separada.

#### oraculo-4 · S4 · A pista 'Plantio a partir de' passa a dizer 'sem janela antes do fim da safra' quando o problema é a área, não a data.
- **reproducao:** Executado: ui_adendo_codex.py em 1440 e 390. Com a soja de 30 ha em C1-B, os campos do painel mostram pmin_txt = 'sem janela antes do fim da safra', enquanto o alerta diz corretamente 'Máximo 18 ha nesse período'. Com o café sem fim, nenhuma data resolve 30 ha. Na base a pista dava uma data, porque a soma não travava.
- **causa:** tools/prototipo/v37/gen37/safra.js:505-506: pminDraft procura uma data com a área do rascunho. Quando a trava de soma vem de uma perene sem fim, a busca nunca encontra janela e a pista aponta para a data.
- **correcao:** Quando ocChecar devolver trava de soma ou de safra que não depende do plantio, mostrar '—' ou 'reduza a área (máximo X ha)' em vez de 'sem janela'. Cosmético: o alerta já dá a saída certa.

#### oraculo-5 · S4 · Defeito pré-existente e teórico nos dados atuais: com folga 0, uma cultura sem ciclo no CD-02 tem núcleo de um dia que some na T-faixa.
- **reproducao:** Executado: node <scratchpad>/safc01-oraculo/repro_folga0.js. Sorgo de talhão inteiro (100 ha, com plano, sem cultivar com ciclo) sobre café perene de talhão inteiro. Saída: 'base folga 0 trav []', 'base folga 1 trav [["faixa",…]]', 'novo folga 0 trav []', 'novo folga 1 trav [["faixa",…]]'. Nos dados sintéticos todas as anuais têm ciclo (Soja, Milho e Feijão) e a folga padrão é 1, conferido em CEN.cultivares e D2.folga.
- **causa:** tools/prototipo/v37/gen37/ocupacao.js:52 (nuc = plantio sem ciclo mínimo) combinado com :76, que intersecta [plantio, nuc + folga) e dá vazio com folga 0. Já ocNucAtivo (:59) conta o dia do plantio.
- **correcao:** Na T-faixa e no 'outros' da M1, usar um fim de núcleo de pelo menos plantio + 1, coerente com ocNucAtivo. Abrir em tarefa separada se a folga 0 entrar em uso.

**O que a lente tentou e não quebrou**
- Oráculo diferencial, executado. 3203 fixtures geradas com semente 20261009 (fixtures.json, sha256 dc129ee6…), cobrindo: perenes antigas (1996–2021) e recentes, anuais com plano publicado e em rascunho, colheita informada, estimado, sem ciclo, observado, mesma faixa e faixas distintas, talhão inteiro, áreas no limite (±0,004, ±0,005, ±0,006, ±0,01), edição, Dividir em 2 ou 3 partes (1133 fixtures), ciclo vinculado, outra fazenda e outro talhão, folga 0, 1 e 3. Resultado: o JS novo e o Python novo coincidem exatamente com o oráculo dia a dia (horizonte 31/12/2080) em 323 fixtures com trava de soma, 277 com pendência de soma R-15 (novas = depois − antes), na tabela (trav e pend de soma, exc, próprias e de fora, Situação Sobreposição), na faixa com '· N ha em sobreposição' e em 877 mensagens M1 (pior dia e 'A partir de'). Divergências: 0.
- Variante de dados estranhos, executada: 1204 fixtures, semente 777, com colheita real ou informada antes do plantio, área 0, T de 0,01 e 5, folga 30 e anos até 2069. Divergências do JS e do Python novos contra o oráculo: 0.
- Paridade JS × Python no novo, executada sobre 4407 fixtures, conferindo trav, pend, aviso, mensagem da trava, mensagem da pendência e trav, pend, Situação, exc, faixa e texto da faixa na tabela: 0 divergências.
- O oráculo pega o defeito original, executado contra ecc8b00 (ocupacao.js ca306131, ocupacao.py 9c512457). Em 225 fixtures a base não trava e devia, igual em JS e Python, sem nenhum falso positivo. Fixture mínima: o caso do Codex com 2 ocupações (CODEX-2020-70). Variante encolhida de F0013.0: mamão alvo de 0,01 ha em 2030, com café de 2020, soja observada e milho em 2031; o oráculo dá [soma, alvo+o1+o4, o5, 22417, 150.01] e a base dá [].
- O oráculo tem dentes, executado. Mutantes do serviço novo: sem o ponto ocNucLib dá 22, 188 e 227 divergências; sem plantio + 1 dá 0, 15 e 15; sem a liberação est dá 0, 239 e 278; contagem errada da pendência dá 0, 269 e 315 (trav, pend e tabela). Mutante no Python: 269 divergências de paridade de pend.
- O que não é soma ficou igual entre base e novo, executado nas 4407 fixtures: travas de faixa, observado e safra, pendências de par e avisos, em JS e em Python.
- Dados sintéticos do protótipo, executado (dados_demo.py). 47 linhas de tabela das 4 safras (S2627, S27SF, S2526 e LG2627) saem idênticas na base e no novo. O ocChecar dos 40 cultivos existentes não mudou, e nenhum trava ao salvar sem mudança.
- Harness do Codex (6079770308), executado: base com 2 passam e 1 falha (rc 1); novo com 3/3 (rc 0) e trava [[soma, cafe, soja, 20970, 110]].
- Rota de UI do ADENDO do Codex (S2627, C1), executada em 1440×900 e 390×844 com toque. 30 ha e 19 ha recusados com 'De 12/05/2028 a 27/09/2028, 20 ha de C1 estão com Café (C1-A, Safra 2026/27). Máximo 18 ha nesse período.', painel aberto, rascunho mantido e nada gravado. 18 ha grava. Editar para 19 ha é recusado e a área continua 18. Sem erro de JS.
- Dividir na UI, executado: café de 2020 no B1 com 50 + 70 é recusado ('A divisão travaria a área… Nada foi gravado'); 50 + 30 grava.
- ocupacao_unit.py do autor, executado de forma independente: 117 OK e 0 FALHA (rc 0).
- Mensagem perene + perene, executada: a base leva 86.105 ms (congela a tela) e o novo leva 1 ms, com 'A partir de 01/06/2027, 40 ha de T1 estão com Café…'.
- Desempenho com histórico longo, executado e só indicativo (medição única, sem mediana): com 62, 152 e 242 ocupações num talhão, o ocChecar fica parecido ou mais rápido no novo (46 contra 56 ms, 111 contra 238 ms, 203 contra 253 ms). Sem travamento.
- Ocupação com plantio vazio no talhão, executado: sem erro, mesmo resultado na base e no novo.
- Aplicar plano (linha e lote): só especificado por leitura de código, não executado no navegador. apAvalia (safra.js:1403) chama ocAvaliaCultivo, que é o mesmo caminho do Salvar.

**Comandos registrados pela lente**

| Comando | Resultado |
|---|---|
| `git -C <sp-safc01> show ecc8b00:tools/prototipo/v37/gen37/ocupacao.{js,py} e ef0d7b2:… copiados para .../scratchpad/safc01-oraculo/{base,novo}/ ; sha256sum` | base js ca306131… e py 9c512457…; novo js e5c3759e… e py 616593e6…, iguais aos arquivos da worktree |
| `python3 gera.py 3200 20261009 > fixtures.json (em <scratchpad>/safc01-oraculo)` | 3203 fixtures (novo 1552, divide 1133, edita 515, codex 3); sha256 dc129ee668043448… |
| `node oraculo.js fixtures.json > oraculo.json` | rc 0 em 44,9 s; força bruta dia a dia até 31/12/2080 |
| `node roda_servico.js novo/ocupacao.js fixtures.json; python3 roda_servico.py novo fixtures.json; node roda_servico.js base/ocupacao.js fixtures.json semmsg; python3 roda_servico.py base fixtures.json semmsg` | rc 0 nos quatro; tempo total do serviço: js novo 3,4 s, py novo 4,7 s, js base 15,6 s, py base 23,4 s |
| `python3 compara.py fixtures.json oraculo.json js_novo.json py_novo.json js_base.json py_base.json divergencias.json` | Novo, JS e Python: 0 divergências (trava e pendência de soma, tabela, exc, M1, paridade). Base: 225 trav_soma (nao_trava_e_devia 225, trava_e_nao_devia 0) e 173 pend_soma, em JS e em Python. Saída em compara.txt |
| `python3 gera_estranho.py 1200 777 > fixtures_estranho.json; oráculo, 4 serviços e compara.py` | Novo: 0 divergências. Base: 106 travas de soma perdidas. Saída em compara_estranho.txt |
| `mutantes mut/M1..M4 (JS) e mutpy (Python) contra oraculo.json` | Todos detectados: 22/188/227, 0/15/15, 0/239/278, 0/269/315; Python com 269 divergências de paridade de pend |
| `python3 encolhe.py fixtures.json F0013.0 base/ocupacao.js` | Fixture mínima com 4 cultivos; oráculo [[soma, alvo+o1+o4, o5, 22417, 150.01]], base [] |
| `node harness_codex.js base/ocupacao.js ; node harness_codex.js novo/ocupacao.js` | base rc 1 (PERENE-ANTIGO-EXCESSO falha); novo rc 0 (3/3) |
| `PYTHONDONTWRITEBYTECODE=1 python3 dados_demo.py` | 47 linhas de tabela com 0 diferenças; 40 cultivos com ocChecar sem diferença e nenhuma trava ao salvar sem mudança |
| `cd <sp-safc01>/tools/prototipo/v37/gen37 && PYTHONDONTWRITEBYTECODE=1 SAFRION_DADOS=sintetico python3 ocupacao_unit.py` | rc 0; RESULTADO: 117 OK, 0 FALHA (saída em ocupacao_unit_revisor.txt) |
| `env PYTHONDONTWRITEBYTECODE=1 CHROME_BIN=<chrome> flock /tmp/cdpF.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 ui_adendo_codex.py 1440 900 0 (e 390 844 1)` | rc 0 nos dois. 30 e 19 ha recusados com 'Máximo 18 ha'; 18 ha grava; edição para 19 recusada; toast '20 ha livres em C1' (o real é 0); erros_js vazio |
| `(mesmo prefixo) python3 ui_livre_dividir.py` | rc 0. Toast do Planejar '40 ha livres em B1'; painel Dividir 'livre 40 ha'; com 50 + 70, selo 'Área conferida' junto da recusa; toast do Dividir '40 ha livres' (o real é 0) |
| `node repro_cruz.js ; node repro_m1.js ; node repro_folga0.js ; node saida_m1b.js novo/ocupacao.js fixtures.json ; node saida_m1b.js base/ocupacao.js fixtures.json` | Os três defeitos pré-existentes saem iguais na base e no novo (só o controle do repro_cruz muda, e trava no novo como deve). Máximo da M1 não resolve em 2 de 100 travas no novo e em 1 de 30 na base |
| `node msg_perene.js novo ; timeout 180 node msg_perene.js base` | novo 1 ms ('A partir de 01/06/2027…'); base 86.105 ms ('De 01/06/2027 a sem fim…') |
| `node desempenho_hist.js {10,25,40} {base,novo}` | ocChecar por chamada: 56 contra 46 ms, 238 contra 111 ms, 253 contra 203 ms (base contra novo). Sem travamento. Medição indicativa, sem repetição |
| `git -C <sp-safc01> status --short \| grep -v '^??' ; git log -1` | Nenhum arquivo versionado alterado; HEAD continua em ef0d7b2 |

### Lente tela

#### tela-1 · S3 · O aviso de área livre depois de gravar ou dividir ignora o café de outra safra. O aceite do ADENDO do Codex no comentário 6079770308 continua não atendido.
- **reproducao:** Executado em ef0d7b2, 1440x900 e 390x844. Comando: env CHROME_BIN=<chrome> flock /tmp/cdpF.lock env CDP_GL=1 SAFRION_DADOS=sintetico RENDER_DIR=<scratchpad>/safc01-ui/render_fix ROTULO=fix timeout 900 python3 <scratchpad>/safc01-ui/ui_adversarial.py tudo A,B,C,D (saída em ui_fix.txt). Para B e D, rodada corrigida em ui_fix_BD.txt.
  
  Cenário do ADENDO: C1 tem 38 ha, com café de 2019 reduzido a 20 ha (C1-A) na Safra 2026/27. Na safra nova de 2028 entra soja de 18 ha (o limite) na C1-B.
  - Aviso exibido: 'Cultivo incluído como parcela C1-B · 20 ha livres em C1 · plano Soja alta tecnologia.'
  - Na mesma tela, a tabela mostra C1 'Planejado' com Área livre '—'. O correto é 0 ha livre (38 − 20 − 18).
  
  No Dividir (fluxo D), com o mesmo café numa safra de 2027 que cruza o período: 'C1 dividido em 2 parcelas · 20 ha livres.'
  
  FALHA nos 4 casos (2 fluxos × 2 larguras). A base ecc8b00 tem o mesmo defeito: '8 ha livres' depois de gravar 30 ha (ui_base.txt).
- **causa:** - safra.js:797-799 (cultAfter) calcula a sobra como T menos a soma das áreas desta safra no talhão.
  - safra.js:860 (dvSave) calcula a sobra como T − A.
  - Nenhum dos dois passa pelo ocTabela/ocAvalia. Ficam de fora as perenes sem fim e as ocupações de outras safras.
  - Isso contraria a R-09 (docs/planejar-safra/etapa-2-talhoes/ESPECIFICACAO.md:275) e o aceite A3 (:592, 'nunca como livres').
  - Contraria também o ADENDO do comentário 6079770308: a área livre do aviso, do painel e da tabela tem de sair da mesma fonte que a trava.
  - A correção ef0d7b2 não mexeu nesse ponto, e o relato do autor não responde ao ADENDO.
- **correcao:** - Tirar a área livre do aviso do próprio serviço. Depois de gravar, montar as ocupações com as linhas novas (ocTodos), usar o area_livre da linha t que o ocTabela devolve e, quando der 0, trocar o trecho por 'C1 sem área livre'.
  - Fazer o mesmo no dvSave.
  - Proteção de regressão no teste de navegador:
    - rota do ADENDO (soja de 18 ha): o aviso não pode anunciar '20 ha livres';
    - Dividir 10 + 8: o aviso não pode trazer 'ha livres'.
  - O fluxo A/D do ui_adversarial.py já falha hoje e serve de modelo.

#### tela-2 · S3 · O painel Dividir propõe uma divisão que a própria trava recusa e a marca como 'Área conferida'.
- **reproducao:** Executado em ef0d7b2, 1440x900 e 390x844. Comando: ... python3 <scratchpad>/safc01-ui/fluxo_E_dividir_sugestoes.py (saídas ui_fix_E.txt e ui_fix_E390.txt; capturas fix_E_dividir_1440.png e fix_E_dividir_390.png). Cenário: C1 com café de 2019 (20 ha, C1-A, Safra 2026/27), safra SR 2027 que cruza o período e soja de 18 ha na C1-B.
  
  '+ Adicionar parcela':
  - pré-preenche [('C1-B','18'),('C1-A','20')], com o nome da parcela do café;
  - o selo verde diz 'Talhão 38 ha · alocado 38 ha · livre 0 ha · Área conferida';
  - Salvar responde 'A divisão travaria a área: 1 parcela… Nada foi gravado.'
  
  'Distribuir área igualmente':
  - reparte 19 + 19 e mantém 'Área conferida';
  - Salvar responde 'Nada foi gravado';
  - cada parcela recebe a mensagem '… 39 ha de C1 estão com Café (C1-A…) e Soja (C1-C…). Máximo 0 ha nesse período.' Em nenhum momento aparece o limite real, que é de 18 ha somando as parcelas.
  
  Nada é gravado, então não há dano ao dado. O painel, porém, leva a agrônoma direto à recusa.
- **causa:** - safra.js:863-865 (divVals): dv_resumo e dv_selo usam T − Σ parcelas.
  - safra.js:887-891 (dv_add): a área pré-preenchida é T − A2, e o nome vem de nextNome com os nomes só desta safra (safra.js:526).
  - safra.js:895 e safra.js:816 (dvDist): reparte T inteiro.
  - O ocMsgTrava (ocupacao.js:168-176), avaliado por parcela no dvSave (safra.js:852), conta a parcela irmã como ocupação de fora. Por isso cada parcela recebe 'Máximo 0 ha'.
- **correcao:** - Calcular a capacidade do Dividir pelo serviço: área desta safra no talhão + L.area_livre da linha do ocTabela (ou T menos a pior ocupação de fora no período das parcelas).
  - Usar essa capacidade no resumo, no selo, no '+ Adicionar parcela' e no 'Distribuir área igualmente'.
  - Gerar o nome pelas faixas de todas as ocupações do talhão (ocTodos, mesma fazenda e talhão).
  - No dvSave, trocar a mensagem por parcela por uma agregada, por exemplo: 'As parcelas somam 38 ha; com o Café (C1-A, Safra 2026/27) o máximo é 18 ha.'
  - Proteção de regressão: fluxo E.

#### tela-3 · S3 · Defeito antigo, fora dos arquivos do SAF-C01, no mesmo caminho de gravar com perene. Perene nova numa safra antiga com anual futura: a parcela sugerida colide e a mensagem manda replanejar a anual, o que não resolve e devolve a mesma recusa.
- **reproducao:** Executado na correção e na base, 1440x900. Comando: ... python3 <scratchpad>/safc01-ui/fluxo_F_sugestao_perene.py desktop (saídas ui_fix_F.txt e ui_base_F.txt). Cenário: soja de 90 ha no B1 (BV 2027) e, depois, safra 2020 com Planejar B1 e café de 30 ha, sem digitar a parcela. 30 + 90 = 120 cabe na soma.
  - O painel mostra 'B1', mas grava como B1-A, a parcela da soja de 2027.
  - Recusa: 'B1-A tem Soja da BV 2027 primeiro desde 01/06/2027… replaneje esse soja para 05/07/2027 ou depois.'
  - Depois de replanejar a soja para 05/07/2027, como a mensagem pede, a nova tentativa recebe a mesma recusa com a mesma saída. A orientação entra em laço.
  - A base ecc8b00 tem o mesmo comportamento.
  - A saída que funciona é digitar outra parcela (B1-C grava, como mostra o fluxo B).
- **causa:** - safra.js:463-466 e safra.js:469-471 (sugerirParcela e parcelaFinal) chamam nextNome (safra.js:526) só com os nomes desta safra e de L.fora, as ocupações que cruzam a janela da safra. A soja de 2027 fica de fora da safra 2020.
  - ocupacao.js:191-193 (ocMsgSemJanela) estima o fim do café por ocFimEstimado, um valor finito, embora a perene não tenha fim (OC_INF). Por isso propõe replanejar a anual, o que nunca libera a faixa.
- **correcao:** Em tarefa separada, porque está fora de ocupacao.js e ocupacao.py e já existia antes:
  - nextNome/parcelaFinal devem evitar as faixas de todas as ocupações do talhão.
  - Em ocMsgSemJanela, quando a ocupação nova ou a outra for perene, não sugerir replanejar; sugerir outra parcela livre, por exemplo: 'use outra parcela (ex.: B1-C)'.
  - Proteção de regressão: fluxo F.

**O que a lente tentou e não quebrou**
- Rota do ADENDO do Codex, executada em 1440x900 e 390x844. No C1 de 38 ha, com café de 2019 reduzido a 20 ha (C1-A), a soja de 30 ha na C1-B (safra 2028) é recusada com 'De 12/05/2028 a 27/09/2028, 20 ha de C1 estão com Café (C1-A, Safra 2026/27). Máximo 18 ha nesse período.' e nada é gravado. Na base ecc8b00 o mesmo salvar gravou 30 ha (controle).
- Duplo clique pelo CDP (mousePressed/Released com clickCount 1 e 2) e duplo toque a 390 em Salvar, com excesso: recusa nas duas larguras. Dois .click() no mesmo tique do JS: recusa. No limite de 18 ha, dois .click() síncronos gravam uma linha só.
- Volta ao rascunho: depois das recusas, cultura, plano, plantio, parcela, área e meta ficam intactos. Escape mostra 'Há alterações não salvas' e não fecha; 'Continuar editando' volta ao rascunho com 30 ha e C1-B.
- O limite exato grava: soja de 18 ha no C1 (2028 e 2027), café de 30 ha no B1 de 120 ha e divisão 10 + 8 no C1. Depois de gravar, a tabela mostra C1 'Planejado', Área livre '—' e nenhuma Sobreposição.
- Editar para cima é recusado e a área gravada não muda: soja 18 → 19 ha (C1) e café 30 → 31 ha (B1, safra 2020).
- Ordem inversa: com a soja de 2027 (90 ha) gravada primeiro, o café de 2020 de 40 ha numa safra 2020 é recusado ('Máximo 30 ha'), e mais um café de 10 ha é recusado ('Máximo 0 ha'). A base grava os dois.
- Aplicar plano com ocupação antiga: soja de 2020 com plano no B1 e duas sojas sem plano em safras de 2027 que se cruzam (70 + 70 > 120). O painel mostra 'não recebe: … Máximo 50 ha' e 'Aplicar plano em 0 cultivos', e o plano não é aplicado. A base aplica.
- Dividir com café de 2019 numa safra de 2027 que cruza: 10 + 9 é recusado com 'Nada foi gravado' e o motivo; 10 + 8 grava. A base grava 10 + 9.
- Sem erro de JS e sem rolagem lateral em todos os fluxos (A a F), em 1440x900 e 390x844. É emulação no Chrome headless, não aparelho físico.
- Busca por chamadores (grep em todo o gerador): ocChecar, ocAvalia, ocTabela, ocPlantioMin e ocMsgTrava só aparecem em ocupacao.js e safra.js. O cultCheck é chamado por g2lib.js:127 via processo_safra.py:240. Quem grava cultivo: g2save→cultCheck→ocAvaliaCultivo, dvSave→ocChecar (safra.js:852) e doApply→apAvalia→ocAvaliaCultivo; o cultAfter roda só depois do g2save. Não achei gravador sem trava. O 'Vincular ciclo' cai em chk.o nulo pela deduplicação do ciclo, mas não acrescenta área, porque área, plantio e faixa vêm do ciclo. Isso é especificado por leitura do código, não executado.
- Diferencial JS independente, executado: 1200 conjuntos aleatórios, com folga 0, 1 e 3, plantios de 1995 a 2030, perene, plano com DAP negativo, DATA, DAPC e DANC, colheita informada ou real, sem ciclo e ciclos repetidos. O ocAvalia por eventos deu exatamente o mesmo que o laço dia a dia da base com o teto ampliado para d0+60000 (trava e pendência R-15): 0 diferenças, 204 conjuntos com trava de soma, 99 com pendência de soma, 11,8 s.
- Harness do Codex (6079770308): na correção 3/3 (PERENE-ANTIGO-EXCESSO trava [[soma,cafe,soja,20970,110]], pend 9 dias, sit Sobreposição, exc 10). Na base, 2 passam e 1 falha.
- Execuções repetidas por mim: ocupacao_unit.py com 117 OK e 0 FALHA (paridade JS = Python incluída); cópia do saf_c01_test.py do autor com 38 ok e 0 falhas; build com 0 FALHA e 140 telas; montar_render com 140 páginas. Nenhum arquivo versionado da worktree foi alterado (git status sem mudanças rastreadas).
- Não executado: largura 360 px, varredura.py, ocupacao_test.py, saf_revisao_test.py, Vincular ciclo pela tela e troca de fazenda de uma safra com cultivos.

**Comandos registrados pela lente**

| Comando | Resultado |
|---|---|
| `cd <sp-safc01>/tools/prototipo/v37/gen37 && python3 build.py > <scratchpad>/safc01-ui/build.log; grep -c FALHA; python3 montar_render.py` | 0 FALHA; 140 artboards; _render montado com 140 páginas e 20 arquivos (só arquivos gerados e não rastreados; git status sem mudança rastreada) |
| `git archive ecc8b00 tools/prototipo \| tar -x -C <scratchpad>/safc01-ui/base; SAFRION_DADOS=sintetico python3 build.py; python3 montar_render.py (na cópia da base)` | Base montada fora do repositório: 0 FALHA, 140 páginas, ocupacao.js sha256 ca3061319ae0… (igual ao citado pelo Codex) |
| `node <scratchpad>/safc01-ui/harness_codex.js <ocupacao.js da correção \| da base>` | Correção (e5c3759e16e7): 3/3 passam, exit 0. Base (ca3061319ae0): PERENE-ANTIGO-EXCESSO FALHA (trav [], sit Planejado) e os outros 2 passam, exit 1 |
| `node <scratchpad>/safc01-ui/diff_eventos.js <ocupacao.js correção> <ocupacao.js base>` | {conjuntos:1200, com_trava_soma:204, com_pend_soma:99, diferencas:0, ms:11845}, exit 0 |
| `env CHROME_BIN=<chrome> flock /tmp/cdpF.lock env CDP_GL=1 SAFRION_DADOS=sintetico RENDER_DIR=<scratchpad>/safc01-ui/render_fix ROTULO=fix timeout 900 python3 ui_adversarial.py tudo A,B,C,D` | Saída em ui_fix.txt: 50 ok e 14 falhas. Os fluxos A e C valem: o único vermelho de A é o aviso '20 ha livres' (achado 1), nas duas larguras. As falhas de B e D nesta rodada vieram de defeitos do meu script, não do produto: em B, o nome sugerido B1-A colidia por faixa (o que levou ao achado 3); em D, o meu localizador não achava o botão 'Salvar divisão'. Corrigi o script e rodei de novo na linha abaixo. |
| `(mesmo ambiente) python3 ui_adversarial.py tudo B,D` | Saída em ui_fix_BD.txt: 28 ok e 2 falhas. As 2 falhas são o aviso do Dividir '20 ha livres' (achado 1), em 1440 e 390. Todas as travas, limites e edições passam. |
| `(RENDER_DIR=base, GEN=base) python3 ui_adversarial.py desktop A,B,C,D` | Saída em ui_base.txt: 14 ok e 19 falhas. A base grava o excesso em todas as rotas (adendo 30 ha, café 2020 depois da soja, edição para cima, aplicar plano, dividir 10 + 9). O controle confirma que os testes pegam o defeito. |
| `(fix) python3 fluxo_E_dividir_sugestoes.py desktop / celular` | Saídas em ui_fix_E.txt e ui_fix_E390.txt: 3 ok e 2 falhas em cada largura. '+ Adicionar parcela' propõe C1-A com 20 ha e 'Distribuir área igualmente' propõe 19 + 19, ambos com 'Área conferida'; Salvar recusa nos dois (achado 2). |
| `(fix e base) python3 fluxo_F_sugestao_perene.py desktop` | Saídas em ui_fix_F.txt e ui_base_F.txt: 1 ok e 2 falhas nas duas versões, com comportamento igual. A parcela sugerida B1-A colide e a orientação 'replaneje esse soja para 05/07/2027' entra em laço (achado 3, defeito antigo). |
| `SAFRION_DADOS=sintetico python3 ocupacao_unit.py (worktree, só leitura)` | RESULTADO: 117 OK · 0 FALHA (23 s de relógio) |
| `(cópia do saf_c01_test.py do autor com a captura no scratchpad) python3 saf_c01_test_copia.py tudo` | RESULTADO: 38 ok · 0 falhas (tudo), exit 0 |
| `grep -rn 'ocChecar\|ocAvalia\|ocTabela\|cultCheck\|ocPlantioMin\|ocMsgTrava\|ocOcupacoes' (gerador, sem testes e _render) e grep 'g2check' / g2set em g_cult` | Chamadores só em ocupacao.js, safra.js (404, 428, 479, 753-759, 764-783, 852, 1330-1331, 1403) e g2lib.js:127 via processo_safra.py:240. Nenhum outro gravador de cultivo sem trava. |
| `git -C <sp-safc01> status --short \| grep -v '^??'` | Vazio: nenhum arquivo versionado alterado. Scripts, logs e capturas ficaram em <scratchpad>/safc01-ui/ (scratchpad = <scratchpad>) |

### Lente regressao

#### regressao-1 · S3 · Desempenho: o ocPlantioMin sem janela fica O(n²) no histórico do talhão e passa a ser alcançado com perene antiga (de ~0,3 s a ~15 s)
- **reproducao:** Executado: `node scratchpad/rd/tempo_hist_escala.js fixture.json oc_base.js oc_head.js` (talhão X de 500 ha, café de 1996 com 100 ha e mais k anos de histórico com 3 ocupações por ano; soja nova de 410 ha na 2027/28, que sempre trava; ocPlantioMin desde 01/09/2027; mediana de 3). HEAD: trav soma e 1 pendência; ocPlantioMin leva 48 ms com 1 ocupação, 334 ms com 10, 832 ms com 22, 3.477 ms com 46 e 14.886 ms com 91. Base: trav [] e pend 0, com 1,9 a 22 ms, porque não enxerga a trava e o laço para no primeiro dia. `node tempo_hist2.js` (91 ocupações): HEAD 20.522 e 27.262 ms, base 43 e 46 ms. ocChecar por chamada é parecido nos dois (perfil.js: base 22 a 25 ms, HEAD 39 a 43 ms; ocAvalia 9 a 24 ms nos dois). Tudo medido com carga média de 21 a 25 em 4 CPUs, por causa dos Chrome de outras sessões; os ms absolutos estão inflados. Nas sementes e no caso do adendo o custo é pequeno (tempo_ui.js: HEAD 48 a 102 ms ao recusar 30 ha no C1).
- **causa:** ocupacao.js:149-152: o ocPlantioMin anda dia a dia até o fim da safra e, em cada dia, chama o ocChecar (ocupacao.js:141), que usa todas as ocupações do talhão de todas as safras (`mesmo`) com 2× ocOcupacoes + 2× ocAvalia (par a par O(n²)). Antes, o teto d0+900 escondia a soma em talhão com histórico e o laço saía no primeiro dia. Agora a trava está certa, nenhum dia serve e o laço percorre a safra inteira. Caminhos de tela que disparam o laço: safra.js:756 (ocAvaliaCultivo, ao gravar, porque o excesso com perene gera a pendência de soma de 9 dias) e o pminDraft (safra.js:476-479), chamado pelo cultLive pmin_txt (:506) e pelo cultDraft (:515) a cada área nova digitada no rascunho. A tabela de desempenho do autor não cobre esse regime: ela mede ocPlantioMin só na Santa Rita, onde ele sai cedo.
- **correcao:** Antes do laço do ocPlantioMin (ou na entrada do ocAvalia dentro do ocChecar), descartar as ocupações que liberam no pior caso antes de (desde − antecedência do plano − 1). Manter sempre as da própria safra (sid), porque a T-área soma a safra inteira, e as perenes. Elas não cruzam nenhum candidato, então a trava e a pendência que envolvem o alvo não mudam. Prova de conceito fora do repositório (scratchpad/rd/mitiga.js, só 6 casos, filtro aplicado na lista de cultivos): o resultado é igual nos 6, e o tempo cai de 15.844 para 32 ms (91 ocupações) e de 4.707 para 26 ms (46). Acrescentar o histórico longo com ocPlantioMin sem janela ao desempenho.js e um teste de equivalência filtrado × sem filtro sobre conjuntos aleatórios em ocupacao_unit.py (JS e Python).

#### regressao-2 · S3 · O toast "N ha livres" depois de gravar ignora a perene de outra safra; o adendo pedia toast, painel e tabela pela mesma fonte da trava e isso não foi tratado
- **reproducao:** Executado: `env CHROME_BIN=<chrome> flock /tmp/cdpF.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 scratchpad/rd/codex_adendo.py <sp-safc01>/tools/prototipo/v37/gen37 18` (harness do adendo do Codex, soja de 18 ha no C1). HEAD: toast 'Cultivo incluído como parcela C1-B · 20 ha livres em C1 · plano Soja alta tecnologia.'. A tabela mostra C1 Planejado, ÁREA LIVRE '—', C1-A Café 20 ha e C1-B Soja 18 ha, ou seja, 38 ha = C1 inteiro, e o livre real é 0. A base dá o mesmo toast (não é regressão). Com 30 ha o HEAD recusa corretamente com 'De 12/05/2028 a 27/09/2028, 20 ha de C1 estão com Café (C1-A, Safra 2026/27). Máximo 18 ha nesse período.'. O saf_c01_test não pega o erro: no limite ele só confere 'Cultivo incluído como parcela' no toast.
- **causa:** safra.js:797: `const livre=T-leaves(all).filter(c=>c.v.talhao===t&&daSaf(c)).reduce(...)` soma só os cultivos desta safra. A trava (ocChecar) e o painel/tabela (ocTabela, area_livre) contam a perene sem fim de outra safra. O relato do autor não cita esse ponto em 'O que ficou fora'.
- **correcao:** Depois de gravar, tirar a área livre do toast da linha do talhão em ocTabela recalculada (area_livre, a mesma fonte do painel 'Livre: 18 ha'). No saf_c01_test e no caso do adendo, conferir o número do toast no limite: 0 ha livres, ou omitir o trecho quando for 0.

**O que a lente tentou e não quebrou**
- Comparei a base ecc8b00 com o HEAD ef0d7b2 em todos os testes pedidos, todos executados, e nenhum mudou de resultado. Base e HEAD: ocupacao_test 65 ok/0 nos dois, com as mesmas linhas; saf_revisao_test 42/0; saf_operacoes_test 87/0; tabelas_saf_test 24/24; partest 46 ok e 1 falha nos dois, o vermelho conhecido 'T1-C copia ajuste do T1-B'; saf_cmp_continuidade_test 31/0; etapas_celular_test 14/0; varredura 140/140 sem erro; capacidade_unit 76 OK/0; rend_multiconjuntos_unit 106/106. Unidade: a base tem 104 OK/0 com o teste dela; o HEAD tem 117 OK/0, com os mesmos 104 nomes da base e mais 13 do SAF-C01.
- saf_c01_test.py: 38 ok/0 no HEAD. Rodando o mesmo teste com o serviço da base (cópia na minha worktree da base): 16 ok e 22 falhas, e a tela grava 90 ha. O teste pega o defeito.
- Diferencial próprio em JS (difer.js) com 3.000 conjuntos aleatórios: folga 0/1/2, sem ciclo, colheita observada, talhão inteiro, ciclo compartilhado, plantios de 2005 a 2028, com e sem alvo. HEAD × referência dia a dia sem teto, escrita por mim: 0 diferenças (772 com trava de soma, 548 com pendência de soma). Base × HEAD onde o teto antigo não limita: 0 diferenças em 188. Mensagem M1 base × HEAD com período finito: 262 iguais. Linha da tabela fora de trav/pend/exc: 0 diferenças. 0 exceções.
- Sementes (sementes.js), 262 casos: ocTabela de S2627, S27SF, S2526 e LG2627 e de 7 safras novas (inclusive 2040 na Santa Rita e na Lagoa), com folga 1 e 0; ocChecar de cada cultivo sem mudança, com +10 % e com +60 % de área. Base = HEAD em tudo, ou seja, nenhuma Situação, faixa, chip ou mensagem da demonstração mudou.
- Paridade JS × Python do HEAD em 1.500 conjuntos meus (gera_conj.js + confere_py.py): ocChecar, trava, pendência, mensagens M1 e de pendência, tabela, faixa, exc e Situação, com 0 diferenças.
- R-15 nos controles (controles.js, base × HEAD). Mesma faixa, com 30 e 70 ha, café antigo e recente: trava de faixa e pend {} iguais à base. Limite exato de 60 ha e 60,005 ha (dentro da tolerância de 0,005): sem trava e sem pendência, igual à base. 60,01 ha: trava 100,01 e pendência de 9 dias. Perene recente com 70 ha: trava [soma, cafe, soja, 20970, 110] e pend {soja: [soma, cafe, 21082, 21090, 9]}, idênticas à base. A perene antiga dá agora exatamente o mesmo, inclusive com folga 0 (9 dias, de 20/09 a 28/09) e com café de 1990. Nas bordas do teto antigo (café em 12/12/2024, 13/12/2024 e 31/12/2024), a base oscilava e o HEAD é estável. A única diferença de texto é ' · N ha em sobreposição' na faixa, como especificado.
- Adendo do Codex pela tela (codex_adendo.py): a base grava 30 ha no C1 (50 ha em 38); o HEAD recusa com fato, dano e saída e mantém o painel; 18 ha gravam nos dois. Sem erro de JS.
- Desempenho, mediana de 50 com process.hrtime.bigint e 5 rodadas alternadas no mesmo processo (tempo.js), base → HEAD em ms: LG ocTabela LG2627 20,59 → 5,19; LG ocTabela NLG28 20,78 → 5,66; LG ocChecar lg01 1,80 → 0,73; LG ocPlantioMin lg01 1,04 → 0,03. Extremo (perene de 30 anos, 1996, + 20 ocupações): ocChecar 6,14 → 1,96, ocTabela 0,89 → 0,31, ocPlantioMin 6,70 → 1,84. Com 20 parcelas simultâneas: ocChecar 7,38 → 1,80, ocTabela 2,43 → 1,08. No extremo, a base não trava 510 ha em 500 e o HEAD trava [soma, acafe, anovo, 21092, 510]; o limite de 400 ha passa nos dois. Escala com n parcelas em 2027, sem perene antiga (mediana de 20): n=100 dá 26,3 na base e 28,4 no HEAD (empate dentro do ruído); n=200 dá 57,0 e 38,2.
- Mensagem perene + perene (pp.js, café 2026 + café 2027): a base levou 93.710 ms de relógio (47 s de CPU, sob carga) e devolveu 'De 01/06/2027 a sem fim…'. O HEAD leva 0,7 a 2 ms e devolve 'A partir de 01/06/2027…'. Com o vizinho Sorgo sem ciclo (semdata.js), o HEAD responde em 1 ms com 'A partir de'; a base passou de 20 s e foi cortada pelo timeout.
- Cultivo sem plantio (sem_plantio.js do autor): base e HEAD dão a mesma saída e não lançam exceção no JS. Na tela, o plantio é obrigatório (safra.js:836).
- Prova matemática conferida: entre dois pontos de evento seguidos, núcleo e previsão não mudam (núcleo muda em plantio, plantio+1 e nucLib; previsão em ini e lib). Depois do último ponto finito só ficam perenes, com nu = pv, então dá trava ou nada e o trecho final de 1 dia não altera a contagem. O novo oráculo de propriedades (só os dias de plantio) é mais forte que o antigo (400 dias, de 3 em 3), porque a soma dos núcleos só cresce num plantio.
- Arquivos versionados de <sp-safc01> intactos (git status sem mudanças; HEAD ef0d7b2). Só regerei project/ e _render/, que não são versionados.
- Limpeza: removi a minha worktree scratchpad/safc01-base-rd e a branch tmp/safc01-base-rd. Usei esse nome porque já existia scratchpad/safc01-base (tmp/safc01-base, criada às 12:30 por outra sessão). Essa outra worktree não foi tocada nem removida.

**Comandos registrados pela lente**

| Comando | Resultado |
|---|---|
| `cd <sp-camada-sintetica> && git worktree add -b tmp/safc01-base-rd scratchpad/safc01-base-rd ecc8b00` | Executado. Worktree da base criada; removida no fim com git worktree remove --force e git branch -D tmp/safc01-base-rd. |
| `python3 build.py > log; grep -c FALHA log; python3 montar_render.py (base e HEAD)` | Executado. rc=0 e 0 FALHA nas duas; 140 artboards; _render com 140 páginas, dados sintéticos (dados_lagoa_fonte.REAL=False). |
| `SAFRION_DADOS=sintetico python3 ocupacao_unit.py \| capacidade_unit.py \| rend_multiconjuntos_unit.py (base e HEAD)` | Executado. ocupacao_unit: base 104 OK/0 (48 s), HEAD 117 OK/0 (34 s). capacidade_unit: 76/0 nas duas. rend_multiconjuntos_unit: 106/106 nas duas. |
| `env CHROME_BIN=<chrome> flock /tmp/cdpF.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 <teste> para ocupacao_test, saf_revisao_test, saf_operacoes_test, tabelas_saf_test, partest, saf_cmp_continuidade_test, etapas_celular_test e varredura (scratchpad/rd/nav.sh, base e HEAD alternados)` | Executado. Base = HEAD em todos: 65/0, 42/0, 87/0, 24/24, 46 ok e 1 falha (vermelho conhecido da base, rc=0), 31/0, 14/0 e 140/140. As linhas ok/falha são idênticas nos dois. |
| `mesmo prefixo de navegador + saf_c01_test.py (HEAD; e cópia do teste na worktree da base)` | Executado. HEAD 38 ok/0 (rc=0); base 16 ok/22 falhas (rc=1). |
| `mesmo prefixo de navegador + scratchpad/rd/codex_adendo.py <gen37> 30\|18 (HEAD e base)` | Executado. Base com 30 ha: grava (toast '8 ha livres'). HEAD com 30 ha: recusa com 'De 12/05/2028 a 27/09/2028, 20 ha de C1 estão com Café… Máximo 18 ha'. Com 18 ha grava nos dois, com o toast '20 ha livres em C1' (errado; achado 2). |
| `node scratchpad/rd/tempo.js fixture.json 5 oc_base.js oc_head.js` | Executado. O HEAD é mais rápido em todas as 9 medidas (ver sem_quebra). No extremo, a base não trava 510 ha e o HEAD trava. |
| `node scratchpad/rd/tempo_escala.js \| tempo_hist2.js \| tempo_hist_escala.js \| perfil.js \| tempo_ui.js` | Executado. Escala de parcelas equivalente. Histórico longo com ocPlantioMin sem janela no HEAD: 0,33 s (10 ocupações) a 14,9 s (91) (achado 1). Caso do adendo: 48 a 102 ms. |
| `node scratchpad/rd/mitiga.js fixture.json oc_head.js` | Executado (prova de conceito da correção proposta, só 6 casos). Mesmo plantio mínimo; 15.844 → 32 ms e 4.707 → 26 ms. |
| `node scratchpad/rd/difer.js fixture.json oc_base.js oc_head.js 3000 777` | Executado. HEAD × referência dia a dia: 0 diferenças. Base × HEAD sem teto ativo: 0 em 188. 262 mensagens M1 iguais. 0 diferenças de tabela. 0 erros. |
| `node scratchpad/rd/sementes.js fixture.json oc_base.js oc_head.js` | Executado. 262 casos, 0 diferentes. |
| `node gera_conj.js fixture.json oc_head.js 1500 4242 conj_head.json && python3 confere_py.py <gen37 HEAD> conj_head.json` | Executado. 1.500 casos, 0 diferenças JS × Python. |
| `node scratchpad/rd/controles.js oc_base.js oc_head.js` | Executado. Mesma faixa e limite exato sem pendência nos dois. Perene recente igual à base (9 dias). Perene antiga agora igual à recente. |
| `time node scratchpad/rd/pp.js oc_base.js 2026 / oc_head.js 2026\|2020` | Executado. Base: mensagem em 93.710 ms (real 1m33,9s). HEAD: 0,7 a 2 ms. |
| `cd <sp-safc01> && git status --short \| grep -v '^??'` | Executado. Vazio: nenhum arquivo versionado alterado; HEAD ef0d7b2. |

## fechamento

**Commits** (branch `claude/v44-saf-c01`, worktree `<sp-safc01>`; sem push e sem PR)
- **d1b81f4** SAF-C01: correções da verificação
- **64a3041** SAF-C01: saídas brutas da verificação

**O que mudou** (tudo em `tools/prototipo/v37/gen37/`, salvo a especificação)
- **Serviço** (`ocupacao.js`, espelho em `ocupacao.py`):
  - `ocNucFim` (js:60, py:165): o núcleo sempre inclui o dia do plantio. A T-faixa passa a usá-lo.
  - `ocFisica` (js:71, py:185): mede a área física. Numa mesma faixa conta a maior área. O talhão inteiro cobre o talhão.
  - `ocAvalia` e `crA` (js:80/91, py:201/231): a soma usa a área física. O dia só sai da soma quando o próprio alvo está na mesma área de outra ocupação com plano. A varredura agora calcula o fim do núcleo e a liberação uma vez por ocupação.
  - `ocPlantioMin` (js:160, py:376): pré-filtro que dá o mesmo resultado sem ele. Ficam de fora as ocupações que liberam antes de todo candidato.
  - `ocPior`, `ocMaximo`, `ocPeriodoTxt` e a M1 (js:184-198, py:424-451): o pior dia é calculado pelo núcleo do alvo. O "Máximo" é arredondado para baixo.
  - `ocMsgSemJanela` com perene (js:216, py:505): diz "use outra parcela (ex.: B1-B)".
- **Tela** (`safra.js`):
  - `faixasEmUso` (464) e `sugerirParcela` (468): a parcela sugerida não repete faixas ainda ocupadas no talhão.
  - `pmArea` (486) e a pista (517): mostram "reduza a área: máximo X ha".
  - P3 com nome livre (770).
  - Aviso ao gravar pelo `livreDepois` (808/824): área livre da mesma conta da tabela.
  - `dvCap` (829): capacidade do Dividir. É usada em `openDiv` (841), no `dvSave` (recusa agregada em 879-885 e aviso em 886), no resumo e no selo do `divVals` (894), em `dv_add` (921) e em `dv_dist` (929).
- **Testes:**
  - `ocupacao_unit.py`: novas referências dia a dia (349/379); 7 casos dos achados (434); propriedade da M1 (492); PlantioMin com filtro igual a sem filtro (517).
  - `saf_c01_test.py`: verificações de aviso e Dividir; novos fluxos `fluxo_adendo` (121) e `fluxo_perene_antes` (139).
- **Especificação** `docs/planejar-safra/etapa-2-talhoes/ESPECIFICACAO.md`: linhas 305, 306, 309, 330, 563 e 564.

**Testes (todos executados)**

| Comando | Resultado |
|---|---|
| `build.py` e `grep -c FALHA` | 0 falhas, 140 telas |
| `montar_render.py` | 140 páginas montadas |
| harness do Codex | base ecc8b00: 2 passam, 1 falha<br>ef0d7b2: 3/3<br>final: 3/3, com trava `[soma,cafe,soja,20970,110]` e excesso de 10 ha |
| `ocupacao_unit.py` | 130 OK, 0 falhas |
| o mesmo teste contra ef0d7b2 | 120 OK, 10 falhas (pega todos os achados) |
| `saf_c01_test.py tudo` | 66 ok, 0 falhas |
| o mesmo teste contra o render de ef0d7b2 | 34 ok, 32 falhas (parte delas é consequência da primeira divergência) |
| `ocupacao_test` | 65/0 |
| `saf_revisao_test` | 42/0 |
| `saf_operacoes_test` | 87/0 |
| `tabelas_saf_test` | 24/24 |
| `saf_cmp_continuidade_test` | 31/0 |
| `etapas_celular_test` | 14/0 |
| `capacidade_unit` | 76/0 |
| `rend_multiconjuntos_unit` | 106/106 |
| `partest` | 46 ok, 1 falha: o vermelho conhecido "T1-C copia ajuste do T1-B" |
| `varredura.py` | 140/140 páginas sem erro |
| oráculo v2, 3203 + 1204 casos | 0 divergências no JS e no Python (soma, pendência, tabela, 936 + 343 mensagens M1) |
| 4 mutantes do serviço | todos detectados pelo oráculo |
| dados da demonstração, 262 casos | tabelas, travas e pendências iguais; só 2 mensagens M1 mudam, que antes saíam com o período invertido |

**Desempenho** (mediana em ms, 3 rodadas; máquina com carga 12 a 17 em 4 CPUs, então os números são indicativos)

| Medida | base ecc8b00 | anterior ef0d7b2 | correção |
|---|---|---|---|
| Lagoa `ocTabela` LG2627 | 17 / 28 / 31 | 5,1 / 4,5 / 4,6 | 4,5 / 6,5 / 4,1 |
| Santa Rita `ocChecar` | 3,3 / 3,4 / 4,4 | 1,1 / 0,8 / 0,9 | 1,0 / 0,9 / 0,9 |
| Extremo `ocChecar` | 4,8 / 4,7 / 5,2 | 3,4 / 3,3 / 2,4 | 1,3 / 1,1 / 1,2 |
| `ocPlantioMin` com histórico de 91 ocupações | 25 (mas não trava) | 14.000 a 15.400 | 15 a 30 |

**Achados**
- **Aceitos e corrigidos:** todos os S3 dos três verificadores (aviso de área livre, Dividir, par antigo na mesma faixa, M1 com três ocupações, parcela sugerida e P3 com perene, desempenho do PlantioMin) e os dois S4 (pista do plantio e folga 0).
- **Adaptados, com motivo:**
  - O nome da parcela evita as faixas ainda ocupadas no início da safra, inclusive as futuras, e não todas as do histórico. Assim a sucessão da R-19 continua reaproveitando nomes sem multiplicar letras.
  - O par antigo na mesma faixa foi corrigido nesta frente, e não em tarefa separada, porque contradizia a frase nova da R-14.
- **Recusados:** nenhum.

**Limites da prova (o que não foi provado)**
- A tela foi testada só em emulação no Chrome headless. Não foram testados 360 px nem aparelho físico.
- Aplicar plano (linha e lote) e Vincular ciclo não foram executados no navegador. Para Aplicar plano há só leitura de código: ele usa a mesma função do Salvar.
- O oráculo v2 foi adaptado por mim às regras novas. As regras em si (área física e quando o dia sai da soma) são decisão minha e precisam da revisão do Codex.
- Quando o alvo divide a mesma faixa com uma ocupação sem plano, o "Máximo" é conservador, não exato.
- Com parcelas plantadas em datas diferentes, a capacidade do Dividir é suficiente para não travar, mas pode ficar abaixo do que realmente cabe. Esse caso não foi testado na tela.
- O aviso continua dizendo "0 ha livres", em vez de omitir o trecho.
- `docs/STATUS.md` não foi atualizado.

**O que conferir na tela**
1. **Roteiro do ADENDO:**
   - Na S2627, reduzir o café do C1 para 20 ha.
   - Criar a safra 2028 da Santa Rita e, em "Planejar ›" no C1, lançar soja SOJA-AT em C1-B, plantio 01/06/2028, 30 ha.
   - Deve recusar com "Máximo 18 ha", e a pista do plantio deve dizer "reduza a área: máximo 18 ha".
   - Com 18 ha deve gravar, com o aviso "0 ha livres em C1".
2. **Dividir na Boa Vista:**
   - Café de 40 ha (plantio 2020) no B1, numa safra que cruza a BV 2027, e soja de 80 ha na BV 2027.
   - Ao abrir o Dividir do B1: "outras safras 40 ha · livre 0 ha".
   - "+ Adicionar parcela" deve vir com nome que não é o do café e sem área.
   - 50 + 40 ha: selo "Excede em 10 ha" e recusa agregada com "máximo 80 ha".
   - "Distribuir área igualmente" deve dar 40 + 40.
3. **Perene antes da anual:**
   - Soja de 90 ha no B1 da BV 2027; depois, café de 30 ha numa safra de 2020 com a parcela B1-A digitada: deve recusar com "use outra parcela (ex.: B1-B)".
   - Sem digitar a parcela, deve gravar em B1-B.

Arquivos principais:
- `<sp-safc01>/docs/planejar-safra/verificacao-saf-c01/correcoes/bateria.txt` (índice dos brutos)
- `<sp-safc01>/docs/planejar-safra/verificacao-saf-c01/depois.json`
