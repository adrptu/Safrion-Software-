"""Painel CONTROLE-02/F2; publicar só com adaptador e AL18 reais da composição."""
from pathlib import Path
from engine import BTN_ST, LINE, MUTED, SURF
from areas.analise_solo import _overlay, _cabeca

H=lambda s:'{{'+s+'}}'

def js():
    root=Path(__file__).resolve().parent
    return '\n'+(root/'plano_referencia.js').read_text()+'\n'+(root/'plano_referencia_comando.js').read_text()+'\n'+(root/'plano_referencia_ui.js').read_text()+'''
const _PR_EV=EXTRAVALS; EXTRAVALS=function(self,v){_PR_EV(self,v);planoRefVals(self,v);};
'''

def entrada():
    return f'<sc-if value="{H("pr_has")}" hint-placeholder-val="{H("false")}"><div style="display:flex;justify-content:flex-end;"><button type="button" id="pr_abrir" class="acoes-lnk" onClick="{H("pr_abrir")}" style="min-height:44px;">Comparar versões do plano</button></div></sc-if>'

def painel():
    corpo=_cabeca('pr_',chip=False)
    corpo+=f'<p role="status" style="margin:0;font-weight:700;">{H("pr_estado")}</p><p style="margin:0;color:{MUTED};font-size:13px;">{H("pr_nota")}</p>'
    corpo+=f'<sc-if value="{H("pr_temHistorico")}" hint-placeholder-val="{H("false")}"><label for="pr_versao">Versão de referência</label><select id="pr_versao" value="{H("pr_versao")}" onChange="{H("pr_trocar")}" style="min-height:44px;width:100%;"><sc-for list="{H("pr_versoes")}" as="pv" hint-placeholder-count="0"><option value="{H("pv.id")}">{H("pv.nome")}</option></sc-for></select><button type="button" onClick="{H("pr_modo")}" style="{BTN_ST(False,True)}">{H("pr_modoTexto")}</button><button type="button" onClick="{H("pr_historico")}" style="{BTN_ST(False,True)}">Consultar versão selecionada</button></sc-if>'
    corpo+=f'<sc-if value="{H("pr_temErro")}" hint-placeholder-val="{H("false")}"><p role="alert">{H("pr_erro")}</p></sc-if><sc-if value="{H("pr_previa")}" hint-placeholder-val="{H("false")}"><p>{H("pr_consequencia")}</p><ul><sc-for list="{H("pr_impedimentos")}" as="msg" hint-placeholder-count="0"><li>Revisar antes de publicar: {H("msg")}</li></sc-for><sc-for list="{H("pr_avisos")}" as="msg" hint-placeholder-count="0"><li>Aviso: {H("msg")}</li></sc-for></ul></sc-if>'
    corpo+=f'<label for="pr_busca">Buscar no conteúdo</label><input id="pr_busca" type="search" value="{H("pr_busca")}" onChange="{H("pr_buscar")}" style="min-height:44px;width:100%;box-sizing:border-box;"><span style="color:{MUTED};font-size:12px;">{H("pr_contagem")}</span>'
    corpo+=f'<sc-if value="{H("pr_vazio")}" hint-placeholder-val="{H("false")}"><p>{H("pr_vazioTexto")}</p></sc-if>'
    corpo+=f'<ul style="list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px;"><sc-for list="{H("pr_linhas")}" as="pl" hint-placeholder-count="0"><li style="border:1px solid {LINE};border-radius:10px;padding:12px;overflow-wrap:anywhere;"><b>{H("pl.entidade")}</b><div style="color:{MUTED};font-size:13px;">{H("pl.campo")} {H("pl.estado")}</div><dl style="margin:8px 0 0;"><sc-if value="{H("pr_comparando")}" hint-placeholder-val="{H("false")}"><dt>Na versão selecionada</dt><dd style="margin:0 0 8px;">{H("pl.antes")}</dd></sc-if><dt>{H("pr_valorTitulo")}</dt><dd style="margin:0;">{H("pl.depois")}</dd></dl><p style="margin:4px 0 0;font-size:12px;">{H("pl.aviso")}</p></li></sc-for></ul>'
    corpo+=f'<div class="so-pe" style="position:sticky;bottom:-20px;margin:auto -22px -20px;padding:12px 22px;background:{SURF};border-top:1px solid {LINE};display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;"><sc-if value="{H("pr_voltarPrim")}" hint-placeholder-val="{H("false")}"><button type="button" onClick="{H("pr_voltar")}" style="{BTN_ST(True,True)}">{H("pr_retorno")}</button></sc-if><sc-if value="{H("pr_voltarSec")}" hint-placeholder-val="{H("false")}"><button type="button" onClick="{H("pr_voltar")}" style="{BTN_ST(False,True)}">{H("pr_retorno")}</button></sc-if><sc-if value="{H("pr_publicacao")}" hint-placeholder-val="{H("false")}"><button type="button" onClick="{H("pr_preparar")}" style="{BTN_ST(True,True)}">Conferir publicação</button></sc-if><sc-if value="{H("pr_previa")}" hint-placeholder-val="{H("false")}"><button type="button" id="pr_publicar" disabled="{H("pr_bloqueada")}" onClick="{H("pr_confirmar")}" style="{BTN_ST(True,True)}">Publicar referência</button></sc-if></div>'
    return _overlay('pr_',720,corpo)
