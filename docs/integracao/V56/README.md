# V56 · candidata composta (executado)

Regime leve do protótipo (AGENTS.md 3.5), revisão por candidata composta (aceita pelo Codex em 6096838853). Sem push, sem PR, sem publicação.

- **Base:** `0c0931f` (a v55 publicada: `claude/prototipo-v44`), numa cópia local (`git worktree add --detach … 0c0931f`). Build 135 quadros, 0 FALHA; render 142 páginas.
- **Candidata:** branch local `int/v56`, código em `1f83eee` (o commit deste pacote só acrescenta `docs/`). Build 138 quadros, 0 FALHA; render 145 páginas; sintaxe JS das 145 páginas sem erro (`brutos/builds/`).
- **Ambiente:** Chrome headless com emulação, dados sintéticos (`SAFRION_DADOS=sintetico`), um teste de navegador por vez na trava `/tmp/cdpN.lock` (nenhum teste da bateria usa a porta 9333: todos abrem o Chrome numa porta livre).
- **Comando:** `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpN.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 <teste>`, de `tools/prototipo/v37/gen37`. Os testes sem navegador rodaram com `env SAFRION_DADOS=sintetico python3 <teste>`.

## 1. O que entrou (por frente)

| Frente | Origem | Junção | `git diff --shortstat <junção>^1 <junção>` | Correções de integração |
|---|---|---|---|---|
| DS (design system) | `943433c` | `d30f30b` | 19 arquivos, +1233 −48 | `93ca16c` (ds_unit conta só páginas com tela); `490301f` (DS × TABR) |
| TABR (tabelas de Cadastros e Irrigação) | `a2e9a9b` | `4afd477` | 34 arquivos, +1914 −331 | `ab25ec2` (c3cond com c3man); `1e847eb` (TABR × BEN); `8245911` (TABR × SOLO) |
| CTL5 (outorga, AG-07, Praga-alvo, ficha do pivô) | `f82ea6d` | `7cd0082` | 29 arquivos, +2130 −300 | `885a68c` (CTL5 × TABR e CTL5 × SOLO) |
| SOLO (análise de solo e recomendação) | `d324855` | `afc38fa` | 31 arquivos, +2962 −170 | — |
| NAV1 (Planos agronômicos em lista → detalhe) | `a7023ca` | `a676ac0` | 8 arquivos, +1013 −250 | — |
| COM (Comercial e logística) | `5efb2c4` | `e9670f0` | 24 arquivos, +2644 −125 | `0ad2d0d` (PV-031 do BEN no Comercial); `1f83eee` (COM × BEN) |
| v55 publicada (RESP-01, partest T1-C, COMP-02) | `0c0931f` | `2e466eb` | 131 arquivos, +14062 −27 (6 de código: +162 −27) | — |

Conflitos da junção `2e466eb`, resolvidos com as duas intenções:
- `engine.py`: `componentDidMount`/`g2mudou` do DS e a medida do aviso na troca (`g2avisoH`, RESP-01); o aviso com `aria-live="off"` do DS e `AVISO_PE` + `width: max-content` da RESP-01; `G2_GLOSS` do DS.
- `areas/processo_os.py`: o passo da liberação da COMP-02 (`osManCond` com `esp`/`passo`) seguido do selo "Plano mudou pela análise" do SOLO.

Recibo da publicação da v55 copiado em `docs/integracao/V55/publicacao.md` (commit `5d2119c`).

## 2. Testes · base `0c0931f` × candidata (executado)

"—" = o teste não existe na base (só roda na candidata). Brutos em `brutos/base-0c0931f/` e `brutos/cand-2e466eb/`; os testes refeitos depois das correções em `brutos/cand-1f83eee/`; comparação linha a linha em `brutos/comparacao.txt`.

### Gerais
| Teste | Base | Candidata |
|---|---|---|
| `varredura.py` | 142/142 páginas sem erro | 145/145 páginas sem erro (refeita em 1f83eee) |
| `acoes_duplicadas.py` | 142 páginas · 0 com ação repetida | 145 páginas · 0 com ação repetida |
| `links_ocultos_test.py` | 14 · 0 falhas | 14 · 0 falhas (L4: nenhum link visível para `BEN.dc.html`; `BEN_PUBLICADO=False`) |

### Aceite das frentes
| Frente | Teste | Base | Candidata |
|---|---|---|---|
| DS | `ds_unit_test.py` (inclui `node ds_unit.js`) | — | 44/44 + 29/29 |
| DS | `ds_test.py` (`DS_PARTES=A,B,C,D,E,G`) | — | 68/68 |
| DS | `componentes_test.py` matriz · rotacao · ajustes2 | 3/0 · 6/0 · 2/0 | 3/0 · 6/0 · 2/0 |
| DS | `componentes_test.py` interacao | 8 ok · 2 falhas (10, 14) | 8 ok · 2 falhas (10, 14): as mesmas |
| DS | `componentes_test.py` ajustes | 2 ok · 2 falhas (26, 27) | 2 ok · 2 falhas (26, 27): as mesmas (ver 3.2) |
| TABR | `tabelas_cad_irr_unit.py` | — | 49/49 |
| TABR | `tabelas_cad_test.py` | — | 178/178 (antes da correção: 176/178) |
| TABR | `tabelas_irr_test.py` | — | 106/106 (antes: parava no item da Pendência) |
| TABR | `irtest.py` · `irr_fluxo_test.py` · `irr_estado_test.py` · `map_irrig_filtro_test.py` | 26/26 · 33/0 · 38/0 · 15/0 | 26/26 · 33/0 · 38/0 · 15/0 |
| TABR | `cada_cd03_test.py` · `cada_fix03_test.py` · `cadc_cd06_test.py` · `cadc_fix_cd06.py` · `cadc_cd02_test.py` | 14/14 · 11/11 · 14/14 · 13/13 · 15/15 | 14/14 · 11/11 · 14/14 · 13/13 · 15/15 |
| CTL5 | `outorga_unit_test.py` · `usar_os_unit_test.py` · `ficha_pivo_unit_test.py` · `praga_alvo_unit_test.py` | — | 27/27 · 24/24 · 23/23 · 21/21 |
| CTL5 | `ctl5_test.py` | — | 30/30 (antes: 28/30) |
| CTL5 | `ficha_pivo_test.py` · `praga_alvo_test.py` | — | 21/21 (antes: 17/21) · 14/14 |
| CTL5 | `agrofit_test.py` | 16/17 (item 3) | 17/18 (item 3): a mesma falha |
| CTL5 | `carencia_test.py` | 91/91 | 91/91 |
| SOLO | `solo_unit_test.py` | — | 126/126 |
| SOLO | `solo_saf_test.py` · `solo_os_test.py` · `solo_ag02_test.py` · `solo_rev_test.py` | — | 36/36 · 18/18 · 32/32 · 22/22 |
| SOLO | `tabelas_os_test.py` · `tabelas_saf_test.py` · `map_aprov_test.py` · `map_decisoes_test.py` | 38/38 · 24/24 · 5/0 · 18/0 | 38/38 · 24/24 · 5/0 · 18/0 |
| NAV1 | `pa_regras_test.py` · `pa_lista_test.py` | — | 18/18 · 24/0 |
| NAV1 | `patest.py` | para no início (`Recolher DAP 45` não existe: o teste antigo da PA) | 46 ok |
| NAV1 | `acao_unica_test.py` familias · v3 | 8/0 · 10/0 | 8/0 · 10/0 |
| NAV1 | `etapas_celular_test.py` celular | 14/0 | 14/0 |
| COM | `comercial_unit_test.py` · `producao_unit_test.py` | — · 121/121 | 114/114 · 123/123 |
| COM | `comercial_revisao_test.py` · `comercial_fluxo_test.py` | — | 33/33 · 72/72 (antes: 71/72) |
| COM | `producao_fluxo_test.py` · `reserva_duplo_clique_test.py` | 66/66 · — | 67/67 · 2/2 |

### Cruzamentos
| Teste | Base | Candidata |
|---|---|---|
| `acao_unica_test.py` responsivo · saf | 5/0 · 10/0 | 5/0 · 10/0 |
| `partest.py` | 50/0 | 50/0 |
| `ma_regras_test.py` · `ma_app_test.py` · `ma_unica_test.py` | 150/150 · 36/36 · 23/23 | 150/150 · 36/36 · 23/23 |
| `dose_divergente_test.py` unit · nav | 35/35 + 2/2 · 21/21 | 35/35 + 2/2 · 21/21 |
| `cafe_apurar_test.py` unit · nav | 16/16 · 10/10 | 16/16 · 10/10 |
| `ben_unit_test.py` · `os_aprov_lib_test.py` · `tabelas_est_test.py` | 168/168 · 45/45 · 34/34 | 168/168 · 45/45 · 34/34 |
| `ostest.py` | 32 ok · 1 falha (OS-0440) | 32 ok · 1 falha: a mesma |
| `os_cenario_test.py` | 20/21 | 20/21: a mesma asserção |
| `osacoes.py` | 40 ok · 5 falhas | 40 ok · 5 falhas: as mesmas (diff vazio) |
| `etapas_celular_test.py` complemento | 7 ok · 2 falhas (17, 20) | 7 ok · 2 falhas: idênticas (diff vazio) |
| `etapas_celular_test.py` desktop | 0 ok · 1 falha (15: falta `gen37_antes/_render`) | a mesma (ambiente) |
| `etapas_celular_test.py` faixa | 0 ok · 1 falha (16: CMP, PA, SAF a 1400–1360 px) | 0 ok · 1 falha (16: CMP, SAF; a PA não tem mais faixa) |

**Reaproveitamento com prova.** A bateria da candidata rodou no código de `2e466eb`. Depois vieram só as correções da seção 3.1: `git diff --stat 2e466eb 1f83eee -- tools/` mostra 6 arquivos, `areas/cad_ativos_pessoas.py` (largura de duas colunas do CD-04) e 5 testes. Cada um desses testes foi refeito no build de `1f83eee`, junto com `cadc_cd02_test.py` e a `varredura.py` (`brutos/cand-1f83eee/`). Os demais resultados da candidata valem para `1f83eee` (os arquivos deles e o que eles geram não mudaram, salvo a largura de coluna do CD-04, que só a `tabelas_cad_test` mede). Nada da base foi reaproveitado de pacotes antigos: toda a coluna "Base" rodou nesta sessão.

## 3. Vermelhos

### 3.1 Vermelhos novos encontrados e corrigidos (com teste)
Todos já estavam vermelhos nas próprias junções (sonda: `ctl5_test` 28/30 e `tabelas_irr_test` parado em `7cd0082`, `brutos/sondas/juncao-7cd0082/`). Nenhuma correção afrouxa o controle; onde o teste mudou, ele passou a medir o estado composto.

| Commit | Frentes | Defeito | Correção | Teste |
|---|---|---|---|---|
| `1e847eb` | TABR × BEN | CD-04 › Pessoas rolava 37 px na caixa a 1440 px (A1 da TABR) com as pessoas e a equipe do Beneficiamento ("Beneficiamento e qualidade", "Autorizar rota e liberar ordem de processo"). Sonda: `a2e9a9b` 1142/1142 px; `4afd477` e `2e466eb` 1179/1142 px | Equipe 120 → 104 px e Habilidades 160 → 136 px (quebram linha antes): 1142/1142 px | `tabelas_cad_test` "CD (A1)" |
| `8245911` | TABR × SOLO | O teste esperava o Calcário dolomítico sem preço; o SOLO (D-10) deu a ele R$ 180,00/t | O item CD-06 confere o Calcário como está (t, granel, R$ 180,00/t, 15/09/2026, Em dia); o "—" com "Sem preço" segue no `cadc_cd02_test` (sementes das cultivares) | `tabelas_cad_test` 178/178; `cadc_cd02_test` 15/15 |
| `490301f` | DS × TABR | O chip passou a usar a dica do design system (`data-dica`), não o `title`: o teste morria em TypeError | O teste lê `data-dica`, confere o texto do leitor de tela e que não há `title` por cima | `tabelas_irr_test` 106/106 |
| `885a68c` | CTL5 × TABR | E3.1: a linha da CD-01 › Água tem o documento, a vazão e o vencimento em colunas; o número fica na faixa e no painel. E3.2c: o painel da captação guarda os valores nos campos | E3.1 confere as colunas, a Situação "Vence em 90 dias" e "Outorga SINT-002/0000 · 20/11/2026" na faixa; E3.2c lê o texto e os campos | `ctl5_test` 30/30 |
| `885a68c` | CTL5 × TABR | Itens 1, 10 e 16b: a capacidade do CD-03 só aparece com a Classe numa grandeza (A4, TABR-CTX-01) | O teste filtra Classe = Irrigação para ler 597,6 / 558 / 612 m³/h e limpa o filtro | `ficha_pivo_test` 21/21 |
| `885a68c` | CTL5 × SOLO | Item 12: com o SOLO o talhão P2 tem análise (AGS-003), e a ficha mostra a CAD medida, não "sem medição" | A ficha mostra a mesma CAD do campo "Água disponível no solo (referência)" do setor (uma fonte) | `ficha_pivo_test` 21/21 |
| `1f83eee` | COM × BEN | A recusa "Registrar venda sem cliente" contava 7 vendas; o cenário composto tem 8 (a PV-031 do packing) | Antes = depois = 8 (nada gravado) | `comercial_fluxo_test` 72/72 |

Nenhuma junção foi revertida.

### 3.2 Vermelhos da base (iguais nos dois lados)
| Teste | Asserção que falha | Observação |
|---|---|---|
| `componentes_test.py interacao` | 10 "PA · repouso branco com 'Abrir plano →' visível; hover muda fundo e borda…"; 14 "famílias · botão, menu, chip, busca (hover e foco)… respondem" | hover no Chrome headless; mesma asserção, medidas de posição diferentes |
| `componentes_test.py ajustes` | 26 "tabela no celular (SAF, CMP, CD-06, SU-01, MA) · … todo controle da 1ª linha e do cabeçalho fica inteiro à vista com o foco…"; 27 "menu · com 'aberto' guardado, CMP e O.S. começam recolhidos…" | **Atenção:** no 26, a candidata acrescenta o cabeçalho "Natureza de custo ⇅" do CD-06 (coluna nova da TABR) aos que não cabem inteiros a 360 px ao lado da coluna presa; na base só o SU-01 ("PEDIR ATÉ · NECESSÁRIA") tinha esse problema. É o mesmo defeito de classe (cabeçalho sem quebra × coluna limitada pelo g2lib), não corrigido aqui porque a correção é do g2lib, não da junção. Fica para a TABR (TABR-CTX-02) |
| `agrofit_test.py` | 3 "cabeçalho: 'Base atualizada · 02/10/2026'…" | depende do relógio: o arquivo é de 02/10/2026 e hoje passa de 7 dias, então a tela diz "Base de 02/10/2026 · desatualizada" |
| `ostest.py` | "painel da nova ordem A liberar: Liberar para execução e Ajustar antes de liberar, sem selo de agrônomo" (OS-0440) | trava de unidade (VERMELHOS.md da v55) |
| `os_cenario_test.py` | "A liberar sem revisão: Liberar para execução + Ajustar antes de liberar; área 0 recusada…; cenário v2 sem aprov" | o número medido muda de 6 para 7 (versão do cenário com o Comercial); a asserção é a mesma |
| `osacoes.py` | percentual da OS-0421; OS-0430 com dono Ana; lista sem rolagem horizontal; recusa não muda o saldo (OS-0420); saldo e dispensado da OS-0421 | linhas FALHOU idênticas (diff vazio) |
| `etapas_celular_test.py` complemento · desktop · faixa | 17 e 20 · 15 (falta `gen37_antes/_render`) · 16 | faixa: a candidata falha em CMP e SAF; a base também na PA, que deixou de ter faixa (NAV-1) |

**Vermelho novo restante: nenhum.** O sub-caso do CD-06 no item 26 está acima para o Codex decidir se o trata como novo.

## 4. O que o proprietário passa a ver (em português simples)
- **Design system:** linhas que separam o cabeçalho e os blocos, fundo verde ao passar o mouse, um realce rápido no que mudou ao trocar de tela ou de etapa, e dicas que abrem também pelo teclado e pelo toque; quando um botão está indisponível, o motivo aparece escrito ao lado.
- **Tabelas de Cadastros e Irrigação:** uma informação por coluna, a Situação logo depois do nome e filtro e ordem em todas as colunas; a capacidade das máquinas aparece quando se filtra a Classe.
- **Água, Agrofit e pivô:** a outorga vem só do cadastro de Água e trava pela data da janela; a Consulta Agrofit só consulta, com "Usar na O.S." numa pulverização A liberar; a Praga-alvo aparece por uso; a ficha do pivô fica no equipamento e abre pela Irrigação.
- **Análise de solo:** Análises de solo no menu Agrícola; a dose do plano mostra "Análise sugere"; a O.S. diz de onde veio a dose e avisa "Plano mudou pela análise".
- **Planos agronômicos:** lista que abre o detalhe, sem etapas que não existem, e "Abrir cultivo no Planejar safra ›".
- **Comercial:** menu Comercial com Contratos e pedidos, Expedição e entregas e Painel comercial. O packing (BEN) continua fora do menu.
- **Já publicado na v55 e mantido:** o aviso não cobre os botões em tela baixa; a cópia de ajuste entre parcelas; máquina liberada não tira a pendência de outra pessoa.
- **Da integração:** o cadastro de Pessoas volta a caber na tela de 1440 px.

## 5. Limitações
- Emulação no Chrome headless, não aparelho físico.
- `ds_test` parte F (capturas antes/depois) não rodou: não faz parte do aceite (A–E, G).
- `agrofit_test` item 3 e `etapas_celular_test desktop` dependem do relógio e de uma pasta de comparação que não existe nesta máquina: falham igual nos dois lados.
- As lentes de revisão e a publicação ficam fora desta etapa.
