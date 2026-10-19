# MAPA-REAL F2 · Imagem Sentinel-2 real da Lagoa Grande no artefato, 19/10/2026

**Pedido do proprietário (19/10):** "o mapa ainda não está usando google earth engine, Leaflet ou similar (escolher o melhor para nosso propósito)".

**Decisão dos agentes:** o mapa continua no MapLibre, que já desenhava a Lagoa Grande. O que faltava era a fonte real. A crítica e a divisão de arquivos estão no PR #47 (6266180436 e 6266211728).
- **Google Earth Engine:** processa imagem, mas não desenha mapa. O uso comercial é pago.
- **Leaflet:** é mais fraco que o MapLibre para camadas de pixel e para muitos objetos.

**Decisão do proprietário (19/10, canal do Claude, lista de escolha):** "Exceção só no artefato privado". Ele enviou o KML na conversa; o Claude processa na nuvem e publica só no artefato privado. Nada vai ao GitHub, e não há custo. Registro no PR #47 (6266706310) e em `../pedidos-proprietario.md`.

**Autoria:** Claude. **Revisão:** Codex.

## O que entra no repositório (só código, nenhum valor real)
- **`tools/geo/s2_l2a.py`:** recebe o KML e gera `dados_lagoa/` e `dados_lagoa_kml.py`, no formato de `tools/prototipo/v37/specs/esquema_lagoa.md`. É o mesmo formato da demonstração sintética, lido por `dados_lagoa_fonte.py`, por isso nenhuma tela mudou.
  - **Imagem:** Sentinel-2 L2A (ESA/Copernicus) pelo catálogo público Earth Search, sem conta e sem custo. Usa as cenas de 25/09 e 10/09/2026, as datas que o Mapa já usa.
  - **Índices do contrato C4 (NDVI, NDRE, EVI, SAVI e NDMI):** calculados por pixel de 10 m dentro de cada pivô. Nuvem e sombra saem pela SCL.
  - **Cor natural:** do produto TCI.
  - **Pivôs:** círculo pelo ponto central do KML e pela área declarada (HECTARE). Para conferência, compara com o círculo desenhado na pasta POLIGONO.
  - **Pasta de saída:** recusa gravar dentro de um repositório git.
- **`tools/geo/s2_l2a_test.py`:** 10 casos com um KML fictício (no mar, valores inventados), sem rede e sem dado real.
- **`tools/prototipo/v37/gen37/.gitignore`:** segunda barreira contra `dados_lagoa/` e `dados_lagoa_kml.py`.

## Defeito achado e corrigido antes de publicar
- **Sintoma:** a primeira saída deu NDVI 1,00 em quase todos os pivôs.
- **Causa:** o catálogo já entrega a reflectância sem o deslocamento de −0,1 da linha de base ≥ 04.00 (`earthsearch:boa_offset_applied: true`). Descontar de novo deixava o vermelho negativo na vegetação densa: o vermelho bruto chegou a 296, isto é, 0,03 de reflectância.
- **Correção:** o desconto só se aplica quando o catálogo ainda não o aplicou.
- **Contraprova:** o caso `Reflectancia` reprova a regra antiga (NDVI > 1).

## Conferência (executada em 19/10)
1. **Processamento real:**
   - 23 pivôs, 2 cenas sem nuvem sobre os pivôs, 16 pontos de água e 18 temas do CAR;
   - fica só no diretório temporário da sessão, fora de qualquer repositório.
2. **Reprodutibilidade:** a versão do `s2_l2a.py` deste commit, rodada de novo sobre o mesmo KML, gerou os 11 arquivos byte a byte iguais aos publicados.
3. **Recusa:** o script recusa gravar com a saída dentro deste repositório.
4. **Build com os dados reais** (árvore `1e927f62`, a do PR #138, mais os dados reais):
   - `paginas_scan` deu 5/5 nas 147 páginas, nos 2 tamanhos e sem erro de JavaScript;
   - nas fotos, o Mapa mostra a imagem real com o NDVI por pixel, a 1440 e 390 px. As fotos não vão ao repositório, porque mostram a fazenda real.
5. **Artefato:**
   - versões 161 a 163 (`1792413975-e91a`), com 147 páginas e 5 arquivos da Lagoa Grande, em 3 lotes;
   - leitura de volta de 7 arquivos (mapa, dados reais e uma página de cada lote): 7/7 iguais ao build por sha256.
6. **Teste sintético:** `python3 -m unittest tools.geo.s2_l2a_test -v` deu 10/10.

## Observações para o proprietário (sem valores aqui)
- **Pivôs:** em 4 dos 23, a área declarada (HECTARE) diverge do círculo desenhado no KML ou falta o círculo. A lista vai ao proprietário no canal dele, não ao repositório.
- **Escopo do mapa real:** a imagem e os pivôs são reais; as O.S. e a safra continuam sendo do cenário de demonstração.

## Fica para depois
- **Mapa de fundo além da margem de 1,5 km:** precisaria de mosaico próprio ou de imagem paga. Fica com o proprietário, junto da cotação de créditos.
- **No software real:** o servidor busca as cenas por organização, a cada passagem do satélite. Entra na passagem para o software real, com homologação e o aceite do proprietário.
