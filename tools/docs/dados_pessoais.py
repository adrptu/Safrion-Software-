# -*- coding: utf-8 -*-
"""Confere o inventário de dados pessoais (docs/dados-pessoais.md, roteiro E21) contra o código, só com Python padrão.

Acha nas migrações toda coluna cujo nome traz email, subject, ip, user_agent, responsible ou database_user, e no Terraform
toda variável cujo bloco cita user:, group: ou e-mail. Cada uma precisa estar na lista da seção "Conferência automática"
do inventário; item da lista que não existe mais no código também falha. A lista pode ter itens a mais que o padrão não
acha (ex.: app.app_user.name), desde que existam. Comentário SQL (--) não conta como coluna."""
import os
import re
from pathlib import Path

PADRAO_COLUNA = re.compile(r'(^|_)(e?mail|subject|ip|user_agent|responsible|database_user)($|_)')
PADRAO_VARIAVEL = re.compile(r'user:|group:|e-?mail', re.I)
RESTRICOES = {'primary', 'unique', 'check', 'foreign', 'constraint', 'exclude', 'like'}
ITEM = re.compile(r'^- `((?:[a-z_]+\.[a-z_]+\.[a-z_]+)|(?:tf:[a-z_]+\.[a-z_]+))`\s*$', re.M)
INVENTARIO = 'docs/dados-pessoais.md'


def _sem_comentarios(sql):
    return re.sub(r'--[^\n]*', '', sql)


def colunas(raiz):
    """Todas as colunas criadas nas migrações, como schema.tabela.coluna."""
    achadas = set()
    pasta = os.path.join(raiz, 'packages', 'db', 'migrations')
    for nome in sorted(os.listdir(pasta)):
        if not nome.endswith('.sql'):
            continue
        sql = _sem_comentarios(Path(pasta, nome).read_text(encoding='utf-8'))
        for m in re.finditer(r'CREATE TABLE(?: IF NOT EXISTS)?\s+([a-z_]+\.[a-z_]+)\s*\((.*?)\n\);', sql, re.S | re.I):
            tabela, corpo = m.group(1), m.group(2)
            for linha in corpo.splitlines():
                c = re.match(r'\s*([a-z_][a-z0-9_]*)\s+\S', linha)
                if c and c.group(1).lower() not in RESTRICOES:
                    achadas.add(f'{tabela}.{c.group(1)}')
        for m in re.finditer(r'ALTER TABLE\s+([a-z_]+\.[a-z_]+)\s+ADD COLUMN(?: IF NOT EXISTS)?\s+([a-z_][a-z0-9_]*)', sql, re.I):
            achadas.add(f'{m.group(1)}.{m.group(2)}')
    return achadas


def variaveis(raiz):
    """Variáveis do Terraform por módulo, com o texto do bloco: {'tf:modulo.nome': texto}."""
    achadas = {}
    base = os.path.join(raiz, 'infra', 'terraform')
    for modulo in sorted(os.listdir(base)):
        pasta = os.path.join(base, modulo)
        if not os.path.isdir(pasta):
            continue
        for nome in sorted(os.listdir(pasta)):
            if not nome.endswith('.tf'):
                continue
            texto = Path(pasta, nome).read_text(encoding='utf-8')
            for m in re.finditer(r'^variable "([a-z_][a-z0-9_]*)" \{\n(.*?)^\}', texto, re.S | re.M):
                achadas[f'tf:{modulo}.{m.group(1)}'] = m.group(2)
    return achadas


def conferir(raiz):
    """Lista de falhas; vazia quando código e inventário batem."""
    caminho = os.path.join(raiz, INVENTARIO)
    if not os.path.exists(caminho):
        return [f'{INVENTARIO} ausente']
    listados = set(ITEM.findall(Path(caminho).read_text(encoding='utf-8')))
    todas_colunas = colunas(raiz)
    todas_variaveis = variaveis(raiz)
    pessoais = {c for c in todas_colunas if PADRAO_COLUNA.search(c.rsplit('.', 1)[1])}
    pessoais |= {v for v, texto in todas_variaveis.items() if PADRAO_VARIAVEL.search(texto)}
    falhas = [f'{i} tem dado pessoal e não está no inventário' for i in sorted(pessoais - listados)]
    falhas += [f'{i} está no inventário e não existe mais' for i in sorted(listados - todas_colunas - set(todas_variaveis))]
    return falhas
