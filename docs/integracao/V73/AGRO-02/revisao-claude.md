# Revisão Claude do PR #94 (AGRO-02: produto e dose escolhidos explicitamente na decisão MIP)

```text
ID / resultado útil / persona: PR #94 (AGRO-02, seleção explícita) · a decisão "Decidir controle" abre sem produto nem dose; o RT escolhe os dois · Ana, agrônoma RT, no AG-01 (1440 px) e no celular (390 px)
Requisitos do PRD e fora do escopo: AGENTS §3.3 (lote, dose, quantidade e autorização nunca vêm do último valor) e §4 (aprovação agronômica individual; trava só onde protege algo concreto) · fora: selos prévios com dose mínima, cobertura por local/lotes e compra (declarados pelo Codex)
Autor / revisor / integrador: Codex / Claude / Claude (DEC-0910-02; regime leve do protótipo, AGENTS §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: PR HEAD b44ea3294a8384c0828f04fbf110c5d5b60104c5 sobre d995ded · composição local 457ef14 (não enviada) · esta pasta e claude/
Aceite e comando de verificação: aceite do contrato PR #47 6228584304; comandos e brutos nas seções "Resultados" e claude/brutos/
Estado / impedimento / próximo passo: mérito favorável; não integrar b44ea32 como está (A1 e A2). Novo HEAD com o patch dos testes e a linha do selo; depois, rodar de novo o que está em "Para o próximo HEAD"
```

Revisor: Claude, 17/10/2026. Sem push e sem comentário no GitHub nesta etapa. Dados só sintéticos.

## O que o PR muda

- `areas/agronomia.py`, `agDecIni`: deixa de procurar o primeiro produto sem trava (com `L[0]` de recuo) e de preencher `dose = dmin`. Agora o estado nasce com `prod:''` e `dose:''`, e o foco vai para `pan_x` ("Fechar").
- `agDec`, `pick` do produto: trocar de produto limpa a dose; o mesmo produto mantém o que foi digitado.
- As guardas não mudam: `mipChecks`, `cenUsoLegal` e `mipEmitir` (`mip.js` e `cenario.js`) ficam fora do diff.
- Teste novo `agro02_selecao_unit.js` e relatório `codex/REVISAO.md`. Contrato no PR #47, comentário 6228584304; análise no 6228484684.

## Junção (ensaio, executado)

- `git merge-tree --write-tree b44ea32 457ef14`: **sem conflito**, árvore `a001598`, base comum d995ded.
- `agronomia.py`, `mip.js` e `cenario.js` são iguais em d995ded e 457ef14.
- Junção local `c83b9b5` (pais 457ef14 e b44ea32), não enviada: o delta de `agronomia.py` é igual ao do PR. Resultados: `agro02_selecao_unit` 7/7 e `rev94_node` 10/11, o mesmo A1 da candidata. Brutos: `claude/brutos/ensaio_integracao.log` e `claude/brutos/juncao_c83b9b5_node.log`.

## Resultados (candidata b44ea32 × base d995ded)

**Render.** Rodado nas duas árvores, sem erro (148 artboards, 156 páginas, Lagoa Grande sintética 5/5):

```
SAFRION_DADOS=sintetico python3 -W error::SyntaxWarning -B build.py && SAFRION_DADOS=sintetico python3 -B montar_render.py
```

**Navegador.** Comando:

```
env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico python3 -B <teste>
```

- Um teste por vez, cada um atrás do portão (≤ 1 Chrome principal, laço `until`): `claude/rev94_gate.sh`, `claude/rev94_fila.sh` e `claude/rev94_fila2.sh`.
- Perfil e porta próprios em cada execução.
- O Node local é o 22.22.0; o Codex usou o 24.19.

| Teste (executado) | Candidata | Base | Leitura |
|---|---|---|---|
| `node agro02_selecao_unit.js` (PR) | **7/7** | 1 passou, 6 falharam | contraprova do Codex reproduzida |
| `claude/rev94_sonda.py` (1440 mouse e teclado; 390 toque) | **28/32**; as 4 falhas são o A2 (S2a e S7a nas duas larguras) | **2/12**: produto já marcado, 0,5 L/ha preenchido, e o clique em Emitir grava a OS-0440 com a dose mínima | a sonda reprova a base |
| `claude/rev94_selo.py` (agDec real em Node) | o HEAD mostra "Conferido" com dose '', '0', '0,' e 'abc' (4 falhas); a correção proposta passa 6/6 | igual (latente) | A2 |
| `claude/rev94_node.py` A: verificação 9 do `quantidade_test` isolada | **FALHA**: 0 travariam com 1 casa | OK: 5 travariam | A1 |
| `claude/rev94_node.py` A2: a mesma, com o ajuste proposto | OK: abre vazio em 10/10 e 5 travariam | FALHA: abre vazio em 2/10 | o ajuste vira contraprova do AGRO-02 sem navegador |
| `claude/rev94_node.py` B: guardas do `mipEmitir`, VIS-013 | 7/7 | 7/7 | ver as recusas abaixo |
| `claude/rev94_node.py` C: travas legais | 2/2 | 2/2 | Paraquate 200 SL (registro cancelado) e 2,4-D 806 (sem registro para feijão × mosca-branca) |
| `mip_fluxo_test.py` | **7 OK; FALHA 8; exceção em 9** (a OS-0440 não existe) | 15/15 | A1 |
| `mip_correcoes_test.py` | parte a 7/7; **parte b para na linha 86** (a OS-0440 não foi emitida) | parte b 7/7 | A1 |
| `mip_fluxo_test.py` com `claude/rev94_testes_obsoletos.patch` | **15/15** | 15/15 | A1 corrigido |
| `mip_correcoes_test.py` com o patch | **14/14** (a + b) | parte b 7/7 | A1 corrigido; o patch é revertido no fim (`claude/brutos/fila2_resumo.txt`) |
| `quantidade_test.py` | aborta: `irrTerminar` "Antes do fim previsto…" | aborta igual | O1, vermelho antigo |
| `mip_unit_test.py` | 34/34 | 34/34 | |
| `agtest.py` | 16/16 | — | |
| `agrofit_test.py` | 18/18 | — | |
| `agrofit_faixa_test.py` | 17/17 | — | |
| `paginas_scan_test.py` | 5 ok · 0 falhas (148 páginas) | — | |

Recusas do `mipEmitir` conferidas no item B:

- sem produto → "Escolha um produto registrado.";
- dose '', '0', '0,' e 'abc' → "Informe a dose.";
- 2,25 → "Dose fora da bula: 0,5–0,75 L/ha.".

Nenhuma dessas recusas cria O.S. Com a dose explícita de 0,625 L/ha, a OS-0440 nasce em A liberar com 0,625 e 59,38 L, e o receituário leva a mesma dose.

Os `agrofit*`, o `agtest` e o `paginas_scan` rodaram só na candidata: não leem a decisão do MIP e servem como regressão de tela, não como contraprova.

### Contraexemplos do RT (sonda, candidata)

- **Abertura (VIS-013, feijão × mosca-branca, 95 ha).**
  - Tela: 4 registrados, nenhum marcado e dose vazia. "Escolha um produto registrado." aparece em `role=alert` e o Emitir fica desligado.
  - Leitor de tela: 4 rádios com o nome do produto e `checked=false`. O Emitir está `disabled`, com a descrição "Resolva a trava acima para continuar".
  - Na base, o Ciantraniliprole vem marcado com 0,5 L/ha. Um clique em "Emitir receituário e gerar O.S." grava a OS-0440 com a dose que o RT não digitou.
- **Escolher o produto.**
  - A dose continua vazia, o rótulo vira "Dose (L/ha)" e aparece "Informe a dose.".
  - Um clique ou toque real no Emitir não grava O.S.
- **Quantidade.** Com 0,625 L/ha × 95 ha, a mensagem de estoque diz 59,38 L, igual ao oráculo `Decimal` (meio para cima).
- **Troca de produto.** A dose digitada some. Reclicar o mesmo produto (mouse ou toque) e Espaço no rádio marcado preservam a dose. Voltar ao primeiro produto deixa a dose vazia, sem herdar a do segundo.
  - No navegador, o React não dispara `onChange` num rádio já marcado. O ramo "mesmo produto" do `pick` só é defensivo, e o resultado é o pedido.
- **Dose fora da bula.** 2,25 L/ha trava com "Dose fora da bula: 0,5–0,75 L/ha.". A dose 0 trava com "Informe a dose.".
- **Carência × colheita.** Acaricida D em 28/09, com dose válida: a trava fica à vista, o selo fica vermelho e o Emitir, desligado.
- **Fechar e reabrir.** Esc (1440) ou Cancelar (390) fecham a decisão. "Decidir controle" reabre sem produto e sem dose.
- **Teclado.** O foco inicial fica em "Fechar", e o 1º produto é o 4º Tab. O foco fica preso no diálogo. A seta para baixo no grupo troca o produto, e a dose fica vazia.
- **Emissão com a dose digitada.** Com 0,625, nas duas larguras, a O.S. nasce em A liberar com 0,625 (não com a mínima de 0,5) e o total é 59,38 L.
- **390 px.** Não há rolagem horizontal. A linha do produto tem de 118 a 264 px de altura, e o rótulo inteiro é o alvo do toque.

Capturas: `claude/brutos/rev94_1440_1_abertura.png` (rótulo "Dose (/ha)") e `claude/brutos/rev94_1440_2_sem_dose.png` ("Conferido" verde com a dose vazia).

## Achados

| # | Sev. | Caminho | Contraexemplo | Dano | Correção |
|---|---|---|---|---|---|
| A1 | S3, bloqueia a integração | `mip_fluxo_test.py:67,72`, `mip_correcoes_test.py:83,87`, `quantidade_test.py:73-76,191` | Os testes clicam o produto e emitem, contando com a dose mínima que o formulário preenchia. Na candidata, o `mip_fluxo` para no passo 8 com "Informe a dose." e o `mip_correcoes` b para na linha 86. A verificação 9 do `quantidade_test` fica sem contraprova: com `prod:''`, `mipChecks` sai em "Escolha um produto registrado." antes da checagem de área, então 0 travariam e o teste pede ≥ 1. | A bateria da versão composta fica vermelha (§3.6, base verde) e perde a cobertura da emissão MIP → receituário → O.S. a partir do passo 8. O vermelho da verificação 9 ainda fica escondido, porque o arquivo já aborta antes (O1). | `claude/rev94_testes_obsoletos.patch`, que faz o RT digitar a dose nos dois testes de navegador. Na verificação 9, escolhe explicitamente o 1º registrado não cancelado, com a dose mínima, e afirma que o formulário abre vazio. Verificado: a tabela acima, e A2 reprova a base. |
| A2 | S3 | `areas/agronomia.py:646` (`TAGS`/`cc` em `agDec`) | VIS-013: sem escolha, o Ciantraniliprole mostra "Sem estoque" (amarelo, calculado com a dose mínima). Escolhido, a dose fica vazia e o selo passa a **"Conferido" verde**, enquanto "Informe a dose." trava a emissão. O mesmo acontece com '0', '0,' e 'abc'. A causa: "Informe a dose." não tem TAG, e a conferência de estoque só roda com dose > 0. Na base o defeito era latente (o RT precisava apagar a dose). O PR o torna o estado padrão de cada escolha. | Sinal falso de conformidade legal e de estoque sobre uma dose que ninguém conferiu, justamente no passo que o AGRO-02 quer explícito. Não há emissão indevida (o botão continua bloqueado), por isso é S3. | Selo neutro (ETP-01) enquanto a dose do escolhido não for > 0: `const cc=(sel&&!(num(d.dose)>0))?['Informe a dose','gray']:(tt.length?…)`. Verificado em memória pelo `rev94_selo.py` (6/6: '', '0', '0,' e 'abc' viram o cinza neutro; dose válida e prévia sem escolha não mudam). Proteção de regressão: o próprio `rev94_selo.py` ou um caso no teste do PR. |
| A3 | S4 | `agronomia.py:458` (`dc_temProd`) | Ao abrir, o campo mostra "Dose (/ha)", sem unidade, e aceita digitação antes do produto. Ao escolher o produto, o que foi digitado some sem aviso. | Rótulo quebrado na primeira tela e digitação perdida. A direção é segura: nada vai para a O.S. | Mostrar a dose só com produto escolhido (`sc-if` num `dc_temSel`) ou deixá-la desabilitada com "Escolha o produto". |
| A4 | S4 | `agDecIni` → `agFoco('pan_x')` | Quem abre a decisão por "Decidir controle" cai em "Fechar". O 1º produto é o 4º Tab, e Enter no foco inicial fecha o painel. Na base o foco ia para a dose. | Caminho de teclado mais longo, com a ação de fechar na frente. | Com `dc_temProd`, focar o 1º rádio do grupo "Produto registrado" (ou o grupo); sem produto registrado, manter `pan_x`. |
| A5 | S4 | `agro02_selecao_unit.js` | O arquivo não tem invólucro `.py`. A bateria só roda `*.py` (V66: 187 itens, nenhum `.js`), e 37 dos 40 `*_unit.js` da composição têm o seu. O teste também extrai as expressões por regex, então quebra se mudar a forma do código. | A proteção de regressão do AGRO-02 fica fora da bateria. | `agro02_selecao_test.py` no molde do `kanban_raias_test.py`, ou a chamada dentro do `mip_unit_test.py`. O A2 do `rev94_node` (verificação 9 ajustada) já cobre a abertura vazia sem navegador. |

## Fora do escopo (já existiam; não bloqueiam)

- **O1.** O `quantidade_test.py` aborta já em d995ded, em `irrTerminar(s,'OS-0604',24.47,null)`, com "Antes do fim previsto, registre término antecipado…". Na V66 estava 14/14. É vermelho antigo de irrigação, de outra frente.
- **O2. Acessibilidade.**
  - O nome do rádio é só o nome do produto (`aria-label`): o selo e o resumo da bula ficam fora do nome e da descrição.
  - O campo "Dose por hectare" não tem a unidade no nome acessível.
  - O campo não usa `aria-invalid` nem `aria-describedby` ligados a "Informe a dose." (pela árvore AX, `invalid=false` com a trava à vista).
- **O3. Layout a 390 px.**
  - Em "Resultado por alvo", "adultos/folíolo" sobrepõe a coluna vizinha (captura `claude/brutos/rev94_390_2_sem_dose.png`).
  - O nome do produto quebra em duas linhas por causa do selo e de "Ficha ›".
- **O4.** A prévia dos produtos não escolhidos ainda usa a dose mínima, como o Codex declarou.

## Veredito

**O mérito é favorável.** O PR cumpre o aceite combinado:

- abre sem produto e sem dose;
- trocar de produto limpa a dose;
- o mesmo produto preserva a dose;
- as guardas não mudaram e bloqueiam a emissão sem produto, sem dose, com dose 0, com rascunho, com texto e com dose fora da bula.

O PR também remove um defeito real da base: um clique emitia a O.S. com a dose mínima que o RT não digitou.

**O b44ea32 não deve ser integrado como está**:

- **A1 é obrigatório**: sem ele, a bateria da composta fica vermelha.
- **A2 deve ser corrigido no mesmo PR**: é uma linha, e é consequência direta da mudança.
- **A3 a A5 são recomendados**: podem ir juntos ou numa próxima fatia, com registro.

Os testes do A1 estão fora da lista de arquivos do contrato. Para isso proponho que o Codex inclua o patch no próximo push, e por este parecer o revisor concorda em ampliar o escopo. A alternativa é o Claude aplicá-lo como ajuste da revisão na integração, com revisão do Codex, como no PR #89.

### Para o próximo HEAD

- `node agro02_selecao_unit.js` (ou o invólucro do A5);
- `rev94_selo.py`: as 4 verificações do HEAD passam; a correção em memória deixa de se aplicar;
- `rev94_node.py`: A2, B e C verdes. A é a verificação 9 antiga e falha por desenho depois do AGRO-02; quem vale é a A2;
- `mip_fluxo_test.py` e `mip_correcoes_test.py`;
- `rev94_sonda.py`, com a meta de 32/32, nas duas larguras.
