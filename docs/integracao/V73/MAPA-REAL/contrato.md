# MAPA-REAL F2 — contrato do pacote privado

19/10/2026 · proposta Codex para revisão/integração Claude.
Base documental recuperada: `d022c74524a7bcb349c05dd25cc13c2ec9cb472d`. Este arquivo não existe nessa árvore. Divisão: PR47/6266180436, corrigida6266211728 e confirmada6266706310. Somente este documento pertence ao Codex nesta entrega; RX1/PR137 já entregue permanece em revisão. Implementação `tools/geo/s2_l2a.py`, teste sintético e mapa `areas/inicio.py` continuam Claude. Não altera PRD, proteção ou autoria desses arquivos.

## Decisão e alcance

O recibo Claude6266706310 transcreve a escolha de Adrianus: **“Exceção só no artefato privado”**. A opção apresentada incluía envio do KML da Lagoa Grande à sessão existente do Claude, processamento nessa nuvem e imagem/perímetros derivados somente no artefato privado, fora do GitHub e sem custo. Não autorizou imagem submétrica paga, nova conta, assinatura ou exposição pública.

Codex leu esse recibo, mas não conferiu a resposta original na interface: o Mac estava bloqueado. Não afirmar verificação direta nem usar este documento como autorização genérica para outros dados/destinos. O operador que recebeu a decisão original deve vinculá-la à entrega e manter exatamente o alcance informado, sem pedir novamente a mesma decisão já recebida.

A exceção é específica: KML dessa fazenda e pacote derivado de imagem Sentinel-2 L2A, índices C4 e perímetros. Não estende a publicação a cadastros pessoais, documentos, outorgas, anotações internas ou outras propriedades presentes no KML. Extrair apenas a geometria e identificadores mínimos necessários; não transportar descrições/ExtendedData indiscriminadamente. Dados reais e derivados ficam fora de commits, PRs, comentários, logs, capturas de QA compartilhadas, fixtures e testes. O KML original não integra o pacote publicado.

Antes de inserir dado real, confirmar o controle de acesso efetivo do artefato e de seus arquivos: a URL difícil de descobrir ou a palavra “privado” não bastam. Acesso anônimo, link público ou configuração ambígua não satisfazem a escolha; preservar o pacote e a demonstração sintética, com pendência explícita, sem mudar compartilhamento ou proteções. Nenhum convite novo está autorizado aqui.

## Produto e estados

MapLibre permanece o renderizador. Esta entrega usa pacote pré-processado compatível com as restrições já observadas do artefato; não comprova conector online, atualização contínua ou servidor independente do Mac. A rotina portátil pode rodar localmente ou no executor autorizado; a execução remota precisa de recibo real. Não adicionar outro menu, editor de talhões ou fonte paralela de O.S.

| Contexto existente | Estado | Próximo passo |
|---|---|---|
| Mapa / fazenda e talhão | Demonstração sintética | Explorar a demonstração, com rótulo permanente |
| Mapa / pacote recebido | Em processamento | Mostrar andamento real; preservar a versão anterior |
| Mapa / pacote real conferido | Cena disponível | Abrir talhão, qualidade e índices da mesma cena |
| Talhão / índice | Sem dado ou cobertura parcial | Ver qualidade; não pintar ausência como índice baixo |
| Mapa / falha de busca ou pacote inválido | Não atualizado | Tentar novamente quando a causa estiver resolvida; manter a última cena identificada |
| Mapa / acesso privado não demonstrado | Publicação pendente | Conferir acesso, sem inserir dados reais |

O seletor e o painel existentes preservam fazenda, safra, talhão, camada, zoom e foco. Uma ação primária pelo contexto ativo. Rótulo mínimo de cena: fonte, data de aquisição, qualidade da área e resolução do índice; data de processamento é separada. “Nuvem x%” identifica seu denominador (talhão/fazenda/cena); percentual global da cena não substitui a cobertura válida por talhão e índice.

## Contrato analítico e compatibilidade

Fonte única: C4, PRD61.4.1 e LABMAP-13..16, sem duplicar fórmulas nem promover limites de demonstração a homologados. Recorte C4 recuperado em `edits/indices_mapa_fase1.json`, SHA256 `ab5071b53f3753055e74eb6ffcd0d3e2bf92f924fb19a8b08ffa6d5f58dd50fd` (referência do registro existente, não arquivo novo exigido).

- Os cinco índices são NDVI, NDRE, EVI, SAVI e NDMI; NDWI legado sem fórmula não é equivalente. Resolução efetiva, bandas, escala/deslocamento por metadado, grade e versão de máscara/processamento seguem C4. NDRE/NDMI reamostrados não adquirem detalhe nativo de10m.
- Máscara, nodata, denominador zero e resultado inválido não viram zero nem sofrem clamp silencioso. Cobertura e estatística usam a base declarada por índice/talhão. Classes exigem limites homologados/versionados; sem eles, valor contínuo e legenda. Cor/índice não gera diagnóstico, compra ou prescrição.
- Identificar coleção/cena/assets e aquisição efetivamente usados. Não fixar o nome da coleção apenas pelo relato de HTTP200; conferir o metadado do asset e registrar a versão do processamento. Atribuição segue a fonte realmente utilizada.
- O fundo de contexto e o raster analítico são distinguidos. Mosaico com mais de uma aquisição identifica as datas; não apresentar uma única data fictícia. A imagem de contexto não autoriza consultar valores analíticos fora do recorte validado.
- Compatibilidade precisa ser comprovada por geração e consumo sintéticos no formato vigente. Em `dados_lagoa_fonte.py` da base, o modo real exige **a pasta com `lagoa_s2_resumo.json` e as constantes de `dados_lagoa_kml`**; gerar somente um JSON/imagem não completa a integração. Definir a montagem autorizada sem alterar esse leitor silenciosamente. Não fabricar campos de água/outorga/cadastros ausentes para satisfazer imports.
- `SAFRION_DADOS=sintetico` continua forçando a demonstração. Pacote incompleto/incompatível não mistura perímetros reais com índices sintéticos sob rótulo real. Se houver fallback, a troca e sua origem são explícitas. Montagem e publicação devem preservar a versão válida anterior quando falharem.

## Aceite e provas da entrega

| Verificação | Evidência necessária |
|---|---|
| Privacidade e escopo | Recibo da decisão original, destino e acesso efetivo conferidos; nenhum dado real no repositório/logs/provas públicas; perímetros e imagem limitados ao pacote autorizado |
| Cálculo | LABMAP-13 por índice, com oráculo independente, metadados e casos inválidos em matrizes sintéticas; não apenas conferir a presença dos cinco nomes |
| Cena e qualidade | LABMAP-14/15: recorte, máscara, cobertura, resolução, aquisição/processamento e idempotência; resultado real inspecionado somente no destino autorizado |
| Montagem | Pacote sintético completo consumido pelo leitor vigente; incompleto, modo forçado sintético e troca de versão sem mistura; nenhuma constante real em fixture |
| Tela | LABMAP-16; fonte/qualidade/legenda coerentes com o pixel, ausência explícita, filtro e seleção preservados; teclado e390px proporcionais ao delta |
| Publicação | SHA de código, versão do artefato e recibo de readback; separar código local, push, revisão, integração e pacote publicado |
| Custo e execução | Sem nova contratação/recarga/API paga; acesso público ao catálogo não prova custo total zero. Se a rota exigir cobrança, interromper essa rota e apresentar preço/limite antes de executar; não mudar o orçamento existente |

Os itens acima são critérios, **não testes executados**. Código e testes sintéticos podem ser revisados no GitHub; a inspeção do pacote real ocorre somente no ambiente autorizado. Um recibo sanitizado identifica versão e resultado sem coordenadas, nomes privados, conteúdo de KML, paths locais ou URLs que revelem o recorte.

Aplicado: mapa vigente, C4 como fonte única, origens explícitas, pacote mínimo e recuperação. Fora: imagem submétrica, novo provedor pago, publicação pública, produção, atualização automática e outros dados reais. Cortado: troca de biblioteca sem necessidade, cópia de fórmulas, novo menu e promessa de “sem custo” baseada só em HTTP200.

Estado desta entrega: contrato pronto para crítica Claude; pipeline, integração visual, privacidade do destino e publicação real ainda dependem das provas respectivas. Não conclui MAPA-FROTA, MAPA-REAL completo nem o protótipo inteiro.
