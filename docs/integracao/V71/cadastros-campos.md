# V71 · Cadastros: só o essencial e documentos para crédito no Crédito

Pedido do proprietário em 16/10/2026: "elimine campos dos formularios de cadastro que não sejam essenciais à gestão. documentos para credito podemos deixar tudo separado em outro lugar para nao perder foco e produtividade."

Padrão: CAD-02 em [`docs/design-system/padroes-1610-cadastros.md`](../../design-system/padroes-1610-cadastros.md).

## Critério

Cada campo teve o uso conferido por busca da chave em `areas/*.py`, `g2lib.js`, `engine.py`, nos `*.js` do gerador e nos dados (`dados*.py`).

| Decisão | Quando |
|---|---|
| **Fica** | <ul><li>Alimenta cálculo, regra, trava ou outro módulo.</li><li>É exigido por lei ou documento fiscal.</li><li>Identifica o registro, ou é coluna, filtro ou busca.</li></ul> |
| **Sai** | Não muda decisão e ninguém lê. Campo calculável também sai e passa a ser calculado (AGENTS §3.3). |
| **Move** | É documento para crédito. Vai para Crédito › Documentos para crédito (GE-08), com os mesmos dados sintéticos. |

O motor não tem seção recolhida "Mais detalhes" no formulário. Por isso nenhum campo foi para esse lugar.

## Tabela campo a campo

### CD-01 · Fazenda (painel aberto pela linha da fazenda)

| Campo | Decisão | Prova |
|---|---|---|
| Nome da fazenda | fica | Identifica a fazenda. É lido em O.S., Planejar safra e Mapa (`ocupacao_cen.py`, `ficha_pivo.py`, `talmapa.js`). |
| Empresa | fica | Situação "Empresa a informar". Dimensão Empresa da Estrutura gerencial (CD-07). |
| Município e UF | fica | 2ª linha da fazenda na lista. A UF calcula o fuso. |
| Fuso horário | **sai** (calculado) | Vem da UF (`DC.FUSO_UF`) ao salvar (`g2after` do `g_faz`). Fora do CD-01, nenhuma tela lê o campo. |
| Área total do imóvel | fica | Regra: os talhões ativos não passam dela (`talErros` e `fazErros`). Coluna "Área total". |
| Posse | fica | Situação "Posse a informar". Pede o fim do contrato. Coluna "Posse". |
| Fim do contrato | fica | Regra: contrato vencido barra o salvar até renovar ou inativar (`fazErros`). |
| Arrendador ou parceiro | **move** | Vai para o Crédito, no "Contrato de arrendamento" da Boa Vista. Só `dados_cad` e o CD-01 tinham a chave `arrend`. |
| Custo da terra | **sai** do cadastro | Nenhuma tela lê. O texto de ajuda prometia o custo por hectare, mas o custo não usava o valor. O valor (8 sc/ha/ano) segue no contrato de arrendamento do Crédito. |
| Módulos fiscais | **move** | Vai para o Crédito, no CAR da fazenda. Enquadramento de crédito; só o CD-01 lia. |
| CAR | **move** | Vai para o Crédito. A ajuda do campo dizia: "bloqueia só o crédito rural". Nenhuma regra fora do crédito. |
| Matrícula e cartório | **move** | Vai para o Crédito. Nenhuma tela lia. |
| Pendência nos documentos | **move** | Vai para o Crédito, na pendência do documento. "Não bloqueia o planejamento." |
| Perímetros, Restrição ambiental, Recursos hídricos (só leitura, Lagoa Grande) | **sai** | Repetiam as abas Ambiental e Água do mesmo CD-01. |
| Situação | fica | Regra: fazenda inativa sai do Planejar safra. |

### CD-01 · Talhão

Todos os campos **ficam**:
- Identificação, Fazenda, Sistema, Pivô ou setor e Área cultivável alimentam regras (`talErros`) e o balanço hídrico.
- Área do polígono e Geometria são só leitura.
- Motivo da diferença é exigido acima de 1 %.
- Situação é regra.

### CD-02 · Cultivar e cultura

Todos **ficam**:
- Cultura e cultivar identificam o registro.
- Ciclo e Item de semente vão para o Planejar safra, Compras e Estoque.
- Registro (RNC ou cadastro próprio) é legal: RNC/MAPA.
- Unidade de produtividade é a meta do Planejar safra.
- Situação é regra.

### CD-03 · Máquina ou instalação e conjunto

| Campo | Decisão | Prova |
|---|---|---|
| Responsável técnico (só leitura, da Manutenção) | **sai** | Não muda decisão no cadastro. Segue na Manutenção, aberta pelo link "Abrir … na Manutenção" do painel. |

Ficam:
- Classe, Nome e Modelo (identificam).
- Condição técnica: trava que vem da Manutenção.
- Capacidades: potência mínima, largura, tanque da ficha do caldeiro, vazão.
- Custo R$/h e Fonte: rendimento e custo da O.S.
- Horímetro: leitura da Manutenção.
- Calibração: regra.
- Local: Manutenção.
- Situação.
- No conjunto, todos os campos ficam.

### CD-04 · Pessoa e equipe

| Campo | Decisão | Prova |
|---|---|---|
| Calendário de trabalho (da pessoa) | **sai** | Nenhuma tela lia o calendário da pessoa: a jornada e a capacidade usam o da equipe. A ajuda do campo Equipe mostra o calendário dela. |

Ficam:
- Nome, Equipe e Habilidades.
- Validades NR-31, NR-10, NR-12 e CREA: lei, e regra de alocável em O.S.
- Vínculo: regra do "Disponível até".
- Admissão: regra de alocável.
- Disponível até.
- Custo-hora: custo da O.S.
- Situação.
- Na equipe, todos os campos ficam.

### CD-05 · Parceiro

| Campo | Decisão | Prova |
|---|---|---|
| Produtos de interesse (Cliente) | **sai** | Nenhuma tela lia. Não era coluna nem regra. |
| Local e horário de entrega (Cliente) | **sai** | Nenhuma tela lia. O pedido de venda e a Logística têm os próprios. |
| Condição de pagamento (Cliente) | **sai** | Nenhuma tela lia o valor do parceiro. Vendas usa a condição do pedido (`dados_comercial.py` lê só a lista de opções). |
| Garantias aceitas (Parceiro de crédito) | **sai** | Nenhuma tela lia. A garantia é de cada solicitação ou contrato, no Crédito (GE-08, coluna Garantia). A coluna do filtro "Parceiros de crédito" também saiu. |
| Gerente do crédito, e-mail e telefone do gerente | **sai** | Repetiam o contato do parceiro (nome, e-mail e WhatsApp). Nenhuma tela lia. |

Ficam:
- CPF/CNPJ: lei e registro único.
- Nome e Papéis.
- Contato, E-mail, WhatsApp e Canais: regras da cotação.
- Grupos e Homologado: cotação.
- Limite de crédito comercial e validade: regra "Limite vencido" e colunas.
- Linhas de crédito: situação do papel e coluna.
- RNTRC: lei, ANTT.
- Veículos: coluna.
- Operações que presta: situação e coluna.
- Motivo da suspensão.

### CD-06 · Item, grupo e local

Todos **ficam**:
- Unidade-base: dose, compra e estoque.
- Embalagem e conteúdo: regra.
- Controle: lote e validade no Estoque.
- Preço e data: custo do plano e cotação, com regra.
- Garantia ou densidade: rótulo e registro do produto. O Solo usa a garantia (`DC.GARANTIA`).
- Local padrão: o recebimento sugere.
- Situação.

### CD-07 · Código

Todos **ficam**:
- Hierarquia e vigência.
- Rateio.
- Tradução, conta e TOP: publicação no ERP.
- Origem e Vínculos são só leitura: explicam a trava e o impacto.

### CD-08 · Rendimento e operação

Todos **ficam**:
- O cálculo do rendimento e do custo (`REND_CAMPOS`) é o mesmo do Planejar safra.
- Fonte: a premissa a validar é pendência.
- Processo e Atividades usuais vão para os Planos.

## Documentos para crédito (Crédito › Documentos para crédito)

- **Onde fica:**
  - `GE-08.dc.html#vis=documentos`, nova visão do Crédito, também no menu e na tela de entrada (cartão "Documentos");
  - grade do motor com Tabela | Cartões e filtro rápido pela Situação;
  - uma linha por documento e fazenda (ou parceiro).
- **Fonte:** os mesmos dados sintéticos de `dados_cad.FAZENDAS` e a condição documental do CRE-0102 (certidão exigida pelo Banco Terra). Nada se perdeu.

| Documento | Fazenda | Dado |
|---|---|---|
| CAR | Santa Rita | Recibo `GO-5218805-…` · registrado |
| Matrícula | Santa Rita | 12.401 · CRI de Rio Verde |
| Certidão de matrícula atualizada | Santa Rita | Exigida por Banco Terra · CRE-0102 · pendente (em conferência depois do envio) |
| CAR | Boa Vista | Pendente (em branco no cadastro) |
| Matrícula | Boa Vista | 8.421 · CRI de Sorriso |
| Contrato de arrendamento | Boa Vista | Arrendador, 8 sc/ha/ano, até 31/08/2029 · pendente: sem registro em cartório |
| CAR | Lagoa Grande | Recibo do KML (sintético) · 38,6 módulos fiscais |
| Matrícula | Lagoa Grande | Pendente |

- **No cadastro:** sobrou só o vínculo discreto "Documentos para crédito ›", no painel da fazenda (CD-01).
- **Ficaram no CD-01, porque a regra os usa:**
  - a outorga de água (aba Água: a Irrigação usa, CTL-5);
  - a restrição ambiental (aba Ambiental, consulta do CAR).

## Verificação

`cadastros_padrao_test.py`, partes P6a a P6e:
- formulários sem os campos que saíram;
- Crédito com os documentos e os mesmos números de `dados_cad`.

Os testes de cadastro com oráculo ajustado a esta mudança são:
- `cadp_test`;
- `cada_cd03_test`;
- `cada_cd04_test`;
- `cadf_test`;
- `credito_menu_test`.
