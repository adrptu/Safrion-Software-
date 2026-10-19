# COLH-APONT F1 · Apontar a colheita na web, 19/10/2026

**Pedido do proprietário (18/10):** "não encontrei no sistema onde faz apontamento da colheita". Lente "leve e fluido" (19/10).
**Especificação:** `docs/gestao/GESTAO-1810.md` §2 (desenho) e §6 (aceite C1–C3).
**Autoria:** Claude. **Revisão:** Codex (regime leve do protótipo, AGENTS §3.5). **Base:** `bf84dcf8` (ponta da composição `claude/v44-v135-osagrupa`). **Branch:** `claude/v44-colh-apont`.

## Resultado útil
Em **Agrícola › Colheita**, o talhão com O.S. de colheita em execução mostra a primária verde **"Apontar colheita"**. Ela abre o painel do talhão já no apontamento do dia:
- **Data:** já com hoje, com os atalhos "Hoje" e "Ontem", editável;
- **Área colhida (ha):** vazia, nunca com o último valor; o saldo a colher da O.S. fica à vista;
- **Horas de colhedora:** opcional;
- **Umidade média (%):** opcional e só como registro; aparece só para grão e café;
- **Perdas na colheita:** opcional e só como registro, na unidade de produtividade da cultura (t/ha no mamão, sc/ha na soja);
- **Observação:** opcional.

Só a área e a data são obrigatórias. Um clique em **"Apontar"** grava, sem confirmação extra. Na hora, o mesmo painel atualiza:
- a lista **"Apontamentos da colheita"**, por dia, com o estado (Provisório, Conferido, Duplicidade a conferir, no aparelho) e quem apontou ("pelo app · Marcos" ou "pela web · Ana (gestora)");
- o saldo a colher e o passe com a nova área e a produtividade (R-02).

O bloco **"Cargas do dia"** mostra as cargas do talhão na data do formulário e o caminho **"Registrar carga ›"**. Ele abre o Recebimento com a pesagem nova, a O.S. e o dia já preenchidos e corrigíveis.

Tarefa C1 medida no teste: **2 cliques e 1 campo digitado** (a primária, a área e "Apontar").

**Dano evitado:** colheita sem registro, produtividade com área inventada, carga sem origem e área somada duas vezes.

## O que mudou
| Arquivo | Mudança |
|---|---|
| `tools/prototipo/v37/gen37/producao.js` | `prTal` (fonte única da Colheita, da camada Colheita do Mapa e do Painel agrícola): O.S. de colheita Em execução, ou só Liberada, dá a ação `apontar`; o passo da previsão que valeria fica em `ac0`. Regras novas: `prApSaldo`, `prApValida`, `prApontarColheita`, `prApLista`, `prApMotivo`. |
| `tools/prototipo/v37/gen37/areas/producao.py` | Painel da COLH: `prPanAp` (formulário, cargas do dia), `prSecAp` (lista e motivo), `prPorTxt` e `prApDiaForm`. A chave nasce no `g2pick`, e a primária do cabeçalho abre pelo mesmo `g2pick`. O Recebimento (CARGA) aceita `#nova:<O.S.>:<aaaa-mm-dd>`. |
| `tools/prototipo/v37/gen37/areas/mobile.py` | MB-10: "Apontar área · OS-…" passou a "Apontar colheita · OS-…", e "Gravar área" passou a "Apontar". |
| `tools/prototipo/v37/gen37/colh_apont_test.py`, `colh_apont_unit.js` | Teste novo: node mais navegador, com C1, C2, C3, O.S. liberada, Registrar carga, 390 px e erro de JS. |
| `tools/prototipo/v37/gen37/producao_fluxo_test.py` | Oráculos trocados pela especificação (ver "Oráculos trocados"). |

`cenario.js` e `cenApontar` não mudaram.

## Decisões
1. **Primária pela fonte única.** A regra está em `prTal`, então a Colheita, o Mapa (camada Colheita) e o Painel agrícola mostram o mesmo próximo passo. Com O.S. de colheita Em execução, ou só Liberada, a primária é "Apontar colheita" (spec §2, C1).
   - Os passos da previsão (Coletar contagem, Publicar previsão, Programar colheita) viram a **secundária** do painel.
   - No Pivô 19, "Publicar previsão" abre o formulário da previsão, com plantas/ha e perda editáveis, e a primária dele publica.
   - A colheita do dia é o fato que se perde se não for registrado. A previsão da semana seguinte continua a um toque.
2. **Mesmo comando do app.** `prApontarColheita` valida e chama `cenApontar` com `origem:'web'` e a chave do formulário (R-07, ENG-021). Assim valem:
   - a mesma duplicidade: na mesma data de um apontamento do app, o novo fica "Duplicidade a conferir" e não soma;
   - o mesmo saldo da ordem;
   - a mesma conferência: entra Provisório e quem confere é o do papel AL-12.

   A chave nasce quando o painel abre e morre no sucesso. O 2º clique de um duplo clique repete a mesma chave e o mesmo conteúdo, então nada duplica.
3. **Umidade e perdas** ficam em `c.producao.apont[<chave do apontamento>]`, o registro da colheita, junto com quem registrou na web. Nunca ficam no `ap`:
   - o `ap` pertence ao comando único (`cenario.js`, trecho do Codex);
   - pôr campos no `ap` mudaria o conteúdo comparado na idempotência.

   A umidade aparece só para grão e café, que têm umidade-padrão no cadastro de unidade. Na fruta seria campo sem uso.
4. **Data futura é recusada** no comando da web (`prApValida`), com o erro junto do campo. O app sempre aponta hoje. O dano evitado é registrar como fato o que ainda não aconteceu.
5. **O.S. só Liberada:** a regra do `cenApontar` não mudou (só soma em O.S. Em execução). O painel mostra o próximo passo com verbo, **"Iniciar a OS-0505"** (verde, leva à O.S.), e não um formulário que não grava.
6. **Sem O.S. de colheita (C3):** não há a primária "Apontar colheita". A lista do talhão traz o motivo e **"Programar colheita ›"**, que leva à O.S. nova já com cultivo, atividade e janela (`OS.dc.html#nova:…`).
   - Com O.S. A liberar, o caminho é "Abrir OS-…".
   - Se a primária já é "Programar colheita", o link não se repete.
7. **Quem apontou:** na web, o perfil que registrou ("Ver como"). O `ap.quem` continua sendo o executor, o responsável da O.S., como no apontamento web da tela O.S.
8. **Nome igual no app e na web** (regra de ouro): no app, "Apontar área" virou "Apontar colheita" e "Gravar área" virou "Apontar".
   - A tela O.S. continua com **"Registrar apontamento"**. Ela vale para todas as operações (pulverização, plantio…), pelo mesmo comando, e um nome por tipo de operação dentro dela criaria a inconsistência que a regra quer evitar.
   - As horas continuam obrigatórias no app (turno do operador) e opcionais na web (escritório), como pede a especificação.

## Comandos e resultados (executados em 19/10, árvore desta branch, dados sintéticos)
Todos em `tools/prototipo/v37/gen37`. Build: `SAFRION_DADOS=sintetico python3 -W error::SyntaxWarning -B build.py && python3 -B montar_render.py` (155 páginas). Navegador: `env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico`, um teste de cada vez.

| Comando | Resultado | Bruto |
|---|---|---|
| `python3 -B colh_apont_test.py` (U: 15 no node · C1 ×7 · C2 · C3 · L · R · M ×2 · E) | **29/29** | `colh_apont_test.log` |
| **Contraprova:** o mesmo teste com `RENDER_DIR=<render de bf84dcf8>` | **reprova: 16 ok · 13 falhas** (sem a primária "Apontar colheita"; ver abaixo) | `colh_apont_contraprova_base.log` |
| `producao_fluxo_test.py` (os, fluxo, erros, celular, revisao, unid) | **93/93**; AC-17: 14 cliques e 5 campos (teto 30 e 5) | `producao_fluxo_test.log` |
| `producao_fluxo_test.py` antes de trocar os oráculos | 15/20 até parar: só os passos do §8.1 que mudam por C1 | `producao_fluxo_antes_oraculo.log` |
| `producao_unit_test.py` (inclui: nenhum nome de `producao.js` redefinido pelo JS das telas) | 160/160 | `producao_unit_test.log` |
| `colheita_mapa_test.py` | 7/7 | `colheita_mapa_test.log` |
| `painel_agricola_test.py` | 81/81 | `painel_agricola_test.log` |
| `filtros_cultura_test.py` | 11/11 | `filtros_cultura_test.log` |
| `mapa_mux_f0_test.py` | 17/17 | `mapa_mux_f0_test.log` |
| `ds_1610_test.py` | 16/16 | `ds_1610_test.log` |
| `os_cenario_test.py` | 22/22 | `os_cenario_test.log` |
| `app_cenario_test.py` | 15/15 | `app_cenario_test.log` |
| `textos_soltos_test.py` | 267 ok · 0 falhas (64 telas) | `textos_soltos_test.log` |
| `links_ocultos_test.py` | 16 · 0 falhas | `links_ocultos_test.log` |
| `paginas_scan_test.py` | 5/5 (147 páginas) | `paginas_scan_test.log` |
| `mbtest.py` | 1 falha (MB-02, excesso de 220 px), **igual à base** (vermelho já registrado na Base verde 2); MB-10 sem falha | `mbtest.log`, `mbtest_BASE.log` |
| `cafe_apurar_test.py` | unit 17/17; nav 6/10, **igual à base** (as 4 falhas leem a linha e o cartão do C1, vazios nas duas árvores; nenhuma depende desta fatia) | `cafe_apurar_test.log`, `cafe_apurar_test_BASE.log` |
| `ap_unico_test.py` | 6/13 no node e parada no navegador, **igual à base** (a montagem do motor JS do teste põe um comentário Python `#` dentro do JS: erro de montagem do teste) | `ap_unico_test.log`, `ap_unico_test_BASE.log` |
| `reserva_duplo_clique_test.py` | parada no início (`CLK` sem definição na página), **igual à base** | `reserva_duplo_clique_test.log`, `reserva_duplo_clique_test_BASE.log` |

### Contraprova
O render da base `bf84dcf8` foi montado de uma árvore separada da mesma base. Nele, o `colh_apont_test.py` reprova nos 13 itens de tela:
- a primária é "Publicar previsão do Pivô 19";
- não há formulário de apontar nem lista de apontamentos;
- C3 não tem o motivo nem "Programar colheita ›";
- a O.S. liberada não tem "Iniciar a OS-0505";
- o Recebimento não aceita a O.S. e o dia pelo endereço;
- o app mostra "Apontar área".

Passam os 15 itens do node (eles leem as regras da árvore desta branch, não o render) e o "sem erro de JS".

### Oráculos trocados (`producao_fluxo_test.py`), com o motivo
Motivo único: a especificação C1 tornou "Apontar colheita" a primária do talhão com O.S. de colheita em execução. Não foi feito para o teste passar.
- §8.1: sem seleção, a primária do Pivô 19 é "Apontar colheita do Pivô 19" (antes "Publicar previsão do Pivô 19").
- "Publicar previsão" é secundária do painel e abre o formulário; a primária dele publica. Isso dá mais 1 clique na tarefa do proprietário (AC-17 = 14 de 30).
- Depois de publicar, a primária continua "Apontar colheita", e "Programar colheita S40" é a secundária do painel (antes era a primária). A-04 e A-16 (revisao) e o rascunho do `unid` passam pela mesma secundária.
- MB-10: "Apontar colheita · OS-0505" e "Apontar" (antes "Apontar área" e "Gravar área").

Nenhuma asserção de valor mudou: área, produção, produtividade, versões e cargas são as mesmas.

## Fotos olhadas (fora do git, scratchpad)
- `colh_1440_painel.png`: painel do Pivô 19 com 20 ha digitados.
- `colh_1440_lista.png`: depois de apontar, a lista com 26/09 provisório e o saldo 5,11 ha.
- `colh_1440_c3.png`: T1-A Soja, com o motivo e "Programar colheita ›".
- `colh_1440_liberada.png`: "Iniciar a OS-0505".
- `colh_390_painel.png` e `colh_390_lista.png`: celular, com o "Apontar" preso ao rodapé do painel.

Nas fotos não há desalinhamento nem peça fora do lugar. O painel é o componente comum (`painel()`/`prPainel`), sem estilo local. Há uma só primária verde por contexto (BOT-01).

## Limitações e fora desta fatia
- **Conferência do apontamento** (Provisório → Conferido): continua na Conferência diária. O painel só mostra o estado.
- **Apontamento por parcela** (`parc`): não exposto na web, como no app. O apontamento vale para o talhão da O.S.
- **Rótulo da tela O.S.** ("Registrar apontamento"): mantido, pelo motivo da decisão 8.
- **"Registrar carga ›"** leva à pesagem do Recebimento (carga que chega à balança). A carga "A pesar" registrada no campo continua no app (MB-10).
- **Mês fechado e ajuste no período seguinte** (K3): é a fatia FECH-1.

## Vermelhos da base (não desta fatia)
Os quatro testes abaixo falham igual na base `bf84dcf8`. A prova é rodar o mesmo teste no render de uma árvore separada da base, com os brutos `*_BASE.log`.
- `cafe_apurar_test.py` (nav);
- `ap_unico_test.py`;
- `reserva_duplo_clique_test.py`;
- `mbtest.py` (MB-02).

Nenhum oráculo deles foi mexido. Ficam para a frente Base verde.
