# DS-MAN: Manutenção no padrão do Agrícola (17 e 18/10/2026)

Pedido do proprietário (17/10, 23h): "Design system de manutenção ainda não está no padrão".

| Campo | Valor |
|---|---|
| ID / resultado útil / persona | DS-MAN. A Manutenção com o cabeçalho, os blocos, as linhas e a entrada do Agrícola (O.S. e MOD-AGR). Personas: Otávio (PCM), Zé (mecânico), Ana (gestora) |
| Requisitos e fora do escopo | `docs/design-system/` e PRD cap. 74. Fora: regras e painéis da OM, app de campo e o motor (`engine.py`, `g2lib.js`), que não foram tocados |
| Autor / revisor / integrador | Claude (autor) · Codex (revisor) · Claude (integrador da composição) |
| Base | `5466c6d0` (v129); integrado sobre a v130 (`684b3459`) na composição da v131 |
| Arquivos | `areas/maquinas.py`, `areas/modulos.py`, `ui37.py` (FLUXO37), `visoes_marcas.py`, `ds_man_test.py` (novo) e os oráculos dos testes da Manutenção |

## 1. O que mudou

A medição por regra (`ds_modulos.py`) dava 0 desvio para a Manutenção. A comparação com a O.S. do Agrícola, que é a tela aprovada, mostrou 7 desvios. Cada um virou regra com medida em `ds_man_test.py`, descrita em `docs/design-system/padroes-1710.md`:

| Regra | Antes (v129) | Depois |
|---|---|---|
| CAB-3 | Título "Manutenção" ao lado de "‹ Manutenção"; trilha "Manutenção › Manutenção" | O título é a visão aberta (Sem ordem, Ordens, Ativos, Planos); a trilha diz "Manutenção › visão" |
| CAB-4 | Texto solto de 3 linhas no topo e botão cinza sem motivo junto | Só título, selo e ações. Ação indisponível pela peça comum `acao_motivo`, com dica e motivo junto do botão |
| ABA-01 | Duas fileiras de abas soltas (visão e Ativos \| Abastecimentos) | Uma fileira acima do bloco; Ativos \| Abastecimentos dentro do bloco |
| ABA-02 | "Ordens 0" com 16 ordens; "Planos 0" com 10 planos | O número da aba é o que pede ação e só aparece se for maior que 0, com dica |
| BLO-01 | Lista solta, com 11 chips na mesma fileira | Lista num bloco com título, os filtros rápidos dentro; no máximo 2 recortes ao lado das fases e o resto no ⋯ |
| TAB-14 | Linhas de 3 a 5 linhas e cabeçalhos quebrados | No máximo 2 linhas por registro a 1440 px; rótulos curtos (Próxima, Grupo, Lançamento, A fazer); selo curto com o texto na dica |
| ENT-01 | Cartões em grade, na ordem do menu | Blocos Cadastro, Execução e Resultados, como o MOD-AGR. Acima deles fica só a linha de pendência "N ativos sem plano · Vincular ›" |

**Decisão do integrador (18/10):** o autor tinha tirado da entrada o aviso "N ativos sem plano · Vincular ›" do MA-VINCULO. Sem ele, chegar aos ativos sem plano passa de 1 toque para 2 (cartão Ativos e depois o filtro "Sem plano"). O aviso foi mantido como a única linha de pendência acima dos blocos, e aparece só quando há pendência. A regra ENT-01 e os testes dizem isso: `ds_man_test` E2 e `ma_vinculo_test` A1/B1.

## 2. Inventário de ações (nada perdido)

`inventario_antes.json` × `inventario_depois.json`: a mesma quantidade de ações em cada visão (Sem ordem 32, Ordens 36, Ativos 55, Abastecimentos 31, Planos 26, Ativo 16, Plano 25, Painel 6).
- O que muda é o rótulo: "Próxima manutenção" virou "Próxima"; "Lançamento · operador" virou "Lançamento"; "Próximo passo" virou "A fazer".
- Os recortes "Esta semana" e "Espera por peça" foram para o ⋯ do bloco, como "Ver carga desta semana" e "Ver ordens que esperam peça".
- A entrada mantém os 5 cartões e o aviso de pendência.

## 3. Testes executados (render da composição v131)

| Teste | Resultado |
|---|---|
| `ds_man_test` | 99 ok · 0 falhas |
| `ma_menu`, `ma_unica`, `ma_vinculo`, `ma_rastreio` | 10/10 · 23/23 · 101/101 · 58/58 |
| `ma_atrito`, `ma_correcoes_om`, `ma_correcoes_pm`, `ma_planos`, `ma_revisao` | 13/13 · 15/15 · 12/12 · 18/18 · 18/18 |
| `man_limpa`, `botoes_retorno`, `solo_mapa_calor` | 9/0 · 6/0 · 9/9 |
| `ds_test`, `ds_1610`, `cartoes` | 72/72 · 16/0 · 70/70 |
| `paginas_scan`, `links_ocultos`, `textos_soltos`, `cad_inicio` | 5/0 (148 páginas) · 16/0 · 267/0 · 16/0 |
| `nav_modulos` | 14/15. A 15ª verificação reprova no Crédito: os cartões da entrada não são os itens do menu. O `MOD-CRE.dc.html` é igual byte a byte ao da v130, então o vermelho já existia; fica para a base verde |
| `ds_modulos` (catraca do padrão) | 11 desvios em 10 de 148 telas (eram 13 na v128) |

Os brutos estão em `logs/`.

## 4. Contraprova

`ds_man_test` no render da v129, antes do DS-MAN: 25 ok · 56 falhas (`logs/ds_man_contraprova_v129.log`). A O.S. e o MOD-AGR passam nas mesmas medidas, porque a régua é a da tela aprovada.

## 5. O que ficou de fora

- O Painel (PMAN) já usa a peça dos painéis (`pn-card`), sem mudança.
- O app de campo da Manutenção fica para a frente do app.
- A divergência entre o menu e a entrada do Crédito vai para a base verde.
