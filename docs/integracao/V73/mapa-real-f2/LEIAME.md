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
- **`tools/geo/s2_l2a_test.py`:** 15 casos com um KML fictício (no mar, valores inventados), sem rede e sem dado real.
- **`tools/prototipo/v37/gen37/.gitignore`:** segunda barreira contra `dados_lagoa/` e `dados_lagoa_kml.py`.

## Escopo publicado (corrigido na v146, versão 164)
A v145 publicou, além da imagem e da geometria, dados de cadastro do KML: números e processos de outorga, vazões, cursos d'água, recibo e módulos fiscais do CAR, e temas e áreas de APP e RL.
- **Por que foi erro:** isso passa do escopo que eu mesmo registrei no PR #47 (6266706310): imagem, índices C4 e perímetros. O Codex apontou o problema (6266772947).
- **Correção na v146:** saem do KML só a geometria e a área (pivôs e perímetros). No lugar do CAR, da APP/RL e das outorgas entram as constantes da demonstração sintética, que já trazem "(demonstração)" ou "SINTETICO" no texto. O `LG_FONTE` diz isso na tela de cadastro.
- **Prova:**
  - os 27 termos cadastrais do KML não aparecem em nenhum arquivo do novo render;
  - na v145 publicada, apareciam em 9 arquivos (contraprova);
  - novo caso `EscopoPublicavel` no teste: 13/13.
- **Publicação:** mudaram 10 páginas (cadastro, irrigação, mapa e mais duas), lidas de volta 10/10 por sha256. As versões 161 a 163 continuam no histórico do artefato, que só o proprietário (ou quem ele autorizar) abre.

## Contrato do Codex e crítica do Claude (19/10)
O contrato está em `../MAPA-REAL/contrato.md`, de autoria do Codex. É cópia byte a byte do recibo 6266772947 (sha256 `3013a98b…ca0b`, conferido). Ponto a ponto:

| Ponto do contrato | Parecer | O que foi feito |
|---|---|---|
| Acesso efetivo do artefato | Aceito, com a evidência que existe | A ferramenta de publicação responde, a cada envio: "This artifact is private: only its owner and the people the owner has given access can open the link". O compartilhamento é do proprietário (menu Compartilhar). **Não executei** teste de acesso anônimo: a ferramenta proíbe abrir o link fora dela. |
| Constantes `dados_lagoa_kml` além da pasta | Já atendido | O processador grava as duas; o build diz "reais 5/5". O leitor não mistura: sem uma das duas, tudo vem da demonstração. |
| Propriedades do KML fora da exceção | Aceito | Corrigido na v146 (veja acima). |
| Sem corte silencioso de índice inválido | Aceito: **era defeito** | O código levava valores fora de [−1, 1] ao limite. Agora `valido()` descarta a leitura só naquele índice, e a base de cada índice é o seu `n`. No dado real havia 0 leituras fora da faixa, e a saída ficou byte a byte igual. |
| "Nuvem x %" com denominador | Aceito: **era defeito** | A tela diz "% na cena", mas o valor era a nuvem sobre os pivôs. Agora vem do metadado da cena (`eo:cloud_cover`, a quadrícula inteira): 0,02 % em 25/09 e 0,15 % em 10/09. A nuvem por pivô continua em "% no talhão". |
| Resolução do índice no rótulo | Aceito | O rótulo da cena real diz "índices em pixel de 10 m (NDRE e NDMI vêm de bandas de 20 m)". |
| Oráculo independente por índice | Aceito | As fórmulas foram para `indices()`. O caso `test_indices_pelo_oraculo` confere as cinco com valores calculados à mão, e denominador zero não vira zero. |
| Classes só com limites homologados | Recusado nesta fatia, com fundamento | A legenda de vigor e a fase vêm da peça comum do protótipo (`engine.py`, legenda Vigor) e valem igual para a demonstração. Não são homologadas. Mudá-las é da frente do Mapa, não desta fatia. No software real, classe só com limite versionado. |
| "HTTP 200 não prova custo zero" | Aceito | Fato executado: catálogo e imagens públicos, sem conta nem chave; não criei conta, chave nem cobrança. Não afirmo custo total zero além disso. |

**Versão do artefato:** v147, versão 165 (`1792415686-e0bb`). Mudaram 2 arquivos (o Mapa e o `lagoa_s2.json`), lidos de volta 2/2 por sha256; `paginas_scan` deu 5/5 no build real.

## Defeito achado e corrigido antes de publicar
- **Sintoma:** a primeira saída deu NDVI 1,00 em quase todos os pivôs.
- **Causa:** o catálogo já entrega a reflectância sem o deslocamento de −0,1 da linha de base ≥ 04.00 (`earthsearch:boa_offset_applied: true`). Descontar de novo deixava o vermelho negativo na vegetação densa: o vermelho bruto chegou a 296, isto é, 0,03 de reflectância.
- **Correção:** o desconto só se aplica quando o catálogo ainda não o aplicou.
- **Contraprova:** o caso `Reflectancia` reprova a regra antiga (NDVI > 1).

## Conferência (executada em 19/10)
1. **Processamento real:**
   - 23 pivôs e 2 cenas sem nuvem sobre os pivôs. O cadastro do KML é lido mas não é publicado (veja "Escopo publicado");
   - fica só no diretório temporário da sessão, fora de qualquer repositório.
2. **Reprodutibilidade:** a versão do `s2_l2a.py` do commit `4020a2a7`, rodada de novo sobre o mesmo KML, gerou os 11 arquivos byte a byte iguais aos publicados na v145. A v146 foi gerada pela versão deste commit.
3. **Recusa:** o script recusa gravar com a saída dentro deste repositório.
4. **Build com os dados reais** (árvore `1e927f62`, a do PR #138, mais os dados reais):
   - `paginas_scan` deu 5/5 nas 147 páginas, nos 2 tamanhos e sem erro de JavaScript;
   - nas fotos, o Mapa mostra a imagem real com o NDVI por pixel, a 1440 e 390 px. As fotos não vão ao repositório, porque mostram a fazenda real.
5. **Artefato:**
   - versões 161 a 163 (`1792413975-e91a`), com 147 páginas e 5 arquivos da Lagoa Grande, em 3 lotes;
   - leitura de volta de 7 arquivos (mapa, dados reais e uma página de cada lote): 7/7 iguais ao build por sha256.
   - v146: versão 164 (`1792414809-c42a`), 10 páginas trocadas, leitura de volta 10/10 por sha256; `paginas_scan` 5/5 no build com os dados reais.
6. **Teste sintético:** `python3 -m unittest tools.geo.s2_l2a_test -v` deu 15/15.

## Observações para o proprietário (sem valores aqui)
- **Pivôs:** em 4 dos 23, a área declarada (HECTARE) diverge do círculo desenhado no KML ou falta o círculo. A lista vai ao proprietário no canal dele, não ao repositório.
- **Escopo do mapa real:** a imagem e os pivôs são reais; as O.S. e a safra continuam sendo do cenário de demonstração.

## Fica para depois
- **Mapa de fundo além da margem de 1,5 km:** precisaria de mosaico próprio ou de imagem paga. Fica com o proprietário, junto da cotação de créditos.
- **No software real:** o servidor busca as cenas por organização, a cada passagem do satélite. Entra na passagem para o software real, com homologação e o aceite do proprietário.
