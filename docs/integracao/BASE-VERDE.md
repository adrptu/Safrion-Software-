# BASE-VERDE · vermelhos antigos da v55/v56 zerados (executado)

Regime leve do protótipo (AGENTS.md 3.5). Sem push, sem PR, sem publicação. Dados sintéticos (`SAFRION_DADOS=sintetico`).

- **Base:** `302b26f` (candidata v56 sem a CTL-4), worktree `/home/user/sp-verde`, branch local `claude/v44-base-verde`.
- **Objetivo:** tirar os vermelhos iguais nos dois lados (v55 × v56) que obrigavam toda bateria a rodar duas vezes (versão anterior × candidata) só para separar o antigo do novo.
- **Ambiente:** Chrome headless (Chromium 141 do Playwright, `/tmp/cloudchrome/chrome`) por CDP, um teste de navegador por vez na trava `/tmp/cdpB.lock`: `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpB.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 <teste>`, de `tools/prototipo/v37/gen37`.
- **Regra seguida:** nenhum teste ficou mais fraco. Nenhuma asserção foi removida e nenhuma tolerância aumentou. Onde o oráculo mudou, a mudança cita a regra vigente e foi provada contra mutantes, isto é, o produto com o defeito que o teste existe para pegar. Os mutantes rodaram numa cópia do `gen37`, com a troca aplicada e desfeita por um script. Os brutos estão em `BASE-VERDE/brutos/`.

## 1. Vermelho × causa × correção × commit × prova

Antes: reprodução nesta base (`brutos/reproducao/`), igual à V56. Depois: o mesmo teste no código corrigido.

| Vermelho (base) | Causa | Correção | Commit | Prova |
|---|---|---|---|---|
| `agrofit_test` item 3 (selo "Base atualizada · 02/10/2026") | **Relógio.** O selo compara o arquivo do AGROFIT (Last-Modified 02/10/2026) com `Date.now()` e marca a base como desatualizada depois de 7 dias (`agDiasArq() > 7`; validade por fonte, DEC-0910-13 b). A partir de 10/10 o item falhava em qualquer versão. | O navegador do teste usa um relógio fixo em 05/10/2026 12:00 BRT (outro dia com `?relogio=`). O item ficou mais forte: confere também o limite com o mesmo arquivo. Com 7 dias (09/10) a base segue em dia; com 8 dias (10/10) aparece "Base de 02/10/2026 · desatualizada". | `783f70a` | Antes 17/18, depois 18/18. Mutantes `agDiasArq()>99` (nunca vence) e `agDiasArq()>-1` (sempre vencida): o item 3 falha nos dois. |
| `os_cenario_test` item 1 ("cenário v2 sem aprov") | **Teste desatualizado.** O teste exigia `c.v == 2`. Pela regra de `cenario.py`, a semente sobe de número a cada mudança (v=2 em 01/10 tirou o aprov; hoje é v=7). | O cenário lido tem de ser a semente da própria página (`CEN0.v` do `OS.dc.html` servido), e a semente não pode ser anterior à v=2. O resto do item não mudou: A liberar sem aprov, sem selo, Liberar + Ajustar, área 0 recusada. | `5d2208f` | Antes 20/21, depois 21/21. Mutante com a semente em `"v": 1`: o item 1 falha. |
| `ostest` "painel da nova ordem A liberar…" (OS-0440) | **Teste desatualizado.** A revisão do CTL-1 (achado 1, `2e52e2b`) e a AGR-07 fizeram a unidade diferente da bula travar a liberação. O plano Soja AT v6 tem o Inseticida B em L/ha e a bula é em kg/ha. `legal_unit.js` N11 e `os_cenario_test` 14e já cobram isso. | O item confere o motivo exato ("…dose em L/ha e bula em 0,8–1 kg/ha: unidade diferente da bula") e quem resolve (Ana). Confere também que não há botão "Liberar para execução", que há "Ajustar antes de liberar" e que não há selo de agrônomo. | `2a24216` | Antes 32 ok · 1 falha, depois 33 · 0. Mutante em que a unidade volta a ser só alerta (`tr.push` → `al.push`): o item falha, porque o painel volta a mostrar Liberar. |
| `osacoes` 5 falhas (percentual, dono OS-0430, rolagem, recusa, saldo/dispensado) | **Teste desatualizado.** A TABELAS-FOCO, incremento 1 (pedido 5983172395, `5ad4cad`), trouxe uma variável por coluna e a rolagem dentro da caixa (item 6). O `ostest` e o `os_cenario_test` mudaram naquele commit; o `osacoes` ficou com os textos antigos. | `cel(id, coluna)` igual a `os_lib.Os.cel`, com valores exatos: Área, Realizado, Progresso 54,3 %, Saldo e Dispensado; Quem resolve "Ana (agrônoma)" e Prazo "antes de 25/09". Rolagem: a página não rola de lado, a tabela cabe ou rola dentro da caixa (overflow-x auto/scroll), e a 1ª coluna e o filtro Talhão ficam à vista. | `9193ae2` | Antes 40 ok · 5 falhas, depois 45 · 0. Cada um destes mutantes faz o teste falhar: saldo sem descontar a dispensa; Dispensado vazio; progresso arredondado a 54,0 %; ação e prazo na mesma coluna; `.g2rola` com overflow visible (a caixa deixa de rolar: 2150 px de tabela em 1116 px de caixa); dispensa sem o limite de 20 % (a recusa some e o saldo vai a 0). Um mutante equivalente: Dispensado 0, que a coluna mostra como "—". |
| `componentes_test ajustes` 26 (CULTIVOS no SAF, Natureza de custo no CD-06, PEDIR ATÉ no SU-01 a 360 px) | **Ambiente.** A aba aberta por `/json/new` fica em segundo plano e, depois da 1ª navegação, o documento perde o foco da janela (`document.hasFocus()` false). Assim `focus()` não dispara focusin, e o g2lib não leva à vista o cabeçalho que estava só em parte visível (scrollLeft ficava em 0). Não era a largura do cabeçalho: a nota da V56 sobre o CD-06 cai aqui. | `comp_lib.Chrome` chama `Page.bringToFront` ao abrir a aba, como o `ds_test` já fazia. O teste não mudou. | `ef07af8` | Antes 2 ok · 2 falhas, depois 3 · 1 (o 27 cai no commit seguinte). Mutante sem a rolagem do foco do g2lib no SAF: o 26 volta a falhar em CULTIVOS. |
| `componentes_test ajustes` 27 (Tab depois do último item do menu) | **Teste desatualizado.** O CTL-3 (`0b99e0e`) pôs no fim do menu o seletor "Trocar perfil de demonstração", um select. O teste focava o último a/button: o 1º Tab ia ao select e o 2º ao botão do menu, que não fecha o menu. | O "último item" passou a ser o último controle focável do menu, e o log mostra qual foi. As larguras são medidas depois que a transição do menu acaba (`getAnimations`, até 3 s): com a máquina carregada, 0,18 s de CSS passavam de 0,35 s. Os valores esperados não mudaram. | `0a367bc` | Antes FALHA, depois 4/4. Mutante em que o g2lib não fecha o menu quando o foco sai para o conteúdo: o 27 falha. |
| `componentes_test interacao` 10 e 14 (hover) | **Ambiente.** O headless do Linux não tem dispositivo apontador e responde `(hover:none)`. O Chromium 141 aceita e ignora `setEmulatedMedia` hover/pointer. Desligar a emulação de toque também tira o mouse. | `comp_lib.Chrome(mouse=True)` usa a mesma chave `--blink-settings` do `ds_test`. `aparelho()` só desliga o toque se ele foi ligado. O modo interacao usa mouse; o item 12 (toque) roda num Chrome próprio e devolve o Chrome com mouse aos itens 13 a 19. O item 18 mede depois da transição (`assenta`): num mutante sem relação com ele, marcou 232 px aos 0,35 s. | `33352f4` | Antes 8 ok · 2 falhas, depois 10 · 0 (duas vezes). Mutante sem `.g2card:hover`: o 10 falha. Mutante sem o hover do menu lateral: o 14 falha. |
| `etapas_celular_test complemento` 17 (O.S. e AG-07 a 720×450 @2) | **Defeito do produto (S4).** Em tela baixa quem rola é a coluna `.ml-tog+div`, que só tinha o respiro de cima. O `main[data-scroll]` tem 8 px em cima e embaixo. Levar à vista a última linha parava 6 px abaixo da borda: linha em 422–456 numa janela de 450. | `ui37.py`: `scroll-padding-bottom:8px` na coluna. O teste não mudou. | `94eb487` | Antes FALHA, depois complemento 9/9. Mutante sem o respiro novo: o 17 falha. |
| `etapas_celular_test complemento` 20 (SAF 800×360 sem folha) | **Teste desatualizado.** Com 4 etapas desde `8a08de9` (SAF etapa única), a faixa do SAF cabe inteira a 800 px e não fica compacta, então não há folha. A regra da faixa é a do item 16: completa sem sobreposição, ou compacta. | Compacta: o mesmo critério de antes (folha fixa, última etapa à vista ou tocável). Completa: todas as etapas na faixa, nenhuma vazando ou sobreposta, sem folha e com a última à vista. A 568×320 o SAF segue compacto. | `6059775` | Antes FALHA, depois 9/9. Mutantes: folha do CMP sem position:fixed e etapas do SAF sobrepostas (46 sobreposições). O 20 falha nos dois. |
| `etapas_celular_test faixa` 16 (CMP e SAF a 1400 px) | **Teste desatualizado.** A varredura contava como vazamento o texto só para leitor de tela (`.etp-sr`, "· etapa atual"). A função MEDIR do mesmo teste já o descontava. Todos os retângulos "fora" eram o `.etp-sr`. | A VAR esconde o `.etp-sr` durante a medida, como a MEDIR. | `53e7444` | Antes 0 ok · 1 falha, depois 1 · 0. Mutante com os rótulos do CMP em 60 px sem quebra: o 16 falha. Um mutante sem !important é equivalente, porque o `min-width:min-content` do produto vence. |
| `etapas_celular_test desktop` 15 (falta `gen37_antes`) | **Ambiente / referência ausente.** A referência era `../gen37_antes/_render`, uma cópia feita à mão que não existe fora da máquina de quem a fez. Com a referência no lugar apareceram dois motivos de tempo, não de desenho: (a) a barra de carga entre telas (DS-RETORNO, `#g2-carga`), passageira, entrava na foto de um lado e não do outro; (b) a foto podia sair antes da montagem da tela (`g2montou`, 60 ms depois do 1º desenho): de um lado já havia o anúncio "Tela: …" do `#g2-vivo` (1×1 px, só para leitor de tela) e do outro não; no AG-07, de um lado ainda "Carregando culturas e alvos…" do AGROFIT. | O teste monta a referência sozinho: `git archive` do commit fixo `REF_DESKTOP = 302b26f`, depois `build.py` e `montar_render.py`, em cache por commit e modo de dados (`~/.cache/safrion-gen37-ref`). `ANTES_DIR` e `ANTES_REF` continuam mandando. A foto da geometria é tirada, nos dois lados, quando a tela assentou (até 3 s): a montagem já rodou (a barra existe), a barra terminou e não há "Carregando" na tela. Se não assentar em 3 s, a foto sai assim mesmo e a diferença aparece. O que ele compara não mudou: todos os elementos a 1440 px, menu aberto e recolhido, em todas as telas. | `46227fe` (referência e espera da barra) e `907eb4d` (espera da montagem e do "Carregando"; conferido na retomada) | Antes "base ausente". Só com a espera da barra: a fatia 30:45 passou duas vezes e a tela inteira passou uma vez (814 s), mas a repetição falhou em COLH, IN-03, MB-07, OS (anúncio) e AG-07 (Carregando) (`desktop-espera/1-…`). Com a espera da montagem: tela inteira 1/1 (769 s) e controle sem mutação duas vezes 1/1 (`desktop-espera/2-…`). Mutantes que o 15 pega: 30 px a mais no topo do main do CMP (menu aberto) e menu recolhido com 80 px em vez de 68 px na O.S. (`e15_assenta_muda*`). A referência em cache é idêntica, byte a byte, a uma montagem nova de `302b26f` (`desktop-espera/3-referencia-reconstruida.txt`). Bateria completa: seção 2. |

## 2. Bateria completa da v56 depois das correções

Executado uma vez, na trava `/tmp/cdpB.lock`, numa árvore limpa: `inicio 11:23:43 HEAD 0900d59 árvore v37 907ecf0 · árvore limpa: 0 arquivos alterados`; `fim 12:54:59 · árvore limpa: 0 arquivos alterados`. O código é o desta entrega (árvore `tools/prototipo/v37` = `907ecf0`, a mesma de `907eb4d` em diante; os commits seguintes só mudam `docs/`). Montagem única antes da bateria: `build.py` 138 quadros, 0 FALHA; `montar_render.py` 145 páginas, dados sintéticos 5/5. Lista: a mesma da V56 (`brutos/scripts/lista_bateria.txt`), com o desktop nas fatias 0:73 e 73:145 (seção 4). Brutos em `brutos/bateria-final/`.

**Resultado: 55 testes de navegador e 17 sem navegador, todos com rc=0 e sem falha. Zero vermelhos.** Os 9 testes que estavam vermelhos na V56 (coluna do meio; o desktop conta uma vez, em duas fatias) estão verdes. Nenhum vermelho novo.

| Teste | V56 (302b26f) | Agora | rc | Tempo |
|---|---|---|---|---|
| `varredura` | verde | 145/145 páginas sem erro | 0 | 372 s |
| `acoes_duplicadas` | verde | 145 páginas · 0 com ação repetida · erros 0 | 0 | 240 s |
| `ds_test` | verde | OK 68/68 | 0 | 291 s |
| `componentes_matriz` | verde | 3 ok · 0 falhas (matriz) | 0 | 86 s |
| `componentes_rotacao` | verde | 6 ok · 0 falhas (rotacao) | 0 | 48 s |
| `componentes_interacao` | 8 ok · 2 falhas (10, 14) | 10 ok · 0 falhas (interacao) | 0 | 46 s |
| `componentes_ajustes` | 2 ok · 2 falhas (26, 27) | 4 ok · 0 falhas (ajustes) | 0 | 68 s |
| `componentes_ajustes2` | verde | 2 ok · 0 falhas (ajustes2) | 0 | 68 s |
| `tabelas_cad_test` | verde | 178/178 ok | 0 | 327 s |
| `tabelas_irr_test` | verde | 106/106 ok | 0 | 209 s |
| `irtest` | verde | 26 de 26 verificações OK | 0 | 51 s |
| `irr_fluxo_test` | verde | 33 ok · 0 falhas [] | 0 | 146 s |
| `irr_estado_test` | verde | 38 ok · 0 falhas [] | 0 | 14 s |
| `map_irrig_filtro_test` | verde | 15 ok · 0 falhas [] | 0 | 26 s |
| `cada_cd03_test` | verde | OK 14/14 | 0 | 17 s |
| `cada_fix03_test` | verde | OK 11/11 | 0 | 19 s |
| `cadc_cd06_test` | verde | OK 14/14 | 0 | 26 s |
| `cadc_fix_cd06` | verde | OK 13/13 | 0 | 36 s |
| `ctl5_test` | verde | 30/30 [] | 0 | 81 s |
| `agrofit_test` | 17/18 (item 3) | 18/18 ok · 40 s [] | 0 | 41 s |
| `carencia_test` | verde | 91/91 verificações | 0 | 82 s |
| `ficha_pivo_test` | verde | OK 21/21 | 0 | 76 s |
| `praga_alvo_test` | verde | 14/14 ok · 49 s [] | 0 | 50 s |
| `solo_saf_test` | verde | OK 36/36 | 0 | 119 s |
| `solo_os_test` | verde | OK 18/18 | 0 | 75 s |
| `solo_ag02_test` | verde | OK 32/32 | 0 | 58 s |
| `solo_rev_test` | verde | OK 22/22 | 0 | 174 s |
| `tabelas_os_test` | verde | 38/38 ok | 0 | 36 s |
| `tabelas_saf_test` | verde | 24/24 ok | 0 | 44 s |
| `tabelas_est_test` | verde | 34/34 ok | 0 | 33 s |
| `map_aprov_test` | verde | 5 ok · 0 falhas [] | 0 | 15 s |
| `map_decisoes_test` | verde | 18 ok · 0 falhas [] | 0 | 52 s |
| `pa_lista_test` | verde | 24 ok · 0 falhas | 0 | 127 s |
| `patest` | verde | 46 ok · OK | 0 | 32 s |
| `acao_familias` | verde | 8 ok · 0 falhas (familias) | 0 | 64 s |
| `acao_v3` | verde | 10 ok · 0 falhas (v3) | 0 | 121 s |
| `acao_responsivo` | verde | 5 ok · 0 falhas (responsivo) | 0 | 88 s |
| `acao_saf` | verde | 10 ok · 0 falhas (saf) | 0 | 70 s |
| `etapas_celular` | verde | 14 ok · 0 falhas (celular) | 0 | 44 s |
| `etapas_complemento` | 7 ok · 2 falhas (17, 20) | 9 ok · 0 falhas (complemento) | 0 | 50 s |
| `etapas_desktop_a` | 0 ok · 1 falha (15: base ausente) | 1 ok · 0 falhas (desktop) | 0 | 365 s |
| `etapas_desktop_b` | (idem) | 1 ok · 0 falhas (desktop) | 0 | 364 s |
| `etapas_faixa` | 0 ok · 1 falha (16: CMP, SAF) | 1 ok · 0 falhas (faixa) | 0 | 45 s |
| `comercial_revisao_test` | verde | OK 33/33 | 0 | 117 s |
| `comercial_fluxo_test` | verde | OK 72/72 | 0 | 139 s |
| `producao_fluxo_test` | verde | OK 67/67 | 0 | 270 s |
| `reserva_duplo_clique_test` | verde | OK 2/2 | 0 | 11 s |
| `partest` | verde | 50 ok · 0 falhas | 0 | 100 s |
| `ma_unica_test` | verde | 23/23 ok | 0 | 191 s |
| `dose_divergente_nav` | verde | 21/21 ok · FALHAS: 0 | 0 | 74 s |
| `cafe_apurar_nav` | verde | OK 10/10 | 0 | 31 s |
| `ostest` | 32 ok · 1 falha (OS-0440) | 33 ok · 0 falhas [] | 0 | 26 s |
| `os_cenario_test` | 20/21 | 21/21 ok | 0 | 41 s |
| `osacoes` | 40 ok · 5 falhas | 45 ok · 0 falhas | 0 | 29 s |
| `cadc_cd02_test` | verde | OK 15/15 | 0 | 27 s |

| Teste sem navegador | Agora | rc |
|---|---|---|
| `ds_unit_test` | OK 44/44 : OK 29/29 | 0 |
| `tabelas_cad_irr_unit` | 49/49 ok | 0 |
| `outorga_unit_test` | 27/27 | 0 |
| `usar_os_unit_test` | 24/24 | 0 |
| `ficha_pivo_unit_test` | 23/23 | 0 |
| `praga_alvo_unit_test` | 21/21 | 0 |
| `solo_unit_test` | OK 126/126 | 0 |
| `pa_regras_test` | 18/18 | 0 |
| `comercial_unit_test` | OK 114/114 | 0 |
| `producao_unit_test` | OK 123/123 | 0 |
| `ben_unit_test` | OK 168/168 | 0 |
| `ma_regras_test` | 150/150 ok | 0 |
| `ma_app_test` | 36/36 ok | 0 |
| `os_aprov_lib_test` | TOTAL 45 · falhas 0  passou · TOTAL 45 · falhas 0 | 0 |
| `dose_divergente_unit` | unit: 35/35  unit Início: 2/2 | 0 |
| `cafe_apurar_unit` | unit: 16/16 | 0 |
| `links_ocultos_test` | TOTAL 14 · falhas 0 | 0 |

`brutos/bateria/` é uma prévia da mesma lista rodada antes destas conferências, em `53e7444` com o `etapas_celular_test.py` alterado e sem commit (árvore suja). Ela não vale como prova de nenhum commit. Também deu tudo verde, mas a repetição do desktop daquela versão falhou (seção 1).

## 3. Fora desta base (só registro)

Vermelhos da CTL-4 (frente `sp-ctl4`, fora da `302b26f`), não tratados aqui: `consumo_divergente_test` 20 e 21 e `testes_pedido` T01, T02 e T05. Entram com a junção da CTL-4.

## 4. O que muda para quem roda a bateria

- **Uma rodada basta para estes testes:** nenhum deles depende mais de rodar a versão anterior para separar vermelho antigo de novo.
- **`comp_lib.Chrome`:** a aba vem para a frente e o documento fica com foco de janela, como com quem usa. Com `mouse=True`, o Chrome tem hover e ponteiro fino. `aparelho()` só desliga o toque se ele foi ligado; para quem não usa `mouse=True` isso não muda nada.
- **`etapas_celular_test desktop`:**
  - A 1ª rodada monta a referência de `302b26f` (cerca de 20 s) e as seguintes usam o cache.
  - A chave do cache é o commit (o `git archive` de uma árvore limpa leva junto o gerador daquele commit: `build.py`, `montar_render.py` e dados sintéticos) mais o modo de dados (`SAFRION_DADOS`). A montagem pronta não é refeita nem alterada; uma montagem nova do mesmo commit saiu idêntica byte a byte (`brutos/desktop-espera/3-referencia-reconstruida.txt`). Cada execução abre o Chrome com perfil novo (`mkdtemp`).
  - A comparação completa levou de 769 s a 879 s com a máquina carregada, perto do limite de 900 s. Por isso a bateria roda o desktop em duas fatias, `desktop 0 73` e `desktop 73 145`, que o próprio teste prevê ("fatias A:B para caber no tempo de um comando"). As duas fatias juntas cobrem as 145 telas.
  - Quando uma mudança de desktop for decidida, troque `REF_DESKTOP` no mesmo commit, dizendo o motivo.
- **Correção de registro:** a mensagem de `9193ae2` diz que o mutante com overflow visible "faz a página rolar 2150 px". O medido foi outro: a caixa deixa de rolar (`caixa: false`, 2150 px de tabela em 1116 px de caixa) e a página não rola. A tabela acima está certa.
