# -*- coding: utf-8 -*-
"""Ficha do pivô (pedido do proprietário, 09/10/2026: "na irrigação onde colocamos os dados da ficha do pivô, lâmina 21 h etc.").

O que é: a CAPACIDADE do equipamento de irrigação, como está na ficha técnica do fabricante, no detalhe do equipamento
(CD-03 › Máquinas, instalações e setores › Bomba do Pivô 2 › "Ficha do pivô ›") e aberta pela Irrigação (IR-01 › setor P2 › "Ficha do pivô",
ou IR-01.dc.html#P2:ficha) com o MESMO componente e o MESMO registro (sem cadastro paralelo).
Onde se registra (revisão de 10/10, A4): no detalhe do equipamento do pivô ("Registrar ficha do pivô ›", ou "Editar ficha" na ficha aberta),
no CD-03 ou no setor da Irrigação. Grava no navegador (localStorage 'talhao-os-ficha-pivo-v1'); a semente é dados.FICHA_PIVO (sintética).
Fonte única da vazão (A2): a vazão da ficha é a do equipamento no cadastro (o campo do CD-03 fica só leitura com ficha) e a do setor na
Irrigação (irrGet → irrEqVaz), que a duração e a trava de outorga usam. Equipamento e setor: o setor guarda a chave do equipamento (x.eq);
nome e modelo vêm do cadastro (no CD-03, a linha ao vivo); a fazenda vem do setor (A7).
Conferência (uma conta, fpvConf, A1): lâmina pela conta = lâmina a 100 % × 100 ÷ percentímetro, em centésimos inteiros; diverge quando
|ficha − conta| > 0,05 mm + 0,05 mm × 100 ÷ percentímetro (meia casa da linha mais a meia casa da lâmina a 100 %, que a conta multiplica).
A conta só confere: não corrige a ficha. "21 h" é o regime de operação (h/dia, fora do horário de ponta), sem outro uso.
A ficha não prescreve lâmina (A3): a lâmina a aplicar segue o limite por passada do SETOR (o que a programação aplica, x.lmax) e o
responsável técnico. Água disponível no solo (CAD) do talhão: ponto de leitura nomeado (fpvCad, lê irrCadTxt da frente SOLO quando existir)."""
import json
import dados as D
import dados_cad as DC
from engine import grid, MUTED, LINE, BG, SURF, ACC, DISP, YEL, YELS, RED, REDS, BTN_ST, _MINI, _MINIP

H = lambda s: '{{' + s + '}}'
KEY = 'talhao-os-ficha-pivo-v1'
GID = 'g_fpv'
COLS = [dict(k='pct', l='Percentímetro', t='num', a='r', u='%', w=110), dict(k='tempo', l='Tempo de volta', t='num', a='r', u='h', d=1, w=110),
        dict(k='lam', l='Lâmina', t='num', a='r', u='mm', d=1, w=90), dict(k='conta', l='Lâmina pela conta', t='num', a='r', u='mm', d=2, w=120),
        dict(k='conf', l='Conferência', w=170)]
# campos do registro (a ficha do fabricante); a linha de 100 % da tabela é o tempo de volta e a lâmina a 100 % (não se digita duas vezes)
CAMPOS = [dict(k='fabricante', l='Fabricante', t='txt', req=True),
          dict(k='raio_m', l='Raio', t='num', u='m', min=10, max=2000),
          dict(k='area_ha', l='Área irrigada', t='num', u='ha', min=0.1, max=1000),
          dict(k='vazao_ls', l='Vazão', t='num', u='L/s', min=1, max=2000),
          dict(k='pressao_mca', l='Pressão', t='num', u='mca', min=1, max=200),
          dict(k='volta_100_h', l='Tempo de volta a 100 %', t='num', u='h', min=0.5, max=500),
          dict(k='lamina_100_mm', l='Lâmina a 100 %', t='num', u='mm', min=0.1, max=200),
          dict(k='regime_h', l='Regime de operação', t='num', u='h/dia', min=1, max=24),
          dict(k='regime_obs', l='Observação do regime', t='txt', req=False)]
PCT_MODELO = [90, 80, 70, 60, 50, 40, 30, 20, 10]   # linhas da tabela num registro novo (só o percentímetro; tempo e lâmina em branco)


def seed():
    """fichas da semente (dados.FICHA_PIVO), por equipamento do cadastro."""
    return {aid: dict(f) for aid, f in D.FICHA_PIVO.items()}


def pivos():
    """equipamentos de irrigação que são o pivô de um setor da Irrigação (x.eq do setor, tipo pivô): onde a ficha se registra.
    Nome e modelo do cadastro, setor e pivô da Irrigação, fazenda do setor, talhões do cadastro de talhões (CD-01) e a vazão e área atuais
    do setor (para o registro novo já vir com elas, corrigíveis)."""
    import dados_irrigacao as DI
    at = {a['id']: a for a in DC.ATIVOS}; fz = {f['id']: f['nome'] for f in DC.FAZENDAS}
    out = {}
    for sid, x in DI.seed()['setores'].items():
        aid = x.get('eq')
        if not aid or x.get('tipo') != 'pivô' or aid not in at: continue
        a = at[aid]
        tal = [dict(t=t, ha=ha) for t, ha, cult, fase, obs in D.TALHOES if DC.SISTEMA.get(obs, ('', ''))[1] == a['nome']]
        out[aid] = dict(nome=a['nome'], modelo=a['modelo'], setor=sid, pivo=x['nome'], faz=fz.get(x['faz'], x['faz']), tal=tal, ha=x['ha'], vaz=x['vazao'])
    return out


def talhoes(aid):
    """talhões irrigados pelo equipamento (cadastro de talhões: sistema e pivô/setor)."""
    return [t['t'] for t in pivos().get(aid, {}).get('tal', [])]


# registro gravado + a conta da conferência: vai para toda página com o estado da Irrigação (dados_irrigacao.js_prefixo) e para o CD-03
STORE_JS = r'''
// ===== Ficha do pivô · registro (ficha_pivo.py): semente FPV0 + o registrado no navegador ('talhao-os-ficha-pivo-v1') =====
// Lido pelo cadastro (CD-03: a vazão do equipamento) e pela Irrigação (irrEqVaz: a vazão do setor, usada na duração e na trava de outorga).
// "Restaurar demonstração" (cenário da O.S.) volta a ficha à semente, como a Irrigação. Sem localStorage vale só para a tela aberta.
const FPV_KEY = 'talhao-os-ficha-pivo-v1';
let FPV_MEM = null, FPV_RAW = null, FPV_OBJ = null, FPV_ALL = null, FPV_ALLK = null, FPV_CR = null, FPV_CV = 0;
function fpvCenRev() { let t = null; try { t = localStorage.getItem('talhao-os-cenario-v1'); } catch (e) { t = null; }
  if (t !== FPV_CR) { FPV_CR = t; try { const c = JSON.parse(t || 'null'); FPV_CV = (c && c.rev) || 0; } catch (e) { FPV_CV = 0; } } return FPV_CV; }
function fpvLer() { let t = null; try { t = localStorage.getItem(FPV_KEY); } catch (e) { t = null; }
  if (t) { let o = (t === FPV_RAW && FPV_OBJ) ? FPV_OBJ : null; if (!o) { try { o = JSON.parse(t); } catch (e) { o = null; } }
    if (o && o.cenVisto && fpvCenRev() < o.cenVisto) { try { localStorage.removeItem(FPV_KEY); } catch (e) {} FPV_MEM = null; o = null; }   /* o cenário voltou ao início */
    if (o && o.fichas) { FPV_RAW = t; FPV_OBJ = o; return o; } }
  return FPV_MEM || { fichas: {} }; }
function fpvFichas() { const o = fpvLer(); if (FPV_ALLK === o && FPV_ALL) return FPV_ALL; FPV_ALL = Object.assign({}, FPV0, o.fichas || {}); FPV_ALLK = o; return FPV_ALL; }
function fpvFicha(aid) { return fpvFichas()[aid] || null; }
function fpvGravar(aid, f) { const o = JSON.parse(JSON.stringify(fpvLer())); o.fichas = o.fichas || {}; o.fichas[aid] = f;
  o.cenVisto = Math.max(o.cenVisto || 0, fpvCenRev()); o.rev = (o.rev || 0) + 1; FPV_MEM = o;
  try { const t = JSON.stringify(o); localStorage.setItem(FPV_KEY, t); FPV_RAW = t; FPV_OBJ = o; } catch (e) {} return o.rev; }
// linhas da ficha: a de 100 % é o tempo de volta e a lâmina a 100 % (campos); as outras, como foram registradas
function fpvLinhas(f) { return [[100, f.volta_100_h, f.lamina_100_mm]].concat((f.tabela || []).filter(l => Number(l[0]) !== 100)); }
// conferência (a única conta da ficha): lâmina pela conta = lâmina a 100 % × 100 ÷ percentímetro, em centésimos inteiros (sem erro de
// arredondamento). Diverge quando |ficha − conta| > 0,05 mm + 0,05 mm × 100 ÷ percentímetro: meia casa da linha (1 casa na ficha) mais a meia
// casa da lâmina a 100 %, que a conta multiplica por 100 ÷ percentímetro (revisão de 10/10, A1). Em centésimos: |Lp×P − 10⁴×L| ≤ 5×P + 5×10⁴.
function fpvC(x) { return Math.round(Number(x) * 100); }
function fpvConf(f) { const L = fpvC(f.lamina_100_mm);
  return fpvLinhas(f).map(l => { const P = fpvC(l[0]), Lp = fpvC(l[2]), num = Lp * P - 10000 * L;
    return { pct: Number(l[0]), tempo: Number(l[1]), lam: Number(l[2]), conta: L * 100 / P, dif: num / (100 * P), tol: 0.05 + 500 / P, ok: Math.abs(num) <= 5 * P + 50000 }; }); }
'''

UI_JS = r'''
// ===== Ficha do pivô · gaveta (ficha_pivo.py): o mesmo componente no CD-03 e no IR-01; ler, registrar e editar =====
function fpvN(n,d){ return Number(n).toLocaleString('pt-BR',{minimumFractionDigits:d,maximumFractionDigits:d}); }
function fpvNat(n){ return Number(n).toLocaleString('pt-BR',{maximumFractionDigits:2}); }
function fpvM3(ls){ return Math.round(Number(ls)*36)/10; }   /* L/s → m³/h (1 casa) */
function fpvTxt(n){ return (n===null||n===undefined||n==='')?'':String(n).replace('.',','); }
// equipamento: nome e modelo do cadastro (no CD-03, a linha ao vivo: renomear aparece na ficha; na Irrigação, o cadastro da semente)
function fpvEq(self,aid){ const E=FPV_EQ[aid]||{}; let nome=E.nome||'', modelo=E.modelo||'';
  if(FPV_CTX==='CD'){ try{ const r=(RW(self,'g_atv')||[]).find(x=>x.id===aid); if(r){ nome=r.v.nome||nome; modelo=r.v.modelo||''; } }catch(e){} }
  return {nome:nome,modelo:modelo}; }
// setor da Irrigação → equipamento do setor (x.eq): com ficha (fpvDe) ou só pivô onde se pode registrar (fpvPode)
function fpvPode(sid){ try{ const x=irrGet().setores[sid]; return x&&x.eq&&FPV_EQ[x.eq]?x.eq:''; }catch(e){ return ''; } }
function fpvDe(sid){ const a=fpvPode(sid); return a&&fpvFicha(a)?a:''; }
function fpvSint(aid){ return !((fpvLer().fichas||{})[aid]); }   /* semente sintética até alguém registrar */
// vazão atual do equipamento (para o registro novo): na Irrigação, a do setor; no cadastro, a da linha (m³/h ÷ 3,6)
function fpvVazAtual(self,aid){ const E=FPV_EQ[aid]||{};
  if(FPV_CTX==='IR'){ try{ const x=irrGet().setores[E.setor]; if(x) return x.vazao; }catch(e){} }
  try{ const r=(RW(self,'g_atv')||[]).find(x=>x.id===aid); const m=r?g2num(r.v.vazao_ir):NaN; if(!isNaN(m)&&m>0) return Math.round(m/3.6*10)/10; }catch(e){}
  return E.vaz; }
function fpvAbrir(self,id,volta,novo){ if(!FPV_EQ[id]) return; if(!novo&&!fpvFicha(id)) return; self.__fpvVolta=volta||null;
  self.setState({fpv:id,fpvEd:novo?fpvRascunho(self,id,true):null});
  setTimeout(()=>{ try{ const a=document.querySelector('aside[aria-label^="Ficha do pivô"]'); if(a){ a.scrollTop=0; const b=a.querySelector(novo?'input':'button[aria-label="Fechar"]'); if(b) b.focus(); } }catch(e){} },40); }
// rascunho do registro: ficha existente (como está) ou nova (vazão e área atuais do setor, percentímetros usuais; o resto em branco)
function fpvRascunho(self,aid,novo){ const f=novo?null:fpvFicha(aid), E=FPV_EQ[aid]||{}, d={};
  FPV_CAMPOS.forEach(c=>{ d[c.k]=f?fpvTxt(f[c.k]):''; });
  if(!f){ d.vazao_ls=fpvTxt(fpvVazAtual(self,aid)); d.area_ha=fpvTxt(E.ha); }
  const L=f?(f.tabela||[]).filter(l=>Number(l[0])!==100).map(l=>({pct:fpvTxt(l[0]),tempo:fpvTxt(l[1]),lam:fpvTxt(l[2])})):FPV_PCT.map(p=>({pct:String(p),tempo:'',lam:''}));
  return {aid:aid,novo:!f,d:d,L:L,e:{},le:[],warn:null,ini:JSON.stringify([d,L])}; }
function fpvSujo(ed){ return !!ed&&JSON.stringify([ed.d,ed.L])!==ed.ini; }
function fpvMuda(self,patch){ const ed=self.state.fpvEd; if(!ed) return; self.setState({fpvEd:Object.assign({},ed,patch,{warn:null})}); }
// validação do registro: campos obrigatórios e faixas; linhas com tempo ou lâmina precisam de percentímetro único entre 1 e 99 %
// (a linha de 100 % vem do tempo de volta e da lâmina a 100 %); linha só com o percentímetro não entra
function fpvValida(d,L){ const e={}, le=[], tab=[], vistos={};
  FPV_CAMPOS.forEach(c=>{ const s=String(d[c.k]||'').trim();
    if(!s){ if(c.req!==false) e[c.k]='Informe: '+c.l.toLowerCase()+'.'; return; }
    if(c.t!=='num') return;
    const x=g2num(s); if(isNaN(x)||x<c.min||x>c.max) e[c.k]=c.l+' entre '+fpvNat(c.min)+' e '+fpvNat(c.max)+' '+c.u+'.'; });
  L.forEach((l,i)=>{ const p=String(l.pct||'').trim(), t=String(l.tempo||'').trim(), m=String(l.lam||'').trim(); if(!t&&!m) return;
    const P=g2num(p), T=g2num(t), M=g2num(m); let er='';
    if(P===100) er='A linha de 100 % vem do tempo de volta e da lâmina a 100 % (campos acima).';
    else if(!p||isNaN(P)||P<1||P>99) er='Percentímetro entre 1 e 99 %.';
    else if(vistos[P]) er='Percentímetro '+fpvNat(P)+' % repetido.';
    else if(!t||isNaN(T)||T<=0) er='Informe o tempo de volta desta linha (h).';
    else if(!m||isNaN(M)||M<=0) er='Informe a lâmina desta linha (mm).';
    if(er) le[i]=er; else { vistos[P]=1; tab.push([P,T,M]); } });
  tab.sort((a,b)=>b[0]-a[0]); return {e:e,le:le,tab:tab,ok:!Object.keys(e).length&&!le.some(Boolean)}; }
function fpvSalvar(self){ const ed=self.state.fpvEd; if(!ed) return; const r=fpvValida(ed.d,ed.L);
  if(!r.ok){ self.setState({fpvEd:Object.assign({},ed,{e:r.e,le:r.le,warn:null})}); return; }
  const f={}; FPV_CAMPOS.forEach(c=>{ const s=String(ed.d[c.k]||'').trim(); f[c.k]=c.t==='num'?g2num(s):s; }); f.tabela=r.tab;
  const nome=fpvEq(self,ed.aid).nome, ant=fpvFicha(ed.aid);
  /* repetir o mesmo registro não grava de novo (idempotente): diz que nada mudou */
  if(ant&&!ed.novo&&JSON.stringify(FPV_CAMPOS.map(c=>ant[c.k]).concat([fpvLinhas(ant).slice(1)]))===JSON.stringify(FPV_CAMPOS.map(c=>f[c.k]).concat([f.tabela]))){
    self.setState({fpvEd:null,g2toast:'Ficha do pivô sem alteração · '+nome+'.'}); return; }
  const rev=fpvGravar(ed.aid,f);
  self.setState({fpvEd:null,fpvrev:rev,irrrev:Date.now(),g2toast:'Ficha do pivô salva · '+nome+' · vazão '+fpvNat(f.vazao_ls)+' L/s ('+fpvN(fpvM3(f.vazao_ls),1)+' m³/h): o cadastro e a Irrigação usam esta vazão.'}); }
// fechar volta ao detalhe de onde a ficha foi aberta (equipamento no CD-03, setor no IR-01); com alteração não salva, pergunta antes
function fpvFechar(self,acao){ const ed=self.state.fpvEd;
  if(ed&&fpvSujo(ed)&&acao!=='descartar'){ self.setState({fpvEd:Object.assign({},ed,{warn:acao||'fechar'})}); return; }
  if(ed&&!ed.novo&&(acao==='cancelar'||(acao==='descartar'&&ed.warn==='cancelar'))){ self.setState({fpvEd:null}); return; }   /* editar → volta à ficha */
  const b=self.__fpvVolta; self.__fpvVolta=null; self.setState({fpv:null,fpvEd:null}); g2set(self,'g_fpv',{fmc:null});
  if(b&&b.gid){ const sp=GRIDS.find(g=>g.id===b.gid); if(sp) setTimeout(()=>{ if(g2find(g2rows(self,sp),b.rid)) g2open(self,sp,b.rid,null); },0); } }
// água disponível no solo (CAD) do talhão: ponto de leitura nomeado. A frente SOLO (Análises de solo) define irrCadTxt na Irrigação;
// sem ela a ficha diz, na Irrigação, que não há medição e, no cadastro, onde ler. A CAD é do solo: não muda a capacidade nem prescreve lâmina.
function fpvCad(E){ try{ if(typeof irrCadTxt==='function'&&typeof irrGet==='function'){ const s=irrGet(), x=s.setores[E.setor]; if(x) return irrCadTxt(s.faz[x.faz],E.setor,x); } }catch(e){} return ''; }
// o que a gaveta mostra (em cache pela ficha, pelo nome e modelo do cadastro e pelo limite do setor: linhas estáveis para a grade)
function fpvVista(self,aid){ const f=fpvFicha(aid), E=FPV_EQ[aid]; if(!f||!E) return null; const q=fpvEq(self,aid);
  let lmax=null; if(FPV_CTX==='IR'){ try{ const x=irrGet().setores[E.setor]; if(x) lmax=x.lmax; }catch(e){} }
  const k=JSON.stringify([f,q,lmax,fpvSint(aid)]), C=(self.__fpvC=self.__fpvC||{}); if(C[aid]&&C[aid].k===k) return C[aid].v;
  const conf=fpvConf(f), div=conf.filter(r=>!r.ok), tal=E.tal[0]||{t:E.setor};
  const lin=conf.map(r=>r.ok?'Confere':('Diverge '+(r.dif<0?'−':'+')+fpvN(Math.abs(r.dif),2)+' mm'));
  const rows=conf.map((r,i)=>({id:'p'+fpvNat(r.pct),v:{pct:r.pct,tempo:r.tempo,lam:r.lam,conta:r.conta},s:{conf:lin[i]},p:{conf:[{k:'chip',t:lin[i],c:r.ok?'green':'yellow'}]}}));
  const resumo=div.length?((div.length===1?'1 linha da ficha diverge da conta: ':div.length+' linhas da ficha divergem da conta: ')
      +div.map(r=>fpvNat(r.pct)+' % · '+fpvN(r.lam,1)+' mm na ficha × '+fpvN(r.conta,2)+' mm pela conta').join('; ')+'. Confira a ficha com o fabricante; a conta não corrige o registro.')
    :'A tabela da ficha confere com a conta em todas as linhas.';
  const kv=[{l:'Identificação',v:E.pivo+' · setor '+E.setor+' · '+q.nome},{l:'Fabricante e modelo',v:f.fabricante+(q.modelo?' · '+q.modelo:'')},
    {l:'Raio',v:fpvNat(f.raio_m)+' m'},{l:'Área irrigada',v:fpvNat(f.area_ha)+' ha'},{l:'Vazão',v:fpvNat(f.vazao_ls)+' L/s · '+fpvN(fpvM3(f.vazao_ls),1)+' m³/h'},
    {l:'Pressão',v:fpvNat(f.pressao_mca)+' mca'},{l:'Tempo de volta a 100 %',v:fpvN(f.volta_100_h,1)+' h'},{l:'Lâmina a 100 %',v:fpvN(f.lamina_100_mm,1)+' mm'},
    {l:'Regime de operação',v:fpvNat(f.regime_h)+' h/dia'+(f.regime_obs?' · '+f.regime_obs:'')},
    {l:'Talhão',v:tal.t+' · '+E.faz+(tal.ha!==undefined?' · '+fpvNat(tal.ha)+' ha no cadastro':'')}];
  /* a ficha não prescreve lâmina: o limite é o do setor (o que a programação aplica); na Irrigação, o valor atual do setor */
  const nota='Capacidade do equipamento: a ficha não prescreve lâmina. A lâmina a aplicar segue o limite por passada do setor '+E.setor
    +(lmax!==null&&lmax!==undefined?(' (até '+fpvN(lmax,1)+' mm por passada)'):', na Irrigação,')+' e o responsável técnico ('+FPV_RT+').';
  const v={t:'Ficha do pivô · '+E.pivo,sub:q.nome+' · irriga o talhão '+tal.t+' ('+E.faz+') · ficha técnica do fabricante, registrada como está'+(fpvSint(aid)?' (dados sintéticos)':''),
    kv:kv,rows:rows,resumo:resumo,diverge:div.length>0,nota:nota,
    conta:'Conferência: lâmina pela conta = lâmina a 100 % ('+fpvN(f.lamina_100_mm,1)+' mm) × 100 ÷ percentímetro. Diverge quando a diferença passa de 0,05 mm + 0,05 mm × 100 ÷ percentímetro (meia casa da linha mais a meia casa da lâmina a 100 %, que a conta multiplica); a conta não corrige a ficha.'};
  C[aid]={k:k,v:v}; return v; }
const FPV_IST='font-family:inherit;font-size:14px;padding:8px 10px;border-radius:10px;box-sizing:border-box;width:100%;min-width:0;color:#15201A;background:#FFFFFF;border:1px solid ';
// chamada no início do PREVALS da tela: as linhas da tabela entram antes de a grade desenhar
function fpvVals(self,v){ const id=self.state.fpv, ed=self.state.fpvEd&&self.state.fpvEd.aid===id?self.state.fpvEd:null, E=id?FPV_EQ[id]:null;
  const f=E&&!ed?fpvVista(self,id):null, sp=GRIDS.find(g=>g.id==='g_fpv'); v.fpv_open=!!(E&&(f||ed)); v.fpv_vw=!!f; v.fpv_ed=!!ed; v.fpv_kv=[]; v.fpv_ff=[]; v.fpv_el=[];
  if(sp) sp.rows=f?f.rows:[]; if(!v.fpv_open) return;
  v.fpv_pivo=E.pivo; v.fpv_close=()=>fpvFechar(self,'fechar');
  v.fpv_key=(e)=>{ if(e.key==='Escape'&&!g2st(self,'g_fpv').fmc){ e.preventDefault(); e.stopPropagation(); fpvFechar(self,'fechar'); } };
  v.fpv_lkH=FPV_CTX==='IR'?('CD-03.dc.html#ficha='+id):('IR-01.dc.html#'+E.setor); v.fpv_lkT=FPV_CTX==='IR'?'Abrir no cadastro do equipamento':('Ver o setor '+E.setor+' na Irrigação');
  if(f){ v.fpv_t=f.t; v.fpv_sub=f.sub; v.fpv_kv=f.kv; v.fpv_resumo=f.resumo;
    v.fpv_rst=f.diverge?'background:#FFF3D6;color:#8A5A00;':'background:#E4F3E9;color:#1E7A4C;';
    v.fpv_nota=f.nota; v.fpv_conta=f.conta; const cad=fpvCad(E); v.fpv_cadL='Água disponível no solo (CAD) · talhão '+((E.tal[0]||{}).t||E.setor);
    /* sem a leitura nesta tela: na Irrigação, não há medição (o mesmo texto da frente SOLO); no cadastro, a leitura fica no setor (não diz "sem medição", que pode ser falso) */
    v.fpv_cad=cad||(FPV_CTX==='IR'?'sem medição de água no solo neste talhão (Análises de solo)':('lida no setor '+E.setor+' da Irrigação (vem de Análises de solo)'));
    v.fpv_edit=()=>{ g2set(self,'g_fpv',{fmc:null}); self.setState({fpvEd:fpvRascunho(self,id,false)}); }; return; }
  /* registro (novo ou edição): campos da ficha + tabela percentímetro × tempo × lâmina; o que foi digitado fica quando há erro */
  const q=fpvEq(self,id); v.fpv_t=(ed.novo?'Registrar ficha do pivô · ':'Editar ficha do pivô · ')+E.pivo;
  v.fpv_sub=q.nome+' · digite como está na ficha técnica do fabricante. A vazão vale para o cadastro e para a Irrigação (duração e trava de outorga).';
  v.fpv_ff=FPV_CAMPOS.map(c=>{ const er=ed.e[c.k]||''; return {k:c.k,l:c.l,fid:'fpv_f_'+c.k,v:ed.d[c.k]||'',im:c.t==='num'?'decimal':'text',u:c.u||'',hasU:!!c.u,err:!!er,errMsg:er,
    ist:FPV_IST+(er?'#B42318':'#E4E9E5')+';',set:(e)=>{ const cur=self.state.fpvEd; if(!cur) return; const d=Object.assign({},cur.d,{[c.k]:e.target.value}); const e2=Object.assign({},cur.e); delete e2[c.k]; fpvMuda(self,{d:d,e:e2}); }}; });
  const setL=(i,k)=>(e)=>{ const cur=self.state.fpvEd; if(!cur) return; const L=cur.L.map((l,j)=>j===i?Object.assign({},l,{[k]:e.target.value}):l); const le=cur.le.slice(); le[i]=''; fpvMuda(self,{L:L,le:le}); };
  v.fpv_el=ed.L.map((l,i)=>{ const er=ed.le[i]||''; const st=FPV_IST+(er?'#B42318':'#E4E9E5')+';text-align:right;'; const n=i+1;
    return {pct:l.pct,tempo:l.tempo,lam:l.lam,lp:'Percentímetro da linha '+n,lt:'Tempo de volta da linha '+n,ll:'Lâmina da linha '+n,lr:'Remover a linha '+n,st:st,err:!!er,errMsg:er,
      setP:setL(i,'pct'),setT:setL(i,'tempo'),setM:setL(i,'lam'),rm:()=>{ const cur=self.state.fpvEd; if(!cur) return; fpvMuda(self,{L:cur.L.filter((x,j)=>j!==i),le:cur.le.filter((x,j)=>j!==i)}); }}; });
  const L100=[g2num(ed.d.volta_100_h),g2num(ed.d.lamina_100_mm)];
  v.fpv_l100='Linha de 100 %: '+(isNaN(L100[0])?'—':fpvN(L100[0],1)+' h')+' · '+(isNaN(L100[1])?'—':fpvN(L100[1],1)+' mm')+' (vem do tempo de volta e da lâmina a 100 %).';
  v.fpv_add=()=>{ const cur=self.state.fpvEd; if(!cur) return; fpvMuda(self,{L:cur.L.concat([{pct:'',tempo:'',lam:''}])}); };
  v.fpv_hasErr=Object.keys(ed.e).length>0||ed.le.some(Boolean); v.fpv_warn=!!ed.warn;
  v.fpv_save=()=>fpvSalvar(self); v.fpv_cancel=()=>fpvFechar(self,'cancelar');
  v.fpv_discard=()=>fpvFechar(self,'descartar'); v.fpv_keep=()=>fpvMuda(self,{}); }
'''


def store_js():
    """registro gravado + conta (FPV0 da semente): para dados_irrigacao.js_prefixo (todas as telas com o estado da Irrigação) e o CD-03."""
    return 'const FPV0 = ' + json.dumps(seed(), ensure_ascii=False).replace('</', '<\\/') + ';\n' + STORE_JS


def js(ctx):
    """JS da gaveta para a tela (ctx='IR' no IR-01, 'CD' no CD-03): equipamentos de pivô, campos do registro e funções.
    O registro (store_js) vem do prefixo da Irrigação no IR-01; o CD-03 o inclui (cd03())."""
    pol = D.POLITICA_AGUA; rt = pol['autor'].replace(' (', ', ').replace(')', '')
    return ('const FPV_EQ = ' + json.dumps(pivos(), ensure_ascii=False).replace('</', '<\\/') + ';\nconst FPV_CTX = ' + json.dumps(ctx)
            + ';\nconst FPV_CAMPOS = ' + json.dumps(CAMPOS, ensure_ascii=False) + ';\nconst FPV_PCT = ' + json.dumps(PCT_MODELO)
            + ';\nconst FPV_RT = ' + json.dumps(rt, ensure_ascii=False) + ';\n' + UI_JS)


def painel():
    """Gaveta "Ficha do pivô" (sub-detalhe do equipamento). Leitura: campos, tabela da ficha com filtro e ordenação (G2, uma variável por coluna,
    unidade na célula), conferência, CAD do talhão (leitura), a nota de que a ficha não prescreve lâmina e "Editar ficha". Registro (novo ou
    edição): os campos da ficha e a tabela percentímetro × tempo × lâmina, com "Salvar ficha" (a ação primária da gaveta) e "Cancelar"."""
    F = lambda s: H('fpv_' + s)
    TH = f'font-size: 10.5px; font-weight: 700; letter-spacing: .04em; color: {MUTED}; text-transform: uppercase;'
    MUT = f'font-size: 12.8px; color: {MUTED}; line-height: 1.45;'
    LK = f'color: {ACC}; font-weight: 700; text-decoration: none; font-size: 13px;'
    FALSO = '{{false}}'
    lab = lambda t: f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{t}</div>'
    # barra da tabela: a origem dos números e, com filtro aplicado, os filtros com × e "Limpar filtros" (a G2 só mostra a barra com algo nela)
    g = grid(COLS, [], edit=dict(m='none'), gid=GID, search=False, total=False,
             tools=f'<span style="font-size: 12px; color: {MUTED};">Registrada como está na ficha</span>')
    kv = (f'<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 18px; padding: 12px 14px; background: {BG}; border-radius: 12px;">'
          f'<sc-for list="{F("kv")}" as="x" hint-placeholder-count="10"><div style="min-width: 0;"><div style="{TH}">{H("x.l")}</div>'
          f'<div style="font-size: 13.2px; font-weight: 600; margin-top: 2px; line-height: 1.4; overflow-wrap: anywhere;">{H("x.v")}</div></div></sc-for></div>')
    sec = lambda titulo, corpo: (f'<section aria-label="{titulo}" style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top: 1px solid {LINE};">'
                                 f'{lab(titulo)}{corpo}</section>')
    ERR = f'font-size: 12px; font-weight: 700; color: {RED};'
    vista = (f'<sc-if value="{F("vw")}" hint-placeholder-val="{FALSO}">'
             f'<div role="status" style="padding: 9px 12px; border-radius: 10px; font-size: 13px; font-weight: 600; line-height: 1.45; {F("rst")}">{F("resumo")}</div>'
             + kv
             + sec('Percentímetro × tempo de volta × lâmina', f'<div style="min-width: 0;">{g}</div><div style="{MUT}">{F("conta")}</div>')
             + sec('Solo do talhão', f'<div style="font-size: 12.8px; line-height: 1.45;"><b>{F("cadL")}</b><br><span style="color: {MUTED};">{F("cad")}</span></div>')
             + f'<div role="note" style="padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.8px; font-weight: 600; line-height: 1.45;">{F("nota")}</div>'
             + f'<div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; padding-top: 10px; border-top: 1px solid {LINE};">'
               f'<button type="button" onClick="{F("edit")}" style="{BTN_ST(False, True)}">Editar ficha</button>'
               f'<span style="flex-grow: 1;"></span><a href="{F("lkH")}" style="{LK}">{F("lkT")} ›</a></div>'
             + '</sc-if>')
    campo = (f'<sc-for list="{F("ff")}" as="x" hint-placeholder-count="9"><div style="display: flex; flex-direction: column; gap: 4px; min-width: 0;">'
             f'<label for="{H("x.fid")}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{H("x.l")}</label>'
             f'<div style="display: flex; align-items: center; gap: 6px; min-width: 0;"><input id="{H("x.fid")}" type="text" inputMode="{H("x.im")}" value="{H("x.v")}" onChange="{H("x.set")}" style="{H("x.ist")}">'
             f'<sc-if value="{H("x.hasU")}" hint-placeholder-val="{FALSO}"><span style="font-size: 12.5px; color: {MUTED}; white-space: nowrap;">{H("x.u")}</span></sc-if></div>'
             f'<sc-if value="{H("x.err")}" hint-placeholder-val="{FALSO}"><span role="alert" style="{ERR}">{H("x.errMsg")}</span></sc-if></div></sc-for>')
    U = lambda u: f'<span style="font-size: 12px; color: {MUTED}; white-space: nowrap;">{u}</span>'
    cel = lambda val, setf, rot, u: (f'<div style="display: flex; align-items: center; gap: 4px; min-width: 0;"><input type="text" inputMode="decimal" aria-label="{H(rot)}" value="{H(val)}" '
                                     f'onChange="{H(setf)}" style="{H("y.st")}">{U(u)}</div>')
    GRID_L = 'display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)) 30px; gap: 6px; align-items: center;'
    linhas = (f'<div aria-hidden="true" style="{GRID_L} {TH}"><span>Percentímetro</span><span>Tempo de volta</span><span>Lâmina</span><span></span></div>'
              f'<sc-for list="{F("el")}" as="y" hint-placeholder-count="9"><div role="group" aria-label="{H("y.lp")}" style="display: flex; flex-direction: column; gap: 3px;">'
              f'<div style="{GRID_L}">' + cel('y.pct', 'y.setP', 'y.lp', '%') + cel('y.tempo', 'y.setT', 'y.lt', 'h') + cel('y.lam', 'y.setM', 'y.ll', 'mm')
              + f'<button type="button" aria-label="{H("y.lr")}" title="{H("y.lr")}" onClick="{H("y.rm")}" style="border: 0; background: {BG}; width: 28px; height: 28px; border-radius: 999px; cursor: pointer; font-size: 15px; color: {MUTED};">×</button></div>'
              f'<sc-if value="{H("y.err")}" hint-placeholder-val="{FALSO}"><span role="alert" style="{ERR}">{H("y.errMsg")}</span></sc-if></div></sc-for>'
              f'<div><button type="button" onClick="{F("add")}" style="{_MINI}">+ Adicionar linha</button></div>'
              f'<div style="{MUT}">{F("l100")} Linhas sem tempo e sem lâmina não entram.</div>')
    registro = (f'<sc-if value="{F("ed")}" hint-placeholder-val="{FALSO}">'
                f'<sc-if value="{F("hasErr")}" hint-placeholder-val="{FALSO}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">Corrija os campos destacados; o que você preencheu foi mantido.</div></sc-if>'
                f'<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 14px;">{campo}</div>'
                + sec('Percentímetro × tempo de volta × lâmina', linhas)
                + f'<div style="flex-grow: 1;"></div>'
                f'<sc-if value="{F("warn")}" hint-placeholder-val="{FALSO}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.'
                f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{F("discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{F("keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
                f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 8px; border-top: 1px solid {LINE};">'
                f'<button type="button" onClick="{F("cancel")}" style="{BTN_ST(False, True)}">Cancelar</button><button type="button" onClick="{F("save")}" style="{BTN_ST(True, True)}">Salvar ficha</button></div>'
                '</sc-if>')
    return (f'<sc-if value="{F("open")}" hint-placeholder-val="{FALSO}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
            f'<button type="button" tabIndex="-1" aria-label="Fechar ficha do pivô" onClick="{F("close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
            f'<aside role="dialog" aria-modal="true" aria-label="Ficha do pivô · {F("pivo")}" onKeyDown="{F("key")}" class="fpv-gaveta" style="position: relative; width: 680px; max-width: 100%; height: 100vh; '
            f'overflow-y: auto; overflow-x: hidden; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px;"><div style="display: flex; flex-direction: column; gap: 3px; flex-grow: 1; min-width: 0;">'
            f'<h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em; line-height: 1.3;">{F("t")}</h2>'
            f'<div style="{MUT}">{F("sub")}</div></div>'
            f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{F("close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
            + vista + registro
            + '</aside></div></sc-if>')
