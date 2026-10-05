# PCM × Suprimentos de manutenção · v2 · Fora de escopo

Complemento de `ESPECIFICACAO.md` (§13 do v1). Rótulo: especificado. Cada item diz por que fica fora e quando volta. Os Blocos 2 a 7 não estão aqui: estão no backlog (ESPECIFICACAO.md §11.5 e Anexos). Aqui fica o que não entra em bloco nenhum, ou entra só depois de uma decisão.

## 1. Depende de decisão do proprietário ou de dado real

| Item | Por que fica fora | Volta quando |
|---|---|---|
| Reserva firme desde a aprovação e alocação automática do que chega por "criticidade, depois data" (achado A02) | A DEC-2609-13 (PRD l.12227) fixa a reserva na liberação. A alocação automática seria regra sem dono nem default visível | O dono responder a D5 (DECISOES.md §4) |
| Pedido automático por mínimo/máximo (achado A07) | Sem política expressa do dono. O PRD só admite automação de pedido com política expressa, limites e fornecedor/condições homologados (65.5 l.9202). Até lá, a sugestão de um toque abre a SC | O dono publicar a política P8 (DECISOES.md §3) |
| Delegar ao responsável de manutenção a decisão de conflito com O.S. de produção (achado A08) | A 47.8 (l.7820) dá a decisão à gerência dentro da alçada. Delegar não é default nem parâmetro | Proposta à v3.10 com o dano nomeado (plantio sem trator na janela) e decisão do dono |
| Pneus por posição, recapagem e km (47.1 l.7704: "quando controlados") | Decisão de escopo | O dono decidir controlar pneus (D3) |
| Consignação de peças caras (65.2) | Sem fornecedor nem decisão | Fornecedor real oferecer e o dono aprovar |
| Teto e autorizador da compra de balcão | Dado da fazenda (D1). O fato já é registrável com o default P4 (M25) | D1 respondida; vira o teto da P4 |
| Capacidade semanal por especialidade (semanas equivalentes do KPI-PCM-08) | Não há capacidade disponível cadastrada. O turno da equipe Oficina (`dados_cad.py:74`) não é capacidade disponível; inventar o número daria indicador sem lastro | O dono definir a P10, ou o Bloco 4 trazer capacidade com fonte |

## 2. Software real, legal ou fiscal

| Item | Por que fica fora | Volta quando |
|---|---|---|
| Integração com o ERP (escritor oficial de pedido, estoque e custo; 66.2 l.9249-9251) | Software real; exige autorização do dono (AGENTS §2) | Etapa de software real autorizada |
| Normas legais externas e obrigações fiscais da NF de serviço | Ficam com o contador e o ERP; nenhuma norma é citada | Software real, com o contador |
| Telemetria de horímetro | Sem integração | Integração autorizada |

## 3. Sem dado, sem pedido ou sem dono

| Item | Por que fica fora | Volta quando |
|---|---|---|
| Custódia de ferramentas e EPIs (SU-02 "EPIs") | Não foi pedida | O dono pedir |
| Pool de componentes rotativos | Sem dado real | Depois do Bloco 5, com histórico real |
| Medição de serviço item a item | O Bloco 3 mede o valor total | Contrato real com planilha de medição |
| Ressarcimento financeiro de garantia | O GE-04 não tem nota de crédito | Bloco 5 entregue e GE-04 com crédito |

## 4. Fora do Bloco 1 por desenho

| Item | Por que fica fora | Volta quando |
|---|---|---|
| Registro da compra de balcão pelo mecânico no app (foto da NF) | No Bloco 1 quem registra é o almoxarife (M25) | Bloco 6 (MB-05/MB-09 no cenário) |
| Confirmação da entrega pelo mecânico no app | O mecânico não tem app até o Bloco 6; a entrega de OM grava `confirmado:'balcao'` (M14) | Bloco 6 |
| Dividir uma linha de REQ entre lotes | O Bloco 1 segue o `cenLiberar` da O.S. (`cenario.js:55-56`): uma linha, um lote. O seed não tem peça com livre dividido | Primeiro caso real ou sintético com livre dividido; vale para O.S. e OM juntas |
| "Apta para uso" calculada no recebimento (conferida − quarentena) | Muda o formulário do EST para todos os fluxos, não só a manutenção | Caso de produtividade próprio do EST (AGENTS §3.3), com a medição de toques |
| Pedidos novos de **insumos** aparecerem no EST | Já falha hoje (`processo_estoque.py:209-211` só lê `E2.pedidos`), mas não é manutenção | Tarefa própria depois do 1c, reaproveitando `cenGravarPedidos` |
| Previsão versionada dos PCs antigos (`CD.pedidos`, PC-088..095) | O 1c versiona só os PC-2xx (`prevs`); os antigos ficam no `pcx` | Quando o KPI-SUP-05 cobrir compras de insumo |
| Rótulo da etapa 1 da CMP "Abra a demanda (safra ou manutenção)" | A v3.9 contrata "Escolha a safra" (PRD l.10367). No Bloco 1 a origem distingue as linhas | Aceite da v3.10 (DECISOES.md §6, item 3) |
| Série única para SOL e SC | O SOL é indexado e numerado pela safra (`safra.js:641, 1013-1014`); a manutenção não tem safra (PRD l.4493) | Se o Planejar safra mudar a numeração |
| Atalhos de insumo com o nome antigo ("Abrir Compra de insumos ›", `safra.js:840`; `processo_safra.py:251`; `inicio.py:897, 903`; `planejamento.py:253`) | São ações no contexto de insumos; o destino continua certo | Se o 1c preferir alinhar o texto (sem efeito em teste, salvo `acao_unica_test.py:89, 138-139`, `saf_cmp_continuidade_test.py:78, 81, 117, 175`, `testes_pedido.py:83-85`, `saftest.py:68`) |
| Telas SU-01 a SU-09 (ocultas; citam uma OM-0234 que diverge da real: `suprimentos.py:265-267, 495-499, 564, 703-704`) | Não são fonte de dados; reativá-las cria segunda verdade | O dono pedir as telas de volta |
| Renomear Rui e Paula no cadastro bruto (`dados_cad.py:84-85`) | A tela CD-04 já mostra Rui como almoxarife (`cad_ativos_pessoas.py:34-37`) | O dono pedir |
| Parâmetro "aptidão com custo pendente" (RF-AST-005 l.2570) | Sem dano concreto a proteger: a conciliação já trava o Encerrar (PCMS-C07, achado A09) | Codex ou dono pedirem; cobre só pendência que não seja nota em conferência, default "permitida" |
