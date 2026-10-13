# Publicação da referência técnica — comando F2

Autor Codex; revisor/integrador Claude. Continuação da mesma fatia CONTROLE-02/F2; PR dependente da57. Contratos6151403193/6151490018, gravador Claude6151368134. Não encerra F2-01..06 nem habilita publicação na UI.

`PlanoReferenciaComando.publicar(self, {chave, esperada, safra, ator, previa}, validarDominio)` grava versão e recibo no cenário compartilhado, usando exclusivamente `cenMudar(...,{estrito:true})` e `cenIdem`. `esperada` é null antes de R1 ou o ID da última referência. A chave representa a intenção e deve permanecer igual no retry. Reenvio confirmado recupera versão/recibo sem incrementar rev. Outra carga com a mesma chave é recusada. R2 preserva R1 e marca orçamento a revisar; repetição sem mudança não apaga essa marca. Nenhuma publicação aprova orçamento ou libera O.S.

Persistência: `c.planoReferencias = [{contexto:{fazenda,safra},versoes:[{id,por,em,sq,retrato}],orcamentoRevisar}]`. O recibo de cenIdem usa chave `PLANO-REF:<intenção>` e metadado `plano:{contexto,id,nova}`; não duplica o retrato. A trilha consome `PlanoReferencia.trilha(h.versoes)`; sq vem da revisão do gravador. O snapshot e o recibo falham juntos quando a escrita estrita falha.

Revalida contexto, cadastro/permissão AL-18, estado da safra, prévia e referência esperada na operação. Replay também revalida permissão/contexto. O adaptador de código `validarDominio(self,safra,c)` deve retornar sincronamente `{impedimentos:string[]}` com as regras existentes de área/dose/capacidade/recomendação. É chamado dentro da transação, nunca substituído por um booleano de aprovação. Ausência, retorno inválido ou impedimento recusam a operação. A UI não deve fornecer um adaptador vazio; esse adaptador existe somente como fixture nos testes.

## Dependências e autoria

A base deste PR tem o núcleo f2aaec84 do PR57. Testado por composição local com fonte Claude fd0b1c44ba8f44f4ed40364ebd6bb36dd010e93f (gravador estrito/CONF), sem incluir esses arquivos na autoria Codex. O executor requer essa composição: não apresentar a base v56 sozinha como ambiente pronto. Sem o gravador estrito, o comando recusa antes de acessar o cenário.

Claude mantém cenario.js, g2lib.js/AL-18 e CF04. Codex mantém plano_referencia*.js/.py, UI SAF e documentação F2. AL-18 está aceita pelo autor, mas a entrada de teste é fixture; falta compor a entrada real. Mapa de impedimentos e integração de UI/CF04 continuam pendentes. A leitura/seleção de histórico deve usar contexto completo de fazenda/safra, sem escolher o primeiro registro.

## Evidência executada

Em `tools/prototipo/v37/gen37`, Node no PATH, executar `python3 plano_referencia_comando_test.py` sobre a composição descrita: **13/13 +1 guarda de dependência**. `comando-unit.txt` cobre R1, replay/recarga JSON, conflito de intenção, R2, no-op, duas prévias sequenciais, cota/retry, revogação, plano alterado, contexto/encerramento e validação transacional. Usa seletores, cenário, cenIdem e gravador reais; localStorage controlado e adaptador de domínio/AL18 de teste, só dados sintéticos. Não prova concorrência simultânea entre processos/abas, UI, regra agronômica, banco ou HML. O lock/consistência entre abas exige contraprova na composição visual.

`cen_grava_test.py` do Claude: **10/10** reproduzidos, bruto `strict-test.txt`; aceite focal do caminho estrito. Núcleo corrigido:41/41 no PR57. Consulta UI25/25 anterior preservada sem reexecução por não mudar apresentação. Publicação visual ainda não conectada ou testada.

Aplicado: transação compartilhada, recibo recuperável, conflito explícito e rascunho preservado. Fora: adaptador agronômico, composição de alçada/trilha e UI de publicação. Cortado: segundo armazenamento, segundo mecanismo de idempotência e sucesso otimista antes da gravação.
