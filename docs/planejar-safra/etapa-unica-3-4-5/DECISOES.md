# Decisões · Planejar safra, etapa única (v2)

Companheiro de [ESPECIFICACAO.md](ESPECIFICACAO.md). Os "§" citados são dessa especificação. "v1:N" é a linha N da especificação anterior (`saf345/especificacao.md`).

## 1. Assumi

Decisões técnicas e de produto delegadas aos agentes; o Codex revisa.

- **Nome e verbo.** "Dimensione operações e recursos" usa o verbo do PRD (UX-01, "Dimensione recursos") e nomeia o que a etapa ajusta.
- **Topo em três peças:** veredito, atalhos de capacidade e custo de operação. Não há faixa de indicadores. O veredito é o único lugar de "cabe", do que falta e do que ficou fora da conta.
- **Ordem do veredito:** decisão → "Fora da conta" → prazo. O que fica fora muda a decisão; a janela vazia só a qualifica.
- **`g_cap` recolhida em qualquer largura**, com uma ordem só no DOM e sem regra por largura. Ao abrir, entra na vista (`scrollIntoView`). Medido em simulação: aberta por padrão, sobra 1 linha da `g_op` a 1280 × 800 (§2.1).
- **Atalhos saem enquanto a grade está aberta.** Sem isso, o mesmo % apareceria 3 vezes: no atalho, na coluna Maior uso e na célula.
- **Custo de operação na linha do título**, com o qualificador sempre visível (exceção à regra antiga de esconder qualificador abaixo de 400 px). Na simulação, isso recupera uma linha da `g_op` a 1366 × 768 em relação a pôr o custo na linha dos atalhos.
- **`outrasSafras` vazio quando a própria safra está encerrada.** A S2526 não divide recursos com as abertas: a `g_cap` dela fica toda "—". O predicado de safra.js:344 só fala das outras safras; este caso é escolha minha.
- **Maior uso conta toda célula em que esta safra tem demanda,** mesmo pequena. Na S27SF, Operadores dá 42 % em mai/27, com 4,40 h dela e 651,43 h da S2627. É o uso real da equipe num mês em que a Safrinha trabalha.
- **Linha filha não repete o estado de janela do pai.** Chips de problema aparecem sempre.
- **Texto do R3:** "Cálculo incompleto: <operação> com <N ha sem conjunto | N ocorrências pendentes (causa)>".
- **Prévia nomeia "operação · conjunto"** de quem deixa ou volta a trabalhar, a partir do motivo de safra.js:65.
- **Toques na `g_cap`:** Recurso, Maior uso e Mês abrem o formulário; só as células de mês filtram (P12 adaptado às colunas novas).
- **Unidade ha-op.** Fica na célula; os cabeçalhos "Área trabalhada" e "Custo R$/ha" são escolha do proprietário (RETOMADA-NUVEM.md:202).
- **Ordem dos PRs** (§10): PR 1 e PR 2a antes da cadeia; PR 3 ainda com 6 etapas; PR 4 com a renumeração. Assim `acao_unica` e `etapas_celular` mudam uma vez só e não existe etapa provisória.
- **`g_cap` sem filtro nem ordenação no cabeçalho** (exceção registrada à regra "toda tabela com filtro e ordenação", revisão SAF de 06/10/2026, S4). É uma matriz de 6 recursos × meses, de leitura: a coluna Maior uso já é a ordenação útil, e o filtro é o toque na célula, que filtra a `g_op` pelo recurso e pelo mês (§3.3). Cabeçalho com ferramentas em 15 colunas tiraria a linha de dados que a `g_op` precisa a 1280 × 800 (§2.1). Volta quando o G2 ganhar navegação por setas ou se o proprietário pedir.
- **Meses da `g_cap` pelos dados** (revisão SAF, S3.1): os do calendário dentro do período da safra (`capMeses`), sem lista fixa por safra. Como a demanda desta safra fora do período não conta na capacidade, nenhum mês com demanda dela fica fora da grade. Verificação SAF-C02: toda `g_cap` nasce com o calendário inteiro e `capMeses` recorta pelo período gravado; antes as safras fixas ficavam com as colunas do build e, com o mesmo período, as duas vistas mostravam meses diferentes.
- **Capacidade simétrica entre safras abertas** (SAF-C02, achado e decisão proposta pelo Codex em 09/10/2026, aplicada): `capSaf` recebe o período de cada outra safra e etiqueta cada ocorrência pela safra de origem; fato, custo e datas ficam, e a carga de fora aparece no veredito, no filtro e no `aria-label`. Evita total do mês dependente da safra aberta (340 h × 140 h no harness) e verde enganoso. **R5 → R4 é esperado** quando há carga de outra safra fora da conta num recurso × mês com demanda desta, mesmo que somada ela ainda caiba (verificação SAF-C02, S2627 até 30/06/2027: a S27SF passa de verde a amarelo citando 25,3 h): é o que a decisão pede e a mesma regra da ocorrência fora da própria safra; a alternativa "só tira o verde se somada desse falta" fica para o Codex decidir se o amarelo virar ruído.
- **IDs de teste renumerados na v2:** C1–C24, N1–N7, O1–O19, V1–V14, L1–L4, P1–P8, M1. O mapa de cada achado está na seção 5.

## 2. Cortei

- **Do produto:** a lista do §6 da especificação.
- **Da proposta v1:**
  - a faixa de 4 indicadores;
  - as colunas Unidades e "Horas na safra" da `g_cap`;
  - o negrito na maior célula;
  - a abertura da `g_cap` rolada até o mês de maior uso;
  - "Atende" em verde;
  - trio, motivos e decorrido na coluna Situação;
  - o selo `v.aj` como Origem;
  - a "Memória";
  - a etapa 3 provisória do PR 2;
  - o texto "com a demanda atual" da prévia.
- **Propostas dos revisores que recusei** (com fundamento):
  - chip "prazo não informado" em cada linha e 3º botão "Sem prazo": pegariam 100 % das linhas nas 4 safras (P01, MN-07);
  - veredito cinza "R5b" quando falta janela (R-02): ficaria cinza para sempre, porque nenhuma safra tem janela, e o alerta viraria ruído (AGENTS §4); a ressalva vai no texto;
  - `g_cap` que abre sozinha no vermelho e página que rola abaixo de 900 px (P03);
  - colunas em R$, R$/ha só no formulário e valores sem centavos (P06, já recusados na verificação);
  - rótulos "Custo R$/ha trabalhado" e "ha trabalhados" (P06), em favor da unidade "ha-op" na célula (R-06);
  - rótulo dinâmico "Todas as N atividades em uso" (MN-04);
  - copiar a janela no "Todas" (MN-05): mudar a regra é do Codex, dono do oráculo D-01;
  - `data-noedit` como atributo (P12);
  - abrir o formulário do recurso só pelo nome (P12).

## 3. Parâmetros do dono, com padrão

Só perguntas da realidade da fazenda. Até a resposta vale o comportamento conservador (`docs/DECISIONS.md:29`). O padrão roda só no protótipo de desenvolvimento, como proposta.

| ID | Pergunta (uma linha, com captura) | Padrão até a resposta | Se a resposta for outra |
|---|---|---|---|
| **PEND-SAF-01 (P2)** | "Na tabela de operações bastam o rendimento (ha/h) e o Custo R$/ha, com largura, velocidade, eficiência, custo por hora e R$/kg ao tocar na operação? Isso muda a sua decisão de 26/09 (DEC-2609-03). [Sim] [Manter na tabela]" | formulário (§4.1); `g_rend_*` continua no corpo até a resposta (PR 4, commit i) | as 5 colunas voltam na linha da operação, e a tabela passa das 7 colunas úteis (PRD.md:287). "Configuráveis" exige componente novo, porque o G2 não esconde colunas: vira fatia própria |
| **PEND-SAF-02 (P1)** | "Você usa o custo da safra mês a mês nesta tela (para o caixa), ou basta o total por cultura?" | sai do Planejar safra (PR 4, commit ii); continua exigido no orçamento (PRD 44.5 e 44.6, PRD.md:7192, :7196) | custo por mês ganha desenho próprio, sem voltar como terceira grade do bloco |
| **P3** | "As duas fazendas dividem máquinas e pessoas?" | cada fazenda soma as suas safras abertas (§3.3); o cadastro único é limite do protótipo | muda só `outrasSafras`. A S2627 passa a receber a carga da LG2627: Operadores de nov/26 iriam a (73,74 + 23.613,86) ÷ 1.490,40 = 1.589 % (calculado com C5 e a base) |

**Quando perguntar:** já, na issue 1, junto com o pedido de registro. As perguntas não dependem de código (R-01). Se não houver resposta, repetir na homologação com a captura antes (`saf3-1440.png`) e a depois (P09).

## 4. Pendente

**Codex · registrar (antes do PR 4), em três partes:**

(a) **DEC-0510-xx, só o que o proprietário pediu.** Texto proposto, que não é aprovação do proprietário:
> "DEC-0510-xx · Planejar safra em 4 etapas. Pedido do proprietário (Adrianus, chat, 05/10/2026): «Integre a etapa 3, 4 e 5 numa só fazendo um UX e UI mais inteligente, simples e intuitivo possível. Elimine duplicidades dados menos relevantes e foque no mais essencial que gera valor real na gestão operacional da safra.» Regra: as etapas 3, 4 e 5 viram a etapa 3, 'Dimensione operações e recursos', e a demanda de insumos passa a ser a etapa 4. Ajustes de numeração: UX-01, título, Melhoria e Etapas (PRD.md:11728, :11736, :11742); 71.6 Planejamento (:10361); 52.1 'A etapa 3' (:8241); DEC-2609-09 '(etapa 5)' (:12223); AC-72-03 'etapas 4 a 6' → 'etapas 3 e 4' (:12243); fluxogramas v3_9 do UX-01 e do FL-AG-08; endereço por nome (`passo=`), com `etapa=N` antigo lido na numeração de 6. Colunas do rendimento: PEND-SAF-01. Custo por mês: PEND-SAF-02. O passo 'Publique plano' do FL-AG-08 fica pendente, não removido."

(b) **Proposta dos agentes que responde ao pedido**, com aceite do proprietário na homologação. Não usar o rótulo "pedido do proprietário".
- O que propõe: topo com veredito, atalhos e custo; `g_cap` (recurso × mês, ocupação); `g_op` com 8 colunas.
- Frases do PRD que caem, citadas uma a uma:
  - UX-01, "Plano e dimensionamento usam indicadores nas linhas e meses nas colunas" (PRD.md:11738);
  - 71.6 Plano e recursos, "Uma matriz por atividade/recurso, com indicadores nas linhas e meses nas colunas; total do período, expansão e origem" (PRD.md:10365). A origem passa ao toque na célula.

(c) **PEND-SAF-01 e PEND-SAF-02** em "Decisões pendentes do proprietário" (`docs/DECISIONS.md:27`), com o texto da seção 3.

**Codex · confirmar severidades (PRD 22.1)**, para nenhuma versão sair com S2 conhecido:
- **Candidatas a S2:**
  - R$/ha com denominador misto ("R$ 1.427,61/ha da safra");
  - falso verde com 475 ha (41 %) fora;
  - falso verde sem janela (R-02, P01);
  - falta de recurso escondida nas pendentes sem recurso: na LG2627, Tratores de out/26 aparecem com 57 % hoje e são 234 % (MN-01, R-07);
  - prévia do recurso diferente do resultado salvo (MN-02);
  - capacidade só da safra aberta, sem as outras da fazenda (P02);
  - custo de operação com 60 % de antes da safra sem aviso (MN-03);
  - R$/ha da cultura com R$ 0 nas pendentes (R-12).
- **S3:** "Mês do pico"; links da Compra sem mapeamento; ha-op sem unidade (R-06); "Todas" em atividades invisíveis (MN-04, R-09); janela perdida em "Todas" (MN-05); Origem falsa (MN-06); filtro que não fecha (MN-08); números na Situação (R-08).
- **S4:** recursos editáveis na S2526 (R-11); limiar "<1 %" (MN-11); rótulo do R$/ha (P06); toques na `g_cap` (P12).
- **Item 10 do CONTROLE-01** (`pce/verificada.md:202`): decide se o CONTROLE-01 entra antes da homologação (§10).

**Codex · decidir a Regra A:** ocorrências antes do início, depois do fim ou fora do calendário (FORA-DE-ESCOPO.md).

**Integração da cadeia #36–#44** (impedimento 1, §0.1).

**Registrar as 5 referências do setor** num arquivo do módulo (R-004 §3.1).

## 5. Revisão aplicada

Os 33 achados confirmados. Números refeitos com o motor real em `scratchpad/v2calc/`.

| ID | Grav. | O que mudou | Onde | Ajuste ou conflito |
|---|---|---|---|---|
| MN-01 | alta | Pendente "sem recurso na fazenda" entra na demanda pelo necessário. Necessárias = max(teto, maior equipe). Célula vermelha "precisa N"; nunca "—" com pendente. R2 dispara. LG2627: 127 em nov/26, 9 meses; Tratores 10 em out/26, 4 meses | §3.1, §3.3, §3.5, §4.2; C5, C6, C12, C16, V8, V13 | A demanda segue o R-07 (`x.nh` para toda causa com horas), que contém a do MN-01; nos dados de hoje os números são iguais. A regra de necessárias segue o MN-01 (geral), mais ampla que a do R-07 (só com semRec) |
| MN-02 | alta | A prévia recalcula `repartir` com os pools do rascunho, só nas ocorrências que usam o recurso, e diz quem deixa ou volta a trabalhar. Nota fixa nova; o espelho recebe `recursos` | §4.2; C10–C15; P1–P3 | Com o MN-01, Operadores 8 → 5 dá 67 % em vermelho antes e depois de salvar; saem "mai/27 —" e o negativo "nunca 67 %". Operadores 0: "não calculável · precisa N", não "—". Tratores 4 → 5 passa a 27 % → 22 % (P02) |
| MN-03 | alta | Uma etiqueta por ocorrência (antes do início, fora do calendário, depois do fim); Data com a faixa real; custo com "inclui R$ 919.906,51 de antes de 01/09/2026"; Resumo com Y e Z; Regra A sem depender de calendário | §3.2, §3.4, §4.3, §7; O19; FORA | "75 ocorrências antes do início" fica só no veredito (P05), e o custo não repete o 75. O R$/ha do Mamão na LG2627 fica "parcial" (R-12), não R$ 4.072,16 |
| MN-04 | média | "Todas" só nas atividades em uso (`atvEmUso`); aviso "(6 atividades)"; ajuda nova | §4.1; O9, O10 | O item `aj = true` foi substituído pela Origem calculada (MN-06). REND 4a-c não cobria o caso (v1:509) |
| MN-05 | média | Janela em duas entradas com conds exclusivas; `jan_op` só leitura em "Todas"; guarda em `rendCheck`; ajuda fiel à lista de cópia; conta por atividade | §4.1, §3.1; O8, O11 | O O25 do P01 (janela pela operação) deixa de existir: em "Todas" a janela não é editável |
| MN-06 | média | Origem calculada por `origemCfg` contra o CD-02; não lê `v.aj` | §4.1; O13 | Executado: 42 de 43 padrão na S2627 (o prestador é "Ajustado"); 42 de 42 nas outras safras; depois do "Todas" na Pulverização, 6 ajustadas e 8 padrão |
| MN-07 | média | Sem janela, a Situação não fica verde; o veredito conta o que não foi verificado | §3.1, §3.4; O4–O7 | Rótulos e contagem conciliados com P01, R-02 e P07 (seção 6) |
| MN-08 | média | No filtro, a 7ª coluna vira "Horas de <recurso>" (`cargaRec`), com "não usa" e Total que fecha; limpa `f.horas`; linha de filtro igual para pessoas, com "precisa de N, tem M" | §3.5; C21; V4–V7 | `cargaRec` usa `x.nh` (MN-01, R-07), não `i.horas × i.rec` |
| MN-09 | baixa | `plano_op` e `capacidade` com `planos` e `cfg_override`; derivação igual ao `rendAfter`; O9 e O20 calculados | §0.3, §10; C22 | `'*'` também respeita as atividades em uso (MN-04) |
| MN-10 | baixa | Tabela de totais sem "—"; duas colunas de horas de pessoas; notas | §7; C4, C24 | A coluna do calendário passou a ser demanda (MN-01): LG2627 86.839,80 h. As 15.351,14 h atendidas ficam no Resumo |
| MN-11 | baixa | `fmtOcup`: "<1 %" quando 0 < o < 1 %; função única | §3.3; C20, V3 | O negrito saiu (P04); o par de células virou C20 |
| P01 | alta | Três estados com cor e texto; não repetir o pai; testes | §3.4; O4–O7 | Sem 3º botão; contagem no veredito, porque o indicador Pendências saiu (P05); rótulos "Janela não informada" e "Cabe na janela" |
| P02 | alta | `outrasSafras` (abertas, mesma fazenda); célula cinza; linha de filtro com a divisão; veredito "somando…"; subtítulo do recurso; P3 com padrão | §3.1, §3.3, §3.5, §4.2; C2, C7, C17–C19; V6, V12 | Safra encerrada não soma outras (assumido). Tratores fev/27 vai a 27 %; Operadores fev/27 a 31 % |
| P03 | alta | `g_cap` recolhida; atalhos no topo; nunca abre sozinha; L1 conta as linhas da `g_op` | §2, §3.2; L1 | Medido de novo com o topo da v2 (veredito mais longo): 1280 × 800 mostra as 8 operações, mas não o Total. Custo e Resumo foram para a linha do título; o aceite segue o medido |
| P04 | média | Colunas Maior uso e Mês; Unidades sai da grade; sem negrito; sem abertura rolada; Resumo como link; L2 | §3.3, §3.2; V3, L2 | A `g_cap` vem recolhida (P03) e entra na vista ao abrir. "Horas na safra" também sai (P10). Saem todos os indicadores (P05), não só um. Simulação: sem o limite de 45 %, a coluna Mês corta 15 px a 390 |
| P05 | média | Sem faixa de indicadores; veredito como único lugar; "Fora da conta"; área de ações só com o atalho; V2 | §3.1, §3.2, §5.2; V2 | O custo de operação fica sozinho na linha do título e não é botão |
| P06 | baixa | Total no quadro do Resumo; 2 casas em toda a etapa; nota sem número repetido; "Como a conta é feita" explica ha-op | §4.3 | Rótulos "R$/ha trabalhado" e "ha trabalhados" substituídos pela unidade ha-op do R-06 |
| P07 | média | "Na estimativa mensal, " em R4 e R5; frase do prazo; sem link novo; testes | §3.1; V1, V12, O7 | Contagem por atividade (R-02, MN-05) |
| P09 | média | DEC-0510 reduzida; PEND-SAF-01; pergunta com capturas | seções 3 e 4; §10 | Somado ao R-01: perguntar já e repetir na homologação |
| P10 | baixa | Base da matriz declarada; meses do período da safra; "Horas na safra" vai ao formulário; sem rolagem lateral a 1280 | §3.3, §4.2; V3 | Unidades também sai (P04). Maior uso só com o % e Mês em coluna própria; simulação a 1280: 956 = 956 px |
| P11 | baixa | Coordenação com saf2 (ordem de lá; reserva por função); `proxSaf`; área com plano = `cultRows` − `semPlano`; V10 só fev/27 | §0.3, §5.2, §5.4; V10 | O indicador saiu (P05); a área com plano fica no veredito, com a mesma base da faixa "Nesta safra" |
| P12 | baixa | `g2nr`; `act` com `full`; "—" inerte; V14 | §3.3; V14 | As colunas que abrem o formulário são Recurso, Maior uso e Mês (P04, P10) |
| R-01 | alta | Registro em três partes; frases do PRD que caem nomeadas; remoções que dependem de P1 e P2 em commits reversíveis | seção 4; §0.1, §10 | A divisão 3a/3b virou "PR 3 sem remoções + commits do PR 4", por causa da ordem do R-03 |
| R-02 | alta | "Cabe na janela" e "Janela não informada"; contagem por atividade; casos com janela | §3.1, §3.4; O4–O7 | Sem janela, o R5 continua verde e a ressalva vai no texto (MN-07, P01, P07), em vez de cinza |
| R-03 | alta | Impedimento da cadeia; PR 2a; sem etapa provisória; renumeração no PR 4 | §0.1, §10 | Executado: `gh api` (cadeia em rascunho) e `merge-base` (não ancestral) |
| R-05 | média | Ordem com o CONTROLE-01; literais de demanda viram paridade; capacidade do plano sem descontar o realizado; "Publicar versão" no fora de escopo | §7, §10; FORA | Executado: 20,84 h do Fungicida 1ª aplicação (T1-B e T2) nos 49,07 h de Pulverizadores em dez/26 |
| R-06 | média | ha-op na operação, ha nos demais níveis; guarda; Resumo com "ha-op (hectares-operação)" | §3.4, §4.3; O2 | Escolhido no lugar dos rótulos do P06 |
| R-07 | média | Demanda com `x.h + x.fh`; "≥" onde falta medida; R2 com "Inclui N ocorrências…"; Tratores da LG2627 em falta | §3.1, §3.3; C5 | O texto das pendências foi para o veredito (sem o indicador) |
| R-08 | média | Situação só com chips; "Neste talhão" e "Nesta configuração" no formulário; B2b–d e B5a leem o formulário | §3.4, §4.1, §9.3; O3 | — |
| R-09 | média | `atvEmUso` como fonte única do "N atividades" e do alcance do "Todas"; contagens nos testes | §3.4, §4.1; O9 | O item `aj` foi substituído pelo MN-06 |
| R-10 | média | `cadc_cd0102_b` registrado como já vermelho; paridade CD-02 em O17; suprimentos.py:489 e safra.js:845; N4a e N4b; guardas estáticos; texto da origem gravada | §5.3, §9.3; N4a, N4b, N7, O17 | Executado: `cadc_cd0102_b.py` falha na linha 27 (RuntimeError) na base; guardas acham 2 e 14 linhas hoje |
| R-11 | baixa | Fundamento (PRD 52.1) e dano corretos; S4; subtítulo "Para ajustar, abra uma safra aberta." | §4.2; V11 | — |
| R-12 | baixa | `resumoCultura` e `dados2.resumo_cultura`; denominador declarado; "parcial" com pendente; casos de ajuste | §4.3, §7; C23; P4–P6 | O `cult.py` deixa de ser oráculo |

## 6. Conflitos entre achados e como resolvi

1. **Situação e janela (MN-07, P01, R-02, P07).**
   - Estados: "Com pendência", "Janela não informada" (R-02, mais claro que "Sem prazo") e "Cabe na janela" (MN-07, R-02).
   - A contagem vai no veredito, por atividade (R-02, MN-05), porque o indicador Pendências do P01 saiu (P05).
   - A cor do R5 não muda (MN-07, P01, P07), em vez do cinza do R-02.
   - O filtro rápido sai dos valores de `s.sit` (R-02), sem 3º botão fixo (P01, MN-07).
2. **Demanda sem alocação (MN-01 × R-07).** Adotei `x.nh` para toda causa com horas calculáveis (R-07, PRD 53.2 "não truncar déficit"). As necessárias seguem a regra geral do MN-01. Nos 4 conjuntos de dados os números coincidem.
3. **Indicadores (P03, P04, P05, P01, MN-03).** Sai a faixa inteira (P03, P05). O custo de operação fica sozinho na linha do título, com o qualificador do MN-03.
4. **Colunas da `g_cap` (P04 × P10).** Ficam Recurso, Maior uso e Mês e os meses. Unidades vai para formulário, filtro, `aria-label` e veredito (P04); "Horas na safra" vai para o formulário (P10). Simulação: cabe a 1280 sem rolagem lateral.
5. **Grade visível ou recolhida (P03 × P04/P05).** Recolhida em todas as larguras. O L2 do celular mede depois de abrir, com `scrollIntoView`.
6. **Unidade do R$/ha (P06 × R-06).** Fica a unidade "ha-op" na célula da operação e o cabeçalho do proprietário. Do P06 ficam o Total no Resumo, as 2 casas e a explicação.
7. **Origem (MN-04/R-09 item 3 × MN-06).** A Origem calculada torna o `aj` desnecessário; o `rendAfter` muda só o alcance do "Todas".
8. **Operadores 8 → 5 (MN-02 × MN-01).** Vale o MN-01: 67 % em vermelho, igual antes e depois de salvar.
9. **Ordem dos PRs (R-03 × R-01 × P09).** PR 1 e 2a antes da cadeia; PR 3 sem remoções; PR 4 com a renumeração e as remoções em commits reversíveis que esperam P1 e P2.
10. **Fora da conta × custo (P05 × MN-03).** O número de ocorrências antes do início fica no veredito; o custo diz o valor e a data.
11. **R$/ha do Mamão na LG2627 (MN-03 × R-12).** Fica "parcial · 56 ocorrências pendentes" (R-12); o qualificador de antes do início continua (MN-03).

## 7. Ressalvas da verificação que mudaram a especificação

- **Etiqueta × realizado.** "Antes do início da safra" e "já realizado" são cortes diferentes. Na LG2627, 8 ocorrências de 01 a 22/09/2026 estão dentro da safra e antes de hoje: R$ 4.662,28 de operação e R$ 63.518,90 de insumos (executado). Elas contam em set/26. Por isso o Resumo usa "antes de hoje" só para os insumos (Y) e "antes do início" para as 75.
- **Arredondamento da nota.** A demanda bruta da LG2627 é 1.846.704,175 em ponto flutuante. Y é calculado como total − Z exibido, para a soma mostrada fechar.
- **Paridade com o CD-02.** O teste antigo comparava a lista exata de 10 rótulos. A regra nova é "subsequência ordenada", porque o formulário da safra tem campos a mais por desenho (Aplicar em, Conjunto, Diesel, Janela e os 3 só de leitura).
