# ENTREGA-FAZ · Compra única da safra e entregas programadas por fazenda

> Proprietário, 16/10/2026: "Após enviar insumos das fazendas e talhoes planejados para a safra para o setor de compras comprar, reune todo o volume, na hora de entregar, separa por fazenda para nao entregar tudo numa fazenda só. Veja como fazer programacao de entrega com fornecedor e fazenda.... da melhor forma possivel baseado no uso do plano agronomico + definicao agronomo, etc use as melhores praticas para isso. Fornecedor na hora de clicar no link (email e zap / portal do sistema para fornecedor) fornecedor pode ver em 1 clique total e por fazenda os volumes, e na gestao de entregas e datas, sempre separado por fazenda. melhore o prompt para si mesmo para fazer isso com perfeição."

## Pedido melhorado

- **Resultado:** uma negociação só com o volume total da safra, e cada fazenda recebe o que vai usar, no local certo, na janela tirada do plano agronômico.
- **Quem usa:**
  - o comprador negocia e acompanha;
  - o fornecedor confirma e entrega;
  - o almoxarife de cada fazenda recebe;
  - o agrônomo e o gestor são a origem da demanda.
- **Restrições:**
  - nenhuma quantidade sem fazenda;
  - a soma por fazenda é igual ao total;
  - mudança de plano vira proposta, nunca efeito silencioso;
  - o servidor é a autoridade de saldo e reserva;
  - o fornecedor não vê nada além do próprio pedido.
- **Pronto quando:**
  - o fornecedor abre o link e vê o total e cada fazenda lado a lado, sem outro clique;
  - confirma ou propõe datas por fazenda;
  - a nota fiscal entra na fazenda certa;
  - pedido, entregas e notas fecham por item e por fazenda.

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: ENTREGA-FAZ / comprar o total da safra numa negociação e entregar a cada fazenda o que ela usa, na janela do plano; o fornecedor vê total e fazendas em 1 clique / comprador, fornecedor, almoxarife da fazenda (agrônomo e gestor como origem da demanda)
Requisitos do PRD e fora do escopo: §IDs do PRD abaixo; fora: §Fora do escopo
Autor / revisor / integrador: Claude / Codex / Codex (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: claude/v44-v69-mapa em a685f5e / safra.js (etapa 4), areas/processo_compras.py, entrega.js (novo: programação e invariantes), areas/parceiros.py (página do link), areas/processo_estoque.py (recebimento por entrega), dados2.py e dados_cad.py (antecedência, recebimento da fazenda, classe e capacidade do local), cenario.js (estado das entregas), testes novos entrega_faz_unit.js e entrega_faz_test.py
Aceite e comando de verificação: E1–E19 (com E4b, E4c, E5b, E8b e E16b) abaixo / node entrega_faz_unit.js; python3 -B entrega_faz_test.py; mais cal01_test.py, cmptest.py, est_cenario_test.py, node safra_grupo_contrato_test.js, pt06_unit.py, ds_1610_test.py
Estado / impedimento / próximo passo: especificado, sem código; revisado pelo Codex e pelo Gemini em 16/10 (§Revisão), achados tratados nesta versão; na fila sem ampliar frentes nem autorias (§3.6), depois de Cadastros e da Onda 0; no protótipo tudo é simulado; P1 e P2 só travam o software real
```

## Revisão (Codex e Gemini)

- **Peso das propostas abaixo:** são do autor e só valem depois dos aceites (§3). Cada achado é aceito, ajustado ou recusado com fundamento.

| Revisor | SHA-256 do texto revisado | Data | Parecer |
|---|---|---|---|
| Codex | `ac2dec62796db1270a2476a5c54abcb6520d745d820250c643f9d0a16e033933` (b93e06f, 300 linhas) | 16/10/2026 | Direção aceita: compra agregada e entrega identificada por fazenda, com os ajustes 1–8 abaixo. Comentário 6219426486 no PR #47. Executou um script independente em Decimal, com calendário, com 7 verificações aritméticas: reproduziu S1 (Óleo 860 = 220 + 640; Glifosato 320 = 20 + 300), as três entregas e janelas, o E12 em quatro entregas com as quantidades preservadas, e a falta de 90 L do E6, coerente com a sobra de 10 L. Não executou CAL-01, `entrega.js` nem navegador. Brutos com o Codex em `work/dupla-20261013/entrega-faz-20261016/`. |
| Codex (R2) | `0184cd89683d85ab3c923a5992627f4d92d8d163ce145fdcba7b8cf0b5a08814` (0d26443, 398 linhas) | 16/10/2026 | Aceitou os 8 encaminhamentos e reproduziu o Decimal. Restaram 1 achado S2 no script de prova e 1 ajuste de texto (R2-1 e R2-2, abaixo). Comentário 6220011063 no PR #47. |
| Gemini (conector do Codex) | o texto de b93e06f; requisição com SHA-256 `88a9968d3d8afaaa70d1e740d4c920a43d79af4af15c7b018d77975c726a371d` | 16/10/2026, início 15:54:55Z | Modelo `gemini-3.1-pro-preview`, esforço HIGH; resposta `0EjSaruFH-qDn_APgPSKuAk`, fim STOP, 17.165 tokens. Uma consulta, com o documento sintético inteiro, sem ferramentas, testes nem fontes externas. Sugestões 1 e 5 incorporadas com restrição; 6 e 3 corrigidas; 2 recusada. |

**Tratamento dos achados** (esta versão; os testes continuam especificados; as contas marcadas "executado" rodaram no script de conferência do Claude, não no `entrega.js`, no CAL-01 nem no navegador):

| # | Achado (sev.) | Tratamento |
|---|---|---|
| 0 | Título "Decisões dos agentes" antes dos aceites | **Aceito.** Passa a "Propostas (valem depois dos aceites)", sem ampliar fila nem autoria. |
| 1 | Regeneração lia a necessidade já abatida pela própria programação e podia recriar o pedido ou apagar a dívida (S2) | **Aceito**, com a sugestão G1 sob a mesma restrição. A simulação exclui só as previsões abertas desta programação e preserva recebimentos reais, compromissos de outros pedidos e a quantidade contratada. Ela só reposiciona o saldo aberto. Cada saldo aberto mantém o vínculo com a necessidade de origem (versão e destino). Repetir sem mudança não muda nada. Propostas 1, 4 e 10; E12 e E18 (executado). |
| 2 | Capacidade calculada por item e pela necessidade líquida, sem ocupação física no tempo (S2) | **Aceito.** A ocupação do local é física e datada: estoque apto, reservado e quarentena, mais todas as chegadas de todos os pedidos e itens, menos os usos planejados identificados. Reserva não libera espaço. A sugestão G6 tratava o fim da janela como saída e foi corrigida: o fim da janela não é uso nem saída. A confirmação e a chegada revalidam o estado atual, serializadas por local. Sem capacidade, fica a pendência "capacidade não informada", sem proibição nova. Proposta 4; E4 e E4b (executado). |
| 3 | "NF de outra fazenda" e "Receber aqui" no mesmo caminho; a chegada errada ia direto ao apto (S2) | **Aceito.** Dois caminhos. A nota de outra fazenda não se vincula e nada entra. A chegada física divergente é registrada como fato, fica segregada, fora do apto e da cobertura, e espera inspeção e a decisão da alçada vigente (liberar aqui, transferir ou devolver). A transferência tem saída, trânsito e chegada, ligada ao pedido. **Recusada a G2** (senha ou liberação por terceiro): a alçada vem da permissão no servidor. Proposta 8; E16 e E16b. |
| 4 | "Cancelado" estava na fórmula, mas faltavam a transição e o efeito na previsão (S2) | **Aceito.** Reaproveita aditivo, cancelamento e divergência já previstos (SU-05, SU-06, RF-SUP-006), com autorização e recibo, sem tela nova. Cancelar o saldo remove só a previsão cancelada, e a falta é recalculada por data. Replay não duplica, e a 2ª conferência legítima da mesma linha soma só o complemento. Novas situações: "Encerrada parcial" e "Cancelada". Propostas 7 e 9; E10 e E11 (executado). |
| 5 | O link podia mostrar o rascunho do comprador; a confirmação não citava a versão (S2) | **Aceito**, com a sugestão G5 e recuperação. O link lê a última versão enviada; "Enviar" publica a versão e o recibo de uma vez. A confirmação cita a versão e as entregas mostradas. A rejeição por concorrência guarda a intenção e mostra as diferenças, sem recarregar e apagar a edição. Histórico e entregas recebidas não mudam. Propostas 6 e 11; E14 e E19. |
| 6 | Calendário implícito; o guloso prometia o mínimo de caminhões | **Aceito.** Dias corridos, data civil no fuso da fazenda, interseção com os dias de recebimento e com a chegada viável. Janela vazia é conflito recuperável, nunca adiada em silêncio. O guloso dá o mínimo só em intervalos sem outras restrições, e o desempate é fixo. "Confirmar entregas" mostra datas e versão no próprio lugar. Propostas 2 e 4; E8 e E8b (executado). |
| 7 | NR-31 lida como capacidade física "L/kg" (a sugestão G3 também estava imprecisa) | **Aceito.** O 31.7.16 é um critério regulatório conjunto (litros mais quilos ≤ 100) só para o armário. Não converte L em kg nem cria total físico. As grandezas ficam separadas, e a regra é nomeada com fonte e versão. A capacidade física declarada também vale, e a classe do local não prova os requisitos do 31.7.14. Nenhuma linha de total soma unidades ou produtos diferentes. Conferido no PDF oficial pelo Codex (págs. 22–23 na contagem dele) e pelo Claude com `pdftotext` (31.7.14 começa na pág. 23 e 31.7.16 está na 24, num arquivo de 81 páginas). Referência 5, proposta 4; E5 e E5b (executado). |
| 8 | Isolamento e escopo | **Aceito.** Mover quantidade exige permissão nas duas fazendas. O token cobre só pedido, contato e ações autorizadas, com expiração e revogação no servidor, e a nota fica restrita à entrega. O protótipo marca "Simulação", e o E7 visual não prova autorização no servidor. A P2 segue pendente no software real. Os IDs ficam estáveis, e filtros, rascunho e foco são preservados. Visões extras cortadas. Propostas 3, 4, 6 e 7; E6, E7 e E17. |
| R2-1 | O script de prova tirava do local a quantidade arredondada à embalagem e apagava a sobra (S2). Contraprova executada pelo Codex: local com 20 L, usos de 11 L e 20 L, galão de 20 L; o script aceitava 20 + 20 | **Aceito.** A simulação passou a ser diária e por item: sai o uso efetivo, a sobra fica no local e passa ao uso seguinte do item, e o estoque final é conferido. Novo E4c (29 L > 20 L, executado). E4 e E4b rodaram de novo sem mudança de número. Proposta 4 e §Contas conferidas. |
| R2-2 | A contraprova dizia "reprova" sem execução na base | **Aceito.** O texto passa a dizer o resultado esperado na base, sem declarar falha executada. |
| G1 | Gemini: regenerar a programação pela demanda | **Incorporada com restrição** (item 1). |
| G2 | Gemini: senha ou liberação por terceiro na chegada divergente | **Recusada** (Codex e Claude): a autorização é do servidor, pela permissão do usuário. |
| G3 | Gemini: regra de armazenagem da NR-31 | **Corrigida** (item 7). |
| G5 | Gemini: versão e concorrência no link | **Incorporada com recuperação** (item 5). |
| G6 | Gemini: tratar o fim da janela como saída na capacidade | **Corrigida** (item 2). |

## Situação em 16/10 (conferida no código)

Caminhos relativos a `tools/prototipo/v37/gen37/`.

| Parte | Hoje | Onde |
|---|---|---|
| Demanda por fazenda | **Pronta.** O CAL-01 de cada fazenda usa o estoque apto (com reservas), os recebimentos e a quarentena da própria fazenda; estoque de outra fazenda não cobre (DEM-07). Cada uso tem data e a falta líquida dele (`linhas[].nec`) | `cal01.js:11-49`, `cal01.js:113-115`, `dados2.py:155` |
| Data de necessidade | Só "1º uso" e "Falta em". Não há antecedência por item; a chegada viável é uma só para tudo (hoje + 7 dias) | `dados2.py:1250`, `dados2.py:1253-1255` |
| Envio a Compras | Uma solicitação por fazenda. "Enviar as N fazendas" manda N solicitações separadas; a soma por insumo das fazendas existe só para leitura | `safra_grupo.js:3-6`, `:105-126`, `:129-142`; `safra.js:976-982`, `:2038` |
| Compra | Um processo por safra de uma fazenda; o contexto mostra uma fazenda só | `areas/processo_compras.py:638` |
| Pedido | Um por fornecedor, com **uma data só** (hoje + maior prazo) e **sem fazenda nem local** | `processo_compras.py:375-376`, `:573`; `dados2.py:859-863` |
| Entregas (etapa 6) | Lista por pedido. Reprogramar muda a data do pedido inteiro. "Confirmar fornecedor" é clicado pelo comprador (simulado) | `processo_compras.py:185-191`, `:605-611`, `:704-706` |
| Recebimentos previstos na demanda | Todos atribuídos à Santa Rita | `dados2.py:949` |
| Recebimento por NF | O local sai de uma lista de todos os locais (padrão Galpão 2); a tela é da Santa Rita | `areas/processo_estoque.py:21`, `:95`, `:169` |
| Programação de entregas (SU-05) | Cargas por item, depósito e mês, todas em depósitos da Santa Rita; módulo fora do menu | `areas/suprimentos.py:2`, `:630-651` |
| Portal do fornecedor (PT-05det) | Cargas com data e placa; frete "CIF Galpão 2"; nada por fazenda; módulo fora do menu. Convite e confirmação simulados | `areas/parceiros.py:2`, `:405`, `:409-418`; `processo_compras.py:166`, `:712` |
| Cadastro da fazenda | Sem endereço de entrega, horário de recebimento nem recebedor | `dados_cad.py:13-17` |
| Locais | Cada local já pertence a uma fazenda. Capacidade só em tanque e silo; sem classe de armazenagem | `dados_cad.py:198-200`; `dados2.py:1048` |
| Embalagem de entrega | Já existe por item (galão 20 L, saco 25 kg, big bag) | `dados_cad.py:164` |

**Lacuna central:** a demanda nasce certa por fazenda e data, e a compra perde a fazenda. O pedido não sabe para onde nem quando entregar cada parte.

## Referências (AGENTS §3.3), consultadas em 16/10/2026

| # | Fonte oficial | O que diz | Decisão |
|---|---|---|---|
| 1 | SAP S/4HANA, scheduling agreement: [learning.sap.com, "Working with Scheduling Agreements"](https://learning.sap.com/courses/purchasing-in-sap-s-4hana/working-with-scheduling-agreements) (sem data na página) | A quantidade total do item é dividida em parcelas, cada uma com data própria. O acordo é "always plant-specific", e a liberação avisa o fornecedor | **Adaptar.** Total por item, com parcelas por fazenda (fazenda = planta). Diferente do SAP, **um pedido cobre várias fazendas**, para não dividir o volume da negociação |
| 2 | Oracle Fusion Procurement: [Purchasing Document Line Locations](https://docs.oracle.com/en/cloud/saas/procurement/25c/oadpr/PurchasingDocumentLineLocationExtractPVO.html) e [What's New 25C, mudança de pedido pelo fornecedor](https://docs.oracle.com/en/cloud/saas/readiness/scm/25c/proc25c/25C-procurement-wn-f38414.htm) (atualização 25C) | Cada programação do pedido tem local de entrega, data pedida (*need-by*) e data prometida (*promised*). O fornecedor pode dividir a programação "to stagger deliveries", e a mudança fica pendente de aprovação do comprador | **Adotar.** Data pedida e data prometida são campos separados. A proposta do fornecedor só vale com a decisão do comprador |
| 3 | SAP Business Network: [learning.sap.com, "Exploring Ship Notice Transaction Integration"](https://learning.sap.com/courses/configure-sap-business-network-proxy-integration/exploring-ship-notice-transaction-integration) (sem data) | O fornecedor envia o aviso de embarque quando está pronto para embarcar; cancelar o aviso apaga a entrega prevista. A rede não tem tolerância de horário nesse aviso | **Adotar** "Avisar embarque" por entrega. A janela de data é nossa |
| 4 | Senior Sistemas, dona do GAtec: [F420PEN, Programação de Entregas de Ordem de Compra](https://documentacao.senior.com.br/gestaoempresarialerp/5.10.4/menu_suprimentos/f420pen.htm) (ERP 5.10.4) e [Necessidade de compras](https://documentacao.senior.com.br/gestaoempresarialerp/7.0.0/backoffice/suprimentos/gestao-compras/necessidade-compra.htm) (7.0.0) | A F420PEN emite ordem de compra com entregas semanais, quinzenais ou mensais. A Necessidade de compras agrupa por empresa, filial, fornecedor e depósito; a cotação só junta necessidades da mesma filial | **Adaptar:** as datas vêm do uso no plano, não de um período fixo. **Descartar** a cotação separada por filial, que perde volume. **Adotar** a separação por destinatário na nota fiscal (P2). A busca de 16/10 não achou documentação pública de entrega por fazenda no GAtec, no TOTVS Agro nem no Siagri |
| 5 | [NR-31, gov.br/MTE](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/nr-31-atualizada-2024-1.pdf) (redação da Portaria SEPRT 22.677/2020; última alteração na Portaria MTE 342/2024) | **31.7.14:** edificação própria para agrotóxicos e afins, com acesso restrito, ventilação e placas, a mais de 15 m de habitações e de alimentos. **31.7.15:** estrados, longe de paredes e teto. **31.7.16:** "até o limite de 100 (cem) litros ou 100 (cem) quilos, ou a somatória de litros e quilos considerados conjuntamente", em armário exclusivo e trancado. **31.7.17:** transporte em recipiente rotulado e fechado. A ABNT NBR 9843-3:2019 (armazenamento em propriedades rurais) consta do catálogo; o texto é pago e **não foi lido** | **Adotar:** defensivo ou afim só vai a local dessa classe. No armário vale o critério regulatório conjunto do 31.7.16 (L + kg ≤ 100), nomeado com fonte e versão. Não é conversão física nem capacidade do local: a capacidade declarada também vale. A classe do local não prova os demais requisitos do 31.7.14 |
| 6 | Meta, WhatsApp Business Platform: [Message templates](https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates/) (sem data) | Fora da janela de atendimento, só a mensagem modelo chega ao destinatário. As categorias são autenticação, marketing e utilidade, e a categoria entra no preço | **Adiar** o envio real (custo e conta: P1). No protótipo, o link é simulado |

Estar num sistema do mercado não prova a regra de domínio. As travas daqui nomeiam o dano que evitam.

## Propostas (valem depois dos aceites)

1. **A demanda vem do plano efetivo de cada fazenda.**
   - O plano efetivo é a versão publicada do plano agronômico com os ajustes do agrônomo no talhão (PRD 40.3). A conta é o CAL-01 da fazenda.
   - **Nenhuma fórmula nova** (ENG-011): a programação lê as linhas do CAL-01 (`nec` por data de uso).
   - Cada linha leva fazenda, talhão, atividade, versão do plano e data de uso (RN-003, 44.1).
   - Comprar não autoriza aplicar. A O.S. continua com aprovação individual (PRD 41), e a reserva continua na liberação (CMD-06, PRD 42).
   - **A programação não se reconstrói pela própria sombra.**
     - Depois de emitido o pedido, as entregas abertas entram no CAL-01 da fazenda como previsão.
     - Para simular uma reprogramação, o cálculo exclui **só as previsões abertas desta programação**. Ficam os recebimentos reais, as previsões de outros pedidos, as reservas e a quantidade contratada.
     - A simulação só reposiciona no tempo o **saldo aberto** (programado − recebido conferido − cancelado). Não recria o pedido nem apaga dívida porque a necessidade caiu a zero.
     - Cada saldo aberto mantém o vínculo com a necessidade de origem: versão do plano, fazenda, talhão e uso.
     - Repetir o cálculo sem mudança na entrada devolve a mesma lista e as mesmas quantidades. A proposta só aparece quando há diferença (E18).
2. **Data de necessidade por item.**
   - Cada item tem duas antecedências, que definem a janela de cada uso: `[uso − máxima, uso − mínima]`, nunca antes da chegada viável do fornecedor escolhido (data do pedido + prazo dele).
     - **Mínima:** chegar até N dias antes do uso (conferência, laudo, tratamento de semente).
     - **Máxima:** não chegar antes de M dias do uso (validade, conservação, espaço).
   - **Calendário do contrato:**
     - antecedência, janela e prazo do fornecedor contam em **dias corridos**. Prazo em dias úteis fica fora do escopo até existir calendário de feriados;
     - toda data é **data civil local** da fazenda de destino, no fuso dela (CD-01), sem hora. O horário de recebimento aparece com o fuso;
     - a janela usada é a interseção com os **dias de recebimento** da fazenda (dias da semana e datas sem recebimento, informados no cadastro) e com a chegada viável. O início é o primeiro dia de recebimento; o fim é o último dia de recebimento até `uso − mínima`;
     - **janela vazia é conflito recuperável**, com o motivo (prazo do fornecedor ou dia sem recebimento) e as saídas: antecipar com o fornecedor, outro fornecedor, aceitar fora com justificativa ou o agrônomo rever o uso. Nunca se adia em silêncio para depois do "entregar até" (E8b).
   - O padrão é por grupo, com valores de demonstração editáveis no item (RN-043; P3):

     | Grupo | Mínima | Máxima |
     |---|---|---|
     | Sementes | 10 dias | 45 dias |
     | Fertilizantes e corretivos | 5 dias | 60 dias |
     | Defensivos e adjuvantes | 5 dias | 30 dias |
     | Inoculantes e biológicos | 2 dias | 10 dias |

   - "Entregar até" aparece no Planejar safra (etapa 4), ao lado de "Falta em".
3. **Uma compra para a safra inteira.**
   - A safra de várias fazendas (SAF-FAZ-2) abre uma compra só. A cotação, a comparação, a aprovação e o pedido usam o total; o pedido continua sendo um por fornecedor.
   - As solicitações continuam uma por fazenda, com identidade, versão e DEM-09 intactos; a compra soma essas solicitações por item.
   - Safra de uma fazenda: a mesma tela, com uma coluna de fazenda.
   - **Na demonstração**, S2627 (Santa Rita) e LG2627 (Lagoa Grande) passam a sub-safras da mesma safra-mãe. O grupo leva o nome da primeira, "Safra 2026/27"; IDs, cultivos e solicitações não mudam.
   - A negociação agrupada **não decide destinatário fiscal** nem cria empresa para fazenda sem cadastro. Isso é a P2, pendente no software real.
4. **Programação de entregas por fazenda: o centro do pedido.**
   - **Entrega programada** = fornecedor + fazenda + janela. Cada linha da entrega tem item, quantidade, embalagens e local de recebimento.
   - **Montagem sugerida** (determinística: a mesma entrada dá a mesma saída):
     1. Por fazenda, cada uso com falta (`nec`) vira uma necessidade com janela (proposta 2).
     2. As necessidades são ordenadas pelo fim da janela; o desempate é o uso, depois o item, depois o ID. A entrega fecha no fim da primeira e leva todas as que começam até essa data, de qualquer item do mesmo pedido. A janela da entrega é o cruzamento das janelas. Esse guloso dá o menor número de entregas **só** em intervalos sem outras restrições. Com capacidade, locais e embalagens, não promete mínimo de caminhões.
     3. Cada linha arredonda para embalagem inteira. A sobra cobre o uso seguinte do item (PRD 65.5), e a diferença aparece ("arredondamento +10 L"), nunca some.
     4. **Capacidade física no tempo:**
        - a ocupação do local em cada dia soma o estoque físico (apto, reservado e quarentena), as chegadas de **todos** os pedidos e itens com destino a ele e tira os usos planejados identificados (O.S. e plano) até o dia anterior;
        - sai do local o **uso efetivo**, nunca a quantidade arredondada à embalagem. A sobra de embalagem fica no local e passa ao uso seguinte do mesmo item, e o estoque final, depois do último uso, também é conferido (E4c);
        - no mesmo dia, a chegada conta antes do uso, como no CAL-01. O pico do dia é que se compara;
        - reserva não libera espaço (RN-011). O fim da janela não é uso nem saída;
        - chegada sem data prometida conta desde o primeiro dia da janela (o caso mais cheio);
        - se a entrega não cabe, sai dela a necessidade de fim mais tardio (mesmo desempate), que começa no primeiro dia de recebimento em que cabe. Se esse dia passa do fim da janela, vira conflito com local, data, pico e limite;
        - **nunca corta quantidade nem adia em silêncio** (65.5);
        - cada grandeza tem a sua capacidade (L, kg, un), sem conversão. No local do tipo armário de defensivos vale também a regra regulatória nomeada **NR-31 31.7.16** (L + kg ≤ 100, critério conjunto da norma, com fonte e versão), que não é conversão física;
        - capacidade em branco é a pendência explícita "capacidade não informada": nem zero, nem infinita, nem "aprovada" (65.5.1). Não bloqueia, não cria proibição nova e aparece na entrega;
        - a confirmação do fornecedor e a chegada revalidam no servidor o estado físico atual do local, **uma por vez por local**. Duas confirmações simultâneas não ocupam o mesmo espaço: a segunda vê a primeira (E4b).
   - **Invariantes** (o servidor confere a cada comando; o dano evitado vem entre parênteses):
     - toda entrega tem fazenda e um local daquela fazenda (material na fazenda errada);
     - a soma das entregas do item é igual à quantidade do item no pedido, e, por fazenda, a soma das entregas é igual à parcela da fazenda (comprar ou cobrar diferente do entregue);
     - linha de defensivo ou afim só vai a local dessa classe (NR-31 31.7.14: defensivo junto de alimento ou de semente). A classe do local é declaração do cadastro e não prova os demais requisitos do 31.7.14; o sistema não afirma conformidade;
     - quantidades de produtos ou unidades diferentes nunca viram uma quantidade só. Totais de quantidade são por item; a linha de total da tela soma só valor (R$) (RN-033).
   - **Sempre total e por fazenda lado a lado, por item:** colunas Total, Fazenda A, Fazenda B…; em cada item, o Total confere a soma das fazendas.
   - O comprador pode mudar janela ou local, ou mover quantidade de um item entre fazendas sem mudar o total.
     - Mover exige permissão do comprador nas **duas** fazendas, conferida no servidor.
     - Cada mudança revalida invariantes e capacidade.
     - Quando mexe no que o fornecedor já confirmou, volta a pedir o aceite dele.
     - Quando deixa uma fazenda abaixo da necessidade, avisa com a falta resultante e pede o motivo.
5. **A cotação já sai com destinos.** O convite leva o total e a divisão por fazenda, com janelas e municípios. A proposta informa prazo e frete (CIF ou FOB). A comparação mede "chega a tempo" por fazenda, pela primeira janela de cada uma, e não só pela primeira falta da safra (refina a DEM-08).
6. **Link do fornecedor** (a página do pedido do PT-05, reaproveitando a PT-05det).
   - **Acesso:**
     - um link por pedido e por contato do CD-05, enviado ao e-mail ou ao WhatsApp do cadastro;
     - tem finalidade e validade (até 30 dias depois da última entrega) e pode ser revogado (FL-26, RN-039). Expiração e revogação são decididas no servidor;
     - o token só alcança aquele pedido, aquele contato e as ações autorizadas. A nota enviada só se vincula à entrega em que foi enviada.
   - **Versão mostrada:**
     - o link lê sempre a **última versão enviada** da programação; o rascunho do comprador nunca aparece como programação oficial;
     - cada confirmação ou proposta cita a versão e as entregas exatas que foram mostradas;
     - versão nova não apaga aceite anterior nem histórico, e não muda entrega já recebida.
   - **Abre direto no pedido:** Total e por fazenda lado a lado, sem outro clique. Abaixo, as entregas agrupadas por fazenda, cada uma com:
     - endereço e coordenadas;
     - dias e horário de recebimento;
     - quem recebe (função e telefone da portaria);
     - restrição de veículo.
   - **Ações**, cada uma com a chave da intenção e um recibo:
     - Confirmar (todas ou por fazenda). As datas sugeridas, a versão e as entregas aparecem junto do botão; canceladas e recebidas ficam de fora; não há clique extra de rotina;
     - Propor outra data (por entrega, com data por atalho e motivo escolhido numa lista);
     - Avisar embarque (data, placa e número da NF-e);
     - Enviar NF-e;
     - Abrir divergência.
   - **Nunca aparecem:** outros pedidos, propostas ou fornecedores; preço de referência; demanda, estoque ou talhões; usuários da organização (EX-35; PT-06 no PR #75).
   - O comprador pode registrar uma confirmação recebida por telefone, com canal e pessoa (fato registrado, RN-018).
   - No protótipo, o envio é simulado, e a página do link mostra "Simulação" no topo; o token é o da demonstração. O E7 visual não prova autorização no servidor (§Testes). SU-05 e o portal continuam fora do menu: a programação fica na etapa 6 de Compras, uma solução só para o mesmo problema (§3.4).
7. **Gestão de entregas no sistema** (Compras, etapa 6 "Acompanhe as entregas").
   - **Lista agrupada por fazenda** por padrão (AGR-02), com as peças que já existem: Tabela | Cartões e Agrupar por Fazenda ou Fornecedor. Sem calendário nem outras visões extras.
   - **IDs estáveis:** entrega e solicitação mantêm o ID nas versões. A entrega dividida ganha sufixo e fica ligada à de origem (SR-1 → SR-1a e SR-1b). Abrir o detalhe preserva filtros, rascunho e foco, e a situação aparece em texto, não só em cor.
   - **Situações:** A enviar → Aguarda confirmação → Confirmada → Proposta do fornecedor → Embarcada → Recebida em parte → Recebida; também **Encerrada parcial** (saldo cancelado por aditivo ou cancelamento autorizado) e **Cancelada** (antes de qualquer recebimento). "Atrasada" (janela vencida sem recebimento) e "Conflito" (capacidade, prazo ou dia de recebimento) são marcas, não etapas.
   - **Pontualidade:** a data pedida (fim da janela) e a data prometida ficam separadas. A primeira promessa fica guardada para medir pontualidade, e reprogramar não apaga o atraso (RF-SUP-012).
   - **Reprogramar** vale para a entrega, não para o pedido inteiro, e exige motivo (lista curta e "Outro").
   - **Cobertura da demanda:**
     - entrega não confirmada cobre a demanda da fazenda como "a confirmar" (cobertura proposta, PCE-03);
     - entrega atrasada deixa de cobrir na data antiga, e a falta reaparece no Planejar safra e em Compras (RF-SUP-001).
8. **Recebimento na fazenda certa** (Estoque, com o filtro de Fazenda da DEC-2609-11).
   - **Nota × entrega:** a nota escolhe a entrega, e a lista só mostra entregas daquela fazenda.
   - **Parcial:** recebimento parcial mantém aberto o saldo da entrega (RF-SUP-006/007). A tolerância é a do item no pedido (DEC-0910-25 a; sem tolerância, 0 %), e a sobra fica bloqueada até a decisão.
   - **Conferência repetida:** replay do mesmo evento (mesma chave) não duplica. Uma 2ª conferência legítima da mesma nota e linha soma só o complemento autorizado, até a quantidade da nota; acima disso, vira sobra bloqueada.
   - **Cobertura:** só o conferido e apto entra no físico apto da fazenda que recebeu e cobre a demanda dela (DEM-07). Material em quarentena cobre de forma condicionada (65.4).
   - **Dois caminhos distintos para o que não bate:**
     - **Documento de outra fazenda** (nota de uma entrega programada para outra fazenda, sem chegada física aqui): o vínculo é recusado, com o nome da fazenda certa (EX-35). Nada entra.
     - **Chegada física divergente** (o caminhão de uma entrega de outra fazenda descarrega aqui): o padrão é Recusar a descarga. Se o material fica, o almoxarife registra **"Chegada fora da programação"**: é o fato, não um recebimento regular (RN-018).
       - O material fica **segregado**, fora do apto e da cobertura, num local revalidado por fazenda, classe e capacidade. Se o local é incompatível, a descarga não é registrada como guardada ali.
       - A entrega programada continua aberta na fazenda de destino, e a demanda dela continua descoberta.
       - Depois da inspeção, a alçada vigente de estoque da fazenda que recebeu (hoje, o gestor; PEND-CTL-02, DEC-0910-25 b) escolhe uma saída. **Liberar aqui** troca o destino da entrega e pede o aceite do fornecedor. **Transferir** cria a transferência ligada ao pedido e à entrega originais (SU-08): saída aqui, em trânsito indisponível nos dois lados, chegada conferida no destino (CAL-02). A previsão da entrega vira a chegada da transferência, sem duplicar o previsto nem o físico. **Devolver ao fornecedor** abre divergência.
       - O financeiro (título e divergência comercial) segue separado (RN-028).
       - Quem não tem a alçada registra a chegada, mas não libera para apto nem transfere. A tela mostra o responsável (RN-045). Não existe senha nem liberação por terceiro.
       - O fato da chegada e a pendência nunca se perdem: ficam na lista da fazenda até a decisão.
   - **D5** (DEC-1610-01) vale para peça de ordem de manutenção. No insumo agrícola, o vínculo da chegada é a fazenda; a reserva para a O.S. continua na liberação (P5).
9. **Conciliação de pedido, entregas e notas**, por item e por fazenda.
   - **Saldos:**
     - o pedido é a soma das entregas;
     - o recebido conferido sai de cada nota, por entrega;
     - saldo a entregar = programado − recebido conferido − cancelado (CAL-03).
   - **Divergência:** diferença entre nota, entrega e conferido abre divergência com dono e bloqueia o título correspondente (RF-SUP-011; DEC-0910-25 a). O financeiro é separado do físico (RN-028).
   - **Saldo que não vem:** depois de um recebimento parcial, o saldo continua aberto até uma destas saídas:
     - **Aguardar o saldo:** continua a mesma entrega, ou uma nova data com motivo.
     - **Encerrar parcial:** o cancelamento do saldo usa o aditivo ou o cancelamento já previstos (SU-05: volume só muda por aditivo aceito pela contraparte; RF-SUP-006: alteração relevante pede reaprovação), com autorização e recibo, sem tela nova.
   - **Efeito do cancelamento:** remove só a previsão cancelada. A falta real é recalculada por data no CAL-01 da fazenda, e não se afirma que falta o mesmo número cancelado: pode haver estoque, reserva ou uso diferente (E11).
10. **Mudança de plano vira reprogramação proposta, nunca silenciosa.**
    - **Mudança de data:** nova versão do plano, data de plantio ou dose muda a demanda da fazenda (DEM-09).
      - A simulação segue a proposta 1: sem as previsões abertas desta programação, só com o saldo aberto.
      - A entrega afetada mostra ⚠ com o antes e o depois ("uso de 25/10 passou a 12/10: chegar até 07/10") e a ação "Propor reprogramação".
      - Entregas não afetadas e já recebidas não mudam.
    - **Aumento:** vira complemento pela solicitação da fazenda (DEM-09), ou move quantidade do mesmo item de outra fazenda. Nunca muda o pedido sozinho (40.3, PCE-11).
    - **Redução com pedido emitido:** nada baixa sozinho (`cal01.js:194-197`). A linha mostra "acima da demanda" e as saídas: mover para outra fazenda ou negociar aditivo com o fornecedor.
11. **O servidor é a autoridade** (AGENTS §4; PRD 24).
    - Saldos, reservas, invariantes da programação e recebimentos são decididos pelo servidor.
    - Cada comando leva a chave de idempotência de quem inicia e a versão esperada da programação (73.3; ENG-021/022). Os comandos são: emitir pedido com programação, enviar programação, confirmar, propor data, decidir proposta, avisar embarque, mover entre fazendas, reprogramar, encerrar parcial, cancelar, registrar chegada fora da programação, decidir chegada e receber.
    - **Rascunho e versão enviada:** o comprador edita um rascunho, que só ele vê. "Enviar programação" publica a versão nova e o recibo de uma vez, na mesma transação da saída (outbox).
    - **Concorrência sem perda:** comando com versão velha é recusado sem sobrescrever nada.
      - A recusa guarda a intenção de quem agiu (datas, motivo, rascunho) e mostra as diferenças entre a versão vista e a atual.
      - Oferece repetir a mesma intenção sobre a atual, sem recarregar a tela e apagar a edição.
    - A ocupação do local é revalidada uma por vez por local (proposta 4). As permissões por fazenda e o escopo do token são do servidor.
    - Efeito, recibo e saída (outbox) gravam na mesma transação. Quantidades em decimal, com unidade (ENG-013, RN-033).

## Telas

Master-detail, uma primária por tela. DS (cap. 74) no padrão das telas de processo do módulo Agrícola (Planejar safra), que Compras já usa: ETP-02, TAB-08 (⇅ e funil por coluna, seta de abrir), VIS-06, AGR-02, FIL-01 (faixa de filtros pela peça comum), TAB-05/06, BOT-01 (verbo + objeto, um verde por contexto) e AVI-01.

| Tela | O que muda | Primária |
|---|---|---|
| Planejar safra › etapa 4 | Coluna "Entregar até" por fazenda. A faixa das fazendas (FIL-01) já existe | "Enviar as N fazendas para cotação" (existente) |
| Compras › etapa 1 | A safra de várias fazendas é uma linha, com as fazendas e as solicitações de cada uma | Abrir compra |
| Compras › etapa 2 | Demanda em matriz: Item · Total · uma coluna por fazenda (quantidade e "entregar até"). Em cada item, o Total confere a soma das fazendas; a linha de total soma só valor (R$) | (existente) |
| Compras › etapas 3 e 4 | O convite mostra total e fazendas com janelas. A comparação marca "chega depois" por fazenda | (existentes) |
| Compras › etapa 6 (lista) | Entregas agrupadas por fazenda, com totais só por item. Faixa FIL-01 com Fazenda (chips com contagem: "Todas 3 · Santa Rita 1 · Lagoa Grande 2"), Situação e Fornecedor. Tabela \| Cartões; Agrupar por Fazenda ou Fornecedor. Selo da versão: "Rascunho · v3 enviada" | "Enviar programação ao fornecedor" enquanto o rascunho for diferente da versão enviada |
| Detalhe da entrega (painel) | Fazenda, local, endereço e janela; linhas e embalagens; classe e capacidade (ou "capacidade não informada"); usos que a entrega cobre (talhão, atividade, data e versão do plano, com link ao Planejar safra); histórico de datas e versões; notas fiscais. "Encerrar parcial" e "Cancelar" ficam no ⋯ (TAB-05) | Pela situação: "Aceitar data proposta", "Reprogramar entrega" ou "Receber na fazenda" |
| Detalhe do pedido (painel) | Matriz Total × fazendas por item, com a soma conferida; entregas e conciliação com as notas | Enviar programação |
| Link do fornecedor (PT-05det) | Selo "Simulação" no protótipo. Topo: Total e por fazenda, por item, da última versão enviada. Abaixo: entregas por fazenda, com endereço, dias e horário de recebimento (com o fuso) e recebedor | Confirmar entregas (datas sugeridas e versão à vista) |
| Estoque › Confira recebimentos | Bloco "Chegam nesta fazenda" (entregas confirmadas ou embarcadas da fazenda do filtro); a nota escolhe a entrega. Secundária "Registrar chegada fora da programação"; a lista "Chegadas fora da programação" fica até a decisão da alçada | Receber |
| Cadastros | Fazenda: "Recebimento de insumos" (endereço, coordenadas, dias da semana, datas sem recebimento, horário, recebedor, restrição de veículo). Local: classe de armazenagem, tipo (armário de defensivos ou não) e capacidade por grandeza. Item: antecedência mínima e máxima | Salvar (existente) |

- **Celular (390 px):**
  - Cartões (VIS-06), um por item, com uma linha de Total e uma por fazenda;
  - a matriz rola dentro da tabela, com Item e Total fixos, e a página não rola de lado;
  - situação em texto e alvos de 44 px.
- **Cliques** (§3.3, contados no teste):
  - o fornecedor confirma tudo com 2 cliques: abrir o link e "Confirmar entregas". As datas sugeridas (o primeiro dia de recebimento de cada janela), a versão e as entregas já estão à vista junto do botão;
  - propõe uma data com 4 (Propor data, atalho de data, motivo, Enviar);
  - o comprador envia a programação com 1 clique a partir da etapa 6.

## Dados de exemplo (sintéticos)

**S1.**
- **Contexto:** hoje é 23/09/2026. O fornecedor é a Santa Rita Insumos (F04), com prazo de 7 dias (chegada viável em 30/09).
- **Itens:** Óleo mineral e Glifosato 480, ambos em galão de 20 L.
- **Antecedência** de defensivos e adjuvantes: de 5 a 30 dias.
- **Estoque apto** desses itens: 0 nas duas fazendas.
- **Calendário:** as duas fazendas recebem todos os dias, e a capacidade dos locais não está informada (pendência visível). As variações E4, E4b e E8b mudam só isso.

| Fazenda | Item | Usos (data · necessidade líquida) | Local |
|---|---|---|---|
| Santa Rita | Óleo mineral | 25/10 · 120 L; 12/11 · 90 L | Almox. defensivos |
| Santa Rita | Glifosato 480 | 05/11 · 20 L | Almox. defensivos |
| Lagoa Grande | Óleo mineral | 30/10 · 400 L; 20/11 · 230 L | Almox. Lagoa Grande |
| Lagoa Grande | Glifosato 480 | 25/10 · 293,34 L | Almox. Lagoa Grande |

Programação esperada (montagem da proposta 4):

| Entrega | Fazenda | Janela | Linhas |
|---|---|---|---|
| LG-1 | Lagoa Grande | 30/09–20/10 | Glifosato 300 L (15 galões); Óleo 400 L (20 galões) |
| SR-1 | Santa Rita | 13/10–20/10 | Óleo 220 L (11 galões); Glifosato 20 L (1 galão) |
| LG-2 | Lagoa Grande | 21/10–15/11 | Óleo 240 L (12 galões) |

**Pedido PC-101:**

| Item | Total | Santa Rita | Lagoa Grande |
|---|---|---|---|
| Óleo mineral | 860 L | 220 L | 640 L |
| Glifosato 480 | 320 L | 20 L | 300 L |

O arredondamento fica visível: Óleo +20 L (10 L em cada fazenda) e Glifosato +6,66 L (Lagoa Grande).

## Aceite

| ID | Caso | Oráculo |
|---|---|---|
| E1 | "Entregar até" no Planejar safra | Santa Rita · Óleo: 20/10 (uso 25/10 − 5 dias). Lagoa Grande · Óleo: 25/10. Lagoa Grande · Glifosato: 20/10. Com antecedência mínima de 10 dias, Santa Rita · Óleo passa a 15/10 |
| E2 | Compra única da safra de 2 fazendas | Etapa 1: uma linha "Safra 2026/27" com as duas fazendas e as duas solicitações. Etapa 2, com S1: Óleo 840 L = 210 + 630 e Glifosato 313,34 L = 20 + 293,34, lado a lado. Na demonstração, em todos os itens o Total é a soma das fazendas. A linha de total soma só valor (R$), nunca quantidades de itens diferentes |
| E3 | Programação sugerida (S1) | Exatamente LG-1, SR-1 e LG-2, com as janelas e embalagens da tabela. Arredondamento visível (+20 L e +6,66 L). Rodar duas vezes dá o mesmo resultado |
| E4 | Capacidade no tempo (S1 só com o Óleo da Lagoa Grande; Almox. Lagoa Grande com 500 L) | Duas entregas: 400 L em 30/09–25/10 e 240 L em 31/10–15/11. Em 30/10 a chegada conta antes do uso: 640 L > 500 L. Com 300 L: conflito "400 L > 300 L no Almox. Lagoa Grande em 25/10", nada cortado, e a de 240 L em 31/10–15/11. Com 500 L e 150 L em quarentena no local: conflito "550 L > 500 L" (quarentena e reserva ocupam espaço). Capacidade em branco: pendência "capacidade não informada", sem conflito e sem "aprovada" |
| E4b | Duas chegadas antes do consumo e concorrência (S1 completo; Lagoa Grande com 500 L) | Glifosato 300 L (30/09–20/10, uso em 25/10) e Óleo 400 L (até 25/10, uso em 30/10) estariam juntos no local em 25/10: 700 L > 500 L. Sai o Óleo (fim mais tardio) e não há dia que caiba até 25/10: conflito recuperável "pico de 700 L > 500 L em 25/10", nada cortado nem adiado. O Glifosato fica em 30/09–20/10 e a de 240 L em 31/10–15/11. Dois fornecedores confirmam ao mesmo tempo 400 L e 300 L para o mesmo local antes do consumo: a primeira grava; a segunda é recusada com o pico de 700 L > 500 L e continua como proposta |
| E4c | A sobra de embalagem ocupa espaço (contraprova do Codex) | Local com 20 L; Óleo com usos de 11 L em 20/10 e 20 L em 20/11; galão de 20 L; físico 0. A 1ª entrega é de 20 L, em 30/09–15/10, e depois do uso sobram 9 L no local. A 2ª precisa de 11 L e chega como 20 L: 9 + 20 = 29 L > 20 L, conflito recuperável, nada cortado. O estoque final (9 L em 21/11) também é conferido |
| E5 | Classe de armazenagem | Levar a linha do Óleo da SR-1 para "Galpão 2" ou "Câmara fria" é recusado ("adjuvante: só em local de defensivos e afins, NR-31 31.7.14"). Local de outra fazenda é recusado. Nada muda. A classe do local não vale como atestado dos requisitos do 31.7.14 |
| E5b | Critério regulatório do armário (NR-31 31.7.16) | Armário de defensivos na Lagoa Grande com 60 L de Óleo e 50 kg de Acetamiprido 200 SP: conflito "NR-31 31.7.16: 60 L + 50 kg = 110 > 100". As quantidades ficam em L e kg, separadas, sem conversão. Se o armário declara capacidade de 80 L, ela também vale. Nenhuma tela mostra "110" como quantidade de estoque |
| E6 | Invariantes, mover entre fazendas e permissão | Entrega sem fazenda é recusada. Mover 100 L de Óleo da LG-2 para a SR-1 deixa Santa Rita com 320 L e Lagoa Grande com 540 L; o total continua 860 L; a LG-2 aparece com a falta de 90 L e pede motivo; SR-1 e LG-2 voltam a "Aguarda confirmação". Reduzir só a SR-1 sem aditivo é recusado ("o total mudaria de 860 para 760 L"). Comprador com permissão só na Santa Rita: mover é recusado no servidor ("sem permissão na Lagoa Grande") e nada muda |
| E7 | Link do fornecedor (1 clique, sem exposição) | Ao abrir o link do PC-101, a página mostra "Simulação", o Total (860 e 320 L) e cada fazenda (Santa Rita 220 e 20 L; Lagoa Grande 640 e 300 L), mais as 3 entregas por fazenda com endereço, horário e recebedor. O texto da página não tem: usuários da organização (Ana, Marcos, Rui, Paula, Carlos), outros fornecedores, "SOL-", estoque, talhões, preço de referência. Trocar o pedido no endereço, ou usar link vencido ou revogado: "Este link não dá acesso a este pedido", sem dado nenhum. A nota enviada pelo link só se vincula à entrega em que foi enviada. Este caso é visual: a autorização do token no servidor é teste do software real (§Testes) |
| E8 | Confirmar e propor por fazenda | Junto do botão aparecem v1, as 3 entregas e as datas sugeridas; canceladas e recebidas ficam de fora. "Confirmar entregas" grava 30/09 (LG-1), 13/10 (SR-1) e 21/10 (LG-2), com a v1. Propostas para a LG-2 (janela 21/10–15/11; uso em 20/11): 28/10 fica "Proposta do fornecedor · dentro da janela"; 18/11 fica em âmbar, "depois do entregar até (15/11), antes do uso" (aviso ao gestor, P4); 20/11 fica em vermelho, "chega no dia do uso", e o aceite exige justificativa. Ao aceitar, a promessa passa à nova data, e a primeira (21/10) fica guardada para a pontualidade |
| E8b | Calendário e janela vazia | A proposta do E12 com a Santa Rita recebendo só segunda e sexta (dias corridos, data local) fica: Óleo 120 L (6 galões) em 25/09–05/10, e Glifosato 20 L com Óleo 100 L (5 galões) em 16/10–30/10. Janela vazia, pelo item de demonstração Nitrato de cálcio da Santa Rita (uso em 01/10, mínima de 5 dias, pedido em 23/09 com prazo de 7 dias): o "entregar até" é 26/09 e a chegada viável é 30/09. Resultado: conflito recuperável "o fornecedor chega em 30/09, depois do entregar até (26/09); uso em 01/10", com as saídas. Nada é adiado em silêncio |
| E9 | Aviso de embarque | O fornecedor avisa o embarque da LG-1 (placa QAS-2C41, NF-e 7001), e ela passa a "Embarcada". O Estoque com o filtro Lagoa Grande mostra a LG-1 em "Chegam nesta fazenda"; com o filtro Santa Rita, não mostra |
| E10 | Recebimento parcial na fazenda certa | A NF 7001 da LG-1 (Glifosato 300 L e Óleo 400 L) é conferida na Lagoa Grande com Glifosato 200 L e Óleo 400 L. Resultado: LG-1 "Recebida em parte", com saldo de 100 L de Glifosato; físico apto da Lagoa Grande +200 L de Glifosato e +400 L de Óleo, que cobrem a demanda dela; Santa Rita sem mudança. A mesma nota no Estoque da Santa Rita, sem material lá, tem o vínculo recusado ("NF 7001 é da entrega LG-1, Lagoa Grande"). Replay com a mesma chave não cria entrada. Uma 2ª conferência legítima da mesma linha com +100 L soma só o complemento (Glifosato 300 L, LG-1 "Recebida"); mais +50 L vira sobra bloqueada |
| E11 | Conciliação e encerramento parcial (a partir do E10, sem a 2ª conferência) | PC-101 · Glifosato: pedido 320 = programado 320 (20 + 300); recebido 200; saldo 120 (Santa Rita 20 e Lagoa Grande 100). NF 7001 com 300 L e 200 L conferidos abre a divergência "Falta 100 L", com dono, e bloqueia o título. "Encerrar parcial" da LG-1 (aditivo aceito pelo fornecedor, autorização e recibo): cancelado 100 L; LG-1 "Encerrada parcial"; Glifosato do pedido 320 → 220 (20 + 200), recebido 200, saldo 20 (Santa Rita). Sai só a previsão de 100 L, e a falta da Lagoa Grande em 25/10 vira 93,34 L (293,34 − 200), não 100. Replay do cancelamento devolve o mesmo recibo |
| E12 | Plano mudou a data (Santa Rita · Óleo: uso de 25/10 vira 12/10) | A simulação exclui só as previsões abertas do PC-101 na Santa Rita. A SR-1, já confirmada, mostra ⚠ "uso de 25/10 passou a 12/10: chegar até 07/10" e a proposta de dividir em SR-1a (Óleo 120 L e Glifosato 20 L, 06–07/10) e SR-1b (Óleo 100 L, 13/10–07/11), ligadas à SR-1. LG-1 e LG-2 não mudam (4 entregas). O total de Santa Rita continua 220 L de Óleo. Nada muda no pedido nem no fornecedor sem "Propor reprogramação" e o aceite dele; até lá, a demanda de Santa Rita mostra a falta em 12/10 |
| E13 | Plano mudou a quantidade | Dose maior em Santa Rita (+60 L de Óleo): o complemento da solicitação aparece em Compras e o PC-101 não muda; a SR-1 avisa "+60 L em Santa Rita: cotar complemento ou mover da Lagoa Grande". Redução de 100 L na Lagoa Grande com pedido emitido: nada baixa sozinho; a linha mostra "100 L acima da demanda" e as saídas |
| E14 | Idempotência e concorrência sem perda | Clicar duas vezes em "Confirmar entregas" grava um registro com o mesmo recibo. O fornecedor confirma sobre a v2 quando o comprador já enviou a v3: recusa "A programação mudou (v2 → v3)", com as diferenças (por exemplo, a LG-2 passou a 31/10–15/11) e as datas dele mantidas no formulário. "Confirmar sobre a v3" reaproveita a intenção, sem recarregar a tela. As confirmações da v2 ficam no histórico, e a LG-1 já recebida não muda. O mesmo vale para o rascunho do comprador recusado por concorrência. Reenvio com a mesma chave devolve o mesmo recibo |
| E15 | Atraso | Em 21/10, sem embarque da LG-1 (janela até 20/10), ela fica "Atrasada". A Lagoa Grande volta a mostrar falta de Glifosato em 25/10 e de Óleo em 30/10, e a pontualidade conta contra a promessa original |
| E16 | Caminhão na fazenda errada | A LG-1 (Glifosato 300 L e Óleo 400 L) chega à Santa Rita, e o padrão é Recusar a descarga. Se descarrega, o almoxarife registra "Chegada fora da programação": os 700 L ficam segregados no Almox. defensivos da Santa Rita (classe conferida; capacidade não informada, pendência). O apto da Santa Rita não muda, a LG-1 continua aberta e a Lagoa Grande continua com falta em 25/10 e 30/10. O gestor da Santa Rita escolhe "Transferir para a Lagoa Grande": saída na Santa Rita, em trânsito (indisponível nas duas), chegada conferida na Lagoa Grande (+300 L e +400 L aptos), ligada ao PC-101 · LG-1. Em nenhum momento os 700 L contam em dois lugares, e a previsão da LG-1 não soma com a da transferência. O título e a divergência com o fornecedor seguem à parte |
| E16b | Chegada divergente sem alçada | Paula (almoxarife) registra a chegada. "Liberar para apto" e "Transferir" mostram "decisão do gestor da Santa Rita", e o servidor recusa o comando dela. A chegada e a pendência continuam na lista "Chegadas fora da programação" depois de recarregar. Não existe senha nem liberação por terceiro |
| E17 | Celular, teclado e cliques | A 390 px, cada item mostra Total e fazendas, sem rolagem lateral da página, com a situação em texto e alvos de 44 px. Abrir e fechar o detalhe mantém filtros, rascunho e foco. O teclado faz todo o fluxo. Cliques contados no teste: o fornecedor confirma tudo com 2 e o comprador envia a programação com 1. Antes, não havia confirmação do fornecedor nem nada por fazenda |
| E18 | O saldo aberto não se reconstrói pela necessidade (a partir do E10) | Glifosato da Lagoa Grande: pedido 300 L, recebidos 200 L, abertos 100 L. A simulação sem as previsões abertas do PC-101 vê falta de 93,34 L em 25/10 e mantém a entrega de 100 L (5 galões); não recria 300 L. Se o plano reduz o uso da Lagoa Grande para 150 L (necessidade 0), os 100 L continuam abertos, "acima da demanda", e saem só por cancelamento ou aditivo (E11). Repetir o cálculo sem mudança devolve a mesma lista e as mesmas quantidades, sem proposta. O saldo aberto mostra a origem: versão do plano, Lagoa Grande e uso de 25/10 |
| E19 | Rascunho × versão enviada | O comprador muda a SR-1 para 15/10 no rascunho v4: o link continua na v3, e o selo diz "Rascunho · v3 enviada". "Enviar programação" publica a v4 e o recibo juntos; se a gravação falha, não existe nem v4 nem recibo, e o rascunho fica. A confirmação seguinte cita a v4, a SR-1 e 15/10 |

**Contas conferidas:**
- **Executado pelo Claude**, no script de conferência em Decimal com calendário: S1, E4, E4b, E4c, E5b, E8b, E11, E12 e E18, inclusive a repetição sem mudança. Não é o `entrega.js`, o CAL-01 nem o navegador.
  - O script e a saída estão em `docs/integracao/V71/entrega-faz/` (`entrega_chk.py` e `entrega_chk.out`, gerado com `python3 -I entrega_chk.py > entrega_chk.out`).
  - Depois do R2-1, a capacidade é simulada por item, com o uso efetivo, e E4 e E4b rodaram de novo com os mesmos números.
- **Executado pelo Codex:** S1, E6, E12 e a contraprova do E4c.
- **Só especificado:** o restante.

**Contraprova (resultado esperado, não executado):**
- Na base a685f5e não existem antecedência por item, compra única da safra, entrega por fazenda, link do fornecedor nem chegada fora da programação. Por isso se espera que E1 a E11 e E15 a E19 não passem quando o teste existir: as telas e os campos que eles procuram não estão lá.
- Não é falha executada de CAL-01 nem do produto real, que ainda não existe.
- A contraprova roda junto com `entrega_faz_test.py`, contra o render da base. Os aceites são propostos e viram teste depois dos aceites desta versão.

## Testes (proporcionais ao risco: estoque, demanda e dinheiro)

- **Unidade (`node entrega_faz_unit.js`):**
  - janela com calendário (dias corridos, data local, dias de recebimento), guloso com desempate, arredondamento com sobra;
  - capacidade física no tempo (pico do dia, todos os pedidos, quarentena e reserva, uso efetivo com sobra de embalagem e estoque final), critério regulatório NR-31 31.7.16 e classe;
  - invariantes, mover entre fazendas com permissão nas duas, conciliação, encerramento parcial e cancelamento;
  - simulação sem as previsões abertas da própria programação (E18);
  - idempotência, versão, rascunho × enviada e recusa por concorrência que preserva a intenção.
- **Propriedade, com gerador simples e semente fixa:**
  - em cada item, o Total é a soma das fazendas;
  - não existe entrega sem fazenda;
  - janela vazia sempre vira conflito, nunca adiamento;
  - o total fica entre a necessidade e a necessidade + 1 embalagem por linha;
  - repetir a simulação sem mudança não muda a lista nem as quantidades;
  - a ocupação de nenhum dia, inclusive depois do último uso, passa da capacidade sem um conflito registrado;
  - a sobra de embalagem só sai do local pelo uso efetivo.
- **Navegador (`entrega_faz_test.py`):**
  - E2, E7 a E10, E16, E16b, E17 e E19, a 1440 e a 390 px;
  - sem erro de JS;
  - cliques contados.
- **Software real (fora do protótipo):** teste de integração no servidor para:
  - o escopo do token (pedido, contato e ações; expiração e revogação);
  - a nota restrita à entrega;
  - a permissão nas duas fazendas;
  - a serialização da ocupação por local;
  - a publicação da versão com o recibo.
  - No protótipo, o E7 é só visual.
- **Devem continuar verdes:** `cal01_test.py`, `cmptest.py`, `est_cenario_test.py`, `safra_grupo_contrato_test.js`, `pt06_unit.py` e `ds_1610_test.py`.
- **Contraprova** em cada regra de estoque, demanda e acesso. **Fotos** na galeria (skill `padrao-safrion`).

## IDs do PRD aplicáveis

- **Telas:** SU-01, SU-04, SU-05 (Programação de entregas), SU-06, SU-08, PT-01, PT-02, PT-05, PT-06, CD-01, CD-05, CD-06, UX-03.
- **Fluxos:** FL-09, FL-10, FL-11, FL-26.
- **Cálculos:** CAL-01, CAL-02 (trânsito não conta em dois locais), CAL-03, CAL-11 (embalagem não muda dose).
- **Reposição:** 65.3, 65.4, 65.5, 65.5.1; PCE-03, PCE-04, PCE-08, PCE-11.
- **Requisitos:** RF-SUP-001, 004, 006, 007, 009, 011, 012.
- **Regras:** RN-001, 003, 010, 011, 015, 018, 019, 028, 032, 033, 034, 035, 039, 043, 044, 045.
- **Comandos:** CMD-12, CMD-13, CMD-14, CMD-15; CMD-06 e 42 como limites.
- **Domínio:** 40.3, 44.1, 41 e 42; PRD 24; 73.3; ENG-011, 013, 017, 021, 022.
- **Navegação e design:** 4.2, 4.3; cap. 74.
- **Decisões:** DEC-2609-11, DEC-0910-25 (a e b), DEC-1610-01 (D5), PEND-CTL-02 (padrão adotado); EX-35.
- **Regras do protótipo:** DEM-07, DEM-08, DEM-09; SAF-FAZ-2.

## Fora do escopo (com condição de retorno)

| Item | Volta quando |
|---|---|
| Envio real por e-mail e WhatsApp | P1 for autorizada (conta, domínio e custo) |
| NF-e real (XML da SEFAZ, chave de acesso, manifestação) e ERP | O proprietário autorizar a integração real (AGENTS §2) |
| Frete por distância, roteirização e contratação de transporte | O proprietário pedir; até lá vale o CIF ou FOB da proposta |
| Contrato de safra com liberações e limite de crédito | A DEC-07 (exposição de compras) for decidida |
| Agenda de doca e fila de caminhões no recebimento (cap. 50) | Depois do piloto, se a portaria virar gargalo |
| Produto com regra própria de transporte ou guarda (carga perigosa, controle especial) | Houver curadoria regulatória com fonte |
| Comprar junto safras diferentes (por exemplo, a safrinha) | O proprietário pedir |
| Conversão física entre kg e L na capacidade | Houver densidade por item com fonte (RN-033). Hoje cada grandeza tem a sua capacidade; o critério conjunto do armário é a regra regulatória da NR-31 31.7.16, não conversão |
| Prazo em dias úteis e calendário de feriados | Houver calendário por município com fonte. Hoje: dias corridos e as datas sem recebimento informadas pela fazenda |

## Decisões só do proprietário (com recomendação)

| ID | Pergunta | Recomendação | Até decidir |
|---|---|---|---|
| P1 | Enviar o link de verdade por e-mail e WhatsApp? Gera custo e conta: o WhatsApp cobra por mensagem modelo, e o e-mail precisa de domínio | E-mail transacional no piloto. WhatsApp com mensagem modelo de "utilidade" quando o custo for autorizado | Envio simulado; o comprador copia o link |
| P2 | Nota fiscal por fazenda: cada fazenda é o destinatário fiscal da sua entrega? Fazendas de empresas diferentes podem estar no mesmo pedido? (Santa Rita fica em GO e Lagoa Grande em MG, sem empresa no cadastro) | Negociação e preço únicos; NF-e por entrega, com o destinatário e o local de entrega da fazenda. Empresas diferentes: um pedido por empresa, com o mesmo preço da compra única. Confirmar com o contador | No protótipo: um pedido por fornecedor e nota por entrega, marcados "Simulação". No software real, a negociação agrupada não decide destinatário fiscal nem empresa de fazenda sem cadastro até esta resposta |
| P3 | Antecedência padrão por grupo (dias antes do uso) | Os valores da proposta 2, editáveis no item | Valores de demonstração, marcados assim |
| P4 | Data do fornecedor depois do "entregar até": quem aceita? | O comprador aceita. Depois do "entregar até", o gestor da fazenda recebe aviso; no dia do uso ou depois, o aceite exige justificativa | Como recomendado, marcado "a confirmar" |
| P5 | Estender a D5 ao insumo agrícola (reservar para a O.S. na chegada)? | Não. O vínculo da chegada é a fazenda; reservar antes da liberação prenderia insumo de O.S. sem aprovação agronômica (PRD 41 e 42) | Não reserva na chegada |
