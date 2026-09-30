# -*- coding: utf-8 -*-
"""Pacote HTML executável do protótipo v3.7: telas + runtime + página inicial + instruções."""
import os, zipfile, shutil, json
HERE=os.path.dirname(os.path.abspath(__file__)); PROJ=os.path.join(HERE,'project')
OUT=os.path.join(HERE,'..','entrega','Do-talhao-a-OS_v3.7_prototipo-html.zip')
SUP=os.path.join(HERE,'..','..','telas','pack','measure','support.js')
LEIA="""Do Talhão à O.S. — protótipo navegável v3.7 (pacote HTML)
Fonte oficial: PRD v3.7 — 23/09/2026 · etapa: validação do proprietário · dados fictícios

COMO ABRIR
1. Descompacte a pasta inteira (não abra os arquivos de dentro do ZIP).
2. Abra o arquivo ABRIR-AQUI.html com dois cliques (Chrome, Edge ou Safari).
3. Navegue clicando: o índice leva aos perfis, cenários e áreas; o logotipo do menu volta ao índice.

DEPENDÊNCIAS
- Precisa de internet ao abrir: o motor das telas (support.js) carrega a biblioteca de interface e as fontes pela rede.
- Nenhuma credencial, servidor ou instalação. Nada é enviado a lugar nenhum; ações mostram resultados simulados.
- Se o navegador bloquear a navegação entre arquivos locais, rode na pasta:  python3 -m http.server 8000
  e abra http://localhost:8000/ABRIR-AQUI.html

LIMITES
- Cada tela guarda o que foi clicado enquanto está aberta; ao recarregar, volta ao cenário inicial.
- Troca de perfil demonstra a experiência, não comprova segurança de acesso.
- Aprovar o protótipo não inicia o software real.
"""
ABRIR='<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=Main.dc.html"><title>Do Talhão à O.S. · protótipo v3.7</title></head><body><a href="Main.dc.html">Abrir o protótipo</a></body></html>'
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    root='Do-talhao-a-OS_prototipo-v3.7/'
    for f in sorted(os.listdir(PROJ)):
        if f.endswith('.dc.html'): z.write(os.path.join(PROJ,f),root+f)
    z.write(SUP,root+'support.js')
    z.writestr(root+'ABRIR-AQUI.html',ABRIR); z.writestr(root+'LEIA-ME.txt',LEIA)
print(OUT, round(os.path.getsize(OUT)/1e6,1),'MB')
