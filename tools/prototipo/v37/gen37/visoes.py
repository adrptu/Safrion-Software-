# -*- coding: utf-8 -*-
"""Visões das listagens (VISOES-1, pedido do proprietário de 10/10/2026: "a visão nasce do atributo dominante").
Fonte única do que cada entidade pode mostrar: uma visão só entra se o dado a sustenta (atributo com fonte no código).
O build (engine.visoes) e os testes leem daqui; o JS não recalcula, recebe a lista pronta (data-visoes e a grade).
Desenho: DESENHO.md §1 e §2.1 (tabela entidade × visões; o que fica de fora tem motivo)."""

# ordem fixa no seletor (a Lista é sempre a primeira); no celular aparecem as 3 primeiras válidas e "mais"
ORDEM = ['lista', 'cartoes', 'agrupada', 'kanban', 'calendario', 'timeline', 'mapa', 'carga', 'frentes', 'matriz', 'arvore', 'galeria']
# nome curto (minúsculo: entra no "Ver em <nome>") e nome de menu (texto do item no "mais", celular)
NOME = {'lista': 'tabela',   # VISOES-2 §2: Lista e Tabela agrupada são uma visão só, a Tabela (a chave e o ?view=lista ficam)
        'cartoes': 'cartões',   # DS VIS-05 (15/10/2026): toda lista tem Tabela e Cartões
         'agrupada': 'tabela agrupada', 'kanban': 'kanban', 'calendario': 'calendário', 'timeline': 'linha do tempo',
        'mapa': 'mapa', 'carga': 'carga por recurso', 'frentes': 'frentes de trabalho', 'matriz': 'matriz', 'arvore': 'árvore', 'galeria': 'galeria'}
# ícones Lucide 1.45.0 (ISC; LICENSES/lucide-ISC.txt) convertidos para o icon() do engine; só entram os que alguma tela usa
ICONE = {'lista': 'v_agrupada', 'cartoes': 'v_cartoes', 'agrupada': 'v_agrupada', 'kanban': 'v_kanban', 'calendario': 'v_calendario', 'carga': 'v_carga', 'frentes': 'v_frentes', 'mapa': 'map'}
# Modo de ver a listagem (proprietário, 15/10/2026: "Coloque modos de visão em todas telas... tem que ter opção tabela e 'Cartões'"):
# Tabela | Cartões no fim da barra de toda grade de listagem do menu (engine.grid, com colunas essenciais ou "Agrupar por") e nas Atividades
# do plano (PA). Os cartões leem as mesmas linhas da Tabela (busca, filtro rápido, filtros, Agrupar por com descer e trilha, Colunas).
# Onde a listagem já tem seletor de visões (VISOES-1: O.S.) ou o Kanban da própria tela (BEN, MA › Ordens), o modo não entra (o Kanban
# já cumpre o papel dos cartões). Preferência por perfil × tela × listagem (safrion.pref.modo:*) e ?view=cartoes na listagem principal.
MODOS = ['tabela', 'cartoes']
MODO_NOME = {'tabela': 'Tabela', 'cartoes': 'Cartões'}          # aria-label e dica do botão (só ícone)
MODO_ICONE = {'tabela': 'v_agrupada', 'cartoes': 'v_cartoes'}  # o mesmo ícone da Tabela no seletor da VISOES-1 (ICONE['lista'])
# DS VIS-05 (padroes-1510: "toda lista tem Tabela e Cartões"): listagens do menu sem colunas essenciais nem Agrupar por que também ganham o
# seletor (engine.grid). Fora, com o motivo: grade que a tela não desenha (só dados e formulário: CD-01 Fazendas, CD-02 Culturas, CD-04
# Equipes, CD-06 Grupos e CD-08 Operações, que são cartões ou listas mestras próprias); tabela do detalhe de um registro (CA-01det, IR-03det,
# os painéis da MA, AG-02 › atributos do laudo); matriz e comparação com forma própria (SAF › Capacidade recurso × mês, GE-02 › caixa V1 × V2,
# a conta do percentímetro na CD-03 e IR-01); roteiro guiado que não é lista de registros (ON-01 › passos e recursos do trial).
MODO_LISTAS = {('AG-02.dc.html', 'g_uso'), ('CD-01.dc.html', 'g_amb'), ('CD-06.dc.html', 'g_loc'), ('CF-01.dc.html', 'g_pes'), ('CF-01.dc.html', 'g_alc'),
               ('CF-05.dc.html', 'g_uso'), ('CMP.dc.html', 'g_saf'), ('COLH.dc.html', 'g_sem'), ('IC.dc.html', 'g_icf'), ('IC.dc.html', 'g_ich'),
               ('IV.dc.html', 'g_ivp'), ('PAGR.dc.html', 'g_pna'), ('GE-08.dc.html', 'g_cre'), ('GE-08.dc.html', 'g_dos'),
               ('PT-01.dc.html', 'g_op'), ('PT-01.dc.html', 'g_av')}
# o atributo dominante que cada visão exige (regra do pedido: sem o dado, sem a visão)
EXIGE = {
    'lista': [],
    'cartoes': [],                              # DS VIS-05: toda lista tem Tabela e Cartões (as mesmas linhas, g2lib.g2cdVals)
    'agrupada': ['categoria', 'somavel'],      # chave de grupo + valor somável na mesma unidade (subtotal por grupo)
    'kanban': ['fluxo'],                        # estados com fluxo fixo (colunas que não mudam)
    'calendario': ['data'],                     # data relevante para a decisão
    'timeline': ['inicio', 'fim'],              # início E fim
    'mapa': ['geometria'],                      # geometria ou coordenada própria (nunca inventada)
    'carga': ['recurso', 'tempo'],              # recurso × dia/hora
    'frentes': ['familia', 'rota'],             # EX-54: família de implemento + geometria para a sequência de talhões
    'matriz': ['linha', 'coluna', 'valor'],     # duas dimensões e um valor que se soma
    'arvore': ['pai_filho'],                    # hierarquia que a Lista ainda não mostra
    'galeria': ['foto_principal'],              # imagem real como informação principal
}

def rotulo(k):
    """Nome acessível do botão (aria-label) e texto da dica: "Ver em <nome>"."""
    return 'Ver em ' + NOME[k]

def menu_nome(k):
    """Texto do item no menu "mais" (celular): o nome com a inicial maiúscula."""
    n = NOME[k]; return n[:1].upper() + n[1:]

# ---- registro por entidade: visão ativa → {atributo: fonte}; corte → motivo ----
REGISTRO = {
    # EX-55 F1 (proprietário, 18/10/2026: mapa dentro das telas): Pragas e doenças (AG-01) com Tabela, Cartões e Mapa
    'mip': {
        'ativas': {
            'lista': {},
            'cartoes': {},   # DS VIS-05: as linhas da Tabela em cartões
            'mapa': {'geometria': 'contornos dos talhões do Mapa (geo_talhoes.mapa(), a mesma fonte do IN-04); classe de mapa_camadas.js mcMIP e vistorias de mip.js mipDoTal'},
        },
        'cortes': {
            'kanban': 'As etapas da vistoria já são a coluna Situação e os chips de situação (uma solução por problema, AGENTS §3.4).',
            'calendario': 'A data da vistoria é um dia só; a próxima vistoria do talhão sai do "Programar vistoria" (DESENHO 1.4).',
        },
    },
    # EX-55 F1: Irrigação (IR-01, setores) com Tabela, Cartões e Mapa
    'irr': {
        'ativas': {
            'lista': {},
            'cartoes': {},   # DS VIS-05: as linhas da Tabela em cartões
            'mapa': {'geometria': 'contornos dos talhões do Mapa (geo_talhoes.mapa(), a mesma fonte do IN-04); classe de mapa_camadas.js mcIrr e entrada de irrigacao_estado.js irrMapaEntrada'},
        },
        'cortes': {
            'carga': 'A agenda dos pivôs e do gotejo é a Programação (IR-02), que já mostra setor × dia (uma solução por problema, AGENTS §3.4).',
            'kanban': 'A situação do setor já é a coluna Situação e o filtro rápido (DESENHO 1.4).',
        },
    },
    # VIS-08 (proprietário, 18/10/2026: "O modo de visão em mapa em planejar safra tem que ser pelo ícone igual os demais"):
    # Cadastros › Fazendas e talhões (CD-01, árvore fazenda › talhão) com Tabela, Cartões e Mapa no seletor da VISOES-1
    'tal': {
        'ativas': {
            'lista': {},
            'cartoes': {},   # DS VIS-05: as linhas da Tabela em cartões
            'mapa': {'geometria': 'polígonos do cadastro (areas/cad_fazendas.py GEO_MAPA, Santa Rita) e pivôs do KML (dados_lagoa_fonte LG_PIVOS, Lagoa Grande)'},
        },
        'cortes': {
            'kanban': 'O talhão não tem fluxo de etapas; a situação é a coluna Situação e o filtro rápido (DESENHO 1.4).',
            'calendario': 'Cadastro sem data que decida algo na lista (DESENHO 1.4).',
        },
    },
    # VIS-08: Agrícola › Beneficiamento (BEN): Lista | Cartões | Kanban pelo ícone (engine.visoes_locais; o estado segue o bn_vis da tela)
    'ben': {
        'ativas': {
            'lista': {},
            'cartoes': {},   # DS VIS-05: as linhas da Tabela em cartões (g2modoExterno da tela)
            'kanban': {'fluxo': 'fases da ordem de beneficiamento no Kanban da O.S. (areas/processo_os.py _kanban; FASES com 5 etapas)'},
        },
        'cortes': {
            'mapa': 'A ordem de beneficiamento é da unidade de beneficiamento, sem talhão próprio no desenho (DESENHO 1.4).',
        },
    },
    # VIS-08: Manutenção › Ordens (MA): Lista | Cartões | Kanban pelo ícone (engine.visoes_locais; antes, uma cópia da barra com outro ícone de Tabela)
    'ma_om': {
        'ativas': {
            'lista': {},
            'cartoes': {},   # DS VIS-05: as linhas da Tabela em cartões (g2modoExterno da tela)
            'kanban': {'fluxo': 'fases da ordem no Kanban da O.S. (areas/processo_os.py _kanban, usado pela Manutenção em areas/maquinas.py)'},
        },
        'cortes': {
            'mapa': 'A ordem de manutenção é do ativo (oficina ou campo), sem contorno de talhão (DESENHO 1.4).',
        },
    },
    # VIS-08: Planejar safra › "Editar talhões…" (painel de edição em lote; engine.visoes_locais, a visão é do painel aberto)
    'saf_tal': {
        'ativas': {
            'lista': {},
            'mapa': {'geometria': 'contornos dos talhões do Mapa (geo_talhoes.mapa(), a mesma fonte do IN-04); seleção e rótulo de safra_mapa.js'},
        },
        'cortes': {
            'cartoes': 'Painel de edição em lote célula a célula (Tab entre colunas, colar do Excel); cartão não edita em lote. A listagem da etapa tem Tabela e Cartões.',
        },
    },
    'os': {
        'ativas': {
            'lista': {},
            'cartoes': {},   # DS VIS-05 (padroes-1510, 15/10/2026): as linhas da Tabela em cartões, mesmo painel e mesmo Agrupar por
            'kanban': {'fluxo': 'FASES com 5 etapas fixas (areas/processo_os.py FASES; _kanban; PRD 2972-2988)'},
            # VISOES-2 (F2a): a janela da ordem (início e fim ISO) decide quando ela acontece; só leitura, programar continua no detalhe
            'calendario': {'data': 'Janela da O.S.: início e fim ISO (o.ini e o.fim, colunas Início e Fim da grade g_os em areas/processo_os.py)'},
            'carga': {'recurso': 'alocacao.py RECURSOS (máquina, implemento, pessoa)',
                      'tempo': 'alocacao.py DIAS e ALOC (dia e hora; DEC-2609-09)'},
            # EX-54 (proprietário, 18/10/2026): frentes de trabalho, a visão ao lado da Carga por recurso (prompt-safrion-frentes-trabalho.md)
            'frentes': {'familia': 'implemento da alocação ou da ficha técnica, senão a operação (os_frentes.js frFamilia)',
                        'rota': 'contornos dos talhões do Mapa (geo_talhoes.mapa(), a mesma fonte do IN-04)'},
            # EX-55 F1 (proprietário, 18/10/2026: "visão mapa dentro do próprio submenu/tela… ordem de serviço"): reabre a DEC-2609-09, que
            # mantinha o mapa das ordens só no IN-04 "até pedido do proprietário". É a camada O.S. do Mapa da fazenda sobre as linhas visíveis da lista
            'mapa': {'geometria': 'contornos dos talhões do Mapa (geo_talhoes.mapa(), a mesma fonte do IN-04); classes de mapa_camadas.js mcOS e ordens de os_mapa.js'},
        },
        'cortes': {
            'agrupada': 'Fundida na Tabela (VISOES-2 §2, pedido do proprietário de 14/10): agrupar é o "Agrupar por" da Tabela, com descer e trilha; ?view=agrupada abre a Tabela agrupada por Onde.',
            'timeline': 'Repete o Calendário e a Carga (uma solução por problema, AGENTS §3.4; DESENHO 1.4).',
            'matriz': 'Nenhuma matriz decide algo na O.S. (DESENHO 1.1).',
            'arvore': 'A Lista já é a forma da O.S.; o talhão é vínculo multivalorado, não pai (DESENHO 1.1).',
            'galeria': 'Sem imagem como informação principal (DESENHO 1.4).',
        },
    },
}

def sustenta(k, atributos):
    """A visão k é sustentada pelos atributos dados ({atributo: fonte})? Cada atributo exigido tem de existir com fonte não vazia."""
    if k not in EXIGE: return False
    return all(str((atributos or {}).get(a) or '').strip() for a in EXIGE[k])

def checar(ent):
    """Falha (ValueError) se alguma visão ativa da entidade não tem o atributo exigido com fonte, ou se um corte não tem motivo."""
    r = REGISTRO.get(ent)
    if r is None: raise ValueError(f'visoes: entidade sem registro: {ent}')
    for k, at in r['ativas'].items():
        if k not in ORDEM: raise ValueError(f'visoes: visão desconhecida em {ent}: {k}')
        if not sustenta(k, at):
            falta = [a for a in EXIGE[k] if not str((at or {}).get(a) or '').strip()]
            raise ValueError(f'visoes: {ent}·{k} sem atributo com fonte: {falta}')
    for k, motivo in r.get('cortes', {}).items():
        if not str(motivo or '').strip(): raise ValueError(f'visoes: corte sem motivo em {ent}: {k}')
        if k in r['ativas']: raise ValueError(f'visoes: {ent}·{k} ativa e cortada ao mesmo tempo')
    return True

def validas(ent):
    """Visões válidas da entidade, na ORDEM fixa (fonte única para o build e os testes)."""
    checar(ent)
    at = REGISTRO[ent]['ativas']
    return [k for k in ORDEM if k in at]

# ---- §2.4 (estática): nas telas com seletor, toda escrita de URL preserva location.search (o ?view) ----
# revisão VISOES-1, achado A9: a checagem antiga só pegava "replaceState(…location.pathname)" exato; esta acusa replaceState, pushState,
# location.replace/assign e location.href= cujo argumento usa location.pathname sem location.search, salvo quando passa por g2visaoUrl (que troca
# só o view= e mantém o resto da query)
import re as _re
_ESCRITA = _re.compile(r'(?:history\.(?:replaceState|pushState)|location\.(?:replace|assign))\s*\(|location\.href\s*=(?!=)')

def _argumento(src, i):
    """Texto do argumento a partir de src[i]: até o ")" que fecha a chamada, ou até ";", "}" ou fim de linha na atribuição."""
    if src[i - 1] == '(':
        n, j = 1, i
        while j < len(src) and n:
            n += {'(': 1, ')': -1}.get(src[j], 0); j += 1
        return src[i:j - 1]
    m = _re.match(r'[^;}\n]*', src[i:]); return m.group(0)

def escritas_sem_query(src):
    """Trechos de escrita de URL que apagariam a query (usam location.pathname sem location.search)."""
    ruins = []
    for m in _ESCRITA.finditer(src):
        arg = _argumento(src, m.end())
        if 'location.pathname' in arg and 'location.search' not in arg and 'g2visaoUrl(' not in arg: ruins.append((m.group(0) + arg)[:160])
    return ruins
