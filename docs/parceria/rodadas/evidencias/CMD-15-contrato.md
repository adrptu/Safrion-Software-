# Contrato F1/CMD-15: recebimento de insumos por documento e inspeção

**Versão 3.16 (30/09), com os ajustes do Codex de 01:43Z, 01:45Z, 02:46Z, 03:17Z, 03:48Z, 05:52Z, 06:24Z, 06:29Z, 06:50Z, 07:46Z, 07:52Z (CX-UI01, CX-UI03), 10:22Z (p95 no fechamento) e 11:19Z (espera controlada) e 12:07Z (trava do efeito).** As versões anteriores ficam ao lado (v1 6e730024…, v2 8b0a53a2…, v3 205ad36e…, v3.1 b45fc372…, v3.3 9a244564…, v3.4 1f357769…, v3.5 feaca462…, v3.6 a170f747…, v3.7 d359406e…, v3.8 afc701e6…, v3.9 edc0cabd…, v3.10 6a7a8318…, v3.11 6ffb359f…, v3.12 75910766…, v3.13 1ad9c368…, v3.14 b254594f…, v3.15 bf4d9882…). A v3.17 propõe a §9.3 (prazo para a trava do efeito), só proposta. A v3.16 propõe a §9.2 (espera controlada na aquisição de conexão), sem editar produto antes do ACK. A v3.15 propõe a §9.1 (ensaio de desempenho delimitado), sem mudar comportamento. A v3.14 encaixa o aviso antecipado na tela (§6.3). A v3.13 cria a §6.3 (aviso antecipado de duplicidade, só leitura e rota). A v3.12 preserva o rascunho quando uma intenção se resolve sem confirmar (CX-UI04, §6.2). A v3.11 corrige a rejeição depois de repetir (CX-R02) e a conexão que cai com o cliente emprestado (CX-R03), na §6. A v3.10 corrige a tela: intenção por chave própria entre abas (§6.2) e todas as ocorrências no detalhe (§7.1). A v3.8 detalhou a repetição por deadlock (§6) e a escala do valor unitário (§6.2); a v3.9 fecha a garantia de prazo (§6). A v3.5 acrescentou a §6.1 (leitura e consulta por chave) e a v3.6, a §6.2 (borda HTTP). A v3.7 acrescenta à §6.2 a regra da incerteza e cria a §7.1 (a tela, por entidade e estado); ajusta a §8.

Base de código: main `6882918`; `packages` e `apps/web/src` iguais aos de `38b4be3`. V11 é o PRD v3.11; "plano" é `plano-execucao-safrion.md` (29/09). Caminhos relativos à raiz. "Decisão técnica" marca o que não vem de fonte.

## 0. Fonte que prevalece
- **PRD:** a fonte canônica vigente é a v3.9 da main. Este contrato usa como referência candidata a v3.11 (`1615a12`, branch `docs/prd-produto-fixo`, fora da main), sem declará-la adotada; os IDs que só existem na v3.11 são candidatos até a decisão ser registrada na fonte canônica, depois da revisão. O núcleo é igual ao da v3.9: SU-06 (V11:1232-1244), FO-18 (V11:2336), RF-SUP-007 (V11:2597), CMD-15 (V11:2799), AC-14 (V11:4842) e DEMO-02 (V11:4778).
- **A v3.11 acrescenta:** IDEM-03/09/14/16 (V11:12637, 12648, 12658, 12660), a leitura transacional do CMD-15 (V11:13175), AC-73/74/84/87 (V11:13561-13582), SUBST-07/14 (V11:6966, 6973) e FLUXUX-16/18 (V11:9643, 9645).
- **Se a v3.9 prevalecer:** a §2, a §6 e a §9 passam a citar R-006-requisitos.md:78 (v3.10 em revisão), e caem SUBST-07/14 e FLUXUX-16/18. O Codex registra a adoção em `docs/DECISIONS.md`.
- **Escopo:** segue o plano de 29/09, mais novo que o R-006 de 27/09. Compra integrada ao planejamento é Fase 1 comercial (plano:31, 46, 124); financeiro é Fase 3 (plano:37); "E2" é onda do PRD, não fase. Onde plano e R-006 divergirem, o Codex decide e registra em DECISIONS.md.

## 1. Entidades e comandos
**Já existe:** as tabelas `product`, `packaging_conversion`, `lot`, `stock_movement`, `intent_record`, `audit_log` e `outbox` (0001_fundacao.sql:79-274); no domínio, as situações inspeção × bloqueio (saldo.ts:24-32), a mudança de uma dimensão (saldo.ts:243-256) e a conversão de embalagem para a base (unidades.ts:147-163); o comando `estoque.registrar-entrada`, só do almoxarife (matriz.ts:4-16).

**Falta** (migração 0007):
- `counterparty`: contraparte mínima com UNIQUE (org, identificação), que não duplica identidade (CD-05, V11:1760), com carga fictícia.
- `receipt_document`: emitente, tipo, série, número, emissão, data do recebimento (texto civil), fazenda, referência de pedido opcional, status, versão, autor e chave da intenção.
- `receipt_line`: número 1..N, produto, lote, validade (data ou "não se aplica", §5), local, quantidade do documento, unidade ou embalagem com conversão (id e versão), parcelas (apto, quarentena, bloqueado, recusado), motivo, responsável e prazo da decisão da quarentena, referência opcional da linha do pedido e valor unitário opcional.
- `receipt_occurrence`: ocorrência de chegada ligada à linha, quando chega produto diferente do documento (§5). Guarda o produto real (cadastrado, ou descrito se não houver cadastro), a quantidade e a unidade como foram contadas, o destino físico (retido para decisão, ou devolvido na entrega), o responsável, o prazo e o status. Não é estoque e não gera movimento.
- Validade por produto: `product.expiry_policy` (`controla` | `nao_se_aplica`, padrão `controla`). O lote grava a própria `expiry_applies`, fixada na criação, com CHECK (expiry_applies = (expiry_date IS NOT NULL)) e `lot.expiry_date` anulável. O lote não aponta para a política atual do produto: mudar a política depois não invalida lote antigo nem o histórico.
- Lote por produto: `product.lot_policy` (`informado` | `por_documento`, padrão `informado`) e `lot.kind` (`fabricante` | `agrupamento_interno`, padrão `fabricante`). Produto `por_documento` (diesel a granel) recebe lote interno, com código estável `DOC:<id do documento>` (o id é UUID persistido do documento, §6) e kind `agrupamento_interno`. A tela mostra a referência legível à parte ("Granel · NF <série>/<número> · <emitente>") e nunca chama esse lote de lote do fabricante. Duas NF de emitentes diferentes com o mesmo número ficam em lotes diferentes; o reenvio da mesma intenção reusa o mesmo documento e, portanto, o mesmo lote. Lote de fabricante com código parecido (inclusive anterior à 0007) continua fabricante: o banco exige DOC:<uuid> só para o interno, e o efeito recusa colisão de código com lote de fabricante, sem reusar nem reclassificar (CMD15-CX03).
- `stock_movement.receipt_line_id`, anulável, com FK composta por organização: liga cada movimento à linha que o gerou (V11:8775) e servirá ao estorno.
- **A inspeção não vira entidade.** É a parcela em quarentena, com responsável e prazo da decisão (data civil) enquanto aberta (V11:1244, 9413), mais o comando de liberação, com autor e motivo na auditoria. O FO-15 é de produção (V11:2333).

| commandType | Origem no PRD | Alvo | Incremento |
|---|---|---|---|
| `estoque.receber-documento` | CMD-15 (V11:2799) | `receipt_document`, versão esperada 0 | 1 |
| Consulta por chave (GET, sem efeito) | IDEM-09 (V11:12648) | — | 1 |
| `estoque.liberar-qualidade` | Botão da SU-06 (V11:1234). Sem CMD próprio: o CMD-24 é de produção (V11:2808) | `lot` + versão | 2 |
| `estoque.segregar` | Botão da SU-06 (V11:1234) | `lot` + versão | 2 |
| `estoque.estornar-documento` | ENG-026 (V11:5375) | `receipt_document` + versão | 3 |

**Incremento aditivo:** `estoque.registrar-entrada`, o formulário atual e os testes aprovados (B2, HML-ISO) ficam como estão. A retirada é outra mudança, só depois de o recebimento por documento ser aceito como substituto (o matriz.ts:4 já anuncia essa troca). Nenhum comando novo além de `estoque.receber-documento` no incremento 1.

## 2. Estados
- **Rascunho só no navegador** (IDEM-03, V11:12637; FORM-04, V11:2446), no padrão de `apps/web/src/estoque/rascunho.ts:25-87`, mas em `localStorage` por usuário e organização, limpo ao confirmar e ao sair. O `sessionStorage` atual (:30-32) perde até 50 linhas quando a aba fecha. Isso muda o estado Rascunho do R-006-requisitos.md:27; o Codex registra em DECISIONS.md.
- **Documento:** nasce `Confirmado`, na versão 1, e passa a `Estornado` no incremento 3. Não uso "Recebido", que já é palavra do lote (estado.ts:26). **Lote:** o estado é derivado do saldo (estado.ts:20-32; V11:2768). Liberar leva quarentena a liberado uma única vez (V11:9413).
- **Dimensões próprias** (decisão técnica):
  - inspeção: Pendente enquanto houver quarentena, depois Concluída;
  - divergência: Nenhuma ou Aberta. Aberta vira pendência com responsável e próxima ação "Ver divergência", que abre o detalhe existente. Não há comando de encerrar no incremento 1: a decisão vem com Resolver diferença (§7);
  - ocorrência de chegada: Aberta, com responsável e prazo, e a mesma próxima ação "Ver divergência";
  - financeiro: Fase 3.
- **Parcela → situação do movimento:** apto → `liberado_livre`; quarentena → `quarentena_livre`; bloqueado, com motivo → `liberado_bloqueado`; recusado, com motivo → nenhum movimento. Parcela zero não gera movimento nem chama a conversão. O servidor recusa `quarentena_bloqueado`; hoje só a tela limita (estado.ts:49).
- **Quem executa:** o almoxarife recebe; nos incrementos 2 e 3, também libera, segrega e estorna (PER-18, R-006-requisitos.md:16). O papel qualidade da SU-06 (V11:1228) entra quando existir. O gerente só lê (matriz.ts:15-16).

## 3. Origem e fornecedor sem duplicata
- **Identidade da origem:** (org, emitente_id, tipo, série, número), com índice único parcial `WHERE status = 'confirmado'` (ENG-024, V11:5373). Assim a NF corrigida pode entrar de novo depois do estorno. Tipo `nfe` ou `outro`; série NOT NULL (`""` se não houver). Série e número são normalizados antes da chave e do hash: trim, NFC e sem zeros à esquerda quando numéricos.
- **Mesma chave, conteúdo equivalente:** devolve o recibo original (db/src/comando.ts:328-343; IDEM-14). **Outra chave, mesma origem** (NF relançada): 422 `DOCUMENTO_JA_RECEBIDO`, sem movimento; a tela abre o documento existente por `documentoPorOrigem`. **Concorrência com chaves diferentes:** o INSERT do cabeçalho é o primeiro passo do efeito. O perdedor espera o índice, recebe 23505 no savepoint e sai com o mesmo 422, nunca 500.
- **Erro de chave pelo nome da constraint:** só o índice de origem vira `DOCUMENTO_JA_RECEBIDO`. Colisão de PK vira `ALVO_INVALIDO`, com a resposta de inexistente, porque o id é global e a restrição não passa pelo RLS (0001:105, 122, 173). Produto, conversão, lote e local são validados por SELECT antes do INSERT. A FK composta é a última barreira, e um 23503 que ainda escape também vira `ALVO_INVALIDO`. Hoje só ConflitoVersao, RejeicaoNegocio e ErroDominio viram registro; o resto sai como 500 (comando.ts:389-404).
- **Pedido não é identidade** (ponto do Codex, 00:15:32Z): várias NF podem citar o mesmo `external_order_ref`, porque entrega parcial é legítima. A identidade é a da NF inteira, não a do pedido nem a da linha. Correção de NF confirmada = estorno (incremento 3) e novo documento; nunca editar o confirmado.
- **Aviso antecipado:** a "Duplicidade" do FO-18 é consultada antes de confirmar, mas não substitui o índice. **O documento não substitui a conferência** (V11:2597): as parcelas vêm do que foi conferido.

## 4. Vínculos
- **Fazenda:** fica no cabeçalho. O local de cada linha tem de ser dessa fazenda: a 0007 cria UNIQUE (org, farm_id, id) em `stock_location`, e a linha usa FK composta.
- **Lote:** identificado por (produto, código) (0001:115). A 0007 cria UNIQUE (org, id, product_id) em `lot`, e a linha usa FK composta para garantir que o lote seja do produto da linha. Lote existente com validade diferente: 422 `VALIDADE_DIFERENTE_DO_LOTE`; a validade não é corrigível (0001:301). Sem versão esperada por lote em `data`: a entrada não decide pelo saldo, só serializa (§6).
- **Pedido:** compras é onda E2 no PRD (V11:4917), mas o recorte da etapa 10 é Fase 1 comercial (plano:46, 124). Aqui ficam `external_order_ref` no cabeçalho e `external_order_line_ref` na linha, opcionais, com sistema de origem (V11:4569, 8764, 8775). A falta de pedido aparece explícita na tela e em `pending`. No recorte da etapa 10 a referência vira FK, sem migrar movimento. **Plano e safra** chegam pelo pedido (FL-10, V11:10879; V11:10597); até lá ficam na pendência "Sem pedido", sem ser omitidos.
- **Custo:** valor unitário opcional por unidade do documento, em BRL, com escala 8 (decimal.ts:24). Ausente é NULL, não zero (RN-032, V11:239). A parcela recusada não gera movimento nem custo. Sem valoração neste incremento (decisão técnica; o custo virá do consumo valorizado, plano:78).
- **Mapa:** a interação no mapa é aceite de cada entrega da Fase 1 (plano:31). A cobertura estoque → área vem dos vínculos de demanda, reserva e O.S. (plano:95). O recebimento guarda fazenda e local, e o mapa lê o mesmo saldo (V11:12481). Sem geometria até a etapa 03.

## 5. Quantidades
- **Na linha:** a quantidade do documento e as 4 parcelas, na mesma unidade: embalagem com contagem inteira (unidades.ts:147-163) ou unidade de medida (unidades.ts:71-87). Conferido = apto + quarentena + bloqueado + recusado; físico = apto + quarentena + bloqueado. O recusado não entra no físico nem quita entrega (V11:4295).
- **Divergência aberta** quando o conferido difere do documento (falta ou sobra), ou quando bloqueado ou recusado é maior que zero. Motivos em lista fechada: avaria, validade, produto_diferente, falta, sobra, outro (com texto). Quarentena sozinha não é divergência; é inspeção pendente.
- **Produto diferente** (SUBST-14, V11:6973): o que chegou no lugar do produto do documento é uma ocorrência de chegada, não estoque aceito.
  - A linha do produto do documento fica com o conferido dele (em geral 0, divergência "falta").
  - A `receipt_occurrence` guarda o produto real, a quantidade e a unidade como foram contadas e o destino físico, com responsável e prazo.
  - Nada entra no físico nem no saldo e nada é liberado automaticamente. O produto real nunca é convertido pelo cadastro do produto do documento (A não serve para B).
  - Para o produto real virar estoque é preciso decisão explícita posterior, com lote, unidade e conversão dele (Resolver diferença, §7). A SUBST-07 (V11:6966) trata de pedido e item fixo, que a F1 ainda não tem; passa a valer com o recorte da etapa 10.
- **Validade:** data civil, ou "não se aplica" (combustível, por exemplo). Nunca data fictícia (RN-032, V11:239). Precedência:
  - **lote existente:** vale a `expiry_applies` congelada do lote, mesmo que `product.expiry_policy` tenha mudado depois. Lote com validade exige a mesma data (senão 422 `VALIDADE_DIFERENTE_DO_LOTE`); lote sem validade recusa data (422 `VALIDADE_NAO_SE_APLICA`);
  - **lote novo:** vale a política vigente do produto no recebimento. `controla` sem data dá 422 `VALIDADE_OBRIGATORIA`; `nao_se_aplica` com data dá 422 `VALIDADE_NAO_SE_APLICA`.
- **Vencido e FEFO:** lote sem validade nunca vence e não entra no saldo vencido. Na ordem FEFO, fica fora da ordenação por vencimento, mas continua elegível: vem depois dos lotes com validade, em ordem determinística pela primeira entrada (recorded_at do primeiro movimento) e depois pelo id do lote. Quarentena e bloqueio continuam fora do utilizável, com ou sem validade.
- **Conversão:** a 0007 cria UNIQUE (org, id, product_id, version) em `packaging_conversion` e FK composta na linha (hoje só o id é conferido, 0001:156). O movimento passa a gravar `conversion_id`/`version`, hoje vazios (estoque.ts:214-217).
- **Unidade da linha:** unidade de medida da mesma dimensão do produto, conferida antes de qualquer fato, gere ou não movimento (UNIDADE_INCOMPATIVEL; CMD15-CX05).
- **Escala:** na base, maior que zero, até 6 casas, `un` só inteiro e abaixo de 1e15 (saldo.ts:95, 142-163). Fora disso, 422 `QUANTIDADE_INVALIDA`, o código do domínio (saldo.ts:144-148).
- **Exemplos:** 3 galões de 5 L (conversão v1, fator 5) dão 15 L, e o movimento grava o original "3 galão 5 L", a base "15 L" e a conversão v1. NF-TESTE-002: 2 galões do lote F26-03, 1 apto e 1 bloqueado por avaria, geram 2 movimentos no mesmo lote.

## 6. Reenvio, conflito, RLS, auditoria e atomicidade
- **Envelope sem mudança:** `executarComando` (db/src/comando.ts:285-451). O id do documento é um UUID gerado no cliente ao confirmar e guardado com a chave (decisão técnica).
- **Consulta sem efeito** (IDEM-09, V11:12648): um GET por (commandType, chave), com a organização da sessão, devolve o recibo quando a intenção está **registrada** e visível. Registrada = resultado terminal gravado por COMMIT, qualquer que seja: `confirmed`, `rejected` ou `version_conflict`. "Confirmado" fica reservado para `outcome = confirmed`. A resposta perdida de uma rejeição também precisa ser recuperada (Codex 05:52Z). Caso contrário, responde "recibo ainda não localizado". Nunca responde "não recebido" nem "em processamento": o `processing` fica dentro da transação que o insere e não é visível antes do COMMIT (0001:177-178). A tela preserva chave e conteúdo e oferece reenviar exatamente os mesmos, o que é idempotente. O formulário atual continua como está (RegistrarEntrada.tsx:144-145).
- **Hash:** a rota normaliza `data` antes do envelope, com decimais sem zero à direita e linhas ordenadas pelo número. Isso resolve "10" × "10.0", que hoje caem em `IDEMPOTENCY_KEY_REUSED` (canonico.ts:17-18; decimal.ts:26 aceita os dois).
- **Numeração e versão:**
  - linhas 1..N; movimentos 1..M em `intent_item`, contados na intenção inteira (0001:146), cada um com `receipt_line_id`;
  - cada lote ganha uma versão por comando; movimentos do mesmo lote dividem a `lot_version` e têm `intent_item` diferentes (0001:147-148);
  - efeito novo `receberDocumento`, sem chamar `registrarMovimento` em laço (estoque.ts:171-238).
- **Travas em dois passos:** (1) inserir ou obter os lotes em ordem de (product_id, code), com INSERT … ON CONFLICT DO NOTHING; (2) SELECT … FOR UPDATE em ordem de id, antes dos movimentos. A ordem por id sozinha não ordena lotes novos, cujo id é aleatório.
- **Deadlock (40P01) com orçamento:** a transação inteira, com a mesma chave e o mesmo conteúdo, é repetida no máximo 2 vezes (3 tentativas), com pausa curta crescente (50 ms e 150 ms) e teto total de 2 s. Esgotado o orçamento, a resposta é a falha transitória que já existe (`FALHA_TRANSITORIA`, 503, `resultadoIncerto: false`, porque o ROLLBACK veio antes do COMMIT), com a orientação de repetir com a mesma chave e o mesmo conteúdo. Nenhum efeito parcial fica e nenhuma mensagem do banco vai ao cliente (comando.ts:455-469). O teto de 2 s é prazo com cancelamento: ao estourar, a tentativa em curso é cancelada e revertida, e o ROLLBACK precisa ser confirmado. `resultadoIncerto: false` só com ROLLBACK comprovado. Timeout de conexão, COMMIT sem resposta ou ROLLBACK que falhou dão `resultadoIncerto: true`, como o envelope já distingue (commitEnviado). A chave protege o efeito; ela não autoriza repetição sem limite.
  - **Como (v3.9, Codex 07:52Z):**
    - só o erro do próprio PostgreSQL (`DatabaseError` com `code = '40P01'`) repete, e só com ROLLBACK confirmado e sem COMMIT enviado. Qualquer outro SQLSTATE (57014, 23514, 55P03…), um `code` que não veio do banco ou falha de conexão não repete;
    - a repetição usa a mesma intenção (chave, conteúdo, ator e alvo) e o mesmo hash;
    - o prazo conta do início do comando, e a pausa só acontece se couber antes dele.
  - **Garantia exata:**
    - **(a)** Nenhuma tentativa nova começa, nem pausa, se não couber em 2 s desde o início.
    - **(b)** Nas tentativas repetidas, todo comando SQL (os do envelope e os do efeito) passa por um invólucro do cliente:
      - antes de cada um, o prazo é conferido e, depois dele, nenhum comando começa;
      - cada comando recebe `SET LOCAL statement_timeout` com o que falta, para o servidor cortá-lo no prazo (57014);
      - o COMMIT só sai com prazo restante;
      - o ROLLBACK usa sempre o cliente cru.
    - **(c)** A resposta sai até max(duração da 1ª tentativa, 2 s) mais o ROLLBACK e o custo local.
    - **(d)** Nenhum efeito tardio: depois do prazo, o COMMIT nunca é enviado.
  - **Ajuste de escopo explícito:** o teto é da repetição, não de todo comando. A primeira tentativa segue sem prazo novo, como hoje: esperas de chave (`esperaChaveMs`) e comandos longos já aceitos não mudam. Pôr o teto também na primeira tentativa é outra decisão.
  - **ROLLBACK que falha** dá `resultadoIncerto: true` (antes, só o COMMIT enviado dava) e nunca repete.
  - **Conexão que cai com o cliente emprestado** (v3.11, CX-R03): o pg emite 'error' no cliente, e sem ouvinte o processo inteiro cai. O envelope e o `emOrganizacao` ouvem durante o empréstimo; o erro ouvido retira a conexão do pool (`release(erro)`), e a falha chega a quem chamou pela consulta rejeitada. Nunca é engolida.
  - **Rejeição depois de repetir** (v3.11, CX-R02): o `ROLLBACK TO SAVEPOINT efeito` usa o cliente cru, como o ROLLBACK. Numa transação abortada pelo erro que virou rejeição (23505 da origem, por exemplo), nenhum SET cabe antes dele. O prazo volta a ser conferido no comando seguinte e antes do COMMIT.
  - **Log:** `tentativas`, junto com os códigos que já existem.
- **Conflito de versão:** só ocorre se o documento-alvo já existir com versão diferente de 0; devolve 409 com a versão atual (comando.ts:390-394).
- **Onde validar:** fora do efeito, 400 sem gravar nada: forma, somas, listas fechadas e número de linhas (resposta.ts:36-40). Dentro do efeito, 422 registrado: origem duplicada, validade, conversão, lote, fazenda, escala e produto (comando.ts:399-401).
- **Recibo:** `confirmed` mesmo com recusa, divergência ou ocorrência. `pending`: "Inspeção pendente: linha N, <responsável> até <data>", "Divergência aberta: linha N, <quem registrou o recebimento>" (responsável contextual verificável pela sessão, sem campo manual a mais), "Produto divergente retido: linha N, <responsável> até <data>" e "Sem pedido". Responsável de inspeção e de ocorrência é pessoa ATIVA da própria organização (RESPONSAVEL_NAO_ENCONTRADO; FK composta com app_user na 0007; CMD15-CX04). `nextAction` só com ação que existe no incremento 1:
  - "Ver inspeção pendente" (abre o detalhe do documento) se houver quarentena;
  - senão "Ver divergência" se houver divergência ou ocorrência;
  - senão "Receber documento".
  Liberar entra no incremento 2.
- **Tudo ou nada** (IDEM-16): cabeçalho, linhas, lotes novos, movimentos, versões, outbox, recibo e auditoria numa só transação. Uma linha inválida rejeita o documento inteiro. Outbox: `estoque.recebimento_confirmado` v1, mais um `estoque.movimento_registrado` por lote (0001:272).
- **RLS:**
  - as 4 tabelas novas (`counterparty`, `receipt_document`, `receipt_line`, `receipt_occurrence`) com ENABLE + FORCE e a política `isolamento` (0001:278-293), com FKs compostas por organização;
  - `app_runtime` só com SELECT e INSERT; o incremento 3 precisará de UPDATE de status e versão no documento;
  - id de outra organização recebe a resposta de inexistente (FLUXUX-18).
- **Auditoria:** uma linha por comando, com autor e correlação (comando.ts:430-449; NFR-04). before/after trazem, por lote afetado, versão, físico, utilizável, quarentena, bloqueado e vencido na unidade-base, na data civil do recebimento; o after traz também as linhas (id, número, motivo). O motivo da auditoria lista as linhas divergentes ("linha N: motivo (texto)") (CMD15-CX06). **Limites:** até 50 linhas por documento e corpo de 64 KiB só para este comando (rotas/comandos.ts:27-28).

## 6.1 Leitura do documento e consulta por chave (só banco; rota e tela na etapa seguinte)
Tudo roda dentro de `emOrganizacao` (sessão + RLS, como `listarLotes`), no papel app_runtime, sem gravar nada: nenhuma intenção, auditoria, outbox ou versão. Identificador fora do formato devolve vazio ou null, nunca erro do banco. Outra organização é indistinguível de inexistente. As quantidades são texto decimal, como gravadas; as datas civis são AAAA-MM-DD; a validade ausente é `null` explícito, nunca data fictícia.

- **`consultarIntencao(c, { commandType, idempotencyKey, actorId }) → Recibo | null`** (comando.ts, aditivo; mesma projeção `COLUNAS_RECIBO` e mesmo `recibo()` do envelope, com `alreadyReceived: true`).
  - Devolve só o que foi registrado; `processing` nunca aparece, porque só existe dentro da transação que o insere.
  - `null` quer dizer "recibo ainda não localizado", nunca "não recebido" nem "em processamento".
  - **Autorização (decisão técnica):**
    - a organização vem da sessão e o RLS a garante;
    - com `actorId` da sessão, a consulta só devolve a intenção do próprio autor. É a recuperação de uma resposta perdida por quem enviou. Chave de outro autor = `null`, igual à ausência, sem revelar nada;
    - `actorId: null` é só para leituras internas que já provaram a visibilidade do alvo (o recibo no detalhe do documento). A rota passa sempre o usuário da sessão;
    - na rota, a permissão exigida é a mesma de executar o comando consultado (a matriz, na etapa seguinte).
- **`listarDocumentos(c) → DocumentoResumo[]`** (recebimento.ts), do mais recente (data do recebimento, depois o instante do registro). Campos:
  - identificação e origem: id, emitente {id, nome, identificação}, tipo, série, número, emissão, recebimento, fazenda {id, nome}, status, versão, registradoEm;
  - contagens: linhas, divergências (linhas com motivo), inspeções (linhas com quarentena > 0) e ocorrências abertas.
- **`documento(c, id) → DocumentoDetalhe | null`**: o resumo, mais:
  - pedido {sistema, referência} | null e autor {id, nome};
  - recibo (via `consultarIntencao` pela chave gravada no documento, `actorId: null`), que dá a pendência e a próxima ação do mesmo recibo, sem outra fonte de estado;
  - linhas, em ordem de número:
    - identificação: id, número, produto {id, nome}, lote {id, código, tipo, validade | null}, local {id, nome};
    - quantidades: documento, unidade, conversão {id, versão} | null, parcelas {apto, quarentena, bloqueado, recusado};
    - divergência {motivo, texto | null} | null. No incremento 1 toda divergência está Aberta: não há comando que a encerre;
    - inspeção {responsável {id, nome}, prazo} | null;
    - pedidoLinha | null, valorUnitario | null;
    - movimentos: ids em ordem de versão do lote. É o vínculo com o extrato do lote;
  - ocorrências, em ordem de linha:
    - id, linha {id, número}, produto real {id, nome} ou {descrição};
    - quantidade e unidade contadas;
    - destino, status, responsável {id, nome}, prazo | null, registradaEm.
- **Fica para a etapa da tela:** `documentoPorOrigem`, que é o aviso de duplicidade do FO-18 antes de confirmar. Não entra neste bloco porque só a tela o usa. O índice parcial continua sendo a barreira.

## 6.2 Borda HTTP: comando e GET de recibo (sem tela)
**POST `/api/v1/comandos/estoque.receber-documento`.** Usa a mesma fábrica `criarRotaComandos`, sem rota de mutação paralela. A ordem é a atual, e cada recusa vem antes de qualquer gravação:
1. comando desconhecido → 404;
2. Origin diferente → 403;
3. corpo que não é JSON → 415;
4. sem sessão → 401;
5. matriz → 403;
6. corpo lido com limite de bytes do comando antes do parse → 413;
7. JSON inválido → 400;
8. `EsquemaPedidoComando` estrito → 400.

Depois vêm as regras próprias do comando novo:
- `target.type = 'receipt_document'` e `expectedVersion = 0`, senão 400, sem gravar. `target.id` é o id do documento, gerado no cliente (§6).
- `data` passa por `EsquemaDadosRecebimento` estrito, senão 400 com os campos, sem ecoar valores. O esquema não aceita movimento livre: só o documento.
- `canonizarRecebimento(data)` vira o `data` da intenção (hash) e o insumo do efeito. "10" e "10.0" são o mesmo conteúdo, e a mesma chave devolve o mesmo recibo.
- Organização e ator vêm sempre da sessão. Campo de ator ou organização no corpo é recusado pelo esquema estrito.
- Resposta: o recibo, com status pelo resultado. 200 confirmed; 422 rejected; 409 version_conflict. Chave reutilizada ou em processamento dá 409 com o código; falha transitória dá 503.
- Limite por comando, explícito: `estoque.registrar-entrada` 16 KiB (inalterado); `estoque.receber-documento` 64 KiB (50 linhas, §6).
- **Valor unitário (v3.8, Codex 07:46Z):**
  - O esquema recusa, com 400 `CONTRATO_INVALIDO` e sem gravar, escala acima de 8 casas depois da forma canônica (zeros à direita não contam: "1.123456780" vale) e valor negativo, com o campo e o problema.
  - Antes, o CHECK de `unit_price` na 0007 fazia disso um 23514 no efeito, que virava 503 incerto na tela.
  - Nenhum outro campo muda.
- O comando legado segue idêntico: alvo `lot` igual ao lote, só entrada, mesmas versões.

**GET `/api/v1/intencoes/{commandType}/{chave}`** (IDEM-09), sem efeito:
1. comando desconhecido → 404 `NAO_ENCONTRADO`;
2. qualquer parâmetro na query → 400. Autor e organização nunca vêm do cliente, e `actorId: null` não existe na borda;
3. Origin presente e diferente da aplicação, ou `Sec-Fetch-Site` fora de `same-origin`/`none` → 403;
4. sem sessão → 401;
5. papel sem permissão de **executar** o comando consultado → 403. O gerente não consulta chave de comando que não pode enviar;
6. chave vazia, só espaços ou com mais de 128 caracteres → 400;
7. `consultarIntencao` com o autor da sessão, dentro de `emOrganizacao`;
8. **Recibo registrado:** o mesmo corpo e o mesmo status que o reenvio do POST devolveria (200, 422 ou 409, com `alreadyReceived: true`). Assim o cliente trata a recuperação com o mesmo código da resposta original;
9. **Não localizado:** 404 com o código novo `RECIBO_NAO_LOCALIZADO` (classe acesso). A mensagem é "Recibo ainda não localizado: reenvie o mesmo pedido com a mesma chave; ele não é gravado duas vezes." Nunca "não recebido" nem "em processamento". Intenção de outra organização ou de outro autor dá a mesma resposta;
10. `cache-control: no-store` e `x-correlation-id` em toda resposta. Nenhuma gravação: intenção, auditoria, outbox ou log de conteúdo.

**Incerteza só se resolve com recibo terminal correspondente** (Codex 06:29Z e 06:50Z):
- Um POST sem resposta certa deixa a intenção **incerta**: rede caiu, 5xx, 409 `IDEMPOTENCY_IN_PROGRESS` ou corpo que não é recibo. A intenção guarda chave, id do documento e corpo exato, e fica imutável.
- Só um recibo **validado** (`EsquemaRecibo`) **e correspondente** resolve a incerteza, venha do GET ou do reenvio do mesmo POST. Correspondente quer dizer mesmo `commandType`, mesma `idempotencyKey`, `targetType = receipt_document` e o mesmo `targetId`. O resultado pode ser confirmado, rejeitado ou conflito.
- Nenhuma outra resposta ao GET ou ao reenvio encerra a incerteza nem libera editar ou criar outra chave: 400, 401, 403, 404 `RECIBO_NAO_LOCALIZADO`, 413, 415, 5xx, rede ou recibo de outra chave. A tela mantém chave, corpo e rascunho, mesmo com sessão expirada ou papel mudado, e diz o que fazer ("Entre de novo para conferir", "Reenvie o mesmo").
- A regra da resposta do POST (`desfechoDaResposta`, entrada.ts) **não** é copiada para as falhas do GET. Numa primeira tentativa, 400/401/403/413/415 no POST são certezas de que nada foi gravado. Num reenvio de intenção incerta, não são.
- A consulta nunca reenvia sozinha: reenviar é gesto explícito ("Reenviar o mesmo").
- A intenção incerta sobrevive a recarregar, isolada por usuário e organização (`localStorage`, chave com os dois ids). Outra sessão no mesmo navegador não a vê nem a reenvia. Sair apaga.
- **Várias abas (v3.10, CX-UI01):**
  - Cada intenção pendente tem a própria chave `safrion:recebimento-intencao:<usuário>:<organização>:<chave da intenção>`, com o corpo imutável e os campos enviados. Ela nasce antes do POST (sem gravar, nada é enviado) e só é apagada por quem a resolve com recibo correspondente, ou por Sair.
  - O rascunho (`safrion:recebimento:<usuário>:<organização>`) guarda só campos, e gravá-lo nunca toca intenção.
  - Nada depende de ler, alterar e gravar a mesma chave de forma atômica: intenções são criadas e apagadas por chave própria, e o rascunho vale pela última gravação.
  - Toda aba mostra primeiro a intenção pendente mais antiga, travada, com "Consultar recibo". Com mais de uma, trata uma de cada vez. O evento `storage` avisa as outras abas.
  - Ao confirmar, o rascunho só é limpo se ainda for o conteúdo enviado; o que outra aba digitou depois fica.
- **Recusa sem perder preenchimento (v3.12, CX-UI04):**
  - Uma intenção resolvida sem confirmar (rejeitada, conflito ou recusa certa do primeiro envio) só volta direto para os campos quando não há rascunho diferente guardado.
  - Havendo rascunho diferente, os campos dela vão para um **formulário guardado** (`safrion:recebimento-guardado:<u>:<o>:<id>`), com o motivo, e o rascunho fica intacto. O erro de uma NF nunca aparece nos campos de outra.
  - A tela lista os guardados, cada um com o nome do documento e o motivo, e dá duas saídas explícitas:
    - **Abrir para corrigir:** o rascunho atual, se tiver conteúdo, vira guardado, e nada se perde;
    - **Descartar:** gesto explícito.
  - Nenhum POST sai sozinho. Sair apaga os guardados, como o resto.

**Continuam fora e registrados antes do aceite do incremento:**
- a tela (FO-18, lista e detalhe);
- a trilha legível do lote granel (`DOC:<uuid>` nunca aparece cru);
- o retry de deadlock (§6);
- `documentoPorOrigem`.

## 6.3 Aviso antecipado de duplicidade: `documentoPorOrigem` (v3.13; só leitura e rota, tela depois)
É auxiliar do FO-18: avisa, antes de confirmar, que a NF daquele emitente já entrou. **O índice parcial e o recibo continuam a autoridade**: o aviso pode não aparecer (corrida, rede) e a confirmação ainda recusa com `DOCUMENTO_JA_RECEBIDO`.

- **Banco:** `documentoPorOrigem(c, {emitente, tipo, serie, numero}) → DocumentoResumo | null` (recebimento.ts).
  - Normaliza com `identidadeDaOrigem`, a mesma do comando e do índice: NFC, trim e sem zeros à esquerda quando numérico.
  - Procura o documento `confirmado` da organização da sessão (RLS).
  - Emitente fora do formato ou origem inválida devolve null, sem consultar e sem erro do banco.
- **Rota:** GET `/api/v1/recebimentos/origem?emitente=<uuid>&tipo=<nfe|outro>&serie=<texto>&numero=<texto>`, pela fábrica nova `rotas/recebimentos.ts`.
  - Recusas, na ordem:
    - parâmetro fora desses quatro (autor ou organização nunca vêm da requisição) → 400;
    - outro site (Origin ou Sec-Fetch-Site, como no GET de recibo) → 403;
    - sem sessão → 401;
    - papel sem permissão de **executar** `estoque.receber-documento` → 403 (é ajuda de quem recebe);
    - origem inválida (tipo, emitente não UUID, número vazio ou acima de 20 caracteres, série acima de 8, depois da normalização) → 400 com o campo.
  - Respostas: `200 { encontrado: true, documento: { id, tipo, serie, numero, emitente: { id, nome }, recebimento, status } }` ou `200 { encontrado: false }`.
  - Sem cache compartilhado (`no-store`) e sem gravação.
- **Sem enumeração:** o emitente é UUID da própria organização. Outra organização e inexistente dão a mesma resposta `{ encontrado: false }`.
- **Na tela (v3.14):**
  - A consulta sai quando a identidade fiscal fica completa e válida (emitente, tipo e número; série opcional). Dispara ao sair do Número ou da Série e ao trocar Tipo ou Emitente; nunca por tecla.
  - Uma consulta em andamento é cancelada, e a resposta que chega para uma origem que já mudou é descartada.
  - **Encontrado:** aviso no bloco Documento, "Esta NF já foi recebida em dd/mm/aaaa", com o link **Ver recebimento** (o detalhe do documento). O preenchimento fica guardado no rascunho, e confirmar continua possível: o índice decide.
  - **Não encontrado:** nada a mostrar; nunca "NF nova".
  - **Indisponível** (rede, 401, 403 ou 5xx): nota neutra "Não deu para conferir agora; a confirmação confere de novo". Isso não equivale a origem nova.
  - Na confirmação recusada com `DOCUMENTO_JA_RECEBIDO`, a tela faz a mesma consulta para oferecer **Ver recebimento**. Nada é descartado nem reenviado sozinho.

## 7. Menor incremento
**Entra:**
- Almoxarife: Receber → FO-18 → Confirmar → detalhe do documento, com parcelas, divergência como alerta, responsável e prazo da inspeção e próxima ação.
- Estoque › Recebimentos, com listagem e detalhe. O gerente lê, sem o botão Receber. A trilha do lote abre a linha e o documento de origem. Tela nova, ao lado da entrada atual por lote, que continua.
- Reuso da UI (ponto do Codex): `Tabela`, `Cabecalho`, `estadoDaUrl` e `caminhoDeVolta`; o padrão de envio incerto de `entrada.ts` (sucesso só com recibo, chave/conteúdo/versão preservados, edição bloqueada enquanto incerto); o rascunho passa a ter a identidade do documento. Depois de confirmar, nada de quantidade, lote ou validade é herdado pelo próximo documento. Local único e unidade vêm do contexto, sempre visíveis; quantidade e condição exigem conferência.
- Carga fictícia (DEC-2709-01), somada ao seed atual sem renomeá-lo (ambiente.ts:184-198): Fornecedor Teste Ltda, Fungicida A, galão de 5 L v1 e Diesel S10 (sem validade, em L). O local é o "Almoxarifado central" existente, sem "Depósito Central" (§7.1; aceito pelo Codex às 06:56Z). A tarefa da HML avisa que, até o incremento 3, erro de digitação só se corrige com `demo:reset` (R-006-requisitos.md:45-47).

### 7.1 A tela, por entidade e estado (Codex 06:50Z)
Reuso de `Cabecalho`, `Tabela` (G2), `estadoDaUrl`/`caminhoDeVolta`, `Selo` e das classes atuais. Sem protótipo, sem design system novo e sem navegação de fases futuras. Menu: **Estoque · Recebimentos · Cadastros**; Recebimentos é visível a quem lê estoque.

| Entidade / nível | Estado | Ação primária (uma) | O que a tela mostra |
|---|---|---|---|
| Recebimentos (lista) | — | Almoxarife: **Receber documento**. Gerente: nenhuma (só consulta) | Documento (NF série/número), emitente, recebido em, estado com palavra (Conforme · Divergência aberta · Inspeção pendente) e linhas; filtro, ordem e agrupamento da G2 na URL |
| Formulário (FO-18) | Em edição | **Confirmar recebimento**, que valida no campo e na linha e foca o primeiro erro | Origem (emitente, NF-e/outro, série, número, emissão, recebido em = hoje, visível e editável), fazenda e local do contexto (lidos quando únicos), e linhas com produto, lote ou "Granel · lote do documento", validade ou "Não se aplica", unidade (base e embalagens do produto) e quantidade do documento, mais as 4 parcelas. Motivo só com divergência, texto só com "outro", responsável e prazo só com quarentena, ocorrência só com "produto diferente". Resumo "N linhas · X divergências" junto ao botão |
| Formulário | Enviando | Nenhuma: o botão fica ocupado e os campos só leitura | "Enviando" |
| Formulário | Envio incerto | **Consultar recibo** | Aviso fixo: "O envio pode ter chegado". Campos travados com o conteúdo enviado. Se a consulta der "ainda não localizado", aparece a secundária **Reenviar o mesmo**. Com sessão expirada: "Entre de novo para conferir" |
| Formulário | Rejeitado (recibo 422) | **Confirmar recebimento** (nova chave, depois de corrigir) | Motivo em português junto ao campo ou à origem. Rascunho mantido |
| Documento (detalhe), ocorrências (v3.10, CX-UI03) | — | — | **Todas** as ocorrências, abertas e registradas: situação com palavra (Aberta, Registrada), linha, o que chegou (produto ou descrição), quantidade e unidade contadas, destino, quem responde e prazo, quando houver. Devolvida na entrega não vira pendência |
| Documento (detalhe) | Confirmado, com ou sem pendências | A próxima ação do recibo: "Ver inspeção pendente" ou "Ver divergência" levam às pendências; "Receber documento" só para o almoxarife. Gerente: "Somente consulta" | Origem, autor e hora; pendências com o que é, a linha, quem resolve e o prazo; linhas com as parcelas (palavra + número, nunca só cor). Cada linha abre o lote e o seu extrato |
| Lote (granel) | — | A do lote, sem mudança | Nome "Granel · NF série/número · emitente", nunca `DOC:<uuid>`. Lote de fabricante com código parecido não muda |
| Extrato do lote | — | — | Coluna Origem ("NF 1/7001 · linha 1" ou "Entrada manual"); o movimento de recebimento abre o documento |

- **Decimais:** pt-BR no campo ("12,5"; milhar só em grupos de três). Viram texto canônico sem `Number`. Parcela vazia é 0.
- **Rascunho em `localStorage`** por usuário e organização (§2). Depois de confirmar, nada de quantidade, lote ou validade passa para o próximo documento. Sai do rascunho só o que é contexto: fazenda e local únicos, e a data de hoje.
- **Carga fictícia somada** (ambiente.ts): Fornecedor Teste Ltda, Fungicida A em L com galão de 5 L v1 e Diesel S10 (sem validade, lote por documento). **Sem "Depósito Central":** um segundo local mudaria o formulário legado de entrada, que hoje mostra o local único só para leitura, e as jornadas B2. O recebimento usa o "Almoxarifado central" existente. Desvio do R-006 §1.6 registrado aqui.
- **Aviso antecipado de duplicidade** (`documentoPorOrigem`): fica fora deste commit. Hoje a duplicidade aparece na confirmação, com o recibo 422 `DOCUMENTO_JA_RECEBIDO` e o texto "Este documento do emitente já foi recebido". O índice e o recibo continuam a autoridade. O aviso antecipado exigiria outra leitura HTTP.

**Fica fora deste incremento, com motivo e destino.** O que é da Fase 1 continua nela; o Codex registra cada corte em DECISIONS.md.

| Item | Motivo | Destino |
|---|---|---|
| Liberar qualidade e Segregar | Não estão na jornada; o domínio já existe | Incremento 2 da F1 (RF-SUP-007 P0/E1; DEMO-02) |
| Estorno vinculado | Até lá, `demo:reset` corrige os dados fictícios | Incremento 3 da F1 (ENG-026) |
| Pedido, CAL-03, Resolver diferença (inclusive decidir a ocorrência de produto divergente) e devolução | O pedido ainda não existe; quando existir, o CAL-03 é transacional no CMD-15 (V11:13175). Até lá, divergência e ocorrência ficam abertas e visíveis, com responsável | Fase 1 comercial: recorte da etapa 10 (plano:46, 124) |
| Retirar a entrada atual por lote | Só depois de o recebimento por documento ser aceito como substituto | Mudança própria, depois do aceite |
| Título GE-04 | É financeiro | Fase 3 (plano:37) |
| Cadastros mínimos por tela e feedback com print e comentário (FLUXUX-16) | É outra fatia; aqui basta a carga fictícia. O R-006:99 (27/09) previa feedback por mensagem | Etapa 02 da F1 (plano:236, 745, 754) |
| Geometria no mapa | Ainda não há geometria; fazenda e local já ficam gravados | Etapa 03 (plano:95) |
| Ler QR e anexo com checksum | Exigem armazenamento | Depois da F1 (V11:8785) |
| Projeção da SU-01 | A SU-01 não existe | Com a SU-01 (V11:1244) |
| Valoração | O valor unitário é gravado, sem cálculo | Fatia de custo direto (E1, V11:4916) |

## 8. Arquivos
**Claude, novos:**
- `packages/db/migrations/0007_recebimento_documento.sql`.
- `packages/domain/src/recebimento.ts`, com export em `index.ts`: parcelas, divergência, parcela → situação, agrupamento por lote e numeração.
- `packages/contracts/src/recebimento.ts`, mais `index.ts` e `erros.ts`: EsquemaDadosRecebimento, normalização e códigos novos.
- `packages/db/src/recebimento.ts`: `receberDocumento`, `listarDocumentos` e `documento`, com as ocorrências (§6.1); `documentoPorOrigem` vem na etapa da tela.
- `consultarIntencao` em `packages/db/src/comando.ts` (aditivo, §6.1), exportada em `packages/db/src/index.ts` e `packages/db/src/web.ts` junto com as leituras do documento, servida por `apps/web/src/rotas/intencoes.ts` (fábrica nova) e `apps/web/src/app/api/v1/intencoes/[commandType]/[chave]/route.ts` (GET, só leitura; §6.2).
- Borda do comando (§6.2): `apps/web/src/rotas/comandos.ts` (despacho por commandType e limite por comando), `apps/web/src/autorizacao/matriz.ts` (o comando novo, só do almoxarife), `packages/contracts/src/erros.ts` (`RECIBO_NAO_LOCALIZADO`) e `packages/db/src/web.ts` (exporta `receberDocumento` e `COMANDO_RECEBER_DOCUMENTO`). Testes: `apps/web/test/matriz.test.ts` e `apps/web/test/recebimento-rotas.int.test.ts` (novo, HTTP por Request com PostgreSQL real).
- Testes da leitura: `packages/db/test/leitura-recebimento.int.test.ts` (novo), usando a semente e o efeito já fechados.
- **Tela (§7.1).**
  - Novos:
    - `apps/web/src/recebimento/{formulario.ts, rascunho.ts, lista.ts, ReceberDocumento.tsx}`;
    - `apps/web/src/app/(app)/estoque/recebimentos/{page.tsx, novo/page.tsx, [documento]/page.tsx}`;
    - `apps/web/test/recebimento.test.ts`;
    - `apps/web/e2e/{recebimento.spec.ts, recebimento-celular.spec.ts}`.
  - Aditivos:
    - `packages/db/src/recebimento.ts` (`opcoesDoRecebimento`);
    - `packages/db/src/estoque.ts` (nome legível do granel em `listarLotes`; origem no `extratoDoLote`);
    - `packages/db/src/ambiente.ts` (carga fictícia);
    - `packages/db/src/web.ts` (exports);
    - `apps/web/src/estoque/lista.ts` (nome do lote e coluna Origem);
    - `apps/web/src/app/(app)/estoque/[lote]/page.tsx` (título com o nome legível);
    - `apps/web/src/app/(app)/layout.tsx` (item Recebimentos);
    - `apps/web/src/componentes/{ItemMenu.tsx, Cabecalho.tsx, BotaoSair.tsx}`: ativo sem sobrepor Recebimentos; ação primária da lista; apagar rascunhos também do `localStorage`;
    - `apps/web/src/estilo/componentes.css` (linhas do formulário e pendências);
    - testes afetados: `apps/web/test/estoque.test.ts`, `packages/db/test/consultas.int.test.ts` e `packages/db/test/leitura-recebimento.int.test.ts`, mais `ambiente.int.test.ts` se a carga mudar contagens.
- `apps/web/src/recebimento/*` e `apps/web/src/app/(app)/estoque/recebimentos/{page.tsx,[documento]/page.tsx}`.
- Testes: `packages/domain/test/recebimento.test.ts` (fast-check), `packages/db/test/recebimento.int.test.ts`, `packages/db/test/concorrencia-recebimento.int.test.ts` e `apps/web/e2e/recebimento.spec.ts`.

**Claude, ajustados (só aditivos):**
- `packages/domain/src/saldo.ts` (lote sem validade: nunca vence e, no FEFO, fica elegível depois dos lotes com validade, conforme a §5), `packages/db/src/estoque.ts` (o extrato mostra linha e documento; lote com validade nula), `packages/db/src/ambiente.ts` (carga fictícia somada), `apps/web/src/autorizacao/matriz.ts` (acrescenta `estoque.receber-documento`) e `apps/web/src/rotas/comandos.ts` (despacho por commandType e limite do corpo só para o comando novo).
- Testes, só onde as tabelas e o comando novos mudam contagens:
  - `papeis-rls.int.test.ts:46-48` (de 17 para 21 tabelas), `migracao.int.test.ts:31,48` e `isolamento.int.test.ts`;
  - `apps/web/test/matriz.test.ts:16,21`;
  - regressão dos saldos atuais de `saldo.test.ts` com lote que tem validade.
- **Consumidores da validade nula, ajuste mínimo junto com o efeito** (risco localizado pelo Codex às 03:48Z): `packages/db/src/estoque.ts:87,307` (tipo `string | null`), `apps/web/src/estoque/lista.ts:38` e `apps/web/src/app/(app)/estoque/[lote]/page.tsx:58` mostram "Não se aplica" e mantêm explícito o valor ausente na ordenação. O formatador geral (`formato/data.ts:17`) continua estrito, e as datas reais dos lotes atuais não mudam. A regressão afetada inclui a lista e o detalhe com o Diesel. O fluxo do `RegistrarEntrada` não muda.
- **Não mudam:** `RegistrarEntrada.tsx`, `entrada.ts`, `estoque.spec.ts`, `isolamento.spec.ts` e `conferir_e2e.py`.
- **Aptidão:** migração e domínio isolados não são incremento apto à liberação enquanto esses consumidores não forem compatíveis.

**Codex:** tarefa do dono (R-006 §5), roteiro de aceite, cortes da §7, registro da adoção da v3.11 e do plano de 29/09 em DECISIONS.md, revisão por SHA e ensaio na HML. **Gemini:** parecer no SHA antes do merge.

## 9. Aceite
**Domínio:**
- 3 × 5 L = 15 L.
- As parcelas somam o conferido, e o recusado fica fora do físico. A divergência é derivada das parcelas. Parcela zero não gera movimento.
- Propriedade com ao menos 100 casos: apto ≥ 0 e bloqueado ≤ físico (decisão técnica).
- Lote sem validade não vence e não entra no vencido; lote com validade segue o comportamento atual (regressão).
- FEFO: lotes com validade por vencimento; depois os sem validade, pela primeira entrada e pelo id; a ordem é a mesma em duas execuções.

**Integração** (Postgres real, com `app_runtime` sem BYPASSRLS; ENG-025, V11:5374):
- **Saldos da jornada:** NF-TESTE-001 com físico 15, apto 15, bloqueado 0; lote F26-03 com físico 10, bloqueado 5, apto 5; produto com físico 25, apto 20.
- **Quarentena:** 60 recebidos com 10 em quarentena dão 50 utilizáveis (RF-SUP-007; AC-14; RN-015, V11:222), com responsável e prazo no detalhe e em `pending`. **Lote vencido** (AC-20): entra no físico e fica fora do apto.
- **Reenvio:**
  - envio igual devolve o mesmo recibo com `alreadyReceived` (AC-73, V11:13561);
  - mesma chave com outro conteúdo dá `IDEMPOTENCY_KEY_REUSED` (AC-74, V11:13562);
  - "10" e "10.0" com a mesma chave devolvem o mesmo recibo;
  - a consulta por chave responde sem efeito;
  - com a intenção ainda na transação de outra conexão (PostgreSQL real, commit retido), a consulta responde "recibo ainda não localizado", nunca "não recebido". Depois do commit, devolve o recibo.
- **Concorrência:**
  - 10 envios simultâneos com a mesma chave criam 1 documento (AC-84, V11:13579);
  - 10 envios com chaves diferentes e a mesma origem dão 1 confirmado e 9 `DOCUMENTO_JA_RECEBIDO`;
  - o documento A, com lotes novos X e Y, contra o B, com Y e X, termina sem deadlock;
  - nenhum 500.
- **Validade por produto:**
  - Diesel S10 é recebido sem data e o lote grava "não se aplica";
  - lote criado com validade, depois de o produto mudar para `nao_se_aplica`, continua exigindo a mesma data num novo recebimento (a política do lote prevalece);
  - Fungicida A sem data dá `VALIDADE_OBRIGATORIA`;
  - data no Diesel dá `VALIDADE_NAO_SE_APLICA`;
  - mudar a política do produto não altera lote nem movimento antigos.
- **Granel:** duas NF de emitentes diferentes com a mesma série e o mesmo número, ambas de Diesel S10, criam dois lotes `agrupamento_interno` diferentes; o reenvio da mesma intenção não cria lote novo.
- **Deadlock persistente** (40P01 injetado em toda tentativa): termina em até 3 tentativas e 2 s, com `FALHA_TRANSITORIA`, `resultadoIncerto: false` e nenhum documento, linha, movimento ou versão gravados. Com a conexão derrubada durante o COMMIT, a resposta é `resultadoIncerto: true`.
- **Produto diferente:** chegou o produto B no lugar do A. A ocorrência fica aberta, com o produto, a quantidade e a unidade reais, o responsável e o prazo. O saldo e o físico de A e de B não mudam, nenhum movimento é criado e a pendência aparece no recibo e no detalhe.
- **Rejeições com 422, com só o registro gravado:** conversão de outro produto, lote de outro produto, validade diferente da do lote, local de outra fazenda e quantidade fora da escala. No incremento 3, com o índice parcial, a mesma NF volta a entrar depois de `Estornado`.
- **Trilha e atomicidade:** o movimento leva à linha, e a linha ao documento. Uma falha forçada depois dos movimentos não grava nada (IDEM-16). **Auditoria** (NFR-04): autor, antes e depois, versão, motivo e correlação.
- **Isolamento** (FLUXUX-18; AC-04, V11:4832): a organização B, ao listar, abrir, consultar a chave, usar o fornecedor da A ou receber no lote ou local da A, recebe a resposta de inexistente. As ocorrências e os fornecedores da A não aparecem para a B. Um id de documento da A enviado pela B dá `ALVO_INVALIDO`, sem revelar que o id existe.

**E2E:**
- Jornada R-006 §5, passos 1 a 6. A divergência "avaria" aparece como alerta na lista e no detalhe. O gerente não vê o botão Receber.
- Listagem Recebimentos com filtro, ordenação, agrupamento e retorno ao ponto de partida (AC-02/03). Trocar a fazenda com um documento aberto não altera o documento (AC-05).
- Recarregar a página com envio sem resposta consulta pela chave antes de reenviar (AC-87, V11:13582; R-006-requisitos.md:78). Sem recibo localizado, oferece reenviar a mesma chave com o mesmo conteúdo.
- As jornadas atuais (B2-C01..C03, HML-ISO-01..03) continuam passando sem mudança.
- Depois de uma falha, o rascunho é preservado. É a única parte do FLUXUX-16 aceita aqui.

**Não funcional:** p95 ≤ 600 ms e WCAG 2.2 AA, conforme o R-006. O p95 é medido pelo ensaio delimitado da §9.1.

## 9.1 Ensaio de desempenho delimitado (v3.15; proposta, só roda depois do ACK do Codex)
**Pergunta:** o comando e as duas consultas novas cabem nos orçamentos do PRD §29.3 (R-006:80) no servidor desta candidata, sem rede? Não é SLO, não mede HML nem a rede de referência, e não substitui o teste P1 da §29.2/§29.4.

- **Versão:** head `1f0817a` (código igual ao de `605b9ff`; depois dele, só testes e documentação). Build de produção do Next e `next start`, `SAFRION_AMBIENTE=dev`, login DEV fictício (Almoxarife); o cookie de sessão é obtido uma vez pelo fluxo real de entrada.
- **Ambiente:** MacBook Air M2 (Mac14,2), 8 núcleos, 8 GB; Node 24.21.0 e PostgreSQL 17.10 do toolchain; PostgreSQL local por TCP 127.0.0.1 com a configuração padrão do initdb; pool do app `max: 3` (`apps/web/src/servidor/ambiente.ts:52`), sem mudança. Gerador, servidor e banco disputam a mesma máquina; isso fica registrado com o uso de CPU e memória.
- **Gerador:** script Node (`fetch`) em modelo de chegada aberto: horários de disparo sorteados antes, com semente fixa, sem esperar resposta para disparar a próxima. Registra o atraso de cada disparo; um disparo com mais de 50 ms de atraso conta como "não disparado no horário" e é relatado. Não é k6 (PRD §29.4), limite declarado.
- **Tempo medido nos dois lados:** no cliente, do envio à resposta completa em loopback (limite superior do tempo de servidor); no servidor, `duracao_ms` e `tentativas` do log estruturado do envelope (só o envelope, sem HTTP e sessão). O orçamento vale para o tempo do cliente; o do servidor explica.
- **Dados (perfil):** o banco da demo (Fornecedor Teste Ltda, Fungicida A com galão 5 L e validade, Diesel S10 a granel por documento) mais uma pré-carga de 1.000 NFs confirmadas pelo próprio POST, fora da medição. Mistura de NFs: 70% com 3 linhas, 20% com 1 e 10% com 10, alternando lote de fabricante com validade e lote interno de granel. Número de NF, código de lote de fabricante e chave de idempotência únicos por requisição; a demo tem só dois produtos e um local, então todos os comandos já disputam o mesmo produto e local.

| Classe | Operação | Orçamento (PRD §29.3) |
|---|---|---|
| Comando | `POST /api/v1/comandos/estoque.receber-documento` | p95 ≤ 600 ms, p99 ≤ 1,5 s |
| Consulta | `GET /api/v1/recebimentos/origem` (metade NF existente, metade nova) | p95 ≤ 300 ms, p99 ≤ 800 ms |
| Consulta | `GET /api/v1/intencoes/estoque.receber-documento/<chave>` (recibo existente) | p95 ≤ 300 ms, p99 ≤ 800 ms |

- **Fases (cerca de 10 min no total):**
  1. Frio: `next start` recém-iniciado, 20 comandos em sequência. Relatado à parte, fora do p95.
  2. Aquecimento: 60 s a 2 req/s com a mistura abaixo. Descartado.
  3. **Normal, a que vale para o orçamento:** 5 min a 10 req/s; 60% origem, 20% comando e 20% recibo (≈ 1.800, 600 e 600 amostras).
  4. Rajada: 60 s a 30 req/s, mesma mistura. Relatada à parte; mostra a espera do pool de 3.
  5. Contenção: 30 s a 4 comandos/s, todos no mesmo lote de fabricante já existente do Fungicida A. O recebimento trava a linha do lote (`FOR UPDATE`, `packages/db/src/recebimento.ts:395`), então os comandos se enfileiram nela. Relatada à parte; mostra espera e repetição por 40P01.
- **Resultado:** p50, p95, p99, máximo e contagem por classe e fase; erros inesperados por classe, com limite ≤ 0,1% (validação de negócio esperada é contada à parte); atraso do gerador; CPU e memória de `next` e `postgres` por `ps` a cada 5 s; distribuição de `tentativas`.
- **Reconciliação (reprova se falhar):** documentos confirmados = recibos aceitos que o gerador recebeu; linhas = movimentos; saldo por lote = soma das linhas aptas; nenhuma intenção em `processing`; nenhuma NF duplicada; auditoria e outbox na proporção do comando.
- **Reprovação:** qualquer orçamento estourado na fase 3, erro inesperado acima do limite ou reconciliação com diferença. Nada de ajustar pool, índices, amostra ou fase para passar: um estouro vira achado, com causa investigada e registrada.
- **Regras de veredito, fixadas antes da carga (ACK do Codex, 10:39Z):**
  - Por fase e classe, relato planejadas, disparadas no prazo (atraso ≤ 50 ms), atrasadas, concluídas e falhas. Nenhuma fica fora do denominador.
  - Cada requisição tem timeout de 10 s. Timeout, erro de rede, 5xx e 4xx inesperado contam como falha e entram nos quantis como latência infinita, nunca como sucesso rápido. O tempo inclui o corpo completo, e não há reenvio pelo gerador.
  - Latência relatada de dois jeitos: desde o disparo real e desde o horário planejado. O veredito usa a segunda, que é a mais conservadora. Os quantis (nearest-rank) são por operação, sem misturar GET e POST.
  - **INCONCLUSIVO** para o orçamento se, na fase normal, menos de 99% das planejadas de alguma classe saírem no prazo, ou se alguma não concluir dentro do prazo de encerramento da fase (timeout + 5 s). Nesse caso não há aprovação por medir só as sobreviventes.
  - **APROVADO** só se a fase normal for válida, cada classe cumprir o p95 e o p99, o erro inesperado ficar ≤ 0,1% por classe e a reconciliação fechar. Fora disso, **REPROVADO**, com o achado investigado.
  - Resposta perdida (timeout ou rede) num comando é **incerta**. Depois da carga, fora da medição, consulto a chave pelo GET de recibo: confirmado entra na reconciliação; `RECIBO_NAO_LOCALIZADO` não entra. Nunca trato ausência de 200 como ausência de COMMIT.
- **Reconciliação por chave, com base no retrato tirado depois da pré-carga:**
  - Cada chave termina como confirmada, rejeitada ou incerta resolvida; nenhuma intenção fica em `processing`.
  - Documentos, linhas e movimentos batem com o delta das chaves confirmadas. Linhas = movimentos porque o perfil só tem uma parcela positiva por linha (apto).
  - O saldo **por lote, na unidade base**, bate com a soma das linhas (galão de 5 L vira L; o lote de granel é `DOC:<id do documento>`).
  - Outbox = um evento de recebimento mais um por lote afetado, por comando confirmado.
  - Pelo menos uma auditoria por chave confirmada, sem NF duplicada e sem efeito extra.
- **Leitura honesta:** os 20 do frio são uma série de primeiras requisições depois da subida, não 20 partidas a frio independentes. A contenção pode terminar com zero 40P01, porque a ordem das travas enfileira os comandos, e isso não é falha nem prova de deadlock real. CPU e memória também são registradas para o processo do gerador.
- **Fora do ensaio:** HML, Cloud Run e Cloud SQL; rede de referência e de resiliência; aparelho físico; "do toque ao recibo" e abrir lista ou detalhe na tela; o envelope P1 (20 organizações, 50 req/s por 30 min, 8 h, volume de 10 milhões de movimentos); OIDC.
- **Arquivos:** só novos, fora do repositório: `gerador-p95.mjs` e `rodar-p95.py` no rascunho do Claude, com as saídas exportadas para `fontes-claude/cmd15/p95-1f0817a/`. Nenhuma edição em produto ou teste do repositório.

## 9.2 Espera controlada na aquisição de conexão (v3.16; proposta do achado CMD15-P95-01, só edita depois do ACK)
**O que se sabe, por leitura de código:**
- O app pega conexão em três pontos: `resolverSessao` (`pool.query`, antes de qualquer rota autenticada), `emOrganizacao` (leituras, `sessao.ts:50`) e `tentarComando` (`comando.ts:354`, antes do `BEGIN`).
- Em HML o pool já recebe `connectionTimeoutMillis` de 10 s (`LIMITE_CONEXAO_MS`, `conexao.ts:72`, via `extra` do conector). Em DEV, no E2E e no ensaio local, não recebe prazo nenhum; o achado local vem em parte dessa diferença.
- O pg-pool 3.14.0 fixado trata o prazo de forma nativa: tira da fila quem esperou demais e responde `timeout exceeded when trying to connect`. Assim, a conexão liberada depois vai para o próximo da fila, sem vazamento e sem `Promise.race` nosso.
- Hoje esse erro sobe cru nos três pontos e vira `FALHA_INTERNA` 500 ("erro inesperado"), e não uma resposta legível.

**Menor delta proposto (autor Claude, revisão Codex, Gemini antes de integrar; mesma branch do PR #32):**
1. `packages/db/src/sessao.ts`: um `emprestarConexao(pool)` que só reclassifica a rejeição de aquisição do pg-pool em `ErroComando('FALHA_TRANSITORIA', …, { resultadoIncerto: false, repetirEmMs })`. Aqui é certo que nada começou, porque o `BEGIN` ainda não rodou; qualquer outro erro passa intacto. `emOrganizacao` e `tentarComando` (`comando.ts`) passam a usá-lo.
2. `packages/db/src/sessao-web.ts`: `resolverSessao` pega a conexão pelo mesmo helper, então autenticação de POST e GET respondem 503 legível, e não 500.
3. `packages/db/src/resposta.ts`: `repetirEmMs` passa a detalhe público de `FALHA_TRANSITORIA`. Em `apps/web/src/rotas/resposta.ts`, o `json()` põe `Retry-After` quando esse detalhe existe.
4. `apps/web/src/servidor/ambiente.ts`: o pool de DEV e local recebe o mesmo `LIMITE_CONEXAO_MS` da HML, exportado de `conexao.ts`. **Nenhum número novo:** os 10 s valem também para abrir conexão pelo conector, então mudá-los fica para depois da medição em HML.

**Precisões do ACK do Codex (11:31Z), valem sobre o texto acima:**
- `resultadoIncerto: false` descreve só esta tentativa, nunca uma intenção anterior com a mesma chave. Nas leituras o campo é omitido.
- A captura é só da rejeição de `await pool.connect()` por prazo. As duas mensagens do pg-pool 3.14.0 são `timeout exceeded when trying to connect`, na fila do pool cheio, e `Connection terminated due to connection timeout`, ao abrir conexão nova; nenhum comando SQL rodou em nenhuma delas. Qualquer outra falha de conexão e qualquer erro de query, execução ou commit ficam como hoje.
- `resolverSessao` com cliente já emprestado ou em transação não readquire, não libera e não captura erro de query. Com pool, pega a conexão pelo helper e devolve como o `pool.query` devolve, com o erro da query.
- Os 10 s valem por aquisição, não como prazo HTTP total. A diferença entre DEV e HML é hipótese de causa do P95-01, não demonstrada pelo ensaio.
- `Retry-After` só em 503, com `repetirEmMs` finito e positivo, em segundos inteiros (arredondado para cima). A sugestão de 1 s é decisão técnica, ainda sem medição.
- Contraprova: POST confirmado com resposta perdida, depois reenvio que falha na aquisição (503, esta tentativa não começou), depois a mesma chave com o pool livre devolve o recibo original.

**Fora deste delta:** travas, queries, execução e commit (resultado incerto como hoje) e transporte. **Correção da v3.16 original:** o `lock_timeout` do envelope vale só para a gravação da chave da intenção; logo depois volta ao padrão (`comando.ts:401`), e as travas do efeito, como a do lote, esperam sem prazo na primeira tentativa. Uma trava longa segura a conexão e esgota o pool; é outra hipótese de causa do P95-01, registrada e não tratada aqui. A aquisição não cobre nada disso. Também fica de fora qualquer mudança na tela: ela já trata 5xx como incerto e consulta pela chave, e nunca reenvia com chave nova. O pool segue com `max: 3`.

**Testes (integração, PostgreSQL real, pool injetado com prazo curto e `max: 1` segurado pelo teste):**
- POST de comando com o pool esgotado: 503 `FALHA_TRANSITORIA`, `resultadoIncerto: false`, `Retry-After`, e nenhuma linha em `intent_record`. Depois de liberar, a mesma chave e o mesmo conteúdo confirmam uma vez só.
- GET de origem, GET de recibo e resolução de sessão: 503 legível, sem 500.
- Sem vazamento: depois do prazo, liberar a conexão segurada volta `idleCount`, `waitingCount` fica 0 e `totalCount` não passa de `max`; o que esperou demais não executa nada depois.
- O prazo de aquisição não interrompe um comando que já tem conexão e espera trava de lote; enquanto ele espera, o próximo comando recebe a falha legível sem começar. Solta a trava, o primeiro confirma uma vez.
- Erro que não seja de aquisição continua como era (mutação: reclassificar tudo precisa ficar vermelho).
Fica declarado que a detecção depende da mensagem do pg-pool fixado; o teste falha se ela mudar.

## 9.3 Prazo para a trava do efeito (v3.17; ACK do Codex às 12:15Z, implementada em 0c74bad)
**Risco (Codex 12:07Z, prioridade de investigação antes de homologar):** na primeira tentativa, depois de gravar a chave, o envelope faz `SET LOCAL lock_timeout TO DEFAULT` (`comando.ts:401`). A partir daí, a trava do efeito (`SELECT … FOR UPDATE` dos lotes, `recebimento.ts:395`) espera sem prazo. Uma transação lenta ou presa num lote segura a conexão e pode esgotar o pool de 3, parando os recebimentos. Isso **não** está provado como causa do P95-01. No ensaio, a contenção de 4 comandos por segundo no mesmo lote ficou com o envelope em no máximo 1.787 ms, sem espera indefinida.
**Decisões anteriores que esta proposta muda, de forma explícita:** ADR 0003 ("`lock_timeout` só na inserção da chave") e §6 v3.9 ("a primeira tentativa segue sem prazo novo… é outra decisão").

**Menor delta proposto:**
1. `comando.ts`: no lugar de `SET LOCAL lock_timeout TO DEFAULT`, o efeito herda o **mesmo `lock_timeout` da espera pela chave** (`esperaChaveMs`, padrão 2 s). É reaproveitamento de um parâmetro que já existe para disputa, **sem prova de p95 ou p99**. O limite vale para **cada espera por trava**, não para a duração do efeito, da transação ou da resposta HTTP: travas seguidas, a aquisição de até 10 s, a execução, o COMMIT e o ROLLBACK somam e podem passar de 4 s. A mudança **reduz a espera indefinida por travas; não limita a espera total.** Nas tentativas repetidas, o `statement_timeout` recalculado por comando (v3.9) pode vencer antes e dar 57014, com a semântica de prazo atual. Isso não vira 55P03, e a janela de repetição não aumenta.
2. **Recuperação:** a trava que estoura dá 55P03 no efeito. **Só com ROLLBACK confirmado antes do COMMIT**, a resposta é a `FALHA_TRANSITORIA` 503 que já existe, com `resultadoIncerto: false` (esta tentativa não gravou nada) e `repetirEmMs`, portanto com `Retry-After`. Se o ROLLBACK falha ou o COMMIT já saiu, o resultado segue incerto, sem `repetirEmMs`. **Não há repetição automática** (a v3.9 já exclui o 55P03). A recuperação mantém chave e conteúdo e nunca nega um recibo anterior; a tela segue como hoje, com incerto, consulta pela chave e reenvio da mesma chave. O primeiro COMMIT e o ROLLBACK continuam como limites declarados.
3. A espera pela chave em outra transação continua `IDEMPOTENCY_IN_PROGRESS`, como hoje. O código distingue as duas pelo ponto em que o 55P03 ocorre.
**Fora:** `statement_timeout` na primeira tentativa (prazo total do comando), `idle_in_transaction_session_timeout` no papel do banco, mudança de pool e ensaio de carga novo. Cada um é decisão separada, se a investigação pedir.

**Testes (integração, PostgreSQL real, sem pendurar):**
- Lote travado por outra transação: o comando falha perto de `esperaChaveMs` com `FALHA_TRANSITORIA`, `resultadoIncerto: false`, `codigoPg: '55P03'` e `repetirEmMs`, sem linha de intenção, documento ou movimento. Liberada a trava, a mesma chave confirma uma vez.
- Disputa curta no mesmo lote (trava segurada por menos que o prazo): os comandos esperam e confirmam, sem 503.
- Espera pela chave inalterada: segue `IDEMPOTENCY_IN_PROGRESS`.
- **Duas travas seguidas**, cada uma liberada antes da espera: o comando confirma e a duração total passa da espera. Isso prova que o limite é por trava, não do comando.
- Outra falha do efeito com ROLLBACK confirmado (não 55P03) segue `FALHA_TRANSITORIA` sem `repetirEmMs`. Exceção desde 01/10: a classe 22 (dado recusado pelo banco) vira `FALHA_INTERNA` com o sinal de falha permanente (CAD-01 §11.1); o teste desta linha usa um erro fora das classes 22, 40P01 e 55P03.
- Sem resíduo depois do ROLLBACK: nenhuma intenção, auditoria ou outbox da chave, e a conexão devolvida ao pool.
- Tentativa repetida: sem teste novo; a regressão de prazo da v3.9 fica com os testes de `repeticao-deadlock` existentes.
- O teste usa vigia com prazo e solta a trava no `finally`, para que a mutação "sem prazo na trava" falhe pela asserção e não por timeout.

**Arquivos:** `packages/db/src/comando.ts` e os testes meus (`conexao-caida` ou `repeticao-deadlock`), mais um adendo datado no ADR 0003 (não é meu; precisa de reserva) e contrato e recibo.

## 10. Pergunta aberta
Nenhuma. O lote de granel foi resolvido na §1 (lote interno por documento, com referência legível à parte). Se o PRD trouxer regra própria para granel, ela prevalece.

Nenhum achado ignorado: os 19 da revisão adversarial, os 5 do Codex (01:43Z) com as notas das 01:45Z, os 3 pontos mais os 3 fechamentos do Codex (02:46Z) a precisão editorial e de prazo (03:17Z) e o escopo dos consumidores da validade nula (03:48Z) foram aplicados.