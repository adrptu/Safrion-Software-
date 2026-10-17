PROJETO: Safrion (Do Talhão à O.S.)
PEDIDO: Telas, menus e funções ocultos — levar para o visível o que tem valor e uso real, excluir o resto

CONTEXTO
- Pedido do proprietário: verificar todos os menus, telas e funcionalidades ocultos; dizer o que vale aproveitar no protótipo visível; pedir para excluir o restante; manter só o que agrega valor e tem uso real.
- Versão analisada: 1792184197-5a81 (https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm). Privado: o Claude lê com a ferramenta Artifact (action "read"); o Codex lê pela cópia do protocolo.
- O resultado completo, com evidência, links a trocar e a tabela de 123 itens, está no anexo-telas-ocultas.md, que o proprietário anexa.

O QUE A ANÁLISE ACHOU
- A barra principal tem 9 itens (Mapa, Cadastros, Agrícola, Manutenção, Suprimentos, Comercial, Crédito, Configurações, Outros acessos). Os hubs mostram 38 telas.
- Das 148 telas, 110 estão fora do menu:
  - 83 só se alcançam por link dentro de outra tela;
  - 4 só por "Outros acessos";
  - 7 por "Outros acessos" e links;
  - 7 órfãs: nenhum link leva até elas (GE-01 Visão gerencial, IN-03 Agenda, PL-03 Capacidade, PT-06, MB-05det, MB-08 e MB-08x);
  - 8 só redirecionam (MA-01 a MA-05, MA-04det, PM, Main).
- Decisão proposta para as 110 telas fora do menu, mais 11 funções ocultas dentro de telas visíveis e 2 itens de navegação:
  - Levar para o visível: 26 itens (20 telas). 16 dessas telas levam a função e depois saem; IN-01 Meu dia, IN-02 Aprovações, MB-05det e MB-08 ficam e ganham entrada.
  - Manter como detalhe: 24 itens (22 telas).
  - Excluir: 58 itens (54 telas, mais 4 funções).
  - Decidir com o proprietário: 15 itens (14 telas, mais Outros acessos).
  - Se tudo for aceito, saem 70 telas.
- Funções que só existem em telas ocultas e não podem se perder: recolhimento de lote (CO-06), NF-e e lacre na saída (LO-02det), transferir, perda e estorno (SU-08), ler NF-e no recebimento (SU-06), trava de registro no receituário (AG-04det), emitir O.S. do período (PL-04), trocar recurso em execução (PL-05det), resultado por cultura (GE-01), MTBF e MTTR (GE-06), "pedir até" (SU-01), contrato com cargas (SU-05), ponto de pedido editável (SU-02).
- Regras fixas violadas em telas ocultas, que não migram: PL-04 "Liberar prontas", CA-01 "Liberar selecionadas" e IN-02 "Aprovar selecionados" liberam ou aprovam em lote.
- Números que não batem e somem com o legado: VE-04 mostra R$ 244 mil a receber e o PCOM R$ 91.470; o lote F26-02 diverge entre SU-03 e SU-03det; a família CO usa base antiga (OC-0510 no T7 × OS-0510 no Pivô 6).
- Isolamento: o BO-02 mostra a cobrança de outras organizações dentro de "Outros acessos".
- "Pagar fatura ›" fica no cabeçalho de todas as telas e não confere papel; só o gestor paga. Proposta: só no Mapa e na Assinatura, e só para quem paga.

LEVAR PARA O VISÍVEL (sem 10º item na barra; usar hubs, abas, visões e seções que já existem)
- Mapa: atalhos "Meu dia · N" e "Aprovações · N" no cabeçalho e página inicial por perfil (UX-05). Meu dia absorve a Agenda (IN-03) como visão Calendário e as Ocorrências (CA-03) como visão. Aprovações lista cada O.S. com produto, uma por vez, "aprovou, abre a próxima", sem "Aprovar selecionados".
- Agrícola › Ordens de serviço: filtro "A conferir" com conferência por exceção (CA-02); "Emitir O.S. do período" (PL-04, sem "Liberar prontas"); substituto lado a lado também em execução (PL-05det); seção "Receituário e versões" com a trava de registro Agrofit (AG-04det); filtro "Receituários" para o RT (AG-04); coluna "Situação · próximo passo" por padrão.
- Agrícola › Planos agronômicos: fonte, validade e aprovador RT por versão (AG-05).
- Agrícola › Estoque de produto: rastreabilidade do lote e "Simular recolhimento" (CO-06).
- Agrícola › Custos e fechamento: visão "Resultado da safra" com receita, margem e ROIC por cultura (GE-01).
- Agrícola › Painel: custo de pulverização por ha e aderência ao dia previsto (GE-06).
- Agrícola › Irrigação: etapas como abas visíveis; "Programar irrigação" em lote (IR-02).
- Manutenção › Painel: disponibilidade, MTBF, MTTR e custo por hora por ativo (GE-06).
- Suprimentos › Compras: coluna "Pedir até", itens atrasados e "Comprar urgente" (SU-01); contratos com cargas sob demanda (SU-05).
- Suprimentos › Estoque: ler NF-e ou QR no recebimento (SU-06, UX-09); transferir, registrar perda e estornar com vínculo (SU-08).
- Suprimentos › Painel: "Faltas atrasadas" (SU-01).
- Comercial › Expedição: checklist da saída com NF-e, lacre com foto, conferência do lote e balança (LO-02det).
- Cadastros › Produtos e locais: seção "Reposição" do item, com mínimo, ponto de pedido e máximo (SU-02).
- Outros acessos › App de campo: entrada para MB-08 Irrigação de hoje e MB-05det Receber devolução; fila "A separar" na aba Almoxarife.

EXCLUIR (depois de migrar o que a tabela do anexo indica e trocar os links)
- Início: IN-03 (vira visão do Meu dia).
- Agronomia: AG-03, AG-03det, AG-06.
- Campo: CA-01, CA-01det, CA-01x-os0420, CA-04, OS-0424-ficha (a versão impressa entra na ficha do app).
- Planejamento: PL-01, PL-02, PL-02det, PL-03, PL-05, PL-06 (conferir antes se a SAF já cobre autorizar execução, pendência vencida e ajuste local).
- Irrigação: IR-02.
- Colheita (base antiga): CO-01, CO-02, CO-02det, CO-03, CO-04, CO-05, CO-05det, CO-06det, CO-07.
- Logística: LO-01 a LO-04 (e a aba Motorista do MB-10).
- Gestão: GE-06det, GE-07.
- Suprimentos: SU-03, SU-03det, SU-04, SU-05det, SU-07, SU-07det, SU-09.
- Comercial: VE-01 a VE-06 e VE-04det.
- Portal: PT-06 (órfã).
- Redirecionamentos: MA-01 a MA-05, MA-04det, PM e Main (conferir antes se a publicação usa o Main como página inicial).
- Funções: os recortes #vis= da GE-08, "Abrir ordem completa ›" de 2 O.S., as cópias de "Restaurar demonstração" (fica uma no menu do avatar).
- Links que apontam para telas que saem, a trocar antes (o destino de cada um está no anexo): GE-03, GE-08, IN-04, OS, PAGR, AG-01, AG-02, AG-07, PROD, IN-01 e IN-02.

DECISÕES DO PROPRIETÁRIO (não implantar sem aceite registrado)
1. Financeiro (GE-04 Contas a pagar, GE-05 Contas a receber): no Safrion ou no ERP? Recomendação da análise: ERP; no Safrion fica o estado do título e a aprovação na caixa de Aprovações.
2. Portal do parceiro (PT-01 a PT-05det, PT-07): fornecedor, comprador e banco entram no Safrion? Se sim, o mínimo é responder cotação por convite (PT-02det) e enviar o XML da NF-e (PT-05det), com login próprio e fora do menu da fazenda.
3. Onboarding (ON-01): trial próprio ou implantação assistida? Em qualquer caso, sai do menu, abre sozinho na primeira entrada e mostra "passo N de 6" no Mapa.
4. Backoffice (BO-01, BO-02): ferramenta de administração separada, fora do menu da fazenda (hoje expõe outras organizações).
5. Outros acessos: fica com App de campo e, se o portal ficar, Portal do parceiro.

ORDEM DE TRABALHO: PRIMEIRO MELHORAR, DEPOIS IMPLANTAR
1. Claude e Codex, cada um sozinho, conferem a tabela do anexo no código vigente: Confirmado (com arquivo e trecho), Refutado ou Já resolvido. Para cada tela a excluir, confirmam que nada de valor se perde e que todos os links foram listados; para cada função a levar, confirmam o destino.
2. Divergência se resolve por fonte ou reprodução. O Gemini real entra só se a decisão mudar escopo ou fluxo de forma material. Pacote mínimo, sem dados reais.
3. O Codex registra a lista final, as decisões do proprietário pendentes e as fatias no checkpoint (só ele edita o checkpoint).
4. Implantação na fase registrada no STATUS, por fatias, nesta ordem: (a) levar as funções para o visível e trocar os links; (b) só então excluir as telas, com o aceite do proprietário registrado; (c) publicar e repetir o grafo de navegação. Revisão cruzada: quem revisa integra o PR do outro. A exclusão é reversível pelo histórico do repositório; nada se apaga fora dele.
Não simule o Codex nem o Gemini.

ACEITE OBSERVÁVEL
- Nenhuma tela órfã e nenhum redirecionamento sem uso.
- Toda tela que fica é alcançada pela barra, por um hub, por um atalho do Mapa ou como detalhe de um registro visível.
- As 12 funções listadas acima existem nas telas visíveis antes da exclusão das telas antigas.
- Nenhum link quebrado (verificação automática de todos os .dc.html e rotas).
- Nenhum número divergente entre telas para o mesmo título, pedido ou lote.
- Nenhum lote de aprovação ou liberação de O.S. com produto (decisão fixa).
- Meu dia e Aprovações alcançáveis em 1 clique a partir do Mapa, para os perfis certos (UX-05).

NÃO FAZER
- Criar um 10º item na barra principal.
- Excluir tela antes de levar a função de valor e trocar os links.
- Levar para o visível os botões de lote que violam a aprovação individual.
- Decidir pelo proprietário os itens de escopo comercial.

ENTREGA (no canal registrado)
- Tabela final por tela e função: decisão Claude · decisão Codex · decisão final · destino · links trocados · aceite do proprietário quando couber.
- Grafo de navegação antes e depois (telas no menu, por link, órfãs).
- Três listas curtas, com motivo: aplicado, deixado de fora, cortado.
- Suposições e pendências, cada uma com o gatilho de retomada.
