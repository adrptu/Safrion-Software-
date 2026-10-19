# EX-56 · Varredura final: situação do portão (Claude, 18/10/2026)

Prompt: `prompt-safrion-varredura-final.md` (sha256 `6c8b788e…`). O EX-56 é o último item do protótipo e só começa quando o checkpoint (issue #1) mostrar três coisas ao mesmo tempo:
- todos os outros EX com decisão final;
- os adotados implantados, revisados e aceitos;
- uma candidata completa identificada.

**Hoje o portão está fechado.** Pelo prompt, não se começa nem em paralelo. Fica registrado o que falta, quem resolve e o gatilho de retomada. O registro oficial é do Codex, no checkpoint.

## O que falta (conferido no repositório e no PR #47, 18/10)

| Item | Situação | Quem resolve |
|---|---|---|
| EX-01 a EX-42 | Validação do Claude em `V71/ex-validacao-claude/`. Falta a tabela consolidada com a decisão final de cada item e a implantação das ondas que ainda não entraram | Codex registra; Claude e Codex implantam |
| EX-43 Raio-X do alvo | RX-0 em fechamento (C2.2 aceito em 6253895754). RX-1, RX-2, a marcação do RT e o risco ainda não começaram | Codex (RX) e Claude (revisão) |
| EX-44 a EX-51 | Desenhos confrontados; implantação parcial (ex.: DRILL-RECOLHIDO, Mapa sem Lista, KMZ, EX-50 LO-02det) | Codex registra o que falta por item |
| EX-50: portal do parceiro, onboarding e backoffice | Decisão do proprietário (§5 do prompt de excelência) | Proprietário |
| EX-52 e EX-53 | Classificação independente pedida ao Codex. A do Claude ainda não existia quando esta linha dizia "lacradas"; correção de 19/10 (6257310093): o Claude escreve e lacra a sua antes de ler a do Codex | Claude e Codex, depois confronto |
| EX-54 Frentes | F1 em bateria na v135. F2 em diante pendentes, com pacote Gemini (calda contínua, lavagem, clima) | Claude implanta; Codex revisa |
| EX-55 Mapa nas telas | Desenho aceito (§6). F1 em implantação dividida: Codex `mapa_camadas.js`, Claude `mapa_emb.js` e adaptadores | Claude e Codex |
| EX-57 Perenes | Novo. Validação independente, Gemini real obrigatório e RT valida os parâmetros por cultura antes do código | Claude e Codex; Gemini; RT |
| Decisões do proprietário (§5) | Abertas: EX-32 (confirmar), irrigação só com água, EX-10 tolerância, clima (alerta × bloqueio), alçadas por valor, automações com IA, validações agronômicas com o RT | Proprietário e RT |
| Candidata completa e operável | Ainda não existe: v135 em bateria; EX-55 F1 e EX-57 abertos | Claude (composição) |

## Pendências que dependem de gente real (avisar já, porque levam tempo)

- **Critério 5 de encerramento:** teste moderado com 3 a 5 pessoas por persona nas jornadas principais. Exige convidar pessoas reais (agrônoma, PCP, operador, almoxarife, compras, gestor). É com o proprietário; os agentes preparam o roteiro e a medida.
- **Critério 8:** aceite explícito do proprietário sobre a candidata final.
- **RT (Ana):** valida os parâmetros por cultura do EX-57 e as validações agronômicas do §5.

## O que já se pode adiantar sem furar o portão

Ferramenta de medida, não varredura: o robô de jornadas v6 (Etapa 1) e o inventário comum podem ser preparados como instrumento, sem rodar a auditoria. Fica para quando a v135 estiver publicada e houver frente livre (§3.6, teto de 3 frentes).

## Gatilho de retomada

O checkpoint do Codex mostrar todos os EX (exceto o 56) com decisão final e os adotados aceitos, mais a candidata identificada (versão, URL, fontes, diff, provas). Nesse momento começa a Etapa 1 (inventário comum), com Codex, Claude e Gemini reais na mesma candidata.
