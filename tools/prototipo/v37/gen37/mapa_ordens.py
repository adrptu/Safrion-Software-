"""EX-55 F1 · ordens do mapa: fonte única do Mapa da fazenda (IN-04) e do mapa embutido da O.S. (os_mapa.js).
Movido sem mudança de conteúdo de areas/inicio.py (antes _ORD_MAPA, IRR_OS, _selo_cor e _ord_mapa). O IN-04 e a O.S. leem daqui;
as O.S. do cenário fora desta lista entram no navegador (os_mapa.js mcOrdsBase), com o prazo pela janela contra HOJE."""
import datetime as _dt
import json
import dados as D
import dados_lagoa_safra as DLS

HOJE=_dt.date(2026,9,23)   # o "hoje" da demonstração do Mapa (o mesmo de areas/inicio.py)


def nfb(v,d=0):
    s=f'{v:,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')
    return s


# ordens no mapa = dados.ORDENS (menos OB-0104, do armazém). Tipo, selo, janela, responsável e link de detalhe vêm do registro
# canônico; fase, realizado, saldo e custódia vêm do cenário compartilhado no navegador (cenGet), com o registro como semente.
# Aqui ficam só os campos do mapa: talhões da geometria, complemento do realizado, prazo e a próxima ação da ordem
# (rótulo, destino, tipo: 'lib' = liberação pelo agrônomo, com ajuste opcional (o primário é o "Liberar para execução" do núcleo
# da O.S.; o rótulo daqui é o ajuste) · 'op' = pendência operacional, que no painel só aparece com o próximo passo impedido;
# condição: 'ag' = só enquanto a ordem está a liberar pelo agrônomo no cenário, 'cust' = só com custódia).
ORD_MAPA=[  # id, talhões da geometria, complemento do realizado, prazo, ação
 ('OS-0421',['T1','T2'],'','no prazo',None),
 ('OS-0420',['T4'],'','atrasada',('Acompanhar OM-0233','MA.dc.html#om=OM-0233','op',None)),   # PL-05 é oculta e fixa (Frente F): a OM-0233 viva
 ('OS-0419',['P2'],'lâmina 10,81 mm','irrigando hoje',None),
 ('OS-0424',['T1'],'T1-B','até 3 dias',None),
 ('OS-0422',['P2'],'2 passadas de 6,75 mm','até 3 dias',('Definir janela','IR-03det.dc.html#OS-0422:janela','op',None)),
 ('OS-0418',['P1'],'Ureia 12 kg/ha','vence hoje',('Ajustar antes de liberar','OS.dc.html#OS-0418','lib','ag')),
 ('OS-0417',['P1'],'','até 3 dias',('Receber sobras','EST.dc.html','op','cust')),
 ('OS-0415',['T3'],'','encerrada',None),
 ('OS-0423',['T7'],'estimativa por ET','vence hoje',('Resolver conflito','IR-03det.dc.html#OS-0423:conflito','op',None)),
 ('OS-0425',['C1'],'','no prazo',None),
 ('OS-0430',['T1'],'T1-A','até 3 dias',('Ajustar antes de liberar','OS.dc.html#OS-0430','lib','ag')),
 ('OS-0431',['T2'],'','até 3 dias',None),
]
ORD_MAPA+=[tuple(x) for x in DLS.ORD_MAPA]   # Lagoa Grande: ordens nos pivôs (ids PVxx do mapa)
# irrigação só com água: sem agrônomo e sem "política" — o selo é a pendência operacional, com o dono dela (igual a IR-02/IR-03)
IRR_OS={'OS-0419':dict(tipo='Irrigação · água',selos=[]),
        'OS-0422':dict(tipo='Irrigação · água',selos=[['Janela a definir','yellow']],dono='João'),
        'OS-0423':dict(tipo='Irrigação · água por gotejo',selos=[['Conflito · parada da B3','red']],dono='Caio · PCP')}
def selo_cor(t):
    if t.startswith('Impedida') or t.startswith('Falta máquina') or t.startswith('Conflito'): return 'red'
    return 'yellow'
def ordens():
    out=[]
    for oid,tal,suf,pz,act in ORD_MAPA:
        o=D.ORDEM[oid]; ts=([o['selo']] if o['selo'] else [])+list(o.get('selos_extra') or [])
        real=f"{nfb(o.get('realizado') or 0)}/{nfb(o.get('area') or 0)} ha"+(f" · saldo {nfb(o['saldo'])} ha" if o.get('realizado') and o.get('saldo') else '')+(f' · {suf}' if suf else '')
        d=dict(id=oid,tal=tal,tipo=o['tipo'],fase=o['etapa'],selos=[[t,selo_cor(t)] for t in ts],area=o.get('area') or 0,rz=o.get('realizado') or 0,suf=suf,
               jan=o['janela'],real=real,saldo=o['saldo'] or 0,resp=o['resp'],pz=pz,h=o['detalhe'] or 'OS.dc.html',saf=o.get('saf') or '2026/27')
        if oid in IRR_OS: d.update(IRR_OS[oid])
        if act: d['act']=dict(t=act[0],h=act[1],k=act[2],c=act[3])
        out.append(d)
    assert {x['id'] for x in out}=={o['id'] for o in D.ORDENS+D.ORDENS_LG if o['id'].startswith('OS-')}, 'mapa fora do registro de ordens'
    assert not any('política' in json.dumps(x,ensure_ascii=False) for x in out), 'irrigação só com água não usa política/agrônomo'
    assert not any((x.get('act') or {}).get('k')=='dec' for x in out), "O.S. sem revisão: a ação do agrônomo no mapa é 'lib' (liberar)"
    assert not any(s in json.dumps(out) for s in ('IN-02det','IN-02x-os0420')), 'telas de decisão de O.S. não são mais geradas: use OS.dc.html#OS-xxxx'
    return out
