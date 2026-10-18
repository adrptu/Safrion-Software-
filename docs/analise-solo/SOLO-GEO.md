# SOLO-GEO · laudo georreferenciado, mapa de calor, zonas e taxa variável (rascunho R1, 18/10/2026)

Autor: Claude · revisor: Codex · integrador: Codex (DEC-0910-02) · protótipo no regime leve (AGENTS §3.5).
Visão macro e micro do Mapa: [`docs/mapa/MAPA-VISOES.md`](../mapa/MAPA-VISOES.md). O Solo é a primeira camada a recebê-la.

## Pedido do proprietário (18/10/2026, literal)

> "nao vi conexao dos laudos de analise de solo com a questao do georeferenciamento, como vamos ver o mapa de calor sem os dados de georeferenciamento de cada ponto? e como vamos fazer agricultura de precisao em taxa variavel e enviar arquivos para as máquinas sem isso?"
>
> "No mapa em analise de solo, só podemos ver indicador por indicador, temos que ter opção de ver todos talhoes e dentro do talhao todos indicadores (min, médio e máximo) para uma visão macro mais sistemica e global de como está nosso solo, rapidamente numa visao integrada."

## 1. Diagnóstico (código de `b812702c`, executado e lido)

| Ponto | Hoje | Efeito |
|---|---|---|
| Pontos da amostragem | `dados_solo.pontos()` gera de 8 a 30 pontos por laudo numa espiral, em posição relativa (u, v) dentro do talhão, com a média igual ao laudo composto | O mapa de calor é **demonstração**. Não vem de amostra real. |
| Coordenadas | O Mapa converte (u, v) em pixel e em lon/lat só para mostrar (`soloGrade`, `lgLL`) | Nenhum ponto tem latitude e longitude registradas, precisão do GPS ou ID do laboratório. |
| AG-02 (laudo) | Registra o laudo composto (PDF/OCR) e valida | O laudo **não mostra nem importa pontos**. Por isso o proprietário não vê a ligação. |
| Plano de amostragem | Não existe | Não há grade, densidade, ID de ponto nem navegação até o ponto. |
| Interpolação | IDW (inverso do quadrado da distância) com todos os pontos do talhão, mascarado pelo talhão | Funciona. Faltam limite de vizinhos e raio, densidade e confiança. |
| Classes | Absoluto usa a tabela demonstrativa | A tabela regional ainda depende do proprietário. |
| Zonas e prescrição | Não existem. O #131 SOLO-VRA ficou só na fila | Não há taxa variável nem arquivo para máquina. |
| Visão | Um indicador por vez | Não há visão de todos os talhões × indicadores. |
| Geometria | Santa Rita em plano de desenho, sem coordenada. Lagoa Grande com contornos lon/lat (sintéticos fora do Mac) | Para gerar prescrição, todo talhão precisa de limite georreferenciado. |

**Severidade proposta:** S2 para o software real, porque o mapa de calor parece medido e não é. No protótipo, a tela passa a dizer quando o ponto é sintético.

## 2. Ciclo completo (agricultura de precisão), do limite ao "como aplicado"

1. **Limite georreferenciado do talhão** em WGS84, importado de KML/KMZ, SHP ou GeoJSON. A importação de KMZ no Mapa já existe (F1). É pré-requisito: sem limite não há grade nem prescrição.
2. **Plano de amostragem**, em grade regular ou por zonas:
   - **Grade:** densidade em ha por ponto. É um parâmetro do responsável técnico, com padrão de demonstração de 2 ha/ponto.
   - **Zonas:** histórico de NDVI, produtividade ou condutividade.
   - **Cada ponto:** ID único `FAZ-TALHÃO-Pnn`, lat/lon, profundidades (0–20 e 20–40 cm) e raio das subamostras.
   - **Exportar o plano** para o app de campo e em GPX, KML, GeoJSON ou CSV.
3. **Coleta no app**, que funciona sem internet:
   - navega até o ponto;
   - grava a posição real, com a precisão do GPS em metros, o código da sacola (QR) e a profundidade;
   - desvio acima da tolerância (padrão 15 m) vira **aviso**, não bloqueio.
4. **Resultado do laboratório por amostra** (CSV/XLSX), juntado pela ID.
   - Recusa: ID desconhecida ou duplicada, valor sem unidade, unidade sem conversão.
   - Aviso: ponto sem resultado.
   - O laudo composto do talhão passa a ser **derivado** dos pontos (média ponderada pela área de influência), e não digitado de novo.
   - O PDF/OCR continua para o laudo composto sem grade.
5. **Validação do agrônomo** sobre o lote de amostras. Como hoje, o OCR nunca valida.
6. **Interpolação** por indicador e camada:
   - **F1:** IDW com potência 2, até 12 vizinhos e raio de busca, em células de 10 m × 10 m, mascarado pelo talhão.
   - **F5:** krigagem ordinária quando houver pelo menos 30 pontos e o semivariograma ajustar.
   - **A tela mostra:** n pontos, densidade (ha/ponto), CV %, erro da validação cruzada e "baixa confiança" abaixo de 1 ponto a cada 5 ha ou com menos de 6 pontos.
7. **Classes agronômicas** pela tabela regional. A escolha da tabela é do proprietário e está pendente. Até lá vale a tabela demonstrativa, rotulada como tal.
8. **Zonas de manejo:**
   - agrupamento k-means de 2 a 5 zonas sobre os indicadores escolhidos, com área mínima por zona e suavização;
   - o responsável técnico aprova;
   - as zonas aprovadas servem à próxima amostragem e à prescrição.
9. **Prescrição em taxa variável** (calcário, gesso, P₂O₅ e K₂O; semente fica para depois):
   - a dose de cada célula ou zona sai **da mesma fórmula** da recomendação do talhão, aplicada ao valor interpolado (serviço único de domínio, ENG-011, com unidades explícitas, ENG-013);
   - limites da máquina: dose mínima, dose máxima e passo;
   - o total da prescrição é comparado ao plano e ao estoque;
   - cada prescrição tem versão e hash, e a **O.S. carrega a prescrição aprovada** (aprovação agronômica individual, PRD 41).
   - **Arquivos:**
     - **Shapefile** (zip com .shp/.shx/.dbf/.prj, WGS84), com o atributo `Rate` e a unidade no nome do campo e no .prj/.cpg. É o formato aceito pela maioria dos monitores.
     - **ISO-XML** (ISO 11783-10, `TASKDATA.XML`), com grade do tipo 2 ou zonas de tratamento, para terminais ISOBUS.
     - **KML/GeoJSON** para conferência visual.
   - **Trava só onde protege algo concreto:**
     - dose fora dos limites da máquina, produto sem conversão de unidade e prescrição sem aprovação **bloqueiam**;
     - densidade baixa e classe demonstrativa são **aviso**.
10. **"Como aplicado"** (as-applied) importado da máquina: consumo real por zona, desvio da prescrição e custo por hectare. A safra seguinte compara produtividade × solo × prescrição.

## 3. Visão macro e micro do solo (pedido 2; padrão geral em MAPA-VISOES)

- **Resumo** (macro sintética), por fazenda e camada:
  - uma barra por indicador com a % da área em cada classe;
  - a frase do que importa, por exemplo "K abaixo do adequado em 212 ha (31 %)".
- **Matriz** (macro analítica):
  - linhas são os talhões e colunas são os indicadores do laudo;
  - cada célula mostra **mín · méd · máx**, colorida pela classe da média, com uma barra do mínimo ao máximo sobre a escala de classes;
  - um laudo composto sem grade mostra só o valor, com a marca "composta";
  - o rodapé traz a média da fazenda ponderada pela área;
  - dá para ordenar por qualquer indicador e filtrar "só o que está abaixo do adequado".
- **Talhão** (micro sintética): todos os indicadores do talhão em mini-mapas (pequenos múltiplos) com a mesma legenda, mais mín/méd/máx, CV % e n pontos.
- **Indicador do talhão** (micro analítica): o mapa de calor grande, com os pontos (ID, coordenada e valor), histograma, zonas, recomendação e prescrição.
- **Navegação:**
  - célula → indicador do talhão;
  - talhão → talhão;
  - "‹ Matriz" volta;
  - o filtro de camada, laudo e contraste é o mesmo nas quatro visões.

## 4. Fatias

| Fatia | Conteúdo | Dano evitado |
|---|---|---|
| **F1** (agora, protótipo) | Matriz e Resumo do Solo. Talhão com todos os indicadores. Ponto com lat/lon e origem ("sintético de demonstração" ou "medido"). Aba **Pontos** no laudo do AG-02 com ID, lat, lon, precisão e valores. Importar CSV de pontos (ID, lat, lon) e de resultados por ID, com recusas | Decidir pelo mapa sem saber de onde vem o número |
| F2 | Plano de amostragem (gerar grade no polígono, densidade, exportar), coleta no app com GPS e QR | Amostra fora do lugar, ID trocada |
| F3 | Zonas, prescrição (calcário, gesso, P, K), limites da máquina, aprovação na O.S., exportação Shapefile e ISO-XML, import do "como aplicado" | Dose errada na máquina, insumo a mais ou a menos |
| F4 | MAPA-VISOES nas outras camadas | Análise lenta, camada por camada |
| F5 | Krigagem, validação cruzada, produtividade × solo | Mancha falsa por interpolação ruim |

No artefato publicado, o ambiente bloqueia o download. Na F3, a tela gera o arquivo, mostra o conteúdo, o tamanho e o hash, e diz isso. No software real, o arquivo é baixado e enviado.

## 5. Aceite da F1 (com contraprova na v134)

- **G1** Mapa › Solo tem a visão **Matriz**: todos os talhões com laudo × todos os indicadores da camada, com mín · méd · máx. Oráculo: estatística dos pontos do laudo (Decimal), uma casa a mais que o laudo.
- **G2** A cor da célula é a classe da média, com a mesma escala do mapa. A barra mín–máx fica sobre a escala de classes.
- **G3** O laudo composto sem pontos mostra o valor e "composta". Talhão sem laudo aparece na linha "sem laudo", com "Registrar laudo ›".
- **G4** Ordenar por K e filtrar "abaixo do adequado" mudam a matriz e o número de talhões.
- **G5** Resumo: a área por classe de cada indicador soma a área com laudo (±0,1 ha), e a frase de destaque vem do pior indicador por área.
- **G6** Clicar no talhão abre **Talhão**: todos os indicadores em mini-mapas, com mín/méd/máx, CV % e n pontos.
- **G7** Clicar na célula abre o mapa de calor daquele talhão e indicador. "‹ Matriz" volta com ordem e filtro mantidos.
- **G8** AG-02 › laudo › aba **Pontos**:
  - ID, lat e lon com 6 casas, origem e valores;
  - a média dos pontos é igual ao composto;
  - a origem "sintético de demonstração" aparece na aba e no Mapa.
- **G9** Importar o CSV de pontos com coordenada fora do talhão, ID repetida ou linha sem coordenada: recusa linha a linha, e nada é gravado.
- **G10** Importar o CSV de resultados por ID:
  - grava o lote;
  - o Mapa passa a usar os pontos medidos e mostra "medido";
  - a matriz muda.
- **G11** No celular (390 px) a matriz rola dentro do contêiner, com a 1ª coluna fixa; teclado e leitor de tela percorrem as células; nada sai da página.
- **G12** Nenhum erro de JavaScript e nenhuma gravação ao só olhar.

## 6. Fora do escopo agora (condição de volta)

- Integração direta com nuvens de fabricantes (Operations Center, Climate e outras): é integração externa, decisão do proprietário.
- Tabela regional de classes: volta quando o proprietário escolher a tabela.
- Taxa variável de semente e de defensivo: volta depois da F3, com mapa de produtividade.

## 7. Perguntas ao Codex

1. A matriz deve mostrar também o P10/P90 além de mín/máx, por robustez a ponto anômalo? Minha proposta é mín/méd/máx visíveis e P10/P90 na dica.
2. "Baixa confiança" abaixo de 1 ponto a cada 5 ha ou com menos de 6 pontos: aceita como padrão de demonstração?
3. A prescrição na O.S.: a aprovação agronômica aprova a versão (hash) da prescrição, e qualquer mudança gera versão nova e volta para aprovação. Concorda?
4. CSV de resultados: colunas mínimas `id_amostra, profundidade, analito, valor, unidade, metodo`. Formato longo ou largo?
