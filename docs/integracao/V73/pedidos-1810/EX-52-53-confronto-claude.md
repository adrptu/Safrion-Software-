# EX-52 e EX-53 · Confronto Claude × Codex v1

- **Autor:** subagente do Claude, 19/10/2026. Trabalho só de leitura: nada foi editado, postado ou commitado, e nenhum teste foi executado.
- **Entradas:**
  - Claude: `docs/integracao/V73/pedidos-1810/EX-52-53-classificacao-claude.md` na composição `/tmp/claude-0/osg`. Recalculei o sha256 e ele confere com `2b41f360…` [conferido].
  - Codex v1: PR #47, comentário 6257663208 (19/10, 01:23Z), lido inteiro. Os hashes declarados (EX52 `24ef71eb…`, EX53 `46021f57…`) não puderam ser verificados: o comentário junta os dois textos sob um cabeçalho e repete duas vezes o bloco "Fechamento".
- **Bases:**
  - O Claude citou a composição `7aa910df` e o Codex, o PR #121 (`fd8a73c`, `5f51118`, `27b3633`).
  - A composição está hoje em `646854d9` e já contém o PR #121 (`e4c55028`, EX-57 F0c). As linhas citadas abaixo são da `646854d9`, relativas a `tools/prototipo/v37/gen37/`.
  - O PRD citado é o do repositório no `94e19e45`.
- **Leitura dos rótulos:**
  - "Adotar com salvaguardas" ou "com adaptação de domínio" do Codex conta como Adotar quando a salvaguarda não muda fórmula, unidade nem trava.
  - Divergência material é a que muda a decisão, uma fórmula ou unidade, uma trava ou dano, ou o escopo de uma fatia.

## 0. Resultado

| EX | Grupo | Itens | Convergem | Divergência material | Sem posição do Codex |
|---|---|---|---|---|---|
| EX-52 | J1–J8 | 8 | 7 | 1 (J6) | 0 |
| EX-52 | Fatias F1–F5 | 5 | 0 | 0 | 5 |
| EX-53 | Indicadores | 55 | 38 | 16 | 1 (K6) |
| EX-53 | Captura D1–D13 | 13 | 11 | 2 (D8, D12) | 0 |
| EX-53 | Fatias F1–F5 | 5 | 3 | 2 (F1, F5) | 0 |
| EX-53 | Financeiro | 1 | 0 | 1 | — |
| **EX-52** | | **13** | **7** | **1** | **5** |
| **EX-53** | | **74** | **52** | **21** | **1** |

Como se resolvem as 21 divergências do EX-53:
- **A fonte sustenta o Codex (11):** P1, P2, P4, P7, A5, A6 (fusão), A8, S3, K1, K4 e F1. Em nove delas o Codex expõe erro ou lacuna do Claude: P1, P2, P7, A5, A6, S3, K1, K4 e F1.
- **A fonte sustenta o Claude (8):** A14, A16, S1, S9, D8, D12, F5 e M4 (este com ressalva).
- **A fonte não decide (2):** P8 e Financeiro. A decisão é dos agentes.

## 1. Achados do confronto que valem para vários itens

- **X1 · Referências do Claude vencidas pelo PR #121.** O `_data_atv` saiu; as linhas do plano usam a data canônica (`areas/inicio.py:262-283`) [conferido no diff `12e4d03f..e4c55028`]. A dependência "espera o EX-57 F0" do J5 e do P3 está atendida na composição, ainda não na versão publicada.
- **X2 · Aprovação em lote (T1).** A decisão de 18/10 só está em `decisoes-proprietario-1810.md:19-31`. O `docs/DECISIONS.md` não a registra e o AGENTS §4 ainda diz "individual" [conferido por grep]. Pelo AGENTS §2 ela vale quando registrada, e quem registra é o Codex (`:23`). Nenhuma classificação muda: o Painel não aprova e o J7 não conta aprovação.
- **X3 · Achado novo.** A camada Custos do Mapa também tem limites fixos de 0,5 % e 10 % (`areas/inicio.py:802`) [conferido], além dos três do T3. Mesma correção, mas o arquivo é compartilhado com o EX-55 e o EX-57.
- **X4 · O que falta na v1 do Codex:** recomendação sobre dose variável (J1, exigida pelo prompt), fatias do EX-52, linhas do K6 e do P8, e a proposta financeira pelos seis critérios (`LEIAME.md:28`).
- **X5 · Defeitos achados pelos dois, de forma independente (prova forte):** cor por limite fixo (`areas/painel_gestao.py:43`, `:106`); "Execução em andamento" medindo O.S. em execução, não o plano (`areas/paineis.py:53-55`); Meu dia estático; `manCumprimento` só com encerradas (`dados_manutencao.py:1183-1184`); sem baixa de título (`comercial.js:68`, D-C07); GE-08 só demonstrativo.
- **X6 · Gemini não é necessário por ora** [inferido]: as divergências se resolvem pela fonte ou vão ao RT; margem e equilíbrio convergem depois da correção do P1.

## 2. EX-52 · ideias e fatias

| ID | Claude | Codex | Converge | Nota (fonte) |
|---|---|---|---|---|
| J1 | Adaptar | Adaptar | Sim | O Codex não se posiciona sobre a dose variável. O Claude não a inclui (etapa E3, PRD.md:4918). Sem recomendação de incluir, o tema não vai ao proprietário (prompt de ideias, linhas 40 e 92) |
| J2 | Adaptar | Adaptar | Sim | O PRD.md:3010 decide: barra e percentual no cartão e no marcador, sem pintar parte do polígono. O "progresso proporcional" do Codex se lê assim. Entra do Codex: ritmo maior que zero, senão "não estimável" |
| J3 | Adaptar | Adaptar | Sim | A saída de Estoque e Cargas (Claude) é sustentada por `visoes.py:42`, porque a visão Carga exige tempo. O Codex pede contrato de duração por domínio, sem motor genérico, o que dá o mesmo efeito |
| J4 | Adotar | Adotar (adaptadores) | Sim | O contrato do Claude equivale aos adaptadores do Codex. Somar ao contrato "reserva alheia" e "sem data não conta como coberto" (PR #121) |
| J5 | Adaptar | Adaptar | Sim | O EX-57 F0 já está na composição (X1). Entra do Codex: carência pela aplicação real e itens sem data fora da grade |
| J6 | Rejeitar no protótipo | Adaptar por estágio | **Não** | Ver 2.1 |
| J7 | Adaptar | Adaptar | Sim | Para O.S. impedida e atrasada, vale a regra do Painel: um item por O.S. (`areas/painel_gestao.py:73`) [conferido]. O Meu dia entra por atalho do Mapa, não pelo menu (EX-50, prompt de telas ocultas, linha 30), e as duas leituras batem |
| J8 | (a) Adaptar, (b) estudo | (a) Adaptar, (b) Adotar só o estudo | Sim | — |
| F1–F5 | F1 e F4 Adotar; F2, F3 e F5 Adaptar | — | Sem posição | O Codex deixou a fatia para depois do confronto. A F5 depende do J6 |

### 2.1 J6 Modo treino
- **Em comum:** os dois recusam anunciar isolamento com a troca de perfil local e exigem tenant no servidor quando for software real.
- **Diferença:** o Codex quer, já no protótipo, um cenário sintético separado com a marca "Treino" e restauração local. O Claude não.
- **Fonte:**
  - O aceite do J6, "nenhuma ação do treino aparece na organização real" (prompt de ideias, linha 71), não tem como ser provado no protótipo, onde tudo é sintético numa chave só (`cenario.js:6`) [inferido a partir do conferido pelo Claude].
  - O critério de entrada pede ganho medido e diz "Na dúvida, o item fica fora, com o motivo registrado" (`prompt-safrion-excelencia.md:785-791`) [conferido].
  - O teste com usuários é moderado (DEC-1610-02).
- **Proposta:** prevalece a posição do Claude: fora do protótipo, com registro e gatilho para o software real. A forma técnica é dos agentes (prompt de ideias, linha 93). O Codex pode reabrir se nomear o ganho medido de um roteiro guiado no protótipo.

## 3. EX-53 · indicadores

| ID | Claude | Codex | Conv. | Nota |
|---|---|---|---|---|
| P1 Margem | Adaptar | Adaptar | **Não** (fórmula) | 3.1 |
| P2 Produtividade esperada × meta | Adotar | Adaptar | **Não** | 3.1 |
| P3 Custo/ha × orçado | Adaptar | Adaptar | Sim | Os dois recusam o "% do ciclo". O orçado faseado já existe: linhas do plano com data canônica (`areas/inicio.py:262-283`). Linha sem data fica "parcial", sem cor |
| P4 Custo por unidade | Adotar | Adaptar | **Não** | 3.1 |
| P5 Equilíbrio | Adaptar | Adaptar | Sim | O preço de equilíbrio do Claude está na CAL-18 (PRD.md:4503). Preço ou produção ≤ 0 dá "não calculável" (Codex) |
| P6 Comercialização | Adaptar | Adaptar | Sim | A oferta (apto + previsão restante, `comercial.js:410-435`) é a "previsão elegível" do Codex. Exposição ≥ 0; o excesso aparece como Déficit (`:435`) |
| P7 Área em risco | Adaptar | Adaptar | **Não** (unidade) | 3.1 |
| P8 Listas | Adaptar | Sem linha; a ordem vem no P7 | **Não** (ordem) | 3.1 |
| A1 Execução do plano | Adaptar | Adaptar | Sim | Os 59 % de hoje são as O.S. em execução (`areas/paineis.py:53-55`). O Codex separa o excesso e o que está fora do plano |
| A2 Operações na janela | Adaptar | Adaptar | Sim | Coorte das janelas encerradas; número principal em contagem (KPI-PCP-01, PRD.md:8674) |
| A3 Rendimento | Adaptar | Adaptar | Sim | Não somar as horas de trator e implemento (PRD.md:7292, :7346) |
| A4 Custo da operação | Adaptar | Adaptar | Sim | Separar insumo real de operação padrão (Claude) e provisório de conferido (Codex) |
| A5 Dose aplicada | Adaptar | Adaptar | **Não** (fórmula) | 3.1 |
| A6 Receituário e carência | Rejeitar | Adaptar | **Não** (decisão) | 3.1 |
| A7 Clima | Adaptar | Adaptar | Sim | Sem série horária não há evidência. É alerta, não bloqueio (18/10) |
| A8 Focos sem decisão | Adotar | Adaptar | **Não** | 3.1 |
| A9 Tempo até a decisão | Adaptar | Adaptar | Sim | Fim = o primeiro entre O.S. liberada e decisão "monitorar" (`mip.js:176`) [conferido]. Casos abertos à vista (Codex; PRD.md:8657, por analogia) |
| A10 Vistorias em dia | Adaptar | Adaptar | Sim | Denominador = previstas já vencidas na data de corte (Codex) |
| A11 Eficácia | Adaptar | Adaptar | Sim | "Redução observada". Leitura anterior zero dá "não calculável" |
| A12 Lâmina | Adaptar | Adaptar | Sim | Em mm, não índice; a faixa 0,9–1,1 é só exemplo |
| A13 Outorga e energia | Adaptar | Adaptar | Sim | Usar o hidrômetro (`irrigacao_estado.js:522`, `:564`), não o volume comprometido (`:288`). Limites de vazão instantânea e do dia (`:305-308`) [conferido] |
| A14 Produtividade realizada | Adotar | Adaptar | **Não** (rótulo) | 3.1 |
| A15 Perdas | Adaptar | Adaptar | Sim | Pelo protocolo, nunca meta − realizado (KPI-AGR-05) |
| A16 Umidade e impureza | Adotar | Adaptar | **Não** (rótulo) | 3.1 |
| M1 Disponibilidade | Adaptar | Adaptar | Sim | CAL-06; as indisponibilidades simultâneas se unem (Codex) |
| M2 Área parada por máquina | Adaptar | Adaptar | Sim | Saldo por ativo, com o rótulo "ha-operação", como no P7 |
| M3 MTBF e MTTR | Adaptar | Adaptar | Sim | Sem falha: "não estimável". Hoje cada OM tem uma só "hora de oficina" (`dados_manutencao.py:809`) |
| M4 Preventiva × corretiva | Adaptar (KPI-PCM-06) | Adaptar (preventiva ÷ total) | **Não** (fórmula) | 3.1 |
| M5 Cumprimento preventivo | Adaptar | Adaptar | Sim | Mesmo defeito achado pelos dois (`dados_manutencao.py:1183-1184`) |
| M6 Custo de manutenção | Adaptar | Adaptar | Sim | Não somar ao custo da safra (KPI-PCM-10) |
| M7 Fila e retrabalho | Adaptar | Adaptar | Sim | HH pendentes. Retrabalho = reincidência; reabertura é só suspeita |
| S1 Cobertura de 14 dias | Adotar | Adaptar | **Não** (rótulo) | 3.1 |
| S2 Ruptura | Adaptar | Adaptar | Sim | KPI-SUP-01 sobre a projeção canônica |
| S3 Pedidos tardios | Adotar | Adaptar (junto com o S2) | **Não** | 3.1 |
| S4 OTIF do fornecedor | Adaptar | Adaptar | Sim | Entregas devidas no denominador; promessa original imutável |
| S5 Prazo de compra | Adaptar | Adaptar | Sim | Marcos do KPI-SUP-04 |
| S6 Preço pago | Adaptar | Adaptar | Sim | Comparar por nutriente só com equivalência validada pelo RT |
| S7 Acurácia do inventário | Adaptar | Adaptar | Sim | KPI-SUP-02 |
| S8 A vencer e parado | Adaptar | Adaptar | Sim | Validade sem custo não vira R$ 0 |
| S9 Quarentena | Adotar | Adaptar | **Não** (rótulo) | 3.1 |
| C1 Preço médio | Adotar | Adotar | Sim | — |
| C2 Vendida e exposição | Adaptar (funde com o P6) | Coberto pela linha "Comercialização" | Sim | — |
| C3 Custo coberto | Adaptar | Adaptar | Sim | Receita contratada líquida (CAL-18), com o rótulo "cobertura contratual" |
| C4 Oferta × compromissos | Adotar | Adotar | Sim | — |
| C5 OTIF do cliente | Adaptar | Adaptar | Sim | O ponto contratado já está no código: na retirada vale a saída; na entrega, a confirmação (R-C09, `docs/comercial/ESPECIFICACAO.md:133`) [conferido] |
| C6 Recebíveis | Adaptar | Adaptar | Sim | D-C07: não há baixa |
| C7 Aproveitamento | Adaptar | Adaptar | Sim | O `benBal` já usa a entrada da ordem e separa "outro destino" (`ben.js:204-211`) [conferido] |
| C8 Primeira inspeção | Adaptar | Adaptar | Sim | — |
| C9 Reclamações | Adaptar | Adaptar | Sim | Reclamação e devolução da mesma entrega contam uma vez |
| K1 Limite × utilizado | Adotar | Adaptar | **Não** | 3.1 |
| K2 Vencimentos | Adaptar | Adaptar | Sim | Faixas exclusivas, ou acumuladas com rótulo |
| K3 Garantias | Adaptar | Adaptar | Sim | A mesma saca não garante duas vezes |
| K4 Endividamento | Adaptar | Adaptar | **Não** (fórmula) | 3.1 |
| K5 Ficha cadastral | Adotar | Adotar | Sim | — |
| K6 Financeiro no Crédito | Adaptar | Sem linha | Sem posição | Seção 6 |

### 3.1 Divergências materiais: resolução pela fonte
1. **P1 · Erro do Claude exposto.** No Claude, preço líquido = (Σ contratado + kg não vendidos × referência) ÷ produção esperada: com contrato acima da previsão, entra receita de volume que a lavoura não tem e o preço infla. O cenário já tem períodos em Déficit (prompt do painel, linha 20; `comercial.js:435`) [conferido]. **Resolução (Codex):** receita = contratado até a produção esperada + max(0, esperada − contratada) × referência; o excesso aparece como "sobrecontratação: X kg", abre o C4 e não vira receita.
2. **P2 · Erro do Claude exposto.** O `prResultado` citado pelo Claude mede o colhido: kg recebido ÷ área colhida (`producao.js:143-149`, `:163-178`) [conferido], não a esperada. **Resolução (Codex), Adaptar:** esperada = previsão publicada ÷ área prevista; o realizado fica no A14; o denominador não muda quando a colheita começa; na soja, previsão = meta (`dados_producao.py:125`).
3. **P4 · Herda o P1 e o P2 e passa a Adaptar.** Produção zero ou ausente dá "sem dado" (CUSTO-06, PRD.md:8316); a unidade passa pelo conversor único (UNID-PROD em `producao.js`). Os dois pedem isso.
4. **P7 · Unidade.** A soma dos saldos das O.S. dá ha-operação: duas O.S. no mesmo talhão contam a mesma terra duas vezes. PRD.md:7292 e RN-005 (PRD.md:212) [conferido] sustentam o Codex. **Resolução:** número principal "ha-operação em risco", com o rótulo, e ao lado "ha físicos afetados" (união dos talhões). Fica do Claude: saldo no lugar da área total, atrasadas à parte, "clima" fora das causas.
5. **P8 · A fonte não decide.** Os dois recusam "ha × dias". Claude: classe → ha ÷ max(1, dias) → R$. Codex: criticidade → prazo → impacto. O PRD.md:6986 fala só em "fila por prazo/prioridade" e o PRD.md:7860 separa urgência de prioridade econômica. Decidem os agentes, com o Codex à frente do aceite. **Proposta [inferido]:** classe → faixa de prazo (vencida, ≤ 1 d, ≤ 3 d, ≤ 7 d) → ha-operação → R$, com o contraexemplo do Codex (100 ha em 7 d × 100 ha em 1 d) como teste.
6. **A5 · Erro do Claude exposto.** O numerador é o consumo real: KPI-CUS-04 (PRD.md:8676) e "consumo conferido" no prompt (linha 62). O informado pode ser recusado no Estoque e ficar "baixado" (`cenario.js:637`) [conferido]. **Resolução:** consumo conferido ou baixado, líquido de devoluções, ÷ (dose × área executada do trecho) − 1. Fica do Claude: a faixa do RT só colore, porque a B-R8 não tem tolerância (`cenario.js:626-631`) [conferido].
7. **A6 · Decisão.** O motivo do Claude confere: a trava segura aprovar e liberar (`areas/processo_os.py:290-293`) [conferido]. Mas a RN-018 (PRD.md:225) permite registrar fato não conforme, e o PRD.md:6986 diz que registrar não autoriza [conferido]: a exceção pode existir. **Fusão, Adaptar:** nada de % na primeira vista (Claude); duas contagens de exceção com dono (Codex), em "Atacar agora", classe 1: aplicação registrada sem autorização válida naquele momento; colheita prevista dentro da carência (`carSec`, `areas/inicio.py:1244`).
8. **A8 · Dedup.** O `areas/paineis.py:79` conta vistorias, não casos talhão × alvo [conferido]; um foco revistoriado antes da decisão conta duas vezes [inferido]. **Resolução (Codex), Adaptar:** um caso por talhão × alvo, com a idade desde a primeira vistoria acima do NC.
9. **A14 · Só rótulo.** O `prResultado` já separa o parcial, usa a área colhida e o kg corrigido pela função única `prCorrigir` (`producao.js:57-60`, `:147`) [conferido]. Fica o Adotar do Claude; a contraprova do Codex (sem desconto duplo) vira teste.
10. **A16 · Só rótulo.** O `prCorrigir` já aplica o padrão de umidade e impureza [conferido]. Fica o Adotar, com a cobertura "N de M cargas com amostra" (Codex) no ⓘ.
11. **M4 · Fórmula.** O KPI-PCM-06 (PRD.md:8660), horas emergenciais ÷ horas de manutenção, sustenta o ID do Claude. Mas não há classe emergencial no protótipo (tipos de OM: Corretiva, Preventiva, Serviço…) [conferido], e o PRD.md:7955 manda registrar a urgência à parte. **Resolução:** horas por tipo (Codex), sem o nome KPI-PCM-06, até a marca de urgência entrar no D3.
12. **S1 · Só rótulo.** O CAL-01 já é a projeção cronológica única, com cada necessidade uma vez (`cal01.js:1-10`), e com o PR #121 a demanda sem data fica fora dela [conferido]. Fica o Adotar do Claude, válido na composição.
13. **S3 · Erro do Claude exposto.** A fonte só marca o item ("chega depois da falta", `areas/processo_compras.py:406`); não há R$ [conferido]. **Resolução (Codex), Adaptar:** R$ = quantidade da linha atrasada × preço da linha, nunca o pedido inteiro.
14. **S9 · Só rótulo.** Os dois usam a quantidade na unidade do lote. Fica o Adotar, com dono e prazo no item.
15. **K1 · Erro do Claude exposto.** O `D.CRE` guarda texto ('R$ 850 mil', 'R$ 300 mil', `dados.py:80`) de uma linha só; as outras três são estáticas (`areas/gestao.py:583-588`) [conferido]. **Resolução (Codex):** limite, liberado e saldo devedor em número, por linha; "liberado" não é "utilizado".
16. **K4 · Erro do Claude exposto.** O CET é texto por linha ('14,2% a.a.', 'troca 5,8 sc/ha', '—') e não há saldo devedor (`areas/gestao.py:583-588`) [conferido]: a média ponderada do Claude não tem dado. **Resolução:** dívida ÷ receita líquida esperada (os dois); CET por linha, lado a lado, sem média, até haver saldo e fluxos; o limite de endividamento é do proprietário.

## 4. EX-53 · captura D1–D13

| ID | Claude | Codex | Conv. | Nota |
|---|---|---|---|---|
| D1 | Adaptar | Adaptar | Sim | Horas = fim − início − pausas; editar exige motivo. Troca de contador já pede decisão (`dados_manutencao.py:808`) |
| D2 | Adaptar | Adaptar | Sim | Deslocamento é motivo próprio, não parada mecânica |
| D3 | Adaptar | Adaptar | Sim | Gravar o momento efetivo da falha e a hora do registro (Codex). Horas por mecânico como HH |
| D4 | Adaptar | Adaptar | Sim (desenho) | O escopo na F1 diverge (seção 5) |
| D5 | Adaptar | Adaptar | Sim | Protocolo do RT antes de qualquer uso |
| D6 | Adaptar | Adaptar | Sim | Promessa original imutável; hoje ela é sobrescrita (`areas/processo_compras.py:618`, citado pelo Claude) |
| D7 | Adaptar | Adaptar | Sim | O R-C09 já separa retirada e entrega |
| D8 | Adotar | Adaptar | **Não** (rótulo) | O `benBal` tem faixa de conferência e "em processo" (`ben.js:204-214`) [conferido]. O reprocesso vinculado não existe (nenhuma ocorrência em `ben.js`) [conferido] e fica como pendência, fora do D8 do prompt. Fica o Adotar |
| D9 | Adaptar | Adaptar | Sim | Primeiro resultado imutável |
| D10 | Adaptar | Adaptar | Sim | Limite acumulado pela quantidade entregue |
| D11 | Adaptar | Adaptar | Sim | Configurações guarda só o que falta (limites, plano de comercialização, valor de reposição, calendário). A meta de produtividade continua no cultivo e é lida de lá (o "não criar segundo cadastro" do Codex) |
| D12 | Adotar | Adaptar | **Não** (rótulo) | Já existem "Sistema na data de corte", recusa de contagem desatualizada e outro contador na recontagem (`areas/processo_estoque.py:124`, `:378-398`, `:435`) [conferido]. Fica o Adotar; falta só a leitura por código |
| D13 | Adaptar | Adaptar | Sim | O hidrômetro já é obrigatório; falta a energia |

## 5. EX-53 · fatias

| ID | Claude | Codex | Conv. |
|---|---|---|---|
| F1 | Regras no que existe, T3/T4 e D1, D2, D3, D11; o D4 só com a hora | D11 e eventos D1–D4 com recuperação, conflito e rejeição | **Não** (escopo do D4) |
| F2 | Adaptar | "Não é só ligar dados" | Sim |
| F3 | Adotar | Depende das fontes canônicas do PR #121 | Sim: o PR #121 já está na composição (`e4c55028`) |
| F4 | Adaptar | Depende de dados e da decisão vigente | Sim |
| F5 | Adaptar (sai o D12) | Métricas só com cobertura | **Não** (segue o D12) |

- **F1 · Erro do Claude exposto.**
  - O prompt põe o D4 na F1 (prompt do painel, linha 156), e o registro de 18/10 diz que "a condição real da aplicação fica registrada" (`decisoes-proprietario-1810.md:12`) [conferido].
  - **Resolução:** na F1, o D4 grava a hora e a condição (da estação ou digitada, com a origem). Só a avaliação contra o limite espera o RT e o EX-54.
  - Também fica do Codex a prova de sincronização sem duplicar (ENG-021/022), sem prometer offline real multiusuário só com o `localStorage`.
- **F5:** segue o D12 e fica com o Claude.

## 6. Financeiro (decisão delegada aos agentes)
- **Claude:** proposta pelos seis critérios: título a pagar nasce no recebimento conferido; o Painel mostra "fluxo previsto", não "caixa"; nenhuma lista nova; sem ERP, recebimento e pagamento são registrados na origem.
- **Codex:** não propôs; pede reaproveitar a D-C07 antes de ampliar as baixas.
- **Fonte:** o `LEIAME.md:28` manda cada agente propor sozinho pelos seis critérios, e o Codex registra [conferido]. A D-C07 (`docs/comercial/DECISOES.md:13`): o protótipo não registra recebimento; pagamento é do Financeiro (GE-05, oculto), porque fazê-lo no Comercial "seria um segundo lugar para o título"; retomada quando o GE-05 entrar no estado [conferido].
- **Conflito:** o critério 4 do Claude ("Registrar recebimento" na venda) contraria a D-C07 enquanto o GE-05 existir; o critério 2 tira o GE-05 e, com ele, a premissa da D-C07. A proposta do Claude precisa dizer, com motivo, que revisa a D-C07.
- **Proposta:** a D-C07 vale até a decisão ser registrada; o Codex publica a sua proposta pelos seis critérios; se os dois aceitarem "título na origem, GE-04 e GE-05 fora", a D-C07 é substituída no mesmo registro. Não vai ao proprietário (ele delegou); banco, contrato e custo reais continuam com ele.

## 7. O que os dois já concordam e pode virar a primeira fatia
Cada ponto abaixo foi conferido nos dois pareceres e no código.
- **T3:** cor sem meta.
  - A régua fixa de 10 % está em `areas/painel_gestao.py:43`, e o cartão "Ativos liberados" é comparado com 95 % em `:106`.
  - Isso conflita com o PRD.md:8714 ("meta não configurada não recebe verde automático") e com as regras 4 e 5 do EX-53.
- **T4:** o mesmo "% do orçado" é calculado duas vezes no Painel (`areas/painel_gestao.py:93` e `:170`), fora do `custo_dominio.py`.
- **M5:** o `manCumprimento` conta só as preventivas encerradas (`dados_manutencao.py:1183-1184`), contra o KPI-PCM-05 e o KPI-PCM-09 (PRD.md:8659, :8663).
- **M1:** "Ativos liberados" não é disponibilidade; os dois concordam que o cartão perde a cor.
- **Outros pontos sem divergência, que entram nas próprias fatias:**
  - J2 sem pintura de fração;
  - J4 com contrato por domínio;
  - J7 sem ranking;
  - J8(b) só como estudo;
  - captura D1, D2, D3 e D11, com o D4 incluindo a condição.

## 8. Primeira fatia proposta: EX-53 F1a, "número honesto no Painel"
- **Resultado útil:**
  - o gestor deixa de ver cor sem meta e "% do orçado" em dobro;
  - o PCM passa a ver o cumprimento de preventiva com as atrasadas na base.
  - Dano evitado: decidir por uma cor sem meta e por um cumprimento inflado.
- **Escopo:**
  1. **T3 no Painel:** sem limite configurado, o cartão fica sem cor de estado e mostra "meta não configurada". "Ativos liberados" vira contagem sem cor.
  2. **T4:** o `custo_dominio.py` entrega o % do orçado consumido e o Painel só lê.
  3. **M5:**
     - denominador: preventivas com vencimento original no período, encerradas ou não, mais os vencimentos sem ordem (`manSemOrdem`);
     - numerador: as feitas até o vencimento original.
- **Fica fora, para a F1b, junto com o D11 e a captura D1–D4:**
  - a camada Custos do Mapa (`areas/inicio.py:802`, arquivo compartilhado com o EX-55 e o EX-57);
  - o `INT_LIM` (`inteligencia.js:6`).

| Arquivo ou papel | Dono | Situação |
|---|---|---|
| Aceite e roteiro (acordo da §3.4, arquivo da rodada) | Codex | Dono da análise EX-52/53 |
| `areas/painel_gestao.py` | Claude (proposto) | **Sem dono na divisão vigente.** Autor histórico: Claude (PAINEL-03, `9c6e587c`) |
| `areas/custo_dominio.py` | Claude (proposto) | **Sem dono na divisão vigente.** Autor histórico: Claude (PAINEL-02, `bff02ff1`) |
| `dados_manutencao.py` (`manCumprimento`) e `areas/maquinas.py:431` (leitura) | Claude (proposto) | **Sem dono na divisão vigente.** O `maquinas.py` já tem o VIS-08 do Claude (`37c3ecb6`) |
| Testes novos de unidade e contraprova | Claude; o Codex reproduz | — |
| Composição, base verde e publicação | Claude | Divisão vigente |
| Checkpoint (issue #1) e registro no `DECISIONS.md` | Codex | — |

- **Aceite medido** (combinar com o Codex antes do código):
  - Nenhum cartão do PG sem limite configurado tem cor de estado. Contraprova: a versão atual pinta "Ativos liberados 94 %" pela régua de 95 % e põe verde em todo desvio ≤ 0.
  - O % do orçado tem um cálculo só: o `areas/painel_gestao.py` não contém mais `real_total_rs/g.orcado_rs`. Prioridades e Alavancas mostram o mesmo número.
  - M5: uma semente com uma preventiva vencida e não feita no período baixa o cumprimento. Contraprova: o `manCumprimento` atual a ignora.
- **Verificação (§3.5):**
  - testes de unidade das regras;
  - `build.py` com a varredura das páginas;
  - `painel03_test.py`, `painel_modulos_test.py` e os testes da MA.
  - Nada disso foi executado nesta análise.

## 9. O que a fonte não decide, e quem decide
- **Agentes:** a ordem do P8; a reabertura do J6, só com ganho medido; o Financeiro diante da D-C07; a base declarada do ritmo do J2.
- **RT:** a faixa do A5; os limites do D4 e do A7 (com o EX-54); o n mínimo do A11; o protocolo do A15 e do D5; a equivalência do S6; a meta do A9.
- **Proprietário:** o limite de endividamento (K4); usar o J7 como meta de avaliação, o que nenhum dos dois propõe.
- **Registro pendente:** a aprovação em lote de 18/10 no `DECISIONS.md` e no AGENTS §4 (Codex, X2).
