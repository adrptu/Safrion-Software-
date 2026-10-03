# Engenharia Agrícola — máquinas, operações, pós-colheita, precisão

## Entidades
**Máquina/implemento** (tipo, marca, modelo, ano, potência, largura útil, horímetro/odômetro, valor de aquisição, vida útil, valor residual); **Operação mecanizada** (máquina + implemento, talhão, área, início/fim, horas, combustível, operador, velocidade, regulagens); **Abastecimento**; **Ordem de serviço** (manutenção — ver engenharia-producao-mecanica.md); **Telemetria** (posição, rpm, consumo, alarmes, ISOBUS).

## Capacidade e dimensionamento
- **Capacidade de campo teórica** CcT (ha/h) = largura (m) × velocidade (km/h) / 10.
- **Capacidade efetiva** CcE = CcT × eficiência de campo (Ef: plantio 60–75 %, pulverização 55–65 %, colheita 65–80 %, preparo 75–85 %).
- **Horas necessárias** = área / CcE; **dias** = horas / (h/dia × dias úteis prováveis — descontar chuva pela série histórica).
- **Dimensionamento de frota**: nº máquinas = área / (CcE × h/dia × dias disponíveis na janela de operação). Alertar quando a janela (ZARC, ponto de colheita) não fecha.
- **Potência requerida** (kW) = força de tração (kN) × velocidade (m/s) / eficiência tratória; relação peso/potência 45–55 kg/cv (preparo) a 35–40 (transporte); **patinagem** ideal 8–15 % (pneu) — telemetria.
- **Velocidade** por operação: semeadura 4–7 km/h (precisão), pulverização 8–20, colheita 4–8.

## Custo horário de máquina (base ASABE / Embrapa)
Custos fixos (por hora):
- **Depreciação** = (Vi − Vr) / (vida útil em horas); Vr ≈ 10–20 % Vi; vida útil trator 10 000–12 000 h, colhedora 3 000–4 000 h, implemento 2 000–2 500 h.
- **Juros sobre capital** = ((Vi + Vr)/2 × taxa a.a.) / horas por ano.
- **Abrigo, seguro e taxas** = 1–2 % Vi / horas por ano.
Custos variáveis (por hora):
- **Combustível** = consumo (L/h) × preço; estimativa 0,15–0,20 L/cv/h × carga; medir real por abastecimento/telemetria.
- **Lubrificantes** = 10–15 % do combustível. **Reparos e manutenção** = fator RM (30–100 % Vi ao longo da vida) / horas de vida. **Pneus** separadamente.
- **Operador** = salário + encargos (≈ 1,8–2,0×) / horas produtivas.
**Custo/ha da operação** = custo horário (trator + implemento) / CcE. Comparar com **terceirização** (R$/ha de mercado).

## Semeadura e plantio
- Regulagem: população, profundidade (soja 3–5 cm, milho 3–5), espaçamento; **distribuição longitudinal** (CV % de espaçamento entre sementes, meta < 20–25 %; duplas/falhas). Dosador (vácuo/disco), velocidade limitada, adubo no sulco.
- Cálculo de disco/engrenagem: sementes por metro = população / (10 000 / espaçamento m); relação de transmissão conforme catálogo.

## Pulverização
- **Volume de calda** (L/ha) = (vazão por bico L/min × 600) / (velocidade km/h × espaçamento entre bicos m) — calibrar antes de cada produto/lote; verificar bicos (vazão ± 10 % da média).
- **Quantidade de produto** = dose (L ou kg/ha) × área; **por tanque** = dose × (capacidade tanque / volume de calda).
- Escolha de ponta pela classe de gota (ASABE S572: fina a extra grossa) × alvo e produto; pressão dentro da faixa; altura da barra (50 cm); **deriva** (Δ-T, vento); **mapa de aplicação** com seção/bico automático e sobreposição (%).
- Rastro: registrar seções ligadas, taxa aplicada real vs. prescrita; drone (UAV) — MAPA/DECEA, faixa e altura.

## Colheita
- Regulagem: velocidade do cilindro/rotor, abertura côncavo, ventilador, peneiras; **perdas** (plataforma, trilha, separação) medidas em kg/ha com quadro (2 m² → × 5 000) — soja meta ≤ 60 kg/ha; grãos quebrados/avariados.
- Monitor de produtividade: calibração de fluxo e umidade; **mapa de produtividade** (limpeza de outliers, atraso de fluxo) → zonas de manejo.
- Logística de colheita: capacidade de tanque graneleiro, graneleiro auxiliar, caminhões, tempo de ciclo; fila e ociosidade da colhedora (gargalo).

## Pós-colheita e armazenagem
- **Recepção**: ticket de balança, umidade, impurezas, classificação; **desconto** e peso líquido; romaneio por produtor/talhão.
- **Secagem**: umidade inicial → final (ex. 18 → 14 %); água a remover (kg) = massa × (Ui − Uf)/(100 − Uf); temperatura de secagem por uso (semente ≤ 40 °C, grão consumo até 80–100 °C na massa ≤ 45); consumo de lenha/GLP (energia por ponto de umidade).
- **Aeração**: com base na umidade de equilíbrio (temperatura e UR do ar) — tabelas por grão; termometria (cabos) com alerta de aquecimento; **umidade de armazenamento segura** soja/milho 13–14 %; controle de pragas (expurgo com fosfina — registro e responsável), quebra técnica (0,5–1 %/mês).
- Estoque por silo/lote: entradas, saídas, estoque físico vs. fiscal, fixação de preço (grão a fixar).

## Agricultura de precisão e telemetria
- Ciclo completo de AP (amostragem, zonas de manejo, prescrição VRT, as-applied, avaliação), satélite/drone e georreferenciamento: ver **geo-precisao.md**.
- Na máquina: piloto automático RTK com linhas AB por talhão, controle de seções e de taxa (formatos ISOXML/Shapefile do fabricante), sobreposição < 5 %.
- Telemetria: horas motor vs. horas efetivas (eficiência), consumo L/ha, rpm/carga, alarmes, localização; **eficiência operacional** = horas efetivas / horas totais; importação automática via API do fabricante (John Deere Ops Center, FieldView, AGCO, CNH, Solinftec).

## Irrigação (hidráulica)
- Pivô central: vazão (m³/h), lâmina por volta (mm) = vazão × tempo / (área × 10); percentímetro ↔ lâmina; **CUC (Christiansen) ≥ 85 %**, CUD; pressão e bocais (teste de uniformidade); energia (kWh/mm/ha) e demanda contratada; horário de tarifa (verde/azul).
- Gotejamento: vazão emissor, espaçamento, CUD, filtragem, entupimento; bombeamento: potência (kW) = Q (m³/s) × H (m) × 9,81 / η.

## Construções e energia rurais
- Dimensionamento de galpões, silos (capacidade t = volume × densidade aparente: soja 0,75, milho 0,75, trigo 0,78 t/m³), curral, sala de ordenha, esterqueira (NBR, licenciamento); fotovoltaica (kWp, geração, compensação), biodigestor (m³ biogás por t dejeto), custo de energia por atividade.

## Indicadores
| Indicador | Cálculo | Meta/ref. |
|---|---|---|
| Custo horário e por ha por máquina | fórmulas acima | vs. terceirização |
| Eficiência de campo | CcE real / CcT | por operação |
| Eficiência operacional (telemetria) | h efetivas / h motor | ≥ 70 % |
| Consumo L/ha por operação | combustível / área | histórico |
| Sobreposição de aplicação | % área aplicada 2× | < 5 % |
| Uniformidade de irrigação (CUC) | teste de campo | ≥ 85 % |
| Perdas de colheita | kg/ha medidos | ≤ 60 kg/ha soja |
| CV de distribuição de sementes | desvio de espaçamento | < 25 % |
| Disponibilidade mecânica | (h disponíveis − h parada)/h disponíveis | ≥ 90 % |
| Aplicação real vs. prescrita | erro médio | ± 5 % |
