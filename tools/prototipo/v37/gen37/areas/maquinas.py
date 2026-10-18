# -*- coding: utf-8 -*-
"""Manutenção num só lugar (PCM simplificado v2, docs/pcm-simplificado/ESPECIFICACAO.md) — MA.dc.html.

Pedido do proprietário (05/10/2026): "PCM /manutenção também tem telas e menus demais. simplifique, integre em algo mais prático e
intuitivo, sem perde funcionalidade importante. Elimina qualquer coisa ambigua, repetitiva, e faça o melhor num só."
- 1 item de menu ("Manutenção") → 1 tela MA com 4 visões: Sem ordem (planejamento) · Ordens (execução e apontamento; Em conferência e
  Encerradas são controle) · Ativos (controle) · Planos (planejamento, uso raro). Ativo (#ativo=) e plano (#plano=) são páginas de detalhe;
  OM, achado, vencimento, condição, leitura e os formulários são painéis laterais (§2, D-14).
- Um detalhe por coisa: o painel da OM é o único detalhe da ordem (o MA-04det saiu, S2); a mesma regra serve o app (MB-09det, S4).
- Um comando por efeito: "Mover janela" (D-38), painel Condição + "Declarar apto" (D-10), uma função de leitura (D-40), "Encerrar ordem" com
  regra única (D-34). Os dados e as regras ficam em dados_manutencao.py (estado único; desde o 1a, dentro do cenário).
- Ver como (simulação) Otávio · Zé · Ana pelo perfil de demonstração (g2lib G2_PERFIS, frente D do CTL-3): define a abertura e o "por" de
  todo comando; a matriz papel × comando habilita ou desabilita com o motivo (D-33).
- Endereços: #vis= (&tipo=, &modo=), #om=, #achado=, #venc=, #ativo=, #plano=, #leitura=, #novo=plano:<ativo>; F5 reabre; abrir não grava.
  PM, MA-01..05 e MA-04det viram páginas de redirecionamento fora do canvas e do Índice (D-24; build.REDIRECIONA).
Saíram (inventário F01–F111, §4): a faixa "Telas da manutenção", as 3 etapas do PM, "Marcar pendentes como feitas", KPIs e selos fixos,
Pareto, utilização, Agenda, Elegível, contingência fixa e os 3 "Restaurar demonstração" (agora 1×, no menu ⋯).
"""
import json, os, re
from engine import (grid,esc,icon,BTN_ST,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,DISP,EXTRA,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, HEIGHTS37
import ui37
import dados_manutencao as DM

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
T=lambda: H('true')
def IF(cond,html,dflt=False): return f'<sc-if value="{H(cond)}" hint-placeholder-val="{T() if dflt else F()}">{html}</sc-if>'
def FOR(lst,as_,html,n=2): return f'<sc-for list="{H(lst)}" as="{as_}" hint-placeholder-count="{n}">{html}</sc-for>'

FNAME='MA.dc.html'
# endereços antigos → novos (§3.1; D-24): a página antiga só redireciona (F5, favoritos e links antigos não quebram)
REDIRECIONA={'PM.dc.html':'vis=planos','MA-01.dc.html':'vis=ativos','MA-02.dc.html':'vis=semordem&tipo=achados','MA-03.dc.html':'vis=semordem',
             'MA-04.dc.html':'vis=ordens','MA-05.dc.html':'vis=ativos&modo=abastecimentos','MA-04det.dc.html':'om=OM-0233'}
PRIM=BTN_ST(True,True); SEC=BTN_ST(False,True)
LBL=f'font-size: 12px; font-weight: 600; color: {MUTED};'
SECT=f'font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;'
ERRS=f'font-size: 12px; font-weight: 700; color: {RED};'
LNK=f'border: 0; background: transparent; padding: 4px 2px; font-family: inherit; font-size: 12.5px; font-weight: 700; color: {ACC}; text-decoration: underline; text-underline-offset: 3px; cursor: pointer;'
INP=f'font-family: inherit; font-size: 13.5px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; box-sizing: border-box; background: #fff; color: {INK};'

CSS=('.ma-vis-m{display:none}'
     '.ma-vc-s{display:none}'
     # 390 px (AC-PCM-22): cartões numa faixa que rola de lado, filtros numa linha, "Ver como" curto e botões do cabeçalho menores: ≥ 5 linhas da grade acima da dobra
     '@media (max-width:640px){.ma-vis{display:none!important}.ma-vis-m{display:flex!important}'
     '.ma-cards{display:flex!important;flex-wrap:nowrap!important;overflow-x:auto;gap:8px!important;order:9}.ma-cards .ma-card{flex:0 0 auto!important;min-width:132px;padding:6px 10px!important}.ma-sem{order:9}'
     '.ma-top{gap:6px!important}.ma-top button{padding:4px 9px!important;font-size:12px!important}.ma-top .ma-lbl{font-size:0!important;gap:0!important}'
     '.g2caixa div[role=group]{flex-wrap:nowrap!important;overflow-x:auto}.g2caixa div[role=group]>button{flex:0 0 auto}.g2rola [role=row][data-rid]>[role=cell]{padding-top:6px!important;padding-bottom:6px!important}'
     # DS-MAN (17/10/2026): no celular cada lista da Manutenção mostra só a 1ª linha da célula (identidade e selo); a 2ª linha (subtítulo) fica no
     # detalhe. Antes só Ativos, e escondendo tudo depois da 1ª parte: com o ⚠ da situação na frente, o nome do ativo sumia
     '.ma-blo [role=row][data-rid]>[role=cell] .g2pw>[style*="flex-basis: 100%"]~*{display:none!important}.ma-blo [role=row][data-rid]>[role=cell]{min-height:46px;box-sizing:border-box}'
     # MA-VINCULO: no celular a ação do "Sem plano" fica à vista na célula Plano (o resto da célula continua no detalhe), com 44 px de alvo
     '.ma-gat [role=row][data-rid]>[role=cell] .g2pw>a[href*="vincular="],.ma-gat [role=row][data-rid]>[role=cell] .g2pw>a[href*="novo=plano"]{display:inline-flex!important;align-items:center;min-height:44px}'   # no celular a linha do ativo mostra o essencial de cada coluna; o resto fica no detalhe
     '.ma-cards .ma-card>span:last-child{display:none}.ma-cards .ma-card>span:nth-child(2){font-size:18px!important}'
     '.ma-flt{flex-wrap:nowrap!important;overflow-x:auto;padding-bottom:2px}.ma-flt>*{flex:0 0 auto}'
     # faixa Filtros (MAN-LIMPA-01) no celular: uma linha que rola de lado, com o título de cada filtro (proprietário, 14/10: "precisa manter o
     # título de cada filtro para o usuário não se perder"), para a lista começar acima da dobra (AC-PCM-22)
     '.ma-fx .mf-tela{flex-wrap:nowrap!important;overflow-x:auto;padding:6px 10px!important;gap:8px!important}.ma-fx .mf-tela>label{flex:0 0 auto}'
     # DS-MAN (17/10/2026): o bloco da lista no celular sem o título (a visão já está no título da tela e na lista Visão); a linha fica só com a escolha Ativos | Abastecimentos
     '.ma-blo>div:first-child h3{display:none!important}.ma-blo>div:first-child:not(:has(button)){display:none!important}.ma-blo>div:first-child{padding:10px 8px 0!important}.ma-blo>div:last-child{padding:10px 8px 8px!important}'
     # e a barra da lista numa linha que rola de lado (busca, filtros rápidos, Pendência, Ativos | Abastecimentos, Colunas), como a faixa Filtros
     '.ma-blo .g2caixa>div:first-child{flex-wrap:nowrap!important;overflow-x:auto}.ma-blo .g2caixa>div:first-child>*{flex:0 0 auto}'
     '.ma-vc-l{display:none}.ma-vc-s{display:inline}.ma-hb{padding:7px 12px!important;font-size:13px!important}'
     '.ma-pan{width:100%!important;max-width:100%!important;left:0!important}.ma-hide-m{display:none!important}.ma-flt{flex-wrap:wrap}'
     # peças da OM no celular: a situação (chip) desce para a linha de baixo, inteira; sem chip por cima da coluna Aplicado
     '.ma-pcs{grid-template-columns:minmax(0,1fr) 64px 76px!important}.ma-pcs-h>:nth-child(3){display:none}.ma-pcs-l>:nth-child(3){grid-column:1 / -1;grid-row:2;justify-self:start}}'
     '.ma-pan{position:fixed;top:0;right:0;bottom:0;z-index:60;width:620px;max-width:100%;background:#fff;box-shadow:-12px 0 40px -12px rgba(21,32,26,.35);'
     'display:flex;flex-direction:column;box-sizing:border-box;outline:none}'
     '.ma-pan-c{flex:1 1 0!important;overflow-y:auto;padding:18px 22px;display:flex;flex-direction:column;gap:12px;min-height:0!important}'   # a primária do rodapé fica à vista (AC-PCM-22)
     '.ma-pan-f{flex:0 0 auto;display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 22px 14px;border-top:1px solid #E4E9E5;background:#fff}'
     '@media (min-width:1024px){[data-root]:has(.ma-pan.ma-nm) main[data-scroll]{padding-right:652px}}'
     '.ma-bl{border:1px solid #E4E9E5;border-radius:12px;background:#fff}.ma-bl>button.ma-blh{display:flex;align-items:center;gap:8px;width:100%;border:0;background:transparent;'
     'padding:9px 12px;font-family:inherit;font-size:13px;font-weight:800;color:#15201A;cursor:pointer;text-align:left}.ma-bl-c{padding:2px 12px 12px;display:flex;flex-direction:column;gap:8px}'
     '.ma-sr{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}'
     '.ma-card{flex:1 1 0;min-width:0;padding:10px 14px;border:1px solid #E4E9E5;border-radius:12px;background:#fff;text-align:left;font-family:inherit;color:#15201A;display:flex;flex-direction:column;gap:2px}'
     'button.ma-card{cursor:pointer}button.ma-card[aria-pressed=true]{border-color:#1E7A4C;box-shadow:inset 0 0 0 1px #1E7A4C;background:#F2F8F4}')

# =====================================================================================
# JS da tela: endereço, Ver como, visões, grades, detalhes e painéis. Regras e cálculos vêm de dados_manutencao.JS (fonte única).
MA_JS=r'''
const MA_PERFIS=['Otávio','Zé','João','Ana'];   /* João (eletricista NR-10) executa as OMs de eletricista (revisão 09/10, A8) */
const MA_CH={green:['#1E7A4C','#E4F3E9'],yellow:['#8A5A00','#FFF3D6'],red:['#B42318','#FDE8E6'],gray:['#5B6660','#EEF1EE']};
const MA_PRIM=__PRIM__, MA_SEC=__SEC__;
const MA_ETC={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray'};
const MA_VIS=[{k:'semordem',t:'Sem ordem'},{k:'ordens',t:'Ordens'},{k:'ativos',t:'Ativos'},{k:'planos',t:'Planos'}];
const MA_VISTIT=__VISTIT__;   /* DS-MAN (17/10/2026): título de cada visão no cabeçalho = o nome do item do menu (ui37.MENU2, fonte única) */
const MA_NAVST=__NAVST__;   /* menu Manutenção (13/10): estilo do subitem [inativo, ativo]; o destaque segue a visão aberta */
/* DS-MAN: filtro rápido dentro do bloco com a contagem num selo, o mesmo desenho dos chips de fase da O.S. (referência do Agrícola) */
function ma_chipF(on){ return 'display:inline-block;font-family:inherit;font-size:12.5px;font-weight:700;padding:6px 12px;border-radius:999px;cursor:pointer;white-space:nowrap;'+(on?'border:1px solid #1E7A4C;background:#E4F3E9;color:#1E6B47;':'border:1px solid #E4E9E5;background:#FFFFFF;color:#15201A;'); }
function ma_nst(on){ return 'display:inline-block;margin-left:2px;font-size:11.5px;font-weight:800;padding:0 7px;border-radius:999px;'+(on?'background:rgba(255,255,255,.65);color:inherit;':'background:#EEF1EE;color:#15201A;'); }
/* TAB-14 (DS-MAN): selo curto na célula; o texto longo vai para a dica do selo (e para o leitor de tela, g2sr) */
function ma_chd(t,c,d){ const x=ma_ch(t,c); if(d&&d!==t) x.dica=d; return x; }
function ma_G(id){ return GRIDS.find(g=>g.id===id); }
function ma_chipSt(c){ const k=MA_CH[c]||MA_CH.gray; return 'display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+k[0]+';background:'+k[1]+';'; }
function ma_dotSt(c){ const k=MA_CH[c]||MA_CH.gray; return 'width:6px;height:6px;border-radius:999px;flex-shrink:0;background:'+k[0]+';'; }
function ma_pill(on){ return 'font-family:inherit;font-size:12.5px;font-weight:700;padding:5px 11px;border-radius:999px;cursor:pointer;white-space:nowrap;'+(on?'border:1px solid #1E7A4C;background:#E4F3E9;color:#1E6B47;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;'); }
function ma_ch(t,c){ return {k:'chip',t:t,c:c}; }
function ma_cond(a){ return a.cond==='Apto'?'green':(a.cond==='Bloqueado'?'red':'yellow'); }
function ma_condTxt(c,a){ const i=a.condInfo||{}; if(a.cond==='Bloqueado') return 'Bloqueado · desde '+manBr(i.desde); if(a.cond==='Restrito') return 'Restrito'+(i.ate?' · até '+manBr(i.ate):''); return 'Apto'; }
/* ---------- endereço (F5 reabre; abrir não grava) ---------- */
function ma_hashLer(){ const o={}; String(decodeURIComponent((location.hash||'').slice(1))).split('&').forEach(p=>{ const i=p.indexOf('='); if(i>0) o[p.slice(0,i)]=p.slice(i+1); }); return o; }
function ma_hashDe(st){ const p=[]; const pg=st.pg, pan=st.pan;
  if(!pg&&st.vis) p.push('vis='+st.vis); if(!pg&&st.vis==='semordem'&&st.tipo) p.push('tipo='+st.tipo);
  if(!pg&&st.vis==='ativos'&&st.amodo==='abast') p.push('modo=abastecimentos'); if(!pg&&st.vis==='ativos'&&st.amodo!=='abast'&&st.fpend==='Sem plano') p.push('pend=semplano'); if(!pg&&st.vis==='ordens'&&(st.omodo==='kanban'||st.omodo==='cartoes')) p.push('modo='+st.omodo);
  if(pg) p.push(pg.k+'='+pg.id); if(pan&&['om','achado','venc','leitura'].indexOf(pan.k)>=0&&pan.id) p.push(pan.k+'='+pan.id);
  if(st.np&&st.np.novoDe) p.push('novo=plano:'+st.np.novoDe); return p.join('&'); }
function ma_hashSync(st){ try{ const h=ma_hashDe(st); if(decodeURIComponent((location.hash||'').slice(1))!==h) history.replaceState(null,'',location.pathname+location.search+(h?'#'+h:'')); }catch(e){} }
/* abertura pelo perfil (§2): Otávio em Sem ordem quando há o que virar ordem; Zé em Ordens "Aguardam você"; Ana em Ativos */
function ma_abertura(c,pf){ const pa=manPapelDe(pf);
  if(pa==='mecanico') return {vis:'ordens',rot:'voce'};
  if(pa==='gestor') return {vis:'ativos',rot:''};
  if(pa==='pcm'){ const crit=Object.values(c.achados).some(q=>q.estado==='Sem ordem'&&(q.crit==='Alta'||q.sug==='Bloqueado')); return {vis:(manSemOm(c).length||crit)?'semordem':'ordens',rot:''}; }
  return {vis:'ordens',rot:''}; }
function ma_aplicaHash(self,h){ const c=manGet(); const s={pan:null,pg:null,rec:null};
  const ab=ma_abertura(c,g2perfil()); s.vis=h.vis||((h.om)?'ordens':(h.achado||h.venc?'semordem':ab.vis)); s.rot=(!h.vis&&!h.om&&s.vis==='ordens')?ab.rot:'';
  if(h.tipo) s.tipo=h.tipo==='achados'?'achados':(h.tipo==='vencimentos'?'venc':''); if(h.modo==='abastecimentos'){ s.vis='ativos'; s.amodo='abast'; }
  if(h.pend==='semplano'){ s.vis='ativos'; s.amodo='ativos'; s.fpend='Sem plano'; }   /* MA-VINCULO: "N ativos sem plano" da entrada do módulo e do CD-03 */ if(h.modo==='kanban'||h.modo==='cartoes') s.omodo=h.modo;
  if(h.ativo&&c.ativos[h.ativo]) s.pg={k:'ativo',id:h.ativo}; if(h.plano&&c.planos[h.plano]) s.pg={k:'plano',id:h.plano};
  if(h.om&&c.oms[h.om]) s.pan={k:'om',id:h.om,modal:true}; else if(h.achado&&c.achados[h.achado]) s.pan={k:'achado',id:h.achado,modal:true};
  else if(h.venc) s.pan={k:'venc',id:h.venc,modal:true}; else if(h.leitura) s.pan={k:'leitura',id:h.leitura,modal:true};
  self.setState(s); if(h.novo&&h.novo.indexOf('plano:')===0&&c.ativos[h.novo.slice(6)]) setTimeout(()=>pmNovo(self,manGet(),h.novo.slice(6)),0);
  if(h.vincular&&c.ativos[h.vincular]) setTimeout(()=>vlAbrir(self,{aids:[h.vincular]}),0);   /* "Vincular ao PM-xx ›" da linha do ativo: o painel já com a sugestão */
  if(!s.pan&&!s.pg&&s.vis==='ordens') setTimeout(()=>ma_autoAbre(self),0); }
/* a ≥1024 px a visão Ordens abre, sem modal, o painel da 1ª OM que espera o papel (abrir não executa) */
function ma_espera(c,o,pf){ const k=manPf(pf).k, pa=manPapelDe(pf); if(!manAberta(o)) return false;
  if(o.executante&&o.executante===k&&(o.etapa==='Liberadas'||o.etapa==='Em execução')) return true;
  if(pa==='pcm'&&(o.etapa==='A liberar'||o.etapa==='Em conferência')) return true;
  if(o.etapa==='Em conferência'&&o.trata&&!o.aptidao&&!manPode(c,pf,'condicao',{aid:o.aid})) return true; return false; }
function ma_ordFila(c){ return Object.values(c.oms).filter(o=>manAberta(o)).sort((a,b)=>(a.janIso||'9').localeCompare(b.janIso||'9')||({'Alta':0,'Média':1,'Baixa':2}[a.crit]-{'Alta':0,'Média':1,'Baixa':2}[b.crit])||a.id.localeCompare(b.id)); }
function ma_autoAbre(self){ try{ if(!window.matchMedia('(min-width: 1024px)').matches) return; }catch(e){ return; } const st=self.state; if(st.pan||st.pg||st.vis!=='ordens') return;
  const c=manGet(); const o=ma_ordFila(c).find(x=>ma_espera(c,x,g2perfil())); if(o) self.setState({pan:{k:'om',id:o.id,modal:false},rec:null,anun:'Painel da '+o.id+' aberto ao lado.'}); }
function ma_vis(self,k){ self.setState({vis:k,pg:null,pan:null,rec:null,card:'',fase:'',rot:'',anun:'',ftipo:(k==='ordens'&&self.state.ftipo==='Inspeção')?'':self.state.ftipo}); if(k==='ordens') setTimeout(()=>ma_autoAbre(self),0); }
function ma_abrir(self,k,id,extra){ const r=document.activeElement; if(!self.state.pan) self.__panRet=(r&&r!==document.body&&!(r.closest&&r.closest('#ma-painel')))?r:null;
  self.setState(Object.assign({pan:{k,id,modal:true},rec:null,pf:{},pchave:manChave(),paviso:null},extra||{})); setTimeout(()=>{ const e=document.getElementById('ma-painel'); if(e) e.focus(); },0); }
function ma_fechar(self){ self.setState({pan:null,rec:null,paviso:null,pf:{},anun:''}); setTimeout(()=>{ const r=self.__panRet; self.__panRet=null; if(r&&document.contains(r)) r.focus(); },0); }
function ma_pg(self,k,id){ self.setState({pg:{k,id},pan:null,rec:null,blk:{},anun:''}); try{ const m=document.querySelector('main[data-scroll]'); if(m) m.scrollTop=0; }catch(e){} }
function ma_volta(self){ const k=self.state.pg&&self.state.pg.k; self.setState({pg:null,pan:null,rec:null,vis:k==='plano'?'planos':'ativos'});
  setTimeout(()=>{ try{ const g=self.__lastRow; if(g){ const r=document.querySelector('[data-rid="'+g+'"]'); if(r){ r.scrollIntoView({block:'center'}); r.focus(); } } }catch(e){} },60); }
/* comando: aplica, guarda o comprovante no painel e a "Próxima" (só navega); a chave do registro é renovada depois de cada comando gravado */
/* A11 (revisão 09/10): o painel da OM guarda o o.rv lido ao abrir; todo comando dele confere a versão (manRv) antes de gravar. Mudou em outra aba ou
   no app → "Mudou desde que você abriu…" e nada grava; o painel já mostra o estado novo e a referência é renovada (o próximo toque confirma). */
function ma_mud(self,fn){ const pan=self.state.pan; const ref=(pan&&pan.k==='om'&&self.__rv&&self.__rv.id===pan.id)?self.__rv:null;
  const r=manMudar(self,ref?((m,cc)=>{ const o=m.oms[ref.id]; if(o) manRv(o,ref.rv); return fn(m,cc); }):fn);
  if(ref){ const o=manGet().oms[ref.id]; if(o) self.__rv={id:ref.id,rv:o.rv||0}; } return r; }
function ma_cmd(self,fn,depois){ const r=ma_mud(self,fn); if(!r.erro&&!r.nada) self.setState({pchave:manChave()}); if(!r.erro&&!r.aviso&&!r.avisoTol&&!r.avisoConf&&!r.avisoLeit&&!r.rep&&depois) depois(r); return r; }
function ma_rec(self,r,prox){ if(r&&!r.erro&&r.msg) self.setState({rec:{msg:r.msg,prox:prox||null},paviso:null}); }
/* "Próxima": no lote recém-gerado, a próxima dele ainda a liberar (Abrir as 3 › …); fora do lote, a próxima ordem que espera o papel */
function ma_proxOm(c,pf,id,lote){ if(lote&&lote.indexOf(id)>=0){ const n=lote.find(x=>x!==id&&c.oms[x]&&c.oms[x].etapa==='A liberar'); if(n) return {t:'Próxima: '+n+' ›',k:'om',id:n}; }
  const o=ma_ordFila(c).find(x=>x.id!==id&&ma_espera(c,x,pf)); return o?{t:'Próxima: '+o.id+' ›',k:'om',id:o.id}:null; }
/* ---------- linhas das grades (a linha identifica, o painel resolve: nenhum botão de comando na linha; o ID é link) ---------- */
function ma_selosAtv(c,a){ const s=[]; if(a.cond==='Bloqueado') s.push(ma_ch('Ativo bloqueado','red')); if(a.suspeita) s.push(ma_ch('Leitura a confirmar','yellow'));
  else if(manAntiga(c,a)) s.push(ma_ch('Leitura de '+manBr(a.leit.data),'yellow'));
  Object.keys(c.prop||{}).forEach(k=>{ const pp=c.prop[k]; if(pp.sub===a.id) s.push(ma_chd('Substituto proposto','yellow','Substituto proposto · '+pp.os.join(' e ')+' · aguarda PCP')); }); return s; }
function ma_pecasTxt(c,s){ const fs=(s.pecas||[]).filter(x=>{ const it=c.itens[x.item]; return it&&(it.saldo-it.reservado)<x.qtd; });
  if(!(s.pecas||[]).length) return {t:'—',c:''}; if(!fs.length) return {t:'Com saldo',c:''}; const x=fs[0], it=c.itens[x.item]; return {t:'Falta '+manN(x.qtd-Math.max(0,it.saldo-it.reservado),1)+' '+it.un+' · '+it.nome,c:'red'}; }
function ma_linhasSemOrdem(self,c,st){ const rows=[]; const hz=st.prazo==='venc'?-1e9:(st.prazo==='30'?30:c.horiz);
  const SO=manSemOrdem(c,st.prazo==='venc'?-1e9:hz);   /* a mesma lista do Painel de Manutenção (fonte única) */
  if(st.tipo!=='achados') SO.venc.forEach(l=>{ const ini=manIniJanela(l.x); const venc=l.x.sit==='Vencida';
    if(st.fgrupo&&l.a.grupo!==st.fgrupo) return; if(st.fplano&&l.pid!==st.fplano) return; if(st.fcrit) return;
    const pc=ma_pecasTxt(c,l.s); const prz=venc?manSitTxt(c,l.x):(l.x.sit==='Vence em breve'?'Em breve · janela abre '+(ini<=0?'hoje':'em '+Math.ceil(ini)+' d'):'Em dia · janela abre em '+Math.ceil(ini)+' d');
    const a=l.a; const k=l.vk+'#'+l.sid; const vid=l.pid+'|'+l.aid+'|'+l.sid;
    rows.push({id:'v:'+vid,k:'venc',tp:'Preventiva',key:k,venc:venc,devida:manDevida(l),v:{prazo:(venc?1000:2000)+ini,item:l.pid},s:{item:l.pid+' v'+l.p.versao+' vencimento',ativo:a.nome,oque:l.s.nome,prazo:prz,pecas:pc.t,prox:manDevida(l)?'Gerar ordem preventiva':'Aguardar a janela'},
      p:{item:[{k:'link',t:l.pid+' v'+l.p.versao,h:'#venc='+vid},{k:'mut',t:'· vencimento'}],ativo:[{k:'b',t:a.nome},{k:'br',t:''},{k:'mut',t:manLeitTxt(a)}].concat(ma_selosAtv(c,a)).concat(l.est?[ma_ch('Marco estimado','yellow')]:[]),
         oque:[{k:'txt',t:l.s.nome},{k:'br',t:''},{k:'mut',t:manGatTxt(l.s)}],prazo:[ma_chd(venc?'Vencida':(l.x.sit==='Vence em breve'?'Em breve':'Em dia'),venc?'red':(l.x.sit==='Vence em breve'?'yellow':'gray'),prz)],
         pecas:pc.c?[ma_chd('Falta peça','red',pc.t)]:[{k:'mut',t:pc.t}],
         prox:[{k:'txt',t:manDevida(l)?'Gerar ordem preventiva':'Aguardar a janela'}]}}); });
  if(st.tipo!=='venc') SO.ach.forEach(q=>{ const a=c.ativos[q.aid];
    if(st.fgrupo&&a.grupo!==st.fgrupo) return; if(st.fplano) return; if(st.fcrit&&q.crit!==st.fcrit) return;
    const op=manAchOpcoes(c,q.id); const grave=q.crit==='Alta'||q.sug==='Bloqueado'; const prz=q.voltou?('Voltou da '+q.voltou):(q.crit+' · desde '+manBr(q.oc[0]||q.em));
    rows.push({id:'a:'+q.id,k:'achado',tp:q.origem==='Inspeção'?'Inspeção':'Corretiva',crit:grave,v:{prazo:(grave?0:3000)+manDias(q.em,c.hoje)*-1,item:q.id},s:{item:q.id+' '+q.origem,ativo:a.nome,oque:q.comp+' '+q.sint,prazo:prz,pecas:'—',prox:op.prim?op.prim.t:''},
      p:{item:[{k:'link',t:q.id,h:'#achado='+q.id},{k:'mut',t:'· '+q.origem.toLowerCase()}].concat(q.nova?[{k:'br',t:''},ma_ch('Nova','yellow')]:[]),ativo:[{k:'b',t:a.nome},{k:'br',t:''},{k:'mut',t:manLeitTxt(a)}].concat(ma_selosAtv(c,a)),
         oque:[{k:'txt',t:q.comp},{k:'br',t:''},{k:'mut',t:q.sint+(q.oc.length>1?' · '+q.oc.length+' ocorrências':'')}],prazo:[ma_chd(q.voltou?('Voltou da '+q.voltou):q.crit,q.voltou?'yellow':(grave?'red':(q.crit==='Média'?'yellow':'gray')),prz)],pecas:[{k:'mut',t:'—'}],
         prox:[{k:'txt',t:op.prim?op.prim.t:'—'}].concat(q.sug!=='Apto'?[{k:'br',t:''},ma_ch('Sugere '+q.sug,q.sug==='Bloqueado'?'red':'yellow')]:[])}}); });
  rows.sort((x,y)=>x.v.prazo-y.v.prazo); return rows; }
function ma_pendTxt(c,o){ const s=manSelos(c,o); if(!s.length) return null; const p=s[0]; return {t:p.t+(p.dono?' · '+p.dono:'')+(p.prazo?' · '+p.prazo:''),c:p.c,n:s.length-1,
  curto:ma_pendCurto(p.t),todos:s.map(x=>ma_pendCurto(x.t)),dica:s.map(x=>x.t+(x.dono?' · '+x.dono:'')+(x.prazo?' · '+x.prazo:'')).join(' | ')}; }
/* DS-MAN (TAB-14): o nome curto da pendência ("Conflito · OS-0420 28/09" → "Conflito"; "Compra SC-12 (simulado)" → "Compra (simulado)") */
function ma_pendCurto(t){ t=String(t||''); if(/^Compra /.test(t)) return 'Compra (simulado)'; return t.split(' · ')[0]; }
/* MAN-LIMPA-01: Tipo, Criticidade e Grupo da faixa Filtros nas ordens (as contagens dos chips de fase usam o mesmo recorte) */
function ma_omFiltro(c,os,st){ return os.filter(o=>(!st.ftipo||o.tipo===st.ftipo)&&(!st.fcrit||o.crit===st.fcrit)&&(!st.fgrupo||(c.ativos[o.aid]||{}).grupo===st.fgrupo)); }
/* filtro "Com conflito" em Ordens (F25/F26): conflito com a produção calculado sobre AL e registro do app a resolver */
function ma_temConf(c,o){ return !!(((o.etapa==='A liberar'||o.etapa==='Liberadas')&&manConflito(c,o)&&!o.conflitoAceito)||o.conflitoApp); }
function ma_linhaOm(c,o){ const a=c.ativos[o.aid]; const p=ma_pendTxt(c,o); const fin=o.etapa==='Encerradas'; const custo=fin?manCustoFinal(c,o):manCusto(c,o,'est');
  const tt=o.tipo==='Preventiva'?(o.serv+' · Preventiva · '+o.pid+' v'+o.ver):(o.tipo==='Corretiva'?((o.comp?o.comp:'Corretiva')+' · '+o.crit):'Pendência · '+o.serv);
  const ex=manExecSug(o); const real=o.exec&&o.exec.horas!==undefined?(' · '+manN(o.exec.horas,1)+' h real'):'';
  return {id:o.id,m:{pend:p?[...new Set(p.todos)].map(x=>({id:x,l:x})):[]},v:{jan:o.janIso||'',custo,tempo:Number(o.tempo)||0,ord:(fin?'z'+String(9e13-manT(o.exec&&o.exec.data||o.janIso||'2000-01-01')).padStart(16,'0'):'a'+(o.janIso||'9')+({'Alta':0,'Média':1,'Baixa':2}[o.crit]||1))},
    s:{om:o.id+' '+(a?a.nome:''),serv:tt,fase:o.etapa,pend:p?p.t:'',exe:o.executante||(ex?ex+' (sugerido)':'—'),tempo:(Number(o.tempo)>0?manN(o.tempo,1)+' h prev.':'sem tempo')+real,custo:manRS(custo)+(fin?'':' est.'),jan:o.jan||''},
    p:{om:[{k:'link',t:o.id,h:'#om='+o.id},{k:'br',t:''},{k:'mut',t:a?a.nome:''}],serv:[{k:'txt',t:o.serv},{k:'br',t:''},{k:'mut',t:o.tipo==='Preventiva'?('Preventiva · '+o.pid+' v'+o.ver):(o.tipo+' · '+o.crit)}],
       jan:[{k:'txt',t:o.jan||'—'}],fase:[ma_ch(o.etapa,MA_ETC[o.etapa]||'gray')],pend:p?[ma_chd(p.curto,p.c,p.dica)].concat(p.n?[{k:'mut',t:'+'+p.n}]:[]):[{k:'mut',t:'—'}],
       exe:o.executante?[{k:'txt',t:o.executante}]:(ex?[{k:'mut',t:ex+' (sugerido)'}]:[ma_ch('Falta: executante','red')]),tempo:[{k:'txt',t:Number(o.tempo)>0?manN(o.tempo,1)+' h prev.':'sem tempo'}].concat(real?[{k:'br',t:''},{k:'mut',t:real.slice(3)}]:[]),
       custo:[{k:'txt',t:manRS(custo)+(fin?'':' est.')}]}}; }
function ma_prox(c,a){ const ls=manLinhas(c).filter(l=>l.aid===a.id&&l.s&&l.x.gats.length); const ord={'Vencida':0,'Vence em breve':1,'Em dia':2};
  ls.sort((x,y)=>(ord[x.x.sit]-ord[y.x.sit])||(manIniJanela(x.x)-manIniJanela(y.x))); if(!ls.length) return null; return {l:ls[0],n:ls.length-1}; }
function ma_linhaAtv(c,a,per){ const px=ma_prox(c,a); const abertas=Object.values(c.oms).filter(o=>o.aid===a.id&&manAberta(o)); const achs=Object.values(c.achados).filter(q=>q.aid===a.id&&q.estado==='Sem ordem');
  const cp=manCustoPeriodo(c,per,a.id); const cons=ma_consumo(c,a); const i=a.condInfo||{};
  const ab=abertas.map(o=>({k:'link',t:o.id+' · '+o.etapa,h:'#om='+o.id})).concat(achs.map(q=>({k:'link',t:q.id+' sem ordem',h:'#achado='+q.id})));
  /* TAB-14 (DS-MAN): até 2 linhas; o que passar de 2 fica no "+N" (a lista inteira no detalhe do ativo, bloco Ordens e Achados) */
  const abp=[]; ab.slice(0,2).forEach((x,j)=>{ if(j) abp.push({k:'br',t:''}); abp.push(x); }); if(ab.length>2) abp.push({k:'mut',t:'+'+(ab.length-2)});
  const pl=ma_plCel(c,a);
  const pend=[]; if(a.suspeita) pend.push('Leitura a confirmar'); if(pl.semp) pend.push('Sem plano'); if(achs.length) pend.push('Achado sem ordem');
  if(cons&&cons.desvio!==null&&Math.abs(cons.desvio)>=15) pend.push('Desvio de consumo'); if(px&&px.l.x.prev&&manDias(c.hoje,px.l.x.prev)<=30) pend.push('Vence em 30 d'); if(manRestricaoVencida(c,a)) pend.push('Restrição vencida');
  return {id:a.id,pend,semp:pl.semp,v:{custo:cp.enc,cond:{'Bloqueado':0,'Restrito':1,'Apto':2}[a.cond],prox:px?(px.l.x.prev?manT(px.l.x.prev)/864e5:9e9):9e9,leit:a.leit?a.leit.val:null},
    s:{ativo:a.nome+' '+a.modelo+' '+a.local+' '+a.grupo,plano:pl.s,cond:a.cond,leit:a.leit?manLeitTxt(a):'sem contador',prox:px?(px.l.s.nome+' '+px.l.x.sit):'—',ab:abertas.map(o=>o.id).join(' ')+' '+achs.map(q=>q.id).join(' '),cons:cons?cons.t:'— sem método',grupo:a.grupo},
    /* TAB-14 (DS-MAN, 17/10/2026): uma linha por registro, duas no máximo; o selo curto e o texto longo na dica (o modelo, o "desde", a data e o
       serviço seguinte ficam no detalhe do ativo e na busca) */
    p:{ativo:[{k:'link',t:a.nome,h:'#ativo='+a.id},{k:'br',t:''},{k:'mut',t:a.local}],plano:pl.p,cond:[ma_chd(a.cond,ma_cond(a),ma_condTxt(c,a)+(i.motivo?' · '+i.motivo:''))].concat(manRestricaoVencida(c,a)?[ma_ch('Restrição vencida','yellow')]:[]),
       leit:a.leit?[{k:'txt',t:manLeitTxt(a)}].concat(a.suspeita?[{k:'br',t:''},ma_chd('A confirmar','yellow',manQ(a.suspeita.val,a.un)+' a confirmar')]:(manAntiga(c,a)?[{k:'br',t:''},ma_chd('Antiga','yellow','Leitura de '+manBr(a.leit.data)+': mais de '+(c.antiga||7)+' dias')]:[])):[{k:'mut',t:'sem contador'}],
       prox:px?[ma_chd(px.l.x.sit==='Vence em breve'?'Em breve':px.l.x.sit,MAN_SITC[px.l.x.sit]||'gray',px.l.x.sit+': '+px.l.s.nome+' · '+manProxTxt(c,px.l.x)+(px.n?' · +'+px.n+(px.n>1?' serviços':' serviço'):'')),{k:'br',t:''},{k:'mut',t:px.l.s.nome+(px.n?' +'+px.n:'')}]:[{k:'mut',t:'—'}],   /* "Sem plano" fica na coluna Plano (MA-VINCULO) */
       ab:abp.length?abp:[{k:'mut',t:'—'}],cons:cons?[{k:'txt',t:manConsTxt({lh:cons.lh,un:cons.un})}].concat(cons.desvio!==null&&Math.abs(cons.desvio)>=15?[ma_ch((cons.desvio>0?'+':'')+manN(cons.desvio)+' %','yellow')]:[]):[{k:'mut',t:'— sem método'}]}}; }   /* o método (tanque cheio a tanque cheio) fica na dica do cabeçalho da coluna e no detalhe */
/* MA-VINCULO (16/10): coluna Plano da visão Ativos. Cada plano do ativo (nada colapsado) com a situação; sem plano, a sugestão explícita
   ("Vincular ao PM-xx ›" abre o painel com ela escolhida) ou "Criar plano ›". Links, não botões: a linha identifica, o painel resolve. */
function ma_plCel(c,a){ const pls=manPlanosDe(c,a.id); const semp=manAtvAtivo(a)&&!pls.some(manPlVale); const pp=[]; const st=[];
  if(!manAtvAtivo(a)) return {semp:false,s:'Ativo '+String(a.sit||'inativo').toLowerCase(),p:[{k:'mut',t:'Ativo '+String(a.sit||'inativo').toLowerCase()}]};
  pls.forEach((p,j)=>{ const si=manPlSit(c,p,a); if(j) pp.push({k:'br',t:''}); pp.push({k:'link',t:p.id,h:'#plano='+p.id}); pp.push(Object.assign(ma_ch(si.t,si.c),si.dica?{dica:si.dica}:{})); st.push(p.id+' · '+si.t); });
  if(semp){ const sg=manVincSug(c,a)[0]; if(pp.length) pp.push({k:'br',t:''}); pp.push(ma_ch('Sem plano','yellow')); pp.push({k:'br',t:''});
    pp.push(sg?{k:'link',t:'Vincular ao '+sg.p.id+' ›',h:'#vis=ativos&vincular='+a.id}:{k:'link',t:'Criar plano ›',h:'#vis=ativos&novo=plano:'+a.id}); st.unshift('Sem plano'); }
  return {semp,s:st.join('; '),p:pp}; }
/* consumo pelo último lançamento com método (tanque cheio a tanque cheio; PRD CAL-07); sem método, "—" */
function ma_consumo(c,a){ const bs=(c.abast||[]).filter(b=>b.aid===a.id&&!b.tipo&&b.qual!=='Estornado').sort((x,y)=>(y.data+(y.hora||'')).localeCompare(x.data+(x.hora||'')));
  for(const b of bs){ const lh=manLh(c,b); if(lh&&lh.lh!==null){ const dv=(a.lh&&lh.un==='L/h')?Math.round((lh.lh/a.lh-1)*100):null; return {t:manConsTxt(lh)+' · tanque cheio',lh:lh.lh,un:lh.un,desvio:dv,b:b.id}; } } return null; }
function ma_linhaAb(c,b){ const a=c.ativos[b.aid]||{nome:b.aid}; const lh=manLh(c,b); const qc={'Confirmada':'green','A confirmar':'yellow','Troca de contador':'green','Descartada':'gray','Estornado':'gray','Estorno':'gray','Substituída':'gray'}[b.qual]||'gray';
  return {id:b.id,v:{vol:b.vol,data:b.data+' '+(b.hora||''),lh:lh?Math.round(lh.lh*10)/10:null},s:{id:b.id+' '+b.op+' '+(b.evid||''),ativo:a.nome,tq:b.tq,data:manBr(b.data)+' '+(b.hora||''),met:b.tipo?'Estorno':(lh?'Tanque cheio':(b.cheio?'Tanque cheio (sem anterior)':'Estimada')),qual:b.qual},
    p:{id:[{k:'link',t:b.id,h:'#leitura='+b.id},{k:'br',t:''},{k:'mut',t:b.op+(b.evid?' · '+b.evid:' · sem evidência')}],ativo:[{k:'txt',t:a.nome}],tq:[{k:'txt',t:b.tq}],
       data:[{k:'txt',t:manBr(b.data)+' '+(b.hora||'')}].concat(b.leit!==null&&b.leit!==undefined?[{k:'br',t:''},{k:'mut',t:manQ(b.leit,b.un)}]:[]),met:[{k:'txt',t:b.tipo?('Estorno de '+b.ref):(lh?'Tanque cheio':(b.cheio?'Tanque cheio · sem anterior':'Estimada'))}],
       lh:lh?[{k:'txt',t:manConsTxt(lh)}]:[{k:'mut',t:'—'}],qual:[ma_ch(b.qual,qc)].concat(b.estorno?[{k:'mut',t:'· '+b.estorno}]:[])}}; }
function ma_linhaPl(c,p){ const e=pmEst(p); const nv=pmVincs(c,p.id).length; const cand=pmCands(c,p).length; const si=pmSit(c,p); const sem=manLinhas(c,p.id).filter(l=>l.s&&manDevida(l)&&!l.om&&!l.dup).length;
  return {id:p.id,v:{},s:{nome:p.id+' '+p.nome,est:e[0],apl:manAplTxt(c,p),svs:manWork(p).map(s=>s.nome).join(', '),atv:nv+' vinculados de '+(nv+cand),sit:si.t+(sem?' · '+sem+' sem ordem':''),grupo:p.grupo},
    p:{nome:[{k:'link',t:p.id,h:'#plano='+p.id},{k:'br',t:''},{k:'mut',t:p.nome}],grupo:[{k:'txt',t:p.grupo||'—'}],est:[ma_ch(e[0],e[1])],apl:[{k:'txt',t:manAplTxt(c,p)}],svs:[{k:'txt',t:manWork(p).map(s=>s.nome).join(' · ')||'—'}],
       atv:[{k:'txt',t:nv+(nv===1?' vinculado de ':' vinculados de ')+(nv+cand)}],
       /* TAB-14 (DS-MAN): o selo diz a pior situação; a contagem inteira ("1 vence em breve · 1 em dia") vai para a dica */
       sit:[ma_chd(/^Publique/.test(si.t)?'Não publicado':si.t.split(' · ')[0],si.c,si.t)].concat(sem?[{k:'br',t:''},{k:'link',t:sem+' sem ordem',h:'#vis=semordem&plano='+p.id}]:[])}}; }
/* ---------- Ver como (simulação) e menu ⋯ ---------- */
/* sem a faixa "Ver como" (proprietário, 14/10): o perfil de quem age é o do avatar do menu lateral (g2perfil), lido a cada desenho */
function ma_verComo(self,v){
  /* ⋯ Mais ações (engine.mais, componente único): abrir e fechar é do g2lib; restaurar pede confirmação logo abaixo do ⋯ */
  v.rst_ask=!!self.state.rst; v.rst=()=>self.setState({rst:true}); v.rst_cancel=()=>self.setState({rst:false});
  v.rst_ok=()=>{ manReset(self); self.setState({rst:false,pan:null,pg:null,rec:null,sv:null,np:null,vl:null,dv:null}); }; }
'''

# ---------- visões (listas), detalhe do ativo e painéis: preenchem os buracos da tela ----------
MA_JS+=r'''
function PREVALS(self,v){ manOuvir(self); const c=manGet(); const st=self.state; const pf=g2perfil();
  if(!self.__hashIni){ self.__hashIni=1; const h=ma_hashLer(); setTimeout(()=>ma_aplicaHash(self,h),0);
    try{ window.addEventListener('hashchange',()=>{ const h2=ma_hashLer(); if(ma_hashDe(self.state)!==decodeURIComponent((location.hash||'').slice(1))) ma_aplicaHash(self,h2); }); }catch(e){} 
    /* subitem do menu na própria tela: aplica a visão no clique, sem esperar o hashchange. Antes, com o painel da OM aberto ao lado,
       a sincronização estado → endereço podia regravar o # antigo entre o clique e o hashchange, e a troca de visão se perdia (v57) */
    try{ document.addEventListener('click',e=>{ const a=e.target&&e.target.closest?e.target.closest('a[href^="MA.dc.html#"]'):null;
      if(!a||e.defaultPrevented||e.button||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey) return; e.preventDefault();
      history.pushState(null,'',location.pathname+location.search+'#'+a.getAttribute('href').split('#')[1]); ma_aplicaHash(self,ma_hashLer()); }); }catch(e){} }
  const vis=st.vis||'semordem'; const per=st.per||'mes';
  /* Sem ordem */
  const so=ma_linhasSemOrdem(self,c,Object.assign({prazo:'10'},st,{tipo:''}));
  const soF=st.ftipo?so.filter(r=>r.tp===st.ftipo):so;
  ma_G('g_so').rows=soF; self.__so=soF;
  /* Ordens */
  const os=Object.values(c.oms).filter(o=>o.etapa!=='Canceladas');
  const fim=(o)=>o.etapa==='Encerradas'; const dom=manAdd(c.hoje,7-new Date(manT(c.hoje)).getUTCDay());
  const osB=ma_omFiltro(c,os,st); let oF=osB; if(st.fase) oF=oF.filter(o=>o.etapa===st.fase);
  if(st.rot==='voce') oF=oF.filter(o=>ma_espera(c,o,pf)); else if(st.rot==='semana') oF=oF.filter(o=>!fim(o)&&o.janIso&&o.janIso<=dom); else if(st.rot==='conf') oF=oF.filter(o=>ma_temConf(c,o));
  else if(st.rot==='peca') oF=oF.filter(o=>!fim(o)&&manFalta(c,o).length);
  const oR=oF.map(o=>ma_linhaOm(c,o)).sort((a,b)=>String(a.v.ord).localeCompare(String(b.v.ord)));
  ma_G('g_om').rows=oR; self.__om=oR;
  /* Ativos e abastecimentos */
  const at=c.ordem.map(id=>c.ativos[id]).filter(a=>a&&(!st.fgrupo||a.grupo===st.fgrupo)).map(a=>ma_linhaAtv(c,a,per)).filter(r=>!st.fpend||r.pend.indexOf(st.fpend)>=0)
    .sort((a,b)=>(a.v.cond-b.v.cond)||(a.v.prox-b.v.prox));
  ma_G('g_at').rows=at; self.__at=at; ma_G('g_ab').rows=(c.abast||[]).filter(b=>!st.fgrupo||(c.ativos[b.aid]||{}).grupo===st.fgrupo).sort((x,y)=>(y.data+(y.hora||'')).localeCompare(x.data+(x.hora||''))).map(b=>ma_linhaAb(c,b));   /* o Grupo vale também para os lançamentos, pelo ativo de cada um (MAN-LIMPA-GRUPO-01) */
  /* Planos */
  ma_G('g_pl').rows=pmPlans(c).filter(p=>!st.fgrupo||p.grupo===st.fgrupo).map(p=>ma_linhaPl(c,p));
  /* detalhe do ativo */
  const pg=st.pg; const A=pg&&pg.k==='ativo'?c.ativos[pg.id]:null;
  if(A){ const ls=manLinhas(c).filter(l=>l.aid===A.id);
    ma_G('d_venc').rows=ls.map(l=>{ const vid=l.pid+'|'+l.aid+'|'+(l.sid||''); return {id:vid,v:{prox:l.x.prev?manT(l.x.prev)/864e5:9e9},s:{serv:(l.s?l.s.nome:'—')+' '+l.pid,sit:l.x.sit,prox:l.s?manProxTxt(c,l.x):'—',om:l.om?l.om.id:''},
      p:{serv:[{k:'txt',t:l.s?l.s.nome:'—'},{k:'mut',t:'· '+l.pid+' v'+l.p.versao}],sit:[ma_ch(l.s?manSitTxt(c,l.x):l.x.sit,MAN_SITC[l.x.sit]||'gray')],prox:[{k:'txt',t:l.s?manProxTxt(c,l.x):'—'}],
         om:l.om?[{k:'link',t:l.om.id+' · '+l.om.etapa,h:'#om='+l.om.id}]:(l.dup?[{k:'link',t:l.dup.id+' (pelo '+l.dup.pid+')',h:'#om='+l.dup.id}]:[{k:'mut',t:manDevida(l)?'sem ordem':'—'}])}}; });
    ma_G('d_ach').rows=Object.values(c.achados).filter(q=>q.aid===A.id).sort((x,y)=>y.em.localeCompare(x.em)).map(q=>({id:q.id,v:{em:q.em},s:{id:q.id,comp:q.comp+' '+q.sint,crit:q.crit,est:q.estado==='Na OM'?'Na '+q.om:q.estado},
      p:{id:[{k:'link',t:q.id,h:'#achado='+q.id},{k:'mut',t:'· '+manBr(q.em)}],comp:[{k:'txt',t:q.comp+' · '+q.sint}],crit:[ma_ch(q.crit,q.crit==='Alta'?'red':(q.crit==='Média'?'yellow':'gray'))],
         est:[ma_ch(q.estado==='Na OM'?'Na '+q.om:q.estado,q.estado==='Sem ordem'?'yellow':(q.estado==='Resolvido'?'green':'gray'))].concat(q.voltou&&q.estado==='Sem ordem'?[{k:'mut',t:'voltou da '+q.voltou}]:[])}}));
    ma_G('d_om').rows=Object.values(c.oms).filter(o=>o.aid===A.id).map(o=>ma_linhaOm(c,o)).sort((a,b)=>String(a.v.ord).localeCompare(String(b.v.ord)));
    const lts=(c.leituras||[]).filter(x=>x.aid===A.id).map(x=>({id:x.id,v:{data:x.data,val:x.val},s:{data:manBr(x.data),val:manQ(x.val,x.un),orig:x.origem,qual:x.qual},
      p:{data:[{k:'link',t:manBr(x.data),h:'#leitura='+x.id}],val:[{k:'txt',t:manQ(x.val,x.un)}],orig:[{k:'txt',t:x.origem}].concat(x.por&&x.por!=='seed'?[{k:'mut',t:'· '+x.por}]:[]),qual:[ma_ch(x.qual,x.qual==='Confirmada'?'green':(x.qual==='A confirmar'?'yellow':'gray'))]}}));
    const abs=(c.abast||[]).filter(b=>b.aid===A.id&&(b.tipo||!b.lt)).map(b=>({id:b.id,v:{data:b.data,val:b.vol},s:{data:manBr(b.data),val:manN(b.vol)+' L',orig:b.id+' '+b.tq,qual:b.qual},
      p:{data:[{k:'link',t:manBr(b.data),h:'#leitura='+b.id}],val:[{k:'txt',t:manN(b.vol)+' L'}],orig:[{k:'txt',t:(b.tipo?'Estorno '+b.id+' de '+b.ref:b.id+' · '+b.tq)}],qual:[ma_ch(b.qual,'gray')]}}));
    ma_G('d_lei').rows=lts.concat(abs).sort((x,y)=>String(y.v.data).localeCompare(String(x.v.data))); }
  else { ['d_venc','d_ach','d_om','d_lei'].forEach(g=>{ ma_G(g).rows=[]; }); }
  const Pp=pg&&pg.k==='plano'?c.planos[pg.id]:null;
  ma_G('d_vinc').rows=Pp?pmVincs(c,Pp.id).map(k=>{ const aid=k.split('|')[1]; const a=c.ativos[aid]; const vv=c.vinc[k]; const ls=manLinhas(c,Pp.id).filter(l=>l.aid===aid&&l.s);
    const om=ls.map(x=>x.om).find(Boolean)||Object.values(c.oms).find(o=>o.pid===Pp.id&&o.aid===aid&&manAberta(o))||null; const si=manPlSit(c,Pp,a);
    const px=[]; ls.forEach((l,j)=>{ if(j) px.push({k:'br',t:''}); px.push({k:'txt',t:l.s.nome+' · '+manProxTxt(c,l.x)}); });
    return {id:k,ro:true,v:{},s:{ativo:a.nome,base:manVincDeTxt(a,vv.marco),prox:ls.map(l=>l.s.nome+' · '+manProxTxt(c,l.x)).join(' · ')||'—',sit:si.t,om:om?om.id:''},
      p:{ativo:[{k:'link',t:a.nome,h:'#ativo='+aid},{k:'mut',t:'· '+a.modelo}],base:[{k:'txt',t:manVincDeTxt(a,vv.marco)}].concat(vv.marco.est?[ma_ch('estimado','yellow')]:[]).concat(vv.marco.de?[{k:'mut',t:'da '+vv.marco.de}]:[]),
         prox:px.length?px:[{k:'mut',t:Pp.versao?'—':'vence quando o plano for publicado'}],sit:[Object.assign(ma_ch(si.t,si.c),si.dica?{dica:si.dica}:{})],
         om:(om?[{k:'link',t:om.id+' · '+om.etapa,h:'#om='+om.id}]:[{k:'mut',t:'—'}]).concat([{k:'act',t:'Desvincular',fn:'pl_desv:'+k}])}}; }):[]; }
'''

MA_JS+=r'''
function EXTRAVALS(self,v){ const c=manGet(); const st=self.state; const pf=g2perfil(); const vis=st.vis||'semordem';
  ma_verComo(self,v); ma_hashSync(st);
  MA_VIS.forEach(x=>{ const on=!st.pg&&x.k===vis; v['navvis_'+x.k]=MA_NAVST[on?1:0]; v['navvis_'+x.k+'_cur']=on?'page':'false'; });   /* subitem do menu = visão aberta (no detalhe, nenhum) */
  const lista=!st.pg; v.lista=lista; v.pg_ativo=!!(st.pg&&st.pg.k==='ativo'&&c.ativos[st.pg.id]); v.pg_plano=!!(st.pg&&st.pg.k==='plano'&&c.planos[st.pg.id]);
  ['semordem','ordens','ativos','planos'].forEach(k=>{ v['v_'+k]=lista&&vis===k; });
  self.g2pick=(gid,rid)=>{ self.__lastRow=rid; const cc=manGet();
    if(gid==='g_so'){ const r=(self.__so||[]).find(x=>x.id===rid); if(r) ma_abrir(self,r.k==='venc'?'venc':'achado',rid.slice(2)); }
    else if(gid==='g_om'||gid==='d_om') ma_abrir(self,'om',rid);
    else if(gid==='g_at') ma_pg(self,'ativo',rid);
    else if(gid==='g_ab'||gid==='d_lei') ma_abrir(self,'leitura',rid);
    else if(gid==='g_pl') ma_pg(self,'plano',rid);
    else if(gid==='d_venc') ma_abrir(self,'venc',rid);
    else if(gid==='d_ach') ma_abrir(self,'achado',rid);
    else if(gid==='d_vinc'){ ma_pg(self,'ativo',rid.split('|')[1]); } };
  /* seletor de visão (ABA-02, DS-MAN 17/10/2026): o número da aba é o que pede ação naquela visão, só quando passa de zero, com a dica que diz o
     que ele conta; é o mesmo número da lista aberta (Sem ordem, até 10 d) ou de um filtro rápido da visão (Ordens › Aguardam você; Ativos ›
     Bloqueado). Planos sem número (rascunho é raro e aparece no Estado da lista). Antes: "Ordens 0" com 16 ordens e "Planos 0" com 10 planos.
     Vermelho só para impedimento (§3.1) */
  const so=ma_linhasSemOrdem(self,c,{prazo:'10',tipo:''}); const espera=Object.values(c.oms).filter(o=>ma_espera(c,o,pf)).length;
  const bloq=Object.values(c.ativos).filter(a=>a.cond==='Bloqueado').length;
  const pl_=(n,um,muitos)=>n+' '+(n>1?muitos:um);
  const cont={semordem:[so.length,so.some(r=>r.crit),pl_(so.length,'pendência vencida ou que vence em até 10 dias','pendências vencidas ou que vencem em até 10 dias')],
    ordens:[espera,false,pl_(espera,'ordem aguarda você','ordens aguardam você')],ativos:[bloq,bloq>0,pl_(bloq,'ativo bloqueado','ativos bloqueados')],planos:[0,false,'']};
  v.vis=MA_VIS.map(x=>{ const on=lista&&vis===x.k; const n=cont[x.k][0]; const red=cont[x.k][1];
    return {k:x.k,t:x.t,n:String(n),temN:n>0,dica:n>0?cont[x.k][2]:'',lab:n>0?(x.t+' · '+cont[x.k][2]):x.t,opt:n>0?(x.t+' · '+n):x.t,on:String(on),go:()=>ma_vis(self,x.k),st:'display:inline-flex;align-items:center;gap:7px;font-family:inherit;font-size:13px;font-weight:700;padding:7px 14px;border-radius:999px;cursor:pointer;white-space:nowrap;'+(on?'border:1px solid #1E7A4C;background:#E4F3E9;color:#1E6B47;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;'),
      nst:'font-size:11.5px;font-weight:800;padding:0 7px;border-radius:999px;'+(red?'background:#FDE8E6;color:#B42318;':'background:#EEF1EE;color:#15201A;')}; });
  v.vis_k=vis; v.vis_set=(e)=>ma_vis(self,e.target.value);
  /* CAB-3 (DS-MAN): o cabeçalho diz a tela — trilha "Manutenção › <visão>" e o título da visão (no detalhe: "› <registro>"), como a O.S. */
  const pgA=st.pg&&st.pg.k==='ativo'?c.ativos[st.pg.id]:null, pgP=st.pg&&st.pg.k==='plano'?c.planos[st.pg.id]:null;
  v.ma_tit=pgP?MA_VISTIT.planos:(pgA?MA_VISTIT.ativos:MA_VISTIT[vis]); v.ma_tr_reg=pgA?pgA.nome:(pgP?(pgP.id+' · '+pgP.nome):''); v.ma_tr_det=!!v.ma_tr_reg; v.ma_tr_lista=!v.ma_tr_reg;
  /* selo do cabeçalho: só impedimentos, calculado */
  const conf=Object.values(c.oms).filter(o=>(o.etapa==='A liberar'||o.etapa==='Liberadas')&&manConflito(c,o)&&!o.conflitoAceito).length;
  const capp=manAppConfAbertos(c).length;   /* registros do app a resolver (S4) */
  const sl=[]; if(bloq) sl.push(bloq+(bloq>1?' ativos bloqueados':' ativo bloqueado')); if(conf) sl.push(conf+(conf>1?' conflitos':' conflito')); if(capp) sl.push(capp+(capp>1?' registros do app a resolver':' registro do app a resolver'));
  v.st_ma=sl.join(' · ')||'Sem impedimentos'; v.st_ma_st=ma_chipSt(sl.length?'red':'green').replace('padding:2px 9px;','padding:3px 10px;'); v.st_ma_dot=ma_dotSt(sl.length?'red':'green');
  /* MAN-LIMPA-01 (proprietário, 14/10/2026: "elimine os cards de manutenção, vamos focar os cards na área de gráficos e relatórios"): a tela de
     trabalho não tem cartões; os indicadores ficam no Painel de Manutenção. Os filtros seguem a faixa Filtros (funil), como na O.S. */
  const chs=(lst,cur,set)=>lst.map(([k,t])=>({t,on:String(cur===k),st:ma_pill(cur===k),go:()=>set(k)}));
  /* Sem ordem: prazo com a contagem de cada recorte (TAB-02), no recorte da faixa Filtros, dentro do bloco (DS-MAN) */
  v.so_prazo=[['venc','Vencidas'],['10','Até 10 d'],['30','Até 30 d']].map(([k,t])=>{ const on=(st.prazo||'10')===k; const r=ma_linhasSemOrdem(self,c,Object.assign({},st,{prazo:k,tipo:''})); const n=(st.ftipo?r.filter(x=>x.tp===st.ftipo):r).length;
    return {t,n:String(n),temN:true,dica:'',on:String(on),st:ma_chipF(on),nst:ma_nst(on),go:()=>self.setState({prazo:k})}; });
  const grupos=[]; c.ordem.forEach(id=>{ const g=(c.ativos[id]||{}).grupo; if(g&&grupos.indexOf(g)<0) grupos.push(g); });
  v.f_grupos=[{v:'',t:'Todos os grupos'}].concat(grupos.map(g=>({v:g,t:g}))); v.f_grupo=st.fgrupo||''; v.f_setgrupo=(e)=>self.setState({fgrupo:e.target.value});
  const TIPOS={semordem:['Preventiva','Corretiva','Inspeção'],ordens:['Preventiva','Corretiva']}; const vv=st.vis||'semordem';
  v.f_tipos=[{v:'',t:'Todos os tipos'}].concat((TIPOS[vv]||[]).map(x=>({v:x,t:x}))); v.f_tipo=st.ftipo||''; v.f_settipo=(e)=>self.setState({ftipo:e.target.value});
  v.flt_tipo=!!TIPOS[vv]; v.flt_crit=!!TIPOS[vv];   /* cada visão mostra só os filtros que valem para ela; a Pendência dos ativos fica na barra da lista (DS-MAN) */
  v.f_crits=[{v:'',t:'Toda criticidade'},{v:'Alta',t:'Alta'},{v:'Média',t:'Média'},{v:'Baixa',t:'Baixa'}]; v.f_crit=st.fcrit||''; v.f_setcrit=(e)=>self.setState({fcrit:e.target.value});
  /* Ordens: chips Todas + 5 fases (a única contagem de fase, no recorte da faixa Filtros); rotina; Lista | Kanban em ícones */
  const os=Object.values(c.oms).filter(o=>o.etapa!=='Canceladas'); const ab=os.filter(o=>manAberta(o)); const osB=ma_omFiltro(c,os,st);
  v.fchips=[{t:'Todas',n:String(osB.length),temN:true,dica:'',on:String(!st.fase),go:()=>self.setState({fase:''}),st:ma_chipF(!st.fase),nst:ma_nst(!st.fase)}].concat(MAN_FASES.map(f=>({t:f,n:String(osB.filter(o=>o.etapa===f).length),temN:true,dica:'',on:String(st.fase===f),st:ma_chipF(st.fase===f),nst:ma_nst(st.fase===f),go:()=>self.setState({fase:st.fase===f?'':f})})));
  const nVoce=os.filter(o=>ma_espera(c,o,pf)).length; const dom=manAdd(c.hoje,7-new Date(manT(c.hoje)).getUTCDay());
  /* DS-MAN (17/10/2026): no bloco ficam as fases e 2 recortes de ação (Aguardam você, Com conflito). "Esta semana" (com a carga por dia) e
     "Espera por peça" passam ao ⋯ do bloco; ligados, aparecem como recorte ativo ao lado dos outros e saem com um toque. A Pendência também
     filtra por pendência pela coluna (Falta peça, Conflito…) */
  const rot=(k,t,n,dica)=>({t,n:n===null?'':String(n),temN:n!==null,dica:dica||'',on:String(st.rot===k),st:ma_chipF(st.rot===k),nst:ma_nst(st.rot===k),go:()=>self.setState({rot:st.rot===k?'':k})});
  v.rotinas=[rot('voce','Aguardam você',nVoce,'Ordens em que o próximo passo é seu'),rot('conf','Com conflito',os.filter(o=>ma_temConf(c,o)).length,'Conflito com a produção ou registro do app a resolver')]
    .concat(st.rot==='semana'?[rot('semana','Esta semana',null,'Ordens abertas com janela até domingo; a carga por dia aparece acima da lista')]:[])
    .concat(st.rot==='peca'?[rot('peca','Espera por peça',ab.filter(o=>manFalta(c,o).length).length,'Ordens abertas com peça em falta')]:[]);
  v.om_semana_go=()=>self.setState({rot:'semana'}); v.om_peca_go=()=>self.setState({rot:'peca'});
  /* DS VIS-05 (15/10/2026: "toda lista tem Tabela e Cartões"): Lista | Cartões | Kanban; Cartões é a mesma grade g_om em cartões (g2lib.g2modosFim) */
  v.om_lista=['lista','cartoes'].indexOf(st.omodo||'lista')>=0; v.om_kanban=st.omodo==='kanban'; self.g2modoExterno=(gid)=>(gid==='g_om'&&self.state.omodo==='cartoes')?'cartoes':'tabela';
  v.om_modos=[['lista','Lista','v_lista'],['cartoes','Cartões','v_cartoes'],['kanban','Kanban','v_kanban']].map(([k,t],i)=>({k,t,i:String(i),li:k==='lista',ca:k==='cartoes',ka:k==='kanban',on:String((st.omodo||'lista')===k),go:()=>self.setState({omodo:k})}));
  v.semana=st.rot==='semana'; const dias={}; os.filter(o=>manAberta(o)&&o.janIso&&o.janIso<=dom).forEach(o=>{ const d=o.janIso<c.hoje?'vencidas':o.janIso; (dias[d]=dias[d]||[]).push(o); });
  v.sem_dias=Object.keys(dias).sort().map(d=>{ const esp={}; dias[d].forEach(o=>{ esp[o.esp]=(esp[o.esp]||0)+(Number(o.tempo)||0); });
    return {t:d==='vencidas'?'Atrasadas':(manSem(d)+' '+manBr(d)),oms:dias[d].map(o=>o.id).join(', '),hh:Object.keys(esp).map(k=>k+' '+manN(esp[k],1)+' HH').join(' · ')}; });
  /* Kanban: 5 colunas fixas, o mesmo filtro da lista */
  const spO=ma_G('g_om'), stO=g2st(self,'g_om'); const okIds=new Set((self.__om||[]).filter(r=>g2match(r,spO,stO)).map(r=>r.id));
  v.kb=MAN_FASES.map(f=>{ const cs=os.filter(o=>o.etapa===f&&okIds.has(o.id)); return {t:f,n:String(cs.length),nst:'background:#EEF1EE;color:#15201A;border-radius:999px;font-weight:800;',carga:cs.length?manN(cs.reduce((s,o)=>s+(Number(o.tempo)||0),0),1)+' HH':'',vazio:!cs.length,
    cards:cs.map(o=>{ const a=c.ativos[o.aid]; const sl=manSelos(c,o); return {id:o.id,lab:'Abrir '+o.id+' · '+(a?a.nome:''),open:()=>ma_abrir(self,'om',o.id),key:(e)=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); ma_abrir(self,'om',o.id); } },
      st:'display:flex;flex-direction:column;gap:5px;padding:10px;border-radius:10px;background:#fff;border:1px solid #E4E9E5;cursor:pointer;text-align:left;',tipo:o.serv,local:(a?a.nome:'')+' · '+(o.jan||'—'),hasBar:false,bar:'',hasReal:false,real:'',
      selos:sl.slice(0,2).map(z=>({t:z.t,st:ma_chipSt(z.c),dot:ma_dotSt(z.c)})),hasObs:false,obs:'',hasDp:!!o.executante,dp:o.executante?('Executante: '+o.executante):'',meta:o.tipo+' · '+o.crit}; })}; });
  /* Ativos: Ativos | Abastecimentos; custo da coluna no mês corrente (o período e os indicadores ficam no Painel) */
  /* (o período ficou só no cálculo do custo do mês da coluna) */
  v.at_ativos=(st.amodo||'ativos')==='ativos'; v.at_abast=st.amodo==='abast';
  v.at_modos=[['ativos','Ativos'],['abast','Abastecimentos']].map(([k,t])=>({t,on:String((st.amodo||'ativos')===k),st:ma_chipF((st.amodo||'ativos')===k),go:()=>self.setState({amodo:k})}));   /* DS-MAN: escolha dentro do bloco */
  /* MA-VINCULO: filtro rápido "Sem plano" na barra da grade (TAB-01; o mesmo estado da lista Pendência, ao lado dele desde a DS-MAN) */
  { const nsp=manSemPlano(c).filter(a=>!st.fgrupo||a.grupo===st.fgrupo).length; const onS=st.fpend==='Sem plano';
    v.at_semp_tem=nsp>0||onS; v.at_semp_n=String(nsp); v.at_semp_on=String(onS); v.at_semp_lab=onS?'Mostrar todos os ativos':'Mostrar só os ativos sem plano';
    v.at_semp_st='font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;min-height:var(--g2-alvo,0px);box-sizing:border-box;'+(onS?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;');
    v.at_semp_go=()=>self.setState({fpend:onS?'':'Sem plano'}); }
  v.pl_desv=(k)=>dvAbrir(self,k);
  v.f_pends=[{v:'',t:'Toda pendência'}].concat(['Leitura a confirmar','Sem plano','Achado sem ordem','Desvio de consumo','Vence em 30 d','Restrição vencida'].map(x=>({v:x,t:x}))); v.f_pend=st.fpend||''; v.f_setpend=(e)=>self.setState({fpend:e.target.value});
  /* Planos: linha calculada dos ativos sem plano */
  const sp=pmSemPlano(c); v.tem_sem=sp.length>0; v.sem_n=sp.length+(sp.length>1?' ativos sem plano':' ativo sem plano'); v.sem=sp.map(a=>({t:a.nome,lab:'Criar plano para '+a.nome,go:()=>pmNovo(self,manGet(),a.id)}));
  /* primária da visão (cabeçalho): com painel aberto, só a do painel é primária */
  const panAberto=!!(st.pan||st.sv||st.np||st.vl||st.dv); ma_hprim(self,v,c,pf,vis,lista,panAberto);
  /* páginas e painéis */
  if(v.pg_ativo) ma_ativoV(self,v,c,c.ativos[st.pg.id],pf); else ma_ativoV0(v);
  if(v.pg_plano) pmPlanoV(self,v,c,c.planos[st.pg.id],pf); else pmPlanoV0(v);
  ma_panV(self,v,c,pf); pmSvP(self,v,c); pmNpP(self,v,c); vlP(self,v,c,pf); dvP(self,v,c,pf); }
function ma_hprim(self,v,c,pf,vis,lista,panAberto){ let t='',fn=null,dis='',sec=null;
  if(lista&&vis==='semordem'){ const spS=ma_G('g_so'), stS=g2st(self,'g_so'); const ks=(self.__so||[]).filter(r=>r.k==='venc'&&r.devida&&g2match(r,spS,stS)).map(r=>r.key); const n=ks.length;   /* A6: o que a grade mostra */
    t=n?('Gerar '+n+(n>1?' ordens preventivas':' ordem preventiva')):'Gerar ordens preventivas'; dis=n?manPode(c,pf,'gerar'):'Nada a gerar neste filtro';
    fn=()=>{ const r=ma_cmd(self,c2=>manGerarTodas(c2,ks,g2perfil())); if(r&&r.ids&&r.ids.length){ self.setState({gerados:r.ids,vis:'ordens',fase:'A liberar',rot:''}); ma_abrir(self,'om',r.ids[0]); ma_rec(self,r,r.ids.length>1?{t:'Abrir as '+r.ids.length+' › próxima: '+r.ids[1],k:'om',id:r.ids[1]}:null); } };
    sec={t:'Registrar achado',fn:()=>ma_novoAch(self,'')}; }
  else if(lista&&vis==='ativos'&&self.state.amodo==='abast'){ t='Registrar abastecimento'; dis=manPode(c,pf,'registrar'); fn=()=>ma_novoAb(self,''); }
  else if(lista&&vis==='planos'){ t='Criar plano'; dis=manPode(c,pf,'plano'); fn=()=>pmNovo(self,manGet(),null); }
  else if(lista&&vis==='ativos'){ const spA=ma_G('g_at'), stA=g2st(self,'g_at'); const qc=spA.qf?spA.cols.find(x=>x.k===spA.qf.k):null;
    const ids=(self.__at||[]).filter(r=>r.semp&&g2match(r,spA,stA)&&(!stA.qv||!qc||g2qhas(r,qc,spA.qf,stA.qv))).map(r=>r.id);   /* MA-VINCULO: o que a grade mostra */
    if(ids.length){ t='Vincular a plano'; dis=manPode(c,pf,'plano'); fn=()=>vlAbrir(self,{aids:ids}); }
    sec={t:'Registrar achado',fn:()=>ma_novoAch(self,'')}; }
  /* CAB-4 (DS-MAN): a primária fica verde; indisponível para o perfil, é a peça comum acao_motivo (aria-disabled, dica e o motivo junto do botão) */
  v.hp_tem=!!t; v.hp_t=t; v.hp_dis=!!dis; v.hp_why=dis||''; v.hp_fn=fn||(()=>{}); v.hp_st=panAberto?MA_SEC:MA_PRIM;
  v.hs_vis=!!sec&&!t; v.hs_menu=!!sec&&!!t; v.hs_t=sec?sec.t:''; v.hs_fn=sec?sec.fn:(()=>{}); }   /* MAIS-01: com a primária à vista, a secundária vai para o ⋯ */
'''

# ---------- detalhe do ativo (página) ----------
MA_JS+=r'''
function ma_motor(a){ return ['Trator','Colhedora','Pulverizador','Veículo'].indexOf(a.classe)>=0; }
function ma_agenda(c,aid){ const r=MAN_AL.rec[aid]; if(!r) return []; return manAloc().filter(x=>x.r===r&&x.dia>=c.hoje).map(x=>manBr(x.dia)+' '+x.os+' '+String(Math.floor(x.ini)).padStart(2,'0')+':'+String(Math.round((x.ini%1)*60)).padStart(2,'0')+'–'+String(Math.floor(x.fim)).padStart(2,'0')+':'+String(Math.round((x.fim%1)*60)).padStart(2,'0')+(x.sit==='firme'?'':' · '+x.sit)); }
function ma_custoNat(c,aid,per){ const P=manPeriodo(c,per); const n={pecas:0,lub:0,ofi:0,terc:0};
  Object.values(c.oms).filter(o=>o.aid===aid&&o.etapa==='Encerradas'&&o.exec&&o.exec.data>=P.de&&o.exec.data<=P.ate).forEach(o=>{ (o.pecas||[]).forEach(p=>{ const v=(p.apl||0)*(p.preco||0); if(/^(OL|GR)-/.test(p.item||'')) n.lub+=v; else n.pecas+=v; });
    n.ofi+=((o.exec&&o.exec.horas)||0)*c.custoh; n.terc+=Number(o.terc)||0; }); return n; }
function ma_ativoV0(v){ v.at_kv=[]; v.at_blk=[]; v.at_agenda=[]; v.at_hist=[]; v.at_cn=[]; v.at_prim=false; v.at_secs=[]; }
function ma_ativoV(self,v,c,a,pf){ const st=self.state; const i=a.condInfo||{}; const ms=manMots(a); const trs=ms.map(m=>manMotOm(c,m)).filter(Boolean); const tr=trs[0]||(i.om&&c.oms[i.om]);
  v.at_cas=ma_cas(self,c,manAppConfAbertos(c,undefined,a.id),pf); v.at_hasCa=v.at_cas.length>0;
  v.at_t=a.nome; v.at_sub=a.modelo+' · '+a.local+' · '+a.grupo+' · responsável técnico: '+manRtTxt(a); v.at_cond=ma_condTxt(c,a); v.at_cst=ma_chipSt(ma_cond(a)); v.at_cdot=ma_dotSt(ma_cond(a));
  v.at_leit=a.leit?('Leitura '+manLeitTxt(a)+(a.suspeita?' · '+manQ(a.suspeita.val,a.un)+' a confirmar':'')):'Sem contador'; v.voltar=()=>ma_volta(self);
  const achs=Object.values(c.achados).filter(q=>q.aid===a.id&&q.estado==='Sem ordem');
  const bo=st.blk||{};   // TAB-12 (17/10/2026): todo bloco nasce recolhido, com o resumo à vista (antes abria o da situação atual)
  const B=(k,t,sum)=>{ const open=!!bo[k]; const tog=()=>self.setState({blk:Object.assign({},self.state.blk||{},{[k]:!open})});
    v['ab_'+k]=open; v['abk_'+k+'_t']=t; v['abk_'+k+'_s']=sum; v['abk_'+k+'_o']=g2seta(open).exp; v['abk_'+k+'_g']=tog; return {k,t,sum,open:String(open),tog}; };
  const ls=manLinhas(c).filter(l=>l.aid===a.id&&l.s); const oms=Object.values(c.oms).filter(o=>o.aid===a.id);
  v.at_blk=[B('sit','Situação',ma_condTxt(c,a)+(ms.length>1?' · '+ms.length+' motivos':'')+(trs.length?' · tratada pela '+[...new Set(trs.map(o=>o.id))].join(' e '):'')),B('venc','O que vence',ls.length?(ls.filter(manDevida).length+' devido(s) de '+ls.length):'Sem plano'),
    B('ach','Achados',achs.length?(achs.length+' sem ordem'):'nenhum sem ordem'),B('om','Ordens',oms.filter(manAberta).length+' abertas · '+oms.filter(o=>!manAberta(o)).length+' encerradas'),
    B('lei','Leituras e abastecimentos',a.suspeita?'1 leitura a confirmar':(a.leit?manLeitTxt(a):'sem contador')),B('cus','Custo e desempenho',manRS(manCustoPeriodo(c,st.per||'mes',a.id).enc)+' · '+manPeriodo(c,st.per||'mes').t)];
  v.at_kv=[{l:'Condição',v:ma_condTxt(c,a)+(i.motivo&&ms.length<2?' · '+i.motivo:'')}].concat(ms.length>1?ms.map((m,j)=>({l:'Motivo '+(j+1),v:m.motivo+' · '+manMotTxt(c,m)+(manMotOm(c,m)?' '+manMotOm(c,m).etapa:'')})):[])
    .concat([{l:'Desde · quem',v:i.desde?(manBr(i.desde)+' · '+(i.por||'—')):'—'},{l:'Evidência',v:i.evid||'—'},
    {l:'Prazo · limites',v:a.cond==='Restrito'?((i.ate?'até '+manBr(i.ate):'sem prazo')+(i.lim?' · '+i.lim:'')+(manRestricaoVencida(c,a)?' · Restrição vencida':'')):'—'},
    {l:'Tratada pela',v:trs.length?[...new Set(trs.map(o=>o.id+' · '+o.etapa))].join(' e '):'—'},{l:'Responsável técnico',v:manRtTxt(a)},
    {l:'Leitura',v:a.leit?(manLeitTxt(a)+' · '+a.leit.origem):'sem contador'},{l:'Retorno previsto',v:tr&&manAberta(tr)?(tr.ret||'—')+(manFalta(c,tr).length?' (condicional: falta peça)':'')+(ms.length>1?' · apto só com todos os motivos resolvidos':''):'—'}]);
  v.at_agenda=ma_agenda(c,a.id).map(t=>({t})); v.at_semAgenda=!v.at_agenda.length;
  v.at_hist=(a.condHist||[]).slice(-4).reverse().map(h=>({t:manBr(h.em)+' · '+h.cond+' · '+h.motivo+(h.por?' · '+h.por:'')}));
  v.at_mudar=()=>ma_abrir(self,'cond',a.id); v.at_mudar_dis=!!manPode(c,pf,'condicao',{aid:a.id}); v.at_mudar_why=manPode(c,pf,'condicao',{aid:a.id});
  const per=st.per||'mes'; const n=ma_custoNat(c,a.id,per); const cons=ma_consumo(c,a); const cu=(()=>{ const os=Object.values(c.oms).filter(o=>o.aid===a.id&&o.tipo==='Preventiva'&&o.etapa==='Encerradas'&&o.vencOrig); return os.length?(os.filter(o=>o.exec&&o.exec.data<=o.vencOrig).length+' de '+os.length):'não calculável'; })();
  v.at_cn=[{l:'Peças (3.1.05)',v:manRS(n.pecas)},{l:'Lubrificantes (3.1.04)',v:manRS(n.lub)},{l:'Oficina (Custo R$/h da oficina '+c.custoh+')',v:manRS(n.ofi)},{l:'Terceiros',v:manRS(n.terc)},
    {l:'Custo por hora operada',v:'não calculável (KPI-PCM-10)'},{l:'Consumo',v:cons?(cons.t+(cons.desvio!==null?' · desvio '+(cons.desvio>0?'+':'')+cons.desvio+' %':'')):'— sem método'},
    {l:'Disponibilidade 30 d',v:'não calculável'},{l:'MTBF · MTTR',v:'não estimável'},{l:'Cumprimento de preventiva',v:cu}];
  /* primária do detalhe: a primeira que se aplica (§3.4) */
  const semTrata=a.cond==='Bloqueado'&&ms.some(m=>!manMotOm(c,m)); let P=null;   /* A1: algum motivo sem ordem que o trate */
  if(a.suspeita) P={t:'Confirmar leitura '+manQ(a.suspeita.val,a.un),fn:()=>ma_abrir(self,'leitura',a.suspeita.lt||a.suspeita.ab),dis:manPode(c,pf,'leituraDecidir')};
  else if(semTrata) P={t:'Criar ordem corretiva',fn:()=>ma_cmd(self,c2=>manCorretivaAtivo(c2,a.id,g2perfil(),self.state.pchave),(r)=>{ if(r.id) ma_abrir(self,'om',r.id); ma_rec(self,r); }),dis:manPode(c,pf,'decidir')};
  else if(ma_motor(a)&&a.un) P={t:'Registrar abastecimento',fn:()=>ma_novoAb(self,a.id),dis:manPode(c,pf,'registrar')};
  else if(a.un) P={t:'Registrar leitura',fn:()=>ma_novaLeit(self,a.id),dis:manPode(c,pf,'registrar')};
  const panAberto=!!(st.pan||st.sv||st.np||st.vl||st.dv);
  v.at_prim=!!P; v.at_pt=P?P.t:''; v.at_pfn=P?P.fn:(()=>{}); v.at_pdis=!!(P&&P.dis); v.at_pwhy=(P&&P.dis)||''; v.at_pst=(panAberto||(P&&P.dis))?MA_SEC:MA_PRIM;
  v.at_secs=[{t:'Registrar achado',fn:()=>ma_novoAch(self,a.id),dis:manPode(c,pf,'registrar')}].concat(a.un&&(!P||P.t!=='Registrar leitura')?[{t:'Registrar leitura',fn:()=>ma_novaLeit(self,a.id),dis:manPode(c,pf,'registrar')}]:[])
    .map(x=>({t:x.t,fn:x.fn,dis:!!x.dis,why:x.dis||'',st:MA_SEC}));
  v.at_cd03='CD-03.dc.html'; v.at_rec='OS.dc.html';
  /* MA-VINCULO: os planos do ativo à vista no cabeçalho; sem plano, "Vincular ao PM-xx ›" (sugestão explícita: abre o painel) ou "Criar plano ›" */
  const pls=manPlanosDe(c,a.id); const semp=manAtvAtivo(a)&&!pls.some(manPlVale); const sg=semp?manVincSug(c,a)[0]:null;
  v.at_pls=pls.map(p=>{ const si=manPlSit(c,p,a); return {t:p.id,h:'#plano='+p.id,s:si.t,st:ma_chipSt(si.c),dot:ma_dotSt(si.c)}; }); v.at_temPls=pls.length>0;
  v.at_semPl=semp; v.at_semPlt=sg?((sg.cp.nivel==='escopo'?'Sem vínculo':'Sem plano')+' · Vincular ao '+sg.p.id+' ›'):'Sem plano · Criar plano ›';
  v.at_semPlGo=()=>{ if(sg) vlAbrir(self,{aids:[a.id]}); else pmNovo(self,manGet(),a.id); }; }
'''

# ---------- painéis (um por registro; uma primária no rodapé) ----------
MA_JS+=r'''
function maF(self,k,x){ const f=Object.assign({},self.state.pf||{}); f[k]=x; self.setState({pf:f,paviso:null}); }
function ma_novoAch(self,aid){ ma_abrir(self,'novoAch','',{pf:{aid:aid||'',origem:'',comp:'',sint:'',crit:'',sug:'',evid:'',leit:''}}); }
function ma_novoAb(self,aid){ const c=manGet(); const tq=aid?manTanques(c,aid):[]; ma_abrir(self,'abast','',{pf:{aid:aid||'',data:c.hoje,tq:tq.length===1?tq[0]:'',vol:'',leit:'',op:aid?manOperadorDia(c,aid,c.hoje):'',evid:'',cheio:false}}); }
function ma_novaLeit(self,aid){ const c=manGet(); ma_abrir(self,'novaLeit','',{pf:{aid:aid||'',data:c.hoje,leit:''}}); }
function ma_btn(t,fn,dis,prim){ return {t,fn:dis?(()=>{}):fn,dis:!!dis,why:dis||'',st:(prim&&!dis)?MA_PRIM:MA_SEC}; }
function ma_panV(self,v,c,pf){ const st=self.state; const pan=st.pan;
  const L=['pk_om','pk_achado','pk_venc','pk_cond','pk_leitura','pk_novoAch','pk_abast','pk_novaLeit','pk_pub']; L.forEach(k=>{ v[k]=false; });
  ['om_fases','om_blk','om_tks','om_pcs','om_rets','om_kv','om_achs','om_cands','om_atalhos','ac_kv','ac_crit','ac_secs','vc_kv','vc_pecas','cd_acoes','cd_hist','cd_achs','cd_oms','cd_rts','lt_kv','na_ativos','na_orig','na_comp','na_crit','na_sug','ab_ativos','ab_tqs','ab_ops','ab_datas','nl_ativos','pb_dif','pb_oab','pan_secs','om_inc_tipos'].forEach(k=>{ v[k]=[]; });
  v.pan_open=!!pan; v.anun=st.anun||''; if(!pan||pan.k!=='om') self.__rv=null; if(!pan){ v.pan_t=''; v.pan_sub=''; return; }
  v.pan_modal=!!pan.modal; v.pan_role=pan.modal?'dialog':'complementary'; v.pan_am=pan.modal?'true':'false'; v.pan_cls='ma-pan'+(pan.modal?'':' ma-nm');
  v.pan_close=()=>ma_fechar(self);
  v.pan_key=(e)=>{ if(!e) return; if(e.key==='Escape'){ e.preventDefault(); ma_fechar(self); return; } let est=false; try{ est=window.matchMedia('(max-width: 640px)').matches; }catch(x){}
    if(e.key==='Tab'&&(pan.modal||est)) ma_trap(e,document.getElementById('ma-painel')); };
  self.__panClose=()=>ma_fechar(self); ma_modalDoc(self,()=>(self.state.pan&&self.state.pan.modal)?{root:document.getElementById('ma-painel'),close:()=>self.__panClose()}:null);
  const rec=st.rec; v.pan_rec=!!rec; v.pan_rect=rec?rec.msg:''; v.pan_hasProx=!!(rec&&rec.prox); v.pan_proxt=rec&&rec.prox?rec.prox.t:''; v.pan_prox=()=>{ const p=self.state.rec&&self.state.rec.prox; if(p) ma_abrir(self,p.k,p.id); };
  const av=st.paviso; v.pan_av=!!av; v.pan_avt=av?av.t:''; v.pan_avHasIn=!!(av&&av.campo); v.pan_avin=av&&av.campo?(st.pf||{})[av.campo]||'':''; v.pan_avlab=av&&av.lab||''; v.pan_avset=(e)=>{ const f=Object.assign({},self.state.pf||{}); f[av.campo]=e.target.value; self.setState({pf:f}); };
  v.pan_avok=av&&av.ok?av.ok.fn:(()=>{}); v.pan_avokt=av&&av.ok?av.ok.t:''; v.pan_avno=()=>{ self.setState({paviso:null}); if(av&&av.foco) setTimeout(()=>{ const e=document.getElementById(av.foco); if(e){ e.focus(); if(e.select) e.select(); } },0); }; v.pan_avnot=av&&av.no?av.no:'Voltar';
  let P=null, S=[]; const k=pan.k;
  if(k==='om'){ const o=c.oms[pan.id]; if(o){ v.pk_om=true; const r=ma_panOm(self,v,c,o,pf); P=r.P; S=r.S; } }
  else if(k==='achado'){ const q=c.achados[pan.id]; if(q){ v.pk_achado=true; const r=ma_panAch(self,v,c,q,pf); P=r.P; S=r.S; } }
  else if(k==='venc'){ v.pk_venc=true; const r=ma_panVenc(self,v,c,pan.id,pf); P=r.P; S=r.S; }
  else if(k==='cond'){ const a=c.ativos[pan.id]; if(a){ v.pk_cond=true; const r=ma_panCond(self,v,c,a,pf); P=r.P; S=r.S; } }
  else if(k==='leitura'){ v.pk_leitura=true; const r=ma_panLeit(self,v,c,pan.id,pf); P=r.P; S=r.S; }
  else if(k==='novoAch'){ v.pk_novoAch=true; const r=ma_panNovoAch(self,v,c,pf); P=r.P; S=r.S; }
  else if(k==='abast'){ v.pk_abast=true; const r=ma_panAb(self,v,c,pf); P=r.P; S=r.S; }
  else if(k==='novaLeit'){ v.pk_novaLeit=true; const r=ma_panNovaLeit(self,v,c,pf); P=r.P; S=r.S; }
  else if(k==='pub'){ const p=c.planos[pan.id]; if(p){ v.pk_pub=true; const r=pmPubV(self,v,c,p,pf); P=r.P; S=r.S; } }
  const hideP=!!av; v.pan_hasP=!!P&&!hideP; v.pan_pt=P?P.t:''; v.pan_pfn=P?P.fn:(()=>{}); v.pan_pdis=!!(P&&P.dis); v.pan_pst=P?P.st:MA_SEC; v.pan_pwhy=P?P.why:''; v.pan_hasWhy=!!(P&&P.why&&!hideP);
  v.pan_secs=hideP?[]:S; }
/* ---------- painel da OM: o único detalhe da ordem (web e app) ---------- */
/* cancelar sem execução (D5): secundária em A liberar e Liberadas, com motivo; a reserva volta ao livre, com registro (manCancelar) */
function ma_omPrim(self,c,o,pf,f){ const r=ma_omPrim0(self,c,o,pf,f); if(o.etapa!=='A liberar'&&o.etapa!=='Liberadas') return r;
  const canc=()=>self.setState({paviso:{t:'Cancelar a '+o.id+': informe o motivo. A reserva da ordem volta ao estoque livre, com registro.',campo:'canc',lab:'Motivo do cancelamento',
    ok:{t:'Cancelar a '+o.id,fn:()=>{ const mt=(self.state.pf||{}).canc; ma_cmd(self,c2=>manCancelar(c2,o.id,mt,g2perfil(),self.state.pchave),(x)=>ma_rec(self,x)); }},no:'Voltar'}});
  return {P:r.P,S:r.S.concat([ma_btn('Cancelar ordem · motivo',canc,manPode(c,pf,'cancelar'),false)])}; }
function ma_omPrim0(self,c,o,pf,f){ const a=c.ativos[o.aid]; const P={}; const S=[];
  const run=(fn,prox)=>ma_cmd(self,fn,(r)=>ma_rec(self,r,prox===undefined?ma_proxOm(manGet(),g2perfil(),o.id,self.state.gerados):prox));
  if(o.etapa==='A liberar'){ const fl=manFalta(c,o); const cf=manConflito(c,o);
    if(fl.length){ if(!o.sc) return {P:ma_btn('Solicitar compra (simulado · Compras recebe no 1c)',()=>run(c2=>manSolicitar(c2,o.id,g2perfil()),null),manPode(c,pf,'ponte'),true),S};
      return {P:ma_btn('Registrar recebimento (simulado · papel do Almoxarifado)',()=>run(c2=>manReceber(c2,o.id,g2perfil()),null),manPode(c,pf,'ponte'),true),S}; }
    const ex=f.exe!==undefined?f.exe:manExecSug(o); const tp=f.tempo!==undefined?f.tempo:(Number(o.tempo)>0?String(o.tempo).replace('.',','):'');
    const lib=(forcar)=>{ const r=ma_cmd(self,c2=>manLiberar(c2,o.id,forcar,g2perfil(),{executante:ex,tempo:tp}),(r2)=>ma_rec(self,r2,ma_proxOm(manGet(),g2perfil(),o.id,self.state.gerados)));
      if(r.aviso) self.setState({paviso:{t:r.msg,ok:{t:'Liberar mesmo assim',fn:()=>lib(true)},no:'Voltar'}}); };
    const falta=!ex?'Falta: executante':(!(manNum(tp)>0)?'Falta: tempo previsto (h)':''); const pod=manPode(c,pf,'liberar');
    if(cf){ const pl=manProxLivre(c,o); const tl=manTolLim(c,o); const dentro=pl&&(!tl||(!tl.venc&&pl<=tl.dl));
      if(dentro){ S.push(ma_btn('Liberar mesmo assim',()=>lib(true),pod||falta,false)); return {P:ma_btn('Mover janela para '+manBr(pl),()=>run(c2=>manMover(c2,o.id,pl,'',g2perfil()),null),manPode(c,pf,'mover'),true),S}; } }
    return {P:ma_btn('Liberar serviço',()=>lib(false),pod||falta,true),S}; }
  if(o.etapa==='Liberadas') return {P:ma_btn('Iniciar serviço',()=>run(c2=>manIniciar(c2,o.id,g2perfil()),null),manPode(c,pf,'executar',{o}),true),S};
  if(o.etapa==='Em execução'){ const fl=manFaltaConcluir(c,o,f.leit,f.horas); const pod=manPode(c,pf,'executar',{o});
    const conc=(forcar)=>{ const ff=self.state.pf||{}; const ap={}; (o.pecas||[]).forEach((p,i)=>{ if(ff['ap'+i]!==undefined) ap[i]=ff['ap'+i]; });
      const r=ma_cmd(self,c2=>manConcluir(c2,o.id,ff.leit,ff.horas,forcar,ap,g2perfil()),(r2)=>{ self.setState({pf:{}}); ma_rec(self,r2); });
      if(r.avisoLeit) self.setState({paviso:{t:r.msg,ok:{t:'Concluir com esta leitura',fn:()=>conc(true)},no:'Corrigir leitura',foco:'om-leitura'}}); };
    return {P:ma_btn('Concluir serviço',()=>conc(false),pod||(fl.length?'Falta: '+fl.join(' · '):''),true),S}; }
  if(o.etapa==='Em conferência'){ const fe=manFaltaEncerrar(c,o); const custo=manCusto(c,o);
    if(o.trata&&!o.aptidao){ const pod=manPode(c,pf,'condicao',{aid:o.aid}); const m=manAptoMotivo(c,o);
      const manter=()=>self.setState({paviso:{t:'Manter '+(a?a.nome:'o ativo')+' '+(a?a.cond.toLowerCase():'')+': informe o motivo (o vínculo com a '+o.id+' é desfeito).',campo:'mant',lab:'Motivo para manter',
        ok:{t:'Manter '+(a?a.cond.toLowerCase():''),fn:()=>{ const mt=(self.state.pf||{}).mant; ma_cmd(self,c2=>manManter(c2,o.id,mt,g2perfil()),(r)=>ma_rec(self,r)); }},no:'Voltar'}});
      if(!m){ S.push(ma_btn('Manter '+(a?a.cond.toLowerCase():'')+' · motivo',manter,pod,false)); return {P:ma_btn(manAptoRot(c,o),()=>run(c2=>manDeclararApto(c2,o.id,g2perfil())),pod,true),S}; }
      return {P:ma_btn('Manter '+(a?a.cond.toLowerCase():'')+' · motivo',manter,pod,true),S:[ma_btn('Declarar apto',()=>{},m,false)]}; }
    if((o.pecas||[]).some(p=>p.sob>0)) return {P:ma_btn('Resolver sobras (simulado · papel do Almoxarifado)',()=>run(c2=>manSobras(c2,o.id,g2perfil()),null),manPode(c,pf,'ponte'),true),S};
    return {P:ma_btn('Encerrar ordem · '+manRS(custo),()=>run(c2=>manEncerrar(c2,o.id,g2perfil())),manPode(c,pf,'encerrar')||(fe.length?'Falta: '+fe.join(' · '):''),true),S}; }
  return {P:null,S}; }
/* registros do app que chegaram depois de a OM mudar (S4, §3.7): nunca aplicados em silêncio; Otávio aplica sobre o estado de agora ou descarta com motivo */
function ma_cas(self,c,lst,pf){ const pd=manPode(c,pf,'decidir');
  return lst.map(x=>({t:'Conflito a resolver · Otávio · '+x.desc,s:'Registrado no app por '+x.por+' às '+x.at+', sem sinal · '+x.mot,dis:!!pd,why:pd||'',hasWhy:!!pd,
    ap:()=>ma_cmd(self,c2=>manAppConfAplicar(c2,x.id,g2perfil()),(r)=>ma_rec(self,r)),
    dmv:(self.state.pf||{})['cad_'+x.id]||'',dset:(e)=>maF(self,'cad_'+x.id,e.target.value),dlab:'Motivo para descartar · '+x.desc,
    ds:()=>ma_cmd(self,c2=>manAppConfDescartar(c2,x.id,(self.state.pf||{})['cad_'+x.id],g2perfil()),(r)=>ma_rec(self,r))})); }
function ma_panOm(self,v,c,o,pf){ const st=self.state; const f=st.pf||{}; const a=c.ativos[o.aid]; const cur=MAN_FASES.indexOf(o.etapa);
  if(!self.__rv||self.__rv.id!==o.id) self.__rv={id:o.id,rv:o.rv||0};   /* A11: versão lida ao abrir o painel */
  v.om_cas=ma_cas(self,c,manAppConfAbertos(c,o.id),pf); v.om_hasCa=v.om_cas.length>0;
  v.pan_t=o.id+' · '+(a?a.nome:''); v.pan_sub=(String(o.serv||'').indexOf(o.tipo)===0?o.serv:o.tipo+(o.pid?' · '+o.pid+' v'+o.ver:'')+' · '+o.serv); v.om_ah='#ativo='+o.aid; v.om_at='Abrir '+(a?a.nome:'ativo')+' ›'; v.om_goAt=()=>ma_pg(self,'ativo',o.aid);
  v.om_fases=MAN_FASES.map((x,i)=>({t:x,cur:i===cur?'step':'false',st:'display:flex;flex-direction:column;gap:5px;font-size:11.5px;font-weight:'+(i===cur?'800':'600')+';color:'+(i<=cur?'#15201A':'#8A968E')+';',
    bst:'height:5px;border-radius:999px;background:'+(i<cur?'#9CCBB0':(i===cur?'#1E7A4C':'#E4E9E5'))+';'}));
  const pr=ma_omPrim(self,c,o,pf,f); const sl=manSelos(c,o); const p0=sl[0];
  v.om_veio=o.de?('Pendência da '+o.de):(o.pid?(o.pid+' v'+o.ver+' · '+o.serv):(o.origAch?o.origAch+' · achado':String(o.origem||'').split(' · ')[0]));
  v.om_aqui=o.etapa==='Canceladas'&&o.canc?('Cancelada em '+manBr(o.canc.em)+' por '+o.canc.por+' · '+o.canc.motivo):o.etapa; v.om_falta=p0?(p0.t+(p0.dono?' · '+p0.dono:'')+(p0.prazo?' · '+p0.prazo:'')+(sl.length>1?' · +'+(sl.length-1):'')):'nada'; v.om_prox=pr.P?pr.P.t:(o.etapa==='Encerradas'?'—':'—');
  // TAB-12 (17/10/2026): o painel da ordem é o detalhe de UM registro, como o painel da O.S. (exceção da TAB-12): abre o bloco da fase, o que faz a
  // ordem andar (Janela e equipe, Tarefas e Conclusão, Peças, Custo); recolher os blocos daqui custava 2 cliques a cada ordem concluída (AC-PCM-28)
  const ab=o.etapa==='A liberar'||o.etapa==='Liberadas'?'jan':(o.etapa==='Em execução'?'tk':(o.etapa==='Em conferência'?(o.trata&&!o.aptidao?'tk':'pc'):'cus')); const bo=st.oblk||{};
  const B=(k,t,sum)=>{ const open=bo[o.id+k]===undefined?(k===ab||(k==='con'&&o.etapa==='Em execução')):!!bo[o.id+k]; const tog=()=>self.setState({oblk:Object.assign({},self.state.oblk||{},{[o.id+k]:!open})});
    v['ob_'+k]=open; v['obk_'+k+'_t']=t; v['obk_'+k+'_s']=sum; v['obk_'+k+'_o']=g2seta(open).exp; v['obk_'+k+'_g']=tog; return {k,t,sum,open:String(open),tog}; };
  const cf=(o.etapa==='A liberar'||o.etapa==='Liberadas')?manConflito(c,o):null; const nr=o.chk.filter(t=>t.tipo==='Teste'?((t.tent||[]).slice(-1)[0]||{}).r==='Aprovado':!!t.r).length;
  const custoE=manCusto(c,o,'est'), custoF=o.etapa==='Encerradas'?manCustoFinal(c,o):null;
  v.om_blk=[B('jan','Janela e equipe',(o.jan||'—')+' · '+(o.executante||manExecSug(o)||'sem executante')+(cf?' · '+cf.t:'')),B('tk','Tarefas',nr+' de '+o.chk.length+' respondidas'),
    B('pc','Peças',(o.pecas||[]).length?((o.pecas||[]).length+' itens'+((o.retiradas||[]).length?' · '+o.retiradas.length+' retiradas':'')):'sem peças'),
    B('con','Conclusão',o.exec?('concluída '+manBr(o.exec.data)+(o.exec.leit!==null&&o.exec.leit!==undefined&&a?' · '+manQ(o.exec.leit,a.un):'')+' · '+manN(o.exec.horas,1)+' h'):'leitura e horas na conclusão'),
    B('cus','Custo e tempos',custoF!==null?manRS(custoF):(manRS(custoE)+' est.')),B('ori','Origem',(o.achados||[]).length?(o.achados.join(', ')):String(o.origem||'').split(' · ')[0])];
  /* ativo, só leitura */
  const fica=o.trata&&a&&a.cond!=='Apto'?manAptoFica(c,o):[];
  v.om_cond=a?(ma_condTxt(c,a)+(o.trata&&a.cond!=='Apto'?' · tratada por esta OM':'')+(fica.length?' · outros motivos: '+fica.map(m=>manMotTxt(c,m)).join(' · '):'')):'—'; v.om_cst=ma_chipSt(a?ma_cond(a):'gray'); v.om_cdot=ma_dotSt(a?ma_cond(a):'gray'); v.om_leit=a&&a.leit?('Leitura '+manLeitTxt(a)):'sem contador';
  /* janela e equipe */
  const podeJ=(o.etapa==='A liberar'||o.etapa==='Liberadas'); const pm=manPode(c,pf,'mover'); v.om_janEd=podeJ&&!pm; v.om_janRo=!v.om_janEd;
  v.om_jan=(o.jan||'—')+(o.vencOrig&&o.vencOrig!==o.janIso?' · vencimento original '+manBr(o.vencOrig):''); v.om_conf=!!cf; v.om_conft=cf?(cf.t+' · '+cf.det):'';
  const usa=MAN_AL.rec[o.aid]?manAloc().filter(x=>x.r===MAN_AL.rec[o.aid]&&x.dia>=c.hoje&&x.sit!=='manutenção').map(x=>x.os):[];
  /* substituto proposto (ponte até o 1b): o PCP decide em O.S. › Recursos */
  const pp=(c.prop||{})[o.id]; const ps=pp?c.ativos[pp.sub]:null; const pa=(a&&a.cond==='Bloqueado'&&manAberta(o))?manPropAfeta(c,o):[];
  v.om_prop=pp?('Substituto proposto: '+(ps?manNome(ps):pp.sub)+' para '+pp.os.join(' e ')+' · por '+pp.por+' · aguarda PCP (simulado)'):''; v.om_hasProp=!!pp;
  v.om_podeProp=!pp&&pa.length>0&&!!manPropSub(c,o); v.om_propDis=!!manPode(c,pf,'ponte'); v.om_propWhy=manPode(c,pf,'ponte')||('Registrar a proposta de substituto para '+pa.join(' e '));
  v.om_propGo=()=>ma_cmd(self,c2=>manPropor(c2,o.id,g2perfil()),(r)=>ma_rec(self,r));
  v.om_imp=(cf||(a&&a.cond==='Bloqueado'))?('Impacto na produção: '+(cf?cf.os.join(' e ')+' em '+manBr(cf.dia):([...new Set(usa)].join(', ')||'nenhuma O.S. alocada na semana'))+' · lido da alocação do PCP (O.S. › Recursos)'):''; v.om_hasImp=!!v.om_imp;
  const pl=podeJ?manProxLivre(c,o):null; const tl=manTolLim(c,o);
  v.om_atalhos=podeJ?[{t:'Amanhã',d:manAdd(c.hoje,1)}].concat(pl?[{t:'Próxima sem conflito ('+manBr(pl)+')',d:pl}]:[]).map(x=>({t:x.t,on:String(f.jan===x.d),st:ma_pill(f.jan===x.d),go:()=>maF(self,'jan',x.d)})):[];
  v.om_jand=f.jan||''; v.om_setjand=(e)=>maF(self,'jan',e.target.value); v.om_tol=tl?('Tolerância até '+manBr(tl.dl)+(tl.venc?' · já venceu':'')):'';
  v.om_mover=()=>{ const ff=self.state.pf||{}; const r=ma_cmd(self,c2=>manMover(c2,o.id,ff.jan,ff.jmot,g2perfil(),ff.jforca),(r2)=>{ self.setState({pf:{}}); ma_rec(self,r2); });
    if(r.avisoTol) self.setState({paviso:{t:r.msg,campo:'jmot',lab:'Motivo para mover fora da tolerância',ok:{t:'Mover mesmo assim',fn:()=>{ const f2=self.state.pf||{}; ma_cmd(self,c2=>manMover(c2,o.id,f2.jan,f2.jmot,g2perfil(),true),(r3)=>{ self.setState({pf:{}}); ma_rec(self,r3); }); }},no:'Voltar'}});
    else if(r.avisoConf) self.setState({paviso:{t:r.msg,ok:{t:'Mover mesmo assim',fn:()=>{ const f2=self.state.pf||{}; ma_cmd(self,c2=>manMover(c2,o.id,f2.jan,f2.jmot,g2perfil(),true),(r3)=>{ self.setState({pf:{}}); ma_rec(self,r3); }); }},no:'Voltar'}}); };
  v.om_moverDis=!f.jan;
  const ed=o.etapa==='A liberar'&&!manPode(c,pf,'liberar'); v.om_exeEd=ed; v.om_exeRo=!ed;
  const cands=manExecCands(o.esp); const exAt=f.exe!==undefined?f.exe:manExecSug(o);
  v.om_cands=[{v:'',t:cands.length?'Escolha quem executa':'Prestador (texto)'}].concat(cands.map(k=>({v:k,t:k+' · '+((manPessoa(k)||{}).nr||[]).join(', ')}))).concat(o.executante&&cands.indexOf(o.executante)<0?[{v:o.executante,t:o.executante}]:[]);
  v.om_exe=exAt; v.om_setexe=(e)=>maF(self,'exe',e.target.value); v.om_exeTxt=(o.executante||'—')+(o.executante?'':(manExecSug(o)?' · sugerido '+manExecSug(o):''));
  v.om_exeSug=!o.executante&&cands.length===1?('Única pessoa habilitada ('+MAN_ESP_NR[o.esp]+'): '+cands[0]+' · corrigível'):(!cands.length&&!o.executante?'Falta: executante (nenhuma pessoa do CD-04 com a habilitação)':'');
  v.om_esp=o.esp; v.om_tempo=f.tempo!==undefined?f.tempo:(Number(o.tempo)>0?String(o.tempo).replace('.',','):''); v.om_settempo=(e)=>maF(self,'tempo',e.target.value); v.om_tempoTxt=Number(o.tempo)>0?manN(o.tempo,1)+' h':'—';
  v.om_ret=o.ret||'—';
  /* tarefas pelo tipo (nada vem marcado; motivo fora de Feito, Conforme e Aprovado) */
  const exe=o.etapa==='Em execução'; const pE=manPode(c,pf,'executar',{o}); const pT=manPode(c,pf,'teste',{o});
  v.om_tks=o.chk.map((t,i)=>{ const tp=t.tipo||'Serviço'; const isT=tp==='Teste'; const isM=tp==='Medição'; const why=isT?pT:pE; const ed=exe&&!why;
    const R=MAN_RESP[tp]||MAN_RESP['Serviço']; const ul=(t.tent||[]).slice(-1)[0]; const rr=isT?(ul?ul.r:''):(t.r||'');
    const pend=f['tr'+i]||'';
    return {n:String(i+1),t:t.t,tipo:tp,isT,notT:!isT,isM,ed,edR:ed&&!isT,ro:!ed,why:exe&&isT&&!pE&&pT?'Teste: '+pT:'',hasWhy:exe&&isT&&!pE&&!!pT,nova:!!(t.nova&&!t.r),
      opts:R.map(x=>({t:x,on:String(isT?pend===x:t.r===x),lab:x+' · '+t.t,go:()=>{ if(isT){ maF(self,'tr'+i,pend===x?'':x); return; } ma_mud(self,c2=>manResp(c2,o.id,i,t.r===x?'':x,undefined,g2perfil())); },
        st:'font-family:inherit;font-size:12px;font-weight:700;padding:4px 9px;border-radius:8px;cursor:pointer;white-space:nowrap;'+((isT?pend===x:t.r===x)?(MAN_OK.indexOf(x)>=0?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #8A5A00;background:#FFF3D6;color:#8A5A00;'):'border:1px solid #E4E9E5;background:#fff;color:#15201A;')})),
      r:rr||'Sem resposta',rst:ma_chipSt(MAN_OK.indexOf(rr)>=0?'green':(rr?(rr==='Reprovado'?'red':'yellow'):'gray')),rdot:ma_dotSt(MAN_OK.indexOf(rr)>=0?'green':(rr?(rr==='Reprovado'?'red':'yellow'):'gray')),
      por:t.por?('por '+t.por+(t.em?' às '+t.em:'')+((t.motPor&&t.motPor!==t.por)?' · motivo editado por '+t.motPor+(t.motEm?' às '+t.motEm:''):'')):'',hasPor:!!t.por&&!isT,
      mot:t.mot||'',hasMotIn:ed&&!isT&&!!t.r&&MAN_OK.indexOf(t.r)<0,hasMotTx:!ed&&!!t.mot,motlab:'Motivo · '+t.t,setmot:(e)=>{ const val=e.target.value; ma_mud(self,c2=>manResp(c2,o.id,i,t.r,val,g2perfil())); },
      val:t.val===undefined||t.val===''?'':String(t.val).replace('.',','),un:t.un||'',vlab:'Valor · '+t.t+(t.un?' ('+t.un+')':''),hasValIn:ed&&isM,hasValTx:!ed&&isM&&t.val!==''&&t.val!==undefined,valTx:t.val!==''&&t.val!==undefined?manN(t.val,2)+' '+(t.un||''):'',
      setval:(e)=>{ const val=e.target.value; ma_mud(self,c2=>manResp(c2,o.id,i,undefined,undefined,g2perfil(),val)); },
      tents:(t.tent||[]).map((x,j)=>({t:(j+1)+'ª tentativa · '+x.r+' · '+x.evid+' · '+x.por+' · '+x.em,st:ma_chipSt(x.r==='Aprovado'?'green':'red'),dot:ma_dotSt(x.r==='Aprovado'?'green':'red'),r:x.r})),hasTents:isT&&(t.tent||[]).length>0,
      tentEd:ed&&isT,tevid:f['te'+i]||'',tlab:'Evidência do teste · '+t.t,settevid:(e)=>maF(self,'te'+i,e.target.value),treg:!!pend,
      tgo:()=>{ const ff=self.state.pf||{}; const ev='foto (simulada)'+(String(ff['te'+i]||'').trim()?' · '+String(ff['te'+i]).trim():''); ma_cmd(self,c2=>manTentativa(c2,o.id,i,pend,ev,g2perfil()),(r)=>{ const f2=Object.assign({},self.state.pf||{}); delete f2['tr'+i]; delete f2['te'+i]; self.setState({pf:f2}); ma_rec(self,r); }); },
      tgot:'Anexar foto e registrar '+(pend||''),fixo:!!t.fixo}; });
  const pI=manPode(c,pf,'incluir',{o}); v.om_incPode=['Corretiva','Pendência'].indexOf(o.tipo)>=0&&MAN_ABERTAS.indexOf(o.etapa)>=0; v.om_incEd=v.om_incPode&&!pI; v.om_incWhy=v.om_incPode&&pI?pI:'';
  v.om_inc_tipos=MAN_TIPOS.map(x=>({v:x,t:x})); v.om_inct=f.itipo||'Serviço'; v.om_setinct=(e)=>maF(self,'itipo',e.target.value); v.om_incx=f.itxt||''; v.om_setincx=(e)=>maF(self,'itxt',e.target.value);
  v.om_inc=()=>{ const ff=self.state.pf||{}; ma_cmd(self,c2=>manIncluir(c2,o.id,ff.itipo||'Serviço',ff.itxt,g2perfil()),(r)=>{ const f2=Object.assign({},self.state.pf||{}); delete f2.itxt; self.setState({pf:f2}); ma_rec(self,r); }); };
  v.om_tkn=nr+' de '+o.chk.length+' respondidas';
  /* peças: Item · Planejado · Situação · Aplicado; retiradas com destino e responsável */
  v.om_pcs=(o.pecas||[]).map((p,i)=>{ const it=p.item?c.itens[p.item]:null; const disp=it?it.saldo-it.reservado:null; let s,cc; const nec=manNec(p);
    const rr=(p.rsv||[]).reduce((a,x)=>a+x.qtd,0); const dv=o.etapa==='Canceladas'?((o.canc||{}).dev||[]).find(x=>x.item===p.item&&p.item):null;
    /* D5: o chip curto diz a situação; a linha de baixo, a origem (pedido › recebimento › reserva › ordem) ou o motivo */
    let orig=(p.rsv||[]).map(x=>(x.pc?x.pc+' › ':'')+'recebimento '+x.rec+' ('+manBr(x.em)+') › reserva '+manN(x.qtd,1)+' '+p.un+' › '+o.id).join(' · ');
    if(dv){ s='Devolvida ao livre'; cc='gray'; orig='Reserva de '+manN(dv.qtd,1)+' '+p.un+' devolvida ao livre em '+manBr(o.canc.em)+' (cancelada: '+o.canc.motivo+')'+(dv.orig?' · recebimento '+dv.orig:''); }
    else if(o.etapa==='Canceladas'){ s='Sem reserva (cancelada)'; cc='gray'; }
    else if(p.sob>0){ s='Sobra '+manN(p.sob,1)+' '+p.un+' a devolver'; cc='yellow'; } else if(p.dev){ s='Aplicado '+manN(p.apl,1)+' · devolvido '+manN(p.dev,1)+' '+p.un; cc='green'; }
    else if(p.apl&&o.exec){ s='Aplicado '+manN(p.apl,1)+' '+p.un; cc='green'; }
    else if(p.res&&rr>0){ const fl=nec>1e-9&&disp<nec; s='Peça chegou · reservada'; cc=fl?'yellow':'green';
      if(nec>1e-9) orig='Reservada '+manN(p.res,1)+' de '+manN(p.qtd,1)+' '+p.un+(fl?' · falta '+manN(nec-Math.max(0,disp),1)+' '+p.un+(o.sc?' ('+o.sc.id+')':''):'')+' · '+orig; }
    else if(p.res){ s='Reservado '+manN(p.res,1)+' '+p.un; cc='green'; }
    else if(it&&disp<p.qtd){ const rt=manResTxt(c,p.item,o.id); s='Falta '+manN(p.qtd-Math.max(0,disp),1)+' '+p.un+(o.sc?' · '+o.sc.id:''); cc='red'; if(rt) orig=rt+': ninguém a usa em outra ordem'; } else if(it){ s='Livre '+manN(disp,1)+' '+p.un; cc='gray'; } else { s='Sem código no catálogo (1b)'; cc='gray'; }
    return {nome:p.nome,orig,hasOrig:!!orig,q:manN(p.qtd,1)+' '+p.un,s,st:ma_chipSt(cc),dot:ma_dotSt(cc),ed:exe&&!pE,ro:!(exe&&!pE),av:f['ap'+i]===undefined?'':f['ap'+i],aph:'vazio = '+manN(p.qtd,1),alab:'Aplicado · '+p.nome+' ('+p.un+')',un:p.un,
      apl:o.exec?manN(p.apl,1)+' '+p.un:'—',aset:(e)=>maF(self,'ap'+i,e.target.value)}; });
  v.om_temPc=v.om_pcs.length>0; v.om_semPc=!v.om_temPc;
  const pR=(manPode(c,pf,'executar',{o})&&manPode(c,pf,'ponte'))||'';
  v.om_rets=(o.retiradas||[]).map((r,i)=>({t:r.nome+' · '+manN(r.qtd)+' '+r.un,d:r.dest||'A definir',rs:r.resp||'—',ok:!!(r.dest&&r.dest!=='A definir'&&r.resp),st:ma_chipSt(r.dest&&r.dest!=='A definir'&&r.resp?'gray':'red'),dot:ma_dotSt(r.dest&&r.dest!=='A definir'&&r.resp?'gray':'red'),
    ed:!pR&&manAberta(o)&&o.etapa!=='A liberar'&&o.etapa!=='Liberadas',dests:['','Recondicionar','Garantia','Sucata'].map(x=>({v:x,t:x||'Destino'})),dv:f['rd'+i]!==undefined?f['rd'+i]:(r.dest==='A definir'?'':r.dest),
    setd:(e)=>maF(self,'rd'+i,e.target.value),rv:f['rr'+i]!==undefined?f['rr'+i]:(r.resp||''),setr:(e)=>maF(self,'rr'+i,e.target.value),dlab:'Destino · '+r.nome,rlab:'Responsável · '+r.nome,
    go:()=>{ const ff=self.state.pf||{}; const d=ff['rd'+i]!==undefined?ff['rd'+i]:(r.dest==='A definir'?'':r.dest), rs=ff['rr'+i]!==undefined?ff['rr'+i]:r.resp; ma_cmd(self,c2=>manRetirada(c2,o.id,i,d,rs,g2perfil()),(x)=>ma_rec(self,x)); }}));
  v.om_temRet=v.om_rets.length>0;
  /* conclusão: leitura pela função única; horas pelo chip "Previsto" ou digitadas (sem valor implícito, D-18) */
  v.om_conEd=exe&&!pE; v.om_hasCont=!!(a&&a.un); v.om_unl=a&&a.un==='km'?'Leitura do odômetro · km':'Leitura do horímetro · h'; v.om_leitv=f.leit||''; v.om_setleit=(e)=>maF(self,'leit',e.target.value);
  v.om_ult=a&&a.leit?('Última: '+manLeitTxt(a)+' · '+a.leit.origem):''; v.om_horas=f.horas||''; v.om_sethoras=(e)=>maF(self,'horas',e.target.value);
  v.om_prevt='Previsto ('+manN(o.tempo||0,1)+' h)'; v.om_prevOn=String(!!f.horas&&manNum(f.horas)===Number(o.tempo)); v.om_prevSt=ma_pill(!!f.horas&&manNum(f.horas)===Number(o.tempo)); v.om_prev=()=>maF(self,'horas',String(o.tempo||0).replace('.',','));
  v.om_exRo=!!o.exec; v.om_exkv=o.exec?[{l:'Concluída em',v:manBr(o.exec.data)},{l:'Leitura',v:(o.exec.leit!==null&&o.exec.leit!==undefined&&a&&a.un)?manQ(o.exec.leit,a.un):'—'},{l:'Horas de oficina',v:manN(o.exec.horas,1)+' h'}]:[];
  /* custo e tempos (função única) */
  v.om_kv=[{l:'Estimado',v:manRS(custoE)},{l:'Final',v:custoF!==null?manRS(custoF):'no encerramento'},{l:'Custo R$/h da oficina',v:manRS(c.custoh)},{l:'Tempo previsto',v:Number(o.tempo)>0?manN(o.tempo,1)+' h':'—'},
    {l:'Horas reais',v:o.exec?manN(o.exec.horas,1)+' h':'—'},{l:'Espera por peça · por equipe',v:'não calculável até o 1c'}];
  /* origem */
  v.om_orig=o.origem||'—'; v.om_achs=(o.achados||[]).map(x=>{ const q=c.achados[x]; return {t:x+(q?' · '+q.sint+' · '+q.estado:''),h:'#achado='+x,go:()=>ma_abrir(self,'achado',x)}; }); v.om_temAch=v.om_achs.length>0;
  v.om_hasPl=!!o.pid; v.om_plt=o.pid?('Abrir '+o.pid+' · a ordem segue na v'+o.ver+' ›'):''; v.om_goPl=()=>{ if(o.pid) ma_pg(self,'plano',o.pid); };
  return pr; }
'''

MA_JS+=r'''
/* ---------- painel do achado: a decisão é a triagem (o selo "Nova" sai) ---------- */
function ma_panAch(self,v,c,q,pf){ const st=self.state; const f=st.pf||{}; const a=c.ativos[q.aid];
  v.pan_t=q.id+' · '+(a?a.nome:''); v.pan_sub=q.origem+' · '+q.comp+' · '+(q.estado==='Na OM'?'na '+q.om:q.estado);
  v.ac_kv=[{l:'Sintoma',v:q.sint},{l:'Componente',v:q.comp},{l:'Origem',v:q.origem+(q.os?' · '+q.os:'')},{l:'Ocorrências',v:q.oc.length+' · '+q.oc.map(manBr).join(', ')},
    {l:'Evidência',v:q.evid||'Sem evidência'},{l:'Leitura',v:(q.leit!==''&&q.leit!==undefined&&a&&a.un)?manQ(q.leit,a.un):'—'},{l:'Condição sugerida',v:q.sug},{l:'Registrado por',v:(q.por||'—')+' · '+manBr(q.em)},
    {l:'Responsável técnico',v:manRtTxt(a)},{l:'Estado',v:(q.estado==='Na OM'?'Na '+q.om:q.estado)+(q.voltou&&q.estado==='Sem ordem'?' · voltou da '+q.voltou:'')+(q.mot?' · '+q.mot:'')}];
  v.ac_semEvid=!q.evid; v.ac_nova=!!q.nova;
  const pd=manPode(c,pf,'decidir'); const ed=q.estado==='Sem ordem'&&!pd;
  v.ac_crit=['Alta','Média','Baixa'].map(x=>({t:x,on:String(q.crit===x),st:ma_pill(q.crit===x),dis:!ed,go:()=>{ if(ed) manMudar(self,c2=>manAchCrit(c2,q.id,x,g2perfil())); }}));
  v.ac_atv=a?(a.nome+' · '+ma_condTxt(c,a)):'—'; v.ac_mudar=()=>ma_abrir(self,'cond',q.aid); v.ac_temOm=q.estado==='Na OM'&&!!q.om; v.ac_omt='Abrir '+q.om+' ›'; v.ac_goOm=()=>ma_abrir(self,'om',q.om);
  if(q.estado!=='Sem ordem') return {P:null,S:[]};
  const op=manAchOpcoes(c,q.id); const vai=(r)=>{ if(r&&r.id) { ma_abrir(self,'om',r.id); ma_rec(self,r,null); } };
  const exe=(x)=>{ if(x.k==='vincular') return ()=>ma_cmd(self,c2=>manAchVincular(c2,q.id,x.om,g2perfil()),vai);
    if(x.k==='gerar') return ()=>ma_cmd(self,c2=>manAchGerar(c2,q.id,g2perfil(),self.state.pchave),vai);
    if(x.k==='corretiva') return ()=>ma_cmd(self,c2=>manAchCorretiva(c2,q.id,g2perfil(),self.state.pchave),vai);
    return ()=>self.setState({paviso:{t:'Fechar '+q.id+' sem serviço: informe o motivo (PRD 54.4).',campo:'fmot',lab:'Motivo',ok:{t:'Fechar sem serviço',fn:()=>{ const m=(self.state.pf||{}).fmot; ma_cmd(self,c2=>manAchFechar(c2,q.id,m,g2perfil()),(r)=>ma_rec(self,r)); }},no:'Voltar'}}); };
  return {P:ma_btn(op.prim.t,exe(op.prim),pd,true),S:op.sec.map(x=>ma_btn(x.t,exe(x),pd,false))}; }
/* ---------- painel do vencimento ---------- */
function ma_panVenc(self,v,c,id,pf){ const q=String(id).split('|'); const l=manLinhas(c,q[0]).find(x=>x.aid===q[1]&&x.sid===q[2]);
  if(!l||!l.s){ v.pan_t='Vencimento'; v.pan_sub='Não encontrado'; v.vc_calc=''; return {P:null,S:[]}; }
  const a=l.a, s=l.s, x=l.x, g=x.gats[x.prim]; v.pan_t=l.pid+' · '+s.nome+' · '+a.nome; v.pan_sub=x.sit+(x.sit==='Vencida'?' · '+manSitTxt(c,x):'');
  const ref=l.ref; const parts=x.gats.map(gg=>gg.u==='d'?('ou '+manBr(gg.due)+' ('+manN(s.gat.d)+' dias após '+manBr(ref.data)+')'):(manQ(gg.due,gg.u)+' = '+manQ(ref.leit,gg.u)+' + '+manQ(s.gat[gg.u],gg.u)+(a.leit?' · leitura '+manQ(a.leit.val,a.un)+' em '+manBr(a.leit.data):'')));
  v.vc_calc=parts.join(' · ')+(manPrimTxt(x)?' · '+manPrimTxt(x):'');
  v.vc_kv=[{l:'Tolerância',v:manTolTxt(s)||'sem tolerância'},{l:'Início da janela',v:isFinite(manIniJanela(x))?(manIniJanela(x)<=0?'aberta':'em '+Math.ceil(manIniJanela(x))+' d'):'—'},
    {l:'Cumpre também',v:(s.cumpre||[]).map(id2=>(manPub(l.p).find(y=>y.id===id2)||{}).nome).filter(Boolean).join(', ')||'—'},{l:'Versão',v:l.pid+' v'+l.p.versao},{l:'Última execução',v:manBr(ref.data)+(ref.leit!==null&&ref.leit!==undefined&&a.un?' · '+manQ(ref.leit,a.un):'')+(ref.om?' · '+ref.om:'')},
    {l:'Tempo · especialidade',v:manN(s.tempo,1)+' h · '+s.esp}];
  v.vc_pecas=(s.pecas||[]).map(y=>{ const it=c.itens[y.item]||{nome:y.item,un:'',saldo:0,reservado:0}; const d=it.saldo-it.reservado; return {t:it.nome+' · '+manN(y.qtd,1)+' '+it.un,s:(d>=y.qtd?'livre ':'falta · livre ')+manN(d,1)+' '+it.un,st:ma_chipSt(d>=y.qtd?'gray':'red'),dot:ma_dotSt(d>=y.qtd?'gray':'red')}; });
  v.vc_temPc=v.vc_pecas.length>0; v.vc_plt='Abrir '+l.pid+' ›'; v.vc_goPl=()=>ma_pg(self,'plano',l.pid);
  v.vc_temOm=!!(l.om||l.dup); const om=l.om||l.dup; v.vc_omt=om?('Abrir '+om.id+' · '+om.etapa+' ›'):''; v.vc_goOm=()=>{ if(om) ma_abrir(self,'om',om.id); };
  v.vc_emDia=!manDevida(l)&&!om; v.vc_emDiat='Em dia: a ordem é gerada quando a janela se aproximar (PRD CAL-06).';
  if(om||!manDevida(l)) return {P:null,S:[]};
  return {P:ma_btn('Gerar ordem preventiva',()=>ma_cmd(self,c2=>manGerar(c2,l.vk,l.sid,g2perfil()),(r)=>{ if(r.id){ ma_abrir(self,'om',r.id); ma_rec(self,r); } }),manPode(c,pf,'gerar'),true),S:[]}; }
/* ---------- painel Condição (CMD-18; Restringir com prazo; Encerrar restrição; responsável técnico) ---------- */
function ma_panCond(self,v,c,a,pf){ const st=self.state; const f=st.pf||{}; const i=a.condInfo||{};
  v.pan_t='Condição · '+a.nome; v.pan_sub=ma_condTxt(c,a)+(i.motivo?' · '+i.motivo:'')+' · responsável técnico: '+manRtTxt(a);
  const acs=[]; if(a.cond!=='Bloqueado') acs.push(['bloquear','Bloquear']); if(a.cond==='Apto') acs.push(['restringir','Restringir']);
  if(a.cond==='Restrito') acs.push(['encerrar','Encerrar restrição']); acs.push(['rt','Trocar responsável técnico']);
  const ac=acs.find(x=>x[0]===f.acao)?f.acao:acs[0][0];
  v.cd_acoes=acs.map(([k,t])=>({t,on:String(ac===k),st:ma_pill(ac===k),go:()=>maF(self,'acao',k)}));
  const ms=manMots(a); v.cd_bloqTxt=a.cond==='Bloqueado'?('Bloqueado → Apto só por “Declarar apto” na ordem que trata cada motivo, com teste aprovado (CMD-19)'+(ms.length?': '+ms.map(m=>m.motivo+' · '+manMotTxt(c,m)).join(' | '):'')+'. Um defeito novo entra por Registrar achado → “Registrar e bloquear” e soma um motivo.'):'';
  v.cd_isB=ac==='bloquear'; v.cd_isR=ac==='restringir'; v.cd_isE=ac==='encerrar'; v.cd_isT=ac==='rt';
  ['motivo','evid','lim','ate','achado','om','rt'].forEach(k=>{ v['cd_'+k]=f[k]||''; v['cd_set'+k]=(e)=>maF(self,k,e.target.value); });
  v.cd_achs=[{v:'',t:'Sem achado de origem'}].concat(Object.values(c.achados).filter(q=>q.aid===a.id&&(q.estado==='Sem ordem'||q.estado==='Na OM')).map(q=>({v:q.id,t:q.id+' · '+q.sint})));
  const oms=Object.values(c.oms).filter(o=>o.aid===a.id&&MAN_ABERTAS.indexOf(o.etapa)>=0); v.cd_oms=[{v:'',t:'Sem ordem que trate (o detalhe pedirá Criar ordem corretiva)'}].concat(oms.map(o=>({v:o.id,t:'Tratar na '+o.id+' · '+o.serv+' · '+o.etapa})));
  v.cd_temOms=oms.length>0; v.cd_rts=MAN_PES.map(p=>({v:p.k,t:p.k+' · '+p.f+(p.nr.length?' · '+p.nr.join(', '):'')}));   /* S4: pessoas do CD-04 (habilitação), não uma lista paralela */
  v.cd_hist=(a.condHist||[]).slice(-5).reverse().map(h=>({t:manBr(h.em)+' · '+h.cond+' · '+h.motivo+(h.por?' · '+h.por:'')+(h.om?' · '+h.om:'')}));
  const pod=manPode(c,pf,'condicao',{aid:a.id});
  const go=(acao,d)=>ma_cmd(self,c2=>manCondicao(c2,a.id,acao,d,g2perfil()),(r)=>{ self.setState({pf:{}}); ma_rec(self,r); });
  const D=()=>Object.assign({},self.state.pf||{});
  if(ac==='bloquear') return {P:ma_btn('Bloquear '+a.nome,()=>go('bloquear',D()),pod,true),S:[]};
  if(ac==='restringir') return {P:ma_btn('Restringir '+a.nome,()=>go('restringir',D()),pod,true),S:[]};
  if(ac==='encerrar') return {P:ma_btn('Encerrar restrição',()=>go('encerrar',D()),pod,true),S:[]};
  return {P:ma_btn('Trocar responsável técnico',()=>go('rt',D()),pod,true),S:[]}; }
/* ---------- painel da leitura / lançamento: decisão da leitura a confirmar e estorno ---------- */
function ma_panLeit(self,v,c,id,pf){ const lt=(c.leituras||[]).find(x=>x.id===id); const b=(c.abast||[]).find(x=>x.id===id||(lt&&lt.ab&&x.id===lt.ab));
  const L=lt||(b&&b.lt?(c.leituras||[]).find(x=>x.id===b.lt):null); const aid=(L&&L.aid)||(b&&b.aid); const a=c.ativos[aid];
  if(!a){ v.pan_t='Leitura'; v.pan_sub='Não encontrada'; return {P:null,S:[]}; }
  v.pan_t=(b?b.id:(L?L.id:''))+' · '+a.nome; v.pan_sub=b?(b.tipo?('Estorno de '+b.ref):('Abastecimento · '+manN(b.vol)+' L · '+b.tq)):('Leitura · '+(L?L.origem:''));
  v.lt_kv=(b?[{l:'Volume',v:manN(b.vol)+' L'},{l:'Tanque/lote',v:b.tq},{l:'Operador',v:b.op},{l:'Evidência',v:b.evid||'sem evidência'},{l:'Método',v:manLh(c,b)?('Tanque cheio · '+manConsTxt(manLh(c,b))+(manLh(c,b).n>1?' ('+manLh(c,b).n+' lançamentos desde o cheio anterior)':'')):(b.cheio?'Tanque cheio (sem anterior)':'Estimada')},{l:'Registrado por',v:b.por||'—'}].concat(b.motivo?[{l:'Motivo',v:b.motivo}]:[]):[])
    .concat(L?[{l:'Leitura',v:manQ(L.val,L.un)+' · '+manBr(L.data)},{l:'Origem',v:L.origem},{l:'Qualidade',v:L.qual}]:[]).concat([{l:'Leitura atual do ativo',v:manLeitTxt(a)}]);
  const pend=a.suspeita&&((L&&a.suspeita.lt===L.id)||(b&&a.suspeita.ab===b.id)); const pd=manPode(c,pf,'leituraDecidir');
  const S=[]; let P=null;
  if(pend){ P=ma_btn(a.suspeita.tipo==='menor'?'Confirmar troca de contador':('Confirmar leitura '+manQ(a.suspeita.val,a.un)),()=>ma_cmd(self,c2=>manLeituraOk(c2,a.id,g2perfil()),(r)=>ma_rec(self,r)),pd,true);
    S.push(ma_btn('Descartar',()=>ma_cmd(self,c2=>manLeituraDescartar(c2,a.id,g2perfil()),(r)=>ma_rec(self,r)),pd,false)); }
  if(b&&!b.tipo&&b.qual!=='Estornado') S.push(ma_btn('Corrigir com estorno',()=>self.setState({paviso:{t:'Estornar '+b.id+': o original fica no histórico e o estorno é um lançamento novo; depois registre o correto.',campo:'emot',lab:'Motivo do estorno',
    ok:{t:'Estornar '+b.id,fn:()=>{ const m=(self.state.pf||{}).emot; ma_cmd(self,c2=>manEstornar(c2,b.id,m,g2perfil(),self.state.pchave),(r)=>ma_rec(self,r)); }},no:'Voltar'}}),manPode(c,pf,'estorno'),false));
  return {P,S}; }
/* ---------- Registrar achado (Sem ordem e detalhe do ativo; app MB-04 pela mesma função) ---------- */
function ma_panNovoAch(self,v,c,pf){ const st=self.state; const f=st.pf||{}; v.pan_t='Registrar achado'; v.pan_sub='Prefixo pela origem: Relato e Alerta → SM · Inspeção → INSP (D-48).';
  v.na_ativos=[{v:'',t:'Escolha o ativo'}].concat(c.ordem.map(id=>c.ativos[id]).map(a=>({v:a.id,t:manNome(a)+' · '+a.local}))); v.na_aid=f.aid||''; v.na_setaid=(e)=>maF(self,'aid',e.target.value);
  const one=(k,lst)=>lst.map(x=>({t:x,on:String(f[k]===x),st:ma_pill(f[k]===x),go:()=>maF(self,k,f[k]===x?'':x)}));
  v.na_orig=one('origem',['Relato','Inspeção','Alerta']); v.na_comp=one('comp',MAN_COMP); v.na_crit=one('crit',['Alta','Média','Baixa']); v.na_sug=one('sug',['Apto','Restrito','Bloqueado']);
  v.na_sint=f.sint||''; v.na_setsint=(e)=>maF(self,'sint',e.target.value); v.na_leit=f.leit||''; v.na_setleit=(e)=>maF(self,'leit',e.target.value);
  const a=c.ativos[f.aid]; v.na_hasCont=!!(a&&a.un); v.na_un=a&&a.un?a.un:''; v.na_ult=a&&a.leit?('Última: '+manLeitTxt(a)):''; v.na_rt=a?('Responsável técnico: '+manRtTxt(a)):'';
  v.na_evid=f.evid||''; v.na_foto=()=>maF(self,'evid',f.evid?'':'foto (simulada)'); v.na_fotot=f.evid?'Remover foto':'Anexar foto (simulado)'; v.na_semEvid=!f.evid;
  const ab=a&&f.comp?manAchAberto(c,a.id,f.comp):null; v.na_rep=!!ab; v.na_rept=ab?('Possível repetição de '+ab.id+' · '+ab.sint+' ('+ab.oc.length+(ab.oc.length>1?' ocorrências':' ocorrência')+')'):'';
  const pd=manPode(c,pf,'registrar'); const pb=a?manPode(c,pf,'condicao',{aid:a.id}):'x';
  const go=(rep,bloq)=>ma_cmd(self,c2=>manAchRegistrar(c2,Object.assign({},self.state.pf||{},{rep,bloquear:bloq}),g2perfil(),self.state.pchave),(r)=>{ if(r.id){ self.setState({pf:{}}); ma_abrir(self,'achado',r.id); ma_rec(self,r); } });
  const sobe=ab?manAchSobe(ab,f):[]; v.na_rept=ab?(v.na_rept+(sobe.length?' · a nova é mais grave: somar eleva '+sobe.join(' e '):'')):'';   /* A2: somar nunca perde a gravidade */
  if(ab&&f.sug==='Bloqueado'&&!pb&&a&&!manMots(a).some(m=>m.achado===ab.id)) return {P:ma_btn('Somar ao '+ab.id+' e bloquear',()=>go('somar',true),pd,true),S:[ma_btn('Só somar',()=>go('somar',false),pd,false),ma_btn('Registrar novo',()=>go('novo',true),pd,false)]};
  if(ab) return {P:ma_btn('Somar ao '+ab.id,()=>go('somar',false),pd,true),S:[ma_btn('Registrar novo',()=>go('novo',f.sug==='Bloqueado'&&!pb),pd,false)]};
  if(f.sug==='Bloqueado'&&!pb) return {P:ma_btn('Registrar e bloquear',()=>go('',true),pd,true),S:[ma_btn('Só registrar',()=>go('',false),pd,false)]};
  return {P:ma_btn('Registrar achado',()=>go('',false),pd,true),S:[]}; }
/* ---------- Registrar abastecimento: herda ativo, data e operador da alocação; "Salvar e registrar outro" limpa tudo menos a data ---------- */
function ma_panAb(self,v,c,pf){ const st=self.state; const f=st.pf||{}; v.pan_t='Registrar abastecimento'; v.pan_sub='Um lançamento por tíquete · leitura nunca pré-preenchida (D-19).';
  v.ab_ativos=[{v:'',t:'Escolha o ativo'}].concat(c.ordem.map(id=>c.ativos[id]).filter(a=>a.un).map(a=>({v:a.id,t:manNome(a)+' · '+manLeitTxt(a)})));
  const a=c.ativos[f.aid]; v.ab_aid=f.aid||'';
  v.ab_setaid=(e)=>{ const aid=e.target.value; const g=manGet(); const tq=aid?manTanques(g,aid):[]; const ff=Object.assign({},self.state.pf||{},{aid,tq:tq.length===1?tq[0]:'',op:aid?manOperadorDia(g,aid,(self.state.pf||{}).data||g.hoje):''}); self.setState({pf:ff}); };
  const dts=[['Hoje',c.hoje],['Ontem',manAdd(c.hoje,-1)]]; v.ab_datas=dts.map(([t,d])=>({t,on:String(f.data===d),st:ma_pill(f.data===d),go:()=>{ const ff=Object.assign({},self.state.pf||{},{data:d}); if(ff.aid) ff.op=manOperadorDia(manGet(),ff.aid,d)||ff.op; self.setState({pf:ff}); }}));
  v.ab_data=f.data||c.hoje; v.ab_setdata=(e)=>maF(self,'data',e.target.value); v.ab_max=c.hoje;
  const tqs=a?manTanques(c,a.id):MAN_TQ.map(t=>t.id); v.ab_tqs=tqs.map(t=>({t,on:String(f.tq===t),st:ma_pill(f.tq===t),go:()=>maF(self,'tq',f.tq===t?'':t)}));
  v.ab_vol=f.vol||''; v.ab_setvol=(e)=>maF(self,'vol',e.target.value); v.ab_leit=f.leit||''; v.ab_setleit=(e)=>maF(self,'leit',e.target.value);
  v.ab_un=a&&a.un?a.un:''; v.ab_ult=a&&a.leit?('Última: '+manLeitTxt(a)):''; v.ab_hasCont=!!(a&&a.un);
  const opd=a?manOperadorDia(c,a.id,f.data||c.hoje):''; v.ab_opsug=opd?('Operador da alocação em '+manBr(f.data||c.hoje)+': '+opd+' · corrigível'):(a?'Sem alocação neste dia: escolha o operador.':'');
  v.ab_ops=MAN_OPS.map(x=>({t:x,on:String(f.op===x),st:ma_pill(f.op===x),go:()=>maF(self,'op',f.op===x?'':x)}));
  v.ab_cheio=!!f.cheio; v.ab_setcheio=(e)=>maF(self,'cheio',!!e.target.checked); v.ab_foto=()=>maF(self,'evid',f.evid?'':'foto (simulada)'); v.ab_fotot=f.evid?'Remover foto':'Anexar foto (simulado)'; v.ab_evid=f.evid||'sem evidência';
  const pd=manPode(c,pf,'registrar');
  const go=(outro)=>ma_cmd(self,c2=>manAbastecer(c2,Object.assign({},self.state.pf||{}),g2perfil(),self.state.pchave),(r)=>{ if(outro){ self.setState({pf:{aid:'',data:(self.state.pf||{}).data||manGet().hoje,tq:'',vol:'',leit:'',op:'',evid:'',cheio:false},rec:{msg:r.msg,prox:null}}); }
    else { self.setState({pf:{}}); ma_abrir(self,'leitura',r.id); ma_rec(self,r); } });
  return {P:ma_btn('Registrar abastecimento',()=>go(false),pd,true),S:[ma_btn('Salvar e registrar outro',()=>go(true),pd,false)]}; }
function ma_panNovaLeit(self,v,c,pf){ const st=self.state; const f=st.pf||{}; v.pan_t='Registrar leitura'; v.pan_sub='Mesma função do abastecimento, da conclusão e do achado (D-40).';
  v.nl_ativos=[{v:'',t:'Escolha o ativo'}].concat(c.ordem.map(id=>c.ativos[id]).filter(a=>a.un).map(a=>({v:a.id,t:manNome(a)+' · '+manLeitTxt(a)}))); v.nl_aid=f.aid||''; v.nl_setaid=(e)=>maF(self,'aid',e.target.value);
  const a=c.ativos[f.aid]; v.nl_un=a&&a.un?a.un:''; v.nl_ult=a&&a.leit?('Última: '+manLeitTxt(a)):''; v.nl_leit=f.leit||''; v.nl_setleit=(e)=>maF(self,'leit',e.target.value);
  v.nl_data=f.data||c.hoje; v.nl_setdata=(e)=>maF(self,'data',e.target.value); v.nl_max=c.hoje;
  return {P:ma_btn('Registrar leitura',()=>ma_cmd(self,c2=>manLeituraAvulsa(c2,(self.state.pf||{}).aid,(self.state.pf||{}).leit,(self.state.pf||{}).data,g2perfil(),self.state.pchave),(r)=>{ self.setState({pf:{}}); ma_rec(self,r); }),manPode(c,pf,'registrar'),true),S:[]}; }
/* painel modal: Tab e Shift+Tab giram dentro; Esc e Tab valem também com o foco fora do painel aberto */
function ma_focaveis(root){ return root?[...root.querySelectorAll('button,a[href],input,select,textarea,[tabindex]:not([tabindex="-1"])')].filter(x=>!x.disabled&&x.getClientRects().length):[]; }
function ma_trap(e,root){ if(!e||e.key!=='Tab'||!root) return; const f=ma_focaveis(root); if(!f.length) return; const a=document.activeElement;
  if(!root.contains(a)){ e.preventDefault(); f[0].focus(); return; }
  if(e.shiftKey&&(a===f[0]||a===root)){ e.preventDefault(); f[f.length-1].focus(); } else if(!e.shiftKey&&a===f[f.length-1]){ e.preventDefault(); f[0].focus(); } }
function ma_modalDoc(self,get){ if(self.__maModal) return; self.__maModal=true;
  try{ document.addEventListener('keydown',(e)=>{ const m=get(); if(!m||!m.root) return; if(m.root.contains(e.target)) return;
    if(e.key==='Escape'){ e.preventDefault(); m.close(); } else if(e.key==='Tab') ma_trap(e,m.root); }); }catch(err){} }
'''

# =====================================================================================
# Planos (visão Planos + página do plano #plano=): rascunho, versão, publicar, travas do serviço e do vínculo (regra de hoje, moldura nova)
PM_JS=r'''
const PM_GR=['Tratores','Pulverizadores','Plantadeiras','Colhedoras','Implementos','Irrigação','Beneficiamento','Armazenagem','Veículos'];
const PM_CC={green:['#1E7A4C','#E4F3E9'],yellow:['#8A5A00','#FFF3D6'],red:['#B42318','#FDE8E6'],gray:['#5B6660','#EEF1EE']};
function pmChip(c){ const k=PM_CC[c]||PM_CC.gray; return 'display:inline-flex;align-items:center;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:700;white-space:nowrap;color:'+k[0]+';background:'+k[1]+';'; }
const PM_IN='font-family:inherit;font-size:13.5px;padding:8px 10px;border-radius:9px;box-sizing:border-box;width:100%;background:#fff;color:#15201A;';
const PM_BASE={exec:'Data e leitura da execução',prog:'Vencimento programado'};
function pmPlans(c){ return c.ordemPlanos.map(id=>c.planos[id]).filter(Boolean); }
function pmEst(p){ if(p.estado==='Inativo') return ['Inativo','gray']; if(!p.versao) return ['Rascunho v1','yellow']; if(p.rasc) return ['Publicado v'+p.versao+' · Rascunho v'+p.rasc.v+' em edição','yellow']; return ['Publicado v'+p.versao,'green']; }
function pmVincs(c,pid){ return Object.keys(c.vinc).filter(k=>k.split('|')[0]===pid&&manVincVale(c.vinc[k])); }
function pmSemPlano(c){ return c.ordem.map(id=>c.ativos[id]).filter(a=>manAtvAtivo(a)&&!Object.keys(c.vinc).some(k=>k.split('|')[1]===a.id&&manVincVale(c.vinc[k]))&&!pmPlans(c).some(p=>p.estado!=='Inativo'&&manCabe(c,p,a))); }
function pmCands(c,p){ return c.ordem.map(id=>c.ativos[id]).filter(a=>manAtvAtivo(a)&&manCabe(c,p,a)&&!manVincVale(c.vinc[p.id+'|'+a.id])); }
function pmUnits(c,p){ const u={n:0}; c.ordem.forEach(id=>{ const a=c.ativos[id]; if(a&&(manCabe(c,p,a)||manVincVale(c.vinc[p.id+'|'+a.id]))){ u.n++; if(a.un) u[a.un]=1; } }); return u; }
function pmNum(x){ const t=String(x===undefined||x===null?'':x).trim(); if(!t) return null; const n=Number(t.replace(/\./g,'').replace(',','.')); return isNaN(n)?NaN:n; }
function pmFoco(id,alt){ setTimeout(()=>{ const e=document.getElementById(id)||(alt&&document.getElementById(alt)); if(e) e.focus(); },0); }
function pmRet(self){ const r=document.activeElement; if(!self.state.sv&&!self.state.np&&!self.state.vl&&!self.state.dv) self.__pmRet=(r&&r!==document.body&&!(r.closest&&r.closest('aside')))?r:null; }
function pmBack(self){ setTimeout(()=>{ const r=self.__pmRet; self.__pmRet=null; if(r&&document.contains(r)) r.focus(); },0); }
function pmSit(c,p){ if(p.estado==='Inativo') return {t:'Inativo · não gera vencimentos',c:'gray'}; if(!p.versao) return {t:'Publique para gerar vencimentos',c:'gray'};
  const ls=manLinhas(c,p.id).filter(l=>l.s); if(!ls.length) return {t:'Sem ativos vinculados',c:'gray'};
  const n={}; ls.forEach(l=>{ n[l.x.sit]=(n[l.x.sit]||0)+1; });
  const T={'Vencida':['vencida','vencidas'],'Vence em breve':['vence em breve','vencem em breve'],'Em dia':['em dia','em dia']}; const ord=['Vencida','Vence em breve','Em dia'];
  const w=ord.find(k=>n[k]); return {t:ord.filter(k=>n[k]).map(k=>n[k]+' '+T[k][n[k]>1?1:0]).join(' · '),c:MAN_SITC[w]||'gray'}; }
function pmPid(self){ const pg=self.state.pg; return pg&&pg.k==='plano'?pg.id:null; }
/* edição grava no rascunho v(n+1); plano ainda sem versão publicada edita a própria v1 */
function pmEdit(self,pid,fn){ return manMudar(self,c=>{ manExige(c,g2perfil(),'plano'); const p=c.planos[pid]; const novo=!!p.versao&&!p.rasc; if(novo) p.rasc={v:p.versao+1,servicos:manClone(p.servicos)};
  const r=fn(c,p,manWork(p))||{}; const fim=novo?(' Rascunho v'+p.rasc.v+' criado; a v'+p.versao+' publicada e as ordens abertas não mudam.'):(p.versao?' Gravado no rascunho v'+p.rasc.v+'.':' Gravado na v1 (rascunho).');
  return {msg:(r.msg||'Salvo.')+fim,st:r.st}; }); }
function pmTkKey(t){ const q=manTk(t); return q.t+'|'+(q.tipo||'Serviço'); }
function pmDiff(c,p){ const out=[]; const w=manWork(p); const nt=(s)=>s.tarefas.length+(s.tarefas.length===1?' tarefa':' tarefas');
  if(!p.versao){ w.forEach(s=>out.push({k:'Incluído',c:'green',n:s.nome,t:manGatTxt(s)+' · '+nt(s)})); return out; }
  if(!p.rasc) return out; const pub={}; p.servicos.forEach(s=>{ pub[s.id]=s; }); const seen={};
  const pn=(x)=>{ const it=c.itens[x.item]||{nome:x.item,un:''}; return it.nome+' '+manN(x.qtd,1)+' '+it.un; };
  w.forEach(s=>{ seen[s.id]=1; const o=pub[s.id]; if(!o){ out.push({k:'Incluído',c:'green',n:s.nome,t:manGatTxt(s)+' · '+nt(s)}); return; }
    const ch=[]; if(o.nome!==s.nome) ch.push('nome: '+o.nome+' → '+s.nome); if(manGatTxt(o)!==manGatTxt(s)) ch.push(manGatTxt(o)+' → '+manGatTxt(s));
    if(manTolTxt(o)!==manTolTxt(s)) ch.push('tolerância: '+(manTolTxt(o)||'—')+' → '+(manTolTxt(s)||'—'));
    if((o.base||'exec')!==(s.base||'exec')) ch.push('próximo ciclo conta de: '+PM_BASE[s.base||'exec'].toLowerCase());
    if((o.cumpre||[]).join()!==(s.cumpre||[]).join()) ch.push('cumpre também: '+((s.cumpre||[]).map(id=>(w.find(x=>x.id===id)||{}).nome).filter(Boolean).join(', ')||'nenhum'));
    if(Number(o.tempo)!==Number(s.tempo)) ch.push('tempo: '+manN(o.tempo,1)+' → '+manN(s.tempo,1)+' h'); if(o.esp!==s.esp) ch.push('especialidade: '+o.esp+' → '+s.esp);
    const ok=o.tarefas.map(pmTkKey), sk=s.tarefas.map(pmTkKey);
    s.tarefas.forEach((t,i)=>{ if(ok.indexOf(sk[i])<0) ch.push('inclui tarefa “'+manTkT(t)+'” ('+(manTk(t).tipo||'Serviço')+')'); }); o.tarefas.forEach((t,i)=>{ if(sk.indexOf(ok[i])<0) ch.push('retira tarefa “'+manTkT(t)+'”'); });
    const om={}; (o.pecas||[]).forEach(x=>{ om[x.item]=x; }); const sm={}; (s.pecas||[]).forEach(x=>{ sm[x.item]=x; });
    (s.pecas||[]).forEach(x=>{ const y=om[x.item]; if(!y) ch.push('inclui '+pn(x)); else if(Number(y.qtd)!==Number(x.qtd)) ch.push(pn(y)+' → '+manN(x.qtd,1)); });
    (o.pecas||[]).forEach(y=>{ if(!sm[y.item]) ch.push('retira '+pn(y)); });
    if(ch.length) out.push({k:'Alterado',c:'yellow',n:s.nome,t:ch.join(' · ')}); });
  p.servicos.forEach(o=>{ if(!seen[o.id]) out.push({k:'Excluído',c:'red',n:o.nome,t:manGatTxt(o)}); });
  return out; }
function pmFld(self,v,pre,k,isChk){ const st=self.state[pre]; const e=(st.errs||{})[k]||'';
  v[pre+'_'+k]=st.d[k]; v[pre+'_e'+k]=e; v[pre+'_he'+k]=!!e; v[pre+'_st'+k]=PM_IN+'border:1px solid '+(e?'#B42318':'#E4E9E5')+';';
  v[pre+'_set'+k]=(ev)=>{ const cur=self.state[pre]; if(!cur) return; const val=isChk?!!ev.target.checked:ev.target.value; const d=Object.assign({},cur.d,{[k]:val}); const er=Object.assign({},cur.errs||{}); delete er[k];
    self.setState({[pre]:Object.assign({},cur,{d,errs:er,warn:false})}); }; }
function pmPanel(self,v,pre,o){ const st=self.state[pre]; v[pre+'_open']=!!st; if(!st){ v[pre+'_titulo']=''; v[pre+'_sub']=''; return false; }
  const fim=()=>{ self.setState({[pre]:null}); pmBack(self); };
  const close=()=>{ const cur=self.state[pre]; if(cur&&JSON.stringify(cur.d)!==cur.orig&&!cur.warn){ self.setState({[pre]:Object.assign({},cur,{warn:true})}); return; } fim(); };
  self['__pmClose_'+pre]=close; ma_modalDoc(self,()=>{ const q=['sv','np','vl','dv'].find(x=>self.state[x]); return q?{root:document.getElementById(q+'-painel'),close:()=>self['__pmClose_'+q]()}:null; });
  v[pre+'_titulo']=o.titulo; v[pre+'_sub']=o.sub; v[pre+'_close']=close;
  v[pre+'_key']=(e)=>{ if(!e) return; if(e.key==='Escape'){ e.preventDefault(); close(); } else ma_trap(e,document.getElementById(pre+'-painel')); };
  v[pre+'_save']=o.save; v[pre+'_warn']=!!st.warn; v[pre+'_discard']=fim; v[pre+'_keep']=()=>self.setState({[pre]:Object.assign({},self.state[pre],{warn:false})});
  v[pre+'_nerr']=Object.keys(st.errs||{}).length>0; return true; }
/* ---------- serviço (gatilhos, tolerância, base, cumpre também, tempo, especialidade) ---------- */
function pmSvOpen(self,c,p,sid){ pmRet(self); const s=sid?manWork(p).find(x=>x.id===sid):null; const g=s?s.gat:{}, t=s?(s.tol||{}):{};
  const f=(n)=>(n===undefined||n===null||n==='')?'':String(n).replace('.',',');
  const d={nome:s?s.nome:'',h:f(g.h),km:f(g.km),d:f(g.d),th:f(t.h),tkm:f(t.km),td:f(t.d),base:s?(s.base||'exec'):'exec',cumpre:s?(s.cumpre||[]).slice():[],tempo:s?f(s.tempo):'',esp:s?s.esp:''};
  self.setState({sv:{pid:p.id,sid:sid||null,d,orig:JSON.stringify(d),errs:{},warn:false},np:null,vl:null,dv:null,pan:null}); pmFoco('sv_nome'); }
function pmSvSave(self){ const st=self.state.sv; const d=st.d; const errs={}; const c=manGet(); const p=c.planos[st.pid]; const U=pmUnits(c,p);
  if(!String(d.nome).trim()) errs.nome='Informe o nome do serviço.'; else if(manWork(p).some(x=>x.id!==st.sid&&x.nome.toLowerCase()===String(d.nome).trim().toLowerCase())) errs.nome='Já existe um serviço com este nome no plano.';
  else { const dup=pmVincs(c,p.id).map(k=>{ const aid=k.split('|')[1]; const x=manDupServ(c,p.id,aid,[String(d.nome).trim()]); return x?(manNome(c.ativos[aid])+' já faz '+x.s+' pelo '+x.pid+'.'):''; }).find(Boolean); if(dup) errs.nome=dup; }
  const g={}, t={}; [['h','th'],['km','tkm'],['d','td']].forEach(([k,tk])=>{ const n=pmNum(d[k]), m=pmNum(d[tk]);
    if(n!==null){ if(isNaN(n)||n<=0) errs[k]='Maior que zero.'; else g[k]=n; }
    if(m!==null){ if(isNaN(m)||m<0) errs[tk]='Zero ou mais.'; else if(!n) { if(m>0) errs[tk]='Informe o intervalo.'; } else if(m>=n) errs[tk]='Menor que o intervalo.'; else t[k]=m; } });
  if(!Object.keys(g).length&&!errs.h&&!errs.km&&!errs.d) errs.h='Informe ao menos um gatilho: horas, km ou dias.';
  if(g.km&&U.n&&!U.km) errs.km='Nenhum ativo deste plano tem odômetro.';
  if(g.h&&U.n&&!U.h) errs.h='Nenhum ativo deste plano tem horímetro.';
  const tempo=pmNum(d.tempo); if(tempo===null||isNaN(tempo)||tempo<=0) errs.tempo='Informe o tempo em horas.';
  if(!d.esp) errs.esp='Escolha a especialidade.';
  if(Object.keys(errs).length){ self.setState({sv:Object.assign({},st,{errs,warn:false})}); return; }
  pmEdit(self,p.id,(c2,p2,w)=>{ let s=st.sid?w.find(x=>x.id===st.sid):null; const novo=!s;
    if(novo){ const n=w.reduce((m,x)=>Math.max(m,Number(String(x.id).slice(1))||0),0)+1; s={id:'s'+n,tarefas:[],pecas:[]}; w.push(s); }
    Object.assign(s,{nome:String(d.nome).trim(),gat:g,tol:t,base:d.base||'exec',cumpre:d.cumpre.filter(id=>id!==s.id&&w.some(x=>x.id===id)),tempo,esp:d.esp});
    const xs=Object.assign({},self.state.xs||{}); xs[s.id]=true;
    return {msg:(novo?'Serviço incluído: ':'Serviço salvo: ')+s.nome+' · '+manGatTxt(s)+'.',st:{sv:null,xs,flash:s.id}}; }); }
/* ---------- novo plano · editar nome e Aplica-se a ---------- */
function pmNovo(self,c,aid,pid){ pmRet(self); const a=aid?c.ativos[aid]:null; const p=pid?c.planos[pid]:null;
  const d=p?{nome:p.nome,tipo:p.aplica.t,modelo:p.aplica.t==='modelo'?p.aplica.v[0]:'',ativos:p.aplica.t==='ativos'?p.aplica.v.slice():[],base:''}
           :{nome:a?(a.nome+' · preventiva'):'',tipo:a?'ativos':'modelo',modelo:'',ativos:a?[a.id]:[],base:''};
  self.setState({np:{pid:pid||null,novoDe:aid||'',d,orig:JSON.stringify(d),errs:{},warn:false},sv:null,vl:null,dv:null,pan:null}); pmFoco('np_nome'); }
function pmCobertos(c,d,pid){ const as=d.tipo==='modelo'?c.ordem.map(x=>c.ativos[x]).filter(a=>a&&a.modelo===d.modelo):(d.ativos||[]).map(x=>c.ativos[x]).filter(Boolean); const out=[];
  as.forEach(a=>{ pmPlans(c).forEach(p=>{ if(p.id===pid||p.estado==='Inativo') return; if(manCabe(c,p,a)||c.vinc[p.id+'|'+a.id]){ const t=a.nome+' já está no '+p.id; if(out.indexOf(t)<0) out.push(t); } }); });
  return out; }
function pmNpSave(self){ const st=self.state.np, d=st.d, errs={}; const c=manGet();
  if(!String(d.nome).trim()) errs.nome='Informe o nome do plano.'; else if(pmPlans(c).some(x=>x.id!==st.pid&&x.nome.toLowerCase()===String(d.nome).trim().toLowerCase())) errs.nome='Já existe um plano com este nome.';
  if(d.tipo==='modelo'&&!d.modelo) errs.modelo='Escolha o modelo.'; if(d.tipo==='ativos'&&!d.ativos.length&&!(st.pid&&pmVincs(c,st.pid).length)) errs.ativos='Marque ao menos um ativo.';
  if(!errs.modelo&&!errs.ativos){ const na=manAplicaNova(c,st.pid?c.planos[st.pid]:{id:'',aplica:{t:'ativos',v:[]},grupo:''},d); if(na.erro) errs[d.tipo==='modelo'?'modelo':'ativos']=na.erro; }
  if(Object.keys(errs).length){ self.setState({np:Object.assign({},st,{errs,warn:false})}); return; }
  if(st.pid){ manMudar(self,c2=>{ manExige(c2,g2perfil(),'plano'); const p=c2.planos[st.pid]; if(!p) throw new Error('Plano não encontrado.'); p.nome=String(d.nome).trim();
      const na=manAplicaNova(c2,p,d); if(na.erro) throw new Error(na.erro); p.aplica=na.aplica; p.grupo=na.grupo;   /* MA-VINCULO: trocar "Aplica a" não perde vínculo */
      const nv=pmCands(c2,p).length; return {msg:p.id+' salvo · '+manAplTxt(c2,p)+(nv?' · '+nv+(nv>1?' ativos a vincular':' ativo a vincular'):'')+'.',st:{np:null}}; }); pmBack(self); return; }
  manMudar(self,c2=>{ manExige(c2,g2perfil(),'plano'); const id='PM-'+String(c2.seqpm).padStart(2,'0'); c2.seqpm++; const base=d.base?c2.planos[d.base]:null;
    const as=d.tipo==='modelo'?c2.ordem.map(x=>c2.ativos[x]).filter(a=>a.modelo===d.modelo):d.ativos.map(x=>c2.ativos[x]);
    c2.planos[id]={id,nome:String(d.nome).trim(),grupo:(as[0]||{}).grupo||'Implementos',aplica:{t:d.tipo,v:d.tipo==='modelo'?[d.modelo]:d.ativos.slice()},estado:'Ativo',versao:0,
      servicos:base?manClone(manWork(base)):[],rasc:null,hist:[]}; c2.ordemPlanos.push(id);
    return {msg:'Plano '+id+' criado em rascunho v1'+(base?' com os serviços de '+base.id:'')+' · inclua os serviços, vincule os ativos e publique.',st:{np:null,pg:{k:'plano',id},pan:null,xs:{}},id}; }); }
/* ---------- publicar (painel com diferenças, impacto e "ordens abertas seguem a vN") ---------- */
function pmPub(self,pid){ return manMudar(self,c=>{ manExige(c,g2perfil(),'plano'); const p=c.planos[pid]; if(!p) throw new Error('Plano não encontrado.'); if(p.versao&&!p.rasc) return {nada:true,msg:'Nada a publicar: edite um serviço para criar o rascunho.'};
  const w=manWork(p); if(!w.length) throw new Error('Inclua ao menos um serviço antes de publicar.');
  const sg=w.find(s=>!Object.keys(s.gat||{}).length); if(sg) throw new Error('“'+sg.nome+'” está sem gatilho.');
  const sk=w.find(s=>!s.tarefas.length); if(sk) throw new Error('“'+sk.nome+'” está sem tarefas no checklist.');
  const sgt=manPubSemGatilho(c,p,w); if(sgt.length) throw new Error('Não publicado: '+sgt.join(' · ')+'. Ajuste o gatilho ou desvincule o ativo.');   /* MA-VINCULO (Codex 6229032017) */
  const nv=p.versao?p.rasc.v:1; if(p.rasc){ p.servicos=p.rasc.servicos; p.rasc=null; } p.versao=nv; const h=String(c.hoje).split('-'); p.hist.unshift({v:nv,at:h[2]+'/'+h[1]+'/'+h[0]});
  const ab=Object.values(c.oms).filter(o=>o.pid===pid&&MAN_ABERTAS.indexOf(o.etapa)>=0);
  const ls=manLinhas(c,pid).filter(l=>l.s); const dv=ls.filter(l=>manDevida(l)&&!l.om);
  return {msg:pid+' v'+nv+' publicada'+(ab.length?' · '+ab.map(o=>o.id+' segue na v'+o.ver).join(', '):'')+' · '+(ls.length?(dv.length?dv.length+(dv.length>1?' vencimentos sem ordem':' vencimento sem ordem'):'vencimentos recalculados pela v'+nv):'vincule os ativos para gerar vencimentos')+'.',st:{pan:null}}; }); }
function pmPubV(self,v,c,p,pf){ const nv=p.versao?(p.rasc?p.rasc.v:null):1; v.pan_t='Publicar '+p.id+(nv?' v'+nv:''); v.pan_sub=p.versao?('Alterações do rascunho v'+nv+' em relação à v'+p.versao):'Primeira versão do plano (v1)';
  v.pb_dif=pmDiff(c,p).map(d=>({k:d.k,st:pmChip(d.c),n:d.n,t:d.t})); v.pb_vazio=!!nv&&!v.pb_dif.length;
  const ab=Object.values(c.oms).filter(o=>o.pid===p.id&&MAN_ABERTAS.indexOf(o.etapa)>=0);
  v.pb_oab=ab.map(o=>({t:o.id+' · '+manNome(c.ativos[o.aid])+' · '+o.serv+' · '+o.etapa+' · segue na v'+o.ver})); v.pb_temOab=ab.length>0;
  const na=pmVincs(c,p.id).length; v.pb_imp=nv?(na?('Vencimentos de '+na+(na>1?' ativos':' ativo')+' passam à v'+nv+'; as ordens abertas seguem a versão em que nasceram.'):'Nenhum ativo vinculado.'):'Nada a publicar.';
  const sgt=nv?manPubSemGatilho(c,p,manWork(p)):[];
  if(!nv) return {P:null,S:[]}; return {P:ma_btn('Publicar v'+nv,()=>pmPub(self,p.id),manPode(c,pf,'plano')||(sgt.length?('Ativo vinculado ficaria sem gatilho: '+sgt.join(' · ')):''),true),S:[]}; }
/* ---------- serviços do plano: linha + checklist (com tipo) e peças editáveis na expansão ---------- */
function pmPcSet(self,sid,patch){ const n=Object.assign({},self.state.pcd||{}); n[sid]=Object.assign({item:'',q:'',err:''},n[sid]||{},patch); self.setState({pcd:n}); }
function pmTkAdd(self,p,s){ const tk=(self.state.tkd||{})[s.id]||{v:'',tipo:'Serviço'}; const t=String(tk.v||'').trim(); const tipo=tk.tipo||'Serviço'; const set=(o)=>{ const n=Object.assign({},self.state.tkd||{}); n[s.id]=o; self.setState({tkd:n}); };
  if(!t){ set({v:'',tipo,err:'Escreva a tarefa.'}); return; } if(s.tarefas.some(x=>manTkT(x).toLowerCase()===t.toLowerCase())){ set({v:t,tipo,err:'Esta tarefa já está no checklist.'}); return; }
  const r=pmEdit(self,p.id,(c2,p2,w)=>{ w.find(y=>y.id===s.id).tarefas.push({t,tipo}); return {msg:'Tarefa incluída em '+s.nome+': '+t+' ('+tipo+').'}; }); if(!r.erro){ set({v:'',tipo,err:''}); pmFoco('pm-tk-'+s.id); } }
function pmPcAdd(self,p,s){ const d=(self.state.pcd||{})[s.id]||{item:'',q:''}; const n=pmNum(d.q);
  if(!d.item){ pmPcSet(self,s.id,{err:'Escolha o item do estoque.'}); return; } if(n===null||isNaN(n)||n<=0){ pmPcSet(self,s.id,{err:'Informe a quantidade, maior que zero.'}); return; }
  const it=manGet().itens[d.item]; const r=pmEdit(self,p.id,(c2,p2,w)=>{ w.find(y=>y.id===s.id).pecas.push({item:d.item,qtd:n}); return {msg:'Peça incluída em '+s.nome+': '+it.nome+' '+manN(n,1)+' '+it.un+'.'}; });
  if(!r.erro) pmPcSet(self,s.id,{item:'',q:'',err:''}); }
function pmSvV(self,c,p,s,pub){ const xs=self.state.xs||{}; const open=!!xs[s.id]; const del=self.state.del===s.id; const o=pub[s.id];
  let chg=''; if(p.rasc&&p.versao){ if(!o) chg='Novo'; else if(JSON.stringify(o)!==JSON.stringify(s)) chg='Alterado'; }
  const w=manWork(p); const cum=(s.cumpre||[]).map(id=>(w.find(x=>x.id===id)||{}).nome).filter(Boolean); const rasc=!p.versao||!!p.rasc;
  const tk=(self.state.tkd||{})[s.id]||{v:'',tipo:'Serviço',err:''}; const pc=(self.state.pcd||{})[s.id]||{item:'',q:'',err:''}; const ja={}; (s.pecas||[]).forEach(x=>{ ja[x.item]=1; });
  const np=(s.pecas||[]).length; const nv=p.rasc?p.rasc.v:p.versao+1;
  return {nome:s.nome,chg,hasChg:!!chg,chgst:pmChip(chg==='Novo'?'green':'yellow'),gat:manGatTxt(s)+(Object.keys(s.gat||{}).length>1?' · o que vencer primeiro':''),tol:manTolTxt(s)||'sem tolerância',
    cum:cum.length?('cumpre também '+cum.join(', ')):'',hasCum:!!cum.length,cont:s.tarefas.length+(s.tarefas.length===1?' tarefa':' tarefas')+' · '+np+(np===1?' peça':' peças'),
    tempo:manN(s.tempo,1)+' h · '+s.esp,open:g2seta(open).exp,isOpen:open,lab:g2seta(open,'checklist e peças de '+s.nome).lab,
    tog:()=>{ const n=Object.assign({},self.state.xs||{}); n[s.id]=!open; self.setState({xs:n}); },edit:()=>pmSvOpen(self,manGet(),p,s.id),
    rst:self.state.flash===s.id?'background:#E4F3E9;':'',podeDel:rasc&&!del,asking:del,notAsking:!del,ask:()=>self.setState({del:s.id}),no:()=>self.setState({del:null}),
    yes:()=>pmEdit(self,p.id,(c2,p2,w2)=>{ const i=w2.findIndex(x=>x.id===s.id); if(i>=0) w2.splice(i,1); w2.forEach(x=>{ x.cumpre=(x.cumpre||[]).filter(id=>id!==s.id); }); return {msg:'Serviço excluído: '+s.nome+'.',st:{del:null}}; }),
    dlab:'Excluir serviço '+s.nome,delmsg:'Excluir “'+s.nome+'”'+(p.versao?' do rascunho v'+nv+'? A v'+p.versao+' publicada e as ordens abertas não mudam.':'?'),
    did:'pm-det-'+s.id,dlab2:'Checklist e peças de '+s.nome,ntar:String(s.tarefas.length),
    tarefas:s.tarefas.map((t,i)=>({t:manTkT(t),tipo:manTk(t).tipo||'Serviço',n:String(i+1),rlab:'Retirar tarefa '+manTkT(t),rm:()=>pmEdit(self,p.id,(c2,p2,w2)=>{ w2.find(y=>y.id===s.id).tarefas.splice(i,1); return {msg:'Tarefa retirada: '+manTkT(t)+'.'}; })})),
    semTar:!s.tarefas.length,tkid:'pm-tk-'+s.id,tklab:'Nova tarefa de '+s.nome,tkv:tk.v,tkerr:tk.err||'',tkHasErr:!!tk.err,tktipo:tk.tipo||'Serviço',tktipos:MAN_TIPOS.map(x=>({v:x,t:x})),tktlab:'Tipo da nova tarefa de '+s.nome,
    tkset:(e)=>{ const n=Object.assign({},self.state.tkd||{}); n[s.id]={v:e.target.value,tipo:(n[s.id]||{}).tipo||'Serviço',err:''}; self.setState({tkd:n}); },
    tksett:(e)=>{ const n=Object.assign({},self.state.tkd||{}); n[s.id]={v:(n[s.id]||{}).v||'',tipo:e.target.value,err:''}; self.setState({tkd:n}); },
    tkkey:(e)=>{ if(e.key==='Enter'){ e.preventDefault(); pmTkAdd(self,p,s); } },tkadd:()=>pmTkAdd(self,p,s),
    pecas:(s.pecas||[]).map((x,i)=>{ const it=c.itens[x.item]||{nome:x.item,un:'',saldo:0,reservado:0}; const disp=it.saldo-it.reservado;
      return {nome:it.nome,q:manN(x.qtd,1)+' '+it.un,saldo:(disp>=x.qtd?'livre ':'falta · livre ')+manN(disp,1)+' '+it.un,st:pmChip(disp>=x.qtd?'gray':'red'),rlab:'Retirar peça '+it.nome,
        rm:()=>pmEdit(self,p.id,(c2,p2,w2)=>{ w2.find(z=>z.id===s.id).pecas.splice(i,1); return {msg:'Peça retirada: '+it.nome+'.'}; })}; }),
    semPecas:!np,temPecas:!!np,
    pcopts:[{v:'',t:'Item do estoque'}].concat(Object.keys(c.itens).filter(k=>!ja[k]).map(k=>({v:k,t:c.itens[k].nome+' ('+c.itens[k].un+')'}))),
    pcitem:pc.item,pcq:pc.q,pcerr:pc.err||'',pcHasErr:!!pc.err,pcun:(pc.item&&c.itens[pc.item])?c.itens[pc.item].un:'',
    pcsetitem:(e)=>{ pmPcSet(self,s.id,{item:e.target.value,err:''}); if(e.target.value) pmFoco('pm-pcq-'+s.id); },pcsetq:(e)=>pmPcSet(self,s.id,{q:e.target.value,err:''}),
    pckey:(e)=>{ if(e.key==='Enter'){ e.preventDefault(); pmPcAdd(self,p,s); } },pcadd:()=>pmPcAdd(self,p,s),pcid:'pm-pc-'+s.id,pcqid:'pm-pcq-'+s.id,pclab:'Peça para '+s.nome,pcqlab:'Quantidade da peça para '+s.nome}; }
function pmPlanoV0(v){ v.svs=[]; v.hist=[]; v.p_secs=[]; }
function pmPlanoV(self,v,c,p,pf){ const st=self.state; const e=pmEst(p); v.p_nome=p.id+' · '+p.nome; v.p_est=e[0]; v.p_est_st=pmChip(e[1]); v.voltarPl=()=>ma_volta(self);
  const nv=pmVincs(c,p.id).length; v.p_meta=manAplTxt(c,p)+' · '+(p.versao?'v'+p.versao+' em vigor':'sem versão publicada')+' · '+nv+(nv===1?' ativo vinculado':' ativos vinculados');
  const pp=manPode(c,pf,'plano');
  const inatFaz=()=>manMudar(self,c2=>{ manExige(c2,g2perfil(),'plano'); c2.planos[p.id].estado='Inativo'; return {msg:p.id+' inativo · para de gerar vencimentos; nada foi apagado e as ordens abertas seguem.',st:{inat:false}}; });
  const dv=manLinhas(c,p.id).filter(l=>l.s&&manDevida(l)); const oa=Object.values(c.oms).filter(o=>o.pid===p.id&&manAberta(o)&&o.etapa!=='Em conferência');
  v.p_podeInat=p.estado!=='Inativo'&&!!p.versao&&!st.inat&&!pp; v.p_inat=()=>{ if(dv.length||oa.length) self.setState({inat:true}); else inatFaz(); };
  v.inat_ask=!!st.inat&&p.estado!=='Inativo'; v.inat_t=p.id+' tem '+[dv.length?dv.map(l=>l.a.nome+' · '+l.s.nome+' '+l.x.sit.toLowerCase()).join(', '):'',oa.length?oa.map(o=>o.id).join(', ')+(oa.length>1?' abertas':' aberta'):''].filter(Boolean).join(' e ')+'. Inativar tira o plano dos vencimentos.';
  v.inat_yes=inatFaz; v.inat_no=()=>self.setState({inat:false});
  v.ban_i=p.estado==='Inativo'; const reat=()=>manMudar(self,c2=>{ manExige(c2,g2perfil(),'plano'); const q=c2.planos[p.id]; const nomes=manPub(q).map(x=>x.nome);
    const dup=pmVincs(c2,p.id).map(k=>{ const aid=k.split('|')[1]; const x=manDupServ(c2,p.id,aid,nomes); return x?(manNome(c2.ativos[aid])+' já faz '+x.s+' pelo '+x.pid):''; }).find(Boolean);
    if(dup) throw new Error('Não reativado: '+dup+'.'); q.estado='Ativo'; return {msg:p.id+' reativado · vencimentos recalculados.'}; });
  v.ban_r=!!p.rasc&&!v.ban_i; v.ban_t=p.rasc?('Rascunho v'+p.rasc.v+' em edição · vencimentos seguem a v'+p.versao):'';
  v.ban_n=!p.versao&&!v.ban_i;
  v.nodisc=!st.disc; v.disc=!!st.disc; v.disc_ask=()=>self.setState({disc:true}); v.disc_no=()=>self.setState({disc:false});
  v.disc_t='Descartar o rascunho'+(p.rasc?' v'+p.rasc.v:'')+'? A v'+p.versao+' publicada continua valendo.';
  v.disc_yes=()=>manMudar(self,c2=>{ manExige(c2,g2perfil(),'plano'); c2.planos[p.id].rasc=null; return {msg:'Rascunho descartado · '+p.id+' segue na v'+p.versao+'.',st:{disc:false}}; });
  const pub={}; p.servicos.forEach(s=>{ pub[s.id]=s; }); const w=manWork(p);
  v.svs=w.map(s=>pmSvV(self,c,p,s,pub)); v.sv_vazio=!w.length; v.sv_tem=!!w.length;
  v.hist_open=!!st.histOpen; v.hist_exp=g2seta(st.histOpen).exp; v.hist_tog=()=>self.setState({histOpen:!st.histOpen});
  v.hist=(p.rasc?[{t:'v'+p.rasc.v,at:'rascunho em edição',st:'Rascunho',stst:pmChip('yellow')}]:(!p.versao?[{t:'v1',at:'rascunho em edição',st:'Rascunho',stst:pmChip('yellow')}]:[]))
    .concat((p.hist||[]).map(h=>({t:'v'+h.v,at:'publicada em '+h.at,st:h.v===p.versao?'Em vigor':'Substituída',stst:pmChip(h.v===p.versao?'green':'gray')})));
  /* primária: Publicar vN (desabilitada com o motivo enquanto faltar serviço, gatilho ou tarefa) · Reativar · nenhuma */
  const nvv=p.versao?(p.rasc?p.rasc.v:null):1; let P=null;
  if(v.ban_i) P={t:'Reativar',fn:reat,dis:pp};
  else if(nvv){ const sk=w.find(s=>!s.tarefas.length), sg=w.find(s=>!Object.keys(s.gat||{}).length); const sgt=manPubSemGatilho(c,p,w); const why=pp||(!w.length?'Inclua ao menos um serviço':(sg?'“'+sg.nome+'” está sem gatilho':(sk?'“'+sk.nome+'” está sem tarefas':(sgt.length?'Ativo vinculado ficaria sem gatilho: '+sgt.join(' · '):''))));
    P={t:'Publicar v'+nvv,fn:()=>ma_abrir(self,'pub',p.id),dis:why}; }
  const panAberto=!!(st.pan||st.sv||st.np||st.vl||st.dv);
  v.p_prim=!!P; v.p_pt=P?P.t:''; v.p_pfn=P&&!P.dis?P.fn:(()=>{}); v.p_pdis=!!(P&&P.dis); v.p_pwhy=(P&&P.dis)||''; v.p_pst=(panAberto||(P&&P.dis))?MA_SEC:MA_PRIM;
  /* MA-VINCULO: "Ativos deste plano" com "Vincular ativos" na própria seção (candidatos compatíveis primeiro, busca, vários de uma vez) */
  const ncv=c.ordem.map(id=>c.ativos[id]).filter(a=>a&&!manVincVale(c.vinc[p.id+'|'+a.id])&&!manVincCompat(c,p,a).erro).length; const nvn=pmVincs(c,p.id).length;
  v.p_nvinc=String(nvn); v.p_apl='Aplica a: '+manAplTxt(c,p); v.p_semVinc=!nvn; v.p_temVl=p.estado!=='Inativo'&&(ncv>0||pmCands(c,p).length>0); v.p_vlt='Vincular ativos'; v.p_vlNc=ncv?(ncv+(ncv>1?' compatíveis':' compatível')):'nenhum compatível';   /* com candidato do "Aplica a" que não serve, o painel mostra o motivo */
  v.p_vldis=!!pp; v.p_vlwhy=pp||''; v.p_vl=()=>{ if(!pp) vlAbrir(self,{pid:p.id}); };
  v.p_secs=[{t:'Incluir serviço',fn:()=>pmSvOpen(self,manGet(),p,null)},{t:'Editar plano',fn:()=>pmNovo(self,manGet(),null,p.id)}]
    .filter(x=>!x.hide).map(x=>({t:x.t,fn:pp?(()=>{}):x.fn,dis:!!pp,why:pp||'',st:MA_SEC})); }
function pmSvP(self,v,c){ const st=self.state.sv; const p=st?c.planos[st.pid]:null;
  if(!pmPanel(self,v,'sv',{titulo:st&&st.sid?'Editar serviço':'Incluir serviço',sub:p?(p.id+' · '+(p.versao?'grava no rascunho v'+(p.rasc?p.rasc.v:p.versao+1)+'; a v'+p.versao+' e as ordens abertas não mudam.':'grava na v1 em rascunho.')):'',save:()=>pmSvSave(self)})){ v.sv_bases=[]; v.sv_esps=[]; v.sv_cum=[]; return; }
  ['nome','h','km','d','th','tkm','td','base','tempo','esp'].forEach(k=>pmFld(self,v,'sv',k));
  v.sv_bases=[{v:'exec',t:PM_BASE.exec},{v:'prog',t:PM_BASE.prog}]; v.sv_esps=[{v:'',t:'Escolha a especialidade'}].concat(c.esp.map(x=>({v:x,t:x})));
  const w=p?manWork(p):[]; v.sv_cum=w.filter(x=>x.id!==st.sid).map(x=>({t:x.nome,on:st.d.cumpre.indexOf(x.id)>=0,lab:'Cumpre também '+x.nome,
    tog:()=>{ const cur=self.state.sv; const cu=cur.d.cumpre.slice(); const i=cu.indexOf(x.id); if(i>=0) cu.splice(i,1); else cu.push(x.id); self.setState({sv:Object.assign({},cur,{d:Object.assign({},cur.d,{cumpre:cu}),warn:false})}); }}));
  v.sv_temCum=v.sv_cum.length>0; const U=p?pmUnits(c,p):{n:0};
  v.sv_ghelp=U.n?('Ativos deste plano: '+[U.h?'horímetro (h)':'',U.km?'odômetro (km)':''].filter(Boolean).join(' e ')+((!U.h&&!U.km)?'sem contador · use dias':'')+'. Tolerância do fabricante ou da política.'):'Tolerância do fabricante ou da política.'; }
function pmNpP(self,v,c){ const st=self.state.np; const ed=!!(st&&st.pid);
  if(!pmPanel(self,v,'np',{titulo:ed?'Editar plano':'Novo plano de manutenção',sub:ed?st.pid:'Nasce em rascunho v1.',save:()=>pmNpSave(self)})){ v.np_tipos=[]; v.np_mods=[]; v.np_atvs=[]; v.np_bases=[]; v.np_avs=[]; return; }
  v.np_novo=!ed; const cob=pmCobertos(c,st.d,st.pid); v.np_avs=cob.map(t=>({t})); v.np_temAv=cob.length>0;
  const p0=ed?c.planos[st.pid]:null; const muda=!!p0&&JSON.stringify({t:st.d.tipo,v:st.d.tipo==='modelo'?[st.d.modelo]:st.d.ativos})!==JSON.stringify({t:p0.aplica.t,v:p0.aplica.v});
  const na=muda?manAplicaNova(c,p0,st.d):null; v.np_ef=na?na.efeito.map(t=>({t})):[]; v.np_temEf=!!na&&!na.erro&&na.efeito.length>0; v.np_apl=p0?('Hoje: '+manAplTxt(c,p0)):'';
  ['nome','tipo','modelo','base'].forEach(k=>pmFld(self,v,'np',k));
  v.np_tipos=[{v:'modelo',t:'Todos os ativos de um modelo'},{v:'ativos',t:'Ativos escolhidos'}];
  const mods=[]; c.ordem.forEach(id=>{ const m=c.ativos[id].modelo; if(mods.indexOf(m)<0) mods.push(m); });
  v.np_mods=[{v:'',t:'Escolha o modelo'}].concat(mods.map(m=>({v:m,t:m+' · '+c.ordem.map(id=>c.ativos[id]).filter(a=>a.modelo===m).map(a=>a.nome).join(', ')})));
  v.np_isMod=st.d.tipo==='modelo'; v.np_isAtv=st.d.tipo==='ativos';
  v.np_atvs=c.ordem.map(id=>c.ativos[id]).map(a=>({t:manNome(a),on:st.d.ativos.indexOf(a.id)>=0,
    tog:()=>{ const cur=self.state.np; const l=cur.d.ativos.slice(); const i=l.indexOf(a.id); if(i>=0) l.splice(i,1); else l.push(a.id); const er=Object.assign({},cur.errs||{}); delete er.ativos; self.setState({np:Object.assign({},cur,{d:Object.assign({},cur.d,{ativos:l}),errs:er,warn:false})}); }}));
  const e=(st.errs||{}).ativos||''; v.np_eativos=e; v.np_heativos=!!e;
  v.np_bases=[{v:'',t:'Plano em branco'}].concat(pmPlans(c).map(x=>({v:x.id,t:'Copiar serviços de '+x.id+' · '+x.nome}))); }
/* ---------- Vincular a plano (MA-VINCULO, 16/10/2026): um painel para 1 ou vários ativos, aberto pelo ativo, pela visão Ativos ou pelo plano ----------
   SEL-04: a ação em lote é no painel lateral (lista já marcada, campos comuns uma vez, uma primária "Vincular N …"; tudo ou nada; repetir não duplica).
   Base de contagem: a do vínculo encerrado volta como estava; a da última OM encerrada do mesmo serviço vem proposta (corrigir pede motivo); sem
   execução registrada a pessoa escolhe "Contar de agora" ou "Informar a última execução" (nada é inferido). Prévia pela mesma conta do vencimento. */
function vlChipSt(on){ return 'font-family:inherit;font-size:12.5px;font-weight:700;padding:6px 12px;border-radius:999px;cursor:pointer;min-height:var(--g2-alvo,36px);box-sizing:border-box;text-align:left;'+(on?'border:1px solid #1E7A4C;background:#E4F3E9;color:#1E6B47;box-shadow:inset 0 0 0 1px #1E7A4C;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;'); }
function vlB(st,aid){ const b=(st.d.b||{})[aid]||{}; return {modo:st.d.bmodo||'',corr:!!b.corr,data:b.data||'',leit:b.leit===undefined?'':b.leit,mot:b.mot||''}; }
function vlOps(c,pre){ const out=[]; c.ordemPlanos.map(id=>c.planos[id]).forEach(p=>{ if(!p||p.estado==='Inativo') return; let n=0, best=9;
    pre.forEach(aid=>{ const a=c.ativos[aid]; if(!a||manVincVale(c.vinc[p.id+'|'+aid])) return; const cp=manVincCompat(c,p,a); if(cp.erro) return; n++; best=Math.min(best,MAN_NIV[cp.nivel]); });
    if(n) out.push({p,n,best}); });
  return out.sort((x,y)=>(y.n-x.n)||(x.best-y.best)||((y.p.versao?1:0)-(x.p.versao?1:0))||x.p.id.localeCompare(y.p.id)); }
function vlLista(c,st){ const p=c.planos[st.d.pid]; const rows=[], seen={};
  if(!p) return st.pre.map(aid=>c.ativos[aid]).filter(Boolean).map(a=>({a,cp:{erro:'',avisos:[],nivel:''},ja:false,pre:true,semPl:true}));
  const add=(a,pre)=>{ if(!a||seen[a.id]) return; seen[a.id]=1; const ja=manVincVale(c.vinc[p.id+'|'+a.id]); rows.push({a,cp:ja?{erro:'',avisos:[],nivel:''}:manVincCompat(c,p,a),ja,pre}); };
  st.pre.forEach(aid=>add(c.ativos[aid],true));
  const cs=c.ordem.map(id=>c.ativos[id]).filter(a=>a&&!manVincVale(c.vinc[p.id+'|'+a.id])).map(a=>({a,cp:manVincCompat(c,p,a)}));
  cs.filter(x=>!x.cp.erro).sort((x,y)=>MAN_NIV[x.cp.nivel]-MAN_NIV[y.cp.nivel]).forEach(x=>add(x.a,false));
  cs.filter(x=>x.cp.erro&&manAtvAtivo(x.a)&&manCabe(c,p,x.a)).forEach(x=>add(x.a,false));   /* do "Aplica a" mas recusado: aparece com o motivo */
  const on=(st.d&&st.d.on)||{}; Object.keys(on).filter(k=>on[k]).forEach(aid=>{ if(c.ativos[aid]){ add(c.ativos[aid],false); return; } if(seen[aid]) return; seen[aid]=1;   /* marcado é marcado: fica na lista até ser desmarcado, mesmo inválido */
    rows.push({a:{id:aid,nome:aid,modelo:'—',local:'fora do cadastro',classe:''},cp:{erro:aid+' não está mais no cadastro.',avisos:[],nivel:''},ja:false,pre:false,sumiu:true}); });
  const q=g2norm(st.q||'').trim(); if(!q) return rows;
  cs.filter(x=>x.cp.erro).forEach(x=>add(x.a,false));   /* na busca, o que não serve aparece com o motivo */
  rows.forEach(r=>{ r.casa=g2norm(r.a.nome+' '+r.a.modelo+' '+r.a.local+' '+r.a.classe).indexOf(q)>=0; });
  return rows.filter(r=>r.pre||on[r.a.id]||r.casa); }   /* a busca só filtra o que ainda não foi marcado: o lote não muda com ela */
function vlMarcaIni(c,st){ const on={}; vlLista(c,st).forEach(r=>{ if(r.ja||r.cp.erro) return; if(r.pre||(st.fixo&&r.cp.nivel==='escopo')) on[r.a.id]=true; }); return on; }
function vlAbrir(self,o){ pmRet(self); const c=manGet(); o=o||{}; const pre=(o.aids||[]).filter(id=>c.ativos[id]);
  const pid=o.pid||((vlOps(c,pre)[0]||{}).p||{}).id||'';
  const st={fixo:!!o.pid,pre,q:'',d:{pid,on:{},bmodo:'',b:{}},errs:{},chave:manChave(),falha:'',warn:false};
  st.d.on=vlMarcaIni(c,st); st.orig=JSON.stringify(st.d);
  self.setState({vl:st,sv:null,np:null,dv:null,pan:null}); pmFoco('vl-painel'); }
function vlSet(self,patch,dpatch){ const cur=self.state.vl; if(!cur) return; self.setState({vl:Object.assign({},cur,patch||{},dpatch?{d:Object.assign({},cur.d,dpatch)}:{},{warn:false,falha:''})}); }
function vlSetB(self,aid,patch){ const cur=self.state.vl; if(!cur) return; const b=Object.assign({},cur.d.b||{}); b[aid]=Object.assign({},b[aid]||{},patch); const er=Object.assign({},cur.errs||{});
  Object.keys(patch).forEach(k=>{ delete er[aid+'.'+k]; }); self.setState({vl:Object.assign({},cur,{d:Object.assign({},cur.d,{b}),errs:er,warn:false,falha:''})}); }
function vlRuins(c,p,L){ return L.filter(r=>r.ja||r.cp.erro).map(r=>r.ja?(r.a.nome+' já está vinculado ao '+p.id):r.cp.erro.replace(/\.$/,'')); }
function vlSalvar(self){ const st=self.state.vl; if(!st) return; const c=manGet(); const p=c.planos[st.d.pid];
  if(!p){ self.setState({vl:Object.assign({},st,{falha:'Nada foi gravado: o plano '+st.d.pid+' não existe mais.'})}); return; }
  const on=st.d.on||{}; const L=vlLista(c,Object.assign({},st,{q:''})).filter(r=>on[r.a.id]); const errs={};   /* o lote é o conjunto marcado (st.d.on), revalidado agora; a busca não entra */
  const ruins=vlRuins(c,p,L); if(ruins.length){ self.setState({vl:Object.assign({},st,{errs:{},falha:'Nada foi gravado. Desmarque '+(ruins.length>1?'estes ativos':'este ativo')+' ou ajuste: '+ruins.join(' · ')+'.'})}); return; }
  L.forEach(r=>{ if(manVincBase(c,p,r.a).modo==='hist') return; const x=manVincRef(c,p,r.a,vlB(st,r.a.id)); Object.keys(x.errs).forEach(k=>{ errs[k==='modo'?'_modo':(r.a.id+'.'+k)]=x.errs[k]; }); });
  if(Object.keys(errs).length){ self.setState({vl:Object.assign({},st,{errs,falha:''})}); return; }
  const ids=L.map(r=>r.a.id); const itens=L.map(r=>({aid:r.a.id,base:vlB(st,r.a.id)}));
  const r=manMudar(self,c2=>manVincular(c2,st.d.pid,itens,g2perfil(),st.chave),{estrito:true});
  if(r.erro){ self.setState({vl:Object.assign({},self.state.vl||st,{falha:r.erro})}); return; }   /* nada gravado: o painel fica com tudo o que foi escolhido */
  self.setState({vl:null}); vlVolta(self,ids); }
/* foco de volta: quem abriu; se a linha mudou (o link sumiu), a linha do ativo vinculado; senão o título */
function vlVolta(self,ids){ setTimeout(()=>{ const r=self.__pmRet; self.__pmRet=null; if(r&&document.contains(r)&&r.getClientRects().length){ r.focus(); return; }
  const row=[...document.querySelectorAll('main [role=row][data-rid]')].find(x=>x.getClientRects().length&&ids.some(id=>x.getAttribute('data-rid')===id||x.getAttribute('data-rid').endsWith('|'+id)));
  const r0=row||[...document.querySelectorAll('main [role=row][data-rid]')].find(x=>x.getClientRects().length);   /* o ativo saiu do filtro: a 1ª linha da mesma lista */
  if(r0){ r0.focus(); return; } const h=document.querySelector('main h2'); if(h){ h.setAttribute('tabindex','-1'); h.focus(); } },80); }
function vlP(self,v,c,pf){ const st=self.state.vl; const p=st?c.planos[st.d.pid]:null;
  if(!pmPanel(self,v,'vl',{titulo:st&&st.fixo&&p?('Vincular ativos ao '+p.id):'Vincular a plano',sub:'A base de contagem é a última execução de cada ativo (o marco é a última execução do serviço). Vincular não registra manutenção como feita.',save:()=>vlSalvar(self)})){ v.vl_ops=[]; v.vl_ls=[]; return; }
  v.vl_fixo=!!st.fixo&&!!p; v.vl_pnome=p?(p.id+' · '+p.nome):''; v.vl_papl=p?(manAplTxt(c,p)+' · '+(p.versao?('v'+p.versao+' em vigor'):'rascunho: vence só depois de publicar')):'';
  const ops=st.fixo?[]:vlOps(c,st.pre);
  v.vl_ops=ops.map(o=>{ const on=o.p.id===st.d.pid; return {id:o.p.id,nome:o.p.nome,n:o.n+(o.n>1?' ativos':' ativo')+(o.p.versao?'':' · rascunho'),on:String(on),st:vlChipSt(on),
    go:()=>{ const cur=self.state.vl; if(!cur||cur.d.pid===o.p.id) return; const n=Object.assign({},cur,{d:Object.assign({},cur.d,{pid:o.p.id}),errs:{},falha:'',warn:false}); n.d.on=vlMarcaIni(manGet(),n); self.setState({vl:n}); }}; });
  v.vl_temOps=!st.fixo&&ops.length>0; v.vl_temOpAv=v.vl_temOps&&st.pre.length>1&&ops.some(o=>o.n<st.pre.length);
  v.vl_opAv='Um plano por vez: quem não serve ao plano escolhido fica de fora, com o motivo.';
  const grs=[...new Set(st.pre.map(id=>(c.ativos[id]||{}).grupo).filter(Boolean))];
  v.vl_semOps=!st.fixo&&!ops.length; v.vl_semOpsT=v.vl_semOps?('Nenhum plano de '+grs.join(' ou ')+' serve '+(st.pre.length>1?'a estes ativos.':'a este ativo.')):'';
  v.vl_criar=()=>{ const aid=st.pre[0]; self.setState({vl:null}); pmNovo(self,manGet(),aid); };
  v.vl_q=st.q||''; v.vl_setq=(e)=>vlSet(self,{q:e.target.value}); v.vl_busca=!!st.fixo||!!st.q||vlLista(c,Object.assign({},st,{q:''})).length>6;   /* busca onde a lista é longa (o plano e suas candidatas) */
  const L=vlLista(c,st); const on=st.d.on||{}; const ers=st.errs||{};
  const LT=vlLista(c,Object.assign({},st,{q:''})).filter(r=>on[r.a.id]); const marc=LT.filter(r=>!r.ja&&!r.cp.erro); const ruins=p?vlRuins(c,p,LT):[]; const semH=p?marc.filter(r=>manVincBase(c,p,r.a).modo===''):[];
  v.vl_temSem=semH.length>0; v.vl_semT='Sem execução registrada ('+semH.map(r=>r.a.nome).join(', ')+'): como contar?';
  v.vl_semAj=st.d.bmodo==='agora'?'Conta de hoje e da leitura atual de cada ativo (marco estimado, fica marcado). Se houve revisão, informe-a.':(st.d.bmodo==='ult'?'Informe a data e a leitura da última execução de cada um.':'Escolha uma das duas: nada é inferido.');
  v.vl_agoraOn=String(st.d.bmodo==='agora'); v.vl_ultOn=String(st.d.bmodo==='ult'); v.vl_agoraSt=vlChipSt(st.d.bmodo==='agora'); v.vl_ultSt=vlChipSt(st.d.bmodo==='ult');
  v.vl_agora=()=>{ const cur=self.state.vl; const er=Object.assign({},cur.errs||{}); delete er._modo; self.setState({vl:Object.assign({},cur,{d:Object.assign({},cur.d,{bmodo:'agora'}),errs:er,warn:false,falha:''})}); };
  v.vl_ult=()=>{ const cur=self.state.vl; const er=Object.assign({},cur.errs||{}); delete er._modo; self.setState({vl:Object.assign({},cur,{d:Object.assign({},cur.d,{bmodo:'ult'}),errs:er,warn:false,falha:''})}); };
  v.vl_eModo=ers._modo||''; v.vl_temEModo=!!ers._modo; v.vl_hoje=c.hoje;
  const IN='font-family:inherit;font-size:13.5px;padding:7px 9px;border-radius:8px;box-sizing:border-box;background:#fff;color:#15201A;min-height:var(--g2-alvo,36px);';
  v.vl_ls=L.map(r=>{ const a=r.a, id=a.id; const ok=!r.ja&&!r.cp.erro; const marcado=!!on[id]; const isOn=marcado&&ok; const b0=p&&ok?manVincBase(c,p,a):{modo:''}; const bb=vlB(st,id);
    const x=isOn&&b0.modo!=='hist'?manVincRef(c,p,a,bb):null; const ref=x&&x.ref; let orig='', inp=false, temCorr=false, corrT='';
    if(b0.modo==='hist'){ const f=b0.v.fim; orig='Retoma a contagem de antes (desvinculado em '+manBr(f.em)+' · '+f.mot+'): base '+manVincDeTxt(a,b0.v.marco)+(Object.keys(b0.v.ult||{}).length?' e as últimas execuções guardadas.':'.'); }
    else if(b0.modo==='om'){ const t0=b0.om+' · '+manBr(b0.data)+(a.un&&b0.leit!==null&&b0.leit!==undefined?' · '+manQ(b0.leit,a.un):''); orig=bb.corr?('Corrigindo a base da '+t0+':'):('Última execução registrada: '+t0+'.'); temCorr=true; corrT=bb.corr?('Usar a da '+b0.om):'Corrigir'; inp=bb.corr; }
    else if(st.d.bmodo==='agora') orig=ref?('Sem execução registrada · contando de agora: '+manVincDeTxt(a,ref)+' (marco estimado).'):'Sem execução registrada · contar de agora:';
    else if(st.d.bmodo==='ult'){ orig='Última execução (sem registro no sistema):'; inp=true; }
    else orig='Sem execução registrada · escolha acima como contar.';
    const vv=b0.modo==='hist'?b0.v:(ref?{marco:ref,ult:{}}:null);
    const prev=isOn&&p&&vv?manVincPrev(c,p,a,vv).map(z=>({nome:z.nome,txt:z.txt,st:'font-size:12.5px;color:'+({'Vencida':'#B42318','Vence em breve':'#8A5A00'}[z.sit]||'#15201A')+';'})):[];
    const ed=ers[id+'.data']||'', el=ers[id+'.leit']||(x&&st.d.bmodo==='agora'&&x.errs.leit)||'', em=ers[id+'.mot']||'';
    const brd=(er)=>IN+'border:1px solid '+(er?'#B42318':'#E4E9E5')+';';
    return {id,idx:'vl-x-'+id,nome:a.nome,sub:a.modelo+' · '+a.local+(a.leit&&a.un?' · '+manLeitTxt(a):(a.un?'':' · sem contador')),on:marcado,dis:!ok&&!marcado,
      tog:()=>{ const cur=self.state.vl; const o2=Object.assign({},cur.d.on||{}); o2[id]=!o2[id]; vlSet(self,null,{on:o2}); },
      temErro:!!(r.cp.erro||r.ja),erro:r.ja?('Já vinculado ao '+(p?p.id:'')+'.'):(r.cp.erro?'Não serve: '+r.cp.erro:''),avs:ok?r.cp.avisos.map(t=>({t})):[],
      mostra:isOn,orig,temCorr,corrT,corr:()=>vlSetB(self,id,bb.corr?{corr:false}:{corr:true,data:b0.data||'',leit:(b0.leit===null||b0.leit===undefined)?'':String(b0.leit)}),
      inp,cont:!!a.un,un:a.un||'',idd:'vl_data_'+id,idl:'vl_leit_'+id,idm:'vl_mot_'+id,data:bb.data,leit:String(bb.leit),mot:bb.mot,pedeMot:inp&&b0.modo==='om',
      setd:(ev)=>vlSetB(self,id,{data:ev.target.value}),setl:(ev)=>vlSetB(self,id,{leit:ev.target.value}),setm:(ev)=>vlSetB(self,id,{mot:ev.target.value}),
      hoje:()=>vlSetB(self,id,{data:c.hoje}),temAtual:!!(a.leit&&a.un),atualT:a.leit&&a.un?('Atual · '+manQ(a.leit.val,a.un)):'',atual:()=>vlSetB(self,id,{leit:a.leit?String(a.leit.val):''}),
      std:brd(ed),stl:brd(el)+'width:110px;text-align:right;',stm:brd(em)+'flex:1 1 180px;min-width:0;',temEd:!!ed,ed,temEl:!!el,el,temEm:!!em,em,prev,temPrev:prev.length>0}; });
  v.vl_vazio=st.q?!L.some(r=>r.casa):!L.length; v.vl_vazioT=st.q?(L.length?'Nenhum outro ativo com “'+st.q+'”: os marcados continuam na lista.':'Nenhum ativo com “'+st.q+'”.'):'Nenhum ativo para vincular.';
  const n=marc.length; const pp=manPode(c,pf,'plano');
  const why=pp||(!p?'Escolha o plano':(ruins.length?('Desmarque '+(ruins.length>1?'os que não servem':'o que não serve')+': '+ruins.join(' · ')):(!n?'Marque ao menos um ativo':((semH.length&&!st.d.bmodo)?'Escolha como contar os ativos sem execução registrada':''))));
  v.vl_rot=p?('Vincular '+(n>1?n+' ativos ':'')+'ao '+p.id):'Vincular'; v.vl_sdis=!!why; v.vl_swhy=why; v.vl_temWhy=!!why; v.vl_sst=why?MA_SEC:MA_PRIM;
  v.vl_temFalha=!!st.falha; v.vl_falha=st.falha?(st.falha+' Suas escolhas continuam aqui.'):''; }
/* ---------- Desvincular (com motivo; histórico guardado; a OM aberta continua) ---------- */
function dvAbrir(self,k){ pmRet(self); const q=String(k).split('|'); const d={mot:''};
  self.setState({dv:{pid:q[0],aid:q[1],d,orig:JSON.stringify(d),errs:{},warn:false,chave:manChave(),falha:''},sv:null,np:null,vl:null,pan:null}); pmFoco('dv_mot','dv-painel'); }
function dvSalvar(self){ const st=self.state.dv; if(!st) return; if(manVazio(st.d.mot)){ self.setState({dv:Object.assign({},st,{errs:{mot:'Informe o motivo.'}})}); return; }
  const r=manMudar(self,c2=>manDesvincular(c2,st.pid,st.aid,st.d.mot,g2perfil(),st.chave),{estrito:true});
  if(r.erro){ self.setState({dv:Object.assign({},self.state.dv||st,{falha:r.erro})}); return; } self.setState({dv:null}); vlVolta(self,[]); }
function dvP(self,v,c,pf){ const st=self.state.dv; const p=st?c.planos[st.pid]:null, a=st?c.ativos[st.aid]:null;
  if(!pmPanel(self,v,'dv',{titulo:'Desvincular '+(a?a.nome:''),sub:p?(p.id+' · '+p.nome):'',save:()=>dvSalvar(self)})){ v.dv_ms=[]; v.dv_oms=[]; return; }
  pmFld(self,v,'dv','mot');
  v.dv_ms=['Ativo vendido ou baixado','Vínculo feito por engano','Passou para outro plano'].map(t=>({t,on:String(st.d.mot===t),st:vlChipSt(st.d.mot===t),go:()=>{ const cur=self.state.dv; self.setState({dv:Object.assign({},cur,{d:Object.assign({},cur.d,{mot:t}),errs:{},warn:false,falha:''})}); }}));
  const ab=Object.values(c.oms).filter(o=>o.pid===st.pid&&o.aid===st.aid&&manAberta(o));
  v.dv_oms=ab.map(o=>({t:o.id+' · '+o.serv+' · '+o.etapa,h:'#om='+o.id})); v.dv_temOm=ab.length>0;
  v.dv_omT=ab.length>1?'Estas ordens continuam abertas (desvincular não apaga ordem; se não for fazer, cancele na própria ordem):':'Esta ordem continua aberta (desvincular não apaga ordem; se não for fazer, cancele na própria ordem):';
  v.dv_ef=a&&p?(a.nome+' deixa de gerar vencimentos do '+p.id+'. A base de contagem e as últimas execuções ficam guardadas: vincular de novo retoma a mesma contagem.'):'';
  const pp=manPode(c,pf,'plano'); const why=pp||(manVazio(st.d.mot)?'Informe o motivo':'');
  v.dv_rot='Desvincular'; v.dv_sdis=!!why; v.dv_swhy=why; v.dv_temWhy=!!why; v.dv_sst=MA_SEC+'color:#B42318;border-color:#B42318;';
  v.dv_temFalha=!!st.falha; v.dv_falha=st.falha?(st.falha+' O motivo continua aqui.'):''; }
'''

# =====================================================================================
# HTML
def _chips(lst,label,n=3):
    return (f'<div role="group" aria-label="{label}" style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">'
            + FOR(lst,'x',f'<button type="button" aria-pressed="{H("x.on")}" onClick="{H("x.go")}" style="{H("x.st")}">{H("x.t")}</button>',n) + '</div>')
def _sel(val,setfn,lst,label,idv=None):
    return (f'<select{(" id="+chr(34)+idv+chr(34)) if idv else ""} aria-label="{label}" value="{H(val)}" onChange="{H(setfn)}" style="{INP} max-width: 100%;">'
            + FOR(lst,'o',f'<option value="{H("o.v")}">{H("o.t")}</option>',3) + '</select>')
def _kv(lst,cols=2):
    return (f'<div style="display: grid; grid-template-columns: repeat({cols}, minmax(0, 1fr)); gap: 8px 16px; padding: 10px 12px; background: {BG}; border-radius: 10px;">'
            + FOR(lst,'x',f'<div style="min-width: 0;"><div style="font-size: 10.5px; font-weight: 700; letter-spacing: .05em; color: {MUTED}; text-transform: uppercase;">{H("x.l")}</div><div style="font-size: 13px; font-weight: 600; margin-top: 2px; overflow-wrap: anywhere;">{H("x.v")}</div></div>',4) + '</div>')
def _chiph(t,st,dot): return f'<span style="{H(st)}"><span style="{H(dot)}"></span>{H(t)}</span>'
def _lab(t): return f'<div style="{SECT}">{t}</div>'
def _fld(rot,inner): return f'<label style="display: flex; flex-direction: column; gap: 4px; {LBL} min-width: 0;">{rot}{inner}</label>'
def _blk(pre,k,corpo):
    """bloco recolhível com uma linha de resumo; a seta abre. Detalhe do ativo: nasce recolhido (TAB-12, 17/10/2026). Painel da ordem (obk_): abre o
    da fase, como o painel da O.S. (seção de UM registro, exceção da TAB-12; data-secao-registro)"""
    reg = ' data-secao-registro="1"' if pre == 'obk_' else ''
    return (f'<section class="ma-bl" aria-label="{H(pre+k+"_t")}"><button type="button" class="ma-blh"{reg} aria-expanded="{H(pre+k+"_o")}" onClick="{H(pre+k+"_g")}">'
            f'{E.seta()}<span>{H(pre+k+"_t")}</span><span style="font-weight: 600; color: {MUTED}; font-size: 12.5px; flex: 1 1 auto; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">· {H(pre+k+"_s")}</span></button>'
            + IF(pre.replace('_','')+'_'+k if False else ('ob_'+k if pre=='obk_' else 'ab_'+k),f'<div class="ma-bl-c">{corpo}</div>') + '</section>')
def _btns(lst):
    return FOR(lst,'b',f'<button type="button" disabled="{H("b.dis")}" title="{H("b.why")}" onClick="{H("b.fn")}" style="{H("b.st")}">{H("b.t")}</button>',2)

def _cabecalho():
    """⋯ Mais ações da manutenção no fim dos comandos do cabeçalho (componente único engine.mais, 15/10/2026): Registrar achado quando a
    visão também tem a primária (uma secundária à vista no máximo) e Restaurar demonstração. Restaurar apaga o que foi feito na demonstração:
    pede confirmação logo abaixo do ⋯, fora do menu, e a decisão fica à vista até a resposta."""
    itens=[IF('hs_menu',f'<button type="button" role="menuitem" onClick="{H("hs_fn")}">{H("hs_t")}</button>'),
           f'<button type="button" role="menuitem" onClick="{H("rst")}" data-dica="Volta manutenção, O.S., Estoque e App ao início: o estado é um só.">Restaurar demonstração</button>']
    conf=IF('rst_ask',f'<div role="alertdialog" aria-label="Restaurar demonstração" style="position: absolute; right: 0; top: calc(100% + 6px); z-index: 50; width: 300px; max-width: calc(100vw - 24px); box-sizing: border-box; background: #fff; border: 1px solid {LINE}; border-radius: 12px; box-shadow: 0 14px 34px -14px rgba(21,32,26,.4); padding: 10px 12px; display: flex; flex-direction: column; gap: 8px;">'
            f'<span role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">Restaurar toda a demonstração (manutenção, O.S., Estoque e App)?</span>'
            f'<span style="display: flex; gap: 6px; justify-content: flex-end;"><button type="button" onClick="{H("rst_cancel")}" style="{_MINI}">Manter</button><button type="button" onClick="{H("rst_ok")}" style="{_MINI} color: {RED}; border-color: {RED};">Restaurar</button></span></div>')
    return f'<span style="position: relative; display: inline-flex;">{E.mais("Manutenção",itens)}{conf}</span>'

def _prim_cab():
    """Ações do cabeçalho (MAIS-02 e BOT-01): a secundária só aparece quando a visão não tem primária; a primária da visão é verde. Para o perfil
    sem o papel (ou sem nada a fazer no filtro), a primária fica indisponível pela peça comum engine.acao_motivo: aria-disabled, dica e o motivo
    junto do botão (PRD DS-06 e 74.5.0, VIS-04), como em Assinatura, Backoffice e Compras. DS-MAN (17/10/2026): sai o texto solto ao lado do
    botão cinza ("Ação do Otávio (responsável de manutenção)" em 3 linhas)."""
    prim=(f'<button type="button" class="ma-hb" aria-disabled="{H("hp_dis")}" data-dica="{H("hp_why")}" onClick="{H("hp_fn")}" style="{H("hp_st")}">{H("hp_t")}</button>')
    return (IF('hs_vis',f'<button type="button" class="ma-hb" onClick="{H("hs_fn")}" style="{SEC}">{H("hs_t")}</button>')
            + IF('hp_tem',E.acao_motivo(prim,H('hp_dis'),H('hp_why'))))

# DS-MAN (proprietário, 17/10/2026, 23h: "Design system de manutenção ainda não está no padrão"; referência: Agrícola › Ordem de Serviço):
# - a fileira das visões (Sem ordem · Ordens · Ativos · Planos) é a única acima do bloco (a Manutenção é uma tela só, pedido de 05/10);
# - cada lista mora num bloco com título (processo_os.bloco, o mesmo do "Ordens por fase"), com os filtros rápidos dentro dele;
# - Ativos | Abastecimentos é uma escolha dentro do bloco (antes uma 2ª fileira solta);
# - em Ordens: as fases e 2 recortes de ação; "Esta semana" e "Espera por peça" no ⋯ do bloco (ligados, viram recorte ativo);
# - a Pendência dos ativos passa da faixa do topo para a barra da lista (TAB-01: filtro da lista fica com a lista; a faixa fica com Tipo,
#   Criticidade e Grupo, que valem para a tela). Fazenda não entra: ativo e ordem não têm fazenda no dado (só o local).
# TAB-14: w = largura máxima do conteúdo da célula (g2pw), escolhida para cada célula caber em 2 linhas e a grade inteira (todas as colunas) caber
# sem rolagem lateral a 1280 px (ds_man_test L1 a L4; ma_correcoes_om_test 8).
def _blo(html):
    """o bloco da O.S. (processo_os.bloco) com a classe ma-blo: no celular o título do bloco sai (a visão já está no título da tela e na lista
    Visão; fica a linha só quando tem a escolha Ativos | Abastecimentos) e a lista sobe: ≥ 5 linhas acima da dobra a 390 px (AC-PCM-22)"""
    assert html.startswith('<section style='), 'bloco sem <section>'
    return html.replace('<section style=','<section class="ma-blo" style=',1)

def _visoes():
    from areas.processo_os import _kanban, bloco
    G=lambda cols,gid,**k: grid(cols,[],edit=dict(m='pick'),gid=gid,total=k.pop('total',False),**k)
    g_so=G([dict(k='item',l='Item',w=170),dict(k='ativo',l='Ativo · leitura',w=215),dict(k='oque',l='O que',w=230),dict(k='prazo',l='Prazo',t='num',w=110),
            dict(k='pecas',l='Peças',w=110),dict(k='prox',l='A fazer',w=230,pq='situacao')],'g_so')   # "Próximo passo" quebrava o cabeçalho
    g_om=G([dict(k='om',l='Ordem · ativo',w=180),dict(k='serv',l='Serviço · tipo',w=210),dict(k='jan',l='Janela',t='date',w=80),dict(k='fase',l='Fase',w=130),
            dict(k='pend',l='Pendência',w=130,multi=True),dict(k='exe',l='Executante',w=90),dict(k='tempo',l='Tempo',t='num',w=70),dict(k='custo',l='Custo',t='num',w=100)],'g_om',cartoes='externo')   # DS VIS-05: Cartões entra no seletor Lista | Cartões | Kanban da tela
    L_=ui37.MF_LBL.format(MUTED=MUTED); S_=ui37.MF_SEL.format(LINE=LINE,SURF=SURF,INK=INK)
    fsel=lambda rot,val,setfn,lst: (f'<label style="{L_}">{rot}<select aria-label="Filtrar por {rot.lower()}" value="{H(val)}" onChange="{H(setfn)}" style="{S_}">'
                                    + FOR(lst,'o',f'<option value="{H("o.v")}">{H("o.t")}</option>',3) + '</select></label>')
    semp=IF('at_semp_tem',f'<button type="button" data-filtro-tela="pendencia" aria-pressed="{H("at_semp_on")}" title="{H("at_semp_lab")}" onClick="{H("at_semp_go")}" style="{H("at_semp_st")}">Sem plano <span style="opacity: .75;">{H("at_semp_n")}</span></button>')
    modo_at=(f'<div role="group" aria-label="Mostrar" style="display: flex; gap: 6px;">'
             + FOR('at_modos','x',f'<button type="button" aria-pressed="{H("x.on")}" onClick="{H("x.go")}" style="{H("x.st")}">{H("x.t")}</button>',2) + '</div>')
    g_at=G([dict(k='ativo',l='Ativo · local',w=175),dict(k='plano',l='Plano',w=150),dict(k='cond',l='Condição',w=110),dict(k='leit',l='Leitura',t='num',w=105),dict(k='prox',l='Próxima',t='num',w=115,pq='quando'),
            dict(k='ab',l='Em aberto',w=140),dict(k='custo',l='Custo no mês',t='num',a='r',d=2,pre='R$ ',agg='sum',w=100),dict(k='cons',l='Consumo',w=95,ajuda='Consumo do último abastecimento de tanque cheio a tanque cheio (L/h); o selo mostra o desvio da referência do ativo.')],'g_at',total=True,
           qf=dict(k='cond',l='condição'),busca_extra=semp+fsel('Pendência','f_pend','f_setpend','f_pends'))
    g_ab=G([dict(k='id',l='Lançamento',w=130),dict(k='ativo',l='Ativo',w=170),dict(k='tq',l='Tanque/lote',w=130),dict(k='vol',l='Volume (L)',t='num',a='r',w=75),
            dict(k='data',l='Data · leitura',w=100),dict(k='met',l='Método',w=150),dict(k='lh',l='Consumo',t='num',a='r',w=80),dict(k='qual',l='Qualidade',w=135)],'g_ab',qf=dict(k='qual',l='qualidade'))
    g_pl=G([dict(k='nome',l='Plano',w=230),dict(k='grupo',l='Grupo',w=110),dict(k='est',l='Estado',w=110),dict(k='apl',l='Aplica-se a',w=190),dict(k='svs',l='Serviços',w=140),dict(k='atv',l='Ativos',w=115),dict(k='sit',l='Situação',w=140)],'g_pl')
    linha=lambda *xs: '<div class="ma-flt" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">'+''.join(xs)+'</div>'
    chipsN=lambda lst,lab,n,pre='x': (f'<div role="group" aria-label="{lab}" style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">'
                                       + FOR(lst,pre,f'<button type="button" aria-pressed="{H(pre+".on")}" data-dica="{H(pre+".dica")}" onClick="{H(pre+".go")}" style="{H(pre+".st")}">{H(pre+".t")} '
                                             + IF(pre+'.temN',f'<span style="{H(pre+".nst")}">{H(pre+".n")}</span>',True) + '</button>',n) + '</div>')
    # ---- Sem ordem ----
    semordem=_blo(bloco('Pendências por prazo','',linha(chipsN('so_prazo','Prazo pelo início da janela',3)) + g_so))
    # ---- Ordens ----
    semana=IF('semana',f'<div role="note" aria-label="Esta semana" style="display: flex; flex-direction: column; gap: 4px; padding: 10px 12px; border-radius: 12px; background: {BG};">'
              f'<div style="{SECT}">Esta semana · por dia · capacidade da oficina não calculável (sem P10)</div>'
              + FOR('sem_dias','d',f'<div style="display: flex; gap: 10px; flex-wrap: wrap; font-size: 12.8px;"><b style="min-width: 90px;">{H("d.t")}</b><span>{H("d.oms")}</span><span style="color: {MUTED};">{H("d.hh")}</span></div>',3) + '</div>')
    modos=(f'<div class="g2visoes-w"><div class="g2visoes" role="toolbar" aria-label="Visão das ordens">'
           + FOR('om_modos','x',f'<button type="button" data-i="{H("x.i")}" aria-label="{H("x.t")}" data-dica="{H("x.t")}" aria-pressed="{H("x.on")}" onClick="{H("x.go")}">'
                 + IF('x.li',icon('v_lista',16),True) + IF('x.ca',icon('v_cartoes',16)) + IF('x.ka',icon('v_kanban',16)) + '</button>',3) + '</div></div>')
    mais_om=E.mais('Ordens por fase',[('Ver carga desta semana',H('om_semana_go')),('Ver ordens que esperam peça',H('om_peca_go'))])
    ordens=_blo(bloco('Ordens por fase','',
                      linha(chipsN('fchips','Filtrar por fase',6,'fc'),chipsN('rotinas','Rotina',2),'<span style="flex-grow: 1;"></span>',mais_om,modos)
                      + semana + IF('om_lista',g_om,True) + IF('om_kanban',_kanban())))
    # ---- Ativos | Abastecimentos: a escolha fica na linha do título do bloco, à direita (como a troca de visão do "Ordens por fase") ----
    # a classe ma-gat (desenho da linha no celular) vai na própria caixa da grade: a caixa abre o corpo do bloco e o título fica sem linha (SEP-20261015 b)
    g_at=g_at.replace('<div class="g2caixa"','<div class="g2caixa ma-gat"',1)
    ativos=(IF('at_ativos',_blo(bloco('Ativos por condição','',g_at,acao=modo_at)),True) + IF('at_abast',_blo(bloco('Abastecimentos por qualidade','',g_ab,acao=modo_at))))
    # ---- Planos ----
    planos=_blo(bloco('Planos e cobertura','',
                 # faixa com fundo logo abaixo do título: a borda neutra (que some dentro do bloco, SEP_CSS) diz ao separador que não precisa de linha
                 IF('tem_sem',f'<div class="ma-sem" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 10px 12px; background: {BG}; border: 1px solid {LINE}; border-radius: 12px;">'
                    f'<span style="font-size: 12.5px; font-weight: 800;">{H("sem_n")}</span>'
                    + FOR('sem','a',f'<button type="button" onClick="{H("a.go")}" aria-label="{H("a.lab")}" title="{H("a.lab")}" style="{_MINI}">{H("a.t")} · Criar plano</button>',4) + '</div>')
                 + g_pl))
    # ---- fileira das visões (a única acima do bloco) e faixa Filtros ----
    sel=(f'<div class="ma-vis" role="group" aria-label="Visão" style="display: flex; flex-wrap: wrap; gap: 6px;">'
         + FOR('vis','x',f'<button type="button" aria-pressed="{H("x.on")}" aria-label="{H("x.lab")}" data-dica="{H("x.dica")}" onClick="{H("x.go")}" style="{H("x.st")}">{H("x.t")}'
               + IF('x.temN',f'<span style="{H("x.nst")}">{H("x.n")}</span>') + '</button>',4) + '</div>'
         f'<label class="ma-vis-m" style="align-items: center; gap: 8px; {LBL}">Visão<select aria-label="Visão" value="{H("vis_k")}" onChange="{H("vis_set")}" style="{INP} font-weight: 700;">'
         + FOR('vis','x',f'<option value="{H("x.k")}">{H("x.opt")}</option>',4) + '</select></label>')
    faixa=ui37.faixa_filtros(IF('flt_tipo',fsel('Tipo','f_tipo','f_settipo','f_tipos'),True) + IF('flt_crit',fsel('Criticidade','f_crit','f_setcrit','f_crits'),True)
                             + fsel('Grupo','f_grupo','f_setgrupo','f_grupos'))
    col=lambda x: f'<div style="display: flex; flex-direction: column; gap: 10px; min-width: 0;">{x}</div>'
    return (IF('lista',col(sel + f'<div class="ma-fx">{faixa}</div>' + IF('v_semordem',semordem,True) + IF('v_ordens',ordens) + IF('v_ativos',ativos) + IF('v_planos',planos)),True))

def _cas(lst):
    """Conflitos do app (S4): o registro feito sem sinal que encontrou a ordem mudada; Otávio aplica ou descarta com motivo."""
    return IF(lst.replace('cas','hasCa'),FOR(lst,'x',f'<div role="alert" style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.8px; font-weight: 700;">{H("x.t")}'
        f'<span style="font-weight: 600;">{H("x.s")}</span><div style="display: flex; gap: 8px; flex-wrap: wrap;">'
        f'<button type="button" disabled="{H("x.dis")}" title="{H("x.why")}" onClick="{H("x.ap")}" style="{_MINI}">Aplicar registro do app</button>'
        f'<input aria-label="{H("x.dlab")}" placeholder="Motivo para descartar" value="{H("x.dmv")}" onChange="{H("x.dset")}" disabled="{H("x.dis")}" style="{INP} flex: 1 1 160px; font-size: 12.5px;">'
        f'<button type="button" disabled="{H("x.dis")}" title="{H("x.why")}" onClick="{H("x.ds")}" style="{_MINI}">Descartar · motivo</button></div>'
        + IF('x.hasWhy',f'<span style="font-size: 12px; font-weight: 600;">{H("x.why")}</span>') + '</div>',1))
def _pag_ativo():
    G=lambda cols,gid,search=False: grid(cols,[],edit=dict(m='pick'),gid=gid,total=False,search=search)
    d_venc=G([dict(k='serv',l='Serviço · plano',w=230),dict(k='sit',l='Situação',w=170),dict(k='prox',l='Próximo',t='num',w=170),dict(k='om',l='Ordem',w=170)],'d_venc')
    d_ach=G([dict(k='id',l='Achado',t='date',w=150),dict(k='comp',l='Componente · sintoma',w=280),dict(k='crit',l='Criticidade',w=110),dict(k='est',l='Estado',w=190)],'d_ach')
    d_om=G([dict(k='om',l='Ordem · ativo',w=140),dict(k='serv',l='Serviço · tipo',w=220),dict(k='jan',l='Janela',t='date',w=90),dict(k='fase',l='Fase',w=120),dict(k='custo',l='Custo',t='num',w=130)],'d_om',True)
    d_lei=G([dict(k='data',l='Data',t='date',w=100),dict(k='val',l='Leitura · volume',t='num',w=130),dict(k='orig',l='Origem',w=280),dict(k='qual',l='Qualidade',w=150)],'d_lei',True)
    cab=(f'<div style="display: flex; align-items: flex-start; gap: 12px; flex-wrap: wrap;"><div style="display: flex; flex-direction: column; gap: 6px; flex: 1 1 320px; min-width: 0;">'
         f'<button type="button" onClick="{H("voltar")}" style="{LNK} align-self: flex-start;">‹ Ativos</button>'
         f'<h2 style="margin: 0; font-family: {DISP}; font-size: 21px; letter-spacing: -.02em;">{H("at_t")}</h2><span style="font-size: 13px; color: {MUTED};">{H("at_sub")}</span>'
         f'<span style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">{_chiph("at_cond","at_cst","at_cdot")}<span style="font-size: 12.5px; font-weight: 600;">{H("at_leit")}</span></span>'
         + f'<span class="ma-atpl" style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; font-size: 13px;"><span style="{LBL}">Plano</span>'
         + FOR('at_pls','x',f'<a href="{H("x.h")}" style="color: {ACC}; font-weight: 800; text-decoration: none;">{H("x.t")} ›</a>{_chiph("x.s","x.st","x.dot")}',1)
         + IF('at_semPl',f'<button type="button" onClick="{H("at_semPlGo")}" style="{LNK}">{H("at_semPlt")}</button>') + '</span></div>'
         f'<div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">{_btns("at_secs")}'
         + IF('at_prim',f'<button type="button" disabled="{H("at_pdis")}" title="{H("at_pwhy")}" onClick="{H("at_pfn")}" style="{H("at_pst")}">{H("at_pt")}</button>')
         + f'</div></div>'
         f'<div style="display: flex; gap: 14px; flex-wrap: wrap;"><a href="{H("at_cd03")}" style="color: {ACC}; font-weight: 700; font-size: 13px; text-decoration: none;">Abrir no CD-03 ›</a>'
         f'<a href="{H("at_rec")}" style="color: {ACC}; font-weight: 700; font-size: 13px; text-decoration: none;">Ver agenda em O.S. › Recursos ›</a></div>')
    sit=(_kv('at_kv',4)
         + f'<div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;"><button type="button" disabled="{H("at_mudar_dis")}" title="{H("at_mudar_why")}" onClick="{H("at_mudar")}" style="{LNK}">Mudar condição ›</button>'
         + IF('at_mudar_dis',f'<span style="font-size: 12px; color: {MUTED};">{H("at_mudar_why")}</span>') + '</div>'
         + _lab('Agenda da semana (O.S. › Recursos)') + FOR('at_agenda','x',f'<div style="font-size: 12.8px;">{H("x.t")}</div>',2)
         + IF('at_semAgenda',f'<div style="font-size: 12.8px; color: {MUTED};">Sem alocação nas O.S. a partir de hoje.</div>')
         + _lab('Histórico da condição') + FOR('at_hist','x',f'<div style="font-size: 12.5px; color: {MUTED};">{H("x.t")}</div>',2))
    venc=(d_venc + IF('at_semPl',f'<div><button type="button" onClick="{H("at_semPlGo")}" style="{LNK}">{H("at_semPlt")}</button></div>'))
    corpo=(cab + _cas('at_cas') + _blk('abk_','sit',sit) + _blk('abk_','venc',venc) + _blk('abk_','ach',d_ach) + _blk('abk_','om',d_om) + _blk('abk_','lei',d_lei) + _blk('abk_','cus',_kv('at_cn',3)))
    return IF('pg_ativo',f'<div style="display: flex; flex-direction: column; gap: 10px;">{corpo}</div>')

def _pag_plano():
    d_vinc=grid([dict(k='ativo',l='Ativo',w=180),dict(k='base',l='Base de contagem',w=170),dict(k='prox',l='Próximo vencimento',w=240),dict(k='sit',l='Situação',w=130),dict(k='om',l='Ordem',w=150)],[],
                edit=dict(m='pick'),gid='d_vinc',total=False,search=False,dele=True,menu_linha=True)   # MA-VINCULO: ⋯ da linha com "Desvincular" (TAB-05)
    tk=(f'<li style="display: flex; align-items: center; gap: 8px; padding: 5px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
        f'<span style="font-size: 12px; font-weight: 800; color: {MUTED}; width: 18px; flex-shrink: 0;">{H("t.n")}</span><span style="flex-grow: 1; min-width: 0;">{H("t.t")}</span>'
        f'<span style="font-size: 11.5px; font-weight: 700; color: {MUTED}; border: 1px solid {LINE}; border-radius: 999px; padding: 0 7px;">{H("t.tipo")}</span>'
        f'<button type="button" class="pm-x" aria-label="{H("t.rlab")}" title="Retirar tarefa" onClick="{H("t.rm")}">×</button></li>')
    pc=(f'<div style="display: grid; grid-template-columns: minmax(0, 1fr) 70px auto 26px; gap: 8px; align-items: center; padding: 5px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
        f'<span style="min-width: 0;">{H("p.nome")}</span><span style="text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap;">{H("p.q")}</span><span style="{H("p.st")}">{H("p.saldo")}</span>'
        f'<button type="button" class="pm-x" aria-label="{H("p.rlab")}" title="Retirar peça" onClick="{H("p.rm")}">×</button></div>')
    inl=f'font-family: inherit; font-size: 13px; padding: 6px 9px; border-radius: 8px; border: 1px solid {LINE}; box-sizing: border-box; background: #fff; color: {INK};'
    det=(f'<div class="pm-sv-det" id="{H("s.did")}" role="region" aria-label="{H("s.dlab2")}">'
         f'<div style="display: flex; flex-direction: column; gap: 4px; min-width: 0;"><div style="{SECT}">Checklist · {H("s.ntar")}</div>'
         f'<ol style="margin: 0; padding: 0; list-style: none;">' + FOR('s.tarefas','t',tk,4) + '</ol>'
         + IF('s.semTar',f'<span style="font-size: 12.5px; color: {RED}; font-weight: 700;">Sem tarefas · inclua o checklist antes de publicar.</span>')
         + f'<div style="display: flex; gap: 6px; padding-top: 6px; flex-wrap: wrap;"><select aria-label="{H("s.tktlab")}" value="{H("s.tktipo")}" onChange="{H("s.tksett")}" style="{inl}">'
           + FOR('s.tktipos','o',f'<option value="{H("o.v")}">{H("o.t")}</option>',4) + '</select>'
           f'<input id="{H("s.tkid")}" aria-label="{H("s.tklab")}" placeholder="Nova tarefa" value="{H("s.tkv")}" onChange="{H("s.tkset")}" onKeyDown="{H("s.tkkey")}" style="{inl} flex: 1 1 160px; min-width: 0;">'
           f'<button type="button" onClick="{H("s.tkadd")}" style="{_MINI}">Incluir tarefa</button></div>' + IF('s.tkHasErr',f'<span role="alert" style="{ERRS}">{H("s.tkerr")}</span>') + '</div>'
         f'<div style="display: flex; flex-direction: column; gap: 4px; min-width: 0;"><div style="{SECT}">Peças e lubrificantes do estoque</div>'
         + IF('s.temPecas',FOR('s.pecas','p',pc,2)) + IF('s.semPecas',f'<span style="font-size: 12.5px; color: {MUTED};">Sem peças.</span>')
         + f'<div style="display: flex; gap: 6px; padding-top: 6px; flex-wrap: wrap; align-items: center;"><select id="{H("s.pcid")}" aria-label="{H("s.pclab")}" value="{H("s.pcitem")}" onChange="{H("s.pcsetitem")}" style="{inl} flex: 1 1 180px; min-width: 0;">'
           + FOR('s.pcopts','o',f'<option value="{H("o.v")}">{H("o.t")}</option>',4) + '</select>'
           f'<input id="{H("s.pcqid")}" aria-label="{H("s.pcqlab")}" placeholder="Qtd" inputMode="decimal" value="{H("s.pcq")}" onChange="{H("s.pcsetq")}" onKeyDown="{H("s.pckey")}" style="{inl} width: 70px; text-align: right;">'
           f'<span style="font-size: 12px; color: {MUTED}; min-width: 18px;">{H("s.pcun")}</span><button type="button" onClick="{H("s.pcadd")}" style="{_MINI}">Incluir peça</button></div>'
         + IF('s.pcHasErr',f'<span role="alert" style="{ERRS}">{H("s.pcerr")}</span>') + '</div></div>')
    svrow=(f'<div class="pm-sv" style="{H("s.rst")}"><div class="pm-sv-linha">'
           + E.seta_abrir(H("s.open"),H("s.lab"),H("s.tog"),controla=H("s.did")) +
           f'<span style="display: flex; flex-direction: column; gap: 3px; min-width: 0; align-items: flex-start;"><button type="button" class="pm-nome" onClick="{H("s.edit")}" title="Editar gatilhos, tolerância, tempo e especialidade">{H("s.nome")}</button>'
           + IF('s.hasChg',f'<span style="{H("s.chgst")}">{H("s.chg")}</span>') + '</span>'
           f'<span style="display: flex; flex-direction: column; gap: 2px; min-width: 0;"><b style="font-weight: 700;">{H("s.gat")}</b><span style="font-size: 12px; color: {MUTED};">{H("s.tol")}</span>'
           + IF('s.hasCum',f'<span style="font-size: 12px; color: {MUTED};">{H("s.cum")}</span>') + '</span>'
           f'<span style="font-size: 12.5px; color: {MUTED};">{H("s.cont")}</span><span style="font-size: 12.5px;">{H("s.tempo")}</span>'
           + IF('s.podeDel',f'<button type="button" class="g2del" aria-label="{H("s.dlab")}" title="Excluir serviço (só no rascunho)" onClick="{H("s.ask")}">{E._TRASH}</button>',True)
           + IF('!s.podeDel','<span></span>') + '</div>'
           + IF('s.asking',f'<div role="alert" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 8px 12px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">'
                f'<span style="flex-grow: 1;">{H("s.delmsg")}</span><button type="button" onClick="{H("s.yes")}" style="{_MINI} color: {RED}; border-color: {RED};">Excluir serviço</button><button type="button" onClick="{H("s.no")}" style="{_MINI}">Manter</button></div>')
           + IF('s.isOpen',det) + '</div>')
    cab=(f'<button type="button" onClick="{H("voltarPl")}" style="{LNK} align-self: flex-start;">‹ Planos</button>'
         f'<div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;"><h2 style="margin: 0; font-family: {DISP}; font-size: 20px; letter-spacing: -.02em;">{H("p_nome")}</h2>'
         f'<span style="{H("p_est_st")}">{H("p_est")}</span><span style="font-size: 13px; color: {MUTED};">{H("p_meta")}</span><span style="flex-grow: 1;"></span>'
         + _btns('p_secs')
         + IF('p_prim',f'<button type="button" disabled="{H("p_pdis")}" title="{H("p_pwhy")}" onClick="{H("p_pfn")}" style="{H("p_pst")}">{H("p_pt")}</button>')
         + '</div>' + IF('p_pdis',f'<div style="font-size: 12px; font-weight: 700; color: {MUTED};">{H("p_pwhy")}</div>')
         + IF('inat_ask',f'<div role="alert" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 10px 14px; border-radius: 12px; background: {REDS}; color: {RED}; font-size: 13px; font-weight: 700;">'
              f'<span style="flex-grow: 1; min-width: 0;">{H("inat_t")}</span><button type="button" onClick="{H("inat_yes")}" style="{_MINI} color: {RED}; border-color: {RED};">Inativar mesmo assim</button>'
              f'<button type="button" onClick="{H("inat_no")}" style="{_MINI}">Manter ativo</button></div>'))
    ban=(IF('ban_r',f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 8px 14px; border-radius: 12px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700;">'
            f'<span style="flex-grow: 1; min-width: 0;">{H("ban_t")}</span>'
            + IF('nodisc',f'<button type="button" onClick="{H("disc_ask")}" style="{_MINI}">Descartar rascunho</button>',True)
            + IF('disc',f'<span role="alert" style="flex-basis: 100%; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; color: {RED};"><span style="flex-grow: 1;">{H("disc_t")}</span>'
                 f'<button type="button" onClick="{H("disc_yes")}" style="{_MINI} color: {RED}; border-color: {RED};">Descartar rascunho</button><button type="button" onClick="{H("disc_no")}" style="{_MINI}">Manter</button></span>')
            + '</div>')
         + IF('ban_n',f'<div style="padding: 8px 14px; border-radius: 12px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700;">Rascunho v1 · publique para o plano gerar vencimentos.</div>')
         + IF('ban_i',f'<div style="padding: 8px 14px; border-radius: 12px; background: {GRAYS}; color: {INK}; font-size: 13px; font-weight: 700;">Inativo · não gera vencimentos; as ordens abertas seguem.</div>'))
    svs=(IF('sv_tem',f'<div style="display: flex; flex-direction: column; gap: 8px;">' + FOR('svs','s',svrow,2) + '</div>')
         + IF('sv_vazio',f'<div style="padding: 14px; background: {BG}; border-radius: 12px; font-size: 13px;">Nenhum serviço ainda · use “Incluir serviço”.</div>'))
    hist=(f'<section class="ma-bl"><button type="button" class="ma-blh" aria-expanded="{H("hist_exp")}" onClick="{H("hist_tog")}">{E.seta()}Versões</button>'
          + IF('hist_open','<div class="ma-bl-c">'+FOR('hist','h',f'<div style="display: grid; grid-template-columns: 48px 200px 110px; gap: 10px; align-items: center; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
                f'<b>{H("h.t")}</b><span style="color: {MUTED};">{H("h.at")}</span><span><span style="{H("h.stst")}">{H("h.st")}</span></span></div>',2)+'</div>') + '</section>')
    inat=IF('p_podeInat',f'<div><button type="button" onClick="{H("p_inat")}" title="Para de gerar vencimentos; nada é apagado" style="{LNK} color: #4B5A51;">⋯ Inativar plano</button></div>')
    corpo=(cab + ban + f'<section aria-label="Serviços" style="display: flex; flex-direction: column; gap: 8px;">{_lab("Serviços")}{svs}</section>'
           + f'<section aria-labelledby="pm-atv-t" style="display: flex; flex-direction: column; gap: 8px;"><div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">'
             f'<h3 id="pm-atv-t" style="{SECT} margin: 0;">Ativos deste plano · {H("p_nvinc")}</h3><span style="font-size: 12.5px; color: {MUTED};">{H("p_apl")}</span><span style="flex-grow: 1;"></span>'
             + IF('p_temVl',f'<span style="font-size: 12px; color: {MUTED};">{H("p_vlNc")}</span><button type="button" class="ma-hb" disabled="{H("p_vldis")}" title="{H("p_vlwhy")}" onClick="{H("p_vl")}" style="{SEC}">{H("p_vlt")}</button>'
                  + IF('p_vldis',f'<span style="font-size: 12px; font-weight: 700; color: {MUTED};">{H("p_vlwhy")}</span>'))
             + '</div>' + IF('p_semVinc',f'<div style="padding: 10px 12px; background: {BG}; border-radius: 12px; font-size: 13px;">Nenhum ativo vinculado: o plano não gera vencimentos.</div>')
             + IF('!p_semVinc',d_vinc,True) + '</section>' + hist + inat)
    return IF('pg_plano',f'<div style="display: flex; flex-direction: column; gap: 12px;">{corpo}</div>')

PM_CSS=('.pm-sv{border:1px solid #E4E9E5;border-radius:12px;background:#fff}'
        '.pm-sv-linha{display:grid;grid-template-columns:max(30px,var(--g2seta-alvo)) minmax(0,1.1fr) minmax(0,1.6fr) 130px 160px 34px;gap:10px;align-items:center;padding:8px 10px;font-size:13px}'
        '.vl-lista{display:flex;flex-direction:column}.vl-l{display:grid;grid-template-columns:minmax(0,230px) minmax(0,1fr);gap:6px 14px;align-items:start;padding:10px 0;border-top:1px solid #E4E9E5}'
        '.vl-ck{display:flex;gap:10px;align-items:flex-start;min-height:40px;cursor:pointer}.vl-ck input{width:20px;height:20px;margin:1px 0 0;accent-color:#1E7A4C;flex-shrink:0}'
        '.vl-ck:has(input:disabled){cursor:default;opacity:.85}.vl-d{display:flex;flex-direction:column;gap:6px;min-width:0}.vl-in{display:flex;gap:8px 14px;flex-wrap:wrap;align-items:center}'
        '.vl-g{display:inline-flex;gap:6px;align-items:center;flex-wrap:nowrap;max-width:100%}.vl-g input[type=date]{min-width:0;flex:0 1 150px}'
        '.vl-prev{display:flex;flex-direction:column;gap:2px;padding:6px 10px;border-radius:8px;background:#F4F7F5}'
        '@media (max-width:640px){.vl-l{grid-template-columns:minmax(0,1fr)}.vl-ck{min-height:44px}.vl-in input,.vl-at{min-height:44px}.ma-atpl a{display:inline-flex;align-items:center;min-height:44px}'
        '.ma-rod>span[id$="-why"]{flex:1 1 100%!important}#dv_mot{min-height:44px}}'   # no celular o motivo da primária desligada fica numa linha e os dois botões juntos
        '.pm-sv-det{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px;padding:10px 14px 14px 50px;border-top:1px solid #E4E9E5}'
        '@media (max-width:640px){.pm-sv-linha{grid-template-columns:max(30px,var(--g2seta-alvo)) minmax(0,1fr) 34px}.pm-sv-linha>:nth-child(3),.pm-sv-linha>:nth-child(4),.pm-sv-linha>:nth-child(5){display:none}.pm-sv-det{grid-template-columns:1fr;padding-left:14px}}'
        '.pm-nome{border:0;background:transparent;padding:0;font-family:inherit;font-size:13.5px;font-weight:800;color:#15201A;cursor:pointer;text-align:left;text-decoration:underline;text-decoration-color:#C9D3CC;text-underline-offset:3px}'
        '.pm-nome:hover{color:#1E7A4C}.pm-x{width:26px;height:26px;border:0;border-radius:6px;background:transparent;cursor:pointer;color:#8A968E;font-size:16px;line-height:1;flex-shrink:0}'
        '.pm-x:hover{background:#FDE8E6;color:#B42318}')

def _painel():
    sb=f'font-size: 12.5px; color: {MUTED};'
    hd=(f'<div style="display: flex; gap: 10px; align-items: flex-start;"><div style="flex-grow: 1; min-width: 0;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; letter-spacing: -.02em;">{H("pan_t")}</h2>'
        f'<div style="font-size: 13px; color: {MUTED}; margin-top: 2px;">{H("pan_sub")}</div></div>'
        f'<button type="button" aria-label="Fechar painel" title="Fechar" onClick="{H("pan_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>')
    rec=IF('pan_rec',f'<div role="status" style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border-radius: 10px; background: {ACCS}; color: #1E6B47; font-size: 12.8px; font-weight: 700;">✓ {H("pan_rect")}'
           + IF('pan_hasProx',f'<div><button type="button" onClick="{H("pan_prox")}" style="{LNK}">{H("pan_proxt")}</button></div>') + '</div>')
    av=IF('pan_av',f'<div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.8px; font-weight: 700;">{H("pan_avt")}'
          + IF('pan_avHasIn',_fld(H('pan_avlab'),f'<input id="ma-av-in" value="{H("pan_avin")}" onChange="{H("pan_avset")}" style="{INP}">'))
          + f'<div style="display: flex; gap: 8px; flex-wrap: wrap;"><button type="button" onClick="{H("pan_avok")}" style="{_MINIP}">{H("pan_avokt")}</button><button type="button" onClick="{H("pan_avno")}" style="{_MINI}">{H("pan_avnot")}</button></div></div>')
    # ---- OM ----
    fases=(f'<div role="list" aria-label="Fases da ordem" style="display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 6px;">'
           + FOR('om_fases','s',f'<div role="listitem" aria-current="{H("s.cur")}" style="{H("s.st")}"><span style="{H("s.bst")}"></span>{H("s.t")}</div>',5) + '</div>')
    cel=lambda l,h,b=False: (f'<span style="display: inline-flex; flex-direction: column; gap: 1px; min-width: 0; flex: 1 1 0;"><span style="font-size: 10.5px; font-weight: 700; letter-spacing: .06em; color: {MUTED};">{l}</span>'
                             f'<span style="font-size: 12.5px; font-weight: {800 if b else 600}; color: {ACC if b else INK}; overflow-wrap: anywhere;">{H(h)}</span></span>')
    faixa=(f'<div aria-label="Continuidade" style="display: flex; align-items: flex-start; gap: 8px; padding: 8px 12px; background: {ACCS}; border: 1px solid {LINE}; border-radius: 12px; flex-wrap: wrap;">'
           + cel('VEIO DE','om_veio') + cel('ESTÁ AQUI','om_aqui') + cel('FALTA','om_falta') + cel('PRÓXIMA AÇÃO','om_prox',True) + '</div>')
    atv=(f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 12.8px;">{_chiph("om_cond","om_cst","om_cdot")}<span>{H("om_leit")}</span>'
         f'<button type="button" onClick="{H("om_goAt")}" style="{LNK}">{H("om_at")}</button></div>')
    jan=(f'<div style="font-size: 13px;"><b>Janela:</b> {H("om_jan")}</div>'
         + IF('om_conf',f'<div role="alert" style="padding: 7px 10px; border-radius: 8px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("om_conft")}</div>')
         + IF('om_hasImp',f'<div style="{sb}">{H("om_imp")}</div>')
         + IF('om_hasProp',f'<div style="font-size: 12.8px; font-weight: 700; color: {YEL};">{H("om_prop")}</div>')
         + IF('om_podeProp',f'<div><button type="button" disabled="{H("om_propDis")}" title="{H("om_propWhy")}" onClick="{H("om_propGo")}" style="{SEC}">Propor substituto (simulado · o PCP decide)</button></div>')
         + IF('om_janEd',f'<div style="display: flex; align-items: flex-end; gap: 8px; flex-wrap: wrap;">' + FOR('om_atalhos','x',f'<button type="button" aria-pressed="{H("x.on")}" onClick="{H("x.go")}" style="{H("x.st")}">{H("x.t")}</button>',2)
              + _fld('Dia',f'<input type="date" aria-label="Dia da janela" value="{H("om_jand")}" onChange="{H("om_setjand")}" style="{INP}">')
              + f'<button type="button" disabled="{H("om_moverDis")}" onClick="{H("om_mover")}" style="{SEC}">Mover janela</button></div>'
              + f'<div style="{sb}">{H("om_tol")}</div>')
         + f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; align-items: end;">'
         + _fld('Executante',IF('om_exeEd',_sel('om_exe','om_setexe','om_cands','Executante','om-exe'))+IF('om_exeRo',f'<span style="font-size: 13px; font-weight: 700; color: {INK};">{H("om_exeTxt")}</span>'))
         + _fld('Especialidade',f'<span style="font-size: 13px; font-weight: 700; color: {INK};">{H("om_esp")}</span>')
         + _fld('Tempo previsto · h',IF('om_exeEd',f'<input id="om-tempo" inputMode="decimal" value="{H("om_tempo")}" onChange="{H("om_settempo")}" style="{INP} width: 110px; text-align: right;">')+IF('om_exeRo',f'<span style="font-size: 13px; font-weight: 700; color: {INK};">{H("om_tempoTxt")}</span>'))
         + '</div>' + f'<div style="{sb}">{H("om_exeSug")}</div><div style="{sb}">Retorno previsto: {H("om_ret")}</div>')
    tkrow=(f'<div style="display: flex; flex-direction: column; gap: 6px; padding: 8px 0; border-top: 1px solid {LINE};">'
           f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"><span style="font-size: 12px; font-weight: 800; color: {MUTED}; width: 18px;">{H("t.n")}</span>'
           f'<span style="font-size: 13px; font-weight: 600; flex: 1 1 200px; min-width: 0;">{H("t.t")}</span>'
           f'<span style="font-size: 11px; font-weight: 700; color: {MUTED}; border: 1px solid {LINE}; border-radius: 999px; padding: 0 7px;">{H("t.tipo")}</span>'
           + IF('t.nova',f'<span style="{ma_chip_st("yellow")}">Tarefa nova</span>')
           + IF('t.fixo',f'<span style="font-size: 11px; color: {MUTED};">não excluível</span>')
           + IF('t.edR',f'<span role="group" aria-label="{H("t.t")}" style="display: inline-flex; gap: 4px; flex-wrap: wrap;">'+FOR('t.opts','b',f'<button type="button" aria-pressed="{H("b.on")}" aria-label="{H("b.lab")}" onClick="{H("b.go")}" style="{H("b.st")}">{H("b.t")}</button>',3)+'</span>')
           + IF('t.ro',_chiph('t.r','t.rst','t.rdot')) + IF('t.hasPor',f'<span style="font-size: 12px; color: {MUTED};">{H("t.por")}</span>') + '</div>'
           + IF('t.hasValIn',f'<label style="margin-left: 26px; display: inline-flex; align-items: center; gap: 6px; {LBL}">Valor<input aria-label="{H("t.vlab")}" inputMode="decimal" value="{H("t.val")}" onChange="{H("t.setval")}" style="{INP} width: 100px; text-align: right;">{H("t.un")}</label>')
           + IF('t.hasValTx',f'<span style="margin-left: 26px; font-size: 12.8px;">Medido: {H("t.valTx")}</span>')
           + IF('t.hasMotIn',f'<input aria-label="{H("t.motlab")}" placeholder="Motivo (obrigatório)" value="{H("t.mot")}" onChange="{H("t.setmot")}" style="margin-left: 26px; {INP}">')
           + IF('t.hasMotTx',f'<span style="margin-left: 26px; font-size: 12.5px; color: {MUTED};">Motivo: {H("t.mot")}</span>')
           + IF('t.hasTents',f'<div style="margin-left: 26px; display: flex; flex-direction: column; gap: 4px;">'+FOR('t.tents','x',f'<span style="{H("x.st")}"><span style="{H("x.dot")}"></span>{H("x.t")}</span>',2)+'</div>')
           + IF('t.tentEd',f'<div style="margin-left: 26px; display: flex; gap: 6px; flex-wrap: wrap; align-items: center;"><span role="group" aria-label="Resultado · {H("t.t")}" style="display: inline-flex; gap: 4px;">'
                +FOR('t.opts','b',f'<button type="button" aria-pressed="{H("b.on")}" aria-label="{H("b.lab")}" onClick="{H("b.go")}" style="{H("b.st")}">{H("b.t")}</button>',2)+'</span>'
                f'<input aria-label="{H("t.tlab")}" placeholder="Leitura do instrumento (opcional)" value="{H("t.tevid")}" onChange="{H("t.settevid")}" style="{INP} flex: 1 1 160px;">'
                + IF('t.treg',f'<button type="button" onClick="{H("t.tgo")}" style="{SEC}">{H("t.tgot")}</button>') + '</div>')
           + IF('t.hasWhy',f'<span style="margin-left: 26px; font-size: 12px; font-weight: 700; color: {MUTED};">{H("t.why")}</span>') + '</div>')
    tks=(f'<div style="{sb}">{H("om_tkn")}</div>' + FOR('om_tks','t',tkrow,5)
         + IF('om_incEd',f'<div style="display: flex; gap: 6px; flex-wrap: wrap; align-items: center; padding-top: 6px;">{_sel("om_inct","om_setinct","om_inc_tipos","Tipo da tarefa")}'
              f'<input aria-label="Nova tarefa" placeholder="Nova tarefa" value="{H("om_incx")}" onChange="{H("om_setincx")}" style="{INP} flex: 1 1 180px;"><button type="button" onClick="{H("om_inc")}" style="{_MINI}">Incluir tarefa</button></div>')
         + IF('om_incWhy',f'<div style="{sb}">Incluir tarefa: {H("om_incWhy")}</div>'))
    pcs=(IF('om_temPc',f'<div class="ma-pcs ma-pcs-h" style="display: grid; grid-template-columns: minmax(0, 1fr) 80px minmax(0, 1fr) 110px; gap: 8px; font-size: 11px; font-weight: 800; color: {MUTED}; text-transform: uppercase;"><span>Item</span><span>Planejado</span><span>Situação</span><span>Aplicado</span></div>'
             + FOR('om_pcs','p',f'<div class="ma-pcs ma-pcs-l" style="display: grid; grid-template-columns: minmax(0, 1fr) 80px minmax(0, 1fr) 110px; gap: 8px; align-items: center; padding: 5px 0; border-top: 1px solid {LINE}; font-size: 12.8px;">'
                   f'<b style="font-weight: 600;">{H("p.nome")}</b><span style="font-variant-numeric: tabular-nums;">{H("p.q")}</span>{_chiph("p.s","p.st","p.dot")}'
                   + IF('p.ed',f'<label style="display: inline-flex; align-items: center; gap: 4px;"><input aria-label="{H("p.alab")}" inputMode="decimal" placeholder="{H("p.aph")}" value="{H("p.av")}" onChange="{H("p.aset")}" style="{INP} width: 70px; text-align: right; font-size: 12.5px;">{H("p.un")}</label>')
                   + IF('p.ro',f'<span>{H("p.apl")}</span>')
                   + IF('p.hasOrig',f'<span style="grid-column: 1 / -1; margin-top: -2px; font-size: 11.5px; color: {MUTED};">{H("p.orig")}</span>') + '</div>',3))
         + IF('om_semPc',f'<div style="{sb}">Sem peças nesta ordem (corretiva nasce sem peças até “Incluir peça”, PCMS Bloco 2).</div>')
         + IF('om_temRet',_lab('Peças retiradas · nunca voltam ao estoque livre')
              + FOR('om_rets','r',f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 5px 0; border-top: 1px solid {LINE}; font-size: 12.8px;">'
                    f'<b style="font-weight: 600; flex: 1 1 200px;">{H("r.t")}</b>{_chiph("r.d","r.st","r.dot")}<span style="color: {MUTED};">{H("r.rs")}</span>'
                    + IF('r.ed',f'<span style="display: flex; gap: 6px; flex-wrap: wrap; flex-basis: 100%;"><select aria-label="{H("r.dlab")}" value="{H("r.dv")}" onChange="{H("r.setd")}" style="{INP}">'
                         + FOR('r.dests','o',f'<option value="{H("o.v")}">{H("o.t")}</option>',4) + '</select>'
                         f'<input aria-label="{H("r.rlab")}" placeholder="Responsável" value="{H("r.rv")}" onChange="{H("r.setr")}" style="{INP} flex: 1 1 140px;"><button type="button" onClick="{H("r.go")}" style="{_MINI}">Registrar destino</button></span>')
                    + '</div>',2)))
    con=(IF('om_conEd',f'<div style="display: flex; gap: 14px; flex-wrap: wrap; align-items: flex-end;">'
            + IF('om_hasCont',_fld(H('om_unl'),f'<input id="om-leitura" inputMode="decimal" value="{H("om_leitv")}" onChange="{H("om_setleit")}" style="{INP} width: 150px; text-align: right;">'))
            + f'<div style="display: flex; flex-direction: column; gap: 4px;"><span style="{LBL}">Horas de oficina · h</span><span style="display: flex; gap: 6px; align-items: center;">'
              f'<button type="button" aria-pressed="{H("om_prevOn")}" onClick="{H("om_prev")}" style="{H("om_prevSt")}">{H("om_prevt")}</button>'
              f'<input id="om-horas" aria-label="Horas de oficina" inputMode="decimal" value="{H("om_horas")}" onChange="{H("om_sethoras")}" style="{INP} width: 90px; text-align: right;"></span></div></div>'
            + IF('om_hasCont',f'<span style="{sb}">{H("om_ult")}</span>'))
         + IF('om_exRo',_kv('om_exkv',3)))
    ori=(f'<div style="font-size: 13px; font-weight: 600;">{H("om_orig")}</div>'
         + IF('om_temAch',FOR('om_achs','x',f'<div><button type="button" onClick="{H("x.go")}" style="{LNK}">Achado {H("x.t")} ›</button></div>',1))
         + IF('om_hasPl',f'<div><button type="button" onClick="{H("om_goPl")}" style="{LNK}">{H("om_plt")}</button></div>'))
    om=(fases + faixa + atv + _cas('om_cas') + _blk('obk_','jan',jan) + _blk('obk_','tk',tks) + _blk('obk_','pc',pcs) + _blk('obk_','con',con) + _blk('obk_','cus',_kv('om_kv',3)) + _blk('obk_','ori',ori))
    # ---- achado ----
    ach=(f'<div style="display: flex; gap: 6px; flex-wrap: wrap;">' + IF('ac_nova',f'<span style="{ma_chip_st("yellow")}">Nova</span>') + IF('ac_semEvid',f'<span style="{ma_chip_st("yellow")}">Sem evidência</span>') + '</div>'
         + _kv('ac_kv',2)
         + f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"><span style="{LBL}">Criticidade</span>'
         + FOR('ac_crit','x',f'<button type="button" disabled="{H("x.dis")}" aria-pressed="{H("x.on")}" onClick="{H("x.go")}" style="{H("x.st")}">{H("x.t")}</button>',3) + '</div>'
         + f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 12.8px;"><span>Ativo: {H("ac_atv")}</span><button type="button" onClick="{H("ac_mudar")}" style="{LNK}">Mudar condição ›</button></div>'
         + IF('ac_temOm',f'<div><button type="button" onClick="{H("ac_goOm")}" style="{LNK}">{H("ac_omt")}</button></div>'))
    venc=(f'<div style="font-size: 13px; font-weight: 600; line-height: 1.45;">{H("vc_calc")}</div>' + _kv('vc_kv',2)
          + IF('vc_temPc',_lab('Peças planejadas')+FOR('vc_pecas','x',f'<div style="display: flex; gap: 8px; align-items: center; font-size: 12.8px;"><span style="flex-grow: 1;">{H("x.t")}</span>{_chiph("x.s","x.st","x.dot")}</div>',2))
          + IF('vc_emDia',f'<div style="{sb}">{H("vc_emDiat")}</div>')
          + f'<div style="display: flex; gap: 12px; flex-wrap: wrap;"><button type="button" onClick="{H("vc_goPl")}" style="{LNK}">{H("vc_plt")}</button>'
          + IF('vc_temOm',f'<button type="button" onClick="{H("vc_goOm")}" style="{LNK}">{H("vc_omt")}</button>') + '</div>')
    # ---- condição ----
    cond=(IF('cd_bloqTxt',f'<div style="padding: 8px 10px; border-radius: 8px; background: {GRAYS}; font-size: 12.8px; font-weight: 600;">{H("cd_bloqTxt")}</div>')
          + _chips('cd_acoes','Ação de condição')
          + IF('cd_isB',_fld('Motivo do bloqueio',f'<input id="cd-motivo" value="{H("cd_motivo")}" onChange="{H("cd_setmotivo")}" style="{INP}">')+_fld('Evidência',f'<input value="{H("cd_evid")}" onChange="{H("cd_setevid")}" style="{INP}">')
               +_fld('Achado de origem',_sel('cd_achado','cd_setachado','cd_achs','Achado de origem'))+IF('cd_temOms',_fld('Tratar na ordem',_sel('cd_om','cd_setom','cd_oms','Ordem que trata'))))
          + IF('cd_isR',_fld('Motivo da restrição',f'<input id="cd-motivo-r" value="{H("cd_motivo")}" onChange="{H("cd_setmotivo")}" style="{INP}">')+_fld('Limites de operação',f'<input value="{H("cd_lim")}" onChange="{H("cd_setlim")}" style="{INP}">')
               +_fld('Prazo da restrição',f'<input type="date" value="{H("cd_ate")}" onChange="{H("cd_setate")}" style="{INP}">')+_fld('Evidência',f'<input value="{H("cd_evid")}" onChange="{H("cd_setevid")}" style="{INP}">'))
          + IF('cd_isE',_fld('Motivo',f'<input value="{H("cd_motivo")}" onChange="{H("cd_setmotivo")}" style="{INP}">')+_fld('Evidência (medição)',f'<input value="{H("cd_evid")}" onChange="{H("cd_setevid")}" style="{INP}">'))
          + IF('cd_isT',_fld('Responsável técnico',_sel('cd_rt','cd_setrt','cd_rts','Responsável técnico'))+_fld('Motivo',f'<input value="{H("cd_motivo")}" onChange="{H("cd_setmotivo")}" style="{INP}">'))
          + _lab('Histórico') + FOR('cd_hist','x',f'<div style="font-size: 12.5px; color: {MUTED};">{H("x.t")}</div>',2))
    leit=_kv('lt_kv',2)
    nach=(_fld('Ativo',_sel('na_aid','na_setaid','na_ativos','Ativo','na-aid')) + f'<span style="{sb}">{H("na_rt")}</span>'
          + _fld('Origem',_chips('na_orig','Origem')) + _fld('Componente',_chips('na_comp','Componente',7))
          + _fld('Sintoma',f'<textarea id="na-sint" rows="2" value="{H("na_sint")}" onChange="{H("na_setsint")}" style="{INP} resize: vertical;"></textarea>')
          + _fld('Criticidade',_chips('na_crit','Criticidade')) + _fld('Condição sugerida',_chips('na_sug','Condição sugerida'))
          + f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"><button type="button" onClick="{H("na_foto")}" style="{_MINI}">{H("na_fotot")}</button>'
          + IF('na_semEvid',f'<span style="{ma_chip_st("yellow")}">Sem evidência</span>') + '</div>'
          + IF('na_hasCont',_fld('Leitura (opcional) · '+H('na_un'),f'<input id="na-leit" inputMode="decimal" value="{H("na_leit")}" onChange="{H("na_setleit")}" style="{INP} width: 150px; text-align: right;">')+f'<span style="{sb}">{H("na_ult")}</span>')
          + IF('na_rep',f'<div role="alert" style="padding: 8px 10px; border-radius: 8px; background: {YELS}; color: {YEL}; font-size: 12.8px; font-weight: 700;">{H("na_rept")}</div>'))
    nab=(_fld('Ativo',_sel('ab_aid','ab_setaid','ab_ativos','Ativo','ab-aid'))
         + f'<div style="display: flex; align-items: flex-end; gap: 8px; flex-wrap: wrap;">{_fld("Data",_chips("ab_datas","Data"))}'
         + _fld('ou',f'<input type="date" aria-label="Data do abastecimento" max="{H("ab_max")}" value="{H("ab_data")}" onChange="{H("ab_setdata")}" style="{INP}">') + '</div>'
         + _fld('Tanque/lote',_chips('ab_tqs','Tanque/lote'))
         + f'<div style="display: flex; gap: 12px; flex-wrap: wrap;">' + _fld('Volume · L',f'<input id="ab-vol" inputMode="decimal" value="{H("ab_vol")}" onChange="{H("ab_setvol")}" style="{INP} width: 120px; text-align: right;">')
         + IF('ab_hasCont',_fld('Leitura · '+H('ab_un'),f'<input id="ab-leit" inputMode="decimal" value="{H("ab_leit")}" onChange="{H("ab_setleit")}" style="{INP} width: 140px; text-align: right;">')) + '</div>'
         + IF('ab_hasCont',f'<span style="{sb}">{H("ab_ult")}</span>')
         + _fld('Operador',_chips('ab_ops','Operador',5)) + f'<span style="{sb}">{H("ab_opsug")}</span>'
         + f'<label style="display: inline-flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600;"><input type="checkbox" checked="{H("ab_cheio")}" onChange="{H("ab_setcheio")}" style="width: 16px; height: 16px; accent-color: {ACC}; margin: 0;">Tanque cheio (método do consumo L/h)</label>'
         + f'<div style="display: flex; align-items: center; gap: 8px;"><button type="button" onClick="{H("ab_foto")}" style="{_MINI}">{H("ab_fotot")}</button><span style="{sb}">{H("ab_evid")}</span></div>')
    nlei=(_fld('Ativo',_sel('nl_aid','nl_setaid','nl_ativos','Ativo','nl-aid')) + _fld('Data',f'<input type="date" max="{H("nl_max")}" value="{H("nl_data")}" onChange="{H("nl_setdata")}" style="{INP}">')
          + _fld('Leitura · '+H('nl_un'),f'<input id="nl-leit" inputMode="decimal" value="{H("nl_leit")}" onChange="{H("nl_setleit")}" style="{INP} width: 150px; text-align: right;">') + f'<span style="{sb}">{H("nl_ult")}</span>')
    pub=(FOR('pb_dif','d',f'<div style="display: grid; grid-template-columns: 86px minmax(0, 1fr); gap: 10px; align-items: baseline; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
                       f'<span><span style="{H("d.st")}">{H("d.k")}</span></span><span><b>{H("d.n")}</b> <span style="color: {MUTED};">· {H("d.t")}</span></span></div>',2)
         + IF('pb_vazio',f'<div style="{sb}">O rascunho está igual à versão publicada.</div>')
         + f'<div style="font-size: 13px; font-weight: 600;">{H("pb_imp")}</div>'
         + IF('pb_temOab',_lab('Ordens abertas · seguem a versão em que nasceram')+FOR('pb_oab','x',f'<div style="font-size: 12.8px;">{H("x.t")}</div>',1)))
    corpo=(hd + rec + IF('pk_om',om) + IF('pk_achado',ach) + IF('pk_venc',venc) + IF('pk_cond',cond) + IF('pk_leitura',leit) + IF('pk_novoAch',nach) + IF('pk_abast',nab) + IF('pk_novaLeit',nlei) + IF('pk_pub',pub) + av)
    pe=(f'<div class="ma-pan-f">' + IF('pan_hasP',f'<button type="button" disabled="{H("pan_pdis")}" onClick="{H("pan_pfn")}" style="{H("pan_pst")}">{H("pan_pt")}</button>')
        + _btns('pan_secs') + IF('pan_hasWhy',f'<span style="font-size: 12px; font-weight: 700; color: {MUTED}; flex-basis: 100%;">{H("pan_pwhy")}</span>') + '</div>')
    return (IF('pan_open',
        IF('pan_modal',f'<button type="button" aria-label="Fechar" tabIndex="-1" onClick="{H("pan_close")}" style="position: fixed; inset: 0; z-index: 59; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>')
        + f'<aside id="ma-painel" class="{H("pan_cls")}" role="{H("pan_role")}" aria-modal="{H("pan_am")}" aria-label="{H("pan_t")}" tabIndex="-1" onKeyDown="{H("pan_key")}"><div class="ma-pan-c">{corpo}</div>{pe}</aside>')
        + f'<div class="ma-sr" role="status" aria-live="polite">{H("anun")}</div>')

def ma_chip_st(c):
    k={'green':(ACC,ACCS),'yellow':(YEL,YELS),'red':(RED,REDS),'gray':('#5B6660',GRAYS)}[c]
    return f'display: inline-flex; align-items: center; padding: 2px 9px; border-radius: 999px; font-size: 12px; font-weight: 700; white-space: nowrap; color: {k[0]}; background: {k[1]};'

# ---------- painéis do plano (formulários com Salvar/Cancelar e aviso de alterações não salvas) ----------
def _aside(pre,corpo,w=520,dyn=False):
    """dyn=True (MA-VINCULO): a primária leva o verbo e a contagem (pre_rot), fica desligada com o motivo à vista (pre_sdis, pre_swhy) e o rodapé
    gruda no fim do painel (alcançável a 390 px com a lista longa). Sem dyn, o rodapé Cancelar | Salvar de sempre."""
    if dyn:
        rod=(f'<div class="pe-form ma-rod" style="display: flex; justify-content: flex-end; align-items: center; gap: 8px; flex-wrap: wrap; padding: 10px 24px 14px; border-top: 1px solid {LINE}; position: sticky; bottom: -22px; margin: 0 -24px -22px; background: {SURF}; z-index: 2;">'
             + IF(f'{pre}_temWhy',f'<span id="{pre}-why" style="font-size: 12px; font-weight: 700; color: {MUTED}; flex: 1 1 160px; min-width: 0;">{H(pre+"_swhy")}</span>')
             + f'<button type="button" onClick="{H(pre+"_close")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" disabled="{H(pre+"_sdis")}" aria-describedby="{pre}-why" onClick="{H(pre+"_save")}" style="{H(pre+"_sst")}">{H(pre+"_rot")}</button></div>')
    else:
        rod=(f'<div class="pe-form" style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 8px; border-top: 1px solid {LINE};">'
             f'<button type="button" onClick="{H(pre+"_close")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" onClick="{H(pre+"_save")}" style="{BTN_ST(True,True)}">Salvar</button></div>')
    return IF(f'{pre}_open',
        f'<div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
        f'<button type="button" aria-label="Fechar" tabIndex="-1" onClick="{H(pre+"_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
        f'<aside id="{pre}-painel" tabIndex="-1" role="dialog" aria-modal="true" aria-label="{H(pre+"_titulo")}" onKeyDown="{H(pre+"_key")}" style="outline: none; position: relative; width: {w}px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">'
        f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1; letter-spacing: -.02em;">{H(pre+"_titulo")}</h2>'
        f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H(pre+"_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
        f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45; margin-top: -6px;">{H(pre+"_sub")}</div>'
        + IF(f'{pre}_nerr',f'<div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">Corrija os campos destacados; o que você preencheu foi mantido.</div>')
        + corpo + '<div style="flex-grow: 1;"></div>'
        + IF(f'{pre}_warn',f'<div role="alert" class="saida" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.'
             f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H(pre+"_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H(pre+"_keep")}" style="{_MINIP}">Continuar editando</button></div></div>')
        + rod + f'</aside></div>')
def _err(pre,k): return IF(f'{pre}_he{k}',f'<span role="alert" style="{ERRS}">{H(pre+"_e"+k)}</span>')
def _inp(pre,k,rot,typ='text',num=False,w=None,suf=''):
    inp=(f'<input id="{pre}_{k}" type="{typ}" value="{H(pre+"_"+k)}" onChange="{H(pre+"_set"+k)}"'+(' inputMode="decimal"' if num else '')
         +f' style="{H(pre+"_st"+k)}{(" width: "+w+";") if w else ""}{" text-align: right;" if num else ""}">')
    if suf: inp=f'<span style="display: inline-flex; align-items: center; gap: 6px;">{inp}<span style="font-size: 12.5px; color: {MUTED}; white-space: nowrap;">{suf}</span></span>'
    return f'<div style="display: flex; flex-direction: column; gap: 4px; min-width: 0;"><label for="{pre}_{k}" style="{LBL}">{rot}</label>{inp}{_err(pre,k)}</div>'
def _selp(pre,k,rot,lst,onch=None):
    return (f'<div style="display: flex; flex-direction: column; gap: 4px; min-width: 0;"><label for="{pre}_{k}" style="{LBL}">{rot}</label>'
            f'<select id="{pre}_{k}" value="{H(pre+"_"+k)}" onChange="{H(onch or (pre+"_set"+k))}" style="{H(pre+"_st"+k)}">'
            + FOR(lst,'o',f'<option value="{H("o.v")}">{H("o.t")}</option>',3) + '</select>' + _err(pre,k) + '</div>')
def _checks(lst,rotulo):
    return (f'<div role="group" aria-label="{rotulo}" style="display: flex; flex-wrap: wrap; gap: 6px;">'
            + FOR(lst,'o',f'<label style="display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px; border: 1px solid {LINE}; border-radius: 999px; font-size: 12.5px; cursor: pointer;">'
                  f'<input type="checkbox" checked="{H("o.on")}" onChange="{H("o.tog")}" style="accent-color: {ACC}; margin: 0;">{H("o.t")}</label>',4) + '</div>')
def _paineis_plano():
    tri=lambda a,b,c: f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px;">{a}{b}{c}</div>'
    sv_body=(_inp('sv','nome','Nome do serviço') + f'<div style="{SECT}">Gatilhos · o que vencer primeiro</div>'
             + tri(_inp('sv','h','A cada (h)',num=True),_inp('sv','km','A cada (km)',num=True),_inp('sv','d','A cada (dias)',num=True))
             + tri(_inp('sv','th','Tolerância ± h',num=True),_inp('sv','tkm','Tolerância ± km',num=True),_inp('sv','td','Tolerância ± dias',num=True))
             + f'<span style="font-size: 11.5px; color: {MUTED}; margin-top: -6px;">{H("sv_ghelp")}</span>'
             + _selp('sv','base','Próximo ciclo conta de','sv_bases')
             + IF('sv_temCum',f'<div style="display: flex; flex-direction: column; gap: 6px;"><span style="{LBL}">Cumpre também (uma ordem fecha os dois ciclos)</span>'+_checks('sv_cum','Serviços cumpridos junto')+'</div>')
             + f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">{_inp("sv","tempo","Tempo estimado (h)",num=True)}{_selp("sv","esp","Especialidade","sv_esps")}</div>')
    np_body=(_inp('np','nome','Nome do plano') + _selp('np','tipo','Aplica-se a','np_tipos') + IF('np_isMod',_selp('np','modelo','Modelo','np_mods'))
             + IF('np_isAtv',f'<div style="display: flex; flex-direction: column; gap: 6px;"><span style="{LBL}">Ativos</span>'+_checks('np_atvs','Ativos do plano')+_err('np','ativos')+'</div>')
             + IF('np_temAv',f'<div style="padding: 8px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">' + FOR('np_avs','a',f'<div>{H("a.t")}</div>',1) + '</div>')
             + IF('!np_novo',f'<span style="font-size: 12px; color: {MUTED}; margin-top: -6px;">{H("np_apl")}</span>')
             + IF('np_temEf',f'<div role="status" aria-label="Efeito da mudança" style="display: flex; flex-direction: column; gap: 4px; padding: 8px 12px; border-radius: 10px; background: {ACCS}; color: #1E6B47; font-size: 12.5px; font-weight: 700;">'
                  f'<span style="{SECT} color: #1E6B47;">Ao salvar</span>' + FOR('np_ef','e',f'<div>{H("e.t")}</div>',2) + '</div>')
             + IF('np_novo',_selp('np','base','Começar de','np_bases'),True))
    # MA-VINCULO: Vincular a plano (1 ou vários; SEL-04) e Desvincular
    inp=(f'<div class="vl-in"><span class="vl-g"><label for="{H("r.idd")}" style="{LBL}">Data</label><input id="{H("r.idd")}" type="date" max="{H("vl_hoje")}" value="{H("r.data")}" onChange="{H("r.setd")}" style="{H("r.std")}">'
         f'<button type="button" class="vl-at" onClick="{H("r.hoje")}" style="{_MINI}">Hoje</button></span>'
         + IF('r.cont',f'<span class="vl-g"><label for="{H("r.idl")}" style="{LBL}">Leitura</label><input id="{H("r.idl")}" inputMode="numeric" value="{H("r.leit")}" onChange="{H("r.setl")}" style="{H("r.stl")}"><span style="font-size: 12.5px; color: {MUTED};">{H("r.un")}</span>'
              + IF('r.temAtual',f'<button type="button" class="vl-at" onClick="{H("r.atual")}" style="{_MINI}">{H("r.atualT")}</button>') + '</span>')
         + '</div>' + IF('r.temEd',f'<span role="alert" style="{ERRS}">{H("r.ed")}</span>')
         + IF('r.pedeMot',f'<div class="vl-in"><label for="{H("r.idm")}" style="{LBL}">Motivo da correção</label><input id="{H("r.idm")}" value="{H("r.mot")}" onChange="{H("r.setm")}" style="{H("r.stm")}"></div>'
              + IF('r.temEm',f'<span role="alert" style="{ERRS}">{H("r.em")}</span>')))
    linha=(f'<div class="vl-l" data-aid="{H("r.id")}"><label class="vl-ck"><input type="checkbox" checked="{H("r.on")}" disabled="{H("r.dis")}" onChange="{H("r.tog")}" aria-describedby="{H("r.idx")}">'
           f'<span style="display: flex; flex-direction: column; gap: 2px; min-width: 0;"><b style="font-size: 13.5px;">{H("r.nome")}</b><span style="font-size: 12px; color: {MUTED};">{H("r.sub")}</span></span></label>'
           f'<div id="{H("r.idx")}" class="vl-d">'
           + IF('r.temErro',f'<span style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("r.erro")}</span>')
           + FOR('r.avs','x',f'<span style="font-size: 12.5px; font-weight: 700; color: {YEL};">⚠ {H("x.t")}</span>',1)
           + IF('r.mostra',f'<span style="font-size: 12.5px;">{H("r.orig")}</span>'
                + IF('r.temCorr',f'<button type="button" onClick="{H("r.corr")}" style="{LNK} align-self: flex-start;">{H("r.corrT")}</button>')
                + IF('r.inp',inp) + IF('r.temEl',f'<span role="alert" style="{ERRS}">{H("r.el")}</span>')
                + IF('r.temPrev',f'<div class="vl-prev" aria-label="Prévia do vencimento">' + FOR('r.prev','x',f'<span style="{H("x.st")}"><b>{H("x.nome")}</b> {H("x.txt")}</span>',1) + '</div>'))
           + '</div></div>')
    vl_body=(IF('vl_temFalha',f'<div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("vl_falha")}</div>')
             + IF('vl_fixo',f'<div style="font-size: 13px;"><b>{H("vl_pnome")}</b><br><span style="color: {MUTED};">{H("vl_papl")}</span></div>')
             + IF('vl_temOps',f'<div style="display: flex; flex-direction: column; gap: 6px;"><span id="vl-pl-t" style="{LBL}">Plano</span><div role="radiogroup" aria-labelledby="vl-pl-t" style="display: flex; flex-wrap: wrap; gap: 6px;">'
                  + FOR('vl_ops','o',f'<button type="button" role="radio" aria-checked="{H("o.on")}" onClick="{H("o.go")}" style="{H("o.st")}"><b>{H("o.id")}</b> · {H("o.nome")} <span style="font-weight: 600; opacity: .75;">· {H("o.n")}</span></button>',2)
                  + '</div>' + IF('vl_temOpAv',f'<span style="font-size: 12px; color: {MUTED};">{H("vl_opAv")}</span>') + '</div>')
             + IF('vl_semOps',f'<div role="note" style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700;">{H("vl_semOpsT")}'
                  f'<button type="button" onClick="{H("vl_criar")}" style="{LNK}">Criar plano ›</button></div>')
             + IF('vl_temSem',f'<div role="group" aria-labelledby="vl-sem-t" style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border-radius: 10px; background: {BG};">'
                  f'<span id="vl-sem-t" style="font-size: 13px; font-weight: 700;">{H("vl_semT")}</span><span style="display: flex; gap: 6px; flex-wrap: wrap;">'
                  f'<button type="button" aria-pressed="{H("vl_agoraOn")}" onClick="{H("vl_agora")}" style="{H("vl_agoraSt")}">Contar de agora</button>'
                  f'<button type="button" aria-pressed="{H("vl_ultOn")}" onClick="{H("vl_ult")}" style="{H("vl_ultSt")}">Informar a última execução</button></span>'
                  f'<span style="font-size: 12px; color: {MUTED};">{H("vl_semAj")}</span>' + IF('vl_temEModo',f'<span role="alert" style="{ERRS}">{H("vl_eModo")}</span>') + '</div>')
             + IF('vl_busca',f'<label style="display: flex; align-items: center; gap: 6px; padding: 4px 10px; border: 1px solid {LINE}; border-radius: 999px; background: {BG};">'
               f'<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="{MUTED}" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>'
               f'<input id="vl_q" type="search" aria-label="Buscar ativo" placeholder="Buscar ativo, modelo ou local" value="{H("vl_q")}" onChange="{H("vl_setq")}" style="font-family: inherit; font-size: 13px; border: 0; background: transparent; outline: none; flex: 1 1 auto; min-width: 0; min-height: 32px;"></label>')
             + f'<div class="vl-lista" role="group" aria-label="Ativos">' + FOR('vl_ls','r',linha,3) + IF('vl_vazio',f'<div style="font-size: 13px; color: {MUTED}; padding: 8px 0;">{H("vl_vazioT")}</div>') + '</div>')
    dv_body=(IF('dv_temFalha',f'<div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("dv_falha")}</div>')
             + f'<div style="font-size: 13px; line-height: 1.45;">{H("dv_ef")}</div>'
             + IF('dv_temOm',f'<div role="note" style="display: flex; flex-direction: column; gap: 4px; padding: 8px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">{H("dv_omT")}'
                  + FOR('dv_oms','o',f'<a href="{H("o.h")}" style="color: {YEL};">{H("o.t")} ›</a>',1) + '</div>')
             + f'<div style="display: flex; flex-direction: column; gap: 6px;"><span id="dv-m-t" style="{LBL}">Motivo</span><div role="group" aria-labelledby="dv-m-t" style="display: flex; flex-wrap: wrap; gap: 6px;">'
               + FOR('dv_ms','m',f'<button type="button" aria-pressed="{H("m.on")}" onClick="{H("m.go")}" style="{H("m.st")}">{H("m.t")}</button>',3) + '</div></div>'
             + _inp('dv','mot','Motivo (escreva ou escolha acima)'))
    return _aside('sv',sv_body,w=560)+_aside('np',np_body,w=520)+_aside('vl',vl_body,w=720,dyn=True)+_aside('dv',dv_body,w=480,dyn=True)

# =====================================================================================
def _redirect(fname,destino):
    """página antiga = só redirecionamento (fora do canvas e do Índice): leva a âncora antiga (#OM-0234, #PM-01, #novo:a14) ao endereço novo"""
    js=("(function(){var h=decodeURIComponent((location.hash||'').slice(1)),d='"+destino+"';"
        "if(/^OM-\\d+$/.test(h)) d='om='+h; else if(/^PM-\\d+$/.test(h)) d='plano='+h; else if(/^novo:/.test(h)) d='vis=planos&novo=plano:'+h.slice(5);"
        "location.replace('"+FNAME+"#'+d);})();")
    html=(f'<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
          f'<title>Manutenção</title><script>{js}</script></head><body style="font-family: system-ui, sans-serif; color: {INK};">'
          f'<p>Esta tela agora é a <a href="{FNAME}#{destino}">Manutenção</a> (uma tela com Sem ordem, Ordens, Ativos e Planos).</p></body></html>\n')
    open(os.path.join(E.P,fname),'w',encoding='utf-8').write(html)

def _status_dyn(fname,hole):
    import ui37
    p=os.path.join(E.P,fname); s=open(p,encoding='utf-8').read(); old=ui37.chip(H(hole),'red')
    assert s.count(old)==1, 'selo do cabeçalho não encontrado em '+fname
    open(p,'w',encoding='utf-8').write(s.replace(old,f'<span style="{H(hole+"_st")}"><span style="{H(hole+"_dot")}"></span>{H(hole)}</span>'))

# título de cada visão = nome do item do menu da Manutenção (ui37.MENU2, fonte única), pela âncora #vis=
VIS_TIT={h.split('#vis=')[1]:l for n,_i,its in ui37.MENU2 if n=='Manutenção' for l,h in its if '#vis=' in h}

def _titulo_dyn(fname):
    """CAB-3 (DS-MAN, 17/10/2026): o título não repete o "‹ Manutenção" — diz a visão aberta ("Ordens de manutenção"…) e a trilha diz
    "Manutenção › <visão>" (no detalhe, "› <registro>"), como "Agrícola › Ordem de Serviço". A casca escreve o título fixo da tela (o <title> da
    aba continua "Manutenção"); aqui o <h1> e a trilha vazia passam a ler a visão do estado da tela."""
    p=os.path.join(E.P,fname); s=open(p,encoding='utf-8').read()
    h1=re.search(r'(<h1 style="[^"]*">)Manutenção(</h1>)',s); assert h1 and s.count(h1.group(0))==1, 'título do cabeçalho não encontrado em '+fname
    s=s.replace(h1.group(0),h1.group(1)+H('ma_tit')+h1.group(2))
    vazio='<div style="display: flex; align-items: center; gap: 10px; font-size: 12.5px; font-weight: 500;"><span></span>'
    assert s.count(vazio)==1, 'trilha do cabeçalho não encontrada em '+fname
    sep=f' <span style="color: {MUTED};">›</span> '
    tr=(f'<span style="color: {MUTED};">Manutenção</span>{sep}' + IF('ma_tr_lista',f'<span>{H("ma_tit")}</span>',True)
        + IF('ma_tr_det',f'<span style="color: {MUTED};">{H("ma_tit")}</span>{sep}<span>{H("ma_tr_reg")}</span>'))
    open(p,'w',encoding='utf-8').write(s.replace(vazio,vazio[:-len('<span></span>')]+'<span>'+tr+'</span>'))

def ma():
    E._reset_screen(FNAME)
    EXTRA.append('<style>'+CSS+PM_CSS+'</style>')
    corpo=_visoes()+_pag_ativo()+_pag_plano()
    EXTRA.append(_painel()); EXTRA.append(_paineis_plano())
    EXTRAJS[0]=(DM.js_prefixo()+MA_JS.replace('__NAVST__',json.dumps([ui37.subnav_st(False),ui37.subnav_st(True)],ensure_ascii=False)).replace('__VISTIT__',json.dumps(VIS_TIT,ensure_ascii=False)).replace('__PRIM__',json.dumps(PRIM)).replace('__SEC__',json.dumps(SEC))+PM_JS)
    HEIGHTS37[FNAME]=1000
    # 14/10/2026 (proprietário: "tire das telas ver como simulação"): sem a faixa "Ver como"; quem age é o perfil do avatar do menu lateral (a
    # mesma fonte, g2perfil). O menu ⋯ (Restaurar demonstração) vai para o fim dos comandos do cabeçalho, sem uma linha só para ele.
    shell37('MA','Manutenção',corpo,fname=FNAME,status=(H('st_ma'),'red'),primary_html=_prim_cab()+_cabecalho(),search=False)
    _status_dyn(FNAME,'st_ma'); _titulo_dyn(FNAME)
    for f,d in REDIRECIONA.items(): _redirect(f,d)
    return FNAME

def build():
    ma()
