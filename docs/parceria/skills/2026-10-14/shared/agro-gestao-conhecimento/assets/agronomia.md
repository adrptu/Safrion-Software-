# Agronomia — planejamento, manejo, solo, água, produção

## Entidades centrais
**Fazenda → Setor → Talhão (polígono, área, solo, histórico) → Zona de manejo**; **Safra** (ano-safra, cultura, cultivar/híbrido, ciclo, data de plantio, população, espaçamento, sistema: sequeiro/irrigado, plantio direto/convencional); **Operação** (tipo, data, talhão, insumos + doses, máquina, operador, condições climáticas, custo); **Colheita** (peso bruto, umidade, impurezas, peso líquido, destino, ticket de balança); **Estágio fenológico** (soja V/R, milho V/VT/R, escala BBCH); **Ocorrência** (praga, doença, daninha, nível de infestação, ponto GPS, foto).

## Planejamento de safra
- **ZARC** (Zoneamento Agrícola de Risco Climático, MAPA): janela de plantio por cultura/município/solo/ciclo — condição para crédito e Proagro. Alertar plantio fora da janela.
- **Rotação/sucessão**: histórico do talhão (cultura, cultivar, defensivos usados — rotação de mecanismos de ação IRAC/FRAC/HRAC).
- **População de plantas**: plantas/ha = (10 000 m²/ha / espaçamento entre linhas em m) × plantas/m linear; sementes/ha = população / (germinação × vigor/emergência); kg sementes/ha = sementes/ha × PMS (g) / 1000 / 1000.
  Exemplo dimensional: 10 plantas/m e 0,50 m entre linhas → 200 000 plantas/ha. Germinação e emergência são frações (0–1), com denominador positivo; ausência ou zero não permite calcular sementes/ha.
- **Graus-dia** (GD) = (Tmáx + Tmín)/2 − Tb (Tb soja 10 °C, milho 10 °C); previsão de estágios e colheita por acúmulo térmico.
- **Balanço hídrico climatológico** (Thornthwaite-Mather) para risco; **ETc = Kc × ETo** (ETo Penman-Monteith FAO-56; Kc por estágio, tabela FAO/Embrapa parametrizável).

## Solo e fertilidade
- **Análise de solo** (0–20 e 20–40 cm): pH (CaCl₂/água), M.O., P (Mehlich/resina), K, Ca, Mg, Al, H+Al, S, micros (B, Cu, Fe, Mn, Zn), argila. Derivados: **SB** = Ca+Mg+K(+Na); **CTC (T)** = SB + H+Al; **V%** = SB/T × 100; **m%** = Al/(SB+Al) × 100; relação Ca/Mg, Ca/K.
- **Necessidade de calagem (saturação por bases)**: NC (t/ha) = (V₂ − V₁) × T / PRNT, para 0–20 cm; ajustar por profundidade de incorporação (× prof/20) e pela % da área aplicada. V₂ alvo: soja/milho 60–70 %, café 60 %, pastagem 50–60 % (parametrizar por cultura/estado — RS/SC usam SMP).
- **Gessagem** (Cerrado, Sousa & Lobato): NG (kg/ha) = 50 × argila (%) [ou 6,2 × argila g/kg], quando Ca < 0,5 cmolc/dm³ ou m% > 20 % em 20–40 cm.
- **Adubação 4C** (fonte, dose, época, local certos): recomendação por tabela estadual (Boletim 100 SP, 5ª Aprox. MG, Manual RS/SC, Cerrado) → dose de N-P₂O₅-K₂O; conversão formulado: kg formulado = dose nutriente / (% no formulado/100). Adubação de sistema, parcelamento de N e K, expectativa de produtividade, exportação de nutrientes (soja ≈ 80 kg N, 15 kg P₂O₅, 40 kg K₂O por t de grão — tabela por cultura).
- **Amostragem georreferenciada** (grade ou zona) para taxa variável; mapa de fertilidade interpolado.

## Manejo fitossanitário
- **MIP/MID**: monitoramento com amostragem (pano-de-batida, armadilhas), **nível de ação / nível de dano econômico** por praga (ex. soja: percevejo 2/pano em R; lagartas 20/pano ou 30 % desfolha vegetativo, 15 % reprodutivo) — alerta quando atinge.
- **Receita agronômica na comercialização ao usuário**, emitida por profissional legalmente habilitado, ressalvadas exceções regulamentadas: [Lei 14.785/2023, art. 39 e texto consolidado](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14785.htm), consultado em 14/10/2026. A Lei 7.802/1989 foi revogada pelo art. 65; não a usar como fundamento vigente. Antes de modelar conformidade, conferir regulamentação aplicável, regras estaduais e registro/rótulo/bula atuais, inclusive enquadramento específico de bioinsumos. Controles operacionais a validar: produto registrado no MAPA (AGROFIT) para cultura × alvo, dose dentro do rótulo, **intervalo de segurança (carência)**, intervalo de reentrada, classe toxicológica, EPI, tríplice lavagem/devolução de embalagens (inpEV). Validar: cultura autorizada, dose máxima, nº máximo de aplicações, carência antes da colheita, mistura em tanque.
- **Condições de aplicação**: temperatura < 30 °C, UR > 55 %, vento 3–10 km/h (Δ-T ideal 2–8); registrar e alertar deriva.
- **Rotação de mecanismos de ação** (IRAC/FRAC/HRAC) por talhão/safra — alerta de repetição.
- **Vazio sanitário e calendário de semeadura** (soja: por estado) — validar datas.
- **Manejo de daninhas**: banco de sementes, dessecação pré-plantio, resistência (buva, capim-amargoso, caruru) — histórico por talhão.

## Água e irrigação
- **Lâmina líquida** (mm) = ETc acumulada − chuva efetiva; **lâmina bruta** = líquida / eficiência (pivô 85 %, gotejo 90–95 %, aspersão 75 %). 1 mm = 10 m³/ha.
- **Capacidade de água disponível** (CAD) = (CC − PMP) × densidade × profundidade radicular; irrigar quando esgotar a fração f (0,4–0,6).
- **Manejo por sensores** (tensiômetro, capacitivo) ou balanço; **outorga** e volume outorgado (m³/h, h/dia) — alertar consumo vs. outorga; energia (kWh/mm).
- Fertirrigação: dose por injeção, condutividade elétrica, compatibilidade.

## Colheita e produção
- **Peso corrigido** = Peso bruto × (100 − U_colheita)/(100 − U_padrão) − impurezas; padrões: soja 14 %, milho 14 %, trigo 13 %, arroz 13 %, feijão 14 %, café 11–12 % (beneficiado); desconto de impurezas acima de 1 %; **tabela de descontos** parametrizável (armazém/cooperativa).
- **Produtividade** = peso líquido / área colhida: sc/ha (60 kg; café 60 kg beneficiado; arroz 50 kg), kg/ha, t/ha, @/ha (algodão em caroço). Comparar com histórico do talhão, média regional (CONAB/IMEA) e potencial.
- **Perdas na colheita**: medição por área conhecida (copo/quadro) → kg/ha; meta soja ≤ 1 sc/ha.
- **Ponto de colheita**: umidade, maturação fisiológica (R8 soja, R6 milho), dessecação.
- **Qualidade**: classificação oficial (MAPA IN por produto: tipo, avariados, ardidos, quebrados, esverdeados), aflatoxina, PH (trigo).
- **Rastreabilidade e caderno de campo**: exigido por GlobalG.A.P., RTRS, Rainforest, ProTerra; exportar por talhão/safra.

## Culturas perenes e outras
- Café: lavoura por talhão e ano (bienalidade), poda, esqueletamento, produção em litros/sc beneficiada (rendimento ~ 480 L → 1 sc), maturação (% cereja), qualidade (bebida, peneira, defeitos). Cana: ATR, TCH (t cana/ha), TAH (t açúcar/ha), corte (ciclo 5–6 cortes), soqueira. Frutas: caixas/ha, calibre, brix. Hortaliças: ciclos curtos, colheitas múltiplas. Silvicultura: IMA (m³/ha/ano), inventário florestal.

## Indicadores agronômicos (dashboard)
| Indicador | Cálculo | Referência |
|---|---|---|
| Produtividade (sc/ha, kg/ha) | peso líquido corrigido / área colhida | histórico, média regional, potencial |
| Eficiência de uso de N/P/K | produção / nutriente aplicado | por cultura |
| Custo por saca / por ha | custo total da safra no talhão / sacas (ou ha) | CONAB |
| Índice de estande | plantas emergidas / meta | ≥ 90 % |
| % área dentro do ZARC | área plantada na janela / área total | 100 % |
| Aplicações fora de condição | nº aplicações com T/UR/vento fora / total | 0 |
| Conformidade de receituário | aplicações com receita válida / total | 100 % |
| Perdas de colheita (sc/ha) | medição em campo | ≤ 1 sc/ha soja |
| Lâmina aplicada vs. ETc | mm aplicados / mm demandados | 0,9–1,1 |
| Índice de vegetação (NDVI) por talhão | imagem de satélite/drone | tendência e anomalias |
| Ocorrências acima do nível de ação | monitoramentos ≥ NA | tempo até ação |
