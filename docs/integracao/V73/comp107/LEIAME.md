# Composição com o PR #107 (EX-50(a)-SUP / SU-02), 17/10/2026

- **Base:** `a691c2c`.
- **Integração:** PR #107 do Codex (HEAD `91fa027`) integrado em `175ae8b`.
- **Ajustes do integrador:**
  - `5ef39a9`: selo do cabeçalho pelo estado (`supPolSelo`, MARK/`dyn_status`); sai o bloco "Publicação de vigência"; "Simular antecedência".
  - `43089eb`: substitutos MARK/`dyn_status` na captura do teste VM.
  - `ff3ae2c`: oráculo do textos_soltos passa ao selo vivo.
- **Parecer:** 6235406447. Reteste no PR em 6235406242. Achados A1–A4 em 6235369391, todos fechados.
- **Testes pelo impacto** (executados; brutos nesta pasta):

  | Teste | Resultado |
  |---|---|
  | sup_politicas | 11/11 |
  | sup_politicas_ui (VM, g2open/g2save/g2persist reais) | 9/9 |
  | sup_necessidades | 15/15 |
  | acao_unica | 10/10 |
  | componentes | 3/3 |
  | links_ocultos | 16/16 |
  | paginas_scan | 5/5 (148 páginas) |
  | compras_materiais | 32/32 |
  | textos_soltos | 267/268 |

- **Vermelho antigo:** a falha restante do textos_soltos, `D CA-01det`, é da base v121 (`../comp106/textos_soltos_base.log`).
- **Sonda no navegador** (`sonda_su02.py`/`.log`):
  - selo: 1 proposta → 2 → "1 proposta aguardando gestor · 1 aprovada a publicar" → 1;
  - publicar gera vigente v5 com recibo `p1:1`;
  - o perfil sem gestão é recusado;
  - 390 sem rolagem horizontal; o teclado abre o painel;
  - nenhum erro de JS.
- **Páginas que mudam em relação ao publicado:** só `SU-02.dc.html`.
