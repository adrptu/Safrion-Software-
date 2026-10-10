# -*- coding: utf-8 -*-
"""DS-SEPARADOR, DS-HOVER, DS-RETORNO e DS-DICA (09/10/2026) · regras do módulo sem navegador: python3 ds_unit_test.py
1. node ds_unit.js: texto da dica, dicionário de estados (5 fases do Kanban) e contraste AA do hover, do realce e da dica;
2. CSS comum (engine.G2_CSS, o mesmo em toda tela): hover verde sem a camada cinza, separador, realce, barra de carga, dica e
   indisponível com motivo; nenhuma regra de hover cinza no gerador;
3. motor: a montagem e cada desenho chamam g2montou/g2mudou (ponto central, nenhuma tela chama g2flash); o aviso visível não é lido em dobro;
4. glossário e fórmula da coluna (GLOSSARIO, _formula, _ajuda_auto);
5. os tokens medidos no teste de contraste são os do engine;
6. com o build feito: toda página do project/ carrega o CSS comum do módulo; BO-02 e CF-05 mostram o motivo do indisponível em texto (DS-06).
Revisão DS (09/10): 2.4 (linha dupla, achado 5), 3.6 (selo do bloqueio, achado 6), 3.7 e 3.8 (achados 1, 3, 9, 10), 4.6 (achado 7) e 4.7 (achado 8)."""
import os, re, sys, glob, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import engine as E
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:300] if (extra != '' and not cond) else ''))

# 1 · regras puras do g2lib (node)
r = subprocess.run(['node', os.path.join(HERE, 'ds_unit.js')], capture_output=True, text=True)
print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:])
chk('1 node ds_unit.js (dica, dicionário de estados, contraste AA)', r.returncode == 0, r.stdout[-600:] + r.stderr[-300:])

# 2 · CSS comum
css = E.G2_CSS
DSH = getattr(E, 'DS_HOVER', {}); DSR = getattr(E, 'DS_RETORNO', {}); SEP = getattr(E, 'SEP_CSS', None)   # na base (ecc8b00) não existem: o teste falha sem quebrar
chk('2.1 hover: sem a camada cinza (rgba(21,32,26,.05)) nem escurecer controle claro (brightness .95)', 'rgba(21,32,26,.05)' not in E.INTERACAO_CSS and 'brightness(.95)' not in E.INTERACAO_CSS)
chk('2.2 hover: camada verde (#F2F8F4 sobre o branco) e borda #9DBFAA nos controles claros; primária só escurece', DSH.get('camada', '?') in css and 'border-color:#9DBFAA!important' in css and 'brightness(.92)' in css)
fontes = [os.path.join(HERE, f) for f in ('engine.py', 'ui37.py')] + glob.glob(os.path.join(HERE, 'areas', '*.py'))
cinza = []
for f in fontes:
    for m in re.finditer(r':hover[^{}"]*\{[^}]*background(?:-color)?:\s*(#(?:F4F6F3|E4E9E5|EEF1EE|EEF3EE|F9FBF8|F7F9F6))', open(f, encoding='utf-8').read(), re.I):
        cinza.append((os.path.basename(f), m.group(1)))
chk('2.3 nenhuma regra de hover com fundo cinza no gerador (engine, ui37, areas)', not cinza, cinza)
# revisão DS (achado 5): a exceção da linha dupla deixou de ser só a tabela emoldurada (.g2caixa): vale para todo conteúdo que começa com borda
# no topo (caixa com borda, ficha cuja 1ª célula tem border-top), que já faz o papel da linha (AG-04det, GE-05, GE-06det tinham duas linhas)
chk('2.4 separador: linha abaixo do título do bloco (sem linha dupla sobre conteúdo que começa com borda no topo), do painel lateral e .g2-cab', bool(SEP) and SEP in css
    and 'aside[role=dialog]>div:first-child:has(>h2)' in SEP and ':is([style*="border: 1px"],[style*="border-top: 1px"])' in SEP and '>:first-child>[style*="border-top: 1px"]:first-child' in SEP)
chk('2.5 realce: animação de 0,52 s e, com menos movimento, realce estático sem animação', '@keyframes g2realce' in css and '.g2-realce{animation:g2realce 0.52s' in css and re.search(r'prefers-reduced-motion:reduce\)\{\.g2-realce\{animation:none!important', css))
chk('2.6 barra de carga no topo e dica (role=tooltip criada pelo g2lib) com estilo comum', '#g2-carga{' in css and '.g2dica{' in css and '.g2dica-i{' in css)
chk('2.7 indisponível com motivo (aria-disabled) com a aparência do desabilitado', ':is(button,a)[aria-disabled=true]{opacity:.55' in css)
# PRD DS-06 e 74.5.0 (VIS-04): o motivo do indisponível fica em texto visível junto do controle, na cor do texto secundário; a dica só complementa
am = getattr(E, 'acao_motivo', None)
chk('2.8 motivo visível do indisponível: estilo comum .g2motivo (texto secundário #65736A, sem depender de ponteiro)', '.g2motivo{' in css and 'color:#65736A' in css.split('.g2motivo{', 1)[-1].split('}', 1)[0])
amh = am('<button aria-disabled="{{d}}" data-dica="{{m}}">Conciliar</button>', '{{d}}', '{{m}}') if am else ''
chk('2.9 componente comum acao_motivo: o botão e, só quando indisponível, o motivo em texto ao lado (sc-if no mesmo estado)', bool(am) and 'class="g2ind"' in amh and '<sc-if value="{{d}}"' in amh and 'class="g2motivo"' in amh and '{{m}}</span>' in amh, amh)

# 3 · motor
chk('3.1 montagem chama g2montou e cada desenho chama g2mudou (pontos centrais)', 'componentDidMount() { g2montou(this); }' in E.ENGINE_JS2 and 'g2mudou(this); }' in E.ENGINE_JS2)
lib = open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8').read()
chamadas = []
for f in glob.glob(os.path.join(HERE, 'areas', '*.py')) + [p for p in glob.glob(os.path.join(HERE, '*.js')) if os.path.basename(p) not in ('g2lib.js', 'support.js', 'ds_unit.js')]:
    if re.search(r'\bg2flash\(', open(f, encoding='utf-8').read()): chamadas.append(os.path.basename(f))
chk('3.2 nenhuma tela chama g2flash direto (a função é chamada só pelo motor)', not chamadas, chamadas)
chk('3.3 aviso visível com aria-live=off; o anúncio sai uma vez pela região viva (aria-live polite)', 'role="status" aria-live="off"' in E.G2_TOAST and "setAttribute('aria-live','polite')" in lib)
chk('3.4 clique em aria-disabled="true" é recusado no g2lib (o comando não roda) e a recusa é anunciada', "closest('[aria-disabled=\"true\"]')" in lib and "'Indisponível: '+m" in lib)
chk('3.5 a recusa realça o motivo visível junto do controle (g2flash no .g2motivo do mesmo .g2ind)', "closest('.g2ind')" in lib and "querySelector('.g2motivo')" in lib)
# revisão DS (achado 6): o selo do bloqueio do encerramento usa o mesmo bloqueio do painel e do comando (osEncBloq), na lista, no Kanban e no painel
po = open(os.path.join(HERE, 'areas', 'processo_os.py'), encoding='utf-8').read()
chk('3.6 selo do bloqueio do encerramento: nome por osEncSelo (osMerge) e dica por osSeloDica ← osEncBloq na lista, no Kanban e no painel', 'function osSeloDica(o,t)' in po and 'const b=osEncBloq(o)' in po.split('function osSeloDica(o,t)', 1)[-1][:200]
    and po.count('osSeloDica(o,') >= 3 and 'dica:osSeloDica(o,s.t)||g2dicaDe(s.t)' in po and "dv:osSeloDica(o,x.t)" in po and po.count('const t=osEncSelo(o.encM)') == 2
    and '_chip_hole("s.t","s.st","s.dot","s.dica")' in po)
# revisão DS (achados 1, 3, 9, 10): pontos centrais do g2lib
chk('3.7 voltar pelo navegador (bfcache) termina a barra de carga; troca de etapa com o foco perdido foca o título do novo contexto', "addEventListener('pageshow'" in lib and 'e.persisted' in lib and "g2carga('fim')" in lib.split("addEventListener('pageshow'", 1)[-1][:120]
    and "hh.focus(" in lib.split('function g2mudou', 1)[-1][:1400])
chk('3.8 title igual ao rótulo visível sai enquanto o ponteiro está em cima (g2ttTira/g2ttVolta); o foco no título anuncia só o estado', 'function g2ttTira' in lib and 'g2ttTira(e.target)' in lib and 'g2ttVolta();' in lib and "g2flash(h,foca?stT:" in lib)

# 4 · glossário e fórmula
cols = [dict(k='q', l='Quantidade'), dict(k='p', l='Preço'), dict(k='tot', l='Total')]
chk('4.1 fórmula da coluna calculada com os rótulos', hasattr(E, '_formula') and E._formula('tot', [dict(k='tot', op='mul', a=['q', 'p'])], cols) == 'Calculado: Quantidade × Preço.')
chk('4.2 termo sem rótulo não vira fórmula (não mostra chave interna)', hasattr(E, '_formula') and E._formula('tot', [dict(k='tot', op='sub', a=['bru', 'tar'])], cols) == '')
chk('4.3 rótulo do campo do formulário completa a fórmula', hasattr(E, '_formula') and E._formula('liq', [dict(k='liq', op='sub', a=['bru', 'tar'])], [dict(k='liq', l='Líquido')], [dict(k='bru', l='Peso bruto'), dict(k='tar', l='Tara')]) == 'Calculado: Peso bruto − Tara.')
a = (E._ajuda_auto if hasattr(E, '_ajuda_auto') else (lambda cols, calc: cols))([dict(k='c', l='Custo R$/ha'), dict(k='l', l='Lâmina aplicada'), dict(k='x', l='Contagem × NC'), dict(k='z', l='Área', ajuda='própria'), dict(k='n', l='Nome')], None)
chk('4.4 glossário: R$/ha, lâmina e NC ganham dica; ajuda própria fica; coluna comum fica sem dica', 'reais por hectare' in a[0].get('ajuda', '') and '10 m³' in a[1].get('ajuda', '') and 'nível de controle' in a[2].get('ajuda', '') and a[3]['ajuda'] == 'própria' and 'ajuda' not in a[4], a)
chk('4.5 sc/ha diz a saca da cultura (DEC-0510-03)', any('60 kg' in t and '50 kg' in t for rx, t in getattr(E, 'GLOSSARIO', []) if rx == 'sc/ha'))
# revisão DS (achado 7): a unidade com período tem dica própria; a genérica de R$/ha não se aplica a ela
a = E._ajuda_auto([dict(k='p', l='Preço R$/ha·mês'), dict(k='e', l='Equivalente R$/ha·ano'), dict(k='c', l='Custo R$/ha'), dict(k='m', l='Mínimo R$/mês')], None)
chk('4.6 R$/ha·mês e R$/ha·ano: dica com o período (a de R$/ha fica para R$/ha sem período); R$/mês sem dica', 'por mês' in a[0].get('ajuda', '') and 'valor ÷ área em ha)' not in a[0].get('ajuda', '')
    and 'por ano' in a[1].get('ajuda', '') and '× 12' in a[1].get('ajuda', '') and 'valor ÷ área em ha)' not in a[1].get('ajuda', '') and a[2].get('ajuda', '').startswith('R$/ha: reais por hectare')
    and 'ajuda' not in a[3], [x.get('ajuda') for x in a])
# revisão DS (achado 8): a sigla ou a unidade que está na célula também dá a dica do cabeçalho (g2glossCol no navegador), com o mesmo texto
GC = getattr(E, '_GLOSS_CEL', None)
chk('4.7 glossário da célula = GLOSSARIO sem as entradas só de rótulo ("^"), e o motor entrega G2_GLOSS ao g2lib', bool(GC) and all(not rx.startswith('^') for rx, t in GC)
    and len(GC) == len([1 for rx, t in E.GLOSSARIO if not rx.startswith('^')]) and any(rx == 'sc/ha' for rx, t in GC) and "const G2_GLOSS = '+gloss" in open(os.path.join(HERE, 'engine.py'), encoding='utf-8').read()
    and 'tt:c.ajuda||g2glossCol(sp,c,rows)' in open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8').read())

# 5 · tokens
du = open(os.path.join(HERE, 'ds_unit.js'), encoding='utf-8').read()
chk('5.1 o teste de contraste mede os tokens do engine (realce, linha, camada do hover)', bool(DSR) and DSR['realce'] in du and DSH.get('fundo', '?') in du and 'sobre(BRANCO, VERDE, 0.07)' in du and DSH.get('camada') == 'rgba(30,122,76,.07)')

# 6 · páginas geradas
pags = sorted(glob.glob(os.path.join(E.P, '*.dc.html')))
if pags:
    sem = [os.path.basename(p) for p in pags if '@keyframes g2realce' not in open(p, encoding='utf-8').read() or '.g2-cab{' not in open(p, encoding='utf-8').read()]
    chk(f'6 as {len(pags)} páginas do project/ carregam o CSS comum (realce, separador, dica)', not sem, sem)
    ind = [f for f in ('BO-02.dc.html', 'CF-05.dc.html') if 'class="g2ind"' not in open(os.path.join(E.P, f), encoding='utf-8').read() or 'class="g2motivo"' not in open(os.path.join(E.P, f), encoding='utf-8').read()]
    chk('6.1 BO-02 (Conciliar pagamentos) e CF-05 (Pedir proposta empresarial): primária indisponível com o motivo visível (acao_motivo)', not ind, ind)
else:
    print('(6 pulado: rode python3 build.py antes)')
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
