# MAPA-FROTA F1 · Máquinas das O.S. em execução no Mapa, 19/10/2026

**Pedido do proprietário (16/10, 19:34 e 19:36):** máquinas em execução andando no mapa, com 1 clique e ícones.
**Especificação:** `docs/integracao/V71/MAPA-FROTA.md` (aceites M1–M24, contrato de leitura, decisões 1–20). Oráculo das regras: `docs/integracao/V71/mapa-frota/mapa_frota_chk.py`.
**Autoria:** Claude. **Revisão e integração:** Codex. **Base:** composição `e4318104` (v144).

## Resultado útil
No Mapa, o botão **Máquinas (N)** liga e desliga a camada com 1 clique, em qualquer função. Cada O.S. em execução com fonte de posição vira um marcador: ícone da operação, rótulo curto ("T03 · Pulverização") e selo com forma e palavra ("▶ trabalhando"). Tocar no marcador abre o painel do conjunto:
- O.S. e versão;
- operação e talhão;
- conjunto (pela programação ou de demonstração);
- estado e posição, com fonte, hora e idade;
- quanto falta, com a estimativa no rendimento de referência;
- carga (projeção da O.S.);
- operador, só para gestor e PCP;
- e o botão **Abrir O.S.**

**Lista (N)** mostra a lista equivalente, para teclado, leitor de tela e celular.

Da O.S. em execução, **Ver no mapa** abre o Mapa na fazenda da O.S., com o conjunto selecionado. Quando o contexto salvo esconderia a O.S., aparece a faixa "Recorte temporário".

**Dano evitado:**
- não saber onde está a máquina de cada O.S.;
- confundir demonstração com telemetria;
- presumir posição no centro do talhão;
- expor posição e operador a quem não coordena pessoas.

## O que é simulação
- **Só leitura.** As posições são simuladas e rotuladas "Posições simuladas · demonstração". O percurso tem passadas de 36 m e recuo de 18 m, dentro do talhão da O.S.; a velocidade é de 8 km/h na pulverização e de 3 km/h na colheita, com paradas; há uma leitura a cada 10 s.
- **Nada é gravado:** área, saldo, consumo, carga e fase vêm só da O.S.
- **Quem tem fonte simulada:** só OS-0421 (Santa Rita) e OS-0505 (Lagoa Grande, com o conjunto de demonstração Trator LG-01 + Carreta de colheita LG).
- **Quem não tem marcador:** OS-0420 (impedida, sem fonte) aparece na lista como "Posição indisponível". As fertirrigações OS-0506 e OS-0507 são ativos fixos e mostram "ver na Irrigação".
- **Lagoa Grande:** as leituras nascem no navegador, em metros relativos ao centro do pivô. Nenhuma coordenada é gravada.

## Mudança
- **`frota.js` (novo):** regras puras portadas do oráculo:
  - contrato de leitura L1–L14;
  - posição e estado P1–P13;
  - conflito por componente K1–K7;
  - pausa e agrupamento Z1–Z6;
  - família do ícone pela operação;
  - conjuntos derivados de `alVigente` (só leitura) e do grupo do OS-LOTE;
  - percurso sintético e leituras simuladas.
- **`frota_ui.js` (novo):** camada do Mapa:
  - marcadores com alvo de 44 px (SVG da Santa Rita e MapLibre da Lagoa Grande);
  - agrupamento "N máquinas";
  - legenda, lista, painel e permissões (decisão 15);
  - Esc devolve o foco à origem;
  - `#frota=OS-…` com recorte temporário;
  - um relógio só para mapa, lista e painel.
  - Gancho só de teste: `window.__frotaRelogio`, `window.__frotaFixture` e `window.__frotaTeste`. A camada não chama nenhum deles.
- **`dados_frota.py` (novo):** fixture da simulação (decisão 7), rendimento de referência por família e tanque do pulverizador (projeção EX-38).
- **`engine.py`:** 4 ícones de família no catálogo comum (`f_gotas`, `f_broto`, `f_graos`, `f_grade`).
- **`areas/inicio.py`:**
  - botões Máquinas e Lista na barra de ferramentas;
  - contêineres da camada, da legenda e do painel;
  - CSS;
  - `frVals` no fim do `MAPVALS`;
  - durante o recorte temporário, o endereço e o `mapa-ctx` não mudam.
- **`areas/processo_os.py`:** "Ver no mapa" no bloco Recursos alocados da O.S. em execução, que agora abre por padrão para ficar a 1 clique (K4).

## Fica para depois (com motivo)
- **"Ver no mapa" no ⋯ da linha da lista e do Kanban:** o ⋯ vem das ações da célula do motor da grade; entra numa entrega seguinte, sem mudar o motor nesta fatia.
- **M11 e M23** (20 sobrepostos e o foco ao agrupar): o agrupamento existe (`frAgrupar`, Z6 no teste de unidade), mas ainda não tem caso de navegador com 20 conjuntos.
- **M21 (EX-42):** não se aplica antes da barra de tempo.
- **F2** (movimento suave, rastro e pausa da animação) e **F3** (telemetria real): fatias seguintes.

## Achados das fotos (1440 e 390 px), corrigidos antes do envio
1. **Mensagem repetida.** A dica "Máquinas · toque numa máquina…" aparecia ao lado de um aviso com o mesmo texto. A 390 px o aviso cobria a linha Operador do painel. O aviso saiu; o modo do mapa e o `aria-pressed` dizem o estado.
2. **Título do painel quebrado.** "…PJ-3030 36" ficava numa linha e "m" sozinho na outra. Agora número e unidade não se separam, e o título quebra em linhas equilibradas.
3. **Rótulo do marcador ilegível.** Na Lagoa Grande ele se sobrepunha ao rótulo do pivô. Ganhou fundo branco e fica acima do rótulo do pivô.
4. **Rótulo sob a barra de ferramentas.** Quando a máquina está sob a barra, o rótulo vai para baixo do disco.
5. **Versão com "v" duplicado.** O subtítulo do painel mostrava "vv2". O M3 passou a conferir "OS-0421 · v2" e reprova na versão anterior (19/20).

## Testes executados
Árvore `27a50071` (F1 + composição `d022c745`). Brutos em `brutos/`.

| Teste | Resultado |
|---|---|
| `frota_unit` (node) | 53/53 |
| `mapa_frota` | 20/20 (M1–M5, M7–M10, M12–M16, M18–M20, M24), depois das correções das fotos |
| Contraprova no render da v144 (`RENDER_DIR`) | 0/4: M1, M2, M3 e M12 reprovam (`brutos/contraprova_v144_mapa_frota.log`) |
| Contraprova do "vv" (render antes da correção) | 19/20: M3 reprova (`brutos/apos_fotos/contraprova_vv_mapa_frota.log`) |
| `alocacao_unit` | 21/21 |
| `mapa9` | 13/13 |
| `mapa_filtros` | 7/7 |
| `mapa_faixa` | 25/25 |
| `mapa_cancel` | 6/6 |
| `map_trilha_icones` | 9/9 |
| `talmapa` | 8/8 |
| `colheita_mapa` | 7/7 |
| `mapa_mux_f1` | 43/43 |
| `mapa_mux_f2` | 29/29 |
| `componentes` | 3/3 |
| `ds_1610` | 16/16 |
| `acao_unica` | 10/10 |
| `os_recurso` | 16/16 |
| `os_cenario` | 22/22 |
| `solo_ag02` | 30/30 |
| `solo_saf` | 36/36 |
| `ds` | 72/72 |
| `paginas_scan` | 5/5, nas 147 páginas |

**`regras_toque`:** passou 4/5 na bateria, com três navegadores ao mesmo tempo. O R2 (a dica ⓘ do Mapa a 390 px) espera 1,6 s fixos antes de tocar. Rodando sozinho, passou 5/5 duas vezes (`regras_toque_r1/r2.log`), e na v144 passou 5/5 (`regras_toque_v144.log`). Depois das correções das fotos, 5/5. Uma sonda isolada abriu a dica normalmente no build da F1. Registro como teste sensível à carga, sem esconder a falha.

Depois das correções das fotos, rodaram de novo `mapa_frota` (20/20), `regras_toque` (5/5), `map_trilha_icones` (9/9), `mapa_mux_f1` (43/43), `ds_1610` (16/16) e `frota_unit` (53/53).

**Fotos conferidas em `fotos/`:**
- Santa Rita: com o painel a 1440 e 390 px e com a lista a 390 px;
- Lagoa Grande: com o painel a 1440 px;
- "Ver no mapa" com o recorte temporário.

## Correção K4 (revisão do Codex 6270760702)
**Achado (reproduzido):** duas O.S. Em execução do mesmo grupo, com o mesmo trator e implemento em blocos sequenciais (K4), eram 1 conjunto físico no modelo, mas a tela montava o marcador por O.S. No mesmo ponto aparecia a bolha "2 máquinas", com "Máquinas (2)" e "Lista (2)". O `frMarcadores` passava no K4, mas a tela não o usava. Reprodução no código de `1e927f62`, com `frota.js` e `frota_ui.js` num VM e cenário sintético: `brutos/correcao_k4/repro_antes_1e927f62.log` (`modelItems 2, physicalSets 1, visiblePositions 2, conflicts [0,0]`, bolha "2 máquinas").

**O que mudou (uma regra só):**
- **`frota.js`:**
  - `frEntradas` faz uma entrada por conjunto físico. As O.S. do mesmo conjunto só se juntam quando nenhum componente dele está em conflito, o que equivale ao K4: mesmo grupo, mesmo conjunto, programação do grupo e blocos sem sobreposição.
  - Com conflito (K2, K5, K6), cada O.S. fica com a sua entrada e o selo; conjuntos distintos nunca se juntam (K7).
  - O `frMarcadores` passa a usar o `frEntradas` e recebe os grupos, como o `frConflitos`. Nos casos K2, K4 e K7 a saída é a mesma do oráculo; o oráculo não afirma a contagem de marcadores do K5 e do K6.
- **`frota_ui.js`:**
  - O `frModelo` devolve as entradas. O marcador, o `aria-label`, "Máquinas (N)", "Lista (N)", as linhas da lista e a bolha "N máquinas" passam a contar conjuntos.
  - O marcador do K4 diz "· 2 O.S.". O painel mostra os campos de cada O.S., com o horário da programação; máquina, estado e posição vêm da leitura do marcador (M15). A primária é "Abrir OS-0421" e a secundária, "Abrir OS-0424".
  - "Ver no mapa" de qualquer O.S. do conjunto seleciona o marcador dele, e o Esc devolve o foco a esse marcador.
  - A bolha diz "N máquinas · Conflito" quando alguém nela tem conflito.
  - A lista não repete mais a O.S. em "também na" (antes: "OS-0424, OS-0424", uma vez por componente).

**Testes executados** (árvore de trabalho sobre `1e927f62`, render sintético). Brutos em `brutos/correcao_k4/`:

| Comando (de `gen37/`) | Resultado |
|---|---|
| `node frota_unit.js` | 57/57 (53 + KT1–KT4: K4 na tela, "Ver no mapa" com foco e seleção, K2/K5/K6/K7 na tela e a bolha com conflito) |
| `env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B mapa_frota_test.py` | 23/23 (20 + K4, K4 "Ver no mapa" e o contraexemplo K6) |
| `paginas_scan_test.py` (mesmo ambiente) | 5/5, nas 147 páginas |
| `ds_1610_test.py` (mesmo ambiente) | 16/16 |

**Contraprova no código de `1e927f62`:**
- **`node frota_unit.js <cópias antigas>/frota.js`:** 54/57. KT1, KT2 e KT4 reprovam (`frota_unit_contraprova_1e927f62.log`). O KT3 passa nas duas versões: os casos incompatíveis já mostravam o conflito, e ele protege contra regressão.
- **Navegador:** o bloco K4/K6 do `mapa_frota_test.py` rodou no render com o `frota.js` e o `frota_ui.js` antigos trocados no `IN-04.dc.html`, que os embute literalmente. Resultado 0/3 (`mapa_frota_k4_contraprova_1e927f62.log`):
  - "Máquinas (3)" com a bolha "2 máquinas";
  - "Ver no mapa" da OS-0424 deixa o marcador do conjunto sem seleção, o painel diz "Posição indisponível" e o foco se perde no Esc;
  - a bolha do K6 não diz "Conflito".

**Fotos** (1440 e 390 px, conferidas e não versionadas; texto em `fotos_texto.log`):
- um marcador "T03 · Pulverização · ▶ trabalhando · 2 O.S.", com alvo de 44 × 44 px;
- o painel com as 2 O.S. e as ações "Abrir OS-0421" e "Abrir OS-0424", que a 390 px ficam visíveis na folha inferior;
- a lista com uma linha "OS-0421 e OS-0424";
- o K6 com "2 máquinas · Conflito";
- nenhuma rolagem lateral e nenhum erro de JS.
