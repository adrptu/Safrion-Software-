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
