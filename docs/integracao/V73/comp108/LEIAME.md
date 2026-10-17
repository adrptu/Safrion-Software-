# Composição com o PR #108 (EX-50(a)-SUP / SU-08), 17/10/2026

- **Base:** `3e0483e`. O PR #108 do Codex (HEAD `550de54`) foi integrado em `8dceba2`.
- **Meus ajustes:** `3d822e4` e o commit deste recibo. "Registrar perda" virou a ação principal, transferência e estorno ficaram como prévias e saíram os kpis (TAB-07). O rodapé mantém a frase "Correção não apaga a operação original".
- **Parecer:** 6235896564. O reteste está em 6235896246 e os achados A1–A3, em 6235833604.
- **Gitleaks:** `3e0483e1..550de54` sem achado.
- **Testes pelo impacto** (executados; brutos nesta pasta):

  | Teste | Resultado |
  |---|---|
  | sup_movimentos | 7/7 |
  | sup_movimentos_ui | 7/7 |
  | sup_politicas_ui | 9/9 |
  | sup_necessidades | 15/15 |
  | est_a4_test | 53/53 |
  | est_onda0 | 24/24 |
  | acao_unica | 10/10 |
  | componentes | 3/3 |
  | links_ocultos | 16/16 |
  | paginas_scan | 5/5 (148 páginas) |
  | textos_soltos | 267/268 |

  A falha restante, `D CA-01det`, já existia na v121.
- **Sonda no navegador** (`sonda_su08.py`/`.log`):
  - extrato com 10 linhas "Histórico (exemplo)", sem ações;
  - a perda gera AJ-71 em Aguardando gestor e o físico não muda;
  - Rui é recusado pela AL-09;
  - Ana aprova: físico 60.000 → 59.995 e `MV-1001`;
  - as prévias não criam movimento;
  - "Registrar perda" abre com o Enter;
  - a 390 não há rolagem horizontal;
  - nenhum erro de JS.
- **Páginas que mudam em relação ao publicado:** 56. A `SU-08` muda de fato. As outras 55 diferem só pela função `cenPerdaNova`, acrescentada ao fim do `cenario.js` que todas carregam (conferido página a página).
