# OS-LOTE · Agrupar operações e reprogramar O.S. futuras

R3 documental · 16/10/2026 · Codex, revisão/integração Claude pendente. Substitui o rascunho da base 052b9bf, preservado no Git. Não implementa produto nem comprova navegador, banco ou HML.

Pedido do proprietário de 16/10: agrupar a mesma atividade, insumos e doses de vários talhões; reprogramar rapidamente datas, produtos e cancelamentos das ordens futuras ainda não aprovadas, preservando o que já foi aprovado ou executado. A operação consolidada deve parecer uma tarefa única, sem apagar sua origem.

## Acordo curto — AGENTS §3.4

| Campo | Contrato |
|---|---|
| ID / resultado / persona | OS-LOTE. PCP reúne trabalho compatível e reprograma futuras; agrônomo decide a versão técnica; operador executa destinos autorizados. |
| Requisitos / fora | PRD 24, 41.1–3, 41.10–11 (GRUPO-01..10), 73.3, 73.9; DEC-1610-03, CMD-06/42/46/47 e ENG-021/022. Fora: mudar plano padrão, SAF-MAPA, PA-OPER F1, irrigação/manutenção/beneficiamento, código de produto, aprovação automática e evolução do PRD canônico. |
| Autor / revisor / integrador | Codex / Claude real / Claude. Contrato 6220764750, ACK 6220878307; conciliação solicitada em 6220907841. |
| Base / arquivos | Leitura: protótipo 052b9bfe7a3a46e8bff04e7e7afb9b632d83586e; normas main c827408673580d18195dcf247388dac036d26bc1, PRD blob f50555e0994acd6c47dce318eeb05f58b901aa04. Base de commit acordada: 62f2c35a9752fa6a0c18cdc77707d312bfd9a3bd, OS-LOTE.md idêntico ao rascunho inicial (conferência literal). Somente este arquivo e os-lote/. |
| Aceite / comando | Conciliação sem alterar PRD, cinco referências reutilizadas, estados/permissões, exemplos e negativas abaixo; `python3 -I docs/integracao/V71/os-lote/oraculo.py`. Saída versionada. Implementação e testes de produto ficam pendentes. |
| Estado / próximo passo | Especificação em revisão; Claude revisa as diferenças materiais. Gemini critica equivalência, seleção e recuperação em pacote sintético delimitado. |

## 1. Reconciliação com o contrato vigente

O PRD é a fonte da regra, não o comportamento incompleto do protótipo. §41.10 já distingue **uma O.S. multilinha para rascunhos não emitidos** de **agrupador de execução para O.S. emitidas**. Emitidas conservam ID, versão, demanda, histórico e vínculo ao plano; o agrupador apenas coordena as linhas. Não cancelar origens para simular consolidação. O grupo não tem estoque nem custo próprios a somar às ordens.

Preservar as cinco fases do Kanban: A liberar, Liberadas, Em execução, Em conferência, Encerradas; Canceladas continua no histórico. “Aguardando agrônomo” é selo/pendência dentro de A liberar, nunca sexta coluna “A aprovar”. A aprovação é por O.S./versão (inclusive cada O.S. num agrupador); CMD-42 e CMD-06 têm ações e recibos separados, mesmo com as duas alçadas na mesma pessoa. DEC-1610-03 mantém essa exigência.

§73.3 IDEM-10 governa reprogramação em lote: chave e recibo por O.S. independente, com resultado parcial explícito. O ID da submissão só correlaciona itens. A criação/alteração de um agrupador com linhas interdependentes é um único efeito atômico: ou associa todas as linhas confirmadas ou nenhuma. Não distribuir uma mesma ocorrência entre dois grupos ativos por concorrência.

Desfazer/separar nunca apaga versões, recibos ou fatos confirmados (ENG-026). É correção vinculada, com versão esperada e nova intenção; não restaura aprovação antiga por copiar valores.

Regras normativas são as referências da seção 1. Organização do painel, rótulos e seleção explícita abaixo são escolhas de UX da R3, propostas para revisão; não constituem nova regra do PRD.

## 2. Entidades, contexto e próxima ação

| Entidade / nível | Estado visível | Primária / destino | Seções do detalhe |
|---|---|---|---|
| O.S. / lista e detalhe existentes | A liberar + Aguardando agrônomo | Revisar versão (agrônomo); PCP pode propor reprogramação | Situação e origem, atividade/talhões, insumos, recursos, histórico |
| O.S. / detalhe | A liberar + Aprovada vN | Liberar para execução, só com alçada e prontidão | Aprovação e prontidão separadas |
| Agrupador / agrupamento da lista O.S. e detalhe | Composição proposta; pendências por linha | Confirmar agrupamento; depois Liberar selecionadas (aprovadas e prontas) ou Revisar versões pendentes | Receita comum, destinos, janela/recursos, origens |
| Linha/talhão / subdetalhe | Não iniciado, parcial ou concluído, com saldo | Abrir O.S. de origem / Registrar avanço autorizado | Área, dose/unidade, carga, realizado, saldo e restrições |
| Reprogramação / painel contextual da lista | Rascunho; conferindo; enviando; resultado por O.S. | Aplicar em N O.S.; após retorno Resolver pendentes | Seleção, mudanças, prévia antes→depois, recibos |

Agrupador e reprogramação usam a listagem e o detalhe de O.S.; não criam menu ou fila autônoma. Na seleção preservam fazenda, safra, filtros, busca e posição; título mostra origem (“O.S. futuras · Fazenda demonstração · Safra demonstração”). Links ao talhão retornam ao mesmo rascunho e foco. No mapa/Planejar safra, apenas atalho contextual para essa função, sem editar aquelas frentes neste contrato.

## 3. A — Agrupar operações compatíveis

### Elegibilidade e significado de “igual”

Nesta primeira implementação, selecionar ordens **A liberar**, inclusive **A liberar + Aprovada vN**, sem início/realizado, preparo, entrega, custódia, reserva ou vínculo ativo a outro grupo. Para as aprovadas, comparar a compatibilidade sobre suas versões técnicas aprovadas exatas; o agrupador altera somente a coordenação operacional, preservando ID, versão técnica, escopo e aprovação de cada origem. Pendência de aprovação permanece visível por linha e não recebe a aprovação de outra. **Liberadas**, ordens parciais ou com compromisso incompatível ficam excluídas com motivo e acesso ao fluxo existente de saldo; não reabrir nem cancelar implicitamente. As possibilidades mais amplas do PRD 41.10/GRUPO-06..08 permanecem pendentes na mesma tarefa.

Comparação por identificadores estáveis, valores exatos e versão, nunca pelo rótulo da tabela:

- Mesma organização e fazenda, safra/ciclo compatível e frente operacional. Nesta fatia, culturas distintas ficam separadas até comprovação explícita da compatibilidade técnica/documental por linha (§41.10). Operação e método iguais, incluindo parâmetros técnicos pertinentes (profundidade/regulagem etc.).
- Mesmo conjunto de produtos, formulação e concentração; mesma dose canônica e **base de aplicação**. A ordem visual dos produtos não importa. 1 L/ha = 1.000 mL/ha por fator exato conhecido; 1 L/ha ≠ 1 L/100 L e kg ≠ L sem conversão específica válida. Doses não viram médias. Ausência, dose zero não justificada ou conversão desconhecida exigem correção, não inferência.
- Mesma receita de preparo identificada e versão vigente, com instruções e escopo cobrindo todos os destinos. “Receita de preparo” não se confunde com receituário legal: cada talhão/O.S. mantém seus documentos exigidos, validade e vínculo. Nome/ingrediente ativo igual não substitui essas verificações.
- Para tanque comum: volume de aplicação, concentração de calda, perfil de aplicação e capacidade útil compatíveis; mesmas doses com 100 e 150 L/ha não são iguais. Para sólido, perfil/regulagem e base correspondentes; não impor água/tanque. Taxa variável e dose por semente ficam fora desta primeira fatia, sem apagar requisitos do PRD.
- Interseção **global** de janelas técnicas e validades (máximo dos inícios, mínimo dos fins), restrições por alvo/estádio/cultura, reentrada/exclusões e equipamento. Não basta que A cruze B e B cruze C. Horários/fusos e intervalo final explicitados; duração positiva deve caber, não apenas uma data de contato.
- Identidade da ocorrência + talhão/parcela/versão impede seleção repetida. Área autorizada e geometria não se sobrepõem para o mesmo serviço. Somar área de operações não equivale a medir área física única da fazenda.

### Fluxo e efeito

Na lista, “Agrupar operações compatíveis” abre candidatos no contexto atual; no detalhe, “Adicionar talhões compatíveis”. Reutilizar nomes PRD, sem duplicar botões equivalentes. Sugestão não seleciona automaticamente. Checkbox com nome da O.S./talhão; “Selecionar compatíveis deste recorte (N)” é ação explícita e mostra quais IDs entram, inclusive quando paginados. Mudança de filtro não amplia seleção silenciosamente. Compatibilidade exige todos os parâmetros pertinentes definidos, não apenas igualdade com a ordem âncora: perfil/restrição ausente aparece em Excluídas · Definir parâmetro, nunca herda o valor da âncora. Incompatíveis têm motivo, não só cor; nenhum item fora da permissão aparece.

Prévia na mesma superfície: destinos/áreas, receita/versão, quantidade por produto/unidade, cargas, janela comum e programação de pessoas/máquinas. Uma primária: **Confirmar agrupamento**. Para rascunhos ainda não emitidos, texto **Emitir O.S. para N talhões** e consequência explícita. Criar não aprova, libera, prepara ou reserva. A confirmação leva versões esperadas de todas as origens e do grupo, não só um hash final. Conflito devolve IDs e diferenças, conserva a seleção e edição ainda válidas e marca a linha conflitante para conferência; retirar/substituir exige ação explícita e nova prévia, sem reenvio automático de subconjunto. Após o recibo, a próxima primária é **Liberar selecionadas** para linhas aprovadas e prontas, ou **Revisar versões pendentes** conforme o contexto ativo. Liberar selecionadas executa CMD-06 linha a linha, com alçada, prontidão, versão esperada e recibo por origem; não libera automaticamente ao agrupar nem mistura CMD-42 com CMD-06. O agrupador nunca herda ou produz aprovação técnica.

Ordens emitidas mantêm seus IDs; agrupador tem ID/versão e vínculo às ocorrências. Prévia consolidada não soma novamente demanda, requisições ou custo. Reserva de execução nasce em CMD-06 (RSV-03/APROV-09), portanto as ordens elegíveis normalmente têm **reserva zero**, não reservas a transferir. Estado legado com reserva, custódia, preparo ou vínculo incompatível é excluído e encaminhado para reconciliação; não “corrigir” apagando movimentos.

Não escolher recursos da ordem mais cedo automaticamente. Exibir recursos atuais, diferenças e proposta de sequência. Reutilizar critérios de `alChoques`, `alCandidatos`, `alBloqueado` e permissões de `alTrocar` (`alocacao.py`), avaliando o **estado final proposto**, sem contar os próprios blocos substituídos como conflito. Validar choques entre linhas do lote e com trabalho fora dele, manutenção, classe e habilitação. Ausência/conflito de máquina impede programação/liberação pertinente, não a decisão agronômica (§73.9.6). Permitir salvar composição sem prontidão com pendência nomeada; nunca mostrar horário como confirmado quando não cabe.

Horas: somar área/capacidade efetiva por linha/recurso e tempos de deslocamento/setup conhecidos. Capacidade ausente não vale zero; mostrar “Horas não calculadas · informar capacidade”. Não prometer economia de deslocamento ou limpeza; não eliminar limpeza exigida. Quantidade necessária não é arredondada para embalagem cheia. Insumos diferentes mantêm totais separados; custo real depende do consumo/custeio por origem, sem rateio cego de custo/ha.

“Separar este talhão” antes de liberação cria revisão da composição, retira só aquela linha, preserva origens e demanda. Se já houve aprovação técnica, revisão segue §41.3: separar somente a programação, mantendo o mesmo ID/versão técnica e seu escopo, preserva aprovação vinculada; mudança técnica exige revisão. Não copiar assinatura para nova entidade/versão. Data fora da janela aprovada ou equipamento que muda método/regulagem não é ajuste meramente operacional; fora da reprogramação em lote inicial de ordens não aprovadas (§4). Após preparo/execução, usar tratamento de saldo e custódia existente; não oferecer desfazer simples. Apontamento continua por talhão/linha: deslocamento não é área, 100% de área não encerra ordem, carência/reentrada partem do fato pertinente de cada destino. Calda remanescente nunca retorna como produto original (§41.10 e42).

## 4. B — Reprogramar futuras em lote

Uma ação secundária **Reprogramar O.S. futuras** abre painel único com seleção, mudança e prévia; sem wizard artificial. Herdar fazenda/safra/talhões visíveis. Data inicial hoje, no fuso da fazenda; não reaproveitar dose/quantidade anterior como escolha. Exibir elegíveis e excluídas com motivo e acesso à O.S. (por exemplo, “4 fora: 2 aprovadas, 1 em execução, 1 encerrada”). Seleção começa vazia; “Selecionar as N futuras deste recorte” exige ação explícita. O.S. multilinha que também cobre talhão não selecionado aparece como **escopo maior**, não entra silenciosamente: escolher explicitamente toda a O.S. ou separar pelo fluxo permitido e refazer a prévia.

Elegíveis: futuras na data informada, A liberar, não aprovadas e sem fato/compromisso incompatível descrito em A. Permissões são por ação: PCP pode propor datas/recursos no seu escopo; alterações técnicas (incluir/retirar/trocar produto, dose, método, área, janela técnica) exigem competência/alçada vigente do agrônomo, como `osc_ajustar`/AL-02. Cancelar usa competência e motivo do CMD-46; operador não ganha poderes por ser lote. Revisão técnica posterior continua necessária para executar.

Escolher ações na mesma linha de trabalho: deslocar ±dias ou data explícita; incluir/retirar/substituir produto; alterar dose; cancelar com motivo. Datas respeitam calendário/fuso, não somam 24h cegamente. Troca de produto não copia dose por padrão; só equivalência autorizada e versão explícita do contrato de produto fixo/equivalente (§40.5). Busca limitada ao catálogo/escopo e erro junto do campo. Cancelamento e outras edições da mesma O.S. não combinam: pedir escolha para evitar efeitos descartados.

Prévia **por ID/versão exata**: antes→depois, talhões cobertos, doses/bases, data/janela, quantidade e demanda por produto, custo estimado e sua fonte ou “não calculado”. Mostrar denominador da variação em R$/ha; nunca somar custos/ha. Operação altera a O.S. e sua demanda única, não reescreve plano agronômico. Cortado o atalho ambíguo “Atualizar plano também?”; qualquer atualização do plano usa o fluxo PA existente e autorização própria.

Não submeter itens com bloqueio conhecido sem mostrar o motivo. Usuário corrige a seleção/rascunho ou retira explicitamente essas O.S. antes de confirmar **Aplicar em N O.S.**. Depois, concorrência ou falha pode produzir resultado parcial: “3 alteradas · 1 mudou de versão · 1 pendente de envio”, cada linha com ação pertinente, sem toast de sucesso global. Não repetir confirmadas. Rejeição de negócio/conflito termina a intenção; corrigir preserva rascunho e gera nova intenção por item. Falha transitória mantém chave e conteúdo. Timeout exige consultar recibo, não presumir cancelamento. Não aprovar offline nem gerar fichas/pacotes a partir da prévia.

Mudanças técnicas geram nova versão não aprovada e invalidam documentos futuros vinculados; operacionais dentro do envelope mantêm versão técnica/aprovação quando cabível (§41.3/APROV-11), mas neste lote inicial aprovada já está excluída. Não chamar `osc_ajustar` com liberação padrão `true`: o código atual é referência parcial, não implementação deste contrato. Cancelamento libera somente compromissos válidos associados; não baixa estoque ou devolve custódia sem fato.

Reprogramar linha de grupo só se a transação também atualizar/revalidar composição e versão esperada do agrupador. Se a nova receita ficar diferente, a prévia oferece **Separar esta O.S. do grupo e aplicar alteração**, sem tocar nas outras; a confirmação daquele item inclui ambos os efeitos indivisíveis. Grupo com preparo, execução ou versão concorrente exige fluxo de saldo, não alteração parcial escondida. Itens que dependem do mesmo agrupador não são tratados como independentes: resolver o escopo conjunto antes de submeter.

**Desfazer reprogramação**: nova prévia compensatória do conjunto efetivamente confirmado, por item, somente enquanto versões resultantes continuam vigentes e não há aprovação/liberação/execução/material comprometido posterior. Se alguém editou depois, mostrar conflito e encaminhar revisão; não sobrescrever. A compensação incrementa versões, reconcilia demanda e mantém toda a trilha. Link ao recibo persistente também oferece recuperação depois que o aviso temporário some. Ao abrir a recuperação, reler versões e dependências; se inviável, mostrar motivo persistente e acesso ao detalhe, sem depender de tooltip. O comando revalida no envio para cobrir corrida posterior; não adicionar polling/serviço novo por rotina.

## 5. Negativas, dano e recuperação

| Caso | Resposta e dano evitado |
|---|---|
| Outra fazenda/organização, escopo adulterado ou perfil sem competência | Recusar no comando, manter rascunho permitido; evita alteração de patrimônio/decisão sem autoridade. |
| Receita/versão/formulação/base/volume diferente | Separar candidatas; evita calda/dose errada. Nunca usar média ou nome aproximado. |
| Janela global vazia ou tempo total não cabe | Impedir programação inválida; conservar composição pendente ou separar programação explicitamente. Evita promessa de execução fora da janela. |
| Mudança da versão técnica aprovada ou de sua aprovação, início, parcial, entrega/preparo ou dupla vinculação após a prévia | Conflito sem efeito no agregado afetado; reler e mostrar diferenças, preservando seleção e rascunho. Uma origem Aprovada v3 que passa a v4 entre prévia e confirmação não entra por equivalência de valores: exige nova prévia da versão vigente, sem herdar aprovação v3. Aprovação já existente na prévia não é causa de exclusão. Evita invalidar execução/consumo ou duplicar serviço. |
| Produto/uso/receituário/credencial inválidos ou vencidos, dose fora do limite aplicável | Impedir a transição que exige validade; informar requisito e responsável, conservar proposta. Reutilizar RN-016, §41 e fontes versionadas; não presumir legalidade por catálogo ou consenso de IA. |
| Nova data conflita com carência/reentrada/colheita ou restrição técnica obrigatória | Sinalizar exatamente o destino e regra; não tratar toda janela como aviso dispensável. Dado ausente exige conferência, não zero dias. |
| Estoque insuficiente ou lote inapto | Mostrar falta e dono; aprovação técnica não depende de saldo. Liberação/reserva continua impedida; agrupar não fabrica estoque. |
| Máquina/pessoa ocupada, bloqueada ou sem habilitação | Revalidar programação no conjunto final; indicar conflito e ajuste. Preservar validade técnica quando só a prontidão mudou. |
| Reenvio, outra aba, queda depois do commit | Mesma intenção devolve o recibo; versão decide disputa de intenções diferentes. Evita duplicar ordem, demanda ou avanço de data. |
| Compensação sobre edição posterior | Recusar desfazer automático; preservar ambas as trilhas e abrir revisão. Evita perda do trabalho do colega. |

## 6. Oráculo e aceites rastreáveis

Exemplos exclusivamente aritméticos, sem recomendação de aplicação. `os-lote/oraculo.py` usa Decimal e datas sintéticas. É especificação executável independente; não exercita produto, transação real ou navegador.

- **A1 / GRUPO-01..03:** seleção explícita e equivalência exata, inclusive unidades e interseção global. Negativas N1..N8 do oráculo e tabela acima. Mesmo conjunto de produto em outra ordem é equivalente; volume/base/versão diferentes não.
- **A2 / produtividade:** agrupar três destinos e chegar ao recibo **sem abrir o detalhe de cada O.S.** e sem redigitar receita herdada. Medir a tarefa completa conforme §7, incluindo seleção e conferência; meta de aceite, ainda não executada.
- **A3 / GRUPO-04:** A 10 ha + B 15 ha, 2 L/ha, 100 L/ha, tanque 2000 L → 25 ha, 50 L de produto,2500 L de calda, cargas 2000/500 L, produto 40/10 L, destinos 10+10/5 ha. A 10/B 15/C 5 ha, capacidade 5 ha/h, deslocamento 0,5 h, setup 0,25 h → 30 ha, 60 L, 3000 L, 6,75 h. Capacidade desconhecida impede estimativa; não preenche zero.
- **A4 / GRUPO-05:** demanda das origens 50 L permanece 50 L após agrupamento, não 100 L. Reserva zero continua zero antes de CMD-06; nenhuma saída nova. Valores de custo originados permanecem rastreáveis sem novo custo no grupo.
- **A5 / GRUPO-06/08:** separar preserva IDs, histórico e demanda; compensação não restaura versão/recibo velho nem apaga material. Parte em execução permanece fora do atalho, com fluxo de saldo acessível.
- **A6 / GRUPO-07:** realização A 10 ha/B 5 ha → 15 ha aplicados, 30 L consumidos, 10 ha/20 L de saldo teórico; não afirmar que saldo teórico é produto físico disponível ou calda preparada. Carência por destino/fato; grupo não encerra sozinho.
- **A7:** incluir A liberar + Aprovada vN sem compromissos incompatíveis; agrupamento operacional preserva ID e aprovação individual da versão exata, sem CMD-06/fichas/reserva por efeito do agrupamento ou CMD-42. Executar a negativa de versão aprovada alterada entre prévia e confirmação (§5): conflito, seleção preservada e nenhuma aprovação herdada. Liberar selecionadas revalida e produz recibo CMD-06 por linha.
- **A8 / GRUPO-09:** retry e disputa não duplicam grupo/vínculo. Banco real e concorrência ficam como aceites de implementação, não resultado do oráculo.
- **B1:** cinco O.S., dois talhões, deslocamento de +7 dias e uma troca explícita de dose: interações em lote **≤ 50%** das interações da mesma tarefa feita O.S. a O.S. na base, do mesmo ponto inicial até todos os recibos. **Zero redigitação de receita ou dose herdada**; a dose deliberadamente alterada é entrada necessária e contada. Mesma persona, permissões, dados e dispositivo (§7). Meta de aceite, sem ganho medido nesta entrega.
- **B2/B4:** somente elegíveis, sem ampliar escopo de ordem multilinha; regras técnicas/documentais e servidor impedem mudanças inválidas. Fonte/validade da regra ficam identificadas.
- **B3:** 10+15+5 ha, produto X 2→1,5 L/ha → 60→45 L, delta −15 L; reprogramação não muda área única nem cria custo realizado. Preço sintético 20 R$/L: 1200→900 R$, delta −300 R$, R$/ha 40→30. Sem preço: parcial/não calculado.
- **B5:** cancelar a ordem de 5 ha com motivo remove sua demanda 10 L; as outras continuam 50 L. Não cria devolução de estoque quando nada foi entregue.
- **B6:** compensação 3→4 (não 3→2), condicionada à versão e ausência de fatos posteriores; histórico preservado.
- **B7:** chave/recibo por item; sucesso parcial e replay sem repetir avanço. Alteração de conteúdo com chave antiga é conflito.
- **B8:** histórico com autor, instante do servidor, versões antes/depois, ID da submissão e origens; sem aprovação inventada.

Implementação deve executar ainda contrato/domínio + navegador 1440/390 px + teclado, fluxo com erro e retomada, `os_recurso_test`, `os_aprov_lib`, `os_cenario`, `tabelas_os` e checks DS proporcionais. Rodar contraprovas afetadas na base com defeito; não repetir bateria geral por documento. HML futura exige banco real para atomicidade/idempotência/isolamento. GRUPO-10 com personas de campo permanece pendente; exemplo numérico não equivale à homologação agronômica.

## 7. UX, benchmark e medição honesta

Referências do módulo Estoque↔O.S.↔App reutilizadas da pesquisa de27/09/2026 (`outputs/diretriz-benchmark-e-produtividade.md` no canal da equipe); páginas públicas conferidas novamente em16/10/2026. Sem login, teste comparativo ou ranking. São inspirações, não prova de conformidade brasileira nem de desempenho.

| Fonte oficial | Prática / decisão nesta fatia / prova esperada |
|---|---|
| [John Deere Work Plans](https://developer.deere.com/industry/precision) | Contexto de trabalho por talhão enviado ao equipamento. Adaptar herança de contexto e destino; adiar integração com máquina. Provar nenhuma redigitação de fazenda/receita herdadas. Página dev-docs anterior sem corpo recuperável nesta leitura; usar fonte de indústria. |
| [Agworld Activity Management](https://www.agworld.com/products/activity-management/) | Planejado→atividade→histórico por campo. Adaptar uma origem rastreável e resultado por linha. Provar executar/editar sem duplicar demanda; não adotar alegação comercial de ganho como medição. |
| [Cropwise — Creating a Work Order](https://help.us.cropwise.com/hc/en-us/articles/49465730801043-Creating-a-Work-Order) | Seleção por fazenda/cultura/área e reaproveitamento de contexto. Adaptar seleção contextual e teclado; descartar herdar última dose e apagar ordem original após aplicação. Provar escopo explícito e histórico intacto. |
| [FieldView](https://climate.com/pt-br.html) | Contexto de talhão e acompanhamento de operações/mapas. Adaptar ponte ao detalhe; adiar novas camadas de mapa. Provar retorno conserva recorte/rascunho. |
| [Aegro — Estoque e patrimônio](https://treinamento.aegro.com.br/lp/estoque-insumos-patrimonio.html) | Atividade conecta consumo e custo da safra. Adaptar efeito único por origem. Provar agrupador sem segunda baixa/custo e mostrar inconsistências. |

**Antes:** código052b9bf tem O.S. individual e `osc_ajustar`; não há jornada OS-LOTE concluída a medir. Contagem comparável ainda não executada. **Depois proposto:** abrir contexto, selecionar conjunto explícito, editar uma vez, conferir prévia e confirmar; aprovação/liberação continuam etapas reais independentes. Dois cliques antigos não incluíam seleção e oito cliques/dois campos não cobrem escolha de produto/dose; deixam de ser aceite garantido. Metas de aceite antes do código: B1 exige ≤ 50% das interações da alternativa individual completa e zero redigitação de receita/dose herdada; A2 exige recibo dos três destinos sem abrir cada detalhe de O.S. Nenhuma dessas metas está medida ou garantida. Se a alternativa individual não concluir a mesma tarefa, a comparação fica bloqueada, sem substituir seu denominador por uma contagem inventada.

No E2E da implementação registrar do mesmo ponto inicial até todos os recibos: cliques/toques (incluindo seleção, autocomplete, confirmação, rolagem em registro separado), campos e caracteres digitados, tempo e erros, antes e depois, mesma persona/dados/dispositivo. Para função ausente na base, declarar “sem equivalente”, medir alternativa individual que realmente conclua a tarefa ou marcar comparação bloqueada; não inventar baseline zero. Ganho só após execução.

Conformidade proposta: lista→detalhe→linha; controles DS existentes; uma primária no painel ativo, fundo sem competição; campos relacionados juntos; filtros/ordem/grupos/posição/foco preservados; totais do recorte selecionado por unidade. A prévia permite abrir linha sem perder edição.390px: resumo legível, primária alcançável com teclado virtual sem cobrir campos, alvos DS44px. Teclado:Tab/Shift+Tab,Space seleciona,Enter abre,Esc volta preservando rascunho e foco; seleção tem nome e contagem acessíveis. Enviando/pendente/confirmado/erro por texto; foco no erro com recuperação. Vazio→ajustar filtros; falha de leitura→tentar novamente sem apagar proposta; alteração externa→comparar versões. Verificação de acessibilidade/UI está **especificada**, não executada nesta entrega documental.

**Aplicado:** fonte única PRD/DS, contexto herdado, seleção explícita, comparação exata, rastreabilidade, recibos e recuperação versionada. **Deixado de fora:** código, mapas novos, PA, operação parcialmente executada no atalho inicial e medições de UI; têm contrato próprio ou exigem implementação. **Cortado:** nova coluna A aprovar, cancelamento automático de origens, reserva no agrupamento, aprovação+liberação composta, pré-seleção implícita, wizard de três telas e promessa de cliques sem medição.

## 8. Histórico e limites de evidência

Rascunho Claude 93fe5f0, ainda igual em 62f2c35, preservado no Git. R2 Codex concilia §§41.10/73.3, corrige desfazer/reserva/estados e delimita aceites. Não altera PRD nem legitima discrepâncias do código atual. Oráculo executado: 25/25 casos aritméticos, resultado.json nesta pasta. Gemini real Pro/HIGH concluiu STOP (25 casos foram informados, não executados pelo modelo), pacote ce1b1251f4e42bfdf573d71042b01d9dbac57a368f82722ab7f6445baa8e2807. Tratamento de cinco sugestões em os-lote/revisao-gemini.md; retorno Claude R2 recebido em 6221130698; implementação permanece pendente até contrato específico. Protótipo→implementado no real→testado→HML continuam estados distintos.

R3 incorpora os dois ajustes obrigatórios da revisão Claude 6221130698: agrupamento operacional de A liberar + Aprovada vN e aceites numéricos A2/B1, sem ampliar a reprogramação técnica de aprovadas (§4). Acrescentada a negativa de concorrência da versão aprovada. Oráculo aritmético e seus 25 resultados permanecem inalterados; as novas negativas de comando e metas de UX exigem implementação e execução próprias. Não foram executadas como produto. R3 aguarda revisão/integração Claude.
