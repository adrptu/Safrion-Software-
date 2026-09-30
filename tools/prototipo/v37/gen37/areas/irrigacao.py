# -*- coding: utf-8 -*-
"""Irrigação (módulo OCULTO do menu, preservado) — processo sequencial em 4 telas ligadas pela faixa de etapas:
IR-01 Confira o balanço hídrico › IR-02 Programe a irrigação › IR-03 Execute as ordens (+ IR-03det, OS-0419) › IR-04 Acompanhe clima e sensores.

Regra v3.9 (decisão do proprietário, 26/09): água só-água NÃO passa pelo agrônomo. O sistema programa a lâmina que a cultura
precisa (balanço hídrico) e libera pela prontidão operacional (janela, bomba, energia, sem conflito), sem requisição/custódia.
Acima do limite por passada do equipamento, a lâmina é dividida em passadas; sonda sem dado usa estimativa por ET (não bloqueia).
Adicionar produtos reclassifica a MESMA ordem (nova versão, fertirrigação) e só essa versão vai à aprovação do agrônomo.
Água aplicada parcialmente só é creditada na área coberta. IDs de requisito ficam fora da interface.

observacoes (dados locais coerentes com dados.py / dados2.py / processo_os.py):
- HOJE = 23/09/2026 (dados.HOJE). Balanço de 7 dias = 16/09..22/09 (dias fechados); déficit inicial em 15/09.
- Pivô 2: 17/09 OS-0388 8.640 m³ (10,8 mm) · 19/09 OS-0391 6.400 m³ (8,0 mm) · 22/09 OS-0394 1.206 m³ = 10,4 mm em 11,6 ha
  (1,5 mm equivalentes em 80 ha) → 5,0 + 38,5 − 12,0 − 20,3 = 11,2 mm. Pivô 1: 5,0 + 33,6 − 12,0 − 18,2 = 8,4 mm.
  Gotejo T7: 3,1 + 29,4 − 10,5 − 12,0 ≈ 10,0 mm (sonda sem dado desde 20/09 06:00 → 21 e 22/09 estimados).
- OS-0419 (dados.OS): 1 volta a 62 % = 10,81 mm × 80 ha ÷ 166 L/s ≈ 14,5 h → janela hoje 20:00–amanhã 10:31, início 20:02, término
  previsto amanhã 10:33; andamento de 2,1 h ≈ 14,47 % da volta (11,6 ha). Recibos AU-3098 · LIB-2287 · EX-5120.
  Conferência automática: hidrômetro 8.480 m³ = 10,6 mm em 80 ha × 10,81 mm estimados (−1,9 %, tolerância 3 %).
- OS-0418 (fertirrigação v2): 8,1 mm × 95 ha ÷ 150 L/s ≈ 14,3 h → janela 24/09 21:00–25/09 11:15 (fora de ponta). OS-0422: 13,5 mm × 80 ha ≈ 18,1 h.
- OS-0422 (próximo ciclo, 13,5 mm = 2 passadas de 6,75 mm, janela a definir) e OS-0423 (gotejo T7, estimativa por ET, conflito com a
  parada da B3) = as mesmas de processo_os.py. Liberações LIB-2291/LIB-2292; novas ordens a partir de OS-0440 (OS-0425 é a adubação do café C1).
- Reclassificação da OS-0419: Ureia 45 % (mesmo produto da REQ-038/OS-0418, dados2) 12 kg/ha × 80 ha = 960 kg, versão v2 da MESMA ordem.
- Vazões: Pivô 2 166 L/s (6,7 mm × 80 ha em 9 h), Pivô 1 150 L/s, Gotejo T7 233 L/s (4,0 mm × 42 ha em 2 h).
"""
import json
from engine import (grid,section,esc,icon,chip,btn,msgbtn,Pt,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,DISP,
                    BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, steps_bar, continuity, HEIGHTS37, PARENT37
import dados as D

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
P=D.PIVO; POL=D.POLITICA_AGUA
def _n(v,d=None):
    if d is not None: v=f'{v:.{d}f}'
    return str(v).replace('.',',')

# ---------------- faixa de etapas (links) ----------------
ETAPAS=[('Confira o balanço hídrico','IR-01.dc.html'),('Programe a irrigação','IR-02.dc.html'),
        ('Execute as ordens','IR-03.dc.html'),('Acompanhe clima e sensores','IR-04.dc.html')]
WHY={2:'1 conflito · 1 janela a definir',4:'Sonda T7 sem dado há 3 d'}
def faixa(cur): return steps_bar([dict(t=t,href=h,why=WHY.get(i,'')) for i,(t,h) in enumerate(ETAPAS,1)],current=cur)
def navpe(cur):
    a=f'<a href="{ETAPAS[cur-2][1]}" style="{_MINI} font-size: 13px; padding: 8px 12px; text-decoration: none;">‹ {ETAPAS[cur-2][0]}</a>' if cur>1 else ''
    b=f'<a href="{ETAPAS[cur][1]}" style="{_MINI} font-size: 13px; padding: 8px 12px; text-decoration: none;">{ETAPAS[cur][0]} ›</a>' if cur<len(ETAPAS) else ''
    return f'<div style="display: flex; align-items: center; gap: 10px;">{a}<span style="flex-grow: 1;"></span>{b}</div>'

# ---------------- ações secundárias com ícone + rótulo + title ----------------
_SV={'play':'M8 5v14l11-7z','pause':'M7 5h3v14H7zM14 5h3v14h-3z','plus':'M12 5v14M5 12h14','refresh':'M21 12a9 9 0 1 1-2.6-6.4M21 4v5h-5',
     'upload':'M12 16V4M7 9l5-5 5 5M4 16v4h16v-4','flag':'M5 21V4h11l-2 4 2 4H5','phone':'M7 2h10v20H7zM11 18h2','gauge':'M12 14l4-5M3 14a9 9 0 1 1 18 0'}
def ic(name,size=15):
    if name in _SV: return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" '
                            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{_SV[name]}"/></svg>')
    return icon(name,size)
_IST='display: inline-flex; align-items: center; gap: 6px; text-decoration: none; '
def imsg(text,message,ico,title):
    """botão secundário que executa e mostra o resultado (aviso), com ícone e title."""
    b=msgbtn(text,message)
    return (b.replace('<button type="button"',f'<button type="button" title="{esc(title)}"',1)
             .replace('style="',f'style="{_IST}',1).replace(f'>{esc(text)}</button>',f'>{ic(ico)}{esc(text)}</button>',1))
def ilink(text,href,ico,title):
    return f'<a href="{href}" title="{esc(title)}" style="{_IST}{BTN_ST(False,True)}">{ic(ico)}{esc(text)}</a>'
def ifn(text_hole,fn,ico,title,st=None):
    return f'<button type="button" onClick="{H(fn)}" title="{esc(title)}" style="{_IST}{st or BTN_ST(False,True)}">{ic(ico)}{text_hole}</button>'
def txt(html): return f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.65;">{html}</div>'
B=lambda t: f'<b style="color: {INK};">{t}</b>'

def R(id,ro=False,o=None,**cells):
    """linha G2: str/num → v; lista de partes → p (+ s para busca); tupla (valor, partes) → v e p."""
    v={}; s={}; p={}
    for k,c in cells.items():
        if isinstance(c,tuple): v[k]=c[0]; p[k]=c[1]; s[k]=' '.join(x.get('t','') for x in c[1] if x.get('k')!='br')
        elif isinstance(c,list): p[k]=c; s[k]=' '.join(x.get('t','') for x in c if x.get('k')!='br')
        else: v[k]=c
    d=dict(id=id,v=v,s=s,p=p)
    if ro: d['ro']=True
    if o: d['o']=[dict(t=t) if isinstance(t,str) else t for t in o]
    return d

# painel lateral genérico (processo): título, subtítulo, corpo, rodapé
def painel(pre,corpo,rodape,w=480):
    return (f'<sc-if value="{H(pre+"_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
            f'<button type="button" aria-label="Fechar" onClick="{H(pre+"_cancel")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
            f'<aside role="dialog" aria-label="{H(pre+"_titulo")}" style="position: relative; width: {w}px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
            f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1;">{H(pre+"_titulo")}</h2>'
            f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H(pre+"_cancel")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED};">×</button></div>'
            f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H(pre+"_sub")}</div>{corpo}<div style="flex-grow: 1;"></div>'
            f'<sc-if value="{H(pre+"_warn")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.'
            f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H(pre+"_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H(pre+"_keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
            f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};">{rodape}</div></aside></div></sc-if>')
def campo(lbl,fid,inner,err_pre):
    return (f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="{fid}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{lbl}</label>{inner}'
            f'<sc-if value="{H(err_pre+"_has")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H(err_pre)}</span></sc-if></div>')
INP='font-family: inherit; font-size: 14px; padding: 9px 11px; border-radius: 10px; box-sizing: border-box; width: 100%; border: 1px solid '+LINE+'; background: #fff; color: '+INK+';'

JS_COMUM=r'''
function IRG(id){ return GRIDS.find(g=>g.id===id); }
function nfx(n,d){ return Number(n).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function chipSt(c){ const cc=G2C[c]||G2C.gray; return 'display:inline-flex;align-items:center;gap:6px;padding:4px 11px;border-radius:999px;font-size:12.5px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';'; }
const PRIM='display:inline-flex;align-items:center;gap:6px;padding:11px 20px;border-radius:10px;font-size:14px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap;text-decoration:none;background:#1E7A4C;color:#fff;border:1px solid #1E7A4C;';
const PRIMOFF='display:inline-flex;align-items:center;gap:6px;padding:11px 20px;border-radius:10px;font-size:14px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap;background:#EEF1EE;color:#5B6660;border:1px solid #E4E9E5;';
'''

# =====================================================================================
def ir01():
    fname='IR-01.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    DIAS=['16/09','17/09','18/09','19/09','20/09','21/09','22/09']
    BAL=[
     dict(id='P2',setor='Pivô 2',sub='Milho V10 · 80 ha',fontes='estação + sonda · hoje 06:00',est=False,d0=5.0,etc=38.5,pef=12.0,apl=20.3,
          nota='3 eventos · 1 parcial',dfin=11.2,lam='9,7 / 10,81 mm',tar=('OS-0419','IR-03det.dc.html'),lb=10.81,
          ev=['17/09 · volta completa OS-0388 · 8.640 m³ medidos = 10,8 mm em 80 ha','19/09 · volta completa OS-0391 · 6.400 m³ medidos = 8,0 mm em 80 ha',
              '22/09 · passagem parcial OS-0394 · 10,4 mm medidos em 11,6 ha (1.206 m³) = 1,5 mm equivalentes em 80 ha'],
          serie=[10.5,5.2,10.7,8.2,1.7,7.2,11.2],etcd=5.5),
     dict(id='P1',setor='Pivô 1',sub='Feijão R5 · 95 ha',fontes='estação + sonda · hoje 06:00',est=False,d0=5.0,etc=33.6,pef=12.0,apl=18.2,
          nota='2 voltas completas',dfin=8.4,lam='7,3 / 8,1 mm',tar=('OS-0418','IR-03.dc.html'),lb=8.1,
          ev=['17/09 · volta completa OS-0387 · 9.595 m³ medidos = 10,1 mm em 95 ha','21/09 · volta completa OS-0393 · 7.695 m³ medidos = 8,1 mm em 95 ha'],
          serie=[9.8,4.5,9.3,14.1,6.9,3.6,8.4],etcd=4.8),
     dict(id='T7',setor='Gotejo T7',sub='Mamão · 42 ha',fontes='sem sonda desde 20/09',est=True,d0=3.1,etc=29.4,pef=10.5,apl=12.0,
          nota='3 eventos até 19/09',dfin=10.0,lam='—',tar=('OS-0423','IR-03.dc.html'),lb=4.0,
          ev=['16/09 · OS-0389 · 1.680 m³ medidos = 4,0 mm em 42 ha','18/09 · OS-0390 · 1.680 m³ medidos = 4,0 mm em 42 ha',
              '19/09 · OS-0392 · 1.680 m³ medidos = 4,0 mm em 42 ha · encerrada automaticamente (sonda ativa)'],
          serie=[3.3,7.5,7.7,7.9,1.6,5.8,10.0],etcd=4.2),
    ]
    num=lambda k,l,**kw: dict(k=k,l=l,t='num',a='r',u='mm',d=1,**kw)
    rows=[]
    for b in BAL:
        memo=f'{_n(b["d0"],1)} + {_n(b["etc"],1)} − {_n(b["pef"],1)} − {_n(b["apl"],1)} = {("≈" if b["est"] else "")}{_n(b["dfin"],1)} mm'
        rows.append(R(b['id'],
          o=[f'Memória: déficit em 15/09 + ETc − chuva efetiva − aplicado equivalente = {memo}',
             'ETc = ET₀ Penman-Monteith (estação Santa Rita) × Kc do estádio · chuva efetiva = 60 % da chuva de 20/09']
            +[f'Aplicado · {e}' for e in b['ev']]+([dict(t='Ver fontes e sensores',h='IR-04.dc.html')] if b['est'] else []),
          setor=[Pt.b(b['setor']),Pt.mut(b['sub']),Pt.br()]+([Pt.chip('Estimativa · '+b['fontes'].lower(),'yellow')] if b['est'] else [Pt.mut(b['fontes'])]),
          d0=b['d0'],etc=b['etc'],pef=b['pef'],apl=(b['apl'],[Pt.txt(_n(b['apl'],1)+' mm'),Pt.br(),Pt.mut(b['nota'])]),
          dfin=(b['dfin'],[Pt.b(('≈' if b['est'] else '')+_n(b['dfin'],1)+' mm'),Pt.br(),Pt.mut(('líq./bruta '+b['lam']) if b['lam']!='—' else 'sem lâmina')]),
          lam=b['lam'],enq=[Pt.chip('—','gray')],tar=b['tar'][0]))
        rows[-1]['v']['sid']=b['id']
        rows[-1]['v']['href']=b['tar'][1]
    g_bal=grid([dict(k='setor',l='Setor · fontes',w=200),num('d0','Déficit 15/09'),num('etc','+ ETc 7 d'),num('pef','− Chuva ef.'),
                num('apl','− Aplicado (equiv. área)',w=150),num('dfin','= Déficit hoje',w=150),dict(k='enq',l='Necessidade · ordem',w=250)],
               rows,edit=dict(m='origin',title='Balanço',fields=[dict(k='setor',l='Setor',ro=True),dict(k='d0',l='Déficit em 15/09 (mm)',ro=True),dict(k='etc',l='ETc 7 dias (mm)',ro=True),
                   dict(k='pef',l='Chuva efetiva (mm)',ro=True),dict(k='apl',l='Aplicado equivalente na área total (mm)',ro=True),dict(k='dfin',l='Déficit hoje (mm)',ro=True),dict(k='lam',l='Lâmina líquida / bruta recomendada',ro=True)]),
               gid='g_bal',total=False,search=False)
    srows=[]
    for b in BAL:
        cells={}
        for i,(dia,val) in enumerate(zip(DIAS,b['serie'])):
            est=b['est'] and i>=5
            cells[f'd{i}']=(val,[(Pt.mut if est else (Pt.b if i==6 else Pt.txt))(('≈' if est else '')+_n(val,1))])
        orig=[f'Cada dia: déficit anterior + ETc {_n(b["etcd"],1)} mm − chuva efetiva − aplicado equivalente']+[f'Aplicado · {e}' for e in b['ev']]+['20/09 · chuva efetiva '+_n(b['pef'],1)+' mm (estação Santa Rita)']
        if b['est']: orig.append('21 e 22/09 estimados: sonda sem dado desde 20/09 06:00')
        srows.append(R(b['id']+'s',o=orig,setor=[Pt.b(b['setor'])],**cells))
    g_ser=grid([dict(k='setor',l='Setor')]+[dict(k=f'd{i}',l=d,t='num',a='r',d=1) for i,d in enumerate(DIAS)],srows,
               edit=dict(m='origin',title='Série diária',fields=[dict(k='setor',l='Setor',ro=True)]),gid='g_ser',total=False,search=False)
    PARS=[R('P2',setor=[Pt.b('Pivô 2'),Pt.mut('Milho V10 · 80 ha')],lmax=POL['lamina_max'],imin=18,efic=90,fonte=[Pt.txt('Sonda + estação')]),
          R('P1',setor=[Pt.b('Pivô 1'),Pt.mut('Feijão R5 · 95 ha')],lmax=POL['lamina_max'],imin=18,efic=90,fonte=[Pt.chip('Sonda suspeita · usa ET','yellow')]),
          R('T7',setor=[Pt.b('Gotejo T7'),Pt.mut('Mamão · 42 ha')],lmax=6.0,imin=12,efic=95,fonte=[Pt.chip('Sem sonda · usa ET','yellow')])]
    g_pol=grid([dict(k='setor',l='Setor',w=190),dict(k='lmax',l='Lâmina máx. por passada',t='num',a='r',u='mm',d=1,w=170),dict(k='imin',l='Intervalo mín.',t='num',a='r',u='h'),
                dict(k='efic',l='Eficiência do sistema',t='num',a='r',u='%',w=150),dict(k='fonte',l='Umidade do solo',w=200)],PARS,
               edit=dict(m='form',title='Limites do equipamento',sub='Vale para a próxima programação. As ordens já liberadas não mudam.',
                   fields=[dict(k='lmax',l='Lâmina máxima por passada',t='num',req=True,min=1,max=40,u='mm'),dict(k='imin',l='Intervalo mínimo entre passadas',t='num',req=True,min=6,max=96,u='h'),
                           dict(k='efic',l='Eficiência do sistema',t='num',req=True,min=50,max=100,u='%')]),gid='g_pol',total=False,search=False)
    EXTRAJS[0]=JS_COMUM+r"""
const PROX={'P2':13.5};
function PREVALS(self,v){ const par={}; g2rows(self,IRG('g_pol')).forEach(r=>{ par[r.id]=r.v; });
  g2rows(self,IRG('g_bal')).forEach(r=>{ let e; const lm=Number((par[r.v.sid]||{}).lmax)||12;
    if(r.v.sid==='P1') e=[{k:'chip',t:'Fertirrigação · aguarda agrônomo',c:'yellow'}];
    else if(r.v.sid==='T7') e=[{k:'chip',t:'Irrigar 4,0 mm · estimativa por ET',c:'yellow'}];
    else { const n=Math.ceil(PROX.P2/lm); e=[{k:'chip',t:'Irrigar 10,81 mm hoje · liberada',c:'green'},{k:'br',t:''},{k:'mut',t:'próximo ciclo 13,5 mm em '+n+(n>1?' passadas':' passada')}]; }
    e=e.concat([{k:'br',t:''},{k:'link',t:'Abrir '+r.v.tar,h:r.v.href}]); r.p.enq=e; r.s.enq=e[0].t; }); }
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_pol'||!r) return; const n=Math.ceil(PROX.P2/(Number(r.v.lmax)||12));
    self.setState({g2toast:'Limites do '+r.p.setor[0].t+' salvos · próxima programação usa até '+nfx(r.v.lmax,1)+' mm por passada'+(r.id==='P2'?' · 13,5 mm do próximo ciclo = '+n+(n>1?' passadas':' passada'):'')+' · ordens liberadas não mudam.'}); }; }
"""
    corpo=(
      section('Balanço por setor','Confira o déficit de cada setor; clique na linha para ver a memória de cálculo e as fontes.',
          [imsg('Recalcular e explicar','Recalculado 06:12 · ET₀ Penman-Monteith (estação Santa Rita) · chuva efetiva 60 % da chuva · memória de cálculo por setor anexada ao evento.','calc','Recalcular o balanço com as leituras de hoje')],g_bal)
      + section('Déficit no fim de cada dia (mm)','Acompanhe a evolução do déficit; ≈ indica estimativa sem sonda.','',g_ser)
      + section('Limites do equipamento','Ajuste pela linha; acima do limite a lâmina é dividida em passadas.','',g_pol)
      + section('Passagem parcial do pivô','Confira como a lâmina de uma passagem parcial entra no balanço.','',
          txt(f'Pivô 2: {_n(P["lamina_100"])} mm a 100 % em {_n(P["volta_h"])} h/volta · percentímetro {B(str(P["percent"])+" %")} → {B(_n(P["lamina_aplicada"])+" mm por passagem")}. '
              f'Uma execução de {_n(P["exec_h"])} h cobre ≈ {B(_n(P["cobertura_pct"])+" % da volta")} (11,6 ha): a lâmina é creditada só nessa área — '
              f'no balanço do setor entra o volume dividido pela área total (1.206 m³ = 1,5 mm em 80 ha), {B("nunca a lâmina cheia no pivô inteiro")}. Hidrometria validada prevalece.'))
      + navpe(1))
    shell37('IR-01','Balanço hídrico',corpo,fname=fname,
      subtitle='Confira o déficit de cada setor; o sistema programa a lâmina que a cultura precisa.',
      status=('T7 com estimativa por ET','yellow'),primary='Programar irrigação',primary_href='IR-02.dc.html',steps=faixa(1),search=False,
      footer='Água sem produto não passa pelo agrônomo. Sem sonda, o balanço usa ET e mostra estimativa; previsão do tempo nunca entra como chuva realizada.')

# =====================================================================================
def ir02():
    fname='IR-02.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    SETORES=['Pivô 2 · Milho V10','Pivô 1 · Feijão R5','Gotejo T7 · Mamão']
    def row(id,tar,tipo,setor,bomba,janela,lamina,dur,vazao,energia,conf='',fert=False,ro=False):
        r=R(id,ro=ro,tar=tar,tipo=tipo,setor=setor,bomba=bomba,janela=janela,lamina=lamina,dur=dur,vazao=vazao,energia=energia,conf=conf,novo='0')
        r['v']['fert']=fert; return r
    rows=[row('a19','OS-0419','água','Pivô 2 · Milho V10','rio · bomba B2','hoje 20:00–amanhã 10:31',P['lamina_aplicada'],round(P['volta_62_h'],1),166,'Ponta parcial (20–21 h)'),
          row('a18','OS-0418','fertirrigação v2','Pivô 1 · Feijão R5','rio · bomba B1','24/09 21:00–25/09 11:15',8.1,14.3,150,'Fora de ponta',fert=True,ro=True),
          row('a22','OS-0422','água','Pivô 2 · Milho V10','rio · bomba B2','a definir',13.5,18.1,166,'Fora de ponta'),
          row('a23','OS-0423','água','Gotejo T7 · Mamão','reservatório · bomba B3','hoje 14:00–16:00',4.0,2.0,233,'Fora de ponta',conf='Parada da B3 14:00–15:00')]
    g_ag=grid([dict(k='tar',l='Ordem',w=130),dict(k='setor',l='Setor · bomba',w=190),dict(k='janela',l='Janela · energia',w=160),dict(k='lamina',l='Lâmina · duração',t='num',a='r',u='mm',d=2,dmin=1),
               dict(k='aut',l='Etapa · pendência',w=260),dict(k='acao',l='Ação',w=170)],rows,
              edit=dict(m='form',title='Programação',newTitle='Programar período',
                  sub='Ajuste janela, lâmina e bomba. Com janela definida e sem conflito, a ordem é liberada ao salvar.',
                  fields=[dict(k='novo',l='novo',t='txt',cond=dict(k='novo',eq='__nunca'),**{'def':'1'}),
                          dict(k='setor',l='Setor',t='sel',opts=SETORES,req=True,cond=dict(k='novo',eq='1'),**{'def':SETORES[0]}),
                          dict(k='janela',l='Janela',t='txt',req=True,help='Ex.: 25/09 21:00–26/09 11:15 ou "a definir"'),
                          dict(k='lamina',l='Lâmina bruta',t='num',req=True,min=0.5,max=30,u='mm',help=f'Acima de {_n(POL["lamina_max"])} mm por passada, o sistema divide em passadas.'),
                          dict(k='dur',l='Duração',t='num',req=True,min=0.1,max=24,u='h'),
                          dict(k='vazao',l='Vazão',t='num',min=1,max=400,u='L/s'),
                          dict(k='energia',l='Energia',t='sel',opts=['Fora de ponta','Ponta parcial (20–21 h)','Ponta'],req=True,**{'def':'Fora de ponta'})]),
              gid='g_ag',total=False,add=None)
    EXTRAJS[0]=JS_COMUM+r'''
const LMAX=12.0; const SONDA={'Pivô 2 · Milho V10':'','Pivô 1 · Feijão R5':'sonda P1 suspeita','Gotejo T7 · Mamão':'sonda sem dado'};
const BOMBA={'Pivô 2 · Milho V10':['rio · bomba B2',166],'Pivô 1 · Feijão R5':['rio · bomba B1',150],'Gotejo T7 · Mamão':['reservatório · bomba B3',233]};
const LIBID={'OS-0422':'LIB-2291','OS-0423':'LIB-2292'};
// lâmina como na O.S., no Mapa e no app: 13,5 mm · 4,0 mm · 10,81 mm · 6,75 mm
function irMm(n){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:2}); }
// conflito com o mesmo selo da O.S. e do Mapa ("Conflito · parada da B3"); o horário vai na linha de baixo
function irConf(c){ const h=(/\d{1,2}:\d{2}–\d{1,2}:\d{2}/.exec(c||'')||[''])[0]; const t=String(c||'').replace(h,'').trim(); return [t.charAt(0).toLowerCase()+t.slice(1),h]; }
function janOk(j){ j=String(j||'').trim().toLowerCase(); return !!j && j.indexOf('definir')<0; }
// água só-água: sem aprovação; passadas pelo limite do equipamento; liberada quando a operação está pronta
function aval(self,r){ const x=r.v;
  if(x.fert) return {fert:true,etapa:'A liberar'};
  const lam=Number(x.lamina)||0; const np=Math.max(1,Math.ceil(lam/LMAX-1e-9)); const est=SONDA[x.setor]||'';
  const pronto=janOk(x.janela)&&!x.conf;
  return {np,por:lam/np,est,pronto,etapa:pronto?'Liberadas':'A liberar'}; }
function PREVALS(self,v){ g2rows(self,IRG('g_ag')).forEach(r=>{ const x=r.v; const a=aval(self,r);
  r.p.tar=[{k:'b',t:x.tar||'nova'},{k:'br',t:''},{k:'mut',t:x.tipo||'água'}]; r.s.tar=x.tar||'';
  r.p.setor=[{k:'txt',t:x.setor},{k:'br',t:''},{k:'mut',t:(x.bomba||'')+(x.vazao?' · '+nfx(x.vazao,0)+' L/s':'')}]; r.s.setor=x.setor;
  r.p.janela=[{k:'txt',t:x.janela},{k:'br',t:''},{k:'mut',t:x.energia||''}]; r.s.janela=x.janela;
  r.p.lamina=[{k:'txt',t:irMm(x.lamina)+' mm'},{k:'br',t:''},{k:'mut',t:(a.np>1?a.np+' passadas de '+irMm(a.por)+' mm':nfx(x.dur,1)+' h')}]; r.s.lamina=irMm(x.lamina)+' mm';
  let au, ac=[];
  if(a.fert){ au=[{k:'chip',t:'A liberar',c:'gray'},{k:'chip',t:'Aguardando agrônomo',c:'yellow'},{k:'br',t:''},{k:'mut',t:'fertirrigação · produto na água'}]; ac=[{k:'link',t:'Ver decisão',h:'IN-02det.dc.html'}]; }
  else { au=[{k:'chip',t:a.etapa,c:a.etapa==='Liberadas'?'green':'gray'}];
    const cf=irConf(x.conf);
    if(x.conf) au.push({k:'chip',t:'Conflito · '+cf[0],c:'red'});
    else if(!janOk(x.janela)) au.push({k:'chip',t:'Janela a definir',c:'yellow'});
    const mu=[x.conf&&cf[1]?'parada '+cf[1]:'',a.est?'estimativa por ET · '+a.est:''].filter(Boolean).join(' · ');
    if(mu) au.push({k:'br',t:''},{k:'mut',t:mu});
    if(x.conf) ac.push({k:'act',t:'Resolver conflito',fn:'conf:'+r.id,u:true});
    else if(!janOk(x.janela)) ac.push({k:'act',t:'Definir janela',fn:'jan:'+r.id,u:true});
    if(a.etapa==='Liberadas') ac.push(x.tar==='OS-0419'?{k:'link',t:'Abrir ordem',h:'IR-03det.dc.html'}:{k:'link',t:'Ver nas ordens',h:'IR-03.dc.html'}); }
  r.p.aut=au; r.s.aut=au.map(p=>p.t).join(' '); r.p.acao=ac.length?ac:[{k:'mut',t:'—'}]; r.s.acao=''; }); }
function upd(self,rid,fn){ const rows=g2clone(g2rows(self,IRG('g_ag'))); const r=rows.find(x=>x.id===rid); if(!r) return null; fn(r); g2set(self,'g_ag',{rows,fl:rid}); return r; }
function libMsg(self,r){ const a=aval(self,r); const x=r.v;
  return x.tar+' Liberada · '+(LIBID[x.tar]||'LIB-2293')+' · '+irMm(x.lamina)+' mm'+(a.np>1?' em '+a.np+' passadas de '+irMm(a.por)+' mm':'')+' · janela '+x.janela+' · liberar não liga o equipamento.'; }
function EXTRAVALS(self,v){ const st=self.state;
  self.g2after=(gid,rows,r,isNew)=>{ if(gid!=='g_ag'||!r) return;
    if(!r.v.tar){ const dup=rows.find(x=>x!==r && x.v.tar && !x.v.fert && x.v.setor===r.v.setor && String(x.v.janela).trim()===String(r.v.janela).trim());
      if(dup){ g2set(self,'g_ag',{rows:rows.filter(x=>x!==r),fl:dup.id}); self.setState({g2toast:'Tarefa única '+dup.v.tar+' recuperada ('+dup.v.setor+' · '+dup.v.janela+') · nenhuma ordem duplicada.'}); return; }
      const n=self.state.seq||440; const bb=BOMBA[r.v.setor]||['',0]; r.v.tar='OS-0'+n; r.v.tipo='água'; r.v.bomba=bb[0]; if(!r.v.vazao) r.v.vazao=bb[1]; r.v.conf=''; r.v.novo='0'; r.v.fert=false;
      const a=aval(self,r); self.setState({seq:n+1,g2toast:r.v.tar+' programada · '+(a.etapa==='Liberadas'?'liberada automaticamente · '+irMm(r.v.lamina)+' mm'+(a.np>1?' em '+a.np+' passadas':'')+' · sem requisição nem custódia.':'A liberar até definir a janela.')}); return; }
    const a=aval(self,r); self.setState({g2toast:a.fert?'Salvo · '+r.v.tar+' segue com o agrônomo (fertirrigação).':(a.etapa==='Liberadas'?libMsg(self,r):'Salvo · '+r.v.tar+' A liberar: '+(r.v.conf?'resolva o conflito.':'defina a janela.'))}); };
  v.conf=(rid)=>{ const r=upd(self,rid,(x)=>{ x.v.janela='hoje 15:00–17:00'; x.v.conf=''; x.s.janela='hoje 15:00–17:00'; });
    if(r) self.setState({g2toast:'Janela de '+r.v.tar+' movida para 15:00–17:00 · sem sobreposição com a parada da B3 · '+libMsg(self,r)}); };
  v.jan=(rid)=>g2open(self,IRG('g_ag'),rid,null);
  // estado no cabeçalho
  const all=g2rows(self,IRG('g_ag')); const nconf=all.filter(r=>r.v.conf).length; const njan=all.filter(r=>!r.v.fert&&!r.v.conf&&!janOk(r.v.janela)).length;
  const t=[]; if(nconf) t.push(nconf+(nconf>1?' conflitos':' conflito')); if(njan) t.push(njan+(njan>1?' janelas a definir':' janela a definir'));
  v.hs_t=t.length?t.join(' · '):'Programação sem pendências'; v.hs_st=chipSt(t.length?'yellow':'green'); }
'''
    corpo=(
      section('Agenda por setor e bomba','Programe janela, lâmina e bomba; clique na linha para ajustar e resolva conflitos na coluna Ação.',
          [imsg('Simular capacidade','Simulação hidráulica e elétrica: B2 comporta as janelas de hoje; B3 conflita com a parada de manutenção 14:00–15:00 — 1 ajuste sugerido.','gauge','Simular vazão e energia das janelas programadas')],g_ag)
      + navpe(2))
    prim=(f'<span style="{H("hs_st")}">{H("hs_t")}</span><span style="flex-grow: 0; width: 8px;"></span>'
          f'<button type="button" onClick="{H("g_ag_new")}" style="{BTN_ST(True)}">Programar período</button>')
    shell37('IR-02','Programação da irrigação',corpo,fname=fname,
      subtitle='Programe janela, lâmina e bomba; água sem produto é liberada sozinha quando a operação está pronta.',
      primary_html=prim,steps=faixa(2),search=False,
      footer='Só a fertirrigação vai ao agrônomo, com requisição. Água sem produto não usa requisição nem custódia. Liberar não liga equipamento.')

# =====================================================================================
def ir03():
    fname='IR-03.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    ET=lambda n: [Pt.chip(n,{'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray'}[n])]
    rows=[
     R('o19',ordem=[Pt.b('OS-0419'),Pt.br(),Pt.mut('Água')],setor=[Pt.txt('Pivô 2 · Milho V10'),Pt.br(),Pt.mut('hoje 20:00–amanhã 10:31')],etapa=ET('Liberadas'),alvo=P['lamina_aplicada'],
       apl=[Pt.mut('— · 0 de 80 ha · 1 volta (14,5 h)')],aut='Necessidade do balanço · AU-3098',at='hoje 06:12',acao=[Pt.cta('Abrir ordem','IR-03det.dc.html')]),
     R('o14',ordem=[Pt.b('OS-0394'),Pt.br(),Pt.mut('Água')],setor=[Pt.txt('Pivô 2 · Milho V10'),Pt.br(),Pt.mut('ontem 20:00 · parou às 22:06 (2,1 h)')],etapa=ET('Em conferência')+[Pt.chip('Divergência medida','yellow')],alvo=P['lamina_aplicada'],
       apl=[Pt.txt('10,4 mm medida (−3,8 %)'),Pt.br(),Pt.mut('11,6 de 80 ha')],aut='Necessidade do balanço',at='hoje 06:00',acao=[{'k':'act','t':'Revisar divergência','fn':'div:o14'}]),
     R('o23',ordem=[Pt.b('OS-0423'),Pt.br(),Pt.mut('Água')],setor=[Pt.txt('Gotejo T7 · Mamão'),Pt.br(),Pt.mut('hoje 14:00–16:00')],etapa=ET('A liberar')+[Pt.chip('Conflito · parada da B3','red'),Pt.mut('estimativa por ET')],alvo=4.0,apl=[Pt.mut('— · 0 de 42 ha')],aut='Necessidade estimada por ET · sonda sem dado',at='hoje 06:12',
       acao=[Pt.link('Resolver conflito','IR-02.dc.html')]),
     R('o22',ordem=[Pt.b('OS-0422'),Pt.br(),Pt.mut('Água')],setor=[Pt.txt('Pivô 2 · Milho V10'),Pt.br(),Pt.mut('janela a definir')],etapa=ET('A liberar')+[Pt.chip('Janela a definir','yellow'),Pt.mut('2 passadas de 6,75 mm')],alvo=13.5,apl=[Pt.mut('— · 0 de 80 ha')],aut='Necessidade do balanço · próximo ciclo',at='hoje 06:12',
       acao=[Pt.link('Definir janela','IR-02.dc.html')]),
     R('o18',ordem=[Pt.b('OS-0418'),Pt.br(),Pt.mut('Fertirrigação v2')],setor=[Pt.txt('Pivô 1 · Feijão R5'),Pt.br(),Pt.mut('24/09 21:00–25/09 11:15')],etapa=ET('A liberar')+[Pt.chip('Aguardando agrônomo','yellow')],alvo=8.1,apl=[Pt.mut('— · 0 de 95 ha')],aut='Aprovação individual',at='ontem 17:40',acao=[Pt.link('Ver decisão','IN-02det.dc.html')]),
     R('o12',ordem=[Pt.b('OS-0392'),Pt.br(),Pt.mut('Água')],setor=[Pt.txt('Gotejo T7 · Mamão'),Pt.br(),Pt.mut('19/09 14:00–16:00')],etapa=ET('Encerradas')+[Pt.mut('Encerrada automaticamente')],alvo=4.0,
       apl=[Pt.txt('4,0 mm medida'),Pt.br(),Pt.mut('42 de 42 ha')],aut='Necessidade do balanço',at='19/09 16:04',acao=[Pt.mut('—')]),
    ]
    g_os=grid([dict(k='ordem',l='Ordem',w=140),dict(k='setor',l='Setor · janela',w=170),dict(k='etapa',l='Etapa · selo',w=270),
               dict(k='alvo',l='Lâmina alvo',t='num',a='r',u='mm',d=2),dict(k='apl',l='Aplicada · área',w=190),dict(k='acao',l='Ação',w=200)],
              rows,edit=dict(m='ro',title='Ordem',fields=[dict(k='ordem',l='Ordem',ro=True),dict(k='setor',l='Setor · janela',ro=True),dict(k='etapa',l='Etapa · selo',ro=True),
                   dict(k='apl',l='Aplicada · área',ro=True),dict(k='aut',l='Origem da lâmina',ro=True),dict(k='at',l='Atualizada em',ro=True)]),gid='g_os',total=False)
    EXTRAJS[0]=JS_COMUM+r'''
function EXTRAVALS(self,v){ v.div=(rid)=>{ const rows=g2clone(g2rows(self,IRG('g_os'))); const r=rows.find(x=>x.id===rid); if(!r) return;
    if(r.p.etapa[0].t==='Encerradas'){ self.setState({g2toast:'OS-0394 já está encerrada.'}); return; }
    r.p.etapa=[{k:'chip',t:'Encerradas',c:'gray'},{k:'mut',t:'Hidrômetro prevaleceu'}]; r.s.etapa='Encerradas Hidrômetro prevaleceu'; r.p.acao=[{k:'mut',t:'—'}]; r.v.at='hoje 06:20';
    g2set(self,'g_os',{rows,fl:rid}); self.setState({g2toast:'Hidrômetro validado prevalece: 10,4 mm confirmados em 11,6 ha (1.206 m³) · balanço do Pivô 2 já usa o medido, sem duplicar · OS-0394 encerrada.'}); }; }
'''
    corpo=(
      section('Ordens de irrigação','Abra a ordem de hoje para executar; clique na linha para ver o resumo e siga o link da ação.',
          [imsg('Requisitar insumo','Indisponível agora: nenhuma fertirrigação aprovada. A OS-0418 aguarda o agrônomo — a requisição da mesma ordem nasce após a aprovação. Água sem produtos não usa requisição.','box','Requisitar insumo de uma fertirrigação aprovada')],g_os)
      + navpe(3))
    shell37('IR-03','Ordens de irrigação',corpo,fname=fname,
      subtitle='Abra a ordem de hoje para executar; conferência e encerramento da água consistente são automáticos.',
      status=('1 em conferência · 3 a liberar','yellow'),primary='Abrir ordem de hoje',primary_href='IR-03det.dc.html',steps=faixa(3),search=False,
      footer='Etapas: A liberar → Liberadas → Em execução → Em conferência → Encerradas. Pausa, conflito e revisão são selos; o término físico leva a Em conferência.')

# =====================================================================================
def ir03det():
    fname='IR-03det.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000; PARENT37[fname]='IR-03.dc.html'
    g_aut=grid([dict(k='ver',l='Verificação',w=200),dict(k='sit',l='Situação',w=330),dict(k='ori',l='Origem · recibo',w=330)],
               [R('x',ver='—',sit='—',ori='—')],edit=dict(m='ro',title='Verificação',fields=[dict(k='ver',l='Verificação',ro=True),dict(k='sit',l='Situação',ro=True),dict(k='ori',l='Origem · recibo',ro=True)]),
               gid='g_aut',total=False,search=False)
    g_trl=grid([dict(k='hora',l='Quando'),dict(k='rec',l='Recibo'),dict(k='ev',l='Evento',w=520),dict(k='quem',l='Quem')],
               [R('x',hora='—',rec='—',ev='—',quem='—')],edit=dict(m='ro',title='Evento',fields=[dict(k='hora',l='Quando',ro=True),dict(k='rec',l='Recibo',ro=True),dict(k='ev',l='Evento',ro=True),dict(k='quem',l='Quem',ro=True)]),
               gid='g_trl',total=False,search=False)
    EXTRAJS[0]=JS_COMUM+r'''
const FASES=['A liberar','Liberadas','Em execução','Em conferência','Encerradas'];
function hm(min){ const h=Math.floor(min/60), m=min%60; return String(h).padStart(2,'0')+':'+String(m).padStart(2,'0'); }
const T0=20*60+2, DUR=871, PZ=21*60+4;   // 1 volta a 62 % ≈ 14,52 h: início 20:02 → término amanhã 10:33
function fimMin(np){ return T0+DUR+8*np; }
function dhm(min){ return (min>=1440?'24/09 ':'23/09 ')+hm(min%1440); }   // hora com o dia (a volta passa da meia-noite)
function PREVALS(self,v){ const st=self.state; const fase=st.fase||'Liberadas'; const v2=st.v2; const np=st.np||0;
  const ch=(t,c)=>[{k:'chip',t,c}];
  const aut=[];
  if(!v2){ aut.push({id:'a1',v:{ver:'Necessidade da cultura',ori:'balanço de 23/09 · déficit 11,2 mm · AU-3098'},s:{},p:{sit:ch('10,81 mm em 1 passada · sem aprovação','green')}});
    aut.push({id:'a2',v:{ver:'Liberação operacional',ori:'prontidão validada 06:12 · LIB-2287'},s:{},p:{sit:ch('Registrada automaticamente · vigente','green')}});
    aut.push({id:'a3',v:{ver:'Requisição · custódia · sobras',ori:'água sem produtos'},s:{},p:{sit:ch('Não aplicável','gray')}});
    aut.push({id:'a4',v:{ver:'Encerramento',ori:(fase==='Encerradas'?'8.480 m³ = 10,6 mm × 10,81 mm estimados em 80 ha (−1,9 %) · EX-5120':'hidrômetro × estimativa na área coberta (tolerância 3 %)')},s:{},
      p:{sit:(fase==='Encerradas'?ch('Encerrada automaticamente · '+dhm(fimMin(np)+1),'green'):ch('Automático se os fatos forem consistentes','gray'))}}); }
  else { aut.push({id:'b1',v:{ver:'Autorização técnica',ori:'fila de Ana (agrônoma) · RC-0419-2'},s:{},p:{sit:ch('Aprovação individual pendente · v2 ('+v2.prod+' '+nfx(v2.dose,1)+' kg/ha)','yellow')}});
    aut.push({id:'b2',v:{ver:'Liberação da água',ori:'AU-3098 mantida só no histórico'},s:{},p:{sit:ch('Não vale para o saldo com produto','gray')}});
    aut.push({id:'b3',v:{ver:'Liberação operacional',ori:'nova liberação após aprovação · LIB-2287 revogada'},s:{},p:{sit:ch(v2.exec?'Saldo pausado · revisão de saldo':'Revogada · voltou a A liberar',v2.exec?'yellow':'gray')}});
    aut.push({id:'b4',v:{ver:'Requisição · custódia',ori:'mesma ordem · sem estoque paralelo'},s:{},p:{sit:ch('Após aprovação: '+nfx(v2.dose*80,0)+' kg de '+v2.prod,'gray')}});
    aut.push({id:'b5',v:{ver:'Encerramento',ori:'consumo, devolução e sobras conciliados'},s:{},p:{sit:ch('Sem encerramento automático','yellow')}}); }
  aut.forEach(r=>{ r.s.sit=r.p.sit[0].t; }); IRG('g_aut').rows=aut;
  const ev=[['23/09 06:12','AU-3098','Necessidade calculada pelo balanço · déficit 11,2 mm → 10,81 mm brutos em 1 passada (limite 12,0 mm)','sistema'],
            ['23/09 06:12','LIB-2287','Liberação operacional automática · janela hoje 20:00–amanhã 10:31, bomba B2, energia conferidas','sistema']];
  if(st.ini){ ev.push(['23/09 20:02','EX-5120','Início · telemetria da B2 ativa · mesma ordem no mapa, Kanban e app de campo','João']);
    for(let i=0;i<np;i++){ ev.push(['23/09 '+hm(PZ+16*i),'EX-5120','Pausa · selo Pausada · etapa preservada','João']); if(i<np-1||!st.pausado) ev.push(['23/09 '+hm(PZ+16*i+8),'EX-5120','Retomada','João']); } }
  if(v2) ev.push([v2.quando,'RC-0419-2','Versão v2 · '+v2.prod+' '+nfx(v2.dose,1)+' kg/ha · '+(v2.exec?'saldo em revisão; área já irrigada preservada na v1, sem duplicar no balanço':'volta a A liberar')+' · fila do agrônomo','Ana (gestora)']);
  if(fase==='Em conferência'||fase==='Encerradas') ev.push([dhm(fimMin(np)),'EX-5120','Término físico · 14,5 h de bombeamento · volta completa nos 80 ha → Em conferência','João']);
  if(fase==='Encerradas') ev.push([dhm(fimMin(np)+1),'EX-5120','Conferência automática · 8.480 m³ = 10,6 mm medidos × 10,81 mm estimados (−1,9 %) · encerrada · balanço creditado uma vez (10,6 mm em 80 ha)','sistema']);
  IRG('g_trl').rows=ev.map((e,i)=>({id:'e'+i,v:{hora:e[0],rec:e[1],ev:e[2],quem:e[3]},s:{},p:{}})); }
function EXTRAVALS(self,v){ const st=self.state; const fase=st.fase||'Liberadas'; const v2=st.v2; const np=st.np||0; const pz=!!st.pausado;
  const toast=(t)=>self.setState({g2toast:t});
  const iniciar=()=>{ const s=self.state; if(s.v2) return toast('Indisponível: a v2 aguarda aprovação individual de Ana (agrônoma); a ordem volta a Liberadas após aprovar e liberar de novo.');
    if((s.fase||'Liberadas')!=='Liberadas') return toast('A irrigação já foi iniciada às 20:02.');
    self.setState({fase:'Em execução',ini:true,g2toast:'Em execução · início 20:02 registrado (EX-5120) · telemetria da B2 ativa · término previsto amanhã 10:33.'}); };
  const terminar=()=>{ const s=self.state; const f=s.fase||'Liberadas';
    if(f!=='Em execução') return toast(f==='Liberadas'?'Indisponível: nada foi executado ainda. Inicie a irrigação; o término físico leva a ordem a Em conferência.':'Término já registrado.');
    if(s.v2) return toast('Indisponível: saldo em revisão (v2). Aguarde a aprovação individual de Ana (agrônoma).');
    if(s.pausado) return toast('Retome a irrigação antes de confirmar o término.');
    const n=s.np||0; self.setState({fase:'Em conferência',g2toast:'Término físico '+dhm(fimMin(n))+' registrado · Em conferência automática: hidrômetro × estimativa na área coberta.'});
    setTimeout(()=>{ if((self.state.fase||'')==='Em conferência') self.setState({fase:'Encerradas',g2toast:'Conferência automática: 10,6 mm medidos × 10,81 mm estimados em 80 ha (−1,9 %, tolerância 3 %) · Encerradas · recibos AU-3098 · LIB-2287 · EX-5120.'}); },1600); };
  v.pausar=()=>{ const s=self.state; const f=s.fase||'Liberadas';
    if(f!=='Em execução') return toast(f==='Liberadas'?'Indisponível: a ordem ainda está Liberada. Inicie a irrigação para pausar — a pausa vira selo e a etapa é preservada.':'Indisponível: a execução já terminou.');
    if(s.v2) return toast('Saldo já pausado pela revisão da v2.');
    const n=s.np||0; if(!s.pausado){ self.setState({pausado:true,np:n+1,g2toast:'Pausada às '+hm(PZ+16*n)+' · selo Pausada · a etapa continua Em execução.'}); }
    else self.setState({pausado:false,g2toast:'Retomada às '+hm(PZ+16*(n-1)+8)+' · término previsto '+dhm(fimMin(n))+'.'}); };
  v.pz_t=pz?'Retomar':'Pausar'; v.pz_ico_play=pz; v.pz_ico_pause=!pz;
  // cabeçalho: selo + ação primária
  let t,c; if(v2&&!v2.exec){ t='A liberar · aguardando agrônomo (v2)'; c='yellow'; } else if(v2){ t='Em execução · revisão de saldo (v2)'; c='yellow'; }
  else if(fase==='Liberadas'){ t='Liberadas · hoje 20:00–amanhã 10:31'; c='green'; } else if(fase==='Em execução'){ t=pz?'Em execução · Pausada':'Em execução · desde 20:02'; c=pz?'yellow':'green'; }
  else if(fase==='Em conferência'){ t='Em conferência · automática'; c='yellow'; } else { t='Encerradas · '+dhm(fimMin(np)+1); c='gray'; }
  v.hs_t=t; v.hs_st=chipSt(c);
  let pt,pf,off=false; if(v2){ pt='Aguardando aprovação da v2'; pf=iniciar; off=true; } else if(fase==='Liberadas'){ pt='Iniciar irrigação'; pf=iniciar; }
  else if(fase==='Em execução'){ pt='Confirmar término da irrigação'; pf=terminar; } else if(fase==='Em conferência'){ pt='Conferindo…'; pf=()=>toast('Conferência automática em andamento.'); off=true; }
  else { pt=''; pf=null; }
  v.prim_t=pt; v.prim_fn=pf||(()=>{}); v.prim_st=off?PRIMOFF:PRIM; v.prim_btn=!!pf; v.prim_link=!pf;
  v.term=terminar;
  // trilha de etapas da ordem
  const cur=(v2&&!v2.exec)?'A liberar':fase; const ci=FASES.indexOf(cur);
  FASES.forEach((f,i)=>{ v['tr'+i]=(i<ci)?'display:inline-flex;align-items:center;gap:6px;padding:5px 11px;border-radius:999px;font-size:12.5px;font-weight:700;color:#1E7A4C;background:#E4F3E9;'
      :(i===ci?'display:inline-flex;align-items:center;gap:6px;padding:5px 11px;border-radius:999px;font-size:12.5px;font-weight:800;color:#fff;background:#1E7A4C;'
      :'display:inline-flex;align-items:center;gap:6px;padding:5px 11px;border-radius:999px;font-size:12.5px;font-weight:600;color:#5B6660;background:#EEF1EE;'); });
  const selos=[]; if(pz) selos.push('Pausada'); if(v2) selos.push(v2.exec?'Revisão de saldo · v2':'Aguardando agrônomo · v2'); v.tr_selo=selos.join(' · '); v.tr_has_selo=selos.length>0;
  v.tr_hint=v2?(v2.exec?'A área já irrigada fica na v1, sem duplicar no balanço; o saldo espera a aprovação da v2.':'Com produtos, a ordem precisa de aprovação individual, requisição e conciliação; não encerra sozinha.')
    :(fase==='Encerradas'?'Fatos consistentes: conferida e encerrada automaticamente.':'Água sem produto: sem aprovação; com registros consistentes, conferência e encerramento são automáticos.');
  v.c_aqui=t; v.c_falta=v2?'aprovação individual da v2':({Liberadas:'iniciar e confirmar o término','Em execução':'confirmar o término','Em conferência':'conferência automática',Encerradas:'nada nesta ordem'}[fase]);
  v.c_prox=pt||'Voltar às ordens';
  // reclassificação (adicionar produtos)
  const rc=st.rc; v.rc_open=!!rc;
  v.rc_abrir=()=>{ const s=self.state; const f=s.fase||'Liberadas'; if(s.v2) return toast('A v2 já está na fila do agrônomo.'); if(f==='Em conferência'||f==='Encerradas') return toast('Indisponível: a execução terminou. Programe uma nova fertirrigação em Programe a irrigação.');
    const d={prod:'Ureia 45%',dose:'12',mot:''}; self.setState({rc:{d,o:Object.assign({},d),err:{},warn:false}}); };
  if(rc){ const exec=(fase==='Em execução'); v.rc_titulo='Adicionar produtos · OS-0419'; v.rc_sub='Reclassifica para fertirrigação criando a versão v2 da mesma ordem: herda ID, setor, janela e saldo. Só quem pode propor ou revisar o saldo usa esta ação.';
    v.rc_prod=rc.d.prod; v.rc_dose=rc.d.dose; v.rc_mot=rc.d.mot; const n=g2num(rc.d.dose);
    v.rc_prev=(exec?'A ordem continua Em execução com selo Revisão de saldo: o saldo pausa e a área já irrigada fica na v1, sem duplicar no balanço.':'A ordem volta a A liberar: com produto, o saldo precisa do agrônomo e a liberação LIB-2287 é revogada.')
      +' Requisição de '+(isNaN(n)?'—':nfx(n*80,0))+' kg só após a aprovação individual.';
    const set=(k)=>(e)=>{ const cur=self.state.rc; const d=Object.assign({},cur.d,{[k]:e.target.value}); const er=Object.assign({},cur.err); delete er[k]; self.setState({rc:Object.assign({},cur,{d,err:er,warn:false})}); };
    v.rc_setprod=set('prod'); v.rc_setdose=set('dose'); v.rc_setmot=set('mot');
    ['dose','mot'].forEach(k=>{ v['rc_e'+k]=(rc.err||{})[k]||''; v['rc_e'+k+'_has']=!!(rc.err||{})[k]; });
    const dirty=()=>{ const cur=self.state.rc; return Object.keys(cur.d).some(k=>String(cur.d[k])!==String(cur.o[k])); };
    v.rc_warn=!!rc.warn; v.rc_cancel=()=>{ if(dirty()) self.setState({rc:Object.assign({},self.state.rc,{warn:true})}); else self.setState({rc:null}); };
    v.rc_discard=()=>self.setState({rc:null}); v.rc_keep=()=>self.setState({rc:Object.assign({},self.state.rc,{warn:false})});
    v.rc_ok=()=>{ const cur=self.state.rc; const er={}; const dn=g2num(cur.d.dose); if(isNaN(dn)||dn<=0) er.dose='Use um número maior que zero (ex.: 12).'; else if(dn>50) er.dose='Máximo 50 kg/ha por evento.';
      if(!String(cur.d.mot||'').trim()) er.mot='Informe o motivo agronômico.'; if(Object.keys(er).length){ self.setState({rc:Object.assign({},cur,{err:er})}); return; }
      const ex=((self.state.fase||'Liberadas')==='Em execução'); const quando='23/09 '+(ex?hm(PZ+30):'18:40');
      self.setState({rc:null,pausado:false,v2:{prod:cur.d.prod,dose:dn,mot:cur.d.mot,exec:ex,quando},
        g2toast:'OS-0419 v2 criada ('+cur.d.prod+' '+nfx(dn,1)+' kg/ha) · fila de Ana (agrônoma) · '+(ex?'segue Em execução com selo Revisão de saldo · saldo pausado':'voltou a A liberar · a liberação da água não vale para o saldo com produto')+' · requisição só após a aprovação.'}); }; }
}
'''
    trail=(f'<div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">'
           + f'<span aria-hidden="true" style="color: {MUTED};">›</span>'.join(f'<span style="{H("tr"+str(i))}">{f}</span>' for i,f in enumerate(['A liberar','Liberadas','Em execução','Em conferência','Encerradas']))
           + f'<sc-if value="{H("tr_has_selo")}" hint-placeholder-val="{F()}"><span style="margin-left: 8px; display: inline-flex; padding: 4px 10px; border-radius: 999px; background: {YELS}; color: {YEL}; font-size: 12px; font-weight: 700;">{H("tr_selo")}</span></sc-if></div>'
           + f'<div style="font-size: 12.8px; color: {MUTED}; margin-top: 8px;">{H("tr_hint")}</div>')
    def kv(items):
        return (f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px 18px; margin-top: 14px; padding-top: 12px; border-top: 1px solid {LINE};">'
                + ''.join(f'<div style="display: flex; flex-direction: column; gap: 2px; min-width: 0;"><span style="font-size: 11px; font-weight: 700; letter-spacing: .05em; color: {MUTED}; text-transform: uppercase;">{l}</span>'
                          f'<span style="font-size: 13.5px; font-weight: 600;">{t}</span></div>' for l,t in items) + '</div>')
    pz_btn=(f'<button type="button" onClick="{H("pausar")}" title="Pausar ou retomar a irrigação em execução (a pausa vira selo)" style="{_IST}{BTN_ST(False,True)}">'
            f'<sc-if value="{H("pz_ico_pause")}" hint-placeholder-val="{H("true")}">{ic("pause")}</sc-if><sc-if value="{H("pz_ico_play")}" hint-placeholder-val="{F()}">{ic("play")}</sc-if>{H("pz_t")}</button>')
    acoes=[pz_btn,ilink('Registrar avanço','MB-08.dc.html','phone','Registrar avanço pelo app de campo'),
           ifn('Adicionar produtos','rc_abrir','plus','Reclassificar para fertirrigação: cria a versão v2 desta mesma ordem')]
    rc_corpo=(campo('Produto','rc_prod',f'<select id="rc_prod" value="{H("rc_prod")}" onChange="{H("rc_setprod")}" style="{INP}"><option value="Ureia 45%">Ureia 45%</option><option value="Nitrato de cálcio">Nitrato de cálcio</option><option value="Nitrato de potássio">Nitrato de potássio</option></select>','rc_eprod')
              + campo('Dose (kg/ha)','rc_dose',f'<input id="rc_dose" value="{H("rc_dose")}" onChange="{H("rc_setdose")}" style="{INP}">','rc_edose')
              + campo('Motivo agronômico','rc_mot',f'<textarea id="rc_mot" value="{H("rc_mot")}" onChange="{H("rc_setmot")}" placeholder="Ex.: deficiência de N no estádio V10" style="{INP} min-height: 64px; resize: vertical;"></textarea>','rc_emot')
              + f'<div style="padding: 10px 12px; border-radius: 10px; background: {BG}; font-size: 12.8px; line-height: 1.5;"><b>Efeito</b> · {H("rc_prev")}</div>')
    rc_rod=(f'<button type="button" onClick="{H("rc_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button>'
            f'<button type="button" onClick="{H("rc_ok")}" style="{BTN_ST(True,True)}">Criar versão v2</button>')
    EXTRA.append(painel('rc',rc_corpo,rc_rod))
    corpo=(
      continuity('Programação de hoje',H('c_aqui'),H('c_falta'),H('c_prox'))
      + section('Execução','Inicie, pause e confirme o término; cada comando grava um recibo na trilha.',acoes,
          trail + kv([('Setor','Pivô 2 · Milho V10 · 80 ha'),('Janela','hoje 20:00–amanhã 10:31'),('Bomba · energia','B2 · 166 L/s · ponta parcial (20–21 h)'),
                      ('Lâmina alvo',f'{_n(P["lamina_aplicada"])} mm (percentímetro {P["percent"]} %)'),('Duração','14,5 h (1 volta) · término previsto amanhã 10:33'),('Déficit de origem','11,2 mm · balanço de 23/09')]))
      + section('Lâmina e área creditada','Confira a lâmina e a área que o balanço vai creditar.','',
          txt(f'{_n(P["lamina_100"])} mm a 100 % em {_n(P["volta_h"])} h/volta · percentímetro {B(str(P["percent"])+" %")} → {B(_n(P["lamina_aplicada"])+" mm por passagem")} em ≈ 14,52 h/volta. '
              f'A volta completa credita {_n(P["lamina_aplicada"])} mm nos 80 ha. Se a volta parar antes, o balanço credita só a área coberta '
              f'(ex.: {_n(P["exec_h"])} h ≈ {B(_n(P["cobertura_pct"])+" % da volta")} ≈ 11,6 ha), {B("não o pivô inteiro")}; o hidrômetro validado prevalece sobre a estimativa.'))
      + section('Origem e materiais','Confira de onde vem a lâmina e o que não se aplica à água sem produtos.','',g_aut)
      + section('Trilha e recibos','Confira os eventos desta ordem, do mais antigo ao mais recente.','',g_trl)
      + navpe(3))
    prim=(f'<span style="{H("hs_st")}">{H("hs_t")}</span><span style="width: 8px;"></span>'
          f'<sc-if value="{H("prim_btn")}" hint-placeholder-val="{H("true")}"><button type="button" onClick="{H("prim_fn")}" style="{H("prim_st")}">{H("prim_t")}</button></sc-if>'
          f'<sc-if value="{H("prim_link")}" hint-placeholder-val="{F()}"><a href="IR-03.dc.html" style="{BTN_ST(True)} text-decoration: none;">Voltar às ordens</a></sc-if>')
    shell37('IR-03','OS-0419 · Irrigação · Pivô 2',corpo,fname=fname,crumbs_extra=['OS-0419'],
      subtitle='Execute a irrigação e confirme o término; o comando físico continua com o irrigante.',
      primary_html=prim,steps=faixa(3),search=False,
      footer='Apontamento de algo já ocorrido nunca concede autorização retroativa. Telemetria e registro manual do mesmo evento atualizam uma única aplicação.')

# =====================================================================================
def ir04():
    fname='IR-04.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    EST={'Ativa':'green','Suspeita · salto 18 p.p.':'red','Sem dado desde 20/09':'yellow','Aguardando 1ª leitura':'gray','Previsão ≠ chuva realizada':'gray'}
    def srow(id,nome,gr,at,un,cal,cob,estado,acao,ro=False):
        r=R(id,ro=ro,at=at,cal=cal,cob=cob,estado=(estado,[Pt.chip(estado,EST[estado])]),acao=acao,gr=gr,un=un)
        r['v']['nome']=nome; r['p']['nome']=[Pt.b(nome),Pt.br(),Pt.mut(gr+' · '+un)]; r['s']['nome']=nome; return r
    rows=[srow('s1','Estação meteorológica Santa Rita','ET₀ / chuva / vento','hoje 06:00','mm/dia · mm','2027-02-28','Raio 8 km','Ativa',[Pt.mut('—')]),
          srow('s2','Hidrômetro · Pivô 2','Volume','hoje 06:00','m³','2026-09-30','Pivô 2','Ativa',
               [Pt.act('Agendar calibração','Inspeção do hidrômetro do Pivô 2 criada para 29/09 · troca ou reset exige evento próprio com leituras de fechamento e abertura — nunca consumo negativo silencioso.')]),
          srow('s3','Sonda de umidade · P1 (20 cm)','Umidade do solo','hoje 05:40','% vol.','2027-01-31','Pivô 1','Suspeita · salto 18 p.p.',[Pt.cta('Abrir ação','GE-07.dc.html',u=True)]),
          srow('s4','Sonda de umidade · T7','Umidade do solo','20/09 06:00','% vol.','2027-01-31','Gotejo T7','Sem dado desde 20/09',[Pt.cta('Abrir ação','GE-07.dc.html')]),
          srow('s5','Previsão meteorológica (modelo externo)','Chuva prevista 48 h','hoje 06:00','mm','','Regional','Previsão ≠ chuva realizada',[Pt.mut('—')],ro=True)]
    g_src=grid([dict(k='nome',l='Fonte',w=300),dict(k='at',l='Atualização'),dict(k='cal',l='Calibração',w=210),
                dict(k='cob',l='Cobertura'),dict(k='estado',l='Estado',w=230,chips=EST),dict(k='acao',l='Ação',w=170)],rows,
               edit=dict(m='form',title='Fonte',newTitle='Cadastrar sensor',sub='Ajuste o cadastro e a próxima calibração. O estado vem das leituras validadas.',
                   fields=[dict(k='nome',l='Nome',t='txt',req=True),dict(k='gr',l='Grandeza',t='sel',req=True,opts=['ET₀ / chuva / vento','Volume','Umidade do solo','Chuva prevista 48 h'],**{'def':'Umidade do solo'}),
                           dict(k='un',l='Unidade',t='sel',req=True,opts=['mm/dia · mm','m³','% vol.','mm'],**{'def':'% vol.'}),
                           dict(k='cob',l='Setor coberto',t='sel',req=True,opts=['Pivô 1','Pivô 2','Gotejo T7','Raio 8 km','Regional'],**{'def':'Pivô 2'}),
                           dict(k='cal',l='Próxima calibração',t='date',req=True)]),
               gid='g_src',total=False,add='Cadastrar sensor')
    drows=[R('p2',o=['Hidrômetro · Pivô 2 · 32.480 m³ (09–22/09)','Medidor de energia · bomba B2 · 23.370 kWh','Eficiência = volume ÷ energia · lâmina = volume ÷ 80 ha'],
             setor=[Pt.b('Pivô 2'),Pt.mut('Milho')],vol=32480,kwh=23370,lam=40.6,evt='10,4 mm (medida · 22/09)',ef=1.39,ind=[Pt.chip('+4 % vs quinzena anterior','green')]),
           R('p1',o=['Hidrômetro · Pivô 1 · 34.580 m³ (09–22/09)','Medidor de energia · bomba B1 · 25.610 kWh','Lâmina = volume ÷ 95 ha'],
             setor=[Pt.b('Pivô 1'),Pt.mut('Feijão')],vol=34580,kwh=25610,lam=36.4,evt='8,1 mm (medida · 21/09)',ef=1.35,ind=[Pt.chip('Estável','gray')]),
           R('t7',o=['Hidrômetro · Gotejo T7 · 10.080 m³ (09–22/09)','Medidor de energia · bomba B3 · 5.760 kWh','Lâmina = volume ÷ 42 ha','Sonda sem dado desde 20/09: balanço estimado'],
             setor=[Pt.b('Gotejo T7'),Pt.mut('Mamão')],vol=10080,kwh=5760,lam=24.0,evt='4,0 mm (medida · 19/09)',ef=1.75,ind=[Pt.chip('Sem sonda desde 20/09','yellow')])]
    g_des=grid([dict(k='setor',l='Setor'),dict(k='vol',l='Volume',t='num',a='r',u='m³',agg='sum'),dict(k='kwh',l='Energia',t='num',a='r',u='kWh',agg='sum'),
                dict(k='lam',l='Lâmina aplicada',t='num',a='r',u='mm',d=1),dict(k='evt',l='Último evento'),dict(k='ef',l='Eficiência',t='num',a='r',u='m³/kWh',d=2),dict(k='ind',l='Indicador')],drows,
               edit=dict(m='origin',title='Desempenho',fields=[dict(k='setor',l='Setor',ro=True),dict(k='vol',l='Volume (m³)',ro=True),dict(k='kwh',l='Energia (kWh)',ro=True),dict(k='ef',l='Eficiência (m³/kWh)',ro=True)]),
               gid='g_des',search=False)
    EXTRAJS[0]=JS_COMUM+r'''
const HOJE='2026-09-23';
function dias(a,b){ return Math.round((new Date(b+'T12:00:00')-new Date(a+'T12:00:00'))/86400000); }
function br(s){ const a=String(s).split('-'); return a.length===3?a[2]+'/'+a[1]+'/'+a[0]:s; }
function PREVALS(self,v){ g2rows(self,IRG('g_src')).forEach(r=>{ const c=r.v.cal; let p;
    if(!c) p=[{k:'tag',t:'Não se aplica'}]; else { const d=dias(HOJE,c); p=d<0?[{k:'chip',t:'Vencida em '+br(c),c:'red'}]:(d<=7?[{k:'chip',t:'Vence '+br(c),c:'yellow'}]:[{k:'chip',t:'Em dia · até '+br(c),c:'green'}]); }
    r.p.cal=p; r.s.cal=p[0].t; r.p.nome=[{k:'b',t:r.v.nome},{k:'br',t:''},{k:'mut',t:(r.v.gr||'')+' · '+(r.v.un||'')}]; r.s.nome=r.v.nome;
    if(!r.v.estado){ r.v.estado='Aguardando 1ª leitura'; r.p.estado=[{k:'chip',t:'Aguardando 1ª leitura',c:'gray'}]; r.s.estado='Aguardando 1ª leitura'; r.v.at='—'; r.p.acao=[{k:'mut',t:'—'}]; } }); }
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{ if(gid==='g_src'&&r&&String(r.id).indexOf('n')===0) self.setState({g2toast:'Sensor cadastrado · aguardando a primeira leitura validada · nada entra no balanço sem origem.'}); }; }
'''
    corpo=(
      section('Fontes e sensores','Confira origem, calibração e estado de cada fonte; clique na linha para ajustar o cadastro.',
          [imsg('Importar leitura','12 leituras importadas da estação · 1 rejeitada por unidade divergente (in → mm) · nada gravado sem origem.','upload','Importar leituras de arquivo ou da estação'),
           imsg('Marcar leitura suspeita','Leitura da sonda P1 marcada como suspeita · excluída do balanço até a inspeção · ação vinculada na gestão.','flag','Excluir uma leitura do balanço até a inspeção')],g_src)
      + section('Desempenho por setor · 09–22/09','Compare volume, energia e eficiência da quinzena; clique na linha para ver a origem de cada número.',
          [imsg('Comparar períodos','Comparativo 26/08–08/09 × 09–22/09: Pivô 2 +4 % de eficiência após o ajuste do percentímetro; Pivô 1 estável; Gotejo T7 sem sonda desde 20/09.','trend','Comparar com a quinzena anterior')],g_des)
      + navpe(4))
    shell37('IR-04','Clima, sensores e desempenho',corpo,fname=fname,
      subtitle='Confira a qualidade das fontes; leitura suspeita sai do balanço até a inspeção.',
      status=('1 leitura suspeita · 1 sensor sem dado','yellow'),primary='Abrir ação da sonda P1',primary_href='GE-07.dc.html',steps=faixa(4),search=False,
      footer='Previsão do tempo orienta a programação, mas não entra como chuva realizada. Troca ou reset de medidor exige evento próprio.')

def build():
    ir01(); ir02(); ir03(); ir03det(); ir04()
