# -*- coding: utf-8 -*-
"""CD-07 · estrutura gerencial (15 verificações no Chrome): árvore Dimensão → código, Cultura e Processo vindos do CD-02 (só a
tradução edita), vínculos (grupos da natureza, operações do processo, rateio do centro), versão em vigor × rascunho no cabeçalho,
'Importar do ERP' simulado com prévia, 'Publicar estrutura' e rótulos sem jargão."""
from cadc_lib import T
import time
t=T(); J=t.J
try:
    t.goto('CD-07.dc.html'); body=J("document.body.innerText")
    t.chk('cabeçalho com versão em vigor, rascunho e pendência; primária "Cadastrar código"; secundárias Importar e Publicar',
          'v5 em vigor · rascunho v6 com 3 alterações · 1 tradução pendente' in t.header() and 'Cadastrar código' in t.header()
          and 'Importar do ERP' in body and 'Publicar estrutura' in body and 'Publicar estrutura v6' not in body and not t.errs(), t.header())
    t.chk('Cultura vem do CD-02 (5 culturas, com milho) e Processo é etapa (TRAT), sem PULV nem CR-SOJA',
          '5 códigos · de Culturas e cultivares' in (t.anyrow(0,'Cultura 5') or '') and t.rowtxt(0,'MILHO') and 'operações Pulverização' in (t.rowtxt(0,'TRAT') or '')
          and 'PULV' not in body and 'CR-SOJA' not in body, [t.anyrow(0,'Cultura 5'),t.rowtxt(0,'TRAT')])
    t.chk('natureza mostra grupos do CD-06 e hierarquia; centro de responsabilidade mostra o rateio',
          'grupos Fertilizantes, Corretivos' in (t.rowtxt(0,'3.1.01') or '') and 'em 3.1' in (t.rowtxt(0,'3.1.01') or '') and 'soma 6 naturezas' in (t.rowtxt(0,'Custo direto') or '')
          and 'rateio por horas de máquina' in (t.rowtxt(0,'CC-OFI') or ''), [t.rowtxt(0,'3.1.01'),t.rowtxt(0,'CC-OFI')])
    t.chk('exclusão bloqueada com motivo: cultura do CD-02 e natureza usada em grupos',
          'vem de Culturas' in (t.rowtxt(0,'SOJA') or '') and 'usada em grupos' in (t.rowtxt(0,'3.1.05') or ''), [t.rowtxt(0,'SOJA'),t.rowtxt(0,'3.1.05')])
    t.openrow(0,'SOJA'); d=t.dlg()
    t.chk('código do CD-02 abre só com a tradução editável', all(t.fdis(k) for k in ('cod','nome','dim','ini')) and not t.fdis('trad') and 'só a tradução' in d, d[:200])
    t.fset('trad','Conta do ERP'); t.fset('conta','cultura 01'); t.btn('Salvar'); time.sleep(.2)
    t.chk('tradução salva no rascunho: SOJA mapeada, "alterado na v6" e 4 alterações no cabeçalho',
          'cultura 01' in (t.rowtxt(0,'SOJA') or '') and 'alterado na v6' in (t.rowtxt(0,'SOJA') or '') and 'rascunho v6 com 4 alterações' in t.header(), [t.rowtxt(0,'SOJA'),t.header()])
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
          'Cultura' not in ops and 'Processo' not in ops and 'Direcionador de rateio' in L and 'novo na v6' in (t.rowtxt(0,'CC-MAQ') or '') and 'rateio por horas de máquina' in (t.rowtxt(0,'CC-MAQ') or ''),
          [ops,L,t.rowtxt(0,'CC-MAQ'),t.alerts()])
    t.clk('Importar do ERP'); pv=J("(document.querySelector('[aria-label=\"Prévia da importação do ERP\"]')||{}).innerText||''")
    t.chk('Importar do ERP mostra a prévia simulada (novos, nome alterado, sem conta)',
          'simulada' in pv and '3.1.07 · Serviços de terceiros' in pv and 'Defensivos → Defensivos agrícolas' in pv and 'PRJ-PIVO3' in pv, pv[:300])
    t.clk('Trazer 3 mudanças para o rascunho'); time.sleep(.2)
    t.chk('trazer põe 2 códigos novos e 1 nome no rascunho, sem publicar',
          t.rowtxt(0,'3.1.07') and t.rowtxt(0,'CC-ARM') and 'Defensivos agrícolas' in (t.rowtxt(0,'3.1.02') or '') and 'rascunho v6 com 8 alterações' in t.header() and 'nada foi publicado' in t.toast(),
          [t.header(),t.toast()])
    t.clk('Importar do ERP')
    t.chk('segunda importação não repete as mudanças', 'não tem mudanças novas' in t.toast(), t.toast())
    t.clk('Publicar estrutura'); time.sleep(.2); ts=t.toast()
    t.chk('publicar: v6 em vigor, v5 preservada, código sem conta fica fora',
          'estrutura v6 publicada' in ts and 'v5 preservada' in ts and 'PRJ-PIVO3' in ts and 'v6 em vigor · 1 tradução pendente' in t.header() and 'rascunho' not in t.header(), [ts,t.header()])
    t.clk('Publicar estrutura')
    t.chk('publicar sem alterações avisa que não há nada a publicar; sem erros de JS', 'Nada a publicar' in t.toast() and not t.errs(), [t.toast(),t.errs()])
    t.shot('cadc_cd07.png')
finally:
    t.fim()
