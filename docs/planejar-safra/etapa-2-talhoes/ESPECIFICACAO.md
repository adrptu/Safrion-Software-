# Planejar safra · etapa 2 "Talhões e cultivos" · especificação v2

**Pedido do proprietário (Adrianus, 05/10/2026):** "em planejar safra, não faz sentido o botão adicionar cultivo, afinal todos talhões da fazenda devem estar disponiveis na tabela. Os talhoes comprometidos com culturas já plantadas, perenes, que indisponibilizam o talhão num dado período, etc devem ser consideradas nessa funcionalidade."

**Base:** `claude/v44-tabelas-05`, HEAD `884620c`, lida em modo leitura. Caminho sem prefixo = relativo a `/home/user/sp-tab5/tools/prototipo/v37/gen37`.

**Documentos irmãos:** decisões, parâmetros do dono, pendências e revisão aplicada em [`DECISOES.md`](DECISOES.md); o que fica de fora em [`FORA-DE-ESCOPO.md`](FORA-DE-ESCOPO.md).

**Evidência:**
- **Executado:** todo número marcado "(exec.)" saiu de `verificacao/` (`./roda.sh`, saídas `saida_*.txt` ao lado). Os scripts aplicam as regras do §4 sobre `dados.py`, `dados2.py`, `dados_cad.py`, `dados_lagoa_safra.py` e `areas/cadastros.py`. Eles não rodam o protótipo.
- **Especificado:** o resto. Nada foi aberto no navegador nesta versão, exceto as medidas de largura do DONO-02, feitas pela revisão (`../rev/dono02_refuta.py`, `../rev/d2_fitcontent.py`).
- A Lagoa Grande usa dados sintéticos (`dados_lagoa_fonte.py:22`, `REAL=False`).
- **Parâmetro em todos os números:** folga de liberação = 1 dia (R-06). Os resultados com folga 0 e 3 estão em `saida_ocupacao_f0.txt`, `saida_ocupacao_f3.txt` e `saida_trava_f0.txt`.

---

## 0. Como executar (fica · muda · sai)

**Arquivos novos** (autor: Claude; revisor: Codex)

| Arquivo | Papel |
|---|---|
| `ocupacao.js` | Serviço único de ocupação (ENG-011): início, Ocupa até, fim por, núcleo, pior caso P(o), liberação, Área livre, Situação, trava, pendência, aviso e PlantioMin. Carregado junto com `cal01.js` em `areas/processo_safra.py:202`. |
| `ocupacao.py` | Espelho em Python das mesmas funções, para paridade e, depois, para o CD-01det. |
| `ocupacao_unit.py` | Unidade, casos de borda e propriedades, JS × Python (OC-U1…U9), no padrão de `rend_multiconjuntos_unit.py`. |
| `ocupacao_test.py` | Navegador: OC-01…OC-23 (§7.1). |

**Muda**

| Onde | Mudança | PR |
|---|---|---|
| `g2lib.js:286` | `presa()`: toda coluna que não é a presa passa de `minmax(min-content, vis)` para `fit-content(vis)`. Seleção e lixeira encolhem ao conteúdo (DONO-02). | G |
| `g2lib.js:146, 172, 186` | `r.fora` recebe o tratamento de `r.livre`: sem seleção, sem lixeira, fora da contagem do filtro de coluna. | G |
| `g2lib.js:42, 46` | Opção `qf.nivel0`: `g2qhas` e o `tok` de `g2qvals` não descem aos filhos. As outras grades não mudam. | G |
| `g2lib.js:221-222` | Título e subtítulo do formulário podem vir do estado (`fm.title`/`fm.sub`): "Planejar T1", "Vincular ciclo C1". | G |
| `g2lib.js:229` | `t:'num'` ganha `inputmode="decimal"`. | G |
| `areas/processo_safra.py:29` | Opções de fazenda = fazendas ativas do CD-01, com a Lagoa Grande. Entra junto com o Vincular ciclo (PR-B3), nunca antes. | B3 |
| `areas/processo_safra.py:32-34` | `TALH`/`TALFAZ` vêm dos talhões **Ativos** de `_tal_rows()` (`areas/cad_fazendas.py:56-66`), com o B1 (`:61`). "PVnn" vira "Pivô n" pelo `DL.PID_DE` invertido (`dados_lagoa_safra.py:19`). | B1 |
| `areas/processo_safra.py:37-39` | `CULT_COLS` = as 16 colunas do §3.1. | B2 |
| `areas/processo_safra.py:40-49` | `CULT_FIELDS` = painel do §2. Saem Talhão e Fazenda. Plano vem antes de Plantio. Entram Parcela sugerida, "Plantio a partir de" e Ocupação prevista (só leitura, `g2live`). **Colheita prevista** é data editável sem plano e só leitura com plano (DONO-07). | B3 |
| `areas/processo_safra.py:70` | `qf=dict(k='sit',l='situação',nivel0=True)`. | B2 |
| `areas/processo_safra.py:201` | `d2` ganha `culturas` (classe e unidade, `dados_cad.py:31-32`), `ciclos` (cultivar → dias, `areas/cadastros.py:406-408`), `hoje` (`dados2.py:4`) e `folga=1`. | A/B1 |
| `areas/processo_safra.py:222` | Título "Talhões e cultivos"; `acao=acoes()` sem botão. | B3 |
| `areas/processo_safra.py:203` | Aviso de safra criada: "Planeje os talhões livres na tabela." | B3 |
| `safra.js` (novo helper) | `cultsDe(self, safId)`: fonte única das linhas desta safra (`sk` + `v.saf`). Usada em `cultRows` (`:308`), `proxSaf` (`:647-651`), contagem e área da etapa 1 (`:655`), `usados` (`:294`), `openApply` (`:904-905`) e no serviço (REG-08). | B1 |
| `safra.js:291` | `leaves()` ignora `r.fora` e `r.livre` em qualquer nível. | B1 |
| `safra.js:292-303` | `syncLivres` vira `syncTalhoes`: monta, **sobre uma cópia** (`g2clone`), a linha de cada talhão e as filhas de fora. Nunca altera o array de `g2rows` (`g2lib.js:20`) nem grava. A fazenda vem da safra pelo id real (hoje `:299` cai em Santa Rita). | B1/B2 |
| `safra.js:305-307` | `cultNovoTalhao` vira `abrirPlanejar(t)`: Área = Área livre, Plantio = PlantioMin (R-17), Parcela sugerida (R-19). | B3 |
| `safra.js:316-317` | `dcol` ganha chave de ordenação e de filtro separadas do texto: perene ordena como o fim mais tardio; "sem data" é valor de filtro próprio, diferente de "(vazio)" (REG-07). | B2 |
| `safra.js:495-516` | `leafParts`/`grpParts` ganham Situação, Livre a partir de, Ocupa até, Fim por e Safra. Em `grpParts`, Tipo, Área e Área livre contam só os filhos desta safra. | B2 |
| `safra.js:518-526` | `normCult` nunca promove filha de fora ao nível 0. | B1 |
| `safra.js:527-537` | `cultCheck`: o talhão vem da linha; soma desta safra ≤ área (regra de hoje) + trava do serviço (R-14). | B4 |
| `safra.js:538-551` | `cultAfter`: grava `v.saf` e a fazenda da safra (hoje `:540` grava "Santa Rita"); `colheita` vem do formulário (`x.colheita||''`); nome sugerido (R-19). Sai o desvio de `:541`. | B1/B3 |
| `safra.js:565-581` | `dvSave`: trava por parcela, erro na própria linha; a parcela nova grava `saf`. | B4/B1 |
| `safra.js:585` | Grupo `grp_` grava `v.saf`. | B1 |
| `safra.js:538, 578, 925` | Os três gravadores passam por `soDaSafra(rows)` (REG-09). | B1 |
| `safra.js:648` | "Continuar: cadastrar cultivos" → "Continuar: planejar talhões". | B3 |
| `safra.js:835` | `k2` vira a faixa de resumo (§3.4). | B2 |
| `safra.js:853-856` | Link de safra grava `#saf=<id>&passo=cultivos[&cult=<id>]`, nunca `etapa=` (padrão do paralelo, `saf345/especificacao.md:432-433`). | B2 |
| `safra.js:885-894` | Ramo `step===2` de `safAcoes`: estados do §5.1. | B3/B4 |
| `safra.js:902-927` | `openApply`/`apVals`/`doApply`: mostra antes quem trava e quem fica com pendência (R-16). | B4 |
| `dados2.py:78-80` | `e4` e `e5` na S2526 com `origem='lavoura em campo'` (§6.2). | B1 |

**Sai**

| Onde | O quê |
|---|---|
| `areas/processo_safra.py:218-220` e `acoes(add_cult)` em `:222` | Os dois "Adicionar cultivo" (`data-acao="adicionar"`). |
| `safra.js:879-881` | `add_fn`, `add_prim`, `add_sec`. |
| `safra.js:541` | Desvio "T2 já está nesta safra → Dividir". |
| `safra.js:303` | "sem cultivo · N ha" e "Planejar talhão ›" na coluna Cultura. |
| `areas/processo_safra.py:40-44` | Campo Talhão, Fazenda fixa e lista fixa de 5 culturas. |
| `safra.js:891` | "adicione o primeiro…". |

**Fica sem mudar:** Dividir (`safra.js:553-633`, agora com R-14 por parcela); `nextNome` (`:319`); plano, versão, meta e ajustes em `leafParts` (`:499-504`); Aplicar plano e ajustes locais (`:902-1002`, com R-16); S2526 só consulta (`:296`); `colheitaDe` (`:18-19`), só para DANC/DAPC; ids dos cultivos, que as O.S. referenciam (`areas/processo_os.py:164-205`).

---

## 1. Perguntas que a etapa responde

1. Quais talhões ativos a fazenda desta safra tem, e quanto de cada um está planejado nesta safra?
2. O que ocupa cada talhão no período (esta safra, outra safra, perene, lavoura em campo), até quando e por qual fonte?
3. Quanto está livre e a partir de que dia posso plantar **com o plano escolhido**?
4. Onde a saída da cultura anterior não está confirmada ou há sobreposição prevista (A conferir)?
5. Quais cultivos estão sem plano? (já existe, continua na nota)

A etapa não responde custo, operação nem demanda.

---

## 2. Layout (Safrinha 2027, especificado)

**1440 × 900.** A coluna 1 fica presa; a 1440 cabem, sem rolar, de "Talhão ou parcela" a "Safra" (§3.1, colunas 1-9; aceite OC-17).

```
┌ Planejar safra · Fazenda Santa Rita · Safrinha 2027 ───────────────────────────────────────────────────────┐
│ Talhões e cultivos                                                                   (cabeçalho sem botão) │
│ Nesta safra 553 · Livre 152 · A conferir 380 · Perene 80 · de 1.165 ha · 1 sucessão a conferir            │
│ [Todas 8] [A conferir 4] [Perene 2] [Livre 1] [Planejado 1]                         [🔍 Buscar          ] │
│ ┌──┬────────────────┬──────────┬──────────┬───────────┬──────┬───────┬───────────┬──────────┬────────── → │
│ │☐ │Talhão ou parc. │Situação  │Área livre│Livre a p. │Área  │Cultura│Ocupa até  │Fim por   │Safra      │
│ │  │▾ T1 Planejar › │Livre     │152 ha    │21/02/2027 │160 ha│Milho  │           │          │           │
│ │  │   T1-A         │          │          │           │160 ha│Soja   │10/02/2027 │Pelo plano│2026/27 ›  │ esmaecida
│ │☐ │   T1-A         │          │          │           │160 ha│Milho  │10/07/2027 │Pelo plano│—          │
│ │  │   T1-B         │          │          │           │152 ha│Soja   │20/02/2027 │Pelo plano│2026/27 ›  │ esmaecida
│ │  │ T3 Planejar ›  │A conferir│96 ha     │18/02/2027 │—     │Soja   │17/02/2027 │Estimado  │2026/27 ›  │ folha: ocupação de fora esmaecida
│ │  │ T7             │Perene    │—         │—          │—     │Mamão F│sem fim    │Perene    │2026/27 ›  │
│ │  │ Total                                            │553 ha│                                           │
│ └── coluna 1 presa; Variedade, Plano, Versão, Plantio, Meta, Ajustes e Tipo rolam dentro da caixa ───────│
├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ P1: a soja da Safra 2026/27 sai por estimativa em 08/03/2027 (sem plano); o feijão desta safra entra em   │
│ 15/04/2027.  Informar colheita de P1 na Safra 2026/27 ›                                                    │
│                                                        [ avanço da etapa 2 (rótulo do paralelo) ]          │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**390 × 844**, medidas reais da grade corrigida (exec. pela revisão: `../rev/d2_fc.txt`): trilho do menu 0-68 px; caixa de 266 px a partir de x=96; seleção 32 px; Talhão cerca de 120 px; cerca de 114 px para a Situação (98 px a 360 × 800). Área livre e Livre a partir de aparecem com uma rolagem da caixa. Grupos recolhidos abaixo de 1024 px (`G2_ESTREITO`, `g2lib.js:244`).

```
┌──┬─ Safrinha 2027 · Santa Rita ──────────┐
│≡ │ Talhões e cultivos                     │
│  │ Nesta safra 553 · Livre 152 ·          │
│  │ A conferir 380 · Perene 80 · de 1.165  │
│  │ [Todas 8][A conferir 4][Perene 2] →    │ chips com rolagem própria
│  │┌──┬──────────────┬──────────┬─ →       │
│  ││☐ │Talhão        │Situação  │ Área l.  │
│  ││  │▸ T1 Planejar›│Livre     │          │
│  ││  │▸ T2          │Planejado │          │
│  ││  │ T3 Planejar ›│A conferir│          │
│  ││  │ T4 Planejar ›│A conferir│          │
│  ││  │▸ P1          │A conferir│          │
│  ││  │ P2 Planejar ›│A conferir│          │
│  ││  │ T7           │Perene    │          │
│  ││  │ C1           │Perene    │          │
│  │└──┴──────────────┴──────────┴─         │
│  │ nota curta (motivo também na dica da Situação)
│  │ [ avanço ]                             │
└──┴────────────────────────────────────────┘
```

Se o rótulo mais longo de Situação mais o cabeçalho "SITUAÇÃO ⇅ ▾" não couberem em 98 px, usar abreviação com o texto inteiro em `title`/`aria-label` (OC-18).

**Painel "Planejar T1"** (lateral a 1440; tela cheia a 390, Salvar preso no rodapé)

```
┌ Planejar T1 ─────────────────────────────────── ✕ ┐
│ Santa Rita · Safrinha 2027 · T1 312 ha             │  contexto herdado, só leitura
│ Livre: 152 ha a partir de 21/02/2027 (folga 1 dia) │
│ Cultura   [Milho ▾]                                │  CD-02 (lista, como hoje)
│ Variedade [Híbrido AG 8700 ▾]                      │
│ Plano     [Milho safrinha v4 ▾]                    │  antes do Plantio (DONO-05)
│ Plantio   [21/02/2027]                             │  padrão = PlantioMin
│           Plantio a partir de 21/02/2027 com este plano
│ Parcela   [T1-B]                                   │  sugerida (R-19)
│ Área      [152] ha            máximo 152 ha        │  teclado numérico
│ Colheita prevista 11/07/2027 · do plano            │  sem plano: campo de data editável
│ Meta      [170] [sc/ha ▾]                          │
│ Ocupação prevista: 21/02/2027 a 11/07/2027         │  ao vivo
│                         [Cancelar] [ Salvar ]      │
└────────────────────────────────────────────────────┘
```

**Painel "Vincular ciclo C1"** (R-24): cultura, cultivar, plantio real, área e faixa do ciclo, travados; pede Plano (opcional), Meta e Unidade da meta (padrão do CD-02).

---

## 3. Colunas, árvore, filtros e faixa

### 3.1 Colunas, nesta ordem

As cinco primeiras respondem "onde, quanto e quando". Cultura, Ocupa até, Fim por e Safra vêm logo depois, para responder "o que ocupa e até quando" sem rolar (§1, pergunta 2).

| # | Coluna | Linha do talhão (nível 0) | Cultivo desta safra | Ocupação de fora (esmaecida, só leitura) |
|---|---|---|---|---|
| 1 | **Talhão ou parcela** (presa) | nome + `Planejar ›` (Área livre > 0 e safra editável), `Vincular ciclo ›` (R-24) ou `Dividir` (só desta safra) | nome + `Dividir` no talhão inteiro | nome |
| 2 | **Situação** | Sobreposição · A conferir · Livre · Planejado · Perene · Ocupado (R-10) | vazia, salvo alerta próprio: A conferir ou Sobreposição | vazia, salvo alerta próprio |
| 3 | **Área livre** | "152 ha" ou "—" | — | — |
| 4 | **Livre a partir de** | data (com "est." se depender de estimativa) · "sem data" · "—" | — | — |
| 5 | **Área** | Σ desta safra, entra no total ("—" se zero) | "160 ha" | "152 ha", fora do total |
| 6 | Cultura | culturas desta safra; na folha com uma ocupação de fora, a dela | sim | sim |
| 7 | **Ocupa até** | — (folha: a da ocupação de fora) | data · "sem fim" · "sem data" | idem |
| 8 | **Fim por** | — | Pelo plano · Colheita informada · Observado · Estimado (ciclo) · Sem ciclo · Perene | idem |
| 9 | **Safra** | — | — (a safra aberta já está no cabeçalho) | link "Safra 2026/27 ›" → `#saf=S2627&passo=cultivos` |
| 10 | Variedade | idem Cultura | sim | sim |
| 11 | Plano agronômico | como `grpParts` | como `leafParts` (Aplicar plano, Ajustar insumos) | só o nome |
| 12 | Versão | como hoje | como hoje | como hoje |
| 13 | Plantio | faixa de datas desta safra | data | data |
| 14 | Meta | "por parcela" | "170 sc/ha" | — |
| 15 | Ajustes locais | Σ | como hoje | — |
| 16 | Tipo | "Talhão inteiro" · "N parcelas" (só desta safra) · "—" | Talhão inteiro · Parcela | Talhão inteiro · Parcela |

- **Área:** formato vigente da grade (`d=2, dmin=0`, `g2lib.js:7`): "152 ha", "29,92 ha".
- **Ajuda no cabeçalho "Fim por":** "Pelo plano e Colheita informada são previsões. Estimado: ciclo da cultivar ou plano mais longo da cultura (CD-02), sem plano no cultivo. Observado: colheita registrada."
- **"Fim por" e "Ocupa até":** visíveis a partir de 1024 px; abaixo, alcançáveis com rolagem.
- **Troca aceita:** a 1440, Plano agronômico sai da vista; "Aplicar plano" continua na barra de lote e no menu da linha.

### 3.2 Árvore

- **Nível 0:** todo talhão ativo da fazenda da safra (na S2526, R-20).
- **Filhos:** os cultivos desta safra e as ocupações de fora **visíveis** pela R-12.
- **Folha** quando: (a) um único cultivo desta safra, de talhão inteiro, e nenhuma filha de fora visível; (b) nenhum cultivo desta safra e no máximo uma ocupação de fora visível — a linha do talhão mostra, esmaecidos, Cultura, Variedade, Ocupa até, Fim por e Safra dela, sem seleção e fora das contas.
- **Grupo** nos outros casos: aberto a 1440, recolhido abaixo de 1024 px.
- **Ordem:** a do CD-01; no grupo, filhas por data de início.
- **Linhas com grupos abertos (exec.):** S2627 18 (hoje 10; 15 sem e4/e5), S27SF 15 (hoje 9), safra do caso 5 15, 2027/28 8.

### 3.3 Filtro rápido e busca

- O filtro rápido usa a Situação **só do nível 0** (`qf.nivel0`): a soma dos chips é igual a Todas.
- Valores por safra: §6.1.
- Custo aceito: o chip Planejado não mostra um talhão Livre que tem uma parcela planejada (T1 na S27SF). A coluna Cultura e a busca continuam valendo nas filhas.

### 3.4 Faixa de resumo (substitui o `k2`, `safra.js:835`)

**"Nesta safra X · Livre Y · A conferir Z · Perene P · Ocupado W · de T ha · N sucessão(ões) a conferir"**

- As cinco parcelas somam T (R-09). Parcela de 0 ha é omitida, para caber a 390 px; "Nesta safra" sempre aparece.
- "Nesta safra" corresponde ao chip Planejado; a faixa soma **hectares por classe**, os chips contam **talhões pela Situação**. Um talhão Livre pode ter hectares de outra safra (T1 no caso 5).
- "N sucessão a conferir" = talhões em A conferir sem área a conferir (R-10, item 2b). Chip A conferir = talhões com área a conferir + talhões com sucessão a conferir.
- Com dado antigo em Sobreposição por soma (R-10, item 1), a faixa ganha "· N ha em sobreposição" logo depois de "de T ha": N = Σ por talhão da maior soma certa acima da área. As cinco parcelas continuam somando T (a Perene vai só até o resíduo), então sem esse trecho o excesso sumiria do resumo (SAF-C01).

**Fonte única dos números de faixa (exec., `saida_ocupacao_f1.txt`; iguais com e sem e4/e5):**

| Safra | Nesta safra | Livre | A conferir | Perene | Ocupado | Cultiváveis | Sucessões a conferir |
|---|---|---|---|---|---|---|---|
| S2627 (2026/27) | 1.165 | 0 | 0 | 0 | 0 | 1.165 | 1 (P1) |
| S27SF (Safrinha 2027) | 553 | 152 | 380 | 80 | 0 | 1.165 | 1 (P1) |
| Nova 10/01–30/08/2027 (caso 5 de `acao_unica_test.py`) | 0 | 450 | 475 | 80 | 160 | 1.165 | 0 |
| Nova 2027/28 (01/09/2027–31/08/2028) | 0 | 1.085 | 0 | 80 | 0 | 1.165 | 0 |
| LG2627 (sintética) | 1.285,23 | 0 | 0 | 0 | 0 | 1.285,23 | 0 |
| Nova da Boa Vista (2026/27) | 0 | 120 | 0 | 0 | 0 | 120 | 0 |
| Nova da Lagoa 2027/28 | 0 | 0 | 0 | 1.285,23 | 0 | 1.285,23 | 0 |
| Nova da Lagoa 2026/27 (cruza a LG2627) | 0 | 0 | 0 | 1.285,23 | 0 | 1.285,23 | 0 |

---

## 4. Regras numeradas e testáveis

Todas as funções abaixo existem uma vez, em `ocupacao.js`/`ocupacao.py` (ENG-011).

**R-01 · Talhões.** A tabela traz os talhões **Ativos** do CD-01 da fazenda da safra aberta. Negativo: nenhum talhão de outra fazenda; a LG2627 nunca oferece o T1.

**R-02 · Ocupação.** Cada cultivo de qualquer safra da mesma fazenda, inclusive desta, com faixa (nome da parcela, ou o talhão inteiro), área, início, Ocupa até, fim por, núcleo e P(o).

**R-03 · Início.**
- Com plano: plantio + o menor DAP negativo do plano (SOJA-AT −20, SOJA-PD −15, MAMAO-IMP −60).
- Gatilho DATA conta só se cair dentro do período da safra do cultivo **e** não antes de plantio − maior antecedência do plano. Fora disso não muda o início, e a linha mostra o aviso "O plano <id> tem datas fixas fora desta safra (ex.: 15/10/2026). Revise o plano ou troque o gatilho para DAP/DAPC." DANC e DAPC não entram no início.
- Sem plano: o plantio.

**R-04 · Ocupa até (último dia ocupado) e "Fim por", nesta ordem:**
- (a) **Perene** (classe do CD-02, `dados_cad.py:31-32`): "sem fim". Nesta fatia o ciclo perene não termina (FORA-DE-ESCOPO).
- (b) **Observado:** colheita real registrada. Nesta fatia o serviço aceita o campo `colheita_real`; não há tela que o grave e os dados não o usam.
- (c) **Pelo plano:** a maior data entre as atividades do plano (com o filtro de DATA da R-03) e a colheita informada.
- (d) **Colheita informada:** sem plano, a colheita prevista digitada no painel (DONO-07).
- (e) **Estimado (ciclo):** sem plano e sem colheita: plantio + o maior entre o ciclo da cultivar (`areas/cadastros.py:406-408`) e a última atividade relativa (DAP/DANC/DAPC) dos planos publicados da mesma cultura. Ex. (exec.): c5 (62 X) = 22/10/2026 + máx(112, 118) = 17/02/2027.
- (f) **Sem ciclo:** cultura sem ciclo cadastrado e sem plano publicado: "sem data".
- (b), (c) e (d) são previsões, menos o Observado. Só o Observado é fato.

**R-05 · `colheitaDe` não serve como fim** (T7 "acabaria" em 10/03/2025). Negativo: T7 e C1 com "sem fim".

**R-06 · Liberação (CAL-14, PRD.md:4393).**
- `liberacao(o, modo) = Ocupa até(o, modo) + folga`. Folga é parâmetro do dono, em dias, **padrão 1** (dia seguinte); 0 = plantio no dia da colheita, atrás da colhedora. A tela mostra a folga ao lado da data.
- `ativo(o, x, modo) = início ≤ x < liberacao(o, modo)`. Modos: `est` (Ocupa até) e `pior` (P(o)).
- Livre a partir de é a liberação da **área**, não o dia de plantio: com plano, vale a R-17.
- A data de colheita é o início da colheita; a duração dela fica fora (FORA-DE-ESCOPO).

**R-07 · Mesmo ciclo.** Mesmo `v.ciclo` (gravado pelo Vincular ciclo) é **uma** ocupação: conta uma vez e nunca conflita consigo mesma. Sem `v.ciclo`, no protótipo, a chave é fazenda + faixa + cultura + plantio. Em produção, a identidade é o id do ciclo com vigência própria (RF-DAT-003, PRD.md:2482; FO-01, PRD.md:2311).

**R-08 · Fim no pior caso, P(o) (OC-R1).**
- Perene: sem fim. Observado, Pelo plano e Colheita informada: Ocupa até.
- Estimado: o maior entre o fim da safra do cultivo e o fim estimado.
- Sem ciclo: o maior entre o fim da safra e plantio + o maior ciclo da cultura no CD-02; sem ciclo na cultura, sem fim até alguém informar a colheita.

**R-09 · Área livre, Livre × A conferir e faixa.**
- Os cultivos desta safra reservam a área deles por todo o período desta safra. As ocupações de fora entram com `ativo`.
- m(d) = mín sobre x ∈ [d, fim desta safra] de (T − área desta safra − Σ de fora ativas em x). A Área livre é o **primeiro** m(d) > 0,005 ha, e o d é Livre a partir de.
- Conta m(d) duas vezes: modo `pior` dá o **Livre**; modo `est` menos o `pior` dá o **A conferir**, com Livre a partir de estimado ("sem data" quando a de fora é Sem ciclo).
- Se a data do Livre vier do P(o) de uma ocupação estimada, a área é A conferir, com a data estimada.
- Faixa: Perene = área de perenes de fora até o resíduo de cada talhão; Ocupado = T − Nesta safra − Livre − A conferir − Perene.

**R-10 · Situação do talhão**, pela primeira condição verdadeira:
1. **Sobreposição:** existe trava (R-14) entre ocupações que cruzam o período. Só acontece com dado antigo.
2. **A conferir:** (a) há área a conferir (R-09); ou (b) no mesmo talhão e na mesma faixa (ou talhão inteiro), um cultivo desta safra e uma ocupação de outra safra estão em sucessão e o fim do que vem primeiro é Estimado ou Sem ciclo, com o segundo começando antes do P(o) do primeiro — **nos dois sentidos**; ou (c) um cultivo desta safra tem pendência de sobreposição prevista (R-15).
3. **Livre:** Área livre > 0.
4. **Planejado:** há cultivo desta safra.
5. **Perene:** um perene de outra safra ocupa o talhão.
6. **Ocupado:** nenhuma das anteriores.
- A célula Situação "A conferir" traz o motivo como dica (`title`/`aria-describedby`), por ex. "Sucessão a conferir: soja sem fim confirmado (08/03/2027 est.) antes do feijão em 15/04/2027".

**R-11 · Situação das filhas:** vazia, salvo o alerta próprio (A conferir ou Sobreposição). A natureza da filha está em Safra e Fim por (REG-06).

**R-12 · Filhas de fora visíveis:** as que cruzam o período (início ≤ fim desta safra e P(o) + folga > início desta safra) **e**:
- (a) não estão escondidas pela faixa: só se esconde quando esta safra usa a mesma faixa (mesmo nome) ou tem cultivo de talhão inteiro no talhão. Uma ocupação de fora de talhão inteiro continua visível enquanto esta safra só tiver parcelas; **ou**
- (b) são a imediatamente anterior ou posterior, na mesma faixa ou no talhão inteiro, a um cultivo desta safra.
- Negativo: mesma faixa, ocupação de fora não adjacente: escondida.
- Ocupação escondida que causa A conferir ou Sobreposição é citada na nota (§5.1).

**R-13 · Fora das contas e nunca gravadas.**
- Linhas de talhão, folhas de fora e filhas `r.fora` não entram em: total da Área (`g2sum`, `g2lib.js:94`), faixa "Nesta safra", `leaves()`, seleção, lote, ocorrências, demanda, R$/kg e contagem da etapa 1.
- O estado `g_cult_*` guarda só cultivos desta safra. `syncTalhoes` monta a exibição sobre cópia; os gravadores aplicam `soDaSafra(rows)`, que remove `livre`/`fora` em todos os níveis e desfaz grupos só de exibição (REG-09).
- Negativo: a paridade de `saf_cmp_continuidade_test.py:147-153` não muda.

**R-14 · Trava (impede salvar; nada é gravado).** Dano evitado: insumo e O.S. emitidos para área fisicamente ocupada (dinheiro e estoque), ou operação sobre lavoura já confirmada no campo. Só entra o que é certo:
- **Núcleo** = [plantio, fim certo]. Fim certo: perene, sem fim; Observado, a colheita real; senão, o menor entre Ocupa até e plantio + **ciclo mínimo da cultura** − 1 (menor ciclo das cultivares no CD-02: soja 112, milho 140, feijão 90). Cultura sem ciclo: só o dia do plantio. O ciclo mínimo é decisão técnica que o Codex revisa e não substitui a colheita informada.
- **T-área (regra de hoje, `safra.js:527-537`):** Σ das áreas desta safra no talhão > área + 0,005 ha.
- **T-faixa:** mesma faixa ou talhão inteiro, núcleos cruzados contando a folga (`[plantio, núcleo + folga)`, sempre com o dia do plantio: cultura sem ciclo com folga 0 ocupa o dia), e pelo menos uma das duas com plano aplicado ou perene.
- **T-soma:** num mesmo dia, a área física em núcleo > área + 0,005 ha, com plano em alguma. Área física: na mesma faixa conta a maior área; talhão inteiro cobre o talhão. Conferida em todos os dias, sem horizonte: a varredura vai de evento em evento (plantio, fim do núcleo, início e liberação), e uma perene ou ocupação antiga no talhão não a encurta, nem um par antigo na mesma faixa (dado antigo). O dia só sai da soma do cultivo quando ele mesmo está na mesma área de outra ocupação em núcleo com plano (a T-faixa cobre esse par). SAF-C01; a pendência de soma da R-15 usa a mesma varredura e a mesma área física.
- **T-observado:** atividade da nova antes da colheita real registrada da outra, na mesma faixa.
- Onde roda: salvar Planejar e Vincular; editar área, plantio, plano ou colheita; Dividir; Aplicar plano (linha e lote). Excluir não trava.
- Mensagem: fato, dano e saída (§7.3). Pior dia = nos dias de núcleo do cultivo, o de maior área física dos outros em núcleo (o critério da T-soma). Período citado = do maior início ao menor Ocupa até entre o cultivo e quem está no pior dia (com duas ocupações, a interseção dos dois períodos). "Máximo X ha" = área − ocupação no pior dia; com a T-área, também o que sobra desta safra; arredondado para baixo, e regravar com ele não trava pela área. Sem fim (só perenes): "A partir de dd/mm/aaaa, …" (SAF-C01 e verificação de 09/10/2026: com três ocupações o período saía invertido e o máximo não destravava).

**R-15 · Pendência e aviso (salva).** Previsões que se cruzam não travam (PRD 39.4, PRD.md:6683-6685; SAFRA-08, PRD.md:6731).
- **Sobreposição prevista:** os períodos `[início, liberacao(est))` se cruzam na mesma faixa (ou a soma diária prevista passa da área) e os núcleos não. O plano é aplicado, o cultivo entra na demanda e a linha fica A conferir com "Sobreposição prevista: N dias (<atividade> dd/mm × <cultura> até dd/mm)".
  - A pendência fica no de plantio mais tardio. Quando a antecessora recebe plano, a pendência vai para a sucessora; a antecessora nunca é bloqueada.
  - Some quando as datas deixam de se cruzar ou quando a colheita real da anterior é registrada antes da atividade.
  - Ações na nota: "Mudar plantio ›" (abre o painel com PlantioMin) e "Informar colheita de <talhão> na <safra> ›" (DONO-07).
- **Aviso ao salvar** quando a anterior tem fim Estimado ou Sem ciclo e a nova começa antes do P(o) dela: "provável sobreposição (N dias)" se cruza a estimativa; "saída de <cultura> estimada em dd/mm; confirme a colheita" se não cruza; "não conferida" se Sem ciclo. O aviso também aparece ao salvar o Planejar.
- Proteção física de verdade (sucessora só libera O.S. com colheita real da antecessora) fica na liberação, CMD-06 (FORA-DE-ESCOPO).

**R-16 · Lote.** Aplicar plano mostra no painel, antes de confirmar, quem trava (não recebe) e quem recebe com pendência. O botão vira "Aplicar plano em N cultivos". O aviso final lista os dois grupos.

**R-17 · PlantioMin (sucessão).**
- PlantioMin = menor data ≥ Livre a partir de + maior antecedência do plano (`max(0, −menor DAP)`) sem trava **nem** pendência contra **todas** as ocupações do talhão, inclusive as sucessoras de outra safra.
- Sem plano, ou plano sem atividade antes do plantio: PlantioMin = Livre a partir de.
- O painel recalcula ao trocar o plano enquanto a pessoa não digitou a data; se ela digitou uma data menor, não sobrescreve e mostra o aviso com a data mínima.
- Sem janela antes do fim da safra: a mensagem dá o fato e a saída dupla (§7.3, P3).
- Parcelas que liberam em datas diferentes: usa a faixa sugerida (R-19); sem faixa, o dia em que a soma diária comporta a área.

**R-18 · Perene.** Perene de outra safra não tem Planejar; tem **Vincular ciclo ›** nas condições da R-24, senão a linha fica sem ação. Na safra dele, o perene é editável como hoje (plano, meta, ajustes), sem simular novo plantio (PRD.md:6662).

**R-19 · Parcela.** Área igual à do talhão gera talhão inteiro; menor, parcela. Nome sugerido: a faixa de fora que libera exatamente essa área no dia de Livre a partir de (T1-B depois do c2); senão `nextNome`, sem repetir as faixas desta safra nem as do talhão ainda ocupadas no início dela, inclusive as de ocupações futuras (SAF-C01: um café numa safra de 2020 não recebe a parcela da soja de 2027). Editável. Dividir continua como hoje (DEC-2609-01, PRD.md:12216), com R-14 por parcela e a capacidade do serviço: área − maior área física de fora em núcleo nos dias de núcleo das parcelas. Resumo ("outras safras N ha"), selo, "+ Adicionar parcela" (nome e área), "Distribuir área igualmente" e a recusa de área (agregada: quem ocupa, soma das parcelas e máximo) saem dela. A área livre do aviso depois de gravar ou dividir é a da coluna Área livre (R-09), a mesma do painel.

**R-20 · Safra encerrada.** Consulta só dos cultivos dela: sem linha de talhão, sem Planejar, sem Dividir (`safra.js:296`); Situação, Área livre e Livre a partir de "—"; Plantio, Ocupa até, Fim por e Safra preenchidos.

**R-21 · Fazenda herdada.** O cultivo novo grava a fazenda da safra; a safra nova acha a fazenda pelo id real. Negativo: cultivo na safra da Boa Vista nunca grava "Santa Rita".

**R-22 · Safras novas separadas.** `cultsDe(self, safId)` é a única fonte das linhas de uma safra; na grade `g_cult_NOVA`, linhas com `v.saf` diferente da safra aberta ficam escondidas (fora da tabela, do `g2sum`, da seleção e da lixeira), sem apagar dado. Negativo: duas safras novas não dividem cultivos, ocupação, contagem da etapa 1 nem lote.

**R-23 · Seleção e lixeira** só nas linhas desta safra.

**R-24 · Vincular ciclo (PL-01, PRD.md:561; DEMO-09, PRD.md:4717).**
- Aparece na linha Perene de outra safra quando: a safra aberta é editável, é da mesma fazenda, e **nenhuma safra que já contém o ciclo cruza o período desta**. Dano evitado pela condição: insumos do perene contados duas vezes no mesmo período (S2).
- Cria nesta safra um cultivo com a mesma fazenda, faixa, área, cultura, cultivar e plantio real do ciclo, `v.ciclo` = id de origem, **sem plano, sem colheita**, `ro=False`. O painel pede Plano (opcional), Meta e Unidade. O plano não é copiado (copiar dobraria a demanda e levaria datas fixas de outra safra).
- Vincular duas vezes o mesmo ciclo na mesma safra é recusado.
- Se a condição falhar, a linha fica Perene sem ação e a nota diz "Ciclo na <safra> ›".

**R-25 · Estado só de perenes.** Safra sem cultivo, sem área livre ou a conferir, só com perenes de outra safra que cruza o período (Lagoa nova 2026/27): nota "Todos os talhões estão com perenes da <safra> neste período (N ha). Planeje por ela ›", sem primária e sem avanço.

---

## 5. Ações

### 5.1 Área de ações da etapa 2 (uma primária por estado, `safAcoes`)

| Estado (precedência) | Nota | Primária | Avanço |
|---|---|---|---|
| Correção pedida pela revisão | como hoje (`safra.js:886-889`) | como hoje | Voltar à revisão |
| Sobreposição (dado antigo) | "Sobreposição em P2: …", as duas ocupações e a data | "Corrigir P2" | secundário |
| Nenhum cultivo nesta safra | "Nenhum cultivo nesta safra: 2 talhões livres (450 ha), 4 a conferir (475 ha)[, N ciclos perenes a vincular]. Use Planejar › [ou Vincular ciclo ›] na linha." · ou R-25 | nenhuma | nenhum |
| Seleção ativa | como hoje | barra da lista | secundário |
| Cultivos sem plano | como hoje + frase de A conferir/pendência (abaixo) | Aplicar plano em N cultivos | secundário |
| Tudo com plano | frase de A conferir/pendência, se houver | avanço da etapa 2 (rótulo do paralelo) | — |
| Safra encerrada | — | Ver a etapa seguinte | — |

**Frase de A conferir/pendência** (em qualquer estado, depois da nota de precedência; até 3 talhões e "+N"):
- S2627: "P1: o Feijão da Safrinha 2027 começa em 15/04/2027; a saída da soja é estimada em 08/03/2027 (sem plano, CD-02). Informar colheita de P1 ›"
- Pendência: "P2: sobreposição prevista de 11 dias com o Milho da Safra 2025/26 (até 15/11/2026). Mudar plantio › · Informar colheita de P2 na Safra 2025/26 ›" (a 2025/26 é encerrada: a ação vira "Ver P2 na Safra 2025/26 ›" e a nota diz que a confirmação depende de quem responde por ela).
- A ação "Informar colheita" abre `#saf=<id>&passo=cultivos&cult=<cultivo>` com o painel desse cultivo aberto.

### 5.2 Ações por linha (não contam como duplicata: `ferramentas/acoes_duplicadas.py` exclui `[role=row]`)

| Ação | Onde | O que faz |
|---|---|---|
| **Planejar ›** | talhão com Área livre > 0 | Painel do §2. Ao salvar, a linha vira Planejado ou a sobra continua Livre. Aviso: "Cultivo incluído como parcela T4-A · 104 ha livres em T4", mais o aviso da R-15. |
| **Vincular ciclo ›** | perene de outra safra, R-24 | Painel de vínculo; o cultivo entra em "Cultivos sem plano". |
| **Dividir** | talhão inteiro ou grupo desta safra sem área livre | Como hoje; o clique no grupo também abre (`dr='div_<t>'`). |
| **Aplicar plano / Reaplicar / Ajustar insumos** | cultivos desta safra | Como hoje, com R-14, R-15 e R-16. |
| **Clique na linha** | cultivo desta safra | Painel em edição; Colheita prevista editável se sem plano. |
| **Safra 2026/27 ›** | coluna Safra | Abre a outra safra em `passo=cultivos`. |
| **Lixeira** | linhas desta safra | Como hoje; a área volta a Livre. |

**Fim do "Adicionar cultivo"**, sem substituto genérico:

| Caso que o botão cobria | Caminho agora |
|---|---|
| Talhão livre | Planejar › |
| Talhão com cultivo e sobra | Planejar › (cria a parcela; o desvio `safra.js:541` deixa de existir) |
| Talhão cheio | Dividir |
| Ciclo perene existente em safra nova | Vincular ciclo › |
| Talhão de outra fazenda | Impossível |
| Talhão que não existe | Cadastrar no CD-01 (PRD.md:1672); aparece no Planejar com o PR-C |

---

## 6. Dados de demonstração

### 6.1 Fonte única de períodos e situações (exec., folga 1, com e4/e5; `saida_ocupacao_f1.txt`)

**Períodos (Santa Rita):**

| Cultivo | Safra | Faixa | Início | Plantio | Ocupa até | Fim por | Núcleo até | P(o) |
|---|---|---|---|---|---|---|---|---|
| c1 | 2026/27 | T1-A | 25/09/2026 | 15/10/2026 | 10/02/2027 | Pelo plano | 03/02/2027 | 10/02/2027 |
| c2 | 2026/27 | T1-B | 05/10/2026 | 25/10/2026 | 20/02/2027 | Pelo plano | 13/02/2027 | 20/02/2027 |
| c3 | 2026/27 | T2 | 28/09/2026 | 18/10/2026 | 13/02/2027 | Pelo plano | 06/02/2027 | 13/02/2027 |
| c4 | 2026/27 | T4 | 20/10/2026 | 20/10/2026 | 15/02/2027 | Estimado | 08/02/2027 | 31/08/2027 |
| c5 | 2026/27 | T3 | 22/10/2026 | 22/10/2026 | 17/02/2027 | Estimado | 10/02/2027 | 31/08/2027 |
| c6 | 2026/27 | P1 | 10/11/2026 | 10/11/2026 | 08/03/2027 | Estimado | 01/03/2027 | 31/08/2027 |
| c7 | 2026/27 | P2 | 25/11/2026 | 25/11/2026 | 23/03/2027 | Estimado | 16/03/2027 | 31/08/2027 |
| c8 | 2026/27 | T7 | 10/03/2025 | 10/03/2025 | sem fim | Perene | sem fim | sem fim |
| c9 | 2026/27 | C1 | 15/01/2019 | 15/01/2019 | sem fim | Perene | sem fim | sem fim |
| d1 | Safrinha 2027 | T1-A | 20/02/2027 | 20/02/2027 | 10/07/2027 | Pelo plano | 09/07/2027 | 10/07/2027 |
| d2 | Safrinha 2027 | T2 | 25/02/2027 | 25/02/2027 | 15/07/2027 | Pelo plano | 14/07/2027 | 15/07/2027 |
| d3 | Safrinha 2027 | P1 | 15/04/2027 | 15/04/2027 | 14/07/2027 | Pelo plano | 13/07/2027 | 14/07/2027 |
| e4 | 2025/26 | P1 | 05/07/2026 | 05/07/2026 | 10/10/2026 | Colheita informada | 02/10/2026 | 10/10/2026 |
| e5 | 2025/26 | P2 | 10/08/2026 | 10/08/2026 | 15/11/2026 | Colheita informada | 15/11/2026 | 15/11/2026 |

(e1–e3 terminam em fev–mar/2026 e não cruzam nenhuma safra aberta.)

**Situação e Livre a partir de por talhão:**

| Talhão | S27SF | S2627 | Caso 5 | 2027/28 |
|---|---|---|---|---|
| T1 | Livre 152 ha · 21/02/2027 | Planejado | Livre 152 ha · 21/02/2027 | Livre 312 · 01/09/2027 |
| T2 | Planejado | Planejado | Livre 298 ha · 16/07/2027 | Livre 298 · 01/09/2027 |
| T3 | A conferir 96 ha · 18/02/2027 est. | Planejado | A conferir 96 · 18/02/2027 est. | Livre 96 · 01/09/2027 |
| T4 | A conferir 204 ha · 16/02/2027 est. | Planejado | A conferir 204 · 16/02/2027 est. | Livre 204 · 01/09/2027 |
| P1 | A conferir (sucessão c6 → d3) | A conferir (sucessão c6 → d3) | A conferir 95 · 15/07/2027 | Livre 95 · 01/09/2027 |
| P2 | A conferir 80 ha · 24/03/2027 est. | Planejado | A conferir 80 · 24/03/2027 est. | Livre 80 · 01/09/2027 |
| T7 | Perene | Planejado | Perene | Perene · Vincular ciclo › |
| C1 | Perene | Planejado | Perene | Perene · Vincular ciclo › |
| **Chips** | A conferir 4 · Perene 2 · Livre 1 · Planejado 1 | Planejado 7 · A conferir 1 | A conferir 4 · Livre 2 · Perene 2 | Livre 6 · Perene 2 |

Outras safras: Boa Vista nova = B1 Livre 120 ha desde 01/09/2026. Lagoa nova 2027/28 = 23 pivôs Perene, 23 "Vincular ciclo ›", 0 Planejar. Lagoa nova 2026/27 = 23 Perene sem ação (R-25). S2526 = e1–e5 em consulta.

**Filhas de fora visíveis (R-12):** S2627 — d1 (T1-A, sucessor do c1), d2 (T2), d3 e e4 (P1), e5 (P2). S27SF — c1 (antecessor do d1) e c2 (T1-B) no T1, c3 no T2, c6 no P1; T3, T4, P2, T7 e C1 são folhas com c5, c4, c7, c8 e c9.

### 6.2 Incoerências corrigidas nesta fatia

1. **Lavouras em campo fora de qualquer safra** (`dados.py:12-13`; Mapa `areas/inicio.py:189-190, 198`; MIP `dados_mip.py:82-83`; irrigação `dados_irrigacao.py:88, 91`). Entram em `dados2.py:78-80` (PR-B1), metas de `inicio.py:198`:
   ```
   C('e4','P1','Talhão inteiro','Feijão','BRS Estilo',95,'2026-07-05',48,'sc/ha',None,colheita='2026-10-10',ro=True)   + origem='lavoura em campo'
   C('e5','P2','Talhão inteiro','Milho','Híbrido AG 8700',80,'2026-08-10',180,'sc/ha',None,colheita='2026-11-15',ro=True) + origem='lavoura em campo'
   ```
   - O serviço lê a ocupação por faixa e período, nunca pelo id da safra; OC-U7 prova o mesmo resultado com e5 na S2526 ou numa lista `OCUPACOES` sintética.
   - Provisório até a decisão da S2526 (DECISOES, Pendentes). Até lá, a colheita prevista do e5 só muda em `dados2.py`.
   - Efeitos: S2526 passa a 5 cultivos e 881 ha (PL-01, `areas/planejamento.py:147`; CD-01det de P1 e P2, `areas/cad_fazendas.py:455`); uso de cultivar no CD-02 +1 em AG 8700 e BRS Estilo (`areas/cadastros.py:401-404`); demanda não muda (`dados2.py:132-134`); plantio do c7 não muda.
2. **Fazenda da safra nova** vem do id real (`safra.js:299`) e o cultivo novo a herda (`safra.js:540`).
3. **Safras novas na mesma grade** separadas por `v.saf` e `cultsDe` (R-22).
4. **Fonte dos talhões** = CD-01, com o B1 (R-01).

**Verificado (exec., `saida_trava_f1.txt`):** nenhuma trava nem pendência nos dados atuais da Santa Rita e da Lagoa, com e sem e4/e5.

### 6.3 Registrar sem mexer
OS-0421, 0431, 0420 e 0415 com datas que contradizem o plano; OS-0417, 0418, 0419, 0422 e 0424 de P1/P2 marcadas na 2026/27 enquanto o Mapa diz 2025/26; S2526 "Encerrada" com lavoura em campo (PRD.md:563); T3 "pré-plantio" no MIP × "colhido" no Mapa; área cultivável maior que o polígono (T4 204 × 203,6 ha; P1 95 × 94,7 ha); plantio parcial do T4 (SAFRA-06); ciclo antigo do Pivô 12 sem erradicação registrada (o lg12 já é o ciclo novo); soma dos pivôs (1.285,23 ha) maior que a área consolidada (1.156,71 ha), dado sintético.

---

## 7. Testes

### 7.1 Novos

**`ocupacao_unit.py`** (JS × Python, sem navegador)

| ID | Caso | Esperado |
|---|---|---|
| OC-U1 | Períodos dos cultivos da Santa Rita | Tabela de períodos do §6.1 |
| OC-U2 | Faixas | Tabela do §3.4, cinco parcelas somando T |
| OC-U3 | Situação e chips (nível 0) | §6.1; soma dos chips = Todas |
| OC-U4 | Mensagens | Textos exatos do §7.3 |
| OC-U5 | Propriedades, 400 sequências de 3 salvamentos, semente 20261005, folga 0/1/3 | Trava simétrica; nunca dois núcleos cruzados na mesma faixa com plano entre aceitos; soma diária dos núcleos ≤ área; faixa = T; chips = Todas; P(o) ≥ fim estimado; perene sem fim; PlantioMin aceito sem trava nem pendência e PlantioMin − 1 com trava ou pendência; DATA fora da safra nunca muda início nem fim; mesmo ciclo em duas safras não conflita. **Exec. (amostra Python):** 1.200 salvamentos, 398 aceitos, 802 recusados, 0 falhas |
| OC-U6 | Paridade | JS = Python em todos os casos |
| OC-U7 | e5 na S2526 × e5 numa lista sintética | Mesma liberação (16/11/2026) e mesma pendência do c7 |
| OC-U8 | Casos de borda | Tabela do §7.3 (trava, pendência, aviso), com folga 1 e folga 0 |
| OC-U9 | Regressão de dados | Com os dados atuais, as faixas do §3.4 e a paridade de `saf_cmp_continuidade_test.py:147-153` não mudam |

**`ocupacao_test.py`** (navegador, 1440 e 390)

| ID | Caso | Esperado |
|---|---|---|
| OC-01 | Talhões | S27SF 8 talhões, nenhum pivô; LG2627 23 pivôs, nunca o T1; Boa Vista nova só o B1, Livre 120 ha |
| OC-02 | Tabela S27SF | Linhas do §6.1. Depois de Planejar T4-A (100 ha, 28/02/2027), o c4 continua visível e T4 fica A conferir 104 ha desde 16/02/2027 est. |
| OC-03 | Faixa | §3.4, com "1 sucessão a conferir" na S2627 e na S27SF |
| OC-04 | Chips | §6.1; soma = Todas; o chip Livre mostra T1 e, ao abrir, as filhas |
| OC-05 | Perene | **Negativo:** T7 e C1 sem Planejar e sem Vincular na S27SF e no caso 5 (a S2627 cruza). **Positivo:** na 2027/28, T7 e C1 com Vincular ciclo e sem Planejar; vincular C1 mantém plantio 15/01/2019 travado, faixa "Nesta safra 38 · Livre 1.085 · Perene 42"; C1 + T7 → "Nesta safra 80 · Livre 1.085"; a S2627 continua igual; o cultivo vinculado nasce sem plano; vincular duas vezes é recusado. Lagoa nova 2027/28: 23 Vincular; depois de vincular todos, "Nesta safra 1.285,23". Lagoa nova 2026/27: nota da R-25, nenhuma ação |
| OC-06 | Sucessão | Planejar T1 na S27SF: padrões 152 ha, 21/02/2027, T1-B; prévia "21/02/2027 a 11/07/2027"; salva. Faixa "Nesta safra 705 · A conferir 380 · Perene 80"; T1 Planejado |
| OC-07 | **Negativo**, área | T1 312 ha em 21/02/2027: M1, nada gravado. Em 11/07/2027: salva |
| OC-08 | Folga | T1-B 152 ha em 20/02/2027: com folga 1 salva com pendência de 1 dia (P1 do §7.3); com folga 0 salva sem pendência |
| OC-09 | Lote | S2627, SOJA-AT em T4, T3, P1 e P2: aplica nos 4; P2 fica A conferir com "Sobreposição prevista: 11 dias"; a demanda inclui o P2 (R$ 167.992,00); nenhum "sem plano" na nota; o ocupante (e5) está visível na linha antes da ação |
| OC-10 | Edição entre safras | Plantio do c1 em 30/10/2026: salva; pendência de 6 dias no d1 (P2 do §7.3); d1 visível no grupo T1 |
| OC-11 | Núcleo | T3 na S27SF: milho MILHO-SF em 10/02/2027 → M2; em 11/02/2027 salva com o aviso "provável sobreposição (7 dias)". Depois, SOJA-AT no c5 na S2627 recebe o plano e a pendência passa ao milho (7 dias) |
| OC-12 | Sai de A conferir | SOJA-AT no c6: P1 Planejado nas duas safras; chips da S2627 "Planejado 8" |
| OC-13 | Fora das contas e gravação | Total, faixa, seleção, lote e etapa 1 ignoram `fora`. Na S27SF: Planejar T1 → Salvar; Dividir T2 → Salvar; Aplicar plano; trocar de etapa duas vezes → nenhuma linha `fora`/`livre` em `state.g2['g_cult_S27SF'].rows`; T7 e C1 continuam folhas de fora; o número de filhas de fora não cresce; paridade da demanda idêntica |
| OC-14 | Sem botão | 0 `[data-acao=adicionar]` e 0 "Adicionar cultivo" no SAF, em todas as safras e estados |
| OC-15 | Fazenda e safras novas | Cultivo na Boa Vista grava Boa Vista. Safras novas N1 e N2; T1 planejado só na N1 → na N2: etapa 1 com 0 cultivos e 0 ha, T1 Livre, total 0, lote sem o cultivo da N1; na N1: 1 cultivo |
| OC-16 | Safra encerrada | S2526: 5 cultivos, sem Planejar nem Dividir, Situação "—" |
| OC-17 | Layout | **390 × 844 e 360 × 800**, por `getBoundingClientRect`: página sem rolagem lateral; seleção ≤ 40 px; cabeçalho e chip de Situação de todas as linhas visíveis inteiros sem rolar a caixa; Área livre e Livre a partir de inteiras depois de uma rolagem; "Planejar ›" na coluna presa, com foco à vista. **1440 × 900:** de Talhão a Safra (9 colunas) visíveis sem rolar (célula ≤ borda direita da caixa); registrar se Variedade cabe, sem prometer. Grupos recolhidos abaixo de 1024 px; painel em tela cheia a 390; no máximo uma primária |
| OC-18 | Acessibilidade | Situação com texto, não só cor; motivo do A conferir em `aria-describedby`; foco volta à linha depois de salvar; Esc no painel pede confirmação |
| OC-19 | Medição (AGENTS §3.3) | "Milho em 100 ha do T4 na Safrinha", a 390 e a 1440, no mesmo teste. **Antes:** rolar até a coluna Cultura, "Planejar talhão ›", Cultura, Variedade, Plantio, Meta, Salvar. **Depois:** "Planejar ›" (coluna presa), Cultura, Variedade, Área, Meta, Salvar (Plantio vem do PlantioMin). Contar toques, caracteres e rolagens laterais; registrar os números medidos, sem prometer antes |
| OC-20 | Lavoura em campo | CD-01det de P1 e P2 mostra o grupo 2025/26 com e4 e e5 em consulta |
| OC-21 | PlantioMin | Planejar T1 no caso 5 com SOJA-AT sugere 13/03/2027 e salva sem editar; trocar para MILHO-SF sem ter digitado volta a 21/02/2027. Na S27SF, T1-B: SOJA-AT 13/03, SOJA-PD 08/03, MILHO-SF e FEIJ-PV 21/02/2027. c7 com SOJA-AT sugere 06/12/2026; com SOJA-PD, 01/12/2026 |
| OC-22 | Colheita informada | Colheita 10/02/2027 no c4 (S2627, sem plano) → na S27SF, T4 Livre 204 ha desde 11/02/2027; chips "A conferir 3 · Livre 2 · Perene 2 · Planejado 1". Negativo: com plano, o campo é só leitura. Navegação: a ação da nota abre a S2627 em `passo=cultivos` com o painel do c4 aberto |
| OC-23 | Padrões não levam a recusa | (a) Planejar T3 na S27SF com os padrões (18/02/2027), depois SOJA-AT e SOJA-PD no c5: salvam sem pendência. (b) Planejar P2 com o padrão (24/03/2027), depois SOJA-AT no c7 com plantio 06/12/2026: M2 nomeando as duas ocupações e sem sugerir data que a trava recuse; a sugestão é a saída dupla P3 |

### 7.2 A adaptar (no mesmo PR, sem pular nem esconder caso)

- **`acao_unica_test.py:6`:** texto do modo saf.
- **`acao_unica_test.py:91-100` (caso 3):** entrada pelo "Planejar ›" do T3 na S27SF (`#saf=S27SF&passo=cultivos`); mantém painel sem trocar de etapa, Esc com "Há alterações não salvas" e "Continuar editando" preservando a variedade; acrescenta 0 `[data-acao=adicionar]`.
- **`acao_unica_test.py:102-106` (caso 4):** `'4 sem plano' in k2` passa a ler a nota (`:105`).
- **`acao_unica_test.py:107-112` (caso 5):** `prims==[]`, `avancos==0`, nota começa com "Nenhum cultivo nesta safra"; T7 e C1 Perene sem Planejar nem Vincular; T1 Livre 152 ha, 21/02/2027.
- **`acao_unica_test.py:120-134` (caso 7):** o lote aplica nos 4 (P2 com pendência); conferir "Voltar à revisão ›" como avanço e `nota1 != nota0`.
- **`acao_unica_test.py:70, 88-89, 120-139`:** número e rótulos de etapa são do paralelo.
- **`partest.py:26` (LEGT):** quando o Tipo for "N parcelas", tratar Área livre "—" como zero (`(lv==='0'||lv==='—')?'área toda alocada':…`), para `:49` continuar igual.
- **`partest.py:49-52, 75-76`:** "9 cultivos · 1.165 ha" e "15 cultivos" viram a faixa "Nesta safra 1.165" mais a contagem de linhas desta safra (filtrar pela coluna Safra = "—" ou por `r.fora`).
- **`partest.py:131`:** igual; acrescentar "Livre a partir de 21/02/2027".
- **`partest.py:132-137`:** entrada pelo "Planejar ›" do T4; aviso "parcela T4-A · 104 ha livres em T4" e "A conferir"; **acrescentar** que a linha c4 continua presente depois de salvar.
- **`partest.py:138-143`:** T2 sem Planejar; Dividir T2 + 50 ha dá "Excede em 50 ha"; com 248 ha salva em 2 parcelas.
- **`saftest.py:22, 33, 49, 58, 63`:** `match(...)[0]` vira `(match(...)||[''])[0]`, lendo a faixa "Nesta safra …". `:24-32` continua com 4 selecionados e "aplicado a 4 cultivos" (P2 com pendência); rodar e registrar k4, k6 e a SOL/complemento da Compra (`:58-69`) contra a base `884620c`, sem prometer números.
- **`testes_pedido.py:54-57` (t02):** "aplicado a 4 cultivos" continua; acrescentar a pendência do P2 com a causa. `:58-62` não muda.
- **`tabelas_saf_test.py:96`:** acrescentar SITUAÇÃO, LIVRE A PARTIR DE, OCUPA ATÉ, FIM POR e SAFRA, por inclusão. `:99-106` filtram linhas desta safra pela coluna Safra ou por `fora`, não por CULTURA (as filhas de fora também têm cultura). `:109`: o clique na 2ª célula ainda abre o formulário.
- **`componentes_test.py`:** regressão do `presa()`: numa grade presa a 390 × 844 e 360 × 800, seleção ≤ 40 px e a coluna logo depois da presa termina dentro da caixa (`right ≤ caixa.left + clientWidth + 1`). Junto com `tabelas_os_test.py` e `tabelas_est_test.py` (PR-G).
- **Continuam sem mudança:** `psfix38test.py:80-84`, `saf38test.py:72`, `saf_cmp_continuidade_test.py:147-153`, `cadf_test.py`, `cadf_det_test.py`, `cadf_fix_det_test.py`, `cadf_fix_lista_test.py`, `etapas_celular_test.py` (exceto o (1,6) do paralelo). Se algum depender da forma da S2627, adaptar por inclusão, nunca esconder.
- **`verif_saf*.py`:** obsoletos antes deste pedido; não contam como proteção.

### 7.3 Fonte única de trava, pendência e mensagens (exec., folga 1, `saida_trava_f1.txt`)

| Caso | Resultado |
|---|---|
| S27SF, Milho T1-B 152 ha, 21/02/2027 | Salva |
| S27SF, Milho T1-B 152 ha, 20/02/2027 | Salva; pendência 1 dia com c2 (P1). Folga 0: salva sem pendência |
| S27SF, Milho T1-B 152 ha, 15/02/2027 (tarefa do dono) | Salva; pendência 6 dias com c2 |
| S27SF, Milho T1-C 152 ha, 15/02/2027 | Salva; pendência de soma em 20/02/2027 (c2 + T1-C + d1) |
| S27SF, Milho T1 312 ha, 21/02/2027 | **Recusado (M1):** T-área (472 > 312 ha) e T-faixa com d1 |
| S27SF, Milho T1 312 ha, 11/07/2027 | Salva |
| S27SF, Milho MILHO-SF T3, 23/10/2026 · 10/01/2027 · 10/02/2027 | **Recusado (M2):** núcleo do c5 até 10/02/2027 |
| S27SF, Milho MILHO-SF T3, 11/02/2027 | Salva; aviso "provável sobreposição (7 dias)" |
| S27SF, Milho MILHO-SF T3, 18/02/2027 | Salva; aviso "saída da soja estimada em 17/02/2027; confirme a colheita" |
| S27SF, Milho **sem plano** T3, 23/10/2026 | Salva; aviso (nenhuma das duas tem plano) |
| c5 com colheita informada 20/01/2027 → milho T3 21/01/2027 · 20/01/2027 | Salva · **Recusado (M2)** |
| S2627, SOJA-AT em c4, c5, c6 · SOJA-PD em c4, c5, c6 | Salvam |
| S2627, SOJA-AT em c7 | Salva; pendência 11 dias com e5 (05–15/11/2026) (P1). Demanda do P2: R$ 167.992,00 |
| S2627, SOJA-PD em c7 | Salva; pendência 6 dias (10–15/11/2026). Demanda do P2: R$ 110.680,00 |
| e5 com **colheita real** 20/11/2026 → SOJA-AT em c7 | **Recusado (M4)**; PlantioMin 11/12/2026 |
| e5 sem colheita informada (estimado 28/12/2026, núcleo até 27/12/2026) → SOJA-AT em c7 | **Recusado (M2)**; S2627 P2 A conferir, "2 sucessões a conferir" |
| Plantio do c1 em 30/10/2026 | Salva; pendência 6 dias no d1 (20–25/02/2027) (P2) |
| T3 milho 11/02/2027, depois SOJA-AT no c5 · SOJA-PD no c5 | c5 recebe o plano; pendência no milho de 7 dias · 4 dias |
| T3 milho no padrão 18/02/2027, depois SOJA-AT ou SOJA-PD no c5 | Salvam sem pendência |
| P2 milho no padrão 24/03/2027, depois SOJA-AT no c7 (25/11/2026) | Salva; pendência só com e5 (11 dias) |
| P2 milho 24/03/2027, depois c7 SOJA-AT com plantio 06/12/2026 | **Recusado (M2):** núcleo do c7 até 27/03/2027 × milho de 24/03; sem janela → P3 |
| P2 milho 24/03/2027, depois c7 SOJA-PD com plantio 01/12/2026 | Salva; pendência 3 dias no milho (24–26/03/2027) |
| S27SF T1-B, SOJA-AT 12/03/2027 · 13/03/2027 | Pendência 1 dia · salva (PlantioMin) |
| 2027/28, Café CAFE-AR T3 01/11/2027 · Mamão MAMAO-F P2 01/11/2027 | Salvam, início 01/11/2027, aviso de datas fixas (15/10/2026 · 01/10/2026) |
| 2027/28, Milho T7 01/10/2027 | **Recusado (M3):** perene |
| 2027/28, Vincular c9 | Uma ocupação, sem trava |

**Mensagens** (OC-U4; `<…>` vem do dado):
- **M1 (T-área/T-faixa por área):** "De 21/02/2027 a 10/07/2027, 160 ha de T1 estão com Milho (T1-A, Safrinha 2027). Máximo 152 ha nesse período."
- **M2 (núcleo):** "T3 está com Soja 62 X da Safra 2026/27, plantada em 22/10/2026: ocupa a área até pelo menos 10/02/2027 (ciclo mínimo da soja, 112 dias, CD-02). O plano geraria insumo e O.S. sobre lavoura em campo. Informe a colheita da soja ou plante a partir de 11/02/2027."
- **M3 (perene):** "T7 tem Mamão Formosa perene, sem fim registrado. O plano geraria insumo e O.S. sobre o pomar. O encerramento do ciclo ainda não existe no sistema."
- **M4 (observado):** "O Milho AG 8700 de P2 foi colhido em 20/11/2026; a dessecação da Soja alta tecnologia cai em 05/11/2026, com o milho em campo. Plantio a partir de 11/12/2026 resolve."
- **P1 (pendência):** "P2: sobreposição prevista de 11 dias. A dessecação da Soja alta tecnologia cai em 05/11/2026 e o Milho AG 8700 (Safra 2025/26) está previsto até 15/11/2026. Mude o plantio para 06/12/2026 ou depois, ou confirme a colheita do milho."
- **P2 (pendência entre safras):** "T1-A: a colheita prevista da Soja passa para 25/02/2027, depois do plantio do Milho da Safrinha 2027 (20/02/2027). Sobreposição prevista de 6 dias."
- **P3 (sem janela):** "P2 tem Milho da Safrinha 2027 a partir de 24/03/2027. Para a soja com Soja alta tecnologia começar depois do milho anterior (16/11/2026), replaneje esse milho para 04/04/2027 ou depois."
- **P3 com perene nova** (replanejar a sucessora não resolve): "O café é perene e não libera B1-A: use outra parcela (ex.: B1-B)."
- **Pista "Plantio a partir de" sem janela por causa da área:** "reduza a área: máximo 18 ha" (o mesmo máximo da M1), em vez de "sem janela antes do fim da safra".

---

## 8. PRs pequenos e ordem

| Ordem | PR | Conteúdo | Testes |
|---|---|---|---|
| 0 | **Contrato** (Codex autor, Claude revisor) | Decisão de 05/10 em `docs/DECISIONS.md`; PRD 39.2 passo 1 (PRD.md:6656), PL-01 (PRD.md:561-565), UX-01 (PRD.md:11736-11740); exemplo em `tools/prototipo/v37/specs/padrao-comandos-v3-prompt.md:35`. Pré-requisito comum com a etapa única (`saf345/especificacao.md:646`) | revisão escrita |
| 1 | **PR-A** `claude/v44-ocupacao-a` | Só `ocupacao.js`, `ocupacao.py`, `ocupacao_unit.py`. e4/e5 como fixture sintética no unit. **Não toca `dados2.py`** (reservado pelo paralelo, `saf345/especificacao.md:51`) | OC-U1…U9 |
| 2 | Etapa única, PR 2 (paralelo) | Numeração e `passo=` | do paralelo |
| 3 | **PR-G** `claude/v44-g2lib-fora` | As 5 mudanças de `g2lib.js` do §0, com base combinada com a parte `act`/`aria-label` do paralelo | `componentes_test`, `tabelas_os_test`, `tabelas_est_test`, bateria sem vermelho novo |
| 4 | **PR-B1** | Talhões do CD-01, fazenda herdada, `cultsDe`/`v.saf`, `soDaSafra`, camada de exibição sobre cópia, e4/e5 em `dados2.py`, Boa Vista. Só leitura | OC-01, OC-13, OC-15, OC-16, OC-20 |
| 5 | **PR-B2** | 16 colunas, Situação, faixa, chips, árvore, R-12, `dcol`, links `passo=cultivos`. Só leitura | OC-02…OC-04, OC-17, OC-18, adaptações do §7.2 |
| 6 | **PR-B3** | "Planejar ›" no lugar do "Adicionar", painel (Plano antes de Plantio, PlantioMin, Colheita prevista), Vincular ciclo, Lagoa no formulário | OC-05, OC-06, OC-14, OC-19, OC-21, OC-22 |
| 7 | **PR-B4** | Trava, pendência, avisos, lote, mensagens | OC-07…OC-12, OC-23 |
| 8 | **PR-C** | CD-01 vivo no SAF: lê `talhao-os-cd01-v1` (`areas/cad_fazendas.py:121, 179-180`) para talhão criado, editado ou Inativo. Pré-requisito: decisão da S2526 | Talhão criado aparece; Inativo some; área editada vale |

Em todos: links novos gravam `#saf=<id>&passo=cultivos`, nunca `etapa=`; quem entra depois refaz a base; ninguém sobrescreve arquivo ativo do outro (AGENTS §3.4; `RETOMADA-NUVEM.md:20`). A homologação só acontece depois do PR-C (§9).

---

## 9. Aceite

### 9.1 Matriz de aceite

| # | Critério | Regras | Testes | Achados |
|---|---|---|---|---|
| A1 | Nenhum "Adicionar cultivo" no SAF; todo caso que ele cobria tem caminho | R-18, R-24, §5.2 | OC-14, OC-05 | DONO-01, OC-R7, REG-01 |
| A2 | Todos os talhões ativos da fazenda da safra, inclusive o B1 | R-01, R-21 | OC-01, OC-15 | — |
| A3 | Perenes, outras safras e lavouras em campo aparecem com Situação, Ocupa até, Fim por e Safra, e nunca como livres; a causa de cada A conferir está à vista | R-04, R-10, R-12 | OC-02, OC-05, OC-20, OC-09/10 (ocupante visível) | OC-R4, REG-05, DONO-08, OC-R11 |
| A4 | Trava só com o certo (núcleo, observado, área), com fato, dano e saída, sem gravar | R-14 | OC-07, OC-11, OC-23(b), OC-U5, OC-U8 | OC-R5, REG-02, OC-R10 |
| A5 | Previsões cruzadas viram pendência visível e o plano entra na demanda | R-15, R-16 | OC-08, OC-09, OC-10, OC-11 | REG-02 |
| A6 | Fim estimado coerente com os planos e pior caso que não esconde lavoura | R-04(e), R-08, R-09 | OC-U1, OC-U2, OC-U8 | OC-R1, OC-R2, OC-R9 |
| A7 | Padrão do painel nunca leva a recusa | R-17 | OC-21, OC-23, OC-U5 | DONO-05, OC-R2 |
| A8 | Saída do A conferir existe: aplicar plano ou informar colheita, com link | R-04(d), R-15, §5.1 | OC-12, OC-22 | DONO-07 |
| A9 | Faixa e chips dizem a mesma coisa | R-09, R-10, §3.3-3.4 | OC-03, OC-04, OC-U2, OC-U3 | DONO-04, REG-06, OC-R11 |
| A10 | Folga explícita, padrão 1, 0 permite plantar no dia da colheita | R-06 | OC-08, OC-U8 | OC-R3, OC-R9 |
| A11 | Linhas de fora nunca gravadas nem contadas; safras novas separadas | R-13, R-22 | OC-13, OC-15 | REG-08, REG-09 |
| A12 | S2627 com as mesmas linhas desta safra e os mesmos números de área, plano e demanda | R-13 | OC-U9, OC-13 | REG-05 |
| A13 | Celular responde "o que está livre"; 1440 responde "o que ocupa e até quando" | §2, §3.1 | OC-17, OC-18 | DONO-02, DONO-03, REG-07 |
| A14 | Medição de toques contra o caminho real de hoje | §2 | OC-19 | DONO-06 |
| A15 | Nenhuma falha nova na bateria completa | — | §7.2 | REG-10 |

### 9.2 Comandos (em `tools/prototipo/v37/gen37`)

```
python3 build.py
python3 ocupacao_unit.py
python3 ocupacao_test.py
python3 acao_unica_test.py saf
python3 partest.py
python3 saftest.py
python3 testes_pedido.py
python3 tabelas_saf_test.py
python3 saf_cmp_continuidade_test.py
python3 psfix38test.py
python3 cadf_det_test.py
python3 cadf_fix_det_test.py
python3 componentes_test.py
python3 tabelas_os_test.py
python3 tabelas_est_test.py
python3 etapas_celular_test.py
python3 ../ferramentas/acoes_duplicadas.py . <saida.json> SAF
```

Depois, a bateria completa, a mesma da evidência `884620c`. Verificação desta especificação: `verificacao/roda.sh`.

### 9.3 Para o proprietário (na homologação, depois do PR-C e dos dois pareceres)

**Tarefa curta:**
1. Planejar safra › Safrinha 2027. Confira que T7 e C1 aparecem como Perene, sem "Planejar", e que o T1 mostra 152 ha livres a partir de 21/02/2027.
2. Em "Planejar ›" do T1, escolha Milho e plantio em 15/02/2027: o sistema salva e avisa a sobreposição prevista com a soja, com a data desde quando fica livre.
3. Troque para 21/02/2027 e salve: sem aviso.
4. Na Safra 2026/27, aplique o plano de soja em T4, T3, P1 e P2: os quatro recebem o plano, e o P2 mostra "Sobreposição prevista: 11 dias" com o milho até 15/11/2026. Use "Mudar plantio ›" e confira que o aviso some com 06/12/2026.

**Limitações a dizer:**
- As edições continuam só na página: O.S., Compra e CD-01 leem o dado estático.
- Folga de liberação = 1 dia até ele responder (DECISOES).
- Datas previstas ou estimadas não travam; geram pendência visível. Trava só com o que é certo: o ciclo mínimo da cultura depois do plantio, a colheita registrada, o perene e a área do talhão.
- Indisponibilidade por período (pousio, reforma, arrendamento, embargo) ainda não existe: o talhão aparece Livre. Por ora, marque Inativo no CD-01 se ele sair de uso de vez.
- Duas culturas no mesmo talhão na mesma safra ainda não: para a safrinha, use a safra dela, como a Safrinha 2027.
- Numa safra nova da Lagoa que cruza a Safra Mamão 2026/27, os pivôs aparecem Perene sem ação; planeje pela safra existente.
- Ciclo perene não termina no sistema (erradicação/renovação).
