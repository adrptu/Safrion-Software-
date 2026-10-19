# Revisão do PR #132 (Codex): EX-53 D11b, dedicação semanal por pessoa e fonte CD-04, 19/10/2026

**Revisor e integrador:** Claude. **Autor:** Codex. **HEAD revisado:** `6ed2b16b3d3360f7f9b65933eed569a05d23533e`.

**Composição:** merge sem conflito sobre `d37e56e4` (v143), com 9 arquivos.

## Parecer
**Favorável.** Achados:
- **P2 do app do Codex** (CD-04 sem `cenOuvir`): está corrigido e reproduzido no navegador, com contraprova (abaixo).
- **Achados da minha leitura:** nenhum S1 a S3.

## O que conferi na leitura
- **Nomes globais novos:** `pessoas*`, `capacidade*`, `PESSOAS0`, `CAP_ESPECIALIDADES`, `c4fonte`, `c4grava`, `m6Pre`/`m6Extra` e `capAbre`/`capSalvar`/`capFecha`. Cada um aparece uma única vez no código: sem colisão com outras áreas.
- **Troca `PREVALS → m6Pre` e `EXTRAVALS → m6Extra` no `CF6_JS`:** há exatamente uma ocorrência de cada.
- **`cenOuvir` na CD-04:** aparece uma vez no HTML gerado; o prefixo do cenário não se repete.
- **Calendário:** o teto vem do calendário da equipe. O calendário da própria pessoa saiu da CD-04 em 16/10 ("nenhuma tela lia"); todas as 15 pessoas sintéticas estão em "Da equipe".
- **Teto nominal:** "seg–sex · 07–17h" dá 50 HH/semana, e é só um teto. A dedicação é informada pelo gestor; nada é presumido. Escala 6×2 sem âncora fica sem base (`null`).
- **Peso:** `PESSOAS0` e os dois `.js` passam a ir no prefixo de toda tela. Cada página cresce cerca de 13 KB (IN-04: 2.385.004 → 2.398.434 bytes). Os dados são sintéticos (ENG-017).

## Testes executados (render sintético da composição, Chrome)

| Teste | Resultado |
|---|---|
| Node do autor: `capacidade_unit_test.js`, `pessoas_estado_unit_test.js`, `pessoas_concorrencia_test.cjs` | PASS · PASS · PASS |
| Contraprova Node: `pessoas_concorrencia_test.cjs` com a CD-04 do `18691b5d` (sem `cenOuvir`) | Reprova: "CD04 deve registrar uma única escuta", 0 de 1 |
| `sonda_abas.py` (desta pasta, navegador real, duas janelas da mesma origem, tudo pela tela). E1 B salva a Oficina em 08–18h e A, ociosa, mostra 08–18h sem interação; E2 o rascunho aberto em A sobrevive à gravação de B; E3 o salvar de A com a revisão antiga é recusado, com o rascunho mantido e a fonte com o valor de B; E4 sem erro de JS | 4/4 |
| Contraprova: `sonda_abas.py` no mesmo render, com a chamada `cenOuvir(self)` retirada da CD-04 | 3/4. Reprova E1: A fica em 07–17h |

**Navegador (impacto):**

| Teste | Resultado |
|---|---|
| `config` | 90/90 |
| `config_regressao` | 6/6 |
| `cada_cd04` | 15/15 |
| `cada_fix04` | 12/12 |
| `cad_inicio` | 16/16 |
| `cadastros_padrao` | 44/44 |
| `tabelas_cad` | 206/206 |
| `popover_390` | 9/9 |
| `visoes_v23_codex` | 23/23 |
| `ex53_alav_meta` | 5/5 |
| `ex53_metas` | PASS |
| `ex53_m5_cartao` | PASS |
| `painel03` | 54/54 |
| `paginas_scan` | 5/5 (147 páginas) |
| `textos_soltos` | 267/267 |

**Unitários:**

| Teste | Resultado |
|---|---|
| `config_unit` | 226/226 |
| `man_backlog_unit` | 16/16 |
| `alocacao_unit` | 21/21 |
| `ben_unit` | 206/206 |
| `config_app_unit` | 4/4 |
| `metas_unit_test.js` | PASS |

Os brutos estão em `logs/`.

## Fica para depois (autoria Claude, fora deste PR)
O consumidor `manBacklog`/`pgBacklog` vai ler `capacidadeDe(c, especialidade)` e mostrar as semanas equivalentes por especialidade. Quando não há capacidade, o painel diz o motivo, sem número.
