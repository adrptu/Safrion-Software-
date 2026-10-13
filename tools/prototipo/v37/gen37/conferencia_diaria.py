"""CONTROLE-02: subdetalhe diário dentro dos apontamentos da O.S."""
from pathlib import Path
from engine import LINE, MUTED, RED, BTN_ST

def H(s):
    return "{{" + s + "}}"

def F():
    return H("false")


def js_nucleo():
    return Path(__file__).with_suffix('.js').read_text(encoding='utf-8')


def js_ui():
    return Path(__file__).with_name('conferencia_diaria_ui.js').read_text(encoding='utf-8')


def linha_html():
    secondary = 'font:inherit;min-height:44px;padding:8px 12px;border:1px solid '+LINE+';border-radius:8px;background:white;cursor:pointer;'
    field = 'font:inherit;min-height:44px;width:100%;box-sizing:border-box;border:1px solid '+LINE+';border-radius:8px;padding:8px;'
    return (f'<sc-if value="{H("a.cdVisivel")}" hint-placeholder-val="{F()}"><div style="padding:8px 0 12px;border-bottom:1px solid {LINE};font-size:13px;overflow-wrap:anywhere;">'
      f'<strong>{H("a.cdEstado")}</strong>'
      f'<sc-if value="{H("a.cdTemRecibo")}" hint-placeholder-val="{F()}"><p role="status" style="margin:6px 0;color:{MUTED};">{H("a.cdRecibo")}</p></sc-if>'
      f'<sc-if value="{H("a.cdFechado")}" hint-placeholder-val="{F()}"><button id="{H("a.cdOpenId")}" type="button" onClick="{H("a.cdAbrir")}" style="{secondary}">Conferir dia</button></sc-if>'
      f'<sc-if value="{H("a.cdAberto")}" hint-placeholder-val="{F()}"><section aria-label="Conferência diária" style="display:flex;flex-direction:column;gap:10px;margin-top:8px;">'
      f'<b>{H("a.cdTitulo")}</b><span>{H("a.cdContexto")}</span><span>{H("a.cdComparacao")}</span>'
      f'<span>Decisão de {H("a.cdQuem")}. Conferir mantém a fase da O.S. e os lançamentos de consumo. Divergência fica pendente de resolução.</span>'
      f'<sc-if value="{H("a.cdTemImpedimento")}" hint-placeholder-val="{F()}"><span role="status">{H("a.cdImpedimento")}</span></sc-if>'
      f'<sc-if value="{H("a.cdPode")}" hint-placeholder-val="{F()}"><label for="{H("a.cdDecId")}">Resultado da conferência</label>'
      f'<select id="{H("a.cdDecId")}" value="{H("a.cdDec")}" onChange="{H("a.cdDecSet")}" style="{field}"><option value="conferir">Conferir dia</option><option value="divergencia">Registrar divergência</option></select>'
      f'<label for="{H("a.cdMotId")}">Motivo — obrigatório para divergência ou resolução</label><textarea id="{H("a.cdMotId")}" value="{H("a.cdMot")}" onChange="{H("a.cdMotSet")}" style="{field}min-height:80px;"></textarea>'
      f'<sc-if value="{H("a.cdTemErro")}" hint-placeholder-val="{F()}"><div id="{H("a.cdErrId")}" role="alert" tabIndex="-1" style="color:{RED};">{H("a.cdErro")}</div><button type="button" onClick="{H("a.cdAtualizar")}" style="{secondary}">Rever dados atuais</button></sc-if>'
      f'<button type="button" onClick="{H("a.cdSalvar")}" style="{BTN_ST(True,True)}min-height:44px;">Registrar conferência</button></sc-if>'
      f'<button type="button" onClick="{H("a.cdVoltar")}" style="{secondary}">Voltar aos apontamentos</button></section></sc-if></div></sc-if>')
