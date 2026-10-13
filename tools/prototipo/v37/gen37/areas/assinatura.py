# -*- coding: utf-8 -*-
"""CF-05 · Assinatura e cobrança (PLAT-01; docs/plataforma-assinaturas/ESPECIFICACAO.md §3.1). Menu › Configurações.
A organização vê, numa tela, quanto paga, por quê e o que fazer: plano, uso medido lido do cadastro (nunca digitado aqui), faturas com a
memória da cobrança, troca de plano ou área com prévia antes → depois e o painel "Demonstração" que avança a data da cobrança.
Cobrança simulada: nenhum provedor, nenhuma credencial, nenhum campo de cartão (a forma é escolhida numa lista). Estado em c.assin do
cenário salvo (assinatura.js, prefixo de toda tela); valores por assinMensalidade (regra decimal única cenQtd).
Uma ação primária (R14): Pagar fatura › Ampliar área contratada › Alterar plano ou área. A faixa de cobrança não aparece aqui (R11).
Os painéis (fatura, plano) e o estilo vivem aqui e são usados também pela plataforma (areas/plataforma.py)."""
import json
from engine import grid, section, esc, BTN_ST, INK, MUTED, LINE, BG, SURF, ACC, ACCS, YEL, YELS, RED, REDS, DISP, EXTRAJS
import engine as E
import ui37
from ui37 import shell37, HEIGHTS37
import cenario
import dados_assinatura as DA
import dados_cad as DC

H = lambda s: '{{' + s + '}}'
PERFIL_CF = DA.GESTORA   # quem age no CF-05 (perfil da casca), gravado em cada ato (revisão PLAT, achado 4)
F_ = H('false'); T_ = H('true')
SEC = BTN_ST(False, True)
PRI = BTN_ST(True, True)
LNK = f'border: 0; background: transparent; padding: 0; color: {ACC}; font-family: inherit; font-size: 13px; font-weight: 700; cursor: pointer; text-decoration: underline; text-underline-offset: 3px;'
# escolha (Pix/boleto/cartão, Essencial/Completo, filtro rápido escolhido): tonal (DS-36), nunca o verde cheio da primária (A11)
CSS = ('<style>'
       '.assin-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}'
       '.assin-kpi{padding:14px 16px;background:#FFFFFF;border:1px solid #E4E9E5;border-radius:16px;display:flex;flex-direction:column;gap:6px;min-width:0}'
       '.assin-kl{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#65736A;font-weight:700}'
       ".assin-kv{font-family:'Sora','Manrope',sans-serif;font-size:24px;font-weight:700;letter-spacing:-.02em;line-height:1.15;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}"
       '.assin-ks{font-size:12.5px;color:#65736A;line-height:1.35}'
       '.assin-esc{font-family:inherit;font-size:13px;font-weight:700;padding:8px 14px;border-radius:999px;border:1px solid #E4E9E5;background:#FFFFFF;color:#15201A;cursor:pointer}'
       '.assin-esc[aria-checked=true]{border-color:#1E7A4C;background:#E4F3E9;color:#1E7A4C}'
       '.assin-esc:disabled{opacity:.45;cursor:not-allowed}.assin-prim:is(:disabled,[aria-disabled=true]){opacity:.5;cursor:not-allowed}'
       '.assin [role=group] button[aria-pressed=true]{background:#E4F3E9!important;color:#1E7A4C!important;border-color:#1E7A4C!important}'
       '.assin-lin{display:flex;justify-content:space-between;gap:12px;padding:7px 0;border-bottom:1px solid #E4E9E5;font-size:13px;line-height:1.4}'
       '.assin-lin>span:first-child{color:#65736A;flex-shrink:0;max-width:46%}.assin-lin>span:last-child{text-align:right;min-width:0;overflow-wrap:anywhere}'
       '.assin-pv{display:flex;flex-direction:column;gap:2px;padding:7px 0;border-bottom:1px solid #E4E9E5;font-size:13px}'
       '.assin-pv b{font-weight:700}.assin-pv .mud{color:#1E7A4C;font-weight:800}'
       '@media (max-width:640px){.assin-kpis{grid-template-columns:1fr 1fr;gap:10px}.assin-kv{font-size:19px}.assin-kpi{padding:12px}}'
       '</style>')


def kpis_dyn(pre, rotulos):
    """resumo de 4 números com valores do estado (2 × 2 no celular)."""
    return '<div class="assin-kpis">' + ''.join(
        f'<div class="assin-kpi"><div class="assin-kl">{esc(r)}</div><div class="assin-kv">{H(f"{pre}{i}v")}</div><div class="assin-ks">{H(f"{pre}{i}s")}</div></div>'
        for i, r in enumerate(rotulos)) + '</div>'


def painel(hole, corpo, rodape, largura=480):
    """painel lateral (aside role=dialog) do mesmo padrão dos formulários G2: fundo escuro fecha; Esc fecha; título vem do estado."""
    return (f'<sc-if value="{H(hole)}" hint-placeholder-val="{F_}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
            f'<button type="button" aria-label="Fechar" tabIndex="-1" onClick="{H(hole + "_fechar")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
            f'<aside role="dialog" aria-label="{H(hole + "_tit")}" onKeyDown="{H(hole + "_tecla")}" style="position: relative; width: {largura}px; max-width: 100%; height: 100%; overflow-y: auto; background: {SURF}; '
            f'box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em; flex-grow: 1;">{H(hole + "_tit")}</h2>'
            f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H(hole + "_fechar")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
            + corpo + '<div style="flex-grow: 1;"></div>' + rodape + '</aside></div></sc-if>')


def linhas(lista):
    """lista rótulo → valor (memória da cobrança, totais por fazenda)."""
    return (f'<div><sc-for list="{H(lista)}" as="ln" hint-placeholder-count="4"><div class="assin-lin"><span>{H("ln.t")}</span><span style="{H("ln.st")}">{H("ln.v")}</span></div></sc-for></div>')


def eventos(lista):
    return (f'<div style="font-size: 12px; font-weight: 800; letter-spacing: .06em; color: {MUTED};">EVENTOS</div>'
            f'<div><sc-for list="{H(lista)}" as="ev" hint-placeholder-count="2"><div class="assin-lin"><span>{H("ev.d")}</span><span>{H("ev.t")}</span></div></sc-for></div>')


def titulo(t):
    return f'<div style="font-size: 12px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{esc(t)}</div>'


def chip_dyn(key):
    return f'<span style="{H(key + "_st")}"><span style="{H(key + "_dot")}"></span>{H(key)}</span>'


def injeta(fname, tit, html):
    """conteúdo dinâmico logo depois do título (a casca só aceita estado fixo)."""
    import os
    p = os.path.join(E.P, fname); s = open(p, encoding='utf-8').read(); alvo = f'>{esc(tit)}</h1>'
    assert s.count(alvo) == 1, (fname, alvo)
    open(p, 'w', encoding='utf-8').write(s.replace(alvo, alvo + html, 1))


# JS comum às telas da assinatura (CF-05 e plataforma): partes de célula, estilo do selo e o painel da fatura
JS_COMUM = r'''
function aCh(t,c){ return {k:'chip',t:t,c:c||'gray'}; }
function aSelo(self,v,key,t,c){ const cc=G2C[c]||G2C.gray; v[key]=t; v[key+'_st']='display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';';
  v[key+'_dot']='width:6px;height:6px;border-radius:999px;background:'+cc[0]+';'; }
function aGrid(id){ return GRIDS.find(g=>g.id===id); }
function aPainel(self,v,hole,aberto,tit,fechar){ v[hole]=!!aberto; v[hole+'_tit']=tit||''; v[hole+'_fechar']=fechar; v[hole+'_tecla']=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); fechar(); } }; }
// memória da cobrança de uma fatura (cópia da fatura; a prévia do período aberto é calculada ao vivo)
function aMemoria(f){ const C=f.copia||{}; const P=assinPlano(C.plano)||{}; const bruto=(C.bruto!==undefined&&C.bruto!==null)?C.bruto:cenQtd(C.preco,C.cobrada);
  const L=[{t:'Área medida',v:assinHa(C.medida)+(C.ntal===null||C.ntal===undefined?' · informada pela organização':' · '+C.ntal+' talhões')+(f.previa?' · ao vivo até '+assinBrC(C.fechamento):' · fechamento '+assinBrC(C.fechamento))}];
  if(C.abertura!==null&&C.abertura!==undefined) L.push({t:'Medida do período',v:'maior entre a abertura ('+assinBrC(C.abertura_d)+': '+assinHa(C.abertura)+') e '+(f.previa?'hoje ('+assinBrC(C.hoje)+': ':'o fechamento ('+assinBrC(C.fechamento)+': ')+assinHa(C.fech)+')'+(C.piso?' · vale a abertura: inativar talhão não reduz o mês em curso':'')});
  L.push({t:'Área contratada',v:(P.pago?assinHa(C.contratada)+' · contrato '+C.versao+(C.aceite_por?' · aceite por '+C.aceite_por:''):'— (avaliação)')},
    {t:'Área cobrada',v:'mín(medida; contratada) = '+assinHa(C.cobrada)},
    {t:'Conta',v:P.pago?('máx('+assinR(C.minimo)+'; '+assinR(C.preco)+'/ha·mês × '+assinHa(C.cobrada)+' = '+assinR(bruto)+') = '+assinR(Math.max(C.minimo,bruto))):'avaliação · sem cobrança'});
  if(C.credito) L.push({t:'Crédito do período',v:'− '+assinR(C.credito)});
  if(C.saldo) L.push({t:'Saldo de crédito',v:assinR(C.saldo)+' para '+assinComp(C.saldo_comp)+' (o que passou da fatura não se perde)'});
  L.push({t:f.previa?'Prévia do período':'Valor da fatura',v:assinR(f.valor),st:'font-weight:800;'});
  if(P.pago) L.push({t:'Pela área contratada seria',v:assinR(assinMensalidade(C.plano,C.contratada,C.contratada,0).valor)+' (DEC-01, a decidir pelo proprietário)'});
  L.push({t:'Plano',v:(P.nome||'—')+' · '+(P.pago?assinR(P.preco)+'/ha·mês · mínimo '+assinR(P.minimo):'sem cobrança')});
  return L.map(x=>Object.assign({st:''},x)); }
function aAno(P){ return P&&P.pago?assinR(cenQtd(P.preco,12))+'/ha·ano':'—'; }   /* equivalente anual pela regra decimal única (achado 8) */
function aEventos(f){ return (f.eventos||[]).slice().sort((a,b)=>(a.d<b.d?-1:(a.d>b.d?1:0))).map(e=>({d:assinBr(e.d),t:e.t})); }
// baixa a fatura em CSV (gerado no navegador a partir da cópia da fatura); a última fica em window.__assinCsv para conferência
function aBaixar(self,org,f){ const csv=assinCsv(org,f); try{ window.__assinCsv=csv; }catch(e){}
  try{ const b=new Blob(['﻿'+csv],{type:'text/csv;charset=utf-8'}); const a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download='fatura-'+org.id+'-'+f.comp+'.csv';
    document.body.appendChild(a); a.click(); setTimeout(()=>{ try{ URL.revokeObjectURL(a.href); a.remove(); }catch(e){} },500); }catch(e){}
  self.setState({g2toast:'Fatura de '+assinComp(f.comp)+' baixada em CSV (cópia da fatura, gerada no navegador).'}); }
'''

CF_JS = r'''
function cfMed(){ return assinMedir(ASSIN_CAD0, assinCadSalvo()); }
function cfSafe(id){ return String(id).replace(/[^A-Za-z0-9]/g,'_'); }
function cfFaturas(org,A,med){ return (org.faturas||[]).concat([assinPrevia(org,A.hoje,med.ha,med.n)]); }
function cfAbreFat(self,id){ self.setState({cf_fat:id,cf_chave:assinChave('pag'),cf_forma:'',cf_ferr:'',cf_cts:false,cf_motivo:'',cf_cts_chave:assinChave('cts'),cf_pl:false}); }
function cfAbrePl(self,plano,ha){ self.setState({cf_pl:true,cf_pl_plano:plano,cf_pl_ha:assinNf(ha,0,2),cf_pl_chave:assinChave('ace'),cf_des_chave:assinChave('des'),cf_pl_err:'',cf_fat:null}); }
function cfFranq(P){ return P.pago?('satélite '+P.sat+' '+P.sat_un+' · IA '+P.ia+' '+P.ia_un):('satélite '+P.sat+' · IA '+P.ia+' no período'); }
function PREVALS(self,v){ cenOuvir(self); assinOuvir(self,true);
  const A=assinLer(), org=A.orgs[A.demo], hoje=A.hoje, med=cfMed(); const k=assinContrato(org,hoje), ag=assinAgendado(org,hoje), P=assinPlano(k.plano);
  const pv=assinPrevia(org,hoje,med.ha,med.n); self._cf={A,org,hoje,med,k,ag,P,pv};
  // bloco 1 · uso medido (lido do cadastro; só leitura; a origem abre o cadastro)
  aGrid('g_uso').rows=med.linhas.map(l=>({id:'u_'+l.id,v:{faz:l.faz,t:l.t,decl:l.decl,sit:l.sit},s:{faz:l.faz,sit:l.sit},p:{t:[{k:'b',t:l.t}],sit:[aCh(l.sit,l.conta?'green':'gray')]},
    o:[{t:'Abrir no cadastro',h:'CD-01det.dc.html#talhao='+encodeURIComponent(l.id)}].concat(l.contorno?[]:[{t:'Sem contorno validado: a área cultivável vem do cadastro e não é conferida por geometria (limite conhecido).'}])}));
  // bloco 2 · faturas (as fechadas são cópia; o período aberto é a prévia ao vivo)
  aGrid('g_fat').rows=cfFaturas(org,A,med).map(f=>{ const est=assinFatEstado(f,hoje); const C=f.copia; const Pp=assinPlano(C.plano)||{};
    const regra=Pp.pago?(assinR(Pp.preco)+'/ha·mês · mínimo '+assinR(Pp.minimo)):'avaliação · sem cobrança';
    return {id:f.id,dr:'cf_fat_'+cfSafe(f.id),v:{comp:f.comp+'-01',cob:C.cobrada,regra:regra,val:f.valor,venc:f.venc,est:est},s:{comp:assinComp(f.comp),regra:regra,est:est},
      p:{comp:[{k:'b',t:assinComp(f.comp)}].concat(f.previa?[{k:'mut',t:'prévia'}]:[]),est:[aCh(est,ASSIN_FCOR[est])]}}; });
  // bloco 3 · planos (a Avaliação só aparece no BO-01)
  const kc=ag||k; aGrid('g_pl').rows=ASSIN_PAR.planos.filter(x=>x.pago).map(x=>{ const m=assinMensalidade(x.id,med.ha,kc.ha,0); const seu=x.id===k.plano, agd=ag&&ag.plano===x.id&&x.id!==k.plano;
    return {id:'pl_'+x.id,dr:'cf_pl_'+x.id,v:{plano:x.nome,mod:x.modulos.join(', '),lim:'até '+assinNf(x.limite,0,0)+' ha',usu:x.usuarios,fr:cfFranq(x),preco:x.preco,min:x.minimo,val:m.valor,sel:seu?'Seu plano':(agd?'Agendado para '+assinBrC(ag.desde):'—')},
      s:{sel:seu?'Seu plano':(agd?'Agendado para '+assinBrC(ag.desde):'—')},
      p:{plano:[{k:'b',t:x.nome}],mod:x.id==='ess'?[{k:'txt',t:'Núcleo: '+x.modulos.join(', ')}]:[{k:'txt',t:'Núcleo + '+ASSIN_PAR.planos.find(y=>y.id==='comp').modulos.filter(md=>ASSIN_PAR.planos.find(y=>y.id==='ess').modulos.indexOf(md)<0).join(', ')}],
        preco:[{k:'txt',t:assinR(x.preco)},{k:'mut',t:aAno(x)+' · exemplo'}],min:[{k:'txt',t:assinR(x.minimo)},{k:'mut',t:'exemplo'}],
        val:[{k:'b',t:assinR(m.valor)},{k:'mut',t:'com '+assinHa(med.ha)}],sel:seu?[aCh('Seu plano','green')]:(agd?[aCh('Agendado para '+assinBrC(ag.desde),'yellow')]:[{k:'mut',t:'—'}])}}; }); }
function EXTRAVALS(self,v){ const X=self._cf; const {A,org,hoje,med,k,ag,P,pv}=X; const st=self.state;
  const est=assinEstado(org,hoje); aSelo(self,v,'cf_st',est.t+(est.dias?' · '+est.dias+(est.dias===1?' dia':' dias'):''),est.c);
  const ab=assinAberta(org); const prim=assinPrimaria(org,hoje,med.ha);
  // resumo
  v.cf_k0v=P.nome; v.cf_k0s=(P.pago?assinR(P.preco)+'/ha·mês · contrato v'+k.v:'sem cobrança')+(ag?' · '+assinPlano(ag.plano).nome+' agendado para '+assinBrC(ag.desde):'');
  v.cf_k1v=assinHa(med.ha); v.cf_k1s='de '+assinHa(k.ha)+' contratados · '+med.n+' talhões'+(ag&&ag.ha!==k.ha?' · '+assinHa(ag.ha)+' a partir de '+assinBrC(ag.desde):'');
  v.cf_k2v=assinR(pv.valor); v.cf_k2s=assinComp(pv.comp)+' fecha em '+assinBrC(pv.copia.fechamento)+(pv.copia.piso?' · medida da abertura '+assinHa(pv.copia.medida):'')
    +(pv.copia.credito?' · crédito de '+assinR(pv.copia.credito):'')+(pv.copia.saldo?' · saldo de '+assinR(pv.copia.saldo)+' para '+assinComp(pv.copia.saldo_comp):'');
  if(ab){ const ea=assinFatEstado(ab,hoje); v.cf_k3v=assinR(ab.valor); v.cf_k3s='fatura de '+assinComp(ab.comp)+' · '+(ea==='Vencida'?'vencida em '+assinBrC(ab.venc):'vence '+assinBrC(ab.venc)); }
  else { v.cf_k3v=assinBr(pv.venc); v.cf_k3s='fatura de '+assinComp(pv.comp)+' · Pix, boleto ou cartão (simulado)'; }
  // acima do contratado: não entra na cobrança sem aceite (R2)
  const lim=(ag||k).ha; const exc=assinCent(med.ha)-assinCent(k.ha);
  v.cf_acima=exc>0; v.cf_acima_t=exc>0?(assinHa(exc/100)+' acima da área contratada não entram na cobrança de '+assinComp(pv.comp)+(assinCent(med.ha)>assinCent(lim)||!ag?'; com o aceite da ampliação, entram a partir de '+assinBr(assinMesSeg(hoje))+'.':'; a ampliação já está agendada para '+assinBr(ag.desde)+'.')):'';
  v.cf_pessoas='Pessoas com acesso: '+CF_PESSOAS+' (Cadastros › Pessoas e equipes) · usuários sem limite · não entram na cobrança';
  // primária única (R14)
  v.cf_prim_dis=false; v.cf_prim_tit='';
  if(prim==='pagar'){ v.cf_prim_t='Pagar fatura'; v.cf_prim_fn=()=>cfAbreFat(self,ab.id); }
  else if(prim==='proposta'){ const pr=org.proposta; if(!self.__cfPro) self.__cfPro=assinChave('pro'); const kp=self.__cfPro;
    v.cf_prim_t=pr?'Proposta empresarial pedida em '+assinBrC(pr.d):'Pedir proposta empresarial'; v.cf_prim_dis=!!pr;
    v.cf_prim_tit=pr?'Pedido '+pr.recibo+' por '+pr.por+': a plataforma responde; a cobrança segue o contrato de hoje.':'Medida acima de '+assinNf(ASSIN_PAR.limite_ha,0,0)+' ha: os planos vão até esse limite.';
    v.cf_prim_fn=()=>{ if(!pr) cenMudar(self,c=>assinProposta(c,cfMed().ha,kp,CF_POR)); }; }
  else if(prim==='ampliar'){ v.cf_prim_t='Ampliar área contratada'; v.cf_prim_fn=()=>cfAbrePl(self,k.plano,assinSugere(med.ha)); }
  else { v.cf_prim_t='Alterar plano ou área'; v.cf_prim_fn=()=>cfAbrePl(self,(ag||k).plano,(ag||k).ha); }
  // linhas: abrir fatura e plano
  cfFaturas(org,A,med).forEach(f=>{ v['cf_fat_'+cfSafe(f.id)]=()=>cfAbreFat(self,f.id); });
  ASSIN_PAR.planos.forEach(x=>{ v['cf_pl_'+x.id]=()=>cfAbrePl(self,x.id,(ag||k).ha); });
  // atalho da faixa: CF-05.dc.html#pagar abre a fatura aberta
  if(!self.__cfh){ self.__cfh=1; let h=''; try{ h=location.hash||''; }catch(e){} if(/pagar/.test(h)&&ab) setTimeout(()=>cfAbreFat(self,ab.id),0); }
  // origem do talhão: o título diz o talhão (a 1ª coluna da grade é a fazenda)
  const FU=v.g_uso_F, fu=g2st(self,'g_uso').fm; if(FU&&FU.open&&fu&&fu.rid){ const r=g2find(aGrid('g_uso').rows,fu.rid); if(r) FU.title='Talhão '+r.v.t+' · '+r.v.faz; }
  // ---- painel da fatura ----
  const f=st.cf_fat?cfFaturas(org,A,med).find(x=>x.id===st.cf_fat):null; const fe=f?assinFatEstado(f,hoje):'';
  aPainel(self,v,'cf_fp',!!f,f?'Fatura de '+assinComp(f.comp):'',()=>self.setState({cf_fat:null}));
  if(f){ aSelo(self,v,'cf_fest',fe,ASSIN_FCOR[fe]); v.cf_fsub=f.previa?'Prévia do período em medição: o valor muda com o cadastro até o fechamento; depois a fatura guarda a cópia e nunca é recalculada.':'Cópia da fatura emitida em '+assinBr(f.emitida)+' · vence '+assinBr(f.venc)+' · cobrança simulada, nenhum valor é cobrado.';
    v.cf_fmem=aMemoria(f); v.cf_fev=aEventos(f); v.cf_temev=v.cf_fev.length>0;
    v.cf_fpag=f.st==='aberta'; v.cf_formas=ASSIN_PAR.formas.map(x=>({t:x+' · simulado',on:String(st.cf_forma===x),go:()=>self.setState({cf_forma:x,cf_ferr:''})}));
    v.cf_ferr=st.cf_ferr||''; v.cf_tferr=!!st.cf_ferr;
    v.cf_pagar=()=>{ const r=cenMudar(self,c=>assinPagar(c,f.id,self.state.cf_forma,self.state.cf_chave,CF_POR)); self.setState({cf_ferr:r.erro||''}); };
    v.cf_podects=assinPodeContestar(f); v.cf_cts=!!st.cf_cts&&v.cf_podects; v.cf_cts_tog=()=>self.setState({cf_cts:!self.state.cf_cts});   /* uma contestação por fatura (achado 1) */
    v.cf_motivo=st.cf_motivo||''; v.cf_setmot=(e)=>self.setState({cf_motivo:e.target.value});
    v.cf_contestar=()=>{ const r=cenMudar(self,c=>assinContestar(c,f.id,self.state.cf_motivo,self.state.cf_cts_chave,CF_POR)); if(!r.erro) self.setState({cf_cts:false}); };
    v.cf_csv=()=>aBaixar(self,org,f); }
  else { v.cf_fmem=[]; v.cf_fev=[]; v.cf_formas=[]; }
  // ---- painel do plano ou área (prévia hoje → depois) ----
  aPainel(self,v,'cf_pp',!!st.cf_pl,'Alterar plano ou área',()=>self.setState({cf_pl:false}));
  if(st.cf_pl){ const pl=st.cf_pl_plano||k.plano; const P1=assinPlano(pl); const ha=assinNum(st.cf_pl_ha); const desde=assinMesSeg(hoje);
    v.cf_ppl=ASSIN_PAR.planos.filter(x=>x.pago).map(x=>({t:x.nome,on:String(pl===x.id),go:()=>self.setState({cf_pl_plano:x.id,cf_pl_err:'',cf_pl_chave:assinChave('ace')})}));
    v.cf_pha=st.cf_pl_ha||''; v.cf_setha=(e)=>self.setState({cf_pl_ha:e.target.value,cf_pl_err:'',cf_pl_chave:assinChave('ace')});
    const teto=assinCent(med.ha)>assinCent(ASSIN_PAR.limite_ha);
    v.cf_pha_aj='medida hoje: '+assinHa(med.ha)+' · o plano vai até '+assinNf(ASSIN_PAR.limite_ha,0,0)+' ha'+(teto?': acima disso, proposta empresarial (primária)':'');
    const ve=assinValidaArea(st.cf_pl_ha,med.ha); v.cf_pl_err=st.cf_pl_err||''; v.cf_tplerr=!!v.cf_pl_err; v.cf_pha_st='width:160px;font-family:inherit;font-size:14px;padding:9px 11px;border-radius:10px;box-sizing:border-box;border:1px solid '+(v.cf_pl_err?'#B42318':'#E4E9E5')+';';
    v.cf_pini='Início: '+assinBr(desde)+' (dia 1 do próximo ciclo; a mudança nunca retroage)';
    const m0=assinMensalidade(k.plano,med.ha,k.ha,0), m1=(P1&&!ve)?assinMensalidade(pl,med.ha,ha,0):null;
    const mods=(a,b)=>{ const sai=a.modulos.filter(x=>b.modulos.indexOf(x)<0), ent=b.modulos.filter(x=>a.modulos.indexOf(x)<0); return sai.length?'saem: '+sai.join(', '):(ent.length?'entram: '+ent.join(', '):'nenhum'); };
    const dif=m1?(assinCent(m1.valor)-assinCent(m0.valor))/100:null;
    const L=[['Plano',P.nome,P1?P1.nome:'—'],['Área contratada',assinHa(k.ha),isNaN(ha)?'—':assinHa(ha)],['Preço',assinR(P.preco)+'/ha·mês · '+aAno(P),P1?assinR(P1.preco)+'/ha·mês · '+aAno(P1):'—'],
      ['Mínimo',assinR(P.minimo)+'/mês',P1?assinR(P1.minimo)+'/mês':'—'],['Franquias',cfFranq(P),P1?cfFranq(P1):'—'],
      ['Mensalidade com a área medida hoje ('+assinHa(med.ha)+')',assinR(m0.valor),m1?assinR(m1.valor):'—'],
      ['Diferença por mês','',dif===null?'—':((dif>0?'+':(dif<0?'−':''))+assinR(Math.abs(dif)).replace('R$ ','R$ '))],
      ['Módulos que mudam','',P1?mods(P,P1):'—'],['Periodicidade','','mensal'],['Prazo e cancelamento','',ASSIN_PAR.cancelamento]];
    v.cf_pv=L.map(x=>({t:x[0],a:x[1],b:x[2],tema:!!x[1]&&x[1]!==x[2]}));   /* só o que muda mostra hoje → depois */
    const alvo=ag||k; v.cf_pl_pode=!teto&&!(alvo.plano===pl&&assinCent(alvo.ha)===assinCent(ha));
    v.cf_pl_ok='Aceitar e agendar para '+assinBr(desde);
    v.cf_aceitar=()=>{ const r=cenMudar(self,c=>assinMudar(c,pl,self.state.cf_pl_ha,cfMed().ha,self.state.cf_pl_chave,CF_POR)); self.setState({cf_pl_err:r.erro||''}); };   /* a chave muda quando o formulário muda (ou ao desfazer): o clique repetido devolve o mesmo recibo (R8) */
    v.cf_tag=!!ag; v.cf_ag_t=ag?('Mudança agendada: '+assinPlano(ag.plano).nome+' · '+assinHa(ag.ha)+' a partir de '+assinBr(ag.desde)+' (aceite '+assinBrC(ag.aceite)+(ag.recibo?' · '+ag.recibo:'')+(ag.por?' · por '+ag.por:'')+').'):'';
    v.cf_desfazer=()=>{ const r=cenMudar(self,c=>assinDesfazer(c,self.state.cf_des_chave,CF_POR)); if(!r.erro&&!r.repetido) self.setState({cf_pl_chave:assinChave('ace'),cf_des_chave:assinChave('des')}); }; }
  else { v.cf_ppl=[]; v.cf_pv=[]; }
  // ---- demonstração: data simulada da cobrança (só avança) e restaurar ----
  v.cf_hoje=assinBr(hoje);
  v.cf_datas=ASSIN_PAR.datas.map(d=>{ const cur=d===hoje, pas=assinD(d)<assinD(hoje); return {t:assinBr(d)+(cur?' · atual':''),dis:cur||pas,on:String(cur),
    go:()=>{ if(cur||pas) return; const m=cfMed(); cenMudar(self,c=>assinAvancar(c,d,{ha:m.ha,n:m.n})); }}; });
  v.cf_restaurar=()=>cenMudar(self,c=>{ delete c.assin; return {msg:'Assinatura da demonstração restaurada: data simulada 23/09/2026, contrato v2, sem fatura aberta. O cadastro não mudou.'}; }); }
'''


def build():
    fname = 'CF-05.dc.html'; E._reset_screen(fname)
    ui37.CAT['CF-05'] = dict(ui37.CAT.get('CF-05', {}), titulo='Assinatura e cobrança')
    tal_cols = [dict(k='faz', l='Fazenda', w=150), dict(k='t', l='Talhão', w=150), dict(k='decl', l='Área cultivável (ha)', t='num', a='r', d=2, dmin=0, agg='sum'),
                dict(k='sit', l='Situação', w=200)]
    g_uso = grid(tal_cols, [], gid='g_uso', search=True, total=True, so={'k': 'decl', 'd': True}, qf=dict(k='faz', todas='Todas'),
                 edit=dict(m='origin', title='Talhão', fields=[dict(k='faz', l='Fazenda', ro=True), dict(k='t', l='Talhão', ro=True),
                                                             dict(k='decl', l='Área cultivável', t='num', u='ha', ro=True), dict(k='sit', l='Situação', ro=True)]))
    g_fat = grid([dict(k='comp', l='Competência', t='date', w=150), dict(k='cob', l='Área cobrada (ha)', t='num', a='r', d=2, dmin=0),
                  dict(k='regra', l='Regra', w=260), dict(k='val', l='Valor (R$)', t='num', a='r', d=2), dict(k='venc', l='Vencimento', t='date'),
                  dict(k='est', l='Estado', w=150)], [], gid='g_fat', search=True, total=False, so={'k': 'comp', 'd': True}, qf=dict(k='est', todas='Todos'),
                 edit=dict(m='ro', title='Fatura', fields=[]))
    g_pl = grid([dict(k='plano', l='Plano', w=120), dict(k='mod', l='Módulos', w=340), dict(k='lim', l='Limite de área'), dict(k='usu', l='Usuários'),
                 dict(k='fr', l='Franquias', w=240), dict(k='preco', l='Preço R$/ha·mês', t='num', a='r', w=200), dict(k='min', l='Mínimo R$/mês', t='num', a='r'),
                 dict(k='val', l='Valor para a sua área', t='num', a='r', w=170), dict(k='sel', l='Situação', w=170)], [], gid='g_pl', search=True, total=False,
                edit=dict(m='ro', title='Plano', fields=[]))
    nota = lambda t, cor=MUTED: f'<div style="font-size: 12.5px; color: {cor}; line-height: 1.45; padding-top: 10px;">{t}</div>'
    aviso = (f'<sc-if value="{H("cf_acima")}" hint-placeholder-val="{F_}"><div role="note" style="padding: 9px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700; line-height: 1.4;">'
             f'{H("cf_acima_t")}</div></sc-if>')
    datas = (f'<div role="group" aria-label="Data simulada da cobrança" style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">'
             f'<sc-for list="{H("cf_datas")}" as="dt" hint-placeholder-count="4"><button type="button" class="assin-esc" aria-checked="{H("dt.on")}" disabled="{H("dt.dis")}" onClick="{H("dt.go")}">{H("dt.t")}</button></sc-for>'
             f'<span style="flex-grow: 1;"></span><button type="button" onClick="{H("cf_restaurar")}" style="{SEC}">Restaurar assinatura da demonstração</button></div>')
    demo = (f'<div style="background: {YELS}; border: 1px solid #F1DDA8; border-radius: 16px; padding: 14px 18px; display: flex; flex-direction: column; gap: 10px;">'
            f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;"><span style="font-size: 15px; font-weight: 800; color: {YEL};">Demonstração</span>'
            f'<span style="font-size: 12px; font-weight: 700; color: {YEL};">só demonstração · avança a data da cobrança, não a dos outros módulos</span></div>'
            f'<div style="font-size: 13px; color: {INK};">Data simulada da cobrança: <b>{H("cf_hoje")}</b>. O período fecha no último dia do mês e a fatura vence no dia 1 (exemplo, a decidir pelo proprietário).</div>'
            + datas + '</div>')
    corpo = ('<div class="assin" style="display: flex; flex-direction: column; gap: 18px;">' + CSS
             + kpis_dyn('cf_k', ['Plano', 'Área medida', 'Prévia do período', 'Próxima cobrança']) + aviso
             + section('Uso medido', 'Confira a área que define a cobrança; ela vem do cadastro e não se digita aqui. Clique no talhão para abrir a origem.', '',
                       nota(f'Origem: Cadastros › Fazendas, áreas e talhões · conta a área cultivável dos talhões ativos de fazendas ativas; safra, parcela e operação não entram.').replace('padding-top: 10px;', 'padding: 0 0 10px;')
                       + g_uso + nota(H('cf_pessoas')))
             + section('Faturas', 'Abra a fatura para ver a memória da cobrança, pagar (simulado), contestar ou baixar em CSV.', '', g_fat)
             + section('Planos', 'Compare os planos com o valor para a sua área; clique no plano para ver a prévia e aceitar a mudança.', '',
                       nota(f'Preço, mínimo, franquias e cancelamento: <b>exemplo · a decidir pelo proprietário</b> (DEC-01, DEC-05, DEC-09). Usuários sem limite e fora da cobrança.', YEL).replace('padding-top: 10px;', 'padding: 0 0 10px;')
                       + g_pl)
             + demo + '</div>')
    # painel da fatura
    formas = (f'<div role="radiogroup" aria-label="Forma de pagamento" style="display: flex; flex-wrap: wrap; gap: 8px;"><sc-for list="{H("cf_formas")}" as="fo" hint-placeholder-count="3">'
              f'<button type="button" role="radio" class="assin-esc" aria-checked="{H("fo.on")}" onClick="{H("fo.go")}">{H("fo.t")}</button></sc-for></div>')
    corpo_f = (f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">{chip_dyn("cf_fest")}<span style="font-size: 12.5px; color: {MUTED}; line-height: 1.4;">{H("cf_fsub")}</span></div>'
               + titulo('Memória da cobrança') + linhas('cf_fmem')
               + f'<sc-if value="{H("cf_temev")}" hint-placeholder-val="{F_}">{eventos("cf_fev")}</sc-if>'
               + f'<sc-if value="{H("cf_fpag")}" hint-placeholder-val="{F_}"><div style="display: flex; flex-direction: column; gap: 8px; padding-top: 6px;">{titulo("Forma de pagamento (simulado)")}{formas}'
               + f'<span style="font-size: 11.5px; color: {MUTED};">Nenhum dado de cartão, conta ou documento é pedido: o pagamento é simulado e o evento do provedor chega na hora.</span>'
               + f'<sc-if value="{H("cf_tferr")}" hint-placeholder-val="{F_}"><span role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("cf_ferr")}</span></sc-if></div></sc-if>'
               + f'<sc-if value="{H("cf_cts")}" hint-placeholder-val="{F_}"><div style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border-radius: 12px; background: {BG};">'
               + f'<label for="cf_motivo" style="font-size: 12px; font-weight: 700; color: {MUTED};">Motivo da contestação</label>'
               + f'<textarea id="cf_motivo" value="{H("cf_motivo")}" onChange="{H("cf_setmot")}" style="font-family: inherit; font-size: 13.5px; padding: 9px 11px; border-radius: 10px; border: 1px solid {LINE}; min-height: 64px; resize: vertical;"></textarea>'
               + f'<span style="font-size: 11.5px; color: {MUTED};">Enquanto a plataforma não resolve, a fatura não conta atraso nem restringe nada. A fatura não é reescrita.</span>'
               + f'<div><button type="button" onClick="{H("cf_contestar")}" style="{SEC}">Registrar contestação</button></div></div></sc-if>')
    rod_f = (f'<div style="display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; padding-top: 10px; border-top: 1px solid {LINE};">'
             f'<button type="button" onClick="{H("cf_csv")}" style="{SEC}">Baixar fatura (CSV)</button>'
             f'<sc-if value="{H("cf_podects")}" hint-placeholder-val="{F_}"><button type="button" aria-expanded="{H("cf_cts")}" onClick="{H("cf_cts_tog")}" style="{SEC}">Contestar fatura</button></sc-if>'
             f'<sc-if value="{H("cf_fpag")}" hint-placeholder-val="{F_}"><button type="button" onClick="{H("cf_pagar")}" style="{PRI}">Confirmar pagamento (simulado)</button></sc-if></div>')
    E.EXTRA.append(painel('cf_fp', corpo_f, rod_f, 500))
    # painel do plano ou área
    corpo_p = (titulo('Plano') + f'<div role="radiogroup" aria-label="Plano" style="display: flex; gap: 8px;"><sc-for list="{H("cf_ppl")}" as="pp" hint-placeholder-count="2">'
               f'<button type="button" role="radio" class="assin-esc" aria-checked="{H("pp.on")}" onClick="{H("pp.go")}">{H("pp.t")}</button></sc-for></div>'
               + f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="cf_pha" style="font-size: 12px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">Área contratada</label>'
               + f'<div style="display: flex; align-items: center; gap: 8px;"><input id="cf_pha" type="text" inputMode="decimal" value="{H("cf_pha")}" onChange="{H("cf_setha")}" style="{H("cf_pha_st")}"><span style="font-size: 13px; color: {MUTED};">ha</span></div>'
               + f'<span style="font-size: 11.5px; color: {MUTED};">{H("cf_pha_aj")}</span>'
               + f'<sc-if value="{H("cf_tplerr")}" hint-placeholder-val="{F_}"><span role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("cf_pl_err")}</span></sc-if></div>'
               + f'<div style="font-size: 13px; font-weight: 600;">{H("cf_pini")}</div>'
               + titulo('Prévia · hoje → depois')
               + f'<div><sc-for list="{H("cf_pv")}" as="pv" hint-placeholder-count="6"><div class="assin-pv"><span style="color: {MUTED}; font-size: 12px; font-weight: 700;">{H("pv.t")}</span>'
               + f'<span><sc-if value="{H("pv.tema")}" hint-placeholder-val="{T_}"><span>{H("pv.a")} → </span></sc-if><b>{H("pv.b")}</b></span></div></sc-for></div>'
               + f'<sc-if value="{H("cf_tag")}" hint-placeholder-val="{F_}"><div role="note" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 12px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700;">'
               + f'<span>{H("cf_ag_t")}</span><div><button type="button" onClick="{H("cf_desfazer")}" style="{SEC}">Desfazer mudança</button></div></div></sc-if>')
    rod_p = (f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 10px; border-top: 1px solid {LINE};">'
             f'<sc-if value="{H("cf_pl_pode")}" hint-placeholder-val="{T_}"><button type="button" onClick="{H("cf_aceitar")}" style="{PRI}">{H("cf_pl_ok")}</button></sc-if></div>')
    E.EXTRA.append(painel('cf_pp', corpo_p, rod_p, 500))
    pessoas = sum(1 for p in DC.PESSOAS if p.get('login'))
    EXTRAJS[0] = (cenario.js_prefixo() + DA.js_cad0() + f'const CF_PESSOAS = {pessoas};\nconst CF_POR = {json.dumps(PERFIL_CF, ensure_ascii=False)};\n'
                  + JS_COMUM + CF_JS)
    HEIGHTS37[fname] = 1700
    shell37('CF-05', 'Assinatura e cobrança', corpo, fname=fname, search=False, perfil=PERFIL_CF,
            subtitle='Cobrança simulada · nenhum valor é cobrado. Plano, uso medido no cadastro, faturas e mudança de plano ou área com prévia.',
            primary_html=E.acao_motivo(f'<button type="button" class="assin-prim" aria-disabled="{H("cf_prim_dis")}" data-dica="{H("cf_prim_tit")}" title="{H("cf_prim_tit")}" onClick="{H("cf_prim_fn")}" style="{BTN_ST(True)}">{H("cf_prim_t")}</button>', H("cf_prim_dis"), H("cf_prim_tit")),   # DS-06/VIS-04: motivo visível junto do botão
            footer='Preços, trial e régua são exemplos a decidir pelo proprietário (DEC-01/05/09). Inadimplência nunca apaga dado.')
    injeta(fname, 'Assinatura e cobrança', chip_dyn('cf_st'))
