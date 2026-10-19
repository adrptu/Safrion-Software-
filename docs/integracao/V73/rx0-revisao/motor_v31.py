# -*- coding: utf-8 -*-
"""RX-0 · variante de motor v3.1 (C2, autoria Claude; contrato 6253554386). Só para o ensaio C3 do Codex; não muda o produto.
Aplica 3 trocas literais na fonte do Raio-X v3 (raiox-pragas-no-tempo-v3.html, sha256 e7872cb0…) e grava a v3.1:
  1. rxFit: conta também as semanas do grupo baixo (q.wkLo).
  2. rxLevels: Clima só é forte com >= 5 semanas no grupo alto E no baixo; representante com mates (grupo correlacionado) vira 'grupo'
     (causa não separável), nunca 'forte' de uma variável só; Clima forte numa safra fica 'moderada' com q.candidatoSafra = true.
  3. rxCombinaSafras(a, b): combinação entre safras do mesmo alvo e fator. Clima só é 'forte' se as duas safras têm candidatoSafra com o
     mesmo sinal de beta; 'grupo' em qualquer safra fica 'grupo'; senão vale o menor nível das duas (ordem: insuf < nulo < fraca < moderada).
Uso: python3 -I motor_v31.py <fonte-v3.html> <saida-v31.html>   → imprime o sha256 da saída."""
import hashlib, sys
SHA_V3 = 'e7872cb02fc667330354560a6b88b82cd5485ab656b2d7546b2500d645805e5e'
TROCAS = [
    ("q.wkHi = new Set(hi.map(r => r.wk)).size; });",
     "q.wkHi = new Set(hi.map(r => r.wk)).size; q.wkLo = new Set(R.rows.filter((r, i) => !I[i]).map(r => r.wk)).size; });"),
    ("let lv = !enough ? 'insuf' : ex && q.q < .1 ? (q.stable && (q.f.tipo !== 'Clima' || q.wkHi >= 3) ? 'forte' : 'moderada') : ex80 ? 'fraca' : 'nulo';",
     "let lv = !enough ? 'insuf' : ex && q.q < .1 ? (q.stable && (q.f.tipo !== 'Clima' || (q.wkHi >= 5 && q.wkLo >= 5)) ? 'forte' : 'moderada') : ex80 ? 'fraca' : 'nulo';\n"
     "    if (lv === 'forte' && q.mates && q.mates.length) lv = 'grupo';   // v3.1: representante de grupo correlacionado; causa não separável\n"
     "    if (lv === 'forte' && q.f.tipo === 'Clima') { q.candidatoSafra = true; lv = 'moderada'; }   // v3.1: clima numa safra só, no máximo moderada"),
    ("// camada 3: eficácia de Henderson-Tilton",
     "// v3.1: combinação entre safras (mesmo alvo e fator). Clima forte só com candidatoSafra nas duas e o mesmo sinal de beta.\n"
     "const RX31_ORD = ['insuf', 'nulo', 'confirmar', 'fraca', 'moderada'];\n"
     "function rxCombinaSafras(a, b) { if (!a || !b) return { level: 'nao_avaliavel', motivo: 'uma safra sem resultado' };\n"
     "  if (a.level === 'grupo' || b.level === 'grupo') return { level: 'grupo', motivo: 'grupo correlacionado em pelo menos uma safra' };\n"
     "  if (a.candidatoSafra && b.candidatoSafra && Math.sign(a.beta) === Math.sign(b.beta) && Math.sign(a.beta) !== 0) return { level: 'forte', motivo: 'clima com o mesmo sinal nas duas safras' };\n"
     "  if (a.level === 'forte' && b.level === 'forte' && Math.sign(a.beta) === Math.sign(b.beta)) return { level: 'forte', motivo: 'forte nas duas safras' };\n"
     "  const ia = RX31_ORD.indexOf(a.level === 'forte' ? 'moderada' : a.level), ib = RX31_ORD.indexOf(b.level === 'forte' ? 'moderada' : b.level);\n"
     "  return { level: RX31_ORD[Math.max(0, Math.min(ia, ib))], motivo: 'menor nível das duas safras' }; }\n"
     "// camada 3: eficácia de Henderson-Tilton"),
]
src = open(sys.argv[1], encoding='utf-8').read()
assert hashlib.sha256(src.encode('utf-8')).hexdigest() == SHA_V3, 'fonte não é a v3 e7872cb0'
for a, b in TROCAS:
    assert src.count(a) == 1, 'trecho ausente ou repetido: ' + a[:60]
    src = src.replace(a, b)
open(sys.argv[2], 'w', encoding='utf-8').write(src)
print(hashlib.sha256(src.encode('utf-8')).hexdigest())
