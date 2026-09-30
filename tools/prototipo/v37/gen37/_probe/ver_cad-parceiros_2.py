# -*- coding: utf-8 -*-
"""Verificador CD-05 · formulário: CPF/CNPJ primeiro, duplicidade ao digitar, seções por papel, ajuda condicional, desmarcar papel, transportador."""
import importlib.util, os, time
s=importlib.util.spec_from_file_location('vl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_lib.py')); L=importlib.util.module_from_spec(s); s.loader.exec_module(L)
t=L.T(); SH=os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_')
SECS="(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return []; return [...a.querySelectorAll('div')].filter(d=>!d.querySelector('div,label,input') && /^[A-ZÇÃÉÍÓÚ ]{6,}$/.test(d.innerText.trim())).map(d=>d.innerText.trim());})()"
DUP="[...document.querySelectorAll('aside [role=status]')].map(x=>x.innerText.replace(/\\s+/g,' ')).join(' | ')"
HELP="(k)=>{const a=document.querySelector('aside[role=dialog]').innerText.replace(/\\s+/g,' '); const L={contato:['Nome do contato','E-mail'],email:['E-mail','WhatsApp'],cnpj:['CPF ou CNPJ','Nome ou razão social']}[k]; const i=a.indexOf(L[0]+' '); const j=a.indexOf(' '+L[1]+' ',i+1); return a.slice(i,j);}"
try:
    t.load(); t.novo()
    lb=t.labs(); t.chk('1 novo: começa pelo CPF/CNPJ, sem seções antes de marcar papel', lb[:3]==['CPF ou CNPJ','Nome ou razão social','Papéis'] and t.J(SECS)==[], (lb,t.J(SECS)))
    t.setk('cnpj','9876543200011'); d1=t.J(DUP); t.setk('cnpj','98765432000110'); d2=t.J(DUP)
    t.chk('2 duplicidade: 13 dígitos sem aviso; 14 dígitos só números acha Coopergrão', d1=='' and 'Já cadastrado: Coopergrão (Cliente)' in d2 and 'Abrir e ativar papel' in d2, (d1,d2))
    t.setk('cnpj','123.456.789-09'); d3=t.J(DUP)
    t.chk('3 duplicidade por CPF: Adão Ferreira', 'Já cadastrado: Adão Ferreira (Prestador)' in d3, d3)
    t.setk('cnpj','61.222.333/0001-44')
    for p in ['Prestador','Cliente','Fornecedor','Transportador','Parceiro de crédito']: t.can(p)
    sc=t.J(SECS); t.chk('4 cinco papéis: títulos de seção na ordem', sc==['FORNECEDOR','CLIENTE','PARCEIRO DE CRÉDITO','TRANSPORTADOR','PRESTADOR'], sc)
    papv=t.J("document.getElementById('fx_g_forn_papeis')?document.getElementById('fx_g_forn_papeis').value:[...document.querySelectorAll('aside[role=dialog] label')].filter(l=>l.querySelector('input[type=checkbox]')&&l.querySelector('input').checked).map(l=>l.innerText.trim()).join('|')")
    print('papeis marcados', papv)
    hc=t.J(f"({HELP})('contato')"); he=t.J(f"({HELP})('email')")
    t.chk('5 com Fornecedor: ajuda de homologação em contato e e-mail', 'homologar' in (hc or '') and 'homologar' in (he or ''), (hc,he))
    t.J("document.querySelector('aside[role=dialog]').scrollTop=0"); t.c.shot(SH+'form5.png')
    ah=t.J("(()=>{const a=document.querySelector('aside[role=dialog]'); const r=a.getBoundingClientRect(); const sv=[...a.querySelectorAll('button')].find(b=>b.innerText.trim()==='Salvar'); const s=sv.getBoundingClientRect(); return {top:r.top,h:r.height,sh:a.scrollHeight,ch:a.clientHeight,save:[s.top,s.bottom],vh:innerHeight, ov:getComputedStyle(a).overflowY};})()")
    print('aside', ah)
    for p in ['Fornecedor','Cliente','Parceiro de crédito','Prestador']: t.can(p)
    sc=t.J(SECS); lb=t.labs(); hc=t.J(f"({HELP})('contato')")
    t.chk('6 desmarcar papéis some com as seções e com a ajuda de homologação', sc==['TRANSPORTADOR'] and 'Grupos homologados' not in lb and 'Produtos de interesse' not in lb and 'homologar' not in (hc or ''), (sc,lb,hc))
    t.setk('nome','Frete Rápido Ltda'); t.setk('rntrc','1234567'); t.btn('Salvar'); al=t.al()
    t.chk('7 transportador: RNTRC com 8 dígitos e veículos obrigatórios', 'O RNTRC tem 8 dígitos.' in al and 'Escolha ao menos uma opção.' in al, al)
    t.setk('rntrc','12345678'); t.can('Truck graneleiro 14 t'); t.btn('Salvar'); time.sleep(.2)
    ln=t.lin('Frete Rápido'); t.chk('8 transportador salvo: RNTRC e veículo na linha, contagem 3', not t.aberto() and 'RNTRC 12345678' in ln and 'Truck graneleiro 14 t' in ln and 'Transportadores 3' in t.fils(), (ln,t.st()))
    # papel marcado com erro e depois desmarcado não bloqueia
    t.novo(); t.setk('cnpj','71.333.444/0001-55'); t.setk('nome','Poda Certa ME'); t.can('Cliente'); t.btn('Salvar'); a1=t.al()
    t.can('Cliente'); t.can('Prestador'); ops=t.J("[...document.querySelectorAll('aside[role=dialog] label')].filter(l=>l.querySelector('input[type=checkbox]')).map(l=>l.innerText.trim())")
    print('opções (papéis + operações):', ops)
    t.can('Poda'); t.btn('Salvar'); time.sleep(.2); ln=t.lin('Poda Certa')
    t.chk('9 erro em seção desmarcada não bloqueia salvar', 'Escolha ao menos uma opção.' in a1 and not t.aberto() and 'Prestador' in ln and 'Cliente' not in ln, (a1,ln,t.al()))
    # existente: CPF/CNPJ só consulta
    t.abre('Coop. Vale'); tit=t.J("(document.querySelector('aside[role=dialog] h2')||{}).innerText"); dis=t.J("document.getElementById('fx_g_forn_cnpj').disabled||document.getElementById('fx_g_forn_cnpj').readOnly")
    hcn=t.J(f"({HELP})('cnpj')"); sc=t.J(SECS)
    t.chk('10 existente: título, CPF/CNPJ só consulta com ajuda, seções Fornecedor e Cliente', tit=='Parceiro · Coop. Vale' and dis and 'não muda depois do cadastro' in (hcn or '') and sc==['FORNECEDOR','CLIENTE'], (tit,dis,hcn,sc))
    t.c.shot(SH+'form10.png')
    t.btn('Cancelar'); t.chk('11 cancelar sem mudar fecha sem pedir confirmação', not t.aberto(), t.aside()[:120])
    # abrir e ativar papel e cancelar: deve avisar alteração não salva
    t.novo(); t.can('Transportador'); t.setk('cnpj','66.890.123/0001-60'); d=t.J(DUP); t.btn('Abrir e ativar papel')
    tit=t.J("(document.querySelector('aside[role=dialog] h2')||{}).innerText"); on=t.on('Transportador'); st=t.st()
    t.chk('12 Abrir e ativar papel: Coop. Vale com Transportador marcado e aviso', 'Já cadastrado: Coop. Vale (Fornecedor, Cliente)' in d and tit=='Parceiro · Coop. Vale' and on and 'Transportador marcado' in st, (d,tit,on,st))
    t.btn('Cancelar'); w=t.J("document.body.innerText.indexOf('Há alterações não salvas')>=0")
    t.chk('13 cancelar depois de ativar papel pede confirmação', w and t.aberto(), w)
    t.btn('Descartar alterações'); ln=t.lin('Coop. Vale')
    t.chk('14 descartar não grava o papel', not t.aberto() and 'Transportador' not in ln and t.errs()=='', (ln,t.errs()))
finally: t.close()
