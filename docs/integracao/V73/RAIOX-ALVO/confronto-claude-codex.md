# Raio-X do alvo · confronto Claude × Codex (passo 2)

Versão 1 · 17/10/2026 · autor Claude · revisor e registro: Codex. Gemini **não** consultado nem simulado: o pacote da §7 é enviado pelo Codex. Nada aqui é desenho final; o Codex registra o desenho e as fatias no checkpoint. Só leitura e reprodução: nenhum arquivo de produto foi alterado, nenhum comentário foi publicado no GitHub.

## 0. Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: RAIOX-ALVO passo 2 · confronto ponto a ponto das duas avaliações, com prova própria de cada divergência · agentes, RT (pelo Gemini) e proprietário
Requisitos do PRD e fora do escopo: os do passo 1 (CL:11) mais EX-42 §8 · fora: implantação, checkpoint, envio ao Gemini, comentário no PR
Autor / revisor / integrador: Claude / Codex / Codex registra o desenho e as fatias
Base: v3 529adf7 (SHA-256 e7872cb0…805e5e); crítica do Claude 34e411a; avaliação do Codex b291746 (codex/raiox-avaliacao-20261017); PR #47, comentários 6227178767, 6227224844 e 6227327207; PRD e DECISIONS em origin/main c8274086; EX-42 em b989864 · arquivos: docs/integracao/V73/RAIOX-ALVO/confronto-claude-codex.md e reproducao/confronto/**
Aceite e comando de verificação: git show 529adf7:docs/integracao/V73/pedidos-1610/raiox-pragas-no-tempo-v3.html > /tmp/v3.html; git fetch origin codex/raiox-avaliacao-20261017; bash docs/integracao/V73/RAIOX-ALVO/reproducao/confronto/rodar.sh /tmp/v3.html <saída> → saída 0, cinco "igual ao versionado" e três "igual ao bruto do Codex"
Estado / impedimento / próximo passo: entregue · o Codex aceita, ajusta ou recusa cada resolução da §3, envia a §7 ao Gemini real e registra o desenho e as fatias no checkpoint
```

**Como ler.** `CL:n` é a linha de `critica-claude.md` (34e411a). `CX:n` é a linha de `docs/integracao/V73/RAIOX/codex/raiox-avaliacao-codex.md` (b291746). `#622…` é um comentário no PR #47, lido com `gh api` (só leitura). `PED:n` é a linha de `raiox-alvo-pedido.md` (529adf7; o arquivo é idêntico em 96191be, a base citada pelo Codex). `ART:n` é a linha do v3 em 529adf7. `PRD:n` e `DEC:n` estão em origin/main c8274086, e `EX-42:n` em b989864. `R-Cn` é a seção "== Cn" de `reproducao/confronto/confronto.txt`. **Executado** significa que rodei e a saída está versionada; **lido**, que é leitura sem execução; **especificado**, que é proposta ainda não testada.

## 1. Resumo

- **35 pontos confrontados (§3):** 15 convergentes, 12 complementares e 8 divergentes. Cada uma das 8 divergências tem resolução proposta: 5 por fonte, 2 por reprodução e 1 por método (E1). Cabe ao Codex aceitar ou recusar cada uma. O Gemini recebe só as decisões de domínio e de parâmetro que restam (§7).
- **As três contraprovas do Codex procedem** (executado, com prova própria; §4):
  1. **Controle depois de D:** confirmado. No v3, toda a linha do tempo tem 1.055 item-data afetados em 21 sementes, com |ΔE| de até 74,9 p.p. Em D = 86 o efeito é zero.
  2. **Clima realizado no teste:** confirmado. Com o treino idêntico, trocar só o clima posterior ao corte muda o Brier. Usando só dados até a origem, o modelo vence a persistência em 2 de 21 sementes no ácaro e em 4 de 21 na mosca.
  3. **Fallback do pareamento:** confirmado. Em 17 das 56 aplicações, só se chega a 2 controles pelo nível "qualquer candidato".
- **A crítica do Claude tem 7 correções** (E1 a E7, §5), com o texto original preservado:
  - p-valor por contagem no bootstrap;
  - rótulo "falsos" no nulo do clima;
  - contrato do backtest;
  - descrição do pareamento;
  - aceite de 80 %;
  - escopo da F1b;
  - D1 e D3.
- **Os números da crítica não mudam.** Todos foram calculados em D = 86, onde o controle posterior a D não ocorre. A conclusão "sem previsão, perde da persistência em 19 de 20 sementes" vale **só no ácaro e na mosca** e passa a ser rotulada como diagnóstico retrospectivo.
- **Achados que nenhum dos dois viu** (§6.3): o "Próximos 7 dias" numa data passada usa o clima realizado depois de D; irrigação e adubação realizadas depois da origem entram no risco; o conjunto de teste é escolhido com informação posterior à origem; e há outra aplicação dentro do seguimento.
- **Para o proprietário** (§8), só a fonte de clima horário e de previsão com arquivo (custo e contrato). As fontes vigentes já respondem D1 e D3.

## 2. Evidência executada e brutos

| O quê | Onde | Estado |
|---|---|---|
| Reprodução da crítica: original, 20 réplicas, nulo do clima e época | `reproducao/repro.json` (blocos `original`, `replicas`, `nuloClima`, `nuloClimaSuave`, `epoca`), `resumo.txt`, `calor.txt`; script `raiox_repro.mjs` | Executado pelo Claude em 17/10. **Reproduzido pelo Codex** em #6227327207 (Node 24.19; 237/280, 130/280, 4 F/M, 41 + 3 ruídos; diferenças < 1e-12). Deixa de ser só relato. Ressalva dele: isso verifica a reprodução, não valida o método |
| Provas do confronto (C1 a C7) | `reproducao/confronto/confronto.mjs` → `confronto.json` (semente original completa e 20 réplicas), `resumo.mjs` → `confronto.txt` | Executado, Node v22.22.0, cerca de 30 s |
| Harness do Codex (b291746): núcleo, controle futuro e previsão futura | executados pelo `rodar.sh`, passo 3, a partir do commit dele | Executado: as três saídas são **iguais** aos brutos dele. O motor contido no harness é idêntico ao do v3 (conferido por inclusão literal) |
| Comando único | `reproducao/confronto/rodar.sh <v3.html> <saída>` roda os passos 1 a 3 e confere com os brutos versionados (`conferir.mjs`) | Executado três vezes. A 1ª gerou as saídas do confronto, que foram versionadas. A 2ª acusou só a linha "nota" do resumo da crítica, um argumento opcional do `../rodar.sh`, agora repassado. A 3ª deu saída 0, com tudo igual. Log da 3ª em `reproducao/confronto/rodada.txt` |

**Ganchos** (cada um com uma ocorrência conferida; o script falha se não achar o texto exato):
- semente das réplicas, igual à da crítica;
- clima da análise trocável depois de um dia de corte, sem mexer na simulação;
- três ganchos que só **leem** o rxHT (nível de pareamento e controles lidos depois de D).

A autoconferência compara E e nCtrl com o rxHT sem os ganchos, em D = 30, 50, 70 e 86: são iguais.

**C5 é indicativo**, não é método proposto. A reamostragem replica linhas, o que torna a regra "8 de cada lado" do limiar mais permissiva, e a variável fora do modelo conta como efeito 0.

## 3. Tabela de confronto

| # | Tema | Claude (34e411a) | Codex (b291746 e PR #47) | Classe | Resolução proposta | Como foi resolvida |
|---|---|---|---|---|---|---|
| X-01 | Números declarados do protótipo | 12/14, 0 F/M, Brier 4/4 (CL:24, :229-231) | o mesmo (CX:11-16) | convergente | nenhuma | Reprodução cruzada: o Codex rodou o script do Claude (#6227327207) e o Claude rodou os 3 harness do Codex (`rodada.txt`, passo 3). Executado |
| X-02 | O que o 12/14 conta | 5 dos 12 são Fraca; 7/14 em F/M (CL:24) | conta direção pela variável do grupo; não mede magnitude (CX:18) | complementar | O gabarito separa direção em qualquer nível, direção em F/M, direção pelo grupo e magnitude contra o oráculo | Reprodução R-C5: com a seleção refeita, só 2/14 têm IC95 sem o zero e sinal certo |
| X-03 | Aceite de direção | RX-0: ≥ 80 % em F/M, com 2 safras (CL:201) | registrar a divergência; não afrouxar (#6227224844) | **divergente** | Manter os 100 % de PED:209 na fixture de referência, para efeitos "fortes" definidos antes do ajuste pelo oráculo. A taxa na série de sementes é medida e publicada. Meta abaixo de 100 % só com decisão do proprietário | Por fonte: PED:209 é o aceite do pedido. O Claude retira os 80 % como aceite (E5) |
| X-04 | Falso positivo ≤ 5 % | ruído exibido em qualquer nível ≤ 5 % (CL:201) | separar "0 na fixture" de "≤ 5 % na série"; denominador, sementes e regra fixados antes (CX:43) | complementar | Fixture: 0 em F/M. Série com ≥ 20 sementes: F/M ≤ 5 % (PED:210), com "qualquer nível" medido à parte | Por fonte (PED:210) e reprodução: F/M 4/480, qualquer nível 44/504, conferido pelo Codex |
| X-05 | Controle lido depois de D no rxHT | não visto | "rxHT, linhas 620–634: nearestObs ±3 admite controle depois de D" (CX:21) | complementar (só o Codex) | Só observação ≤ D. Sem par elegível, "sem comparação válida" | Reprodução R-C1 (§4.1) e fonte EX-42:28 ("Nenhuma fonte futura entra em análise até D") |
| X-06 | Teste da previsão com clima realizado | "é previsão perfeita" (CL:132) | o mesmo, com harness: +70 °C em D35 dá +10 °C na entrada (CX:22) | convergente | Backtest só com dado disponível na origem e previsões arquivadas | Harness do Codex (igual) e R-C2: treino idêntico, e trocar só o clima pós-corte muda o Brier (§4.2) |
| X-07 | Contrato do backtest em origem móvel da crítica | "Executado, origem móvel semanal" (CL:133-142) | não é previsão fixa de 7 dias na origem; manter como diagnóstico (#6227327207) | **divergente** | Rotular como diagnóstico retrospectivo. Contrato prospectivo (origem e horizonte fixos, população na origem) antes de usar o Brier como portão | Reprodução R-C7: 1ª vistoria depois da origem em 0 de 370 pares (o filtro permitiria até 2 dias). Horizonte da origem até a 2ª vistoria: 1, 2 ou 7 dias. Procede em parte (E3) |
| X-08 | Pareamento com fallback | só descreve o 1º nível (CL:118); "0 sem controle porque o gerador escalona" (CL:125) | relaxa até qualquer candidato (CX:23) | complementar, com correção da crítica | Sem fallback. Nível de pareamento declarado. Sem par: resultado indisponível, com motivo | Reprodução R-C3: 17/56 só pelo nível 3 (282/1.193 em 21 sementes) (E4) |
| X-09 | ε no Henderson-Tilton | ε só na taxa r (CL:88) | ε muda o HT tradicional; rótulo e método explícitos; não suavizar denominador inválido (CX:23) | complementar (só o Codex) | HT clássico como padrão (PED:121); ε só declarado; denominador zero → indisponível | Por fonte: ART:631 (`tr = (after + eps) / (before + eps)`) e PED:121 (fórmula sem ε). Valor → Gemini Q2 |
| X-10 | Seguimento do NC | retorno num intervalo, sem estimador, Turnbull com ≥ 20 casos (CL:123) | censura em D, dia exato, 1ª leitura pós acima não é retorno (CX:24) | convergente | EX-42 §8 inteiro; censura na última leitura elegível; sem estimador nesta fase | Por fonte (EX-42:42) e reprodução R-C4 (§4.4) |
| X-11 | Seleção de janela, limiar e representante; evidência pós-seleção | "maldição do vencedor"; refazer a escolha na reamostragem (CL:99) | validar o procedimento inteiro; "sem estimativa executada" (CX:25) | convergente | Seleção refeita dentro de cada treino ou reamostragem, validada em dados separados; limiar do protocolo | Reprodução R-C5 (indicativa): 7/14 F/M no v3 caem para 2/14 com a seleção refeita; ruído 0 |
| X-12 | p-valor por contagem no bootstrap | "p = (k + 1) ÷ (B + 1)" no servidor (CL:100, :166) | não adotar sem hipótese nula e teste definidos (#6227224844) | **divergente** | Declarar H0. O (k + 1) ÷ (B + 1) só vale com reamostras geradas sob a nula; o bootstrap em torno da estimativa dá intervalo, não p | Por método, lido (E1). O Claude aceita |
| X-13 | Época com 1 safra | o calor some com o controle de época; selo; Forte só com 2 safras (CL:163, :154-156) | não excluir a época só porque some um efeito; não identificabilidade; sensibilidade (CX:26) | complementar | Com 1 safra, rodar com e sem época, mostrar os dois e o selo. Forte só com 2 safras | Reprodução da crítica (`calor.txt`): calor em F/M 4, 7 e 3 de 21 → 0 ou 1 de 21 com época. Regra → Gemini Q1 |
| X-14 | Nulo do clima ("falsos") | 18 achados "falsos" (CL:247; :178; placebo :157) | o clima deslocado não é independente: "variável desalinhada no controle negativo" (#6227327207) | **divergente** | Trocar o rótulo. Placebo só com desalinhamento verificado (\|ρ\| baixo) ou com outra safra | Reprodução R-C6: \|ρ\| entre o clima deslocado e o verdadeiro chega a 0,76 (E2) |
| X-15 | Linguagem causal na 1ª camada | vista "Sobe e desce"; "faz subir" no aceite (CL:189, :201) | "associado a aumento/redução", não "faz subir" (CX:29) | **divergente** (leve) | 1ª camada: "associado a aumento/redução". Vista sem verbo causal | Por fonte: PED:135 ("Associação não é causa"). O Claude adota a posição do Codex |
| X-16 | Ranking, frases de ação, resistência | cortar "rotacione" e "prefira" (C-02, C-03, CL:124) | sem ranking; "possível perda de resposta; investigar…" (CX:26, :29, :51) | convergente | Texto do aviso do Codex, nunca diagnóstico | Por fonte: PRD:6215, :6225 e EX-42:40. Critério do aviso → Gemini Q5 |
| X-17 | Camada 3 dentro da F1b? | "a mesma peça do AG-06 e da F1b" (C-04, CL:41; RX-1, CL:202) | a F1b não autorizou causalidade nem sobrevivência; contrato próprio (#6227224844; CX:35) | **divergente** | Extensão com contrato próprio, reaproveitando a peça e a função de domínio da F1b, depois de ela integrada | Por fonte: EX-42:40 ("sem… eficácia causal") e :42 ("não introduzir estimador de sobrevivência nesta fatia") (E6) |
| X-18 | Entrada no Mapa, sem menu novo | C-05 | CX:29 | convergente | nenhuma | Por fonte: DEC:111 (DEC-1610-09) e EX-42:24 |
| X-19 | Cabeçalho e estados | estado em palavras e base no topo (CL:190) | data de corte, cobertura e 5 estados: calculando, disponível, insuficiente, desatualizado, erro (CX:29) | complementar | Juntar: cabeçalho com alvo, cultura/safra, protocolo/unidade, data de corte, base e cobertura; 5 estados, cada um com o próximo passo | Lido; sem conflito |
| X-20 | Design system | cor de estado em dado, mapa de correlações, tabela equivalente, 44 px (C-06 a C-08, CL:191) | aceita C-06 a C-08 como direção (#6227224844); teclado, 1440/390 (CX:31) | convergente | nenhuma | Por fonte: PRD:14122, :13883, :14725 |
| X-21 | Validade, NC histórico, parâmetros, UR ≠ molhamento | C-09 a C-12 | aceita (#6227224844) | convergente | nenhuma | Por fonte: EX-42:30, :38, :44; DEC:149; PRD:512 |
| X-22 | "Criar vistoria" ou "Programar vistoria" | usar o "Programar vistoria" existente (C-16) | "rascunho com contexto" (CX:31); depois aceita C-16 (#6227224844) | convergente | "Programar vistoria" → FO-03, herdando talhão, alvo e protocolo | Por fonte: PRD:430 |
| X-23 | Marca do RT ≠ publicação | C-17 | CX:31; aceita (#6227224844) | convergente | nenhuma | Por fonte: PRD:508-510, :6235 |
| X-24 | Pré-requisito EX-42 e teto de frentes | depois de F1a, F1d e F1b; teto de 3 (C-14, CL:197) | dependência imediata do EX-42; a q30 vem primeiro (CX:34, :39, :53) | convergente | nenhuma | Por fonte: AGENTS §3.6 e EX-42:50-56 |
| X-25 | Gabarito e contrato de dados | RX-0: oráculo, 2 safras, campanhas, sequências, placebo (CL:201) | contratos com tempo disponível e proveniência; sementes independentes; casos adversariais (CX:34, :44) | complementar | Unir as duas listas (§9) | Lido |
| X-26 | Método da camada 2 | regressão com efeito de talhão; não GBM+SHAP (CL:106-111) | comparar uma alternativa simples antes de LightGBM/SHAP (CX:25) | convergente | Regressão primeiro; GBM só se passar no gabarito completo | Por fonte: PED:111 ("o mais simples que passar no gabarito") |
| X-27 | Portão da previsão | duas referências, ≥ 20 eventos, sem % antes da calibração, cortar 14 dias (CL:113, :144-145) | validação por horizonte; 14 dias com aceite próprio (CX:18, :22, :37, :45) | convergente | Portão prospectivo da §7 Q4 | Parâmetros → Gemini Q4 |
| X-28 | Nível de evidência | só F/M; mínimos por tipo; Forte só com 2 safras (CL:147-157) | Forte não só pela mesma safra (CX:25); os números são "propostas, não garantia" (#6227224844) | convergente (direção) | Regra declarada antes do ajuste | Material de domínio → Gemini Q1 |
| X-29 | Ausência e cobertura da janela | ≥ 80 % dos dias, senão "sem dado" (CL:80) | ausência ≠ zero (CX:44); 80 % como proposta (#6227224844) | convergente | nenhuma | Parâmetro → Gemini Q6 |
| X-30 | Teste com usuários (UX-13) | não visto | "3 a 5 e pelo menos 4" é incoerente (CX:42) | complementar (só o Codex) | Fixar antes: 5 participantes e ≥ 4 de 5, quando a DEC-1610-02 chegar | Por fonte: DEC:104 (DEC-1610-02: 3 a 5, depois dos demais módulos) e PED:222 |
| X-31 | Job real | conjunto com hash e chave idempotente do achado (CL:209) | publicação atômica, falha e recuperação, acesso revalidado (CX:46) | complementar | Unir | Lido |
| X-32 | Custo de cálculo | medido 31-65 ms por alvo e data; estimados ~6 min de CPU por fazenda por noite (CL:221) | fora (CX:50) | complementar (só o Claude) | Fica como estimativa; o plano de nuvem é do proprietário quando houver software real | Lido |
| X-33 | D1: o motor fica fora do "assistente de IA desligado"? | "É dele? Sim" (CL:215) | não presumir; conferir as vigentes (CX:50; #6227224844) | **divergente** (leve) | Não perguntar de novo: informar, com o custo | Por fonte: DEC:113 desliga o **assistente** "com provedores e local de processamento"; PRD:15352 e :15385 (PEND-IA-01: provedores, contrato de dados); o motor é "motor determinístico" (PRD:4744, :9009; IAG-04 em :15350) (E7) |
| X-34 | D3: quem marca e quem promove | "É dele? Sim" (CL:217) | idem | **divergente** (leve) | Promover já é o fluxo de versão do AG-05 com aprovador técnico; quem marca é regra de produto delegada | Por fonte: PRD:508-510, :6282, :6235; DEC:134 ("Cobre: produto, regra…") (E7) |
| X-35 | D2: mínimo de evidência | delegável, com o Gemini (CL:216) | não presumir (CX:50) | complementar | Proposta conjunta depois do Gemini; o proprietário confirma no desenho final | Por fonte: PED:234 lista a D2 como dele; DEC:134 permite padrão seguro até lá |

## 4. Contraprovas do Codex: prova própria e efeito na crítica

### 4.1 Controle lido depois de D (X-05) — confirmada

- **Fonte (lido).** `nearestObs(sq.obs, da, 3)` (ART:627) aceita a leitura do controle até 3 dias depois de `ap.after.day ≤ D`. Só o tratado é cortado em D (ART:625).
- **Fixture (executado, R-C1).** É a do Codex, mas rodando o `rxHT` extraído do v3, não uma cópia:
  - com os controles lidos em D1 e D12, E = 0,4762, e os 2 controles foram lidos depois de D;
  - com só as leituras até D, E vira "sem comparação válida";
  - mudando **só** a leitura de D12 dos controles para 30, E = 0,8197. Um dado posterior a D muda o resultado.
- **Nos dados do v3 (executado, R-C1).** Comparei o `rxHT` com um `rxHT` só com dados até D, em cada data D de 1 a 86:
  - semente original: 47 item-data mudam E (13, 14, 10 e 10 por alvo), 7 viram "sem comparação válida" e o maior |ΔE| é 27 p.p.;
  - 21 sementes: 1.055 item-data mudam E, até 74,9 p.p.;
  - **em D = 86: zero.**
- **Efeito na crítica:** nenhum número muda, porque a camada 3 da crítica foi calculada em D = 86. O defeito afeta quem volta a linha do tempo, e a regra do EX-42:28 cobre esse caso.

### 4.2 Clima realizado no teste da previsão (X-06, X-07) — confirmada, com três extensões

Prova própria (executado, R-C2), no desenho do gate do v3 (corte em D − 21, D = 86).

**Mecanismo:**
- Todas as variáveis de janela usadas no teste do ácaro incluem dias depois da 1ª vistoria do par (217/217). Nos demais alvos: 264/308, 294/343 e 222/259.
- Treino idêntico (conferido: β igual). Trocar só o clima posterior ao corte pelo de 35 dias antes muda o Brier do modelo:
  - ácaro 0,0588 → 0,1083;
  - mosca 0,0443 → 0,0877;
  - antracnose 0,0030 → 0,0004;
  - cochonilha 0,0441 → 0,0569.

**Quantas vezes o modelo vence a persistência, em 21 sementes:**

| Variante | Ácaro | Mosca | Antracnose | Cochonilha |
|---|---|---|---|---|
| v3, clima realizado | 19 | 21 | 18 | 21 |
| Só dados até a 1ª vistoria (tempo dos dias anteriores) | **2** | **4** | 18 | 21 |
| Climatologia das 4 semanas anteriores | 3 | 7 | 20 | 21 |
| "Previsão" com metade dos dias certos | 13 | 19 | 20 | 21 |

**Extensões que nenhum dos dois tinha visto** (§6.3):
- **na tela:** em D < 86, o "Próximos 7 dias" do detalhe do talhão (ART:1024) lê o clima realizado de D + 1 a D + 7. Trocar só esse clima muda a probabilidade em até 63,3 p.p. (cochonilha, D72) e em todos os talhões do ácaro em D58;
- **manejo:** a irrigação e a adubação realizadas depois da origem também entram. Somar 70 mm no dia 75 muda a irrigação da janela de 29 para 99 mm/semana, e 12 adubações caem em (72, 79];
- **população do teste:** o par só existe se não houve aplicação entre as vistorias. Isso é informação posterior à origem: exclui 731 de 4.863 pares candidatos em 21 sementes, 213 deles abaixo do NC na origem (exatamente os talhões cujo risco o painel mostraria).

**Efeito na crítica:** confirma CL:132. O número de CL:27 e CL:142 ("sem previsão perde em 19 de 20 sementes") vale **só no ácaro e na mosca**. Na antracnose e na cochonilha, a versão sem previsão vence a persistência em 16 e 20 de 20. No gate do v3 isso reaparece: 2/21 e 4/21 contra 18/21 e 21/21. O contrato da tabela da crítica muda o rótulo (E3), não os números.

### 4.3 Fallback do pareamento (X-08) — confirmada

- **Fonte (lido):** ART:630 tem três níveis. Primeiro, estádio e nível ≥ 30 %; depois, só o estádio; e, com menos de 2, **qualquer candidato**.
- **Executado (R-C3), em D = 86:**
  - ácaro 13/0/3, mosca 12/0/4, antracnose 3/0/6 e cochonilha 11/0/4 (níveis 1/2/3);
  - "sem comparação" 0;
  - em 21 sementes, 282 de 1.193 aplicações só têm E pelo nível 3.
- **Com a regra estrita que a crítica propôs** (±2 dias, nível 0,5× a 2×, sem aplicação nem resíduo do controle, só até D):
  - 22 das 56 aplicações ficam sem comparação, além de 8 leituras do dia excluídas;
  - em 21 sementes, 479 de 1.193.
- **Efeito na crítica:** CL:118 descreve só o 1º nível. CL:125 ("0 aplicações sem controle válido, porque o gerador escalona os gatilhos") explica só parte: o zero também vem do fallback. A tabela da camada 3 (CL:235) chama de "controle válido" o que inclui o nível 3. Correção E4. A conclusão de CL:244 (nenhuma diferença passaria na regra da 3.6) fica mais forte, porque com a regra estrita o n cai.

### 4.4 Seguimento do NC (X-10) — procede

**Executado (R-C4), em D = 86:**
- o v3 conta o retorno no dia exato, mas o retorno demonstrado está sempre num intervalo de 7 dias (vistorias semanais);
- censurar em D, e não na última leitura, acrescenta de 0 a 6 dias (média ~3);
- "1ª leitura pós já acima do NC": 0 na semente original. Isso confirma CL:123, que vale só para essa semente. Em 21 sementes há 21 casos, e as réplicas já trazem a contraprova dirigida;
- outra aplicação dentro do seguimento: 7 de 56 na semente original e 112 de 1.193 em 21 sementes. O v3 credita o seguimento à primeira aplicação (§6.3).

### 4.5 Evidência pós-seleção (X-11) — reforça os dois

- **Executado (R-C5, indicativo):** refazendo janela, limiar e representante em cada uma de 200 reamostras em blocos de talhão × semana, só 2 dos 14 efeitos plantados mantêm o IC95 sem o zero com o sinal certo (mosca: folha molhada e chuva forte). No v3 são 7 de 14 em F/M. Nenhuma variável de ruído passa.
- Isso estima, para esta semente, a inflação que o Codex registrou como "ainda sem estimativa executada" (CX:25).

## 5. Correções da crítica do Claude (texto original preservado em `critica-claude.md`)

| ID | Onde (CL) | Original (trecho) | Correção | Prova |
|---|---|---|---|---|
| E1 | :100, :166 | "No servidor: B ≥ 2.000 e p = (k + 1) ÷ (B + 1)" | O p-valor exige H0 declarada (efeito = 0 da variável, com os controles) e um teste. A fórmula (k + 1) ÷ (B + 1) só vale para reamostras geradas **sob a nula**: permutação em blocos ou controle negativo com desalinhamento verificado. O bootstrap em torno da estimativa dá **intervalo** (percentil ou BCa), ou um teste de Wald com erro-padrão do bootstrap, rotulado como aproximação com ~12 semanas efetivas. O q < 0,10 de CL:154 passa a depender desse teste declarado | Lido (#6227224844); aceito pelo Claude |
| E2 | :247, :178, :157 | "18 achados de clima **falsos**"; placebo "com o clima deslocado" | "18 achados com a **variável desalinhada** (controle negativo), não verdade causal conhecida". O clima deslocado ainda correlaciona com o verdadeiro: na janela 0, os dias quentes e secos têm ρ de −0,68 a −0,76 no deslocamento de 49, e de −0,26 a −0,39 no de 35. O placebo da 3.6 só vale com desalinhamento verificado (\|ρ\| baixo), ou entre safras. A correção vale só para o clima deslocado. Nas variáveis sem efeito plantado do gabarito (CL:230), "falso positivo" segue a definição de ruído do pedido (PED:208, :210) | Executado, R-C6; #6227327207 |
| E3 | :27, :133-142, :168 | "Executado, origem móvel semanal… sem previsão perde em 19/20" | Fica como **diagnóstico retrospectivo**, não como portão prospectivo. O horizonte da origem até a 2ª vistoria é de 1, 2 ou 7 dias, não 7 dias fixos. A 1ª vistoria nunca passou da origem (0/370, embora o filtro permita até 2 dias), então a coluna "sem previsão" não leu tempo realizado depois da origem. A coluna "Modelo" usa o clima realizado por desenho, e a população do teste é condicionada à ausência de aplicação depois da origem (§6.3). O contrato prospectivo vai na Q4. A falta de previsão arquivada exige avaliação separada, sem trocá-la pelo clima realizado | Executado, R-C7 e R-C2; #6227327207 |
| E4 | :118, :125, :235 | "aceita 2 controles quaisquer com nível ≥ 30 %…"; "0 sem controle porque o gerador escalona"; "(aplicações com controle válido)" | O v3 relaxa até qualquer candidato (ART:630). Em 17 das 56 aplicações, o E existe só por esse fallback; o "0 sem controle" vem em parte dele. O título da tabela passa a "aplicações com E calculado pelo v3, inclusive pelo fallback" | Executado, R-C3 |
| E5 | :201 | RX-0: direção "≥ 80 %" em F/M com 2 safras | **Divergência explícita com PED:209 (100 %).** O Claude retira os 80 % como aceite. Valem os 100 % na fixture de referência, para efeitos definidos como "fortes" pelo oráculo antes do ajuste; a taxa em F/M na série de sementes é medida e publicada. Afrouxar só com decisão do proprietário | Por fonte, PED:209; #6227224844 |
| E6 | :41, :202 | "A camada 3 vira a mesma peça do AG-06 e da F1b"; RX-1 "na peça da F1b" | A F1b não autoriza eficácia causal nem estimador de sobrevivência (EX-42:40, :42). O RX-1 é **extensão com contrato próprio**, que reaproveita a peça e a função de domínio da F1b depois de ela integrada | Por fonte; #6227224844 |
| E7 | :215, :217 | D1 e D3: "É dele? Sim" | D1: a DEC-1610-11 desliga o assistente com provedores (PEND-IA-01). O motor é cálculo determinístico (PRD:4744, :9009, :15350): não é pergunta nova, é informação com o custo. A camada 4 segue o PRD:6316 (E4, "mesmos controles"). D3: a promoção já é o fluxo de versão do AG-05 com aprovador técnico (PRD:508-510, :6282; "atualização do protocolo depende de revisão", :6235); quem marca é regra de produto delegada (DEC:134) | Por fonte; #6227224844 |

**Precisão, sem erro:** CL:123 ("nenhuma 'volta' sem leitura abaixo do NC antes") vale na semente original. Nas 20 réplicas há 21 casos (R-C4).

## 6. Completude

### 6.1 Só o Claude viu (o Codex não contestou)

- **Variáveis** (§2 da crítica): hora da vistoria, condição na hora da aplicação, inimigos naturais, NDVI como substituto da falta de água, edição do IRAC/FRAC.
- **Ausente vira média** (`v * 7 / n`, ART:529; `impute`, ART:539).
- **Par de 5 a 10 dias:** perde a revisita de 3 dias perto do NC.
- **Zero-inflação, regressão à média e avaliador das duas leituras.**
- **Resíduo além de 10 dias:** 8, 15, 3 e 8 pares.
- **Leitura do mesmo dia como "antes":** 4/16, 2/16, 1/9 e 1/15.
- **Janela depois e métrica por classe de ação e por tipo de alvo.**
- **Sequência:** não testável com este gerador (1 caso).
- **Campanha sem controle e frase com n = 2.**
- **Ressurgência e vizinhança cortadas.**
- **Faixa testemunha.**
- **Modelo de dados** (fatos, não janelas).
- **Custo de cálculo.**
- **"Fraca" exibe 8,7 % de ruído.**
- **Referência "nível + estádio"** além da persistência 0/1.

### 6.2 Só o Codex viu (o Claude confirmou ou aceitou)

- **Controle lido depois de D** (X-05).
- **Fallback do pareamento** (X-08).
- **ε no HT** (X-09).
- **Censura em D** (X-10).
- **"Associado a"** (X-15).
- **Cinco estados da tela** (X-19).
- **Tempo de disponibilidade e revisão retroativa** (bitemporal).
- **Casos adversariais:** previsão publicada depois da origem, unidade ou protocolo mudados, denominador zero.
- **UX-13 incoerente** (X-30).
- **Job real:** publicação atômica, falha e recuperação, acesso.
- **Escopo da F1b** (X-17).
- **Nulo do p-valor** (X-12).
- **Independência do nulo do clima** (X-14).
- **Contrato do backtest** (X-07).

### 6.3 Nenhum dos dois viu (achados deste confronto, executado)

| # | Achado | Prova | Proposta |
|---|---|---|---|
| N1 | Em D < 86, o "Próximos 7 dias" do detalhe do talhão usa o clima realizado de D + 1 a D + 7 (ART:1024 → rxRisk) | R-C2: até 63,3 p.p. trocando só esse clima | Em data passada, mostrar só fatos, ou o risco calculado com a previsão arquivada daquela data |
| N2 | A irrigação e a adubação realizadas depois da origem entram na janela do risco e do teste (`irrAt`, `ADUB_BY`) | R-C2: +70 mm → +70 na variável; 12 adubações em (72, 79] | Na origem, só manejo realizado até a origem, ou programado e rotulado como tal |
| N3 | A população do teste depende do futuro: o par some se houve aplicação entre as vistorias | R-C2: 731/4.863 excluídos; 213 abaixo do NC na origem | Definir a população na origem; aplicação posterior vira censura rotulada, não exclusão silenciosa |
| N4 | Outra aplicação dentro do seguimento do NC | R-C4: 7/56 e 112/1.193 | Encerrar o seguimento na nova aplicação, marcada como interferência (EX-42:38) |
| N5 | O avaliador usado na linha é o da 2ª leitura (ART:562), o que é informação posterior à origem no teste | Lido. Variável sem efeito plantado; dano pequeno aqui | Na origem, usar o avaliador conhecido até a origem |

**Ainda não testado por ninguém:** tela no navegador (1440/390, teclado), usuários, parecer do RT, servidor, banco e job, magnitude contra o oráculo (o gerador não tem oráculo), gerador com 2 safras e com campanhas, previsões arquivadas reais.

## 7. Pacote mínimo para o Gemini (o envio é do Codex)

Regras do pacote:
- só método, evidência e parâmetros que exigem fonte ou RT;
- dados 100 % sintéticos, do gerador do v3;
- nenhum dado real, nenhum segredo;
- perguntas fechadas;
- as posições dos agentes vêm só do que cada um escreveu.

**Fora do pacote:**
- **janelas, limiares e condição favorável por alvo (a G1 da crítica):** saem do protocolo AG-05, com fonte e adoção do RT (PRD:512; EX-42:38, :44). Perguntar ao Gemini geraria receita agronômica;
- **ressurgência (G5):** sai da F1 (sem efeito plantado);
- **época:** entra na Q1.

**Q1. Nível de evidência dos achados de associação.** Qual regra mínima vale para exibir um achado como Moderada ou Forte?
- **A (PED:136):** ≥ 8 eventos e ≥ 3 talhões para qualquer variável; Fraca exibida.
- **B:**
  - mínimos por tipo de variável:
    - clima: ≥ 6 semanas com a condição e ≥ 6 sem;
    - variável de talhão: ≥ 5 talhões de cada lado;
    - manejo, água e nutrição: ≥ 8 eventos, ≥ 3 talhões e ≥ 4 semanas;
  - só F/M exibidos;
  - Forte só com o mesmo sinal em 2 safras;
  - com 1 safra, no máximo Moderada, com o selo "clima e época se confundem" e o resultado com e sem época.
- **C:** B, com intervalo e nível calculados com a seleção (janela, limiar, representante) refeita em cada treino ou reamostragem e validados em dados separados.
- **Claude:** C (CL:147-157 mais E1 e R-C5). **Codex:** "não classificar Forte só pela reprodução da mesma safra" e validar o procedimento inteiro (CX:25); os números de B são "propostas, não garantia" (#6227224844).
- **Dados sintéticos:**
  - 1 safra de 86 dias, 20 talhões, 12 semanas, 180 a 203 pares por alvo;
  - 14 efeitos plantados e 24 variáveis sem efeito;
  - em 21 sementes: direção em qualquer nível 85 %, em F/M 46 %; ruído em F/M 0,8 %, em qualquer nível 8,7 %;
  - com a seleção refeita: 2 de 14 com IC95 sem o zero.

**Q2. Métrica depois da aplicação.** Na comparação com talhões-controle, que métrica usar por tipo de medida? E a janela "depois" deve ser parâmetro do protocolo por classe de ação do produto?
- **A:**
  - HT clássico (PED:121) para contagem e % de folhas;
  - Abbott sem leitura antes;
  - denominador zero → indisponível;
  - janela fixa de 5 a 14 dias.
- **B:** HT com ε = 5 % do NC, rotulado (como o v3).
- **C:**
  - A para contagem e folhas;
  - para incidência perto da saturação (doença em fruto com protetor), diferença em escala logit ou cloglog, ou área abaixo da curva;
  - presença: não calcular;
  - janela "depois" como parâmetro por classe de ação (lenta × choque), com fonte e adoção do RT.
- **Claude:** C (CL:121-122). **Codex:** ε só com rótulo e método explícitos, sem suavizar denominador inválido (CX:23); ε de 5 % do NC como proposta (#6227224844).
- **Dados sintéticos:**
  - tratado 10 → 5, controles 10 → 10: HT clássico 50,0 %; com ε = 0,5, 47,6 %;
  - tratado 0 → 2, controles 10 → 10: HT clássico indefinido; com ε, −400 %;
  - produtos do gerador: resíduo de 18 dias (IRAC 23) e de 10 dias (IRAC 6). O gerador não planta ação lenta, então essa parte não é testável com ele;
  - contas feitas à mão sobre a fórmula do PED:121 e do ART:631.

**Q3. Seguimento depois da aplicação.** Depois da F1b, o Raio-X pode estimar a duração do controle? Com que método?
- **A:** só as contagens do EX-42 §8:
  - retorno no intervalo entre leituras;
  - 1ª leitura pós acima;
  - seguiu abaixo até a última leitura;
  - sem seguimento;
  - outra aplicação no seguimento.
- **B:** A, mais um estimador com censura por intervalo (Turnbull) a partir de ≥ 20 retornos demonstrados; censura na última leitura elegível; seguimento encerrado por outra aplicação.
- **C:** Kaplan-Meier com dia exato e censura em D (como o v3).
- **Claude:** A agora, B depois (CL:123). **Codex:** censura na última observação elegível; KM convencional não; "método exige decisão específica" (CX:24). Os dois recusam C.
- **Dados sintéticos:**
  - vistorias semanais: retorno sempre num intervalo de 7 dias;
  - censurar em D acrescenta 0 a 6 dias;
  - em 21 sementes: 21 casos de "1ª pós acima" e 112 de 1.193 com outra aplicação no seguimento.

**Q4. Portão da probabilidade em 7 dias.** O portão é prospectivo. Os dois agentes concordam em: origem e horizonte fixos, só dado disponível na origem e previsões arquivadas (CX:22; #6227327207). O Claude acrescenta a população definida na origem (N3). Com esse portão, qual exigência mínima libera a % na tela?
- **A:** vencer a persistência 0/1 no Brier, com ≥ 10 eventos no teste.
- **B:** vencer a persistência 0/1 **e** o nível + estádio, com intervalo do ganho acima de zero e ≥ 20 eventos; sem calibração medida, só ordem e fatores, sem %.
- **C:** B, mais calibração medida por faixa antes de exibir %; 14 dias com aceite próprio.
- **Claude:** C (CL:113, :144-145). **Codex:** validação por horizonte, 14 dias sem herdar o resultado de 7, previsão arquivada avaliada à parte (CX:22, :37, :45; #6227327207). Não há número mínimo escrito por ele.
- **Dados sintéticos:**
  - eventos no teste: 4, 5, 1 e 9;
  - vitórias sobre a persistência em 21 sementes: clima realizado 19, 21, 18, 21; só dados até a origem 2, 4, 18, 21; com metade dos dias certos 13, 19, 20, 21.

**Q5. Aviso de possível perda de resposta.** Quando mostrar "possível perda de resposta; investigar cobertura, pressão e sequência" para um grupo IRAC/FRAC? Nunca é diagnóstico nem ação.
- **A:** nunca automático; só a coluna "posição na sequência", com n.
- **B:** com 1 safra, quando a variação depois da aplicação cai na 2ª aplicação seguida (ou posterior) do mesmo grupo, com ≥ 5 casos por posição e controles válidos.
- **C:** só com 2 safras e ≥ 5 casos por posição, com controles válidos.
- **Claude:** A na F1, C depois (CL:124). **Codex:** o texto do aviso, sem diagnóstico (CX:26); sem número mínimo escrito.
- **Dados sintéticos:** o gerador planta ×0,70 por aplicação seguida do mesmo grupo. Na semente original há só 1 caso com antes e depois (ácaro) e 0 nos demais.

**Q6. Parâmetros dos dados.** Que padrões aceitar?
- **(a) Cobertura da janela:** ≥ 80 %, 100 % ou 60 % dos dias com dado; abaixo disso, "sem dado" naquela variável.
- **(b) ε na taxa r:** 5 % do NC, 1 % do NC, ou escala logit para incidência.
- **(c) Pares:** de 5 a 10 dias (como o v3), ou de 3 a 14 dias com o intervalo como covariável.
- **Claude:** 80 %, 5 % e de 3 a 14 dias (CL:80, :88, :89). **Codex:** 80 % e ε de 5 % "são propostas, não garantia" (#6227224844); ausência ≠ zero (CX:44); sobre (c), sem posição escrita.
- **Dados sintéticos:**
  - o v3 escala a soma da janela por 7/n (ART:529) e imputa a média do NDVI (ART:539);
  - a revisita de 3 dias perto do NC fica fora dos pares de 5 a 10 dias.

## 8. Decisões do proprietário

| Decisão | Situação nas fontes | Recomendação |
|---|---|---|
| **P1. Fonte de clima horário e de previsão com arquivo das previsões emitidas** | Continua com ele: custo, contrato e fonte externa (DEC:135; AGENTS §2; PRD:6308) | **Conjunta:** pedir só com estimativa de custo e fonte. Até lá, camada 4 fora e clima só com a série diária existente (CL:218; CX:22; #6227224844) |
| P2. Faixa testemunha nas O.S. de controle (posterior) | Risco de lavoura e custo; também envolve o RT | **Só do Claude** (CL:219); o Codex não tem posição. Não pedir agora |
| P3. Plano de nuvem do job noturno | Gasto novo, só quando houver software real | Informar a estimativa (CL:221); não é pergunta agora |

**Não pedir de novo:**
- **D1:** a fonte responde (E7);
- **D3:** a fonte responde (E7);
- **D2:** proposta conjunta depois do Gemini; ele confirma no desenho final, porque PED:234 a lista como dele;
- **aceite de 100 %:** mantido; só iria a ele se alguém propusesse afrouxar;
- **teste com usuários:** a DEC-1610-02 já decidiu.

## 9. Fatias: sugestão conjunta (quem registra é o Codex)

**Pré-requisito comum:** EX-42 F1a, F1d e F1b integradas. Teto de 3 frentes, com a q30 primeiro. Nenhuma implantação concorrente (CL:197; CX:39, :53).

| Ordem | Fatia (Claude / Codex) | Conteúdo comum | Aceite mínimo comum |
|---|---|---|---|
| 1 | RX-0 / Fatia 1 | contrato de observação, protocolo e **tempo de disponibilidade**; proveniência; exclusões; gerador com oráculo, 2 safras, campanhas sem controle, sequências e sementes independentes | casos adversariais: controle futuro, revisão retroativa, previsão publicada depois da origem, ausência ≠ zero, protocolo mudado, denominador zero, sem pareamento, censura, e mais N1 a N5; 100 % de direção na fixture (X-03) |
| 2 | RX-1 / Fatia 2 | comparação com controles **sem fallback**, só com dados até D, seguimento do EX-42 §8 e "sem comparação válida"; **extensão com contrato próprio** sobre a peça da F1b | leitura do dia excluída; campanha → "sem comparação válida"; nenhum dado posterior a D muda o resultado; varredura de texto sem "rotacione", "prefira" ou "melhor" |
| 3 | RX-2 / Fatia 3 | associações "associado a aumento/redução", só F/M, sub-detalhe com casos do EX-42, método simples primeiro e seleção validada | regra da Q1; nenhuma cor de estado em dado; tabela equivalente |
| 4 ou 5 | RX-3 / Fatia 5 | marca do RT com autor e data; "Propor revisão" ao AG-05 pelo fluxo de versão | a marca nunca publica |
| 5 ou 4 | RX-4 / Fatia 4 | risco em 7 dias com o portão da Q4 e a previsão arquivada (P1); 14 dias à parte | portão prospectivo da Q4 |

**Divergência de fatiamento (uma só):** a ordem entre a marca do RT e o risco.
- O Claude põe a marca antes (RX-3) e o risco por último (RX-4). Motivos: o risco depende da P1 (custo, do proprietário) e da Q4; o PRD:6316 põe os modelos preditivos em E4; e a AGENTS §3.1 manda preparar só a dependência imediata.
- O Codex manteve a ordem do pedido: risco na fatia 4 e marca na 5 (CX:37-38), sem argumento escrito pela ordem.
- Sugestão: marca antes. A decisão é do Codex.

## 10. Segredos

Gitleaks 8.30.1, com a config `/home/user/Safrion-Software-/.gitleaks.toml` e `--redact`, em 17/10, antes do commit deste confronto:
- `gitleaks dir docs/integracao/V73/RAIOX-ALVO`: ~622 KB, sem achados;
- `gitleaks git --log-opts=b9898643…..HEAD`: 2 commits (f694006, 34e411a), sem achados.

A varredura do intervalo com o commit deste confronto vai no recibo ao coordenador.
