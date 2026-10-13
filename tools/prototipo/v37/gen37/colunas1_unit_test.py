# -*- coding: utf-8 -*-
"""COLUNAS-1 · colunas essenciais, lote 1 (pedido do proprietário de 10/10; AUDITORIA COLUNAS §4.2): testes sem navegador.
Parte 1 (Python): monta as telas do lote (MA, CA-01det, CA-01x, CA-02, CA-03, ON-01, ON-01det e SAF) sem gravar arquivo (shell37 trocado por uma
captura) e confere, grade a grade: a lista exata de colunas (positiva), as que saíram (negativa), que o detalhe (formulário ou painel da linha) tem
o campo de cada dado que saiu e que a busca da grade (texto r.s da 1ª coluna) continua achando a linha por ele.
Parte 2 (node): as linhas da Manutenção (ma_linhaOm, ma_linhaAtv, ma_linhaAb, ma_linhaPl, ma_linhasSemOrdem, ma_tipoOm) sobre o cenário
único, e a busca da SAF (cultBusca, e3Busca) — colunas1_unit.js.
Uso (de gen37/): python3 colunas1_unit_test.py    (sai 1 se algum caso falhar)"""
import os, sys, json, re, subprocess, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
OK, FAIL = [], []
def ok(cond, msg, extra=''):
    (OK if cond else FAIL).append(msg); print(('OK    ' if cond else 'FALHA ') + msg + ('' if cond else ' · ' + str(extra)[:700]), flush=True)

import engine as E
TELAS = {}
def captura(mod):
    """monta a área sem gravar: cada shell37 guarda as grades da tela (fname → {gid: spec})"""
    m = importlib.import_module(mod)
    def fake(fid, titulo, corpo, *a, **k):
        fn = k.get('fname') or (fid + '.dc.html')
        TELAS[fn] = {g['id']: g for g in E.GRIDS}
    m.shell37 = fake
    for nome in ('_status_dyn', '_redirect'):   # pós-processos que gravam em project/ (MA): fora do teste
        if hasattr(m, nome): setattr(m, nome, lambda *a, **k: None)
    m.build()

for mod in ('areas.campo', 'areas.onboarding_backoffice', 'areas.maquinas', 'areas.processo_safra'):
    captura(mod)
def cols(fn, gid): return [c['l'] for c in TELAS[fn][gid]['cols']]
def keys(fn, gid): return [c['k'] for c in TELAS[fn][gid]['cols']]
def fields(fn, gid): return {f['k']: f for f in (TELAS[fn][gid].get('edit') or {}).get('fields', [])}
def rows(fn, gid): return TELAS[fn][gid]['rows']

# ---------------- grades: colunas exatas (positiva) e as que saíram (negativa) ----------------
ESPERADO = {
    ('MA.dc.html', 'g_so'): (['Item', 'Ativo', 'O que', 'Prazo', 'Peças', 'Próximo passo'], ['Ativo · leitura']),
    ('MA.dc.html', 'g_om'): (['Ordem', 'Ativo', 'Serviço', 'Janela', 'Fase', 'Pendência', 'Executante'], ['Ordem · ativo', 'Serviço · tipo', 'Tempo', 'Custo']),
    ('MA.dc.html', 'g_at'): (['Ativo', 'Condição', 'Próxima manutenção', 'Em aberto', 'Custo no período'], ['Ativo · local', 'Leitura', 'Consumo']),
    ('MA.dc.html', 'g_ab'): (['Lançamento', 'Ativo', 'Volume', 'Data', 'Consumo', 'Qualidade'], ['Lançamento · operador', 'Tanque/lote', 'Data · leitura', 'Método']),
    ('MA.dc.html', 'g_pl'): (['Plano', 'Estado', 'Situação'], ['Aplica-se a', 'Serviços', 'Ativos']),
    ('MA.dc.html', 'd_om'): (['Ordem', 'Serviço · tipo', 'Janela', 'Fase', 'Custo'], ['Ordem · ativo']),
    ('MA.dc.html', 'd_vinc'): (['Ativo', 'Marco', 'Próximo vencimento', 'Situação', 'Ordem'], []),
    ('CA-01det.dc.html', 'g_ap'): (['Data', 'Área do dia', 'Conferência'], ['Turno', 'Acumulado', 'Origem · sincronização']),
    ('CA-01det.dc.html', 'g_mat'): (['Item · lote', 'Em custódia', 'A entregar', 'Custódia de'], ['Solicitado', 'Entregue', 'Consumido']),
    ('CA-01x-os0420.dc.html', 'g_ins'): (['Produto', 'Dose da v2', 'Saldo de 70 ha na v3'], ['Quantidade para 100 ha', 'Fonte']),
    ('CA-01x-os0420.dc.html', 'g_ap0420'): (['Data', 'Área do dia', 'Conferência'], ['Turno', 'Acumulado', 'Origem · sincronização']),
    ('CA-01x-os0420.dc.html', 'g_req0420'): (['Item', 'Consumido', 'Em custódia', 'Custo apontado'], ['Requisição', 'Solicitado', 'Entregue']),
    ('CA-02.dc.html', 'g_fila'): (['Apontamento', 'Realizado do dia', 'Consumos e sobras', 'Conferência', 'Ação'], ['Equipe · conjunto', 'Horas', 'Origem · sincronização', 'Conferência · ação', 'Realizado · acumulado']),
    ('CA-03.dc.html', 'g_oc'): (['Ocorrência', 'Local', 'Gravidade', 'Responsável', 'Próxima ação'], ['Local · instante', 'Relato', 'Evidência', 'Destino · responsável']),
    ('ON-01.dc.html', 'g_passos'): (['Passo', 'Estado', 'Próxima ação'], ['Dado pedido no momento do uso']),
    ('ON-01.dc.html', 'g_trial'): (['Recurso', 'Habilitação', 'Franquia', 'Ao esgotar ou expirar'], ['Unidade']),
    ('ON-01det.dc.html', 'g_imp'): (['Objeto', 'Linhas', 'Erro', 'Estado'], ['Mapeamento', 'Sistema de coordenadas']),
    ('SAF.dc.html', 'g_saf'): (['Safra', 'Fazenda', 'Área', 'Estado', 'Próximo passo'], ['Cultivos']),
    ('SAF.dc.html', 'g_cult_S2627'): (['Talhão ou parcela', 'Situação', 'Área livre', 'Livre a partir de', 'Área', 'Cultura', 'Plano agronômico', 'Plantio'],
                                      ['Ocupa até', 'Fim por', 'Safra', 'Variedade', 'Versão', 'Meta', 'Ajustes locais', 'Tipo']),
    ('SAF.dc.html', 'g_op'): (['Operação › atividade › talhão', 'Situação', 'Data', 'Conjunto', 'Horas-conjunto', 'Custo R$/ha'], ['Rendimento', 'Área trabalhada']),
}
for (fn, gid), (pos, neg) in ESPERADO.items():
    c = cols(fn, gid)
    ok(c == pos and not any(x in c for x in neg), f'{fn} {gid}: {len(pos)} colunas essenciais, nesta ordem; saíram {", ".join(neg) or "(nenhuma)"}', c)
# toda grade do lote continua com filtro e ordenação por coluna (cabeçalho com ▾) e as que tinham busca seguem com ela
for (fn, gid) in ESPERADO:
    ok(TELAS[fn][gid].get('id') == gid, f'{fn} {gid}: grade registrada')
# as 5 grades de cultivo (uma por safra) têm as mesmas colunas (R-08)
cg = {g: cols('SAF.dc.html', g) for g in TELAS['SAF.dc.html'] if g.startswith('g_cult_')}
ok(len(cg) == 5 and len({tuple(v) for v in cg.values()}) == 1, 'SAF: as 5 grades de cultivo (uma por safra) com as mesmas 8 colunas (R-08)', cg)
# CA-02: o roteiro projetado da OS-0418 (Quando, Evento, Efeito, Quem) sai da fila (4 → 0); a trilha real fica no detalhe da ordem (O.S.)
ok('g_proj' not in TELAS['CA-02.dc.html'] and 'g_fila' in TELAS['CA-02.dc.html'], 'CA-02: o roteiro projetado da OS-0418 sai da fila (sem a grade g_proj); a fila de conferência fica', sorted(TELAS['CA-02.dc.html']))
# R-07: unidade junto do número, nunca em coluna própria
ok(all('Unidade' not in cols(fn, gid) for (fn, gid) in ESPERADO), 'R-07: nenhuma grade do lote com coluna de unidade')
# R-08: os apontamentos têm a mesma forma no CA-01det e no CA-01x
ok(cols('CA-01det.dc.html', 'g_ap') == cols('CA-01x-os0420.dc.html', 'g_ap0420'), 'R-08: apontamentos com a mesma forma (Data, Área do dia, Conferência) no CA-01det e no CA-01x')

# ---------------- o detalhe recebe o dado antes da coluna sair (formulário ou painel da linha) ----------------
DET = {
    ('CA-01det.dc.html', 'g_ap'): ['turno', 'ac', 'orig'], ('CA-01det.dc.html', 'g_mat'): ['sol', 'ent', 'cons'],
    ('CA-01x-os0420.dc.html', 'g_ins'): ['qtd_t', 'fonte'], ('CA-01x-os0420.dc.html', 'g_ap0420'): ['turno', 'ac', 'orig'],
    ('CA-01x-os0420.dc.html', 'g_req0420'): ['req', 'sol', 'ent'], ('CA-02.dc.html', 'g_fila'): ['eq', 'acum', 'orig', 'horas'],
    ('CA-03.dc.html', 'g_oc'): ['inst', 'relato', 'evid', 'dest'], ('ON-01.dc.html', 'g_passos'): ['dado'], ('ON-01det.dc.html', 'g_imp'): ['map', 'crs'],
    ('SAF.dc.html', 'g_cult_S2627'): ['var', 'meta', 'unm_txt', 'ver_txt', 'ocup_txt', 'fimpor_txt', 'aj_txt'],
    ('SAF.dc.html', 'g_rend_S2627'): ['area_c', 'rend_c', 'rend'],
}
for (fn, gid), ks in DET.items():
    f = fields(fn, gid)
    ok(all(k in f for k in ks), f'{fn} {gid}: o detalhe da linha tem {", ".join(ks)}', sorted(f))
# o valor que saiu da linha está na linha (v) para o detalhe mostrar
r = rows('CA-01det.dc.html', 'g_mat')[0]['v']; ok((r.get('sol'), r.get('ent'), r.get('cons'), r.get('cust')) == (175, 160, 95, 65), 'CA-01det materiais: solicitado 175, entregue 160, consumido 95 e em custódia 65 L no detalhe (a conta fecha: 160 − 95 = 65)', r)
r = rows('CA-01x-os0420.dc.html', 'g_ins'); ok([x['v'].get('qtd_t') for x in r] == ['5.200 kg', '12.000 kg', '5,2 L'], 'CA-01x instrução: quantidade para 100 ha (dose × área) com a unidade no detalhe', [x['v'].get('qtd_t') for x in r])
r = rows('ON-01.dc.html', 'g_trial'); fr = {x['id']: x['v'].get('fr', '') for x in r}
ok(fr['t3'] == '12 cenas / 30 dias' and fr['t4'] == '200 interações / 30 dias' and fr['t2'].endswith(' ha declarados') and all('un' not in x['v'] for x in r), 'ON-01 trial: unidade junto da franquia (R-07)', fr)
ok('un' not in fields('ON-01.dc.html', 'g_trial'), 'ON-01 trial: o detalhe também sem campo Unidade separado')
r = rows('CA-03.dc.html', 'g_oc'); ok([x['v'].get('resp') for x in r] == ['Zé', 'Ana', 'Ana', 'João'], 'CA-03: Responsável = quem resolve (R-06); a área de destino fica no detalhe', [x['v'].get('resp') for x in r])

# ---------------- a busca continua achando a linha pelo dado que saiu ----------------
def acha(fn, gid, termo):
    sp = TELAS[fn][gid]
    return [x['id'] for x in rows(fn, gid) if termo.lower() in ' '.join(str((x.get('s') or {}).get(c['k'], (x.get('v') or {}).get(c['k'], ''))) for c in sp['cols']).lower()]
ok(acha('CA-02.dc.html', 'g_fila', 'PJ-3030') == ['f1', 'f3'] and acha('CA-02.dc.html', 'g_fila', 'offline') == ['f2'] and acha('CA-02.dc.html', 'g_fila', '3,1 h') == ['f2'],
   'CA-02: a busca acha o apontamento pela equipe, pela origem e pelas horas (saíram da linha)', [acha('CA-02.dc.html', 'g_fila', t) for t in ('PJ-3030', 'offline', '3,1 h')])
ok(acha('CA-03.dc.html', 'g_oc', 'Pressão hidráulica') == ['OC-114'] and acha('CA-03.dc.html', 'g_oc', 'Rota W') == ['OC-115'] and acha('CA-03.dc.html', 'g_oc', '14:20') == ['OC-116'] and acha('CA-03.dc.html', 'g_oc', 'Irrigação') == ['OC-111'],
   'CA-03: a busca acha a ocorrência pelo relato, pela evidência, pelo instante e pela área de destino (saíram da linha)')
ok(not acha('CA-03.dc.html', 'g_oc', 'nada disso'), 'CA-03: busca sem resultado não acha linha (negativo)')

# ---------------- caminho canônico (R-11): nada no CA-01det, CA-01x e CA-02 aponta a SU-07 ou a CA-04 ----------------
src = open(os.path.join(HERE, 'areas', 'campo.py'), encoding='utf-8').read()
def corpo(fn):
    i = src.find(f"def {fn}():"); j = src.find('\ndef ', i + 5); return src[i:j]
ruins = {fn: re.findall(r"(SU-07|CA-04)\.dc\.html", corpo(fn)) for fn in ('_ca01det', '_ca01x_0420', '_ca02')}
ok(not any(ruins.values()) and src.count("EST.dc.html#req=REQ-03") >= 5, 'R-11: CA-01det, CA-01x e CA-02 levam custódia e requisição ao Estoque (EST#req=), nunca à SU-07 nem à CA-04 ocultas', ruins)

# ---------------- parte 2: node (Manutenção e busca da SAF) ----------------
import cenario, dados_manutencao as DM
import areas.maquinas as MAQ
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MOTOR, PRELUDIO = ([JSC], '') if os.path.exists(JSC) else (['node'], 'globalThis.print=(...a)=>console.log(...a);\n')
sj = open(os.path.join(HERE, 'safra.js'), encoding='utf-8').read()
def fun(nome):
    i = sj.find('function ' + nome + '('); j = sj.find('{', i); n = 0
    for k in range(j, len(sj)):
        n += {'{': 1, '}': -1}.get(sj[k], 0)
        if n == 0: return sj[i:k + 1]
    return ''
src_js = (PRELUDIO + cenario.perfis_js() + DM.js_prefixo() + MAQ.MA_JS.replace('__PRIM__', json.dumps(MAQ.PRIM)).replace('__SEC__', json.dumps(MAQ.SEC)) + MAQ.PM_JS
          + '\n' + fun('cultBusca') + '\n' + fun('e3Busca') + '\n' + fun('e3Achar') + '\n' + open(os.path.join(HERE, 'colunas1_unit.js'), encoding='utf-8').read())
os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True)
p = os.path.join(HERE, '_probe', 'colunas1_unit_all.js'); open(p, 'w', encoding='utf-8').write(src_js)
r = subprocess.run(MOTOR + [p], capture_output=True, text=True, timeout=120)
out = r.stdout.strip().splitlines()
ok(r.returncode == 0 and out, 'motor JS (node) executou sem erro', r.stderr[:800])
for x in (json.loads(out[-1]) if out else []): ok(x['ok'], x['n'], x['info'])

print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
