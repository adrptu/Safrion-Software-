PROJETO: Safrion (Do Talhão à O.S.)
PEDIDO: Raio-X do alvo — o que faz cada praga ou doença subir e descer, medido nos dados da própria fazenda

CONTEXTO
- O EX-42 (Manejo × resposta da lavoura no Mapa) põe lado a lado, na mesma linha do tempo, o nível do alvo, as aplicações, as adubações, a água e o clima. O usuário vê os dados, mas ainda tira a conclusão sozinho.
- Este pedido dá o passo seguinte: um motor que cruza todas as variáveis com a evolução de cada alvo e entrega, em linguagem do produtor, o que faz o alvo aumentar e o que faz diminuir. Cada achado vem com tamanho do efeito, janela de tempo, limiar, confiança e a evidência clicável.
- O pedido é do proprietário: correlacionar temperatura, umidade do ar, chuva, irrigação, aplicações, adubações e o resto do que o sistema já registra, para entregar ao usuário uma inteligência real, baseada nos dados, sobre cada alvo em análise.

REFERÊNCIAS PARA TIRAR BOAS IDEIAS (não são requisito)
- Protótipo principal: https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm. Ver o IN-04 (camada Pragas e doenças), o AG-01 (monitoramento), o AG-05 (protocolo e NC por alvo) e o MB-06 (vistoria no app).
- Protótipo do Raio-X: https://claude.ai/artifact/BhceWUXPoT9BXgTGUCy6LP (versão 3), mais o arquivo pragas-no-tempo.html, que o proprietário anexa. Os links são privados: o Claude lê com a ferramenta Artifact (action "read"); o Codex lê pelo arquivo anexado, salvo na pasta de insumos do protocolo, se houver.
  - Na camada Pragas e doenças, o painel ao lado do mapa já é um Raio-X funcional, calculado no próprio navegador sobre dados sintéticos, em cerca de 20 ms por data. Tem quatro abas:
    - Sobe e desce: listas com efeito, intervalo, barra de efeito, nível de evidência (Forte · Moderada · Fraca · A confirmar), casos, talhões e "anda junto". O clique abre o sub-detalhe do achado: curva por faixa com o limiar, "quando pesa" (janelas), casos que abrem a linha do tempo do talhão na data, marcação do RT e "Como foi calculado";
    - Controle: eficácia de Henderson-Tilton e dias de proteção (Kaplan-Meier) por produto, calda, sequência e condição na aplicação, e o alerta da armadilha da correlação crua;
    - Risco 7 dias: probabilidade de passar do NC com a previsão do tempo, só exibida se vencer a persistência no teste das 3 semanas anteriores, com os fatores e "Criar vistoria" (rascunho);
    - Correlações: tabela variável × janela com a correlação parcial.
  - O detalhe do talhão mostra a linha "Próximos 7 dias" com a chance e os fatores.
  - O código é referência de método e de interface, não de arquitetura: no Safrion o cálculo roda no servidor, por job noturno idempotente, e a tela lê o resultado pronto.
- A simulação do pragas-no-tempo.html tem efeitos plantados conhecidos e por isso serve de gabarito (seção 6):
  - clima por alvo: dias quentes e secos, folha molhada, umidade alta e chuva forte que lava a folha;
  - falta de água nos pivôs P3, P14 e P21 (ácaro);
  - nitrogênio acima do programa usual (ácaro, mosca-branca, cochonilha) e potássio baixo (antracnose);
  - eficácia por produto e equipamento, com perda em dia quente e seco (×0,78), com chuva até 1 dia depois (×0,70) e na aplicação seguida do mesmo grupo (×0,70);
  - variáveis sem efeito para testar falso positivo: vento e avaliador da vistoria.
  - Resultado no protótipo em 25/09: 12 de 14 efeitos plantados recuperados, nenhum falso positivo forte ou moderado; a previsão venceu a persistência nos 4 alvos.

LIÇÕES DO PROTÓTIPO (validar no desenho final)
- Com uma safra só, clima e época andam juntos. Controlar a época (mês ou data) apagou o efeito do calor e do ar seco. Regra proposta: a época só entra como controle com 2 safras ou mais; com uma safra, a tela declara a limitação.
- Calor, ar seco (DPV), umidade baixa e dias quentes e secos se movem juntos (correlação ≥ 0,7). O motor agrupa essas variáveis, mede o grupo por quem melhor separa o crescimento e mostra "anda junto". Não tentar separar o que os dados não separam.
- A janela de maior associação é escolhida entre 3; a correção multiplica o p-valor pelas janelas testadas antes do Benjamini-Hochberg.
- O p-valor por contagem no bootstrap tem piso (1 ÷ reamostras) que impedia passar no FDR; usar a aproximação normal do bootstrap.
- A correlação crua entre número de aplicações e nível do alvo deu +0,59 na demonstração. Mostrar essa armadilha ao usuário ensina por que a eficácia exige talhões-controle.
- Chuva forte prevista derruba o risco de ácaro e de mosca-branca: o risco precisa da previsão do tempo, não só do histórico.

OBJETIVO
Para cada alvo (ácaro, mosca-branca, antracnose, cochonilha, lagarta, ferrugem etc.), o agrônomo e o gestor veem, no contexto do mapa:
- o que faz subir e o que faz descer, ordenado pelo tamanho do efeito;
- a partir de que valor o efeito aparece (limiar) e depois de quantos dias (janela);
- quanto cada produto, dose, volume e condição de aplicação controlou de verdade, e por quantos dias segurou abaixo do NC;
- se algum grupo IRAC/FRAC está perdendo eficácia;
- quais talhões tendem a passar do NC nos próximos 7 e 14 dias, e por quê.
Tudo é evidência para a decisão do responsável técnico (RT). Nada vira recomendação ou O.S. automática.

ORDEM DE TRABALHO: PRIMEIRO MELHORAR, DEPOIS IMPLANTAR
1. Claude e Codex, cada um sozinho, criticam este desenho contra o PRD, o NAV/DS, o EX-42 e o protocolo de monitoramento vigente: variáveis que faltam, métodos melhores ou mais simples, riscos de conclusão errada, cortes possíveis.
2. Divergência se resolve por fonte ou reprodução. O Gemini real entra nas decisões materiais de domínio: janelas e limiares por alvo, métrica de eficácia, regra de nível de evidência. Pacote mínimo, sem dados reais.
3. O Codex registra o desenho final e as fatias no checkpoint (só ele edita o checkpoint).
4. Implantação na fase registrada no STATUS: primeiro no protótipo, com dados sintéticos rotulados; depois na aplicação Next, por fatias tela → domínio → banco, com revisão cruzada (quem revisa integra o PR do outro).
Não simule o Codex nem o Gemini.

1. PERGUNTAS QUE A FUNCIONALIDADE RESPONDE
- O que faz o ácaro subir nesta fazenda? Quanto sobe e depois de quantos dias?
- Além do defensivo, o que faz descer? Por exemplo, chuva forte que lava ácaro e mosca-branca, irrigação por aspersão, inimigos naturais, poda ou roçada.
- Qual produto, dose, volume de calda e condição de aplicação funcionou de verdade? Por quantos dias segurou?
- Aplicar em dia quente e seco, com vento ou com chuva logo depois reduziu a eficácia? Em quanto?
- Algum grupo IRAC/FRAC perde eficácia a cada aplicação seguida?
- Uma aplicação contra outro alvo provocou ressurgência? Por exemplo, piretroide seguido de explosão de ácaro.
- A adubação muda a pressão? Por exemplo, N alto favorecendo sugadores, e K, Ca e B reduzindo doença.
- Água de menos ou de mais muda o alvo? Por exemplo, os pivôs sub-irrigados.
- O alvo está vindo do vizinho? Pressão nos talhões próximos, borda, cultura hospedeira.
- Quais talhões vão passar do NC na próxima semana, com a previsão do tempo?

2. VARIÁVEIS (todas já existem ou chegam por integração; nada de digitação nova)
Resposta, por talhão × alvo × vistoria:
- nível observado na unidade do protocolo do alvo (incidência %, intensidade, contagem por amostra ou presença, conforme o AG-05) e a razão nível ÷ NC;
- taxa de crescimento entre vistorias seguidas: r = ln((y2 + ε) ÷ (y1 + ε)) ÷ dias entre elas. É a resposta principal, porque tira o peso do nível de partida;
- evento "passou do NC" (sim ou não) e dias até passar;
- depois de uma aplicação: eficácia e dias até voltar ao NC.
Regras da resposta:
- percentual de NC não é percentual de área, e alvo de presença não ganha percentual inventado;
- vistoria parcial não entra como completa;
- valores observados, sem interpolação entre vistorias.

Preditores, por janela antes de cada vistoria (padrão 0–7, 8–14 e 15–28 dias; configurável por alvo):
- Clima, da estação ou da API (horário quando houver, para folha molhada e DPV; microclima por talhão quando existir):
  - Tmáx, Tmín, Tméd, amplitude e graus-dia acima da temperatura-base do alvo;
  - UR média e mínima, horas com UR ≥ 90 %, horas de folha molhada e DPV;
  - chuva: mm, dias com chuva, maior chuva diária, dias com chuva ≥ 10 mm ("lavagem");
  - vento, radiação ou ETo;
  - contagem de dias com a condição favorável ao alvo, como quente e seco (≥ 32 °C e UR < 50 %) para ácaro, ou folha molhada por 8 h ou mais entre 18 e 30 °C para antracnose.
- Água:
  - irrigação em mm, frequência e método (aspersão, gotejo, pivô);
  - suficiência hídrica (lâmina aplicada ÷ necessidade) e déficit acumulado;
  - NDMI, quando houver cena válida.
- Defensivos:
  - dias desde a última aplicação contra o alvo;
  - produto e ingrediente ativo (Agrofit, EX-28) e grupo IRAC/FRAC. Os dados abertos do Agrofit não trazem o grupo de resistência, só o grupo químico e o modo de ação em texto: o grupo IRAC/FRAC vem de uma tabela de referência por ingrediente ativo, versionada e com fonte;
  - dose em relação à bula, volume de calda, equipamento (barra ou atomizador), adjuvante e pH da calda;
  - condição na hora da aplicação: temperatura, UR, vento, Delta T, horário e chuva até 6 h depois;
  - posição na sequência do mesmo grupo (1ª, 2ª, 3ª aplicação seguida);
  - aplicações contra outros alvos, para captar efeito colateral, como piretroide e ressurgência de ácaro, ou fungicida e fungos que controlam pragas.
- Nutrição:
  - N, K2O, Ca, B e S aplicados (kg/ha) na janela e no acumulado da safra;
  - programa de adubação, intervalo entre adubações e relação N/K;
  - análise foliar, quando houver.
- Planta e talhão: cultura, variedade, estádio fenológico, idade, densidade, NDVI e NDRE, histórico do alvo na safra anterior e solo.
- Vizinhança e fonte: nível do alvo nos talhões vizinhos, ponderado pela distância; tendência da fazenda; borda, quebra-vento e cultura hospedeira ao lado.
- Inimigos naturais e controle biológico, quando monitorados.
- Operações que mudam o alvo: roçada, poda, erradicação de plantas, colheita.
- Esforço e qualidade da amostragem: número de pontos, quem avaliou e a hora. Entram como controle, para que viés de avaliador não pareça efeito.

3. COMO CALCULAR (rigor para não enganar o usuário)
Camada 1 · Exploração
- Correlação de Spearman entre cada variável e a taxa de crescimento do alvo, em cada janela.
- Intervalo de confiança por bootstrap em blocos de talhão e semana.
- Correção para muitas comparações (Benjamini-Hochberg, FDR de 10 %).
- Correlação parcial controlando o nível de partida e o estádio; a época (mês) entra só com 2 safras ou mais (ver LIÇÕES DO PROTÓTIPO).
- Saída: a janela de maior associação de cada variável e o "mapa de correlações" (variável × janela).

Camada 2 · Modelo explicativo por alvo
- Modelo de efeitos mistos sobre a taxa de crescimento, com o talhão como efeito aleatório. Ou gradient boosting (por exemplo LightGBM) com SHAP, para efeitos não lineares e interações como calor × seca e N alto × calor. Claude e Codex escolhem o mais simples que passar no gabarito.
- Saídas:
  - direção e magnitude em linguagem direta ("+85 % em 7 dias");
  - limiar, o ponto em que a curva de resposta vira ("acima de 31 °C");
  - interações relevantes.
- Validação temporal: treina no passado e testa no futuro, sem embaralhar.
- O modelo só aparece para o usuário se, no teste, prever melhor que a referência ingênua de persistência (a próxima vistoria igual à atual).

Camada 3 · Efeito das aplicações (medida de efeito, não correlação)
A correlação crua engana aqui por dois motivos. Primeiro, só se aplica quando o alvo está alto, e a correlação mostraria "aplicação aumenta praga" (causalidade reversa). Segundo, depois de um pico vem queda natural (regressão à média). Por isso:
- Eficácia de Henderson-Tilton: E = (1 − (Td × Ca) ÷ (Ta × Cd)) × 100.
  - Ta e Td: nível no talhão tratado antes e depois;
  - Ca e Cd: nível nos talhões-controle antes e depois. Controle é talhão sem aplicação contra o alvo na mesma janela, pareado por nível inicial, estádio e clima;
  - sem vistoria antes, usar Abbott: E = (1 − Td ÷ Cd) × 100.
- Estudo de eventos (antes e depois, com controle) e "dias de proteção" até voltar ao NC, por curva de sobrevivência de Kaplan-Meier, que aceita casos ainda abaixo do NC no fim da série.
- Quebrar a eficácia por produto, dose em relação à bula, volume, equipamento, condição de aplicação e posição na sequência do grupo. Queda de eficácia ao longo da sequência gera alerta de possível resistência.
- Sem controle pareado: mostrar "sem comparação válida", nunca um número.

Camada 4 · Risco à frente
- Probabilidade de cada talhão passar do NC em 7 e 14 dias, com o modelo da camada 2 e a previsão do tempo.
- Calibrada: o "70 %" precisa acontecer cerca de 70 % das vezes (curva de calibração e Brier score).
- Mostra os 3 fatores que mais pesam no risco daquele talhão.

Regras de honestidade (valem para todas as camadas)
- Associação não é causa. Só a camada 3 mede efeito de manejo, e mesmo ela é estimativa com intervalo.
- Nível de evidência em texto: Forte · Moderada · Fraca · Insuficiente. Ele sai de regra declarada: número de eventos, número de talhões, número de safras, intervalo de confiança e estabilidade entre safras. Abaixo do mínimo (proposta: menos de 8 eventos ou menos de 3 talhões) o efeito não é exibido.
- O clima do dia é o mesmo para a fazenda inteira. A variação vem do tempo, não dos talhões, e pede várias semanas e safras. Avisar quando a série é curta.
- Confundidores declarados e controlados: época do ano, estádio, esforço amostral e avaliador.
- Ausente não é zero: dia sem estação não é 0 mm, e talhão sem vistoria não é alvo zerado.
- Conhecimento agronômico como referência. O RT valida, por alvo, a biologia esperada, por exemplo:
  - ácaro favorecido por calor e ar seco;
  - antracnose favorecida por molhamento e chuva;
  - chuva forte reduzindo ácaro e mosca-branca.
  Achado contra a biologia vira "achado a confirmar", nunca regra.
- Partida a frio: sem dados suficientes na fazenda, mostrar o conhecimento de referência validado pelo RT como "referência, não medido nesta fazenda". Um modelo regional ou da cultura, com agrupamento hierárquico, entra só com aviso.
- Rastreabilidade: versão do modelo, dados usados e data do cálculo guardados com cada achado. Recálculo noturno e idempotente.

4. O QUE O USUÁRIO VÊ
Entrada: no Mapa, camada Pragas e doenças, com o alvo escolhido, um painel "Raio-X do alvo" ao lado do gráfico do EX-42. O mesmo painel aparece filtrado no detalhe do monitoramento (AG-01) e no detalhe do talhão. Sem menu novo: segue o NAV vigente.

a) Cabeçalho
- alvo, recorte (fazenda, safra, período) e base de dados ("142 vistorias · 23 talhões · 2 safras");
- nível de evidência geral e data do cálculo.

b) "Faz subir" e "Faz descer"
- Duas listas lado a lado, ordenadas pelo tamanho do efeito.
- Cada item em uma frase, por exemplo: "Dias quentes e secos (≥ 32 °C e UR < 50 %) por 3 dias ou mais → +85 % em 7 dias (de +40 % a +140 %) · 38 casos · 14 talhões · Forte".
- Barra horizontal com o efeito e o intervalo, na mesma escala para todos os itens.
- Tipo do fator em texto: clima, água, defensivo, nutrição, planta, vizinhança.

c) Sub-detalhe de um achado (clique no item)
- curva de resposta com o limiar marcado;
- gráfico da janela: em que dias antes da vistoria o efeito é maior;
- os casos que sustentam o achado (talhões e datas). Cada caso abre a linha do tempo do EX-42 já posicionada na data;
- ressalvas e "Como foi calculado" (método, n, intervalo, versão). Termos como IC, SHAP e FDR ficam só aqui, nunca na primeira camada.

d) "O que funcionou no controle"
- tabela de eficácia (Henderson-Tilton) e de dias de proteção, por produto, grupo, dose, volume, equipamento e condição de aplicação;
- alerta de queda de eficácia na sequência do grupo;
- comparações de condição, por exemplo "aplicar em dia quente e seco teve eficácia 18 pontos menor".

e) "Risco nos próximos 7 dias"
- talhões ordenados por probabilidade, com os 3 fatores de cada um;
- ação "Criar vistoria" (rascunho). Nunca O.S. automática: a O.S. de controle segue o fluxo MIP, com aprovação individual do RT.

f) Mapa de correlações, sob demanda
- variável × janela, com cor divergente do design system e só as células significativas destacadas;
- serve ao agrônomo que quer ver tudo; não é a primeira camada.

Interface
- Linguagem do produtor e números em pt-BR.
- Texto junto da cor, nunca só cor.
- Tabelas conforme o padrão de tabelas interativas (filtro e ordenação no cabeçalho, agrupar, detalhar).
- Abre em menos de 1 s, porque o cálculo é pré-computado.

Aprendizado com o campo
- O agrônomo marca cada achado: "Confere com o campo" · "Não confere" · "Investigar".
- A marca vira dado. A regra validada pelo RT entra no protocolo do alvo (AG-05), com versão e fonte.

5. DADOS A LIGAR (sem digitação nova)
- vistorias (AG-01, MB-06), com pontos, esforço e avaliador;
- protocolo com o NC por alvo e estádio (AG-05);
- O.S. apontadas: produto, dose, calda, equipamento, horário e clima do apontamento;
- Agrofit: produto, ingrediente ativo, grupo químico e modo de ação (EX-28);
- tabela de grupos IRAC/FRAC por ingrediente ativo, versionada e com fonte (o Agrofit não traz esse dado);
- fertirrigação e irrigação (IR-*);
- estação meteorológica ou API, horária, mais a previsão de 7 a 14 dias;
- chuva medida;
- cenas de satélite com máscara de nuvem (C4);
- talhão: cultura, variedade, estádio, idade e geometria (para a vizinhança);
- operações: roçada, poda, erradicação, colheita.
Modelo de dados sugerido (Claude e Codex validam):
- tabela diária por talhão com as variáveis já agregadas por janela;
- tabela de eventos de manejo;
- tabela de achados: alvo, variável, janela, direção, efeito, intervalo, n, evidência, versão do modelo e marca do RT.

6. VALIDAÇÃO E ACEITE OBSERVÁVEL
Gabarito sintético, a partir da simulação do pragas-no-tempo.html: gerar dados com os efeitos plantados (seção REFERÊNCIAS), mais variáveis sem efeito nenhum (ruído). O motor precisa:
- recuperar a direção de 100 % dos efeitos fortes plantados, e a magnitude dentro do intervalo em pelo menos 80 % deles;
- não exibir como Forte ou Moderada nenhuma variável de ruído (falso positivo ≤ 5 %);
- detectar a perda de eficácia por aplicações seguidas do mesmo grupo;
- passar no teste de causalidade reversa: aplicação feita com o alvo alto não pode aparecer como "faz subir";
- passar no teste de vazamento: nenhuma variável usa informação posterior à vistoria.
Previsão:
- melhor que a persistência no Brier score;
- calibração dentro de ±10 pontos percentuais.
Agronômico:
- o RT valida o Raio-X de pelo menos 2 alvos do mamão (ácaro e antracnose) e de 1 alvo de grão;
- cada achado confere com a biologia do alvo ou tem justificativa registrada.
UX:
- em até 2 ações a partir do mapa, o usuário vê o que faz o alvo subir e descer e abre a evidência de qualquer item;
- teste com 3 a 5 agrônomos (UX-13): pelo menos 4 explicam corretamente o que um achado quer dizer e o que ele não quer dizer.

7. FATIAS SUGERIDAS (o Codex decide)
1. Dados e janelas, mais o gerador do gabarito sintético.
2. Eficácia das aplicações (camada 3). É o maior valor imediato e já responde "o que funcionou".
3. "Faz subir" e "Faz descer" (camadas 1 e 2), com sub-detalhe e mapa de correlações.
4. Risco nos próximos 7 e 14 dias (camada 4).
5. Marcação do RT e entrada da regra validada no protocolo.
Cada fatia tem ID, persona, arquivos, autor, revisor e aceite observável, e segue o Double Diamond (descobrir, definir o aceite medido, desenvolver, entregar com a medida).

8. DECISÕES DO PROPRIETÁRIO
- Confirmar que o motor estatístico não está coberto por "assistente de IA desligado". Ele não usa IA generativa, e os textos dos achados saem de modelos de frase preenchidos com os números. Registrar o custo de cálculo estimado.
- Mínimo de evidência para exibir um efeito (proposta: 8 eventos e 3 talhões).
- Quem pode marcar achado e promover regra ao protocolo (proposta: só o RT).

9. NÃO FAZER
- Recomendar produto ou dose, gerar O.S. ou mexer na aprovação agronômica individual.
- Mostrar correlação crua entre aplicação e alvo como se fosse efeito.
- Exibir efeito sem número de casos, intervalo e nível de evidência, ou esconder a incerteza.
- Fixar limiar ou janela de alvo no código: parametrizar por cultura e estádio, com fonte e versão.
- Interpolar vistorias ou tratar ausência como zero.
- Criar menu ou tela fora do NAV vigente.
- Usar IA generativa para redigir achados.

10. ENTREGA (no canal registrado)
- Desenho final, com o que Claude e Codex mudaram neste pedido e por quê.
- Fatias, com autoria e revisão.
- Resultado do gabarito: tabela "efeito plantado × efeito recuperado", falsos positivos e testes de causalidade reversa e de vazamento.
- Parecer do RT por alvo validado e as medidas de UX.
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado.
- Suposições e pendências, cada uma com o gatilho de retomada.
