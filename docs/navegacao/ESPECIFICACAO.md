# NAV-1 · Planos agronômicos sem etapas falsas e o cultivo aberto no Planejar safra

- **Origem:** [`CONSOLIDADO.md`](CONSOLIDADO.md) §3.1 (N2-PA e X-AGR-6), pedido do proprietário de 09/10 ("veja se tem algum submenu redundante para enxugar e integrar, bem como telas e etapas de processo, assim como fizemos com planejar safra").
- **Pedido junto (repassado a esta frente em 09/10):** conferir se os botões de incluir em branco seguem o design system padronizado (lugar, prioridade e estilo), sem conflitar com os demais botões. Resposta na seção 3, contra os padrões BOT-01 a BOT-09 que o proprietário aprovou em 09/10 (`docs/design-system/README.md`, commit `cb74290` da main).
- **Autor / revisor / integrador:** Claude / Codex / Claude. **Base:** `cdc185f`, branch `claude/v44-nav`.
- **Arquivos:** `tools/prototipo/v37/gen37/areas/processo_planos.py`, `patest.py`, `pa_lista_test.py` (novo), `pa_regras_test.py` (novo); linhas da PA em `acao_unica_test.py` e `componentes_test.py` (seção 5).
- **Revisão:** parecer adversarial do Codex de 09/10 sobre `cdc185f..0e1c368`; as correções estão na seção 7.
- **Fora do escopo:** adoção de versão por cultivo no Planejar safra (PRD 40.3), já registrada como pendência da frente Planejar safra em `sp-solo/docs/analise-solo/ESPECIFICACAO.md:411`.

## 1. O que mudou na tela (executado)

**Antes (`cdc185f`):** três "etapas" (Escolha o plano · Edite as atividades · Publique a versão). A 2 e a 3 apareciam em vermelho como "impedida" antes de abrir um plano. O avanço "Revisar e publicar ›" só trocava de tela. A etapa 3 sem rascunho mostrava "Nada a publicar". O link do cultivo caía na etapa 1 do Planejar safra.

**Depois:** lista → detalhe, como o PM da PCM (D-03).
- **Lista:** a biblioteca por cultura, com o filtro por cultura e a posição guardada. "Criar plano" fica no cabeçalho e herda a cultura do filtro.
- **Detalhe (`PA.dc.html#plano=<id>`):** nome, estado e versão; a faixa do rascunho com "Descartar rascunho"; os blocos Atividades (dose e insumo na tabela), Cultivos que usam este plano e Versões (recolhido, com o resumo visível).
  - Com rascunho, o bloco "Alterações do rascunho vN em relação à vM" (diferenças, custo/ha e impacto nos cultivos) é o último antes do Próximo passo.
  - **Próximo passo:** "‹ Biblioteca de planos" e, só com rascunho, "Publicar versão vN". A nota ao lado do botão resume as alterações ("1 alteração na v7: Fungicida 1ª aplicação (Fungicida A: 0,5 → 0,6 L/ha).", até 2 itens e "e mais N") e leva ao bloco completo por "Ver alterações". A área é fixa no pé da tela, então o resumo fica à vista junto do botão a 1440 e a 390 px.
- **Endereço:** lido ao carregar e no `hashchange`, gravado ao abrir. F5 reabre o mesmo plano; um id inexistente abre a lista com um aviso, sem erro.
- **Voltar** ("‹ Biblioteca de planos" ou Esc sem painel aberto) devolve a rolagem e o foco ao cartão aberto por último.
  - Com a dose ou a inclusão de insumo digitadas e não concluídas, voltar ou trocar o endereço não sai: a nota avisa e oferece "Descartar e voltar à biblioteca" (ou "Descartar e abrir <plano>") e "Continuar editando".
  - Com o painel aberto, trocar o endereço não troca de plano: o endereço volta e o painel continua no plano em que foi aberto.
  - O Esc fecha só a camada de cima (painel, filtro de coluna, lista de busca, menu sobreposto); só sem nenhuma delas volta à lista.
- **Publicar** (a versão publicada é imutável; cada trava abaixo evita publicar algo diferente do que a pessoa vê):
  - não muda nenhum cultivo (PRD 40.3); o foco vai aos cultivos;
  - fica desabilitado com o motivo, na nota e na dica (VIS-04), quando o rascunho não tem atividade;
  - também enquanto uma inclusão de insumo está aberta. **Dano evitado:** publicar uma versão sem o insumo que está sendo digitado;
  - também enquanto uma dose está em edição ("Confirme (Enter) ou cancele (Esc) a dose de X…"). **Dano evitado:** publicar uma dose que não apareceu nas alterações. Se o clique começa com o botão desabilitado e a saída do campo grava a dose no meio dele, o clique não publica: a dose entra no rascunho e no resumo, e o aviso pede para conferir e clicar de novo;
  - também quando o rascunho voltou a ficar igual à versão publicada. **Dano evitado:** uma versão nova vazia, que marcaria os cultivos como desatualizados sem mudança nenhuma.
- **X-AGR-6:** cultivo de safra aberta numa versão anterior mostra "Na v6 · v7 publicada" e o link "Abrir cultivo no Planejar safra ›" → `SAF.dc.html#saf=<safra>&passo=cultivos&cult=<id>`, que abre a etapa 2 com o painel do cultivo. O texto de impacto diz que a troca de versão é por cultivo, no Planejar safra (PRD 40.3), e que no protótipo ela ainda não existe; o aviso de publicação diz que a versão publicada aqui ainda não chega ao Planejar safra.
- **Painéis:** abrem com o foco no 1º campo, e o Esc fecha. Antes, o foco ficava no botão atrás do véu e o Esc não fechava.

**Cliques medidos** no mesmo cenário (mudar a dose do Fungicida A de 0,5 para 0,6 L/ha e publicar), contados pelo `pa_lista_test.py` L12 na execução real:

| Build | Cliques | Teclas |
|---|---|---|
| `cdc185f` | 5 | 4 |
| NAV-1 | 4 | 4 |

O clique que sai é "Revisar e publicar ›". As 4 teclas são "0,6" e Enter.

## 2. Decisões (autor; o revisor confirma ou recusa)

| ID | Decisão | Por quê |
|---|---|---|
| NAV-D1 | O Planejar safra mantém "Escolha a safra" como etapa 1, por ora (X-AGR-3, não aplicar) | O proprietário citou o SAF como modelo. A pergunta segue para o Codex na rodada |
| NAV-D2 | Publicar a PA com um clique, com o resumo das diferenças na nota ao lado do botão | Sem tela de confirmação: o resumo fica à vista junto do botão (área fixa no pé da tela), o bloco completo está a um clique ("Ver alterações"), e publicar não muda cultivos. Ajustado na revisão (R1): antes, o bloco ficava fora da tela depois de mudar uma dose |
| NAV-D3 | X-CTX: a fazenda só acompanha quando a pessoa escolhe | Abrir uma tela não grava contexto (CONSOLIDADO §2.2) |
| NAV-D4 | "Criar plano" no cabeçalho, em vez de "Novo plano" no bloco, como primária só na lista | BOT-02 (tela do menu: no cabeçalho), BOT-03 (Criar, nunca "Novo") e BOT-05 ("+"). O §3.1 pedia "Novo plano como primária"; o design system de 09/10, aprovado pelo proprietário, é mais novo e prevalece |

## 3. Botões de criar e incluir (resposta ao pedido de 09/10)

Conferidos contra os padrões BOT-01 a BOT-09 do design system de 09/10 (`docs/design-system/README.md`, commit `cb74290` da main).

| Botão | Antes | Depois | Regra |
|---|---|---|---|
| Criar plano | "Novo plano" branco no cabeçalho do bloco | Verde, tamanho padrão, no cabeçalho à direita do título, com "+"; só na lista | BOT-01, 02, 03, 04, 05 |
| Incluir atividade (bloco) | Branco no cabeçalho do bloco | O mesmo lugar e estilo (branco, compacto), agora com "+" | BOT-04, 05, 06 |
| Incluir atividade (plano vazio) | Verde mini num bloco "Nenhuma atividade ainda" | Sai. O bloco Atividades mostra o vazio e mantém o mesmo botão no mesmo lugar; o Próximo passo diz o que falta | BOT-01 (bloco comum sem verde), BOT-02 (mesma ação, mesmo lugar) |
| Incluir insumo | "+ Incluir insumo" (o "+" em texto) | "Incluir insumo" mini com o mesmo "+" desenhado; nome acessível "Incluir insumo em <atividade>" | BOT-04 (mini na tabela), BOT-05 |
| Confirmação da linha de inclusão | "Incluir" verde mini dentro do bloco | "Incluir" branco mini; o Enter na dose também inclui | BOT-01 (um verde por contexto: o verde é o Publicar) |
| Rodapé dos painéis | "Salvar" em todos | Atividade nova: "Incluir atividade"; plano novo: "Criar plano"; edição: "Salvar" | BOT-02 (painel: verbo do efeito) |
| Publicar versão vN | Na etapa 3, depois de "Revisar e publicar ›" | No Próximo passo do detalhe; desabilitado com o motivo quando falta atividade ou há inclusão aberta | BOT-01, 02, 08, VIS-04 |

**Conflito:** cada contexto tem no máximo um verde (`pa_lista_test.py` L2, L3, L5, L7; `acao_unica_test.py` 11). Nenhum comando aparece duas vezes (`acoes_duplicadas.py`).

## 4. Pendências para outras frentes (não feitas aqui)

- **DS (botões, tarefa 48):**
  - `engine.area_acoes` não aceita `disabled`. A PA põe o atributo no próprio build, e o build falha se o componente mudar (BOT-09: levar ao componente).
  - O "+" de Criar/Incluir ainda não é ícone do `engine` (`MAIS` está local em `processo_planos.py`).
  - Os rodapés "Salvar" dos outros painéis de inclusão ainda não têm o verbo do efeito.
- **PCM (PM):** "Incluir serviço" verde com o plano vazio contraria BOT-01 depois desta mudança.
- **O.S.:** "Nova ordem" no bloco contraria BOT-02/03.
- **CTL5:** AG-07 "PL-xx ›" → `PA.dc.html#plano=<id>` (o endereço já existe).
- **Planejar safra (adoção, PRD 40.3; revisão R5):** a troca de versão por cultivo não existe no protótipo, e a PA não grava no `cenario.js` (o seletor do Planejar safra continua mostrando a v6). Aceite proposto para a frente dona: publicar a v7 da Soja alta tecnologia na PA; o link "Abrir cultivo no Planejar safra ›" do c1 abre o painel do cultivo com "Na v6 · v7 publicada" e um comando para adotar a v7, que grava a troca no cenário; de volta à PA, o c1 aparece "Na versão em vigor" e os demais continuam na v6. Depende de a PA gravar os planos no estado único (item abaixo).
- **Quem publica (AG-05, já na base, fora desta frente):** publicar não grava quem publicou nem confere o perfil (`g2perfil`); qualquer perfil do "Ver como" publica uma dose. O PRD prevê o aprovador técnico. Vai para a frente de perfis (CTL-3/CONF), com aceite: só o perfil agrônomo publica, e a versão guarda quem e quando.
- **Integrador (`etapas_celular_test.py`, linha 143):** a correção preferida (revisão T2) mantém a PA no zoom de 200 %, que continua conferindo cabeçalho, título e comando: no item 7, ler `z[g].get('sobrepoe',0)` e `z[g].get('vazam')` no lugar de `z[g]['sobrepoe']` e `z[g]['vazam']`, como no `etapas_celular_alt_codex.py` do revisor. Hoje o teste aborta no item 7 com `KeyError: 'sobrepoe'`, e os itens 7 a 14 não rodam. Esta frente não edita o arquivo (§3.1); a troca, rodada numa cópia contra o build corrigido, deu o resultado da §7.1.
- **Estado único:** a PA guarda os planos no estado da tela (como na base), não no `cenario.js`. Um plano criado some no F5; o endereço dele então abre a lista com aviso.

## 5. Testes antigos com expectativa mudada (motivo: a PA deixou de ter etapas)

- **`patest.py`:** reescrito de etapas para lista → detalhe, com as mesmas regras. Já estava vermelho na base: parava em "Recolher DAP 45", que não existe mais.
- **`acao_unica_test.py`, só nas linhas da PA:**
  - 11: lista com "Criar plano" verde no cabeçalho; detalhe sem primária; com rascunho, "Publicar versão v7".
  - 25: rodapé "Incluir atividade".
  - 26: o detalhe sem rascunho no lugar da "etapa 3".
  - 27: o detalhe também entra na matriz 360/768/zoom.
- **`componentes_test.py`:**
  - 11 e 12: "abriu o plano" passa a ser `#plano=`, no lugar de "Etapa 2 de 3".
  - 14: "Criar plano" no cabeçalho; a etapa inerte passa a ser medida no Planejar safra, porque a PA não tem mais faixa.
  - Atenção ao integrar: a frente DS mexe nas mesmas linhas do item 14.
- **`etapas_celular_test.py`:** não editado (fora desta frente). **Fica vermelho:** o item 7 (linha 143) mede a PA no zoom de 200 % como tela com etapas e quebra com `KeyError: 'sobrepoe'`, porque a PA não tem mais faixa; o teste aborta ali e os itens 7 a 14 não rodam. Os itens 1 a 6 já tiram a PA pelo `temEtapas` (linha 122). Correção para o integrador, depois da PCM e da SUP (§4).
- **`pa_regras_test.py` U5 (revisão R1):** com rascunho e alterações, a nota do Próximo passo deixa de ser vazia e passa a ter o resumo das alterações.

## 6. Evidência (executada em 09/10, 16:03–17:00 UTC)

Build do commit `19aeb94` (`build.py` → 0 FALHA, 140 artboards; `montar_render.py` → 140 páginas). Testes de navegador no Chrome headless, um por vez (`flock /tmp/cdpE.lock`), contra o `_render` desse build. Emulação, não aparelho físico.

| Comando (de `gen37/`) | Depois (NAV-1) | Base `cdc185f` |
|---|---|---|
| `python3 pa_regras_test.py` | 11/11 | 0/11 (as funções puras não existem) |
| `ANTES=<_render da base> python3 pa_lista_test.py` | 16 ok · 0 falhas | 2 ok · 12 falhas (faixa, "impedida", sem `#plano=`, link na etapa 1) |
| cliques para mudar uma dose e publicar (L12) | 4 cliques + 4 teclas | 5 cliques + 4 teclas |
| `python3 patest.py` | 46 ok | vermelho ("RuntimeError: Uncaught") |
| `python3 acao_unica_test.py familias` | 8 ok · 0 falhas | 8 ok (expectativa antiga) |
| `python3 acao_unica_test.py v3` | 10 ok · 0 falhas | 10 ok (expectativa antiga) |
| `python3 componentes_test.py matriz` | 3 ok · 0 falhas | 3 ok |
| `python3 componentes_test.py interacao` | 8 ok · 2 falhas (10 e 14, hover no headless) | as mesmas 2 falhas (vermelho conhecido) |
| `python3 componentes_test.py ajustes2` | 2 ok · 0 falhas | 2 ok |
| `python3 etapas_celular_test.py` | **quebra no item 7** (`KeyError`, §5); 14 ok · 0 falhas com a troca da linha 142 só em memória | 14 ok |
| `python3 agrofit_test.py` | 17/17 | 17/17 |
| `python3 varredura.py` | 140/140 páginas sem erro | — |
| `python3 links_ocultos_test.py` | 8 · 0 falhas (nenhum par novo) | 8 · 0 falhas |
| `python3 ../ferramentas/acoes_duplicadas.py . /tmp/NAV1-dup.json` | 140 páginas · 0 com ação repetida | — |
| `python3 verif_pa.py` (diagnóstico, sem asserção) | roda no detalhe sem mudança; limites do gatilho iguais; sem erro de JS | — |

## 7. Revisão adversarial do Codex (09/10) e correções

Parecer do Codex (papel revisor) sobre `cdc185f..0e1c368`: não integrar antes de corrigir o R1 (S2), estabilizar o `pa_lista_test.py` (T1) e resolver o `etapas_celular_test.py` (T2). Correções no commit "NAV1: correções da revisão". Cada achado tem proteção de regressão; os casos novos falham no `0e1c368` e passam depois (executado, §7.1).

| Achado | Sev. | O que mudou | Regressão |
|---|---|---|---|
| R1 · dose digitada sem Enter entrava na versão publicada sem aparecer nas diferenças | S2 | "Publicar" desabilitado com o motivo enquanto a dose está em edição. O desabilitar sozinho não basta: no Chrome, o blur da dose grava ao apertar o botão, o botão se habilita antes de soltar e o clique passa (executado: 12 de 12 combinações de tempo). Por isso o clique que começa com o botão desabilitado, ou que vem até 1 s depois de a saída do campo gravar uma dose, não publica: a dose entra no rascunho e no resumo, e o aviso pede para conferir e clicar de novo. O resumo das alterações fica na nota ao lado do botão (área fixa no pé da tela) | `pa_regras_test` U5, U13, U14; `pa_lista_test` L5 (nota na tela a 1440 × 900), L11 (390 × 844), L14a e L14b (clique de verdade) |
| R2 · dose inválida + Publicar publicava sem a mudança, com o erro na tela | S3 | A mesma trava: o campo continua aberto com o erro e o botão desabilitado | U14; L14c |
| R3 · rascunho igual à versão publicada virava uma versão vazia e marcava os cultivos | S3 | Desabilitado com "O rascunho vN está igual à vM: altere algo ou descarte o rascunho." (tela e regra pura); salvar o painel sem mudar nada não cria rascunho | U5, U7, U17; L15 |
| R4 · trocar o endereço com o painel aberto gravava no plano errado | S3 | Com o painel aberto, o endereço volta e nada muda ("Feche o painel antes de trocar de plano."); o painel guarda o plano em que foi aberto, e salvar em outro plano ou numa atividade que não existe fecha sem gravar | U16; L16 |
| R5 · o link prometia a adoção, que não existe no destino | S3 | Os textos dizem que a troca de versão é por cultivo no Planejar safra (PRD 40.3) e que no protótipo ela ainda não existe; a pendência tem aceite na §4 | L6 (textos), §4 |
| R6 · Esc com o filtro de coluna ou o menu sobreposto voltava à lista | S4 | O Esc da PA passa à fase de bolha e respeita quem já tratou o Esc; isenta qualquer `[role=dialog]`, lista, menu e o menu sobreposto | L17 |
| R7 · aviso com o id interno depois do F5 | S4 | "Plano do endereço não encontrado (no protótipo, um plano criado aqui não fica guardado ao recarregar): escolha um plano da biblioteca." | L18 |
| R8 · voltar descartava sem aviso a inclusão de insumo digitada | S4 | Voltar, ou trocar o endereço, com a dose ou a inclusão digitadas não sai: a nota avisa, com "Descartar e voltar à biblioteca" (ou "Descartar e abrir <plano>") e "Continuar editando" | U15; L19 |
| T1 · `pa_lista_test.py` instável (L7, L8) | S3 | Esperas pela condição (até 6 a 8 s) no lugar das esperas fixas, também nos casos novos; o clique espera (até 2 s) nada estar por cima do alvo, como uma lista de busca que ainda está fechando | 5 rodadas seguidas sem falha (§7.1) |
| T2 · `etapas_celular_test.py` vermelho | S3 | Arquivo fora desta frente (§3.1 do CONSOLIDADO): a correção do revisor está na §4 para o integrador e foi rodada numa cópia (§7.1) | — |
| T3 · lacunas dos testes | S4 | U4 com "retira"; U8b com d1 (S27SF) e lg01 (LG2627); U10 com a base em rascunho; U13 com 0, vazio, "−2" e "-2"; mutação: 18 de 18 mutantes mortos (§7.1) | — |
| Fora do escopo · quem publica (AG-05) | S3, já na base | Registrado na §4 para a frente de perfis | — |

### 7.1 Evidência das correções (executada em 09/10, 18:39–21:50 UTC)

Build do `7b7d260` (o código da PA não muda depois dele): `build.py` → 0 FALHA, 140 artboards; `montar_render.py` → 140 páginas. Navegador: Chrome headless, um teste por vez (`flock /tmp/cdpE.lock`), emulação, não aparelho físico. Logs em `scratchpad/nav1fix/` (`bateria.idx`, `bateria2.idx`, `log_*.txt`).

| Comando (de `gen37/`) | Depois das correções | No `0e1c368` (antes) |
|---|---|---|
| `python3 pa_regras_test.py` | 18/18 | 10/18 (os casos novos de R1, R2, R3, R4, R8 e o U5) |
| mutação do `pa_regras_test.py` (cópia, `mut/run.py` → `mut/resultado.txt`) | 18 de 18 mutantes mortos, inclusive os 3 vivos do revisor (safra fixa, cópia do rascunho, sem "retira") | 3 vivos de 11 (revisor) |
| `python3 pa_lista_test.py` | 24 ok · 0 falhas em 5 rodadas: 2 com o `7b7d260` e 3 com o clique que espera nada por cima (commit seguinte) | 13 ok · 11 falhas (L5, L6, L7a, L11, L14a, L14c, L15 a L19) |
| `ANTES=<_render de cdc185f> python3 pa_lista_test.py` (L12) | mudar uma dose e publicar: 4 cliques + 4 teclas; base 5 cliques + 4 teclas | — |
| `python3 patest.py` | 46 ok | — |
| `python3 acao_unica_test.py familias` / `v3` | 8 ok · 0 falhas / 10 ok · 0 falhas | — |
| `python3 componentes_test.py matriz` / `ajustes2` | 3 ok · 0 falhas / 2 ok · 0 falhas | — |
| `python3 componentes_test.py interacao` | 8 ok · 2 falhas (10 e 14, hover no headless; vermelho conhecido da base) | — |
| `python3 etapas_celular_test.py` | **vermelho**: `KeyError: 'sobrepoe'` no item 7 (arquivo fora desta frente, §4) | — |
| o mesmo com a troca do revisor na linha 143 (cópia em `etc_alt/`) | 14 ok · 0 falhas | — |
| `python3 agrofit_test.py` | 17/17 | — |
| `python3 varredura.py` | 140/140 páginas sem erro | — |
| `python3 links_ocultos_test.py` | 8 · 0 falhas | — |
| `python3 ../ferramentas/acoes_duplicadas.py . /tmp/NAV1-dup.json` | 140 páginas · 0 com ação repetida · erros 0 | — |
| `python3 verif_pa.py` (diagnóstico) | limites do gatilho iguais aos da §6; sem erro de JS | — |
| sondas do revisor (`probes/adv.py` A, B, D, E, F, G2, H, I, J, L) | A: o clique não publica, a dose do Glifosato entra no rascunho e no resumo ao lado do botão ("2 alterações na v7…"); B: não publica, erro no campo, botão desabilitado com o motivo; D: desabilitado ("O rascunho v7 está igual à v6…"), 0 links; E e F: o Esc fecha só o filtro ou o menu, o plano continua aberto; G2: o painel continua na Soja e "Salvar" sem mudança não grava ("Nada mudou…"); H: aviso sem id; J: não volta à biblioteca com a inclusão digitada; L: "Cancelar" fecha na 1ª vez, 5 de 5 | A, B, D, E, F, G2, H e J reproduziam os achados |

**Sonda I:** o bloco completo de alterações continua no fim da página (0 px visível a 1440 × 900 e a 390 × 844 logo depois de mudar a dose). O que fica à vista é o resumo na nota ao lado de "Publicar" (L5 a 1440 × 900 e L11 a 390 × 844 medem a nota dentro da tela), com "Ver alterações" para o bloco. Foi a opção do próprio parecer ("um resumo na nota do Próximo passo").
