# EX-56 · Varredura final: situação do portão (Claude, 18/10/2026; atualizado em 19/10 com a v144)

Prompt: `prompt-safrion-varredura-final.md` (sha256 `6c8b788e…`). O EX-56 é o último item do protótipo e só começa quando o checkpoint (issue #1) mostrar três coisas ao mesmo tempo:
- todos os outros EX com decisão final;
- os adotados implantados, revisados e aceitos;
- uma candidata completa identificada.

**Em 19/10 o portão continua fechado.** O proprietário decidiu terminar o protótipo com as frentes grandes, sem corte de escopo; elas entram antes da varredura. Pelo prompt, não se começa nem em paralelo. Fica registrado o que falta, quem resolve e o gatilho de retomada. O registro oficial é do Codex, no checkpoint.

## O que falta (conferido no repositório e no PR #47, 19/10)

| Item | Situação | Quem resolve |
|---|---|---|
| EX-01 a EX-42 | Validação do Claude em `V71/ex-validacao-claude/`. Falta a tabela consolidada com a decisão final de cada item e a implantação das ondas que ainda não entraram | Codex registra; Claude e Codex implantam |
| EX-43 Raio-X do alvo | RX-0 fechado (C2.2 aceito em 6253895754). RX-1, RX-2, a marcação do RT e o risco ainda não começaram | Codex (RX) e Claude (revisão) |
| EX-44 a EX-51 | Desenhos confrontados; implantação parcial (ex.: DRILL-RECOLHIDO, Mapa sem Lista, KMZ, EX-50 LO-02det) | Codex registra o que falta por item |
| EX-50: portal do parceiro, onboarding e backoffice | Decidido em 18/10: delegado aos agentes (`decisoes-proprietario-1810.md`) | Claude e Codex; o Codex registra |
| EX-52 | Classificações independentes; falta a implantação | Codex |
| EX-53 | Publicado em partes da v139 à v144 (metas, alavancas, cumprimento de preventiva, backlog com semanas equivalentes). Falta a reincidência | Claude |
| EX-54 Frentes | F1 publicada na v135 e aprovação em lote no grupo na v136. F2 em diante pendentes, com pacote Gemini (calda contínua, lavagem, clima) | Claude implanta; Codex revisa |
| EX-55 Mapa nas telas | F1 publicada na v137. Falta a F2 (mapa do Planejar safra e das Frentes no mesmo componente) | Claude e Codex |
| EX-57 Perenes | F0a e F0b (regra única de datas) integradas, sem tela. Faltam os consumidores (Codex) e as F1–F4, que esperam o RT validar os parâmetros por cultura | Codex; RT |
| Frentes grandes do Claude | MAPA-FROTA F1, PA-OPER F1, MAPA-MIP-PROD F1, SOLO-GEO F1, COLH-APONT | Claude implanta; Codex revisa |
| Frentes grandes do Codex | RX-1/RX-2, MIP-NC/ORC-2, Resolver em 1 clique | Codex implanta; Claude revisa |
| Decisões do proprietário (§5) | Respondidas em 18/10 (`decisoes-proprietario-1810.md`), inclusive a aprovação em lote. Continua aberta só a validação agronômica pelo RT | RT |
| Candidata completa e operável | Ainda não existe: a v144 é a ponta publicada, e as frentes grandes acima estão abertas | Claude (composição) |

## Pendências que dependem de gente real (avisar já, porque levam tempo)

- **Critério 5 de encerramento:** teste moderado com 3 a 5 pessoas por persona nas jornadas principais. Exige convidar pessoas reais (agrônoma, PCP, operador, almoxarife, compras, gestor). É com o proprietário; os agentes preparam o roteiro e a medida.
- **Critério 8:** aceite explícito do proprietário sobre a candidata final.
- **RT (Jéssica e Altair, indicados pelo proprietário em 19/10; PR #47, 6265116161):** validam os parâmetros por cultura do EX-57 e as validações agronômicas. Não se presume disponibilidade nem acesso ao software.
- **Pessoas do teste:** os agentes preparam o roteiro; o proprietário indica as pessoas depois. Nenhum convite ou contato foi autorizado.

## O que já se pode adiantar sem furar o portão

Ferramenta de medida, não varredura: o robô de jornadas v6 (Etapa 1) e o inventário comum podem ser preparados como instrumento, sem rodar a auditoria. Fica para quando houver frente livre (§3.6, teto de 3 frentes).

## Gatilho de retomada

O checkpoint do Codex mostrar todos os EX (exceto o 56) com decisão final e os adotados aceitos, mais a candidata identificada (versão, URL, fontes, diff, provas). Nesse momento começa a Etapa 1 (inventário comum), com Codex, Claude e Gemini reais na mesma candidata.
