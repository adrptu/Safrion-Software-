# R-006: skills instalados, ferramentas, FERR-01 e plano F0 → F1

- **Data:** 27/09/2026
- **Autor deste registro:** Claude Code
- **Revisor:** Codex
- **Coordenação:** skill `safrion-equipe`, carregado nesta sessão.

## 1. Skills (autor e integrador: Codex; revisor: Claude). Verificado
- **Instalação:** fonte única `~/.agents/skills`; os 14 diretórios de `~/.claude/skills` são links para ela; backup em `cons/work/skills-backup-installed`.
- **Manifesto final** `4bd8aa65…aa129`: 45 arquivos conferidos nos dois caminhos, nenhum divergente.
- **Leitura real:** o catálogo da sessão do Claude lista os 14 com as descrições novas. O `safrion-equipe` foi carregado pelo link.
- **Parecer:** `cons/work/revisao-skills-claude.md`. Aprovado; A1–A10, o adendo de UX e n1–n3 foram incorporados.

## 2. Acesso à IA (autor da proposta: Codex; revisor: Claude). Acordado
- **IA-1 e IA-2:** o acesso fica no cabeçalho, no computador e no celular; o botão flutuante é só variante, se o teste mostrar dificuldade real; um painel por vez.
- **IA-3:** aprovação na Caixa ou em Aprovações; o resultado aparece também no registro de origem.
- **IA-4:** habilitado e indisponível mantém o acesso com o motivo; não habilitado fica fora.
- **IA-5:** nenhuma mudança no protótipo agora; o 59.2 (ajuda contextual cedo) fica preservado.
- **Onde está:** bloco 74.5.31 (DS-87) no rascunho do cap. 74 da v3.10. Revisão: `cons/work/revisao-ia-acesso-claude.md`.

## 3. Ferramentas (autor da matriz: Codex, `cons/outputs/ferramentas-engenharia.md`)
- **Seleção:** vale a do PRD 23.1. Fase e custo estão em `cons/work/revisao-ferramentas-claude.md`.
- **SonarQube (ENG-018):** pendente, com exceção registrada no plano (§4). A proteção interina não equivale ao gate.
- **FERR-01, corrigido:** commit `7ee1d95` na branch `fix/ci-trivy-sem-correcao`. Autor: Claude. Revisor e integrador: Codex.
  - O Trivy bloqueia alta e crítica com ou sem correção.
  - Exceção só por não aplicabilidade comprovada, em `.trivyignore.yaml`, com motivo e validade de no máximo 90 dias.
  - Portão `tools/ci/checar_ci_seguranca.py` com 12 testes. Contra o `ci.yml` anterior, acusa as linhas 48 e 57.
  - **Executado localmente:** 18 testes ok no Python 3.9.6 e no 3.12.14; `checar_docs` 45 ok.
  - **Não executado:** o próprio Trivy e a CI remota.
- **FERR-02:** só avaliado. Os segredos continuam no Trivy e no Gitleaks até o Codex confirmar que o Gitleaks cobre o histórico e os arquivos novos.

## 4. CI remota
Segunda tentativa às 10h54, falhou antes de iniciar: aviso de pagamentos ou limite de gastos na conta (Codex, pelo conector; `actions/runs/36320502642`). **CI não liberada.** Não tentar de novo até a conta mudar. Nada é declarado verde.

## 5. Plano F0 → F1 → homologação (para revisão do Codex, passo 1 do próprio plano)
- **Plano:** [R-006-plano-f0-f1.md](R-006-plano-f0-f1.md). Evidências: `evidencias/R-006-requisitos.md`, `R-006-hospedagem.md` e `R-006-ambiente.md`.
- **Revisão adversarial:** dois revisores, 16 achados decididos, todos com motivo.
- **Resumo:**
  - F0 em três PRs (domínio; banco com RLS, idempotência e outbox; shell com login e `/saude`);
  - homologação no Google Cloud em São Paulo, ≈ US$ 16,32/mês (≈ R$ 88 com IOF), com orçamento de US$ 25 e alertas — **o Google avisa, mas não corta o gasto**;
  - F1 com a tarefa curta do Adrianus (duas notas fictícias, um galão avariado).
- **Decisões do Adrianus**, num pedido único:
  - D1: iniciar o software real, com dados fictícios;
  - D2: print do bloqueio do GitHub;
  - D3: instalar o Docker Desktop neste Mac;
  - D4: autorizar o gasto da homologação, por frase literal.
- **Autorização para iniciar código:** textos e datas em `cons/work/revisao-skills-claude.md`. O D1 fecha a exigência formal que o próprio Adrianus fez em 23/09 ("aguarde meu comando explícito"). Não é confirmação técnica.

## 6. Acordo curto da revisão do plano
```text
ID / resultado útil / persona: R-006-P1 / plano F0→F1 revisado para liberar o pedido ao Adrianus / proprietário
Requisitos do PRD e fora do escopo: AGENTS §2, §3.1–3.4; PRD 23–31; fora: código, contas, contratação
Autor / revisor / integrador: Claude / Codex / Codex
Base (commit ou hashes) / arquivos sob responsabilidade: main a1f5b16 + esta branch / docs/parceria/rodadas/R-006-*
Aceite e comando de verificação: parecer escrito do Codex nesta rodada; python3 tools/docs/checar_docs.py = 0 falhas
Estado / impedimento / próximo passo: aguardando revisão; CI remota bloqueada; depois, o pedido único (passo 2)
```
