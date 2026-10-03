# Job de produção: atualização diária do AGROFIT e das monografias da ANVISA

Especificação para o sistema real. No protótipo, `atualizar.py` faz o mesmo ciclo à mão (GET condicional, validação, `processar.py`). Em produção isto roda **no servidor, agendado**, nunca em computador pessoal.

## 1. Fontes

| Fonte | URL | Publicação observada (02/10/2026) |
|---|---|---|
| Produtos formulados (MAPA, CC-BY) | `https://dados.agricultura.gov.br/dataset/6c913699-e82e-4da3-a0a1-fb6c431e367f/resource/d30b30d7-e256-484e-9ab8-cd40974e1238/download/agrofitprodutosformulados.csv` | Last-Modified 07:04:54 UTC, ~392 MB |
| Produtos técnicos (MAPA, CC-BY) | `https://dados.agricultura.gov.br/dataset/6c913699-e82e-4da3-a0a1-fb6c431e367f/resource/a200c70b-e025-4a9a-be1b-ec7275d7921f/download/agrofitprodutostecnicos.csv` | Last-Modified 12:30:14 UTC, ~0,7 MB |
| Monografias / LMR (ANVISA) | `https://dados.anvisa.gov.br/dados/TA_MONOGRAFIA_AGROTOXICO.csv` | Last-Modified 18:29:11 UTC, ~2,5 MB, cp1252 |

Os horários vêm de uma única observação. O job grava o `Last-Modified` de cada execução, e a agenda é revista depois de 30 dias de histórico.

O arquivo de formulados traz **só registros ativos** (`SITUACAO = TRUE`). Um cancelamento não aparece como linha: o produto **some** do arquivo. Os dados abertos também não trazem dose, carência, intervalo de reentrada nem grupo IRAC/FRAC/HRAC. Esses campos ficam na curadoria a partir da bula, fora deste job.

## 2. Onde e quando roda

- **Onde:** um agendador gerenciado do ambiente de produção (CronJob do cluster ou agendador da nuvem) dispara um contêiner sem estado. Um único executor por vez, garantido por trava no banco (`pg_try_advisory_lock`). Uma execução concorrente sai sem fazer nada.
- **Quando (UTC):** de hora em hora, entre 07:30 e 23:30. Cada execução faz GET condicional das três fontes. Uma resposta 304 não custa nada, e o processamento só acontece quando o conteúdo muda. Com isso, os formulados entram por volta das 07:30, os técnicos por volta das 13:30 e a ANVISA por volta das 19:30, sem depender de horário fixo.
- **Boa vizinhança:** no máximo uma requisição condicional por fonte por hora, `User-Agent: SafrionPrototipo/1.0 (consulta a dados abertos AGROFIT/MAPA)` (em produção, o nome do produto), sem dado pessoal nos cabeçalhos, respeito a `429`/`503` com `Retry-After`, HTTPS com certificado validado.

## 3. Detecção de mudança

1. **GET condicional:** `If-None-Match` com o ETag salvo e `If-Modified-Since` com o Last-Modified salvo. Uma resposta 304 encerra a fonte.
2. **Hash:** com resposta 200, o job baixa em streaming para um arquivo temporário e calcula o SHA-256. Se o hash for igual ao da última versão processada, só atualiza `verificado_em`, porque o servidor pode trocar o ETag sem mudar o conteúdo.
3. **Diferença semântica:** feita na carga (seção 5), contra a última versão publicada.

## 4. Validação antes de publicar (quarentena)

Uma versão nova só é publicada se passar em todas as checagens abaixo. Se falhar, fica em `quarentena`, a versão anterior continua valendo e a equipe técnica recebe um alerta:

- Tamanho igual ao `Content-Length` e arquivo não vazio. Também há um teto (2 GB) para proteger o disco.
- Cabeçalho e colunas exatamente os esperados. Coluna nova ou renomeada vai para quarentena, não para adivinhação.
- Codificação esperada (UTF-8 nos arquivos do MAPA, cp1252 na ANVISA), com correção dos caracteres de controle C1 e `\x1a`.
- Todas as linhas com o número certo de colunas, e campos de produto iguais em todas as linhas do mesmo registro.
- Comparação com a versão anterior: queda de mais de 5% nos registros ou de mais de 10% nas linhas segura a versão para conferência humana. Arquivo truncado na origem não pode virar uma onda de "registro cancelado".

O conteúdo baixado é dado não confiável: só é lido por um parser de CSV, nada é executado e textos vão escapados para a interface.

## 5. Carga idempotente

Tabelas (nomes indicativos):

- `fonte_versao`: fonte, etag, last_modified, sha256 (único por fonte), bytes, linhas, registros, baixado_em, status (`processando`, `publicada`, `quarentena`, `falhou`).
- `agrofit_produto`: chave `nr_registro`. Guarda marcas, formulação, titular, classes, modo de ação, classes toxicológica e ambiental, orgânico, `ativo`, `primeira_versao`, `ultima_versao_vista`, `hash_campos`.
- `agrofit_produto_ingrediente`, `agrofit_ingrediente` (com grupo químico e código de monografia), `agrofit_cultura`, `agrofit_alvo`.
- `agrofit_uso`: chave `(nr_registro, cultura, alvo)`, com `vigente_desde` e `vigente_ate`.
- `anvisa_lmr`: chave `(monografia, cultura, inicio_vigencia)`. Guarda valor, tipo, autorizado e ato legal.
- `agrofit_evento`: histórico (seção 6).

Regras:

- Tudo de uma versão entra numa **única transação**. A versão só vira `publicada` no commit.
- A gravação é por upsert na chave natural. Uma linha só é alterada quando `hash_campos` muda.
- **Nada é apagado.** Um produto ausente vira `ativo = false`, e um uso retirado recebe `vigente_ate`.
- Reprocessar a mesma versão (mesmo sha256) não gera nenhuma escrita nem evento. Isso é testado.
- Depois do commit, o job gera os arquivos de consulta da página: índice, usos por cultura, usos por produto e LMR, no mesmo formato de `processar.py`. Eles vão para o armazenamento com nome versionado, cache imutável e um ponteiro `atual` trocado por último. Se a geração falhar, o ponteiro continua na versão anterior.

## 6. Histórico por produto

Cada diferença entre versões publicadas grava um `agrofit_evento` com o registro, o tipo, os valores antes e depois (JSON), a `fonte_versao` e a data:

| Tipo | Quando |
|---|---|
| `REGISTRO_NOVO` | registro que não existia |
| `REGISTRO_AUSENTE` | sumiu do arquivo pela 1ª vez (pode ser falha da origem) |
| `REGISTRO_RETIRADO` | ausente em 2 publicações seguidas, ou confirmado na consulta do AGROFIT |
| `REGISTRO_REAPARECEU` | voltou depois de ausente ou retirado |
| `USO_INCLUIDO` / `USO_RETIRADO` | par cultura × alvo entrou ou saiu |
| `CULTURA_RETIRADA` | o produto perdeu todos os usos numa cultura |
| `MUDOU_TOXICOLOGICA` / `MUDOU_AMBIENTAL` | reclassificação |
| `MUDOU_TITULAR` / `MUDOU_MARCA` / `MUDOU_FORMULACAO` / `MUDOU_INGREDIENTE` | dado cadastral |
| `LMR_ALTERADO` / `LMR_REVOGADO` | mudança na monografia para uma cultura |

## 7. Alerta ao agrônomo quando muda um produto que ele usa

"Usa" quer dizer que o produto, ligado ao insumo pelo `nr_registro` gravado no cadastro de insumos, aparece em pelo menos um destes lugares: lote em estoque, plano agronômico vigente, O.S. aberta ou programada, ou receituário emitido nos últimos 12 meses. O destinatário é o agrônomo responsável pela fazenda ou safra. Para cada fazenda, produto e evento sai um só alerta, que aponta para onde o produto é usado (plano, O.S., lote).

| Gravidade | Eventos | O que acontece |
|---|---|---|
| Crítico | `REGISTRO_RETIRADO`, `CULTURA_RETIRADA` ou `USO_RETIRADO` na cultura ou alvo da fazenda | Alerta na hora (no app e no canal escolhido pelo agrônomo). Bloqueia só a emissão de **novo** receituário e a liberação de O.S. com aquele produto naquela cultura, porque usar fora do registro é ilegal. O que já foi executado não muda. |
| Atenção | `REGISTRO_AUSENTE` (antes vai só para a equipe técnica), mudança toxicológica ou ambiental, LMR reduzido, mudança de titular, marca ou formulação | Aviso na ficha do produto e no plano. Entra no resumo diário. Não bloqueia nada. |
| Informativo | `REGISTRO_NOVO` ou `USO_INCLUIDO` para cultura da fazenda | Resumo semanal opcional ("novas opções registradas para mamão"). |

A primeira ausência de um registro não chega ao agrônomo. A equipe técnica confere no AGROFIT e, se a ausência se confirmar ou se repetir na publicação seguinte, sai o alerta crítico.

## 8. Falhas e dados velhos

- **Retentativas:** 3 tentativas por fonte, com espera de 5 s, 20 s e 60 s, respeitando `Retry-After`. Esgotadas as tentativas, a fonte fica como `falhou`, os dados anteriores são mantidos e a próxima hora tenta de novo.
- **Alertas para a equipe técnica**, nunca para o agricultor:
  - falha em 3 execuções seguintes;
  - versão em quarentena;
  - formulados sem verificação bem-sucedida há 36 h;
  - `Last-Modified` dos formulados sem mudar há 7 dias, o que pode indicar que o MAPA parou de publicar;
  - erro na geração dos arquivos de consulta.
- **Na interface:** a consulta sempre mostra "Dados do AGROFIT de DD/MM/AAAA" (o Last-Modified). Se os dados tiverem mais de 3 dias, aparece um aviso discreto. A consulta nunca fica vazia por falha do job.
- **Por execução, o job registra:** duração, status HTTP, bytes, linhas, registros, eventos por tipo e alertas enviados. Uma execução sem nenhuma alteração também é registrada (`inalterado`).

## 9. Retenção

| Item | Guarda |
|---|---|
| CSV bruto de cada versão publicada (comprimido) | 30 dias completos, mais a 1ª versão de cada mês por 5 anos |
| Versões em quarentena | 90 dias |
| `fonte_versao`, `agrofit_evento`, `anvisa_lmr` histórico | Sem expiração: é a trilha de auditoria do que estava registrado quando um receituário foi emitido. Conferir com o jurídico o prazo legal de guarda do receituário. |
| Arquivos de consulta gerados | Últimas 7 versões |
| Logs de execução | 90 dias |

## 10. Testes do job

- **Unitários:** separação de ingredientes `a (grupo) (480 g/L) + b (…)`, normalização de classes, modo de ação, cultura e alvo, e casamento de ingrediente com monografia (sal ou éster, grafia em inglês, sinônimos).
- **Integração com CSV de fixture:** a versão A seguida da versão B gera exatamente os eventos esperados. Reprocessar B gera zero escritas. Um arquivo truncado vai para quarentena. Um cabeçalho alterado vai para quarentena. Um produto ausente uma vez gera `REGISTRO_AUSENTE` sem alertar o agrônomo, e ausente duas vezes gera `REGISTRO_RETIRADO` com alerta crítico.
- **Contrato:** o job confere as colunas da fonte a cada execução (seção 4).

## 11. Fora deste job (depois)

- **API AGROFIT (Embrapa AgroAPI):** consulta pontual e dados de bula, adiados por decisão do proprietário.
- **Dose, carência, reentrada e grupo IRAC/FRAC/HRAC:** curadoria a partir da bula, com fonte e data por campo.

## 12. O que a página AG-07 lê (publicar ao lado de AG-07.dc.html)

`agrofit_meta.json`, `agrofit_indice.json`, `agrofit_lmr.json` e `agrofit_usos_cultura_0.json` … `agrofit_usos_cultura_<n-1>.json`
(`n` = `contagens.fatias_cultura` da meta). A página lê a meta sem cache e os demais com `?v=<versao>`; se um arquivo vier com
outra `versao`, tenta de novo uma vez e depois mostra erro com "Tentar de novo". Por isso a publicação troca primeiro os arquivos de
dados e por último a meta. `agrofit_usos_produto_*.json` e `agrofit_tecnicos.json` não são lidos pela página (ficam para a API).
O selo do cabeçalho fica amarelo ("desatualizada") quando o `Last-Modified` dos formulados passa de 7 dias, o mesmo limite da seção 8.

## 13. Modo de ação para a rotação (IRAC/FRAC/HRAC)

O AGROFIT publica só o grupo químico, e o rótulo varia dentro do mesmo modo de ação (por exemplo, "triazol", "Triazolinthione" e
"imidazol" são todos FRAC 3). A rotação da AG-07 compara o código de `agrofit_dados.GRUPO_RESIST`, que cobre todos os ingredientes
químicos do arquivo de 02/10/2026. Quando o job trouxer um ingrediente químico novo, o build da AG-07 imprime
`AVISO AG-07: N ingrediente(s) químico(s) sem código…` (função `lacunas_resist`). Enquanto isso, a rotação desse ingrediente usa o
grupo químico do AGROFIT. Para resolver, inclua o nome em `GRUPO_RESIST_NOVOS` com o código da classificação pública ou, se ele não
tiver grupo (óleo, extrato, modo de ação desconhecido), em `SEM_CODIGO_RESIST`. O `agrofit_test.py` (verificação 10) falha se algum
alternativo da rotação repetir o modo de ação do produto aberto.
