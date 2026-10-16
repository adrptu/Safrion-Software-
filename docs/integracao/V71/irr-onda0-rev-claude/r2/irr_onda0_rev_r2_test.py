# -*- coding: utf-8 -*-
"""Revisão do Claude, PR #79 R2 (HEAD 392bc494; IRR-ONDA0, autor Codex): navegador real (Chrome headless por CDP), dados sintéticos.
V1 R1 término no IR-03det · V2 início/pausa/retomada/término com o relógio simulado · V3 R2 piso da ficha no IR-02 ·
V4 R3 divergência com papel e motivo · V5 água × fertirrigação (DEC-2609-10) · V6 teclado e foco · V7 390 px com toque ·
V8 cenário salvo na base abre sem perda. R2: F1 (área × tempo exige motivo e conferência), F2 (relógio por ordem), F3 (medição única),
S4 (zero medido), P1–P3 persistência e retorno (recarregar no meio do fluxo), Q1–Q4 contraexemplos do revisor (irrigante/gestor).
Uso: python3 irr_onda0_rev_test.py <gen37> [--base]   (RENDER_DIR opcional; BASE_RENDER = _render da base para o V8)."""
import sys, os, time, json
G = sys.argv[1]; sys.path.insert(0, G)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(G, '_render')
RB = os.environ.get('BASE_RENDER')
OK, FAIL, ACH_OK, ACH_FAIL = [], [], [], []
def chk(n, c, x=''):
    (OK if c else FAIL).append(n); print(('OK   ' if c else 'FALHA'), n, '' if c else str(x)[:600], flush=True)
def ach(n, c, x=''):
    (ACH_OK if c else ACH_FAIL).append(n); print(('ok   ' if c else 'ACHADO'), n, '' if c else str(x)[:600], flush=True)
p, srv = servir(R); c = Chrome(); J = c.js; U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
pb = srvb = None
if RB: pb, srvb = servir(RB)
DLG = "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getBoundingClientRect().width>1)"
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
def dlg():
    return J("(()=>{const d=" + DLG + "; if(!d) return null; const n=" + N + "; return {lab:d.getAttribute('aria-label')||'',txt:n(d.innerText),foco:d.contains(document.activeElement),"
             "cob:(d.querySelector('#tm_cob')||{value:null}).value,vol:(d.querySelector('#tm_vol')||d.querySelector('#cm_vol')||{value:null}).value,mot:(d.querySelector('#cm_mot')||{value:null}).value,"
             "radios:d.querySelectorAll('input[type=radio]').length};})()")
def toast():
    for _ in range(12):
        t = J("((document.querySelector('.g2toast')||{}).innerText||'').trim()")
        if t: return t
        time.sleep(.25)
    return ''
def head(): return J(f"{N}((document.querySelector('header')||{{}}).innerText)") or ''
def main(): return J(f"{N}((document.querySelector('main')||{{}}).innerText)") or ''
def alvo(txt, raiz=None):
    r = json.dumps(raiz)
    return J(f"""(()=>{{const R={r}?{DLG}:document; if(!R) return null; const n={N};
      const b=[...R.querySelectorAll('button,a,[role=button]')].find(b=>n(b.innerText)==={json.dumps(txt)}&&b.getBoundingClientRect().width>0); if(!b) return null;
      b.scrollIntoView({{block:'center'}}); const q=b.getBoundingClientRect(); return [q.left+q.width/2,q.top+q.height/2,q.width,q.height,q.left,q.right];}})()""")
def clicar(txt, raiz=None, toque=False, espera=.8):
    r = alvo(txt, raiz)
    if not r: return None
    time.sleep(.2); r = alvo(txt, raiz)
    if toque: c.toque(r[0], r[1])
    else: c.mouse(r[0], r[1]); c.mouse(r[0], r[1], 'mousePressed', 'left'); c.mouse(r[0], r[1], 'mouseReleased', 'left')
    time.sleep(espera); return r
def preencher(fid, val):
    return J(f"""(()=>{{const d={DLG}; const e=d&&d.querySelector('#{fid}'); if(!e) return null; e.focus();
      const P=e.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:(e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(e,{json.dumps(val)});
      e.dispatchEvent(new Event('input',{{bubbles:true}})); e.dispatchEvent(new Event('change',{{bubbles:true}})); return e.value;}})()""")
def S(): t = J("localStorage.getItem('talhao-os-irrigacao-v1')"); return json.loads(t) if t else None
def ordem(id_):
    s = S(); o = s and s['ordens'].get(id_)
    if not o: return None
    return {'etapa': o['etapa'], 'conf': o.get('conf'), 'ps': o['passadas'], 'pausas': o['exec'].get('pausas', []), 'tr': [[t['q'], t['ev'], t['quem']] for t in o['trilha']], 'lam': o.get('lam')}
def ap(sid, os_):
    s = S(); return [{'vol': a['vol'], 'cob': a['cob']} for a in s['setores'][sid]['bal']['ap'] if a['os'] == os_] if s else []
def deficit(setor='Pivô 2', faz=None):
    """déficit lido na IR-01 (linha do setor), como a pessoa vê; navega para a IR-01"""
    abrir('IR-01.dc.html' + ('#faz=' + faz if faz else ''), 1.8)
    t = J(f"(()=>{{const n={N}; const r=[...document.querySelectorAll('[role=row]')].map(r=>n(r.innerText)).find(t=>t.indexOf({json.dumps(setor)}+' ')>=0&&/mm/.test(t)); return r||'';}})()")
    import re
    m = re.search(re.escape(setor) + r'(?!\d).*?≈?(\d+,\d) mm', t); return float(m.group(1).replace(',', '.')) if m else t
def P2def(): return deficit('Pivô 2')
def reset(perfil=None):
    coletar(); c.goto(U('Main.dc.html'), .3); J("localStorage.clear();sessionStorage.clear();1")
    if perfil: J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)});1")
ERRJS = []
def coletar():
    try: ERRJS.extend(J("(window.__errs||[]).filter(e=>!/favicon|Failed to load resource/i.test(e))") or [])
    except Exception: pass
def abrir(h, espera=1.6):
    coletar(); c.goto(U('Main.dc.html'), .2); c.goto(U(h), espera)
def jserros(): coletar(); return sorted(set(ERRJS))
def iniciar_0419():
    abrir('IR-03det.dc.html#OS-0419'); clicar('Iniciar irrigação'); return toast()
def linha(prefixo):
    return J(f"(()=>{{const n={N}; return [...document.querySelectorAll('[role=row]')].map(r=>n(r.innerText)).find(t=>t.indexOf({json.dumps(prefixo)})===0)||null;}})()")
def thdr():
    """rótulo do término no cabeçalho (392b: acompanha o antecipado)"""
    for t in ('Registrar término antecipado', 'Confirmar término'):
        if alvo(t): return t
    return None
def tprim():
    d = dlg(); return (d and d['lab'].split(' · ')[0]) or 'Confirmar término'
def mot_visivel(fid): return bool(J(f"(()=>{{const d={DLG}; const e=d&&d.querySelector('#{fid}'); return !!e&&e.getBoundingClientRect().width>0;}})()"))
def terminar(cob, vol, motivo=None):
    """abre o término pelo cabeçalho, preenche e grava; motivo só se o campo aparecer (ou se forçado)"""
    clicar(thdr()); d0 = dlg(); preencher('tm_cob', cob); preencher('tm_vol', vol); time.sleep(.3)
    pedido = mot_visivel('tm_mot')
    if motivo and pedido: preencher('tm_mot', motivo)
    clicar(tprim(), 'dlg'); return {'painel0': d0, 'motivo_pedido': pedido, 'toast': toast(), 'depois': dlg()}
def selos(): return head()
def recarregar(espera=1.8):
    """recarga real (F5); navegar para a mesma URL com # não recarrega a página"""
    coletar(); c.call('Page.reload', {'ignoreCache': False}); time.sleep(espera)
try:
    c.aparelho(1440, 900)
    # ============ V1 · R1 término (IR-03det) + F1 ============
    reset(); d0 = P2def()
    t = iniciar_0419(); h = head(); o = ordem('OS-0419')
    chk('V1a OS-0419 inicia (Em execução); déficit do P2 antes = 11,2 mm; cabeçalho "Registrar término antecipado"', 'Em execução' in h and o and o['etapa'] == 'Em execução' and d0 == 11.2 and 'Registrar término antecipado' in h, [t, h, d0])
    clicar(thdr()); d = dlg()
    chk('V1b painel abre sem área e sem leitura pré-preenchidas (nenhuma "Volta completa" marcada)', bool(d) and d['cob'] == '' and d['vol'] == '' and d['radios'] == 0 and 'Volta completa' not in d['txt'], d)
    chk('V1c antes do fim previsto: "Término antecipado" e rótulo "simulado"', bool(d) and 'término antecipado' in d['lab'].lower() and 'simulado' in d['txt'].lower(), d)
    prim = tprim(); clicar(prim, 'dlg'); d = dlg(); o = ordem('OS-0419')
    chk('V1d confirmar logo depois, sem área e sem leitura: recusado junto dos campos, nada gravado', bool(d) and 'Informe a área real' in d['txt'] and 'Informe o volume medido' in d['txt']
        and o['etapa'] == 'Em execução' and o['ps'][0]['vol'] is None, [d and d['txt'][:400], o and o['etapa']])
    preencher('tm_cob', '10'); clicar(prim, 'dlg'); d = dlg()
    chk('V1e só a área (sem leitura): recusado; a leitura nunca vem da estimativa', bool(d) and 'Informe o volume medido' in d['txt'] and ordem('OS-0419')['etapa'] == 'Em execução', d and d['txt'][:300])
    preencher('tm_vol', '1000'); time.sleep(.3); mv = mot_visivel('tm_mot'); clicar(prim, 'dlg'); d = dlg(); o = ordem('OS-0419')
    chk('F1a 10 ha a 0 min de bombeamento: campo de motivo visível e gravar sem motivo é recusado, nada gravado', mv and bool(d) and 'Informe o motivo' in d['txt'] and o['ps'][0]['vol'] is None, [mv, d and d['txt'][-300:]])
    preencher('tm_mot', 'Sensor de horário parado (sintético)'); clicar(prim, 'dlg'); t = toast(); o = ordem('OS-0419'); d = dlg(); h = head()
    chk('V1f término antecipado grava só o informado (Parcial, 10 ha, 1.000 m³) e o motivo', d is None and o['ps'][0]['st'] == 'Parcial' and o['ps'][0]['cob'] == 10 and o['ps'][0]['vol'] == 1000 and o['ps'][0].get('motivoTempo') == 'Sensor de horário parado (sintético)', [t, o and o['ps']])
    tr = ' | '.join(x[1] for x in o['tr'])
    chk('V1g trilha "Término antecipado (simulado) · … tempo incompatível a conferir · motivo"; Em conferência com selo "Área e tempo a conferir"', 'Término antecipado (simulado)' in tr and 'tempo incompatível a conferir' in tr and o['etapa'] == 'Em conferência' and 'Área e tempo a conferir' in h, [o['etapa'], h, tr[-300:]])
    chk('V1h/F1b nada creditado antes da validação: sem aplicação da OS-0419 e déficit do P2 segue 11,2 mm', ap('P2', 'OS-0419') == [] and P2def() == 11.2, [ap('P2', 'OS-0419'), P2def()])
    abrir('IR-03det.dc.html#OS-0419:conferir'); d = dlg(); mv = mot_visivel('cm_mot')
    chk('F1c conferência: pede motivo mesmo dentro da tolerância (−7,5 %) e avisa "área e tempo a conferir"', bool(d) and mv and 'área e tempo a conferir' in d['txt'] and bool(alvo('Aceitar com motivo', 'dlg')), d and d['txt'][:300])
    clicar('Aceitar com motivo', 'dlg'); d = dlg()
    chk('F1d validar sem motivo é recusado', bool(d) and 'motivo' in d['txt'].lower() and ordem('OS-0419')['etapa'] == 'Em conferência', d and d['txt'][-200:])
    preencher('cm_mot', 'Área e leitura conferidas em campo (sintético)'); clicar('Aceitar com motivo', 'dlg'); t = toast(); o = ordem('OS-0419')
    chk('F1e validado com motivo: encerra e credita só a faixa (1.000 m³ em 10 ha); quem e motivo gravados', o['etapa'] == 'Encerradas' and ap('P2', 'OS-0419') == [{'vol': 1000, 'cob': 10}] and (o['ps'][0].get('tempoConferido') or {}).get('quem') == 'Ana' and P2def() == 11.2,
        [t, o['etapa'], ap('P2', 'OS-0419'), o['ps'][0].get('tempoConferido')])
    # F1 · o contraexemplo A1: volta completa a 0 h
    reset(); iniciar_0419(); r = terminar('80', '8480'); o = ordem('OS-0419')
    chk('F1f 80 ha e 8.480 m³ a 0 h: motivo pedido na tela e gravar sem ele é recusado (nada gravado)', r['motivo_pedido'] and r['depois'] is not None and 'Informe o motivo' in r['depois']['txt'] and o['ps'][0]['vol'] is None, [r['motivo_pedido'], r['depois'] and r['depois']['txt'][-200:]])
    preencher('tm_mot', 'Volta informada pelo operador (sintético)'); clicar(tprim(), 'dlg'); t = toast(); o = ordem('OS-0419'); dd = P2def()
    chk('F1g com motivo: Em conferência, sem crédito; P2 segue 11,2 mm (não 1,7)', o['etapa'] == 'Em conferência' and ap('P2', 'OS-0419') == [] and dd == 11.2 and (o['conf'] or {}).get('st') == 'Área e tempo a conferir', [t, o['etapa'], o['conf'], dd])
    # F1 · caso compatível com o tempo: sem motivo e com crédito direto
    reset(); iniciar_0419(); clicar('Pausar'); clicar('Retomar irrigação'); r = terminar('5', '540'); o = ordem('OS-0419')
    chk('F1h após 60 min bombeando, 5 ha (≤ 80 × 60/871 = 5,51 ha) e 540 m³: sem motivo, grava e credita a faixa', not r['motivo_pedido'] and r['depois'] is None and ap('P2', 'OS-0419') == [{'vol': 540, 'cob': 5}], [r['motivo_pedido'], r['toast'], ap('P2', 'OS-0419'), o['etapa']])
    print('     F1h:', r['toast'][:200])
    # ============ V2 · início → pausa → retomada → término (relógio por ordem) ============
    reset(); iniciar_0419(); o = ordem('OS-0419'); ag0 = S()['agora']
    chk('V2a início hoje 20:02 (1202 min) e o relógio global não muda (06:12 = 372)', o['ps'][0]['st'] == 'Em execução' and o['ps'][0]['iniReal'] == 1202 and ag0 == 372, [o['ps'][0], ag0])
    clicar('Pausar'); h = head(); o = ordem('OS-0419')
    chk('V2b Pausar: selo Pausada, etapa Em execução, primária Retomar irrigação', 'Pausada' in h and 'Em execução' in h and 'Retomar irrigação' in h and len(o['pausas']) == 1, [h, o['pausas']])
    abrir('IR-03det.dc.html#OS-0419:termino'); d = dlg(); t = toast()
    chk('V2c pausada: o link direto de término não abre o painel', d is None, [d, t])
    clicar('Retomar irrigação'); h = head(); o = ordem('OS-0419')
    chk('V2d Retomar: sem selo Pausada, primária de término, pausa fechada; relógio global segue 372', 'Pausada' not in h and bool(thdr()) and o['pausas'][0]['fim'] is not None and S()['agora'] == 372, [h, o['pausas'], S()['agora']])
    chk('V2e nada creditado entre início, pausa e retomada', not ap('P2', 'OS-0419') and P2def() == 11.2, [ap('P2', 'OS-0419')])
    abrir('IR-03det.dc.html#OS-0419'); r = terminar('30', '3000', 'Leitura de área pelo app (sintético)'); o = ordem('OS-0419')
    pz = o['pausas'][0]; fim = o['ps'][0].get('fimReal'); ini = o['ps'][0]['iniReal']; trl = [(x[0], x[1][:70]) for x in o['tr']][-4:]
    print('     V2 horários: início', ini, '· pausa', pz['ini'], '→', pz['fim'], '· término', fim, '· trilha', trl)
    chk('V2f término depois da retomada (início ≤ pausa ≤ retomada ≤ término) e "1,0 h de bombeamento" (pausa descontada)', fim is not None and ini <= pz['ini'] <= pz['fim'] <= fim and any('1,0 h de bombeamento' in x[1] for x in o['tr']), [ini, pz, fim, trl])
    chk('V2g 30 ha em 60 min pede motivo; com ele, sem crédito até conferir', r['motivo_pedido'] and ap('P2', 'OS-0419') == [] and o['etapa'] == 'Em conferência', [r, ap('P2', 'OS-0419')])
    # ============ F2 · relógio por ordem: a OS-0423 continua na sua janela ============
    reset(); abrir('IR-03det.dc.html#OS-0423:conflito'); clicar('Aplicar janela', 'dlg'); iniciar_0419()
    abrir('IR-03det.dc.html#OS-0423'); clicar('Iniciar irrigação'); t = toast(); s = S(); p23 = s['ordens']['OS-0423']['passadas'][0]
    chk('F2a depois de iniciar a OS-0419 (20:02), a OS-0423 inicia às 15:02, dentro da janela 15:00–17:00; relógio global 372', p23.get('iniReal') == 902 and s['agora'] == 372 and '15:02' in t, [t, p23.get('iniReal'), s['agora']])
    # ============ V3 · R2 piso da ficha (IR-02) ============
    reset(); abrir('IR-02.dc.html#programar=P2', 2.0); d = dlg()
    chk('V3a Santa Rita · Pivô 2: passadas de 6,7 mm (ficha a 100 %) e 9,0 h', bool(d) and '2 de 6,7 mm' in d['txt'] and '9,0 h por passada' in d['txt'], d and d['txt'][-420:])
    print('     P2:', d and d['txt'][d['txt'].find('DÉFICIT'):][:260])
    abrir('IR-02.dc.html#faz=Lagoa Grande', 1.4); abrir('IR-02.dc.html#programar=PV19', 2.0); d = dlg()
    chk('V3b Lagoa Grande · PV19: 1 passada de 7,21 mm (ficha demonstrativa) e 16,0 h', bool(d) and '1 de 7,21 mm' in d['txt'] and '16,0 h' in d['txt'], d and d['txt'][-420:])
    print('     PV19:', d and d['txt'][d['txt'].find('DÉFICIT'):][:360])
    clicar('Programar', 'dlg'); t = toast(); s = S()
    oid = s and next((k for k, o in s['ordens'].items() if o['setor'] == 'PV19'), None); o = ordem(oid) if oid else None
    chk('V3c ordem do PV19 nasce com a lâmina e a duração da ficha (7,21 mm · 960 min)', bool(o) and abs(o['ps'][0]['lam'] - 7.21) < 1e-9 and o['ps'][0]['dur'] == 960, [t, oid, o and o['ps']])
    reset(); abrir('IR-01.dc.html#faz=Lagoa Grande', 2.0)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf('Pivô 19')===0); r&&(r.querySelector('[role=cell] span')||r).click();})()"); time.sleep(.8)
    J("(()=>{const e=document.querySelector('#fx_g_set_lmax'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,'5'); e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true}));})()")
    clicar('Salvar', 'dlg'); t = toast(); lm = (S() or {'setores': {'PV19': {}}})['setores']['PV19'].get('lmax')
    abrir('IR-02.dc.html#programar=PV19', 2.0); d = dlg()
    chk('V3d limite 5 mm < 7,21 mm da ficha: bloqueio com motivo e sem "Programar"', lm == 5 and bool(d) and 'incompatível' in d['txt'] and not alvo('Programar', 'dlg'), [t, lm, d and d['txt'][-300:]])
    reset(); abrir('IR-01.dc.html', 2.0); r1 = linha('Pivô 2') or J(f"(()=>{{const n={N}; return [...document.querySelectorAll('[role=row]')].map(r=>n(r.innerText)).find(t=>/Pivô 2 /.test(t))||'';}})()")
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf('Pivô 2')===0); r&&(r.querySelector('[role=cell] span')||r).click();})()"); time.sleep(.8)
    nec = J("(document.querySelector('#fx_g_set_necT')||{}).value") or ''
    chk('S4a IR-01 Pivô 2: necessidade bruta 12,44 mm e programação 13,4 mm explicada no detalhe', 'bruta 12,44 mm' in nec and 'programação 13,4 mm' in nec, [nec, r1])
    # ============ V4 + F3 · divergência (IR-03det OS-0394) ============
    reset(); abrir('IR-03det.dc.html#OS-0394:conferir'); d = dlg()
    chk('V4a −3,8 %: primária "Aceitar com motivo" e secundária "Devolver para conferir o hidrômetro"', bool(d) and bool(alvo('Aceitar com motivo', 'dlg')) and bool(alvo('Devolver para conferir o hidrômetro', 'dlg')) and '−3,8 %' in d['txt'], d and d['txt'][:400])
    clicar('Aceitar com motivo', 'dlg'); d = dlg(); o = ordem('OS-0394')
    chk('V4b Ana sem motivo: recusada junto do campo, leitura 1206 preservada, nada gravado', bool(d) and 'Informe o motivo' in d['txt'] and d['vol'] == '1206' and (o is None or o['etapa'] == 'Em conferência'), [d and d['txt'][:300], o and o['etapa']])
    reset('Rui'); abrir('IR-03det.dc.html#OS-0394:conferir'); preencher('cm_mot', 'conferido por Rui'); clicar('Aceitar com motivo', 'dlg'); t = toast(); o = ordem('OS-0394')
    chk('V4c Rui (almoxarife) com motivo: recusado, nada gravado', 'irrigante ou gestor' in t and (o is None or o['etapa'] == 'Em conferência'), [t, o and o['etapa']])
    clicar('Devolver para conferir o hidrômetro', 'dlg'); t = toast(); o = ordem('OS-0394')
    chk('V4d Rui também não devolve', 'irrigante ou gestor' in t and (o is None or (o['conf'] or {}).get('st') != 'Devolvida'), [t, o and o['conf']])
    reset(); abrir('IR-03det.dc.html#OS-0394:conferir'); preencher('cm_mot', 'Hidrômetro aferido em campo (sintético)'); clicar('Aceitar com motivo', 'dlg'); t = toast(); o = ordem('OS-0394')
    tr = o and ' | '.join(f'{x[1]} ({x[2]})' for x in o['tr'])
    chk('V4e Ana com motivo: encerra; motivo e quem na conferência e na trilha', bool(o) and o['etapa'] == 'Encerradas' and o['conf'].get('motivo') == 'Hidrômetro aferido em campo (sintético)' and o['conf'].get('quem') == 'Ana' and 'motivo: Hidrômetro aferido' in tr, [t, o and o['conf'], tr and tr[-300:]])
    reset('João'); abrir('IR-03det.dc.html#OS-0394:conferir'); clicar('Devolver para conferir o hidrômetro', 'dlg'); t = toast(); o = ordem('OS-0394'); h = head()
    chk('V4f João (irrigante) devolve: segue Em conferência, medição e crédito provisório preservados, selo Devolvida', bool(o) and o['etapa'] == 'Em conferência' and o['conf']['st'] == 'Devolvida' and o['conf']['med'] == 1206
        and ap('P2', 'OS-0394') == [{'vol': 1206, 'cob': 11.6}] and 'Devolvida' in h, [t, o and o['conf'], h])
    abrir('IR-03det.dc.html#OS-0394:conferir'); d = dlg()
    chk('V4g devolvida: a conferência reabre com "Aceitar com motivo" (a devolução não fecha nada)', bool(d) and bool(alvo('Aceitar com motivo', 'dlg')), d and d['txt'][:200])
    reset(); abrir('IR-03det.dc.html#OS-0394:conferir'); preencher('cm_vol', '1291,6'); time.sleep(.4); mv = mot_visivel('cm_mot'); ok1 = bool(alvo('Aceitar com motivo', 'dlg'))
    clicar('Aceitar com motivo' if ok1 else 'Validar e encerrar', 'dlg'); t = toast(); d = dlg(); o = ordem('OS-0394')
    chk('F3a 1.291,6 m³ (+3,0017 % sobre 1.253,96): a tela pede motivo e o comando recusa sem ele', mv and ok1 and d is not None and 'Informe o motivo' in d['txt'] and (o is None or o['etapa'] == 'Em conferência'), [mv, ok1, t, d and d['txt'][-200:]])
    preencher('cm_mot', 'Leitura no limite conferida (sintético)'); clicar('Aceitar com motivo', 'dlg'); o = ordem('OS-0394')
    chk('F3b com motivo encerra com 1.291,6 m³ gravado com precisão', bool(o) and o['etapa'] == 'Encerradas' and abs(o['conf']['med'] - 1291.6) < 1e-9, o and o['conf'])
    reset(); abrir('IR-03det.dc.html#OS-0394:conferir'); preencher('cm_vol', '1253'); time.sleep(.4); mv = mot_visivel('cm_mot'); okv = bool(alvo('Validar e encerrar', 'dlg'))
    clicar('Validar e encerrar', 'dlg'); t = toast(); o = ordem('OS-0394')
    chk('F3c 1.253 m³ (−0,08 %): sem campo de motivo, "Validar e encerrar" encerra', not mv and okv and bool(o) and o['etapa'] == 'Encerradas', [mv, okv, t, o and o['etapa']])
    # ============ S4 · zero medido ============
    reset(); iniciar_0419(); r = terminar('10', '0', 'Hidrômetro zerado (sintético)'); abrir('IR-03det.dc.html#OS-0419'); m = main()
    hid = m[m.find('HIDRÔMETRO'):][:60]; conf = m[m.find('CONFERÊNCIA'):][:110]
    chk('S4b zero medido aparece como medido: "0 m³ medidos" e "0 × … m³ estimados"', '0 m³ medidos' in hid and 'aguardando' not in conf and conf.startswith('CONFERÊNCIA 0 ×'), [r['toast'], hid, conf])
    # ============ V5 · água × fertirrigação (DEC-2609-10) ============
    reset('João'); abrir('IR-03det.dc.html#OS-0419'); m = main(); t = iniciar_0419(); o = ordem('OS-0419')
    chk('V5a só água: liberada pela prontidão, sem agrônomo, e o irrigante inicia', 'automática pela prontidão' in m and bool(o) and o['etapa'] == 'Em execução', [t, o and o['etapa']])
    reset(); abrir('IR-03det.dc.html#OS-0419'); clicar('Adicionar produtos'); preencher('rc_mot', 'Deficiência de N em V10 (sintético)'); clicar('Criar versão v2', 'dlg'); t = toast(); h = head(); m = main()
    chk('V5b com produto (v2): volta a exigir a agrônoma na O.S.; "Iniciar irrigação" sai da tela', 'Liberação do agrônomo' in h and 'agrônoma' in m and not alvo('Iniciar irrigação'), [t, h, m[:300]])
    # ============ V6 · teclado e foco ============
    def foco(): return J(f"(()=>{{const a=document.activeElement; if(!a||a===document.body) return null; const cs=getComputedStyle(a); return {{t:{N}(a.innerText||a.value||a.id||a.tagName).slice(0,60),id:a.id,vis:a.matches(':focus-visible'),ol:cs.outlineStyle+' '+cs.outlineWidth,bs:cs.boxShadow,dlg:!!a.closest('aside[role=dialog]')}};}})()")
    def visivel(f): return bool(f) and f['vis'] and ((f['ol'].split()[0] != 'none' and f['ol'].split()[1] != '0px') or f['bs'] != 'none')
    def tab_ate(txt, n=120):
        for _ in range(n):
            c.tab(); f = foco()
            if f and f['t'] == txt: return f
        return None
    def digitar(s_):
        for ch in s_: c.tecla(ch, text=ch)
    ENTER = lambda: c.tecla('Enter', 'Enter', 13, text='\r')
    ESPACO = lambda: c.tecla(' ', 'Space', 32, text=' ')
    reset(); abrir('IR-03det.dc.html#OS-0419'); J("document.activeElement&&document.activeElement.blur();1")
    f = tab_ate('Iniciar irrigação')
    chk('V6a Tab chega a "Iniciar irrigação" com foco visível', visivel(f), f)
    ENTER(); time.sleep(1); o = ordem('OS-0419')
    chk('V6b Enter inicia', bool(o) and o['etapa'] == 'Em execução', o and o['etapa'])
    rot = thdr(); f = foco()
    if not (f and f['t'] == rot): f = tab_ate(rot, 60)
    gat = f and f['t']; ENTER(); time.sleep(.9); d = dlg(); f = foco()
    chk('V6c Enter no término do cabeçalho abre o painel com o foco dentro (na área real)', bool(d) and bool(f) and f['dlg'] and f['id'] == 'tm_cob', [gat, f])
    c.tecla('Escape', 'Escape', 27); time.sleep(.7); f = foco()
    chk('V6d Esc sem alteração fecha e o foco volta ao gatilho', dlg() is None and bool(f) and f['t'] == rot, f)
    ENTER(); time.sleep(.9); digitar('12'); c.tab(); digitar('1200'); c.tab(); f = foco(); digitar('Leitura manual (teclado)'); time.sleep(.3); d = dlg()
    chk('V6d2 Tab da leitura leva ao motivo (campo do F1 na ordem do teclado)', bool(f) and f['id'] == 'tm_mot', f)
    c.tecla('Escape', 'Escape', 27); time.sleep(.6); d2 = dlg()
    chk('V6e Esc com rascunho pede confirmação e preserva o digitado (área, leitura e motivo)', bool(d2) and 'alterações não salvas' in d2['txt'] and d2['cob'] == '12' and d2['vol'] == '1200' and J(f"(()=>{{const d={DLG}; const e=d&&d.querySelector('#tm_mot'); return e?e.value:null;}})()") == 'Leitura manual (teclado)', [d and (d['cob'], d['vol']), d2 and d2['txt'][-200:]])
    f = tab_ate('Continuar editando', 30); ENTER(); time.sleep(.5)
    f = tab_ate('Registrar término antecipado', 40)
    chk('V6f Tab até a primária do painel com foco visível', visivel(f), f)
    ESPACO(); time.sleep(1); o = ordem('OS-0419'); f = foco()
    chk('V6g Espaço registra o término antecipado (12 ha, 1.200 m³, com motivo) e o painel fecha', dlg() is None and o['ps'][0]['cob'] == 12 and o['ps'][0]['vol'] == 1200 and o['ps'][0].get('motivoTempo') == 'Leitura manual (teclado)', [o['ps'][0], f])
    print('     foco após gravar:', f)
    reset(); abrir('IR-03det.dc.html#OS-0394'); J("document.activeElement&&document.activeElement.blur();1")
    f = tab_ate('Conferir medição'); ENTER(); time.sleep(.9); f = foco(); d = dlg()
    chk('V6h Enter em "Conferir medição" abre o painel com o foco na leitura', bool(d) and bool(f) and f['id'] == 'cm_vol', [f, d and d['lab']])
    c.tab(); f = foco(); digitar('Leitura conferida'); time.sleep(.3)
    chk('V6i Tab leva ao motivo', bool(f) and f['id'] == 'cm_mot', f)
    f = tab_ate('Aceitar com motivo', 10); vf = visivel(f); ESPACO(); time.sleep(1); o = ordem('OS-0394')
    chk('V6j Espaço em "Aceitar com motivo" (foco visível) encerra com o motivo digitado', vf and bool(o) and o['etapa'] == 'Encerradas' and o['conf'].get('motivo') == 'Leitura conferida', [f, o and o['etapa'], o and o['conf']])
    # ============ V7 · 390 px com toque ============
    c.aparelho(390, 844, 2, True)
    def lado(): return J("document.documentElement.scrollWidth>innerWidth+1||document.body.scrollWidth>innerWidth+1")
    def alvo44(txt, raiz=None):
        r = alvo(txt, raiz); return (bool(r) and r[2] >= 44 and r[3] >= 44 and r[4] >= -0.5 and r[5] <= 390.5, r)
    reset(); abrir('IR-01.dc.html', 2.0); l1 = lado()
    abrir('IR-02.dc.html#programar=P2', 2.0); l2 = lado(); a2 = alvo44('Cancelar', 'dlg')
    abrir('IR-03det.dc.html#OS-0419', 1.8); l3 = lado(); a3 = alvo44('Iniciar irrigação'); clicar('Iniciar irrigação', toque=True); o = ordem('OS-0419')
    rot = thdr(); a3b = alvo44(rot); clicar(rot, toque=True); d = dlg(); l3b = lado(); prim = tprim(); a3c = alvo44(prim, 'dlg'); a3d = alvo44('Cancelar', 'dlg')
    chk('V7a 390 px sem rolagem horizontal da página: IR-01, IR-02 (painel), IR-03det (página e painel de término)', not (l1 or l2 or l3 or l3b), [l1, l2, l3, l3b])
    chk('V7b toque inicia e abre o término; Iniciar, término, Registrar e Cancelar com alvo ≥ 44 px dentro da tela', bool(o) and o['etapa'] == 'Em execução' and bool(d) and a2[0] and a3[0] and a3b[0] and a3c[0] and a3d[0], [a2, a3, a3b, a3c, a3d])
    preencher('tm_cob', '5'); preencher('tm_vol', '500'); time.sleep(.3)
    mr = J(f"(()=>{{const e=({DLG}).querySelector('#tm_mot'); if(!e) return null; const q=e.getBoundingClientRect(); return [q.left,q.right,q.height];}})()")
    preencher('tm_mot', 'toque 390 (sintético)'); clicar(prim, 'dlg', toque=True); o = ordem('OS-0419')
    chk('V7c toque registra o término antecipado (5 ha, 500 m³, motivo); campo de motivo dentro da tela', o['ps'][0]['cob'] == 5 and o['ps'][0]['vol'] == 500 and bool(mr) and mr[0] >= 0 and mr[1] <= 390.5, [o['ps'][0], mr])
    abrir('IR-03det.dc.html#OS-0394:conferir', 1.8); d = dlg(); l4 = lado(); b1 = alvo44('Devolver para conferir o hidrômetro', 'dlg'); b2 = alvo44('Aceitar com motivo', 'dlg')
    chk('V7d 390 px: painel de conferência sem rolagem lateral; Devolver e Aceitar ≥ 44 px dentro da tela', bool(d) and not l4 and b1[0] and b2[0], [l4, b1, b2])
    c.shot(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v7_390_' + ('base' if '--base' in sys.argv else ('ec65' if '--ec65' in sys.argv else 'pr')) + '.png'))
    preencher('cm_mot', 'toque (sintético)'); clicar('Aceitar com motivo', 'dlg', toque=True); o = ordem('OS-0394')
    chk('V7e toque em "Aceitar com motivo" encerra', bool(o) and o['etapa'] == 'Encerradas', o and o['etapa'])
    c.aparelho(1440, 900)
    # ============ P · persistência e retorno (recarregar no meio do fluxo) ============
    reset(); iniciar_0419(); clicar(thdr()); preencher('tm_cob', '7'); preencher('tm_vol', '700'); time.sleep(.2)
    recarregar(); o = ordem('OS-0419'); h = head(); d = dlg()
    chk('P1 recarregar com o painel de término preenchido: nada gravado pela metade; segue Em execução, painel fechado', o['etapa'] == 'Em execução' and o['ps'][0]['vol'] is None and d is None and 'Em execução' in h, [o['etapa'], o['ps'][0], d])
    abrir('IR-03det.dc.html#OS-0419:termino'); d = dlg()
    chk('P1b o link #termino reabre o painel vazio (rascunho não vira fato)', bool(d) and d['cob'] == '' and d['vol'] == '', d)
    c.tecla('Escape', 'Escape', 27); time.sleep(.6); clicar('Pausar')
    recarregar(); h = head()
    chk('P2 recarregar pausada: segue Pausada com "Retomar irrigação"', 'Pausada' in h and 'Retomar irrigação' in h, h)
    clicar('Retomar irrigação'); terminar('30', '3000', 'Área do app (sintético)')
    recarregar(); h = head(); o = ordem('OS-0419')
    abrir('IR-03.dc.html', 1.6); lst = J(f"(()=>{{const n={N}; return [...document.querySelectorAll('[role=row]')].map(r=>n(r.innerText)).find(t=>t.indexOf('OS-0419')>=0)||'';}})()")
    chk('P3 recarregar e voltar à lista: pendência "Área e tempo a conferir" persiste, sem crédito', 'Área e tempo a conferir' in h and ap('P2', 'OS-0419') == [] and o['etapa'] == 'Em conferência' and 'Em conferência' in lst, [h, lst])
    # ============ Q · contraexemplos do irrigante e do gestor ============
    # Q1: o mesmo irrigante registra o término incompatível e valida a própria conferência
    reset('João'); iniciar_0419(); terminar('80', '8480', 'Volta completa informada (sintético)'); abrir('IR-03det.dc.html#OS-0419:conferir'); preencher('cm_mot', 'Eu mesmo conferi (sintético)'); clicar('Aceitar com motivo', 'dlg'); o = ordem('OS-0419')
    ach('Q1 o irrigante que registrou a volta incompatível não deveria validar sozinho a própria conferência', not (o['etapa'] == 'Encerradas' and ap('P2', 'OS-0419')), {'etapa': o['etapa'], 'credito': ap('P2', 'OS-0419'), 'conf': o['conf'], 'tempoConferido': o['ps'][0].get('tempoConferido')})
    # Q2: Rui (almoxarife) registra término de irrigação
    reset('Rui'); t0 = iniciar_0419(); r = terminar('5', '540', 'Rui registrou (sintético)'); o = ordem('OS-0419')
    print('     Q2 Rui iniciou:', t0[:90], '· término:', r['toast'][:120], '· etapa', o and o['etapa'])
    # Q3: avanço com área total não dispensa a conferência do término
    reset(); iniciar_0419(); clicar('Registrar avanço'); preencher('av_cob', '80'); clicar('Salvar avanço', 'dlg'); r = terminar('80', '8480'); o = ordem('OS-0419')
    chk('Q3 avanço de 80 ha a +30 min não dispensa o motivo do término incompatível', r['motivo_pedido'] and o['ps'][0]['vol'] is None, [r['motivo_pedido'], r['toast'], r['depois'] and r['depois']['txt'][-160:]])
    # Q4: gotejo T7 (OS-0423): término antecipado com a área inteira do setor
    reset(); abrir('IR-03det.dc.html#OS-0423:conflito'); clicar('Aplicar janela', 'dlg'); abrir('IR-03det.dc.html#OS-0423'); clicar('Iniciar irrigação'); clicar('Pausar'); clicar('Retomar irrigação')
    sT7 = S()['setores']['T7']; r = terminar(str(sT7['ha']).replace('.', ','), '400'); o = ordem('OS-0423')
    print('     Q4 gotejo T7', sT7['ha'], 'ha após 60 min de 120: motivo pedido =', r['motivo_pedido'], '·', r['toast'][:150] or (r['depois'] and r['depois']['txt'][-150:]))
    # ============ V8 + F2 · cenário salvo na base abre e termina ============
    if pb:
        UB = lambda pg: f'http://127.0.0.1:{pb}/{pg}'
        coletar(); c.goto(UB('Main.dc.html'), .3); J("localStorage.clear();sessionStorage.clear();1")
        c.goto(UB('IR-03det.dc.html#OS-0394:conferir'), 1.6); clicar('Validar e encerrar', 'dlg')
        c.goto(UB('IR-03det.dc.html#OS-0423:conflito'), 1.6); clicar('Aplicar janela', 'dlg')
        c.goto(UB('IR-03det.dc.html#OS-0419'), 1.6); clicar('Iniciar irrigação'); clicar('Pausar'); clicar('Retomar irrigação')
        salvo = J("localStorage.getItem('talhao-os-irrigacao-v1')"); sb = json.loads(salvo); ERRJS.clear()
        reset(); J(f"localStorage.setItem('talhao-os-irrigacao-v1',{json.dumps(salvo)});1"); abrir('IR-03det.dc.html#OS-0419'); h = head(); s = S()
        e = {'rev': s['rev'], 'o394': s['ordens']['OS-0394']['etapa'], 'o423': s['ordens']['OS-0423']['etapa'], 'o419': s['ordens']['OS-0419']['etapa'], 'pz': len(s['ordens']['OS-0419']['exec']['pausas']), 'ag': s['agora']}
        chk('V8a estado salvo na base abre igual (OS-0394 encerrada, OS-0423 liberada, OS-0419 em execução com a pausa)',
            json.loads(J("localStorage.getItem('talhao-os-irrigacao-v1')")) == sb and e['o394'] == 'Encerradas' and e['o423'] == sb['ordens']['OS-0423']['etapa'] and e['o419'] == 'Em execução' and e['pz'] == 1 and 'Em execução' in h, [e, h])
        e8 = J("(window.__errs||[]).filter(e=>!/favicon|Failed to load resource/i.test(e))") or []
        chk('V8b sem erro de JavaScript ao abrir o cenário salvo', not e8, e8)
        r = terminar('20', '2000', 'Cenário salvo na base (sintético)'); o = ordem('OS-0419')
        chk('F2b a OS-0419 em execução do cenário salvo termina (20 ha, 2.000 m³; motivo se pedido), sem "Avance a simulação"', o['ps'][0].get('vol') == 2000 and 'Avance' not in r['toast'], [r['motivo_pedido'], r['toast'], o['ps'][0]])
        abrir('IR-03det.dc.html#OS-0423'); clicar('Iniciar irrigação'); t = toast(); s = S()
        chk('F2c no cenário salvo, a OS-0423 inicia na sua janela (15:02)', s['ordens']['OS-0423']['passadas'][0].get('iniReal') == 902, [t, s['ordens']['OS-0423']['passadas'][0].get('iniReal')])
    else:
        print('     V8 não executado: defina BASE_RENDER')
    errs = jserros(); chk('V9 sem erro de JavaScript nas páginas percorridas', not errs, errs)
finally:
    c.close(); srv.terminate()
    if srvb: srvb.terminate()
print(f'ACHADOS (contraexemplos do revisor): {len(ACH_OK)} ok · {len(ACH_FAIL)} achados {ACH_FAIL}')
print(f'RESULTADO: {len(OK)}/{len(OK)+len(FAIL)}' + (f' · falhas {FAIL}' if FAIL else ''))
