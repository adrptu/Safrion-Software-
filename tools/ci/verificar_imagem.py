"""Prova do artefato real no Docker; não equivale a homologação com banco/OIDC.

Usa apenas imagens locais construídas pela CI, sem rede, portas publicadas ou
volumes do host. Credenciais-canário são fictícias, com destino inacessível.
Falhas bloqueiam a CI; a limpeza nunca substitui a primeira falha.
"""
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

LIMITES = ["--network", "none", "--read-only", "--cap-drop", "ALL",
           "--security-opt", "no-new-privileges", "--pids-limit", "128",
           "--memory", "512m", "--cpus", "1"]
CANARIO = "credencial-ficticia-do-teste"
RAIZ = Path(__file__).resolve().parents[2]
# Versão e commit que a construção gravou na imagem (E08): versão do pacote da web e commit do checkout construído.
VERSAO = json.loads((RAIZ / "apps/web/package.json").read_text(encoding="utf-8"))["version"]


def commit_do_checkout():
    """Commit do código construído; na CI, igual ao GITHUB_SHA (em PR, o de composição)."""
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True, text=True, timeout=20)
    commit = r.stdout.strip() if r.returncode == 0 else ""
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise AssertionError("commit do checkout ilegível")
    if os.environ.get("GITHUB_SHA") and os.environ["GITHUB_SHA"] != commit:
        raise AssertionError("checkout diferente do GITHUB_SHA")
    return commit


def executar(args, esperado=0, timeout=40):
    r = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode != esperado:
        # Sem imprimir argv, saída do processo ou erro do driver.
        raise RuntimeError(f"docker {args[0]}: saída {r.returncode}, esperada {esperado}")
    return r.stdout + r.stderr if args[0] == 'logs' else r.stdout


def verificar(destino):
    prefixo = "safrion-prova-" + uuid.uuid4().hex[:12]
    containers = []
    commit = None
    evidencia = {"commit": None, "evento": os.environ.get("GITHUB_EVENT_NAME"), "versao": VERSAO, "imagens": {},
                 "provas": [], "limpeza": False}
    falha = None

    def registrar(nome, acao):
        try:
            acao()
            evidencia["provas"].append({"nome": nome, "resultado": "passou"})
        except Exception as erro:
            evidencia["provas"].append({"nome": nome, "resultado": "falhou", "tipo": type(erro).__name__})
            raise

    def rodar(alvo, sufixo, *args, esperado=0):
        nome = prefixo + "-" + sufixo
        containers.append(nome)
        return executar(["run", "--name", nome, *LIMITES, *args], esperado)

    try:
        commit = evidencia["commit"] = commit_do_checkout()
        for alvo in ("web", "preparo"):
            imagem = "safrion-" + alvo + ":ci"
            info = json.loads(executar(["image", "inspect", imagem]))[0]
            evidencia["imagens"][alvo] = {"id": info["Id"], "usuario": info["Config"]["User"]}

            def na_imagem(env=info["Config"].get("Env") or []):
                if "SAFRION_COMMIT=" + commit not in env or "SAFRION_VERSAO=" + VERSAO not in env:
                    raise AssertionError("versão ou commit da construção ausente na imagem")

            registrar(alvo + ": versão e commit da construção na imagem", na_imagem)
            if alvo == "web" and info["Config"].get("Healthcheck", {}).get("Test", [])[:1] != ["CMD"]:
                raise AssertionError("healthcheck requer forma exec na imagem sem shell")
            registrar(alvo + ": usuário não-root", lambda a=alvo, i=imagem: rodar(
                a, a + "-uid", "--entrypoint", "node", i, "-e",
                "if (!process.getuid || !process.getgid || process.getuid() === 0 || process.getgid() === 0) process.exit(1)"))

        registrar("preparo: argumentos obrigatórios", lambda: rodar(
            "preparo", "uso", "safrion-preparo:ci", esperado=2))

        def recusar_producao():
            saida = rodar("preparo", "prod",
                         "-e", "SAFRION_ADMIN_URL=postgres://teste:" + CANARIO + "@127.0.0.1:1/postgres",
                         "-e", "SAFRION_SENHA_MIGRATOR=" + CANARIO,
                         "-e", "SAFRION_SENHA_APP_RUNTIME=" + CANARIO,
                         "safrion-preparo:ci", "--ambiente", "prod", "--banco", "prova", esperado=1)
            resposta = json.loads(saida)
            if resposta.get("codigo") != "AMBIENTE_PROIBIDO" or CANARIO in saida:
                raise AssertionError("recusa de produção inválida")

        registrar("preparo: produção recusada antes da conexão", recusar_producao)

        def saude_indisponivel():
            nome = prefixo + "-web"
            containers.append(nome)
            executar(["run", "--detach", "--name", nome, *LIMITES,
                      "-e", "DATABASE_URL=postgres://teste:" + CANARIO + "@127.0.0.1:1/prova",
                      "-e", "SAFRION_ORIGEM=https://hml.invalid",
                      "-e", "SAFRION_AMBIENTE=hml", "safrion-web:ci"])
            # Sem -e de versão e commit na execução: o /saude mostra os da imagem.
            executar(["exec", "-e", "ESPERADO_VERSAO=" + VERSAO, "-e", "ESPERADO_COMMIT=" + commit, nome,
                      "node", "--input-type=module", "-e", """
              import { setTimeout as esperar } from 'node:timers/promises';
              let resposta;
              for (let i = 0; i < 40; i++) {
                try { resposta = await fetch('http://127.0.0.1:8080/saude', {signal: AbortSignal.timeout(1000)}); break; }
                catch { await esperar(250); }
              }
              if (!resposta || resposta.status !== 503) process.exit(1);
              const corpo = await resposta.json();
              const campos = ['ambiente', 'commit', 'migracao', 'status', 'verificadoEm', 'versao'];
              if (JSON.stringify(Object.keys(corpo).sort()) !== JSON.stringify(campos)
                || corpo.status !== 'indisponivel' || corpo.ambiente !== null || corpo.migracao !== null
                || corpo.versao !== process.env.ESPERADO_VERSAO || corpo.commit !== process.env.ESPERADO_COMMIT
                || !Number.isFinite(Date.parse(corpo.verificadoEm))) process.exit(1);
            """])
            logs = executar(["logs", nome])
            if CANARIO in logs:
                raise AssertionError("credencial-canário no log")

        registrar("web: saúde 503 sem banco e sem dado sensível", saude_indisponivel)
    except Exception as erro:
        falha = erro
    finally:
        limpeza = True
        # Tenta todos os nomes exclusivos, mesmo se uma remoção falhar.
        for nome in containers:
            try:
                executar(["rm", "--force", nome])
            except Exception as erro:
                limpeza = False
                falha = falha or erro
        evidencia["limpeza"] = limpeza
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(evidencia, ensure_ascii=False, indent=2) + "\n")
    if falha:
        raise falha


if __name__ == "__main__":
    try:
        verificar(Path(sys.argv[1]))
        print("OK: imagens executadas; sete provas passaram; containers removidos.")
    except Exception as erro:
        print(f"ERRO: prova de imagem não concluída ({type(erro).__name__}); confira execucao.json.")
        sys.exit(1)
