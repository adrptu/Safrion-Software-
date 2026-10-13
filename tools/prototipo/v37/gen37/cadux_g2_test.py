# -*- coding: utf-8 -*-
"""CADUX · as regras do g2test.py / cadc_g2arvore.py nas 7 telas dos Cadastros, com a seleção que abre detalhe (DEC-0910-01, SEL-01).
O g2test.py espera "clique na linha abre o formulário"; nos Cadastros a linha abre o registro em consulta e "Editar {entidade}" abre o
formulário (regra nova, R12). Este teste refaz, em cada tela, a 1440 × 900 (mouse) e a 390 × 844 (toque):
  ordena     · o cabeçalho da coluna muda a ordem (ou a lista tem menos de 2 linhas);
  abre       · o alvo da linha abre o painel em consulta (nenhum campo editável);
  teclado    · Enter no alvo da linha abre o mesmo painel; Esc fecha e devolve o foco ao alvo (só 1440);
  edita      · "Editar {entidade}" abre o formulário; nome vazio é recusado com o erro no painel;
  não salvo  · Cancelar com alteração pede confirmação; "Continuar editando" mantém o digitado;
  salva      · Salvar volta à consulta do mesmo registro e a lista mostra o valor novo;
  link       · link dentro da linha não abre o formulário.
Uso (navegador um por vez): env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpH.lock env CDP_GL=1 timeout 900 python3 cadux_g2_test.py"""
import os, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from comp_lib import Chrome, servir
from cadux_nav import Nav, alvo_linha, botao, botao_ini, PAINEL
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('OK    ' if cond else 'FALHA ') + n + ('' if cond else ' · ' + str(info)[:600]), flush=True)
# tela, endereço do registro (abre o grupo dele no mestre), id da linha, "Editar {entidade}"
TELAS = [('CD-01', '#reg=T2', 'T2', 'Editar talhão'), ('CD-02', '#reg=cv3', 'cv3', 'Editar cultivar'), ('CD-03', '#reg=a02', 'a02', 'Editar ativo'),
         ('CD-04', '#reg=p2', 'p2', 'Editar pessoa'), ('CD-05', '#reg=F03', 'F03', 'Editar parceiro'), ('CD-06', '#reg=i18', 'i18', 'Editar item'),
         ('CD-07', '#dim=natureza&cod=3.1.02', None, 'Editar código')]
EDIT = "[...document.querySelectorAll('aside[role=dialog] input:not([readonly]):not([disabled]),aside[role=dialog] select:not([disabled]),aside[role=dialog] textarea:not([readonly])')].filter(e=>e.getClientRects().length).map(e=>e.id)"
SETV = """((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
port, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
def limpa():
    c.goto(f'http://127.0.0.1:{port}/Main.dc.html', .3); J('localStorage.clear();sessionStorage.clear()')
def painel_t():
    return J(f"({PAINEL}||{{getAttribute:()=>''}}).getAttribute('aria-label')") or ''
def primeiras():
    return J("[...document.querySelectorAll('.cmd-d [role=row][data-rid]')].filter(r=>r.getClientRects().length).map(r=>r.getAttribute('data-rid'))")
try:
    for L, (w, h, toque) in (('1440', (1440, 900, False)), ('390', (390, 844, True))):
        c.aparelho(w, h, toque=toque); larga = w >= 1024
        for pag, end, rid, editar in TELAS:
            limpa(); n = Nav(c, port, toque); n.abre(pag, end, 1.0)
            if rid is None: rid = J("(()=>{ const a=document.querySelector('aside[role=dialog]'); const m=(location.hash||'').match(/(?:^|[#&])reg=([^&]+)/); return m?decodeURIComponent(m[1]):null; })()") or J("(document.querySelector('.cmd-d [role=row][data-rid] .g2alvo')||{closest:()=>({getAttribute:()=>null})}).closest('[data-rid]').getAttribute('data-rid')")
            t0 = painel_t()
            n.clica(botao_ini('×', PAINEL) if J(f"!!{botao_ini('×', PAINEL)}") else f"{PAINEL}.querySelector('button[aria-label=Fechar]')", 'fechar')
            P = f'{L} {pag}'
            chk(f'{P}: o endereço do registro abre o painel em consulta ({t0}) e fechar volta à lista', bool(t0) and not J(f"!!{PAINEL}"), [t0, painel_t()])
            # ordena
            a = primeiras()
            if len(a) >= 2 and J("!!document.querySelector('.cmd-d .g2hb')"):
                J("document.querySelector('.cmd-d .g2hb').click()"); time.sleep(.3); b = primeiras(); J("document.querySelector('.cmd-d .g2hb').click()"); time.sleep(.3); d = primeiras()
                chk(f'{P}: o cabeçalho da coluna muda a ordem', b != d or a != b, [a[:4], b[:4], d[:4]])
            # abre em consulta pelo alvo da linha
            alvo = alvo_linha(rid)
            n.clica(alvo, f'linha {rid}')
            ed = J(EDIT)
            chk(f'{P}: o alvo da linha abre o painel em consulta, sem campo editável (SEL-01)', bool(painel_t()) and ed == [], [painel_t(), ed])
            # teclado (1440): Enter no alvo abre; Esc fecha e devolve o foco
            if larga:
                n.tecla('Escape'); foco = J(f"document.activeElement===({alvo})")
                chk(f'{P}: Esc fecha o painel e devolve o foco ao alvo da linha', not J(f"!!{PAINEL}") and foco, [painel_t(), foco])
                J(f"({alvo}).focus()"); n.tecla('Enter')
                chk(f'{P}: Enter no alvo da linha abre o painel', bool(painel_t()) and J(EDIT) == [], painel_t())
            # edita: nome vazio recusado
            n.clica(botao(editar, PAINEL), editar)
            ed = J(EDIT); campo = next((i for suf in ('_nome', '_item', '_t') for i in ed if i.endswith(suf)), ed[0] if ed else None)
            chk(f'{P}: "{editar}" abre o formulário', bool(campo), ed)
            if not campo: continue
            orig = J(f"document.querySelector('#{campo}').value")
            J(f"({SETV})('#{campo}','')"); time.sleep(.2); n.clica(botao('Salvar', PAINEL), 'Salvar')
            err = J("[...document.querySelectorAll('aside[role=dialog] [role=alert]')].map(x=>x.innerText).join(' | ')")
            chk(f'{P}: nome vazio recusado com o erro no painel e o formulário aberto', bool(err) and J(EDIT) != [], [err, J(EDIT)])
            novo = (orig or 'X') + ' TESTE'
            J(f"({SETV})('#{campo}',{json.dumps(novo)})"); time.sleep(.2); n.clica(botao('Cancelar', PAINEL), 'Cancelar')
            aviso = J("document.body.innerText.indexOf('Há alterações não salvas')>=0")
            n.clica(botao('Continuar editando'), 'Continuar editando')
            chk(f'{P}: Cancelar com alteração pede confirmação; "Continuar editando" mantém o digitado', aviso and J(f"document.querySelector('#{campo}')&&document.querySelector('#{campo}').value") == novo,
                [aviso, J(f"(document.querySelector('#{campo}')||{{}}).value")])
            n.clica(botao('Salvar', PAINEL), 'Salvar', espera=.8)
            t1 = painel_t(); ed1 = J(EDIT)
            n.clica(f"{PAINEL}.querySelector('button[aria-label=Fechar]')", 'fechar')
            lin = J(f"(()=>{{ const r=document.querySelector('[data-rid={json.dumps(rid)}]'); return r?r.innerText.replace(/\\s+/g,' '):''; }})()")
            chk(f'{P}: Salvar volta à consulta do mesmo registro e a lista mostra o valor novo', bool(t1) and ed1 == [] and novo in (lin or '') + ' ' + t1, [t1, ed1, lin[:160]])
            # link dentro da linha não abre o formulário
            lk = J("(()=>{ const a=document.querySelector('.cmd-d [role=row][data-rid] a[href]'); if(!a) return 'sem link'; a.addEventListener('click',e=>e.preventDefault(),{once:true}); a.click(); return !document.querySelector('aside[role=dialog]') || ![...document.querySelectorAll('aside[role=dialog] input:not([readonly])')].length; })()")
            chk(f'{P}: link dentro da linha não abre o formulário', lk in (True, 'sem link'), lk)
            chk(f'{P}: sem erro de script', not J('window.__errs||[]'), J('window.__errs'))
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL[:12]) if FAIL else ''))
sys.exit(1 if FAIL else 0)
