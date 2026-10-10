# Decisões tomadas por delegação (09/10/2026)

**Para:** Adrianus · **De:** Claude · **Data:** 09/10/2026, noite
**Autor:** Claude (este texto e o futuro PR de registro) · **Revisor e integrador:** Codex (DEC-0910-02)

## Estado após o retorno do Codex 6091153950

O Codex respondeu como co-decisor (recibo 6091153950), sobre as versões `077b8f4` e `17852bc` deste texto. É a revisão das decisões, não prova de execução nem aceite dos 130 assuntos. Todos os ajustes que ele pediu foram aplicados abaixo. Os IDs e a correspondência com as entradas DEC-0910-xx não mudaram.

| Estado | IDs | Entrada DEC-0910 |
|---|---|---|
| **Acordo** | A delegação (seção 1). O Codex recebeu a sua mensagem direta no canal dele: não há ratificação pendente na sua volta. | 03 |
| **Acordo do Codex, delimitado** (o limite está escrito em cada linha) | OPE-01, OPE-08, PRO-01, MAN-01, MAN-02, PLA-05, PLA-06, PLA-DS02, PLA-DS03, PLA-DS04, PLA-DS09, PLA-DS15, PRC-03 | 15, 18, 31, 24 (c), 29 (a), 38 (b), 39, 04 |
| **Acordo delimitado às fontes** (rastreabilidade, parâmetros e fontes com versão; **não** valida fórmula, norma, habilitação profissional nem leitura de lei ainda "a verificar") | AGR-06, AGR-08, AGR-09, IRR-01, IRR-02 (também com o ajuste abaixo), OPE-17, SUP-12, SUP-13, PRO-04, PRO-05 | 09, 10, 14, 33, 34, 22, 27, 28 (a), 32 (c, d) |
| **Ajuste do Codex aplicado** (o Codex confere o texto ajustado) | PRC-01, PRC-02, PRC-04, PRC-05, PRC-06, EXT-01, EXT-02, OPE-04, OPE-06, MAN-08, SUP-04, OPE-07, OPE-18, AGR-05, IRR-02, PLA-DS06, PLA-DS10, PLA-DS13 | 04, 05, 06, 07, 11, 13 (b), 16 (c, e), 17, 19 (d), 21 (b), 25 (a), 34, 39 |
| **Aguardando o Codex** | Todos os outros IDs. Silêncio não é aprovação. | as demais |

**O que os ajustes mudaram:**
- **Ordem (PRC-01, PRC-02).** A sequência segue risco e dependência. Continuam em curso, sem interrupção, a correção do Beneficiamento e a revisão da DOM. O Beneficiamento integrado **não está aceito**: o defeito S2 de origem de lote (Codex 6090699184) continua aberto. Nenhum trecho é publicado com risco impeditivo conhecido. Cada exigência vai para o ID que já existe, sem outra fila.
- **Registro (PRC-04).** As decisões entram agora no registro que já existe (`docs/DECISIONS.md`). Conforme o seu pedido direto de 09/10, citado pelo Codex, o PRD 3.12 só vem depois de todas as implantações atuais concluídas, com IDs, estados e provas conferidos. Nenhuma pendência é antecipada nem apagada.
- **Passagem ao software real (PRC-06).** Vale o FOCO-APLICACAO-REAL v2: primeiro, concluir todo o conjunto vigente do protótipo, com uma candidata completa que funcione e a validação e auditoria tripla; depois, transferir na ordem tela → domínio → banco → homologação. Uma frente revisada sozinha não libera a passagem. Saiu "defeitos graves corrigidos **ou** escritos como aceite": registrar um S2 não o resolve. O trabalho em curso da C2 (PRs #32 a #35) continua. Depois da passagem, o protótipo não ganha evolução paralela. A trava da aprovação do agrônomo (CMD-42) e as demais proteções da fatia real continuam.
- **Referências de mercado (PRC-05).** Reaproveitar as válidas que já existem e pesquisar só a lacuna concreta de módulo ainda não coberto, sem repetir cinco pesquisas a cada teste ou correção. Continua fora qualquer "acima do mercado" sem prova.
- **Custo (EXT-01, EXT-02).** Desenvolvimento, QA e homologação já estão autorizados: referência de US$ 30/mês antes de tributos e US$ 10/mês de GitHub Actions. Não pedimos de novo o que já foi concedido. Antes de dizer que algo está travado por login ou faturamento, conferimos o estado da conta e do projeto; se houver um ato que só o senhor pode fazer, registramos qual é e a prova. Os US$ 15 no Cloud Run são proposta nossa, não teto aprovado nem garantia de cobrança limitada. O trabalho que não depende da nuvem não para.
- **Abastecimento e conciliação (OPE-04, OPE-06, MAN-08).** Proximidade de volume, hora ou horímetro não prova que dois registros são o mesmo fato, e dois abastecimentos verdadeiros próximos não podem sumir. Só a mesma identidade junta sozinha (recibo, ou o segundo registro apontando o primeiro; o mesmo trecho do totalizador da bomba é leitura nossa, a confirmar pelo Codex, e até lá vai à conferência); os casos duvidosos vão à conferência, sem soma e sem junção silenciosa. Entre o limite absoluto e o percentual vale o maior, com testes de fronteira. Prazos e tolerâncias são parâmetros, não verdades universais.
- **Recebimento (SUP-04).** Saiu o 1 % como incerteza automática. A incerteza da balança só existe com origem técnica (instrumento, método e unidade) e não se confunde com a tolerância do contrato; sem esse dado, "a conferir". Divergência de nota ou contrato nunca é dispensada por incerteza presumida. Registrar o peso medido não autoriza pagamento.
- **Aplicação ainda em conferência (OPE-07, OPE-18).** Ela já protege: carência e reentrada valem de forma preventiva na área possivelmente afetada, à vista, até a apuração, sem inventar precisão. A correção guarda o histórico.
- **Validade dos dados (AGR-05).** "Nunca para a irrigação" vale só para a idade do dado e não passa por cima de segurança, equipamento, outorga ou permissão. As validades são parâmetros, não recomendação agronômica certificada.
- **Rede de captação (IRR-02).** Cada outorga limita o próprio ponto e o próprio ato. A rede física não autoriza somar outorgas independentes.
- **Design (PLA-DS06, PLA-DS10, PLA-DS13).** Cartões no celular só onde a tarefa ganha com eles. O índice de umidade é o NDMI do contrato C4 (não NDWI), sem diagnóstico nem comando de irrigação. Casas decimais pela unidade e pela regra, sem apagar dose pequena, área, massa ou conversão.
- **Fontes (AGR-06, AGR-08, AGR-09, IRR-01, OPE-17, SUP-12, SUP-13, PRO-04, PRO-05).** Referência candidata não vira regra certificada, e reverter uma decisão não tira uma proteção obrigatória.

**Continua com o senhor:** produção, dados reais, novos gastos ou contratações e efeitos externos fora da autorização concreta (a lista do Codex); e, por cautela nossa, a configuração de segurança e o seu aceite como usuário (seções 1 e 4).

**Estado do trabalho:**
- Escritas pelo Claude e revisadas por contraexemplo. A revisão achou 1 bloqueio e 10 ajustes; todos foram corrigidos neste texto. Depois, o retorno do Codex 6091153950 foi aplicado.
- No protótipo, as decisões valem como as decisões das frentes valem hoje: o Codex revisa sem bloquear. As linhas ajustadas valem com o ajuste.
- Na `main` e no software real, cada decisão só vale com o acordo escrito do Codex sobre ela.
- **Nada aqui é aprovação sua.** O senhor pode mudar qualquer linha; cada uma diz como reverter.
- **Nada foi alterado ainda** no protótipo nem na `main`. Nenhum teste foi rodado nesta etapa.

---

## 1. A delegação

**Texto literal** (seu chat com o Claude, 09/10/2026, à noite, entre cerca de 21:40 e 22:00 UTC; a hora exata vai no trecho anexado ao PR de registro):
> "voce e codex tomem todas deciões por mim, estarei fora."

No canal do Codex, o senhor escreveu diretamente a ele: "Vc e o claude tomem todas decisões por mim, sempre na melhor prática. Vou esta fora, quando voltar não quero nada parado" (trecho também citado no PR #47, comentário 6089857604). O Codex confirmou que recebeu essa mensagem no próprio canal (recibo 6091153950). A delegação chegou, portanto, direto aos dois agentes, cada um no seu canal.

Antes, no mesmo dia, o senhor escreveu:
- "Faça o merge entre voce e codex, nao quero trabalho pra mim";
- "quero tudo pronto hoje";
- e, sobre o parecer: "apenas me dê seu parecer sem mudar nada ainda".

**Como lemos.** O "sem mudar nada ainda" valia para o parecer. A delegação que veio depois nos permite decidir e executar o que está dentro dos limites abaixo. Esta é a nossa leitura, e o senhor pode corrigi-la.

**O que a delegação cobre:** produto, regras, desenho das telas, prioridade, escopo do protótipo e do software real, valores-padrão e parâmetros.

**O que ela não cobre** (fica com o senhor, sem bloquear o resto):
- novos gastos, contratações ou contas fora da autorização concreta (o orçamento já concedido para desenvolvimento, QA e homologação não é pedido de novo; EXT-01);
- usar dado real de cliente;
- integrar o ERP real e outros efeitos externos (mensagens reais, envio a terceiros) fora da autorização concreta;
- publicar para usuários reais e entrar em produção;
- mudar configuração de segurança;
- o seu aceite como usuário.

**Fato da fazenda não é decisão.** Um dado da realidade (por exemplo, a massa da saca escrita num contrato) vira um parâmetro com padrão seguro e a marca "a confirmar com o dado real".

**Como cada decisão foi tomada:**
- reversível ou por parâmetro, sempre que possível;
- com o dano que evita;
- com a regra, o PRD ou a norma em que se apoia (norma com item e "verificar vigência");
- com o padrão escolhido, o que muda no protótipo e no software real, e como reverter.

**Canal de cada agente.** Pelo AGENTS §2, autorização passada de um agente ao outro não vale como sua. Aqui não houve repasse: cada agente recebeu a delegação direto do senhor, no próprio canal. Por isso não há ratificação pendente na sua volta (acordo do Codex 6091153950). Mesmo assim:
- o Claude anexa no PR de registro o trecho literal do canal dele, com data e hora;
- o Claude é autor deste texto e do PR de registro; o Codex revisa e, depois do aceite dele, integra (DEC-0910-02);
- o que continua reservado ao senhor está na lista acima e na seção 4.

Nos registros (`docs/DECISIONS.md` agora e o PRD 3.12 depois de concluídas as implantações atuais), cada linha decidida leva a frase "decidido pelos agentes sob a delegação de 09/10, não é aprovação do proprietário".

---

## 2. Em resumo

- **130 assuntos levantados.** 114 foram decididos pelos agentes. 14 ficam aguardando o senhor, porque estão fora da delegação. Os outros 2 (EXT-01 e EXT-02) deixaram de aguardar o senhor com o retorno do Codex: o gasto de desenvolvimento, QA e homologação já foi autorizado, e o teto do Cloud Run é proposta nossa.
- **Três mudanças que mais protegem pessoas e lavoura:**
  1. A primeira fatia do software real que libera O.S. já nasce com a aprovação do agrônomo conferida. Nessa fatia, O.S. com agrotóxico fica de fora até existirem reentrada, receituário ligado à O.S. e autoria.
  2. Carência e reentrada passam a contar **pela área realmente tratada**. Isso inclui a lavoura anterior ainda em pé e a área tratada a mais que o conferente aceitou.
  3. No software real, outorga vencida "em renovação" só irriga com a regra do órgão conferida ou com documento do órgão que diga que ela continua valendo.
- **Ordem decidida** (por risco e dependência; PRC-01, PRC-02 e PRC-06):
  1. terminar o que está em curso: a correção do Beneficiamento (integrado, mas ainda não aceito) e a revisão da DOM;
  2. juntar as demais frentes prontas;
  3. encaixar as correções da mesma natureza em cada frente, logo depois da junção dela;
  4. abrir as frentes novas, uma por vez (3.1 a 3.4);
  5. com todo o conjunto do protótipo concluído, candidata completa e validação e auditoria tripla, passar ao software real: tela → domínio → banco → homologação.

### As seis perguntas que o parecer deixava para o senhor

| Pergunta do parecer | Como ficou | A confirmar |
|---|---|---|
| 1. Quem libera a O.S. já aprovada: PCP ou gestor? | PCP ou gestor, escolhido por fazenda. Quem tem os dois papéis confirma uma vez só, e o sistema grava dois registros (OPE-01). | Quem faz o papel de PCP na fazenda real. |
| 2. Os contratos de soja são em saca de 50 ou 60 kg? | Os quatro contratos do protótipo são de demonstração e ficam com 60 kg. No contrato real, a massa é obrigatória, sem valor pré-escolhido, e é lida do documento (PRO-01). | A massa escrita em cada contrato real. |
| 3. Com a outorga "em renovação", pode irrigar? | No protótipo: sim, com protocolo no prazo e não negado, rotulado como premissa. No software real: só com a regra do órgão conferida na implantação, ou com documento do órgão que diga que a outorga vale (IRR-01). | Com o jurídico: órgão, prazo do pedido e validade durante a análise. |
| 4. As camadas do Mapa voltam às 9 de 26/09? | Sim. Carência e Insumos viram filtros. Antes, conferimos se o corte "Solo e Colheita na Fase 2" foi um pedido seu mais novo; se foi, ele prevalece (PLA-01). | — |
| 5. Custo da terra e formação da lavoura perene? | Linha própria, fora do custo operacional e dentro do custo total. A formação entra como investimento, depreciado ao longo dos anos (SUP-12). | Com o contador. |
| 6. Alçada da manutenção e criticidade das máquinas? | Alçada própria da ordem de manutenção. No protótipo, os valores são de demonstração. No software real, tudo sobe ao nível mais alto até a fazenda publicar os valores (MAN-01). A criticidade é A, B ou C, pela consequência da falha (MAN-02). | Valores reais e a classe de cada máquina. |

---

## 3. Decisões por domínio

**Como ler:**
- "(revisada)" marca as decisões que a revisão por contraexemplo mudou;
- marcas do retorno do Codex 6091153950: "ajustada · Codex" (texto mudado pelo ajuste dele, que ele confere), "acordo delimitado · Codex" (acordo nos limites escritos na linha) e "acordo às fontes · Codex" (veja abaixo). Linha sem marca do Codex aguarda o Codex; silêncio não é aprovação;
- "acordo às fontes": o acordo vale para rastreabilidade, parâmetros e fontes com versão. Lei, norma, fórmula e habilitação citadas continuam "a verificar"; referência candidata não vira regra certificada;
- os acordos delimitados de PLA-05, PLA-06, PLA-DS02, PLA-DS03, PLA-DS04, PLA-DS09, PLA-DS15 e PRC-03 valem com: controles mantidos, estado verdadeiro na tela, vocabulário único, contexto e foco preservados, origem da demonstração à vista, aviso enquanto a ligação não existir, e nenhum texto "aprovado pelo proprietário";
- reverter uma decisão nunca tira uma proteção que a lei ou a segurança exigem;
- "Protótipo" e "Real" dizem onde cada mudança acontece;
- "Gravidade estimada pelo Claude" quer dizer que o Codex ainda vai confirmar a gravidade.

### 3.1 Agronomia e lei

| ID | Decisão | Padrão | Por quê (dano evitado · base) | O que muda | Como reverter |
|---|---|---|---|---|---|
| AGR-01 | Continua a aprovação do agrônomo O.S. por O.S., inclusive nas operações mecânicas. A pré-autorização por limites (PEND-01) não entra agora. Para a fila não atrasar roçada e cultivo, o agrônomo pode aprovar de uma vez várias O.S. que ele mesmo marcou e viu. | "Aprovar selecionadas" só para O.S. sem insumo, mostrando o resumo de cada uma e registrando a decisão por O.S. A PEND-01 volta à mesa se, no piloto, a O.S. mecânica esperar o agrônomo mais de 1 dia útil (mediana) ou perder a janela. | Evita operação fora do plano feita sem ninguém olhar (solo úmido, talhão errado) e evita a fila travando o campo. Base: seu pedido de 26/09. | Protótipo: nada agora; "Aprovar selecionadas" entra depois da frente 3.1. Real: aprovação em lote com um recibo por O.S., e medição do tempo de espera por tipo de operação. | Adotar a PEND-01 por decisão registrada. |
| AGR-02 | Gesso: no protótipo continua como demonstração rotulada. No software real, a sugestão nasce desligada e só liga com protocolo publicado pelo responsável técnico (fonte, região, método e casos de teste). Até lá, o laudo de 20 a 40 cm aparece, e o agrônomo inclui o gesso à mão. | Demonstração: gatilho Ca < 0,5 cmolc/dm³ ou m > 20 %; dose de 50 (anual) ou 75 (perene) × argila %. Real: desligado. O gesso nunca é derivado do calcário. | Evita dose errada no talhão inteiro (gasto alto e perda de magnésio e potássio) e uma conta apresentada como se fosse fonte científica. Base: PRD 70.4, DEC-08. Candidata: Embrapa Cerrados (Sousa e Lobato, 2004), a conferir capítulo, tabela e vigência. | Protótipo: só o rótulo ("protocolo a publicar pelo responsável técnico"). Real: uma regra única para o gesso, ligada por fazenda e cultura. | Desligar o gesso na regra; no real, revogar a versão do protocolo. |
| AGR-03 | A dose sugerida usa a tabela de recomendação escolhida pelo responsável técnico de cada fazenda. A escolha fica registrada com fonte, edição, tabela, cultura, extrator do laboratório e região. Sem tabela publicada, o software real não sugere dose: vale a dose do plano. | Referências candidatas por região: verificar se o estado tem comissão ou boletim próprio e qual a edição vigente. Cerrado (GO, MT, DF): Embrapa Cerrados, 2004. MG: 5ª Aproximação, 1999. SP: Boletim 100 do IAC, 2022. ES: Incaper, 2007. Laudo com extrator diferente do da tabela não gera sugestão. | Evita dose de outra região ou de outro método de laboratório: o mesmo número de fósforo quer dizer coisas diferentes em Mehlich e em resina. Base: seu desenho de 05/10 ("tabela regional decidida pela fazenda") e PRD cap. 33. | Protótipo: rótulo "Demonstração — tabela a escolher pela fazenda com o responsável técnico". Real: cadastro da tabela por fazenda e cultura, com casos de teste tirados da própria tabela. | Publicar nova versão da tabela. Desligar volta à dose do plano. |
| AGR-04 | Laudo por zona com taxa variável, leitura automática de laudo e propostas de corretivos na Compra ficam para o software real. Não se faz média das zonas. | O laudo por zona aparece, sem dose. O calcário aparece como "sem fornecedor homologado". | A média daria calcário a menos nas manchas ácidas e a mais nas já corrigidas. Três frentes novas agora atrasariam a junção das 13 prontas. A leitura automática tem custo, e isso é decisão sua. | Protótipo: nada. Real: depois das fatias de O.S., estoque e app, com prescrição por zona aprovada pelo agrônomo. | Trazer de volta ao protótipo por decisão registrada, depois do passo 1. |
| AGR-05 (ajustada · Codex) | Cada dado de campo tem validade por fonte, e fonte, idade e vencimento ficam sempre à vista. Dado vencido não impede o agrônomo de decidir: aparece "vencido" e deixa de alimentar sugestão automática. | Valores propostos, parâmetros por fazenda; não são recomendação agronômica certificada: sonda 24 h; clima 24 h; previsão 12 h; telemetria 15 min; vistoria de pragas 7 dias; satélite ou drone 10 dias; análise de solo 24 meses (12 em talhão irrigado); foliar só na safra e no estádio da coleta. A idade do dado, sozinha, nunca para a irrigação só com água. Isso não passa por cima de impedimento de segurança, de equipamento, de outorga ou de permissão. | Evita pulverizar pela vistoria de três semanas atrás ou adubar por laudo de quatro anos, sem encher a tela de alertas. Base: PRD 73.7.8. | Protótipo: nada novo; a Irrigação entra na frente 3.3. Real: tabela por fazenda com versão, e cada decisão grava a fonte e a idade do dado usado. | Publicar nova versão da tabela. |
| AGR-06 (revisada; acordo às fontes · Codex) | "Aplicação segura e legal" é a primeira frente nova, logo depois da junção das frentes prontas. A ordem é: família da operação, reentrada, ocorrências com destino, receituário ligado à O.S., sobra de calda e EPI. A autoria do receituário do MIP sai desta frente e vai para Configurações, junto com a AGR-08. | Reentrada: ao liberar, compara o início da janela da O.S. com "reentrada até"; ao iniciar, compara a hora atual. A exceção é a bula permitir entrar com EPI e a O.S. registrar o EPI. Família: Agrícola, Irrigação só com água, Manutenção ou Beneficiamento. A dispensa do agrônomo vale só para irrigação sem nenhum produto, decidida pela família e nunca pelo nome. Ocorrência de segurança vai ao gestor com "Pausar ordem", e a O.S. não encerra com ocorrência sem destino. | Evita pessoa no talhão tratado dentro do prazo (intoxicação); "Irrigação com ureia" passando sem agrônomo; deriva ou tontura sem ninguém tratar; aplicação sem receituário rastreável. Base: Lei 14.785/2023 e regulamento; NR-31, item 31.7 (verificar vigência). | Protótipo: depois do passo 1. Real: família, reentrada, autoria e receituário ligado são condição para a primeira fatia com O.S. de agrotóxico. | Trocar a ordem por decisão registrada. A reentrada só vira aviso se a lei e a bula permitirem. |
| AGR-07 | O plano e o ajuste por talhão passam a conferir bula, alvo, carência e unidade, com aviso na linha. A trava continua na liberação da O.S. Se a unidade da dose for diferente da unidade do lote, a emissão e a reserva travam. | Aviso no plano; trava na O.S.; trava de unidade sem conversão automática, salvo fator cadastrado para o item. | Evita comprar para dose fora da bula e só descobrir na liberação (ex.: inseticida a 0,30 L/ha com bula de 0,8 a 1,0 kg/ha). Evita 50 kg reservados num lote controlado em litros. Base: registro e bula no Agrofit. | Protótipo: na frente Outorga e Agrofit, depois da junção. Real: uma conferência legal única, que no plano avisa e na O.S. trava. | O aviso do plano pode virar trava; o fator de conversão libera o item. |
| AGR-08 (acordo às fontes · Codex) | A habilitação do agrônomo é conferida na hora de aprovar a O.S., emitir receituário e publicar plano, e não só ao dar o papel. Junto: só o agrônomo assina o receituário do MIP, e fica registrado quem publica o plano. | Cadastro com conselho e número (CREA, CRT ou outro), UF, e visto quando a UF for diferente da fazenda. A validade é a da certidão ou da conferência (parâmetro), com data e quem conferiu. Sem habilitação válida, a ação é recusada com o motivo. ART: aviso ao gestor, sem travar. Aprovação feita com habilitação válida continua válida depois. | Evita aprovação e receituário assinados por quem perdeu a habilitação. Base: Lei 14.785/2023; Lei 5.194/1966; Lei 6.496/1977; Lei 13.639/2018 (verificar vigência e o alcance de cada habilitação para o receituário). | Protótipo: frente Configurações, logo depois da junção dela. Real: conferida no servidor na mesma operação, sem consulta automática ao conselho. | Mudar os documentos aceitos ou a validade (parâmetro). A conferência no ato não se desliga enquanto a lei exigir habilitação para aprovar e receitar. |
| AGR-09 (acordo às fontes · Codex) | Fazenda arrendada com contrato vencido e em renovação continua operando, com aviso. Sai a trava que hoje impede até salvar o cadastro da fazenda. Só se trava abrir safra ou plantar cultura nova depois da data de saída, e só com o contrato marcado Encerrado. | Situação do contrato: Em renovação (protocolo e prazo de revisão de 90 dias), Renovado ou Encerrado. Sem situação informada, aparece só o aviso pedindo a informação. | Evita parar a fazenda por causa de uma data, quando a lei em regra garante a colheita e a preferência na renovação. Evita investir em terra que vai sair. Base: Estatuto da Terra, art. 95, e Decreto 59.566/1966 (verificar vigência). | Protótipo: o cadastro de fazendas deixa de recusar o salvar, e o aviso aparece na fazenda, no Planejar safra e na O.S. Real: contrato de posse com situação e versão. | Restaurar a trava ao salvar. |

### 3.2 Operação e O.S.

| ID | Decisão | Padrão | Por quê (dano evitado · base) | O que muda | Como reverter |
|---|---|---|---|---|---|
| OPE-01 (acordo delimitado · Codex) | Quem libera é escolhido por fazenda. Padrão: o PCP, e o gestor também pode. Quem tem os dois papéis (aprovar e liberar) confirma uma vez, e o sistema grava dois registros. A confirmação única diz, no próprio texto, que aprova e libera; no instante dela, versão, permissão e habilitação são conferidas de novo. Quem só libera depende de aprovação válida daquela versão. Nunca há sucesso pela metade incoerente: a tela mostra exatamente o que foi gravado, ou aprovada e liberada, com os dois recibos, ou aprovada e em A liberar, com o motivo à vista. | PCP ou gestor. Confirmação única só para quem tem os dois papéis. Dois recibos sempre. | Evita O.S. parada sem ninguém para liberar e liberação gravada em nome de quem não decidiu. Base: aprovar não libera; seu pedido de 01/10 (sem etapa de revisão a mais). Decide a PEND-OS-01 (ela só sai da tabela no PRD 3.12). | Protótipo: a alçada passa a "PCP ou gestor", e a demonstração mostra o Caio (PCP) liberando O.S. já aprovada. Real: duas ações, dois recibos, mesmo numa confirmação. | Trocar a alçada em Configurações. |
| OPE-02 | No celular sem sinal, o pacote de trabalho vale até 7 dias. Depois disso, há 30 dias para enviar sem duplicar, mais 30 de folga. A proteção contra duplicação fica guardada 90 dias. | 7 + 30 + 30 = 67 dias; guarda de 90 dias. | Evita apontamento lançado duas vezes e fato do campo recusado cedo demais. | Protótipo: rótulo "padrão decidido". Real: configuração inicial; o sistema recusa mudança que deixe a guarda menor que a soma. | Configurações, com versão. |
| OPE-03 | O envio recusado por chegar tarde vai a um dono: o PCP (ordem e apontamento), o almoxarife do local (estoque) ou o responsável pela integração (outro sistema). O dono tem 1 dia útil para assumir; depois, o gestor é avisado. Nada é reaplicado sozinho. | Esses donos; papel vago fica com o gestor. | Evita fato do campo parado sem dono, com estoque e custo errados. | Protótipo: dono visível. Real: configuração inicial. | Configurações. |
| OPE-04 (ajustada · Codex) | Tolerâncias iniciais de conciliação, usadas só entre registros que já são o mesmo fato pela identidade: mesmo recibo ou chave do comando, o segundo registro apontando o primeiro, ou o mesmo trecho do totalizador da bomba (este último é leitura nossa, a confirmar pelo Codex; até lá, vai à conferência). Dentro delas, fica um fato só, sem somar, e a origem de cada valor fica guardada. Acima delas, abre conferência. Proximidade de volume, hora ou horímetro não prova que é o mesmo fato: registros sem identidade comum nunca são somados nem juntados sozinhos; os parecidos vão à conferência como "possível repetição". | Valores propostos, parâmetros (não são verdades universais). Abastecimento: 2 L ou 2 %, vale o maior. Área: 0,5 ha ou 3 %, vale o maior. Horas: 0,2 h. Água: 5 %. Entrega: zero em embalagem fechada; 1 % a granel, só entre registros da mesma entrega (não é a incerteza da balança, SUP-04). Consumo: 3 %. Diferença igual ao limite fica dentro; acima dele, conferência. | Tolerância zero encheria a fila de arredondamentos; tolerância alta esconderia diferença real; juntar por proximidade apagaria um abastecimento verdadeiro. | Protótipo: testes de fronteira onde há conciliação: no limite; logo acima dele; no ponto em que o absoluto e o percentual se cruzam (100 L no abastecimento, cerca de 16,7 ha na área); dois registros legítimos próximos, com recibos diferentes, continuam dois. Real: configuração inicial, revista depois da primeira safra do piloto. | Configurações, por tipo. |
| OPE-05 | Uma nota de uma linha no PRD 72.3: o app não aceita área acima do saldo; quem fez a mais relata por ocorrência; registro de outro aparelho que passe do saldo não é descartado. | — | Evita o servidor descartar área realmente feita. | Protótipo: nada. Real: só texto no PRD. | Tirar a nota. |
| OPE-06 (ajustada · Codex) | Prazos e janelas de conciliação iguais para todas as fazendas, como parâmetros. A janela do abastecimento só aponta "possível repetição" (mesma máquina e mesmo ponto, dentro da janela e da diferença de medidor); ela nunca junta, soma ou apaga registro sozinha. Dois abastecimentos verdadeiros próximos não podem sumir: o primeiro aceito conta, e o outro fica em conferência, sem efeito no saldo confirmado e com a quantidade à vista, até alguém decidir. | Valores propostos: janela de 2 h; ±0,2 h no horímetro ou ±2 km no hodômetro, conforme o medidor da máquina, junto com a janela. "Aguardando original" e "aguardando entrega": 72 h. Caso de conferência: 2 dias úteis. Incerteza da hora do celular: 5 ou 30 min (PRD, PEND-09). | Prazo curto gera alerta falso; prazo longo deixa a O.S. aberta por semanas; janela usada como prova junta abastecimentos diferentes. | Protótipo: prazos lidos da configuração, sem número fixo no código. Testes de fronteira: 2 h exatas dentro da janela e 2 h e 1 min fora; ±0,2 h exato dentro; dois abastecimentos verdadeiros na janela, com recibos diferentes, continuam dois e aparecem na conferência. Real: configuração inicial. | Configurações. |
| OPE-07 (revisada; ajustada · Codex) | Quando o conferente aceita trabalho acima do autorizado ou fora da versão, quem aprovou aquela versão fica ciente. Vale para toda O.S. com aprovação, inclusive a mecânica; na irrigação só com água, fica ciente o PCP. Toda aplicação aceita, dentro ou acima do autorizado, conta pela área realmente tratada para carência e reentrada. Área aceita fora do receituário ou da versão abre ocorrência ao agrônomo. Nada é aprovado para trás. **Aplicação relatada e ainda em conferência já protege:** a proteção contra entrada e colheita não espera o aceite do fato. Até a apuração, carência e reentrada valem de forma preventiva na área possivelmente afetada (a autorizada mais a relatada; sem desenho, a parcela ou o talhão inteiro), com o rótulo "preventiva · em apuração", sem inventar precisão. A conferência acerta a área por um registro novo, que guarda o anterior. | Ciência sem trava. Carência e reentrada pela área real. Ocorrência quando a área fica fora do receituário. Proteção preventiva enquanto a aplicação está em conferência. | Evita o agrônomo não saber da área a mais e alguém colher ou entrar ali dentro do prazo, inclusive enquanto o fato ainda é conferido. Base: Lei 14.785/2023. | Protótipo: "ciente" na trilha da ordem e nas pendências do agrônomo. Real: o mesmo, mais o cálculo por área, inclusive o preventivo. | Limitar a ciência às O.S. com produto. A carência por área não se reverte. |
| OPE-08 (acordo delimitado · Codex) | Não se encerra a O.S. enquanto um celular que tem a ordem informou registros dela ainda não enviados. Celular perdido ou quebrado: o gestor usa "Encerrar sem o aparelho", que grava motivo, autor e trilha. Celular sem notícia: só aviso. O que chegar depois entra como correção ligada à ordem: nunca reescreve período já fechado e nunca se presume consumo zero para o que ficou no aparelho. | Trava só com pendência informada; saída do gestor com motivo. | Evita fechar com área ainda no celular e aplicar duas vezes no mesmo lugar. É a nossa leitura da sua DEC-2609-13 ("encerrar exige apontamentos enviados"), com a exceção do aparelho perdido e a garantia de que nada é descartado. | Protótipo: o app envia primeiro o resumo dos pendentes, e "Conferir e encerrar" recusa dizendo o nome do celular. Real: condição no encerramento. | Trocar a trava por aviso. |
| OPE-09 (revisada) | Duas correções na frente de domínio, como o incremento seguinte depois da junção dela. (1) Iniciar confere todos os produtos da versão aprovada: sem requisição, ou sem entrega para a carga, não inicia. (2) O volume de calda (L/ha) passa a fazer parte da versão aprovada, e painel, app e ficha usam uma conta só. | Dados sintéticos: 100 L/ha e tanque de 3.000 L. | Evita mistura sem o adjuvante. Evita preparar a 120 L/ha num pulverizador regulado para 100 (cerca de 17 % menos produto, com risco de resistência). Gravidade estimada pelo Claude. | Protótipo: frente de domínio, depois da junção. Real: uma conta única de cargas e conferência no servidor ao iniciar. | Reverter o commit. |
| OPE-10 | Na frente de demanda: (1) uso do plano com data passada e sem O.S. continua na compra como "Vencida · decidir", com duas saídas (emitir a O.S. ou retirar do plano com motivo); (2) a cobertura diz se vem do estoque ou do pedido; (3) a data de plantio sugerida nunca fica no passado. | Só o realizado tira um uso da compra. | Evita que MAP 51 t, glifosato 408 L e semente 10,6 t saiam da compra sem nenhuma O.S. Gravidade estimada pelo Claude. | Protótipo: a parte (1) entra antes da junção, porque é o próprio objetivo da frente; as partes (2) e (3) entram logo depois. Real: só fato realizado ou decisão registrada tira um uso do plano. | Reverter o commit. |
| OPE-11 | Cancelar O.S. sem execução devolve a reserva na hora. Se já houve entrega, a O.S. fica "Cancelamento pendente" até o material voltar ao almoxarifado ou ter destino com motivo. Enquanto isso, "Liberar" não aparece e não é aceito. | — | Evita 320 L de agrotóxico com o operador sem pendência em lugar nenhum. Gravidade estimada pelo Claude. | Protótipo: frente de suprimentos, junto com a "reserva que volta", com teste de que "Liberar" é recusado. Real: como o PRD já manda. | Reverter o commit. |
| OPE-12 | A frente "Planejamento confiável" vem depois da "Aplicação segura e legal". Ela cobre variedade do cadastro, versão do plano gravada no cultivo, estados da safra, conferência diária e custo por horas. No software real, essas regras valem desde a primeira fatia do Planejar safra. | O escopo é escrito no acordo curto e dividido em dois incrementos se passar de uma fatia testável de ponta a ponta. | Mais uma frente agora atrasaria a junção das prontas. Lei e saúde (reentrada, receituário) vêm antes. | Protótipo: as limitações conhecidas entram na mensagem de teste. | Antecipar a variedade do cadastro se o seu teste mostrar o erro. |
| OPE-13 | A tabela do Planejar safra mostra rendimento (ha/h) e custo R$/ha. Largura, velocidade, eficiência e custos ficam no formulário. Há aviso se a eficiência sair de 50 a 90 %. | — | Com 16 a 18 colunas, a tabela fica ilegível no celular. Eficiência irreal subestima horas e custo. Base: seu pedido de 05/10. | Protótipo: falta só o aviso. Real: PRD ajustado. | As colunas voltam na linha. |
| OPE-14 | O custo mês a mês fica só no Orçamento. No Planejar safra, aparece o total por cultura. | — | Duas telas calculando o mesmo custo acabariam divergindo. | Protótipo: conferir se o Orçamento mostra o mês. Real: aceite da fatia do Orçamento. | Desenho próprio no Planejar safra. |
| OPE-15 | Máquina e pessoa pertencem a uma fazenda. Quando atendem as duas, o cadastro marca "atende também", e a capacidade soma as safras das duas. | Sem a marca: só a própria fazenda. | Evita as duas fazendas parecerem com folga e atrasarem juntas, e evita alarme falso que leva a comprar máquina. | Protótipo: a tela diz quais recursos entraram na conta. Real: campo "fazendas atendidas". | Pôr ou tirar a marca. |
| OPE-16 | O talhão fica livre no próprio dia da colheita registrada, para plantar atrás da colhedora. Folga maior só gera aviso, nunca trava. | Folga de 0 dia, configurável. | Evita pendência falsa para quem planta no dia da colheita e perda de um dia de janela. | Protótipo: folga de 1 passa a 0 na etapa 2 do Planejar safra, depois da junção. Real: parâmetro por organização. | Voltar a 1 dia. |
| OPE-17 (acordo às fontes · Codex) | O talhão ganha "indisponível por período". Embargo ambiental e área arrendada a terceiro travam o planejamento e a liberação; pousio e reforma só avisam. Atividade exigida pelo órgão passa com o documento, mas a aprovação do agrônomo continua quando houver produto. O que for colhido em área embargada leva a restrição até a venda. | Trava para embargo e arrendado a terceiro; aviso para pousio e reforma. | Evita plantar, aplicar ou vender o que vem de área embargada (multa, crime ambiental, crédito) e programar insumo para área que está com outro. Base: Lei 9.605/1998, art. 72; Decreto 6.514/2008, arts. 16, 54 e 79 (verificar vigência). | Protótipo: na frente Planejamento confiável. Real: no planejamento, na liberação e no Comercial. | Pousio e reforma, tipo a tipo, em Configurações. A trava do embargo e do arrendado a terceiro não se desliga. |
| OPE-18 (revisada; ajustada · Codex) | (1) O ciclo da lavoura perene termina quando a O.S. de erradicação ou renovação é encerrada, na data e na área reais. (2) A safra 2025/26 continua "Encerrada", com "2 cultivos em campo" até a colheita. (3) Liberar a cultura seguinte sem a colheita da anterior registrada só avisa. Carência e reentrada contam por área e data, para qualquer lavoura em pé ali, inclusive a anterior. Se a O.S. da cultura seguinte leva produto, o agrônomo vê o aviso ao aprovar. (4) Como na OPE-07, a aplicação ainda em conferência já protege a colheita da anterior, de forma preventiva, até a apuração. | Aviso, não trava; carência por área. | Evita talhão ocupado para sempre, reescrever safra fechada e parar a safrinha por atraso de digitação. Evita colher a soja dentro da carência da dessecação feita para a safrinha. | Protótipo: etapa 2 do Planejar safra, com o teste "colheita da anterior recusada dentro da carência da dessecação". Real: ciclo com estado próprio e carência por área. | Parâmetro "exige área colhida", que pode virar trava. |

### 3.3 Suprimentos e custos

| ID | Decisão | Padrão | Por quê (dano evitado · base) | O que muda | Como reverter |
|---|---|---|---|---|---|
| SUP-01 | Ajuste de inventário e consumo acima da custódia: decide o gestor. O consumo coberto pela custódia pode ser aceito pelo almoxarife ou pelo gestor. Se quem decidiu também contou, a decisão vale, com a marca "revisão independente pendente" até outra pessoa revisar. | Exigir segunda pessoa acima de um valor: parâmetro desligado. | Evita desvio escondido por quem contou e ajustou sozinho, sem parar a fazenda que tem um gestor só. Decide a PEND-CTL-02 (ela só sai da tabela no PRD 3.12). | Protótipo: já está feito; só falta registrar. Real: a marca aparece no fechamento do período. | Mudar as alçadas. |
| SUP-02 | Uma só tabela de alçada para compra de insumo, peça e serviço, medida pelo valor total da compra. | Protótipo: até R$ 50 mil, até R$ 300 mil, acima disso Direção, rotulados "demonstração". Real: começa vazia; sem política publicada, a Direção aprova toda compra. | Evita compra alta aprovada por quem não pode, compra fatiada para caber na alçada e número de demonstração virando regra. | Protótipo: rótulo. Real: alçada por papel e valor, com versão. | Editar níveis e valores. |
| SUP-03 | Não há teto por O.S. O controle de dinheiro é o orçamento autorizado, conferido ao liberar. Estouro vira aviso. | — | Evita um limite que não age e uma segunda trava paralela ao orçamento. | Protótipo: sai o texto "R$ 80 mil" de Configurações. | Criar o teto como aviso. |
| SUP-04 (revisada; ajustada · Codex) | Vale a tolerância que o contrato ou o pedido declara por item; sem ela, 0 %. A incerteza de medição é outra coisa: só existe com origem técnica registrada para a balança ou o medidor (instrumento, classe ou certificado, método e unidade) e não é tolerância comercial. Sem esse dado conferido, fica "incerteza a conferir", e nenhuma diferença é dispensada por presunção. Dentro da incerteza conferida, o estoque entra pelo medido e não se abre caso de medição. Fora dela, ou sem ela, o excedente fica bloqueado até o comprador decidir, e a falta vira saldo a receber. Nota diferente do pedido ou do contrato abre divergência sempre. Registrar o peso ou o volume medido não autoriza pagamento nem aceite financeiro: o pagamento segue nota, contrato e alçada. | Contrato: 0 %. Incerteza: sem valor de fábrica; "a conferir" até a origem técnica ser registrada. O 1 % proposto antes foi retirado. | Evita pagar o que não foi comprado, dispensar divergência por uma incerteza presumida e tratar tolerância do contrato como erro de balança. Com a incerteza conferida, evita abrir caso de medição em toda carga de granel. Base: PRD 70.4, DEC-07 (±10 % não é padrão). | Protótipo: entra com a etapa "do pedido ao recebimento". Real: tolerância por item no contrato e incerteza por balança. | Preencher a tolerância no contrato. |
| SUP-05 | Lote em quarentena só sai com liberação do gestor e documento conforme o motivo: laudo (qualidade) ou registro de inspeção (avaria, embalagem, identificação). Lote vencido nunca volta. | — | Evita produto fora do padrão na lavoura. Evita "número de laudo" inventado para embalagem amassada. Base: Lei 10.711/2003, Lei 6.894/1980 e decretos (verificar). | Protótipo: motivo em lista curta, na frente de suprimentos. Real: o motivo e o documento ficam gravados. | Exigir laudo em todos os motivos. |
| SUP-06 | Prazos de reserva: planejamento até 3 dias depois do início previsto (14 dias sem data); execução, 2 dias de folga; manutenção, 7 dias; aviso 24 h antes. Ordem liberada, pausada ou com pacote no celular não perde a reserva. | — | Evita material preso a ordem parada e reserva sumindo de ordem que só espera a chuva. | Protótipo: nada (não tem validade de reserva). Real: configuração inicial. | Configurações. |
| SUP-07 | Até 2 renovações de reserva, de até 7 dias (3 na execução), com motivo. | — | Evita estoque preso sem fim. | Real: limite e aviso quando outra ordem tem falta do mesmo produto. | Configurações. |
| SUP-08 | Material levado ao campo sem retorno: o almoxarife resolve em 2 dias úteis. Ordem sem cobertura: 1 dia útil. Depois disso, só aviso. Nada é ajustado sozinho. | — | Evita material fora de controle e sem dono. | Real: fila com prazo. | Configurações. |
| SUP-09 | Sobra transferida direto de uma O.S. para outra reduz, no mesmo registro, a reserva da O.S. que recebe. | — | Evita reserva em dobro, falta falsa e compra do que já existe. | Real: tudo na mesma operação. | Um ponto da regra. |
| SUP-10 | Fechar o mês com celular sem enviar gera só aviso. O que chegar depois entra como ajuste do mês anterior, contado uma vez só. | — | Evita um aparelho perdido travar o fechamento. | Real. | Parâmetro de bloqueio. |
| SUP-11 | Ordem na frente de suprimentos: juntar SUP-1, 2a e 2b; lote elegível (só lote apto, da fazenda, válido até o fim da janela; o que vence primeiro sai primeiro, repartindo entre lotes); reserva que volta; produto errado no recebimento; peças da manutenção (1b); do pedido ao recebimento (SUP-3). | — | Evita defensivo vencido entregue, liberação recusada com estoque em dois lotes, insumo de uma fazenda indo para outra e produto errado entrando com o nome do comprado. Gravidade estimada pelo Claude. | Protótipo: cada passo com o seu teste. Real: as mesmas regras na regra única de reserva. | Reverter o commit. |
| SUP-12 (acordo às fontes · Codex) | O custo da terra fica numa linha própria, fora do custo operacional e dentro do custo total. Terra arrendada: o valor do contrato. Terra própria: só como "estimativa" na visão econômica. A formação da lavoura perene vai para "Formação" e volta como depreciação anual (a confirmar com o contador). A margem aparece nas duas leituras. | O contrato em sc/ha/ano é convertido pelo preço do pagamento efetivo; antes dele, por estimativa rotulada com fonte e data. | Evita comparar talhão arrendado e próprio como iguais, vender abaixo do custo total sem perceber e lançar a formação do café num ano só. | Protótipo: corrigir já o texto de ajuda que promete "entra no custo por hectare". Real: componente Terra separado. | É só a forma de mostrar. |
| SUP-13 (acordo às fontes · Codex) | Peça recondicionada entra no estoque pelo custo do recondicionamento, como item próprio "recondicionada". Entra a natureza "Serviços de terceiros". | — | Evita inflar o estoque, cobrar a mesma peça duas vezes e misturar peça nova com recondicionada. Base: CPC 16 (a conferir com o contador). | Protótipo: natureza nova no catálogo. | Parâmetro de política de custo. |
| SUP-14 | Reposição automática fica desligada; o sistema só sugere, com um toque. No software real, liga só por política publicada para cada item, e gera solicitação, nunca pedido. | — | Evita dinheiro comprometido sem decisão. | Protótipo: nada. | Publicar a política do item. |

### 3.4 Manutenção

| ID | Decisão | Padrão | Por quê (dano evitado · base) | O que muda | Como reverter |
|---|---|---|---|---|---|
| MAN-01 (revisada; acordo delimitado · Codex) | Quem aprova a ordem de manutenção é o responsável de manutenção. O valor tem alçada própria da manutenção. Serviço externo é aceito pelo responsável, ou por técnico habilitado designado por ele, depois do teste; o pagamento só sai com o aceite e com a nota conferida. Compra de balcão tem teto por ordem, somando todas as compras. Conflito com a produção: PCM e PCP resolvem dentro do limite técnico da máquina; fora dele, decide o gerente. Máquina bloqueada nunca vai ao campo, e nenhuma alçada a libera. Registrar um fato (serviço feito, compra de balcão) não vale como autorização para trás. | Protótipo: R$ 10 mil, R$ 100 mil, acima disso Direção, e balcão de R$ 2 mil, rotulados "demonstração". Real: sem valores publicados, a autorização sobe ao nível mais alto, e todo balcão aparece ao gerente como exceção, sem bloquear o registro. O pedido de compra ligado à ordem segue a alçada de compras (SUP-02) e mostra a autorização da ordem. | Evita reforma grande sem ninguém de fora ver o valor, balcão sem teto e pagamento de serviço que não passou no teste. | Protótipo: faixas próprias na ordem, com teste de R$ 9.999 × R$ 10.001. Real: alçada por tipo de documento; fica registrado que a regra antiga da especificação da manutenção (P7) foi substituída. | Publicar outra versão dos valores. |
| MAN-02 (acordo delimitado · Codex) | A criticidade passa a ser um campo da máquina (A, B ou C), com motivo, dado pelo responsável de manutenção e revisto a cada safra. Deixa de ser calculada pelo atraso. Máquina sem classe é tratada como A. As classes da demonstração são rotuladas "sintéticas", e nenhuma classe libera máquina bloqueada. | A: risco a pessoas ou ao ambiente, ou para operação de janela sem substituto. B: para a produção, mas há substituto. C: não para nada. Ordem da fila: bloqueada, classe, gravidade e data. | Evita a revisão vencida de um implemento sem importância passar na frente da bomba do pivô no período seco. | Protótipo: classes sintéticas, com o teste "C vencida fica atrás de A em dia". Real: campo com histórico. | Voltar a ordenar pelo atraso. |
| MAN-03 | O custo-hora da oficina não é inventado. No protótipo, R$ 320/h marcado como "hipótese". No real, a fazenda informa: custo mensal da oficina dividido pelas horas lançadas em ordens. Sem valor, aparece "a valorar" e o custo fica parcial. | — | Custo-hora chutado contamina o custo por máquina, a tarifa das operações e a alçada. | Protótipo: rótulo. | Nova versão do parâmetro. |
| MAN-04 | Controle de pneus fica para depois. Pneu entra como peça, e recapagem como serviço. O tema volta se houver frota de estrada ou se pneu estiver entre os três maiores custos. | — | Evita digitação pneu a pneu sem retorno. | Nada. | Abrir a frente. |
| MAN-05 | A peça fica presa à ordem desde a aprovação com valor autorizado. Peça comprada para a ordem fica com ela. Peça livre vai para a máquina de classe mais alta. A entrega só acontece depois da liberação. A reserva vale até o fim da janela mais 7 dias. | — | Evita a ordem menos importante levar o filtro que o pulverizador esperava. | Protótipo: no passo 1b. Real: reserva de manutenção. | Configurações (momento da reserva). |
| MAN-06 | A capacidade da oficina é dada em horas por semana de cada especialidade, informadas pelo responsável. Sem valor, o indicador fica "não calculável". | Protótipo: mecânico 40 h e eletricista 8 h, sintéticos. | Evita mostrar uma folga que não existe. | Quando o indicador existir. | Apagar o valor. |
| MAN-07 | Preventiva gerada sozinha, sem duplicar e sem aprovar. Aprovar várias preventivas do plano num toque, dentro da alçada. Antecipar com motivo. "Liberar após inspeção" no lugar de "desfazer bloqueio". | — | Evita preventiva esquecida, ordem duplicada e máquina com freio ruim liberada "por engano". Base: NR-31, item 31.12 (verificar vigência). | Protótipo: depois do 1b, uma regra por vez. | Desligar cada regra. |
| MAN-08 (ajustada · Codex) | Na frente de manutenção: o abastecimento lançado duas vezes com a mesma identidade (mesmo recibo, ou o segundo registro apontando o primeiro) vira um só, e a diferença de volume acima da tolerância vai para conferência. Registros só parecidos (mesma máquina, hora e horímetro próximos) vão à conferência como "possível repetição", sem soma e sem junção sozinha: dois abastecimentos verdadeiros nunca somem. O consumo por hora soma os abastecimentos parciais entre tanques cheios (já corrigido). Uma regra única "a máquina impede o trabalho" vale ao liberar e iniciar O.S. e irrigação. As peças entram pelo 1b. | Identidade, janela, tolerância e testes de fronteira da OPE-04 e da OPE-06. | Evita 640 L contados em dobro, um abastecimento verdadeiro apagado como repetição e máquina ou bomba bloqueada indo ao campo. Gravidade estimada pelo Claude. | Protótipo: a frente só entra depois da revisão do Codex da correção do freio e do diesel. Abastecimento repetido e regra de impedimento vêm como o incremento seguinte, e também só são publicados depois de revisados pelo Codex. | Reverter o commit (não recomendado). |
| MAN-09 | Quem lança o abastecimento é o abastecedor designado de cada ponto; sem designado, o almoxarife. A divergência é resolvida pelo almoxarife, ou pelo gestor se o almoxarife for autor de um dos registros. | — | Evita lançamento de memória e evita quem pôs o diesel resolver a própria divergência. | Protótipo: campo "Abastecedor" no ponto. | Retirar o abastecedor do ponto. |

### 3.5 Produção e comercial

| ID | Decisão | Padrão | Por quê (dano evitado · base) | O que muda | Como reverter |
|---|---|---|---|---|---|
| PRO-01 (revisada; acordo delimitado · Codex) | A massa da saca é um dado de cada contrato, gravado com a fonte. Os quatro contratos de soja do protótipo são de demonstração, identificados, e ficam com 60 kg. No contrato novo, o campo é obrigatório e vem sem valor escolhido; "60 kg" e "50 kg" aparecem para um toque, com o aviso "conferir no contrato", e o documento fica gravado. No software real não há valor-padrão, e contrato antigo nunca é reinterpretado. | Demonstração: 60 kg, só nos quatro contratos sintéticos. Contrato antigo sem a massa escrita: "saca a conferir", que suspende só o que depende dela. | Evita contar 199.000 kg de soja que não existe ou entregar 1/6 a menos. Base: DEC-0510-03. | Protótipo: semente com 60 kg; as telas ocultas passam a dizer "sc 60 kg"; o senhor não precisa mais "registrar a saca" no teste. Real: campo no contrato, nunca recalculado. | Uma linha na semente. |
| PRO-02 | Na fruta, o local de recebimento decide. No galpão, a fruta é vendida por kg; no packing, fica "em processo" até ser classificada e embalada. | Lagoa Grande: galpão. Santa Rita: packing. | Evita a mesma fruta aparecer em dois lugares. | Nada. | Trocar o tipo do local. |
| PRO-03 | Plantas vivas por hectare e perda esperada são dados do talhão, com a origem. | Protótipo: 1.700 plantas/ha e 5 %, "sintético". Real: contagem e histórico da fazenda. | Evita prometer em venda fruta que não existe. | Nada. | Mudar o valor. |
| PRO-04 (acordo às fontes · Codex) | Cada armazém tem a sua tabela de desconto de umidade e impureza, com documento e vigência. Sem ela, vale a tabela de referência rotulada, e a carga fica "desconto a conferir". | Base de 14 % de umidade e 1 % de impureza (IN MAPA 11/2007 e 60/2011; verificar). | Evita mostrar mais sacas do que o armazém vai creditar. | Protótipo: rótulo "referência sintética". | Parâmetro por armazém. |
| PRO-05 (acordo às fontes · Codex) | Nenhuma norma de classificação fica embutida no código. Há um cadastro por produto, com norma, item, vigência e quem conferiu, e a norma só é ativada depois de conferida. | — | Evita classificar por norma revogada. | Protótipo: rótulo "sintética, sem norma". | Desativar a versão; sem norma ativa, a classificação fica "a conferir". |
| PRO-06 | Os R$ 120.000 da Frutas Real ficam como dado de demonstração. No real, o limite é por cliente, com validade; sem limite, a saída do produto pede aprovação. | — | Evita produto saindo para quem já deve acima do aceito. | Nada. | Mudar o valor. |
| PRO-07 | Aprovar crédito é um papel com teto em reais. No protótipo, só a Ana. No real, o titular tem o papel sem teto e o concede a outros com teto. Quem registrou a venda não aprova sozinho o crédito dela. | — | Evita o vendedor liberar o crédito da própria venda. | Nada. | Conceder o papel a outro perfil. |
| PRO-08 | Entrega no cliente ou retirada na fazenda vem do cadastro do cliente e pode ser corrigida na venda. | — | Evita frete e risco do transporte sem dono. | Nada. | Mudar no cadastro. |
| PRO-09 | A tolerância de peso é por contrato; sem ela, 0 %. O excesso só sai do mesmo lote, com aprovação, e a falta vira entrega parcial. | — | Evita entregar e cobrar além do contratado e tirar a reserva de outro cliente. | Nada. | Apagar a tolerância. |
| PRO-10 | Os parâmetros do beneficiamento são sintéticos no protótipo. No real, vêm da alçada da fazenda, do protocolo do responsável técnico e do cadastro de pessoas; se faltar algum, aparece "não definido". | — | Evita número inventado decidindo perda e custo. | Rótulo. | Nova versão da rota. |
| PRO-11 | Lote fora do padrão pode ser vendido a um cliente que aceitou por escrito, só naquela venda. A concessão vale só para tipo ou classe comercial. Nunca vale para critério de lei (carência, resíduo, contaminante, registro) nem para produto desclassificado pela norma oficial. | Sem aceite registrado, não há concessão. | Evita perder a venda e evita "reclassificar" o lote como bom para conseguir vender. | Protótipo: na frente Comercial, depois da junção. | Desligar a ação. |
| PRO-12 | Café: o fruto colhido em litros, o café em coco em kg, e a saca de 60 kg só para o beneficiado. Grão úmido: aparece o "equivalente a 14 % (estimado)", só para leitura. | — | Evita somar café em coco como beneficiado e vender saca de grão que vai encolher na secagem. | Protótipo: no BEN-3. | Esconder o rótulo. |
| PRO-13 | Laranja em caixas de 40,8 kg por hectare (com t/ha ao lado); coco e abacaxi em mil frutos por hectare. | — | É a unidade que o mercado usa, como o senhor pediu em 05/10. | Nada no código. | Trocar a linha da cultura. |
| PRO-14 | A meta de acerto da previsão é um alvo de teste: erro médio de até 10 %, calculado só com amostra mínima. Ficar fora da meta abre revisão e nunca bloqueia venda. | 8 semanas na fruta; 1 safra no grão. | Evita vender confiando em previsão ruim e evita travar venda por um número sem base. Base: PRD 70.4, DEC-03. | Com o CONTROLE-02. | Mudar a meta. |
| PRO-15 | Oportunidades só vão a destinatários que o produtor confirma. O envio automático fica desligado e só será construído depois do piloto, se houver pedido. | — | Evita dados do produtor com parceiros sem autorização (LGPD). Base: PRD 70.4, DEC-06. | Nada. | Ligar por organização. |

### 3.6 Irrigação e água

| ID | Decisão | Padrão | Por quê (dano evitado · base) | O que muda | Como reverter |
|---|---|---|---|---|---|
| IRR-01 (revisada; acordo às fontes · Codex) | Outorga vencida e "em renovação". No protótipo, irriga com aviso se o pedido foi protocolado no prazo e não foi negado. No software real, não há regra de fábrica: a regra de cada órgão (prazo do pedido e se a outorga vale durante a análise) é item obrigatório da implantação, com norma e fonte. Até lá, só irriga se o próprio documento do protocolo disser que a outorga continua valendo; senão, a tarefa fica em A liberar com o gestor e o próximo passo "Conferir a regra do órgão". O gestor recebe o aviso "Pedir renovação" 180 dias antes do vencimento. | Protótipo: 120 dias e "vale durante a análise", com o rótulo "premissa de demonstração · regra do órgão não conferida". Real: sem padrão. | Evita irrigar sem outorga válida (multa e embargo da captação) e evita parar pivô que a regra do órgão considera válido. Base: Lei 9.433/1997, arts. 12, 16, 49 e 50 (verificar vigência). A analogia com a licença ambiental (LC 140/2011) não serve de padrão para o real. | Protótipo: data e situação do protocolo, com quatro casos de teste. Real: regra única de outorga, conferida ao liberar e ao iniciar. | Parâmetros por órgão. |
| IRR-02 (ajustada; acordo às fontes · Codex) | Cada outorga limita o próprio ponto e o próprio ato (vazão, volume e o que mais o ato fixar). A rede de captação declarada no cadastro (pontos, bombas, adutora, pivôs e setores) diz de que ponto sai a água de cada pivô e acrescenta o limite físico da bomba e da adutora; ela não soma outorgas independentes. Limite conjunto só quando o próprio ato do órgão cobre os pontos em conjunto, com o documento. Pivô sem ligação a um ponto não libera. | Sem rede declarada, vale a outorga do ponto. Na demonstração, "Rede Rio A (demonstração)", com limite por ponto. A semente liga todos os pivôs e setores das duas fazendas, e os testes conferem que nenhum fica sem ligação e que um ponto não empresta saldo a outro. | Evita captar acima da outorga de um ponto supondo que outro ponto do mesmo rio ou da mesma rede cobre a diferença. Base: Lei 9.433/1997 (verificar vigência). | Protótipo: campo Rede e limite por ponto. Real: cadastro de captação, com cada pivô ligado a um ponto antes da primeira liberação. | Declarar ou desfazer redes. O limite por ponto e por ato não se reverte. |
| IRR-03 | "Lâmina 21 h" é a lâmina por dia que o pivô entrega ligado 21 horas, fora do horário de ponta. Fica guardada como capacidade do equipamento, conferida pela conta vazão × 21 h ÷ área. Vira aviso quando a necessidade do pico passa dela e nunca vira recomendação. | Na dúvida, tratada como lâmina bruta. Exemplo da ficha sintética: 15,7 mm/dia. | Evita tratar capacidade como recomendação e evita não perceber que o pivô não acompanha o pico. | Protótipo: campo na ficha do pivô e aviso de capacidade. | O campo é só informativo. |
| IRR-04 | Os dois defeitos graves da irrigação entram na frente Outorga e Agrofit, logo depois da junção. (1) Cada setor diz de onde vem o volume: hidrômetro, ou "sem medidor", com volume estimado por tempo × vazão e marcado "estimado". (2) Uma vazão só, a da ficha do pivô. O resto da "Irrigação medida" fica para a frente 3.3. | A conferência automática do volume estimado só acontece com início e fim confirmados pelo irrigante. Dois parâmetros com nomes diferentes: tolerância entre medido e estimado (3 %, valor proposto) e tolerância entre dois registros do mesmo fato (5 %). | Evita estimativa gravada como medição, que deixa a lâmina e a outorga erradas. Evita o Pivô 1 com 300 m³/h num lugar e 540 m³/h em outro. | Protótipo: sai o preenchimento automático com 98,5 % do previsto. Real: cadastro único de setor e a origem do volume gravada. | Parâmetro "exigir conferência manual do estimado". |

### 3.7 Plataforma, acesso e design

| ID | Decisão | Padrão | Por quê (dano evitado · base) | O que muda | Como reverter |
|---|---|---|---|---|---|
| PLA-01 | A barra do Mapa volta aos nove nomes que o senhor decidiu em 26/09, e "Lavoura" passa a "Estádio". Carência vira filtro de Colheita, e Insumos vira filtro de Ordens de serviço. Solo e Colheita leem os dados reais; talhão sem laudo aparece "Sem laudo" em cinza, nunca como zero. | Filtros de Ordens de serviço: Fases, Avanço, Atrasos, Impedimentos e Insumos. | Evita trocar uma decisão sua sem registro e evita a carência sumir do Mapa. Base: DEC-2609-06 e DEC-2609-12. | Protótipo: depois do passo 7 da junção. Antes, conferir no histórico de onde veio o "Solo e Colheita ficam para a Fase 2" (se for pedido seu mais novo, ele prevalece). O teste da barra é atualizado no mesmo commit. | Editar as listas. |
| PLA-02 | A cobrança é pela área contratada (com versão e aceite), não pela medida. Área medida maior gera aviso e o botão "Ampliar área contratada". Os preços continuam com o senhor. | Base: área contratada. | Evita cobrança-surpresa e evita o cliente deixar de cadastrar talhão para não pagar. Base: PRD 70.4, DEC-01. | Protótipo: um parâmetro. | Parâmetro "medida". |
| PLA-03 | Atraso de pagamento: de 1 a 10 dias, só aviso. A partir de 11 dias, não se cria nem se reativa talhão para planejar área nova. Nada mais é bloqueado nem apagado, e continua possível registrar um fato em área nova (ocorrência com a área desenhada). Suspender ou rescindir o contrato fica com o senhor. | — | Bloquear a O.S. empurraria a aplicação para fora do sistema, sem aprovação nem carência. | Protótipo: já é assim; só falta registrar. | Lista de restrições vazia. |
| PLA-04 | Cada pessoa entra na tela do seu trabalho e pode escolher outra como inicial, inclusive o Mapa. | — | O operador no campo vai direto à sua fila. Base: PRD 70.4, DEC-02. | Protótipo: "Entrar como" abre a tela do papel. | Tabela papel → tela. |
| PLA-05 (acordo delimitado · Codex) | Nenhum controle de qualidade e segurança é reduzido por prazo, nem pelo "tudo pronto hoje". | Os 10 checks obrigatórios da `main`. | Evita dado de uma fazenda visível a outra e perda de dados. Base: PRD 70.4, DEC-04. | Nada. | Só por ADR. |
| PLA-06 (acordo delimitado · Codex) | Etapas e cores: "Concluída" só aparece com a condição cumprida, e o vermelho só com impedimento real, com motivo e quem resolve. | — | Evita a safra seguir com cultivos sem plano e evita que ninguém note o vermelho verdadeiro. Base: ETP-01 (seu, 09/10). | Protótipo: frente de design, depois da junção dela. | Reverter os commits. |
| PLA-07 | Prazos internos para exceção de integração: controladoria e almoxarifado assumem em 1 dia útil, e o caso sobe em 3; TI assume em 4 horas úteis, e o caso sobe em 1 dia útil. Não são promessa ao cliente. | — | Evita exceção parada sem dono no fechamento do mês. | Real. | Configurações. |
| PLA-08 | Nenhum tipo de efeito no ERP segura o encerramento da O.S., salvo exigência legal, fiscal ou contratual demonstrada. | — | Evita O.S. presas esperando um ERP fora do ar. | Real. | Marcar o tipo. |
| PLA-09 | Atualização dos indicadores: operacionais em 5 min (15 no pior caso); necessidade e custos em 15 min (60 no pior caso). Se isso exigir custo maior de processamento, a decisão vai ao senhor. | — | Evita comprar sobre necessidade velha. | Real. | Consolidar custos de hora em hora. |
| PLA-10 | Em equipe pequena, a pessoa pode mudar a própria meta, com revisor posterior. A remuneração só usa a versão revista. | — | Evita bônus sobre meta mudada pela própria pessoa sem conferência. | Real. | Desabilitar a exceção. |
| PLA-11 | A gravação no ERP só é ligada depois que cada caso ocorrido foi conciliado e um fechamento mensal saiu sem divergência. | — | Evita lançamento errado no sistema oficial. | Real (ERP real continua com o senhor). | Editar o critério. |
| PLA-12 | Cada tipo de lançamento no ERP tem como dono o responsável pelo processo. A TI configura e suspende, mas não habilita. | — | Evita a TI ligar efeito financeiro sem o dono saber. | Real. | Alçadas. |
| PLA-13 | Ordem de ligação no ERP: consumo e devolução, depois custos, depois pedidos. Os títulos ficam no ERP. | — | Começa onde o risco é menor. | Real. | Reordenar. |
| PLA-14 | "Relatar problema" exige print, com a opção "Não consigo anexar a imagem" para quem não consegue (leitor de tela, câmera que falhou). | — | Evita excluir quem usa leitor de tela. Base: Lei 13.146/2015 (verificar vigência). | Real. | Retirar a opção. |
| PLA-15 | Print e comentário do chamado ficam guardados por 180 dias depois do encerramento e podem ser apagados antes, a pedido. | — | Evita guardar imagem com dado do cliente além do necessário (LGPD). | Real. | Parâmetro. |
| PLA-16 | Prazos internos de primeira resposta: acesso em 1 dia útil, defeito em 2, dúvida em 2, sugestão em 5. Não são promessa ao cliente. | — | Evita chamado esquecido e promessa que não se cumpre. | Real. | Editar os valores. |
| PLA-17 | O administrador da organização vê a lista dos chamados, sem print nem comentário. | — | Evita vazar dado dentro da própria organização. | Real. | Parâmetro. |
| PLA-18 | "Relatar problema" entra junto com o primeiro piloto, e também na homologação, para o senhor. | — | Evita feedback perdido no WhatsApp. | Real. | Tirar do escopo. |
| PLA-19 | "Implantação parada" só conta as etapas sem as quais o perfil não chega ao primeiro resultado útil. | — | Evita alarme falso ao cliente. | Real. | Marcar todas as etapas. |
| PLA-20 | Acompanhar a adoção dos clientes é uma permissão individual, com segundo fator e trilha, revista a cada 90 dias. | — | Evita dados de uso vistos por quem não precisa. | Real. | Ampliar a concessão. |
| PLA-21 | O contato com cliente de adoção baixa é feito por uma pessoa, nunca por mensagem automática. | — | Evita o cliente se sentir vigiado. | Real. | Nova decisão. |
| PLA-22 | Não há pontuação agregada de adoção até medir no piloto. | — | Evita uma nota que ninguém consegue explicar. | Nada. | Criar com versão. |
| PLA-23 | No protótipo, entram o papel Comercial e a almoxarife Lúcia (pessoas fictícias). Substituição temporária de papéis (nas férias do agrônomo) e exportação completa dos dados são obrigatórias no software real antes do piloto. | — | Evita ninguém aprovar nas férias do agrônomo, ou alguém usar o login dele. Evita o cliente não conseguir levar os próprios dados. | Protótipo: duas linhas no catálogo de papéis. | Tirar as linhas. |
| PLA-24 | Resolve a PEND-REPO-01: a proteção da `main` está ativa. A pendência aponta para cá e só sai da tabela no PRD 3.12. | Conferido hoje na API do GitHub: regra ativa, sem exceção, exige PR e os 10 checks, repositório privado. | Evita pedir ao senhor algo já resolvido. | Só registro. | Reabrir se a leitura mudar. |

**Design system** (pendências do capítulo 74 do PRD; todas entram pela frente de design, depois da junção dela, salvo indicação):

| ID | Decisão | Padrão | Por quê (dano evitado · base) | O que muda | Como reverter |
|---|---|---|---|---|---|
| PLA-DS01 | Cores das fases da O.S.: A liberar em cinza, Liberadas em azul, Em execução em verde, Em conferência em amarelo, Encerradas em cinza, sempre com o nome escrito. | Proposta do PRD 74.12. | Evita confundir "pronta para iniciar" com "em execução". | Kanban, lista e Mapa. | Trocar a variável de cor. |
| PLA-DS02 (acordo delimitado · Codex) | "Sobras a receber". | — | "Pendente" sozinho não diz quem age. | Protótipo já usa. | Trocar o rótulo. |
| PLA-DS03 (acordo delimitado · Codex) | Sem modo escuro por enquanto; as cores ficam organizadas por significado, prontas para um segundo tema. | Só tema claro. | Evita ler errado uma dose num tema sem contraste medido. | Nada. | Acrescentar o tema escuro e medir. |
| PLA-DS04 (acordo delimitado · Codex) | O nome exibido é "Do Talhão à O.S.". A marca provisória fica até o logotipo. Marca comercial e registro no INPI ficam com o senhor. | — | Evita dois nomes no mesmo produto e marca não registrada em material comercial. | Texto do menu. | Trocar a constante do nome. |
| PLA-DS05 | Fontes Sora (títulos) e Manrope (texto), servidas pelo próprio produto, sem buscar no Google durante o uso. A licença (OFL) é conferida no pacote. | — | Evita tela sem fonte no campo sem sinal e envio de dado de navegação a terceiro. | Só no real. | Trocar a família. |
| PLA-DS06 (ajustada · Codex) | Três larguras de tela: celular abaixo de 768 px, tablet de 768 a 1279 px (menu recolhido) e computador a partir de 1280 px. No celular, cartão no lugar de tabela é escolha por tarefa: só onde a pessoa não perde a comparação entre linhas nem as ações da tabela. Cada tela é conferida na largura real, com leitura, teclado e foco, reaproveitando os padrões já aceitos do design system e da navegação. | — | Evita tabela cortada no celular e evita trocar por cartões a tabela em que comparar linhas é o próprio trabalho. | Testes também em 768 e 1366 px nos marcos, com leitura, teclado e foco. | Trocar os valores. |
| PLA-DS07 | A barra do Mapa tem 96 px, com rótulo de até duas linhas. | — | Evita rótulo cortado e alvo pequeno para o dedo. | Nada. | Trocar a variável. |
| PLA-DS08 | A safra mostra só os estados do PRD 8.1, e "Em planejamento" sai. | Rascunho → Planejamento técnico aprovado → Orçamento autorizado → Em execução → Em fechamento → Encerrada. | Evita esconder se o plano foi aprovado e se o dinheiro foi autorizado. | Protótipo: frente do Planejar safra, depois da junção. | Acrescentar o rótulo ao PRD. |
| PLA-DS09 (acordo delimitado · Codex) | Menu recolhido de 64 px, com nome e dica em cada item. Aberto no computador, recolhido no tablet, e a escolha de cada pessoa fica lembrada. | — | Evita o menu tomar o Mapa no tablet. | Botão de recolher. | Trocar a variável. |
| PLA-DS10 (ajustada · Codex) | Vale o contrato C4 já revisado: a camada Satélite usa NDVI, NDRE, EVI, SAVI e NDMI, e o índice de umidade é o NDMI (não é trocado pelo NDWI). Cada índice mostra nome, fórmula e fonte exatos, como no contrato. O NDMI ganha rampa própria, diferente da de vigor, que mostra o valor do índice e o contraste entre áreas, sem rótulo de diagnóstico ("muito seco", "úmido") e sem virar comando ou sugestão de irrigação. | Rampa contínua do valor do índice, com a legenda numérica. | Evita ler umidade como vigor e evita que uma cor do mapa vire decisão de irrigar. | Camada Satélite. | Trocar a rampa de cores. |
| PLA-DS11 | O Solo usa cores por faixa técnica: baixo laranja, médio amarelo, adequado verde e alto azul. Sem faixa técnica, mostra só o valor. | — | Evita pH ou fósforo alto pintados como "ótimos", induzindo adubo e corretivo a mais. | Camada Solo e telas de solo. | Trocar a rampa de cores. |
| PLA-DS12 | No software real, satélite pixel a pixel, com imagem gratuita (Sentinel-2; verificar os termos). Imagem paga de alta resolução fica com o senhor. No protótipo, onde não há cena, aparece "média do talhão". | — | A média esconde a mancha de doença ou de falha de plantio. | Linha de fonte da camada. | Voltar à média por talhão. |
| PLA-DS13 (ajustada · Codex) | A precisão de cada número segue a unidade e a regra de domínio dele, e é a mesma no cálculo, nas tabelas e nos documentos: duas casas não podem apagar dose pequena, área, massa ou conversão. Números compactos ("mil", "mi") só no mapa, em cartões e em indicadores, onde não impedem decisão, e sempre com o valor exato acessível (dica ou detalhe). | Casas definidas por unidade, uma vez só, na regra de domínio. | Evita que o arredondamento esconda diferença de dinheiro, de dose, de área ou de massa. | Uma função única de formatação, que recebe a unidade. | Desligar o modo compacto. |
| PLA-DS14 | Dois sons curtos no app, "salvo" e "atenção", sempre acompanhados de texto e respeitando o modo silencioso. | — | Evita o operador de luva repetir ou abandonar um registro. | Opcional no protótipo. | Desligar. |
| PLA-DS15 (acordo delimitado · Codex) | Reserva comercial vencida: "Vencida · devolvida ao disponível". | — | "Liberar" tinha dois sentidos no mesmo produto. | Frente Comercial. | Trocar o rótulo. |

### 3.8 Processo e prioridade

| ID | Decisão | Padrão | Por quê (dano evitado · base) | O que muda | Como reverter |
|---|---|---|---|---|---|
| PRC-01 (ajustada · Codex) | Juntar as frentes prontas uma por vez, por risco e dependência (seção 5). Continuam em curso, sem interrupção: a correção do Beneficiamento e a revisão da DOM. O Beneficiamento integrado não está aceito: o S2 de origem de lote (Codex 6090699184) continua aberto. Nenhum trecho é publicado com risco impeditivo conhecido. Antes de qualquer teste seu, consertar "Restaurar dados iniciais" e "Entrar como". | A fonte de cada frente ainda não integrada vai para revisão do Codex como pacote de patches em `docs/integracao/<ID>/` na própria branch única (como a DOM em `7386172`), sem branch nova no GitHub: a branch única de 05/10 continua sem exceção. Cada exigência nova vai para o ID que já existe (frente, PEND ou DEC), sem outra fila. | Evita o senhor testar com dados alterados e perfil errado, evita uma frente desfazer a outra e evita dar por aceita uma frente com S2 aberto. | Protótipo: uma junção por commit, com os testes das duas frentes que mexem nos mesmos arquivos. | Reverter o commit de junção. |
| PRC-02 (revisada; ajustada · Codex) | As correções do passo 2 entram em cada frente logo depois da junção dela. As únicas exceções são defeitos da própria frente. Dentro de cada frente, a ordem é por risco e dependência: primeiro o que impede publicar. As frentes novas do passo 3 só começam depois do passo 1, uma por vez: 3.1 Aplicação segura e legal, 3.2 Planejamento confiável, 3.3 Irrigação medida, 3.4 Cadastro que alimenta os processos. | Na 3.1: família, reentrada, ocorrências com destino, receituário ligado, sobra de calda e EPI. | Evita várias frentes abertas e nenhuma terminada; lei e pessoas vêm primeiro. | Seção 5. | A ordem muda sem desfazer nada. |
| PRC-03 (acordo delimitado · Codex) | Já agora: aviso "Demonstração: o que salvar aqui ainda não muda os outros módulos" nas telas de cadastro. Na 3.4, só três ligações: talhão inativo fora do planejamento novo, fornecedor homologado lido pela Compra e identidade única da máquina. | — | Evita o senhor validar um cadastro que não muda nada. | Protótipo: o aviso sai de cada tela quando a ligação dela fica pronta. | Tirar o aviso. |
| PRC-04 (revisada; ajustada · Codex) | Registrar já, no registro que existe (`docs/DECISIONS.md`): os seus pedidos, com texto literal e data; as decisões dos agentes nas frentes, confirmadas frente a frente quando o Codex revisar a junção; e a delegação de 09/10, que chegou direto aos dois agentes, com texto, canal e hora. Conforme o seu pedido direto de 09/10, citado pelo Codex, o PRD 3.12 só é escrito depois de todas as implantações atuais concluídas, com IDs, estados e provas conferidos. Até lá, nenhuma pendência é antecipada nem apagada. Nenhum registro diz "aprovado pelo proprietário". | Autor deste texto e do PR de registro: o Claude. O Codex revisa e integra (DEC-0910-02). | Evita desfazer decisão não registrada, evita um PRD que diga pronto o que ainda está em implantação e evita declarar aprovação sua que não houve. | Real: PR de registro na `main` agora (DECISIONS); PRD 3.12 depois. | Outro PR. |
| PRC-05 (ajustada · Codex) | Reaproveitar as referências de mercado válidas que já existem (fonte oficial e data) e pesquisar só a lacuna concreta de módulo ainda não coberto. Não se repetem cinco pesquisas como condição de cada teste ou correção. Nenhum texto diz "acima do mercado" sem prova. | Candidatos a lacuna, a conferir contra o material existente: Suprimentos e Estoque, Manutenção e Beneficiamento. Autor da pesquisa: o Codex; revisor: o Claude. | Evita decidir com base em superioridade não comprovada e evita pesquisa repetida que não muda decisão. | A alegação sai dos textos; no parecer, passa a "segue o contrato do produto". | É documento. |
| PRC-06 (revisada; ajustada · Codex) | Vale o FOCO-APLICACAO-REAL v2. Primeiro, concluir todo o conjunto vigente do protótipo, com uma candidata completa que funcione de ponta a ponta e a validação e auditoria tripla. Depois, transferir ao software real nesta ordem: tela → domínio → banco → homologação. Uma frente revisada sozinha não libera a passagem. O trabalho em curso da C2 (PRs #32 a #35) continua, sem interromper a autoria atual. Na transferência, continuam as proteções: a fatia que liberar O.S. já nasce com a aprovação do agrônomo por versão conferida no servidor na liberação, a família da operação e a habilitação conferida ao aprovar; O.S. com agrotóxico é recusada até a fatia própria, com reentrada, autoria do receituário, receituário ligado à O.S. e carência por área. | Nenhum S2 conhecido no escopo: escrever um S2 como caso de aceite não o resolve. A ordem das fatias vai na tarefa escrita pelo Codex. Depois da passagem, o protótipo não ganha evolução paralela; só recebe correção que afete a validação. Desenvolvimento, QA e homologação já autorizados (EXT-01). | Evita a primeira fatia real liberar O.S. sem agrônomo, que seria o defeito mais grave possível. Evita levar ao real uma peça que o conjunto ainda não validou e dois produtos evoluindo em paralelo. | Real: desenvolvimento, QA e homologação; só se chama de homologação o ambiente que existe e foi conferido. | Uma linha no DECISIONS. |

---

## 4. O que fica aguardando o senhor

### 4.1 Fora da delegação

EXT-01 e EXT-02 continuam na tabela para manter os IDs, mas **não aguardam o senhor** (ajuste do Codex 6091153950).

| ID | O quê | Enquanto isso |
|---|---|---|
| EXT-01 (ajustada · Codex) | **Não aguarda o senhor.** Desenvolvimento, QA e homologação já estão autorizados: referência de US$ 30/mês antes de tributos (seu aceite de 29/09, R-006) e US$ 10/mês de GitHub Actions (informado pelo Codex 6091153950; a fonte literal vai citada no PR de registro). Não pedimos de novo orçamento concedido. | Antes de dizer que algo está travado por login ou faturamento, conferimos o estado atual da conta e do projeto. Se houver um ato que só o senhor pode fazer (por exemplo, cartão, termos ou autenticação pessoal), registramos qual é e a prova. O trabalho que não depende da nuvem segue. |
| EXT-02 (ajustada · Codex) | **Não aguarda o senhor.** O limite de US$ 15/mês no Cloud Run é proposta interna nossa, dentro do orçamento concedido. Não é teto aprovado pelo senhor nem garantia de que a cobrança fique limitada. | Valem os alertas de orçamento da homologação (referência de US$ 30); alerta não interrompe a cobrança. |
| EXT-03 | Hospedagem do piloto (cerca de US$ 112 a 183/mês) e domínio próprio, só depois do seu aceite da candidata. | Nada contratado. |
| EXT-04 | Licença do SonarQube. | A exceção registrada continua e vence antes do piloto; Semgrep, lint e testes continuam como controles. |
| EXT-05 | Revisão humana de segurança e arquitetura antes do piloto. | Preparamos o escopo e duas ou três opções com preço público, sem contatar fornecedor. Sem essa revisão, não há piloto. |
| EXT-06 | Docker Desktop no seu Mac. | Não é necessário: a CI já roda o banco real. |
| EXT-07 | Integração real com ERP (Sankhya ou TOTVS) e busca de nota na SEFAZ. | A fila do ERP continua simulada, sem credencial e sem envio real. |
| EXT-08 | Dados reais da implantação (empresas, fazendas, protocolos, plano de contas, alçadas, crédito, conectividade). | Tudo sintético e rotulado. Preparamos o formulário vazio do PRD 20.6. |
| EXT-09 | Publicar para usuários reais, iniciar o piloto e aceitar a candidata de produção. | A candidata fica pronta em desenvolvimento e na CI, sem publicar. O protótipo privado continua sendo atualizado. |
| EXT-10 | Que atendimento prometer no piloto (horário, plantão, 24×7). | O piloto não é chamado de 24×7, e os prazos internos não são promessa. |
| EXT-11 | Assistente de IA: provedor, contrato de dados e orçamento. | Desligado. |
| EXT-12 | O seu aceite das fatias como usuário. | Para cada fatia pronta, preparamos um pacote curto: link, versão, o que mudou, uma tarefa de poucos minutos, as limitações e só as perguntas sobre a fazenda. |
| EXT-13 | Preço, mínimo, franquias, planos, período de avaliação e calendário de cobrança. | Exemplos no protótipo, sem cobrança real. A base de cobrança (PLA-02) e a régua de atraso (PLA-03) já valem para qualquer preço. |
| EXT-14 | Ferramenta de mercado para os chamados. | Tela interna restrita à equipe de suporte. |
| EXT-15 | Aceitar consignação de peças de fornecedor. | Sem consignação. |
| EXT-16 | Mensagens reais por e-mail ou WhatsApp. | O convite é um link que o administrador copia e envia pelo próprio canal. |

**Partes de decisões tomadas que ficam com o senhor:**
- marca comercial e registro no INPI (PLA-DS04);
- imagem de satélite paga (PLA-DS12);
- custo maior de processamento para atualizar indicadores (PLA-09);
- suspender ou rescindir contrato por falta de pagamento (PLA-03);
- prazo de atendimento escrito em contrato (PLA-16, com a EXT-10);
- leitura automática de laudo, que tem custo (AGR-04).

Não há ratificação da delegação pendente na sua volta: o Codex recebeu a mensagem direto do senhor (6091153950). A passagem ao software real segue a condição do PRC-06.

### 4.2 Dados reais a confirmar (não bloqueiam; vale o padrão seguro)

| Domínio | O que confirmar | Padrão até lá |
|---|---|---|
| Agronomia | Responsável técnico de cada fazenda, tabela e fonte que ele usa, extrator do laboratório, se os laudos trazem argila e a camada de 20 a 40 cm. Conselho, número, UF e ART dos agrônomos (dado real, só na implantação). Operações manuais em talhão tratado. O.S. mecânicas por semana e número de agrônomos. Frequência de envio das sondas. Contratos de arrendamento. Unidade do cadastro de produtos. | Demonstração rotulada; no real, sem sugestão de dose. |
| Operação | Quem faz o PCP. Tempo real sem sinal. Divergências reais por tipo. Rotina de abastecimento. Máquinas e equipes que atendem as duas fazendas. Se planta atrás da colhedora. Áreas embargadas ou arrendadas a terceiro. Volume de calda e tanque útil de cada pulverizador. | Valores das tabelas acima, revistos depois do piloto. |
| Suprimentos | Pessoas reais e limite para exigir segunda pessoa. Alçadas reais de compra. Tolerâncias dos contratos e classe das balanças. Laboratórios. Com o contador: formação do perene, vida útil, arrendamento, custo da terra própria e conta de serviços de terceiros. | Direção aprova tudo; tolerância de contrato 0 %. |
| Manutenção | Valores de alçada e quem decide conflito. Classe de cada máquina. Custo mensal da oficina. Frota de estrada e gasto com pneus. Horas por especialidade. Pontos de abastecimento e quem opera cada um. | Tudo sobe ao nível mais alto; sem classe = A; custo parcial. |
| Produção e comercial | Massa da saca de cada contrato. Se a fruta passa por packing. Contagem de plantas e perda. Tabela de desconto de cada armazém. Vigência das normas de classificação. Limite de crédito de cada cliente (dado real). Modalidade de entrega, tolerância de peso e medida regional do café. Meta da previsão. | Massa obrigatória; referência rotulada; sem limite, pede aprovação. |
| Irrigação | Com o jurídico: órgão de cada outorga, prazo do pedido de renovação e validade durante a análise, e protocolos reais. Rede comum de captação, bombas, adutora e medidores. Ficha real de cada pivô e horário de ponta. Quais setores têm hidrômetro e a vazão medida. | No real, só irriga com a regra do órgão conferida ou documento; sem medidor = volume estimado. |
| Plataforma | Área contratada de cada cliente. Horário útil e responsáveis. Volume mínimo por operação para ligar o ERP. Capacidade do suporte e quem faz parte dele. Logotipo e marca. | Valores internos, sem promessa ao cliente. |
| Processo | Conectividade e aparelhos reais do app antes do piloto. | Ensaio sem sinal de 72 h como mínimo. |

---

## 5. Ordem de execução decidida

**Regra geral (PRC-02).**
- Cada correção do passo 2 entra na frente dela como o incremento seguinte, logo depois da junção daquela frente.
- Só há duas exceções, por serem defeitos da própria frente:
  - o consumo de diesel na manutenção, já corrigido e esperando a revisão do Codex;
  - a parte 1 da demanda (OPE-10).
- Em cada frente, vem primeiro o defeito grave e o que viraria gravíssimo no software real.
- Nenhum trecho é publicado com risco impeditivo conhecido.
- Cada junção roda os testes das duas frentes que mexem nos mesmos arquivos e confere que as telas das duas continuam funcionando.

### Passo 1. Juntar o que está pronto (por risco e dependência; PRC-01)

A lista abaixo é a sequência atual. Ela muda quando um risco impeditivo ou uma dependência pedir, sem abrir outra fila.

0. Em curso, sem interrupção:
   - a correção do Beneficiamento, com as provas. O Beneficiamento foi integrado, mas **não está aceito**: o S2 de origem de lote (Codex 6090699184) continua aberto;
   - a revisão da DOM pelo Codex (candidata recuperável, base `ecc8b00`→`1fd8cfa`, pacote em `7386172`). Ela volta ao integrador depois da revisão.
1. Terminar o lote do Planejar safra em curso: trava de área com perene, ajuste `64a3041` e capacidade igual entre safras.
2. Demanda única (sp-ctl4), com a parte 1 da OPE-10 antes da junção.
3. Domínio (sp-dom), depois da revisão do item 0.
4. Suprimentos 2a e 2b (sp-sup).
5. Manutenção (sp-pcm). Entra só depois da revisão do Codex da correção `ba03515` (freio e diesel). Se a revisão não tiver chegado, a fila segue sem ela, e a manutenção entra assim que for revisada.
6. Configurações (sp-conf), com a mesma regra de esperar a revisão sem parar a fila.
7. Outorga e Agrofit (sp-ctl5), solo (sp-solo) e comercial (sp-com).
8. Tabelas (sp-tabr), design (sp-ds) e navegação (sp-nav). Por último, os cadastros com seleção que abre detalhe (sp-cadux).

**No mesmo passo, antes de qualquer pacote de teste para o senhor:**
- "Restaurar dados iniciais" passa a apagar o que ficou guardado no navegador;
- "Entrar como" passa a trocar de verdade o perfil;
- aviso de demonstração nas telas de cadastro (PRC-03);
- texto de ajuda do custo da terra corrigido (SUP-12);
- fonte das frentes ainda não integradas como pacote de patches em `docs/integracao/<ID>/` na branch única, para a revisão do Codex.

### Passo 2. Encaixes nas frentes, logo depois da junção de cada uma

| Frente | O que entra, em ordem |
|---|---|
| Planejar safra (lote SAF) | Folga de 0 dia (OPE-16). Fim do perene, safra encerrada com cultivos em campo e aviso na cultura seguinte (OPE-18). Estados da safra do PRD 8.1 (PLA-DS08). Aviso de eficiência fora da faixa (OPE-13). |
| Demanda (sp-ctl4) | Partes 2 e 3 da OPE-10: cobertura por estoque ou por pedido; plantio sugerido nunca no passado. |
| Domínio (sp-dom) | Mistura completa para iniciar e volume de calda na versão aprovada (OPE-09). |
| Suprimentos (sp-sup) | Lote elegível. Reserva que volta, junto com o cancelamento pendente (OPE-11). Produto errado no recebimento, junto com o motivo da quarentena (SUP-05). Peças da manutenção (1b). Do pedido ao recebimento, com a tolerância do contrato e a incerteza da balança só com origem técnica (SUP-11, SUP-04). |
| Manutenção (sp-pcm) | Abastecimento repetido, só por identidade, e abastecedor por ponto (MAN-08, MAN-09). Regra única "a máquina impede o trabalho" (MAN-08). Alçada própria e teto de balcão (MAN-01). Criticidade (MAN-02). Peças pelo 1b, reservadas na aprovação (MAN-05). Depois, as regras da MAN-07, uma por vez. Tudo isso só é publicado depois da revisão do Codex. |
| Configurações (sp-conf) | Habilitação conferida na hora de aprovar, autoria do receituário do MIP e de quem publica o plano (AGR-08, AGR-06). Quem libera: PCP ou gestor (OPE-01). Papel Comercial e almoxarife Lúcia (PLA-23). Rótulo "padrão decidido" nos parâmetros (OPE-02 a OPE-06). |
| Outorga e Agrofit (sp-ctl5) | Origem do volume e vazão única (IRR-04). Outorga em renovação (IRR-01). Rede de captação (IRR-02). Lâmina 21 h (IRR-03). Conferência legal no plano e trava de unidade (AGR-07). Regra de impedimento no "Iniciar irrigação" (MAN-08). |
| Solo (sp-solo) | Rótulos do gesso e da tabela (AGR-02, AGR-03). Cores do Solo por faixa técnica (PLA-DS11). |
| Comercial (sp-com) | Massa da saca (PRO-01). "Vencida · devolvida ao disponível" (PLA-DS15). Aceite de lote fora do padrão (PRO-11). |
| Design (sp-ds) | Etapas e cores (PLA-06). Cores das fases (PLA-DS01). Rampa do NDMI (PLA-DS10). Menu recolhido (PLA-DS09). Precisão por unidade e números compactos (PLA-DS13). |
| Navegação e Mapa | Barra do Mapa com os nove nomes (PLA-01), depois do item 7 do passo 1. "Entrar como" abre a tela do papel (PLA-04). |
| Cadastros (sp-cadux) | Arrendamento vencido com aviso (AGR-09). |

### Passo 3. Frentes novas, uma por vez

Cada frente nova começa com o acordo curto de seis campos, escrito pelo Codex. Se o Codex não puder, o Claude escreve e o Codex revisa sem bloquear.

1. **Aplicação segura e legal** (3.1), nesta ordem:
   1. família da operação;
   2. reentrada;
   3. ocorrências com destino, junto com a ciência do aprovador (OPE-07) e o encerramento com pendência do celular (OPE-08);
   4. receituário ligado à O.S.;
   5. sobra de calda;
   6. EPI.
   Carência e reentrada já nascem por área realmente tratada (OPE-07, OPE-18). Depois, "Aprovar selecionadas" na fila do agrônomo (AGR-01).
2. **Planejamento confiável, junto com o CONTROLE-02** (3.2), em dois incrementos se passar de uma fatia testável:
   - variedade do cadastro;
   - versão do plano gravada no cultivo;
   - estados e autorização da safra;
   - conferência diária;
   - custo por horas;
   - talhão indisponível (OPE-17);
   - custo da terra e formação (SUP-12);
   - meta da previsão (PRO-14).
3. **Irrigação medida** (3.3): percentímetro, parâmetros com versão e validade dos dados por fonte na Irrigação (AGR-05).
4. **Cadastro que alimenta os processos** (3.4): talhão inativo, fornecedor homologado, identidade única da máquina e "atende também as duas fazendas" (OPE-15). O aviso de demonstração sai de cada tela quando a ligação dela fica pronta.

Nenhuma frente fora desta lista nasce do parecer sem nova decisão.

Nossa leitura, que o Codex confere: os passos 1 a 3 formam o conjunto vigente do protótipo que precisa estar concluído antes da passagem ao software real (PRC-06).

### Software real (PRC-06, ajustada pelo Codex)

1. O trabalho em curso da C2 continua (PRs #32 a #35), sem interromper a autoria atual.
2. A passagem só começa com todo o conjunto vigente do protótipo concluído, uma candidata completa que funciona de ponta a ponta e a validação e auditoria tripla (FOCO-APLICACAO-REAL v2). Uma frente revisada sozinha não libera a passagem.
3. A transferência segue a ordem tela → domínio → banco → homologação. A ordem das fatias vai na tarefa escrita pelo Codex; a proposta anterior (Estoque ligado à O.S., app de campo sem sinal, O.S. com agrotóxico) fica como ponto de partida.
4. Proteções que continuam em qualquer ordem:
   - a fatia que liberar O.S. já nasce com a aprovação do agrônomo por versão, conferida no servidor ao liberar, com a família da operação e com a habilitação conferida ao aprovar;
   - O.S. com agrotóxico é recusada até a fatia própria, com reentrada, autoria do receituário, receituário ligado à O.S. e carência por área;
   - nenhum defeito S2 conhecido no escopo: escrever o defeito como caso de aceite não o resolve.

Depois da passagem, o protótipo não ganha evolução paralela; só recebe correção que afete a validação. Desenvolvimento, QA e homologação já estão autorizados (EXT-01); só se chama de homologação o ambiente que existe e foi conferido.

---

## 6. Como a revisão por contraexemplo mudou as decisões

| Decisão | O que estava errado | Como ficou |
|---|---|---|
| PRC-06 (bloqueava) | A primeira fatia real (Estoque × O.S.) liberaria O.S. agrícola sem a aprovação do agrônomo. | A fatia já nasce com aprovação, família e habilitação, e recusa O.S. com agrotóxico até a fatia própria. Depois, o Codex (6091153950) mudou o momento da passagem: FOCO-APLICACAO-REAL v2. |
| AGR-06 e PRC-02 | Mandavam a autoria do receituário do MIP para lugares diferentes. A reentrada não dizia o que comparar. | Autoria em Configurações; reentrada compara o início da janela (ao liberar) e a hora atual (ao iniciar). |
| OPE-07 | A área tratada a mais ficava sem carência e reentrada. | Carência e reentrada pela área real, e ocorrência ao agrônomo fora do receituário. |
| OPE-18 | A carência da cultura seguinte não protegia a colheita da anterior. | Carência por área e data, para qualquer lavoura em pé. |
| IRR-01 | Chamava de "conservador" um padrão permissivo, tirado por analogia. | No real, sem padrão de fábrica; só irriga com a regra do órgão conferida ou documento. |
| MAN-01 | Levava valores de demonstração ao software real. | No real, tudo sobe ao nível mais alto até a fazenda publicar valores. |
| PRO-01 | O campo pré-preenchido com 60 kg contrariava "o sistema não presume". | Campo sem valor escolhido; um toque em 60 ou 50 kg, com "conferir no contrato". |
| SUP-04 | A tolerância de 0 % abria caso em toda carga de granel. | 0 % no contrato, mais uma incerteza de medição separada por balança. Depois, o Codex (6091153950) retirou o 1 % automático: a incerteza só existe com origem técnica. |
| OPE-09 | Entrava antes da junção, contra a regra do passo 2. | Entra logo depois da junção da frente de domínio. |
| PRC-04 | A delegação estava só no canal do Claude, e o Codex dependeria de repasse. | Prova anexada e leitura registrada pelo Codex. Depois, o Codex confirmou que recebeu a delegação direto no canal dele: não há ratificação pendente (6091153950). |

As observações menores também entraram:
- referências de adubação como "candidatas por região";
- conselho além do CREA e visto de outra UF;
- restrição do embargo chegando à venda;
- produto desclassificado fora da concessão;
- duas tolerâncias de água com nomes distintos;
- todos os pivôs da demonstração ligados a uma rede;
- depreciação no lugar de amortização;
- frente 3.2 dividida se ficar grande;
- registro de fato em área nova mesmo com atraso de pagamento;
- "Liberar" recusado com cancelamento pendente;
- fonte para revisão por pacote de patches na branch única (sem branch nova);
- "gravidade estimada pelo Claude" nas correções vindas do parecer.

Ao consolidar, alinhamos mais três decisões à regra do passo 2: a OPE-10 (só a parte 1 antes da junção), a MAN-08 (diesel em dobro e impedimento depois da junção revisada) e a PLA-06 (depois da junção do design).

Os ajustes do retorno do Codex 6091153950 estão no quadro do início. Onde eles mudaram uma linha desta seção, vale o quadro.

---

## 7. O que foi conferido e o que não foi

**Executado:**
- leitura da `main` (`5831eb3`): `AGENTS.md` e `docs/DECISIONS.md`;
- leitura do comentário 6088167538 do Codex, pela API do GitHub;
- leitura da regra de proteção da `main` (24154464), pela API, em 09/10: ativa, sem exceção, exige PR e os 10 checks; repositório privado;
- leitura das seções 1, 2, 4 e 7 do parecer e do índice do levantamento dos 130 assuntos;
- as decisões e a revisão por contraexemplo foram recebidas prontas desta mesma sessão; a revisão registrou as próprias leituras (PRD v3.11, commits das frentes e código do protótipo);
- leitura integral do retorno do Codex 6091153950;
- leitura de `docs/parceria/rodadas/evidencias/R-006-hospedagem.md` na `main` (`a4fc3ae`): aceite de 29/09, "Autorizar HML com referência de US$30/mês", só para a homologação, antes de tributos, sem ser teto; em 28/09, o projeto da nuvem existia com faturamento vinculado;
- leitura das regras de conciliação do PRD (CONC-05, CONC-09, CONC-10 e CONC-11), na cópia da `main` usada no inventário, para os ajustes da OPE-04 e da OPE-06;
- o esquema do protótipo lista os índices NDVI, NDRE, EVI, SAVI e NDMI (`tools/prototipo/v37/specs/esquema_lagoa.md`, linha 21).

**Não executado:**
- nenhum teste;
- nenhuma mudança no protótipo ou na `main`;
- nenhuma norma conferida na fonte oficial: todas continuam "verificar vigência";
- o estado atual da conta e do projeto da nuvem não foi conferido nesta etapa;
- o FOCO-APLICACAO-REAL v2, o contrato C4, o recibo 6090699184 e o seu pedido direto de 09/10 sobre o PRD 3.12 são citados pelo retorno do Codex; não foram relidos nesta etapa;
- o trecho do totalizador da bomba como identidade (OPE-04, DEC-0910-16 c) é leitura nossa e aguarda a confirmação do Codex;
- a fonte literal dos US$ 10/mês de GitHub Actions não foi achada no repositório; vale o que o Codex informou, a citar no PR de registro;
- os IDs sem marca do Codex continuam aguardando o Codex, e os ajustados aguardam a conferência dele sobre o texto.
