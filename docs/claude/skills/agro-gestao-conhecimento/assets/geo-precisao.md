# Agricultura de precisão, satélite, georreferenciamento e agrimensura

## Fundamentos geoespaciais (regras para todo dado com posição)
- **Datum oficial do Brasil: SIRGAS 2000** (EPSG:4674 geográfico; UTM SIRGAS 2000 EPSG:31978–31985 para fusos 18S–25S). Armazenar sempre em SIRGAS 2000 (ou WGS 84 EPSG:4326 para app/web — diferença < 1 m, mas **declarar o SRID**); calcular área/distância em projeção métrica (UTM do fuso, ou equal-area para grandes áreas). Converter sempre por biblioteca (PostGIS/proj), nunca manualmente.
- **Banco**: PostGIS (`geometry(Polygon, 4674)`), índice GiST, validação de topologia (`ST_IsValid`, sem auto-interseção, sem sobreposição entre talhões da mesma fazenda, polígono dentro do imóvel); área = `ST_Area(ST_Transform(geom, UTM))`; centroide, buffer, interseção (área de APP dentro do talhão).
- **Formatos**: GeoJSON (web/API), Shapefile e KML/KMZ (importação/exportação com produtor e monitores), GeoPackage, ISOXML/ISO 11783 (máquinas), GeoTIFF/COG (rasters), shapefile de prescrição (colunas de taxa). Importação tolerante: reprojetar, corrigir geometria, avisar unidade.
- **Precisão do GNSS** por uso: navegação/celular 3–10 m; DGPS/SBAS 0,5–1 m; **RTK 2–3 cm** (base própria, rede NTRIP/RBMC-IBGE/IBGE-PPP para pós-processamento); PPP 10–20 cm. Registrar em cada ponto: fonte, precisão (HDOP/estimativa), horário. Piloto automático em plantio/colheita exige RTK e **linhas de referência (AB) persistidas por talhão**.
- **Dados de campo mobile**: ponto GPS + precisão + foto georreferenciada + horário em toda ocorrência/monitoramento, funcionando **offline** com mapa em cache (tiles MBTiles) e sincronização.

## Agrimensura e cadastro rural
- **Georreferenciamento de imóveis rurais** (Lei 10.267/2001, INCRA): obrigatório para transferência/desmembramento; **SIGEF** (certificação de vértices, precisão posicional ≤ 0,50 m em limites artificiais; 3,00 m naturais; 7,50 m inacessíveis — Norma Técnica 3ª ed./Manual Técnico de Posicionamento), responsável técnico credenciado (ART/TRT), **memorial descritivo** (vértices com coordenadas, azimutes, distâncias, confrontantes), planta, matrícula no cartório com **CNM**. O sistema deve armazenar/ler o arquivo SIGEF (.ods/.txt) e exibir a certificação.
- **Cadastros que devem conferir entre si**: matrícula (área registral) · **CCIR/SNCR** (INCRA, código do imóvel) · **CAR** (SICAR: área total, APP, reserva legal ≥ % por bioma — 80 % Amazônia, 35 % Cerrado na Amazônia Legal, 20 % demais; uso consolidado, PRA) · **ITR/NIRF/CIB** (Receita: VTN, área tributável, grau de utilização) · **CAFIR** · **SIGEF/certificação**. Alertar divergência de área entre eles e vencimentos (CCIR anual, ITR set.).
- **Topografia**: levantamento planialtimétrico (RTK, estação total, drone RTK/PPK), curvas de nível, declividade (%) por talhão e classe de aptidão, **terraceamento** (espaçamento por declividade/solo), bacias de contenção, estradas internas e drenagem; MDT/MDS a partir de LiDAR/drone; cálculo de volumes (corte/aterro para silos, açudes, currais); **cadastro de infraestrutura** (cercas, cochos, aguadas, pivôs, redes elétricas, benfeitorias) como camadas.
- **Unidades e conversões**: 1 ha = 10 000 m²; alqueire paulista 2,42 ha; mineiro/goiano 4,84 ha; do norte 2,72 ha; tarefa (NE) ≈ 0,3025–0,4356 ha (varia por estado — parametrizar); acre 0,4047 ha; área declarada × área do polígono (tolerância, ex. 2 %).
- **Divisas e vizinhos**: confrontantes, cercas compartilhadas, servidões, estradas, APP de curso d'água (faixa por largura do rio: 30 m até 10 m de largura, 50 m 10–50 m, etc.), nascentes (raio 50 m), reserva legal averbada/CAR — camadas de restrição que bloqueiam plantio/aplicação (alerta de operação dentro de APP).

## Sensoriamento remoto e satélite aplicado
- **Fontes**: Sentinel-2 (10 m, 5 dias, gratuito — 13 bandas, red-edge), Landsat 8/9 (30 m, 16 d, térmico), MODIS (250 m, diário, séries longas), CBERS-4A (2 m pan), PlanetScope (3 m, diário, pago), Sentinel-1 (radar SAR — funciona com nuvem: umidade, plantio, alagamento), imagens térmicas; **drone/UAV** (multiespectral/RGB/térmica, cm/pixel, sob demanda). Acesso via STAC/Copernicus, Google Earth Engine, Sentinel Hub, Planet API; **máscara de nuvem** (SCL) obrigatória e % cobertura registrada por cena.
- **Índices**: **NDVI** = (NIR − Red)/(NIR + Red) (vigor/biomassa; satura em dossel fechado); **NDRE** = (NIR − RedEdge)/(NIR + RedEdge) (N e vigor em estádios avançados); **EVI** (menos saturação); **SAVI** (solo exposto); **NDWI/NDMI** (água/umidade da planta); **GNDVI**; **LAI** estimado; CIred-edge (clorofila). Normalizar por cultivar/estádio; comparar **talhão vs. média histórica e vs. vizinhos** no mesmo dia.
- **Aplicações com regra de negócio**: série temporal NDVI por talhão (curva da safra, detecção de **anomalias** — mancha com queda > x % vs. talhão → alerta e ponto para vistoria); **estimativa de produtividade** (modelo por curva de índice + histórico + clima — sempre com intervalo de confiança); **zonas de manejo** (clusterização k-means de NDVI multi-safras + produtividade + CE do solo + altimetria → 3–5 zonas estáveis); **detecção de plantio/colheita** (mudança abrupta do índice/SAR) e área plantada; **falhas de estande** (drone, contagem de plantas por visão computacional); **daninhas em reboleira** (drone → mapa de aplicação localizada, economia de herbicida 50–90 %); **estresse hídrico** (térmico/CWSI) para manejo de pivô; **pastagem**: biomassa/altura (kg MS/ha) por satélite para ajuste de lotação e balanço forrageiro; **degradação de pasto** (tendência plurianual); **monitoramento ambiental** (desmatamento — PRODES/DETER/MapBiomas alerta, queimadas — INPE/FIRMS, para conformidade e crédito); **seguro e crédito** (comprovação de plantio, laudo de sinistro por índice, seguro paramétrico).
- **Clima**: estações próprias (pluviômetro, T, UR, vento, radiação) + reanálise (ERA5/NASA POWER) + previsão (INMET/ECMWF/GFS) → balanço hídrico por talhão, chuva acumulada, janela de aplicação/plantio/colheita, graus-dia, alertas de geada/veranico; grade climática interpolada para fazendas sem estação.
- **Qualidade do dado**: guardar cena, data, sensor, % nuvem, processamento (L2A), versão do algoritmo; nunca mostrar índice de cena com nuvem sem aviso; gráficos com lacunas explícitas.

## Agricultura de precisão — ciclo completo
1. **Diagnóstico**: amostragem de solo em grade (1 amostra/2–5 ha) ou por zona; **condutividade elétrica aparente** (Veris/EM38 → textura/umidade); altimetria (RTK/MDT); mapas de produtividade de várias safras (limpeza: remover fluxo < 10 %, velocidade anômala, borda, atraso); NDVI histórico.
2. **Interpolação e mapas**: IDW ou krigagem (com variograma) por atributo (P, K, pH, V%, argila, M.O.); resolução 10–30 m; classes com legenda agronômica (tabela de interpretação estadual); **mapa de variabilidade** com CV por talhão (CV < 15 % → taxa fixa pode bastar).
3. **Zonas de manejo**: combinação normalizada (produtividade multi-safra + NDVI + CE + altitude) → clusterização (k-means/fuzzy) → 2–5 zonas, validadas com solo; **potencial produtivo** por zona (alto/médio/baixo) → meta de produtividade e adubação por zona.
4. **Prescrição de taxa variável (VRT)**: calcário e gesso (por grade/zona), P e K (reposição + correção por classe), N (por NDRE/sensor ativo em tempo real — algoritmo de N-rich strip ou por zona), **população de semente variável** por potencial, aplicação localizada de defensivo (mapa de daninhas/reboleira), fungicida/inseticida por zona de risco; taxa mínima/máxima e arredondamento pelo equipamento; **arquivo no formato do monitor** (Shapefile com coluna de taxa, ISOXML, formatos John Deere/Trimble/AGCO/Case-New Holland/Stara/Jacto) e teste de leitura.
5. **Execução e controle**: piloto automático RTK, controle de seções e de taxa; **mapa "as-applied"** (aplicado real) comparado à prescrição → erro médio, área fora de ± 10 %, sobreposição (< 5 %) e falhas; consumo real vs. previsto por zona; telemetria (ISOBUS/API do fabricante: John Deere Operations Center, Climate FieldView, AGCO, CNH, Solinftec) importada automaticamente.
6. **Avaliação**: mapa de produtividade da safra × zonas × prescrição → **resposta por zona** (kg/ha por kg de insumo), **faixas de teste** (on-farm trials com repetições, análise estatística simples), **retorno econômico** da AP (economia de insumo + ganho de produtividade − custo do serviço/equipamento), atualização das zonas (estabilidade temporal).
- **Sensores e IoT**: umidade do solo (capacitivo/tensiômetro) por zona → manejo de irrigação por setor de pivô (**VRI**), estação meteorológica, armadilhas inteligentes (contagem de pragas por imagem), sensores de silo (termometria), rastreamento de máquinas; protocolos LoRaWAN/NB-IoT; dados com timestamp e localização.
- **Drones**: planejamento de voo (GSD cm/pixel, sobreposição 75/70 %, altura, RTK/PPK ou pontos de controle), ortomosaico, MDS, índices; **pulverização com drone** (MAPA/DECEA/ANAC: registro, faixa, volume ultrabaixo) — registro de operação.

## Gestão do programa de AP (o que o software controla)
- **Camadas por talhão com histórico** (solo por ano, produtividade por safra, NDVI por data, prescrições e as-applied por operação, zonas com versão) — comparáveis lado a lado e sobrepostas, com legenda e valores no toque.
- **Fluxo**: coleta → laboratório (laudo importado por lote de amostra, com QR) → interpretação → prescrição → aprovação do agrônomo → envio ao monitor/operador (app offline) → execução → as-applied → avaliação → próxima safra. Status e responsável por etapa.
- **Integrações**: laboratórios de solo (arquivo padrão), monitores e telemetrias dos fabricantes, plataformas de satélite, estações meteorológicas, SIGEF/CAR (consulta pública), MapBiomas/INPE.
- **Custo e retorno** por talhão: custo da amostragem/mapas/serviço + insumo aplicado (VRT vs. taxa fixa simulada) vs. produtividade por zona — relatório "AP pagou?".

## Indicadores
| Indicador | Cálculo | Meta / uso |
|---|---|---|
| Área georreferenciada e certificada (SIGEF) / área total | % | 100 % dos imóveis |
| Divergência de área (matrícula × CAR × polígono) | % | ≤ 2 % ou justificada |
| Talhões com geometria válida e sem sobreposição | % | 100 % |
| Operações dentro de área restrita (APP/RL) | ocorrências | 0 |
| Cobertura de amostragem de solo (ha/amostra, idade) | por talhão | ≤ 5 ha/amostra; ≤ 3 anos |
| CV da variabilidade (produtividade, P, K, pH) | por talhão | decide taxa variável |
| Erro aplicado × prescrito (VRT) | média e % área fora ± 10 % | ≤ 10 % área |
| Sobreposição / falha de aplicação | % área | < 5 % / 0 |
| Economia de insumo com VRT/aplicação localizada | kg ou R$ vs. taxa fixa | por safra |
| Resposta por zona (kg produzido/kg insumo) | mapa produtividade × prescrição | ajustar metas |
| Anomalias de NDVI detectadas → vistoriadas (tempo) | dias | ≤ 3 dias |
| Estabilidade das zonas de manejo entre safras | % área que mantém classe | ≥ 70 % |
| Acurácia da estimativa de produtividade por satélite | erro vs. real | ≤ 10 % |
| Precisão GNSS dos dados de campo | % pontos ≤ tolerância | ≥ 95 % |
| Retorno do programa de AP (R$/ha) | ganhos − custos | > 0 e crescente |
