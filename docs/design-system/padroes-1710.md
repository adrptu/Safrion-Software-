# Padrões de 17/10/2026

Pedidos do proprietário em 17/10, transformados em padrão pelo método da skill `padrao-safrion`.

- **Valem para todas as telas do mesmo tipo**, no protótipo e no software real.
- **Medição e catraca:** `tools/prototipo/v37/gen37/ds_modulos.py` (148 telas, 10 regras); `--catraca` reprova se a contagem de alguma regra subir em algum módulo.
- **Relatório da frente:** `docs/integracao/V73/ds-modulos-2/DS-MODULOS-2.md`.

## MAIS-02 · Ações do cabeçalho da tela: a primária e o ⋯

> "os 3 pontinhos no topo da tela a direita em criar plano.... é uma boa, toda tela que tiver mais ações pode ter esses 3 pontinhos nesses botões dessa região da tela."

**Referência:** Manutenção › Planos ("Criar plano" + ⋯).

**Regra:** à direita do título fica à vista no máximo uma primária verde; as outras ações do contexto vão para o "⋯ Mais ações", à direita dela. Detalhe, exceções e peça única em [barra-limpa-mais-acoes.md](barra-limpa-mais-acoes.md) §3. Substitui, só no cabeçalho da tela, o "primária e uma secundária à vista" da MAIS-01.

**Dano evitado:** fileira de botões no topo, que esconde o comando da vez.

**Teste:** `ds_modulos.py` regra MAIS-02 (148 telas) e `cadc_cd07_test.py` (Estrutura gerencial). Contraprova: o render anterior tem 1 desvio (CD-07) e reprova.

## VIS-07 · Cartões compactos em grade (revê a VIS-06 no motor)

> "os cartoes em ordem de serviço estao fora do padrao design system" (print da O.S. em Cartões, agrupada por talhão)

**O que estava errado:** dentro de cada grupo o cartão saía como uma linha larga de tabela dentro de uma caixa, com cabeçalho de colunas acima dos grupos e os valores espalhados na largura toda.

**Regra (modo Cartões do motor, em toda tela, inclusive agrupado):**
- Grade de cartões compactos: vários por fileira no computador (mínimo de 300 px cada), um por fileira no celular.
- Dentro de cada grupo, a mesma grade; o título do grupo e as somas ficam acima dela.
- Cada cartão:
  1. seta à esquerda quando há itens dentro (abre no próprio cartão), seleção quando a lista tem;
  2. título com o identificador e, ao lado, o **selo de estado** (a 1ª coluna em que todo valor começa por um selo: Fase, Situação);
  3. até 4 campos, cada um com o seu rótulo, em duas colunas;
  4. ⋯ da linha no fim da 1ª linha.
- Sem cabeçalho de colunas.
- Total numa faixa acima dos cartões, com rótulos.

**Peça única:** `CARTOES_CSS` e `_cartoes_html` no `engine.py`; `g2cdVals` no `g2lib.js` (selo e campos). A lista própria das Atividades do plano não muda.

**Dano evitado:** cartão que parece linha de tabela, valores longe do nome e rótulo distante do valor.

**Teste:** `ds_1610_test.py` parte C (C1 reescrito: O.S., O.S. agrupada por talhão, Planejar safra, Parceiros e Produtos) e `cartoes_test.py`. Contraprova: o render anterior (cartão em linha com cabeçalho de colunas) reprova C1.

## TAB-05 · ⋯ da linha por padrão no motor

Aplicação da TAB-05 de 15/10 ("em vez desses botões soltos na tabela, coloque os 3 pontinhos") em toda grade do motor, sem depender de cada tela pedir. Detalhe em [barra-limpa-mais-acoes.md](barra-limpa-mais-acoes.md) §4.

## CAB-1 e CAB-2 nas telas fora do menu

Aplicação da PAR-01 de 16/10 ("os demais módulos estão com design system diferente do nosso padrão de excelencia do módulo agrícola") ao cabeçalho das 86 telas fora do menu, na casca comum (`ui37.shell37`):
- **CAB-1:** "‹ Módulo" (`ui37.volta_pilula`) pelo prefixo da tela, para o módulo do menu onde o assunto mora hoje (`ui37.VOLTA_PREF`): Campo, Planejamento, Irrigação e Gestão em Agrícola; Colheita, Vendas e Logística em Comercial; Suprimentos; Mapa; Portal do parceiro; Outros acessos (Onboarding e Backoffice). O caminho diz o mesmo módulo. O detalhe continua voltando à sua lista pela seta.
- **CAB-2:** fazenda, safra e parceiro saem do topo e vão para a faixa "Trabalhando em" (FIL-01), o mesmo desenho das telas do menu (`ui37.CTX_LAB`).
- A ficha impressa da OS-0424 ganha o mesmo "‹ Ficha do app" (fora da impressão).

## TAB-07 · Sem cartões de resumo: como cada tela ficou

Aplicação tela a tela da TAB-07 de 15/10. Regra de bolso usada em todas:
- contagem que a lista já mostra: sai (fica no filtro rápido ou na linha);
- o que pede atenção: vai ao selo do cabeçalho;
- soma de uma coluna: vira a linha de total;
- dado do próprio registro (assinatura, vistoria): vira pares rótulo × valor (SEP-20261015 e), sem número grande;
- tela de indicadores (Painel do módulo, Indicadores do portal): os cartões são o conteúdo e ficam.

A tabela tela a tela está no relatório da frente.
