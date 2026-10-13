# -*- coding: utf-8 -*-
"""Portão "Revisão do Codex no commit atual": o merge automático só acontece depois que o commit que vai entrar na
main foi revisado pelo app do Codex e recebeu o parecer favorável escrito do revisor (DEC-0910-02).
Sem rede: lê os comentários do PR (um JSON por linha, como gh api --paginate --jq '.[]').

Passa quando, para o commit atual (head do PR):
- o comentário-resumo do app do Codex tem a marca codex-security-review:v1 com headSha igual ao head completo e status
  completed, e a linha Code Review com Completed e o head abreviado (7 caracteres);
- o último ato do revisor para esse head é um comentário dedicado, de quem tem acesso ao repositório, cujo texto
  inteiro é "Parecer favorável do revisor: <head completo>", atualizado depois do resumo. O ato de retirada é um
  comentário dedicado "Parecer retirado: <head completo>". Linha citada, em bloco de código ou dentro de outro texto
  não conta (PR49-REV-20261013-02).
Concluir a revisão não é parecer favorável: achados do app, contestados ou não, ficam para o revisor avaliar antes de
publicar o parecer (achado do Codex 4253439328). O autor nunca publica esses comentários (AGENTS.md 3).
Formato desconhecido, resumo ausente ou de outro commit: falha fechado, com o motivo. Fora de pull_request (push na
main) não há PR a conferir: o portão já valeu no PR que gerou o merge.

  python3 revisao_codex.py --evento pull_request --head SHA --comentarios comentarios.jsonl
"""
import argparse, json, re, sys

APP_CODEX = 'chatgpt-codex-connector[bot]'
RESUMO = '<!-- codex-pull-request-review-summary -->'
MARCA = re.compile(r'<!--\s*codex-security-review:v1\s*(\{.*?\})\s*-->')
LINHA_CODE_REVIEW = re.compile(r'^\|\s*📝\s*\*\*Code Review\*\*\s*\|(.*)$', re.M)
ATO = re.compile(r'(Parecer favorável do revisor|Parecer retirado): ([0-9a-f]{40})')
FAVORAVEL = 'Parecer favorável do revisor'
ACESSO = {'OWNER', 'MEMBER', 'COLLABORATOR'}
ORIENTACAO = 'Marque o PR como pronto para revisão ou comente "@codex review" depois do último push.'


def ler_comentarios(texto):
    return [json.loads(l) for l in texto.splitlines() if l.strip()]


def resumo_do_codex(comentarios):
    """O comentário-resumo mais recente do app do Codex, ou None."""
    resumos = [c for c in comentarios
               if (c.get('user') or {}).get('login') == APP_CODEX and RESUMO in (c.get('body') or '')]
    return max(resumos, key=lambda c: c.get('updated_at') or '', default=None)


def motivo_de_bloqueio(comentarios, head):
    """None quando o app revisou o head e o revisor deu parecer favorável a ele; senão, o motivo em português."""
    if not re.fullmatch(r'[0-9a-f]{40}', head or ''):
        return f'head inválido: {head!r}'
    resumo = resumo_do_codex(comentarios)
    if resumo is None:
        return f'o Codex ainda não publicou o resumo da revisão. {ORIENTACAO}'
    corpo = resumo['body']
    m = MARCA.search(corpo)
    if not m:
        return 'resumo do Codex sem a marca codex-security-review:v1 (formato mudou; conferir à mão)'
    try:
        marca = json.loads(m.group(1))
    except ValueError:
        return 'marca do resumo do Codex ilegível (formato mudou; conferir à mão)'
    if marca.get('headSha') != head:
        return f'o último resumo do Codex é do commit {str(marca.get("headSha"))[:7]}, não de {head[:7]}. {ORIENTACAO}'
    if marca.get('status') != 'completed':
        return f'revisão de segurança do Codex em {head[:7]} com status {marca.get("status")!r}, não completed'
    linha = LINHA_CODE_REVIEW.search(corpo)
    if not linha:
        return 'resumo do Codex sem a linha Code Review (formato mudou; conferir à mão)'
    if '**Completed**' not in linha.group(1):
        return f'revisão de código do Codex em {head[:7]} ainda não concluída'
    if f'`{head[:7]}`' not in linha.group(1):
        return f'a revisão de código do Codex não é do commit {head[:7]}. {ORIENTACAO}'
    # Vale o último ato dedicado para o head (parecer ou retirada). O parecer precisa ser posterior à última
    # atualização do resumo: achado novo exige nova avaliação (4253491148).
    atos = []
    for c in comentarios:
        m = ATO.fullmatch((c.get('body') or '').strip())
        if (m and m.group(2) == head and c.get('author_association') in ACESSO
                and not (c.get('user') or {}).get('login', '').endswith('[bot]')):
            atos.append((c.get('updated_at') or '', c.get('id') or 0, m.group(1)))
    falta = (f'falta o parecer favorável do revisor para {head[:7]}, posterior ao último resumo do Codex: '
             f'comentário dedicado com o texto exato "{FAVORAVEL}: {head}"')
    if not atos:
        return falta
    quando, _, ato = max(atos)
    if ato != FAVORAVEL:
        return f'o último ato do revisor para {head[:7]} retirou o parecer. {falta}'
    if quando <= (resumo.get('updated_at') or ''):
        return falta
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--evento', required=True)
    ap.add_argument('--head', default='')
    ap.add_argument('--comentarios')
    a = ap.parse_args(argv)
    if a.evento != 'pull_request':
        print(f'Evento {a.evento}: sem PR a conferir; a revisão do Codex é exigida no PR antes do merge.')
        return 0
    if not a.comentarios:
        print('ERRO: --comentarios é obrigatório em pull_request', file=sys.stderr)
        return 2
    with open(a.comentarios, encoding='utf-8') as f:
        motivo = motivo_de_bloqueio(ler_comentarios(f.read()), a.head)
    if motivo:
        print(f'Aguardando: {motivo}', file=sys.stderr)
        return 1
    print(f'OK: revisão do app do Codex concluída e parecer favorável do revisor em {a.head[:7]}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
