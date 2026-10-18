# Recibo da publicação do artefato v131 (18/10/2026): Manutenção no padrão do Agrícola (DS-MAN) e Compras → Estoque por linha (C-3/C-4)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm. Versões 135 (`1792328392-2f38`) e 136 (`1792328405-e047`), em 2 lotes; o estado completo é a 136.
- **Antes de enviar:** a versão publicada era a v130 (versão 134).
  - A listagem conferiu os hashes de EST e CMP com o espelho.
  - Mudaram 60 páginas. As outras 88 e os arquivos de apoio são iguais byte a byte e não foram reenviados.
  - O prefixo do cenário (Compras) vai em toda página que o carrega; por isso são tantas.
- **Leitura de volta, sha256 igual ao espelho:**

  | Página | sha256 |
  |---|---|
  | `CMP.dc.html` | `7589d077…` |
  | `EST.dc.html` | `ccee35d6…` |
  | `MA.dc.html` | `3be9d32d…` |
  | `MOD-MAN.dc.html` | `59eb6749…` |

- **Origem:** `c65df394` (worktree `intn1`) = v130 (`684b3459`) + DS-MAN (`e8cfef9c`, `17fca80a`) + C-3/C-4.
  - C-3/C-4 entra com o PR #114 até `e257902a` e os patches do integrador `1f268b45`, `efb479e9` e `f5857498`.
  - O commit seguinte (`9f2c178a`) só mexe em teste; a montagem do produto é a mesma.
- **Montagem:** `_render` às 12:20:03 UTC, depois do commit `c65df394` (12:19:46), com a árvore do produto limpa.
- **O que a pessoa vê:**
  - Manutenção:
    - título da visão;
    - abas com número só do que pede ação;
    - lista num bloco com título;
    - linhas de até 2 linhas;
    - entrada em blocos Cadastro, Execução e Resultados, com a linha "N ativos sem plano · Vincular ›";
    - relatório em `../ds-man/LEIAME.md`.
  - Compras:
    - a compra aprovada vira pedido por linha no Estoque;
    - o recebimento parcial baixa a linha certa;
    - a etapa 6 mostra Recebido, Em quarentena (agora) e A entregar por linha;
    - a mesma NF pode trazer vários itens do mesmo pedido;
    - o Planejar safra mostra "Pedidos emitidos".
- **Provas:** bateria cruzada das duas frentes no render final (`bateria/resumo.txt`).
  - c34_test 19 PASS; c34_paridade 6/6; n1_composicao 7/7 (`bateria/n1_composicao_pos.log`); est_onda0 24/24; mip_unit 34/34; legal_unit 35/35.
  - c34_fluxo 17/17; n1_fluxo 10/10; ds_man 99/0; ma_vinculo 101/101; ma_unica 23/23.
  - compras_materiais 32/32; d5_reserva 13/13; est_a4_nav 15/15; tabelas_est 34/34; tabelas_os 40/40; mip_fluxo 15/15.
  - ds_test 72/72; paginas_scan 5/0 (148 páginas); links_ocultos 16/0.
  - DS-MAN: bateria da Manutenção em `../ds-man/logs/`.
  - Contraprova do C-3/C-4: sem o patch do Q3, c34_fluxo dá 15/17 (`c34_fluxo_contraprova.log`).
- **Vermelhos antigos:** iguais aos do render da v130, caso a caso (`c34-base130/`).
  - demanda_unica 60/71; saf_cmp_continuidade 14 e 16.
  - est_fix1, est_fix2, est_cenario, est_laudo_lote_nav e esttest: oráculos das grades recolhidas (TAB-12).
  - demanda_estado_nav e demanda_unica_nav.
  - nav_modulos: a entrada do Crédito diverge do menu.
  - mbtest MB-02.
  - Ficam para a base verde 2.
- **n1_composicao:** a 1ª rodada deu 6/7. Era o teste: o recorte do `cenario.js` não incluía a marca de Compras que o `cenReset` passou a chamar. Corrigido em `9f2c178a`; a contraprova continua reprovando 6 de 7.
