# Configurações · especificação (CONF-01)

**Pedido do proprietário (Adrianus, 05/10/2026):** "adicione configurações e plataforma de assinaturas na ordem mais correta possível de prioridade". Diretriz permanente: essencialismo, uma ação primária por tela, planejamento, execução e controle separados, tudo no mesmo estado (`cenario.js`), sem redigitação.

```text
ID / resultado útil / persona: CONF-01 · "quem decide o quê" lido pelos próprios comandos e "quem fez o quê" lido dos registros · gestora (Ana) e proprietário
Requisitos do PRD e fora do escopo: CF-01..CF-04, 2.1, FO-39, FO-40, RF-GOV-001..004, RF-INT-001, CMD-06/09/24/42/46/47/50, ENG-017 · fora: §9
Autor / revisor / integrador: Claude / Codex / integrador da branch claude/prototipo-v44
Base / arquivos: 99537ca · gen37/{g2lib.js, cenario.js, configuracoes.js (novo), dados_config.py (novo), dados_cad.py, engine.py, ui37.py, build.py, areas/configuracoes.py, processo_os.py, processo_estoque.py, inicio.py, cad_ativos_pessoas.py, assinatura.py}
Aceite e comando: §8 · build 0 FALHA, montar_render, unidade e navegador (§7)
Estado / impedimento / próximo passo: implementado P1-P7 (§11, executado) · revisão do Codex pendente · integrador junta a branch claude/v44-config
```

**Rótulos.** Tudo é **especificado**, salvo o marcado **executado**. Decisões tomadas sem o proprietário: `DECISOES.md` (CONF-D01..D56). Revisor: Codex.

**Executado (06/10, leitura e sondas):** leitura de `areas/configuracoes.py` (inteiro), `g2lib.js:247-271`, `cenario.js` (inteiro), `processo_os.py:300-500, 620-630, 690-730`, linhas de papel de `processo_estoque.py`, `cad_ativos_pessoas.py:1-60, 280-403`, `dados_cad.py:60-90`, `ui37.py:30-80, 200-230`, `engine.py:1440-1458`, `assinatura.js:1-250`, `dados_assinatura.py:90-130`, `build.py`, `cftest.py`, `os_aprov_lib_unit.js:108-123`; PRD 2, 2.1, CF-01..CF-05, FO-39/40, RF-GOV-001..006, CMD-06/42/46/47/48; specs vizinhas `plataforma-assinaturas/`, `controle-01/PLANO.md` (CTL-7, PEND-*), `pcm-simplificado/` (Otávio, matriz §3.1), `suprimentos-simplificado/` (Ver como, Direção). `python3` sobre `cenario.seed()`: 6 O.S. em A liberar, 5 Em execução, `c.movs` vazio. `dados_cad`: 10 pessoas, 9 com login, só Ana com CREA (31/12/2027); Caio está em `G2_PERFIS` e **não** está no CD-04. `node` com `cenQtd`: 20 % de 350 / 100 / 75,11 / 73,18 / 71,11 ha = 70 / 20 / 15,02 / 14,64 / 14,22 ha; 15 % de 350 = 52,5 ha; 25 % = 87,5 ha.

**Abreviações:** `gen37/` = `tools/prototipo/v37/gen37/`; PRD = `/home/user/Safrion-Software-/docs/PRD.md` v3.9; CFG = `areas/configuracoes.py`; OSP = `areas/processo_os.py`; ESTP = `areas/processo_estoque.py`; CAP = `areas/cad_ativos_pessoas.py`.

## 0. Mapa: fica, muda, sai

| Peça | Onde | Decisão | Passo |
|---|---|---|---|
| CF-01 com 7 usuários digitados (e-mail, escopo, vigência, 2º fator, delegação, sessões e dispositivos) | CFG:84-157 | **sai**; CF-01 "Usuários e alçadas" lê o CD-04 e o estado | P4 |
| CF-02: alçadas em texto (AL-01 "Liberador do domínio · Caio (PCP)", teto R$ 80 mil :167), políticas IR-LIM, PE-04, TL-01 (:185-200), "Propor revisão" sem efeito nos comandos | CFG:159-230 | **sai**; bloco Alçadas no CF-01 lendo `G2_ALCADAS` | P4 |
| CF-02det (AL-05 v3 a 25 %, testes digitados) | CFG:232-287 | **sai**; ordens afetadas calculadas no painel da alçada | P4 |
| CF-03 (Sankhya, TOTVS, estação; fila NF 4412 e REQ-031 locais; offline APT-1187) | CFG:289-350 | **muda**: 5 conexões; fila do ERP = movimentos do cenário | P6 |
| CF-03det (de-para do ERP; conflito offline) | CFG:352-414 | **sai**: o conflito é o CMD-09 da O.S.; o de-para era dado local | P6 |
| CF-04: trilha digitada (:418-430), parâmetros (:431-436), documentação (:437-445) | CFG:416-458 | **muda**: trilha de `confTrilha`; parâmetros e documentação saem | P5 |
| Dados locais e ajudantes (APT, INV, REQ, `JS_BASE`, `prim_dyn`, `ic`, `nota`) | CFG:15-81 | saem os que ficarem sem uso | P6 |
| Menu | `ui37.py:42` | **muda**: 4 itens (§2); cada item entra no passo que entrega a tela | P4-P6 |
| Perfis: `G2_PERFIS` e funções | `g2lib.js:247-262`, `:266` (`perfil_opts`) | **fica** `G2_PERFIS` como padrão; **entram** `G2_PAPEIS`, `G2_ALCADAS`, `g2conf`, `g2perfis`, `g2alc`; `g2pf`, `g2perfil`, `g2quem`, `g2quemUm` e `g2navvals` usam o efetivo | P1 |
| `cenExige`, `cenExigeUm` | `cenario.js:68-69` | **muda**: papel sem titular ativo diz onde conceder | P2 |
| Papel literal nos comandos | OSP:317, 326, 362, 446, 452-457; `cenario.js:131, 148, 199, 322, 392-393` | **muda**: lido de `g2alc` | P2 |
| Papel literal nas telas | OSP:493-494, 626-627, 633, 718, 727-728, 843; ESTP:203-204, 377, 386, 493, 538, 568; `inicio.py:826` | **muda**: lido de `g2alc` | P2 |
| Pessoa literal como "quem decide" (`OS_AGRO`, `CEN_CONF_AP`, `CEN_CONC_RESP`) | OSP:253, 302, 305, 316, 490; `cenario.js:173-174, 195, 222` | **muda**: texto de `g2quem` da alçada (AL-02, AL-10, AL-12) ou do papel (almoxarife entrega e recebe devolução); sem titular, diz onde conceder; `resp` já gravado em `c.confs` fica | P2 |
| Dispensa guarda só a última (`osc_txt` sobrescreve `dispPor`) | OSP:453-460 | **muda**: + lista `o.osc.disps` (uma linha por CMD-47); `disp`, `dispPor`, `dispEm` ficam | P2 |
| Caso CC fechado pela decisão de duplicidade sem marca | `cenario.js:334, 347` | **muda**: grava `via: 'CMD-09'` (a trilha não o conta como CMD-50) | P2 |
| App de campo ignora o acesso do operador | `cenario.js:156, 179, 357, 411` | **muda**: `cenAppAtivo(c)` no início dos quatro comandos (R2) | P2 |
| Recusar ajuste sem autor | `cenario.js:151`; ESTP:296-298, 582 (`estRecontar` sem ator) | **muda**: grava quem recusou | P2 |
| Aprovar e liberar numa confirmação só; ajuste "Salvar e liberar" | OSP:313-335, 362-389, 476-494, 633-695; `inicio.py:817-831` | **muda**: R13 (por quem age) | P3 |
| Alçada de compras (`dados2.ALCADA`, lida pela CMP) | `dados2.py:705`; `processo_compras.py:19` | **fica** (fonte da CMP); o CF-01 a mostra só para leitura (AL-16) | P4 |
| Pessoas | `dados_cad.py:77-88`; CAP:35-38 (`_OVR`, `_ORDEM`) | **muda**: Caio entra (p11) | P1 |
| "Acesso ao app" editável no CD-04 | CAP:45, 297, 328-331, 366-375, 389-395 | **muda**: só leitura do estado + link para o CF-01 | P4 |
| Prefixo de toda tela | `engine.py:1449-1458` | **muda**: + `_conf_prefixo()`, uma vez, depois do da assinatura | P1 |
| Telas que deixam de ser geradas | `build.py:24` | + CF-02, CF-02det (P4), CF-03det (P6), de `project/` e `_render/` | P4, P6 |
| Alturas medidas | `heights_override.json:17-21` | saem CF-01..CF-03det | P4-P6 |
| Link "Propor regra ou alçada"; rodapé "segue CF-02" | `gestao.py:490`; `suprimentos.py:1113` | CF-02 → `CF-01.dc.html#alc=AL-01`; texto → "Configurações › Usuários e alçadas" | P4 |
| Testes antigos | P1: `cada_cd04_test.py:25-28` (10 → 11). P2: `os_aprov_lib_unit.js:107` (A7, `OS_LIB`), `ap_unico_unit.js:74, 82, 150, 185, 238` e `aprova_quem_decide_unit.js:21` (comparam com `CEN_CONF_AP`/`OS_AGRO`, que viram função; o texto do seed é o mesmo). P3: `os_aprov_lib_unit.js:108-123` (A8). P4: `cftest.py`, `cada_cd04_test.py:42-49`, `links_ocultos_test.py:34`. P7: `assinatura_test.py:174, 192` e `plataforma_test.py:83` (atos novos gravam "Ana (gestora)"; o seed segue "Ana · Gestora", registro do passado) | **mudam** com motivo no commit (§8); `os_aprov_lib_unit.js` N5 e `aprova_quem_decide_unit.js:221-225` **não** mudam | P1-P7 |
| CF-05: pessoas contadas na geração; quem paga é texto fixo | `assinatura.py:154, 161-206, 288-289` (`CF_PESSOAS`, `CF_POR`) | **muda**: contagem do estado; AL-15 conferida na tela do CF-05 dentro do `cenMudar`. `assinIni` (`assinatura.js:60`) **não muda**: o backoffice usa o mesmo comando com "Admin plataforma" | P7 |

## 1. Missão e princípios

A gestora responde numa tela **quem decide o quê** e, em outra, **quem fez o quê**, com a mesma fonte que os comandos usam.
1. Uma fonte por fato: pessoa = CD-04; papel = estado (`c.conf`) sobre o padrão `G2_PERFIS`; alçada = `G2_ALCADAS` (+ `c.conf`), e a de compras = `dados2.ALCADA`, a mesma que a CMP lê (AL-16, só leitura até a frente Suprimentos integrar); registro = o que o comando gravou. A trilha não tem texto digitado; nenhuma alçada aparece fora da tabela que o comando dela lê.
2. Mudança vale para o próximo comando, na hora, e nunca reescreve registro passado (RF-GOV-004).
3. Trava só onde protege algo concreto, com o dano nomeado (§4); o resto é aviso.
4. Simulado é rotulado: convite, sincronização e conexões não enviam nada real; no protótipo não existe credencial.
5. O perfil de demonstração ("Ver como", `g2perfil`) demonstra a experiência e não é segurança: no software real o servidor tira o ator da sessão.

## 2. Menu e telas: antes → depois

| Antes (6 telas ocultas + CF-05) | Depois: grupo Configurações, último do menu, 4 itens | Natureza |
|---|---|---|
| CF-01, CF-02, CF-02det | 1. **Usuários e alçadas** (`CF-01.dc.html`): blocos Pessoas e Alçadas | planejamento (define quem decide) |
| CF-04 | 2. **Auditoria** (`CF-04.dc.html`) | controle |
| CF-03, CF-03det | 3. **Integrações** (`CF-03.dc.html`) | execução simulada (sincronizar) e controle |
| CF-05 (PLAT-01) | 4. **Assinatura e cobrança** (sem mudança de tela; P7) | controle e execução (pagar) |

Perfil da casca: `Ana · Gestora`, trocável (Ver como). Nenhuma tela nova de detalhe: detalhe = painel da linha (master-detail), modal (`aside role=dialog`, `aria-modal`, véu): com ele aberto, conta só a primária do painel (padrão v3.1 do `acao_unica_test.py`).

## 3. Telas

### 3.1 CF-01 · Usuários e alçadas
**Pergunta:** quem entra, e quem decide cada comando?
**Primária (uma, pela ordem):** mudança de alçada pendente que o perfil pode confirmar → `Confirmar AL-xx` (abre o painel da alçada); alçada sem titular → `Resolver AL-xx` (abre o painel da alçada); senão `Convidar pessoa` (lista curta das pessoas do CD-04 sem acesso; um toque abre o painel da pessoa, onde está o único comando de convite). Perfil sem o papel da AL-13: a primária fica desabilitada com "decisão de Ana (gestora)". Ninguém sem acesso: desabilitada com "Todas as pessoas do cadastro têm acesso".
**Status:** "10 com acesso · 1 sem acesso" (cinza); "AL-xx aguarda confirmação" (amarelo); "AL-xx sem titular" (vermelho).
**Bloco Pessoas** (linha de origem: "Cadastrar, função e habilitação: Cadastros › Pessoas e equipes"). Colunas: Pessoa (nome · equipe, do CD-04) · Papéis (chips; "só app de campo" sem papel) · Decide (nº e nomes curtos das alçadas, pela R7) · Acesso ("Ativo desde 01/07/2026", "Sem acesso", "Desativado em 26/09/2026"). Filtro de texto; rápido Com acesso · Sem acesso · Desativadas; lista Papel (7). Ordenação por coluna (padrão: acesso, depois nome).
Linha → **painel Pessoa** (`#pessoa=Caio`): dados do CD-04 só leitura (habilidades; CREA quando houver) e "Abrir no cadastro"; 7 papéis liga/desliga, cada um com "decide: AL-…"; prévia "Ganha · Perde · Alçadas que ficam sem titular"; ação do painel `Salvar papéis` (com acesso) ou `Convidar (simulado)` (sem acesso); secundárias `Desativar acesso` ou `Reativar acesso` e `Ver como Caio` (só com papel e acesso ativo).
**Bloco Alçadas.** Colunas: Alçada (`AL-01 · Liberar O.S. agrícola · CMD-06`) · Quem decide (papel → pessoas: "gestor · Ana") · Valor / limite (unidade na célula: "até 20 % da área da ordem · acima: direção e agrônomo") · Situação ("Vigente v1 desde 01/07/2026", "Aguarda 2º aprovador", "Sem titular") · Mudança ("Editável: papel", "Fixa: lei"). Filtro de texto; rápido Editáveis · Pendências. Ordenação (padrão: AL).
Linha → **painel Alçada** (`#alc=AL-05`): definição, versões (dos eventos), **ordens afetadas agora**, calculadas pela mesma função do comando (AL-01: as O.S. em A liberar com link; AL-05: as O.S. Em execução com área, limite em ha com 2 casas e saldo; AL-09/AL-10: ajustes e consumos pendentes). Só nas editáveis: Papel (lista curta, um toque) ou Limite (% inteiro, teclado numérico, "%" junto) e Motivo (obrigatório); prévia (quem ganha e quem perde; "vale na hora" ou "aguarda 2º aprovador: amplia o seu poder"); primária `Salvar alçada` ou `Enviar para confirmação`. Pendente: primária `Confirmar mudança` (outra pessoa com gestor ou direção); `Desistir da mudança` é secundária (quem propôs). **Sem titular** (editável ou fixa): lista curta de quem está ativo e pode receber o papel (habilidade do CD-04 primeiro; agrônomo só com CREA válido), um toque escolhe, primária `Conceder <papel> a <pessoa>` (o mesmo comando do painel Pessoa). AL-16 só mostra os níveis e o link "Abrir Compra de insumos".
**Estados:** em dia; pessoa sem acesso; alçada aguardando 2º aprovador; alçada sem titular; perfil sem gestor (só leitura).
**Celular 390 px:** blocos empilhados; 1ª coluna presa e rolagem interna; chips quebram linha; painel em largura total; primária no cabeçalho.

### 3.2 CF-04 · Auditoria
**Pergunta:** quem fez o quê, quando e com que efeito?
**Primária:** `Baixar trilha (CSV)` com as linhas filtradas, no formato do `assinCsv` (`;`, aspas, BOM, CRLF); a exportação vira registro (RF-GOV-003). Filtro sem linhas: desabilitada com "Nenhum registro para baixar".
**Resumo (uma linha):** "14 registros · 3 autores · lidos dos comandos gravados; nada é digitado aqui".
**Grade:** Quando ("26/09/2026 10:42") · Quem ("Caio (PCP)") · O quê ("Liberar O.S. · CMD-06") · Objeto (link: "OS-0430 v1") · Antes → depois / efeito ("A liberar → Liberadas · requisição reservada no Estoque") · Origem (web, app, provedor simulado, plataforma). Filtros: Pessoa (lista), Comando (lista, §5), Mês (atalhos dos meses com registro + Todos), texto. Ordenação (padrão: Quando, mais recente primeiro).
Linha → **detalhe só leitura:** todos os campos, id do registro de origem (CMD, AJ-, CC-, CFG-, PAG-…), de onde vem a data ("data do registro", "data operacional da demonstração" ou "data simulada da cobrança"), `Abrir no domínio` e a frase "A trilha não se edita: corrija no domínio, por ajuste ou estorno vinculado".
**Estados:** com registros; filtro sem resultado ("Nenhum registro com estes filtros · Limpar filtros"); registro sem autor (chip cinza "autor não registrado").
**Celular 390 px:** Quando e Quem visíveis (Quem vai junto de Quando na 1ª coluna, a presa; CONF-D56); demais colunas na rolagem interna; filtros em uma linha que rola.

### 3.3 CF-03 · Integrações
**Pergunta:** o que entra e sai, de onde, e está em dia?
**Primária:** `Sincronizar agora (simulado)`. **Selo da tela:** "Demonstração · nenhuma conexão real".
**Grade (5 linhas):** Conexão · Traz / leva (escritor oficial) · Estado · Última sincronização · Pendências (nº com link) · Credencial. Filtro de texto e rápido Com pendência; ordenação.
Linha → **painel Conexão:** escritor por objeto; ambiente "Demonstração (dados sintéticos) · homologação e produção só com autorização do proprietário"; credencial "Não configurada · em produção fica no cofre do ambiente e só aparece mascarada (••••••••)"; últimas sincronizações (dos eventos); pendências com o lugar onde se resolvem (ERP: movimentos e estornos na fila, por id; App de campo: duplicidades → O.S.). O App de campo mostra o estado de `c.app` ("Com sinal (simulado)" ou "Sem sinal · n no aparelho"), nunca "online" ou "ao vivo" (PRD CF-03).
**Celular 390 px:** igual às outras telas.

## 4. Regras (testáveis; o dano que cada trava evita)

R1. Pessoa = CD-04 (`cad_ativos_pessoas.pessoas()`, mesma função do CD-04). O CF-01 não tem campo de nome nem cria pessoa. *Dano evitado: dois cadastros de pessoas que divergem.*
R2. Papel efetivo = `c.conf.pessoas[id].papeis` quando existe (id do CD-04; `k` = nome, a chave de `G2_PERFIS` e dos registros), senão `G2_PERFIS`; só conta com acesso Ativo. `g2papel`, `cenExige` e o Ver como leem o efetivo na hora; o Ver como lista só quem tem acesso Ativo e ao menos um papel, e o perfil guardado que deixou de valer cai no 1º perfil efetivo (não em `G2_PERFIS[0]`). Sem `c.conf`, o efetivo é exatamente `G2_PERFIS`. O app de campo também lê o acesso: com o operador (`c.app.operador`) desativado, iniciar e fechar turno, confirmar recebimento e registrar ocorrência recusam antes de qualquer outra conferência ("Acesso de Marcos desativado em Configurações"); o que já estava na fila do aparelho envia. *Dano evitado: decisão ou fato de campo gravado em nome de quem foi desligado.*
R3. Ninguém concede papel nem reativa acesso a si mesmo (PRD 2.1, RF-GOV-002). Retirar o próprio papel pode, desde que fique ao menos um (CONF-D49); desativar o próprio acesso, não (CONF-D34). *Dano evitado: autoconcessão de poder sem outro olhar; e, sem papel ou sem acesso, o Ver como passar em silêncio a outra pessoa e o ato seguinte sair em nome dela.*
R4. Papel agrônomo só com CREA válido no CD-04 na data operacional (26/09/2026), também ao reativar acesso (sem CREA válido, volta sem o papel e a prévia diz). *Dano evitado: aprovação agronômica e receituário por pessoa não habilitada (lei).*
R5. O último gestor ativo não perde o papel nem é desativado. *Dano evitado: organização sem ninguém que conceda papel (trancada).*
R6. Retirar papel ou desativar acesso que deixa alçada sem titular é permitido, com a prévia nomeando as alçadas; depois, a alçada mostra "Sem titular" e a primária vira `Resolver AL-xx`. Não é trava: quem foi desligado perde o acesso na hora (segurança da informação primeiro). O nível "acima do limite" da AL-05 não conta como sem titular.
R7. Comandos e telas com papel leem `g2alc(id)` (`cenExigeAlc(ator, id, ação, nível)` escolhe `cenExige` ou `cenExigeUm` pelo `modo` da linha; nível `base` ou `acima`). Textos de "quem decide" vêm de `g2quem` da alçada, nunca de nome fixo. Nenhum literal de papel ou pessoa nas linhas do §0. Para cada linha de `G2_ALCADAS`: perfil com os papéis passa e sem eles recusa, sem gravar nada. Formato da linha: `{id, t, cmd, papeis, modo: 'todos'|'um', lim?, un?, acima?: {papeis, modo}, edita: 'papel'|'lim'|'acima'|'', opc?, faixa?, porque_fixa?}`; versão e vigência vêm dos eventos CFG.

| AL | Comando | Quem decide (padrão) | Valor / limite | Mudança |
|---|---|---|---|---|
| AL-01 | Liberar O.S. agrícola (CMD-06) | gestor (PEND-OS-01) | — · fora desta alçada: água sem produto, que libera pela prontidão (DEC-2609-10) | editável: gestor · PCP · agrônomo |
| AL-02 | Aprovar a versão (CMD-42) e ajustar antes de liberar | agrônomo (R4) | — | fixa: lei e PRD 41 |
| AL-04 | Cancelar sem execução (CMD-46) | gestor | só sem realizado | fixa |
| AL-05 | Dispensar saldo (CMD-47) | gestor e agrônomo | até 20 % da área da ordem; acima, direção e agrônomo | editável: limite 1-100 % |
| AL-09 | Aprovar ajuste de inventário | gestor; quem contou e aprova fica com revisão posterior (PEND-CTL-02) | — | editável: gestor · direção |
| AL-10 | Aceitar consumo (CMD-50) | coberto pela custódia: almoxarife ou gestor; acima: gestor (PEND-CTL-02) | a custódia | editável (só o excedente): gestor · direção |
| AL-11 | Liberar lote da quarentena com laudo (CMD-24) | gestor | — | fixa |
| AL-12 | Decidir duplicidade de apontamento (CMD-09) | conferência | — | fixa |
| AL-13 | Conceder e retirar papel, convidar, desativar | gestor | R3, R4, R5 | fixa |
| AL-14 | Alterar alçada | gestor; confirmação: outro gestor ou direção (R10) | — | fixa |
| AL-15 | Pagar fatura, mudar plano, desfazer mudança, pedir proposta e contestar (CF-05) | gestor | — | fixa; entra em `G2_ALCADAS` no P7. O backoffice (conciliar, resolver) segue "Admin plataforma", fora da organização |
| AL-16 | Aprovar compra (Compra de insumos) | níveis de `dados2.ALCADA`: gestor de suprimentos até R$ 50.000,00 · gerente da fazenda até R$ 300.000,00 · acima, Direção | R$ por compra | só leitura (a CMP lê a mesma tabela); vira linha de `G2_ALCADAS` quando a frente Suprimentos integrar (§5) |
| AL-17 | Publicar previsão de colheita (Colheita R-17; CONF-D41) | agrônomo | — · a contagem do campo não muda a previsão | editável: agrônomo · gestor · PCP |

R8. Mudança de alçada exige motivo, cria a versão seguinte e vale para comandos novos; registros antigos guardam quem decidiu sob a versão de então. Uma mudança pendente por alçada: outra proposta antes de confirmar ou desistir recusa com o motivo.
R9. Alçada só aponta para papel que ao menos uma pessoa ativa tem. O nível `acima` da AL-05 (direção) não entra nesta regra nem na R6: sem titular, o que passa do limite é só recusado, como hoje. *Dano evitado: fluxo essencial (liberar, ajustar estoque) parado por configuração.*
R10. Mudança que amplia o poder de quem altera (depois dela, ele decide um comando ou uma faixa de valor que antes não decidia: ex. AL-01 de PCP para gestor alterada pela gestora; AL-05 de 20 para 25 % alterada por quem dispensa) fica "Aguarda 2º aprovador" até outra pessoa ativa com gestor ou direção confirmar; até lá vale a versão anterior; quem propôs pode desistir. *Dano evitado: elevar a própria alçada (RF-GOV-002).*
R11. Limite da dispensa em ha = `cenQtd(limite/100, área da ordem)` (decimal, regra única), comparado ao total já dispensado mais o pedido; acima, exige direção e agrônomo. A mesma função dá o texto do painel (OSP:727-728, ha com 2 casas). A mensagem de recusa mantém o texto de hoje com o limite vigente ("71 ha = 20,3 % acima de 20 % · exige Direção."), que `osacoes.py` e `aprova_quem_decide_unit.js` conferem. *Dano evitado: dispensa grande sem decisão superior.*
R12. Toda mudança do CF (papel, convite, acesso, alçada, confirmação, sincronização, exportação) passa por `cenMudar`, leva a chave de quem inicia (gerada ao abrir o painel ou a tela) e o perfil; sem um ou outro, recusa. A mesma chave com o mesmo conteúdo devolve o mesmo recibo `CFG-nnnn` sem novo efeito; com outro conteúdo, recusa como conflito (ENG-021, como `cenApontar`). Depois de gravar, o painel gera chave nova; o 2º clique de um duplo clique (ou antes de a tela redesenhar) repete o mesmo pedido com a mesma chave (CONF-D51). Os comandos de outras telas que a trilha lê e que movem quantidade (dispensa CMD-47, entrega, recebimento) também levam a chave de quem inicia (CONF-D50). *Dano evitado: segunda mudança descartada em silêncio, papel diferente do que a gestora vê.*
R13. O.S. agrícola: CMD-42 e CMD-06 são registros separados; quem age decide pelo que tem (perfil, R7):
- AL-02 e AL-01: uma confirmação grava os dois (PEND-OS-01, como hoje); se a versão já tem CMD-42, grava só o CMD-06.
- Só AL-02: primária `Aprovar vN` (`osc_aprovar`: regra legal e total > 0 da O.S. antes de gravar; grava só o CMD-42); a ordem fica em **A liberar** com o selo "Aprovada vN · aguarda liberação". Aprovar de novo a mesma versão recusa sem gravar. No ajuste, o botão é `Salvar e aprovar vN+1` (`osc_ajustar` sem liberar + `osc_aprovar`, no mesmo `cenMudar`).
- Só AL-01: libera só versão com CMD-42 e grava só o CMD-06; sem ele, recusa "Aprovação agronômica da vN pendente: decisão de Ana (agrônoma)", sem gravar.
- `Salvar ajuste` (sem aprovar) segue sem CMD-42 (N5 do `os_aprov_lib_unit.js`); a aprovação de uma versão nunca libera outra.
O Kanban segue com 5 fases. *Dano evitado: liberar versão que ninguém aprovou; registrar aprovação que ninguém deu; e, sem isto, nenhuma O.S. liberada quando os papéis se separam (S2, PLANO CTL-7).*
R14. Trilha = função única `confTrilha(c, A)` sobre as fontes da §5, só leitura, uma linha por ato. Data: a do registro; registro do cenário só com hora usa a data operacional (26/09/2026); a da assinatura é a data simulada da cobrança. Ordem: data, hora, ordem de gravação. Autor = o campo de quem agiu, até " → " (na entrega, o destinatário vai no efeito); filtro por pessoa pelo 1º nome (regra do `g2mesma`: "Ana · Gestora" e "Ana (gestora)" são Ana). Fatura paga sem `paga_por` e com `evt` aparece "Provedor (simulado)", lido do evento. Registro sem autor aparece "autor não registrado"; nunca se infere autor: o comando grava o perfil de quem age, nunca quem deveria agir (CONF-D45). Cada linha tem identidade estável (`uid` = id do registro de origem; CONF-D48): o detalhe aberto não troca de registro quando outra aba grava. O "Registro de origem" é único por linha ("nº k" na ordem da fonte quando a fonte se repete; CONF-D55).
R15. `Baixar trilha (CSV)` gera o arquivo no navegador com as linhas filtradas e grava o evento "Exportação · n registros · filtros".
R16. Nenhuma credencial existe no protótipo; nenhuma tela, CSV, aviso ou registro mostra segredo (ENG-017); o selo "Demonstração" nunca some (integração simulada não aparece como online).
R17. Fila do ERP = movimentos de `c.movs` já no servidor (`sinc !== false`) com tipo `recebimento-nf`, `entrega`, `devolucao`, `ajuste` ou `consumo` com `det` não vazio, cuja impressão (tipo, produto, lote, qtd, det) difere da última enviada (`c.conf.erp[id]`); nunca `reserva`, `contagem`, `inspecao` nem `recebimento` (confirmação no app, sem quantidade). `Sincronizar agora (simulado)` grava a impressão de cada um e a data operacional como última sincronização das 4 conexões de demonstração. Repetir não reenvia. Movimento enviado e depois estornado (`det` esvaziado pela decisão de duplicidade "vale este") volta à fila uma vez, como estorno. O app de campo não sincroniza pela web. *Dano evitado: saldo do ERP diferente do sistema depois de um estorno.*
R18. Nada no CF-01, CF-03 e CF-04 é restringido por inadimplência (PLAT R13); a faixa de cobrança aparece (PLAT R11).

Unidades: `%` e `ha` na célula; produtividade por cultura (DEC-0510-03) não se aplica. Kanban de 5 fases e aprovação agronômica individual: preservados (R13).

## 5. Integração com o estado único e os outros módulos

| Lê | De onde | Para |
|---|---|---|
| Pessoas, equipe, habilidades, CREA, login inicial | `cad_ativos_pessoas.pessoas()` na geração → `CONF0.pessoas` (o CD-04 não grava no navegador) | CF-01, R4 |
| Papéis padrão e alçadas padrão | `G2_PERFIS`, `G2_ALCADAS` (bloco `<perfis>` do `g2lib.js`, lido também pelos testes sem navegador) | todos os comandos com papel |
| Acessos, papéis, alçadas, conexões, eventos CFG | `c.conf` no cenário (`talhao-os-cenario-v1`); ausente ou de outra versão → padrão | CF-01, CF-03, CF-04, Ver como, `cenExige` |
| Trilha, uma linha por ato: CMD-42/06 (`o.osc.ev`; a liberação só com água grava o CMD-06 com autor, CONF-D53); nova versão (`o.osc.aj`); CMD-46 (`o.osc.canPor`); CMD-47 (`o.osc.disps`, P2); CMD-09 (`o.ap[].dec`, sem os de `modo: 'estornado'`, que são efeito); CMD-50 (`c.confs` com `por` e sem `via`); ajuste de inventário aprovado ou recusado (`c.ajustes`: `por`; no efeito, quem contou (`contador`), quem registrou (`reg`, só se for outra pessoa) e a causa; CONF-D47); enviar para conferência e encerrar a O.S. (CMD-08 e CMD-10 em `o.osc.fim`, CONF-D46); `c.movs` só dos tipos `recebimento-nf`, `entrega` sem `conf`, `recebimento` (confirmação no app), `devolucao` e `inspecao` (o `ajuste` já vem de `c.ajustes`; `reserva`, `contagem` e `consumo` ficam fora, D18); assinatura da organização `A.demo` (contratos, desfeitos, faturas pagas, contestação e resolução, proposta em `c.assin`); eventos CFG; colheita (`c.producao`, CONF-D40): previsão publicada, pesagem, estorno, descarte, liberação de lote, reserva e cancelamento de produto e expedição, sem o que veio do seed; beneficiamento (CONF-D43): histórico de cada ordem (`o.ben.hist`) e decisões da Qualidade sobre o lote de produção (resultado, liberação, reclassificação, bloqueio, destinação), sem o que veio do seed | cenário | CF-04 |
| Fila do ERP; app de campo (`c.app.fila`, duplicidades) | `c.movs`, `c.app`, `c.ordens` | CF-03 |

Leitura em toda tela: `g2conf()` usa `cenGet()` onde há `cenario.js`; sem ele, lê a mesma chave e aceita só `c.v === ASSIN_CENV` e `c.conf.v === CONF0.v` (regra do `assinLer`; sem `CONF0` na página, vale o padrão). Nos dois caminhos, cache pelo texto salvo e pelo tamanho de `G2_PERFIS` (os testes injetam perfis): `g2pf` roda muitas vezes por desenho e não pode analisar o cenário a cada chamada. `CONF0.v` = versão + resumo do seed **e** do bloco `<perfis>`, para que outra frente que mude `G2_PERFIS` invalide o `c.conf` salvo. Nunca é chamado no carregamento do script (`ASSIN_CENV` e `CONF0` são `const` declarados depois do `g2lib.js`). `configuracoes.js` entra em toda tela e só declara nomes `conf*`/`CONF*` no topo (regra RV-01 da PLAT: um nome repetido derruba a página inteira). Os comandos do CF calculam R3, R5, R9 e R10 sobre o `c` da transação, não sobre `g2conf()`. Grava só por `configuracoes.js` dentro de `cenMudar` (CF-01, CF-03, CF-04 carregam `cenario.js_prefixo()`): `confPapeis`, `confConvidar`, `confAcesso`, `confAlcMudar`, `confAlcConfirmar`, `confAlcDesistir`, `confSincronizar`, `confExportar`. `cenReset()` volta tudo ao padrão. CD-04 e CF-05 só leem (`confAcessoDe(k)`, `confComAcesso()`).
**Outras frentes (uma solução por problema):** a matriz papel × comando da manutenção (`pcm-simplificado` §3.1) e a alçada de compras (`suprimentos-simplificado`: Ana até R$ 300.000, acima Direção) entram como linhas de `G2_ALCADAS`, no mesmo formato, quando a frente for integrada; até lá o CF-01 mostra a de compras lendo `dados2.ALCADA` (AL-16, a tabela da CMP, sem cópia). Otávio e a pessoa da Direção entram pelo CD-04 e `G2_PERFIS` dessas frentes, e o CF-01 os mostra sem mudança.

## 6. Seed sintético (`dados_config.py` + bloco `<perfis>`; números fecham)

Pessoas: **11** (10 do CD-04 + Caio: `p11`, função PCP, equipe Agronomia, CLT, admissão 04/03/2024, custo R$ 52/h, habilidade Conferir, com login; todos os campos que `pessoas()` lê, sem eles o build falha). Com acesso **10**; sem acesso **1** (Beto, admitido 22/09). Papéis (= `G2_PERFIS`): Ana gestor + agrônomo, Caio PCP, Rui almoxarife, Paula almoxarife + conferência, Zé mecânico = **7** atribuições em **5** pessoas; só app de campo: Marcos, Carlos, Nilton, Lucas, João (**5**); direção: **0**. CREA válido: Ana (31/12/2027).
Alçadas: **12** no bloco (11 em `G2_ALCADAS` + AL-16 só leitura; até o P7, 10 + AL-16); editáveis **4** (AL-01 papel, AL-05 limite, AL-09 papel, AL-10 excedente); pendentes 0; sem titular 0.
Eventos CFG da implantação: acesso de Ana por "Plataforma (implantação)" em 28/06/2026 (dia do aceite do contrato v1 da PLAT); Ana concede a Caio, Marcos, Carlos, Paula, Nilton, João, Rui e Zé em 01/07/2026 (início do contrato v1) e a Lucas em 01/08/2026 (admissão) = **10**.
Trilha no início: 10 acessos + contratos v1 (28/06) e v2 (28/08) por "Ana · Gestora" + faturas de jul e ago pagas pelo provedor (01/08, 01/09) = **14**; por mês: jun 2 · jul 8 · ago 3 · set 1; autores: Ana 11, Plataforma 1, Provedor (simulado) 2.
Conexões: ERP · Sankhya (26/09/2026 06:40; fila 0, porque `c.movs` começa vazio); Estação meteorológica · Santa Rita (26/09 06:00); Telemetria de máquinas (25/09 18:10); Laboratório de análises (18/09 14:00); App de campo (Com sinal (simulado); 0 no aparelho; 0 duplicidades).
**Roteiro de números** (cada item parte do seed, com `cenReset()`; "trilha +n" = linhas novas no CF-04):
- AL-01 → PCP por Ana: vale na hora (Ana não tem PCP). Em OS-0430, Ana vê `Aprovar v1` (CMD-42; fica A liberar com o selo); Ver como Caio → `Liberar para execução` (CMD-06, REQ reservada). Caio antes do `Aprovar v1`: recusado, nada gravado. Trilha +3: AL-01 v1 → v2, CMD-42 por Ana (agrônoma), CMD-06 por Caio (PCP).
- AL-05 20 → 15 % por Ana: vale na hora; OS-0421 (350 ha) passa a até 52,5 ha. Trilha +1.
- AL-05 20 → 25 % por Ana: aguarda 2º aprovador e o comando segue com 70 ha; outra proposta para a AL-05 recusa (R8); Ana não confirma a própria; Ana concede gestor a Caio, Ver como Caio → `Confirmar AL-05` → 87,5 ha. Trilha +3 (proposta, concessão, confirmação).
- Conceder agrônomo a Caio: recusado (sem CREA). Ana concede direção a si: recusado (R3). Ana retira o próprio gestor: recusado (R5). Trilha +0 e `c.rev` igual.
- Desativar Paula: AL-12 sem titular (vermelho), primária `Resolver AL-12`; Paula some do Ver como; registros antigos seguem "Paula (conferência)"; a O.S. e o Estoque deixam de dizer "Paula (conferência) decide" e dizem que a conferência está sem titular. `Resolver AL-12` → Rui → `Conceder conferência a Rui`: AL-12 volta a ter titular. Trilha +2.
- Convidar Beto: acesso Ativo, só app; o CD-04 mostra o acesso; CF-05 "Pessoas com acesso: 11" (P7). Trilha +1.
- Desativar Marcos (só app): `Iniciar turno` no app recusa com o motivo; o CF-01 mostra "Desativado em 26/09/2026". Trilha +1.
- Ana libera a OS-0430 (3 reservas, fora da fila) e, com Ver como Rui, entrega Glifosato 480 no Estoque: fila do ERP 1; `Sincronizar` → enviado 1; de novo → 0 enviados. Trilha +5 (CMD-42, CMD-06, entrega, 2 sincronizações).

## 7. Passos (cada um deixa o protótipo funcionando)

- **P1 · Estado e regras, sem tela.** Bloco `<perfis>`: `G2_PAPEIS`, `G2_ALCADAS`, `g2conf`, `g2perfis`, `g2alc`; funções de perfil usam o efetivo. `dados_config.py` (`CONF0`, `js_prefixo()`), `configuracoes.js` (comandos e `confTrilha`), prefixo uma vez no `engine()`; Caio no `dados_cad.py` (campos da §6) e em `_ORDEM` (CAP:38). `G2_ALCADAS` sem AL-15 (entra no P7). Teste: `node config_unit.js` (R1-R5, R10, R12, R14 com cenário salvo de outra versão) + `os_aprov_lib_unit.js`, `aprova_quem_decide_unit.js`, `ap_unico_unit.js` sem mudança + `varredura.py` inteira; `cada_cd04_test.py:25-28` passa de 10 para 11 pessoas (motivo no commit); o CF-05 passa a contar 10 com acesso (Caio tem login).
- **P2 · Comandos leem a alçada.** Literais de papel e de pessoa do §0 → `g2alc`/`cenExigeAlc`/`g2quem` da alçada (`OS_LIB`, `OS_AGRO`, `CEN_CONF_AP`, `CEN_CONC_RESP` viram funções); mensagem de papel sem titular; limite da dispensa por R11 (mesma mensagem); `o.osc.disps`; `via: 'CMD-09'`; `cenAprovarAjuste` e `estRecontar` gravam quem recusou; app de campo lê o acesso (R2). Sem mudança visível no seed. Teste: `config_unit.js` (R7 linha a linha; grep sem literal em todas as linhas do §0; R2 do app) + testes de O.S., Estoque, App e Mapa existentes; mudam só os do §0 (P2), pelo nome da constante.
- **P3 · Aprovar e liberar por quem age (R13).** OSP e `inicio.py` (§0): `osc_aprovar`, selo, botão do ajuste. Teste: `os_aprov_lib_unit.js` A8 muda (motivo: caminho previsto no PLANO CTL-7: Beto aprova e fica em A liberar; Otávio libera depois; Otávio antes da aprovação é recusado); N5 e P1-P4 sem mudança; `legal_unit.js` sem mudança; `os_cenario_test.py` sem regressão além do vermelho conhecido.
- **P4 · CF-01 no menu.** Tela §3.1 em CFG; menu: entra só "Usuários e alçadas" (antes de "Assinatura e cobrança"); CD-04 lê o acesso (`cada_cd04_test.py:42-49` muda: o acesso sai do formulário, motivo no commit); CF-02 e CF-02det saem (`build.py:24`, `project/` e `_render/`); `gestao.py:490`, `suprimentos.py:1113`; `links_ocultos_test.py:34`. Teste: novo `config_test.py` (CF-01) substitui `cftest.py` (motivo: telas e números novos).
- **P5 · CF-04 Auditoria.** Tela §3.2 lendo `confTrilha`; CSV; menu ganha "Auditoria". Teste: `config_test.py` (CF-04) e `config_unit.js` (trilha de cada item do roteiro).
- **P6 · CF-03 Integrações.** Tela §3.3; CF-03det sai; dados locais sem uso saem de CFG; menu ganha "Integrações". Teste: `config_test.py` (CF-03) e `config_unit.js` (fila do ERP com estorno).
- **P7 · Assinatura no mesmo estado.** AL-15 entra em `G2_ALCADAS`. CF-05 conta pessoas por `confComAcesso()`; na tela do CF-05, pagar, aceitar, desfazer, pedir proposta e contestar passam `cenExigeAlc(g2perfil(), 'AL-15', ação)` como quem age, dentro do `cenMudar` (a recusa não grava). `assinIni` e os comandos do backoffice não mudam (BO-01/BO-02 seguem com "Admin plataforma"; exigir AL-15 ali pararia a conciliação). A condição de retorno da PLAT §9 está cumprida. Teste: `assinatura_unit.js` sem mudança + casos novos de AL-15; `assinatura_test.py:174, 192` e `plataforma_test.py:83` com "Ana (gestora)" nos atos novos (motivo no commit); perfil Rui recusado; `plataforma_test.py` conciliação e resolução sem mudança.

Em cada passo: `python3 build.py > /tmp/CONF-build.log; grep -c FALHA /tmp/CONF-build.log` = 0; `python3 montar_render.py`; navegador um por vez com `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdp9333.lock env CDP_GL=1 timeout 900 python3 <teste>`: `varredura.py`, `../ferramentas/acoes_duplicadas.py . /tmp/CONF-dup.json`, os testes do módulo e os afetados. Vermelhos conhecidos da base (lista do pedido) não são deste módulo e não são escondidos. JS dentro de string Python só com `/* */`.

## 8. Critérios de aceite (teste que prova)

| # | Critério | Teste |
|---|---|---|
| A1 | Sem `c.conf`, `g2perfis()` = `G2_PERFIS` (5 perfis, mesma ordem); cenário salvo de outra versão volta ao padrão | `config_unit.js` |
| A2 | Com um dia em "Duplicidade a conferir" (dois `cenApontar` na mesma data): conceder conferência a Rui → `cenApDecidir` com Rui grava "Rui (conferência)"; retirar: recusa sem gravar; mesma chave e mesmo conteúdo 2× = 1 evento, mesmo recibo; mesma chave com outro conteúdo = conflito, nada gravado | `config_unit.js` |
| A3 | Autoconcessão, agrônomo sem CREA e último gestor recusam com o motivo e `c.rev` igual | `config_unit.js` |
| A4 | Cada linha de `G2_ALCADAS` (AL-15 a partir do P7): perfil com os papéis passa e sem eles recusa no comando real, nos níveis `base` e `acima`; nenhum literal de papel ou de pessoa nas linhas do §0; AL-16 mostra os níveis de `dados2.ALCADA`, sem edição | `config_unit.js` |
| A5 | AL-01 → PCP: Ana aprova (só CMD-42, A liberar com selo; aprovar de novo recusa), Caio libera (só CMD-06); Caio antes da aprovação é recusado sem gravar; `Salvar e aprovar v2` grava o CMD-42 v2 e a v1 aprovada não libera a v2; `Salvar ajuste` não grava CMD-42 (N5); com AL-01 = gestor, Ana segue numa confirmação (P1-P4 sem mudança); 5 fases | `os_aprov_lib_unit.js` + `config_test.py` |
| A6 | Cada parte a partir do seed: AL-05 20 → 25 % por Ana fica pendente e o comando usa 70 ha na OS-0421; nova proposta para a AL-05 recusa; Ana não confirma a própria; Caio com gestor confirma → 87,5 ha; 20 → 15 % vale na hora (52,5 ha); 71 ha com o limite de 20 % recusa com a mensagem de hoje | `config_unit.js` + `config_test.py` |
| A7 | Alçada para papel sem titular ativo (AL-09 → direção) é recusada | `config_unit.js` |
| A8 | Desativar Paula: some do Ver como; AL-12 "Sem titular" e primária `Resolver AL-12`; O.S. e Estoque não dizem mais "Paula (conferência) decide"; registros antigos intactos; `Resolver AL-12` → `Conceder conferência a Rui` devolve o titular | `config_test.py` |
| A9 | Convidar Beto: acesso Ativo no CF-01 e no CD-04; CF-05 conta 11 | `config_test.py`, `assinatura_test.py` |
| A10 | Trilha: 14 registros no seed (jun 2 · jul 8 · ago 3 · set 1); cada item do roteiro da §6 acrescenta exatamente o "trilha +n" dele, cada ato uma vez com autor, data e objeto; duas dispensas na mesma O.S. = 2 linhas; "vale este" = 1 linha CMD-09 e nenhuma CMD-50; filtros pessoa, comando e mês; nada editável | `config_unit.js` + `config_test.py` |
| A11 | CSV = linhas filtradas, sem segredo; a exportação vira registro | `config_test.py` |
| A12 | 5 conexões com selo Demonstração; nenhum texto com cara de segredo (`/(senha|token|secret|apikey)\s*[:=]|[A-Za-z0-9_-]{24,}/i`) no texto visível das 3 telas, nos painéis abertos e no CSV; sincronizar 2× envia a fila uma vez; consumo enviado e depois estornado por "vale este" volta à fila uma vez, como estorno | `config_unit.js` + `config_test.py` |
| A13 | Uma primária (botão verde cheio) por tela em CF-01, CF-03 e CF-04 em cada estado da §3; com painel aberto, uma só, a do painel (medida do `acao_unica_test.py` v3); `acoes_duplicadas.py` sem achado | `config_test.py`, `acoes_duplicadas.py` |
| A14 | Toda grade com filtro e ordenação; `%` e `ha` na célula | `config_test.py` |
| A15 | Menu: Configurações por último, 4 itens na ordem da §2; CF-02, CF-02det e CF-03det fora de `project/` e `_render/`, sem link para eles | `config_test.py`, `links_ocultos_test.py`, `ls` |
| A16 | 390 px: primária visível, sem rolagem horizontal da página, painel em largura total | `config_test.py` (captura) |
| A17 | `cenReset()` volta acessos, alçadas, conexões e trilha ao seed | `config_unit.js` |
| A18 | CF-05: pagar e mudar plano com Ver como Rui recusam sem gravar; com Ana gravam "Ana (gestora)"; no BO-02, conciliar e resolver seguem com "Admin plataforma" com qualquer Ver como | `assinatura_unit.js`, `assinatura_test.py`, `plataforma_test.py` |
| A19 | Marcos desativado: iniciar e fechar turno, confirmar recebimento e ocorrência no app recusam com o motivo do acesso; o que estava na fila do aparelho envia; reativado, volta | `config_unit.js` |

## 9. Fora de escopo (condição de retorno)

| Item | Volta quando |
|---|---|
| Escopo por fazenda e objeto (RF-GOV-001) | um comando conferir a fazenda do objeto |
| Vigência, delegação e substituição temporária (RF-GOV-002) | o proprietário pedir, ou a fazenda real tiver férias de RT a cobrir |
| Login, 2º fator, PIN, sessões e dispositivos | software real (servidor) |
| Pessoa cadastrada ou inativada no CD-04 durante a demonstração | o CD-04 gravar no navegador |
| Políticas IR-LIM, PE-04, TL-01; testes digitados; teto de R$ 80 mil por O.S. | um comando ler o valor (custo previsto da O.S. num serviço único, ENG-011) e o proprietário definir o teto |
| AL-06 Reabrir saldo (CMD-48) e AL-08 Reordenar fila (CMD-37) | os comandos existirem no protótipo |
| Alçada da manutenção; alçada de compras editável e por papel (hoje AL-16 só leitura); Otávio; pessoa da Direção | as frentes PCM e SUP integrarem (§5) |
| Histórico anterior ao cenário (liberações e encerramentos do seed das O.S.) na trilha | segue na própria O.S. (Origem); a trilha começa no que o cenário grava |
| Exportação completa dos cadastros (a PLAT §9 a mandava para o CF-04) | o proprietário pedir; manifesto e checksum (RF-GOV-006) no software real |
| Pedido de acesso de Beto no IN-02 (tela oculta, dado local) | IN-02 voltar ao menu, lendo `c.conf` |
| Manutenção na trilha (estado próprio `talhao-os-manutencao-v1`) | a manutenção gravar no cenário |
| Apontamentos e contagens que conferem, na trilha | o proprietário pedir; seguem na O.S. e no Estoque |
| Parâmetros globais e documentação de processos (CF-04 antigo) | um parâmetro ser lido por comando; a documentação já está no Índice |
| Fila de erros do ERP com de-para e conciliação (CF-03det) | integração ERP em sandbox autorizada |
| Credenciais, conexão real, homologação e produção | autorização e custo aprovados pelo proprietário (AGENTS §2) |
| Mensagem real de convite (e-mail, WhatsApp) | nunca no protótipo; no software real, com autorização |
| Indicadores e metas (PRD 55, "Alçadas e regras › Indicadores e metas") | GE-06 voltar ao menu |

## 10. Revisão por contraexemplo (Claude, autor, 06/10/2026; **executado**: leitura do código da base `99537ca` e sondas `python3`/`grep`; nada foi implementado)

Revisão do próprio autor; não substitui a do Codex. Severidade pelo dano (AGENTS §3).

| # | S | Contraexemplo | Mudou |
|---|---|---|---|
| RV-01 | S2 | P7 punha AL-15 em `assinIni`, que o backoffice também usa: conferida pelo Ver como, `Conciliar pagamentos` e `Resolver` no BO-02 recusam se o perfil guardado for Rui; conferida pelo `por`, recusam sempre ("Admin plataforma" não está em `G2_PERFIS`) e os casos de `assinatura_unit.js` com `ADM` quebram. Fluxo da plataforma bloqueado por um perfil da organização | §0, R7 (AL-15), P7, A18, D21 |
| RV-02 | S3 | R13 dizia "ajustar grava o CMD-42": `Salvar ajuste` com liberação impedida registraria aprovação que a agrônoma não deu e quebraria N5; e "papéis em pessoas diferentes" não diz o que cada perfil vê | R13 por quem age, `osc_aprovar`, `Salvar e aprovar vN+1`, A5, P3, D15 |
| RV-03 | S3 | Trilha contaria o mesmo ato duas vezes ("vale este" grava `dec` no estornado e fecha casos CC com `por`; ajuste aparece em `c.ajustes` e em `c.movs`) e perderia atos (`osc_txt` sobrescreve `dispPor` na 2ª dispensa); "recebimento" ambíguo | §0, §5 (fontes por tipo), R14, A10 |
| RV-04 | S3 | Fila do ERP "uma vez por id": consumo enviado e depois estornado por "vale este" fica enviado e o ERP diverge do sistema; tipos da fila ambíguos (reserva e confirmação no app sem quantidade) | R17, A12, D20 |
| RV-05 | S3 | Desativar Paula deixava a O.S. dizendo "Paula (conferência) decide" (`CEN_CONF_AP`, `CEN_CONC_RESP`, `OS_AGRO` e textos fixos fora do §0); `cenario.js:199` e OSP:627, 633, 718, 843 ficavam com papel literal, então AL-10 → direção deixaria o Estoque nomeando a gestora | §0, R7, P2, A4, A8 |
| RV-06 | S3 | Desativar quem só usa o app (Marcos) não tinha efeito em lugar nenhum: controle que parece controle sem ser (o argumento da própria D06) | R2, §0, P2, A19, D24 |
| RV-07 | S3 | Mesma chave com outro conteúdo devolvia o recibo antigo: a 2ª mudança de papéis no mesmo painel sumiria em silêncio | R12, A2 |
| RV-08 | S3 | Princípio 1 ("nenhuma alçada fora da tabela que os comandos leem") era falso: a CMP (no menu) lê `dados2.ALCADA` (R$ 50.000 / R$ 300.000 / Direção), e o pedido fala em "valores" | §1, §0, R7 (AL-16), §5, §6, A4, D23 |
| RV-09 | S4 | Caio sem vínculo, admissão e custo: `pessoas()` lê `p['vinc']` e `p['custo']` e o build falharia | §6, P1 |
| RV-10 | S4 | Testes que mudam e não estavam listados (`os_aprov_lib_unit.js` A7; `ap_unico_unit.js` C0, C1, V4b, AT3; `aprova_quem_decide_unit.js:21`; `plataforma_test.py:83`); `aprova_quem_decide_unit.js:221-225` listado sem mudar; mensagem da dispensa conferida por `osacoes.py` | §0, R11, P2, P3, P7 |
| RV-11 | S4 | R9 contradizia o seed (AL-05 acima → direção, que ninguém tem); duas propostas pendentes na mesma alçada sem regra; roteiro somava itens dependentes (Beto 11 depois de desativar Paula) e A10 não dizia o que conferir | R8, R9, §6, A6, A10 |
| RV-12 | S4 | `Resolver AL-12` abria um painel sem ação (alçada fixa); `Convidar pessoa` tinha dois caminhos para o mesmo comando; regra da primária com painel aberto não escrita | §2, §3.1, A13 |
| RV-13 | S4 | `g2pf` analisaria o cenário salvo a cada chamada (cache só sem `cenario.js`); `CONF0.v` não mudava com `G2_PERFIS` de outra frente; nomes globais de `configuracoes.js` (em toda tela) sem regra; queda do Ver como para `G2_PERFIS[0]` desativado | §5, R2 |
| RV-14 | S4 | "App de campo ao vivo" contra o PRD CF-03; "3 pessoas" contando sistemas; datas da cobrança simulada misturadas sem rótulo; autor "Provedor (simulado)" sem regra frente à R14; `estRecontar` sem ator; reativar sem conferir CREA; menu com itens antes das telas novas; `suprimentos.py:1113`; condições de retorno da PLAT §9 e do IN-02 soltas | §3.2, §3.3, R4, R14, §0, P4-P6, §9 |

Conferido e mantido: números do seed (6 O.S. em A liberar, 5 Em execução, `c.movs` vazio, 10 pessoas e 9 logins no CD-04, 14 linhas de trilha por mês e por autor, limites 70 / 20 / 15,02 / 14,64 / 14,22 ha, 52,5 e 87,5 ha); Kanban de 5 fases; aprovação agronômica individual (nenhum caminho libera versão sem CMD-42; água só com água segue DEC-2609-10); idempotência por chave de quem inicia; fórmula da dispensa em `cenQtd`; nenhuma credencial.

## 11. Implementação (Claude, 06/10/2026; **executado** salvo indicação)

Commits na `claude/v44-config` (sem push): P1 `eb97164` estado e regras · P2 `47153cb` comandos leem a alçada · P3 `59df41c` aprovar e liberar por quem age · P4 `ca0016f` CF-01 · P5 `3046ba8` CF-04 · P6 `f6128ef` CF-03 · P7 `a3e9172` assinatura no mesmo estado · `1b021f3` índice e decisões D25-D30.

| Verificação | Comando | Resultado |
|---|---|---|
| Build | `python3 build.py > /tmp/CONF-build.log; grep -c FALHA` | 0 FALHA em cada passo |
| Regras sem navegador | `python3 config_unit_test.py` | 111/111 (A1-A12, A17-A19 e A4 linha a linha com AL-15) |
| Defeitos da base | `python3 config_regressao_test.py` · `GEN=<99537ca> python3 config_regressao_test.py` | 6/6 aqui · 0/6 na base (R1-R6) |
| Navegador do módulo | `config_test.py` (1440 e 390 px) | 57/57 |
| Varredura | `varredura.py` (após P7) e `varredura.py Main`/`CF-` (após o índice) | 135/135 · 1/1 · 4/4 páginas sem erro |
| Existentes afetados | os_aprov_lib 51/51 · aprova_quem_decide 102/102 · ap_unico unit 80/80 e nav 23/23 · legal 35/35 · assinatura_unit 76/76 · inicio_entrega 26/26 · links_ocultos 8/8 · cada_cd04 15/15 · plataforma 22/22 · os_ator 15/15 · est_cenario 15/15 · app_cenario 15/15 · map_decisoes 18/18 · map_aprov 5/5 · app_mb03_turno 11/11 · acao_unica familias 8/8 | sem falha |
| Ações repetidas | `../ferramentas/acoes_duplicadas.py . /tmp/CONF-dup.json` | 135 páginas · 0 com ação repetida |
| Vermelhos que já falhavam na base (iguais em 99537ca) | os_cenario 19/20 (PEND-OS-01) · consumo_divergente 20/21 · osacoes 40 ok · 5 falhas (lista da O.S. reformatada) · assinatura_test A9a (osc_liberar chamado sem quem age) | não são deste módulo; não foram escondidos |

Fora do que a §8 pede (continua na §9): pedido de acesso do IN-02, escopo por fazenda, vigência e delegação, manutenção na trilha, alçada de compras editável. Revisão do Codex: pendente.

### 11.1 Correções da revisão adversarial do `9f49bf0` e integração com a Colheita (Claude, 09/10/2026; **executado** salvo indicação)

Commits: `9193c49` correções F1–F13, F15 e parte do F16 (decisões CONF-D31 a D39) · `3d76176` merge de `claude/prototipo-v44` (`cdc185f`, Colheita e Planejar safra), 2 conflitos resolvidos sem perder lado · commit seguinte: F14, resto do F16 (`mbDescartar`) e o S3 de integração (atos da colheita na trilha, AL-17, app da colheita com acesso, recebimento pelo almoxarife ativo; CONF-D40 a D42).

| Verificação | Comando | Resultado |
|---|---|---|
| Build | `python3 build.py > /tmp/CONF-build.log; grep -c FALHA` | 0 FALHA · 137 telas |
| Render | `python3 montar_render.py` | 137 páginas |
| Regras sem navegador | `python3 config_unit_test.py` | 169/169; com as fontes do `3d76176` e estes testes, 10 falhas (INT1b, INT1c, INT2, INT3b, INT3d, INT4, F14b, F14c e os dois casos de texto do F14, sem as funções) |
| App de campo no mesmo estado | `python3 config_app_unit_test.py` (novo) | 4/4; 2/4 com as fontes do `3d76176` (F16 `mbDescartar` e "Entregue por" do movimento) |
| Defeitos da base | `python3 config_regressao_test.py` | 6/6 |
| Navegador do módulo | `config_test.py` (1440 e 390 px) | 70/70 |
| Varredura · ações repetidas | `varredura.py` · `../ferramentas/acoes_duplicadas.py . /tmp/CONF-dup.json` | 137/137 sem erro · 0 páginas com ação repetida |
| Existentes sem navegador | os_aprov_lib 51 · aprova_quem_decide 102 · legal 35 · assinatura_unit 76 · inicio_entrega 26 · ap_unico unit 80 · producao_unit 121 · capacidade 76 · ocupacao 104 · rend_multiconjuntos 106 · mip 34 · carencia unit 50 | sem falha |
| Existentes no navegador | producao_fluxo 66/66 · app_cenario 15/15 · app_entrega_parcial 7/7 · app_mb03_turno 11/11 · app_os0424 9/9 · app_saldo_zero 12/12 · ap_unico nav 23/23 · links_ocultos 8/8 · acao_unica (saf) 10/10 | sem falha (os textos com o almoxarife e o agrônomo no padrão continuam iguais) |
| Vermelhos que já falhavam na base | os_cenario 19/20 (PEND-OS-01) · consumo_divergente 20/21 (EST etapa 4) | iguais aos da §11; não são deste módulo; não foram escondidos |

Riscos que ficam: Comercial e Lúcia agem por nome do registro da colheita até entrarem no CD-04 e no catálogo de papéis (CONF-D41, condição de retorno); a AL-17 é nova (número seguinte à AL-16) e espera a revisão do Codex. Revisão do Codex: pendente.

### 11.2 Merge com o Beneficiamento (Claude, 09-10/10/2026; **executado** salvo indicação)

Commits: `dcfb781` merge de `0644b1b` (BEN-1; CONF-D43 e CONF-D44) · `82dfe5b` merge de `f6cb4f4` (rodada 1 da integração do BEN: "Cancelar a ordem", "Pedir mais caixas", "Enviar para conferência", complemento em outro lote) · `b103870` merge de `0139898` (rodada 2 do BEN). Sem conflito de texto nos dois últimos. Um merge de `a47578f` que ficou aberto na interrupção foi abortado e refeito direto sobre o mais novo. Os atos novos do BEN ("Ordem cancelada", "Caixas pedidas") entram na trilha pelo histórico da ordem, com autor e ordem de gravação; Igor desativado no CF-01 não cancela nem pede caixas.

| Verificação | Comando | Resultado |
|---|---|---|
| Build · render | `python3 build.py > /tmp/CONF-build.log; grep -c FALHA` · `python3 montar_render.py` | 0 FALHA · 138 telas · 138 páginas |
| Regras sem navegador | `python3 config_unit_test.py` | 179/179 (novos: INT5f-j; INT5b/d leem "Enviada para conferência", verbo novo da base) |
| App · defeitos da base | `config_app_unit_test.py` · `config_regressao_test.py` | 4/4 · 6/6 |
| Navegador do módulo | `config_test.py` (1440 e 390 px) | 70/70 (A11: "Exportação · 10 registros · mês jul/2026", eram 8 antes de Igor e Marta) |
| Varredura · ações repetidas | `varredura.py` · `../ferramentas/acoes_duplicadas.py . /tmp/CONF-dup.json` | 138/138 sem erro · 0 páginas com ação repetida |
| Beneficiamento | `ben_unit_test.py` · `ben_mutantes.py` · `ben_fluxo_test.py` (todos os modos) | 168/168 · 76/76 mortos · 168/168 |
| Existentes sem navegador (no `f6cb4f4`) | os_aprov_lib 51 · aprova_quem_decide 102 · legal 35 · assinatura_unit 76 · inicio_entrega 26 · ap_unico unit 80 · producao_unit 121 · capacidade 76 · ocupacao 117 · rend_multiconjuntos 106 · mip 34 · carencia unit 50 | sem falha |
| Existentes no navegador (no `f6cb4f4`) | producao_fluxo 66/66 · esttest OK · est_cenario 15/15 · est_fix1 13/13 · est_fix2 11/11 · tabelas_est 34/34 · links_ocultos 11/11 · cada_cd04 15/15 · ap_unico nav 23/23 · app_cenario 15/15 · app_entrega_parcial 7/7 · app_mb03_turno 11/11 · app_os0424 9/9 · app_saldo_zero 12/12 · acao_unica (saf) 10/10 | sem falha |
| Vermelhos que já falhavam na base | os_cenario 19/20 (PEND-OS-01) · consumo_divergente 20/21 (EST etapa 4) | iguais; não são deste módulo; não foram escondidos |

Riscos que ficam: no Estoque, "Entregar a" ainda é uma lista fixa de nomes (`PESSOAS` em `areas/processo_estoque.py`), o mesmo tipo de segundo cadastro do F6, fora do escopo desta revisão; as decisões delegadas de 09/10 que caem em Configurações (AGR-08 habilitação conferida ao aprovar, OPE-01 "PCP ou gestor" libera, PLA-23 papel Comercial e Lúcia, rótulo "padrão decidido" OPE-02 a OPE-06) ficam para depois da junção desta branch, como o próprio registro delas pede. Revisão do Codex: pendente.

### 11.3 Reverificação adversarial do `8be23d8` (Claude, 10/10/2026; **executado** salvo indicação)

Commit "CONF: ajustes da reverificação" (sem push; gravado em 13/10 por quem retomou a frente, depois de reexecutar build, unidade e navegador, §11.4). Seis achados das lentes independentes, todos S3 (nenhum S1 ou S2). Cada um tem um teste que reprova no `8be23d8` e a menor correção (CONF-D45 a D49):

| Achado | Correção | Teste (resultado no `8be23d8`) |
|---|---|---|
| 1 · Colheita pela web gravava o almoxarife deduzido como autor | `prAtorRec` (`producao.js`) confere o perfil de quem age onde quem recebe é o almoxarife; a tela passa `g2perfil()` | REV1a-i no `config_unit.js` (9 falham) · REV1 no navegador: Zé estorna a CG-2109 (falha) |
| 2 · Mutante M9 (aprovar sem a AL-02) sobrevivia às suítes sem navegador | proteção nova, sem mudança de código | REV2a-b passam no `8be23d8` e matam o M9 (201/203) |
| 3 · Trilha dizia "contou: Rui" com quem registrou; a causa não aparecia | efeito com `contador`, `reg` (só se for outra pessoa) e causa; o CSV repete | REV3a-c (3 falham; REV3d é referência) |
| 4 · Encerrar e enviar para conferência sem autor | `osc_fim` grava `o.osc.fim`; a trilha lê; O.S. e Início passam `g2perfil()` | REV4a-c (3 falham) · REV4 no navegador (falha: "16 registros · 3 autores") |
| 5 · Detalhe aberto no CF-04 trocava de registro quando outra aba gravava | `uid` estável por linha | REV5a-b (2 falham) · REV5 no navegador, com segunda aba (falha) |
| 6 · Gestora que retirava todos os próprios papéis passava o Ver como a outra pessoa | `confPapeis` recusa; a prévia avisa "Você sem nenhum papel" | REV6a (falha; REV6b-c são referências) · REV6 no navegador (2 falham) |

Mutantes das correções (`scratchpad/confrv/fix/mut_fix.py`, cópia própria do gen37): M9 e X1 a X5 (cada correção desligada), 6/6 mortos pelo `config_unit_test.py`.

| Verificação | Comando | Resultado |
|---|---|---|
| Build · render | `python3 build.py` · `python3 montar_render.py` | 0 FALHA · 138 telas · 138 páginas |
| Regras sem navegador | `python3 config_unit_test.py` | 203/203; com as fontes do `8be23d8`, 185/203 (as 18 falhas são os casos REV acima) |
| App · defeitos da base | `config_app_unit_test.py` · `config_regressao_test.py` | 4/4 · 6/6 |
| Navegador do módulo | `config_test.py` (1440 e 390 px) | 77/77 (novo: parte `rev`, 7); a parte `rev` sobre o `_render` do `8be23d8` (`RDIR=…`): 2/7, falham as 5 de REV1, REV4, REV5 e REV6 |
| Beneficiamento | `ben_unit_test.py` · `ben_mutantes.py` · `ben_fluxo_test.py` | 168/168 · 76/76 mortos · 168/168 |
| Existentes sem navegador | producao_unit 121 · os_aprov_lib 51 · aprova_quem_decide 102 · legal 35 · assinatura_unit 76 · inicio_entrega 26 · quantidade 14 · ap_unico unit 80 · carencia unit 50 · mip unit 34 | sem falha |
| Existentes no navegador | os_v39_bloq 11/11 · ap_unico nav: não concluído (o agente caiu pela cota antes do resultado) · producao_fluxo 64/66, ver abaixo | — |
| Varredura · ações repetidas | `varredura.py` · `../ferramentas/acoes_duplicadas.py . <saída>` | não concluídos nesta rodada (o agente caiu pela cota); ver §11.4 |
| Vermelhos que já falhavam na base | os_cenario 19/20 (PEND-OS-01, a mesma falha) · producao_fluxo "(1) Programar colheita S40 abre a ordem nova pré-preenchida": `[None, None]` também no `8be23d8` | não são desta correção; não foram escondidos |
| Instável | producao_fluxo A-04: falhou na bateria completa (a ordem da S40 não foi emitida depois de "Programar colheita S40"); repetido só o modo `revisao`, 18/18 aqui e 18/18 no `8be23d8` | a mesma espera curta depois de "Programar colheita" do item acima; fora desta frente |

Riscos que ficam: na Lagoa Grande, pesar, estornar e descartar seguem gravando "Lúcia" até ela entrar no CD-04 (CONF-D41); o botão "Pesar", "Estornar" ou "Descartar" ainda aparece para quem não tem o papel almoxarife, e o comando recusa dizendo quem decide (o mesmo padrão do "Encerrar"); o encerramento não tem alçada própria (CONF-D46, condição de retorno). Revisão do Codex: pendente.

### 11.4 Rodada de 13/10: todos os achados da reverificação do `8be23d8` (Claude; **executado** salvo indicação)

Base para classificar vermelhos: `8be23d8`. Achados: `scratchpad/v57/conf-achados.json` (lentes acesso, trilha e regressão). Os S3 e S4 de origem frente e correção foram todos corrigidos; dos de origem base, os três pedidos (Compra, irrigação só com água e chave de idempotência, esta tratada como S2) e o foco do painel nas telas de Configurações. Commits: `4711d96` (achados 1-6 da §11.3, trabalho do agente anterior conferido e reexecutado) e `3438fd4` (o restante, CONF-D50 a D56). Nenhum push.

Uma linha por achado (lente · severidade · origem):

| # | Achado | Situação | Commit | Teste que falha antes e passa depois |
|---|---|---|---|---|
| 1 | acesso · S3 · frente: colheita pela web gravava o almoxarife deduzido | corrigido (CONF-D45) | `4711d96` | REV1a-i (`config_unit.js`) · REV1 no navegador |
| 2 | acesso · S3 · frente: mutante M9 (aprovar sem a AL-02) sobrevivia | corrigido: REV2a-b matam o M9 (reexecutado em 13/10: 216/218 no mutante, as 2 falhas são REV2a-b) | `4711d96` | REV2a-b |
| 3 | acesso · S4 · correção: retirar os próprios papéis trocava o Ver como (F11 incompleto) | corrigido (CONF-D49) | `4711d96` | REV6a · REV6 no navegador |
| 4 | acesso · S4 · frente: mutante M13 (sincronizar e exportar sem perfil) sobrevivia | corrigido: teste negativo novo, sem mudança de código (o `8be23d8` estava certo) | `3438fd4` | REV7a: passa no código, falha no mutante M13 (217/218) |
| 5 | acesso · S4 · frente: BEN com produção e conferência (ou qualidade) na mesma pessoa, sem revisão posterior | corrigido (CONF-D54) | `3438fd4` | REV11a e REV11c (REV11b e d são referências) |
| 6 | acesso · S3 · base: Compra aprovava sempre como "Ana (Gerente da fazenda)" | corrigido (CONF-D52); a manutenção (`manLiberar`) fica para a frente PCM | `3438fd4` | `cmptest.py`: Ver como Rui sem "Aprovar compra"; Ana "Valor dentro da sua alçada (Ana · Gerente da fazenda"; trocar o Ver como some com a confirmação; "Compra aprovada por Ana (Gerente da fazenda)" |
| 7 | acesso · S4 · base: irrigação só com água liberada sem conferir o perfil e sem autor | corrigido (CONF-D53); o N4 do `os_aprov_lib_unit.js` passou a esperar o CMD-06 com autor | `3438fd4` | REV10a-b |
| 8 | trilha · S3 · frente: "contou: Rui" com quem registrou; a causa não aparecia | corrigido (CONF-D47) | `4711d96` | REV3a-c |
| 9 | trilha · S3 · frente: enviar para conferência e encerrar sem autor | corrigido (CONF-D46) | `4711d96` | REV4a-c · REV4 no navegador |
| 10 | trilha · S3 · frente: detalhe aberto no CF-04 trocava de registro quando outra aba gravava | corrigido (CONF-D48) | `4711d96` | REV5a-b · REV5 no navegador |
| 11 | trilha · S3 (tratado como S2: movimento duplicado) · base: dispensa, entrega e recebimento sem chave de idempotência | corrigido nos comandos que a trilha lê (CONF-D50); o que falta está na CONF-D50 (chave obrigatória e chamadas sem chave de outras frentes) | `3438fd4` | REV8a-e · REV14c no navegador (a dispensa pela tela grava com a chave gerada ao abrir) |
| 12 | trilha · S4 · correção: duplo clique da mão duplicava a exportação e a sincronização | corrigido (CONF-D51) | `3438fd4` | REV12a e REV12d no navegador (REV12b é referência: um clique depois é outra exportação) |
| 13 | trilha · S4 · correção: o realce do F13 pulava de linha quando outra aba gravava | corrigido pelo `uid` (CONF-D48); teste novo | `4711d96` + teste em `3438fd4` | REV12c no navegador |
| 14 | trilha · S4 · frente: "Registro de origem" igual para dispensas diferentes | corrigido (CONF-D55) | `3438fd4` | REV9a-b |
| 15 | regressão · S3 · correção: a gestora que retira os próprios papéis passava o Ver como a Caio | o mesmo do nº 3 (CONF-D49) | `4711d96` | REV6a · REV6 no navegador |
| 16 | regressão · S4 · frente: primária desabilitada do CF-01 com o motivo só no `title` | corrigido (CONF-D56) | `3438fd4` | REV13b no navegador (390 px) |
| 17 | regressão · S4 · frente: rodapé dos painéis não preso; primária abaixo da dobra a 390 px | corrigido no CF-01, CF-04 e CF-05 (CONF-D56) | `3438fd4` | REV13c no navegador (390 px) |
| 18 | regressão · S4 · frente: no CF-04 a 390 px, Quem sumia ao rolar | corrigido: Quem vai junto de Quando na coluna presa (CONF-D56, §3.2) | `3438fd4` | REV13a no navegador |
| 19 | regressão · S4 · frente: radiogroup de candidatos sem setas e com uma parada de Tab por opção | corrigido (CONF-D56) | `3438fd4` | REV14b no navegador |
| 20 | regressão · S4 · base: o foco não entrava no painel; Esc não fechava sem um Tab | corrigido nas telas de Configurações (CF-01, CF-03, CF-04, CF-05; CONF-D56); BO-02 e CD-04 ficam com as frentes deles | `3438fd4` | REV14a no navegador |

Recusados: nenhum.

Classificação no `8be23d8` (executado): `config_unit.js` desta rodada com as fontes do `4711d96` (o `8be23d8` mais a §11.3): 207/218; falham os 11 casos novos que dependem das correções (REV8a-e, REV9a-b, REV10a-b, REV11a, REV11c); REV7a passa (o código estava certo) e falha no mutante M13. Os testes de navegador novos (REV12a, REV12d, REV13a-c, REV14a-c e os do `cmptest.py`) não foram reexecutados sobre o `_render` do `8be23d8`: os defeitos foram reproduzidos pelas lentes no próprio `8be23d8` (§ achados), e a máquina estava compartilhada (regra de rodar cada teste uma vez).

| Verificação | Comando | Resultado |
|---|---|---|
| Build · render | `python3 build.py` · `python3 montar_render.py` | 0 FALHA · 138 páginas |
| Regras sem navegador | `python3 config_unit_test.py` | 218/218 |
| Mutantes | M9 e M13 (cópia própria do gen37 em `scratchpad/v57/conf/mut`) · `ben_mutantes.py` | M9 morto por REV2a-b · M13 morto por REV7a · 76/76 mortos |
| Outras suítes sem navegador | `os_aprov_lib_test.py` · `aprova_quem_decide_test.py` · `inicio_entrega_test.py` · `ap_unico_test.py unit` · `config_app_unit_test.py` · `config_regressao_test.py` · `producao_unit_test.py` · `ben_unit_test.py` · `legal_unit_test.py` · `assinatura_unit_test.py` | 51/51 · 102/102 · 26/26 · 80/80 · 4/4 · 6/6 · 121/121 · 168/168 · 35/35 · 76 |
| Navegador do módulo | `config_test.py` (1440 e 390 px; parte nova `rev2`) | sem falha restante. Execuções: todas as partes sobre o 1º build (cf01, cf05 e rev sem falha; 5 falhas de cf03/cf04/rev2 eram da 1ª versão do CONF-D51 e um passo da Compra que saiu para o `cmptest.py`); m390 3/3; no build final, cf04 + cf03 + rev2 33/33 |
| Navegador dos módulos tocados | `cmptest.py` · `assinatura_test.py` · `esttest.py 1 2` | sem falha, com as 5 verificações novas do Ver como · 45/45 · OK |
| Varredura | `varredura.py` | 138/138 páginas sem erro; depois do último build, CF-01, CF-03, CF-04 e CF-05 4/4 |

Riscos que ficam: a chave é opcional nos três comandos enquanto houver chamadas sem chave de outras frentes (CONF-D50); a irrigação só com água segue liberável por qualquer perfil ativo (CONF-D53, condição de retorno); "Gestor de suprimentos" da Compra sem papel no catálogo (CONF-D52). Revisão do Codex: pendente.
