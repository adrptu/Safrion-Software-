# -*- coding: utf-8 -*-
"""Mapa de navegação v3.7 em Markdown: convenções, índice, e por tela rota/menu/selos/links (saída e entrada)/ações/formulários."""
import json, os
from navdata import all_screens, CAT
HERE=os.path.dirname(os.path.abspath(__file__))
MAPA=json.load(open(os.path.join(HERE,'..','menu_map.json')))
C=json.load(open(os.path.join(HERE,'project','canvas.json')))
D=all_screens()
order=[n for n in C['order'] if n in D]
rows=sorted([(v.get('page','menu'),v['y'],v['text']) for v in C['notes'].values() if v.get('kind')=='title1'])
def row_of(n):
    y=C['boards'][n]['y']; pg=C['boards'][n].get('page','menu'); t='Índice'
    for rp,ry,rt in rows:
        if rp==pg and y>=ry-300: t=rt
    return t
INC={n:[] for n in D}
for n,v in D.items():
    for t,d in v['links']:
        if d in INC and n not in INC[d] and d!=n: INC[d].append(n)
L=[]
L.append('# Mapa de navegação — Do Talhão à O.S. · protótipo v3.7')
L.append('')
L.append('**Fonte oficial:** PRD v3.7 — 23/09/2026 · **Etapa:** protótipo para validação do proprietário · **Canvas:** https://claude.ai/artifact/WPDgqGvKX6CYTCdPjidBLo')
L.append(f'**Telas:** {len(D)} ({len([n for n in D if len(n)==13])} listas/destinos de família + {len(D)-len([n for n in D if len(n)==13])} detalhes, estados e índice) · **98 famílias** cobertas · links internos {sum(len(v["links"]) for v in D.values())} · ações com efeito {sum(len(v["acoes"]) for v in D.values())} · formulários {sum(len(v["formularios"]) for v in D.values())}')
L.append('')
L.append('## Convenções do protótipo')
L.append('')
for c in [
 '**Entrada:** `Main.dc.html` é o índice central (perfis, cenários, menu vigente e módulos ocultos). O logotipo da barra lateral volta ao índice.',
 '**Menu vigente (25/09/2026):** Mapa · Cadastros ▸ · Agrícola ▸ (Planos agronômicos `PA`, Planejar safra `SAF`, Ordem de Serviço `OS`) · Suprimentos ▸ (Compra de insumos `CMP`, Estoque `EST`). Macro menus expansíveis. Os demais módulos estão ocultos do menu, preservados e alcançáveis por links; no Canvas ficam na página "Módulos ocultos (preservados)".',
 '**Processos numa só tela:** PA, SAF, CMP e EST são telas de trabalho com a faixa "Etapas do processo" (fixa; nomes no imperativo; impedimento com motivo). As etapas trocam o conteúdo na mesma tela, preservando os dados salvos; as ações listadas abaixo incluem as de todas as etapas. Módulos ocultos sequenciais (Irrigação, Máquinas, Colheita, Comercial, Logística) têm faixa de etapas por links.',
 '**Arquivos e IDs:** cada família do PRD tem a tela `XX-NN.dc.html`; detalhes `XX-NNdet.dc.html`; estados/recibos `XX-NNx-<nome>.dc.html`; processos `PA`, `SAF`, `OS`, `CMP`, `EST`.',
 '**Tabelas:** clicar na linha abre o formulário lateral preenchido (Salvar/Cancelar, aviso de não salvo, erros no campo, consulta sem permissão); seta de drill à esquerda só expande; caixa só seleciona; lixeira pede confirmação; totais abrem a composição; cabeçalho ordena e filtra por valor; primeira coluna fixa ao rolar na horizontal.',
 '**Ordens:** registro canônico de 13 ordens (fases A liberar → Liberadas → Em execução → Em conferência → Encerradas; pausa, atraso, parcial e impedimento são selos), iguais em lista, Kanban, mapa, app e detalhes.',
 '**Dados:** mundo único de demonstração (Fazenda Santa Rita, safra 2026/27, hoje = 23/09/2026). Integrações e mensagens são simuladas. Cada tela guarda o próprio estado; entre telas diferentes o estado não é compartilhado; recarregar volta ao cenário inicial.',
]: L.append(f'- {c}')
L.append('')
L.append('## Índice')
L.append('')
cur=None
for n in order:
    r=row_of(n)
    if r!=cur: L.append(f'\n**{r}**\n'); cur=r
    v=D[n]; L.append(f'- [{n.replace(".dc.html","")} · {v["titulo"]}](#{n.replace(".dc.html","").lower()})')
L.append('')
L.append('## Telas')
cur=None
for n in order:
    v=D[n]; base=v['familia']; r=row_of(n)
    if r!=cur: L.append(f'\n### {r}\n'); cur=r
    fam=CAT.get(base,{})
    L.append(f'<a id="{n.replace(".dc.html","").lower()}"></a>')
    L.append(f'#### {n.replace(".dc.html","")} · {v["titulo"]}')
    meta=[f'Arquivo `{n}`']
    if fam: meta.append(f'Família **{base} — {fam.get("titulo","")}** (PRD l. {fam.get("linha")})')
    if v['rota']: meta.append(f'Rota `{v["rota"]}`')
    if base in MAPA: meta.append(f'Menu **{MAPA[base]["area"]} › {MAPA[base]["submenu"]}**')
    L.append(' · '.join(meta))
    if v['selos']: L.append(f'- **Estados e selos visíveis:** {" · ".join(v["selos"][:18])}')
    if v['links']:
        L.append('- **Leva a:** '+'; '.join(f'{t} → `{d}`' for t,d in v['links'] if d!=n))
    if INC.get(n): L.append('- **Chega de:** '+', '.join(f'`{x}`' for x in INC[n][:25])+(' …' if len(INC[n])>25 else ''))
    if v['acoes']:
        L.append('- **Ações com efeito (resultado exibido):**')
        for t,m in v['acoes']: L.append(f'  - *{t}* → {m}')
    fs=[f for f in v['formularios'] if f['titulo'] or f['campos']]
    if fs:
        L.append('- **Formulários (painel lateral):**')
        for f in fs: L.append(f'  - **{f["titulo"] or "(sem título)"}** — campos: {", ".join(f["campos"]) or "leitura"}' + (f' · confirmar: *{f["confirmar"]}*' if f['confirmar'] else ''))
    L.append('')
out=os.path.join(HERE,'..','entrega','Do-talhao-a-OS_v3.7_mapa-de-navegacao.md')
os.makedirs(os.path.dirname(out),exist_ok=True)
open(out,'w').write('\n'.join(L)); print(out, len('\n'.join(L)),'chars')
