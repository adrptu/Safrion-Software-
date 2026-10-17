# Revisão e integração do PR #99 (BASE-QTD) pelo Claude

- **Autor:** Codex. **Revisor e integrador:** Claude.
- **Composição:** `666dacb` = `4fd5b8b` + merge do HEAD `24a632a`, sem conflito.
- **Escopo:** só teste. Muda apenas `quantidade_test.py` e os documentos em `docs/integracao/V73/BASE-QTD/`.
- **Diagnóstico do Codex, conferido:** o teste antigo terminava a irrigação logo depois de iniciar e sem medição. A trava "Antes do fim previsto" abortava a bateria (`teste_antigo.log`: rc=1).

## O que muda no teste

- A fixture `terminarNoFim` avança o relógio sintético até o fim previsto e informa uma leitura sintética de hidrômetro. O comando do produto não muda.
- A verificação **15** prova que terminar cedo, ou sem medição, é recusado sem alterar o estado.
- A varredura **10** ganha `EXC_LINHAS`: 5 linhas exatas nomeadas como exceção. Uma linha nova, ou uma dessas linhas alterada, volta a reprovar.

## Execução Claude

Executado no gen37 com dados sintéticos; a coluna **Log** dá o arquivo bruto nesta pasta.

| Caso | Log | Resultado |
|---|---|---|
| Teste do PR sobre `4fd5b8b` + #96 + #97 (árvore de revisão) | `candidata.log` | 15/15 |
| Teste do PR na composição `666dacb` | `composicao.log` | 15/15 |
| Teste antigo (`613bda6`) na mesma árvore | `teste_antigo.log` | rc=1: aborta |
| M1: sem a trava "Antes do fim previsto" (`irrigacao_estado.js:462`) | `mut_tempo.log` | 14/15: reprova na 15 |
| M2: `x.dose*area` numa função nova em `cenario.js` | `mut_nova.log` | 14/15: reprova na 10 |
| M3: uma linha da exceção alterada (`custo_dominio.py`, `x.dose*p*1`) | `mut_linha.log` | 14/15: reprova na 10 |

Os arquivos do produto foram restaurados depois de cada mutante.

## Achado que não bloqueia

**A1 · S3 · dívida de ENG-011.** Três das linhas da exceção calculam a quantidade de produto por carga do tanque com `dose × área` direto, sem passar pela regra única `cenQtd` (`cenario.js:56`):
- `cenario.js:117`: `q:x.dose*ha`;
- `cenario.js:119`: `q:x.dose*haCarga`;
- `cenario.js:916`: `q:x.dose*vol/a.f.volumeHa`.

Elas só servem à prévia da calda e não baixam custódia, mas o arredondamento pode divergir do que é reservado.

**Proposta:** levar as três para `cenQtd` numa fatia própria e tirá-las de `EXC_LINHAS`. Hoje a exceção registra a dívida e não a esconde: qualquer mudança nessas linhas reprova.
