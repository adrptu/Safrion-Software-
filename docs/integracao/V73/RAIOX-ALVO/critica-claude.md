# Raio-X do alvo · crítica independente do Claude (passo 1)

Versão 1 · 16/10/2026 · autor Claude · sem leitura da crítica do Codex · Gemini não consultado nem simulado (as perguntas de domínio estão na §9).
Só leitura e reprodução. Nenhum arquivo de produto foi alterado; nada aqui é decisão final: o Codex registra o desenho e as fatias no checkpoint.

## 0. Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: RAIOX-ALVO passo 1 · crítica do Claude ao pedido "Raio-X do alvo" · agrônomo/RT e gestor no Mapa
Requisitos do PRD e fora do escopo: AG-01, AG-05, AG-06, 15.1, 16.1, 33.8, 33.10, 33.12, 74 (DS-03, DS-16, DS-70); EX-42 · fora: implantação, checkpoint, Gemini
Autor / revisor / integrador: Claude / Codex (crítica própria, em separado) / Codex registra o desenho final
Base (commit ou hashes) / arquivos sob responsabilidade: protótipo b9898643662715a3f7b17bf7797d44e81e5e4a3d; PRD e DECISIONS em origin/main c8274086 (conteúdo igual a 94e19e45); artefato v3 SHA-256 00b5d915221eda4c789ec8f7ee8eeb6e526086815de136ace62e023ef10ed72e; pedido SHA-256 f50d2d5d…485d · arquivos: docs/integracao/V73/RAIOX-ALVO/**
Aceite e comando de verificação: bash docs/integracao/V73/RAIOX-ALVO/reproducao/rodar.sh <HTML do artefato v3> <pasta de saída>
Estado / impedimento / próximo passo: entregue · aguarda a crítica do Codex · divergências por fonte ou reprodução · §9 vai ao Gemini real pelo conector do Codex
```

**Como ler as fontes.** `PRD:n` e `DEC:n` = linha de `docs/PRD.md` e `docs/DECISIONS.md` em origin/main c8274086. `ART:n` = linha do HTML do artefato v3 (versão 1792193012-4fc4, 151.928 bytes; privado, não versionado; lido com a ferramenta Artifact). `EX-42:n`, `MMP:n` (MAPA-MIP-PROD.md) e `gen37/arquivo:n` = arquivos do protótipo em b989864. **Executado** = rodei e a saída está em `reproducao/`; **lido** = leitura, sem execução.

**Insumo do repositório.** O `docs/integracao/V71/insumos/pragas-no-tempo.html` (SHA-256 `8b9e105e…f15`, 94.868 bytes) **não** é o artefato v3: não tem o Raio-X (0 ocorrências de "Raio-X"). É a versão do EX-42. Toda a análise abaixo usa o v3 lido do artefato.

## Resumo: o que eu mudaria e por quê

1. **O "12 de 14" é real, mas conta achado fraco.** Reproduzi exatamente: 12/14, nenhum falso positivo Forte/Moderado, previsão acima da persistência nos 4 alvos (executado). Só que 5 dos 12 são "Fraca", com intervalo de 95 % cruzando o zero (ex.: ácaro, calor achado pela UR com q = 1). Contando só Forte/Moderada: **7/14**. Em 20 outras sementes: 85 % em qualquer nível, **46 %** em Forte/Moderada.
2. **O exemplo-modelo do pedido quase nunca aparece como Forte.** "Dias quentes e secos → +85 % · Forte" saiu Forte/Moderada em 14 de 63 alvo-sementes. Com uma safra, a variação do clima vem de ~12 semanas iguais para a fazenda toda. Proposta: Forte só com 2 safras; antes disso, a referência do protocolo, rotulada "não medido nesta fazenda".
3. **"Fraca" exibe ruído.** 44 de 504 testes de variável sem efeito (8,7 %) apareceram na lista como Fraca; como Forte/Moderada, 4 (0,8 %). Proposta: as listas mostram só Forte e Moderada.
4. **O risco de 7 dias foi testado com o clima que de fato ocorreu** (previsão perfeita, ART:661-664). Sem a previsão, o modelo perde para "repetir a última vistoria" em 19 de 20 sementes no ácaro e na mosca. Contra uma referência probabilística simples (nível de partida + estádio), empata na antracnose (9/20) e na cochonilha (10/20). Proposta: camada 4 por último (E4, PRD:6316), testada com previsões arquivadas.
5. **A camada 3 é o AG-06 e a F1b do EX-42.** Uma solução só, sem "melhor produto", sem "rotacione", com retorno ao NC em intervalo (EX-42:40, :42; PRD:6215, :6225).
6. **Parâmetros saem do protocolo AG-05**, com fonte e adoção do RT: janelas, limiares, condição favorável, métrica de eficácia por tipo de alvo. Sem adoção, "não calculável" (PRD:512; EX-42:38, :44).
7. **Estado da lavoura não é causa.** O NDVI saiu "Forte" no ácaro como substituto da falta de água plantada, que ficou "Fraca". Fica fora do modelo, como já decidido no E10 da MAPA-MIP-PROD (MMP:456, :466).
8. **Design system:** "sobe" em vermelho e "desce" em verde usam cor de estado em dado (DS-16, DS-03). O mapa de correlações pede uma paleta divergente que o capítulo 74.7 não tem. Corto o mapa da F1.
9. **Método:** regressão simples com efeito de talhão e limiar do protocolo, implementada no serviço de domínio em TypeScript. Não GBM+SHAP: ~200 pares por alvo-safra, colinearidade e fuga da stack.

## 1. Aderência

| ID | Decisão | Ponto | Motivo e fonte |
|---|---|---|---|
| C-01 | aceitar | Nada vira recomendação nem O.S.; o motor só calcula e mostra evidência | PRD 15.1 "Calcular" e "Sugerir" (PRD:4744, :4748); 33.8 (PRD:6215) |
| C-02 | cortar | Frases de ação do v3: "Prefira as horas frescas" (ART:1229) e "Sinal de resistência: rotacione o mecanismo de ação" (ART:1232) | Recomendação e diagnóstico de resistência. PRD:6225 ("controle ruim sozinho não confirma resistência"; evitar "trocar grupo em toda aplicação"); EX-42:40. Já apontado em ed8af42 para o HTML do EX-42; o v3 repete |
| C-03 | ajustar | "O que funcionou no controle", ordem por eficácia e a frase "teve a maior eficácia" (ART:1227) | Ranking de potência: PRD:6215 e EX-42:40. Nome "Depois da aplicação · comparado com talhões sem aplicação"; ordem padrão por casos válidos; o usuário pode ordenar a coluna Eficácia (TAB-08) |
| C-04 | ajustar | A camada 3 vira a mesma peça do AG-06 e da F1b do EX-42, com a mesma função de domínio | AG-06 já é "intervenções comparadas com observações posteriores… confiança" (PRD:521-531); EX-42 F1b substitui os links fixos do AG-06 (EX-42:24, :55); ENG-011 (fórmula num único serviço) |
| C-05 | aceitar | Entrada no Mapa › Pragas e doenças, painel ao lado; filtrado no AG-01 e no talhão; sem menu novo | DEC-1610-09 (DEC:111); EX-42:24. Ajuste: no painel do mapa (DS-52), com 2 vistas na F1 (§5), não 4 abas |
| C-06 | ajustar | Cores de "sobe" e "desce" (ART:207: `.up` em `--bad`, `.dn` em `--ok`; barras vermelha e verde) | DS-16 (PRD:14122): paleta de dados não é cor de estado; DS-03 (PRD:13883): verde é ação ou condição favorável confirmada. Texto neutro com ▲/▼ e a palavra; barra em cinza com o intervalo |
| C-07 | cortar (F1) | Mapa de correlações com "cor divergente do design system" | 74.7 (PRD:14616-14716) não tem paleta divergente; criar uma é padrão novo (DEC-1610-12, skill padrao-safrion). Repete o "Quando pesa" do sub-detalhe. Se voltar: tabela TAB-08 com número e sinal, sem cor |
| C-08 | ajustar | Gráficos da curva e da janela | DS-70 (PRD:14725) e 74.7.8 (PRD:14700): nome acessível e tabela equivalente ("Ver dados"); o v3 só tem `aria-label` |
| C-09 | ajustar | Validade da vistoria: 14 dias no v3 (ART:655, :1024, :1270) | 7 dias para MIP e 10 para satélite (EX-42:30; DEC-0910-13 b, DEC:149) |
| C-10 | ajustar | NC único por alvo no v3 (ART:341-361); mosca-branca com NC 5 no v3 e 10 adultos/folha no seed oficial (gen37/dados_mip.py:59) | NC por estádio e unidade da versão válida na observação (EX-42:30; `mipNC`, gen37/mip.js:36). O Raio-X lê a base única de vistorias, não uma simulação própria (PRD 16.1, PRD:4767) |
| C-11 | ajustar | Janelas, limiares e condição favorável fixos no código (ART:490, :320, :354) | AG-05: "Limiares sem fonte/escopo validados ficam inativos" (PRD:512); EX-42:38 e :44. O próprio pedido proíbe (§9). No protótipo, só como "protocolo demonstrativo" declarado (EX-42:38) |
| C-12 | ajustar | "Horas de folha molhada (UR ≥ 90 %)" | EX-42:44: UR não substitui molhamento foliar. Sem sensor ou modelo adotado pelo RT, a variável se chama "horas com UR ≥ 90 %". No v3 o molhamento nem usa a UR (ART:320) |
| C-13 | aceitar | Motor sem IA generativa, frases de modelo preenchidas com números | PRD 15.1 (PRD:4744) e IAG-04 (PRD:15350). Obrigação que decorre: probabilidade só com treino, validação, população e calibração registrados (PRD:6304) |
| C-14 | ajustar | Ordem de entrada | Camada 4 é modelo preditivo de E4 (PRD:6316). O Raio-X é o "posterior" do EX-42 (EX-42:56): começa depois da F1a, F1d e F1b, dentro do teto de 3 frentes (AGENTS §3.6) |
| C-15 | aceitar | Gabarito sintético | Como cenário separado e rotulado, não misturado à base da Lagoa Grande usada pelo AG-01 (PRD:4769) |
| C-16 | ajustar | "Criar vistoria" (rascunho) | Usar a ação que já existe: "Programar vistoria" → FO-03 (PRD:430; já usada no Mapa, gen37/areas/inicio.py:41), herdando talhão, alvo e protocolo. Sem verbo nem "rascunho" novos |
| C-17 | ajustar | Marca do RT guardada no navegador (ART:1080) | No produto: registro no servidor (usuário, data, marca, versão do achado). Promover vira proposta de versão no AG-05 (Criar versão → Validar → Publicar, PRD:510) com aprovador técnico; nunca automático (PRD:6235). As marcas medem o falso positivo por tipo de achado (RF-AI-004, PRD:2715) |

## 2. Variáveis

Situação em b989864 (lido). "Oficial" = base comum do protótipo (gen37); "só no v3" = existe apenas na simulação do artefato.

| Variável | Hoje | De onde vem no real | F1 |
|---|---|---|---|
| Nível do alvo na unidade do protocolo; NC por estádio; tipo NC ou presença | Oficial (gen37/dados_mip.py:36-70; mip.js:36) | AG-01/MB-06 | Sim |
| Pontos, avaliador, coleta parcial, recoleta | Oficial (dados_mip.py:171-175: `npts`, `resp`, `est='coleta'`, `pend`) | MB-06 | Sim, como qualidade: peso e exclusão, não como "fator" |
| Hora da vistoria | Falta (só a data) | MB-06 registra o instante | Sim: sem ela, leitura do dia da aplicação não serve como antes/depois (EX-42:38) |
| Aplicação: produto, dose, área, calda, equipamento, instante | Oficial (O.S. e apontamento; FO-07 tem instante, PRD:2325) | O.S. apontada (EX-38) | Sim |
| Ingrediente ativo e grupo IRAC/FRAC | Oficial: campo `grupos` (agrofit_dados.py:9-10, "IRAC 11.x, FRAC 2024/2025", conferido em 01/10/2026) | Tabela própria por ingrediente, versionada | Sim. Registrar a edição exata: IRAC MoA 11.5 (11/02/2026) e FRAC Code List 2026 (fontes no fim) |
| Clima diário (Tmáx, Tmín, UR, chuva) | Só no v3 (sintético). Oficial: estação com ET₀, chuva e vento (gen37/dados_irrigacao.py:53); Lagoa Grande só ETo demonstrativa (:61) | Estação ou API: integração | Sim, se houver fonte; sem fonte, a camada de clima não calcula |
| Horário: UR ≥ 90 % por hora, DPV horário, molhamento | Falta | Estação horária ou sensor | Não. DPV diário pela média, rotulado como aproximação |
| Condição na hora da aplicação (T, UR, vento, Delta T, chuva até 6 h) | Falta: o FO-07 não tem campo de clima | Cruzar o instante do apontamento com a estação horária; sem digitação | Só "chuva até 1 dia depois", com chuva diária |
| Previsão de 7 a 14 dias | Só no v3 (inventada, ART:311). Oficial: "chuva prevista 48 h", regional (dados_irrigacao.py:60) | Provedor com arquivo das previsões emitidas | Não (camada 4 depois) |
| Irrigação: lâmina, método, suficiência, déficit | Oficial (balanço de dados_irrigacao.py) | IR-* | Sim |
| NDVI, NDRE, NDMI | Oficial (EX-42 dec. 4) | C4 | Como indicador do estado da lavoura, fora do modelo |
| N, K, Ca, B, S aplicados | Oficial nos planos; executado pela O.S./fertirrigação | O.S. apontada | Sim, só o executado |
| Estádio, idade | Oficial (fase) | Safra | Sim, como controle |
| Vizinhança, borda, hospedeira | Calculável da geometria + vistorias | — | Não: anda junto com a tendência da fazenda; exige modelo espacial |
| Inimigos naturais | Falta no seed (o PRD manda registrar, PRD:6217) | Protocolo | Não, até o protocolo registrar |
| Foliar, pH da calda, adjuvante, solo, variedade, radiação, roçada/poda, safra anterior | Poucos casos ou colineares; safra anterior exige 2 safras | — | Não |

**Regras que o v3 quebra** (lido, conferido na reprodução):
- **Ausente vira média.** A soma da chuva da janela é escalada pelos dias com dado (`v * 7 / n`, ART:530): o dia sem dado ganha a média, não "sem dado". O NDVI ausente recebe a média (`impute`, ART:540). Proposta: janela com menos de 80 % dos dias = "sem dado" e o par sai só daquela variável (DS-66, PRD:14721).
- **Presença** (viroses do mamão, dados_mip.py:65): o ln não se aplica. Fora da F1, ou resposta própria (aparecimento sim/não).
- **Vistoria parcial** (`est='coleta'`, `pend`): fora do cálculo; recoleta entra só com os pontos válidos.

## 3. Método

### 3.1 Resposta

- **Aceitar** r = ln((y2 + ε) ÷ (y1 + ε)) × 7 ÷ dias, ε = 5 % do NC, para contagem e percentual baixo. **Gemini:** para incidência perto da saturação, usar logit ou cloglog, comuns em epidemiologia de doença (Madden, Hughes e van den Bosch, 2007).
- **Ajustar: viés de seleção da vistoria mais frequente.** O v3 só aceita pares de 5 a 10 dias (ART:562). O protocolo manda revisitar em 3 dias quando perto do NC (dados_mip.py:14-15; mip.js:59). Justo quando o alvo está alto, o par some. Proposta: pares de 3 a 14 dias, com o intervalo como covariável, ou o par semanal pulando a revisita.
- **Declarar a zero-inflação.** Pares com y1 < 10 % do NC saem (ART:562). O Raio-X mede crescimento de população instalada, não o aparecimento. A tela diz "a partir de 10 % do NC".
- **Regressão à média.** O controle ln(y1 ÷ NC) fica (ART:567). O erro de amostragem de y1 continua: pesar o par pela precisão (pontos válidos nas duas leituras).
- **Viés do avaliador.** O v3 usa só o avaliador da 2ª leitura (ART:563). Usar o das duas e "mudou de avaliador" como controle.
- **Resíduo.** A exclusão de aplicação é fixa em 10 dias (ART:562); o resíduo plantado chega a 18-20 dias. Executado: 8, 15, 3 e 8 pares "sem aplicação" ainda sob resíduo (2 a 8 %). Proposta: janela de exclusão = período residual do produto, do protocolo.
- **Vazamento.** As janelas terminam na vistoria final do par: serve para explicar. Para prever, a janela entre as vistorias exige previsão (3.5).

### 3.2 Camada 1 (exploração)

- **Aceitar** Spearman parcial e Benjamini-Hochberg só como exploração, fora da primeira camada.
- **Ajustar: escolha sem correção.** O v3 escolhe a janela (corrige × 3, ART:606), o limiar entre 15 quantis (ART:580) e o representante do grupo, e o bootstrap não refaz essas escolhas (ART:597-602). Isso infla o efeito ("maldição do vencedor"). Proposta: limiar do protocolo; o limiar dos dados só aparece como "limiar sugerido, a confirmar"; no job noturno, refazer a escolha dentro de cada reamostragem.
- **Ajustar o piso do p-valor.** O diagnóstico está certo. Mas a aproximação normal com ~12 semanas (os blocos que contam no clima) pode ser otimista. No servidor: B ≥ 2.000 e p = (k + 1) ÷ (B + 1). A normal fica como atalho do protótipo.
- **Aceitar** o bootstrap em blocos de talhão × semana (o "pigeonhole" de Owen, 2007). Para o clima, o n efetivo é o de semanas: daí "Forte só com 2 safras".
- **Ajustar o grupo "anda junto".** Executado: no ácaro, o calor plantado foi representado pela UR, e a tela diria "Umidade do ar faz descer". O rótulo mostra o grupo ("tempo quente e seco: calor, ar seco, UR baixa"); o representante é a variável do protocolo, quando houver.

### 3.3 Camada 2 (modelo explicativo): recomendo um

**Regressão linear com efeito de talhão**, como a do v3 (indicadores de limiar e ridge leve, ART:553), mais:
- intercepto por talhão (aleatório, ou centrar por talhão);
- variável que só muda entre talhões (no simulador, a falta de água, ART:534) comparada entre talhões, com n = número de talhões. No ácaro havia 3 talhões do lado alto: Fraca, e o NDVI levou o crédito como Forte (executado);
- interação só a declarada no protocolo ("quente e seco" já é calor × seca), nunca procurada nos dados.

**Não GBM+SHAP.** Com ~200 pares por alvo-safra ele decora o ruído. O SHAP divide arbitrariamente o efeito entre variáveis colineares, o contrário da lição "anda junto". Exige Python ou biblioteca nativa, fora da stack TypeScript/Node (PRD:5286; seria ADR). E custa ordens de grandeza mais no job (§7).

**Validação temporal:** origem móvel semanal, sem embaralhar. "Só mostra se vencer a persistência" vira: vence a persistência 0/1 **e** o modelo nível + estádio, com intervalo do ganho acima de zero e ≥ 20 eventos no teste.

### 3.4 Camada 3 (efeito das aplicações)

- **Aceitar** Henderson-Tilton (Henderson e Tilton, 1955) e Abbott sem leitura antes (Abbott, 1925), com "sem comparação válida" no lugar do número.
- **Ajustar o controle.** O v3 aceita 2 controles quaisquer com nível ≥ 30 % do tratado e o mesmo "jovem/não jovem" (ART:629-631). Proposta: talhão sem aplicação contra o alvo desde (antes − período residual) até depois; mesma cultura e fase do protocolo; nível antes entre 0,5× e 2× o do tratado; leituras a ±2 dias das do tratado; ≥ 2 talhões distintos.
- **Corrigir a leitura do mesmo dia.** O v3 aceita como "antes" a vistoria do dia da aplicação (ART:402), que na simulação é feita depois dela (ART:380 antes de :398). Executado: 4 de 16 (ácaro), 2 de 16, 1 de 9 e 1 de 15. Sem hora, fora (EX-42:38).
- **Interferência:** outra aplicação entre antes e depois exclui ou marca o par (EX-42:38).
- **Janela depois por modo de ação (Gemini).** Reguladores de crescimento (IRAC 7C, 16, 23) agem devagar; 5 a 14 dias fixos os subestimam frente a um de choque (IRAC 6).
- **Métrica por tipo de alvo (Gemini).** Henderson-Tilton para contagem e folhas infestadas. Para doença em fruto com protetor (antracnose), controle relativo sobre incidência ou área abaixo da curva. Presença: não se aplica.
- **Dias de proteção.** O v3 usa Kaplan-Meier com dia exato (ART:636, :404). O retorno ao NC é um intervalo entre duas leituras, e o EX-42 manda não introduzir estimador de sobrevivência nesta fase (EX-42:42). F1: contagens com intervalo ("voltou entre 14 e 21 dias: n; seguiu abaixo até a última leitura: n; primeira leitura depois já acima: n; sem seguimento: n"). Turnbull (1976) só com ≥ 20 casos. Executado: no v3, nenhuma "volta" sem leitura abaixo do NC antes; a regra pede contraprova dirigida.
- **Sequência e resistência.** Executado: aplicações seguidas do mesmo grupo com antes/depois = 1 (ácaro) e 0 nos demais. O aceite "detecta perda por aplicações seguidas" não é testável com este gerador. F1: só a coluna "posição na sequência" com n. Alerta de investigação (nunca diagnóstico) só com 2 safras e gerador com sequências.
- **Sem controle na vida real.** Executado: 0 aplicações sem controle válido, porque o gerador escalona os gatilhos por talhão. Campanha na fazenda inteira é comum. O gabarito precisa de campanhas, para provar o "sem comparação válida".
- **Frases de comparação com n pequeno.** O v3 publica a frase com n ≥ 2 de cada lado (ART:1228); executado: barra 100 L/ha com n = 2. Aplicar a mesma regra de evidência às frases (EX-42:40: aviso de poucos casos junto ao resultado).
- **Cortar ressurgência da F1.** O gerador não planta o efeito; não há como testar.
- **Testemunha (posterior).** A medida limpa é a faixa sem aplicação. A peça do teste em faixas (MMP:332-337) serve para defensivo (MMP:198). Proposta: "Propor faixa testemunha" na O.S., mantida a aprovação individual; decisão do RT e do proprietário (§7).

### 3.5 Camada 4 (risco)

- **Teste otimista.** O gate do v3 (ART:661-664) treina até D − 21 e testa nas 3 semanas seguintes, mas calcula as variáveis com o clima observado: é previsão perfeita. Compara o Brier com a persistência 0/1, que é uma referência fraca para probabilidade. Eventos no teste: 4, 5, 1 e 9; a antracnose "venceu" com 1 evento.
- **Executado, origem móvel semanal (semente original):**

| Alvo | Casos | Eventos | Modelo | Sem previsão | Nível + estádio | Persistência 0/1 | Taxa-base |
|---|---|---|---|---|---|---|---|
| Ácaro | 84 | 14 | 0,045 | 0,247 | 0,124 | 0,167 | 0,153 |
| Mosca-branca | 90 | 10 | 0,053 | 0,181 | 0,086 | 0,133 | 0,102 |
| Antracnose | 104 | 4 | 0,008 | 0,011 | 0,011 | 0,038 | 0,038 |
| Cochonilha | 92 | 13 | 0,049 | 0,058 | 0,049 | 0,130 | 0,133 |

  Brier, menor é melhor. "Sem previsão" usa as janelas anteriores à 1ª vistoria (aproximação: também desloca a adubação). Em 20 sementes, o modelo vence nível + estádio em 19, 20, 9 e 10; sem previsão, vence a persistência em 1, 1, 16 e 20.
- **Previsão.** v3: inventada (ART:311). Protótipo oficial: só chuva 48 h (dados_irrigacao.py:60). Real: provedor com **arquivo das previsões emitidas**, para o teste honesto. Custo e licença são do proprietário (PRD:6308; AGENTS §2). Validade 12 h (DEC:149).
- **Calibração ±10 p.p.** pede centenas de casos por faixa. Com uma safra, não há. Sem probabilidade até haver; mostrar ordem e fatores, como o v3 já faz quando o teste falha.
- **Cortar 14 dias** até provar com previsões arquivadas.

### 3.6 Nível de evidência (proposta para o Gemini)

- Exibir só **Forte** e **Moderada**. Fraca fica em "Como foi calculado".
- Mínimo por tipo de variável (o "8 eventos e 3 talhões" do pedido vale só para o terceiro tipo):
  - clima (igual para a fazenda): ≥ 6 semanas distintas com a condição e ≥ 6 sem;
  - talhão (constante no talhão): ≥ 5 talhões de cada lado;
  - manejo, água e nutrição (variam no tempo e no talhão): ≥ 8 eventos, ≥ 3 talhões e ≥ 4 semanas.
- **Forte:** intervalo de 95 % sem o zero, q < 0,10 (BH após a correção por janela), mesmo sinal em 2 safras, de acordo com a referência do protocolo. **Moderada:** intervalo e q, com 1 safra ou estável nas duas metades.
- **"A confirmar"** é marca, não nível: contra a referência, aparece só com a marca.
- **Selo** em todo achado de clima com 1 safra: "1 safra: clima e época se confundem".
- **Placebo automático:** refazer com o clima deslocado no tempo; se o efeito com o clima errado for da mesma ordem, o achado não passa de Fraca.

### 3.7 Lições do protótipo

| Lição | Veredito | Evidência (executado) |
|---|---|---|
| Com 1 safra, controlar a época apaga o calor | **Confirmada para o calor; em parte no conjunto** | Calor/ar seco em Forte/Moderada: sem controle 4/21 (ácaro), 7/21 (mosca), 3/21 (cochonilha); com mês 1, 0, 1; com tendência suave 0, 0, 0. No conjunto dos 14 efeitos a perda é pequena: 85 % → 80-81 % (qualquer nível), 47 % → 44 % (F/M). Correção: com 1 safra o calor não fica confiável nem sem o controle. A saída é a referência do protocolo e Forte só com 2 safras |
| Grupos colineares "anda junto" | Confirmada, com ajuste | Representante e rótulo (3.2); NDVI fora do modelo |
| Janela de maior associação × nº de janelas antes do BH | Certa, incompleta | Limiar e representante também são escolhidos sem correção (3.2) |
| Piso do p-valor; usar a normal | Diagnóstico certo; correção diferente no servidor | B ≥ 2.000 e p = (k + 1) ÷ (B + 1) |
| Armadilha aplicações × nível +0,59 | Reproduzida | ρ: ácaro 0,59; mosca 0,22; antracnose 0,72; cochonilha 0,45. Fica como frase de ensino, sem número de "efeito" |
| Chuva forte prevista derruba o risco: precisa da previsão | Confirmada e mais forte | Sem previsão o modelo perde para a persistência em 19/20 sementes no ácaro e na mosca |

## 4. Riscos de conclusão errada (por prioridade)

| # | Risco | Dano | Mitigação |
|---|---|---|---|
| 1 | Achado de clima de 1 safra lido como regra | Pulverização ou irrigação guiada por sazonalidade | Forte só com 2 safras; selo; placebo; referência do protocolo na partida a frio |
| 2 | Eficácia sem controle real ou com leitura do mesmo dia | Trocar um produto bom ou manter um ruim | Regras de controle (3.4); "sem comparação válida"; leitura do dia fora; janela por modo de ação |
| 3 | "Sinal de resistência" com n = 1 | Abandonar um grupo sem motivo | Só suspeita para investigar (PRD:6225), sem frase de ação |
| 4 | Probabilidade de risco testada com previsão perfeita | Falsa segurança; vistoria não programada | Teste com previsões arquivadas; duas referências; ≥ 20 eventos; sem % antes da calibração |
| 5 | Substituto lido como causa (NDVI; irrigação quando o clima falta) | Ação no lugar errado | Estado da lavoura fora do modelo. Executado: com o clima errado, a irrigação virou Forte na mosca e no ácaro |
| 6 | Ausente tratado como média | Efeito inventado | Cobertura mínima de 80 % por janela (§2) |
| 7 | Fraca exibida | 8,7 % de ruído na lista; perda de confiança | Só Forte e Moderada |
| 8 | Limiar escolhido pelos dados | "Acima de 31 °C" errado | Limiar do protocolo; o dos dados como "a confirmar" |
| 9 | Pares filtrados (revisita de 3 dias, y1 < 10 % do NC) | Efeito subestimado, limiar deslocado | Pares de 3 a 14 dias com intervalo como covariável; declarar |
| 10 | Mesmo talhão contado várias vezes | Confiança inflada | Contar talhões distintos; bootstrap por talhão (já apontado em ed8af42) |

## 5. UX

- **Sem jargão na primeira camada.** "semanas-talhão sem controle" (ART:1088) → "semanas sem aplicação". Henderson-Tilton e Kaplan-Meier aparecem no rodapé da aba Controle (ART:1245): vão para "Como foi calculado".
- **Duas ações a partir do mapa.** Lido no código: com a função Pragas e doenças e o alvo já escolhidos, o Raio-X é o painel padrão (0 ações) e a evidência abre em 1. Vindo de outra função: função + alvo + item = 3. O aceite precisa declarar o contexto de partida (EX-42:68).
- **Cortar da tela na F1:** aba Correlações (C-07); aba Risco (3.5); tabela de gabarito (só no teste e no cenário rotulado). Ficam 2 vistas: "Sobe e desce" e "Depois da aplicação".
- **TELA-01** (docs/design-system/diretrizes-ux.md): no topo, o estado em palavras (alvo; base "142 vistorias · 23 talhões · 1 safra"; data do cálculo); a atenção é o achado novo sem marca. O painel é consulta: a primária fica no sub-detalhe, a marca do RT.
- **Acessibilidade.** Nível com palavra e pontos: ok. Cor de estado em dado: C-06. Gráfico sem tabela: C-08. Alvos de 30 a 32 px (ART:233, :65) → 44 px no toque (EX-42:68).
- **"Criar vistoria"** → "Programar vistoria" do AG-01 (C-16).
- **Marca do RT.** Três marcas, com quem e quando; "Não confere" pede o motivo em uma linha, porque vira dado de falso positivo (C-17).

## 6. Cortes e fatias propostas (o Codex decide)

**Pré-requisito:** EX-42 F1a, F1d e F1b integradas (EX-42:50-56). O Raio-X reaproveita o contrato de observações, as séries de água e clima e os pares elegíveis.

| ID | Persona | Entrega | Arquivos prováveis (protótipo) | Aceite observável |
|---|---|---|---|---|
| RX-0 | QA e agrônomo | Gabarito em cenário rotulado: 2 safras, campanhas sem controle, sequências do mesmo grupo, produto lento, placebo de clima. O gerador grava, por par, a contribuição verdadeira de cada fator (oráculo) | `gen37/raiox_gabarito.py` e `gen37/raiox_unit.js` (novos); `dados_mip.py` só leitura | Em ≥ 20 sementes: tabela plantado × achado; efeitos fortes plantados com a direção certa em Forte/Moderada ≥ 80 % (com 2 safras); magnitude dentro do intervalo em ≥ 80 %, contra o oráculo; ruído exibido em qualquer nível ≤ 5 %; aplicação nunca em "faz subir"; nenhuma variável com dado posterior |
| RX-1 | Agrônomo e RT | "Depois da aplicação" na peça da F1b: Henderson-Tilton com controles, "sem comparação válida", retorno ao NC em intervalo, agrupar por produto, grupo, calda e sequência com n, sem ranking | `mip.js` (função única), `areas/inicio.py`, `areas/agronomia.py` (AG-06 vira link vivo) | Com a fixture: leitura do dia excluída com motivo; campanha mostra "sem comparação válida"; ordem padrão por casos; varredura de texto sem "rotacione", "prefira", "melhor" |
| RX-2 | Agrônomo e RT | "Sobe e desce" só Forte/Moderada; sub-detalhe com casos que abrem a linha do tempo do EX-42 na data; "Como foi calculado"; tabela equivalente; partida a frio com a referência rotulada | `raiox.js` (novo, fonte única) ou `mip.js`; `areas/inicio.py` | Contagem de ações a partir do contexto declarado; nenhuma cor de estado em dado (varredura de CSS, como a DS-69); referência mostra "não medido nesta fazenda" |
| RX-3 | RT | Marca do achado e "Propor revisão" ao AG-05, com fonte "dados da fazenda" | `areas/agronomia.py` (AG-05), `mip.js` | Marca persiste com usuário, data e versão; publicar exige aprovador técnico; o achado nunca muda o protocolo sozinho |
| RX-4 | Agrônomo | Risco em 7 dias (E4) | depois de existir previsão com arquivo | Brier melhor que as duas referências, com intervalo; ≥ 20 eventos; calibração medida |

**Cortado da F1:** mapa de correlações, 14 dias, ressurgência, vizinhança, Delta T, pH e adjuvante, alerta de resistência, Kaplan-Meier, GBM+SHAP.

**Modelo de dados (para validar).** Não gravar as janelas numa tabela diária (talhões × dias × variáveis × janelas cresce sem necessidade). Gravar os fatos (clima diário ou horário por fonte, água, eventos de manejo) e calcular as janelas no job noturno. Persistir: o conjunto de análise com hash; os achados (organização, fazenda, alvo, versão do protocolo, variável, janela, limiar e origem do limiar, efeito, intervalo, q, n de eventos, talhões, semanas e safras, nível, marcas "a confirmar" e "1 safra", versão do motor, data de corte); e as marcas do RT em tabela própria. A chave do achado torna o recálculo idempotente (AGENTS §4). No software real: `packages/domain` (função única), `apps/worker` (job), `packages/db`.

## 7. Decisões do proprietário

| Decisão | É dele? | Minha recomendação |
|---|---|---|
| D1. O motor estatístico fica fora do "assistente de IA desligado"? | **Sim**: a DEC-1610-11 (DEC:113; PEND-IA-01, PRD:15385) é dele | Sim, fica fora: é "Calcular/Sugerir" (PRD:4744, :4748), sem provedor externo, sem dado saindo e reprodutível (IAG-04). Mesmo assim, chave liga/desliga por organização (RF-AI-006, PRD:2717) |
| D2. Mínimo de evidência para exibir | **Não necessariamente**: é parâmetro técnico e de domínio, delegado aos agentes com o Gemini (DEC-0910-03), salvo se ele quiser decidir | Regra da 3.6: só Forte/Moderada; mínimos por tipo de variável; Forte com 2 safras |
| D3. Quem marca e quem promove ao protocolo | **Sim**: papéis da organização | Agrônomo e RT marcam; só o RT promove, pelo fluxo de versão do AG-05 com aprovador técnico; o operador não vê as marcas |
| D4 (nova). Fonte de clima horário e previsão com arquivo | **Sim**: gera custo e contrato (AGENTS §2; PRD:6308) | Pedir só com estimativa e fonte. Sem ela: camada 4 fora e clima só com a série diária disponível |
| D5 (nova, posterior). Faixa testemunha nas O.S. de controle | **Sim**, com o RT: risco de lavoura e custo | Opcional, proposta pelo Raio-X quando a eficácia é incerta; nunca para praga quarentenária |

**Custo de cálculo (D1).** Medido (executado): 31 a 65 ms por alvo e data no Node, com ~190 pares, ~14 variáveis em até 3 janelas e 200 reamostras. O custo cresce com pares × variáveis² × reamostras. **Estimativa** para uma fazenda grande: 100 talhões × 30 pares por safra × 3 safras = 9.000 pares; ~20 colunas; 2.000 reamostras. Dá ~1.100 vezes o medido: ~45 s por alvo, ~6 min de CPU por fazenda por noite com 8 alvos, ~3 h de CPU por fazenda por mês. Refazer a seleção dentro do bootstrap pode dobrar. GBM+SHAP com a mesma reamostragem: ordem de horas por fazenda por noite (estimativa). O valor em reais depende do plano de nuvem, ainda não contratado; não estimo sem fonte.

## 8. Reprodução (executado)

**Comando:** `bash docs/integracao/V73/RAIOX-ALVO/reproducao/rodar.sh <HTML do artefato v3> <saída>`. Node v22.22.0, sem navegador. O script extrai do HTML o motor (simulação e camadas 1 a 4, antes do bloco `// estado`) e o `gabaritoRows` da tela, e roda num contexto `vm` isolado. Dois ganchos de uma linha, conferidos (falham se não acharem o texto exato): a semente (réplicas) e o deslocamento do clima só na análise (nulo). Mais um terceiro, para o controle de época. Tempo total: ~30 s. As saídas (`repro.json`, `resumo.txt`, `calor.txt`) são deterministas, salvo os tempos em ms; duas rodadas deram o mesmo resumo.

| Declaração do protótipo (25/09) | Reproduzida? | Medido |
|---|---|---|
| 12 de 14 efeitos plantados recuperados | **Sim, exata** | 12/14. Só Forte/Moderada: 7/14. 20 sementes: 237/280 (85 %); F/M 130/280 (46 %) |
| Nenhum falso positivo Forte ou Moderado | **Sim, nesta semente** | 0/24. 20 sementes: 4/480 (0,8 %). Exibido em qualquer nível, contando a semente original: 44/504 (8,7 %) |
| Previsão melhor que a persistência nos 4 alvos | **Sim** | Brier modelo × persistência: 0,059 × 0,161; 0,044 × 0,136; 0,003 × 0,020; 0,044 × 0,216; eventos no teste 4, 5, 1 e 9. 20 sementes: 75/80. Mas com clima perfeito (3.5) |
| Armadilha +0,59 | **Sim** | Ácaro 0,59 |
| ~20 ms por data | **Não conferido** (sem navegador) | Node: 31-65 ms por alvo e data |

**Camada 3 na semente original** (eficácia mediana com a condição × sem ela; entre parênteses, aplicações com controle válido):

| Condição plantada | Ácaro | Mosca-branca | Antracnose | Cochonilha |
|---|---|---|---|---|
| Dia quente e seco (×0,78) | 57 % (6) × 80 % (10) | 63 % (4) × 76 % (12) | 47 % (6) × 53 % (3) | 62 % (6) × 62 % (9) |
| Chuva até 1 dia depois (×0,70) | 49 % (3) × 78 % (13) | 74 % (3) × 71 % (13) | 53 % (1) × 47 % (8) | 47 % (2) × 64 % (13) |
| Barra 100 L/ha (cobertura 60 %) | 46 % (2) × 78 % (14) | 51 % (2) × 74 % (14) | 6 % (1) × 50 % (8) | 30 % (2) × 64 % (13) |
| Mesmo grupo seguido (×0,70) | 0,5 % (1) × 78 % (15) | — (0) | — (0) | — (0) |

A direção aparece em parte, sempre com n de 1 a 6 de um lado: nenhuma dessas diferenças passaria na regra da 3.6.

**Contraprovas além do pedido (executado):**
- **Nulo do clima:** clima deslocado 21, 35, 49 e 63 dias só na análise. 18 achados de clima falsos exibidos em 16 alvo-rodadas, 1 deles Forte; com tendência suave, 16 (1 Forte). Com o clima errado, a irrigação virou Forte na mosca (deslocamento 35) e no ácaro (35, 49).
- **Resíduo:** 8, 15, 3 e 8 pares "sem aplicação" ainda sob resíduo.
- **Leitura do mesmo dia como "antes":** 4/16, 2/16, 1/9, 1/15.

**Limites.** O gerador fixa os dias de chuva e as ondas de calor (`RAINMM` e `wave`): as réplicas variam só o ruído. O "sem previsão" é aproximação. Não abri a tela. A magnitude contra o plantado **não foi medida**: o v3 não define o efeito verdadeiro de "≥ limiar" para um multiplicador diário plantado. Por isso o RX-0 pede o oráculo no gerador.

## 9. Perguntas de domínio para o Gemini (pacote mínimo, sem dados reais; não simulado)

- **G1. Janelas e limiares por alvo** (mamão: ácaro-rajado, mosca-branca, antracnose, cochonilha; 1 alvo de grão): condição favorável (≥ 32 °C e UR < 50 % para ácaro?), janelas (0-7, 8-14, 15-28 dias?), temperatura-base dos graus-dia, e se "horas com UR ≥ 90 %" serve de substituto do molhamento na antracnose do mamão.
- **G2. Métrica de eficácia por tipo de alvo e janela depois por modo de ação**: Henderson-Tilton em contagem e folhas infestadas; doença em fruto com protetor; reguladores de crescimento (IRAC 7C, 16, 23) × choque (IRAC 6).
- **G3. Regra do nível de evidência** da 3.6: mínimos por tipo de variável e Forte só com 2 safras.
- **G4. Resistência**: o que conta como sinal para investigar (queda na sequência dentro da safra × entre safras), com que n mínimo.
- **G5. Ressurgência**: quais pares grupo × alvo vale testar depois (ex.: piretroide e ácaro), ou cortar.

## Fontes externas (consultadas em 16/10/2026)

- IRAC, "Latest updates to the MoA Classification (version 11.5)", 11/02/2026: https://irac-online.org/?p=16706
- FRAC, "FRAC Code List ® 2026", página de publicações, sem data de publicação: https://www.frac.info/publications
- Referências clássicas, citadas de memória (volume e página a conferir antes de entrar em tela ou no PRD): Abbott (1925), J. Econ. Entomol. 18:265-267; Henderson e Tilton (1955), J. Econ. Entomol. 48:157-161; Benjamini e Hochberg (1995), J. R. Stat. Soc. B 57:289-300; Owen (2007), "The pigeonhole bootstrap", Ann. Appl. Stat. 1:386-411; Brier (1950), Mon. Weather Rev. 78:1-3; Turnbull (1976), J. R. Stat. Soc. B 38:290-295; Madden, Hughes e van den Bosch (2007), *The Study of Plant Disease Epidemics*, APS Press.
