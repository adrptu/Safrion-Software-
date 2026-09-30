# Aplica na O.S.: aba Recursos (PCP), seções Recursos alocados e Retirada e fichas na tela da ordem.
import re
p = 'areas/processo_os.py'; s = open(p).read()
def rep(a, b, tag):
    global s
    n = s.count(a); assert n == 1, f'{tag}: {n}'
    s = s.replace(a, b)

# ---------- Python: dados de alocação e aba Recursos ----------
rep("import dados2 as D2\n", "import dados2 as D2\nimport alocacao as AL\n", 'import')
s = s.replace("def build():\n", '''def _recursos_tab():
    """Semana do PCP por recurso e dia: ordens e horários, conflitos, manutenção, excesso de jornada e uso."""
    res, conf = AL.semana()
    ck = {(c['r'], c['dia'], c['a']) for c in conf} | {(c['r'], c['dia'], c['b']) for c in conf}
    nconf = len({(c['dia'], c['a'], c['b']) for c in conf if not c['manut']})
    manut = sorted({AL.NOME[a['r']] + ' (' + a['os'] + ')' for a in AL.ALOC if a['sit'] == 'manutenção'})
    acima = [f"{x['nome'].split(' · ')[0]} {d['d'][8:10]}/{d['d'][5:7]} ({str(round(d['h'],1)).replace('.',',')} h)" for x in res for d in x['dias'] if d['acima']]
    ociosos = [x['nome'].split(' · ')[0] for x in res if x['uso'] < 0.2]
    kpi = lambda t, v, c: f'<div style="display: flex; flex-direction: column; gap: 2px; padding: 8px 12px; border-radius: 10px; background: {c}; min-width: 0;"><span style="font-size: 11px; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; color: {MUTED};">{t}</span><span style="font-size: 13px; font-weight: 700;">{v}</span></div>'
    top = (f'<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px;">'
           + kpi('Conflitos', f'{nconf} · mesmo recurso em duas ordens no mesmo horário', REDS if nconf else BG)
           + kpi('Em manutenção', ', '.join(manut) or '—', BG) + kpi('Acima da jornada', ', '.join(acima) or '—', YELS if acima else BG)
           + kpi('Ociosos (uso abaixo de 20 %)', ', '.join(ociosos) or '—', BG) + '</div>')
    cols = f'grid-template-columns: 210px repeat({len(AL.DIAS)}, minmax(118px, 1fr)) 150px;'
    head = (f'<div style="display: grid; {cols} gap: 0; font-size: 10.5px; font-weight: 800; letter-spacing: .04em; text-transform: uppercase; color: {MUTED}; background: {BG}; border-radius: 10px 10px 0 0;">'
            f'<div style="padding: 8px 10px;">Recurso</div>' + ''.join(f'<div style="padding: 8px 6px;">{lab}</div>' for _, lab in AL.DIAS) + '<div style="padding: 8px 10px;">Uso na semana</div></div>')
    body = ''; tipo0 = None
    for x in res:
        if x['tipo'] != tipo0:
            tipo0 = x['tipo']; body += f'<div style="padding: 10px 10px 4px; font-size: 11px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; color: {MUTED}; border-top: 1px solid {LINE};">{ {"Máquina":"Máquinas","Implemento":"Implementos","Pessoa":"Pessoas"}[tipo0] }</div>'
        cells = ''
        for d in x['dias']:
            its = ''
            for a in d['itens']:
                t = f"{a['os']} {AL.hh(a['ini'])}–{AL.hh(a['fim'])}"
                if a['sit'] == 'manutenção':
                    its += f'<span title="Indisponível: {a["os"]}" style="display: block; font-size: 11.5px; font-weight: 700; padding: 3px 6px; border-radius: 6px; background: {GRAYS}; color: {MUTED};">Manutenção {a["os"]}</span>'; continue
                bad = (x['r'], d['d'], a['os']) in ck
                st = ('background: #FDE8E6; color: #B42318; border: 1px solid #F4C7C1;' if bad else ('background: #FFF4D6; color: #8A5A00; border: 1px dashed #D9B25B;' if a['sit'] == 'condicional' else f'background: {ACCS}; color: {ACC}; border: 1px solid #BFE0CB;'))
                tt = ('Conflito de horário · ' if bad else ('Condicional · ' if a['sit'] == 'condicional' else '')) + 'abrir ' + a['os']
                its += f'<button type="button" onClick="{H("op_" + a["os"].replace("-", ""))}" title="{tt}" style="display: block; width: 100%; text-align: left; font-family: inherit; font-size: 11.5px; font-weight: 700; padding: 3px 6px; border-radius: 6px; cursor: pointer; {st}">{t}</button>'
            hint = (f'<span style="font-size: 11px; color: #8A5A00; font-weight: 700;">{str(round(d["h"],1)).replace(".",",")} h · acima da jornada</span>' if d['acima']
                    else (f'<span style="font-size: 11px; color: {MUTED};">livre</span>' if not d['itens'] else ''))
            cells += f'<div style="padding: 6px; display: flex; flex-direction: column; gap: 3px; border-left: 1px solid {LINE};">{its}{hint}</div>'
        u = round(x['uso'] * 100); cor = '#B42318' if any(d['conf'] for d in x['dias']) else ('#8A968E' if x['uso'] < 0.2 else ('#8A5A00' if x['uso'] > 0.85 else '#1E7A4C'))
        lab = 'conflito' if any(d['conf'] for d in x['dias']) else ('ocioso' if x['uso'] < 0.2 else ('carga alta' if x['uso'] > 0.85 else 'em uso'))
        uso = (f'<div style="padding: 8px 10px; border-left: 1px solid {LINE}; display: flex; flex-direction: column; gap: 4px;"><span style="font-size: 13px; font-weight: 800; color: {cor};">{u} % · {lab}</span>'
               f'<span style="display: block; height: 6px; border-radius: 999px; background: {GRAYS}; overflow: hidden;"><span style="display: block; height: 100%; width: {min(u,100)}%; background: {cor};"></span></span>'
               f'<span style="font-size: 11px; color: {MUTED};">{str(round(x["h"],1)).replace(".",",")} h de {str(round(x["disp"],1)).replace(".",",")} h</span></div>')
        body += f'<div role="row" style="display: grid; {cols} border-top: 1px solid {LINE}; font-size: 12.5px;"><div style="padding: 8px 10px; font-weight: 700;">{esc(x["nome"])}</div>{cells}{uso}</div>'
    legenda = (f'<div style="display: flex; gap: 14px; flex-wrap: wrap; font-size: 11.5px; color: {MUTED};">'
               f'<span><b style="color: {ACC};">■</b> alocação firme</span><span><b style="color: #8A5A00;">▭</b> condicional (depende de aprovação ou liberação)</span>'
               f'<span><b style="color: #B42318;">■</b> conflito de horário</span><span><b style="color: #8A968E;">■</b> manutenção</span></div>')
    return (f'<div style="display: flex; flex-direction: column; gap: 10px;">{top}'
            f'<div role="table" aria-label="Alocação de recursos na semana" style="border: 1px solid {LINE}; border-radius: 10px; overflow-x: auto;">{head}{body}</div>{legenda}</div>')

def build():
''', 1)
rep("bar,panes=tabs(['Lista','Kanban'],[f'<div style=\"display: flex; flex-direction: column; gap: 10px;\">{lista}</div>',_kanban()],active=0,label='Visão das ordens')",
    "bar,panes=tabs(['Lista','Kanban','Recursos'],[f'<div style=\"display: flex; flex-direction: column; gap: 10px;\">{lista}</div>',_kanban(),_recursos_tab()],active=0,label='Visão das ordens')", 'tabs')
rep("data=dict(ords=ordens,nova=_nova_ordem_dados())", "data=dict(ords=ordens,nova=_nova_ordem_dados(),aloc={o['id']:AL.da_ordem(o['id']) for o in ordens})", 'data')

# ---------- JS: abrir ordem pela aba Recursos; seções da tela da ordem ----------
rep("function EXTRAVALS(self,v){\n  const st=self.state, os=ords(self);",
    "function EXTRAVALS(self,v){\n  const st=self.state, os=ords(self);\n  os.forEach(o=>{ v['op_'+o.id.replace('-','')]=()=>self.setState({pan:o.id,pa:null}); });", 'op-holes')
rep("  v.pan_hasIns=v.pan_ins.length>0;",
    """  v.pan_rec=((OSD.aloc||{})[o.id]||[]).map(r=>({t:r.tipo+' · '+r.nome,j:r.janelas,cond:!!r.cond,al:(r.alertas||[]).map(t=>({t})),hasAl:(r.alertas||[]).length>0}));
  v.pan_hasRec=v.pan_rec.length>0;
  const EQ={'Pulverização':{cap:3000,un:'L',vaz:100,nome:'tanque útil 3.000 L · 100 L/ha'},'Adubação a lanço':{cap:3000,un:'kg',nome:'distribuidor 3.000 kg'}}[a.op];
  const areaP=(o.etapa==='Em execução')?(o.saldo||0):(o.area||0);
  let prep=''; if(EQ&&areaP>0&&(o.ins||[]).length){ const ac=EQ.vaz?EQ.cap/EQ.vaz:EQ.cap/(o.ins.reduce((t,x)=>t+x.dose,0)||1); const n=Math.ceil(areaP/ac-1e-9); const ult=areaP-ac*(n-1);
    prep=n+(n>1?' cargas':' carga')+' ('+EQ.nome+'): '+nd(ac,1)+' ha por carga'+(ult<ac-1e-9?'; última '+nd(ult,1)+' ha':'')+' · '+(o.ins||[]).map(x=>x.p+' '+nd(x.dose*ac,1)+' '+x.un+' por carga').join(', ')+(o.etapa==='Em execução'?' (saldo de '+nf(o.saldo)+' ha)':''); }
  v.pan_prep=prep; v.pan_hasPrep=!!prep&&['Liberadas','Em execução'].indexOf(o.etapa)>=0;
  v.pan_fichas=o.id==='OS-0424'; v.pan_hasRet=(o.ins||[]).length>0&&['Liberadas','Em execução'].indexOf(o.etapa)>=0;
  v.pan_hasIns=v.pan_ins.length>0;""", 'osWork-rec')

# ---------- HTML: seções na tela da ordem ----------
rep("""      f'<div style="display: flex; flex-direction: column; gap: 4px;">{lab("Apontamentos diários")}'""",
    """      f'<sc-if value="{H("pan_hasRet")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 6px;">{lab("Retirada e fichas de execução")}'
      f'<sc-if value="{H("pan_hasPrep")}" hint-placeholder-val="{F()}"><div style="font-size: 13px; line-height: 1.45;">{H("pan_prep")}</div></sc-if>'
      f'<div style="display: flex; gap: 8px; flex-wrap: wrap;"><a href="EST.dc.html" style="{_MINI} text-decoration: none;">Retirar no almoxarifado ›</a>'
      f'<sc-if value="{H("pan_fichas")}" hint-placeholder-val="{F()}"><a href="OS-0424-app.dc.html" style="{_MINI} text-decoration: none;">Ficha no app (sem internet) ›</a><a href="OS-0424-ficha.dc.html" style="{_MINI} text-decoration: none;">Ficha impressa ›</a></sc-if></div></div></sc-if>'
      f'<sc-if value="{H("pan_hasRec")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 2px;">{lab("Recursos alocados")}'
      f'<sc-for list="{H("pan_rec")}" as="rc" hint-placeholder-count="3"><div style="display: grid; grid-template-columns: minmax(0,1.2fr) minmax(0,1fr) minmax(0,1.3fr); gap: 10px; align-items: center; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 12.8px;">'
      f'<b>{H("rc.t")}</b><span style="color: {MUTED};">{H("rc.j")}</span><span style="display: flex; flex-wrap: wrap; gap: 4px;"><sc-if value="{H("rc.cond")}" hint-placeholder-val="{F()}"><span style="display: inline-flex; padding: 2px 8px; border-radius: 999px; font-size: 11.5px; font-weight: 700; color: #8A5A00; background: #FFF4D6;">condicional</span></sc-if>'
      f'<sc-for list="{H("rc.al")}" as="al" hint-placeholder-count="1"><span style="display: inline-flex; padding: 2px 8px; border-radius: 999px; font-size: 11.5px; font-weight: 700; color: #B42318; background: #FDE8E6;">{H("al.t")}</span></sc-for></span></div></sc-for></div></sc-if>'
      f'<div style="display: flex; flex-direction: column; gap: 4px;">{lab("Apontamentos diários")}'""", 'painel-secoes')
open(p, 'w').write(s); print('patch recursos ok')
