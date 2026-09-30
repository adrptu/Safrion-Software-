# -*- coding: utf-8 -*-
"""Verificador CD-05 · suspensão e estado do cabeçalho calculado."""
import importlib.util, os, time
s=importlib.util.spec_from_file_location('vl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_lib.py')); L=importlib.util.module_from_spec(s); s.loader.exec_module(L)
t=L.T(); SH=os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_')
FOOT="(()=>{const a=document.querySelector('aside[role=dialog]'); return [...a.querySelectorAll('button')].map(b=>b.innerText.trim()).filter(x=>x&&x!=='×');})()"
CHIPC="(()=>{const h=document.querySelector('h1'); const c=h.nextElementSibling; return c?getComputedStyle(c).color+' '+getComputedStyle(c).backgroundColor:'';})()"
try:
    t.load(); c0=t.chip(); cc0=t.J(CHIPC)
    t.novo(); f=t.J(FOOT); t.btn('Cancelar')
    t.chk('1 cadastro novo não tem Suspender parceiro', 'Suspender parceiro' not in f, f)
    t.abre('Sementes Vale'); f=t.J(FOOT); lb=t.labs()
    t.chk('2 existente: Suspender parceiro no rodapé, sem campo de motivo', 'Suspender parceiro' in f and 'Motivo da suspensão' not in lb, f)
    t.btn('Suspender parceiro'); f=t.J(FOOT); lb=t.labs(); t.c.shot(SH+'susp.png')
    t.chk('3 Suspender mostra Motivo e troca o botão por Manter ativo', 'Motivo da suspensão' in lb and 'Manter ativo' in f and 'Suspender parceiro' not in f, (f,lb[-2:]))
    t.btn('Manter ativo'); lb=t.labs(); t.btn('Cancelar')
    t.chk('4 Manter ativo desfaz e cancelar fecha sem confirmação', 'Motivo da suspensão' not in lb and not t.aberto(), lb[-2:])
    # limite vencido renovado → some do cabeçalho
    t.abre('Rede Hortifrúti BA'); t.setk('limv','2027-01-31'); t.btn('Salvar'); time.sleep(.2); c1=t.chip()
    t.chk('5 renovar validade tira "limite vencido" do cabeçalho', '1 limite vencido' in c0 and 'limite vencido' not in c1 and '2 grupos sem fornecedor' in c1, (c0,c1))
    # grupos sem fornecedor cobertos → Cadastro em dia (verde)
    t.abre('Agro Norte'); t.can('Combustível'); t.can('Peças'); t.btn('Salvar'); time.sleep(.2); c2=t.chip(); cc2=t.J(CHIPC)
    t.chk('6 cobrir os 2 grupos deixa o cabeçalho "Cadastro em dia" em verde', 'Cadastro em dia' in c2 and cc2!=cc0, (c2,cc0,cc2))
    # suspender o único fornecedor de Combustível → volta a pendência
    t.abre('Agro Norte'); t.btn('Suspender parceiro'); t.setk('motivo','Nota fiscal com divergência recorrente'); t.btn('Salvar'); time.sleep(.2); c3=t.chip(); ln=t.lin('Agro Norte'); st=t.st()
    t.chk('7 suspender o fornecedor atualiza cabeçalho, linha e aviso', 'grupos sem fornecedor' in c3 and 'Suspenso' in ln and 'Nota fiscal com divergência' in ln and 'Suspenso: Agro Norte' in st, (c3,ln,st))
    t.fil('Fornecedores'); ln=t.lin('Agro Norte'); t.chk('8 filtro Fornecedores: Homologado mostra Suspenso e motivo', 'Suspenso' in ln and 'Nota fiscal' in ln, ln)
    t.abre('Agro Norte'); sub=t.aside(); f=t.J(FOOT); mv=t.J("(document.getElementById('fx_g_forn_motivo')||{}).value")
    t.chk('9 suspenso abre com subtítulo, motivo gravado e Reativar parceiro', 'Suspenso: fora de cotação, oferta e crédito' in sub and mv=='Nota fiscal com divergência recorrente' and 'Reativar parceiro' in f, (mv,f))
    t.btn('Reativar parceiro'); lb=t.labs(); f=t.J(FOOT); t.c.shot(SH+'reat.png')
    t.chk('10 Reativar esconde o motivo antes de salvar', 'Motivo da suspensão' not in lb, (lb[-2:],f))
    t.btn('Salvar'); time.sleep(.2); st=t.st(); ln=t.lin('Agro Norte'); c4=t.chip()
    t.chk('11 reativado: aviso, linha volta a Sim e cabeçalho em dia', 'Reativado: Agro Norte' in st and 'Suspenso' not in ln and 'Cadastro em dia' in c4, (st,ln,c4))
    t.abre('Agro Norte'); t.btn('Suspender parceiro'); mv=t.J("(document.getElementById('fx_g_forn_motivo')||{}).value"); t.btn('Manter ativo'); t.btn('Cancelar')
    t.chk('12 suspender de novo começa com motivo vazio', mv=='', mv)
    # suspender cliente no filtro Clientes
    t.fil('Clientes'); t.abre('Frutas Real'); t.btn('Suspender parceiro'); t.setk('motivo','Atraso recorrente'); t.btn('Salvar'); time.sleep(.2); ln=t.lin('Frutas Real'); fs=t.fils()
    t.chk('13 cliente suspenso continua no filtro Clientes com Suspenso e motivo', 'Suspenso' in ln and 'Atraso recorrente' in ln and 'Clientes 5' in fs, (ln,fs))
finally: t.close()
