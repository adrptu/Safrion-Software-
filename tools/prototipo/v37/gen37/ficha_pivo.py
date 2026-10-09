# -*- coding: utf-8 -*-
"""Ficha do pivô (pedido do proprietário, 09/10/2026: "na irrigação onde colocamos os dados da ficha do pivô, lâmina 21 h etc.").

O que é: a CAPACIDADE do equipamento de irrigação, registrada como está na ficha técnica do fabricante (dados sintéticos), no detalhe do
equipamento (CD-03 › Máquinas, instalações e setores › Bomba do Pivô 2 › "Ficha do pivô ›") e aberta pela Irrigação (IR-01 › setor P2 ›
"Ficha do pivô", ou IR-01.dc.html#P2:ficha) com o MESMO componente e os MESMOS dados (sem cadastro paralelo).
Fonte: dados.FICHA_PIVO (chave = equipamento do cadastro) com tempo de volta e lâmina a 100 % de dados.PIVO; vínculo pivô → talhão =
cadastro de talhões (dados.TALHOES + dados_cad.SISTEMA). A vazão da ficha é a da Irrigação (setor P2) e a do cadastro da bomba.
Conferência: lâmina pela conta = lâmina a 100 % × 100 ÷ percentímetro (Decimal); diverge quando |ficha − conta| > 0,05 mm (meia casa da
ficha, que tem uma casa). A conta só confere: não corrige a ficha. "21 h" é o regime de operação (h/dia, fora do horário de ponta), sem
outro uso. A ficha não prescreve lâmina: a lâmina a aplicar segue a política de água (PA-07) e o responsável técnico.
Água disponível no solo (CAD) do talhão: ponto de leitura nomeado (fpvCad, lê irrCadTxt da frente SOLO quando existir na tela)."""
import json
from decimal import Decimal
import dados as D
import dados_cad as DC
from engine import grid, MUTED, LINE, BG, SURF, ACC, INK, DISP, YEL, YELS

H = lambda s: '{{' + s + '}}'
MEIA_CASA = Decimal('0.05')   # tolerância da conferência: meia unidade da última casa da ficha (lâmina com 1 casa)
GID = 'g_fpv'
COLS = [dict(k='pct', l='Percentímetro', t='num', a='r', u='%', w=110), dict(k='tempo', l='Tempo de volta', t='num', a='r', u='h', d=1, w=110),
        dict(k='lam', l='Lâmina', t='num', a='r', u='mm', d=1, w=90), dict(k='conta', l='Lâmina pela conta', t='num', a='r', u='mm', d=2, w=120),
        dict(k='conf', l='Conferência', w=170)]


def dec(x):
    return Decimal(str(x))


def lamina_conta(lam100, pct):
    """lâmina (mm) ao percentímetro pct (%) pela ficha: lâmina a 100 % × 100 ÷ pct. Só conferência; não é prescrição."""
    return dec(lam100) * 100 / dec(pct)


def conferencia(f):
    """linhas da ficha (como estão) com a conta e a diferença ficha − conta; ok quando |dif| ≤ meia casa."""
    out = []
    for pct, tempo, lam in f['tabela']:
        c = lamina_conta(f['lamina_100_mm'], pct); dl = dec(lam); dif = dl - c
        out.append(dict(pct=dec(pct), tempo=dec(tempo), lam=dl, conta=c, dif=dif, ok=abs(dif) <= MEIA_CASA))
    return out


def talhoes(aid):
    """talhões irrigados pelo equipamento (cadastro de talhões: sistema e pivô/setor)."""
    nome = next(a['nome'] for a in DC.ATIVOS if a['id'] == aid)
    return [t for t, ha, cult, fase, obs in D.TALHOES if DC.SISTEMA.get(obs, ('', ''))[1] == nome]


def br(x, d):
    s = f'{float(x):,.{d}f}'
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')


def _diverge(dif):
    return 'Diverge ' + ('−' if dif < 0 else '+') + br(abs(dif), 2) + ' mm'


def dados_pagina():
    """o que a gaveta mostra, por equipamento: campos com a unidade junto do valor, linhas da tabela (texto e números para ordenar)."""
    out = {}
    pol = D.POLITICA_AGUA; rt = pol['autor'].replace(' (', ', ').replace(')', '')
    for aid, f in D.FICHA_PIVO.items():
        at = next(a for a in DC.ATIVOS if a['id'] == aid)
        tal = talhoes(aid); t0 = tal[0] if tal else ''
        ha = next((h for t, h, *_ in D.TALHOES if t == t0), None)
        conf = conferencia(f); div = [r for r in conf if not r['ok']]
        linhas = [dict(pct=br(r['pct'], 0) + ' %', t=br(r['tempo'], 1) + ' h', l=br(r['lam'], 1) + ' mm', c=br(r['conta'], 2) + ' mm',
                       conf='Confere' if r['ok'] else _diverge(r['dif'])) for r in conf]
        rows = [dict(id='p' + br(r['pct'], 0), v=dict(pct=float(r['pct']), tempo=float(r['tempo']), lam=float(r['lam']), conta=float(r['conta'])),
                     s=dict(conf=x['conf']), p=dict(conf=[dict(k='chip', t=x['conf'], c='green' if r['ok'] else 'yellow')])) for r, x in zip(conf, linhas)]
        if div:
            resumo = ((f'{len(div)} linha da ficha diverge da conta: ' if len(div) == 1 else f'{len(div)} linhas da ficha divergem da conta: ')
                      + '; '.join(f"{br(r['pct'], 0)} % · {br(r['lam'], 1)} mm na ficha × {br(r['conta'], 2)} mm pela conta" for r in div)
                      + '. Confira a ficha com o fabricante; a conta não corrige o registro.')
        else:
            resumo = 'A tabela da ficha confere com a conta em todas as linhas.'
        vz = dec(f['vazao_ls'])
        kv = [dict(l='Identificação', v=f"{f['pivo']} · setor {t0} · {at['nome']}"), dict(l='Fabricante e modelo', v=f"{f['fabricante']} · {f['modelo']}"),
              dict(l='Raio', v=f"{br(f['raio_m'], 0)} m"), dict(l='Área irrigada', v=f"{br(f['area_ha'], 0)} ha"),
              dict(l='Vazão', v=f"{br(vz, 0)} L/s · {br(vz * Decimal('3.6'), 1)} m³/h"), dict(l='Pressão', v=f"{br(f['pressao_mca'], 0)} mca"),
              dict(l='Tempo de volta a 100 %', v=f"{br(f['volta_100_h'], 1)} h"), dict(l='Lâmina a 100 %', v=f"{br(f['lamina_100_mm'], 1)} mm"),
              dict(l='Regime de operação', v=f"{f['regime_h']} h/dia · {f['regime_obs']}"),
              dict(l='Talhão', v=f"{t0} · Santa Rita" + (f" · {br(ha, 0)} ha no cadastro" if ha is not None else ''))]
        out[aid] = dict(pivo=f['pivo'], setor=t0, talhao=t0, equip=at['nome'], kv=kv, linhas=linhas, rows=rows, resumo=resumo, diverge=bool(div),
                        sub=f"{at['nome']} · irriga o talhão {t0} (Santa Rita) · ficha técnica do fabricante, registrada como está (dados sintéticos)",
                        conta=(f"Conferência: lâmina pela conta = lâmina a 100 % ({br(f['lamina_100_mm'], 1)} mm) × 100 ÷ percentímetro; diverge quando a "
                               f"diferença passa de {br(MEIA_CASA, 2)} mm (meia casa da ficha); a conta não corrige a ficha."),
                        nota=(f"Capacidade do equipamento: a ficha não prescreve lâmina. A lâmina a aplicar segue a política de água {pol['id']} "
                              f"(até {br(pol['lamina_max'], 1)} mm por passada) e o responsável técnico ({rt})."))
    return out


JS = r'''
// ===== Ficha do pivô (09/10/2026): capacidade do equipamento · o mesmo componente no CD-03 e no IR-01 (ficha_pivo.py) =====
function fpvDe(setor){ return Object.keys(FPV).find(k=>FPV[k].setor===setor)||''; }
function fpvAbrir(self,id,volta){ if(!FPV[id]) return; self.__fpvVolta=volta||null; self.setState({fpv:id});
  setTimeout(()=>{ try{ const a=document.querySelector('aside[aria-label^="Ficha do pivô"]'); if(a){ a.scrollTop=0; const b=a.querySelector('button[aria-label="Fechar"]'); if(b) b.focus(); } }catch(e){} },40); }
// fechar volta ao detalhe de onde a ficha foi aberta (equipamento no CD-03, setor no IR-01)
function fpvFechar(self){ const b=self.__fpvVolta; self.__fpvVolta=null; self.setState({fpv:null}); g2set(self,'g_fpv',{fmc:null});
  if(b&&b.gid){ const sp=GRIDS.find(g=>g.id===b.gid); if(sp) setTimeout(()=>{ if(g2find(g2rows(self,sp),b.rid)) g2open(self,sp,b.rid,null); },0); } }
// água disponível no solo (CAD) do talhão: ponto de leitura nomeado. A frente SOLO (Análises de solo) define irrCadTxt na Irrigação;
// sem ela a ficha diz, na Irrigação, que não há medição e, no cadastro, onde ler. A CAD é do solo: não muda a capacidade nem prescreve lâmina.
function fpvCad(f){ try{ if(typeof irrCadTxt==='function'&&typeof irrGet==='function'){ const s=irrGet(), x=s.setores[f.setor]; if(x) return irrCadTxt(s.faz[x.faz],f.setor,x); } }catch(e){} return ''; }
// chamada no início do PREVALS da tela: as linhas da tabela entram antes de a grade desenhar
function fpvVals(self,v){ const id=self.state.fpv, f=id?FPV[id]:null, sp=GRIDS.find(g=>g.id==='g_fpv'); v.fpv_open=!!f; v.fpv_kv=[];
  if(sp) sp.rows=f?f.rows:[]; if(!f) return;
  v.fpv_pivo=f.pivo; v.fpv_t='Ficha do pivô · '+f.pivo; v.fpv_sub=f.sub; v.fpv_kv=f.kv; v.fpv_resumo=f.resumo;
  v.fpv_rst=f.diverge?'background:#FFF3D6;color:#8A5A00;':'background:#E4F3E9;color:#1E7A4C;';
  v.fpv_nota=f.nota; v.fpv_conta=f.conta; const cad=fpvCad(f); v.fpv_cadL='Água disponível no solo (CAD) · talhão '+f.talhao;
  /* sem a leitura nesta tela: na Irrigação, não há medição (o mesmo texto da frente SOLO); no cadastro, a leitura fica no setor (não diz "sem medição", que pode ser falso) */
  v.fpv_cad=cad||(FPV_CTX==='IR'?'sem medição de água no solo neste talhão (Análises de solo)':('lida no setor '+f.setor+' da Irrigação (vem de Análises de solo)'));
  v.fpv_lkH=FPV_CTX==='IR'?('CD-03.dc.html#ficha='+id):('IR-01.dc.html#'+f.setor); v.fpv_lkT=FPV_CTX==='IR'?'Abrir no cadastro do equipamento':('Ver o setor '+f.setor+' na Irrigação');
  v.fpv_close=()=>fpvFechar(self);
  v.fpv_key=(e)=>{ if(e.key==='Escape'&&!g2st(self,'g_fpv').fmc){ e.preventDefault(); e.stopPropagation(); fpvFechar(self); } }; }
'''


def js(ctx):
    """JS da gaveta para a tela (ctx='IR' no IR-01, 'CD' no CD-03): dados da ficha + funções."""
    return ('const FPV = ' + json.dumps(dados_pagina(), ensure_ascii=False).replace('</', '<\\/') + ';\nconst FPV_CTX = ' + json.dumps(ctx) + ';\n' + JS)


def painel():
    """Gaveta "Ficha do pivô" (sub-detalhe do equipamento): campos, tabela da ficha com filtro e ordenação (G2, uma variável por
    coluna, unidade na célula), conferência, CAD do talhão (leitura) e a nota de que a ficha não prescreve lâmina."""
    F = lambda s: H('fpv_' + s)
    TH = f'font-size: 10.5px; font-weight: 700; letter-spacing: .04em; color: {MUTED}; text-transform: uppercase;'
    MUT = f'font-size: 12.8px; color: {MUTED}; line-height: 1.45;'
    LK = f'color: {ACC}; font-weight: 700; text-decoration: none; font-size: 13px;'
    lab = lambda t: f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{t}</div>'
    # barra da tabela: a origem dos números e, com filtro aplicado, os filtros com × e "Limpar filtros" (a G2 só mostra a barra com algo nela)
    g = grid(COLS, [], edit=dict(m='none'), gid=GID, search=False, total=False,
             tools=f'<span style="font-size: 12px; color: {MUTED};">Registrada como está na ficha</span>')
    kv = (f'<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 18px; padding: 12px 14px; background: {BG}; border-radius: 12px;">'
          f'<sc-for list="{F("kv")}" as="x" hint-placeholder-count="10"><div style="min-width: 0;"><div style="{TH}">{H("x.l")}</div>'
          f'<div style="font-size: 13.2px; font-weight: 600; margin-top: 2px; line-height: 1.4; overflow-wrap: anywhere;">{H("x.v")}</div></div></sc-for></div>')
    sec = lambda titulo, corpo: (f'<section aria-label="{titulo}" style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top: 1px solid {LINE};">'
                                 f'{lab(titulo)}{corpo}</section>')
    return (f'<sc-if value="{F("open")}" hint-placeholder-val="{{{{false}}}}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
            f'<button type="button" tabIndex="-1" aria-label="Fechar ficha do pivô" onClick="{F("close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
            f'<aside role="dialog" aria-modal="true" aria-label="Ficha do pivô · {F("pivo")}" onKeyDown="{F("key")}" class="fpv-gaveta" style="position: relative; width: 680px; max-width: 100%; height: 100vh; '
            f'overflow-y: auto; overflow-x: hidden; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px;"><div style="display: flex; flex-direction: column; gap: 3px; flex-grow: 1; min-width: 0;">'
            f'<h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em; line-height: 1.3;">{F("t")}</h2>'
            f'<div style="{MUT}">{F("sub")}</div></div>'
            f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{F("close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
            f'<div role="status" style="padding: 9px 12px; border-radius: 10px; font-size: 13px; font-weight: 600; line-height: 1.45; {F("rst")}">{F("resumo")}</div>'
            + kv
            + sec('Percentímetro × tempo de volta × lâmina', f'<div style="min-width: 0;">{g}</div><div style="{MUT}">{F("conta")}</div>')
            + sec('Solo do talhão', f'<div style="font-size: 12.8px; line-height: 1.45;"><b>{F("cadL")}</b><br><span style="color: {MUTED};">{F("cad")}</span></div>')
            + f'<div role="note" style="padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.8px; font-weight: 600; line-height: 1.45;">{F("nota")}</div>'
            + f'<div><a href="{F("lkH")}" style="{LK}">{F("lkT")} ›</a></div>'
            + '</aside></div></sc-if>')
