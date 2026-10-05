# -*- coding: utf-8 -*-
"""Teste CDP · REND-MULTICONJUNTOS-20261003 no Planejar safra (SAF.dc.html), Safra 2026/27 · Santa Rita.
Defina os rendimentos e Confira o plano operacional com vários conjuntos de tamanhos/rendimentos diferentes na mesma fazenda:
 1 dados iniciais: Plantio dividido entre a plantadeira da fazenda (6,8 ha/h) e um prestador (2,925 ha/h); totais da etapa 4 = espelho dados2.plano_op
 2 T2 (298 ha) no plano operacional: área por conjunto, horas-conjunto, decorrido, custo e diesel = dados2.repartir; Σ área = 298
 3 um conjunto só (Dessecação pré-plantio): uma linha, horas = área ÷ 21,6
 4 incluir outra configuração em Adubação de cobertura pelo formulário (por classe, sem patrimônio): a anterior continua; plano recalcula
 5 mudar a repartição (prestador 30 % fixo): T2 segue o espelho; demanda de insumos (CAL-01) igual à inicial (dose × área)
 6 recurso compartilhado: a nova configuração usa o mesmo distribuidor do cadastro → em sequência; janela curta → "sequência não cabe na janela"
 7 partes fixas acima de 100 % são recusadas no formulário (o que foi digitado fica)
 8 remover a configuração incluída (com confirmação): volta a uma linha e os totais voltam aos iniciais; sem erros de JS
 9 celular 390 px · 10 Safrinha 2027 e Lagoa Grande = espelho · 11 safra encerrada só consulta
Capturas: _probe/rend_depois_rendimentos.png, rend_depois_plano_operacional.png, rend_depois_form_nova.png, rend_depois_conflito.png,
rend_depois_celular_rendimentos.png, rend_depois_celular_plano.png.
Modos, cada um < 60 s: python3 rend_multiconjuntos_test.py [fluxo|telas|bordas|bordas2]   (fluxo = 1–8, padrão; telas = 9–11;
bordas = B1 janela 0 h (causa, linhas agregadas, aviso na etapa 5), B2 sequência × janela de 3 h (com necessário × atendido × saldo nas etapas
4 e 5 e o S5 da decisão Codex REND-RETORNO-1818: partes 50/50), B3 teclado; bordas2 = B5 motivo do grupo da fazenda e troca da 1ª
configuração, B6 prestador fora das horas-homem). Capturas novas: rend_bordas_*.png."""
import sys, os, time, subprocess, json
MODO=(sys.argv[1] if len(sys.argv)>1 else 'fluxo')
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
import dados2 as D2
R=os.path.join(HERE,'_render'); PROBE=os.path.join(HERE,'_probe'); os.makedirs(PROBE,exist_ok=True)
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
OK=[]; FAIL=[]
def chk(nome,cond,det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ')+nome+(f' · {str(det)[:500]}' if det!='' else ''),flush=True)
def fmt(x,d=0):
    s=f'{float(x):,.{d}f}'; return s.replace(',','X').replace('.',',').replace('X','.')
def nfa(x):   # como nfa da tela: até 2 casas, sem zeros à direita
    s=fmt(round(float(x),2),2); return s.rstrip('0').rstrip(',')
def trio_txt(e):   # as três linhas da ocorrência (safra.js · trio): necessário, atendido e saldo, com unidades
    hs=lambda a,b: f' · {fmt(a,1)} horas-conjunto · {fmt(b,1)} h decorridas'; n,f=e['nec'],e['falta']
    return [f"Necessário: {nfa(n['area'])} ha"+hs(n['hconj'],n['decorrido']),f"Atendido: {nfa(e['alocado'])} ha"+hs(e['hconj'],e['decorrido']),
            f"Saldo: {nfa(e['saldo'])} ha · faltam "+hs(f['hconj'],f['decorrido'])[3:]]
def cfg_txt(x): return f"precisa de {nfa(x['nq'])} ha = {fmt(x['nh'],1)} h · faltam {nfa(x['fq'])} ha = {fmt(x['fh'],1)} h"
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
c=None; ERR=[]
try:
    c=Chrome(port=free()); J=c.js; B=f'http://127.0.0.1:{p}/'
    c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__err=[];addEventListener('error',e=>window.__err.push(String(e.message)));"})
    clk=lambda t,root=None,w=.45: (J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"),time.sleep(w))[0]
    T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    k4=lambda: J("(document.body.innerText.match(/[\\d.,]+ ha trabalhados[^\\n]+/)||[''])[0]") or ''
    k6=lambda: J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]") or ''
    from comp_lib import IR_ETAPA
    def etapa(n): r=J(f"({IR_ETAPA})({n})"); time.sleep(.5); return r   # a faixa só informa (UX-ACAO-UNICA-20261003): anda pela área de ações
    # células visíveis de cada linha; o triângulo de abrir/recolher (▸ ▾) sai do texto da 1ª célula
    # TABELAS-FOCO (5983172395): a etapa 3 tem uma variável por coluna (Operação | Atividade | Conjunto | Modo | Largura | Velocidade | Eficiência |
    # Rendimento | Custo R$/h | R$/ha | R$/kg | … ; ordem real: Operação | Atividade | Conjunto | Rendimento | custos | Modo | Largura | Velocidade | Eficiência | Parte | Trabalha | Janela | Planos); LEG lê essas colunas e remonta as 6 células de antes, para os
    # mesmos valores serem conferidos pelas mesmas asserções (as outras grades passam como estão)
    LEG=r"""(x=>{ let cs=[...x.querySelectorAll('[role=cell]')].map(c=>c.innerText.replace(/\s+/g,' ').trim()); const tb=x.closest('[role=table]');
      const hs=tb?[...tb.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\s+/g,' ').trim().toUpperCase()):[];
      // incremento 2d (decisão de 05/10/2026): a unidade fixa vai na célula ("36 m", "R$ 109,40/ha"); para as contas abaixo valerem como antes,
      // tira a unidade só das colunas que a levam (data-un no cabeçalho); a exibição com unidade é conferida em tabelas_saf_test
      const UN=tb?[...tb.querySelectorAll('[role=columnheader]')].map(h=>h.getAttribute('data-un')||''):[];
      const tira=(t,u)=>{ if(!u||t==='—') return t; if(u.indexOf('R$')===0){ const m=t.match(/^([−-]?)R\$ (.+?)(\/\S+)?$/); return m?m[1]+m[2]:t; } return t.endsWith(' '+u)?t.slice(0,-u.length-1):t; };
      cs=cs.map((t,i)=>tira(t,UN[i]));
      // etapa 4: Gatilho | Data separados e Parte | Janela | Talhão no fim; remonta a coluna "Gatilho · data" de antes (regra, data ou parte da configuração)
      if(hs[1]==='GATILHO'&&hs[2]==='DATA'&&cs.length>=15){ const nm=cs[0], ix=nm.indexOf(' precisa de '); const part=cs[12], jan=cs[13];
        const cfg=part&&part!=='—'; const opOld=cfg?((part==='pelo rendimento'?'pelo rendimento':part+' % da área')+(jan&&jan!=='—'?' · janela '+jan+' h':'')+(ix>=0?' '+nm.slice(ix+1):''))
          :((cs[1]&&cs[1]!=='—')?cs[1]:((cs[2]&&cs[2]!=='—')?cs[2]:''));
        return [cfg&&ix>=0?nm.slice(0,ix):nm,opOld].concat(cs.slice(3,12)); }
      if(hs[0]!=='OPERAÇÃO'||hs[1]!=='ATIVIDADE'||cs.length<15) return cs;
      const st=t=>t.replace(/^[▸▾]\s*/,''); const op=st(cs[0]), atv=cs[1], nome=cs[2], modo=cs[7], part=cs[11], seq=cs[12], jan=cs[13].replace(/,0$/,''), pl=cs[14];
      const janT=(jan&&jan!=='—')?' janela '+jan+' h por talhão':''; const param=modo==='Informado'?'informado':(cs[8]+' m × '+cs[9]+' km/h × '+cs[10]+' %').replace(/,00? /g,' ');
      if(/^\d+ atividades?$/.test(atv)){ const aj=/ ajustado nesta safra$/.test(op); return [op.replace(/ ajustado nesta safra$/,'')+' '+atv+(aj?' ajustado nesta safra':''),nome,'','','','']; }
      if(/ configurações/.test(atv)){ const mais=/ \+ Outra configuração$/.test(atv); return [atv.replace(/ \+ Outra configuração$/,'')+(pl!=='—'?' '+pl:'')+(mais?' + Outra configuração':''),part,'por configuração','','','por configuração']; }
      const c5=cs[5]+((cs[6]&&cs[6]!=='—')?' '+cs[6]:'');
      if(seq==='Ao mesmo tempo'||seq==='Em sequência') return ['Parte: '+(part==='pelo rendimento'?'pelo rendimento':part.replace(/,0$/,'')+' % da área')+(seq==='Em sequência'?' em sequência':'')+janT,nome,param,cs[3],cs[4],c5];
      return [atv+(pl!=='—'?' '+pl:'')+janT,nome,param,cs[3],cs[4],c5]; })"""
    def rows(): return J(f"[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent).map(r=>({LEG})(r).map((t,i)=>i===0?t.replace(/^[▸▾]\\s*/,''):t))") or []
    def row(pref):
        return next((r for r in rows() if r and r[0].startswith(pref)),None)
    def rowAfter(anchor,pref):
        rs=rows(); i=next((k for k,r in enumerate(rs) if r and r[0].startswith(anchor)),None)
        return None if i is None else next((r for r in rs[i+1:] if r and r[0].startswith(pref)),None)
    def rec(t): J(f"(()=>{{const b=[...document.querySelectorAll('button[aria-label]')].filter(x=>x.offsetParent).find(b=>b.getAttribute('aria-label')==='Recolher '+{json.dumps(t)}); if(b) b.click();}})()"); time.sleep(.3)
    def abrirCfg(sub):   # configuração (linha "Parte: …") cujo conjunto contém sub
        r=J(f"(()=>{{const rs=[...document.querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent); const r=rs.find(x=>{{const cs=({LEG})(x); return cs[0]&&cs[0].startsWith('Parte:')&&cs[1]&&cs[1].indexOf({json.dumps(sub)})>=0; }}); if(!r) return 'sem linha'; r.querySelector('[role=cell] span').click(); return 'ok';}})()"); time.sleep(.45); return r
    def exp(t): r=J(f"(()=>{{const b=[...document.querySelectorAll('button[aria-label]')].filter(x=>x.offsetParent).find(b=>b.getAttribute('aria-label')==='Expandir '+{json.dumps(t)}); if(!b) return 'sem'; b.click(); return 'ok';}})()"); time.sleep(.35); return r
    def abrir(pref,idx=0):
        r=J(f"(()=>{{const rs=[...document.querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent&&(x.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(pref)})||(({LEG})(x)[0]||'').startsWith({json.dumps(pref)}))); const r=rs[{idx}]; if(!r) return 'sem linha'; r.querySelector('[role=cell] span').click(); return 'ok';}})()"); time.sleep(.45); return r
    def campo(k,v):
        return J(f"""(()=>{{const i=document.querySelector('aside [id$="_{k}"]'); if(!i) return 'sem campo {k}'; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
          Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(v)}); i.dispatchEvent(new Event(i.tagName==='SELECT'?'change':'input',{{bubbles:true}})); return 'ok';}})()""")
    painel=lambda: J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or ''
    def col():
        try: ERR.extend(J("window.__err||[]") or [])
        except Exception as e: ERR.append(str(e))
    c.size(1440,1000)
    if MODO=='fluxo':
        c.goto(B+'SAF.dc.html#saf=S2627&etapa=4',wait=1.6)
        # ---------- 1 · totais iniciais × espelho ----------
        m=D2.plano_op('S2627'); t0=k4()
        exp_t=f"{nfa(m['area'])} ha trabalhados · {fmt(m['hconj'])} horas-conjunto · {fmt(m['hh'])} horas-homem · {fmt(m['diesel'])} L de diesel"
        print('k4 inicial:',t0); print('espelho   :',exp_t,'· custo op.',round(m['cop'],2),'· multi',m['multi'],'· sem conjunto',m['saldo'],'· pendentes',m['pend'])
        chk('1 totais iniciais da etapa 4 = espelho dados2.plano_op (área, horas-conjunto, horas-homem, diesel)',t0.startswith(exp_t),[t0,exp_t])
        tot=next((r for r in rows() if r and r[0]=='Total'),None); chk('1b total da coluna Custo de operação = espelho',tot and fmt(m['cop']) in tot,[tot,fmt(m['cop'])])
        etapa(6); k6a=k6(); print('k6 inicial:',k6a); etapa(4)
        # ---------- 2 · T2 dividido entre dois conjuntos ----------
        pools={r['id']:dict(un=r['un'],nome=r['nome']) for r in D2.RECURSOS}
        def esperado_T2(part=None):
            cfs=[D2.cfg_in(x) for x in D2.cfgs_rend('S2627','Plantio','Plantio e adubação de base')]
            if part is not None: cfs[1]['part']=part
            return D2.repartir(298,cfs,pools)
        def ver_T2(rotulo,part=None,shot=None):
            e=esperado_T2(part); rec('Pulverização'); rec('Adubação a lanço'); exp('Plantio'); exp('Plantio e adubação de base'); exp('T2 · Soja 58 W')
            oc=rowAfter('Plantio e adubação de base','T2 · Soja 58 W'); ks=[r for r in rows() if r and (r[0].startswith('Trator T1 JD 6M 155') or r[0].startswith('Prestador'))]
            print(f'   {rotulo} · tela T2:',oc); [print('      ',k) for k in ks]
            print(f'   {rotulo} · espelho: q',[round(x["q"],4) for x in e['itens']],'h',[round(x["h"],4) for x in e['itens']],'hconj',round(e['hconj'],4),'dec',round(e['decorrido'],4),'custo',round(e['custo'],2),'diesel',round(e['diesel'],2))
            okv=bool(oc) and oc[3]==nfa(298) and oc[4]==fmt(e['hconj'],1) and oc[5].startswith(fmt(e['decorrido'],1)) and oc[6]==fmt(e['custo']) and oc[10]==fmt(e['diesel'])
            okk=len(ks)==2 and all(k[3]==nfa(x['q']) and k[4]==fmt(x['h'],1) and k[6]==fmt(x['custo']) for k,x in zip(ks,e['itens']))
            soma=sum(x['q'] for x in e['itens'])+e['saldo']
            if shot: c.shot(os.path.join(PROBE,shot))
            return okv and okk and abs(soma-298)<1e-9, [oc,ks]
        ok,det=ver_T2('inicial',shot='rend_depois_plano_operacional.png')
        chk('2 T2 (298 ha): duas configurações com área, horas-conjunto, decorrido, custo e diesel do espelho; Σ área = 298 ha; decorrido < horas-conjunto',ok and det[0][5]!=det[0][4],det)
        # ---------- 3 · um conjunto só ----------
        rec('Plantio'); exp('Pulverização'); exp('Dessecação pré-plantio')
        rs=[r for r in rows() if r and r[0].startswith('T2 ·')]
        one=next((r for r in rs if r[1].startswith('28/09') or r[2]=='set/26'),None)
        chk('3 um conjunto só (Dessecação pré-plantio em T2): sem linhas de configuração, horas = decorrido = 298 ÷ 21,6',one is not None and one[4]==fmt(298/21.6,1) and one[5]==fmt(298/21.6,1),[one,fmt(298/21.6,1)])
        # ---------- 4 · incluir outra configuração em Adubação de cobertura ----------
        etapa(3); print('abrir Adubação de cobertura:',abrir('Adubação de cobertura'),'·',painel().split('\n')[0:3])
        acts=J("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim()).filter(t=>/configuração/.test(t))"); print('ações do formulário:',acts)
        print('incluir:',clk('+ Outra configuração para Adubação de cobertura','aside[role=dialog]'))
        print('form novo:',painel().replace('\n',' | ')[:300])
        chk('4a "+ Outra configuração" abre "Nova configuração" com a atividade à vista e "Por classe" sem patrimônio',
            'Nova configuração' in painel() and J("(document.querySelector('aside [id$=\"_opatv\"]')||{value:''}).value")=='Adubação a lanço · Adubação de cobertura'
            and J("(document.querySelector('aside [id$=\"_conj_id\"]')||{value:''}).value")=='classe')
        for k,v in [('nome','Trator 75 cv + distribuidor 12 m'),('larg','12'),('vel','8'),('efic','70'),('maq','120'),('impl','30'),('pess','1'),('pess_rs','38'),('diesel','8')]: campo(k,v)
        time.sleep(.3); c.shot(os.path.join(PROBE,'rend_depois_form_nova.png'))
        print('salvar:',clk('Salvar','aside[role=dialog]'),T())
        grp=row('Adubação de cobertura'); ks=[r for r in rows() if r and len(r)>1 and r[0].startswith('Parte:') and ('Distribuidor 3 t' in r[1] or 'distribuidor 12 m' in r[1])]
        print('grupo:',grp); [print('   ',k) for k in ks]
        chk('4b a atividade vira grupo com 2 configurações; a anterior (Trator 03 + Distribuidor 3 t, 18 ha/h) continua; a nova com 6,72 ha/h',
            grp and '2 configurações' in grp[0] and len(ks)==2 and any('Trator 03 + Distribuidor 3 t' in k[1] and k[3]=='18,00' for k in ks) and any('distribuidor 12 m' in k[1] and k[3]=='6,72' for k in ks),[grp,ks])
        J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>/^.?\\s*Plantio\\b/.test(r.innerText.trim())); if(r){ r.scrollIntoView({block:'start'}); window.scrollBy(0,-130);} })()"); time.sleep(.3)
        c.shot(os.path.join(PROBE,'rend_depois_rendimentos.png'))
        etapa(4); t1=k4(); print('k4 com a nova:',t1); chk('4c plano operacional recalculado (horas-conjunto mudam)',t1!=t0 and 'ha trabalhados' in t1,[t0,t1])
        # ---------- 5 · mudar a repartição do prestador para 30 % ----------
        etapa(3); print('abrir prestador:',abrirCfg('Prestador'),painel().split('\n')[0])
        print('campos:',campo('part','30'),T()); print('salvar:',clk('Salvar','aside[role=dialog]'),T())
        pr=next((r for r in rows() if r and r[0].startswith('Parte: 30 %')),None); chk('5a prestador com "Parte: 30 % da área"; a outra segue pelo rendimento',pr is not None and 'Prestador' in pr[1],pr)
        etapa(4); ok,det=ver_T2('30 %',part=30); chk('5b T2 com 30 % fixo no prestador: área 89,4 + 208,6 = 298 ha e horas/custo/diesel do espelho',ok,det)
        etapa(6); k6b=k6(); print('k6 depois:',k6b); chk('5c demanda de insumos (CAL-01) igual à inicial: a divisão não muda dose × área',k6b==k6a and k6a!='',[k6a,k6b])
        # ---------- 6 · recurso compartilhado ----------
        etapa(3); print('abrir a nova:',abrirCfg('distribuidor 12 m'),painel().split('\n')[0])
        opts=J("[...document.querySelectorAll('aside [id$=\"_conj_id\"] option')].map(o=>[o.value,o.innerText])"); print('opções de conjunto:',opts)
        alvo,alvo_t=next((o for o in opts if o[0].endswith('+a07') and not o[0].startswith('a03')),(None,''))
        NOVO=alvo_t.split(' · ')[0]
        print('escolher',alvo,NOVO,campo('conj_id',alvo)); time.sleep(.2); print('salvar:',clk('Salvar','aside[role=dialog]'),T())
        etapa(4); rec('Pulverização'); rec('Plantio'); exp('Adubação a lanço'); exp('Adubação de cobertura')
        o=rowAfter('Adubação de cobertura','T'); print('ocorrência:',o)
        if o: exp(o[0].split(' 2 configurações')[0])
        seq=[r for r in rows() if r and len(r)>4 and 'em sequência' in r[0]]; print('em sequência:',seq[:2])
        chk('6a mesmo distribuidor do cadastro nas duas configurações → em sequência: decorrido = horas-conjunto na ocorrência',bool(o) and o[4]==o[5].split(' ')[0] and len(seq)>=2,[o,seq[:2]])
        etapa(3); abrirCfg(NOVO); campo('jan','3'); print('janela 3 h:',clk('Salvar','aside[role=dialog]'),T())
        abrirCfg('Trator 03 + Distribuidor 3 t'); campo('jan','3'); print('janela 3 h:',clk('Salvar','aside[role=dialog]'),T())
        etapa(4); exp('Adubação a lanço'); exp('Adubação de cobertura'); exp('T2 · Soja 58 W')
        o2=rowAfter('Adubação de cobertura','T2 · Soja 58 W'); print('T2 com janela 3 h:',o2); print('k4:',k4())
        c.shot(os.path.join(PROBE,'rend_depois_conflito.png'))
        chk('6b janela de 3 h por talhão: área que não cabe fica "sem conjunto" com motivo; sequência acima da janela aparece como conflito; nada vira 0 h',
            bool(o2) and 'ha sem conjunto' in o2[0] and 'sequência não cabe na janela' in o2[0] and 'janela' in o2[0] and o2[4] not in ('0','0,0'),o2)
        # ---------- 7 · partes fixas acima de 100 % ----------
        etapa(3); abrirCfg('Trator T1 JD 6M 155'); campo('part','80'); clk('Salvar','aside[role=dialog]')
        pe=J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText:'';})()")
        chk('7 partes fixas 30 % + 80 % são recusadas com motivo; o formulário continua aberto com o que foi digitado',
            'o máximo é 100 %' in pe and J("(document.querySelector('aside [id$=\"_part\"]')||{value:''}).value")=='80',pe[:200])
        J("(()=>{const i=document.querySelector('aside [id$=\"_part\"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,''); i.dispatchEvent(new Event('input',{bubbles:true}));})()")
        clk('Salvar','aside[role=dialog]')
        # ---------- 8 · remover a configuração incluída ----------
        abrirCfg(NOVO); nm=J("(document.querySelector('aside [id$=\"_conj_id\"]')||{value:''}).value"); print('remover config com conjunto',nm)
        print('remover (1º toque):',clk('Remover esta configuração','aside[role=dialog]'))
        conf=J("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim()).filter(t=>/^Confirmar: remover/.test(t))"); print('confirmação:',conf)
        print('confirmar:',clk('Confirmar: remover','aside[role=dialog]'),T())
        g2=row('Adubação de cobertura'); print('linha:',g2)
        chk('8a remover pede confirmação e a atividade volta a uma linha com o conjunto anterior',bool(conf) and g2 and '2 configurações' not in g2[0] and 'Trator 03 + Distribuidor 3 t' in g2[1],[conf,g2])
        # prestador volta a dividir pelo rendimento e a janela da 1ª sai: totais voltam aos iniciais
        abrir('Parte: 30 %'); campo('part',''); clk('Salvar','aside[role=dialog]')
        abrir('Adubação de cobertura'); campo('jan',''); clk('Salvar','aside[role=dialog]'); print('desfeito:',T())
        etapa(4); t2=k4(); print('k4 final:',t2); chk('8b depois de desfazer, o plano operacional volta aos totais iniciais',t2==t0,[t0,t2])
        col(); chk('8c sem erros de JS na página',not ERR,ERR)
    if MODO=='telas':
        # ---------- 10 · outras safras: totais = espelho; safra encerrada só consulta ----------
        for sf in ('S27SF','LG2627'):
            c.goto('about:blank',wait=.1); c.goto(B+f'SAF.dc.html#saf={sf}&etapa=4',wait=1.6); ms=D2.plano_op(sf); tk=k4()
            ex=f"{nfa(ms['area'])} ha trabalhados · {fmt(ms['hconj'])} horas-conjunto · {fmt(ms['hh'])} horas-homem · {fmt(ms['diesel'])} L de diesel"
            chk(f'10 {sf}: totais da etapa 4 = espelho dados2.plano_op (uma configuração por atividade)',tk.startswith(ex) and ms['multi']==0,[tk,ex,ms['multi']])
            if sf=='LG2627':   # PRE-REV R7: 'Por mês' com área de até 2 casas; os meses somam o total do período
                clk('Por mês'); ar=next((r for r in rows() if r and r[0]=='Área trabalhada (ha)'),None)
                num=lambda t: float(t.replace('.','').replace(',','.')) if t and t not in ('—','') else 0.0
                vs=[num(x) for x in (ar or [])[1:-1]]; tt=num((ar or [''])[-1])
                chk('10b LG2627 por mês: área trabalhada com até 2 casas e meses = total do período',bool(ar) and any(',' in x for x in ar[1:]) and abs(sum(vs)-tt)<=0.006*max(1,len(vs)),[ar,round(sum(vs),2),tt])
        c.goto('about:blank',wait=.1); c.goto(B+'SAF.dc.html#saf=S2526&etapa=3',wait=1.6)
        lk=J("[...document.querySelectorAll('main button,main a')].filter(b=>b.offsetParent&&/Outra configuração/.test(b.innerText)).length")
        abrir('Colheita'); fa=J("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim()).filter(t=>/configuração/.test(t))"); ro=J("(()=>{const i=document.querySelector('aside [id$=\"_larg\"]'); return i?i.readOnly:null;})()")
        chk('11 Safra 2025/26 (encerrada): sem "+ Outra configuração" na tabela nem no formulário, que abre só em consulta',lk==0 and fa==[] and ro is True,[lk,fa,ro])
        clk('Fechar','aside[role=dialog]'); col()   # fecha a consulta (o rascunho aberto sobrevive à recarga)
        # ---------- celular (390 px): mesmas etapas, tabela rola dentro da caixa ----------
        c.size(390,844); c.goto(B+'SAF.dc.html#saf=S2627&etapa=3',wait=1.6)
        J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>/^.?\\s*Plantio\\b/.test(r.innerText.trim())); if(r){ r.scrollIntoView({block:'center'});} })()"); time.sleep(.3)
        c.shot(os.path.join(PROBE,'rend_depois_celular_rendimentos.png'))
        hs=J("document.documentElement.scrollWidth>innerWidth+1")
        c.goto(B+'SAF.dc.html#saf=S2627&etapa=4',wait=1.6); exp('Plantio'); exp('Plantio e adubação de base'); exp('T2 · Soja 58 W')
        J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>/T2 · Soja 58 W/.test(r.innerText)); if(r) r.scrollIntoView({block:'center'});})()"); time.sleep(.3)
        c.shot(os.path.join(PROBE,'rend_depois_celular_plano.png'))
        hs2=J("document.documentElement.scrollWidth>innerWidth+1"); col()
        chk('9 celular 390 px: etapas 3 e 4 sem rolagem lateral da página (a tabela rola dentro da caixa) e sem erros',not hs and not hs2 and not ERR,[hs,hs2,ERR])
    # ---------- bordas da verificação (rodada 2): janela 0 h, sequência × janela, teclado ----------
    SEQ='Em sequência: divide trator, implemento ou operador'
    def salvar(): r=clk('Salvar','aside[role=dialog]'); return r,T()
    def so(op,atv):   # etapa 4 só com a operação e a atividade abertas, e as ocorrências divididas expandidas
        etapa(4)
        for o in ('Pulverização','Plantio','Adubação a lanço','Tratamento de sementes'):
            if o!=op: rec(o)
        exp(op); exp(atv)
        for l in (J("[...document.querySelectorAll('button[aria-label^=\"Expandir T\"]')].filter(b=>b.offsetParent).map(b=>b.getAttribute('aria-label'))") or []):
            J(f"(()=>{{const b=document.querySelector('button[aria-label={json.dumps(l)}]'); if(b) b.click();}})()"); time.sleep(.3)
        return rows()
    def abrirEm(grupo,pred):   # abre a configuração (linha "Parte: …") de um grupo de atividade, escolhida por pred(conjunto)
        r=J(f"""(()=>{{const rs=[...document.querySelectorAll('[role=row]')].filter(x=>x.offsetParent); const cs=x=>({LEG})(x);
          const i=rs.findIndex(x=>(cs(x)[0]||'').replace(/^[▸▾]\\s*/,'').startsWith({json.dumps(grupo)})); if(i<0) return 'sem grupo'; const P={pred};
          const r=rs.slice(i+1).find(x=>x.classList.contains('g2ed')&&(cs(x)[0]||'').startsWith('Parte:')&&P(cs(x)[1]||'')); if(!r) return 'sem linha'; r.querySelector('[role=cell] span').click(); return 'ok';}})()"""); time.sleep(.45); return r
    def tecla(enter_real):   # Enter como o teclado manda (keyDown com o caractere) ou só o keyDown sem caractere
        ev={'type':'keyDown','key':'Enter','code':'Enter','windowsVirtualKeyCode':13}
        if enter_real: ev.update(text='\r',unmodifiedText='\r')
        c.call('Input.dispatchKeyEvent',ev); c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Enter','code':'Enter','windowsVirtualKeyCode':13}); time.sleep(.5)
    if MODO=='bordas':
        # ---------- B1 · janela 0 h com rendimento válido: pendente com a causa certa, nunca 0 h nem R$ 0; a etapa 5 avisa ----------
        c.goto(B+'SAF.dc.html#saf=S2627&etapa=3',wait=1.6)
        print('abrir TSI:',abrir('Tratamento de sementes'),campo('jan','0'),salvar())
        rs=so('Tratamento de sementes','Tratamento de sementes'); c.shot(os.path.join(PROBE,'rend_bordas_janela0_etapa4.png'))
        op=next((r for r in rs if r and r[0].startswith('Tratamento de sementes 1 atividade')),None); oc=next((r for r in rs if r and r[0].startswith('T2 ·')),None); tk=k4()
        print('operação:',op); print('T2:',oc); print('k4:',tk)
        chk('B1a janela 0 h (rendimento 40 ha/h válido): o aviso diz "sem horas na janela · pendente", não "sem rendimento"',
            bool(oc) and 'sem horas na janela · pendente' in oc[0] and 'sem rendimento' not in oc[0] and 'ocorrências pendentes (sem horas na janela)' in tk and 'sem rendimento' not in tk,[oc,tk])
        chk('B1b linhas de operação e atividade com todas as ocorrências pendentes não mostram 0,0 h nem R$ 0',
            bool(op) and op[4] not in ('0','0,0') and op[6] not in ('0','0,0') and 'sem horas na janela · 3 pendentes' in op[0],op)
        etapa(5); t5=J("document.querySelector('main').innerText") or ''; av=next((l for l in t5.split('\n') if 'A demanda não inclui' in l),'')
        c.shot(os.path.join(PROBE,'rend_bordas_janela0_etapa5.png')); print('etapa 5:',av)
        chk('B1c etapa 5 avisa que a demanda não inclui a área sem conjunto nem as ocorrências pendentes','610 ha sem conjunto' in av and '3 ocorrências pendentes' in av,av)
        # ---------- B2 · duas configurações em sequência numa janela de 3 h (Controle de ácaro, T7 42 ha) ----------
        c.goto('about:blank',wait=.1); c.goto(B+'SAF.dc.html#saf=S2627&etapa=3',wait=1.6)
        abrir('Controle de ácaro')
        for k,v in [('esc','Só esta atividade'),('modo','Largura × velocidade'),('larg','6'),('vel','8'),('efic','75'),('maq','180'),('impl','0'),('pess','0'),('pess_rs','0')]: campo(k,v)
        print('A:',salvar()); abrir('Controle de ácaro'); print('incluir:',clk('+ Outra configuração para Controle de ácaro','aside[role=dialog]'))
        campo('conj_id','prestador'); time.sleep(.2)
        for k,v in [('nome','B prestador 12 m'),('modo','Largura × velocidade'),('larg','12'),('vel','8'),('efic','75'),('maq','300'),('seq',SEQ),('jan','3')]: campo(k,v)
        print('B:',salvar())
        print('A em sequência, janela 3 h:',abrirEm('Controle de ácaro',"t=>t.indexOf('B prestador')<0"),campo('seq',SEQ),campo('jan','3'),salvar())
        rs=so('Pulverização','Controle de ácaro'); i=next((k for k,r in enumerate(rs) if r and r[0].startswith('T7 ·')),None)
        oc=rs[i] if i is not None else None; ks=rs[i+1:i+3] if i is not None else []; print('T7:',oc); [print('    ',k) for k in ks]
        c.shot(os.path.join(PROBE,'rend_bordas_sequencia_janela3.png'))
        e=D2.repartir(42,[dict(nome='A',rend=D2.rend_calc(6,8,75),custo_h=180,jan=3,seq=True),dict(nome='B',rend=D2.rend_calc(12,8,75),custo_h=300,jan=3,seq=True)])
        print('espelho: q',[round(x['q'],4) for x in e['itens']],'sem conjunto',round(e['saldo'],4),'decorrido',e['decorrido'],'hconj',e['hconj'])
        import re as _re
        m=_re.search(r'([\d.,]+) ha sem conjunto',oc[0] if oc else ''); sem=float(m.group(1).replace('.','').replace(',','.')) if m else -1
        chk('B2a sequência numa janela de 3 h: no máximo 21,6 ha atendidos; "sem conjunto" ≥ 20,4 ha (= espelho 25,8 ha); decorrido e horas-conjunto 3,0 h',
            bool(oc) and abs(sem-25.8)<0.01 and sem>=20.4 and oc[4]=='3,0' and oc[5].startswith('3,0') and abs(e['saldo']-25.8)<1e-9,[oc,sem])
        # REND-RETORNO-1818: a necessidade é da demanda inteira (42 ÷ 10,8 × 2 = 70/9 h); "6 h" cortava cada uma na janela antes de somar
        chk('B2b o conflito continua à vista com o motivo (precisam de 7,78 h para os 42 ha; a janela tem 3 h) e a área que não cabe é explicada',
            bool(oc) and 'sequência não cabe na janela' in oc[0] and 'em sequência precisam de 7,78 h para 42 ha; a janela tem 3 h' in oc[0] and 'dividem a mesma janela' in oc[0],oc)
        tt=trio_txt(e); cf=[cfg_txt(x) for x in e['itens']]; print('esperado:',tt,cf)
        chk('B2c necessário = atendido + saldo na ocorrência (42 ha · 7,8 = 3,0 + 4,8 horas-conjunto) e em cada configuração (a parte dela e o que falta), = espelho',
            bool(oc) and all(t in oc[0] for t in tt) and len(ks)==2 and all(t in k[1] for t,k in zip(cf,ks)),[oc and oc[0],[k[1] for k in ks]])
        tk4=k4(); etapa(5); t5=J("document.querySelector('main').innerText") or ''; av=next((l for l in t5.split('\n') if 'A demanda não inclui' in l),'')
        m5=_re.search(r'conta ([\d.,]+) das ([\d.,]+) horas-conjunto necessárias, faltam ([\d.,]+)',av); m4=_re.search(r'fora das horas-conjunto: faltam ([\d.,]+) horas-conjunto',tk4)
        num=lambda x: float(x.replace('.','').replace(',','.')); print('k4:',tk4); print('etapa 5:',av)
        chk('B2e etapas 4 e 5 não se contradizem: a etapa 5 conta as horas atendidas das necessárias e falta o mesmo número de horas-conjunto da etapa 4 (necessárias = contadas + faltam)',
            bool(m5 and m4) and m5.group(3)==m4.group(1) and abs(num(m5.group(1))+num(m5.group(3))-num(m5.group(2)))<=0.11,[m4 and m4.group(0),m5 and m5.group(0)])
        # ---------- S5 da decisão Codex na tela: partes fixas 50/50 em sequência, janela de 3 h ----------
        etapa(3); print('A 50 %:',abrirEm('Controle de ácaro',"t=>t.indexOf('B prestador')<0"),campo('part','50'),salvar())
        print('B 50 %:',abrirEm('Controle de ácaro',"t=>t.indexOf('B prestador')>=0"),campo('part','50'),salvar())
        rs=so('Pulverização','Controle de ácaro'); i=next((k for k,r in enumerate(rs) if r and r[0].startswith('T7 ·')),None)
        oc5=rs[i] if i is not None else None; ks5=rs[i+1:i+3] if i is not None else []; print('T7 50/50:',oc5); [print('    ',k) for k in ks5]
        c.shot(os.path.join(PROBE,'rend_bordas_s5_partes_50_50.png'))
        e5=D2.repartir(42,[dict(nome='A',rend=D2.rend_calc(6,8,75),custo_h=180,jan=3,seq=True,part=50),dict(nome='B',rend=D2.rend_calc(12,8,75),custo_h=300,jan=3,seq=True,part=50)])
        tt5=trio_txt(e5); cf5=[cfg_txt(x) for x in e5['itens']]; print('espelho 50/50:',tt5,cf5,'déficit',e5['deficit'])
        chk('B2d S5 na tela (50 % + 50 %, janela 3 h): necessário 42 ha = 8,8 horas-conjunto (21 ha em 5,8 h + 21 ha em 2,9 h), atendido e saldo do espelho, motivo com as 8,75 h da demanda inteira',
            bool(oc5) and all(t in oc5[0] for t in tt5) and 'em sequência precisam de 8,75 h para 42 ha; a janela tem 3 h' in oc5[0] and len(ks5)==2 and all(t in k[1] for t,k in zip(cf5,ks5))
            and abs(e5['nec']['hconj']-8.75)<1e-9 and abs(e5['deficit']-5.75)<1e-9,[oc5 and oc5[0],[k[1] for k in ks5]])
        # ---------- B3 · teclado: "+ Outra configuração" da linha do grupo abre com Enter ----------
        etapa(3); foco=J("(()=>{const b=[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&b.innerText.trim()==='+ Outra configuração'); if(!b.length) return 0; b[0].focus(); return document.activeElement===b[0]?b.length:0;})()")
        tecla(False); sem_txt='Nova configuração' in painel()
        J("(()=>{const b=[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&b.innerText.trim()==='+ Outra configuração'); if(b.length) b[0].focus();})()")
        tecla(True); com_txt='Nova configuração' in painel(); print('foco:',foco,'· Enter só keyDown (sem caractere):',sem_txt,'· Enter do teclado (keyDown com \\r):',com_txt)
        chk('B3 "+ Outra configuração" da linha do grupo abre "Nova configuração" com Enter do teclado',bool(foco) and com_txt,[foco,sem_txt,com_txt])
        col(); chk('B4 sem erros de JS',not ERR,ERR)
    if MODO=='bordas2':
        # ---------- B5 · grupo da fazenda (1 distribuidor) põe em sequência: o motivo aparece; a troca da 1ª configuração conta ----------
        c.goto(B+'SAF.dc.html#saf=S2627&etapa=3',wait=1.6)
        abrir('Adubação de cobertura'); clk('+ Outra configuração para Adubação de cobertura','aside[role=dialog]')
        for k,v in [('nome','Classe distribuidor 12 m'),('larg','12'),('vel','8'),('efic','70'),('maq','120'),('impl','30'),('pess','1'),('pess_rs','38')]: campo(k,v)
        print('classe:',salvar())
        rs=so('Adubação a lanço','Adubação de cobertura'); oc=next((r for r in rs if r and r[0].startswith('T2 ·')),None); print('T2:',oc)
        chk('B5a "Ao mesmo tempo" posta em sequência pelo grupo da fazenda: a ocorrência mostra "Distribuidores: ao mesmo tempo precisariam de 2, a fazenda tem 1"',
            bool(oc) and 'Distribuidores: ao mesmo tempo precisariam de 2, a fazenda tem 1' in oc[0],oc)
        etapa(3); print('troca 2 h na 1ª:',abrirEm('Adubação de cobertura',"t=>t.indexOf('Trator 03')>=0"),campo('troca','2'),salvar())
        rs=so('Adubação a lanço','Adubação de cobertura'); oc2=next((r for r in rs if r and r[0].startswith('T2 ·')),None); print('T2 com troca:',oc2)
        num=lambda x: float(x.split(' ')[0].replace('.','').replace(',','.'))
        chk('B5b troca informada na 1ª configuração entra no decorrido (decorrido = horas-conjunto + 2 h)',bool(oc2) and abs(num(oc2[5])-num(oc2[4])-2)<0.11,oc2)
        # ---------- B6 · prestador pelo formulário: não conta horas-homem da fazenda (etapa 4 = etapa 5) ----------
        c.goto('about:blank',wait=.1); c.goto(B+'SAF.dc.html#saf=S2627&etapa=3',wait=1.6)
        abrir('Adubação de cobertura'); clk('+ Outra configuração para Adubação de cobertura','aside[role=dialog]'); campo('conj_id','prestador'); time.sleep(.2)
        pess0=J("(document.querySelector('aside [id$=\"_pess\"]')||{value:null}).value"); campo('nome','Prestador lanço'); campo('maq','250')
        cc=J("(()=>{const i=document.querySelector('aside [id$=\"_custo_c\"]'); return i?(i.value||i.innerText):null;})()"); r_=salvar(); print('prestador:',pess0,cc,r_)
        etapa(4); tk=k4(); import re as _re; hh4=_re.search(r'([\d.]+) horas-homem',tk).group(1)
        etapa(5); clk('Pessoas'); clk('Por mês'); rs=rows(); i=next((k for k,r in enumerate(rs) if r and r[0].startswith('Operadores e equipe')),None)
        d=next((r for r in rs[i+1:] if r and r[0]=='Demanda (h)'),None) if i is not None else None; print('k4:',tk); print('etapa 5 pessoas:',d)
        chk('B6a prestador incluído pelo formulário (Pessoas vinha 1, copiado): horas-homem da etapa 4 = demanda de pessoas da etapa 5',bool(d) and d[-1]==hh4,[pess0,hh4,d and d[-1]])
        chk('B6b o aviso diz que a tarifa do prestador é a de Máquina e que implemento e pessoas da fazenda não entram','Prestador: a tarifa é a de Máquina (R$ 250,00/h)' in (r_[1] or ''),r_)
        col(); chk('B7 sem erros de JS',not ERR,ERR)
finally:
    if c: c.close()
    srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK)+len(FAIL)} OK'+(' · falhas: '+' | '.join(FAIL) if FAIL else ''),flush=True)
sys.exit(0 if not FAIL else 1)
