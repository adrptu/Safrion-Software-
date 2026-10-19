"""Paleta canônica do módulo puro, compartilhada com o gerador IN-04."""
import json
from pathlib import Path

_fonte = (Path(__file__).resolve().parent.parent / "mapa_camadas.js").read_text(encoding="utf-8")
_linha = next(linha for linha in _fonte.splitlines() if linha.startswith("const MC_COR="))
LCOR_OP = json.loads(_linha[len("const MC_COR="):-1])
