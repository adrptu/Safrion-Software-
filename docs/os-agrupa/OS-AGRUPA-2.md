# OS-AGRUPA-2 · Frentes de trabalho: agrupar O.S. e talhões semelhantes para executar em sequência

**Pedido do proprietário (18/10/2026):** "na parte de ordem de serviço agricola, o agrupamento de OS e talhoes semelhantes para facilitar execucao e logistica contínua na fazenda esta muito ruim. pegue as melhores praticas e referencias do mundo nisso e crie algo mais inteligente, intuitivo, prático."

Autor: Claude. Revisor: Codex, que é o autor do OS-LOTE (`docs/integracao/V71/OS-LOTE.md`) e da sua F1. Regime leve do protótipo (AGENTS §3.5): implanta, testa e revisa depois. Os patches no código do OS-LOTE são do integrador e estão avisados no PR #47.

## 1. O que estava ruim (executado no render da v134, 18/10)

| # | Defeito | Dano |
|---|---|---|
| 1 | Só agrupa caldas idênticas e só as cinco O.S. sintéticas "Talhão demonstrativo A–E" e "Parcela demonstrativa A–D". Esses talhões não existem no mapa. Nenhuma O.S. real da semente forma grupo. | O proprietário não vê o caso real da fazenda. |
| 2 | Calcário (OS-0502), plantio (OS-0431) e sexagem (OS-0511) saem com "Sem conjunto · alocar pulverizador na O.S.". | Mensagem errada: trata toda operação como pulverização. |
| 3 | Sem mapa, sem rota e sem distância entre talhões. A sequência vem do prazo e do número da O.S. | Não ajuda a logística: a equipe atravessa a fazenda à toa. |
| 4 | Nas O.S. comuns, cada talhão prepara as suas cargas ("sem transferir restos entre O.S."), mesmo com o mesmo pulverizador e a mesma calda. | Mais preparos de calda e sobra no fim de cada talhão. |
| 5 | "Fora de grupo (12)" lista O.S. encerradas, em conferência e em execução, uma por uma. | Ruído: esconde as poucas que importam. |
| 6 | A programação pede o fuso da fazenda num seletor e a data e hora num campo livre. | Pede dado que o sistema já tem. |

## 2. Referências (consultadas em 18/10/2026)

| Fonte | Prática | Decisão |
|---|---|---|
| John Deere Operations Center, Work Planner ([RDO, visão geral](https://www.rdoequipment.com/resources/blogs/john-deere-work-planner-overview); [Farming Ahead](https://www.farmingahead.com.au/software-and-apps/news/1402934/john-deere-brings-work-planner-to-its-operations-center)) | Plano de trabalho por talhão com produto, variedade e prescrição. O plano aparece na cabine quando o operador chega ao talhão. | **Adotar** o plano por talhão em sequência. **Adiar** o envio à máquina (integração). |
| Agworld, Tank Mix Calculator ([ajuda, 18/10](https://help.agworld.com/en/articles/4099455-use-the-tank-mix-calculator-on-the-agworld-iphone-and-ipad-app)) | Quanto produto vai em cada carga do tanque e quantas recargas a atividade exige. | **Adotar** com uma melhoria: a carga segue de um talhão para o próximo na mesma frente. Só a última é parcial. |
| Bochtis e Sørensen, "The vehicle routing problem in field logistics", partes I (2009) e II (2010), *Biosystems Engineering*. Ver também "Machinery management in bio-production systems: planning and scheduling aspects" ([CIGR Journal](https://cigrjournal.org/index.php/Ejounral/article/view/1719)). | A logística de campo como problema de roteamento com janelas de tempo. | **Adaptar:** a janela comum é obrigatória e a rota usa a heurística do vizinho mais próximo a partir da janela que fecha primeiro. Fica explicável e sem otimizador. |
| Plessen, "Coupling of Crop Assignment and Vehicle Routing for Harvest Planning in Agriculture" ([arXiv 1703.08999](https://arxiv.org/abs/1703.08999)) | Visitar em sequência os talhões da mesma cultura, minimizando o deslocamento dentro da janela. | **Adotar** o agrupamento por cultura e operação com sequência pelo mapa. |
| Extensões de limpeza de pulverizador ([SDSU](https://extension.sdstate.edu/general-cleaning-recommendations-sprayer-equipment); [UMN](https://agrisk.umn.edu/Library/AMPRecord/mitigating_herbicide_damage_to_specialty_crop1)) | Limpeza entre produtos conforme a bula. Tanques separados para herbicida e para fungicida e inseticida. | **Adotar** a regra de juntar só a mesma calda, o que dispensa limpeza entre talhões. Trocar de calda continua com limpeza conforme a bula, fora da frente. |
| Solinftec, ALICE ([AgFeed](https://agfeed.com.br/agro-brands/apresentado-por-solinftec-agro-brands/alice-no-pais-da-autonomia-solinftec-lanca-agentes-de-ia-e-inaugura-nova-era-nas-operacoes-agricolas)) | Sugestão contínua com a decisão nas mãos do produtor. | **Adotar:** o sistema sugere e a pessoa confirma. Nada se agrupa sozinho. |

Estar no mercado não prova a regra de domínio. As travas abaixo vêm do PRD 41.10 e do OS-LOTE, não das referências.

## 3. Regras do EX-54 F1 (fonte única: `os_frentes.js`; testes `os_frentes_unit.js`)

Prompt do proprietário: `docs/integracao/V73/pedidos-1810/prompt-safrion-frentes-trabalho.md` e a especificação viva `frentes-trabalho-safrion.html`. Esta seção substitui a versão anterior desta especificação (diálogo com cargas contínuas).

- **R1 · Frente.** Um conjunto (trator, implemento e operador) percorre uma sequência de talhões da mesma família.
- **R2 · Candidatas.** O.S. não encerradas do recorte da lista, em qualquer etapa antes de Em conferência, com saldo. A frente executa só as liberadas; as outras aparecem com quem decide (a aprovação é do RT, por O.S. e versão).
- **R3 · Família pelo implemento.** Plantadeira → Plantio; distribuidor → A lanço; senão, pela operação (pulverização, calagem, plantio). Fertirrigação vai pelo pivô e fica fora. Famílias nunca se misturam.
- **R4 · Compatibilidade.**
  - Pulverização e a lanço juntam pelos produtos ativos (o adjuvante não separa).
  - Calda idêntica (produtos, dose e unidade canônicas, e vazão) continua.
  - O mesmo produto com outra dose é nova calda na mesma frente.
  - O adjuvante diferente é troca de calda.
  - Vazão ainda não definida não vira outra calda: entra com "Definir vazão" e não conta na carga.
  - Plantio junta pela cultura: troca de semente pede a limpeza da plantadeira.
  - A lanço com outra dose pede nova regulagem.
- **R5 · Herbicida por último**, mesmo com a janela mais curta, e a frente fecha com a tríplice lavagem.
- **R6 · Período.** Junta as janelas que se cruzam ou se seguem; a que começa depois de todas abre outra frente.
- **R7 · Ordem.** Primeiro a janela que fecha antes. No empate, a mesma calda e depois o talhão mais perto. A distância é a haversine sobre lon/lat. No desenho sem escala, a ordem é pela proximidade, sem km.
- **R8 · Ganho.** A frente mostra km da rota contra cada O.S. sozinha (ida e volta da sede) e cargas.
  - As cargas ficam fechadas por O.S. até a decisão do RT sobre a calda contínua com rateio.
  - A carga contínua aparece só como ganho a decidir.
- **R9 · Quantidade.** O produto de cada O.S. vem da regra única (`cenQtd`). A frente soma as O.S.
- **R10 · Nada muda sozinho.** A frente não aprova, não libera, não reserva e não grava. "Agrupar N O.S. desta calda" abre a conferência do OS-LOTE com as O.S. na ordem da rota.

## 4. Tela

- **Visão "Frentes"** no seletor de visões da O.S. (sexta visão, ícone de rota; endereço `?view=frentes`). Substitui o diálogo e o botão "Agrupar O.S. semelhantes".
- **Lista de frentes** (cartões), com produto, família, talhões, hectares, caldas e janela.
- **A frente escolhida:**
  - por que juntou;
  - mapa com a rota numerada e a sede;
  - tabela da rota (ordem, talhão, O.S., área, janela, distância e situação);
  - trocas (calda, regulagem, limpeza, tríplice lavagem);
  - pendências com quem decide;
  - produtos;
  - ganho em km e cargas.
- **"Fora das frentes (N)"** recolhido, com o motivo de cada O.S.
- **Celular (390 px):** uma coluna.

## 5. Semente de demonstração (dados sintéticos)

- **Lagoa Grande:** OS-0584 a OS-0594, a semana da especificação viva (acaricida, fungicida e calagem), com ficha técnica completa.
- **Santa Rita:**
  - OS-0595 a OS-0599: dessecação em T1-B, T3 e P1, com P1 sem vazão;
  - KCl a lanço em P2 e T2.
- **O que essas O.S. não fazem:**
  - não desviam a numeração das O.S. novas;
  - não entram na demanda de compra (`cenOsDem` e `dados2.os_dem`), porque a demonstração não muda os totais de compra e estoque já conferidos.
- **Selo:** "Demonstração".
- **IDs:** os de 0601 em diante são das tarefas automáticas da Irrigação.

## 6. Aceite (executado)

- **Unitário:** `node os_frentes_unit.js`, com 15 casos (R2 a R9, com oráculo independente da distância).
- **Navegador:** `os_frentes_test.py` (F1 a F9, a 1440 e 390 px):
  - Lagoa Grande: frentes de acaricida (5 pivôs, 2 caldas), fungicida (4) e calagem (3);
  - Santa Rita: OS-0421 com OS-0424, com o adjuvante como troca de calda, e OS-0420 com OS-0431 no plantio;
  - "Definir vazão" e quem decide;
  - nada é aprovado, liberado ou reservado;
  - a conferência do OS-LOTE abre na ordem da rota;
  - sem erro de script e sem rolagem horizontal.
- **Contraprova:** o render da v134 dá 2/18 (`logs/contraprova_os_frentes_v134.log`).

## 7. Fora desta fatia (F2 e F3), com a condição de retorno

- **"Programar frente"** (capacidade, linha do tempo e divisão por conjunto): F2, depois do aceite da F1.
- **Clima, rendimento e limites de calda:** sem valores fixos no código. Voltam pelo cadastro (CD-08) e pela previsão, na F3.
- **Calda contínua com rateio:** volta com a decisão do RT (pacote Gemini/Codex de domínio).
- **"Mostrar frentes" no Mapa e "Roteiro de hoje" no app:** com o EX-55 (mapa nas telas).
- **Envio do plano à máquina** (ISOXML ou API do fabricante): volta quando houver integração autorizada pelo proprietário.
