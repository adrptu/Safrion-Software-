# -*- coding: utf-8 -*-
"""Comercial e logística · sonda da base f4121bd para a revisão por contraexemplo (ESPECIFICACAO.md v1.1; CE-nn em DECISOES.md).
Descreve o comportamento do código ANTES da implementação (não é teste de aceite; depois do P1 alguns valores mudam de propósito).
Uso: SAFRION_DADOS=sintetico python3 docs/comercial/verificacao/sonda_base.py   → uma linha por observação.
Dados sintéticos (a Lagoa Grande é sintética)."""
import os, sys, subprocess, tempfile
sys.dont_write_bytecode = True   # não deixa __pycache__ no gerador
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
G = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tools', 'prototipo', 'v37', 'gen37'))
sys.path.insert(0, G); os.chdir(G)
import cenario
from areas.processo_os import JS_NUCLEO
from areas import producao as AP

COM = r'''
function MUD(c, fn) { const x = cenClone(c); try { const r = fn(x) || {}; Object.keys(c).forEach(k => delete c[k]); Object.assign(c, x); return r; } catch (e) { return { erro: String(e.message || e) }; } }
'''
SEM = COM + r'''
const c = cenClone(CEN0);
for (const id of ['L38-132', 'L39-131', 'L39-132']) { const S = prSaldos(c, c.producao.lotes[id]); print('CE-01 sem o núcleo da carência:', id, S.q, '· apto', S.apto, 'kg'); }
print('CE-01 sem o núcleo: typeof carAvaliar =', typeof carAvaliar, '(prReservar pula a avaliação do destino)');
'''
COMN = COM + r'''
let c = cenClone(CEN0);
for (const id of ['L38-132', 'L39-131', 'L39-132']) { const S = prSaldos(c, c.producao.lotes[id]); print('CE-01 com o núcleo:', id, S.q, '· apto', S.apto, 'kg'); }
const w39 = prOfertaSem(c, 'Mamão Formosa · fruta de campo', '2026-W39');
print('CE-05 S39 em curso na Previsão e colheita: publicada', w39.pub, 'kg · oferta livre', w39.livre, 'kg · semana começou:', prSemComecou('2026-W39'));
MUD(c, x => prReceber(x, { carga: 'CG-2108', ticket: 'TK-4520', bruto: 19250, tara: 7200, cond: 'Íntegra' }));
MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 10000 }));
let r = MUD(c, x => prReservar(x, { pedido: 'PV-036', lote: 'L39-133', kg: 40 })); print('CE-03 reservar 40 kg de excesso para o PV-036:', r.erro || 'aceito');
const L = c.producao.lotes['L39-133'];
r = MUD(c, x => prReservar(x, { pedido: 'PV-038', lote: 'L39-133', kg: 2050 })); print('CE-08 PV-038 (S41 começa ' + prSemIni('2026-W41') + ') reserva o L39-133 que vence ' + L.validade + ':', r.erro || 'aceito');
const c2 = cenClone(CEN0); c2.producao.movs.push({ id: 'MP-X', tipo: 'expedição', lote: 'L38-131', kg: -30040, pedido: 'PV-038', d: '2026-10-06' });
const o = prOfertaSem(c2, 'Mamão Formosa · fruta de campo', '2026-W41'); print('CE-03 PV-038 expedido 30.040 kg de 30.000: vendas futuras', o.futKg, 'kg · oferta livre', o.livre, 'kg');
c.producao.pedidos['CT-T'] = { id: 'CT-T', cliente: 'CD Horti', prod: 'Mamão Formosa · fruta de campo', cultura: 'Mamão Formosa', classe: '', saf: '', tipo: 'futura', janela: 'S39', sem: '2026-W39', qtd: 20000, dest: 'MI-BR' };
const w = prOfertaSem(c, 'Mamão Formosa · fruta de campo', '2026-W39'); print('CE-02 futura de 20.000 kg na S39 em curso: prOfertaSem a conta (vendas futuras', w.futKg, 'kg); a R-C13 v1.0 tira a S39 do Painel e o estoque só soma prontas');
print('CE-06 prCompat(venda classe A, lote sem classe):', prCompat({ prod: L.prod, classe: 'A', saf: '' }, L));
print('CE-06 produto do lote de mamão no estado:', L.prod);
print('CE-14 perfis no cadastro:', G2_PERFIS.length);
'''

def rodar(js, nucleo):
    src = ('globalThis.print=(...a)=>console.log(...a);\n' + cenario.perfis_js() + cenario.js_prefixo() + (JS_NUCLEO if nucleo else '')
           + AP.PR_UI_JS + AP.PR_PED_JS + js)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(src); p = f.name
    r = subprocess.run(['node', p], capture_output=True, text=True, timeout=120); os.unlink(p)
    print(r.stdout.strip()); print(r.stderr.strip()[-800:]) if r.returncode else None


rodar(SEM, False)
rodar(COMN, True)
from areas import cad_parceiros as CP
import dados_cad as DC
print('CE-06 produtos do CD-05 (PRODUTOS_VENDA):', DC.PRODUTOS_VENDA)
print('CE-06 produto de estoque por cultura (CULTURA_UN.prod):', sorted({u['prod'] for u in DC.CULTURA_UN.values()}))
print('CE-09 cultivos de mamão por fazenda:', sorted({(k['faz']) for k in __import__('dados_producao').catalogo()['cult'].values() if k['cultura'] == 'Mamão Formosa'}))
