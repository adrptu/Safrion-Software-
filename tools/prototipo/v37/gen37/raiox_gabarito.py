"""RX-0: núcleo do oráculo; não é prova de recuperação pelo motor.

Unidade confirmada em rxRows do artefato v3: log((v2+eps)/(v1+eps))*7/gap.
Entradas são resultados de replay pareado, nunca coeficientes diários × 7.
"""
import hashlib
import json
import math
import statistics

CONTRATO = {
    'versao': 1,
    'estimando': 'contraste controlado condicionado à agenda fixa',
    'unidade': 'log-razao-semanal',
    'k_min': 20,
    'clipping_max': 0.20,
    'limiar_absoluto': math.log(1.20),
    'limiar_status': 'proposta técnica sintética, pendente de revisão',
    'agendas': ['ligado', 'desligado'],
    'safras_min': 2,
    'intervencao_clima': 'somente crescimento; eficácia de aplicação preservada',
    'referencias_clima': {'qs': False, 'molh': False, 'ur': 65},
}



# Pré-especificação anterior ao primeiro ensaio do motor. Não reduz o gate
# de 100% de direção nas fixtures determinísticas ao agregado de séries.
ENSAIO = {
    'versao': 2,
    'unidade_replica': 'semente; talhoes agrupados dentro de cada replica',
    'comparacao': 'classe e sinal; nunca magnitude beta versus delta',
    'por_safra': True,
    'limites': {'direcao_fixture_deterministica': 1.0,
                'direcao_series_fortes': 0.80, 'forte_placebo_max': 0.05,
                'forte_fraco_max': 0.05, 'forte_nao_identificavel_max': 0.0,
                'forte_nao_pareado_max': 0.0},
    'insuf': 'contar separadamente; sem denominador avaliavel nao ha aceite',
    'denominador_min': 20,
    'denominador_unidade': 'sementes distintas por safra/alvo/fator/classe esperada; nunca janelas ou talhoes',
    'denominador_regra': 'abaixo do minimo: nao avaliavel, mesmo com proporcao favoravel; nao juntar safras ou classes',
    'denominador_direcao': 'todas as replicas de classe esperada forte; insuf do motor conta no denominador e nao como acerto',
    'denominador_fixture': 'todos os casos determinísticos pre-especificados; 100% obrigatório, reportar contagem',
    'limites_status': 'proposta para revisao; proporcoes nao sao garantia estatistica',
    'ambiguo': 'sem expectativa de sinal; reportar separadamente',
    'suporte': {'talhoes_min': 3, 'alto_min': 40, 'baixo_min': 40, 'semanas_min': 5},
    'ausentes': 'nao avaliavel; sem imputacao; n14/k14 nao sao eventos',
    'estado': 'pre_especificado; ensaio nao executado',
}


def expandir_populacao(episodios, talhoes=16):
    """Exposições próprias com clima comum por réplica, sem criar eventos.

    Mantém o catálogo, o clima, o ruído e a duração de cada fonte. Varia
    n14/k14 e o gatilho de agenda por talhão, não apenas o ruído. Não garante
    suporte após exclusões; o avaliador precisa conferi-lo antes do aceite.
    A identidade fonte deve ser única por cenário/safra/semente/alvo/fator.
    """
    import copy
    if type(talhoes) is not int or talhoes < 8 or talhoes % 4:
        raise ValueError('População fatorial exige múltiplo de quatro, com pelo menos oito talhões')
    vistos, saida = set(), []
    for ep in episodios:
        chave = tuple(ep[k] for k in ('cenario','safra','semente','alvo','fator'))
        if chave in vistos:
            raise ValueError('Mais de um talhão fonte na mesma população')
        vistos.add(chave)
        for i in range(talhoes):
            novo = copy.deepcopy(ep)
            novo['cenario'] = ep['cenario']+'-populacao-v2'
            novo['talhao'] = ep['talhao']+'-P'+str(i+1).zfill(2)
            for d, dia in enumerate(novo['dias']):
                # Cruzamento completo N × K × gatilho. Cada nível de agenda
                # recebe as quatro combinações, sem selecionar por resultado.
                fase_n = math.pi*(i % 2)
                fase_k = math.pi*((i // 2) % 2)
                dia['n14'] = 6.4 + 3*(1+math.sin(d/7+fase_n))
                dia['k14'] = 10 + 8*(1+math.cos(d/9+fase_k))
            novo['politica']['gatilho'] = ep['politica']['gatilho']*(0.8+0.4*(i//4)/(talhoes//4-1))
            saida.append(novo)
    return saida


def hash_contrato():
    return hashlib.sha256(json.dumps(CONTRATO, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def crescimento(v1, v2, nc, d1, d2, corte, aplicacoes=()):
    """Mesma transformação de rxRows; recusa janelas inelegíveis e futuro."""
    vals = (v1, v2, nc, d1, d2, corte)
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or
           not math.isfinite(x) for x in vals):
        raise ValueError('Entradas finitas obrigatórias')
    if nc <= 0 or v1 < .1 * nc or v2 < 0 or not 5 <= d2-d1 <= 10 or d2 > corte:
        raise ValueError('Janela inelegível para rxRows')
    if any(d1 - 10 < dia <= d2 for dia in aplicacoes):
        raise ValueError('Aplicação interfere na janela de rxRows')
    eps = .05 * nc
    return math.log((v2 + eps)/(v1 + eps))*7/(d2-d1)


def contraste(par):
    """Cada braço fornece v1/v2; identidade/exógenos/ruído devem coincidir."""
    a, b = par['ligado'], par['desligado']
    for key in ('semente', 'safra', 'talhao', 'alvo', 'd1', 'd2', 'nc',
                'agenda_hash', 'exogenos_hash', 'ruido_hash'):
        if key not in a or key not in b or a[key] != b[key]:
            raise ValueError('Pareamento divergente: '+key)
    if not par.get('intervencao'):
        raise ValueError('Intervenção obrigatória')
    ys = [crescimento(x['v1'], x['v2'], x['nc'], x['d1'], x['d2'],
                      par['corte'], par['aplicacoes']) for x in (a, b)]
    clips = [x['dias_clipping']/(x['d2']-x['d1']) for x in (a, b)]
    if any(not 0 <= q <= 1 for q in clips):
        raise ValueError('Contagem de clipping inválida')
    return {'delta': ys[0]-ys[1], 'resultados': ys,
            'identificavel': max(clips) <= CONTRATO['clipping_max'],
            'clipping': clips, 'semente': a['semente']}


def classe(replicas):
    for r in replicas:
        if (type(r['semente']) is not int or r['semente'] < 0 or
                type(r['identificavel']) is not bool or
                isinstance(r['delta'], bool) or not isinstance(r['delta'], (int, float)) or
                not math.isfinite(r['delta'])):
            raise ValueError('Réplica inválida: semente, identificabilidade ou delta')
    if len(replicas) < CONTRATO['k_min']:
        return {'classe': 'insuficiente'}
    if len({r['semente'] for r in replicas}) != len(replicas):
        raise ValueError('Sementes duplicadas não são réplicas independentes')
    if not all(r['identificavel'] for r in replicas):
        return {'classe': 'nao_identificavel'}
    ds = [r['delta'] for r in replicas]
    mu, sd = statistics.mean(ds), statistics.stdev(ds)
    forte = abs(mu) >= CONTRATO['limiar_absoluto'] and abs(mu) >= 2*sd
    return {'classe': 'forte' if forte else 'fraco', 'media': mu, 'dp': sd,
            'sinal': 0 if abs(mu) < 1e-12 else (1 if mu > 0 else -1)}


def consolidar(agendas):
    """Não converte exclusão em fraco nem compensa uma safra com outra."""
    if len(agendas) < CONTRATO['safras_min']:
        raise ValueError('Duas safras obrigatórias')
    saida = {}
    for safra, por_agenda in agendas.items():
        if set(por_agenda) != set(CONTRATO['agendas']):
            raise ValueError('Duas agendas de sensibilidade obrigatórias')
        cs = [classe(por_agenda[k]) for k in CONTRATO['agendas']]
        sementes = [{r['semente'] for r in por_agenda[k]} for k in CONTRATO['agendas']]
        pareamento = sementes[0] == sementes[1]
        if not pareamento:
            estado = 'nao_pareado'
        elif any(c['classe'] in ('insuficiente', 'nao_identificavel') for c in cs):
            estado = 'nao_identificavel' if any(c['classe']=='nao_identificavel' for c in cs) else 'insuficiente'
        elif len({(c['classe'], c['sinal']) for c in cs}) != 1:
            estado = 'ambiguo'
        else:
            estado = cs[0]['classe']
        saida[safra] = {'classe': estado, 'agendas': cs, 'sementes_pareadas': pareamento,
                        'sinal': cs[0].get('sinal') if estado in ('forte', 'fraco') else None}
    estados = {(x['classe'], x['sinal']) for x in saida.values()}
    return {'contrato_hash': hash_contrato(), 'safras': saida,
            'classe': ('nao_pareado' if any(x['classe']=='nao_pareado' for x in saida.values()) else next(iter(estados))[0] if len(estados)==1 else 'ambiguo'),
            'recuperacao_motor': 'nao_executada'}


def replay(x0, dias, agenda, cap, fx, desligar=None):
    """Reexecuta trajetória com exógenos e eficácia já sorteados e agenda fixa.

    `dias` contém wk, clima, falta, n14, k14, imigracao, chuva e ruido_obs.
    def/n/k/lav neutralizam coeficientes. qs/molh/ur usam multiplicadores
    clima_sem explícitos do alvo; só crescimento, não eficácia de aplicação.
    Fórmula e ordem seguem simulatePest v3, inclusive decremento do resíduo.
    """
    if desligar not in (None, 'def', 'n', 'k', 'lav', 'qs', 'molh', 'ur', 'placebo'):
        raise ValueError('Fator não implementado no replay')
    efeito = dict(fx)
    if desligar in ('def', 'n', 'k', 'lav'):
        efeito[desligar] = 1 if desligar == 'lav' else 0
    if len({a['day'] for a in agenda}) != len(agenda):
        raise ValueError('Aplicações duplicadas no mesmo dia')
    apps = {a['day']: a for a in agenda}
    x, resid, saida = x0, 0, []
    for d, clima in enumerate(dias):
        if d in apps:
            ap = apps[d]
            if not 0 <= ap['eff'] <= .95 or ap['resid'] < 0:
                raise ValueError('Aplicação inválida')
            x *= 1-ap['eff']
            resid = ap['resid']
        multiplicador = clima['clima']
        if desligar in ('qs', 'molh', 'ur'):
            multiplicador = clima['clima_sem'][desligar]
        g = clima['wk']**(1/7)*multiplicador*(1 + efeito['def']*clima['falta'] +
                efeito['n']*(clima['n14']-6.4) + efeito['k']*max(0, 1-clima['k14']/20))
        if resid > 0:
            g = 1+(g-1)*.2
            resid -= 1
        bruto = x*g + clima['imigracao']*(.3 if resid > 0 else 1)
        clipping = bruto < .05 or bruto > cap
        x = max(.05, min(cap, bruto))
        if clima['chuva'] >= 10:
            lavado = x*efeito['lav']
            clipping = clipping or lavado < .05
            x = max(.05, lavado)
        saida.append({'day': d, 'x': x, 'v': max(0, x*clima['ruido_obs']),
                      'clipping': clipping, 'resid': resid})
    return saida


def digest(valor):
    return hashlib.sha256(json.dumps(valor, sort_keys=True, allow_nan=False,
                                     separators=(',', ':')).encode()).hexdigest()


def agenda_observada(x0, dias, cap, fx, observacoes, nc, politica, desligar=None):
    """Agenda adaptativa observada; depois é congelada nos dois braços.

    Com produtos/cobertura usa a escolha, resistência e eficácia do v3.
    O ruído de aplicação é pré-sorteado por dia. Sem produtos, conserva a
    política simplificada apenas para controles sintéticos explícitos.
    """
    agenda, ultimo, pendente = [], -99, None
    grupo, consecutivos, contagem = None, 0, {}
    for dia in range(len(dias)):
        if pendente == dia:
            if 'produtos' in politica:
                produtos, n = politica['produtos'], len(agenda)
                oleos = [p for p in produtos if p['c'] == 'Óleo mineral']
                if politica.get('oleo1') and n == 0 and oleos:
                    produto = oleos[0]
                elif politica.get('repete'):
                    produto = next((p for p in produtos if p['c'] != 'Óleo mineral'), produtos[0])
                else:
                    candidatos = [p for p in produtos if p['c'] != 'Óleo mineral' and p['g'] != grupo]
                    produto = candidatos[(n + politica['id_tamanho']) % len(candidatos)] if candidatos else produtos[0]
                repeticoes = contagem.get(produto['g'], 0)
                consecutivos = consecutivos+1 if produto['g'] == grupo else 0
                resistencia = .7**consecutivos if consecutivos > 0 else .93**repeticoes
                chuva_depois = dias[dia]['chuva'] + (dias[dia+1]['chuva'] if dia+1 < len(dias) else 0) >= 5
                cov = politica['cobertura']
                eff = min(.95, produto['base']*cov*resistencia *
                          (politica['app_qs'] if dias[dia].get('quenteSeco', False) else 1) *
                          (politica['app_chuva'] if chuva_depois else 1) *
                          (.9 + dias[dia]['ruido_app']*.18))
                resid = math.floor(produto['res']*(.7+.3*cov)+.5)
                contagem[produto['g']] = repeticoes+1
                grupo = produto['g']
                agenda.append({'day': dia, 'eff': eff, 'resid': resid, 'produto': produto['c'],
                               'grupo': grupo, 'rep': repeticoes+1, 'consec': consecutivos})
            else:
                agenda.append({'day': dia, 'eff': dias[dia]['eff'], 'resid': politica['resid']})
            ultimo, pendente = dia, None
        if dia in observacoes:
            valor = replay(x0, dias[:dia+1], agenda, cap, fx, desligar)[-1]['v']
            if valor >= nc*politica['gatilho'] and dia-ultimo > 9 and pendente is None:
                proximo = min(len(dias)-1, dia+politica['delay'])
                if proximo > dia:
                    pendente = proximo
    return agenda


def gerar(episodios):
    """Produz entradas observáveis separadas do oráculo de intervenção.

    Recebe episódios com exógenos já sorteados; não calibra limiar nos resultados.
    Agrupa por cenário, talhão, alvo, fator e janela. Não mede recuperação.
    """
    # Rejeita NaN/Infinity no pacote antes de calcular ou mascarar por clipping.
    digest(episodios)
    entradas, pares, grupos, exclusoes, identidades = [], [], {}, {}, set()
    mundos = {}
    for ep in episodios:
        if type(ep['semente']) is not int or ep['semente'] < 0:
            raise ValueError('Semente inteira não negativa obrigatória')
        for campo in ('x0', 'cap', 'nc'):
            valor = ep[campo]
            if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor <= 0:
                raise ValueError('Grandeza positiva obrigatória: '+campo)
        chave_ep = tuple(ep[k] for k in ('cenario', 'safra', 'semente', 'talhao', 'alvo', 'fator'))
        if chave_ep in identidades:
            raise ValueError('Episódio duplicado')
        identidades.add(chave_ep)
        dias, obs, fator = ep['dias'], ep['observacoes'], ep['fator']
        if sorted(set(obs)) != obs or any(not isinstance(d, int) or d < 0 or d >= len(dias) for d in obs):
            raise ValueError('Dias de observação inválidos')
        if ep['politica']['delay'] < 1:
            raise ValueError('Atraso deve ser positivo')
        for referencia in CONTRATO['agendas']:
            agenda = agenda_observada(ep['x0'], dias, ep['cap'], ep['fx'], obs,
                                      ep['nc'], ep['politica'], fator if referencia=='desligado' else None)
            trajetorias = {braco: replay(ep['x0'], dias, agenda, ep['cap'], ep['fx'],
                            fator if braco=='desligado' else None) for braco in CONTRATO['agendas']}
            entrada = {k: ep[k] for k in ('cenario', 'safra', 'semente', 'talhao', 'alvo', 'nc')}
            entrada.update(id=digest(chave_ep[:-1]),
                           series=[{'day': d, 'clima': q.get('clima_observado'),
                                    'chuva': q['chuva'], 'falta_agua': q['falta'],
                                    'n14': q['n14'], 'k14': q['k14'],
                                    'covariavel_teste': q.get('covariavel_teste')} for d, q in enumerate(dias)],
                           proveniencia='gerador sintético RX-0; sem dados reais',
                           agenda_referencia=referencia,
                           obs=[{'day': d, 'v': trajetorias[referencia][d]['v']} for d in obs],
                           apps=[{'day': a['day']} for a in agenda])
            if referencia == 'ligado':
                mundo = chave_ep[:-1]
                if mundo in mundos and mundos[mundo] != entrada:
                    raise ValueError('Mundo factual conflitante')
                if mundo not in mundos:
                    mundos[mundo] = entrada
                    entradas.append(entrada)
            for d1, d2 in zip(obs, obs[1:]):
                chave = tuple(ep[k] for k in ('cenario', 'talhao', 'alvo', 'fator'))+(d1,d2)
                safra = grupos.setdefault(chave, {}).setdefault(ep['safra'], {a: [] for a in CONTRATO['agendas']})
                base = {k: ep[k] for k in ('semente', 'safra', 'talhao', 'alvo', 'nc')}
                base.update(d1=d1, d2=d2, agenda_hash=digest(agenda), exogenos_hash=digest(dias),
                            ruido_hash=digest([d['ruido_obs'] for d in dias]))
                par = {'intervencao': fator, 'corte': obs[-1], 'aplicacoes': [a['day'] for a in agenda],
                       'cenario': ep['cenario'], 'agenda_referencia': referencia}
                for braco, traj in trajetorias.items():
                    par[braco] = dict(base, v1=traj[d1]['v'], v2=traj[d2]['v'],
                                      dias_clipping=sum(q['clipping'] for q in traj[d1+1:d2+1]))
                contagem = exclusoes.setdefault(ep['safra'], {'total': 0, 'inelegivel': 0, 'clipping': 0})
                contagem['total'] += 1
                try:
                    resultado = contraste(par)
                    contagem['clipping'] += not resultado['identificavel']
                    safra[referencia].append(resultado)
                    par['resultado'] = resultado
                except ValueError as erro:
                    # Preserve a janela recusada no bruto; não a converta em efeito zero.
                    contagem['inelegivel'] += 1
                    par['exclusao'] = str(erro)
                pares.append(par)
    classificados = []
    for chave, safras in sorted(grupos.items()):
        classificados.append({'chave': chave, 'resultado': consolidar(safras)})
    classes_por_safra = {}
    for item in classificados:
        for safra, resultado in item['resultado']['safras'].items():
            c = classes_por_safra.setdefault(safra, {'total': 0, 'contagens': {}})
            estado = resultado['classe']
            c['total'] += 1
            c['contagens'][estado] = c['contagens'].get(estado, 0)+1
    for c in classes_por_safra.values():
        c['denominador'] = 'grupos cenário/talhão/alvo/fator/janela, consolidados entre agendas'
        c['fracoes'] = {estado: c['contagens'].get(estado, 0)/c['total']
                        for estado in ('forte', 'fraco', 'ambiguo', 'nao_identificavel', 'insuficiente', 'nao_pareado')}
    for c in exclusoes.values():
        c['fracao_excluida'] = (c['inelegivel']+c['clipping'])/c['total'] if c['total'] else None
    return {'entrada': entradas, 'oraculo': {'contrato': CONTRATO, 'contrato_hash': hash_contrato(),
            'entrada_hash': digest(entradas), 'pares': pares, 'classes': classificados,
            'exclusoes_por_safra': exclusoes, 'classes_por_safra': classes_por_safra, 'recuperacao_motor': 'nao_executada'}}


def medir_suporte(entradas):
    """Condições necessárias por réplica; não testa limiar/colinearidade do motor."""
    # Dado malformado não é exclusão agronômica. Validar também observações
    # isoladas e aplicações fora das janelas antes de contar qualquer suporte.
    digest(entradas)
    for e in entradas:
        valores = [e['nc']] + [x[k] for x in e['obs'] for k in ('day', 'v')] + [x['day'] for x in e['apps']]
        if any(type(x) not in (int, float) or not math.isfinite(x) for x in valores):
            raise ValueError('Suporte exige observações e aplicações finitas')
        if e['nc'] <= 0 or any(x['v'] < 0 for x in e['obs']):
            raise ValueError('Suporte exige NC positivo e observações não negativas')
        if any(a['day'] >= b['day'] for a,b in zip(e['obs'], e['obs'][1:])):
            raise ValueError('Suporte exige observações em ordem estritamente crescente')
    grupos = {}
    for e in entradas:
        chave = tuple(e[k] for k in ('cenario', 'safra', 'semente', 'alvo'))
        g = grupos.setdefault(chave, {'janelas': 0, 'excluidas': 0, 'talhoes': set(), 'semanas': set()})
        apps = [a['day'] for a in e['apps']]
        for a,b in zip(e['obs'], e['obs'][1:]):
            try:
                crescimento(a['v'], b['v'], e['nc'], a['day'], b['day'], e['obs'][-1]['day'], apps)
            except ValueError:
                g['excluidas'] += 1
                continue
            g['janelas'] += 1
            g['talhoes'].add(e['talhao'])
            g['semanas'].add(b['day']//7)
    saida = []
    for chave,g in sorted(grupos.items()):
        saida.append(dict(zip(('cenario','safra','semente','alvo'),chave),
                          janelas=g['janelas'], excluidas=g['excluidas'],
                          talhoes=len(g['talhoes']), semanas=len(g['semanas']),
                          necessario=(g['janelas'] >= 80 and len(g['talhoes']) >= 3 and len(g['semanas']) >= 5),
                          suporte_alto_baixo='nao_avaliado', recuperacao_motor='nao_executada'))
    return saida


def selecionar_disponiveis(registros, corte, protocolo, unidade):
    """Contrato temporal de QA (dias sintéticos); não é adaptador do MIP.

    Revisão conhecida mais recente prevalece, inclusive se remove o valor.
    Previsão futura só é legível quando já publicada no corte; fatos futuros
    nunca entram. Protocolo/unidade incompatíveis são exclusões explícitas.
    """
    digest(registros)
    recentes, vistos, excluidos = {}, set(), []
    for r in registros:
        if not r.get('fonte') or not r.get('id') or type(r.get('versao')) is not int:
            raise ValueError('Identidade, versão e fonte obrigatórias')
        if r.get('tipo') not in ('fato', 'previsao'):
            raise ValueError('Tipo de registro desconhecido')
        for campo in ('dia', 'disponivel_em'):
            if type(r.get(campo)) is not int:
                raise ValueError('Dia inteiro obrigatório: '+campo)
        chave = (r['id'], r['versao'])
        if chave in vistos:
            raise ValueError('Versão duplicada')
        vistos.add(chave)
        if r['disponivel_em'] > corte:
            excluidos.append({'id': r['id'], 'versao': r['versao'], 'motivo': 'ainda_nao_disponivel'})
            continue
        anterior = recentes.get(r['id'])
        if anterior is None or (r['disponivel_em'], r['versao']) > (anterior['disponivel_em'], anterior['versao']):
            recentes[r['id']] = r
    conhecidos = {}
    for r in registros:
        if r['disponivel_em'] <= corte:
            conhecidos.setdefault(r['id'], []).append(r)
    for revisoes in conhecidos.values():
        ordenadas = sorted(revisoes, key=lambda r: r['versao'])
        if any(a['disponivel_em'] > b['disponivel_em'] for a,b in zip(ordenadas, ordenadas[1:])):
            raise ValueError('Versão e publicação fora de ordem')
    elegiveis = []
    for r in recentes.values():
        motivo = None
        if r['tipo']=='fato' and r['dia'] > corte:
            motivo = 'fato_futuro'
        elif r.get('protocolo') != protocolo or r.get('unidade') != unidade:
            motivo = 'protocolo_ou_unidade_incompativel'
        elif r.get('valor') is None:
            motivo = 'valor_ausente'
        elif isinstance(r['valor'], bool) or not isinstance(r['valor'], (int, float)):
            raise ValueError('Valor numérico ou ausência explícita obrigatórios')
        if motivo:
            excluidos.append({'id': r['id'], 'versao': r['versao'], 'motivo': motivo})
        else:
            elegiveis.append(dict(r))
    return {'registros': sorted(elegiveis, key=lambda r: (r['dia'], r['id'])),
            'exclusoes': excluidos, 'corte': corte}


def seguimento_nc(observacoes, aplicacao, nc, corte, outras_aplicacoes=()):
    """Oráculo QA de intervalo/censura; observações já disponíveis no corte.

    Não interpola o dia exato. A leitura do dia da nova aplicação é excluída
    porque a ordem dentro do dia é desconhecida. Não estima sobrevivência.
    """
    digest([observacoes, aplicacao, nc, corte, outras_aplicacoes])
    if not isinstance(nc, (int, float)) or isinstance(nc, bool) or nc <= 0:
        raise ValueError('NC positivo obrigatório')
    interferencia = min((d for d in outras_aplicacoes if aplicacao < d <= corte), default=None)
    leituras = sorted((o for o in observacoes if aplicacao < o['day'] <= corte and
                      (interferencia is None or o['day'] < interferencia)), key=lambda o: o['day'])
    if len({o['day'] for o in leituras}) != len(leituras):
        raise ValueError('Leituras duplicadas no mesmo dia')
    ultima = None
    for o in leituras:
        if o.get('v') is None:
            continue
        if isinstance(o['v'], bool) or not isinstance(o['v'], (int, float)) or o['v'] < 0:
            raise ValueError('Leitura inválida')
        if o['v'] >= nc:
            if ultima is None:
                return {'estado': 'primeira_leitura_ja_acima', 'dia_leitura': o['day'], 'intervalo': None}
            return {'estado': 'retorno_em_intervalo', 'intervalo': [ultima['day'], o['day']],
                    'limites': 'aberto à esquerda, fechado à direita'}
        ultima = o
    return {'estado': 'censurado' if ultima else 'sem_leitura_valida',
            'ultima_leitura': ultima['day'] if ultima else None,
            'motivo': 'nova_aplicacao' if interferencia is not None else 'corte',
            'interferencia': interferencia}


def eficacia_referencia(tratado, controles, aplicacao, corte):
    """HT clássico de QA, sem epsilon/fallback; pares já disponíveis até D.

    Cada par declara pré/pós/datas/unidade/protocolo e interferência. Não
    procura controles nem prova comparabilidade agronômica ou causalidade.
    """
    digest([tratado, controles, aplicacao, corte])
    def motivo(p):
        if not p.get('unidade') or not p.get('protocolo'):
            return 'contexto_ausente'
        if not p['antes_dia'] < aplicacao < p['depois_dia'] <= corte:
            return 'datas_inelegiveis'
        if p.get('interferencia', False):
            return 'aplicacao_interferente'
        for campo in ('antes', 'depois'):
            v = p.get(campo)
            if v is None:
                return 'valor_ausente'
            if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
                raise ValueError('Contagem inválida')
        return None
    falha = motivo(tratado)
    if falha or tratado['antes'] == 0:
        return {'estado': 'sem_comparacao_valida', 'motivo': falha or 'denominador_zero', 'pares': []}
    validos, excluidos = [], []
    for c in controles:
        falha = motivo(c)
        if c.get('unidade') != tratado.get('unidade') or c.get('protocolo') != tratado.get('protocolo'):
            falha = 'protocolo_ou_unidade_incompativel'
        if falha is None and (c['antes_dia'], c['depois_dia']) != (tratado['antes_dia'], tratado['depois_dia']):
            falha = 'datas_nao_pareadas'
        if falha is None and (c['antes'] == 0 or c['depois'] == 0):
            falha = 'denominador_zero'
        if falha:
            excluidos.append({'id': c['id'], 'motivo': falha})
            continue
        validos.append({'controle': c['id'], 'eficacia': 1-(tratado['depois']/tratado['antes'])*(c['antes']/c['depois'])})
    return {'estado': 'comparacoes_calculadas' if validos else 'sem_comparacao_valida',
            'pares': validos, 'exclusoes': excluidos}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('episodios', help='JSON de episódios/exógenos pré-sorteados')
    parser.add_argument('--suporte-populacao', type=int, metavar='TALHOES', help='Só mede suporte por réplica, sem executar motor')
    args = parser.parse_args()
    with open(args.episodios, encoding='utf8') as f:
        episodios = json.load(f)
    if args.suporte_populacao is not None:
        grupos = {}
        for e in episodios:
            chave = tuple(e[k] for k in ('cenario','semente','alvo'))
            grupos.setdefault(chave, []).append(e)
        suporte = []
        for grupo in grupos.values():
            p = gerar(expandir_populacao(grupo,args.suporte_populacao))
            suporte.extend(medir_suporte(p['entrada']))
        pacote = {'ensaio': ENSAIO, 'ensaio_hash': digest(ENSAIO), 'suporte': suporte}
    else:
        pacote = gerar(episodios)
    print(json.dumps(pacote, ensure_ascii=False, sort_keys=True, allow_nan=False))
