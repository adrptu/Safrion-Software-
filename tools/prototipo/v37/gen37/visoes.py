# -*- coding: utf-8 -*-
"""Visões das listagens (VISOES-1, pedido do proprietário de 10/10/2026: "a visão nasce do atributo dominante").
Fonte única do que cada entidade pode mostrar: uma visão só entra se o dado a sustenta (atributo com fonte no código).
O build (engine.visoes) e os testes leem daqui; o JS não recalcula, recebe a lista pronta (data-visoes e a grade).
Desenho: DESENHO.md §1 e §2.1 (tabela entidade × visões; o que fica de fora tem motivo)."""

# ordem fixa no seletor (a Lista é sempre a primeira); no celular aparecem as 3 primeiras válidas e "mais"
ORDEM = ['lista', 'agrupada', 'kanban', 'calendario', 'timeline', 'mapa', 'carga', 'matriz', 'arvore', 'galeria']
# nome curto (minúsculo: entra no "Ver em <nome>") e nome de menu (texto do item no "mais", celular)
NOME = {'lista': 'lista', 'agrupada': 'tabela agrupada', 'kanban': 'kanban', 'calendario': 'calendário', 'timeline': 'linha do tempo',
        'mapa': 'mapa', 'carga': 'carga por recurso', 'matriz': 'matriz', 'arvore': 'árvore', 'galeria': 'galeria'}
# ícones Lucide 1.45.0 (ISC; LICENSES/lucide-ISC.txt) convertidos para o icon() do engine; só entram os que alguma tela usa
ICONE = {'lista': 'v_lista', 'agrupada': 'v_agrupada', 'kanban': 'v_kanban', 'carga': 'v_carga'}
# o atributo dominante que cada visão exige (regra do pedido: sem o dado, sem a visão)
EXIGE = {
    'lista': [],
    'agrupada': ['categoria', 'somavel'],      # chave de grupo + valor somável na mesma unidade (subtotal por grupo)
    'kanban': ['fluxo'],                        # estados com fluxo fixo (colunas que não mudam)
    'calendario': ['data'],                     # data relevante para a decisão
    'timeline': ['inicio', 'fim'],              # início E fim
    'mapa': ['geometria'],                      # geometria ou coordenada própria (nunca inventada)
    'carga': ['recurso', 'tempo'],              # recurso × dia/hora
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
    'os': {
        'ativas': {
            'lista': {},
            'agrupada': {'categoria': 'Talhão multivalorado (areas/processo_os.py, coluna tal multi=True; agrupamento TF06 em PREVALS)',
                         'somavel': 'Área em ha somada como ha-operação; o grupo conta O.S. distintas (PRD 297 e 7292)'},
            'kanban': {'fluxo': 'FASES com 5 etapas fixas (areas/processo_os.py FASES; _kanban; PRD 2972-2988)'},
            'carga': {'recurso': 'alocacao.py RECURSOS (máquina, implemento, pessoa)',
                      'tempo': 'alocacao.py DIAS e ALOC (dia e hora; DEC-2609-09)'},
        },
        'cortes': {
            'timeline': 'Repete o Calendário e a Carga (uma solução por problema, AGENTS §3.4; DESENHO 1.4).',
            'mapa': 'DEC-2609-09 mantida: o mapa das ordens fica no IN-04; reabrir só por pedido do proprietário (DESENHO 1.4).',
            'calendario': 'Fatia 2 (VISOES-2): o dado sustenta (início e fim ISO), mas não entra na F1.',
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
# location.replace/assign e location.href= cujo argumento usa location.pathname sem location.search (g2visaoUrl recebe os dois e passa)
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
        if 'location.pathname' in arg and 'location.search' not in arg: ruins.append((m.group(0) + arg)[:160])
    return ruins
