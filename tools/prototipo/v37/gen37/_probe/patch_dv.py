p='areas/processo_safra.py'; s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)==1, a[:90]
    s=s.replace(a,b)
rep("""function _safhooks(self){ self.g2after=(gid,rows,r)=>{ if(gid==='g_saf' && r && String(r.id).indexOf('n')===0 && !self.state.saf){ if(!r.v.estado) r.v.estado='Rascunho'; self.setState({saf:r.id,step:2,g2toast:'Safra criada: '+r.v.nome+'. Defina os cultivos.'}); } };""",
"""function _safhooks(self){ self.g2after=(gid,rows,r,isNew)=>{ if(gid==='g_saf' && r && String(r.id).indexOf('n')===0 && !self.state.saf){ if(!r.v.estado) r.v.estado='Rascunho'; self.setState({saf:r.id,step:2,g2toast:'Safra criada: '+r.v.nome+'. Defina os cultivos.'}); }
    if(String(gid).indexOf('g_cult_')===0) cultAfter(self,gid,rows,r,isNew); };
  self.g2check=(gid,rows,r,d,isNew)=>(String(gid).indexOf('g_cult_')===0?cultCheck(self,gid,rows,r,d,isNew):null);""")
rep("""bloco('Cultivos e planos','Defina onde, o quê e quando plantar. Clique na linha para editar; clique no nome do plano para ver e ajustar as atividades deste cultivo.',cult_html)""",
"""bloco('Cultivos e planos','Defina onde, o quê e quando plantar; divida o talhão em quantas parcelas precisar. Clique na linha para editar e no nome do plano para ajustar as atividades.',cult_html)""")
anchor="""    prim=f'<button type="button" onClick="{H("prim_fn")}" style="{H("prim_st")}">{H("prim_t")}</button>'"""
panel=r'''    # ---------- painel: dividir o talhão em parcelas (sem limite de quantidade) ----------
    DV_COLS='92px 86px 124px minmax(110px,1fr) 138px 70px 90px minmax(140px,1.2fr) 32px'
    lab_row=''.join(f'<span>{x}</span>' for x in ['Parcela','Área (ha)','Cultura','Variedade','Plantio','Meta','Unidade','Plano',''])
    dv_row=(f'<div style="display: grid; grid-template-columns: {DV_COLS}; gap: 8px; align-items: center; padding: 7px 0; border-top: 1px solid {LINE};">'
            f'<input aria-label="Nome da parcela {H("r.lab")}" value="{H("r.local")}" onChange="{H("r.s_local")}" readOnly="{H("r.dis")}" style="{H("r.st_local")}">'
            f'<input aria-label="Área de {H("r.lab")} em hectares" inputMode="decimal" value="{H("r.area")}" onChange="{H("r.s_area")}" readOnly="{H("r.dis")}" style="{H("r.st_area")}">'
            f'<select aria-label="Cultura de {H("r.lab")}" value="{H("r.cult")}" onChange="{H("r.s_cult")}" disabled="{H("r.dis")}" style="{H("r.st_cult")}"><sc-for list="{H("r.oc")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>'
            f'<input aria-label="Variedade de {H("r.lab")}" value="{H("r.var")}" onChange="{H("r.s_var")}" readOnly="{H("r.dis")}" style="{H("r.st_var")}">'
            f'<input type="date" aria-label="Plantio de {H("r.lab")}" value="{H("r.plantio")}" onChange="{H("r.s_plantio")}" readOnly="{H("r.dis")}" style="{H("r.st_plantio")}">'
            f'<input aria-label="Meta de {H("r.lab")}" inputMode="decimal" value="{H("r.meta")}" onChange="{H("r.s_meta")}" readOnly="{H("r.dis")}" style="{H("r.st_meta")}">'
            f'<select aria-label="Unidade da meta de {H("r.lab")}" value="{H("r.unm")}" onChange="{H("r.s_unm")}" disabled="{H("r.dis")}" style="{H("r.st_unm")}"><sc-for list="{H("r.ou")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>'
            f'<span style="{H("r.pst")}">{H("r.plano")}</span>'
            f'<span><sc-if value="{H("r.notAsk")}" hint-placeholder-val="{H("true")}"><button type="button" class="g2del" aria-label="Excluir parcela {H("r.lab")}" title="Excluir parcela" onClick="{H("r.rm")}">×</button></sc-if></span></div>'
            f'<sc-if value="{H("r.ask")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 7px 10px; margin-bottom: 6px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("r.askMsg")}<span style="flex-grow: 1;"></span><button type="button" onClick="{H("r.rmNo")}" style="{_MINI}">Cancelar</button><button type="button" onClick="{H("r.rm")}" style="{_MINI} color: {RED}; border-color: {RED};">Excluir parcela</button></div></sc-if>'
            f'<sc-if value="{H("r.hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 12px; color: {RED}; font-weight: 700; padding: 0 0 6px;">{H("r.errMsg")}</div></sc-if>')
    EXTRA.append(
      f'<sc-if value="{H("dv_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar" onClick="{H("dv_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="{H("dv_titulo")}" onKeyDown="{H("dv_key")}" style="position: relative; width: 1060px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
      f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1;">{H("dv_titulo")}</h2><button type="button" aria-label="Fechar" onClick="{H("dv_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED};">×</button></div>'
      f'<div style="font-size: 13px; color: {MUTED};">Defina quantas parcelas precisar e os dados de cada uma; a soma não pode passar da área do talhão.</div>'
      f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 9px 12px; border-radius: 10px; background: {BG}; font-size: 13px;"><b>{H("dv_n")}</b><span style="color: {MUTED};">{H("dv_resumo")}</span><span role="status" style="{H("dv_selost")}">{H("dv_selo")}</span></div>'
      f'<sc-if value="{H("dv_hasg")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("dv_gerr")}</div></sc-if>'
      f'<div style="overflow-x: auto;"><div style="min-width: 940px;">'
      f'<div style="display: grid; grid-template-columns: {DV_COLS}; gap: 8px; font-size: 10.5px; font-weight: 700; letter-spacing: .03em; text-transform: uppercase; color: {MUTED}; padding-bottom: 4px;">{lab_row}</div>'
      f'<sc-for list="{H("dv_rows")}" as="r" hint-placeholder-count="2">{dv_row}</sc-for></div></div>'
      f'<sc-if value="{H("dv_edit")}" hint-placeholder-val="{H("true")}"><div style="display: flex; gap: 8px; flex-wrap: wrap;"><button type="button" onClick="{H("dv_add")}" style="{_MINI}">+ Adicionar parcela</button><button type="button" onClick="{H("dv_dist")}" style="{_MINI}">Distribuir área igualmente</button></div></sc-if>'
      f'<div style="flex-grow: 1;"></div>'
      f'<sc-if value="{H("dv_warn")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("dv_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H("dv_keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
      f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};"><sc-if value="{H("dv_edit")}" hint-placeholder-val="{H("true")}"><button type="button" onClick="{H("dv_close")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" onClick="{H("dv_save")}" style="{BTN_ST(True,True)}">Salvar divisão</button></sc-if>'
      f'<sc-if value="{H("dv_ro")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("dv_discard")}" style="{BTN_ST(False,True)}">Fechar</button></sc-if></div></aside></div></sc-if>')
'''
rep(anchor, panel+anchor)
open(p,'w').write(s); print('patch ok')
