# Q5-AMB: nota antiga só baixa a linha única em que cabe (18/10/2026)

| Campo | Valor |
|---|---|
| ID / resultado útil / persona | Q5-AMB. Uma nota antiga, conferida sem unidade ou sem linha, não baixa duas linhas do mesmo pedido. Persona: Ana (gestora), que compra pela falta do Planejar safra |
| Requisitos e fora do escopo | ENG-011 (regra única JS × Python) e ENG-013 (unidade explícita). Fora: conversão de unidade, que não existe sem base |
| Autor / revisor / integrador | Claude (autor do patch Q5 `f5857498` e desta correção) · Codex (revisor; achado em 6249640248) · Claude (integrador da composição) |
| Base | `8dcf39d4` (v131) |
| Arquivos | `cenario.js`, `dados2.py`, `areas/processo_compras.py`, `areas/processo_estoque.py`; testes `c34_test.cjs`, `c34_paridade_test.py` (casos novos), `n1_emission_test.cjs`, `n1_recipe_test.cjs` (recorte pelo nome) |

## 1. Defeito (S2)

O patch Q5 (`f5857498`) deixou a nota sem unidade valer com a unidade do pedido. O Codex mostrou o contraexemplo: no mesmo PC, o item A tem a linha 1 com 100 kg e a linha 2 com 50 L. Uma nota antiga de 20, sem unidade e sem linha, baixava as duas linhas: 80 kg e 30 L. A mesma quantidade saía duas vezes, sem base de conversão. Com a mesma unidade nas duas linhas, a baixa também dobrava.

Dano: a previsão de recebimento fica menor do que é. A demanda mostra uma falta que não existe, e a compra pode sair maior.

## 2. Regra

Uma nota sem unidade ou sem linha só baixa a linha se ela for a única do mesmo PC e item onde a nota cabe.
- **Uma linha possível:** baixa essa linha. O caso antigo que o Q5 queria recuperar continua valendo.
- **Mais de uma linha possível:** a nota não baixa nenhuma. As linhas em que ela cabe saem do suprimento e vão para `recebNaoApuravel`, com o aviso "Nota N sem unidade ou linha cabe em mais de uma linha do PC: previsão fora do suprimento. Confira a nota no Estoque."
- A previsão nunca fica integral. A regra é a mesma do P2: o lote já está no físico, e manter a previsão inteira esconderia uma falta.
- A nota com unidade e linha não muda: baixa só a sua linha.

Mesma regra nos dois lados:
- JS: `cenCompCabe`, `cenCompOutra` e `cenCompCasa(r,p,linhas)` no `cenario.js`;
- Python: `cabe`, `chave` e `linha_de` em `dados2.est_dem`.

Quem usa a regra:
- `cenEstDem` e `est_dem`: a previsão da demanda;
- `cenCompSaldo`: a etapa 6 de Compras e o EST, com as linhas do mesmo PC tiradas de `cenCompLinhas`;
- `epeds` do EST: os pedidos da semente, com a lista `E2.pedidos`.

Na etapa 6 de Compras, a linha ambígua mostra "Não apurável" em Recebido e em A entregar, e a dica cita a nota.

## 3. Testes executados

Ver `logs/`.

| Teste | Resultado |
|---|---|
| `c34_test.cjs` | 20 PASS (19 + Q5) |
| `c34_paridade_test.py` | 6 + 6 paridades JS × Python PASS. Casos Q5: legado único abate; unidade divergente não abate; contraexemplo do Codex (100 kg e 50 L) sai do suprimento com aviso nas duas linhas; mesma unidade sem linha, ambígua; unidade única entre as linhas, baixa só a sua; com linha, baixa só a sua |
| `n1_emission`, `n1_recipe` | 8 e 24 PASS. Vermelhos desde a v131: recortavam o `cenario.js` pela linha 305, que o C-3/C-4 deslocou. Agora pegam o `cenIdem` pelo nome |
| `n1_adapter`, `n1_composicao`, `sup_movimentos` | 6 · 7/7 · 7 PASS |
| `ben_unit`, `legal_unit`, `usar_os_unit`, `config_unit`, `mip_unit`, `producao_unit` | 206/206 · 35/35 · 24/24 · 226/226 · 34/34 · 160/160 |
| `os_aprov_lib`, `ma_regras`, `cen_grava`, `aprova_quem_decide` | 51/51 · 150/150 · 10/10 · 103/103 |
| Navegador (render da candidata): `c34_fluxo`, `est_onda0`, `est_item_divergente`, `est_a4`, `est_a4_nav`, `tabelas_est` | 17/17 · 24/24 · 6/6 · 53/53 · 15/15 · 34/34 |
| `compras_materiais` (navegador e unit), `d5_reserva` | 32/32 e 41/41 · 13/13 |
| `demanda_unica` | 60/71: as mesmas 11 falhas da v131, conferidas linha a linha (`diff` vazio contra `artefato-v131/bateria`) |
| `saf_cmp_continuidade` | 29/31: as mesmas #14 e #16 da v131 (base verde 2) |

## 4. Contraprova

Os testes novos rodaram sobre o `cenario.js`, o `dados2.py` e as telas da v131 (`8dcf39d4`):
- `c34_paridade` reprova no contraexemplo do Codex: 80 kg e 30 L, com `recebNaoApuravel` vazio (`logs/c34_paridade_contraprova_f5857498.log`);
- `c34_test` reprova no caso Q5 (`logs/c34_test_contraprova_f5857498.log`).

## 5. Limites

- Na semente, nenhum PC tem duas linhas do mesmo item, e toda nota gravada depois do C-3 leva unidade e linha. O caso ambíguo vem só de dados antigos do navegador. Por isso o "Não apurável" da etapa 6 está coberto pelo teste de domínio (`cenCompSaldo`), não por um passo no navegador.
- No EST, a linha ambígua mantém o saldo sem a nota ambígua, que é o limite superior. O aviso fica na demanda e em Compras.
- `logistica_saida_test.cjs` depende do `logistica_saida_captured.js`, que só existe depois da captura no navegador. Não rodou aqui.
