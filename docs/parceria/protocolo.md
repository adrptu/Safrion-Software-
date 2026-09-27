# Protocolo de parceria Claude + Codex

- **Autor:** Codex
- **Revisor:** Claude
- **Versão canônica atual:** fora do repositório, em `/Users/adrianussanders/Documents/Codex/2026-09-27/cons/outputs/protocolo-revisao-agro.md`, até o Codex trazê-la para cá por pull request com os ajustes acordados na rodada R-001.

Resumo do que já foi acordado (R-001):
- Um autor e um revisor por artefato. O PRD é a fonte única.
  - O Claude redige arquitetura, ADRs, contratos e a matriz de cobertura do PRD.
  - O Codex revisa e converte a cobertura em backlog, QA e critérios de pronto.
- Severidade S1–S4 conforme o PRD 22.1, separada da prioridade P0–P3.
- Revisão só conta com registro escrito do outro agente em `docs/parceria/rodadas/` ou no pull request.
- Autorização passada de um agente para outro não substitui a do proprietário nas matérias reservadas a ele (`AGENTS.md`, seção 2).
