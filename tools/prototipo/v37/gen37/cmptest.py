# -*- coding: utf-8 -*-
"""Teste CDP do processo Compra de insumos (CMP.dc.html) com a SOL-2026-07: safra → demanda → convites → propostas → aprovação → pedidos.
Uso: python3 cmptest.py [rapido]   (rapido = só o caminho da Direção)"""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=None; FAL=[]
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
ROWCLK="""((t)=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf(t)>=0); if(!r) return 'sem linha '+t; const s=r.querySelector('[role=cell] b')||r.querySelector('[role=cell] span'); s.click(); return 'ok';})"""
# linha-filha t dentro do grupo g (árvore): devolve o texto ou clica
KID="""((g,t,click)=>{const rows=[...document.querySelectorAll('[role=row].g2r')]; const i=rows.findIndex(r=>!r.classList.contains('g2kid')&&r.innerText.replace(/\\s+/g,' ').replace(/^[\\s▾▸]+/,'').startsWith(g)); if(i<0) return 'sem grupo '+g;
  for(let k=i+1;k<rows.length&&rows[k].classList.contains('g2kid');k++){ const x=rows[k]; if(x.innerText.replace(/\\s+/g,' ').indexOf(t)>=0){ if(click){ (x.querySelector('[role=cell] b')||x.querySelector('[role=cell] span')).click(); return 'ok'; } return x.innerText.replace(/\\s+/g,' '); } } return 'sem linha '+t;})"""
def chk(nome,cond,extra=''):
    print(('OK   ' if cond else 'FALHA')+' · '+nome+(' · '+str(extra) if extra!='' else ''));
    if not cond: FAL.append(nome)
try:
    c=Chrome(port=free()); J=c.js
    # ouvinte de erros instalado antes de cada documento (window.__err não existe sem ele)
    c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__err=[];addEventListener('error',e=>window.__err.push(String(e.message)));addEventListener('unhandledrejection',e=>window.__err.push(String(e.reason)));"})
    T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
    def clk(t,root=None,w=.45): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(w); return r
    from comp_lib import IR_ETAPA
    def ir_etapa(n): r=J(f"({IR_ETAPA})({n})"); time.sleep(.45); return r   # a faixa só informa: anda pela área de ações
    def setv(sel,val): r=J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.25); return r
    def row(t): r=J(f"({ROWCLK})({json.dumps(t)})"); time.sleep(.4); return r
    def kid(g,t,click=False): r=J(f"({KID})({json.dumps(g)},{json.dumps(t)},{json.dumps(click)})"); time.sleep(.4 if click else 0); return r
    def rowtxt(t): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(t)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'sem linha';}})()")
    def after(t,u): return J(f"(()=>{{const rows=[...document.querySelectorAll('[role=row]')]; const i=rows.findIndex(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(t)})>=0); const k=rows.slice(i+1).find(r=>r.innerText.indexOf({json.dumps(u)})>=0); return k?k.innerText.replace(/\\s+/g,' '):'sem linha';}})()")
    opts=lambda k: J(f"[...document.querySelectorAll('[id$=_{k}] option')].map(o=>o.value)")
    sub=lambda: J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return ''; const d=a.querySelector('h2').parentElement.nextElementSibling; return d?d.innerText:'';})()")
    body=lambda: J("document.body.innerText")
    cur=lambda: J("(document.querySelector('[aria-current=step]')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
    aside=lambda: J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText")
    def fid(k): return J(f"(document.querySelector('[id$=_{k}]')||{{id:''}}).id")
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/CMP.dc.html'); time.sleep(.6)
    chk('sem erro JS', J("(window.__err&&window.__err.length)?window.__err:'nenhum'")=='nenhum', J("window.__err||''"))
    chk('abre na etapa 1', cur().startswith('1 Escolha a safra'), cur())
    chk('nenhuma safra escolhida sozinha', 'Nenhuma safra escolhida' in body())
    chk('impedimentos visíveis', J("[...document.querySelectorAll('.etp-ind .etp-itens>li')].filter(b=>/Escolha a safra/.test(b.innerText)).length")>=5)
    b=body(); chk('Safrinha sem solicitação', 'Solicitação ainda não enviada pelo planejamento' in b)
    chk('link Ver origem para SAF (demanda de insumos da Safra 2026/27, passo=demanda)', J("[...document.querySelectorAll('a')].some(a=>a.innerText.trim()==='Ver origem'&&a.getAttribute('href')==='SAF.dc.html#saf=S2627&passo=demanda')"))
    chk('link Planejar safra na Safrinha (demanda de insumos da Safrinha, passo=demanda)', J("[...document.querySelectorAll('a')].some(a=>/Abrir Planejar safra/.test(a.innerText)&&a.getAttribute('href')==='SAF.dc.html#saf=S27SF&passo=demanda')"))
    print('  etapa 4 sem safra:', ir_etapa(4), T()); chk('etapa bloqueada sem safra', cur().startswith('1 '))
    # Safrinha: fica na etapa 1, etapas impedidas
    row('Safrinha 2027'); chk('Safrinha selecionada fica na etapa 1', cur().startswith('1 ') and 'Sem solicitação' in J("document.querySelector('.etp-ind').innerText"), T())
    # 2025/26 consulta
    clk('Consultar pedidos'); chk('2025/26 abre pedidos em consulta', cur().startswith('6 ') and 'PC-061' in body() and 'Entregue' in body(), cur())
    clk('Trocar safra')
    # Safra 2026/27
    print('  abrir compra:', clk('Abrir compra'), T())
    chk('etapa 2 · demanda', cur().startswith('2 Confira a demanda'))
    # CTL-4 (demanda única): as O.S. entram na demanda (antes R$ 379.580,00 e MAP 62.500 kg); Fungicida A e Adjuvante saem da SOL; a Ureia da OS-0418 entra
    b=body(); chk('SOL-2026-07 e total igual ao Planejar safra', 'SOL-2026-07' in b and 'R$ 428.305,00' in b and '428.305,00' in J("[...document.querySelectorAll('.g2tot')].map(x=>x.innerText).join(' ')"))
    clk('Expandir tudo'); b=body()
    chk('MAP 11-52 79.500 (500 kg da OS-0417 em custódia contam) e KCl coberto com quarentena', '79.500' in b and 'em quarentena não contam' in b)
    row('MAP 11-52'); a=aside(); chk('origem do insumo abre (consulta)', 'T1-A' in a and 'Ver no Planejar safra' in a, a[:80]); clk('Fechar','aside[role=dialog]')
    # compras-estoque-01 · etapa 2: falta a partir de (demanda datada × estoque apto + pedidos previstos)
    chk('coluna Falta a partir de', 'falta a partir de' in body().lower())
    t=rowtxt('2,4-D 806'); chk('2,4-D falta a partir de 28/09/2026', '28/09/2026' in t, t)
    t=rowtxt('Nitrato de cálcio'); chk('Nitrato de cálcio falta a partir de 01/10/2026', '01/10/2026' in t, t)
    t=rowtxt('KCl 60%'); chk('KCl coberto mostra —', '—' in t and '/20' not in t, t)
    t=rowtxt('Semente de soja 58 W'); chk('58 W coberto (PC-090 chega antes) mostra —', '—' in t and '/20' not in t, t)
    # CTL-4 (DEM-01/02): a OS-0430 (chave c1|a1, T1-A) cobre a dessecação do T1-A e o uso entra pela ordem; o T2 segue pelo plano
    row('2,4-D 806'); a=aside(); chk('origem com data no início da linha', '25/09/2026 · T1-A · OS-0430 · Dessecação' in a and '28/09/2026 · T2 · Dessecação' in a, a[:300]); clk('Fechar','aside[role=dialog]')
    # etapa 3
    clk('Solicitar cotações'); chk('etapa 3', cur().startswith('3 '))
    b=body(); chk('Química Centro-Oeste desabilitada com motivo', 'Não homologado' in b and 'documentação fiscal pendente' in b)
    chk('link homologar CD-05', J("[...document.querySelectorAll('a')].some(a=>a.getAttribute('href')==='CD-05.dc.html')"))
    row('Química Centro-Oeste'); chk('não homologado não abre edição', not J("!!document.querySelector('aside[role=dialog]')") and 'não é homologado' in T(), T())
    time.sleep(.2)
    # compras-estoque-06 · canal só entre os autorizados; destinatário e escopo no subtítulo
    print('  convite Casa do Adubo (Fertilizantes):', kid('Fertilizantes','Casa do Adubo',True))
    o=opts('canal'); s=sub(); print('  canais:', o, '| sub:', s[:200])
    chk('Casa do Adubo só com E-mail autorizado', o==['E-mail'], o)
    chk('subtítulo mostra destinatário e itens do convite', 'Destinatário: e-mail vendas@casadoadubo.com.br' in s and 'Itens do convite (Fertilizantes)' in s and 'MAP 11-52 · 79.500 kg' in s and 'simulado' in s, s)
    chk('ajuda explica o canal único', 'único canal autorizado' in aside(), aside()[:300])
    clk('Cancelar','aside[role=dialog]')
    print('  editar convite Coop. Vale (Fertilizantes):', row('Coop. Vale'))
    chk('form do convite abre pela linha', 'Convite' in aside(), aside()[:60])
    chk('Coop. Vale tem E-mail e WhatsApp autorizados', opts('canal')==['E-mail','WhatsApp'], opts('canal'))
    setv('#'+fid('canal'),'WhatsApp'); chk('destinatário acompanha o canal escolhido', 'Destinatário: WhatsApp 65 99466-7788' in sub(), sub()[:120])
    setv('#'+fid('prazo'),'29/09/2026'); clk('Salvar','aside[role=dialog]')
    chk('convite salvo', 'WhatsApp' in body() and 'Convite atualizado' in T(), T())
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Fertisul/.test(r.innerText)); r.focus(); r.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));})()"); time.sleep(.4)
    chk('teclado (Enter) abre o convite', 'Convite · Fertisul' in aside(), aside()[:40]); clk('Cancelar','aside[role=dialog]')
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Fertilizantes/.test(r.innerText)); r.querySelector('[role=cell] b').click();})()"); time.sleep(.4)
    chk('linha de grupo recolhe (não edita)', not J("!!document.querySelector('aside[role=dialog]')") and 'cotacoes@fertisul' not in body())
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Fertilizantes/.test(r.innerText)); r.querySelector('[role=cell] b').click();})()"); time.sleep(.4)
    print('  enviar:', clk('Enviar convites (simulado)'), T())
    chk('aviso simulado', 'nenhuma mensagem real foi enviada' in T())
    time.sleep(6.5)
    b=body(); chk('respostas chegaram', 'Proposta recebida' in b and 'Sem resposta até agora' in b, J("document.body.innerText.match(/\\d+ de \\d+ convites responderam/)"))
    print('  enviar de novo:', clk('Comparar propostas'))
    # etapa 4
    chk('etapa 4', cur().startswith('4 '))
    b=body(); chk('menor custo total destacado', 'Menor custo total' in b and 'Escolhida' in b)
    k4=J("document.body.innerText.match(/\\d+ propostas · custo total escolhido [^\\n]+/)"); print('  k4:', k4)
    # quantidade acima da necessidade
    row('MAP 11-52'); chk('form da escolha abre', 'Proposta escolhida' in aside())
    setv('#'+fid('ped'),'90000'); clk('Salvar','aside[role=dialog]')
    chk('valida ≤ necessidade', 'Máximo' in aside(), J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')"))
    setv('#'+fid('ped'),'40000'); clk('Salvar','aside[role=dialog]'); chk('quantidade parcial salva', 'de 79.500 kg' in body(), T())
    # vencedor que não é o menor: clicar na proposta da Santa Rita Insumos para o Inoculante
    clk('Expandir tudo')
    r=J("""(()=>{const rows=[...document.querySelectorAll('[role=row].g2ed')]; const i=rows.findIndex(r=>/Inoculante líquido/.test(r.innerText)); const k=rows.slice(i+1).find(r=>/Santa Rita Insumos/.test(r.innerText)); if(!k) return 'sem proposta'; k.querySelector('[role=cell] span').click(); return 'ok';})()"""); time.sleep(.4)
    a=aside(); chk('proposta abre escolha pré-preenchida', 'Santa Rita Insumos' in J(f"document.querySelector('#{fid('venc')}').value"), r)
    clk('Salvar','aside[role=dialog]'); chk('justificativa obrigatória', 'Informe justificativa' in aside(), J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')"))
    clk('Cancelar','aside[role=dialog]'); chk('aviso de alteração não salva', 'Há alterações não salvas' in aside()); clk('Continuar editando','aside[role=dialog]')
    setv('#'+fid('just'),'Entrega em 4 dias para o tratamento de sementes'); clk('Salvar','aside[role=dialog]')
    chk('escolha justificada', 'Justificada' in body(), T())
    # compras-estoque-01 · etapa 4: chega dd/mm, selo de atraso, escolha padrão = menor custo que chega a tempo
    t=rowtxt('2,4-D 806'); print('  2,4-D:', t)
    chk('2,4-D: padrão Agro Norte (menor custo que chega a tempo)', 'falta a partir de 28/09' in t and 'Agro Norte' in t and 'Menor custo a tempo' in t and 'chega 28/09' in t, t)
    t=after('2,4-D 806','Santa Rita Insumos'); print('  Santa Rita p/ 2,4-D:', t)
    chk('Santa Rita: menor custo total, mas chega depois da falta', 'Menor custo total' in t and 'Chega depois da falta (28/09)' in t and 'chega 30/09' in t, t)
    r=J("""(()=>{const rows=[...document.querySelectorAll('[role=row].g2ed')]; const i=rows.findIndex(r=>/2,4-D 806/.test(r.innerText)); const k=rows.slice(i+1).find(r=>/Santa Rita Insumos/.test(r.innerText)); if(!k) return 'sem proposta'; k.querySelector('[role=cell] span').click(); return 'ok';})()"""); time.sleep(.4)
    a=aside(); chk('escolher a atrasada: justificativa obrigatória com as datas', 'chega em 30/09/2026, depois da falta de 28/09/2026' in a, a[:400])
    clk('Salvar','aside[role=dialog]'); chk('atrasada sem justificativa não salva', 'Informe justificativa' in aside())
    clk('Cancelar','aside[role=dialog]'); clk('Descartar alterações','aside[role=dialog]')
    t=rowtxt('Nitrato de cálcio'); chk('Nitrato de cálcio: padrão Casa do Adubo (Fertisul chega depois)', 'Casa do Adubo' in t and 'Menor custo a tempo' in t, t)
    # CTL-4 (DEM-08): a Ureia da OS-0418 falta em 24/09 e nenhuma proposta chega antes: padrão = a que chega primeiro, sem justificativa obrigatória
    # (não há alternativa a tempo para justificar); o aviso "chega depois da falta" continua e o resumo conta a escolha atrasada
    t=rowtxt('Ureia 45%'); k4b=J("(document.body.innerText.match(/\\d+ propostas · custo total escolhido [^\\n]+/)||[''])[0]") or ''
    chk('DEM-08 Ureia: padrão Casa do Adubo "Chega primeiro" + "Chega depois da falta (24/09)", sem "Justificativa pendente"; resumo "1 escolha chega depois da falta" e nenhuma sem justificativa',
        'Casa do Adubo' in t and 'Chega primeiro' in t and 'Chega depois da falta (24/09)' in t and 'Justificativa pendente' not in t and '1 escolha chega depois da falta' in k4b and 'sem justificativa' not in k4b, (t,k4b))
    # etapa 5 · Direção (total acima de 300 mil?) → depende da quantidade; primeiro volta MAP ao total
    row('MAP 11-52'); setv('#'+fid('ped'),'79500'); clk('Salvar','aside[role=dialog]')
    clk('Revisar aprovação'); chk('etapa 5', cur().startswith('5 '))
    b=body(); chk('alçada: Direção exigida', 'Exigida para' in b and 'Acima da sua alçada' in b, J("document.body.innerText.match(/Valor da compra[^\\n]+/)"))
    chk('prévia de pedidos PC-101…', 'PC-101 (prévia)' in b)
    ir_etapa(6); b=body(); chk('navegar não aprova', 'PC-101' not in b and 'PC-088' in b and 'Parcial' in b)
    chk('PC-088 60/100 t, 10 t quarentena, 40 t a entregar', '60 de 100 t recebidas' in b and '10 t em quarentena' in b and '40.000 kg' in b)
    ir_etapa(5)
    print('  enviar à Direção:', clk('Enviar à Direção'), T()); chk('pendente com a Direção', 'Aguardando Direção' in body())
    # mudança material invalida o envio: reduz MAP para 40 t (fica na alçada da Ana)
    ir_etapa(4); row('MAP 11-52'); setv('#'+fid('ped'),'40000'); clk('Salvar','aside[role=dialog]')
    chk('aviso de reenvio', 'reenviada' in T(), T())
    ir_etapa(5); b=body(); chk('dentro da alçada da Ana', 'Valor dentro da sua alçada' in b and 'perdeu a validade' in b, J("document.body.innerText.match(/Valor da compra[^\\n]+/)"))
    # revisão CONF 13/10 (achado de base): quem aprova é o Ver como, lido na hora; nunca "Ana" fixa
    def vercomo(k): J(f"(()=>{{const s=document.querySelector('.menu-lat select'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,{json.dumps(k)}); s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"); time.sleep(.6)
    vercomo('Rui'); b=body(); chk('Ver como Rui (sem gestor nem direção): sem "Aprovar compra"; a primária reenvia à Gerente da fazenda; a alçada não marca "Seu perfil · Ana"', 'Aprovar compra' not in b and 'Reenviar à Gerente da fazenda' in b and 'Seu perfil · Ana' not in b, J("document.body.innerText.match(/[^\\n]*alçada[^\\n]*/g)"))
    vercomo('Ana'); b=body(); chk('Ver como Ana: "Valor dentro da sua alçada (Ana · Gerente da fazenda"', 'Valor dentro da sua alçada (Ana · Gerente da fazenda' in b, J("document.body.innerText.match(/Valor dentro[^\\n]+/)"))
    clk('Aprovar compra'); chk('pede confirmação, como Ana · Gerente da fazenda', 'Confirmar aprovação' in body() and 'como Ana · Gerente da fazenda' in body())
    vercomo('Rui'); b=body(); chk('trocar o Ver como para Rui com a confirmação aberta: a confirmação some e nada é aprovado', 'Confirmar aprovação' not in b and 'Compra aprovada' not in T())
    vercomo('Ana'); clk('Aprovar compra')
    clk('Confirmar aprovação'); t=T(); chk('aprovada gera PCs, por Ana (Gerente da fazenda), o perfil de quem agiu', 'Compra aprovada por Ana (Gerente da fazenda)' in t and 'PC-101' in t, t)
    print('  aprovar de novo:', clk('Acompanhar entrega'))
    b=body(); chk('etapa 6 com novos pedidos', cur().startswith('6 ') and ('PC-101' in b and 'PC-088' in b and 'Fertisul' in b))
    chk('link Estoque', J("[...document.querySelectorAll('a')].some(a=>a.getAttribute('href')==='EST.dc.html')"))
    print('  confirmar fornecedor:', clk('Confirmar fornecedor'), T()); chk('confirmação simulada', 'Confirmado pelo fornecedor' in body())
    row('PC-102'); chk('pedido abre reprogramação', 'Previsão de entrega' in aside(), aside()[:60])
    setv('#'+fid('prev'),'2026-09-01'); clk('Salvar','aside[role=dialog]'); chk('data passada recusada', 'a partir de hoje' in aside())
    setv('#'+fid('prev'),'2026-10-09'); t=T(); clk('Salvar','aside[role=dialog]'); t=T(); chk('previsão reprogramada', '09/10/2026' in body(), t)
    # compras-estoque-01 · etapa 6: aviso sem bloquear quando a nova data passa da falta do item
    # CTL-4: a PC-102 (Casa do Adubo) leva o Nitrato de cálcio e a Ureia da OS-0418 (falta 24/09): o aviso usa a falta mais cedo dos itens
    t=rowtxt('PC-102'); print('  PC-102:', t); chk('PC-102 (Nitrato de cálcio e Ureia) avisa: nova data depois da falta de 24/09', 'Nova data depois da falta de 24/09' in t, t)
    row('PC-090'); setv('#'+fid('prev'),'2026-10-20'); clk('Salvar','aside[role=dialog]'); t=T()
    # CTL-4: com as O.S. na demanda (OS-0420 e OS-0431 tiram 8.944 kg antes), a semente 58 W falta já no 1º plantio (T1-A, 15/10), não mais em 18/10
    chk('PC-090 depois do plantio de T1-A: aviso sem bloquear', 'nova data depois da falta de 15/10/2026' in t and 'Nova data depois da falta de 15/10' in rowtxt('PC-090'), t)
    c.shot('_probe/cmp_e6.png')
    ir_etapa(2); b=body(); clk('Expandir tudo'); b=body(); chk('demanda mostra pedidos', 'Parcial · PC-101' in b and 'Pedido PC-' in b)
    t=rowtxt('Semente de soja 58 W'); chk('58 W passa a faltar em 15/10/2026 com o PC-090 reprogramado', '15/10/2026' in t and 'chega depois da falta' in t, t)
    clk('Trocar safra'); chk('safra mostra pedidos emitidos', 'Pedidos emitidos' in body())
    # caminho Direção numa página nova (sem o andamento gravado: talhao-os-compras-v1 guarda a compra entre recargas)
    J("localStorage.removeItem('talhao-os-compras-v1')"); c.goto(f'http://127.0.0.1:{p}/CMP.dc.html'); time.sleep(.6)
    clk('Abrir compra'); ir_etapa(3); clk('Enviar convites (simulado)'); time.sleep(6.5)
    clk('Comparar propostas'); clk('Revisar aprovação'); clk('Enviar à Direção')
    chk('pendente: ações secundárias de devolução e recusa', 'Registrar devolução' in body() and 'Registrar recusa' in body())
    print('  registrar decisão:', clk('Registrar aprovação da Direção'), T())
    b=body(); chk('Direção aprova (simulado) e emite pedidos', 'Aprovada por Direção (simulado)' in b and 'Pedidos emitidos' in b)
    chk('aprovada: sem devolução/recusa', 'Registrar devolução' not in b)
    c.shot('_probe/cmp_e5.png')
    # ---- compras-estoque-05 · convite adicional depois do envio · compras-estoque-02 · devolução e recusa da Direção ----
    J("localStorage.removeItem('talhao-os-compras-v1')"); c.goto(f'http://127.0.0.1:{p}/CMP.dc.html'); time.sleep(.6)
    clk('Abrir compra'); ir_etapa(3)
    for f in ['Agro Norte','Santa Rita Insumos']:
        kid('Fungicidas',f,True); setv('#'+fid('conv'),'Não convidar'); clk('Salvar','aside[role=dialog]')
    chk('Fungicidas só com a Coop. Vale convidada', 'Não convidar' in kid('Fungicidas','Agro Norte') and 'Convidar' in kid('Fungicidas','Coop. Vale'), kid('Fungicidas','Agro Norte'))
    clk('Enviar convites (simulado)'); time.sleep(6.5)
    # CTL-4: o Fungicida A saiu da SOL-2026-07 (a OS-0421 já o tem); o caso usa o Fungicida TS, do mesmo grupo
    ir_etapa(4); t=rowtxt('Fungicida TS'); chk('Fungicida TS sem proposta', 'Sem proposta ainda' in t, t)
    row('Fungicida TS'); t=T(); chk('aviso aponta o convite adicional', 'Enviar convites adicionais' in t and 'Agro Norte' in t, t)
    ir_etapa(3); r=kid('Fungicidas','Agro Norte',True); a=aside()
    chk('não convidado abre o formulário depois do envio', 'Convite · Agro Norte' in a and 'Convite adicional' in sub(), sub()[:160])
    setv('#'+fid('conv'),'Convidar'); clk('Salvar','aside[role=dialog]')
    chk('ação primária vira Enviar 1 convite adicional', 'Enviar 1 convite adicional (simulado)' in body(), J("[...document.querySelectorAll('main button, header button')].map(b=>b.innerText).filter(t=>/Enviar|Comparar/.test(t)).join('|')"))
    kid('Fungicidas','Coop. Vale',True); t=T(); chk('já convidado continua só consulta', 'Convite simulado enviado a Coop. Vale' in t and not J("!!document.querySelector('aside[role=dialog]')"), t)
    nenv=J("document.body.innerText.match(/(\\d+) de (\\d+) convites responderam/)"); print('  antes:', nenv)
    clk('Enviar 1 convite adicional',w=.1); t=T(); chk('envio adicional simulado, sem reenviar', 'Convites adicionais simulados' in t and 'nenhuma mensagem real' in t and 'Quem já recebeu não recebe de novo' in t, t)
    time.sleep(2.5); t=kid('Fungicidas','Agro Norte'); print('  Agro Norte:', t); chk('Agro Norte respondeu', 'Proposta recebida' in t, t)
    depois=J("document.body.innerText.match(/(\\d+) de (\\d+) convites responderam/)"); print('  depois:', depois)
    chk('só 1 convite a mais', nenv and depois and int(depois[2])==int(nenv[2])+1, f'{nenv} → {depois}')
    clk('Comparar propostas'); t=rowtxt('Fungicida TS'); chk('Fungicida TS agora tem proposta da Agro Norte', 'Agro Norte' in t and 'Sem proposta' not in t, t)
    clk('Revisar aprovação'); clk('Enviar à Direção'); chk('pendente com a Direção', 'Aguardando Direção' in body())
    clk('Registrar devolução'); chk('abre motivo da devolução', 'Confirmar devolução' in body())
    clk('Confirmar devolução'); chk('devolução exige motivo', 'Informe o motivo da devolução' in body())
    J("(()=>{const i=document.querySelector('textarea[aria-label=\"Motivo da decisão\"]'); const P=HTMLTextAreaElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'Negociar MAP com prazo de 60 dias'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
    clk('Confirmar devolução'); b=body(); t=T()
    chk('devolvida: motivo na etapa 5 e trilha', 'Devolvida pela Direção' in b and 'Devolvida · Negociar MAP com prazo de 60 dias' in b, t)
    chk('primário vira Ajustar escolhas (sem reenvio sem mudança)', 'Ajustar escolhas' in b and 'Reenviar à Direção' not in b)
    clk('Ajustar escolhas'); b=body(); chk('etapa 4 mostra o motivo no topo', cur().startswith('4 ') and 'Devolvida pela Direção (simulado): Negociar MAP com prazo de 60 dias' in b)
    row('MAP 11-52'); setv('#'+fid('ped'),'62000'); clk('Salvar','aside[role=dialog]'); chk('aviso de reenvio após mudança', 'Reenvie à Direção' in T(), T())
    ir_etapa(5); chk('depois da mudança: Reenviar à Direção', 'Reenviar à Direção' in body())
    clk('Reenviar à Direção'); chk('reenviada e pendente de novo', 'Aguardando Direção' in body() and 'Reenviado' in T(), T())
    clk('Registrar recusa'); J("(()=>{const i=document.querySelector('textarea[aria-label=\"Motivo da decisão\"]'); const P=HTMLTextAreaElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'Orçamento da safra cortado'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
    clk('Confirmar recusa'); b=body(); t=T()
    chk('recusada: trilha mostra Recusada · motivo', 'Recusada · Orçamento da safra cortado' in b and 'Não contratado' in b, t)
    chk('recusada: nenhum pedido emitido', 'Pedidos emitidos' not in b and 'necessidade da SOL-2026-07 continua aberta' in b)
    clk('Conferir demanda aberta'); clk('Expandir tudo'); t=rowtxt('MAP 11-52'); chk('etapa 2: insumos Não contratado, necessidade aberta', cur().startswith('2 ') and 'Não contratado' in t and 'necessidade aberta' in t, t)
    clk('Trocar safra'); chk('etapa 1: Recusada · não contratado', 'Recusada · não contratado' in body())
    c.shot('_probe/cmp_recusa.png')
    chk('sem erro JS no fim', J("(window.__err&&window.__err.length)?window.__err:'nenhum'")=='nenhum', J("window.__err||''"))
finally:
    if c: c.close()
    srv.terminate()
print('\nFALHAS:', FAL if FAL else 'nenhuma')
