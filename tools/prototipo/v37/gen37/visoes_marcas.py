# -*- coding: utf-8 -*-
"""VISOES-2 V2-3 · marcas das listagens do menu, num quadro só (ESPEC §3.1, §3.6 e §5; fonte das colunas: docs/integracao/VISOES-2/
pedido-1410.md, "Colunas: só o essencial", aprovada pelo proprietário em 14/10/2026).

O motor (engine.grid) chama marcar() em cada grade. Para as grades deste quadro:
- ess: posição de cada coluna de "Abre com" (a 1ª é a identidade, travada); as outras ficam em "Colunas +N" (g2lib.g2colsVis);
- pq: a pergunta de cada coluna (oque, quem, quando, onde, medida, situacao), que agrupa o painel de colunas e o "Agrupar por";
- sico: as colunas de situação (Situação, Estado, Condição; Pendência, Qualidade, Avisos, Resultado, Sinal do app) que saem do padrão viram
  ícone antes da identidade, só quando pedem atenção;
- ag: "Agrupar por" com um nível por dimensão (O quê, Quem, Quando, Onde), lido da própria coluna (g2lib.g2agVals_, D.ck); data agrupa
  por mês. Grade em árvore não ganha: a árvore já agrupa.
Grade que já traz as próprias marcas (O.S., Planejar safra › talhões) fica como está. Rótulo do quadro que não casar com nenhuma coluna
para o build (erro), para o quadro nunca ficar desatualizado em silêncio."""
import re

# Ondas (14/10): 1 · Cadastros e Agrícola; 2 · Manutenção, Suprimentos, Comercial, Configurações e Backoffice. Cada onda com a bateria
# dos módulos antes de publicar. A AG-07 fica de fora até migrar o modo próprio (por produto × por uso,
# com 6 e 8 colunas): a pedido-1410 manda tirar essas opções (ESPEC §5, V2-3). Desde 15/10/2026 a AG-07 traz as
# próprias marcas (ess e pq em areas/agronomia.py, AGF_COLS_P e AGF_COLS_U: Tox · amb fica no painel "Colunas").
ABRE = """
CD-01 g_tal ; Fazenda › talhão ; Área total ; Área cultivável ; Talhões ; Diferença ; Parcelas na safra 2026/27
CD-01 g_agua ; Ponto de água ; Vencimento ; Vazão ; Uso
CD-01det g_parc ; Safra › parcela ; Cultura ; Área ; Plantio
CD-02 g_cv ; Cultura › cultivar ; Ciclo ; Cultivos
CD-03 g_atv ; Máquina ou instalação ; Custo R$/h ; Próxima calibração
CD-03 g_cj ; Conjunto ; Operações ; Rendimento
CD-04 g_pes ; Pessoa ; Equipe ; Validade da habilitação ; Habilidades
CD-05 g_forn ; Parceiro ; Papéis ; Contato
CD-06 g_itm ; Grupo › item ; Unidade ; Preço de referência
CD-07 g_dim ; Dimensão › código ; Nome ; Conta no ERP (Sankhya)
CD-08 g_rend ; Operação › conjunto ; Cultura ; Rendimento ; Custo R$/ha
AG-02 g_lau ; Laudo ; Fazenda · talhão ; V % ; pH ; P ; K ; MO ; Coleta
AG-02 g_agua ; Medição ; Talhão · zona ; Data ; CAD
AG-01 g_vis ; Vistoria ; Alvo ; Contagem × NC ; Talhão · cultura ; Próximo passo
AG-01det g_pts ; Ponto ; Contagem ; × NC ; Fotos
SAF g_saf ; Safra ; Fazenda ; Próximo passo ; Área
SAF g_op ; Operação › atividade › talhão ; Data ; Conjunto ; Horas-conjunto ; Custo total
SAF g_rend_* ; Operação ; Conjunto ; Rendimento ; Custo R$/ha ; Janela por talhão
SAF g_recp_maq ; Recurso ; Unidades ; Necessárias no pico ; Mês do pico
SAF g_recp_pes ; Recurso ; Pessoas ; Necessárias no pico ; Mês do pico
SAF g_dem ; Grupo ; Insumo ; Falta em ; Necessidade líquida ; Valor
SAF g_sug ; Talhão ; Atividade · produto ; Padrão ; Sugestão
GE-02 g_ver ; Versão ; Custo total ; Pico de caixa ; Estado · aprovação
GE-03 g_lan ; Origem (documento) ; Componente ; Dimensões ; Valor
IR-01 g_set ; Setor ; Déficit hoje ; Próximo passo ; Próxima passada
IR-02 g_ag ; Captação › ordem ; Início ; Lâmina ; Setor ; Fim ; Próximo passo
IR-03 g_os ; Ordem ; Setor ; Próximo passo ; Início ; Lâmina ; Etapa
IR-04 g_src ; Fonte ; Grandeza ; Atualização ; Efeito no balanço
IR-04 g_cap ; Captação ; Vazão outorgada ; Uso do dia ; Vencimento
IR-04 g_des ; Setor ; Lâmina aplicada ; Eficiência ; Variação da eficiência
COLH g_tal ; Talhão · variedade ; Situação · próximo passo ; Previsão ; Colhido ; Referência · desvio
CARGA g_cg ; Carga · ticket ; Situação · próximo passo ; Líquido ; Origem
BEN g_ob ; Ordem ; Produto ; Próximo passo ; Fase ; Em processo
PROD g_lot ; Lote · produto ; Disponível ; Qualidade · próximo passo ; Físico ; Local · validade
MA g_so ; Item ; Ativo · leitura ; O que ; Prazo ; Próximo passo
MA g_om ; Ordem · ativo ; Serviço · tipo ; Janela ; Executante ; Fase
MA g_at ; Ativo · local ; Plano ; Em aberto ; Próxima manutenção ; Leitura
MA g_ab ; Lançamento · operador ; Ativo ; Data · leitura ; Volume ; Consumo
MA g_pl ; Plano ; Aplica-se a ; Serviços ; Ativos
CMP g_dem ; Grupo · insumo ; Falta a partir de ; Necessidade ; Un. ; Valor ; Na compra
CMP g_conv ; Grupo · fornecedor ; Convite ; Responder até ; Resposta
CMP g_cmp ; Grupo · insumo · proposta ; Custo ; Escolha ; Preço ; A pedir ; Entrega
CMP g_apr ; Pedido · fornecedor · insumo ; Quantidade ; Preço ; Entrega ; Valor
CMP g_ent ; Pedido · fornecedor · insumo ; A entregar ; Previsão ; Ação
CMP g_mat ; Requisição ; Situação · próximo passo ; Urgência ; Origem · destino ; Valor
EST g_rec ; Nota fiscal ; Item ; Divergência ; Fornecedor ; Na nota ; Conferida
EST g_ent ; Requisição ; Item ; A entregar em embalagens ; O.S. ; Lote ; A entregar
EST g_dev ; Requisição ; O.S. ; Item ; Em custódia ; Com quem
EST g_lot ; Item › lote ; Local ; Físico ; Disponível ; Validade
EST g_cnt ; Contagem ; Item ; Local ; Diferença ; Ação
EST g_mov ; Hora ; Movimento ; Item ; Quantidade ; Quem
IC g_icm ; Insumo ; O que fazer ; Economia estimada ; Preço agora ; Mês mais barato
IC g_ici ; Insumo ; Último pago ; Melhor cotação ; vs último ; Sinal
PCOM g_of ; Produto › período ; Oferta ; Compromissos ; Livre para vender
PCOM g_pr ; Produto ; Preço médio realizado ; A receber ; Preço médio contratado ; Referência de mercado ; Vencido
VEN g_ven ; Venda · cliente ; Situação · próximo passo ; Falta ; Produto ; Quantidade ; Preço
EXPED g_rm ; Carga · romaneio ; Data ; Situação · próximo passo ; Venda · cliente ; Previsto
IV g_ivm ; Produto ; O que fazer ; Preço agora ; Agora vs normal do mês ; Melhor mês para vender
IV g_ivs ; Produto ; Oferta da safra ; Comercializado ; Livre para vender
IV g_ivc ; Venda ; Cliente ; Preço ; Líquido
CF-04 g_tr ; Quando ; Quem ; O quê ; Objeto ; Antes → depois / efeito
CF-03 g_con ; Conexão ; Última sincronização ; Pendências
CF-05 g_fat ; Competência ; Área cobrada ; Valor ; Vencimento
CF-05 g_pl ; Plano ; Módulos ; Preço R$/ha·mês ; Valor para a sua área
BO-02 g_org ; Organização ; Plano ; Mensalidade ; Fatura aberta ; Próximo evento
BO-02 g_fila ; Evento ; Organização ; Valor ; Resultado
"""

def _quadro():
    q = {}
    for ln in ABRE.strip().splitlines():
        cab, *cols = [x.strip() for x in ln.split(';')]
        pg, gid = cab.split()
        q[(pg + '.dc.html', gid)] = cols
    return q
QUADRO = _quadro()

def _acha(pagina, gid):
    if not gid: return None
    if (pagina, gid) in QUADRO: return QUADRO[(pagina, gid)]
    for (pg, g), cols in QUADRO.items():
        if pg == pagina and g.endswith('*') and gid.startswith(g[:-1]): return cols
    return None

_SIT = re.compile(r'^(situação|estado|fase|condição|etapa|próximo passo|próxima ação|ação|pendência|resultado|sinal|decisão|escolha|avisos|conferência|qualidade)', re.I)
_QUANDO = re.compile(r'(^data|^prazo|vencimento|^início|^fim\b|janela|^mês|semana|^hora|^quando|plantio|coleta|validade|atualização|chegada|competência|responder até|^próxim[ao] (manutenção|calibração|passada|evento)|1º uso|falta (em|a partir)|ocupa até|livre a partir|disponível até)', re.I)
_QUEM = re.compile(r'(responsável|^quem|executante|equipe|operador|fornecedor|cliente|parceiro|^pessoa|credor|dono|com quem|líder|transportador|prestador|contraparte|papéis|usuário|organização)', re.I)
_ONDE = re.compile(r'(talhão|fazenda|^local|setor|depósito|captação|ponto de água|zona|destino|praça|região|doca|rota)', re.I)
SICO_ROT = re.compile(r'^(situação|estado|condição)( do (lote|papel))?$', re.I)
# outras colunas de situação que levam selo de atenção (Pendência "Conflito", Qualidade, Avisos, Resultado, Sinal do app): ocultas, também viram
# ícone; o normal continua sem ícone (Codex/bateria V2-3: o "Conflito" vermelho da IR-03 sumia do padrão)
SICO_MAIS = re.compile(r'^(pendência|qualidade|avisos|resultado|sinal do app)$', re.I)

def pergunta(c, i):
    """Pergunta da coluna (ESPEC §3.1): a identidade é O quê; número é medida; data é Quando; o resto pelo rótulo."""
    l = c.get('l') or ''
    if i == 0: return 'oque'
    if c.get('t') == 'num' and not _QUANDO.search(l): return 'medida'
    if c.get('t') == 'date': return 'quando'
    if _SIT.search(l): return 'situacao'
    if _QUANDO.search(l): return 'quando'
    if _QUEM.search(l): return 'quem'
    if _ONDE.search(l): return 'onde'
    return 'oque'

def marcar(pagina, gid, cols, ag=None, tree=False, sico=None):
    """Aplica o quadro à grade (pagina, gid). Devolve (cols, ag, sico) — sem mudança fora do quadro ou em grade já marcada."""
    abre = _acha(pagina, gid)
    if not abre or any(c.get('ess') for c in cols): return cols, ag, sico
    rot = [c.get('l') for c in cols]
    falta = [x for x in abre if x not in rot]
    if falta: raise ValueError(f'visoes_marcas: {pagina} {gid}: "Abre com" sem coluna correspondente: {falta} (colunas: {rot})')
    if rot[0] != abre[0]: raise ValueError(f'visoes_marcas: {pagina} {gid}: a 1ª de "Abre com" ({abre[0]}) não é a identidade ({rot[0]})')
    out = []
    for i, c in enumerate(cols):
        c = dict(c); c.setdefault('pq', pergunta(c, i))
        if c.get('l') in abre: c['ess'] = abre.index(c['l']) + 1
        out.append(c)
    vis = set(abre)
    if sico is None:
        ks = [c['k'] for c in out if SICO_ROT.match(c.get('l') or '') and c['l'] not in vis][:1]
        ks += [c['k'] for c in out if SICO_MAIS.match(c.get('l') or '') and c['l'] not in vis]
        if ks: sico = dict(k=ks[0], ks=ks) if len(ks) > 1 else dict(k=ks[0])
    if ag is None and not tree:
        ag2 = []
        for pq in ('oque', 'quem', 'quando', 'onde'):
            cand = [c for c in out[1:] if c['pq'] == pq and c.get('t') != 'num' and (pq != 'quando' or c.get('t') == 'date')]
            cand.sort(key=lambda c: (' · ' in (c.get('l') or ''), ' › ' in (c.get('l') or '')))   # coluna de um valor só antes da composta
            if cand:
                c = cand[0]; dt = c.get('t') == 'date'
                ag2.append(dict(pq=pq, l=c['l'], niv=['Mês' if dt else c['l']], ck=[c['k']], dt=[1 if dt else 0], um='item', plural='itens'))
        if ag2: ag = ag2
    return out, ag, sico
