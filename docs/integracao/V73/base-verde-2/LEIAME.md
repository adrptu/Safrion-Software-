# Base verde 2 (18/10/2026)

Vermelhos antigos que vinham da v130/v131. A regra é a do AGENTS §3.6: separar defeito do produto, teste obsoleto e falha da ferramenta, e corrigir sem afrouxar.

| Campo | Valor |
|---|---|
| ID / resultado útil | Base verde 2. A bateria volta a distinguir regressão de ruído: cada vermelho restante passa a ser defeito real |
| Autor / revisor / integrador | Claude (autor, testes e menu) · Codex (revisor; a revisão não bloqueia, §3.5) · Claude (integrador) |
| Base | `6234dd69` (v132) |

## 1. Causas e correções

| Vermelho | Causa | Tipo | Correção |
|---|---|---|---|
| `est_fix1`, `est_fix2`, `est_cenario`, `esttest`, `est_laudo_lote_nav`, `demanda_estado_nav` | TAB-12 (17/10): as grades nascem recolhidas, e os testes procuravam lotes e requisições que não estavam na tela | Teste obsoleto | `est_lib.expandir()`: depois de abrir e de trocar de seção, usa o "Expandir tudo" de cada grade visível, como a pessoa. A linha não achada abre as grades e é procurada de novo. Os testes com helper próprio ganharam o mesmo passo |
| `est_fix1` etapas 4 e 5 | TAB-05 (17/10): as ações da linha moram no ⋯ da própria linha | Teste obsoleto | O que precisa estar inteiro (ou alcançável pelo teclado) é o ⋯ da linha |
| `est_fix1` Restaurar | O botão de visão "Tabela", só com ícone, também fica pressionado | Teste obsoleto | Conta só os filtros com nome |
| `demanda_unica` (11), `saf_cmp_continuidade` #14, `cal01`, `cmptest`, `demanda_unica_nav` | OS-LOTE (`6dfa09c1`, Codex, 16/10) pôs na semente as O.S. de demonstração do agrupamento, com Sulfato de magnésio: a 2026/27 ganhou 1 insumo e R$ 178,50 (85 kg) | Semente mudou; a conta está certa | Totais esperados atualizados (14 → 15 insumos; R$ 428.305,00 → R$ 428.483,50; B12, B18 e E1 pelo mesmo delta), com a origem citada no teste. Conferi o insumo novo calculando a demanda da `ee725ab` contra a de agora: só o Sulfato de magnésio entrou, nada saiu nem mudou |
| `demanda_unica` A8, E1–E3, H1 (`KeyError: 'Santa Rita'`) | `fe296d63` (15/10, filtro Safra do Mapa): a demanda do Mapa passou a ser por safra | Teste obsoleto | As asserções por fazenda leem a safra corrente de cada uma (Santa Rita = S2627, Lagoa Grande = LG2627) |
| `saf_cmp_continuidade` #16 | TAB-12: os itens da comparação de propostas nascem recolhidos | Teste obsoleto | "Expandir tudo" antes de ler |
| `nav_modulos` N2 Crédito | O CRE F2 (`52cfe856`, Codex, 16/10) mudou os cartões da entrada (Ficha do grupo, Dossiês, Pedidos e contratos, Liberações e garantias), mas o menu ficou com a lista antiga | **Defeito do produto (S3):** menu e entrada diferentes | O menu passa a ter a mesma lista da entrada, numa fonte só (`ui37.MENU2` + `CURTO37`); saiu a lista à parte em `modulos.itens_do`. Os documentos para crédito seguem na ficha ("Ver documentos") e em `#vis=documentos` |
| `mbtest` MB-02 (excesso de 1.142 px) | O pacote do operador passou a listar as 5 O.S. de demonstração do agrupamento (OS-0595 a OS-0599) | Altura da prancha desatualizada | Prancha do MB-02 de 2.320 para 3.480 px, e o viewport do teste acompanha |
| `mbtest` saía com código 0 mesmo com falha | — | Ferramenta | Sai com 1 quando há falha |
| `cmptest` (21 OK e queda; verde na v95 com 101) | TAB-12 (árvores de convites e propostas recolhidas); TAB-05/DS-MODULOS-2 (ações secundárias no ⋯ do topo); o caminho "Direção numa página nova" zerava só a chave antiga, mas desde o C-3/C-4 a compra mora no cenário; o Sulfato de magnésio também chega depois da falta | Teste obsoleto | Abre as árvores; o clique alcança o item do ⋯; as ações secundárias são lidas no menu fechado; a página nova começa do armazenamento vazio, como no `c34_fluxo`; o resumo conta 2 escolhas atrasadas e confere que a 2ª é o Sulfato |
| `cadastros_padrao` P5a/P5b | TAB-12: a fazenda nasce recolhida no CD-01 | Teste obsoleto | Confere que nasce recolhida, abre pela seta, soma os talhões aberta e recolhe de novo |
| `n1_emission`, `n1_recipe` | Recortavam o `cenario.js` pela linha 305 | Ferramenta | Já corrigido no Q5-AMB (`f6a9374a`): pegam o `cenIdem` pelo nome |

## 2. Testes executados

Executado nesta candidata (`6234dd69` + as mudanças desta pasta), com `SAFRION_DADOS=sintetico`. Brutos em `logs/`.

| Teste | Resultado |
|---|---|
| `est_fix1` · `est_fix2` · `est_cenario` · `est_laudo_lote_nav` · `esttest` | 13/13 · 11/11 · 15/15 · 7/7 · OK |
| `demanda_unica` · `demanda_estado_nav` · `demanda_unica_nav` · `cal01` | 71/71 · 14/14 · 29/29 · 45/45 |
| `cmptest` · `saf_cmp_continuidade` | sem falha · 31/31 |
| `nav_modulos` · `credito_menu` · `cadastros_padrao` | 15/15 · 26/26 · 44/44 |
| `mbtest` · `ds_test` · `ds_man` | 0 falhas (sai com 1 quando falha) · 72/72 · 99/99 |
| `paginas_scan` · `links_ocultos` · `textos_soltos` | 5/5 (148 páginas) · 16/16 · 267/267 |

**Cartões do Planejar safra** (defeito do proprietário de 18/10: "esse cartão está com defeito, cortado e fora do padrão"). A faixa da fazenda virou cabeçalho de seção nos Cartões, e os totais saem numa linha só (`g2lib.js`). Resultados em `logs/cartoes/`:
- `cartoes` 70/70;
- `drill_recolhido` 66/66;
- `saf_fazendas` 14/14;
- `saf_multi_fazenda` 23/23;
- `saf_tab` 14/14;
- `seta_padrao` 14/14;
- `tabelas_saf` e `saf_lote` entram em `logs/cartoes/` assim que terminarem.

## 3. Contraprova

- **Menu do Crédito:** o `nav_modulos` reprova a v131 no N2, com menu e entrada diferentes (`docs/integracao/V73/ds-man/logs/`). Na candidata, as duas listas saem da mesma fonte.
- **Totais da demanda:** os casos de dano do `demanda_unica` (seção A: compra em dobro e compra a menos) não mudaram. Só mudou o total da semente, pelo insumo conferido acima.
- **Grades recolhidas:** o recolhimento padrão continua conferido pelo `drill_recolhido_test`. O passo de abrir fica nos testes de domínio, não no produto.
