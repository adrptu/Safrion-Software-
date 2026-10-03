# Engenharia de Produção e Mecânica — processos, manutenção, estoque, qualidade

## Gestão de processos (Lean)
- **Mapear fluxo de valor** (VSM) das operações críticas (plantio, colheita, ordenha, recebimento, oficina): tempo de ciclo, esperas, gargalo. **8 desperdícios**: superprodução, espera, transporte, excesso de processo, estoque, movimento, defeito, talento. Cada tela de operação deve reduzir um deles.
- **Takt time** = tempo disponível / demanda; **lead time**; **gargalo (TOC)**: identificar → explorar → subordinar → elevar. Ex.: colhedora esperando caminhão = gargalo na logística.
- **5S**, **kaizen** (registro de melhorias com ganho medido), **padronização** (procedimento operacional padrão — POP com checklist no app), **kanban** para peças e insumos, **PDCA/DMAIC** para problemas recorrentes, **A3**.
- **Planejamento e controle (PCP)**: plano mestre por safra → ordens de operação por talhão/semana → sequenciamento por janela e recursos (máquinas, pessoas, insumos) → apontamento real → replanejamento. Programação por capacidade finita; alerta de conflito de recurso.
- **Gestão visual**: quadro de operações do dia/semana, andon (parada de máquina), metas visíveis.

## Manutenção (foco: máquinas e instalações agrícolas)
- Estratégias: **corretiva** (evitar), **preventiva** (por horímetro/km/tempo — plano do fabricante parametrizado: 10/50/250/500/1000 h), **preditiva** (análise de óleo, vibração, termografia, telemetria de alarmes), **TPM** (operador faz inspeção diária: checklist pré-operacional com foto).
- **Ordem de serviço**: máquina, tipo, sintoma, causa, peças, mão de obra, horas parada, custo, técnico, horímetro; **histórico por equipamento** e por componente.
- Indicadores: **MTBF** = h operação / nº falhas; **MTTR** = h reparo / nº falhas; **Disponibilidade** = MTBF/(MTBF+MTTR); **custo de manutenção / valor de reposição** (meta 2–5 % a.a.); **% preventiva vs. corretiva** (meta ≥ 70 % preventiva); **backlog** de OS; **aderência ao plano**.
- **OEE** = Disponibilidade × Desempenho × Qualidade (colhedora: h efetivas/h programadas × CcE real/CcE padrão × produto sem perdas/total); meta world-class 85 %.
- **FMEA** para falhas críticas em janela (colhedora, pivô, ordenhadeira, secador): severidade × ocorrência × detecção → RPN → ação.
- Alertas automáticos: preventiva vencendo (por horímetro da telemetria), garantia, revisão, licenças (CIV/CRLV, ANTT, tacógrafo, NR-12).

## Mecânica aplicada
- **Motores diesel**: potência (cv/kW: 1 cv = 0,7355 kW), torque, rotação, **consumo específico** (g/kWh ≈ 200–250 → L/h = kW × cee / (densidade 840 g/L)); curva de carga; Tier 3/MAR-I; aditivo Arla 32; combustível: qualidade, água, filtragem, tanques (registro de abastecimento e reconciliação).
- **Transmissão e hidráulica**: TDP (540/1000 rpm), fluxo hidráulico (L/min) × implemento, pressão; fluidos e intervalos; contaminação (ISO 4406).
- **Lubrificação**: plano por ponto (graxa/óleo, periodicidade, quantidade); análise de óleo (viscosidade, metais de desgaste, silício = poeira, água, TBN).
- **Pneus e rodados**: pressão por carga/velocidade (tabela), lastro, compactação; rastreio de vida útil.
- **Desgaste e vida útil**: componentes de desgaste (facas, discos, ponteiras, correias, rolamentos) por hora/ha; ponto de troca por medição; estoque mínimo por criticidade.
- **Segurança**: NR-12 (proteções), NR-31 (trabalho rural, EPI, capacitação, agrotóxicos), NR-35, cabine/ROPS, checklist de bloqueio (LOTO), acidentes e quase-acidentes registrados (taxa de frequência/gravidade).

## Estoque e suprimentos
- **Classificação ABC** (valor) × **XYZ** (variabilidade de consumo) × **criticidade**; política por classe.
- **Ponto de pedido** = demanda diária × lead time + estoque de segurança; **ES** = z × σ_demanda × √LT; **EOQ** = √(2·D·S/H).
- **Giro** = consumo anual / estoque médio; **cobertura (dias)** = estoque / consumo diário; **acurácia de inventário** (meta ≥ 98 %); **ruptura**.
- Insumos agrícolas: compra antecipada (barter/troca por grão), lotes e validade (defensivos, sementes: germinação com validade), armazém de agrotóxicos (NBR 9843), FISPQ, devolução de embalagens; **peças**: código do fabricante, aplicação por máquina, equivalentes.
- Recebimento: conferência × pedido × NF (3-way match); divergências; qualidade (laudo de semente, análise de fertilizante).

## Logística
- Transporte de grãos: ciclo (carregamento, viagem, fila, descarga), R$/t·km, capacidade (t/viagem), roteirização; frete (CT-e, MDF-e), tabela ANTT piso mínimo; sazonalidade e contratação.
- Transporte de animais: GTA, densidade por caminhão, tempo de viagem, bem-estar; leite: rota de coleta, temperatura, tempo até resfriar (≤ 3 h) e coletar.
- Armazéns e pátios: capacidade estática vs. dinâmica, fila de caminhões (tempo médio, meta), programação de descarga.

## Qualidade
- **CEP** (cartas de controle) para processos repetitivos: umidade na secagem, CCS/CBT do leite, peso de carcaça, distribuição de sementes; **capacidade de processo** (Cp, Cpk ≥ 1,33).
- **Não conformidades** registradas com causa raiz (5 porquês, Ishikawa) e ação corretiva; **auditorias** (checklists de certificação: GlobalG.A.P., BPF, HACCP em laticínio/frigorífico, Rainforest, RTRS).
- Custo da qualidade: prevenção, avaliação, falhas internas/externas (descontos por umidade, devoluções).

## Indicadores
| Indicador | Cálculo | Meta |
|---|---|---|
| OEE por máquina crítica | D × P × Q | ≥ 85 % |
| MTBF / MTTR / disponibilidade | ver acima | disponibilidade ≥ 90 % |
| % manutenção preventiva | h preventiva / h total manutenção | ≥ 70 % |
| Custo de manutenção / valor de reposição | anual | 2–5 % |
| Aderência ao plano de operações | operações no prazo / planejadas | ≥ 90 % |
| Ociosidade de gargalo | h parada da colhedora por espera / h totais | < 10 % |
| Giro e cobertura de estoque | ver acima | por classe ABC |
| Acurácia de inventário | itens corretos / contados | ≥ 98 % |
| Ruptura de insumo crítico | ocorrências na safra | 0 |
| Taxa de frequência de acidentes | acidentes × 10⁶ / HHT | tendência ↓ |
| Cpk dos processos-chave | estatístico | ≥ 1,33 |
| Custo por t·km / por viagem | frete + ciclo | benchmark regional |
