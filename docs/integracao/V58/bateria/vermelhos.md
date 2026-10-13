# V58 · classificação dos vermelhos da bateria completa

**Escopo:**
- Bateria executada na candidata v58 (`int/v58`), com dados sintéticos: 156 testes do `gen37`, 6 em paralelo.
- O `mbtest.py` ficou fora porque reescreve o `_render`.
- Saída bruta, uma linha por teste: `_resumo.txt`.

**Regra (AGENTS §3.6):**
- Cada vermelho é **defeito do produto**, **teste obsoleto** ou **falha da ferramenta**.
- Corrigir não é afrouxar: a verificação continua reprovando o defeito que protege.
- "Vermelho antigo" quer dizer que falha igual na v57 publicada (`3a76f79`), rodado no mesmo ambiente.
- Também foram conferidos os testes com saída 0 que imprimem falha: o código de saída sozinho não prova nada.

## 1. Defeito do produto (corrigido nesta versão)

| Teste | Defeito | Correção | Depois |
|---|---|---|---|
| `ma_menu_test` | Corrida no menu Manutenção: com o painel da OM aberto, trocar de visão às vezes não mudava a lista (2 de 8 trocas na contraprova). | O clique no menu grava o endereço e aplica a visão na hora (`areas/maquinas.py`). | 6/6 |

## 2. Teste obsoleto (o produto mudou por decisão registrada; a verificação foi atualizada, não afrouxada)

| Teste | O que mudou no produto | Ajuste | Depois |
|---|---|---|---|
| `cafe_apurar_test` (unidade e navegador) | Desde a CONF (v57), pesar e receber é decisão do almoxarife. | A pesagem age como Rui; o restante continua no perfil padrão. | 16/16 e 10/10 |
| `dose_divergente_test` | Desde a R14, a mensagem diz quem enviou para conferência. | O teste espera "enviada para conferência por Ana (gestora)". | 22/22 |
| `ocupacao_test` (OC-18) | Desde a v56, a dica fica em `data-dica`. | Ler `data-dica`. | 65/65 |
| `comercial_fluxo_test` | — (espera fixa de 0,9 s) | Espera pela condição. | 72/72 |
| `ma_unica_test` (AC-PCM-01) | Desde a v57, o menu Manutenção tem 4 subitens. | Esperar os 4 subitens. | 23/23 |
| `ma_planos_test` | — (pasta de captura inexistente) | Cria a pasta. | 18/18 |
| `quantidade_test` | Desde a v56, encerrar exige a conferência diária. | Paula confere cada dia apontado. | 14/14 |
| `config_test` (AL-12) | Na v58, a AL-12 passou a se chamar "Conferir o dia e decidir duplicidade de apontamento" (CONTROLE-02, `fd0b1c4`). | Procurar a AL-12 pelo ID. | 88/88 |
| `tabelas_cad_test`, TABR-CTX-02, CD-03 Vazão (4 casos) | Desde a v56 (CTL-5), as vazões vêm da fonte única da Irrigação: 540, 597,6 e 838,8 m³/h (antes 300, 340 e 45; ver `dados_cad.py`). | Esperar as vazões vigentes. A regra testada não mudou: só valores na unidade da coluna, cada um abrindo a sua linha. | 206/206 (com o CD-04) |
| `tabelas_cad_test`, CD-04 (A1) | Desde a CONF (v57, CONF-D05), o acesso ao app só se lê no painel da pessoa e se gerencia em Configurações. O campo editável era do TABR anterior. | Verificar o calendário, o acesso só para leitura com o link para Configurações e a **ausência** do campo editável (contraprova). | 206/206 |
| `saf_operacoes_test` (O1), `tabelas_saf_test`, `rend_multiconjuntos_test` | Coluna nova "Custo total" na etapa 3 do Planejar safra (pedido do proprietário, 13/10). | 9 colunas; "Custo R$/ha" e "Custo total" com chaves próprias. Unidade do custo total conferida por nível. | 87/87, 24/24, 18/18 |

## 3. Falha da ferramenta (o produto está certo)

| Teste | Causa | Prova |
|---|---|---|
| `conferencia_diaria_test`, `_nav` e `_casos_nav` | Exigem `--output`, e o executor da bateria não passou o argumento (rc=2 em 0 s). | Com `--output`: 30/30. No `_nav`, as 16 verificações do JSON estão OK. O "RESULTADO: 0/0" final é defeito do contador do próprio teste. |
| `config_test` | Estourou 900 s sob carga de 6 navegadores. | Sozinho: 88/88, depois de corrigir a AL-12 (§2). |
| `g2test` | Precisa das páginas como argumento; sem elas não verifica nada (0 s). | `g2test.py CD-02 CD-06 CD-07`: as três grades ordenam, abrem consulta ou formulário e respondem ao teclado. |
| `cadc_test`; `ap_unico_nav`, `cafe_apurar_nav`, `dose_divergente_nav` | São índice ou módulo chamado pelo `*_test` correspondente; rodados sozinhos, não verificam nada. | Os `*_test` que os chamam estão verdes: `ap_unico` 23/23, `cafe_apurar` 10/10, `dose_divergente` 22/22. |
| `saf_capacidade_simetrica_test` | Uma execução sob carga (4 testes e 2 varreduras em paralelo) falhou 2 de 38 com a página ainda não montada (`{{v3_ver}}`). | Repetido em seguida: 38/38. Na bateria: 38/38. Fica registrado como sensível a carga, sem tolerância nova. |

## 4. Vermelhos antigos (falham igual na v57; não são regressão da v58)

| Teste | Resultado na v58 e na v57 | Classe provável | Frente |
|---|---|---|---|
| `consumo_divergente_test` | rc=1 nas duas | a diagnosticar: teste obsoleto ou exibição perdida | tarefa #80 |
| `os_cenario_test` | 21/22 nas duas ("A liberar sem revisão…") | a diagnosticar | backlog de base verde |
| `ostest` | 32/33 nas duas (painel da nova ordem A liberar) | mesma família do `os_cenario` | backlog de base verde |
| `intest`, `psfix38test`, `saf38test`, `saftest` | rc=1 nas duas | testes das telas v38, anteriores à etapa única do Planejar safra | backlog de base verde |
| `testes_pedido` (T01, T02, T05: seis etapas da safra) | falham nas duas, com saída 0 | obsoleto: a safra tem 4 etapas desde a etapa única | backlog de base verde |
| `agrofit_test` | 17/18 nas duas, com saída 0 (cabeçalho da base) | a diagnosticar | backlog de base verde |
| `getest` | GE-04 nas duas, com saída 0 | a diagnosticar | backlog de base verde |
| `vetest` | "OF-103 editada" nas duas, com saída 0 | a diagnosticar | backlog de base verde |
| `cotest` | 41/53 nas duas, com saída 0 | a diagnosticar | backlog de base verde |
| `ben_fluxo_test` | 2/13 nas duas | Beneficiamento fora da navegação até a rodada 3 (decisão vigente) | BEN rodada 3 |

Nenhum dos vermelhos antigos toca o que a v58 muda: inteligência comercial, etapas 2 e 3 do Planejar safra, menu Manutenção, TABR-CTX-02 e o núcleo CONTROLE-02, que fica dormente. Ficam na fila de base verde (AGENTS §3.6), um por vez.

## 5. Reexecução depois das correções (mesma candidata, executada em 13/10)
| Teste | Bateria | Depois |
|---|---|---|
| `cafe_apurar_test` | 1/10 falhou | 16/16 e 10/10 |
| `config_test` | tempo esgotado | 88/88 |
| `dose_divergente_test` | 2/2 (parou no meio) | 22/22 |
| `ma_unica_test` | 22/23 | 23/23 |
| `ma_planos_test` | 18/18 com saída 1 | 18/18 |
| `quantidade_test` | saída 1 | 14/14 |
| `tabelas_cad_test` | 201/206 | 206/206 |
| `conferencia_diaria_test`, `_nav` e `_casos_nav` | sem `--output` | 30/30; JSON do `_nav` 16/16 e do `_casos_nav` 14/14 |
| `saf_totais_test` (novo) | — | 11/11; na montagem anterior, reprova |
