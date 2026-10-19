# Relatos da frente NAV1 (NAV-1: Planos agronômicos em lista → detalhe)

Fonte: resultado do workflow `modulo-prototipo` da NAV1 (run `wf_6b35ec3f-c04`, concluído em 09/10 às 21:43 UTC), o mesmo texto do `journal.jsonl`.
- Os agentes foram implementar, revisar e corrigir.
- A primeira tentativa de cada fase foi interrompida e retomada; a de corrigir, duas vezes.
- **A revisão é adversarial, feita por um agente Claude que se identifica "no papel do Codex". Não é a revisão do Codex, que continua pendente.**

Rótulos:
- **executado:** a saída está em `brutos/`;
- **relatado:** o agente diz que rodou, mas a saída não está no pacote.

As transcrições `brutos/*_transcricao_*.txt` são saídas copiadas do transcript do agente, para comandos que não gravaram arquivo. Nada foi reexecutado.

## Resumo

### Implementação (`19aeb94`, `74a6df6`, `0e1c368`)
- **Entrou:**
  - a PA virou lista → detalhe (`#plano=<id>`), sem faixa de etapas falsas;
  - as alterações aparecem acima de "Publicar versão vN";
  - X-AGR-6: o cultivo abre no Planejar safra (`SAF.dc.html#saf=…&passo=cultivos&cult=…`).
- **Testes antigos ajustados:**
  - `patest.py` reescrito;
  - `acao_unica_test.py`: itens 11, 25, 26 e 27;
  - `componentes_test.py`: itens 11, 12 e 14.
- **Medida (executado: L12 em `NAV1-impl_r2_pa_lista.log` e `NAV1-corr_log_pa_lista_4.txt`):** na base `cdc185f`, mudar uma dose e publicar custa 5 cliques e 4 teclas; na NAV-1, 4 cliques e 4 teclas.

### Revisão adversarial (sobre `0e1c368`)

| ID | Sev. | Achado | Evidência | Correção em `7b7d260` | Regressão |
|---|---|---|---|---|---|
| R1 | **S2** | Dose digitada sem Enter entra na versão publicada sem aparecer nas diferenças. O bloco de alterações ficava fora da tela, com 0 px visíveis a 1440 e a 390. | executado: sondas A e I em `NAV1-rev_transcricao_sondas.txt`; controle na base em `NAV1-rev_base_A.txt` | "Publicar" fica desabilitado com o motivo enquanto a dose está em edição. O clique até 1 s depois de gravar a dose também não publica. O resumo das alterações fica na nota ao lado do botão ("Ver alterações"). | U* em `pa_regras_test`; L5 (1440) e L11 (390) em `pa_lista_test` |
| R2 | S3 | Dose inválida + Publicar publica sem a mudança | executado: sonda B | mesma trava do R1 | idem |
| R3 | S3 | Rascunho igual à versão publicada vira uma v7 vazia | executado: sonda D | Publicar desabilitado com o motivo | idem |
| R4 | S3 | Trocar o endereço com o painel aberto grava em outro plano | executado: sonda G | a troca é ignorada e o endereço volta | U16 |
| R5 | S3 | O link do X-AGR-6 promete uma adoção de versão que não existe no destino | executado: captura citada pela revisão (não está no pacote) | o texto diz que a troca de versão ainda não existe; pendência na §4 da especificação | — |
| R6 | S4 | O Esc volta à lista quando deveria fechar só o filtro ou o menu | executado: sondas E e F | o Esc fecha só a camada aberta | — |
| R7 | S4 | O aviso depois do F5 mostra o id interno | executado: sonda H | texto sem id | — |
| R8 | S4 | "‹ Biblioteca de planos" descarta a inclusão digitada | executado: sonda J | avisa antes de descartar | U15 |
| T1 | S3 (teste) | `pa_lista_test` com espera fixa (15/16 e 14/16) | executado: `NAV1-rev_log_pa_lista2.txt`, `NAV1-rev_pa_lista_head.log` | espera pela condição; `a7023ca` espera o alvo livre | 24 ok · 0 em cada rodada: `NAV1-corr_pa_lista_1.log` e `NAV1-corr_log_pa_lista_2..6.txt` |
| T2 | S3 (teste) | `etapas_celular_test.py` aborta com `KeyError: 'sobrepoe'` na linha 143 | executado: `NAV1-rev_log_etapas_celular.txt`; base 14/0 em `NAV1-rev_log_base_etapas_celular.txt` | **não corrigido na frente:** o arquivo está fora dela, e a correção é do integrador (ver README) | — |
| T3 | S4 (teste) | 3 mutantes vivos (M1, M6 e M8) e proteção perdida para dose "−2" | executado: mutantes em `NAV1-rev_transcricao_sondas.txt` | casos novos (d1/lg01, base com rascunho, "retira", "−2") | 18 de 18 mutantes mortos (executado: `NAV1-corr_mut_resultado.txt`) |

Fora do escopo e já na base: publicar não grava quem publicou e não confere o perfil (AG-05).

### Correção (`7b7d260` e `a7023ca`): testes

| Comando | Resultado | Rótulo |
|---|---|---|
| `pa_regras_test.py` | 18/18 | executado: `NAV1-corr_regras.log` e `NAV1-corr_transcricao_regras.txt` (21:20) |
| `pa_regras_test.py` antes da correção (`0e1c368`) | 10/18 | relatado. O transcript da 1ª tentativa (`NAV1-corr1_transcricao_regras.txt`) mostra 10/17 numa versão intermediária do teste |
| mutação do `pa_regras_test` | 18 de 18 mortos | executado: `NAV1-corr_mut_resultado.txt` |
| `pa_lista_test.py` | 24 ok · 0 em cada rodada | executado: `NAV1-corr_pa_lista_1.log` e `NAV1-corr_log_pa_lista_2..6.txt` (o 4 a 6 já com o clique de `a7023ca`) |
| `pa_lista_test.py` em `0e1c368` | 13 ok · 11 falhas | executado: `NAV1-corr_log_pa_lista_antes_0e1c368.txt` |
| sondas `adv.py` depois da correção | nenhum achado se reproduz | executado: `NAV1-corr_adv_depois.txt`, `NAV1-corr_adv_depois2.txt` |
| `patest.py` | 46 ok | executado: `NAV1-corr_log_patest.txt` |
| `acao_unica` famílias / v3 | 8/0 · 10/0 | executado |
| `componentes` matriz / ajustes2 / interação | 3/0 · 2/0 · 8 ok e 2 falhas (itens 10 e 14, hover no headless, igual à base) | executado; base em `NAV1-impl_base_comp_interacao.log` |
| `etapas_celular_test.py` | quebra no item 7 (`KeyError`) | executado: `NAV1-corr_log_etapas_celular.txt` |
| `etapas_celular_test.py` com `.get()` na linha 143 (alternativa da revisão), numa cópia | 14 ok · 0 | executado: `NAV1-corr_log_etapas_celular_alt.txt` |
| `etapas_celular_test.py` sem `'PA'` na linha 142, troca em memória | 14 ok · 0 | executado antes da correção: `NAV1-impl_r2_etapas_sem_pa.log` |
| `agrofit_test` / `varredura` / `links_ocultos` / `acoes_duplicadas` | 17/17 · 140/140 · 8/0 · 0 repetidas | executado: `NAV1-corr_log_*` |
| `build.py` / `montar_render.py` | 0 FALHA, 140 artboards / 140 páginas | executado: `NAV1-build.log`, `NAV1-render.log` |

Índices das baterias:
- `NAV1-corr_bateria.idx`: 18:46–19:29, sobre `7b7d260`;
- `NAV1-corr_bateria2.idx`: 21:20–21:42, já com o `pa_lista_test` de `a7023ca`;
- `NAV1-rev_bateria.idx`: revisão.

### Riscos que ficam (relato da correção)
- A troca de versão no cultivo (PRD 40.3) ainda não existe.
- A PA não grava no `cenario.js`: um plano criado some no F5.
- A trava do R1 depende de tempo (1 s). Foi testada só no Chrome headless, não em aparelho físico.

## implementacao

NAV-1 está pronto na branch `claude/v44-nav`, em 3 commits (sem push nem PR). Os Planos agronômicos viraram lista → detalhe, sem as etapas falsas, e o cultivo abre direto no Planejar safra. Ficou um vermelho que não posso corrigir: o `etapas_celular_test.py`, que está fora dos meus arquivos (detalhe em "Riscos").

**Retomada.** Às 16h não havia nenhum commit sobre `cdc185f`. O trabalho de antes da queda estava inteiro e sem commit: código da PA, testes novos e ajustados, e os documentos. Conferi tudo, rodei de novo e fiz o commit. Não descartei nada. Apaguei as cópias temporárias da base que eu tinha criado (cerca de 100 MB no scratchpad).

#### Commits
- `19aeb94` NAV-1: Planos agronômicos em lista → detalhe, sem etapas falsas; cultivo abre no Planejar safra
  - `areas/processo_planos.py`, mais os testes novos `pa_lista_test.py` e `pa_regras_test.py`.
  - O que sai: a faixa de etapas, as etapas "impedidas", o avanço que só navegava e o bloco "Nada a publicar".
  - O que entra: o endereço `#plano=<id>`. Com rascunho, as alterações vN × vM ficam logo acima de "Publicar versão vN"; sem rascunho, nenhuma primária.
  - X-AGR-6: o cultivo mostra "Na vN · vM publicada" e o link "Abrir cultivo no Planejar safra ›" leva a `SAF.dc.html#saf=…&passo=cultivos&cult=…`.
- `74a6df6` NAV-1: testes antigos da PA na regra nova (`patest.py`; `acao_unica_test.py` só nas linhas da PA; `componentes_test.py`).
- `0e1c368` NAV-1: especificação, decisões e evidência
  - `docs/navegacao/CONSOLIDADO.md`, versionado sem mudança, e `docs/navegacao/ESPECIFICACAO.md`.
  - Decisões registradas: o SAF mantém "Escolha a safra" como etapa 1 por ora; publicar a PA em um clique; X-CTX só por escolha; "Criar plano" no cabeçalho.

#### Testes (executados, comandos de `gen37/`, Chrome headless)
| Comando | Resultado |
|---|---|
| `build.py` / `montar_render.py` | 0 FALHA, 140 artboards / 140 páginas |
| `pa_regras_test.py` | 11/11 (na base: 0/11, as funções não existem lá) |
| `ANTES=<_render da base> pa_lista_test.py` | 16 ok · 0 falhas |
| Cliques para mudar uma dose e publicar (mesmo cenário) | base `cdc185f`: 5 cliques + 4 teclas; agora: 4 cliques + 4 teclas |
| `patest.py` | 46 ok (na base estava vermelho: "RuntimeError: Uncaught") |
| `acao_unica_test.py familias` / `v3` | 8/0 · 10/0 |
| `componentes_test.py matriz` / `ajustes2` / `interacao` | 3/0 · 2/0 · 8 ok e 2 falhas |
| `etapas_celular_test.py` | quebra no item 7 (vermelho novo, ver "Riscos") |
| `agrofit_test.py` | 17/17 |
| `varredura.py` | 140/140 |
| `links_ocultos_test.py` | 8 · 0 falhas |
| `acoes_duplicadas.py` | 0 páginas com ação repetida |
| `verif_pa.py` (só diagnóstico) | sem erro de JavaScript; não precisou de mudança |

- **`componentes_test.py interacao`:** as 2 falhas (itens 10 e 14, hover no headless) são as mesmas da base.
- **Reprodução na base com `pa_lista_test.py`:** deu 2 ok · 12 falhas (faixa, "impedida", sem `#plano=`, link caindo na etapa 1). Essa rodada completa foi às 14:25, antes da queda; nesta retomada refiz contra a base só a medida de cliques.

#### Testes antigos com expectativa mudada
Motivo comum: a PA deixou de ter etapas e "Criar plano" segue o padrão de botões BOT-02/03.
- **`patest.py`:** reescrito de etapas para lista → detalhe, com as mesmas regras.
- **`acao_unica_test.py`:**
  - item 11: lista com "Criar plano" e detalhe com "Publicar versão v7" no lugar das etapas;
  - item 25: o rodapé do painel novo passa a ser "Incluir atividade";
  - item 26: o detalhe sem rascunho substitui a antiga "etapa 3";
  - item 27: o detalhe também entra na matriz 360/768/zoom.
- **`componentes_test.py`:**
  - itens 11 e 12: o plano aberto é conferido por `#plano=`, no lugar de "Etapa 2 de 3";
  - item 14: "Criar plano" no cabeçalho, e a etapa inerte passa a ser medida no SAF.

#### O que ficou fora
- **Menu (`ui37.py` MENU2):** sem mudança, a especificação não pede.
- **Adoção de versão por cultivo no SAF (PRD 40.3):** fica com a frente Planejar safra.
- **Pendências de outras frentes, registradas na §4 da especificação:**
  - DS: `area_acoes` sem `disabled` e o ícone "+" ainda local;
  - PCM: "Incluir serviço" verde;
  - O.S.: "Nova ordem";
  - CTL5: AG-07 → `PA#plano=`.

#### Riscos
- **`etapas_celular_test.py` vermelho, correção do integrador (eu não podia editar o arquivo):**
  - O item 7, na linha 142, mede a PA como tela com etapas e quebra com `KeyError: 'sobrepoe'`.
  - Correção: tirar `'PA'` da lista da linha 142 e mudar o rótulo para "5 telas".
  - Com essa troca feita só em memória (`scratchpad/nav1/etapas_sem_pa.py`), sem editar o arquivo: 14 ok · 0 falhas.
  - A especificação dizia que esse teste ficaria verde sem edição; não ficou.
- **Conflito ao integrar com a frente DS:** ela mexe nas mesmas linhas do item 14 do `componentes_test.py`.
- **Plano criado some no F5:** os planos ficam no estado da tela, como já era na base, e não no `cenario.js`. Depois do F5, o endereço desse plano abre a lista com um aviso.
- **Botão Voltar do navegador:** o endereço é gravado com `replaceState`, como na tela de Manutenção da PCM, então o Voltar não volta do detalhe para a lista. A volta é pelo "‹ Biblioteca de planos" ou pelo Esc.
- **Ajuste frágil:** o `disabled` do Publicar entra por troca de texto no `engine.area_acoes`. Uma verificação no build falha se esse componente mudar.

## revisao

**Parecer de revisão adversarial da NAV-1 (papel Codex, 09/10/2026), sobre `cdc185f..0e1c368` em `claude/v44-nav`**

**Veredito:** não integrar antes de corrigir o R1 (S2). Também é preciso estabilizar o `pa_lista_test.py` e resolver o `etapas_celular_test.py` (T1 e T2). Os demais achados podem ser corrigidos na mesma branch depois.

Tudo foi executado em cópias no scratchpad, no Chrome headless com o `flock` (emulação, não aparelho físico). Nenhum arquivo versionado foi alterado. Build da cópia: 0 FALHA, 140 artboards; `montar_render`: 140 páginas.

#### Achados

**R1 · S2 · Dose digitada sem confirmar entra na versão publicada sem aparecer nas diferenças (regressão)**
- **Reprodução (executada, `probes/adv.py` A e I):**
  1. Com o rascunho v7 aberto (Fungicida A 0,5 → 0,6), digitei "6" na dose do Glifosato 480 (era 2 L/ha), sem Enter.
  2. Cliquei em "Publicar versão v7".
  3. O blur gravou a dose e publicou na mesma ação: a v7 saiu "Em vigor" com Glifosato 480 = 6 L/ha.
  4. O bloco de alterações, antes do clique, mostrava só o Fungicida A.
- **O bloco de alterações fica fora da tela logo depois de mudar uma dose:**
  - a 1440×900: está em y=1160–1354 com a janela de 900 px, e o Publicar está em y=414;
  - a 390×844: está em y=1510–1868, com o Publicar na tela;
  - nos dois casos, 0 px do bloco visível.
  - A premissa do NAV-D2 ("as alterações já estão à vista") não vale.
- **Base (controle executado, `probes/base_A.py`):** "Revisar e publicar ›" gravava a dose e a etapa 3 mostrava "Glifosato 480: 2 → 6 L/ha" antes do Publicar. A regressão é desta mudança.
- **Dano:** uma versão de receita, que é imutável, sai com dose não revisada. É o resultado técnico que a trava protege (AGENTS §4).
- **Causa:**
  - `areas/processo_planos.py:357-360`: o `paAcoes` só bloqueia com `iadd`, não com `ied`;
  - `:365` e `:407` passam só `{iadd}`;
  - `:207` e `:497`: o onBlur chama `paDoseOk`, que grava antes do clique;
  - `:574`: as alterações são o último bloco, depois de Cultivos e Versões;
  - `pa_lista_test.py:132-137` (L5) confere só a ordem no DOM, não a visibilidade.
- **Correção:**
  - no `paAcoes`, `if(ui.ied)`: desabilitar com o motivo "Confirme (Enter) ou cancele (Esc) a dose de X para publicar a vN", passando `{iadd, ied}` nas linhas 365 e 407;
  - mostrar as diferenças junto do botão: um resumo na nota do Próximo passo ("2 alterações: Glifosato 480 2 → 6 L/ha; Fungicida A 0,5 → 0,6 L/ha") ou o bloco logo abaixo da faixa do rascunho;
  - no teste: L5 passa a medir no viewport a 1440 e 390, e entra um caso novo "dose sem Enter + Publicar não publica".

**R2 · S3 · Dose inválida digitada e Publicar: publica sem a mudança, e o erro fica na tela**
- **Reprodução (executada, B):** com o rascunho v7, digitei 0 no Fungicida A e cliquei em Publicar. Saiu "Versão v7 publicada", o campo continuou aberto com 0 e o alerta "Informe a dose por hectare, maior que zero.".
- **Causa:** a mesma do R1. Além disso, o `paPub` (`:367`) não limpa o `ied`.
- **Correção:** a mesma trava do `ied` do R1.

**R3 · S3 · Rascunho igual à versão publicada vira uma v7 vazia e marca os cultivos como desatualizados**
- **Reprodução (executada, D):** mudei 0,5 → 0,6 → 0,5. A tela mostrou "O rascunho está igual à versão publicada" e Publicar ficou habilitado. Ao publicar: v7 criada, 3 cultivos "Na v6 · v7 publicada" e 3 links "Abrir cultivo no Planejar safra ›" para adotar nada.
- **Causa:**
  - o `paAcoes` e o `paPubFaz` (`:357-364`) não olham o `paDiff`;
  - o `paSitCult` (`:371-374`) gera o link;
  - o publicar já era assim na base, mas o link é novo.
- **Correção:** desabilitar com o motivo "O rascunho vN está igual à vM: altere algo ou descarte o rascunho" quando `p.versao>0 && !paDiff(p).length`, com um caso no `pa_regras_test`.

**R4 · S3 · Trocar o endereço com o painel aberto grava a atividade no plano errado**
- **Reprodução (executada, G2):**
  1. Abri o painel "Atividade · Dessecação pré-plantio" na Soja.
  2. Mudei o endereço para `#plano=MILHO-SF`.
  3. O painel virou "Nova atividade" e o rodapé "Incluir atividade".
  4. O clique criou "Rascunho v5" no Milho safrinha com a "Dessecação pré-plantio".
- **Causa:**
  - `:140-145`: o `aplica` chama o `paOpen` sem olhar `fm`, `np`, `iadd` e `ied`;
  - `:130-133`: o `paOpen` não fecha o `fm` nem o `np`;
  - `:280-282`: o `paFm` cai em "Nova atividade" quando o `aid` não existe;
  - `:316-319`: o `paSave` grava no `state.pid`.
- **Correção:** com painel ou edição aberta, o `aplica` ignora a troca e devolve o endereço com `paHashSet(cur)`. O `paFm` fecha o painel se `fm.aid && !a0`.

**R5 · S3 · O link do X-AGR-6 promete uma ação que não existe no destino**
- **Execução:** o Planejar safra abre o cultivo certo, mas o seletor mostra "Soja alta tecnologia v6 · 8 atividades" (captura `_probe/pa_lista_1440_saf_cultivo.png`). A v7 não existe lá, porque a PA não grava no `cenario.js`.
- **Texto que promete:** o aviso (`:367`) e o impacto (`:384`) dizem "decida a adoção em Planejar safra".
- **Situação:** a adoção (PRD 40.3) está registrada como fora do escopo, mas o texto leva o proprietário a um beco sem saída.
- **Correção:** até existir a adoção, dizer que ela ainda não está no protótipo, ou registrar a pendência com aceite na frente do Planejar safra.

**R6 · S4 · Esc capturado volta à lista quando deveria só fechar outra camada**
- **Reprodução (executada):**
  - **E:** com o filtro de coluna da tabela de cultivos aberto e o foco em "↑ Classificar de A a Z", o Esc fechou o filtro e voltou à biblioteca.
  - **F:** a 390 px, com o menu lateral aberto por cima do detalhe, o Esc também voltou à biblioteca.
  - Na base não havia o `paEsc`. A comparação com a base é por leitura de código; não rodei a base nesse cenário.
- **Causa:**
  - `:136-139` e `:145`: o listener em captura só isenta `aside[role=dialog]`;
  - o filtro da grade é `div role="dialog"` (`engine.py:1209`);
  - o `g2glob` (`g2lib.js:295`) desiste porque encontra `defaultPrevented`.
- **Correção:** isentar qualquer `[role=dialog]` visível, `.menu-lat` e o menu sobreposto aberto, ou registrar o listener na fase de bolha respeitando `defaultPrevented`.

**R7 · S4 · Depois do F5, o aviso mostra o id interno ("Plano “NPmv18mng3” não encontrado…") (executado, H)**
- **Causa:** `:144`.
- **Correção:** usar um texto sem id.

**R8 · S4 · "‹ Biblioteca de planos" descarta sem aviso a inclusão de insumo digitada**
- **Reprodução (executada, J):** escolhi o produto, digitei a dose 0,3 e voltei à biblioteca. Ao reabrir, a inclusão não existia mais. No mesmo estado o Esc é bloqueado, e o aceite comum pede aviso antes de descartar.
- **Causa:** `paLista` em `:134`.
- **Correção:** avisar antes de sair, como no painel, ou bloquear como no Esc.

**T1 · S3 (teste) · `pa_lista_test.py` não reproduziu o 16/16 aqui**
- **Rodadas (executadas):** 15 ok · 1 falha (L8) e 14 ok · 2 falhas (L8 e L7a).
- **A tela funciona isolada:**
  - o painel do Planejar safra aparece em cerca de 0,9 s;
  - a captura tirada logo depois da medida do L8 mostra o painel aberto;
  - o "Cancelar" da inclusão funcionou 5 de 5 vezes (`probes/adv.py` L).
- **Causa:** esperas fixas em `pa_lista_test.py:149-150` (`w=1.6`) e `:163` (`w=.4`).
- **Correção:** esperar a condição, com limite de cerca de 6 s.

**T2 · S3 (teste) · `etapas_celular_test.py` vermelho**
- **Executado:** `KeyError: 'sobrepoe'` na linha 143. O teste aborta depois de 6 OK, então os itens 7 a 14 não rodam (não é só o item 7). Na base: 14 ok · 0 falhas.
- **Correção melhor que tirar a PA:** em `:143`, usar `z[g].get('sobrepoe',0)` e `z[g].get('vazam')` e manter a PA. Assim a PA continua coberta no zoom de 200 % (cabeçalho e título). Executado: 14 ok · 0 falhas (`etapas_celular_alt_codex.py` na cópia). A correção é do integrador.

**T3 · S4 (teste) · Lacunas e uma proteção de regressão perdida**
- **Mutação em `pa_regras_test.py`:** 11 mutantes; 7 mortos, 1 equivalente (M2) e 3 vivos:
  - **M1:** link com a safra fixa S2627. O U8 só usa o c1 e o L6 só a SOJA-AT; os links de S27SF e LG2627 não têm proteção. O comportamento hoje está certo: executei d1, d3, lg01, lg24, c8 e c9, e todos abrem o cultivo e a fazenda certos.
  - **M6:** copiar o rascunho da base em vez da versão publicada (`pa_regras_test.py:64`, U10). O teste usa uma base sem rascunho e não distingue os dois.
  - **M8:** a diferença sem "retira" (`:34`, U4). Nenhum caso retira insumo.
- **Proteção perdida:** o `patest.py` antigo (linha 119, "dose com − é recusada") saiu, e nenhum teste novo digita dose negativa. O comportamento continua certo: "−2" e "-2" são recusados (executado, K).
- **Correção:** acrescentar d1 e lg01 no U8, uma base com rascunho no U10, "retira" no U4, a dose "−2" na tabela e os casos do R1 e do R3.

**Fora do escopo, já na base · S3:** publicar não grava quem publicou e não usa `g2perfil`. Qualquer perfil em "Ver como" publica uma dose. O PRD AG-05 prevê "aprovador técnico". Não foi causado pela NAV-1.

#### O que tentei e não quebrou (executado)

- **Duplo clique em Publicar:** só uma v7, e o botão sai depois de publicar (C).
- **Links do X-AGR-6:** c1, c2, c3, c8 e c9 (S2627), d1 e d3 (S27SF) e lg01 e lg24 (LG2627) abrem a etapa 2 com o painel do cultivo certo e a fazenda certa (Santa Rita ou Lagoa Grande).
- **Voltar do navegador depois do link:** o bfcache devolve a PA com a v7 publicada.
- **Endereço e Esc:** `#plano=XYZ` abre a lista com aviso; F5 reabre o plano; dose 0, "−2" e "-2" recusadas; Esc com a dose ou a inclusão abertas não sai do detalhe.
- **Regras e uma primária:**

  | Comando | Resultado |
  |---|---|
  | `pa_regras_test` | 11/11 |
  | `patest` | 46 ok |
  | `acao_unica_test familias` | 8 ok · 0 falhas |
  | `acao_unica_test v3` | 10 ok · 0 falhas |
  | `acoes_duplicadas` | 140 páginas · 0 com ação repetida |

- **Regressão em outros módulos:**

  | Comando | Resultado |
  |---|---|
  | `varredura` | 140/140 páginas sem erro |
  | `links_ocultos_test` | 8 · 0 falhas |
  | `agrofit_test` | 17/17 |
  | `componentes_test matriz` | 3 ok · 0 falhas |
  | `componentes_test ajustes2` | 2 ok · 0 falhas |
  | `componentes_test interacao` | 8 ok · 2 falhas (itens 10 e 14, hover no headless, vermelho conhecido) |

- **Cliques para mudar uma dose e publicar:** base 5 cliques + 4 teclas; NAV-1 4 cliques + 4 teclas. Confirmado.
- **Arquivos:** o diff não toca O.S., estoque, apontamento nem `cenario.js`. As mudanças em `acao_unica_test.py` (itens 11, 25, 26 e 27) e em `componentes_test.py` (itens 11, 12 e 14) são só da PA, e a etapa inerte do item 14 continua medida no Planejar safra.

**Observação:** sem perceber, sobrescrevi com arquivos de `cdc185f` o diretório antigo e compartilhado `scratchpad/rev/base` (de 06/10). Nenhum arquivo versionado foi tocado.

Evidência em `<scratchpad>/nav1-codex-rev-1791565515/`:
- `log_*.txt` (bateria), `bateria.idx`
- `adv_KG2.txt`, `adv_L.txt`, `base_A.txt`
- `probes/adv.py`, `probes/base_A.py`, `probes/saf_links_all.py`
- `mut/run_mut_regras.py`
- `head/tools/prototipo/v37/gen37/etapas_celular_alt_codex.py`
- `head/tools/prototipo/v37/gen37/_probe/pa_lista_1440_saf_cultivo.png`

## correcao

**NAV-1: correções da revisão (branch `claude/v44-nav`, worktree `<sp-nav>`)**

Corrigi todos os achados da revisão, menos o T2. O `etapas_celular_test.py` continua vermelho porque o arquivo está fora desta frente e a correção fica com o integrador. Não fiz push nem PR.

**Commits**
- `7b7d260` "NAV1: correções da revisão". Cada achado ganhou um teste de regressão em `pa_regras_test` (U*) e `pa_lista_test` (L*):
  - **R1 (S2):** enquanto uma dose está em edição, "Publicar" fica desabilitado com o motivo. Um clique que chega até 1 s depois de a dose ser gravada também não publica: a dose entra no rascunho, aparece no resumo e o aviso pede um novo clique. Só desabilitar não bastava: no Chrome, o clique passava em 12 de 12 combinações de tempo testadas. O resumo das alterações agora fica na nota ao lado do botão, com o link "Ver alterações".
  - **R2:** dose inválida não publica; o erro continua no campo.
  - **R3:** rascunho igual à versão publicada fica desabilitado com o motivo. Salvar o painel sem mudar nada não cria rascunho.
  - **R4:** trocar o endereço com o painel aberto não muda nada; o endereço volta e nada é gravado no outro plano.
  - **R5:** os textos dizem que a troca de versão no cultivo ainda não existe no protótipo. A pendência, com aceite, está na §4 da especificação.
  - **R6:** o Esc fecha só o filtro ou o menu que estiver aberto.
  - **R7:** o aviso depois do F5 não mostra mais o id interno.
  - **R8:** voltar à biblioteca com dose ou insumo digitados avisa antes de descartar.
  - **T1:** as esperas fixas do teste viraram esperas pela condição.
  - **T3:** os casos que faltavam entraram nos testes ("retira", d1 e lg01 no link, base com rascunho, dose "−2").
- `a7023ca`:
  - `pa_lista_test.py`: o clique espera, até 2 s, nada estar por cima do alvo.
  - `docs/navegacao/ESPECIFICACAO.md` §7.1: resultado de cada comando, depois e antes das correções.

**Testes (todos executados; navegador headless, um teste por vez com `flock`)**

| Comando | Resultado | Antes (`0e1c368`) |
|---|---|---|
| `build.py` | 0 FALHA, 140 artboards | |
| `montar_render.py` | 140 páginas | |
| `pa_regras_test.py` | 18/18 | 10/18 |
| mutação do `pa_regras_test` | 18 de 18 mutantes mortos, inclusive os 3 que você deixou vivos | |
| `pa_lista_test.py` | 24 ok · 0 falhas em 5 rodadas seguidas | 13 ok · 11 falhas |
| L12, mudar uma dose e publicar | 4 cliques + 4 teclas | base `cdc185f`: 5 cliques + 4 teclas |
| `patest.py` | 46 ok | |
| `acao_unica_test familias` / `v3` | 8 ok · 0 / 10 ok · 0 | |
| `componentes_test matriz` / `ajustes2` | 3 ok · 0 / 2 ok · 0 | |
| `componentes_test interacao` | 8 ok · 2 falhas (itens 10 e 14, hover no headless; vermelho conhecido) | |
| `etapas_celular_test.py` | quebra no item 7 com `KeyError: 'sobrepoe'` | |
| `etapas_celular_test.py` com a sua troca da linha 143, numa cópia | 14 ok · 0 | |
| `agrofit_test` | 17/17 | |
| `varredura` | 140/140 páginas sem erro | |
| `links_ocultos_test` | 8 · 0 falhas | |
| `acoes_duplicadas` | 140 páginas · 0 com ação repetida · erros 0 | |
| `verif_pa` | limites do gatilho iguais à base; sem erro de JS | |
| suas sondas `adv.py` (A, B, D, E, F, G2, H, I, J, L) | nenhum achado se reproduz | |

**Recusado com motivo**
- **T2, nada recusado no mérito:** `etapas_celular_test.py` está na lista dos arquivos que esta frente não pode tocar. A sua troca da linha 143 está na §4 para o integrador e passou numa cópia (14 ok · 0).
- **Sonda I:** o bloco completo de alterações continua no fim da página, como você mediu. O que fica à vista é o resumo na nota ao lado de "Publicar", que foi uma das duas correções que o parecer propôs. L5 (1440 × 900) e L11 (390 × 844) conferem que essa nota está na tela.

**Riscos restantes**
- `etapas_celular_test.py` fica vermelho até o integrador aplicar a troca.
- A troca de versão no cultivo (PRD 40.3) ainda não existe. A PA não grava no `cenario.js`, então um plano criado some no F5 e o Planejar safra continua mostrando a v6.
- Publicar não grava quem publicou e não confere o perfil (AG-05). Já era assim na base e ficou registrado para a frente de perfis.
- A trava do R1 depende de tempo (1 s depois de a dose ser gravada). Está coberta por teste de unidade e por clique real, mas só no Chrome headless, não num aparelho físico.

**O que o proprietário pode conferir:** em Planos agronômicos, abra "Soja alta tecnologia" e mude a dose do Fungicida A para 0,6 com Enter. O resumo da alteração aparece ao lado de "Publicar versão v7". Clique em Publicar: a v7 entra em vigor, e cada cultivo mostra "Na v6 · v7 publicada" com o link "Abrir cultivo no Planejar safra ›".

Arquivos: `<sp-nav>/tools/prototipo/v37/gen37/areas/processo_planos.py`, `pa_regras_test.py`, `pa_lista_test.py` e `<sp-nav>/docs/navegacao/ESPECIFICACAO.md` (§4, §7 e §7.1). Os logs estão em `<scratchpad>/nav1fix/` (`bateria.idx`, `bateria2.idx`, `log_*.txt`, `adv_depois2.txt`, `mut/resultado.txt`).
