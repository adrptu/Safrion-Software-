# Como contribuir

1. **Comece por uma issue** com os IDs do PRD e os critérios de aceite (modelos em `.github/ISSUE_TEMPLATE/`).
2. **Branch própria** a partir da `main`, no formato `tipo/nnn-descricao-curta` (ex.: `feat/012-reserva-com-validade`, `docs/004-prd-v3-10`). Trabalho em paralelo usa branches ou worktrees separados, com um responsável por tarefa.
3. **Pull request pequeno**, de preferência até cerca de 400 linhas alteradas fora de arquivos gerados:
   - uma intenção por pull request;
   - código, testes e documentação mudam juntos (ENG-020);
   - o modelo de pull request pede requisitos, evidência, risco e reversão.
4. **Revisão independente:** outro agente ou pessoa revisa. Ninguém aprova nem integra o próprio pull request. Alterações em permissão, saldo, cálculo, pagamento, migração ou infraestrutura pedem revisão do domínio ou de segurança também (ENG-019).
5. **Evidência:** checks da CI verdes no commit revisado, com os comandos e as saídas relevantes no pull request. O que não foi executado fica marcado como "especificado".
6. **Mensagens de commit** no imperativo, em português, com a linha de coautoria quando houver.
7. **Merge** pela interface do GitHub, depois da revisão e dos checks. Nada de push direto nem force push na `main`.

Severidade de defeito: S1–S4 (PRD 22.1). Prioridade de trabalho: P0–P3 (`AGENTS.md`).
