"""EX-38: código real em Node, dados sintéticos; não substitui navegador/teclado/toque."""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import cenario, engine as E
from areas import mobile as M, processo_os as P, os_campo as F

def main():
    node=os.environ.get('NODE') or shutil.which('node')
    if not node: raise SystemExit('Node indisponível')
    # Captura o JS efetivamente composto pelo gerador do detalhe, sem executar navegador.
    screens={}
    original=M.emit
    def capture(*args,**kw):
        screens[kw.get('fname') or args[0]]=kw.get('js','')
        return original(*args,**kw)
    M.emit=capture
    with tempfile.TemporaryDirectory(prefix='ex38-') as out:
        E.P=out; M.build(); F.build()
        js=screens['MB-02det.dc.html']; a=js.index('const dProj='); b=js.index('const aps=',a)
        detail='function detail(c,o){const v={},r=mbReq(c,o);'+js[a:b]+'return v.d_ins;}\n'
        source=(ROOT/'areas/processo_os.py').read_text(); a=source.index('  const consumoProj='); b=source.index('  /* 14/10',a)
        panel='function panel(c,o){CEN_MEM=c;const v={};o=Object.assign({},o,{r:osReqVis(o,c.reqs[o.req])});'+source[a:b]+'return v.pan_ins;}\n'
        a=source.index("  const EQ={'Adubação");b=source.index('  v.pan_fichas=',a)
        prep='function panelPrep(c,o){const rcC=c,a={op:"Pulverização"},v={};'+source[a:b]+'return v.pan_prep;}\n'
        mb=(ROOT/'areas/mobile.py').read_text(); a=mb.index('function mbIns(');b=mb.index('function mbCard',a)
        reqvis=source[source.index('function osPendCons'):source.index('function osMerge')]
        emb=mb[mb.index('function mbEmb'):mb.index('// Área que ainda cabe')]
        payload=cenario.perfis_js()+cenario.js_prefixo()+'\n'+reqvis+emb+'\n'+('const OSC='+json.dumps(dict(os=F.OS,retirada='fixture'))+';\n'+F.APP_JS.replace('function EXTRAVALS(self,v)','function appVals(self,v)'))+'\n'+mb[a:b]+detail+panel+prep
        payload+='\n'+(ROOT/'ex38_test.js').read_text()
        run=subprocess.run([node],input=payload,text=True,capture_output=True)
        print(run.stdout,end='');print(run.stderr,end='',file=sys.stderr)
        if run.returncode: raise SystemExit(run.returncode)
        print('Geração: mobile.build + OS0424 app/ficha OK; sem navegador')

if __name__=='__main__': main()
