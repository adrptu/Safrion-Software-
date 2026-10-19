# Decisões do proprietário de 18/10/2026, noite (seção 5 do prompt de excelência)

**Registro:** resposta do proprietário no canal do Claude, em texto, à lista "Depende de você" (seção 5 de `prompt-safrion-excelencia.md`).
- Sessão: https://claude.ai/code/session_01Div8EjesSwVnpSUvYjZ7kh
- Escopo: só texto, sem dado real.

| Pergunta (seção 5) | Resposta literal | Como fica (leitura do Claude; o Codex registra no checkpoint) |
|---|---|---|
| EX-32 · lote de O.S. com produto | "O.S pode ser liberada em lote sim." | **Liberação em lote permitida.** Liberar é o CMD-06 (estoque e reserva, máquina, operador, trava legal) e não é aprovar (AGENTS §4: "Aprovar não libera; liberar é o CMD-06"). A **aprovação agronômica continua individual**, por ser regra fixa (PRD 41 e 73.9; decisão de 16/10 "aprovação em lote: fora"). O lote só leva O.S. já aprovadas uma a uma e devolve o resultado por linha (P23). A O.S. sem aprovação, ou com trava legal, fica fora do lote com o motivo e quem resolve. O EX-32 deixa de remover o lote e passa a garantir essas condições, com teste de regressão |
| Irrigação só com água | "Irrigação com água fora da aprovacao agronomica" | Confirma a DEC-2609-10. Com produto na água (fertirrigação), a aprovação continua exigida |
| EX-10 · turno dentro da tolerância | "turno aceito" | **Aceite automático** do turno dentro da tolerância. O que estiver fora vai para "Aceitar com motivo" ou "Devolver" (conferência por exceção, P39) |
| EX-08 · clima | "clima como alerta" | **Alerta, não bloqueio.** O alerta aparece em "Iniciar turno" e na ficha. A condição real da aplicação fica registrada (D4 do EX-53). Não há exceção a liberar |
| Alçadas por valor | "alçadas por valor ok" | **Adotadas** para perda, crédito a cliente, frete, liberação de lote e pagamento de manutenção. Abaixo da alçada, "Aprovar e emitir pedido" numa ação só. A fatura de oficina sai da alçada de suprimentos |
| Automações com IA | "automação com IA (desligadas somente por hora)" | **Desligadas por ora**, prontas para ligar depois. Continua valendo a regra de ligar só com a estimativa de custo (prompt de excelência §9). A estimativa vai ao proprietário quando a automação estiver pronta |
| EX-50 · portal do parceiro, onboarding e backoffice | "portal do parceiro, onbording e backoffice façam da melhor forma." | **Delegado aos agentes.** O ponto de partida são as respostas de 17/10 (`pedidos-1710/decisoes-proprietario.md`): portal mínimo fora do menu (cotação por convite e XML da NF-e, com login próprio), implantação assistida e backoffice como ferramenta separada. Claude e Codex revisam e o Codex registra |

**Ponto a confirmar com o proprietário:** se "liberada em lote" quis dizer também *aprovar* em lote, isso muda uma regra fixa do PRD (aprovação agronômica individual). Até ele dizer, vale a leitura acima.

## Confirmação do proprietário (18/10/2026, noite): aprovação em lote

**Literal:** "pode aprovar em lote as O.S sim"

**Efeito:** substitui a decisão de 16/10 ("Aprovação em lote: fora, de propósito") e muda a regra fixa "Toda O.S. agrícola tem aprovação agronômica individual" (AGENTS §4; PRD 41 e 73.9). O texto da regra no AGENTS.md e no PRD é atualizado pelo Codex, com esta decisão como fonte. O Claude não edita o AGENTS.md.

**Como fica (desenho do Claude, que o Codex revisa):**
- **Quem aprova:** só quem tem o papel de decisão agronômica (CTL-3) aprova em lote. Os outros perfis veem o botão desligado, com o motivo.
- **Antes de confirmar, uma prévia** com cada O.S.: produto, dose, alvo, talhão e alertas.
- **Travas legais por O.S.** (registro, cultura × alvo, dose de bula, carência, receituário): a O.S. barrada sai do lote com o motivo e quem resolve. **O lote nunca passa por cima de trava.**
- **Um registro de aprovação por O.S.** (CMD-42: quem, quando, versão, chave de idempotência própria) e o resultado por linha (P23). O rastro fica igual ao da aprovação uma a uma.
- **Aprovar não libera:** a liberação (CMD-06) continua sendo a ação seguinte, que também pode ser em lote.
- **EX-32:** muda de "tirar o lote" para "lote com papel, prévia, travas por O.S. e resultado por linha". Os testes de regressão provam que a O.S. com trava não é aprovada no lote e que cada O.S. ganha o seu registro.
