"""EST-1/CTL4: quarentena vencida não é suprimento recuperável por laudo."""
import os,sys,pathlib,tempfile,subprocess
os.environ.setdefault('SAFRION_DADOS','sintetico')
import cenario
base=pathlib.Path(__file__).parent
src=cenario.js_prefixo()+'\n'+(base/'cal01.js').read_text()+r'''
let fails=0;
for(const vencido of [false,true]){
 const l={prod:'P',lote:'Q',un:'L',local:'A',validade:vencido?'01/2000':'12/2099',fisico:100,quarentena:100,reservado:0};
 const c={lotes:{'P|Q':l},reqs:{},ordens:{},movs:[]},before=JSON.stringify(c);
 const est=cenEstDem(c,'F',{locFaz:{A:'F'}},[]);
 const x=Object.assign({faz:'F',saf:'S',hoje:'2026-09-26',viavel:'2026-09-26',ordem:{S:0},osd:[],occ:[{k:'K',saf:'S',tal:'T',local:'T',nome:'Aplicar',area:1,dt:'2026-09-27',prods:[{nome:'P',dose:10,q:10,un:'L',preco:1}]}]},est);
 const d=demFazenda(x).P,expect=vencido?10:0;
 console.log(JSON.stringify({vencido,disp:cenDisp(l),quarentenaFisica:l.quarentena,quarentenaProjetada:d.quarC,compra:d.liq,condicional:d.cond,expectedCompra:expect,memoria:cal01Memo(d.cal,{quar:100,un:d.un,quarC:d.quarC,quarRef:d.quarRef,cond:d.cond,condFalta:d.condFalta})}));
 const memo=cal01Memo(d.cal,{quar:100,un:d.un,quarC:d.quarC,quarRef:d.quarRef,cond:d.cond,condFalta:d.condFalta});
 const ok=d.liq===expect&&d.cond===(vencido?0:10)&&before===JSON.stringify(c)&&(!vencido||memo.some(t=>t.includes('Vencido: 100 L')&&t.includes('01/2000')))&&(!vencido||!memo.some(t=>t.includes('se o laudo liberar')||t.includes('até o laudo')));
 console.log((ok?'OK ':'FALHA ')+(vencido?'vencido não deve cobrir compra por laudo':'válido permanece condicionado ao laudo'));if(!ok)fails++;
}
console.log('RESULTADO principal '+(2-fails)+'/2');
const c={lotes:{v:{prod:'P',lote:'V',un:'L',local:'A',validade:'01/2000',fisico:7,quarentena:7,reservado:0},a:{prod:'P',lote:'A',un:'L',local:'A',validade:'12/2099',fisico:3,quarentena:3,reservado:0}},reqs:{},ordens:{},movs:[]};
const before=JSON.stringify(c),est=cenEstDem(c,'F',{locFaz:{A:'F'}},[]),x=Object.assign({faz:'F',saf:'S',hoje:'2026-09-26',viavel:'2026-09-26',ordem:{S:0},osd:[],occ:[{k:'K',saf:'S',tal:'T',local:'T',nome:'Aplicar',area:1,dt:'2026-09-27',prods:[{nome:'P',dose:10,q:10,un:'L',preco:1}]}]},est),d=demFazenda(x).P;
const opts={quar:10,un:d.un,quarC:d.quarC,quarRef:d.quarRef,cond:d.cond,condFalta:d.condFalta};
const txt=demCondTxt(opts),memo=cal01Memo(d.cal,opts);console.log(JSON.stringify({mistura:{compra:d.liq,condicional:d.cond},txt,memo}));
const ok=d.liq===7&&d.cond===3&&txt.includes('lote A')&&!txt.includes('lote V')&&memo.some(t=>t.includes('Vencido: 7 L'))&&!memo.some(t=>t.startsWith('Reprovado:'))&&before===JSON.stringify(c);
console.log((ok?'OK ':'FALHA ')+'mistura separa vencido do laudo pendente sem criar reprovação');if(!ok)fails++;
console.log('RESULTADO total '+(3-fails)+'/3');if(fails)process.exitCode=1;
'''
with tempfile.NamedTemporaryFile('w',suffix='.js') as f:
 f.write(src);f.flush();r=subprocess.run(['node',f.name],capture_output=True,text=True)
 print(r.stdout,end='');print(r.stderr,end='',file=sys.stderr);sys.exit(r.returncode)
