# Benchmark de Cadastros (CD-01 a CD-07)

```text
ID / resultado útil / persona: CADUX-B1 · cinco referências oficiais para redesenhar os Cadastros com "seleção abre detalhes" · gestor de dados, agrônomo, PCM, compras
Requisitos do PRD e fora do escopo: CD-01..CD-07; PRD 4.2, 4.3, 60, 67.3; FO-01, FO-21..FO-26, FO-40. Fora: código (esta etapa só documenta), preço das referências, avaliações de usuários
Autor / revisor / integrador: Claude / Codex / Claude
Base (commit ou hashes) / arquivos sob responsabilidade: claude/v44-cadux @ 8356a07 · docs/cadastros-ux/BENCHMARK.md
Aceite e comando de verificação: cada afirmação tem fonte oficial com URL e data (§7); páginas abertas em 09/10/2026 por WebFetch, curl e API pública da central Zendesk da Cropwise
Estado / impedimento / próximo passo: especificado (pesquisa documental; nenhum produto foi usado nem testado) · sem impedimento · próximo: desenho das telas a partir do §4 e do §5
```

**Pedido do proprietário (09/10/2026):** "os cadastros ainda não estão intuitivos com melhor UX e UI. faça algo mais prático e intuitivo. E use seleção para abrir detalhes... como clicar na fazenda e abrir talhões cadastrados nela na tela."

**Regra de leitura.** Só entra o que a página da fonte mostra; "não confirmado" quer dizer que a página lida não diz. Nenhuma referência publica contagem de cliques: a medição antes e depois fica no nosso teste ponta a ponta (AGENTS §3.3). Estar no mercado não prova que a regra está certa; cada prática passa pelo PRD antes de entrar. Itens que só existem na v3.10/3.11 do PRD estão marcados "v3.10/3.11 em revisão".

## 1. As cinco referências

| # | Referência | Por que está aqui | Limite da evidência |
|---|---|---|---|
| A | **Aegro** (Brasil) | Gestão agrícola feita para a fazenda brasileira; central de ajuda pública em português, atualizada em ago–set/2026 | Não diz o que abre ao clicar no talhão; nada sobre registro no MAPA nem embalagem no catálogo |
| C | **Cropwise Financials** (Syngenta Digital) | Árvore Fazenda → Talhão → Zona de cultivo com painel de detalhes; ficha do produto com bula, reentrada e carência; ajuda 2025–2026 | É a versão dos EUA (EPA, CLU). A oferta brasileira (Cropwise Operations, Strider) não tem central pública que eu tenha conseguido abrir |
| D | **John Deere Operations Center** | Referência de máquina conectada; Land (cliente, fazenda, campo, contornos), Equipamentos (máquinas e implementos), Produtos, Equipe; ajuda oficial 2024–2026 | Foco nos EUA; várias páginas sem data |
| S | **Senior ERP Mega, módulo Agro** (Brasil) | ERP brasileiro com cadastro agrícola documentado em público; mostra o "jeito ERP" (fundo agrícola, talhão com subguias, recurso único) e serve de contraste | Páginas sem data; descrevem campos, não o fluxo de uso |
| F | **Climate FieldView** (Bayer) | Muito usado no Brasil; lista de campos ao lado do mapa, importação, mesclar campos | Cobre só campos e contornos; o passo a passo detalhado é de 2016 (PDF oficial); a página atual é curta |

**Tentadas e não confirmadas:** TOTVS Agro (no TDN só achei boletins técnicos, nenhuma página de cadastro de talhão); Siagri/Aliare (sem central pública encontrada); Cropwise Operations no Brasil e Strider (só loja de aplicativos e notícia); Solinftec, Agrotools e Farmbox (sem ajuda pública encontrada); Agrivi (só páginas de marketing); Trimble Ag (as páginas de suporte redirecionam para a página inicial); Agworld (só um anúncio de 2021). Para "Agrosys" e "Agrivalle" não identifiquei produto de gestão com documentação pública.

## 2. O que as referências fazem

### 2.1 Fazenda → talhão: organização e o que a seleção abre
- **Cropwise.** O menu Properties tem a lista "Farm Field Tree" (Fazenda → Talhão → Zona de cultivo) e o mapa. Ao selecionar uma fazenda ou um talhão na árvore, aparecem **Details** e, no talhão, **Cost Analysis**. Em Details estão localização, licenças, dados legais, terra, água, notas, produtos aplicados, colheita e histórico de culturas [C3]. Na árvore da tela de mapas para impressão há busca, filtro por fazenda e agrupamento por fazenda ou por cultura [C7]. No app, o usuário escolhe pela árvore ou pelo mapa: tocar na fazenda leva aos talhões dela ou aos detalhes da fazenda; tocar no talhão abre "View Full Details", com rota até o talhão [C8].
- **Deere.** Land tem as abas Clientes e fazendas, Campos, Contornos e Marcações, com vista de mapa e de tabela. A lista de campos fica à esquerda, com caixas de seleção; selecionar um campo abre o painel **Field Details** [D9][D10][D11]. Filtros: busca, filtros rápidos por cliente, fazenda e campo, e filtros como "sem fazendas" e "sem campos" [D9][D11]. Selecionar uma marcação na lista leva a ela no mapa e mostra os detalhes [D11]. No app, a aba "Clients and Farms" lista tudo, e selecionar o campo abre os detalhes para edição [D8]. O mapa pode colorir os campos pela última cultura semeada ou pela cultura planejada [D13].
- **FieldView.** O painel "Fields List" fica à esquerda, e "Add a Field" fica no rodapé da lista [F1]. Campo sem contorno aparece com "?" [F2].
- **Aegro.** A unidade é a "propriedade". Para separar várias fazendas dentro dela, a ajuda manda criar um **agrupador** com o nome de cada fazenda [A4]. O mesmo agrupador serve para tipo de solo ou microclima [A3]. No mapa, o talhão selecionado fica destacado. As cores mostram as safras em andamento (mapa da propriedade) ou as cultivares (mapa da safra) [A5]. O "Painel de Controle do Talhão" traz informações gerais, custo orçado e realizado e eventos, com "+" para registrar observação ou atividade [A6]. A ajuda não diz como se chega a esse painel, se pelo mapa ou pela lista.
- **Senior.** A hierarquia é Fundo agrícola → Talhão → Sub-área → Área produtiva, em formulários com guias e subguias [S1][S4]. A ficha do talhão é uma consulta separada, com filtros à esquerda e duplo clique para ver os detalhes [S2]. O mapa (GIS) também é consulta separada: passar o mouse sobre o talhão mostra um quadro com informações [S5].

### 2.2 Contorno, área e versões
- **Área informada × área do contorno.** A Cropwise usa "Reported Area" quando o contorno não representa a área real [C1]. O Aegro calcula a área pelo desenho, avisa que pode ser imprecisa e aceita a medida oficial [A1]. O FieldView pede uma área aproximada [F1].
- **Contorno ativo.** A Deere admite um só contorno ativo por campo: criar outro inativa o anterior [D9].
- **Mudar a área de talhão que já está em safra.** O Aegro pergunta se a mudança vale "apenas para safras futuras" ou para as safras escolhidas [A8].
- **Ferramentas de desenho:**
  - polígono, círculo (pivô: centro e raio, ou centro e arrasto), retângulo e corte [C1][D9][A1];
  - busca por endereço ou coordenada [C1][D9][A1];
  - detecção automática pela imagem de satélite (Cropwise Explorer) [C15];
  - base pública de imóveis, só nos EUA (CLU, parcelas) [C1][F1][D12];
  - contorno tirado de uma operação já feita pela máquina [D9].
- **Zona de cultivo** (equivale à nossa parcela por safra):
  - nasce do talhão com o mesmo contorno, que pode ser ajustado, e se divide com a ferramenta de corte [C4][C5];
  - "Bulk Edit" atribui a cultura a vários talhões de uma vez e mostra um resumo das mudanças antes de concluir [C4].

### 2.3 Importação
- **Aegro:** importa KML [A2]:
  - todas as áreas do arquivo vêm marcadas, e o usuário desmarca as que não quer;
  - corrige nome e área, agrupa e salva.
  - Shapefile não está confirmado.
- **Cropwise:**
  - Financials importa shapefile em .zip: o usuário marca os campos e importa [C2];
  - Explorer importa uma fazenda por vez, sem limite de campos [C15].
- **Deere:** desenho, shapefile ou "de operação anterior" [D9].
- **FieldView (2016):** .zip de shapefiles na Data Inbox; o usuário escolhe os campos e recebe o aviso de quantos entraram [F3].
- **Planilha de cadastros com prévia por linha:** nenhuma das páginas lidas mostra.

### 2.4 Máquinas e implementos
- **Deere:**
  - Equipamentos tem as abas Máquinas e Implementos, e clicar na linha (não na caixa de seleção) abre o painel de detalhes [D6];
  - para adicionar, o usuário informa o número de série ou lê a plaqueta com a câmera, e modelo, marca e tipo vêm preenchidos; sem número de série, digita nome, modelo, marca e tipo [D4][D5][D15];
  - registros duplicados se mesclam: o usuário escolhe o registro que fica, revisa e pode desfazer [D6].
- **Aegro:**
  - Patrimônio tem os tipos Máquina, Silo, Benfeitoria, Pivô, Veículo e Estação meteorológica;
  - só o nome e o tipo de máquina são obrigatórios; há uma caixa "Implemento – não motorizado";
  - horímetro para máquina, silo, benfeitoria e pivô; odômetro em km para veículo;
  - a primeira foto aparece ao lado do nome na lista [A9];
  - a lista fica à esquerda, agrupada por tipo, e marcar um tipo ou um item filtra o cartão de resumo (Painel, Eventos, Custos) [A10];
  - antes de arquivar, confere atividades e alertas pendentes [A11];
  - no app, o cadastro pede nome e tipo, com foto opcional [A12].
- **Cropwise:** Equipment pede nome, tipo e situação [C10].
- **Senior:** um único cadastro "Recurso" cobre equipamento, pessoa, insumo e matéria-prima, organizado em grupos (árvore), com o campo "Implemento: Sim/Não" [S3].
- **Vínculo fixo trator–implemento:** nenhuma página lida mostra.

### 2.5 Pessoas e equipes
- **Deere:**
  - o membro da equipe entra por e-mail, com login; o papel define níveis de acesso padrão, que podem ser ajustados;
  - ou entra como "Name Only", sem login, para registro (operadores);
  - várias pessoas podem ser adicionadas de uma vez [D7].
- **Aegro:** usuário com e-mail e perfis que se somam, ou "Apenas Aegrozap", só por WhatsApp e sem e-mail, para tratorista, estoquista e encarregado [A17].
- **Cropwise:** em People só o nome é obrigatório; a habilitação ("License Info") é opcional [C10].
- **Senior:** a pessoa é um recurso do tipo "Humano", com funções de RH [S3].

### 2.6 Produtos e insumos
- **Biblioteca de referência + lista da organização:**
  - **Aegro:** o catálogo global é "alimentado por usuários de todo o Brasil". O usuário digita o nome e a busca cobre o catálogo próprio e o global. Item importado não se edita. Sem correspondência, "Continuar" leva à categoria e aos campos [A13][A14].
  - **Cropwise:** "+ Add Product" busca na lista Cropwise, com ✓ para o que já está na lista e + para adicionar. "Create Custom" só vale para fertilizante e serviço; defensivo ou semente que falte se pede por solicitação [C11][C13].
  - **Deere:** Product Manager tem as abas Variedades, Defensivos, Fertilizantes e Caldas. "Add" abre uma busca para marcar os produtos. Selecionar o produto na tabela abre um painel à direita para editar [D2].
- **Unidade:** no Aegro, a unidade padrão só muda dentro da mesma escala (L ↔ mL, mas não unidade ↔ kg), e a troca não altera lançamentos anteriores [A13].
- **Bula, reentrada e carência:**
  - **Cropwise:** a ficha do produto tem as abas Inventory, Documentation (bula) e REI/PHI (reentrada e carência por cultura). Os valores vêm pré-carregados "pelo valor mais seguro do país" e podem ser editados [C12].
  - **Senior:** carência (dias), princípio ativo e dosagem por unidade ficam no recurso [S3].
- **Saldo na ficha do produto:** a Cropwise mostra "Total available quantity = faturado − aplicado" [C12].
- **Registro no MAPA e embalagem como entidade:** nenhuma página lida mostra. A Cropwise tem preço por "standard package unit" [C11]. A página do Aegro não cita embalagem, princípio ativo nem classe [A13].
- **Calda como cadastro:** a Deere tem [D3].

### 2.7 Fornecedores e parceiros
- **Aegro:**
  - "Fornecedores e emitentes" é um cadastro só, usado por Financeiro, Estoque, Compras e Fiscal; abre de quatro lugares, sempre com o mesmo formulário;
  - CPF/CNPJ é dispensável para lançamento e obrigatório para nota fiscal e Livro Caixa;
  - o apelido é obrigatório, para facilitar a busca;
  - o CEP preenche o endereço;
  - arquivar é bloqueado enquanto houver parcela em aberto, e excluir é definitivo [A15].
- **Cropwise:** em Companies só o nome é obrigatório [C10].
- **Deere:** parceiro é uma organização com quem se compartilham dados, como concessionária ou consultor [D1][D7]. Não é cadastro de fornecedor e não serve de referência para o CD-05.
- **Senior:** cadastro de fornecedor não lido nesta pesquisa.

### 2.8 Locais de estoque
- **Aegro:** um estoque padrão nasce com a propriedade; só o nome é obrigatório; um fornecedor pode servir de local de estoque [A16].

### 2.9 Celular
- **Cropwise:** o app funciona offline e sincroniza uma safra e uma organização por vez [C9]. Permite escolher pela árvore ou pelo mapa, abrir os detalhes do talhão e traçar a rota até ele [C8].
- **Deere:** o app adiciona e edita campos, mas não desenha contorno: ele é desenhado na web ou vem da máquina [D8]. Também adiciona equipamento pelo número de série [D15].
- **Aegro:** o app desenha a área tocando pontos no mapa [A7] e cadastra máquina com foto [A12]. Funcionamento offline não confirmado.

### 2.10 Arquivar, excluir e duplicidade
- **Arquivar** tira o item da lista sem apagar o histórico; o filtro "arquivados" mostra os itens em cinza e permite desarquivar [C6][D11][A11][A15].
- **Excluir:** na Deere, só se exclui o que já foi arquivado, e cliente ou fazenda com campo ativo não pode ser excluído [D11].
- **Duplicidade:**
  - buscar antes de criar [A13][A15];
  - mesclar com prévia de antes e depois: campos, até 5 por vez [D10]; equipamentos, com desfazer [D6]; FieldView [F2].

## 3. O que se repete e o que o nosso PRD já diz
1. **A lista seleciona, o painel mostra e age.** A Deere faz isso em produtos, caldas, equipamentos e campos; a Cropwise, na árvore com Details; o Aegro, no patrimônio, onde a seleção filtra o cartão de resumo. É o nosso "a linha identifica, o painel resolve" de Suprimentos (`engine.py`, aside `role=dialog`). O PRD 4.3 diz: "formulário curto abre painel; processo com várias dependências abre página".
2. **Árvore Fazenda → Talhão (→ parcela) com busca e filtros:** Cropwise e Deere; o FieldView usa cliente, fazenda e campo como nomes. O Aegro é o contraexemplo, porque não tem fazenda como entidade.
3. **Mapa e lista ligados:** app da Cropwise e Deere. O PRD 67.3 e o MAPUX-04 já exigem seleção nos dois sentidos. O mapa amplo (IN-04) pede o complemento abaixo do mapa, não numa coluna lateral (MAPUX-01).
4. **Mínimo obrigatório:** nome e tipo (Aegro; Cropwise; Deere quando não há número de série). O resto é opcional ou só é exigido quando o processo pede (CPF/CNPJ do fornecedor no Aegro). É o que diz o PRD 60.1.
5. **Arquivar em vez de excluir.** Igual ao RF-DAT-001.

## 4. Decisão por prática

| # | Prática (fontes) | Decisão | Motivo: dano evitado ou esforço poupado | Onde |
|---|---|---|---|---|
| B01 | Clicar na fazenda mostra, na mesma tela, os talhões dela e o resumo da fazenda (C3, C7, C8, D9, F1) | **Adotar** | É o pedido do proprietário. Tira a troca entre as abas Fazendas e Talhões e a página separada para ver os talhões de uma fazenda | CD-01; PRD 4.3 |
| B02 | Clicar no item abre um painel lateral com identidade, estado e a ação do momento; processo longo (polígono, parcelas) abre página (D2, D6, D9, C3) | **Adotar** | Reaproveita o componente de Suprimentos. Uma ação primária, no painel. Retorno preserva a seleção (PRD 4.2) | CD-01 a CD-07 |
| B03 | Mapa e lista ligados (C8, D9, D11) | **Adaptar** | As referências põem a lista à esquerda do mapa. O nosso PRD pede seleção nos dois sentidos e o complemento abaixo do mapa (MAPUX-01/04). A 390 px os dois não cabem lado a lado: alterna Lista e Mapa, mantendo a seleção | CD-01; PRD 67.3 |
| B04 | Cor do talhão no mapa pela cultura da safra (A5, D13, C7) | **Adaptar** | Ajuda a reconhecer o talhão rápido, mas no cadastro o que pede ação é o polígono. Cor pela cultura da safra aberta e marca própria para "sem polígono" e "área divergente" | CD-01 |
| B05 | Fazenda como agrupador livre de talhões (A3, A4) | **Descartar** | A fazenda guarda documento, CAR, fuso, água e reserva (FO-01). Um agrupador livre não guarda isso e permite talhão "sem fazenda" | CD-01; FO-01 |
| B06 | Área informada × área do contorno; um contorno ativo; versões (C1, A1, D9) | **Adotar (já existe)** | Manter "área cultivável × polígono com motivo acima de 1 %" e a versão que preserva as O.S. emitidas. Falta só mostrar isso no painel do talhão | CD-01; RF-DAT-002 |
| B07 | Mudar a área de talhão em safra pergunta a quais safras a mudança se aplica (A8) | **Adaptar** | Perguntar só se houver safra aberta com parcela no talhão. Safra encerrada nunca muda: protege a integridade do fato registrado | CD-01; PL-01 |
| B08 | A parcela nasce do talhão e se divide por corte; cultura em lote com resumo antes de concluir (C4, C5) | **Adotar onde já está** | Isso já acontece no Planejar safra (etapa 2, todos os talhões). O cadastro só consulta as parcelas; um segundo caminho criaria duas fontes | PL-01; CD-01 |
| B09 | Importar KML ou shapefile: tudo marcado, desmarcar, corrigir nome e área, salvar, aviso de quantos entraram (A2, C2, F3) | **Adotar** | Menos digitação. A prévia já é exigida (FO-40). Escolher a coluna que dá o nome evita renomear um a um | CD-01; IN-04; FO-40 |
| B10 | Desenho por polígono, círculo de pivô (centro e raio) e corte; busca por coordenada (C1, D9, A1) | **Adaptar** | Pivô é comum: a Lagoa Grande tem 23. Círculo por centro e raio, como o "Círculo do KML" que já temos. No protótipo, simulado | CD-01 |
| B11 | Contorno vindo de base pública de imóveis, de detecção por imagem ou de operação da máquina (C1, C15, D9, D12) | **Adiar** | No Brasil, o equivalente seria CAR/SICAR ou SIGEF, com fonte, licença e precisão a homologar (PRD 60.2: consulta pública não é integração pronta). A operação da máquina depende de integração com equipamentos | CD-01 |
| B12 | Máquinas, Implementos e Instalações como filtro rápido de uma lista de ativos; a linha abre o painel (D6, A9, A10, S3) | **Adotar** | Um toque para filtrar. O CD-03 já inclui instalações (pivôs, bombas). O conjunto máquina + implemento fica no detalhe, como o PRD manda | CD-03 |
| B13 | Selecionar um grupo filtra os itens e o resumo (tipo → ativos; A10) | **Adotar como regra geral** | A mesma lógica do B01 em todos os cadastros com grupo: fazenda → talhões, tipo → ativos, equipe → pessoas, categoria → produtos | CD-01 a CD-06 |
| B14 | Ler a plaqueta ou o código com a câmera e preencher o modelo (D4, D5) | **Adaptar** | "Código físico: leitura" (AGENTS §3.3): ler o código patrimonial no app. Preencher o modelo por base de fabricante fica adiado, porque não há base licenciada | CD-03; app |
| B15 | Contador conforme a classe: horímetro (máquina, pivô, silo) ou km (veículo) (A9) | **Adotar** | Evita contador na unidade errada. Já previsto em "Configurar contador" | CD-03 |
| B16 | Foto do ativo na lista (A9, A12) | **Adiar** | Ajuda a reconhecer o ativo no campo, mas exige guardar arquivos (custo), e o protótipo não tem fotos sintéticas | CD-03 |
| B17 | Mesclar duplicados com prévia e desfazer (D6, D10, F2) | **Adiar** | Faz sentido no software real, com dados importados. No protótipo, evitar a duplicata na criação (B19) | CD-01, CD-03, CD-05; RF-DAT-007 |
| B18 | Pessoa sem login, só para registro; o acesso é outro passo (D7, A17, C10) | **Adotar (já no PRD)** | "Pessoa cadastrada não recebe login por consequência" (CD-04). O acesso fica no CF-01 | CD-04; CF-01 |
| B19 | Buscar antes de criar: digitar o nome procura na lista própria e na biblioteca; sem resultado, "Cadastrar diferente" (A13, A15, C11, D2) | **Adotar** | Evita duplicidade e digitação. É o "Adicionar da biblioteca / Cadastrar diferente" do PRD 60.1 | CD-02, CD-05, CD-06 |
| B20 | Criar no contexto: o mesmo formulário abre de onde a falta aparece e volta ao fluxo (A14, A15, C13) | **Adaptar** | Poupa troca de tela (já fazemos com "Cadastrar fazenda…" a partir do talhão). Defensivo e semente exigem identidade (registro, formulação): nenhum atalho cria produto incompleto (PRD 60.3) | CD-05, CD-06 |
| B21 | Várias pessoas de uma vez (D7) | **Adaptar** | Cadastrar a equipe com várias pessoas numa tela (nome e função), com dados pessoais mínimos (FO-23) | CD-04 |
| B22 | Acesso só por WhatsApp para quem não usa o sistema (A17) | **Adiar** | Enviar mensagem real exige autorização do proprietário (AGENTS §2) | CD-04; CF-01 |
| B23 | Catálogo global alimentado pelos próprios usuários (A13) | **Descartar** | Item global precisa de fonte, versão e curadoria (PRD 60.3). Nome parecido não prova que é o mesmo produto | CD-06 |
| B24 | A unidade padrão só muda dentro da mesma grandeza e não reescreve lançamentos (A13) | **Adotar** | Protege estoque e custo (ENG-013). "Unidade comercial não determina dose" (PRD 60.3) | CD-06 |
| B25 | Ficha do produto com bula, reentrada e carência por cultura (C12, S3) | **Adaptar** | Mostrar por cultura, com fonte e versão (AGROFIT, bula). Na Cropwise o valor é editável à vontade; aqui o valor da bula é o piso legal, e o ajuste local só pode ser mais restritivo, com motivo. Proposta a confirmar no PRD (AG-07) | CD-06; AG-07 |
| B26 | Saldo na ficha do produto (C12) | **Adaptar** | O produto não tem saldo editável (FO-25). O painel mostra "Ver saldos e lotes" (SU-03), sem número próprio | CD-06 |
| B27 | Calda como item de cadastro (D3) | **Descartar** | A calda é receita com dose e aprovação agronômica (AG-04, O.S.). "Último valor" nunca vale para dose | CD-06 |
| B28 | Trocar no app o produto de uma aplicação já registrada (D2) | **Descartar** | Fato registrado só muda por correção do domínio, com histórico | — |
| B29 | Documento fiscal exigido só quando o processo pede; CEP preenche o endereço; apelido para busca (A15) | **Adaptar** | Obrigatório conforme o processo (PRD 60.1). Mas o CPF/CNPJ é a chave contra duplicidade (RF-DAT-005): exigir para homologar fornecedor e para documento fiscal, e avisar quando faltar | CD-05 |
| B30 | Arquivar em vez de excluir; arquivar bloqueado por dependência concreta (parcela em aberto, atividade pendente, campo ativo) (A11, A15, C6, D11) | **Adotar** | RF-DAT-001: inativar bloqueia novos usos e conserva a consulta. A trava fica só onde protege dinheiro ou um fato (AGENTS §4), mostrando a dependência e quem resolve | CD-01 a CD-07 |
| B31 | Faixa "precisa de atenção" com o que falta: talhão sem contorno, fazenda sem talhão (D11, D14, F2) | **Adotar (já existe)** | Acrescentar "fazenda sem talhão" ao que já mostramos | CD-01 |
| B32 | Local de estoque padrão criado com a fazenda (A16) | **Adotar** | Poupa um cadastro antes do primeiro recebimento; o nome continua editável. Fornecedor como local fica **adiado**: custódia em terceiro é regra de Suprimentos | CD-06; SU |
| B33 | App que sincroniza uma safra por vez e funciona offline (C9) | **Adiar** | Vale para o PWA do software real (Dexie, Workbox); o protótipo não tem modo offline | app |
| B34 | Desenhar o contorno no celular tocando pontos (A7) | **Descartar para o contorno oficial** | A precisão do toque é baixa para uma área que vira custo e dose. No celular: consultar, localizar e registrar observação. O contorno oficial vem de arquivo, da tela grande ou da máquina | CD-01; app |
| B35 | Duplo clique para abrir; quadro ao passar o mouse sobre o mapa (S2, S5) | **Descartar** | Não existem no toque. Um toque seleciona e abre o painel (PRD 4.3) | todos |
| B36 | Formulário único com dezenas de campos e tabelas pré-requisito (S1, S4) | **Descartar** | É o que torna o cadastro "não intuitivo". Campos avançados recolhidos e só o obrigatório do processo (PRD 60.1). Os campos legais que o Senior traz (CAR, INCRA, registro do imóvel) continuam no detalhe da fazenda | todos |

## 5. Padrão resultante (insumo para o desenho; não é decisão do proprietário)
- **Uma tela por cadastro, em três camadas:**
  1. grupos numa lista curta (fazendas, tipos de ativo, equipes, categorias), com um toque para selecionar e "Todas" para a visão geral;
  2. os itens do grupo na grade, com filtro, ordenação e unidade na célula (grades da frente TABELAS-FOCO);
  3. o painel aberto ao tocar no item, com estado, uma ação primária e "Abrir página" quando o processo for longo.
- **CD-01:**
  - selecionar a fazenda mostra o resumo dela (área, documentos pendentes, água) e os talhões dela, em lista ou mapa;
  - tocar no talhão abre o painel do talhão: área cultivável × polígono, versão, parcelas da safra aberta e próxima ação;
  - "Todas" mantém a árvore atual, com subtotal por fazenda.
- **A 390 px:** os grupos viram seletor no topo (lista curta, um toque), a grade vira cartões, e o painel ocupa a tela com Voltar, que preserva a seleção (PRD 4.2).
- **Medir antes e depois**, em cliques e caracteres digitados no teste ponta a ponta (AGENTS §3.3):
  - ver os talhões da Lagoa Grande;
  - achar o talhão sem polígono e definir o contorno;
  - cadastrar um implemento;
  - adicionar um defensivo da biblioteca.
- **Depende de** TABELAS-FOCO (grades de Cadastros) e da frente DS (separadores, hover verde, retorno visual, g2dica).

## 6. Lacunas
- **O PRD vai além das cinco referências** (as páginas lidas não mostram nada a copiar nestes pontos):
  - registro no MAPA no cadastro do produto;
  - embalagem como entidade separada;
  - conjunto máquina + implemento;
  - habilitação vencida bloqueando alocação;
  - importação de planilha com correção de causa repetida em lote (CADN-07 a CADN-11, v3.10/3.11 em revisão).
- **AGROFIT (MAPA):** a página de consulta devolveu 403 ao acesso automático em 09/10/2026. Não foi reconferida aqui; o PRD 60.2 já a indica como fonte.
- **Avaliações de usuários** (G2, Capterra, Reclame Aqui) não foram pesquisadas nesta etapa.

## 7. Fontes (todas acessadas em 09/10/2026)
"Data" é a data que a própria página mostra; "—" quando não mostra.

**Aegro: central de suporte** (aegro.com.br/suporte)

| ID | Página | Data | URL |
|---|---|---|---|
| A1 | Como adicionar uma área manualmente no Aegro? | 05/08/2026 | https://aegro.com.br/suporte/cadastros/como-adicionar-uma-area-manualmente-no-aegro/ |
| A2 | Como importar uma área por arquivo KML? | 05/08/2026 | https://aegro.com.br/suporte/cadastros/como-importar-uma-area-por-arquivo-kml/ |
| A3 | Como utilizar o Agrupador de Áreas? | 05/08/2026 | https://aegro.com.br/suporte/cadastros/como-utilizar-o-agrupador-de-areas/ |
| A4 | Como organizar duas ou mais fazendas dentro de uma mesma propriedade | 05/08/2026 | https://aegro.com.br/suporte/cadastros/como-organizar-duas-ou-mais-fazendas-dentro-de-uma-mesma-propriedade/ |
| A5 | Como funciona o Mapa do Aegro e qual é o significado das suas diferentes cores? | 05/08/2026 | https://aegro.com.br/suporte/cadastros/como-funciona-o-mapa-do-aegro-e-qual-e-o-significado-das-suas-diferentes-cores/ |
| A6 | Painel de Controle do Talhão | 05/08/2026 | https://aegro.com.br/suporte/safras/painel-de-controle-do-talhao/ |
| A7 | Como cadastrar uma área no aplicativo? | 05/08/2026 | https://aegro.com.br/suporte/cadastros/como-cadastrar-uma-area-no-aplicativo/ |
| A8 | Como editar a área dentro da safra? | 05/08/2026 | https://aegro.com.br/suporte/safras/como-editar-a-area-dentro-da-safra/ |
| A9 | Como cadastrar os seus patrimônios | 21/09/2026 | https://aegro.com.br/suporte/patrimonio-maquinas/como-cadastrar-os-seus-patrimonios/ |
| A10 | Como funcionam os filtros nos Patrimônios | 19/08/2026 | https://aegro.com.br/suporte/patrimonio-maquinas/como-funcionam-os-filtros-nos-patrimonios/ |
| A11 | Como gerenciar um patrimônio | 19/08/2026 | https://aegro.com.br/suporte/patrimonio-maquinas/como-gerenciar-um-patrimonio/ |
| A12 | Como cadastrar um maquinário no aplicativo? | 05/08/2026 | https://aegro.com.br/suporte/patrimonio-maquinas/como-cadastrar-um-maquinario-no-aplicativo/ |
| A13 | Entenda o Catálogo | 05/08/2026 | https://aegro.com.br/suporte/estoque/entenda-o-catalogo/ |
| A14 | Como criar um novo elemento no catálogo | 05/08/2026 | https://aegro.com.br/suporte/estoque/como-criar-um-novo-elemento-no-catalogo/ |
| A15 | Como gerenciar fornecedores | 05/08/2026 | https://aegro.com.br/suporte/estoque/como-gerenciar-fornecedores/ |
| A16 | Como gerenciar um locais de estoque | 05/08/2026 | https://aegro.com.br/suporte/estoque/como-gerenciar-um-locais-de-estoque/ |
| A17 | Como adicionar pessoas à minha equipe | 05/08/2026 | https://aegro.com.br/suporte/equipe-permissoes/como-adicionar-pessoas-a-minha-equipe/ |

**Cropwise (Syngenta Digital): central de ajuda dos EUA.** O HTML devolveu 403 ao WebFetch; o mesmo artigo foi lido pela API pública da central (`/api/v2/help_center/en-us/articles/{id}.json`).

| ID | Página | Data | URL |
|---|---|---|---|
| C1 | Using Draw and Import Tools to Create a Farm Field Tree | 08/07/2025 | https://help.us.cropwise.com/hc/en-us/articles/7760516120851 |
| C2 | Importing a Farm Field Tree into Cropwise Financials | 08/07/2025 | https://help.us.cropwise.com/hc/en-us/articles/7752656085395 |
| C3 | Farm and Field Details and Cost Analysis | 23/05/2026 | https://help.us.cropwise.com/hc/en-us/articles/26554869014419 |
| C4 | Assigning Crop Zones to Fields | 23/05/2026 | https://help.us.cropwise.com/hc/en-us/articles/7763201319955 |
| C5 | Splitting a Field into Crop Zones | 23/05/2026 | https://help.us.cropwise.com/hc/en-us/articles/21736713352467 |
| C6 | Archiving Farms and Fields | 08/07/2025 | https://help.us.cropwise.com/hc/en-us/articles/23546032242707 |
| C7 | Property Maps | 08/07/2025 | https://help.us.cropwise.com/hc/en-us/articles/36530845440531 |
| C8 | Viewing Information and Records by Field (app) | 20/05/2026 | https://help.us.cropwise.com/hc/en-us/articles/7763032015763 |
| C9 | Getting Started with the Cropwise Financials Mobile App | 20/05/2026 | https://help.us.cropwise.com/hc/en-us/articles/42214993459987 |
| C10 | Adding People, Companies and Equipment | 23/05/2026 | https://help.us.cropwise.com/hc/en-us/articles/7821587498387 |
| C11 | Managing the Product List | 06/03/2026 | https://help.us.cropwise.com/hc/en-us/articles/23729648972179 |
| C12 | Product Details | 23/05/2026 | https://help.us.cropwise.com/hc/en-us/articles/9542886181267 |
| C13 | Creating Custom Products in Production Records | 23/05/2026 | https://help.us.cropwise.com/hc/en-us/articles/12122280494611 |
| C14 | Q3 2026 CWF Release Notes (etiquetas nas zonas de cultivo; correção da área informada × contorno) | 22/09/2026 | https://help.us.cropwise.com/hc/en-us/articles/53254044970771 |
| C15 | Cropwise Explorer – Managing Fields in Existing Farms | 02/10/2026 | https://help.us.cropwise.com/hc/en-us/articles/4488834083219 |

**John Deere: documentação oficial** (onlinesupport.deere.com, onlinesupport.ag.deere.com, deere.ca, displaysimulator.deere.com)

| ID | Página | Data | URL |
|---|---|---|---|
| D1 | Operations Center: features | — | https://www.deere.ca/en/technology-products/precision-ag-technology/operations-center/features/ |
| D2 | How Do I Create and Edit Products? | — | https://onlinesupport.deere.com/operations-center-7f4abdfc/setup-04811888/products-b8442ebb/how-do-i-create-and-edit-products-ac5a3fc0 |
| D3 | How Do I Create and Edit a Tank Mix? | — | https://onlinesupport.deere.com/operations-center-7f4abdfc/setup-04811888/products-b8442ebb/how-do-i-create-and-edit-a-tank-mix-7dcb948f |
| D4 | How Can I Add Equipment to My Organization? | © 2024 | https://onlinesupport.deere.com/operations-center-7f4abdfc/setup-04811888/equipment-0befbfee/how-can-i-add-equipment-to-my-organization-acbd0b4e |
| D5 | Adding Equipment Using the Barcode Scanner Feature | — | https://onlinesupport.deere.com/operations-center-7f4abdfc/setup-04811888/equipment-0befbfee/adding-equipment-using-the-barcode-scanner-feature-000c5f65 |
| D6 | Eliminate Duplicates – Equipment Merge Explained | — | https://onlinesupport.deere.com/operations-center-7f4abdfc/setup-04811888/equipment-0befbfee/eliminate-duplicates-equipment-merge-explained-55044b82 |
| D7 | How Can I Add a Team Member to My Organization | — | https://onlinesupport.deere.com/operations-center-7f4abdfc/setup-04811888/team-03c6cec3/how-can-i-add-a-team-member-to-my-organization-983fd4a6 |
| D8 | Add and Edit Fields in Ops Center Mobile | 18/02/2026 | https://onlinesupport.deere.com/operations-center-7f4abdfc/mobile-aa3f446c/operations-center-mobile-2c2ca671/add-and-edit-fields-in-ops-center-mobile-196df3da |
| D9 | How do I Create, Edit and Import Boundaries? | 16/04/2026 | https://onlinesupport.ag.deere.com/setup-3a38c6a8/land-99ba3fbc/how-do-i-create-edit-and-import-boundaries-3ef8dd9a |
| D10 | How do I Merge Fields and Merge Boundaries in Land | — | https://onlinesupport.ag.deere.com/setup-3a38c6a8/land-99ba3fbc/how-do-i-merge-fields-and-merge-boundaries-in-land-6a5ced13 |
| D11 | How do I archive and delete Clients, Farms, Fields, and/or Field Assets | — | https://onlinesupport.ag.deere.com/setup-3a38c6a8/land-99ba3fbc/how-do-i-archive-and-delete-clients-farms-fields-and-f07458c7 |
| D12 | Boundaries from Parcel Data | — | https://onlinesupport.deere.com/operations-center-7f4abdfc/setup-04811888/land-ca52ba4b/boundaries-from-parcel-data-47c0132d |
| D13 | Boundary Color Settings in Operations Center Web and Mobile | 08/10/2025 | https://onlinesupport.deere.com/operations-center-7f4abdfc/more-d98243cd/map-8880925b/boundary-color-settings-in-operations-center-web-and-mob-7b566a84 |
| D14 | Home – Basics and Navigation (itens de configuração pendente, como contorno faltando) | — | https://onlinesupport.deere.com/operations-center-7f4abdfc/home-aad5d42b/home-basics-and-navigation-048d90fc |
| D15 | Adding Equipment in Operations Center Mobile | © 2024 | https://onlinesupport.deere.com/operations-center-7f4abdfc/mobile-aa3f446c/operations-center-mobile-2c2ca671/adding-equipment-in-operations-center-mobile-29e88d5d |

**Senior: Portal de Documentação, ERP Mega, Agronegócio** (todas sem data na página)

| ID | Página | URL |
|---|---|---|
| S1 | Agronômico – Talhão – Cadastro do Talhão | https://documentacao.senior.com.br/erp-mega/manual-do-usuario/agronegocio/agronomico/talhao/talhao |
| S2 | Agronômico – Consultas – Ficha do Talhão | https://documentacao.senior.com.br/erp-mega/manual-do-usuario/agronegocio/agronomico/consultas/ficha-do-talhao |
| S3 | Global Agrícola – Cadastros – Recurso | https://documentacao.senior.com.br/erp-mega/manual-do-usuario/agronegocio/global-agricola/cadastros/recurso |
| S4 | Agronômico – Fundo Agrícola | https://documentacao.senior.com.br/erp-mega/manual-do-usuario/agronegocio/agronomico/fundo-agricola/fundo-agricola |
| S5 | Agronômico – Consultas – Georreferência (GIS) | https://documentacao.senior.com.br/erp-mega/manual-do-usuario/agronegocio/agronomico/consultas/georreferencia |

**Climate FieldView** (climate.com)

| ID | Página | Data | URL |
|---|---|---|---|
| F1 | Map Your Fields (Getting started) | © 2026 | https://climate.com/en-us/resources/getting-started/fieldview-101-overview/map-your-fields.html |
| F2 | How to Manage Fields & Boundaries in FV Web (PDF) | 02/02/2016 (metadado do PDF) | https://www.climate.com/static/global/assets/static/docs/how-to-manage-fields-using-fv-web-field-manager-da67c75a.pdf |
| F3 | How to Create Field Boundaries Using Shapefiles in Climate FieldView (PDF) | 09/03/2016 (metadado do PDF) | https://www.climate.com/static/global/assets/static/docs/Create%20Field%20Boundaries%20Using%20Shapefiles_4C4K163336-66204be8.pdf |
