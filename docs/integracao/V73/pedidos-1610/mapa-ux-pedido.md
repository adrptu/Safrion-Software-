PROJETO: Safrion (Do Talhão à O.S.)
PEDIDO: Mapa da fazenda com UX e UI de excelência — passar o mouse e entender, clicar e detalhar, sem perder o contexto

CONTEXTO
- Pedido do proprietário: melhorar a UX, a UI e o design do mapa com os talhões. Passar o mouse sobre o talhão mostra o essencial; clicar detalha; usar recursos visuais intuitivos, como no protótipo do Raio-X.
- O Mapa (IN-04) é a entrada do gestor (UX-05) e tem a barra com 9 camadas (decisão fixa): Integrado, Satélite, Solo, Pragas e doenças, Ordens de serviço, Irrigação, Estádio, Colheita e produtividade, Custos.
- A seção "O QUE JÁ EXISTE" resume a leitura do código do protótipo; o detalhe está no anexo-mapa-analise.md. Confirme cada item no código vigente antes de usar.

REFERÊNCIAS PARA TIRAR BOAS IDEIAS (não são requisito)
- Protótipo principal: https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm (versão 1792184197-5a81): IN-04 e as outras telas com mapa listadas abaixo.
- Protótipo do Raio-X: https://claude.ai/artifact/BhceWUXPoT9BXgTGUCy6LP (versão 3), mais o arquivo pragas-no-tempo.html, que o proprietário anexa. O que vale observar nele:
  - cada talhão é um botão, com número grande, valor e estado em texto dentro do desenho;
  - selos no talhão para manejo recente (defensivo ou adubação nos últimos 10 dias);
  - hover e foco de teclado mostram o mesmo cartão: área, estádio, valor da camada, estado, data da vistoria ou da cena, manejo recente e "Clique para ver a evolução";
  - o clique seleciona (contorno forte e aria-pressed) e abre o detalhe no painel ao lado, sem sair do mapa; clicar de novo ou Esc fecha; "‹ Todos os talhões" volta;
  - o painel sem seleção mostra a visão da fazenda (o Raio-X ou o ranking da camada), e cada item leva ao talhão;
  - linha do tempo arrastável que recolore o mapa, com ícones de manejo clicáveis;
  - nuvem e "sem dado" em cinza hachurado, nunca com cor de índice; legenda com os valores.
  Os links são privados: o Claude lê com a ferramenta Artifact (action "read"); o Codex lê pelo arquivo anexado ou pela cópia do protocolo.

ORDEM DE TRABALHO: PRIMEIRO MELHORAR, DEPOIS IMPLANTAR
1. Claude e Codex, cada um sozinho, avaliam o mapa atual contra este desenho, o PRD, o NAV/DS, a skill de indicadores de satélite e as 10 heurísticas. Cada um lista o que adotar, adaptar ou descartar e o que falta, camada por camada.
2. Divergência se resolve por fonte ou reprodução. O Gemini real entra só em decisão material de fluxo ou acessibilidade. Pacote mínimo, sem dados reais.
3. O Codex registra o desenho final e as fatias no checkpoint (só ele edita o checkpoint).
4. Implantação na fase registrada no STATUS, primeiro no protótipo, com revisão cruzada.
Não simule o Codex nem o Gemini.

1. O PADRÃO DE INTERAÇÃO DO TALHÃO (igual em todas as camadas e telas com mapa)
Desenho
- Polígono real do talhão (ou pivô), preenchido pela camada, com contorno fino e o número grande no centro, com halo para ler sobre qualquer cor.
- Dentro do desenho, no máximo 3 linhas: número, valor da camada com unidade, estado em texto curto. Em zoom pequeno, só o número.
- Selos pequenos no canto para o que pede atenção: manejo recente, O.S. em andamento, alerta. Cada selo com ícone e significado na legenda.
- Sem dado, nuvem ou sem lavoura: padrão hachurado ou cor neutra, nunca a cor de um valor.

Passar o mouse (e foco de teclado, com o mesmo conteúdo)
- Contorno realçado no talhão e cursor de mão, em menos de 100 ms.
- Cartão flutuante com o essencial para decidir se vale clicar:
  - número, área, cultura e estádio;
  - valor da camada com unidade, estado em texto e data do dado (vistoria, cena, apontamento);
  - comparação curta quando ajuda: "2,1× o NC" ou "−0,04 de NDVI em 15 dias";
  - manejo recente ou O.S. em andamento;
  - a dica "Clique para detalhar".
- O cartão nunca é cortado pela borda da tela nem cobre o talhão; some ao sair; não tem ação dentro (ação fica no detalhe).

Clicar (ou Enter no talhão focado)
- Seleciona: contorno forte, aria-pressed, número em destaque. O mapa não muda de zoom sozinho.
- Abre o detalhe do talhão no painel lateral (embaixo, no celular), sem sair do mapa: estado, valor, série no tempo, manejo e a ação primária da camada (por exemplo, "Decidir controle" em Pragas, "Criar vistoria" em Satélite, "Abrir O.S." em Ordens de serviço).
- "Abrir talhão ›" leva ao detalhe completo (CD-01det), e voltar devolve o mapa como estava: camada, data, zoom, seleção e filtros.
- Clicar de novo no talhão, Esc ou "‹ Todos os talhões" fecha o detalhe.
- A URL guarda camada, data e talhão selecionado, para compartilhar e voltar.

Seleção de vários talhões (só onde há ação em lote real)
- Shift + clique ou "Selecionar no mapa" (laço ou retângulo) marca vários talhões; uma barra mostra "4 talhões · 182 ha" e as ações possíveis, por exemplo "Criar O.S. para os 4" (uma O.S. por talhão, P23) ou "Criar vistoria".
- A aprovação agronômica continua individual (decisão fixa): o lote cria rascunhos, não libera.

Legenda que trabalha
- Cada classe da legenda mostra a contagem de talhões e a área ("Acima do NC · 5 talhões · 312 ha").
- Passar o mouse numa classe destaca os talhões dela; clicar filtra o painel por ela; clicar de novo limpa.

Navegação e busca
- Busca de talhão por número ou nome ("P12", "T4"): centraliza e seleciona.
- Trocar de camada mantém zoom, data e seleção.
- Teclado: Tab entra no mapa; setas andam entre talhões vizinhos; Enter seleciona; Esc fecha; "/" busca.

Celular e campo
- Sem depender de hover: o toque seleciona e abre o detalhe numa folha inferior; toque longo mostra o cartão de resumo.
- Alvos de toque de 48 px ou mais, texto legível ao sol, "você está aqui" quando o GPS estiver ligado.

Acessibilidade
- Cada talhão é um botão com nome acessível completo: "P4, 73 ha, mamão em produção, ácaro 23 % das folhas, acima do NC, vistoria em 19/09".
- Estado sempre em texto além da cor; contraste do número sobre o preenchimento; foco visível; nada só no hover.

Desempenho
- Hover e seleção em menos de 100 ms; troca de camada sem recarregar a página; rótulos sem sobreposição; sem salto de layout.

2. POR CAMADA (o que o hover e o clique mostram e qual é a ação primária)
O desenho final define, para cada uma das 9 camadas: cor e legenda, conteúdo do cartão de hover, seções do detalhe no painel e ação primária. Ponto de partida:
- Integrado: o pior estado entre as camadas e o motivo ("ácaro acima do NC · O.S. atrasada"); ação: a do motivo principal.
- Satélite: índice, classe, cena e nuvem, variação; ação: "Ver histórico" ou "Criar vistoria" na mancha (skill de indicadores de satélite).
- Solo: última análise, principais limitações (V %, P, K), recomendação; ação: "Ver análise".
- Pragas e doenças: nível × NC, data da vistoria, tendência, aplicação recente, risco em 7 dias (EX-43); ação: "Decidir controle" quando acima do NC.
- Ordens de serviço: O.S. ativas, fase, atraso, % executado; ação: "Abrir O.S.".
- Irrigação: lâmina × necessidade, último turno, falha; ação: "Abrir turno" ou "Ajustar".
- Estádio: estádio atual e próximo, DAE; ação: "Ver calendário".
- Colheita e produtividade: sc/ha ou t/ha, estimado × colhido, umidade; ação: "Abrir romaneios".
- Custos: custo/ha realizado × planejado, parcial quando faltar dado; ação: "Ver custo do talhão".

3. O QUE JÁ EXISTE NO PROTÓTIPO (evidência)
Leitura do código da versão 1792184197-5a81. O inventário completo, com linhas de código, 30 defeitos (D1–D30) e 15 oportunidades, está no arquivo anexo-mapa-analise.md, que o proprietário anexa. Confirme no código vigente; o que depende do navegador está marcado nele.
Telas com mapa ou forma de talhão:
- IN-04: Santa Rita em SVG esquemático (formas desenhadas à mão); Lagoa Grande, a fazenda padrão, em MapLibre 5.9 baixado do CDN, com imagem RGB e pixels de lagoa_s2.json num canvas. Boa Vista sem geometria.
- CD-01 (visão Mapa): SVG estático com outras coordenadas; o clique abre o formulário de edição, não o detalhe CD-01det.
- CD-01det: a mesma forma (clip-path) para todo talhão, inclusive pivô.
- PL-06 e CA-01 (visão Mapa): SVG estático; no CA-01 os valores estão escritos no HTML e a paleta de fases difere da do IN-04.
- AG-01det: pontos da rota posicionados pelo índice, não pelo GPS.
- MB-*: nenhuma tela de campo mostra mapa.
O que o mapa faz bem hoje e deve ser preservado:
- 9 camadas com faixa de filtros, KPIs, fonte (ⓘ) e link de módulo; rótulo da camada sempre visível sobre o talhão.
- Clique seleciona e abre o painel lateral (384 px) com o detalhe da camada; trocar de camada mantém a seleção; contexto salvo ao voltar.
- Na camada Ordens de serviço, o próximo passo (Liberar, Aprovar, Iniciar, Apontar, Enviar conferência, Encerrar) roda no próprio mapa, com confirmação.
- Seleção de vários talhões com soma de área e "Programar vistoria nas áreas".
Defeitos principais (os números remetem ao anexo):
- Hover: nenhuma dica em nenhum dos mapas; a exclusão é proposital no código ("polígono do mapa não vira dica"). Na Lagoa Grande, só o cursor muda; na Santa Rita, o realce some sob os pixels. O valor do pixel só aparece com clique (D3).
- Teclado e leitor de tela: na Lagoa Grande (padrão), pivôs no canvas sem foco e marcadores role="img"; sem lista nem busca, o painel é inalcançável sem mouse (D1). Na Santa Rita, botões dentro de svg role="img" (D2). Abas de camada sem o padrão ARIA completo (D21).
- Zoom da Santa Rita é CSS de 1× a 2× sem pan: as bordas ficam inalcançáveis (D4). Tela cheia só na Santa Rita (D5). "Todas" mostra só a Santa Rita (D6).
- Satélite: contraste padrão "Talhão" com nomes absolutos ("Falha"), então todo talhão parece ter falha; legenda sem valores; o painel usa a classe absoluta, e a mesma área fica vermelha no mapa e "Bom" no painel (D9). Pixel anunciado como 10 m, mas cada célula da Santa Rita tem cerca de 1,13 ha (D10). Mancha fixa no T7, sobre o rótulo (D11).
- Destinos que perdem contexto: "Ver histórico" leva ao AG-06, que é de pragas (D7); "Nova O.S. neste talhão" e "Abrir ordens" abrem sem o talhão, embora a O.S. aceite #tal= (D8); #talhao= não troca a fazenda (D18).
- Cores: "sem dado" igual ao fundo (contraste 1,0:1); a mesma cor com significados diferentes entre camadas (amarelo é alerta e também "produção contínua"); paleta de estado não segura para daltonismo (D14, D15). Na Lagoa Grande, a legenda não bate com o mapa (opacidade 55 %, nuvem sem hachura) (D13). Custos e Colheita sem escala de cor: o valor só está no rótulo.
- Seleção: clique no fundo e Esc não desmarcam (D16); seleção e câmera fora da URL (D17); "Medir" não mede e o resultado some num aviso de 4,5 s, mudo para leitor de tela (D19); painel sem Esc nem foco, nascendo fora da tela no estreito (D20).
- Toque: ferramentas com cerca de 29 px, zoom 36 px, fechar 30 px (D22); legenda bloqueia cliques no rodapé do mapa (D23).
- Rótulos: textos cortados e encolhidos com o SVG; na Lagoa Grande, sem regra de colisão nem por zoom (D12, D28).
- Mesmo pivô com três nomes: P1, Pivô 1 e PV01 (D27). Quatro desenhos diferentes da Santa Rita entre telas.
- O mapa padrão depende do CDN em tempo de execução, sem indicador de carga do JSON de 2,5 MB (D26).
Oportunidades priorizadas pela análise (ver o anexo):
1. "Ir para talhão": lista ou busca acessível sincronizada com o mapa.
2. Cartão rápido no hover e no foco, e inspetor de pixel no Satélite e no Solo.
3. Um só motor de mapa (MapLibre) com pan, enquadrar e tela cheia, empacotado para funcionar sem CDN.
4. Contraste honesto: padrão Fazenda ou Absoluto na visão da fazenda, legenda sempre com valores, painel na mesma escala do mapa.
5. Destinos com contexto (#tal=, histórico real do índice) e links de módulo em todas as camadas.
6 a 15. Fazenda coerente; paleta semântica única; legenda fiel e filtrável; escala de cor em Custos e Colheita; regras de rótulo; manchas por dados; seleção previsível; URL como estado; ferramentas com retorno e alvos de 44 px; um componente de mapa comum a IN-04, CD-01, CA-01, PL-06 e AG-01det.

4. ACEITE OBSERVÁVEL
- Em qualquer camada, passar o mouse (ou focar com Tab) num talhão mostra o cartão em menos de 100 ms, sem corte, com valor, estado em texto e data do dado.
- Um clique abre o detalhe ao lado com a ação primária da camada; voltar devolve o mapa igual.
- Em 2 ações, o gestor vai do mapa à decisão do talhão mais crítico da camada.
- Teclado e leitor de tela percorrem os talhões com nome acessível completo.
- No celular, tudo funciona por toque.
- Os defeitos D1 a D30 do anexo estão fechados, ou cada um tem o motivo de ficar.
- Teste com 3 a 5 usuários por perfil (UX-13): sucesso ≥ 95 % em "achar o talhão pior e abrir o detalhe" e em "comparar dois talhões".

5. NÃO FAZER
- Mudar a barra de 9 camadas ou criar camada nova sem decisão registrada.
- Abrir modal por cima do mapa para o detalhe do talhão, ou navegar para outra tela perdendo o contexto.
- Colocar ações dentro do cartão de hover.
- Cor sem texto, ou cor de valor para "sem dado".
- Zoom ou recentralização automática sem pedido.

6. ENTREGA (no canal registrado)
- Desenho final por camada, com o que Claude e Codex mudaram e por quê.
- Fatias, com autoria e revisão.
- Medidas antes e depois (cliques até o detalhe, tempo até achar o talhão, acessibilidade).
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado.
- Suposições e pendências, cada uma com o gatilho de retomada.
