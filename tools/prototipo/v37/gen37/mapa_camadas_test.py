"""EX55 D2: contrato puro e contraprova; A2/A5 no navegador são separados."""
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys

# Executar somente em páginas isoladas do ensaio, após aplicar o contexto real.
# O coletor lê classes e legendas do render corrente; não muda filtros/dados.
SNAPSHOT_JS = r'''JSON.stringify((()=>{
 const self=MUX.self;if(!self)throw Error('mapa ainda não inicializado');
 const l=lay(self),f=flt(self,l),ids=TIDS();
 if(!ids.length)throw Error('inventário de talhões vazio');
 return {fazenda:FAZ,camada:l,filtros:f,alvos:ALV,
  linhas:ids.map(id=>({id,...cls(l,f,id)})),
  legenda:legend(self,l,f,[]).map(x=>({k:x.k===undefined?null:x.k,t:x.t}))};
})())'''


def comparar(base, candidata):
    """Cada pacote contém 60 casos nomeados e seus snapshots, sem omissões."""
    fases = ['Todas', 'A liberar', 'Liberadas', 'Em execução', 'Em conferência', 'Encerradas']
    casos = ['OS|'+v+'|'+f for v in ['Fases', 'Avanço', 'Atrasos', 'Impedimentos'] for f in fases]
    casos += ['MIP|'+d+'|'+a for d in ['7', '30'] for a in ['sem alvo', 'com alvo']]
    casos += ['IRR|Hoje', 'IRR|Balanço hídrico']
    esperados = {faz+'|'+c for faz in ['Santa Rita', 'Lagoa Grande'] for c in casos}
    for pacote in [base, candidata]:
        assert set(pacote) == esperados, 'inventário incompleto ou casos inesperados'
        por_fazenda = {}
        for chave, snap in pacote.items():
            faz = chave.split('|', 1)[0]
            assert snap['fazenda'] == faz, 'contexto de fazenda incorreto'
            modo = chave.split('|')[1:]
            f = snap['filtros']
            if modo[0] == 'OS':
                assert snap['camada'] == 'O.S./prazos' and f['ver'] == modo[1] and f['fase'] == modo[2], 'visão ou fase incorreta'
            elif modo[0] == 'MIP':
                assert snap['camada'] == 'MIP/MID' and f['per'] == 'Últimos '+modo[1]+' dias', 'período incorreto'
                assert (bool(snap['alvos']) if modo[2] == 'com alvo' else snap['alvos'] is None), 'filtro de alvo incorreto'
            else:
                assert snap['camada'] == 'Irrigação' and f['ver'] == modo[1], 'visão de irrigação incorreta'
            ids = [r['id'] for r in snap['linhas']]
            assert ids and len(ids) == len(set(ids)), 'talhões ausentes ou duplicados'
            assert set(ids) == por_fazenda.setdefault(faz, set(ids)), 'inventário varia entre casos'
            assert snap['legenda'], 'legenda ausente'
    assert base == candidata, 'classes, rótulos, inventário, contexto ou legendas divergentes'
    return len(esperados)

HERE = Path(__file__).resolve().parent
NODE = os.environ.get('NODE', 'node')


def main():
    subprocess.run([NODE, str(HERE / 'mapa_camadas_unit.js')], check=True)
    source = (HERE / 'mapa_camadas.js').read_text(encoding='utf-8')
    palette = json.loads(next(x for x in source.splitlines() if x.startswith('const MC_COR='))[13:-1])
    assert set(palette) == {'ok', 'good', 'lime', 'yellow', 'orange', 'red', 'gray', 'blue', 'navy', 'none', 'cloud', 'purple', 'sat'}
    with tempfile.TemporaryDirectory(prefix='ex55-mutation-') as td:
        td = Path(td)
        shutil.copyfile(HERE / 'mapa_camadas_unit.js', td / 'mapa_camadas_unit.js')
        if (HERE / 'inicio.base.py').exists():
            shutil.copyfile(HERE / 'inicio.base.py', td / 'inicio.base.py')
        assert "x.d<5?'ok'" in source
        (td / 'mapa_camadas.js').write_text(source.replace("x.d<5?'ok'", "x.d<6?'ok'", 1), encoding='utf-8')
        result = subprocess.run([NODE, str(td / 'mapa_camadas_unit.js')], capture_output=True, text=True)
        assert result.returncode != 0 and 'yellow' in result.stderr and 'ok' in result.stderr, result.stderr
        print('PASS: mutação do limiar 5→6 rejeitada por divergência de classe')
    print('PASS: contrato puro; não certifica paridade visual nem regressões de navegador')


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--coletor':
        print(SNAPSHOT_JS)
    elif len(sys.argv) == 4 and sys.argv[1] == '--comparar':
        print('PASS paridade de', comparar(json.loads(Path(sys.argv[2]).read_text()), json.loads(Path(sys.argv[3]).read_text())), 'contextos capturados')
    else:
        main()
