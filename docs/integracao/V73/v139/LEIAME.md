# v139: VIS-08, modo de visão pelo ícone em toda tela (19/10/2026)

**Pedido do proprietário (18/10):** "O modo de visão em mapa em planejar safra tem que ser pelo ícone igual os demais que você fez". O padrão está em `docs/design-system/padroes-1810.md`.

**Código:** commit `37c3ecb6` em `claude/v44-v135-osagrupa`, sobre a base `7aa910df`.
- **Mudam 4 páginas:** `SAF.dc.html`, `CD-01.dc.html`, `BEN.dc.html` e `MA.dc.html`.
- **Build do commit limpo:** idêntico ao render testado, 179 arquivos e 0 diferenças por sha256.

## Testes executados (render `SAFRION_DADOS=sintetico`)

**Brutos:**
- `logs/bateria43/`: a bateria de 43 testes no navegador e os testes de unidade (`resumo.txt`).
- `logs/repeticao/`: os testes corrigidos rodados de novo.
- `logs/repeticao/base_v138/`: os mesmos testes no render da v138, para separar a falha que já existia.
- `logs/contraprova_visao_icone_v138.log`: a contraprova.

| Grupo | Resultado |
|---|---|
| `visao_icone_test` (novo) | 1/1: 110 seletores em 66 telas. A contraprova na v138 reprova SAF, CD-01 (2 grupos) e BEN |
| Unidade | `visoes_unit` 26/26, `ds_unit` 31/31 |
| Telas mudadas | `saf_mapa` 10/10, `saf_lote` 47/47, `cadf` 15/15, `cadf_fix_lista` 11/11, `cadastros_padrao` 44/44, `cadastros_rev1` 19/19, `tabelas_cad` 206/206, `cartoes` 70/70, `man_limpa` 9/9, `ma_unica` 23/23, `ma_rastreio` 58/58, `ma_vinculo` 101/101, `ma_menu` 10/10, `ma_planos` 18/18, `ma_atrito` 13/13, `tabelas_ben` 12/12 |
| Gerais | `paginas_scan` 5/5 (146 páginas), `ds_test` 72/72, `ds_padrao` 17/17, `ds_1510` 17/17, `ds_1610` 16/16, `ds_man` 99/99, `visoes` 9/9, `visoes_perfil` 13/13, `links_ocultos` 16/16, `nav_modulos` 15/15, `seta_padrao` 14/14, `busca_unica` 7/7 |

**Vermelhos que não vêm da VIS-08.** São iguais na v138 e vão para a base verde:
- `cadf_det_test`: quebra no passo 3 do mesmo jeito na v138. O teste foi corrigido para abrir a árvore e falta rodar de novo.
- `producao_fluxo_test`: 15/20, com as mesmas 5 linhas na v138.
- `ben_fluxo_test`, na verificação "Estoque de produto a 390 px": procura `.pr-card`, mas a classe só existe no CSS. O `PROD.dc.html` é idêntico ao da v138.

**`nav_modulos`:** na bateria de 43, com 3 navegadores em paralelo, estourou a espera de 6 s ao abrir a O.S. Rodado de novo com a máquina livre, deu 15/15.

## Prova visual (executada)

`fotos/`: as 4 telas em 1440 e 390 px, conferidas uma a uma.
- Em 390 px, na Manutenção › Ordens, o seletor fica no fim da linha dos filtros de fase, que rola na horizontal. Isso já era assim antes.
- A foto `cd01_lista_390` abre no Mapa porque guarda a última visão escolhida, por perfil (VISOES-1).

## Publicação (19/10/2026)

A v139 publicada (versões 149–151, recibo em `../artefato-v139/LEIAME.md`) leva, além da VIS-08:
- o PR #121 (EX-57 F0c) e o PR #122 (EX-53 F1a parte 1), ambos do Codex;
- o PR #125 (EX-53 F1a parte 2, do Claude).

Provas e aceites:
- **Bloco A** (VIS-08 + #121 + #122): brutos em `logs/blocoA/`. O `visual_corte` e o `ben_fluxo` são iguais à base, e o aceite do Codex está em 6258622734.
- **F1a parte 2:** provas em `../ex53-f1a2/`. A revisão e a integração foram do Codex (PR #125, `f44ab371`).
