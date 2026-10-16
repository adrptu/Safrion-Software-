# -*- coding: utf-8 -*-
"""Execução da O.S. liberada — ficha do caldeiro e do operador no app (offline) e ficha impressa (PRD cap. 41.3–41.4).
Exemplo: OS-0424 · Fungicida A no T1-B (soja, 128 ha a 0,5 L/ha = 64 L), liberada; REQ-039 reserva 65 L do lote F26-02.
05/10 (G1 do CTL-1): saiu do milho do Pivô 2 (0,8 L/ha, sem registro do Fungicida A para milho) para a soja do T1-B, dentro da bula.
Conta das cargas (41.4): área da carga = volume final da carga ÷ vazão; produto da carga = dose × área da carga; a última carga é proporcional.
Retirada (v3.9, 26/09/2026): o estado vem da REQ-039 do cenário compartilhado (cenario.js) — Reservado → Entregue por Rui (Estoque) →
Recebido (cenConfirmarRecebimento, sem sinal vai para a fila do aparelho). Preparo do app e da impressão leem a mesma projeção da versão vigente.
"""
import json, math
from engine import (esc, INK, MUTED, LINE, BG, SURF, ACC, ACCS, YEL, YELS, RED, REDS, GRAYS, DISP, FONT, G2_CSS, G2_TOAST, EXTRAJS, _MINI, _MINIP)
import engine as E
import dados2 as D2
import cenario
from ui37 import HEIGHTS37

H = lambda s: '{{' + s + '}}'
F = lambda: H('false')
T = lambda: H('true')

# ---------- dados da ordem e do equipamento (versão v1 liberada) ----------
OS = dict(id='OS-0424', ativ='Fungicida', op='Pulverização', local='T1-B · Soja 62 X', area=128.0, versao='v1 liberada por Ana (agrônoma) em 23/09 17:40',
          janela='24/09 · 06:00–11:00', valida='24/09 18:00', resp='Marcos', req='REQ-039', almox='Rui')
CJ = next(c for c in D2.CONJ if c['id'] == 'r1')
EQ = dict(conj=CJ['conj'], vel=CJ['vel'], barra=CJ['larg'], bicos='leque 110-015 · 3 bar')
PRODS = [dict(p='Fungicida A', dose=0.5, un='L', lote='F26-02', val='03/2028', emb='galão 5 L', reserv=65)]


def nf(n, d=0):
    s = f'{n:,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    if d and s.endswith(',' + '0' * d): s = s[:-(d + 1)]
    return s


def _page(fname, title, W, Hh, body, bg=BG, movel=False):
    # movel: App de campo (pendência de componentes 03/10) · largura do aparelho (meta viewport) e raiz móvel do engine (MOBILE_CSS):
    # ocupa a janela, rola por dentro e respeita as áreas seguras; em 1280 px ou mais fica como a prancha de 390 px, igual à base
    vp = '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, interactive-widget=resizes-content">\n' if movel else ''
    html = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
{vp}<title>{esc(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&amp;family=Sora:wght@600;700&amp;display=swap">
<style>
body{{margin:0;font-family:{FONT};color:{INK};background:{bg}}}
a{{color:{ACC}}}
{G2_CSS}
{E.MOBILE_CSS if movel else ''}
@media print{{ .noprint{{display:none !important}} body{{background:#fff}} }}
</style>
</helmet>
{body}
{G2_TOAST}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{Hh}}}}}'>
{E.engine()}
</script>
</body>
</html>'''
    open(f'{E.P}/{fname}', 'w', encoding='utf-8').write(html)
    E._reset_screen(fname)
    return fname


# ---------- app de campo (390 px): retirada → preparo carga a carga → aplicação ----------
PREPARO_JS = 'const FICHA0424 = '+json.dumps(OS,ensure_ascii=False)+';\n'+r'''
function oscPreparo(c,v){ const o=c.ordens['OS-0424'], p=cenPreparoOrdem(c,o);
  v.preparo=cenPreparoTxt(p); v.preparoOk=p.ok&&p.n>0; v.preparoBloq=!v.preparoOk;
  v.versao=o?o.versao:'Ordem indisponível';
  v.validade=o&&CEN0.ordens[o.id]&&o.versao===CEN0.ordens[o.id].versao?FICHA0424.valida:'Conferir validade da nova instrução';
  v.totalArea=p.ok?cenNum(p.area,3)+' ha':'—'; v.totalVol=p.ok?cenNum(p.area*p.vazao,3)+' L':'—';
  v.totalProds=p.ok?o.ins.map(x=>x.p+' '+cenNum(x.dose*p.area,3)+' '+x.un).join(' · '):'—';
  v.vazao=p.ok?cenNum(p.vazao)+' L/ha':'Não informada';
  v.hacarga=p.ok?cenNum(p.haCarga,3)+' ha':'Não calculável';
  v.conjunto=p.ok?p.conjunto:p.motivo;
  v.doses=o?(o.ins||[]).map(x=>x.p+' '+cenNum(x.dose,3)+' '+x.un+'/ha').join(' · '):'';
  v.cargas=p.cargas.map(x=>({n:x.n,parcial:x.parcial,volt:cenNum(x.vol,3)+' L de calda',areat:cenNum(x.area,3)+' ha',
    prods:x.prods.map(y=>({p:y.p,q:cenNum(y.q,3)+' '+y.un})),produtos:x.prods.map(y=>y.p+' '+cenNum(y.q,3)+' '+y.un).join(' · ')}));
  v.saldoIns=o?cenInsumosOrdem(c,o).map(cenInsumoSaldoTxt).join(' · '):'';
  return p;
}
'''

APP_JS = PREPARO_JS + r'''
// Gancho de teste/inspeção (o script roda isolado em new Function): mesma API do cenário usada pelos testes app_*.
try { window.__cen = { cenGet, cenMudar, cenReset, cenLiberar, cenEntregar, cenConfirmarRecebimento, cenIniciarTurno, cenFecharTurno, cenOcorrencia, cenSinal, cenPodeEncerrar }; } catch (e) {}
function EXTRAVALS(self,v){ cenOuvir(self); const c=cenGet(); const st=self.state; const d=OSC; oscPreparo(c,v); const cargas=v.cargas; const N=cargas.length; const chave=JSON.stringify([v.versao,cargas]); const feitas=st.preparoChave===chave?Math.min(st.feitas||0,N):0;
  // retirada = REQ-039 do cenário: reservado → entregue pelo almoxarife → recebido no app (custódia do operador)
  const r=c.reqs[d.os.req]; const its=r?r.itens:[]; const pend=its.filter(i=>i.custodia>0&&!i.confirmado);
  const ret=its.length>0&&its.every(i=>(i.custodia>0&&i.confirmado)||i.consumido>0);
  const semSinal=(c.movs||[]).some(m=>m.tipo==='recebimento'&&m.req===d.os.req&&m.sinc===false);
  const fase=!ret?'ret':(feitas<N?'prep':'apl'); const cg=cargas[Math.min(feitas,N-1)]||{n:0,parcial:false,volt:'—',areat:'—',prods:[]};
  v.ret=ret; v.naoRet=!ret;
  v.ret_st=ret?'Recebido · '+its.map(i=>cenNum(i.custodia)+' '+i.un).join(' + ')+' com '+c.app.operador+(semSinal?' · aguardando sinal':' · conferido com '+d.os.almox)
    :(pend.length?'Entregue por '+d.os.almox+' · confirme o recebimento':'Reservado · retire com '+d.os.almox+' no almoxarifado');
  v.ret_cst='display:inline-flex;align-items:center;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;'+(ret?'color:#1E7A4C;background:#E4F3E9;':'color:#8A5A00;background:#FFF4D6;');
  v.cg_t='Carga '+cg.n+' de '+N+(cg.parcial?' · última, parcial':''); v.cg_par=cg.parcial; v.cg_vol=cg.volt; v.cg_area=cg.areat; v.cg_prods=cg.prods;
  v.cg_st='display:flex;flex-direction:column;gap:8px;padding:12px 14px;border-radius:14px;border:'+(cg.parcial?'2px solid #8A5A00;background:#FFFFFF':'1px solid transparent;background:#F4F6F3')+';';   // SEP-20261015 (d): a carga atual dentro do cartão leva fundo, não moldura
  v.prep=fase!=='ret'; v.feitas_t=feitas+' de '+N+' cargas preparadas'; v.bar_st='display:block;height:100%;border-radius:999px;background:#1E7A4C;width:'+(N?Math.round(100*feitas/N):0)+'%;';
  v.lista=cargas.map((x,i)=>({t:'Carga '+x.n+' · '+x.volt+' · '+x.areat,s:i<feitas?'✓':'',st:'font-size:12.5px;color:'+(i<feitas?'#1E7A4C':(i===feitas&&fase==='prep'?'#15201A':'#8A968E'))+';font-weight:'+(i===feitas&&fase==='prep'?'800':'600')+';'}));
  v.prim_t=fase==='ret'?(pend.length?'Confirmar recebimento':'Retirar no almoxarifado'):(fase==='prep'?('Carga '+cg.n+' preparada'):'Registrar apontamento');
  v.primDis=!v.preparoOk; if(v.primDis) v.prim_t='Conferir preparo na O.S.';
  v.prim=()=>{ if(v.primDis){self.setState({g2toast:v.preparo});return;} if(fase==='ret'){ if(pend.length){ cenMudar(self,c=>cenConfirmarRecebimento(c,d.os.req)); return; }
      self.setState({g2toast:'Nada entregue ainda: retire com '+d.os.almox+' no almoxarifado ('+d.os.req+' · '+d.retirada+'). Quando ele entregar, confirme o recebimento aqui.'}); return; }
    if(fase==='prep'){ self.setState({preparoChave:chave,feitas:feitas+1,g2toast:'Carga '+cg.n+' preparada ('+cg.volt+'). Marcada nesta tela; ainda não é aplicação.'}); return; }
    self.setState({g2toast:'Apontamento aberto para '+d.os.id+'. Calda preparada não é área aplicada: registre a área feita.'}); };
}'''


def app():
    fname = 'OS-0424-app.dc.html'
    d = dict(os=OS, retirada=', '.join(f"{x['p']} {nf(x['reserv'])} {x['un']} · lote {x['lote']}" for x in PRODS))
    EXTRAJS[0] = cenario.js_prefixo() + 'const OSC = ' + json.dumps(d, ensure_ascii=False) + ';\n' + APP_JS
    card = lambda t, inner, extra='': (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; padding: 12px 14px; display: flex; flex-direction: column; gap: 8px; {extra}">'
                                      f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; color: {MUTED};">{t}</div>{inner}</section>')
    kv = lambda l, v: f'<div style="display: flex; justify-content: space-between; gap: 10px; font-size: 13.5px;"><span style="color: {MUTED};">{l}</span><b style="text-align: right;">{v}</b></div>'
    ret = card('Retirada no almoxarifado', f'<div><span style="{H("ret_cst")}">{H("ret_st")}</span></div>'
               + ''.join(kv(x['p'], f"{nf(x['reserv'])} {x['un']} · {nf(math.ceil(x['reserv']/5))} × {x['emb']}") + kv('Lote · validade', f"{x['lote']} · {x['val']}") for x in PRODS)
               + kv('Requisição', OS['req']))
    prep = card('Caldeiro · preparo', f'<div role="status">{H("preparo")}</div><div>{H("saldoIns")}</div>' +
                f'<div style="{H("cg_st")}"><b style="font-size: 16px;">{H("cg_t")}</b>'
                f'<div style="display: flex; gap: 14px; font-size: 13px;"><span>Tanque: <b>{H("cg_vol")}</b></span><span>Área: <b>{H("cg_area")}</b></span></div>'
                f'<sc-for list="{H("cg_prods")}" as="p" hint-placeholder-count="1"><div style="display: flex; justify-content: space-between; font-size: 15px; padding: 6px 0;"><span>{H("p.p")}</span><b>{H("p.q")}</b></div></sc-for>'
                f'<div style="font-size: 12.5px; color: {MUTED};">Complete com água até o volume do tanque, na ordem da instrução liberada.</div></div>'
                f'<span style="display: block; height: 6px; border-radius: 999px; background: {GRAYS}; overflow: hidden;"><span style="{H("bar_st")}"></span></span>'
                f'<div style="font-size: 12px; color: {MUTED};">{H("feitas_t")}</div>'
                f'<sc-for list="{H("lista")}" as="l" hint-placeholder-count="3"><div style="display: flex; justify-content: space-between; {H("l.st")}"><span>{H("l.t")}</span><span>{H("l.s")}</span></div></sc-for>')
    opr = card('Operador · aplicação', kv('Vazão', H('vazao')) + kv('Velocidade', f"{nf(EQ['vel'])} km/h") + kv('Barra', f"{nf(EQ['barra'])} m")
               + kv('Bicos · pressão', EQ['bicos']) + kv('Área por carga', H('hacarga')) + kv('Dose', H('doses')))
    # SEP-20261015 (a): a barra de ação fixa no pé, branca sobre o fundo cinza, separa-se por sombra (como a faixa de etapas), sem linha
    body = (f'<div data-mroot="1" style="position: relative; width: 100%; height: 1030px; --mw: 390px; box-sizing: border-box; display: flex; flex-direction: column; background: {BG}; overflow: clip;">'
            f'<header style="padding: 44px 20px 12px; background: {SURF}; border-bottom: 1px solid {LINE}; display: flex; flex-direction: column; gap: 5px;">'
            f'<div style="display: flex; align-items: center; gap: 8px;"><a href="OS.dc.html" aria-label="Voltar para Ordem de Serviço" style="text-decoration: none; font-size: 20px; color: {INK};">‹</a>'
            f'<h1 style="margin: 0; font-family: {DISP}; font-size: 19px;">{OS["id"]} · {OS["ativ"]}</h1></div>'
            f'<div style="font-size: 13px; color: {MUTED};">{OS["local"]} · {nf(OS["area"])} ha · {OS["janela"]}</div>'
            f'<div role="status" style="display: inline-flex; align-self: flex-start; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 999px; background: {ACCS}; color: {ACC}; font-size: 12px; font-weight: 700;">● Disponível sem internet · {H("versao")}</div></header>'
            f'<main style="flex-grow: 1; min-height: 0; overflow-y: auto; padding: 14px 16px; display: flex; flex-direction: column; gap: 12px;">{ret}{prep}{opr}'
            f'<a href="OS-0424-ficha.dc.html" style="{_MINI} text-decoration: none; text-align: center;">Abrir ficha para imprimir</a></main>'
            f'<div style="padding: 12px 16px 26px; background: {SURF}; box-shadow: 0 -6px 12px -10px rgba(21,32,26,.25);"><button type="button" onClick="{H("prim")}" disabled="{H("primDis")}" style="display: block; width: 100%; padding: 17px; border: 0; border-radius: 16px; background: {ACC}; color: #fff; font-family: inherit; font-size: 16px; font-weight: 800; cursor: pointer;">{H("prim_t")}</button></div></div>')
    HEIGHTS37[fname] = 1030
    return _page(fname, "OS-0424 · ficha de campo", 390, 1030, body, movel=True)


# ---------- ficha impressa (A4): mesma versão, validade e QR ----------
def _qr():
    import hashlib
    h = hashlib.sha256(b'OS-0424-v1').digest(); cells = []
    for y in range(21):
        for x in range(21):
            fixed = (x < 7 and y < 7) or (x > 13 and y < 7) or (x < 7 and y > 13)
            if fixed:
                on = (x % 6 == 0 or y % 6 == 0 or (2 <= x % 14 <= 4 and 2 <= y % 14 <= 4)) if True else False
                xx, yy = x % 14 if x > 13 else x, y % 14 if y > 13 else y
                on = xx in (0, 6) or yy in (0, 6) or (2 <= xx <= 4 and 2 <= yy <= 4)
            else:
                on = (h[(x * 21 + y) % 32] >> ((x + y) % 8)) & 1
            if on: cells.append(f'<rect x="{x}" y="{y}" width="1" height="1"/>')
    return f'<svg viewBox="-1 -1 23 23" width="104" height="104" role="img" aria-label="QR da OS-0424 v1 (demonstração)"><rect x="-1" y="-1" width="23" height="23" fill="#fff"/><g fill="#15201A">{"".join(cells)}</g></svg>'


def ficha():
    fname = 'OS-0424-ficha.dc.html'; EXTRAJS[0] = cenario.js_prefixo() + PREPARO_JS + 'function EXTRAVALS(self,v){ cenOuvir(self); oscPreparo(cenGet(),v); v.imprimir=()=>{ if(!v.preparoOk){self.setState({g2toast:v.preparo});return;} try{ window.print(); }catch(e){} }; }'
    th = f'text-align: left; font-size: 10.5px; letter-spacing: .05em; text-transform: uppercase; color: {MUTED}; padding: 6px 8px; border-bottom: 1.5px solid {INK};'
    td = f'padding: 9px 8px; border-bottom: 1px solid {LINE}; font-size: 13.5px;'
    box = '<span style="display: inline-block; width: 16px; height: 16px; border: 1.5px solid #15201A; border-radius: 3px;"></span>'
    rowst='display:grid;grid-template-columns:44px 96px 78px minmax(0,1fr) 40px 50px;'
    rows = (f'<sc-for list="{H("cargas")}" as="c"><div role="row" style="{rowst}"><div role="cell" style="{td}">{H("c.n")}</div><div role="cell" style="{td}">{H("c.volt")}</div>'
            f'<div role="cell" style="{td}">{H("c.areat")}</div><div role="cell" style="{td}">{H("c.produtos")}</div><div role="cell" style="{td}">{box}</div><div role="cell" style="{td}"></div></div></sc-for>')
    headers=''.join(f'<div role="columnheader" style="{th}">{t}</div>' for t in ['Carga','Calda','Área','Produtos · dose: '+H('doses'),'Feito','Hora'])
    totals=''.join(f'<div role="cell" style="{td}">{t}</div>' for t in ['Total',H('totalVol'),H('totalArea'),H('totalProds'),'',''])
    kv = lambda l, v: f'<div><div style="font-size: 10.5px; letter-spacing: .05em; text-transform: uppercase; color: {MUTED};">{l}</div><div style="font-size: 15px; font-weight: 800;">{v}</div></div>'
    linha = lambda l: f'<div style="display: flex; gap: 8px; align-items: flex-end; font-size: 13px;"><span style="white-space: nowrap;">{l}</span><span style="flex-grow: 1; border-bottom: 1px solid #15201A; height: 18px;"></span></div>'
    sec = lambda t: f'<div style="font-size: 12px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; margin-top: 14px;">{t}</div>'
    body = (f'<div style="width: 794px; min-height: 1123px; box-sizing: border-box; padding: 36px 44px; background: #fff; display: flex; flex-direction: column; gap: 10px;">'
            f'<div class="noprint" style="display: flex; gap: 8px; justify-content: flex-end;"><a href="OS-0424-app.dc.html" style="{_MINI} text-decoration: none;">Voltar à ficha do app</a><button type="button" onClick="{H("imprimir")}" disabled="{H("preparoBloq")}" style="{_MINIP}">Imprimir</button></div>'
            f'<header class="g2-cab" style="display: flex; gap: 18px; align-items: flex-start;"><div style="flex-grow: 1;">'
            f'<div style="font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: {MUTED};">Ficha de preparo e aplicação · uso sem internet</div>'
            f'<h1 style="margin: 4px 0 2px; font-family: {DISP}; font-size: 24px;">{OS["id"]} · {OS["ativ"]} · {OS["local"]}</h1>'
            f'<div style="font-size: 13px;">{nf(OS["area"])} ha · janela {OS["janela"]} · responsável {OS["resp"]}</div>'
            f'<div style="font-size: 13px; margin-top: 4px;"><b>Versão:</b> {H("versao")} · <b>Válida até:</b> {H("validade")}</div></div>'
            f'<div style="text-align: center; font-size: 10.5px; color: {MUTED}; width: 120px;">{_qr()}<div>Confira a versão na O.S. antes de preparar</div></div></header>'
            + sec('Retirada no almoxarifado')
            + f'<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">' + ''.join(kv('Produto', x['p']) + kv('Quantidade', f"{nf(x['reserv'])} {x['un']} · {nf(math.ceil(x['reserv']/5))} × {x['emb']}") + kv('Lote · validade', f"{x['lote']} · {x['val']}") + kv('Requisição', OS['req']) for x in PRODS) + '</div>'
            + f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 4px;">{linha("Entregue por (almoxarife)")}{linha("Recebido por (caldeiro)")}</div>'
            + sec('Caldeiro · preparo por carga')
            + f'<div role="status" style="font-size: 12.5px;">{H("preparo")}</div><div>{H("saldoIns")}</div>'
            + f'<div role="table" aria-label="Cargas de preparo"><div role="row" style="{rowst}">{headers}</div><div role="rowgroup">{rows}</div><div role="row" style="{rowst}">{totals}</div></div>'
            + sec('Operador · aplicação')
            + f'<div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;">{kv("Vazão", H("vazao"))}{kv("Velocidade", nf(EQ["vel"])+" km/h")}{kv("Barra", nf(EQ["barra"])+" m")}{kv("Bicos · pressão", EQ["bicos"])}{kv("Conjunto", H("conjunto"))}</div>'
            + sec('Apontamento (lance no app quando houver sinal)')
            + f'<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px;">{linha("Data")}{linha("Início")}{linha("Fim")}{linha("Área feita (ha)")}{linha("Sobra (L)")}{linha("Ocorrência")}</div>'
            + f'<div style="margin-top: auto; padding-top: 14px; border-top: 1px solid {LINE}; font-size: 11px; color: {MUTED};">Ficha da versão exibida acima. Antes de preparar, confira a versão vigente na O.S.; se mudou, reemita a ficha. O QR desta demonstração não consulta versões. Calda preparada não é área aplicada.</div></div>')
    HEIGHTS37[fname] = 1123
    return _page(fname, 'OS-0424 · ficha impressa', 794, 1123, body, bg='#fff')


def build():
    app(); ficha()

