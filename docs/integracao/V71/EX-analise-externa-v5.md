# Análise externa, 5ª versão (16/10/2026): delta sobre a 4ª (seção 0, leitura pelas heurísticas, EX-41 e EX-42)

O proprietário colou a 5ª versão em 16/10/2026, no canal do Claude, como arquivo (`prompt-safrion-excelencia.md`, SHA-256 `089b09206673c1e7b1ed219f6515c9ab0b75d7b29260ec9e9fc46c65ffb6a833`), junto com o protótipo `pragas-no-tempo.html` (SHA-256 `8b9e105e7ee7e9f0692c2264b3f41fe45bcb3da1bec3916f23e8a0e72a717f15`, dados sintéticos, copiado em [`insumos/pragas-no-tempo.html`](insumos/pragas-no-tempo.html)).

- **Mantém da 4ª versão** (`EX-analise-externa-v4.md`): EX-01 a EX-40, Anexo A (P01–P66), método, critério de entrada, "não fazer", decisões do proprietário e entrega. A tabela final e a lista do Codex passam a ir até EX-42; o EX-42 entra entre os candidatos ao Gemini real.
- **Abaixo, só o que é novo,** no texto do proprietário.
- **Como entra:** é insumo, não requisito; PRD, NAV/DS, protocolo e decisões registradas prevalecem.
- **Onde a seção 0 já está:** [`docs/design-system/diretrizes-ux.md`](../../design-system/diretrizes-ux.md) (pedido de 16/10), que completa o PRD cap. 4, 55, 64, 74 e 75 e o AGENTS §3.3. **Fato conferido em 16/10:** o texto do PRD e do AGENTS na `main` (`c827408`) ainda não cita ISO 9241-210, Carbon, Fluent 2, Double Diamond nem TELA-01; a fonte vigente é o `diretrizes-ux.md` da composição. O que a seção 0 acrescenta (perfis e plataformas, app sem sinal, como medir) entra nesse arquivo, sem lista paralela.

O objetivo não é um software só bonito: é um sistema de gestão agrícola excepcionalmente simples, intuitivo, rápido e eficiente, com a excelência comprovada por indicadores objetivos de usabilidade e produtividade.

0. DIRETRIZES PERMANENTES DE UX, UI E DESIGN SYSTEM
Valem para toda decisão de UX, UI e design system, no protótipo e no software real. A avaliação de 16/10 já as registrou no PRD (cap. 4, 55, 64, 74 e 75) e no AGENTS §3.3. Confira e referencie a fonte vigente; não crie lista paralela.
- ISO 9241-210 (design centrado no usuário) é o método central: o software se adapta à maneira como o usuário trabalha, e não o contrário. Cada fatia passa pelas quatro atividades: contexto de uso, requisitos do usuário, solução e avaliação com usuário real.
- As 10 heurísticas de Nielsen (NN/g) são o critério de projeto e de revisão de toda tela. A gravidade 0–4 da NN/g se liga ao S1–S4 do PRD 22.1. Prioridades:
  - menos carga cognitiva;
  - menos cliques e digitação;
  - navegação intuitiva;
  - consistência entre telas;
  - prevenção de erro;
  - retorno imediato de cada ação;
  - eficiência para iniciante e para quem usa muito.
- O design system é próprio e segue as práticas do IBM Carbon:
  - navegação e organização da informação;
  - tabelas, filtros e formulários;
  - painéis e visualização de dados;
  - botões, menus e componentes interativos;
  - hierarquia visual e tipografia;
  - acessibilidade e responsividade.
  Use o Microsoft Fluent 2 onde ele for melhor (por exemplo, a barra de comandos com ⋯). Não copie o visual de nenhum dos dois: a identidade é do Safrion, moderna e funcional.
- O processo é o Double Diamond: Descobrir → Definir → Desenvolver → Entregar, encaixado no ciclo da fatia. Antes de desenhar ou implementar uma tela, entenda o problema, o contexto operacional e o fluxo real do usuário.
- Simplicidade operacional (regra TELA-01): cada tela responde em segundos a três perguntas:
  1. O que está acontecendo? (estado em palavras)
  2. O que exige minha atenção? (com quantidade e motivo)
  3. Qual ação devo executar agora? (uma primária com verbo)
  A informação certa aparece no momento certo, com a ação certa. A complexidade fica dentro do sistema, não com o usuário.
- Indicadores de excelência. As metas são iniciais e só valem depois de validadas com usuários reais:
  - sucesso na tarefa essencial ≥ 95 %;
  - tempo por tarefa abaixo da linha de base e caindo a cada versão;
  - interações por tarefa nunca acima da versão anterior no mesmo cenário;
  - erros por tarefa ≤ 0,2;
  - facilidade de aprendizado: tempo da 2ª execução ÷ tempo da 1ª ≤ 0,7;
  - satisfação: SUS ≥ 80;
  - acessibilidade: 0 violação séria de WCAG 2.2 AA;
  - desempenho percebido: INP ≤ 200 ms, LCP ≤ 2,5 s e app sem sinal sem travar.
- Perfis e plataformas:
  - a experiência se adapta a gestores, agrônomos, PCP, almoxarife, caldeiro, operadores, líderes e equipes de campo;
  - os perfis usam as mesmas telas com permissões diferentes, sem menus por perfil (P65);
  - a excelência vale para o desktop e para o app de campo.
- Limite: não elimine funcionalidade necessária só para reduzir cliques. Rastreabilidade, segurança, integridade dos dados e regras de negócio ficam.

## Diagnóstico · leitura pelas heurísticas e por perfil

Leitura pelas 10 heurísticas de Nielsen (achados que tocam cada uma):
- H1 Visibilidade do estado.
  - Forte: faixa VEIO DE → FALTA → PRÓXIMA AÇÃO.
  - Lacunas:
    - primária que falha depois do clique (EX-05);
    - recibo de "volta completa" com 14 % da volta (EX-36);
    - "faltam 15 L" ausente no app (EX-38).
- H2 Correspondência com o mundo real.
  - Forte: unidades do campo.
  - Lacunas: falta galão por carga, g por cova e sementes por metro (EX-39); códigos internos na tela (EX-03).
- H3 Controle e liberdade: ações de risco sem motivo, alçada ou Desfazer (EX-33); medidas já marcadas (EX-34).
- H4 Consistência e padrões: dados que se contradizem (EX-01), telas e formulários duplicados (EX-02), vocabulário (EX-03), "Salvar" genérico (EX-37), componentes (EX-41).
- H5 Prevenção de erro: aprovação em lote (EX-32), listas sem filtro (EX-35), cálculos divergentes e dupla alocação (EX-38), clima e calibração (EX-08).
- H6 Reconhecer em vez de lembrar: contexto não herdado (EX-04) e texto livre onde cabe lista (EX-37).
- H7 Flexibilidade e eficiência:
  - turno, abastecimento, NF, romaneio e safra nascendo preenchidos (EX-06, EX-09, EX-11, EX-12, EX-14);
  - visões salvas (EX-31);
  - busca global e atalhos (UX-10, UX-11).
- H8 Estética e minimalismo: painéis por exceção (EX-26), consolidação (EX-02), ajustes menores (EX-40).
- H9 Reconhecer e recuperar erro: bloqueio com motivo antes do clique (EX-05) e conferência por exceção (EX-10).
- H10 Ajuda: sem achado novo além do UX-12.

Por perfil e plataforma:
- agrônomo: caixa única de decisões (EX-31, UX-05, UX-06);
- almoxarife, caldeiro, operador e líder de campo: ficha por papel (EX-39);
- o app de campo hoje cobre só a pulverização. Plantio, adubação, fertirrigação, caldeiro e líder não têm fluxo móvel (EX-39).


## Onda B · EX-41

EX-41 Componentes do design system padronizados (práticas do Carbon, com o Fluent 2 onde for melhor), a partir do que os modais mostraram:
  - Tabela de dados:
    - filtro e ordenação no cabeçalho, agrupar e colunas;
    - uma só forma de filtrar por tela (o CD-04 tem três);
    - barra de ação em lote só com ações permitidas em lote (EX-32).
  - Botões:
    - primária com verbo e objeto;
    - secundárias discretas;
    - destrutivas separadas e no ⋯ (barra de comandos do Fluent);
    - ação indisponível aparece desabilitada com o motivo e quem resolve (EX-05).
  - Formulários (EX-37):
    - rótulo visível, obrigatório marcado e ajuda curta só onde evita erro;
    - unidade como sufixo e teclado decimal (já existem);
    - "Mais opções" para o raro.
  - Painel lateral para detalhe e criação, que já é o padrão. Confirmação só no irreversível.
  - Avisos:
    - aviso na própria linha para o que pede ação;
    - aviso temporário de retorno com Desfazer;
    - nenhuma nota interna na tela.
  - Estado vazio com uma ação; skeleton no carregamento; etapas só onde há etapas reais.
  - Um componente por tarefa: um formulário de recebimento, um de nova safra, um de venda (EX-02).


## EX-42 · funcionalidade nova

EX-42 Manejo × resposta da lavoura no Mapa (camadas "Pragas e doenças" e "Satélite" do IN-04). Funcionalidade nova pedida pelo proprietário. O objetivo é ver o que de fato melhora a lavoura, em nutrição e em controle de pragas e doenças, para o manejo melhorar a cada ciclo.
  - Protótipo de referência para tirar boas ideias. Usa dados sintéticos e não é requisito:
    - link: https://claude.ai/artifact/BhceWUXPoT9BXgTGUCy6LP (versão 2). É privado: o Claude lê com a ferramenta Artifact (action "read").
    - arquivo: pragas-no-tempo.html, que o proprietário anexa ao pedido. É por ele que o Codex lê o protótipo; se o protocolo tiver uma pasta de insumos, salve uma cópia lá.
  - Primeiro melhorar, depois implantar:
    1. Claude e Codex, cada um sozinho, avaliam o protótipo contra o PRD, o NAV/DS, a camada Satélite atual (índices, cena, contraste Talhão/Fazenda/Absoluto e "Ver histórico") e a camada Pragas e doenças atual. Cada um lista o que adotar, adaptar ou descartar e o que falta.
    2. Divergência se resolve por fonte ou reprodução. O Gemini real entra se houver decisão material de domínio: métricas de efeito, janelas de comparação, condições favoráveis por alvo.
    3. O Codex registra o desenho final e as fatias. Só então se implanta, na fase registrada no STATUS, com revisão cruzada.
  - O que o desenho deve cobrir (pontos de partida do protótipo):
    - Barra de tempo arrastável, com teclado, "Reproduzir" e "Hoje", que recolore o mapa:
      - pragas pela última vistoria em relação ao NC;
      - satélite pela última cena válida, com nuvem e "sem imagem" em cinza hachurado, nunca com cor de índice.
    - Gráfico da fazenda e do talhão na mesma linha do tempo:
      - nível × NC em pragas, ou NDVI/NDRE com a faixa P10–P90 no satélite;
      - comparação com a média da fazenda ou dos pivôs do mesmo estádio.
    - Ícones de manejo clicáveis na linha do tempo: defensivo, adubação ou fertirrigação, e operação. Quando se sobrepõem, viram um ícone com contagem. O clique mostra:
      - insumos, dose por ha e total;
      - grupo IRAC/FRAC, entrada e sequência do grupo;
      - calda e equipamento;
      - nutrientes (N, K2O, S, B em kg/ha);
      - clima no dia, com alerta de dia quente e seco para aplicação;
      - o efeito medido e a janela usada: em pragas, vistoria até 10 dias antes → 5 a 14 dias depois; no vigor, cena até 10 dias antes → 10 a 25 dias depois, menos a variação dos pivôs do mesmo estádio;
      - um botão para ir à vistoria ou à cena que mediu o efeito.
    - Faixas de chuva e irrigação (mm) e de clima:
      - temperatura máxima e umidade do ar, dia a dia;
      - marca da condição favorável ao alvo, por exemplo quente e seco (≥ 32 °C e UR < 50 %) para ácaro, ou folha molhada por 8 h ou mais entre 18 e 30 °C para antracnose;
      - no satélite, marca de calor ≥ 35 °C;
      - ao passar o mouse: Tmáx/Tmín, UR, horas de folha molhada, chuva e irrigação.
    - Painel "o que funcionou", até a data da barra:
      - pragas: redução mediana e dias até voltar ao NC, agrupando por produto, por produto e calda, por sequência do grupo ou pelo clima da semana; e o crescimento semanal sem controle nas semanas favoráveis × nas demais;
      - vigor: resposta por programa de adubação, dose de N e estádio; nível de hoje em relação ao estádio; calor × irrigação;
      - sempre com o número de casos, aviso de pouca evidência abaixo de 3 e o texto "associação, não causa".
  - Dados que o sistema real precisa ligar, sem digitação nova:
    - vistorias (AG-01, MB-06);
    - O.S. com apontamento: produto, dose, calda e conjunto;
    - fertirrigação e irrigação (IR-*);
    - estação meteorológica ou API: Tmáx, Tmín, UR, horas de folha molhada, DPV;
    - chuva medida;
    - cenas de satélite com máscara de nuvem (C4);
    - protocolo com o NC por alvo e estádio (AG-05).
  - Regras:
    - valores observados, sem interpolação;
    - janelas e limiares configuráveis por cultura e estádio, validados pelo agrônomo;
    - nenhuma recomendação automática: a decisão continua com o RT.
  - Aceite observável: em até 2 ações, o usuário vê a evolução de um alvo ou índice num talhão, com manejo e clima na mesma linha do tempo, e abre os insumos e doses de qualquer aplicação. Validar com agrônomo real (UX-13).


## Implantação · texto que substitui o da 4ª versão

- Cada item adotado vira uma fatia com ID, persona, arquivos, autor, revisor e aceite observável.
- Cada fatia segue o Double Diamond:
  - Descobrir: contexto de uso e fluxo real do perfil;
  - Definir: aceite medido antes do código;
  - Desenvolver;
  - Entregar: com a medida depois.
- Toda tela nova ou alterada passa pela regra TELA-01 e pelas 10 heurísticas.
- Medida dos indicadores da seção 0:
  - interações por tarefa nos testes ponta a ponta, como na linha de base de 16/10 (UX-03);
  - tempo, sucesso, erros, aprendizado e SUS no teste moderado com 3 a 5 pessoas por perfil (UX-13);
  - acessibilidade por verificação automática, teclado e leitor de tela.
- Para a Onda 0, cada correção ganha um teste de regressão: lote recusado para O.S. com produto; ação de risco exige motivo e alçada; medida não pré-preenchida; lista filtrada por contexto e organização; irrigação fora da tolerância não encerra; O.S., app, ficha e almoxarifado com o mesmo cálculo; recurso único sem dupla alocação; limpeza registrada depois de produto hormonal.
- Siga a fase registrada no STATUS (protótipo ou transferência ao Next), sem evolução paralela.
- Revisão cruzada: quem revisa integra o PR do outro.
- Publique incrementos operáveis no artefato existente, com versão, URL e mudança concreta.
- O PRD só muda quando a decisão alterar um requisito, referenciando o design system e com revisão real.

