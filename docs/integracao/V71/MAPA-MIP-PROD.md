# MAPA-MIP-PROD · Pragas e doenças no tempo, mapa de produtividade e alavancas da produtividade

> Proprietário, 16/10/2026 (1º pedido): "coloque no mapa na funcionalidade pragas e doenças... um jeito de conseguir arrastar uma barra e ver evolução do monitoramento de pragas e doenças por talhao e global (media) do alvo selecionado e ao clicar no talhao, ver isso tambem junto com as aplicacoes realizadas para ver quais defensivos/calda/entrada estao gerando reducao de pragas e doencas com datas interligadas do monitoramento x aplicaco de forma muito visual e intuitiva.
>
> também importacao dos mapas de colheita para mostrar os mapas de calor das manchas de produtividade em cada região do talhão.
>
> melhore o prompt para sí mesmo, melhore o que pedi junto com codex e implemente da melhor forma possível."

> Proprietário, 16/10/2026 (2º pedido): "Junte forças com codex para criar uma funcionalidade no mapa, de correlação de variáveis / estatísticas. dados de satelite, irrigacao, produtividade, analise de solo, mapa de colheita, pragas e doenças monitoramento, e gerando análise de causa e efeito, correlaçoes para o time focar nas alavancas e veriaveis que mais impactam na produtividade. melhore o prompt para sí mesmo para melhorar com codex e fazer um trabalho brilhante."

Três partes, uma base de dados (grade do talhão, monitoramento, aplicações e mapa de colheita) e uma fatia por vez:
- **Parte 1 · MAPA-MIP-TEMPO:** linha do tempo do monitoramento no mapa e o que se associou à redução.
- **Parte 2 · MAPA-PRODUTIVIDADE:** importar o mapa de colheita e ver o mapa de calor da produtividade.
- **Parte 3 · ALAVANCAS:** quais variáveis mais explicam a diferença de produtividade, quanto valem e como confirmar.

## Pedido melhorado

**Parte 1 · MAPA-MIP-TEMPO**
- **Resultado útil:** o agrônomo arrasta a data e vê, por talhão e na média da fazenda, como um alvo evoluiu. Toca no talhão e vê a série desse alvo com as aplicações realizadas na mesma linha do tempo, e a redução observada depois de cada uma. Numa lista, vê quais produtos ou misturas se associaram a redução, com o número de casos.
- **Personas:** agrônomo RT (decide o controle), gerente (acompanha), monitor de campo (consulta no celular).
- **Leitura do pedido:** "calda/entrada" é a mistura do tanque (todos os produtos da O.S., inclusive adjuvante) e o volume de calda; "entrada" é cada insumo dessa mistura.
- **Restrições:** a mesma base do AG-01 e das O.S.; validade da leitura pela PROJ-13; média do CAL-12; PRD 33.8 (sem lista por "potência", IRAC/FRAC só para rotação); IA desligada (DEC-1610-11); o sistema não recomenda produto (é do RT).
- **Pronto quando:** T1–T9 passam, K1–K4 ficam no teto e a contraprova reprova a ponta antes.

**Parte 2 · MAPA-PRODUTIVIDADE**
- **Resultado útil:** importar o arquivo do monitor de colheita, ver o que entrou e o que ficou de fora, publicar e ver as manchas de produtividade de cada região do talhão, na unidade da cultura, ao lado da produtividade apurada.
- **Personas:** gerente e agrônomo (analisam); quem cuida das máquinas ou do escritório (importa).
- **Restrições:** PRD cap. 62 (COLMAP-01 a 10), CAL-16, UNID-PROD; importar nunca cria carga, lote nem estoque; importar duas vezes não duplica.
- **Pronto quando:** C1–C10 passam, K5–K6 ficam no teto, contraprova reprova.

**Parte 3 · ALAVANCAS** (pedido melhorado com o coordenador)
- **Resultado útil:** o time vê, por talhão, fazenda e safra, quais variáveis mais explicam a diferença de produtividade, quanto isso vale em sc/ha e R$/ha, com que confiança, e qual o próximo passo para confirmar e agir.
- **Personas:** gerente e agrônomo (focam o esforço); proprietário (vê onde está o dinheiro).
- **Restrições:** estatística determinística, não IA; a tela diz "associado a", nunca "causa"; causa só com teste em faixas; alavanca controlável separada de condição.
- **Pronto quando:** E0–E12 e F1–F3 passam com os dados sintéticos de efeito plantado, K7–K8 ficam no teto, contraprova reprova.

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: MAPA-MIP-PROD (MAPA-MIP-TEMPO, MAPA-PRODUTIVIDADE, ALAVANCAS) / ver a evolução de um alvo no tempo com as aplicações, o mapa de produtividade importado e as alavancas da produtividade com valor e confiança / agrônomo RT, gerente, monitor de campo, quem importa os arquivos
Requisitos do PRD e fora do escopo: AG-01, AG-06, CAL-12, CAL-16, 33.8, 36 (TV), 61.5 (LABMAP-06/10/12), 62 (COLMAP-01..10), 74 (DS), 4.2/4.3, PROJ-13 e PEND-13 (valores aceitos na DEC-1610-04), DEC-1610-03/09/11/12, DEC-2609-10/12; fora: §Fora do escopo
Autor / revisor / integrador: Claude / Codex (produto e QA) e Gemini (lente agronômica e estatística, pelo conector do Codex) / Codex (regime leve do protótipo, §3.5)
Base (commit ou hashes) / arquivos sob responsabilidade: ponta de claude/v44-v69-mapa em bf7d8b6 (frente Cadastros integrada em eabc4a3; os arquivos citados abaixo não mudaram desde 0d26443) / areas/inicio.py, mip.js, dados_mip.py, dados_lagoa_safra.py, areas/agronomia.py (AG-06 e AG-01det), talmapa.js (peça de importação reaproveitada), colmapa.js (novo), alavancas.js (novo), dados_colmapa.py (novo), testes novos mip_tempo_unit.js, mapa_mip_tempo_test.py, colmapa_unit.js, colmapa_test.py, alavancas_unit.js, alavancas_test.py
Aceite e comando de verificação: T1–T9, C1–C10, E0–E12, F1–F3 abaixo / node mip_tempo_unit.js; node colmapa_unit.js; node alavancas_unit.js; python3 -B mapa_mip_tempo_test.py; python3 -B colmapa_test.py; python3 -B alavancas_test.py; ANTES=<_render da ponta antes da fatia, de árvore limpa>; oráculos: mapa_mip_prod_chk.py e mapa_alavancas_chk.py (§Conferência)
Estado / impedimento / próximo passo: especificado, sem código; revisão do Codex e do Gemini pendente; fatias F1a → F1b → F2a → F3a → F3b, dentro do teto de três frentes (§3.6); F2b e F3c dependem do proprietário
```

## Revisão (Codex e Gemini)

- **Codex:** produto, aceite, cliques e QA.
- **Gemini, pelo conector do Codex:** lente agronômica (MIP, janelas antes e depois, limpeza do mapa) e estatística (n efetivo, FDR, LMG, teste em faixas).
- **Texto enviado:** este arquivo, na versão do envio. O Codex registra na rodada, no ato do envio, o SHA-256 do texto exato (`sha256sum docs/integracao/V71/MAPA-MIP-PROD.md`), a data, o modelo e o parecer.
- **Peso das decisões abaixo:** são proposta do autor. Viram decisões dos agentes só depois dos dois pareceres escritos (§3). Cada achado é aceito, ajustado ou recusado com fundamento.

| Revisor | SHA-256 do texto revisado | Data | Parecer |
|---|---|---|---|
| Codex | — | — | Pendente. |
| Gemini (conector do Codex) | — | — | Pendente. |

**Tratamento dos achados:** nenhum achado recebido ainda.

## Situação em 16/10 (lida no código em bf7d8b6)

| Parte | Hoje |
|---|---|
| **Mapa (IN-04)** | 9 funções fixas (DEC-1610-09; `areas/inicio.py:112`, nomes em `:431`). Faixa branca de uma linha, 52 px (MAP-04; `:1542-1554`). Legenda numa caixa no rodapé do mapa (`:1562-1563`). Ferramentas no alto à direita (`:1526-1537`): "Importar" de talhões KML/GeoJSON (`:1529`) e "Importar laudo" só no Solo (MAP-02, `:1532-1537`).<br>• **Lagoa Grande:** mapa real (MapLibre) com pixels de 10 m do Sentinel-2 (`:381-389`, `lgEnsure :616`, `lgSync :639`).<br>• **Santa Rita:** desenho fora de escala (`GEO :102-105`; células de 16 px "10 m demonstrativo" em `:353-378`; coordenada da célula em `pxCoord :755`). |
| **Pragas e doenças no mapa** | Mesma base do AG-01 (`dados_mip.py` + `mip.js`). Filtro Período 7 ou 30 dias (`:121`). Alvos com escolha múltipla (`:1180-1188`; `ALV`, `alvosFaz :538-541`). Cor = pior situação no período (`cls :836-840`; legenda `:867`). Números Vistorias, Acima do NC, Atenção e Em controle (`:899-900`). Painel com o próximo passo do MIP (`:1050-1064`).<br>**Não há** data escolhida, média da fazenda, série nem aplicações no mapa. |
| **Protocolo** | Método, unidade, NC, NC por fase (`ncf`) e versão (`dados_mip.py:36-68`). **Não há** nível de dano (ND). |
| **Vistorias** | De 1 a 3 por talhão × alvo na semente (`dados_mip.py:178-213`). Média do CAL-12 e classes acima, foco, perto e abaixo em `mipRes` (`mip.js:73-102`). Ritmo e "Vistoria atrasada" em `mipRitmo` (`mip.js:126-137`). |
| **Avaliação pós** | "Redução observada = 1 − pós/pré" só quando a leitura pós foi programada e ligada (`pos_de`; `mip.js:99-100`, `mipPos :346-352`), com o texto "não equivale a eficácia causal" (`mip.js:161`). |
| **Série e histórico** | AG-01det mostra uma barra por leitura do mesmo método (`areas/agronomia.py:846-849`, bloco em `:890`), sem aplicações. O painel do AG-01 lista vistorias e aplicações com o grupo de modo de ação (`mipHist`, `mip.js:354-361`; `areas/agronomia.py:732-733`). |
| **Aplicações** | `APL` do MIP: talhão, data, produto, alvo e O.S. (`dados_mip.py:227-235`), sem dose, calda nem área.<br>Aplicação efetiva (apontamento com data e área; O.S. cancelada sem apontamento não conta) só no motor de carência (`dados_carencia.py:9`; `carAplic :296-325`, que já aceita uma data de corte).<br>O.S. da Lagoa com produto e dose por ha (`dados_lagoa_safra.py:175-185`) e apontamentos (`:139-146`).<br>Volume de calda fixo no código (`areas/processo_os.py:789`; achado EX-38). |
| **Bula e modo de ação** | Produtos elegíveis por cultura × alvo, com grupo IRAC/FRAC, carência e máximo de aplicações (`dados_mip.py`, `_agf`; base demonstrativa do `agrofit_dados.py`). |
| **AG-06 · Eficácia e histórico** | Módulo oculto (`areas/agronomia.py:4`) com 5 linhas fixas EF-017 a EF-021 (`:384-428`), sem ler o MIP nem as O.S. A EF-018 cita "redução de 62 %" no P2, que a base do MIP não tem. |
| **Mapa de calor do Solo** | IDW sem raio (`soloIdw`, `:1301`), valor por célula (`soloGrade :1304-1312`), contraste Talhão, Fazenda ou Absoluto (`:1313-1316`), legenda (`:1324-1328`), números com média ponderada pela área (`:1329-1334`), área por classe no painel (`:1352-1358`). Na Lagoa, por pixel (`lgSoloCanvas :589-597`). |
| **Colheita no mapa** | Situação da Previsão e colheita (`colhCls :1379`; filtro "Mostrar" com Situação e Carência e destino em `:125`). **Não há** mapa de produtividade. |
| **Unidade de produtividade** | `CULTURA_UN` (`dados_cad.py:41`): soja e milho em sc de 60 kg, umidade de referência 14 %. Conversor único (`producao.js:34`, `:205-262`), seletor UNID-PROD (`unidprod_ui.py`), equivalência de umidade `prMs` (`producao.js:56`, a mesma do CAL-16). |
| **Importação com prévia** | Talhões KML/GeoJSON no Mapa: leitura, linhas com destino e aviso, "Importar N para o cadastro" (`talmapa.js:91-129`, painel `:204-218`). Também ON-01det e o "Trazer N mudanças" do CD-07 (`areas/cad_produtos_estrutura.py:374`). |
| **Geometria** | `talgeo.js`: coordenadas [lon, lat], área geodésica, ponto no polígono (`tgDentro :23`), círculo do pivô pela área (`tgCirculo`, `tgRaioDeHa`). |
| **Preço** | Referência sintética do Comercial: soja R$ 129,40/sc e milho R$ 61,80/sc (`dados_comercial.py:16-17`). |
| **Irrigação** | Balanço por pivô; o setor de irrigação é o pivô inteiro (`dados_irrigacao.py:55-63`). Não há setor angular. |
| **PRD** | Já pede a importação do mapa de colheita (cap. 62, COLMAP-01 a 10), a redução observada (CAL-12) e o AG-06 (eficácia e histórico). |

**Achados ligados** (não são desta frente; registrados para não se perderem):
- **A1 · Duas georreferências sintéticas da Santa Rita.** `pxCoord` (`areas/inicio.py:755`, centro perto de −15,56 · −54,30) e `_SR_LL` (`dados_mip.py:100`, perto de −17,83 · −50,62). A parte 2 usa só a do mapa.
- **A2 · Paleta dos mapas de calor ruim para daltonismo.** A rampa vermelho → verde do Solo e do Satélite (`SOLOPAL`, `:1282`; `SATPAL`, `:345`) tem luminância 0,167 · 0,316 · 0,688 · 0,665 · 0,385 · 0,141 (executado): não sobe em ordem, e o pior (0,167) e o melhor (0,141) quase se igualam. Fere a LABMAP-12. A troca é na peça comum, numa frente própria (skill `padrao-safrion`), e a parte 2 herda o resultado.
- **A3 · AG-06 fixo e divergente** do MIP (EF-018). A F1b o substitui pela leitura viva.

## Referências (AGENTS §3.3)

Estar no mercado não prova que a regra está certa. A decisão é por prática. Consultas feitas em 16/10/2026 por este agente.

| Referência | Prática | Decisão | Conferência |
|---|---|---|---|
| Climate FieldView · "Put your data to work" ([link](https://climate.com/en-gb/getting-started/fieldview-201-overview/put-your-data-to-work.html)) | Mapas lado a lado ("compare critical data layers such as soil maps, application rate, and seed population to yield"); análise de produtividade por talhão, híbrido e solo; regiões salvas para "monitor those regions throughout the season"; imagens de saúde da lavoura por data | **Adotar** o lado a lado (parte 3) e a escolha da data (parte 1). **Adaptar** a análise por categoria: por zona do SOLO-VRA e por setor. **Descartar** a comparação sem número de casos. | Aberta. |
| John Deere Operations Center · recursos ([link](https://www.deere.ca/en/technology-products/precision-ag-technology/operations-center/features/)) | "Track yields from different fields and compare outcomes for current year's product and variety trials"; atualização com "yield, moisture levels, and varieties" | **Adotar** a comparação de ensaios da safra (teste em faixas, F3b). **Adiar** a leitura direta do Operations Center: exige conta e contrato do proprietário. | Aberta (deere.ca). A página dos EUA veio sem texto. O passo a passo do "Analysis" com duas camadas e seleção por polígono veio de um revendedor ([Koenig](https://support.koenigequipment.com/how-can-i-use-data-analysis-to-evaluate-field-performance)), não oficial. |
| Aegro · "Linha do tempo do talhão" ([link](https://aegro.com.br/suporte/safras/linha-do-tempo-do-talhao/)) | Uma célula por praga e data, com cor contra o nível de controle; mapa de calor dos pontos da amostragem. Sem nível cadastrado, qualquer valor acima de zero vira "acima". | **Adotar** a cor pela classe contra o NC e o acesso aos pontos. **Descartar** "sem NC = acima": aqui, sem NC numérico vale o critério de presença do protocolo, sem divisão por zero (CAL-12). A página não liga aplicações à linha do tempo: é a lacuna que esta frente cobre. | Aberta (atualizada em 05/08/2026). |
| Cropwise Protector (Syngenta Digital) · página do app ([link](https://apps.apple.com/us/app/-/id1509531036)) | "Follow all agronomic events through indicators and heatmaps"; mapas para achar "areas without application" | **Adotar** a ideia de eventos agronômicos numa linha só (leituras e aplicações). **Adaptar** "área sem aplicação": aqui é a área apontada da O.S., que marca o par como parcial. | Aberta (loja do app; desenvolvedor Syngenta Digital LTDA). Sem documentação de produto sobre o histórico por talhão: não conferido. |
| xarvio Field Manager · "Data management and analytics" ([link](https://ag.xarvio.com/field-manager/data-management-and-analytics)) | Zonas por histórico de biomassa e mapas de produtividade | **Adiar** zonas por histórico de muitas safras (precisa de mais de uma safra; ver Embrapa Pecuária Sul abaixo). | Não conferido: a página veio sem texto; só o resumo da busca. |
| Embrapa Cerrados · Comunicado Técnico 96, "Geração de mapas de produtividade para experimentos com milho no âmbito de fazenda" (Shiratsuchi, 2003) ([PDF](https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/568680/1/comtec96.pdf)) | Remoção de erros antes do mapa; inverso da distância com "12 vizinhos e um peso igual a dois" e célula de 2 m; krigagem "trabalhosa e exige conhecimento em geoestatística"; experimento em faixas lado a lado colhidas em separado | **Adotar** IDW com potência 2 e 12 vizinhos (parte 2) e o teste em faixas (F3b). **Adiar** a krigagem. | Aberta e lida (texto extraído do PDF). |
| Embrapa Pecuária Sul · "Produtividade de soja e forragem em zonas de manejo definidas a partir do mapa de colheita" (Pilon e outros) ([PDF](https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/1028843/1/Pilonetal.pdf)) | Zonas alta, média e baixa a partir do mapa de colheita da soja; as zonas "não reproduziram" a produção da forragem seguinte | **Adotar** a cautela: uma safra não define zona permanente (também PRD 62.3). | Aberta e lida. |
| Embrapa Soja · folder "MIP-Soja: manejo integrado de pragas da soja" (2012) ([registro](https://www.infoteca.cnptia.embrapa.br/handle/doc/915970)) | Amostragem com pano de batida e níveis de ação por praga | **Adotar** como referência de que método, unidade e nível de ação vêm do protocolo, com fonte e versão. Os NC da semente continuam demonstrativos. | Registro aberto; o folder em si não foi lido. |

**Referências da parte 3**

| Referência | Prática | Decisão | Conferência |
|---|---|---|---|
| Oregon State University Extension · EM 9381, "Experimenting on the farm: Introduction to experimental design" (Tanner, Jones e Verhoeven, maio 2023) ([link](https://extension.oregonstate.edu/catalog/em-9381-experimenting-farm-introduction-experimental-design)) | Testemunha igual ao manejo padrão; repetição e sorteio; "start with at least four replications"; blocos de parcelas vizinhas; bordadura sem coleta | **Adotar** no teste em faixas: pares sorteados, bordadura, pelo menos 4 repetições (padrão 6). | Aberta. |
| Embrapa Cerrados · Comunicado Técnico 96 (acima) | Faixas lado a lado na largura da plataforma, colhidas em separado | **Adotar** largura da faixa em múltiplos da plataforma e da semeadora. | Aberta e lida. |
| Climate FieldView (acima) | Lado a lado de camadas com a produtividade | **Adotar** o lado a lado, com n, intervalo e "associado a", que a página não mostra. | Aberta. |
| Esri · "How Spatial Autocorrelation (Global Moran's I) works" ([link](https://doc.esri.com/en/arcgis-pro/latest/tool-reference/spatial-statistics/h-how-spatial-autocorrelation-moran-s-i-spatial-st.html)) | Definição do I de Moran, pesos padronizados por linha, E[I] = −1/(n−1) | **Adotar** o I de Moran (vizinhos por aresta, linhas padronizadas), com teste por permutação em vez da aproximação normal. | Aberta. |
| Benjamini e Hochberg (1995), "Controlling the false discovery rate", JRSS B 57(1):289–300, DOI 10.1111/j.2517-6161.1995.tb02031.x | Controle da proporção esperada de falsos positivos | **Adotar** o BH para as variáveis de cada análise. | Metadados conferidos por busca; o artigo não foi aberto. |
| Grömping (2006), "Relative Importance for Linear Regression in R: The Package relaimpo", J. Stat. Software 17(1) ([link](https://www.jstatsoft.org/article/view/v017i01)) | Importância relativa por "averaging over orderings of regressors" (LMG) | **Adotar** o LMG. **Adiar** os intervalos por bootstrap do LMG. | Página aberta (resumo). |
| Clifford, Richardson e Hémon (1989), "Assessing the significance of the correlation between two spatial processes", Biometrics 45(1):123–134 | n efetivo da correlação entre dois processos espaciais | **Adotar** a aproximação do n efetivo pelo correlograma. | Não conferido (citação de memória do método; conferir antes da F3a). |
| Copernicus Data Space Ecosystem · cotas ([link](https://documentation.dataspace.copernicus.eu/Quotas.html)) | Conta gratuita com cotas: 10.000 requisições e 10.000 unidades de processamento por mês na API Sentinel Hub | **Adiar** para a F3c (conta e custo de processamento são do proprietário). | Aberta. |

## Base comum (vale para as três partes)

1. **Lugar: dentro do Mapa, sem função nova.** A barra continua com os 9 nomes (DEC-1610-09). Cada parte é uma opção do filtro **Mostrar**, a mesma peça que já existe em Colheita e Irrigação (`areas/inicio.py:122`, `:125`).
   - **Pragas e doenças:** Mostrar · **Situação** (a de hoje) | **Evolução** (parte 1).
   - **Colheita e produtividade:** Mostrar · Situação | Carência e destino | **Produtividade** (parte 2) | **Alavancas** (parte 3).
   - A faixa branca fica com uma linha (MAP-04). Os filtros que não valem para a opção somem, como já faz `fvis` (`:550`).
2. **Grade.** A unidade espacial é a **célula** do talhão.
   - **Software real:** célula de 10 m (a mesma do Sentinel-2 L2A, perto da largura da plataforma) e **bloco de inferência de 1 ha** (100 × 100 m), ambos parâmetros. Agregações: zona (SOLO-VRA), setor de irrigação, talhão e safra.
   - **Protótipo:** a célula do desenho na Santa Rita (16 px; o P1 tem 134 células de 0,709 ha pela área do cadastro) e o pixel de 10 m na Lagoa Grande. A célula do desenho já tem o tamanho de um bloco: a inferência é por célula.
   - O desenho da Santa Rita está fora de escala. As áreas usam sempre a área do cadastro; a geometria do desenho só posiciona.
3. **Catálogo de variáveis.** Cada variável tem fonte, unidade, data, resolução, método de levar à célula, validade e marca de origem.

| Variável | Fonte | Unidade | Até a célula | Validade | Marca | Tipo |
|---|---|---|---|---|---|---|
| Produtividade | mapa de colheita limpo (parte 2); referência: apurada do talhão | a da cultura (UNID-PROD), base de umidade da cultura | IDW dos pontos válidos | a safra | medido → interpolado | resultado |
| Solo: pH, V %, P, K, MO, CTC, argila | laudo do AG-02 em grade, com suporte amostral declarado (SOLO-VRA, decisão 4) | as do laudo (mg/dm³, cmolc/dm³, %) | IDW dos pontos, como o mapa de calor de hoje | 24 meses (PEND-13) | interpolado; laudo composto = declarado, um valor por talhão | condição (argila, CTC, MO) ou controlável (K, P pela adubação; pH, V % pela calagem) |
| Satélite: NDVI, NDRE | Sentinel-2 L2A, uma cena por data | índice | pixel de 10 m; nuvem = sem dado | 10 dias para decisão (PEND-13); na análise, a data faz parte do nome ("NDVI 15/01") | medido; sintético fora do Mac | **indicador** |
| Irrigação | balanço hídrico (CAL-09, `dados_irrigacao.py`) | mm (déficit acumulado; lâmina aplicada × necessidade) | por setor; hoje setor = pivô inteiro | o ciclo ou a fase escolhida | medido ou estimado (≈) | controlável no pivô; condição no sequeiro |
| Pragas e doenças | vistorias do AG-01 (parte 1) | pressão: unidade do protocolo × dia | por talhão; por célula só com pontos georreferenciados e protocolo que permita | 7 dias por leitura (PROJ-13) | medido | controlável (momento do controle) |
| Aplicações | O.S. com apontamento | dias de atraso; grupo IRAC/FRAC | por talhão ou parcela apontada | a safra | medido | controlável |
| Manejo | cultivo, plano e O.S. | data de plantio, cultivar, população (plantas/ha), adubação aplicada (kg/ha) | por talhão; por zona quando a prescrição foi por zona | a safra | declarado ou medido | controlável |

4. **Regras comuns.**
   - **Uma unidade por número.** Média, série e comparação só entre o mesmo protocolo (método e unidade), a mesma cultura e a mesma safra. Comparar safras é lado a lado, nunca somado sem método declarado (PRD 62.3). *Dano evitado:* média de unidades diferentes, que não significa nada e leva a decisão errada.
   - **Ausente não é zero.** "Sem leitura recente", "sem registro", "Sem laudo", "sem variação no escopo". *Dano evitado:* mancha falsa ou alvo "controlado" por falta de dado.
   - **Idade e validade.** Pela PROJ-13, publicada por CMD-29; o protocolo pode reduzir a validade de um alvo. Idade igual à validade ainda conta como atual.
   - **"Por quê" em cada número:** fórmula, entradas e origem, com a peça já usada no Solo.
   - **Uma fórmula, um serviço (ENG-011):** `mip.js` (série, par, pressão), `colmapa.js` (leitura, limpeza, grade), `alavancas.js` (estatística). No software real, `packages/domain`, com decimal para dinheiro e quantidade (ENG-013).
   - **Sem IA (DEC-1610-11) e sem recomendar produto.** A escolha do produto é do RT, pela bula e pelo receituário.

## Parte 1 · MAPA-MIP-TEMPO — decisões propostas (valem depois dos pareceres)

1. **Evolução.** Em Pragas e doenças, "Mostrar · Evolução" troca o período pela data escolhida na barra do tempo. "Situação" continua igual e abre por padrão.
2. **Um alvo por vez, com a unidade.** Em Evolução, o menu Alvos vira escolha única (`menuitemradio`).
   - A opção é alvo × protocolo. Quando o mesmo alvo tem dois protocolos na fazenda, aparecem dois itens: "Mosca-branca · adultos/folíolo (Feijão)" e "Mosca-branca · adultos/folha (Mamão)".
   - Com vários alvos escolhidos na Situação, a Evolução fica com o primeiro e avisa ("Evolução mostra um alvo por vez: Ácaro-rajado").
   - *Dano evitado:* somar adultos por folíolo com adultos por folha.
3. **Leitura válida.** Vistoria do protocolo concluída, sem pacote pendente no aparelho, completa ou decidida com coleta parcial (`mipParcial`).
   - A média é a do CAL-12, pelo `mipRes` (só pontos válidos; recoleta fora).
   - Vistoria programada ou em coleta não entra.
   - Troca de versão do protocolo (método) fica marcada na série, e nenhum par antes × depois atravessa a troca (LABMAP-10).
4. **Estado do talhão na data D.**
   - Vale a última leitura válida até D. Idade = D − data da leitura.
   - **Idade ≤ validade** (7 dias, PROJ-13): cor pela classe do `mipRes` (acima, foco, perto, abaixo; na presença, com ou sem sintoma). Rótulo "9 % · 04/09".
   - **Idade > validade:** cinza hachurado, "sem leitura recente · 27/08 (há 8 dias)".
   - **Nenhuma leitura até D:** cinza, "sem leitura até 04/09".
   - **Talhão sem o protocolo na data** (sem cultura ou fase fora): neutro, "fora do alvo".
   - *Dano evitado:* decidir sobre leitura velha como se fosse de hoje, ou tratá-la como zero.
5. **Média da fazenda.** Média ponderada pela área: Σ (média do talhão × área) ÷ Σ área, só dos talhões com leitura atual na data.
   - Ao lado: cobertura (área com leitura atual ÷ área com o protocolo na data) e "4 de 20 pivôs".
   - Sem nenhum talhão atual: "—".
   - **NC:** uma linha só quando todos os talhões da média têm o mesmo NC na data. Senão, "NC varia por fase: 2,0 (V) e 4,0 (R)" e "acima do NC: k de n".
   - **Critério de presença** (viroses): sem média; "k de n talhões com sintoma".
6. **NC e nível de dano.** O NC (e o NC por fase) vem do protocolo, com a versão. O nível de dano econômico (ND) entra como campo opcional do protocolo, com fonte; sem fonte, não aparece (PRD 33.8 separa os dois). Os NC da semente são demonstrativos e aparecem assim.
7. **Barra do tempo.** Fica na caixa da legenda, no rodapé do mapa (`:1562`), numa linha acima da legenda. A faixa branca não muda (MAP-04).
   - **Peças:** "‹" (leitura anterior) · trilho com marcas finas nas datas com leitura e losangos nas datas de aplicação · "›" (leitura seguinte) · data escolhida · "Hoje".
   - **Faixa de datas:** da primeira leitura do alvo nos cultivos da safra do filtro até hoje. O filtro Safra escolhe os cultivos, como já faz em Estádio e Custos. Num cultivo perene, as leituras do mesmo cultivo de antes do início da safra também entram, porque o cultivo é o mesmo (o PV06 foi plantado em 12/03/2025; a Safra Mamão 2026/27 começa em 01/09/2026).
   - **Controle:** `input type="range"` com passo de 1 dia. Teclado: ← e → mudam 1 dia; PgUp e PgDn, 7 dias; Home e End, início e hoje.
   - **Nome acessível:** `aria-valuetext` = "04/09/2026 · 4 de 20 pivôs com leitura atual · média 12,61 % folhas com ácaro".
   - **Desenho:** o mapa recolore no máximo uma vez por quadro (`requestAnimationFrame`) enquanto arrasta.
   - A data vai para o contexto do mapa (`mapa-ctx`, `:1111`) e para o endereço (`#data=2026-09-04`): voltar e recarregar mantêm a data.
8. **Talhão clicado: série com as aplicações.** O painel lateral de hoje (folha inferior no celular) mostra:
   - **Gráfico:** eixo do tempo igual ao da barra, com o cursor na data escolhida. Pontos das leituras coloridos pela classe, com o valor. Linha do NC tracejada; ND só com fonte. Faixas cinza nos dias sem leitura atual (os mesmos dias em que o mapa mostra "sem leitura recente").
   - **Marcas de aplicação:** só aplicações efetivas, pela regra do motor de carência (`carAplic`: apontamento com data e área; O.S. cancelada sem apontamento não conta). O registro histórico do MIP sem O.S. aparece marcado "sem O.S.". O.S. programadas ficam numa lista à parte, fora do gráfico.
   - **Cada marca mostra:** produtos e dose por ha; volume de calda (o da O.S.; sem registro, "calda não registrada", nunca os 100 L/ha fixos do código, EX-38); área apontada ("20 de 37,75 ha" quando parcial); O.S.; grupo IRAC/FRAC; fim da carência e reentrada (AG-07).
   - **Alvo da aplicação:** "para este alvo" quando o produto tem registro para cultura × alvo (`MIPD.agf`) ou a O.S. nasceu de decisão do MIP para esse alvo. As demais aplicações de defensivo aparecem em cinza, "outro alvo", porque também podem mexer na contagem.
   - **Tabela equivalente** (TAB-08) com leituras e aplicações, para leitor de tela e teclado.
9. **Par antes × depois e redução observada.**
   - **Antes:** a última leitura válida até 7 dias antes do primeiro apontamento.
   - **Depois:** a primeira leitura válida de 3 a 14 dias depois do último apontamento.
   - Leituras dos dias de aplicação não entram: a ordem no dia é desconhecida.
   - Os limites (7, 3 e 14 dias) são parâmetros com padrão de demonstração; o protocolo pode trazer a janela dele (PRD 33.8, "avaliação na janela do protocolo").
   - Leitura pós já ligada à decisão (`pos_de`, `mipPos`) prevalece sobre a janela.
   - **Redução observada** = (antes − depois) ÷ antes, que é o 1 − depois/antes do CAL-12, pela mesma função do `mipRes`. Só com antes > 0. Se subir, aparece "aumento de X %".
   - **Par parcial**, sempre com o motivo:
     - falta a leitura antes;
     - falta a leitura depois (dentro da janela: "aguardando leitura pós até 04/10");
     - área apontada menor que 95 % do talhão, sem parcela que a represente (parâmetro);
     - aplicação sem O.S. (sem dose e área);
     - outra aplicação de defensivo no talhão dentro da janela ("com interferência");
     - troca de versão do protocolo.
   - **Texto da tela** (uma linha; o resto na dica ⓘ): "Redução observada: compara a leitura antes e depois. Sem uma faixa sem aplicação (testemunha), não prova que o produto causou a queda." Na dica: chuva, inimigos naturais, fase da cultura e a própria dinâmica da praga também mudam a contagem; eficácia (Abbott, Henderson-Tilton) exige testemunha.
   - *Dano evitado:* trocar de produto, ou repetir um, por um caso que não prova nada.
10. **Pressão e atraso** (alimentam o painel e a parte 3).
    - **Pressão do alvo** = soma, dia a dia, do excesso acima do NC que o mapa mostraria naquele dia (o mesmo degrau e a mesma validade da decisão 4). Unidade: a do protocolo × dia. Os dias sem leitura atual aparecem contados à parte.
    - **Atraso do controle** = dias entre a primeira leitura acima do NC e o primeiro apontamento de aplicação para o alvo.
11. **O que reduziu (F1b).** É o AG-06 Eficácia e histórico, lendo o MIP e as O.S. As linhas fixas EF-017 a EF-021 saem.
    - **Lugar:** AG-06 entra no item Pragas e doenças do menu, como o AG-03 e o AG-04. O mapa liga com "Ver o que reduziu ›" na faixa branca, no lugar do link da camada.
    - **Lista** (TAB-08, AGR-02 agrupando por alvo): Alvo (protocolo e unidade) · Produto ou mistura · Grupo IRAC/FRAC · Aplicações · Pares completos · Redução mediana · Mínimo a máximo · Situação.
    - **Mistura** = o conjunto dos produtos da O.S., inclusive adjuvante. Agrupar por produto usa o agrupamento comum da grade.
    - **Comparação** só com pelo menos 3 pares completos (parâmetro, padrão de demonstração). Abaixo disso: "poucos casos (1 de 3)", sem número de redução na coluna. Pares parciais aparecem contados à parte, fora da mediana.
    - **Ordem padrão:** alvo e número de pares completos, nunca pela redução (PRD 33.8: não é lista por potência). Não há "melhor produto".
    - **Mesmo grupo em sequência** no talhão: só aviso, o mesmo do `mipChecks` (AGR-025).
    - **Detalhe (P60):** linha → pares → par → as duas vistorias (AG-01det) e a O.S.
    - **Filtros** pela faixa comum (FIL-01): Fazenda, Safra, Cultura e Alvo.
12. **Leitura, não comando.** A parte 1 não cria comando nem grava nada: só lê o MIP, as O.S. e o cenário. A semente nova é dado de demonstração.

## Parte 2 · MAPA-PRODUTIVIDADE — decisões propostas

1. **Lugar.** Colheita e produtividade › Mostrar · **Produtividade**.
   - A ferramenta **"Importar mapa de colheita"** é a última do alto do mapa e aparece só nessa função, como o "Importar laudo" do Solo (MAP-02).
   - A importação usa a mesma peça de prévia do "Importar talhões" (`talmapa.js`): arquivo → prévia → publicar.
   - A Previsão e colheita ganha só um link para a mesma ferramenta: um serviço, dois caminhos (PRD 62.1).
2. **Formatos.**
   - **Software real:**
     - CSV georreferenciado (lat/lon WGS 84 ou SIRGAS 2000; separador e decimal detectados; mapeamento de colunas salvo por fonte);
     - Shapefile de pontos (.zip com .shp, .shx, .dbf, .prj e .cpg);
     - GeoJSON de pontos;
     - ISOXML (TASKDATA.XML e os TLG*.bin, ISO 11783-10) só quando o leitor ler dados de colheita daquela versão e daquele terminal, com teste real (COLMAP-01 e 10);
     - GeoTIFF de superfície já processada: guarda método e resolução do fornecedor e não finge ter os pontos;
     - PDF ou imagem só como anexo.
   - **Protótipo:** CSV sintético, com o botão "Usar arquivo de exemplo".
   - Nenhuma marca é anunciada como compatível sem teste no terminal real (PRD 62.1).
3. **Talhão, cultura, safra e unidade.**
   - **Talhão:** ponto no polígono do cadastro (`tgDentro`). Pontos em dois talhões viram duas camadas; pontos fora de todos ficam "fora do talhão".
   - **Cultura e safra:** o cultivo do talhão com colheita no período das datas do arquivo. Se houver dúvida, a prévia pergunta só isso.
   - **Unidade:** massa úmida e umidade viram produtividade na umidade de referência. Coluna declarada como já corrigida não é corrigida de novo (COLMAP-05). Unidade sem fator explícito do produto (bu/ac, por exemplo) fica recusada, com motivo.
4. **Limpeza.** Cada ponto leva o primeiro motivo que falhar, nesta ordem. Os padrões são de demonstração, ajustáveis em "⋯ Ajustar limpeza", e refazem a prévia.

| Ordem | Regra | Padrão | Dano evitado |
|---|---|---|---|
| 1 | Fora do talhão | polígono do cadastro | produção de outro talhão ou da estrada no mapa |
| 2 | Umidade inválida | fora de 8 a 40 % | correção de umidade sobre número impossível |
| 3 | Velocidade fora da faixa | fora de 3 a 10 km/h | parada ou manobra que vira pico de produtividade |
| 4 | Início e fim de passada | 2 pontos de cada lado | enchimento e esvaziamento da máquina lidos como mancha |
| 5 | Atraso de fluxo | deslocar N segundos (perfil do monitor; 0 no arquivo sintético) | mancha deslocada do lugar real |
| 6 | Borda | a menos de 1 largura de plataforma (9 m) do contorno | plataforma parcial na borda lida como baixa produtividade |
| 7 | Fora da faixa robusta | \|valor − mediana\| > 3 × 1,4826 × MAD do talhão | pico do sensor; o corte é largo para não apagar baixa produtividade real (COLMAP-04) |

5. **Umidade e unidade.** A equivalência é a do CAL-16 pelo `prMs` (`producao.js:56`): kg × (100 − umidade) ÷ (100 − umidade de referência), com a referência da cultura no cadastro (14 % para soja e milho). Impureza e desconto comercial ficam fora do mapa. A unidade é a da cultura, e o seletor UNID-PROD vale aqui.
6. **Média e cobertura.**
   - **Média** = Σ massa corrigida ÷ Σ área dos pontos válidos (largura × distância). Nunca a média simples dos pontos (PRD 62.3).
   - **Cobertura** = área válida ÷ área do talhão.
   - O total do talhão (média × área) aparece como "estimativa", separado da parte colhida.
7. **Grade e interpolação.**
   - **Regra:** valor da célula = IDW com potência 2 dos 12 pontos válidos mais próximos, até um raio igual ao maior entre 15 m e a meia diagonal da célula.
   - Célula sem ponto no raio fica **"sem registro"**: nunca zero, nunca extrapolada (LABMAP-06).
   - **Peça comum:** a mesma função passa a servir o Solo. O `soloIdw` vira chamada dela com k = todos e raio sem limite, e o Solo não muda.
   - **Por que não krigagem no protótipo:** pede variograma por talhão e conhecimento de geoestatística (Embrapa, Comunicado 96). Com pontos densos de colheita, o ganho é pequeno. No software real, entra como opção com o variograma à vista (§Fora do escopo).
8. **Classes e legenda.**
   - **"% da média do talhão"** (padrão): < 85 · 85–95 · 95–105 · 105–115 · ≥ 115 %.
   - **"Sextos do talhão":** o contraste Talhão do Solo.
   - A legenda traz a unidade e os limites em sc/ha. A dica da célula traz valor, número de pontos e distância ao ponto mais perto.
   - "Sem registro" em cinza hachurado.
   - A paleta é a comum dos mapas de calor (achado A2).
9. **Comparação com a apurada.**
   - Ao lado do mapa: "Mapa 58,97 · Apurada 57,20 sc/ha · +3,09 %".
   - A apurada é a produtividade do mesmo talhão e safra na Previsão e colheita (`prPrtv`: produção na base de umidade da cultura, sem desconto comercial, ÷ área colhida).
   - O mapa nunca substitui a pesagem. Não há calibração automática para "fechar" com a balança (PRD 62.2).
   - Importar não cria carga, lote nem estoque (COLMAP-07).
   - Sem apurada no talhão: "sem produção apurada no talhão" (exemplo: a soja 2025/26 da Santa Rita, aberta sem talhão, D-17).
10. **Servidor e idempotência.**
    - **Comando** "Importar mapa de colheita", com chave = SHA-256 dos bytes do arquivo + talhão + safra + cultura + versão do leitor.
    - **Mesmo arquivo de novo:** "já importado em 16/10 por Marcos (v1)". Nada duplica: camada, área e massa.
    - **Arquivo diferente** para o mesmo talhão e safra: v2. A v1 fica "substituída" e consultável.
    - **Parâmetros de limpeza mudados:** nova versão processada do mesmo original, sem nova importação.
    - **Recibo:** quem, quando, arquivo, SHA-256, leitor, parâmetros e contagens.
    - **Original:** imutável no software real (PRD 62.2). No protótipo ficam o SHA-256, as contagens, os parâmetros e os valores por célula no estado compartilhado (como o laudo do Solo), sem o arquivo inteiro (cota do navegador).
    - *Dano evitado:* área ou produção contadas duas vezes; mapa que muda sem rastro.
11. **Desempenho.** Protótipo: 13.077 pontos (0,80 MB) → prévia em até 2 s a 1440 px (medir). Real: 95 ha a 10 m = 9.500 células; vizinhos por grade de busca.

## Parte 3 · ALAVANCAS — decisões propostas

1. **Lugar e escopo.** Colheita e produtividade › Mostrar · **Alavancas**, em painel lateral (folha inferior no celular).
   - O escopo vem da faixa do topo (Fazenda, Safra, Cultura; FIL-01) e do talhão tocado no mapa. Sem talhão tocado, valem todos os talhões com mapa da cultura e safra.
   - Uma análise é sempre uma cultura × uma safra.
2. **Unidade e mínimo.** Inferência por bloco (1 ha no real; a célula do desenho no protótipo). Mínimo de 30 blocos com valor (parâmetro). Abaixo disso, a tela mostra só os mapas e a dispersão, com "dados insuficientes para medir associação".
3. **Variáveis que entram.** As do catálogo, com a validade em dia. Ficam de fora, com o motivo à vista:
   - **sem variação no escopo** (o atraso de aplicação num talhão só, por exemplo): entra só quando a análise junta vários talhões;
   - **fora da validade** ou **unidade incompatível**;
   - **categóricas** (cultivar, grupo de modo de ação): comparação de medianas por categoria, sem modelo, na F3a;
   - **indicador** (NDVI, NDRE): aparece como "acompanha a produtividade", fora do modelo. *Dano evitado:* o indicador é efeito da produtividade e, no modelo, esconderia K e água.
4. **Associação simples.** Spearman ρ, com intervalo de 95 % pelo z de Fisher (erro padrão √(1,06 ÷ (n_ef − 3))) e **n efetivo** por par.
   - O n efetivo segue Clifford, Richardson e Hémon (1989): Var(r) ≈ [n + Σ_k n_k ρx(k) ρy(k)] ÷ n², n_ef = 1 + 1 ÷ Var(r). ρ(k) é o correlograma de Moran por classe de distância, até metade da extensão do talhão.
   - O p usa t com n_ef − 2 graus de liberdade. O q é o BH sobre as variáveis do escopo.
   - **Em português na tela:** "células vizinhas se parecem; as 134 células deste pivô valem por cerca de 12 observações independentes".
5. **Modelo e importância.** Regressão linear múltipla com as variáveis do escopo.
   - Efeito relativo com as variáveis padronizadas; efeito em sc/ha por unidade, com intervalo de 95 %.
   - **Importância relativa pelo LMG:** média, sobre todas as ordens de entrada, do ganho de R² de cada variável. Soma igual ao R².
   - **Por que LMG e não permutação:** é determinístico, soma ao R² e divide a parte comum das variáveis correlacionadas de um jeito documentado (Grömping, 2006). Roda em 2^p regressões (p ≤ 10 dá 1.024). A permutação depende de sorteio e do modelo escolhido.
   - **Ficam fora do protótipo:** interação, curva (não linear), cultivar como variável no modelo, intervalo do LMG por bootstrap, modelo espacial (SAR ou GLS) e floresta aleatória.
   - **Conferência espacial:** I de Moran dos resíduos (vizinhos por aresta, linhas padronizadas, permutação com 999 sorteios). Com p < 0,05, a tela avisa "dependência espacial restante" e nenhuma variável fica "forte". Sugere aumentar o bloco.
6. **Confiança, em dois níveis.**
   - **"Forte":** q < 0,05 no modelo, com o BH sobre as hipóteses (cada variável fora de grupo e cada grupo pelo teste F conjunto) e resíduos sem dependência espacial.
   - **"Não confirmada":** o resto.
   - A tela nunca diz "causa". Diz "associado a", com a força e a confiança.
7. **Variáveis confundidas.** |ρ| ≥ 0,7 entre duas variáveis explicativas (parâmetro) forma um grupo: uma linha só ("Argila + CTC · andam juntas"), teste F conjunto, LMG somado e nenhum ganho separado. *Dano evitado:* atribuir à CTC o efeito da argila, ou o contrário.
8. **Tipo.**
   - **Controlável:** adubação (K, P), calagem (pH, V %), população, época, irrigação no pivô, momento do controle.
   - **Condição:** argila, CTC, MO, relevo, chuva no sequeiro.
   - **Indicador:** NDVI, NDRE.
   - O "Foque aqui" mostra só controláveis.
9. **Valor.**
   - **Faixas:** a ruim e a boa são o quartil pior e o quartil melhor da variável (P25 e P75 pelo método linear), no sentido do efeito.
   - **Ganho potencial** = |β| × (mediana da faixa boa − mediana da faixa ruim). Intervalo = intervalo de β × a mesma diferença.
   - **R$/ha** = ganho × preço da referência do Comercial, com data e fonte. **R$ na safra** = R$/ha × área da faixa ruim. Dinheiro em decimal.
   - **Na tela:** "Os ganhos não se somam: as faixas se sobrepõem e as variáveis se influenciam."
   - *Dano evitado:* prometer o total de várias alavancas que dividem a mesma área.
10. **Foque aqui.** No máximo 3 cartões, só controláveis com confiança "forte", em ordem de R$ na faixa ruim.
    - **Cartão:** "K baixo · 24,10 ha · até +7,47 sc/ha (5,53 a 9,41) · R$ 966,62/ha".
    - **Uma ação de 1 toque por cartão:**
      - "Criar teste em faixas" (padrão para insumo e manejo);
      - "Abrir recomendação de solo" (SOLO-VRA), depois de efeito confirmado;
      - "Revisar operação no plano" (PA-OPER), para população e época;
      - "Abrir irrigação do pivô" (IR-01), para água. A irrigação não está no plano (DEC-2609-10);
      - "Ver focos de praga" (parte 1), para pressão de praga.
    - Condição e indicador nunca viram cartão.
11. **Ranking e lado a lado.**
    - **Ranking** (TAB-08), em ordem de LMG: Variável · Tipo · Parte da variação (barra com %) · Efeito (sc/ha por unidade, intervalo) · Associação simples (ρ, intervalo, n_ef) · Confiança · n.
    - **Tocar numa variável abre o lado a lado:**
      - mapa da variável e mapa da produtividade, na mesma grade; tocar numa célula destaca a mesma célula nos dois;
      - dispersão com as células e a reta;
      - tabela por zona (SOLO-VRA) ou por setor.
    - A 390 px, o lado a lado vira abas: Variável | Produtividade | Dispersão.
12. **Sobreposição visual.** Na Produtividade, "Sobrepor: focos de praga | zonas de solo" desenha os contornos por cima do mapa de calor. O número que acompanha diz "X ha de baixa produtividade coincidem com focos · coincidência, não causa".
13. **Teste em faixas (F3b).** Fecha o ciclo hipótese → teste → efeito confirmado.
    - **Proposta automática:** 6 pares de faixas (padrão; mínimo 4, OSU), largura em múltiplo da plataforma e do implemento (padrão 18 m = 2 × 9 m), tratamento e testemunha sorteados dentro de cada par, bordadura sem coleta, fora da cabeceira e só na faixa ruim da variável.
    - **O.S. de teste:** nasce em rascunho, em A liberar, com produto e dose do plano (o RT edita). Segue a aprovação agronômica individual (DEC-1610-03). Aprovar não libera (CMD-06).
    - **Análise automática** quando o mapa de colheita daquele talhão e safra entrar: diferença por par (tratamento − testemunha), média com intervalo de 95 % pelo t com (pares − 1) graus de liberdade.
    - **"Efeito confirmado"** quando o intervalo não contém o zero. O valor líquido desconta o custo do tratamento (dose × preço do plano).
    - O efeito confirmado fica registrado na alavanca, com a fonte: O.S., versão do mapa e data. A mesma peça serve depois para testar defensivo com testemunha (§Fora do escopo).
14. **Satélite.**
    - **Protótipo:** série sintética, marcada assim (a Lagoa usa a imagem real só no Mac).
    - **Software real:** Sentinel-2 L2A. Pelo Copernicus Data Space, a conta é gratuita, com 10.000 unidades de processamento por mês na API (conferido em 16/10). O pipeline do protótipo já usa o catálogo Earth Search, sem conta (`areas/inicio.py:381-384`).
    - Processar na nuvem tem custo. A conta em nome da empresa ou um serviço pago é do proprietário (F3c, §Perguntas).
15. **Não é IA.** São contas determinísticas e reproduzíveis com a mesma entrada. A tela não recomenda produto nem dose.

## Telas (master-detail, uma primária, DS do Agrícola)

**Parte 1**
- **Mapa › Pragas e doenças › Evolução.**
  - **Faixa branca:** Mostrar · Alvo (escolha única) · números "Média 12,61 % folhas · Cobertura 18,36 % · Acima do NC 1 · Sem leitura recente 1" · "Ver o que reduziu ›" (F1b).
  - **Rodapé do mapa:** a barra do tempo, numa linha acima da legenda.
  - **Legenda:** acima do NC · foco · perto do NC · abaixo do NC · sem leitura recente (hachurado) · sem leitura · fora do alvo. Cor e texto sempre.
- **Talhão (painel).** Título "Pivô 4 · Ácaro-rajado · % folhas com ácaro". Depois, gráfico; lista de aplicações (▸ abre o par); leituras; programadas.
  - **Primária:** a mesma de hoje, o próximo passo do MIP para o talhão (`mipProx`). O gráfico não cria ação nova.
- **Aplicação (sub-detalhe, no painel):** produtos, dose, calda, área, O.S. e grupo; antes e depois com as duas vistorias; redução ou o motivo do "parcial".
- **AG-06 (F1b):** lista → pares → par, com a primária "Programar avaliação" só onde falta a leitura pós (o `mipPos` de hoje).

**Parte 2**
- **Mapa › Colheita e produtividade › Produtividade.**
  - **Faixa branca:** Mostrar · Classes · números "Média 58,97 sc/ha · Coberta 93,58 % · Apurada 57,20 · +3,09 %".
- **Importar (painel da peça comum).**
  - **Etapas:** escolher arquivo ou "Usar arquivo de exemplo" → prévia ("o que entrou e o que ficou de fora", com o motivo, a área e o mapa dos pontos) → **"Publicar camada"** (primária, BOT-01). "Descartar" e "Ajustar limpeza" ficam no ⋯.
- **Talhão (painel):**
  - média, cobertura, apurada e diferença;
  - área por classe;
  - versão do mapa, com quem, quando, arquivo e SHA-256 curto;
  - links "Ver aplicações", "Comparar com o solo", "Criar vistoria";
  - a primária de hoje (`colhAc`); na F3a, "Ver alavancas".

**Parte 3**
- **Mapa › Colheita e produtividade › Alavancas** (painel): "Foque aqui" (até 3 cartões) → ranking → variável (lado a lado).
  - Sem verde na análise: é consulta. A ação de cada cartão é secundária, com verbo.
- **Teste em faixas (F3b):** painel com o desenho proposto no mapa → primária "Criar O.S. de teste" → a O.S. abre em A liberar.

**Todas**
- **390 px:** sem rolagem lateral da página; alvos de 44 px (o polegar da barra também); folha inferior até metade da altura, com a barra do tempo fixa logo acima; lado a lado em abas.
- **Teclado:** foco visível; Esc fecha primeiro o menu ou o painel aberto; a barra do tempo funciona sem mouse; o gráfico tem a tabela equivalente.
- **Padrão novo no catálogo:** barra do tempo (TEM-01) e lado a lado (LAD-01), com varredura, contraprova e fotos (DEC-1610-12, skill `padrao-safrion`).

## Dados sintéticos de demonstração

Todos sintéticos, marcados "demonstração". Nada aqui é recomendação de campo.

**Parte 1 · Lagoa Grande · Ácaro-rajado** (protocolo `mamao-acaro`: % folhas com ácaro, NC 15, 20 pontos por pivô)
- **Vistorias novas VIS-061 a VIS-072** em `dados_mip.py`. A semente vai para `v=3`, que descarta o estado antigo salvo no navegador, como a `v=2` fez.

| Pivô (ha) | Leituras (data · média · 20 pontos) |
|---|---|
| PV06 (62,79) | VIS-061 25/08 · 22 (16 × 20 e 4 × 30) · VIS-062 04/09 · 9 (18 × 10 e 2 × 0) · VIS-051 19/09 · 18 (já existe) |
| PV04 (73,18) | VIS-063 27/08 · 20 (20 × 20) · VIS-064 10/09 · 6 (12 × 10 e 8 × 0) · VIS-057 22/09 · 4 (já existe) |
| PV17 (33,36) | VIS-065 26/08 · 16 (16 × 20 e 4 × 0) · VIS-066 03/09 · 8 (16 × 10 e 4 × 0) · VIS-060 10/09 · 3 (já existe) |
| PV09 (74,98) | VIS-067 28/08 · 18 (18 × 20 e 2 × 0) · VIS-068 08/09 · 7,5 (15 × 10 e 5 × 0) · VIS-071 20/09 · 5 (10 × 10 e 10 × 0) |
| PV02 (37,75) | VIS-069 01/09 · 12 (12 × 20 e 8 × 0) · VIS-070 09/09 · 10 (20 × 10) · VIS-072 18/09 · 6 (12 × 10 e 8 × 0) |

- **O.S. novas, encerradas, com apontamentos conferidos** (em `dados_lagoa_safra.py` e no `APL` do MIP, chave ácaro-rajado):
  - OS-0521 · PV04 · Acaricida D 0,6 L/ha · calda 1.000 L/ha · 29/08 (40 ha) e 30/08 (33,18 ha);
  - OS-0522 · PV17 · Acaricida D 0,6 L/ha · calda 1.000 L/ha · 28/08 (33,36 ha);
  - OS-0523 · PV09 · Acaricida D 0,6 L/ha · calda 1.000 L/ha · 30/08 e 31/08 (74,98 ha);
  - OS-0524 · PV02 · Fenpiroximato 50 SC 100 mL/100 L + Óleo mineral 0,5 L/ha · calda 1.000 L/ha · 02/09 (20 de 37,75 ha).
- **Já existentes e usados:** a aplicação histórica de Abamectina 18 EC no PV06 em 28/08, sem O.S. (`dados_mip.py:227-235`); OS-0508 (tebuconazol, PV23, 19–20/09); OS-0504 (abamectina, PV06, Liberadas para 24–25/09).
- **Efeitos colaterais previstos na Situação de hoje** (os testes que os conferem mudam junto, com a prova):
  - PV09 e PV02 ganham leitura de ácaro recente: rótulo "· +1" e "Vistorias" do período (7 dias) com +2 na Lagoa Grande;
  - "Encerradas" da Lagoa com +4 O.S.;
  - VIS-060 continua "Vistoria atrasada" (`mip_correcoes_test.py`).
- **Nível de dano:** nenhum protocolo da semente tem ND. O teste de unidade cobre ND com fonte e sem fonte.

**Partes 2 e 3 · Santa Rita · P1 (pivô) · Soja · Safra 2024/25**
- **Safra 2024/25 encerrada,** histórico sintético, com o cultivo P1 · Soja · 95 ha. Fechamento sintético: 5.434 sc (326.040 kg na base de 14 %) em 95 ha = 57,20 sc/ha. A safra entra no filtro Safra do mapa (`_SAFK`, `areas/inicio.py:470`). Os testes que contam safras são conferidos.
- **Arquivo de exemplo** `P1_soja_2024-25_sintetico.csv`, do gerador do `mapa_alavancas_chk.py` (semente 20261016).
  - **Conteúdo:** 13.077 pontos (passadas a cada 9 m, um ponto a cada 5 s, largura de 9 m); 0,80 MB.
  - **Colunas:** `lat;lon;passada;vel_kmh;largura_m;dist_m;umid_pct;massa_kg`. SHA-256 `cb849c20b98b336d45108614ea9c5865ef72e7ddd340d356ffc855d4682ca101`.
  - **Coordenadas:** a conversão linear do `tgCirculo` (111.320 m por grau de longitude × cos(lat); 110.540 m por grau de latitude). Centro do P1 no `pxCoord` do desenho: −15,54727 · −54,29720. Raio pela área do cadastro: 549,9 m.
  - **Defeitos plantados:** a máquina passa 12 m além da borda; início e fim de passada com 35 % da massa; 1 % de paradas (1,2 km/h); 0,5 % de umidade 0; 0,5 % de picos (× 2,5).
- **Camadas por célula** (134 células do P1, já levadas à célula, marcadas "sintético"):
  - solo de 2024 (K, P, MO, pH, V %, argila, CTC);
  - déficit hídrico acumulado por setor angular do pivô (4 setores de 90°: 14, 18, 58 e 16 mm). O setor angular não existe no cadastro de hoje (setor = pivô inteiro) e só serve à demonstração;
  - NDVI de 15/01/2025.
- **Verdade plantada** (sc/ha por unidade): K +0,20 · déficit −0,10 · argila +0,15 · CTC 0 (confundida com a argila) · MO 0 · P 0 · pH 0 e V % 0 (confundidos entre si). NDVI é efeito da produtividade. Ruído de 2,0 sc/ha por célula e de 3,0 sc/ha por ponto.
- **Teste em faixas sintético** (semente 20261017): 6 pares; efeito plantado +3,0 sc/ha; variação entre blocos de 3 sc/ha; ruído por faixa de 1,2 sc/ha.

## Aceite

Os oráculos foram calculados nos scripts de §Conferência (executados). Os testes do produto ainda não existem: estão especificados, não executados.

**Parte 1 · MAPA-MIP-TEMPO**

| ID | Fatia | Caso | Oráculo |
|---|---|---|---|
| T1 | F1a | Lagoa Grande · Evolução · Ácaro-rajado · 04/09/2026 | **Pivôs:** PV06 9 abaixo · PV17 8 abaixo · PV09 18 acima, com 7 dias (= validade, ainda atual) · PV02 12 perto (12 = 0,8 × 15).<br>**PV04:** "sem leitura recente · 27/08 (há 8 dias)", fora da média. Os outros 15 pivôs de mamão: "sem leitura até 04/09".<br>**Média:** 2.634,63 ÷ 208,88 = 12,6131… (mostrada 12,61 % folhas com ácaro). **Cobertura:** 208,88 de 1.137,45 ha (18,36 %), 4 de 20 pivôs.<br>**Mutantes:** leitura velha na média 14,5296; leitura velha como zero 9,3407; média simples 11,75. |
| T2 | F1a | A mesma camada em 23/09 (hoje) | PV06 18 · PV04 4 · PV09 5 · PV02 6. **PV17:** "sem leitura recente" (10/09, 13 dias). **Média:** 2.024,34 ÷ 248,70 = 8,1397… (8,14). **Cobertura:** 21,86 %. |
| T3 | F1a | Unidade e NC (teste de unidade com dois protocolos do mesmo alvo e NC por fase) | "Mosca-branca" com dois protocolos vira duas opções, e não existe média conjunta. Feijão em V e em R na mesma data: "NC varia por fase: 2,0 (V) e 4,0 (R)", sem linha única. Presença: sem média, "k de n com sintoma". |
| T4 | F1a | Barra do tempo | ← e → mudam 1 dia; PgUp e PgDn, 7; Home e End, 25/08 e 23/09. "‹" e "›" saltam entre 25/08, 26/08, 27/08, 28/08, 01/09, 03/09, 04/09, 08/09, 09/09, 10/09, 18/09, 19/09, 20/09 e 22/09. `aria-valuetext` como na decisão 7. F5 mantém a data. A 390 px o polegar tem 44 px. |
| T5 | F1a | Tocar PV04 | **Série:** 27/08 · 20 → 10/09 · 6 → 22/09 · 4; NC 15 tracejado; dias sem leitura atual sombreados (04 a 09/09 e 18 a 21/09).<br>**Marca da OS-0521** em 29–30/08: Acaricida D 0,6 L/ha · 43,908 L no total · calda 1.000 L/ha (73.180 L) · 73,18 ha · IRAC 23 · carência até 06/09.<br>**Par:** 20 → 6 = **redução observada de 70 %**, com a linha de cautela. |
| T6 | F1a | Pares parciais e fora dos pares | **PV02 · OS-0524:** 16,67 %, "parcial · área 20 de 37,75 ha (52,98 %)".<br>**PV06 · 28/08:** 59,09 %, "parcial · sem O.S."<br>**PV23 · OS-0508:** "aguardando leitura pós até 04/10".<br>**OS-0504** (Liberadas, 24–25/09): só em "programadas", fora do gráfico e dos pares. |
| T7 | F1b | O que reduziu · Ácaro-rajado | **Acaricida D · IRAC 23:** 3 aplicações · 3 pares completos · mediana 58,33 % · 50,0 a 70,0 %.<br>**Abamectina 18 EC · IRAC 6:** 1 aplicação · 0 completos, 1 parcial · "poucos casos (0 de 3)".<br>**Fenpiroximato 50 SC + Óleo mineral · IRAC 21A:** 1 · 0 completos, 1 parcial · "poucos casos".<br>Ordem por alvo e pares, não por redução. O detalhe chega à VIS-063, à VIS-064 e à OS-0521. **Mutante:** média em vez de mediana dá 59,44 %. |
| T8 | F1b | Pressão e atraso no PV04 (27/08 a 23/09) | **Pressão:** 5 × 8 dias = 40 (% folhas)·dia, com 10 dias sem leitura atual. **Atraso do controle:** 2 dias (acima em 27/08, primeiro apontamento em 29/08). **Mutante trapézio:** 12,5. |
| T9 | F1a–F1b | DS, celular, erros e o que não pode mudar | 1440 e 390 px sem rolagem lateral; cor e texto em todo estado; uma primária por contexto; sem erro de JS. A Situação muda só como previsto em §Dados. `mapa_faixa_test.py` continua com a faixa de 52 px. |

**Parte 2 · MAPA-PRODUTIVIDADE**

| ID | Fatia | Caso | Oráculo |
|---|---|---|---|
| C1 | F2a | Um ponto (teste de unidade): 9 m × 8 m, 28,8 kg úmidos a 17 % | 4.000 kg/ha úmidos → 3.860,465116 kg/ha a 14 % (CAL-16) → **64,341085 sc/ha**. **Mutantes:** sem corrigir 66,666667; corrigir duas vezes 62,096629; saca de 50 kg 77,209302. |
| C2 | F2a | Média pela área (teste de unidade): (72 m², 4.000) · (36 m², 2.000) · (72 m², 3.500) kg/ha | 612.000 ÷ 180 = **3.400 kg/ha**. A média simples (3.166,67) é o mutante. |
| C3 | F2a | Faixa robusta (teste de unidade): 62, 58, 60, 61, 59, 63, 57, 60, 0, 180, 64 | Mediana 60, MAD 2, limite ±8,8956: saem 0 e 180; 57 a 64 ficam. |
| C4 | F2a | IDW (teste de unidade): pontos a 3, 4 e 5 m com 60, 50 e 70 | 12,591667 ÷ 0,213611 = **58,946684**. Célula sem ponto no raio: "sem registro", nunca 0. |
| C5 | F2a | Prévia do arquivo de exemplo | 13.077 pontos; **entraram 11.851**; ficaram de fora 1.226: início ou fim de passada 483 · fora do talhão 420 · velocidade 126 · borda 69 · fora da faixa robusta 66 · umidade inválida 62. A soma confere. Talhão P1, Soja, Safra 2024/25 detectados sem pergunta. |
| C6 | F2a | Publicar camada | **Média:** 58,97 sc/ha na base de 14 % (58,9688). **Coberta:** 88,90 ha (93,58 %). **Apurada:** 57,20 (5.434 sc ÷ 95 ha). **Diferença:** +3,09 %. As 134 células têm valor. Legenda com sc/ha e classes. **Mutantes:** sem limpeza 59,68; média simples 58,9733. |
| C7 | F2a | Importar de novo e mudar | **O mesmo arquivo:** "já importado em … (v1)"; nada duplicado. **Um byte diferente:** v2, com a v1 "substituída". **Limpeza ajustada:** nova versão processada, sem nova importação. **Cargas, lotes e estoque:** contagens iguais antes e depois (COLMAP-07). |
| C8 | F2a | Umidade | Coluna declarada "produtividade a 14 %": não corrige de novo. Umidade 0 ou 55: "umidade inválida". |
| C9 | F2a | Unidade (UNID-PROD) | kg/ha mostra 3.538,13 (58,9688 × 60); t/ha mostra 3,54. Sem conversão dupla. |
| C10 | F2a | DS, celular e erros | Como T9; a prévia a 390 px em folha inferior; arquivo ilegível com mensagem e caminho. |

**Parte 3 · ALAVANCAS** (P1 · Soja · 2024/25 · 134 células · semente 20261016)

| ID | Fatia | Caso | Oráculo |
|---|---|---|---|
| E0 | F3a | Escopo | 134 células ≥ 30. As 8 variáveis entram; o NDVI fica como indicador. |
| E1 | F3a | Importância | R² = 0,627 = Σ LMG. **Parte da variação:** K 48,7 % · déficit 33,4 % · Argila + CTC 8,8 % · pH + V % 8,0 % · MO 0,9 % · P 0,2 %. |
| E2 | F3a | **Recupera o efeito plantado** | **K:** β +0,241 (0,178 a 0,304) contém +0,20. **Déficit:** β −0,078 (−0,113 a −0,043) contém −0,10. |
| E3 | F3a | "Forte" (BH sobre 6 hipóteses no modelo) | K (q = 3,5 × 10⁻¹¹), déficit (q = 6,1 × 10⁻⁵) e o grupo Argila + CTC (F = 4,90; q = 0,018). |
| E4 | F3a | **Não acusa as nulas** | MO (q = 0,206), P (q = 0,727) e o grupo pH + V % (F = 2,07; q = 0,195) ficam "não confirmada". Os intervalos de β de MO e P contêm o zero. |
| E5 | F3a | **Confundidas como grupo** | Argila + CTC e pH + V % (|ρ| ≥ 0,7), uma linha cada, sem ganho separado. A argila sozinha não se separa (β de −0,33 a 0,27), embora o efeito plantado (+0,15) esteja no intervalo. |
| E6 | F3a | Associação simples com n efetivo | K: ρ 0,670 (0,147 a 0,901), n_ef 12,2. pH: ρ 0,229, q = 0,557. **Contraprova:** com as 134 células tratadas como independentes, pH e V % teriam q = 0,012 (falso positivo por estrutura espacial comum). |
| E7 | F3a | Conferência espacial | I de Moran dos resíduos −0,030 (p = 0,645): sem aviso. No "Por quê": K 0,888 e produtividade 0,558. |
| E8 | F3a | **Valor** (preço R$ 129,40/sc) | **K:** faixa ruim 24,10 ha · +7,47 sc/ha (5,53 a 9,41) contém o plantado 6,20 · R$ 966,62/ha · R$ 23.295 na faixa ruim.<br>**Déficit:** faixa ruim 24,81 ha (setor 3) · +3,44 sc/ha (1,91 a 4,98) contém o plantado 4,40 · R$ 445,14/ha · R$ 11.044.<br>A frase "não se somam" aparece. |
| E9 | F3a | Foque aqui | 2 cartões: "K baixo" → "Criar teste em faixas"; "Água no setor 3" → "Abrir irrigação do pivô". Nenhum cartão de condição (argila) nem de indicador (NDVI). A palavra "causa" não aparece. |
| E10 | F3a | Indicador | NDVI: ρ 0,692, "acompanha a produtividade", fora do modelo. **Mutante com NDVI no modelo:** β de K cai 20,0 % (0,193). |
| E11 | F3a | BH (teste de unidade, em decimal) | p = 0,001 · 0,008 · 0,039 · 0,041 · 0,042 · 0,06 → q = 0,006 · 0,024 · 0,0504 · 0,0504 · 0,0504 · 0,06. Passam 2; sem correção, passariam 5. |
| E12 | F3a | Lado a lado, celular e teclado | Tocar K abre os dois mapas, a dispersão e a tabela por setor. Uma célula destacada nos dois mapas. A 390 px, abas. Tudo pelo teclado. Sem erro de JS. |
| F1 | F3b | Proposta de teste no cartão K | 6 pares de faixas de 18 m, sorteio dentro do par, bordadura, fora da cabeceira, na faixa ruim. O.S. de teste em A liberar, com aprovação individual. A área tratada aparece. |
| F2 | F3b | Análise com o mapa do ensaio (semente 20261017) | **Diferenças:** 0,66 · 2,33 · 1,79 · 2,83 · 2,13 · 4,32. **Média:** 2,34 sc/ha. **Intervalo de 95 %:** 1,07 a 3,61 (t com 5 gl = 2,5706) → **"efeito confirmado"**; contém o plantado (+3,0).<br>**Valor:** 2,34 × R$ 129,40 = R$ 302,80/ha bruto − R$ 240,00 de custo (100 kg/ha de KCl a R$ 2,40, sintético) = **R$ 62,80/ha**. Registrado na alavanca com a fonte. |
| F3 | F3b | O método, não só uma semente | Em 4.000 ensaios simulados, o intervalo contém o efeito em 95,1 % e não contém o zero em 93,0 %. **Mutante sem pareamento:** limite inferior −2,45, contra 1,07. |

## Cliques e digitação (AGENTS §3.3)

O "Antes" foi lido no código em bf7d8b6 e é medido de novo no mesmo teste e cenário, na ponta antes de cada fatia (`ANTES=<_render>`). Nenhum cenário existente pode piorar.

| ID | Cenário | Antes | Depois (teto) |
|---|---|---|---|
| K1 | Ver a média do ácaro na Lagoa em 04/09 | Impossível: o mapa não escolhe data nem calcula média | ≤ 4 cliques (Pragas e doenças, Evolução, Alvo, Ácaro-rajado) + 1 arraste; 0 digitação |
| K2 | Ver a série do PV04 com as aplicações | AG-01 → linha da vistoria → painel → AG-01det: cerca de 4 cliques, sem as aplicações, e mais a O.S. em outra tela | +1 clique a partir do K1 (tocar o PV04) |
| K3 | Ver a redução observada da OS-0521 | Impossível: o AG-06 é fixo; o `mipRes` só calcula com leitura pós ligada | +1 clique a partir do K2 (tocar a marca) |
| K4 | Ver o que se associou a redução no ácaro | Impossível: o AG-06 está fora do menu e é fixo | ≤ 1 clique a partir do K1 ("Ver o que reduziu ›") |
| K5 | Importar o mapa do P1 e vê-lo publicado | Impossível | ≤ 3 cliques (Colheita e produtividade, Importar mapa de colheita, Publicar camada) + escolher o arquivo; 0 digitação quando talhão, cultura e safra são detectados |
| K6 | Comparar o mapa com a apurada | Impossível | +1 clique (tocar o talhão); a diferença também fica nos números da faixa |
| K7 | Ver as alavancas do P1 2024/25 | Impossível | ≤ 4 cliques (Colheita e produtividade, Alavancas, Safra 2024/25, P1) |
| K8 | Criar o teste em faixas a partir do cartão | Impossível | ≤ 2 toques (Criar teste em faixas, Criar O.S. de teste) |

## Contraprova

- **Na ponta antes de cada fatia** (de árvore limpa), com execução e saída versionadas:
  - antes da F1a: não há "Mostrar · Evolução" nem barra do tempo; T1, T2, T4, T5 e T6 reprovam;
  - antes da F1b: o AG-06 mostra as linhas fixas EF-017 a EF-021, e T7 e T8 reprovam;
  - antes da F2a: não há importação nem Produtividade; C5 a C9 reprovam;
  - antes da F3a e da F3b: não há Alavancas nem teste em faixas; E0 a E12 e F1 a F3 reprovam.
- **Mutantes de cálculo** (teste de unidade):
  - **parte 1:** leitura velha na média (14,5296), velha como zero (9,3407), média simples (11,75), validade de 8 dias (o PV04 entraria), leitura do dia da aplicação usada no par, parcial dentro da mediana, média em vez de mediana (59,44 %), trapézio na pressão (12,5), NC único quando varia por fase;
  - **parte 2:** sem limpeza (59,68), média simples, sem correção de umidade (66,67), correção dupla (62,10), saca de 50 kg (77,21), célula sem ponto como zero, importar duas vezes somando;
  - **parte 3:** sem n efetivo (pH e V % com q = 0,012), NDVI no modelo (β de K −20,0 %), sem BH (5 em vez de 2 na lista fixa), teste em faixas sem pareamento (−2,45), ganhos somados (10,91 sc/ha mostrado como total).
- **Mutantes de fluxo** (navegador):
  - a barra recolore sem atualizar a média e a cobertura;
  - a calda some e aparece 100 L/ha;
  - importar cria carga ou lote;
  - a tela diz "causa";
  - o cartão aparece para a argila.
- **Registro honesto:** a primeira execução do `mapa_alavancas_chk.py` usou a semente 20261016 também no teste em faixas, e o intervalo (0,26 a 2,45) não conteve o +3,0 plantado. Um intervalo de 95 % erra 5 % das vezes. Por isso o aceite do F3 prova a cobertura do método em 4.000 ensaios, e o ensaio de demonstração usa semente própria (20261017), dita aqui.

## Testes (proporcionais ao risco: decisão de controle, produtividade e dinheiro)

- **Unidade** (`node mip_tempo_unit.js`, `node colmapa_unit.js`, `node alavancas_unit.js`):
  - todos os oráculos de T, C e E, com os mesmos números dos scripts de conferência;
  - dinheiro e quantidade em decimal;
  - **propriedade** (1.000 casos com semente fixa): a média da fazenda fica entre o menor e o maior valor dos talhões atuais; leitura com idade > validade nunca entra; Σ pontos por motivo + válidos = total; Σ LMG = R²; o BH nunca rejeita mais que o p bruto.
- **Navegador** (`python3 -B mapa_mip_tempo_test.py`, `colmapa_test.py`, `alavancas_test.py`), a 1440 e a 390 px, com toque e teclado:
  - os T, C, E e F da fatia;
  - K1 a K8 com `ANTES`;
  - sem erro de JS.
- **Regressão:**
  - `mip_test.js`, `mip_fluxo_test.py`, `mip_correcoes_test.py`, `praga_alvo_test.py`, `painel_modulos_test.py` (conferir VIS-060 e as contagens da Lagoa);
  - `mapa_faixa_test.py`, `mapa9_test.py`, `popover_390_test.py`, `talmapa_test.py` (a peça de importação);
  - `colheita_mapa_test.py`, `solo_mapa_calor_test.py` (o Solo com a IDW comum não muda), `carencia_test.py`, `producao_unit_test.py`;
  - `ds_1610_test.py` e a galeria da skill `padrao-safrion`.

## Fatias (uma por vez, AGENTS §3.1 e §3.6)

| Fatia | O que entrega | Por que nesta ordem | Depende de |
|---|---|---|---|
| **F1a** | Evolução no mapa: barra do tempo, cor por data, média com cobertura, painel do talhão com série, aplicações e pares | Maior valor do 1º pedido com menor risco: só leitura, sem comando novo, sobre a base do MIP que já existe | uma das três frentes abertas publicada (§3.6) |
| **F1b** | AG-06 vivo ("o que reduziu"), pressão e atraso | Precisa dos pares da F1a | F1a integrada |
| **F2a** | Importar CSV com prévia, limpeza, Produtividade, comparação com a apurada, idempotência | 2º item do 1º pedido; base da parte 3 | F1b, ou antes se o proprietário pedir |
| **F2b** | Shapefile, GeoJSON e ISOXML no software real, com homologação | Precisa de arquivos reais e do terminal | arquivos e monitores reais (§Perguntas) |
| **F3a** | Alavancas: ranking, lado a lado, sobreposição, Foque aqui, com os dados sintéticos | Precisa do mapa de produtividade (F2a) | F2a integrada |
| **F3b** | Teste em faixas com análise automática | Fecha o ciclo da F3a | F3a integrada |
| **F3c** | Satélite real no software real | Conta e custo | decisão do proprietário (§Perguntas) |

## Fora do escopo (com condição de retorno)

| Item | Volta quando |
|---|---|
| Animação "reproduzir" da barra do tempo | o teste com usuários (DEC-1610-02) mostrar que arrastar não basta |
| Eficácia com testemunha (Abbott, Henderson-Tilton) para defensivo | o RT pedir faixa sem aplicação; reaproveita a peça do teste em faixas (F3b) |
| Chuva entre a aplicação e a leitura pós como marca de interferência | houver chuva diária por fazenda no cenário (estação ou fonte com validade) |
| Validade da leitura maior que 7 dias para um alvo (nematoide tem intervalo de 30 dias e aparece "sem leitura recente" depois de 7) | o proprietário mudar a PEND-13 para aquele alvo; hoje o protocolo só pode reduzir a validade (PROJ-13) |
| Krigagem, com variograma à vista | o software real tiver a fatia de mapas e um agrônomo de precisão revisar |
| Calibração do mapa pela balança | aprovação explícita por versão (PRD 62.2); nunca automática |
| Zonas de manejo por várias safras | houver pelo menos 3 safras de mapa no mesmo talhão (Embrapa Pecuária Sul; PRD 62.3) |
| Interação, curva, cultivar no modelo, LMG com bootstrap, modelo espacial, floresta aleatória | a F3a estiver em uso e o teste em faixas mostrar a necessidade |
| Setor angular de irrigação real | houver telemetria por ângulo ou programação por setor no pivô |
| Leitura direta de FieldView, Operations Center ou outro fabricante | o proprietário autorizar conta e contrato |
| Paleta segura para daltonismo nos mapas de calor (achado A2) | frente própria na peça comum, pela skill `padrao-safrion` |
| As duas georreferências da Santa Rita (achado A1) | a frente da geometria da Santa Rita (desenho → polígonos reais) |

## Perguntas ao proprietário

**Nenhuma pergunta nova agora.** As que apareceram foram confrontadas com as decisões existentes:

1. **Validade da leitura de monitoramento:** já decidida. PROJ-13 e PEND-13 (vistoria MIP/MID 7 dias), com o valor aceito pela DEC-1610-04. O protocolo pode reduzir a validade, não aumentar.
2. **Aprovação da O.S. de teste em faixas:** já decidida. Aprovação agronômica individual (DEC-1610-03).
3. **IA:** já decidida. Desligada (DEC-1610-11). A parte 3 é estatística determinística.
4. **Marcas e modelos dos monitores de colheita, e arquivos reais de safras passadas** (F2b): é a mesma pergunta pendente da SOLO-VRA ("o proprietário informar marca e modelo dos monitores"). Faz-se uma vez só, para as duas frentes, quando a F2b abrir. Arquivo real é dado real e fica com ele (AGENTS §2).
5. **Satélite no software real** (F3c): só vai ao proprietário quando a F3a estiver integrada, com a estimativa de custo de processamento por fazenda e mês e a fonte. Nesse momento a pergunta é: conta gratuita do Copernicus em nome da empresa ou serviço pago. O padrão é o mesmo da DEC-1610-11.

## Conferência executada (Decimal e numpy)

Os scripts estão em `/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/chk/`. Na entrega, vão para `docs/integracao/V71/mapa-mip-prod/` com as saídas (§3.6).
- **`mapa_mip_prod_chk.py`** (partes 1 e 2, Decimal, sem ler o repositório): `python3 -I mapa_mip_prod_chk.py` → **28 de 28 conferências passaram** (executado em 16/10/2026). Confere T1–T8 e C1–C4, mais o SHA-256 da idempotência.
- **`mapa_alavancas_chk.py`** (arquivo completo da parte 2 e parte 3; numpy 2.4.6 e scipy 1.17.1; dinheiro em Decimal; semente 20261016): `python3 -I mapa_alavancas_chk.py` → **25 de 25 conferências passaram** (executado em 16/10/2026). Gera o arquivo de exemplo, limpa, interpola, analisa e roda o teste em faixas.
- **Luminância da paleta** do achado A2: calculada em Python (executado).
- **O que não foi executado:** nenhum teste do produto (não há código); a citação de Clifford, Richardson e Hémon (1989) não foi conferida na fonte.
