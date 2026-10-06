# -*- coding: utf-8 -*-
"""Onboarding (módulo OCULTO do menu, preservado) — padrão G2 (edição pela linha, descrições imperativas).
ON-01 Entrada e implantação guiada (+ ON-01det prévia da importação). Módulo não sequencial: sem faixa de etapas.
06/10/2026 (PLAT-01): o backoffice da plataforma saiu daqui: BO-01 Planos e preços e BO-02 Assinaturas e cobrança estão em
areas/plataforma.py, no mesmo estado da assinatura (c.assin); BO-01det, BO-02det, BO-03, BO-03det e BO-04 saíram (PLAT-D02).
O trial da Boa Esperança (TRIAL) vem de dados_assinatura.py: um só trial para ON-01, BO-01 e BO-02.

observacoes (dados locais — não existem em dados.py/dados2.py; coerentes com caps. 57–58 e com o mundo DEMO):
- Organização Boa Esperança (trial, coorte set/2026) é outro contratante: HOJE = dados.HOJE (23/09) é o dia 5 de 30 (19/09 → 18/10).
- Prévia da importação: 12 linhas de talhões = 9 limpas + 1 sobreposição + 2 duplicidades (T1, T2) · 48 linhas de estoque · 6 máquinas.
"""
import json, re
from engine import (grid,section,kpis,chip,btn,tag,icon,esc,msgbtn,drawer_button,field,Pt,
                    INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,BTN_ST,EXTRAJS)
from ui37 import shell37, continuity, HEIGHTS37, PARENT37
import dados as D

H=lambda s: '{{'+s+'}}'
# ---- dados locais (coerentes com caps. 57–58) ----
CTX_ON=('Organização Boa Esperança','Trial · termina 18/10/2026',None); PERFIL_ON='Otávio · Responsável'
PRIV='Nenhum privilégio administrativo concede consulta indiscriminada a dados agronômicos dos clientes.'
from dados_assinatura import TRIAL   # um só trial para ON-01, BO-01 e BO-02 (PLAT-01, RV-09)

# ---------- ajudantes: botões com ícone + rótulo + title ----------
def _ic(html,name,title):
    m=re.match(r'^(<(button|a)\b[^>]*?)>(.*)</(button|a)>$',html,re.S)
    return f'{m.group(1)} title="{esc(title)}"><span style="display: inline-flex; align-items: center; gap: 6px;">{icon(name,14)}{m.group(3)}</span></{m.group(4)}>'
def imsg(t,msg,ic,title,primary=False): return _ic(msgbtn(t,msg,primary=primary),ic,title)
def ilnk(t,href,ic,title): return _ic(btn(t,small=True,href=href),ic,title)
def sbtn(t,fn,ic,title,primary=False):
    return (f'<button type="button" onClick="{H(fn)}" title="{esc(title)}" style="{BTN_ST(primary,True)}">'
            f'<span style="display: inline-flex; align-items: center; gap: 6px;">{icon(ic,14)}{esc(t)}</span></button>')
def csel(label,opts):
    """lista suspensa com as opções do cadastro certo (evita a heurística genérica de field())."""
    idn=''.join(ch for ch in label.lower() if ch.isalnum())
    o=''.join(f'<option{" selected" if i==0 else ""}>{esc(x)}</option>' for i,x in enumerate(opts))
    return (f'<div style="display: flex; flex-direction: column; gap: 4px; min-width: 0;"><label for="{idn}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{esc(label)}</label>'
            f'<select id="{idn}" style="font-family: inherit; font-size: 14px; font-weight: 500; color: {INK}; padding: 10px 12px; border: 1px solid {LINE}; border-radius: 10px; background: {SURF}; width: 100%;">{o}</select></div>')
def dd(title,sub,campos,confirm,done,href=None):
    """painel lateral: campos = [(rótulo, valor)] ou [(rótulo, [opções])] → lista suspensa."""
    body=''.join(csel(l,v) if isinstance(v,list) else field(l,v,ph=(v=='')) for l,v in campos)
    return dict(title=title,sub=sub,fields=[],content=body,confirm=confirm,done=done,href=href)
def idrw(t,d,ic,title,primary=False): return _ic(drawer_button(t,d,primary=primary),ic,title)
def dpart(t,d):
    """ação de linha que abre um painel lateral (não abre a edição da linha)."""
    h=drawer_button(t,d); did=re.search(r'\{\{\s*(\w+)_open\s*\}\}',h).group(1)
    return {'k':'act','t':t,'fn':did+'_open','did':did,'done':d['done']}
def texto(html_): return f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.65;">{html_}</div>'
def _priv():
    return (f'<div style="display: flex; align-items: center; gap: 8px; font-size: 12.5px; color: {MUTED};">'
            f'{icon("check",14,ACC)}<span><b style="color:{INK};">Isolamento:</b> {esc(PRIV)}</span></div>')
def acoes(*xs): return f'<div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">{"".join(xs)}</div>'
B=lambda s: f'<b style="color:{INK};">{s}</b>'

# =====================================================================================
def on01():
    fn='ON-01.dc.html'; HEIGHTS37[fn]=1180
    d_org=dd('Rever dados da organização','CPF/CNPJ só é pedido na contratação.',
             [('Nome da organização','Boa Esperança'),('Responsável','Otávio'),('E-mail do responsável','otavio@boaesperanca.agro')],
             'Salvar dados','Dados da organização salvos')
    d_des=dd('Desenhar talhão','Geometria validada e área calculada; sobreposição exige justificativa.',
             [('Fazenda',['Boa Esperança']),('Nome do talhão','T1'),('Cultura','Soja')],'Salvar desenho','Talhão salvo · área calculada 48,2 ha')
    d_car=dd('Anexar CAR','O documento fica pendente e visível até ser anexado; nada é presumido.',
             [('Arquivo do CAR',''),('Número do recibo do CAR','')],'Anexar documento','CAR anexado · pendência resolvida')
    d_cul=dd('Cultura e ciclo','Informe as datas com a precisão que você tiver; dá para ajustar depois.',
             [('Cultura','Soja'),('Safra',['2026/27','Safrinha 2027']),('Plantio previsto','')],'Salvar cultura e ciclo','Cultura e ciclo salvos · próximo passo: recursos')
    d_eq=dd('Convidar pessoa','O convite preserva organização, papel e destino; não cria empresa duplicada.',
            [('E-mail','joao@boaesperanca.agro'),('Papel',['Operador','Agrônomo','Gestor','Consulta']),('Fazenda',['Boa Esperança'])],
            'Enviar convite','Convite enviado · pendente de aceite (simulado · nenhuma mensagem real enviada)')
    d_imp=dd('Importar dados','Prévia obrigatória com mapeamento, sistema de coordenadas e erros por objeto; nada é gravado sem validar.',
             [('Arquivo','talhoes_boa_esperanca.zip (shapefile)'),('Objeto',['Talhões','Estoque inicial','Máquinas']),('Sistema de coordenadas','SIRGAS 2000 / UTM 22S (detectado)')],
             'Gerar prévia','Prévia gerada',href='ON-01det.dc.html')
    d_int=dd('Configurar integração (opcional)','O modo autônomo funciona sem integração; conector empresarial não é benefício implícito do trial.',
             [('Sistema de origem',['ERP contábil (consulta)','Planilha periódica','Nenhum (autônomo)']),('Escopo','Cadastros e custos')],
             'Solicitar homologação','Solicitação registrada · funcionalidade segue demonstrativa até homologar')
    P=[('p1','1 · Organização','Concluído','green','nome e e-mail do responsável — CPF/CNPJ só na contratação',[dpart('Rever dados',d_org)]),
       ('p2','2 · Fazenda e área','Com pendências','yellow',f'área declarada {TRIAL["area_ha"]} ha · faltam o polígono (desenho ou importação) e o CAR — nada é presumido',
        [dpart('Desenhar áreas',d_des),dpart('Anexar CAR',d_car)]),
       ('p3','3 · Cultura e ciclo','Em andamento','yellow','cultura Soja · safra 2026/27 · datas com a precisão que você tiver',[dpart('Continuar cultura e ciclo',d_cul)]),
       ('p4','4 · Recursos','A fazer','gray','máquinas e equipe são pedidas quando a primeira O.S. precisar delas',[dpart('Convidar equipe',d_eq)]),
       ('p5','5 · Importação','3 objetos com erro','yellow','prévia, mapeamento e erros por objeto antes de gravar',[Pt.cta('Corrigir prévia','ON-01det.dc.html')]),
       ('p6','6 · Primeiro trabalho','A fazer','gray','rascunho de planejamento da safra com próximos passos',[{'k':'mut','t':'pelo botão principal'}])]
    g_p=grid([dict(k='passo',l='Passo',w=170),dict(k='estado',l='Estado'),dict(k='dado',l='Dado pedido no momento do uso',w=380),dict(k='acao',l='Próxima ação',w=280)],
       [dict(id=i,v=dict(passo=p,estado=e,dado=dd_,acao=' '.join(x['t'] for x in a)),s={},p=dict(passo=[Pt.b(p)],estado=[Pt.chip(e,c)],acao=a)) for i,p,e,c,dd_,a in P],
       edit=dict(m='ro',title='Passo',fields=[dict(k='passo',l='Passo',ro=True),dict(k='estado',l='Estado',ro=True),dict(k='dado',l='Dado pedido',t='area',ro=True)]),
       search=False,gid='g_passos',total=False)
    T=[('t1','Cadastro, planejamento, execução e consultas','Incluído no trial','green','30 dias','período',f'termina {TRIAL["fim"]} · aviso desde a entrada'),
       ('t2','Área gerida','Incluído no trial','green',f'{TRIAL["area_ha"]} ha','área declarada','importação maior abre revisão transparente do limite, sem cobrar'),
       ('t3','Cenas de satélite','Franquia finita','yellow','12','cenas / 30 dias','serviço pausa; demonstração identificada continua'),
       ('t4','Assistente de IA','Franquia finita','yellow','200','interações / 30 dias','pausa ao esgotar; o resto do trial continua'),
       ('t5','Exportação dos próprios dados','Sempre disponível','green','ilimitada','—','mantida por 90 dias após expirar (janela informada)'),
       ('t6','Comando remoto de equipamento','Fora do trial','gray','—','—','não é benefício implícito; contratação empresarial')]
    g_t=grid([dict(k='rec',l='Recurso',w=260),dict(k='hab',l='Habilitação'),dict(k='fr',l='Franquia'),dict(k='un',l='Unidade'),dict(k='fim',l='Ao esgotar ou expirar',w=380)],
       [dict(id=i,v=dict(rec=r,hab=h,fr=f,un=u,fim=x),s={},p=dict(hab=[Pt.chip(h,c)])) for i,r,h,c,f,u,x in T],
       edit=dict(m='ro',title='Direito do trial',fields=[dict(k='rec',l='Recurso',ro=True),dict(k='fr',l='Franquia',ro=True),dict(k='un',l='Unidade',ro=True),dict(k='fim',l='Ao esgotar ou expirar',t='area',ro=True)]),
       search=False,gid='g_trial',total=False)
    # ações de linha: quando o painel é confirmado, a linha mostra o resultado e o estado do passo avança
    acts={i:a for i,_,_,_,_,a in P}
    EXTRAJS[0]='const ON_ACTS='+json.dumps(acts,ensure_ascii=False)+';\n'+ON1_JS
    corpo=(
      kpis([('TRIAL',H('k_tdia'),H('k_tfim')),('ÁREA DECLARADA',f'{TRIAL["area_ha"]} ha','limite do trial'),
            ('PENDÊNCIAS',H('k_pend'),H('k_pendd')),('MODO','Autônomo','sem integração')])
      + section('Passos do assistente','Continue de onde parou: cada dado é pedido quando for usado e nada fictício é gravado como fato.',
        [idrw('Importar arquivo',d_imp,'doc','Importar planilha ou shapefile com prévia obrigatória'),
         idrw('Configurar integração',d_int,'layers','Conectar um sistema de origem (opcional)'),
         ilnk('Abrir mapa','IN-04.dc.html','map','Ver as áreas no mapa')],g_p)
      + section('Direitos do trial','Confira o que o trial inclui e o que acontece quando cada franquia acaba.',
        chip('Valores de piloto · hipótese','yellow'),g_t,state='yellow'))
    shell37('ON-01','Entrada e implantação guiada',corpo,ctx=CTX_ON,perfil=PERFIL_ON,
      subtitle='Veja o mapa cedo; operar exige os dados e autorizações do processo, pedidos no momento do uso.',
      status=('Passo 3 de 6 · retomável','yellow'),
      primary='Criar primeiro planejamento',primary_href='SAF.dc.html',
      footer='Entrada por Google, Apple ou e-mail leva à mesma conta; contratar não exige cartão para tarefas gratuitas (ONB-04/06, cap. 58).')

ON1_JS=r'''
const ON_EST={p2:['Concluído','green'],p3:['Concluído','green'],p4:['Em andamento','yellow']};
function PREVALS(self,v){ const ad=self.state.added||{}; let pend=['polígono','CAR','prévia'];
  g2rows(self,GRIDS.find(g=>g.id==='g_passos')).forEach(r=>{ const a=ON_ACTS[r.id]||[]; let all=a.length>0 && a.some(x=>x.did);
    r.p.acao=a.map(x=>{ if(!x.did) return x; if(ad[x.did]) return {k:'chip',t:x.done.split(' · ')[0],c:'green'}; all=false; return x; });
    if(r.id==='p2'){ if(ad[a[0].did]) pend=pend.filter(x=>x!=='polígono'); if(ad[a[1].did]) pend=pend.filter(x=>x!=='CAR'); }
    if(all && ON_EST[r.id]){ r.p.estado=[{k:'chip',t:ON_EST[r.id][0],c:ON_EST[r.id][1]}]; r.s.estado=ON_EST[r.id][0]; } });
  v.k_pend=String(pend.length); v.k_pendd=pend.join(' · ')||'nenhuma';
  /* dia do trial pela mesma data simulada do BO-02 (PLAT-D19; revisão PLAT, achado 8) */
  const A=assinLer(), tr=assinTrial(A.orgs.boaesp,A.hoje); v.k_tdia=tr.acabou?'encerrado':tr.t; v.k_tfim='até '+assinBrC(tr.fim); }
'''
# =====================================================================================
ON_JS=r'''
const IMP_PEND={tal:'1 talhão com sobreposição a justificar',est:'o estoque inicial (48 linhas) até definir a unidade da coluna “qtde”',dup:'2 duplicidades (T1, T2) aguardando mesclar ou ignorar'};
function imp_R(self){ return g2rows(self,GRIDS.find(g=>g.id==='g_imp')); }
function imp_ok(r){ const x=r.v; if(r.id==='tal') return !!String(x.just||'').trim(); if(r.id==='est') return !!x.un && x.un!=='A definir'; if(r.id==='dup') return !!x.dec && x.dec!=='A decidir'; return true; }
function PREVALS(self,v){ const gv=self.state.grav||{}; let nerr=0;
  imp_R(self).forEach(r=>{ const x=r.v; const ok=imp_ok(r); let err=null;
    if(r.id==='tal' && !ok) err='1 sobreposição a justificar';
    if(r.id==='est'){ if(!ok) err='coluna “qtde” sem unidade'; r.p.map=[{k:'txt',t:x.map+(ok?' · qtde em '+x.un:'')}]; r.s.map=r.p.map[0].t; }
    if(r.id==='dup' && !ok) err='mesclar ou ignorar — decisão sua';
    r.p.crs=[{k:(r.id==='tal'?'txt':'mut'),t:(r.id==='tal'?(x.crs||'—'):'—')}];
    r.p.erros=err?[{k:'chip',t:err,c:'yellow'}]:[{k:'mut',t:'—'}]; r.s.erros=err||'—';
    let e,c;
    if(r.id==='tal'){ if(gv.tal1){ e='Gravado · 10 talhões'; c='green'; } else if(gv.tal9){ e='9 gravados · 1 na prévia'; c='yellow'; } else if(ok){ e='Pronto para validar'; c='green'; } else { e='Prévia · 9 prontos'; c='gray'; } }
    else if(r.id==='dup'){ if(gv.dup){ e='Resolvido · '+(x.dec.indexOf('Mesclar')===0?'mesclados':'ignorados'); c='green'; } else if(ok){ e='Pronto para validar'; c='green'; } else { e='Prévia'; c='gray'; } }
    else { if(gv[r.id]){ e='Gravado'; c='green'; } else if(ok){ e='Pronto para validar'; c='green'; } else { e='Prévia'; c='gray'; } }
    r.p.estado=[{k:'chip',t:e,c:c}]; r.s.estado=e;
    const done=(r.id==='tal')?gv.tal1:gv[r.id]; r.ro=!!done;
    if(!ok && !done) nerr++; });
  v.imp_falta=nerr?('corrigir '+nerr+(nerr>1?' objetos':' objeto')+' com erro'):'nada · validar o que falta';
}
function EXTRAVALS(self,v){
  v.val_fn=()=>{ const gv=Object.assign({},self.state.grav||{}); const R=imp_R(self); const by={}; R.forEach(r=>by[r.id]=r); const nov=[], pend=[];
    if(!gv.tal9){ gv.tal9=true; nov.push('9 talhões'); }
    if(imp_ok(by.tal)){ if(!gv.tal1){ gv.tal1=true; nov.push('1 talhão com sobreposição justificada'); } } else pend.push(IMP_PEND.tal);
    if(!gv.maq){ gv.maq=true; nov.push('6 máquinas'); }
    if(imp_ok(by.est)){ if(!gv.est){ gv.est=true; nov.push('48 linhas de estoque ('+by.est.v.un+')'); } } else pend.push(IMP_PEND.est);
    if(imp_ok(by.dup)){ if(!gv.dup){ gv.dup=true; nov.push('duplicidades T1 e T2 '+(by.dup.v.dec.indexOf('Mesclar')===0?'mescladas ao desenho':'ignoradas')); } } else pend.push(IMP_PEND.dup);
    let m=nov.length?('Gravados: '+nov.join(', ')):'Nada novo a gravar · validação idempotente, nenhum registro duplicado';
    m+= pend.length?(' · permanecem na prévia, com erro localizado: '+pend.join('; ')+'.'):' · prévia concluída.';
    self.setState({grav:gv,g2toast:m}); };
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_imp'||!r) return; self.setState({g2toast: imp_ok(r)?('Erro corrigido em '+r.v.obj+' · valide a prévia para gravar'):('Salvo · '+r.v.obj+' ainda com erro')}); };
}
'''
def on01det():
    fn='ON-01det.dc.html'; HEIGHTS37[fn]=900; PARENT37[fn]='ON-01.dc.html'
    CRS=['SIRGAS 2000 / UTM 22S','SIRGAS 2000 / UTM 23S','SIRGAS 2000 (geográfico)','WGS 84']
    rows=[dict(id='tal',v=dict(obj='Talhões (shapefile)',linhas=12,map='automático (nome, cultura)',crs='SIRGAS 2000 / UTM 22S',just=''),s={},p={}),
          dict(id='est',v=dict(obj='Estoque inicial (planilha)',linhas=48,map='item, depósito, qtde',un='A definir'),s={},p={}),
          dict(id='maq',v=dict(obj='Máquinas (planilha)',linhas=6,map='automático'),s={},p={}),
          dict(id='dup',v=dict(obj='Duplicidades',linhas=2,map='T1 e T2 já desenhados no mapa',dec='A decidir'),s={},p={})]
    for r in rows: r['p']['obj']=[Pt.b(r['v']['obj'])]
    g=grid([dict(k='obj',l='Objeto',w=200),dict(k='linhas',l='Linhas',t='num',a='r'),dict(k='map',l='Mapeamento',w=240),dict(k='crs',l='Sistema de coordenadas',w=200),
            dict(k='erros',l='Erro'),dict(k='estado',l='Estado')],rows,
       edit=dict(m='form',title='Objeto da importação',sub='Corrija o erro deste objeto; a prévia é recalculada e nada é gravado até você validar.',
            fields=[dict(k='obj',l='Objeto',ro=True),dict(k='map',l='Mapeamento de colunas',t='txt',req=True,help='A IA pode sugerir; nunca completa dados.'),
                    dict(k='crs',l='Sistema de coordenadas',t='sel',opts=CRS,req=True,cond=dict(k='obj',eq='Talhões (shapefile)')),
                    dict(k='just',l='Justificativa da sobreposição (T2 × T3, 2 ha)',t='area',cond=dict(k='obj',eq='Talhões (shapefile)'),help='Sem justificativa, o talhão sobreposto fica na prévia.'),
                    dict(k='un',l='Unidade da coluna “qtde”',t='sel',opts=['A definir','sc 50 kg','kg','t','L','un'],req=True,cond=dict(k='obj',eq='Estoque inicial (planilha)')),
                    dict(k='dec',l='Decisão sobre T1 e T2',t='sel',opts=['A decidir','Mesclar com o desenho','Ignorar da importação'],req=True,cond=dict(k='obj',eq='Duplicidades'))]),
       search=False,gid='g_imp',total=False)
    corpo=(
      continuity('Assistente de implantação (passo 5)','Prévia da importação',H('imp_falta'),'Validar prévia')
      + section('Erros e mapeamento por objeto','Clique no objeto para corrigir o erro na própria linha; depois valide para gravar o que passou.','',g,state='yellow')
      + section('Regra da importação','Grave somente o que foi validado; a IA sugere mapeamentos, mas não completa dados.','',
        texto(f'Estoque, análise ou plantio {B("nunca")} são completados com dados inventados. Área importada maior que a declarada ({TRIAL["area_ha"]} ha) '
              f'abre {B("revisão transparente do limite do trial")}, sem cobrança automática.'),state='gray'))
    EXTRAJS[0]=ON_JS
    shell37('ON-01','Importação · prévia e erros',corpo,fname=fn,crumbs_extra=['Importação'],ctx=CTX_ON,perfil=PERFIL_ON,
      subtitle='Prévia com mapeamento, sistema de coordenadas e erros por objeto; duplicidade detectada e relatório corrigível.',
      status=('3 objetos com erro','yellow'),
      primary_html=f'<button type="button" onClick="{H("val_fn")}" title="Gravar o que passou na validação" style="{BTN_ST(True)}">Validar prévia</button>',
      footer='Validar grava somente o que passou; o erro permanece preenchido na prévia com correção localizada (cap. 58.3).')

def build():
    on01(); on01det()
