# Checklist de revisão de código

Marque severidade em cada comentário: **[bloqueia]** · **[sugestão]** · **[nit]**.

## 1. Correção
- [ ] Implementa exatamente o pedido; comportamento anterior preservado onde não deveria mudar
- [ ] Casos limite: vazio, nulo, 0, 1, máximo, negativo, unicode/acentos, strings longas, listas grandes
- [ ] Concorrência: duas requisições iguais ao mesmo tempo; duplo clique; operação repetida (idempotência)
- [ ] Datas: UTC no armazenamento, fuso na exibição, horário de verão, fim de mês/ano
- [ ] Dinheiro: inteiro/decimal, arredondamento definido, soma de parcelas fecha o total
- [ ] Condições e comparações corretas (`<` vs `<=`, `==` vs `===`, off-by-one em paginação)

## 2. Erros e resiliência
- [ ] Toda chamada externa tem timeout; retry só em falha transitória, com backoff e limite
- [ ] Nenhum `catch` vazio ou que só loga; erro chega ao usuário com ação possível e ao Sentry com contexto
- [ ] Transações envolvem operações que precisam ser atômicas; rollback em falha
- [ ] Entrada inválida → 400 com detalhe do campo; recurso inexistente → 404; sem stack trace exposto

## 3. Segurança
- [ ] Validação de entrada na borda (schema) e autorização em todo endpoint/ação (objeto pertence ao usuário/tenant?)
- [ ] Sem SQL/comando/HTML concatenado; queries parametrizadas; saída escapada
- [ ] Sem segredo, token, senha ou PII em código, log, teste, URL ou mensagem de erro
- [ ] Dependência nova justificada, mantida, sem CVE conhecida
- [ ] Upload: tipo/tamanho validados; arquivos fora do webroot; nomes sanitizados

## 4. Testes
- [ ] Existem para todo comportamento novo/alterado; nomes descrevem comportamento
- [ ] Testam limites e erros, não só o caminho feliz
- [ ] Determinísticos (sem tempo real, rede, ordem); banco real em integração
- [ ] Nenhum `skip`/`only`; cobertura não caiu

## 5. Legibilidade e estrutura
- [ ] Entendo cada função em uma leitura; nomes revelam intenção
- [ ] Funções curtas, um propósito, ≤ 3 parâmetros, sem flag booleana
- [ ] Sem duplicação de conhecimento (existe util/componente que já faz isso?)
- [ ] Sem código morto, comentado, `TODO` solto, `console.log`
- [ ] Sem números/strings mágicos; sem `any`/`ignore`
- [ ] Módulo certo (domínio não importa infraestrutura; UI não contém regra de negócio)

## 6. Desempenho
- [ ] Sem N+1; índice existe para o filtro/ordenação da query; paginação em listas
- [ ] Sem carregar tudo em memória; streams para arquivos grandes
- [ ] Frontend: sem re-render desnecessário, bundle não cresceu sem motivo, imagens dimensionadas

## 7. Compatibilidade e operação
- [ ] Migração expand/contract, reversível, testada com dados
- [ ] API retrocompatível ou versionada; clientes antigos continuam funcionando
- [ ] Variáveis de ambiente novas documentadas e validadas; feature flag onde há risco
- [ ] Logs/métricas cobrem o novo caminho; documentação atualizada

## 8. Produto
- [ ] Segue `ux-essencial` (ação primária única, fricção zero, estados, acessibilidade, claro/escuro)
- [ ] Tabelas conforme `tabelas-interativas`; textos pt-BR, formatos locais
