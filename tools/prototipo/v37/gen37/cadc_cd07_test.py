# -*- coding: utf-8 -*-
"""CD-07 · estrutura gerencial (15 verificações no Chrome): árvore Dimensão → código, Cultura e Processo vindos do CD-02 (só a
tradução edita), vínculos (grupos da natureza, operações do processo, rateio do centro), versão em vigor × rascunho no cabeçalho,
'Importar do ERP' simulado com prévia, 'Publicar estrutura' e rótulos sem jargão."""
# TABELAS-FOCO (06/10/2026): origem, código superior (painel) e o que muda no rascunho (coluna No rascunho; a versão v6 está no cabeçalho)
from cadc_lib import T
import time
t=T(); J=t.J
try:
    t.goto('CD-07.dc.html'); body=J("document.body.innerText")
    def pv(txt,k): t.openrow(0,txt); v=t.fv(k) or ''; t.cancel(); return v   # campo do painel do código (origem e vínculos, revisão TABR)
    t.chk('cabeçalho com versão em vigor, rascunho e pendência; primária "Cadastrar código"; secundárias Importar e Publicar',
          'v5 em vigor · rascunho v6 com 3 alterações · 1 tradução pendente' in t.header() and 'Cadastrar código' in t.bloco()
          and 'Importar do ERP' in body and 'Publicar estrutura' in body and 'Publicar estrutura v6' not in body and not t.errs(), t.header())
    t.chk('Cultura vem do CD-02 (5 culturas, com milho) e Processo é etapa (TRAT), sem PULV nem CR-SOJA',
          # TABELAS-FOCO (06/10/2026); revisão TABR (09/10/2026, A1): a origem e os vínculos ficam no painel do código
          'Cultura 5 códigos' in (t.anyrow(0,'Cultura 5') or '') and pv('MILHO','origT')=='Culturas e cultivares' and 'operações Pulverização' in pv('TRAT','vincT')
          and 'PULV' not in body and 'CR-SOJA' not in body, [t.anyrow(0,'Cultura 5'),pv('MILHO','origT'),pv('TRAT','vincT')])
    t.openrow(0,'3.1.01'); sup=t.fv('sup'); t.cancel()   # o código superior saiu da célula do código para o painel (TABELAS-FOCO)
    t.chk('natureza mostra grupos do CD-06 e hierarquia; centro de responsabilidade mostra o rateio',
          'grupos Fertilizantes, Corretivos' in pv('3.1.01','vincT') and sup=='3.1' and 'soma 6 naturezas' in pv('Custo direto','vincT')
          and 'rateio por horas de máquina' in pv('CC-OFI','vincT'), [pv('3.1.01','vincT'),pv('CC-OFI','vincT')])
    t.openrow(0,'SOJA'); d1=t.dlg(); t.cancel(); t.openrow(0,'3.1.05'); d2=t.dlg(); t.cancel()
    t.chk('exclusão bloqueada com motivo (no painel): cultura do CD-02 e natureza usada em grupos',
          'vem de Culturas e cultivares' in d1 and 'natureza de grupos de insumo' in d2, [d1[-160:],d2[-160:]])
    t.openrow(0,'SOJA'); d=t.dlg()
    t.chk('código do CD-02 abre só com a tradução editável', all(t.fdis(k) for k in ('cod','nome','dim','ini')) and not t.fdis('trad') and 'só a tradução' in d, d[:200])
    t.fset('trad','Conta do ERP'); t.fset('conta','cultura 01'); t.btn('Salvar'); time.sleep(.2)
    t.chk('tradução salva no rascunho: SOJA mapeada, "alterado na v6" e 4 alterações no cabeçalho',
          # revisão TABR (09/10/2026, A1): a Situação logo depois do código ("SOJA Mapeado …"); No rascunho continua no fim
          'cultura 01' in (t.rowtxt(0,'SOJA') or '') and (t.rowtxt(0,'SOJA') or '').startswith('SOJA Mapeado') and (t.rowtxt(0,'SOJA') or '').endswith(' Alterado') and 'rascunho v6 com 4 alterações' in t.header(), [t.rowtxt(0,'SOJA'),t.header()])
    t.openrow(0,'3.1.02'); L=t.labels()
    t.chk('rótulos sem jargão e grupos de insumo só leitura na natureza',
          'Tradução no ERP' in L and 'Tipo de operação (TOP) no ERP' in L and 'Grupos de insumo' in L and 'Como a integração traduz' not in L and 'TOP do ERP' not in L
          and t.fdis('grp') and 'Herbicidas' in (t.fv('grp') or ''), L)
    t.fset('sup','9.9'); t.btn('Salvar')
    t.chk('código superior inexistente é barrado junto ao campo', 'Não existe o código 9.9 em Natureza.' in t.alerts(), t.alerts())
    t.cancel()
    t.clk('Cadastrar código'); ops=t.fopts('dim'); t.fset('dim','Centro de responsabilidade'); L=t.labels()
    for k,v in [('cod','CC-MAQ'),('nome','Máquinas · apoio'),('rat','Horas de máquina'),('ini','2026-10-01'),('conta','centro 313')]: t.fset(k,v)
    t.btn('Salvar'); time.sleep(.2)
    t.chk('novo centro: dimensão sem Cultura/Processo, pede o rateio e entra no rascunho',
          # revisão TABR (09/10/2026, A1): os vínculos (rateio) ficam no painel do código
          'Cultura' not in ops and 'Processo' not in ops and 'Direcionador de rateio' in L and (t.rowtxt(0,'CC-MAQ') or '').endswith(' Novo') and 'rateio por horas de máquina' in pv('CC-MAQ','vincT'),
          [ops,L,t.rowtxt(0,'CC-MAQ'),pv('CC-MAQ','vincT'),t.alerts()])
    t.clk('Importar do ERP'); pv=J("(document.querySelector('[aria-label=\"Prévia da importação do ERP\"]')||{}).innerText||''")
    t.chk('Importar do ERP mostra a prévia simulada (novos, nome alterado, sem conta)',
          'simulada' in pv and '3.1.07 · Serviços de terceiros' in pv and 'Defensivos → Defensivos agrícolas' in pv and 'PRJ-PIVO3' in pv, pv[:300])
    t.clk('Trazer 3 mudanças para o rascunho'); time.sleep(.2)
    t.chk('trazer põe 2 códigos novos e 1 nome no rascunho, sem publicar',
          t.rowtxt(0,'3.1.07') and t.rowtxt(0,'CC-ARM') and 'Defensivos agrícolas' in (t.rowtxt(0,'3.1.02') or '') and 'rascunho v6 com 8 alterações' in t.header() and 'nada foi publicado' in t.toast(),
          [t.header(),t.toast()])
    t.clk('Importar do ERP')
    t.chk('segunda importação não repete as mudanças', 'não tem mudanças novas' in t.toast(), t.toast())
    t.aviso('Publicar estrutura'); time.sleep(.2); ts=t.toast()
    t.chk('publicar: v6 em vigor, v5 preservada, código sem conta fica fora',
          'estrutura v6 publicada' in ts and 'v5 preservada' in ts and 'PRJ-PIVO3' in ts and 'v6 em vigor · 1 tradução pendente' in t.header() and 'rascunho' not in t.header(), [ts,t.header()])
    sem=J("![...document.querySelectorAll('main button')].some(b=>b.innerText.indexOf('Publicar estrutura')>=0)")
    t.chk('sem alterações no rascunho não aparece "Publicar estrutura"; sem erros de JS', sem and not t.errs(), [sem,t.errs()])
    t.shot('cadc_cd07.png')
finally:
    t.fim()
