# -*- coding: utf-8 -*-
"""EX-53 D11b · dedicação ativa de quem saiu do cadastro de pessoas (achado do Codex no PR #134: 4311510516 e 6262533728). No Chrome, 1440 × 900.
A CD-04 não exclui pessoa (inativa); a dedicação órfã vem de estado já gravado. O teste monta esse estado no armazenamento local, como o Codex
reproduziu, e faz o resto pela tela.
  O1 CF-06 pela tela: Zé 30 e Otávio 20 HH/semana de Mecânico; a dica do Backlog da oficina diz "Mecânico 50 HH/semana (2 pessoas)"
  O2 o Zé sai da fonte de pessoas com a dedicação ativa: o Mecânico fica sem semanas (o total não é parcial) e a dica diz "pessoa saiu do cadastro"
  O3 a CF-06 lista o Zé como "Saiu do cadastro · Rever dedicação"; o painel abre só com o motivo e "Retirar dedicação" (sem horas, sem "Salvar")
  O4 retirar com motivo: a linha sai da lista e o cartão volta a mostrar o Mecânico pela dedicação do Otávio ("Mecânico 20 HH/semana (1 pessoa)",
     semanas = HH ÷ 20), sem "a revisar" (retirada não gera falso alerta)
  O5 o histórico continua: a dedicação do Zé tem duas versões gravadas (definida e retirada), com motivo e recibo
  O6 nenhum erro de JavaScript
Contraprova: o render do HEAD 5401dc50 reprova O2 e O3 (dica "não configurada"; a CF-06 não mostra a dedicação órfã).
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B cf06_orfa_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:900])

ORA = r"""(()=>{ const c=window.__man.manGet(); let h=0;
  Object.values(c.oms).filter(o=>['A liberar','Liberadas','Em execução'].indexOf(o.etapa)>=0&&o.esp==='Mecânico').forEach(o=>{ const t=Number(o.tempo); if(t>0) h+=t; });
  return h; })()"""
CARD = r"""(()=>{ const k=[...document.querySelectorAll('[role=tabpanel] .pg-card')].filter(x=>x.getClientRects().length).find(x=>/Backlog da oficina/.test(x.innerText));
  if(!k) return null; const s=k.querySelector('.pg-sub'), t=k.querySelector('.pg-tip');
  return {sub:s?s.innerText.replace(/\s+/g,' ').trim():'', dica:t?t.getAttribute('data-dica')||'':''}; })()"""
F = lambda v: ('%.1f' % v).replace('.', ',').replace(',0', '') if abs(v - round(v)) < 1e-9 else ('%.1f' % v).replace('.', ',')
SETV = "((k,val)=>{ const i=document.getElementById(k); if(!i) return 'sem '+k; const P=i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:(i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; })"
BTN = "((t)=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(a=>a.getClientRects().length); const b=a&&[...a.querySelectorAll('button')].find(b=>(b.innerText||'').trim()===t); if(!b) return false; b.click(); return true; })"
ABRE = "((n)=>{ const r=[...document.querySelectorAll('[data-g2g=g_cap] [role=row][data-rid]')].find(r=>r.innerText.indexOf(n)>=0); if(!r) return 'sem linha'; (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); return 'ok'; })"
LINHA = "((n)=>{ const r=[...document.querySelectorAll('[data-g2g=g_cap] [role=row][data-rid]')].find(r=>r.innerText.indexOf(n)>=0); return r?r.innerText.replace(/\\s+/g,' ').trim():null; })"
PAINEL = r"""(()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(a=>a.getClientRects().length); if(!a) return null;
  const vis=e=>!!(e&&e.getClientRects().length); return {titulo:(a.querySelector('h2,h3')||{}).innerText||'', horas:vis(a.querySelector('#c6_h0')), motivo:vis(a.querySelector('#c6_motivo')),
  botoes:[...a.querySelectorAll('button')].filter(vis).map(b=>(b.innerText||'').trim()).filter(Boolean), texto:a.innerText.replace(/\s+/g,' ').slice(0,400)}; })()"""
# o estado gravado é achado pelo conteúdo (o registro de capacidade), sem depender do nome da chave
ESTADO = "Object.keys(localStorage).find(k=>{ try{ const x=JSON.parse(localStorage.getItem(k)); return !!(x&&x.conf&&x.conf.capacidadePessoas&&x.cadPessoas); }catch(e){ return false; } })"
port, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda p: f'http://127.0.0.1:{port}/{p}'
erros = []
def card():
    # sai antes: a mesma URL com âncora não recarrega a página, e o cartão seguiria com o estado anterior
    c.goto('about:blank', .1); c.goto(U('PG.dc.html#mod=man'), 2.4); erros.extend(J("window.__e") or []); return J(CARD) or {}
def dedica(nome, horas, motivo):
    c.goto(U('CF-06.dc.html'), 1.8); ab = J(ABRE + f"({json.dumps(nome)})"); time.sleep(.6)
    s = [J(SETV + f"('c6_h0',{json.dumps(horas)})"), J(SETV + f"('c6_motivo',{json.dumps(motivo)})")]; time.sleep(.3)
    ok = J(BTN + "('Salvar dedicação')"); time.sleep(.9); erros.extend(J("window.__e") or []); return [ab, s, ok]
def semanas(sub): return [x for x in sub.replace(' ', ' ').split(' — ')[0].split(' · ') if 'semana' in x]
try:
    c.aparelho(1440, 900); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    c.goto(U('MA.dc.html'), 1.2); hm = J(ORA) or 0; print('      oráculo HH de Mecânico:', hm)
    # grava a fonte de pessoas pela CD-04 sem tocar na Oficina (o calendário do Comercial), para o estado ter a lista de pessoas
    c.goto(U('CD-04.dc.html'), 1.8)
    J("(()=>{ const t=[...document.querySelectorAll('[role=tab]')].find(t=>/^Equipes/.test(t.innerText.trim())); if(t) t.click(); })()"); time.sleep(.6)
    J("(()=>{ const r=[...document.querySelectorAll('[data-g2g=g_eq] [role=row][data-rid]')].find(r=>/Comercial/.test(r.innerText)); if(r) (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); })()"); time.sleep(.6)
    cd = [J(SETV + "('fx_g_eq_cal','seg–sáb · 06–15h')")]; time.sleep(.3); cd.append(J(BTN + "('Salvar')")); time.sleep(.9)
    d1 = dedica('Zé', '30', 'teste cf06_orfa: dedicação do Zé à mecânica'); d2 = dedica('Otávio', '20', 'teste cf06_orfa: dedicação do Otávio à mecânica')
    k1 = card(); print('      O1:', cd, d1, d2, k1)
    chk('O1 CF-06 pela tela: Zé 30 e Otávio 20 HH/semana de Mecânico; a dica diz "Mecânico 50 HH/semana (2 pessoas)"',
        cd == ['ok', True] and d1[0] == 'ok' and d1[2] and d2[0] == 'ok' and d2[2] and 'Mecânico 50 HH/semana (2 pessoas)' in k1.get('dica', ''), [cd, d1, d2, k1])
    # estado legado: o Zé sai da fonte de pessoas e a dedicação ativa continua (a CD-04 não exclui; o Codex reproduziu assim em 6262533728)
    tira = J("(()=>{ const k=" + ESTADO + "; if(!k) return 'sem estado'; const x=JSON.parse(localStorage.getItem(k)); const ze=x.cadPessoas.pessoas.find(p=>p.v.nome==='Zé'); if(!ze) return 'sem Zé';"
             " x.cadPessoas.pessoas=x.cadPessoas.pessoas.filter(p=>p.id!==ze.id); localStorage.setItem(k,JSON.stringify(x)); return [ze.id, !!(x.conf.capacidadePessoas[ze.id]&&x.conf.capacidadePessoas[ze.id].ativa)]; })()")
    k2 = card(); print('      O2:', tira, k2)
    chk('O2 o Zé saiu da fonte de pessoas com a dedicação ativa: o Mecânico fica sem semanas e a dica diz "pessoa saiu do cadastro"',
        isinstance(tira, list) and tira[1] and not [x for x in semanas(k2.get('sub', '')) if x.startswith('Mecânico')] and 'pessoa saiu do cadastro' in k2.get('dica', '') and 'Mecânico' in k2.get('dica', ''), [tira, k2])
    c.goto(U('CF-06.dc.html'), 1.8); lz = J(LINHA + "('Zé')"); ab = J(ABRE + "('Zé')"); time.sleep(.6); pn = J(PAINEL) or {}
    print('      O3:', lz, ab, pn)
    chk('O3 a CF-06 lista o Zé como "Saiu do cadastro · Rever dedicação"; o painel tem só o motivo e "Retirar dedicação" (sem horas, sem "Salvar")',
        bool(lz) and 'Saiu do cadastro' in lz and 'Rever dedicação' in lz and ab == 'ok' and pn.get('motivo') and not pn.get('horas')
        and 'Retirar dedicação' in pn.get('botoes', []) and 'Salvar dedicação' not in pn.get('botoes', []), [lz, ab, pn])
    rt = [J(SETV + "('c6_motivo','teste cf06_orfa: o Zé saiu do cadastro; retirada da dedicação')")]; time.sleep(.3); rt.append(J(BTN + "('Retirar dedicação')")); time.sleep(.9)
    lz2 = J(LINHA + "('Zé')"); erros.extend(J("window.__e") or []); k4 = card(); sm = hm / 20 if hm else 0
    esperado = 'Mecânico ' + F(hm) + ' (' + F(sm) + ' ' + ('semana' if sm < 2 else 'semanas') + ')'
    print('      O4:', rt, lz2, esperado, k4)
    chk(f'O4 retirada com motivo: a linha sai e o cartão volta a "{esperado}" com "Mecânico 20 HH/semana (1 pessoa)", sem "a revisar"',
        rt == ['ok', True] and lz2 is None and hm > 0 and esperado in k4.get('sub', '').replace(' ', ' ') and 'Mecânico 20 HH/semana (1 pessoa)' in k4.get('dica', '')
        and 'a revisar' not in k4.get('dica', ''), [rt, lz2, k4])
    hist = J("(()=>{ const k=" + ESTADO + "; const x=JSON.parse(localStorage.getItem(k)); return (x.conf.ev||[]).filter(e=>e.tipo==='capacidade'&&e.alvo===" + json.dumps(tira[0] if isinstance(tira, list) else '') + ")"
             ".map(e=>({t:e.t,motivo:!!e.motivo,recibo:!!e.id,depois:e.depois})); })()")
    print('      O5:', hist)
    chk('O5 o histórico continua: a dedicação do Zé tem a versão definida e a retirada, com motivo e recibo',
        isinstance(hist, list) and [h['t'] for h in hist] == ['Dedicação semanal definida', 'Dedicação retirada'] and all(h['motivo'] and h['recibo'] for h in hist), hist)
    chk('O6 nenhum erro de JavaScript', not erros, erros[:5])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK+FAIL} ok')
sys.exit(1 if FAIL else 0)
