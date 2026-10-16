# `ds_test.py` de 69/72 para 72/72 (base verde, VEL §3.6)

| Item | Valor |
|---|---|
| Base | `1639ab3` (claude/v44-v69-mapa); `base_1639ab3_completo.log`: **FALHOU 69/72** (D13, D15, E2) |
| Correção | `5e5e62d`, render de árvore limpa (worktree destacada), dados sintéticos |
| Comando | `env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B ds_test.py` (`DS_RENDER=<render>`, `DS_PARTES=D` ou `E` nas contraprovas) |
| Normal | `normal_5e5e62d.log`: **OK 72/72**, rc=0 |

## Classificação

| Falha | Classe | Causa | O que mudou |
|---|---|---|---|
| D13 | **Defeito do produto** (S3 no protótipo: a pessoa consegue ver o bloqueio abrindo o painel) | Desde a VISOES-2 V2-1 (14/10), o selo da lista da O.S. é o ícone de situação antes do código: um `span role=img` com `data-dica` e sem borda arredondada. O `g2lib.g2dicaSelo` só procurava `[data-dica-de]` e chips com `border-radius`. Com Tab na OS-0418, bloqueada por falta de insumo, a dica mostrada era a da fase: "A liberar… Próximo passo: liberar". | O `g2dicaSelo` passa a incluir `span[role=img][data-dica]`, e a dica no foco fica igual à do hover (D10): "Situação: Falta insumo · Ureia 45% — …". O oráculo aceita o rótulo "Situação:" antes do nome do selo, e o resto continua igual (o que falta, quem resolve, `aria-describedby`). A regra entrou em `docs/design-system/separador-hover-retorno-dica.md` §4. |
| D15 | **Teste obsoleto** (a VISOES-2 V2-1 mudou a apresentação, e o teste não acompanhou) | O selo amarelo "Sobras a receber" virou ícone sem texto. A dica dele é "Situação: Sobras a receber — Encerrar bloqueado: …". O seletor `[data-dica^="Encerrar bloqueado"]` não achava nada, o `hover(None)` não fazia nada, e o teste lia a dica que estivesse aberta ("Ver em tabela"). | O teste acha o ícone pela dica do bloqueio e reprova se não o encontrar. Confere o nome do selo e o mesmo texto do bloqueio que aparece no painel, com quem resolve (Rui, almoxarife). |
| E2 | **Teste obsoleto** (VISOES-2 V2-1: no celular, `g2colsVis` mostra só as 3 primeiras colunas do padrão) | A 390 px, a linha mostra O.S., Atividade e Talhão; a Fase não aparece nela. O "aviso duplicado" da coleta é o par aviso visível (`aria-live=off`) + região viva. Esse par é o desenho previsto (C9) e não causou a reprovação: o teste reprovou porque a fase não estava na linha. | O teste confere o que a pessoa vê: o painel da ordem (aberto por cima da lista) com a fase atual "Liberadas", os chips de fase (A liberar −1, Liberadas +1), o realce e o anúncio. |

Nenhuma falha veio da ferramenta. Uma fragilidade do teste fazia o D15 mostrar a mensagem errada: seletor vazio sem reprovação explícita. Isso foi corrigido junto.

## Contraprovas (a versão com defeito reprova)

| Execução | Render | Resultado | Item que reprova |
|---|---|---|---|
| `base_1639ab3_D.log` | base sem a correção | FALHOU 17/18, rc=1 | só o D13: a dica é "A liberar: …" |
| `base_1639ab3_E.log` | base sem a correção | OK 5/5, rc=0 | nenhum: no E2 o produto já estava certo |
| `mutante_d15_D.log` | `m_d15` | FALHOU 17/18, rc=1 | só o D15: o selo não tem a dica do bloqueio |
| `mutante_e2_E.log` | `m_e2` | FALHOU 4/5, rc=1 | só o E2: painel em "A liberar" e chips sem mudança, com o aviso "liberada" |

Os mutantes são feitos por `mutantes.py`, numa cópia do render do `5e5e62d`, trocando uma linha do `OS.dc.html`. O código do produto não muda.
- **`m_d15`:** o ícone de situação usa a dica genérica do dicionário em vez da do bloqueio do encerramento (`osSeloDica`). É o defeito do achado 6 da revisão DS.
- **`m_e2`:** a liberação reserva e avisa "liberada", mas a ordem fica em A liberar.

sha256 do `OS.dc.html`:
- normal: `091c871dc5f70c23d55a68665640079e905b74b569368b2b2a19f8c932e8c333`
- `m_d15`: `882db76c854bd159d7a74c7cdadba2161a345dca24d68f351148c890c62a5c4d`
- `m_e2`: `fb8583e2ed86332a78eed33c41d0efadd5d9d468151553b2aefa9875a274b5ee`

## Demais testes do módulo (render do `5e5e62d`)

| Teste | Resultado (rc) | Bruto |
|---|---|---|
| `ds_unit_test.py` | OK 44/44 e 31/31 (0) | `ds_unit_5e5e62d.log` |
| `ds_padrao_test.py` | 17 ok · 0 falhas (0) | `ds_padrao_test_5e5e62d.log` |
| `ds_1510_test.py` | 17 ok · 0 falhas (0) | `ds_1510_test_5e5e62d.log` |
| `ds_1610_test.py` | 14 ok · 0 falhas (0) | `ds_1610_test_5e5e62d.log` |
| `visoes_test.py` (dica dos ícones de visão) | 9 ok · 0 falhas (0) | `visoes_test_5e5e62d.log` |
| `regras_toque_test.py` (dica no toque) | 5 ok · 0 falhas (0) | `regras_toque_test_5e5e62d.log` |

## Composição com a ponta nova da base (VEL §3.6)

A base andou de `1639ab3` para `b87f79b`: 10 commits, nenhum em `g2lib.js`, `ds_test.py`, `engine.py` ou `processo_os.py`. O merge gerou `f8d0d40`. Repeti no render de árvore limpa desse commit:

| Execução | Resultado (rc) | Bruto |
|---|---|---|
| `ds_test.py` | OK 72/72 (0) | `normal_f8d0d40.log` |
| `m_d15`, parte D | FALHOU 17/18, só o D15 (1) | `mutante_d15_D_f8d0d40.log` |
| `m_e2`, parte E | FALHOU 4/5, só o E2 (1) | `mutante_e2_E_f8d0d40.log` |
| `ds_unit_test.py` | OK 44/44 e 31/31 (0) | `ds_unit_f8d0d40.log` |

sha256 do `OS.dc.html` no `f8d0d40`:
- normal: `6425bb3c5d939169fc48a6881bd0852df84f053b7911370657227b10ebd66a57`
- `m_d15`: `fafa346be11f8d3cbf87650df4619b818926a18853bbea3e22022cf2afcec839`
- `m_e2`: `8fa8ef43c8ccf6420333234a08e2ce66052f17a5429b7c95564fcd8df15cb969`

## Composição com a base em `052b9bf`

A base andou de `b87f79b` para `052b9bf`: 10 commits, entre eles a frente CADASTROS-PADRÃO. No `ds_test.py`, ela mexeu só no B6. O merge gerou `d0eb3a8`, sem conflito. O `OS.dc.html` tem o mesmo sha256 do `f8d0d40`. Repeti no render de árvore limpa:

| Execução | Resultado (rc) | Bruto |
|---|---|---|
| `ds_test.py` | OK 72/72 (0) | `normal_d0eb3a8.log` |
| `m_d15`, parte D | FALHOU 17/18, só o D15 (1) | `mutante_d15_D_d0eb3a8.log` |
| `m_e2`, parte E | FALHOU 4/5, só o E2 (1) | `mutante_e2_E_d0eb3a8.log` |
| `ds_unit_test.py` | OK 44/44 e 31/31 (0) | `ds_unit_d0eb3a8.log` |

## Composição com a base em `6733a4c` (PR #76 integrado)

A base andou de `052b9bf` para `6733a4c` e agora inclui o PR #76, que muda o cartão do `engine.section()`. O merge gerou `d61bb58`, sem conflito. O `OS.dc.html` continua com o mesmo sha256. Repeti no render de árvore limpa:

| Execução | Resultado (rc) | Bruto |
|---|---|---|
| `ds_test.py` | OK 72/72 (0) | `normal_d61bb58.log` |
| `m_d15`, parte D | FALHOU 17/18, só o D15 (1) | `mutante_d15_D_d61bb58.log` |
| `m_e2`, parte E | FALHOU 4/5, só o E2 (1) | `mutante_e2_E_d61bb58.log` |
| `ds_unit_test.py` | OK 44/44 e 31/31 (0) | `ds_unit_d61bb58.log` |
