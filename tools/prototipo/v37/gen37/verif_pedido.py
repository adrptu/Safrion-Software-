# -*- coding: utf-8 -*-
"""Verificador · roda T04 e T06 de testes_pedido.py sem gravar evidências em validacao/ (capturas e resultado vão para o scratchpad)."""
import sys, os, time, subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import testes_pedido as tp
from cdp import Chrome
from journeys import free
tp.OUT='/private/tmp/claude-501/-Users-adrianussanders-Library-Application-Support-Claude-scratch-workspaces-3f2449ee-7729-4f0a-96cc-d0f539bf7a66-57b91317-014d-44f0-ad90-4438cd376723-scratch-2026-09-22-5d85a9/ed477ec7-a5fd-431d-bc5d-c0e06c6234e4/scratchpad/v38/verif_shots'
sel=sys.argv[1:] or ['T04','T06']
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',tp.R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    for cod,nome,fn in tp.TESTES:
        if cod not in sel: continue
        c=Chrome(port=free()); c.size(1440,1000); t=tp.T(c,f'http://127.0.0.1:{p}/',cod)
        try: fn(t)
        except Exception as ex: t.log('Execução',False,f'erro: {ex}')
        finally: c.close()
        print(f"{cod} {'PASSOU' if t.ok else 'FALHOU'} · {nome} · {len(t.passos)} passos"); [print('   ✗',x['passo'],'→',x['obs']) for x in t.passos if not x['ok']]
finally: srv.terminate()
