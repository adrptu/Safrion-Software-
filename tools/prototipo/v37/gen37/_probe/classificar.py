# -*- coding: utf-8 -*-
"""Classificador único das saídas de teste do protótipo (bateria e reclassificação dos logs já gravados).
Quatro resultados:
- falha: código de saída ≠ 0; linha que começa com FALHA/FALHOU; RESULTADO: FALHOU; Traceback; TIMEOUT; contador positivo
  (FALHAS: n, n falhas); ou placar parcial na mesma linha (a/b ok, a de b verificações) com a < b. Basta uma ocorrência:
  um erro anterior não é escondido por um resumo final zero.
- nao_executado: só imprimiu a ajuda (linha "Uso:") e nenhuma verificação.
- revisar: saída 0 sem evidência positiva de verificação (formato informal); não conta como aprovado.
- ok: sem sinal de falha e com evidência positiva (OK, RESULTADO: OK, a/b ok, FALHAS: 0 ...).
"FALHAS: 0" e "FALHAS: nenhuma" são sucesso."""
import re
_RUIM = re.compile(r'(?mi)^\s*(?:FALHA|FALHOU)\b|\bRESULTADO:\s*FALHOU\b|^Traceback\b|^TIMEOUT\b|\bFALHAS:\s*[1-9]\d*\b|\b[1-9]\d*\s+falhas\b')
_PLACAR = re.compile(r'(?i)(?<![\d/])(\d{1,3})[ \t]*(?:/|de)[ \t]*(\d{1,3})[ \t]+(?:ok\b|verifica)')   # na mesma linha; datas (mm/aaaa) não contam
_BOM = re.compile(r'(?mi)^\s*OK\b|\bRESULTADO:\s*OK\b|(?<![\d/])\d{1,3}[ \t]*(?:/|de)[ \t]*\d{1,3}[ \t]+(?:ok\b|verifica)|\bFALHAS:\s*(?:0|nenhuma)\b|\b0 falhas\b|\b[1-9]\d*\s+ok\b')
_AJUDA = re.compile(r'(?m)^\s*Uso:')

def motivos(out, code):
    m = []
    if code != 0: m.append(f'exit {code}')
    for x in _RUIM.finditer(out or ''): m.append(x.group(0).strip())
    for a, b in _PLACAR.findall(out or ''):
        if int(a) < int(b): m.append(f'placar {a}/{b}')
    return m

def classe(out, code):
    if motivos(out, code): return 'falha'
    if not _BOM.search(out or ''): return 'nao_executado' if _AJUDA.search(out or '') else 'revisar'
    return 'ok'

def ruim(out, code): return classe(out, code) != 'ok'

if __name__ == '__main__':
    casos = [('FALHAS: 0', 0, 'ok'), ('FALHAS: nenhuma', 0, 'ok'), ('RESULTADO: 14/14 ok', 0, 'ok'), ('42 de 42 verificações OK', 0, 'ok'),
             ('FALHAS: 2', 0, 'falha'), ('  FALHA saldo', 0, 'falha'), ('3 falhas', 0, 'falha'), ('OK tudo certo', 1, 'falha'),
             ('  FALHA x\n...\nFALHAS: 0', 0, 'falha'), ('RESULTADO: 13/14 ok', 0, 'falha'), ('Traceback (most recent call last):', 0, 'falha'),
             ('0 falhas', 0, 'ok'), ('31 ok · 0 falhas []', 0, 'ok'),
             ('lote 18.000 kg 03/2027\n  OK  saldo', 0, 'ok'), ('Vencido · 07/2026\n  OK  lote', 0, 'ok'),
             ('FALHOU campo X\nRESULTADO: FALHOU 14/15', 0, 'falha'), ('RESULTADO: FALHOU 15/15', 0, 'falha'),
             ('Testes da frente\nUso: python3 cadc_test.py cd02 | cd06', 0, 'nao_executado'), ('rodou sem contar nada', 0, 'revisar'), ('terminou ok', 0, 'revisar')]
    erros = [(o, c, e, classe(o, c)) for o, c, e in casos if classe(o, c) != e]
    print('classificador:', len(casos) - len(erros), '/', len(casos), 'casos corretos', erros or '')
    raise SystemExit(1 if erros else 0)
