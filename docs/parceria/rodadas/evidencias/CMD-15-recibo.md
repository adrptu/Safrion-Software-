# CMD-15 — recebimento de insumos por documento: recibo compacto do incremento 1

Gerado por script a partir de saídas de comando (git, sha256, logs das baterias e das mutações) no Mac do proprietário. Serve
para retomar e reproduzir o incremento sem depender desse Mac. **Não é CI, HML nem aceite:** o parecer do Gemini e a CI do PR
seguem pendentes.

## Versões
- Base: main `6882918fab421940d26686838a5a24e8913d9a51`.
- Candidata: `claude/cmd15-recebimento` em `62f0c23d33c1738273273c333397b52d9fb44405` (código e testes; este recibo e o contrato vêm num commit só de documentação).
- Contrato vigente: [CMD-15-contrato.md](CMD-15-contrato.md), v3.16, sha256 `70568fbd1a1e9afcdeef2c021d64b89d9e1eda9edf48e741b03c03a287bdb4ab` (a v3.15 acrescenta a §9.1, ensaio de desempenho; a v3.16, a §9.2, prazo de aquisição; a v3.17, a §9.3, prazo por trava do efeito).

## Commits do incremento (do mais antigo ao mais novo)
- `ce0e2a4` feat(estoque): núcleo do recebimento por documento e inspeção (CMD-15, incremento 1)
- `3e336e1` fix(estoque): achados CMD15-CX01..03 do Codex no núcleo do recebimento
- `bbf6bad` feat(estoque): efeito estoque.receber-documento, atômico pelo envelope (CMD-15)
- `05155a0` fix(estoque): achados CMD15-CX04..06 do Codex no efeito do recebimento
- `5dd0df9` fix(estoque): leitura de lote sem validade nas telas de Estoque (CMD-15)
- `0e8161d` feat(estoque): leitura do documento de entrada e consulta do recibo por chave (CMD-15 §6.1)
- `d1dceea` feat(estoque): borda HTTP do recebimento e GET de recibo por chave (CMD-15 §6.2)
- `343eacc` feat(estoque): tela de recebimento por documento (CMD-15 §7.1)
- `7e79ecc` feat(db): repetição por deadlock no envelope e escala do valor unitário (CMD-15 §6, v3.9)
- `b3c8b34` fix(estoque): envio pendente entre abas e ocorrências no detalhe (CX-UI01, CX-UI03)
- `78409d3` docs(db): comentários do retry alinhados à v3.9 (janela de repetição)
- `28874bd` fix(db): rejeição depois de repetir e conexão que cai com o cliente emprestado (CX-R02, CX-R03)
- `9b80d35` fix(estoque): recusa não sobrescreve o rascunho seguinte; formulários guardados (CX-UI04)
- `d595285` feat(estoque): aviso antecipado de duplicidade por origem fiscal (CMD-15 §6.3)
- `605b9ff` feat(estoque): aviso antecipado de duplicidade no formulário (CMD-15 §6.3, v3.14)
- `9e7b686` test(estoque): ramos do recebimento que o gate de cobertura da CI cobra (CMD-15)
- `77d8912` fix(db): prazo de aquisição de conexão com erro legível (CMD-15 §9.2, CMD15-P95-01)
- `e732d1a` test(db): devolução única da conexão segurada nos testes da §9.2
- `0c74bad` fix(db): prazo para cada espera de trava no efeito do comando (CMD-15 §9.3)
- `62f0c23` test(db): ROLLBACK que falha depois do 55P03 fica incerto, sem repetirEmMs (§9.3)

## Bateria completa em `605b9ff` (local, não CI)
Executada com o `node` e o PostgreSQL 17 do toolchain do time, numa cópia descartável, com PostgreSQL privado só por TCP.
- tsc domain: saída 0
- tsc contracts: saída 0
- tsc db: saída 0
- tsc web: saída 0
- eslint: saída 0
- prettier: saída 0
- vitest unit: domain+contracts+web(estoque, formato, tabela, matriz, recebimento): saída 0
- vitest unit COMPLETO (configuração padrão, todos os arquivos): saída 0
- initdb: saída 0
- pg start: saída 0
- vitest integração COMPLETA (db + web, todos os *.int.test.ts): saída 0
- pg stop: saída 0
- **unit focado (domínio, contratos, web do estoque e do recebimento):** 148/148 testes em 12/12 arquivos.
- **unit completo (configuração padrão):** 300/300 testes em 25/25 arquivos.
- **integração completa com PostgreSQL real (db + web; inclui a contraprova de repetição do Codex):** 234/234 testes em 23/23 arquivos.
- **E2E** (build de produção do Next + `next start`, Chrome do sistema, login DEV, projetos desktop e celular Pixel 7 emulado): 25 testes passaram; etapas build pacotes=0, next build=0, initdb=0, pg start=0, playwright (desktop + celular)=0, pg stop=0.
- Também passaram, nessa cópia: `tools/dev/fronteiras.mjs` e `prettier --check .` do repositório inteiro.
- **Lacuna desta bateria:** o unit rodou `vitest run` sem `--coverage`; o gate da CI (`pnpm run test` = `vitest run --coverage`, 95% por arquivo em `vitest.config.ts`) não foi reproduzido aqui. Ver a seção seguinte.

## Gate de cobertura da CI (`vitest run --coverage`)
Origem do achado: CI do PR #32 no head `c5a1220` (run 36699998664, job "Código"), confirmado pela auditoria do Codex.
- Reproduzido localmente antes da correção: saída 1, 300/300 testes verdes, ramos abaixo de 95%: `packages/contracts/src/recebimento.ts` 80%; `packages/domain/src/recebimento.ts` 94.61%.
- Depois de `62f0c23` (só testes de comportamento, sem mudar produto nem limiar): saída 0, 303/303 testes; tsc, eslint e prettier com saída 0.

## Ensaio de desempenho delimitado (contrato §9.1)
Local, em `1f0817a`, `next start` de produção, login DEV, MacBook Air M2 8 GB, PostgreSQL 17 local, pool do app `max: 3`; gerador de chegada aberta com semente fixa, na mesma máquina. Regras de veredito fixadas no contrato antes da carga.
- **Veredito: INCONCLUSIVO.** Na fase normal (5 min a 10 req/s), a parcela disparada no prazo ficou abaixo de 99% em todas as classes:
  - comando: 567/596 no prazo, 0 falhas; latência desde o horário planejado p50/p95/p99 63.6 / 1451.2 / 8871.3 ms; envelope no servidor 42 / 461 / 1718 ms.
  - origem: 1678/1764 no prazo, 0 falhas; latência desde o horário planejado p50/p95/p99 19.1 / 752.6 / 7450 ms.
  - recibo: 554/590 no prazo, 0 falhas; latência desde o horário planejado p50/p95/p99 20.1 / 815.3 / 6935.1 ms.
- Causa provável, não isolada: pressão de memória na máquina (swap quase cheio depois do ensaio; picos isolados e simultâneos no servidor e no gerador). **O p95 válido fica para HML/nuvem**; não se repete neste Mac.
- Reconciliação: OK. Delta pós-pré-carga igual ao esperado em documentos, linhas, movimentos e outbox (1091, 3355, 3355, 4446); 6591 lotes exatos na unidade base; sem `processing`, NF duplicada ou confirmada sem auditoria.
- Achado CMD15-P95-01 (rajada a 30 req/s): timeouts de 10 s no cliente e envelope de até 20289 ms. Dos 95 comandos incertos, a consulta pela chave achou 73 confirmados e 22 sem recibo localizado na reconciliação. Nenhum efeito divergente ou duplicado foi observado no ensaio, mas ausência de recibo não prova que o comando não rodou: eles seguem incertos, sob a mesma chave. Acima da capacidade não houve espera limitada nem erro legível (PRD §29.2, ENG-076); a causa não foi isolada (fila, travas, execução e commit, ou transporte). Encaminhado ao Codex; não é arquivo do CMD-15.
- Zero repetições por 40P01 no ensaio inteiro, inclusive na contenção sobre o mesmo lote; isso não é falha nem prova de deadlock.

## Prazo de aquisição com erro legível (contrato §9.2, achado CMD15-P95-01)
Na rejeição por prazo do pool (fila cheia ou conexão nova que não abre a tempo), comando, leitura e sessão respondiam erro interno 500. Agora respondem `FALHA_TRANSITORIA` 503 com `Retry-After`: nenhum comando SQL da tentativa rodou, e num comando `resultadoIncerto: false` descreve só esta tentativa. DEV e CI passam a ter o mesmo prazo de 10 s por aquisição da HML (adendo de 30/09 no ADR 0006).
- tsc domain: saída 0, tsc contracts: saída 0, tsc db: saída 0, tsc web: saída 0, eslint: saída 0, prettier: saída 0, vitest unit: domain+contracts+web(estoque, formato, tabela, matriz, recebimento): saída 0, vitest unit COMPLETO com cobertura (pnpm run test da CI): saída 0, initdb: saída 0, vitest integração COMPLETA (db + web, todos os *.int.test.ts): saída 0.
- Unit completo com cobertura (gate da CI): 303/303; integração completa com PostgreSQL: 237/237. Mutações: 8/8 detectadas. E2E fica para a CI do push.
- **Correção dos testes (`e732d1a`, achado do Codex):** das 8 mutações acima, 2 terminaram por timeout do teste (a conexão segurada não voltava ao pool depois da asserção falhar), e não pela asserção. Com a devolução única no `finally`, as 2 foram refeitas: "leitura sem o helper (pool.connect cru)" detectada em 3.6 s; "leitura afirma resultadoIncerto" detectada em 2.6 s, pela asserção e sem timeout.
- **Limite:** o prazo vale por aquisição, não é prazo HTTP total. A trava do efeito, que antes esperava sem prazo, é tratada na §9.3 abaixo.

## Prazo para cada espera de trava no efeito (contrato §9.3, commit `0c74bad`)
Antes, na primeira tentativa, o envelope voltava o `lock_timeout` ao padrão depois de gravar a chave, e a trava do efeito (o lote, por exemplo) esperava sem prazo segurando a conexão. Agora o efeito herda o mesmo `lock_timeout` da espera pela chave (`esperaChaveMs`, 2 s por padrão). O 55P03 com ROLLBACK confirmado vira `FALHA_TRANSITORIA` com `repetirEmMs`, sem repetição automática. Adendo de 30/09 no ADR 0003.
- **O limite vale para cada espera por trava, não para o comando.** Reduz a espera indefinida por travas; não limita a espera total. Um teste determinístico com duas travas seguidas, cada uma liberada antes da espera, confirma com duração acima da espera. O valor de 2 s reaproveita um parâmetro existente, sem prova de p95 ou p99.
- Unit completo com cobertura (gate da CI): 303/303; integração completa: 241/241; arquivo de teste final (depois de um ajuste de lint na vigia): 11/11. Mutações: "trava do efeito volta a esperar sem prazo" em 14 s; "toda falha confirmada vira trava ocupada" em 6.6 s; "55P03 do efeito sem repetirEmMs" em 5.4 s, todas pela asserção e sem timeout de teste. E2E fica para a CI.
- **ROLLBACK que falha depois do 55P03** (contraprova do Codex, incorporada em `62f0c23`): o resultado fica incerto, sem `repetirEmMs` nem `Retry-After`, com a conexão fora do pool e sem resíduo. A mutação "trava ocupada sem conferir o ROLLBACK (sem !incerto)" foi detectada em 7.3 s, pela asserção.

## Revisões independentes do Codex
Recibos em `cons/work/cmd15-review/<sha>/receipt.json`, fora do repositório; o registro dos pareceres está em `cons/outputs/revisao-f0a.md`.
- `05155a0`: sha256 `b7058a2f7d1d470d9c1b809fe1ef10ff58ac5cfb4334cf83c0a34c3cc96df732`
- `0e8161d`: sha256 `99f5d09f3d6558d9800971b33e13643d2469a9238f66894bc739118ce680b8f4`
- `28874bd`: sha256 `c453979bdf24d9e30b212e2d8f8dee11aea9a0581cac5bc9a8ad0b86d8265797`
- `343eacc`: sha256 `c71b0e47d4d9dead534c016ac8aa364447ac3452513a0ebd31c9df3ba44a73ca`
- `3e336e1`: sha256 `9db8aff243e5db3159af1e75d03700c68bb30ee2a36f734669d2d8f60d8efbfc`
- `5dd0df9`: sha256 `8e4906edabc34638c7590f61116091f679752b1d41bdd1caffe68fbf0d246b8c`
- `605b9ff`: sha256 `dd07c321217c01db1c3b7ca0fca0040f4b9d7c774ab0c206662a3d4852a8c67f`
- `78409d3`: sha256 `dee63514faeba926fce1ffd81ce6d953de0a3a78d78b0bb51246d4f21a20a0e8`
- `7e79ecc`: sha256 `dd9745ae4692d3127e6df5412555159625d4803c16bddd27b075e35e9c2d03cb`
- `9b80d35`: sha256 `815c5a43f26938c5677689d80fe332b70207986532953b1c0aaa9cef79cb1a8b`
- `bbf6bad`: sha256 `4e594783288ecc9bf695bfd5734618a09c55750fe681c577ad641c397cd2858d`
- `ce0e2a4`: sha256 `206c7fa19f5873f7f05f0f2d8f67dd78276581bad5b6b2fea069c8114d3629a9`
- `d1dceea`: sha256 `c5423e7b6df844fcf745a48c5e997016108cba014d1a3c86ecd09c393a5f99fc`
- `d1dceea-retry`: sha256 `0f917110209b990228d7c724d0e011500a5363c2f36b0a60f89538b36ecb6f9f`
- `d595285`: sha256 `1980aa694d96e096eafd0fd1af61c59a20fc36b252fa371c81fb8be03827558c`
- Achados tratados no incremento: CX01–CX06, CX-UI01–CX-UI04, CX-R02 e CX-R03. CX-R01 e CX-R04 foram contraprovas do Codex, verdes.
- Parecer do Codex favorável a todos os deltas de código, até `605b9ff`, e ao commit de testes de cobertura `9e7b686` (registro de 10:48Z).
- CI do PR #32 em `1f0817a`, conferida pelo Codex: 8 de 10 checks verdes, inclusive cobertura, integração com PostgreSQL, build e jornadas de navegador; seguem vermelhos Imagens (as 2 HIGH de `libssl3t64`) e Gitleaks (ref gen37, conserto no PR #31).

## Contraprovas por mutação
Cada mutação altera o código de produção numa cópia descartável e roda os testes do bloco; "detectada" = algum teste ficou vermelho.
- `aquisicao-77d8912/correcao-testes-e732d1a/mutacoes.json`: 2/2 detectadas.
- `aquisicao-77d8912/mutacoes.json`: 8/8 detectadas.
- `cmd15-efeito-mutacoes.json`: 6/6 detectadas.
- `cmd15-nucleo-cx-mutacoes.json`: 11/11 detectadas.
- `cmd15-nucleo-mutacoes.json`: 8/8 detectadas.
- `cobertura-9e7b686/mutacoes.json`: 4/4 detectadas.
- `cxr-28874bd/mutacoes.json`: 2/3 detectadas. Não detectada, declarada como equivalente: erro ouvido não retira a conexão.
- `mutacoes-efeito-cx04-06.json`: 8/9 detectadas. Não detectada, declarada como equivalente: sem validação da unidade pelo lote.
- `mutacoes-http.json`: 10/10 detectadas.
- `mutacoes-leitura.json`: 6/6 detectadas.
- `mutacoes-validade-nula.json`: 3/3 detectadas.
- `origem-d595285/mutacoes.json`: 3/3 detectadas.
- `retry-7e79ecc/mutacoes-retry.json`: 9/9 detectadas.
- `tela-343eacc/mutacoes-unit.json`: 8/8 detectadas.
- `tela-fix-78409d3/mutacoes-unit.json`: 5/5 detectadas.
- `trava-0c74bad/mutacoes.json`: 3/3 detectadas.
- `trava-0c74bad/rollback-62f0c23/mutacoes.json`: 1/1 detectadas.
- `ui04-9b80d35/mutacoes-unit.json`: 2/2 detectadas.
- Mutações de tela (E2E): 8/9 detectadas. `tela-fix-78409d3/mutacao-e2e-C.txt` passou verde: declarada equivalente e trocada por mutação fiel na unidade.

## Limites
- Local, não CI. Login DEV, não OIDC. Sem HML e sem aparelho físico: o celular é emulação do Playwright.
- O 40P01 dos casos de repetição é injetado por gatilho; só um caso é deadlock natural.
- O filtro `status = 'confirmado'` da consulta por origem ainda não tem teste de estorno, que chega no incremento 3.
- Nos formulários guardados, o motivo da recusa se perde depois da segunda troca entre formulários (limite declarado).
- p95 local INCONCLUSIVO (seção acima); o válido é em HML. A janela de 2 s limita a repetição, não a duração de qualquer comando (contrato §6, v3.9).
- Imagens: o Trivy da CI acusa 2 HIGH em `libssl3t64` (CVE-2026-75804, CVE-2026-84782) na base distroless `cc-debian13` fixada por digest no `Dockerfile`; a correção Debian é `3.5.7-1~deb13u3`, e a tag oficial ainda não tinha pin corrigido na consulta do Codex. Retomada: candidata oficial com assinatura e digest verificados, pacote corrigido nos metadados, build, smoke e Trivy das duas imagens.
- Gitleaks: o vermelho do PR #32 vem da ref `claude/prototipo-gen37-fonte` (commit 310844a), alcançada pela varredura de todas as refs; o conserto é o PR #31. Depois de integrado, atualizar a base do #32 e gerar CI nova sobre a combinação.
- Parecer do Gemini e CI verde do PR pendentes antes de qualquer integração.

## Como reproduzir
Pré-requisitos: Node da `.nvmrc`, pnpm do `packageManager`, um PostgreSQL 17 descartável com usuário administrador, e Chrome.

```bash
pnpm install
pnpm run typecheck && pnpm run lint && pnpm run format:check
pnpm run test
SAFRION_TEST_DATABASE_URL=postgresql://admin:SENHA@127.0.0.1:5432/postgres pnpm run test:integration
pnpm run build
SAFRION_TEST_DATABASE_URL=postgresql://admin:SENHA@127.0.0.1:5432/postgres pnpm run test:e2e
```

Cada arquivo de integração cria e apaga o próprio banco. Na CI, o mesmo roteiro está em `.github/workflows/ci.yml` (integração) e `navegador.yml` (E2E).
