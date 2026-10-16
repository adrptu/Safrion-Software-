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
Aceite e comando de verificação: E1–E17 abaixo / node entrega_faz_unit.js; python3 -B entrega_faz_test.py; mais cal01_test.py, cmptest.py, est_cenario_test.py, node safra_grupo_contrato_test.js, pt06_unit.py, ds_1610_test.py
Estado / impedimento / próximo passo: especificado; na fila (§3.6, no máximo 3 frentes); no protótipo tudo é simulado; P1 e P2 só travam o software real
```

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
| 5 | [NR-31, gov.br/MTE](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/nr-31-atualizada-2024-1.pdf) (redação da Portaria SEPRT 22.677/2020; última alteração na Portaria MTE 342/2024) | **31.7.14:** edificação própria para agrotóxicos e afins, com acesso restrito, ventilação e placas, a mais de 15 m de habitações e de alimentos. **31.7.15:** estrados, longe de paredes e teto. **31.7.16:** até 100 L ou 100 kg em armário exclusivo e trancado. **31.7.17:** transporte em recipiente rotulado e fechado. A ABNT NBR 9843-3:2019 (armazenamento em propriedades rurais) consta do catálogo; o texto é pago e **não foi lido** | **Adotar como trava:** linha de defensivo ou afim só vai a local dessa classe, e armário tem capacidade de 100 L/kg |
| 6 | Meta, WhatsApp Business Platform: [Message templates](https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates/) (sem data) | Fora da janela de atendimento, só a mensagem modelo chega ao destinatário. As categorias são autenticação, marketing e utilidade, e a categoria entra no preço | **Adiar** o envio real (custo e conta: P1). No protótipo, o link é simulado |

Estar num sistema do mercado não prova a regra de domínio. As travas daqui nomeiam o dano que evitam.

## Decisões dos agentes (delegação do proprietário)

1. **A demanda vem do plano efetivo de cada fazenda.**
   - O plano efetivo é a versão publicada do plano agronômico com os ajustes do agrônomo no talhão (PRD 40.3). A conta é o CAL-01 da fazenda.
   - **Nenhuma fórmula nova** (ENG-011): a programação lê as linhas do CAL-01 (`nec` por data de uso).
   - Cada linha leva fazenda, talhão, atividade, versão do plano e data de uso (RN-003, 44.1).
   - Comprar não autoriza aplicar. A O.S. continua com aprovação individual (PRD 41), e a reserva continua na liberação (CMD-06, PRD 42).
2. **Data de necessidade por item.**
   - Cada item tem duas antecedências, que definem a janela de cada uso: `[uso − máxima, uso − mínima]`, nunca antes da chegada viável do fornecedor escolhido (hoje + prazo dele).
     - **Mínima:** chegar até N dias antes do uso (conferência, laudo, tratamento de semente).
     - **Máxima:** não chegar antes de M dias do uso (validade, conservação, espaço).
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
4. **Programação de entregas por fazenda: o centro do pedido.**
   - **Entrega programada** = fornecedor + fazenda + janela. Cada linha da entrega tem item, quantidade, embalagens e local de recebimento.
   - **Montagem sugerida** (determinística: a mesma entrada dá a mesma saída):
     1. Por fazenda, cada uso com falta (`nec`) vira uma necessidade com janela.
     2. As necessidades são ordenadas pelo fim da janela. A entrega fecha no fim da primeira e leva todas as que começam até essa data, de qualquer item do mesmo pedido. A janela da entrega é o cruzamento das janelas. É o guloso clássico de intervalos: dá o menor número de entregas por fazenda (menos caminhões, menos recebimentos).
     3. Cada linha arredonda para embalagem inteira. A sobra cobre o uso seguinte do item (PRD 65.5), e a diferença aparece ("arredondamento +10 L"), nunca some.
     4. **Capacidade:** a ocupação projetada do local é calculada assim: os itens desse local, na mesma unidade, pelo CAL-01, e cada entrega conta desde o início da janela ou desde a data prometida. Se a chegada passa da capacidade, sai da entrega a necessidade de fim mais tardio, e a janela dela começa quando cabe. Sem saída, vira conflito com local, data e excesso. **Nunca corta quantidade** (65.5). Capacidade em branco é "não informada" (nem zero nem infinita; 65.5.1).
   - **Invariantes** (o servidor confere a cada comando; o dano evitado vem entre parênteses):
     - toda entrega tem fazenda e um local daquela fazenda (material na fazenda errada);
     - a soma das entregas do item é igual à quantidade do item no pedido, e, por fazenda, a soma das entregas é igual à parcela da fazenda (comprar ou cobrar diferente do entregue);
     - linha de defensivo ou afim só vai a local dessa classe (NR-31, item 31.7.14: defensivo junto de alimento ou de semente).
   - **Sempre total e por fazenda lado a lado:** colunas Total, Fazenda A, Fazenda B…, com a soma conferida na linha de total.
   - O comprador pode mudar janela ou local, ou mover quantidade de um item entre fazendas sem mudar o total.
     - Cada mudança revalida invariantes e capacidade.
     - Quando mexe no que o fornecedor já confirmou, volta a pedir o aceite dele.
     - Quando deixa uma fazenda abaixo da necessidade, avisa com a falta resultante e pede o motivo.
5. **A cotação já sai com destinos.** O convite leva o total e a divisão por fazenda, com janelas e municípios. A proposta informa prazo e frete (CIF ou FOB). A comparação mede "chega a tempo" por fazenda, pela primeira janela de cada uma, e não só pela primeira falta da safra (refina a DEM-08).
6. **Link do fornecedor** (a página do pedido do PT-05, reaproveitando a PT-05det).
   - **Acesso:**
     - um link por pedido e por contato do CD-05, enviado ao e-mail ou ao WhatsApp do cadastro;
     - tem finalidade e validade (até 30 dias depois da última entrega) e pode ser revogado (FL-26, RN-039);
     - quem tem o link só vê aquele pedido.
   - **Abre direto no pedido:** Total e por fazenda lado a lado, sem outro clique. Abaixo, as entregas agrupadas por fazenda, cada uma com:
     - endereço e coordenadas;
     - dias e horário de recebimento;
     - quem recebe (função e telefone da portaria);
     - restrição de veículo.
   - **Ações**, cada uma com a chave da intenção e um recibo:
     - Confirmar (todas ou por fazenda);
     - Propor outra data (por entrega, com data por atalho e motivo escolhido numa lista);
     - Avisar embarque (data, placa e número da NF-e);
     - Enviar NF-e;
     - Abrir divergência.
   - **Nunca aparecem:** outros pedidos, propostas ou fornecedores; preço de referência; demanda, estoque ou talhões; usuários da organização (EX-35; PT-06 no PR #75).
   - O comprador pode registrar uma confirmação recebida por telefone, com canal e pessoa (fato registrado, RN-018).
   - No protótipo, o envio é simulado e o link abre a página do portal com o token da demonstração. SU-05 e o portal continuam fora do menu: a programação fica na etapa 6 de Compras, uma solução só para o mesmo problema (§3.4).
7. **Gestão de entregas no sistema** (Compras, etapa 6 "Acompanhe as entregas"; cobre as visões da SU-05).
   - **Lista agrupada por fazenda** por padrão (AGR-02). Agrupar por também oferece Fornecedor, Item e Semana.
   - **Situações:** A enviar → Aguarda confirmação → Confirmada → Proposta do fornecedor → Embarcada → Recebida em parte → Recebida. "Atrasada" (janela vencida sem recebimento) e "Conflito" (capacidade ou prazo) são marcas, não etapas.
   - **Pontualidade:** a data pedida (fim da janela) e a data prometida ficam separadas. A primeira promessa fica guardada para medir pontualidade, e reprogramar não apaga o atraso (RF-SUP-012).
   - **Reprogramar** vale para a entrega, não para o pedido inteiro, e exige motivo (lista curta e "Outro").
   - **Cobertura da demanda:**
     - entrega não confirmada cobre a demanda da fazenda como "a confirmar" (cobertura proposta, PCE-03);
     - entrega atrasada deixa de cobrir na data antiga, e a falta reaparece no Planejar safra e em Compras (RF-SUP-001).
8. **Recebimento na fazenda certa** (Estoque, com o filtro de Fazenda da DEC-2609-11).
   - **Nota × entrega:** a nota escolhe a entrega, e a lista só mostra entregas daquela fazenda. Nota de uma entrega de outra fazenda é recusada, com o nome da fazenda certa (EX-35).
   - **Parcial:** recebimento parcial mantém aberto o saldo da entrega (RF-SUP-006/007). A tolerância é a do item no pedido (DEC-0910-25 a; sem tolerância, 0 %), e a sobra fica bloqueada até a decisão.
   - **Cobertura:** o que chega entra no físico apto da fazenda que recebeu e cobre a demanda dela (DEM-07). Material em quarentena cobre de forma condicionada (65.4).
   - **Caminhão na fazenda errada:** o padrão é Recusar.
     - "Receber aqui" registra o fato onde ele aconteceu (RN-018) e propõe a transferência para a fazenda programada (SU-08, em trânsito).
     - A fazenda programada continua descoberta até a transferência chegar: material nunca conta em dois lugares.
   - **D5** (DEC-1610-01) vale para peça de ordem de manutenção. No insumo agrícola, o vínculo da chegada é a fazenda; a reserva para a O.S. continua na liberação (P5).
9. **Conciliação de pedido, entregas e notas**, por item e por fazenda.
   - **Saldos:**
     - o pedido é a soma das entregas;
     - o recebido conferido sai de cada nota, por entrega;
     - saldo a entregar = programado − recebido conferido − cancelado (CAL-03).
   - **Divergência:** diferença entre nota, entrega e conferido abre divergência com dono e bloqueia o título correspondente (RF-SUP-011; DEC-0910-25 a). O financeiro é separado do físico (RN-028).
10. **Mudança de plano vira reprogramação proposta, nunca silenciosa.**
    - **Mudança de data:** nova versão do plano, data de plantio ou dose muda a demanda da fazenda (DEM-09). A entrega afetada mostra ⚠ com o antes e o depois ("uso de 25/10 passou a 12/10: chegar até 07/10") e a ação "Propor reprogramação".
    - **Aumento:** vira complemento pela solicitação da fazenda (DEM-09), ou move quantidade do mesmo item de outra fazenda. Nunca muda o pedido sozinho (40.3, PCE-11).
    - **Redução com pedido emitido:** nada baixa sozinho (`cal01.js:194-197`). A linha mostra "acima da demanda" e as saídas: mover para outra fazenda ou negociar aditivo com o fornecedor.
11. **O servidor é a autoridade** (AGENTS §4; PRD 24).
    - Saldos, reservas, invariantes da programação e recebimentos são decididos pelo servidor.
    - Cada comando leva a chave de idempotência de quem inicia e a versão esperada da programação (73.3; ENG-021/022). Os comandos: emitir pedido com programação, enviar programação, confirmar, propor data, decidir proposta, avisar embarque, mover entre fazendas, reprogramar e receber.
    - Versão velha recebe "A programação mudou: abra a versão atual" e nada é sobrescrito.
    - Efeito, recibo e saída (outbox) gravam na mesma transação. Quantidades em decimal, com unidade (ENG-013, RN-033).

## Telas

Master-detail, uma primária por tela. DS (cap. 74) no padrão das telas de processo do módulo Agrícola (Planejar safra), que Compras já usa: ETP-02, TAB-08 (⇅ e funil por coluna, seta de abrir), VIS-06, AGR-02, FIL-01 (faixa de filtros pela peça comum), TAB-05/06, BOT-01 (verbo + objeto, um verde por contexto) e AVI-01.

| Tela | O que muda | Primária |
|---|---|---|
| Planejar safra › etapa 4 | Coluna "Entregar até" por fazenda. A faixa das fazendas (FIL-01) já existe | "Enviar as N fazendas para cotação" (existente) |
| Compras › etapa 1 | A safra de várias fazendas é uma linha, com as fazendas e as solicitações de cada uma | Abrir compra |
| Compras › etapa 2 | Demanda em matriz: Item · Total · uma coluna por fazenda (quantidade e "entregar até"). A linha de total confere a soma | (existente) |
| Compras › etapas 3 e 4 | O convite mostra total e fazendas com janelas. A comparação marca "chega depois" por fazenda | (existentes) |
| Compras › etapa 6 (lista) | Entregas agrupadas por fazenda, com subtotal por fazenda e total. Faixa FIL-01 com Fazenda (chips com contagem: "Todas 3 · Santa Rita 1 · Lagoa Grande 2"), Situação e Fornecedor. Visões: Tabela, Cartões e Calendário (semana × fazenda) | "Enviar programação ao fornecedor" enquanto houver entrega a enviar |
| Detalhe da entrega (painel) | Fazenda, local, endereço e janela; linhas e embalagens; classe e capacidade; usos que a entrega cobre (talhão, atividade e data, com link ao Planejar safra); histórico de datas; notas fiscais | Pela situação: "Aceitar data proposta", "Reprogramar entrega" ou "Receber na fazenda" |
| Detalhe do pedido (painel) | Matriz Total × fazendas com a soma conferida, entregas e conciliação com as notas | Enviar programação |
| Link do fornecedor (PT-05det) | Topo: Total e por fazenda. Abaixo: entregas por fazenda com endereço, horário e recebedor | Confirmar entregas |
| Estoque › Confira recebimentos | Bloco "Chegam nesta fazenda" (entregas confirmadas ou embarcadas da fazenda do filtro); a nota escolhe a entrega | Receber |
| Cadastros | Fazenda: "Recebimento de insumos" (endereço, coordenadas, dias e horário, recebedor, restrição de veículo). Local: classe de armazenagem e capacidade. Item: antecedência mínima e máxima | Salvar (existente) |

- **Celular (390 px):**
  - Cartões (VIS-06) com uma linha de Total e uma por fazenda;
  - a matriz rola dentro da tabela, com Item e Total fixos, e a página não rola de lado;
  - alvos de 44 px.
- **Cliques** (§3.3, contados no teste):
  - o fornecedor confirma tudo com 2 cliques (abrir o link e "Confirmar entregas", com as datas sugeridas no início de cada janela);
  - propõe uma data com 4 (Propor data, atalho de data, motivo, Enviar);
  - o comprador envia a programação com 1 clique a partir da etapa 6.

## Dados de exemplo (sintéticos)

**S1.**
- **Contexto:** hoje é 23/09/2026. O fornecedor é a Santa Rita Insumos (F04), com prazo de 7 dias (chegada viável em 30/09).
- **Itens:** Óleo mineral e Glifosato 480, ambos em galão de 20 L.
- **Antecedência** de defensivos e adjuvantes: de 5 a 30 dias.
- **Estoque apto** desses itens: 0 nas duas fazendas.

| Fazenda | Item | Usos (data · necessidade líquida) | Local |
|---|---|---|---|
| Santa Rita | Óleo mineral | 25/10 · 120 L; 12/11 · 90 L | Almox. defensivos |
| Santa Rita | Glifosato 480 | 05/11 · 20 L | Almox. defensivos |
| Lagoa Grande | Óleo mineral | 30/10 · 400 L; 20/11 · 230 L | Almox. Lagoa Grande |
| Lagoa Grande | Glifosato 480 | 25/10 · 293,34 L | Almox. Lagoa Grande |

Programação esperada (montagem da decisão 4):

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
| E2 | Compra única da safra de 2 fazendas | Etapa 1: uma linha "Safra 2026/27" com as duas fazendas e as duas solicitações. Etapa 2, com S1: Óleo 840 L = 210 + 630 e Glifosato 313,34 L = 20 + 293,34, lado a lado. Na demonstração, a soma por fazenda é igual ao total em todas as linhas |
| E3 | Programação sugerida (S1) | Exatamente LG-1, SR-1 e LG-2, com as janelas e embalagens da tabela. Arredondamento visível (+20 L e +6,66 L). Rodar duas vezes dá o mesmo resultado |
| E4 | Capacidade (S1 só com o Óleo da Lagoa Grande e o local com 500 L) | Duas entregas: 400 L em 30/09–25/10 e 240 L em 31/10–15/11 (640 L não cabem antes do uso de 30/10). Com 300 L: conflito "400 L > 300 L no Almox. Lagoa Grande", nada cortado. Capacidade em branco: "não informada", sem conflito |
| E5 | Classe de armazenagem | Levar a linha do Óleo da SR-1 para "Galpão 2" ou "Câmara fria" é recusado ("adjuvante: só em local de defensivos e afins, NR-31 31.7.14"). Local de outra fazenda é recusado. Nada muda |
| E6 | Invariantes e mover entre fazendas | Entrega sem fazenda é recusada. Mover 100 L de Óleo da LG-2 para a SR-1 deixa Santa Rita com 320 L e Lagoa Grande com 540 L; o total continua 860 L; a LG-2 aparece com a falta de 90 L e pede motivo; SR-1 e LG-2 voltam a "Aguarda confirmação". Reduzir só a SR-1 sem aditivo é recusado ("o total mudaria de 860 para 760 L") |
| E7 | Link do fornecedor (1 clique, sem exposição) | Ao abrir o link do PC-101, a página mostra o Total (860 e 320 L) e cada fazenda (Santa Rita 220 e 20 L; Lagoa Grande 640 e 300 L), mais as 3 entregas por fazenda com endereço, horário e recebedor. O texto da página não tem: usuários da organização (Ana, Marcos, Rui, Paula, Carlos), outros fornecedores, "SOL-", estoque, talhões, preço de referência. Trocar o pedido no endereço, ou usar link vencido ou revogado: "Este link não dá acesso a este pedido", sem dado nenhum |
| E8 | Confirmar e propor por fazenda | "Confirmar entregas" grava as datas prometidas 30/09 (LG-1), 13/10 (SR-1) e 21/10 (LG-2). Propostas para a LG-2 (janela 21/10–15/11; uso em 20/11): 28/10 fica "Proposta do fornecedor · dentro da janela"; 18/11 fica em âmbar, "depois do entregar até (15/11), antes do uso" (aviso ao gestor, P4); 20/11 fica em vermelho, "chega no dia do uso", e o aceite exige justificativa. Ao aceitar, a promessa passa à nova data, e a primeira (21/10) fica guardada para a pontualidade |
| E9 | Aviso de embarque | O fornecedor avisa o embarque da LG-1 (placa QAS-2C41, NF-e 7001), e ela passa a "Embarcada". O Estoque com o filtro Lagoa Grande mostra a LG-1 em "Chegam nesta fazenda"; com o filtro Santa Rita, não mostra |
| E10 | Recebimento parcial na fazenda certa | A NF 7001 da LG-1 (Glifosato 300 L e Óleo 400 L) é conferida na Lagoa Grande com Glifosato 200 L e Óleo 400 L. Resultado: LG-1 "Recebida em parte", com saldo de 100 L de Glifosato; físico apto da Lagoa Grande +200 L de Glifosato e +400 L de Óleo, que cobrem a demanda dela; Santa Rita sem mudança. A mesma nota no Estoque da Santa Rita é recusada ("NF 7001 é da entrega LG-1, Lagoa Grande"). Ler a mesma nota de novo não cria entrada |
| E11 | Conciliação | PC-101 · Glifosato: pedido 320 = programado 320 (20 + 300); recebido 200; saldo 120 (Santa Rita 20 e Lagoa Grande 100). NF 7001 com 300 L e 200 L conferidos abre a divergência "Falta 100 L", com dono, e bloqueia o título até a solução |
| E12 | Plano mudou a data (Santa Rita · Óleo: uso de 25/10 vira 12/10) | A SR-1, já confirmada, mostra ⚠ "uso de 25/10 passou a 12/10: chegar até 07/10" e a proposta de dividir em SR-1a (Óleo 120 L e Glifosato 20 L, 06–07/10) e SR-1b (Óleo 100 L, 13/10–07/11). O total de Santa Rita continua 220 L de Óleo. Nada muda no pedido nem no fornecedor sem "Propor reprogramação" e o aceite dele; até lá, a demanda de Santa Rita mostra a falta em 12/10 |
| E13 | Plano mudou a quantidade | Dose maior em Santa Rita (+60 L de Óleo): o complemento da solicitação aparece em Compras e o PC-101 não muda; a SR-1 avisa "+60 L em Santa Rita: cotar complemento ou mover da Lagoa Grande". Redução de 100 L na Lagoa Grande com pedido emitido: nada baixa sozinho; a linha mostra "100 L acima da demanda" e as saídas |
| E14 | Idempotência e concorrência | Clicar duas vezes em "Confirmar entregas" grava um registro com o mesmo recibo. Proposta do fornecedor sobre a versão 2, quando o comprador já mandou a 3: "A programação mudou: abra a versão atual", nada sobrescrito. Reenvio com a mesma chave devolve o mesmo recibo |
| E15 | Atraso | Em 21/10, sem embarque da LG-1 (janela até 20/10), ela fica "Atrasada". A Lagoa Grande volta a mostrar falta de Glifosato em 25/10 e de Óleo em 30/10, e a pontualidade conta contra a promessa original |
| E16 | Caminhão na fazenda errada | A LG-1 chega à Santa Rita, e a opção padrão é Recusar. "Receber aqui" soma ao físico de Santa Rita 300 L de Glifosato e 400 L de Óleo e propõe a transferência para a Lagoa Grande. A Lagoa Grande segue descoberta até a transferência ser recebida; nenhuma quantidade conta nas duas fazendas |
| E17 | Celular, teclado e cliques | A 390 px, o link mostra Total e fazendas sem rolagem lateral da página, com alvos de 44 px. O teclado faz todo o fluxo. Cliques contados no teste: fornecedor confirma tudo com 2 e o comprador envia a programação com 1. Antes, não havia confirmação do fornecedor nem nada por fazenda |

**Contraprova:** a versão de a685f5e não tem antecedência, compra única, entrega por fazenda nem link, e reprova E1 a E11 e E15 a E17. Os aceites são propostos; viram teste depois da revisão do Codex sobre esta versão.

## Testes (proporcionais ao risco: estoque, demanda e dinheiro)

- **Unidade (`node entrega_faz_unit.js`):**
  - janela, guloso, arredondamento com sobra, capacidade e classe;
  - invariantes, mover entre fazendas e conciliação;
  - idempotência e versão.
- **Propriedade, com gerador simples e semente fixa:**
  - a soma por fazenda é igual ao total;
  - não existe entrega sem fazenda;
  - janela vazia sempre vira conflito;
  - o total fica entre a necessidade e a necessidade + 1 embalagem por linha.
- **Navegador (`entrega_faz_test.py`):**
  - E2, E7 a E10, E16 e E17, a 1440 e a 390 px;
  - sem erro de JS;
  - cliques contados.
- **Devem continuar verdes:** `cal01_test.py`, `cmptest.py`, `est_cenario_test.py`, `safra_grupo_contrato_test.js`, `pt06_unit.py` e `ds_1610_test.py`.
- **Contraprova** em cada regra de estoque, demanda e acesso. **Fotos** na galeria (skill `padrao-safrion`).

## IDs do PRD aplicáveis

- **Telas:** SU-01, SU-04, SU-05 (Programação de entregas), SU-06, SU-08, PT-01, PT-02, PT-05, PT-06, CD-01, CD-05, CD-06, UX-03.
- **Fluxos:** FL-09, FL-10, FL-11, FL-26.
- **Cálculos:** CAL-01, CAL-03, CAL-11 (embalagem não muda dose).
- **Reposição:** 65.3, 65.4, 65.5, 65.5.1; PCE-03, PCE-04, PCE-08, PCE-11.
- **Requisitos:** RF-SUP-001, 004, 006, 007, 009, 011, 012.
- **Regras:** RN-001, 003, 010, 015, 018, 019, 028, 032, 033, 034, 035, 039, 043, 044.
- **Comandos:** CMD-12, CMD-13, CMD-14, CMD-15; CMD-06 e 42 como limites.
- **Domínio:** 40.3, 44.1, 41 e 42; PRD 24; 73.3; ENG-011, 013, 017, 021, 022.
- **Navegação e design:** 4.2, 4.3; cap. 74.
- **Decisões:** DEC-2609-11, DEC-0910-25 (a), DEC-1610-01 (D5); EX-35.
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
| Capacidade somando kg e L com conversão | Houver densidade por item com fonte (RN-033); hoje só a mesma unidade, ou "L e kg somados" quando o local declara essa regra (armário da NR-31) |

## Decisões só do proprietário (com recomendação)

| ID | Pergunta | Recomendação | Até decidir |
|---|---|---|---|
| P1 | Enviar o link de verdade por e-mail e WhatsApp? Gera custo e conta: o WhatsApp cobra por mensagem modelo, e o e-mail precisa de domínio | E-mail transacional no piloto. WhatsApp com mensagem modelo de "utilidade" quando o custo for autorizado | Envio simulado; o comprador copia o link |
| P2 | Nota fiscal por fazenda: cada fazenda é o destinatário fiscal da sua entrega? Fazendas de empresas diferentes podem estar no mesmo pedido? (Santa Rita fica em GO e Lagoa Grande em MG, sem empresa no cadastro) | Negociação e preço únicos; NF-e por entrega, com o destinatário e o local de entrega da fazenda. Empresas diferentes: um pedido por empresa, com o mesmo preço da compra única. Confirmar com o contador | No protótipo: um pedido por fornecedor e nota por entrega |
| P3 | Antecedência padrão por grupo (dias antes do uso) | Os valores da decisão 2, editáveis no item | Valores de demonstração, marcados assim |
| P4 | Data do fornecedor depois do "entregar até": quem aceita? | O comprador aceita. Depois do "entregar até", o gestor da fazenda recebe aviso; no dia do uso ou depois, o aceite exige justificativa | Como recomendado, marcado "a confirmar" |
| P5 | Estender a D5 ao insumo agrícola (reservar para a O.S. na chegada)? | Não. O vínculo da chegada é a fazenda; reservar antes da liberação prenderia insumo de O.S. sem aprovação agronômica (PRD 41 e 42) | Não reserva na chegada |
