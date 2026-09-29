# Segurança

- **Não publique vulnerabilidades em issues abertas.** Comunique ao proprietário do repositório de forma privada.
- **Nenhum segredo, credencial ou dado real** de cliente entra no repositório: código, fixtures, logs, prompts ou artefatos (ENG-017). Segredo exposto é revogado, não apenas apagado do histórico.
- **Varreduras na CI:** segredos (Gitleaks, CLI fixada por checksum, todas as refs do checkout inteiro, com diff de merge por pai e canário no commit raiz e na resolução de merge: `tools/ci/varrer_segredos.py`) e vulnerabilidades e configuração (Trivy). Com código, entram também SAST e dependências (PRD 23.1 e 26).
- **Requisitos completos de segurança:** PRD 26 (aplicação, infraestrutura e cadeia de dependências) e 24 (integridade e isolamento entre organizações).
