import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
FAIL=[]
def ok(n,cond,info=''):
    print(('OK  ' if cond else 'FALHA ')+n, info if not cond else '')
    if not cond: FAIL.append(n)
def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
def setv(sel,val): r=J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.2); return r
def openrow(txt): r=J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"""); time.sleep(.4); return r
def openfirst(txt): r=J(f"""(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>{{const c=r.querySelector('[role=cell]'); return c && c.innerText.trim()==={json.dumps(txt)};}}); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"""); time.sleep(.4); return r
def dialog(): return J("(document.querySelector('aside[role=dialog]')||{}).innerText||''")
def body(): return J("document.body.innerText")
def go(f): c.goto(f'http://127.0.0.1:{p}/{f}'); time.sleep(.6)
try:
    c.size(1440,1000)
    # ---- PT-02det ----
    go('PT-02det.dc.html')
    ok('pt02det total inicial', '360.904,99' in body(), body()[:0])   # CTL-4: a SOL-2026-07 leva MAP 79.500 kg (80.000 − 500 kg em custódia da OS-0417, revisão do 853a6a8) e Ureia 1.140 kg (era 293.166,01 com MAP 62.500 e sem Ureia)
    ok('prim sem mudança avisa', clk('Submeter proposta v2')=='ok' and 'Nada mudou' in T(), T())
    openrow('O frete CIF'); ok('esclarecimento abre form', 'Sua resposta' in dialog())
    clk('Salvar','aside[role=dialog]'); ok('valida resposta vazia', 'Informe' in dialog(), dialog()[:200])
    setv('[id$=_resp]','Sim, CIF até o Galpão 2 para os 5 itens.'); clk('Salvar','aside[role=dialog]')
    ok('resposta registrada', 'Resposta registrada' in T() and 'Respondida' in J("[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('O frete CIF')>=0).innerText"), T())
    openfirst('MAP 11-52'); ok('item abre form preço', 'Preço' in dialog())
    setv('[id$=_preco]','3,70'); clk('Salvar','aside[role=dialog]')
    row=J("[...document.querySelectorAll('[role=row]')].find(r=>{const c=r.querySelector('[role=cell]'); return c&&c.innerText.trim()==='MAP 11-52';}).innerText.replace(/\\s+/g,' ')")
    ok('total da linha recalculado', '294.150,00' in row, row)   # CTL-4: 79.500 kg × R$ 3,70 (era 80.000 kg antes da revisão do 853a6a8; 62.500 kg antes da CTL-4)
    ok('prim submete v2', clk('Submeter proposta v2')=='ok' and 'v2 submetida' in T() and 'v1 fica preservada' in T(), T())
    ok('prim vira v3 sem duplicar', 'Submeter proposta v3' in body())
    clk('Submeter proposta v3'); ok('v3 sem mudança avisa', 'Nada mudou desde a v2' in T(), T())
    openrow('CIF · incluso'); ok('condições abre form', 'Frete' in dialog() and 'Validade' in dialog())
    clk('Cancelar','aside[role=dialog]')
    c.shot('_probe/pt02det.png')
    # ---- PT-03 ----
    go('PT-03.dc.html')
    openrow('caixas padrão'); setv('[id$=_vol]','5000'); clk('Salvar','aside[role=dialog]')
    ok('volume acima do publicado bloqueado', 'Máximo' in dialog(), dialog()[:300])
    setv('[id$=_vol]','1800'); clk('Salvar','aside[role=dialog]')
    clk('Enviar proposta'); ok('envia proposta', 'intenção de pedido' in T(), T())
    clk('Enviar proposta'); ok('reenvio não duplica', 'nada foi duplicado' in T(), T())
    # ---- PT-05det ----
    go('PT-05det.dc.html')
    openrow('Carga 3'); ok('carga 3 abre form', 'Placa do caminhão' in dialog())
    setv('[id$=_placa]','QAS-2C41'); clk('Salvar','aside[role=dialog]'); ok('previsão salva', 'Previsão da carga 3 atualizada' in T(), T())
    openrow('Cargas 1–2'); ok('carga recebida em consulta', 'Consulta' in dialog() or 'permissão' in dialog(), dialog()[:200]); clk('Fechar','aside[role=dialog]')
    clk('Abrir divergência'); clk('Abrir divergência'); ok('divergência idempotente', 'nada foi duplicado' in T(), T())
    ok('drawer primário', clk('Enviar documento da carga 3')=='ok' and 'Documento da carga 3' in body())
    # ---- PT-07 ----
    go('PT-07.dc.html')
    openrow('Fertisul Fertilizantes'); ok('credenciamento abre form', 'Regiões' in dialog() and 'E-mail de cotação' in dialog())
    setv('[id$=_mail]','invalido'); clk('Salvar','aside[role=dialog]'); ok('e-mail validado', 'E-mail inválido' in dialog())
    setv('[id$=_mail]','cotacoes@fertisul.com.br'); clk('Salvar','aside[role=dialog]'); ok('perfil salvo', 'correspondência de convites recalculada' in T(), T())
    clk('+ Convidar usuário'); ok('novo usuário', 'Convidar usuário' in dialog(), dialog()[:120])
    setv('[id$=_nome]','Paulo Mendes'); setv('[id$=_mail]','paulo@fertisul.com.br'); clk('Salvar','aside[role=dialog]')
    ok('convite enviado', 'Convite enviado a Paulo Mendes' in T() and 'Paulo Mendes' in body(), T())
    openrow('Marta Nunes'); ok('admin em consulta', 'permissão' in dialog(), dialog()[:200]); clk('Fechar','aside[role=dialog]')
    openrow('Mensagens de negócio'); setv('[id$=_canal]','Portal + WhatsApp'); clk('Salvar','aside[role=dialog]'); ok('preferência salva', 'Preferência salva' in T(), T())
    # ---- PT-04det / PT-06 / PT-01 ----
    go('PT-04det.dc.html')
    clk('Conferir documento'); ok('DEMO-10 conferir', 'Liberado até agora: R$ 300 mil de R$ 850 mil' in T(), T())
    clk('Acompanhar liberação'); ok('DEMO-10 acompanhar', 'aceite não equivale a desembolso' in T(), T())
    ok('DEMO-10 texto parcela', '1ª parcela de R$ 300 mil liberada' in body())
    go('PT-04.dc.html'); regra = J("(document.querySelector('button.g2-info[aria-label=\"Regras desta tela\"]')||{getAttribute:()=>''}).getAttribute('data-dica')") or ''   # o rodapé virou a dica ⓘ (menos texto, 14/10)
    ok('DEMO-10 PT-04', 'Aprovado · documento pendente' in body() and 'Condição de crédito aceita não equivale a desembolso' in regra, regra)
    go('PT-06.dc.html'); openrow('Selecionadas'); ok('indicador abre origem', 'Valor calculado' in dialog() and 'CT-2026-11' in dialog(), dialog()[:300]); clk('Fechar','aside[role=dialog]')
    go('PT-01.dc.html'); openrow('SOL-2026-07'); ok('oportunidade em consulta com origem', 'Convite enviado' in dialog(), dialog()[:200])
    print('js err:', J("window.__err||'nenhum'"))
finally:
    c.close(); srv.terminate()
print('FALHAS:', FAIL or 'nenhuma')
