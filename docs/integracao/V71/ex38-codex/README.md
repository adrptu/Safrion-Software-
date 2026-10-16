## Revisão R2 · 16/10/2026

Correção do retorno Claude6220912272 sobre e3e017c. A previsão restante agora desconta a área registrada offline e usa cenOsSup com a custódia local; o consumo reconhecido no escritório continua vindo de osReqVis. A pendência permanece explícita. Após 20ha/10L offline: necessidade15L, Adjuvante35L,5cargas e consumo reconhecido95L; após envio105L. Área toda no aparelho não pede nova retirada. Não altera a regra de baixa ou sincronização.

Corrigidas carga fantasma por ponto flutuante, trava de preparo que bloqueava recebimento, cartão MB01 sem retirada/embalagem/custódia/conferência e ficha sem parcial/instrução. A ação do cartão vem antes da descrição dos insumos, mantendo-a alcançável. Singular, conjunto com trator, indicação de saldo e motivo acessível da ação foram ajustados. Totais da ficha usam cenQtd; a proporção interna das cargas continua sem arredondamento intermediário.

Provas r2/:17/17 cenários Node,400 combinações,4 AST,5 verificações estruturais em HTML gerado e34 dependências conferidas por blob/origem. Mesmo conjunto Node na candidata anterior e3e017c:12/17, cinco contraprovas. Perfis reais de demonstração carregados por cenario.perfis_js; fechamento, sinal e confirmação usam comandos reais. Recebimento prévio é fixture sintética. Estados/títulos da trilha têm stubs de apresentação no harness; não são prova de navegador. O erro antigo de harness na base519ed7b permanece erro de ferramenta, não contraprova executada.

Gitleaks8.30.1: varredura completa dos fontes editados aponta somente CEN_KEY da linha6, literal localStorage talhao-os-cenario-v1 idêntico no pai; não é credencial. Nenhuma proteção/allowlist alterada. Delta novo e provas sem achados (log específico em r2/).

Claude deve repetir sua revisão45casos, base e mutante2500L, regressões app_entrega_parcial/app_mb03_turno/consumo_divergente/mbtest,390px,teclado ePDF. Codex não executou navegador/teclado/toque/PDF; bloqueio de ferramenta preservado. Entrega para revisão, sem aceite funcional ou integração própria.

---
Histórico anterior, preservado; a descrição de offline abaixo foi superada pela R2:

# EX-38 · preparo, saldo e consumo — candidata Codex
Base: 519ed7be57fdb8f340108fdef06449b3c1c3a1e2. Contrato: recibos6218767007,6218871703 e6218879317 no PR47. Codex autor; Claude revisor/integrador.

Uma projeção por ordem usa o pulverizador alocado (alDaOrdem → AL0.ativo → capacidade de dados_cad) e a instrução versionada do cenário. A instrução100L/ha de OS0421/0424 é sintética, aprovada tecnicamente no recibo6218879317, não recomendação agronômica. Sem instrução vigente/capacidade/conjunto, mostra motivo e não calcula por padrão. Cenário salvo só recupera instrução inicial quando a versão coincide; sem reset, sem alterar v7. Após nova versão é preciso informar sua instrução; PA-OPER tratará origem RT/bula.

O painel, MB02det e app/ficha0424 usam a projeção. Última carga proporcional, dose interna sem arredondar para fazer contas; apresentação até3casas. Consumo só registrado; ausência difere de zero. Previsto do saldo e falta=max(0,previsto−custódia) compartilhados com MB01. Sem requisição também por produto não presente numa REQ existente. Saldo do cenário e custódia registrados não deduzem novamente fila offline; pendência explícita. Não altera comandos, estoque, dose ou aplicação. Marcar carga preparada é estado desta tela, não aplicação; mudança de preparo não reutiliza marcações da versão anterior.

## Evidência executada
- ex38_test.py em Python3.9/Node24:12/12;400 combinações determinísticas com propriedade por carga cheia/parcial, soma de áreas e limite do tanque.
- Blocos reais painel/MB01/MB02det; app0424 EXTRAVALS; geração mobile.build e app/ficha0424; sintaxe Python.
- Contraprova em fontes equivalentes da base: painel3000/100 versus mobile2000/120; adjuvante47,5L sem registro; MB01 só mostra custódia65L. Três falhas esperadas, logs adjuntos.
- Dependências geradoras locais comparadas ao tree1f7bc575; fontes divergentes importáveis recuperadas no snapshot isolado. Dados sintéticos.
- UI local bloqueada: Codex não executou navegador, toque, teclado ou impressão. Provas Node não substituem isso.

## Revisão de Claude pendente
Executar P1–P5 conforme6218879317: painel/MB02det421; painel/app/ficha424 com mesmos valores. Ficha usa linhas dinâmicas com semântica de tabela, totais preservados. Conferir render real e impressão, foco/Enter e390px. Testar sem conjunto, capacidade ausente, instrução ausente/desatualizada, último tanque8ha/800L/4L em424, mudança de versão após marcar carga, consumo0 versus ausente, saldo15L. Retornar um parecer consolidado; integrar somente pelo revisor.

Aplicado: contexto/versão, dados de origem, aviso recuperável, ação existente e saldo explícito. Fora: engine/g2lib/alocacao/cadastros/calibração/embalagem/limpeza/CA01det (retirada do aceite para EX02). Cortado: CALDA/PREP421 duplicados, cálculos estáticos de carga, consumo inferido e alegação falsa de gravação permanente/QR funcional. Não cria menu/rota ou auditoria integral; protótipo incompleto, sem Next/HML/produção.

