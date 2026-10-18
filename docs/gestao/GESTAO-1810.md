# GESTAO-1810 · Colheita, MIP, orçamento, custos e fechamento

Pedidos do proprietário de 18/10/2026:
- "nao encontrei no sistema onde faz apontamento da colheita";
- "orçamento está muito fraco";
- "controle de pragas e doenças nao encontrei onde se define para cada alvo de cada cultura, o nivel de controle e o indicador para monitorar";
- "Composicao de custos e fechamentos também está muito fraco, use as melhores práticas e junto com codex faça algo realmente sólido e eficaz".

Autor Claude; revisor Codex (regime leve do protótipo, AGENTS §3.5: implantação começa já, a revisão não bloqueia).

## Acordo curto (AGENTS §3.4)

```text
ID / resultado útil / persona: COLH-APONT, MIP-NC, ORC-2, CUSTO-2/FECH-1 / registrar a colheita do dia, definir o NC de cada alvo, orçar e fechar o custo com origem / encarregado de colheita, RT, controller, gerente
Requisitos do PRD e fora do escopo: colheita (docs/colheita/ESPECIFICACAO.md R-02, R-06), MIP (dados_mip), custo (custo_dominio, PAINEL-02), GE-02, GE-03; fora: §Fora do escopo
Autor / revisor / integrador: Claude / Codex / Codex
Base / arquivos: claude/v44-v134 / producao.js, areas/producao.py, dados_mip.py, areas/agronomia.py, areas/cad_culturas.py, custo_dominio.py, areas/gestao.py; testes novos colh_apont_test, mip_nc_test, orc2_test, custo2_test
Aceite e comando: §6 / python3 -B <teste>_test.py; contraprova no render da v133
Estado / impedimento / próximo passo: especificado; F1 de cada item em fatias, uma por vez
```

## 1. Princípios (valem para os quatro)

1. **Um fato, um registro.**
   - Área colhida vem do apontamento da O.S. de colheita; massa vem da pesagem.
   - Custo vem do documento que o gera: consumo × preço, hora × custo-hora, nota de serviço.
   - Nada disso se digita de novo numa tela de controle (R-02 da colheita, ENG-011).
2. **Ausente não vira zero.** Preço, NC ou área ausente aparecem como pendência, com o que falta e onde resolver.
3. **Toda tela de controle leva ao documento de origem** em um toque.
4. **Unidade explícita e decimal** em dinheiro e quantidade (ENG-013).

## 2. COLH-APONT · apontamento da colheita

**Diagnóstico (código de `9c6e587c`):**
- Na web, a área colhida só se aponta pela app (MB-10, aba Colheita: "Apontar área").
- A tela do menu, Agrícola › Colheita (COLH), é previsão, programação e resultado, sem a ação de apontar.
- A antiga CO-02det, com "Apontamentos por dia", está oculta.
- Por isso o proprietário não achou.

**Prática de referência:**
- Apontamento diário por talhão (ou parcela): área colhida, horas de máquina e equipe, perdas na colheita por amostragem e umidade média.
- Produção pela pesagem das cargas, ligadas ao dia e ao talhão.
- Produtividade = produção ÷ área colhida, calculada.

**Desenho F1:**
- Em Colheita (COLH), o talhão com O.S. de colheita Liberada ou Em execução tem a primária **"Apontar colheita"**. Ela abre o painel do dia:
  - data, já com hoje;
  - área colhida (ha), com o saldo do talhão à vista;
  - horas de colhedora;
  - umidade média (%) e perdas (sc/ha), opcionais e só como registro;
  - observação.
- **Grava pelo mesmo comando da app** (`cenApontar`): mesma chave, mesma duplicidade e mesma conferência.
- **O painel mostra as cargas do dia** do talhão, com "Registrar carga ›" para o Recebimento com o talhão e o dia preenchidos.
- **Produção, produtividade e "saldo a colher"** atualizam na hora, pelas regras de hoje (R-02, R-06).
- **Lista de apontamentos do talhão,** por dia: provisório ou conferido, e quem apontou.

**Dano evitado:** colheita sem registro, com produtividade inventada ou carga sem origem.

## 3. MIP-NC · alvos, indicador e nível de controle por cultura

**Diagnóstico:** os protocolos existem só no código (`dados_mip.py`, demonstrativos), sem tela para o RT definir ou conferir.

**Prática de referência** (manejo integrado; Embrapa por cultura, a conferir a edição de cada circular):
- por cultura × alvo × estádio: método de amostragem (pano de batida, armadilha, folha, planta), unidade do indicador, **nível de controle (NC)**, nível de atenção (padrão 80 % do NC, como a regra de hoje), pontos por hectare e frequência;
- fonte e data de cada número.

**Desenho F1:**
- **Lugar:** Cadastros › Culturas (CD-02) ganha a aba **"Monitoramento (MIP)"**. Uma tabela por cultura com:
  - Alvo, Tipo (praga, doença, planta daninha) e Método;
  - Indicador (unidade), NC por estádio e Nível de atenção;
  - Pontos/ha, Frequência, Fonte e Situação.
- **Edição:** só o RT edita. A versão anterior fica no histórico. NC sem fonte aparece "Premissa a validar" (amarelo), não some.
- **Uma fonte:** o motor do MIP (`mipCls`, vistoria, mapa e Painel) passa a ler o protocolo da cultura no cadastro, e a semente é a de hoje. A Vistoria mostra "NC 15 lagartas/m (R1–R5) · fonte".
- **Em Pragas e doenças (AG-01),** o resultado de cada vistoria leva a "Protocolo: Lagarta-da-soja ›" para o cadastro.

**Dano evitado:** decisão de controle com limiar errado ou sem fonte. Ataque não detectado ou aplicação desnecessária.

## 4. ORC-2 · orçamento

**Diagnóstico:** GE-02 tem versões V1, V2 e C1 com números fixos, e os botões só dão aviso. Não liga ao Planejar safra nem ao realizado.

**Prática de referência:**
- Orçamento **por direcionador** (driver-based):
  - insumo = área × dose × preço de referência;
  - operação = área × (h/ha) × custo-hora;
  - indiretos com critério de rateio explícito.
- Por safra × cultura × talhão × natureza × mês.
- **Base aprovada congelada;** revisões em versão nova, com aprovador.
- **Previsão corrente** (*forecast*) = realizado + a realizar pelo plano.
- **Comprometido** (pedidos aprovados ainda não recebidos) separado do realizado.

**Desenho F1:**
- **GE-02 lê os mesmos números** do Planejar safra (demanda de insumos e custo de operação da etapa 3) e do custo das O.S. (`agrCustoRef`).
- **Colunas:** Orçado (base) · Comprometido · Realizado (provisório | conferido) · A realizar · Previsão · Variação · % consumido × % da área executada.
- **Quebras:** natureza (Sementes, Fertilizantes, Defensivos, Operações mecanizadas, Mão de obra, Irrigação, Colheita e frete, Indiretos) e drill até o talhão e o documento.
- **Indicadores:**
  - custo/ha;
  - custo/saca = custo ÷ produção da colheita; sem produção, "Sem produção ainda";
  - ponto de equilíbrio em sc/ha = custo/ha ÷ preço de referência;
  - margem prevista por cultura, reaproveitando a INTEL e o Comercial.
- **Versões:** "Congelar base" grava a versão com data e quem aprovou. "Criar cenário" muda premissas (preço, dose, área) e mostra o efeito, sem tocar na base.

## 5. CUSTO-2 e FECH-1 · composição de custos e fechamento

**Diagnóstico:** GE-03 traz linhas de custo fixas e um passo a passo do fechamento com pendência fixa.

**Prática de referência:**
- **Objeto de custo:** Safra › Fazenda › Cultura › Talhão (centro de resultado).
- **Centros de apoio** (máquinas, oficina, armazém, administração) rateados por direcionador: hora de máquina, área ou volume.
- **Critério com versão.**
- **Classificação** direto × indireto e variável × fixo.
- **Leitura em camadas** (IEA e CONAB; conferir as edições das metodologias):
  - custo operacional efetivo (desembolso);
  - custo operacional total (+ depreciação e mão de obra fixa);
  - custo total (+ remuneração do capital e da terra).
- **Fechamento mensal por competência,** com lista de verificação objetiva. O período fechado fica travado: correção só por ajuste com motivo no período aberto seguinte. O fechamento gerencial exporta ao ERP (financeiro no ERP, decisão de 17/10).

**Desenho F1:**
- **GE-03 Composição:** a árvore Cultura › Talhão › Natureza › Documento, com:
  - Orçado, Realizado, Variação;
  - a **ponte da variação** que fecha com o total:
    - insumos: efeito área + efeito dose (quantidade/ha) + efeito preço;
    - operações: efeito área + efeito rendimento (h/ha) + efeito custo-hora;
    - na ordem fixa área → quantidade → preço, com a regra escrita na dica;
  - O.S. de vários talhões sem apontamento por talhão em "Sem rateio", visível, nunca somada calada (regra de hoje);
  - preço ausente em "Pendente", nunca zero.
- **FECH-1 · Fechar competência** (mês), com verificações calculadas dos fatos:
  1. apontamentos do mês conferidos (conferência diária);
  2. O.S. do mês fora de "Em conferência" há mais de N dias;
  3. consumo sem preço (pendências do custo);
  4. O.S. sem rateio;
  5. recebimento sem nota ou nota sem recebimento (Suprimentos);
  6. critério de rateio do apoio com versão vigente.
- Cada verificação mostra quantos itens tem e leva a cada um.
- **"Fechar setembro/26"** só sem bloqueio. Grava um recibo com os totais por cultura e natureza e trava o mês.
- **Reabrir** exige motivo e quem decide; o recibo anterior fica.

## 6. Aceite (F1)

| ID | Caso | Oráculo |
|---|---|---|
| C1 | Colheita › Pivô 19 (OS-0505 em execução) › "Apontar colheita" 20 ha hoje | o apontamento aparece no dia, provisório; o saldo cai 20 ha; a produtividade do passe usa a nova área (R-02); a app vê o mesmo |
| C2 | Repetir o mesmo apontamento (duplo clique) | não duplica (mesma chave) |
| C3 | Talhão sem O.S. de colheita | sem a primária; o motivo e "Programar colheita ›" |
| M1 | CD-02 › Soja › Monitoramento | os alvos do protocolo atual, com NC por estádio, unidade, método, fonte |
| M2 | RT muda o NC da lagarta de 20 para 10 e salva | a vistoria que dava "abaixo do NC" passa a "acima do NC" no AG-01, no Mapa e no Painel (uma fonte) |
| M3 | NC sem fonte | "Premissa a validar" visível; a conta usa o valor e o selo avisa |
| O1 | GE-02 por cultura | orçado = previsto do plano (o mesmo do `agrCustoRef`); realizado = provisório + conferido; a soma das culturas fecha com o total |
| O2 | Congelar base e mudar uma dose no plano | a base não muda; a previsão muda; a variação mostra o efeito |
| K1 | GE-03 › Soja › T1 › Defensivos | ponte área + dose + preço = variação total (diferença ≤ R$ 0,01) |
| K2 | Fechar setembro com apontamento não conferido | bloqueado, com o item e o link |
| K3 | Tratar pendências e fechar | recibo com totais; o mês aparece travado; novo apontamento com data em setembro vai para o ajuste de outubro, com motivo |

**Contraprova:** o render da v133 não tem a primária de apontar, a aba de MIP, o orçado calculado nem as verificações calculadas.

## 7. Fatias e ordem

1. **COLH-APONT F1.** É a menor e destrava a operação.
2. **MIP-NC F1.**
3. **ORC-2 F1 + CUSTO-2 F1.** Mesma base de números, uma fatia só.
4. **FECH-1 F1.**

Cada fatia entra numa versão publicada antes da próxima, dentro do teto de três frentes (§3.6).

## 8. Fora do escopo (condição de volta)

| Item | Volta quando |
|---|---|
| Contabilidade fiscal, ativo biológico e lançamento contábil | integração com o ERP, decisão e custo do proprietário |
| Rateio automático de O.S. de vários talhões sem apontamento por talhão | regra aprovada pelo RT e pelo controller (hoje fica "Sem rateio") |
| Monitoramento por armadilha eletrônica ou imagem | fonte e contrato |
| Remuneração da terra e do capital (custo total) | taxa definida pelo proprietário |

## 9. Para o Codex (crítica pedida)

1. Ordem da ponte (área → quantidade → preço), ou média das ordens (Shapley), como no INTEL-03?
2. Fechamento: as 6 verificações bastam? Falta alguma que proteja dinheiro ou estoque?
3. MIP: o NC fica na cultura (CD-02) ou no plano agronômico? Proposta: no cadastro da cultura, com o plano só referenciando.
4. Colheita na web: algum risco de apontar pelo escritório, e não pela app, que a conferência diária não cubra?
