# COLUNAS-1 · colunas essenciais, lote 1 (Manutenção, Apontamentos CA-*, Onboarding ON-01, Planejar safra etapas 1 e 2 e g_op)

- **Pedido do proprietário (10/10/2026, literal):** "Em várias telas vi tabelas com colunas não essenciais, elimine isso e foque somente no essencial para gestão e funcionamento do sistema e que precisa estar na tela para clareza e ação do usuário."
- **Fonte da verdade:** AUDITORIA COLUNAS consolidada (§2.1, §2.2, §3 R-01 a R-16, §1.3, §1.5 e §1.6), item §4.2 (1 a 4), e o alinhamento do Codex 6092397439 (4 a 7 colunas a 1440 px e 2 a 4 a 390 px são referência, não limite; remover coluna não remove dado, regra nem filtro útil).
- **Branch:** `claude/v44-colunas`, base `7e3d0d2`. Regime leve do protótipo (AGENTS §3.5). Sem push nem PR: o integrador junta a branch.
- **Rótulos:** **executado** = rodado nesta branch, com o comando e a saída; **especificado** = decidido e ainda não implementado.
- **Ambiente:** Chrome headless com emulação de aparelho (1440 × 900 e 390 × 844, toque a 390). Não é aparelho físico. Dados sintéticos (a Lagoa Grande é sintética).

<<COMMITS>>

## O que mudou, tela a tela

Legenda: **M** fica na linha; **D** vai ao detalhe (painel, formulário, página do registro); **R** sai (com a regra); **÷** coluna "A · B" dividida.
Em toda tela: a busca da grade (`r.s`) continua achando a linha pelo dado que saiu (executado: `colunas1_unit_test` e `colunas1_test`); unidade junto do número (R-07); estado e travas ficam na linha (R-13).

### 1. Manutenção (`areas/maquinas.py`)

**Sem ordem (g_so)** · propósito: decidir o que vira ordem (vencimentos e achados sem OM).
- M (6 → 6): Item, Ativo, O que, Prazo, Peças, Próximo passo.
- D (dentro da célula, R-12): a versão do plano ("PM-02 v2") e a periodicidade ("a cada 250 h ou 180 dias") vão ao painel do vencimento (campos Versão e Periodicidade); a leitura e a data do ativo vão ao painel do vencimento e do achado (campo "Leitura atual do ativo").
- Fica na célula do Ativo: os selos "Ativo bloqueado", "Leitura de dd/mm", "Leitura a confirmar" e "Marco estimado" (R-13).

**Ordens (g_om)** · propósito: andar as OMs pelas 5 fases (Kanban sem mudança).
- M (8 → 7): Ordem, Ativo (÷ de "Ordem · ativo", R-01), Serviço, Janela, Fase, Pendência, Executante.
- D: Tempo e Custo → painel da OM, bloco "Custo e tempos" (Estimado, Final, Tempo previsto, Horas reais) e bloco Ordens da página do ativo (Custo) (R-10). Tipo, plano e criticidade → cabeçalho do painel da OM ("Corretiva · pressão hidráulica · criticidade Alta"; "Preventiva · PM-02 v2 · Revisão 250 h") e coluna "Serviço · tipo" da página do ativo.
- Filtro Tipo: chips **Todos os tipos · Preventiva · Corretiva · Pendência** fora da grade, criados antes de o tipo sair da célula (AUDITORIA §1.5, condição); o Kanban lê o mesmo filtro. A ordem padrão por janela e criticidade vem do dado (`ma_ordFila`) e fica.
- Executante com largura máxima 130 px: com 90 px o selo "Falta: executante" vazava 22 px da última coluna e a grade rolava a 1440 (executado, medida abaixo).

**Ativos (g_at)** · propósito: ver o que está apto e o que pede ação por máquina.
- M (7 → 5): Ativo, Condição, Próxima manutenção, Em aberto, Custo no período (o Custo fica: tarefa de 1 clique do `ma_atrito_test`).
- D: Leitura → página do ativo (cabeçalho "Leitura 4.312 h · 23/09" e "Leituras e abastecimentos"); Consumo → modo Abastecimentos e bloco "Custo e desempenho"; o local → cabeçalho da página do ativo.
- Sobe para Em aberto, antes das ordens (R-13, à vista também a 390): "Leitura a confirmar", "Leitura de dd/mm" (leitura antiga) e "Desvio de consumo +N %" (desvio ≥ 15 %).

**Abastecimentos (g_ab)** · propósito: conferir lançamentos de combustível.
- M (8 → 6): Lançamento, Ativo, Volume, Data, Consumo, Qualidade.
- D: operador, evidência, Tanque/lote, Método e a leitura do abastecimento → painel do lançamento (campos Tanque/lote, Operador, Evidência, Método, Leitura).
- Filtro Tanque/lote: seletor fora da grade, criado antes de a coluna sair (AUDITORIA §1.5, condição: é o caminho para achar o combustível suspeito).

**Planos (g_pl)** · propósito: ver o estado dos planos e o que vence por plano.
- M (6 → 3): Plano, Estado, Situação.
- D: Aplica-se a (R-03, repete o nome), Serviços e o contador Ativos (R-16) → página do plano (cabeçalho, Serviços, Ativos vinculados).
- Situação ganha a pendência "N ativo(s) do modelo sem vínculo" quando o plano alcança ativo sem vínculo; sem nenhum vínculo segue "Sem ativos vinculados".

**Página do ativo · Ordens (d_om)** · 5 → 5: o nome do ativo sai da célula Ordem (é o título da página, R-03); "Serviço · tipo" e Custo ficam (é onde o tipo e o custo continuam por ordem).

**Teclado (correção):** a ≥ 1024 px o painel da 1ª OM já vem aberto ao lado; abrir outra OM pelo Enter não guardava a linha e o Esc deixava o foco no `body`. Agora o Esc devolve o foco à linha (executado no `colunas1_test`, "Esc fecha o painel e o foco volta à linha"; antes do ajuste, falhava com `BODY`).

### 2. Apontamentos (`areas/campo.py`)

**CA-01det · Apontamentos de turno (g_ap)** · 6 → 3: Data, Área do dia, Conferência. D: Turno ("Dia N de 7" repete a data, R-03), Acumulado (derivável, R-10) e Origem · sincronização → detalhe do turno (campos "Acumulado até este turno" e "Origem · sincronização"). Mesma forma no CA-01x e na O.S. (R-08).

**CA-01det · Materiais em custódia (g_mat)** · 7 → 4: Item · lote, Em custódia, A entregar, Custódia de. D: Solicitado, Entregue e Consumido → detalhe da custódia, com a conta "Em custódia = 160 − 95 = 65 L" (R-10; a mesma lista no Estoque não mostra o consumido, R-08). O lote fica (rastreabilidade).

**CA-01x OS-0420 · Instrução herdada (g_ins)** · 5 → 3: Produto, Dose da v2, Saldo de 70 ha na v3. D: Quantidade para 100 ha (dose × área) e Fonte → detalhe do produto.

**CA-01x · Apontamentos (g_ap0420)** · 6 → 3 (como o CA-01det, R-08).

**CA-01x · Materiais e custo (g_req0420)** · 7 → 4: Item, Consumido, Em custódia, Custo apontado. D: Requisição (ID técnico, R-12), Solicitado e Entregue → detalhe.

**CA-02 · Fila de conferência (g_fila)** · 7 → 5: Apontamento, Realizado do dia, Consumos e sobras, Conferência, Ação (÷ de "Conferência · ação", R-01). D: Equipe · conjunto, Horas (a divergência já aparece em Consumos), Origem · sincronização e o acumulado → formulário "Corrigir apontamento" (campos só de leitura; Horas editável).

**CA-02 · Roteiro da OS-0418 (g_proj)** · 4 → 0: a tabela projetada (Quando, Evento, Efeito, Quem) sai da fila; explica, não decide a conferência. A trilha real fica no detalhe da ordem (O.S. › OS-0418: aprovação e liberação em registros separados e trilha do insumo reservado › entregue › consumido › em custódia › devolvido). Na fila fica um bloco curto com a regra em uma frase e o "Liberar OS-0418".

**CA-03 · Ocorrências (g_oc)** · 7 → 5: Ocorrência, Local, Gravidade, Responsável, Próxima ação. D: instante, Relato (texto longo), Evidência e a área de destino ("Manutenção", "Agronomia") → formulário da ocorrência. Responsável = quem resolve (R-06; "Destino · responsável" dividida pela R-01).

**Caminho canônico (R-11):** `campo.py:61` (OS-0417 "Ver custódia"), `:264` e `:293` (CA-01det), `:335` (CA-01x) e `:394` (CA-02) levavam à SU-07 e à CA-04, ocultas; passam a `EST.dc.html#req=REQ-031/035/036`. "Requisitar material" e "Ver consumo e devoluções" do CA-01det viram um link só: "Ver REQ-035 no Estoque". O `links_ocultos_test` tira os pares CA-01det→CA-04, CA-01det→SU-07 e CA-01x→SU-07 da lista residual: um elo novo para elas volta a reprovar.

### 3. Onboarding (`areas/onboarding_backoffice.py`)

**ON-01 · Passos (g_passos)** · 4 → 3: Passo, Estado, Próxima ação. D: "Dado pedido no momento do uso" → consulta do passo (campo "Dado pedido").

**ON-01 · Trial (g_trial)** · 5 → 4: Recurso, Habilitação, Franquia, Ao esgotar ou expirar. R: Unidade → junto da franquia ("12 cenas / 30 dias", "200 interações / 30 dias", "480 ha declarados") (R-07).

**ON-01det · Importação (g_imp)** · 6 → 4: Objeto, Linhas, Erro, Estado. D: Mapeamento e Sistema de coordenadas (técnicos) → formulário do objeto; a unidade da "qtde" do estoque inicial fica no mapeamento do detalhe.

### 4. Planejar safra (`areas/processo_safra.py`, `safra.js`)

**Etapa 1 · Escolha a safra (g_saf)** · 6 → 5: Safra, Fazenda, Área, Estado, Próximo passo. D: Cultivos (contador, R-16; a etapa 2 lista). A Fazenda fica: a lista mostra safras de Santa Rita e da Lagoa Grande (varia).

**Etapa 2 · Talhões e cultivos (g_cult_*)** · 16 → 8: Talhão ou parcela, Situação, Área livre, Livre a partir de, Área, Cultura, Plano agronômico, Plantio (mais seleção e excluir).
- **Pré-condição cumprida antes do corte:** o formulário do cultivo ganhou o campo **Versão aplicada** (`ver_txt`: "v3 · versão publicada de …"; "plano de X incompatível com Y" quando não casa).
- D → formulário do cultivo: Variedade, Meta (com a unidade de mercado, DEC-0510-03), Versão aplicada, Ajustes locais ("2 ajustes de insumo só neste cultivo"), Ocupa até ("Ocupação prevista") e Fim por.
- R: Tipo (a árvore talhão → parcela já diz).
- Safra de outra ocupação: link "Safra 2026/27 ›" na célula de identificação da linha esmaecida (AUDITORIA §1.6, item 3); abre o cultivo de lá.
- Larguras máximas da AUDITORIA §2.2 (Talhão 130, Plano 170): a grade cabe na caixa de 1.116 px (executado).

**Etapa 3 · Operações (g_op)** · 8 → 6: Operação › atividade › talhão, Situação, Data, Conjunto, Horas-conjunto, Custo R$/ha. D: Rendimento ("21,60" ha/h) e Área trabalhada (em ha-op na operação, ha na atividade e no talhão, com as horas-conjunto) → formulário Rendimento (campo novo "Área trabalhada").

## Regras de corte respeitadas (prova)

- **O detalhe recebe o dado antes da coluna sair:** cada campo que saiu tem par no detalhe (`colunas1_unit_test`, grupo "o detalhe da linha tem …", e `colunas1_test`, que abre o detalhe e lê o valor).
- **Busca:** a busca da grade acha a linha pelo dado que saiu (CA-02 por "PJ-3030", "offline", "3,1 h"; CA-03 por relato, evidência, instante e destino; MA pelo tipo, ativo, plano, leitura, consumo, operador, tanque e método; SAF pela variedade, meta, versão, safra, área trabalhada e rendimento).
- **Filtro sem chip órfão:** nenhuma grade do lote guarda filtro no `sessionStorage` (só a `g_os` da O.S. usa `g2keep`). O `colunas1_test` grava um estado antigo com filtro e ordenação de colunas que saíram (Meta e Tipo na SAF etapa 2; Tempo e Custo nas Ordens) e confere que nenhuma linha some e não aparece chip "Limpar filtros". Os dois filtros de coluna que tinham uso real viraram filtros fora da grade antes do corte (Tipo das Ordens; Tanque/lote dos Abastecimentos).
- **Estado e travas à vista (R-13):** Fase e Pendência (Ordens), Condição e os selos (Ativos e Sem ordem), Conferência (CA-01det, CA-01x, CA-02), Gravidade (CA-03), Situação (SAF) ficam na linha.
- **Unidade junto do número (R-07):** nenhuma grade do lote tem coluna de unidade.

## Medidas (executado; `colunas1_evid.py`)

Antes = `_render` da base `7e3d0d2` (cópia própria montada com `build.py` e `montar_render.py`); depois = esta branch. "Rolagem lateral" = `scrollWidth − clientWidth` da caixa da grade (`.g2rola`). A 390 px a grade rola dentro da caixa com a 1ª coluna presa; a página não rola. O conjunto de 2 a 4 colunas no celular depende do contrato G2-COL (AUDITORIA §2.11, frente DS), que ainda não existe.

<<MEDIDAS>>

**Comportamento a 1440 × 900 (depois):** ordenar por uma coluna, filtrar outra, abrir o detalhe da linha e voltar; teclado a partir da busca da grade.

<<COMPORTAMENTO>>

<<NOTAS_COMPORTAMENTO>>

## Capturas

`capturas/antes-<tela>-1440.jpg`, `capturas/antes-<tela>-390.jpg`, `capturas/depois-<tela>-1440.jpg`, `capturas/depois-<tela>-390.jpg` (JPEG, qualidade 55, a 1ª grade da tela à vista). `capturas/antes.json` e `capturas/depois.json` têm os cabeçalhos, as medidas e o comportamento de cada tela.

## Testes

<<TESTES>>

## Diffs

`diff-<grupo>.patch` (contra `7e3d0d2`): `diff-MA.patch`, `diff-CA.patch`, `diff-ON.patch`, `diff-SAF.patch`, `diff-testes.patch`.

<<FORA>>
