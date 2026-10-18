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
}


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
        if any(c['classe'] in ('insuficiente', 'nao_identificavel') for c in cs):
            estado = 'nao_identificavel' if any(c['classe']=='nao_identificavel' for c in cs) else 'insuficiente'
        elif len({(c['classe'], c['sinal']) for c in cs}) != 1:
            estado = 'ambiguo'
        else:
            estado = cs[0]['classe']
        saida[safra] = {'classe': estado, 'agendas': cs,
                        'sinal': cs[0].get('sinal') if estado in ('forte', 'fraco') else None}
    estados = {(x['classe'], x['sinal']) for x in saida.values()}
    return {'contrato_hash': hash_contrato(), 'safras': saida,
            'classe': next(iter(estados))[0] if len(estados)==1 else 'ambiguo',
            'recuperacao_motor': 'nao_executada'}


def replay(x0, dias, agenda, cap, fx, desligar=None):
    """Reexecuta trajetória com exógenos e eficácia já sorteados e agenda fixa.

    `dias` contém wk, clima, falta, n14, k14, imigracao, chuva e ruido_obs.
    Só def/n/k/lav podem ser neutralizados nesta etapa. Não altera a agenda.
    Fórmula e ordem seguem simulatePest v3, inclusive decremento do resíduo.
    """
    if desligar not in (None, 'def', 'n', 'k', 'lav'):
        raise ValueError('Fator não implementado no replay')
    efeito = dict(fx)
    if desligar:
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
        g = clima['wk']**(1/7)*clima['clima']*(1 + efeito['def']*clima['falta'] +
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
    entradas, pares, grupos, exclusoes, identidades = [], [], {}, {}, set()
    for ep in episodios:
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
            entrada.update(agenda_referencia=referencia,
                           obs=[{'day': d, 'v': trajetorias[referencia][d]['v']} for d in obs],
                           apps=[{'day': a['day']} for a in agenda])
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
    for c in exclusoes.values():
        c['fracao_excluida'] = (c['inelegivel']+c['clipping'])/c['total'] if c['total'] else None
    return {'entrada': entradas, 'oraculo': {'contrato': CONTRATO, 'contrato_hash': hash_contrato(),
            'entrada_hash': digest(entradas), 'pares': pares, 'classes': classificados,
            'exclusoes_por_safra': exclusoes, 'recuperacao_motor': 'nao_executada'}}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('episodios', help='JSON de episódios/exógenos pré-sorteados')
    args = parser.parse_args()
    with open(args.episodios, encoding='utf8') as f:
        pacote = gerar(json.load(f))
    print(json.dumps(pacote, ensure_ascii=False, sort_keys=True, allow_nan=False))
