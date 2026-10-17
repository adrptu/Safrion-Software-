# RX-0 · contrato de dados e gabarito do Raio-X do alvo (proposta mínima do Claude)

Versão 1 · 17/10/2026 · autor Claude · revisor e registro: Codex.
**Versão 1.1 · Δ 17/10**, depois do retorno do Codex (comentários 6227947437 e 6227991541 do PR #47): os seis ajustes pedidos e mais quatro pontos estão na §12. O texto da versão 1 fica preservado; onde ele mudou, há um ponteiro "→ Δ 17/10-n". **Dependência:** o RX-0 só vira executável depois do EX-42 e de contrato, base e arquivos delimitados (Δ 17/10-9).
- **Estado: especificado.** Nada deste contrato foi implementado ou testado. As únicas execuções citadas estão em `reproducao/gemini/` (rótulos K e V) e no confronto (R-Cn).
- Escrito para o Codex registrar sem reinterpretar: cada regra tem ID, cada teste tem entrada mínima e saída esperada, e cada número sem fonte está marcado como pendente.
- O RX-0 cobre só dados e gabarito: nenhum modelo, risco, nível de evidência ou tela.

## 0. Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: RX-0 (Fatia 1 do Codex) · tabela de análise "como era em D" e gabarito com verdade plantada, para que RX-1 a RX-4 sejam testados contra um oráculo · QA e agrônomo/RT
Requisitos do PRD e fora do escopo: PED §2, §3 "Regras de honestidade", §6; EX-42 §2, §6, §8; PRD:512, :6304 · fora: estimador, nível de evidência, risco, tela, job real, fonte real de clima ou previsão (P1 do proprietário)
Autor / revisor / integrador: a definir pelo Codex no registro (proposta: Claude autor, Codex revisor e integrador; teto de 3 frentes, depois do EX-42 F1a, F1d e F1b)
Base (commit ou hashes) / arquivos sob responsabilidade: v3 529adf7; confronto 45b097f; consolidação bff2e0e; EX-42 b989864 · arquivos a fixar no registro (sugestão da CL:201: gen37/raiox_gabarito.py e gen37/raiox_unit.js, novos; dados_mip.py só leitura)
Aceite e comando de verificação: §9; comando a fixar quando houver autoria
Estado / impedimento / próximo passo: proposta · depende do registro do Codex e do EX-42 F1a (contrato comum de observações), que o RX-0 estende sem reimplementar (CX:34)
```

→ Δ 17/10-9: dependência do EX-42 e de contrato, base e arquivos delimitados antes de virar executável.

## 1. Termos

| Termo | Definição |
|---|---|
| t_evento | Instante em que o fato aconteceu: leitura, execução, dia do clima, aquisição da cena |
| t_disp | Instante em que o servidor passou a conhecer aquela **versão** do fato: sincronização, confirmação do apontamento, ingestão, processamento, emissão e recebimento da previsão |
| D | Data de corte de um cálculo, como instante. Na tela por dia, D = 23:59:59,999 do dia, no fuso da fazenda |
| t0 | Origem de uma unidade analítica: só existe na camada 4 e na definição de população prospectiva |
| Versão de parâmetros | Conjunto versionado de janelas, faixas, pisos e tolerâncias. Cada parâmetro tem origem "adotado pelo RT", "demonstrativo" ou "pendente" |
| Latente | Nível verdadeiro x(t) do gerador, sem erro de medição. Só existe no pacote do gabarito |

## 2. Unidade de observação e chave (RX0-U)

São fatos, não janelas (CL:209). As janelas são calculadas a partir dos fatos.

| ID | Unidade | Chave | Campos obrigatórios |
|---|---|---|---|
| U1 | Leitura de vistoria | (org, fazenda, talhão/cultivo, alvo, leitura_id, versão) | t_evento com hora; t_disp; valor na unidade do protocolo **ou** ausente com motivo; unidade; versão do protocolo AG-05; pontos previstos e válidos; estado (completa, parcial, recoleta); avaliador (pseudônimo no sintético) |
| U2 | Evento de manejo realizado (aplicação, adubação, irrigação, operação) | (org, fazenda, talhão, evento_id, versão) | t_início e t_fim da execução; t_disp; estado (confirmado completo, parcial, pendente, cancelado; EX-42:36); produto, ingrediente ativo, dose, área, calda e equipamento realizados; alvo(s); motivo (gatilho MIP deste alvo, calendário, campanha, outro alvo, desconhecido) |
| U3 | Série ambiental (clima diário ou horário, chuva medida, cena de satélite) | (fonte, estação ou talhão, período, variável, versão) | valor ou ausente com motivo; t_disp; qualidade |
| U4 | Previsão emitida | (fonte, t_emissão, t_alvo, variável, local) | valor; t_disp ≥ t_emissão |
| U5 | Par de crescimento (camadas 1 e 2) | (talhão, alvo, leitura_1, leitura_2, D, versão de parâmetros, versão do contrato) | ids e versões das fontes usadas; exporta também a leitura anterior a leitura_1, se existir, para teste de pré-tendência (R7) |
| U6 | Episódio de aplicação (camada 3) | (aplicação_id, alvo, leitura_antes, leitura_depois, D, versões) | candidatos a controle, cada um com o motivo de inclusão ou exclusão e a razão C_depois ÷ C_antes |
| U7 | Origem de previsão (camada 4) | (talhão, alvo, t0, h, versões) | membros e motivos definidos só com fatos de t_disp ≤ t0 |

**Regra:** toda unidade derivada carrega a lista de (id, versão) das fontes usadas, ou seja, a proveniência (X-25, X-31). Mudar qualquer versão gera chave nova; o recálculo é idempotente (CL:209). → Δ 17/10-4: chaves com organização, fazenda, cultivo e safra; U4 com revisão da emissão.

## 3. Tempo de disponibilidade (RX0-T)

**Regras.**
- **T1 · Corte em D** ("só entra o que estava disponível em D"). Um fato entra num cálculo com corte D só se t_evento ≤ D **e** t_disp ≤ D. Entre as versões do mesmo fato, vale a de maior t_disp ≤ D. → Δ 17/10-1: a existência do fato também depende de t_disp.
  - Única exceção ao t_evento: a previsão (U4). Ela entra com t_emissão ≤ D e t_disp ≤ D, sempre rotulada "previsão emitida em …".
- **T2 · Origem t0 (camada 4).**
  - Variáveis e pertença à população só com t_disp ≤ t0 e t_evento ≤ t0, mais previsões emitidas e recebidas até t0.
  - Fato posterior a t0 só pode ser desfecho ou evento intercorrente, nunca critério de entrada ou variável (N1, N2, N3, N5).
- **T3 · Camadas 1 e 2.** A exposição do par termina no instante da 2ª leitura: t_evento ≤ t(leitura_2) (PED:213). T1 vale para tudo.
- **T4 · Camada 3.** Leituras do tratado e dos controles só com T1 (X-05). A elegibilidade do controle é avaliada com os fatos disponíveis em D.
  - Exigir "controle sem aplicação até C_depois" condiciona no futuro em relação ao instante da aplicação. Como a aplicação é disparada pelo nível (V2), isso pode enviesar o fator do controle.
  - O RX-0 não proíbe essa exigência (sem ela não há controle). Ele exporta o motivo de exclusão de cada candidato, e o oráculo mede o viés (ORA-04). Rótulo: especificado, não medido.
- **T5 · Revisão retroativa.** Uma correção com t_disp > D não muda o resultado de D. Recalcular D em qualquer data devolve o mesmo resultado (ADV-07).
- **T6 · Parâmetros e tabelas versionadas.**
  - Usa-se a versão publicada até D (ou até t0).
  - Exceção: o NC que classifica uma leitura é o da versão válida no t_evento da leitura (EX-42:30). → Δ 17/10-1: só entre as versões publicadas até o corte.

**Quando cada variável fica conhecida.** Valores de atraso no gerador: GER-09.

| ID | Variável | t_evento | Fica conhecida em (t_disp) | Camadas 1–2 (par) | Camada 3 (episódio) | Camada 4 (origem t0) |
|---|---|---|---|---|---|---|
| V-01 | Nível, pontos, estado da leitura | instante da leitura | recebimento no servidor (o app pode estar sem rede) | as duas leituras, T1 | antes e depois, T1 | só leituras até t0; a futura é só desfecho |
| V-02 | Avaliador da leitura | idem | idem | das duas leituras; "mudou de avaliador" | idem | só de leituras até t0 (N5) |
| V-03 | NC, unidade e tipo do alvo | — | publicação da versão AG-05 | versão válida no t_evento de cada leitura | idem | idem |
| V-04 | Parâmetros de análise | — | publicação da versão | versão até D | idem | versão até t0 |
| V-05 | Aplicação realizada | instante da execução | confirmação do apontamento (EX-38) | exclui o par se o efeito residual cobre o intervalo | define o episódio; interferência | só realizadas até t0; programadas (O.S. liberada até t0) entram só rotuladas "programado" (N2) |
| V-06 | Motivo da aplicação | criação da O.S. | criação | — | exportado | até t0 |
| V-07 | Grupo IRAC/FRAC | — | edição publicada da tabela | — | versão até D | versão até t0 |
| V-08 | Posição na sequência do grupo | da aplicação | da última aplicação contada | — | só aplicações até a do episódio | até t0 |
| V-09 | Irrigação realizada | dia ou instante | leitura ou apontamento | janela até t(leitura_2) | — | até t0 (N2) |
| V-10 | Adubação ou fertirrigação realizada | instante | apontamento | janela até t(leitura_2) | — | até t0 (N2) |
| V-11 | Clima diário (Tmáx, Tmín, UR, chuva, vento) | dia | ingestão, nunca antes do fim do dia | janela até t(leitura_2) | condição no dia da aplicação | dias até t0; depois de t0, só previsão emitida até t0 (N1) |
| V-12 | Clima horário (horas UR ≥ 90 %, DPV) | hora | ingestão | idem | condição na hora da aplicação | idem |
| V-13 | Previsão | t_alvo | recebimento (≥ t_emissão) | não usa | não usa | só emitida e recebida até t0 |
| V-14 | Cena de satélite (NDVI, NDMI) | aquisição | processamento | aquisição até t(leitura_1); estado da lavoura, fora do modelo (CL:30) | — | até t0 |
| V-15 | Estádio ou fase | data da mudança | registro | versão válida em t(leitura_1) | idem no tratado e nos controles | até t0 |
| V-16 | Desfecho da camada 4 | leitura em (t0, t0 + h] | t_disp dessa leitura | — | — | só como rótulo na avaliação |

## 4. Ausência, zero, vistoria parcial e avaliador (RX0-A)

- **A1 · Três estados.** Cada valor é **observado** (número, inclusive 0), **ausente** (com motivo: sem vistoria, falha da estação, nuvem, não sincronizado) ou **inelegível** (existe, mas não serve: parcial, unidade ou protocolo incompatível, sem hora no dia da aplicação). Ausente nunca vira 0 nem média (PED:139, :242; EX-42:30).
- **A2 · Janela.**
  - Exporta {soma ou média dos dias com dado, dias com dado, dias da janela}.
  - Nunca escala pela fração de dias (o `v * 7 / n` do ART:529) nem imputa (o `impute` do ART:539).
  - O mínimo de cobertura é parâmetro pendente (Q6a) e é aplicado pela camada que consome, que declara o valor.
- **A3 · Falta por uso** (R4 da revisão).
  - Camada 1: casos disponíveis por variável, com n por variável.
  - Camada 2: casos completos no conjunto declarado, com a contagem e o motivo das exclusões.
  - A sensibilidade ao mecanismo de falta é aceite do RX-2.
- **A4 · Vistoria parcial.**
  - Estado "parcial (válidos/previstos)", inelegível como extremo de par enquanto não houver fração mínima adotada (pendente).
  - Recoleta é leitura própria, com seu instante. Nada se soma em silêncio (PED:71).
- **A5 · Avaliador.** Toda leitura carrega o avaliador. Os pares (camadas 1 a 3) exportam o avaliador das duas leituras e "mudou de avaliador" (CL:92). A camada 4 só vê avaliadores de leituras até t0 (N5; V3).
- **A6 · Mesmo dia.** Sem hora ou ordem confiável, a leitura do dia da aplicação é inelegível como antes ou depois (EX-42:38).
- **A7 · Zero.**
  - 0 é observação válida.
  - Nos papéis de divisor do EST-3a vira "sem comparação válida" com motivo (K1–K5).
  - y2 = 0 no par deixa r indefinido. O RX-0 marca o par; o tratamento (ε declarado ou classe "zerou") é pendente (Q6b). Nunca há ε silencioso (X-09).

## 5. Versões (RX0-V)

- **V1.** Toda unidade derivada e todo pacote do gabarito carregam:
  - versão do contrato RX-0;
  - versão do protocolo AG-05 por cultura e alvo: id, número, data de publicação, fonte e situação "adotado pelo RT" ou "demonstrativo";
  - versão de parâmetros, com a origem de cada parâmetro;
  - edição da tabela IRAC/FRAC;
  - versão do gerador (commit e hash da configuração);
  - semente;
  - hash do conjunto de entrada.
- **V2.** Protocolo demonstrativo só no gerador e sempre rotulado (EX-42:38). O RX-0 não adota parâmetro agronômico (PRD:512).
- **V3.** NC para classificar uma leitura: versão válida no t_evento (T6). → Δ 17/10-1.
- **V4.** Mudou a unidade entre as duas leituras do par → par "incompatível" (ADV-19).

## 6. Estimandos das camadas que vêm depois (RX0-EST)

Cada estimando segue os atributos do ICH E9(R1) (→ Δ 17/10-10): pergunta, população, variável, eventos intercorrentes com estratégia, sumário e o que o oráculo exporta. O RX-0 só os fixa, para que o gabarito exporte a verdade de cada um. Nenhum estimador é escolhido aqui.

### EST-1 · Associação (camada 1; Q1; X-02, X-13, X-15)

| Atributo | Definição |
|---|---|
| Pergunta | Entre os pares de leituras do alvo no recorte (fazenda, safra), a taxa de crescimento semanal é maior ou menor quando a condição X (definição, limiar e janela da versão de parâmetros) esteve presente, comparando pares com o mesmo nível de partida e estádio? É associação, não efeito ("associado a aumento ou redução", X-15) |
| População P-PAR(D) | Pares de leituras seguidas do mesmo talhão e alvo, as duas completas e com T1. Δt dentro da faixa da versão (pendente; a do v3 é 5–10 dias). y1 ≥ piso da versão (declarado: "mede crescimento de população instalada", CL:90). Nenhuma aplicação contra o alvo com efeito residual no intervalo (resíduo do protocolo, CL:93). X com dado conforme A2. Uma população por variável (A3) |
| Variável | r = ln(y2 ÷ y1) × 7 ÷ Δt, por semana; y2 = 0 conforme A7 |
| Contraste | Δ = média de r com X presente − média de r com X ausente, no mesmo nível de partida e estádio |
| Intercorrentes | Aplicação no intervalo: critério de exclusão, contado (P2) |
| Sumário | exp(Δ) − 1 por semana, com n de pares, talhões e semanas distintos |
| Oráculo | θ(X) = média, nos pares expostos, de r_lat − r_lat^(−X) (ORA-02, ORA-03). Direção = sinal de θ; magnitude = θ e exp(θ) − 1. A diferença entre Δ e θ é o confundimento que o gabarito mede |

### EST-2 · Modelo explicativo (camada 2)

| Atributo | Definição |
|---|---|
| Pergunta | O contraste do EST-1 para cada variável declarada, mantidas as outras variáveis declaradas |
| População | P-PAR(D) com casos completos no conjunto declarado (A3) |
| Oráculo | O mesmo θ(X) do EST-1: efeito direto com o manejo congelado. Coeficiente de modelo é estimador, não estimando (PED:111) |

### EST-3a · Variação após a aplicação comparada com controles (camada 3; Q2; X-05, X-08, X-09)

| Atributo | Definição |
|---|---|
| Pergunta | Na aplicação contra o alvo no talhão T, quanto o fator de mudança do nível entre a leitura antes e a depois ficou abaixo do fator dos talhões-controle no mesmo intervalo? Nome na tela: "Variação observada após o manejo" (EX-42:40) |
| População P-EPI(D) | Aplicações realizadas e confirmadas (U2) com T1. Leitura antes completa e anterior à aplicação (A6). Leitura depois completa na janela "depois" da versão (pendente; EX-42:38). Sem outra aplicação contra o alvo no talhão entre as leituras: senão "interferência", sem resultado (EX-42:38) |
| Controles | Talhões sem aplicação contra o alvo desde t(C_antes) − resíduo até t(C_depois). Leituras completas dentro da tolerância da versão em torno das do tratado, todas com T1. Pareamento da versão (estádio; nível antes). **Sem fallback** (X-08). Número mínimo de controles distintos da versão (o v3 usa 2) |
| Variável | R = (T_depois ÷ T_antes) ÷ agregado(C_depois ÷ C_antes); E = 1 − R. A agregação está pendente: mediana das razões (ART:631) ou razão de médias. O RX-0 exporta a razão de cada controle |
| Elegibilidade estrutural (fixa, não parâmetro) | T_antes > 0; C_antes > 0 em cada controle; C_depois > 0 no agregado. Senão "sem comparação válida", com o 1º motivo nesta ordem: tratado zerado antes, controle zerado antes, controle zerado depois (K1–K5; divergência D1). T_depois = 0 é válido: E = 1, "zero observado depois". Sem ε. O piso de precisão do nível antes é parâmetro pendente, igual para tratado e controle (o v3 só aplica no controle: V1, ART:628) |
| Sem leitura antes | "Sem comparação válida" (divergência D2; o PED:124 fica como mudança registrada) |
| Intercorrentes | Outra aplicação no tratado ou no controle no intervalo: fora, com motivo |
| Sumário (RX-1) | Por grupo: mediana de E, com n de aplicações, n de talhões distintos e dispersão; sem ranking (EX-42:40) |
| Oráculo | E_true = 1 − x(t_depois) ÷ x^(−aplicação)(t_depois), latente, com o manejo posterior congelado (ORA-04). Exporta também a razão leitura ÷ latente da leitura antes, porque a aplicação é escolhida pela leitura ruidosa (V2) |

### EST-3b · Seguimento depois da aplicação (Q3; X-10; N4)

| Atributo | Definição |
|---|---|
| Pergunta | Depois da aplicação, o que as leituras seguintes mostraram em relação ao NC? Só descrição, sem estimador (EX-42:42) |
| População | P-EPI(D), sem exigir controle → Δ 17/10-2: P-SEG(D) |
| Estados (exclusivos, em ordem) | S6 NC incompatível → indisponível. S4 sem leitura depois. S2 1ª leitura depois ≥ NC: "retorno não demonstrado". S5 nova aplicação contra o alvo antes de qualquer leitura ≥ NC: "encerrado por nova aplicação em t" (o seguimento termina ali; nada é creditado à 1ª). S1 leitura < NC seguida de leitura ≥ NC: "retorno entre t_(k−1) e t_k", com a largura do intervalo, mesmo com lacuna. S3 abaixo do NC até a última leitura elegível: censura nessa leitura, não em D → Δ 17/10-2: janela W e nova ordem |
| Oráculo | 1º dia latente com x ≥ NC depois da aplicação (ORA-05), para conferir que o intervalo de S1 o contém → Δ 17/10-5 |

### EST-3c · Sequência do grupo (Q5)

| Atributo | Definição |
|---|---|
| Variável | Posição k = número de aplicações seguidas do mesmo grupo IRAC/FRAC contra o alvo no talhão, pela edição da tabela (V-07) |
| Sumário | Só a coluna "posição na sequência" com n por posição. Sem aviso nesta fase (Q5 A, aceita pelo Codex em 6227548175, item 5) |
| Oráculo | Fator plantado de cada aplicação (no v3, 0,7^k ou 0,93^rep: ART:385) |

### EST-4 · Risco em h dias (Q4; X-06, X-07; N1, N2, N3, N5)

| Atributo | Definição |
|---|---|
| Pergunta (proposta; divergência D4) | Na origem t0, entre os talhões elegíveis, qual a probabilidade de o alvo **precisar de ação** até t0 + h? "Precisar de ação" = alguma leitura completa em (t0, t0 + h] ≥ NC **ou** aplicação contra o alvo com motivo "gatilho MIP" em (t0, t0 + h]. h = 7; 14 só com contrato próprio (X-27) → Δ 17/10-7 |
| População P-ORI(t0) | Talhões cuja última leitura completa até t0 está abaixo do NC, com idade dentro da validade (7 dias MIP; EX-42:30, DEC-0910-13 b), sem efeito residual de aplicação contra o alvo em t0. Tudo decidido só com fatos até t0 (T2) |
| Intercorrentes | Aplicação com outro motivo (calendário, campanha, outro alvo): a unidade fica e o desfecho é observado como está (política de tratamento), com marca e sensibilidade. Motivo desconhecido: contado à parte. Nenhuma unidade sai da população em silêncio (N3) |
| Perda | Sem leitura em (t0, t0 + h] e sem aplicação: "sem desfecho", no denominador do relatório como perda |
| Variáveis | Só da coluna "Camada 4" da §3 |
| Exportado pelo RX-0 | Os três desfechos (composto, só leituras, marca do intercorrente com o motivo), para que o RX-4 escolha sem mudar o RX-0 → Δ 17/10-7 |
| Oráculo | Nenhum de probabilidade. O gerador exporta o desfecho realizado e se o latente cruzou o NC em (t0, t0 + h], para medir quanto a vistoria semanal esconde |
| Sumário (RX-4) | Brier e log-loss contra persistência 0/1 e nível + estádio, por horizonte, em origens posteriores ao treino; portão da Q4, pendente |

### População explícita (RX0-P)

- **P1.** Toda taxa publicada carrega numerador, denominador, população (ID e definição), sementes, regra, D e versões (X-04).
- **P2.** Identidade, por tipo de unidade e por D: candidatos = incluídos + soma dos excluídos por motivo.
- **P3.** Taxas de populações diferentes não se combinam nem se comparam sem rótulo.
- **P4. "Efeito forte plantado"** (X-03; 6227548175, item 3):
  - é uma lista enumerada no manifesto do gabarito (ORA-08), congelada com hash antes de qualquer execução do RX-2;
  - o oráculo mostra a magnitude de cada um;
  - quem achar que um "forte" é pequeno contesta antes do congelamento, não depois do resultado.
- **P5.** Ruído = variáveis com oráculo exatamente 0, listadas no manifesto. O denominador do falso positivo é fixado antes (X-04).

## 7. Gerador e oráculo

### Gerador (RX0-GER)

| ID | Requisito | Por quê |
|---|---|---|
| GER-01 | Réplicas independentes: cada semente sorteia o clima (dias de chuva, ondas de calor), os perfis de talhão e o ruído | O v3 fixa a chuva e as ondas de calor (ART:296, :313; CL:253) |
| GER-02 | Fluxos aleatórios separados por (fonte, talhão, alvo, dia): processo, medição, efeito da aplicação, decisão, avaliador | No v3, um único `r()` por talhão × alvo alimenta tudo (ART:374-397, lido). Tirar uma aplicação desloca todo o ruído seguinte, e o contrafactual deixa de ser comparável |
| GER-03 | 2 safras | Época separável do clima (X-13) |
| GER-04 | Cenário de campanha: todos os talhões tratados juntos | Provar o "sem comparação válida" (CL:125) |
| GER-05 | Sequências do mesmo grupo com casos por posição; produto de ação lenta | Q5; CL:121. O v3 tem 1 caso (CL:124) |
| GER-06 | Zeros verdadeiros e limite de detecção | V2: 0 zeros em 21.188 leituras; piso latente de 0,05 (ART:394) |
| GER-07 | Faltas de vistoria, parciais, recoletas, revisita de 3 dias perto do NC, leitura no dia da aplicação com e sem hora | V2: o v3 só tem intervalos de 7 e 21 dias; a revisita é do protocolo oficial (CL:89) |
| GER-08 | Avaliador em dois cenários: ruído (oráculo 0) e viés plantado | V3: sem viés, o teste do N5 não tem poder |
| GER-09 | Atrasos t_disp − t_evento por fonte (app sem rede, estação, satélite) e revisões retroativas | T1, T5. Os valores são do gerador, não do protocolo |
| GER-10 | Previsões arquivadas: emitidas por dia, com erro declarado, t_emissão e t_disp | N1 e Q4 sem fonte real (P1 do proprietário) |
| GER-11 | Regra de decisão exportada: leitura-gatilho e motivo (gatilho MIP, calendário, campanha, outro alvo) | V2: no v3, 100 % por gatilho, 33 % abaixo do NC (regressão à média, R3) |
| GER-12 | Manifesto dos mecanismos plantados: ID, variável, alvo, forma, parâmetro, cenário; lista de ruído | P4, P5 |
| GER-13 | Rótulo "dados sintéticos — gabarito", em cenário separado da base Lagoa Grande | C-15; EX-42:34 |
| GER-14 | Protocolo demonstrativo declarado (NC, janelas, limiares), com origem "demonstrativo" | EX-42:38; V2 |

### Oráculo (RX0-ORA)

| ID | Definição |
|---|---|
| ORA-01 | Série latente x(t) por talhão × alvo × dia, só no pacote do gabarito. Nunca na entrada da análise (ADV-10) |
| ORA-02 | Contrafactual por mecanismo m: os mesmos fluxos (GER-02), m desligado e as decisões congeladas (mesmas aplicações, nos mesmos dias) |
| ORA-03 | Por par (EST-1, EST-2): τ = r_lat − r_lat^(−m). Por população: média nos expostos, sinal, magnitude (log por semana e %) e n |
| ORA-04 | Por episódio (EST-3a): E_true = 1 − x(t_depois) ÷ x^(−aplicação)(t_depois); razão leitura ÷ latente da leitura antes |
| ORA-05 | Por episódio (EST-3b): 1º dia latente com x ≥ NC depois da aplicação → Δ 17/10-5 |
| ORA-06 | Por aplicação (EST-3c): fator plantado |
| ORA-07 | Mundo nulo por mecanismo: m desligado **sem** congelar as decisões. O oráculo de m é 0 por construção |
| ORA-08 | Manifesto: commit do gerador, hash da configuração, sementes, lista de "fortes" (P4) e de ruído (P5), data de congelamento |

## 8. Testes adversariais que o RX-0 tem de passar (RX0-ADV)

Todos os testes:
- NC 10 e dias inteiros, salvo indicação;
- "idêntico" significa a mesma saída serializada, byte a byte;
- cada teste nomeia a origem (X, E, N, Q, PED, EX-42).

### Vazamento do futuro

**ADV-01 · Controle lido depois de D** (X-05; R-C1)
- Entrada: tratado T com leitura d1 = 10, aplicação d2, leitura d10 = 5. Controles C1 e C2 com leituras d1 = 10 e d12 = 10. D = 10.
- Esperado:
  - episódio "sem comparação válida: controle sem leitura depois até D";
  - trocar só as leituras d12 dos controles para 30 deixa a saída de D = 10 idêntica;
  - com D = 12 e tolerância de pareamento da versão ≥ 2 dias, E = 0,5.
- → Δ 17/10-3: ramos explícitos e executados.

**ADV-02 · Clima realizado e previsão publicada depois da origem** (X-06; N1)
- Entrada: t0 = fim do dia 30, h = 7. Clima realizado dos dias 31 a 37 presente na base. Previsão P1 emitida e recebida em d30 18:00 para os dias 31 a 37, com Tmáx 30 °C. Previsão P2 emitida em d31 06:00. Variante: Tmáx realizado de d35 + 70 °C.
- Esperado:
  - as variáveis de t0 vêm de P1, e a variante sai idêntica;
  - sem P1: "sem previsão emitida até a origem", nunca P2 nem o realizado;
  - na tela com D = 58 (data passada), o "Próximos 7 dias" usa só previsão emitida até 58 ou fica indisponível.

**ADV-03 · Manejo depois da origem** (N2)
- Entrada: t0 = 72. Irrigação realizada de 70 mm em d75. Adubação realizada em d76. O.S. de irrigação liberada em d70 para d74.
- Esperado:
  - variáveis de t0 idênticas com e sem as realizações de d75 e d76;
  - a O.S. de d74 entra só como "programado", com rótulo.

**ADV-04 · Seleção que depende do futuro** (N3)
- Entrada: t0 = 40. Talhões A, B e C com última leitura em d38 abaixo do NC.
  - A: leitura d45 = 12.
  - B: aplicação contra o alvo (calendário) em d42 e leitura d45 = 2.
  - C: sem leitura até d47.
- Esperado:
  - P-ORI(40) = {A, B, C}, com denominador 3;
  - A: evento;
  - B: não evento, com a marca "aplicação depois da origem: calendário, d42";
  - C: "sem desfecho";
  - relatório: 3 = 2 com desfecho (1 com intercorrente) + 1 perda;
  - nenhuma exclusão silenciosa.

**ADV-05 · Seguimento: reaplicação, 1ª acima, lacuna, censura, sobreposição** (N4; X-10; EX-42:38, :42) → Δ 17/10-2: estados pela P-SEG e caso (g)
- Base de todos os casos: leitura antes em d1 = 12 e aplicação a1 em d2.
- Casos:
  - **(a)** d9 = 3, nova aplicação em d12, d16 = 11 → S5 "encerrado por nova aplicação em d12". Nunca "retorno entre d9 e d16".
  - **(b)** d9 = 11 → S2 "retorno não demonstrado".
  - **(c)** d9 = 3, sem leitura em d16, d23 = 12 → S1 "retorno entre d9 e d23", largura 14.
  - **(d)** d9 = 3, d16 = 4, D = 20 → S3 "abaixo do NC até d16" (censura em d16, não em d20).
  - **(e)** sem leitura depois de d2 até D → S4.
  - **(f)** outra aplicação de outro produto em d4, com leituras d1 e d9 → episódio "interferência". Nenhum resultado é atribuído a cada aplicação.

**ADV-06 · Avaliador da leitura futura** (N5; V3)
- Entrada: cenário com viés plantado (GER-08: o avaliador B lê × 1,5). t0 = 40. Última leitura em d38 pelo avaliador A; a próxima, em d45, pelo B.
- Esperado:
  - variáveis de t0 idênticas trocando o avaliador de d45 (A ↔ B);
  - "mudou de avaliador" só existe em pares fechados.

**ADV-07 · Revisão retroativa e sincronização tardia** (CX:44; T1, T5)
- Entrada: leitura L em d5 = 4, com t_disp d5, corrigida para 14 com t_disp d20. Leitura M em d8, sem rede, com t_disp d11.
- Esperado:
  - com D = 10: L = 4 e M ausente ("não sincronizada", não zero);
  - com D = 11: M presente;
  - com D = 25: L = 14;
  - recalcular D = 10 em qualquer data dá a mesma saída.
- → Δ 17/10-1: este "Esperado" foi substituído (M sem sinal conhecido não aparece em D = 10); ADV-07b novo.

**ADV-08 · Exposição depois da 2ª leitura do par** (PED:213; T3)
- Entrada: par (d7, d14 às 09:00). Chuva de 30 mm em d15. Irrigação em d14 às 18:00.
- Esperado: variáveis do par idênticas com e sem a chuva de d15 e a irrigação das 18:00.

**ADV-09 · Leitura no dia da aplicação** (A6; EX-42:38)
- Entrada: aplicação em d7 às 08:00. Leituras em d7: (a) sem hora; (b) às 07:00; (c) às 10:00.
- Esperado:
  - (a) inelegível como antes, motivo "sem hora no dia da aplicação";
  - (b) elegível como antes;
  - (c) inelegível como antes.

**ADV-10 · Verdade fora da análise** (ORA-01)
- Entrada: pacote do gabarito com x_latente e o oráculo.
- Esperado:
  - o esquema da tabela de análise não tem nenhum campo latente ou do oráculo;
  - a camada de análise falha ao pedir um deles;
  - só o avaliador do gabarito lê o oráculo.

### Ausência

**ADV-11 · Ausente ≠ zero** (PED:139; ART:529, :539)
- Entrada:
  - chuva da janela de 7 dias: 0, 0, ausente, ausente, ausente, 12, 0 mm;
  - sem leitura na semana 3;
  - leitura d21 = 0;
  - NDVI sem cena válida (nuvem).
- Esperado:
  - janela {soma 12 mm, 4 dias com dado, 7 dias}, nunca 21 mm (12 × 7 ÷ 4);
  - sem par na semana 3; o par semana 2 → semana 4 tem Δt = 14 e segue a faixa da versão;
  - d21 = 0 é observado e entra;
  - NDVI ausente, "nuvem", nunca média.

**ADV-12 · Vistoria parcial** (A4; PED:71)
- Entrada: leitura com 6 de 10 pontos válidos; recoleta 2 dias depois com 10 de 10.
- Esperado:
  - parcial "6/10", inelegível como extremo de par, contada nas exclusões;
  - a recoleta é leitura própria;
  - nada é somado.

**ADV-13 · Falta por uso** (A3; R4)
- Entrada: 10 pares; irrigação ausente em 2; clima completo.
- Esperado:
  - clima: 10 pares;
  - irrigação: 8 pares, 2 excluídos com motivo "irrigação ausente";
  - modelo com clima e irrigação: 8 casos completos, com a contagem;
  - nada imputado.

### Controle negativo, mundo nulo e permutação

**ADV-14 · Controle negativo desalinhado** (X-14; E2; R-C6; Lipsitch e outros, 2010)
- Entrada: clima semanal verdadeiro X = 1, 2, 3, 4, 5, 6. Candidato N1 = X uma semana antes: 0, 1, 2, 3, 4, 5. Candidato N2 = 4, 1, 6, 2, 5, 3.
- Esperado:
  - o RX-0 exporta o ρ de Spearman com X: N1 = 1,00; N2 = 0,0857 (soma dos quadrados das diferenças de posto = 32);
  - sem limite declarado, os dois são "não utilizáveis como controle negativo: limite de desalinhamento não declarado";
  - com limite L declarado: utilizável só se |ρ| ≤ L; N1 nunca;
  - rótulo do resultado: "variável desalinhada", nunca "falso positivo".
- Caso real: deslocamento de 49 dias, |ρ| até 0,76 (R-C6).

**ADV-15 · Mundo nulo e ruído** (ORA-07; P5)
- Entrada: o mecanismo "quente e seco → ácaro" desligado, com a mesma semente.
- Esperado:
  - oráculo do mecanismo = 0 em todas as unidades;
  - ruído de medição por (talhão, alvo, dia) idêntico ao do mundo completo (GER-02);
  - variáveis de ruído do manifesto com oráculo 0 nos dois mundos.

**ADV-16 · Permutação** (E1; X-12; R8; Phipson e Smyth, 2010)
- Entrada: 2 talhões × 3 semanas; clima semanal da fazenda X = 1, 2, 3, igual nos dois talhões; unidade de troca declarada = semana; K = 5; semente s.
- Esperado:
  - em cada permutação, X é igual nos dois talhões da mesma semana;
  - o multiconjunto {1, 2, 3} se mantém;
  - y, chaves e ausências não mudam;
  - a mesma semente dá as mesmas permutações;
  - o pacote declara H0 ("sem associação entre X semanal e y, dada a estrutura preservada") e a unidade;
  - o p da camada que consome é (1 + k) ÷ (1 + K); uma permutação isolada nunca é relatada como diagnóstico.

### População explícita

**ADV-17 · Taxas com população** (P1, P3; X-04)
- Entrada: 4/480 ("20 réplicas, ruído, F/M") e 44/504 ("original + 20, ruído, qualquer nível").
- Esperado:
  - as duas saem lado a lado, com numerador, denominador, população, sementes e regra;
  - pedir 4 ÷ 504 falha com o motivo "populações diferentes".

**ADV-18 · Contagem de exclusões e campanha** (P2; X-08; CL:125)
- Entrada: 5 talhões tratados contra o alvo no mesmo dia e nenhum outro talhão com o alvo na janela.
- Esperado:
  - 5 episódios "sem comparação válida: sem controle elegível", sem fallback;
  - identidade 5 = 0 incluídos + 5 excluídos ("sem controle").

**ADV-19 · Protocolo e unidade mudados** (CX:44; T6; V4) → Δ 17/10-1: cada versão publicada no início da vigência
- Entrada:
  - NC 15 na versão 1 (até d39) e 10 na versão 2 (desde d40); leituras d35 = 12 e d42 = 12;
  - na versão 3 (desde d50), a unidade muda de "% de folhas" para "ácaros por folha"; leituras d49 e d56.
- Esperado:
  - d35 abaixo do NC (12 < 15) e d42 acima (12 ≥ 10);
  - par (d49, d56) "incompatível: unidade mudou";
  - as chaves levam a versão.

### Vetores fixados para as camadas seguintes

**ADV-20 · Divisores do HT** (EST-3a; K1–K11; V1)
- Entrada e saída esperada no RX-1:
  - T 10 → 5, C 10 → 10: E = 0,5;
  - T 10 → 0, C 10 → 10: E = 1, "zero observado depois";
  - T 0 → 2: "tratado zerado antes";
  - C 0 → 10: "controle zerado antes", nunca 100 %;
  - C 10 → 0: "controle zerado depois";
  - C 0 → 0: "controle zerado antes".
- Os quatro casos com zero em papel de divisor, na forma de razão, nunca saem com número. O v3 dá −4; nulo; −10; nulo (V1).

**ADV-21 · Oráculo mínimo e reprodutibilidade** (ORA-02 a ORA-04; GER-01, GER-02)
- Entrada: gerador em modo fixture, sem ruído, sem imigração e sem resíduo.
  - (a) Crescimento diário 1 e aplicação com eficácia 0,8 em d2; leituras d1 e d9.
  - (b) Crescimento base 1 por dia e um dia "quente e seco" com multiplicador 1,05 dentro do par (d1, d8).
- Esperado:
  - (a) E_true = 0,8 exato;
  - (b) τ = ln(1,05) = 0,04879 por semana (5 %);
  - mesma semente e versão → saída idêntica;
  - outra semente → outro clima.
- → Δ 17/10-5: caso (c) novo, do ORA-05.

## 9. Aceite do RX-0 (especificado)

1. ADV-01 a ADV-21 passam.
2. Cada ADV tem contraprova: a versão com o defeito correspondente (por exemplo, o `rxHT` do v3 para o ADV-01 e o ADV-20, o `v * 7 / n` para o ADV-11) **reprova**. Isso segue a regra "corrigir não é afrouxar" (AGENTS §3.6).
3. O gabarito tem ≥ 20 sementes independentes (GER-01) e o manifesto congelado (ORA-08), com a lista de "fortes" e de ruído.
4. P2 vale para toda data D da linha do tempo, nas três unidades derivadas.
5. Nenhum estimador, nível de evidência, risco ou texto de tela é entregue no RX-0.

→ Δ 17/10-8: o aceite inclui ADV-07b, ADV-21(c) e ADV-22.

## 10. Pendências (nenhuma bloqueia o registro)

| Pendência | Dono | Até lá |
|---|---|---|
| Faixa de Δt dos pares, piso de nível, resíduo, janela "depois", tolerância e critérios de pareamento, número mínimo de controles, fração mínima de pontos | Protocolo AG-05 e RT (PRD:512) | "Demonstrativo" no gerador; "pendente" no contrato |
| Cobertura mínima da janela (Q6a), ε ou classe "zerou" (Q6b), agregação dos controles, limite de desalinhamento (ADV-14) | Claude e Codex, com fonte (DEC-0910-03) | O RX-0 exporta os insumos; a camada que consome declara o valor |
| Estratégia do intercorrente na camada 4 (D4) | Codex registra, com o contrato do RX-4 | O RX-0 exporta as três variantes |
| Lista de "efeitos fortes" (P4) | Claude e Codex, antes do RX-2 | Sem lista, o RX-2 não roda o aceite de 100 % |
| Fonte real de previsão com arquivo (P1) | Proprietário (custo e contrato) | GER-10 sintético |

## 11. Rastreabilidade

| ID já usado | Onde entra no RX-0 |
|---|---|
| X-03, X-04 | P1 a P5; ADV-17 |
| X-05 | T4; ADV-01 |
| X-06, X-07 | T2; EST-4; ADV-02 |
| X-08 | EST-3a (sem fallback); ADV-18 |
| X-09 | A7; EST-3a (sem ε); ADV-20 |
| X-10 | EST-3b; ADV-05 |
| X-12, E1 | ADV-16 |
| X-13 | GER-03 |
| X-14, E2 | ADV-14 |
| X-15 | EST-1 (pergunta) |
| X-25, X-31 | U5 a U7 (proveniência e chave) |
| N1 | T2; V-11; ADV-02 |
| N2 | T2; V-05, V-09, V-10; ADV-03 |
| N3 | T2; EST-4; ADV-04 |
| N4 | EST-3b S5; ADV-05(a) |
| N5 | A5; V-02; GER-08; ADV-06 |
| Q1 | EST-1, EST-2 |
| Q2 | EST-3a; ADV-20 |
| Q3 | EST-3b |
| Q4 | EST-4 |
| Q5 | EST-3c |
| Q6 | A2, A3, A7; GER-07 |

## 12. Δ 17/10 · ajustes depois do retorno do Codex (6227947437 e 6227991541)

**Decisões do Codex** (lidas, sem reinterpretar):
- D1, D2 e D3 aceitas;
- D4 fica como alternativa exportada;
- V1–V3, N5 e K1–K11 reproduzidos por ele;
- nenhuma aprovação integral do RX-0; a PR 88 segue prioridade.

Os ajustes abaixo substituem os trechos apontados por "→ Δ 17/10-n". A verificação aritmética está em `reproducao/gemini/delta_1710.txt` (executado).

### Δ 17/10-1 · Existência conhecida e versão retroativa (completa T1 e T6; substitui o "Esperado" do ADV-07)

- **T1a.** A existência de um fato também tem t_disp. Para o corte D, um fato sem nenhuma versão com t_disp ≤ D **não existe**: não aparece como linha, nem como "não sincronizada", nem com outro motivo.
- **T1b.** O motivo "não sincronizada" só aparece em D se, até D, havia um sinal conhecido da própria leitura, como um aviso de pendência enviado pelo aparelho com t_disp ≤ D.
  - Sem sinal, mas com expectativa conhecida até D (vistoria programada ou cadência da versão do protocolo): "ausente: sem registro conhecido".
  - Sem sinal nem expectativa: nada.
- **T1c.** Conhecer o fato depois de D não muda nem revela nada em D. A saída de D é idêntica com e sem o fato que só chega depois.
- **T6a.** Para classificar uma leitura (NC, unidade, parâmetros), vale a versão **vigente no t_evento da leitura entre as publicadas até o corte** (t_disp da versão ≤ D).
  - Versão publicada depois do corte, mesmo com vigência retroativa, não muda o resultado de D; vale para os cortes posteriores à publicação.
  - No ADV-19, cada versão é publicada no início da sua vigência.

**ADV-07 (substituto) · Revisão retroativa e sincronização tardia**
- Entrada:
  - leitura L em d5 = 4, com t_disp d5, corrigida para 14 com t_disp d20;
  - leitura M em d8, com t_disp d11, sem nenhum sinal antes de d11;
  - vistoria do talhão programada para d8, com t_disp d1.
- Esperado:
  - D = 10: L = 4; M não aparece; a vistoria programada de d8 aparece como "ausente: sem registro conhecido", nunca "não sincronizada" nem zero;
  - a saída de D = 10 é idêntica nos mundos com M e sem M;
  - D = 11: M presente; D = 25: L = 14;
  - recalcular D = 10 em qualquer data dá a mesma saída.
- Variante com sinal: aviso de pendência de M recebido em d9 → em D = 10, "não sincronizada" (e só nesse caso).

**ADV-07b (novo) · Versão retroativa do NC**
- Entrada: NC v1 = 15, vigente e publicada desde d0; v2 = 10, vigente desde d5 e publicada em d20. Leitura d6 = 12.
- Esperado:
  - consulta com D = 10 → "abaixo do NC (15, v1)";
  - consulta com D = 25 → "acima do NC (10, v2)";
  - recalcular D = 10 depois de d20 → continua v1.
- Contraprova: um classificador que use a "versão vigente no t_evento" sem filtrar a publicação dá "acima (10, v2)" em D = 10 e reprova.

### Δ 17/10-2 · População própria do seguimento (substitui "População" e "Estados" do EST-3b)

- **P-SEG(D):** aplicações contra o alvo realizadas e confirmadas (U2), com T1.
  - Não exige leitura depois, controle nem ausência de outra aplicação: essas condições definem estados, não a entrada.
  - A leitura antes é exportada se existir, mas não é exigida.
  - A P-EPI (EST-3a) continua como estava. Os relatórios mostram as duas populações (P1).
- **Janela de seguimento:** W = (t_aplicação, t_fim]. t_fim é o instante da próxima aplicação contra o alvo no mesmo talhão, se houver até D; senão, D.
  - Só leituras completas em W, com T1.
  - Leitura do dia da nova aplicação sem hora ou ordem confiável fica fora de W (A6).
- **Estados** (exclusivos, avaliados nesta ordem):
  1. S6: NC incompatível → indisponível.
  2. Nenhuma leitura em W: S5a "encerrado por nova aplicação em t, sem leitura depois", se W terminou por nova aplicação; senão S4 "sem leitura depois".
  3. 1ª leitura de W ≥ NC: S2 "retorno não demonstrado".
  4. Leitura < NC seguida de leitura ≥ NC em W: S1 "retorno entre t_(k−1) e t_k", com a largura (o primeiro par desse tipo).
  5. Todas as leituras de W < NC: S5b "abaixo do NC até t_k; encerrado por nova aplicação em t", se W terminou por nova aplicação; senão S3 "abaixo do NC até t_k" (censura em t_k).
- **ADV-05 com a P-SEG:**
  - (a) S5b "abaixo do NC até d9; encerrado por nova aplicação em d12";
  - (b) S2;
  - (c) S1 (d9, d23], largura 14;
  - (d) S3 em d16;
  - (e) S4;
  - (f) no EST-3a, "interferência"; no EST-3b, a1 fica S5a "encerrado por nova aplicação em d4, sem leitura depois", e a aplicação de d4 tem seguimento próprio;
  - **(g) novo:** aplicação em d2, nova aplicação em d5, nenhuma leitura até D = 20 → S5a em d5, nunca S4.

### Δ 17/10-3 · ADV-01 com os ramos explícitos (substitui o "Esperado" do ADV-01; executado, `delta_1710.txt` bloco A)

| Corte | Controles com d12 = 10 | Controles com d12 = 30 |
|---|---|---|
| D = 10 | sem comparação válida: controle sem leitura depois até D | igual à coluna ao lado, byte a byte |
| D = 12 (tolerância da versão ≥ 2 dias) | E = 0,5000000000 | E = 0,8333333333 |

- A invariância vale só antes da disponibilidade (D = 10). Em D = 12 a saída muda com a leitura, como deve.
- Contraprova: o `rxHT` do v3 já em D = 10 dá 0,4762 e 0,8197 (R-C1).

### Δ 17/10-4 · Chaves com a identidade de origem (substitui a coluna "Chave" da §2)

| ID | Chave |
|---|---|
| U1 | (org, fazenda, cultivo, safra, talhão, alvo, leitura_id, versão) |
| U2 | (org, fazenda, cultivo, safra, talhão, evento_id, versão) |
| U3 | (org, fazenda, fonte, estação ou talhão/cultivo, período, variável, versão). Em fonte regional compartilhada, também o id do local no provedor |
| U4 | (org, fazenda, fonte, emissão_id, revisão da emissão, t_emissão, t_alvo, variável, local), com t_disp por revisão. Duas revisões da mesma emissão são versões distintas, e T1 escolhe a de maior t_disp ≤ D (ou ≤ t0) |
| U5 | (org, fazenda, cultivo, safra, talhão, alvo, leitura_1, leitura_2, D, versão de parâmetros, versão do contrato) |
| U6 | (org, fazenda, cultivo, safra, aplicação_id, alvo, leitura_antes, leitura_depois, D, versões) |
| U7 | (org, fazenda, cultivo, safra, talhão, alvo, t0, h, versões) |

- Os campos de identidade são copiados da origem (contrato comum do EX-42 F1a), nunca recalculados nem inferidos do nome. IDs locais só são únicos dentro de (org, fazenda).
- Par, episódio, controle e origem nunca cruzam fazenda, cultivo ou safra.

**ADV-22 (novo) · Colisão de IDs**
- Entrada: fazendas F1 e F2, da mesma org e de orgs diferentes, cada uma com talhão "P3" e leitura_id "L1" no mesmo dia.
- Esperado:
  - unidades distintas;
  - nenhum par, episódio ou controle mistura F1 e F2;
  - as contagens por fazenda são iguais às de cada fazenda processada sozinha.

### Δ 17/10-5 · ORA-05 e cobertura (substitui a linha ORA-05 e o "Oráculo" do EST-3b)

- **Exportado por aplicação:**
  - t_queda: 1º dia com latente < NC depois da aplicação;
  - t_retorno: 1º dia ≥ NC depois de t_queda;
  - todos os cruzamentos para cima depois de t_queda;
  - t_primeiro_acima: 1º dia ≥ NC depois da aplicação, que existe mesmo sem queda.
- **Fixture sem ruído de medida** (leitura = latente). Invariantes determinísticas para S1:
  - há ao menos um cruzamento para cima em (t_(k−1), t_k];
  - t_retorno ≤ t_k.
  - "t_retorno dentro do intervalo" **não** é invariante. Executado (`delta_1710.txt` bloco B2): o retorno em d5 fica fora de (d9, d16], e o cruzamento de d13 fica dentro.
- **Com ruído de medida** nada é determinístico. São medidas de cobertura, com n e população:
  - fração de S1 com t_retorno no intervalo;
  - fração de S1 com algum cruzamento no intervalo;
  - fração de S2 em que o latente nunca caiu abaixo do NC (bloco B3).
  - Sem limiar de aprovação no RX-0; limiar, se houver, é do contrato do RX-1.

**ADV-21 caso (c) (novo)**
- Entrada: as fixtures B1, B2 e B3 de `delta_1710.txt`.
- Esperado: as saídas registradas lá, campo a campo (queda, retorno, cruzamentos, intervalo de S1 e as duas verificações).

### Δ 17/10-6 · Alcance da equivalência HT × contraste de logs (EST-3a; revisão R7)

- A identidade ln(1 − E) = [ln T_depois − ln T_antes] − [ln C_depois − ln C_antes] foi demonstrada só para valores positivos (K10). Com algum zero, os dois lados saem infinitos (`delta_1710.txt` bloco C).
- É álgebra de um par antes/depois. Não prova identificação causal, nem tendência paralela, nem equivalência a qualquer estimador DiD (vários períodos, regressão, escala de nível, adoção escalonada).
- O teste de pré-tendência do U5 só pode reprovar.

### Δ 17/10-7 · D4 só como alternativa exportada (substitui "Pergunta" e "Exportado pelo RX-0" do EST-4)

- O RX-0 exporta separadamente:
  - **cruzamento observado:** alguma leitura completa em (t0, t0 + h] ≥ NC;
  - **ação registrada:** aplicação contra o alvo em (t0, t0 + h], com o motivo;
  - a perda.
- O composto "precisou de ação" é só alternativa derivada. Não é estimando primário nem verdade agronômica (6227947437). A escolha é do contrato do RX-4.
- População, perda e intercorrentes do EST-4 não mudam.

### Δ 17/10-8 · Aceite

Os itens 1 e 2 da §9 valem para ADV-01 a ADV-22, com o ADV-07b e o caso (c) do ADV-21. O caso (c) separa a invariante sem ruído de medida da medida de cobertura.

### Δ 17/10-9 · Dependência

O RX-0 depende do EX-42 (F1a, F1d e F1b integradas). Ele só vira executável depois que o Codex registrar contrato, base e arquivos delimitados, com autoria definida e dentro do teto de frentes (AGENTS §3.6). Esta proposta não abre implantação e não passa à frente da PR 88 (6227947437).

### Δ 17/10-10 · ICH E9(R1)

Referência oficial localizada pelo Codex: *ICH E9(R1) Addendum on estimands and sensitivity analysis in clinical trials to the guideline on statistical principles for clinical trials*, Step 4, 2019, https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf. É framework metodológico, não norma agro.

### Rastreabilidade do Δ

| Pedido do Codex (6227947437) | Onde |
|---|---|
| 1. ADV07/T6 | Δ 17/10-1; ADV-07 substituto; ADV-07b |
| 2. EST3b | Δ 17/10-2; ADV-05(g) |
| 3. ADV01 | Δ 17/10-3; `delta_1710.txt` A |
| 4. U3/U5/U6/U7 e U4 | Δ 17/10-4; ADV-22 |
| 5. ORA05 | Δ 17/10-5; ADV-21(c); `delta_1710.txt` B |
| 6. HT × logs | Δ 17/10-6; `delta_1710.txt` C |
| D4 | Δ 17/10-7 |
| ICH E9(R1) | Δ 17/10-10 |
| Dependência | Δ 17/10-9 |
