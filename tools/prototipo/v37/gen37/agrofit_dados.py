# -*- coding: utf-8 -*-
"""Consulta Agrofit (AG-07): base DEMONSTRATIVA de produtos fitossanitários no formato de registro do AGROFIT.

Desde 02/10/2026 a AG-07 lista os registros REAIS (dados abertos do AGROFIT, dados_agrofit/site/*.json). Esta base continua como
"Referência conferida em bula" dentro da ficha real e como elo "Na fazenda" (AGROFIT_INGREDIENTES, no fim do arquivo); os links
antigos AG-07.dc.html#<id> (O.S., MIP) abrem a lista filtrada pelo mesmo ingrediente.

O que é real e o que é demonstrativo
- Grupos de modo de ação: conferidos nas classificações públicas em 01/10/2026: IRAC (inseticidas, ed. 11.x, e o esquema de
  nematicidas N-1…N-4 / N-UN*), FRAC Code List (2024/2025; multissítios M1/M2/M3) e HRAC Global (numeração 2020+).
- Situação regulatória: conferida na página da Anvisa "Reavaliação de agrotóxicos" (gov.br/anvisa). Paraquate proibido desde
  22/09/2020 (RDC 177/2017); epoxiconazol e tiofanato-metílico seguem em reavaliação toxicológica; glifosato (RDC 441/2020),
  2,4-D (RDC 284/2019), abamectina (RDC 442/2020) e acefato (RDC 45/2013) foram mantidos com restrições após reavaliação.
- Cada uso tem o campo `conferido`: True quando o par cultura × alvo foi visto em bula pública do mesmo ingrediente (ADAPAR,
  agrolink, fabricante, monografia Anvisa); False quando é combinação agronômica usual ainda não conferida. A ficha deve marcar
  os usos com conferido=False como "não conferido na bula". Doses, carências, nº de aplicações, classes toxicológica e ambiental
  e reentrada são DEMONSTRATIVOS: plausíveis, mas não substituem a bula do produto comercial.
- Não há número de registro, marca comercial nem titular: o nome segue o padrão da fazenda (ingrediente + concentração + formulação)
  ou o nome genérico que a fazenda já usa ('Fungicida A', 'Inseticida B'…). A consulta oficial é o AGROFIT (link em CONSULTA).
- Fora do AGROFIT por lei própria e, portanto, fora desta base: fertilizantes, corretivos, sementes, mudas e inoculantes.
- Viroses do mamão (mosaico, meleira, mancha-anelar) não têm controle químico: manejo por roguing; nenhum produto inventado.

Cobertura: todos os defensivos e adjuvantes dos planos (dados2.PLANOS, dados_lagoa_safra.PLANOS) e dos lotes e ordens do cenário
(cenario.seed()) têm ficha com o nome EXATO da fazenda. A REC-014 v2 e a OS-0420 (telas estáticas de agronomia.py e campo.py)
usam 'TS nematicida (abamectina)', ligado à ficha 'Abamectina 500 FS' por `nomes_fazenda` e `refs_fazenda`. Os demais produtos
são alternativas de outro grupo de ação para os alvos das culturas da fazenda (manejo de resistência).

Campos de cada produto (para a ficha)
  id, nome, nomes_fazenda [nomes usados nos planos/estoque/ordens/recomendações], ingrediente, concentracao, formulacao, classe,
  grupos [códigos IRAC/FRAC/HRAC em ordem canônica], grupo (rótulo gerado de grupos), grupo_nome (rótulo gerado), tox, amb,
  reentrada, situacao (Vigente · Em reavaliação · Cancelado), situacao_nota,
  usos [cultura, alvo, chave (alvo normalizado p/ comparar), dose, carencia, max_aplic, intervalo, conferido],
  avisos [restrições da bula, para a seção Segurança],
  alertas_fazenda [dict(ref, texto, alt) · divergência plano/recomendação × bula que a página NÃO calcula, para a seção Na fazenda;
                   alt = id da alternativa. Dose de plano ou O.S. acima da bula é calculada ao vivo na AG-07: não repetir aqui],
  refs_fazenda [dict(ref, href, texto) · registros estáticos que usam o produto e não estão no cenário].
Rotação: alternativas(p, uso) devolve só produtos com interseção VAZIA de grupos (mistura que divide um componente não é rotação);
lista vazia → mostrar SEM_ALTERNATIVA. Registro cancelado: substitutos(p, uso) devolve os produtos permitidos para o mesmo
cultura × alvo, de QUALQUER grupo (o que importa é o que substitui o proibido); lista vazia → mostrar SEM_SUBSTITUTO.
"""
import re

CONSULTA = dict(data='20/09/2026', demonstrativo=True,
                link='https://agrofit.agricultura.gov.br/agrofit_cons/principal_agrofit_cons')

SEM_ALTERNATIVA = 'Sem alternativa registrada de outro grupo nesta base · conferir no AGROFIT oficial'
SEM_SUBSTITUTO = 'Sem substituto registrado nesta base · conferir no AGROFIT oficial'

# classificação toxicológica (escala Anvisa, RDC 294/2019) e classe ambiental (potencial de periculosidade, IBAMA)
_T2 = 'Categoria 2 · altamente tóxico'
_T3 = 'Categoria 3 · moderadamente tóxico'
_T4 = 'Categoria 4 · pouco tóxico'
_T5 = 'Categoria 5 · improvável de causar dano agudo'
_TN = 'Não classificado'
_A1 = 'I · altamente perigoso'
_A2 = 'II · muito perigoso'
_A3 = 'III · perigoso'
_A4 = 'IV · pouco perigoso'

_PRE = 'uso pré-plantio'
_TS = 'não determinada (TS)'
_ADJ = 'segue o produto associado'

# código → (nome curto, usado em misturas; nome completo, usado em produto de um grupo só)
GRUPOS = {
 'HRAC 1': ('inibidor da ACCase', 'inibidor da ACCase'),
 'HRAC 2': ('inibidor da ALS', 'inibidor da ALS'),
 'HRAC 4': ('auxina sintética', 'mimetizador de auxina'),
 'HRAC 5': ('inibidor do FSII', 'inibidor do fotossistema II'),
 'HRAC 9': ('inibidor da EPSPS', 'inibidor da EPSPS'),
 'HRAC 10': ('inibidor da GS', 'inibidor da glutamina sintetase'),
 'HRAC 14': ('inibidor da PPO', 'inibidor da PROTOX (PPO)'),
 'HRAC 15': ('inibidor de AGCML', 'inibidor da síntese de ácidos graxos de cadeia muito longa'),
 'HRAC 22': ('desviador do FSI', 'desviador de elétrons do fotossistema I'),
 'HRAC 27': ('inibidor da HPPD', 'inibidor da HPPD'),
 'FRAC 1': ('benzimidazol', 'benzimidazol (MBC)'),
 'FRAC 3': ('triazol (DMI)', 'triazol (DMI)'),
 'FRAC 4': ('fenilamida', 'fenilamida'),
 'FRAC 7': ('carboxamida (SDHI)', 'carboxamida (SDHI)'),
 'FRAC 11': ('estrobilurina (QoI)', 'estrobilurina (QoI)'),
 'FRAC 12': ('fenilpirrol', 'fenilpirrol'),
 'FRAC 29': ('desacoplador', 'desacoplador da fosforilação oxidativa'),
 'FRAC M1': ('cúprico', 'cúprico (multissítio)'),
 'FRAC M2': ('enxofre (multissítio)', 'enxofre (multissítio)'),
 'FRAC M3': ('ditiocarbamato', 'ditiocarbamato (multissítio)'),
 'IRAC 1B': ('organofosforado', 'organofosforado (inibidor da acetilcolinesterase)'),
 'IRAC 2B': ('fenilpirazol', 'fenilpirazol (bloqueador do canal de cloro mediado por GABA)'),
 'IRAC 3A': ('piretroide', 'piretroide (modulador do canal de sódio)'),
 'IRAC 4A': ('neonicotinoide', 'neonicotinoide (agonista do receptor nicotínico)'),
 'IRAC 5': ('espinosina', 'espinosina (ativador alostérico do receptor nicotínico)'),
 'IRAC 6': ('avermectina', 'avermectina (ativador do canal de cloro)'),
 'IRAC 7C': ('juvenoide', 'análogo do hormônio juvenil'),
 'IRAC 15': ('benzoilureia', 'benzoilureia (inibidor da biossíntese de quitina)'),
 'IRAC 16': ('buprofezina', 'inibidor da biossíntese de quitina tipo 1'),
 'IRAC 21A': ('METI', 'inibidor do complexo I mitocondrial (METI)'),
 'IRAC 23': ('ácido tetrônico', 'ácido tetrônico (inibidor da acetil-CoA carboxilase)'),
 'IRAC 28': ('diamida', 'diamida (modulador do receptor de rianodina)'),
 'IRAC UN': ('modo de ação incerto', 'modo de ação incerto'),
 'IRAC UNF': ('fungo entomopatogênico', 'fungo entomopatogênico (modo de ação incerto)'),
 'IRAC N-2': ('avermectina (nematicida)', 'avermectina (modulador do canal de cloro)'),
 'IRAC N-UNB': ('bactéria', 'bactéria (modo de ação incerto)'),
}
_SIS = {'HRAC': 0, 'FRAC': 1, 'IRAC': 2}

def _ordem(cod):
    sis, resto = cod.split(' ', 1)
    m = re.match(r'([A-Z]+-?)?(\d+)?(.*)$', resto)
    pre, num, suf = m.group(1) or '', m.group(2), m.group(3)
    return (_SIS[sis], pre != '', pre, int(num) if num else 999, suf)

def _chave(alvo):
    """Alvo normalizado para comparar produtos: sem nome científico; nas daninhas, só a modalidade."""
    a = re.sub(r'\s*\([^)]*\)', '', alvo).strip().lower()
    if ' · ' in a:
        a = 'daninhas · ' + a.split(' · ', 1)[1].strip()
    return a

def U(cultura, alvo, dose, carencia, max_aplic, intervalo='', conferido=False, chave=None):
    return dict(cultura=cultura, alvo=alvo, chave=chave or _chave(alvo), dose=dose, carencia=carencia, max_aplic=max_aplic,
                intervalo=intervalo, conferido=conferido)

def UC(*a, **k):
    """Uso conferido: par cultura × alvo visto em bula pública do mesmo ingrediente."""
    return U(*a, conferido=True, **k)

def P(grupos, nomes_fazenda=None, avisos=(), alertas_fazenda=(), refs_fazenda=(), **k):
    g = sorted(set(grupos), key=_ordem)
    k.update(grupos=g, nomes_fazenda=list(nomes_fazenda or [k['nome']]), avisos=list(avisos),
             alertas_fazenda=list(alertas_fazenda), refs_fazenda=list(refs_fazenda),
             grupo=' + '.join(g) if g else '—',
             grupo_nome=(GRUPOS[g[0]][1] if len(g) == 1 else ' + '.join(GRUPOS[c][0] for c in g)) if g
                        else 'adjuvante (sem modo de ação)')
    return k

def A(ref, texto, alt=None):
    return dict(ref=ref, texto=texto, alt=alt)

PRODUTOS = [
 # ====================== produtos da fazenda (nome exato dos planos, do estoque e das ordens) ======================
 # Glifosato 480: carências da monografia Anvisa G01 (pós-emergência das infestantes): café 15 dias, mamão 3 dias; soja e milho em
 # pré-plantio (plantio direto) sem carência determinada. Café e mamão também vistos em bula pública (mamão até 2 aplicações/ano).
 P(id='glifosato-480', nome='Glifosato 480', ingrediente='glifosato (sal de isopropilamina)', concentracao='480 g/L (360 g/L e.a.)',
   formulacao='SL', classe='Herbicida', grupos=['HRAC 9'], tox=_T5, amb=_A3, reentrada='24 h',
   situacao='Vigente', situacao_nota='Reavaliação concluída pela Anvisa (RDC 441/2020): mantido com restrições.',
   usos=[UC('Soja', 'plantas daninhas · dessecação pré-plantio', '1,5–3,0 L/ha', _PRE, 1),
         UC('Milho', 'plantas daninhas · dessecação pré-plantio', '1,5–3,0 L/ha', _PRE, 1),
         UC('Café', 'plantas daninhas · jato dirigido na entrelinha', '2,0–4,0 L/ha', '15 dias', '2 por ano'),
         UC('Mamão', 'plantas daninhas · jato dirigido na entrelinha', '2,0–4,0 L/ha', '3 dias', '2 por ano')]),
 # 2,4-D 806: restrições da bula DMA 806 BR (2024-11) e da mitigação da reavaliação (RDC 284/2019): soja semeada 7 (argiloso) a
 # 15 dias (arenoso) após a aplicação; milho só até 25 cm; reentrada 24 h para até 2 h de atividade, 18 dias para 8 h.
 P(id='acido-24d-806', nome='2,4-D 806', ingrediente='2,4-D (sal dimetilamina)', concentracao='806 g/L (670 g/L e.a.)',
   formulacao='SL', classe='Herbicida', grupos=['HRAC 4'], tox=_T4, amb=_A3,
   reentrada='24 h (até 2 h de atividade) · 18 dias (8 h de atividade)',
   situacao='Vigente', situacao_nota='Reavaliação concluída pela Anvisa (RDC 284/2019): mantido com restrições.',
   avisos=['Soja: semear só 7 dias (solo argiloso) a 15 dias (solo arenoso) depois da aplicação.',
           'Milho: aplicar só até a planta atingir 25 cm.'],
   usos=[UC('Soja', 'folhas largas · dessecação pré-plantio (aplicar 7–15 dias antes da semeadura: argiloso 7, arenoso 15)',
            '0,8–1,5 L/ha', _PRE, 1),
         UC('Milho', 'folhas largas · pós-emergência (até o milho atingir 25 cm)', '0,4–1,0 L/ha', 'não determinada', 1,
            chave='daninhas · folhas largas pós-emergência')]),
 P(id='cletodim-240', nome='Cletodim 240', ingrediente='cletodim', concentracao='240 g/L', formulacao='EC', classe='Herbicida',
   grupos=['HRAC 1'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[U('Soja', 'gramíneas (capim-amargoso, capim-pé-de-galinha) · pós-emergência', '0,35–0,45 L/ha + óleo mineral', '60 dias', 1,
           chave='daninhas · gramíneas pós-emergência'),
         U('Feijão', 'gramíneas · pós-emergência', '0,35–0,45 L/ha + óleo mineral', '45 dias', 1,
           chave='daninhas · gramíneas pós-emergência')]),
 P(id='atrazina-500', nome='Atrazina 500', ingrediente='atrazina', concentracao='500 g/L', formulacao='SC', classe='Herbicida',
   grupos=['HRAC 5'], tox=_T5, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[U('Milho', 'folhas largas · pós-emergência inicial', '3,0–5,0 L/ha', 'não determinada', 1,
           chave='daninhas · folhas largas pós-emergência')]),
 # Diquat: feijão 1,5–2,0 L/ha e soja 1,0–2,0 L/ha na dessecação pré-colheita, carência de 7 dias (conferido em bula pública).
 P(id='diquat-200', nome='Diquat 200', ingrediente='diquate (dibrometo)', concentracao='200 g/L', formulacao='SL', classe='Herbicida',
   grupos=['HRAC 22'], tox=_T3, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[UC('Feijão', 'dessecação pré-colheita', '1,5–2,0 L/ha', '7 dias', 1),
         UC('Soja', 'dessecação pré-colheita', '1,0–2,0 L/ha', '7 dias', 1)]),
 # 'Fungicida A' = protioconazol + trifloxistrobina, como a AG-07 já declarava. Bula de referência de 19/08/2025 (ADAPAR 2025-10):
 # soja · ferrugem-asiática 0,4–0,5 L/ha (máx. 2, carência 30 dias), soja · mancha-alvo 0,4 L/ha; feijão · antracnose e
 # mancha-angular 0,4–0,5 L/ha, ferrugem 0,4 L/ha, máx. 3 a cada 14 dias, carência 15 dias. Categoria 4, classe ambiental II.
 P(id='fungicida-a', nome='Fungicida A', ingrediente='protioconazol + trifloxistrobina', concentracao='175 + 150 g/L',
   formulacao='SC', classe='Fungicida', grupos=['FRAC 3', 'FRAC 11'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Vigente',
   situacao_nota='',
   alertas_fazenda=[A('SOJA-AT · T1-B (1ª aplicação)', 'Ajuste exclusivo de 0,60 L/ha acima da faixa da bula (0,4–0,5 L/ha).')],
   usos=[UC('Soja', 'ferrugem-asiática', '0,4–0,5 L/ha', '30 dias', 2, '14 dias'),
         UC('Soja', 'mancha-alvo', '0,4 L/ha', '30 dias', 2, '14 dias'),
         UC('Feijão', 'antracnose', '0,4–0,5 L/ha', '15 dias', 3, '14 dias'),
         UC('Feijão', 'mancha-angular', '0,4–0,5 L/ha', '15 dias', 3, '14 dias'),
         UC('Feijão', 'ferrugem', '0,4 L/ha', '15 dias', 3, '14 dias')]),
 # 'Fungicida C' (escolha deste módulo): azoxistrobina + ciproconazol. Café · ferrugem conferido em bula pública do mesmo
 # ingrediente: 0,5 L/ha a cada 60 dias ou 0,75 L/ha a cada 90 dias, carência de 30 dias. Soja · ferrugem: não conferido.
 P(id='fungicida-c', nome='Fungicida C', ingrediente='azoxistrobina + ciproconazol', concentracao='200 + 80 g/L', formulacao='SC',
   classe='Fungicida', grupos=['FRAC 11', 'FRAC 3'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   # dose do plano CAFE-AR (0,80 L/ha) acima da bula: a AG-07 calcula ao vivo ("Acima da bula: máx. 0,75 L/ha"); sem alerta fixo repetido
   usos=[UC('Café', 'ferrugem', '0,5–0,75 L/ha', '30 dias', 2, '60–90 dias'),
         U('Soja', 'ferrugem-asiática', '0,3 L/ha', '30 dias', 2, '14 dias')]),
 # 'Fungicida TS' (escolha deste módulo): fludioxonil + metalaxil-M, tratamento de sementes. O plano SOJA-AT usa 0,10 L em
 # "Tratamento de sementes", coerente com 100 mL/100 kg de sementes. Soja, milho e feijão conferidos em bula pública.
 P(id='fungicida-ts', nome='Fungicida TS', ingrediente='fludioxonil + metalaxil-M', concentracao='25 + 10 g/L', formulacao='FS',
   classe='Fungicida', grupos=['FRAC 12', 'FRAC 4'], tox=_T5, amb=_A2, reentrada='não se aplica (TS)', situacao='Vigente',
   situacao_nota='',
   usos=[UC('Soja', 'podridões de sementes e tombamento (Rhizoctonia, Fusarium, Pythium, Phomopsis)', '100 mL/100 kg de sementes', _TS, 1),
         UC('Milho', 'podridões de sementes (Fusarium, Pythium)', '100 mL/100 kg de sementes', _TS, 1),
         UC('Feijão', 'antracnose e podridões de sementes', '100 mL/100 kg de sementes', _TS, 1)]),
 # Tebuconazol: no mamão as bulas públicas registram só antracnose (até 6 aplicações a cada 14 dias, carência 7 dias). O uso
 # "mamão · oídio" foi RETIRADO (não registrado); a atividade i10 do MAMAO-IMP cita oídio → alerta e alternativa (enxofre).
 P(id='tebuconazol-200-ec', nome='Tebuconazol 200 EC', ingrediente='tebuconazol', concentracao='200 g/L', formulacao='EC',
   classe='Fungicida', grupos=['FRAC 3'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   alertas_fazenda=[A('MAMAO-IMP · Fungicida preventivo (antracnose e oídio)',
                      'Oídio sem registro neste produto no mamão; alternativa registrada: Enxofre 800 WG.', 'enxofre-800-wg')],
   usos=[UC('Mamão', 'antracnose', '0,5–1,0 L/ha', '7 dias', 6, '14 dias')]),
 # 'Inseticida B' = acefato, como a AG-07 já declarava. Soja (percevejo-marrom), milho (percevejo-barriga-verde, pulgão) e feijão
 # (mosca-branca, carência 14 dias) conferidos em bula pública; reentrada de 48 h. Formulação SP (pó): dose em kg/ha.
 P(id='inseticida-b', nome='Inseticida B', ingrediente='acefato', concentracao='750 g/kg', formulacao='SP', classe='Inseticida',
   grupos=['IRAC 1B'], tox=_T4, amb=_A3, reentrada='48 h',
   situacao='Vigente', situacao_nota='Reavaliação concluída pela Anvisa (RDC 45/2013): mantido com restrições.',
   alertas_fazenda=[A('SOJA-AT e MILHO-SF · Inseticida', 'Planos em 0,30 L/ha: produto em pó (SP), dose da bula em kg/ha (0,8–1,0 kg/ha).'),
                    A('MILHO-SF · Inseticida (55 DAP)', 'Época de lagarta-do-cartucho, alvo sem registro neste produto.',
                      'clorantraniliprole-200-sc')],
   usos=[UC('Soja', 'percevejo-marrom', '0,8–1,0 kg/ha', '14 dias', 2, '10 dias'),
         UC('Milho', 'percevejo-barriga-verde', '0,8–1,0 kg/ha', '35 dias', 1),
         UC('Milho', 'pulgão-do-milho', '0,8–1,0 kg/ha', '35 dias', 1),
         UC('Feijão', 'mosca-branca', '1,0 kg/ha', '14 dias', 2, '10 dias')]),
 # Acetamiprido em mamão · mosca-branca conferido em bulas públicas (carência de 3 a 5 dias conforme o produto). Sem alternativa de
 # outro grupo registrada para mamão · mosca-branca encontrada (espiromesifeno no mamão só ácaro-rajado; a mistura acetamiprido +
 # piriproxifem de referência tem no mamão só cigarrinha-verde). MAMAO-IMP i6 "pulgão e ácaro": pulgão sem registro e, segundo a
 # Embrapa, não coloniza o mamoeiro e transmite o vírus da mancha-anelar de forma não persistente (inseticida não evita a virose);
 # o acetamiprido não age sobre ácaro (na mesma atividade, a abamectina cobre ácaro).
 P(id='acetamiprido-200-sp', nome='Acetamiprido 200 SP', ingrediente='acetamiprido', concentracao='200 g/kg', formulacao='SP',
   classe='Inseticida', grupos=['IRAC 4A'], tox=_T4, amb=_A3, reentrada='24 h', situacao='Vigente', situacao_nota='',
   alertas_fazenda=[A('MAMAO-IMP · Controle de pulgão e ácaro',
                      'Pulgão sem registro neste produto (inseticida não evita a mancha-anelar); ácaro fora do espectro do acetamiprido.')],
   usos=[UC('Mamão', 'mosca-branca', '0,25–0,40 kg/ha', '3 dias', 3, '7 dias')]),
 # Abamectina em mamão (ácaro-rajado e ácaro-branco) conferida em bulas públicas: 400–1200 mL/ha, até 2 aplicações a cada 10 dias,
 # carência de 14 dias. Cochonilha não registrada (na base só a buprofezina cobre cochonilha do mamão).
 P(id='abamectina-18-ec', nome='Abamectina 18 EC', ingrediente='abamectina', concentracao='18 g/L', formulacao='EC',
   classe='Inseticida e acaricida', grupos=['IRAC 6'], tox=_T3, amb=_A2, reentrada='24 h', situacao='Vigente',
   situacao_nota='Reavaliação concluída pela Anvisa (RDC 442/2020): mantido com restrições.',
   alertas_fazenda=[A('MAMAO-PROD · Controle de ácaro e cochonilha (12/10 · OS-0504)',
                      'Colheita em 20/10, a 8 dias da aplicação: carência da bula é 14 dias.'),
                    A('MAMAO-PROD · Controle de ácaro e cochonilha (12/10 · OS-0504)',
                      'Cochonilha sem registro neste produto; alternativa registrada: Buprofezina 250 WP.', 'buprofezina-250-wp')],
   usos=[UC('Mamão', 'ácaro-rajado', '0,4–1,2 L/ha', '14 dias', 2, '10 dias'),
         UC('Mamão', 'ácaro-branco', '0,4–1,2 L/ha', '14 dias', 2, '10 dias')]),
 # 'Acaricida D' (escolha deste módulo): espiromesifeno. Mamão · ácaro-rajado (400–800 mL/ha, até 3 aplicações a cada 7 dias),
 # feijão e soja · mosca-branca conferidos em bula pública. No mamão a bula traz só ácaro-rajado (sem mosca-branca).
 P(id='acaricida-d', nome='Acaricida D', ingrediente='espiromesifeno', concentracao='240 g/L', formulacao='SC',
   classe='Inseticida e acaricida', grupos=['IRAC 23'], tox=_TN, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[UC('Mamão', 'ácaro-rajado', '0,4–0,8 L/ha', '7 dias', 3, '7 dias'),
         UC('Feijão', 'mosca-branca', '0,4–0,6 L/ha', '14 dias', 2, '7 dias'),
         UC('Soja', 'mosca-branca', '0,4–0,6 L/ha', '14 dias', 2, '7 dias')]),
 # Adjuvantes: registrados no MAPA e consultáveis no AGROFIT; sem modo de ação e sem carência própria.
 P(id='oleo-mineral', nome='Óleo mineral', ingrediente='óleo mineral emulsionável', concentracao='756 g/L', formulacao='EC',
   classe='Adjuvante', grupos=[], tox=_T5, amb=_A4, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[U('Soja', 'adjuvante de calda (herbicidas e fungicidas)', '0,5 L/ha (0,25–0,5 % v/v)', _ADJ, _ADJ),
         U('Milho', 'adjuvante de calda (herbicidas)', '0,5 L/ha (0,25–0,5 % v/v)', _ADJ, _ADJ),
         U('Feijão', 'adjuvante de calda (herbicidas)', '0,5 L/ha (0,25–0,5 % v/v)', _ADJ, _ADJ),
         U('Mamão', 'adjuvante de calda (acaricidas e inseticidas)', '0,5–1,0 L/ha', _ADJ, _ADJ)]),
 # 'Adjuvante espalhante' (escolha deste módulo): organossiliconado, coerente com 0,25 L/ha em ~200 L/ha de calda (≈ 0,1 % v/v).
 P(id='adjuvante-espalhante', nome='Adjuvante espalhante', ingrediente='copolímero poliéter-polimetilsiloxano (organossiliconado)',
   concentracao='1000 g/L', formulacao='SL', classe='Adjuvante', grupos=[], tox=_T4, amb=_A3, reentrada='24 h',
   situacao='Vigente', situacao_nota='',
   usos=[U('Soja', 'adjuvante de calda (fungicidas)', '0,1–0,25 L/ha (0,05–0,1 % v/v)', _ADJ, _ADJ),
         U('Milho', 'adjuvante de calda (fungicidas)', '0,1–0,25 L/ha (0,05–0,1 % v/v)', _ADJ, _ADJ),
         U('Feijão', 'adjuvante de calda (fungicidas)', '0,1–0,25 L/ha (0,05–0,1 % v/v)', _ADJ, _ADJ),
         U('Café', 'adjuvante de calda (fungicidas)', '0,1–0,25 L/ha (0,05–0,1 % v/v)', _ADJ, _ADJ)]),
 # 'TS nematicida (abamectina)' da REC-014 v2 / OS-0420 → ficha Abamectina 500 FS (nomes_fazenda). Bula de referência (soja):
 # nematoide-das-galhas (Meloidogyne incognita) e das-lesões (Pratylenchus brachyurus), 125 mL/100 kg; o CISTO (Heterodera
 # glycines) NÃO está registrado para este ingrediente em TS. Grupo nematicida IRAC N-2; como inseticida, o mesmo ingrediente é IRAC 6.
 P(id='abamectina-500-fs', nome='Abamectina 500 FS', nomes_fazenda=['Abamectina 500 FS', 'TS nematicida (abamectina)'],
   ingrediente='abamectina', concentracao='500 g/L', formulacao='FS', classe='Nematicida', grupos=['IRAC N-2'], tox=_T3, amb=_A2,
   reentrada='não se aplica (TS)', situacao='Vigente',
   situacao_nota='Reavaliação concluída pela Anvisa (RDC 442/2020): mantido com restrições.',
   alertas_fazenda=[A('REC-014 v2 · OS-0420', 'Soja · nematoide-de-cisto: alvo não registrado para este ingrediente; '
                      'alternativa registrada: Pasteuria nishizawae FS (IRAC N-UNB).', 'pasteuria-nishizawae-fs'),
                    A('REC-014 v2 · OS-0420', 'Dose da recomendação 100 mL/100 kg de semente; bula de referência 125 mL/100 kg.')],
   refs_fazenda=[dict(ref='REC-014 v2', href='AG-04det.dc.html', texto='TS nematicida (abamectina) · 100 mL/100 kg de semente'),
                 dict(ref='OS-0420', href='CA-01x-os0420.dc.html', texto='Plantio · Soja 58 W · T4 · TS nematicida (abamectina)')],
   usos=[UC('Soja', 'nematoide-das-galhas (Meloidogyne incognita)', '125 mL/100 kg de sementes', _TS, 1),
         UC('Soja', 'nematoide-das-lesões (Pratylenchus brachyurus)', '125 mL/100 kg de sementes', _TS, 1)]),

 # ====================== alternativas de outro grupo de ação (manejo de resistência) ======================
 # --- Soja · ferrugem-asiática (e mamão · antracnose) ---
 # Mancozebe 750 WG: soja · ferrugem-asiática 1,5–3,0 kg/ha, carência 30 dias (conferido); mancozebe consta entre os registrados
 # para antracnose do mamão; varíola do mamão não conferida.
 P(id='mancozebe-750-wg', nome='Mancozebe 750 WG', ingrediente='mancozebe', concentracao='750 g/kg', formulacao='WG',
   classe='Fungicida', grupos=['FRAC M3'], tox=_T5, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[UC('Soja', 'ferrugem-asiática', '1,5–3,0 kg/ha', '30 dias', 3, '14 dias'),
         UC('Mamão', 'antracnose', '2,0–3,0 kg/ha', '14 dias', 4, '14 dias'),
         U('Mamão', 'varíola (pinta-preta)', '2,0–3,0 kg/ha', '14 dias', 4, '14 dias')]),
 # Fluxapiroxade + piraclostrobina 167 + 333 g/L: soja · ferrugem-asiática 300–350 mL/ha, até 2 aplicações (conferido).
 # Divide o QoI (FRAC 11) com o Fungicida A e o Fungicida C: não é rotação para eles.
 P(id='fluxapiroxade-piraclostrobina-sc', nome='Fluxapiroxade + piraclostrobina 167+333 SC',
   ingrediente='fluxapiroxade + piraclostrobina', concentracao='167 + 333 g/L', formulacao='SC', classe='Fungicida',
   grupos=['FRAC 7', 'FRAC 11'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[UC('Soja', 'ferrugem-asiática', '0,30–0,35 L/ha', '30 dias', 2, '14 dias'),
         U('Soja', 'mancha-alvo', '0,30–0,35 L/ha', '30 dias', 2, '14 dias')]),
 # Epoxiconazol + piraclostrobina 50 + 133 g/L: café · ferrugem (1,5 L/ha e depois 1,0 L/ha, até 2 aplicações) conferido.
 # Epoxiconazol em reavaliação toxicológica na Anvisa (edital de chamamento nº 17, de 30/11/2020).
 P(id='epoxiconazol-piraclostrobina-se', nome='Epoxiconazol + piraclostrobina 50+133 SE',
   ingrediente='epoxiconazol + piraclostrobina', concentracao='50 + 133 g/L', formulacao='SE', classe='Fungicida',
   grupos=['FRAC 3', 'FRAC 11'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Em reavaliação',
   situacao_nota='Epoxiconazol em reavaliação toxicológica pela Anvisa desde 2020; uso conforme a bula vigente.',
   usos=[UC('Café', 'ferrugem', '1,0–1,5 L/ha', '45 dias', 2, '60 dias'),
         U('Soja', 'ferrugem-asiática', '0,5 L/ha', '30 dias', 2, '14 dias')]),
 # --- Café · ferrugem ---
 # Oxicloreto de cobre: café · ferrugem preventivo, até 5 aplicações a cada 30 dias, FRAC M1 (conferido em bula pública).
 P(id='oxicloreto-cobre-840-wp', nome='Oxicloreto de cobre 840 WP', ingrediente='oxicloreto de cobre', concentracao='840 g/kg',
   formulacao='WP', classe='Fungicida', grupos=['FRAC M1'], tox=_T4, amb=_A3, reentrada='24 h', situacao='Vigente',
   situacao_nota='',
   usos=[UC('Café', 'ferrugem', '2,0–5,0 kg/ha', '7 dias', 5, '30 dias')]),
 # --- Café · mancha-de-phoma (VIS-016, DIA-010 "Intervir já") ---
 # Boscalida 500 WG: café · Phoma costaricensis 150 g/ha, máx. 3 aplicações (conferido em bula pública da boscalida 500 g/kg);
 # mancha-de-ascochyta, carência 45 dias, Categoria 5 e classe III conforme a revisão de 01/10 (ficha pública do mesmo produto).
 # Única opção para phoma nesta base: a rotação mostra SEM_ALTERNATIVA.
 P(id='boscalida-500-wg', nome='Boscalida 500 WG', ingrediente='boscalida', concentracao='500 g/kg', formulacao='WG',
   classe='Fungicida', grupos=['FRAC 7'], tox=_T5, amb=_A3, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[UC('Café', 'mancha-de-phoma (Phoma costaricensis)', '150 g/ha', '45 dias', 3),
         UC('Café', 'mancha-de-ascochyta (Ascochyta coffeae)', '150 g/ha', '45 dias', 3)]),
 # --- Mamão · antracnose, oídio e ácaro-branco ---
 # Azoxistrobina consta entre os fungicidas citados para antracnose do mamão; par não conferido em bula.
 P(id='azoxistrobina-250-sc', nome='Azoxistrobina 250 SC', ingrediente='azoxistrobina', concentracao='250 g/L', formulacao='SC',
   classe='Fungicida', grupos=['FRAC 11'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[U('Mamão', 'antracnose', '0,3–0,4 L/ha', '7 dias', 3, '14 dias')]),
 # Metalaxil-M + mancozebe: RETIRADO. O mamão não consta das bulas de referência dessa composição (WP e WG) e a podridão-do-pé não é
 # alvo monitorado na fazenda.
 # Enxofre 800 WG: bula de referência (rev10, ADAPAR 2026-07) conferida: mamão · oídio (Oidium caricae) e ácaro-branco
 # (Polyphagotarsonemus latus), 400 g/100 L (calda 1000 L/ha), repetir conforme a necessidade; intervalo de segurança "sem
 # restrições"; reentrada após secagem da calda (mín. 24 h); Categoria 5; FRAC M2 (IRAC UN como acaricida); não aplicar na florada
 # nem nas horas mais quentes. Classe ambiental III conforme a revisão (o texto extraído não mostrou a marcação).
 # Discordância parcial com a revisão: a regra "30 dias antes ou depois de óleo" está na bula só para CITROS (e o caju veta óleo na
 # calda; a banana até recomenda óleo). Para o mamão a bula não traz essa restrição → vira alerta para confirmar, não regra.
 P(id='enxofre-800-wg', nome='Enxofre 800 WG', ingrediente='enxofre', concentracao='800 g/kg', formulacao='WG',
   classe='Fungicida e acaricida', grupos=['FRAC M2', 'IRAC UN'], tox=_T5, amb=_A3, reentrada='24 h (após secagem da calda)',
   situacao='Vigente', situacao_nota='',
   avisos=['Não aplicar na florada nem nas horas mais quentes do dia.',
           'Óleo mineral: restrição varia por cultura na bula (30 dias de intervalo nos citros).'],
   alertas_fazenda=[A('MAMAO-PROD · Controle de ácaro e cochonilha (12/10)',
                      'Aplica óleo mineral: confirmar na bula o intervalo entre enxofre e óleo no mamão.')],
   usos=[UC('Mamão', 'oídio (Oidium caricae)', '400 g/100 L de água', 'sem restrições', 'conforme a necessidade'),
         UC('Mamão', 'ácaro-branco (Polyphagotarsonemus latus)', '400 g/100 L de água', 'sem restrições', 'conforme a necessidade')]),
 # --- Soja · percevejo-marrom / Milho · percevejo, lagarta-do-cartucho e cigarrinha ---
 # Tiametoxam + lambda-cialotrina 141 + 106 g/L (ZC), bula de referência de 16/02/2024 lida: soja · percevejo-marrom 200 mL/ha,
 # milho · lagarta-do-cartucho 200–250 mL/ha e percevejo-barriga-verde 150–250 mL/ha, máx. 2; carência soja 30, milho 40, feijão
 # 15 dias; Categoria 4; classe ambiental I. Milho · cigarrinha: a revisão aponta registro em versão posterior (ADAPAR 2024-10);
 # não aparece na versão lida → não conferido. Divide o IRAC 4A com o acetamiprido: não é rotação para ele.
 P(id='tiametoxam-lambda-zc', nome='Tiametoxam + lambda-cialotrina 141+106 ZC', ingrediente='tiametoxam + lambda-cialotrina',
   concentracao='141 + 106 g/L', formulacao='ZC', classe='Inseticida', grupos=['IRAC 4A', 'IRAC 3A'], tox=_T4, amb=_A1,
   reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[UC('Soja', 'percevejo-marrom', '0,20 L/ha', '30 dias', 2),
         UC('Milho', 'lagarta-do-cartucho', '0,20–0,25 L/ha', '40 dias', 2),
         UC('Milho', 'percevejo-barriga-verde', '0,15–0,25 L/ha', '40 dias', 2),
         U('Milho', 'cigarrinha-do-milho', '0,20–0,25 L/ha', '40 dias', 2, '7 dias')]),
 # Etiprole: soja · percevejo-marrom conferido em bula pública; etiprole consta entre os ingredientes citados para D. maidis
 # (par milho · cigarrinha não conferido em bula).
 P(id='etiprole-200-sc', nome='Etiprole 200 SC', ingrediente='etiprole', concentracao='200 g/L', formulacao='SC', classe='Inseticida',
   grupos=['IRAC 2B'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[UC('Soja', 'percevejo-marrom', '0,75–1,0 L/ha', '21 dias', 2, '10 dias'),
         U('Milho', 'cigarrinha-do-milho', '0,5–0,75 L/ha', '30 dias', 2, '7 dias')]),
 # --- Lagartas (soja, milho) e bicho-mineiro (café) ---
 # Clorantraniliprole 200 SC: soja (falsa-medideira, Helicoverpa), milho (lagarta-do-cartucho) e café (bicho-mineiro, 75 mL/ha)
 # conferidos em bula pública; carência de 14 dias em café, milho e soja.
 P(id='clorantraniliprole-200-sc', nome='Clorantraniliprole 200 SC', ingrediente='clorantraniliprole', concentracao='200 g/L',
   formulacao='SC', classe='Inseticida', grupos=['IRAC 28'], tox=_T5, amb=_A2, reentrada='24 h', situacao='Vigente',
   situacao_nota='',
   usos=[UC('Soja', 'lagarta-falsa-medideira', '50–75 mL/ha', '14 dias', 2, '14 dias'),
         UC('Soja', 'Helicoverpa armigera', '75–100 mL/ha', '14 dias', 2, '14 dias'),
         UC('Milho', 'lagarta-do-cartucho', '100–150 mL/ha', '14 dias', 2, '14 dias'),
         UC('Café', 'bicho-mineiro', '75 mL/ha', '14 dias', 2, '30 dias')]),
 # Tiametoxam 250 WG: bula de referência de 19/12/2024 (ADAPAR 2025-03) lida: café · bicho-mineiro (Leucoptera coffeella)
 # 1.400–2.000 g/ha em esguicho no solo sob a copa (50 mL/planta) ou 2.000 g/ha via gotejo, 1 aplicação; carência café 90 dias;
 # Categoria 5; classe ambiental III; reentrada 24 h. Dá ao bicho-mineiro uma opção fora do IRAC 28 (diamidas).
 P(id='tiametoxam-250-wg', nome='Tiametoxam 250 WG', ingrediente='tiametoxam', concentracao='250 g/kg', formulacao='WG',
   classe='Inseticida', grupos=['IRAC 4A'], tox=_T5, amb=_A3, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[UC('Café', 'bicho-mineiro (Leucoptera coffeella)', '1,4–2,0 kg/ha · esguicho no solo sob a copa (50 mL/planta) ou gotejo',
            '90 dias', '1 por ano')]),
 # Espinetoram 250 WG: soja (Helicoverpa 100–150, lagarta-do-cartucho 150–200) e milho (lagarta-do-cartucho 50–100) conferidos;
 # até 4 aplicações por ciclo.
 P(id='espinetoram-250-wg', nome='Espinetoram 250 WG', ingrediente='espinetoram', concentracao='250 g/kg', formulacao='WG',
   classe='Inseticida', grupos=['IRAC 5'], tox=_T5, amb=_A3, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[UC('Soja', 'Helicoverpa armigera', '100–150 g/ha', '14 dias', 4, '7 dias'),
         UC('Soja', 'lagarta-do-cartucho', '150–200 g/ha', '14 dias', 4, '7 dias'),
         UC('Milho', 'lagarta-do-cartucho', '50–100 g/ha', '14 dias', 4, '7 dias')]),
 P(id='lufenurom-50-ec', nome='Lufenurom 50 EC', ingrediente='lufenurom', concentracao='50 g/L', formulacao='EC', classe='Inseticida',
   grupos=['IRAC 15'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[U('Soja', 'lagarta-da-soja', '0,15–0,30 L/ha', '35 dias', 2),
         U('Milho', 'lagarta-do-cartucho', '0,30 L/ha', '35 dias', 2)]),
 # Mesmo grupo da abamectina (IRAC 6): não é rotação para quem já usa avermectina.
 P(id='emamectina-50-wg', nome='Benzoato de emamectina 50 WG', ingrediente='benzoato de emamectina', concentracao='50 g/kg',
   formulacao='WG', classe='Inseticida', grupos=['IRAC 6'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Vigente',
   situacao_nota='',
   usos=[U('Soja', 'Helicoverpa armigera', '0,15–0,20 kg/ha', '14 dias', 2, '7 dias'),
         U('Milho', 'lagarta-do-cartucho', '0,15–0,20 kg/ha', '14 dias', 2, '7 dias')]),
 # --- Plantas daninhas (soja, milho, feijão) ---
 # Glufosinato em feijão · dessecação pré-colheita conferido na revisão de 01/10 (bula pública do glufosinato 200 SL): carência
 # 5 dias, 1,8 L/ha (grão para consumo) a 2,0 L/ha (campo de semente). Soja pré-plantio não conferido.
 P(id='glufosinato-200-sl', nome='Glufosinato de amônio 200 SL', ingrediente='glufosinato de amônio', concentracao='200 g/L',
   formulacao='SL', classe='Herbicida', grupos=['HRAC 10'], tox=_T4, amb=_A3, reentrada='24 h', situacao='Vigente',
   situacao_nota='',
   usos=[U('Soja', 'plantas daninhas · dessecação pré-plantio', '2,0–2,5 L/ha', _PRE, 1),
         UC('Feijão', 'dessecação pré-colheita', '1,8 L/ha (consumo) – 2,0 L/ha (semente)', '5 dias', 1)]),
 P(id='saflufenacil-700-wg', nome='Saflufenacil 700 WG', ingrediente='saflufenacil', concentracao='700 g/kg', formulacao='WG',
   classe='Herbicida', grupos=['HRAC 14'], tox=_T5, amb=_A3, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[U('Soja', 'folhas largas · dessecação pré-plantio', '35–70 g/ha', _PRE, 1),
         U('Milho', 'folhas largas · dessecação pré-plantio', '35–70 g/ha', _PRE, 1)]),
 P(id='s-metolacloro-960-ec', nome='S-metolacloro 960 EC', ingrediente='S-metolacloro', concentracao='960 g/L', formulacao='EC',
   classe='Herbicida', grupos=['HRAC 15'], tox=_T5, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[U('Soja', 'gramíneas e folhas largas · pré-emergência', '1,25–1,75 L/ha', 'não determinada (pré-emergência)', 1),
         U('Milho', 'gramíneas e folhas largas · pré-emergência', '1,25–1,75 L/ha', 'não determinada (pré-emergência)', 1),
         U('Feijão', 'gramíneas e folhas largas · pré-emergência', '1,0–1,5 L/ha', 'não determinada (pré-emergência)', 1)]),
 P(id='tembotriona-420-sc', nome='Tembotriona 420 SC', ingrediente='tembotriona', concentracao='420 g/L', formulacao='SC',
   classe='Herbicida', grupos=['HRAC 27'], tox=_T5, amb=_A3, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[U('Milho', 'folhas largas e gramíneas · pós-emergência', '0,18–0,24 L/ha + adjuvante', 'não determinada', 1,
           chave='daninhas · folhas largas pós-emergência')]),
 P(id='nicosulfurom-40-sc', nome='Nicosulfurom 40 SC', ingrediente='nicosulfurom', concentracao='40 g/L', formulacao='SC',
   classe='Herbicida', grupos=['HRAC 2'], tox=_T5, amb=_A3, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[U('Milho', 'gramíneas · pós-emergência', '1,0–1,5 L/ha', 'não determinada', 1,
           chave='daninhas · gramíneas pós-emergência')]),
 # --- Nematoide-de-cisto via tratamento de sementes (soja) ---
 # Pasteuria nishizawae: nematicida microbiológico registrado para TS de soja contra Heterodera glycines (conferido). Grupo IRAC
 # N-UNB (bactérias de modo de ação incerto). Formulação, concentração e dose demonstrativas.
 P(id='pasteuria-nishizawae-fs', nome='Pasteuria nishizawae FS', ingrediente='Pasteuria nishizawae (bactéria)',
   concentracao='esporos/mL (ver bula)', formulacao='FS', classe='Nematicida', grupos=['IRAC N-UNB'], tox=_TN, amb=_A4,
   reentrada='não se aplica (TS)', situacao='Vigente', situacao_nota='',
   usos=[UC('Soja', 'nematoide-de-cisto (Heterodera glycines)', '0,3 L/100 kg de sementes', _TS, 1)]),
 # --- Café · broca / Milho · cigarrinha (biológico) ---
 # Beauveria bassiana: café · broca-do-café conferido (vários produtos; ex.: 3 pulverizações a cada 25–30 dias; 0,5–1,5 kg/ha);
 # milho · cigarrinha: produtos à base de B. bassiana são usados contra D. maidis (registro do isolado não conferido).
 P(id='beauveria-bassiana-wp', nome='Beauveria bassiana WP', ingrediente='Beauveria bassiana (fungo entomopatogênico)',
   concentracao='≥ 1 × 10⁹ UFC/g', formulacao='WP', classe='Inseticida', grupos=['IRAC UNF'], tox=_TN, amb=_A4,
   reentrada='após secagem da calda', situacao='Vigente', situacao_nota='',
   usos=[UC('Café', 'broca-do-café', '0,5–1,5 kg/ha', 'não determinada', 3, '25–30 dias'),
         U('Milho', 'cigarrinha-do-milho', '0,5–1,0 kg/ha', 'não determinada', 3, '7 dias')]),
 # --- Feijão · mosca-branca ---
 # Piriproxifem: feijão · mosca-branca 250 mL/ha, até 2 aplicações, carência 14 dias (conferido em bula pública).
 P(id='piriproxifem-100-ec', nome='Piriproxifem 100 EC', ingrediente='piriproxifem', concentracao='100 g/L', formulacao='EC',
   classe='Inseticida', grupos=['IRAC 7C'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[UC('Feijão', 'mosca-branca', '0,25 L/ha', '14 dias', 2)]),
 # Ciantraniliprole 100 OD: feijão · mosca-branca (500–750 mL/ha), café · bicho-mineiro (500–700 mL/ha) e café · broca-do-café
 # conferidos em bula pública (Não classificado, classe ambiental III). Mamão não consta.
 P(id='ciantraniliprole-100-od', nome='Ciantraniliprole 100 OD', ingrediente='ciantraniliprole', concentracao='100 g/L',
   formulacao='OD', classe='Inseticida', grupos=['IRAC 28'], tox=_TN, amb=_A3, reentrada='24 h', situacao='Vigente',
   situacao_nota='',
   usos=[UC('Feijão', 'mosca-branca', '0,50–0,75 L/ha', '7 dias', 2, '7 dias'),
         UC('Café', 'bicho-mineiro', '0,50–0,70 L/ha', '7 dias', 2, '30 dias'),
         UC('Café', 'broca-do-café', '1,0–1,5 L/ha', '7 dias', 2, '30 dias')]),
 # --- Feijão e soja · mofo-branco e antracnose ---
 # Fluazinam 500 SC: feijão · mofo-branco 1,0–1,5 L/ha e soja 0,75–1,0 L/ha, carência 28 dias, Categoria 4 (conferido).
 P(id='fluazinam-500-sc', nome='Fluazinam 500 SC', ingrediente='fluazinam', concentracao='500 g/L', formulacao='SC',
   classe='Fungicida', grupos=['FRAC 29'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[UC('Feijão', 'mofo-branco', '1,0–1,5 L/ha', '28 dias', 3, '7–10 dias'),
         UC('Soja', 'mofo-branco', '0,75–1,0 L/ha', '28 dias', 2, '10 dias')]),
 # Tiofanato-metílico 500 SC: feijão · antracnose 500–750 mL/ha e soja · mofo-branco conferidos em bula pública. Em reavaliação
 # toxicológica na Anvisa (edital de chamamento nº 04, de 10/03/2020). Sucessor natural do carbendazim (proibido em 2022), mesmo grupo.
 P(id='tiofanato-metilico-500-sc', nome='Tiofanato-metílico 500 SC', ingrediente='tiofanato-metílico', concentracao='500 g/L',
   formulacao='SC', classe='Fungicida', grupos=['FRAC 1'], tox=_T5, amb=_A3, reentrada='24 h', situacao='Em reavaliação',
   situacao_nota='Tiofanato-metílico em reavaliação toxicológica pela Anvisa desde 2020; uso conforme a bula vigente.',
   usos=[UC('Feijão', 'antracnose', '0,50–0,75 L/ha', '14 dias', 2, '10 dias'),
         UC('Soja', 'mofo-branco', '1,0 L/ha', '14 dias', 2, '10 dias')]),
 # --- Mamão · ácaro-rajado e cochonilha ---
 # Fenpiroximato consta entre os ingredientes citados para ácaro-rajado no mamão; par não conferido em bula.
 P(id='fenpiroximato-50-sc', nome='Fenpiroximato 50 SC', ingrediente='fenpiroximato', concentracao='50 g/L', formulacao='SC',
   classe='Acaricida', grupos=['IRAC 21A'], tox=_T4, amb=_A2, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[U('Mamão', 'ácaro-rajado', '100 mL/100 L de água', '7 dias', 2, '15 dias')]),
 # Buprofezina 250 WP: mamão · cochonilha (Aonidiella comperei), até 3 aplicações a cada 10 dias (conferido em bula pública).
 P(id='buprofezina-250-wp', nome='Buprofezina 250 WP', ingrediente='buprofezina', concentracao='250 g/kg', formulacao='WP',
   classe='Inseticida', grupos=['IRAC 16'], tox=_T5, amb=_A3, reentrada='24 h', situacao='Vigente', situacao_nota='',
   usos=[UC('Mamão', 'cochonilha (Aonidiella comperei)', '100–150 g/100 L de água', '14 dias', 3, '10 dias')]),

 # ====================== registro cancelado ======================
 # Paraquate: proibido no Brasil a partir de 22/09/2020 (Anvisa, RDC 177/2017; decisão mantida em 2020). Era o dessecante usual
 # do feijão e da soja; hoje a fazenda usa o Diquat 200 (mesmo grupo HRAC 22). Usos mantidos só como histórico do registro.
 P(id='paraquate-200-sl', nome='Paraquate 200 SL', ingrediente='paraquate (dicloreto)', concentracao='200 g/L', formulacao='SL',
   classe='Herbicida', grupos=['HRAC 22'], tox=_T2, amb=_A2, reentrada='24 h', situacao='Cancelado',
   situacao_nota='Proibido no Brasil desde 22/09/2020 (Anvisa, RDC 177/2017): uso e comércio vedados.',
   usos=[UC('Feijão', 'dessecação pré-colheita', '1,5–2,0 L/ha', '7 dias', 1),
         UC('Soja', 'dessecação pré-colheita', '1,5–2,0 L/ha', '7 dias', 1),
         UC('Soja', 'plantas daninhas · dessecação pré-plantio', '1,5–2,0 L/ha', _PRE, 1)]),
]

# Alvos monitorados na fazenda sem produto (ou sem rotação) nesta base: a consulta deve dizer isso, não ficar vazia.
LACUNAS = [
 dict(cultura='Feijão', alvo='percevejo-marrom', ref='VIS-006 · P1 Feijão',
      texto='Nenhum produto desta base tem registro para percevejo no feijão; conferir no AGROFIT oficial.'),
 dict(cultura='Mamão', alvo='mosca-branca', ref='MAMAO-PROD · Controle de mosca-branca',
      texto='Só o acetamiprido (IRAC 4A) nesta base; ' + SEM_ALTERNATIVA.lower() + '.'),
 dict(cultura='Mamão', alvo='pulgão', ref='MAMAO-IMP · Controle de pulgão e ácaro',
      texto='Sem registro nesta base; pulgão não coloniza o mamoeiro e inseticida não evita a mancha-anelar (Embrapa).'),
]

_POR_ID = {p['id']: p for p in PRODUTOS}

def por_id(i):
    return _POR_ID.get(i)

def por_nome(nome):
    """Ficha pelo nome usado na fazenda (plano, estoque, ordem ou recomendação)."""
    return next((p for p in PRODUTOS if nome in p['nomes_fazenda']), None)

def alternativas(p, uso):
    """Produtos com o mesmo cultura × alvo e NENHUM grupo em comum com p (rotação real). Cancelados e adjuvantes ficam fora."""
    g = set(p['grupos'])
    if not g:
        return []
    out = []
    for q in PRODUTOS:
        if q is p or q['situacao'] == 'Cancelado' or not q['grupos'] or g & set(q['grupos']):
            continue
        for u in q['usos']:
            if u['cultura'] == uso['cultura'] and u['chave'] == uso['chave']:
                out.append((q, u))
                break
    return out

def substitutos(p, uso):
    """Registro cancelado: produtos permitidos (não cancelados, com modo de ação) para o mesmo cultura × alvo, de qualquer grupo."""
    out = []
    for q in PRODUTOS:
        if q is p or q['situacao'] == 'Cancelado' or not q['grupos']:
            continue
        for u in q['usos']:
            if u['cultura'] == uso['cultura'] and u['chave'] == uso['chave']:
                out.append((q, u))
                break
    return out

# ======================= ligação com os dados abertos do AGROFIT (AG-07 sobre a base real, 02/10/2026) =======================
# A AG-07 lista os registros reais (dados_agrofit/site/agrofit_*.json). Esta base vira "Referência conferida em bula" dentro da ficha
# real e o elo "Na fazenda": cada ficha da fazenda é ligada a TODO registro com a MESMA combinação de ingredientes ativos.
# Nomes EXATOS do AGROFIT (agrofit_indice.json · ingredientes), na ordem da concentração em `concentracao`. A página casa pelo nome
# (sem acento e sem caixa), não pelo índice: uma nova geração dos arquivos pode renumerar os ingredientes.
# Lista vazia: sem registro ativo no arquivo (paraquate, proibido desde 22/09/2020) ou fora do arquivo (adjuvante organossiliconado).
AGROFIT_INGREDIENTES = {
    'glifosato-480': ['glifosato-sal de isopropilamina'], 'acido-24d-806': ['2,4-D-dimetilamina'], 'cletodim-240': ['cletodim'],
    'atrazina-500': ['Atrazina'], 'diquat-200': ['Dibrometo de diquate'], 'fungicida-a': ['Protioconazol', 'trifloxistrobina'],
    'fungicida-c': ['Azoxistrobina', 'ciproconazol'], 'fungicida-ts': ['fludioxonil', 'metalaxil-M'], 'tebuconazol-200-ec': ['tebuconazol'],
    'inseticida-b': ['acefato'], 'acetamiprido-200-sp': ['acetamiprido'], 'abamectina-18-ec': ['Abamectina'], 'acaricida-d': ['Espiromesifeno'],
    'oleo-mineral': ['óleo mineral'], 'adjuvante-espalhante': [], 'abamectina-500-fs': ['Abamectina'], 'mancozebe-750-wg': ['mancozebe'],
    'fluxapiroxade-piraclostrobina-sc': ['fluxapiroxade', 'piraclostrobina'], 'epoxiconazol-piraclostrobina-se': ['epoxiconazol', 'piraclostrobina'],
    'oxicloreto-cobre-840-wp': ['oxicloreto de cobre'], 'boscalida-500-wg': ['Boscalida'], 'azoxistrobina-250-sc': ['Azoxistrobina'],
    'enxofre-800-wg': ['enxofre'], 'tiametoxam-lambda-zc': ['tiametoxam', 'lambda-cialotrina'], 'etiprole-200-sc': ['Etiprole'],
    'clorantraniliprole-200-sc': ['clorantraniliprole'], 'tiametoxam-250-wg': ['tiametoxam'], 'espinetoram-250-wg': ['Espinetoram'],
    'lufenurom-50-ec': ['lufenurom'], 'emamectina-50-wg': ['Benzoato de Emamectina'], 'glufosinato-200-sl': ['Glufosinato - sal de amônio'],
    'saflufenacil-700-wg': ['saflufenacil'], 's-metolacloro-960-ec': ['S-metolacloro'], 'tembotriona-420-sc': ['Tembotriona'],
    'nicosulfurom-40-sc': ['nicossulfurom'], 'pasteuria-nishizawae-fs': ['Pasteuria nishizawae'], 'beauveria-bassiana-wp': ['Beauveria bassiana'],
    'piriproxifem-100-ec': ['piriproxifem'], 'ciantraniliprole-100-od': ['Ciantraniliprole'], 'fluazinam-500-sc': ['fluazinam'],
    'tiofanato-metilico-500-sc': ['tiofanato-metílico'], 'fenpiroximato-50-sc': ['fenpiroximato'], 'buprofezina-250-wp': ['buprofezina'],
    'paraquate-200-sl': [],
}
# Por que a ficha não tem registro no arquivo (texto da faixa quando o link antigo AG-07.dc.html#<id> não acha produto).
SEM_REGISTRO = {
    'adjuvante-espalhante': 'o arquivo de produtos formulados do AGROFIT não traz adjuvantes; confira o registro do adjuvante no MAPA.',
}
# Grupo de resistência (IRAC/FRAC/HRAC) por ingrediente, só os conferidos nesta base (GRUPOS). O AGROFIT NÃO publica esse grupo:
# a AG-07 mostra o código como "referência". Nome normalizado (sem acento, minúsculas); vale o nome exato ou o nome seguido de
# sal/éster/cepa (ex.: "glifosato-sal de potassio", "beauveria bassiana, cepa ant-03"); "2,4-db" NÃO casa com "2,4-d".
GRUPO_REF = [
    (['glifosato'], 'HRAC 9'), (['2,4-d'], 'HRAC 4'), (['cletodim'], 'HRAC 1'), (['atrazina'], 'HRAC 5'),
    (['diquate', 'dibrometo de diquate'], 'HRAC 22'), (['glufosinato'], 'HRAC 10'), (['saflufenacil'], 'HRAC 14'),
    (['s-metolacloro', 'metolacloro'], 'HRAC 15'), (['tembotriona'], 'HRAC 27'), (['nicossulfurom'], 'HRAC 2'),
    (['protioconazol', 'ciproconazol', 'tebuconazol', 'epoxiconazol'], 'FRAC 3'),
    (['trifloxistrobina', 'azoxistrobina', 'piraclostrobina'], 'FRAC 11'), (['fludioxonil'], 'FRAC 12'), (['metalaxil'], 'FRAC 4'),
    (['fluxapiroxade', 'boscalida'], 'FRAC 7'), (['mancozebe'], 'FRAC M3'), (['oxicloreto de cobre'], 'FRAC M1'), (['enxofre'], 'FRAC M2'),
    (['fluazinam'], 'FRAC 29'), (['tiofanato-metilico'], 'FRAC 1'),
    (['acefato'], 'IRAC 1B'), (['acetamiprido', 'tiametoxam'], 'IRAC 4A'), (['abamectina', 'benzoato de emamectina'], 'IRAC 6'),
    (['espiromesifeno'], 'IRAC 23'), (['lambda-cialotrina'], 'IRAC 3A'), (['etiprole'], 'IRAC 2B'),
    (['clorantraniliprole', 'ciantraniliprole'], 'IRAC 28'), (['espinetoram'], 'IRAC 5'), (['lufenurom'], 'IRAC 15'),
    (['piriproxifem'], 'IRAC 7C'), (['fenpiroximato'], 'IRAC 21A'), (['buprofezina'], 'IRAC 16'),
    (['beauveria bassiana'], 'IRAC UNF'), (['pasteuria nishizawae'], 'IRAC N-UNB'),
]
assert set(AGROFIT_INGREDIENTES) == set(_POR_ID), 'AGROFIT_INGREDIENTES precisa cobrir todas as fichas'
assert all(c in GRUPOS for _, c in GRUPO_REF)

def conc_num(p):
    """Concentração numérica da ficha, na ordem de AGROFIT_INGREDIENTES ('175 + 150 g/L' → [175, 150]); [] quando não é g/L ou g/kg."""
    m = re.match(r'\s*([\d.,]+(?:\s*\+\s*[\d.,]+)*)\s*g/(?:L|kg)\b', p['concentracao'])
    return [float(x.replace('.', '').replace(',', '.')) for x in re.split(r'\s*\+\s*', m.group(1))] if m else []

def confere_agrofit(indice):
    """Nomes de AGROFIT_INGREDIENTES ausentes do índice real (o build da AG-07 falha se houver)."""
    import unicodedata
    nz = lambda s: ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if not unicodedata.combining(c)).strip()
    tem = {nz(x[0]) for x in indice['ingredientes']}
    return [(k, n) for k, ns in AGROFIT_INGREDIENTES.items() for n in ns if nz(n) not in tem]

# ======================= grupo de resistência de TODOS os ingredientes químicos do arquivo (rotação da AG-07, 03/10/2026) =======================
# O AGROFIT só publica o grupo químico, e o rótulo varia dentro do mesmo modo de ação ('triazol', 'Triazolinthione' e 'imidazol' são
# todos FRAC 3; 'carboxamida', 'anilida', 'carboxanilida' e 'pirazol carboxamida' são FRAC 7; 'estrobilurina', 'oxazolidinadiona' e
# 'imidazolinona' (fenamidona) são FRAC 11) e mistura modos de ação ('imidazol' tem ciazofamida, FRAC 21; 'anilida' tem diflufenicam,
# HRAC 12; 'triazolona' tem tiencarbazona, HRAC 2; 'dicarboximida' tem captana/folpete, FRAC M4). Por isso a rotação compara o
# CÓDIGO de modo de ação por ingrediente, desta tabela (classificações públicas IRAC 11.x, FRAC Code List 2024/2025 e HRAC 2020+).
# Mesma regra de casamento de GRUPO_REF: nome normalizado exato ou seguido de sal/éster ('glifosato' casa 'glifosato-sal de potassio').
# Grupos "UN" (modo de ação desconhecido) NÃO entram: dois ingredientes UN não são do mesmo grupo. Biológicos, extratos, óleos,
# feromônios e reguladores ficam sem código (SEM_CODIGO_RESIST): a rotação usa o próprio ingrediente ou o grupo químico do AGROFIT.
GRUPO_RESIST_NOVOS = [
    # ---- FRAC (fungicidas e bactericidas) ----
    (['tiabendazol', 'carbendazim'], 'FRAC 1'), (['iprodiona', 'procimidona'], 'FRAC 2'),
    (['bromuconazol', 'difenoconazol', 'fluquinconazol', 'flutriafol', 'imibenconazol', 'ipconazol', 'mefentrifluconazol', 'metconazol',
      'miclobutanil', 'propiconazol', 'tetraconazol', 'triadimenol', 'triadimefom', 'triticonazol', 'hexaconazol', 'flusilazol',
      'fenbuconazol', 'procloraz', 'imazalil', 'triflumizol'], 'FRAC 3'),
    (['benalaxil'], 'FRAC 4'), (['fenpropimorfe', 'fenpropidina', 'espiroxamina'], 'FRAC 5'),
    (['bixafem', 'flutolanil', 'impirfluxam', 'pidiflumetofen', 'pidiflumetofem', 'carboxina', 'tifluzamida', 'benzovindiflupyr',
      'benzovindiflupir', 'fluindapyr', 'fluindapir', 'isopirazam', 'fluopyram', 'fluopiram', 'isofetamida', 'ciclobutrifluram',
      'sedaxano', 'pentiopirade'], 'FRAC 7'),
    (['ciprodinil', 'pirimetanil'], 'FRAC 9'),
    (['cresoxim-metilico', 'dimoxistrobin', 'fluoxastrobina', 'mandestrobina', 'metominostrobin', 'picoxistrobina', 'famoxadona',
      'fenamidona'], 'FRAC 11'),
    (['diclorana'], 'FRAC 14'), (['triciclazol'], 'FRAC 16.1'), (['pencicurom'], 'FRAC 20'),
    (['ciazofamida', 'florylpicoxamida', 'amissulbrom'], 'FRAC 21'), (['zoxamida'], 'FRAC 22'), (['casugamicina'], 'FRAC 24'),
    (['cimoxanil'], 'FRAC 27'), (['cloridrato de propamocarbe', 'propamocarbe'], 'FRAC 28'), (['hidroxido de fentina'], 'FRAC 30'),
    (['fosetil'], 'FRAC 33'), (['dimetomorfe', 'mandipropamid', 'bentiavalicarbe'], 'FRAC 40'), (['fluopicolide'], 'FRAC 43'),
    (['ametoctradina'], 'FRAC 45'), (['natamicina'], 'FRAC 48'), (['oxatiapiprolim', 'fluoxapiprolim'], 'FRAC 49'),
    (['piriofenone', 'metrafenona'], 'FRAC 50'), (['ipflufenoquina'], 'FRAC 52'),
    (['hidroxido de cobre', 'oxido cuproso', 'sulfato de cobre', 'carbonato de cobre'], 'FRAC M1'),
    (['metiram', 'propinebe', 'tiram'], 'FRAC M3'), (['captana', 'folpete'], 'FRAC M4'), (['clorotalonil'], 'FRAC M5'),
    (['dodina'], 'FRAC M7'), (['ditianona'], 'FRAC M9'),
    # ---- IRAC (inseticidas, acaricidas, nematicidas, fumigantes) ----
    (['benfuracarbe', 'carbossulfano', 'cloridrato de formetanato', 'carbaril', 'metomil', 'tiodicarbe', 'carbofurano'], 'IRAC 1A'),
    (['cadusafos', 'clorpirifos', 'dimetoato', 'fenitrotiona', 'fosmete', 'fostiazato', 'malationa', 'pirimifos-metilico', 'profenofos',
      'terbufos', 'metamidofos'], 'IRAC 1B'),
    (['fipronil'], 'IRAC 2B'),
    (['acrinatrina', 'alfa-cipermetrina', 'beta-ciflutrina', 'beta-cipermetrina', 'bifentrina', 'cipermetrina', 'deltametrina',
      'esfenvalerato', 'fenpropatrina', 'gama-cialotrina', 'permetrina', 'zeta-cipermetrina', 'etofenproxi'], 'IRAC 3A'),
    (['clotianidina', 'dinotefuram', 'imidacloprido', 'tiacloprido'], 'IRAC 4A'), (['sulfoxaflor'], 'IRAC 4C'),
    (['flupiradifurona'], 'IRAC 4D'), (['espinosade'], 'IRAC 5'), (['milbemectina'], 'IRAC 6'),
    (['brometo de metila'], 'IRAC 8A'), (['dazomete', 'metam-sodico'], 'IRAC 8F'), (['pimetrozina'], 'IRAC 9B'),
    (['afidopiropeno'], 'IRAC 9D'), (['hexitiazoxi', 'clofentezina'], 'IRAC 10A'), (['etoxazol'], 'IRAC 10B'),
    (['diafentiurom'], 'IRAC 12A'), (['oxido de fembutatina'], 'IRAC 12B'), (['propargito'], 'IRAC 12C'),
    (['clorfenapir', 'sulfluramida'], 'IRAC 13'), (['cloridrato de cartape', 'cartape'], 'IRAC 14'),
    (['bistriflurom', 'clorfluazurom', 'diflubenzurom', 'flufenoxurom', 'novalurom', 'teflubenzurom', 'triflumurom'], 'IRAC 15'),
    (['ciromazina'], 'IRAC 17'), (['cromafenozida', 'metoxifenozida', 'tebufenozida'], 'IRAC 18'), (['amitraz'], 'IRAC 19'),
    (['piridabem', 'tolfenpyrad', 'tebufempirade'], 'IRAC 21A'), (['indoxacarbe'], 'IRAC 22A'), (['metaflumizone'], 'IRAC 22B'),
    (['espirodiclofeno', 'espiropidion', 'espirotetramate'], 'IRAC 23'),
    (['fosfina', 'fosfeto de aluminio', 'fosfeto de magnesio'], 'IRAC 24A'), (['cyflumetofen'], 'IRAC 25A'),
    (['ciclaniliprole', 'flubendiamida', 'tetraniliprole'], 'IRAC 28'), (['flonicamida'], 'IRAC 29'),
    (['isocicloseram', 'broflanilida'], 'IRAC 30'), (['dimpropiridaz'], 'IRAC 36'),
    # ---- HRAC (herbicidas) ----
    (['profoxidim', 'cialofope-butilico', 'clodinafope-propargil', 'fenoxaprope-p-etilico', 'fluazifope-p-butilico',
      'haloxifope-p-metilico', 'propaquizafope', 'quizalofope-p-etilico', 'quizalofope-p-tefurilico', 'pinoxadem', 'metamifop',
      'setoxidim'], 'HRAC 1'),
    (['azimsulfurom', 'ciclossulfamurom', 'clorimurom-etilico', 'etoxissulfurom', 'flazasulfurom', 'foramsulfurom',
      'halossulfurom-metilico', 'iodossulfurom-metilico-sodico', 'metsulfurom-metilico', 'ortossulfamurom', 'pirazossulfurom-etilico',
      'sulfometurom-metilico', 'trifloxissulfurom-sodico', 'imazamoxi', 'imazapique', 'imazapir', 'imazaquim', 'imazetapir',
      'cloransulam-metilico', 'diclosulam', 'flumetsulam', 'penoxsulam', 'piroxsulam', 'bispiribaque-sodico', 'piritiobaque-sodico',
      'tiencarbazona metilica'], 'HRAC 2'),
    (['pendimetalina', 'trifluralina'], 'HRAC 3'),
    (['mcpa', 'dicamba', 'aminopiralide', 'fluroxipir-meptilico', 'triclopir-butotilico', 'aminociclopiraclor', 'halauxifen-metil',
      'picloram', 'florpirauxifen-benzil', 'quincloraque'], 'HRAC 4'),
    (['ametrina', 'prometrina', 'simazina', 'terbutilazina', 'hexazinona', 'metamitrona', 'metribuzim', 'amicarbazona', 'diurom',
      'linurom', 'tebutiurom', 'bromacila', 'propanil'], 'HRAC 5'),
    (['bentazona', 'octanoato de ioxinila'], 'HRAC 6'), (['diflufenicam'], 'HRAC 12'), (['clomazona', 'bixlozona'], 'HRAC 13'),
    (['flumicloraque-pentilico', 'flumioxazina', 'tiafenacil', 'carfentrazona-etilica', 'sulfentrazona', 'fomesafem', 'lactofem',
      'oxifluorfem', 'acifluorfem-sodico', 'oxadiazona', 'piraflufem'], 'HRAC 14'),
    (['acetocloro', 'alacloro', 'piroxassulfona'], 'HRAC 15'), (['asulam'], 'HRAC 18'), (['paraquate'], 'HRAC 22'),
    (['biciclopirona', 'mesotriona', 'isoxaflutol', 'tolpiralate', 'topramezona'], 'HRAC 27'), (['indaziflam'], 'HRAC 29'),
]
# Nome curto (rotação, lista) e completo (ficha) dos códigos novos; os da base conferida vêm de GRUPOS.
_GRUPOS_NOVOS = {
    'FRAC 2': ('dicarboximida', 'dicarboximida (transdução de sinal osmótico)'),
    'FRAC 5': ('amina (morfolina)', 'amina/morfolina (inibidor da biossíntese de esterol, classe II)'),
    'FRAC 9': ('anilinopirimidina', 'anilinopirimidina (síntese de metionina)'),
    'FRAC 14': ('hidrocarboneto aromático', 'hidrocarboneto aromático (peroxidação de lipídios)'),
    'FRAC 16.1': ('MBI-R', 'inibidor da síntese de melanina (redutase)'),
    'FRAC 20': ('fenilureia', 'fenilureia (divisão celular)'),
    'FRAC 21': ('QiI', 'inibidor do complexo III no sítio Qi (QiI)'),
    'FRAC 22': ('benzamida (tubulina)', 'benzamida/toluamida (montagem da tubulina)'),
    'FRAC 24': ('antibiótico hexopiranosil', 'antibiótico hexopiranosil (síntese de proteína)'),
    'FRAC 27': ('cianoacetamida-oxima', 'cianoacetamida-oxima (modo de ação incerto, grupo próprio)'),
    'FRAC 28': ('carbamato', 'carbamato (permeabilidade da membrana)'),
    'FRAC 30': ('organoestânico', 'organoestânico (ATP sintase)'),
    'FRAC 33': ('fosfonato', 'fosfonato (etil fosfonato)'),
    'FRAC 40': ('CAA', 'amida do ácido carboxílico (CAA · síntese de celulose)'),
    'FRAC 43': ('benzamida (espectrina)', 'benzamida (deslocalização de proteínas tipo espectrina)'),
    'FRAC 45': ('QoSI', 'inibidor do complexo III no sítio Qo, ligação estigmatelina (QoSI)'),
    'FRAC 48': ('polieno', 'polieno (ergosterol da membrana)'),
    'FRAC 49': ('OSBPI', 'inibidor da proteína de ligação a oxisterol (OSBPI)'),
    'FRAC 50': ('aril-fenil-cetona', 'aril-fenil-cetona (actina/miosina)'),
    'FRAC 52': ('DHODH', 'inibidor da di-hidro-orotato desidrogenase (DHODH)'),
    'FRAC M4': ('ftalimida', 'ftalimida (multissítio)'),
    'FRAC M5': ('cloronitrila', 'cloronitrila (multissítio)'),
    'FRAC M7': ('guanidina', 'guanidina (multissítio)'),
    'FRAC M9': ('quinona', 'quinona (multissítio)'),
    'IRAC 1A': ('carbamato', 'carbamato (inibidor da acetilcolinesterase)'),
    'IRAC 4C': ('sulfoximina', 'sulfoximina (agonista do receptor nicotínico)'),
    'IRAC 4D': ('butenolida', 'butenolida (agonista do receptor nicotínico)'),
    'IRAC 8A': ('haleto de alquila', 'haleto de alquila (fumigante, inibidor não específico)'),
    'IRAC 8F': ('gerador de isotiocianato', 'gerador de isotiocianato de metila (fumigante)'),
    'IRAC 9B': ('piridina azometina', 'piridina azometina (modulador de órgão cordotonal, TRPV)'),
    'IRAC 9D': ('pyropene', 'pyropene (modulador de órgão cordotonal, TRPV)'),
    'IRAC 10A': ('inibidor de crescimento de ácaros', 'inibidor de crescimento de ácaros (CHS1)'),
    'IRAC 10B': ('etoxazol', 'etoxazol (inibidor de crescimento de ácaros, CHS1)'),
    'IRAC 12A': ('diafentiurom', 'inibidor da ATP sintase mitocondrial (diafentiurom)'),
    'IRAC 12B': ('organoestânico', 'organoestânico acaricida (ATP sintase)'),
    'IRAC 12C': ('propargito', 'propargito (ATP sintase)'),
    'IRAC 13': ('desacoplador', 'desacoplador da fosforilação oxidativa (gradiente de prótons)'),
    'IRAC 14': ('nereistoxina', 'análogo da nereistoxina (bloqueador do receptor nicotínico)'),
    'IRAC 17': ('ciromazina', 'disruptor da muda de dípteros (ciromazina)'),
    'IRAC 18': ('diacilhidrazina', 'diacilhidrazina (agonista do receptor de ecdisona)'),
    'IRAC 19': ('amitraz', 'agonista do receptor de octopamina (amitraz)'),
    'IRAC 22A': ('oxadiazina', 'oxadiazina (bloqueador do canal de sódio dependente de voltagem)'),
    'IRAC 22B': ('semicarbazona', 'semicarbazona (bloqueador do canal de sódio dependente de voltagem)'),
    'IRAC 24A': ('fosfina', 'fosfina (inibidor do complexo IV mitocondrial)'),
    'IRAC 25A': ('beta-cetonitrila', 'beta-cetonitrila (inibidor do complexo II mitocondrial)'),
    'IRAC 29': ('flonicamida', 'modulador de órgão cordotonal, alvo indefinido (flonicamida)'),
    'IRAC 30': ('isoxazolina', 'isoxazolina/meta-diamida (modulador alostérico do canal de cloro mediado por GABA)'),
    'IRAC 36': ('piridazina pirazolcarboxamida', 'piridazina pirazolcarboxamida (modulador de órgão cordotonal)'),
    'HRAC 3': ('inibidor de microtúbulos', 'inibidor da montagem de microtúbulos'),
    'HRAC 6': ('inibidor do FSII (nitrila)', 'inibidor do fotossistema II (sítio His 215)'),
    'HRAC 12': ('inibidor da PDS', 'inibidor da fitoeno desaturase (PDS)'),
    'HRAC 13': ('inibidor da DXS', 'inibidor da DXS (síntese de carotenoides)'),
    'HRAC 18': ('inibidor da DHP', 'inibidor da di-hidropteroato sintase (DHP)'),
    'HRAC 29': ('inibidor de celulose', 'inibidor da síntese de celulose'),
}
GRUPOS_RESIST = dict(GRUPOS)
GRUPOS_RESIST.update(_GRUPOS_NOVOS)
GRUPOS_RESIST['FRAC 3'] = ('DMI', 'DMI · triazol, triazolintiona e imidazol (inibidor da desmetilação de esterol)')
assert not set(_GRUPOS_NOVOS) & set(GRUPOS), 'código novo repetido em GRUPOS'
# tabela completa = base conferida + novos (um ingrediente, um código; a página casa pelo nome normalizado)
GRUPO_RESIST = list(GRUPO_REF) + GRUPO_RESIST_NOVOS
assert all(c in GRUPOS_RESIST for _, c in GRUPO_RESIST)
_ns = [n for ns, _ in GRUPO_RESIST for n in ns]
assert len(_ns) == len(set(_ns)), 'ingrediente com dois códigos em GRUPO_RESIST'
# Na rotação (AG-07, agRotKeys/agMesmo): código UN (modo de ação desconhecido) não une produtos; multissítio (FRAC M) que o produto
# aberto já tem não conta como rotação, multissítio novo conta.
# Ingredientes químicos sem código de propósito (o build avisa se aparecer ingrediente químico novo fora das duas listas).
SEM_CODIGO_RESIST = {
    'oleo mineral', 'oleo vegetal', 'bicarbonato de potassio', 'terra diatomacea', 'silicato de aluminio anidro', 'acido nonanoico',
    'cloreto de benzalconio', 'azadiractina', 'azadiracti na a', 'azadiracti na b', 'oleo de neem', 'oxymatrine', 'fluensulfona',
    'fluazaindolizine', 'msma', 'lauril eter sulfato de sodio', 'acibenzolar-s-metilico', 'laminarina', 'cerevisane', 'geraniol',
    'cinamaldeido', 'acido tanico', 'fosfato ferrico', 'tidiazurom', 'paclobutrazol', 'extrato hidroalcoolico de azadirachta indica',
    'reynoutria sachalinensis, extrato de raiz e caule', 'sophora flavescens, extrato de sementes', 'tefrosia', 'tephrosia candida',
}
# Rótulos de grupo químico do AGROFIT que NÃO indicam modo de ação comum (organismos, extratos, inorgânicos diversos): sem código,
# cada ingrediente desses conta como grupo próprio na rotação (Bacillus A ≠ Trichoderma B; cobre e fosfina não são "o mesmo grupo").
GQ_GENERICOS = ['Biológico', 'Produto Microbiológico', 'Não se aplica', 'não pertinente', 'Ácaros Vivos', 'Nematóides entomopatogênicos',
                'extrato vegetal', 'Derivado vegetal', 'terpenos', 'Bioquímico', 'inorgânico', 'álcool alifático']
_QUIM = {'Fungicida', 'Inseticida', 'Acaricida', 'Herbicida', 'Nematicida', 'Bactericida', 'Cupinicida', 'Formicida'}

def _nz(s):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if not unicodedata.combining(c)).strip()

def _casa(n, pt):
    return n == pt or (n.startswith(pt) and not n[len(pt):len(pt) + 1].isalnum())

def codigos_resist(nome):
    """Códigos IRAC/FRAC/HRAC de referência do ingrediente (nome do AGROFIT), pela regra de casamento da página."""
    n = _nz(nome)
    return [c for ns, c in GRUPO_RESIST if any(_casa(n, pt) for pt in ns)]

def lacunas_resist(indice):
    """Ingredientes de produto químico (classe não biológica) sem código, fora de SEM_CODIGO_RESIST e de rótulo não genérico.
    Arquivo novo do AGROFIT com ingrediente novo → aparece aqui (o build avisa; a rotação cai no grupo químico até a tabela crescer)."""
    F = {c: i for i, c in enumerate(indice['campos'])}
    IG, CL, GQ = indice['ingredientes'], indice['classes'], indice['gruposQuimicos']
    gen = {_nz(g) for g in GQ_GENERICOS}; sem = {_nz(n) for n in SEM_CODIGO_RESIST}; quim = set()
    for r in indice['produtos']:
        if any(CL[c][1] in _QUIM and CL[c][2] == 0 for c in r[F['classes']]):
            quim.update(x[0] for x in r[F['ingredientes']])
    return sorted(IG[i][0] for i in quim if not codigos_resist(IG[i][0]) and _nz(IG[i][0]) not in sem
                  and (IG[i][1] is None or _nz(GQ[IG[i][1]]) not in gen))
