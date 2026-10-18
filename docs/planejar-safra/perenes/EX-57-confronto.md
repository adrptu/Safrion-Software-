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
