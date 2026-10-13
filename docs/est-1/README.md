# EST-1 — validade no motor e na tela; integração CTL4 pendente

Codex autor; Claude revisor/integrador. Base de reprodução `2cbef389e76f63f630fea05fffaa0ef258316d33` (`claude/v44-v59`). Autoria central liberada pelo Claude real no recibo6156041752: cenLote/cenDisp/cenEntregar0, helper e data operacional em cenario.py; Estoque já liberado em6153002100. ACK e fronteira CTL4 em6156123675. O histórico anterior está em historico-30ea08d.md e nos brutos preservados.

O motor exclui lote vencido da seleção/reserva, zera seu disponível sem apagar físico ou reservas e recusa entrega de reserva vencida antes da movimentação. A tela reutiliza a mesma regra mensal. Entrada/devolução apta vencida seguem bloqueadas; quarentena permite recuperação no mesmo contexto. Data operacional vem de dados_config.DIA_OP, preservando 26/09/2026 no cenário e no Estoque, sem relógio do navegador. Validade MM/AAAA inclusiva até o fim do mês; ausência/— mantém regra existente.

## Verificação executada nesta base

Todos os dados são sintéticos. Build focado Estoque/O.S./mobile/campo + montar_render: exit0, 29 páginas +20 arquivos, sintéticos5/5. Com Node no PATH, executar de tools/prototipo/v37/gen37:

| Comando python3 | Resultado |
|---|---|
| est_validade_test.py | 11/11, exit0; quatro falhas centrais corrigidas, mês/ano/bissexto, reserva e replay |
| est_validade_entrada_test.py | 11/11, exit0 |
| est_a4_test.py | 53/53, exit0 |
| est_item_divergente_test.py | 6/6, exit0 |
| est_validade_nav.py | 10/10, exit0, desktop1440 e celular390 |
| est_validade_entrada_nav.py | 12/12, exit0, desktop1440 e celular390 |
| app_cenario_test.py | 15/15, exit0 |
| os_cenario_test.py (original de Claude) | 21/22, exit1: primeira asserção ainda exige cenário v2; base já v7 |
| est_validade_os_esquema_probe.py | 1/1, exit0: mesmas condições do primeiro caso, expectativa v7; original intacto |
| est_validade_demanda_pendente.py | 0/1, exit1: pendência real abaixo |

Brutos `est1-final-*.txt`. Chrome isolado/localhost; teclado/recuperação/rascunho e ausência de overflow/erro JS nos casos focais. As primeiras execuções de OS/App sem seus HTML renderizados não eram prova do produto; arquivos gerados antes dos resultados acima.

## Dependência material aberta — EST-1 × CTL4

`cenEstDem` soma físico−quarentena diretamente. Contraprova mínima: um único lote sintético vencido, físico100, sem reserva/quarentena → cenDisp=0, mas projeção fisico.Sintético=100. Pode subestimar necessidade de compra. Fonte e bruto próprios anexados; resultado0/1 preservado, não mascarado. `cenEstDem/cenOsSup/cenOsDem` estão fora do contrato de autoria: Claude reserva/corrige esse gancho ou libera explicitamente. Não alterar composição unilateralmente. Revisor deve conferir outros consumidores de estoque da composição e retestar o afetado.

O delta delimitado está entregue para revisão; EST-1 completo e publicação dependem da composição, revisão crítica do Claude e checks pertinentes. Não aprovar/integrar o próprio PR. Sem homologação real, produção, auditoria integral ou gatilho do PRD final.

Aplicado: guardas no comando, estado/motivo/recuperação no mesmo detalhe, uma regra de validade. Fora: FEFO, isolamento por fazenda (IDs próprios), cadastro/validade diária e composição não liberada. Cortado: comparação mensal duplicada da UI e variável sem uso; nenhuma etapa de controle. Suposição: mês/ano já é o contrato do protótipo.


## Correção após revisão automática 5510649280 (13/10)

O head329e466 usava indevidamente a data de planejamento D2.HOJE23/09 para novos registros; corrigido para dados_config.DIA_OP26/09, igual à Produção. E2.hoje lê a mesma fonte, preservando uma regra de validade. Contraprova est_validade_data_test.py0/3 antes →3/3 depois; verifica fontes independentes e novo turno/apontamento. Primeiro executor tentou ler chave do turno após encerrá-lo (null); corrigido antes da reprodução válida, ambos brutos preservados. Registros antigos não são reescritos.

Regressões do delta: validade11/11, entrada11/11, alçadas103/103, A453/53; ap_unico unit80/80. A parte navegador desse agregador esbarrou no sandbox de localhost; foi executada separadamente com autorização: 23/23, exit0, bruto próprio. Build focado/render exit0.

Novo caminho pendente, discussão4264599742: cenConcPrevia aceita reserva própria vencida como origem física para excedente. Contraprova original0/1; est_validade_conc_pendente.py ampliada2/3 (custódia já entregue e recusa passam): reservado cobre falta2L, erro vazio, cenConciliar aceita e físico1199→1197. Cenário legítimo liberaOS0430, entrega1L/item, inicia turno e relata3L do primeiro produto. Pedida extensão de autoria6156373350, sem alterar cenConcPrevia/cenConciliar antes do ACK. Solução deve bloquear apenas retirada complementar vencida, preservar conciliação do já entregue em custódia e recusa sem efeito; CTL4 continua pendente separado. Não integrar/publicar o PR antes dos caminhos e revisão resolvidos.
