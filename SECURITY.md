# Segurança

- **Não publique vulnerabilidades em issues abertas.** Comunique ao proprietário do repositório de forma privada.
- **Nenhum segredo, credencial ou dado real** de cliente entra no repositório: código, fixtures, logs, prompts ou artefatos (ENG-017). Segredo exposto é revogado, não apenas apagado do histórico.
- **Varreduras na CI:** segredos (Gitleaks, CLI fixada por checksum, todas as refs do checkout inteiro, com diff de merge por pai e canário no commit raiz e na resolução de merge: `tools/ci/varrer_segredos.py`) e vulnerabilidades e configuração (Trivy). Com código, entram também SAST e dependências (PRD 23.1 e 26).
- **Alta ou crítica bloqueia, com ou sem correção disponível** (PRD 25.2: nenhuma alta/crítica aplicável sem resolução). "Ainda não tem correção" não é exceção.
- **Exceção só por não aplicabilidade comprovada**, em `.trivyignore.yaml`, referenciado no passo do Trivy (`trivyignores`). Cada item tem `id` e, quando der, `paths` ou `purls`; `statement` com a prova (por que o código não é alcançável ou o pacote não vai para o que é publicado); e `expired_at` de no máximo 90 dias. Os dois agentes revisam cada exceção no PR. O `.trivyignore` simples, sem motivo nem validade, é recusado. O portão `tools/ci/checar_ci_seguranca.py` confere essas regras na CI.
- **Requisitos completos de segurança:** PRD 26 (aplicação, infraestrutura e cadeia de dependências) e 24 (integridade e isolamento entre organizações).
