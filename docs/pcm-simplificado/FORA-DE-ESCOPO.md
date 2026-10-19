# PCM simplificado v2 · Fora de escopo

Complemento de `ESPECIFICACAO.md` (§10). Rótulo: especificado.

- Cada item diz por que fica fora e quando volta.
- O que já está fora na PCMS v2 (`docs/pcm-suprimentos/FORA-DE-ESCOPO.md`) continua fora e não se repete aqui.
- A v2 acrescenta os itens marcados (v2) e ajusta o desbloqueio sem OM.

## 1. Mudaria regra de domínio (o pedido é de tela)

| Item | Por que fica fora | Volta quando |
|---|---|---|
| Geração automática da preventiva na antecedência (desenho "papel") | Tira do PCM a decisão de quando a OM nasce (PCMS §2.2 passo 1). Muda o seed, o C2 e o roteiro do dono. Escrita disparada na leitura, com duas abas abertas, pode duplicar a OM (S2) | O dono pedir, com política expressa e idempotência no servidor |
| (v2) Janela gerada já sem conflito | A janela padrão (DM:363) é a base da PCMS C2 ("precisa 24/09"); o conflito aparece em selo e "Mover janela" resolve (D-08, D-38) | A PCMS C2 ser revista com a nova janela |
| Aprovar várias OMs num toque | Aprovação é individual (PCMS-M05; CMD-42) | O dono definir uma política de lote com alçada |
| Gerar preventiva ainda em dia, para aproveitar outra parada | Não há regra de antecipação (PRD CAL-06); hoje o sistema recusa (DM:358) | O dono definir a regra de antecipação por plano |
| Desfazer **bloqueio** registrado por engano sem OM | Liberar o ativo exige serviço e teste válidos (CMD-19 l.2790); exceção sem regra seria risco S1. A **restrição** já tem saída: "Encerrar restrição", com motivo e evidência (D-34; PRD l.7720) | O Codex propor a exceção com dano nomeado e o dono aceitar |
| Faixa de referência por tarefa de Medição (Conforme derivado) | Os planos do seed não têm faixa; inventar valores seria referência sem fonte (PRD 54.2 l.8373) | Plano com faixa de fonte técnica |

## 2. Dado fixo ou não calculável

| Item | Por que fica fora | Volta quando |
|---|---|---|
| Pareto de não conformidades (M:252-260) | Dado fixo | Bloco 7: KPI-PCM-07 e KPI-PCM-11 derivados no GE-06, por componente (D-45) |
| Utilização por grupo e "Uso 30 d" (M:124-125, 148-158) | Dado fixo | Horas trabalhadas lidas dos apontamentos (CTL-2) por ativo |
| Agenda e Elegível do MA-01 (M:122-123, 159-170) | Fixos; ocupação e elegibilidade são da O.S. › Recursos | Já existem na O.S. (AL); o detalhe do ativo só lê |
| "Tanque Sede 38 %" e consumo fixo (M:695-696, 685-694) | Fixos | Bloco 6: diesel como lote no Estoque. O consumo vem de `c.abast` já no S2 |
| Disponibilidade 30 d, MTBF e MTTR com número | Sem calendário nem histórico de falhas no seed; aparecem "não calculável" / "não estimável" (PRD 55.3) | Bloco 7, com histórico de falhas e calendário |
| (v2) Custo de manutenção por hora operada (KPI-PCM-10) | Não há horas operadas por ativo; aparece "não calculável" | Horas por ativo lidas dos apontamentos (CTL-2) |
| Semanas do backlog (KPI-PCM-08) e capacidade da oficina | Não há capacidade semanal (P10 da PCMS) | O dono definir a P10 |

## 3. Depende de outro bloco ou frente

| Item | Por que fica fora | Volta quando |
|---|---|---|
| "Incluir peça" na OM (corretiva com peças) | O 1b reescreve peças como lote; incluir antes seria retrabalho (D-29) | PCMS Bloco 2 (M20) |
| Remanejar reserva entre OMs | Regra do Bloco 2 (PCMS-M26) | PCMS Bloco 2 |
| Impedimento derivado nas O.S. (Falta máquina pelo bloqueio); agenda como estado | PCMS-A05. Até lá, AL é dado da semana (D-38) | PCMS Bloco 2 |
| Serviço de terceiro na OM | PCMS Bloco 3 | PCMS Bloco 3 |
| Razão de abastecimentos no Estoque › Movimentos | O diesel ainda não é lote | PCMS Bloco 6; então o modo Abastecimentos pode sair (D-15) |
| Papel e permissão reais | Ver como é simulação (D-33) | Software real: login e validação no servidor (CF-02) |
| (v2) Rui no Ver como | Até o 1b/1c, os passos do almoxarife são pontes simuladas com Otávio (D-22) | 1b, quando sobras e entregas passam ao Estoque |
| (v2) Executar OM de quem não está no Ver como (João, concessionária), ou apontar por outra pessoa | O Ver como tem 3 papéis; a regra é testada em node (`ma_regras_test`) | Papéis reais (CF-02) ou pedido do dono |
| Gantt ou calendário visual da oficina | "Esta semana", agrupada por dia, cobre a semana. Sobreposição visual sem capacidade seria enganosa | P10 definida e pedido do dono |

## 4. Sem pedido, sem dado ou com custo

| Item | Por que fica fora | Volta quando |
|---|---|---|
| Hierarquia de planos e plano sazonal (IBM Maximo) | Não há caso no seed | Caso real ou pedido do dono |
| Lembrete por e-mail, SMS ou WhatsApp (John Deere, Aegro) | Canal real tem custo e exige autorização (AGENTS §2) | O dono autorizar o canal |
| Telemetria de horímetro | Não há integração | Integração autorizada |
| Desvincular ativo de plano | Não existe hoje e não foi pedido | Primeiro caso de ativo vendido ou trocado de plano |
| Mudar a casca (menu ☰ a ≤640 px) | Muda todas as telas; é a mesma decisão da SUP | Frente própria de casca |
| Calibração como serviço de plano | É aferição usada por Irrigação, Colheita e app (D-16) | O dono pedir que a calibração gere OM |
| (v2) Janela por hora dentro do dia | A janela é o dia; o conflito compara horas livres com o tempo previsto (D-38) | Programação por hora pedida pelo dono |
| Reescrita do PRD (MA-01..05 como famílias) | O autor é o Codex, por PR no repositório Safrion-Software- | Proposta à v3.10 (DECISOES §5) |
