# Diretrizes permanentes de UX, UI e design system

Pedido do proprietário em 16/10/2026: "Adote essas referências como diretrizes permanentes para todas as decisões de UX, UI e Design System do Safrion."

- **Avaliação completa e plano em 4 ondas:** documento "Safrion · Avaliação de UX e plano priorizado" (Claude Docs, https://claude.ai/artifact/Y5qBcNrBVVtYFnG5WV9wKK).
- **Onde isto se encaixa:** completa o PRD (cap. 4, 55, 64, 74 e 75), o AGENTS §3.3 e os padrões de 09/10 e 15/10 ([padroes-1510.md](padroes-1510.md)). Não é uma lista paralela.

## Referências e papel de cada uma

| Referência | Papel | Regra prática |
|---|---|---|
| ISO 9241-210 | Método central | Cada fatia cobre as 4 atividades: <ul><li>contexto de uso por perfil;</li><li>requisitos do usuário;</li><li>solução;</li><li>avaliação com usuário real, quando o proprietário liberar (decisão de 16/10: depois de melhorar os módulos).</li></ul> |
| Heurísticas da NN/g | Critério de projeto e de revisão | Toda tela nova ou alterada passa pelas 10 heurísticas na revisão adversarial da versão (§3.6). Gravidade NN/g ligada ao PRD 22.1: <ul><li>4 → S2 (ou S1 se houver dano S1);</li><li>3 → S2 ou S3;</li><li>2 → S3;</li><li>1 → S4.</li></ul> |
| IBM Carbon (e Fluent 2 pontual) | Referência do design system | Usamos as práticas, não o visual: <ul><li>tabela de dados, filtros e formulários;</li><li>notificações e estados vazios;</li><li>divulgação progressiva, hierarquia e densidade.</li></ul> O Fluent 2 entra quando é melhor (ex.: ⋯ da barra de comandos). |
| Double Diamond | Processo | Descobrir → Definir → Desenvolver → Entregar, dentro do ciclo da fatia (§3.1). |
| Simplicidade operacional | Regra de tela | **TELA-01** (abaixo). |

## TELA-01 · as três perguntas

Toda tela responde, sem rolar:

1. **O que está acontecendo?** O estado em palavras, no topo.
2. **O que exige minha atenção?** O que trava ou atrasa, com quantidade e motivo, onde está o problema (na linha, TAB-06).
3. **Qual ação devo executar agora?** Uma única primária, com verbo (BOT-01/03).

Tela que não responde às três é achado de revisão. A complexidade fica no sistema (cálculo, sugestão, herança de contexto), não com o usuário.

## Indicadores

| Indicador | Meta inicial (a validar com usuários reais) | Situação em 16/10 |
|---|---|---|
| Sucesso na tarefa essencial | ≥ 95 % | Não medido |
| Tempo por tarefa | Abaixo da linha de base e caindo por versão | Não medido |
| Interações por tarefa | Nunca acima da versão anterior no mesmo cenário | **Medido:** <ul><li>planejar talhão: 3 cliques;</li><li>mudar dose: 4 cliques e 1 campo;</li><li>colheita: 12 cliques e 5 campos;</li><li>beneficiamento: 20 toques e 0 campos.</li></ul> |
| Erros por tarefa | ≤ 0,2 | Não medido |
| Aprendizado (2ª execução ÷ 1ª) | ≤ 0,7 | Não medido |
| Satisfação (SUS) | ≥ 80 | Não medido |
| Acessibilidade WCAG 2.2 AA | 0 violação séria | Parcial (contraste, foco, alvo de 44 px) |
| Desempenho percebido (p75) | INP ≤ 200 ms; LCP ≤ 2,5 s | Não medido (software real) |

## O que nunca se troca por menos cliques

- Aprovação agronômica individual de cada O.S. (pré-autorização recusada em 16/10).
- Autoridade do servidor, idempotência e rastreabilidade.
- Travas de receituário, carência e registro.
- Segurança e dados reais fora do protótipo.
