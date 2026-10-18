PROJETO: Safrion (Do Talhão à O.S.) · EX-57 · Perenes: idade, fase e ciclo no plano agronômico

PEDIDO DO PROPRIETÁRIO (18/10/2026)
Pergunta: "Quando temos uma perene já implantada e ela tem operações no plano agronômico por DAP, estamos já tratando a idade dela para o DAP funcionar na safra?" Depois da resposta ("em parte"), pediu: "Faça prompt para nossas IA resolver isso da melhor forma possível."

COMO TRABALHAR (protocolo da equipe, sem exceção)
1. Leia AGENTS.md, docs/STATUS.md, o cabeçalho do checkpoint da issue #1 e o protocolo canônico. Este prompt não substitui o PRD nem as decisões NAV/DS.
2. Antes de qualquer código, Claude e Codex melhoram este desenho de forma independente: cada um reproduz o comportamento atual no código, confere o modelo proposto e decide Adotar, Adaptar ou Rejeitar cada parte. Divergência se resolve por fonte ou reprodução; o Codex registra no checkpoint (só ele edita o checkpoint).
3. Gemini real é obrigatório neste item, porque a decisão é agronômica e muda o modelo de dados: pacote mínimo (as fases, os gatilhos e os parâmetros por cultura abaixo), sem dados reais, pedindo contraexemplos por cultura (café, mamão e, para não fechar o modelo, citros, banana, uva e cana). Não simule nenhum modelo.
4. O RT (Ana) valida os parâmetros por cultura e cultivar antes de virarem regra; até lá ficam como exemplo configurável, com fonte.
5. Só depois implante, por fatias, com revisão cruzada: quem revisa integra o PR do outro.

O QUE ACONTECE HOJE (versão publicada 1792342402-4b90, conferido no código do Planejar safra)
- Regra única de data da atividade (dataAtv no SAF; espelho em soloDataAtv no AG-02):
  - DAP: data de plantio do cultivo + dias;
  - DATA: data fixa do calendário, com ano;
  - DAC: dias antes (DANC) ou depois (DAPC) da colheita do cultivo.
- O DAP conta sempre da data de plantio original. Na formação funciona: o plano "Mamão Formosa · implantação irrigada" (MAMAO-IMP) vai da calagem (DAP −60) ao "Início da colheita" (DAP 270), usado pelos pivôs plantados em 2026.
- Os planos de produção das perenes não usam DAP; usam data com ano:
  - "Mamão Formosa · produção irrigada" (MAMAO-PROD): datas de 05/10/2026 a 20/01/2027, inclusive cada colheita mensal;
  - "Mamão Formosa produção" (MAMAO-F): 01/10, 15/10 e 01/11/2026;
  - "Café arábica produção" (CAFE-AR): adubações em 15/10 e 15/12/2026, fungicida em 20/01/2027, colheita em 20/05/2027, mais adubação pós-colheita (+30 dias) e poda de esqueletamento (+45 dias) contadas da colheita.
- Plano por DAP numa perene antiga (ex.: café C1, plantado em 15/01/2019) gera datas anos atrás; o Planejar safra só avisa "ocorrências antes do início da safra". A calagem sugerida pelo laudo diz "DAP −60 já passou" e usa a chegada de uma compra nova.
- Lacunas:
  1. O cultivo perene não tem idade nem fase (formação, produção, renovação). A troca do plano de implantação para o de produção é manual; depois do DAP 270 o plano de implantação acaba e a lavoura fica sem atividade até alguém trocar o plano.
  2. Os planos de produção só valem para a safra 2026/27: as datas têm ano e precisam ser refeitas a cada safra.
  3. Não há gatilho por florada, poda, recepa, início do ano agrícola, estádio fenológico, idade em meses ou intervalo fixo (produção contínua do mamão).
  4. A ocupação trata a perene como "sem fim" (OC_INF), o que está certo para a área, mas a idade não aparece em lugar nenhum.

O MODELO A DESENHAR (ponto de partida; Claude, Codex e Gemini melhoram)
1. Cultivo perene
   - Data de plantio (ou de recepa ou replantio, quando houver) e, dela, a idade exibida em anos e meses ("Café Catuaí 144 · plantado em 15/01/2019 · 7 anos e 8 meses", na data do cenário, 23/09/2026).
   - Fase com histórico de datas: formação → produção → renovação (recepa, esqueletamento, replantio) → produção, e encerramento (erradicação). A fase vigente decide qual plano vale.
   - Eventos do ciclo registrados com data real: florada principal, poda, recepa, início e fim de colheita, primeira colheita. Os eventos alimentam os gatilhos.
2. Gatilhos do plano agronômico
   - Formação e renovação: DAP (dias após o plantio) e "dias após a recepa ou o replantio".
   - Produção, sempre repetível a cada safra:
     - dia e mês sem ano ("todo 15/10");
     - dias antes ou depois de um evento do ciclo do mesmo ciclo produtivo: colheita (já existe), florada, poda;
     - dias após o início da safra do cultivo;
     - estádio fenológico, com data prevista pelo histórico e confirmada em vistoria;
     - intervalo fixo para produção contínua ("a cada 7 dias", "a cada 30 dias"), com início e fim;
     - idade em meses, para atividades que dependem da idade da planta.
   - A data prevista sai do gatilho e passa a ser a data confirmada quando o evento real acontece (ex.: a florada real de 2027 desloca as atividades ligadas à florada).
3. Planos por fase e por cultura
   - Cada plano declara a fase a que serve (formação, produção, renovação) e, para perenes, deixa de ter data com ano.
   - Parâmetros por cultura e cultivar, com fonte e validação do RT: idade ou evento que muda de fase (ex.: primeira colheita; no cenário, o plano de implantação do mamão marca o início da colheita no DAP 270), duração típica de cada fase e eventos do ciclo que cada cultura usa (café: florada, colheita, poda; mamão: produção contínua, desbaste, renovação do pomar).
4. Mudança de fase
   - Por evento (ex.: primeira colheita registrada) ou por idade configurada: o sistema propõe "Os pivôs X entram em produção: passar ao plano de produção" e a agrônoma confirma, um cultivo ou um grupo por vez, com registro de quem e quando. Nada muda sozinho.
   - As atividades de formação que já passaram não são geradas; as que estão em aberto na troca aparecem para decidir (manter, cancelar ou reprogramar).
5. Geração das atividades na safra
   - Ao vincular uma perene a uma nova safra (o Planejar safra já tem o vínculo), as ocorrências da safra saem dos gatilhos repetíveis da fase vigente e dos eventos do ciclo, nunca do DAP da formação.
   - Ocorrência que cairia antes do início da safra não é gerada como pendência: aparece como "fora desta safra" com o motivo, só para consulta.
   - A O.S. nasce com a janela calculada e mostra de onde veio a data ("15 dias após a florada de 12/09/2027").
6. Onde aparece
   - Planejar safra e cadastro do talhão: idade, fase e próximo evento do ciclo.
   - Planos agronômicos: fase do plano e tipo de cada gatilho; aviso quando um plano de perene ainda tem data com ano.
   - Mapa e visão Mapa (EX-55): "Mostrar: fase e idade" na camada Estádio.
   - Calendário da safra (EX-52 J5), frentes (EX-54), indicadores de produtividade por idade (EX-53) e Raio-X do alvo (EX-43, controle por estádio) usam a mesma idade, fase e eventos.

MIGRAÇÃO DOS DADOS DO CENÁRIO
- Café C1 (plantado em 15/01/2019, plano CAFE-AR): fase produção; datas com ano viram dia e mês ou dias em relação à colheita e à florada.
- Pivôs de mamão plantados em 2025 com MAMAO-PROD e o talhão T7 com MAMAO-F: fase produção; colheitas mensais com data viram intervalo fixo de produção contínua.
- Pivôs plantados em 2026 com MAMAO-IMP: fase formação; ao atingir o evento ou a idade configurada, a proposta de troca para produção aparece para a agrônoma.
- Planos em uso não mudam no meio da safra sem nova versão publicada e adoção (EX-51 R7 e o versionamento que o protótipo já tem).

FATIAS (ordem sugerida; Claude e Codex podem reordenar com motivo)
F1 Idade e fase no cultivo perene (com histórico) e exibição em Planejar safra, cadastro do talhão e camada Estádio; aviso para plano de perene com data com ano.
F2 Gatilhos repetíveis (dia e mês, intervalo fixo, dias após o início da safra) e geração na safra a partir deles; migração dos planos CAFE-AR, MAMAO-PROD e MAMAO-F.
F3 Eventos do ciclo (florada, poda, recepa, primeira colheita) com data prevista e real, e gatilhos ligados a eles.
F4 Proposta de mudança de fase com confirmação da agrônoma, tratamento das atividades em aberto e estádio fenológico confirmado em vistoria.
Cada fatia: desenho independente de Claude e Codex → Gemini real nos pontos agronômicos → aceite medido antes do código → implantação → revisão cruzada → publicação no artefato existente com versão e mudança concreta.

ACEITE
- O café C1 mostra "7 anos e 8 meses · fase produção" na data do cenário (23/09/2026) e, ao vincular à safra 2027/28, gera as atividades da nova safra sem editar data nenhuma.
- Um plano por DAP aplicado a uma perene em produção não gera ocorrências passadas como pendência; aparece "DAP é da formação: este cultivo está em produção", com a saída (escolher o plano da fase).
- Um pivô em formação (MAMAO-IMP) que registra a primeira colheita recebe a proposta de passar ao plano de produção; nada muda sem a confirmação da agrônoma, e a troca fica registrada.
- Colheita do mamão como produção contínua gera as O.S. pelo intervalo configurado, sem data com ano no plano.
- Uma florada real registrada desloca as atividades ligadas a ela, mostrando a origem da data na O.S.
- Testes unitários da regra de data (cada tipo de gatilho, virada de ano, ano bissexto, evento sem data real, fase trocada no meio da safra) com o mesmo resultado na tela, na O.S. e no espelho do AG-02.

NÃO FAZER
- Trocar fase ou plano automaticamente, sem confirmação da agrônoma.
- Fixar no código idade de entrada em produção, duração de fase ou intervalo de colheita: são parâmetros por cultura e cultivar, com fonte e validação do RT.
- Gerar como pendência atividade de formação que já passou numa lavoura em produção.
- Duplicar a regra de data: continua uma regra só, usada pelo Planejar safra, pela O.S., pelo AG-02 e pelos espelhos de teste.
- Criar item novo na barra principal ou camada nova no Mapa.

ENTREGA (no canal registrado)
- Reprodução do comportamento atual (arquivo e trecho) e validação de cada lacuna, por Claude e por Codex.
- Parecer do Gemini real e validação do RT para os parâmetros por cultura.
- Modelo de dados (cultivo, fase, evento do ciclo, gatilho), regra de data e plano de migração do cenário.
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado. Suposições e pendências com gatilho de retomada.
