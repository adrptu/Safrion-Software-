# Plataforma de assinaturas · decisões tomadas sem o proprietário

Cada decisão abaixo foi tomada pelo Claude para destravar o protótipo. Nenhuma é decisão do proprietário: preços, trial, franquias, base de cobrança e régua continuam **a decidir pelo proprietário** (DEC-01, DEC-05, DEC-09 do PRD 70.4). Rótulo: **especificado**. Revisor: Codex.

Formato: decisão · por quê · como reverter.

**PLAT-D01 · Duas visões, uma no menu.** A organização vê só o CF-05 "Assinatura e cobrança", no grupo Configurações, por último no menu. O backoffice da plataforma (BO-01, BO-02) fica fora do menu do agricultor, acessível pelo índice do protótipo.
- Por quê: PRD 57.5 isola o backoffice ("não aparece na navegação do agricultor"); o pedido coloca "Assinatura e cobrança" em Configurações.
- Reverter: acrescentar um grupo "Plataforma" em `MENU2` (`ui37.py:35-41`) com BO-02 e BO-01.

**PLAT-D02 · De 9 telas para 3.** CF-05det, BO-01det, BO-02det, BO-03 e BO-03det viram o detalhe da linha; BO-04 sai.
- Por quê: essencialismo (menos telas, master-detail); a medição e a memória são o detalhe da fatura ou da organização, não telas próprias.
- Reverter: restaurar as funções de `9c617c4` (`configuracoes.py:526-553`, `onboarding_backoffice.py:298-582`) e tirar os nomes da lista de `build.py:23`.

**PLAT-D03 · Três planos de exemplo.** Avaliação (30 dias, R$ 0); Essencial (R$ 1,50/ha·mês, mínimo R$ 199, satélite 6 cenas e IA 100 por mês); Completo (R$ 2,00/ha·mês, mínimo R$ 299, satélite 12 e IA 200: a hipótese do PRD 57.2 e as franquias do BO-01det atual). Os dois pagos vão até 5.000 ha.
- Por quê: mostrar "o que cada plano inclui" e a troca com prévia precisa de ao menos dois planos pagos. O Essencial é valor novo, só de exemplo.
- Reverter: editar a tabela de planos em `dados_assinatura.py` (fonte única); as três telas e a prévia leem dela.

**PLAT-D04 · Corte de módulos pela onda do PRD 18.1, sem partir a cadeia da O.S.** O núcleo (Mapa, Cadastros, Agrícola com O.S. e app, colheita e produção por talhão, Manutenção, Suprimentos) está em todos os planos. Pós-colheita (beneficiamento), comercial e logística, gestão e resultados e integração ERP só no Completo.
- Por quê: o núcleo é uma cadeia (O.S. → reserva → entrega → apontamento → colheita → produção → custo). Partir essa cadeia entre planos deixaria O.S. sem estoque, sem bloqueio de máquina ou colheita sem registro de produção. Controles essenciais não são opcionais (PRD 57.2). E2 depende de E1, não o contrário. Revisão de 06/10 (RV-11): a colheita saiu do Completo porque a O.S. de colheita é núcleo e o registro da produção é o fato dela; a frente colheita põe "Produção" no menu.
- Reverter: mover módulos entre os planos na mesma tabela; a regra R15 continua a impedir que o núcleo seja partido.

**PLAT-D05 · Base de cobrança (DEC-01).** Cobra-se a área cultivável dos talhões ativos (medida no cadastro), limitada pela área contratada. A memória mostra também quanto seria pela área contratada.
- Por quê: o pedido quer o uso lido dos cadastros. O PRD 57.2 quer área contratada, versionada e com aceite para ampliar. Com o limite, o desenho de um talhão nunca vira cobrança-surpresa. Pousio não reduz a cobrança, porque o talhão segue Ativo. A memória com os dois valores ajuda o proprietário a decidir.
- Reverter: parâmetro `BASE='contratada'` em `dados_assinatura.py`; a cobrada passa a ser a contratada, sem outra mudança.

**PLAT-D06 · Usuários sem limite e fora da cobrança.** A tela mostra quantas pessoas têm acesso, como informação.
- Por quê: PRD 58.1 ("colaboradores convidados não precisam contratar uma segunda assinatura"). Assim o produtor não deixa de cadastrar o operador por medo de custo.
- Reverter: coluna "Usuários incluídos" na tabela de planos e um termo por usuário excedente em `assinMensalidade`.

**PLAT-D07 · Calendário de exemplo.** O período é o mês civil e fecha no último dia. A fatura é emitida e vence no dia 1 do mês seguinte, com 3 tentativas em 10 dias. Não há pró-rata: a área do fechamento vale para o mês.
- Por quê: o legado do PRD 57.4.1 (dia 1; 3 tentativas em 10 dias) já estava no CF-05. Sem pró-rata, o mês tem uma conta só, legível. O limite contratado impede que um talhão do dia 29 vire surpresa.
- Reverter: parâmetros `DIA_VENC`, `TENTATIVAS` e `PRORATA` em `dados_assinatura.py`.

**PLAT-D08 · Régua de inadimplência.** Com 1 a 10 dias de atraso, só aviso. Com 11 dias ou mais, a organização não amplia a área medida: não cria talhão novo (cadastro, desenho ou importação) nem reativa talhão inativo. Corrigir a área de um talhão existente e trocar o contorno seguem. Nenhuma ação de O.S., estoque, irrigação, manutenção, colheita, consulta ou exportação é restringida, e nada é apagado.
- Por quê: o pedido quer aviso e restrição gradual, sem perda de dado. Restringir O.S. empurraria o trabalho de campo para fora do sistema, sem aprovação agronômica, carência e rastreio, o que é pior para a segurança e para os dados. A ampliação aumenta o custo de servir sem pagamento; a dívida não cresce por ela, porque a área acima do contratado não é cobrada (R2). Bloquear a correção da área de um talhão existente atingiria a integridade do fato registrado, por isso fica fora.
- Reverter: parâmetros `DIAS_AVISO` e `RESTRICOES` (lista de ações) em `dados_assinatura.py`. Com lista vazia, fica só o aviso.

**PLAT-D09 · Mudança vale do próximo ciclo.** Mudança de plano ou área começa no dia 1 seguinte e nunca retroage. No aceite, a área contratada precisa ser maior ou igual à medida do dia.
- Por quê: PRD 57.2 e PRECO-04. O mínimo da área evita contratar pouco e gerir muito pagando o mínimo.
- Reverter: parâmetro `INICIO='imediato'` (com pró-rata, PLAT-D07). O piso da área só sai com nova decisão.

**PLAT-D10 · Dinheiro em decimal pela regra que já existe.** O valor sai de `cenQtd(preço, área)`, o decimal exato com 2 casas e arredondamento meio para cima de `cenario.js:29-40`. As áreas somam em centésimos inteiros.
- Por quê: ENG-011 e ENG-013 (fórmula única, decimal). Executado: `2570.23*1.5` dá 3855.3450000000003 em ponto flutuante, e a soma das áreas dá 2570.2299999999996.
- Reverter: não se reverte. Uma regra de dinheiro diferente da de quantidade exige ADR.

**PLAT-D11 · Pagamento simulado.** Na organização da demonstração, o evento simulado do provedor chega no clique de pagar. Nas outras organizações, a fatura só fica Paga por "Conciliar pagamentos" no BO-02.
- Por quê: mostrar ao proprietário, num passo, que pagar tira o aviso e a trava, sem abandonar a regra de evento validado (PRD 58.4). A conciliação continua demonstrada no BO-02. A forma de pagamento é escolhida numa lista (Pix, boleto, cartão final 4242 · simulado): nenhuma tela tem campo de cartão, conta ou documento, porque uma página publicada não pode coletar dado de pagamento.
- Reverter: em `assinPagar`, gravar o evento na fila do provedor em vez de aplicá-lo; a fatura fica Pendente até conciliar.

**PLAT-D12 · Estado em `c.assin` sem subir `CEN0.v` e sem tocar o `cenario.py`.** O seed da assinatura fica só em `ASSIN0` (`dados_assinatura.py`), anexado uma vez a toda tela pelo `engine()`. Um cenário salvo sem `assin` vale `ASSIN0` na leitura; a primeira gravação o copia para `c.assin`. Telas sem `cenario.js` leem a mesma chave e aceitam o cenário só com o `v` vigente, como o `cenGet`.
- Por quê: o pedido quer tudo no mesmo estado. Subir a versão descartaria o progresso salvo de quem testa as O.S. e disputaria o número com outras frentes (o SUP-2a também sobe `v`). Editar o `cenario.py` disputaria a mesma linha com elas, e um seed em `CEN0` e outro para as telas sem `cenario.js` seriam dois seeds na página (revisão de 06/10, RV-01 e RV-22).
- Reverter: incluir `assin` no `CEN0` e subir `v` no `cenario.py:80`, com o aviso de que o salvo é descartado; `ASSIN0` passa a ser lido de lá.

**PLAT-D13 · Data simulada só da cobrança.** Um painel "Demonstração" no CF-05 avança a data da cobrança (23/09, 01/10, 06/10, 16/10). Os outros módulos seguem em 23/09, e as outras organizações não fecham período.
- Por quê: sem avançar a data não dá para ver fatura, atraso e trava. Avançar a data de todo o protótipo mudaria todos os módulos.
- Reverter: tirar o painel; a assinatura fica em 23/09.

**PLAT-D14 · Organização e outros clientes do seed.** "Grupo Santa Rita" reúne as três fazendas do cadastro, inclusive a Lagoa Grande sintética. Os outros clientes são reduzidos a cinco produtores, um por estado. Parceiros e patrocínio saem (Fertisul, Coop. Verde Vale).
- Por quê: um cliente por estado basta para mostrar a carteira. Os planos de parceiro dependem do DEC-05, e o portal está fora do menu.
- Reverter: acrescentar organizações em `dados_assinatura.py`; parceiros voltam com o PT-07 (fora de escopo §9).

**PLAT-D15 · Contestação mínima.** Contestar congela a régua daquela fatura. A plataforma resolve mantendo o valor (novo vencimento em 5 dias) ou creditando no período seguinte. A fatura contestada nunca é reescrita.
- Por quê: é o contrapeso da trava, porque não se restringe cliente por cobrança que ele contesta (PRD BO-03). Fica no último passo (P6) e não bloqueia os anteriores.
- Reverter: tirar `Contestar` e `Resolver`. A régua volta a contar sem exceção.

**PLAT-D16 · Terceira cópia da regra de mescla do cadastro.** `assinMedir` repete a regra de `tmBase` (`talmapa.js:7-11`): o salvo primeiro, depois a base para os ids que faltam, e os inativos saem. Um teste unitário compara as duas sobre o mesmo dado.
- Por quê: `talmapa.js` e `cad_fazendas.py` são de outras frentes ativas. Extrair a regra agora criaria conflito com elas. O P5 toca esses arquivos só com uma linha de guarda em cada ponto que amplia a área (revisão de 06/10, RV-24); a extração mexe nas funções inteiras e fica para a frente de cadastros.
- Reverter (quitar a dívida): mover a regra para uma função pura comum quando a frente de cadastros tocar `talmapa.js` e `cad_fazendas.py`, e apagar as cópias.

## Decisões da implementação (06/10/2026)

**PLAT-D17 · obotest.py fica, só com o onboarding.** A especificação mandava substituí-lo por plataforma_test.py, mas ele também cobre ON-01 e ON-01det, que não mudaram.
- Por quê: tirar o teste inteiro deixaria o onboarding sem cobertura. Os blocos BO-01..BO-04 saem (telas e números novos) e o backoffice novo fica em plataforma_test.py.
- Reverter: apagar obotest.py quando o onboarding ganhar teste próprio.

**PLAT-D18 · Recibo com sequência por tipo.** PAG- (pagamento), ACE- (aceite), CON- (conciliação), CTS- (contestação), RES- (resolução), cada um de 0001.
- Por quê: o recibo que a pessoa vê começa em 0001 no primeiro pagamento, mesmo depois de um aceite; a chave de idempotência continua sendo a de quem inicia (R8).
- Reverter: uma sequência única em `assinRecibo` (assinatura.js).

**PLAT-D19 · A data simulada vale para todas as organizações; só a da demonstração fecha período.** Os dias de atraso da Aurora e o dia do trial da Boa Esperança andam com a data do painel Demonstração.
- Por quê: um relógio só na tela. As outras organizações não fecham período (PLAT-D13), então os números de mensalidade delas não mudam.
- Reverter: guardar `hoje` por organização em `c.assin.orgs[id]`.

**PLAT-D20 · Crédito da contestação vai para o período aberto na data da resolução.** Resolvida em 16/10, o crédito aparece na prévia de out/2026 e entra na fatura quando ela fechar; a fatura contestada volta a vencer em 5 dias e não é reescrita.
- Por quê: R16 ("linha negativa na próxima fatura") sem reescrever a contestada; o painel Demonstração não passa de 16/10, por isso o crédito se vê na prévia.
- Reverter: aplicar o crédito no período seguinte ao da fatura contestada (`assinResolver`).

## Decisões das correções da revisão adversarial (06/10/2026)

**PLAT-D21 · Medida do período = a maior entre a da abertura e a do fechamento** (achado 3; muda o "a área do fechamento vale para o mês" do PLAT-D07).
- Por quê: com a foto só do fechamento, inativar o B1 (120 ha) em 23/09 e reativá-lo em 01/10 tirava 120 ha da cobrança de setembro (contraexemplo executado pelo revisor). Com o piso, inativar não reduz o mês em curso e reativar depois do fechamento entra no mês seguinte. Pousio não muda nada (o talhão segue Ativo, PRD 57.2).
- Limite conhecido: talhão criado e inativado dentro do mesmo mês não entra (o pico dentro do mês não é medido; medir exigiria gravar a cada edição do cadastro, em arquivos de outras frentes). Com `base='contratada'` (DEC-01) o limite some.
- Reverter: tirar `aberturas` de `dados_assinatura.py` e de `assinAvancar`; `assinMedPeriodo` passa a devolver a medida do fechamento.

**PLAT-D22 · Uma contestação por fatura; crédito com teto acumulado e saldo que segue.** (achados 1 e 2)
- A fatura contestada e resolvida não é contestada de novo (a recusa cita o RES-). O crédito somado de uma fatura nunca passa do valor dela. O crédito que passa da fatura do período vira saldo da competência seguinte (memória e CSV mostram "saldo de crédito R$ X para mês/ano"). Fatura de R$ 0,00 nasce quitada pelo crédito: não pede pagamento nem conta atraso.
- Por quê: sem isso, o ciclo contestar → resolver repetia créditos sem limite e congelava a régua para sempre; e R$ 1.285,11 sumiam entre o BO-02 e o CF-05.
- Reverter: não se reverte sem outra regra de contestação decidida pelo proprietário.

**PLAT-D23 · Quem age fica gravado em todo ato da assinatura.** (achado 4)
- Aceite, desfazer, pagamento, contestação, resolução, conciliação e pedido de proposta recusam sem autor e gravam `por` no contrato, no recibo, na fatura e no evento. O CF-05 age como "Ana · Gestora" (perfil da casca) e a plataforma como "Admin plataforma". O contrato desfeito fica guardado com quem desfez (nada se apaga).
- Por quê: PRD 58.4 (login não dá poder de contratar) e PRECO-04 (aceite). Quem *pode* agir segue fora de escopo (§9); quem *fez* não podia faltar.
- Reverter (evoluir): trocar as constantes `CF_POR`/`BO_POR` pelo `g2perfil` quando a frente D (CTL-3) integrar.

**PLAT-D24 · Estado salvo da assinatura com versão própria.** (achado 7) `ASSIN0.v` = versão do formato + resumo do seed (ex.: `2-9670ad1a`). Estado salvo de outro build ou de outro cadastro (KML real no Mac) volta ao seed na leitura e na próxima gravação, como o `cenGet` faz com o cenário.
- Reverter: comparar só a versão do formato (`VERSAO`), sem o resumo.

**PLAT-D25 · Acima de 5.000 ha a primária do CF-05 é "Pedir proposta empresarial".** (achado 10) O pedido é um registro (PRO-0001, com quem pediu), visível no BO-02; nenhuma mensagem real é enviada. Depois do pedido a primária fica desabilitada com a data. A sugestão de "Ampliar área contratada" nunca passa de 5.000 ha.
- Reverter: tirar o ramo `proposta` de `assinPrimaria`.

**PLAT-D26 · Primária do BO-02 pela próxima ação real.** (achado 9) Evento a conciliar → "Conciliar pagamentos" (chave estável no clique repetido); senão contestação aberta → "Resolver contestação" (abre a organização); senão "Conciliar pagamentos" desabilitado com o motivo. O botão do painel passa a "Registrar resolução", para não ter o mesmo rótulo de abrir e de confirmar (RV-18).

**PLAT-D27 · Faixa curta no celular e redesenho só quando a faixa muda.** (achados 12 e 11) Até 640 px a faixa mostra "Fatura de set/2026 vencida há 15 dias · talhão novo suspenso" com o link na mesma linha (de 123 px para cerca de 48 px). As telas sem medição só redesenham quando estado, dias ou data da cobrança mudam; o cadastro só redesenha CF-05, BO-01 e BO-02.

## Para o proprietário decidir (sem pressa; o protótipo funciona com os exemplos)

1. Base de cobrança: área contratada ou área medida no cadastro (DEC-01; PLAT-D05). Contraexemplo para a decisão: com a área medida, o mês precisa de um piso (PLAT-D21) e mesmo assim um talhão criado e inativado dentro do mês não é cobrado; com a área contratada, nada disso existe.
2. Preço, mínimo e franquias de cada plano, e se haverá dois planos (DEC-09; PLAT-D03, D04).
3. Duração do trial, retenção depois do fim e calendário de cobrança (DEC-09; PLAT-D07).
4. Régua de inadimplência: dias e o que é restringido (PLAT-D08).
5. Preços e trial dos parceiros (DEC-05; fora de escopo).
