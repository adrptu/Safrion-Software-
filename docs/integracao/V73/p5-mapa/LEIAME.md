# Mapa: produtividade na unidade escolhida (P5) e rótulo sem corte (MUX-CORTE), 19/10/2026

**Autoria:** Claude. **Revisão e integração:** Codex. **Base:** composição `5bc0b340` (v143 + PR #132). A bateria abaixo rodou sobre `d37e56e4`; os seis testes mais próximos foram repetidos sobre `5bc0b340` (`logs/composicao_5bc0b340/`): `mapa_rotulo_corte` 4/4, `producao_fluxo unid` 25/25, `colheita_mapa` 7/7, `irr_fluxo` 34/34, `mapa_mux_f2` 29/29 e `config` 90/90.

## Resultado útil
O gestor escolhe kg/ha (ou sc/ha, t/ha) para o Mamão na Previsão e colheita, abre o Mapa na camada "Colheita e produtividade" e lê, no pivô, a mesma produtividade e a mesma unidade da tabela.

Em todas as camadas, o rótulo do pivô mostra o valor inteiro: número, unidade e estado.

## Dano evitado
- **P5 (UNID-PROD, último vermelho da base verde do `producao_fluxo`):** o rótulo mostrava a **produção** em t ("48,47 t"), outra grandeza. A Previsão e colheita mostrava a produtividade na unidade escolhida. O gestor comparava talhões de áreas diferentes por um número que não era produtividade. Severidade S3.
- **MUX-CORTE:** o valor ficava numa linha com reticências, e 34 rótulos saíam cortados a 1440 px. Exemplos:
  - "Ácaro-rajado 18 % folhas com ác…"
  - "OS-0502 calagem · falta calcá…"
  - "em colheita · 484,89 k…"

  O número ou a unidade sumiam no mapa de decisão. Severidade S3: o painel do talhão tem o valor inteiro.

## Mudança (`areas/inicio.py`)
- **`colhNum`:** usa `prPrtvResTxt(cultura, R, g2unidPref(cultura))`, a mesma função do painel do talhão e da Previsão e colheita (ENG-011, sem cópia da conta). Antes de começar a colheita, segue a previsão.
- **Rótulo do pivô (fonte comum MUX-F2, vale para as 9 camadas):**
  - o valor ocupa até 3 linhas, e as reticências só aparecem depois da 3ª;
  - `muxQuebra` prende o "·" à palavra anterior (nenhuma linha começa com "·"), o número à unidade, e mantém inteiro o trecho de até 20 caracteres. A 2ª linha começa num trecho.
- **Sem mudança:** o nome acessível, o cartão, a Lista e o `data-rotulo` da Santa Rita continuam com o texto completo de antes.

## Testes executados (render sintético deste commit, Chrome)

| Teste | Resultado |
|---|---|
| `mapa_rotulo_corte` (novo). R1 1440 px e R2 390 px: 9 camadas sem valor cortado (largura nem altura) e sem "·" solto; R3 Pivô 19 "em colheita · 484,89 kg/ha"; R4 sem erro de JS | 4/4 |
| Contraprova: `mapa_rotulo_corte` no render da v143 | 1/4. Reprova R1 (cortes em Integrado, Pragas, O.S., Irrigação e Estádio), R2 e R3 ("em colheita · 36,42 t") |
| `producao_fluxo` completo, só com o P5 | 93/93 (antes 92/93: o AC-h Mapa era o vermelho) |
| `producao_fluxo unid`, com P5 + MUX-CORTE | 25/25 |
| Contraprova: `producao_fluxo unid` no render da v143 | 24/25. Reprova o AC-h Mapa: o rótulo era "48,47 t" |

**Testes do Mapa, com P5 + MUX-CORTE:**

| Teste | Resultado |
|---|---|
| `carencia` | 90/90 |
| `colheita_mapa` | 7/7 |
| `map_decisoes` | 18/18 |
| `map_irrig_filtro` | 15/15 |
| `map_trilha_icones` | 9/9 |
| `mapa9` | 13/13 |
| `mapa_cancel` | 6/6 |
| `mapa_faixa` | 25/25 |
| `mapa_filtros` | 7/7 |
| `mapa_mux_f0` | 17/17 |
| `mapa_mux_f1` | 43/43 |
| `mapa_mux_f2` | 29/29 |
| `mapa_solo_texto` | 9/9 |
| `mip_correcoes` | 14/14 |
| `mip_fluxo` | 15/15 |
| `solo_mapa_calor` | 9/9 |
| `talmapa` | 8/8 |
| `demanda_estado_nav` | 14/14 |
| `demanda_unica_nav` | 29/29 |
| `est_laudo_lote_nav` | 7/7 |
| `map_aprov` | 5/5 |
| `irr_fluxo` | 34/34, depois da correção abaixo |

## Base verde: `irr_fluxo` (vermelho antigo, achado nesta bateria)
- **Sintoma:** a falha 19 contava 24 linhas na IR-01 da Lagoa Grande, quando o esperado é 23 pivôs.
- **Não vem desta mudança:** o render limpo da v143 dá o mesmo 33/34 (`logs/irr_fluxo_v143_antes.log`).
- **Causa medida:** a IR-01 tem duas tabelas, `g_set` (setores) e `g_agua` (Água no solo, AGUA-SOLO-IRR de 18/10). O teste contava as linhas da tela inteira, e a medição AGS-003 do Pivô 2 virava a 24ª. Teste obsoleto na forma de contar; o produto está certo.
- **Correção:**
  - a contagem fica só em `g_set`, e a asserção de 23 pivôs não muda;
  - o teste passa a sair com código 1 quando falha. Antes saía com 0 e escondia o vermelho de quem lê só o código de saída.

## Fotos conferidas (`fotos/`)
- **`antes_colheita_kgha_1440`:** P19 "em colheita · 484,89 k…", cortado.
- **`depois_colheita_1440`:** P19 "em colheita ·" / "484,89 kg/ha".
- **`depois_pragas_1440`:** os nomes do MIP em até 3 linhas, sem corte, e nenhum rótulo sobre o vizinho.
- **`depois_integrado_1440`:** as O.S. em 2 linhas.
- **`depois_colheita_390`:** a 390 px o rótulo segue só com o número do pivô (tamanho pequeno), sem rolagem lateral.

## Revisão do Codex no HEAD 77544fe2 (6262164118 e 4311323857): achado S3 aceito e corrigido
- **Achado:** o `split(' · ')[0]` em `colhNum` jogava fora as qualificações obrigatórias do `prPrtvResTxt`:
  - "· estimativa" (R-U03);
  - no café a apurar, a produtividade medida do campo (R-U07). A Previsão e colheita mostra "kg/ha a apurar · 1.200,00 kg/ha de Café da roça", e o Mapa mostrava só "kg/ha a apurar".
- **Correção:**
  - o rótulo leva o indicador inteiro, e o nome acessível também (vem do mesmo texto);
  - o rótulo em até 3 linhas (MUX-CORTE) comporta o texto.
- **Regressão:** `mapa_colheita_unid_unit_test.py` (novo), no node, com as regras reais (`cenario.js_prefixo()`) e o `colhNum` extraído do gerador:

| Caso | O que confere |
|---|---|
| C1 | Mamão estimado em kg/ha |
| C2 | Café a apurar em kg/ha |
| C3 | Mamão medido na unidade padrão |
| C4 | A mesma função do painel do talhão |

| Execução | Resultado |
|---|---|
| Com a correção | 6/6 |
| Contraprova com o `inicio.py` do 77544fe2 | 4/6 (C1 e C2 reprovam, com os mesmos textos do achado) |

Depois da correção, no render (`logs/revisao_codex/`):

| Teste | Resultado |
|---|---|
| `mapa_rotulo_corte` | 4/4 |
| `producao_fluxo unid` | 25/25 |
| `colheita_mapa` | 7/7 |
| `mapa_mux_f0` | 17/17 |
| `mapa_mux_f1` | 43/43 |
| `mapa_mux_f2` | 29/29 |
| `map_decisoes` | 18/18 |

## Revisão do app do Codex no HEAD 4bc5a634 (4311564651): o rótulo composto do café cabe inteiro
- **Achado:** "em colheita · kg/ha a apurar · 1.200,00 kg/ha de Café da roça" precisa de 4 linhas, e o limite de 3 cortava "Café da roça". O C2 só testava o texto, não o rótulo.
- **Correção:**
  - o limite passa a 4 linhas;
  - `MUX.quebra` fica exposto para inspeção nos testes, como o `window.__MUX` que já existia.
- **Regressão:** R5 no `mapa_rotulo_corte`. Com o Pivô 19 a 1440 px, passa pela mesma quebra os dois textos compostos mais longos e confere que não há corte:
  - o café a apurar com a medida do campo, mais "+1";
  - a estimativa, mais "+1".

| Execução | Resultado |
|---|---|
| `mapa_rotulo_corte` com 4 linhas | 5/5 |
| Contraprova com 3 linhas, no mesmo render | 4/5 (R5 reprova) |
| `producao_fluxo unid` | 25/25 |
| `colheita_mapa` | 7/7 |
| `mapa_mux_f0` | 17/17 |
| `mapa_mux_f1` | 43/43 |
| `mapa_mux_f2` | 29/29 |
| `map_decisoes` | 18/18 |
| `mapa_colheita_unid_unit` | 6/6 |

Brutos em `logs/revisao_codex_2/`.

## Prova pedida pelo Codex na revisão 5569013634 (HEAD 8eef6ace): rótulo composto pela cadeia real, a 1440 e a 390 px
**Pedido:** o R5 roda só a 1440 e injeta o texto no rótulo. Faltava provar os compostos pela cadeia real, nas duas larguras, com o nome acessível e sem sobreposição. Não há defeito novo.

**`mapa_rotulo_real_test.py` (novo):**
- **Cadeia real:** carga recebida → `prProdOS` (modo da participação) → `prResultado` → `colhNum` → `MUX.info` → marcador do MapLibre (rótulo e nome acessível).
- **Estado sintético:** gravado no armazenamento local. A CD-04 grava a fonte pela tela, no calendário do Comercial, que não toca o Mapa. As 3 origens do Pivô 19 nas cargas recebidas passam a "estimada" (COLH R-06), como o formulário de carga grava. O Mamão fica em kg/ha (Ana).
- **E1 e E2 (1440 e 390):** o Pivô 19 mostra "em colheita · 484,89 kg/ha · estimativa", inteiro, antes e depois de selecionar o pivô.
- **E3:** o nome acessível traz o mesmo indicador: "P19, 75 ha, Mamão Formosa Tainung 1 · produção, em colheita · 484,89 kg/ha · estimativa, dado de 23/09 (hoje)".
- **E4:** o rótulo, dentro da tela, não se sobrepõe a outro rótulo, antes e depois de selecionar.
- **E5, sonda de texto e não cadeia real:**
  - **Por que é sonda:** o cenário sintético não tem café em talhão do Mapa. O único café é o C1 da Santa Rita, sem geometria.
  - **O que mede:** os compostos do café a apurar com a medida do campo e da estimativa, pela mesma quebra (`MUX.quebra`), cabem a 1440 e a 390.
- **E6:** sem erro de JS.

| Execução | Resultado |
|---|---|
| Render do PR (8eef6ace) | 6/6 |
| Contraprova no render da v143 | 2/6 |

**A contraprova reprova E1, E2, E3 e E5:**
- O rótulo mostrava a produção, "em colheita · 36,42 t", e o nome acessível também.
- Sem a quebra da MUX, o café composto é cortado.
- **Ressalva:** na v143 ainda não existe a fonte de pessoas da CD-04, que veio com o PR #132. Por isso o estado da estimativa nem chega a ser gravado ali ("sem estado" no bruto). A reprovação vem do rótulo em t.

**Observação fora do escopo do P5:** a 390 px o Pivô 19 abre fora da área do mapa, e selecioná-lo pelo teclado (Tab e Enter) abre o painel sem mover o mapa até ele. O teste centraliza o mapa no pivô, como a pessoa faria ao arrastar. Fica registrado para a frente do Mapa (MUX-F1), sem mudança neste PR.

**Fotos:** `fotos/p19_estimativa_1440.png` e `fotos/p19_estimativa_390.png`, o rótulo real com "estimativa" em 3 linhas.

**Brutos:** `logs/revisao_codex_3/`.
