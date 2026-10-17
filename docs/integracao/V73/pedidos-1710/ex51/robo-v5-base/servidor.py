# -*- coding: utf-8 -*-
"""Servidor local mínimo do robô v5 (EX-51), só em 127.0.0.1.

Uso: python3 -I servidor.py --trabalho <dir> --robo <robô .html> [--telas <screens.json>] [--saida <dir>] [--porta N]

Rotas (nada fora delas):
  GET  /v3/<arquivo>          páginas e arquivos de apoio copiados do _render (<trabalho>/v3)
  GET  /robot3/screens.json   lista [{"n": "<TELA>"}] (--telas; padrão <trabalho>/robot3/screens.json)
  GET  /robot3/vazio.html     página vazia da mesma origem (limpa o armazenamento entre aberturas da 2ª passada)
  GET  /anexo-robo-v5.html    o robô (--robo)
  POST /save?name=<arquivo>   grava o corpo em --saida (padrão <trabalho>/saida)/<arquivo> (só nomes simples, .json)
"""
import argparse, os, re, sys, mimetypes, urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

NOME_OK = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,120}\.json$')
VAZIO = b'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>vazio</title></head><body></body></html>'


def criar(trabalho, robo, porta=0, telas=None, saida=None):
    v3 = os.path.realpath(os.path.join(trabalho, 'v3'))
    telas = telas or os.path.join(trabalho, 'robot3', 'screens.json')
    saida = saida or os.path.join(trabalho, 'saida')
    os.makedirs(saida, exist_ok=True)

    class H(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def log_message(self, *a):   # silencioso; o robô registra o que importa
            pass

        def _env(self, code, corpo, tipo='application/octet-stream'):
            self.send_response(code)
            self.send_header('Content-Type', tipo)
            self.send_header('Content-Length', str(len(corpo)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            if self.command != 'HEAD':
                self.wfile.write(corpo)

        def _arquivo(self, caminho):
            try:
                with open(caminho, 'rb') as f:
                    corpo = f.read()
            except OSError:
                return self._env(404, b'nao encontrado', 'text/plain; charset=utf-8')
            tipo = mimetypes.guess_type(caminho)[0] or 'application/octet-stream'
            if caminho.endswith('.html'):
                tipo = 'text/html; charset=utf-8'
            elif caminho.endswith('.js'):
                tipo = 'text/javascript; charset=utf-8'
            elif caminho.endswith('.json'):
                tipo = 'application/json; charset=utf-8'
            self._env(200, corpo, tipo)

        def do_GET(self):
            p = urllib.parse.urlparse(self.path).path
            p = urllib.parse.unquote(p)
            if p == '/anexo-robo-v5.html':
                return self._arquivo(robo)
            if p == '/robot3/screens.json':
                return self._arquivo(telas)
            if p == '/robot3/vazio.html':
                return self._env(200, VAZIO, 'text/html; charset=utf-8')
            if p.startswith('/v3/'):
                alvo = os.path.realpath(os.path.join(v3, p[len('/v3/'):]))
                if alvo.startswith(v3 + os.sep) and os.path.isfile(alvo):
                    return self._arquivo(alvo)
            return self._env(404, b'nao encontrado', 'text/plain; charset=utf-8')

        do_HEAD = do_GET

        def do_POST(self):
            u = urllib.parse.urlparse(self.path)
            n = int(self.headers.get('Content-Length') or 0)
            corpo = self.rfile.read(n) if n else b''
            if u.path != '/save':
                return self._env(404, b'nao encontrado', 'text/plain; charset=utf-8')
            nome = (urllib.parse.parse_qs(u.query).get('name') or [''])[0]
            if not NOME_OK.match(nome):
                return self._env(400, b'nome invalido', 'text/plain; charset=utf-8')
            tmp = os.path.join(saida, '.' + nome + '.tmp')
            with open(tmp, 'wb') as f:
                f.write(corpo)
            os.replace(tmp, os.path.join(saida, nome))
            self._env(200, b'ok', 'text/plain; charset=utf-8')

    return ThreadingHTTPServer(('127.0.0.1', porta), H)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trabalho', required=True)
    ap.add_argument('--robo', required=True)
    ap.add_argument('--porta', type=int, default=0)
    ap.add_argument('--telas')
    ap.add_argument('--saida')
    a = ap.parse_args()
    srv = criar(a.trabalho, a.robo, a.porta, a.telas, a.saida)
    print('porta', srv.server_address[1], flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
