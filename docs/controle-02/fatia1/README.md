# CONTROLE-02 · fatia 1: conferência diária da O.S.

Autoria Codex, revisão/integração Claude real. Contrato DUPLA-20261013-01, recibos6136895755/6136915810 e desenho6137024482. Base177be524; fonte de produto equivalente à0c0931f (a comparação intermediária contém somente docs/integracao/CTL4-FIX). Destino claude/prototipo-v44; conferir a ponta antes da integração. Não altera os arquivos CTL4/BEN/ACELERA reservados.

A conferente abre o dia em Apontamentos, compara o realizado com o contexto da O.S. e registra Conferido ou Não conforme, com motivo na divergência. Uma divergência abre caso identificado; CMD-09 não o resolve. A ação explícita de vínculo documental (recorte CMD-50) exige evidência de que o fato existente é válido, revalida caso/versão e preserva o recibo do caso. A fase, área, saldo, movimentos e custódia não mudam. Reenvio equivalente recupera o mesmo recibo. Prévia desatualizada é recusada; Rever dados atuais preserva motivo. Mudança futura da versão não apaga nem reabre o recibo de um fato anterior. Rascunho por O.S./dia; troca de perfil fecha o formulário e a permissão é revalidada no comando. Regras agronômicas e decisão de estoque continuam próprias.

Referências canônicas: CMD-09/10/50, OSDIA-03..08 e DEMO-13. Registro de conferência: Conferido / Não conforme; no segundo caso o apontamento fica Provisório para manter os consumidores existentes. Apontamentos antigos Conferidos não recebem autoria fictícia: a tela informa ausência de recibo detalhado. Não há meta diária registrada nesses fatos: a tela distingue área executada do dia e escopo autorizado total, sem inventar desvio diário nem recalcular dose antiga pela versão atual.

Aplicado: subdetalhe dentro da O.S.; uma ação primária no contexto ativo; recibo e recuperação junto da decisão; teclado e alvos44px. Fora: edição do fato físico, revisão técnica, resolução do Estoque, banco/login/HML. Cortado: submenu/tela nova, aprovação duplicada, cálculo de meta diária inexistente.

## Provas executadas

- 30/30 unidade sobre cenario.js, perfis e JS_NUCLEO reais, incluindo os comandos de encerramento e seu responsável.
- 16/16 navegador diário e 14/14 casos (duas abas reais, arquivamento, segregação, selo, consulta): motivo obrigatório/foco, contexto, rascunho ao reabrir O.S., resolução/histórico, versão concorrente, recuperação, perfil, teclado e390px; sem erros JS. Captura inspecionada localmente. Teclado virtual não executado.
- 80/80 regressão existente ap_unico_test.py unit.

Brutos: unit.json, nav.json e ap-unico-regression.txt. Hashes em manifest.json. Testes novos não mockam permissão ou comando. O navegador usa os_lib/App existentes, perfil Chrome isolado e servidor127.0.0.1, sem dados reais.

De tools/prototipo/v37/gen37, Python3.12 e Node no PATH:

```sh
python3 -c 'import areas.processo_os as p; p.build()'
python3 montar_render.py
python3 conferencia_diaria_test.py --output /tmp/controle02-unit.json
python3 conferencia_diaria_nav.py --output /tmp/controle02-nav.json
python3 ap_unico_test.py unit
```

Escolher outputs novos; scripts recusam sobrescrever brutos. Nav também salva captura PNG. Scripts fontes e provas pertencem à mesma candidata; publicação depende da revisão pertinente e integração pelo revisor. Não encerra CONTROLE-02 inteiro, conjunto do protótipo ou gatilho PRD.


Revisão4254267592/4254267597: provisório somado sem recibo agora exige conferência; descartado não bloqueia encerramento, conserva recibo e aparece como Fora do acumulado. Contraprova com comandos reais de apontar/app/substituir/agrônomo antes18/20→depois20/20; nav13/13 e regressão80/80. Brutos adicionais em close-counterexamples.json.

## Correção da crítica Claude 6137033305 (recuperada em 13/10)

A crítica do desenho, antes não incorporada ao registro, procede: conferir com texto livre não pode fechar divergência por caminho paralelo. O comando diário agora abre caso com origem, identificador, versão e motivo; somente resolver o caso permite conferi-lo. Vínculo documental explícito valida permissão, versão da O.S., referência e versão do caso, conteúdo físico e pendências técnicas/Estoque. Reenvio exato retorna o recibo; referência de caso anterior não fecha novo caso. Segregação reutiliza cenRevisao. Histórico de abertura e resolução é preservado. Nenhum efeito físico é reaplicado.

Limite solicitado para revisão crítica: a base não tem resolvedor genérico de relato além de consumo/duplicidade. Este recorte implementa vincular evidência ao fato já contabilizado e arquivar caso de relato já descartado pela decisão de duplicidade, sem novo estorno. Aceitar outro fato, recusar/estornar ou converter para correção não foram implementados nem são simulados; caso que exige mudar quantidades permanece aberto, até correção vinculada própria. Isso não fecha CONTROLE-02/CMD-50 completos. Não chamamos o resolvedor de duplicidade sobre um relato já somado e não alteramos cenario.js reservado. Claude deve avaliar esse recorte antes de integrar/publicar.

Brutos desta revisão: cmd50-unit.json (27/27), cmd50-nav.json (16/16), cmd50-counterexamples.json. Testes executados sobre núcleo real. ap_unico reexecutado 80/80 no terminal, sem mudança no seu núcleo; bruto da rodada anterior permanece. Primeira contraprova 19/25; após implementação, uma fixture que incrementava horas ausentes gerou NaN e foi corrigida para alteração real de área. Não foi relaxada regra do produto. Caso antigo/reabertura e segregação foram acrescentados. Captura da resolução em 390px inspecionada localmente; ação primária visível e alcançável. O resumo 0/0 emitido por Os.fim pertence ao acumulador não usado do helper; os 16 resultados efetivos estão no JSON desta jornada, todos passados.

Aplicado: caso/resolução no mesmo subdetalhe, um objetivo primário e recuperação com rascunho. Fora: alterações físicas e demais decisões CMD-50, por exigir comando e contrato próprios. Cortado: segundo caminho de resolução por Conferir dia. Revisão/integração Claude pendentes; sem publicação.

## Retorno Claude 6138112576 e bot 4254646830

N1 corrigido: cenPodeEncerrar precede cdPendente, tanto na projeção quanto no comando. Estoque/sinal/duplicidade/agronomia mantêm prioridade e responsável; conferência diária continua obrigatória após essas dependências. N2: jornadas afetadas agora conferem os dias pela UI real, com Paula e motivo escrito (helper conferencia_diaria_nav_helpers); a prova unitária de dose chama o comando real. As duas asserções próprias verificam primeiro a sobra, recebem a devolução pelo comando e só então exigem a conferência. Nenhuma regra foi desativada para tornar teste verde.

N3: referência inclui a sequência dos recibos, além de versão e fato. Reenvio exato recupera o último recibo; outra decisão com prévia antiga é conflito. Contraprova executada com duas abas reais no mesmo perfil: a primeira mantém rascunho, a segunda abre caso; a primeira não o resolve até rever a referência atual. N4: vínculo documental explícito permanece limitado e requer aceite Claude; não é implementação de todas as decisões CMD-50.

4254646830 reproduzido: caso aberto do dia substituído sumia da pendência. Agora caso aberto continua bloqueando mesmo fora do acumulado; arquivamento exige descarte por decisão de duplicidade registrada, motivo, papel e referência atuais. Mantém o apontamento descartado, copia a decisão de descarte para a trilha, fecha somente o caso e não repete efeitos. Teste usa comandos reais de web/app/"vale este", sem fabricar estado descartado. Arquivar um fato válido é recusado.

S4 atendidos no recorte: N5 mensagem neutra e referência aos Apontamentos da O.S.; N6 horário local pt-BR; N7 encerradas em consulta sem Conferir; N8 duplo clique não deixa rascunho de erro; N10 aviso de revisão posterior antes de gravar; N11 selo de divergência diária também Em execução, sem substituir os responsáveis anteriores. N9 continua melhoria pendente: conferir dias exige decisão explícita por fato; não foi removida a regra nem inventada aprovação em lote nesta correção.

Provas novas executadas: domínio diário30/30, navegador diário16/16, casos14/14, dose35/35 + mapa2/2, dose navegador22/22, bloqueios13/13, ap_unico navegador23/23. os_cenario21/22: única falha é a expectativa legada c.v=2 diante da semente6, a mesma identificada pelo revisor na base177be524; sem falha nova nessa jornada. Build executado, render142 páginas, sintaxe Python/JS verificada. A bateria completa de27 testes do revisor não foi repetida: reaproveitamos as provas de base/partes inalteradas, retestando as cinco jornadas afetadas. Não declaramos suíte total verde ou aceite do revisor antes de seu retorno.

Brutos nfix-* e n1-dose-* preservados. Primeiro os_cenario/dose-nav interromperam por diretório local _probe ausente; após preparar o diretório, somente esses testes foram retomados, com logs separados. Captura de arquivamento390px inspecionada: ação primária visível. O helper Os.fim imprime0/0 para os testes próprios; os JSONs próprios têm16 e14 resultados passados. Executor local, dados sintéticos; teclado virtual real não testado. Revisão e integração Claude pendentes.

Varredura focal gerada: RESULTADO: 3/3 páginas sem erro. Unidade final30/30 após ajuste de microcopy, em nfix-final-unit.json.
