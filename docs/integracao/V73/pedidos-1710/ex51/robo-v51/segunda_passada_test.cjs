const fs=require('fs'),vm=require('vm'),assert=require('assert');
const py=fs.readFileSync(__dirname+'/rodar.py','utf8');
const js=py.split('LEVA_JS = r"""')[1].split('"""')[0];
function inspect(header,body,hasDialog=true){
 const d={getClientRects:()=>[1],innerText:body,querySelector:()=>header?{innerText:header}:null};
 const ctx={getComputedStyle:()=>({visibility:'visible'}),location:{pathname:'/OS.dc.html',hash:'#OS-0502'},document:{querySelectorAll:s=>s.startsWith('[role=dialog]')?(hasDialog?[d]:[]):[],querySelector:()=>({innerText:'OS-0502'}),body:{innerText:body}}};
 return vm.runInNewContext(js,ctx);
}
let r=inspect('','Corpo cita OS-0502');assert(r.temDialogo);assert.equal(r.dlg,'');
r=inspect('OS-0503','OS-0502');assert.equal(r.dlg,'OS-0503');
r=inspect('','OS-0502',false);assert(!r.temDialogo);assert.equal(r.h1,'OS-0502');
assert(py.includes("r.get('url') != para"));
console.log('PASS A5 extração real LEVA_JS: corpo nunca vira título; h1 só sem diálogo. Verificação estática A6 não substitui navegador.');
