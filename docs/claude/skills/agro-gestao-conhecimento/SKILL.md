---
name: agro-gestao-conhecimento
description: Aplique entidades, unidades, cálculos e referências agro à modelagem e revisão de gestão rural. Use em safra, talhão, insumos, máquinas, estoque, custos, pecuária e indicadores; valide normas e recomendações nas fontes pertinentes.
---

# Conhecimento aplicado: agro + gestão

**Norte:** apoiar decisões com cálculos rastreáveis, unidades corretas e linguagem do produtor. Referências deste skill são ponto de partida, não prescrição nem validação vigente. Conferir fonte, cultura/estádio, região, premissas e responsabilidade técnica antes de incorporar recomendações materiais.

## Como aplicar
1. **Mapear cada módulo às disciplinas** (tabela abaixo) e ler os arquivos correspondentes antes de modelar dados ou telas.
2. **Modelar com as entidades e unidades do setor** (safra, talhão, lote, categoria animal, sc, @, ha, L/ha) — nunca genéricos.
3. **Embutir fórmulas e validações** dos arquivos como regras do domínio, com teste unitário para cada (`dev-testes`): cálculo errado de calagem, umidade ou custo é bug grave.
4. **Selecionar indicadores que resolvem a tarefa da fatia**, com origem, período, unidade e base de comparação válida; não inventar benchmark nem adicionar painel sem decisão concreta.
5. **Fontes oficiais como referência** (Embrapa, CONAB, MAPA, CEPEA/Esalq, IMEA, B3, CFM/NRC, Receita Federal, CPC). Valores legais/fiscais e alíquotas mudam: marcar `verificar vigência` e parametrizar no sistema (nunca hardcode).
6. **Benchmark do setor** (`benchmark-top5`): referências típicas — Aegro, Climate FieldView, John Deere Operations Center, Solinftec, Siagri/Totvs Agro, Datacoper/Agrimanager, Prodap, JetBov, Conta Azul, Omie. UX segue `ux-essencial` e a organização das telas segue `master-detail-ux`.

| Módulo do software | Disciplinas / arquivo |
|---|---|
| Planejamento de safra, talhões, manejo, solo, irrigação, produtividade, rastreabilidade | [agronomia.md](assets/agronomia.md) |
| Máquinas, operações mecanizadas, pulverização, colheita, armazenagem | [engenharia-agricola.md](assets/engenharia-agricola.md) |
| Agricultura de precisão (zonas de manejo, taxa variável, as-applied), satélite/drone/índices (NDVI…), georreferenciamento (SIRGAS 2000, GNSS/RTK, PostGIS), agrimensura e cadastro rural (SIGEF, CAR, CCIR, ITR, topografia), clima | [geo-precisao.md](assets/geo-precisao.md) |
| Manutenção, oficina, frota, peças, motores, telemetria, processos, qualidade, estoque, logística | [engenharia-producao-mecanica.md](assets/engenharia-producao-mecanica.md) |
| Pecuária de corte, leite, suínos, aves, pastagem, nutrição, reprodução, sanidade | [zootecnia.md](assets/zootecnia.md) |
| Custos, financeiro, contábil, fiscal, patrimônio, orçamento, indicadores econômico-financeiros | [contabilidade-financas.md](assets/contabilidade-financas.md) |
| Estratégia, comercialização, mercado, crédito rural, seguro, risco, pessoas, investimento | [administracao-economia.md](assets/administracao-economia.md) |

## Regras transversais de modelagem
- **Ano-safra ≠ ano civil**: operações agrícolas se vinculam à safra/cultura/talhão quando aplicável; despesas corporativas podem precisar de centro de custo e rateio, sem inventar talhão. Distinguir ciclos e safras conforme o modelo vigente.
- **Unidades explícitas e conversíveis** em todo campo numérico: `kg`, `sc 60 kg`, `sc 50 kg` (café), `@ (15 kg)`, `t`, `ha`, `alq` (paulista 2,42 ha; mineiro 4,84 ha), `L`, `L/ha`, `kg/ha`, `cab`, `UA (450 kg PV)`. Conversão centralizada e testada.
- **Área e posição**: talhão georreferenciado (polígono em **SIRGAS 2000**, SRID declarado, PostGIS, geometria válida e sem sobreposição), área calculada em projeção métrica vs. área declarada; hierarquia fazenda → imóvel (matrícula/CAR/SIGEF) → setor → talhão → zona de manejo; camadas de restrição (APP, reserva legal) bloqueiam operações; todo dado de campo tem GPS + precisão + horário (ver geo-precisao.md).
- **Produção com umidade e impurezas**: armazenar bruto, umidade, impurezas e peso líquido corrigido ao padrão.
- **Rastreabilidade por processo**: manter data, responsável, origem e destino e vínculos necessários. Aplicação de insumo, movimentação animal e colheita têm campos e exigências diferentes; verificar normas atuais pertinentes antes de torná-los obrigatórios.
- **Categorias animais** por espécie/sexo/idade/fase; movimentações (nascimento, compra, transferência, venda, morte, mudança de categoria) fecham o inventário mensal.
- **Estoque de insumos** por depósito, lote e validade; baixa automática pela aplicação; saldo nunca negativo (alerta antes).
- **Custos rateados** com critério declarado (ha, horas-máquina, cabeça, litro) e auditável; toda operação gera custo (insumo + máquina + mão de obra).
- **Indicadores sempre com contexto**: valor, meta, benchmark regional/histórico, tendência e drill-down até a operação (`tabelas-interativas`).
- **Parâmetros técnicos editáveis** (tabelas de Kc, exigências nutricionais, PRNT, alíquotas, preços de referência) versionados, com valor padrão de fonte oficial.
- **Offline-first** no campo, GPS, fotos, leitura de código de barras/QR (`dev-frontend-mobile`).

## Checklist por módulo
- [ ] Entidades, unidades e vocabulário do setor (glossário no `docs/benchmark.md`)
- [ ] Fórmulas dos arquivos implementadas como funções puras com testes (inclusive limites e arredondamento)
- [ ] Validações de domínio ativas (carência, dose máxima, estoque, umidade, idade/categoria, prazos fiscais)
- [ ] Indicadores da fatia com origem, período e base de comparação válida
- [ ] Parâmetros técnicos/legais parametrizados e com fonte
- [ ] Custos ligados a safra/talhão/lote com rateio auditável
- [ ] Rastreabilidade exigida pelo processo, com a norma vigente conferida
- [ ] Textos na linguagem do produtor/gestor (sem jargão de TI)
