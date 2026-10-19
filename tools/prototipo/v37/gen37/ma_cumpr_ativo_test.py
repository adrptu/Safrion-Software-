# -*- coding: utf-8 -*-
"""EX-53 · cumprimento de preventiva no detalhe do ativo (Manutenção › ativo › Custo e desempenho) pela regra única KPI-PCM-05
(manCumprimento, achado do Codex 6258683205: o detalhe contava só as encerradas, de todo o histórico). No Chrome a 1440 × 1000.
  W1 cada ativo mostra o KPI-PCM-05 do ativo no período do painel (oráculo refeito no teste sobre os dados crus): "k de n (p %) · período" ou "sem base no período"
  W2 nenhum ativo mostra o texto da conta antiga ("não calculável")
  W3 o filtro por ativo reparte a base sem perder nem repetir: a soma por ativo é igual ao total, no mês e em 12 m
  W4 nenhum erro de JavaScript
Contraprova: o render da v140 reprova W1 e W2.
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B ma_cumpr_ativo_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:900])

LER = r"""(()=>{ const N=s=>(s||'').replace(/\s+/g,' ').trim();
  const s=document.querySelector('section.ma-bl[aria-label="Custo e desempenho"]'); if(!s) return {erro:'sem o bloco Custo e desempenho'};
  const b=s.querySelector('button.ma-blh'); if(b&&b.getAttribute('aria-expanded')!=='true') b.click();
  return {ok:true}; })()"""
VAL = r"""(()=>{ const N=s=>(s||'').replace(/\s+/g,' ').trim();
  const s=document.querySelector('section.ma-bl[aria-label="Custo e desempenho"]'); if(!s) return null;
  const it=[...s.querySelectorAll('.ma-bl-c div')].find(d=>N(d.textContent)==='Cumprimento de preventiva'&&d.nextElementSibling);
  return it?N(it.nextElementSibling.textContent):null; })()"""
ESP = r"""(id=>{ /* oráculo independente: a definição do KPI-PCM-05 (dados_manutencao.py, comentário do manCumprimento) refeita sobre os dados crus */
  const M=window.__man, c=M.manGet(), h=c.hoje, de=h.slice(0,8)+'01', corte=h, dentro=d=>!!d&&d>=de&&d<=corte;
  const os=Object.values(c.oms).filter(o=>o.aid===id&&o.tipo==='Preventiva'&&o.etapa!=='Canceladas'&&dentro(o.vencOrig)&&(o.etapa==='Encerradas'||o.vencOrig<corte));
  const ok=os.filter(o=>o.etapa==='Encerradas'&&o.exec&&o.exec.data&&o.exec.data<=o.vencOrig).length;
  const so=M.manSemOrdem(c).venc.filter(l=>l.aid===id&&l.x.sit==='Vencida'&&dentro(l.x.prev)&&l.x.prev<corte).length, n=os.length+so;
  const t=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'][Number(h.slice(5,7))-1]+'/'+h.slice(0,4);
  return n?ok+' de '+n+' ('+Math.round(ok*100/n)+' %) · '+t:'sem base no período'; })"""
SOMA = r"""(k=>{ const M=window.__man; if(!M.manCumprimento) return {erro:'manCumprimento fora do __man'}; const c=M.manGet(), manCumprimento=M.manCumprimento; const t=manCumprimento(c,k); const ids=Object.keys(c.ativos); let n=0, ok=0;
  ids.forEach(id=>{ const r=manCumprimento(c,k,id); if(r){ n+=r.n; ok+=r.ok; } });
  return {t:t?{n:t.n,ok:t.ok}:null, soma:{n,ok}, ativos:ids.length}; })"""

port, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda p: f'http://127.0.0.1:{port}/{p}'
try:
    c.aparelho(1440, 1000)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear()")
    c.goto(U('MA.dc.html#vis=ativos'), 1.6)
    ids = J("Object.keys(window.__man.manGet().ativos)") or []
    linhas, erros = [], []
    for aid in ids:
        c.goto(U('MA.dc.html#ativo=' + aid), 1.0)
        a = J(LER) or {}
        if a.get('erro'): linhas.append([aid, a['erro'], None]); continue
        time.sleep(.25)
        linhas.append([aid, J(VAL), J(ESP + '(' + json.dumps(aid) + ')')])
        erros += J("window.__e") or []
    dif = [l for l in linhas if l[1] != l[2]]
    chk(f'W1 {len(ids)} ativos: o detalhe mostra o KPI-PCM-05 do ativo no mês (oráculo independente)', ids and not dif, dif[:6])
    velho = [l for l in linhas if l[1] and 'não calculável' in l[1]]
    chk('W2 nenhum ativo com o texto da conta antiga ("não calculável")', ids and not velho and all(l[1] for l in linhas), velho[:6] or [l for l in linhas if not l[1]][:6])
    base = sorted(set(l[1] for l in linhas if l[1])); print('      valores na tela:', base)
    s1 = J(SOMA + "('mes')") or {}; s2 = J(SOMA + "('12m')") or {}
    def rep(s): return (s.get('t') is None and s.get('soma', {}).get('n') == 0) or (s.get('t') and s['t'] == s.get('soma'))
    chk('W3 a soma por ativo é igual ao total (mês e 12 m): o filtro reparte a base sem perder nem repetir', rep(s1) and rep(s2) and (s2.get('t') or {}).get('n', 0) > 0, [s1, s2])
    chk('W4 nenhum erro de JavaScript', not erros, erros[:5])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK+FAIL} ok')
sys.exit(1 if FAIL else 0)
