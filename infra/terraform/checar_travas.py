#!/usr/bin/env python3
# Travas do Cloud SQL da HML que sustentam as exceções GCP-0015 e GCP-0017 do Trivy (hml/README.md, "Achados do
# scanner"). Sem elas, as exceções caem. Dois modos:
#   python3 checar_travas.py                  confere o código em hml/banco.tf (sem credencial, roda em PR);
#   python3 checar_travas.py --plano p.json   confere o plan (terraform show -json), onde o valor já está resolvido.
# Saída 0 = todas as travas presentes; 1 = alguma faltou (lista na saída); 2 = uso incorreto.
import json
import re
import sys
from pathlib import Path

RECURSO = 'google_sql_database_instance.hml'
ESPERADO = {
    'ssl_mode': 'ENCRYPTED_ONLY',
    'connector_enforcement': 'REQUIRED',
}


def bloco_do_recurso(texto: str) -> str:
    inicio = texto.find('resource "google_sql_database_instance" "hml"')
    if inicio < 0:
        return ''
    nivel, i = 0, texto.index('{', inicio)
    for j in range(i, len(texto)):
        nivel += {'{': 1, '}': -1}.get(texto[j], 0)
        if nivel == 0:
            return texto[i:j + 1]
    return ''


def sem_comentarios(texto: str) -> str:
    return '\n'.join(re.sub(r'\s*#.*$', '', linha) for linha in texto.splitlines())


def conferir_codigo(caminho: Path) -> list[str]:
    bloco = sem_comentarios(bloco_do_recurso(caminho.read_text(encoding='utf-8')))
    if not bloco:
        return [f'{RECURSO} não encontrado em {caminho}']
    faltas = []
    for campo, valor in ESPERADO.items():
        if not re.search(rf'\b{campo}\s*=\s*"{valor}"', bloco):
            faltas.append(f'{campo} = "{valor}" ausente')
    if re.search(r'\bauthorized_networks\b', bloco):
        faltas.append('authorized_networks presente: nenhuma rede autorizada é a trava')
    return faltas


def conferir_plano(caminho: Path) -> list[str]:
    plano = json.loads(caminho.read_text(encoding='utf-8'))
    mudancas = [m for m in plano.get('resource_changes', []) if m.get('address') == RECURSO]
    if not mudancas:
        return [f'{RECURSO} ausente do plan']
    depois = mudancas[0].get('change', {}).get('after') or {}
    settings = (depois.get('settings') or [{}])[0]
    ip = (settings.get('ip_configuration') or [{}])[0]
    faltas = []
    if ip.get('ssl_mode') != ESPERADO['ssl_mode']:
        faltas.append(f'ssl_mode = {ip.get("ssl_mode")!r}')
    if settings.get('connector_enforcement') != ESPERADO['connector_enforcement']:
        faltas.append(f'connector_enforcement = {settings.get("connector_enforcement")!r}')
    if ip.get('authorized_networks'):
        faltas.append('authorized_networks não vazio')
    return faltas


def main(argv: list[str]) -> int:
    aqui = Path(__file__).resolve().parent
    if argv == []:
        faltas = conferir_codigo(aqui / 'hml' / 'banco.tf')
    elif len(argv) == 2 and argv[0] == '--plano':
        faltas = conferir_plano(Path(argv[1]))
    else:
        print('Uso: checar_travas.py [--plano plano.json]')
        return 2
    for f in faltas:
        print(f'FALTA: {f}')
    print('OK: travas do Cloud SQL presentes' if not faltas else f'{len(faltas)} trava(s) faltando')
    return 1 if faltas else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
