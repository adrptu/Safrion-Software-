# -*- coding: utf-8 -*-
"""Onboarding e backoffice (módulo OCULTO do menu, preservado) — padrão G2 (edição pela linha, descrições imperativas).
ON-01 Entrada e implantação guiada (+ ON-01det prévia da importação) · BO-01 Planos e contratos (+ BO-01det Produtor Piloto v3)
· BO-02 Assinaturas e cobrança (+ BO-02det Fazenda Aurora) · BO-03 Medição e conciliação (+ BO-03det contestação) · BO-04 Economia (caps. 57–58).
Módulo não sequencial: sem faixa de etapas.

observacoes (dados locais — não existem em dados.py/dados2.py; coerentes com caps. 57–58 e com o mundo DEMO):
- Grupo Santa Rita = 1.165 ha (soma dos talhões de dados.TALHOES) × R$ 2 = R$ 2.330 (FAT-2209-014).
- Organização Boa Esperança (trial, coorte set/2026) é outro contratante: HOJE = dados.HOJE (23/09) é o dia 5 de 30 (19/09 → 18/10).
- Prévia da importação: 12 linhas de talhões = 9 limpas + 1 sobreposição + 2 duplicidades (T1, T2) · 48 linhas de estoque · 6 máquinas.
- BO-02: 23/09 é antes da tentativa 2 (25/09) — tentativas 2 e 3 aparecem como agendadas; evento novo só existe para FAT-2209-016 (evt_1JKT5).
- BO-04: coorte ago/2026 HF/frutas tem 4 de 6 contas ativadas (67 %) → 2 não ativaram, ambas paradas na Importação (antes dizia 4 de 6 paradas).
- BO-03det: ajuste AJ-010 (R$ 0) é a resposta documentada à contestação da Fazenda Aurora.
"""
import json, re
from engine import (grid,section,kpis,chip,btn,tag,icon,esc,msgbtn,drawer_button,field,Pt,
                    INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,BTN_ST,EXTRAJS)
from ui37 import shell37, continuity, HEIGHTS37, PARENT37
import dados as D

H=lambda s: '{{'+s+'}}'
# ---- dados locais (coerentes com caps. 57–58) ----
CTX_BO=('Backoffice da plataforma',None,None); PERFIL_BO='Admin plataforma'
CTX_ON=('Organização Boa Esperança','Trial · termina 18/10/2026',None); PERFIL_ON='Otávio · Responsável'
PRIV='Nenhum privilégio administrativo concede consulta indiscriminada a dados agronômicos dos clientes.'
HIP='Hipótese comercial · não publicável sem decisão'
from dados_assinatura import TRIAL   # um só trial para ON-01, BO-01 e BO-02 (PLAT-01, RV-09)
CONTRATANTES=['Grupo Santa Rita','Fazenda Aurora','Sítio Ipê','Coop. Verde Vale','Agro Bela Vista','Rancho Dois Rios','Fertisul','Organização Boa Esperança','Fazenda Três Marias']
OFERTAS=['Produtor Piloto v3','Patrocínio Cooperativa v2','Parceiro Profissional v1','Trial agricultor v2']
PLANOS=[  # (id, plano/versão, segmento, moeda, vigência, tarifa, estado)
 ('v3','Produtor Piloto v3','Produtores · grãos/HF','BRL','01/07/26 – 30/06/27','maior entre R$ 299 e R$ 2/ha·mês','Vigente'),
 ('v4','Produtor Piloto v4','Produtores · grãos/HF','BRL','sem vigência','R$ 2/ha·mês + faixas marginais','Proposta'),
 ('pp1','Parceiro Profissional v1','Fornecedores','BRL','01/09/26 – 31/08/27','R$/organização·mês (em reais)','Revisada'),
 ('pc2','Patrocínio Cooperativa v2','Carteira patrocinada','BRL','01/08/26 – 31/07/27','R$/ha da carteira deduplicada, com mínimo','Vigente'),
 ('v2','Produtor Piloto v2','Produtores · grãos','BRL','01/01/26 – 30/06/26','R$ 2/ha·mês sem mínimo','Substituída'),
]
EST_PLANO={'Proposta':'gray','Revisada':'yellow','Vigente':'green','Substituída':'gray','Encerrada':'gray'}
FATURAS=[  # estados do cap. 58: pendente, ação necessária, pago, falhou, estornado, cancelado
 ('FAT-2209-014','Grupo Santa Rita',2330,'Pago','evt_1JKQ8 validado · conciliação idempotente'),
 ('FAT-2209-015','Fazenda Aurora',299,'Falhou','evt_1JKR2 · tentativa 1 recusada · 2ª em 25/09'),
 ('FAT-2209-016','Sítio Ipê',299,'Pendente','aguardando evento do provedor'),
 ('FAT-2209-017','Coop. Verde Vale',6400,'Ação necessária','autenticação bancária adicional do pagador'),
 ('FAT-2208-009','Agro Bela Vista',640,'Estornado','estorno conciliado com documento de origem'),
 ('FAT-2208-011','Rancho Dois Rios',299,'Cancelado','cancelamento antes da emissão · sem cobrança'),
]
EST_FAT={'Pago':'green','Pendente':'gray','Ação necessária':'yellow','Falhou':'red','Estornado':'gray','Cancelado':'gray'}
MEDICAO=[  # (id, contratante, base, contratada, medida, franquias, estado, divergência, cor, origens)
 ('sr','Grupo Santa Rita','área contratada','1.165 ha','1.165 ha','satélite 9/12 · IA 140/200','Conciliado','—','gray',
  ['Área contratada 1.165 ha · contrato Produtor Piloto v3 (aceite 01/07/2026)','Área medida 1.165 ha · polígonos validados, safras e sobreposições sem duplicar',
   'Mensalidade R$ 2.330 = 1.165 ha × R$ 2 (acima do mínimo de R$ 299) · FAT-2209-014']),
 ('cv','Coop. Verde Vale','carteira patrocinada','20,0 mil ha','19,6 mil ha','—','Aberto','—','gray',
  ['Carteira contratada 20,0 mil ha · Patrocínio Cooperativa v2','Carteira medida 19,6 mil ha · deduplicada por área física entre cooperados',
   'Período aberto até 30/09 · fatura FAT-2209-017 aguarda o pagador']),
 ('fa','Fazenda Aurora','área contratada','60 ha','35 ha','satélite 2/12','Contestado','base em contestação','red',
  ['Área contratada 60 ha · contrato v1 (aceite 01/08/2026)','Área ocupada apurada 35 ha · polígonos validados 12/09',
   'Mensalidade R$ 299 nas duas bases (mínimo prevalece)']),
 ('bv','Agro Bela Vista','área contratada','320 ha','333 ha','IA 60/200','Ajustado','+13 ha · aceite pendente','yellow',
  ['Área contratada 320 ha · contrato vigente','Área medida 333 ha · ampliação desenhada em 10/09',
   'AJ-009 +13 ha documentado · volta à conciliação · vigência out/2026 com aceite']),
 ('si','Sítio Ipê','área contratada','20 ha','20 ha','satélite 4/12','Aprovado','—','gray',
  ['Área contratada 20 ha · Produtor Piloto v3','Área medida 20 ha · sem divergência','Mensalidade R$ 299 (mínimo) · FAT-2209-016']),
]
EST_MED={'Aberto':'gray','Conciliado':'green','Contestado':'red','Ajustado':'yellow','Aprovado':'green'}
COORTES=[  # (id, coorte, perfil, contas, ativadas, pagantes, retidas 90d, receita/conta, suporte h)
 ('c1','jul/2026','Agricultor · grãos',8,6,4,7,'R$ 1.010','1,2 h'),
 ('c2','ago/2026','Agricultor · HF/frutas',6,4,2,5,'R$ 299','3,4 h'),
 ('c3','set/2026','Agricultor · grãos',9,5,None,None,'—','0,8 h'),
 ('c4','ago/2026','Fornecedor (portal)',12,10,3,11,'R$ 480','0,5 h'),
 ('c5','set/2026','Cooperativa patrocinadora',1,1,1,None,'R$ 6.400','2,0 h'),
]

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
PST=json.dumps(BTN_ST(True)); PSTOFF=json.dumps(BTN_ST(False))

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
      kpis([('TRIAL','dia 5 de 30','até 18/10'),('ÁREA DECLARADA',f'{TRIAL["area_ha"]} ha','limite do trial'),
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
  v.k_pend=String(pend.length); v.k_pendd=pend.join(' · ')||'nenhuma'; }
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

# =====================================================================================
BO1_JS=r'''
const BO_EP={Proposta:'gray',Revisada:'yellow',Vigente:'green','Substituída':'gray',Encerrada:'gray'};
function PREVALS(self,v){ const R=g2rows(self,GRIDS.find(g=>g.id==='g_pl')); let vig=0,hip=0;
  R.forEach(r=>{ const x=r.v; const e=x.estado||'Proposta'; const h=(e==='Proposta'||e==='Revisada');
    r.p.plano=(r.id==='v3')?[{k:'link',t:x.plano,h:'BO-01det.dc.html'}]:[{k:'b',t:x.plano||''}];
    r.p.tarifa=[{k:'txt',t:x.tarifa||''},{k:'br',t:''},h?{k:'chip',t:'Hipótese · não publicável',c:'yellow'}:{k:'tag',t:'preço de piloto · hipótese'}];
    r.p.estado=[{k:'chip',t:e,c:BO_EP[e]||'gray'}]; r.s.estado=e; r.ro=!h;
    if(e==='Vigente') vig++; if(h) hip++; });
  v.k_vig=String(vig); v.k_hip=String(hip); }
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_pl'||!r) return;
    if(!(r.v.estado==='Proposta'||r.v.estado==='Revisada')){ r.v.estado=r.v.e0||'Proposta'; r.s.estado=r.v.estado;
      self.setState({g2toast:'Estado mantido como '+r.v.estado+': vigência só por Aprovar tabela, com decisão comercial. Os demais campos foram salvos.'}); return; }
    r.v.e0=r.v.estado;
    if(!r.v.moeda) r.v.moeda='BRL';
    self.setState({g2toast:(r.id.indexOf('n')===0?(r.v.plano+' criada como proposta · hipótese rotulada · contratos vigentes intactos'):('Salvo · '+r.v.plano+' segue '+r.v.estado.toLowerCase()+' e não publicável sem decisão'))}); };
}
'''
def bo01():
    fn='BO-01.dc.html'; HEIGHTS37[fn]=1120
    SEG=['Produtores · grãos/HF','Produtores · grãos','Fornecedores','Carteira patrocinada']
    g=grid([dict(k='plano',l='Plano e versão',w=200),dict(k='seg',l='Contratante / segmento',w=180),dict(k='moeda',l='Moeda'),dict(k='vig',l='Vigência'),
            dict(k='tarifa',l='Tarifa, mínimo e excedentes',w=300),dict(k='estado',l='Estado')],
       [dict(id=i,v=dict(plano=p,seg=s_,moeda=m,vig=vg,tarifa=t,estado=e,e0=e),s={},p={}) for i,p,s_,m,vg,t,e in PLANOS],
       edit=dict(m='form',title='Versão de plano',newTitle='Nova versão de plano',
            sub='Ajuste a proposta; versões vigentes ou substituídas abrem em consulta e mudam só por nova versão, sem retroagir.',
            fields=[dict(k='plano',l='Plano e versão',t='txt',req=True,**{'def':'Produtor Piloto v5'}),dict(k='seg',l='Contratante / segmento',t='sel',opts=SEG,req=True,**{'def':SEG[0]}),
                    dict(k='moeda',l='Moeda',t='sel',opts=['BRL'],req=True,**{'def':'BRL'}),dict(k='vig',l='Vigência',t='txt',req=True,help='Ex.: 01/07/27 – 30/06/28, ou "sem vigência" enquanto proposta.',**{'def':'sem vigência'}),
                    dict(k='tarifa',l='Tarifa, mínimo e excedentes',t='area',req=True,**{'def':'R$ 2/ha·mês · mínimo R$ 299'}),
                    dict(k='estado',l='Estado',t='sel',opts=['Proposta','Revisada'],req=True,help='Vigente só por Aprovar tabela, com decisão comercial.',**{'def':'Proposta'})]),
       search=False,gid='g_pl',total=False)
    TM=[('tv2','Trial agricultor v2','set/2026','30 dias','área declarada na entrada','satélite 12 cenas · IA 200 interações · ao esgotar, o serviço pausa e o trial segue utilizável','consulta e exportação por 90 dias','Aprovada (piloto)','green'),
        ('tp1','Trial parceiro v1','—','60 dias por categoria','—','ferramentas profissionais','histórico comercial 12 meses (hipótese)','Hipótese','yellow')]
    g_tm=grid([dict(k='ver',l='Versão e coorte',w=170),dict(k='dur',l='Duração',w=120),dict(k='area',l='Limite de área',w=120),dict(k='fr',l='Franquias e esgotamento',w=270),
               dict(k='ret',l='Retenção e exportação',w=150),dict(k='est',l='Estado')],
       [dict(id=i,v=dict(ver=a,co=b,dur=c,area=d_,fr=e,ret=g_,est=h),s=dict(ver=f'{a} {b}'),p=dict(ver=[Pt.b(a)]+([Pt.br(),Pt.mut('coorte '+b)] if b!='—' else []),est=[Pt.chip(h,cc)])) for i,a,b,c,d_,e,g_,h,cc in TM],
       edit=dict(m='ro',title='Matriz do trial',fields=[dict(k='ver',l='Versão',ro=True),dict(k='co',l='Coorte',ro=True),dict(k='dur',l='Duração',ro=True),dict(k='fr',l='Franquias e esgotamento',t='area',ro=True),dict(k='ret',l='Retenção e exportação',ro=True)]),
       search=False,gid='g_tm',total=False)
    d_vinc=dd('Vincular contrato a contratante','A consulta contratual do cliente fica em CF-05 (produtor) ou PT-07 (parceiro).',
              [('Contratante',CONTRATANTES[-1:]+CONTRATANTES[:-1]),('Oferta',OFERTAS),('Vigência início','01/10/2026')],
              'Vincular com aceite','Contrato vinculado · aceite registrado · sem cobrança retroativa')
    corpo=(
      kpis([('VIGENTES NO PILOTO',H('k_vig'),'preços-hipótese do piloto'),('HIPÓTESES',H('k_hip'),'propostas e revisadas · não publicáveis'),
            ('CONTRATOS VINCULADOS','14','todas as versões')])
      + section('Tabelas de plano por versão','Clique numa proposta para ajustá-la; versões vigentes mudam só por nova versão, sem retroagir.',
        [sbtn('Criar versão','g_pl_new','doc','Criar uma nova versão como proposta'),
         imsg('Simular cobrança','500 ha · Produtor Piloto v3 → R$ 1.000/mês (R$ 2 × 500 > mínimo R$ 299; o piso usa o maior valor, não soma). Simulação rotulada como hipótese; nunca movimenta dinheiro real.','calc','Simular a mensalidade para uma área'),
         idrw('Vincular contrato',d_vinc,'users','Vincular um contratante a uma versão, com aceite'),
         msgbtn('Aprovar tabela','Produtor Piloto v4 não aprovada: franquia de IA sem quantidade definida — oferta não pode ser publicada com direitos ou franquias indefinidos. Para resolver: informe a quantidade da franquia na proposta e registre a decisão comercial do proprietário; depois aprove de novo.',primary=True)],g)
      + section('Matriz de direitos do trial','Confira a matriz de cada coorte antes de publicar a oferta; os valores seguem como hipótese de piloto.','',g_tm,state='yellow')
      + section('Regras desta área','Respeite estas regras ao publicar preços e confirmar pagamentos.','',
        texto(f'Preços em hipótese {B("não são publicáveis")} sem decisão comercial; os valores vigentes no piloto (R$ 2/ha·mês, mínimo R$ 299) continuam {B("hipótese")}, não tabela definitiva. '
              f'Confirmação de pagamento segue {B("evento validado do provedor, com idempotência")}. Consulta e fechamento seguro de trabalho já iniciado sobrevivem à expiração do trial.'),state='gray')
      + _priv())
    EXTRAJS[0]=BO1_JS
    shell37('BO-01','Planos e contratos da plataforma',corpo,ctx=CTX_BO,perfil=PERFIL_BO,
      subtitle='Área administrativa exclusiva da plataforma, com autorização e isolamento próprios; não aparece na navegação do agricultor.',
      status=('2 hipóteses aguardando decisão','yellow'),
      footer='Base de cobrança (área contratada × hectare ativo) é decisão comercial pendente: contrato, simulador e medição usam a mesma decisão versionada (57.2).')

def bo01det():
    fn='BO-01det.dc.html'; HEIGHTS37[fn]=1180; PARENT37[fn]='BO-01.dc.html'
    nf=lambda n: f'{n:,.0f}'.replace(',','.')
    prow=[]
    for a in (20,100,500,1000):
        sem=2*a; com=max(299,sem)
        prow.append(dict(id=f'a{a}',v=dict(area=a,sem=sem,com=com,anual=com*12,rha=round(com/a,2)),s={},p={},
            o=[dict(t=f'Sem mínimo: {nf(a)} ha × R$ 2 = R$ {nf(sem)}/mês'),
               dict(t=f'Com mínimo: maior entre R$ 299 e R$ {nf(sem)} = R$ {nf(com)}/mês'+(' (o mínimo cobre até 149,5 ha)' if com==299 else '')),
               dict(t=f'Recorrente anual: R$ {nf(com)} × 12 = R$ {nf(com*12)}'),dict(t='Fonte: Produtor Piloto v3 · preço de piloto · hipótese')]))
    g_par=grid([dict(k='area',l='Área contratada',t='num',a='r',u='ha'),dict(k='sem',l='Sem mínimo (R$/mês)',t='num',a='r',pre='R$ '),
                dict(k='com',l='Com mínimo R$ 299 (R$/mês)',t='num',a='r',pre='R$ '),dict(k='rha',l='Efetivo (R$/ha·mês)',t='num',a='r',d=2,pre='R$ '),
                dict(k='anual',l='Recorrente anual',t='num',a='r',pre='R$ ')],prow,
       edit=dict(m='origin',title='Mensalidade',fields=[dict(k='area',l='Área contratada',t='num',u='ha',ro=True),dict(k='com',l='Mensalidade com mínimo',t='num',u='R$/mês',ro=True)]),
       search=False,gid='g_par',total=False)
    CT=[('c1','Grupo Santa Rita','01/07/2026 – 30/06/2027',1165),('c2','Fazenda Aurora','01/08/2026 – 31/07/2027',60),
        ('c3','Sítio Ipê','01/08/2026 – 31/07/2027',20),('c4','Rancho Dois Rios','01/07/2026 – 30/09/2026 · cancelamento ao fim do ciclo',40)]
    g_ct=grid([dict(k='ctr',l='Contratante',w=200),dict(k='vig',l='Vigência',w=320),dict(k='area',l='Área contratada',t='num',a='r',u='ha'),dict(k='cons',l='Consulta do contratante')],
       [dict(id=i,v=dict(ctr=c,vig=vg,area=a,cons='Ver como o cliente vê'),s={},p=dict(ctr=[Pt.b(c)],cons=[Pt.cta('Ver como o cliente vê','CF-05.dc.html')])) for i,c,vg,a in CT],
       edit=dict(m='ro',title='Contrato',fields=[dict(k='ctr',l='Contratante',ro=True),dict(k='vig',l='Vigência',ro=True),dict(k='area',l='Área contratada',t='num',u='ha',ro=True)]),
       search=False,gid='g_ct',total=False)
    d_vinc=dd('Vincular contrato a Produtor Piloto v3','O aceite do contratante é registrado; sem cobrança retroativa.',
              [('Contratante',['Fazenda Três Marias','Organização Boa Esperança']),('Vigência início','01/10/2026')],'Vincular com aceite','Contrato vinculado · aceite registrado')
    corpo=(
      continuity('Tabelas de plano','Produtor Piloto v3 · vigente no piloto','decisão comercial do preço definitivo','Criar versão a partir desta')
      + section('Parâmetros da versão','Confira a mensalidade por área; clique na linha para ver a conta.',chip('Preço de piloto · hipótese','yellow'),g_par)
      + section('Base e franquias','Cobre a área física uma vez só, sem duplicar por safra, parcela sobreposta ou operação.','',
        texto(f'{B("Base:")} área física produtiva contratada, versionada, com extrato — pousio não cancela a cobrança; ampliação exige preço informado e aceite. A escolha entre área contratada e hectare ativo é {tag("hipótese · decisão pendente")}<br>'
              f'{B("Franquias:")} satélite 12 cenas/mês · IA 200 interações/mês · excedente por pacote aceito antes do uso {tag("hipótese de piloto")}<br>'
              f'{B("Comunicação:")} R$ 2/ha·mês sempre apresentado também como R$ 24/ha·ano, com o mínimo visível {chip(HIP,"yellow")}'),state='gray')
      + section('Contratos vinculados','Consulte os 4 contratos com evento no período (de 9 ativos) e veja cada um como o cliente vê.','',g_ct)
      + section('Decisão','Crie a próxima versão a partir desta; a vigência só encerra quando o último contrato migrar.','',
        acoes(imsg('Criar versão a partir desta','Produtor Piloto v5 criada como proposta, herdando os parâmetros da v3 — contratos vigentes intactos; preço segue hipótese até a decisão comercial.','doc','Criar proposta herdando os parâmetros',primary=True),
              idrw('Vincular contrato',d_vinc,'users','Vincular novo contratante a esta versão'),
              imsg('Encerrar vigência','Bloqueado: 9 contratos ativos vinculados. Para resolver: publique a versão substituta e colete o aceite de cada contrato; a vigência encerra quando o último migrar.','clock','Encerrar a vigência desta versão')))
      + _priv())
    shell37('BO-01','Produtor Piloto v3 · versão vigente',corpo,fname=fn,crumbs_extra=['Produtor Piloto v3'],ctx=CTX_BO,perfil=PERFIL_BO,
      subtitle='Versão vigente no piloto: os valores são hipótese comercial, não tabela definitiva; simuladores nunca movimentam dinheiro real.',
      status=('Vigente · 9 contratos','green'),
      footer='Alterações de preço não são retroativas: mudança futura gera nova vigência com aceite (cap. 57.5; PRECO-01/02/04).')

# =====================================================================================
BO2_JS=r'''
const BO_EF={Pago:'green',Pendente:'gray','Ação necessária':'yellow',Falhou:'red',Estornado:'gray',Cancelado:'gray'};
const BO_EV={'FAT-2209-016':{ok:true,ev:'evt_1JKT5'},'FAT-2209-015':{ok:false,why:'sem evento novo do provedor; tentativa 2 agendada para 25/09'},'FAT-2209-017':{ok:false,why:'aguarda a autenticação bancária adicional do pagador'}};
const BO_OPEN=['Pendente','Falhou','Ação necessária'];
function fat_R(self){ return g2rows(self,GRIDS.find(g=>g.id==='g_fat')); }
function PREVALS(self,v){ const rec=self.state.rec||{}; let n=0,s=0;
  fat_R(self).forEach(r=>{ const x=r.v; let e=x.e0, obs=x.o0;
    if(rec[x.fat] && BO_EV[x.fat] && BO_EV[x.fat].ok){ e='Pago'; obs=BO_EV[x.fat].ev+' validado · conciliado em 23/09 · idempotente'; }
    r.v.estado=e; r.s.estado=e; r.p.estado=[{k:'chip',t:e,c:BO_EF[e]||'gray'}]; r.v.obs=obs; r.s.obs=obs; r.p.obs=[{k:'txt',t:obs}];
    const open=BO_OPEN.indexOf(e)>=0; r.p.acao=open?[{k:'act',t:'Reconciliar',fn:'bo_rec:'+x.fat,u:e==='Falhou'}]:[{k:'mut',t:'—'}]; r.s.acao=open?'Reconciliar':'—';
    if(open){ n++; s+=Number(x.valor)||0; } });
  v.k_ab=String(n); v.k_abv='R$ '+(s/1000).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1})+' mil'; }
function EXTRAVALS(self,v){
  const run=(ids)=>{ const rec=Object.assign({},self.state.rec||{}); const pag=[],pend=[];
    ids.forEach(id=>{ const f=BO_EV[id]; if(!f) return; if(f.ok){ if(!rec[id]){ rec[id]=true; pag.push(id+' paga ('+f.ev+' validado)'); } } else pend.push(id+': '+f.why); });
    const m=[]; if(pag.length) m.push('Conciliada: '+pag.join(', ')+' · evento repetido será ignorado por idempotência'); if(pend.length) m.push('Sem conciliação: '+pend.join(' · '));
    self.setState({rec, g2toast:m.join(' · ')||'Nenhum evento novo · nada duplicado'}); };
  v.bo_rec=(id)=>run([id]);
  v.rec_all=()=>{ const open=fat_R(self).filter(r=>BO_OPEN.indexOf(r.v.estado)>=0).map(r=>r.v.fat);
    if(!open.length){ self.setState({g2toast:'Nenhuma fatura aberta · nada a conciliar'}); return; } run(open); };
}
'''
def bo02():
    fn='BO-02.dc.html'; HEIGHTS37[fn]=1060
    AS=[('s1','Grupo Santa Rita','Produtor Piloto v3','Ativa','green','renovação 01/07/2027 · exige aceite do preço','tok_····4242 · provedor'),
        ('s2','Fazenda Aurora','Produtor Piloto v3','Recuperação por falha','red','tentativa 2 de 3 em 25/09','tok_····8810 · atualização solicitada'),
        ('s3','Organização Boa Esperança','Trial agricultor v2','Trial','yellow',f'termina {TRIAL["fim"]} · sem cartão · sem dívida automática','— (cartão não exigido)'),
        ('s4','Coop. Verde Vale','Patrocínio Cooperativa v2','Ativa','green','fatura mensal dia 1 · pró-rata contratual','faturamento corporativo'),
        ('s5','Fertisul','Parceiro Profissional v1','Renovação com aceite','yellow','aceite do preço até 30/09','tok_····3307'),
        ('s6','Rancho Dois Rios','Produtor Piloto v3','Cancelamento ao fim do ciclo','gray','encerra 30/09 · exportação por 90 dias','token removido')]
    g_as=grid([dict(k='ctr',l='Contratante',w=210),dict(k='plano',l='Plano',w=190),dict(k='estado',l='Estado'),dict(k='prox',l='Próximo evento',w=300),dict(k='pag',l='Pagamento (token)',w=190)],
       [dict(id=i,v=dict(ctr=c,plano=p,estado=e,prox=x,pag=t),s={},p=dict(ctr=[Pt.link(c,'BO-02det.dc.html') if i=='s2' else Pt.b(c)],estado=[Pt.chip(e,cc)])) for i,c,p,e,cc,x,t in AS],
       edit=dict(m='ro',title='Assinatura',fields=[dict(k='ctr',l='Contratante',ro=True),dict(k='plano',l='Plano',ro=True),dict(k='estado',l='Estado',ro=True),dict(k='prox',l='Próximo evento',ro=True),dict(k='pag',l='Pagamento (token)',ro=True)]),
       search=False,gid='g_as',total=False,so={'k':'estado','d':False})
    g_fat=grid([dict(k='fat',l='Fatura'),dict(k='ctr',l='Contratante',w=190),dict(k='valor',l='Valor',t='num',a='r',pre='R$ '),dict(k='estado',l='Estado'),
                dict(k='obs',l='Confirmação / origem',w=330),dict(k='acao',l='Ação')],
       [dict(id=f,v=dict(fat=f,ctr=c,valor=val,e0=e,o0=o,estado=e,obs=o),s={},p=dict(fat=[Pt.b(f)])) for f,c,val,e,o in FATURAS],
       edit=dict(m='ro',title='Fatura',fields=[dict(k='fat',l='Fatura',ro=True),dict(k='ctr',l='Contratante',ro=True),dict(k='valor',l='Valor',t='num',u='R$',ro=True),dict(k='estado',l='Estado',ro=True),dict(k='obs',l='Confirmação / origem',t='area',ro=True)]),
       search=False,gid='g_fat',total=False)
    d_can=dd('Cancelar assinatura ao fim do ciclo','Sem cobrança nova; consulta e exportação seguem pela janela de retenção informada.',
             [('Contratante',['Fertisul','Grupo Santa Rita','Sítio Ipê','Coop. Verde Vale']),('Pedido do contratante (canal e data)',''),('Fim do ciclo','30/09/2026')],
             'Agendar cancelamento','Cancelamento agendado para o fim do ciclo · execução física em andamento não é interrompida')
    corpo=(
      kpis([('ASSINATURAS ATIVAS','14','pagantes'),('EM TRIAL','9',f'coorte {TRIAL["coorte"]}'),
            ('EM RECUPERAÇÃO','1','falha de pagamento'),('FATURAS ABERTAS',H('k_ab'),H('k_abv'))])
      + section('Assinaturas','Acompanhe o estado de cada assinatura; o cartão fica só como token do provedor.',
        [idrw('Cancelar ao fim do ciclo',d_can,'clock','Agendar cancelamento a pedido do contratante')],g_as)
      + section('Faturas e pagamentos do período','Reconcilie pelos eventos validados do provedor; o retorno visual do checkout não confirma pagamento.',
        [sbtn('Reconciliar pagamento','rec_all','check','Conciliar as faturas abertas com os eventos do provedor',primary=True)],g_fat)
      + _priv())
    EXTRAJS[0]=BO2_JS
    shell37('BO-02','Assinaturas e cobrança',corpo,ctx=CTX_BO,perfil=PERFIL_BO,
      subtitle='Trial, assinatura, fatura, tentativa, confirmação, estorno e cancelamento, sem armazenar cartão completo (token do provedor).',
      status=('1 em recuperação · 3 faturas abertas','yellow'),
      footer='Retentativas idempotentes não duplicam fatura ou pagamento; falha de cobrança não desliga máquinas nem cancela O.S. em execução (cap. 57.5; PRECO-08).')

def bo02det():
    fn='BO-02det.dc.html'; HEIGHTS37[fn]=900; PARENT37[fn]='BO-02.dc.html'
    TL=[('e1','Fatura FAT-2209-015 emitida','01/09','ciclo contratual (dia 1) · vence 20/09','Emitida','gray'),
        ('e2','Tentativa 1','20/09','provedor · evt_1JKR2','Falhou · cartão recusado','red'),
        ('e3','Aviso ao pagador + link de atualização','20/09','régua de recuperação contratual','Enviado (simulado)','green'),
        ('e4','Tentativa 2','25/09','provedor · agendada','Agendada','yellow'),
        ('e5','Tentativa 3 (última)','30/09','provedor · agendada','Agendada','gray')]
    g=grid([dict(k='ev',l='Evento',w=280),dict(k='dt',l='Data'),dict(k='orig',l='Origem',w=280),dict(k='res',l='Resultado')],
       [dict(id=i,v=dict(ev=e,dt=d_,orig=o,res=r),s={},p=dict(res=[Pt.chip(r,c)])) for i,e,d_,o,r,c in TL],
       edit=dict(m='ro',title='Evento da cobrança',fields=[dict(k='ev',l='Evento',ro=True),dict(k='dt',l='Data',ro=True),dict(k='orig',l='Origem',ro=True),dict(k='res',l='Resultado',ro=True)]),
       search=False,gid='g_tl',total=False)
    d_ac=dd('Acordo de regularização','Não altera a fatura emitida; gera um plano de recebimento vinculado.',
            [('Contratante',['Fazenda Aurora']),('Forma',['Boleto único','Pix','Novo cartão (token)']),('Vencimento','05/10/2026')],
            'Registrar acordo','Acordo registrado · a fatura permanece até a conciliação do recebimento')
    corpo=(
      continuity('Assinaturas','Recuperação por falha','tentativa 2 (25/09) ou cartão atualizado','Reconciliar pagamento')
      + section('Linha do tempo da cobrança','Acompanhe as três tentativas em dez dias; nenhuma tentativa duplica a fatura.','',g,state='red')
      + section('O que a falha não faz','Preserve a operação e os dados durante a recuperação.','',
        texto(f'Não desliga máquinas, não cancela O.S. em execução, não destrói registros. Sem regularização ao fim da régua: suspende {B("novas demandas pagas")}, '
              f'mantém consulta e exportação pela janela informada e o fechamento seguro do trabalho iniciado.'),state='gray')
      + section('Decisão','Reconcilie quando houver evento novo ou registre um acordo de regularização.','',
        acoes(imsg('Reconciliar pagamento','Sem evento novo do provedor para FAT-2209-015 — nada a conciliar; o retorno visual do checkout não confirma pagamento. Próxima tentativa: 25/09.','check','Conciliar com os eventos do provedor',primary=True),
              idrw('Registrar acordo de regularização',d_ac,'doc','Registrar plano de recebimento vinculado'),
              imsg('Cancelar ao fim do ciclo','Não disponível: a Fazenda Aurora não pediu cancelamento e falha de pagamento não cancela automaticamente. Para resolver: registre o pedido do contratante (canal e data) e então agende o cancelamento ao fim do ciclo.','clock','Cancelar só a pedido do contratante'),
              ilnk('Ver contrato do cliente','CF-05.dc.html','users','Abrir a consulta contratual do produtor')))
      + _priv())
    shell37('BO-02','Assinatura · Fazenda Aurora',corpo,fname=fn,crumbs_extra=['Fazenda Aurora'],ctx=CTX_BO,perfil=PERFIL_BO,
      subtitle='Recuperação por falha de pagamento com comunicação clara e tentativas idempotentes; contexto preservado após autenticação bancária.',
      status=('Recuperação · tentativa 2 em 25/09','red'),
      footer='Confirmação de pagamento só por evento validado e conciliação — página de sucesso do checkout não libera nada (cap. 58.4).')

# =====================================================================================
BO3_JS=r'''
const EM={Aberto:'gray',Conciliado:'green',Contestado:'red',Ajustado:'yellow',Aprovado:'green'};
function PREVALS(self,v){ const ok=!!self.state.aj9; let aj=0,ct=0;
  g2rows(self,GRIDS.find(g=>g.id==='g_med')).forEach(r=>{ const x=r.v; let e=x.e0, d=x.d0, dc=x.dc;
    if(r.id==='bv' && ok){ e='Aprovado'; d='AJ-009 aprovado · vigência out/2026 com aceite'; dc='green'; }
    r.v.estado=e; r.s.estado=e; r.p.estado=[{k:'chip',t:e,c:EM[e]||'gray'}]; r.s.div=d; r.p.div=(d==='—')?[{k:'mut',t:'—'}]:[{k:'chip',t:d,c:dc}];
    if(e==='Ajustado') aj++; if(e==='Contestado') ct++; });
  v.k_aj=String(aj); v.k_ajd=aj?'AJ-009 · alçada comercial':'nenhum pendente';
  v.k_div=String(aj+ct); v.k_divd=(ct?ct+' contestada':'')+(ct&&aj?' · ':'')+(aj?aj+' ajustada':'')||'nenhuma aberta'; }
function EXTRAVALS(self,v){
  v.aj9_fn=()=>{ if(self.state.aj9){ self.setState({g2toast:'Nenhum ajuste a aprovar: a contestação da Fazenda Aurora segue em revisão na memória de cálculo.'}); return; }
    self.setState({aj9:true,g2toast:'AJ-009 (Agro Bela Vista, +13 ha) aprovado após retorno à conciliação · vigência a partir de out/2026 com aceite — medição de set já faturada não foi reescrita; ajuste vinculado ao período.'}); }; }
'''
def bo03():
    fn='BO-03.dc.html'; HEIGHTS37[fn]=900
    rows=[]
    for i,c,base,ctr,med,fr,e,div,dc,orig in MEDICAO:
        o=[dict(t=x) for x in orig]+([dict(t='Abrir memória de cálculo e contestação',h='BO-03det.dc.html')] if i=='fa' else [])
        rows.append(dict(id=i,v=dict(ctr=c,base=base,cm=f'{ctr} → {med}',fr=fr,e0=e,estado=e,d0=div,dc=dc,div=div),s=dict(ctr=f'{c} {base}'),
             p=dict(ctr=[Pt.b(c),Pt.br(),Pt.mut(base)],acao=([Pt.cta('Revisar divergência','BO-03det.dc.html',True)] if i=='fa' else [{'k':'mut','t':'—'}])),o=o))
    g=grid([dict(k='ctr',l='Contratante e base',w=200),dict(k='cm',l='Contratada → medida',w=190),dict(k='fr',l='Franquias usadas',w=190),dict(k='estado',l='Estado'),
            dict(k='div',l='Divergência',w=240),dict(k='acao',l='Ação')],rows,
       edit=dict(m='origin',title='Medição set/2026',fields=[dict(k='ctr',l='Contratante',ro=True),dict(k='cm',l='Contratada → medida',ro=True),dict(k='estado',l='Estado',ro=True)]),
       search=False,gid='g_med',total=False)
    corpo=(
      kpis([('PERÍODO','set/2026','fecha 30/09'),('ÁREA MEDIDA','21,2 mil ha','deduplicada por contratante'),
            ('DIVERGÊNCIAS',H('k_div'),H('k_divd')),('AJUSTES A APROVAR',H('k_aj'),H('k_ajd'))])
      + section('Medição do período por contratante','Clique no contratante para ver a memória de cálculo; revise a contestação e aprove o ajuste pendente.',
        [imsg('Comparar contrato','Fazenda Aurora: o contrato usa área contratada (60 ha); a ocupação apurada é 35 ha. Mensalidade igual nas duas bases (mínimo R$ 299 prevalece) · a escolha da base segue hipótese, com decisão comercial pendente.','scale','Comparar a base do contrato com a medição'),
         sbtn('Aprovar ajuste','aj9_fn','check','Aprovar o ajuste AJ-009 da Agro Bela Vista',primary=True)],g)
      + section('Regra do período','Mantenha a medição faturada intacta: divergência posterior vira ajuste ou crédito no período seguinte.','',
        texto(f'Contestação abre revisão (estado contestado); ajuste documentado {B("retorna à conciliação")} antes da aprovação, com a alçada aplicável. '
              f'Memória de cálculo e origem preservadas; duas safras na mesma área contam uma vez.'),state='gray')
      + _priv())
    EXTRAJS[0]=BO3_JS
    shell37('BO-03','Medição e conciliação comercial',corpo,ctx=CTX_BO,perfil=PERFIL_BO,
      subtitle='Área contratada deduplicada, carteira patrocinada, direitos cobertos, franquias, eventos medidos e ajustes com origem.',
      status=('1 contestação aberta','yellow'),
      footer='Extrato da base acompanha cada fatura: hectares não são duplicados por safra, parcela sobreposta ou operação (PRECO-02/04).')

BO3D_JS=r'''
const LC=['Aberto','Conciliado','Contestado','Ajustado · volta à conciliação','Aprovado'];
function PREVALS(self,v){ const s=self.state;
  g2rows(self,GRIDS.find(g=>g.id==='g_aj')).forEach(r=>{ const e=s.apr?['Aprovado','green']:(s.ajr?['Registrado · período conciliado','yellow']:['A registrar','gray']);
    r.p.estado=[{k:'chip',t:e[0],c:e[1]}]; r.s.estado=e[0]; r.ro=!!s.apr; }); }
function EXTRAVALS(self,v){ const s=self.state; const cur=s.apr?4:(s.ajr?3:2);
  LC.forEach((t,i)=>{ const on=(i===cur), done=(i<cur);
    v['lc'+i+'_st']='display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:999px;font-size:12.5px;font-weight:'+(on?'800':'600')+';'+(on?'background:#E4F3E9;color:#1E7A4C;box-shadow:inset 0 0 0 1.5px #1E7A4C;':(done?'background:#EEF1EE;color:#15201A;':'background:transparent;color:#8A968E;border:1px dashed #D5DCD7;'));
    v['lc'+i+'_t']=(done?'✓ ':'')+t; });
  v.lc_aqui=['Contestado','Contestado','Contestado','Ajustado · conciliado','Aprovado'][cur];
  v.lc_falta=!s.ajr?'ajuste documentado · retorno à conciliação':(!s.apr?'aprovação da alçada comercial':'nada neste período');
  const SC={2:['Contestado desde 18/09','#B42318','#FDE8E6'],3:['Ajustado · aguarda aprovação','#8A5A00','#FFF3D6'],4:['Aprovado · set/2026','#1E7A4C','#E4F3E9']}[cur];
  v.st_t=SC[0]; v.st_st='display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+SC[1]+';background:'+SC[2]+';';
  v.st_dot='width:6px;height:6px;border-radius:999px;background:'+SC[1]+';';
  v.prim_t=!s.ajr?'Registrar ajuste com origem':(!s.apr?'Aprovar ajuste':'Ajuste aprovado');
  v.prim_st=s.apr?PSTOFF:PST;
  v.aj_why=!s.ajr?'Aprovar ajuste fica disponível depois de registrar o ajuste: o período está contestado.':(!s.apr?'Período conciliado · aprovação pela alçada comercial.':'Medição set/2026 aprovada · resposta ao contratante com a memória de cálculo (simulado · nenhuma mensagem real enviada).');
  v.prim_fn=()=>{ const st=self.state;
    if(!st.ajr){ g2open(self,GRIDS.find(g=>g.id==='g_aj'),'aj10',null); return; }
    if(!st.apr){ self.setState({apr:true,g2toast:'AJ-010 aprovado (R$ 0) · medição set/2026 da Fazenda Aurora aprovada · fatura fechada não foi reescrita; mudança de base segue decisão comercial pendente.'}); return; }
    self.setState({g2toast:'Ajuste já aprovado · nada a fazer neste período'}); };
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_aj'||!r) return;
    if(String(r.v.tipo).indexOf('Mudança de base')===0){ r.v.tipo='Ajuste documental sem efeito financeiro'; r.s.tipo=r.v.tipo;
      self.setState({g2toast:'Mudança de base não se resolve nesta medição: é decisão comercial pendente em Planos e contratos. Tipo mantido como ajuste documental; o ajuste não foi registrado.'}); return; }
    const val=Number(r.v.valor)||0;
    self.setState({ajr:true,g2toast:'AJ-010 registrado (R$ '+val.toLocaleString('pt-BR')+') · período volta a conciliado'+(val>0?' · crédito vinculado ao período seguinte':'')+' · aprovação pela alçada comercial'}); }; }
'''
def bo03det():
    fn='BO-03det.dc.html'; HEIGHTS37[fn]=1180; PARENT37[fn]='BO-03.dc.html'
    MEM=[('m1','Área contratada','contrato v1 · aceite 01/08/2026','60 ha','Sim · base vigente','green','base contratual desta vigência'),
         ('m2','Área ocupada apurada','polígonos validados · versão 12/09','35 ha','Não · base é contratada','gray','a contestação pede cobrança pela ocupação'),
         ('m3','Sobreposição T2 × T3','geometria · justificativa pendente','2 ha','Excluída da soma','green','sobreposições não duplicam hectares'),
         ('m4','2ª safra na mesma área','ciclo 2026/27','35 ha','Não conta de novo','green','deduplicação por área física'),
         ('m5','Cenas de satélite','provedor · extrato de consumo','2 de 12','Franquia · sem excedente','green','—'),
         ('m6','Mensalidade resultante','Produtor Piloto v3 (preço de piloto · hipótese)','R$ 299','Igual nas duas bases','green','60 ha × R$ 2 = R$ 120 e 35 ha × R$ 2 = R$ 70 → mínimo R$ 299 prevalece')]
    g_mem=grid([dict(k='par',l='Parcela',w=200),dict(k='fonte',l='Fonte e versão',w=260),dict(k='val',l='Valor',a='r'),dict(k='base',l='Entra na base?'),dict(k='obs',l='Observação',w=320)],
       [dict(id=i,v=dict(par=p,fonte=f,val=val,base=b,obs=o),s={},p=dict(par=[Pt.b(p)] if i=='m6' else [Pt.txt(p)],val=[Pt.b(val)] if i=='m6' else [Pt.txt(val)],base=[Pt.chip(b,c)]),
             o=[dict(t=f'Fonte: {f}'),dict(t=f'Valor: {val} · {b.lower()}')]+([dict(t=o)] if o!='—' else [])) for i,p,f,val,b,c,o in MEM],
       edit=dict(m='origin',title='Parcela da memória',fields=[dict(k='par',l='Parcela',ro=True),dict(k='val',l='Valor',ro=True)]),
       search=False,gid='g_mem',total=False)
    TIPOS=['Ajuste documental sem efeito financeiro','Crédito no período seguinte','Mudança de base (exige decisão comercial)']
    g_aj=grid([dict(k='aj',l='Ajuste'),dict(k='tipo',l='Tipo',w=260),dict(k='valor',l='Valor',t='num',a='r',pre='R$ '),dict(k='origem',l='Origem',w=320),dict(k='estado',l='Estado')],
       [dict(id='aj10',v=dict(aj='AJ-010 · contestação 18/09',tipo=TIPOS[0],valor=0,origem='contestação 18/09 + decisão de base pendente em Planos e contratos',
             resp='Contratamos 60 ha; a mensalidade é R$ 299 nas duas bases (mínimo prevalece). A mudança de base segue decisão comercial.'),s={},p=dict(aj=[Pt.b('AJ-010 · contestação 18/09')]))],
       edit=dict(m='form',title='Ajuste da medição',sub='Registre o ajuste com origem; o período volta à conciliação. Diferença em período faturado vira crédito vinculado, sem reescrever a fatura.',
            fields=[dict(k='aj',l='Ajuste',ro=True),dict(k='tipo',l='Tipo',t='sel',opts=TIPOS,req=True),dict(k='valor',l='Valor',t='num',req=True,min=0,u='R$',help='R$ 0: o mínimo de R$ 299 prevalece nas duas bases.'),
                    dict(k='origem',l='Origem',t='area',req=True),dict(k='resp',l='Resposta ao contratante',t='area',req=True)]),
       search=False,gid='g_aj',total=False)
    lc=f'<span style="color: {MUTED};">›</span>'.join(f'<span style="{H(f"lc{i}_st")}">{H(f"lc{i}_t")}</span>' for i in range(5))
    corpo=(
      continuity('Medição set/2026',H('lc_aqui'),H('lc_falta'),H('prim_t'))
      + f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">{lc}</div>'
      + section('Memória de cálculo','Clique na parcela para ver fonte e versão; nada é recalculado silenciosamente.','',g_mem)
      + section('Contestação do contratante','Responda com a memória de cálculo; a mudança de base se decide em Planos e contratos.','',
        texto(f'Aberta em 18/09 pela Fazenda Aurora na consulta contratual: “Contratamos 60 ha mas ocupamos 35 ha; pedimos medição pela ocupação.” '
              f'Nesta versão a diferença não altera a mensalidade (o mínimo de R$ 299 prevalece nas duas bases). A mudança de base (contratada × ativa) é {B("decisão comercial pendente")} — '
              f'não se resolve reescrevendo esta medição {chip(HIP,"yellow")}'),state='red')
      + section('Ajuste da medição','Registre o ajuste com origem na linha; o período volta à conciliação e então pode ser aprovado.',
        ilnk('Ver contrato do cliente','CF-05.dc.html','users','Abrir a consulta contratual do produtor'),
        g_aj+f'<div style="display: flex; align-items: center; gap: 8px; margin-top: 10px; font-size: 12.5px; color: {MUTED};">{icon("alert",14,YEL)}<span>{H("aj_why")}</span></div>')
      + _priv())
    EXTRAJS[0]=f'const PST={PST}; const PSTOFF={PSTOFF};\n'+BO3D_JS
    shell37('BO-03','Medição · Fazenda Aurora (set/2026)',corpo,fname=fn,crumbs_extra=['Fazenda Aurora · contestação'],ctx=CTX_BO,perfil=PERFIL_BO,
      subtitle='Memória de cálculo com origem por parcela; contestação não reescreve fatura fechada — gera ajuste ou crédito vinculado.',
      status=('Contestado desde 18/09','red'),
      primary_html=f'<button type="button" onClick="{H("prim_fn")}" style="{H("prim_st")}">{H("prim_t")}</button>',
      footer='Aprovar sem retorno à conciliação é impossível por regra de estado; alçada e vigência acompanham o ajuste (PRECO-02/04).')
    # selo do cabeçalho acompanha o estado do período (Contestado → Ajustado → Aprovado)
    import os, engine as E
    fp=os.path.join(E.P,fn); html_=open(fp).read(); stc=chip('Contestado desde 18/09','red')
    assert stc in html_, 'selo do cabeçalho não encontrado'
    open(fp,'w').write(html_.replace(stc,f'<span style="{H("st_st")}"><span style="{H("st_dot")}"></span>{H("st_t")}</span>',1))

# =====================================================================================
def bo04():
    fn='BO-04.dc.html'; HEIGHTS37[fn]=1000
    pct=lambda a,n: f'{round(100*a/n)}%'
    rows=[]
    for i,co,perf,n,at,pg,rt,rec,sup in COORTES:
        parcial=(co=='set/2026')
        ativ=pct(at,n)+(' (parcial)' if parcial and perf.startswith('Agricultor') else '')
        conv=('em trial' if pg is None else ('contratada' if perf.startswith('Cooperativa') else pct(pg,n)))
        ret=('—' if rt is None else pct(rt,n))
        o=[dict(t=f'Contas da coorte: {n} · eventos confirmados de assinaturas, cobrança e medição'),
           dict(t=f'Ativação: {at} de {n} contas com a primeira tarefa útil (login sozinho não conta)'),
           dict(t=('Conversão: coorte ainda em trial até 18/10' if pg is None else f'Conversão: {pg} de {n} contas pagantes (BO-02)')),
           dict(t=('Retenção 90 d: ainda sem 90 dias de observação' if rt is None else f'Retenção 90 d: {rt} de {n} contas ativas após 90 dias'))]
        if i=='c2': o.append(dict(t='Abandono: as 2 contas não ativadas pararam na Importação (erros de prévia sem correção)',h='ON-01det.dc.html'))
        rows.append(dict(id=i,v=dict(co=co,perf=perf,n=n,ativ=ativ,conv=conv,ret=ret,rec=rec,sup=sup),s={},p=dict(co=[Pt.b(co)]),o=o))
    g=grid([dict(k='co',l='Coorte'),dict(k='perf',l='Perfil',w=200),dict(k='n',l='Contas',t='num',a='r'),dict(k='ativ',l='Ativação',a='r'),dict(k='conv',l='Conversão trial → pago',a='r'),
            dict(k='ret',l='Retenção 90 d',a='r'),dict(k='rec',l='Receita/conta·mês',a='r'),dict(k='sup',l='Suporte h/conta',a='r')],rows,
       edit=dict(m='origin',title='Coorte',fields=[dict(k='co',l='Coorte',ro=True),dict(k='perf',l='Perfil',ro=True),dict(k='ativ',l='Ativação',ro=True)]),
       search=False,gid='g_co',total=False)
    d_exp=dd('Criar experimento de ativação','Cadastro separado; não altera retroativamente métricas nem contratos.',
             [('Nome','Assistência de importação no trial'),('Coorte de destino',['out/2026 · HF/frutas','out/2026 · grãos','out/2026 · fornecedores']),
              ('Métrica de sucesso','primeira tarefa útil em 10 min'),('Período','30 dias')],
             'Criar experimento','EXP-07 criado · medição começa na próxima coorte · métricas passadas intactas')
    corpo=(
      kpis([('RECEITA RECORRENTE · MÊS','R$ 38,2 mil','reconhecida'),('CANCELAMENTO · MÊS','2,1%','das contas'),
            ('RETORNO DO CAC','9,8','meses'),('MARGEM DE CONTRIBUIÇÃO','68%','')])
      + section('Coortes por perfil','Clique na coorte para ver os eventos que formam cada taxa; login sozinho não conta como ativação.',
        [imsg('Rastrear receita/custo','Trilha aberta: receita recorrente de set/2026 decomposta em 14 assinaturas conciliadas (Assinaturas e cobrança) e custo direto por conta (nuvem, IA, suporte) — cada valor com evento e período de origem.','trend','Decompor receita e custo por origem'),
         imsg('Investigar abandono','Coorte ago/2026 · HF/frutas: 2 de 6 contas não ativaram — ambas pararam na etapa Importação da implantação guiada, com erros de prévia sem correção. Hipótese a testar: assistência de mapeamento.','alert','Ver onde as contas pararam'),
         idrw('Criar experimento',d_exp,'lab','Cadastrar experimento de ativação')],g)
      + section('Método e período','Leia as definições antes de comparar números; sem definição, o número não aparece.',
        [ilnk('Ver contrato do produtor','CF-05.dc.html','users','Consulta contratual do produtor'),ilnk('Ver portal do parceiro','PT-07.dc.html','users','Consulta contratual do parceiro')],
        texto(f'{B("Período:")} set/2026 (parcial até {D.HOJE[:5]}) · eventos confirmados de assinaturas, cobrança e medição; métrica simulada nunca entra como produção.<br>'
              f'{B("Ativação:")} agricultor = plano utilizável com próximos passos · fornecedor = cotação respondida · comprador = solicitação válida.<br>'
              f'{B("Contribuição:")} receita líquida − custos diretos variáveis e atribuídos; ponto de equilíbrio = fixos ÷ margem — a mesma folha de suporte não é deduzida duas vezes.<br>'
              f'{B("LTV:")} não exibido — retenção observada insuficiente (base pequena); sem perpetuidade fictícia.'),state='gray')
      + _priv())
    shell37('BO-04','Economia e crescimento da plataforma',corpo,ctx=CTX_BO,perfil=PERFIL_BO,
      subtitle='Receita recorrente, conversão, ativação, cancelamento, CAC, margem e suporte por coorte e perfil — painel de leitura, sem máquina de estados própria.',
      status=('Período set/2026 · parcial','gray'),
      footer='Criar experimento abre cadastro separado; nenhuma ação daqui altera métricas, contratos ou faturas retroativamente (PRECO-05).')

def build():
    on01(); on01det(); bo01(); bo01det(); bo02(); bo02det(); bo03(); bo03det(); bo04()
