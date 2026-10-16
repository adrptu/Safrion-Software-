# OS-LOTE F1 + Y4 — correção da revisão 6224997396

Autor da candidata: Codex. Revisor/integrador: Claude real. Base imutável do delta: `6dfa09c190cf55ff16da841561d5739b138b7646`. Patch de colaboração Claude recuperado de `3f95717`, `docs/integracao/V72/os-lote-rev-claude/ajustes-claude.patch`; autoria dessa contribuição preservada. Nenhuma integração própria.

## Tratamento consolidado

- R1: `demoLote` distingue as quatro ordens demonstrativas da numeração das novas O.S. no formulário e no MIP.
- R2: mantida a demanda das O.S. planejadas: +75 kg de Sulfato de magnésio e +R$157,50 na LG2627. Oráculos Python/JS atualizados para R$1.614.360,34; não se excluiu demanda válida para fazer o teste passar.
- R3: AL-19 configurável no CF-01, lida pelo comando real. Padrão PCP **ou agrônomo** preserva o conjunto de pessoas autorizado no HEAD anterior; não herda AL-02 dinamicamente. CF-01 pode trocar o papel entre PCP/agronomia/gestão, sob suas travas existentes. Não concede AL-01/CMD-06 nem AL-02/CMD-42. Caso de comando real positivo/negativo e troca para gestor comprovam revogação do PCP.
- R4: `cenGrupoLiberar` passou para JS_NUCLEO, junto de `osc_liberar`; efeito e idempotência preservados.
- A1/A2: diálogo usa o controle de foco existente; após concluir, a ação de agrupar começa nova composição, mantendo o grupo anterior acessível. Runner Enter/booleano corrigido conforme patch Claude.
- A3/A4: fuso herdado da janela, recusado se diferente no comando; janelas das origens com fusos divergentes também recusadas. Horários apresentados em data local e UTC explícito.
- D1: separar confere compromissos de execução e snapshots atuais, sem exigir ficha técnica de versão antiga. Revisão e cancelamento não aprisionam a composição; liberar continua exigindo a versão exata aprovada.
- D2: soma as quantidades arredondadas **na unidade original de cada origem**, antes de converter g/mL para kg/L. A soma decimal usa cenDec; evita a nova divergência que surgiria ao arredondar 5 mL como 0,01 L. Contraexemplos 4,5135→4,5 kg e mistura de L/mL cobertos.
- S4b/c/d/e/f: mapeamento pessoa/recurso confere nome; consequência diferencia programação confirmada/pendente; separar/programar não aparecem quando há compromisso; liberação sem AL-01 tem motivo visível; recibo não deixa primária inerte nem produz erro de seleção no segundo clique; Origem da O.S. informa grupo e versão.

## Prova executada por Codex

Executor local, Node v24.19.0/Python, dados sintéticos, armazenamento isolado. Nenhum navegador/CDP/serviço iniciado.

- `node os_lote_unit.js`: **85/85**, incluindo os 74 anteriores e 11 regressões. Sonda Claude reproduzida antes/depois: cancelada presa→separável; 4,5135→4,5; mesmo instante em outro fuso aceito→recusado.
- `python3 config_unit_test.py`: **226/226**; patch Claude sem R3 reproduziu **220/221**.
- `python3 alocacao_unit_test.py`: **21/21**.
- `python3 mip_unit_test.py`: **34/34**.
- `python3 cal01_test.py`: **45/45**.
- `python3 demanda_unica_test.py`: **66/71**, cinco falhas A8/E1/E2/E3/H1 `KeyError: Santa Rita` iguais, linha por linha, ao bruto Claude da base/patch. Sem duas regressões R2 restantes; não declarar suíte integral verde.
- `links_ocultos_test.py`: oito verificações de código passaram, inclusive E1/E1b/E1c; restante não executado por ausência de `project/canvas.json` no recorte local. Não montar infraestrutura apenas para repetir prova existente; reconferência pertinente com Claude.
- AST dos seis Python alterados, geração real de OS.dc.html e `node --check` do script gerado: passaram. SHA256 HTML `847af73f88e3bf4faacf3c7036e41329602603c2c3d0f83bcf384474dab256db`.
- Durante montagem dos testes, corrigidos escape de regex no wrapper Node e seleção de só duas origens quando a terceira ainda ocupava recurso. Não são resultados verdes ocultando falha do produto.

Brutos em `before/` e `after/`; manifesto identifica blobs e SHA256. Navegador final 1440/390, Tab/Escape/foco, controle de alçada/recibo, UI da nova ordem, regressões afetadas e composição com PR89: pendentes de Claude. Provas anteriores em `3f95717` são da candidata + patch Claude, não desta candidata adicional.

## Pendências que não são encerradas por esta correção

S4a: recibos ainda guardam snapshots canônicos extensos. Quota/rollback estão cobertos; troca por digest precisa preservar igualdade/idempotência e compatibilidade, sem introduzir hash fraco como se fosse equivalência exata.

S4g: jornada e navegação da Carga para semanas posteriores continuam pendentes no mesmo OS-LOTE. O grupo exibe seus blocos, mas não se declara resolvida a visão semanal fixa nem validação de jornada.

S4h: projeções de cargas ainda têm contagem duplicada/resíduos em área intermediária; D2 resolve o total de insumos por origem, não toda a projeção de preparo. Não ampliar esta correção para refatorar Y4/preparo já validado sem contrato proporcional.

Solicitada decisão explícita do revisor sobre essas três S4 remanescentes antes de integrar; se bloqueantes, devolver a menor continuação no mesmo PR. Não são conclusão funcional nem aceites tácitos. Conjunto do protótipo, auditoria integral, PRD final, aplicação real/HML/produção continuam pendentes.

Aplicado: contexto, foco existente, estados e consequência por operação. Fora: novas regras de aprovação e nova infraestrutura. Cortado: ação de liberação sem alçada, separação impossível e ação redundante após recibo, com motivo/resultado preservados.

## Transporte das provas

A revisão automática recusou o upload do log detalhado de demanda por possível exposição de dados internos. O bruto permanece somente na cópia local da entrega. Neste diretório remoto, `after/demanda-resumo.txt` registra somente contagens e comparação com a base, sem o payload recusado. As duas tentativas iniciais de enviar a árvore inteira falharam por mudança do catálogo do conector; a branch não mudou, conferida antes da estratégia de blobs individuais.
