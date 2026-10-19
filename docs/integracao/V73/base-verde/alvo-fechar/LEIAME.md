# Base verde F3: o "×" dos painéis com alvo de toque de 44 px, 19/10/2026

**Autoria:** Claude. **Revisão e integração:** Codex. **Base:** composição `5bc0b340`.

**Origem:** achado F3 da revisão do PR #129 (`docs/integracao/V73/pr129/LEIAME.md`), anterior ao PR.
- **Medida em 19/10:** a 390 px com toque, "Salvar meta" e "Salvar papéis" já ficam com 44 px de altura (ALVO_ST, DS-ALVO-20261015). Só o "×" de fechar fica com 32 × 32 px.
- **Inventário:** o "×" é desenhado à mão em cerca de 20 telas, entre elas Configurações, O.S., agronomia, solo, irrigação, logística, máquinas, compras, planos e safra. É sempre o mesmo estilo, `width: 32px; height: 32px`.

**Dano evitado:** alvo pequeno no celular, que leva a toque errado ao fechar um formulário com rascunho.

## Mudança (fonte comum, `engine.py`, ALVO_CSS)
Com ponteiro grosso, `button[aria-label^='Fechar']` com `width: 32px` e `height: 32px` no estilo ganha `min-width` e `min-height` de 44 px.
- **Com mouse:** nada muda.
- **Fundo escuro que também fecha o painel:** não tem largura no estilo e fica de fora.
- **Telas:** nenhuma tela precisou ser editada.

## Testes executados (render sintético, Chrome)

| Teste | Resultado |
|---|---|
| `alvo_fechar` (novo). A1 390 px com toque: o "×" mede 44 × 44 em CF-06, CF-01 e O.S.; A2 1440 px com mouse: segue 32 × 32; A3 o fundo segue cobrindo a tela; A4 sem erro de JS | 4/4 |
| Contraprova: `alvo_fechar` na composição `5bc0b340` | 3/4. Reprova A1: 32 × 32 com toque |

**Impacto:**

| Teste | Resultado |
|---|---|
| `ds` | 72/72 |
| `ds_padrao` | 17/17 |
| `ds_1510` | 17/17 |
| `ds_1610` | 16/16 |
| `ds_man` | 99/99 |
| `ds_unit` | 31/31 |
| `regras_toque` | 5/5 |
| `popover_390` | 9/9 |
| `config` | 90/90 |
| `cada_cd04` | 15/15 |
| `paginas_scan` | 5/5 (147 páginas) |

**Vermelho antigo achado na mesma bateria:** `assinatura` dá 39/45, com as mesmas 6 falhas na composição `5bc0b340` sem esta mudança (`logs/assinatura_5bc0b340.log`): A7b, A4d, A9c, A9d, A9e e A18c, sobre fatura, reativação e CSV. Não vem desta mudança. Fica como item da base verde 2, a classificar entre defeito do produto e oráculo obsoleto, sem esconder o teste.

**Fotos (`fotos/`):** `cf06_painel_390_antes` mostra o "×" com 32 px; `cf06_painel_390_depois` mostra o "×" com 44 px, alinhado ao título.
