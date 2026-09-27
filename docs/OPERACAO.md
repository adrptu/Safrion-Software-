# Operação: publicação, retorno e responsabilidades

**Situação:** não há ambiente implantado. Este guia será preenchido junto com o primeiro incremento que tiver implantação, seguindo o PRD 27 (CI/CD, publicação e migrações), 28 (infraestrutura), 29 (desempenho) e 30 (observabilidade, incidentes, backup e continuidade).

Quando houver implantação, o guia precisa ter, testados e com evidência:
- ambientes DEV, HML e PROD isolados (PRD 27.4) e quem pode publicar em cada um;
- publicação pelo workflow protegido, com aprovação registrada;
- migrações compatíveis com a versão anterior e o procedimento de retorno;
- monitoramento, alertas e quem responde (PRD 30);
- backup e restauração testados, com a data do último ensaio;
- segredos: onde ficam, quem tem acesso e como revogar (ENG-017).

Nada disso está feito. Não afirme o contrário.
