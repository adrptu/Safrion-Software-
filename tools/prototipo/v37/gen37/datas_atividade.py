"""EX57 F0a: adaptador Python do núcleo JS, sem duplicar a regra.

calcular_lote recebe [{atividade, cultivo, contexto}] e devolve recibos
{data: ISO|None, origem, variante}. A conversão para date/dia inteiro é do
consumidor. NODE_BINARY permite selecionar o runtime já instalado. Sem shell
ou dependências npm. Use lote na geração para evitar um processo por atividade.
Falha do runtime/entrada é explícita; nunca substitui data por zero ou plantio.
"""
import json
import os
from pathlib import Path
import subprocess

_FONTE = Path(__file__).with_suffix('.js')
_RUNNER = """
const fs = require('fs');
const {daDataAtividade} = require(process.argv[1]);
const entradas = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(entradas.map(e => daDataAtividade(e.atividade, e.cultivo, e.contexto))));
"""


def calcular_lote(entradas):
    """Executa a mesma fonte usada pelo browser; não muta as entradas."""
    if not entradas:
        return []
    processo = subprocess.run(
        [os.environ.get('NODE_BINARY', 'node'), '-e', _RUNNER, str(_FONTE.resolve())],
        input=json.dumps(entradas, ensure_ascii=False, allow_nan=False),
        text=True, capture_output=True, check=True, timeout=30,
    )
    return json.loads(processo.stdout)


def data_atividade(atividade, cultivo, contexto):
    return calcular_lote([dict(atividade=atividade, cultivo=cultivo, contexto=contexto)])[0]
