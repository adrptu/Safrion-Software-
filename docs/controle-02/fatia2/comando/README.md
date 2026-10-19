# Referência técnica — CONTROLE-02/F2

Autor Codex; revisor/integrador Claude. PR58 depende do PR57. A publicação fica disponível apenas quando a composição fornece `safImpedimentosRef` e AL-18. Sem essas dependências, o painel permanece consulta. Não encerra F2 nem substitui aceite da composição real.

## Comando e contexto

`PlanoReferenciaComando.publicar(self,{chave,esperada,safra,ator,previa},validarDominio)` usa exclusivamente `cenMudar(...,{estrito:true})` e `cenIdem`. `esperada` é null antes de R1 ou o ID da última referência. A chave fica igual no retry; replay recupera versão/recibo sem incrementar rev. Outra carga com a mesma chave dá conflito. R2 preserva R1 e marca orçamento a revisar. Sem mudança, não cria outra versão nem limpa essa marca. Não aprova orçamento nem libera O.S.

Persiste `c.planoReferencias=[{contexto:{fazenda,safra},versoes:[{id,por,em,sq,retrato}],orcamentoRevisar}]`; recibo `PLANO-REF:<intenção>` contém metadado `plano:{contexto,id,nova}` sem duplicar snapshot. Ambos falham juntos com erro de escrita estrita. `PlanoReferencia.trilha` consome as versões; sq vem da revisão gravada.

Contexto, permissão, estado, prévia e referência esperada são revalidados. Replay revalida contexto/permissão; fazenda ausente é recusada, sem assumir Santa Rita. `validarDominio(self,safra,c)` deve retornar sincronamente `{impedimentos:string[]}`; o comando o chama dentro da transação. A UI consome também `avisos:string[]`. Ausência, retorno incompleto ou impedimento recusam publicação. O mapa e a implementação das regras pertencem à composição Claude, recibo6152055144; não duplicar regras de domínio aqui.

## Prévia e confirmação

Mesmo subdetalhe da safra: conferir publicação mostra contexto, autor, avisos, impedimentos e consequência, sem gravar. Histórico/comparação permanece consultável fora da confirmação. O botão confirma o retrato conferido e revalida o adaptador. Troca de perfil exige nova prévia; falha conserva intenção e erro na tela. Sucesso só aparece com versão/seq/data/autor persistidos. Retorno e Escape preservam rascunho/foco. Foco na confirmação não rola o cabeçalho para fora da tela.

Claude mantém safra.js/safImpedimentosRef, cenario.js, g2lib/AL18 e CF04; Codex plano_referencia*.js/.py e testes. A base PR57 contém núcleo f2aaec84. Executor local composto com gravador Claude fd0b1c44; a base isolada v56 não é ambiente pronto. Interface do adaptador está conectada, mas validação agronômica e CF04 reais ainda exigem composição e revisão.

## Evidência e limites

Node no PATH, `python3 plano_referencia_comando_test.py`: **19/19 +1 guarda**, em `previa-unit.txt`. R1/R2, replay, conflito, cota/retry, revogação, alteração após prévia, contexto/encerramento, fazenda ausente e callbacks da UI. O teste injeta explicitamente AL18 e adaptador sintético. Não prova regras agronômicas nem concorrência simultânea entre abas. O gravador real foi revisto separadamente,10/10 (`strict-test.txt`); núcleo41/41 no PR57.

`python3 plano_referencia_publicar_nav.py`: navegador real1440×1000/390×844, **24/24** (`publicar-nav.txt`). Publica por botão, recupera R1 após reload, confirma duplo envio único, mostra aviso/impedimento, preserva cabeçalho/foco/rascunho e retorno/Escape. Fixture de domínio e AL18 só na cópia temporária do HTML; isso não é aceite do adaptador real nem candidata publicada. Capturas inspecionadas. Rodada inicial22/22 revelou pela imagem a rolagem do cabeçalho; fix preventScroll e duas asserções adicionais executadas na rodada final. Consulta persistida31/31 anterior preservada (`consulta-persistida-nav.txt`); os6 casos CF05 são revisão separada no retorno6150155986.

Aplicado: prévia explícita, uma primária por contexto, retorno/foco, recibo real do gravador local e erro recuperável. Fora: regras agronômicas reais/CF04 composto, concorrência simultânea, teclado virtual, servidor/banco/HML. Cortado: confirmação extra sem finalidade, armazenamento paralelo, suposição de fazenda e sucesso antes do recibo. O protótipo não oferece controle de acesso de produção.
