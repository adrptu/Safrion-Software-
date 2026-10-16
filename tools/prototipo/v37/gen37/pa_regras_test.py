# -*- coding: utf-8 -*-
"""NAV-1 · regras dos Planos agronômicos (PA), sem navegador: monta o JS real da tela (areas/processo_planos.py: PA0 + JS) no node
e confere as regras puras que a tela usa (docs/navegacao/ESPECIFICACAO.md):
  U1 endereço #plano=<id> (lido ao carregar e no hashchange; vazio ou inexistente = lista)
  U2 rascunho v(n+1) na 1ª mudança, a versão publicada não muda; U3 a 2ª mudança fica no mesmo rascunho
  U4 diferenças vN × vM (dose, inclusão, retirada de insumo, exclusão, gatilho)
  U5 Próximo passo: sem rascunho nenhuma primária; com rascunho "Salvar alterações" (14/10, proprietário) sem nota;
     desabilitado com motivo sem atividade, com a dose em edição (R1/R2), com a inclusão de insumo aberta e com o rascunho igual (R3)
  U6 publicar cria a vN, põe no histórico e não muda os cultivos; U7 recusa sem rascunho, com rascunho vazio e com rascunho igual (R3)
  U8 situação do cultivo (X-AGR-6): chip "Na vN · vM publicada" e link ao cultivo no Planejar safra (#saf&passo=cultivos&cult) nas
     três safras abertas (S2627, S27SF e LG2627)
  U9 novo plano: nome obrigatório e único por cultura; U10 copiar de uma base só traz as atividades da versão publicada (não o
     rascunho dela); U11 descartar
  U12 resumo das alterações na nota (até 2 e "e mais N"; plano novo)
  U13 dose na tabela: 0, vazio, "−2" e "-2" recusados sem rascunho; a saída do campo marca a hora da gravação (R1)
  U14 "Publicar" recusa o clique que começou com o botão desabilitado ou logo depois de a saída do campo gravar a dose (R1); com a
     dose em edição não publica (R2); depois, publica (aviso curto "Plano salvo · v7 …", 15/10: "caixa pequena, pouco texto"; o oráculo
     antigo esperava o resumo das doses, que saiu do aviso)
  U15 sair do detalhe com a dose ou a inclusão digitadas avisa e não troca de plano (R8); vazio sai direto
  U16 o painel da atividade só grava no plano e na atividade em que foi aberto (R4); U17 salvar sem mudança não cria rascunho (R3)
Uso (de gen37/): python3 pa_regras_test.py   (sai 1 se algum caso falhar)
Reprodução na base: GEN=<gen37 da base> python3 pa_regras_test.py (as funções que não existem lá contam como falha)."""
import os, sys, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); GEN = os.environ.get('GEN') or HERE
sys.path.insert(0, GEN); os.chdir(GEN)
import areas.processo_planos as P
G2LIB = open(os.path.join(GEN, 'g2lib.js'), encoding='utf-8').read()   # g2num (paNum) e g2etapa (paOpen), como na tela
src = (G2LIB + '\n/* foco e rolagem da tela (paFoco) sem DOM no node: nada a focar */ globalThis.document={getElementById:()=>null,querySelector:()=>null,querySelectorAll:()=>[]};\nconst PA0 = ' + json.dumps(P._dados(), ensure_ascii=False) + ';\n' + P.JS + r'''
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
caso('U4 diferenças v7 × v6: dose alterada, insumo incluído, insumo retirado, atividade excluída e gatilho mudado',['paRascNo','paDiff'],()=>{
  let r=doseFung(ps0,0.6); const atv=soja().atividades; const herb=atv.find(a=>a.nome==='Herbicida pós-emergente'); const des=atv.find(a=>a.nome==='Dessecação pré-plantio');
  r=paRascNo(r.ps,'SOJA-AT',atv.find(a=>a.nome==='Fungicida 1ª aplicação').id,(a)=>{ a.prods.push({grupo:'Inseticidas',prod:'Inseticida B',dose:0.2,un:'L',preco:90}); });
  const ps=paClone(r.ps); const p=ps.find(x=>x.id==='SOJA-AT'); p.rasc.atividades=p.rasc.atividades.filter(a=>a.id!==herb.id); const dr=p.rasc.atividades.find(a=>a.id===des.id); dr.g={tipo:'DAP',dias:-25,data:null};
  const tirado=dr.prods[0].prod; dr.prods=dr.prods.slice(1);
  const d=paDiff(p); const t=d.map(x=>x.k+': '+x.n+' · '+x.t).join(' | ');
  ok('U4 diferenças v7 × v6: dose alterada, insumo incluído, insumo retirado, atividade excluída e gatilho mudado', /Alterada: Fungicida 1ª aplicação · Fungicida A: 0,5 → 0,6 L\/ha · inclui Inseticida B 0,2 L\/ha/.test(t)&&/Excluída: Herbicida pós-emergente/.test(t)&&/gatilho: DAP −20 → DAP −25/.test(t)
     &&t.includes('Alterada: Dessecação pré-plantio · gatilho: DAP −20 → DAP −25 · retira '+tirado), t); });
const U5='U5 Próximo passo: sem rascunho nenhuma primária; com rascunho "Salvar alterações", sem nota (o resumo vai no aviso ao salvar); desabilitado com o motivo sem atividade, com a dose em edição (R1/R2), com a inclusão aberta e com o rascunho igual à v6 (R3)';
caso(U5,['paAcoes','paRascNo','paResumo'],()=>{
  const sem=paAcoes(soja()); const p7=doseFung(ps0,0.6).ps.find(x=>x.id==='SOJA-AT'); const com=paAcoes(p7); const ab=paAcoes(p7,{iadd:true}); const ed=paAcoes(p7,{ied:{aid:'x',prod:'Glifosato 480',val:'6'}});
  const vaz=paClone(p7); vaz.rasc.atividades=[]; const zv=paAcoes(vaz);
  const igual=paAcoes(doseFung(doseFung(ps0,0.6).ps,0.5).ps.find(x=>x.id==='SOJA-AT'));
  ok(U5, sem.prim===null&&com.prim.t==='Salvar alterações'&&!com.prim.dis&&com.nota===''&&paResumo(p7)==='1 alteração na v7: Fungicida 1ª aplicação (Fungicida A: 0,5 → 0,6 L/ha).'
     &&zv.prim.dis==='Inclua ao menos uma atividade para salvar.'&&zv.nota===zv.prim.dis
     &&ab.prim.dis==='Conclua ou cancele a inclusão do insumo para salvar.'
     &&ed.prim.dis==='Confirme (Enter) ou cancele (Esc) a dose de Glifosato 480 para salvar.'&&ed.nota===ed.prim.dis
     &&igual.prim.dis==='O rascunho v7 está igual à v6: altere algo ou descarte o rascunho.', [sem,com,zv,ab,ed,igual]); });
caso('U6 publicar cria a v7 (em vigor, no histórico com a data de hoje) e não muda nenhum cultivo',['paPubFaz','paRascNo'],()=>{
  const antes=JSON.stringify(PA0.cultivos); const r=paPubFaz(doseFung(ps0,0.6).ps,'SOJA-AT',PA0.hoje); const p=r.p;
  const d=p.atividades.find(a=>a.nome==='Fungicida 1ª aplicação').prods.find(x=>x.prod==='Fungicida A').dose;
  ok('U6 publicar cria a v7 (em vigor, no histórico com a data de hoje) e não muda nenhum cultivo', !r.erro&&p.versao===7&&p.rasc===null&&d===0.6&&p.hist[0].v===7&&p.hist[0].at===PA0.hoje&&p.hist[1].v===6
     &&JSON.stringify(PA0.cultivos)===antes&&PA0.cultivos.filter(c=>c.plano==='SOJA-AT').map(c=>c.ver).join(',')==='6,6,6,5,5', [r.erro,p&&p.versao,p&&p.hist]); });
caso('U7 publicar recusa sem rascunho, com o rascunho sem atividade e com o rascunho igual à versão publicada (R3: nenhuma v7 vazia, nenhum cultivo marcado)',['paPubFaz'],()=>{
  const a=paPubFaz(ps0,'SOJA-AT',PA0.hoje); const ps=paClone(ps0); const p=ps.find(x=>x.id==='SOJA-PD'); p.rasc={v:4,atividades:[]}; const b=paPubFaz(ps,'SOJA-PD',PA0.hoje);
  const ig=doseFung(doseFung(ps0,0.6).ps,0.5).ps; const c=paPubFaz(ig,'SOJA-AT',PA0.hoje);
  ok('U7 publicar recusa sem rascunho, com o rascunho sem atividade e com o rascunho igual à versão publicada (R3: nenhuma v7 vazia, nenhum cultivo marcado)',
     a.erro==='Sem rascunho para publicar.'&&b.erro==='Inclua ao menos uma atividade para salvar.'&&c.erro==='O rascunho v7 está igual à v6: altere algo ou descarte o rascunho.'&&!c.ps, [a.erro,b.erro,c.erro]); });
caso('U8 situação do cultivo (X-AGR-6): em vigor; com rascunho "Continua na v6 ao publicar"; depois de publicar "Na v6 · v7 publicada" com o link ao cultivo no Planejar safra; safra encerrada sem link',['paSitCult','paPubFaz','paRascNo'],()=>{
  const c1=PA0.cultivos.find(c=>c.id==='c1'), e1=PA0.cultivos.find(c=>c.id==='e1'); const p6=soja(); const p7r=doseFung(ps0,0.6).ps.find(x=>x.id==='SOJA-AT'); const p7=paPubFaz(doseFung(ps0,0.6).ps,'SOJA-AT',PA0.hoje).p;
  const a=paSitCult(c1,p6), b=paSitCult(c1,p7r), c=paSitCult(c1,p7), d=paSitCult(e1,p7);
  ok('U8 situação do cultivo (X-AGR-6): em vigor; com rascunho "Continua na v6 ao publicar"; depois de publicar "Na v6 · v7 publicada" com o link ao cultivo no Planejar safra; safra encerrada sem link',
     a.length===1&&a[0].t==='Na versão em vigor'&&b.length===1&&b[0].t==='Continua na v6 ao publicar'&&c[0].t==='Na v6 · v7 publicada'&&c[0].c==='yellow'
     &&c[1]&&c[1].k==='link'&&c[1].t==='Abrir cultivo no Planejar safra ›'&&c[1].h==='SAF.dc.html#saf=S2627&passo=cultivos&cult=c1'&&d.length===1&&d[0].t==='Safra encerrada · fica na v5', [a,b,c,d]); });
// muda o plano (1ª dose da 1ª atividade com insumo; sem insumo, o nome) e publica: a vN+1 para conferir o link dos cultivos
const pubMuda=(pid)=>{ const p=ps0.find(x=>x.id===pid); const a0=p.atividades.find(a=>a.prods.length)||p.atividades[0];
  const r=paRascNo(ps0,pid,a0.id,(a)=>{ if(a.prods.length) a.prods[0].dose=Number(a.prods[0].dose)+1; else a.nome=a.nome+' (revisada)'; }); return paPubFaz(r.ps,pid,PA0.hoje).p; };
caso('U8b o link do cultivo leva a safra e o cultivo de cada um nas três safras abertas: S27SF (d1, Milho safrinha) e LG2627 (lg01, Lagoa Grande)',['paSitCult','paPubFaz','paRascNo'],()=>{
  const d1=PA0.cultivos.find(c=>c.id==='d1'), lg=PA0.cultivos.find(c=>c.id==='lg01');
  const a=paSitCult(d1,pubMuda(d1.plano)), b=paSitCult(lg,pubMuda(lg.plano));
  ok('U8b o link do cultivo leva a safra e o cultivo de cada um nas três safras abertas: S27SF (d1, Milho safrinha) e LG2627 (lg01, Lagoa Grande)',
     a[1]&&a[1].h==='SAF.dc.html#saf=S27SF&passo=cultivos&cult=d1'&&b[1]&&b[1].h==='SAF.dc.html#saf=LG2627&passo=cultivos&cult=lg01'&&/^Na v\d+ · v\d+ publicada$/.test(a[0].t)&&/^Na v1 · v2 publicada$/.test(b[0].t), [a,b]); });
caso('U9 novo plano: nome obrigatório; repetido na mesma cultura recusado (sem diferenciar maiúsculas); o mesmo nome em outra cultura passa; cultura obrigatória',['paNovoErro'],()=>{
  const a=paNovoErro(ps0,{nome:'  ',cultura:'Soja'}), b=paNovoErro(ps0,{nome:'soja ALTA tecnologia',cultura:'Soja'}), c=paNovoErro(ps0,{nome:'Soja alta tecnologia',cultura:'Milho'}), d=paNovoErro(ps0,{nome:'X',cultura:''});
  ok('U9 novo plano: nome obrigatório; repetido na mesma cultura recusado (sem diferenciar maiúsculas); o mesmo nome em outra cultura passa; cultura obrigatória',
     a.nome==='Informe o nome do plano.'&&b.nome==='Já existe um plano com este nome nesta cultura.'&&!Object.keys(c).length&&d.cultura==='Escolha a cultura.', [a,b,c,d]); });
caso('U10 novo plano copiando de uma base: rascunho v1 com as atividades da versão publicada da base (mesmo com a base em rascunho), ids novos, base intacta',['paNovoFaz','paRascNo'],()=>{
  const r=paNovoFaz(ps0,{nome:'Soja teste',cultura:'Soja',base:'SOJA-PD'},'NPx'); const n=r.ps.find(p=>p.id==='NPx'); const b=r.ps.find(p=>p.id==='SOJA-PD');
  /* base com rascunho: a Soja alta tecnologia com o Fungicida A em 0,6 no rascunho v7; a cópia leva a v6 publicada (0,5) */
  const bR=doseFung(ps0,0.6).ps; const r2=paNovoFaz(bR,{nome:'Soja cópia',cultura:'Soja',base:'SOJA-AT'},'NPz'); const n2=r2.ps.find(p=>p.id==='NPz');
  const fA=(atvs)=>atvs.find(a=>a.nome==='Fungicida 1ª aplicação').prods.find(x=>x.prod==='Fungicida A').dose; const b2=r2.ps.find(p=>p.id==='SOJA-AT');
  ok('U10 novo plano copiando de uma base: rascunho v1 com as atividades da versão publicada da base (mesmo com a base em rascunho), ids novos, base intacta',
     n.versao===0&&n.rasc.v===1&&n.rasc.atividades.length===b.atividades.length&&n.rasc.atividades.every(a=>a.id.startsWith('NPx_'))&&b.atividades.every(a=>!a.id.startsWith('NPx_'))&&!b.rasc&&r.ps.length===ps0.length+1
     &&fA(n2.rasc.atividades)===0.5&&fA(b2.rasc.atividades)===0.6&&b2.rasc.v===7, [n.rasc.atividades.length,b.atividades.length,fA(n2.rasc.atividades)]); });
caso('U11 descartar: plano novo sai da biblioteca; plano publicado perde só o rascunho e segue na v6',['paDescartaNo','paNovoFaz','paRascNo'],()=>{
  const r=paNovoFaz(ps0,{nome:'Soja teste',cultura:'Soja',base:''},'NPy'); const a=paDescartaNo(r.ps,'NPy'); const b=paDescartaNo(doseFung(ps0,0.6).ps,'SOJA-AT');
  const pb=b.ps.find(p=>p.id==='SOJA-AT');
  ok('U11 descartar: plano novo sai da biblioteca; plano publicado perde só o rascunho e segue na v6', a.saiu&&!a.ps.some(p=>p.id==='NPy')&&!b.saiu&&pb.rasc===null&&pb.versao===6&&b.msg==='Rascunho v7 descartado. A v6 publicada continua valendo.', [a.msg,b.msg]); });
// tela de mentira para as regras que gravam no estado (o setState da tela grava na hora, como o __setLogicState do runtime)
const tela=(st)=>({state:Object.assign({},st),setState(o){ Object.assign(this.state,o); }});
const fungId=()=>soja().atividades.find(a=>a.nome==='Fungicida 1ª aplicação').id;
caso('U12 resumo na nota: 1 alteração; 3 alterações com "e mais 1"; plano novo "A v1 publica N atividades"',['paResumo','paRascNo','paNovoFaz'],()=>{
  const p1=doseFung(ps0,0.6).ps.find(x=>x.id==='SOJA-AT'); const atv=soja().atividades;
  let r=doseFung(ps0,0.6); r=paRascNo(r.ps,'SOJA-AT',atv.find(a=>a.nome==='Herbicida pós-emergente').id,(a)=>{ a.prods[0].dose=Number(a.prods[0].dose)+1; });
  const ps=paClone(r.ps); const p3=ps.find(x=>x.id==='SOJA-AT'); p3.rasc.atividades=p3.rasc.atividades.filter(a=>a.nome!=='Dessecação pré-plantio');
  const nv=paNovoFaz(ps0,{nome:'Soja nova',cultura:'Soja',base:'SOJA-PD'},'NPr').ps.find(p=>p.id==='NPr');
  const a=paResumo(p1), b=paResumo(p3), c=paResumo(nv);
  ok('U12 resumo na nota: 1 alteração; 3 alterações com "e mais 1"; plano novo "A v1 publica N atividades"',
     a==='1 alteração na v7: Fungicida 1ª aplicação (Fungicida A: 0,5 → 0,6 L/ha).'&&/^3 alterações na v7: .+; .+; e mais 1\.$/.test(b)&&b.includes('Fungicida A: 0,5 → 0,6 L/ha')&&/^A v1 publica \d+ atividades\.$/.test(c)&&paResumo(soja())==='', [a,b,c]); });
caso('U13 dose na tabela: 0, vazio, "−2" (menos tipográfico) e "-2" recusados sem criar rascunho; 0,6 grava; a saída do campo marca a hora e o que mudou (R1)',['paDoseOk','paNum'],()=>{
  const rec=['0','','−2','-2','abc'].map(val=>{ const t=tela({pid:'SOJA-AT',ied:{aid:fungId(),prod:'Fungicida A',val,err:''}}); paDoseOk(t);
    return {val,err:t.state.ied&&t.state.ied.err,rasc:!!(t.state.pl&&t.state.pl.find(p=>p.id==='SOJA-AT').rasc)}; });
  const t=tela({pid:'SOJA-AT',ied:{aid:fungId(),prod:'Fungicida A',val:'0,6',err:''}}); paDoseOk(t);
  const e=tela({pid:'SOJA-AT',ied:{aid:fungId(),prod:'Fungicida A',val:'0,6',err:''}}); const t0=Date.now(); paDoseOk(e,{sai:true});
  ok('U13 dose na tabela: 0, vazio, "−2" (menos tipográfico) e "-2" recusados sem criar rascunho; 0,6 grava; a saída do campo marca a hora e o que mudou (R1)',
     rec.every(x=>x.err==='Informe a dose por hectare, maior que zero.'&&!x.rasc)&&t.state.ied===null&&t.state.pl.find(p=>p.id==='SOJA-AT').rasc.v===7&&!t.__paSaiT
     &&e.__paSaiT>=t0&&e.__paSaiTxt==='Fungicida A: 0,5 → 0,6 L/ha', [rec,t.__paSaiT,e.__paSaiTxt]); });
caso('U14 Publicar: recusa o clique que começou com o botão desabilitado e o que vem logo depois de a saída do campo gravar a dose (R1); com a dose em edição não publica (R2); depois publica a v7',['paPub','paPubAgora'],()=>{
  const pl=doseFung(ps0,0.6).ps; const v=(t)=>t.state.pl.find(p=>p.id==='SOJA-AT').versao;
  const a=tela({pid:'SOJA-AT',pl}); a.__paPubDis=true; paPub(a); const a1=[v(a),a.state.g2toast]; paPub(a); const a2=[v(a),a.state.g2toast];
  const b=tela({pid:'SOJA-AT',pl}); b.__paSaiT=Date.now(); b.__paSaiTxt='Glifosato 480: 2 → 6 L/ha'; paPub(b); const b1=[v(b),b.state.g2toast];
  const c=tela({pid:'SOJA-AT',pl}); c.__paSaiT=Date.now()-PA_SAI_MS-5; paPub(c); const c1=v(c);
  const d=tela({pid:'SOJA-AT',pl,ied:{aid:fungId(),prod:'Fungicida A',val:'0',err:''}}); paPub(d); const d1=[v(d),d.state.g2toast];
  ok('U14 Publicar: recusa o clique que começou com o botão desabilitado e o que vem logo depois de a saída do campo gravar a dose (R1); com a dose em edição não publica (R2); depois publica a v7',
     a1[0]===6&&a1[1]==='O rascunho mudou neste clique: confira e clique em Salvar alterações de novo.'&&a2[0]===7&&/^Plano salvo · v7( · cultivos seguem na versão deles)?$/.test(a2[1])
     &&b1[0]===6&&b1[1]==='A dose de Glifosato 480: 2 → 6 L/ha entrou no rascunho agora: confira e clique em Salvar alterações de novo.'&&c1===7&&d1[0]===6&&!d1[1], [a1,a2,b1,c1,d1]); });
caso('U15 sair do detalhe com a dose ou a inclusão de insumo digitadas avisa e não sai (R8); inclusão em branco e dose fechada saem direto',['paPend','paSair','paSaiNao'],()=>{
  const pend=[paPend({iadd:{aid:'a',prod:'Inseticida B',dose:'',err:''}}),paPend({iadd:{aid:'a',prod:'',dose:'0,3',err:''}}),paPend({iadd:{aid:'a',prod:'',dose:' ',err:''}}),paPend({ied:{aid:'a',prod:'Fungicida A',val:'0',err:'x'}}),paPend({})];
  const t=tela({pid:'SOJA-AT',iadd:{aid:fungId(),prod:'Inseticida B',dose:'0,3',err:''}}); paSair(t,{pid:null}); const av=[t.state.pid,t.state.saiAv];
  paSaiNao(t); const nao=[t.state.pid,t.state.saiAv,!!t.state.iadd];
  const l=tela({pid:'SOJA-AT',iadd:{aid:fungId(),prod:'',dose:'',err:''}}); paSair(l,{pid:null});
  ok('U15 sair do detalhe com a dose ou a inclusão de insumo digitadas avisa e não sai (R8); inclusão em branco e dose fechada saem direto',
     JSON.stringify(pend)===JSON.stringify(['a inclusão de insumo','a inclusão de insumo','','a dose de Fungicida A',''])&&av[0]==='SOJA-AT'&&av[1]&&av[1].pid===null&&av[1].o==='a inclusão de insumo'
     &&nao[0]==='SOJA-AT'&&nao[1]===null&&nao[2]&&l.state.pid===null&&!l.state.iadd, [pend,av,nao,l.state.pid]); });
caso('U16 o painel da atividade só grava no plano e na atividade em que foi aberto (R4): plano trocado ou atividade inexistente fecham sem gravar',['paSave'],()=>{
  const d={op:'Pulverização',nome:'Dessecação pré-plantio',outra:false,tipo:'DAPA',dias:'20',data:''};
  const a=tela({pid:'MILHO-SF',fm:{pid:'SOJA-AT',aid:soja().atividades[0].id,draft:d,orig:'',errs:{},warn:false}}); paSave(a);
  const b=tela({pid:'MILHO-SF',fm:{pid:'MILHO-SF',aid:soja().atividades[0].id,draft:d,orig:'',errs:{},warn:false}}); paSave(b);
  const semR=(t)=>!t.state.pl||!t.state.pl.find(p=>p.id==='MILHO-SF').rasc;
  ok('U16 o painel da atividade só grava no plano e na atividade em que foi aberto (R4): plano trocado ou atividade inexistente fecham sem gravar',
     a.state.fm===null&&semR(a)&&a.state.g2toast==='O painel era de outro plano: nada foi gravado.'&&b.state.fm===null&&semR(b)&&b.state.g2toast==='A atividade não existe mais neste plano: nada foi gravado.', [a.state,b.state]); });
caso('U17 salvar o painel da atividade sem mudar nada não cria rascunho (R3: nenhum rascunho igual à versão publicada)',['paSave'],()=>{
  const a0=soja().atividades[0]; const d={op:a0.op,nome:a0.nome,outra:false,tipo:'DAPA',dias:String(Math.abs(a0.g.dias)),data:''};
  const t=tela({pid:'SOJA-AT',fm:{pid:'SOJA-AT',aid:a0.id,draft:d,orig:'',errs:{},warn:false}}); paSave(t);
  const u=tela({pid:'SOJA-AT',fm:{pid:'SOJA-AT',aid:a0.id,draft:Object.assign({},d,{dias:'25'}),orig:'',errs:{},warn:false}}); paSave(u);
  ok('U17 salvar o painel da atividade sem mudar nada não cria rascunho (R3: nenhum rascunho igual à versão publicada)',
     t.state.fm===null&&!t.state.pl&&t.state.g2toast==='Nada mudou em “Dessecação pré-plantio”: o plano continua como estava.'&&u.state.pl&&u.state.pl.find(p=>p.id==='SOJA-AT').rasc.v===7, [t.state.g2toast,u.state.g2toast]); });
const nf=R.filter(x=>!x).length; console.log('RESULTADO '+(R.length-nf)+'/'+R.length); if(nf) process.exitCode=1;
''')
f = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); f.write(src); f.close()
try:
    r = subprocess.run(['node', f.name], capture_output=True, text=True, timeout=120)
finally:
    os.unlink(f.name)
print(r.stdout.strip()); print(r.stderr.strip()[-2000:]) if r.stderr.strip() else None
lin = r.stdout.splitlines(); n = sum(1 for l in lin if l.startswith(('OK ', 'FALHA '))); fa = sum(1 for l in lin if l.startswith('FALHA '))
sys.exit(0 if r.returncode == 0 and n == 18 and not fa else 1)
