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
 console.log(JSON.stringify({vencido,disp:cenDisp(l),quarentenaFisica:l.quarentena,quarentenaProjetada:d.quarC,compra:d.liq,condicional:d.cond,expectedCompra:expect,memoria:cal01Memo(d.cal,{un:d.un,quarC:d.quarC,quarRef:d.quarRef,cond:d.cond,condFalta:d.condFalta})}));
 const ok=d.liq===expect&&d.cond===(vencido?0:10)&&before===JSON.stringify(c);
 console.log((ok?'OK ':'FALHA ')+(vencido?'vencido não deve cobrir compra por laudo':'válido permanece condicionado ao laudo'));if(!ok)fails++;
}
console.log('RESULTADO '+(2-fails)+'/2');if(fails)process.exitCode=1;
'''
with tempfile.NamedTemporaryFile('w',suffix='.js') as f:
 f.write(src);f.flush();r=subprocess.run(['node',f.name],capture_output=True,text=True)
 print(r.stdout,end='');print(r.stderr,end='',file=sys.stderr);sys.exit(r.returncode)
