# -*- coding: utf-8 -*-
"""Verificador independente · Compra (itens 01, 05, 06): falta calculada à parte, convite adicional, canais, avisos da etapa 6."""
import time, datetime as dt, json
import dados2 as D
from verif_ce_lib import V
v=V('CMP.dc.html'); J=v.J
HOJE=dt.date(2026,9,23)
def br(s): d,m,a=s.split('/'); return dt.date(int(a),int(m),int(d))
# ---- cálculo independente (sem demanda_datada/faltas do implementador)
occ={}
for c in D.CULTIVOS['S2627']:
    if not c['plano']: continue
    for a in D.PLANO[c['plano']]['atividades']:
        d=D.data_atividade(c,a)
        for i,p in enumerate(a['prods']):
            dose=D.AJUSTES.get(c['id'],{}).get(f"{a['id']}|{i}",p['dose'])
            occ.setdefault(D.prod_nome(p['prod'],c),[]).append((d,dose*c['area']))
def falta(n,prevs=None,excl=None):
    ent=[(br((prevs or {}).get(p['id'],p['previsao'])),p['a_entregar']) for p in D.PEDIDOS if p['item']==n and p['a_entregar'] and p['id']!=excl]
    ac=0
    for d in sorted(set(x for x,_ in occ[n])):
        ac+=sum(q for x,q in occ[n] if x==d)
        if ac>D.ESTOQUE.get(n,0)+sum(q for x,q in ent if x<=d)+1e-9: return d
    return None
FN={f['id']:f['nome'] for f in D.FORNECEDORES}
try:
    v.open(); v.chk('sem erro JS', J("window.__err||'nenhum'")=='nenhum', J("window.__err||''"))
    v.clk('Abrir compra'); v.clk('Expandir tudo')
    dem=D.demanda('S2627')
    for n in sorted(occ):
        f=falta(n); t=v.rowtxt(n); exp=f.strftime('%d/%m/%Y') if f else '—'
        seg=t.split(n,1)[1]; seg=seg.split(' kg ',1)[1] if dem[n]['un']=='kg' else seg.split(' L ',1)[1]
        v.chk(f'E2 {n}: falta {exp}', seg.startswith(exp), t[:170])
    # grupo mostra a primeira falta dos seus insumos
    for g in sorted(set(o['grupo'] for o in dem.values())):
        fs=[falta(n) for n,o in dem.items() if o['grupo']==g and falta(n)]
        t=J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2r')].find(r=>!r.classList.contains('g2kid')&&r.innerText.replace(/\\s+/g,' ').replace(/^[\\s▾▸]+/,'').startsWith({json.dumps(g)})); return r?r.innerText.replace(/\\s+/g,' '):'';}})()")
        exp=min(fs).strftime('%d/%m/%Y') if fs else None
        v.chk(f'E2 grupo {g}: {exp}', (exp in t) if exp else ('/20' not in t), t[:140])
    v.row('Fungicida A'); a=v.aside()
    ls=[l for l in a.split('\n') if len(l)>12 and l[2]=='/' and l[5]=='/']
    ds=[dt.date(int(l[6:10]),int(l[3:5]),int(l[:2])) for l in ls]
    v.chk('origem Fungicida A: todas as linhas de atividade começam pela data, em ordem', ds==sorted(ds) and len(ls)==len(occ['Fungicida A']), ls)
    v.chk('origem T1-B com dose ajustada 0,60', any('T1-B' in l and '0,60 L/ha' in l for l in ls), ls)
    v.clk('Fechar','aside[role=dialog]')
    # ---------- etapa 3: canais ----------
    v.clk('Solicitar cotações')
    t=v.kid('Inoculantes','Casa do Adubo'); v.chk('linha Casa do Adubo (Inoculantes) mostra E-mail e o e-mail', 'E-mail' in t and 'vendas@casadoadubo.com.br' in t and 'WhatsApp' not in t, t)
    v.kid('Inoculantes','Casa do Adubo',True); v.chk('Casa do Adubo em Inoculantes: só E-mail', v.opts('canal')==['E-mail'], v.opts('canal'))
    s=v.sub(); v.chk('subtítulo Inoculantes: destinatário e itens do grupo', 'Destinatário: e-mail vendas@casadoadubo.com.br (Juliana Prado)' in s and 'Itens do convite (Inoculantes): Inoculante líquido · 72 L' in s, s)
    v.setv('#'+v.fid('conv'),'Não convidar'); s=v.sub(); print('  sub com Não convidar:', s)
    v.clk('Cancelar','aside[role=dialog]'); v.clk('Descartar','aside[role=dialog]')
    # Fungicidas: só a Coop. Vale (sem proposta nos dados) é convidada
    for f in ['Agro Norte','Santa Rita Insumos']:
        v.kid('Fungicidas',f,True); v.setv('#'+v.fid('conv'),'Não convidar'); v.clk('Salvar','aside[role=dialog]'); print('  ',f,'→',v.T())
    print('  enviar:', v.clk('Enviar convites (simulado)'), v.T()); time.sleep(8)
    k3=J("document.body.innerText.match(/Convites simulados[^\\n]+/)"); print('  k3:', k3)
    v.chk('13 convites (Fungicidas só com a Coop. Vale)', k3 and 'de 13 convites' in k3[0], k3)
    t=v.kid('Fungicidas','Coop. Vale'); v.chk('Coop. Vale: sem resposta', 'Sem resposta' in t, t)
    # etapa 4: insumos de Fungicidas sem proposta, aviso aponta a etapa 3
    v.clk('Comparar propostas'); v.clk('Expandir tudo')
    t=v.rowtxt('Fungicida TS'); v.chk('Fungicida TS sem proposta', 'Sem proposta' in t, t)
    v.row('Fungicida TS'); tt=v.T(); v.chk('aviso sem proposta cita etapa 3, os homologados livres e o botão', 'etapa 3' in tt and 'Agro Norte' in tt and 'Santa Rita Insumos' in tt and 'Enviar convites adicionais' in tt, tt)
    # etapa 4: escolha padrão e selos para todos os insumos com proposta
    import re
    for n in sorted(D.sol_itens()):
        g=dem[n]['grupo']; f=falta(n)
        props=[p for p in D.PROPOSTAS.get(g,[]) if not (g=='Fungicidas')]
        if not props: continue
        un=dem[n]['un']; fob={'kg':0.15,'L':0.40}[un]
        cs=[]
        for p in props:
            preco=round(dem[n]['preco']*p['fator']*100)/100; unit=preco+(fob if p['frete']=='FOB' else 0)
            ch=HOJE+dt.timedelta(days=p['prazo']); cs.append((unit,FN[p['f']],ch,bool(f and ch>f)))
        cs.sort(); low=cs[0]; ref=next((x for x in cs if not x[3]),low)
        t=v.rowtxt(n)
        v.chk(f'E4 {n}: padrão {ref[1]}', ref[1] in t.split('dias')[-1] and ('Menor custo total' in t if ref is low else 'Menor custo a tempo' in t), t[:220])
        for x in cs:
            k=v.after(n,x[1]); late_chip='Chega depois da falta' in k
            v.chk(f'   {n} · {x[1]}: chega {x[2].strftime("%d/%m")} late={x[3]}', ('chega '+x[2].strftime('%d/%m')) in k and late_chip==x[3], k[:200])
    # ---------- convite adicional (antes da aprovação) ----------
    v.clk('3 Solicite cotações')
    print('  clique Fertisul (já convidado):', v.kid('Fertilizantes','Fertisul',True), '| form?', J("!!document.querySelector('aside[role=dialog]')"), v.T())
    v.chk('já convidado: só consulta (sem formulário)', not J("!!document.querySelector('aside[role=dialog]')") and 'Nenhuma mensagem real' in v.T())
    v.kid('Fungicidas','Agro Norte',True); s=v.sub(); v.chk('não convidado abre Convite com aviso de convite adicional', s.startswith('Convite adicional') and 'Itens do convite (Fungicidas)' in s, s)
    v.setv('#'+v.fid('conv'),'Convidar'); v.clk('Salvar','aside[role=dialog]'); print('  salvar:', v.T())
    p=v.prim(); v.chk('primária: Enviar 1 convite adicional (simulado)', 'Enviar 1 convite adicional (simulado)' in p, p)
    t=J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2r')].find(r=>!r.classList.contains('g2kid')&&/^[\\s▾▸]*Fungicidas/.test(r.innerText)); return r?r.innerText.replace(/\\s+/g,' '):'';}})()")
    v.chk('grupo Fungicidas mostra +1 a enviar', '+1 a enviar' in t, t)
    v.clk('Enviar 1 convite adicional (simulado)'); tt=v.T(); print('  adicional:', tt); time.sleep(3)
    k3=J("document.body.innerText.match(/Convites simulados[^\\n]+/)"); print('  k3:', k3)
    v.chk('14 convites, 1 adicional, sem reenvio', k3 and 'de 14 convites' in k3[0] and '1 adicional' in k3[0], k3)
    t=v.kid('Fungicidas','Agro Norte'); v.chk('Agro Norte (Fungicidas): proposta recebida', 'Proposta recebida' in t, t)
    v.kid('Fungicidas','Agro Norte',True); tt=v.T(); v.chk('Agro Norte agora é consulta (horário do convite adicional)', not J("!!document.querySelector('aside[role=dialog]')") and 'Convite simulado enviado a Agro Norte' in tt and '10:47' not in tt, tt)
    # marca Santa Rita (Fungicidas) mas não envia; depois aprova a compra
    v.kid('Fungicidas','Santa Rita Insumos',True); v.setv('#'+v.fid('conv'),'Convidar'); v.clk('Salvar','aside[role=dialog]')
    # etapa 4: escolhe a atrasada (Santa Rita) no 2,4-D com justificativa
    v.clk('4 Compare propostas'); v.clk('Expandir tudo')
    v.J("""(()=>{const rows=[...document.querySelectorAll('[role=row].g2r')]; const i=rows.findIndex(r=>r.innerText.indexOf('2,4-D 806')>=0); const k=rows.slice(i+1).find(r=>r.innerText.indexOf('Santa Rita')>=0); (k.querySelector('[role=cell] span')||k).click();})()"""); time.sleep(.5)
    v.setv('#'+v.fid('just'),'Agro Norte sem estoque confirmado'); v.clk('Salvar','aside[role=dialog]'); print('  escolha:', v.T())
    k4=J("document.body.innerText.match(/\\d+ propostas · custo total[^\\n]+/)"); v.chk('k4 conta 1 escolha que chega depois da falta', k4 and '1 escolha chega depois da falta' in k4[0], k4)
    v.clk('Revisar aprovação'); print('  enviar Direção:', v.clk('Enviar à Direção'), v.T())
    print('  aprovar:', v.clk('Registrar aprovação da Direção'), v.T())
    # depois da aprovação
    v.clk('3 Solicite cotações')
    t=J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2r')].find(r=>!r.classList.contains('g2kid')&&/^[\\s▾▸]*Fungicidas/.test(r.innerText)); return r?r.innerText.replace(/\\s+/g,' '):'';}})()")
    v.chk('aprovada: grupo Fungicidas não anuncia convite a enviar', '+1 a enviar' not in t, t)
    t=v.kid('Fungicidas','Santa Rita Insumos'); print('  Santa Rita (Fungicidas) após aprovação:', t)
    v.chk('aprovada: linha não convidada não diz Convidar', 'Convidar' not in t.replace('Não convidado',''), t)
    v.kid('Fungicidas','Santa Rita Insumos',True); tt=v.T(); v.chk('aprovada: clique mantém o aviso', not J("!!document.querySelector('aside[role=dialog]')") and 'não foi convidado' in tt, tt)
    p=v.prim(); v.chk('aprovada: primária não oferece convite adicional', 'adicional' not in p, p)
    k3=J("document.body.innerText.match(/Convites simulados[^\\n]+/)"); v.chk('aprovada: k3 sem convite a enviar', k3 and 'a enviar' not in k3[0], k3)
    v.shot('ce_cmp_e3_aprovada.png')
    # ---------- etapa 6 ----------
    v.clk('6 Acompanhe a entrega'); v.clk('Expandir tudo')
    t=v.rowtxt('Santa Rita Insumos'); print('  PC Santa Rita:', t)
    v.chk('PC com a escolha atrasada mostra Chega depois da falta (28/09)', 'Chega depois da falta (28/09)' in t, t)
    def reprog(pid,data):
        r=J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(pid)})>=0); if(!r) return 'sem'; (r.querySelector('[role=cell] b')||r).click(); return 'ok';}})()"""); time.sleep(.4)
        v.setv('#'+v.fid('prev'),data); v.setv('#'+v.fid('obs'),'teste'); v.clk('Salvar','aside[role=dialog]'); return v.T()
    pcsr=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>/PC-1\\d\\d/.test(r.innerText)&&r.innerText.indexOf('Santa Rita')>=0); return r?r.innerText.match(/PC-1\\d\\d/)[0]:'';})()")
    tt=reprog(pcsr,'2026-09-27'); t=v.rowtxt(pcsr); v.chk(f'{pcsr} reprogramado para 27/09: sem aviso', 'falta' not in t.lower() and 'Atenção' not in tt, t+' | '+tt)
    tt=reprog(pcsr,'2026-09-29'); t=v.rowtxt(pcsr); v.chk(f'{pcsr} para 29/09: Nova data depois da falta de 28/09', 'Nova data depois da falta de 28/09' in t and 'Atenção' in tt, t+' | '+tt)
    tt=reprog(pcsr,'2026-09-28'); t=v.rowtxt(pcsr); v.chk(f'{pcsr} para 28/09 (dia da falta): sem aviso', 'Nova data' not in t, t)
    for pid,ok,late,fw in [('PC-090','2026-10-18','2026-10-19','18/10'),('PC-091','2026-10-25','2026-10-26','25/10'),('PC-088','2026-11-07','2026-11-08','07/11')]:
        tt=reprog(pid,late); t=v.rowtxt(pid); v.chk(f'{pid} depois da falta: aviso {fw}', f'Nova data depois da falta de {fw}' in t and 'Atenção' in tt, t[:230]+' | '+tt)
        tt=reprog(pid,ok); t=v.rowtxt(pid); v.chk(f'{pid} no dia {ok}: sem aviso', 'Nova data' not in t and 'Atenção' not in tt, t[:230])
    tt=reprog('PC-090','2026-10-20'); t=v.rowtxt('PC-090')
    v.clk('2 Confira a demanda'); v.clk('Expandir tudo'); t=v.rowtxt('Semente de soja 58 W')
    v.chk('E2: 58 W com PC-090 em 20/10 mostra 18/10/2026 e o aviso', '18/10/2026' in t and 'chega depois da falta' in t, t)
    v.clk('6 Acompanhe a entrega')
    r=J("""(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('PC-091')>=0); (r.querySelector('[role=cell] b')||r).click(); return 'ok';})()"""); time.sleep(.4)
    v.setv('#'+v.fid('prev'),'2026-09-20'); v.clk('Salvar','aside[role=dialog]'); v.chk('data passada é recusada', 'a partir de hoje' in v.errs(), v.errs())
    v.clk('Cancelar','aside[role=dialog]'); v.clk('Descartar','aside[role=dialog]')
    v.shot('ce_cmp_e6.png')
    v.chk('sem erro JS no fim', J("window.__err||'nenhum'")=='nenhum', J("window.__err||''"))
finally:
    v.close()
