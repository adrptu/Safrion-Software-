# CONTROLE-02 · fatia 1: conferência diária da O.S.

Autoria Codex, revisão/integração Claude real. Contrato DUPLA-20261013-01, recibos6136895755/6136915810 e desenho6137024482. Base177be524; fonte de produto equivalente à0c0931f (a comparação intermediária contém somente docs/integracao/CTL4-FIX). Destino claude/prototipo-v44; conferir a ponta antes da integração. Não altera os arquivos CTL4/BEN/ACELERA reservados.

A conferente abre o dia em Apontamentos, compara o realizado com o contexto da O.S. e registra Conferido ou Não conforme, com motivo na divergência/resolução. A fase, área, saldo, movimentos e custódia não mudam. Reenvio equivalente recupera o mesmo recibo. Prévia desatualizada é recusada; Rever dados atuais preserva motivo. Mudança futura da versão não apaga nem reabre o recibo de um fato anterior. Rascunho por O.S./dia; troca de perfil fecha o formulário e a permissão é revalidada no comando. Regras agronômicas e decisão de estoque continuam próprias.

Referências canônicas: CMD-09/10, OSDIA-03..08 e DEMO-13. Registro de conferência: Conferido / Não conforme; no segundo caso o apontamento fica Provisório para manter os consumidores existentes. Apontamentos antigos Conferidos não recebem autoria fictícia: a tela informa ausência de recibo detalhado. Não há meta diária registrada nesses fatos: a tela distingue área executada do dia e escopo autorizado total, sem inventar desvio diário nem recalcular dose antiga pela versão atual.

Aplicado: subdetalhe dentro da O.S.; uma ação primária no contexto ativo; recibo e recuperação junto da decisão; teclado e alvos44px. Fora: edição do fato físico, revisão técnica, resolução do Estoque, banco/login/HML. Cortado: submenu/tela nova, aprovação duplicada, cálculo de meta diária inexistente.

## Provas executadas

- 20/20 unidade sobre cenario.js, perfis e JS_NUCLEO reais, incluindo os comandos de encerramento e seu responsável.
- 13/13 navegador: motivo obrigatório/foco, contexto, rascunho ao reabrir O.S., resolução/histórico, versão concorrente, recuperação, perfil, teclado e390px; sem erros JS. Captura inspecionada localmente. Teclado virtual não executado.
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
