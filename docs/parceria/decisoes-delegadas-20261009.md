# Decisões delegadas de 09/10: FOCO v2 e confronto com o checkpoint

**Autor:** Claude · **Revisor e integrador:** Codex (DEC-0910-02) · **Data:** 10/10/2026 · **Pedido:** recibo do Codex 6091443216, item 5

Apoio à DEC-0910-04 e à DEC-0910-05 de [`docs/DECISIONS.md`](../DECISIONS.md). Este arquivo só transcreve referências: não cria regra nem fila. A regra está no FOCO-APLICACAO-REAL v2, e o estado de cada ID é o do checkpoint vigente da issue #1 (comentário 5858061746, editado só pelo Codex).

## FOCO-APLICACAO-REAL v2

Fonte canônica: https://github.com/adrptu/Safrion-Software-/issues/1#issuecomment-5974888468 (04/10/2026, 00:12 UTC). A v2 substitui a v1. Trechos literais:

> 1. Claude conclui TODO o conjunto de melhorias já solicitado/em andamento no protótipo, conferindo IDs/estados no checkpoint existente. Não interromper a autoria, não trocar agora para C2 e não congelar os pedidos REND/AÇÃO/PCP/CAT/MAPA/SUP/ORC/SOLO/VEN e demais contratos vigentes. Preservar a ordem por dependências já coordenada.
>
> 2. Manter o artefato protótipo disponível e publicar incrementos operáveis/revisados quando aptos, com versão e limites, para Adrianus experimentar. Publicação parcial não é conclusão do conjunto, nem HML. Não repassar dados reais para a nuvem; preservar o demonstrador sintético e regras de publicação já autorizadas.
>
> 3. Ao concluir o conjunto, transferir para a aplicação real existente TUDO o que tiver sido validado e melhorado: design, navegação, formulários/estados, regras e cálculos, fluxos integrados e casos de teste. Reaproveitar fontes/componentes/lógica quando tecnicamente adequado; adaptar à arquitetura Next.js/React/TypeScript/PostgreSQL existente, sem importar armazenamento simulado como banco ou duplicar regras de domínio.
>
> 4. Requisitos ainda não validados ou com falha seguem explícitos como pendentes, não somem nem viram aprovados na migração. Protótipo permanece acessível como referência de comparação; não descartá-lo ao iniciar a aplicação real.

Da seção "Qualidade e transferência sem perda" do mesmo comentário:

> (…) só depois de TODAS as melhorias do conjunto concluídas, as três IAs reais fazem a jornada completa no mesmo protótipo identificado, dados/perfis isolados, cobertura e brutos próprios.
>
> Na aplicação real, transferir por fatias verificáveis tela→domínio→banco, vinculando os mesmos IDs/aceites e comparando com o comportamento validado do protótipo. Registrar na mesma tarefa, sem outra fila: referência do protótipo→implementado no real→testado→verificado em HML.

Leitura do Codex (6091443216, item 5): os passos 1 a 3 das decisões delegadas são organização proposta, não definição exaustiva que possa excluir IDs existentes; os pedidos posteriores de NAV, DS, cadastros e hiperclareza continuam.

## Confronto: conjunto vigente × passos 1 a 3

Passos 1 a 3: seção 5 do [texto ao proprietário em `58fb55b`](https://github.com/adrptu/Safrion-Software-/blob/58fb55bdd3d758d20b26f2dad84b371b626344d3/docs/decisoes-delegadas/DECISOES-DELEGADAS.md). Estado: checkpoint lido em 10/10/2026 (cabeçalho das 00:00 UTC, conferido de novo na versão das 00:29 UTC). O checkpoint muda; vale sempre o vigente.

| ID | No checkpoint | Nos passos 1 a 3 |
|---|---|---|
| BEN: S2 de origem por lote (6090699184) | Corrigido (`1440889`); parecer focal favorável 6091321884, sem aceite global | Passo 1, item 0 |
| BEN-1, restante da frente | Preservado no conjunto | **Fora dos passos** |
| DOM: B-R8 e COLH-C01 | S3 resolvido em `c764de9` (6091432263), sem aceite global | Passo 1, itens 0 e 3; passo 2 (OPE-09) |
| COM: Comercial e logística | Preservado no conjunto | Passo 1, item 7; passo 2 |
| PCM: `ba03515`, 1a a 1c e simplificação | Revisão da frente e composição pendentes; 1b e 1c dependem do SUP-2a | Passo 1, item 5; 1b no passo 2. **PCM-1c fora dos passos** |
| SAF-C01b e SAF-C02 | Pareceres focais favoráveis; pacote `7d38e5d` | Passo 1, item 1; passo 2 |
| NAV-1 (`a7023ca`) | Parecer focal favorável; entra depois da composição | Passo 1, item 8; passo 2 |
| NAV-2 | Preservado no conjunto | **Fora dos passos** |
| TABELAS-FOCO: Cadastros e Irrigação | Preservado | Passo 1, item 8 |
| CTL-4 e CTL-5 | Preservados | Passo 1, itens 2 e 7; passo 2 |
| SUP-1, 2a, 2b e SUP-3 | Preservado | Passo 1, item 4; passo 2 |
| SOLO | Preservado | Passo 1, item 7; passo 2 |
| Configurações | Preservado | Passo 1, item 6; passo 2 |
| CONTROLE-02 e RN-031 | Preservados | Passo 3.2 (RN-031 pelo ID, não nomeada) |
| PCP-ALOC (5973928269) | Preservado (PCP) | **Fora dos passos** |
| D7: nove contratos de 03/10 | Preservados; composição não relida | Desdobrados nas linhas abaixo |
| CAT-ATV `e47021d5` | Preservado | **Fora dos passos** (a 3.4 cobre só três ligações) |
| REND-config com D4 e ALOC `058eb147` | Preservado | **Fora dos passos** |
| MAPA: monitoramento, visões `f46b2e19` e ícones `abc41b07` | Preservado | **Fora dos passos** (o passo 2 traz só a barra do Mapa) |
| ORC-CUSTOS `7915f874` | Preservado | **Fora dos passos** |
| SUP v2 `e643eec7` | Preservado | Passo 1, item 4. **Aderência a conferir** |
| SOLO-MAPA-TV `0b10392f`/`8c83b04e` | Preservado | Passo 1, item 7. **Aderência a conferir** |
| VEN v2 `25d0882a`/`df64ef85` | Preservado | Passo 1, item 7. **Aderência a conferir** |
| REND (V44-REND) e AÇÃO (UX-ACAO-UNICA v2) | Histórico nos cabeçalhos arquivados, não lidos; merges na branch única | Fora dos passos, como frentes integradas. **Estado de aceite a conferir** |
| Design system: aplicação de SEL-02, BOT-03 e BOT-07 (PR #50) em todas as telas | Norma, com aplicação aberta | Passo 1, item 8 (sp-ds), sem passo para todas as telas: **fora dos passos** |
| CADUX | Preservado | Passo 1, item 8, por último |
| Ficha do pivô e capacidade | Preservado | Parcial no passo 2 (IRR-03, IRR-04); ficha no detalhe do equipamento **fora dos passos** |
| Agrofit: praga-alvo | Preservado | Parcial no passo 2 (AGR-07); colunas de praga-alvo **fora dos passos** |
| Hiperclareza | Não aparece no checkpoint nem no repositório | **Fora dos passos**; o Codex indica a origem |
| Software real: C2 e PRs #32 a #35 | Preservados para a transição | Fora dos passos por definição (DEC-0910-05) |

**Divergência de ordem.** O cabeçalho das 00:00 UTC coordenava BEN → DOM → COM → PCM; o das 00:29 UTC compõe SAF → DOM → PCM sobre o BEN corrigido. O passo 1 põe CTL-4 e SUP entre essas frentes e a COM depois da PCM. Vale o checkpoint.

**Resultado.** Nenhum ID sai do conjunto vigente: todos continuam como requisito, com o estado do checkpoint, até a conclusão e a auditoria do conjunto (DEC-0910-05).

**Não lido:** os cabeçalhos arquivados do checkpoint (pasta local do Codex) e os textos dos nove contratos de 03/10.
