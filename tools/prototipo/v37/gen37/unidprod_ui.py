# -*- coding: utf-8 -*-
"""UNID-PROD · seletor "Unidade de produtividade" (docs/unidades-produtividade/ESPECIFICACAO.md v1.1 §3; D-U01, D-U13).
Um seletor por tabela, na barra da tabela (engine.grid, tools=), com o mesmo visual nas duas telas que mostram produtividade ou meta:
Previsão e colheita (COLH) e Planejar safra (SAF). O contexto é a cultura do registro com o painel aberto; sem painel, a primeira
cultura visível na tabela, já com os filtros aplicados. A escolha é exibição: fica no navegador de quem usa (g2unidPref e g2unidSet,
bloco <perfis> do g2lib.js), nunca no cenário, e não fecha painel, rascunho, filtro nem ordenação (R-U10, R-U11).
As opções e os números vêm do conversor único de producao.js (prUnpOpcoes, prUnpInd, prUnpMeta)."""
from engine import MUTED, LINE, INK

H = lambda s: '{{' + s + '}}'

# Mesmo desenho dos controles da barra (busca e chips): pílula de 32 px no computador; abaixo de 480 px, alvo de 44 px e fonte de 16 px
# (o iOS não aproxima a tela ao focar), com quebra de linha e sem rolagem horizontal.
CSS = ('.unp{display:inline-flex;align-items:center;gap:6px;flex-wrap:wrap;max-width:100%}'
       '.unp label{font-size:12px;font-weight:700;color:' + MUTED + '}'
       '.unp select{font-family:inherit;font-size:12.5px;font-weight:700;color:' + INK + ';background:#FFFFFF;border:1px solid ' + LINE + ';'
       'border-radius:999px;padding:5px 10px;min-height:32px;max-width:100%;cursor:pointer}'
       '.unp select:focus-visible{outline:2px solid #1E7A4C;outline-offset:2px}'
       '.unp .unp-nota{flex-basis:100%;font-size:11.5px;font-weight:600;color:#8A5A00}'
       '@media (max-width:479px){.unp{width:100%}.unp select{min-height:44px;min-width:44px;font-size:16px;flex:1 1 180px}}')


def sel_html(px):
    """HTML do seletor (px = prefixo dos valores: px_on, px_lab, px_v, px_opts, px_set, px_hasnota, px_nota)."""
    return (f'<sc-if value="{H(px + "_on")}" hint-placeholder-val="{{{{true}}}}"><span class="unp" data-unp="{px}">'
            f'<label for="{px}_sel">{H(px + "_lab")}</label>'
            f'<select id="{px}_sel" aria-label="{H(px + "_lab")}" value="{H(px + "_v")}" onChange="{H(px + "_set")}">'
            f'<sc-for list="{H(px + "_opts")}" as="o" hint-placeholder-count="4"><option value="{H("o.v")}" disabled="{H("o.dis")}">{H("o.t")}</option></sc-for></select>'
            f'<sc-if value="{H(px + "_hasnota")}" hint-placeholder-val="{{{{false}}}}"><span class="unp-nota" role="note">{H(px + "_nota")}</span></sc-if>'
            f'</span></sc-if>')


# JS da tela (entra depois de producao.js e do g2lib.js): valores do seletor de uma tabela. Comentários só com /* */.
JS = r'''
/* UNID-PROD · seletor da tabela: cu = cultura do contexto; nota = motivo de um estágio mostrado sem a massa escolhida (R-U05) */
function unpVals(self,v,px,cu,nota){ v[px+'_on']=!!cu; v[px+'_opts']=[]; v[px+'_hasnota']=false; v[px+'_nota']=''; v[px+'_set']=()=>{}; if(!cu) return;
  const op=g2unidPref(cu); const ops=prUnpOpcoes(cu,'base'); const o=ops.find(x=>x.k===op&&x.ok)||ops[0]; const ped=ops.find(x=>x.k===op);
  v[px+'_lab']='Unidade de produtividade · '+cu; v[px+'_v']=o.k;
  v[px+'_opts']=ops.map(x=>({v:x.k,t:x.ok?x.rot:x.rot+' · indisponível: '+x.motivo.toLowerCase(),dis:!x.ok}));
  const n=(ped&&!ped.ok)?(ped.rot+' indisponível para '+prUn(cu).prod+': '+ped.motivo.toLowerCase()+'; mostra o Padrão.'):(nota||'');
  v[px+'_nota']=n; v[px+'_hasnota']=!!n;
  v[px+'_set']=(e)=>{ g2unidSet(cu,e.target.value); self.setState({unp:(self.state.unp||0)+1}); }; }
/* primeira cultura visível de uma grade (com busca, filtros e filtro rápido aplicados) */
function unpCultVis(self,gid,cultDe){ const sp=GRIDS.find(g=>g.id===gid); if(!sp) return ''; const st=g2st(self,gid);
  const flat=g2flat(sp,st,g2qrows(sp,st,g2disp(self,sp)),null,self.state.added||{}); for(const x of flat){ const c=cultDe(x.r); if(c) return c; } return ''; }
'''
