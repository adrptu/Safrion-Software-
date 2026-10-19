# EX-52 e EX-53 · Classificação independente do Claude

- **Autor:** Claude · **Data:** 19/10/2026 · **Base:** `7aa910df` (composição local `/tmp/claude-0/osg`).
- **Escrita sem ler a classificação do Codex.** Não li GitHub, issues, PRs nem branches `codex/*`. Não abri nenhum arquivo com a classificação do Codex para o EX-52 ou o EX-53. Também deixei de ler, de propósito, a seção "Revisão do Codex sobre a v133" de `docs/painel03/README.md` (linha 148 em diante) e o `docs/planejar-safra/perenes/EX-57-confronto.md`.
- **Fontes.**
  - Os prompts, o `LEIAME.md` e o `decisoes-proprietario-1810.md` de `docs/integracao/V73/pedidos-1810/`.
  - O código de `tools/prototipo/v37/gen37/`.
  - A composição não tem `AGENTS.md`, `docs/PRD.md` nem `docs/DECISIONS.md`. Li esses três no repositório `/home/user/Safrion-Software-` (HEAD `94e19e45`), que não citam o EX-52 nem o EX-53.
- **Convenções.**
  - Caminhos de código relativos a `tools/prototipo/v37/gen37/`. O PRD aparece como `PRD.md:linha (seção)`.
  - **[conferido]**: li no código ou no documento. **[inferido]**: dedução minha, sem execução.
  - Nenhum teste foi executado para esta classificação e nenhum número foi medido no navegador. Os números de exemplo vêm da semente sintética.

## 0. Contagem

| EX | Grupo | Adotar | Adaptar | Rejeitar |
|---|---|---|---|---|
| EX-52 | Ideias J1–J8 | 1 (J4) | 6 (J1, J2, J3, J5, J7, J8) | 1 (J6, no protótipo) |
| EX-52 | Fatias F1–F5 | 2 (F1, F4) | 3 (F2, F3, F5) | 0 |
| EX-53 | Indicadores (55) | 12 | 42 | 1 (A6) |
| EX-53 | Captura D1–D13 | 2 (D8, D12) | 11 | 0 |
| EX-53 | Fatias F1–F5 | 1 (F3) | 4 (F1, F2, F4, F5) | 0 |
| EX-53 | Financeiro (seis critérios) | 0 | 1 | 0 |
| **Total EX-52** | | **3** | **9** | **1** |
| **Total EX-53** | | **15** | **58** | **1** |

Dentro do J1, a dose variável por zona fica fora e não vai ao proprietário. No J8, o modelo de cultura fica só como estudo e não entra no escopo.

## 1. Achados que valem para vários itens

- **T1 · Aprovação em lote (proprietário, 18/10, noite).**
  - A regra 7 do EX-53 ("Decidir nunca aprova em lote (decisão fixa)") e o J7 ("decisão fixa: aprovação individual") foram escritos antes dessa decisão.
  - O Painel continua sem aprovar, porque só lê (`areas/painel_gestao.py:8`) [conferido]. Aprovar em lote acontece em Aprovações, com o papel CTL-3, prévia, travas por O.S. e um CMD-42 por O.S.
  - O motivo do texto muda, mas a proibição de medir a velocidade de aprovação continua (EX-53, NÃO FAZER).
- **T2 · Duas datas de referência.**
  - Atrasos e janelas das O.S. usam `OSD.hoje` = 23/09 (`dados2.py:5`, `:1268`; `areas/paineis.py:44`).
  - O Comercial e o apontamento usam `CEN_DIA_OP` = 26/09 (`dados_config.py:12`; `producao.js:84`) [conferido].
  - Todo indicador que cruza O.S. e Comercial precisa de uma data só, declarada no ⓘ: margem, área em risco e cobertura de 14 dias.
- **T3 · Cor e meta fixas no código.**
  - Hoje há uma régua única de 10 % (`areas/painel_gestao.py:43`), uma referência de 95 % em "Ativos liberados" (`:106`) e um limite de ±5 % na Inteligência (`inteligencia.js:22-23`) [conferido].
  - Isso conflita com três regras:
    - PRD.md:4695 (cap. 14): "cores não usam percentuais universais de tolerância";
    - PRD.md:8714 (55.5): "meta não configurada não recebe verde automático";
    - a regra 4 do EX-53.
  - Na F1, o cartão sem meta (D11) não recebe cor de estado e mostra "meta não configurada", nunca verde.
- **T4 · Uma fórmula, em decimal.**
  - O custo usa ponto flutuante com `r2=Math.round(x*100)/100` (`areas/custo_dominio.py:43`) [conferido].
  - O "% do orçado" é calculado duas vezes no próprio Painel (`areas/painel_gestao.py:93` e `:170`) [conferido].
  - Os dois casos conflitam com a ENG-011 e a ENG-013 (AGENTS §4).
  - Margem, custo projetado, equilíbrio e resultado por ha nascem num serviço só, o de `areas/custo_dominio.py`, com a aritmética decimal que já existe em `producao.js:11-25` (prM, prDiv, prMulDiv). Painel, Mapa, J1 e J8 só leem.
- **T5 · O realizado da operação é custo padrão.**
  - Realizado = insumo informado × preço + COP × ha apontado (`areas/custo_dominio.py:18-22`). O COP é o custo/h do conjunto ÷ o rendimento do CD-08 (`areas/inicio.py:236`) [conferido].
  - Só o insumo é real. A operação só fica real com as horas (D1).
  - O custo/h da máquina já inclui manutenção e depreciação (`areas/cad_ativos_pessoas.py:150`) [conferido]. Somar o custo da OM ao custo da safra duplicaria (PRD.md:8664, KPI-PCM-10).
- **T6 · Base de custo não declarada.**
  - O insumo é COE. O custo/h com depreciação é COT parcial. Terra, juros, estrutura e mão de obra fixa ficam fora [inferido].
  - A CAL-04 (PRD.md:4299-4315) e a CAL-18 (PRD.md:4503) exigem declarar a base.
  - Todo indicador econômico leva no ⓘ: "base: insumos + operação pela taxa da máquina; fora: terra, juros, estrutura e tributos".
- **T7 · GE-03 estático.**
  - Custos e fechamento não lê o cenário: `areas/gestao.py:263-280` não usa `agrCustoRef` nem `cenGet` [conferido].
  - Todo clique "Abre: Custos e fechamento" leva a outro número, o que quebra a regra 2 e o EX-51 R8.
  - Até o GE-03 ler `agrCustoRef`, o clique leva à camada Custos do Mapa ou ao bloco Custos do Painel.
- **T8 · A previsão da soja é a meta.**
  - Na semente, a previsão da soja tem `base='meta'` e vale área × meta × 60 (`dados_producao.py:125`) [conferido].
  - Produtividade esperada × meta dá 0 % por construção. O cartão diz "previsão = meta (sem estimativa independente)".
- **T9 · Eventos gravam só a hora.**
  - `cenAgora()` devolve HH:MM (`cenario.js:29`). É usado em `osc_fim` (`areas/processo_os.py:650`), em `cenMov` (`cenario.js:281`) e no turno (`cenario.js:551`) [conferido].
  - Indicadores medidos em dias precisam de data e hora ISO no evento: tempo até a decisão, quarentena, estoque parado e disponibilidade. O turno noturno da irrigação também.
- **T10 · Limite de cartões.**
  - A regra 9 do EX-53 pede até 6 por seção. O PRD.md:8649 (55.2) diz até 4 cartões iniciais por tela de trabalho.
  - O Painel é painel analítico, não tela de trabalho [inferido]. Fica com 6 no Painel e com 4 quando o cartão aparece na tela da área.
- **T11 · Meu dia e Aprovações ocultos e estáticos.**
  - O IN-01 tem a fila escrita à mão (`areas/inicio.py:1980-1988`) [conferido].
  - O J7 e as listas da regra 7 do EX-53 dependem do EX-50 (tela visível) e do EX-51 R7 (pendências lidas do cenário).

## 2. EX-52 · Ideias dos jogos

### J1 Ciclo do talhão: Adaptar
- **Motivo:** hoje o agrônomo e o gestor abrem 5 camadas para saber se o talhão pagou. Ligar os elos poupa navegação, desde que nenhum número seja recalculado no painel.
- **Já existe [conferido]:**
  - painel do talhão no IN-04 com Estádio, Satélite, Insumos, Custos, Irrigação, Pragas, Carência, Solo e Colheita (`areas/inicio.py:946-1020`);
  - hub "Neste talhão" na camada Integrado, uma linha por função, cada uma com "Ver …" (`areas/inicio.py:1036-1046`);
  - dose sugerida pelo laudo e o texto "Laudo por zona: não sugere dose (taxa variável fora do escopo)" (`areas/analise_solo.py:174`);
  - previsto × realizado do talhão (`areas/inicio.py:979-991`; `areas/custo_dominio.py:25-29`);
  - resultado da colheita (`producao.js:163-178`).
- **Adaptação:**
  1. Sem seção nova. O hub "Neste talhão" passa a seguir a ordem do ciclo: Solo → Plano e dose → O.S. → Colheita → Custos → Resultado. Cada linha mostra o "falta" que a seção já calcula.
  2. Entra um único elo novo, "Resultado por ha", vindo do serviço econômico (T4), com "parcial: falta <x>".
  3. O CD-01det não repete o painel: ganha "Abrir no Mapa" com o talhão (AGENTS §3.4).
- **Fórmula do elo novo:** resultado (R$/ha) = [Σ kg vendidos × preço contratado + kg esperados não vendidos × preço de referência − despesas de venda] ÷ ha plantados − custo (R$) ÷ ha plantados.
- **Fonte:**
  - `comPrecos` (`comercial.js:438-449`);
  - `REF`, com fonte e data (`dados_comercial.py:16-19`);
  - `agrCustoRef` (`areas/custo_dominio.py:40-63`).
  - O feijão não tem cotação e mostra "sem dado" (`dados_comercial.py:19`).
- **Conflitos:**
  - ENG-011: o resultado não pode nascer em `inicio.py`;
  - KPI-CUS-01: R$/ha não se soma entre talhões;
  - CAL-18 (PRD.md:4505): margem sobre receita líquida;
  - T5, T6 e T7: o aceite "mesmos números do GE-03" não é atendível enquanto o GE-03 for estático.
- **Aceite:**
  - Na safra 2026/27, só o mamão da Lagoa Grande tem colheita: OS-0505 em execução e OS-0510 encerrada (`dados_lagoa_safra.py:123`, `:128`) [conferido]. A soja não foi colhida.
  - O aceite precisa nomear o talhão (ex.: Pivô 6) e tratar o perene pelo ciclo do EX-57 [inferido].
- **Depende:** do RT, nada novo (a regra laudo → dose já existe). Do proprietário, nada.
- **Dose variável por zona: não incluir e não levar ao proprietário.**
  - O PRD.md:6431 (cap. 36) especifica a taxa variável, mas a prescrição espacial está na etapa E3, "Ecossistema e integrações avançadas" (PRD.md:4918) [conferido].
  - Ela exige densidade amostral, perfil de máquina homologado e exportação com unidade e CRS (FO-44, PRD.md:2370).
  - O custo é alto: motor espacial, exportação ISOXML ou shape e homologação por terminal. O ganho só existe para cliente com controlador de taxa e laudos em grade.
  - **Gatilho de retomada:** cliente do piloto com controlador e laudos em grade. Aí vira EX próprio, com o RT validando a regra.

### J2 Trabalho andando no mapa: Adaptar
- **Motivo:** o PCP vê se a O.S. termina dentro da janela sem abrir a ordem. Dano evitado: descobrir no último dia que o saldo não cabe.
- **Já existe [conferido]:**
  - "Avanço" da camada Ordens de serviço, com rótulo "realizado/área ha · %", cor por estado e nenhuma pintura de fração (`mapa_camadas.js:22-24`; legenda em `:32`);
  - realizado e saldo vindos do cenário (`os_mapa.js:24`, `:31`);
  - apontamentos por dia, nos estados Conferido, Provisório e Previsto (`areas/processo_os.py:80-83`);
  - atualização entre abas quando o cenário muda (`cenario.js:46-49`; o Mapa chama `cenOuvir` em `areas/inicio.py:1920`);
  - agenda estimada que "não projeta término fora da janela" (`frentes_agenda.js:3-8`).
- **Conflito material:** o PRD.md:3010 (8.4.4, Avanço espacial) diz que, sem geometria executada, o mapa mostra "barra/percentual no cartão e marcador" e não pinta "arbitrariamente 60% da geometria". O J2 pede pintar a fração dentro do polígono.
- **Adaptação:**
  - Sem pintura de fração: o polígono fica com a cor de estado.
  - O rótulo e o cartão ganham uma barra e o texto: "190 de 350 ha · ritmo 47,5 ha/dia (4 dias) · termina 27/09 no ritmo · programado até 26/09 · último apontamento 23/09". Conferido e provisório ficam em linhas separadas.
  - O.S. impedida não projeta: "previsão suspensa: impedida · <causa>".
  - Término depois da janela vira "passa da janela em N dias", em vermelho e em texto.
- **Fórmula:**
  - Ritmo (ha/dia) = Σ ha dos apontamentos somados (`cenApSomado`, `cenario.js:593`) ÷ nº de dias com apontamento.
  - Término = referência + teto(saldo ÷ ritmo) dias.
  - Com dias Previsto, a programação aparece ao lado, sem se misturar com a projeção.
  - A legenda declara a base: "proporção da área, não posição".
- **Semente [inferido, sem execução]:**
  - OS-0421: 50 + 50 + 50 + 40 = 190 ha em 4 dias, ou 47,5 ha/dia. Os 160 ha de saldo levam 4 dias e terminam em 27/09. A janela vai até 26/09 e a programação Previsto é 24–26/09 (50, 50 e 60 ha).
  - OS-0420: 18 + 12 = 30 ha em 2 dias, ou 15 ha/dia. Tem o selo "Impedida · ativo bloqueado" (`dados.py:106`), então a previsão fica suspensa.
- **Onde mora a conta:** no domínio da O.S., ao lado de `cenApSomado`. Mapa, O.S. e Painel (A1) leem a mesma conta. A barra do Mapa continua com 9 nomes (DEC-1610-09).
- **Depende:** nada do RT nem do proprietário.

### J3 Fila por recurso: Adaptar
- **Motivo:** o PCM e o responsável do packing veem o gargalo do dia e o motivo da espera. Dano evitado: máquina parada esperando mecânico sem que ninguém veja.
- **Já existe [conferido]:**
  - Carga por recurso da O.S. (`areas/processo_os.py:1396-1407`), registrada com o recurso e o tempo de `alocacao.py` (`visoes.py:135-136`);
  - regra do registro: a visão "carga" só entra com recurso e tempo (`visoes.py:42`); a Irrigação cortou a carga porque a IR-02 já mostra setor × dia (`visoes.py:79`);
  - na MA, "Esta semana · por dia · capacidade da oficina não calculável (sem P10)" (`areas/maquinas.py:1152`);
  - a OM tem especialidade, executante, tempo estimado e horas reais (`dados_manutencao.py:244`, `:246-247`);
  - "Espera por peça · por equipe: não calculável" (`areas/maquinas.py:620`);
  - horas de linha no beneficiamento (`ben.js:5`).
- **Adaptação:**
  1. O desenho da Carga sai da tela O.S. e vai para o motor, como visão do registro. Recebe {recurso, item, início, duração com a base, estado, motivo da espera}.
  2. A visão entra em dois lugares:
     - MA › Ordens: especialidade ou mecânico × dia; duração = tempo estimado da OM, com a base "estimativa da OM";
     - BEN: linha × dia, pelas horas de linha.
  3. Estoque (separação) e Cargas (balança) ficam fora por ora. A requisição não tem duração (`areas/paineis.py:33`), a carga "A pesar" não tem tempo (`producao.js:134`) e a regra do `visoes.py:42` barra a visão. O corte entra no REGISTRO, com o motivo.
  4. Gargalo só com capacidade cadastrada. Sem ela, a tela diz "capacidade não cadastrada" e não inventa número.
- **Conflitos:**
  - `visoes.py:42`: sem tempo, não há visão;
  - recurso único sem dupla alocação (Onda 0);
  - DEC-1610-01: a peça fica reservada para a OM que a pediu; a visão só mostra.
- **Depende:** nada.

### J4 Componente "tem · chega · falta": Adotar
- **Motivo:** a mesma pergunta ("dá para executar na data?") tem três textos em três telas. Um componente só reduz leitura e erro de interpretação. Dano evitado: falta descoberta na hora de executar.
- **Já existe [conferido]:**
  - insumo da O.S.:
    - necessidade × estoque e pedidos no Mapa (`areas/inicio.py:971-978`);
    - `cenEstDem` (`cenario.js:243`);
    - CAL-01 em `cal01.js`, já com as previsões reprogramadas (`areas/processo_compras.py:51`);
  - "pedido em aberto chega depois da falta" (`areas/processo_compras.py:406`);
  - peça da OM: `manFalta` e reserva de outra OM (`dados_manutencao.py:568-571`); chegada da compra de manutenção (`dados_compras_mat.py:61`);
  - produto do pedido de venda: "Falta X: reservar lote apto" (`areas/vendas.py:110-115`).
- **Contrato (o componente não calcula):** cada domínio entrega:
  - necessário: quantidade, unidade e data;
  - tem: o livre na data, sem quarentena;
  - chega: quantidade, data, documento, firme ou condicionado;
  - falta = necessário − tem − chega até a data, nunca abaixo de 0;
  - quem resolve e o verbo.
  - No pedido de venda, "chega" é colheita prevista e leva o rótulo "previsto", nunca "firme". Unidades diferentes não se somam.
- **Conflitos:** nenhum. O servidor decide saldo e reserva (AGENTS §4). O KCl em quarentena continua sem contar (`areas/processo_compras.py:709`).
- **Depende:** nada. Fica na fatia do EX-45.

### J5 Calendário da safra: Adaptar
- **Motivo:** o gestor vê a safra inteira por talhão e semana, com a carência que corta a colheita. Poupa montar a planilha fora do sistema.
- **Já existe [conferido]:**
  - Calendário da O.S. (`areas/processo_os.py:1476`, `:2049`; semana em `g2lib.js:1306`);
  - data de cada atividade por DAP e DAPC (`areas/inicio.py:237-242`, `:282`);
  - colheita prevista do cultivo (`dados_producao.py:44`);
  - carência na camada Colheita (`areas/inicio.py:1018`, `:1260`);
  - janela 25–27/09 da OS-0502 (`dados_lagoa_safra.py:119`, `:130`).
- **Conflito:** a data da atividade tem 7 variantes no código (`datas_atividade.js:12`; EX-57 F0), o que fere a ENG-011. O calendário não pode escolher uma variante por conta própria: usa a canônica depois do EX-57 F0.
- **Adaptação:**
  - Visão Calendário registrada no `visoes.py` para SAF e COLH, reaproveitando o componente da O.S. em talhão × semana.
  - Planejado (atividade do plano), emitido ou realizado (O.S.) e carência têm estilos e textos diferentes.
  - Estádio só onde há dado (camada Lavoura, `areas/inicio.py:946`). A maturação prevista de grão não existe [inferido] e não se inventa.
- **Depende:** do RT, nada novo (as janelas vêm do plano). Espera o EX-57 F0.

### J6 Modo treino: Rejeitar no protótipo, com registro para o software real
- **Motivo:**
  - No protótipo, tudo já é sintético e o cenário fica numa única chave do navegador (`cenario.js:6`). Uma "organização de treino" não provaria isolamento nenhum.
  - O perfil de demonstração "não é segurança" (`g2lib.js:743`) [conferido].
  - O teste com usuários (DEC-1610-02) é moderado e não precisa de modo guiado.
  - Há custo e nenhum ganho medido antes de o EX-56 fechar o protótipo (critério 7).
- **Já existe [conferido]:** "Restaurar demonstração" (`ficha_pivo.py:71`; app MB-01) e o ON-01 com outro contratante em trial (`areas/onboarding_backoffice.py:9-10`).
- **No software real** (gatilho: primeira equipe nova no piloto):
  - o treino é uma organização própria no servidor;
  - os adaptadores externos são simulados pela identidade do serviço, não por uma variável (PRD.md:5581);
  - tem selo "Treino" permanente, o cenário de exemplo e roteiros por persona com o passo atual e o próximo, mais "Recomeçar".
- **Depende do proprietário:** a "cópia anonimizada da fazenda" é dado real derivado (ENG-017). O PRD.md:5581 pede minimização, acesso e descarte aprovados.

### J7 Progresso da semana por pessoa: Adaptar
- **Motivo:** a pessoa vê no Meu dia o que é dela na semana e abre o grupo, sem filtrar listas. Dano a evitar: virar placar de pessoa.
- **Já existe [conferido]:**
  - dono, janela e impedimento de cada O.S. na projeção (`areas/paineis.py:95`, `:101`);
  - itens com dono no Painel (`areas/painel_gestao.py:75-79`);
  - Meu dia com a fila estática (`areas/inicio.py:1980-1988`).
- **Adaptação:**
  - A linha mostra "minhas O.S. desta semana" (na janela, impedidas, atrasadas). Vem da mesma função do Painel, filtrada por dono e semana, e cada número abre o recorte.
  - Conta só execução. Não conta aprovação nem liberação, inclusive em lote (T1).
  - Sem histórico por pessoa e sem comparação entre pessoas.
- **Conflitos:**
  - PRD.md:7461: sem ranking punitivo, e falta de retorno não prova improdutividade;
  - KPI-PCP-06 (PRD.md:8708): volume individual não mede o valor de uma pessoa;
  - se um dia virar meta de avaliação, valem o PRD 55.5 (FO-38) e a DEC-1610-08.
- **Depende:** do EX-50 e do EX-51 R7. Do proprietário, só se ele quiser usar a linha como meta de avaliação, o que não proponho.

### J8 "E se?" no planejamento: Adaptar (a) e estudo (b) sem implantação
- **Motivo:** o gestor compara a margem de cenários antes de decidir área, venda e custo. Hoje o cenário é digitado e não confere com nada.
- **Já existe [conferido]:**
  - GE-02 "Versões em paralelo" V1, V2 e C1, com premissas em texto e números digitados (`areas/gestao.py:174-186`); "Criar cenário" grava premissas digitadas (`:198-202`);
  - GE-02det V1 × V2 × real, estático (`:220-252`);
  - série de preço e sazonalidade (`inteligencia.js:90-140`);
  - meta e área por cultivo (`dados2.py:63-70`).
- **Adaptação (a): o cenário é calculado, não digitado.**
  - Premissas, cada uma com a fonte:
    - área;
    - produtividade (meta, previsão publicada ou histórico);
    - preço (vendido + referência);
    - custo (plano).
  - Saída lado a lado, com a diferença: receita líquida, custo, margem em R$ e R$/ha, e produtividade em sc/ha ou t/ha.
  - Usa a mesma função da margem do EX-53 P1 (uma fórmula só).
  - A data de plantio só desloca as janelas (DAP). Sem modelo, não se estima o efeito dela na produtividade.
  - O cenário não publica previsão nem gera compra, e leva o selo "cenário".
- **Estudo (b).**
  - O que existe:
    - estação simulada com ET₀, chuva e vento diários (`dados_irrigacao.py:53`);
    - laudos de solo (`dados_solo.py`);
    - cultivar (CD-02);
    - data de plantio (`dados2.py:63`);
    - balanço hídrico (`irrigacao_estado.js:111`).
  - O que falta:
    - série diária longa de temperatura e radiação;
    - água disponível por camada de solo;
    - coeficientes de cultivar calibrados;
    - manejo de N;
    - licença e custo de cálculo do APSIM, do DSSAT e do AquaCrop (não conferi as licenças; a verificar).
  - **Recomendação:** não incluir modelo de cultura no escopo vigente.
  - **Gatilho de retomada:** duas safras de dados do piloto e um RT disposto a calibrar por cultura e região.
- **Conflitos:**
  - PRD 15.1: calcular é determinístico, e nada simulado vira dose, compra ou previsão oficial;
  - DEC-1610-11: não é IA, mas o custo de cálculo vai com estimativa antes de ligar.
- **Depende:** do RT, os parâmetros do modelo (só no estudo b). Do proprietário, nada, porque não recomendo incluir.

### Fatias do EX-52
- **F1 (J4 com o EX-45; J2 com o EX-44): Adotar a ordem.** O J2 já entra com a adaptação do PRD 8.4.4.
- **F2 (J3, J5): Adaptar.** O J3 só na MA e no BEN. O J5 depois do EX-57 F0.
- **F3 (J1): Adaptar.** Além do EX-51, depende do serviço econômico do EX-53 F2 (o elo Resultado) e do GE-03 lendo o cenário.
- **F4 (J7): Adotar a ordem**, depois do EX-50 e do EX-51 R7.
- **F5 (J6, J8a, J8b): Adaptar.** O J6 sai. O J8(a) vem depois do EX-53 F2, porque usa a mesma função de margem. O J8(b) corre em paralelo, como relatório.

## 3. EX-53 · Indicadores do Painel

### 3.1 Ajustes às 10 regras (não contam como item)
- **R2:** quebrada no destino GE-03 (T7).
- **R3:** o selo já existe (`areas/painel_gestao.py:46`).
- **R4 e R5:** ver T3.
- **R6:** já atendida por `prPonderada` (`producao.js:192-197`) e pelo agrupamento fazenda · safra · cultura (`areas/custo_dominio.py:46`).
- **R7:** ver T1; a ordem está em P8.
- **R8:** o recorte já está preparado (`agrPainelRef(c,rec)`, `areas/paineis.py:85-93`). A vistoria do MIP não tem safra e mostra "Sem dados" com recorte de safra (`:66`).
- **R9:** ver T10. Hoje o Painel abre pelo endereço, não pelo perfil (`areas/painel_gestao.py:181-184`) [conferido].

### 3.2 Catálogo

#### Prioridades
**P1 Margem projetada: Adaptar.**
- **Fórmula:** margem (R$/ha) = produtividade esperada (un/ha) × preço líquido esperado (R$/un) − custo projetado (R$/ha). O total em R$ é a margem/ha × ha plantados.
- **Preço líquido esperado:**
  - (Σ valor contratado + kg não vendidos × referência) ÷ produção esperada;
  - menos frete, prazo e tributo sobre venda, este como parâmetro do D11;
  - `intLiquido` já desconta frete e prazo (`inteligencia.js:15`).
- **Custo projetado:** realizado (conferido + provisório) + previsto da área ainda não executada (`orcado_rs − prev_exec_rs`), ÷ área plantada.
- **Fonte [conferido]:**
  - `agrCustoRef` (`areas/custo_dominio.py:58-61`);
  - `comPrecos` (`comercial.js:438-449`);
  - `REF` (`dados_comercial.py:16-19`);
  - previsões (`dados_producao.py:122-125`);
  - meta (`dados2.py:63-70`).
- **Conflitos:** CAL-18 (PRD.md:4505: receita líquida), T4, T5, T6 e T8.
- **Adaptação:**
  - O nome leva a base: "Margem projetada · base insumos + operação padrão".
  - Fica num serviço só. O perene usa o ciclo anual do EX-57.
  - É candidato a Gemini se houver divergência de base.
- **Depende:** o tributo e as despesas de venda são parâmetros que o gestor cadastra no D11.

**P2 Produtividade esperada × meta: Adotar.**
- **Fórmula:** desvio (%) = (produção esperada ÷ área − meta) ÷ meta, na unidade gravada na meta, com `prUnpDesv` (`producao.js:233`).
- **Fonte [conferido]:**
  - `prResultado` (`producao.js:163-178`);
  - meta e unidade da meta (`dados2.py:63-70`);
  - agregação por `prPonderada` (`producao.js:192`).
- **Ressalva:** para a soja, a previsão é a meta (T8).
- **Depende:** nada.

**P3 Custo por hectare × orçado: Adaptar.**
- **Fórmula:** realizado + comprometido (R$) ÷ ha plantados, contra o orçado (R$/ha).
- **Fonte [conferido]:**
  - `real_rs_ha` e `orcado_rs_ha` (`areas/custo_dominio.py:59-60`);
  - o comprometido (requisição solicitada e ainda não consumida) não é valorizado hoje [inferido].
- **Adaptação:**
  - O EX-53 compara "% do orçado consumido" com "% do ciclo decorrido". A comparação passa a ser com o "% do orçado previsto até hoje", pela data de cada atividade do plano (`areas/inicio.py:282`, `_data_atv`).
  - Motivo: o custo agrícola não corre linear no ciclo. Plantio e adubação de base concentram o gasto e dariam falso alarme.
  - A conta do "% do orçado" sai do Painel e passa a vir de `agrCustoRef` (T4).
- **Depende:** nada.

**P4 Custo por unidade produzida: Adotar.**
- **Fórmula:** custo projetado (R$/ha) ÷ produtividade esperada (un/ha), em R$/sc ou R$/t (KPI-CUS-02).
- É a mesma função e a mesma base do P1. Sem produtividade esperada, mostra "sem dado".
- **Depende:** nada.

**P5 Ponto de equilíbrio e margem de segurança: Adaptar.**
- **Conflito:** CAL-18 (PRD.md:4503): "meta comercial não se chama ponto de equilíbrio" e "PMV deve indicar base".
- **Adaptação:** dois números, com a base escrita:
  - produtividade de equilíbrio (sc/ha) = custo projetado ÷ preço líquido esperado;
  - preço de equilíbrio (R$/sc) = (custo/un + despesa/un) ÷ (1 − alíquota sobre a venda).
- **Margem de segurança (%):** (produtividade esperada − produtividade de equilíbrio) ÷ produtividade esperada. A meta (ex.: 20 %) vem do D11, nunca do código.
- **Fonte:** a mesma do P1.
- É candidato a Gemini.

**P6 Comercialização: Adaptar.**
- **Fórmula:** % comprometida = compromissos físicos (kg) ÷ oferta (estoque apto + previsão publicada, kg). Exposição = kg não comprometidos × referência (R$). Preço médio × referência.
- **Fonte [conferido]:** `intPosicao` e `intVendas.posicao` (`inteligencia.js:13`, `:30-36`), sobre `comPainel` (`comercial.js:410`).
- **Adaptação:** o denominador real é a oferta, não a "produção esperada". O texto passa a dizer isso.
- É o mesmo ID do C2 (KPI-COM-04, PRD.md:4732).

**P7 Área em risco na janela: Adaptar.**
- **Fórmula:** Σ ha de saldo das O.S. impedidas com fim da janela ≤ referência + 7 dias, por causa. As atrasadas (janela já vencida) ficam numa linha à parte.
- **Fonte [conferido]:**
  - impedidas, com a causa (`areas/paineis.py:49`, `:93-95`);
  - atrasadas (`:99-102`);
  - área (`areas/painel_gestao.py:61`, que hoje usa a área total e não o saldo).
- **Adaptação:**
  - Usar o saldo, não a área total.
  - Causas = as de `agrCausa` (receituário, insumo, máquina, outro). Sai "clima", porque clima é alerta e não impedimento (proprietário, 18/10).
  - Data de referência única (T2).
- A entrada da OS-0502 depende de ela estar impedida pelo Estoque (`libErr`) [inferido; o selo da semente é None, `dados_lagoa_safra.py:119`].

**P8 Listas "Atacar agora" e "Decidir": Adaptar.**
- **Hoje [conferido]:** a ordem é classe do dano → R$ → ha → dias (`areas/painel_gestao.py:48-51`).
- **Adaptação:**
  - A classe do dano continua primeiro: lei e segurança antes de dinheiro (AGENTS §4).
  - Dentro da classe Lavoura, a prioridade é ha em risco ÷ max(1, dias até o fim da janela). O "ha × dias" pedido inverte a urgência: a janela mais distante subiria na lista.
  - Dentro de Dinheiro e estoque, a ordem é por R$.
  - "Decidir" = Aprovações (EX-51 R7). O Painel nunca aprova (T1).

#### Agrícola · Operações
**A1 Execução do plano: Adaptar.**
- **Hoje [conferido]:** realizado ÷ previsto das O.S. Em execução e Em conferência (`areas/paineis.py:53-62`).
- **Fórmula:** ha executados ÷ ha previstos até a referência.
- **Previsto até a referência:**
  - quando a O.S. tem dias Previsto, usa a soma deles (`areas/processo_os.py:80-81`);
  - senão, a área das atividades e O.S. com janela já encerrada mais o pro rata linear das janelas em curso, com a base declarada.
- Corresponde ao KPI-PCP-01.QUANTIDADE.

**A2 Operações na janela: Adaptar.**
- O KPI-PCP-01 (PRD.md:8674) usa contagem como número principal: O.S. elegíveis concluídas até o fim da janela ÷ O.S. com fim da janela até a referência.
- A área vira componente separado: ha apontados com data ≤ fim ÷ ha das O.S. com janela encerrada.
- **Fonte [conferido]:** janelas (`dados.py:131`; `dados_lagoa_safra.py:130`) e datas dos apontamentos (`areas/processo_os.py:80-84`).
- A meta vem do D11.

**A3 Rendimento real × padrão: Adaptar (depende do D1).**
- **Fórmula:** Σ ha ÷ Σ horas produtivas (turno − paradas), em ha/h, por operação e conjunto, contra o CD-08.
- **Fonte [conferido]:**
  - `ap.h` existe e é opcional (`cenario.js:740`);
  - o app exige "Informe as horas trabalhadas" ao fechar o turno (`cenario.js:797`);
  - a semente não tem horas (`cenario.py:56`);
  - o padrão está em `catalogo_operacoes.py:8-28`.
- Corresponde ao KPI-PCP-05. Sem ranking por operador (PRD.md:7461).

**A4 Custo da operação × orçado: Adaptar.**
- **Hoje:** o realizado da operação é custo padrão (T5).
- **Fórmula:** (insumo consumido × preço + horas reais × custo/h do conjunto) ÷ ha executados, em R$/ha, por operação e talhão, contra o orçado.
- Até existir o D1, o cartão separa "insumo real" e "operação padrão". Fonte: `cusOrdem` (`areas/custo_dominio.py:16-23`).

**A5 Dose aplicada × dose da O.S.: Adaptar.**
- **Conflito:** a regra B-R8 não tem tolerância. Qualquer diferença no centésimo vai para a revisão do agrônomo e põe selo vermelho (`cenario.js:626-649`) [conferido]. A faixa de ±5 % do EX-53 não pode virar tolerância.
- **Fórmula:** consumo informado ÷ (dose × área do trecho) − 1, em %, por produto (KPI-CUS-04, PRD.md:8676). Mais o nº de divergências abertas e revisadas.
- A faixa configurável, definida pelo RT, só colore o desvio.
- **Depende:** do RT, a faixa.

#### Agrícola · Conformidade
**A6 Aplicações com receituário válido e dentro da carência: Rejeitar como indicador.**
- **Motivo:** a trava já impede executar sem receituário. O % fica perto de 100 % por construção e não muda decisão nenhuma (regra 1).
- As exceções já aparecem em "Atacar agora" como classe 1 (`areas/painel_gestao.py:75`, "Receituário divergente") [conferido].
- A carência que corta a colheita deve entrar ali também (fonte: `carSec`, `areas/inicio.py:1260`).
- O % de conformidade fica para a auditoria (CF-04), fora da primeira vista.

**A7 Aplicações fora da condição de clima: Adaptar (depende do D4).**
- **Decisão do proprietário (18/10):** clima é alerta.
- **Fórmula:** nº de cargas de tanque com temperatura, umidade relativa ou vento fora do limite no intervalo da aplicação, e % sobre as aplicações com produto.
- **Fonte:**
  - a estação só tem ET₀, chuva e vento diários (`dados_irrigacao.py:53`);
  - "a cada hora" é só a descrição da conexão (`dados_config.py:21-22`);
  - não há série horária nem registro de carga de tanque no app [conferido, por busca em `areas/mobile.py`].
- **Depende:** do RT (e do EX-54), os limites por produto.

#### Agrícola · Pragas e doenças
**A8 Focos acima do NC sem decisão: Adotar.**
- **Fórmula:** nº de vistorias em "decidir" e a idade de cada uma, em dias desde a vistoria.
- A idade já é calculada (`areas/paineis.py:79-80`, `dias`), mas o cartão só mostra a contagem (`areas/painel_gestao.py:82`) [conferido].
- A meta de 2 dias vem do D11.

**A9 Tempo até o controle: Adaptar.**
- **Adaptação:**
  - Passa a se chamar "Tempo até a decisão do RT": dias da vistoria acima do NC até a O.S. de controle liberada **ou** o registro de "não controlar".
  - Dano evitado: o indicador empurrar o RT a pulverizar só para baixar o número.
- **Fonte [conferido]:**
  - data da vistoria e situação "controle" (`mip.js:173-190`);
  - a data da liberação não existe, porque `osc_fim` grava só a hora (T9).
- **Depende:** do RT, a meta.

**A10 Vistorias em dia: Adaptar.**
- **Fórmula:** vistorias feitas até a data prevista ÷ vistorias previstas no período, em %, mais as atrasadas (nº e dias). Corresponde ao KPI-AGR-02 (PRD.md:8677).
- **Fonte:** "atrasada" com `S.prev` em `areas/paineis.py:81` [conferido]. As vistorias feitas no prazo [inferido] a partir de `vis.data`.

**A11 Eficácia do controle: Adaptar.**
- **Fonte [conferido]:** `mip.js:167` calcula a "redução observada = 1 − pós/pré"; `mip.js:229` diz que ela "não equivale a eficácia causal"; o KPI-AGR-01 (PRD.md:8679) vai na mesma linha.
- **Adaptação:**
  - Nome "Redução observada após o controle", por produto × alvo.
  - Só com n ≥ mínimo (definido pelo RT) e com as limitações escritas.
  - Sem ranking de produto.
- **Depende:** do RT.

#### Agrícola · Irrigação
**A12 Lâmina aplicada ÷ necessária: Adaptar.**
- **Adaptação:** em vez do índice 0,9–1,1, mostrar em mm, com sinal e tamanho:
  - necessidade não atendida (mm e ha), KPI-IRR-01.SALDO;
  - desvio de lâmina = aplicado efetivo − recomendado (mm), KPI-IRR-03 (PRD.md:8681).
- **Fonte [conferido]:** `irrBase` (`irrigacao_estado.js:111`) e a lâmina líquida = bruta × eficiência (`:80-81`). O limiar por setor já existe (`dados_irrigacao.py:117`).

**A13 Uso da outorga e energia: Adaptar.**
- **Fórmula da outorga:** volume medido no hidrômetro (m³) ÷ volume outorgado no período, em %. A trava de outorga já existe (`irrigacao_estado.js:373`) [conferido].
- **Energia:** kWh/m³ e kWh/(mm·ha) (KPI-IRR-02) não existem como dado, só há o aviso de ponta (`:262`). Ficam para o D13.
- Cartões separados (família, PRD 55.1).

#### Agrícola · Colheita e pós-colheita
**A14 Produtividade realizada × prevista × meta: Adotar.**
- **Fórmula:** peso líquido corrigido ÷ área colhida, em sc/ha ou t/ha.
- **Fonte [conferido]:**
  - `prResultado` (`producao.js:163-178`);
  - `prCorrigir` (`producao.js:57-60`);
  - previsão congelada antes da semana por `prVersaoRef` (`producao.js:152`), como pede o KPI-PREV-01;
  - estado "parcial" já calculado.
- O Painel só lê.

**A15 Perdas na colheita: Adaptar (depende do D5).**
- O KPI-AGR-05 (PRD.md:8686) mede pelo protocolo, nunca pela diferença entre meta e realizado.
- A meta "soja ≤ 1 sc/ha" fica no D11 com fonte, não no código.
- Começar só pelos grãos. Para o mamão, o método é outro.
- Dado não existe no protótipo. É candidato a Gemini.
- **Depende:** do RT, o protocolo e a meta por cultura.

**A16 Umidade e impureza na recepção: Adotar.**
- **Fórmula:**
  - média ponderada pelo peso líquido: Σ(u_i × liq_i) ÷ Σ liq_i, em %;
  - desconto em kg = dImp + dUmid, por `prCorrigir` (`producao.js:57-60`).
- **Fonte:** captura por carga (`producao.js:498-499`) [conferido].
- Comparar com o padrão contratado. Vale só para grãos.

#### Manutenção
**M1 Disponibilidade mecânica: Adaptar (depende do D3 e do D11).**
- **Fórmula:** CAL-06 (PRD.md:4339): (H_referência − H_indisponível) ÷ H_referência. O H_referência vem do calendário versionado (53.1).
- **Hoje [conferido]:** "Ativos liberados 94 %" conta ativos contra 95 % fixo (`areas/painel_gestao.py:104-107`; T3), e a MA diz "Disponibilidade 30 d: não calculável" (`areas/maquinas.py:434`).
- **Dado parcial:** as datas de Bloqueado e Apto ficam em `condHist` (`dados_manutencao.py:69`, `:850-853`), só com o dia.
- **Adaptação:**
  - O cartão de contagem perde a cor até haver meta.
  - A disponibilidade entra quando houver data e hora (T9) e o calendário (D11).
  - "Máquina crítica" não existe como atributo do ativo; a criticidade é da OM [inferido].

**M2 Área parada por máquina: Adaptar.**
- **Fórmula:** Σ ha de **saldo** das O.S. impedidas pela causa "Máquina ou equipamento", por ativo bloqueado, e os dias desde o bloqueio.
- **Fonte [conferido]:**
  - `agrCausa` (`areas/paineis.py:49`);
  - `manPropAfeta`, as O.S. alocadas ao ativo (`dados_manutencao.py:1187`);
  - data do bloqueio em `condHist`.
- Exemplo: OS-0420 tem 70 ha de saldo (não 100) e o Trator T1 está na OM-0233.

**M3 MTBF e MTTR: Adaptar.**
- **Fórmula:** CAL-06 e KPI-PCM-02:
  - MTBF = horas operadas ÷ falhas corretivas;
  - MTTR = horas ativas de reparo ÷ reparos;
  - restauração em separado.
- **Fonte [conferido]:**
  - horas operadas pela diferença das leituras de horímetro, que já existem (`dados_manutencao.py:388`, `:1111`), sem depender do D1;
  - falhas = OMs corretivas (`dados_manutencao.py:226-246`);
  - reparo ativo = `exec.horas` (`:244`);
  - a espera não existe (`areas/maquinas.py:620`).
- Sem falha no período, mostrar "não estimável · N h observadas" (PRD.md:8655).

**M4 Preventiva × corretiva: Adaptar.**
- Adota o ID do PRD, KPI-PCM-06 (PRD.md:8660): horas de manutenção emergencial ÷ horas de manutenção, com as horas por tipo à vista.
- **Fonte [conferido]:** `exec.horas` e `tipo` da OM (`dados_manutencao.py:244`, `:822`).
- A meta de 70 % vai para o D11.

**M5 Cumprimento do plano preventivo: Adaptar.**
- **Conflito:** `manCumprimento` (`dados_manutencao.py:1183-1184`) e o detalhe do ativo (`areas/maquinas.py:431`) contam no denominador só as preventivas **encerradas** [conferido]. A vencida e não feita some da base. Isso fere o KPI-PCM-05 e o KPI-PCM-09 (PRD.md:8659-8663).
- **Fórmula:** feitas até o vencimento original (`vencOrig`) ÷ vencimentos do plano no período, incluindo os ainda sem ordem de `manSemOrdem`.

**M6 Custo de manutenção: Adaptar.**
- **Fonte [conferido]:**
  - `manCustoPeriodo` (`dados_manutencao.py:1180`) e o custo por natureza (`areas/maquinas.py:431-432`);
  - a MA diz "Custo por hora operada: não calculável" (`:433`);
  - as horas podem vir do horímetro, como no M3;
  - o valor de reposição não existe: o custo/h substituiu o valor do ativo (`areas/cad_ativos_pessoas.py:4`). Vai para o D11.
- **Conflito:** T5. É indicador de PCM e nunca se soma ao custo da safra.
- A meta de 2 a 5 % ao ano vai para o D11, com fonte.

**M7 Fila e retrabalho: Adaptar.**
- **Fila:** KPI-PCM-08 (PRD.md:8662), em HH pendentes. O dado existe: `tempo` e `esp` da OM (`dados_manutencao.py:247`). As semanas equivalentes não saem, porque falta a capacidade (P10).
- **Retrabalho:** KPI-PCM-07, reincidência por ativo × componente na janela. Não existe fluxo de reabrir OM [inferido].

#### Suprimentos
**S1 Cobertura das O.S. dos próximos 14 dias: Adotar.**
- **Fórmula:** O.S. que começam em até 14 dias com todos os insumos cobertos (livre na data + pedido firme antes do início, sem quarentena) ÷ O.S. que começam em até 14 dias.
- **Fonte [conferido]:** `cenEstDem` (`cenario.js:243`) e CAL-01. Usa o contrato do J4. Corresponde ao KPI-PCP-02 (PRD.md:4712).

**S2 Ruptura: Adaptar.**
- Adota o KPI-SUP-01 (PRD.md:8690): necessidades devidas não cobertas na data ÷ necessidades elegíveis, com as O.S. afetadas, ha e dias.
- Não soma kg de produtos diferentes.
- "Dias parados" precisa da data de início do impedimento, que o estado não tem (`areas/paineis.py:42`, "desde: … null") [conferido].

**S3 Pedidos que chegam depois da necessidade: Adotar.**
- **Fórmula:** nº e R$ dos pedidos abertos com previsão de entrega depois da data da falta que cobrem.
- **Fonte [conferido]:** `areas/processo_compras.py:406`, `:503`, `:889`.

**S4 Entrega no prazo e completa (fornecedor): Adaptar (depende do D6).**
- Segue a CAL-20 e o KPI-SUP-05: no prazo **e** completas ÷ devidas, por linha, contra a promessa original.
- **Conflito:** reprogramar a previsão sobrescreve `prev` (`areas/processo_compras.py:618`) [conferido], e a CAL-20 diz que "alterar promessa não apaga atraso".
- `intPontualidade` (`inteligencia.js:19`) mede só o prazo, sem a completude.
- Com amostra pequena, o cartão diz "parcial: N entregas".

**S5 Prazo de compra: Adaptar.**
- Segue o KPI-SUP-04 (PRD.md:8691): tempo entre marcos (solicitação, aprovação, pedido, recebimento apto), com mediana e p90 por classe de item.
- O dado é parcial: as datas da SOL e do PC existem (`dados_compras_mat.py:76`).

**S6 Preço pago × referência: Adaptar.**
- **Primeiro:** preço por unidade de produto × referência com fonte, que já existe em `intCompras` (`inteligencia.js:49-60`). Os ±5 % fixos vão para o D11.
- **Depois:** R$ por unidade de nutriente ou de i.a., só quando o cadastro tem a garantia ou a concentração.
- **Depende:** do RT, a equivalência agronômica, porque nutrientes não se substituem perfeitamente (S, Cl).

**S7 Acurácia do inventário: Adaptar.**
- Segue o KPI-SUP-02 (PRD.md:8693): itens-lote-local dentro da tolerância ÷ contados, mais a divergência absoluta em quantidade e em valor, sem que os sinais se anulem.
- **Fonte [conferido]:** a contagem **já está no Estoque visível** (`areas/processo_estoque.py:124-130`, "Nova contagem"), e os ajustes passam pela alçada (`areas/painel_gestao.py:119`, `:128`).

**S8 Estoque a vencer e parado: Adaptar.**
- **A vencer:** R$ com validade em até 90 dias = quantidade × preço de referência do item, com a base declarada.
- **Fonte:** validade por lote [conferido, `cenario.py:24-25`]. O lote não tem custo próprio [inferido].
- **Parado:** precisa da data do movimento, e `cenMov` grava só a hora (T9).

**S9 Quarentena pendente: Adotar.**
- **Fórmula:** lotes, quantidade na unidade do lote e dias desde a entrada.
- **Fonte [conferido]:** contagem em `areas/paineis.py:134`; data da entrada na NF de recebimento (`dados2.py:865`). Os dias ainda são dado parcial (T9).

#### Comercial
**C1 Preço médio vendido × referência: Adotar.**
- Já está no Painel: `comPrecos` (`comercial.js:438-449`), com a referência, a fonte e a data (`dados_comercial.py:16-19`) [conferido].
- Só a cor passa a usar a meta (T3).

**C2 Produção vendida e exposição: Adaptar.** Funde com o P6: mesmo ID, mesma função, aparece nas duas abas.

**C3 Custo coberto: Adaptar.**
- **Fórmula:** receita contratada **líquida** (CAL-18) ÷ custo total projetado da safra (P1 × ha), em %.
- A meta vem do plano de comercialização (D11).

**C4 Oferta × compromissos: Adotar.**
- Já está no Painel (`comPainel`, `comercial.js:410-436`; `areas/painel_gestao.py:144-146`).
- Acrescenta os kg em déficit (`livre` negativo), que já são calculados [conferido].

**C5 Entrega no prazo e completa (cliente): Adaptar (depende do D7).**
- Segue o KPI-COM-03 (PRD.md:8698): contra a promessa original; o atraso ainda não entregue conta como não cumprido.
- **Fonte [conferido]:** janela do pedido (`dados_comercial.py:61-64`) e data da entrega (`comercial.js:451-453`). A tolerância vem do D11.

**C6 Recebíveis: Adaptar.**
- "A receber" e "vencido" já existem (`comIndicadores`, `comercial.js:451-454`).
- Prazo real de recebimento e inadimplência (KPI-FIN-10 e KPI-FIN-09, PRD.md:8702-8703) precisam da baixa, e o protocolo está "sem baixa no protótipo (D-C07)" (`comercial.js:68`) [conferido]. Dependem da seção 3.5.

**C7 Aproveitamento do beneficiamento: Adaptar.**
- Segue o KPI-IND-02.VENDAVEL (PRD.md:8687): massa vendável de saída ÷ massa de entrada, sem embalagem e com base de umidade declarada. Descarte e perdas por causa ficam separados.
- **Fonte [conferido]:**
  - balanço em `ben.js:207-212`;
  - saídas por classe com bruto e tara em `ben.js:440-454`.
- As classes vendáveis são parâmetro da rota. Não há histórico da rota [inferido].
- É candidato a Gemini.

**C8 Lotes aprovados na primeira inspeção: Adaptar (depende do D9).**
- Segue o KPI-IND-04 (PRD.md:8689).
- `L.insp` existe (`producao.js:328`, `:562-565`), mas não marca se foi a primeira inspeção ou uma reinspeção [conferido].

**C9 Reclamações e devoluções: Adaptar (depende do D10).**
- Segue o KPI-COM-02: quantidade e valor por causa.
- A devolução com motivo existe (`comDevolverEf`, `comercial.js:362`) [conferido]. A reclamação sem devolução só existe estática no GE-05 (`areas/gestao.py:397`).

#### Crédito
**K1 Limite × utilizado: Adotar.** Lê o `D.CRE` do GE-08 (`areas/gestao.py:583-585`) [conferido]; é estático, mas é uma fonte só.

**K2 Vencimentos: Adaptar.**
- Mostrar o R$ que vence em 30, 60 e 90 dias por linha e, ao lado, os recebimentos previstos, sem fazer razão entre eles.
- Motivo: a CAL-19 (PRD.md:4515) usa caixa disponível, não receita. A razão só entra com o financeiro da seção 3.5.

**K3 Cobertura de garantias: Adaptar.**
- **Fórmula:** garantias físicas (sc) × referência (R$) ÷ saldo devedor.
- O penhor de 30 % da soja está em sacas, sem valor (`areas/gestao.py:579`; `areas/comercial.py:37`).
- Dano a evitar: a mesma saca contar como livre para venda e como garantia. Fica ligado ao E-12 do EX-51.
- **Depende:** a exigência do credor por contrato vai para o D11.

**K4 Endividamento da safra e custo: Adaptar.**
- Dívida ÷ receita líquida esperada.
- Custo efetivo = média dos CET ponderada pelo saldo (`areas/gestao.py:583-587`).
- O barter em sacas fica à parte (CAL-19, sacas devidas) e não entra no % ao ano.
- **Depende do proprietário:** o limite de endividamento é política dele.

**K5 Ficha cadastral em dia: Adotar.** Já existe (`areas/painel_gestao.py:155-160`) e vai para "Ver mais".

**K6 Financeiro (caixa projetado em 30, 60 e 90 dias; a pagar em 7 dias): Adaptar.**
- Entra pela proposta da seção 3.5.
- "Caixa projetado" sem saldo bancário vira "fluxo previsto" (entradas − saídas datadas). O saldo só vem do ERP (KPI-FIN-07).

### 3.3 Captura D1–D13
**D1 Horas de máquina: Adaptar.**
- **Já existe [conferido]:** o turno do app grava início, pausas e fim (`cenario.js:545-557`), mas o fechamento exige horas digitadas (`cenario.js:797`).
- **Adaptação:**
  - As horas passam a ser calculadas: fim − início − pausas. Editar só com motivo.
  - Data e hora ISO, para o turno que passa da meia-noite (T9).
  - O horímetro é gravado na **mesma** coleção de leituras da Manutenção (`dados_manutencao.py:1111`). O CD-03 continua só lendo (`areas/cad_ativos_pessoas.py:144`). A leitura implausível gera aviso (`dados_manutencao.py:23`).
  - Máquina e implemento vêm herdados da alocação.
  - ha/h fora do CD-08 gera alerta.
  - Os ha continuam digitados: o último valor nunca vale para quantidade (AGENTS §3.3).

**D2 Paradas no turno: Adaptar.**
- `cenPausar` existe, sem motivo (`cenario.js:555-557`) [conferido].
- Ganha o motivo em 1 toque. "Quebra" abre um achado para a Manutenção (`manAchRegistrar`, `dados_manutencao.py:885`).
- Validação: soma das paradas ≤ turno.
- Sem ranking (PRD.md:7461).

**D3 Falhas e reparos: Adaptar.**
- **Já existe [conferido]:**
  - início e fim da indisponibilidade em `condHist`, só com o dia (`dados_manutencao.py:69`, `:850-859`);
  - tipo e componente da OM (`:936`);
  - Iniciar e Concluir do mecânico (`manIniciar` em `:733`; `manConcluir` com horas digitadas em `:804`).
- **Adaptação:**
  - Data e hora no bloquear e no liberar.
  - Causa em lista.
  - Horas calculadas de Iniciar a Concluir.
  - O retrabalho vira reincidência (M7).

**D4 Horário e condição da aplicação: Adaptar.**
- A hora do turno existe. Não existem série horária da estação nem carga de tanque no app [conferido].
- No protótipo, falta uma série horária sintética. Sem estação, temperatura, umidade e vento são digitados com teclado numérico.
- Fora do limite: alerta, motivo e aviso ao RT, sem bloqueio (proprietário, 18/10).
- **Depende:** do RT e do EX-54, os limites.

**D5 Perdas na colheita: Adaptar.**
- Dado não existe.
- Método da armação de área conhecida, primeiro para grãos.
- **Depende:** do RT, o nº mínimo de pontos, o tamanho da armação e o método por cultura.

**D6 Entrega de fornecedor: Adaptar.**
- Prometido e recebido já existem e estão ligados (`dados2.py:860-866`) [conferido].
- A promessa original fica imutável, com as revisões à parte (`areas/processo_compras.py:618` sobrescreve hoje). Registro por linha.

**D7 Entrega ao cliente: Adaptar.**
- Janela e quantidade do pedido e a entrega com data e kg já existem (`dados_comercial.py:61-64`; `comercial.js:451-453`) [conferido].
- Falta guardar a promessa original quando a janela muda [inferido].

**D8 Beneficiamento por classe: Adotar.**
- Já existe [conferido]:
  - saídas por classe, descarte, outro destino e perda identificada;
  - balanço que fecha (`ben.js:207-212`, `:427-454`);
  - horas de linha (`ben.js:5`).

**D9 Inspeção de lote: Adaptar.**
- `L.insp` existe, e o resultado já é obrigatório antes de liberar (`producao.js:565`) [conferido].
- Falta a marca automática de primeira inspeção ou reinspeção, pelo histórico do lote.

**D10 Reclamações e devoluções: Adaptar.**
- A devolução com motivo existe (`comercial.js:362`).
- Falta a reclamação sem devolução, com pedido e lote herdados e validação quantidade ≤ entregue. Leva a função do VE-06 legado.

**D11 Metas, referências e parâmetros: Adaptar.**
- **Já existe [conferido]:**
  - meta de produtividade por cultivo (`dados2.py:63-70`);
  - preço de referência com fonte e data (`dados_comercial.py:16-19`);
  - alçadas (CF-01);
  - custo/h (`areas/cad_ativos_pessoas.py:150`).
- **Falta:**
  - plano de comercialização;
  - valor de reposição;
  - calendário de referência (CAL-06, 53.1);
  - limites de cada indicador.
- **Onde:** em Configurações › Indicadores e metas (PRD 55.1, CF-02), sem item novo na barra. Versionado, com fonte, data e quem definiu.

**D12 Contagem de inventário: Adotar.** Já existe no Estoque visível (`areas/processo_estoque.py:124-130`, `:256-268`), com o ajuste por alçada [conferido]. A leitura por código de barras não existe [inferido].

**D13 Água e energia: Adaptar.**
- O volume do hidrômetro já é obrigatório no término (`irrigacao_estado.js:522-547`). O aviso de outorga existe (`:373`) [conferido].
- Falta a energia: leitura do medidor no início e no fim, ou integração.

### 3.4 Fatias
- **F1: Adaptar.**
  - Aplicar as regras ao que já existe e tirar as contagens sem decisão da primeira vista (de acordo com a lista do prompt).
  - Corrigir T3 (cor e 95 % fixos) e T4 (% do orçado em dobro).
  - Captura que já pode começar a contar histórico, porque o turno, as pausas e os eventos do ativo já existem: D1, D2, D3 e D11.
  - D4 grava só o horário. A avaliação da condição espera os limites do RT (EX-54).
- **F2: Adaptar.** Antes do código, combinar a base de custo (T6) e o custo projetado em `custo_dominio.py`, e dar os nomes da CAL-18 ao equilíbrio. O clique precisa do GE-03 lendo o cenário (T7) ou de outro destino.
- **F3: Adotar**, com a A1 e a A5 já adaptadas.
- **F4: Adaptar.** A primeira inspeção depende do D9: trazer o D9, que é pequeno, para esta fatia. PMR e inadimplência dependem da baixa (3.5).
- **F5: Adaptar.** O D12 sai, porque já existe. O MTBF pode começar antes, pelo horímetro (M3).

### 3.5 Financeiro (decisão delegada): proposta do Claude, Adaptar o ponto de partida

**Proposta:** financeiro operacional mínimo no Safrion, sem tela de lista de títulos; contábil, caixa e fiscal no ERP.

| Critério | Como a proposta cumpre | Evidência |
|---|---|---|
| 1. Fechar as cadeias sem beco | O título a receber já nasce de cada saída confirmada (`comTitulos`, `comercial.js:68-74`) [conferido]. O título a pagar nasce do recebimento conferido da NF ligado ao pedido (`dados2.py:864-866`) ou do aceite de serviço da manutenção (`dados_compras_mat.py:23`), com o vencimento pela condição de pagamento do pedido (`dados_compras_mat.py:61`). A baixa reduz a exposição do cliente (`comExpo`, `comercial.js:79`) e reavalia os pedidos retidos por limite | E-8 do EX-51 |
| 2. Um número, uma fonte | GE-04 e GE-05 são estáticos (`areas/gestao.py:333`, `:382-413`) e saem. PC-084, PV-027 e PV-029 só existem neles: nenhuma ocorrência em `dados2.py`, `dados_compras_mat.py`, `dados_comercial.py` ou `comercial.js` [conferido]. A divergência R$ 91.470 × R$ 28.200 some com a saída do GE-05 (o número 28.200 não conferi) | — |
| 3. Não duplicar o ERP | Fora do Safrion: plano de contas, DRE, conciliação bancária, NF-e de saída e saldo bancário. Por isso o Painel mostra "fluxo previsto", não "caixa" (K6) | PRD 55.4, KPI-FIN-07 |
| 4. Com e sem ERP | Com ERP: título e baixa entram pela CF-03 (fila do ERP já simulada, `configuracoes.js:191`). Sem ERP: "Registrar recebimento" na seção a receber da venda e "Registrar pagamento" no pedido (Compras, etapa 6, ou OM), com data, valor, comprovante e chave de idempotência gerada por quem inicia | ENG-021/022 |
| 5. Pagamento por alçada | O pagamento vai a Aprovações com valor, origem e motivo, pelas alçadas por valor (proprietário, 18/10: pagamento de manutenção; a fatura de oficina sai da alçada de Suprimentos). O Safrion só marca "programado". Não há remessa ao banco nem pagamento automático | `decisoes-proprietario-1810.md` |
| 6. Sem item novo nem tela sem decisão | Os títulos aparecem na origem (venda, pedido, OM), em Aprovações e no Painel (Comercial: recebíveis; Crédito: a pagar em 7 dias, que abre Aprovações filtrada). Nenhuma lista nova | — |

- **Muda em relação ao ponto de partida do prompt:** recuso a "lista de títulos num hub existente" enquanto nenhuma decisão a exija. A agenda dos próximos 7 dias é o recorte de Aprovações.
- **Gatilho para rever:**
  - cliente sem ERP que precise de conciliação bancária, porque isso entra no domínio do ERP;
  - ou mudança de preço, contrato ou escopo comercial do produto, o que volta ao proprietário.

## 4. Divergências prováveis a confrontar
1. **J2:** proíbo pintar a fração dentro do polígono (PRD.md:3010, 8.4.4). Outra leitura aceita a pintura com a legenda "proporção".
2. **J6:** rejeito no protótipo. Outra leitura adapta com roteiros guiados sobre o "Restaurar demonstração".
3. **A6:** rejeito o % de conformidade de receituário e carência, porque fica perto de 100 % por construção e as exceções já estão em "Atacar agora". Outra leitura o adota como indicador do RT.
4. **A5:** a faixa de ±5 % só colore, porque a B-R8 não tem tolerância (`cenario.js:626-649`). Outra leitura a usaria como limite de alerta.
5. **P3 e P8:**
   - troco o "% do ciclo decorrido" pelo "% do orçado previsto até hoje";
   - troco "ha × dias até fechar" por ha ÷ dias, e mantenho a classe do dano primeiro.
6. **P1 e P5:** margem sobre receita líquida, com base declarada, e dois números de equilíbrio (CAL-18). Pode exigir o Gemini.
7. **M5:** o denominador do cumprimento de preventiva hoje exclui as vencidas não feitas (`dados_manutencao.py:1183`).
8. **T1:** o texto "aprovação individual, decisão fixa" do EX-53 e do J7 foi superado pela decisão do proprietário de 18/10. O Painel continua sem aprovar.
9. **Financeiro:** título a pagar no recebimento conferido, "fluxo previsto" em vez de "caixa" e nenhuma lista de títulos.
