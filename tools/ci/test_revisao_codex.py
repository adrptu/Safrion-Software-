# -*- coding: utf-8 -*-
"""Regressão do portão "Revisão do Codex no commit atual" (tools/github/revisao_codex.py). Sem rede.

O resumo abaixo segue o formato publicado pelo app do Codex no PR #46 (09/10/2026), com outros SHAs.
"""
import json, os, subprocess, sys, tempfile, unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
GITHUB = os.path.join(os.path.dirname(os.path.dirname(AQUI)), 'tools', 'github')
sys.path.insert(0, GITHUB)
import revisao_codex  # noqa: E402

HEAD = 'a' * 40
OUTRO = 'b' * 40


def resumo(head=HEAD, status='completed', code='✅ **Completed** <relative-time>x</relative-time>', curto=None):
    curto = curto if curto is not None else head[:7]
    marca = json.dumps({'blockingSeverityThreshold': 'P0', 'headSha': head, 'mergeGateEnabled': False,
                        'pullRequestNumber': 46, 'repository': 'adrptu/Safrion-Software-', 'status': status})
    return (f'<!-- codex-pull-request-review-summary -->\n<!-- codex-security-review:v1 {marca} -->\n'
            '## Codex Review Summary\n\n| Review | Status | Commit | Review trigger |\n| --- | --- | --- | --- |\n'
            f'| 📝 **Code Review** | {code} | `{curto}` | Draft marked ready |\n'
            f'| 🔒 **Security Review** | ✅ **Completed** | `{curto}` | Draft marked ready |\n')


def comentario(corpo, login='chatgpt-codex-connector[bot]', atualizado='2026-10-09T13:09:18Z', acesso='NONE'):
    return {'user': {'login': login}, 'body': corpo, 'updated_at': atualizado, 'author_association': acesso}


def parecer(head=HEAD, acesso='OWNER', login='adrptu', atualizado='2026-10-09T15:00:00Z'):
    return comentario(f'Revisão focal.\nParecer favorável do revisor: {head}\n', login=login, acesso=acesso,
                      atualizado=atualizado)


class Portao(unittest.TestCase):
    def motivo(self, comentarios, head=HEAD):
        return revisao_codex.motivo_de_bloqueio(comentarios, head)

    def test_revisao_concluida_no_head_libera(self):
        self.assertIsNone(self.motivo([comentario('outro texto', login='adrptu'), comentario(resumo()), parecer()]))

    def test_revisao_concluida_sem_parecer_nao_libera(self):
        # Contraprova do achado 4253439328 e de PR49-REV-20261013-01: concluir com achados não é parecer favorável.
        com_achados = resumo() + '\n### Security findings\n\n#### Advisory findings (1)\n'
        self.assertIn('parecer favorável', self.motivo([comentario(com_achados)]))
        self.assertIn('parecer favorável', self.motivo([comentario(resumo())]))

    def test_parecer_invalido_nao_libera(self):
        casos = {
            'de outro commit': parecer(head=OUTRO),
            'sem acesso ao repositório': parecer(acesso='NONE'),
            'anterior ao último resumo (4253491148)': parecer(atualizado='2026-10-09T13:00:00Z'),
            'escrito por bot': parecer(login='chatgpt-codex-connector[bot]'),
            'sha curto': comentario(f'Parecer favorável do revisor: {HEAD[:7]}', login='adrptu', acesso='OWNER',
                                    atualizado='2026-10-09T15:00:00Z'),
            'citado no meio da linha': comentario(f'> Parecer favorável do revisor: {HEAD}', login='adrptu',
                                                  acesso='OWNER', atualizado='2026-10-09T15:00:00Z'),
        }
        for nome, c in casos.items():
            with self.subTest(nome):
                self.assertIsNotNone(self.motivo([comentario(resumo()), c]), nome)

    def test_bloqueios(self):
        casos = {
            'sem resumo': [],
            'só o parecer, sem revisão do app': [parecer()],
            'resumo de outro commit': [comentario(resumo(head=OUTRO))],
            'segurança em andamento': [comentario(resumo(status='in_progress'))],
            'código em andamento': [comentario(resumo(code='⏳ **In progress**'))],
            'linha de código de outro commit': [comentario(resumo(curto=OUTRO[:7]))],
            'resumo imitado por pessoa': [comentario(resumo(), login='adrptu')],
            'imitado por outro bot': [comentario(resumo(), login='codex-connector[bot]')],
            'formato sem marca': [comentario('<!-- codex-pull-request-review-summary -->\n| 📝 **Code Review** |')],
            'marca ilegível': [comentario('<!-- codex-pull-request-review-summary -->\n'
                                          '<!-- codex-security-review:v1 {headSha: x} -->')],
            'sem linha de código': [comentario(resumo().replace('📝 **Code Review**', 'Code'))],
        }
        for nome, comentarios in casos.items():
            with self.subTest(nome):
                self.assertIsNotNone(self.motivo(comentarios), nome)

    def test_vale_o_resumo_mais_recente(self):
        antigo = comentario(resumo(), atualizado='2026-10-09T13:00:00Z')
        novo = comentario(resumo(head=OUTRO), atualizado='2026-10-09T14:00:00Z')  # parecer() é das 15:00
        self.assertIsNotNone(self.motivo([antigo, novo, parecer()]))
        self.assertIsNone(self.motivo([novo, antigo, parecer(head=OUTRO)], head=OUTRO))

    def test_head_invalido(self):
        for head in ('', 'abc', 'A' * 40, None):
            with self.subTest(head):
                self.assertIsNotNone(self.motivo([comentario(resumo())], head=head))


class Linha(unittest.TestCase):
    def rodar(self, *args, comentarios=None):
        with tempfile.TemporaryDirectory() as d:
            extra = []
            if comentarios is not None:
                arq = os.path.join(d, 'c.jsonl')
                with open(arq, 'w', encoding='utf-8') as f:
                    f.write(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in comentarios))
                extra = ['--comentarios', arq]
            return subprocess.run([sys.executable, os.path.join(GITHUB, 'revisao_codex.py'), *args, *extra],
                                  capture_output=True, text=True)

    def test_pull_request(self):
        ok = self.rodar('--evento', 'pull_request', '--head', HEAD, comentarios=[comentario(resumo()), parecer()])
        self.assertEqual(ok.returncode, 0, ok.stderr)
        espera = self.rodar('--evento', 'pull_request', '--head', HEAD, comentarios=[])
        self.assertEqual(espera.returncode, 1)
        self.assertIn('@codex review', espera.stderr)
        self.assertEqual(self.rodar('--evento', 'pull_request', '--head', HEAD).returncode, 2)

    def test_push_na_main_passa(self):
        self.assertEqual(self.rodar('--evento', 'push').returncode, 0)


if __name__ == '__main__':
    unittest.main()
