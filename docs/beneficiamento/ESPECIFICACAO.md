# Beneficiamento (grãos, frutas/HF e café) · v2

**Resultado útil:** a ordem de processo entra no menu em Produção › Beneficiamento. No BEN-1, o packing de mamão vai da ordem ao lote vendável reservado, com caixas, balanço, qualidade e estoque no mesmo cenário da O.S., do Estoque e da Manutenção. Grãos e café vêm nos blocos seguintes.

- **Rótulo:** especificado. Nada foi implementado. Só o que traz "(executado)" saiu de comando rodado em 05/10/2026: contas em `verificacao/contas.py` (Python `decimal`) e buscas no código (DECISOES.md §8).
- **Versão 2**, de 05/10/2026. Aplica os 42 achados confirmados da revisão adversarial (DECISOES.md §9).
- **Papéis:** autor Claude · revisor Codex (produto, aceite, QA) · integrador quem não for o autor (AGENTS §3).
- **Contrato:** PRD v3.9. "l.N" é a linha de `docs/PRD.md`. A reserva de material segue a **DEC-2609-13** (l.12227: reserva na liberação).
- **Pedido do proprietário (05/10/2026):** Beneficiamento volta ao menu do protótipo. É pedido, não aprovação deste desenho (portão P1).
- **Base lida (só leitura):** `/home/user/sp-tab5`, branch `claude/v44-tabelas-05`, HEAD `0cf6f90`. `gen37/` = `/home/user/sp-tab5/tools/prototipo/v37/gen37/`; `v37/` = `/home/user/sp-tab5/tools/prototipo/v37/`; `pcm/` = `docs/pcm-suprimentos/ESPECIFICACAO.md`.
- **Arquivos irmãos:** `FORA-DE-ESCOPO.md` e `DECISOES.md`.
- **Fonte única:** números só no §10 (casos K-nn); regras só no §4; testes só no §11; aceite no §12, como matriz AC → regra → caso → teste.
- **Dados:** todos sintéticos (ENG-017; DEC-2709-01). Pessoa nova só com zero ocorrências no `v37/` (§2.3).

---

## 0. Como executar

### 0.1 Portões (antes do primeiro commit)

| # | Portão | Por quê | Quem |
|---|---|---|---|
| P1 | Registrar em `docs/DECISIONS.md` a decisão de 05/10/2026: "Beneficiamento volta ao menu do protótipo como Produção › Beneficiamento; o resto de Colheita e pós-colheita segue oculto". | Muda o recorte do PRD 71.6 (l.10359). `docs/DECISIONS.md` não tem entrada sobre beneficiamento (executado: busca). | Codex registra; fonte: pedido no canal do Claude |
| P2 | TABELAS-FOCO 2b, 2c e 2d com PR aberto e bateria verde, executada e com hash. Hoje: 2b no PR #42; 2c `e1091d5` e 2d `0cf6f90` sem PR (`v37/RETOMADA-NUVEM.md:207, 215`). | AGENTS §3.1: consolidar rascunhos antes de abrir frente. | Integrador da TABELAS-FOCO |
| P3 | PCM × suprimentos Bloco 1 integrado: PRs 1a, 1b e 1c (`pcm/` §11.2). O mínimo pedido é o 1a; o 1b e o 1c entram no portão pelos motivos ao lado. | O BEN-1 reaproveita peças que nascem no PCM 1b: `cenProxId`, `cenOrdem`, `cenMudar(self, fn, cmd)` com recibo e versão (PCMS-G04), entrega no balcão e recebedor herdado (PCMS-M14). O BEN-1 e o PCM 1c editam `areas/processo_estoque.py`. Uma frente ativa por vez (AGENTS §3.1). | Codex decide a fila; se mudar a ordem, vale §0.2 |
| P4 | Acordo curto do §11.1 registrado na rodada. O Codex escreve a tarefa e o roteiro; o Claude revisa. | AGENTS §3.1 passo 1; §3.4. | Codex |
| P5 | Cinco referências do setor para o módulo, com fonte e data. O PRD 45.7 (l.7572) traz três; faltam duas. | AGENTS §3.3. Bloqueia o aceite, não o código. | Codex |
| P6 | TABELAS-FOCO 2e "Colunas configuráveis na G2" (§5.2). Se o Codex não abrir agora, vale o plano B do §5.2. | PRD 4.3 l.287: tabela começa com até sete colunas. A G2 não oculta coluna (`engine.py:1169`). | Codex |

### 0.2 Versão do cenário e arquivos compartilhados

| Frente · PR | `v` | Arquivos que as duas frentes tocam |
|---|---|---|
| PCM 1a · 1b · 1c | 4 · 5 · 6 (`pcm/` §3.1, §11.2) | `cenario.py`, `cenario.js`, `areas/processo_estoque.py`, `areas/processo_os.py`, `dados_cad.py` |
| BEN-1b (semente) | 7 | os mesmos, depois do merge do PCM 1c |
| BEN-3 · BEN-4 (sementes de grão e café) | 8 · 9 | `cenario.py`, `dados_ben.py` |

- **Regra única de versão:** quem integra depois faz rebase antes de abrir o PR. Usa `v = v(main) + 1`, com linha de histórico em `cenario.py:79-80`. Não redefine função de `cenario.js` da frente anterior (AGENTS §3.4). Roda as duas baterias.
- **IDs combinados com o PCM:** REQ-032 a REQ-034 são do PCM (`pcm/` §10). A BEN usa **REQ-030**. Pessoas: p11 Otávio é do PCM; p12 Igor e p13 Marta são da BEN; equipe e8 é da BEN. Contagens que mudam nos testes: §11.5.
- **Sequência de inspeção única:** `cenInspId(c)` em `cenario.js` (BEN-1b), usada pela Qualidade e pela Manutenção (`areas/maquinas.py:226, 252` usam INSP-104 e INSP-105). Combinar no acordo P4 com o autor do PCM.

### 0.3 Mapa do existente (linhas em `0cf6f90`)

**Fica: reutilizar sem mudar o comportamento**

| Peça | Onde | Uso na BEN |
|---|---|---|
| Casca, seções paralelas, abas, continuidade | `ui37.py:256` (`shell37`), `:480` (`secoes_state`), `:453` (`tabs`), `:204` (`continuity`) | Página-processo |
| Grade G2, filtro rápido, painel, área de ações | `engine.py:1169` (`grid`; `qf` na l.1181 exige a coluna em `cols`), `:1262`, `:1085`, `:1290` | Todas as grades |
| Unidade na célula (2d) | `engine.py` (`_col_un` antes de `grid()`); `g2lib.js:9-11` (`g2unf`) | Rótulo "Entrada (kg)" vira célula "12.000 kg" |
| Recorte guardado | `g2lib.js:17-19` (`g2keep`) | Filtro de segmento |
| Cenário atômico | `cenario.js:11-25` (`cenGet`, `cenReset`, `cenMudar`, `cenOuvir`) | Toda escrita da BEN |
| Do PCM 1a-1c (reaproveitar, nunca redefinir) | `c.man` no CEN0; `cenOrdem`; `cenProxId`; `cenMudar(self, fn, cmd)`; entrega no balcão; recebedor herdado; SC, PC e recebimento no cenário (`pcm/` §3.1, §4A, §4C, §11.2) | REQ, idempotência, entrega, compra de caixa (BEN-2) |
| Caixas por requisição | `cenario.js:48` (`cenLiberar` aceita `dose:0` com `tot`), `:68` (`cenEntregar`), `:81` (`cenDevolver`), `:243` (`cenPodeEncerrar`) | Reserva, entrega, devolução, trava de sobra |
| Ativo e locais | `dados_cad.py:56` (a13 Packing linha 1: `kgh=2400`, `custo_h=120`); `:135-138` (LOCAIS, l8 Packing) | Instalação e local |
| Item caixa | `dados_cad.py:130` (pallet de entrega de 60 caixas vazias), `:133` (R$ 4,80); `areas/cadastros.py:690` (`un`), `:714` (texto "tara 1,2 kg") | Material do packing |
| Fator da saca por item | `areas/cadastros.py:689-690` (Soja em grão e Café beneficiado em `sc 60 kg`) | R-B05 |
| Pessoas | `dados_cad.py:77-88` (Ana p1, Paula p6, Rui p7, Zé p8) | Papéis |
| Condição do ativo | `dados_manutencao.py:42` (a13 `cond='Apto'`); depois do PCM 1a, `c.man.ativos` | R-A13 (exibição) |
| Bibliotecas de teste | `comp_lib.py`, `os_lib.py`, `carencia_test.py:9-32` (JS sem navegador), `quantidade_test.py`, `tabelas_{os,est}_test.py`, `tabelas_inventario.py` | Testes da BEN |

**Muda**

| Arquivo:linha | Mudança | PR |
|---|---|---|
| `ui37.py` | + `chip_hole` e `kanban5` (de `areas/processo_os.py:822-842`, HTML igual, `aria-label` "Kanban das ordens"); + `bloco` e `kline` (de `areas/processo_estoque.py:36-42`) | 1a |
| `areas/processo_os.py` | Importa `kanban5` e `chip_hole` (`:882` e `:969` usam `chip_hole`); mantém o próprio `bloco` (`:816-820`) | 1a |
| `cenario.js:48-63` | `cenLiberar`: ordem sem material libera sem abrir REQ (a regra de `areas/processo_os.py:304-307` numa fonte só) | 1a |
| `cenario.js` | + `cenBalcao(o)` (OM ou `fam:'BEN'`), + `cenInspId(c)`, + `cenEstornarConsumo`; `cenEntregar` (`:68-79`): mensagem de OB "Em custódia de <quem> (<OB>)" | 1b |
| `cenario.py:79-80` | `v` pela regra do §0.2, com linha de histórico; `seed_ben()` | 1b |
| `dados.py:35, 105, 108-111, 115, 119` | A OB-0104 sai; a fonte única passa a ser `dados_ben.py` | 1b |
| `areas/processo_os.py:169` | `_ordens()` pula `fam:'BEN'`, como já pula a irrigação só com água; saem os textos da OB-0104 em `:66, :90, :105, :127, :142` | 1b |
| `dados_cad.py:67-68`, `:73-74`, `:77-88`, `:126-133`; `areas/cad_ativos_pessoas.py:28, 38` | Habilidades novas; equipe e8; p12 Igor e p13 Marta; tara numérica do item caixa (os textos de `areas/cadastros.py:714` e `areas/cad_produtos_estrutura.py:69` derivam dela) | 1b |
| `areas/processo_estoque.py` | `:19` LOCAIS da fonte única (`dados_cad.LOCAIS`, com Packing); `:21`/`:94` recebedor de OB = `o.resp`, opções de `dados_cad`; `:188` motivo para OB; `:273` balcão por `cenBalcao`; `:404, 429, 444, 499, 515` link da OB para `BEN.dc.html#ob=`; `:534` seção por endereço; `:582` texto por família | 1c |
| `ui37.py:35-41` (MENU2) | + `('Produção','box',[('Beneficiamento','BEN.dc.html')])` entre Manutenção e Suprimentos; ícone em `engine.py:42` | 1c |
| `v37/ferramentas/acoes_duplicadas.py:15` | Regex aceita `OB-`, `L\d\d-` (no lugar do literal `L27`), `RC-`, `PV-`, `RS-`, `MP-`; `INSP` já é aceito | 1c |
| `cotest.py:24-29, 62-63, 80` | 12 checagens desatualizadas, com expectativa tirada da fonte | 1c |
| Testes da O.S. (lista do §11.5) | Expectativa sem a OB-0104 | 1b |

**Não existe: criar**
- Página `BEN.dc.html`; coleção `c.ben`; versão de rota como dado; registro de saída com estorno; lote de produção; ID de lote; inspeção gravável com situação; movimento de produção (MP-); reserva de produto acabado; fórmula de massa.
- Igor e Marta no CD-04 (`dados_cad.py:77-88` não tem).
- Ativos de secador, terreiro, beneficiadora e balança: pedido ao autor do PCM, para o BEN-5.

**Fica oculto e não é editado no BEN-1**
- `areas/colheita.py` (CO-01 a CO-07). A BEN substitui CO-05, CO-05det, CO-06det e CO-07 na função. Saem no BEN-5, junto com o CO-04.
- A seção de carência do CO-06 (`areas/colheita.py:653-740`) continua: o Mapa liga para ela (`areas/inicio.py:1076`).
- Comercial, Logística e Gestão continuam ocultos, com texto fixo.

**Defeitos do existente que a BEN corrige e não migra**

| Defeito | Onde | Correção |
|---|---|---|
| "Quebra 1,8 t" mistura água e diferença | `areas/colheita.py:107-108` | Água estimada e diferença em linhas próprias |
| Tolerância oculta de 0,05 t | `areas/colheita.py:467` | Faixa declarada na versão da rota (R-F02) |
| Saca de 50 kg ao lado de saca de 60 kg | `areas/colheita.py:116-119, 597-609` | Fator do item do CD-06 (R-B05) |
| Caixas de 10 e 15 kg | `areas/colheita.py:442-443` | Item do cadastro: 20 kg, tara 1,2 kg |
| OB-0104 rotulada "grãos", com janela em 2025 | `dados.py:105, 119` | Café, janela de 2026 (§10.2) |
| 8.612 sc de milho "após OB-0106" | `areas/colheita.py:607-609` | Removido |
| Estado gravado no ID (`L39-119Q`) | `areas/colheita.py:362` | `L39-119` com qualidade Em inspeção |
| Colunas compostas e 12 `Pt.act` que só mostram aviso | `areas/colheita.py:217-219, 314-315, 360-364, 394-396, 414, 522` | Uma variável por coluna; ações que gravam |

### 0.4 Bateria

```sh
cd /home/user/sp-tab5/tools/prototipo/v37/gen37
# bateria do PCM (pcm/ §0.3), inteira, mais:
python3 ben_unit_test.py && python3 ben_fluxo_test.py && python3 tabelas_ben_test.py
python3 tabelas_os_test.py && python3 os_irrig_filtro_test.py && python3 os_v39_bloq_test.py && python3 os_v39_selo_agua_test.py && python3 ostest.py
python3 ../ferramentas/acoes_duplicadas.py
```
- Todo PR roda a bateria inteira, porque o 1b muda o CEN0 de todas as telas do cenário.
- **Critério:** nenhuma falha nova contra a base, rodada no hash base com a saída guardada.
- **Juízo pela linha RESULTADO/FALHAS de cada log**, não só pelo código de saída. Hoje `os_irrig_filtro_test.py` e `ostest.py` saem com 0 mesmo quando falham (§11.5).

---

## 1. Missão e princípios, em ordem de prioridade

1. **O fato físico é verdadeiro.** Massa pesada não se cria e não some sem registro. Estimativa nunca recusa pesagem. Água estimada não é perda. Embalagem não é fruta.
2. **Qualidade e lei.** Lote não liberado não é vendido nem reservado. Fechar o processo não libera o lote. Lote fora do padrão do pedido não é reservado para ele.
3. **Estoque e dinheiro com custódia.** Caixa e produto só se movem por requisição ou movimento, com quem e quando. Correção é estorno com motivo, nunca edição. Diferença acima da alçada sobe a quem pode decidir.
4. **Uma verdade compartilhada.** Uma ordem, um lote e um saldo, lidos por BEN, Estoque e Manutenção no mesmo cenário. Uma regra por problema: o que o PCM já fez, a BEN reaproveita.
5. **Leveza.** Herdar o contexto. Um toque para lista curta. Uma primária por tarefa. Unidade junto do valor.
6. **Honestidade do dado.** Estimado ≠ medido. Parâmetro técnico vem da versão da rota, com fonte "sintético · vN". Nenhuma norma embutida sem item e vigência.

**Lições aplicadas**

| Lição | Fonte | Onde |
|---|---|---|
| Uma fórmula, um produtor; espelho Python = JS | ENG-011; `quantidade.py:1-9` | `ben.js` e `ben_massa.py` (§11.3) |
| Escala declarada por grandeza; comparar depois de quantizar; exibir não altera o guardado | PRD 10.0 l.4187-4197 | §3.4, R-F04 |
| Rateio por acumulado: a soma fecha sem tolerância | `v37/RETOMADA-NUVEM.md:88` | R-E07 |
| Total 0 e número não finito travam antes da conta; nunca ordem sem entrada | `v37/RETOMADA-NUVEM.md:113, 119, 125-126` | R-A04 |
| Aviso e trava com o mesmo critério | `v37/RETOMADA-NUVEM.md:120` | `benEtapas` (R-A09), `benImpedimentos` (R-A05) |
| Aprovar ≠ liberar ≠ liberar lote | DEC-2609-05; DEMO-19 | R-A05, R-E01 |
| O mesmo fato por dois papéis conta uma vez | R-002:49-50 | Custódia de caixa (R-C02) |
| Estado com rótulo próprio, nunca no ID | `v37/RETOMADA-NUVEM.md:135, 215` | `L39-119` Em inspeção |
| Uma variável por coluna; vínculo múltiplo por ID; vazio filtrável | `g2lib.js:23-26` | §5.2 |
| Total sem somar grupos; razão recalculada | PRD 4.3 l.289; l.8147 | §7; R-B03 |
| Navegar nunca executa | `GUIA-PROCESSOS.md:6-8` | R-G07 |
| Teste executa a recusa; mutante; expectativa tirada da fonte | `v37/RETOMADA-NUVEM.md:107, 146, 164` | §11 |
| Nada de `//` no meio de linha no JS embutido | `v37/RETOMADA-NUVEM.md:215` | `ben.js` em arquivo próprio |

---

## 2. Arquitetura do ciclo

Fluxos do PRD: FL-18 (l.3792; regra essencial em l.10826), FL-BEN-01 Grãos (l.7417), FL-BEN-02 Frutas e HF (l.7464), FL-BEN-03 Café (l.7510). Cada bloco percorre o fluxo da sua rota (§12).

### 2.1 Diagrama

```text
 Lote Recebido/Liberado            (BEN-5: "Receba as cargas" cria o lote)
        │ + Nova ordem · Igor       [entradas elegíveis; rota Aprovada do produto e estágio; entrada > 0]
        ▼
   A LIBERAR ── Autorizar rota e liberar · Igor ──▶ LIBERADAS
        │  2 eventos: CMD-42 autoriza a versão da ordem; CMD-06 libera
        │  causas listadas juntas: lote inelegível · caixas · (após PCM B2: ativo)
        │  efeito: entradas reservadas à ordem; caixas reservadas (cenLiberar); REQ por cenProxId
        │  Estoque entrega no balcão → custódia de Igor
   LIBERADAS ── Iniciar processo · Igor ──▶ EM EXECUÇÃO   [entradas → Em processo]
        │  + Registrar saída / descarte / perda (com ticket) · Igor
        │    Σ pesado ≤ entrada + tolerância; caixas ≤ custódia; umidade final se a rota seca
        │  Estornar registro (motivo) · Igor
        │  Concluir execução · Igor   [≥ 1 saída Produto; avanço da rota completo]
        ▼
   EM CONFERÊNCIA ◀── Reabrir execução · Igor (motivo)
        │  |dif| > faixa → justificar (alçada) · estornar e relançar · perda com ticket (alçada sobre dif₀)
        │  Conferir balanço · Rui
        │  Fechar processo (CMD-23) · Igor  [conferido; custódia 0; em processo 0; controles e etapas]
        ▼
   ENCERRADAS → saídas viram lotes EM INSPEÇÃO + inspeção aberta (Marta, prazo)
                entradas → Esgotado; descarte → Destinado; genealogia gravada
        ▼
 Lote Em inspeção ── Registrar resultado (Conforme | Não conforme) · Marta ── Registrar decisão (CMD-24) · Marta
        ├─ Liberar (só Conforme) ───────────────▶ LIBERADO ── Reservar para pedido · Comercial
        ├─ Liberar como classe atingida ────────▶ LIBERADO na classe nova (mesma massa)
        ├─ Manter bloqueio (motivo, prazo) ─────▶ BLOQUEADO (reservas com expedição impedida)
        └─ Destinar (motivo) ───────────────────▶ DESTINADO (físico 0; rastreio fica)
```

### 2.2 Estados

| Objeto | Estados | Fonte |
|---|---|---|
| Ordem de processo | A liberar → Liberadas → Em execução → Em conferência → Encerradas. Retorno Em conferência → Em execução, com motivo. Rascunho e Cancelada ficam fora do quadro (BEN-6). | l.2760; l.2866-2878 |
| Selos da ordem (nunca coluna) | Impedida · Diferença acima da faixa · Ganho aparente acima da faixa · Corrigido na conferência · Sobra em custódia · Recurso sem cadastro · Atrasada. Depois: Diferença parcial (BEN-3), Falta caixa · SC (BEN-2), Linha parada (após PCM Bloco 2) | AGENTS §4 |
| Qualidade do lote | Recebido · Em inspeção · Liberado · Bloqueado · Em processo · Esgotado · Destinado | l.2758 |
| Estágio físico (campo próprio) | Fruta de campo · Fruta embalada · Grão úmido · Grão seco · Fruto de café · Café em coco · Café beneficiado · Subproduto. Pergaminho entra no BEN-6. | l.7506; BEN-05 |
| Inspeção | Aberta → Resultado registrado (situação Conforme ou Não conforme ao padrão e à versão) → Decidida | FO-15 l.2325 |
| Reserva | Ativa → Cancelada. "Expedição impedida" é situação derivada, não estado gravado (R-E06) | AC-49 l.4809; l.2610 |
| Pedido (situação derivada) | Sem reserva · Parcial · Coberto · Em risco | l.7995 |

### 2.3 Quem move

Não há login no protótipo. Cada comando grava o papel que o PRD lhe dá, como `cenDevolver` grava "Rui (almoxarife)" (`cenario.js:87`). No software real a permissão é do servidor (ADR 0004).

| Papel | Pessoa (sintética) | Cadastro | Comandos |
|---|---|---|---|
| Responsável de produção | **Igor** (novo, p12; zero ocorrências: `grep -rlw Igor` em `v37/`, `docs/` e `pcm/`, executado) | habilidades "Autorizar rota da ordem (produção)" e "Liberar ordem de processo" | Nova ordem, Autorizar rota e liberar, Iniciar, Registrar, Estornar, Concluir, Justificar (até a alçada), Reabrir, Fechar |
| Conferente | Rui | `dados_cad.py:85`, "Conferir" | Conferir balanço; receber devolução no EST |
| Almoxarife | Rui, Paula | `dados_cad.py:84-85`; Rui é o almoxarife em todo o cenário (`pcm/` §3.3) | Entregar caixas no EST |
| Qualidade | **Marta** (reaproveitada, p13) | já é a Qualidade em `areas/colheita.py:513-559` e `dados_carencia.py:183`; falta o cadastro; habilidade "Liberar lote (qualidade)" | Registrar resultado e decisão |
| Gestão (alçada) | Ana | `dados_cad.py:78` (agrônoma e gestora); age como gestora | Justificar e confirmar correção acima da alçada de Igor |
| Comercial | papel simulado | não existe pessoa | Reservar e cancelar reserva |
| Manutenção | Zé, Otávio | `dados_cad.py` p8; p11 do PCM | Condição do ativo, lida pela BEN |

- **Critério de pessoa:** pessoa interna do `v37/` só é reaproveitada no mesmo papel e ativa, com arquivo:linha. Nome novo exige zero ocorrências. Helena (contato do P10, `dados_cad.py:101`) e Davi (usuário revogado em 15/09, `areas/configuracoes.py:9, 110, 433`) ficam de fora. "Marta Nunes" (`areas/parceiros.py:463`, Fertisul) é homônima externa, com sobrenome e organização distintos. "Marta (conferente)" no SU-09 oculto (`areas/suprimentos.py:1037, 1047`) é dívida conhecida (DECISOES.md §1).
- A ordem de processo tem responsável próprio, sem agrônomo (l.2874-2876; CMD-42 l.2825). A O.S. de colheita continua com aprovação agronômica (PRD 41.1).

### 2.4 Rotas

Parâmetros e valores: §10.1. Etapas e quem as cumpre: R-A09 (`benEtapas`).

| Aspecto | Frutas/HF: PACK-FRU v3 | Grãos (milho grão): SEC-GRA v2 | Café: CAF-NAT v1 e CAF-BEN v1 |
|---|---|---|---|
| Bloco | BEN-1 | BEN-3 | BEN-4 (a OB-0104 já aparece no BEN-1, só consulta) |
| Entrada → saída | Fruta de campo → Fruta embalada A e B; outro destino; descarte; perda: avaria no manuseio (pesada) | Grão úmido → Grão seco; perda: impureza retirada | Fruto → Café em coco; coco → Café beneficiado + casca; perdas: impurezas e pó |
| Avanço (R-A08) | No Concluir | Por saída (consumo do lote de entrada) | CAF-NAT por saída; CAF-BEN no Concluir |
| Controles obrigatórios | Caixas e bruto em cada saída Produto | Umidade inicial do lote; umidade final, método e base em cada saída Produto | CAF-NAT: como o grão. CAF-BEN: umidade do coco (herdada do lote) e do beneficiado |
| Material | Caixa de mamão 20 kg, 1 un por caixa | — (lenha, GLP e energia no BEN-7) | — (sacaria no BEN-6) |
| Instalação | a13 Packing linha 1; local do lote: Packing | Secador sem cadastro → aviso | Terreiro e beneficiadora sem cadastro → aviso |
| Balanço | Físico líquido; tara fora | Físico, mais água estimada em matéria seca | CAF-NAT: como o grão, hipótese não validada; CAF-BEN: físico |
| Unidade | un (caixa) e kg | kg; sc 60 kg só no grão seco | kg no fruto e no coco; sc 60 kg só no beneficiado |

Soja, feijão e semente exigem versão própria, com fonte (PRD 45.7). Café descascado, via úmida, pergaminho, fermentação, microlote, blend e reprocesso ficam para o BEN-6.

---

## 3. Modelo de domínio

### 3.1 Entidades

| Entidade | Onde | Campos essenciais |
|---|---|---|
| Ordem de processo | `c.ordens[OB]` com `fam:'BEN'` (mesma coleção da O.S., para reaproveitar `cenLiberar`, `cenEntregar`, `cenDevolver`, `cenPodeEncerrar`, `cenOrdem`) | `id, fam, tipo, talhao` (= local), `area:0, etapa, versao` (versão da ordem, vN), `ver` (concorrência, PCMS-G04), `resp, selos, ap:[], req, ins:[{p, dose:0, un, tot}]` e `ben:{seg, prod, rota, rv, ini, fim, ativos[], local, ent[{lote, kg}], sai[], dif0, conf, just[], insp, hist[]}` |
| Versão de rota | `BEN_ROTAS` (`dados_ben.py` → JSON no JS), chave `'PACK-FRU|3'`; estática até o editor (BEN-6) | `estado` (Aprovada · Rascunho), `aprov{quem, em}`, `seg, prods[]` (código do CD-02, `dados_cad.py:31-32`), `fin` ('' = qualquer), `est_ent, saidas[{fluxo, est, classes[]}], etapas[{nome, pert, cond}], ativos[], equipe, mat[], avanco` ('concluir' · 'saida'), `controles[]`, `par{…, fonte}` |
| Registro de saída ou perda | `ordem.ben.sai[]`, IDs `S-01…` por ordem | `id, k` (chave), `fluxo` (Produto · Subproduto · Outro destino · Descarte · Perda identificada), `classe, causa, est, lote` (destino), `cx, pallets, bruto, tara, kg, cons[{lote, kg}]` (consumo do lote, avanço por saída), `uf, metodo, base, destino, orig` (Pesado · Estimado), `ev{ticket, balanca, em}`, `data, quem, estorno{quem, em, motivo, ref}, ref` |
| Lote de produção | `c.ben.lotes[id]`, fora de `c.lotes` (insumos) | `id, prod, seg, est, classe, local, prop, kg, cx, umid{v, metodo, base}, qual, insp, ordem, origem[{lote, kg, modo}], ver, hist[]` |
| Inspeção | `c.ben.insp[id]` | `id, lotes[], padrao, versao, metodo, amostra, resultado, situacao` (Conforme · Não conforme), `decisao, motivo, resp, prazo, estado` |
| Movimento de produção | `c.ben.movs[]`, `MP-1001…` | `tipo` (consumo_proc, producao, destinacao, reserva, reserva_cancelada, bloqueio, liberacao, reclass), `lote, ordem, kg, quem, at, antes, depois, motivo, chave` |
| Pedido · reserva | `c.ben.pedidos` (cópia sintética de `areas/comercial.py`) · `c.ben.reservas` (`RS-0001…`) | Pedido: `id, cliente, prod, est, classe, kg`. Reserva: `id, pedido, lote, kg, estado` (Ativa · Cancelada), `motivo` |
| Sequências | `c.ben.seq` | `lote{semana: maior}`, `insp` |
| Requisição de caixas | `c.reqs['REQ-030']` | item com `confirmado:'balcao'` (PCMS-M14) |
| Lote de caixa | `c.lotes['Caixa de mamão 20 kg|CX26-01']` | `fisico, reservado, quarentena, un:'un', local:'Packing'` |

Proteções da semente:
- A semente BEN não grava em `c.movs`, para não deslocar a numeração MV- que os testes de O.S. e EST esperam (`cenario.js:44`). O histórico da REQ-030 fica nos itens.
- A Manutenção é só lida: `c.man.ativos[id].cond` (PCM 1a). Nenhum terceiro cenário é criado.

### 3.2 Cadastros reutilizados
- Produto: código do CD-02 (`dados_cad.py:31-32`). Fator da saca: item do CD-06 por produto e estágio (`areas/cadastros.py:689-690`); `CULTURAS` é unidade de produtividade por ha e não serve como fator de estoque.
- Ativo a13 (`kgh`, `custo_h`); locais Packing, Armazém Sede, Silo 01.
- Item caixa: preço, embalagem de entrega e tara numérica (nova, `dados_cad.py`).
- Nada é redigitado: lote, produto, estágio, local e umidade inicial vêm do lote de entrada.

### 3.3 Genealogia
- Cada lote guarda `origem:[{lote, kg, modo}]`, muitos-para-muitos (l.8626). `modo` = medido, rateio ou estimado.
- "Para frente" é a busca inversa (`benArvore`) e funciona com saldo 0.
- Rateio de uma saída S sobre entradas Eᵢ: `q6(S·acumᵢ/E) − q6(S·acumᵢ₋₁/E)`. A soma fecha sem tolerância. Registro estornado não entra.

### 3.4 Bases de medida (PRD 10.0, l.4183-4197; decisão em DECISOES.md §1)

| Grandeza | Escala interna | Exibição |
|---|---|---|
| Massa (kg) e água estimada | 6 casas, meio para cima. JS: inteiro escalado por 10⁶ e contas em `BigInt`; Python: `Decimal` | até 3 casas, pt-BR; água rotulada "(estimada)" |
| Umidade medida | casas do método, declaradas na versão (semente: 1 casa) | como medida, com método e base |
| Umidade da mistura, rendimento, recuperação | coeficiente com 12 casas (fração) | % com 2 casas |
| Horas de linha e HH | 6 casas | 2 casas |
| Caixa e pallet | inteiro | inteiro |
| Saca | derivada (kg ÷ fator do item), nunca armazenada; só item com fator | 2 casas, "sc 60 kg" |
| Dinheiro (BEN-2) | 8 casas intermediárias | R$ com 2 casas; R$/kg com 4 |

- **Água retirada** = base − `benEst`, calculada depois da quantização de `benEst`. A forma m × (uᵢ − u_f)/(100 − u_f) é igual na álgebra, mas nunca é calculada nem quantizada à parte (R-B01). Produtor único: `benAgua`, espelho `ben_massa.agua`.
- Comparação depois da quantização, sem épsilon escondido (l.4197). A exibição deriva do valor guardado, nunca do exato.
- A regra `cenQtd` de 2 casas continua só para insumo; a divergência dela e da área com o PRD 10.0 fica como pendência fora da BEN (FORA-DE-ESCOPO.md §3).

### 3.5 Físico do lote de entrada e "em processo"
- O lote de entrada mantém o físico entregue à ordem até o Fechar, quando vira Esgotado (R-A10). Assim a grade de lotes não perde massa antes de os lotes de saída nascerem.
- O que falta processar é o "Em processo" da ordem, nunca o resíduo de saídas e água (senão a diferença seria sempre 0):
  - avanço no Concluir: entrada − Σ registros pesados válidos, até o Concluir, que declara o resto processado (R-A08);
  - avanço por saída: Σ entradas − Σ consumo declarado nas saídas (`cons`, por lote de entrada).
- O painel do lote Em processo mostra "Em processo na <OB>: <kg> de <kg>". Não há coluna nova.
- Os lotes de saída nascem no Fechar (CMD-23, l.2794). Até lá são o "lote de destino" dos registros.

---

## 4. Regras numeradas e testáveis

Cada regra traz enunciado, trava ou aviso com o dano evitado, fonte e bloco. Os números estão no §10; os testes no §11; o aceite no §12. Toda recusa confere que `c.rev`, `c.ben.movs.length` e o histórico ficaram iguais (R-G05).

### 4A. Comuns (FL-18 l.3792; FO-14 l.2324; CO-05 l.2874)

- **R-A01 · Cinco fases.** A fase só muda por comando. "Concluir execução" leva a Em conferência. Condição é selo, nunca coluna. **Trava:** comando fora da fase ("Feche só em Em conferência"). Dano: pular a conferência. Fonte: l.2760, l.2862; AGENTS §4. BEN-1.
- **R-A02 · Rota aprovada e compatível; versão da ordem autorizada.**
  - Só versões Aprovadas compatíveis com o produto (código do CD-02), a finalidade (quando a versão declara) e o estágio das entradas. Rascunho nunca é oferecido.
  - Recusas: "Entradas de produtos diferentes: <A> e <B>"; "Sem rota aprovada para <produto> · <estágio>. Dono: <responsável de produção>".
  - A versão da ordem (rota, entradas, quantidades, caixas) é autorizada pelo responsável de produção (CMD-42), sem agrônomo, no toque de R-A05. Editar antes de liberar (como Retirar entrada) grava a versão seguinte; o CMD-42 cita a versão exibida no clique.
  - **Trava.** Dano: processar fora do roteiro vigente ou com o protocolo de outra espécie (BEN-02: não existe umidade-alvo universal). Fonte: l.1067, l.2825, l.2862, l.2874, l.7405-7411, l.7560. BEN-1.
- **R-A03 · Entrada elegível.** Estágio da rota, qualidade Recebido ou Liberado, saldo livre ≥ quantidade. Conferida ao criar e ao liberar. **Trava** ("<lote> em inspeção (<INSP>) · <responsável>"). Dano: lote suspeito no vendável e na genealogia. Fonte: l.2874; RN-015 l.217; RN-011 l.213. BEN-1.
- **R-A04 · Entrada > 0 e finita.** Ordem sem entrada não é criada. `0`, `NaN` e `1e999` são recusados com "Informe a quantidade de entrada", sem exceção. **Trava.** Dano: ordem presa sem massa. BEN-1.
- **R-A05 · Autorizar rota e liberar (CMD-42 + CMD-06).**
  - Criar a ordem não reserva nada: a reserva de entradas e de caixas nasce só na liberação (DEC-2609-13), como no PCM (PCMS-M05, M09).
  - `benImpedimentos` lista todas as causas de uma vez, cada uma com dono e atalho que só navega. Com qualquer causa, nada é gravado.
  - Sem causa, no mesmo `cenMudar`: evento CMD-42 "Versão vN da ordem autorizada" (rota, entradas, total, caixas) e evento CMD-06 "Liberada" (REQ); entradas reservadas à ordem; caixas reservadas por `cenLiberar` (DEC-2609-13); REQ numerada por `cenProxId` (regra única do PCM 1b). Ordem sem material libera sem REQ.
  - Mensagem de falta de caixa: "<item>: <livre> un disponíveis para <necessário> un · Estoque". Com sobra em custódia de outra ordem, a causa traz o atalho da I4; sem sobra, o atalho da I4b.
  - **Trava.** Dano: liberar sem material, sem lote apto ou sem autorização registrada. Fonte: l.1067, l.2777, l.2862; DEC-2609-04; DEC-2609-05 l.12220; DEC-2609-13 l.12227. BEN-1.
- **R-A06 · Iniciar.** Marca as entradas Em processo (disponível 0). O físico não muda (§3.5). Fonte: l.7549. BEN-1.
- **R-A07 · Massa pesada não se cria.**
  - No registro: Σ(produtos + subprodutos + outro destino + descarte + perdas pesadas) ≤ entrada + tolerância pesada (`par.tol_pesado` × entrada).
  - A água estimada nunca entra nesta trava. Água ou ingrediente adicionado, com peso, entra do lado direito no BEN-6.
  - Mensagem: "Saídas pesadas <Σ> kg > entrada <E> kg + tolerância <t> kg. Confira a pesagem."
  - **Trava.** Dano: vendável inflado ou erro de digitação. Recusar fato medido por causa de estimativa seria S2 (fluxo essencial bloqueado; induz falsificação do registro; RN-018 l.220; l.7415; l.7549). Fonte: l.4423-4427, l.7549. BEN-1.
- **R-A08 · Concluir execução.**
  - Exige ≥ 1 saída Produto com classe.
  - Avanço no Concluir (PACK-FRU, CAF-BEN): o Concluir declara toda a entrada processada; o que não foi registrado vira diferença na conferência.
  - Avanço por saída (SEC-GRA, CAF-NAT): exige em processo = 0 ("Faltam <kg> em processo. Registre em Saídas.").
  - Grava `dif0`, a diferença no momento do Concluir (usada pela R-F07).
  - **Trava.** Dano: produto em processo esquecido. Fonte: l.1067 ("Registrar avanço e saídas"), l.2324, l.7555. BEN-1 (no Concluir) · BEN-3 (por saída).
- **R-A09 · Fechar processo (CMD-23).** Exige: balanço conferido; `cenPodeEncerrar(c, id) === ''`; em processo 0; controles obrigatórios da versão completos e nenhuma etapa Exigida Pendente.
  - `benEtapas(o, rota)` devolve, por etapa, a pertinência, a situação (Cumprida · Pendente · Não se aplica) e a evidência (ID do registro que cumpre, ou o motivo). A aba Etapas e esta trava usam a mesma função. Nenhuma etapa aparece "Exigida" sem registro que a cumpra.
  - PACK-FRU v3: Recepção cumprida com entradas Recebido ou Liberado; Triagem e Classificação com ≥ 1 saída Produto com classe; Embalagem com caixas e bruto > 0 em toda saída Produto (trava no registro, R-C01). Paletização e Pré-resfriamento: "Não se aplica nesta versão (pallet no BEN-8; câmara no BEN-6)". Lavagem: "Não se aplica".
  - SEC-GRA v2 (BEN-3): Pré-limpeza Condicional, cumprida por perda "Impureza retirada" > 0, senão Pendente só como aviso (I7). Secagem Exigida quando a umidade da mistura passa da `u_ref` da versão; cumprida quando toda saída Produto tem umidade final, método e base. Armazenagem cumprida no Fechar (lote criado no local).
  - CAF-NAT v1 (BEN-4): Separação e limpeza Condicional, cumprida por perda "Impurezas" > 0, sem trava. Secagem em terreiro Exigida, cumprida pela umidade final. CAF-BEN v1: Beneficiamento seco cumprido pela saída Café beneficiado; Classificação pela classe dessa saída; Ensacamento "Não se aplica (sacaria no BEN-6)".
  - **Trava** (mensagem de `cenPodeEncerrar`, `cenario.js:246`, ou a etapa pendente). Dano: caixa sumida, saída sem destino, controle sem registro. Fonte: l.2794, l.7407, l.7555; OSFASE-18 l.3013. BEN-1.
- **R-A10 · Fechar cria e encaminha.** Cria os lotes Em inspeção com a genealogia. Abre a inspeção sozinho, com responsável da Qualidade e prazo = data + `par.prazo_insp`. Entradas → Esgotado. Descarte e outro destino → Destinado. Sem clique extra; nunca encerramento sem encaminhamento. Fonte: l.2794, l.2878; OSFASE-18 l.3013; DEMO-19 l.4728. BEN-1.
- **R-A11 · Idempotência e versão esperada (reaproveita PCMS-G04).**
  - (i) Guarda por estado: Autorizar e liberar, Iniciar, Concluir, Conferir, Fechar, Registrar resultado e decisões. Repetir devolve "já feito" e não grava.
  - (ii) Chave e versão: os comandos que acrescentam registro (Nova ordem, Registrar saída ou perda, Estornar, Justificar, Retirar entrada, Reservar, Cancelar reserva) passam `cmd = {chave, nome, obj, ver, payload}` ao `cenMudar` do PCM 1b. A chave nasce ao abrir o formulário e sai só com a confirmação.
    - Mesma chave e payload: devolve o recibo, sem aplicar e sem subir `rev` ("Já feito: <registro> de <kg> (<quem>, <hora>)").
    - Mesma chave com payload diferente, ou `ver` diferente: conflito "A <objeto> mudou depois que você abriu: <estado atual>. Confira e registre de novo." Nada é gravado.
    - Nunca usar o `c.rev` global como versão (O.S., Estoque e app o mudam o tempo todo).
  - **Trava.** Dano: movimento ou registro duplicado (S2; AGENTS §3). Fonte: ENG-021/022 l.5285; DEMO-18 l.4744; AGENTS §4. Servidor, outbox e transação: FORA-DE-ESCOPO.md §2. BEN-1.
- **R-A12 · Reabrir e corrigir.** Reabrir execução exige motivo e volta a Em execução (a declaração do Concluir cai). Corrigir informação fica em Em conferência: lançar a perda que faltou (R-F07) ou estornar e relançar (R-A15). Em Em conferência, nova saída só substitui registro estornado; outra saída exige Reabrir. **Trava** (reabrir sem motivo). Dano: retorno sem causa registrada; o realizado muda em silêncio ou a diferença é coberta por apontamento inventado (RN-019 l.221; l.2878). BEN-1.
- **R-A13 · Condição do ativo.**
  - BEN-1, só exibição: `benCondAtivo(man, id)`, função pura, lê `c.man.ativos[id].cond` e mostra o texto do PCM no painel e na g_rec. Classificação por prefixo, testada desde já: "Apto" → normal; começa com "Restrito" → aviso "Restrito na Manutenção: capacidade reduzida não informada"; "Bloqueado" ou qualquer outro valor → impedimento, com o valor literal.
  - Trava (capacidade 0; Autorizar e liberar e Iniciar impedidos; selo "Linha parada"; dono pelo contrato do PCM): só depois do PCM Bloco 2 (PCMS-A01 e A02; CMD-18/19 l.2789-2790). Sem tela que bloqueie o ativo, a trava não pode ser exercida nem homologada (`areas/maquinas.py:189-210` só muda a grade).
  - Dano (quando a trava entrar): processar em equipamento parado. Fonte: l.7720; PCM-05 l.7799; DEC-2609-14. BEN-1 (exibição).
- **R-A14 · Campos por rota.** Umidade só em grão e café. Caixas, bruto e tara só em fruta. Etapa não pertinente não é exigida. Fonte: BEN-01 l.7559. BEN-1.
- **R-A15 · Estornar registro.**
  - Em Em execução e Em conferência; em Em conferência a ordem não sai da fase.
  - Motivo por toque: Erro de digitação · Pesagem refeita · Outro (texto obrigatório).
  - Não apaga nada: grava registro inverso com `ref`; o original recebe `estorno{quem, em, motivo, ref}` e fica visível, riscado, com o selo "Estornado".
  - O original sai do Σ da R-A07, do balanço, do rateio e da genealogia do Fechar. Os lotes só nascem no Fechar, então nenhum lote é desfeito e nenhum MP- é gravado.
  - Caixas: `consumido −= un`, `custodia += un`, movimento MV `estorno-consumo` em `c.movs` (`cenEstornarConsumo`).
  - Histórico: quem, quando, motivo e a diferença antes → depois, em kg e %.
  - Derruba conferência e justificativa dadas sobre o balanço antigo, com linha no histórico.
  - "Corrigir registro" = estornar e abrir o formulário com fluxo, classe, estágio e destino herdados; caixas, bruto, kg e umidade ficam vazios.
  - Recusas, sem mudar `c.rev`: "Registro já estornado"; estornar o inverso; ordem em A liberar, Liberadas ou Encerradas (Encerradas: "Correção de ordem encerrada é ajuste vinculado com alçada (BEN-7)").
  - **Trava.** Dano: apagar ou editar fato pesado sem rastro, ou fabricar perda ou justificativa para cobrir digitação. Fonte: RN-018 l.220; RN-020 l.222; RN-044 l.246; l.2766; l.2878; l.7097; l.7549. BEN-1.
- **R-A16 · ID de lote único.**
  - `benLoteId(c, dataFato)` = 'L' + semana ISO do fato + '-' + (1 + maior número já usado na semana entre: chaves de `c.ben.lotes`, destinos em `ordens[*].ben.sai[].lote` e `c.ben.seq.lote[semana]`). Grava `seq` no mesmo `cenMudar`; ID de saída estornada nunca volta.
  - Usado por Registrar saída, Nova ordem e Fechar. O Fechar e o Registrar recusam ID que já existe para outra ordem: "Lote <id> já existe (<ordem>)".
  - **Trava.** Dano: sobrescrever lote, genealogia, inspeção e reserva. BEN-1.

### 4B. Grãos (FL-BEN-01 l.7417)

- **R-B01 · Fórmula única em matéria seca** (`benEst`, `benAgua`, `benBal`; espelho `ben_massa.est`, `agua`, `bal`).
  - Base de secagem por entrada: base_e = consumo do lote e − impureza da pré-limpeza do lote e.
  - MS_proc = Σ base_e × (1 − u_e/100). MS_sai = Σ m_s × (1 − u_s/100), sobre as saídas com umidade final.
  - est = q6(MS_proc × Σm_s ÷ MS_sai). Água = Σ base − est. Diferença = est − Σm_s (equivale à R-F01).
  - Com uma entrada e uma saída, é `benEst(m, uᵢ, u_f) = m × (100 − uᵢ)/(100 − u_f)`. Com várias saídas, equivale a usar a umidade ponderada das saídas sem quantizá-la; o resultado não depende da ordem das saídas, e o sinal da diferença é o da diferença em matéria seca.
  - Estimativa, nunca pesagem. A hipótese de conservação da matéria seca é declarada na versão (`par.agua.hipotese_ms`); o painel mostra a diferença em kg de MS como linha informativa.
  - **Trava:** umidade < 0, ≥ 100 ou não finita; na secagem, saída com u_s acima da umidade da mistura das entradas, com a causa escrita. Dano: massa fabricada. Fonte: l.4419, l.4427, l.7415, l.7549; BEN-03 l.7561. BEN-3.
- **R-B02 · Pré-limpeza antes.** A impureza pesada sai da base antes da umidade. Dano evitado: desconto em dobro. Fonte: CAL-16 l.4413-4427. BEN-3.
- **R-B03 · Mistura ponderada.** Umidade da mistura = Σ(m·u) ÷ Σm, coeficiente com 12 casas; nunca a média simples. A matéria seca é somada entrada por entrada. Dano: água errada. Fonte: l.289; l.8147. BEN-3.
- **R-B04 · Água retirada ≠ perda.** Tem linha própria; fica fora de "Perdas identificadas" e do KPI de perdas. Impureza, descarte e diferença são linhas distintas. Fonte: l.7415; KPI-IND-02.VENDAVEL l.8543. BEN-3.
- **R-B05 · Saca só com fator do item.** Sacas = kg físico ÷ fator do item do CD-06 (produto e estágio), só quando o item tem fator; nunca armazenada. Vazia para fruta, fruto de café, café em coco, casca e grão úmido. Nunca "sc" sem massa; nenhum `/60` literal fora do item. A semente acrescenta "Milho em grão" (seco) com `sc 60 kg` no BEN-3. Dano: ler fruto, coco, casca ou grão úmido como sacas comerciais. Fonte: l.4421; l.7506; l.7549. BEN-1 (café beneficiado da OB-0104) · BEN-3.
- **R-B06 · Umidade com método e base.** Obrigatória em cada saída Produto da SEC-GRA, da CAF-NAT e da CAF-BEN. A umidade inicial vem do lote (sem redigitar); lote sem umidade numa rota que a exige faz o Autorizar e liberar recusar. Mensagem: "Informe a umidade final (método e base)". **Trava.** Dano: água, rendimento e sacas sem base declarada (l.7411; l.8543; l.7555). BEN-3 · BEN-4.
- **R-B07 · Grão apto segue sem secagem.** Secagem "Não se aplica" quando a umidade da mistura ≤ `u_ref` da versão do produto e da finalidade. Soja úmida sem versão própria → "Sem rota aprovada", nunca 14 % por omissão. Fonte: BEN-02 l.7560. BEN-3.
- **R-B08 · Compatibilidade e capacidade por instalação.** Aviso no BEN-5; trava no BEN-7, se o dono pedir. Dano: mistura de produtos no mesmo silo e sobrecarga pela capacidade nominal. Fonte: l.7413.

### 4C. Frutas/HF (FL-BEN-02 l.7464)

- **R-C01 · Embalagem não é massa.**
  - `benTara` = caixas × tara do item + pallets × `par.tara_pallet`. Líquido = bruto − tara. Só o líquido entra no balanço.
  - Onde se pesa é parâmetro da versão (`par.pesagem`: 'caixa' · 'pallet'). PACK-FRU v3: 'caixa', caixas cheias pesadas antes da paletização; o campo é "Bruto sem pallet (kg)" e a coluna Pallets não aparece. Com 'pallet', o formulário pede o número de pallets (inteiro, nunca último valor; o 60 de `dados_cad.py:130` é a embalagem de entrega das caixas vazias e não serve de sugestão).
  - **Trava:** saída Produto sem caixas > 0 e bruto > 0 ("Informe caixas e bruto"). Dano: embalagem contada como fruta. Fonte: l.4425, l.7462; BEN-04 l.7562; l.2608. BEN-1.
- **R-C02 · Caixas ≤ custódia.** Cada saída baixa a custódia da REQ (`consumido += un`) e grava movimento MV `consumo`. Mensagem: "Caixas acima da custódia: <n> un. Peça a entrega no Estoque". **Trava.** Dano: estoque de caixa negativo ou sem origem. Fonte: FO-09 l.2319; RN-013 l.215. BEN-1.
- **R-C03 · Caixas sugeridas** = ⌈entrada × `frac_vend` ÷ conteúdo nominal⌉. Confirmadas e editáveis; nunca o último valor. Fonte: AGENTS §3.3; ENG-011. BEN-1.
- **R-C04 · Líquido por caixa** fora de ±`par.aviso_cx` do nominal gera aviso, não trava. Não detecta pallet esquecido (por isso a R-C01 declara a pesagem). Fonte: l.7462. BEN-1.
- **R-C05 · Classe, canal e destino são distintos.** "Outro destino" (indústria) não é perda física. Fonte: BEN-04 l.7562; l.4425. BEN-1.
- **R-C06 · Perecível.** Lote vencido não libera; ruptura de câmara abre ocorrência sem prorrogar validade; FEFO só entre elegíveis. **Trava.** Dano: vender fora de condição. Fonte: l.7462; ATP-03 l.8001. BEN-6.

### 4D. Café (FL-BEN-03 l.7510)

- **R-D01 · Estágios não intercambiáveis.** A rota declara o estágio de entrada; a reserva exige o estágio do pedido ("Estágio <lote> ≠ <pedido>"). **Trava.** Dano: coco vendido como beneficiado. Fonte: l.7506; BEN-05 l.7563. BEN-4.
- **R-D02 · Rendimento medido, com base declarada.** Saída ÷ entrada da ordem, com as umidades do coco e do beneficiado ao lado. Quando diferem, mostra também o rendimento em base seca, pelo serviço da R-B01. Nenhuma constante de rendimento. Fonte: l.7506; l.8543; BEN-05. BEN-4.
- **R-D03 · Registros distintos.** Casca, impurezas, pó e água retirada. Fonte: l.7506. BEN-4.
- **R-D04 a R-D07** (CD e via úmida; blend com nota "a avaliar", que nunca copia a melhor; reprocesso como ordem vinculada; sensorial separado da classificação física): BEN-6. Fonte: l.7502-7506; BEN-06 l.7564; l.2878.

### 4E. Qualidade e estoque de produção

- **R-E01 · Aprovar rota ≠ liberar ordem ≠ liberar lote.** Fechar não libera. **Trava.** Dano: vender lote não inspecionado. Fonte: CMD-23/24 l.2794-2795; BEN-09 l.7567; DEMO-19 l.4728. BEN-1.
- **R-E02 · Inspeção e liberação.**
  - O resultado grava a situação (Conforme · Não conforme) contra o padrão e a versão. O CMD-24 só com resultado ("Registre o resultado (<INSP>)").
  - "Liberar" só com Conforme. Com Não conforme, três saídas: "Liberar como classe atingida" (uma decisão, dois toques: grava a classe, o MP `reclass` sem mudar massa e libera), Manter bloqueio (motivo, prazo) ou Destinar (motivo). Recusa: "Resultado não conforme (<INSP>): libere como classe atingida, mantenha o bloqueio ou destine".
  - A decisão não reabre a ordem.
  - **Trava.** Dano: liberação sem evidência; prometer ao cliente lote fora do padrão dele. Fonte: RF-PRD-007 l.2610; FO-15 l.2325; CMD-24 l.2795; DEMO-19 l.4728. BEN-1.
- **R-E03 · Decisões com motivo.** Bloquear (também lote Liberado), Reclassificar (mesma massa; o lote fica Liberado na classe nova), Destinar (físico → 0, Destinado, MP `destinacao`). **Trava** (sem motivo). Dano: estoque baixado ou retido sem causa auditável; destino sem critério nem dono. Fonte: RF-PRD-009 l.2612; RF-PRD-007 l.2610. BEN-1.
- **R-E04 · Disponível.** Físico do lote Liberado − reserva para ordem − reservas Ativas (inclusive com expedição impedida), ≥ 0. Qualquer outro estado = 0. Fonte: CAL-17 l.4431-4435; RN-011 l.213. BEN-1.
- **R-E05 · Reservar para pedido.**
  - Só lote Liberado, do mesmo produto, estágio e classe do pedido (igualdade; "classe X ou melhor" fica para o BEN-6, com fonte).
  - Classe vazia no lote ou no pedido → "Classe não informada" (vazio igual a vazio nunca passa).
  - Quantidade ≤ mín(disponível, falta); falta = pedido − reservas Ativas. Sugestão = esse mínimo, editável até ele.
  - Recusas: "<lote> em inspeção" / "<lote> bloqueado"; "Classe <x> ≠ <y> do <pedido>"; "Disponível <d> kg"; "<pedido>: falta 0 kg; nada a reservar".
  - **Trava.** Dano: promessa sobre lote inapto, de outra classe ou acima do pedido. Fonte: RF-PRD-007 l.2610; l.7985 ("sem criar reserva excedente"); DEMO-18 l.4744. BEN-1.
- **R-E06 · Reserva com expedição impedida.**
  - A reserva tem só Ativa → Cancelada. "Expedição impedida" é derivada: lote ≠ Liberado, ou produto, estágio ou classe ≠ os do pedido (mesmo padrão de `carLib(...).valida`, `dados_carencia.py:366-368`).
  - A reserva impedida continua Ativa e deduzindo. O pedido fica "Em risco · <motivo>". Liberar de novo tira o impedimento, sem reativação.
  - Só "Cancelar reserva (motivo)", do Comercial, libera o saldo (MP `reserva_cancelada`). Nada é cancelado nem redistribuído sozinho (l.7995).
  - Trava de expedição no BEN-8. Dano: expedir ou faturar lote bloqueado contra reserva já feita. Fonte: AC-49 l.4809; RF-PRD-007 l.2610; CO-06 l.1093; l.7555; BEN-09 l.7567. BEN-1.
- **R-E07 · Genealogia** muitos-para-muitos por rateio acumulado (§3.3); para trás e para frente, com saldo 0. Fonte: l.8626; RF-PRD-006. BEN-1.
- **R-E08 · Estoque único de produção.** A grade de lotes da BEN é a tela canônica de produto acabado; o EST de insumos não lista lote de produção. Fonte: RF-PRD-008 l.2611. BEN-1.
- **R-E09 · Retorno de cliente** entra Bloqueado e não aumenta o vendável. **Trava.** Dano: estoque inflado. Fonte: DEMO-08 l.4716. BEN-5.

### 4F. Balanço e custo

- **R-F01 · Diferença.** dif = processado − (Σ saídas + Σ perdas pesadas + água estimada), em kg na base física, sem tara, só com registros válidos. Processado = entrada inteira (avanço no Concluir) ou Σ consumo (avanço por saída). Fonte: CAL-16 l.4423; FL-18 l.10826. BEN-1 (sem água) · BEN-3.
- **R-F02 · Faixa de conferência** (`benFaixa`, espelho `ben_massa.faixa`).
  - Faixa = `tol_pesado` × processado + incerteza da água. A incerteza só existe em rota com água e hipótese validada: Δu_ent × base ÷ (100 − u_f*) + Δu_sai × base × (100 − uᵢ) ÷ (100 − u_f*)², com u_f* a umidade ponderada das saídas, sem quantizar. Soma linear, de pior caso, declarada.
  - |dif| ≤ faixa: conferível; a linha "Diferença de medição" fica visível com o sinal ("ganho aparente" se negativa).
  - dif > faixa: perda pesada com evidência (R-F07) ou justificativa (R-F03, alçada).
  - dif < −faixa: selo "Ganho aparente acima da faixa"; corrigir pelo estorno (R-A15) ou justificar "Erro de medição" (alçada sobre |dif|).
  - Hipótese de matéria seca não validada: a diferença vira só aviso ("hipótese de matéria seca não validada na <versão> · RT"), sem trava e sem justificativa.
  - Nunca perda ou ganho automático.
  - **Trava.** Dano: perda escondida, custo por kg errado ou pesagem alterada para caber. Fonte: l.4177, l.7415, l.7549, l.10826. BEN-1 (parte pesada) · BEN-3 (água).
- **R-F03 · Justificar diferença.** Motivo por toque (Erro de medição: balança ou umidade · Perda não identificada · Outro) e texto. Vale para os dois sinais. Vira a linha "Diferença justificada", com quem e quando. Nenhum registro "Perda identificada" é criado. Alçada: R-G06. Fonte: l.7549; l.10826. BEN-1.
- **R-F04 · Escala.** A do §3.4. Comparar depois de quantizar a 6 casas; exibir a partir do valor guardado. Fonte: PRD 10.0 l.4187, l.4197. BEN-1.
- **R-F05 · Horas de linha.** h-linha = processado ÷ kgh do ativo (o nominal do CD-03 ou o informado pelo PCM quando existir; nunca fator universal). HH = processado × equipe ÷ kgh, numa expressão só. kg/HH = processado ÷ HH. Rótulo "estimado pela capacidade". Ocupação ≠ HH (BEN-5). Fonte: l.7206; l.8254; BEN-07. BEN-1 (exibe).
- **R-F06 · Custo do beneficiamento, provisório** (`benCusto`, espelho `ben_massa.custo`).
  - Custo = h-linha × `custo_h` do ativo + HH × `par.custo_hh` da versão + Σ caixas usadas × preço do item. O `custo_h` cobre combustível, manutenção e depreciação; o operador entra em Pessoas (`areas/cad_ativos_pessoas.py:112`; l.8131), então não há HH em dobro.
  - Duas bases: "R$/kg de entrada (beneficiamento)" e "R$/kg vendável (beneficiamento)" (Σ Produto, sem descarte, outro destino nem perda).
  - Rótulo fixo: "Provisório · só o beneficiamento: sem matéria-prima, rateio de apoio e perdas valorizadas". Os componentes são listados pela composição da tarifa.
  - Falta tarifa, custo-hora ou produção → "não calculável: falta <item>", nunca R$ 0. A caixa conta uma vez: as usadas, não as entregues.
  - **Trava de exibição.** Dano: custo unitário confundido com custo completo do produto. Fonte: l.7553, l.8127, l.8131, l.8145. BEN-2 (packing). Grão e café: "não calculável" até haver ativo e tarifa (BEN-5, BEN-7).
- **R-F07 · Perda com prova e correção na conferência.**
  - "Perda identificada" só com origem Pesado e evidência: ticket (digitado), balança e data/hora (herdadas como "agora" e a balança da rota, corrigíveis). Sem evidência: "Sem pesagem não é perda identificada. Justifique a diferença (alçada)."
  - Em Em conferência, toda correção (perda nova, estorno, relançamento) exige motivo, grava a diferença antes → depois e põe o selo "Corrigido na conferência".
  - Se a correção leva |dif| de fora para dentro da faixa e |dif₀| (do Concluir) passa da alçada de quem corrige, a correção só vale com a confirmação de quem a alçada indica para |dif₀|: "acima da alçada de <limite>: decide <papel> (<pessoa>)".
  - Rui vê o ticket e o selo ao conferir; sem toque a mais quando não há correção.
  - BEN-5: com a balança no PCM e o recebimento, o ticket passa a ser escolhido de pesagens registradas; só então esta confirmação pode sair, por decisão registrada.
  - **Trava.** Dano: quem executou fecha a própria diferença com apontamento sem prova. Fonte: l.2878; FL-18 l.10826; RN-018 l.220; AGENTS §4 (integridade do fato). BEN-1 · BEN-3 (pré-limpeza).

### 4G. Governança

- **R-G01 · Só dado sintético**, com o rótulo "Demonstração sintética" na casca. Pessoa nova pelo critério do §2.3. Fonte: ENG-017; DEC-2709-01. BEN-1.
- **R-G02 · Parâmetro técnico só da versão da rota**, com fonte "sintético · vN". Nenhum valor universal. O catálogo da fase 7 (`catalogo_operacoes.py:79, 161, 215`) não é usado. Padrão oficial de classificação do MAPA por produto: item e vigência a verificar; não é embutido. Fonte: l.7572; RN-017 l.219; RN-043 l.245. BEN-1.
- **R-G03 · Uma primária por tarefa ativa** (0 em consulta) e 0 ação duplicada em cada fase e estado (§5.3). Fonte: padrão v3.1 (`v37/specs/padrao-comandos-v3-prompt.md:9-21`). BEN-1.
- **R-G04 · Contrato de tabela.** Uma variável por coluna; tipos; unidade na célula (2d); filtro e ordenação por coluna; até 7 colunas iniciais; a 1440 e a 390 px. Fonte: PRD 4.3 l.287-289; `v37/RETOMADA-NUVEM.md:200-229`. BEN-1.
- **R-G05 · Auditoria.** Todo comando grava no histórico da ordem ou do lote (quando, quem, evento, antes → depois, motivo). Gera MP- quando muda massa ou estado de lote, e MV- quando mexe em caixa. Recusa não grava nada. Fonte: AGENTS §4; RN-044 l.246. BEN-1.
- **R-G06 · Alçada de diferença.**
  - Par por versão de rota: percentual do processado e teto em kg (kg não se compara entre mamão, milho e café). Vale o limite mais restritivo. No BEN-7, com custo completo, entra também teto em R$.
  - Até o limite: o responsável de produção. Acima: a gestão (Ana).
  - A mensagem diz qual limite disparou: "<p> % > alçada de <a> %" ou "<kg> kg > alçada de <t> kg (<versão>, sintético)".
  - Aplica-se a |dif| na justificativa (R-F03) e a |dif₀| na correção (R-F07).
  - Valores: padrão sintético (§10.1), "a confirmar pelo proprietário"; o valor real vem da política CF-02 da organização.
  - **Trava.** Dano: perda grande aceita por quem a causou. Fonte: l.193, l.195, RF-GOV-002 l.2673, CF-02 l.1818, RN-043 l.245; l.2876 só para o acúmulo de funções. BEN-1.
- **R-G07 · Pendência com causa, dono e atalho que só navega.** Navegar nunca grava. Fonte: DEC-2609-04; `GUIA-PROCESSOS.md:6-8`. BEN-1.

---

## 5. Telas

### 5.1 Página-processo `BEN.dc.html`
- **Casca:** `shell37('BEN','Beneficiamento', …, primary_html=None, search=False)`, como os processos (`areas/processo_estoque.py:145`). Contexto do topo: Fazenda Santa Rita (DEC-2609-11).
- **Seções paralelas** (`secoes_state`, PRD 4.6 l.322; sem número; cada uma mostra a pendência calculada):

| Seção | Papel | Bloco | Abre por padrão |
|---|---|---|---|
| **Processe as ordens** (abas Lista e Kanban) | Igor, Rui | BEN-1 | Sim (l.7405) |
| **Decida e reserve os lotes** | Marta, Comercial | BEN-1 | — |
| Receba as cargas | Rui | BEN-5 (entra em 1º lugar) | — |

- **Endereços:** `BEN.dc.html#ob=OB-0110`, `#lote=L27-013`, `#sec=lotes`.
- **Recorte:** `g2keep` em todas as grades.
- **Indicadores:** até quatro por contexto, no lugar das contagens que só repetem o Kanban (§7).
- **Rodapé:** "Restaurar demonstração (restaura o cenário inteiro: O.S., Estoque, Manutenção, Compras e app)", com `cenReset`.

### 5.2 Grades

Regras gerais: unidade na célula pelo rótulo com unidade (2d: "Entrada (kg)" → "12.000 kg"); datas ISO; `multi=True` por ID; `total=False` onde há produtos misturados. Colunas iniciais e configuráveis pela R-G04.

**Mecanismo (P6).** A G2 não oculta coluna (`engine.py:1169`). Plano A: o incremento TABELAS-FOCO 2e, de toda a G2 (inclusive a g_os, de 19 colunas): coluna fora do conjunto inicial; botão "Colunas (N ocultas)" ao lado da busca; escolha guardada no recorte (`g2keep`); coluna com filtro ativo nunca some sem o chip do filtro (`g2lib.js:196`); o `qf` continua funcionando sobre coluna oculta. Plano B, se o Codex não abrir o 2e: as colunas ficam visíveis e o desvio do PRD 4.3 vai para FORA-DE-ESCOPO.md com a condição "Colunas configuráveis na G2". Coluna que precisa de filtro (Lotes de entrada, Lotes de origem) nunca vai só para o painel.

| Grade | Colunas iniciais (≤ 7) | Configuráveis |
|---|---|---|
| **g_ob · Ordens** (`m='pick'`; `qf` em Segmento; "+ Nova ordem" ao lado do título) | Ordem · Produto · Fase (chips) · Condição (selos, `multi`) · Em processo (kg) · Próximo passo · Quem resolve | Segmento, Rota, Versão, Instalação, Início, Fim previsto, Lotes de entrada (`multi`), Entrada (kg), Saída vendável (kg), Perdas identificadas (kg), Água retirada (estimada) (kg; BEN-3), Diferença (kg), Responsável |
| **g_lp · Lotes de produção** (`qf` em Qualidade; ordem por prazo da inspeção) | Lote · Produto · Estágio · Classe · Qualidade (chips) · Prazo · Disponível (kg) | Segmento, Local, Proprietário, Inspeção, Responsável, Físico (kg), Reservado (kg), Sacas (vazio sem fator do item), Caixas (un), Umidade (%), Ordem de origem, Lotes de origem (`multi`) |
| **g_pv · Pedidos** (consulta) | Pedido · Cliente · Produto · Estágio · Classe · Falta (kg) · Situação | Pedido (kg), Reservado (kg), Lotes reservados (`multi`) |

- "Quem resolve" usa a chave `dono` da g_os (`areas/processo_os.py:1088`). "Responsável" (Igor em todas as ordens do BEN-1) fica configurável; não há duas colunas com o mesmo valor.
- Validade sai da g_lp até o BEN-6 (coluna sempre vazia sai).

**Cartão do Kanban** (`ui37.kanban5`): Ordem · Produto · Rota vN · Em processo (kg) · selos · próximo passo e quem resolve. O Kanban escreve o filtro ativo, com "Limpar filtros".

**Painel da ordem** (`pick`, 460 px; 100 % no celular). Abas do PRD (l.7405): Etapas · Lotes e quantidades · Qualidade · Recursos e custos · Histórico.

| Grade do painel | Colunas iniciais | Configuráveis |
|---|---|---|
| g_et · Etapas (consulta) | Etapa · Pertinência · Situação · Evidência | — |
| g_ent · Entradas | Lote · Estágio · Qualidade · Quantidade (kg) · Elegível · Motivo · Umidade (%) só em grão e café | Origem |
| g_sai · Saídas, descartes e perdas ("+ Registrar" ao lado do título) | Fruta: Fluxo · Classe · Lote de destino · Líquido (kg) · Caixas (un) · Origem do valor · Situação (Válido · Estornado). Grão e café: Fluxo · Classe · Lote de destino · Líquido (kg) · Umidade final (%) · Origem do valor · Situação | Causa, Estágio, Bruto (kg), Tara (kg; abre a fórmula), Líquido por caixa (kg/un), Pallets (un, só com pesagem no pallet), Consumo do lote (kg; batelada), Destino, Data, Quem, Ticket |
| Balanço (bloco `origin`, nunca editável) | Processado · Saídas · Perdas identificadas · Água retirada (estimada) · Diferença (kg e %) · Faixa (versão) · Situação | Diferença em matéria seca (kg MS; BEN-3) |
| g_mat · Materiais (lê a REQ) | Item · Lote · Solicitado (un) · Entregue (un) · Usado (un) · Em custódia (un) · Devolvido (un) | Situação |
| g_rec · Recursos | Recurso · Tipo · Condição na Manutenção · Capacidade (kg/h) · Horas de linha (h) · Equipe · HH | kg/HH; linha "Custo do beneficiamento (provisório)" em modo `origin` no BEN-2 |
| g_hist · Histórico | Quando · Hora · Quem · Evento · Detalhe · Movimento (MP-/MV-) | — |

Na g_sai, as linhas calculadas ("Água retirada", "Diferença") são `ro` e `origin` e abrem a fórmula com as parcelas. O registro estornado fica riscado, nunca some.

**Painel do lote:** inspeção (padrão e versão, método, amostra, resultado, situação, decisão); genealogia "De onde veio" e "Para onde foi", com kg e modo; reservas; movimentos MP-; para lote Em processo, "Em processo na <OB>: <kg> de <kg>".

### 5.3 Uma ação primária por contexto

| Contexto | Primária | Secundária | Observação |
|---|---|---|---|
| Lista de ordens | nenhuma | "+ Nova ordem" ao lado do título | padrão v3.1 |
| A liberar | **Autorizar rota e liberar** | — | Com impedimento: causas com dono e atalho |
| Liberadas | **Iniciar processo** | — | — |
| Em execução, avanço por saída, em processo > 0 | nenhuma | — | Nota "Faltam <kg> em processo. Registre em Saídas"; "+ Registrar" na g_sai |
| Em execução com ≥ 1 saída Produto (e em processo 0, se por saída) | **Concluir execução** | — | Avanço no Concluir: a nota diz que o não registrado vira diferença |
| Em conferência, fora da faixa, sem justificativa | **Justificar diferença** | Reabrir execução (à esquerda; nomeia o destino) | "Estornar registro" no painel da linha; "+ Registrar perda" na g_sai |
| Em conferência, dentro da faixa ou justificada | **Conferir balanço** | Reabrir execução | — |
| Em conferência, conferida | **Fechar processo** | Reabrir execução | — |
| Encerradas | nenhuma | link "Ver lotes" | Encerrada ≠ liberada |
| Lote Em inspeção sem resultado | **Registrar resultado** | — | — |
| Lote com resultado, não Liberado | **Registrar decisão** | — | Decisão por toque; as opções seguem a situação (R-E02) |
| Lote Liberado com pedido compatível em falta | **Reservar para pedido** | Registrar decisão (bloquear, reclassificar, destinar) | — |
| Lote ou pedido com reserva Ativa | conforme o estado do lote | Cancelar reserva (motivo) | — |
| Lote de rota que ainda não é do bloco (café no BEN-1: L27-013, L38-119, L27-018, L27-019) | nenhuma | — | Só consulta: "Decisões do café entram no BEN-4" |
| Demais estados do lote | nenhuma | — | Nota com a causa |

### 5.4 Celular (390 e 360 px)
- A página não rola; só a área de dados rola (`engine.py:1112-1140`). A faixa de seções recolhe. O painel ocupa a largura toda.
- Alvo de toque ≥ 44 px. Título e primária visíveis. Número não quebra no meio. 1ª e 2ª colunas inteiras.

---

## 6. Inteligência (gatilho → sugestão de um toque, com "por quê")

Os valores entre < > vêm do cenário; os casos estão no §10.

| # | Gatilho | Sugestão | "Por quê" | Bloco |
|---|---|---|---|---|
| I1 | Entradas com uma única versão Aprovada compatível | Rota pré-selecionada, visível e trocável | "Única versão aprovada para <produto> · <estágio>: <rota vN> (<quem>, <data>)." | BEN-1 |
| I2 | Rota com material por caixa | Caixas sugeridas (confirmar) | "<entrada> kg × <frac> previstos ÷ <conteúdo> kg por caixa (<rota vN>, sintético)." | BEN-1 |
| I3 | Lote de entrada em inspeção | "Retirar <lote> da ordem" (grava a versão seguinte) | "Lote em inspeção não entra (<INSP> · <resp> · prazo <data>)." | BEN-1 |
| I4 | Faltam caixas e outra ordem tem sobra em custódia | Atalho "Abrir devolução da <OB> no Estoque" (`EST.dc.html#sec=devolucoes`; só navega) | "<livre> un livres para <necessário> un. A <OB> tem <n> un em custódia." | BEN-1 |
| I4b | Faltam caixas e nenhuma ordem tem sobra | Atalho "Ver saldo de caixas no Estoque" (`#sec=saldos`; só navega) | "Nenhuma ordem tem sobra em custódia. A compra de caixas entra no BEN-2." No BEN-2 vira I17 | BEN-1 |
| I5 | Registrar saída de packing | Lote de destino gerado; tara calculada | "Tara <t> kg por caixa (CD-06); pesado antes da paletização (<rota vN>)." | BEN-1 |
| I6 | Líquido por caixa fora da faixa | Aviso | "<kg/un> kg por caixa contra <nominal> kg: confira a contagem ou a pesagem." | BEN-1 |
| I7 | Rota com Pré-limpeza e nenhuma impureza registrada, em Em execução | "Houve impureza pesada na pré-limpeza? Informe o ticket e o peso." | "A <rota vN> prevê pré-limpeza." Não sugere quantidade nem mostra a diferença como alvo | BEN-3 |
| I8 | Justificar acima da alçada | "Quem decide" pré-selecionado na gestão | "<limite que disparou> do responsável de produção." | BEN-1 |
| I9 | Fechar recusado por custódia | Atalho "Receber devolução no Estoque" | Texto de `cenPodeEncerrar` | BEN-1 |
| I10 | Lote Liberado e pedido compatível em falta | "Reservar <kg> para o <pedido>", editável até o limite | "Mesmo produto, estágio e classe (<classe> nos dois). Faltarão <kg>." | BEN-1 |
| I11 | Inspeção vence hoje | O lote sobe para o topo (ordem por prazo); selo "Vence hoje" | "<INSP> vence em <data>." | BEN-1 |
| I12 | Ativo da rota fora de "Apto" no PCM | "Ver na Manutenção" (MA-01; só consulta, sem efeito na BEN) | "<ativo>: <condição> na Manutenção." | BEN-1 |
| I13 | Recurso da rota sem cadastro | Aviso com atalho para o CD-03 (não trava) | "<recurso> não cadastrado: capacidade e manutenção não são conferidas." | BEN-3 |
| I14 | Lote reservado bloqueado ou reclassificado | O pedido ganha o selo "Em risco · expedição impedida" | "<lote> <motivo> (<quem>)." | BEN-1 |
| I15 | Recuperação abaixo da fração prevista da versão | Aviso no fechamento (não trava) | "Recuperação de <r> contra <frac> previstos." | BEN-1 |
| I16 | Demanda da janela acima das horas disponíveis da linha | Déficit em h-linha na aba Recursos | "<entrada> kg ÷ <kgh> kg/h = <h> h contra <disp> h disponíveis." | BEN-5 |
| I17 | Faltam caixas sem sobra | "Pedir compra da falta (<n> un)" → SC "A cotar" com origem Beneficiamento | "Falta <n> un para a <OB>; precisa em <data>." | BEN-2 |

---

## 7. Indicadores

Fórmula, dono e ritmo por indicador (l.4627); toda razão é razão de totais; as metas são parâmetros do dono com padrão sintético. Cada valor abre a composição e daí o registro. Até quatro por contexto (l.287).

| Indicador | Fórmula · denominador | Onde aparece | Meta inicial | Dono · ritmo | Bloco |
|---|---|---|---|---|---|
| Recuperação comercial (KPI-IND-02.VENDAVEL l.8543) | Σ vendável líquido ÷ (processado − água estimada da R-F01). Perdas, descarte e diferença ficam no denominador; embalagem fora | Painel da ordem (Balanço); seção de ordens, por segmento, ordens encerradas na semana | ≥ `frac_vend` da versão, com o aviso I15 (só packing) | Igor · por ordem, semanal | BEN-1 |
| Rendimento por classe (KPI-IND-02 l.4661) | kg da classe ÷ processado | Painel da ordem (fruta) | acompanhar | Igor · por ordem | BEN-1 |
| Diferença de balanço | \|dif\| e % contra a faixa | Painel da ordem; seção de ordens: "ordens fora da faixa ou justificadas" | \|dif\| ≤ faixa da versão | Rui · por ordem | BEN-1 |
| Perdas e descarte por causa (KPI-COM-02 l.4662: "por causa, origem, classe e destino") | Σ kg de Descarte e de Perda identificada, por causa e destino (sem água; outro destino não é perda, R-C05) ÷ processado físico | Seção de ordens: "maior causa de perda" (Pareto no detalhe) | sem meta: decompõe o que faltou para 100 % | Igor · semanal | BEN-1 |
| Ordens a liberar | contagem, com impedidas | Seção de ordens | — | Igor · diário | BEN-1 |
| Inspeções vencidas ou que vencem hoje | contagem | Seção de lotes (e topo da g_lp) | 0 | Marta · diário | BEN-1 |
| Lote bloqueado | kg Bloqueado ÷ kg físico do mesmo produto e estágio (não somar estágios) | Seção de lotes | acompanhar | Marta · diário | BEN-1 |
| Falta por pedido | Σ falta (pedido − reservas Ativas) | Seção de lotes | acompanhar; nenhuma falta sem dono e prazo | Comercial · diário | BEN-1 |
| Reservas com expedição impedida | kg | Seção de lotes | acompanhar | Comercial · diário | BEN-1 |
| Horas de linha · HH · kg/HH | R-F05 | g_rec, por ordem | acompanhar | Igor · por ordem | BEN-1 |
| Custo do beneficiamento por kg | R-F06 | g_rec (linha `origin`) | — | Ana · por ordem | BEN-2 |
| Água retirada (estimada) | R-B01 ÷ processado | Painel da ordem (grão) | informativo, não é meta | Igor · por ordem | BEN-3 |
| Rendimento coco → beneficiado | R-D02, com umidades | Painel da ordem (café) | acompanhar, sem fator fixo | Igor · por ordem | BEN-4 |
| Ordens fechadas com justificativa; agregados mensais; OEE do packing (KPI-IND-01 l.4651) | razão de totais no período (`agg='ratio'`) | Indicadores (`engine.py:64, 108`) | ≤ 10 % no mês (justificativa) | Ana · mensal | BEN-7 |

Cortado: "ordens fechadas com material conciliado" (a R-A09 já garante); meta de perdas do packing (é o mesmo fato da recuperação).

---

## 8. Integrações

| De → para | O quê | Modo | Bloco |
|---|---|---|---|
| BEN → Estoque | Reserva das caixas na liberação (`cenLiberar`); entrega no balcão em custódia de quem recebe; consumo por saída (MV `consumo`); estorno de consumo (MV `estorno-consumo`); devolução (`cenDevolver`); trava de sobra (`cenPodeEncerrar`) | Real, no cenário; o EST redesenha por `cenOuvir` | BEN-1 |
| Estoque ↔ BEN (tela) | EST abre a seção pelo endereço (`#sec=recebimentos·entregas·devolucoes·saldos·contagens·movimentos`, lido ao abrir e a cada `hashchange`, guarda `self.__hashIni` como `areas/processo_os.py:658-665`; nome desconhecido abre a 1ª, sem erro e sem gravar); recebedor de OB herdado (`o.resp`), corrigível, com opções de `dados_cad`; entrega de OB grava `confirmado:'balcao'` pela mesma regra da OM (`cenBalcao`; PCMS-M14), sem o chip "Aguardando confirmação no app" e fora da contagem k2; link da OB para a BEN; LOCAIS da fonte única (com Packing) | Real | BEN-1 |
| PCM → BEN | Condição do ativo lida de `c.man` (R-A13): exibição | Real (leitura) | BEN-1 |
| PCM → BEN | Trava por condição; ativos novos (secador, terreiro, beneficiadora, balança, câmara fria como ativo); capacidade efetiva em Restrito (campo de limite autorizado e prazo, pedido ao autor do PCM) | Depois do PCM Bloco 2 (PCMS-A01/A02); ativos no BEN-5 | Após PCM B2 · BEN-5 |
| PCM ← BEN | MA-02 cita "OB-0104 · Packing linha 1" (`areas/maquinas.py:254`); deve citar a OB-0110 | Pedido de texto ao autor do PCM; a BEN não edita | PCM |
| BEN → Compras | Falta de caixa vira SC "A cotar" com origem Beneficiamento; a CMP cota e aprova; PC com `prevs`; o selo da ordem mostra a previsão; o EST recebe com NF; a ordem libera | Real, sobre a compra do PCM 1c (`cenGravarPedidos`, `prevAtual`, `cenReceberPedido`); grupo Embalagem na CMP e fornecedor sintético F10 | BEN-2 |
| O.S. ↔ BEN | A OB sai da O.S. (`areas/processo_os.py:169`), como a irrigação só com água. Pelo l.2841, o CO-05 tem Lista, Kanban e Mapa próprios. Mesmo componente de Kanban | Código | BEN-1 |
| Cadastros → BEN | CD-02 (código do produto), CD-03 (a13), CD-04 (Igor, Marta, e8), CD-06 (caixa, tara, fator da saca, locais) | Leitura da fonte única | BEN-1 |
| Colheita → Recebimento | Carga, peso origem × destino, umidade e base, qualidade, genealogia; colheita = O.S. com massa (as OC-* não têm trava de carência: seria S1 no software) | Depois da decisão do Codex | BEN-5 |
| BEN → Gestão (GE-03, CD-07) | Lançamentos por natureza (3.1.06 Embalagens, energia, combustível, mão de obra) × centro de beneficiamento; rateio "kg processados" | Não existe | BEN-7 |
| BEN → Comercial (VE-04) e Logística (LO-02) | Reserva e expedição reais. Hoje o LO-02 mostra o L39-120 "Pronta p/ carregar" (`areas/logistica.py:259-261`): seria S2 no software | Texto fixo oculto | BEN-8 |
| App de campo → BEN | Turno do packing e do secador, offline ("Salvo neste aparelho / Aguardando envio", nunca "Enviado") | Não existe (`areas/mobile.py:167`) | BEN-8 |
| Carência e LMR → lotes L39 | Destino dos lotes de packing; tratamento pós-colheita | Motor em `dados_carencia.py`, hoje só LC-/LM- | BEN-8 |
| Mapa (IN-04) → BEN | `CO-06#lote` → `BEN#lote` | Código | BEN-8 |

---

## 9. Leveza: orçamento de atrito

Metas. O `ben_fluxo_test.py` mede o mesmo cenário e grava a linha de base (não há fluxo antigo comparável). O último valor nunca é usado para lote, quantidade, umidade, classe, pallets ou decisão (AGENTS §3.3).

| Tarefa | Papel | Toques (meta) | Campos digitados | Herdado ou calculado |
|---|---|---|---|---|
| Criar ordem de packing com 2 lotes | Igor | ≤ 6 | 0 | produto, segmento, estágio, local, quantidades (saldo do lote, corrigível), rota (I1), ativo, caixas (I2, confirmar), datas por atalho |
| Autorizar rota e liberar | Igor | 1 | 0 | causas com dono |
| Entregar caixas | Rui (EST) | 1 ("Entregar REQ inteira", PCM) | 0 | recebedor = responsável da ordem |
| Iniciar processo | Igor | 1 | 0 | — |
| Registrar saída de fruta | Igor | 3 | 2 (caixas, bruto) | classe por toque, tara, líquido, lote de destino, balança |
| Registrar descarte ou outro destino | Igor | 3 | 1 (kg) | destino por toque |
| Registrar perda identificada | Igor | 3 | 2 (kg, ticket) | causa por toque; data, hora e balança "agora" (corrigíveis) |
| Corrigir registro | Igor | 2 + o relançamento | 0 (1 com "Outro") | fluxo, classe, estágio e destino; quantidades vazias |
| Concluir execução | Igor | 1 | 0 | — |
| Justificar diferença | Igor ou Ana | 3 | 1 (texto) | motivo por toque; quem decide pela alçada (I8) |
| Conferir balanço | Rui | 1 | 0 | fórmula aberta sob demanda |
| Fechar processo | Igor | 1 | 0 | lotes, inspeção, prazo e responsável |
| Devolver caixas | Rui (EST) | o do EST atual (medir) | 1 | — |
| Registrar resultado | Marta | 3 | 0–1 (observação) | padrão e versão; conforme ou não por toque |
| Registrar decisão | Marta | 2 | 0 (1 com motivo) | classe atingida por toque |
| Reservar para pedido | Comercial | 3 | 0 | pedido compatível e quantidade sugerida (I10) |
| Cancelar reserva | Comercial | 2 | 1 (motivo) | — |
| Registrar saída de grão ou café (BEN-3/4) | Igor | 3 | 3 (kg, umidade final, consumo do lote) | método e base da versão; água estimada |

---

## 10. Seed sintético e casos plantados (fonte única dos números)

Fazenda Santa Rita; "hoje" = 23/09/2026 (`dados.py:5`), semana ISO 39 (executado). Valores em kg com 6 casas internas; aqui sem os zeros à direita. Todas as contas foram refeitas em `Decimal` por `verificacao/contas.py` (executado), salvo indicação.

**IDs livres por busca em `v37/` e em `pcm/` (executado):** REQ-030 (REQ-026 a 028 também; a 029 aparece em `_nav.json`, a 037 em `areas/suprimentos.py`), PV-035, RS-, MP-, INSP-95, L38-116, L38-117, L38-119, L38-120, L39-117, L39-122, L39-123, L10-031, L27-019, OB-0114, CX26-01, CG-0984 a CG-0987, TK-5540, F10, Igor. **IDs herdados de propósito** (já usados nas telas ocultas, `areas/colheita.py`, `areas/comercial.py`): OB-0104, OB-0106, OB-0110, OB-0112, L38-115, L38-118, L39-118 a L39-121, L26-118, L27-013, L27-018, L27-020, L27-022, INSP-88, INSP-92 a INSP-94, CG-0988, CG-1103, CG-1205 a CG-1207, AM-3288, AM-3315, RC-12, PV-028, PV-030, PV-031.

### 10.1 Rotas (`BEN_ROTAS`; aprovação de Igor em 10/09/2026, sintético)

| Rota | Estado | Produto · estágio | Parâmetros (`par`, todos "sintético · vN") |
|---|---|---|---|
| PACK-FRU v3 | Aprovada | MAMAO · Fruta de campo; saídas Fruta embalada A e B, Indústria, Compostagem; perda Avaria no manuseio | `frac_vend` 95 %; `tol_pesado` 0,1 %; equipe 6; ativo a13; caixa 1 un por caixa de Produto; `pesagem` 'caixa'; `tara_pallet` 25 kg; `aviso_cx` ±5 %; `prazo_insp` +2 d; alçada 0,5 % e teto 100 kg; `custo_hh` R$ 32/h (BEN-2; referência D2.CONJ "equipe de café R$ 32/h", `dados_cad.py:76`); avanço no Concluir |
| PACK-FRU v4 | Rascunho | — | nunca oferecida (caso K26) |
| SEC-GRA v2 | Aprovada | MILHO, finalidade grão · Grão úmido; saída Grão seco, classe Padrão | `u_ref` 14,0 % (só milho grão); `tol_pesado` 0,1 %; `agua` {hipótese de MS validada; Δu entrada e saída 0,1 p.p.; método "medidor capacitivo · base úmida"}; alçada 0,5 % e teto 500 kg; `prazo_insp` +2 d; secador sem cadastro; avanço por saída |
| CAF-NAT v1 | Aprovada | CAFE · Fruto de café; saída Café em coco, classe Natural | `tol_pesado` 0,1 %; `agua` {hipótese de MS **não validada**}; alçada 0,5 % e teto 100 kg; `prazo_insp` +2 d; terreiro sem cadastro; avanço por saída |
| CAF-BEN v1 | Aprovada | CAFE · Café em coco; saídas Café beneficiado (classes COB tipo 6 e COB tipo 7), Casca; perdas Impurezas e Pó | `tol_pesado` 0,1 %; alçada 0,5 % e teto 500 kg; `prazo_insp` +2 d; umidade máxima do beneficiado 12,0 % (aviso; `areas/colheita.py:566`); beneficiadora sem cadastro; avanço no Concluir |

### 10.2 Semente do BEN-1 (`seed_ben()`; versão do cenário no §0.2)

**Pessoas e equipe:** p12 Igor (Responsável de produção, e8, custo sintético R$ 38/h); p13 Marta (Qualidade, e8, R$ 34/h); e8 "Beneficiamento e qualidade", líder Igor. CD-04 com 13 pessoas (11 do PCM + 2).

**Ordens** (Kanban 1 · 0 · 1 · 0 · 1):

| Ordem | Rota · janela · fase | Dados |
|---|---|---|
| OB-0110 | PACK-FRU v3 · 23–24/09/2026 · Em execução | Entradas L38-115 3.010 + L38-116 2.980 + L38-117 2.990 + L38-118 3.020 = **12.000 kg**. S-01 Produto A: 480 un, bruto 10.176 kg, destino L39-120. S-02 Produto B: 90 un, bruto 1.908 kg, destino L39-121. S-03 Descarte 600 kg (compostagem). Todos Pesado, balança a13. Inspeção planejada INSP-92. `ins` = caixa, `tot` 600; REQ-030. Histórico: CMD-42 e CMD-06 (Igor, 22/09/2026, sintético), entrega, início em 23/09, sugestão de caixas 570 confirmada em 600 (10 pallets de entrega) |
| OB-0112 | PACK-FRU v3 · 24–25/09/2026 · A liberar | Entradas L39-117 2.960 + L39-118 3.180 + L39-119 3.130 = **9.270 kg**; caixas 441 (sugestão confirmada); `versao` v1 |
| OB-0104 | CAF-BEN v1 · 15–18/09/2026 · Encerradas (consulta no BEN-1) | Coco L27-018 231.400 + L27-019 207.200 = **438.600 kg** → L27-013 221.400 kg + casca L38-119 211.900 kg + impurezas 3.100 kg + pó 2.200 kg (soma 438.600, executado); diferença 0; conferida por Rui em 18/09; histórico CMD-42 e CMD-06 sintéticos |

**Lotes de produção** (`c.ben.lotes`):

| Lote | Produto · estágio · classe | Local | Físico | Qualidade | Origem |
|---|---|---|---|---|---|
| L38-115 a L38-118 | Mamão · Fruta de campo | Packing | 3.010 / 2.980 / 2.990 / 3.020 | Em processo (OB-0110) | OC-0507 · T7 · S38 |
| L39-117 | Mamão · Fruta de campo | Packing | 2.960 | Recebido | CG-1205; T7-Q1 1.776 + T7-Q2 1.184 (estimado, mistura 60/40, `areas/colheita.py:99`) |
| L39-118 | Mamão · Fruta de campo | Packing | 3.180 | Recebido | CG-1206; origem 3.210, destino 3.180 (−30 kg) |
| L39-119 | Mamão · Fruta de campo | Packing (área segregada) | 3.130 | Em inspeção: INSP-94, Marta, prazo 24/09/2026, sem resultado | CG-1207; avaria térmica parcial; AM-3315 |
| L26-118 | Mamão · Fruta embalada · A | Packing (área de bloqueio) | 300 kg, 15 un | Bloqueado: INSP-93, vence 23/09/2026; resultado "maturação avançada em 40 % da amostra", situação Não conforme | RC-12 · PV-027 |
| L27-018 / L27-019 | Café · Café em coco | Armazém Sede | 0 | Esgotado | C1 · jul/26; umidade 11,4 % |
| L27-013 | Café · Café beneficiado · COB tipo 6 | Armazém Sede | 221.400 (3.690 sc 60 kg, executado) | Bloqueado: INSP-88, Marta, prazo 25/09/2026; resultado: defeitos 103 equiv. > 86 do tipo 6 (3 × 300 g, COB), peneira 16↑ 58 % (padrão ≥ 60 %), umidade 11,4 % (≤ 12 %); situação Não conforme (`areas/colheita.py:564-566`) | L27-018 116.807,934337 + L27-019 104.592,065663, rateio (executado) |
| L38-119 | Café · Subproduto · Casca | Armazém Sede | 211.900 | Liberado (uso interno) | OB-0104 |

Umidade do L27-013 e do coco: 11,4 % b.u., "medidor calibrado · média de 3 leituras" (`areas/colheita.py:566`); o mesmo valor nos dois estágios mantém a diferença 0 da OB-0104.

**Materiais, pedidos, sequências e PCM:**
- `c.lotes['Caixa de mamão 20 kg|CX26-01']`: Packing, físico **270 un**, reservado 0, quarentena 0, R$ 4,80. Tara do item: 1,2 kg.
- REQ-030 da OB-0110, estado Entregue: item Caixa de mamão 20 kg, lote CX26-01, un 'un', embalagem "pallet de entrega de 60 caixas vazias", solicitado 600, entregue 600, consumido 570 (480 + 90), custódia **30**, devolvido 0, `confirmado:'balcao'`, quem Igor. A semente não grava reserva em `c.movs`; o CX26-01 fica com reservado 0. Fica abaixo de REQ-041 para não mudar o número que a O.S. e o PCM geram.
- Pedido PV-031: Frutas Real · Mamão Formosa · Fruta embalada · A · **10.000 kg** (`areas/comercial.py:19-21`; janela 28/09–04/10).
- `c.ben.seq` = {lote: {38: 119, 39: 121}, insp: 105} (INSP-105 é a maior da Manutenção, `areas/maquinas.py:252`). Reservas e MP- vazios.
- PCM: a13 com `cond` "Apto" (`dados_manutencao.py:42`), lida de `c.man`.

### 10.3 Casos do BEN-1

| Caso | Números | Regras |
|---|---|---|
| K01 Balanço da OB-0110 | Tara A 480 × 1,2 = 576 → líquido 9.600; tara B 108 → líquido 1.800; descarte 600; Σ 12.000; diferença 0; recuperação **95,00 %**; A **80,00 %**; B **15,00 %**; descarte 5,00 % (executado) | R-C01, R-F01, §7 |
| K02 Genealogia | L39-120 = 2.408 + 2.384 + 2.392 + 2.416 = 9.600; L39-121 = 451,5 + 447 + 448,5 + 453 = 1.800; descarte = 150,5 + 149 + 149,5 + 151 = 600 (executado). Para frente de L38-118: L39-120, L39-121 e descarte | R-E07 |
| K03 Caixas da OB-0110 | Sugestão ⌈12.000 × 0,95 ÷ 20⌉ = **570** (executado), confirmada em 600; REQ-030 600 / 600 / 570 / 30 | R-C03, C-11 |
| K04 Sobra | Fechar recusado: "Sobra em custódia: Caixa de mamão 20 kg 30 un. Receba a devolução no Estoque." Devolução apta de 30 → CX26-01 **300 un** | R-A09 |
| K05 Fechar a OB-0110 | L39-120 9.600 kg, 480 un, e L39-121 1.800 kg, 90 un, Em inspeção; INSP-92, Marta, prazo **25/09/2026**; descarte Destinado; L38-115 a L38-118 Esgotado; MP: 2 `producao`, 1 `destinacao`, 4 `consumo_proc`; etapas exigidas Cumpridas | R-A09, R-A10, R-E01 |
| K06 OB-0112 inicial | 9.270 kg; ⌈9.270 × 0,95 ÷ 20⌉ = ⌈440,325⌉ = **441** (executado). Causas: "L39-119 em inspeção (INSP-94) · Marta" e "Caixa de mamão 20 kg: 270 un disponíveis para 441 un · Estoque" | R-A03, R-A05 |
| K07 Retirar L39-119 | 6.140 kg; ⌈291,65⌉ = **292 un** (executado); versão v2; ainda recusa 270 de 292, com a I4 (OB-0110: 30 un em custódia). Depois de K04 e sem retirar: as duas causas, agora com "300 un disponíveis para 441 un" e a I4b no lugar da I4 | R-A02, R-A05, R-C03 |
| K08 Liberar a OB-0112 (depois de K04 e K07) | REQ-041 (`cenProxId`) com 292 un reservadas; CX26-01 disponível **8 un**; L39-117 e L39-118 reservados à ordem; histórico com 2 linhas (CMD-42: v2, 6.140 kg, 292 un, PACK-FRU v3; CMD-06: REQ-041); h-linha 6.140 ÷ 2.400 = 2,558333 → **2,56 h**; HH 15,35 (executado) | R-A05, R-F05 |
| K09 Massa pesada | OB-0110 + 100 kg A: Σ 12.100 > 12.000 + 12 → recusa (executado) | R-A07 |
| K10 Ganho dentro da faixa | A com bruto 10.177: líquido 9.601; diferença **−1 kg** (−0,01 %); faixa 12 kg → conferível, "ganho aparente 1 kg" (executado) | R-A07, R-F02 |
| K11 Estorno em execução | Estornar S-02: em processo 1.800 kg, custódia 120 un. Relançar B 90 un, bruto 1.008: em processo 900. Estornar e relançar 1.908: em processo 0, custódia 30; 2 linhas riscadas; 4 MV (`estorno-consumo`, `consumo`, `estorno-consumo`, `consumo`) | R-A15, R-C02 |
| K12 Estorno na conferência | Concluir e Conferir (dif 0); estornar S-03: dif **600 kg** (5,00 %), conferência derrubada, primária "Justificar diferença"; relançar o descarte: dif 0, sem alçada (dif₀ = 0), "Conferir balanço" de novo; o Fechar destina só o descarte relançado, sem a linha estornada | R-A15, R-F07 |
| K13 Dentro da alçada | Antes de Concluir, S-02 estornado e relançado com bruto 1.868: líquido 1.760; dif **40 kg** (0,333333 %) > faixa 12 kg; limite de Igor = mín(0,5 % × 12.000 = 60; teto 100) = 60 kg → Igor justifica (executado) | R-F02, R-F03, R-G06 |
| K14 Acima da alçada | Como K13, com bruto 1.808: líquido 1.700; dif **100 kg** (0,833333 %) → Igor: "0,83 % > alçada de 0,5 %: decide Ana (gestão)"; Ana justifica (executado) | R-G06 |
| K15 Correção na conferência | A partir de K14, já em Em conferência e antes da justificativa: perda sem ticket → recusa; perda identificada "Avaria no manuseio" 100 kg com ticket, por Igor → dif 0, mas "acima da alçada de 0,5 %: decide Ana (gestão)" (dif₀ 0,83 %); Ana confirma → conferível, selo "Corrigido na conferência" | R-F07 |
| K16 Teto (só no teste unitário) | Ordem sintética PACK-FRU v3 de 40.000 kg, dif 150 kg (0,375 %): faixa 40; o % permitiria 200; teto 100 → "150 kg > alçada de 100 kg (PACK-FRU v3, sintético): decide Ana" (executado) | R-G06 |
| K17 Caixas acima da custódia | Depois da entrega de 292 un na REQ-041 e do Iniciar da OB-0112: saída com 293 un → "Caixas acima da custódia: 292 un. Peça a entrega no Estoque" | R-C02 |
| K18 Líquido por caixa | B com 80 un e líquido 1.800: 22,5 kg/un (+12,5 %) → aviso (executado) | R-C04 |
| K19 Pallet (só no teste unitário) | 480 caixas, 8 pallets, bruto 10.376: tara 576 + 200 = 776, líquido **9.600**. Ignorar o pallet daria 9.800 (20,416667 kg/cx, +2,08 %), que a R-C04 não pega (executado) | R-C01, R-C04 |
| K20 Inspeção do L39-120 | Liberar sem resultado → recusa; resultado Conforme → Liberado; a OB-0110 continua Encerradas | R-E02 |
| K21 Reserva do PV-031 | Em inspeção → recusa; Liberado: sugestão **9.600 kg**; 10.000 → "Disponível 9.600 kg"; reservado 9.600; falta **400 kg** (DEMO-06); disponível 0; RS-0001 | R-E04, R-E05 |
| K22 Bloquear o lote reservado | Bloquear L39-120 (motivo) → RS-0001 Ativa com "Expedição impedida · L39-120 bloqueado"; PV-031 "Em risco"; falta 400; disponível 0. Liberar de novo → impedimento some; nova reserva → recusa (disponível 0) | R-E03, R-E06 |
| K23 Reclassificar com reserva | L39-120 de A para B (motivo): físico 9.600 antes e depois; Σ do físico de mamão igual; RS-0001 Ativa com "Expedição impedida · classe B ≠ A"; PV-031 "Em risco" | R-E03, R-E06 |
| K24 Cancelar reserva | Sem motivo → recusa; com motivo → RS-0001 Cancelada; L39-120 disponível 9.600 (classe B); PV-031 falta 10.000; MP `reserva_cancelada` | R-E06 |
| K25 Lote não conforme | L26-118: Liberar → "Resultado não conforme (INSP-93): …"; Destinar sem motivo → recusa; com motivo → físico 0, Destinado, MP `destinacao`, rastreio visível | R-E02, R-E03 |
| K26 Rota | Fruta de campo → só PACK-FRU v3; criar com v4 (Rascunho) → recusa; lote sintético de outra fruta injetado no teste → "Sem rota aprovada para <produto> · Fruta de campo. Dono: Igor" | R-A02 |
| K27 Entrada inválida | `0`, `NaN`, `1e999` → "Informe a quantidade de entrada" | R-A04 |
| K28 ID de lote | Semente: `benLoteId(c,'2026-09-23')` = **L39-122** (semana 39, executado). Saída na OB-0112 antes do Fechar da OB-0110: destino L39-122; o Fechar da OB-0110 continua com L39-120 e L39-121. Gerador que olha só `c.ben.lotes` falha. Fechar com ID de outra ordem → recusa | R-A16 |
| K29 Condição do ativo | a13 "Apto" lido de `c.man`. Função pura: "Restrito · monitorado" → aviso; "Bloqueado" → impedimento; "Aguardando teste" → impedimento com o texto literal | R-A13 |
| K30 Repetição | Mesmo formulário de saída salvo duas vezes: 1 registro, 1 MV, `rev` +1; a segunda resposta é "Já feito". Dois quadros: o segundo recebe conflito de versão. Fixture do teste unitário (lote Liberado de 2.000 kg classe A; pedido de 1.000 kg A): reservar 1.000 e depois 500 → "falta 0 kg; nada a reservar", com o disponível em 1.000. Fechar e Autorizar e liberar repetidos: "já feito" | R-A11, R-E05 |
| K31 Inspeção nova | Primeira inspeção gerada no cenário limpo: **INSP-106** (`cenInspId` = 1 + máx(88…94, 105)) | §0.2 |

### 10.4 Casos do BEN-2 (custo e compra de caixa)

| Caso | Números | Regras |
|---|---|---|
| K40 Custo da OB-0110 | 5 h × R$ 120 + 30 HH × R$ 32 + 570 × R$ 4,80 = **R$ 4.296,00**; **R$ 0,3580/kg** de entrada (12.000); **R$ 0,3768/kg** vendável (11.400) (executado). 5 h = 12.000 ÷ 2.400; 30 HH = 12.000 × 6 ÷ 2.400; 400 kg/HH | R-F05, R-F06 |
| K41 Não calculável | `custo_hh` vazio → "não calculável: falta custo-hora da equipe (PACK-FRU v3)"; vendável 0 → "não calculável" | R-F06 |
| K42 Compra de caixa | Marta libera o L39-119 (Conforme); OB-0112 com as 3 entradas, depois da devolução de 30: 300 livres para 441 → falta **141 un**; "Pedir compra da falta" → SC nova (`cenProxId`), origem Beneficiamento, precisa 24/09/2026; F10 "Embalagens Vale" (sintético, grupo Embalagem, prazo 1 dia, CIF) → PC a R$ 4,80 = **R$ 676,80** (executado: 141 × 4,80); EST recebe 141 un com NF sintética → libera com 441 | I17, R-A05 |

### 10.5 Semente e casos do BEN-3 (grão)

**Semente:** OB-0106 SEC-GRA v2 · 20–26/09/2026 · Em execução; inspeção planejada INSP-95. L38-120 Milho · Grão úmido · Armazém Sede · físico **48.000 kg** · Em processo (OB-0106) · origem CG-0984 9.860 a 15,9 % · CG-0985 8.500 a 18,6 % · CG-0986 10.980 a 16,4 % · CG-0987 8.820 a 18,3 % · CG-0988 9.840 a 17,2 % (19–20/09/2026; Σ 48.000, executado). S-01 Produto 39.100 kg a 14,0 %, consumo do L38-120 40.900 kg, 22/09/2026, destino L39-122. Ticket sintético da pré-limpeza TK-5540: 250 kg, 20/09/2026, Armazém Sede (registro ainda não lançado). L10-031 Soja · Grão seco · classe Padrão · Silo 01 · **2.305.200 kg** (38.420 sc) · umidade 14,0 % medida · Liberado · RS-0001 de 232.500 kg (3.875 sc) para o PV-030. PV-030: Coop Grão Sul · Soja · Grão seco · classe Padrão ("Soja · padrão 25/26", `areas/comercial.py:310`) · saldo 4.000 sc = 240.000 kg; falta depois da RS-0001: 7.500 kg (executado). Item "Milho em grão" com `sc 60 kg`. `seq.lote[39]` = 122. Kanban 1 · 0 · 2 · 0 · 1.

**Expectativas do BEN-1 que mudam com esta semente** (tiradas da semente, nunca fixas no teste): K28 passa a L39-123; a reserva do K21 passa a RS-0002; o Kanban da U20 passa a 1 · 0 · 2 · 0 · 1.

| Caso | Números (todos executados) | Regras |
|---|---|---|
| K50 Mistura | L38-120 = **17,2 %** (825.600 ÷ 48.000); a média simples daria 17,28 % | R-B03 |
| K51 BEN-03 | 1.000 kg de 20 % para 10 %: **888,888889** e **111,111111** kg; quantizados a 4 casas, 888,8889 e 111,1111 (l.7561); tela 888,889 kg; soma 1.000 exata | R-B01, R-F04 |
| K52 Empate | 12,345676 kg de 30 % para 20 %: exato 10,8024665 → est **10,802467**; água **1,543209** (a forma direta daria 1,543210 e a soma passaria de m) | R-B01 |
| K53 Escala | 0,0000005 kg → 0,000001 kg; 0,0004995 → guardado 0,000500 → tela 0,001 (direto daria 0,000) | R-F04 |
| K54 OB-0106 parcial | est 39.378,139535; água **1.521,860465**; dif **278,139535**; em processo 7.100 | R-B01, R-F01 |
| K55 Concluir com em processo | 7.100 kg em processo → "Faltam 7.100 kg em processo" | R-A08 |
| K56 Final sem impureza | S-02 6.830 kg a 14,0 %, consumo 7.100: est 46.213,953488; água 1.786,046512; dif **283,953488** (0,59 %); faixa **157,551109** → fora; Igor recusado (0,59 % > 0,5 %) → Ana | R-F02, R-G06 |
| K57 Final com impureza (TK-5540) | base 47.750: est 45.973,255814; água **1.776,744186**; dif **43,255814** (0,09 %); faixa 156,980530 → conferível; recuperação **99,37 %** (45.930 ÷ 46.223,255814); impureza 0,52 % do processado; fechamento na base da saída 99,37 % + 0,54 % + 0,09 % | R-B02, R-F02, §7 |
| K58 Impureza lançada na conferência | A partir de K56: perda sem ticket → recusa; com TK-5540 por Igor → dif 43,26, mas "decide Ana" (dif₀ 0,59 %); Ana confirma | R-F07 |
| K59 Alçada de Igor | Impureza de 100 kg (só no teste unitário): dif 187,674419 (0,39 %) > faixa 157,322877; ≤ 0,5 % e ≤ 500 kg → Igor justifica | R-G06 |
| K60 Várias umidades | 39.100 a 14,0 % + 6.830 a 13,0 %, sem impureza: est 46.134,181828; água 1.865,818172; dif **204,181828**; MS 175,9 kg; mesma resposta com as saídas em outra ordem. Quantizar a umidade ponderada a 2 casas daria 46.133,488102 | R-B01 |
| K61 Ganho dentro | Saídas 45.930 a 13,9 % + impureza 250: dif **−10,139373** (−0,02 %), faixa 156,791940 → conferível como ganho aparente | R-F02 |
| K62 Ganho fora | Como K61, com as saídas a 13,4 %: dif **−275,265589** (−0,57 %), faixa 155,857661 → selo; Igor recusado → Ana "Erro de medição" | R-F02, R-G06 |
| K63 Umidade de entrada errada | Pesagem certa, com a impureza de 250 kg e uᵢ lida como 17,7 %: dif **−234,360465** (−0,49 %), faixa 156,657720 → fora; sem recusa da R-A07; Igor justifica "Erro de medição (umidade)" (≤ 0,5 % e ≤ 500 kg) | R-A07, R-F02 |
| K64 BEN-03 pesado | 889 kg pesados: dif −0,111111; faixa 3,098765 → conferível | R-F02 |
| K65 Sacas | 45.930 kg = **765,5 sc**; 2.305.200 = 38.420 sc; vazio (e não 800, 3.531,67, 68,67, 34,97) para L38-120, L38-119, L27-022 e o coco da OB-0114 | R-B05 |
| K66 Disponível da soja | 2.305.200 − 232.500 = **2.072.700 kg = 34.545 sc** (AC-50, l.4435) | R-E04 |
| K67 Fechar a OB-0106 | L39-122 Milho · Grão seco 45.930 kg (765,5 sc), umidade 14,0 % medida; Em inspeção INSP-95; L38-120 Esgotado | R-A10 |
| K68 Rotas de grão | Soja grão úmido injetada no teste → "Sem rota aprovada para Soja · Grão úmido"; milho + soja → "Entradas de produtos diferentes"; milho a 13,5 % → Secagem "Não se aplica"; saída a 18,0 % (acima da mistura) → recusa; saída sem umidade final → recusa | R-A02, R-B06, R-B07 |

### 10.6 Semente e casos do BEN-4 (café)

**Semente:** OB-0114 CAF-NAT v1 · 24/09–10/10/2026 · A liberar · L27-022 Café · Fruto · Armazém Sede · 4.120 kg a 55,0 % · Recebido (CG-1103; AM-3288). PV-028 Torrefação Serra · Café beneficiado · COB tipo 6 (classe sintética: `areas/comercial.py:314` não traz o tipo) · 500 sc = **30.000 kg**. PV-035 (sintético, livre: o maior no `v37/` é o PV-034) · Mercado interno · Café beneficiado · COB tipo 7 · 30.000 kg (destino que a fonte já prevê: `areas/colheita.py:580`). Kanban 2 · 0 · 2 · 0 · 1; a reserva do K72 é a RS-0002 (a RS-0001 é da soja).

| Caso | Números (todos executados) | Regras |
|---|---|---|
| K70 OB-0114 | Saída 2.098 kg de coco a 12,0 %: est 2.106,818182; água 2.013,181818; dif **8,818182** (0,21 %); hipótese não validada → só aviso; conferível sem justificativa; recuperação 99,58 %. Fechar → **L39-123** Café em coco Em inspeção (o L39-122 é do milho) | R-B01, R-F02, R-A16 |
| K71 Rendimento da OB-0104 | 221.400 ÷ 438.600 = **50,48 %** (coco e beneficiado a 11,4 %); teste com coco a 12,0 % e beneficiado a 11,4 %: base seca **50,82 %** | R-D02 |
| K72 L27-013 até a reserva | Reservar para o PV-028 → recusa (Bloqueado); Liberar → recusa (Não conforme, INSP-88); "Liberar como COB tipo 7" → físico 221.400 antes e depois; reservar para o PV-028 → "Classe COB tipo 7 ≠ COB tipo 6 do PV-028"; reservar 30.000 para o PV-035 → disponível **191.400 kg = 3.190 sc** | R-E02, R-E05 |
| K73 Estágio | Coco liberado → reservar para o PV-028 → "Estágio Café em coco ≠ Café beneficiado" | R-D01 |
| K74 Teto do CAF-BEN (só no teste unitário) | dif 600 kg sobre 438.600 (0,14 %): faixa 438,6; o % permitiria 2.193; teto 500 → Ana | R-G06 |
| K75 Umidade do beneficiado | OB da CAF-BEN sem umidade do beneficiado → recusa; 12,5 % → aviso e encaminhamento à Qualidade | R-B06 |

### 10.7 Plausibilidade a conferir (não bloqueia)
- O L27-013 tem 3.690 sc de C1, cerca de 97 sc/ha, contra 38 sc/ha em `dados2.py:74` e `areas/gestao.py:120`. Corrigir mexe em `dados.py:62`, `areas/processo_os.py:105`, `areas/colheita.py:111, 420, 599`, `engine.py:622` e `areas/logistica.py:299`.
- IDs herdados (L27-013, L27-020, L27-022) não seguem a semana da data do fato. Os IDs novos seguem.
- OC-0501 (01–08/09, `areas/colheita.py:93`) contra as cargas do milho em 19–20/09.
- O a13 está em "Armazém Sede" no CD-03 (`dados_cad.py:56`; `areas/cadastros.py:506`); o local do lote e da ordem de packing é o l8 Packing (`dados_cad.py:137`). A BEN mostra o local do lote; o cadastro não muda (S4).

---

## 11. Ordem de execução

### 11.1 Acordo curto (AGENTS §3.4)
```text
ID / resultado útil / persona: BEN-1 · packing de mamão de ponta a ponta: autorizar e liberar com caixas reservadas, registrar e corrigir saídas, conferir o balanço, fechar com lotes Em inspeção, liberar pela qualidade e reservar ao pedido · Igor (produção), Rui (conferência e almoxarifado), Marta (qualidade), Ana (alçada), Comercial
Requisitos do PRD e fora do escopo: 45.1-45.3, 45.5 (l.7403-7464, 7549-7567); FL-18; FL-BEN-02; CMD-06/23/24/42 (l.2777, 2794-2795, 2825); DEMO-06/07/19; RF-PRD-005 a 009; ENG-021/022; DEC-2609-13. Fora: BEN-2 a BEN-8 (§11.8) e FORA-DE-ESCOPO.md
Autor / revisor / integrador: Claude / Codex (tarefa, roteiro, reprodução, contraexemplos) / Codex
Base (commit ou hashes) / arquivos sob responsabilidade: hash do merge do PCM 1c (portões P2 e P3); arquivos do §11.2
Aceite e comando de verificação: §12 (BEN-1); bateria do §0.4
Estado / impedimento / próximo passo: especificado · aguarda P1-P3 · começar pelo 1a
```

### 11.2 PRs do BEN-1 (pequenos e sequenciais)

**PR 1a · Preparação, sem mudança de comportamento**
- `ui37.py`: + `chip_hole`, `kanban5`, `bloco`, `kline` (§0.3). `areas/processo_os.py` e `areas/processo_estoque.py` passam a importá-los; o número de cópias não aumenta.
- `cenario.js`: `cenLiberar` sem material não abre REQ. Conferir que o PCM 1b deixou `cenProxId` como regra única (`cenario.js:51` e o antigo `osc_reqId`); se faltar algo, completar aqui.
- Cópias conhecidas fora do escopo, a unificar depois com diff de render: `bloco` em `areas/processo_os.py:816`, `agronomia.py:43`, `cadastros.py:21`, `campo.py:87`, `gestao.py:54`, `inicio.py:60`, `logistica.py:62`, `processo_compras.py:62`, `processo_planos.py:374`, `processo_safra.py:13`, `suprimentos.py:78`; `kline` em `processo_compras.py:68` e `processo_safra.py:19`; Kanban estático em `campo.py:122`.
- Aceite: diff vazio do render de `OS.dc.html` e `EST.dc.html`; U21; `tabelas_os_test`, `os_cenario_test`, `os_v39_liberar_test`, `acao_unica_test`, `etapas_celular_test`, `tabelas_est_test`, `est_cenario_test`, `app_cenario_test`, `app_mb03_turno_test`, `app_mb04_test`, `est_fix2_test`, `irr_estado_test`, `quantidade_test` e `carencia_test` com o resultado de antes.

**PR 1b · Núcleo e semente, sem tela (`v` do §0.2)**
- Novos: `gen37/dados_ben.py` (`BEN_ROTAS`, `seed_ben()`, pedidos); `gen37/ben_massa.py` (espelho `Decimal`: `bal`, `faixa`, `sc`, `caixas`, `tara`, `rateio`, `alcada`, `lote_id`); `gen37/ben.js`:
  - funções puras: `benBal`, `benFaixa`, `benSc`, `benCaixas`, `benTara`, `benRateio`, `benDisp`, `benFalta`, `benCondAtivo`, `benImpedimentos`, `benEtapas`, `benArvore`, `benLoteId`, `benAlcada`, `benIndicadores`;
  - comandos (todos por `cenMudar`, com `cmd` quando acrescentam registro): `benNova`, `benRetirarEntrada`, `benAutorizarLiberar`, `benIniciar`, `benSaida`, `benPerda`, `benEstornar`, `benConcluir`, `benJustificar`, `benConferir`, `benReabrir`, `benFechar`, `benResultado`, `benDecidir`, `benReservar`, `benCancelarReserva`.
- Editados: `cenario.py`, `cenario.js`, `dados.py`, `areas/processo_os.py`, `dados_cad.py`, `areas/cad_ativos_pessoas.py` (§0.3).
- Testes: `gen37/ben_unit_test.py` (Python + node, < 30 s; U01-U24) e os ajustes do §11.5.

**PR 1c · Tela, Estoque e menu**
- Novo: `gen37/areas/processo_beneficiamento.py` (`BEN.dc.html`; `EXTRAJS[0] = cenario.js_prefixo() + ben.js + JS da tela`; a condição do ativo vem de `c.man`, sem `dados_manutencao.js_prefixo()`).
- Editados: `ui37.py` (MENU2), `areas/processo_estoque.py` (§8, linha Estoque ↔ BEN), `v37/ferramentas/acoes_duplicadas.py:15` (fora de `gen37/`), `cotest.py`.
- Testes: `gen37/ben_fluxo_test.py` (Chrome por `comp_lib`; `localStorage` limpo; < 90 s por fluxo; E01-E12) e `gen37/tabelas_ben_test.py` (T01-T09).

### 11.3 Testes novos

Formato: `ID · regra · caso · o que confere`. Números e mensagens: §10 e §4.

**`ben_unit_test.py` (Python e node sobre `cenario.js_prefixo() + ben.js`, como `carencia_test.py:9-32`)**
- U01 · R-A04 · K27 · os três valores recusados, sem exceção; `c.rev` igual.
- U02 · R-A02 · K26 · filtro por produto e estágio; v4 nunca oferecida; outra fruta sem rota.
- U03 · R-C01, R-F01, §7 · K01 · tara, líquido, diferença, recuperação e classes.
- U04 · R-C01, R-C04 · K19 · pesagem no pallet; o teste falha se o pallet for ignorado e registra que a R-C04 não pega.
- U05 · R-C03 · K03, K06, K07 · sugestões; nenhum caminho lê o último valor.
- U06 · R-E07 · K02 · rateios; propriedade com semente fixa: Σ genealogia = saída válida, em 6 casas.
- U07 · R-F04 · K53 · escala; exibição a partir do guardado.
- U08 · R-A07, R-F02 · K09, K10 · trava pesada e ganho dentro da faixa.
- U09 · R-F02, R-G06 · K13, K14, K16 · faixa; alçada pelo % e pelo teto; mensagem diz qual limite disparou.
- U10 · R-F07 · K15 · perda sem ticket recusada; correção que entra na faixa pede a alçada de dif₀; Ana confirma.
- U11 · R-A15 · K11, K12 · estornos, custódia, MV, conferência derrubada; recusas ("já estornado", inverso, A liberar, Liberadas, Encerradas).
- U12 · R-A15 · — · propriedade: lançar X e estornar X devolve balanço, custódia e consumido aos valores anteriores, X aleatório com semente fixa.
- U13 · R-A16 · K28 · gerador, colisão recusada, `seq` nunca volta.
- U14 · R-A11 · K30 · (a) mesma chave; (b) versão; (c) reserva repetida; (d) justificativa repetida: uma linha; (e) Fechar e Autorizar e liberar repetidos.
- U15 · R-E04, R-E05 · K21 · disponível; mín(disponível, falta); classe diferente e classe vazia recusadas; mesma classe aceita até o limite.
- U16 · R-E06 · K22, K23, K24 · impedimento derivado; reserva continua deduzindo; cancelar com motivo.
- U17 · R-E02, R-E03 · K20, K25 · Liberar só Conforme; "Liberar como classe atingida" grava classe e MP sem mudar massa; Destinar.
- U18 · R-A13 · K29 · `benCondAtivo` com objeto passado como parâmetro, sem tocar no `localStorage`.
- U19 · R-A09, R-A14 · K05 · `benEtapas` da PACK-FRU v3: OB-0110 com as exigidas Cumpridas; saída Produto sem caixas recusada; ordem de fixture com etapa Exigida Pendente → Fechar recusado.
- U20 · semente · K03, §10.2 · todo item de `c.reqs`: entregue − devolvido = consumido + custódia ≤ solicitado; REQ-030 com saldo a entregar 0 e solicitado = `ins.tot`; físico de cada lote Em processo = Σ entregue à ordem; Σ físico por produto igual entre Iniciar e o Fechar; Kanban da semente.
- U21 · R-A05 · — · (a) `cenLiberar(c,'OS-0430')` direto → REQ-041; (b) com a REQ-030 → REQ-041; (c) `osc_liberar` e `cenLiberar` dão o mesmo ID; (d) ordem com `ins:[]` → nenhuma REQ nova e a próxima com material → REQ-041; (e) todo ID casa com `/^REQ-\d{3}$/`.
- U22 · R-G01, R-G02 · — · todo `par` tem `fonte`; busca na semente por CPF, CNPJ, e-mail ou telefone reais = 0; nenhum `/60` nem `60` literal de saca fora do item; nenhuma constante de rendimento.
- U23 · R-C02 · K17 · caixas acima da custódia; consumo grava MV; estorno grava `estorno-consumo`.
- U24 · §0.2 · K31 · `cenInspId` no cenário limpo.

**`ben_fluxo_test.py` (Chrome)**
- E01 · F1 packing, exatamente o caminho da tarefa do proprietário (§11.7): K06 → OB-0110 Concluir → Conferir (dif 0) → K04 → EST `#sec=devolucoes`, devolução apta → a BEN redesenha sem recarregar → K05 → reservar Em inspeção recusado → K20 → K21 (com o negativo acima do disponível) → Retirar L39-119 e liberar (K08). Confere também: em Em execução a OB-0110 não mostra "Fechar processo"; o painel da OB-0110 mostra as três razões de K01; a g_lp tem "INSP-93 vence hoje" no topo.
- E02 · Estoque e balcão: no EST, a REQ-041 abre com "Entregar a" = Igor; entregar 292; a linha fica sem "Aguardando confirmação no app" e fora do k2; "Receba devoluções" mostra "Com quem: Igor"; na BEN, Iniciar e registrar saída com caixas → custódia baixa; K17. Controle: entrega na OS-0430 para Marcos continua com o chip e `confirmado:false`. Escolher Paula → a tela mostra Paula e grava Paula.
- E03 · Estorno pela tela: K11 e K12.
- E04 · Alçada pela tela: K13, K14, K15.
- E05 · Qualidade e reserva pela tela: K22, K23, K24, K25. Os lotes de café (L27-013, L38-119) abrem só em consulta, sem Registrar decisão nem Reservar (§5.3).
- E06 · Repetição e dois quadros: K30, pela tela.
- E07 · Celular: 390 e 360 px; sem rolagem da página; primária visível; painel sem corte.
- E08 · Recorte: Segmento = Frutas/HF → OB-0110 e OB-0112 → abrir → voltar → recarregar mantém.
- E09 · Medição: toques e campos das tarefas do §9 gravados como linha de base.
- E10 · Manutenção: g_rec da OB-0112 mostra "Apto" lido de `c.man`; nenhum selo "Linha parada".
- E11 · Navegar nunca executa: os atalhos de I3, I4, I4b, I9 e I12 abrem a tela (`EST.dc.html#sec=devolucoes` com `aria-current="true"` em "Receba devoluções"; `#sec=xyz` abre a seção 1); `c.rev` e `c.movs.length` iguais.
- E12 · Antes da devolução, em cenário limpo: K07 (retirar o L39-119 ainda recusa, com a I4); K09; e a variante de K07 depois da devolução sem retirar (duas causas, com a I4b).

**`tabelas_ben_test.py`**
- T01 · TF01 em g_ob, g_lp e g_pv: `multi` por ID (L38-115 ≠ L38-1150) e "(vazio)" em Condição.
- T02, T03, T04 e T06 · TF02, TF03, TF04 e TF06 em g_ob, g_lp e g_pv, a 1440 e 390 px.
- T05 · TF05 (`tabelas_inventario.py`) com 0 coluna suspeita na BEN.
- T07 · até 7 colunas iniciais em g_ob, g_lp, g_pv e g_sai a 1440 px; a 390 px a 1ª e a 2ª inteiras; ligar "Lotes de entrada" (plano A) e o TF01 passa; a escolha sobrevive a abrir, voltar e recarregar.
- T08 · g_sai por rota: a OB-0110 (fruta) não tem Umidade final; com a semente do BEN-3, a OB-0106 não tem Caixas nem Tara.
- T09 · nenhum contexto passa de 4 indicadores (contagem na tela); cada indicador abre a composição.

### 11.4 Mutantes (BEN-1)

Cada um, sozinho, tem de derrubar pelo menos o teste indicado. A saída vai para o relatório.

| Mutante | Derruba |
|---|---|
| M01 desligar a elegibilidade (R-A03) | E01 (K06) |
| M02 R-A07 sem a tolerância | U08 (K10) |
| M03 R-A09 sem `cenPodeEncerrar` | E01 (K04) |
| M04 R-A09 sem a cláusula de controles e etapas | U19 |
| M05 R-C02 desligada | U23 |
| M06 R-E05 limitada só pelo disponível | U14 (c) |
| M07 R-E05 sem comparar classe | U15 |
| M08 R-E02 aceitando Liberar com Não conforme | U17, E05 |
| M09 R-F02 sem o valor absoluto | U08 |
| M10 R-G06 sem o teto | U09 (K16) |
| M11 R-G06 desligada | U09 (K14) |
| M12 R-F07 sem a alçada de dif₀ | U10 |
| M13 `benPerda` sem exigir evidência | U10 |
| M14 estorno que não devolve caixas | U11 |
| M15 estorno que não derruba a conferência | U11 (K12) |
| M16 balanço somando o registro estornado | U11, U12 |
| M17 `benLoteId` olhando só `c.ben.lotes` | U13 |
| M18 chave desligada | U14 (a) |
| M19 versão esperada desligada | U14 (b) |
| M20 `benAutorizarLiberar` sem o evento CMD-42 | E01 (K08) |
| M21 de volta o `'REQ-' + (41 + quantidade)` | U21 (a, e) |
| M22 `estEntregar` sem `cenBalcao` | E02 |
| M23 R-E05 sem o limite do disponível | U15 (K21: 10.000 kg aceito) |

BEN-2: contar as 600 caixas entregues em vez das 570 usadas (derruba K40). BEN-3: `benAgua` devolvendo `benEst` (derruba K57); somar a água na trava da R-A07 (K63); `benFaixa` trocada pela tolerância fixa (propriedade do §11.8); média simples (K50); uma única umidade final (K60).

### 11.5 Regressões a ajustar no 1b (expectativa tirada da fonte)
- **Sem a OB-0104 na O.S.** (contagem calculada como "ordens da Santa Rita − LAM − `fam:'BEN'`"; simulação feita pela revisão, logs da revisão fora do repositório; não rodada nesta síntese):
  - `tabelas_os_test.py:56`: na Santa Rita o seletor não oferece "Sem talhão" e não aparece opção fantasma; `:62-63`: sai o passo "Sem talhão"; ficam `:66-68` e `:70-77` ((vazio) no `g2match`);
  - `os_irrig_filtro_test.py:57-59`: 10 → 9; `:94`: a 2025/26 só com a OS-0415 ("Todas 1", "Encerradas 1"); `:96`: Kanban `[0,0,0,0,1]`; ao final, `sys.exit(1 if FAIL else 0)`;
  - `os_v39_bloq_test.py:42`: contagem exata `col.split(' | ')[1] == '2'` (hoje passa por acaso nos dias com o dígito 3);
  - `os_v39_selo_agua_test.py:48-49`: 10 → 9; `ostest.py:39`: 10 → 9, com saída 1 quando falhar;
  - fora da bateria: `osacoes.py:39` 10 → 9; `verif_os.py:64` é falha antiga (Todas 8 ≠ 11 já em `0cf6f90`) e fica fora do aceite.
- **Contagens do cenário:** `est_cenario_test.py:99`, `os_cenario_test.py:87-89` e o F7 do PCM (restaurar; `pcm/` §11.3): 14 → **15** requisições (a REQ-030 entra na semente); `cada_cd04_test.py:25, 28`: 11/11 → **13/13**; lotes do EST com o CX26-01.
- **Testes que chamam `cenLiberar` direto** (`est_cenario_test.py:13-14`, `tabelas_est_test.py:66`, `est_fix2_test.py:48`, `app_cenario_test.py:15-16`, `app_mb03_turno_test.py:14`, `app_mb04_test.py:15`): descobrem o ID na hora e continuam verdes.

### 11.6 Comando de aceite
```sh
cd /home/user/sp-tab5/tools/prototipo/v37/gen37 && python3 build.py \
 && python3 ben_unit_test.py && python3 ben_fluxo_test.py && python3 tabelas_ben_test.py
bash /home/user/sp-tab5/docs/parceria/evidencias/<rodada>/00-bateria.sh   # bateria do §0.4; juízo pela linha RESULTADO/FALHAS de cada log
```

### 11.7 Homologação do BEN-1 (AGENTS §3.1 passo 3)

Antes de chamar o proprietário: o Codex revisa e reproduz; a bateria completa dá "FALHAS: 0"; `docs/STATUS.md` está atualizado.

**Tarefa curta** (o E01 percorre exatamente estes passos):
1. "Abra Produção › Beneficiamento."
2. "Na OB-0112, toque em Autorizar rota e liberar e leia as duas causas e quem resolve cada uma."
3. "Na OB-0110, toque em Concluir execução e depois em Conferir balanço (fica gravado em nome de Rui, o conferente). Toque em Fechar processo e leia a causa: caixas em custódia. Em Suprimentos › Estoque › Receba devoluções, devolva as caixas aptas da REQ-030. Volte e feche: o L39-120 e o L39-121 ficam Em inspeção."
4. "No L39-120, registre o resultado conforme e, em Registrar decisão, escolha Liberar (fica gravado em nome de Marta, da Qualidade). Toque em Reservar para pedido, aceite a quantidade sugerida para o PV-031 e confira que o pedido mostra a parte que ainda falta: o lote apto não cobre o pedido inteiro, e o sistema não deixa prometer mais que ele."
5. "Volte à OB-0112, toque em Retirar L39-119 e libere: a requisição de caixas aparece no Estoque."

**Limitações declaradas:** só o packing de mamão; o café da OB-0104 aparece só em consulta (decisões no BEN-4); grão só no BEN-3; sem custo e sem compra de caixa (BEN-2); a condição da máquina aparece, mas ainda não trava (depende do PCM Bloco 2); sem recebimento de carga; sem capacidade da linha; sem app; sem expedição. Correção de ordem encerrada só no BEN-7.

### 11.8 Blocos seguintes (um ativo por vez; cada um só abre depois do aceite do anterior)

| Bloco | Resultado útil | Regras e casos | Depende de |
|---|---|---|---|
| **BEN-2 · Packing sem parar e com custo** | Falta de caixa vira compra com previsão (I17): SC com origem Beneficiamento → CMP → PC com `prevs` → selo "Falta caixa · <SC> · prev <data> · Comprador (Ana)" → EST recebe → libera. Custo provisório do beneficiamento na g_rec. Grupo Embalagem na CMP (`dados2.py:682`; sai da lista extra de `dados_cad.py:117`, pelo `assert` de grupos únicos do PCM) e F10 com `PROPOSTAS['Embalagem']`. Regressão: `cadp_fix_test.py:75, 80` 22 → 23 parceiros (o PCM 1c deixa 22) | R-F06; K40-K42 | BEN-1 aceito |
| **BEN-3 · Grãos (milho)** | SEC-GRA v2 com mistura, matéria seca, faixa, pré-limpeza com ticket, sacas do grão seco, disponível da soja. Teste de propriedade: variar uᵢ e u_f em ±0,1 p.p. não muda a decisão de K56 nem de K57; 1 a 4 saídas com umidades diferentes: resultado independe da ordem e o sinal segue a MS; paridade Python = JS em ≥ 5.000 casos com empates e `benEst + benAgua == base` exata | R-B01 a R-B07, R-F02 (água), R-F07; K50-K68 | BEN-2 |
| **BEN-4 · Café seco** | CAF-NAT v1 e CAF-BEN v1: OB-0114, decisões do L27-013, PV-028 e PV-035, rendimento com base de umidade, "Sem material libera sem REQ" exercido | R-D01 a R-D03, R-B06; K70-K75 | BEN-3 |
| **Trava do ativo** | R-A13 com trava: o teste chama o comando de bloquear do PCM (nunca grava no armazenamento); roteiro do dono: bloquear na MA-01 → a BEN recusa → liberar o ativo → a causa some | R-A13 | PCM Bloco 2 (PCMS-A01/A02) |
| **BEN-5 · Receba as cargas e capacidade** | Recebimento (FO-13); retorno bloqueado (R-E09); criar ordem a partir do recebido; colheita = O.S. com massa; saem CO-04, CO-05, CO-05det, CO-06det e CO-07; ocupação, gargalo e déficit (I16, com o parâmetro "horas disponíveis da linha"); R-B08 (aviso); ativos novos do PCM, com horários e medições do secador e do terreiro ao longo do processo (l.7405, l.7413); ticket escolhido da balança (R-F07) | R-E09, R-B08; I16 | BEN-4; decisão do Codex sobre colheita = O.S. |
| **BEN-6 · Café completo, rotas e perecíveis** | CD e via úmida, pergaminho, fermentação, microlote, blend, reprocesso, sensorial; editor de rota ("editar cria a próxima versão"); Rascunho e Cancelada; Autorizar sem liberar, Devolver e Rejeitar; validade, câmara e FEFO; água ou ingrediente adicionado no balanço; "classe X ou melhor"; rótulo "Ordem" no EST; sacaria | R-D04 a R-D07, R-C06 | BEN-5 |
| **BEN-7 · Custos completos e indicadores** | Energia, lenha e GLP sem somar sobre a tarifa; HH com custo; rateio entre classes com método e versão; matéria-prima por estágio; CD-07 e GE-03; teto de alçada em R$; `agg='ratio'`; OEE do packing; agregados mensais; ajuste vinculado de ordem encerrada (l.7097); trava R-B08 se o dono pedir | R-F06 completo | BEN-6 |
| **BEN-8 · Campo, mercado e rastreio** | Turno do packing e do secador no app (offline); FL-19; reserva e expedição reais no VE-04 e LO-02 (corrige o S2 do LO-02); trava de expedição da R-E06; carência e LMR dos L39; serviço de terceiro (BEN-08); link do Mapa; genealogia unificada com `dados_carencia.py`; identificação do pallet até o cliente | — | BEN-7; Comercial e Logística no menu; vocabulário 74.4.3 aprovado na v3.10 |

---

## 12. Critérios de aceite (matriz de rastreio)

Negativos marcados com −. Toda recusa confere o que a R-G05 pede.

**BEN-1**

| AC | Critério | Regra | Caso | Teste |
|---|---|---|---|---|
| AC-01 | Menu com "Produção › Beneficiamento" entre Manutenção e Suprimentos; abre `BEN.dc.html`; o canvas põe a tela na página "menu" | P1 | — | E01, `varredura.py` |
| AC-02 | A O.S. não lista a OB-0104; contagens, Kanban e seletor de talhão como no §11.5; o filtro (vazio) segue coberto | §0.3 | — | §11.5 |
| AC-03 | Kanban com exatamente 5 colunas e a contagem da semente | R-A01 | §10.2 | U20, E01 |
| AC-04 | Recorte por Segmento sobrevive a abrir, voltar e recarregar | R-G04 | — | E08 |
| AC-05 − | Autorizar e liberar a OB-0112 recusa com as duas causas, cada uma com dono e atalho | R-A03, R-A05 | K06 | E01 |
| AC-06 − | Retirar o L39-119 grava v2 e a nova sugestão; a liberação ainda recusa, com a I4; sem sobra, a I4b | R-A02, R-A05, R-C03 | K07 | E12, U05 |
| AC-07 − | Saída que passa da entrada + tolerância é recusada; ganho dentro da faixa grava | R-A07, R-F02 | K09, K10 | U08, E12 |
| AC-08 − | Concluir → Em conferência; Conferir com diferença 0; Fechar recusado pela custódia | R-A08, R-F02, R-A09 | K01, K04 | E01 |
| AC-09 | EST abre "Receba devoluções" pelo endereço; a devolução apta atualiza o CX26-01; a BEN redesenha sem recarregar | R-G07, §8 | K04 | E01, E11 |
| AC-10 | Fechar cria os lotes Em inspeção, abre a inspeção com responsável e prazo, destina o descarte, esgota as entradas; disponível 0; etapas Cumpridas | R-A09, R-A10, R-E01 | K05 | E01, U19 |
| AC-11 | Genealogia para trás fecha a soma; para frente funciona com saldo 0 | R-E07 | K02 | U06, E01 |
| AC-12 − | Reservar lote Em inspeção é recusado | R-E05 | K21 | E01 |
| AC-13 − | CMD-24 sem resultado recusado; com Conforme libera; a ordem continua Encerradas | R-E02 | K20 | E01, U17 |
| AC-14 − | Reserva acima do disponível recusada; a sugestão é aceita; a falta aparece | R-E04, R-E05 | K21 | U15, E01 |
| AC-15 | Autorizar e liberar a OB-0112 grava os 2 eventos, a REQ e as reservas | R-A02, R-A05 | K08 | E01 |
| AC-16 − | Entrega de OB no balcão, em nome do responsável, sem chip do app; saída baixa a custódia; caixas acima recusadas; a O.S. continua igual | R-C02, §8 | K17 | E02, U23 |
| AC-17 | Estorno com motivo e trilha, nas duas fases; caixas devolvidas; conferência derrubada; recusas | R-A15 | K11, K12 | U11, U12, E03 |
| AC-18 − | Faixa e alçada: Igor dentro do limite; acima, Ana; o teto vale mesmo quando o % permitiria | R-F02, R-F03, R-G06 | K13, K14, K16 | U09, E04 |
| AC-19 − | Perda sem ticket recusada; correção na conferência que entra na faixa pede a alçada de dif₀ | R-F07 | K15 | U10, E04 |
| AC-20 | Bloquear, liberar de novo, reclassificar e cancelar a reserva seguem a R-E06; a massa não muda | R-E03, R-E06 | K22, K23, K24 | U16, E05 |
| AC-21 − | Lote Não conforme não é liberado; destinar exige motivo | R-E02, R-E03 | K25 | U17, E05 |
| AC-22 − | Repetição e dois quadros não duplicam registro, MV, MP nem reserva | R-A11 | K30 | U14, E06 |
| AC-23 | IDs de lote e de inspeção nunca colidem | R-A16, §0.2 | K28, K31 | U13, U24 |
| AC-24 | Condição do a13 exibida a partir de `c.man`, sem trava | R-A13 | K29 | U18, E10 |
| AC-25 − | Rota incompatível, Rascunho e entrada inválida recusados | R-A02, R-A04 | K26, K27 | U01, U02 |
| AC-26 | Escala de 6 casas; exibição a partir do guardado | R-F04 | K53 | U07 |
| AC-27 | Semente coerente (REQ, físico, Kanban) | R-G05, §3.5 | K03, §10.2 | U20 |
| AC-28 | Uma regra para o número da REQ; ordem sem material sem REQ | R-A05 | — | U21 |
| AC-29 | Indicadores: o painel da OB-0110 mostra as razões de K01; a seção de lotes mostra a inspeção que vence hoje no topo e a falta do PV-031; cada valor abre a composição; nenhum contexto passa de 4 | §7 | K01, K21 | E01, T09 |
| AC-30 | Pessoas: CD-04 com 13; Igor sem homônimo; Marta reaproveitada; nenhuma pessoa em situação contraditória no CF-01 e no CD-04 | R-G01 | §10.2 | `cada_cd04_test`, U22 |
| AC-31 | Fluxo FL-BEN-02 percorrido: recepção, classificação, embalagem, balanço, qualidade, reserva | §2 | — | E01 |
| AC-32 | Tabelas: TF01-TF06; até 7 colunas iniciais; 1ª e 2ª inteiras a 390 px | R-G04 | — | T01-T08 |
| AC-33 | 0 ação duplicada e no máximo 1 primária em cada fase e estado | R-G03 | — | `acao_unica_test.py`, `acoes_duplicadas.py` |
| AC-34 | 390 e 360 px sem rolagem da página; primária visível; painel sem corte | R-G04 | — | E07 |
| AC-35 | Navegar nunca executa | R-G07 | — | E11 |
| AC-36 | Linha de base de toques e campos gravada | §9 | — | E09 |
| AC-37 | Os mutantes M01-M23 derrubam o teste indicado | §11.4 | — | relatório |
| AC-38 | Regressão: bateria sem falha nova, juízo pela linha RESULTADO/FALHAS | §0.4 | — | bateria |

**BEN-2**

| AC | Critério | Regra | Caso | Teste |
|---|---|---|---|---|
| AC-40 | Custo provisório da OB-0110 com as três parcelas e as duas bases, rotulado | R-F06 | K40 | unitário e fluxo do BEN-2 |
| AC-41 − | Sem custo-hora ou sem vendável → "não calculável", nunca R$ 0 | R-F06 | K41 | idem |
| AC-42 | Falta de caixa sem sobra vira SC, PC com previsão e recebimento; a ordem libera; o selo mostra a previsão | I17, R-A05 | K42 | fluxo do BEN-2 |

**BEN-3**

| AC | Critério | Regra | Caso | Teste |
|---|---|---|---|---|
| AC-50 | Mistura ponderada; − a média simples reprova | R-B03 | K50 | unitário |
| AC-51 | BEN-03, empate e paridade Python = JS em ≥ 5.000 casos; `benEst + benAgua == base`; − umidade 100, `NaN`, `1e999` e u_s acima da mistura recusados | R-B01, R-F04 | K51, K52, K53, K68 | unitário |
| AC-52 − | Concluir com em processo recusado | R-A08 | K55 | fluxo |
| AC-53 − | Sem a impureza: fora da faixa; Igor recusado pela alçada | R-F02, R-G06 | K56 | fluxo |
| AC-54 | Com o ticket em Em execução: dentro da faixa; conferível; recuperação e água separadas | R-B02, R-B04, R-F02 | K57 | fluxo |
| AC-55 − | Impureza lançada na conferência sem ticket recusada; com ticket, decide a gestão | R-F07 | K58 | fluxo |
| AC-56 | Várias umidades, ganho dentro e fora, umidade de entrada errada, BEN-03 pesado | R-B01, R-F02 | K60-K64 | unitário |
| AC-57 | Sacas só com fator; disponível da soja | R-B05, R-E04 | K65, K66 | unitário e tabelas |
| AC-58 | Fechar a OB-0106 com o lote, a umidade medida e a inspeção planejada | R-A10 | K67 | fluxo |
| AC-59 − | Rotas de grão por produto e finalidade; secagem não pertinente | R-A02, R-B06, R-B07 | K68 | unitário |
| AC-60 | Fluxo FL-BEN-01 percorrido | §2 | — | fluxo |

**BEN-4**

| AC | Critério | Regra | Caso | Teste |
|---|---|---|---|---|
| AC-70 | OB-0114: diferença só com aviso; Fechar cria o L39-123 | R-B01, R-F02, R-A16 | K70 | fluxo |
| AC-71 | Rendimento com umidades e base seca | R-D02 | K71 | unitário |
| AC-72 − | L27-013: bloqueado, não conforme e classe errada recusados; "Liberar como classe atingida" mantém a massa; reserva para o pedido compatível | R-E02, R-E05 | K72 | fluxo |
| AC-73 − | Estágio diferente recusado | R-D01 | K73 | fluxo |
| AC-74 − | Teto da CAF-BEN | R-G06 | K74 | unitário |
| AC-75 − | Umidade do beneficiado obrigatória; acima do limite, aviso | R-B06 | K75 | unitário |
| AC-76 | Fluxo FL-BEN-03 percorrido | §2 | — | fluxo |

## 13. Implementação do BEN-1 (executado em 06/10/2026, branch `claude/v44-beneficiamento`)

- **Rótulo:** executado. Decisões e adaptações à base (a Colheita já cria lote, MP-, pedido e reserva): `DECISOES.md` §12 (BEN-D01 a BEN-D13).
- **Arquivos novos (`gen37/`):** `ben.js` (regras e comandos `ben*`), `dados_ben.py` (rotas, caixa, semente), `ben_massa.py` (espelho Decimal das contas, só para teste), `areas/processo_beneficiamento.py` (`BEN.dc.html`), `ben_unit.js` + `ben_unit_test.py` (node), `ben_mutantes.py` (mutantes do §11.4), `ben_fluxo_test.py` (navegador).
- **Editados:** `producao.js` (qualidade do lote beneficiado, carência e LC- pela genealogia, classe obrigatória no produto classificado, `prProxLote`, liberar lote pelo perfil), `areas/producao.py` (Estoque de produto: inspeção, resultado e decisão do lote de produção, atalhos ao Beneficiamento), `cenario.py` (cenário v5 com a semente e `ben.js` no prefixo), `dados_cad.py` (caixa de 10 kg com tara, Igor e Marta, equipe e8), `g2lib.js` (perfis Igor e Marta), `ui37.py` (Produção › Beneficiamento), `areas/cadastros.py` e `areas/cad_produtos_estrutura.py` (texto da caixa pela fonte única).
- **Casos com a caixa de 10 kg:** os números do §10.3 valem com as caixas dobradas e a massa igual (K01 tara 576 kg = 960 × 0,6; K03 1.140 sugeridas e 1.200 confirmadas; K06 881; K07 584; K08 REQ-041 com 584 un e 16 livres; K17 584 un em custódia); o próximo lote na semente é o L39-133 (K28; sequência única da Produção).
- **Fora (inalterado):** BEN-2 a BEN-8 (§11.8), a OB-0104 em consulta e a saída dela da O.S. (fica no Kanban da O.S., como antes), as abas do painel (o painel usa seções na mesma rolagem), colunas configuráveis (plano B do §5.2: 7 colunas visíveis), indicadores agregados da seção (só o selo do cabeçalho e as razões do balanço).
