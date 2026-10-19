# LEVE · travas do protótipo, uma por uma (19/10/2026)

**Pedido do proprietário (19/10):** "Não quero um sistema travado e burocrático, quero leve e fluido."
**Regra aplicada:** AGENTS §4. Trava só onde protege algo concreto: resultado técnico da lavoura, dinheiro e estoque, lei, segurança da informação, integridade do fato registrado ou decisão explícita do proprietário. O resto vira aviso, padrão preenchido ou sai.

**Fonte:** inventário estático das telas de `tools/prototipo/v37/gen37` (sem `_render`, testes e aposentados), feito por subagente do Claude em 19/10 sobre a árvore `claude/v44-pa-oper-f1`. Cada linha cita arquivo e linha daquela árvore. É levantamento de código, não teste em navegador: cada item aplicado ganha teste e contraprova na própria fatia.

**Dono do arquivo** segue o acordo de 19/10 (PR #47, 6257468542 e 6257501950): o Codex é dono de `safra.js`, `suprimentos.py`, `cal01.js`, `ocupacao.*` e `necAgg`; nos demais, quem precisa escreve o patch no próprio PR e o dono revisa.

## Já aplicado (PA-OPER, PR #142)
| Trava | Decisão | Dano que continua protegido |
|---|---|---|
| Ciclo submeter → em revisão → devolver nos planos | **Saiu.** Quem tem o papel publica; quem não tem deixa o rascunho guardado | Bula (⛔ impede publicar) e papel de agrônomo para publicar |
| Alvo em branco deixava a operação "Pendente" | **Saiu.** Sem alvo, a bula é conferida pelo uso mais permissivo | Bula; a O.S. segue com aprovação individual |
| "Confirme (Enter) a dose" e o 2º clique em "Salvar e publicar" (R1) | **Saiu.** A dose aberta entra no mesmo clique e o aviso diz qual | Dose inválida não publica; dose acima da bula fica no rascunho com ⛔ |

## LEVE-1 · Claude aplica agora (arquivos sem dono exclusivo do Codex)
| # | Tela | Hoje | Passa a | Dano avaliado |
|---|---|---|---|---|
| 1 | O.S. e Mapa · Iniciar e Enviar para conferência | 2º bloco "Confirmar …" | grava no clique, com recibo | nenhum: o comando já valida; o recibo registra |
| 2 | App · Fechar turno (MB-03, MB-10) | "Informe as horas trabalhadas." | horas = agora − início − pausas, editável | nenhum |
| 3 | O.S. · Nova ordem | "Informe o início da janela." | data do gatilho do plano, ou hoje | nenhum |
| 4 | Manutenção · Liberar OM | "Falta: executante" / "tempo previsto" | sugestão do executante e tempo do serviço, editáveis | nenhum |
| 5 | Manutenção · Vincular ativos ao plano | "Escolha como contar…" | padrão "Contar de agora" (selo "Marco estimado") | nenhum |
| 6 | Cadastros · Produtos | "Informe a data do preço." | hoje | nenhum |
| 7 | Comercial · Encerrar saldo de venda | recusado com carga programada | o encerramento cancela a carga programada, no mesmo comando | nenhum: a carga não saiu |
| 8 | Gestão e Campo · botões "Prévia" sem efeito | botão que não faz nada | saem | nenhum |
| 9 | Motivo obrigatório sem dano (Desvincular, Achado, Cancelar OM, Checklist, reordenar fila, encerrar/cancelar carga, Irrigação: divergência e fertirrigação, AL de Configurações) | campo obrigatório | opcional; quem e quando continuam gravados | nenhum além do registro |
| 10 | Cadastros · Fazendas: diferença de área e soma dos talhões | impede salvar | aviso | nenhum |
| 11 | Irrigação · Terminar sem leitura do volume | impede terminar | termina "Sem leitura"; o balanço só credita o medido | nenhum: o crédito segue só com leitura |

## Proposta ao Codex (arquivo ou decisão dele)
| Tela | Proposta | Por quê |
|---|---|---|
| Suprimentos · Políticas (SU-02) | o gestor salva e já vale, com versão; Aprovar e Publicar numa coisa só; justificativa opcional | a política só sugere reposição |
| Suprimentos · Inventário, Perda, Destinação | abaixo do limite em R$ da AL-09, aplica direto com registro; acima, vai ao gestor ao salvar, sem "Submeter"; evidência opcional | alçada mantida onde há dinheiro |
| Suprimentos · "Prévia de transferência/estorno" | sai até existir o comando | botão sem efeito |
| Planejar safra (`safra.js`) | trocar de ação salva o formulário válido; inválido vira rascunho | planejar não reserva |
| O.S. · Encerrar com conferência diária pendente (CONTROLE-02) | só caso "Não conforme" aberto segura | a fila não altera área, horas nem consumo |
| O.S. · Enviar com saldo de área | a dispensa abre no mesmo passo, área preenchida, motivo em opções | a Direção acima de 20 % (AL-05) fica |
| App · Confirmar recebimento + Iniciar turno | um toque só; o servidor grava a custódia | a custódia continua registrada |
| Compras · justificativa da escolha que não é a de menor custo | aviso "+R$ X" e justificativa opcional; sem 2º clique na aprovação | a alçada que aprova o valor fica |
| Metas e Capacidade | motivo opcional | quem e quando já ficam |
| Beneficiamento · balanço dentro da faixa | enviar já confere e fecha | fora da faixa, justificativa e alçada ficam |
| Previsão de colheita | salvar publica, com histórico; autorização só abaixo do prometido | dinheiro só se reduzir volume prometido |

## Fica como está (com o dano)
- **Lei e resultado técnico:** bula na versão do plano; receituário divergente; carência ao iniciar colheita; aprovação agronômica individual da O.S. e o CMD-06 separado (PRD 41 e 73.9); agrônomo só com CREA.
- **Dinheiro e estoque:** saldo e lote ao liberar; NF na entrada; laudo para tirar da quarentena; alçadas acima do limite; aprovação desatualizada reenvia; recontagem cega e quem tinha a custódia não confirma o próprio recebimento; **contagem do recebimento sem pré-preencher com a quantidade da NF** (o inventário propunha preencher; recusado: com o número da NF já no campo, a conferência deixa de achar falta).
- **Fato registrado:** apontamento aguardando sinal ou em duplicidade; divergência de dose em revisão técnica; leitura de horímetro menor que a anterior; ativo bloqueado pela Manutenção; "pode operar?" no registro de falha.
- **Segurança:** ninguém tira os próprios papéis nem amplia o próprio poder sem 2º aprovador; fechamento contábil travado por conciliação.
- **Confirmação mantida de propósito:** Aprovar, Liberar e Encerrar a O.S. (reserva de estoque, ato agronômico e encerramento sem volta).
