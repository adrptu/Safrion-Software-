# Composição com o PR #106 (EX-50(a)-SUP / SU-01), 17/10/2026

- **Base:** `8b2b44c`. PR #106 do Codex, HEAD `b0888cc`, integrado em `5697d1a`; ajuste do integrador em `fea4441` (SU-04 sem a ação órfã "Enviar COT-113" e sem "1 rascunho" no selo).
- **Parecer:** 6234809748; reteste no PR em 6234809387 (Node 15/15, contraprova em 3c183db 1 !== 0, 1440/390/teclado).
- **Testes pelo impacto na composição** (executados; brutos nesta pasta): compras_materiais_unit 41/41, compras_materiais 32/32, acao_unica 10/10, componentes 3/3, links_ocultos 16/16, demanda_estado_nav 14/14, quantidade 16/16, paginas_scan 5/5 (148 páginas), sup_necessidades 15/15.
- **Vermelho antigo:** textos_soltos 267/268, falha `D CA-01det`. O mesmo teste no render publicado (v121, `textos_soltos_base.log`) dá a mesma falha, então ela não vem desta integração. Fica na fila da base verde.
- **Páginas que mudam em relação ao publicado:** só `SU-01.dc.html` e `SU-04.dc.html`.
