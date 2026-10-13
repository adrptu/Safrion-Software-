# -*- coding: utf-8 -*-
"""Teste do CD-01 · correções da verificação independente (frente cad-fazendas): talhão com parcelas em safra aberta não muda de
fazenda, mapa só mostra talhão da fazenda do mapa, "Importar geometrias" retirado, formulários de cadastro novo com texto de cadastro.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: B1, E2) sobre a seleção que abre detalhe (DEC-0910-01); roda a
lógica da página no node (cadux_node.py). Expectativas que mudaram, com o motivo:
  2, 3  o texto de criação começa por "Crie" (BOT-03: o verbo é "Criar"), não "Cadastre";
  9, 10 (página sem rolagem; legenda do mapa inteira) dependem de layout: passaram para o teste de navegador cadux_cd01_test.py
        ("a página não rola; a grade e o mapa rolam dentro do bloco"), com a mesma regra.
Uso: python3 cadf_fix_lista_test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:300] if extra and not cond else ''), flush=True)
html = open(os.path.join(HERE, 'project', 'CD-01.dc.html'), encoding='utf-8').read()
o = roda('CD-01', AUX + r'''
let x=v(); x.cd_nfaz(); v(); const F2=painel('g_faz'); OUT.d2=F2.sub; OUT.l2=rotulos('g_faz'); fecha('g_faz');
x=v(); x.cd_criar(); v(); const F3=painel('g_tal'); OUT.d3=F3.sub; OUT.l3=rotulos('g_tal'); fecha('g_tal');
x=mestre('SR'); edita('g_tal','T3'); OUT.d4=painel('g_tal').sub; OUT.l4=rotulos('g_tal');
fset('g_tal','faz','Boa Vista'); OUT.t5=salva('g_tal'); OUT.e5=errosT('g_tal'); OUT.ab5=!!painel('g_tal');
cancela('g_tal'); fecha('g_tal'); x=mestre(''); OUT.sr6=linhaTxt('g_tal','F_SR'); OUT.bv6=linhaTxt('g_tal','F_BV'); x=mestre('SR'); OUT.f6=x.mf_T3;
// ---------- talhão sem parcelas muda de fazenda ----------
x=mestre('BV'); edita('g_tal','B1'); fset('g_tal','faz','Santa Rita'); OUT.t7=salva('g_tal'); OUT.ab7=!!(painel('g_tal')&&!painel('g_tal').cons); fecha('g_tal');
x=mestre(''); OUT.sr7=linhaTxt('g_tal','F_SR');
// ---------- reativar com aviso próprio ----------
edita('g_tal','B1'); fset('g_tal','sit','Inativo'); salva('g_tal'); fecha('g_tal');
edita('g_tal','B1'); fset('g_tal','sit','Ativo'); OUT.t8=salva('g_tal'); fecha('g_tal');
OUT.ls=ls();
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 sem erro JS e "Importar geometrias" retirado da tela', not o.get('__errs') and 'Importar geometrias' not in html, o.get('__errs'))
chk('2 fazenda nova: texto de criação, sem instrução de inativar e sem campo Situação', (o.get('d2') or '').startswith('Crie a fazenda') and 'Inativa' not in (o.get('d2') or '')
    and 'Altere' not in (o.get('d2') or '') and 'Situação' not in (o.get('l2') or []), [o.get('d2'), o.get('l2')])
chk('3 talhão novo: texto de criação, sem "Área do polígono" vazio e sem Situação', (o.get('d3') or '').startswith('Crie o talhão') and 'Inativo' not in (o.get('d3') or '')
    and 'Área do polígono' not in (o.get('l3') or []) and 'Situação' not in (o.get('l3') or []) and 'Área cultivável' in (o.get('l3') or []), [o.get('d3'), o.get('l3')])
chk('4 edição do T3 mantém texto de edição, polígono e Situação', 'Altere o talhão' in (o.get('d4') or '') and 'Área do polígono' in (o.get('l4') or []) and 'Situação' in (o.get('l4') or []), [o.get('d4'), o.get('l4')])
chk('5 T3 com parcelas na safra aberta não muda de fazenda (erro no campo Fazenda)', o.get('ab5') and 'T3 tem parcelas na Safra 2026/27 da Santa Rita. Tire-as no Planejar safra antes de mudar de fazenda.' in (o.get('e5') or '')
    and 'Salvo' not in (o.get('t5') or ''), [o.get('e5'), o.get('t5')])
chk('6 depois de cancelar: T3 segue na Santa Rita (1.165,0 ha) e verde no mapa', '1.165,0 ha' in (o.get('sr6') or '') and '120,0 ha' in (o.get('bv6') or '') and o.get('f6') == '#8FD67F', [o.get('sr6'), o.get('bv6'), o.get('f6')])
chk('7 B1 sem parcelas muda para a Santa Rita', not o.get('ab7') and 'Salvo: B1 · Santa Rita.' in (o.get('t7') or '') and '1.285,0 ha' in (o.get('sr7') or '') and '9 talhões' in (o.get('sr7') or ''), [o.get('t7'), o.get('sr7')])
chk('8 reativar o B1 avisa que volta ao Planejar safra e ao Mapa', 'B1 reativado: volta ao Planejar safra e ao Mapa.' in (o.get('t8') or ''), o.get('t8'))
# 11: mapa só mostra talhão da fazenda do mapa (cadastro salvo por versão anterior com o T3 na Boa Vista)
ls = json.loads(o.get('ls') or '{}'); k = 'talhao-os-cd01-v1'
cad = json.loads(ls.get(k) or 'null') or {}
for t in cad.get('tal', []):
    if t.get('id') == 'T3': t['v']['faz'] = 'Boa Vista'
ls[k] = json.dumps(cad, ensure_ascii=False)
m = roda('CD-01', AUX + r'''let x=v(); OUT.f3=x.mf_T3; OUT.f2=x.mf_T2; OUT.tu=typeof x.mt_T3; try{ x.cd_mtu; }catch(e){} OUT.p=!!painel('g_tal');''', hash='#faz=SR',
         antes='(function(){ const o=' + json.dumps(ls, ensure_ascii=False) + '; for(const k in o) localStorage.setItem(k,o[k]); })();')
chk('11 T3 de outra fazenda não aparece no mapa da Santa Rita nem abre por ele', m.get('f3') == '#E9EEE6' and m.get('f2') == '#8FD67F' and not m.get('p') and not m.get('__errs'), m)
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
