# -*- coding: utf-8 -*-
"""Contraprovas do revisor (Claude) sobre o portão aceite.avaliar() real (PR #112 @7c2045d6). Sem navegador.
P0: o portão sobre os recibos dirigidos da rodada 1 (base, revisor/saidas).
P1: inventário mínimo todo aprovado + 1 caso crítico extra inconclusivo → deve bloquear.
P2: falta o caso da OS-0424, mas o título do detalhe da OS-0425 cita a OS-0424 → deveria bloquear.
P3: recibo de outra execução (sem vínculo com o render medido) → o portão aceita? (limite)
P4: inventário todo aprovado e taxa 0,95, mas IDs clicáveis, volta e Voltar a 0 % → o portão não lê as outras três metas.
Uso: python3 -I portao_contraprovas.py --robo51 <pasta robo-v51> --base <pasta saidas da rodada 1>"""
import argparse, importlib.util, json, os, shutil, tempfile
ap = argparse.ArgumentParser(); ap.add_argument('--robo51', required=True); ap.add_argument('--base', required=True)
a = ap.parse_args()
spec = importlib.util.spec_from_file_location('aceite51', os.path.join(a.robo51, 'aceite.py')); G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
out = {}
def em(casos, endereco=None, taxa=1.0, erros=()):
    with tempfile.TemporaryDirectory() as d:
        json.dump({'casos': casos, 'origens': []}, open(os.path.join(d, 'casos-criticos.json'), 'w'))
        json.dump({'casos': endereco or [], 'origens': []}, open(os.path.join(d, 'casos-criticos-endereco.json'), 'w'))
        return G.avaliar(d, taxa, list(erros))
with tempfile.TemporaryDirectory() as d:
    for f in ('casos-criticos.json', 'casos-criticos-endereco.json'):
        shutil.copy(os.path.join(a.base, f), d)
    out['P0_base_rodada1'] = G.avaliar(d, 34 / 68, [])
OK = {'r': 'navega', 'alvo': 'OS-0502', 'abriu': True}
REQ = [('OS→EST','entregar','OS-0424'),('OS→EST','entregar','OS-0425'),('OS→EST','devolver','OS-0417'),('OS→EST','saldo','OS-0418'),
       ('OS→receituário','','OS-0504'),('OS→receituário','','OS-0508'),('receituário→OS','','VIS-051'),('receituário→OS','','VIS-052'),
       ('Aprovações→OS','',''),('OM→OS','','OM-0233'),('OS→OM','','OS-0420'),('OS→OM','','OS-0431'),('OS→OM','','OS-0507')]
RA = [{'percurso': 'OS→receituário', 'sub': 'AG-01', 'detalhe': 'OS-0504', 'res': dict(OK, alvo='RA-0140')},
      {'percurso': 'receituário→OS', 'sub': 'AG-01', 'detalhe': 'RA-0140 · receituário', 'res': OK}]
todos = [{'percurso': g, 'sub': s, 'detalhe': i + ' · detalhe', 'res': OK} for g, s, i in REQ] + RA
out['P1_controle_tudo_aprovado'] = em(todos)['estado']
out['P1_extra_inconclusivo'] = em(todos + [{'percurso': 'OS→EST', 'sub': 'outro', 'detalhe': 'OS-0430', 'res': {'r': 'navega', 'alvo': '', 'inconclusivo': True}}])['estado']
sem0424 = [c for c in todos if not c['detalhe'].startswith('OS-0424')]
sem0424 = [dict(c, detalhe='OS-0425 · desdobrada da OS-0424') if c['detalhe'].startswith('OS-0425') else c for c in sem0424]
out['P2_sem_OS0424_titulo_0425_cita_0424'] = em(sem0424)['estado']
out['P3_recibo_sem_vinculo_ao_render'] = 'o recibo não traz hash do render nem identificador da execução; avaliar() aceita qualquer JSON com o formato (P1 controle usa recibo fabricado e dá ' + out['P1_controle_tudo_aprovado'] + ')'
out['P4_so_chegada'] = em(todos, taxa=0.95)['estado'] + ' com taxa de chegada 0,95; a assinatura avaliar(diretorio, taxa, erros) não recebe IDs clicáveis, volta à origem nem Voltar'
print(json.dumps(out, ensure_ascii=False, indent=1))
