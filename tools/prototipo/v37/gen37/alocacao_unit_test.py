# -*- coding: utf-8 -*-
"""Troca de recurso na O.S. (pedido do proprietário, 14/10/2026: "ordem de serviço agrícola está faltando edição de ... recursos (pessoas e
máquinas)"): regras de alocacao.py (alVigente, alDaOrdem, alCandidatos, alTrocar) no motor do cenário, sem navegador. Dados sintéticos."""
import os, sys, json, subprocess, tempfile
from pathlib import Path
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cenario
from areas.processo_os import JS_NUCLEO, _ordens

TEST = r'''
const assert=require('node:assert/strict'); let n=0, f=0;
function chk(nome,a,e){ try{ assert.deepEqual(a,e); console.log('OK '+nome); }catch(x){ f++; console.log('FALHA '+nome+' · '+JSON.stringify(a)); } n++; }
function erro(fn){ try{ fn(); return ''; }catch(e){ return String(e.message); } }
const P=k=>g2pf(k);
let c=cenClone(CEN0); const j0=JSON.stringify(c);
const r0=alDaOrdem(c,'OS-0430');
chk('OS-0430: Trator 03, pulverizador, Marcos e Paula, condicionais (seed da semana do PCP)',r0.map(x=>[x.r,x.tipo,x.cond,x.de]),[['T03','Máquina',true,null],['PJ','Implemento',true,null],['MAR','Pessoa',true,null],['PAU','Pessoa',true,null]]);
chk('leitura não muda o cenário',JSON.stringify(c),j0);
const cd=alCandidatos(c,'OS-0430','T03');
chk('substitutos do Trator 03 em 25/09 13:00–20:24: T1 bloqueado, T02 ocupado na OS-0420, T04 livre',cd.map(x=>[x.r,x.ok,x.motivo]),
  [['T1',false,'bloqueado na Manutenção'],['T02',false,'ocupado na OS-0420 em 25/09 13:00–16:00'],['T04',true,'']]);
chk('implemento sem outro da mesma função: nenhum substituto',alCandidatos(c,'OS-0430','PJ'),[]);
chk('operador só por operador (Paula é caldeiro): Carlos, ocupado na OS-0420',alCandidatos(c,'OS-0430','MAR').map(x=>[x.r,x.ok]),[['CAR',false]]);
chk('sem o papel (Otávio, PCM): recusa e nada muda',[erro(()=>alTrocar(c,'OS-0430','T03','T04',P('Otávio'))).indexOf('decisão de')>=0,JSON.stringify(c)===j0],[true,true]);
chk('substituto ocupado: recusa com o motivo',erro(()=>alTrocar(c,'OS-0430','T03','T02',P('Caio'))),'Troca recusada: Trator 02 MF 7719 ocupado na OS-0420 em 25/09 13:00–16:00. Nada foi alterado.');
chk('ordem em execução (OS-0420): recusa',erro(()=>alTrocar(c,'OS-0420','T02','T04',P('Caio'))).indexOf('só antes da execução')>=0,true);
const m=alTrocar(c,'OS-0430','T03','T04',P('Caio'));
chk('Caio (PCP) troca Trator 03 → Trator 04',[m.msg,c.ordens['OS-0430'].rec],['Trator 03 → Trator 04 na OS-0430.',{T03:'T04'}]);
chk('painel: Trator 04 no lugar, com o original',alDaOrdem(c,'OS-0430').filter(x=>x.tipo==='Máquina').map(x=>[x.r,x.de]),[['T04','T03']]);
chk('histórico da troca com quem e quando',c.ordens['OS-0430'].recHist.map(h=>[h.de,h.para,h.por]),[['T03','T04','Caio (PCP)']]);
chk('outras ordens com o Trator 03 seguem iguais (OS-0421)',alDaOrdem(c,'OS-0421').some(x=>x.r==='T03'),true);
chk('alocação vigente: blocos da OS-0430 no Trator 04',alVigente(c).filter(a=>a.os==='OS-0430'&&a.r==='T04').length,1);
chk('repetir a mesma troca (duplo clique): recusa, sem segundo efeito',[erro(()=>alTrocar(c,'OS-0430','T03','T04',P('Caio'))).indexOf('não está na OS-0430')>=0,c.ordens['OS-0430'].recHist.length],[true,1]);
chk('Trator 03 volta a ser substituto do Trator 04 (livre na janela)',alCandidatos(c,'OS-0430','T04').find(x=>x.r==='T03').ok,true);
alTrocar(c,'OS-0430','T04','T03',P('Proprietário'));
chk('voltar ao original apaga a troca e registra no histórico (perfil com todos os papéis)',[c.ordens['OS-0430'].rec,c.ordens['OS-0430'].recHist.length,c.ordens['OS-0430'].recHist[1].por.indexOf('Proprietário')===0],[{},2,true]);
const lib=cenClone(CEN0); lib.man.ativos.a01.cond='Disponível';
chk('Trator T1 apto na Manutenção: deixa de ser bloqueado e o bloco de manutenção não conta',alCandidatos(lib,'OS-0430','T03').find(x=>x.r==='T1').ok,true);
chk('OS-0431 (T1 em 24/09): com o T1 bloqueado, alerta de manutenção; apto, sem alerta',[alDaOrdem(CEN0,'OS-0431').find(x=>x.r==='T1').alertas.length>0,alDaOrdem(lib,'OS-0431').find(x=>x.r==='T1').alertas.length],[true,0]);
// revisão Codex 6167883199 (S2): cancelar libera o compromisso futuro; ordem que saiu do estado não volta; evento externo fica
{ const cc=cenClone(CEN0); const antes=alVigente(cc).filter(a=>a.os==='OS-0430').length;
  osc_cancelar(cc,'OS-0430','teste de cancelamento',null,P('Proprietário'));
  chk('cancelar a OS-0430 (comando real) libera os 4 blocos dela; o Trator 03 fica só com a OS-0421',[antes,cc.ordens['OS-0430'].etapa,alVigente(cc).filter(a=>a.os==='OS-0430').length,[...new Set(alVigente(cc).filter(a=>a.r==='T03').map(a=>a.os))]],[4,'Canceladas',0,['OS-0421']]);
  chk('com a OS-0430 cancelada, o Trator 03 deixa de ser ocupado nela: substituto da OS-0421 vê só os choques reais',alChoques(cc,'T03','OS-0421',AL0.aloc.filter(a=>a.os==='OS-0421'&&a.r==='T03')).some(x=>x.com==='OS-0430'),false);
  const rm=cenClone(CEN0); delete rm.ordens['OS-0430'];
  chk('ordem que saiu do estado não ressuscita na alocação; eventos de fora do cenário (OS-0419, OS-0423) e a manutenção ficam',[alVigente(rm).some(a=>a.os==='OS-0430'),alVigente(rm).some(a=>a.os==='OS-0419'),alVigente(rm).some(a=>a.os==='OS-0423'),alVigente(rm).some(a=>a.sit==='manutenção')],[false,true,true,true]); }
console.log('RESULTADO '+(n-f)+'/'+n);
process.exit(f?1:0);
'''


def main():
    osd = 'const OSD = ' + json.dumps(dict(ords=_ordens()), ensure_ascii=False) + ';\n'
    src = cenario.perfis_js() + cenario.js_prefixo() + osd + JS_NUCLEO + TEST
    with tempfile.TemporaryDirectory(prefix='aloc-') as d:
        p = Path(d) / 't.js'; p.write_text(src)
        r = subprocess.run(['node', str(p)], text=True, capture_output=True)
        print(r.stdout); print(r.stderr[-1500:], end='')
        return r.returncode


if __name__ == '__main__':
    sys.exit(main())
