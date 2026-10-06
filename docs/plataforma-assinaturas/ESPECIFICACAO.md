# Plataforma de assinaturas · especificação (PLAT-01)

**Pedido do proprietário (Adrianus, 05/10/2026):** "adicione configurações e plataforma de assinaturas na ordem mais correta possível de prioridade". Diretriz permanente: essencialismo, uma ação primária por tela, tudo no mesmo estado, sem redigitação.

**Rótulos.** Tudo é **especificado**, salvo o marcado **executado**. Nenhum código foi editado. Base `9c617c4`, branch `claude/v44-plataforma`. Autor: Claude. Revisor: Codex. Decisões tomadas sem o proprietário: `DECISOES.md` (PLAT-D01..D16).

**Executado (leitura e sondas, 05–06/10):**
- Leitura de `gen37/areas/onboarding_backoffice.py` (BO-01..04 e detalhes), `areas/configuracoes.py:469-553` (CF-05, CF-05det), `ui37.py`, `engine.py:1427-1449`, `cenario.py`, `cenario.js`, `talmapa.js`, `areas/cad_fazendas.py`, `dados_cad.py`; PRD 5 (BO-01..04, CF-05), 18.3, 57, 58, 70.4 (DEC-01/05/09).
- `python3` com `Decimal` sobre os cadastros: Santa Rita 1.165 ha (8 talhões) + Boa Vista 120 ha (B1) + Lagoa Grande 1.285,23 ha (23 pivôs da demonstração sintética) = **2.570,23 ha**; 10 pessoas no CD-04, **9 com login**.
- `node` com `cenario.js`: `2570.23*1.5` = 3855.3450000000003; soma em ponto flutuante das áreas = 2570.2299999999996; `cenQtd(1.5,2570.23)` = **3855.35** e `cenQtd(2,2570.23)` = **5140.46** (decimal exato, meio para cima).

**Abreviações:** `gen37/` = `tools/prototipo/v37/gen37/` · PRD = `/home/user/Safrion-Software-/docs/PRD.md` v3.9.

---

## 0. Mapa: fica, muda, sai

| Peça | Onde | Decisão | Passo |
|---|---|---|---|
| Menu de 5 grupos | `ui37.py:35-41` | **muda**: grupo `('Configurações','grid',[('Assinatura e cobrança','CF-05.dc.html')])` no fim | P2 |
| Grupo de 1 item vira link com o nome do grupo | `ui37.py:60` | **muda**: só quando o rótulo do item é igual ao do grupo (Mapa); Configurações abre como grupo e mostra o item | P2 |
| CF-05 com plano em texto, 9 áreas fixas, 3 faturas fixas e contestação por talhão | `configuracoes.py:469-524` e constantes `:24-33` | **sai** de lá; tela nova em `areas/assinatura.py`, mesmo arquivo `CF-05.dc.html`, título "Assinatura e cobrança" (PRD 57.5), lendo o estado | P2 |
| CF-05det (memória de set/2026) | `configuracoes.py:526-553` | **sai**: a memória é o detalhe da linha da fatura | P2 |
| BO-01 + BO-01det (versões, aprovar tabela, vincular contrato, simulação 20–1.000 ha) | `onboarding_backoffice.py:238-337` | **muda**: BO-01 "Planos e preços" só de leitura dos parâmetros + simulação; criar/aprovar versão sai (§9) | P4 |
| BO-02 + BO-02det (assinaturas, faturas, linha do tempo da Aurora) | `onboarding_backoffice.py:340-425` | **muda**: BO-02 lista organizações do mesmo estado; linha do tempo vira detalhe da linha | P4 |
| BO-03 + BO-03det (medição, contestação, AJ-009/010) | `onboarding_backoffice.py:428-539` | **sai**: medição é o detalhe da organização no BO-02; contestação mínima no P6 | P4, P6 |
| BO-04 (coortes, CAC, LTV) | `onboarding_backoffice.py:542-582` | **sai** (§9) | P4 |
| Dados locais `CTX_BO`, `CONTRATANTES`, `OFERTAS`, `PLANOS`, `FATURAS`, `MEDICAO`, `COORTES` | `onboarding_backoffice.py:21,26-66` | **saem**; entra `dados_assinatura.py` (fonte única do seed) | P1 |
| ON-01 e ON-01det, ajudantes, `CTX_ON`, `TRIAL` | `onboarding_backoffice.py:22,25,68-235` | **ficam** intocados | — |
| `cenDec`/`cenQtd` (decimal, 2 casas, meio para cima) | `cenario.js:29-40` | **fica**: é a regra de dinheiro também (valor = preço × área) | P1 |
| Estado único | `cenario.py:80`, `cenario.js:11-19` | **muda**: `c.assin` no seed; cenário salvo sem `assin` recebe a do seed ao ler; `CEN0.v` **não** sobe | P1 |
| Mescla base + salvo dos talhões | `talmapa.js:7-11` (`tmBase`), `cad_fazendas.py:179-180` | **fica**; `assinatura.js` aplica a mesma regra numa função pura, testada contra o `tmBase` (PLAT-D16) | P1 |
| Pessoas com login | `dados_cad.py:77-88` | **fica**; lido na geração (o CD-04 não grava no navegador) | P1 |
| Valores do motor em toda tela | `engine.py:1435`, `engine.py:1449` | **muda**: anexa `assinatura.js` e chama `assinAvisoVals(this,v)` | P3 |
| Cabeçalho da casca | `ui37.py:326-332` | **muda**: faixa de cobrança abaixo do título (só web; `mobile37`, `ui37.py:356`, não muda) | P3 |
| Botões que criam talhão | `cad_fazendas.py:257,261` (`g_tal_new`); `talmapa.js:59` (`tmIniciar` novo), `:164` (importar), `:24-25` (`tmSalvar` novo) | **muda**: trava de inadimplência antes de abrir o desenho ou o formulário | P5 |
| Telas que deixam de ser geradas | `build.py:23` | **muda**: + CF-05det, BO-01det, BO-02det, BO-03, BO-03det, BO-04 | P2, P4 |
| Índice e listas de exceção | `indice.py:15,54`; `links_ocultos_test.py:32`; `acao_unica_test.py:394`; `heights_override.json:9-14,28-29` | **muda**: Backoffice aponta para BO-02 (2 telas); entradas das telas que saem são removidas | P4 |
| Testes antigos | `obotest.py` (77 linhas), `cftest.py:75-81` | **mudam** com motivo no commit: as telas e números testados saem (§8) | P2, P4 |

## 1. Missão e princípios

A organização sabe, numa tela, **quanto paga, por quê e o que fazer**; a plataforma vê todas as organizações no mesmo estado. Princípios:
1. Cobrança simulada, nunca real: nenhum provedor, nenhuma credencial; tudo rotulado "simulado".
2. Preço, mínimo, franquia, trial, calendário e régua são **parâmetros de exemplo, a decidir pelo proprietário** (DEC-01, DEC-05, DEC-09), numa tabela só.
3. Uso lido dos cadastros, nunca digitado aqui; fatura fechada nunca é recalculada.
4. Inadimplência avisa e restringe aos poucos, **nunca apaga dado nem para trabalho de campo**.
5. O agricultor não vê o backoffice; o backoffice não vê dado agronômico (PRD 57.5).

## 2. Menu e telas: antes → depois

| Antes (9 telas, todas ocultas) | Depois (3 telas) | Natureza | Onde |
|---|---|---|---|
| CF-05 Assinatura e medição + CF-05det | **CF-05 Assinatura e cobrança** | controle (uso e faturas) com duas execuções: pagar, aceitar mudança | Menu › Configurações |
| BO-02 + BO-02det + BO-03 + BO-03det | **BO-02 Assinaturas e cobrança** (plataforma) | execução (conciliar) e controle da carteira | Oculto; Índice › Backoffice |
| BO-01 + BO-01det | **BO-01 Planos e preços** | planejamento comercial (parâmetros) | Oculto; telas irmãs do BO-02 |
| BO-04 | — | sai (§9) | — |

BO-01 e BO-02 usam `secoes_nav` (telas irmãs, `ui37.py:113`), perfil "Admin plataforma". CF-05 usa o perfil "Ana · Gestora" até existir o "Ver como" (§9).

## 3. Telas

### 3.1 CF-05 · Assinatura e cobrança
**Pergunta:** quanto vou pagar, por quê, e o que preciso fazer?
**Cabeçalho:** título; selo do estado da assinatura (§4 R10) + selo "Cobrança simulada"; **uma ação primária**, pela ordem (R14): `Pagar fatura` › `Ampliar área contratada` › `Alterar plano ou área`.
**Resumo (4 números):** Plano ("Completo · R$ 2,00/ha·mês"); Área medida ("2.570,23 ha de 2.600 ha contratados"); Prévia do período ("R$ 5.140,46 · set/2026 fecha em 30/09"); Próxima cobrança ("01/10/2026").
**Bloco 1 · Uso medido (grade):** colunas Fazenda · Talhão · Área cultivável (`2.570,23 ha` na célula, soma no rodapé) · Situação ("Conta na medição" / "Inativo · fora") · Origem ("Cadastros › Fazendas, áreas e talhões"). Filtro de texto, filtro rápido por fazenda, ordenação por qualquer coluna (padrão: área decrescente). Linha → detalhe de origem (só leitura) com o link "Abrir no cadastro" (`CD-01det.dc.html#talhao=<id>`). Abaixo, uma linha: "Pessoas com acesso: 9 (Cadastros › Pessoas e equipes) · usuários sem limite · não entram na cobrança". Aviso quando medida > contratada: "20,23 ha acima da área contratada não entram na cobrança até o aceite".
**Bloco 2 · Faturas (grade):** Competência · Área cobrada (`ha`) · Regra ("R$ 2,00/ha·mês · mínimo R$ 299,00") · Valor (`R$`) · Vencimento · Estado. Filtro de texto e rápido por estado; ordenação (padrão: competência decrescente). Linha → **detalhe (memória)**: medida, contratada, cobrada = mín(medida; contratada), conta `máx(mínimo; preço × cobrada)`, versão da medição ("fechamento 30/09 · 32 talhões"), "pela área contratada seria R$ 5.200,00 (DEC-01, a decidir pelo proprietário)", eventos (emitida, tentativa, paga `evt_…`). No detalhe de fatura A vencer ou Vencida: `Pagar fatura` (= primária) e `Contestar fatura` (P6).
**Bloco 3 · Planos (grade, 3 linhas):** Plano · Módulos · Limite de área · Usuários · Franquias · Preço R$/ha·mês · Mínimo R$/mês · **Valor para a sua área** (`R$` com a área medida, calculado pela mesma função) · selo "Seu plano" ou "Agendado para 01/10". Cada parâmetro com o selo "exemplo · a decidir pelo proprietário". Filtro e ordenação da grade padrão. Linha → painel **Alterar plano ou área**:
- campos: Plano (lista curta, um toque: Essencial, Completo); Área contratada (número com "ha"; preenchida com a atual; ajuda "medida hoje: 2.570,23 ha"); Início (calculado: dia 1 do próximo ciclo, só leitura);
- **prévia** viva: hoje → depois (plano, área cobrada, mensalidade, diferença por mês e o que muda nos módulos);
- confirmar: `Aceitar e agendar para 01/10/2026`; mudança agendada mostra `Desfazer mudança` no mesmo painel.
**Bloco 4 · Demonstração (amarelo, rotulado "só demonstração"):** "Data simulada da cobrança": 23/09/2026 · 01/10/2026 · 06/10/2026 · 16/10/2026 (só avança) e `Restaurar assinatura da demonstração` (zera `c.assin`).
**Estados da tela:** em dia sem pendência; fatura a vencer; em atraso; inadimplente; acima do contratado; mudança agendada; em contestação (P6).
**Celular 390 px:** resumo em 2 × 2; grades com a 1ª coluna fixa e rolagem interna; primária sempre no cabeçalho; painel ocupa a largura; prévia em lista "hoje → depois", sem tabela.

### 3.2 BO-02 · Assinaturas e cobrança (plataforma)
**Pergunta:** quem paga quanto, quem está atrasado e o que conciliar?
**Primária:** `Conciliar pagamentos` (processa os eventos simulados do provedor, uma vez cada).
**Resumo:** Mensalidades vigentes (R$); Organizações por estado; Faturas abertas (quantidade · R$); Área medida paga (ha).
**Grade:** Organização · Plano · Estado · Área medida (`ha`) · Área contratada (`ha`) · Mensalidade (`R$`) · Fatura aberta (competência · estado) · Próximo evento. Filtro de texto, rápido por estado e plano, ordenação. Linha → detalhe: totais por **fazenda** (sem talhão, sem cultura), faturas, eventos, e para a organização da demonstração `Ver como o cliente vê` (CF-05). Na contestação aberta: `Resolver contestação` (P6).
**Celular 390 px:** igual ao CF-05.

### 3.3 BO-01 · Planos e preços
**Pergunta:** quanto cada plano cobra por área, e o que falta o proprietário decidir?
**Primária:** `Simular área` (painel: hectares → mensalidade de cada plano).
**Grade 1 · Parâmetros:** Plano · Módulos · Limite de área · Usuários · Franquias · Preço R$/ha·mês · Mínimo R$/mês · Equivalente R$/ha·ano · Decisão pendente (DEC-01/05/09). Linha → detalhe só leitura.
**Grade 2 · Simulação fixa (PRECO-03):** 20, 100, 149,5, 500, 1.000 e 5.000 ha × planos (`R$` na célula), filtro e ordenação.
**Texto curto:** PRECO-01 (R$ 2,00/ha·mês = R$ 24,00/ha·ano), mínimo pelo maior valor, mudança nunca retroage.

## 4. Regras (testáveis; o dano que cada trava evita)

R1. **Medida** = soma da área cultivável (`decl`) dos talhões com situação Ativo em fazendas Ativas, do cadastro (base da geração + o salvo em `talhao-os-cd01-v1`, mesma regra do `tmBase`). Soma em centésimos inteiros. Safra, parcela, consórcio e operação não entram: a unidade é o talhão (PRECO-02), e o CD-01 e o Mapa já impedem sobreposição (`talmapa.js:49`).
R2. **Cobrada** = mín(medida; contratada). Acima do contratado não se cobra sem aceite (PRD 57.2). *Dano evitado: cobrança-surpresa ao desenhar um talhão.*
R3. **Mensalidade** = máx(mínimo; `cenQtd(preço, cobrada)`) − crédito do período (nunca < 0). Mínimo é o maior, não se soma (PRECO-03). Uma função, `assinMensalidade`, usada por CF-05, BO-01, BO-02 e prévia.
R4. Período = mês civil; fecha no último dia; a fatura guarda a cópia da medição (área, plano, preço, mínimo, contratada, nº de talhões) e **nunca é recalculada**. *Dano evitado: reescrever cobrança já emitida.*
R5. Emissão e vencimento no dia 1 do mês seguinte; 3 tentativas em 10 dias (exemplo, PRD 57.4.1).
R6. Mudança de plano ou área vale do dia 1 do próximo ciclo; nunca retroage (PRECO-04).
R7. Área contratada no aceite ≥ medida do dia. *Dano evitado: contratar 100 ha e gerir 2.570 ha pagando o mínimo.*
R8. Aceite, pagamento e conciliação levam chave de idempotência gerada por quem inicia (ao abrir o painel); repetir a chave devolve o mesmo recibo sem novo efeito; pagar fatura já paga com outra chave não paga de novo (PRECO-08).
R9. Fatura só fica Paga por evento (simulado) do provedor: na organização da demonstração o evento chega na hora; nas demais, por `Conciliar pagamentos`. Evento visto uma vez (`evt` registrado).
R10. **Estado da assinatura** (derivado, não gravado): Em avaliação · Ativa · Em atraso (fatura vencida há 1–10 dias) · Inadimplente (11 dias ou mais) · Cancelada. Fatura Pendente (evento a conciliar) e Em contestação não contam dias.
R11. **Em atraso:** faixa amarela em todas as telas web para a gestão, com o verbo "Pagar fatura" e link ao CF-05; nada restrito. O app de campo nunca mostra cobrança.
R12. **Inadimplente:** faixa vermelha; não amplia o uso: `Cadastrar talhão` (CD-01), `Desenhar` e `Importar` talhão novo (Mapa) recusam antes de abrir, com motivo e caminho ("Pague a fatura de set/2026 em Configurações › Assinatura e cobrança"). *Dano evitado: crescer o uso (e a dívida) sem pagar.* Editar talhão existente, contorno novo de talhão existente e inativar continuam.
R13. **Nunca restringe:** O.S. (emitir, aprovar, liberar, entregar, apontar, conferir, encerrar), receituário, irrigação, manutenção, estoque, consulta. *Dano evitado: empurrar o trabalho de campo para fora do sistema, sem aprovação agronômica, carência e rastreio.* Nada é apagado em estado algum.
R14. Primária do CF-05 (uma): fatura vencida ou a vencer → `Pagar fatura`; senão medida > contratada → `Ampliar área contratada` (painel com Completo/atual e área = medida arredondada para cima à centena); senão `Alterar plano ou área`.
R15. Plano Essencial não inclui os módulos de colheita/pós-colheita, comercial/logística e gestão; o núcleo (Mapa, Cadastros, Agrícola com O.S. e app, Manutenção, Suprimentos) está em todos. *Dano evitado: O.S. sem reserva de estoque ou sem bloqueio de máquina por plano partido.* Hoje nenhum desses módulos está no menu: a prévia diz o que mudaria; a trava de consulta entra com eles (§9).
R16. Contestação (P6): congela a régua da fatura; resolução "Manter valor" (novo vencimento = data + 5 dias) ou "Creditar no próximo período" (crédito ≤ valor, linha negativa na próxima fatura). Fatura contestada não é reescrita. *Dano evitado: restringir cliente por cobrança que ele contesta.*
R17. BO mostra área por fazenda e por organização, nunca talhão, cultura ou operação (PRD 57.5).

Unidades: `ha` e `R$` na célula (DEC-0510-02); rótulos "Preço R$/ha·mês", "Mínimo R$/mês". Unidade de produtividade (DEC-0510-03) não se aplica. Kanban de 5 fases e aprovação agronômica: intocados (R13).

## 5. Integração com o estado único e com os outros módulos

| Lê | De onde | Para |
|---|---|---|
| Talhões, fazendas, situação, área cultivável | CD-01: base da geração (`cad_fazendas._faz_rows/_tal_rows`) + `talhao-os-cd01-v1` | medida (R1) |
| Pessoas com login | `dados_cad.PESSOAS` (geração) | linha informativa |
| Assinatura, contratos, faturas, eventos, recibos, data simulada | `cenGet().assin` (`talhao-os-cenario-v1`) | CF-05, BO-01, BO-02, faixa, trava |

| Grava | Quem | Função (em `assinatura.js`, via `cenMudar`) |
|---|---|---|
| pagamento + evento + recibo | CF-05 | `assinPagar(c, fat, forma, chave)` |
| mudança agendada (contrato vN) | CF-05 | `assinMudar(c, plano, ha, chave)` / `assinDesfazer(c)` |
| data simulada e fechamento do período | CF-05 (demonstração) | `assinAvancar(c, data, medida)` |
| conciliação | BO-02 | `assinConciliar(c, chave)` |
| contestação e resolução (P6) | CF-05 / BO-02 | `assinContestar`, `assinResolver` |

Funções puras (sem gravar): `assinMedir(cad0, salvo)`, `assinMensalidade(plano, medida, contratada, credito)`, `assinEstado(org, hoje)`, `assinPrimaria(org, medida)`, `assinTrava(acao)` (lê o estado; devolve "" ou o motivo), `assinAvisoVals(self, v)` (faixa). Outras telas atualizam por `cenOuvir` (evento `storage`). Módulos de colheita, comercial e configurações (CF-01..04) passam a ler `assinTrava` quando entrarem no menu.

## 6. Seed sintético (`dados_assinatura.py`; números fecham)

Organização da demonstração **Grupo Santa Rita** (3 fazendas do cadastro). Plano Completo. Contrato v1 desde 01/07/2026, 1.200 ha (aceite 28/06); v2 desde 01/09/2026, área = medida da base arredondada para cima à centena (**2.600 ha** com a Lagoa sintética; aceite 28/08, entrada de Boa Vista e Lagoa Grande).

| Competência | Medida | Cobrada | Conta | Valor | Estado em 23/09 |
|---|---|---|---|---|---|
| jul/2026 | 1.165,00 ha | 1.165,00 ha | máx(299; 2,00 × 1.165) | R$ 2.330,00 | Paga 01/08 · `evt_demo_0801` |
| ago/2026 | 1.165,00 ha | 1.165,00 ha | idem | R$ 2.330,00 | Paga 01/09 · `evt_demo_0901` |
| set/2026 | 2.570,23 ha | 2.570,23 ha | máx(299; 2,00 × 2.570,23) | R$ 5.140,46 | Em medição (fecha 30/09) |

Outras organizações (medição informada pelo inquilino, sintética):

| Organização | Plano | Contratada | Medida | Mensalidade | Situação em 23/09 |
|---|---|---|---|---|---|
| Fazenda Aurora | Completo | 60 ha | 35 ha | máx(299; 70,00) = R$ 299,00 | ago R$ 299,00 vencida 01/09, 3 tentativas recusadas → Inadimplente |
| Sítio Ipê | Essencial | 20 ha | 20 ha | máx(199; 30,00) = R$ 199,00 | Ativa, em dia |
| Agro Bela Vista | Completo | 320 ha | 333 ha | 2,00 × 320 = R$ 640,00 | ago R$ 640,00 Pendente (`evt_1JKT5` a conciliar); 13 ha acima do contratado |
| Org. Boa Esperança | Avaliação | — | 480 ha declarados | R$ 0,00 | dia 5 de 30 (19/09 → 18/10), sem cartão |
| Rancho Dois Rios | Essencial | 40 ha | — | — | Cancelada 31/08 a pedido; consulta e exportação até 29/11 |

Fila do provedor: `evt_1JKT5` (Bela Vista, R$ 640,00, aprovado) e `evt_1JKR9` (Aurora, recusado). Totais do BO-02 em 23/09: mensalidades vigentes 5.140,46 + 299,00 + 199,00 + 640,00 = **R$ 6.278,46**; Ativa 3 · Em avaliação 1 · Inadimplente 1 · Cancelada 1; faturas abertas **2 · R$ 939,00** (depois de conciliar: 1 · R$ 299,00); área medida paga 2.570,23 + 35 + 20 + 333 = **2.958,23 ha**.

Planos (exemplo, a decidir): **Avaliação** 30 dias, R$ 0, limite = área declarada, todos os módulos, satélite 12 cenas e IA 200 interações no período, consulta e exportação 90 dias após o fim (DEC-09) · **Essencial** núcleo, R$ 1,50/ha·mês, mínimo R$ 199, até 5.000 ha, usuários sem limite, satélite 6 cenas/mês, IA 100/mês · **Completo** núcleo + colheita/pós-colheita, comercial/logística, gestão e integração ERP em sandbox, R$ 2,00/ha·mês (hipótese PRD 57.2), mínimo R$ 299, até 5.000 ha, usuários sem limite, satélite 12 cenas/mês, IA 200/mês (franquias do BO-01det atual).

Roteiro de números (data simulada da organização da demonstração; as outras não fecham período):
- 01/10: set fecha com 2.570,23 ha → R$ 5.140,46, vence hoje; out/2026 abre em medição.
- 06/10: vencida há 5 dias → Em atraso (faixa amarela). 16/10: há 15 dias → Inadimplente (faixa vermelha, R12).
- Trocar para Essencial em 23/09: prévia R$ 5.140,46 → **R$ 3.855,35** a partir de 01/10 (−R$ 1.285,11/mês); set fecha em Completo.
- Talhão novo de 50 ha em 23/09: medida 2.620,23 ha; cobrada 2.600 ha → R$ 5.200,00; aviso de 20,23 ha; `Ampliar` sugere 2.700 ha → R$ 5.240,46 a partir de 01/10.
- BO-01: 20 ha → 299,00 / 199,00; 100 → 299,00 / 199,00; 149,5 → 299,00 / 224,25; 500 → 1.000,00 / 750,00; 1.000 → 2.000,00 / 1.500,00; 5.000 → 10.000,00 / 7.500,00 (Completo / Essencial).

No Mac (KML real da Lagoa), a medida e a contratada v2 mudam: os testes calculam a expectativa pela mesma regra a partir das linhas do cadastro.

## 7. Passos (cada um deixa o protótipo funcionando)

- **P1 · Estado e regras.** `dados_assinatura.py` (seed §6, planos, parâmetros com rótulo de decisão); `assinatura.js` (funções §5); `cenario.py:80` ganha `assin`; leitura sem `assin` usa a do seed. Teste: `node assinatura_unit.js`.
- **P2 · CF-05 no menu.** `areas/assinatura.py` (§3.1), menu e regra do grupo de 1 item (`ui37.py:35-41,60`), remover CF-05/CF-05det de `configuracoes.py`, `build.py:23`, novo `assinatura_test.py` (CF-05), `cftest.py` sem a parte CF-05 (motivo no commit).
- **P3 · Faixa de cobrança.** `engine.py:1435,1449` e `ui37.py:326-332`. Teste: faixa em OS, EST e CD-01 com data 06/10 e 16/10; nada no MB-01.
- **P4 · Plataforma.** `areas/plataforma.py` com BO-01 e BO-02 (§3.2, §3.3); `onboarding_backoffice.py` fica só com ON; índice, listas de exceção e `heights_override.json`; `obotest.py` substituído por `plataforma_test.py` (motivo: telas e números novos).
- **P5 · Trava de inadimplência.** `assinTrava('ampliar_area')` nos 4 pontos do §0, antes de abrir formulário ou desenho; `tmSalvar` novo também recusa (defesa). Teste no `assinatura_test.py`.
- **P6 · Contestação mínima.** R16 no detalhe da fatura (CF-05) e no detalhe da organização (BO-02).

Em cada passo: `python3 build.py > /tmp/PLAT-build.log; grep -c FALHA /tmp/PLAT-build.log` = 0; `python3 montar_render.py`; navegador um por vez com `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdp9333.lock env CDP_GL=1 timeout 900 python3 <teste>`: `varredura.py`, `../ferramentas/acoes_duplicadas.py . /tmp/PLAT-dup.json`, os testes do módulo e os existentes; vermelhos da base listados no pedido não são deste módulo e não são escondidos.

## 8. Critérios de aceite (teste que prova)

| # | Critério | Teste |
|---|---|---|
| A1 | Medida = soma decimal da área cultivável dos talhões ativos (base + salvo); inativo e fazenda inativa saem; igual ao `tmBase` | `assinatura_unit.js` |
| A2 | `assinMensalidade`: tabela da §6 inteira (inclui 3.855,35 e 224,25) e mínimo pelo maior | `assinatura_unit.js` |
| A3 | Fatura fechada não muda após editar, criar ou inativar talhão | unit + `assinatura_test.py` |
| A4 | Mudança agendada vale de 01/10; set fecha no plano antigo; desfazer antes de 01/10 volta ao anterior | unit + navegador |
| A5 | Área contratada abaixo da medida é recusada no aceite, com o motivo | unit + navegador |
| A6 | Mesma chave de pagamento ou aceite repetida: um efeito, mesmo recibo; fatura paga não paga de novo | unit |
| A7 | Estados por data: 23/09 Ativa; 01/10 a vencer; 06/10 Em atraso; 16/10 Inadimplente; pagar volta a Ativa | unit + navegador |
| A8 | Faixa amarela/vermelha em OS, EST e CD-01 com "Pagar fatura"; nenhuma no MB-01 | `assinatura_test.py` |
| A9 | Inadimplente: Cadastrar talhão, Desenhar e Importar recusam antes de abrir; editar talhão existente e todas as ações de O.S. seguem | `assinatura_test.py` |
| A10 | Talhão novo de 50 ha no Mapa: CF-05 mostra 2.620,23 ha, aviso de 20,23 ha e primária `Ampliar área contratada` | `assinatura_test.py` |
| A11 | Uma primária por tela em CF-05, BO-01, BO-02 em todos os estados | `acao_unica_test.py`, `acoes_duplicadas.py` |
| A12 | BO-02: totais da §6; pagar no CF-05 aparece Paga no BO-02; conciliar duas vezes não duplica | `plataforma_test.py` |
| A13 | BO-02 detalhe sem talhão e sem cultura | `plataforma_test.py` |
| A14 | Toda grade com filtro e ordenação; `ha` e `R$` na célula | `varredura.py` + teste do módulo |
| A15 | 390 px: primária visível, resumo 2 × 2, sem rolagem horizontal da página | `assinatura_test.py` (captura) |
| A16 | Menu: Configurações por último, com "Assinatura e cobrança"; Mapa segue como link único | `assinatura_test.py` |
| A17 | Contestação congela a régua; resolver com crédito aparece na fatura seguinte (P6) | unit + navegador |

## 9. Fora de escopo (condição de retorno)

| Item | Volta quando |
|---|---|
| Criar, revisar e aprovar versão de plano; vincular contrato (BO-01 antigo) | o proprietário decidir DEC-01/05/09 e pedir a tabela aprovada |
| Cancelar assinatura pelo cliente e o "somente consulta" depois do fim do ciclo | `cenMudar` ganhar nome de comando (SUP-2a) para aplicar consulta sem listar telas |
| Trava de consulta dos módulos fora do plano Essencial | colheita, comercial ou gestão entrarem no menu |
| Restrição de serviços pagos (satélite, IA) | existir serviço pago real ou simulado com franquia medida |
| Planos de parceiros e patrocínio (Fertisul, Coop. Verde Vale; PT-07) | DEC-05 e o portal do parceiro voltar ao menu |
| Economia da plataforma (BO-04: coortes, CAC, LTV) | houver 3 coortes com 90 dias observados (PRD 57.3) |
| Pró-rata, faixas marginais acima de 5.000 ha, plano anual, desconto | decisão comercial do proprietário (PRD 57.2) |
| Trial do ponto de vista do agricultor (avisos de fim, contratar) | ON-01 voltar ao menu |
| Quem pode pagar e alterar plano (só gestão) | "Ver como" (G2_PERFIS, CTL-3 frente D) integrado |
| Pessoas lidas do estado do navegador | CD-04 gravar no navegador ou CF-01 existir |
| Exportação completa dos dados | CF-04 (Configurações) |
| Provedor de pagamento, nota fiscal, cobrança real | nunca no protótipo; no software real só com autorização e custo aprovados pelo proprietário (AGENTS §2) |
