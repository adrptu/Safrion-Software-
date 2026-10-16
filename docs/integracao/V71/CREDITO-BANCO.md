# CRE-BANCO · Dossiê de crédito para banco e fundo, preenchido pelo sistema

> Proprietário, 16/10/2026 (com duas planilhas anexas): "para voce e codex desenhar melhor a parte de credito, analisem esses 2 arquivos que é o que os bancos pedem para iniciar tratativas de empréstimo. Implementem isso da melhor forma possível no nosso módulo de credito, com maxima intuitividade, simplicidade e rapidez e clareza para o usuário e banco / fundo fazer o credito o mais rapido possivel, sem retrabalho e sem confusão."

## Pedido melhorado

- **Resultado:** o produtor monta, em minutos, o dossiê que o banco ou o fundo pede para abrir a conversa de crédito. O sistema preenche tudo o que já sabe. O produtor digita só o que falta, uma vez, e a resposta serve para todos os dossiês seguintes.
- **Quem usa:**
  - direção ou financeiro do grupo: monta, completa, autoriza e envia;
  - analista do banco ou do fundo: lê, baixa no próprio modelo e pede complemento;
  - agrônomo e almoxarife: são a origem dos dados de safra e de estoque, sem tarefa nova.
- **Restrições:**
  - cada número mostra de onde veio: sistema, cálculo ou declaração;
  - uma data-base por dossiê, e versão enviada não muda;
  - nada sai sem consentimento com finalidade, destinatário, dados e prazo;
  - dados pessoais só os que o modelo do credor exige (NFR-17);
  - nenhuma regra de crédito inventada: o sistema entrega dados, e quem decide é o credor.
- **Pronto quando:**
  - o dossiê do modelo completo de banco sai com as pendências listadas, cada uma com a pergunta e o motivo;
  - o segundo dossiê, para outro credor ou modelo, não pede de novo nada do que já foi respondido;
  - o credor abre o link, vê a versão concedida com a origem de cada número, baixa no próprio modelo e pede complemento pelo mesmo lugar.

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: CRE-BANCO / o dossiê de crédito sai do sistema no modelo de cada credor, com pendências claras, versão congelada, consentimento e link de leitura / direção e financeiro do grupo; analista do banco ou do fundo
Requisitos do PRD e fora do escopo: GE-08, PT-04, FO-20, FO-42, FL-22, CAL-19, RN-039, 57.4.2, NFR-17, DEC-1610-14 (CAD-02), AGENTS §3.3 e §4; fora: §Fora do escopo
Autor / revisor / integrador: Claude / Codex / Codex (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: claude/v44-v69-mapa em b93e06f / areas/gestao.py (_ge08 e GE-08det novo), areas/parceiros.py (pt04, pt04det), ui37.py (Crédito no MENU2 e CURTO37), dados_credito.py (novo: modelos sintéticos e mapa campo → fonte), credito.js (novo: montagem, unidades, coerência, versão e consentimento), credito_menu_test.py (atualizado), cre_dossie_unit.js e cre_dossie_test.py (novos)
Aceite e comando de verificação: C1–C14 abaixo / node cre_dossie_unit.js; python3 -B cre_dossie_test.py; python3 -B credito_menu_test.py; mais pttest.py e getest.py
Estado / impedimento / próximo passo: especificado; aguarda a revisão do Codex; entra quando uma das frentes abertas entrar na versão publicada (§3.6); depende da CAD-02 (documentos de crédito saem do Cadastro) e reaproveita o link da ENTREGA-FAZ
```

## O que os bancos pedem (estrutura das duas planilhas)

**Sigilo (ENG-017).** Os dois arquivos foram lidos fora do repositório, numa pasta temporária, só como dados, sem executar macro. Daqui só sai estrutura: abas, seções, rótulos, unidades, listas, fórmulas e contagens. Nenhum valor, nome, documento, endereço, matrícula ou instituição foi copiado. Os arquivos não entram no repositório.

**A · Questionário completo.** 9 abas: 6 de preenchimento, 2 de instrução (texto em imagem) e 1 oculta com as listas.

| Aba | Seções e campos |
|---|---|
| Dados pessoais | Data-base. Até 25 pessoas do grupo com 8 colunas: nome, CPF/CNPJ, grau de parentesco, atua na atividade, data de nascimento, função (5 opções), tempo na atividade, regime de casamento (4 opções) |
| Questionário de safra | Série de **10 safras**: 4 anteriores, a de referência e 5 futuras. A referência é o ano-safra que contém a data-base, com virada em setembro. 36 blocos e 458 linhas, cada linha com unidade. 20 blocos no padrão de grãos, cada um com 4 seletores (cultura em 7 opções, época 1ª/2ª/3ª, sequeiro ou irrigado, UF) e 11 linhas: área, produtividade, produção*, volume com preço fixado em US$ e em R$, preço fixado em US$ e em R$, preço médio final*, volume já entregue*, custo por hectare e % do custo incorrido (* calculado em parte das safras). Também: sementes (23 linhas), algodão (2 × 17), café (2 × 15), laranja (2 × 16), cana (14), bovinos em cria, recria e engorda (9, 12 e 16 linhas, 16 obrigatórias), suínos (14), leite (11), eucalipto (11), aves de postura e de corte (15 cada). Uma coluna de observação por bloco |
| Ativos | Premissas: data-base, câmbio, soja (R$/sc), cana (R$/t) e boi (R$/@). Caixa e aplicações (7 × 6). Recebíveis de produto entregue (15 × 7, vencimento em 3 faixas desde a data-base). Produto acabado (16 × 4). Insumos (2 linhas). Semoventes (13 × 5). Imóveis próprios (102 × 12, com CAR, áreas em produção, a abrir e de reserva, R$/ha, área já em garantia, tipo da garantia e credor). Arrendados de terceiros (9 × 9) e para terceiros (9 × 8). Área irrigada. Máquinas, infraestrutura e armazenagem. Outros imóveis (13 × 2). Participações (6 × 5) |
| Passivos | Dívida bancária (110 × 14: instituição numa lista de cerca de 80, finalidade em 5 opções, moeda, taxa, vencimento final, saldo e 7 faixas anuais). Dívida de terras (11 × 14, em R$, sacas, US$, cana ou boi). Fornecedores, inclusive barter (17 × 8). Outras dívidas (4 × 7). Um atalho "Retirada da família" sem seção correspondente |
| Outros resultados | Venda de terras e de outros ativos a receber (5 faixas). Despesas gerais e administrativas: 12 meses passados, 12 seguintes e depois |
| Intenção de investimentos | Compra de terras (3 × 11). Novos investimentos (6 linhas com fontes e 3 faixas). Investimentos realizados (6 linhas com fontes) |

Valores em R$ mil e em mil sacas. Listas suspensas em todas as escolhas; células de cultura travadas por validação. A planilha tem vínculo externo com um modelo de análise do credor, cujas abas indicam bureau de crédito, áreas embargadas, preço de terra de referência e cenários. Essa análise é do credor, e o dossiê não a refaz.

**B · Simplificado.** 6 abas: 4 de preenchimento e 2 ocultas.

| Aba | Seções e campos |
|---|---|
| Questionário de safra | Cadastro: nome do grupo; até 10 pessoas (nome, CPF, vínculo em 4 opções, tomador e avalista sim ou não); região; e-mails; endereço para documentos; data-base. Série de **3 safras** (passada, atual e futura). 20 blocos e 195 linhas: 9 de grãos (cultura, manejo, época; área, rendimento, preço, custo/ha, mais 5 calculadas: produção, receita, custo total, resultado e margem), café, gado (2), suínos, cana, leite, aves, algodão e 3 culturas livres. Resumo por safra |
| Ativos | Caixa; recebíveis; produto acabado com valor; insumos; semoventes; terras próprias (12 × 6, com área produtiva, de pasto e de reserva); arrendadas (12 × 7); outros imobilizados; outros recebíveis de curto e longo prazo; participações (6); intenção de investimento (8 usos × fontes × descrição × valor em 12 meses). Valores em R$ milhões |
| Passivos | Bancária (38 linhas, 2 de exemplo, 6 faixas por ano-calendário), terras (8), fornecedores (7) e outras dívidas (7) |
| Patrimônios detalhados | Imóveis urbanos (10 × 6, com proprietário e valor de mercado), máquinas e veículos da fazenda (10 × 6, com ano, proprietário e valor de mercado) e veículos particulares (7 × 5) |
| Ocultas | Listas de safras e instituições; premissas do credor em cenário base e de estresse (macro e micro). Nada para o produtor preencher |

**Repetição.** Os dois modelos pedem quase a mesma coisa, em formas diferentes. Dos 78 campos canônicos do mapa abaixo, **41 aparecem nas duas planilhas**, 27 só na completa e 10 só na simplificada. Unidades e séries diferem: R$ mil, R$ milhões ou R$; 10 safras ou 3. **Conclusão:** o dado é guardado uma vez, na unidade de base, e cada modelo é só uma forma de saída.

## Situação em 16/10 (conferida no código)

| Parte | Hoje |
|---|---|
| Entrada do Crédito (MOD-CRE) | 3 cartões, Contratos, Liberações e Dossiê, cada um abre uma visão da GE-08 (`ui37.MENU2`; `credito_menu_test.py`) |
| Solicitações e contratos | 4 linhas fixas: custeio com penhor, trator com alienação, barter com CPR física e armazém em rascunho. O formulário tem finalidade (texto), credor (3 opções), valor (R$ mil) e garantia (5 textos). Não tem moeda, parcelas, saldo, nem vínculo da garantia ao bem (`areas/gestao.py`, `_ge08`) |
| Comparar propostas | Mensagem fixa |
| Liberações | Etapas fixas; anexar certidão; a 2ª liberação fica bloqueada até a conferência |
| Dossiê e consentimento | 3 blocos fixos (Produção e áreas; Fluxo de caixa; Compromissos e garantias), com "Autorizado para", prazo e "Autorizar bloco". Nenhum dado vem dos módulos. Não há versão, pendência, documento nem modelo de credor |
| Botão primário da GE-08 | "Solicitar proposta a credores" abre a PT-04, que é a tela do credor: o produtor cai na visão do banco |
| Portal do credor (PT-04 e PT-04det, fora do menu) | Dossiês concedidos, histórico de acesso, blocos com fonte e validade, pedir complemento, condição precedente, contraproposta e recusa, tudo em texto fixo (`areas/parceiros.py`) |
| Cadastro de fazendas (CD-01) | CAR, matrícula e cartório, módulos fiscais, posse, arrendador, fim do contrato, custo da terra. "CAR em branco bloqueia só o crédito rural." Pela CAD-02 (frente CADASTROS-PADRAO), os documentos de crédito vão para o Crédito (DEC-1610-14) |
| Planilha de banco | Não há importação nem exportação |

## Referências (AGENTS §3.3), consultadas em 16/10/2026

| # | Fonte oficial | O que diz | Decisão |
|---|---|---|---|
| 1 | Banco Central, MCR 2-9: [Voto 82/2025–CMN, de 18/12/2025](https://normativos.bcb.gov.br/Votos/CMN/202582/Voto_do_CMN_82_2025.pdf). Manual vigente em [manuais.bcb.gov.br/app/manual/mcr/publico](https://manuais.bcb.gov.br/app/manual/mcr/publico); o endereço responde, mas o texto é carregado por JavaScript e não foi lido nesta sessão | O crédito rural exige a inscrição do imóvel no CAR (Lei 12.651, art. 78-A; Resolução CMN 4.487/2016). Pela resolução que acompanha o Voto, com vigência em 02/01/2026, o credor verifica supressão de vegetação após 31/07/2019 pelo PRODES a partir de 1º/04/2026 (imóvel com mais de 4 módulos fiscais) e de 04/01/2027 (até 4). Também verifica embargos e o cadastro de empregadores | **Adaptar.** O dossiê leva o CAR e os módulos fiscais de cada imóvel. Imóvel sem CAR em pedido de crédito rural vira pendência com o motivo legal. A verificação em si é do credor, e o sistema não a imita (descartar) |
| 2 | BNDES: [BNDES Crédito Rural](https://www.bndes.gov.br/wps/portal/site/home/financiamento/produto/bndes-credito-rural). MAPA: [Plano Safra 2026/2027](https://www.gov.br/agricultura/pt-br/assuntos/politica-agricola/plano-safra) | Linhas para investimento, máquinas, custeio, capital de giro e CPR-F/CDCA. "Procure uma instituição financeira credenciada [...] que informará a documentação necessária, analisará a possibilidade de concessão do crédito e negociará as garantias" | **Adotar.** Cada credor tem o próprio modelo sobre um núcleo comum, e a finalidade do pedido usa essas linhas |
| 3 | B3: [Cédula do Produto Rural (CPR)](https://www.b3.com.br/pt_br/produtos-e-servicos/registro/renda-fixa-e-valores-mobiliarios/cedula-do-produto-rural-cpr.htm). O texto da Lei 8.929/1994 no Planalto não respondeu em 16/10 | Desde 1º/01/2021, a CPR física ou financeira precisa ser registrada em entidade autorizada pelo Banco Central (Lei 13.986/2020). Há dispensa abaixo de certos valores quando o credor original não é instituição financeira (Resolução CMN 4.927/2021). A CPR financeira vem da Lei 10.200/2001 | **Adaptar.** A CPR do sistema ganha registradora, número e data do registro, e entra no dossiê como compromisso. O mesmo saco não garante dois contratos (regra já existente). Fazer o registro na registradora: **adiar** (contrato e custo) |
| 4 | Banco Central: [Resolução Conjunta nº 1/2020, compilada](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/51028/Res_Conj_0001_v4_P.pdf), arts. 10 e 15 | No Open Finance, o consentimento tem linguagem clara, finalidade determinada, prazo de até 12 meses, dados discriminados e identificação do cliente. É vedado o aceite pré-marcado ou presumido. Mudar finalidade, prazo ou dados exige novo consentimento. A revogação vale a qualquer tempo, de forma imediata e pelo mesmo canal | **Adaptar** como boa prática (o Safrion não é participante do Open Finance) para o consentimento do dossiê. Importar dívidas pelo Open Finance: **adiar** (P8) |
| 5 | Serasa Experian: [Agro Score](https://www.serasaexperian.com.br/solucoes/agro-score/) | Pontuação de 0 a 1.000 por CPF ou CNPJ, com dados cadastrais, demográficos e comportamento financeiro no mercado agrícola, usada pelo credor antes da concessão e no monitoramento da carteira | **Descartar** o score próprio. O bureau é consulta do credor; o dossiê entrega dados limpos e com origem, sem nota nem limite sugerido |

O PRD já cita a [Resolução CMN 4.883/2020](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?numero=4883&tipo=Resolu%C3%A7%C3%A3o+CMN) (S8, CET do crédito rural) para comparar propostas (CAL-19); nada muda nisso. Estar no mercado não prova a regra de domínio.

## Decisões dos agentes (delegação do proprietário)

1. **Uma Ficha do grupo e um dossiê por pedido.**
   - A **Ficha do grupo** guarda, uma vez, o que o sistema não sabe: pessoas, empresas, avaliações, contratos anteriores ao sistema, histórico de safras e atividades fora do sistema.
   - O **dossiê** junta a Ficha e os dados do sistema numa data-base, para uma finalidade e um ou mais credores. A finalidade pode ser "Análise de limite", sem pedido, ou um pedido do Crédito (custeio, investimento, máquinas, CPR, comercialização).
   - Os documentos de crédito (matrícula, CAR, CCIR, ITR, arrendamento, certidões, IR ou balanço) ficam na Ficha, por imóvel ou pessoa, com validade. Isso cumpre a DEC-1610-14 e a CAD-02: o cadastro de fazendas mostra só um aviso, "Documentos: N pendentes · abrir no Crédito".
   - *Dano evitado:* o mesmo dado digitado em dois lugares e com valores diferentes.
2. **Campo canônico, modelo do credor.**
   - O sistema guarda cada dado uma vez, em unidade de base: kg, ha, R$ em decimal, data.
   - Um **modelo** diz quais campos o credor exige, em que unidade, em que série de safras e em que célula. Começa com dois modelos sintéticos de mesma estrutura das planilhas recebidas: o **completo** (10 safras, R$ mil, mil sacas) e o **simplificado** (3 safras, R$ milhões).
   - O mapeamento de cada modelo é curado por nós e versionado. O usuário não monta coluna.
   - Credor sem modelo usa o **dossiê padrão** (todos os blocos).
   - *Dano evitado:* o banco receber números numa unidade que ele lê em outra (R$ mil lidos como R$ milhões).
3. **O sistema primeiro; o usuário só digita o que falta.**
   - Montar o dossiê pede 3 coisas, todas de um toque: para quem (credor do CD-05 com o papel Parceiro de crédito, ou "ainda não sei"), para quê (finalidade e valor opcional) e a data-base (hoje, ou os atalhos "fim do mês anterior", "30/06" e "31/12").
   - O resto vem do mapa campo → fonte (abaixo). O que falta vira **pendência**, com a pergunta curta, o campo tipado (número com unidade, data com atalho, lista de um toque), o motivo ("exigido pelo modelo completo") e o tempo estimado.
   - A resposta grava na Ficha e vale para todos os dossiês.
   - **Dado com validade** (valor de terra e de máquinas, câmbio, saldo de aplicação) volta como "Confirmar ou atualizar"; se não mudou, basta um toque.
   - **Nunca valor herdado** para papel no pedido (tomador, avalista, anuente) nem para autorização (AGENTS §3.3).
4. **Origem em cada número.** Cada campo mostra uma marca:
   - **Sistema:** registrado com documento de origem, com link para a tela de origem;
   - **Calculado:** fórmula visível, sempre a do serviço de domínio existente (ENG-011), sem fórmula nova;
   - **Declarado:** quem informou, quando, com que fonte (laudo, referência de mercado ou estimativa) e até quando vale.
   - Campo de sistema não se edita no dossiê: o link abre a origem.
   - *Dano evitado:* o banco tratar estimativa como fato registrado, e o produtor corrigir o número no lugar errado.
5. **Safras pela data-base.** A safra de referência é o ano-safra que contém a data-base (virada em setembro), como nos dois modelos e na safra do sistema (1º/09 a 31/08).
   - **Safras com dado no sistema:** área e cultura do Planejar safra; produtividade pela meta ou pela previsão V2 na safra aberta, e pela colheita ÷ área na encerrada; custo pelo orçamento V2 ou pelo realizado.
   - **Safras anteriores ao sistema:** histórico declarado uma vez por safra e cultura (área, produtividade, preço, custo).
   - **Safras futuras:** o plano atual repetido, com premissa de crescimento por cultura (área e produtividade), declarada uma vez e marcada "Projeção".
6. **Unidades, moeda e preço.**
   - **Conversão na saída:** cada célula do modelo declara o fator, por exemplo sc = kg ÷ massa da saca da cultura (CULTURA_UN), mil sc = sc ÷ 1.000, R$ mil = R$ ÷ 1.000. Arredondamento só na saída.
   - **Saca com massa ambígua** (50 ou 60 kg, `fatAmb`) fica pendente, nunca palpite.
   - **Moeda no pedido e no contrato:** pedido de venda e contrato de crédito ganham o campo moeda (FO-19 e FO-20 já o preveem). Sem câmbio informado, o campo em US$ fica pendente, nunca 0.
   - **Fórmulas do modelo:** o dossiê preenche só as células de entrada. As fórmulas do credor (por exemplo, o preço médio final ponderado pelo câmbio) ficam intactas.
   - **Preço onde o modelo pede entrada:** na safra encerrada, o preço médio realizado; na aberta, o preço médio ponderado entre os contratos e a referência de mercado no volume não fixado, com a premissa declarada; na futura, a referência, marcada "Projeção".
7. **Coerência: trava só onde protege algo concreto (AGENTS §4).**
   - **Trava a autorização:** garantias que somam mais de 100 % da produção prevista do mesmo produto e safra (penhor + CPR + barter).
     - *Dano evitado:* o mesmo saco garantir dois contratos, ou seja, dinheiro do credor sem lastro.
   - **Trava a autorização:** destinatário sem consentimento ativo.
     - *Dano evitado:* dado do grupo exposto sem autorização.
   - **Aviso:** área plantada maior que a área em produção dos imóveis; produtividade declarada no histórico diferente da colheita registrada (vale a registrada, e o aviso diz isso).
   - **Aviso forte:** imóvel sem CAR em pedido de crédito rural. Pela Lei 12.651, art. 78-A, o credor não pode conceder; a pendência diz isso, mas o envio não é bloqueado.
   - **Pendência obrigatória do modelo:** não bloqueia o envio. Ela vai ao credor como "a informar até <data>", à vista, nunca escondida nem preenchida com zero.
8. **Versão congelada.**
   - Autorizar o envio congela a versão: data-base, valores, origens, modelo e versão do mapeamento, mais o SHA-256 do conteúdo canônico.
   - Dado de origem que muda depois não altera a versão enviada. O dossiê mostra "Dados mudaram desde a v1 · Gerar v2", e a v2 lista as diferenças campo a campo.
   - Complemento pedido pelo credor gera a v2 da mesma forma.
   - *Dano evitado:* o banco analisar um número que mudou sem aviso.
9. **Consentimento e acesso** (RN-039, 57.4.2, referência 4).
   - **Cada envio registra:**
     - o destinatário: o credor e as pessoas convidadas dele;
     - a finalidade;
     - os blocos discriminados pelo modelo;
     - o prazo: padrão de 90 dias, teto de 12 meses;
     - quem autorizou, pela alçada "Autorizar dossiê de crédito" em Usuários e alçadas.
   - **Aceite ativo:** nenhuma caixa vem marcada. Mudar finalidade, blocos, prazo ou destinatário pede novo consentimento.
   - **Revogação imediata** na mesma tela. O credor guarda só a decisão já registrada (PT-04 de hoje).
   - **Link reaproveitado da ENTREGA-FAZ** (uma solução por problema): token por destinatário, finalidade e validade, revogável. Fora do dossiê concedido, a mensagem é "Este link não dá acesso a este dossiê", sem dado nenhum.
   - **Histórico de acesso:** quem, quando e qual bloco, igual para os dois lados.
10. **Lado do credor (PT-04det).**
    - O credor vê a versão concedida, a data-base e os blocos, com a origem de cada número, e as pendências "a informar".
    - Baixa no próprio modelo (planilha) ou o resumo (PDF).
    - "Pedir complemento" aponta o campo ou o documento e um prazo; isso vira pendência no dossiê do produtor.
    - Aprovação continua condicional e não é desembolso (PT-04 e FL-22 de hoje).
11. **Dados pessoais mínimos** (NFR-17).
    - Só os campos que o modelo do credor exige. Regime de casamento e data de nascimento só para tomador ou avalista; a pergunta explica o porquê: anuência do cônjuge em garantia real.
    - CPF mascarado em listagens e completo só no dossiê autorizado.
    - No protótipo, só a massa sintética de CPF e CNPJ com dígito válido do CD-05.
12. **Exportação no modelo.**
    - **Protótipo:** a planilha do modelo sintético é gerada pelo próprio sistema, com o mesmo escritor de ZIP do pacote de prescrição da SOLO-VRA (quem chegar primeiro cria; o outro reaproveita), mais o PDF de resumo.
    - O sistema relê a própria planilha e confere com conta independente.
    - **Arquivo do credor:** preencher o arquivo que o produtor recebeu do banco fica no software real (§Fora do escopo).

## Fluxo proposto

1. **Montar** (Dossiês › "Montar dossiê"): 3 perguntas de um toque. O sistema monta na hora e abre o detalhe com a faixa "N do sistema · M calculados · K declarados · P pendências".
2. **Completar** ("O que falta"): lista única de pendências, das obrigatórias pelo modelo às opcionais. Cada uma é respondida na própria linha, e a resposta vai para a Ficha.
3. **Conferir:** as verificações da decisão 7 aparecem antes de autorizar, com o número e o link da origem.
4. **Autorizar:** gaveta de consentimento (decisão 9). Congela a versão (decisão 8).
5. **Enviar:** link ao credor, mais a planilha no modelo e o PDF para anexar onde ele pedir. No protótipo, o envio é simulado: download e link de demonstração (P1).
6. **Acompanhar:** acessos, complementos (geram a v2), prazo, "Revogar acesso". O pedido segue para propostas, contrato e liberações, como hoje.

**Lado do credor:** abrir o link → ler os blocos com origem → baixar no modelo → aprovar, contrapropor, recusar ou pedir complemento (PT-04det).

## Telas (master-detail, uma primária por tela, DS do Agrícola; método da skill `padrao-safrion`, DEC-1610-12)

| Tela | Conteúdo | Primária (BOT-01) |
|---|---|---|
| Entrada do Crédito (MOD-CRE) | 4 cartões na ordem do processo: **Ficha do grupo** · **Dossiês** · **Pedidos e contratos** · **Liberações e garantias** | — (cartões) |
| Ficha do grupo (GE-08 `#vis=ficha`) | Grade comum (TAB-08) com uma linha por item. Seções: Pessoas · Imóveis e documentos · Bens e avaliações · Contratos anteriores ao sistema · Histórico de safras · Outras atividades. Colunas: item, situação (completo, falta, vence em), atualizado em e "usado em N dossiês". A linha abre o painel com o formulário curto | "Completar ficha" (abre a próxima pendência) |
| Dossiês (GE-08 `#vis=dossies`) | Uma linha por dossiê: número sintético (DOS-0001), finalidade e pedido, credor, modelo, data-base e versão, situação (Rascunho · N pendências, Pronto, Enviado · lido em, Complemento pedido, Expirado, Revogado), acesso até | "Montar dossiê" |
| Detalhe do dossiê (GE-08det, novo) | Cabeçalho: credor · modelo · data-base · versão · situação. Etapas (ETP-01, futura neutra): Montar → Completar → Autorizar → Enviar → Acompanhar. Faixa de origem. Tabela dos 7 blocos e dos documentos, com origem e situação. Seção "O que falta" com respostas na linha. Ações secundárias com ícone: baixar no modelo, baixar PDF, ver acessos, revogar | Muda com a etapa: "Responder pendências" → "Autorizar envio" → "Enviar ao credor" → "Gerar nova versão" |
| Bloco (painel lateral) | Cada campo com valor, unidade, origem (link, fórmula ou declarante e data) e destino no modelo. Campo declarado edita ali mesmo; campo de sistema abre a origem | "Salvar" (só no declarado) |
| Autorizar e enviar (gaveta) | Destinatário, finalidade, blocos exigidos pelo modelo (lista discriminada, sem caixa pré-marcada), prazo (90 dias; atalhos 30, 90, 180 dias e 12 meses), formatos, quem autoriza | "Autorizar e enviar" |
| Dossiê do credor (PT-04det, ajustado) | Versão concedida, blocos com origem, pendências "a informar", histórico de acesso | "Baixar no meu modelo" |
| Pedidos e contratos (GE-08 `#vis=contratos`) | Como hoje, mais moeda, parcelas e garantia vinculada ao bem (imóvel, máquina, safra ou pessoa). A primária deixa de abrir a PT-04 | "Novo pedido" |

**A 390 px:** a faixa de origem rola dentro dela; as pendências viram cartões em linha (VIS-06); alvos de 44 px; o teclado faz o fluxo todo.

## Mapa campo → fonte

**78 campos canônicos** (as 2 planilhas juntas, sem repetição; documentos à parte, por modelo):

| Origem | Campos | Observação |
|---|---|---|
| **Já existe** | 15 | Cultura, área, sistema, imóvel, CAR, estoque de produto, máquinas, contratos do Crédito, CPR e barter |
| **Derivável** | 29 | Produtividade, produção, preços, entregas, custos, áreas em produção e irrigada, caixa, recebíveis, fornecedores, saldo e cronograma da dívida |
| **Falta** | 34 | Detalhados abaixo |
| · uma vez, depois reaproveitado | 15 | Pessoas, CNPJ, endereço, histórico anterior ao sistema, ano de implantação dos perenes, contratos e dívidas anteriores ao sistema, máquinas (ano e dono), outros imóveis |
| · confirmar na data-base (1 toque se não mudou) | 8 | Câmbio, valor da terra, valor de máquinas e infraestrutura, aplicações, participações, área a abrir, despesas gerais, intenções de investimento |
| · por pedido | 1 | Papel de cada pessoa (tomador, avalista, anuente) |
| · só se houver | 8 | Pecuária e outras atividades fora do sistema, pasto, semoventes, arrendamento para terceiros, outros recebíveis, outras dívidas, retirada, preços de cana e boi |
| · até existir o campo moeda | 2 | Fixação em US$ e moeda da dívida |

Na série de safras, que é a maior parte das células (458 linhas × 10 safras na completa), quase tudo é **Já existe** ou **Derivável**. Digita-se só o histórico anterior ao sistema e as premissas de projeção.

| ID | Campo canônico | Planilha | Origem | Fonte no sistema ou pergunta |
|---|---|---|---|---|
| B1.01 | Nome do grupo | B | Já existe | nome da organização (onboarding) |
| B1.02 | Empresas do grupo: razão social e CNPJ | A | Falta · uma vez | nome já existe (Estrutura gerencial); CNPJ só é pedido na contratação |
| B1.03 | Pessoas do grupo: nome e CPF | A+B | Falta · uma vez | CD-04 é a equipe, não os sócios; reusa a validação de CPF do CD-05 |
| B1.04 | Vínculo ou grau de parentesco | A+B | Falta · uma vez | lista de um toque |
| B1.05 | Papel no pedido: tomador, avalista, anuente | B | Falta · por pedido | por pedido, sem valor herdado |
| B1.06 | Atua na atividade, função e tempo na atividade | A | Falta · uma vez | listas curtas |
| B1.07 | Data de nascimento | A | Falta · uma vez | só se o modelo exigir |
| B1.08 | Regime de casamento | A | Falta · uma vez | só para tomador ou avalista casado |
| B1.09 | Região de produção | B | Derivável | UF e municípios das fazendas (CD-01) |
| B1.10 | E-mails de contato | B | Já existe | e-mail do responsável da organização (onboarding) |
| B1.11 | Endereço para documentos | B | Falta · uma vez | uma vez |
| B1.12 | Data-base das informações | A+B | Derivável | data do congelamento da versão |
| B2.01 | Câmbio de referência (R$/US$) | A | Falta · confirmar na data-base | premissa com fonte e data |
| B2.02 | Preço de referência da soja (R$/sc) | A | Derivável | referência de mercado do Comercial, com fonte e data |
| B2.03 | Preço de referência da cana (R$/t) e do boi (R$/@) | A | Falta · só se houver | só com atividade declarada |
| B3.01 | Cultura | A+B | Já existe | cultivos do Planejar safra; Culturas (CD-02) |
| B3.02 | Época: 1ª, 2ª ou 3ª safra | A+B | Derivável | ordem do cultivo no talhão dentro da safra |
| B3.03 | Sistema: sequeiro ou irrigado | A+B | Já existe | sistema do talhão (pivô e gotejo = irrigado) |
| B3.04 | UF do bloco | A | Já existe | fazenda (CD-01) |
| B3.05 | Área plantada (ha) | A+B | Já existe | cultivos do Planejar safra |
| B3.06 | Produtividade (sc/ha) | A+B | Derivável | meta do plano ou previsão V2 na safra atual; colheita ÷ área nas encerradas |
| B3.07 | Produção total | A+B | Derivável | área × produtividade; colheita registrada nas encerradas |
| B3.08 | Volume e preço médio fixados em R$ | A | Derivável | Contratos e pedidos da safra (venda, CPR, barter) |
| B3.09 | Volume e preço médio fixados em US$ | A | Falta · até ter moeda | o pedido não tem moeda; vira derivável com o campo moeda (FO-19) |
| B3.10 | Preço médio final (R$/sc) | A+B | Derivável | média ponderada: fixado + referência no volume não fixado |
| B3.11 | Volume já entregue | A | Derivável | Expedição e entregas |
| B3.12 | Custo de produção (R$/ha) | A+B | Derivável | orçamento V2 dos planos; realizado em Custos nas encerradas |
| B3.13 | % do custo incorrido | A | Derivável | realizado ÷ V2 |
| B3.14 | Receita, custo total, resultado e margem | B | Derivável | cálculo |
| B3.15 | Observação de quebra de safra ou mudança de área | A | Derivável | sugerida quando o real difere da meta; texto opcional |
| B3.16 | Perenes: ano de implantação (idade, área em formação e em produção) | A+B | Falta · uma vez | uma vez por talhão perene |
| B3.17 | Perenes: renovação ou expansão (área e investimento) | A+B | Derivável | cultivo perene novo no Planejar safra + orçamento |
| B3.18 | Projeções das safras futuras | A+B | Derivável | plano atual + premissa de crescimento por cultura, digitada uma vez |
| B3.19 | Histórico anterior ao sistema | A+B | Falta · uma vez | uma vez por safra; ou importação da planilha antiga preenchida |
| B3.20 | Atividades fora do sistema (pecuária, suínos, leite, aves, eucalipto, cana, sementes, algodão beneficiado) | A+B | Falta · só se houver | bloco declarado, só se existir |
| B4.01 | Imóvel: nome, matrícula e cartório | A+B | Já existe | CD-01 (vai para a Ficha do grupo pela CAD-02) |
| B4.02 | CAR | A | Já existe | CD-01 |
| B4.03 | UF e município | A+B | Já existe | CD-01 |
| B4.04 | Área total | A+B | Já existe | CD-01 |
| B4.05 | Área em produção | A+B | Derivável | soma das áreas cultiváveis dos talhões ativos |
| B4.06 | Reserva legal e APP | A+B | Derivável | camada ambiental do CAR (CD-01); sem camada vira pergunta |
| B4.07 | Área de pasto | B | Falta · só se houver | fora do escopo do sistema |
| B4.08 | Área que ainda pode ser aberta | A | Falta · confirmar na data-base | sugestão calculada para confirmar |
| B4.09 | Área irrigada (própria e de terceiros) | A | Derivável | talhões com pivô ou gotejo |
| B4.10 | Valor da terra (R$/ha) | A | Falta · confirmar na data-base | com fonte e data; vale 12 meses |
| B4.11 | Área já dada em garantia, tipo e credor | A | Derivável | garantias do Crédito (vínculo bem ↔ contrato, novo) |
| B4.12 | Arrendada de terceiros: vencimento, área, unidade e custo/ha | A+B | Já existe | CD-01 (posse, fim do contrato, custo da terra) |
| B4.13 | Arrendamento: início do contrato | A | Falta · uma vez | uma vez por contrato |
| B4.14 | Custo total do arrendamento | A+B | Derivável | área × custo/ha |
| B4.15 | Área arrendada para terceiros | A | Falta · só se houver | uma vez por contrato |
| B5.01 | Caixa (saldo) | A+B | Derivável | contas da Gestão (GE-04, oculto no menu) |
| B5.02 | Aplicações: tipo, instituição, carência | A | Falta · confirmar na data-base | uma vez; saldo na data-base |
| B5.03 | Recebíveis de produto entregue (cliente, moeda, vencimento, safra) | A+B | Derivável | Contas a receber (GE-05, oculto) + entregas |
| B5.04 | Estoque de produto: produto, safra, unidade, quantidade | A+B | Já existe | Estoque de produto (lotes) |
| B5.05 | Valor do estoque de produto | B | Derivável | quantidade × preço contratado ou de referência |
| B5.06 | Insumos em estoque: valor, culturas, forma de pagamento | A+B | Derivável | Estoque × custo médio; reserva; condição da compra |
| B5.07 | Almoxarifado e outros | A | Derivável | estoque de peças e combustível |
| B5.08 | Semoventes | A+B | Falta · só se houver | fora do escopo do sistema |
| B5.09 | Máquinas: tipo, modelo e quantidade | B | Já existe | Máquinas, instalações e conjuntos (CD-03) |
| B5.10 | Máquinas: ano e proprietário | B | Falta · uma vez | uma vez por máquina |
| B5.11 | Máquinas e infraestrutura: valor de mercado | A+B | Falta · confirmar na data-base | com fonte e data; vale 12 meses |
| B5.12 | Capacidade estática de armazenagem | A | Derivável | capacidade dos silos (CD-03) |
| B5.13 | Outros imóveis e veículos particulares | A+B | Falta · uma vez | uma vez |
| B5.14 | Participações em outros negócios | A+B | Falta · confirmar na data-base | uma vez |
| B5.15 | Outros recebíveis (venda de terra, máquina ou outro ativo) | A+B | Falta · só se houver | uma vez por venda |
| B6.01 | Dívida bancária: credor, finalidade e taxa | A+B | Já existe | contratos do Crédito (GE-08) |
| B6.02 | Dívida bancária: moeda | A+B | Falta · até ter moeda | vira derivável com o campo moeda no contrato (FO-20) |
| B6.03 | Dívida bancária: saldo, vencimento final e cronograma anual | A+B | Derivável | parcelas do contrato e títulos em Contas a pagar |
| B6.04 | Contratos anteriores ao sistema: saldo e parcelas | A+B | Falta · uma vez | uma vez por contrato; depois o sistema mantém |
| B6.05 | Dívida de terras | A+B | Falta · uma vez | uma vez por contrato, no mesmo cadastro de contratos |
| B6.06 | Fornecedores a pagar: saldo por vencimento, moeda, cultura | A+B | Derivável | Contas a pagar (GE-04) |
| B6.07 | Barter e CPR: sacas devidas, contraparte, safra | A | Já existe | Contratos e pedidos (CPR e barter) |
| B6.08 | Outras dívidas | A+B | Falta · só se houver | uma vez |
| B6.09 | Despesas gerais e administrativas | A | Falta · confirmar na data-base | não há despesa administrativa no protótipo |
| B6.10 | Retirada da família | A | Falta · só se houver | opcional |
| B7.01 | Investimentos com pedido no Crédito | A+B | Derivável | solicitações de investimento (GE-08) |
| B7.02 | Demais intenções de investimento e fontes | A+B | Falta · confirmar na data-base | uma vez por intenção |
| B7.03 | Investimentos realizados até a data-base | A | Falta · uma vez | uma vez por investimento |

**Fontes ocultas no menu.** GE-04, GE-05 e GE-03 estão fora do menu, mas o dado existe no protótipo. No software real, enquanto essas telas não estiverem publicadas, o campo vira pergunta, marcada "Declarado".

## Aceite

| ID | Caso | Oráculo |
|---|---|---|
| C1 | Montar o dossiê do modelo completo para a Santa Rita, com data-base 16/10/2026 | A faixa mostra a contagem por origem, que bate com a contagem independente do teste sobre o mapa campo → fonte e os dados sintéticos. Campo "Já existe" ou "Derivável" com dado no sistema nunca aparece como pendência |
| C2 | Responder as pendências e montar o 2º dossiê, para outro credor e no modelo simplificado | Nada do que já foi respondido é pedido de novo. Só aparecem o que é por pedido (papel das pessoas) e o que é exclusivo do novo modelo. Contagem de campos digitados no teste: 0 redigitados |
| C3 | Unidades e preço | 300 ha × 60 sc/ha = 18.000 sc: "18,0" em mil sacas (completo), 18.000 sc (simplificado) e 1.080.000 kg na base. R$ 850.000 = "850" em R$ mil e "0,85" em R$ milhões. Preço médio de 10.000 sc a US$ 22 com câmbio 5,40 e 5.000 sc a R$ 130 = R$ 122,53/sc. Sem câmbio, o campo em US$ fica pendente, nunca 0. Saca de 50 ou 60 kg sem fonte fica pendente, nunca palpite |
| C4 | Safra de referência | Com data-base 16/10/2026, a referência é 2026/27. Completo: 2022/23 a 2025/26, depois 2026/27, depois 2027/28 a 2031/32. Simplificado: 2025/26, 2026/27 e 2027/28. Com data-base 15/08/2026, a referência é 2025/26 |
| C5 | Coerência | Penhor de 70 % mais CPR de 20.000 sc sobre a previsão V2 de 51.280 sc = 109 %: "Autorizar envio" bloqueia e mostra os contratos e o percentual. Área plantada maior que a área em produção: aviso com os dois números. Imóvel sem CAR em pedido de custeio rural: pendência com o motivo legal, sem bloquear o envio |
| C6 | Versão congelada | Depois do envio, mudar a meta no Planejar safra não altera a v1 (mesmo SHA-256). O detalhe mostra "Dados mudaram desde a v1"; a v2 lista as diferenças campo a campo |
| C7 | Consentimento | Sem autorização ativa, nada sai. Prazo acima de 12 meses é recusado. Nenhuma caixa vem marcada. Mudar finalidade, blocos, prazo ou destinatário pede novo consentimento. "Revogar acesso" corta o link na hora ("Este link não dá acesso a este dossiê", sem dado). O histórico de acesso é igual nos dois lados |
| C8 | Credor pede complemento | Vira pendência no dossiê do produtor, com campo, motivo e prazo. A resposta gera a v2; o credor vê a v2 e o que mudou |
| C9 | Planilha no modelo | Valores só nas células de entrada; fórmulas do modelo intactas; sem macro. Reler o arquivo devolve os mesmos valores, e os totais conferem com conta independente. O PDF traz a origem de cada número |
| C10 | Dados pessoais mínimos | Só os campos exigidos pelo modelo. CPF mascarado em listagens. Regime de casamento só para tomador ou avalista. A varredura do gerador não acha CPF ou CNPJ fora da massa sintética |
| C11 | Cliques e digitação (§3.3), medidos antes e depois | Do cartão Dossiês ao dossiê montado: até 5 cliques. Digitação = só as pendências aplicáveis à fazenda sintética. 2º dossiê: 0 campos redigitados. Antes: nenhum dado montado; cada planilha seria preenchida à mão |
| C12 | 390 px e teclado | Sem rolagem lateral; pendências respondidas só pelo teclado; alvos de 44 px no toque |
| C13 | Entrada do Crédito | 4 cartões, na ordem Ficha do grupo · Dossiês · Pedidos e contratos · Liberações e garantias; cada um abre só a sua parte, com "‹ Crédito" |
| C14 | Persona certa | Nenhuma ação do produtor abre o portal do credor. A primária de Pedidos e contratos não aponta mais para a PT-04 |

**Contraprova:** a versão de b93e06f (3 blocos fixos, sem dados) reprova C1 a C9, C13 e C14; o `credito_menu_test.py` de hoje espera 3 cartões. Os modelos dos testes são sintéticos e gerados pelo próprio teste, com a mesma estrutura de células; os arquivos recebidos do proprietário não entram no repositório. Os aceites são propostos; viram teste depois da revisão do Codex sobre esta versão.

## Fora do escopo (com condição de retorno)

| Item | Volta quando |
|---|---|
| Preencher o arquivo .xlsx que o produtor recebeu do credor | Software real, no servidor: leitura sem macro, reconhecimento do modelo pela estrutura e mapeamento curado por versão do modelo. P2 decidida |
| Importar a planilha antiga já preenchida para semear o histórico | Software real, com P3 autorizada (dado real do cliente) |
| Score, rating ou limite sugerido pelo sistema | Descartado (referência 5); volta só por pedido do proprietário |
| Verificação de PRODES, embargos e listas restritivas | É do credor (MCR 2-9); volta se o proprietário quiser um autodiagnóstico antes do envio, com fonte oficial integrada |
| Dívidas bancárias pelo Open Finance; câmbio automático; bureau | P8 autorizada (contrato, custo e papel regulatório) |
| Registro da CPR na registradora e assinatura eletrônica | Contrato com registradora ou plataforma de assinatura autorizado (custo) |
| Pecuária, suínos, leite, aves e eucalipto como módulos | Decisão de escopo do proprietário; até lá, bloco declarado (P7) |
| Cenários de estresse macro | São do credor (aba oculta do modelo); voltam se pedidos |
| Envio real a banco ou fundo | Aceite do proprietário na homologação (AGENTS §2; P1) |

## Decisões só do proprietário (com recomendação)

| ID | Pergunta | Recomendação | Até decidir |
|---|---|---|---|
| P1 | Enviar o dossiê de verdade ao banco ou fundo (link e e-mail)? | Só depois do seu aceite na homologação, por e-mail transacional e link, como na ENTREGA-FAZ | Envio simulado: download e link de demonstração |
| P2 | O sistema pode preencher a própria planilha que o banco manda (o arquivo recebido pelo produtor)? | Sim, só com o arquivo enviado pelo produtor. Não guardamos nem distribuímos a planilha do banco; o mapeamento é nosso e versionado | Só os modelos sintéticos e o dossiê padrão |
| P3 | Importar a planilha antiga preenchida (dado real) para não digitar o histórico? | Sim no software real, com consentimento do produtor e prévia antes de gravar | Histórico digitado; no protótipo, só dados sintéticos |
| P4 | Prazo padrão de acesso do credor | 90 dias, renovável, com teto de 12 meses | 90 dias, marcado "a confirmar" |
| P5 | Quem pode autorizar o envio do dossiê? | Você, ou quem você designar na alçada "Autorizar dossiê de crédito" | Só a Direção, como no protótipo de hoje |
| P6 | Valor de terra e de máquinas: basta o valor declarado com fonte e data, ou exige laudo? | Declarado com fonte e data, marcado "Declarado"; laudo opcional anexado | Declarado |
| P7 | Atividades fora do sistema (pecuária, suínos, leite, aves, eucalipto) | Só declaradas no dossiê, sem módulo novo | Bloco declarado |
| P8 | Integrações pagas ou contratuais: Open Finance, registradora de CPR, bureau, câmbio automático | Adiar; estimar o custo antes de qualquer contratação | Digitado com fonte |
