# EX-55 F1: mapa dentro das telas (18/10/2026)

Pedido do proprietário (18/10): a visão Mapa dentro do próprio submenu (Planejar safra, Ordem de serviço, Irrigação etc.), sem ir ao Mapa principal. Desenho e aceite estão em `../EX-55-validacao-claude.md` (§4 e §7).

## O que entrou

| Tela | Visão nova | O que o toque faz |
|---|---|---|
| Ordens de serviço | Mapa: Fases, Avanço, Atrasos e Impedimentos | Abre a O.S. Com várias O.S. no talhão, abre a lista curta |
| Pragas e doenças | Tabela, Cartões e Mapa, nos últimos 7 ou 30 dias | Abre a vistoria. Sem vistoria no período, abre "Programar vistoria" no talhão |
| Irrigação | Tabela, Cartões e Mapa dos setores: Hoje ou Balanço hídrico | Abre o formulário do setor |
| Planejar safra | Correção: a 2ª linha do rótulo aparece no desenho | Sem mudança |

As três telas usam o mesmo componente (`mapa_emb.py` e `mapa_emb.js`) e as mesmas regras de cor do Mapa da fazenda (`mapa_camadas.js`). O recorte da tela (busca, filtros e situação) vale no mapa e aparece em etiquetas removíveis.

## Como conferir no artefato

1. Abra Agrícola › Ordens de serviço e escolha o ícone de mapa na barra de visões.
2. Em "Mostrar", troque entre Fases, Avanço, Atrasos e Impedimentos.
3. Toque no T1 da Santa Rita: abre a lista com as O.S. do talhão.
4. Abra Pragas e doenças › Mapa, filtre a situação "Acima do NC" e veja só o P1 pintado.
5. Abra Irrigação › Mapa e toque no T7: abre o setor Gotejo T7.

## Testes executados (render `SAFRION_DADOS=sintetico` do commit que traz este arquivo)

| Teste | Resultado | O que prova |
|---|---|---|
| `os_mapa_test` | 20/20 | Paridade com o IN-04 em 124 talhões × Mostrar, recorte com etiqueta, clique, teclado, endereço, 390 px |
| `mip_mapa_test` | 16/16 | Paridade em 62 talhões × período, situação e cultura, clique, programar vistoria, hachura, 390 px |
| `irr_mapa_test` | 12/12 | Paridade nos talhões com setor, busca da Tabela no mapa, clique e Enter, 390 px |
| `saf_mapa_test` | 10/10 | A 2ª linha do rótulo é lida só quando está desenhada |
| `visoes_test`, `visoes_unit_test`, `visoes_perfil_test` | 9/9, 25/25, 13/13 | Seletor de visões na O.S., Pragas e doenças e Irrigação |
| `visoes_calendario_test`, `os_frentes_test`, `paginas_scan_test` | 8/8, 18/18, 5/5 (146 páginas) | Calendário e Frentes depois das correções; nenhuma página com erro |
| `mapa9`, `mapa_mux_f1`, `mapa_mux_f2`, `mapa_filtros`, `map_irrig_filtro` | 13/13, 43/43, 29/29, 7/7, verde | O Mapa da fazenda segue igual |
| Unidade: `mapa_camadas_unit.js`, `os_frentes_unit.js`, `mip_unit_test`, `agua_irr_unit.js`, `irr_onda0_test` | 1255, 17/17, 34/34, 7/7, 28/28 | Regras das camadas, Frentes, MIP e irrigação |

**Contraprova da paridade** (`contraprova_m1.sh`): duas mutações na regra, só na página da O.S. O M1 reprova nas duas:
- a mutação da classe acusa o T4 cinza em vez de "em execução";
- a mutação do rótulo também reprova.

Logs: `logs/contraprova_classe.log` e `logs/contraprova_rotulo.log`.

**Mapa da fazenda (IN-04):**
- A entrada da Irrigação foi para uma fonte única (`irrigacao_estado.js · irrMapaEntrada`) sem mudar a saída: a coleta A2 antes e depois desse passo tem 60 de 60 contextos idênticos (`A2_IN04_pacote.json`).
- A camada O.S. muda de propósito: as O.S. do cenário passam a aparecer, com "sem prazo" quando não há janela. As diferenças estão em `A2_dif_ordens_do_cenario.txt`.

## Defeitos achados e corrigidos

| Defeito | Severidade | Prova |
|---|---|---|
| Mapa e Frentes da O.S. aplicavam a busca da Tabela sem mostrá-la | S3 | `os_mapa_test` M2c a M2e |
| A 2ª linha do rótulo do Planejar safra não aparecia no desenho | S3 | `saf_rotulo_depois.png`, `saf_mapa_test` |
| A Irrigação apagava o `?view` ao trocar de fazenda pelo endereço | S3 | `visoes_unit_test` B4 |
| O IN-04 sobrescrevia a regra de água no solo da Irrigação (0 de 26 setores com CAD) | S2 latente | `irrcad_antes.json` × `irrcad_depois.json` |
| Frentes: "limpeza da plantadeira registrada" sem registro (achado do Codex) | S3 | `os_frentes_unit` U8 e contraprova na versão antiga |

Também corrigido o `visoes_calendario_test`, obsoleto em três pontos: lia a faixa de vários dias (14/10), a Tabela recolhida (v129) e as colunas Início e Fim, que saíram da vista padrão. Já falhava igual na base `29d923c7`; o produto desenhava os 7 dias.
