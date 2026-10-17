# Composição com o PR #109 (EX-50(a)-SUP / CA-02), 17/10/2026

- **Base:** `ac5cd1d`. O PR #109 do Codex (HEAD `9d285f2`) foi integrado em `ca9414a`.
- **Ajustes do integrador** (`a5eb5dc`):
  - fila ordenada (Provisório → Dados alterados → Não conforme → Conferido → fase que não admite);
  - selo dinâmico (`ca_st`);
  - sai a faixa de kpis fixos (TAB-07) e a mensagem "Devolver para esclarecimento", que não tinha efeito;
  - a primária "Revisar próximo apontamento" (`ca_proximo`) só abre a próxima pendência;
  - substituto `BTN_ST` na captura do teste.
- **Parecer:** 6236406668. A revisão está em 6236406328.
- **Gitleaks:** `ac5cd1d7..9d285f2` sem achado.
- **Testes pelo impacto** (executados; brutos nesta pasta):

  | Teste | Resultado |
  |---|---|
  | campo_conferencia | 7/7 |
  | conferencia_diaria_test (`--output conferencia_diaria_out.json`) | 30/30 |
  | links_ocultos | 16/16 |
  | acao_unica | 10/10 |
  | paginas_scan | 5/5 (148 páginas) |
  | textos_soltos | 267/268 |

  A falha restante, `D CA-01det`, já existia na v121. O primeiro `conferencia_diaria_test.log` com rc=2 foi falta do argumento `--output`, e a repetição correta deu 30/30.
- **Sonda no navegador:**
  - **No HEAD do PR** (`sonda_ca02_pr_head.log`, perfil Paula):
    - conferir o OS-0420 dia 2 grava `Conferido/Paula`;
    - divergência sem motivo é barrada no campo; com motivo, Não conforme;
    - Rui é recusado pela AL-12 e o formulário fica aberto.
  - **Na composição** (`sonda_ca02.log`):
    - os provisórios vêm primeiro;
    - o selo vai de 4 para 3 depois de conferir;
    - a primária abre a próxima pendência, e o Enter também;
    - a 390 não há rolagem horizontal;
    - nenhum erro de JS.
- **Páginas que mudam em relação ao publicado:** só `CA-02.dc.html`.
