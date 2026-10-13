# CADUX-R · Requisitos dos Cadastros (CD-01 a CD-07) para o redesenho

```text
ID / resultado útil / persona: CADUX-R · o que o PRD e as decisões exigem de cada tela de Cadastros, o que o protótipo já cumpre e o que um redesenho não pode perder · gestor de dados, agrônomo, PCM, compras, controladoria
Requisitos do PRD e fora do escopo: CD-01..CD-07, CF-01..CF-05 (no que toca cadastro), RN-003/005/014/016/018/021/032/033/036/037/042/043/044, FO-01, FO-21..FO-26, FO-28, FO-40, RF-DAT-001..009, cap. 4, 6, 43, 52, 60, 72 (DEC-2609-*), 74 e 75.4; DEC-0510-02/03. Fora: código (esta etapa só documenta), desenho das telas, regras de outros módulos
Autor / revisor / integrador: Claude / Codex / Claude
Base (commit ou hashes) / arquivos sob responsabilidade: claude/v44-cadux @ 98028b0 · PRD v3.11 = docs/PRD.md da main @ 266a682 · arquivo: docs/cadastros-ux/REQUISITOS.md
Aceite e comando de verificação: cada linha tem ID e evidência; 15 testes de navegador dos Cadastros rodados nesta etapa (seção 1): 310 de 310 verificações OK
Estado / impedimento / próximo passo: executado (leitura do PRD e do código; testes rodados) · sem impedimento · próximo: desenho das telas sobre a TABELAS-FOCO e a DS, respeitando a seção 4
```

**Pedido do proprietário (09/10/2026):** "os cadastros ainda não estão intuitivos com melhor UX e UI. faça algo mais prático e intuitivo. E use seleção para abrir detalhes... como clicar na fazenda e abrir talhões cadastrados nela na tela."

## Como ler

- **Contrato.** PRD v3.11. Ele passou a ser a versão vigente na main com o merge do PR #48 (266a682, 09/10/2026 10:24), depois do início desta frente. Esta worktree ainda tem o AGENTS.md que cita a v3.9. Por isso, toda regra que não existe na v3.9 leva a marca **[v3.10]** ou **[v3.11]**. Ela estava "em revisão" quando a frente começou e hoje está vigente. Continuam pendentes, sem valor de aprovação: 73.12, 74.12 (PEND-DS) e 75.8. A diferença entre as versões foi apurada por `diff` entre o `docs/PRD.md` v3.9 (main @ 5d6fce2) e a v3.11. Nas seções lidas, CD-01 a CD-07 e o cap. 72 não mudaram; mudaram 2.1, RN-001/007/009/011/035/038/046/047, 4.2, 4.3, FO-40, FORM-09/13/15, RF-DAT-007, 11.1, 43.2 e 60.3 (CADN-07 a 11). Os cap. 73, 74 e 75 são novos.
- **Protótipo.** Cada linha leva uma marca:
  - **Cumpre**;
  - **Parcial**;
  - **Não**;
  - **Simulado**: a tela mostra, mas não calcula ou não lê arquivo;
  - **N.v.**: não verificado.
- **Evidência:**
  - `arquivo:linha` = código lido em `tools/prototipo/v37/gen37/areas/`, salvo outro caminho indicado;
  - `teste n` = verificação n de um teste de navegador rodado nesta etapa (seção 1);
  - `Inn` = achado medido no [INVENTARIO.md](INVENTARIO.md) (CADUX-0, executado);
  - `Bnn` = decisão do [BENCHMARK.md](BENCHMARK.md).
- **Severidade** (S1 a S4): PRD 22.1. **Prioridade** (P0 a P3): AGENTS §3.

## 0. Resumo

1. **O PRD já pede o que o proprietário pediu.** A regra 4.3 diz: "Linha abre detalhe canônico por clique/teclado". O CD-01 pede "Hierarquia e mapa". O DS-57 e o DS-58 [v3.10] separam a listagem do detalhe. O que puxou para o outro lado foi a DEC-2609-14 com a 71.6 (Tabelas): "clique na linha abre o formulário". O pedido de 09/10 troca isso por "seleção abre detalhes". É preciso registrar essa mudança (seção 6, D1). Este documento não aprova nenhum desenho em nome do proprietário.
2. **O protótipo já tem controles sólidos, e eles estão testados.** 15 testes, 310 de 310 verificações OK:
   - área da fazenda e área alocada em parcelas;
   - área cultivável × polígono, com motivo acima de 1 %;
   - versões do polígono, sem mexer nas O.S. já emitidas;
   - habilitação vencida grava, mas a pessoa fica "Não alocável em O.S.";
   - condição técnica do ativo só leitura, vinda da Manutenção;
   - CPF/CNPJ único com "Abrir e ativar papel";
   - homologação de fornecedor com grupo, contato e e-mail autorizado;
   - unidade-base travada quando o item tem saldo ou plano;
   - saldo fora do cadastro;
   - rascunho × versão em vigor na estrutura gerencial;
   - inativar em vez de excluir.

   A seção 4 lista os 28 controles que o redesenho tem de manter.
3. **Há lacunas de contrato que não são de UX** (seção 5). O redesenho não deve escondê-las:
   - registro do produto e composição [v3.11];
   - conversões de unidade;
   - contador com histórico;
   - código, série, propriedade e componentes do ativo;
   - dados bancários com verificação;
   - biblioteca e importação de planilha;
   - trilha de auditoria;
   - custo-hora visível a todos;
   - versão do padrão de rendimento;
   - dividir e unir talhão;
   - sobreposição e perímetro apenas simulados;
   - outorga em duas fontes.
4. **Design system [v3.10] que o desenho deve seguir:**
   - painel de 460 px para editar e de 820 px para consultar (DS-41);
   - até 7 colunas, e lista de cartões no celular (DS-57);
   - cabeçalho "O que é · Onde · Estado · Quem resolve · Prazo" (DS-58);
   - estado vazio com ação (DS-45);
   - seleção rápida, que nunca lembra lote, dose, quantidade ou autorização (DS-88);
   - talhão como botão focável no mapa (DS-52).
5. **Três pontos para não errar:**
   - Cadastros não têm seletor de fazenda no topo (DEC-2609-11): a fazenda se escolhe no conteúdo;
   - o rótulo "Liberar O.S. (agrônomo)" contradiz a DEC-2609-05;
   - a saca de 60 kg é a única opção de unidade de mercado. A DEC-0510-03 pede o kg por saca explícito, e o estudo `docs/culturas/UNIDADES-DE-MERCADO.md` mostra saca de 50 kg (arroz em RS e SC) e de 25 kg (amendoim).

## 1. Como verifiquei (executado)

```bash
cd /home/user/sp-cadux/tools/prototipo/v37/gen37      # _render montado pelo CADUX-0 em 8356a07; código igual em 98028b0 (git diff só em docs)
CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpH.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 300 python3 <teste>
```

| Teste | Tela | Resultado |
|---|---|---|
| `cadf_test.py` | CD-01 | OK 15/15 |
| `cadf_fix_lista_test.py` | CD-01 | OK 11/11 |
| `cadf_det_test.py` | CD-01det | OK 13/13 |
| `cadf_fix_det_test.py` | CD-01det | OK 9/9 |
| `cadc_cd02_test.py` | CD-02 | OK 15/15 |
| `cada_cd03_test.py` | CD-03 | OK 14/14 |
| `cada_fix03_test.py` | CD-03 | OK 11/11 |
| `cada_cd04_test.py` | CD-04 | OK 15/15 |
| `cada_fix04_test.py` | CD-04 | OK 12/12 |
| `cadp_test.py` | CD-05 | OK 15/15 |
| `cadp_vtest.py` | CD-05 | OK 12/12 |
| `cadp_fix_test.py` | CD-05 | OK 15/15 |
| `cadc_cd06_test.py` | CD-06 | OK 14/14 |
| `cadc_cd07_test.py` | CD-07 | OK 14/14 |
| `tabelas_cad_test.py` | CD-01..07 (uma variável por coluna) | 125/125 ok |

- Nenhum teste alterou arquivo versionado.
- As capturas que os testes gravam em `_probe/` foram tiradas da worktree.
- Os logs ficam no scratchpad (`cadux/req/`), que não persiste.
- É emulação no Chrome headless. Não substitui aparelho físico, teclado real nem leitor de tela.

## 2. Regras que valem para todas as telas de Cadastros

### 2.1 Navegação, lista e detalhe (cap. 4, 20.2, 68.2, 71.6, 72)

| Regra (ID) | O que exige | Protótipo | Evidência |
|---|---|---|---|
| 4.1 | Cadastros na base do menu, com os 7 destinos diretos | Cumpre | menu do protótipo (ui37 `MENU2`) |
| 4.2 · DEC-2609-11 | Cadastros **sem** seletor de fazenda ou safra no topo: o cadastro vale para todas as fazendas | Cumpre | o `MACRO` de `gen37/ui37.py:236-243` não tem CD-*, e `_macro_html` não desenha nada para elas |
| 4.2 | Voltar conserva filtros, seleção e posição | Não | I25 |
| 4.2 | Busca global por ID, talhão, ativo, pessoa e parceiro | Não | `search=False` nas 8 cascas (I28); a busca da grade não acha pelo nível de cima (I27) |
| 4.2 · 68.2 | Detalhe com origem, versão, responsável, prazo e estado, mais a faixa Veio de → Está aqui → Falta → Próxima ação | Não | só o CD-01det tem detalhe, e sem faixa (I08, I10) |
| 4.2 · 74.8.1 | Um primário por contexto; o verbo diz o efeito; lançador ≠ execução | Parcial | uma primária por aba; o mesmo verbo na faixa e na linha (I14); "Salvar" genérico |
| 4.3 | Ordenar, filtrar por valores existentes, filtro textual, intervalo, "+ Agrupar por", "N de M", subtotal só de medida aditiva | Parcial | ordena, valores com contagem, "N de M"; subtotal por fazenda sem total geral (`cadf_test` 1). Faltam intervalo e agrupamento (CORR-DS-46 [v3.10]) |
| 4.3 | Até 7 colunas úteis; o resto vai para o detalhe | Não | 6 grades com 8 a 11 colunas (I35) |
| 4.3 | A linha abre o **detalhe canônico**; checkbox, link e botão na linha não abrem | Parcial | a linha abre o formulário (71.6 e DEC-2609-14); a linha da fazenda não faz nada (I02) |
| 4.3 | A lista localiza; o detalhe compreende; formulário curto em painel; processo em página | Parcial | ver é editar (I09); o caminho vai da lista ao formulário e só depois ao detalhe (I10) |
| 4.3 · 20.2 | Estados: vazio com próximo passo, sem resultado, sem permissão, erro | Parcial | I29, I30 |
| 4.3 · 4.4 | Celular: controles equivalentes sobre uma lista de cartões | Não | 2 colunas a 390 px; a Situação fica fora (I31) |
| 4.3 | WCAG 2.2 AA; alvo de 44 px nas ações de campo | Parcial | contraste do chip do CD-05 (I37); teclado e leitor de tela N.v. |
| 71.6 (Tabelas) | Linha ou Enter abre o formulário lateral; a seta só expande | Cumpre hoje | **muda com o pedido de 09/10** (seção 6, D1) |
| DEC-2609-08 | Painel rola inteiro; tabela não corta | Parcial | o painel rola (`cadf_fix_det` 8); há colunas fora da caixa (I35) |
| DEC-2609-14 | Uma ação primária por tela; criação só com o essencial; inativar em vez de excluir | Cumpre | testes das 7 telas (seção 4, E) |
| RN-042 · 4.6 | Atalho abre o mesmo registro e conserva o contexto | Parcial | os links para SAF, EST e OS saem sem o registro (I24) |
| RN-045 | Função fora do perfil não aparece como pendência | N.v. | os Cadastros não usam perfil de demonstração |

### 2.2 Formulários (cap. 6)

| Regra (ID) | O que exige | Protótipo | Evidência |
|---|---|---|---|
| 6 (cabeça) · FORM-11 | Herdar empresa, fazenda e origem; o calculado é identificado e não se digita de novo | Parcial | condição técnica, polígono e "Capacidade do silo" só leitura; "Cadastrar talhão" na barra pré-escolhe a 1ª fazenda (I23) |
| 6 (cabeça) · FORM-04 | Rascunho aceita o incompleto; confirmar exige o que a etapa pede | Parcial | só o CD-07 tem rascunho; os outros salvam direto |
| 6.2 · FORM-08 | Erro junto ao campo; o que foi digitado fica | Cumpre | "o que você preencheu foi mantido" (`cada_cd04` 6, 13; `cadf_test` 2) |
| 6.2 | Cadastro rápido no contexto, com campos mínimos | Cumpre | "Cadastrar fazenda…" (`cadf_test` 9), "Outra cultura…", "Outra operação…", "Outro grupo…" (`cadc_cd02` 6, 12; `cadc_cd06` 10) |
| 6.2 · FORM-10 | Registro inativo continua no histórico e como valor antigo, mas não é opção nova | Cumpre | fazenda inativa sai das opções e o valor antigo fica (`cad_fazendas.py:437`, `:699`) |
| 6.2 · DS-42 [v3.10] | Obrigatório indicado antes da tentativa ("(opcional)" e `aria-required`) | Não | CORR-DS-48 |
| 6.2 · DS-88 [v3.10] | Lista curta: um toque. Catálogo: busca paginada. Data: atalhos | Não | selects nativos de 2 a 11 opções; seletor de talhão com 32 opções (I08, I36) |
| 6.2 · FORM-06 | Número com unidade visível e vírgula decimal | Cumpre | unidade como sufixo; `g2lib.js:126` |
| 6.3 · FORM-05 | Cada coluna tem fonte: informada, herdada, calculada, evento ou externa | Parcial | condição técnica "Vem da Manutenção"; saldo fora do cadastro (`cadc_cd06` 2) |
| FORM-02 | Referência por ID, não pelo nome digitado; homônimo com código | Parcial | o valor padrão segue o id (`cad_culturas.py:46`); o talhão é identificado pelo nome dentro da fazenda |
| FORM-03 | Trocar a fazenda revalida as dependências sem apagar | Cumpre | parcelas impedem trocar de fazenda (`cad_fazendas.py:168-169`; `cadf_fix_lista` 5) |
| FORM-07 | Perfil sem autorização não vê dado sensível | Não | custo-hora visível na lista do CD-04 (seção 5, L04) |
| FORM-09 [v3.10] | Chave de idempotência por intenção; conflito de versão | N.a. no protótipo | obrigatório no produto (IDEM-02, IDEM-03) |
| FORM-15 [v3.10] | Importar com prévia, erros por linha e "Aplicar a N linhas" | Não | não há importação de planilha (2.4) |

### 2.3 Regras de negócio que atravessam os cadastros (cap. 3)

| RN | O que exige no cadastro | Protótipo | Evidência |
|---|---|---|---|
| RN-003 | Empresa, versão e origem em cada registro; rastreio nos dois sentidos | Parcial | fazenda com empresa; versão só no polígono e no CD-07 |
| RN-005 | Geometria, área física e área plantada são distintas; versões preservam o histórico | Cumpre | área cultivável × polígono; v3 em consulta (`cadf_det` 9) |
| RN-014 | Consignação tem proprietário | Não | o CD-06 não tem proprietário |
| RN-016 | Registro e bula, carência, reentrada e captação não aceitam justificativa | Parcial | outorga com situação na aba Água (`cad_fazendas.py:326`); o registro do produto não está no cadastro (L01). A trava legal fica na O.S. (CTL-1; AGROFIT em `agronomia.py:936`) |
| RN-018 | Fato ocorrido pode ser registrado, mesmo fora da regra | Cumpre | habilitação vencida grava como "Não alocável" (`cada_cd04` 7, 14) |
| RN-021 | Uma condição por ativo, compartilhada | Cumpre | só leitura, vinda da OM-0233 (`cada_cd03` 4) |
| RN-032 | Dado ausente não é zero | Cumpre | "—", "Sem preço", "sem polígono" |
| RN-033 · DEC-0510-02 | Toda quantidade tem unidade; unidade na célula | Cumpre | `tabelas_cad_test` 125/125 |
| RN-036 | Um escritor por entidade; ERP e sistema agrícola sem saldo paralelo | Cumpre | o CD-07 só traduz; saldo nunca no cadastro (`cadc_cd06` 2) |
| RN-037 | Mudança vale para a frente; o histórico guarda a regra aplicada | Parcial | Cumpre no CD-07 (`cadc_cd07` 13) e no polígono (`cadf_det` 9). Não no rendimento do CD-02 (L05) |
| RN-043 | Valor de demonstração não vira padrão | Cumpre | rótulos "simulado" e "Premissa a validar" |
| RN-044 | Alteração material guarda causa, autor, versão e impacto | Não | sem trilha (L03); polígono e CD-07 têm versão e data, sem autor |
| FX-001..008 (cap. 37) | Sem regra de cadastro. Vale o mesmo princípio de FX-005: falta de dado bloqueia só o que depende dele | Cumpre | CAR em branco "bloqueia só o crédito rural" (`cad_fazendas.py:120`) |

### 2.4 Bibliotecas, importação e implantação (cap. 60, 58.3, FL-02, FO-40, RF-DAT-007)

| Regra (ID) | O que exige | Protótipo | Evidência |
|---|---|---|---|
| 60.1 | Três camadas: referência global, seleção da organização e fatos. Comandos "Adicionar da biblioteca", "Importar meus dados", "Revisar sugestões" e "Cadastrar diferente". Campos avançados recolhidos | Não | não há biblioteca; o formulário mostra todos os campos (B19, B36) |
| 60.2 | Fontes: RNC/CultivarWeb, AGROFIT, GS1 e IBGE (localidades) | Parcial | cultivar "RNC · referência" sem número (`cad_culturas.py:80`); município em texto livre (`cad_fazendas.py:110-113`) |
| 60.3 · CADN-01..06 | Item global com ID estável, fonte, data e versão; entidade, formulação e embalagem separadas; ajuste local como diferença | Não | — |
| 60.3 · RF-DAT-007 | CSV/XLSX com mapeamento salvo, prévia, duplicidade e erro por linha; idempotente; reversível sem dependências | Não | CD-07: importação do ERP Simulado, com prévia (`cadc_cd07` 10-12) |
| 60.3 · CADN-07..11 [v3.10] | Correção por causa ("Aplicar a N linhas") e revalidação antes de publicar | Não | — |
| FO-40 · M-10 | Importar geometria com unidade, CRS, parser, hash e prévia antes de gravar o FO-01 | Simulado | prévia de área e diferença (`cadf_det` 8, 12); nenhum arquivo é lido (`cad_fazendas.py:643`); sem CRS nem hash |
| 58.3 | Começar com fazenda, cultura e área aproximada; área aproximada não vira área executável sem validação | Parcial | o talhão nasce sem polígono, e a taxa variável fica bloqueada (`cad_fazendas.py:540`) |
| FL-02 | Base utilizável com as lacunas à vista; documento ausente bloqueia só o processo dele | Cumpre | faixa "precisa de atenção" e chip "Documento pendente" (`cad_fazendas.py:322-334`) |

### 2.5 Permissões, alçadas, integrações e auditoria (2.1, CF-01 a CF-05)

| Regra (ID) | O que exige nos cadastros | Protótipo | Evidência |
|---|---|---|---|
| 2.1 | Papel + escopo + ação + valor + vigência; ninguém amplia o próprio acesso; o servidor decide | N.v. | não há perfil nos Cadastros; no produto, é obrigatório no servidor |
| CF-01 · CD-04 | Pessoa ≠ usuário; "Solicitar acesso" vai ao CF-01 | Cumpre | "Sem login" é o padrão; o pedido é simulado (`cada_cd04` 10-12) |
| CF-02 · 52.4 | Quem publica padrão de rendimento e estrutura gerencial | Parcial | o CD-07 publica versão; o rendimento do CD-02 é editado direto (L05) |
| CF-02 [v3.10] | Nenhuma regra aprova ou libera O.S. agrícola | Cumpre | nenhum cadastro tem dispensa (APROV-04, 3.2) |
| CF-03 | Integração simulada não aparece como online | Cumpre | "simulada · nenhum dado real é lido" (CD-07) |
| CF-04 | Trilha: objeto e versão, autor, revisor, antes e depois, motivo, instante e fuso, origem | Não | L03 |
| CF-05 · FO-41 | Área contratada sem duplicar; inadimplência não apaga dado | Cumpre | talhão novo ou reativado é barrado pela assinatura, sem apagar nada (`cad_fazendas.py:166`, `:442`) |

### 2.6 Design system (cap. 74 [v3.10]) e produtividade (75.4 [v3.10])

| ID | O que exige | Protótipo | Evidência |
|---|---|---|---|
| DS-01 | Estado com palavra e sinal que não depende de cor | Cumpre | chip com ponto |
| DS-02 | Um primário por contexto | Parcial | I14, I17 |
| DS-05 | Número tabular, à direita, com a unidade junto | Cumpre | grade G2 |
| DS-06 | Bloqueio com causa, quem resolve e atalho | Parcial | causa e quem resolve nos erros ("Tire-as no Planejar safra antes de inativar"); sem atalho |
| DS-07 | Contexto visível sem rolar | Não a 390 px | I32 a I34 |
| DS-40 | Grade G2: filtro de 24 × 24, intervalo, "Agrupar por", total aditivo | Parcial | CORR-DS-46 |
| DS-41 | Painel: 460 px para formulário, 820 px para consulta, 1060 px para comparação; Esc, × e véu; foco preso e devolvido | Parcial | só 460 px (CORR-DS-31); Esc e × no painel do polígono (`cad_fazendas.py:492`); foco N.v. |
| DS-45 | Vazio com ação; "Nenhum {item} encontrado" e "+ Novo" só com permissão | Não | I29, I30 |
| DS-52 | Talhão é botão focável com nome; há alternativa em lista | Parcial | polígonos clicáveis num SVG `role="img"`, sem foco (`cad_fazendas.py:230`); a árvore é a alternativa |
| CORR-DS-18/20 | Cores do mapa do cadastro vêm dos tokens, iguais às do IN-04 | Não | hex literais (`cad_fazendas.py:393`) |
| DS-57 | Listagem: até 7 colunas, "N de M", retorno preservado, cartões no celular | Parcial | I31, I35 |
| DS-58 | Detalhe: trilha, Voltar, cabeçalho "O que é · Onde · Estado · Quem resolve · Prazo", Próximo passo com uma ação, origem e histórico no fim | Não | I08 |
| DS-60 | Sub-detalhe em painel sobre o detalhe; fechar devolve ao item | Parcial | parcela em consulta no CD-01det (`cadf_det` 3) |
| DS-71..75 | Verbos de 74.8.1 ("Abrir {objeto}" × "Ver {objeto}"); "Indisponível" × "—"; espaço antes da unidade | Parcial | jargão "Círculo do KML" e "Geometria v3" (I20) |
| DS-88 · UXP-03 | Seleção rápida: busca por nome, código e sinônimo, sem acento; homônimos distintos; **último valor nunca para lote, dose, quantidade ou autorização** | Parcial | I36; os valores iniciais dos campos são fixos (`'def'`), não o último uso |
| UXP-01 | Cinco referências por módulo, com fonte e data | Cumpre | BENCHMARK.md |
| UXP-02 | Cliques e digitação medidos antes e depois, no mesmo cenário | Parcial | linha de base em INVENTARIO §4; o "depois" fica para o desenho |
| PEND-DS-06 | Pontos de quebra: abaixo de 768 px, cartões | Pendente do proprietário | usar a proposta, marcada como proposta (74.1) |

## 3. Requisitos por tela

### 3.1 CD-01 Fazendas, áreas e talhões (e CD-01det)

Contrato:
- Rota `/cadastros/areas`; responsáveis: gestor de dados e agronomia.
- Formulários e requisitos: FO-01, FO-40; RF-DAT-001, RF-DAT-002, RF-EXT-014.
- Capítulos e critérios: cap. 43 (PARC), 39 (SAFRA), 56 (RAST) e 60 (CADN).
- Fluxos: FL-02, FL-R01, FL-R03 e FL-R06.
- Decisões: DEC-2609-01 e DEC-2609-14 (a fazenda é cadastrável, com empresa, município/UF, fuso, área, posse, CAR e matrícula, e os talhões ficam agrupados por fazenda).
- Aceite: AC-72-12.

| Tema | Requisito (ID) | Protótipo | Evidência |
|---|---|---|---|
| Campos da fazenda | Identidade, localização e fuso, unidade de área (FO-01); empresa, município/UF, fuso, área, posse, CAR e matrícula (DEC-2609-14) | Cumpre | `CAMPOS_FAZ` (`cad_fazendas.py:110-127`); fuso sugerido pela UF (`cadf_test` 3); fazenda arrendada pede arrendador, fim do contrato e custo da terra (`cadf_test` 4) |
| Documento | Cadastro básico com documento pendente; a exigência bloqueia só o processo dela (CD-01) | Cumpre | `fazDocs` e `fazPend` (`:322-334`); CAR em branco (`:120`) |
| Documento | Contrato de arrendamento vencido | Parcial (trava a confirmar) | salvar fazenda ativa com fim do contrato no passado é barrado (`:418`). Seção 6, D4 |
| Campos do talhão | Identificação única na fazenda, fazenda, sistema, pivô ou setor, área cultivável, situação | Cumpre | `campos_tal` (`:99-109`); `talErros` (`:162-183`); `cadf_test` 7 |
| Hierarquia | Fazenda → talhão, com subtotal por fazenda e sem total que some fazendas | Cumpre | `cadf_test` 1, 8 |
| Hierarquia | **Selecionar a fazenda abre os talhões dela** (pedido de 09/10; CD-01 "Hierarquia e mapa") | Não | I01, I02 |
| Área | Soma dos talhões ativos ≤ área total da fazenda | Cumpre | `:179-181`; `cadf_test` 7 |
| Área declarada × calculada | Área cultivável × área do polígono, com motivo acima de 1 % (RN-005; FO-01) | Cumpre; o cálculo da área é Simulado | `precisaMotivo` (`:134`); `cadf_det` 8; área de prévia fixa (`:643`) |
| Área | Área cultivável não fica abaixo do alocado em parcelas (43.1; PARC-02) | Cumpre | `:177-178`; `cadf_det` 6 |
| Geometria | Geometria válida, sobreposição justificada, dentro do perímetro (FO-01; RF-DAT-002) | Simulado | as verificações aparecem sempre como "✓" (`:646`) |
| Geometria | Versão do polígono com data e origem; O.S. emitidas ficam na versão delas (RF-DAT-002; RAST-06) | Cumpre (sem autor) | `cadf_det` 9; `cadf_fix_det` 8 |
| Geometria | Salvar só depois da prévia; aviso ao fechar sem salvar | Cumpre | `cadf_det` 7, 12 |
| Geometria | Dividir e unir **talhão** com parentesco e histórico (CD-01; RF-DAT-002; 43.2) | Não | não há ação. A divisão em **parcelas** é no Planejar safra (DEC-2609-01) |
| Parcelas | No cadastro, só consulta, com origem no Planejar safra | Cumpre | `cadf_det` 3-5 |
| Parcelas | Parcela sem polígono é área declarada; taxa variável bloqueada; nada de limite inventado (43.1; PARC-06) | Cumpre | `:540`, `:338` |
| KML | Importar KML ou GeoJSON com prévia, CRS e hash (FO-40) | Parcial | os pivôs da Lagoa Grande vêm da camada sintética como "Círculo do KML", marcado Estimado (`:72`, `:627-628`); "Importar KML ou GeoJSON ›" leva ao IN-04 (`:544`); sem CRS nem hash |
| Ambiental e água | Reserva legal, APP e pontos de água da fazenda, em consulta e com a origem | Cumpre | abas Ambiental e Água; "categorias de APP se sobrepõem (não somar)" (`:282`) |
| Ambiental e água | Outorga com situação de vigência (RN-016, captação) | Cumpre; fonte duplicada | `aguaSit` (`:326`). A Irrigação tem outra tabela (`dados_irrigacao.py:40-46`); L12 |
| Irrigação | Um pivô irriga um só talhão ativo; o sistema combina com o setor | Cumpre | `:172-175`; `cadf_test` 7 |
| Exclusão lógica | Inativar sem excluir (RF-DAT-001): o inativo sai do Planejar safra e do Mapa e o antigo continua consultável; talhão com parcela em safra aberta não inativa; fazenda com talhão ativo não inativa | Cumpre | `cadf_test` 11-13; `cadf_fix_det` 5; `:182`, `:417` |
| Identidade | Renomear não rompe vínculos (RF-DAT-001) | Parcial | mapa e padrões ligados por id (`:215`); o talhão é achado pelo nome dentro da fazenda |
| Ligações | "Vincular ciclo → PL-01" com o contexto | Parcial | "Planejar Tn na safra" abre o SAF sem o talhão (I24) |
| Assinatura | Talhão novo ou reativado não amplia a área com a assinatura inadimplente (CF-05) | Cumpre | `:166`, `:442` |
| Mapa | Paleta operacional dos tokens (74.7); talhão focável (DS-52) [v3.10] | Não | 2.6 |
| Auditoria | Quem mudou a área, a fazenda ou a situação (RN-044; CF-04) | Não | só a data da inativação (`:454`) |
| Aceite | AC-72-12: cadastrar uma fazenda nova e, em seguida, um talhão nela, sem sair do formulário | Cumpre | `cadf_test` 9 |

### 3.2 CD-02 Culturas, cultivares e operações

Contrato:
- Rota `/cadastros/operacoes`; responsáveis: agronomia e PCP.
- Formulários e requisitos: FO-21, FO-28; RF-DAT-009.
- Capítulos e critérios: cap. 52 (REND-01 a 10), 33.3 (cobertura técnica por cultura) e 60.2 (RNC).
- Decisões: DEC-2609-02, DEC-2609-03, DEC-0510-03; APROV-04 [v3.10].
- Aceite: AC-72-03.

| Tema | Requisito (ID) | Protótipo | Evidência |
|---|---|---|---|
| Campos da cultura | Nome, tipo de ciclo (fixo depois do cadastro) e unidade de produtividade (DEC-0510-03) | Cumpre | `cad_culturas.py:84-87`; `cadc_cd02` 3 |
| Unidade | Unidade de mercado por cultura, com kg por saca explícito; variante por UF (arroz RS/SC em saca de 50 kg; amendoim em saca de 25 kg) | Parcial | `UNID_PROD` só tem saca de 60 kg (`dados_cad.py:30`); ver `docs/culturas/UNIDADES-DE-MERCADO.md` |
| Campos da cultivar | Ciclo, semente vinculada ao CD-06, registro (RNC ou cadastro próprio), situação; cultivar repetida e semente de outra cultura são barradas | Cumpre | `:66-81`; `cadc_cd02` 4-8 |
| Registro | "Registro no RNC é referência, não prova de adaptação local" (60.2) | Cumpre | subtítulo do formulário (`:70`) |
| Registro | Número e data do registro no RNC (60.2) | Não | só o tipo de registro |
| Operação | Processo (etapa de custo, que vai ao CD-07), atividades usuais, "Outra operação…" | Cumpre | `:124`; `cadc_cd02` 10-12 |
| Aprovação | APROV-04 [v3.10]: o cadastro de operação **não tem** opção "sem aprovação" para trabalho no talhão | Cumpre | o formulário só tem processo e atividades (`:124`) |
| Rendimento | Modos "Largura × velocidade" e "Informado"; rendimento = L × V ÷ 10 × eficiência; fonte; vigência; cultura (Todas ou uma); custo por hora (DEC-2609-03; 52.2) | Cumpre | `REND_CAMPOS` (`cadastros.py:426`); `:120-121`; `cadc_cd02` 12 (6,72 ha/h) |
| Rendimento | Mesmos rótulos e regras do formulário da etapa 3-4-5 do Planejar safra (52.1) | N.v. nesta etapa | aceite O17 em `docs/planejar-safra/etapa-unica-3-4-5/ESPECIFICACAO.md:623`; não rodei aqui |
| Duplicidade | O mesmo conjunto não se repete na mesma operação e cultura | Cumpre | `cadc_cd02` 13 |
| Versão | "Criar versão" e "Publicar"; editar o padrão exige papel autorizado e não muda O.S. executada, orçamento-base nem plano publicado (52.4; RF-DAT-009; REND-06) | Não | edição direta, só com "Vigente até" (L05) |
| Real × padrão | "Comparar real" (52.4; REND-09) | Simulado | secundária "Comparar com o realizado" |
| Importação | "Importar catálogo"; biblioteca de operações (60.2) | Não | — |
| Ligações | "Abrir protocolo → AG-05"; "Ver cobertura técnica" por cultura (33.3; 33.9) | Não | — |
| Ligações | A mesma ficha de rendimento em CD-02, PCP, orçamento e máquina (REND-01) | Parcial | o Planejar safra mostra "Padrão do cadastro (CD-02)"; o conjunto do CD-03 mostra o rendimento (`cada_cd03` 13); a cultivar não leva ao rendimento (I07) |
| Exclusão lógica | Cultivar em uso não se exclui: inativa | Cumpre | `:149` |

### 3.3 CD-03 Máquinas, instalações e setores

Contrato:
- Rota `/cadastros/ativos`; responsáveis: PCM e gestores de ativos.
- Formulários e requisitos: FO-22; RF-DAT-006.
- Capítulos: 47.1 (PCM único, hierarquia), 36.5 (perfil do terminal) e 53.
- Regras e decisões: RN-021; DEC-2609-14 (classe, capacidade por classe, custo/h, condição técnica vinda da Manutenção, conjuntos); PCMS-A01 (condição com uma fonte).

| Tema | Requisito (ID) | Protótipo | Evidência |
|---|---|---|---|
| Campos | FO-22: código, classe, fabricante e modelo, número de série, fazenda ou local, propriedade, capacidade com unidade, contadores, componentes, vínculo máquina–implemento, início de uso e custo | Parcial | classe (fixa depois do cadastro), nome, modelo, capacidade da classe, custo/h com fonte, horímetro, calibração e local (`cad_ativos_pessoas.py:100-118`; `cada_cd03` 6-9). Faltam código, série, propriedade, início de uso e componentes (L07) |
| Condição | Só leitura, vinda da OM; uma fonte (RN-021; PCMS-A01) | Cumpre | `cada_cd03` 2, 4, 12 |
| Contador | Configurar contador; troca de medidor mantém o histórico (CD-03); horímetro ou km conforme a classe (B15) | Parcial | não regride (`cada_cd03` 5; `cada_fix03`); só o valor atual, sem data nem histórico (`:107`; L06) |
| Calibração | "Registrar calibração": última data e intervalo; vencida aparece na Situação | Cumpre | `:115-117`, `:184-187`; `cada_cd03` 3, 10 |
| Fonte do dado | Dado do fabricante e ensaio da fazenda distinguíveis | Parcial | fonte do custo (Apurado na fazenda, Tabela de referência, Premissa a validar) (`:88`); a capacidade não tem fonte |
| Conjuntos | Máquina + implemento, potência mínima, largura herdada, operadores alocáveis, substituto; ligação com o rendimento | Cumpre | `cada_cd03` 11-13 |
| Instalações | Bombas, pivôs, gotejo, packing, silo e medidores; hierarquia instalação → conjunto → ativo → componente (47.1) | Parcial | as classes existem; não há hierarquia nem componente; os pivôs da Lagoa Grande não estão no CD-03 (`cad_fazendas.py:140`) |
| Máquina conectada | Aba "Terminais e compatibilidade" (36.5; 33.9) | Não | — |
| Exclusão lógica | Inativar; o histórico continua | Cumpre | `:98` |
| Custo | Custo por hora com fonte no lugar do valor do ativo | Cumpre | `cada_cd03` 4, 9 |

### 3.4 CD-04 Pessoas e equipes

Contrato:
- Rota `/cadastros/pessoas`; responsáveis: gerência e administrador autorizado.
- Formulários e requisitos: FO-23; RF-DAT-006.
- Ligações: CF-01; política 2.1.
- Decisão: DEC-2609-14 (habilidades, inclusive caldeiro; habilitações com validade; vencida → "não alocável em O.S." sem bloquear o cadastro).
- Aceite: AC-72-12.

| Tema | Requisito (ID) | Protótipo | Evidência |
|---|---|---|---|
| Campos | FO-23: pessoa ou equipe, função, vínculo, calendário, turno, intervalos e fuso, competências com validade, composição e vigência, custo-hora com encargos (só para quem tem acesso) | Parcial | nome, equipe, habilidades, habilitações com validade, vínculo, admissão, disponível até, calendário, custo e acesso (`cad_ativos_pessoas.py:296-308`). O turno é texto ("seg–sáb · 06–15h"), sem intervalo nem fuso |
| Habilitação | A habilidade pede a habilitação exigida (NR-31, NR-10, NR-12, CREA) | Cumpre | `:29`; `cada_cd04` 9 |
| Habilitação | Vencida ou pendente grava e marca "Não alocável em O.S." (RN-018; DEC-2609-14) | Cumpre | `alocavel` (`:53`); `cada_cd04` 3, 7, 8, 14 |
| Vínculo | Safrista precisa de "Disponível até" | Cumpre | `cada_cd04` 13 |
| Acesso | Pessoa cadastrada não ganha login (CD-04; CF-01; B18) | Cumpre | `cada_cd04` 10-12 |
| Permissão | Custo restrito por permissão; não mostrar remuneração ao operador (CD-04; FO-23; FORM-07) | Não | coluna R$/h na lista (`:312`); a ajuda diz que é restrito (`:305`), mas nada restringe (L04) |
| Dados pessoais | Só o mínimo para a finalidade (FO-23) | Cumpre | sem CPF nem endereço |
| Equipe | Líder, calendário e membros ("Vincular equipe") | Parcial | o painel da equipe não mostra os membros (I04) |
| Rótulo | A habilidade "Liberar O.S. (agrônomo)" | Não | contradiz a DEC-2609-05 ("aprovar não libera; liberar é o CMD-06") (`:27`; L13) |
| Exclusão lógica | Inativar; líder inativo continua visível, com aviso | Cumpre | docstring (`:11`); `cada_fix04` |

### 3.5 CD-05 Parceiros e fornecedores

Contrato:
- Rota `/cadastros/parceiros`; responsáveis: compras, comercial e financeiro.
- Formulários e requisitos: FO-24; RF-DAT-005.
- Capítulos: 46.1 (o CD-05 é o cadastro canônico de clientes; nada de CRM isolado) e 71.6 Compras (fornecedor homologado por grupo, com autorização de canal).
- Decisão: DEC-2609-14 (cinco papéis).
- Aceite: AC-72-12.

| Tema | Requisito (ID) | Protótipo | Evidência |
|---|---|---|---|
| Identidade | Um cadastro por CPF ou CNPJ, com vários papéis; dígito verificador; duplicidade barrada com "Abrir e ativar papel" (RF-DAT-005; AC-72-12) | Cumpre | `cad_parceiros.py:274-276`; `cadp_test` 10-12 |
| Identidade | Filial com identidade própria (RF-DAT-005) | Parcial | cada CNPJ é um parceiro; não há ligação entre matriz e filial |
| Campos por papel | Fornecedor: grupos e homologação. Cliente: produtos, entrega, pagamento, limite e validade. Crédito: linhas, garantias e gerente. Transportador: RNTRC e veículos. Prestador: operações | Cumpre | `:107-137`; `cadp_test` 4-9 |
| Homologação | Exige papel Fornecedor, ao menos um grupo, contato e e-mail autorizado; só o homologado com canal autorizado recebe convite (CD-05; 71.6) | Cumpre | `:278-282`; `cotaveis` (`:219`); `cadp_vtest` |
| Suspensão | Motivo obrigatório; o suspenso sai da cotação e o histórico continua | Cumpre | `cadp_test` 13-15; `cadp_fix_test` |
| Campos ausentes | Culturas, condição do fornecedor, avaliação, documentos, endereços estruturados de entrega e cobrança (CD-05; FO-24) | Não | L08 (I-L3) |
| Pagamento | Mudança de dados bancários passa por verificação (CD-05; FO-24) | Não | não há dados bancários; L08 |
| Portal | "Convidar portal"; acesso externo por escopo (RN-039) | Não | portal oculto no recorte |

### 3.6 CD-06 Produtos, unidades e locais

Contrato:
- Rota `/cadastros/produtos`; responsáveis: suprimentos e controladoria.
- Formulários e requisitos: FO-25; RF-DAT-004.
- Regras: RN-014, RN-015, RN-016 e RN-033.
- Capítulos: 11.1 Materiais [v3.11], 40.5 e SUBST-12 [v3.11], 60.2-60.3, AG-07.
- Decisão: DEC-2609-14 (grupo, embalagem, preço de referência, situação).

| Tema | Requisito (ID) | Protótipo | Evidência |
|---|---|---|---|
| Campos | FO-25: código e nome, categoria, unidade-base, unidades de compra, uso e venda, conversões, lote, série e validade, conservação, local, embalagem, composição e densidade | Parcial | nome, grupo (com natureza), unidade-base, embalagem e conteúdo, controle, preço com data, garantia ou densidade em texto livre, local padrão, situação (`cad_produtos_estrutura.py:92-106`). Faltam código, unidades de compra, uso e venda, conversões e conservação |
| Unidade | A unidade-base trava com saldo ou plano, e o motivo aparece (B24; ENG-013) | Cumpre | `cadc_cd06` 4-5 |
| Saldo | O produto não tem saldo editável; lote e estoque nascem de movimentos (FO-25) | Cumpre | `cadc_cd06` 2 |
| Conversão | "Configurar conversão" e "Validar fator"; fator por item, lote ou contrato; saca de massa não configurada impede a conversão; caixa de peso variável exige peso real (CD-06; RF-DAT-004; 60.3) | Não | só o conteúdo da embalagem na unidade-base (L02) |
| Registro | "Vincular registro → AG-07" (CD-06). O item é um produto comercial registrado, com composição versionada (ingredientes, concentração, base, formulação, registro, bula) e de-para do código do fornecedor (11.1 [v3.11]). Produto fixo = mesmo registro, formulação e concentração (SUBST-12 [v3.11]) | Não | L01 (I-L1) |
| Proprietário | Item ou lote de terceiro (consignação, RN-014; campo "proprietário" do CD-06) | Não | — |
| Embalagem | Compra e retirada em embalagem inteira; o arredondamento aparece como excedente, sem subir a dose (CAL-11; 42.1) | Parcial | conteúdo da embalagem; granel sem conteúdo (`cadc_cd06` 6-8) |
| Preço | Preço de referência com data | Cumpre | `cadc_cd06` 6-7 |
| Identidade | Entidade, formulação e embalagem separadas; não fundir pelo texto (60.3; CADN-03, CADN-09) | Não | item repetido é barrado pelo nome (`cadc_cd06` 11); no produto real, a identidade é registro + formulação + concentração |
| Locais | Local com fazenda e tipo; capacidade do tanque informada; capacidade do silo vinda do ativo | Cumpre | `cadc_cd06` 12-14 |
| Exclusão lógica | O inativo sai dos planos e das cotações; saldo e histórico continuam | Cumpre | `cadc_cd06` 9 |
| Fonte única | Natureza do grupo vem do CD-07; semente da cultivar vem do CD-02 | Cumpre | `cadc_cd06` 3, 10; `cadc_cd02` 14 |

### 3.7 CD-07 Estrutura gerencial

Contrato:
- Rota `/cadastros/estrutura`; responsável: controladoria.
- Formulários e requisitos: FO-26; RF-DAT-008; RF-INT-002.
- Capítulos: 11.3 e 51.1.
- Regras: RN-036 e RN-037.

| Tema | Requisito (ID) | Protótipo | Evidência |
|---|---|---|---|
| Dimensões | Independentes (empresa, natureza, centro, cultura, processo, projeto), sem codificar combinações (11.3; RF-DAT-008) | Cumpre | `cadc_cd07` 2-3 |
| Fonte única | Cultura e Processo vêm do CD-02; aqui só a tradução é editável | Cumpre | `cadc_cd07` 2, 5 |
| Hierarquia | Sem árvore circular; o código superior tem de existir (FO-26) | Parcial | superior inexistente é barrado (`cadc_cd07` 8); ciclo N.v. |
| Vigência e versão | Início e fim; versão em vigor × rascunho; publicar preserva a anterior e vale para novos lançamentos; fatos guardam as dimensões da época (FO-26; RN-037) | Cumpre | `cad_produtos_estrutura.py:271`, `:277`; `cadc_cd07` 6, 13 |
| Exclusão lógica | Código com lançamento não se exclui ("encerre a vigência"); natureza usada em grupos também não | Cumpre | `:315`; `cadc_cd07` 4 |
| ERP | Mapear conta e TOP; código sem conta fica fora da publicação (RF-INT-002) | Cumpre | `cadc_cd07` 13 |
| Importação | "Importar estrutura" com prévia (FO-40) | Simulado | `cadc_cd07` 10-12 |
| Rateio | Regra de apropriação e rateio (FO-26) | Parcial | centro com direcionador (`cadc_cd07` 3, 9) |
| Ações | "Simular relatório" e "Validar vigência" (CD-07) | Não | — |
| Auditoria | Autor da publicação (RN-044) | Não | L03 |

## 4. O que não pode se perder no redesenho

Cada item é controle, rastro ou trava legal. "Dano evitado" segue a regra do AGENTS §4: a trava só fica onde protege algo concreto. Os testes da coluna "Protege" estão verdes hoje. Se um teste quebrar porque o seletor de tela mudou, a regra dele tem de ser reescrita no teste novo. Nunca basta apagar o teste.

| # | Controle | Dano evitado | Onde está | Protege |
|---|---|---|---|---|
| **A** | **Travas legais e técnicas** | | | |
| A1 | Habilitação exigida vencida ou pendente → "Não alocável em O.S.". O cadastro grava, sem bloquear | Operar sem NR-31, NR-10 ou NR-12 válida; perder o registro da pessoa | `cad_ativos_pessoas.py:29`, `:53` | `cada_cd04` 3, 7, 8, 14 |
| A2 | Calibração vencida aparece na situação do ativo | Aplicar com equipamento não aferido | `cad_ativos_pessoas.py:184-187` | `cada_cd03` 3, 10 |
| A3 | Condição técnica só leitura, vinda da Manutenção (RN-021; PCMS-A01) | Alocar máquina em manutenção; duas verdades sobre o ativo | CD-03 | `cada_cd03` 2, 4, 12 |
| A4 | Restrição ambiental e outorga visíveis por fazenda, com a situação de vigência (RN-016, captação) | Irrigar com outorga vencida; somar categorias de APP que se sobrepõem | `cad_fazendas.py:282`, `:326` | `tabelas_cad_test` (CD-01 Água) |
| A5 | Nenhum campo de dispensa de aprovação no cadastro de operação (APROV-04 [v3.10]) | O.S. agrícola executada sem aprovação (S1 pelo AGENTS §3) | `cad_culturas.py:124` | sem teste: criar a verificação de que o formulário de operação não tem campo de dispensa |
| A6 | Registro de cultivar e de produto como referência oficial: a cultivar é "RNC · referência", não prova de adaptação; o registro do produto, quando entrar, é consulta ao AG-07 e nunca valor livre (B25) | Recomendação ou troca de produto sem registro para a cultura e o alvo | `cad_culturas.py:70`, `:80` | sem teste: criar |
| **B** | **Área e geometria** | | | |
| B1 | Soma dos talhões ativos ≤ área da fazenda; área cultivável ≥ alocado em parcelas; parcelas impedem trocar de fazenda e inativar | Área física contada duas vezes; custo por ha e dose errados | `cad_fazendas.py:162-183` | `cadf_test` 7, 11; `cadf_det` 6; `cadf_fix_lista` 5 |
| B2 | Área cultivável × polígono, com motivo acima de 1 % | Área executável diferente da contratada, sem explicação | `cad_fazendas.py:134` | `cadf_det` 8 |
| B3 | Polígono por versão; a nova não muda as O.S. já emitidas; salvar exige prévia; sem polígono não há taxa variável | Reescrever o passado; prescrição sobre limite inventado | `cad_fazendas.py:540`, `:643-665` | `cadf_det` 7, 9, 12; `cadf_fix_det` 8 |
| B4 | "Círculo do KML" é estimativa, não polígono validado (43.1) | Limite fictício usado como real | `cad_fazendas.py:72`, `:627` | `tabelas_cad_test` (pivô PV01: "círculo do KML" na Situação, Polígono "—") |
| B5 | Um pivô irriga um só talhão ativo; o sistema combina com o setor | Lâmina e custo da água atribuídos duas vezes | `cad_fazendas.py:172-175` | `cadf_test` 7 |
| B6 | Subtotal por fazenda, sem total que some fazendas | Comparar bases diferentes (RN-040) | CD-01 | `cadf_test` 1, 8 |
| B7 | Talhão novo ou reativado barrado com a assinatura inadimplente; nada é apagado (CF-05) | Ampliar a área medida sem contrato; perder dado por inadimplência | `cad_fazendas.py:166`, `:442` | `assinatura_test.py`, trava R12 (não rodado nesta etapa) |
| **C** | **Unidade e conversão** | | | |
| C1 | Unidade-base trava com saldo ou plano, e o motivo aparece | Estoque e custo convertidos errado em silêncio | CD-06 | `cadc_cd06` 4-5 |
| C2 | Saldo nunca é editável no cadastro | Saldo sem movimento que o explique | CD-06 | `cadc_cd06` 2 |
| C3 | Unidade na célula, uma variável por coluna, ordenação pelo número (DEC-0510-02) | Ordenar ou filtrar grandezas diferentes juntas | todas | `tabelas_cad_test` 125/125 |
| C4 | Unidade de produtividade da cultura (DEC-0510-03); mudar a preferência não converte o histórico | Meta e produção em base errada; contrato antigo reescrito | `cad_culturas.py:84-87` | `cadc_cd02` 2, 3 |
| C5 | Rendimento: dois modos, fórmula L × V ÷ 10 × eficiência, fonte, e os mesmos campos do Planejar safra | Horas e custo da safra diferentes do cadastro | `cadastros.py:426` | `cadc_cd02` 12; O17 da SAF |
| **D** | **Identidade e duplicidade** | | | |
| D1 | CPF/CNPJ com dígito verificador, único, "Abrir e ativar papel" | Parceiro duplicado; pagamento ou cotação ao cadastro errado | `cad_parceiros.py:274-276` | `cadp_test` 10-12 |
| D2 | Talhão único na fazenda; cultivar única na cultura; conjunto único por operação e cultura; item único | Registros gêmeos que dividem o histórico | CD-01 (`cad_fazendas.py:171`), CD-02, CD-06 | `cadc_cd02` 8, 13; `cadc_cd06` 11. Talhão único na fazenda: sem teste, criar |
| D3 | Homologação exige Fornecedor + grupo + contato + e-mail autorizado; só o homologado com canal autorizado recebe convite | Mensagem a quem não autorizou; cotação a fornecedor não aprovado | `cad_parceiros.py:219`, `:278-282` | `cadp_test`; `cadp_vtest` |
| D4 | Pessoa ≠ usuário: o cadastro não cria login | Acesso concedido sem decisão | CD-04 | `cada_cd04` 10-12 |
| **E** | **Vigência, versão e exclusão lógica** | | | |
| E1 | CD-07: rascunho × em vigor; publicar preserva a anterior; a mudança vale para novos lançamentos | Custos do passado reclassificados | CD-07 | `cadc_cd07` 6, 13 |
| E2 | Inativar, suspender ou encerrar a vigência em vez de excluir; excluir só sem dependência, com confirmação e a causa à vista | Histórico órfão; O.S. antiga sem talhão | `cadastros.py:290` | `cadf_test` 12-13; `cadc_cd06` 9; `cadc_cd07` 4; `cadp_test` 13-15 |
| E3 | Parcelas só em consulta no cadastro; editar no Planejar safra (DEC-2609-01) | Duas portas para a mesma parcela | CD-01det | `cadf_det` 3-5 |
| E4 | Aviso de alteração não salva ao fechar o painel | Perder o que foi digitado | `cad_fazendas.py:492` | `cadf_det` 12 |
| **F** | **Fonte única entre módulos** (RN-042; não pedir o mesmo dado duas vezes) | | | |
| F1 | Cultura e processo (CD-02) → CD-07; grupo (CD-06) → cotação e homologação (CD-05); semente da cultivar → item do CD-06; custo/h do ativo → rendimento; habilidade → operadores do conjunto | O mesmo dado digitado em dois lugares, com dois valores | CD-02, CD-03, CD-05, CD-06, CD-07 | `cadc_cd02` 14; `cadc_cd07` 2; `cada_cd03` 13 |
| **G** | **Permissão** (obrigatória no produto) | | | |
| G1 | Custo-hora e dado pessoal só para quem tem permissão. Hoje não cumpre (L04); o painel de consulta novo **não pode** ampliar a exposição | Acesso indevido a remuneração | CD-04 | a criar no produto (FORM-07) |

## 5. Lacunas de contrato (registrar; o redesenho não as resolve sozinho)

Todas valem para o protótipo com dados sintéticos. No software real, viram requisito do backlog.

| ID | Lacuna | Requisito | Sev. · Prior. | Encaminhamento |
|---|---|---|---|---|
| L01 | O item não tem registro, composição nem de-para do fornecedor | CD-06 "Vincular registro → AG-07"; 11.1 e SUBST-12 [v3.11] | S3 · P1 | O desenho reserva o lugar ("Registro e bula", em consulta ao AG-07). A trava legal continua na O.S. (CTL-1) |
| L02 | Sem conversões de unidade versionadas | CD-06; RF-DAT-004; FO-25 | S3 · P1 | O cálculo de conversão fica num serviço de domínio único (ENG-011), não na tela |
| L03 | Cadastros sem trilha (autor, antes e depois, motivo) | RN-044; CF-04 | S3 · P2 | O detalhe novo reserva "Histórico" no fim (DS-58) e mostra só o que existe (versões do polígono e do CD-07) |
| L04 | Custo-hora visível a qualquer um | CD-04; FO-23; FORM-07 | S3 no protótipo (dados sintéticos); no produto seria acesso indevido · P1 | Esconder na consulta para perfil sem custo quando o protótipo tiver perfil nos Cadastros |
| L05 | Padrão de rendimento sem versão. Editar no CD-02 não muda as safras, que têm grade própria (`safra.js:30`); não verifiquei se chega a uma safra nova | 52.4; RF-DAT-009; REND-06 | S3 · P2 | Decidir com a frente SAF |
| L06 | Contador só com o valor atual; troca de medidor só como texto | CD-03 | S3 · P2 | Frente PCM simplificado |
| L07 | Ativo sem código, série, propriedade, componentes e perfil de terminal | FO-22; 47.1; 36.5 | S3 · P2 | Campos avançados recolhidos (60.1) |
| L08 | Parceiro sem dados bancários com verificação, documentos, avaliação, culturas e endereços estruturados | CD-05; FO-24 | S3 · P2 | O dado bancário só entra no software real, com verificação |
| L09 | Sem biblioteca nem importação de planilha com prévia por linha | 60; RF-DAT-007; CADN-01 a 11 | S3 · P2 | B09, B19 |
| L10 | Não dá para dividir ou unir talhão com linhagem | CD-01; RF-DAT-002; 43.2 | S3 · P3 | — |
| L11 | Sobreposição, perímetro e área do polígono simulados | FO-01; RF-DAT-002 | S3 · P2 | No produto, cálculo com PostGIS; o protótipo mostra "simulado" |
| L12 | Outorga em duas fontes: aba Água do CD-01 e captações da Irrigação (`dados_irrigacao.py:40-46`) | RN-016; RN-036 | S2 (classificado em `docs/controle-01/PLANO.md:36`, CTL-3/E3) · P0 naquela frente | O redesenho não cria uma 3ª fonte; a consolidação é do CONTROLE-01 |
| L13 | Habilidade "Liberar O.S. (agrônomo)" | DEC-2609-05; AGENTS §4 | S3 · P1 | Renomear para "Aprovar O.S. (agrônomo)" no redesenho; conferir quem usa o rótulo |
| L14 | Unidade de produtividade só com saca de 60 kg | DEC-0510-03 (kg por saca explícito); `docs/culturas/UNIDADES-DE-MERCADO.md` (saca de 50 kg no arroz de RS e SC; 25 kg no amendoim) | S3 · P2 | Saca com kg explícito por cultura e UF |

## 6. Decisões que o desenho precisa registrar antes de valer

| ID | Tema | Situação | Proposta |
|---|---|---|---|
| D1 | "Seleção abre detalhes" (pedido de 09/10) × "clique na linha abre o formulário" (DEC-2609-14; 71.6 Tabelas) | A DEC-2609-14 prevalece sobre a 4.3 desde 26/09 (72.1). O pedido de 09/10 volta à 4.3 ("detalhe canônico") | Registrar como decisão do proprietário de 09/10, com o texto literal do pedido, em `docs/DECISIONS.md`, e ajustar a 71.6 e a DEC-2609-14 por PR. Editar continua a um clique ("Editar" no detalhe). A forma exata é proposta técnica, a validar com ele no protótipo |
| D2 | Escolher a fazenda nos Cadastros | A DEC-2609-11 tira o seletor do topo | A fazenda se escolhe no conteúdo (lista de fazendas → talhões dela, B01). Não pôr seletor no topo sem nova decisão |
| D3 | Pontos de quebra no celular | PEND-DS-06 pendente | Usar a proposta (lista de cartões abaixo de 768 px), marcada como proposta (74.1) |
| D4 | Contrato de arrendamento vencido barra salvar a fazenda ativa (`cad_fazendas.py:418`) | Pode ser mais forte que "a exigência documental bloqueia só o processo aplicável" (CD-01) | Perguntar ao proprietário (é realidade da fazenda): contrato em renovação continua operando? Até a resposta, manter a trava e mostrar a causa |
