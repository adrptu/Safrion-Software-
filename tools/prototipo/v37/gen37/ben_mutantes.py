# -*- coding: utf-8 -*-
"""Beneficiamento BEN-1 · mutantes (ESPECIFICACAO.md §11.4): cada mutante, sozinho, tem de derrubar ao menos uma verificação de ben_unit.js.
Aplica a troca no texto do motor (o mesmo de ben_unit_test.py) e roda os testes no node, sem navegador.
Uso: SAFRION_DADOS=sintetico python3 ben_mutantes.py   → uma linha por mutante e 'RESULTADO: OK n/n' (todos mortos)."""
import os, sys, json
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from ben_unit_test import motor, node
M = [
 ('M01 elegibilidade da entrada desligada (R-A03)', "  const Q = benBase(c, L);\n  if (Q.q === 'Em inspeção')", "  const Q = { q: 'Liberado' };\n  if (Q.q === 'Em inspeção')"),
 ('M02 R-A07 sem a tolerância', "if (prCmp(tot, prSoma([proc, tol])) > 0)", "if (prCmp(tot, proc) > 0)"),
 ('M03 Fechar sem cenPodeEncerrar (custódia)', "const pe = cenPodeEncerrar(c, id); if (pe) throw new Error(pe);", ""),
 ('M04 Fechar sem as etapas exigidas', "if (et.length) throw new Error('Etapa exigida pendente", "if (false) throw new Error('Etapa exigida pendente"),
 ('M05 R-C02 caixas acima da custódia desligada', "if (cx > cust + 1e-9) throw new Error('Caixas acima da custódia", "if (false) throw new Error('Caixas acima da custódia"),
 ('M07 R-E05 sem comparar classe', "if (ped.classe !== L.classe) return 'Classe '", "if (false) return 'Classe '"),
 ('M08 R-E02 Liberar com Não conforme', "return res.sit === 'Conforme' ? ['Liberar', 'Manter bloqueio', 'Destinar']", "return true ? ['Liberar', 'Liberar como classe atingida', 'Manter bloqueio', 'Destinar']"),
 ('M08b R-E02 recusa do Liberar não conforme desligada', "if (dec === 'Liberar' && res && res.sit !== 'Conforme') throw", "if (false) throw"),
 ('M09 R-F02 sem o valor absoluto', "const sai = prSoma([prod, outro, desc, perda]); const dif = prSub(proc, sai); const faixa = benFaixa(proc, r); const ad = benAbs(dif);", "const sai = prSoma([prod, outro, desc, perda]); const dif = prSub(proc, sai); const faixa = benFaixa(proc, r); const ad = dif;"),
 ('M10 R-G06 sem o teto', "const porPct = prCmp(lp, r.par.alcada_kg) <= 0;", "const porPct = true;"),
 ('M11 R-G06 desligada', "const pct = prCmp(proc, 0) > 0 ? prDiv(prMul(ad, 100), proc) : 0; const passa = prCmp(ad, lim) > 0;", "const pct = prCmp(proc, 0) > 0 ? prDiv(prMul(ad, 100), proc) : 0; const passa = false;"),
 ('M12 R-F07 sem a alçada de dif0', "if (!b0.dentro && b1.dentro && al.passa &&", "if (false &&"),
 ('M13 perda identificada sem exigir evidência', "if (!String(k.ticket || '').trim()) throw new Error('Sem pesagem", "if (false) throw new Error('Sem pesagem"),
 ('M14 estorno que não devolve caixas', "it.consumido -= s.cx; it.custodia += s.cx;", ""),
 ('M15 estorno que não derruba a conferência', "if (o.ben.conf) { o.ben.conf = null; ca.push('conferência'); }", ""),
 ('M16 balanço somando o registro estornado', "function benValidos(o) { return (o.ben.sai || []).filter(s => !s.estorno); }", "function benValidos(o) { return (o.ben.sai || []); }"),
 ('M17 ID de lote olhando só os lotes', "Object.keys(P.lotes).forEach(ve); Object.values(c.ordens || {}).forEach(o => ((o.ben && o.ben.sai) || []).forEach(s => ve(s.lote)));", "Object.keys(P.lotes).forEach(ve);"),
 ('M18 chave (recibo) desligada', "function benRecibo(c, k, nome, imp) { if (!k || !k.chave) return null;", "function benRecibo(c, k, nome, imp) { return null;"),
 ('M19 versão esperada desligada', "function benVer(o, k) { if (k &&", "function benVer(o, k) { if (false &&"),
 ('M20 liberar sem o evento CMD-42', "benHist(o, quem, 'Versão ' + o.versao + ' da ordem autorizada (CMD-42)',", "(()=>0)(o, quem, 'Versão ' + o.versao + ' da ordem autorizada (CMD-42)',"),
 ('M21 número da REQ pela contagem', "const rid = cenProxId(c, 'reqs', 'REQ', 41);", "const rid = 'REQ-' + (41 + Object.keys(c.reqs).length);"),
 ('M23 R-E05 sem o limite do disponível', "if (prCmp(kg, S.disp) > 0) throw new Error('Acima do disponível", "if (false) throw new Error('Acima do disponível"),
 ('M24 fechar libera o lote (R-E01)', "q0: 'Em inspeção', cond: '', origem: ents.map", "q0: 'Liberado', cond: '', origem: ents.map"),
 ('M25 carência não herdada pela genealogia', "if (x.lote) out.push.apply(out, prOrigCampo(c, P.lotes[x.lote], vis)); else if (x.os) out.push(x);", "if (x.os) out.push(x);"),
 ('M26 liberar lote sem perfil (prLiberarLote)', "const quem = cenExigeUm(ator, ['qualidade', 'agronomo'], 'Liberar o lote ' + lid);", "const quem = 'Qualidade (Marta)';"),
]
U = open(os.path.join(HERE, 'ben_unit.js'), encoding='utf-8').read()
base = motor(); OK = []
for nome, de, para in M:
    n = base.count(de)
    if n != 1: OK.append(False); print(f'FALHA {nome}: trecho achado {n} vezes (o mutante não se aplica)'); continue
    r = node(base.replace(de, para) + U, 'ben_mutante.js'); out = r.stdout.strip().splitlines()
    try: res = json.loads(out[-1])
    except Exception: res = None
    mortos = [x['n'].split(' ')[0] for x in (res or []) if not x['ok']]
    morto = r.returncode != 0 or res is None or bool(mortos)
    OK.append(morto); print(('OK    ' if morto else 'FALHA ') + nome + ' → ' + (', '.join(mortos[:6]) if mortos else ('erro de execução' if morto else 'SOBREVIVEU')))
print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
