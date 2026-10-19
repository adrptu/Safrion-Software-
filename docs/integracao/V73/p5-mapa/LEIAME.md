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
