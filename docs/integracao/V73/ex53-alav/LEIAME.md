# EX-53 D11 no Painel: Alavancas e cartões com a meta vigente, 19/10/2026

**Autoria:** Claude, que tem a autoria do `pgCor` e das Alavancas (PR #47). **Revisão e integração:** Codex.
**Base:** composição `1cf11a81`, com o PR #129 (D11) já integrado.

**Resultado útil:** com a meta gravada pelo gestor em Configurações › Metas e limites, o Painel colore e diz o resultado.
- **Alavancas do resultado:** "Custo da execução" e "Preço médio vendido".
- **Agrícola:** cartões de custo por cultura.
- **Comercial:** cartões de preço médio.

**Dano evitado:** o mesmo desvio aparecia colorido no Mapa e na Inteligência de vendas, mas cinza no Painel. A tela principal do gestor não mostrava o resultado da meta que ele configurou.

## Mudança (`areas/painel_gestao.py`)
- **`pgMeta`:** é o único leitor da meta para o Painel.
  - Custo: `metaAvaliar(c,'custo-desvio', desvio_exec_pct do agrCustoRef, '%', parcial)`, a mesma conta da camada Custos do Mapa.
  - Preço: `intMeta(c,'venda-referencia', intSpread(medC, ref), saca a conferir)`, a mesma conta da Inteligência de vendas. Para isso, o `inteligencia.js` entra no build do Painel (ENG-011: nenhuma cópia da fórmula).
- **Sem meta:** cinza, e o aviso fica uma vez só no título do bloco. Com metade configurada, ele diz qual falta: "Meta de custo não configurada" ou "Meta de preço não configurada".
- **Com meta:** a cor e o texto ("Meta atendida", "Atenção à meta" ou "Fora da meta") vão na célula ou no cartão.
  - Parcial ou sem base fica cinza, sem texto a mais, porque o "—" e o "Indicador parcial" já dizem.
  - O "·" fica preso à palavra anterior, para não abrir linha a 390 px.
- **`pgCor()`:** segue cinza para o que não tem meta no catálogo ("Ativos liberados").

## Testes executados (render sintético deste commit)
| Teste | Resultado |
|---|---|
| `ex53_alav_meta` (novo, navegador). L1 sem meta; L2 meta de custo 5/10; L3 meta de venda 0/−2; L4 cartões = Alavanca; L5 sem erro de JS. O oráculo é refeito sobre os dados crus (`window.__pg.pgDados`) | 5/5 |
| Contraprova: `ex53_alav_meta` no render da composição `1cf11a81`, sem a ligação | 2/5. Reprova L2, L3 e L4, que continuam cinza |
| `ex53_metas` (o Painel sem meta continua cinza, com o aviso uma vez só) · `painel03` | PASS · 54/54 |
| No render anterior ao ajuste de texto (a lógica é a mesma; só mudou o texto de "sem base"): `ex53_m5_cartao`, `ex53_f1c`, `inteligencia_unit`, `inteligencia_nav`, `paginas_scan`, `textos_soltos` | PASS · PASS · 35/35 · 28/28 · 5/5 (147 páginas) · 267/267 |

**Fotos conferidas** (`fotos/`), com custo 5/10 e venda 0/−2 gravados pela CF-06:
- O Mamão de Lagoa Grande fica verde no custo (0,0 %, "Meta atendida") e amarelo no preço (−1,6 %, "Atenção à meta").
- A Soja parcial e o Café sem referência ficam cinza.
- A 390 px não há rolagem lateral, e nenhuma linha começa com "·".
