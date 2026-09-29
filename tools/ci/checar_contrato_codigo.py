# -*- coding: utf-8 -*-
"""Portão do job de código da CI (revisão R001-01 do Codex).
- Nem package.json nem pnpm-lock.yaml: repositório só de documentação → job de código N/A (ativo=false), saída 0.
- Caminho existente que não é arquivo regular: erro, nunca documentação.
- Só um dos dois: erro (aplicação sem lockfile ou lockfile órfão).
- Os dois: exige o contrato mínimo (PRD 23.1/23.4, ENG-006): packageManager "pnpm@X.Y.Z" exato, engines.node,
  .nvmrc com versão exata e os scripts obrigatórios na raiz. Os scripts rodam na CI SEM --if-present.
Escreve ativo=true|false em $GITHUB_OUTPUT quando existir. Uso: python3 tools/ci/checar_contrato_codigo.py [raiz]"""
import json, os, re, sys

SCRIPTS_OBRIGATORIOS = ['format:check', 'lint', 'typecheck', 'test', 'build']
raiz = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
tem_pkg = os.path.isfile(os.path.join(raiz, 'package.json'))
tem_lock = os.path.isfile(os.path.join(raiz, 'pnpm-lock.yaml'))
erros = []

def saida(ativo):
    gh = os.environ.get('GITHUB_OUTPUT')
    if gh:
        with open(gh, 'a', encoding='utf-8') as f: f.write(f'ativo={"true" if ativo else "false"}\n')

invalidos = [nome for nome in ('package.json', 'pnpm-lock.yaml')
             if os.path.lexists(os.path.join(raiz, nome)) and not os.path.isfile(os.path.join(raiz, nome))]
if invalidos:
    for nome in invalidos: print(f'ERRO: {nome} existe, mas não é arquivo regular')
    saida(False); sys.exit(1)

if not tem_pkg and not tem_lock:
    print('N/A: sem package.json e sem pnpm-lock.yaml — repositório só de documentação (ADR 0002).')
    saida(False); sys.exit(0)
if tem_pkg != tem_lock:
    erros.append('package.json sem pnpm-lock.yaml' if tem_pkg else 'pnpm-lock.yaml sem package.json')
else:
    try:
        with open(os.path.join(raiz, 'package.json'), encoding='utf-8') as f:
            pkg = json.load(f)
    except (OSError, ValueError, RecursionError) as e:
        pkg = {}; erros.append(f'package.json inválido: {e}')
    if not isinstance(pkg, dict):
        pkg = {}; erros.append('package.json deve conter um objeto JSON')
    pm = pkg.get('packageManager', '')
    if not isinstance(pm, str) or not re.fullmatch(r'pnpm@\d+\.\d+\.\d+(\+sha\d+\.[0-9a-f]+)?', pm):
        erros.append(f'packageManager deve fixar pnpm@X.Y.Z (encontrado: {pm!r})')
    engines = pkg.get('engines')
    node = engines.get('node') if isinstance(engines, dict) else None
    if not isinstance(node, str) or not node.strip():
        erros.append('engines.node deve ser texto não vazio')
    nvmrc = os.path.join(raiz, '.nvmrc')
    if not os.path.isfile(nvmrc) or not re.fullmatch(r'v?\d+\.\d+\.\d+', open(nvmrc, encoding='utf-8').read().strip()):
        erros.append('.nvmrc ausente ou sem versão exata (X.Y.Z)')
    scripts = pkg.get('scripts')
    if not isinstance(scripts, dict):
        scripts = {}; erros.append('scripts deve ser um objeto JSON')
    falta = [s for s in SCRIPTS_OBRIGATORIOS
             if not isinstance(scripts.get(s), str) or not scripts[s].strip()]
    if falta: erros.append('scripts obrigatórios ausentes ou sem texto não vazio na raiz: ' + ', '.join(falta))

if erros:
    for e in erros: print('ERRO:', e)
    saida(False); sys.exit(1)
print('OK: contrato de código atendido; job de código ativo.')
saida(True); sys.exit(0)
