# -*- coding: utf-8 -*-
"""MAPA-FROTA F1 · fixture da simulação (docs/integracao/V71/MAPA-FROTA.md, decisão 7).

Percursos em metros relativos à âncora do talhão (centro do pivô ou centróide do desenho), velocidades, intervalo e limite de idade,
marca "simulação" e o conjunto de demonstração da Lagoa Grande (Trator LG-01 + Carreta de colheita LG ligados à OS-0505).
Fora da alocação e do cadastro: nada aqui é ativo, alocação, apontamento, consumo, carga nem fase. As leituras nascem no navegador e não
são gravadas; a Lagoa Grande usa o centro do pivô da geometria da página (real ou sintética) sem gravar coordenada."""
import json
import dados2 as D2
import dados_cad as DC
import alocacao as AL

_REND = {c['op']: c['rend'] for c in D2.CONJ}
_ATV = {a['id']: a for a in DC.ATIVOS}

FROTA0 = dict(
    intervalo_s=10,                 # uma leitura a cada 10 s (leituras discretas, sem interpolação na F1)
    limite_s=60,                    # idade-limite da fonte simulada: 60 s é "Atual"; 61 s é "Sem sinal há 1 min" (M5)
    passada_m=36, recuo_m=18,       # passadas paralelas a cada 36 m, com recuo de 18 m nas cabeceiras
    base=[-34.629941, -47.122425],  # âncora sintética das leituras do desenho da Santa Rita (no mar, lat < −34): nunca coordenada real
    vel_kmh={'Pulverização': 8, 'Colheita': 3, 'padrao': 6},
    paradas={'Colheita': dict(anda_s=90, para_s=30)},   # colheita a 3 km/h com paradas ("Parada · carregando")
    simula=['OS-0421', 'OS-0505'],  # só estas têm fonte simulada; OS-0420 e as demais em execução ficam sem fonte (posição indisponível)
    rota_tal={'OS-0421': 'T2'},     # OS-0421 (T1+T2): o percurso fica no T2, onde está o saldo
    demo={'OS-0505': dict(componentes=[dict(id='LG01', papel='trator', nome='Trator LG-01'),
                                       dict(id='CARLG', papel='implemento', nome='Carreta de colheita LG')])},
    # rendimento de referência por família (DEC-2609-03, dados2.CONJ) para o "≈ h" do quanto falta, rotulado como estimativa
    rend={'Pulverização': _REND['Pulverização'], 'Plantio': _REND['Plantio'], 'Adubação e correção': _REND['Adubação a lanço']},
    # capacidade do tanque por recurso (CD-03) para a projeção de preparo do EX-38 (tanque ÷ vazão da O.S.)
    tanque={AL.REC_DO_ATIVO[k]: a['tanque'] for k, a in _ATV.items() if a.get('tanque') and k in AL.REC_DO_ATIVO},
)


def js():
    """FROTA0 + regras (frota.js) + ícones das famílias (engine.ICONS) + camada da tela (frota_ui.js), para o IN-04."""
    import os
    from engine import icon
    here = os.path.dirname(os.path.abspath(__file__))
    ic = {k: icon(k if k in ('Colheita', 'truck', 'wrench') else 'Irrigação' if k == 'Irrigação' else 'f_' + k, 18, '#FFFFFF')
          for k in ('gotas', 'broto', 'graos', 'grade', 'Colheita', 'truck', 'Irrigação', 'wrench')}
    return ('const FROTA0 = ' + json.dumps(FROTA0, ensure_ascii=False) + ';\nconst FR_ICONES = ' + json.dumps(ic, ensure_ascii=False) + ';\n'
            + open(os.path.join(here, 'frota.js'), encoding='utf-8').read() + '\n'
            + open(os.path.join(here, 'frota_ui.js'), encoding='utf-8').read() + '\n')


if __name__ == '__main__':
    print(json.dumps(FROTA0, ensure_ascii=False, indent=1))
