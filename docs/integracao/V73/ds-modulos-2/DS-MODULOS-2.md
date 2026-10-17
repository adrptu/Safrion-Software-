# DS-MODULOS-2 · Padrão do Agrícola em todos os módulos, MAIS-02 e cartões compactos

> Proprietário:
> - 16/10/2026: "os demais módulos estão com design system diferente do nosso padrão de excelencia do módulo agrícola. Faça seu melhor e mantenha sempre o padrão para mim não ter que ficar cobrando toda vez."
> - 17/10/2026: "aplicacao do design system padrao, referencia modulo agricola ainda nao foi para demais modulos, como esta isso para o artefato?"
> - 17/10/2026, sobre Manutenção › Planos: "os 3 pontinhos no topo da tela a direita em criar plano.... é uma boa, toda tela que tiver mais ações pode ter esses 3 pontinhos nesses botões dessa região da tela."
> - 17/10/2026, com print da O.S. em Cartões agrupada por talhão: "os cartoes em ordem de serviço estao fora do padrao design system".

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: DS-MODULOS-2 (MAIS-02, VIS-07, TAB-05 no motor, CAB-1/CAB-2 fora do menu, TAB-07 tela a tela) / todo módulo com o cabeçalho, a tabela, os cartões e as ações do Agrícola / todos os usuários
Requisitos do PRD e fora do escopo: PRD cap. 74; padroes-1510, padroes-1610 e padroes-1710; fora: CA-02, GE-02det, GE-03, GE-08 (frente PAINEL-FIXO-2 do Codex) e os arquivos areas/campo.py e areas/gestao.py; corpo do mapa do IN-04 (frente MAPA-UX); padrão de expansão (x0/exp) e regra de setas (frente DRILL)
Autor / revisor / integrador: Claude / Codex / integrador da composição (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: 5bb8f5e / ui37.py, engine.py, g2lib.js, ds_modulos.py, áreas listadas abaixo e os testes adaptados
Aceite e comando de verificação: ds_modulos.py --catraca e a bateria em "Provas"
Estado / impedimento / próximo passo: ver "O que fica"
```

## O que mudou (peça comum primeiro)

| ID | Mudança | Onde | Alcance |
|---|---|---|---|
| CAB-1 | Tela fora do menu ganha o "‹ Módulo" (`volta_pilula`) pelo prefixo (`VOLTA_PREF`) e o caminho diz o mesmo módulo; ON-01 e BO-02 voltam a "Outros acessos"; a ficha impressa da OS-0424 ganha "‹ Ficha do app" | `ui37.shell37`, `ui37.VOLTA37`, `areas/os_campo.py` | 50 desvios → 1 (CA-02, frente do Codex) |
| CAB-2 | Fazenda, safra e parceiro saem do topo e vão para a faixa "Trabalhando em" (FIL-01, `CTX_LAB`) | `ui37.shell37` | 57 → 0 |
| MAIS-02 | À direita do título, só a primária e o ⋯ com as outras ações; regra medida | `engine.recolhe_cabecalho` (usa `mais` e `item_menu`), `ui37.shell37`, `ds_modulos.py`; Estrutura gerencial (`cad_produtos_estrutura.py`) | 1 → 0 |
| TAB-05 | O ⋯ da linha é o padrão do motor (`menu_linha=None` → ligado); a pergunta da linha fica à vista (`decide`) | `engine.grid`, `g2lib.g2vals`; Estoque marca as perguntas da linha com `decide` | 31 → 2 (CA-02 e GE-08, frente do Codex) |
| VIS-07 | Cartões do motor em grade de cartões compactos, sem cabeçalho de colunas, com o selo de estado no título e até 4 campos rotulados, também agrupados | `engine.CARTOES_CSS`, `engine._cartoes_html`, `g2lib.g2cdVals` | toda lista do motor em Cartões |
| TAB-07 | Cartões de resumo saem de cima da lista, tela a tela (tabela abaixo) | 11 arquivos de área | 34 → 9 (todas em arquivos da frente do Codex) |
| FIL-01 | A escolha do talhão no detalhe do cadastro vai para a faixa comum de filtros | `areas/cad_fazendas.py` | 1 → 0 |

### TAB-07 tela a tela

| Tela | O que saiu de cima da lista | Para onde foi |
|---|---|---|
| IV | Produtos em alta, Vender agora, Mês de melhor preço | colunas Tendência e Melhor mês; "Vender agora N" no filtro rápido; selo do cabeçalho |
| IC | Insumos em alta, Comprar agora, Economia esperando o mês certo | coluna Tendência; "Comprar agora N" no filtro rápido; a economia abre os indicadores entre os blocos, depois da lista |
| CF-05 | Plano, área medida, prévia, próxima cobrança | pares rótulo × valor da própria assinatura (sem número grande) |
| BO-02 | Mensalidades vigentes, organizações, faturas abertas, área cobrada | pares rótulo × valor: são os totais da plataforma pedidos no PRD §6 (área cobrada = mín(medida; contratada) não é soma de coluna) |
| ON-01 | Trial, área declarada, pendências, modo | selo do cabeçalho "Passo 3 de 6 · N pendências · trial até 18/10"; área e modo já estão em "Direitos do trial" |
| AG-01det | Pontos válidos, média válida, pontos ≥ NC, evidências | pares rótulo × valor do resultado da vistoria |
| PT-06 | — | é o painel do Portal do parceiro ("Indicadores"): os cartões são o conteúdo; o medidor passou a tratá-la como Painel |
| PL-01, PL-03, PL-04, PL-05 | safras, carga × capacidade, ordens do período, impedimentos | selo do cabeçalho com o que pede atenção; o resto está nas linhas |
| CO-01, CO-02, CO-07 | oferta, janela, saldos | selo do cabeçalho; linhas da oferta, das ordens e dos lotes |
| LO-01 a LO-04 | cargas, pátio, viagens, fretes | selo do cabeçalho; linhas |
| VE-04 | a confirmar, disputa, sem alocação, recebíveis | selo "3 a confirmar · 2 em risco · 1 disputa"; linhas |
| SU-01 | falta firme, atrasados, condicionado, valor | selo "18 itens com falta firme · 5 atrasados · R$ 428,3 mil"; o condicionado está na linha do KCl |
| SU-03 | conflito, retidos, custódia, valor | selo; coluna Custódia; valor em insumos na linha de total da coluna Valor |
| SU-05 a SU-09 | conflitos, divergências, quarentena, custódia, trânsito, ajustes | selo do cabeçalho (já dizia o que pede atenção); linhas |

## Resultado (executado)

Desvios por módulo e regra, antes → depois. As duas medidas usam o mesmo medidor, o `ds_modulos.py` final, a 1440 × 900 nas 148 telas. "Antes" é o render limpo de 5bb8f5e (`ds-modulos-base-5bb8f5e.json`; o `.log` guarda a 1ª medida, 176, feita com o medidor sem a exceção do painel PT-06). "Depois" é a candidata após a junção de ac5cd1d7 (`ds-modulos.json`, gravado com `--grava` depois de `--catraca` ok). "Menu = não" são as telas fora do menu.

| Módulo | Menu | CAB-1 | CAB-2 | BOT-01 | FIL-01 | TAB-07 | TAB-05 | TAB-08 | VIS-05 | VIS-06 | MAIS-02 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Agrícola | sim | 2 → 1 | — | — | — | 5 → 4 | 3 → 1 | 1 → 1 | — | — | — | **11 → 7** |
| App de campo | sim | — | — | — | — | — | — | — | — | — | — | **0 → 0** |
| Cadastros | sim | — | — | — | 1 → 0 | — | — | — | — | — | 1 → 0 | **2 → 0** |
| Comercial | sim | — | — | — | — | 1 → 0 | — | — | — | — | — | **1 → 0** |
| Configurações | sim | — | — | — | — | 1 → 0 | — | — | — | — | — | **1 → 0** |
| Crédito | sim | — | — | — | — | 1 → 1 | 1 → 1 | — | — | — | — | **2 → 2** |
| Manutenção | sim | — | — | — | — | — | — | — | — | — | — | **0 → 0** |
| Mapa | sim | — | — | — | — | — | — | — | — | — | — | **0 → 0** |
| Onboarding e backoffice | sim | 2 → 0 | — | — | — | 2 → 0 | 1 → 0 | — | — | — | — | **5 → 0** |
| Portal do parceiro | sim | — | — | — | — | — | — | — | — | — | — | **0 → 0** |
| Suprimentos | sim | — | — | — | — | 1 → 0 | 1 → 0 | — | — | — | — | **2 → 0** |
| Agrícola | não | 11 → 0 | 14 → 0 | — | — | 5 → 1 | 4 → 0 | — | — | — | — | **34 → 1** |
| App de campo | não | — | — | — | — | — | — | — | — | — | — | **0 → 0** |
| Comercial | não | 17 → 0 | 22 → 0 | — | — | 8 → 0 | 9 → 0 | — | — | — | — | **56 → 0** |
| Gestão | não | 5 → 0 | 6 → 0 | — | — | 3 → 3 | 2 → 0 | — | — | — | — | **16 → 3** |
| Mapa e Início | não | 3 → 0 | 3 → 0 | — | — | — | — | — | — | — | — | **6 → 0** |
| Onboarding e backoffice | não | 1 → 0 | — | — | — | — | — | — | — | — | — | **1 → 0** |
| Portal do parceiro | não | — | — | — | — | — | 6 → 0 | — | — | — | — | **6 → 0** |
| Suprimentos | não | 9 → 0 | 12 → 0 | — | — | 7 → 0 | 4 → 0 | — | — | — | — | **32 → 0** |
| **Total** | | 50 → 1 | 57 → 0 | 0 → 0 | 1 → 0 | 34 → 9 | 31 → 2 | 1 → 1 | 0 → 0 | 0 → 0 | 1 → 0 | **175 → 13** |

### VIS-07 · O.S. em Cartões, medida antes → depois

Medido com o mesmo roteiro nos dois renders (`OS.dc.html?view=cartoes` e `&ag=onde`, perfil Ana). A candidata tem mais O.S. que a base porque a composição acrescentou ordens; compare a forma, não a contagem.

| Vista | Cartões | Por linha | Largura média | Altura média | Cabeçalho de colunas | Campos rotulados | Com selo de estado |
|---|---|---|---|---|---|---|---|
| solta · 1440 px | 10 → 15 | 1 → 4 | 1282 → 313 px | 54 → 121 px | sim → não | 4–4 → 1–4 | 0 → 15 |
| agrupada por talhão · 1440 px | 11 → 16 | 1 → 1 | 1282 → 313 px | 54 → 124 px | sim → não | 4–4 → 1–4 | 0 → 16 |
| solta · 390 px | 10 → 15 | 1 → 1 | 268 → 268 px | 77 → 79 px | não → não | 1–2 → 1–2 | 0 → 0 |
| agrupada por talhão · 390 px | 11 → 16 | 1 → 1 | 268 → 268 px | 77 → 79 px | não → não | 1–2 → 1–2 | 0 → 0 |

Capturas: `capturas/antes|depois/OS_view-cartoes*_{1440,390}_*.png`.

## O que fica (13 desvios, com o motivo)

| Tela | Regra | Por que fica | Mudança exata, para quem pegar |
|---|---|---|---|
| CA-02 Apontamentos e conferência | CAB-1, TAB-07, TAB-05 | **Fora, frente do Codex** (PAINEL-FIXO-2) | `VOLTA37['CA-02.dc.html']=('Ordem de Serviço','OS.dc.html')`; os 3 `kpis` viram selo ("52 ha provisórios · 1 fora da tolerância") e filtro rápido; sair da `TAB05_FORA` |
| GE-03 Custos e fechamento | TAB-07 | **Fora, frente do Codex** | Competência e lançamentos no selo; provisórios e conciliação como filtro rápido; somas na linha de total |
| GE-08 Crédito e garantias | TAB-07, TAB-05 | **Fora, frente do Codex** | Somas na linha de total da `g_cre`; "A liberar" como filtro rápido; sair da `TAB05_FORA` ("Autorizar bloco" vai ao ⋯) |
| CA-01 Ordens de campo | TAB-07 | Arquivo `areas/campo.py`, da frente aberta do Codex | "A liberar" e "Em conferência" como filtro rápido da Fase; "Saldo parado 70 ha · OS-0420" no selo; "Saldo aberto" na linha de total |
| CA-01det e CA-01x-os0420 (detalhe da O.S.) | TAB-07 | `areas/campo.py`, frente do Codex | Autorizado, Realizado, Saldo e Hoje são dados do próprio registro: pares rótulo × valor, como a vistoria (AG-01det) e a assinatura (CF-05) |
| GE-01 Visão gerencial | TAB-07 | `areas/gestao.py`, frente do Codex | Receita e margem já estão na linha de total; ROIC na linha de total; qualidade dos dados no selo |
| GE-04 Contas a pagar e caixa | TAB-07 | `areas/gestao.py`, frente do Codex | Caixa e saldo no selo; "Vence hoje" e "Aguardando banco" como filtro rápido; somas na linha de total |
| GE-05 Contas a receber | TAB-07 | `areas/gestao.py`, frente do Codex | Carteira na linha de total; "Vencidos" como filtro rápido; créditos solicitados no selo |
| OS-0424-ficha (ficha impressa) | TAB-08 | Regra de domínio: é papel. A ordem das cargas é a sequência do preparo, e no papel não se ordena nem filtra | Registrar como exceção de documento impresso (já tem os 40 px da TAB-10 e o "‹ Ficha do app") |

## Diferenças visuais além das regras medidas

Fotos a 1440 × 900 e 390 × 844 em `capturas/antes` (render de 5bb8f5e) e `capturas/depois` (candidata): referências do Agrícola (OS, SAF, CA-01) e uma tela por módulo (CO-01, VE-01, SU-01, CMP, EST, GE-01, CF-01, PT-02, LO-01, IC, IV), mais O.S. em Cartões (solta e agrupada por talhão), Atividades do plano e Estrutura gerencial.

| Achado | Onde | Feito |
|---|---|---|
| Cabeçalho diferente nas telas fora do menu: fazenda e safra soltas no topo, sem "‹ Módulo", caminho com os módulos antigos (Campo, Planejamento, Gestão e resultados) | 86 telas | Corrigido na casca (`ui37.shell37`) |
| Cartão do motor como linha larga de tabela, com cabeçalho de colunas e valores espalhados | toda lista em Cartões | Corrigido (VIS-07) |
| Cartões de resumo com tipografias diferentes (rótulo em caixa alta em Suprimentos, Logística e Colheita, caixa normal em Campo e Gestão; número de 22 a 30 px) | 25 telas | Saíram com a TAB-07; os que ficam estão nas telas da frente do Codex |
| Botões de ação com texto e borda dentro das células | 31 telas | Corrigido (TAB-05 no motor) |
| Duas ações à vista no cabeçalho | Estrutura gerencial | Corrigido (MAIS-02) |
| Seletor do talhão em 15 px/800 ao lado do título | CD-01det | Corrigido (faixa de filtros, `MF_SEL`) |
| "Voltar à ficha do app" em botão pequeno à direita | ficha impressa | Corrigido ("‹ Ficha do app") |
| Ação de navegação na célula com borda ("Detalhar demanda", "Criar oferta", "Abrir proposta") × o link verde "Liberar ›" do Agrícola | VE-01, PT-02 e outras | **Não mudou:** é o componente aprovado `g2cta` (DS-ALVO de 15/10; `ds_padrao_test.py` T3 confere o desenho). Navega, não é botão de ação (TAB-05 deixa na célula). Fica para decisão de padrão |
| Linha de texto solta acima das seções do Estoque ("2 notas a conferir · em quarentena …") | EST | **Não mudou:** são as linhas `k1…k6` do Estoque, lidas por ~10 testes de domínio do Estoque; fica para a frente do Estoque |
| Indicadores entre os blocos | IV, IC, VE-01 ("Disponibilidade da semana") | **Ficam:** estão depois da 1ª lista; na IV/IC são o painel do assunto e no VE-01 mostram a conta em passos |
| Tabela larga que rola de lado dentro da caixa | SU-01 a 1440 | **Não mudou:** comportamento do motor para muitas colunas (a página não rola de lado) |

## Provas (executado)

Comandos rodados de `tools/prototipo/v37/gen37/` com `CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico`, um teste por vez.

**Medida das regras.** `ds_modulos.py --catraca` → `RESULTADO: catraca ok` (13 desvios em 10 de 148 telas), em 87d2deab e de novo depois da junção da composição ac5cd1d7 (2e765c01). Em seguida, `--grava` com `DS_MOD_JSON=docs/integracao/V73/ds-modulos-2/ds-modulos.json`. A base está em `ds-modulos-base-5bb8f5e.json`/`.log`.

**Bateria pedida, na candidata 87d2deab (render limpo do commit):**

| Teste | Resultado |
|---|---|
| ds_modulos.py --catraca | catraca ok · 13 desvios |
| paginas_scan_test.py | 5 ok · 0 falhas (148 páginas) |
| seta_padrao_test.py | 14 ok · 0 falhas |
| ds_padrao_test.py | 17 ok · 0 falhas |
| ds_1510_test.py | 17 ok · 0 falhas |
| ds_1610_test.py | 15 ok · 0 falhas |
| cartoes_test.py | 70/70 |
| tabelas_saf_test.py | 24/24 |
| tabelas_os_test.py | 40/40 ok |
| acao_unica_test.py | OK |
| ds_test.py | OK 72/72 |
| `node rmenu_alignment_test.js g2lib.js <g2lib de 5bb8f5e>` | 561 OK · 0 falhas |

**Testes dos módulos mexidos (por impacto, executados na árvore da frente):** inteligencia_nav 27/27 · sutest OK (27) · obotest 12/12 · cadc_cd07 OK · plataforma 22 ok · 0 falhas · assinatura 45 ok · 0 falhas · esttest OK (todas as partes) · consumo_divergente 21/21 · lotest OK · mip_fluxo 15/15 · cadf_det OK · cadf_fix_det OK · cadf_test 15/15 · est_validade_conc_nav OK · saf_contexto 10/10 · saf_capacidade_simetrica 38 ok · 0 falhas · rend_multiconjuntos 18/18 · saf_lote 47/47 · saf_fazendas 14/14 · saf_multi_fazenda 23/23 · saf_revisao 42 ok · 0 falhas · saf_c01 68 ok · 0 falhas · ocupacao 65 ok · 0 falhas · demanda_unica_nav 29 ok · 0 falhas · saf_cmp_continuidade 31 ok · 0 falhas · irr_fluxo 34 ok · 0 falhas · ma_rastreio 58/58 · app_cenario 15/15 · app_entrega_parcial 7/7 · solo_ag02 OK 32/32 · est_a4_nav 15/15 · est_fix2 11/11 · componentes 3 ok · 0 falhas · etapas_celular 14 ok · 0 falhas · visoes 9 ok · 0 falhas · os_cenario 22/22 · cadastros_padrao 44/44 · mbtest 0 falhas · ben_fluxo OK 224/224 · agtest 16/16 · app_os0424 9/9 · est_cenario 15/15 · inteligencia_unit 35/35 · cmptest sem falhas · saf_tab 14/14.

**Vermelhos que já estavam na base 5bb8f5e (mesmo teste rodado no render da base, mesmas falhas):** vetest (2 falhas, OF-103 e OF-104) · comercial_fluxo_test AC-16 EXPED (73/74) · cotest (base com 16 falhas; candidata com 12, todas presentes na base) · partest (3 falhas iguais) · irtest (1 ✗ igual) · est_fix1_test (9/13 igual). producao_fluxo_test 92/93: a única falha é "AC-h Mapa: a camada Colheita e produtividade…", que o teste marca de propósito como falha enquanto o botão da camada estiver na barra do IN-04 ("falta ligar ao conversor (P5)", DEC-0910-36). O botão é idêntico na base (`render_antes/IN-04.dc.html`), e esta frente não mexeu no IN-04.

**Oráculos adaptados (com contraprova).** Os testes abaixo liam ações que agora estão no ⋯ da linha (TAB-05), cartões de resumo que saíram (TAB-07), o cabeçalho com duas ações (MAIS-02) ou o cartão largo (VIS-07). Cada um passou a ler o lugar novo e continua reprovando a versão com defeito. Exemplo: o esttest, com o EST da base em `project/` e em `_render/`, reprova a TAB-05.
- inteligencia_nav, sutest, obotest, cadc_cd07, ds_1610 (C1 VIS-07), plataforma (A12j), assinatura (A9e), est_lib (LEGE), esttest, consumo_divergente, ds_padrao (X1)
- lotest, mip_fluxo, cotest, cadf_det, cadf_fix_det, cadf_test, saf_cmp_continuidade, producao_fluxo, est_a4_nav (T3c), etapas_celular, ds_test (C17 pelo teclado no ⋯)

**Depois da junção da composição ac5cd1d7 (2e765c01; o sutest adaptado é dbdcfdbb, só teste):**

| Teste | Resultado |
|---|---|
| ds_modulos.py --catraca, depois --grava | catraca ok · 13 desvios em 10 de 148 telas; base gravada |
| paginas_scan_test.py | 5 ok · 0 falhas (148 páginas) |
| cartoes_test.py | 70/70 |
| ds_1610_test.py | 15 ok · 0 falhas |
| tabelas_os_test.py | 40/40 ok |
| os_lote_test.py | 36/36 |
| ma_vinculo_test.py | 101/101 ok |
| ma_rastreio_test.py · ma_unica_test.py · ma_revisao_test.py · ma_correcoes_pm_test.py | 58/58 · 23/23 · 18/18 · 12/12 |
| sutest.py (SU-08 no contrato do PR #108) | OK; contraprova no render da base: os 4 oks da SU-08 e o da SU-06 reprovam |
| painel_fixo_2_test.py `<gen37> <campo.py e gestao.py de 5bb8f5e> node` | PASS |
| node: sup_movimentos, sup_movimentos_ui, sup_necessidades, sup_politicas, sup_politicas_ui (depois dos `*_capture.py`) | 7 · 7 · 15 · 11 · 9 PASS, 0 falhas (rc 0) |
| node: os_lote_unit.js · os_lote_foco_unit.js | 104 ok · 0 falhas · 8 ok · 0 falhas |
| textos_soltos_test.py | 267 OK · 1 falha. A falha é a mesma no render da base (`RENDER_DIR=render de 5bb8f5e`: 267 OK · 1 falha): "D CA-01det … o agrônomo ajusta e libera a v3 só para o saldo". O texto da dica em `areas/campo.py` é igual em 5bb8f5e, 87d2deab e ac5cd1d7; o teste é anterior ao d5342d48. Arquivo da frente do Codex; fica para quem mexe no CA-01det |

## Fronteiras respeitadas

- **Fora, frente do Codex (PAINEL-FIXO-2):** CA-02, GE-02det, GE-03 e GE-08, e os arquivos `areas/campo.py` e `areas/gestao.py`. Nada mudou neles por esta frente. A CA-02 do PR #109 chega pela composição. `engine.TAB05_FORA` deixa essas 4 telas sem o ⋯ automático da linha, até a frente delas decidir.
- **IN-04 (frente MAPA-UX):** nenhuma linha de `areas/inicio.py` nem de `talmapa.js` mudou: nem o corpo do mapa nem o cabeçalho. O IN-04 já estava sem desvio de CAB-1, CAB-2 e MAIS-02. As telas "Mapa e Início" fora do menu mudaram só pela casca comum (`ui37.shell37`).
- **DRILL:** nenhuma linha `x0`/`exp` mudou, e a regra das setas também não. `seta_padrao_test` dá 14 ok · 0 falhas.
- Não houve rebase nem push forçado. O `ds_modulos_base.json` só mudou pelo `--grava`.


