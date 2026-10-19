# -*- coding: utf-8 -*-
"""MB-02det · detalhe da ordem (Chrome real, ≤ 15 verificações): insumos com unidade em todos os números e rótulo coerente para o item
fora da requisição; listas com teto (cabe com muitos turnos e ocorrências longas); ordem feita e sem sobra aguarda o encerramento.
Uso: python3 app_mb02det_test.py   (compile antes: areas.mobile.build())"""
from app_lib import App

CORTE = """(()=>{const m=document.querySelector('main'); const mr=m.getBoundingClientRect(); const pb=parseFloat(getComputedStyle(m).paddingBottom)||0; let b=0;
 m.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect(); if(r.height>0&&r.width>0&&r.bottom>b) b=r.bottom;}); return Math.round(b-(mr.bottom-pb));})()"""
OC = "return cenOcorrencia(c,'OS-0421','Clima','Vento acima de 10 km/h às 10:30 na bordadura leste; parei a barra 20 min e retomei quando o vento baixou para 6 km/h.');"
a = App(['MB-01', 'MB-02det'])
try:
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
    a.J("localStorage.setItem('talhao-os-mb-os','OS-0421')"); a.abrir('MB-02det'); b = a.body()
    a.ok('entregue 160 L · consumido 95 L' in b, 'Fungicida A: "entregue 160 L · consumido 95 L" (unidade em todos os números)')
    a.ok('fora da REQ-035 · nada com você' in b and 'Peça ao escritório antes de usar' in b and 'sem requisição' not in b,
         'Adjuvante: "fora da REQ-035" coerente com o título Insumos · REQ-035 (sem "sem requisição")')
    for _ in range(3):
        a.mudar("cenIniciarTurno(c,'OS-0421'); return cenFecharTurno(c,20,3,{'Fungicida A':10,'Adjuvante espalhante':0},'');")
    for _ in range(4): a.mudar(OC)
    a.abrir('MB-02det'); b = a.body(); k = a.J(CORTE)
    a.ok('3 turnos anteriores' in b and 'Dia 7' in b and 'Dia 3 ·' not in b, 'apontamentos: os 4 últimos e "3 turnos anteriores"')
    a.ok('+ 2 anteriores' in b and b.count('OC-50') == 2, 'ocorrências: as 2 mais recentes e "+ 2 anteriores"')
    a.ok(k <= 0, f'7 turnos e 4 ocorrências longas cabem na altura (excesso {k} px)')
    # OS-0424 feita (128 ha no T1-B desde o G1 do CTL-1) e sobra devolvida: próximo passo é o encerramento no escritório
    a.mudar("cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos','Rui'); cenConfirmarRecebimento(c,'REQ-039'); cenIniciarTurno(c,'OS-0424'); return cenFecharTurno(c,128,6,null,'');")
    a.mudar("const it=c.reqs['REQ-039'].itens[0]; it.devolvido+=it.custodia; it.custodia=0; return {msg:'devolvido'};")
    a.J("localStorage.setItem('talhao-os-mb-os','OS-0424')"); a.abrir('MB-02det'); b = a.body()
    a.ok('Aguardar encerramento' in b and 'encerramento no escritório' in b and 'Área feita · aguarda encerramento' in b and a.foot() == 'Voltar às ordens',
         'OS-0424 feita e sem sobra: "Aguardar encerramento" e rodapé Voltar às ordens (' + a.foot() + ')')
    a.ok('Iniciar turno' not in b, 'OS-0424 sem saldo não oferece Iniciar turno')
    a.ok(not a.erros(), 'sem erros JS ' + str(a.erros()))
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
finally:
    a.fim()
