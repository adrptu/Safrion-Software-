# Como contribuir

1. **Comece por uma issue** com os IDs do PRD e os critérios de aceite (modelos em `.github/ISSUE_TEMPLATE/`).
2. **Branch própria** a partir da `main`, no formato `tipo/nnn-descricao-curta` (ex.: `feat/012-reserva-com-validade`, `docs/004-prd-v3-10`). Trabalho em paralelo usa branches ou worktrees separados, com um responsável por tarefa.
3. **Pull request pequeno**, de preferência com poucas centenas de linhas fora de arquivos gerados. É orientação, não portão: composição e merge de branches podem ser maiores, desde que mantenham uma intenção:
   - uma intenção por pull request;
   - código, testes e documentação mudam juntos (ENG-020);
   - o modelo de pull request pede requisitos, evidência, risco e reversão.
4. **Revisão independente, conforme o protocolo triplo** (`AGENTS.md` §3.4 e [`docs/parceria/protocolo.md`](docs/parceria/protocolo.md)): Codex, Claude e Gemini contribuem e validam o que for pertinente, e a pessoa responsável revisa quando houver. Ninguém aprova nem integra o próprio pull request. Alterações em permissão, saldo, cálculo, pagamento, migração ou infraestrutura pedem revisão do domínio ou de segurança também (ENG-019).
5. **Evidência:** checks da CI verdes no commit revisado, com os comandos e as saídas relevantes no pull request. O que não foi executado fica marcado como "especificado".
6. **Mensagens de commit** no imperativo, em português, com a linha de coautoria quando houver.
7. **Merge** pelo GitHub (interface, ou `gh pr merge` com o SHA revisado em `--match-head-commit`), depois da revisão e dos checks. Nada de push direto nem force push na `main`.

Severidade de defeito: S1–S4 (PRD 22.1). Prioridade de trabalho: P0–P3 (`AGENTS.md`).
