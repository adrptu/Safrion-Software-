# NAV-1 · Planos agronômicos sem etapas falsas e o cultivo aberto no Planejar safra

- **Origem:** [`CONSOLIDADO.md`](CONSOLIDADO.md) §3.1 (N2-PA e X-AGR-6), pedido do proprietário de 09/10 ("veja se tem algum submenu redundante para enxugar e integrar, bem como telas e etapas de processo, assim como fizemos com planejar safra").
- **Pedido junto (repassado a esta frente em 09/10):** conferir se os botões de incluir em branco seguem o design system padronizado (lugar, prioridade e estilo), sem conflitar com os demais botões. Resposta na seção 3, contra os padrões BOT-01 a BOT-09 que o proprietário aprovou em 09/10 (`docs/design-system/README.md`, commit `cb74290` da main).
- **Autor / revisor / integrador:** Claude / Codex / Claude. **Base:** `cdc185f`, branch `claude/v44-nav`.
- **Arquivos:** `tools/prototipo/v37/gen37/areas/processo_planos.py`, `patest.py`, `pa_lista_test.py` (novo), `pa_regras_test.py` (novo); linhas da PA em `acao_unica_test.py` e `componentes_test.py` (seção 5).
- **Fora do escopo:** adoção de versão por cultivo no Planejar safra (PRD 40.3), já registrada como pendência da frente Planejar safra em `sp-solo/docs/analise-solo/ESPECIFICACAO.md:411`.

## 1. O que mudou na tela (executado)

**Antes (`cdc185f`):** três "etapas" (Escolha o plano · Edite as atividades · Publique a versão). A 2 e a 3 apareciam em vermelho como "impedida" antes de abrir um plano. O avanço "Revisar e publicar ›" só trocava de tela. A etapa 3 sem rascunho mostrava "Nada a publicar". O link do cultivo caía na etapa 1 do Planejar safra.

**Depois:** lista → detalhe, como o PM da PCM (D-03).
- **Lista:** a biblioteca por cultura, com o filtro por cultura e a posição guardada. "Criar plano" fica no cabeçalho e herda a cultura do filtro.
- **Detalhe (`PA.dc.html#plano=<id>`):** nome, estado e versão; a faixa do rascunho com "Descartar rascunho"; os blocos Atividades (dose e insumo na tabela), Cultivos que usam este plano e Versões (recolhido, com o resumo visível).
  - Com rascunho, o bloco "Alterações do rascunho vN em relação à vM" (diferenças, custo/ha e impacto nos cultivos) é o último antes do Próximo passo.
  - **Próximo passo:** "‹ Biblioteca de planos" e, só com rascunho, "Publicar versão vN".
- **Endereço:** lido ao carregar e no `hashchange`, gravado ao abrir. F5 reabre o mesmo plano; um id inexistente abre a lista com um aviso, sem erro.
- **Voltar** ("‹ Biblioteca de planos" ou Esc sem painel aberto) devolve a rolagem e o foco ao cartão aberto por último.
- **Publicar:**
  - não muda nenhum cultivo (PRD 40.3); o foco vai aos cultivos, onde está o próximo passo (a adoção);
  - fica desabilitado com o motivo, na nota e na dica (VIS-04), quando o rascunho não tem atividade;
  - também fica desabilitado enquanto uma inclusão de insumo está aberta. **Dano evitado:** publicar uma versão sem o insumo que está sendo digitado.
- **X-AGR-6:** cultivo de safra aberta numa versão anterior mostra "Na v6 · v7 publicada" e o link "Abrir cultivo no Planejar safra ›" → `SAF.dc.html#saf=<safra>&passo=cultivos&cult=<id>`, que abre a etapa 2 com o painel do cultivo. O texto de impacto continua dizendo que a adoção é por cultivo, no Planejar safra.
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
| NAV-D2 | Publicar a PA com um clique, com as diferenças visíveis logo acima do botão | Sem tela de confirmação: as alterações já estão à vista, e publicar não muda cultivos (decisão do autor, registrada no §3.1) |
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
- **Planejar safra:** adoção de versão por cultivo (PRD 40.3).
- **Integrador (`etapas_celular_test.py`, linha 142):** tirar a `'PA'` da lista do item 7 (e o rótulo passa a "5 telas"). Com essa troca feita só em memória, sem editar o arquivo, o teste deu 14 ok · 0 falhas (executado, §6).
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
- **`etapas_celular_test.py`:** não editado (fora desta frente). **Fica vermelho:** o item 7 (linha 142) mede a PA no zoom de 200 % como tela com etapas e quebra com `KeyError: 'sobrepoe'`, porque a PA não tem mais faixa. Os itens 1 a 6 já tiram a PA pelo `temEtapas` (linha 122). Correção para o integrador, depois da PCM e da SUP (§4).

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
