# CONTROLE-02 · fatia 1: conferência diária da O.S.

Autoria Codex, revisão/integração Claude real. Contrato DUPLA-20261013-01, recibos6136895755/6136915810 e desenho6137024482. Base177be524; fonte de produto equivalente à0c0931f (a comparação intermediária contém somente docs/integracao/CTL4-FIX). Destino claude/prototipo-v44; conferir a ponta antes da integração. Não altera os arquivos CTL4/BEN/ACELERA reservados.

A conferente abre o dia em Apontamentos, compara o realizado com o contexto da O.S. e registra Conferido ou Não conforme, com motivo na divergência. Uma divergência abre caso identificado; CMD-09 não o resolve. A ação explícita de vínculo documental (recorte CMD-50) exige evidência de que o fato existente é válido, revalida caso/versão e preserva o recibo do caso. A fase, área, saldo, movimentos e custódia não mudam. Reenvio equivalente recupera o mesmo recibo. Prévia desatualizada é recusada; Rever dados atuais preserva motivo. Mudança futura da versão não apaga nem reabre o recibo de um fato anterior. Rascunho por O.S./dia; troca de perfil fecha o formulário e a permissão é revalidada no comando. Regras agronômicas e decisão de estoque continuam próprias.

Referências canônicas: CMD-09/10/50, OSDIA-03..08 e DEMO-13. Registro de conferência: Conferido / Não conforme; no segundo caso o apontamento fica Provisório para manter os consumidores existentes. Apontamentos antigos Conferidos não recebem autoria fictícia: a tela informa ausência de recibo detalhado. Não há meta diária registrada nesses fatos: a tela distingue área executada do dia e escopo autorizado total, sem inventar desvio diário nem recalcular dose antiga pela versão atual.

Aplicado: subdetalhe dentro da O.S.; uma ação primária no contexto ativo; recibo e recuperação junto da decisão; teclado e alvos44px. Fora: edição do fato físico, revisão técnica, resolução do Estoque, banco/login/HML. Cortado: submenu/tela nova, aprovação duplicada, cálculo de meta diária inexistente.

## Provas executadas

- 27/27 unidade sobre cenario.js, perfis e JS_NUCLEO reais, incluindo os comandos de encerramento e seu responsável.
- 16/16 navegador: motivo obrigatório/foco, contexto, rascunho ao reabrir O.S., resolução/histórico, versão concorrente, recuperação, perfil, teclado e390px; sem erros JS. Captura inspecionada localmente. Teclado virtual não executado.
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

Limite solicitado para revisão crítica: a base não tem resolvedor genérico de relato além de consumo/duplicidade. Este recorte implementa apenas vincular evidência ao fato já contabilizado. Aceitar outro fato, recusar/estornar ou converter para correção não foram implementados nem são simulados; caso que exige mudar quantidades permanece aberto, até correção vinculada própria. Isso não fecha CONTROLE-02/CMD-50 completos. Não chamamos o resolvedor de duplicidade sobre um relato já somado e não alteramos cenario.js reservado. Claude deve avaliar esse recorte antes de integrar/publicar.

Brutos desta revisão: cmd50-unit.json (27/27), cmd50-nav.json (16/16), cmd50-counterexamples.json. Testes executados sobre núcleo real. ap_unico reexecutado 80/80 no terminal, sem mudança no seu núcleo; bruto da rodada anterior permanece. Primeira contraprova 19/25; após implementação, uma fixture que incrementava horas ausentes gerou NaN e foi corrigida para alteração real de área. Não foi relaxada regra do produto. Caso antigo/reabertura e segregação foram acrescentados. Captura da resolução em 390px inspecionada localmente; ação primária visível e alcançável. O resumo 0/0 emitido por Os.fim pertence ao acumulador não usado do helper; os 16 resultados efetivos estão no JSON desta jornada, todos passados.

Aplicado: caso/resolução no mesmo subdetalhe, um objetivo primário e recuperação com rascunho. Fora: alterações físicas e demais decisões CMD-50, por exigir comando e contrato próprios. Cortado: segundo caminho de resolução por Conferir dia. Revisão/integração Claude pendentes; sem publicação.
