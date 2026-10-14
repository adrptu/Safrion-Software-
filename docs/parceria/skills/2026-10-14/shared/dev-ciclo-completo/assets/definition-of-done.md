# Definition of Done

Uma entrega está pronta quando os critérios aplicáveis ao escopo foram verificados na versão candidata. Marcar não aplicável com motivo; não inventar execução nem transformar um ajuste documental em implantação de produto. Regras do projeto e o SKILL.md prevalecem sobre exemplos deste checklist.

## Código
- [ ] Faz exatamente o que a tarefa pede — nem mais (sem funcionalidade "de brinde"), nem menos
- [ ] Tipagem estrita sem `any`, `@ts-ignore`, `eslint-disable`, `# type: ignore` sem justificativa em comentário
- [ ] Checks aplicáveis de lint/formatação/tipos passam conforme política do projeto
- [ ] Sem código morto, duplicado, comentado ou `TODO` sem issue vinculada
- [ ] Erros tratados em toda fronteira (rede, banco, disco, entrada do usuário) com timeout e mensagem acionável
- [ ] Sem segredo, credencial ou dado pessoal no código, log ou teste
- [ ] Nomes revelam intenção; funções curtas com um propósito; sem números mágicos

## Testes
- [ ] Testes unitários para toda regra de negócio nova/alterada, incluindo limites e erros
- [ ] Teste de integração quando toca banco, fila, API externa ou outro módulo
- [ ] Teste E2E se altera fluxo crítico do usuário (login, compra, cadastro, pagamento)
- [ ] Bug corrigido tem teste de regressão que falhava antes da correção
- [ ] Checks exigidos executados; zero testes, ajuda, skips e falhas intermitentes não contam como aprovação
- [ ] Cenários críticos e gates de cobertura do projeto atendidos; limitações e bloqueios explícitos

## Revisão
- [ ] PR focado e revisável, com problema, resultado, evidências e capturas pertinentes
- [ ] Self-review feito (ler o diff inteiro como se fosse de outra pessoa)
- [ ] Checks exigidos e pertinentes aprovados na candidata identificada
- [ ] Revisado por pessoa ou agente com o checklist de `dev-revisao`; comentários resolvidos

## Produto e UX
- [ ] Segue `ux-essencial` (uma primária por contexto ativo, estados e recuperação, acessibilidade e temas adotados)
- [ ] Passou pelo procedimento de corte de `minimalismo-essencial`; lista de cortes entregue; nada supérfluo na tela
- [ ] Tabelas seguem `tabelas-interativas`
- [ ] Textos em pt-BR revisados; formatação de número/data/moeda correta

## Operação
- [ ] Migrações versionadas, compatíveis e testadas com dados de demonstração; recuperação sem perda indevida verificada
- [ ] Variáveis de ambiente novas em `.env.example`, validadas no boot e configuradas nos ambientes
- [ ] Logs estruturados, métricas e rastreamento cobrem o caminho novo; erro chega ao rastreador adotado pelo projeto com contexto seguro
- [ ] Feature flag/rollback definidos para mudança arriscada
- [ ] Documentação atualizada no mesmo PR (artefatos afetados, como README, ADR, OpenAPI e AGENTS.md; CLAUDE.md referencia a mesma fonte)
- [ ] Quando houver entrega executável: homologação verificada, desempenho contra metas e aceite humano exigido antes de produção

- [ ] Fonte/diff, base e versão recuperáveis; relato e prova distintos; revisão cruzada e integração pelo revisor quando exigidas
- [ ] Estado da entrega identifica protótipo, implementação real, teste, publicação e HML sem confundir conclusão parcial com funcional
