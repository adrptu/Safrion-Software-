# Frente F (CTL-1) · links_ocultos_test.py: testes estruturais sem navegador: (a) só a O.S. e o Mapa liberam ordem agrícola (logo, todo caminho grava CMD-42/CMD-06);
# (b) nenhum elo de tela visível para tela oculta e fixa no escopo; o resto da varredura fica numa lista por PAR (origem → destino) com motivo.
import sys, os, re, json, glob
G=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,G); os.chdir(G)   # rode depois de build.py + montar_render.py (lê project/)
OK=[]; FA=[]
def ok(n,c,i=''): (OK if c else FA).append(n); print(('OK   ' if c else 'FALHA'),n,('' if c else '· '+str(i)[:500]))
import areas.processo_os as P, cenario
# (a) código de produto = .py e .js do gerador, sem testes, sondas, reproduções e saídas
# parte de navegador de um teste (X_nav.py ao lado do X_test.py que a chama: ap_unico, cafe_apurar, dose_divergente) também é teste
# (integração COMP, 10/10: o dose_divergente_nav.py da DOM monta o cenário com osc_liberar e caía no E1); um X_nav.py sem o X_test.py segue lido
def _nav_de_teste(f): return f.endswith('_nav.py') and os.path.exists(f[:-len('_nav.py')]+'_test.py')
fontes=[f for f in glob.glob('*.py')+glob.glob('*.js')+glob.glob('areas/*.py')
        if not re.search(r'test|_unit|unit_|repro|probe|verif|qa37|_lib\.py$',os.path.basename(f)) and not _nav_de_teste(f)]
src={f:open(f,encoding='utf-8').read() for f in fontes}
cham=sorted(f for f,s in src.items() if re.search(r'\bosc_liberar\(',s))
ok('E1 em todo o código de produto, só a O.S. e o Mapa chamam osc_liberar', cham==['areas/inicio.py','areas/processo_os.py'], cham)
cl=sorted(f for f,s in src.items() if re.search(r'\bcenLiberar\(c',s) and not f.endswith('cenario.js'))
ok('E1b só osc_liberar (processo_os) e a liberação da ordem de beneficiamento (ben.js, BEN-D05) chamam cenLiberar: nenhum atalho libera sem gravar CMD-42/CMD-06', cl==['areas/processo_os.py','ben.js'], cl)
# BEN-D05 (integração BEN, 09/10): a OB (fam 'BEN', responsável próprio: Igor) reaproveita cenLiberar. Em ben.js a única função que chama
# cenLiberar é benAutorizarLiberar, que exige o perfil de produção, recusa ordem que não é de beneficiamento (benO) e grava CMD-42 e CMD-06.
# rodada 1 da integração (S4): o E1d antigo dividia o arquivo em "\nfunction " e procurava "cenLiberar(c": um atalho logo depois de
# benAutorizarLiberar (const x = (c, id) => cenLiberar(c, id)) ficava no mesmo pedaço, e uma chamada com outra variável escapava. Agora,
# sem comentários, o nome cenLiberar aparece exatamente uma vez em ben.js, como cenLiberar(c, id), dentro do corpo (chaves casadas) de
# benAutorizarLiberar; e nenhuma outra fonte do Beneficiamento o cita
def _sem_coment(t): return re.sub(r'^[ \t]*//[^\n]*', '', re.sub(r'/\*.*?\*/', '', t, flags=re.S), flags=re.M)
def _corpo(t, nome):
    i = t.find('function ' + nome + '('); j = t.find('{', i) if i >= 0 else -1
    if j < 0: return (-1, -1)
    n = 0
    for k in range(j, len(t)):
        n += {'{': 1, '}': -1}.get(t[k], 0)
        if n == 0: return (j, k)
    return (-1, -1)
def e1d(texto):
    t = _sem_coment(texto); usos = [m.start() for m in re.finditer(r'\bcenLiberar\b', t)]; a, b = _corpo(t, 'benAutorizarLiberar'); f = t[a:b + 1] if a >= 0 else ''
    return (len(usos) == 1 and a < usos[0] < b and t[usos[0]:usos[0] + len('cenLiberar(c, id)')] == 'cenLiberar(c, id)'
            and all(x in f for x in ("cenExige(ator, 'producao'", 'benO(c, id)', "benHist(o, quem, 'Versão ' + o.versao + ' da ordem autorizada (CMD-42)'", "benHist(o, quem, 'Liberada (CMD-06)'")), usos)
_ok, _usos = e1d(src.get('ben.js', ''))
def _sem_coment_py(t): return _sem_coment(re.sub(r'^[ \t]*#[^\n]*', '', re.sub(r'\"\"\".*?\"\"\"', '', t, flags=re.S), flags=re.M))   # docstrings e # fora; o JS da tela (r''') fica
_outros = [f for f in ('areas/processo_beneficiamento.py', 'dados_ben.py') if re.search(r'\bcenLiberar\b', _sem_coment_py(src.get(f, '')))]
ok('E1d em ben.js o nome cenLiberar aparece uma vez só, como cenLiberar(c, id) dentro de benAutorizarLiberar (perfil de produção, benO, CMD-42 e CMD-06); a tela e a semente do BEN não o citam',
   _ok and not _outros, [_usos, _outros])
_b = src.get('ben.js', ''); _m = _b.find('\nfunction benIniciar(')
_mut = [('atalho logo depois de benAutorizarLiberar', _b[:_m] + '\nconst benLibDireto = (c, id) => cenLiberar(c, id);' + _b[_m:]),
        ('chamada com outra variável', _b.replace("o.etapa = 'Em execução'; const T = benCxTot(c, o);", "o.etapa = 'Em execução'; cenLiberar(x, id); const T = benCxTot(c, o);", 1)),
        ('apelido do nome', _b[:_m] + '\nconst benL = cenLiberar;' + _b[_m:])]
ok('E1e o E1d derruba os atalhos de cenLiberar entre funções do ben.js (3 mutantes: atalho colado, outra variável, apelido)',
   _m > 0 and all(not e1d(t)[0] for _, t in _mut) and all(t != _b for _, t in _mut), [(n, e1d(t)[1]) for n, t in _mut])
ef=[(f,len(re.findall(r'\bosc_libEfeito\(',s))) for f,s in src.items() if re.search(r'\bosc_libEfeito\(',s)]   # CTL-3: definição + 2 chamadas
ok('E1c o efeito sem o registro de quem decide (osc_libEfeito) só é chamado por osc_liberar e pela prévia osLibErro (cópia)', ef==[('areas/processo_os.py',3)], ef)
# rodada 1 da integração (S4): o caminho escrito nas mensagens é o do menu (BEN-D14: Produção › Recebimento e beneficiamento); "Produção ›
# Cargas e recebimento" não existe mais no menu. Só o texto que a pessoa lê conta (comentários e docstrings ficam de fora)
_vel = sorted(f for f, t in src.items() if 'Produção › Cargas e recebimento' in (_sem_coment_py(t) if f.endswith('.py') else _sem_coment(t)))
ok('E4 nenhuma mensagem de produto aponta "Produção › Cargas e recebimento" (o menu diz "Produção › Recebimento e beneficiamento")', not _vel, _vel)
seed=cenario.seed()['ordens']
# BEN-D05: a OB em A liberar da semente (OB-0112) é de beneficiamento (fam 'BEN') e fica fora da lista da O.S.: libera pelo Beneficiamento, nunca por osc_liberar
_os_ids={o['id'] for o in P._ordens()}
_e2=[k for k,o in seed.items() if o['etapa']=='A liberar' and (k.startswith('OM-') or (k.startswith('OB-') and (o.get('fam')!='BEN' or k in _os_ids)))]
ok('E2 nenhuma ordem de manutenção em A liberar no cenário; a de beneficiamento em A liberar só com fam BEN e fora da lista da O.S. (OB-0104 Encerradas)', not _e2, _e2)
ops={a['op'] for p in P._nova_ordem_dados()['planos'].values() for a in p['atv']}
ok('E3 "Nova ordem" só emite atividade agrícola do plano', not [o for o in ops if re.search('Benef|Manut|Oficina',o)], sorted(ops))
# (b) elos
PJ=os.path.join(G,'project'); c=json.load(open(os.path.join(PJ,'canvas.json')))
pag={k:v.get('page') for k,v in c['boards'].items()}
# navegação sem submenus (13/10/2026, proprietário): cada módulo com mais de uma tela abre a sua tela de entrada (ui37.HUB37 e a tela
# Cadastros), que leva às telas do módulo (ui37.VOLTA37: cada uma volta por "‹ Módulo"); "Outros acessos" (ui37.OUTROS37, MOD-OUT) leva ao
# app de campo, portal, onboarding e backoffice. Essas telas são alcançáveis, ainda que o canvas deixe CD-01..CD-08, PT-01, ON-01 e BO-02
# na página "ocultos" e o MOD-OUT fora dele; o Main (página técnica mínima, que ui37.oculto exclui) também é origem. Só o resto da página
# "ocultos" segue oculto. O L0 confere no HTML que cada caminho declarado existe (entrada na barra lateral, cartão na entrada, "‹ Módulo"
# de volta): a noção de visível não cresce sem caminho real, e as telas que essas pontas abrem por dentro continuam ocultas (lista residual)
import ui37
ENTRADAS=set(ui37.HUB37.values())|{h for _,h in ui37.VOLTA37.values()}|{ui37.OUTROS37[2]}
ABERTAS=set(ui37.VOLTA37)|{h for _,h,_ in ui37.OUTROS37[3]}
VISIVEIS={k for k,v in pag.items() if v=='menu'}|ENTRADAS|ABERTAS|{'Main.dc.html'}
oc={k for k,v in pag.items() if v=='ocultos'}-VISIVEIS
_rd=lambda f: open(os.path.join(PJ,f),encoding='utf-8').read()
_l0=[('arquivo ausente',f) for f in sorted(VISIVEIS) if not os.path.exists(os.path.join(PJ,f))]
if not _l0:
    _ini=_rd(ui37.INICIO37)
    _l0+=[('sem a entrada na barra lateral',h) for h in sorted(ENTRADAS) if not re.search(r'<a href="'+re.escape(h)+r'" title=',_ini)]
    _l0+=[('sem cartão em '+hub,f) for f,(_,hub) in sorted(ui37.VOLTA37.items()) if not re.search(r'class="mod-cartao" role="listitem" href="'+re.escape(f)+r'(#[^"]*)?"',_rd(hub))]
    _l0+=[('sem "‹ '+rot+'" de volta',f) for f,(rot,hub) in sorted(ui37.VOLTA37.items()) if f'<a href="{hub}" class="volta37" aria-label="Voltar para {rot}"' not in _rd(f)]
    _l0+=[('sem cartão em '+ui37.OUTROS37[2],h) for _,h,_ in ui37.OUTROS37[3] if not re.search(r'class="mod-cartao" role="listitem" href="'+re.escape(h)+r'"',_rd(ui37.OUTROS37[2]))]
ok(f'L0 navegação nova: {len(ENTRADAS)} telas de entrada na barra lateral, {len(ui37.VOLTA37)} telas com cartão na entrada e "‹ Módulo" de volta, '
   f'{len(ui37.OUTROS37[3])} em Outros acessos; {len(oc)} telas seguem ocultas', not _l0 and len(oc)>0, _l0)
pares=set()
# v55 (revisão Codex): o padrão XX-… não via destino sem hífen (BEN.dc.html, CARGA.dc.html): a extração pega todo destino *.dc.html. O ben.js
# (biblioteca de regras, o mesmo texto em toda página do estado, oculta ou não) sai do texto antes: nele BEN.dc.html é o dado que
# benProxEntrada devolve, e as telas visíveis o descartam com o BEN fora da navegação (areas/producao.py prBenProx · PR_BEN_H; L4 e a
# varredura de DOM provam que nenhum <a>/onclick o mostra)
_BENJS=open('ben.js',encoding='utf-8').read()
for f in sorted(VISIVEIS):
    t=open(os.path.join(PJ,f),encoding='utf-8').read().replace(_BENJS,'')
    ds=re.findall(r'([A-Z]{2}-[0-9A-Za-z\-]+\.dc\.html(?:#[^"\'\s<]*)?)',t)+re.findall(r'([A-Za-z0-9][A-Za-z0-9\-]*\.dc\.html(?:#[^"\'\s<]*)?)',t)   # o padrão antigo e o amplo
    for h in {m.split('#')[0] for m in ds} & oc: pares.add((f,h))
p=lambda o,*ds: {(o+'.dc.html',d+'.dc.html') for d in ds}
# PCM simplificado (05/10, S1): MA-01..MA-05 e MA-04det viram a tela única MA (os endereços antigos só redirecionam); S4: MB-09 deixa de ser oculto
ESCOPO=(p('IN-04','PL-05','CA-02','CO-06det')|p('OS','CA-02','CO-06det')|p('MA','PL-04','PL-05','PL-05det')
        |p('IR-04','GE-07')|p('MB-01','MB-07','MB-08','MB-10')|p('MB-02','MB-08')|p('MB-05','MB-05det','SU-03det'))
ok('L1 nenhum elo do escopo (PL-04/PL-05/PL-05det, CA-02, CO-06det, GE-07, MB-05det, MB-07..MB-10, SU-03det a partir de telas visíveis)', not (pares & ESCOPO), sorted(pares & ESCOPO))
# 13/10: o índice saiu do Main (só leva ao Mapa), e os pares dele saíram da lista; as pontas de "Outros acessos" levam às próprias telas internas
RESIDUAL={  # por PAR: um elo novo, mesmo numa tela já listada, quebra o teste; um par que não existe mais também (L2b)
 **{x:'navegação interna da ponta aberta por Outros acessos (portal do parceiro, onboarding, backoffice): telas dela, fora do menu da organização'
    for x in p('PT-01','PT-02det','PT-03','PT-04','PT-05','PT-05det','PT-07')|p('ON-01','ON-01det')|p('BO-02','BO-01')},
 **{x:'vivo (cenário ou MIP), só falta pôr na página visível (build.py VIS_ROWS)' for x in p('MB-01','MB-02det','MB-03x-recibo','MB-06')|p('MB-02','MB-02det','MB-03x-recibo')
    |p('MB-09','MB-03x-recibo')|p('MB-09det','MB-03x-recibo')
    |p('MB-03','MB-02det','MB-03x-recibo')|p('MB-04','MB-03x-recibo')|p('MB-05','MB-03x-recibo')|p('AG-01','MB-06')|p('AG-01det','MB-06')|p('IN-04','MB-06','CO-06')
    |p('PROD','CO-06')|p('MB-07','MB-03x-recibo')|p('MB-10','MB-03x-recibo')},   # colheita (06/10): a avaliação de carência e destino do lote vive na CO-06; MB-07 e MB-10 (no estado) levam aos envios do aparelho como as outras telas do app
 ('MB-01.dc.html','IN-01.dc.html'):'"voltar" do app',
 **{x:'cadeia MIP → diagnóstico e recomendação (frente própria)' for x in p('AG-01','AG-03','AG-03det','AG-04det')|p('AG-02','AG-03det')|p('AG-01det','AG-03det','AG-04det','AG-06','PL-02')|p('AG-07','AG-04det')|p('IN-04','AG-06')},
 **{x:'detalhe fixo na página visível (frente própria)' for x in p('CA-01det','AG-04','CA-02','CA-04','PL-05','SU-07')|p('CA-01x-os0420','AG-04det','CA-02','CA-03det','PL-05','SU-07')}}
fora=sorted(pares-set(RESIDUAL))
ok('L2 todo o resto da varredura está na lista residual, por par e com motivo', not fora, fora)
velhos=sorted(set(RESIDUAL)-pares)
ok('L2b a lista residual só tem pares que a varredura ainda acha (par que sumiu sai da lista, para não liberar de antemão um elo futuro)', not velhos, velhos)
# v55 (10/10): o Beneficiamento sai da navegação até a rodada 3 (defeitos S2 de saldo e reserva de caixas em correção em outra frente;
# BEN_PUBLICADO=False em ui37.py). A tela fica no canvas, na página "ocultos", com motivo. BEN.dc.html não casa com o padrão XX-… acima: a
# conta é própria. O ben.js entra igual em toda página do estado (regras; o endereço que benProxEntrada devolve as telas descartam): o texto
# dele sai antes da busca, e qualquer outra menção a BEN.dc.html numa tela visível (link, ação, faixa, título) quebra o teste
OCULTOS_MOTIVO={'BEN.dc.html':'rodada 3 do BEN; reativar com BEN_PUBLICADO'}
if not ui37.BEN_PUBLICADO:
    _bj=_BENJS
    for h,mot in OCULTOS_MOTIVO.items():
        ok(f'L4a {h} oculto ({mot}): fora do menu (ui37.oculto), fora das telas de entrada e no canvas na página "ocultos"', ui37.oculto(h) and pag.get(h)=='ocultos' and h in oc, [ui37.oculto(h), pag.get(h), h in oc])
        _el=sorted(f for f in VISIVEIS if h in open(os.path.join(PJ,f),encoding='utf-8').read().replace(_bj,''))
        ok(f'L4b nenhuma tela visível aponta para {h} ({mot}) fora do ben.js embutido', not _el, _el)
    _cg=open(os.path.join(PJ,'CARGA.dc.html'),encoding='utf-8').read()
    ok('L4c Cargas e recebimento é tela única: sem a faixa "Telas de recebimento e beneficiamento" (seletor de uma opção só)',
       'Telas de recebimento e beneficiamento' not in _cg and 'class="etp ' not in _cg, [_cg.count('Telas de recebimento'), _cg.count('class="etp ')])
else: ok('L4 BEN publicado (ui37.BEN_PUBLICADO=True): fora da conta de ocultos', True)
import areas.inicio as I, dados_manutencao as DM
a420=[a for a in I._ORD_MAPA if a[0]=='OS-0420'][0][4]
ok('L3 Mapa · OS-0420: o passo vai para a OM-0233 viva (tela MA, visível e com âncora no registro: MA#om=), não para PL-05',
   a420 and a420[1]=='MA.dc.html#om=OM-0233' and 'OM-0233' in DM.seed()['oms'] and pag.get('MA.dc.html')=='menu', a420)
print('TOTAL',len(OK)+len(FA),'· falhas',len(FA)); sys.exit(1 if FA else 0)
