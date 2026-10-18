# EX-57 · Confronto Claude × Codex (18/10/2026)

- **Fontes:**
  - Claude: `EX-57-validacao-claude.md`, lacrado em sha256 `7a169c9c…` e aberto depois da publicação do Codex;
  - Codex: avaliação independente v1, PR #47 comentário 6254095379, feita sem ler o lacrado.
- **Divergências:** resolvidas por fonte. Nenhuma depende de voto.
- **Próximos passos:** o Codex registra o desenho final no checkpoint; em seguida vão o pacote único ao Gemini real (§4) e a validação do RT.

## 1. Onde concordamos (vira desenho)

- Uma função de data com estado (prevista, confirmada, âncora ausente, fora do recorte), origem e versão.
- Eventos do ciclo com data prevista e real.
- Fase proposta por evento ou idade e confirmada pela agrônoma, nunca automática. As atividades em aberto ficam para manter, cancelar ou reprogramar.
- Parâmetros por cultura e cultivar, versionados, com fonte e RT.
- Nada de menu ou camada novos: encaixe nos detalhes e na camada Estádio. Painel, EX-43, 52, 53 e 54 consomem a mesma fonte.
- Migração com prévia e adoção explícita, sem trocar datas de plano em uso.
- Fora do recorte da safra = consulta.

## 2. Pontos do Codex que mudam o meu lacrado (aceitos)

| # | Codex | Meu lacrado | Decisão |
|---|---|---|---|
| C1 | Recepa e poda **não** reiniciam o plantio: guardar o evento e o "tempo desde" | M1 media a idade a partir da recepa ou do replantio | **Codex.** Idade cronológica desde o plantio original, mais "tempo desde a última renovação". O replantio total abre um novo plantio |
| C2 | Replantio parcial = coorte própria, ligada à anterior; não rejuvenescer o talhão todo | Não tratava coorte | **Codex.** A coorte usa a unidade que já existe, a parcela do cultivo (`local`), sem entidade nova. Várias coortes aparecem como "múltiplas", nunca como média |
| C3 | DAPC sem colheita cai no plantio: tem de virar **âncora ausente** | R1 mostrava a divergência, sem o estado | **Codex.** Estado "âncora ausente", com a saída "registrar a colheita prevista". Nunca data presumida |
| C4 | Não eliminar DATA com ano: operação excepcional datada, marcada como não recorrente | M5 já previa aviso, não proibição | **Codex**, mais explícito: a DATA vira "não recorrente" |
| C5 | DAP continua significando plantio. Não proibir por fase; avisar incompatibilidade de finalidade ou âncora | M8 dizia "DAP de formação nunca gera numa perene em produção" | **Codex.** O DAP vale. A ocorrência fora do recorte vira consulta. Plano de formação adotado num cultivo em produção mostra o aviso do prompt ("DAP é da formação: este cultivo está em produção") com a saída |
| C6 | Evento identificado por ID + ciclo + escopo, nunca "o último evento" global | M3 tinha `{tipo, safra,…}` | **Codex.** `evento{id, ciclo, escopo, tipo, prevista, real, fonte, estado}` |
| C7 | O.S. já criada, liberada ou executada não muda sozinha quando o evento real chega | Não estava | **Codex.** O evento real recalcula só as propostas futuras. A O.S. existente recebe proposta de reprogramação com prévia |
| C8 | "Mensal no dia 20" ≠ "a cada 30 dias". Horizonte finito. Identidade estável e idempotente da ocorrência | INT sem fim | **Codex.** Entram o tipo "mensal no dia N" e o horizonte = recorte da safra. A identidade da ocorrência é ciclo + atividade + data-alvo |
| C9 | Política explícita para 29/02, dia 31 e limites da safra | Só 29/02 | **Codex**, com estas propostas para o RT decidir: 29/02 → 28/02; dia 31 → último dia do mês; recorte [início, fim] inclusivo |
| C10 | Mamão de demonstração colhe nos dias 20 e 18: não inferir periodicidade | Migração propunha "INT 30 dias" | **Codex.** A migração é proposta com prévia, e a escolha (mensal dia N, intervalo ou manter datas) é da agrônoma |
| C11 | Ocorrência resolvida uma vez por identidade, mesmo com safras sobrepostas | Meu A3 (demanda duplicada), pendente de reprodução | **Juntos.** A regra do Codex é a correção geral do A3. O teste do A3 prova a correção |
| C12 | A 1ª colheita observada não prova a transição do pivô inteiro | M7 por evento | **Codex.** A proposta mostra a cobertura (coortes, área) e a agrônoma confirma |

## 3. Pontos do Claude que o Codex não trazia (mantidos)

- **F0 · regra de data única antes de tudo.** Há 6 cópias e 2 divergem: `dados2.data_atividade` cai no plantio quando a colheita do plano é DATA; `inicio._data_atv` devolve nada em DAPC/DANC sem colheita. Entra um teste de paridade JS × Python × Mapa × AG-02 em todos os planos × cultivos × safras.
- **Função única de fase.** Hoje são 6 cálculos com 3 conjuntos de limiares para o mamão. Passam a ler os parâmetros por cultura.
- **Maquetes sem função:** `engine.py:111,724-729` e PL-01 "Revisar idades" são ligadas à regra ou removidas.
- **A3 como teste:** perene vinculada à 2027/28 com plano de data com ano. A demanda de compra só da 2027/28.
- **Custo de formação separado do custo da safra de produção:** vai ao Gemini (Q7) e ao RT.
- **R-24 depois da F2:** o "Vincular ciclo" sugere o plano da fase, com confirmação (P25).

## 4. Pacote único para o Gemini real (o Codex envia e registra)

**Pedido:** críticas ao modelo, não doses ou prazos universais. Sem dados reais.
1. **Fases e unidade de identidade por cultura:** café, mamão, citros, banana, uva e cana. Formação · produção · renovação · encerrada servem? A unidade é planta, coorte, ciclo ou corte (soca, ressoca)? Quais os contraexemplos?
2. **Fase de manejo × fenologia observada:** como separar sem duplicar?
3. **Gatilhos:**
   - os tipos: dia e mês, mensal no dia N, intervalo, dias em relação a evento (colheita, florada, poda, recepa), dias após o início da safra, idade em meses e estádio;
   - eles bastam? Falta graus-dia?
4. **Floradas múltiplas** (café, citros): qual florada ancora? Data prevista pelo histórico é aceitável até a real?
5. **Produção contínua** (mamão, banana) com parcelas de idades distintas: intervalo ou calendário fixo, ou contagem e estimativa?
6. **Entrada em produção:** por evento ou por idade? Quais parâmetros exigem RT por cultura, cultivar e região, e quais **não** podem ser inferidos da idade?
7. **Custo de formação:** separar da safra de produção, para o custo por saca não carregar a implantação? Só a separação gerencial; o Safrion não contabiliza.

## 5. Fatias (consenso proposto)

| Fatia | Conteúdo |
|---|---|
| **F0** | Regra de data única com paridade e reprodução do A3. Sem mudança visível |
| F1 | Identidade (ciclo e coorte), idade cronológica e "tempo desde", fase com histórico (proposta → confirmada), âncora ausente, função única de fase com parâmetros, exibição em 3 lugares, maquetes resolvidas |
| F2 | Dia e mês, mensal no dia N, intervalo e dias após o início, com horizonte da safra; ocorrência com identidade única (corrige o A3); fora do recorte = consulta; DATA não recorrente; migração com prévia e adoção |
| F3 | Eventos (florada, poda, recepa, 1ª colheita) com prevista e real, e reprogramação controlada das O.S. |
| F4 | Proposta de troca de fase com cobertura, atividades em aberto, estádio confirmado em vistoria, R-24 sugerindo o plano da fase |

**Condição:** nenhuma fatia começa a ser codificada antes do Gemini real (§4) e da validação do RT. A F0 é exceção: não muda regra agronômica, só unifica o que existe, e pode entrar quando abrir uma frente (§3.6).

**Autoria:** o Claude implementa e o Codex revisa e registra.

## 6. Ajustes da revisão do Codex (6254156428), aceitos

1. **Identidade da ocorrência (corrige C8).** O par "ciclo + atividade + data-alvo" não é estável: a reprogramação cria outra chave. Vale então:
   - ID persistente = escopo (ciclo) + atividade de plano versionada + âncora (evento por ID, ou a recorrência) + **ordinal da recorrência**;
   - a data-alvo é atributo revisável, com histórico;
   - recalcular nunca cria outra obrigação nem perde o vínculo com a O.S.
   
   Prova no contrato: a mesma florada-7 reprogramada de 01 para 03 mantém um único ID.
2. **"Fora do recorte = consulta" vale só para gerar ocorrência histórica *nova*** (corrige §1, §5 e o M8 do lacrado):
   - a obrigação já criada ou em aberto, a execução e o custo real **ficam**, com identidade compartilhada entre safras (C11);
   - o que sai do custo e da demanda é só a ocorrência nunca gerada que cairia antes do recorte;
   - nada se apaga, nada se exclui.
3. **F0 deixa de ser "sem mudança visível".** Corrigir as cópias divergentes muda o resultado. A F0 vira duas partes:
   - **F0a:** extração que preserva o comportamento atual, caso a caso, com testes de paridade onde as cópias concordam e a lista explícita dos casos em que discordam;
   - **F0b:** correção explícita por caso, com a referência declarada, o impacto medido (antes × depois) e uma regressão por caso. Exemplo: DAPC/DANC sem colheita deixa de cair no plantio e vira **âncora ausente**, já reproduzida pelo Codex.
   
   Nenhuma regra divergente vira canônica por ser maioria entre as cópias.

**Contrato de coorte (responde à condição do C2):**
- A identidade da coorte é o **`ciclo`**. Ele persiste entre safras pelo vínculo da R-24, que copia o `ciclo`, a cultura, o plantio e a parcela (`local`). O `local` é só o escopo espacial.
- **Replantio parcial:** "Dividir" a parcela e abrir um **novo `ciclo`** na parte replantada, com `substitui` apontando para o ciclo anterior. A parte que não foi replantada continua no ciclo antigo, com idade e histórico intactos.
- A paridade entre parcela e coorte não é presumida. **Aceite da F1:** o mesmo ciclo mantém o ID depois de vincular a 2027/28 e depois de um replantio parcial.

**Gemini:** o pacote leva as 7 perguntas do §4 mais estes limites: identidade persistente, preservação de obrigações e custos reais e correção explícita das cópias. É uma consulta só.

## 7. Parecer do Gemini real (6254228563) e crítica do Claude à triagem do Codex

Consulta única Pro/HIGH, payload SHA256 `14e1a0a1…4dafd9f`, sem fonte agronômica consultada. Nada abaixo é validado: percentuais de replantio, custo de graus-dia e limiares ficam de fora até ter fonte e RT.

| # | Gemini | Codex | Claude | Como fica no contrato |
|---|---|---|---|---|
| G1 | Dividir a parcela a cada replantio fragmenta o polígono | Adaptar: replantio disperso sem divisão | **Concordo, com dois modos** | **Corrige o §6.** Replantio em **bloco** (parte contígua): "Dividir" + novo `ciclo` com `substitui`, como antes. Replantio **disperso** (falhas): novo `ciclo` com `substitui`, sem dividir a parcela nem mudar a área, com cobertura em **plantas** e precisão declarada (contada ou estimada). A O.S. do talhão cobre todos os ciclos da parcela; a atividade própria da coorte dispersa usa plantas como base. A conta continua a regra única (`cenQtd`, dose × base); hoje a O.S. só tem área como base, e a base em plantas entra na F3 |
| G2 | Âncora sem evento = data nula, nunca plantio | Já previsto (C3) | Concordo | Sem mudança |
| G2b | Sem evento real, a tarefa fica sem data | Rejeitar exigir data real | **Concordo com o Codex** | Três estados: prevista (com origem), confirmada, âncora ausente. A prevista sustenta a demanda de compra e o calendário; sem ela a fazenda compra tarde |
| G3 | Idade cronológica × idade do ciclo | Adotar, sem reset automático | Concordo | Já é o C1 ("tempo desde"). No CE1, a recepa só **propõe** a fase Renovação |
| Q2/Q7 | Fase de manejo decide imobilizado × despesa; custo de formação vira ativo biológico | Rejeitar prescrição contábil | **Concordo e separo os conceitos** | A fase decide **o plano**, nada contábil. A classificação contábil é do proprietário e do contador, fora do Safrion. A fase vigente na data de execução sai do histórico de fase. Separar custo de formação e de produção fica para o EX-53 e o financeiro, que voltam a isso no confronto deles |
| Q1/CE3 | Uva com 2 ciclos no ano; cana com socas | Adaptar | **Sem entidade nova** | O ciclo produtivo é a sequência entre eventos com ordinal (poda k → colheita k), já presente no ID da ocorrência (§6.1). Teste sintético: uva com duas podas na mesma safra gera duas sequências com IDs distintos, e nada bloqueia a segunda. Plano por número da soca (cana) fica de fora até a cana entrar no escopo |
| CE5 | Banana: cortar a planta-mãe não encerra a coorte | — | Adotar como teste | A colheita é evento; só a erradicação ou a renovação total encerram o `ciclo` |
| Q4 | Floradas: ID + tipo + ordinal; a "principal" é marcada pelo RT | Não citado | **Adotar** | A atividade do plano aponta tipo de evento + seletor (principal, ordinal n ou cada um). Teste: reprogramar a florada 1 não move o que está ligado à florada 2 |
| Q5 | Produção contínua por calendário ou intervalo | Opção, não regra universal | Concordo | Intervalo com início e fim é um dos tipos do F2; o RT escolhe por cultura |
| Q6 | Nunca inferir produção pela 1ª colheita | — | **Já é proposta (C12)** | O gatilho de entrada em produção (1ª colheita, idade ou produtividade) é parâmetro por cultura e cultivar, validado pelo RT. No cenário, MAMAO-IMP fica com a 1ª colheita como exemplo de proposta |
| CE4 | Evento antecipado não altera a O.S. em silêncio | — | Já é o C7 | A ocorrência sem O.S. recalcula e mostra a origem; a O.S. existente recebe proposta com prévia |
| Mapa | Cor da coorte predominante + hachura se mistura significativa | Mostrar múltiplas coortes em texto; critério a validar | **Sem limiar** | Cor da coorte com maior cobertura e marca "misto" sempre que houver mais de um ciclo na parcela, com o texto "Produção · 7a8m + replantio 4% · 1a2m" na dica e no `aria-label`. Sem limiar não há critério a validar, e a minoria nunca some. Fica na camada Estádio, sem camada nova |
| a11y | `aria-describedby` obrigatório para a origem da data | Técnica possível | Concordo com o Codex | A origem é texto visível ao lado da data ("15 dias após a florada de 12/09/2027"); o leitor de tela já a lê |
| UX | Conciliação no próprio detalhe, sem menu novo | — | Adotar | Já é a regra master-detail |
| Bissexto | Decisão administrativa do RT | — | **Decisão técnica** | O editor de plano não aceita 29/02 como dia e mês recorrente e pede 28/02 ou 01/03. DAP e intervalos contam dias corridos. Nada vai ao RT |
| GD | Graus-dia como extensão futura | — | Concordo | Fora do escopo: exige dado climático contínuo, e integração com custo é do proprietário |
| N+1 | Calcular idade e fase em lote | — | Nota do software real | Um serviço de domínio (ENG-011) devolve o lote; o protótipo já calcula no cliente |

**O que muda no contrato:** só o G1 (replantio disperso) e o seletor de florada (Q4). O resto já estava coberto ou fica de fora com motivo.

**Continua valendo:** o RT valida os parâmetros por cultura antes de virarem regra, e a F0a pode entrar quando abrir uma frente (§3.6). As F1 a F4 esperam o RT.
