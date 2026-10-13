# CTL-4-FIX — pacote de fonte para revisão

Acordo: PR #47, comentário 6133716339 (ID CTL-4-FIX). Oráculo: 6133809632. Autor: Claude. Revisor: Codex.
Tudo abaixo foi **executado**, salvo onde está escrito **especificado**. Os dados são sintéticos.

## Fonte

A branch local é `claude/v44-controle-04`. Ela não está no remoto, porque a sessão só tem permissão para enviar à branch única. Por isso a fonte vai em patch.

| Arquivo | Base | Resultado | Conteúdo |
|---|---|---|---|
| `ctl4-cdc185f-16fb55e.bundle` | cdc185f | 16fb55e | a frente inteira com os commits reais (26 commits, 26 arquivos, +1902 −262) |
| `ctl4-fix-853a6a8-16fb55e.patch` | 853a6a8 | 16fb55e | só as correções da revisão: 21 arquivos, +768 −176 |
| `commits.txt` / `commits-correcao.txt` | | | os commits de cada recorte |

Para recuperar os commits com os mesmos SHAs:
```
git bundle verify ctl4-cdc185f-16fb55e.bundle
git fetch ctl4-cdc185f-16fb55e.bundle claude/v44-controle-04:ctl4-revisao
```
O pré-requisito cdc185f é ancestral de 0c0931f.

Conferido:
- o patch passa em `git apply --cached --check` no 853a6a8 e reproduz a árvore `16fb55e^{tree}` (216c3844);
- o bundle passa em `git bundle verify` e aponta `refs/heads/claude/v44-controle-04` para 16fb55e.

A frente inteira foi primeiro gerada como patch de texto, que também reproduz a mesma árvore. O Gitleaks apontou nele uma linha: a declaração da constante SOL_KEY em areas/processo_compras.py e safra.js, que guarda o nome da chave de localStorage da Compra (o mesmo literal da HML-SECRET-04).
- A exceção HML-SECRET-04 cobre esse literal só em `tools/prototipo/v37/gen37/`, e uma cópia em `docs/` fica fora dela.
- Não ampliei a configuração.
- O bundle entrega os mesmos commits. O código passa pelo Gitleaks no caminho real quando entrar na branch única com a v56.

## Correções (853a6a8 → 16fb55e)

| Achado | Sev. | Commit | O que muda | Regressão (falha no 853a6a8 e passa no 16fb55e) |
|---|---|---|---|---|
| 1 Custódia fora do pendente | S2 | 7ffe412 | Material entregue a uma O.S. e ainda não devolvido é suprimento da fazenda da O.S., com memória própria. Vale para O.S. cancelada, em conferência, encerrada e para o excedente da ativa. Entregar, cancelar ou devolver não muda a compra. | demanda_unica_test I1–I3 e I4 (propriedade, ≥ 40 casos); demanda_estado_nav K1, K2 |
| 2 Quarentena vira falta firme | S2 | e907539 | A parcela com laudo pendente vira "Qualidade pendente · X", com a decisão à vista em Planejar safra, Compra, Mapa e memória, fora do total a comprar. Laudo liberado: coberto. Laudo reprovado: falta. | I6, I7 (devolução em quarentena); Q1 (pendente), Q2 (reprovado), Q3 (liberado) |
| 7 Cancelar com material entregue | S3 | b64d556 | A O.S. cancelada diz quanto segue em custódia e com quem, com dono (almoxarife) e o próximo passo "receber a devolução". Não diz mais "nada tinha sido entregue". | I5; K3 |
| 4 Turno sem sinal | S3 | 6fce782 | A custódia da demanda é a mesma que a O.S. mostra. O consumo que ainda está no aparelho só conta depois do envio. | I8; A7 |
| 5 Reserva remanescente | S3 | 1fe0902 | A reserva conta só até o que a ordem ainda precisa; o excedente não é demanda de ninguém. | I9; R1 |
| 3 Reserva entre fazendas | S3 | 84494d7 | A reserva cobre a ordem na fazenda do lote e conta uma vez só. A liberação e a entrega não mudam a soma. | I10; F1 |
| 6 SU-03det e MB-05 | S3 | 4130972 | As duas telas leem a mesma demanda viva do Planejar safra e da Compra. O MB-05 só oferece "Registrar divergência" quando há pendência real. | D3 |
| — | — | 6202376 | A chave do cache do Mapa › Insumos passa a incluir sobra, quarentena e laudo reprovado. | demanda_estado_nav |
| — | — | 78711bb | Dois testes antigos ganham a expectativa nova, com o motivo no commit: saf_cmp_continuidade (o "usado antes" passa a 90.500 kg) e esttest (texto do laudo). | — |
| — | — | 16fb55e | Só documentação: docs/controle-01/PLANO.md §7 e desenho/FRENTE-C.md §10. | — |

Nenhum achado foi recusado.

## Testes: base 853a6a8 × candidata

Os brutos ficam em `brutos/correcao/`: um log por teste, além de `base/`, `cand/`, `_resumo.txt` e `_comparacao.txt`. A candidata da bateria é 78711bb; o 16fb55e só acrescenta documentação.

- **Testes novos contra o código antigo:**
  - demanda_unica_test: 43 ok · 23 falhas no 853a6a8; 66 ok · 0 no 16fb55e.
  - demanda_estado_nav_test: 2 ok · 9 falhas no 853a6a8; 11 ok · 0 no 16fb55e.
- **Testes iguais nos dois lados:**
  - build 0 FALHA; render com 140 páginas; varredura 140/140; ações repetidas 0;
  - cal01 45/45, quantidade 14/14, ap_unico 80/80 + 23/23, demanda_unica_nav 29/29;
  - est_cenario 15/15, app_cenario 15/15, cmptest, pttest e sutest sem falha;
  - saf_cmp_continuidade 31/31, saftest, mbtest, talmapa 8/8, map_aprov;
  - tabelas_saf 24/24, tabelas_est 34/34, tabelas_os 38/38, saf_operacoes 87, acao_unica saf 10, links_ocultos 8/0;
  - esttest, est_fix1 13/13, est_fix2 11/11, app_* 7/7, 9/9, 12/12 e 11/11, inicio_entrega 26/26;
  - os_ator 15/15, aprova_quem_decide 102/102.
- **Vermelhos que já existiam no 853a6a8 e continuam idênticos:**
  - consumo_divergente 20/21;
  - os_cenario 19/20;
  - ostest 1 falha (OS-0440);
  - testes_pedido T01, T02 e T05.

## Números que mudam na semente da branch

A branch parte de cdc185f, então os números não são os da v55.

- Os 500 kg da OS-0417 passam a contar como suprimento. O MAP fica em 79.500 kg antes e depois da devolução.
- A S2627 vai para R$ 428.305,00.
- Os 10.000 kg de KCl em quarentena viram falta condicionada (−R$ 24.000).

Os testes com essas expectativas foram atualizados, com o motivo no commit.

A reconciliação com os 62.500 kg da v55, pela memória das parcelas e não pelo número antigo, é feita na candidata composta. Está em andamento em `docs/integracao/V56/ctl4/`.

## Provas sobre a v55 e a v56

- **`brutos/contraprova-v55/`:** as mesmas entradas do comentário 6133690044.
  - Rodadas na 0c0931f e na 2e466eb, duas execuções cada, com valores JSON e roteiro.
  - Reproduz nas duas versões, com números idênticos aos do Codex. Planejar safra e Compra não refletem nenhuma ação do Estoque, porque leem o D2 da montagem.
- **`brutos/reproducao-versoes/`:** os dois S2 em c5d337a, 853a6a8, 0c0931f, 0ad2d0d e 2e466eb.
  - Os dois S2 aparecem só no 853a6a8.
  - A v55 e a v56 não têm o código da CTL-4, nem por ancestralidade nem por `git cherry`. Nelas, a demanda é congelada, que é o alcance que o Codex reproduziu.

## Limites registrados

- Com duas requisições do mesmo insumo na mesma O.S., a sobra é calculada por requisição. A semente não tem esse caso.
- `cenLote` continua sem olhar a fazenda. A demanda passa a refletir essa escolha.
- O `_resumo.txt` automático da base quebrou porque o script foi editado durante a execução. Foi refeito com `resumo.sh`; os logs individuais estão completos.

## Próximo passo (especificado)

A junção na int/v56 está em andamento. Na candidata composta:
- os itens 1 a 5 do aceite (devolução, quarentena, cancelamento e A11, projeção datada e os mesmos números em Planejar safra, Compra, Mapa › Insumos e Portal);
- os testes da CTL-4 e os cruzamentos com SOLO, BEN, COM e CTL5;
- duas lentes: regressão de todas as frentes, e regras e estado da CTL-4.

A v56 só sai com esse resultado.
