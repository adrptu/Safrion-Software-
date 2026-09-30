# -*- coding: utf-8 -*-
"""Catálogo nativo de Operações → Atividades por grupo de cultura.
Padrão de referência: estrutura de custos CONAB/Embrapa (correção e preparo → plantio → tratos culturais →
colheita → pós-colheita), capacidade de campo ASABE D497 (CcT = largura × velocidade × eficiência ÷ 10),
Sistemas de Produção Embrapa (Soja, Milho, Feijão, Algodão, Trigo), IAC/Centro de Tecnologia Canavieira (cana),
Embrapa Café/Procafé (café), Embrapa Fruticultura e Embrapa Hortaliças (frutas e HF), FAO-56 (irrigação),
MIP/MID Embrapa (níveis de ação). Tudo é padrão editável: a fazenda muda máquina, rendimento, insumo e gatilho.
Atividade = (nome, máquina padrão, implemento, rendimento padrão, insumo padrão, unidade, gatilho padrão, observação técnica)
"""
GRUPOS = ['Grãos', 'Cana', 'Café', 'Frutas', 'HF']
FASES = ['1 · Diagnóstico e amostragem', '2 · Correção e preparo do solo', '3 · Plantio e implantação',
         '4 · Tratos culturais', '5 · Irrigação', '6 · Colheita', '7 · Pós-colheita e beneficiamento', '8 · Manutenção da lavoura']

CAT = {
 'Grãos': [
  ('1 · Diagnóstico e amostragem', 'Amostragem de solo', 'Quadriciclo + trado', None, '20 ha/h', '—', '—', 'DAC +10 (pós-colheita)', 'grade de 1 amostra/2–5 ha ou por zona; 0–20 e 20–40 cm; 15–20 subamostras', [
     ('Amostragem em grade', 'Quadriciclo', 'Trado hidráulico', '20 ha/h', '—', '—', 'DAC +10', 'GPS por ponto; laudo válido 24 meses (12 em irrigado)'),
     ('Amostragem por zona de manejo', 'Quadriciclo', 'Trado', '25 ha/h', '—', '—', 'DAC +10', 'zonas por NDVI e histórico de produtividade'),
     ('Amostragem 20–40 cm (gesso)', 'Quadriciclo', 'Trado', '15 ha/h', '—', '—', 'DAC +10', 'decisão de gessagem: Ca < 0,5 cmolc/dm³ ou m > 20 %')]),
  ('1 · Diagnóstico e amostragem', 'Vistoria e monitoramento', 'Manual (GPS)', None, '1 ponto/10 ha', '—', '—', 'semanal, DAP 15 → DAC', 'MIP/MID Embrapa: pano-de-batida, armadilhas, nível de ação por alvo', [
     ('Vistoria de pragas (pano-de-batida)', 'Manual', 'Pano-de-batida', '1 ponto/10 ha', '—', '—', 'semanal DAP 15→DAC', 'nível de ação: lagarta 20/pano · percevejo 2/pano (R1–R7)'),
     ('Vistoria de doenças', 'Manual', '—', '1 ponto/10 ha', '—', '—', 'semanal DAP 30→DAC', 'ferrugem: primeira pústula dispara fungicida'),
     ('Amostragem foliar', 'Manual', '—', '1 amostra/talhão', '—', '—', 'DAP 45–60 (R1)', '3º trifólio sem pecíolo · 30 plantas'),
     ('Conferência de estande', 'Manual', 'Trena', '3 pontos de 2 m', '—', '—', 'DAP 7–14', 'stand < 70 % → replantio da mancha')]),
  ('2 · Correção e preparo do solo', 'Calagem', 'Trator 120 cv', 'Distribuidor de calcário 6 t', '8 ha/h', 'Calcário dolomítico PRNT 80', 't/ha', 'DAP −90 a −60', 'dose pela saturação por bases (V2 por cultura/UF) · incorporar ou superfície em SPD (≤ 3 t/ha)', [
     ('Calagem a lanço', 'Trator 120 cv', 'Distribuidor 6 t', '8 ha/h', 'Calcário PRNT 80', 't/ha', 'DAP −90', 'largura 10 m · 8 km/h · ef. 0,8'),
     ('Calagem em taxa variável', 'Trator 120 cv', 'Distribuidor com controlador', '7 ha/h', 'Calcário PRNT 80', 't/ha', 'DAP −90', 'prescrição por célula (Shapefile/ISOXML)')]),
  ('2 · Correção e preparo do solo', 'Gessagem', 'Trator 120 cv', 'Distribuidor 6 t', '8 ha/h', 'Gesso agrícola', 'kg/ha', 'DAP −60', 'NG = 50 × argila % (20–40 cm) em anuais · junto ou após o calcário', [
     ('Gessagem a lanço', 'Trator 120 cv', 'Distribuidor 6 t', '8 ha/h', 'Gesso agrícola', 'kg/ha', 'DAP −60', 'antes das chuvas')]),
  ('2 · Correção e preparo do solo', 'Fosfatagem corretiva', 'Trator 120 cv', 'Distribuidor 6 t', '8 ha/h', 'Superfosfato simples / fosfato natural', 'kg/ha', 'DAP −60', 'P muito baixo/baixo: corretiva total ou gradual (Sousa & Lobato 2004)', [
     ('Fosfatagem a lanço', 'Trator 120 cv', 'Distribuidor 6 t', '8 ha/h', 'SSP 18 %', 'kg/ha', 'DAP −60', 'fosfato natural reativo antes da calagem; solúvel após')]),
  ('2 · Correção e preparo do solo', 'Preparo do solo', 'Trator 180 cv', 'Subsolador / grade', '1,2–2,2 ha/h', '—', '—', 'DAP −60 a −30', 'só fora do SPD consolidado; subsolagem quando há camada compactada (penetrômetro > 2 MPa)', [
     ('Subsolagem / escarificação', 'Trator 180 cv', 'Subsolador 5 hastes 3 m', '1,2 ha/h', '—', '—', 'DAP −60', '3 m · 5 km/h · ef. 0,8'),
     ('Gradagem pesada', 'Trator 180 cv', 'Grade aradora 4 m', '2,2 ha/h', '—', '—', 'DAP −45', '4 m · 7 km/h · ef. 0,8'),
     ('Gradagem niveladora', 'Trator 120 cv', 'Grade niveladora 6 m', '3,6 ha/h', '—', '—', 'DAP −30', '6 m · 7,5 km/h · ef. 0,8'),
     ('Terraceamento / manutenção de terraços', 'Trator 180 cv', 'Terraceador', '1 ha/h', '—', '—', 'DAC +15', 'conservação de solo (NBR/Embrapa)')]),
  ('3 · Plantio e implantação', 'Dessecação', 'Pulverizador autopropelido 24 m', 'Barra 24 m · bicos leque', '25 ha/h', 'Glifosato 480 + 2,4-D', 'L/ha', 'DAP −20 e −7 (sequencial)', 'janela: vento 3–10 km/h · UR ≥ 55 % · T ≤ 30 °C · intervalo 2,4-D → soja ≥ 7 dias', [
     ('Dessecação pré-plantio (1ª)', 'Pulverizador 24 m', 'Barra 24 m', '25 ha/h', 'Glifosato 480', 'L/ha', 'DAP −20', '24 m · 15 km/h · ef. 0,7 · 100–150 L/ha de calda'),
     ('Dessecação sequencial (2ª)', 'Pulverizador 24 m', 'Barra 24 m', '25 ha/h', 'Paraquate-substituto / diquate', 'L/ha', 'DAP −7', 'buva e capim-amargoso: sequencial obrigatória'),
     ('Dessecação pós-colheita (tiguera)', 'Pulverizador 24 m', 'Barra 24 m', '25 ha/h', 'Glifosato 480', 'L/ha', 'DAC +10', 'antes do vazio sanitário da soja')]),
  ('3 · Plantio e implantação', 'Tratamento de sementes', 'Máquina de TS on-farm', '—', '40 sc/h', 'Fungicida + inseticida + inoculante', 'mL/100 kg', 'DAP −2', 'TSI de fábrica ou on-farm; inoculante Bradyrhizobium ≥ 1,2 × 10⁶ cél./semente', [
     ('Tratamento on-farm', 'Máquina de TS', '—', '40 sc/h', 'Fungicida + inseticida', 'mL/100 kg', 'DAP −2', 'compatibilidade com inoculante'),
     ('Inoculação e Co/Mo', 'Máquina de TS', '—', '40 sc/h', 'Inoculante + Co/Mo', 'dose/sc', 'DAP −1', 'Mo 12–30 g/ha · Co 2–3 g/ha')]),
  ('3 · Plantio e implantação', 'Plantio', 'Trator 180 cv', 'Plantadeira 24 linhas · 0,5 m', '4,7 ha/h', 'Semente + MAP 11-52', 'sc/ha · kg/ha', 'DAP 0 (âncora DAP)', 'população pela germinação/PMS do lote; K no sulco ≤ 50–80 kg/ha K₂O; calendário de semeadura da UF', [
     ('Semeadura de soja', 'Trator 180 cv', 'Plantadeira 24 linhas', '4,7 ha/h', 'Semente 60 kg/ha + MAP', 'kg/ha', 'DAP 0', '12 m · 6 km/h · ef. 0,65'),
     ('Semeadura de milho', 'Trator 180 cv', 'Plantadeira 12 linhas', '3,5 ha/h', 'Semente 60 mil/ha + 08-28-16', 'sc/ha · kg/ha', 'DAP 0', 'singulação ≥ 95 %'),
     ('Semeadura de feijão', 'Trator 120 cv', 'Plantadeira 24 linhas', '4,7 ha/h', 'Semente 90 kg/ha + 04-30-10', 'kg/ha', 'DAP 0', 'feijão irrigado no pivô'),
     ('Semeadura de trigo', 'Trator 120 cv', 'Semeadora de linha 6 m', '4 ha/h', 'Semente 150 kg/ha + MAP', 'kg/ha', 'DAP 0', 'RS/SC/PR e Cerrado irrigado'),
     ('Semeadura de cobertura (braquiária/milheto)', 'Trator 120 cv', 'Semeadora a lanço', '10 ha/h', 'Semente de cobertura', 'kg/ha', 'DAC +5', 'palhada para SPD')]),
  ('4 · Tratos culturais', 'Adubação de cobertura', 'Trator 120 cv', 'Distribuidor 3 t', '10 ha/h', 'KCl 60 % / ureia', 'kg/ha', 'DAP 20–35 (V4–V6)', 'K parcelado em solo arenoso (CTC < 5); N em gramíneas 4–6 folhas', [
     ('Cobertura de potássio', 'Trator 120 cv', 'Distribuidor 3 t', '10 ha/h', 'KCl 60 %', 'kg/ha', 'DAP 25', '12 m · 10 km/h · ef. 0,8'),
     ('Cobertura de nitrogênio (milho/trigo)', 'Trator 120 cv', 'Distribuidor 3 t', '10 ha/h', 'Ureia 46 %', 'kg/ha', 'DAP 25 (V4–V6)', 'parcelar quando N > 80 kg/ha')]),
  ('4 · Tratos culturais', 'Pulverização', 'Pulverizador autopropelido 24 m', 'Barra 24 m', '25 ha/h', 'Herbicida / inseticida / fungicida', 'L/ha · kg/ha', 'DAP 15–75 e por vistoria', 'receituário agronômico · carência × DAC · rotação de modo de ação (IRAC/FRAC/HRAC) · calibração válida', [
     ('Herbicida pós-emergente', 'Pulverizador 24 m', 'Barra 24 m', '25 ha/h', 'Herbicida pós', 'L/ha', 'DAP 15–25', 'estádio da daninha ≤ 4 folhas'),
     ('Inseticida (por nível de ação)', 'Pulverizador 24 m', 'Barra 24 m', '25 ha/h', 'Inseticida', 'L/ha', 'vistoria ≥ nível', 'não por calendário'),
     ('Fungicida 1ª aplicação', 'Pulverizador 24 m', 'Barra 24 m', '25 ha/h', 'Fungicida multissítio + sistêmico', 'L/ha', 'DAP 35 (V8/R1)', 'intervalo 14 dias'),
     ('Fungicida 2ª e 3ª aplicações', 'Pulverizador 24 m', 'Barra 24 m', '25 ha/h', 'Fungicida', 'L/ha', 'DAP 50 e 65 (R3/R5)', 'máximo 3–4 aplicações/safra'),
     ('Foliar de micronutrientes', 'Pulverizador 24 m', 'Barra 24 m', '25 ha/h', 'Mn/Zn/B/Co-Mo', 'L/ha', 'DAP 30–45', 'junto com fungicida quando compatível'),
     ('Pulverização com drone', 'Drone 40 L', '—', '8 ha/h', 'Inseticida/fungicida', 'L/ha', 'por vistoria', 'talhões irregulares ou solo úmido'),
     ('Regulador de crescimento (algodão)', 'Pulverizador 24 m', 'Barra 24 m', '25 ha/h', 'Cloreto de mepiquat', 'L/ha', 'DAP 35–90', 'parcelado pelo crescimento'),
     ('Desfolhante (algodão)', 'Pulverizador 24 m', 'Barra 24 m', '25 ha/h', 'Desfolhante + maturador', 'L/ha', 'DAC −15', '60 % de capulhos abertos')]),
  ('4 · Tratos culturais', 'Cultivo e roçada', 'Trator 120 cv', 'Cultivador / roçadeira', '3–5 ha/h', '—', '—', 'DAP 20–40', 'cultivo mecânico em milho convencional; roçada de bordaduras e carreadores', [
     ('Cultivo mecânico', 'Trator 120 cv', 'Cultivador 6 linhas', '3 ha/h', '—', '—', 'DAP 25', 'milho não SPD'),
     ('Roçada de bordadura', 'Trator 75 cv', 'Roçadeira 2 m', '1,5 ha/h', '—', '—', 'mensal', 'carreadores e APP')]),
  ('5 · Irrigação', 'Irrigação por pivô', 'Pivô central', 'Bomba + tubulação', 'mm/dia', 'Água', 'mm', 'diária por balanço hídrico', 'FAO-56: ETc = ETo × Kc · lâmina bruta = líquida ÷ eficiência · janela noturna · kWh/mm', [
     ('Lâmina do dia', 'Pivô central', '—', '8–14 mm/volta', 'Água', 'mm', 'balanço diário', 'aprovar lâmina gera O.S.'),
     ('Fertirrigação', 'Pivô central', 'Injetor', 'mm', 'N/K solúvel', 'kg/ha', 'DAP 20–60', 'não fertirrigar com déficit > f × CAD'),
     ('Teste de uniformidade (CUC)', 'Manual', 'Coletores', '1 teste/pivô', '—', '—', 'pré-safra e após manutenção', 'CUC ≥ 85 % ok · < 80 % abre O.S. de manutenção')]),
  ('6 · Colheita', 'Colheita mecanizada', 'Colhedora 35 pés', 'Plataforma 10,7 m (soja) · milho 12 linhas', '4,5 ha/h', '—', 'sc/ha', 'DAC 0 (âncora DAC)', 'umidade de colheita soja 13–15 % · milho 18–24 %; perda ≤ 60 kg/ha (soja) medida em armação', [
     ('Colheita de soja', 'Colhedora 35 pés', 'Plataforma draper 10,7 m', '4,5 ha/h', '—', 'sc/ha', 'DAC 0', '10,7 m · 6 km/h · ef. 0,7'),
     ('Colheita de milho', 'Colhedora', 'Plataforma milho 12 linhas', '3,5 ha/h', '—', 'sc/ha', 'DAC 0', 'umidade ≤ 24 % com secador'),
     ('Colheita de algodão', 'Colhedora de algodão', 'Picker 6 linhas', '2,5 ha/h', '—', '@/ha', 'DAC 0', 'rolo/fardo com etiqueta HVI'),
     ('Transbordo', 'Trator 120 cv', 'Carreta graneleira 20 t', '4,5 ha/h', '—', '—', 'DAC 0', 'acompanha a colhedora'),
     ('Transporte interno', 'Caminhão graneleiro', '—', '36 t/viagem', '—', 't', 'DAC 0', 'romaneio por carga · balança'),
     ('Medição de perdas', 'Manual', 'Armação 2 m²', '3 pontos/talhão', '—', 'kg/ha', 'DAC 0 (início e troca de regulagem)', 'acima da tolerância → regular colhedora')]),
  ('7 · Pós-colheita e beneficiamento', 'Beneficiamento e armazenagem', 'Unidade de beneficiamento', 'Balança · pré-limpeza · secador · silo', 't/h', 'Lenha/GLP', 'kWh · t', 'DAC 0 a +3', 'peso líquido corrigido (impureza antes da umidade) · quebra técnica esperada × real · aeração por termometria', [
     ('Recepção e pesagem', 'Balança rodoviária', '—', '10 cargas/h', '—', 't', 'DAC 0', 'umidade e impureza por carga'),
     ('Pré-limpeza', 'Máquina de pré-limpeza', '—', '60 t/h', '—', 't', 'DAC 0', 'impurezas → 1 %'),
     ('Secagem', 'Secador de fluxo contínuo', '—', '30 t/h', 'Lenha / GLP', 't', 'DAC 0', 'ar ≤ 100 °C grão comercial · ≤ 40 °C semente'),
     ('Armazenagem e aeração', 'Silo com termometria', 'Aeração', '—', 'Energia', 'kWh', 'diária', 'aerar quando UR < 70 % e T grão > ambiente + 5 °C'),
     ('Expedição', 'Balança rodoviária', '—', '10 cargas/h', '—', 'sc', 'pedido de venda', 'romaneio · NF-e · certificado de origem')]),
 ],
 'Cana': [
  ('1 · Diagnóstico e amostragem', 'Amostragem e levantamento', 'Quadriciclo / manual', 'Trado', '15 ha/h', '—', '—', 'pré-reforma e anual', 'solo 0–25 e 25–50 cm; levantamento de broca e cigarrinha (Sphenophorus) por ponto', [
     ('Amostragem de solo', 'Quadriciclo', 'Trado', '15 ha/h', '—', '—', 'DAC +15', 'por talhão/ambiente de produção'),
     ('Levantamento de broca e cigarrinha', 'Manual', '—', '1 ponto/5 ha', '—', '—', 'mensal', 'intensidade de infestação → liberação de Cotesia/Metarhizium'),
     ('Amostragem de ATR (pré-colheita)', 'Manual', 'Sonda', '1 amostra/talhão', '—', '—', 'DAC −30', 'curva de maturação · ordem de colheita')]),
  ('2 · Correção e preparo do solo', 'Reforma do canavial', 'Trator 180 cv', 'Grade / eliminador de soqueira', '1,5–2,5 ha/h', 'Glifosato / calcário / gesso', 'L/ha · t/ha', 'reforma (5º–6º corte)', 'eliminação química ou mecânica da soqueira · calagem e gessagem · rotação com leguminosa (crotalária/amendoim)', [
     ('Eliminação de soqueira', 'Pulverizador / trator 180 cv', 'Barra / eliminador', '2,5 ha/h', 'Glifosato', 'L/ha', 'reforma', 'química preferida no SPD de cana'),
     ('Calagem e gessagem', 'Trator 120 cv', 'Distribuidor 6 t', '8 ha/h', 'Calcário · gesso', 't/ha · kg/ha', 'reforma −90 d', 'V2 60 % · gesso k = 75 × argila (semiperene)'),
     ('Subsolagem', 'Trator 220 cv', 'Subsolador 5 hastes', '1,2 ha/h', '—', '—', 'reforma −60 d', 'só com compactação diagnosticada'),
     ('Gradagem', 'Trator 180 cv', 'Grade aradora', '2,2 ha/h', '—', '—', 'reforma −45 d', 'preparo reduzido quando possível'),
     ('Sulcação e adubação de plantio', 'Trator 220 cv', 'Sulcador 2 linhas · 1,5 m', '1,5 ha/h', 'Fosfato + NK de plantio', 'kg/ha', 'plantio −1 d', 'P no fundo do sulco')]),
  ('3 · Plantio e implantação', 'Plantio de cana', 'Trator 220 cv', 'Plantadora de toletes / MPB', '1,2 ha/h', 'Muda (toletes 12–18 t/ha ou MPB) + inseticida/nematicida', 't/ha · L/ha', 'plantio (cana-planta)', 'plantio de ano e meio (fev–abr) ou de ano (set–out); cobrição 5–10 cm', [
     ('Plantio mecanizado de toletes', 'Trator 220 cv', 'Plantadora 2 linhas', '1,2 ha/h', 'Toletes 15 t/ha', 't/ha', 'plantio', 'gemas viáveis ≥ 15/m'),
     ('Plantio de mudas pré-brotadas (MPB)', 'Trator 120 cv', 'Transplantadora', '0,8 ha/h', 'MPB 15 mil/ha', 'mudas/ha', 'plantio', 'menor volume de muda · maior sanidade'),
     ('Inseticida/nematicida no sulco', 'Trator 220 cv', 'Aplicador no sulco', '1,2 ha/h', 'Fipronil / carbofurano-substituto', 'L/ha', 'plantio', 'cupim e nematoide'),
     ('Cobrição', 'Trator 120 cv', 'Cobridor', '2 ha/h', '—', '—', 'plantio 0', '5–10 cm de terra')]),
  ('4 · Tratos culturais', 'Tratos de cana-planta', 'Trator 120 cv', 'Pulverizador / cultivador', '2–4 ha/h', 'Herbicida pré e pós', 'L/ha', '15–90 DAP', 'quebra-lombo; controle de daninhas até fechamento (90–120 DAP)', [
     ('Herbicida pré-emergente', 'Pulverizador 18 m', 'Barra', '12 ha/h', 'Herbicida pré', 'L/ha', 'DAP 5', 'solo úmido'),
     ('Quebra-lombo', 'Trator 120 cv', 'Quebra-lombo', '2 ha/h', '—', '—', 'DAP 30', 'nivelar o sulco'),
     ('Herbicida pós-emergente', 'Pulverizador 18 m', 'Barra', '12 ha/h', 'Herbicida pós', 'L/ha', 'DAP 45', 'antes do fechamento'),
     ('Adubação de cobertura', 'Trator 120 cv', 'Cultivador-adubador', '2,5 ha/h', 'NK', 'kg/ha', 'DAP 60', 'N 60–80 · K₂O 100–140')]),
  ('4 · Tratos culturais', 'Tratos de soqueira', 'Trator 120 cv', 'Cultivador tríplice operação', '2,5 ha/h', 'NK + herbicida', 'kg/ha · L/ha', 'DAC +15 a +60', 'tríplice operação: escarificação, adubação e herbicida numa passada; vinhaça/torta de filtro quando disponível', [
     ('Tríplice operação', 'Trator 120 cv', 'Cultivador tríplice', '2,5 ha/h', 'NK + herbicida', 'kg/ha', 'DAC +20', 'N 80–120 · K₂O 100–150'),
     ('Aplicação de vinhaça (fertirrigação)', 'Carretel / caminhão', 'Aspersão', 'm³/ha', 'Vinhaça', 'm³/ha', 'DAC +10', 'norma CETESB P4.231 · K limita a dose'),
     ('Torta de filtro no sulco/soca', 'Trator 120 cv', 'Distribuidor de orgânico', '2 ha/h', 'Torta de filtro', 't/ha', 'DAC +10', 'fonte de P e MO'),
     ('Enleiramento / manejo de palha', 'Trator 120 cv', 'Enleirador', '3 ha/h', '—', '—', 'DAC +5', 'facilita brotação em soca'),
     ('Controle biológico de broca e cigarrinha', 'Drone / manual', '—', '20 ha/h', 'Cotesia flavipes · Metarhizium', 'copos/ha · kg/ha', 'por levantamento', '6.000 Cotesia/ha ao nível de infestação')]),
  ('5 · Irrigação', 'Irrigação de salvamento / plena', 'Pivô / carretel', '—', 'mm', 'Água', 'mm', 'plantio e estiagem', 'salvamento no plantio e na soca; plena por balanço hídrico', [
     ('Irrigação de salvamento', 'Carretel', '—', '30–60 mm', 'Água', 'mm', 'plantio 0 e DAC +10', 'garante brotação')]),
  ('6 · Colheita', 'Colheita de cana', 'Colhedora de cana', '—', '0,4 ha/h (35 t/h)', 'Maturador (opcional)', 'L/ha · t/ha', 'DAC 0 (curva de maturação)', 'maturador 30–45 d antes; colheita crua mecanizada; ordem pelo ATR e idade', [
     ('Aplicação de maturador', 'Avião / drone', '—', '60 ha/h', 'Maturador', 'L/ha', 'DAC −40', 'antecipa ATR'),
     ('Colheita mecanizada crua', 'Colhedora de cana', '—', '0,4 ha/h', '—', 't/ha', 'DAC 0', '35 t/h · 90 t/ha'),
     ('Transbordo', 'Trator 180 cv', 'Transbordo 12 t', '0,4 ha/h', '—', 't', 'DAC 0', '2 transbordos por colhedora'),
     ('Transporte à usina', 'Caminhão canavieiro (rodotrem)', '—', '60 t/viagem', '—', 't', 'DAC 0', 'até 48 h após o corte')]),
  ('8 · Manutenção da lavoura', 'Aceiros e carreadores', 'Trator 120 cv', 'Grade / motoniveladora', '2 ha/h', '—', '—', 'anual', 'aceiro contra fogo · carreadores para a colheita', [
     ('Manutenção de carreadores', 'Motoniveladora', '—', '3 km/h', '—', 'km', 'DAC −30', 'antes da colheita'),
     ('Aceiro', 'Trator 120 cv', 'Grade', '2 ha/h', '—', '—', 'maio', 'largura ≥ 6 m')]),
 ],
 'Café': [
  ('1 · Diagnóstico e amostragem', 'Amostragem e monitoramento', 'Manual', 'Trado', '10 ha/h', '—', '—', 'anual e quinzenal', 'solo 0–20 (linha) e 20–40; foliar em dez–jan (3º–4º par de folhas); bicho-mineiro, broca e ferrugem quinzenal', [
     ('Amostragem de solo (linha e entrelinha)', 'Manual', 'Trado', '10 ha/h', '—', '—', 'DAC +30', 'projeção da copa'),
     ('Amostragem foliar', 'Manual', '—', '1/talhão', '—', '—', 'dezembro–janeiro', '3º–4º par, ramos plagiotrópicos'),
     ('Monitoramento de ferrugem, bicho-mineiro e broca', 'Manual', 'Lupa', '1 ponto/5 ha', '—', '—', 'quinzenal', 'ferrugem ≥ 5 % folhas → fungicida')]),
  ('2 · Correção e preparo do solo', 'Correção e preparo para implantação', 'Trator 120 cv', 'Distribuidor / subsolador / sulcador', '1–8 ha/h', 'Calcário · gesso · fosfato', 't/ha · kg/ha', 'implantação −90 d', 'V2 60 % · PF 30–40 cm em preparo profundo · sulco/cova com adubação', [
     ('Calagem e gessagem (área total)', 'Trator 120 cv', 'Distribuidor 6 t', '8 ha/h', 'Calcário · gesso', 't/ha', 'implantação −90 d', 'incorporar'),
     ('Subsolagem na linha', 'Trator 180 cv', 'Subsolador', '1,5 ha/h', '—', '—', 'implantação −60 d', 'linha de plantio'),
     ('Sulcação/coveamento e adubação de plantio', 'Trator 120 cv', 'Sulcador / perfurador', '1 ha/h', 'SSP + esterco/orgânico', 'kg/cova', 'implantação −15 d', 'P na cova')]),
  ('3 · Plantio e implantação', 'Plantio de mudas', 'Manual / transplantadora', '—', '1.000 covas/h', 'Muda (3,5–7 mil/ha)', 'mudas/ha', 'implantação (out–dez)', 'espaçamento 3,5–3,8 × 0,5–0,7 m (mecanizável)', [
     ('Plantio de mudas', 'Manual', '—', '1.000 covas/h', 'Muda', 'mudas/ha', 'implantação', 'chuva estabelecida'),
     ('Irrigação de pegamento', 'Carretel / gotejo', '—', 'mm', 'Água', 'mm', 'implantação 0–30 d', 'se veranico'),
     ('Replantio de falhas', 'Manual', '—', '—', 'Muda', 'mudas', 'implantação +45 d', 'falhas > 5 %')]),
  ('4 · Tratos culturais', 'Adubação do cafeeiro', 'Trator 75 cv cafeeiro', 'Distribuidor para café', '2 ha/h', 'NPK (20-00-20) · calcário em faixa', 'kg/ha', 'out, dez, fev (3–4 parcelas)', 'dose pela produtividade esperada e análise (CFSEMG/Boletim 100); parcelar N e K', [
     ('Adubação NPK parcelada', 'Trator 75 cv', 'Distribuidor lateral', '2 ha/h', '20-00-20 / 20-05-20', 'kg/ha', 'out · dez · fev', 'N 250–400 · K₂O 200–350 para > 40 sc/ha'),
     ('Calagem em faixa (projeção da copa)', 'Trator 75 cv', 'Distribuidor lateral', '2 ha/h', 'Calcário', 't/ha', 'julho–agosto', 'SC = largura da faixa ÷ espaçamento'),
     ('Adubação foliar (B, Zn, Cu)', 'Turbo atomizador', '—', '2 ha/h', 'B · Zn · Cu', 'L/ha', 'out, dez, fev', 'junto com fungicida'),
     ('Fertirrigação (gotejo)', 'Sistema de gotejo', 'Injetor', 'ha/turno', 'N e K solúveis', 'kg/ha', 'semanal (set–mar)', 'irrigado')]),
  ('4 · Tratos culturais', 'Pulverização do cafeeiro', 'Turbo atomizador', 'Trator 75 cv', '2 ha/h', 'Fungicida · inseticida', 'L/ha', 'nov–mar por monitoramento', 'ferrugem (cúpricos + triazol/estrobilurina), cercospora, bicho-mineiro, broca; receituário; carência', [
     ('Fungicida (ferrugem/cercospora)', 'Turbo atomizador', '—', '2 ha/h', 'Triazol + estrobilurina / cúprico', 'L/ha', 'dez · fev', 'por incidência ≥ 5 %'),
     ('Inseticida (bicho-mineiro/broca)', 'Turbo atomizador', '—', '2 ha/h', 'Inseticida', 'L/ha', 'por monitoramento', 'broca: 3–5 % frutos brocados'),
     ('Herbicida na linha', 'Pulverizador com bico protegido', '—', '3 ha/h', 'Glifosato / pré-emergente', 'L/ha', 'out e fev', 'sem atingir a saia'),
     ('Roçada da entrelinha', 'Trator 75 cv', 'Roçadeira', '2,5 ha/h', '—', '—', 'a cada 45 d (chuvas)', 'manter cobertura')]),
  ('4 · Tratos culturais', 'Poda e desbrota', 'Manual / podadeira mecanizada', '—', '0,3–0,8 ha/h', '—', '—', 'jul–ago (pós-colheita)', 'esqueletamento, decote, recepa por idade e vigor; desbrota 60–90 d após poda', [
     ('Esqueletamento / decote', 'Podadeira mecanizada', 'Trator 75 cv', '0,8 ha/h', '—', '—', 'julho', 'ciclo de poda'),
     ('Recepa', 'Motosserra / manual', '—', '0,3 ha/h', '—', '—', 'agosto', 'lavoura depauperada'),
     ('Desbrota', 'Manual', '—', '0,5 ha/h', '—', '—', 'poda +60 d', '2–3 brotos/planta')]),
  ('4 · Tratos culturais', 'Arruação e esparramação', 'Trator 75 cv', 'Arruador / esparramador', '3 ha/h', '—', '—', 'DAC −15 e DAC +15', 'arruação antes da colheita (limpa a saia) e esparramação depois', [
     ('Arruação', 'Trator 75 cv', 'Arruador', '3 ha/h', '—', '—', 'DAC −15', 'antes da derriça'),
     ('Esparramação', 'Trator 75 cv', 'Esparramador', '3 ha/h', '—', '—', 'DAC +15', 'devolve a cobertura')]),
  ('5 · Irrigação', 'Irrigação do cafeeiro', 'Gotejo / pivô', '—', 'mm', 'Água', 'mm', 'balanço hídrico (abr–set)', 'estresse hídrico controlado para florada uniforme (jul–ago)', [
     ('Irrigação por balanço hídrico', 'Gotejo', '—', 'mm', 'Água', 'mm', 'diária', 'Kc por fase · suspensão para florada')]),
  ('6 · Colheita', 'Colheita do café', 'Colhedora automotriz', '—', '0,4 ha/h', '—', 'L/ha · sc/ha', 'DAC 0 (maturação ≥ 70 % cereja)', 'mecanizada, semimecanizada (derriçadora) ou manual; pano; varrição e recolhimento', [
     ('Colheita mecanizada', 'Colhedora automotriz', '—', '0,4 ha/h', '—', 'L/ha', 'DAC 0', 'vibração e velocidade por maturação'),
     ('Derriça com derriçadora portátil', 'Derriçadora', 'Pano', '0,08 ha/h', '—', 'L', 'DAC 0', 'terrenos declivosos'),
     ('Varrição e recolhimento', 'Recolhedora', 'Trator 75 cv', '1 ha/h', '—', 'L', 'DAC +5', 'café de varrição separado'),
     ('Transporte ao terreiro', 'Trator + carreta', '—', 'L/viagem', '—', 'L', 'DAC 0', 'mesmo dia')]),
  ('7 · Pós-colheita e beneficiamento', 'Preparo e beneficiamento', 'Lavador · despolpador · secador · beneficiadora', '—', 'sc/h', 'Lenha / energia', 'sc', 'DAC 0 a +30', 'lavagem e separação (boia/cereja) · CD/natural · secagem ≤ 40 °C · descascamento · classificação (peneira, bebida)', [
     ('Lavagem e separação', 'Lavador', '—', '3.000 L/h', 'Água', 'L', 'DAC 0', 'boia × cereja/verde'),
     ('Despolpa / descascamento (CD)', 'Despolpador', '—', '2.000 L/h', '—', 'L', 'DAC 0', 'cereja descascado'),
     ('Secagem (terreiro e secador)', 'Secador rotativo', '—', 'sc/h', 'Lenha', 'sc', 'DAC +1 a +10', 'ar ≤ 40 °C · umidade final 11–12 %'),
     ('Beneficiamento e classificação', 'Beneficiadora', 'Peneiras', '20 sc/h', '—', 'sc', 'DAC +30', 'peneira, defeitos, bebida'),
     ('Armazenagem', 'Tulha / big bag', '—', '—', '—', 'sc', 'DAC +30', 'umidade 11–12 % · lote por talhão')]),
 ],
 'Frutas': [
  ('1 · Diagnóstico e amostragem', 'Amostragem e monitoramento', 'Manual', 'Trado · armadilhas', '10 ha/h', '—', '—', 'anual e semanal', 'solo e foliar por talhão/idade; armadilhas para mosca-das-frutas; psilídeo (citros); sigatoka (banana)', [
     ('Amostragem de solo e foliar', 'Manual', 'Trado', '10 ha/h', '—', '—', 'anual', 'folha por espécie (citros: 4º–6º mês)'),
     ('Monitoramento de pragas (armadilhas)', 'Manual', 'Armadilha McPhail/Jackson', '1/5 ha', 'Atrativo', 'un', 'semanal', 'MAD = moscas/armadilha/dia'),
     ('Inspeção de greening/HLB (citros)', 'Manual', '—', '2 ha/h', '—', '—', 'trimestral', 'erradicação de plantas sintomáticas')]),
  ('2 · Correção e preparo do solo', 'Preparo e implantação do pomar', 'Trator 120 cv', 'Distribuidor · subsolador · sulcador', '1–8 ha/h', 'Calcário · gesso · fosfato · orgânico', 't/ha · kg/cova', 'implantação −90 d', 'V2 70 % (citros SP) · covas/sulcos com P e MO · drenagem', [
     ('Calagem e gessagem', 'Trator 120 cv', 'Distribuidor 6 t', '8 ha/h', 'Calcário · gesso', 't/ha', 'implantação −90 d', 'gesso: k = 75 × argila (perene)'),
     ('Subsolagem e sulcação', 'Trator 180 cv', 'Subsolador / sulcador', '1,2 ha/h', '—', '—', 'implantação −60 d', 'linha de plantio'),
     ('Marcação e coveamento', 'Trator 75 cv', 'Perfurador de covas', '60 covas/h', 'Adubo orgânico + P', 'kg/cova', 'implantação −15 d', 'GPS · espaçamento por espécie'),
     ('Instalação de irrigação (gotejo/microaspersão)', 'Equipe', '—', '1 ha/dia', 'Tubos gotejadores', 'm', 'implantação −7 d', 'projeto com CUC ≥ 90 %'),
     ('Tutoramento / espaldeira (uva, maçã)', 'Equipe', '—', '0,3 ha/dia', 'Mourões · arame', 'un · m', 'implantação', 'sistema de condução')]),
  ('3 · Plantio e implantação', 'Plantio de mudas', 'Manual', '—', '40 mudas/h', 'Muda certificada', 'mudas/ha', 'implantação (chuvas)', 'muda certificada (citros: viveiro telado); irrigação de pegamento', [
     ('Plantio de mudas', 'Manual', '—', '40 mudas/h', 'Muda certificada', 'mudas/ha', 'implantação', 'colo acima do solo'),
     ('Irrigação de pegamento', 'Gotejo', '—', 'mm', 'Água', 'mm', 'implantação 0–60 d', 'diária no início')]),
  ('3 · Plantio e implantação', 'Mamão Formosa · implantação e condução', 'Manual / trator 75 cv', 'Perfurador de covas · distribuidor lateral', '60 covas/h', 'Muda Tainung 01 · esterco · SSP · FTE', 'mudas/ha · L/cova · g/cova', 'implantação (chuvas) e DAP 90–150 (sexagem)', 'INCAPER/Embrapa: cova 40×40×40 preparada 30 d antes; 2–3 mudas/cova; sexagem ao florescimento deixando 1 hermafrodita; boro obrigatório; roguing semanal de PRSV-p', [
     ('Cova de plantio com adubação', 'Trator 75 cv', 'Perfurador de covas', '60 covas/h', 'Esterco 10–20 L + SSP 500–800 g + FTE BR-12 30–50 g', 'por cova', 'implantação −30 d', 'calcário de cova 200–300 g quando não incorporado'),
     ('Plantio de mudas (2–3 por cova)', 'Manual', '—', '40 covas/h', 'Muda Tainung 01', 'mudas/ha', 'implantação', '3,6–3,8 × 1,8–2,0 m · irrigação de pegamento'),
     ('Sexagem (desbaste de plantas)', 'Manual', '—', '0,2 ha/h', '—', '—', 'DAP 90–150 (florescimento)', 'fica 1 planta hermafrodita por cova'),
     ('Adubação de formação (N e K mensal)', 'Manual / distribuidor lateral', '—', '0,5 ha/h', 'Ureia · KCl', 'g/planta', 'DAP 30 → 180 (mensal)', 'INCAPER: N 10–30 g · K₂O 10–40 g por planta e mês'),
     ('Adubação de produção (N, K mensal · P parcelado)', 'Fertirrigação / distribuidor', 'Injetor', 'ha/turno', 'Ureia · nitrato de cálcio · KCl · MAP', 'g/planta', 'florescimento → fim do ciclo (mensal; semanal fertirrigado)', 'N 20–40 g · K₂O 20–60 g por classe de K · P₂O₅ 40–150 g/planta/ano'),
     ('Aplicação de boro', 'Manual / pulverizador', '—', '1 ha/h', 'Ácido bórico', 'g/planta · % foliar', 'a cada 60–90 d desde DAP 60', '0,5–1 g B/planta ou foliar 0,1–0,2 % · alvo foliar 20–30 mg/kg'),
     ('Desbaste de frutos', 'Manual', '—', '0,2 ha/h', '—', '—', 'quinzenal na produção', '1 fruto por nó · calibre Formosa'),
     ('Roguing de mosaico e meleira (PRSV-p)', 'Manual', '—', '1 ha/h', '—', '—', 'semanal', 'nível de controle zero · eliminar a planta na semana'),
     ('Controle de ácaros e pinta-preta', 'Turbo atomizador / costal', '—', '2 ha/h', 'Acaricida · fungicida', 'L/ha', 'por vistoria', 'ácaro-branco: presença em 10 % das folhas'),
     ('Colheita (1–2× por semana)', 'Manual', 'Carrinho · caixa', '150 frutos/h', '—', 'kg', 'DAP 240–300 em diante', 'estádio 1–2 de maturação · pós-colheita hidrotérmico quando exigido'),
     ('Análise foliar bimestral', 'Manual', '—', '1/talhão', '—', '—', 'a cada 60–90 d', '6ª folha do ápice · limbo · 15–20 plantas')]),
  ('4 · Tratos culturais', 'Adubação e fertirrigação', 'Trator 75 cv / gotejo', 'Distribuidor lateral / injetor', '2 ha/h', 'NPK · orgânico · foliar', 'kg/ha', 'parcelado (set–mar)', 'dose por idade/produção e análise (Boletim 100/Embrapa); fertirrigação semanal', [
     ('Adubação NPK parcelada', 'Trator 75 cv', 'Distribuidor lateral', '2 ha/h', 'NPK', 'kg/ha', '3–4 parcelas', 'projeção da copa'),
     ('Fertirrigação', 'Gotejo', 'Injetor', 'ha/turno', 'N · K · Ca', 'kg/ha', 'semanal', 'condutividade elétrica controlada'),
     ('Adubação foliar (B, Zn, Mn)', 'Turbo atomizador', '—', '2 ha/h', 'Micronutrientes', 'L/ha', 'brotação e pós-florada', 'com fungicida compatível')]),
  ('4 · Tratos culturais', 'Poda, raleio e condução', 'Manual / podadeira', '—', '0,2–0,8 ha/h', '—', '—', 'pós-colheita e pré-florada', 'poda de formação/produção/limpeza; raleio de frutos (maçã, uva, pêssego); indução floral (manga); ensacamento', [
     ('Poda de formação/produção', 'Manual / podadeira pneumática', '—', '0,3 ha/h', '—', '—', 'pós-colheita', 'por espécie'),
     ('Raleio de frutos', 'Manual', '—', '0,2 ha/h', '—', '—', 'fruto 10–15 mm', 'maçã, uva, pêssego'),
     ('Indução floral (manga)', 'Turbo atomizador', '—', '2 ha/h', 'Paclobutrazol / nitrato de potássio', 'L/ha · kg/ha', 'calendário do produtor', 'escalonar colheita'),
     ('Ensacamento (manga, goiaba, uva)', 'Manual', '—', '300 frutos/h', 'Saco de papel/TNT', 'un', 'fruto chumbinho', 'mosca-das-frutas'),
     ('Desfolha / desbrota (uva)', 'Manual', '—', '0,3 ha/h', '—', '—', 'pós-florada', 'aeração do cacho')]),
  ('4 · Tratos culturais', 'Pulverização do pomar', 'Turbo atomizador', 'Trator 75 cv', '2 ha/h', 'Fungicida · inseticida · acaricida · óleo', 'L/ha', 'por monitoramento e fenologia', 'greening (psilídeo), pinta-preta, sigatoka, míldio, mosca-das-frutas (isca tóxica); receituário; carência', [
     ('Fungicida (fenologia)', 'Turbo atomizador', '—', '2 ha/h', 'Fungicida', 'L/ha', 'brotação · florada · fruto', 'rotação FRAC'),
     ('Inseticida/acaricida (monitoramento)', 'Turbo atomizador', '—', '2 ha/h', 'Inseticida · acaricida', 'L/ha', 'nível de ação', 'psilídeo: 1 adulto/armadilha'),
     ('Isca tóxica (mosca-das-frutas)', 'Costal / trator', '—', '5 ha/h', 'Proteína hidrolisada + inseticida', 'L/ha', 'MAD ≥ 0,5', 'faixas alternadas'),
     ('Herbicida na linha / roçada da entrelinha', 'Trator 75 cv', 'Bico protegido / roçadeira', '3 ha/h', 'Herbicida', 'L/ha', 'a cada 45–60 d', 'cobertura na entrelinha')]),
  ('5 · Irrigação', 'Irrigação do pomar', 'Gotejo / microaspersão', 'Bomba · filtros', 'mm', 'Água', 'mm', 'diária por balanço hídrico', 'Kc por fase fenológica; manejo por tensiômetro ou sensor', [
     ('Irrigação por balanço hídrico', 'Gotejo', '—', 'mm', 'Água', 'mm', 'diária', 'FAO-56 · Kc por espécie/fase'),
     ('Limpeza de filtros e linhas', 'Manual', '—', '1 setor/h', 'Ácido / cloro', 'L', 'mensal', 'CUC ≥ 90 %')]),
  ('6 · Colheita', 'Colheita de frutas', 'Manual / plataforma', 'Sacola · contentor', 'kg/h · cx/h', '—', 'cx · kg', 'ponto de colheita (°Brix, cor, firmeza)', 'manual com índice de maturação; contentores; transporte rápido ao packing', [
     ('Colheita manual', 'Manual', 'Sacola · escada/plataforma', '60 kg/h', '—', 'kg', 'ponto de colheita', 'turno da manhã'),
     ('Transporte ao packing house', 'Trator + carreta / caminhão', 'Contentor 400 kg', 'viagem', '—', 'kg', 'DAC 0', 'até 4 h após colheita')]),
  ('7 · Pós-colheita e beneficiamento', 'Packing house', 'Linha de beneficiamento', 'Lavagem · classificação · embalagem · câmara fria', 't/h', 'Fungicida pós-colheita · cera', 't', 'DAC 0 a +2', 'lavagem, tratamento pós-colheita, classificação por calibre/cor, embalagem com lote rastreável, resfriamento', [
     ('Recepção e pesagem', 'Balança', '—', 't/h', '—', 'kg', 'DAC 0', 'lote por talhão'),
     ('Lavagem e tratamento pós-colheita', 'Linha', '—', 't/h', 'Fungicida · cera', 'L', 'DAC 0', 'carência zero registrada'),
     ('Classificação e embalagem', 'Classificadora', '—', 'cx/h', 'Caixa · etiqueta', 'un', 'DAC 0', 'calibre · classe · etiqueta rastreável'),
     ('Resfriamento e câmara fria', 'Câmara fria', '—', 't', 'Energia', 'kWh', 'DAC 0', 'temperatura por espécie'),
     ('Expedição', 'Caminhão refrigerado', '—', 'cx', '—', 'cx', 'pedido', 'romaneio · NF-e · GTA fitossanitária quando exigida')]),
 ],
 'HF': [
  ('1 · Diagnóstico e amostragem', 'Amostragem e monitoramento', 'Manual', 'Trado', '5 ha/h', '—', '—', 'a cada ciclo e semanal', 'solo por canteiro/talhão a cada ciclo; foliar em cultura longa (tomate); vistoria semanal de pragas e doenças', [
     ('Amostragem de solo por talhão', 'Manual', 'Trado', '5 ha/h', '—', '—', 'pré-plantio', 'cada ciclo'),
     ('Vistoria semanal (pragas e doenças)', 'Manual', 'Lupa · armadilha adesiva', '1 ponto/ha', '—', '—', 'semanal', 'mosca-branca, tripes, traça, requeima')]),
  ('2 · Correção e preparo do solo', 'Preparo de canteiros', 'Trator 75 cv', 'Enxada rotativa · rotoencanteirador', '0,5 ha/h', 'Calcário · adubo de base · orgânico', 't/ha · kg/ha', 'plantio −30 a −3 d', 'calagem 30–60 d antes; adubação de base incorporada; canteiros 1,0–1,2 m; mulching e gotejo', [
     ('Calagem', 'Trator 75 cv', 'Distribuidor 2 t', '3 ha/h', 'Calcário', 't/ha', 'plantio −45 d', 'V2 70–80 % (hortaliças)'),
     ('Adubação de base', 'Trator 75 cv', 'Distribuidor 2 t', '3 ha/h', 'NPK + orgânico (esterco/composto)', 'kg/ha · t/ha', 'plantio −7 d', 'incorporar'),
     ('Aração e gradagem', 'Trator 75 cv', 'Arado / grade', '1 ha/h', '—', '—', 'plantio −20 d', 'destorroar'),
     ('Encanteiramento', 'Trator 75 cv', 'Rotoencanteirador 1,2 m', '0,5 ha/h', '—', '—', 'plantio −3 d', 'canteiro 1,2 × 0,25 m'),
     ('Mulching e instalação de gotejo', 'Trator 75 cv', 'Aplicador de mulching', '0,4 ha/h', 'Filme plástico · fita gotejadora', 'm', 'plantio −2 d', 'fita a 20 cm')]),
  ('3 · Plantio e implantação', 'Semeadura e transplante', 'Trator 75 cv / manual', 'Semeadora de precisão · transplantadora', '0,3–1,5 ha/h', 'Semente · muda de bandeja · tubérculo', 'mil/ha · kg/ha', 'plantio 0 (âncora DAP)', 'mudas de bandeja (viveiro) para tomate/alface/cebola; semeadura direta para cenoura; batata por tubérculo-semente', [
     ('Produção de mudas em bandeja', 'Viveiro', 'Bandejas 200 células', '10 bandejas/h', 'Semente + substrato', 'mil mudas', 'plantio −25 d', 'muda com 4 folhas'),
     ('Transplante de mudas', 'Trator 75 cv', 'Transplantadora 2 linhas', '0,4 ha/h', 'Muda', 'mil/ha', 'DAP 0', 'irrigar logo após'),
     ('Semeadura direta de precisão', 'Trator 75 cv', 'Semeadora pneumática', '1,5 ha/h', 'Semente', 'mil/ha', 'DAP 0', 'cenoura, beterraba, rúcula'),
     ('Plantio de batata', 'Trator 120 cv', 'Plantadeira de batata 2 linhas', '0,6 ha/h', 'Tubérculo-semente + NPK', 't/ha · kg/ha', 'DAP 0', 'semente certificada')]),
  ('4 · Tratos culturais', 'Tratos de hortaliças', 'Manual / trator 75 cv', 'Cultivador · amontoador', '0,3–1 ha/h', 'NPK cobertura · fertirrigação', 'kg/ha', 'DAP 15–60', 'amontoa (batata), tutoramento e desbrota (tomate), capina/herbicida, cobertura', [
     ('Fertirrigação', 'Gotejo', 'Injetor', 'ha/turno', 'Nutrientes solúveis', 'kg/ha', 'diária/semanal', 'curva de absorção da cultura'),
     ('Adubação de cobertura', 'Manual / trator 75 cv', 'Distribuidor', '1 ha/h', 'NPK', 'kg/ha', 'DAP 20 e 40', 'parcelada'),
     ('Amontoa (batata)', 'Trator 75 cv', 'Amontoador', '0,8 ha/h', '—', '—', 'DAP 25', 'antes do fechamento'),
     ('Tutoramento e desbrota (tomate)', 'Manual', 'Estacas · fitilho', '0,1 ha/h', 'Fitilho', 'm', 'DAP 20–60', 'semanal'),
     ('Capina / herbicida', 'Manual / pulverizador de barra', '—', '0,3–3 ha/h', 'Herbicida seletivo', 'L/ha', 'DAP 10–30', 'poucos registros: preferir mulching')]),
  ('4 · Tratos culturais', 'Pulverização de hortaliças', 'Pulverizador de barra 12 m / costal', '—', '4 ha/h', 'Fungicida · inseticida · biológico', 'L/ha', 'semanal por vistoria', 'MIP intensivo: rotação, biológicos (Bt, Trichoderma), carência curta; receituário; registro por cultura (minor crops)', [
     ('Fungicida (requeima, míldio, oídio)', 'Pulverizador de barra', '—', '4 ha/h', 'Fungicida', 'L/ha', 'por vistoria/clima', 'carência ≤ colheita'),
     ('Inseticida / biológico', 'Pulverizador de barra', '—', '4 ha/h', 'Inseticida · Bt', 'L/ha', 'nível de ação', 'mosca-branca, tripes, traça'),
     ('Aplicação de biológicos de solo', 'Gotejo', 'Injetor', 'ha/turno', 'Trichoderma · Bacillus', 'L/ha', 'DAP 0 e 20', 'via fertirrigação')]),
  ('5 · Irrigação', 'Irrigação de hortaliças', 'Gotejo / aspersão', '—', 'mm', 'Água', 'mm', 'diária', 'turno de rega curto; Kc por fase; gotejo sob mulching', [
     ('Irrigação diária', 'Gotejo', '—', 'mm', 'Água', 'mm', 'diária', 'FAO-56 · tensiômetro')]),
  ('6 · Colheita', 'Colheita de hortaliças', 'Manual / colhedora', 'Caixas · esteira', 'kg/h', '—', 'kg · cx', 'ponto de colheita (dias e aspecto)', 'manual para folhosas/tomate; mecanizada para batata, cenoura, cebola; colheita escalonada', [
     ('Colheita manual', 'Manual', 'Caixa plástica', '40 kg/h', '—', 'kg', 'DAC 0', 'madrugada/manhã'),
     ('Colheita mecanizada (batata/cenoura/cebola)', 'Trator 120 cv', 'Colhedora 2 linhas', '0,4 ha/h', '—', 't/ha', 'DAC 0', 'dessecar rama antes (batata)'),
     ('Transporte ao galpão', 'Trator + carreta', 'Caixas', 'viagem', '—', 'kg', 'DAC 0', 'sombra · até 2 h')]),
  ('7 · Pós-colheita e beneficiamento', 'Beneficiamento e expedição', 'Linha de lavagem e classificação', 'Câmara fria', 'kg/h', 'Embalagem', 'kg · cx', 'DAC 0', 'lavagem, classificação, embalagem com lote/etiqueta rastreável, resfriamento rápido, expedição', [
     ('Lavagem e classificação', 'Linha', '—', '1 t/h', '—', 'kg', 'DAC 0', 'padrão CEAGESP'),
     ('Embalagem e etiqueta', 'Manual', '—', '60 cx/h', 'Caixa · etiqueta', 'cx', 'DAC 0', 'rastreabilidade por lote'),
     ('Resfriamento rápido', 'Hidrocooling / câmara', '—', 't', 'Energia', 'kWh', 'DAC 0', 'cadeia do frio'),
     ('Expedição', 'Caminhão baú', '—', 'cx', '—', 'cx', 'pedido', 'romaneio · NF-e')]),
 ],
}

def contar():
    ops=sum(len(v) for v in CAT.values()); ats=sum(len(o[9]) for v in CAT.values() for o in v)
    return ops,ats
