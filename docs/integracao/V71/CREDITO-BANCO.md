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
  - três datas por dossiê: a data-base (referência econômica), a apuração e a emissão; versão emitida não muda;
  - nada sai sem consentimento preso à versão, com finalidade, destinatário, pessoas, blocos e prazo;
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
Autor / revisor / integrador: Claude / Codex (produto e QA) e Gemini (pelo conector do Codex) / Codex (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: claude/v44-v69-mapa em b93e06f / areas/gestao.py (_ge08 e GE-08det novo), areas/parceiros.py (pt04, pt04det), ui37.py (Crédito no MENU2 e CURTO37), dados_credito.py (novo: modelos sintéticos e mapa campo → fonte), credito.js (novo: montagem, unidades, coerência, versão e consentimento), credito_menu_test.py (atualizado), cre_dossie_unit.js e cre_dossie_test.py (novos)
Aceite e comando de verificação: C1–C20 abaixo / node cre_dossie_unit.js; python3 -B cre_dossie_test.py; python3 -B credito_menu_test.py; mais pttest.py e getest.py
Estado / impedimento / próximo passo: especificado, sem código; revisado pelo Codex e pelo Gemini em 16/10 (§Revisão), achados tratados nesta versão; entra quando uma das frentes abertas entrar na versão publicada (§3.6); depende da CAD-02 (documentos de crédito saem do Cadastro) e usa o mesmo modelo de link da ENTREGA-FAZ, com escopo e token próprios
```

## Revisão (Codex e Gemini)

- **Peso das propostas abaixo:** são do autor e valem depois dos aceites (§3). Cada achado foi aceito, ajustado ou recusado com fundamento.
- **O Codex executou:**
  - contagem independente do mapa: 78 IDs únicos (15 já existem, 29 deriváveis, 34 faltam; 41 nas duas planilhas, 27 só na A, 10 só na B);
  - as contas de C3 e C5 em Decimal.
- **Limites desta revisão:**
  - o Codex não conferiu as planilhas originais nem as enviou ao Gemini;
  - a varredura de sigilo do Claude (executada: valores das duas planilhas comparados com o texto, saída só com coordenadas) não equivale a inspeção independente;
  - ninguém executou produto, XLSX, portal ou navegador. Todos os aceites continuam especificados.

| Revisor | SHA-256 do texto revisado | Data | Parecer |
|---|---|---|---|
| Codex | `0a667ac8b888168e6afd1a423f6806274f9cbba6ae12a3e0134b8f4db78be440` (c9ccbcf, 334 linhas) | 16/10/2026 | Direção aceita: ficha canônica → dossiê por destinatário, com os ajustes 1–8 abaixo. Comentário 6219532066 no PR #47 |
| Gemini (conector do Codex) | o mesmo texto; requisição com SHA-256 `7c9ca16c21833d2921c0cbe75c2d4fccecea700fb00b32445046a9ea77e1616c` | 16/10/2026, 16:01:11Z | Modelo `gemini-3.1-pro-preview`, esforço HIGH; resposta `SErSao6vNP-Zn_AP4vfzqAc`, fim STOP, 19.682 tokens. Uma consulta, com o texto sintético inteiro, sem ferramentas, fontes externas nem testes. Brutos com o Codex em `work/dupla-20261013/cre-banco-20261016/` |

**Tratamento dos achados** (esta versão; os testes e as contraprovas continuam especificados, não executados):

| # | Achado (sev.) | Tratamento |
|---|---|---|
| 1 | Uma "data-base" só misturava a referência econômica, a apuração e a emissão; montar em outubro com data-base 30/06 usaria saldos de outubro (S2) | **Aceito.** Três datas. Corte temporal por campo, com fonte identificada, pelo histórico de eventos: estoque, títulos, dívida, preço e câmbio. Saldo atual filtrado por data não serve. Sem histórico, o campo vira pendência ou declaração datada. Data local, fuso e competência preservados. Propostas 5 e 8, B1.12, C3 e C15 |
| 2 | Consentimento e versão soltos: a v2 do complemento substituía a v1, o link reaproveitava o da ENTREGA-FAZ, a revogação prometia demais (S2) | **Aceito.** Consentimento preso à versão exata, ao credor, à finalidade, às pessoas e aos blocos. Complemento gera v2 em rascunho privado; publicar a v2 pede nova prévia e nova autorização, e a v1 fica intacta. O link segue o mesmo modelo, com escopo e token próprios. Revogar corta acessos futuros e não apaga cópias baixadas, e a tela diz isso. Acessos e downloads observados ficam registrados. Propostas 8 e 9, C7 a C10 |
| 3 | A trava de 100 % escondia a exposição real (S2) | **Ajustado.** O PRD não aprova trava de 100 %: aprova obrigação única sem dupla contagem (RN-029, VE-05, AC-52, DEMO-10), a validação "garantia já onerada" na nova garantia (FO-20) e a revisão dos compromissos afetados quando a previsão cai (FL-16). O dossiê mostra o comprometimento real, mesmo acima de 100 %, com alerta e origem, sem trava. A trava fica na constituição de nova garantia (FO-20). CPR e barter da mesma obrigação contam uma vez. Proposta 7 e C5 |
| 4 | Modelo rígido sem regra para o que não cabe; validação da saída incompleta (S2) | **Aceito.** Nada é truncado e nenhuma linha é inserida às cegas: anexo só se o mapeamento do modelo o aceitar; senão, pendência de compatibilidade. Validação depois de exportar. Abas ocultas do credor não são copiadas; macros e vínculos externos não são executados. O modelo sintético não prova fidelidade às planilhas reais. Proposta 12, C9 e C16 |
| 5 | Custo e safra: orçamento, realizado, pago e projeção confundidos; safra do relatório sobrepondo o ciclo (S2) | **Aceito.** Orçamento aprovado, realizado por competência, pago e projeção atualizada ficam separados (PRD 51, CUSTO-09). O campo do credor segue a definição dele, sem troca silenciosa. A safra do modelo é convenção de relatório. Duas colheitas na mesma área somam área cultivada sem duplicar a área física. B3.12, B3.13, proposta 5, C17 e C18 |
| 6 | Valoração e área: a confirmação apagava a origem; "área que pode ser aberta" saía de subtração | **Aceito.** A confirmação guarda a fonte, o responsável e a data originais e registra a revalidação à parte. Tipo do valor: mercado, contábil ou declarado. A tela mostra a idade e se o valor serve para a data-base. Nenhum prazo inventado. B4.08 vem de documento competente ou fica "desconhecido". Proposta 3, B4.08, B4.10, B5.11 e C19 |
| 7 | Referências: Open Finance em versão antiga; Voto CMN tratado como norma | **Aceito.** A Resolução Conjunta 1 vigente (v8) pede prazo compatível com a finalidade, sem teto geral de 12 meses (Res. Conjunta 7/2023). Os 90 dias e o teto de 12 meses passam a ser política proposta do Safrion. O Voto 82/2025 é proposta: os alertas de CAR e PRODES ficam "a conferir antes de codificar". O sistema não infere concessão de crédito nem regularidade ambiental pelo cadastro. Referências 1 e 4, propostas 7 e 9 |
| 8 | UX e escopo: etapas como telas, modelo desconhecido compartilhando tudo, perguntas já decididas | **Aceito.** Listagem → detalhe com estado, destinatário, versão e uma primária. Pendências respondidas no contexto, com rascunho e foco preservados. "Autorizar e enviar" é uma ação só, com prévia e recibo. Modelo desconhecido gera rascunho sem nenhum bloco marcado. GE-04 e GE-05 continuam sintéticas, e a permissão do protótipo não prova o servidor. P4 a P7 viram propostas dos agentes; P1, P2, P3 e P8 esperam a autorização concreta. Telas, proposta 2, C11 e C20 |
| G1 | Gemini: exportar "37 maiores + Outros" quando não cabe | **Recusado.** Taxa, vencimento, credor e garantia não se somam sem aceite do esquema pelo credor |
| G2 | Gemini: "o sistema não deve policiar risco" | **Não adotado como regra geral.** Vale só para o dossiê, que expõe o que existe; as travas aprovadas para novas vinculações continuam (FO-20, RN-029) |
| G3 | Gemini: revalidar valores a cada 6 meses, com redigitação obrigatória e redutor por depreciação | **Recusado.** Não são regras aprovadas, e depreciação contábil não prova valor de mercado |
| G4 | Gemini: tratar pagamento como custo realizado | **Recusado.** Pagamento não é custo; o realizado é por competência (PRD 51) |

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
| 1 | Banco Central, MCR 2-9: [Voto 82/2025–CMN, de 18/12/2025](https://normativos.bcb.gov.br/Votos/CMN/202582/Voto_do_CMN_82_2025.pdf). Manual vigente em [manuais.bcb.gov.br/app/manual/mcr/publico](https://manuais.bcb.gov.br/app/manual/mcr/publico); o endereço responde, mas o texto é carregado por JavaScript e não foi lido nesta sessão | O Voto é **proposta**, com minuta de resolução sem número nem data; não é a norma promulgada. Ele cita a exigência de CAR para o crédito rural (Lei 12.651, art. 78-A; Resolução CMN 4.487/2016) e propõe a verificação de supressão de vegetação pelo PRODES, de embargos e do cadastro de empregadores. A busca de 16/10 achou notas oficiais citando resoluções posteriores, com prazos escalonados diferentes; os textos não foram lidos | **Adaptar, a conferir antes de codificar.** O dossiê leva o CAR e os módulos fiscais de cada imóvel. Os alertas de CAR e PRODES só entram no código com a norma ou o MCR vigente, com datas e escopo conferidos. O sistema não infere concessão de crédito nem regularidade ambiental pelo cadastro. A verificação em si é do credor (descartar a imitação) |
| 2 | BNDES: [BNDES Crédito Rural](https://www.bndes.gov.br/wps/portal/site/home/financiamento/produto/bndes-credito-rural). MAPA: [Plano Safra 2026/2027](https://www.gov.br/agricultura/pt-br/assuntos/politica-agricola/plano-safra) | Linhas para investimento, máquinas, custeio, capital de giro e CPR-F/CDCA. "Procure uma instituição financeira credenciada [...] que informará a documentação necessária, analisará a possibilidade de concessão do crédito e negociará as garantias" | **Adotar.** Cada credor tem o próprio modelo sobre um núcleo comum, e a finalidade do pedido usa essas linhas |
| 3 | B3: [Cédula do Produto Rural (CPR)](https://www.b3.com.br/pt_br/produtos-e-servicos/registro/renda-fixa-e-valores-mobiliarios/cedula-do-produto-rural-cpr.htm). O texto da Lei 8.929/1994 no Planalto não respondeu em 16/10 | Desde 1º/01/2021, a CPR física ou financeira precisa ser registrada em entidade autorizada pelo Banco Central (Lei 13.986/2020). Há dispensa abaixo de certos valores quando o credor original não é instituição financeira (Resolução CMN 4.927/2021). A CPR financeira vem da Lei 10.200/2001 | **Adaptar.** A CPR do sistema ganha registradora, número e data do registro, e entra no dossiê como compromisso, contada uma vez (RN-029). Fazer o registro na registradora: **adiar** (contrato e custo) |
| 4 | Banco Central: [Resolução Conjunta nº 1/2020, texto compilado v8](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/51028/Res_Conj_0001_v8_P.pdf), arts. 10 e 15 (lido pelo Codex e pelo Claude em 16/10; a v4 citada antes estava desatualizada) | No Open Finance, o consentimento tem linguagem clara, finalidade determinada, **prazo compatível com a finalidade** (art. 10, § 1º, III, pela Res. Conjunta 7/2023, sem o antigo teto geral de 12 meses), dados discriminados e identificação do cliente. É vedado o aceite pré-marcado ou presumido. Mudar a instituição transmissora pede novo consentimento; mudar finalidade, prazo ou dados pede informação específica e concordância ativa (§§ 2º, 7º e 8º). A revogação vale a qualquer tempo, de forma imediata e pelo mesmo canal (art. 15) | **Adaptar** como boa prática para o consentimento do dossiê, sem enquadrar o Safrion como participante do Open Finance. Os 90 dias e o teto de 12 meses são **política proposta do Safrion**, não limite regulatório. Importar dívidas pelo Open Finance: **adiar** (P8) |
| 5 | Serasa Experian: [Agro Score](https://www.serasaexperian.com.br/solucoes/agro-score/) | Pontuação de 0 a 1.000 por CPF ou CNPJ, com dados cadastrais, demográficos e comportamento financeiro no mercado agrícola, usada pelo credor antes da concessão e no monitoramento da carteira | **Descartar** o score próprio. O bureau é consulta do credor; o dossiê entrega dados limpos e com origem, sem nota nem limite sugerido |

O PRD já cita a [Resolução CMN 4.883/2020](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?numero=4883&tipo=Resolu%C3%A7%C3%A3o+CMN) (S8, CET do crédito rural) para comparar propostas (CAL-19); nada muda nisso. Estar no mercado não prova a regra de domínio.

## Propostas (Claude; valem depois dos aceites)

1. **Uma Ficha do grupo e um dossiê por destinatário.**
   - A **Ficha do grupo** guarda, uma vez, o que o sistema não sabe: pessoas, empresas, avaliações, contratos anteriores ao sistema, histórico de safras e atividades fora do sistema.
   - O **dossiê** junta a Ficha e os dados do sistema numa data-base, para uma finalidade e um credor. A finalidade pode ser "Análise de limite", sem pedido, ou um pedido do Crédito (custeio, investimento, máquinas, CPR, comercialização). Dois credores são dois dossiês, cada um com o seu consentimento.
   - Os documentos de crédito (matrícula, CAR, CCIR, ITR, arrendamento, certidões, IR ou balanço) ficam na Ficha, por imóvel ou pessoa, com a validade do próprio documento. Isso cumpre a DEC-1610-14 e a CAD-02: o cadastro de fazendas mostra só um aviso, "Documentos: N pendentes · abrir no Crédito".
   - *Dano evitado:* o mesmo dado digitado em dois lugares e com valores diferentes.
2. **Campo canônico, modelo do credor.**
   - O sistema guarda cada dado uma vez, em unidade de base: kg, ha, R$ em decimal, data.
   - Um **modelo** diz quais campos o credor exige, com a definição de cada um, em que unidade, em que série de safras e em que célula. Começa com dois modelos sintéticos de mesma estrutura das planilhas recebidas: o **completo** (10 safras, R$ mil, mil sacas) e o **simplificado** (3 safras, R$ milhões).
   - O mapeamento de cada modelo é curado por nós e versionado. O usuário não monta coluna. Campo do sistema com definição diferente da do credor não é trocado em silêncio: o mapeamento declara qual medida vai (proposta 5) ou o campo fica pendente.
   - **Credor sem modelo:** gera rascunho no **dossiê padrão**, mas nenhum bloco vai marcado. A pessoa escolhe os blocos na autorização.
   - *Dano evitado:* o banco receber números numa unidade ou definição que ele lê em outra (R$ mil lidos como R$ milhões; orçamento lido como realizado).
3. **O sistema primeiro; o usuário só digita o que falta.**
   - Montar o dossiê pede 3 coisas, todas de um toque: para quem (credor do CD-05 com o papel Parceiro de crédito, ou "ainda não sei"), para quê (finalidade e valor opcional) e a data-base (hoje, ou os atalhos "fim do mês anterior", "30/06" e "31/12").
   - O resto vem do mapa campo → fonte (abaixo). O que falta vira **pendência**, com a pergunta curta, o campo tipado (número com unidade, data com atalho, lista de um toque), o motivo ("exigido pelo modelo completo") e o tempo estimado.
   - A resposta grava na Ficha e vale para todos os dossiês. Responder fica no contexto: o rascunho se guarda sozinho e o foco volta à próxima pendência.
   - **Valor declarado** guarda o tipo (avaliação de mercado, valor contábil ou declaração do produtor), a fonte, o responsável e a data original.
   - **Confirmar um valor** registra a revalidação à parte (quem e quando), sem apagar a fonte, o responsável e a data originais.
   - **Idade do dado:** a tela mostra a idade e se o valor serve para a data-base do dossiê. A validade é a que o próprio registro já tem (do documento ou da exigência do modelo do credor). Nenhum prazo novo é criado.
   - **Nunca valor herdado** para papel no pedido (tomador, avalista, anuente) nem para autorização (AGENTS §3.3).
4. **Origem em cada número.** Cada campo mostra uma marca:
   - **Sistema:** registrado com documento de origem, com link para a tela de origem;
   - **Calculado:** fórmula visível, sempre a do serviço de domínio existente (ENG-011), sem fórmula nova;
   - **Declarado:** quem informou, quando, com que fonte e de que tipo.
   - Campo de sistema não se edita no dossiê: o link abre a origem.
   - *Dano evitado:* o banco tratar estimativa como fato registrado, e o produtor corrigir o número no lugar errado.
5. **Três datas, corte temporal por campo e safras.**
   - **Datas do dossiê:**
     - **data-base:** a referência econômica, escolhida na montagem;
     - **apuração:** quando o sistema extraiu os dados;
     - **emissão:** quando a versão foi congelada na autorização.
   - **Corte na data-base:** cada campo é apurado pelo histórico de eventos da sua fonte até a data-base, nunca pelo saldo atual filtrado por data:
     - estoque: movimentos até a data-base;
     - títulos e recebíveis: emitidos até a data-base e ainda não liquidados nela;
     - dívida: parcelas, liberações e pagamentos até a data-base;
     - custo realizado: por competência;
     - preço e câmbio: a cotação vigente na data-base, com fonte e data.
   - **Sem histórico na fonte:** um campo de cadastro sem vigência ou um saldo guardado só como atual vira pendência ("informar o saldo em 30/06/2026") ou declaração datada. Nunca recebe o valor de hoje.
   - **Data local da fazenda:** o corte usa o fuso do CD-01 e a competência registrada na fonte. Um evento às 23h30 de 30/06 em Rio Verde (UTC−3) entra no corte de 30/06, mesmo sendo 01/07 em UTC.
   - **Safra do relatório:** a safra de referência é o ano-safra que contém a data-base, com virada em setembro, como nos dois modelos. É convenção do modelo e não sobrescreve o ciclo agronômico. O cultivo entra na safra do relatório pela regra declarada no mapeamento; a regra proposta é a data de plantio.
   - **Área cultivada e área física:** duas colheitas nos mesmos 100 ha somam 200 ha cultivados, uma linha por época, sem duplicar a área física de 100 ha. Isso não gera erro.
   - **Safras com dado no sistema:** área e cultura do Planejar safra; produtividade pela meta ou pela previsão V2 na safra aberta, e pela colheita ÷ área na encerrada.
   - **Custo por hectare: medidas separadas,** como no PRD 51 (CUSTO-09: realizado + estimativa para concluir = projeção final; o orçamento-base permanece):
     - orçamento aprovado (V2);
     - realizado por competência;
     - pago;
     - projeção atualizada (realizado + estimativa para concluir).
   - **Regras do custo:**
     - pagamento não é custo realizado;
     - "% do custo incorrido" = realizado ÷ projeção atualizada, com o V2 e o desvio à vista;
     - o campo do credor recebe a medida que a definição dele pede.
   - **Safras anteriores ao sistema:** histórico declarado uma vez por safra e cultura (área, produtividade, preço, custo).
   - **Safras futuras:** o plano atual repetido, com premissa de crescimento por cultura (área e produtividade), declarada uma vez e marcada "Projeção".
6. **Unidades, moeda e preço.**
   - **Conversão na saída:** cada célula do modelo declara o fator, por exemplo sc = kg ÷ massa da saca da cultura (CULTURA_UN), mil sc = sc ÷ 1.000, R$ mil = R$ ÷ 1.000. Contas em decimal, sem arredondar passos intermediários; arredondamento só na apresentação.
   - **Saca com massa ambígua** (50 ou 60 kg, `fatAmb`) fica pendente, nunca palpite.
   - **Moeda no pedido e no contrato:** pedido de venda e contrato de crédito ganham o campo moeda (FO-19 e FO-20 já o preveem). Sem câmbio da data-base, o campo em US$ fica pendente, nunca 0.
   - **Fórmulas do modelo:** o dossiê preenche só as células de entrada. As fórmulas do credor (por exemplo, o preço médio final ponderado pelo câmbio) ficam intactas.
   - **Preço onde o modelo pede entrada:** na safra encerrada, o preço médio realizado; na aberta, o preço médio ponderado entre os contratos e a referência de mercado no volume não fixado, com a premissa declarada; na futura, a referência, marcada "Projeção".
7. **Coerência: trava só onde protege algo concreto (AGENTS §4), conferida no PRD.**
   - **O PRD não aprova trava de 100 % sobre o dossiê.** O que ele aprova:
     - obrigação única, sem dupla contagem do mesmo compromisso físico (RN-029; VE-05: "Barter conta uma vez como obrigação física"; AC-52; DEMO-10);
     - a validação "garantia já onerada" ao constituir garantia (FO-20);
     - quando a previsão cai, recalcular e pedir revisão só dos compromissos afetados (FL-16: previsão de 100 para 80 com 70 comprometidos deixa até 10 a negociar).
     - O "O mesmo saco nunca garante dois contratos" do rodapé da GE-08 é texto do protótipo, não regra do PRD.
   - **Nova garantia (Pedidos e contratos):** continua a regra atual de nova vinculação. A FO-20 recusa garantia sobre produção já onerada além do que está livre, com o contrato e a quantidade.
     - *Dano evitado:* constituir garantia sem lastro.
   - **Dossiê, sem trava:** mostra o comprometimento real, mesmo acima de 100 % (por exemplo, depois de uma quebra de safra), com alerta, contratos e origem. Obrigação fora do sistema pode ser declarada, por quem tem a alçada, com alerta e origem.
     - *Dano evitado:* esconder do credor a exposição que já existe.
   - **Deduplicação:** CPR, barter e penhor que representam a mesma obrigação contam uma vez. O vínculo considera titular, safra, produto, saldo e garantia vinculada. Exemplo do protótipo: o CRE-0095 aparece no Crédito e em Contratos e pedidos e é uma obrigação só.
   - **Trava a autorização:** destinatário, versão, pessoas ou blocos sem consentimento ativo.
     - *Dano evitado:* dado do grupo exposto sem autorização.
   - **Aviso:**
     - área plantada numa mesma época maior que a área em produção dos imóveis (épocas diferentes somam sem aviso);
     - produtividade declarada no histórico diferente da colheita registrada (vale a registrada, e o aviso diz isso).
   - **CAR e PRODES, a conferir antes de codificar** (referência 1): o dossiê mostra se o recibo do CAR está no cadastro e os módulos fiscais. Não afirma regularidade ambiental nem elegibilidade ao crédito.
   - **Pendência obrigatória do modelo:** não bloqueia o envio. Ela vai ao credor como "a informar até <data>", à vista, nunca escondida nem preenchida com zero.
8. **Versão congelada e nova versão.**
   - Autorizar congela a versão:
     - as três datas;
     - valores e origens;
     - modelo e versão do mapeamento;
     - SHA-256 do conteúdo canônico.
   - O arquivo e o link servem exatamente essa versão.
   - **Dado de origem que muda depois** não altera a versão emitida. O dossiê mostra "Dados mudaram desde a v1 · Preparar v2".
   - **v2 em rascunho privado:** o complemento pedido pelo credor, ou a mudança de dado, gera a v2 como rascunho que só o grupo vê, com as diferenças campo a campo.
     - A v2 não substitui sozinha o arquivo nem o link da v1, mesmo com os mesmos blocos.
     - Publicar a v2 pede nova prévia e nova autorização (proposta 9).
   - *Dano evitado:* o banco analisar um número que mudou sem aviso, ou receber dado que ninguém autorizou.
9. **Consentimento e acesso** (RN-039, 57.4.2, referência 4).
   - **Preso à versão:** cada autorização vale para a versão exata (SHA-256) e registra:
     - o credor e as pessoas convidadas dele;
     - a finalidade;
     - as pessoas do grupo cujos dados estão incluídos;
     - os blocos discriminados;
     - o prazo;
     - quem autorizou, pela alçada "Autorizar dossiê de crédito" (CF-01; padrão: Direção).
   - **Novo consentimento:** mudar a versão, o credor, a finalidade, as pessoas, os blocos ou o prazo pede nova autorização.
   - **Prazo:** compatível com a finalidade. **Política proposta do Safrion**, não limite regulatório: padrão de 90 dias, renovável, com teto de 12 meses.
   - **Aceite ativo:** nenhuma caixa vem marcada.
   - **Link:** o mesmo modelo de link da ENTREGA-FAZ, com escopo e token próprios. É um token por destinatário e por versão, guardado por hash, com finalidade e validade, revogável.
     - O token de um não abre o outro.
     - Fora do concedido, a mensagem é "Este link não dá acesso a este dossiê", sem dado nenhum.
   - **Revogar:** corta os acessos futuros na hora.
     - Não apaga cópias já baixadas, e a tela diz isso antes e depois de revogar.
     - O sistema não promete o que o credor guarda.
   - **Histórico:** registra os acessos e downloads observados de fato (quem, quando, versão, bloco ou arquivo), igual para os dois lados.
10. **Lado do credor (PT-04det).**
    - O credor vê a versão concedida, as três datas e os blocos, com a origem de cada número, e as pendências "a informar".
    - Baixa no próprio modelo (planilha) ou o resumo (PDF). Cada download fica registrado com a versão.
    - "Pedir complemento" aponta o campo ou o documento e um prazo; isso vira pendência no dossiê do produtor. O credor continua vendo a v1 até a v2 ser autorizada.
    - Aprovação continua condicional e não é desembolso (PT-04 e FL-22 de hoje).
11. **Dados pessoais mínimos** (NFR-17).
    - Só os campos que o modelo do credor exige. Regime de casamento e data de nascimento só para tomador ou avalista; a pergunta explica o porquê: anuência do cônjuge em garantia real.
    - CPF mascarado em listagens e completo só no dossiê autorizado.
    - No protótipo, só a massa sintética de CPF e CNPJ com dígito válido do CD-05.
12. **Exportação no modelo.**
    - **Protótipo:** a planilha do modelo sintético é gerada pelo próprio sistema, com o mesmo escritor de ZIP do pacote de prescrição da SOLO-VRA (quem chegar primeiro cria; o outro reaproveita), mais o PDF de resumo. O arquivo leva a versão e o SHA-256.
    - **Quando o modelo não comporta tudo** (por exemplo, 45 dívidas para 38 linhas): nada é truncado, nenhuma linha é inserida num modelo rígido e nada é somado em "Outros".
      - **Com anexo aceito no mapeamento do modelo:** as 38 linhas vão ao modelo e as 7 restantes ao anexo, com os subtotais e o total geral conferidos lado a lado.
      - **Sem esse aceite:** a planilha desse modelo não é gerada, e fica a pendência de compatibilidade "o modelo comporta 38; há 45". O link e o PDF continuam com as 45.
    - **Validação depois de exportar:**
      - limites de linhas e colunas;
      - valores aceitos pelas listas do modelo (finalidade, moeda, unidade), com mapeamento explícito; valor sem correspondência vira pendência;
      - tipos e unidades;
      - células de fórmula intactas;
      - referências externas não seguidas;
      - resultados que o modelo calcula conferidos com conta independente. Sem motor de cálculo, ficam marcados "não conferido".
    - **Desconhecido não vira zero:** fica em branco e listado "a informar".
    - **Releitura:** o sistema relê a própria planilha e confere com conta independente. O modelo sintético não prova fidelidade às planilhas reais.
    - **Arquivo do credor:** preencher o arquivo que o produtor recebeu fica no software real (§Fora do escopo). Mesmo lá, sem copiar as abas ocultas de análise do credor e sem executar macros nem vínculos externos.

## Fluxo proposto

Os passos abaixo são estados de um mesmo detalhe, não telas obrigatórias.

1. **Montar** (Dossiês › "Montar dossiê"): 3 perguntas de um toque. O sistema monta na hora e abre o detalhe com as três datas e a faixa "N do sistema · M calculados · K declarados · P pendências".
2. **Completar** ("O que falta"): lista única de pendências, das obrigatórias pelo modelo às opcionais. Cada uma é respondida na própria linha, com rascunho guardado e foco preservado; a resposta vai para a Ficha. As verificações da proposta 7 aparecem na mesma lista, com o número e o link da origem.
3. **Autorizar e enviar:** uma ação só.
   - Abre a prévia exata da versão: blocos, pessoas, datas, alertas e arquivos.
   - Pede o consentimento (proposta 9) e congela a versão (proposta 8).
   - Devolve o recibo: versão, SHA-256, destinatário, prazo e quem autorizou.
   - No protótipo, o envio é simulado: download e link de demonstração (P1).
4. **Acompanhar:**
   - acessos e downloads observados;
   - complementos pedidos, que geram a v2 em rascunho;
   - prazo e "Revogar acesso".
   - O pedido segue para propostas, contrato e liberações, como hoje.

**Lado do credor:** abrir o link → ler os blocos com origem → baixar no modelo → aprovar, contrapropor, recusar ou pedir complemento (PT-04det).

## Telas (master-detail, uma primária por tela, DS do Agrícola; método da skill `padrao-safrion`, DEC-1610-12)

| Tela | Conteúdo | Primária (BOT-01) |
|---|---|---|
| Entrada do Crédito (MOD-CRE) | 4 cartões na ordem do processo: **Ficha do grupo** · **Dossiês** · **Pedidos e contratos** · **Liberações e garantias** | — (cartões) |
| Ficha do grupo (GE-08 `#vis=ficha`) | Grade comum (TAB-08) com uma linha por item. Seções: Pessoas · Imóveis e documentos · Bens e avaliações · Contratos anteriores ao sistema · Histórico de safras · Outras atividades. Colunas: item, situação (completo, falta), tipo e idade do valor, atualizado em e "usado em N dossiês". A linha abre o painel com o formulário curto | "Completar ficha" (abre a próxima pendência) |
| Dossiês (GE-08 `#vis=dossies`) | Uma linha por dossiê: número sintético (DOS-0001), destinatário, finalidade e pedido, modelo, data-base, versão, situação (Rascunho · N pendências, Pronto, Enviado · lido em, v2 em rascunho, Complemento pedido, Expirado, Revogado) e acesso até | "Montar dossiê" |
| Detalhe do dossiê (GE-08det, novo) | Cabeçalho: destinatário · modelo · data-base, apuração e emissão · versão · situação (chip). Faixa de origem. Tabela dos 7 blocos e dos documentos, com origem e situação. Seção "O que falta" com respostas na linha. Ações secundárias com ícone: baixar no modelo, baixar PDF, ver acessos e downloads, revogar | Uma por situação: "Responder pendências" (rascunho com pendência obrigatória) → "Autorizar e enviar" (pronto) → "Preparar v2" (dados mudaram ou complemento pedido) |
| Bloco (painel lateral) | Cada campo com valor, unidade, origem (link, fórmula ou declarante, tipo e data), data do corte e destino no modelo. Campo declarado edita ali mesmo; campo de sistema abre a origem | "Salvar" (só no declarado) |
| Autorizar e enviar (gaveta) | Prévia da versão; destinatário e pessoas convidadas; finalidade; pessoas do grupo incluídas; blocos (lista discriminada, nenhuma caixa marcada, inclusive no modelo desconhecido); prazo (padrão 90 dias; atalhos 30, 90, 180 dias e 12 meses, política do Safrion); formatos; quem autoriza; aviso "revogar corta acessos futuros, não apaga cópias já baixadas" | "Autorizar e enviar" (devolve o recibo) |
| Dossiê do credor (PT-04det, ajustado) | Versão concedida e as três datas, blocos com origem, pendências "a informar", complemento pedido e situação, histórico de acessos e downloads | "Baixar no meu modelo" |
| Pedidos e contratos (GE-08 `#vis=contratos`) | Como hoje, mais moeda, parcelas e garantia vinculada ao bem (imóvel, máquina, safra ou pessoa), com a validação "garantia já onerada" (FO-20). A primária deixa de abrir a PT-04 | "Novo pedido" |

**A 390 px:** a faixa de origem rola dentro dela; as pendências viram cartões em linha (VIS-06); alvos de 44 px; o teclado faz o fluxo todo.

## Mapa campo → fonte

**78 campos canônicos** (as 2 planilhas juntas, sem repetição; documentos à parte, por modelo):

| Origem | Campos | Observação |
|---|---|---|
| **Já existe** | 15 | Cultura, área, sistema, imóvel, CAR, estoque de produto, máquinas, contratos do Crédito, CPR e barter |
| **Derivável** | 29 | Produtividade, produção, preços, entregas, custos, áreas em produção e irrigada, caixa, recebíveis, fornecedores, saldo e cronograma da dívida |
| **Falta** | 34 | Detalhados abaixo |
| · uma vez, depois reaproveitado | 15 | Pessoas, CNPJ, endereço, histórico anterior ao sistema, ano de implantação dos perenes, contratos e dívidas anteriores ao sistema, máquinas (ano e dono), outros imóveis |
| · confirmar na data-base (a confirmação guarda fonte, responsável e data originais) | 8 | Câmbio, valor da terra, valor de máquinas e infraestrutura, aplicações, participações, área a abrir, despesas gerais, intenções de investimento |
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
| B1.12 | Datas do dossiê: data-base (referência econômica), apuração e emissão | A+B | Derivável | data-base escolhida na montagem; apuração e emissão gravadas pelo sistema (proposta 5) |
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
| B3.12 | Custo de produção (R$/ha) | A+B | Derivável | a medida que a definição do credor pede: orçamento aprovado (V2), realizado por competência ou projeção atualizada (PRD 51); pagamento não é custo |
| B3.13 | % do custo incorrido | A | Derivável | realizado por competência ÷ projeção atualizada (realizado + estimativa para concluir), com o V2 e o desvio à vista |
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
| B4.08 | Área que ainda pode ser aberta | A | Falta · confirmar na data-base | só de fonte ou documento ambiental competente; sem isso, "desconhecido" (nunca subtração no cadastro) |
| B4.09 | Área irrigada (própria e de terceiros) | A | Derivável | talhões com pivô ou gotejo |
| B4.10 | Valor da terra (R$/ha) | A | Falta · confirmar na data-base | tipo (mercado, contábil ou declarado), fonte, responsável e data; idade à vista |
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
| B5.11 | Máquinas e infraestrutura: valor de mercado | A+B | Falta · confirmar na data-base | tipo, fonte, responsável e data; depreciação contábil não é valor de mercado |
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

**Data-base passada.** As contagens acima valem para a data-base igual à da montagem. Todo campo Derivável é apurado na data-base pelo histórico da sua fonte (proposta 5). A fonte sem histórico naquela data vira pendência datada.

**Fontes ocultas no menu.** GE-04, GE-05 e GE-03 estão fora do menu; os campos que só existem na semente delas continuam sintéticos. No software real, enquanto essas telas não estiverem publicadas, o campo vira pergunta, marcada "Declarado". A permissão provada no protótipo não vale como prova do servidor.

## Aceite

| ID | Caso | Oráculo |
|---|---|---|
| C1 | Montar o dossiê do modelo completo para a Santa Rita, com data-base 16/10/2026 | A faixa mostra a contagem por origem, que bate com a contagem independente do teste sobre o mapa campo → fonte e os dados sintéticos. Campo "Já existe" ou "Derivável" com dado no sistema nunca aparece como pendência |
| C2 | Responder as pendências e montar o 2º dossiê, para outro credor e no modelo simplificado | Nada do que já foi respondido é pedido de novo. Só aparecem o que é por pedido (papel das pessoas) e o que é exclusivo do novo modelo. Contagem de campos digitados no teste: 0 redigitados |
| C3 | Unidades e preço, na data-base do dossiê | Em Decimal, sem arredondar passos intermediários: 300 ha × 60 sc/ha = 18.000 sc = 18 mil sc (completo) = 1.080.000 kg na base. R$ 850.000 = 850 em R$ mil = 0,85 em R$ milhões. Preço médio de 10.000 sc a US$ 22 com câmbio 5,40 e 5.000 sc a R$ 130 = 1.838.000 ÷ 15.000 = R$ 122,5333…/sc; a tela mostra 122,53 só na apresentação. Sem câmbio da data-base, o campo em US$ fica pendente, nunca 0. Saca de 50 ou 60 kg sem fonte fica pendente, nunca palpite |
| C4 | Safra de referência (convenção do modelo) | Com data-base 16/10/2026, a referência é 2026/27. Completo: 2022/23 a 2025/26, depois 2026/27, depois 2027/28 a 2031/32. Simplificado: 2025/26, 2026/27 e 2027/28. Com data-base 15/08/2026, a referência é 2025/26. O ciclo agronômico dos cultivos não muda |
| C5 | Garantias e coerência | **Exposição real:** penhor de 70 % (35.896 sc) mais CPR de 20.000 sc sobre a previsão V2 de 51.280 sc = 55.896 ÷ 51.280 = 109,001560 % (Decimal). O dossiê mostra o valor com alerta, contratos e origem; "Autorizar e enviar" **não** bloqueia. **Nova garantia:** penhor de mais 5.000 sc da soja 26/27 em Pedidos e contratos é recusado pela FO-20, porque o livre é max(0; 51.280 − 55.896) = 0. **Deduplicação:** penhor de 30 % (15.384 sc) mais a CPR CRE-0095 (6.900 sc), que aparece no Crédito e em Contratos e pedidos, dá 22.284 sc = 43,455538 %, nunca 29.184 sc = 56,911076 %. Os alertas de CAR e PRODES ficam sem teste até a norma vigente ser conferida (referência 1) |
| C6 | Versão congelada | Depois da emissão, mudar a meta no Planejar safra não altera a v1 (mesmo SHA-256, mesmo arquivo). O detalhe mostra "Dados mudaram desde a v1 · Preparar v2"; a v2 em rascunho lista as diferenças campo a campo |
| C7 | Consentimento e link | **Autorização:** sem autorização ativa, nada sai. Nenhuma caixa vem marcada. A autorização da v1 vale só para a v1, o credor, a finalidade, as pessoas, os blocos e o prazo registrados; mudar qualquer um pede nova autorização. **Prazo:** acima de 12 meses é recusado com o motivo "política do Safrion", nunca "norma". **Token:** o do dossiê não abre um pedido da ENTREGA-FAZ, e vice-versa; o da v1 não abre a v2. **Revogar:** o próximo acesso recebe "Este link não dá acesso a este dossiê", sem dado; a tela avisa antes e depois que cópias já baixadas não são apagadas. **Histórico:** registra cada acesso e download observado (quem, quando, versão, bloco ou arquivo), igual nos dois lados |
| C8 | Credor pede complemento | Vira pendência no dossiê do produtor, com campo, motivo e prazo. A resposta gera a v2 em rascunho privado. O credor continua vendo a v1, com o mesmo link, o mesmo arquivo e o mesmo SHA-256, mesmo com os blocos iguais. A v2 só chega a ele depois de nova prévia e de "Autorizar e enviar" |
| C9 | Planilha no modelo | Valores só nas células de entrada; células de fórmula iguais às do modelo; nenhuma macro ou vínculo externo executado; nenhuma aba além das do modelo. **Validação depois de exportar:** limites de linhas, valores aceitos pelas listas, tipos e unidades. Desconhecido fica em branco e listado "a informar", nunca 0. Reler o arquivo devolve os mesmos valores, e os totais conferem com conta independente. O arquivo leva versão e SHA-256, e o download fica registrado. O relatório do teste declara que o modelo sintético não prova fidelidade às planilhas reais |
| C10 | Dados pessoais mínimos | Só os campos exigidos pelo modelo. CPF mascarado em listagens. Regime de casamento só para tomador ou avalista. Incluir uma pessoa do grupo depois da autorização pede nova autorização. A varredura do gerador não acha CPF ou CNPJ fora da massa sintética |
| C11 | Cliques e digitação (§3.3), medidos antes e depois | Do cartão Dossiês ao dossiê montado: até 5 cliques. De "Pronto" ao recibo: 2 cliques ("Autorizar e enviar" e confirmar na prévia). Digitação = só as pendências aplicáveis à fazenda sintética. 2º dossiê: 0 campos redigitados. Antes: nenhum dado montado; cada planilha seria preenchida à mão |
| C12 | 390 px e teclado | Sem rolagem lateral; pendências respondidas só pelo teclado, com o foco voltando à próxima; alvos de 44 px no toque |
| C13 | Entrada do Crédito | 4 cartões, na ordem Ficha do grupo · Dossiês · Pedidos e contratos · Liberações e garantias; cada um abre só a sua parte, com "‹ Crédito" |
| C14 | Persona certa | Nenhuma ação do produtor abre o portal do credor. A primária de Pedidos e contratos não aponta mais para a PT-04 |
| C15 | Data-base passada: montar em 16/10/2026 com data-base 30/06/2026 (Santa Rita, Rio Verde, UTC−3; eventos sintéticos do teste) | **Datas:** o cabeçalho e o PDF mostram data-base 30/06/2026, apuração 16/10/2026 e emissão na autorização. **Estoque:** abertura de 2.305.200 kg em 05/03; saída de 240.000 kg em 30/06 às 23h30 local (01/07 02:30 UTC); saída de 600.000 kg em 05/08. Saldo na data-base = 2.065.200 kg = 34.420 sc, nunca 2.305.200 kg (corte em UTC) nem 1.465.200 kg (saldo de hoje). **Recebíveis:** títulos de R$ 120.000 (emitido 10/05, liquidado 15/07), R$ 50.000 (01/06, liquidado 20/06) e R$ 80.000 (emitido 10/08) dão R$ 120.000 em aberto em 30/06. **Câmbio** sem cotação de 30/06 e **aplicação** sem histórico viram pendências datadas ("informar em 30/06/2026"), nunca o valor de hoje |
| C16 | Modelo que não comporta tudo: 45 dívidas sintéticas, a i-ésima com saldo de R$ 1.000 × i | Total R$ 1.035.000. **Modelo completo (110 linhas):** leva as 45. **Simplificado (38 linhas), sem anexo aceito no mapeamento:** a planilha não é gerada, fica a pendência "o modelo comporta 38; há 45", e o link e o PDF trazem as 45 e o total. **Simplificado com anexo aceito** (modelo de teste): R$ 741.000 nas 38 linhas + R$ 294.000 no anexo = R$ 1.035.000, conferidos lado a lado. Nenhuma linha "Outros" e nenhuma linha inserida no modelo |
| C17 | Custo por hectare: V2 de R$ 5.000/ha; realizado por competência R$ 4.000/ha; estimativa para concluir R$ 2.000/ha; pago R$ 4.500/ha | Projeção atualizada = 4.000 + 2.000 = R$ 6.000/ha. % incorrido = 4.000 ÷ 6.000 = 66,666…%, mostrado 66,67 %; nunca 80 % (realizado ÷ V2). V2 de 5.000 continua à vista, com desvio de +R$ 1.000/ha (+20 %). O pago (4.500) não muda nenhum desses números. O campo do credor recebe a medida da definição dele, que aparece no bloco |
| C18 | Duas colheitas: talhão de 100 ha com soja na 1ª safra e milho na 2ª, na 2026/27 | Duas linhas por época, com 200 ha cultivados no total; área em produção dos imóveis = 100 ha; nenhum aviso nem erro. O aviso só aparece se a soma numa mesma época passar de 100 ha |
| C19 | Valoração e área a abrir | **Valor da terra:** declarado em 10/03/2026 por Ana, tipo "avaliação de mercado", fonte laudo. Confirmado por Carlos em 16/10/2026, mantém fonte, responsável e data originais, e a revalidação fica registrada à parte. Com data-base 30/06/2026, a tela mostra que o valor tem 112 dias na data-base (220 hoje). Avaliação com data posterior à data-base aparece marcada assim. Nenhum redutor automático, nenhum vencimento de 6 meses, nenhuma redigitação obrigatória. **B4.08:** sem documento ambiental, é "desconhecido", mesmo quando total − produção − reserva > 0 |
| C20 | Modelo desconhecido | Credor sem modelo gera rascunho no dossiê padrão. Na autorização, nenhum bloco vem marcado, e "Autorizar e enviar" fica indisponível, com o motivo, até a escolha de ao menos um bloco |

**Contas dos oráculos:** conferidas em Decimal, sem arredondar passos intermediários (executado pelo Claude em 16/10/2026 com `python3` e o módulo `decimal`; as de C3 e C5 também pelo Codex). C15 e C19 também conferidos com `datetime` (executado).

**Contraprova:** a versão de b93e06f (3 blocos fixos, sem dados) reprova os casos que exigem o dossiê (C1 a C11 e C15 a C20), mais C13 e C14; o `credito_menu_test.py` de hoje espera 3 cartões. Os modelos dos testes são sintéticos e gerados pelo próprio teste, com a mesma estrutura de células; os arquivos recebidos do proprietário não entram no repositório. Os campos que só existem na semente da GE-04 e da GE-05 continuam sintéticos, e a permissão provada no protótipo não vale como prova do servidor. Os aceites são propostos; viram teste depois do aceite desta versão pelo Codex.

## Fora do escopo (com condição de retorno)

| Item | Volta quando |
|---|---|
| Preencher o arquivo .xlsx que o produtor recebeu do credor | Software real, no servidor: leitura sem macro nem vínculo externo, reconhecimento do modelo pela estrutura e mapeamento curado por versão do modelo. P2 autorizada |
| Importar a planilha antiga já preenchida para semear o histórico | Software real, com P3 autorizada (dado real do cliente) |
| Score, rating ou limite sugerido pelo sistema | Descartado (referência 5); volta só por pedido do proprietário |
| Verificação de PRODES, embargos e listas restritivas | É do credor. Os alertas de CAR e PRODES ficam a conferir antes de codificar (referência 1). Volta se o proprietário quiser um autodiagnóstico antes do envio, com fonte oficial integrada |
| Dívidas bancárias pelo Open Finance; câmbio automático; bureau | P8 autorizada (contrato, custo e papel regulatório) |
| Registro da CPR na registradora e assinatura eletrônica | Contrato com registradora ou plataforma de assinatura autorizado (custo) |
| Pecuária, suínos, leite, aves e eucalipto como módulos | Pedido do proprietário; até lá, bloco declarado no dossiê |
| Cenários de estresse macro | São do credor (aba oculta do modelo); voltam se pedidos |
| Envio real a banco ou fundo | Aceite do proprietário na homologação (AGENTS §2; P1) |

## Decisões só do proprietário (no momento da autorização concreta)

Nenhuma pergunta nova agora. As quatro abaixo dependem de envio real, dado real ou custo, e só vão ao proprietário quando houver uma autorização concreta a pedir. As antigas P4 a P7 saíram, porque eram escolhas que os agentes decidem:
- prazo de acesso: política proposta de 90 dias, com teto de 12 meses (proposta 9);
- quem autoriza: alçada configurável no CF-01, com padrão Direção (proposta 9);
- valoração: tipo, fonte, responsável e data, com laudo opcional (proposta 3);
- atividades fora do sistema: só declaradas, sem módulo novo (Fora do escopo).

| ID | Pergunta | Recomendação | Até decidir |
|---|---|---|---|
| P1 | Enviar o dossiê de verdade ao banco ou fundo (link e e-mail)? | Só depois do aceite na homologação, por e-mail transacional e link, no mesmo modelo de link da ENTREGA-FAZ | Envio simulado: download e link de demonstração |
| P2 | O sistema pode preencher a própria planilha que o banco manda (o arquivo recebido pelo produtor)? | Sim, só com o arquivo enviado pelo produtor. Não guardamos nem distribuímos a planilha do banco; o mapeamento é nosso e versionado | Só os modelos sintéticos e o dossiê padrão |
| P3 | Importar a planilha antiga preenchida (dado real) para não digitar o histórico? | Sim no software real, com consentimento do produtor e prévia antes de gravar | Histórico digitado; no protótipo, só dados sintéticos |
| P8 | Integrações pagas ou contratuais: Open Finance, registradora de CPR, bureau, câmbio automático | Adiar; estimar o custo antes de qualquer contratação | Digitado com fonte |
