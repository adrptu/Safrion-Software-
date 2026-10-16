# -*- coding: utf-8 -*-
"""Alocação de recursos às O.S. na semana 22–27/09/2026 (fonte única para a tela da ordem e a visão Recursos do PCP).
Coerente com dados.ORDENS: OS-0421 dias 3–7 (manhãs), OS-0420 com Trator T1 quebrado em 22/09 (OM-0233) e substituto Trator 02
a partir de 24/09 condicionado à v3, OS-0431 dependente do T1, OS-0424 em 24/09 06:00–11:00, OS-0430 em 25/09 à tarde, irrigação com João.
"""
DIAS = [('2026-09-22', 'seg 22/09'), ('2026-09-23', 'ter 23/09'), ('2026-09-24', 'qua 24/09'), ('2026-09-25', 'qui 25/09'), ('2026-09-26', 'sex 26/09'), ('2026-09-27', 'sáb 27/09')]
JORNADA = 10.0  # h por dia disponível para máquina, implemento e pessoa (1 turno)
JOR_RECURSO = {'PV1': 24.0, 'PV2': 24.0}  # pivô gira fora do turno: a volta a 62 % leva ≈14,5 h

RECURSOS = [  # id, tipo, nome
    ('T1', 'Máquina', 'Trator T1 JD 6M 155'), ('T02', 'Máquina', 'Trator 02 MF 7719'), ('T03', 'Máquina', 'Trator 03'), ('T04', 'Máquina', 'Trator 04'),
    ('COL', 'Máquina', 'Colhedora Axial-Flow 7250'), ('PV1', 'Máquina', 'Pivô 1'), ('PV2', 'Máquina', 'Pivô 2'),
    ('PJ', 'Implemento', 'Pulverizador PJ-3030 36 m'), ('PL', 'Implemento', 'Plantadeira 24 linhas'), ('DI', 'Implemento', 'Distribuidor 3 t'), ('ES', 'Implemento', 'Esqueletadeira'),
    ('MAR', 'Pessoa', 'Marcos · operador'), ('CAR', 'Pessoa', 'Carlos · operador'), ('PAU', 'Pessoa', 'Paula · caldeiro'), ('JOA', 'Pessoa', 'João · irrigante'),
]
# (recurso, O.S. ou evento, dia, início, fim, situação) — situação: firme | condicional (depende de aprovação/liberação) | manutenção
ALOC = []
def _a(recs, os_, dia, ini, fim, sit='firme'):
    for r in recs: ALOC.append(dict(r=r, os=os_, dia=dia, ini=ini, fim=fim, sit=sit))
for dia, fim in [('2026-09-22', 11.0), ('2026-09-23', 11.0), ('2026-09-24', 11.0), ('2026-09-25', 11.0), ('2026-09-26', 12.0)]:
    _a(['T03', 'PJ', 'MAR', 'PAU'], 'OS-0421', dia, 6.0, fim)
_a(['T1', 'PL', 'CAR'], 'OS-0420', '2026-09-22', 6.0, 9.5)                      # 12 ha até a quebra do T1
_a(['T1'], 'OM-0233', '2026-09-22', 9.5, 18.0, 'manutenção')
for dia in ['2026-09-23', '2026-09-24']: _a(['T1'], 'OM-0233', dia, 6.0, 18.0, 'manutenção')
for dia in ['2026-09-24', '2026-09-25', '2026-09-26', '2026-09-27', '2026-09-28']:
    _a(['T02', 'PL', 'CAR'], 'OS-0420', dia, 6.0, 16.0, 'condicional')              # saldo de 70 ha após a v3 (28/09: PCM simplificado S1, alinha com o substituto "até 28/09")
_a(['T1', 'PL', 'CAR'], 'OS-0431', '2026-09-24', 6.0, 16.0, 'condicional')           # plantio T2 pede o T1 bloqueado
_a(['T04', 'PJ', 'MAR', 'PAU'], 'OS-0424', '2026-09-24', 6.0, 11.0)
_a(['T03', 'PJ', 'MAR', 'PAU'], 'OS-0430', '2026-09-25', 13.0, 20.4, 'condicional')  # 160 ha ÷ 21,6 ha/h ≈ 7,4 h
_a(['PV2'], 'OS-0419', '2026-09-23', 20.0, 24.0); _a(['PV2'], 'OS-0419', '2026-09-24', 0.0, 10.52)   # 1 volta a 62 % ≈ 14,5 h
_a(['JOA'], 'OS-0419', '2026-09-23', 20.0, 22.0); _a(['JOA'], 'OS-0419', '2026-09-24', 6.0, 10.52)  # partida à noite; ronda e término de manhã
_a(['JOA'], 'OS-0423', '2026-09-23', 14.0, 16.0)
_a(['PV1'], 'OS-0418', '2026-09-24', 21.0, 24.0, 'condicional'); _a(['PV1'], 'OS-0418', '2026-09-25', 0.0, 11.25, 'condicional')  # 8,1 mm × 95 ha ÷ 150 L/s ≈ 14,3 h
_a(['JOA'], 'OS-0418', '2026-09-24', 21.0, 23.0, 'condicional'); _a(['JOA'], 'OS-0418', '2026-09-25', 6.0, 11.25, 'condicional')

NOME = {r: n for r, t, n in RECURSOS}; TIPO = {r: t for r, t, n in RECURSOS}
# função do recurso (14/10, troca na O.S.): só troca por outro da mesma função (trator por trator, operador por operador)
CLASSE = {r: (n.split('·')[-1].strip() if t == 'Pessoa' else n.split(' ')[0]) for r, t, n in RECURSOS}
# ativo da Manutenção de cada recurso (fonte da condição Bloqueado/Disponível); dados_manutencao lê daqui
REC_DO_ATIVO = {'a01': 'T1', 'a02': 'T02', 'a03': 'T03', 'a04': 'T04', 'a08': 'COL', 'a15': 'PV1', 'a11': 'PV2', 'a05': 'PJ', 'a06': 'PL', 'a07': 'DI', 'a10': 'ES'}

JS = r"""
// ===== alocação de recursos às O.S. (alocacao.py): a semana do PCP (AL0) + as trocas gravadas no cenário (c.ordens[os].rec = {original: substituto}) =====
// Fonte única de quem e o que está em cada O.S.: painel da O.S., Carga do PCP, conflito com a Manutenção e app de campo. Não muda c.
// alocação vigente: a semana do PCP com as trocas de recurso da O.S. (rec). Ordem cancelada ou que saiu do estado (existia no cenário inicial)
// deixa de ocupar o recurso (revisão Codex 6167883199: o compromisso futuro é liberado); eventos que nunca foram O.S. do cenário (irrigação,
// OS-0419/0423) e a manutenção válida continuam. O realizado não vem daqui: fica nos apontamentos da ordem.
function alVigente(c){ const O=(c&&c.ordens)||{}, S0=(typeof CEN0!=='undefined'&&CEN0&&CEN0.ordens)||{};
  return AL0.aloc.filter(a=>!(O[a.os]?O[a.os].etapa==='Canceladas':!!S0[a.os])).map(a=>{ const t=O[a.os]&&O[a.os].rec&&O[a.os].rec[a.r]; return t?Object.assign({},a,{r:t,de:a.r}):a; }); }
function alHh(x){ const h=Math.floor(x), m=Math.round((x-h)*60); return String(h).padStart(2,'0')+':'+String(m).padStart(2,'0'); }
function alDm(iso){ return String(iso).slice(8,10)+'/'+String(iso).slice(5,7); }
function alAtivo(c,r){ const aid=AL0.ativo[r]; return (aid&&c&&c.man&&c.man.ativos&&c.man.ativos[aid])||null; }
function alBloqueado(c,r){ const a=alAtivo(c,r); return !!a&&a.cond==='Bloqueado'; }
// bloco de manutenção da semana vale enquanto o ativo segue bloqueado (apto na Manutenção = livre); sem ativo ligado, vale sempre
function alManVale(c,r){ const a=alAtivo(c,r); return !a||a.cond==='Bloqueado'; }
// choques do recurso r com os blocos (dia, início, fim) da ordem os: outra O.S. no mesmo horário ou manutenção vigente
function alChoques(c,r,os,blocos,A){ A=A||alVigente(c); const out=[];
  blocos.forEach(b=>A.forEach(x=>{ if(x.r===r&&x.dia===b.dia&&x.os!==os&&x.ini<b.fim&&b.ini<x.fim&&(x.sit!=='manutenção'||alManVale(c,r)))
    out.push({dia:b.dia,ini:Math.max(x.ini,b.ini),fim:Math.min(x.fim,b.fim),com:x.os,manut:x.sit==='manutenção'}); })); return out; }
function alChoqueTxt(x){ return (x.manut?'Em manutenção':'Conflito com '+x.com)+' em '+alDm(x.dia)+' '+alHh(x.ini)+'–'+alHh(x.fim); }
// recursos de uma O.S. (painel): janelas, condicional e alertas; de = recurso original quando trocado
function alDaOrdem(c,os){ const A=alVigente(c), its=A.filter(a=>a.os===os);
  return [...new Set(its.map(a=>a.r))].map(r=>{ const ja=its.filter(a=>a.r===r);
    return {r,de:ja[0].de||null,tipo:AL0.tipo[r],nome:AL0.nome[r],classe:AL0.classe[r],janelas:ja.map(a=>alDm(a.dia)+' '+alHh(a.ini)+'–'+alHh(a.fim)).join(' · '),
      cond:ja.some(a=>a.sit==='condicional'),alertas:alChoques(c,r,os,ja,A).map(alChoqueTxt)}; }); }
// substitutos de r na O.S.: mesma função, fora da ordem; ok=false com o motivo (bloqueado, em manutenção ou ocupado) e aviso de jornada
function alCandidatos(c,os,r){ const A=alVigente(c), ja=A.filter(a=>a.os===os&&a.r===r), usados=new Set(A.filter(a=>a.os===os).map(a=>a.r));
  return Object.keys(AL0.nome).filter(x=>x!==r&&AL0.tipo[x]===AL0.tipo[r]&&AL0.classe[x]===AL0.classe[r]&&!usados.has(x)).map(x=>{
    const ch=alChoques(c,x,os,ja,A), bl=alBloqueado(c,x);
    const mot=bl?'bloqueado na Manutenção':(ch.length?((ch[0].manut?'em manutenção':'ocupado na '+ch[0].com)+' em '+alDm(ch[0].dia)+' '+alHh(ch[0].ini)+'–'+alHh(ch[0].fim)):'');
    const jor=(AL0.jorRec||{})[x]||AL0.jor; const acima=[...new Set(ja.map(b=>b.dia))].filter(d=>A.filter(y=>y.r===x&&y.dia===d&&y.sit!=='manutenção').reduce((s,y)=>s+y.fim-y.ini,0)+ja.filter(b=>b.dia===d).reduce((s,b)=>s+b.fim-b.ini,0)>jor+1e-9);
    return {r:x,nome:AL0.nome[x],ok:!mot,motivo:mot,aviso:acima.length?'acima da jornada em '+acima.map(alDm).join(', '):''}; }); }
// CMD · trocar recurso da O.S. (PCP ou quem libera, AL-01): só antes da execução; mesma função; recusa choque e ativo bloqueado
// (dano evitado: a mesma máquina ou pessoa em duas ordens ao mesmo tempo, ou máquina parada mandada a campo). Origem ganha a linha.
function alTrocar(c,os,de,para,pf){ const co=c&&c.ordens&&c.ordens[os]; if(!co) throw new Error('Ordem '+os+' não encontrada.');
  if(['A liberar','Liberadas'].indexOf(co.etapa)<0) throw new Error('Trocar recurso só antes da execução (A liberar ou Liberadas); a '+os+' está '+co.etapa+'. Nada foi alterado.');
  const quem=pf!==undefined?cenExigeUm(pf,['pcp'].concat(g2alc('AL-01').papeis),'Trocar recurso da '+os):'PCP';
  const atual=alDaOrdem(c,os).find(x=>x.r===de); if(!atual) throw new Error((AL0.nome[de]||de)+' não está na '+os+'. Nada foi alterado.');
  const cand=alCandidatos(c,os,de).find(x=>x.r===para); if(!cand) throw new Error((AL0.nome[para]||para)+' não substitui '+AL0.nome[de]+' (outra função ou já está na ordem). Nada foi alterado.');
  if(!cand.ok) throw new Error('Troca recusada: '+cand.nome+' '+cand.motivo+'. Nada foi alterado.');
  const orig=atual.de||de, hr=cenAgora(); co.rec=Object.assign({},co.rec||{}); if(para===orig) delete co.rec[orig]; else co.rec[orig]=para;
  co.recHist=(co.recHist||[]).concat([{de,para,por:quem,at:hr,t:'Recurso trocado: '+AL0.nome[de]+' → '+cand.nome+' por '+quem+' às '+hr}]);
  return {msg:AL0.nome[de]+' → '+cand.nome+' na '+os+(cand.aviso?' · '+cand.aviso:'')+'.'}; }
"""


def js():
    """AL0 (semana do PCP, recursos, função e ativo de cada um) + as regras da alocação vigente: entra no prefixo do cenário (toda tela do estado)."""
    import json
    al0 = dict(jor=JORNADA, jorRec=JOR_RECURSO, dias=DIAS, nome=NOME, tipo=TIPO, classe=CLASSE, ativo={r: a for a, r in REC_DO_ATIVO.items()},
               aloc=[dict(r=a['r'], os=a['os'], dia=a['dia'], h=round(a['fim'] - a['ini'], 2), ini=a['ini'], fim=a['fim'], sit=a['sit']) for a in ALOC])
    return 'const AL0 = ' + json.dumps(al0, ensure_ascii=False) + ';\n' + JS



def hh(x):
    h = int(x); m = int(round((x - h) * 60))
    return f'{h:02d}:{m:02d}'


def conflitos():
    """Sobreposição de horário do mesmo recurso em ordens diferentes (manutenção conta como indisponível)."""
    out = []
    for i, a in enumerate(ALOC):
        for b in ALOC[i + 1:]:
            if a['r'] == b['r'] and a['dia'] == b['dia'] and a['os'] != b['os'] and a['ini'] < b['fim'] and b['ini'] < a['fim']:
                out.append(dict(r=a['r'], dia=a['dia'], a=a['os'], b=b['os'], ini=max(a['ini'], b['ini']), fim=min(a['fim'], b['fim']),
                                manut=('manutenção' in (a['sit'], b['sit']))))
    return out


def semana():
    """Por recurso: horas por dia, uso da semana, conflitos, excesso de jornada e ociosidade."""
    conf = conflitos(); res = []
    for r, t, n in RECURSOS:
        dias = []; tot = 0.0
        for d, lab in DIAS:
            its = [a for a in ALOC if a['r'] == r and a['dia'] == d]
            h = sum(a['fim'] - a['ini'] for a in its if a['sit'] != 'manutenção'); tot += h
            dias.append(dict(d=d, itens=its, h=h, manut=any(a['sit'] == 'manutenção' for a in its),
                             conf=[c for c in conf if c['r'] == r and c['dia'] == d], acima=h > JOR_RECURSO.get(r, JORNADA) + 1e-9))
        disp = JOR_RECURSO.get(r, JORNADA) * len(DIAS) - sum(a['fim'] - a['ini'] for a in ALOC if a['r'] == r and a['sit'] == 'manutenção')
        res.append(dict(r=r, tipo=t, nome=n, dias=dias, h=tot, disp=disp, uso=(tot / disp if disp else 0)))
    return res, conf


def da_ordem(os_):
    """Recursos alocados a uma O.S., com janelas e alertas (conflito, manutenção, condicional)."""
    conf = conflitos(); its = [a for a in ALOC if a['os'] == os_]
    out = []
    for r in dict.fromkeys(a['r'] for a in its):
        ja = [a for a in its if a['r'] == r]
        cs = [c for c in conf if c['r'] == r and os_ in (c['a'], c['b'])]
        out.append(dict(r=r, tipo=TIPO[r], nome=NOME[r],
                        janelas=' · '.join(f"{a['dia'][8:10]}/{a['dia'][5:7]} {hh(a['ini'])}–{hh(a['fim'])}" for a in ja),
                        cond=any(a['sit'] == 'condicional' for a in ja),
                        alertas=[(f"{'Em manutenção' if c['manut'] else 'Conflito com ' + (c['b'] if c['a'] == os_ else c['a'])} em {c['dia'][8:10]}/{c['dia'][5:7]} {hh(c['ini'])}–{hh(c['fim'])}") for c in cs]))
    return out


if __name__ == '__main__':
    res, conf = semana()
    for x in res: print(f"{x['nome']:32s} {x['h']:5.1f} h / {x['disp']:4.1f} h = {x['uso']*100:5.1f} %", '·', sum(len(d['conf']) for d in x['dias']), 'conflitos')
    for c in conf: print(c)
    print(da_ordem('OS-0424'))
