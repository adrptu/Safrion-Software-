# V55 · RESP-01, partest T1-C e COMP-02 (executado)

- **Base:** `a3b4dab` (candidata v55, `claude/prototipo-v44`), numa cópia local (`git worktree add --detach … a3b4dab`).
- **Branch local:** `int/v55b`. Sem push, sem PR, sem publicação.
- **Commits:**

  | Item | Commit |
  |---|---|
  | V55-RESP-01 | `7b96881` |
  | partest T1-C | `7efc2b9` |
  | V55-COMP-02 | `2310aad` |
  | este pacote | o commit que traz este arquivo |

- **Ambiente:** Chrome headless 141 com emulação (largura × altura em px CSS, escala, toque). Não é aparelho físico. Dados sintéticos (`SAFRION_DADOS=sintetico`).
- **Navegador:** um teste por vez, com a trava `/tmp/cdpV55B.lock`.
- **Qualificação do Codex 6096401790:** atendida.
  - O aviso real fica na tela em todas as medidas. Nada espera ele sumir, nada o esconde.
  - A folga vem da altura medida do aviso, não de um número fixo.
  - O `env(safe-area-inset-bottom)` foi medido com 34 px.
  - O aviso mais longo da etapa 2 foi medido.

## 1. V55-RESP-01 (impeditivo)

### Diagnóstico, com geometria (a3b4dab)
Cenário: Planejar safra, etapa 2 (`SAF.dc.html#saf=S2627&etapa=2`), a 360×800 com a busca focada. A janela é reduzida a 360×420 para simular o teclado virtual aberto.
- **Viewport:** `visualViewport` 360×420, escala 1, `offsetTop` 0. É igual ao viewport de layout: o teclado não sobrepõe o conteúdo.
- **Rolagem:** quem rola é a casca (`.ml-tog+div`, `overflow-y:auto`, 420 px). O `main` tem a altura do conteúdo e não rola.
- **Área de ações:** fica em fluxo (`position:static`, pela regra `@media (max-height:560px)`), no fim do conteúdo.
- **Aviso real "Safra aberta: Safra 2026/27 · Cultivos e planos":**
  - é um `div[role=status]` fixo a `22px + --acoes-h + safe-area` do pé;
  - tem só 180 px de largura: o `left:50%` limita a caixa a meia janela;
  - por isso quebra em 3 linhas, com 76 px de altura (y 322–398).
- **Depois de `scrollIntoView({block:'center'})` em "Dimensionar operações ›":**
  - o botão fica em y 304–348;
  - `elementFromPoint` no centro (214, 326) devolve `div[role=status]`. A pilha é aviso › span › `button[data-acao=avancar]`;
  - o toque real (`Input.dispatchTouchEvent`) cai no aviso, e a etapa continua 2.
- **No fim da rolagem:** o centro de "Dimensionar operações ›" e o de "Aplicar plano em 4 cultivos" ficam sob o aviso.
- **Pelo teclado:**
  - 73 Tabs chegam ao botão, mas o aviso fica sobre o botão focado;
  - Enter avança, porque a tecla não passa pelo aviso;
  - a busca ("T") e a tabela de cultivos e planos (o rascunho da safra) ficam iguais.
- **Aviso mais longo da etapa 2** ("Aplicar plano em 4 cultivos" com a P2 em sobreposição, 345 caracteres):
  - em 180 px de largura dá 17 linhas e 328 px de altura;
  - ocupa 350 de 420 px a partir do pé;
  - o toque no avanço falha, e todos os controles da área ficam sob o aviso.
- **Com `safe-area-inset-bottom` de 34 px:** o aviso sobe 34 px, e o defeito se repete.
- **Controle, 390×844 e 1440×900:** a área é presa (`sticky`) e o aviso sobe acima dela (`--acoes-h`). O toque e Tab+Enter avançam.

Os dados estão em `antes/sonda.log`, `antes/sonda_geometria.json` e `antes/cap_360x420_*`.

### Correção (commit `7b96881`)
- **`tools/prototipo/v37/gen37/engine.py:1469-1471` (G2_TOAST):**
  - acrescenta `width: max-content`, com o `max-width` de antes, `min(560px, 100vw − 32px)`;
  - o aviso passa a usar a largura do texto: 316 px a 360 px;
  - o de 47 caracteres fica em 1 linha (40 px) e o de 345 em 8 linhas (166 px);
  - vale para o aviso de todas as telas.
- **`tools/prototipo/v37/gen37/g2lib.js:291-297` (`g2avisoH`):**
  - `--aviso-h` recebe a altura real do aviso fixo no pé que está visível, ou 0 sem aviso;
  - a medida não depende da altura da janela;
  - é chamada na troca do aviso (`componentDidUpdate`, `engine.py:1451`) e no quadro do g2glob (`g2lib.js:331`).
- **`tools/prototipo/v37/gen37/engine.py:1049` e `1066-1073` (ACOES_CSS, `@media (max-height:560px)`):**
  - `--acoes-h:0 !important`: com a área em fluxo, o aviso vai ao pé já no layout, sem esperar o quadro do g2lib;
  - a área reserva `calc(AVISO_PE + env(safe-area-inset-bottom) + var(--aviso-h) + 8px)` em dois lugares: na margem de baixo (fim da rolagem) e na margem de rolagem dos controles (`scrollIntoView`, foco por Tab);
  - `AVISO_PE = '22px'` é a mesma constante do G2_TOAST;
  - substitui os 82/106 px fixos do rascunho anterior.

### Provas (depois; `depois/sonda.log`, `depois/sonda_geometria.json`, `depois/cap_*`)
Em todas as linhas, o aviso real está na tela no toque e no Enter.

| Dimensão · aviso | Aviso (linhas · altura) | Reserva | Centro do botão depois de rolar | Toque | Fim da rolagem: controle sob o aviso | Tab → foco → Enter | Busca e rascunho |
|---|---|---|---|---|---|---|---|
| 360×420 · carga | 1 · 40 px | 70 px | o botão | 2 → 3 | nenhum | 73 Tabs, foco no avanço e livre, 2 → 3 | iguais |
| 360×420 · longo | 8 · 166 px | 196 px | o botão | 2 → 3 | nenhum | 74, livre, 2 → 3 | iguais |
| 360×420 + safe-area 34 · carga | 1 · 40 px | 104 px | o botão | 2 → 3 | nenhum | 73, livre, 2 → 3 | iguais |
| 360×420 + safe-area 34 · longo | 8 · 166 px | 230 px | o botão | 2 → 3 | nenhum (¹) | 74, livre, 2 → 3 | iguais |
| 390×844 · carga e longo (controle) | 1 e 8 | área presa | o botão | 2 → 3 | nenhum | livre, 2 → 3 | iguais |
| 1440×900 · carga e longo (controle) | 1 e 5 | área presa | o botão | 2 → 3 | nenhum | 98–99 Tabs, livre, 2 → 3 | iguais |

(¹) Com o aviso longo e a safe-area de 34 px, sobram 198 px acima do aviso, menos que a área (244 px) somada à faixa de etapas presa no topo.
- No fim da rolagem, "Mudar plantio de P2 ›" fica sob a faixa de etapas, não sob o aviso.
- Cada controle levado à vista (`scrollIntoView` nearest, como o foco por Tab) fica livre: campo `alcance`.

### Caso 17: oráculo do progresso renderizado (`acao_unica_test.py:245-269`)
- **Erro do oráculo antigo:** ele exigia "Etapa i de n" sempre que a janela tinha até 800 px.
- **Como a faixa realmente decide:** por container query sobre a largura dela (`ui37.py:100`, `_ETP_LIM`).
  - SAF, 4 etapas: fica compacta abaixo de 640 px;
  - CMP, 6 etapas: fica compacta abaixo de 900 px.
- **Medida no Chrome:**
  - a 800×360 e a 768×1024, a faixa do SAF tem 732 e 700 px: mostra a lista inteira das 4 etapas, com a atual "4 Confira a demanda de insumos" visível e livre;
  - a CMP mostra a faixa compacta "Etapa 3 de 6 · Solicite cotações";
  - o contexto ("Safra 2026/27") fica visível e livre.
- **O que o oráculo novo segue:** o modo realmente renderizado.
  - Compacta: o texto "Etapa i de n · Nome" visível e livre.
  - Lista: as n etapas inteiras, dentro da faixa e da janela, sem sobreposição, e a atual visível e livre.
  - Nos dois modos, o contexto visível e livre.
- **Asserções:** nenhuma foi removida. Alcance, última linha, foco, rolagem lateral, um avanço só e aviso sobre a área presa continuam.
- **Asserções novas:**
  - o aviso não fica sobre um controle da área no fim da rolagem;
  - a medida espera dois quadros pintados.
- **Evidência:** `depois/caso17_18/acao_{saf,cmp}_{800x360,768x1024}_progresso.png` e o "progresso por dimensão" em `depois/acao_unica_responsivo.log`.
- **Endereço:** passou de `etapa=6` para `passo=demanda`. É o endereço canônico da mesma etapa: `etapa=N` antigo é lido na numeração de 6, e 6 vira 4.

### Proteção de regressão: 18b e 18c (`acao_unica_test.py:286-313`)
- **18b:** aviso de carga.
- **18c:** aviso mais longo, com safe-area de 34 px.
- **O que os dois verificam:**
  - nenhum controle da área fica sob o aviso no fim da rolagem;
  - cada controle levado à vista fica livre;
  - o toque real no centro de "Dimensionar operações ›", depois de rolar e com o aviso ainda na tela, leva da etapa 2 à 3.

## 2. partest T1-C (commit `7efc2b9`)
- **Oráculo vencido:** `safra.js` (divVals) produz "1 ajuste deste talhão · copiado de T1-B", e o `partest.py:90` esperava "1 ajuste · copiado de T1-B". Corrigido em `partest.py:90-92`.
- **Conferência nova no navegador (`partest.py:96-116`)**, depois de salvar o T1 em 27 parcelas:
  - o T1-C salvo tem, no painel "Insumos e doses", o mesmo produto (Fungicida A) e a mesma dose 0,6 do T1-B (padrão 0,50 L/ha);
  - editar a cópia para 0,75 grava só no T1-C ("1 dose alterada em T1-C");
  - o original (T1-B) continua 0,6.
- **Mutante:** no `_render` sem a cópia do ajuste ao salvar (`safra.js` dvSave), a conferência nova falha. Resultado: 49 ok · 1 falha (`logs/mutante_partest.log`).

## 3. V55-COMP-02 (S3, commit `2310aad`)

### Diagnóstico
`osManCond` é chamado por último em `osMerge`. Com a máquina apta, ele trocava o dono e o prazo já calculados pelo padrão: "PCP · reprogramar antes de liberar" em A liberar e o dono da fase depois.

Medido em a3b4dab, com o preparador do Codex:
- **Caso A, OS-0420 com divergência de dose aberta:**
  - em execução: `""` · `""`;
  - em conferência: "Carlos · conferir";
  - sem o vínculo da máquina, o resultado seria "Ana (agrônoma) · revisar a divergência de dose…".
- **Caso B, OS-0431 A liberar com saldo zerado:**
  - deu "PCP · reprogramar antes de liberar", com o texto "Próximo passo: liberar para execução";
  - sem o vínculo, o resultado seria "Suprimentos · receber o insumo no Estoque".

### Correção (`areas/processo_os.py:243-280` e `284-299`)
- **Regras que marcam `esp`:** são as que já calculam uma pendência específica.
  - Em execução: insumo esgotado, duplicidade e divergência.
  - Em conferência: o bloqueio do encerramento (`encM`).
  - A liberar: saldo ou lote, lei e total 0. O passo da liberação vai junto.
  - Carência atribuída pelo `carMerge` (`carB`, `carE`, `carCol`).
- **Com `esp`, `osManCond`:**
  - tira o impedimento e o selo da máquina;
  - troca no texto só a parte da máquina: "o PCP reprograma…" segue como atividade paralela, e o passo da pendência entra no lugar de "liberar para execução";
  - mantém o dono e o prazo.
- **Sem `esp`:** o padrão de antes, igual ao REV-A5 e ao bloqueio múltiplo.
- **O que a correção não usa:** heurística por texto do dono ou hierarquia nova.

### Teste de unidade (`ma_os_unit.js:19-44`, no `ma_regras_test.py`)
- **COMP-02 A, em execução e em conferência:** o dono e o prazo são iguais aos de `osMerge({...b,bloq:null})`.
  - Os valores são "Ana (agrônoma)" · "revisar a divergência de dose do dia 1" e "… de dose".
  - Não há impedimento nem selo da máquina.
  - Em conferência, o encerramento continua bloqueado pela divergência: ativo apto não encerra a revisão agronômica.
- **COMP-02 B:** "Saldo insuficiente…" leva a "Suprimentos · receber o insumo no Estoque", com o texto "A liberação aguarda … no Estoque".
- **Controle:** com o estoque original, o resultado continua "PCP · reprogramar antes de liberar".

## Comandos → resultados (executado)
- Comandos rodados de `tools/prototipo/v37/gen37`.
- Testes de navegador com `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpV55B.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 <teste>`.
- "Antes" é a cópia de a3b4dab, com o `_render` dela. "Depois" é esta branch.
- Os logs estão em `logs/` e em `depois/`.

| Comando | Antes (a3b4dab) | Depois |
|---|---|---|
| `acao_unica_test.py responsivo` | teste antigo: 1 ok · 2 falhas (17: oráculo do progresso a 800×360/768×1024; 18: aviso sobre o comando). Teste novo: 1 ok · 4 falhas (17: aviso sobre "‹ Operações e recursos" a zoom 200 %; 18; 18b; 18c) | 5 ok · 0 falhas |
| `acao_unica_test.py saf` | 10 ok · 0 falhas | 10 ok · 0 falhas |
| `acao_unica_test.py v3` | 10 ok · 0 falhas | 10 ok · 0 falhas |
| sonda `resp01/sonda_resp01.py` | 360×420: toque perdido no aviso (com e sem safe-area, os dois avisos) | toque e Tab+Enter avançam em todas as linhas |
| `partest.py` | teste antigo: 46 ok · 1 falha (T1-C). Teste novo: 50 ok · 0 falhas | 50 ok · 0 falhas; mutante: 49 ok · 1 falha |
| `ma_regras_test.py` | 145/145; com os casos novos, 147/150 (os 3 COMP-02 vermelhos) | 150/150 |
| `ma_app_test.py` | 36/36 | 36/36 |
| `ma_unica_test.py` | 22/23 duas vezes (AC-PCM-02: painel "Novo plano do Silo 01" ainda vazio na leitura) | 23/23 (¹) |
| `dose_divergente_test.py unit` | 35/35 + 2/2 | 35/35 + 2/2 |
| `dose_divergente_test.py nav` | 21/21 | 21/21 |
| `os_cenario_test.py` | 20/21 | 20/21: a mesma falha, idêntica no `diff` ("A liberar sem revisão… área 0 recusada…") |
| `ostest.py` | 32 ok · 1 falha | 32 ok · 1 falha: a mesma (OS-0440, VERMELHOS.md) |
| `os_aprov_lib_test.py` | 45/45 | 45/45 |
| `build.py` / `montar_render.py` | 0 FALHA · 142 páginas | 0 FALHA · 142 páginas |
| `varredura.py` | — | 142/142 páginas sem erro (estado final, `logs/final_varredura.log`) |

(¹) O AC-PCM-02 depende de tempo: ele lê o painel logo depois de abrir.
- Numa sonda isolada, o painel abre nas duas versões.
- Nesta branch, a 1ª leitura veio vazia uma vez.
- Detalhes em `logs/ma_unica_acpcm02_sonda.txt`.
- O defeito é do teste. Não é efeito destas mudanças.

## Limitações e pendências
- **Emulação:** Chrome headless com emulação, não aparelho físico. A safe-area foi emulada (`Emulation.setSafeAreaInsetsOverride`).
- **Mudança de largura do aviso:** vale para todas as telas, que agora mostram um aviso mais largo no celular. Rodados: varredura, acao_unica saf, v3 e responsivo, e os testes da O.S. e da MA. Não houve bateria geral nova.
- **Quando o aviso some, no fim da rolagem:** a reserva volta a 30 px (8 px + 22 px + safe-area), e a área desce o equivalente à altura do aviso.
- **Quando um aviso aparece, no fim da rolagem:** a área pode ficar sob o aviso até a pessoa rolar ou o aviso sumir, em 4,5 s. A folga passa a existir na hora, mas a posição de leitura não muda sozinha.
- **Atualização no headless:** `--aviso-h` acompanha a troca do aviso no mesmo `componentDidUpdate`. O redimensionamento depende do quadro do g2glob, que no headless carregado chega com atraso. Por isso o caso 17 espera dois quadros.
- **Falhas de base iguais nos dois lados:** `os_cenario` e `ostest` não fazem parte destes três itens.
- **AC-PCM-02 do `ma_unica_test.py`:** a leitura sem espera continua instável. A correção do teste fica para a frente da MA.
- **`docs/STATUS.md`:** não foi atualizado neste pacote.
