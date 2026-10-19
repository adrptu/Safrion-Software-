#!/usr/bin/env python3
"""PT06/EX35: formulário gerado e g2save real, sem navegador/serviço externo.

Execute: python3 pt06_unit.py (Node no PATH, ou variável NODE).
Não substitui a revisão de teclado/celular nem prova isolamento no backend.
"""
import copy
import json
import os
from pathlib import Path
import subprocess
from unittest.mock import patch

import engine as E
from areas import parceiros as P

with patch.object(P, 'shell37'):
    P.pt06()
    grids = copy.deepcopy(E.GRIDS)
    hooks = E.EXTRAJS[0]
    P.pt07()
    perfil = copy.deepcopy(E.GRIDS)

co = next(g for g in grids if g['id'] == 'g_co')
responsavel = next(f for f in co['edit']['fields'] if f['k'] == 'resp')
assert responsavel['opts'] == ['Marta Nunes', 'Diego Prado']
usuarios = next(g for g in perfil if any(r['id'] == 'u1' for r in g['rows']))
assert [r['v']['nome'] for r in usuarios['rows'] if r['id'] in ('u1', 'u2')] == responsavel['opts']
assert 'Sônia Reis' not in responsavel['opts']

checks = r"""
const assert=require('node:assert/strict'); let passed=0;
function check(name,fn){ fn(); passed++; console.log('PASS '+name); }
const sp=GRIDS.find(g=>g.id==='g_co');
function setup(resp='Diego Prado'){
 const self={state:{},setState(p){Object.assign(this.state,p)}}; const v={};
 // Mesma ordem do engine: PREVALS -> montagem g2part da célula -> EXTRAVALS -> clique.
 if(typeof PREVALS==='function') PREVALS(self,v);
 const button=g2part(sp.rows.find(r=>r.id==='r2').p.acao[0],v);
 EXTRAVALS(self,v); button.fn();
 assert.ok(self.state.g2?.g_co?.fm,'ação montada deve abrir o formulário');
 Object.assign(self.state.g2.g_co.fm.draft,{tema:'Contato na região',resp,prazo:'2026-10-30'});
 return {self,v};
}
for(const resp of ['Marta Nunes','Diego Prado']) check('grava membro ativo: '+resp,()=>{
 const {self,v}=setup(resp); const before=JSON.stringify(sp.rows); g2save(self,sp);
 assert.equal(self.state.g2.g_co.fm,null); const r=g2find(g2rows(self,sp),'r2');
 assert.equal(r.v.resp,resp); assert.equal(r.v.tema,'Contato na região'); assert.equal(r.v.prazo,'2026-10-30');
 assert.equal(r.v.reg,'Fertilizantes e corretivos · Triângulo MG'); assert.equal(r.v.org,'F01');
 assert.equal(r.p.acao[0].t,'Revisar ação interna'); assert.match(self.state.g2toast,/demonstração/);
 assert.equal(JSON.stringify(sp.rows),before); v.pt06_acao(); assert.equal(self.state.g2.g_co.fm.draft.resp,resp);
});
for(const resp of ['Ana Lima','Marcos Silva','Rui Santos','Paula Costa','Sônia Reis','Pessoa inexistente'])
 check('recusa sem perder rascunho: '+resp,()=>{
  const {self}=setup(resp); const draft=JSON.stringify(self.state.g2.g_co.fm.draft); const rows=JSON.stringify(g2rows(self,sp));
  g2save(self,sp); assert.match(self.state.g2.g_co.fm.errs.resp,/ativa da Fertisul/);
  assert.equal(JSON.stringify(self.state.g2.g_co.fm.draft),draft); assert.equal(JSON.stringify(g2rows(self,sp)),rows);
  assert.equal(self.state.g2toast,undefined);
 });
check('organização divergente é recusada',()=>{
 const {self}=setup(); const rows=g2clone(sp.rows); g2find(rows,'r2').v.org='OUTRA'; g2set(self,sp.id,{rows});
 g2save(self,sp); assert.match(self.state.g2.g_co.fm.errs.resp,/pertencer à Fertisul/); assert.equal(g2find(g2rows(self,sp),'r2').v.resp,'');
});
check('inelegibilidade após abertura é revalidada',()=>{
 const {self}=setup(); const u=PT06_USUARIOS.find(u=>u.nome==='Diego Prado'); u.ativo=false;
 try { g2save(self,sp); assert.match(self.state.g2.g_co.fm.errs.resp,/ativa da Fertisul/); }
 finally {u.ativo=true;}
});
check('campos obrigatórios e correção preservam contexto',()=>{
 const {self}=setup(''); self.state.g2.g_co.fm.draft.tema=''; g2save(self,sp);
 assert.ok(self.state.g2.g_co.fm.errs.resp); assert.ok(self.state.g2.g_co.fm.errs.tema);
 assert.equal(self.state.g2.g_co.fm.draft.prazo,'2026-10-30');
 Object.assign(self.state.g2.g_co.fm.draft,{resp:'Marta Nunes',tema:'Acompanhar cobertura'}); g2save(self,sp);
 assert.equal(self.state.g2.g_co.fm,null); assert.equal(g2find(g2rows(self,sp),'r2').v.tema,'Acompanhar cobertura');
});
check('fechar rascunho solicita confirmação',()=>{
 const {self}=setup(); g2close(self,sp); assert.equal(self.state.g2.g_co.fm.warn,true);
 assert.equal(self.state.g2.g_co.fm.draft.tema,'Contato na região');
});
check('região sem ação segue consulta',()=>{
 const {self}=setup(); g2open(self,sp,'r1'); assert.equal(self.state.g2.g_co.fm.ro,true);
 assert.deepEqual(sp.edit.fields.filter(f=>g2cond(f,self.state.g2.g_co.fm.draft)).map(f=>f.k),['reg']);
 assert.match(self.g2formSub('g_co',g2find(sp.rows,'r1')),/consulte a origem/);
 assert.deepEqual(pt06Check('g_fu',[],null,{}),{});
});
console.log(passed+'/'+passed+' cenários do motor; esquema PT06/PT07 validado em Python.');
"""
script = 'const GRIDS='+json.dumps(grids, ensure_ascii=False)+';\n'+Path(__file__).with_name('g2lib.js').read_text()+'\n'+hooks+'\n'+checks
subprocess.run([os.environ.get('NODE', 'node'), '-'], input=script, text=True, check=True)
