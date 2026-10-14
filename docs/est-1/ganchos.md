# EST-1 — consumidores de validade

Autor Codex; revisor/integrador Claude. Base 77b41339007bd05ae4a54c9f31812d74695963fc. Autoria liberada pelo Claude no recibo6157512088; ACK Codex6157582439. Dados sintéticos; protótipo, sem efeito em HML/produção.

## Mudança

Três guardas em cenario.js reutilizam cenLoteVencido:
- cenConcPrevia recusa retirada complementar vencida, incluindo reserva antiga. Preserva o aceite do consumo já coberto por custódia e a recusa do relato. cenConciliar permanece intacto e consome a prévia existente.
- cenEstDem exclui físico vencido da projeção de suprimento. Quantidade física, reservas, quarentena e rastreabilidade não são apagadas.
- cenOsSup exclui reserva vencida do suprimento efetivo da O.S. Contraprova exigida pela autorização reproduziu reserva vencida em outra fazenda reduzindo a demanda de10 para0. Reserva válida permanece abatendo10. Não altera fórmula de demanda nem cenOsDem.

## Evidência executada

Conciliação: 2/3 antes →3/3 depois. Antes: complemento2L consumia físico1199→1197; depois: erro na prévia e no comando, físico1199 preservado e conferência aberta. Custódia já entregue e recusa continuam passando.
Demanda: contraprova original físico100 vencido falhava. Após correções,4/4 passam, incluindo controle físico válido55/quarentena5, exclusão de outra fazenda e reservas válidas/vencidas entre fazendas. Contraprova específica cenOsSup:3/4 sem guarda→4/4 com guarda. A primeira extensão de fixture omitiu movimento de reserva e falhou também no controle válido; esse ensaio inválido não sustenta achado nem aceite. Brutos preservados. A fixture final usa movimento reserva real.
Regressões executadas: demanda única71/71, A453/53, validade11/11, entrada15/15.
Build focal Estoque e montagem do render: exit0; render29 páginas existentes, não build integral do conjunto.

Sem alteração de fonte do Claude fora do contrato; sem merge próprio. Revisão crítica e integração por Claude pendentes. Não equivale a conclusão integral EST-1/protótipo nem aciona auditoria global/PRD final.

Navegador focal: est_validade_conc_nav_test.py12/12,1440×900 e390×844, prévia com motivo/recuperação e sem Confirmar aceite, recusa por Enter, físico/reserva/custódia preservados, zero erro de execução. Ensaio inicial9/12 tentou link de seção oculto no menu móvel; diagnóstico confirmou isso e o teste final abre o controle móvel real antes da navegação. Brutos anteriores preservados, sem atribuir a falha do harness ao produto. A checagem py_compile tentou gravar cache fora do sandbox e foi recusada; compile() em memória e execução real do teste passaram.

Aplicado: mesma regra de vencimento nos três consumidores; estado e recuperação no contexto existente. Fora: fórmulas ENG011, cenConciliar, cenOsDem e telas sob autoria Claude. Cortado: possibilidade de confirmar uma retirada inválida; nenhuma etapa nova. Suposição: validade mensal/data operacional segue contrato existente, não relógio real.
