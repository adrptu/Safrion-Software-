# ENTRADA-RAPIDA · onde EDL-01 e INP ainda faltam (próximas ondas)

> Proprietário, 16/10/2026: "todos inputs do usuário no sistema devem ser mais rápido e fácil."

Padrões em `docs/design-system/padroes-1610.md` (seção "Entrada rápida"): **EDL-01** (editar em lote numa grade) e **INP-01 a INP-11** (entrada rápida em todo campo). Esta lista é o inventário para as próximas ondas; **só o Planejar safra foi implementado nesta frente** (`SAF-LOTE.md`).

## Já vale em todas as telas (motor, executado)

- **INP-04** número selecionado ao receber o foco pelo toque ou pela navegação da tela (`g2lib.js`, `g2inp`).
- **INP-07** número, data e código sem corretor ortográfico nem maiúscula automática (`g2lib.js`, `g2inp`).
- **Já existia no formulário do motor:** teclado decimal nos campos `t='num'` e a unidade ao lado quando o campo declara `u` (INP-03); erro junto ao campo e recusa que mantém o digitado (INP-11).
- **Não mudou:** o Enter dos formulários (INP-08). Ele só desce na coluna dentro da grade de edição.

## Como se mediu

- **Executado:** o `entrada_inventario.py` (gen37) lê a especificação das grades em `project/*.dc.html`, depois do build desta branch. Ele conta as listas que se editam por formulário (um painel por linha), as linhas da semente, os campos editáveis do formulário e os números sem unidade declarada. Bruto: `entrada-inventario.json`, nesta pasta.
- **Medido no navegador:** só o Planejar safra (`saf_lote_medida.py`, em `SAF-LOTE.md`).
- **Estimado pelo desenho:** o custo de hoje nas outras telas. Mudar um campo em N linhas pelo formulário custa cerca de 3 cliques por linha (abrir, escolher o campo, salvar) mais a digitação. Na grade, custa cerca de 2 cliques mais a digitação, com Enter descendo.
- **Frequência:** estimada pelo papel da tela no trabalho. O protótipo não tem dado de uso.

## Inventário (telas do menu vigente)

| Prior. | Tela | Lista (grade) | Linhas na semente | Campos no formulário | O que falta | Custo estimado hoje → com EDL-01 | Frequência (estimada) |
|---|---|---|---|---|---|---|---|
| P1 | Suprimentos › Estoque | Contagem de inventário (`g_cnt`) | por inventário | 4 (Quantidade contada sem unidade declarada) | EDL-01 na contagem (uma linha por lote, coluna "contada", Enter desce, colar do coletor); INP-03 com a unidade do item ao lado | 3 cliques por item → ~2 cliques + digitação | a cada inventário (mensal ou por safra), dezenas de itens |
| P1 | Cadastros › Produtos, unidades e locais (CD-06) | Itens (`g_itm`) | 50 | 13 (Conteúdo da embalagem e Preço de referência sem unidade declarada) | EDL-01 para preço de referência e embalagem (colar a tabela do fornecedor); INP-03 (R$/un e "L", "kg" ao lado) | 150 cliques para revisar o preço dos 50 → ~2 cliques + 50 valores ou 1 colagem | mensal (preço) |
| P1 | Cadastros › Fazendas, áreas e talhões (CD-01 e CD-01det) | Talhões (`g_tal`, `g_idt`) | 35 e 32 | 8 | EDL-01 na implantação (colar nome, área, fazenda e situação da planilha do produtor) | 35 formulários → 1 colagem + conferência | implantação e a cada mudança de área |
| P2 | Agrícola › Planejar safra › Operações e recursos | Rendimentos (`g_rend_*`) | 42 a 43 | 19 (13 números) | EDL-01 para rendimento, custo/h e diesel por atividade (o "Aplicar em todas as atividades da operação" já existe por linha) | ~3 cliques por atividade → grade | por safra |
| P2 | Cadastros › Operações e rendimentos (CD-08) | Rendimentos (`g_rend`) | 22 | 16 (8 números) | EDL-01 (mesma grade do item anterior, fonte única) | ~3 cliques por linha → grade | por safra |
| P2 | Cadastros › Pessoas e equipes (CD-04) | Pessoas (`g_pes`) | 15 | 12 (6 datas) | EDL-01 para equipe, função e validades (NR, ASO); INP-05 (datas com atalho) | ~3 cliques por pessoa e data → grade | implantação e vencimentos |
| P2 | Cadastros › Máquinas, instalações e setores (CD-03) | Máquinas (`g_atv`) | 15 | 27 (19 números) | EDL-01 para custo/h, horímetro e potência; INP-03 já tem unidade | ~3 cliques por máquina → grade | implantação e revisão de custo |
| P2 | Suprimentos › Compras | Escolha da cotação (`g_cmp`) | por cotação | 3 (Quantidade a pedir sem unidade declarada) | INP-03 (unidade do item ao lado); EDL-01 para quantidades da cotação | por item → grade | a cada compra |
| P2 | Suprimentos › Estoque | Entrega e devolução (`g_ent`, `g_dev`) | por requisição | 2 e 3 (quantidades sem unidade declarada) | INP-03 (unidade ao lado) | — | diária |
| P3 | Agrícola › Análises de solo (AG-02) | Água no solo e valor do laudo (`g_agua`, `g_ext`) | por laudo | 12 e 2 (CC, PMP e Valor sem unidade declarada) | INP-03; INP-09 (colar o laudo do laboratório) | por valor → 1 colagem | por laudo |
| P3 | Cadastros › Culturas e cultivares (CD-02) | Cultivares (`g_cv`) | 12 | 9 | EDL-01 (ciclo e grupo por cultivar) | ~3 cliques por linha → grade | rara |
| P3 | Cadastros › Parceiros (CD-05) | Parceiros (`g_forn`) | 20 | 22 | INP-07 já cobre CNPJ e CPF; EDL-01 só se a importação do ERP não cobrir | — | rara |
| P3 | Cadastros › Estrutura gerencial (CD-07) | Códigos (`g_dim`) | 30 | 10 | EDL-01 (colar o plano de contas) | 30 formulários → 1 colagem | implantação |

**Fora desta lista, porque estão em PRs abertos do Codex:**
- O.S. em lote (`OS-LOTE`, `cenario.js`, `areas/processo_os.py`);
- Crédito › Documentos (`GE-08`, "Módulos fiscais" sem unidade declarada);
- Estoque (`areas/processo_estoque.py`).

Elas só entram depois da integração desses PRs, com o mesmo padrão.

**Telas ocultas no menu** (PL, SU, VE, CO; módulos preservados) também têm listas editáveis por formulário: Programação integrada, Políticas de estoque, Pedidos, com Quantidade sem unidade. Ficam para quando voltarem ao menu.

## Ordem sugerida das ondas

1. **Estoque › Contagem.** Grade de contagem com Enter descendo, a unidade ao lado e colar do coletor. É a digitação mais repetitiva do almoxarifado.
2. **CD-06 Itens (preço e embalagem) e CD-01 Talhões (implantação).** Colar da planilha do fornecedor e do produtor.
3. **Rendimentos (SAF e CD-08) numa grade só**, pela mesma função de conferência (ENG-011).
4. **Pessoas, Máquinas, Cultivares e Estrutura gerencial**, conforme a implantação dos primeiros clientes.

Cada onda reaproveita a peça do Planejar safra:
- `safra_lote.js`, bloco SL-PURO: colar, datas, número, aplicar aos marcados e contador;
- o desenho de `areas/saf_lote.py`.

A primeira onda que repetir a peça deve levá-la para o motor (`engine.py` e `g2lib.js`) antes de copiar.
