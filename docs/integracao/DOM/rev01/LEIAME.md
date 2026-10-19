# DOM-REV-20261009-01 · rascunho do outro dia preservado (S3)

Achado do Codex em 6091211425: com dois dias divergentes na mesma O.S., confirmar a revisão do dia 1 apagava o texto já escrito do dia 2 (`dvGo` passava `{dvr:null}` ao `osRun`).

- Candidata: `c764de9` (branch local `claude/v44-dom`), filho de `1fd8cfa`. Para reproduzir: `git am rev01/0001-*.patch` depois de `git am patches/*.patch` sobre `ecc8b00`; ou `git apply rev01/diff-1fd8cfa-c764de9.patch` sobre `1fd8cfa`.
- Mudança (2 arquivos, +30 −2):
  - `areas/processo_os.py`: `dvGo` remove só o rascunho do dia confirmado; erro e repetição continuam guardando o texto (o `dvSet` de erro já preservava). Depois de gravar, o foco vai ao campo do próximo dia ainda em revisão.
  - `dose_divergente_nav.py`: seção 10, pelo teclado. Dias 25/09 e 26/09 divergentes, os dois motivos digitados (`Input.insertText` e Tab), Enter em "Aceitar com motivo" do dia 1. Confere que só o dia 1 grava, que o texto do dia 2 continua no campo e que o foco vai para ele. Depois, Tab até "Registrar correção" do dia 2 e Enter, que grava exatamente o rascunho preservado.
- Motor, precisão e regras não mudaram. A bateria inteira não foi repetida (pedido do Codex).

| Prova (executada pelo Claude, Chrome headless e Node, dados sintéticos) | Código | Resultado | Bruto |
|---|---|---|---|
| `python3 dose_divergente_test.py nav` | `1fd8cfa` com o teste novo | rc=1: as duas asserções novas FALHAM (texto do dia 2 `''`, foco perdido); as 19 anteriores passam | `brutos/nav-orig.log` |
| `python3 dose_divergente_test.py nav` | `c764de9` | rc=0, 21/21 | `brutos/nav-fix.log` |
| `python3 dose_divergente_test.py unit` | `c764de9` | dose 35/35, Início 2/2 | `brutos/unit-fix.log` |
| `build.py` e `montar_render.py` | os dois | rc=0, 0 FALHA | `brutos/build-*.log` |
