# V69 · Compras de materiais, peças e serviços (CMP-MAT)

Dados sintéticos. Regime leve do protótipo (AGENTS §3.5). Pedido do proprietário (15/10/2026): "Só temos compras de insumos, cadê as compras de materiais, peças, etc?" e "Compra de materiais, peças, etc tem que seguir uma lógica diferente, porque pode atender varias culturas e safras diferentes o que se está comprando."

## Acordo (AGENTS §3.4)

```text
ID / resultado útil / persona: CMP-MAT · comprar peça, material e serviço de manutenção pela mesma tela de Compras, sem safra; a peça de uma OM chega reservada para ela · Ana (gestora, compra), Otávio (PCM, pede), Zé (mecânico, recebe o uso)
Requisitos do PRD e fora do escopo: PRD 4.2/4.3 (master-detail, uma primária, próximo passo com verbo), cap. 74 (BOT/SEL/ETP/VIS, faixa Filtros), §4 AGENTS (trava só onde protege: dinheiro e estoque). Fora: rateio às culturas (só a frase "rateio pelo uso do ativo"), cadastro dos fornecedores de peças no CD-05, itens de manutenção no catálogo e no Estoque geral (1b), cancelamento de requisição, aprovação acima da alçada (só o motivo).
Autor / revisor / integrador: Claude (autor) / Codex (revisor, sem bloquear: §3.5) / quem integra a branch única
Base (commit ou hashes) / arquivos sob responsabilidade: a0db53a · areas/processo_compras.py, dados_compras_mat.py (novo), dados_manutencao.py (manSolicitar, manReceber, manLiberar, ITENS: ponto de pedido), ui37.py (título do item e faixa condicional), visoes_marcas.py (g_mat), compras_materiais_test.py e compras_materiais_unit.js (novos)
Aceite e comando de verificação: (1) Compras tem o seletor "Insumos da safra | Materiais, peças e serviços"; (2) peça de OM: requisição → cotação → pedido → recebimento põe a peça no saldo para a OM, que sai de "Falta peça" e libera (reserva na liberação, DEC-2609-13); (3) item abaixo do ponto de pedido aparece e vira requisição de reposição, que no recebimento entra no estoque; (4) serviço aceito vai como custo de terceiro da OM; (5) nenhuma requisição de material pede safra ou cultura · `env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico python3 -B compras_materiais_test.py` e `python3 -B compras_materiais_unit_test.py` (contraprova na base a0db53a)
Estado / impedimento / próximo passo: implementado e testado (bateria abaixo) · sem impedimento · revisão do Codex na branch e integração na linha publicada
```

## Regras de domínio (decididas pelos agentes, delegação do proprietário)

- **Origem da necessidade**, nunca o plano da safra: (a) OM da Manutenção que precisa de peça ou de serviço de terceiro; (b) reposição do almoxarifado da oficina quando o saldo livre mais o que já está pedido fica abaixo do ponto de pedido do item; (c) requisição avulsa de uma área (oficina, sede, irrigação…), com urgência.
- **Apropriação** por OM, ativo ou centro de custo. A compra não pede safra nem cultura. O custo chega às culturas pelo uso do ativo (horas × custo R$/h): o detalhe diz "rateio pelo uso do ativo"; o rateio não é construído aqui.
- **Mesmas etapas da compra de insumos:** requisição → cotação (só fornecedor homologado do grupo; envio simulado) → pedido (escolha da proposta, justificativa quando não é a de menor custo, alçada da Compra) → recebimento.
- **Recebimento:** peça de OM fica reservada para a OM desde o recebimento (**D5**, decisão do proprietário de 16/10/2026, `decisoes-proprietario-1610.md`; implementada em `d5_reserva_test.py`): não entra no livre e outra ordem não a usa. O recebimento parcial reserva só o que chegou; a mesma chave não reserva de novo; cancelar a OM devolve a reserva ao livre, com registro. A peça que já estava no livre segue reservada na liberação (DEC-2609-13). Reposição entra no estoque livre da oficina; material avulso sem código vai direto ao centro de custo.
- **Coerência com `docs/pcm-suprimentos` (especificado, não implementado):** mesmos grupos (Peças, Lubrificantes, Serviços de manutenção), mesmos fornecedores F08 (Peças e Lubrificantes) e F09 (Peças), mesma série PC-2nn e o mesmo caso da OM-0235 (F09 R$ 4,80 mais barata, chega em 29/09; a OM precisa em 24/09). Esta fatia não faz o recebimento por NF no Estoque nem a compra de balcão (Bloco 1c dessa especificação).
- **Serviço não tem estoque:** o recebimento é o aceite do serviço, que lança o valor do pedido como custo de terceiro da OM (função única de custo da Manutenção).
- **Uma requisição, uma numeração:** SC-nnn é a mesma sequência do "Solicitar compra" da Manutenção; pedidos de manutenção em PC-2nn (os de insumos ficam em PC-1nn).
- **Fornecedores de peças e serviços** são fictícios e declarados no módulo até entrarem no CD-05 (decisão pendente de integração, sem custo).

## Bateria (executado, 15/10/2026)

Montagem: `SAFRION_DADOS=sintetico python3 -W error::SyntaxWarning -B build.py && python3 -B montar_render.py` → 156 páginas. Navegador: `env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico python3 -B <teste>`, até 3 em paralelo. Base de comparação: a0db53a montada à parte.

| Commit | Testes | Resultado |
|---|---|---|
| c78d2bc (final) | `compras_materiais_unit_test` · `compras_materiais_test` | 44/44 · 32/32 |
| c78d2bc | cmptest · componentes · saf_cmp_continuidade · acao_unica · demanda_estado_nav · est_laudo_lote_nav · config · paginas_scan · nav_modulos · botoes_retorno · busca_unica · ma_correcoes_om · ma_unica | 101 OK · 3/3 · 31/31 · 10/10 · 14/14 · 7/7 · 88/88 · 4/4 (148 páginas) · 15/15 · 6/6 · 7/7 · 15/15 · 23/23 |
| c78d2bc | ben_fluxo (sozinho, limite 4.000 s) | 224/224 (1.866 s) |
| c6ea6a6 | ma_regras · ma_atrito · ma_rastreio · ma_planos · matest · ma_app · ma_app_fluxo · painel_modulos · links_ocultos | 150/150 · 13/13 · 58/58 · 18/18 · 40/40 · 36/36 · 24/24 · 87/87 · 16/16 |
| 391c7a2 | Estoque (est_a4_nav, est_cenario, est_fix1/2, est_item_divergente, est_sem_validade, est_validade × 5, esttest, tabelas_est), inteligencia_nav, irr_fluxo, assinatura, map_decisoes, man_limpa, os_cenario, visoes_v23, visoes_v23_codex | todos verdes (visoes_v23 370/370) |

Contraprova (executado): `compras_materiais_test` na base a0db53a → 4/28 ok (só "sem erro de JS" e o "Solicitar compra" da Manutenção, que já existia); `compras_materiais_unit_test` na base → 2/13.

Vermelhos e classificação (cada um comparado com a base a0db53a nas mesmas condições):
- **Iguais à base (anteriores a esta frente):** ds_test 66/69 (D13, D15, E2 na O.S.), demanda_unica_nav 21 ok · 8 falhas, testes_pedido T01/T02/T03/T05/T07, quantidade 13/14 (`areas/custo_dominio.py`), map_aprov 4/5, aprova_quem_decide 102/103, visual_corte 51 achados na candidata e 52 na base (nenhum em CMP ou MA; a diferença é o LO-02det a 390 px, que só a base acusou).
- **Instáveis sob carga:** ds_unit 28/29 com 3 testes em paralelo, 29/29 sozinho (base 29/29); ben_fluxo estoura 1.500 s em paralelo na candidata e na base, e passa sozinho.
- **Corrigido nesta frente:** componentes_test 2/3 no c6ea6a6. A linha do seletor no cabeçalho empurrou a grade, e o toque do teste caiu no link "Abrir Planejar safra". O seletor foi para o começo da faixa da tela (c78d2bc) e o teste voltou a 3/3.

## Decisões em aberto

- **D5 (proprietário):** decidida em 16/10/2026 (a peça fica reservada para a ordem que pediu) e implementada; a chave `RESERVA_NO_RECEBIMENTO` saiu do código.
- **Ponte da Manutenção:** o botão "Solicitar compra (simulado · Compras recebe no 1c)" e o "Registrar recebimento (simulado · papel do Almoxarifado)" seguem na OM. O rótulo e a ponte são da frente PCM (`ma_rastreio` F110). As duas pontas usam a mesma função de recebimento.
- **Cadastro:** F08 a F12 entram no CD-05 quando os itens da oficina entrarem no catálogo. O `visoes_v23_codex_test` conta 20 parceiros.
