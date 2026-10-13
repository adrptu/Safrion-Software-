# BEN3 · rodada 3 do Beneficiamento integrada na v56

Rótulo: **executado**, com dados sintéticos (`SAFRION_DADOS=sintetico`), em `tools/prototipo/v37/gen37`.

- Branch: `claude/v44-ben3`, sem push. Base: candidata v56 `3f9e4f6`.
- `BEN_PUBLICADO` continua `False` em `ui37.py`. Ligar a tela depende da revisão.
- Fontes:
  - o desenho com as invariantes e a crítica C-1 a C-18: [`DESENHO.md`](DESENHO.md);
  - o aceite do Codex: [`codex-BEN-REV-20261010-06.md`](codex-BEN-REV-20261010-06.md);
  - as decisões: BEN-D33 a BEN-D38 de [`docs/beneficiamento/DECISOES.md`](../../beneficiamento/DECISOES.md) (a BEN-D38 é a revisão adversarial).
- Brutos: pasta [`brutos/`](brutos/), com o resumo do navegador em [`brutos/RESUMO_navegador.txt`](brutos/RESUMO_navegador.txt).
  - "Antes" é o código de `3f9e4f6` com os testes desta rodada, numa cópia feita com `git archive`.
  - "Depois" é esta branch.

## Commits

| Commit | O que faz |
|---|---|
| `5b150b1` | Resgate do trabalho que o agente anterior deixou sem commit sobre `a3b4dab` (v55) |
| `88728cf` | Merge da v56 (`3f9e4f6`). Conflito só na tabela `MTIPO` do Estoque: ficam a `reserva-baixa` (BEN) e a `inspecao-reprovada` (CTL-4) |
| `8b92fee` | U57a-g e mutantes M96-M102: sete regras do desenho que nenhum teste de unidade prendia |
| `1992c3c` | A propriedade passa a conferir a reserva própria do motor (I-d4, nova) e o selo da sobra (I-a1) |
| `17b844a` | Resgate do que ficou sem commit quando a cota interrompeu a sessão (pacote, caminhos, primeiros ajustes do teste de tela) |
| `9831a6e` | O Comercial lê a origem do lote embalado pela genealogia (`comOrigens`; C06j e C06k) |
| `1bbf442` | `ben_fluxo_test` segue a v56 e o estado do BEN fora da navegação |
| `15e2976` | BEN-D37, este README e os brutos |
| `0e7e3cd` … `eea40a3` | Correções da revisão adversarial A1 a A8 (seção abaixo) |
| (último) | BEN-D38 e este README |

## Regras implementadas e o teste de cada uma

| Regra (invariante do DESENHO §3) | Unidade | Propriedade (`ben_prop.js`) | Mutantes mortos | Tela (`ben_fluxo_test.py`) |
|---|---|---|---|---|
| A sobra é a custódia acima do teto do kg aberto em toda fase aberta, com ou sem a conferência dada (I-a1, BEN-D33) | U47a-e, U57e, U57f | I-a1 e o selo (U53g) | M77, M78, M100, M101 | `conferencia`, `conferencia390` |
| Divisão da devolução: a parte até a sobra volta livre e sai do "a entregar"; a caixa em uso volta reservada à linha; a avaria vai para a quarentena (I-a3, I-d2) | U48a, U48c, U48e, U57b, U57c | I-a3, I-d2 (U53a, U53b) | M80, M94, M97, M98 | `sobra`, `sobra390`, `lotes` |
| "A entregar" = solicitado − dispensado − consumido − custódia; só o BEN grava `dispensado` (I-d1) | U48a, U48c | I-d2 | M81 | `sobra` (a conta não diz "dispensado") |
| A entrega baixa só a reserva própria e mantém a trava física (I-d3, crítica C-2) | U48b, U48d, U55 | I-e4, I-d4 | M85a, M85b, M90 | `multilote` |
| `cenResTot`: a base da REQ da semente é o entregue, e a `reserva-baixa` é descontada | U57a, U57b | I-d4 | M96, M97 | — |
| O gancho da devolução falha fechado sem o ben.js (crítica C-10) | U56 | — | M91 | — |
| O Fechar baixa a reserva não entregue (I-a4, I-e4, BEN-D35) | U51, U47e, U57a | I-a4, I-e4 (U53d, U53e) | M84, M95 | `multilote` (reserva 0) |
| Falta na execução: `benFaltaCx` = máx(0, mín(teto, Σsol − Σcons) − Σcust − Σpend), sem `necRota` (I-f4, crítica C-1) | U52a, U52b, U54, U57c | I-f4 | M89 | `complemento` X2 |
| Livre total dos lotes elegíveis; uma linha por lote; tudo ou nada (I-b1 a I-b4, BEN-D34) | U49a-f | I-b1, I-b2, I-b3 (U53c, U53f) | M82, M83 | `multilote`, `multilote390` |
| Fontes de recuperação: sobra de outra ordem, notas e quarentena; a que cobre sozinha, senão todas; a ação real da fase (I-f1 a I-f3) | U49b, U50a-c, U57d, U57g | I-f1, I-f2, I-f3, I-a2 | M79, M99, M102 | `cadeia`, `cadeia390` |
| Devolução guiada no Estoque: `#dev=`, pré-preenchido pela sobra (`benDevPadrao`), revalidação pela sobra e pela fase, retorno à ordem (I-c1 a I-c5) | U47e, U48c | — | M86, M93 | `sobra`, `sobra390` |
| Reserva sem físico depois de um ajuste aprovado: só aviso; a trava física impede o negativo **na entrega**, não no ajuste: aprovar uma contagem velha ainda pode deixar o físico em −69 (A4, do Estoque, fora do BEN) | U55 | — | — | — |
| Tela do BEN: tecla segurada não age, foco no título depois do comando, rascunho protegido, aviso fora do rodapé, rótulos sem verbo repetido (I-g1 a I-g4, I-h1, BEN-D36) | — (código de tela) | — | — | `teclado` T13-T16, `rodape` R1-R4 |
| A venda de fruta beneficiada lê a origem de campo pela genealogia; a abertura conta como origem anterior ao sistema; a falha é fechada (BEN-D37, COM × BEN) | `comercial_unit.js` C06j, C06k | — | — (a contraprova é o código de `3f9e4f6`) | `fluxo` passo (4), PV-031 |

## Revisão adversarial (parecer de 13/10 sobre `15e2976`, A1 a A8)

Cada teste reprova no `15e2976` e passa depois. "Sonda" é a do revisor, rodada no código corrigido.

| Achado | Commit | Teste que reprova antes | Contraprova do revisor |
|---|---|---|---|
| A1 · S2 · pedir a falta não a baixava (139 → pedir 139 → "Faltam 61") | `0e7e3cd` | U52a2, U52c; propriedade I-f5 e U53h; mutante M103 | `pB.js`: 139 → 130 → 0; avaria 50 → 0 |
| A2 · S2 · caixa em uso devolvida bloqueada virava fonte de outra ordem | `a415923` | U58a, U58b; propriedade I-a3 (bloqueada), I-a5, I-f6 e U53i; M104, M105 | `pI.js`: sem fonte quarentena; o laudo devolve as 300 à OB-0113 |
| A3 · S3 · quarentena reprovada citada como fonte que cobre | `74c2607` | U59; propriedade I-f6 com "reprovar" e U53j; M106 | `pC.js`: só a sobra real como fonte |
| A8 · S2 · aba velha pela lista gravava a sobra de novo (869 → 730 → 591) | `001f50c` | `ben_fluxo_test` sobra, passo 6 (1440 e 390) | `tela/rev_u3.py`: OK 5/5 (antes 3/5) |
| A5 · S3 · lote do BEN devolvido pelo cliente perdia a genealogia | `9117ec7` | `comercial_unit` C06l | `pH2.py`: o lote devolvido aponta o L39-120 |
| A6 · S4 · ciclo na genealogia passava sem avaliação | `8dc39a3` | `comercial_unit` C06m | `pH.py`: ciclo, autorreferência e ciclo com campo impedidos |
| A7 · S4 · "com tudo registrado" e "caixas em uso" numa ordem conferida | `20a73c0` | U60; `ben_fluxo_test` conferencia, passo 5; M107 | — |
| A4 · S2 do Estoque (ajuste de contagem velha → físico −69) | — | fora do BEN, com a frente do Estoque | `pE.js` continua mostrando −69, como na base |

Números depois da revisão:

- `ben_unit_test` OK 206/206; no `15e2976`, FALHOU 200/206 (os seis testes novos).
- `ben_prop_test` OK, 360 × 35, 10 casos fixos; no `15e2976`, FALHOU com I-f6, I-a3, I-f1 e U53h-j.
- `ben_mutantes` OK 104/104.
- `comercial_unit_test` OK 118/118; no `15e2976`, FALHOU 116/118.
- `producao_unit_test` OK 123/123.
- Navegador, BEN oculto, carga ≤ 8: NAVREV.
- Sondas do revisor no código corrigido:
  - sem violação: pA, pA2, pB, pC, pF (igual à candidata), pG (CTL-4 sem diferença), pH, pH2, pI e pI_base;
  - o `pE` mostra o A4;
  - a `propX` não acha mais X1, X3 nem I-f1; restam X2, I-e4 e I-e3, todas com ajuste aprovado na trilha (A4).

## Testes da rodada 3, antes e depois (integração na v56)

| Prova | Comando | Antes (`3f9e4f6` + testes novos) | Depois |
|---|---|---|---|
| Unidade do BEN | `python3 ben_unit_test.py` | FALHOU 165/200 (35 falhas: os testes da rodada 3 e as expectativas mudadas de propósito) | OK 200/200 |
| Propriedade (3 sementes, 360 × 35, oráculo independente) | `python3 ben_prop_test.py` | FALHOU com I-d2, I-a3, I-d4, I-b1, I-a4, I-e4, I-b3 e I-a1, e os 7 casos fixos U53a-g | OK |
| Propriedade, tamanho noturno | `RUNS=400 STEPS=50 python3 ben_prop_test.py` | — | OK, 1.200 × 50 |
| Mutantes | `python3 ben_mutantes.py` | — (as âncoras são do código novo) | OK 99/99 |
| Unidade do Comercial | `python3 comercial_unit_test.py` | FALHOU 114/116 (C06j, C06k) | OK 116/116 |
| Harness do Codex (BEN-REV-20261009-03) | `python3 docs/integracao/BEN/rev03/run_harness.py`, na raiz | OK 4/4, CX26-01 `[540, 0]` | OK 4/4, CX26-01 `[540, 540]` (pergunta P1) |
| Unidades vizinhas, sem navegador | 22 testes (`brutos/depois/unidades_vizinhas.txt`) | — | todas verdes |
| Build e montagem | `build.py`, `montar_render.py` | 138 artboards, 145 páginas | 138 artboards, 0 FALHA, 145 páginas |

### Navegador

Regras de execução: carga de 1 minuto ≤ 8, um teste por vez, `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpI.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900`.

| Teste | Base `3f9e4f6`, tela oculta | Worktree, tela oculta | Cópia com a tela publicada (rascunho, sem commit) |
|---|---|---|---|
| `ben_fluxo_test` roteiro, roteiro390 | exceção no R1 (0/8) | OK 34/34 | OK 34/34 |
| cadeia, cadeia390 | — | OK 16/16 | OK 16/16 |
| fluxo, erros, celular, revisao | exceção no passo (2) (2/13); publicada: 60/64 | OK 62/62 | OK 64/64 |
| complemento, lotes, duplo, criada | — | OK 26/26 | OK 26/26 |
| teclado, cancelar, faixa390 | 24/28 | OK 29/29 | OK 33/33 |
| conferencia, conferencia390, sobra, sobra390 | — | OK 26/26 | OK 26/26 |
| multilote, multilote390, rodape, manutencao | — | OK 18/18 | OK 18/18 |
| `links_ocultos_test` | — | 14, 0 falhas | — |
| `comercial_fluxo_test` / `comercial_revisao_test` | — | OK 72/72 / OK 33/33 | — |
| `producao_fluxo_test` | — | OK 67/67 | OK 67/67 |
| `tabelas_est_test` / `tabelas_ben_test` | — | 34/34 / OK 12/12 | — / OK 12/12 |
| `demanda_estado_nav_test` (lock 9333) | — | 14 ok, 0 falhas | — |
| `cafe_apurar_test` / `dose_divergente_test` | — | OK 10/10 / 21/21 | — |

Vermelhos da base, com a causa:

- Com a tela oculta, roteiro, fluxo e faixa390 tentam entrar pela faixa das Cargas, que não oferece a tela. Era teste obsoleto. Agora esses modos conferem que a navegação não aponta a tela oculta e entram pelo endereço.
- Com a tela publicada, o passo (4) do fluxo esperava a primária "Registrar resultado" para o Igor. A v56 só dá o verde a quem tem o papel. Era teste obsoleto.
- Ainda no passo (4), o PV-031 ficava Em risco ("sem lote de campo"). **Era defeito do produto (COM × BEN), corrigido no `9831a6e`.**

Os grupos da cópia publicada fora do fluxo e os testes vizinhos foram rodados antes do `9831a6e` e do `1bbf442`. Essas mudanças só alcançam as telas do Comercial e os ramos com `BEN_PUBLICADO=False` do `ben_fluxo_test`, e os testes afetados foram repetidos depois.

## Mutantes

- **Mortos:** 99 de 99 no `ben_mutantes.py`. Os novos M96 a M102 vieram de uma sonda de 24 mutantes extras nas regras desta rodada. Oito sobreviviam aos testes de unidade, e os U57a-g fecham sete deles.
- **Contra a propriedade:** também morrem M96 a M101. O M102 (só a 1ª nota de caixas é fonte) só tem o U57g, porque a semente tem uma nota de caixa só.
- **Equivalente:** "ordem sem caixa marcada como reservada" não muda nada alcançável. Só a PACK-FRU v3 está aprovada, e ela exige ao menos 1 caixa.
- **De tela, fora do `ben_mutantes.py`:** M87 (tecla segurada), M88 (Esc descarta) e M92 (revalidação só pela versão). O `ben_mutantes.py` roda só o motor. Esses três ficam com os modos `teclado` (T13-T16) e `sobra` (S3 e S4), que reprovavam no código anterior (BEN-D36).

## Limites e pendências

- **Demanda viva da CTL-4:** `cenOsSup` e `cenEstDem` leem as caixas da ordem como bruto e não conhecem o `dispensado` nem a sobra do BEN. Hoje isso não muda compra nenhuma, porque a caixa não é insumo do plano (não aparece em `dados2.os_base` nem em `est_base`). Quando a compra de caixas entrar (BEN-2), a demanda tem de ler `benFaltaCx` e `benCxSobra` (BEN-D37).
- **Arquivo do Comercial:** o `comercial.js` é da frente COM. A mudança é mínima (`comOrigens`) e tem teste ao lado do C06. Vale a conferência do autor do Comercial.
- **`est_laudo_lote_nav_test.py`** não existe em `3f9e4f6`. Ele entrou depois, na branch da CTL-4, e não foi rodado.
- **Gerador da propriedade:** não gera contagem, ajuste, `benRetirar`, `benConfirmarCorrecao` nem comandos de O.S. Os invariantes valem para esse conjunto, e a O.S. fica com os testes de O.S.
- **Fora do escopo** (DESENHO §0): compra de caixas (BEN-2), cancelar ordem liberada (BEN-6), filtro por local de packing e travar a aprovação de ajuste abaixo da reserva (Estoque).
- **Situação do PV-031:** com o BEN publicado, o PV-031 fica "Aguardando crédito", porque a Frutas Real passa do limite. É regra do Comercial, que tem precedência sobre "Parcial".
- **Perguntas ao Codex, não ao proprietário:**
  - P1: as 540 caixas devolvidas em execução voltam reservadas (`[540, 540]`).
  - P2: custódia inteira no Fechar e em conferência dentro da faixa.
  - P3: o `dispensado` não se estende à O.S.
  - P4: a revalidação usa a sobra e a fase; a versão vai só como contexto.
  - P5: a falta é pelo planejado, não pela necessidade da rota.
