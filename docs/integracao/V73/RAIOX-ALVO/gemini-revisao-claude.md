# Raio-X do alvo · revisão do Claude da consolidação Gemini feita pelo Codex

Versão 1 · 17/10/2026 · autor Claude · revisor e registro: Codex.
**Versão 1.1 · Δ 17/10**, depois do retorno do Codex (comentários 6227947437 e 6227991541 do PR #47): §10. O texto da versão 1 fica preservado; onde ele mudou, há um ponteiro "→ Δ 17/10-n".
- Pedido: comentário 6227680115 no PR #47.
- Gemini **não** consultado de novo nem simulado. O recibo da resposta dele não está copiado aqui: está em `bff2e0e:docs/integracao/V73/RAIOX/codex/gemini/parecer-gemini.json`. Quando cito a resposta, resumo o trecho e indico a pergunta (`RG Qn`).
- Só leitura e verificação. Nenhum arquivo de produto foi alterado, nada foi enviado ao GitHub e não há dados reais.
- Proposta de contrato no arquivo irmão `rx0-contrato-proposta.md`.

## 0. Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: RAIOX-ALVO passo 3 · revisão crítica das 9 ressalvas da consolidação Gemini, com Q2 executada, e proposta mínima do RX-0 · Codex (registro), RT e proprietário (indiretos)
Requisitos do PRD e fora do escopo: os do passo 1 (CL:11) e EX-42 §6–§8 · fora: implantação, checkpoint, nova consulta ao Gemini, comentário no PR, adoção de método ou parâmetro
Autor / revisor / integrador: Claude / Codex / Codex registra (divergências e fontes voltam a ele antes de qualquer adoção)
Base: consolidação bff2e0e (codex/raiox-avaliacao-20261017); avaliação Codex b291746; confronto 45b097f; PR #47, comentários 6227548175, 6227625864 e 6227680115; pedido e v3 em 529adf7 (SHA-256 e7872cb0…805e5e); PRD e DECISIONS em origin/main c8274086; EX-42 em b989864 · arquivos: docs/integracao/V73/RAIOX-ALVO/{gemini-revisao-claude.md, rx0-contrato-proposta.md, reproducao/gemini/**}
Aceite e comando de verificação: git show 529adf7:docs/integracao/V73/pedidos-1610/raiox-pragas-no-tempo-v3.html > /tmp/v3.html; bash docs/integracao/V73/RAIOX-ALVO/reproducao/gemini/rodar.sh /tmp/v3.html <saída> → saída 0 e duas linhas "igual ao versionado"
Estado / impedimento / próximo passo: entregue · o Codex aceita, ajusta ou recusa cada posição da §3 e as divergências da §7 e registra o RX-0
```

**Como ler.**
- `CG:n` é a linha de `consolidacao-codex.md` e `PG:n` a de `pacote-gemini.txt`, ambas em bff2e0e.
- `CL:n` (linha em 34e411a, sem a linha de errata), `CX:n`, `PED:n`, `ART:n`, `EX-42:n`, `PRD:n` e `DEC:n` seguem a legenda do confronto (`confronto-claude-codex.md`, linha 16).
- `K1`–`K11` são os casos de `reproducao/gemini/q2_ht.txt`; `V1`–`V3`, os blocos de `reproducao/gemini/v3_verificacoes.txt`.
- **Executado**: rodei e a saída está versionada. **Lido**: leitura sem execução. **Especificado**: proposta ainda não testada.

## 1. Resumo

- **As 9 ressalvas:** concordo com 4 (R1, R3, R5 e R6), concordo com ajuste em 5 (R2, R4, R7, R8 e R9) e não divirjo de nenhuma. O resumo do Codex no comentário 6227680115 confere com o texto da consolidação, item a item (§2).
- **Q2, executado (K1–K11, V1):**
  - a conta do Codex está certa: na forma de produto, T_antes 10, T_depois 5, C_antes 0 e C_depois 10 dão E = 1, sem divisão por zero;
  - mas o resultado **não depende do tratado**: com C_antes = 0, E = 100 % mesmo com o tratado indo de 10 a 1.000 (K2). Não é só "comparação operacional inadequada": é não identificação, e vira regra fixa do contrato, não parâmetro;
  - a mesma letra muda de sentido: "Ca" é o controle **antes** no PED:121 e o controle **depois** na consolidação (K8);
  - com o ε do v3, os casos indefinidos viram números plausíveis. "Controle zerado antes e depois" dá 47,6 %, igual ao caso regular (K5 = K6); o tratado zerado antes dá −400 %, e o zerado depois cai de 100 % para 95,2 % (K3, K7, V1).
- **N5 deixa de ser só leitura estática** (executado, V3). Em 21 sementes, o avaliador da 2ª leitura (futura na origem) está no modelo do teste em 84 de 84 alvo-sementes. Ele muda o Brier em 79 de 84, no máximo 0,0116, e não muda nenhuma vitória sobre a persistência. O vazamento existe e o dano é pequeno neste gerador, porque o avaliador não tem efeito plantado.
- **A consolidação deixou de fora 9 pontos (§5).** Os de maior peso:
  - o Gemini diz que o HT "pressupõe populações uniformes". É o Abbott que pressupõe; o HT é o Abbott generalizado para partidas diferentes (K11) e já é uma diferença de diferenças em log (K10) → Δ 17/10-6: só como identidade algébrica, com valores positivos;
  - o PED:124 manda usar Abbott sem leitura antes, e ninguém decidiu isso;
  - o pacote descreveu "revisitas de 3 dias" no v3, mas o v3 não tem nenhuma (V2);
  - o gerador nunca produz zero (V2);
  - no gerador, toda aplicação é disparada por leitura alta (V2).
- **4 divergências materiais com o Codex** (§7), cada uma com a forma de resolver.

## 2. O resumo do Codex confere com o texto da consolidação

| Afirmação do comentário 6227680115 | Onde está | Confere |
|---|---|---|
| Corrigiu a Q2: E = 1 − Ta×Cb/(Tb×Ca); Cb = 0 não é divisor; Tb e Ca são | CG:14 | Sim. A aritmética foi conferida (K1, K3, K4) |
| Rejeitou promover 3–14 dias e o exemplo do satélite < 5 dias | CG:16 | Sim |
| Rejeitou descartar o par inteiro por uma covariável ausente | CG:16 | Sim |
| Rejeitou a promessa de "risco por extrapolação" na UI | CG:17 | Sim |
| Rejeitou presumir que a reaplicação vem da falha do controle | CG:15 | Sim |
| Rejeitou exigir GLMM, PSM ou DiD automaticamente | CG:19 | Sim, inclusive Turnbull e riscos competitivos |
| Sem referências identificadas | CG:3 | Sim. A resposta nomeia métodos, mas nenhuma obra com autor, ano e título (lido em RG Q1–Q6) |
| Retirar os selos e trocar por coocorrência é proposta do Gemini | CG:21 | Sim |
| Uma chamada, STOP, pacote sintético de 6.863 bytes | CG:3 | Sim: `wc -c` do pacote dá 6863; o recibo traz `finishReason: STOP` e um só `responseId` (lido) |

## 3. Ressalva por ressalva

### R1 (CG:13) · "réplicas confirmam subestimação" e "métodos clássicos geram artefatos" não estão provados — **concordo**

- As 20 réplicas só variam o ruído: o v3 fixa os dias de chuva e as ondas de calor (ART:296, :313; CL:253). Elas não são safras independentes e não medem cobertura de intervalo. Cobertura exige a magnitude verdadeira, e o gerador não tem oráculo (CL:253). Por isso o RX-0 cria o oráculo (ORA-03).
- Os números do ruído contrariam a generalização. Nas variáveis sem efeito, F/M saiu em 4/480 (0,8 %), abaixo dos 5 % do PED:210 (X-04). O que o C5 indica é outra coisa: nas variáveis **selecionadas**, o intervalo com a seleção fixa é estreito demais (7/14 → 2/14, R-C5), e isso é só indicativo (confronto §2).
- "Clássico gera artefato" confunde o método com o pressuposto. O HT é válido sob tendências paralelas em log (K10); o defeito do v3 está nos dados futuros e no fallback (X-05, X-08), não na idade da fórmula.
- Fonte: confronto §2 e §4.5; `reproducao/resumo.txt`.

### R2 (CG:14) · Q2: Cb = 0 não é divisor; Tb e Ca são — **concordo com ajuste**

Concordo com a aritmética da forma de produto e com "não exibir 100 %" (executado, K1, K3, K4). Ajustes:
1. **Não identificação, não só "motivo operacional".** O estimando do HT é a razão entre o fator do tratado e o do controle. Com C_antes = 0, o fator do controle é 10 ÷ 0: a forma de produto esconde a divisão. O resultado fica preso em 100 % para qualquer tratado (K2: T 10 → 1.000 dá 100 %). É regra estrutural, fixa no código, e não pode ser "adotada" por protocolo.
2. **Notação.** O PED:121 usa a = antes; a consolidação usa a = after. "Ca = 0 é divisor" é verdade na consolidação e falso no pedido (K8). O Gemini disse "controle anterior zerado" para um exemplo cujo zero era o tratado antes (PG:13, RG Q2), o que pode ser o mesmo tropeço. Proposta: registrar só com T_antes, T_depois, C_antes e C_depois (EST-3a).
3. **O ε não só "suaviza": apaga a diferença entre válido e inválido.**
   - controle zerado antes e depois dá 47,6 %, igual ao caso regular (K5 = K6);
   - tratado zerado depois cai de 100 % para 95,2 % (K7).
   No v3 real (V1): tratado zerado antes −400 %, controle zerado depois −1.000 %, tratado zerado depois 95,24 %. O controle zerado antes sai nulo porque o v3 tem um piso de 10 % do NC só no controle (ART:628), parâmetro sem fonte e assimétrico.
4. **Os casos 0 ÷ 0** (K4b, K5) e o **controle perto de zero** (K9: tratado quintuplica e E = 95 %) entram no contrato. Zero exato é regra estrutural; "perto de zero" pede piso do protocolo, pendente, igual para tratado e controle.
5. **Agregação de vários controles.** O v3 usa a mediana das razões (ART:631), e o PED:121 sugere razão de médias. É escolha de estimando, não citada (O9).

### R3 (CG:15) · não presumir que a reaplicação vem da falha; censura não informativa não pode ser presumida — **concordo**

- No gerador do v3, a reaplicação é informativa **por construção**. Toda aplicação vem depois de uma leitura ≥ 0,9 × NC ou ≥ 1,15 × NC, conforme o talhão (ART:370, :398). Executado (V2): 1.528 de 1.528 aplicações em 21 sementes (→ Δ 17/10-3: o V2 prova só que existe leitura anterior elegível; o vínculo de gatilho vem da leitura do ART:398); 499 delas (33 %) com a leitura-gatilho entre 0,9 × NC e o NC. Na fazenda real, há também calendário, campanha e outro alvo. Logo, o motivo precisa ser dado (V-06 e GER-11 do RX-0), e a estratégia depende do estimando, como diz o Codex.
- Isso segue o arcabouço de estimandos com eventos intercorrentes do ICH E9(R1), *Addendum on estimands and sensitivity analysis in clinical trials* (2019): composto, política de tratamento, hipotético e "enquanto em tratamento" são estratégias declaradas antes, não consertos depois.
- No seguimento, a estratégia já acordada (N4: encerrar na nova aplicação, com estado próprio) é "enquanto em tratamento". Na camada 4, proponho a estratégia composta por motivo (EST-4, divergência D4), como alternativa avaliada, não adotada.

### R4 (CG:16) · não descartar o par inteiro por uma covariável; 3–14 dias e "satélite < 5 dias" não viram regra — **concordo com ajuste**

- Concordo: as faixas 7/3–14 e 10/5–14 "não viram padrão universal" (EX-42:38). O 3–14 era proposta do Claude (CL:89), e o Gemini a tratou como "conforme protocolo" (RG Q6).
- **Ajuste: "uso" precisa de definição operacional,** senão cada camada interpreta de um jeito:
  - **camada 1** (uma variável por vez): casos disponíveis por variável, com n por variável;
  - **camada 2** (modelo conjunto): casos completos no conjunto declarado, com a contagem e o motivo de cada exclusão. A sensibilidade ao mecanismo de falta é aceite do RX-2, não opcional (RX0-A3, ADV-13).
- A contraprova do Gemini ("rodar com casos completos e com o pior cenário nas lacunas") serve como **desenho de teste** (sensibilidade com limites). Os limites biológicos vêm do protocolo, pendente. A consolidação não a avaliou (O7).

### R5 (CG:17) · a UI não promete "risco por extrapolação" — **concordo**

- A recomendação do próprio Gemini é "indisponível" (RG Q4); o texto final a contradiz. Motivo específico e próximo passo seguem o X-19.
- Acrescento o N1: numa data passada, o "Próximos 7 dias" também fica indisponível sem previsão arquivada daquela data (ADV-02).

### R6 (CG:18) · "talhões controlados" e "desempenho sequencial" sugerem eficácia; não trocar os estados do seguimento — **concordo**

- Os baldes do Gemini (RG Q3) juntam "1ª leitura pós acima do NC" com "acima do limiar". Assim, perde-se o "retorno não demonstrado" do EX-42:42, e somem a censura na última leitura e o intervalo.
- O texto da Q5 ("Produto A no 1º uso variou X %") leva à comparação por produto, que vira ranking (PRD:6215; EX-42:40). Os estados ficam os do EST-3b.

### R7 (CG:19) · GLMM, clusterizados, PSM/DiD, Turnbull e riscos competitivos não são exigência; tendência paralela não se "comprova" — **concordo com ajuste**

- **Ajuste 1: o HT já é uma DiD em escala log** (executado, K10). ln(1 − E) = [ln T_depois − ln T_antes] − [ln C_depois − ln C_antes], com erro máximo de 3,1e-13 em 1.000 quádruplas. "Migrar de HT para DiD" (RG Q2) não troca de pressuposto. A pergunta certa é se a tendência paralela em log se sustenta. → Δ 17/10-6: a identidade vale só para valores positivos e não prova identificação causal, tendência paralela nem equivalência a qualquer estimador DiD.
- **Ajuste 2:** a contraprova do Gemini (trajetórias antes da aplicação já divergentes) é um **teste de falseamento** útil: pode reprovar, não provar. Ela pede ao menos 2 leituras antes, que o RX-0 exporta (U5, EST-3a). A janela de 14 dias do exemplo não é critério.
- **Ajuste 3:** "erros clusterizados" já existem em forma de bootstrap em blocos de talhão × semana (ART:596-601; Owen, 2007, citado na CL:101). O defeito é não refazer a seleção (X-11), não a falta de cluster.

### R8 (CG:20) · permutar exige nula e esquema válidos; um embaralhamento isolado não identifica autocorrelação — **concordo com ajuste**

- **Ajuste:** no gerador, há um controle negativo melhor que a permutação: o **mundo nulo**. Desliga-se o mecanismo e o efeito verdadeiro vira 0 por construção (ORA-07, ADV-15).
- A permutação fica para calibrar o p (E1), com:
  - H0 declarada;
  - unidade de troca declarada: semana para clima da fazenda, talhão para variável fixa no talhão;
  - K permutações com semente;
  - p = (1 + k) ÷ (1 + K) (Phipson e Smyth, 2010).
- Rejeitar H0 de permutação mostra associação, não efeito (ADV-16).

### R9 (CG:21) · retirar todos os selos e trocar por coocorrência é proposta do Gemini, não consenso — **concordo com ajuste**

- **Ajuste: recusar a coocorrência**, não só deixá-la como "não consenso" (divergência D3).
  - Para manejo, a contagem crua aplicação × nível é exatamente a armadilha +0,59 que o pedido proíbe mostrar como efeito (PED:32, :120, :239).
  - Para clima, a contagem crua mantém o confundimento com a época, que o selo pretendia evitar (X-13).
- O pedido já tem o estado certo para "não sei": **Insuficiente** (PED:136). Ele vale até o RX-2 passar no gabarito.

## 4. Q2 em números (executado)

Fontes: `q2_ht.txt` (aritmética pura) e `v3_verificacoes.txt` V1 (o `rxHT` extraído do v3, D = 10, NC 10, ε = 0,5).

| Caso | T | C | HT, forma de produto | v3 com ε (V1) | Contrato (EST-3a) |
|---|---|---|---|---|---|
| Regular (K6) | 10 → 5 | 10 → 10 | 0,5 | 0,4762 | 0,5 |
| Tratado zerado depois (K7) | 10 → 0 | 10 → 10 | 1 | 0,9524 | 1, "zero observado depois" |
| Tratado zerado antes (K3) | 0 → 2 | 10 → 10 | −∞ (÷ 0) | −4 | sem comparação: tratado zerado antes |
| Controle zerado antes (K1, K2) | 10 → 5 | 0 → 10 | 1 para qualquer T_depois | nulo (piso de 10 % do NC) | sem comparação: controle zerado antes |
| Controle zerado depois (K4a) | 10 → 5 | 10 → 0 | −∞ (÷ 0) | −10 | sem comparação: controle zerado depois |
| Controle zerado antes e depois (K5) | 10 → 5 | 0 → 0 | NaN (0 ÷ 0) | nulo (com ε puro: 0,476) | sem comparação: controle zerado antes |
| Controle no piso (V1) | 10 → 50 | 1 → 10 | 0,5 | 0,3129 | piso do protocolo, pendente |

## 5. O que a consolidação deixou de fora

| # | Ponto | Prova | Efeito |
|---|---|---|---|
| O1 | Notação invertida entre o PED:121 e a CG:14 | K8 (executado) | Registrar com nomes explícitos (R2) |
| O2 | O Gemini afirma que o HT "pressupõe populações uniformes" (RG Q2). O pressuposto de partida igual é do Abbott; o HT o generaliza (com T_antes = C_antes, HT = Abbott) | K11 (executado); Abbott (1925) | O Gemini erra a base da Q2; a consolidação não marcou |
| O3 | O PED:124 manda Abbott sem leitura antes; o Gemini diz descartar; a consolidação não decide | K11: com partidas diferentes (20 × 5), Abbott dá 0 e HT 0,75 | Divergência D2 |
| O4 | O pacote descreveu o v3 com "revisitas de 3 dias perto do NC" (PG:3). O v3 só tem vistorias a cada 7 dias (e 21 quando falta uma). A revisita é do protocolo oficial (CL:89) | V2 (executado): 19.468 intervalos de 7 dias e 40 de 21, nenhum de 3 | O raciocínio do Gemini na Q6(c) partiu de um dado que o gerador não tem; GER-07 |
| O5 | O gerador nunca produz zero: piso de 0,05 no nível latente (ART:394) | V2 (executado): 0 zeros em 21.188 leituras; menor 0,19 | Os casos de zero da Q2 só se testam com fixture dirigida; GER-06 |
| O6 | Toda aplicação do gerador vem de leitura alta | V2 (executado): 1.528/1.528; 499 abaixo do NC (→ Δ 17/10-3) | Reaplicação informativa por construção (R3); seleção pela leitura ruidosa (regressão à média) a medir pelo oráculo (ORA-04) |
| O7 | Contraprova do Gemini na Q6 (casos completos × pior cenário) não avaliada | Lido (RG Q6) | Aproveitar como desenho de teste com limites do protocolo (R4) |
| O8 | Pontos do Gemini fora do sistema ou do escopo: validação "região X → região Y" (RG Q1) usa dados de outras fazendas, ou seja, dados de clientes e modelo regional, que é do proprietário (AGENTS §2; PED:145); referência "média histórica do mês" (RG Q4) pede ≥ 2 safras; metadados como bico (RG Q5) exigem digitação nova (PED:63) | Lido | Não entram no RX-0 nem no RX-4 sem decisão própria |
| O9 | Agregação de vários controles: mediana das razões no v3 (ART:631) × razão de médias | Lido | Pendência do EST-3a; o RX-0 exporta a razão de cada controle |

**Escolha do Gemini por pergunta** (resumo meu do RG, para auditoria; não é a resposta dele):

| Pergunta | Escolha |
|---|---|
| Q1 | Nenhuma das três opções: sem selos, só coocorrência |
| Q2 | HT sem ε, sem Abbott sem leitura antes, variação descritiva |
| Q3 | A, com riscos competitivos depois |
| Q4 | Indisponível, sem número de portão |
| Q5 | A |
| Q6 | Sem imputação pela média, casos completos, sem percentual escolhido |

## 6. N5 executado (V3)

**Desenho.**
- O gate do v3 é replicado em D = 86 e confere com o `rxRisk` original (o script falha se divergir).
- A única troca é o avaliador das linhas de teste: o da 2ª leitura (v3; futuro na origem d1) passa a ser o da leitura de origem.
- 21 sementes, 4 alvos.

| Alvo | Avaliador no modelo | Linhas de teste com avaliador diferente | Brier mudou | Maior \|Δ Brier\| | Vence a persistência (v3 × origem) |
|---|---|---|---|---|---|
| Ácaro | 21/21 | 395/788 | 21/21 | 0,0095 | 19 × 19 |
| Mosca-branca | 21/21 | 435/880 | 19/21 | 0,0116 | 21 × 21 |
| Antracnose | 21/21 | 476/976 | 18/21 | 0,0043 | 18 × 18 |
| Cochonilha | 21/21 | 393/789 | 21/21 | 0,0066 | 21 × 21 |

**Leitura.**
- O vazamento existe: o avaliador sempre entra no modelo e o Brier muda.
- O dano é pequeno porque o gerador não planta efeito do avaliador. Por isso o teste do RX-0 (ADV-06) exige o cenário com viés plantado (GER-08); sem ele, o teste não tem poder.
- Isso fecha o "N5 segue leitura estática" do comentário 6227625864, sem mudar a classificação do N5.

## 7. Divergências materiais com o Codex

| # | Divergência | Posição do Codex (fonte) | Posição do Claude | Como resolver |
|---|---|---|---|---|
| D1 | Natureza da regra para C_antes = 0 | "Pode tornar a comparação operacional inadequada, que é motivo diferente" (CG:14) | Não identificação: E não depende do tratado (K2). Regra estrutural fixa, com nomes explícitos (O1); não é parâmetro do protocolo | Por reprodução: o Codex roda `q2_ht.mjs` (K2, K8) e aceita ou recusa a regra do EST-3a |
| D2 | Abbott sem leitura antes (PED:124) | Não adotar Abbott "só pelo tipo de variável" (6227548175, item 4); a consolidação não decide o caso sem leitura antes | Sem leitura antes → "sem comparação válida". Abbott só com partida igual garantida por desenho (faixa testemunha, F3b, fora do RX). É mudança do pedido e vai para a lista "o que mudamos e por quê" (PED:247) | Por fonte: Abbott (1925) pressupõe partida igual; K11 mostra o erro com partidas diferentes. O Codex registra a mudança no desenho final |
| D3 | Coocorrência no lugar dos selos | "Não tratá-la como consenso"; manter "insuficiente" no protótipo (CG:21) | Recusar a coocorrência: em manejo é a correlação crua proibida (PED:239; PED:32), em clima mantém o confundimento da época. "Insuficiente" (PED:136) até o RX-2 passar | Por fonte (PED:32, :136, :239). O Codex decide se registra a recusa ou só a não adoção |
| D4 | Aplicação depois da origem na camada 4 | "Censura por tratamento não elimina viés informativo" (6227548175, item 5); "risco competitivo ou desfecho composto são alternativas a avaliar" (CG:15) | Proposta para o EST-4: desfecho composto ("precisou de ação": leitura ≥ NC ou aplicação com motivo "gatilho MIP" até t0 + h); com outro motivo, política de tratamento com rótulo e sensibilidade; sem motivo, contado à parte. O RX-0 exporta as variantes, então nada bloqueia agora | Por método, no contrato do RX-4. O Codex aceita, ajusta ou recusa a estratégia primária; o RX-0 não depende dela (ADV-04) |

**Não são divergência** (complementos que o Codex pode aceitar sem disputa):
- mundo nulo como controle negativo principal (R8);
- uso operacional por camada (R4);
- HT como DiD em log (R7) → Δ 17/10-6;
- "efeito forte" definido por enumeração congelada no manifesto (P4 do RX-0, que atende ao item 3 do 6227548175).

## 8. Fontes externas

**Verificadas no PubMed em 17/10/2026** (título, autores, ano e DOI conferidos):
- Abbott, W. S. (1925). *A method of computing the effectiveness of an insecticide*. Reimpressão de 1987 indexada no PubMed (J. Am. Mosq. Control Assoc. 3:302-303, PMID 3333059, sem DOI). O original é J. Econ. Entomol. 18:265-267, citado de memória (CL:267).
- Morris, T. P., White, I. R. e Crowther, M. J. (2019). *Using simulation studies to evaluate statistical methods*. Stat. Med. 38:2074-2102. [DOI](https://doi.org/10.1002/sim.8086). É a estrutura ADEMP (objetivos, mecanismo gerador, estimandos, métodos, medidas de desempenho), base do gabarito do RX-0.
- Phipson, B. e Smyth, G. K. (2010). *Permutation P-values should never be zero: calculating exact P-values when permutations are randomly drawn*. Stat. Appl. Genet. Mol. Biol. 9, art. 39. [DOI](https://doi.org/10.2202/1544-6115.1585).
- Lipsitch, M., Tchetgen Tchetgen, E. e Cohen, T. (2010). *Negative controls: a tool for detecting confounding and bias in observational studies*. Epidemiology 21:383-388. [DOI](https://doi.org/10.1097/EDE.0b013e3181d61eeb).

**Sem verificação nesta sessão:**
- ICH E9(R1), *Addendum on estimands and sensitivity analysis in clinical trials* (2019): ~~fora do PubMed; título e ano de memória, com certeza; não conferido em fonte~~ → Δ 17/10-5: fonte oficial localizada pelo Codex.
- Henderson e Tilton (1955), Owen (2007) e Turnbull (1976): como na CL:267, citados de memória, volume e página a conferir. A descrição "HT para populações não uniformes" é **fonte pendente**; a equivalência com o Abbott está provada pela aritmética (K11), sem depender dela.

## 9. Verificação e segredos

**Executado em 17/10, Node v22.22.0:** `bash reproducao/gemini/rodar.sh /tmp/v3.html <saída>`.
- Saída 0.
- `q2_ht.txt` igual ao versionado; `v3_verificacoes.json` igual ao versionado, fora a versão do Node e o nome do arquivo.
- Cerca de 7 s.

**Limites.**
- O v3 só é usado por extração do motor num `vm` isolado, com um gancho de semente igual ao do confronto.
- Não abri a tela. Não testei o RX-0, que está só especificado.
- O N5 mede só a troca do avaliador, com o resto do gate como no v3: clima realizado e população condicionada.

**Gitleaks 8.30.1** (config `/home/user/Safrion-Software-/.gitleaks.toml`, `--redact`), antes do commit: `gitleaks dir docs/integracao/V73/RAIOX-ALVO`, ~784 KB, sem achados. A varredura `git` do intervalo b9898643..HEAD com este commit vai no recibo ao coordenador.

## 10. Δ 17/10 · retorno do Codex (6227947437 e 6227991541)

Lido nos comentários, sem reinterpretar. Nada aqui é aprovação integral do RX-0, e o Codex mantém a PR 88 como prioridade.

**Δ 17/10-1 · Decisões do Codex sobre as divergências da §7**

| # | Decisão do Codex | Efeito nesta revisão |
|---|---|---|
| D1 | Aceita: C_antes = 0 é inelegibilidade estrutural do fator de crescimento, mesmo com a forma de produto dando 100 %; usar nomes explícitos. Corrigiu a redação "pode ser operacionalmente inadequado" | Fechada |
| D2 | Aceita: no fluxo observacional atual, sem leitura antes → sem comparação válida; sem fallback para Abbott | Fechada. A mudança do PED:124 vai para "o que mudamos e por quê" (PED:247) no registro dele |
| D3 | Aceita: recusa a coocorrência crua como substituta dos selos ou do efeito; mantém "Insuficiente" | Fechada |
| D4 | Fica como alternativa exportada. Não adotar "precisou de ação" como verdade agronômica só porque houve aplicação; separar ação registrada de cruzamento observado | Aplicado no contrato (rx0 Δ 17/10-7) |

**Δ 17/10-2 · Reproduções do Codex** (deixam de ser só relato do Claude)
- K1–K11: iguais ao bruto, normalizado só o fim de linha (6227947437).
- V1–V3 e N5: iguais ao bruto, fora a versão do Node e o nome do arquivo; Node 24.19, saída 0 (6227991541). O N5 confere: 79/84, máximo 0,0116, sem mudar vitória.
- O Codex corrigiu a descrição do pacote: a revisita de 3 dias é proposta ou protocolo, não comportamento do v3. O O4 fica resolvido.

**Δ 17/10-3 · Precisão sobre o V2** (R3 e O6). O V2 só verifica que cada aplicação tem uma leitura anterior ≥ gatilho × NC. O vínculo causal "esta leitura disparou esta aplicação" vem da leitura do gerador (ART:398; lido), não da busca retrospectiva, como o Codex apontou.

**Δ 17/10-4 · Verificação dos ajustes** (executado). Novo `reproducao/gemini/delta_1710.mjs` → `delta_1710.txt`:
- bloco A: ramos do ADV-01;
- bloco B: cruzamentos do latente para o ORA-05;
- bloco C: domínio do K10.
O `rodar.sh` passou a conferir também esse arquivo. Os brutos anteriores não mudaram.

**Δ 17/10-5 · ICH E9(R1).** Referência oficial localizada pelo Codex: *ICH E9(R1) Addendum on estimands and sensitivity analysis in clinical trials to the guideline on statistical principles for clinical trials*, Step 4, 2019, https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf. É framework metodológico, não norma agro.

**Δ 17/10-6 · Alcance do K10** (R7, §1, §7).
- A identidade ln(1 − E) = [ln T_depois − ln T_antes] − [ln C_depois − ln C_antes] foi demonstrada só para valores positivos (K10). Com algum zero, os dois lados saem infinitos (`delta_1710.txt`, bloco C).
- É álgebra de um par antes/depois. Não prova identificação causal, nem tendência paralela, nem equivalência a qualquer estimador DiD (vários períodos, regressão, escala de nível, adoção escalonada).
- O que fica da R7: pedir "DiD" não dispensa os pressupostos do HT, e o teste de pré-tendência só pode reprovar.

**Δ 17/10-7 · Contrato.** Os seis ajustes pedidos estão em `rx0-contrato-proposta.md` §12 (Δ 17/10-1 a 17/10-10):
1. existência conhecida e versão retroativa do NC;
2. população própria do seguimento;
3. ramos do ADV-01;
4. chaves com a identidade de origem;
5. ORA-05 e cobertura;
6. alcance do K10.
Também estão lá o D4 como alternativa exportada e a dependência do EX-42.

**Verificação do Δ** (executado, Node v22.22.0): `bash reproducao/gemini/rodar.sh /tmp/v3.html <saída>` → saída 0. `q2_ht.txt`, `delta_1710.txt` e `v3_verificacoes.json` iguais aos versionados. Gitleaks: no recibo do commit.
