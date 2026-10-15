# V69 · Compras de materiais, peças e serviços (CMP-MAT)

Dados sintéticos. Regime leve do protótipo (AGENTS §3.5). Pedido do proprietário (15/10/2026): "Só temos compras de insumos, cadê as compras de materiais, peças, etc?" e "Compra de materiais, peças, etc tem que seguir uma lógica diferente, porque pode atender varias culturas e safras diferentes o que se está comprando."

## Acordo (AGENTS §3.4)

```text
ID / resultado útil / persona: CMP-MAT · comprar peça, material e serviço de manutenção pela mesma tela de Compras, sem safra; a peça de uma OM chega reservada para ela · Ana (gestora, compra), Otávio (PCM, pede), Zé (mecânico, recebe o uso)
Requisitos do PRD e fora do escopo: PRD 4.2/4.3 (master-detail, uma primária, próximo passo com verbo), cap. 74 (BOT/SEL/ETP/VIS, faixa Filtros), §4 AGENTS (trava só onde protege: dinheiro e estoque). Fora: rateio às culturas (só a frase "rateio pelo uso do ativo"), cadastro dos fornecedores de peças no CD-05, itens de manutenção no catálogo e no Estoque geral (1b), cancelamento de requisição, aprovação acima da alçada (só o motivo).
Autor / revisor / integrador: Claude (autor) / Codex (revisor, sem bloquear: §3.5) / quem integra a branch única
Base (commit ou hashes) / arquivos sob responsabilidade: a0db53a · areas/processo_compras.py, dados_compras_mat.py (novo), dados_manutencao.py (manSolicitar, manReceber, manLiberar, ITENS: ponto de pedido), ui37.py (título do item e faixa condicional), visoes_marcas.py (g_mat), compras_materiais_test.py e compras_materiais_unit.js (novos)
Aceite e comando de verificação: (1) Compras tem o seletor "Insumos da safra | Materiais, peças e serviços"; (2) peça de OM: requisição → cotação → pedido → recebimento põe a peça no saldo para a OM, que sai de "Falta peça" e libera (reserva na liberação, DEC-2609-13); (3) item abaixo do ponto de pedido aparece e vira requisição de reposição, que no recebimento entra no estoque; (4) serviço aceito vai como custo de terceiro da OM; (5) nenhuma requisição de material pede safra ou cultura · `env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico python3 -B compras_materiais_test.py` e `python3 -B compras_materiais_unit_test.py` (contraprova na base a0db53a)
Estado / impedimento / próximo passo: em andamento · sem impedimento · implementar, testar e registrar a bateria abaixo
```

## Regras de domínio (decididas pelos agentes, delegação do proprietário)

- **Origem da necessidade**, nunca o plano da safra: (a) OM da Manutenção que precisa de peça ou de serviço de terceiro; (b) reposição do almoxarifado da oficina quando o saldo livre mais o que já está pedido fica abaixo do ponto de pedido do item; (c) requisição avulsa de uma área (oficina, sede, irrigação…), com urgência.
- **Apropriação** por OM, ativo ou centro de custo. A compra não pede safra nem cultura. O custo chega às culturas pelo uso do ativo (horas × custo R$/h): o detalhe diz "rateio pelo uso do ativo"; o rateio não é construído aqui.
- **Mesmas etapas da compra de insumos:** requisição → cotação (só fornecedor homologado do grupo; envio simulado) → pedido (escolha da proposta, justificativa quando não é a de menor custo, alçada da Compra) → recebimento.
- **Recebimento:** peça de OM entra no saldo para a OM, que sai de "Falta peça" e pode ser liberada; a reserva nasce na liberação (**DEC-2609-13**, decisão registrada do proprietário). Prender a peça à OM desde o recebimento é a pergunta **D5** ao proprietário (`docs/pcm-suprimentos/DECISOES.md` §4): fica pronta atrás da chave `RESERVA_NO_RECEBIMENTO` (desligada; `dados_compras_mat.py`), com teste dos dois modos. Reposição entra no estoque da oficina; material avulso sem código vai direto ao centro de custo.
- **Coerência com `docs/pcm-suprimentos` (especificado, não implementado):** mesmos grupos (Peças, Lubrificantes, Serviços de manutenção), mesmos fornecedores F08 (Peças e Lubrificantes) e F09 (Peças), mesma série PC-2nn e o mesmo caso da OM-0235 (F09 R$ 4,80 mais barata, chega em 29/09; a OM precisa em 24/09). Esta fatia não faz o recebimento por NF no Estoque nem a compra de balcão (Bloco 1c dessa especificação).
- **Serviço não tem estoque:** o recebimento é o aceite do serviço, que lança o valor do pedido como custo de terceiro da OM (função única de custo da Manutenção).
- **Uma requisição, uma numeração:** SC-nnn é a mesma sequência do "Solicitar compra" da Manutenção; pedidos de manutenção em PC-2nn (os de insumos ficam em PC-1nn).
- **Fornecedores de peças e serviços** são fictícios e declarados no módulo até entrarem no CD-05 (decisão pendente de integração, sem custo).

## Bateria

A preencher ao fim (executado × especificado).
