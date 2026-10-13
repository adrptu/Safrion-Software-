# EST-1 — lote vencido (rascunho, incompleto)

Codex autor, Claude revisor/integrador. Base PR59/952817e sobre5ec321d. Areas/processo_estoque.py liberado em6153002100. Delimitação de cenario.js/cenario.py solicitada em6153139300; não editar compartilhados antes do retorno. Claude mantém CF04/composição/LEI-AGRO.

Contraprova atual: cenDisp soma90disponíveis em lotevencido; cenLote escolhe vencido100antesdeválido5; cenLiberar reserva vencido; cenEntregar entrega reserva que venceu. Base2/6(exit1). O núcleo não foi alterado neste rascunho.

Implementado só na área Estoque: eitem bloqueia linha/detalhe com motivo de validade e recuperação; estEntregar0 recusa antes de chamar motor. Reutiliza evenc e dataoperacionalE2.hoje. Físico, pendência e reserva existentes conservados. Testes atuais4/8(exit1): os quatro defeitos centrais permanecem, os dois novos casos de tela/comando passam. Não aprovar/integrar/publicar este rascunho como correção completaEST-1.

Navegador10/10 em1440/390: linhaBloqueada, recuperação no detalhe, consulta semcampoeditável, estadointacto, semoverflow/erroJS. Regressões est_a4_test.py53/53 e EST-2 6/6; build/renderexit0. Brutos neste diretório. Dados sintéticos, sem produção/HML.

Próximo: definir autoria cenLote/cenDisp/cenEntregar0 + regra única de validade/dataoperacionalemcenario.py; aplicar bloqueio central e reutilizar na UI; testes8/8 mais limite fimdomês e nova reserva com loteválido alternativo. Inspecionar efeito em outros consumidores antes de declararEST-1completo; FEFO/fazenda/OS-1seguemIDs próprios. Proposta nãoexecutada não vale como teste. Reproduzir degen37 com Node noPATH: python3 est_validade_test.py; browserapósbuild/render: python3 est_validade_nav.py.
