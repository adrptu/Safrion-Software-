# v135 · composição de 18/10/2026 (`claude/v44-v135-osagrupa`)

Junta a v134 (`e0c47a00`), as correções dos 3 S2 da revisão do Codex (`91a8ab1d`) e o EX-54 F1. Base publicada: v133 (`a7680f6a`, versão 142).

## O que entra

| Item | Pedido ou origem | Onde |
|---|---|---|
| EX-54 F1 · Frentes de trabalho | Proprietário, 18/10: o agrupamento de O.S. estava ruim | O.S. › visão **Frentes** (sexta visão, `?view=frentes`). Substitui o diálogo "Agrupar O.S. semelhantes". Motor em `os_frentes.js`: a família vem do implemento; compatibilidade de calda; herbicida por último, com tríplice lavagem; ordem pela janela e pela distância; ganho em km e cargas. A frente não aprova, não libera nem reserva. Especificação: `docs/os-agrupa/OS-AGRUPA-2.md` §3–7 |
| Semente das frentes | Integrador (EX-54) | OS-0584–0594 na Lagoa Grande (pivôs reais) e OS-0595–0599 na Santa Rita, com o selo "Demonstração". Ficam fora da demanda de compra (`cenOsDem` e `dados2.os_dem`) e da faixa OS-0601+, que é das tarefas da Irrigação |
| AGUA-SOLO-IRR, S2 | Codex 6252809331 | Com a CAD, o balanço é dia a dia (FAO-56, eq. 85–86: 0 ≤ Dr ≤ CAD). O déficit de hoje, a série, a faixa da parcial e a necessidade usam a mesma conta (`irrBalDias`) |
| SAF-MAPA, S2 | Codex 6252809331 | Talhão com só parte das linhas marcadas aparece "Em parte · k de n" (`aria-pressed=mixed`). "Aplicar" recebe exatamente o conjunto anunciado |
| ATIVO-UNICO, S2 | Codex 6252809331 | O CD-03 junta por id o que a outra tela gravou e recusa, com o motivo, o mesmo ativo mudado nas duas telas. O rascunho fica |
| EX-55 (especificado) | Proprietário, 18/10: mapa dentro das telas | `docs/mapa/EX-55-validacao-claude.md` com os 5 pontos do Codex (§6). A F1 é dividida em arquivos: Codex `mapa_camadas.js`, Claude `mapa_emb.js` e os adaptadores |
| RX-0 (revisão) | Codex | `rx0-revisao/`: motor v3.1 (`cb481aab…`) e a sonda do C2.1 emendado (`5bdcd2f5`) |

## Testes executados

Bateria da composição: 54 testes em três raias (`logs/bateria/`). 44 passaram na primeira rodada. Os 10 vermelhos e o `map_aprov` (1 falha escondida por `rc=0`) foram classificados um a um e reexecutados (`logs/reexec/`):

| Teste | 1ª rodada | Causa | Correção | Reexecução |
|---|---|---|---|---|
| `config_test` | 89/90 | Oráculo: o painel da AL-01 conta as 16 O.S. de demonstração das Frentes | Espera 22 em A liberar (6 + OS-0584…0599) | 90/90 |
| `ctl5_test` | 19/30 | Oráculo: "Ordem A liberar" passa a oferecer as O.S. de demonstração de acaricida | Seleciona OS-0501 explicitamente; E2.2/E2.9 com a lista da demonstração | 30/30 |
| `cmptest` | DEM-08 | Oráculo da demanda sem a semente antiga | `1 escolha chega depois da falta` e sem linha de sulfato | sem falhas |
| `demanda_unica_nav_test` | 27/29 | Oráculo: contagem de produtos | N5 19/14 e I2 18/13 | 29/29 |
| `visoes_v23_test` | 310/368 | Oráculo: grupos começam recolhidos (DRILL-RECOLHIDO) | Abre o primeiro grupo e volta | 368/368 |
| `visoes2_agrupar_test` | — | Oráculo: idem | `expandir()` antes de G1–G3 | 3/3 |
| `tabelas_os_test` | 34/40 | Oráculo: OS-0597 e OS-0599 da semente na Santa Rita | P1, T1/T2, TF02, TF04, TF06 | 40/40 |
| `painel_modulos_test` | erro | Oráculo: calagens OS-0593/0594 impedidas por Suprimentos | Listas com 0593/0594, n = 7 | 88/88 |
| `nav_modulos_test` N3 | 14/15 (2 vezes) | **Teste:** espera fixa de 1 s. Sonda `sonda_n3.py`: a volta leva 0,1 s livre e até 1,08 s em carga. O produto espera o cartão por até 2 s | Espera a condição (rota e foco), limite 6 s | 15/15 |
| `map_aprov_test` 2 | 4/5 com `rc=0` | **Teste:** a linha começa pelo selo "Falta insumo"; o teste procurava pelo começo do texto. O detalhe da OS-0418 mostra "Liberar bloqueado: sem lote de Ureia 45%" | Acha a linha pelo ID e termina com `rc=1` em falha | 5/5 |

Contraprova das correções de teste: a asserção de conteúdo não mudou. O `nav_modulos` continua exigindo o foco no cartão aberto, e o `map_aprov` continua exigindo o bloqueio e a ausência de selo do agrônomo.

Fora da bateria:
- `datas_atividade_test` (EX-57 F0a/F0b do Codex, integrados em `62e13a67` e `75e77324`): 28.818 comparações legadas e 45 regressões da `canonica`;
- `agua_irr_unit` 7/7, `ativo_unico_unit` 6/6, `os_frentes_unit` 15/15, `os_lote_unit` 104/104.

## Contraprovas na base com o defeito

| Teste | Base | Resultado |
|---|---|---|
| `agua_irr_unit.js` | v134 `e0c47a00` | 1/7 (só "sem CAD" passa, como deve) |
| `ativo_unico_unit.js` | v134 `e0c47a00` | 1/6 (só "sem outra tela" passa) |
| `os_frentes_test` | v134 | 2/18 |

## Vermelhos que não vêm desta composição

| Teste | v135 | v134 (`logs/base134/`) | Situação |
|---|---|---|---|
| `filtros_cultura_test` F2 | 9/10 | 9/10, mesma falha (`Talhão` sem T2) | Vermelho antigo. Diagnóstico com o Codex (PR #47, 6254419571) |
| `tabelas_irr_test` TABR-CTX-02 | 98/106 | vermelho já registrado na integração do IRR-ONDA0 (PR #79) | Vermelho antigo. Mesmo pedido ao Codex |
| `map_aprov_test` 2 | 4/5 | 4/5, mesma falha | Era o localizador do teste, corrigido acima |
| `nav_modulos_test` N3 | 14/15 | 15/15 | Espera fixa do teste, corrigida acima; não é regressão |

**S3 conhecido (da semente de demonstração):** as calagens OS-0593/0594 aparecem no Painel com "falta insumo", mas ficam fora da demanda de compra, porque a semente não compra. Fica para a EX-54 F2.
