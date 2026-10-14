---
name: indicadores-satelite
description: Projete e revise mapas de índices de satélite ou drone, contraste, qualidade e manchas para vistoria. Use em NDVI, NDRE, EVI, índices hídricos e mapas de vigor; não confunda contraste com diagnóstico.
---

# Indicadores de satélite: cores vivas, falhas visíveis

## Integração ao mapa e prova de suporte

Reutilize mapa, navegação, tokens e contrato de índices do projeto. No Safrion, C4 é a fonte do escopo e dos aceites de NDVI, NDRE, EVI, SAVI e NDMI; não acrescente menu separado por seguir um exemplo desta skill. Cada índice exige bandas, fórmula, resolução efetiva, qualidade e fonte verificáveis; suporte a NDVI não comprova suporte aos demais.

Mantenha cena/data, resolução, máscara, área válida e escala absoluta/relativa visíveis no contexto necessário. Sem dado/nuvem não é zero nem área de baixo vigor. Não transforme contraste relativo em diagnóstico ou recomendação automática. Raster sintético demonstra interação e deve ser identificado; não comprova integração com provedor nem observação real. Revalide somente índices/caminhos afetados por uma mudança.


**Norte:** tornar a variabilidade legível, com cores vivas e pixels dentro do talhão. Índice baixo ou cor vermelha indica valor/variação a investigar, não comprova praga, morte ou perda. Escala relativa mostra contraste interno, não gravidade: uma lavoura saudável também pode conter pixels vermelhos nesse modo.

Limiares abaixo são exemplos configuráveis, não diagnóstico universal. Validar por índice, cultura, estádio, sensor e qualidade; cores sempre acompanhadas de valores, legenda e indicação de escala. Comparações entre talhões/datas exigem escala e processamento compatíveis.

Complementa `agro-gestao-conhecimento` (assets/geo-precisao.md, que define fontes, índices e fórmulas). Telas seguem `master-detail-ux`; tabelas seguem `tabelas-interativas`; corte final por `minimalismo-essencial`. Referência de código, paleta e algoritmos em [assets/referencia-implementacao.md](assets/referencia-implementacao.md) — ler antes de codar.

## 1. Os dois níveis de visão (obrigatórios)

| Nível | O que mostra | Como |
|---|---|---|
| **Fazenda** (listagem) | Todos os talhões/pivôs sobre imagem real (true color ou basemap de satélite). Cada polígono preenchido com o raster do índice em cores vivas, opacidade 85 %. **Número/nome do talhão grande no centro** (fonte bold, halo branco ou escuro), legível em qualquer zoom. Manchas fracas aparecem como "ilhas" vermelho/laranja dentro do verde. | Escala **absoluta** (mesma cor = mesmo valor em toda a fazenda) para comparar talhões. Fora dos polígonos, sem overlay. |
| **Talhão** (detalhe) | Um talhão em tela cheia, raster na resolução efetiva das bandas e do processamento, explicitada por fonte/índice, **sem suavização** (`image-rendering: pixelated`, nunca interpolação bilinear/blur). Legenda com as classes e os valores reais. Falhas e zonas fracas delimitadas. | Escala **relativa ao talhão** por padrão (estica percentil 2–98 do próprio talhão), que é o que revela variabilidade dentro de uma lavoura uniforme — ex. 0,84 a 0,93 vira vermelho→verde completo. |

Alternador único e sempre visível: **Contraste: Talhão | Fazenda | Absoluto**. Trocar escala recolore no cliente, sem nova requisição.

## 2. Paleta viva (única em todo o sistema)

O design system e o contrato do projeto prevalecem; a rampa abaixo é uma referência para projetos sem decisão vigente. 6 classes, gradiente contínuo entre elas. Nunca dessaturar, nunca usar paleta "viridis"/azul para vigor.

| Classe | Significado | Cor | NDVI absoluto (padrão, editável por cultura/estádio) |
|---|---|---|---|
| 1 | Índice muito baixo — investigar | `#E4002B` vermelho | < 0,30 |
| 2 | Fraco | `#FF6A00` laranja | 0,30 ≤ índice < 0,45 |
| 3 | Atenção | `#FFD500` amarelo | 0,45 ≤ índice < 0,60 |
| 4 | Médio | `#B5E61D` verde-limão | 0,60 ≤ índice < 0,72 |
| 5 | Bom | `#3FBF2A` verde vivo | 0,72 ≤ índice < 0,82 |
| 6 | Vigor alto | `#0B7A1E` verde escuro | ≥ 0,82 |

- **Nuvem, sombra, neve, sem dado**: cinza `#9E9E9E` hachurado, nunca cor de índice; % de nuvem do talhão sempre exibido. Cena com > 20 % de nuvem no talhão não entra na série sem aviso.
- **Legenda sempre com os valores reais** de cada faixa (no modo relativo os limites mudam por talhão e a legenda acompanha).
- Mesmas cores e mesmos nomes de classe em mapa, tabela, gráfico, badge de status e relatório PDF.
- Índices que não são vigor (NDWI/NDMI umidade, térmico/CWSI) usam a mesma lógica de 6 classes, mas com paleta própria declarada uma vez (azul para água, vermelho para estresse térmico) — nunca reaproveitar a rampa de vigor.

## 3. Falhas e partes fracas (detecção automática)

A classe absoluta usa os limites configurados da paleta; a classe relativa usa os cortes da escala vigente. A cor contínua deve ser calculada pela mesma função para pixel e legenda, sem inferir classe pela posição visual na rampa.

O mapa não é só imagem: o sistema **encontra e lista as manchas**.

1. **Estatística por talhão e data**: média, mediana, desvio, P2/P10/P90/P98, % de área por classe, % nuvem. Excluir borda de 1 pixel do polígono (efeito de borda) da estatística.
2. **Pixel de baixo índice relativo**: definir explicitamente o algoritmo. No exemplo conservador, valor < min(média − 1,5 DP, P10), equivalente a atender ambos os cortes, não ao OU. Excluir nodata, tratar dispersão nula e amostra insuficiente. Classe 1 absoluta é indício para investigar, não falha comprovada.
3. **Mancha**: pixels candidatos contíguos (8-vizinhos) acima da área mínima definida. Três pixels inteiros de 10 × 10 m = 300 m² = **0,03 ha**; em 20 m são 0,12 ha. Calcular pela resolução/transformação real e recorte, sem fixar área pelo nome do sensor. Cada mancha tem geometria, área válida, classe, valor, ponto de vistoria dentro do polígono e evolução em cenas comparáveis.
4. **Queda temporal**: aplicar os níveis da tabela de estados abaixo (atenção de 10–15 %, crítico acima de 15 %) somente como exemplo configurável e validado por cultura/estádio; comparar cenas válidas e comparáveis. Definir denominador e tratar índice anterior zero/negativo ou ausente antes de usar percentual; não gerar diagnóstico agronômico pela queda isolada.
5. **Padrões espaciais** geram hipóteses de vistoria, não causa nem recomendação de aplicação automática. Forma, cor ou consenso de modelos não substituem dados de campo e validação técnica.
6. **Estado do talhão** derivado, visível na listagem e no mapa:

| Estado | Regra | Ação primária |
|---|---|---|
| Sem imagem | nenhuma cena válida ≤ 15 dias | Buscar imagens |
| Sem dado | cena sem estatísticas confiáveis, amostra insuficiente ou valores indisponíveis | Ver qualidade da cena |
| Nuvem | última cena com > 20 % nuvem no talhão | Aguardar próxima cena |
| Normal | área fraca < 5 % e sem queda | Ver histórico |
| Atenção | área fraca 5–15 % ou queda 10–15 % | Ver manchas |
| Crítico | área fraca > 15 % ou queda > 15 % ou mancha nova > 1 ha | Criar vistoria |

## 4. Telas (master-detail)

- **Menu → mapa/listagem vigente do projeto**: mapa da fazenda (§1) + tabela de talhões com colunas: talhão, cultura/estádio, data da cena, índice médio, variação vs. anterior (seta e %), % área fraca, nº de manchas, % nuvem, estado, próximo passo. Filtro/ordenação no cabeçalho, agrupar por fazenda/cultura/estado, clique na linha ou no polígono abre o detalhe (`tabelas-interativas`). Seletor de data e de índice no topo, um só.
- **Detalhe do talhão**: raster grande (§1) com legenda e alternador de contraste; ao lado: estado + ação primária; **lista de manchas** (área, classe, evolução, botão "Ir para" que centraliza o mapa e "Criar vistoria" que gera ocorrência com GPS); histograma das classes (% de área); série temporal do índice médio com faixa P10–P90, lacunas de nuvem explícitas, marcos de plantio/aplicações; comparar duas datas lado a lado (slider ou split).
- **Sub-detalhe: mancha**: recorte do raster centrado na mancha, área e evolução por data, tipo provável, fotos/laudo da vistoria, status (detectada → vistoriada → causa identificada → resolvida/ignorada). Uma ação primária por status.
- Toque/hover em qualquer pixel mostra valor do índice, classe e coordenada. Exportar: PNG do mapa com legenda, GeoTIFF/Shapefile das manchas para o monitor.

## 5. Implementação (resumo; detalhes no asset)

- **Pipeline**: cena L2A (Sentinel-2 via STAC/Copernicus/Sentinel Hub; drone via GeoTIFF) → máscara SCL/nuvem → índice por banda em float32 → clip pelo polígono do talhão (SIRGAS 2000/WGS 84, SRID declarado) → estatísticas + classificação + manchas (job assíncrono, idempotente por cena+talhão) → armazenar raster como COG e resumo em tabela.
- **Dados**: `cena` (sensor, data, nuvem %, versão do processamento), `indice_talhao_cena` (estatísticas, % por classe, referência do COG), `mancha` (geometria, área, classe, valor, centroide, status, vínculo à vistoria).
- **Frontend**: mapa (MapLibre/Leaflet) + camada raster colorizada **no cliente** por função pura `corDoIndice(valor, escala)` — permite trocar contraste sem nova requisição; rótulos dos talhões em camada própria sempre acima do raster; renderização sem suavização.
- **Testes** (`dev-testes`): classificação por faixa (limites inclusivos), stretch por percentil, detecção de manchas em raster sintético (mancha de 3 px conta, 2 px não; borda excluída), regra de estado, cores/hex iguais em mapa e legenda.
- **Performance**: usar COG/overviews, tiles ou formato adequado ao recorte; medir transferência, primeira pintura e interação no dispositivo/rede-alvo contra as metas do projeto. Não reduzir qualidade analítica para atingir um número arbitrário.

## 6. Checklist de entrega
- [ ] Mapa da fazenda com número grande em cada talhão e manchas vermelhas/laranjas visíveis de longe.
- [ ] Detalhe do talhão pixelado, sem blur, com escala relativa por padrão e legenda com valores reais.
- [ ] Alternador Talhão | Fazenda | Absoluto recolorindo no cliente.
- [ ] Paleta de 6 cores exatas (§2) reutilizada em mapa, tabela, badge e gráfico.
- [ ] Nuvem em cinza hachurado, nunca com cor de índice; % nuvem visível.
- [ ] Manchas detectadas, listadas com área/ha, centroide e ação "Criar vistoria".
- [ ] Estado do talhão (5 estados) com uma ação primária cada, na listagem e no detalhe.
- [ ] Série temporal com lacunas explícitas e comparação de duas datas.
- [ ] Testes unitários das funções de cor, stretch, manchas e estado.
