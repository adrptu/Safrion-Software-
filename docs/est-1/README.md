# EST-1 — lote vencido (rascunho, incompleto)

Codex autor, Claude revisor/integrador. Base PR59/952817e sobre5ec321d. Areas/processo_estoque.py liberado em6153002100. Delimitação de cenario.js/cenario.py solicitada em6153139300; não editar compartilhados antes do retorno. Claude mantém CF04/composição/LEI-AGRO.

Contraprova atual: cenDisp soma90disponíveis em lotevencido; cenLote escolhe vencido100antesdeválido5; cenLiberar reserva vencido; cenEntregar entrega reserva que venceu. Base2/6(exit1). O núcleo não foi alterado neste rascunho.

Implementado só na área Estoque: eitem bloqueia linha/detalhe com motivo de validade e recuperação; estEntregar0 recusa antes de chamar motor. Reutiliza evenc e dataoperacionalE2.hoje. Físico, pendência e reserva existentes conservados. Testes atuais4/8(exit1): os quatro defeitos centrais permanecem, os dois novos casos de tela/comando passam. Não aprovar/integrar/publicar este rascunho como correção completaEST-1.

Navegador10/10 em1440/390: linhaBloqueada, recuperação no detalhe, consulta semcampoeditável, estadointacto, semoverflow/erroJS. Regressões est_a4_test.py53/53 e EST-2 6/6; build/renderexit0. Brutos neste diretório. Dados sintéticos, sem produção/HML.

Próximo: definir autoria cenLote/cenDisp/cenEntregar0 + regra única de validade/dataoperacionalemcenario.py; aplicar bloqueio central e reutilizar na UI; testes8/8 mais limite fimdomês e nova reserva com loteválido alternativo. Inspecionar efeito em outros consumidores antes de declararEST-1completo; FEFO/fazenda/OS-1seguemIDs próprios. Proposta nãoexecutada não vale como teste. Reproduzir degen37 com Node noPATH: python3 est_validade_test.py; browserapósbuild/render: python3 est_validade_nav.py.


## Incremento: entradas e devoluções vencidas (13/10)

Autor Codex, somente `areas/processo_estoque.py` já liberado por Claude6153002100; base0449f46. O comando de recebimento recusa parte apta vencida antes de movimentar (inclusive recebimento misto e lote existente vencido com data futura informada). A devolução recusa condição apta em lote vencido, preservando custódia; formulário orienta receber em quarentena e mantém rascunho. Uma mensagem compartilhada no arquivo atende comando e formulário. Validade mensal segue a data operacional já existente E2.hoje/D2.HOJE.

Teste focal `est_validade_entrada_test.py`: 4/11 antes (exit1), 11/11 depois (exit0); limites dezembro/janeiro e fevereiro bissexto. Prévia inicial do teste comparava toda a revisão no replay; corrigida para saldo e movimentos, pois revisão pode mudar sem entrada duplicada. Bruto antes publicado é da versão corrigida do teste. Navegador `est_validade_entrada_nav.py`: 12/12, 1440×1000 e390×844; erro, rascunho, estado intacto, recuperação em quarentena, custódia baixada uma vez, sem overflow/erroJS. Primeiro lançamento bloqueado pelo sandbox antes de abrir porta; execução autorizada com localhost/Chrome isolado concluída exit0. Build da tela/render exit0, dados sintéticos5/5. Regressões A453/53 e EST-2 6/6. As quatro falhas centrais anteriores permanecem: est_validade_test.py4/8exit1.

Aplicado: guarda antes da movimentação, erro junto da condição e recuperação no mesmo detalhe. Fora: motorcentral, FEFO/fazenda, validade diária, mudança de regras de cadastro, produção/HML. Cortado: duplicação da mensagem de recebimento vencido; nenhuma etapa/controle removido. Suposição preservada: vencimento por mês/ano vale até o último dia do mês. Não é conclusãoEST-1 nem autorização de integração/publicação. Ganchos centrais dependem do contrato6153139300, reiterado6154205708.
