# Configurações · decisões tomadas sem o proprietário

Cada decisão abaixo foi tomada pelo Claude para destravar o protótipo (CONF-01, `ESPECIFICACAO.md`). Nenhuma é decisão do proprietário. As pendentes dele que tocam este módulo continuam pendentes e com o padrão dos agentes: **PEND-OS-01** (quem libera a O.S.) e **PEND-CTL-02** (quem aprova ajuste de estoque e consumo acima da custódia). Rótulo: **especificado**. Revisor: Codex.

Formato: decisão · por quê · como reverter.

**CONF-D01 · Quatro itens no menu; usuários e alçadas numa tela só.** Configurações (último grupo): Usuários e alçadas (CF-01) · Auditoria (CF-04) · Integrações (CF-03) · Assinatura e cobrança (CF-05). CF-02 e CF-02det deixam de existir: o bloco Alçadas fica no CF-01.
- Por quê: o pedido limita o grupo a 4 itens com a assinatura. Papel e alçada respondem à mesma pergunta ("quem decide o quê"): a pessoa mostra o que decide, a alçada mostra quem decide. Juntar integrações e auditoria misturaria controle com conexão técnica.
- Reverter: em `MENU2` (`ui37.py:42`), um item próprio para CF-02 no lugar de Integrações, e o bloco Alçadas vira a tela `CF-02.dc.html` (mesmas funções).

**CONF-D02 · Ordem do grupo.** Usuários e alçadas, Auditoria, Integrações, Assinatura e cobrança.
- Por quê: primeiro o que define quem decide (planejamento), depois o controle, depois a parte técnica. A assinatura fica por último para não mudar o que a PLAT já testa (A16 da PLAT: "Configurações por último, com Assinatura e cobrança").
- Reverter: reordenar a lista em `MENU2`.

**CONF-D03 · Papel é permissão de decidir; função e habilidade ficam no CD-04.** Catálogo de 7 papéis (`G2_PAPEIS`): os 6 que já existem em `G2_PERFIS` e `cenExige` (gestor, agrônomo, PCP, almoxarife, conferência, mecânico) e **direção**, que o comando da dispensa já cita ("acima de 20 % · exige Direção", `processo_os.py:457`) e que ninguém tem no seed.
- Por quê: sem a direção no catálogo, a mensagem do comando manda a uma decisão que ninguém pode receber. Paula aparece como "Caldeiro" no CD-04 e com os papéis almoxarife e conferência (CTL-7): é coerente, porque papel não é função.
- Reverter: tirar `direcao` de `G2_PAPEIS`; a dispensa acima do limite volta a ser só recusada.

**CONF-D04 · Caio entra no CD-04.** p11, função PCP, equipe Agronomia, com acesso; habilidade "Conferir" (PRD CMD-48: "conferente ou PCP").
- Por quê: `G2_PERFIS` tinha Caio sem cadastro, ou seja, um segundo cadastro de pessoas. O CD-04 passa de 10 para 11 pessoas; o CF-05 conta 10 com acesso.
- Reverter: tirar p11 de `dados_cad.PESSOAS` e Caio de `G2_PERFIS` juntos (a R1 exige que todo perfil esteja no CD-04).

**CONF-D05 · Acesso e papéis no cenário (`c.conf`), sem subir `CEN0.v`.** O CD-04 mostra o acesso só para leitura, com link "Gerenciar em Configurações"; a opção "Solicitar acesso ao app" do CD-04 sai.
- Por quê: o mesmo estado da O.S., do Estoque e da assinatura (como `c.assin`, PLAT-D12); `cenario.py` não muda e não disputa linha com outras frentes. Um lugar para conceder evita o pedido no CD-04 e a concessão no CF-01 divergirem. "Restaurar demonstração" volta tudo ao seed.
- Reverter: chave própria no `localStorage`; o CD-04 volta a ter o campo (CAP:297) e o CF-01 passa a mostrar pedidos.

**CONF-D06 · O CF-01 não tem escopo por fazenda, vigência, delegação, autenticação nem sessões.**
- Por quê: nenhum comando do protótipo confere fazenda, vigência ou sessão; mostrar seria texto paralelo, que parece controle sem ser. Login e sessão são do servidor no software real.
- Reverter: cada item volta pela condição da §9 da especificação.

**CONF-D07 · Convite simulado aceito na hora, sem e-mail e sem campo de contato.**
- Por quê: o mesmo padrão do evento de pagamento da organização da demonstração (PLAT R9): menos um passo sem decisão. Nenhum dado de contato é coletado e nenhuma mensagem real é enviada (AGENTS §2).
- Reverter: estado "Convite enviado" e ação `Simular aceite` no painel da pessoa.

**CONF-D08 · Só o último gestor ativo é trava; alçada sem titular por retirada ou desativação é aviso.**
- Por quê: sem gestor, ninguém concede papel de novo e a organização fica trancada. Nos outros casos, desligar alguém tem de valer na hora (segurança da informação); a tela mostra "Sem titular" e a primária leva a resolver.
- Reverter: lista de papéis com trava de último titular em `G2_PAPEIS` (ex.: incluir conferência).

**CONF-D09 · Agrônomo só com CREA válido no CD-04, na data operacional (26/09/2026).**
- Por quê: PRD 2.1 (credencial técnica é atributo separado) e persona "Administrador não ganha aprovação técnica só por administrar". Hoje só Ana tem CREA.
- Reverter: tirar a checagem de `confPapeis`; o aviso de CREA fica só no CD-04.

**CONF-D10 · AL-01 alinhada ao padrão PEND-OS-01: o gestor libera.** O texto "Liberador do domínio · Caio (PCP)" sai; a alçada mostra o que o comando faz (`OS_LIB = 'gestor'` vira a linha AL-01 de `G2_ALCADAS`).
- Por quê: o CF-02 dizia uma coisa e o comando fazia outra (PLANO CTL-7, observação do risco aberto).
- **Como reverter (decisão do proprietário):** no CF-01, Alçadas › AL-01 › Papel **PCP**, com o motivo. Vale na hora, porque não amplia o poder de quem altera (R10). Com a R13, Ana aprova (CMD-42) e Caio libera (CMD-06). No código: `papeis:['pcp']` na linha AL-01 de `G2_ALCADAS`. Para voltar de PCP ao gestor depois, a mudança amplia o poder da gestora e precisa de um 2º aprovador (outro gestor ou a direção), ou da mudança no código.

**CONF-D11 · O teto "até R$ 80 mil por ordem" da AL-01 sai.**
- Por quê: nenhum comando calcula o valor da O.S.; o teto era texto. Valor previsto da O.S. pede o custo num serviço único (ENG-011).
- Reverter: quando houver custo previsto da O.S., campo `lim` em reais na AL-01 e a checagem no `osc_liberar`.

**CONF-D12 · Quatro pontos editáveis; os demais fixos com o motivo na linha.** AL-01 papel (gestor · PCP · agrônomo); AL-05 limite (1-100 %); AL-09 papel (gestor · direção); AL-10, só o excedente (gestor · direção).
- Por quê: são as duas pendências do proprietário (PEND-OS-01, PEND-CTL-02) e o "20 %" que o pedido cita. AL-02 é lei; AL-12, AL-13 e AL-14 protegem o próprio controle; o almoxarife não aparece como opção de ajuste nem de excedente, porque quem guarda o estoque não aprova a própria diferença.
- Reverter: campo `edita` da linha em `G2_ALCADAS`.

**CONF-D13 · Mudança que amplia o poder de quem altera espera um 2º aprovador** (outra pessoa ativa com gestor ou direção). Até lá vale a versão anterior.
- Por quê: RF-GOV-002 ("usuário não eleva a própria alçada") e PRD 2.1. Com uma gestora só, a ampliação espera até ela conceder gestor ou direção a outra pessoa; a redução vale na hora.
- Reverter: remover a checagem de `confAlcMudar` (toda mudança vale na hora, com registro).

**CONF-D14 · Alçada só aponta para papel que alguém ativo tem.**
- Por quê: apontar para ninguém para o fluxo (S2) por um clique, sem ganho.
- Reverter: trocar a recusa por aviso em `confAlcMudar`.

**CONF-D15 · Aprovar e liberar por quem age** (R13): quem tem os dois papéis segue numa confirmação; só o agrônomo vê `Aprovar vN` (`osc_aprovar`, só o CMD-42) e, no ajuste, `Salvar e aprovar vN+1`; só o liberador libera versão já aprovada (só o CMD-06). Selo "Aprovada vN · aguarda liberação" em A liberar. `Salvar ajuste` não aprova (revisão RV-02: aprovação só por ato explícito).
- Por quê: é o caminho previsto no PLANO (CTL-7, risco aberto) para quando o cadastro separar os papéis, e sem ele a AL-01 em PCP pararia toda liberação. Com os dois papéis na mesma pessoa, nada muda (PEND-OS-01). O Kanban continua com 5 fases.
- Reverter: tirar `osc_aprovar` e o selo; a AL-01 volta a aceitar só papéis que o agrônomo tenha.

**CONF-D16 · AL-05 em % da área da ordem, em decimal.** Limite em ha = `cenQtd(limite/100, área)`, comparado ao total dispensado mais o pedido.
- Por quê: é a regra que o comando já aplica (`processo_os.py:457`), agora pela regra decimal única em vez de ponto flutuante com folga de 0,001. O pedido diz "20 % de saldo"; o comando e o texto antigo usam a área da ordem, que não muda com o andamento.
- Reverter: trocar `o.area` por `o.saldo` na função única do limite (comando e painel juntos).

**CONF-D17 · Trilha lida dos registros, sem inferir autor.** Registro do cenário só com hora usa a data operacional (26/09/2026); registro sem autor aparece "autor não registrado". `cenAprovarAjuste` passa a gravar quem recusou.
- Por quê: o pedido proíbe trilha digitada; inventar autor ou data seria a mesma falha (AGENTS §2: não declarar o que não houve).
- Reverter: gravar data completa em `cenAgora` (muda todos os comandos) e tirar a data operacional da `confTrilha`.

**CONF-D18 · A trilha cobre decisões e movimentos de custódia; apontamentos, contagens que conferem e manutenção ficam fora.**
- Por quê: o pedido lista aprovado por, liberado por, ajuste, conferência e assinatura. Apontamento é fato do executor e já está na O.S.; a manutenção tem estado próprio e está em refação pela frente PCM.
- Reverter: incluir as fontes na `confTrilha` (a manutenção quando gravar no cenário).

**CONF-D19 · CF-04 com uma ação: `Baixar trilha (CSV)`.** Parâmetros globais e documentação de processos saem.
- Por quê: exportar é a ação do auditor (PRD CF-04 "Exportar autorizado"; RF-GOV-006) e vira registro. Os parâmetros não eram lidos por nada; a documentação já está no Índice.
- Reverter: restaurar os blocos de `99537ca` (CFG:431-445).

**CONF-D20 · Integrações: 5 conexões só de demonstração.** ERP · Sankhya, estação meteorológica, telemetria de máquinas, laboratório de análises e app de campo. TOTVS sai; CF-03det sai; a fila do ERP são os movimentos que mudam o físico (recebimento de NF, entrega, devolução, ajuste, consumo baixado), enviados uma vez por conteúdo: o estornado depois de enviado volta uma vez como estorno (RV-04); nenhuma credencial existe.
- Por quê: uma organização tem um ERP; a fila do cenário mostra idempotência de verdade em vez de erro digitado; o conflito offline já é decidido na O.S. (CMD-09). Nenhum segredo pode entrar no protótipo (ENG-017).
- Reverter: restaurar CF-03det e a linha TOTVS de `99537ca` (CFG:289-414).

**CONF-D21 · A assinatura passa a usar o mesmo estado (P7).** Pagar, mudar plano, desfazer, pedir proposta e contestar exigem AL-15 (gestor) pelo Ver como, na tela do CF-05; `assinIni` e o backoffice ("Admin plataforma", fora da organização) não mudam (RV-01); "Pessoas com acesso" vem do `c.conf`.
- Por quê: as duas condições de retorno da PLAT §9 ("Ver como integrado"; "CF-01 existir") passam a valer. O autor gravado muda de "Ana · Gestora" para "Ana (gestora)", o formato dos outros comandos.
- Reverter: a tela do CF-05 volta a passar o texto fixo `CF_POR` em vez de `cenExigeAlc(g2perfil(), 'AL-15', …)`; `CF_PESSOAS` volta a contar `dados_cad`.

**CONF-D22 · Seed com os eventos de implantação.** Acesso de Ana pela plataforma em 28/06/2026; Ana concede aos outros 8 em 01/07/2026 e a Lucas em 01/08/2026.
- Por quê: a trilha começa com o que a implantação grava, nas datas do contrato v1 da PLAT e da admissão no CD-04, gerado de `dados_cad` (não digitado na trilha).
- Reverter: `CONF0.ev = []` em `dados_config.py`; a trilha começa só com os registros da assinatura.

**CONF-D23 · Alçada de compras (AL-16) só para leitura, lida de `dados2.ALCADA`.** O CF-01 mostra os níveis que a Compra de insumos já aplica (até R$ 50.000,00, até R$ 300.000,00, acima Direção), sem cópia e sem edição.
- Por quê: o pedido fala em "valores" e a única alçada em reais do protótipo é essa; esconder deixaria uma alçada fora da tela que diz quem decide. Editar ou ligar a papéis é da frente Suprimentos, que muda a CMP agora (uma solução por problema).
- Reverter: tirar a linha AL-16 do `CONF0`; nada muda na CMP.

**CONF-D24 · O app de campo respeita o acesso desativado.** Com o operador desativado, iniciar e fechar turno, confirmar recebimento e registrar ocorrência recusam; a fila já no aparelho envia.
- Por quê: sem isso, desativar quem só usa o app não teria efeito (RV-06). Dano evitado: fato de campo em nome de quem foi desligado.
- Reverter: tirar a checagem `cenAppAtivo` dos quatro comandos do app em `cenario.js`.

## Decisões da implementação (06/10/2026, Claude; rótulo: executado no código, revisão do Codex pendente)

**CONF-D25 · Painel fecha depois de gravar.** Salvar papéis, Convidar, Desativar e Reativar (painel Pessoa) e as ações do painel Alçada fecham o painel; o aviso diz o que foi gravado e a linha e o cabeçalho mostram o novo estado.
- Por quê: o resultado fica visível na própria tabela e no estado do cabeçalho; o painel aberto com o estado antigo convidaria a repetir.
- Reverter: tirar `cf1_p:null` / `cf1_a:null` do segundo argumento de `cf1Run` em `areas/configuracoes.py`.

**CONF-D26 · O papel agrônomo fica desabilitado no painel da pessoa sem CREA válido, com o motivo na própria chave.** O comando continua recusando (R4).
- Por quê: não oferecer o que a lei impede; a trava fica no comando, a tela só não convida ao erro.
- Reverter: tirar `semCrea` de `dis` em `v.cf1_paps` (o comando segue recusando com a mesma mensagem).

**CONF-D27 · Pessoa desativada: a primária do painel é "Reativar acesso".** A especificação listava Reativar como secundária; sem papel a salvar, ela é a única ação útil.
- Reverter: mover o botão para o grupo das secundárias (`rod_p`).

**CONF-D28 · Filtro rápido das alçadas por Editáveis · Fixas · Só leitura · Pendências** (marcas da coluna Mudança). A grade aceita um filtro rápido por coluna; "Pendências" junta "Aguarda 2º aprovador" e "Sem titular".
- Reverter: `qf` da grade `g_alc` em outra coluna.

**CONF-D29 · Chave e rascunho do comando são os do desenho.** O 2º clique no mesmo botão antes de redesenhar repete o mesmo comando com a mesma chave (mesmo recibo, R12). Achado no teste de navegador do P4: com a chave nova e o rascunho antigo, o 2º clique desfazia a mudança.
- Reverter: não reverter (dano: mudança desfeita em silêncio).

**CONF-D30 · Selo "Aprovada vN · aguarda liberação" amarelo e dono = quem libera (AL-01).** Mesma cor das pendências que não são impedimento.
- Reverter: cor e dono em `osMerge` (`areas/processo_os.py`).

## Decisões das correções da revisão adversarial (09/10/2026, Claude; rótulo: executado no código e nos testes, revisão do Codex pendente)

**CONF-D31 · A trilha ordena pela ordem de gravação (F1).** `cenMudar` carimba `sq = c.rev` do comando em cada registro novo (o que já existia fica com 0); a trilha ordena por data, `sq`, hora e fonte. A coluna Quando do CF-04 ordena pela mesma ordem.
- Por quê: o registro guarda só HH:MM; dentro do mesmo minuto a trilha mostrava o PCP liberando antes de a alçada permitir. Dano evitado: auditor lê uma sequência de atos que não aconteceu.
- Reverter: tirar `confCarimbar` de `cenMudar` (volta a ordem da fonte dentro do minuto).

**CONF-D32 · Quem apontou e decide a própria duplicidade fica com revisão posterior (F3, AL-12).** O CMD-09 vale e grava `revisão posterior pendente (X apontou o dia N e decidiu)` no registro, no aviso e na trilha; o painel da pessoa avisa ao dar conferência a quem aponta.
- Por quê: é o padrão já adotado para quem contou e aprova o ajuste e para a quarentena (PEND-CTL-02); recusar pararia o fluxo quando a única conferência também aponta. Dano evitado: área e consumo somados por quem executou sem ninguém saber.
- Reverter para trava: em `cenApDecidir`, trocar a marca `rv` por `throw` quando `rv` não for vazio.

**CONF-D33 · Recusar mudança de alçada (F7).** Quem pode confirmar (gestor ou direção, nunca quem propôs) também recusa; a proposta sai, a vigente segue e a recusa entra na trilha. Desativar quem propôs retira a proposta dessa pessoa, com nota no registro do acesso.
- Por quê: sem isso, proposta de quem perdeu o acesso prendia a alçada (só restava confirmar a ampliação).
- Reverter: tirar `confAlcRecusar` e o botão "Recusar mudança"; a retirada ao desativar fica (sem ela a alçada volta a prender).

**CONF-D34 · Ninguém desativa o próprio acesso (F11).** A R5 (último gestor) vem antes, com a mensagem que explica o caminho.
- Por quê: o Ver como trocava de pessoa em silêncio e o próximo ato saía em nome de outra.
- Reverter: tirar a checagem `k0 === p.k` em `confAcesso` e o `!eu` de `cf1_pdes`.

**CONF-D35 · Contador do inventário sem lista fixa e sem valor padrão (F6).** As opções são as pessoas com acesso Ativo e o papel almoxarife; a 1ª opção é "Escolha quem contou"; o comando recusa contador fora dessa lista; a recontagem sugere o outro almoxarife ativo ou deixa vazio.
- Por quê: a lista fixa era um segundo cadastro de pessoas e o padrão gravava o fato em nome de quem não contou (inclusive desligado).
- Reverter: não reverter (dano: fato em nome de pessoa desativada). Para voltar a sugerir alguém, sugerir o perfil de quem age quando ele tiver almoxarife.

**CONF-D36 · Aprovar não espera estoque nem máquina (F4).** Quem só tem a AL-02 vê "Aprovar vN" mesmo com a liberação impedida por saldo, lote ou máquina; o impedimento aparece no texto, para a liberação. Regra legal, total 0 e carência continuam segurando a aprovação.
- Por quê: o `osc_aprovar` não depende do estoque; a tela atrasava a aprovação em série com o Suprimentos.
- Reverter: tirar o bloco `espera` de `osProx`.

**CONF-D37 · Idempotência pelo pedido e versão esperada (F2).** O conteúdo comparado da chave vem do que a pessoa pediu (escolha, motivo e a versão que o painel mostrava); pedido sobre uma versão que mudou é recusado com "reabra e confira".
- Reverter: não reverter (dano: reenvio depois de timeout pareceria falha, e uma decisão poderia valer sobre uma versão que a pessoa não viu).

**CONF-D38 · CSV sem fórmula (F5).** Célula que começa com `= + - @`, tab ou CR ganha `'` na frente (trilha e fatura); número puro fica como está.
- Reverter: não reverter (dano: motivo digitado vira fórmula ao abrir no Excel ou LibreOffice).

**CONF-D39 · Integrações: a última sincronização simulada nunca volta no tempo e o app diz "pelo sinal do aparelho (simulado)" (F15).**
- Reverter: em `confSincronizar`, gravar a hora do relógio sem o máximo.

## Decisões da integração com a Colheita e do F14 (09/10/2026, Claude; rótulo: executado no código e nos testes, revisão do Codex pendente)

**CONF-D40 · Atos da colheita entram na trilha (S3 de integração da revisão).** O CF-04 lê do `c.producao` os atos com autor dos comandos da colheita: publicar previsão (AL-17), pesar e receber carga, estornar carga, descartar carga a pesar, liberar lote de produto, reservar e cancelar reserva de produto e expedir, com data e hora do próprio registro e a ordem de gravação (CONF-D31). O que veio do seed (`CEN0.producao`) é histórico anterior ao cenário (§9) e fica no domínio. Contagem de frutos e carga a pesar são fato de campo, como o apontamento: entram pelo que decidem (a previsão publicada e a pesagem).
- Por quê: a trilha única não mostrava quem liberou um lote para venda nem quem estornou uma carga. Dano evitado: decisão sobre produto e dinheiro sem autor rastreável.
- Reverter: tirar `confTrilhaProd` de `confTrilha` e o bloco `producao` de `confCarimbar` (`configuracoes.js`).

**CONF-D41 · Quem age na colheita vem do papel, onde o papel existe (S3 de integração).**
- Publicar previsão vira a alçada **AL-17** (padrão: agrônomo, como a especificação da Colheita; editável: agrônomo · gestor · PCP), lida por `prPublicar` com o perfil de quem age (Ver como). Sem o papel, recusa sem gravar. O texto "quem publica" vem da alçada.
- Contagem, carga e descarte pelo app respeitam o acesso do operador (`cenAppAtivo`), como iniciar, pausar e fechar turno.
- ~~Receber na fazenda onde recebe o almoxarife (Santa Rita, Boa Vista) grava o almoxarife ativo (`cenAlmox`), não "Rui" fixo.~~ Substituído pela CONF-D45 (10/10/2026): o almoxarife ativo ainda era um autor deduzido.
- Ficam como estão, até entrarem no CD-04 e no catálogo de papéis: Comercial (reservar) e Lúcia (recebimento na Lagoa Grande). Condição de retorno: o proprietário confirmar essas pessoas e papéis; então viram linhas de `G2_ALCADAS` no mesmo formato. A Qualidade saiu desta lista no merge com o Beneficiamento (CONF-D44): liberar lote passou a exigir o papel qualidade ou agrônomo (BEN-1).
- Por quê: com o Ver como, a previsão era gravada em nome de "Ana (agrônoma)" mesmo quando outra pessoa publicava, e um operador desativado ainda gravava contagem (CNT-0002). Dano evitado: fato registrado em nome de quem não agiu ou foi desligado (R2).
- Reverter a AL-17: tirar a linha de `G2_ALCADAS` (`g2lib.js`); `prPublicar` volta a gravar o nome recebido.

**CONF-D42 · Textos da O.S. e do app pela alçada e pelo registro (F14).** Na O.S. em A liberar, "Ana (agrônoma) confere, ajusta se precisar e libera" vira "… e aprova; Caio (PCP) libera" quando as alçadas AL-02 e AL-01 têm pessoas diferentes; a ordem nova e a v2 da irrigação com produto na água ("o agrônomo confere, ajusta se precisar e libera") dizem o mesmo, com os nomes. No app, "Entregue por X" vem do movimento da entrega; "retire com", "devolva a sobra ao/à" e o MB-05 usam o almoxarife ativo; "decisão de …" sobre a área restante vem da AL-02.
- Reverter: tirar `osCondLib` de `osMerge` e voltar os literais (`areas/processo_os.py`, `areas/mobile.py`).

## Decisões do merge com o Beneficiamento (`claude/prototipo-v44` em `0644b1b` e depois em `3b1e7e2`, 09/10/2026, Claude; rótulo: executado no código e nos testes, revisão do Codex pendente)

**CONF-D43 · Atos do beneficiamento entram na trilha.** O CF-04 lê o histórico de cada ordem de beneficiamento (`o.ben.hist`, uma linha por ato com autor: criar, retirar entrada, autorizar a versão (CMD-42), liberar (CMD-06), iniciar, registrar e estornar saída, concluir, justificar diferença, confirmar correção, conferir balanço, reabrir, fechar (CMD-23) e, desde o `3b1e7e2`, cancelar em A liberar (BEN-D22) e pedir mais caixas (complemento da mesma REQ); "Execução concluída" passou a "Enviada para conferência") e as decisões da Qualidade sobre o lote de produção (`c.producao.movs`: resultado, liberação, reclassificação, bloqueio e destinação com lote). O histórico que veio do seed fica no domínio (§9, como na CONF-D40); a destinação do Fechar, sem lote, é efeito do CMD-23. `benMudar` carimba a ordem de gravação como o `cenMudar` (CONF-D31).
- Por quê: com o merge, o Beneficiamento passou a gravar atos com autor fora da trilha única. Dano evitado: lote liberado ou destinado sem autor visível na auditoria.
- Reverter: tirar o bloco das ordens de beneficiamento e as chaves `resultado`, `reclassificação`, `bloqueio` e `destinação` de `CONF_PMV` (`configuracoes.js`) e o carimbo de `benMudar` (`ben.js`).

**CONF-D44 · Igor e Marta entram no catálogo de papéis.** O BEN-1 trouxe Igor (responsável de produção) e Marta (qualidade) ao CD-04 e a `G2_PERFIS`. `G2_PAPEIS` ganha `producao` e `qualidade`, para que o CF-01 conceda e retire esses papéis e, com `c.conf` salvo, eles continuem valendo (sem a entrada no catálogo, a primeira mudança no CF-01 apagaria os dois papéis e travaria o beneficiamento). Os comandos do beneficiamento seguem pedindo o papel direto (`cenExige(ator, 'producao')`); só viram alçada editável quando o proprietário pedir outro titular.
- Efeito nos números do seed: 13 pessoas no CD-04, 12 com acesso, 16 registros na trilha (2 acessos a mais na implantação).
- Reverter: tirar as duas entradas de `G2_PAPEIS` (`g2lib.js`); não reverter enquanto o BEN-1 exigir esses papéis.

## Decisões da reverificação adversarial do `8be23d8` (10/10/2026, Claude; rótulo: executado no código e nos testes, revisão do Codex pendente)

**CONF-D45 · Colheita pela web: quem pesa, estorna e descarta é quem age (achado 1).** Onde quem recebe é o almoxarife (Santa Rita e Boa Vista), `prReceber`, `prEstornar` e `prDescartarCarga` gravam o perfil de quem age (Ver como; a tela passa `g2perfil()`) e recusam sem gravar quando ele não tem o papel almoxarife ("decisão de Rui (almoxarife)"). O texto de quem recebe (`prRec`) só diz quem deve agir e nunca vira autor. Pelo app, o descarte segue com o operador do aparelho. Na Lagoa Grande, o registro segue com o nome da colheita (Lúcia) até ela entrar no CD-04 (CONF-D41, risco declarado).
- Por quê: R14 ("nunca se infere autor"). Com Rui desativado, a pesagem feita por Zé saía em nome de Paula. Dano evitado: carga pesada, estornada ou descartada em nome de quem não agiu.
- Reverter: não reverter. Para abrir o ato a outro papel, trocar `'almoxarife'` em `prAtorRec` (`producao.js`) por uma alçada de `G2_ALCADAS`.

**CONF-D46 · Enviar para conferência (CMD-08) e encerrar (CMD-10) gravam quem agiu (achado 4).** `osc_conferencia` e `osc_encerrar` recebem o perfil de quem age e gravam `{cmd, por, at}` em `o.osc.fim`. A trilha lê uma linha por ato. Não há alçada nova: vale qualquer perfil ativo (`cenQuem`), como antes, e perfil desativado ou fora do cadastro é recusado sem gravar. O que segura o encerramento continua sendo `cenPodeEncerrar` (requisitos locais, PRD RN-047). O encerramento que veio do seed fica na O.S. (§9).
- Por quê: o servidor é a autoridade no encerramento (PRD 24; AGENTS §4) e o ato não tinha autor rastreável. Dano evitado: ordem encerrada sem saber por quem.
- Condição de retorno: se a "regra autorizada" do CMD-10 (PRD) virar um papel definido, ela entra como linha de `G2_ALCADAS`, lida pelo `osc_fim`.
- Reverter: tirar `osc_fim` (`areas/processo_os.py`) e o bloco `x.fim` de `confTrilha` e `confCarimbar` (`configuracoes.js`).

**CONF-D47 · Ajuste de inventário na trilha: quem contou, quem registrou e a causa (achado 3).** O efeito diz "contou: <contador>", "registrou: <perfil>" (só quando foi outra pessoa) e "causa: …". O CSV repete o mesmo texto.
- Por quê: a linha dizia "contou: Rui" com o perfil que registrou, e a causa, obrigatória para aprovar, não aparecia. Dano evitado: o auditor lê um contador que não contou.
- Reverter: não reverter.

**CONF-D48 · Linha da trilha com identidade estável (achado 5).** Cada linha tem `uid` = id do registro de origem (repetição ganha sufixo). O detalhe aberto e o realce do CF-04 guardam o `uid`, não a posição.
- Por quê: um ato gravado em outra aba deslocava as posições, e o painel aberto passava a mostrar outro registro sem clique. Dano evitado: o auditor lê data, objeto e link de um ato que não abriu.
- Reverter: não reverter.

**CONF-D49 · Ninguém retira todos os próprios papéis (extensão da CONF-D34, achado 6).** `confPapeis` recusa quando quem age ficaria sem nenhum papel, e a prévia do painel avisa ("Você sem nenhum papel"). Retirar parte dos próprios papéis continua permitido (R3). Outra pessoa com a AL-13 pode retirar todos os papéis dela.
- Por quê: sem papel, a pessoa sai do Ver como (R2) e o perfil cai em silêncio no primeiro efetivo; o ato seguinte saía com o nome e o poder de outra pessoa.
- Reverter: tirar a checagem `!novo.length && k0 === p.k` em `confPapeis` (`configuracoes.js`) e a linha da prévia (`areas/configuracoes.py`).

## Decisões da rodada de 13/10 (S3/S4 restantes da reverificação e achados de base pequenos; Claude; rótulo: executado no código e nos testes, revisão do Codex pendente)

**CONF-D50 · Dispensa, entrega e recebimento levam a chave de quem inicia (achado de base da trilha, tratado como S2: movimento duplicado).** `cenIdem` (`cenario.js`) guarda o recibo por chave em `c.recibos`: a mesma chave com o mesmo conteúdo devolve "já registrado" sem novo efeito; com outro conteúdo, recusa como conflito (ENG-021/022, PRD 73.3, como `cenApontar` e o R12). Recebem a chave: `osc_dispensar` (CMD-47), `cenEntregar`, `cenReceber` e as funções da tela do Estoque `estEntregar` e `estReceber`. O painel "Dispensar saldo" gera a chave ao abrir; o formulário do Estoque, no 1º envio, e ela fica no próprio formulário (reenvio e duplo clique repetem a chave).
- Por quê: repetir o comando duplicava a dispensa, a entrega ou o recebimento, o movimento e a linha da trilha. Dano evitado: movimento duplicado (S2).
- O que falta (registrado, fora desta frente): sem chave o comando segue como antes, para não quebrar ~45 chamadas de testes e telas de outras frentes que chamam `cenEntregar`, `cenReceber` e `osc_dispensar` sem chave (`ben_unit.js`, `ben_fluxo_test.py`, `aprova_quem_decide_unit.js`, `ap_unico_unit.js`, `inicio_entrega_unit.js`, `os_aprov_lib_unit.js`, `config_unit.js`, `config_app_unit_test.py`, `config_regressao_test.py`, `quantidade_test.py`, `tabelas_est_test.py`, `os_v39_bloq_test.py`, `os_cenario_test.py`, `consumo_divergente_test.py`, `app_*_test.py`, `est_fix1_test.py`, `est_fix2_test.py`, `est_repro.py`, `ostela.py`, `osacoes.py`, `osfix.py`, `ap_unico_nav.py`). Tornar a chave obrigatória no software real é do contrato do servidor (PRD 73.3), não do protótipo. A devolução (`cenDevolver`) e o app de campo (confirmar recebimento) ficam como estão: não foram apontados e já têm trava de estado.
- Reverter: não reverter.

**CONF-D51 · Duplo clique da mão em "Baixar trilha" e "Sincronizar agora" (achado de correção do F16).** O 2º clique de um duplo clique (`event.detail > 1`, contado pelo navegador) ou um 2º clique antes de a tela redesenhar (mesmo nº de desenho) repete o MESMO pedido (mesma chave, mesmo número de linhas e filtros) e recebe o mesmo recibo, sem 2º arquivo; um clique depois do redesenho é outra exportação ou sincronização. Sem janela de tempo, para não engolir um clique deliberado logo depois (uma 1ª versão com 500 ms engolia e foi trocada).
- Por quê: a tela troca a chave depois de gravar e redesenha entre os dois eventos de mouse; o 2º clique usava a chave nova. Dano evitado: exportação e sincronização em dobro na trilha.
- Reverter: tirar `confRepJanela` (`configuracoes.js`) e o `self.__cf3u`/`self.__cf4u` e `rid` das telas.

**CONF-D52 · Compra de insumos aprova pelo Ver como (achado de base).** Quem aprova é o perfil de quem age, lido na hora: com o papel direção, nível Direção; com gestor, Gerente da fazenda; sem um dos dois, nenhum nível ("Sem alçada de compra no perfil de …", envia à alçada). A confirmação confere o perfil de novo antes de emitir os pedidos. O registro fica "Ana (Gerente da fazenda)", o mesmo formato de antes.
- Por quê: a aprovação gravava sempre "Ana (Gerente da fazenda)", mesmo com Ana desativada ou outro Ver como. Dano evitado: compra aprovada em nome de quem não agiu.
- Condição de retorno: "Gestor de suprimentos" (1º nível de `dados2.ALCADA`) não é papel do catálogo; quando a frente Suprimentos ligar os níveis a papéis (CONF-D23), o mapa sai desta função para uma alçada de `G2_ALCADAS`. A manutenção (`manLiberar`) também não recebe quem age (lido no código, não executado): fica para a frente PCM.
- Reverter: `cmpPerfil` volta a devolver `CD.perfil` (`areas/processo_compras.py`).

**CONF-D53 · Irrigação só com água: o CMD-06 tem autor (achado de base).** `osc_liberar` com água confere o perfil ativo de quem age antes de gravar e registra o CMD-06 em `o.osc.ev` ("… irrigação só com água, sem aprovação agronômica (DEC-2609-10)"); a trilha lê. Sem alçada nova: a AL-01 deixa a água de fora (prontidão operacional), e qualquer perfil ativo libera, como antes. O teste N4 do `os_aprov_lib_unit.js` passou a esperar só o CMD-06 (sem CMD-42).
- Por quê: com o perfil desativado a ordem era liberada e nada registrava quem liberou. Dano evitado: ordem liberada sem autor. A DEC-2609-10 dispensa a aprovação agronômica, não a autoria.
- Condição de retorno: se o proprietário definir quem libera a irrigação (operador de irrigação, PCP), vira linha de `G2_ALCADAS` lida aqui.
- Reverter: tirar o bloco `qw` de `osc_liberar` (`areas/processo_os.py`).

**CONF-D54 · Beneficiamento: mesma pessoa na produção e na decisão fica com revisão posterior (achado da frente).** Com o CF-01, produção, conferência e qualidade podem estar na mesma pessoa. Conferir o balanço de uma ordem que a pessoa produziu (saída ou envio para conferência) e registrar o resultado ou decidir o lote que ela produziu (saídas do lote) valem, com "revisão posterior pendente" no registro, no histórico, no movimento e no aviso (padrão 2, o mesmo da AL-09, AL-11 e AL-12). Não trava.
- Por quê: antes, os papéis fixos garantiam pessoas diferentes. Dano evitado: balanço ou lote aprovado por quem o produziu, sem outro olhar registrado.
- Reverter: `benRevProd` e `benRevLote` (`ben.js`) devolvem ''.

**CONF-D55 · Registro de origem único por linha da trilha (achado da frente).** Quando dois atos da mesma fonte teriam o mesmo "Registro de origem" (duas dispensas da OS-0421, CMD-42 de v1 e v2, o histórico de uma ordem de beneficiamento), cada um ganha "nº k" na ordem da própria fonte, que não muda quando outra fonte grava. Vale no detalhe e no CSV.
- Por quê: o auditor não conseguia citar um ato específico. Reverter: tirar o bloco `nsrc`/`isrc` de `confTrilha`.

**CONF-D56 · Telas de Configurações no toque e no teclado (achados S4 da lente de regressão).**
- A primária desabilitada do CF-01 diz o motivo no próprio rótulo ("Convidar: decisão de Ana (gestora)"), não só no `title` (convenção do engine).
- Os rodapés dos painéis do CF-01, CF-04 e CF-05 casam com a regra de rodapé preso do engine (`padding-top: 6px`): a primária do painel fica à vista a 390 px.
- No CF-04 a 390 px, Quem vai junto de Quando na 1ª coluna (a presa), como pede a §3.2; a coluna Quem continua para a largura do computador.
- "Resolver AL-xx" e as opções de papel da alçada: radiogroup com um ponto de Tab e setas que movem e marcam.
- O foco entra no painel ao abrir e Esc fecha sem um Tab antes, nas telas de Configurações (CF-01, CF-03, CF-04, CF-05), por opção do `painel(..., foco=True)` e do `data-foco` no `g2lib.js`. O BO-02 usa o mesmo `painel()` e fica como está (frente Plataforma: basta passar `foco=True`); o CD-04 tem painel próprio (frente Cadastros) e também fica.
- Reverter: cada item pelo próprio trecho marcado "revisão CONF 13/10".
