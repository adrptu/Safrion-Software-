# -*- coding: utf-8 -*-
"""NAV-1 · regras dos Planos agronômicos (PA), sem navegador: monta o JS real da tela (areas/processo_planos.py: PA0 + JS) no node
e confere as regras puras que a tela usa (docs/navegacao/ESPECIFICACAO.md):
  U1 endereço #plano=<id> (lido ao carregar e no hashchange; vazio ou inexistente = lista)
  U2 rascunho v(n+1) na 1ª mudança, a versão publicada não muda; U3 a 2ª mudança fica no mesmo rascunho
  U4 diferenças vN × vM (dose, inclusão, exclusão, gatilho)
  U5 Próximo passo: sem rascunho nenhuma primária; com rascunho "Publicar versão vN"; desabilitado com motivo sem atividade
     e com a inclusão de insumo aberta
  U6 publicar cria a vN, põe no histórico e não muda os cultivos; U7 recusa sem rascunho e com rascunho vazio
  U8 situação do cultivo (X-AGR-6): chip "Na vN · vM publicada" e link ao cultivo no Planejar safra (#saf&passo=cultivos&cult)
  U9 novo plano: nome obrigatório e único por cultura; U10 copiar de uma base só traz as atividades; U11 descartar
Uso (de gen37/): python3 pa_regras_test.py   (sai 1 se algum caso falhar)
Reprodução na base: GEN=<gen37 da base> python3 pa_regras_test.py (as funções que não existem lá contam como falha)."""
import os, sys, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); GEN = os.environ.get('GEN') or HERE
sys.path.insert(0, GEN); os.chdir(GEN)
import areas.processo_planos as P
src = ('const PA0 = ' + json.dumps(P._dados(), ensure_ascii=False) + ';\n' + P.JS + r'''
const R=[]; const ok=(n,c,info)=>{ R.push(!!c); console.log((c?'OK    ':'FALHA ')+n+(c?'':' · '+JSON.stringify(info===undefined?null:info).slice(0,500))); };
const tem=(...fs)=>fs.every(f=>{ try{ return eval('typeof '+f)==='function'; }catch(e){ return false; } });
const caso=(n,fs,f)=>{ if(!tem(...fs)){ ok(n,false,'sem '+fs.join(', ')); return; } try{ f(); }catch(e){ ok(n,false,'erro: '+e.message); } };
const ps0=PA_BASE; const soja=()=>ps0.find(p=>p.id==='SOJA-AT');
const doseFung=(ps,v)=>paRascNo(ps,'SOJA-AT',soja().atividades.find(a=>a.nome==='Fungicida 1ª aplicação').id,(a)=>{ a.prods.find(x=>x.prod==='Fungicida A').dose=v; });
caso('U1 endereço: #plano=SOJA-AT → SOJA-AT; com outro parâmetro antes; codificado; vazio, sem plano= ou só "#plano=" → lista',['paHashId'],()=>{
  const r=[paHashId('#plano=SOJA-AT'),paHashId('#x=1&plano=MILHO-SF'),paHashId('#plano=Soja%20teste'),paHashId(''),paHashId('#saf=S2627'),paHashId('#plano=')];
  ok('U1 endereço: #plano=SOJA-AT → SOJA-AT; com outro parâmetro antes; codificado; vazio, sem plano= ou só "#plano=" → lista', JSON.stringify(r)===JSON.stringify(['SOJA-AT','MILHO-SF','Soja teste','','','']), r); });
caso('U2 1ª mudança de dose na v6 cria o rascunho v7; a v6 publicada e a fonte não mudam',['paRascNo'],()=>{
  const r=doseFung(ps0,0.6); const p=r.ps.find(x=>x.id==='SOJA-AT'); const a6=p.atividades.find(a=>a.nome==='Fungicida 1ª aplicação').prods.find(x=>x.prod==='Fungicida A').dose;
  const a7=p.rasc.atividades.find(a=>a.nome==='Fungicida 1ª aplicação').prods.find(x=>x.prod==='Fungicida A').dose;
  ok('U2 1ª mudança de dose na v6 cria o rascunho v7; a v6 publicada e a fonte não mudam', r.novo&&r.v===7&&p.versao===6&&a6===0.5&&a7===0.6&&!soja().rasc&&/Rascunho v7 criado; a v6 publicada e os 5 cultivos que usam o plano não mudam/.test(r.fim), [r.novo,r.v,p.versao,a6,a7,r.fim]); });
caso('U3 a 2ª mudança fica no mesmo rascunho v7',['paRascNo'],()=>{
  const r1=doseFung(ps0,0.6); const r2=paRascNo(r1.ps,'SOJA-AT',soja().atividades[0].id,(a)=>{ a.prods[0].dose=2.5; });
  ok('U3 a 2ª mudança fica no mesmo rascunho v7', !r2.novo&&r2.v===7&&/Gravado no rascunho v7/.test(r2.fim), [r2.novo,r2.v,r2.fim]); });
caso('U4 diferenças v7 × v6: dose alterada, insumo incluído, atividade excluída e gatilho mudado',['paRascNo','paDiff'],()=>{
  let r=doseFung(ps0,0.6); const atv=soja().atividades; const herb=atv.find(a=>a.nome==='Herbicida pós-emergente'); const des=atv.find(a=>a.nome==='Dessecação pré-plantio');
  r=paRascNo(r.ps,'SOJA-AT',atv.find(a=>a.nome==='Fungicida 1ª aplicação').id,(a)=>{ a.prods.push({grupo:'Inseticidas',prod:'Inseticida B',dose:0.2,un:'L',preco:90}); });
  const ps=paClone(r.ps); const p=ps.find(x=>x.id==='SOJA-AT'); p.rasc.atividades=p.rasc.atividades.filter(a=>a.id!==herb.id); p.rasc.atividades.find(a=>a.id===des.id).g={tipo:'DAP',dias:-25,data:null};
  const d=paDiff(p); const t=d.map(x=>x.k+': '+x.n+' · '+x.t).join(' | ');
  ok('U4 diferenças v7 × v6: dose alterada, insumo incluído, atividade excluída e gatilho mudado', /Alterada: Fungicida 1ª aplicação · Fungicida A: 0,5 → 0,6 L\/ha · inclui Inseticida B 0,2 L\/ha/.test(t)&&/Excluída: Herbicida pós-emergente/.test(t)&&/gatilho: DAP −20 → DAP −25/.test(t), t); });
caso('U5 Próximo passo: sem rascunho nenhuma primária; com rascunho "Publicar versão v7"; sem atividade ou com a inclusão de insumo aberta, desabilitado com o motivo',['paAcoes','paRascNo'],()=>{
  const sem=paAcoes(soja()); const p7=doseFung(ps0,0.6).ps.find(x=>x.id==='SOJA-AT'); const com=paAcoes(p7); const ab=paAcoes(p7,{iadd:true});
  const vaz=paClone(p7); vaz.rasc.atividades=[]; const zv=paAcoes(vaz);
  ok('U5 Próximo passo: sem rascunho nenhuma primária; com rascunho "Publicar versão v7"; sem atividade ou com a inclusão de insumo aberta, desabilitado com o motivo',
     sem.prim===null&&com.prim.t==='Publicar versão v7'&&!com.prim.dis&&!com.nota&&zv.prim.dis==='Inclua ao menos uma atividade para publicar a v7.'&&zv.nota===zv.prim.dis
     &&ab.prim.dis==='Conclua ou cancele a inclusão do insumo para publicar a v7.', [sem,com,zv,ab]); });
caso('U6 publicar cria a v7 (em vigor, no histórico com a data de hoje) e não muda nenhum cultivo',['paPubFaz','paRascNo'],()=>{
  const antes=JSON.stringify(PA0.cultivos); const r=paPubFaz(doseFung(ps0,0.6).ps,'SOJA-AT',PA0.hoje); const p=r.p;
  const d=p.atividades.find(a=>a.nome==='Fungicida 1ª aplicação').prods.find(x=>x.prod==='Fungicida A').dose;
  ok('U6 publicar cria a v7 (em vigor, no histórico com a data de hoje) e não muda nenhum cultivo', !r.erro&&p.versao===7&&p.rasc===null&&d===0.6&&p.hist[0].v===7&&p.hist[0].at===PA0.hoje&&p.hist[1].v===6
     &&JSON.stringify(PA0.cultivos)===antes&&PA0.cultivos.filter(c=>c.plano==='SOJA-AT').map(c=>c.ver).join(',')==='6,6,6,5,5', [r.erro,p&&p.versao,p&&p.hist]); });
caso('U7 publicar recusa sem rascunho e com o rascunho sem atividade',['paPubFaz'],()=>{
  const a=paPubFaz(ps0,'SOJA-AT',PA0.hoje); const ps=paClone(ps0); const p=ps.find(x=>x.id==='SOJA-PD'); p.rasc={v:4,atividades:[]}; const b=paPubFaz(ps,'SOJA-PD',PA0.hoje);
  ok('U7 publicar recusa sem rascunho e com o rascunho sem atividade', a.erro==='Sem rascunho para publicar.'&&b.erro==='Inclua ao menos uma atividade para publicar a v4.', [a.erro,b.erro]); });
caso('U8 situação do cultivo (X-AGR-6): em vigor; com rascunho "Continua na v6 ao publicar"; depois de publicar "Na v6 · v7 publicada" com o link ao cultivo no Planejar safra; safra encerrada sem link',['paSitCult','paPubFaz','paRascNo'],()=>{
  const c1=PA0.cultivos.find(c=>c.id==='c1'), e1=PA0.cultivos.find(c=>c.id==='e1'); const p6=soja(); const p7r=doseFung(ps0,0.6).ps.find(x=>x.id==='SOJA-AT'); const p7=paPubFaz(doseFung(ps0,0.6).ps,'SOJA-AT',PA0.hoje).p;
  const a=paSitCult(c1,p6), b=paSitCult(c1,p7r), c=paSitCult(c1,p7), d=paSitCult(e1,p7);
  ok('U8 situação do cultivo (X-AGR-6): em vigor; com rascunho "Continua na v6 ao publicar"; depois de publicar "Na v6 · v7 publicada" com o link ao cultivo no Planejar safra; safra encerrada sem link',
     a.length===1&&a[0].t==='Na versão em vigor'&&b.length===1&&b[0].t==='Continua na v6 ao publicar'&&c[0].t==='Na v6 · v7 publicada'&&c[0].c==='yellow'
     &&c[1]&&c[1].k==='link'&&c[1].t==='Abrir cultivo no Planejar safra ›'&&c[1].h==='SAF.dc.html#saf=S2627&passo=cultivos&cult=c1'&&d.length===1&&d[0].t==='Safra encerrada · fica na v5', [a,b,c,d]); });
caso('U9 novo plano: nome obrigatório; repetido na mesma cultura recusado (sem diferenciar maiúsculas); o mesmo nome em outra cultura passa; cultura obrigatória',['paNovoErro'],()=>{
  const a=paNovoErro(ps0,{nome:'  ',cultura:'Soja'}), b=paNovoErro(ps0,{nome:'soja ALTA tecnologia',cultura:'Soja'}), c=paNovoErro(ps0,{nome:'Soja alta tecnologia',cultura:'Milho'}), d=paNovoErro(ps0,{nome:'X',cultura:''});
  ok('U9 novo plano: nome obrigatório; repetido na mesma cultura recusado (sem diferenciar maiúsculas); o mesmo nome em outra cultura passa; cultura obrigatória',
     a.nome==='Informe o nome do plano.'&&b.nome==='Já existe um plano com este nome nesta cultura.'&&!Object.keys(c).length&&d.cultura==='Escolha a cultura.', [a,b,c,d]); });
caso('U10 novo plano copiando de uma base: rascunho v1 com as atividades da versão publicada da base, ids novos, base intacta',['paNovoFaz'],()=>{
  const r=paNovoFaz(ps0,{nome:'Soja teste',cultura:'Soja',base:'SOJA-PD'},'NPx'); const n=r.ps.find(p=>p.id==='NPx'); const b=r.ps.find(p=>p.id==='SOJA-PD');
  ok('U10 novo plano copiando de uma base: rascunho v1 com as atividades da versão publicada da base, ids novos, base intacta',
     n.versao===0&&n.rasc.v===1&&n.rasc.atividades.length===b.atividades.length&&n.rasc.atividades.every(a=>a.id.startsWith('NPx_'))&&b.atividades.every(a=>!a.id.startsWith('NPx_'))&&!b.rasc&&r.ps.length===ps0.length+1, [n.rasc.atividades.length,b.atividades.length]); });
caso('U11 descartar: plano novo sai da biblioteca; plano publicado perde só o rascunho e segue na v6',['paDescartaNo','paNovoFaz','paRascNo'],()=>{
  const r=paNovoFaz(ps0,{nome:'Soja teste',cultura:'Soja',base:''},'NPy'); const a=paDescartaNo(r.ps,'NPy'); const b=paDescartaNo(doseFung(ps0,0.6).ps,'SOJA-AT');
  const pb=b.ps.find(p=>p.id==='SOJA-AT');
  ok('U11 descartar: plano novo sai da biblioteca; plano publicado perde só o rascunho e segue na v6', a.saiu&&!a.ps.some(p=>p.id==='NPy')&&!b.saiu&&pb.rasc===null&&pb.versao===6&&b.msg==='Rascunho v7 descartado. A v6 publicada continua valendo.', [a.msg,b.msg]); });
const nf=R.filter(x=>!x).length; console.log('RESULTADO '+(R.length-nf)+'/'+R.length); if(nf) process.exitCode=1;
''')
f = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); f.write(src); f.close()
try:
    r = subprocess.run(['node', f.name], capture_output=True, text=True, timeout=120)
finally:
    os.unlink(f.name)
print(r.stdout.strip()); print(r.stderr.strip()[-2000:]) if r.stderr.strip() else None
lin = r.stdout.splitlines(); n = sum(1 for l in lin if l.startswith(('OK ', 'FALHA '))); fa = sum(1 for l in lin if l.startswith('FALHA '))
sys.exit(0 if r.returncode == 0 and n == 11 and not fa else 1)
