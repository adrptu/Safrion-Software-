# -*- coding: utf-8 -*-
"""Verificador CD-05 · filtro de coluna dentro do filtro de papel, cadastro fora do filtro atual, cobertura, busca, rodapé."""
import importlib.util, os, time, json
s=importlib.util.spec_from_file_location('vl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_lib.py')); L=importlib.util.module_from_spec(s); s.loader.exec_module(L)
t=L.T(); SH=os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_')
OPTS="[...document.querySelectorAll('[data-root] label')].filter(e=>e.closest('[role=table]')===null && !e.closest('aside')).map(e=>e.innerText.replace(/\\s+/g,' ').trim()).filter(Boolean)"
try:
    t.load()
    t.fil('Clientes'); t.J("document.querySelector('[aria-label=\"Filtrar Situação do papel\"]').click()"); time.sleep(.4); o1=t.J(OPTS)
    t.J("document.querySelector('[aria-label=\"Filtrar Papéis\"]').click()"); time.sleep(.4); o2=t.J(OPTS)
    t.chk('1 filtro de coluna no filtro Clientes só oferece valores das linhas visíveis', not any(x.startswith('— ') for x in o1) and not any(x.startswith('Transportador') or x.startswith('Parceiro de crédito') for x in o2), (o1,o2))
    t.J("[...document.querySelectorAll('[data-root] label')].find(l=>l.innerText.trim().startsWith('Transportador')).querySelector('input').click()"); time.sleep(.3)
    t.chk('2 (consequência) escolher um valor oferecido esvazia a grade', len(t.rows())>0, (len(t.rows()), t.J("document.querySelectorAll('[role=table]')[0].parentElement.parentElement.innerText.slice(0,200)")))
    t.J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Limpar').click()"); time.sleep(.2); t.J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Fechar').click()"); time.sleep(.2)
    # cadastro de outro papel a partir do filtro Fornecedores
    t.fil('Fornecedores'); t.novo(); t.setk('cnpj','37.555.666/0001-77'); t.setk('nome','Laticínios Serra Verde'); t.can('Cliente'); t.can('Mamão Formosa classe A'); t.btn('Salvar'); time.sleep(.2)
    fs=t.fils(); ln=t.lin('Laticínios Serra Verde')
    t.chk('3 cliente cadastrado no filtro Fornecedores: volta a Todos e a linha aparece', fs.startswith('Todos 18') and ln and t.J("document.querySelector('[role=group][aria-label=\"Filtrar por papel\"] button[aria-pressed=true]').innerText").startswith('Todos'), (fs,ln))
    # cobertura: clicar no grupo abre quem recebe
    t.fil('Fornecedores'); t.J("(()=>{const t=document.querySelectorAll('[role=table]')[1]; const r=[...t.querySelectorAll('[role=row]')].find(r=>r.innerText.split('\\n')[0].trim()==='Sementes'); (r.querySelector('[role=cell] span')||r).click();})()"); time.sleep(.4)
    a=t.aside(); t.chk('4 cobertura: clicar em Sementes abre os fornecedores que recebem cotação', 'Sementes Vale' in a and 'Coop. Vale' in a, a[:300])
    t.anybtn('Fechar'); t.J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label]'); if(b) b.click();})()"); time.sleep(.3)
    # busca + filtro sem resultado
    t.fil('Todos'); t.J(f"({L.SETV})('[data-root] input[placeholder^=\"Buscar\"]','Banco')"); time.sleep(.3); n1=len(t.rows()); t.fil('Clientes'); n2=len(t.rows())
    body=t.J("document.querySelectorAll('[role=table]')[0].parentElement.parentElement.innerText.replace(/\\s+/g,' ').slice(0,300)")
    t.chk('5 busca "Banco" em Todos acha 1; em Clientes mostra estado vazio', n1==1 and n2==0, (n1,n2,body))
    t.J(f"({L.SETV})('[data-root] input[placeholder^=\"Buscar\"]','')"); time.sleep(.2); t.fil('Todos')
    # rodapé da suspensão (visual)
    t.abre('Fertisul'); t.btn('Suspender parceiro'); t.J("(()=>{const a=document.querySelector('aside[role=dialog]'); a.scrollTop=a.scrollHeight;})()"); time.sleep(.3); t.c.shot(SH+'rodape.png')
    bt=t.J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Manter ativo'); const s=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar'); return [getComputedStyle(b).color, b.getBoundingClientRect().left, s.getBoundingClientRect().left];})()")
    print('botões rodapé', bt)
    t.btn('Manter ativo'); t.btn('Cancelar')
    t.chk('6 sem erro JS de tela (fora o aviso do motor)', all('g2toast' in x for x in t.errs().split(' | ') if x), t.errs()[:200])
finally: t.close()
