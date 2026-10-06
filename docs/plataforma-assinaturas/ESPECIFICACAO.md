# Plataforma de assinaturas · especificação (PLAT-01)

**Pedido do proprietário (Adrianus, 05/10/2026):** "adicione configurações e plataforma de assinaturas na ordem mais correta possível de prioridade". Diretriz permanente: essencialismo, uma ação primária por tela, tudo no mesmo estado, sem redigitação.

**Rótulos.** Tudo é **especificado**, salvo o marcado **executado**. A implementação de 06/10 está na §11. Base `9c617c4`, branch `claude/v44-plataforma`. Autor: Claude. Revisor: Codex. Decisões tomadas sem o proprietário: `DECISOES.md` (PLAT-D01..D20). Revisão por contraexemplo de 06/10 (Claude, não substitui a do Codex): §10.

**Executado (leitura e sondas, 05–06/10):**
- Leitura de `gen37/areas/onboarding_backoffice.py` (BO-01..04 e detalhes), `areas/configuracoes.py:24-33, 469-553` (CF-05, CF-05det), `ui37.py`, `engine.py:1427-1449`, `cenario.py`, `cenario.js`, `talmapa.js`, `areas/cad_fazendas.py` (`talErros` :154, Reativar :647), `areas/inicio.py:484-488` (`_cad0`), `dados_cad.py`, `build.py`, `montar_render.py`, `varredura.py`, `acao_unica_test.py`, `catalogo.json` (BO-01..04, CF-05); PRD 5 (BO-01..04, CF-05), 18.1, 18.3, 57.2, 57.5, 57.6, 58.1, 58.4, 70.4 (DEC-01/05/09).
- `python3` com `Decimal` sobre os cadastros: Santa Rita 1.165 ha (8 talhões) + Boa Vista 120 ha (B1) + Lagoa Grande 1.285,23 ha (23 pivôs da demonstração sintética) = **2.570,23 ha** em 32 talhões; 10 pessoas no CD-04, **9 com login**.
- `node` com `cenario.js`: `2570.23*1.5` = 3855.3450000000003; soma em ponto flutuante das áreas = 2570.2299999999996; `cenQtd` com a regra R3 dá **5.140,46** (2 × 2.570,23), **3.855,35** (1,5 × 2.570,23), 5.200,00, 5.240,46, 224,25, 299,00, 199,00 e 640,00; somas 6.278,46, 6.338,00, 2.958,23 e 2.945,23.

**Abreviações:** `gen37/` = `tools/prototipo/v37/gen37/` · PRD = `/home/user/Safrion-Software-/docs/PRD.md` v3.9.

---

## 0. Mapa: fica, muda, sai

| Peça | Onde | Decisão | Passo |
|---|---|---|---|
| Menu de 5 grupos | `ui37.py:35-41` | **muda**: grupo `('Configurações','grid',[('Assinatura e cobrança','CF-05.dc.html')])` na **última** linha de `MENU2` (a frente colheita insere "Produção" depois de Agrícola: as duas mudanças não se tocam e os índices `navK` dos grupos atuais não mudam) | P2 |
| Grupo de 1 item vira link com o nome do grupo | `ui37.py:60` | **muda**: só quando o rótulo do item é igual ao do grupo (Mapa); Configurações abre como grupo e mostra o item | P2 |
| CF-05 com plano em texto, 9 áreas fixas, 3 faturas fixas e contestação por talhão | `configuracoes.py:469-524`, dentro de `build()` | **sai** de lá; tela nova em `areas/assinatura.py`, mesmo arquivo `CF-05.dc.html`, título "Assinatura e cobrança" (PRD 57.5), lendo o estado | P2 |
| Constantes do CF-05 antigo | `configuracoes.py:24, 26-33` (`AREA_HA`, `AREA_FMT`, `RESERVA`, `FIS_FMT`, `MENS`, `MENS_FMT`, `V1_HA`, `AMPL`, `JUL`, `JUL_FMT`) | **saem**. `n0` (`:25`) **fica**: CF-03 e CF-04 usam (`:317`, `:430`) | P2 |
| CF-05det (memória de set/2026) | `configuracoes.py:526-553` | **sai**: a memória é o detalhe da linha da fatura | P2 |
| BO-01 + BO-01det (versões, aprovar tabela, vincular contrato, simulação 20–1.000 ha) | `onboarding_backoffice.py:238-337` | **muda**: BO-01 "Planos e preços" só de leitura dos parâmetros + simulação; criar/aprovar versão sai (§9) | P4 |
| BO-02 + BO-02det (assinaturas, faturas, linha do tempo da Aurora) | `onboarding_backoffice.py:340-425` | **muda**: BO-02 lista organizações do mesmo estado; linha do tempo vira detalhe da linha | P4 |
| BO-03 + BO-03det (medição, contestação, AJ-009/010) | `onboarding_backoffice.py:428-539` | **sai**: medição é o detalhe da organização no BO-02; contestação mínima no P6 | P4, P6 |
| BO-04 (coortes, CAC, LTV) | `onboarding_backoffice.py:542-582` | **sai** (§9) | P4 |
| Dados e funções do backoffice | `onboarding_backoffice.py` | **saem, por nome** (as linhas mudam com outras frentes): `CTX_BO`, `PERFIL_BO`, `HIP`, `CONTRATANTES`, `OFERTAS`, `PLANOS`, `EST_PLANO`, `FATURAS`, `EST_FAT`, `MEDICAO`, `EST_MED`, `COORTES`, `PST`, `PSTOFF`, `BO1_JS`, `BO2_JS`, `BO3_JS`, `BO3D_JS`, `bo01`…`bo04`. Entra `dados_assinatura.py` (fonte única do seed) | P1, P4 |
| Trial da Boa Esperança (`TRIAL`: 30 dias, 480 ha, até 18/10) | `onboarding_backoffice.py:27` | **muda de lugar**: vai para `dados_assinatura.py`; o ON-01 importa de lá (um só trial para ON-01, BO-01 e BO-02) | P1 |
| ON-01, ON-01det, `CTX_ON`, `PERFIL_ON`, `PRIV`, `H`, `B` e ajudantes (`:73-101`) | `onboarding_backoffice.py` | **ficam**; `build()` passa a chamar só `on01()` e `on01det()` | P4 |
| `cenDec`/`cenQtd` (decimal, 2 casas, meio para cima) | `cenario.js:29-40` | **fica**: é a regra de dinheiro também (valor = preço × área) | P1 |
| Estado único | `cenario.js:6-19` | **muda**: `c.assin` no cenário salvo (`talhao-os-cenario-v1`); o seed fica só em `ASSIN0` (`dados_assinatura.py`); `c.assin` ausente vale `ASSIN0`. `cenario.py` **não muda** e `CEN0.v` **não** sobe (PLAT-D12) | P1 |
| Mescla base + salvo dos talhões | `talmapa.js:7-11` (`tmBase`), `inicio.py:484-488` (`_cad0`), `cad_fazendas.py:179-180` | **fica**; `assinatura.js` aplica a mesma regra numa função pura, sobre a mesma base do Mapa (`_cad0`), testada contra o `tmBase` (PLAT-D16) | P1 |
| Pessoas com login | `dados_cad.py:77-88` | **fica**; lido na geração (o CD-04 não grava no navegador) | P1 |
| Prefixo de assinatura em toda tela | `engine.py:1445-1449` (`engine()`) | **muda**: anexa **uma vez** `ASSIN0`, `ASSIN_CENV` (o `v` de `cenario.seed()`, lido uma vez) e `assinatura.js`. Nenhuma tela repete `assinatura.js` em `EXTRAJS` | P1 |
| Valores do motor em toda tela | `engine.py:1438` | **muda**: depois de `EXTRAVALS`, chama `assinAvisoVals(this,v)` | P3 |
| Cabeçalho da casca | `ui37.py:323-335` (`shell37`) | **muda**: faixa de cobrança abaixo do título **só nas telas da organização**: prefixo fora de `BO`, `ON` e `PT`, e não no próprio CF-05 (R11). `mobile37` (`ui37.py:356`) não muda | P3 |
| Pontos que aumentam a área medida | `cad_fazendas.py:257,261` (`g_tal_new`); `cad_fazendas.py:154` (`talErros`: talhão novo ou Inativo → Ativo, cobre o Reativar do CD-01det `:647`); `talmapa.js:167` (`r_des` → `tmIniciar` novo); `talmapa.js:108` (`tmImportar`, linhas `novo`, inclusive pelo atalho `IN-04.dc.html#importar` de `:163`, usado pelo CD-01det em `:520`); `talmapa.js:24` (`tmSalvar` novo, defesa) | **muda**: uma linha de guarda em cada ponto chamando `assinTrava('ampliar_area')` (R12) | P5 |
| Telas que deixam de ser geradas | `build.py:23` | **muda**: + CF-05det, BO-01det, BO-02det, BO-03, BO-03det, BO-04; o laço apaga de `project/` **e de `_render/`** (o `montar_render.py` só copia; sem isso a varredura e as capturas seguem servindo as telas removidas) | P2, P4 |
| Índice e listas de exceção | `areas/indice.py:15,54`; `links_ocultos_test.py:32` (BO-01 → BO-02); `acao_unica_test.py:394` (tira BO-01det, BO-02det, BO-03det); `heights_override.json:9-14,28-29` | **muda**: Backoffice aponta para BO-02 (2 telas); entradas das telas que saem são removidas | P4 |
| Testes antigos | `obotest.py` (77 linhas), `cftest.py:75-81` | **mudam** com motivo no commit: as telas e números testados saem (§8) | P2, P4 |

## 1. Missão e princípios

A organização sabe, numa tela, **quanto paga, por quê e o que fazer**; a plataforma vê todas as organizações no mesmo estado. Princípios:
1. Cobrança simulada, nunca real: nenhum provedor, nenhuma credencial; tudo rotulado "simulado". **Nenhum campo de cartão, conta ou documento de pagamento**: pagar é escolher a forma numa lista curta (Pix, boleto, cartão final 4242 · simulado).
2. Preço, mínimo, franquia, trial, calendário e régua são **parâmetros de exemplo, a decidir pelo proprietário** (DEC-01, DEC-05, DEC-09), numa tabela só.
3. Uso lido dos cadastros, nunca digitado aqui; fatura fechada nunca é recalculada.
4. Inadimplência avisa e restringe aos poucos; **nunca apaga dado, nunca tira consulta e exportação, nunca para trabalho de campo**.
5. O agricultor não vê o backoffice; o backoffice vê área por organização e por fazenda e o extrato contratual, nunca cultura, safra, operação ou insumo (PRD 57.5; R17).

## 2. Menu e telas: antes → depois

| Antes (9 telas, todas ocultas) | Depois (3 telas) | Natureza | Onde |
|---|---|---|---|
| CF-05 Assinatura e medição + CF-05det | **CF-05 Assinatura e cobrança** | controle (uso e faturas) com duas execuções: pagar, aceitar mudança | Menu › Configurações |
| BO-02 + BO-02det + BO-03 + BO-03det | **BO-02 Assinaturas e cobrança** (plataforma) | execução (conciliar) e controle da carteira | Oculto; Índice › Backoffice |
| BO-01 + BO-01det | **BO-01 Planos e preços** | planejamento comercial (parâmetros) | Oculto; telas irmãs do BO-02 |
| BO-04 | — | sai (§9) | — |

BO-01 e BO-02 usam `secoes_nav` (telas irmãs, `ui37.py:113`), perfil "Admin plataforma". CF-05 usa o perfil "Ana · Gestora" até existir o "Ver como" (§9). CF-05, BO-01 e BO-02 carregam `cenario.js_prefixo()` (gravam `c.assin` e usam `cenQtd`); CF-05 e BO-02 embutem também a base do cadastro (`_cad0`) para medir a área (R1).

## 3. Telas

### 3.1 CF-05 · Assinatura e cobrança
**Pergunta:** quanto vou pagar, por quê, e o que preciso fazer?
**Cabeçalho:** título; selo do estado da assinatura (R10) no status; "Cobrança simulada · nenhum valor é cobrado" no subtítulo (a casca tem um selo só); **uma ação primária**, pela ordem (R14): `Pagar fatura` › `Ampliar área contratada` › `Alterar plano ou área`. A faixa de cobrança (R11) não aparece aqui.
**Resumo (4 números):** Plano ("Completo · R$ 2,00/ha·mês"); Área medida ("2.570,23 ha de 2.600 ha contratados"); Prévia do período ("R$ 5.140,46 · set/2026 fecha em 30/09"); Próxima cobrança ("01/10/2026").
**Bloco 1 · Uso medido (grade):** uma linha acima da grade: "Origem: Cadastros › Fazendas, áreas e talhões". Colunas Fazenda · Talhão · Área cultivável (`2.570,23 ha` na célula, soma no rodapé) · Situação ("Conta na medição" / "Inativo · fora" / "Fazenda inativa · fora"). Filtro de texto, filtro rápido por fazenda, ordenação por qualquer coluna (padrão: área decrescente). Linha → detalhe de origem (só leitura) com o link "Abrir no cadastro" (`CD-01det.dc.html#talhao=<id>`). Abaixo, uma linha: "Pessoas com acesso: 9 (Cadastros › Pessoas e equipes) · usuários sem limite · não entram na cobrança". Aviso quando medida > contratada: "20,23 ha acima da área contratada não entram na cobrança de set/2026; com o aceite da ampliação, entram a partir de 01/10".
**Bloco 2 · Faturas (grade):** Competência · Área cobrada (`ha`) · Regra ("R$ 2,00/ha·mês · mínimo R$ 299,00") · Valor (`R$`) · Vencimento · Estado. Estados (os únicos): **Em medição** (período aberto, ainda não é fatura) · **A vencer** · **Vencida** · **Pendente** (evento do provedor a conciliar) · **Paga** · **Em contestação** (P6). Correspondência com o PRD 58.4: pendente = Pendente, pago = Paga, falhou = Vencida com tentativa recusada; ação necessária, estornado e cancelado ficam fora (§9). Filtro de texto e rápido por estado; ordenação (padrão: competência decrescente). Linha → **detalhe (memória)**: medida, contratada, cobrada = mín(medida; contratada), conta `máx(mínimo; preço × cobrada)`, versão da medição ("fechamento 30/09 · 32 talhões"), "pela área contratada seria R$ 5.200,00 (DEC-01, a decidir pelo proprietário)", eventos (emitida, tentativa, paga `evt_…`). Ações do detalhe: em fatura A vencer ou Vencida, `Confirmar pagamento (simulado)` com a forma escolhida na lista do princípio 1, e `Contestar fatura` (secundária, P6); em qualquer fatura, `Baixar fatura (CSV)` (secundária; gera o arquivo no navegador a partir da cópia da fatura; PRD CF-05 "Baixar dados", ONB-09). O `Pagar fatura` do cabeçalho abre este detalhe na fatura aberta.
**Bloco 3 · Planos (grade, 2 linhas: Essencial e Completo; a Avaliação só aparece no BO-01):** Plano · Módulos · Limite de área · Usuários · Franquias · Preço R$/ha·mês (com o equivalente na célula: "R$ 2,00 · R$ 24,00/ha·ano", PRECO-01) · Mínimo R$/mês · **Valor para a sua área** (`R$` com a área medida, calculado pela mesma função) · selo "Seu plano" ou "Agendado para 01/10". Cada parâmetro com o selo "exemplo · a decidir pelo proprietário". Filtro e ordenação da grade padrão. Linha → painel **Alterar plano ou área**:
- campos: Plano (lista curta, um toque: Essencial, Completo); Área contratada (número com "ha"; preenchida com a atual; ajuda "medida hoje: 2.570,23 ha"); Início (calculado: dia 1 do próximo ciclo, só leitura);
- **prévia** viva, hoje → depois (PRECO-01, PRD 58.4): plano, área contratada, preço por mês e por ano, mínimo, franquias, mensalidade, diferença por mês, módulos que mudam, início, periodicidade (mensal), prazo e cancelamento ("sem fidelidade; cancelamento ao fim do ciclo · exemplo, a decidir pelo proprietário");
- confirmar: `Aceitar e agendar para 01/10/2026`. Com mudança agendada, o painel a mostra com `Desfazer mudança` (secundária); `Aceitar e agendar` só volta quando o formulário difere do agendado.
**Bloco 4 · Demonstração (amarelo, rotulado "só demonstração"):** "Data simulada da cobrança": 23/09/2026 · 01/10/2026 · 06/10/2026 · 16/10/2026 (só avança) e `Restaurar assinatura da demonstração` (zera `c.assin`).
**Estados da tela:** em dia sem pendência; fatura a vencer; em atraso; inadimplente; acima do contratado; mudança agendada; em contestação (P6).
**Celular 390 px:** resumo em 2 × 2; grades com a 1ª coluna fixa e rolagem interna; primária sempre no cabeçalho; painel ocupa a largura; prévia em lista "hoje → depois", sem tabela.

### 3.2 BO-02 · Assinaturas e cobrança (plataforma)
**Pergunta:** quem paga quanto, quem está atrasado e o que conciliar?
**Primária:** `Conciliar pagamentos` (processa os eventos simulados do provedor, uma vez cada).
**Resumo:** Mensalidades vigentes (R$); Organizações por estado; Faturas abertas (quantidade · R$); Área cobrada (ha: Σ mín(medida; contratada) das organizações pagantes).
**Grade:** Organização · Plano · Estado · Área medida (`ha`) · Área contratada (`ha`) · Mensalidade (`R$`) · Fatura aberta (competência · estado) · Próximo evento. A área medida da organização da demonstração é calculada como no CF-05 (`assinMedir` sobre a mesma base e o mesmo salvo), nunca copiada do seed. Filtro de texto, rápido por estado e plano, ordenação. Linha → detalhe: na organização da demonstração, totais por **fazenda**; nas outras, a área informada (sem fazenda); faturas e eventos; na organização da demonstração, `Consulta contratual (CF-05)` (destino previsto no PRD BO-01..04). Na contestação aberta: `Resolver contestação` (P6).
**Celular 390 px:** igual ao CF-05.

### 3.3 BO-01 · Planos e preços
**Pergunta:** quanto cada plano cobra por área, e o que falta o proprietário decidir?
**Primária:** `Simular área` (painel: hectares → mensalidade de cada plano).
**Grade 1 · Parâmetros:** Plano (Avaliação, Essencial, Completo) · Módulos · Limite de área · Usuários · Franquias · Preço R$/ha·mês · Mínimo R$/mês · Equivalente R$/ha·ano · Decisão pendente (DEC-01/05/09). Linha → detalhe só leitura.
**Grade 2 · Simulação fixa (PRECO-03):** 20, 100, 149,5, 500, 1.000 e 5.000 ha × planos (`R$` na célula), filtro e ordenação. Os valores são preenchidos no navegador por `assinMensalidade`; nenhuma mensalidade é calculada em Python.
**Texto curto:** PRECO-01 (R$ 2,00/ha·mês = R$ 24,00/ha·ano), mínimo pelo maior valor, mudança nunca retroage.

## 4. Regras (testáveis; o dano que cada trava evita)

R1. **Medida** = soma da área cultivável (`decl`, número) dos talhões com situação Ativo em fazendas Ativas, do cadastro (base da geração `_cad0` + o salvo em `talhao-os-cd01-v1`, mesma regra do `tmBase`). Soma em centésimos inteiros. Safra, parcela, consórcio e operação não entram: a unidade é o talhão (PRECO-02). O Mapa impede contorno sobreposto (`talmapa.js:49`); o CD-01 e o Mapa impedem talhões ativos acima da área da fazenda (`cad_fazendas.py:173`, `talmapa.js:48`). Talhão sem contorno não é conferido por geometria: limite conhecido, visível no detalhe de origem.
R2. **Cobrada** = mín(medida; contratada). Acima do contratado não se cobra sem aceite (PRD 57.2). *Dano evitado: cobrança-surpresa ao desenhar um talhão.*
R3. **Mensalidade** = máx(mínimo; `cenQtd(preço, cobrada)`) − crédito do período (nunca < 0). Mínimo é o maior, não se soma (PRECO-03). Uma função, `assinMensalidade`, usada por CF-05, BO-01, BO-02 e prévia. Totais e rodapés somam centavos inteiros.
R4. Período = mês civil; fecha no último dia; a fatura guarda a cópia da medição (área, plano, preço, mínimo, contratada, nº de talhões) e **nunca é recalculada**. *Dano evitado: reescrever cobrança já emitida.*
R5. Emissão e vencimento no dia 1 do mês seguinte. Tentativas automáticas (3 em 10 dias, exemplo, PRD 57.4.1) só com cartão salvo (Aurora); a organização da demonstração não tem cartão salvo e paga pelo detalhe da fatura.
R6. Mudança de plano ou área vale do dia 1 do próximo ciclo; nunca retroage (PRECO-04).
R7. Área contratada no aceite ≥ medida do dia e ≤ 5.000 ha (limite dos planos; acima, recusa com "acima de 5.000 ha: proposta empresarial, a decidir pelo proprietário"). *Dano evitado: contratar 100 ha e gerir 2.570 ha pagando o mínimo.*
R8. Aceite, pagamento e conciliação levam chave de idempotência gerada por quem inicia (ao abrir o painel); repetir a chave devolve o mesmo recibo sem novo efeito; pagar fatura já paga com outra chave não paga de novo (PRECO-08).
R9. Fatura só fica Paga por evento (simulado) do provedor: na organização da demonstração o evento chega na hora; nas demais, por `Conciliar pagamentos`. Evento visto uma vez (`evt` registrado).
R10. **Estado da assinatura** (derivado, não gravado): Em avaliação · Ativa · Em atraso (fatura vencida há 1–10 dias) · Inadimplente (11 dias ou mais) · Cancelada. Fatura Pendente e Em contestação não contam dias.
R11. **Em atraso:** faixa amarela nas telas web da organização (prefixo fora de `BO`, `ON` e `PT`; não no CF-05, que já mostra o estado e a primária). Texto com a data simulada: "Fatura set/2026 vencida há 5 dias (data simulada da cobrança: 06/10)". `Pagar fatura` na faixa é **link de texto** para o CF-05, nunca botão verde (não conta como segunda primária). Nada restrito. O app de campo nunca mostra cobrança.
R12. **Inadimplente:** faixa vermelha; não amplia a área medida. Recusam com motivo e caminho ("Pague a fatura de set/2026 em Configurações › Assinatura e cobrança"): `Cadastrar talhão` (CD-01, antes de abrir o formulário); `Desenhar` talhão novo (Mapa, antes de abrir o desenho); linha "Talhão novo" na importação (Mapa, também pelo atalho `#importar` do CD-01det); `Reativar` talhão (CD-01 e CD-01det, na validação ao salvar). Defesa: `talErros` (CD-01) e `tmSalvar` com alvo novo recusam também. Seguem: editar talhão existente, inclusive a área cultivável (corrigir o fato não é ampliar o contrato; R2 evita a cobrança-surpresa); contorno novo de talhão existente, desenhado ou importado; inativar. *Dano evitado: ampliar a área gerida (custo de servir: mapa, satélite, armazenamento) sem pagar a que já usa. A dívida não cresce por isso (R2); o uso, sim.*
R13. **Nunca restringe:** O.S. (emitir, aprovar, liberar, entregar, apontar, conferir, encerrar), receituário, irrigação, manutenção, estoque, colheita, consulta e exportação (`Baixar fatura`). *Dano evitado: empurrar o trabalho de campo para fora do sistema, sem aprovação agronômica, carência e rastreio.* Nada é apagado em estado algum.
R14. Primária do CF-05 (uma): fatura vencida ou a vencer → `Pagar fatura`; senão medida > contratada → `Ampliar área contratada` (painel com Completo/atual e área = medida arredondada para cima à centena); senão `Alterar plano ou área`.
R15. Plano Essencial não inclui pós-colheita (beneficiamento), comercial e logística, gestão e resultados e integração ERP; o núcleo (Mapa, Cadastros, Agrícola com O.S. e app, colheita e produção por talhão, Manutenção, Suprimentos) está em todos. *Dano evitado: O.S. sem reserva de estoque, sem bloqueio de máquina ou colheita sem registro de produção por plano partido.* O grupo "Produção" que a frente colheita põe no menu é núcleo: nada muda aqui. A trava de consulta dos módulos só do Completo entra quando um deles entrar no menu (§9); até lá a prévia diz o que mudaria.
R16. Contestação (P6): congela a régua da fatura; resolução "Manter valor" (novo vencimento = data simulada da resolução + 5 dias) ou "Creditar no próximo período" (crédito ≤ valor, linha negativa na próxima fatura). Fatura contestada não é reescrita. *Dano evitado: restringir cliente por cobrança que ele contesta.*
R17. BO-02 mostra área por organização e, na organização da demonstração, por fazenda; nunca talhão, cultura, safra, operação ou insumo. A consulta contratual (CF-05) mostra o extrato da base: talhão e área cultivável, que é o que se cobra (PRECO-02), sem cultura nem safra (PRD 57.5).

Unidades: `ha` e `R$` na célula (DEC-0510-02); rótulos "Preço R$/ha·mês", "Mínimo R$/mês". Unidade de produtividade (DEC-0510-03) não se aplica. Kanban de 5 fases e aprovação agronômica: intocados (R13).

## 5. Integração com o estado único e com os outros módulos

| Lê | De onde | Para |
|---|---|---|
| Talhões, fazendas, situação, área cultivável | CD-01: base da geração (`inicio._cad0`: `cad_fazendas._faz_rows/_tal_rows`, só id, fazenda, nome, `decl` e situação) + `talhao-os-cd01-v1` | medida (R1) no CF-05 e no BO-02 |
| Pessoas com login | `dados_cad.PESSOAS` (geração) | linha informativa |
| Assinatura, contratos, faturas, eventos, recibos, data simulada | `c.assin` do cenário salvo (`talhao-os-cenario-v1`); ausente → `ASSIN0` | CF-05, BO-01, BO-02, faixa, trava |

**Leitura em qualquer tela (`assinLer`).** Com `cenario.js` na página: `cenGet().assin || ASSIN0`. Sem ele (CD-01, CMP, PA e a maioria das telas): lê a mesma chave do `localStorage` e aceita o cenário só se `c.v === ASSIN_CENV` (a mesma regra do `cenGet`); senão, `ASSIN0`. `assinatura.js` não declara nenhum nome de `cenario.js` (tudo com prefixo `assin`/`ASSIN`): página com os dois carrega sem redeclaração; página sem `cenario.js` não chama `cenGet`.

| Grava | Quem | Função (em `assinatura.js`, via `cenMudar`, que só existe onde há `cenario.js`) |
|---|---|---|
| pagamento + evento + recibo | CF-05 | `assinPagar(c, fat, forma, chave)` |
| mudança agendada (contrato vN) | CF-05 | `assinMudar(c, plano, ha, chave)` / `assinDesfazer(c)` |
| data simulada e fechamento do período | CF-05 (demonstração) | `assinAvancar(c, data, medida)` |
| conciliação | BO-02 | `assinConciliar(c, chave)` |
| contestação e resolução (P6) | CF-05 / BO-02 | `assinContestar`, `assinResolver` |

Toda gravação começa por `c.assin = c.assin || clone(ASSIN0)`. `cenReset()` (Restaurar demonstração do app) apaga o cenário inteiro e devolve a assinatura ao seed.

Funções puras (sem gravar): `assinLer()`, `assinMedir(cad0, salvo)`, `assinMensalidade(plano, medida, contratada, credito)`, `assinEstado(org, hoje)`, `assinPrimaria(org, medida)`, `assinTrava(acao)` (devolve "" ou o motivo), `assinAvisoVals(self, v)` (faixa). Outras telas atualizam pelo evento `storage` da chave do cenário (`cenOuvir` onde houver `cenario.js`; `assinatura.js` escuta a mesma chave onde não houver). Módulos que só o Completo tem (pós-colheita, comercial, gestão) e Configurações (CF-01..04) passam a ler `assinTrava` quando entrarem no menu.

## 6. Seed sintético (`dados_assinatura.py`; números fecham)

Organização da demonstração **Grupo Santa Rita** (3 fazendas do cadastro). Plano Completo. Contrato v1 desde 01/07/2026, 1.200 ha (aceite 28/06). Contrato v2 desde 01/09/2026, área = medida da base arredondada para cima à centena (**2.600 ha** com a Lagoa sintética), aceite 28/08 para a entrada de Boa Vista e Lagoa Grande no cadastro **em 01/09**: por isso agosto fecha só com a Santa Rita (R4) e o aceite respeita R7 (2.600 ≥ 1.165).

| Competência | Medida | Cobrada | Conta | Valor | Estado em 23/09 |
|---|---|---|---|---|---|
| jul/2026 | 1.165,00 ha | 1.165,00 ha | máx(299; 2,00 × 1.165) | R$ 2.330,00 | Paga 01/08 · `evt_demo_0801` |
| ago/2026 | 1.165,00 ha | 1.165,00 ha | idem | R$ 2.330,00 | Paga 01/09 · `evt_demo_0901` |
| set/2026 | 2.570,23 ha | 2.570,23 ha | máx(299; 2,00 × 2.570,23) | R$ 5.140,46 | Em medição (fecha 30/09) |

A medida de jul e ago é a soma dos 8 talhões da Santa Rita na base, calculada na geração (não digitada).

Outras organizações (medição informada pelo inquilino, sintética):

| Organização | Plano | Contratada | Medida | Mensalidade | Situação em 23/09 |
|---|---|---|---|---|---|
| Fazenda Aurora | Completo | 60 ha (desde 01/08) | 35 ha | máx(299; 70,00) = R$ 299,00 | ago R$ 299,00 vencida 01/09, 3 tentativas recusadas até 10/09 → Inadimplente |
| Sítio Ipê | Essencial | 20 ha | 20 ha | máx(199; 30,00) = R$ 199,00 | Ativa, em dia |
| Agro Bela Vista | Completo | 320 ha | 333 ha | 2,00 × 320 = R$ 640,00 | ago R$ 640,00 Pendente (`evt_1JKT5` a conciliar); 13 ha acima do contratado |
| Org. Boa Esperança | Avaliação | — | 480 ha declarados (`TRIAL`, o mesmo do ON-01) | R$ 0,00 | dia 5 de 30 (19/09 → 18/10), sem cartão |
| Rancho Dois Rios | Essencial | 40 ha | — | — | Cancelada 31/08 a pedido; consulta e exportação até 29/11 |

Fila do provedor: `evt_1JKT5` (Bela Vista, R$ 640,00, aprovado) e `evt_1JKR9` (Aurora, pagamento avulso de 22/09 com cartão novo, recusado). Totais do BO-02 em 23/09: mensalidades vigentes 5.140,46 + 299,00 + 199,00 + 640,00 = **R$ 6.278,46**; Ativa 3 · Em avaliação 1 · Inadimplente 1 · Cancelada 1; faturas abertas **2 · R$ 939,00** (depois de conciliar: 1 · R$ 299,00, a da Aurora segue Vencida); área cobrada 2.570,23 + 35 + 20 + 320 = **2.945,23 ha** (medida 2.958,23 ha: a Bela Vista tem 13 ha acima). Cada fatura do seed confere com `assinMensalidade` dos seus dados (A2).

Planos (exemplo, a decidir): **Avaliação** 30 dias, R$ 0, limite = área declarada, todos os módulos, satélite 12 cenas e IA 200 interações no período, consulta e exportação 90 dias após o fim (DEC-09) · **Essencial** núcleo (R15), R$ 1,50/ha·mês, mínimo R$ 199, até 5.000 ha, usuários sem limite, satélite 6 cenas/mês, IA 100/mês · **Completo** núcleo + pós-colheita, comercial e logística, gestão e resultados e integração ERP em sandbox, R$ 2,00/ha·mês (hipótese PRD 57.2), mínimo R$ 299, até 5.000 ha, usuários sem limite, satélite 12 cenas/mês, IA 200/mês (franquias do BO-01det atual).

Roteiro de números (data simulada da organização da demonstração; as outras não fecham período):
- 01/10: set fecha com 2.570,23 ha → R$ 5.140,46, vence hoje (A vencer; primária `Pagar fatura`); out/2026 abre em medição.
- 06/10: vencida há 5 dias → Em atraso (faixa amarela). 16/10: há 15 dias → Inadimplente (faixa vermelha, R12).
- Trocar para Essencial em 23/09: prévia R$ 5.140,46 → **R$ 3.855,35** a partir de 01/10 (−R$ 1.285,11/mês); set fecha em Completo.
- Talhão novo de 50 ha em 23/09: medida 2.620,23 ha; cobrada 2.600 ha → R$ 5.200,00; aviso de 20,23 ha; `Ampliar` sugere 2.700 ha → R$ 5.240,46 a partir de 01/10. No BO-02: Santa Rita com 2.620,23 ha e mensalidades vigentes R$ 6.338,00.
- BO-01: 20 ha → 299,00 / 199,00; 100 → 299,00 / 199,00; 149,5 → 299,00 / 224,25; 500 → 1.000,00 / 750,00; 1.000 → 2.000,00 / 1.500,00; 5.000 → 10.000,00 / 7.500,00 (Completo / Essencial).

No Mac (KML real da Lagoa), a medida e a contratada v2 mudam: os testes calculam a expectativa pela mesma regra a partir das linhas do cadastro.

## 7. Passos (cada um deixa o protótipo funcionando)

- **P1 · Estado e regras.** `dados_assinatura.py` (seed §6, planos, parâmetros com rótulo de decisão, `TRIAL` vindo do onboarding, que passa a importá-lo); `assinatura.js` (funções §5); prefixo no `engine()` (uma vez, sem efeito visível: ainda não há faixa). `cenario.py` não muda. Teste: `node assinatura_unit.js` (inclui `assinLer` com e sem `cenario.js` concatenado, e cenário salvo com outro `v`) + `varredura.py` inteira (nenhuma página quebra com o prefixo).
- **P2 · CF-05 no menu.** `areas/assinatura.py` (§3.1), menu e regra do grupo de 1 item (`ui37.py:35-41,60`), CF-05 e constantes saem de `configuracoes.py` (§0; `n0` fica), `build.py:23` (`project/` e `_render/`), novo `assinatura_test.py` (CF-05), `cftest.py` sem a parte CF-05 (motivo no commit).
- **P3 · Faixa de cobrança.** `engine.py:1438` e `ui37.py:323-335` (§0, R11). Teste: faixa em OS, EST e CD-01 com data 06/10 e 16/10; nenhuma em MB-01, CF-05, BO-02 e ON-01.
- **P4 · Plataforma.** `areas/plataforma.py` com BO-01 e BO-02 (§3.2, §3.3); `onboarding_backoffice.py` fica só com ON (lista por nome no §0); índice, listas de exceção e `heights_override.json`; `obotest.py` substituído por `plataforma_test.py` (motivo: telas e números novos).
- **P5 · Trava de inadimplência.** `assinTrava('ampliar_area')` nos pontos do §0 (R12): antes de abrir, nos botões; ao gravar, em `talErros` e `tmSalvar`. Teste no `assinatura_test.py`.
- **P6 · Contestação mínima.** R16 no detalhe da fatura (CF-05) e no detalhe da organização (BO-02).

Em cada passo: `python3 build.py > /tmp/PLAT-build.log; grep -c FALHA /tmp/PLAT-build.log` = 0; `python3 montar_render.py`; navegador um por vez com `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdp9333.lock env CDP_GL=1 timeout 900 python3 <teste>`: `varredura.py`, `../ferramentas/acoes_duplicadas.py . /tmp/PLAT-dup.json`, os testes do módulo e os existentes; vermelhos da base listados no pedido não são deste módulo e não são escondidos.

## 8. Critérios de aceite (teste que prova)

| # | Critério | Teste |
|---|---|---|
| A1 | Medida = soma decimal da área cultivável dos talhões ativos (base + salvo); inativo e fazenda inativa saem; igual ao `tmBase` | `assinatura_unit.js` |
| A2 | `assinMensalidade`: tabela da §6 inteira (inclui 3.855,35 e 224,25), mínimo pelo maior, e cada fatura do seed confere com os seus dados | `assinatura_unit.js` |
| A3 | Fatura fechada não muda após editar, criar ou inativar talhão | unit + `assinatura_test.py` |
| A4 | Mudança agendada vale de 01/10; set fecha no plano antigo; desfazer antes de 01/10 volta ao anterior | unit + navegador |
| A5 | Área contratada abaixo da medida ou acima de 5.000 ha é recusada no aceite, com o motivo | unit + navegador |
| A6 | Mesma chave de pagamento ou aceite repetida: um efeito, mesmo recibo; fatura paga não paga de novo | unit |
| A7 | Por data: 23/09 Ativa sem fatura aberta; 01/10 Ativa com fatura A vencer; 06/10 Em atraso; 16/10 Inadimplente; pagar volta a Ativa | unit + navegador |
| A8 | Faixa amarela/vermelha em OS, EST e CD-01 (esta sem `cenario.js`) com o link "Pagar fatura" e a data simulada; nenhuma em MB-01, CF-05, BO-02 e ON-01 | `assinatura_test.py` |
| A9 | Inadimplente: Cadastrar talhão e Desenhar recusam antes de abrir; linha "Talhão novo" da importação recusada e linha que atualiza contorno existente importada; Reativar recusado; editar a área de um talhão existente salva; liberar uma O.S. A liberar e apontar no MB-03 seguem | `assinatura_test.py` |
| A10 | Talhão novo de 50 ha (Santa Rita) pelo formulário do CD-01: CF-05 mostra 2.620,23 ha, aviso de 20,23 ha e primária `Ampliar área contratada`; BO-02 mostra 2.620,23 ha e R$ 6.338,00. O mesmo talhão no formato gravado pelo `tmSalvar` (Mapa) dá a mesma medida | `assinatura_test.py` + unit |
| A11 | Uma primária por tela em CF-05, BO-01 e BO-02 em cada estado da §3.1 e da §3.2 (mesmo critério do `EST` de `acao_unica_test.py`: botão verde cheio); `acoes_duplicadas.py` sem achado nas 3 telas | `assinatura_test.py`, `plataforma_test.py`, `acoes_duplicadas.py` |
| A12 | BO-02: totais da §6; pagar no CF-05 aparece Paga no BO-02; conciliar duas vezes não duplica | `plataforma_test.py` |
| A13 | BO-02 detalhe sem talhão, cultura e safra; CF-05 sem cultura e safra | `plataforma_test.py`, `assinatura_test.py` |
| A14 | Toda grade das 3 telas com filtro e ordenação; `ha` e `R$` na célula (a `varredura.py` só prova página sem erro) | testes do módulo |
| A15 | 390 px: primária visível, resumo 2 × 2, sem rolagem horizontal da página | `assinatura_test.py` (captura) |
| A16 | Menu: Configurações por último, com "Assinatura e cobrança"; Mapa segue como link único | `assinatura_test.py` |
| A17 | Contestação congela a régua; resolver com crédito aparece na fatura seguinte (P6) | unit + navegador |
| A18 | Nenhum campo de cartão, conta ou documento em CF-05, BO-01 e BO-02; `Baixar fatura (CSV)` traz os números da cópia da fatura | `assinatura_test.py` |
| A19 | As 6 telas que saem não existem em `project/` nem em `_render/`; nenhum link aponta para elas | `links_ocultos_test.py` + `ls` |

## 9. Fora de escopo (condição de retorno)

| Item | Volta quando |
|---|---|
| Criar, revisar e aprovar versão de plano; vincular contrato (BO-01 antigo) | o proprietário decidir DEC-01/05/09 e pedir a tabela aprovada |
| Cancelar assinatura pelo cliente e o "somente consulta" depois do fim do ciclo | `cenMudar` ganhar nome de comando (SUP-2a) para aplicar consulta sem listar telas |
| Fatura em ação necessária, estornada ou cancelada (PRD 58.4) | provedor de pagamento homologado, no software real |
| Trava de consulta dos módulos só do Completo | pós-colheita, comercial, gestão ou integração ERP entrarem no menu |
| Restrição de serviços pagos (satélite, IA) | existir serviço pago real ou simulado com franquia medida |
| Planos de parceiros e patrocínio (Fertisul, Coop. Verde Vale; PT-07) | DEC-05 e o portal do parceiro voltar ao menu |
| Economia da plataforma (BO-04: coortes, CAC, LTV) | houver 3 coortes com 90 dias observados (PRD 57.3) |
| Pró-rata, faixas marginais acima de 5.000 ha, plano anual, desconto | decisão comercial do proprietário (PRD 57.2) |
| Trial do ponto de vista do agricultor (avisos de fim, contratar) | ON-01 voltar ao menu |
| Quem pode pagar e alterar plano (só gestão) | "Ver como" (G2_PERFIS, CTL-3 frente D) integrado |
| Pessoas lidas do estado do navegador | CD-04 gravar no navegador ou CF-01 existir |
| Exportação completa (todos os cadastros); a fatura já se baixa no CF-05 | CF-04 (Configurações) |
| Provedor de pagamento, nota fiscal, cobrança real | nunca no protótipo; no software real só com autorização e custo aprovados pelo proprietário (AGENTS §2) |

## 10. Revisão por contraexemplo (06/10/2026)

Revisor: Claude, numa passada separada da autoria. Rótulo: **executado** para as leituras e contas citadas no topo; as correções acima são **especificadas**. Severidade pelo dano se implementado como estava (AGENTS §3).

| ID | Sev. | Contraexemplo | Mudou |
|---|---|---|---|
| RV-01 | S2 | `assinatura.js` lendo o estado por `cenGet` quebra toda tela sem `cenario.js` (CD-01, CMP, PA…: `ReferenceError`); anexar `cenario.js` pelo `engine()` redeclara `const CEN0` nas telas que já o têm (`SyntaxError`) | §0, §5 (`assinLer`, prefixo uma vez, nomes `assin*`), P1 com varredura inteira, A8 com CD-01 |
| RV-02 | S3 | Faixa na casca de toda tela web incluiria BO, ON (outra organização) e PT; no CF-05 duplicaria `Pagar fatura` com a primária; como botão verde viraria 2ª primária em toda tela | R11, §0, §3.1, A8 |
| RV-03 | S3 | Trava burlável: o atalho `#importar` do CD-01det e o `Reativar` ampliam a área; bloquear "Importar" inteiro barra o contorno novo de talhão existente, que a própria R12 permite; o dano nomeado ("dívida") não existe com R2 | R12, §0 (pontos com linha), P5, A9 |
| RV-04 | S3 | BO-02 com a medida do seed: depois do talhão de 50 ha, CF-05 diz 2.620,23 e BO-02 diz 2.570,23 (área em dois lugares) | §3.2, §5, §6, A10 |
| RV-05 | S3 | Aceite sem R$/ha·ano, franquias, periodicidade, prazo e cancelamento quebra PRECO-01 e PRD 58.4 | §3.1 Bloco 3 |
| RV-06 | S3 | "Baixar dados" do PRD CF-05 (e ONB-09) some do CF-05; a exportação ia para o CF-04, que não existe | §3.1 Bloco 2, R13, §9, A18 |
| RV-07 | S3 | Estados da fatura não enumerados: aceite não testável e sem ligação com os 6 estados do PRD 58.4 | §3.1 Bloco 2, §9 |
| RV-08 | S3 | §0 por número de linha: "26-66 saem" apaga `TRIAL` (`:27`), que o ON-01 usa 5 vezes; "constantes :24-33 saem" apaga `n0`, usado por CF-03 e CF-04 | §0 por nome |
| RV-09 | S3 | Trial da Boa Esperança em dois lugares (`TRIAL` no ON-01 e no seed novo): o DEC-09 decidido mudaria um só | §0, §6, P1 |
| RV-10 | S3 | Seed: aceite da v2 em 28/08 "com a entrada de BV e LG" faria agosto fechar com 2.570,23 ha (R4) e cobrar R$ 2.400,00, não R$ 2.330,00 | §6 (entrada em 01/09) |
| RV-11 | S3 | Essencial sem colheita parte a cadeia O.S. de colheita → produção, o mesmo dano que o PLAT-D04 evita; a frente colheita põe "Produção" no menu, o que já tornava falso "nenhum desses módulos está no menu" | R15, §6, §9, D04 |
| RV-12 | S3 | Pagar sem regra de campo permite formulário de cartão: página publicada não pode coletar dado de pagamento | princípio 1, §3.1, A18, D11 |
| RV-13 | S4 | Telas removidas ficam em `_render/` (o `montar_render.py` só copia): varredura e capturas seguem servindo o BO-03 com números antigos | §0 `build.py:23`, A19 |
| RV-14 | S4 | "Área medida paga" soma 333 ha da Bela Vista, que paga 320 | §3.2 (Área cobrada 2.945,23 ha), §6 |
| RV-15 | S4 | Avaliação na grade de planos do CF-05 abre um painel em que ela não é opção | §3.1 Bloco 3 |
| RV-16 | S4 | Coluna "Origem" igual nas 32 linhas | §3.1 Bloco 1 |
| RV-17 | S4 | A10 desenhando 50 ha exatos no mapa não é determinístico; A11 cita modos do `acao_unica_test.py` que não cobrem o CF-05; A14 atribui à varredura uma checagem que ela não faz; A7 mistura estado da fatura e da assinatura | A7, A10, A11, A14 |
| RV-18 | S4 | Mesmo rótulo `Pagar fatura` para abrir e para confirmar; `Aceitar` e `Desfazer` juntos no painel | §3.1 |
| RV-19 | S4 | "O CD-01 impede sobreposição": sem contorno, o CD-01 só limita a soma pela área da fazenda | R1 |
| RV-20 | S4 | Evento recusado da Aurora em 23/09 seria uma 4ª tentativa depois das 3 de R5; tentativas na organização da demonstração, que não tem cartão salvo | R5, §6 |
| RV-21 | S4 | R17 contradiz o link do BO ao CF-05, que mostra talhões; o PRD prevê a "consulta contratual ligada a CF-05" | R17, §1, §3.2 |
| RV-22 | S4 | Editar `cenario.py:80` disputa a linha com outras frentes (o SUP-2a sobe `v` ali) e deixa dois seeds na página | §0, §5, D12 |
| RV-23 | S4 | Aceite sem teto: 9.000 ha passariam num plano "até 5.000 ha" | R7, A5 |
| RV-24 | S4 | O PLAT-D16 diz não tocar `talmapa.js` e `cad_fazendas.py`, mas o P5 os edita | D16 |

## 11. Implementação (06/10/2026)

Autor: Claude, branch `claude/v44-plataforma`, sem push. Rótulo: **executado** para o que está nesta seção, com o comando; o resto segue **especificado**. Revisão do Codex: pendente.

| Passo | Commit | Onde |
|---|---|---|
| P1 estado e regras | `899bcfe` | `dados_assinatura.py`, `assinatura.js`, `engine.py` (prefixo uma vez), `assinatura_unit*.{js,py}` |
| P2 CF-05 no menu | `0bd1b52` | `areas/assinatura.py`, `ui37.py` (MENU2 + regra do grupo de 1 item), `configuracoes.py`, `build.py` |
| P3 faixa | `dc50b00` | `engine.py` (assinAvisoVals), `ui37.py` (faixa_cobranca) |
| P4 plataforma | `d45b742` | `areas/plataforma.py`, `onboarding_backoffice.py` (só ON), índice e listas de exceção |
| P5 trava | `bcc5033` | `talmapa.js` (Desenhar, importação, tmSalvar), `cad_fazendas.py` (talErros, Cadastrar talhão) |
| P6 contestação | junto com P1, P2 e P4 | `assinContestar`/`assinResolver`, painel da fatura (CF-05) e detalhe da organização (BO-02) |

Diferenças em relação ao texto acima (todas registradas em `DECISOES.md`, PLAT-D17..D20):
- `obotest.py` não foi apagado: ficou só com ON-01/ON-01det; o backoffice novo está em `plataforma_test.py` (D17).
- Recibos com sequência por tipo (PAG-, ACE-, CON-, CTS-, RES-) (D18). A chave do aceite muda quando o formulário muda ou ao desfazer; o clique repetido devolve o mesmo recibo.
- `assinMudar(c, plano, ha, medida, chave)` recebe a medida do dia (R7 precisa dela).
- Talhão sem parcela é o único que o CD-01 deixa inativar; por isso o roteiro de inativar/reativar usa o B1 (Boa Vista).

Testes de navegador e ajustes vistos neles: `670a29a`. Testes por critério estão nos arquivos `assinatura_unit_test.py` (A1–A7, A10, A12, A17, A18 sem navegador), `assinatura_test.py` (CF-05, faixa, trava, 390 px) e `plataforma_test.py` (BO-02, BO-01, 390 px).

**Executado (06/10, um por vez sob o flock, em retrato do `_render`):** `assinatura_unit_test.py` 46/46 + S0; `assinatura_test.py` 42/42; `plataforma_test.py` 19/19; `varredura.py` 138/138; `acoes_duplicadas.py` 138 páginas, 0 com ação repetida; `obotest.py` 12/12; `cftest.py` 37/37; `cadf_test.py` 15/15; `cadf_det_test.py` 13/13; `talmapa_test.py` 8/8; `acao_unica_test.py v3` 10/10; `links_ocultos_test.py` 7/7; build 0 FALHA em cada commit. Na árvore final: `varredura.py` 138/138 e `acoes_duplicadas.py` 0 com ação repetida. Não rodados por este módulo: os demais testes do protótipo e os vermelhos conhecidos da base.
