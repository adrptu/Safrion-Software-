#!/usr/bin/env python3
"""Uma consulta textual ao Gemini; sem ferramentas, leitura automática ou retries."""
import argparse
import datetime
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

PROJECT = "project-d6996034-e2ee-4e56-836"
MODEL = "gemini-3.1-pro-preview"
MAX_INPUT_BYTES = 8192
MAX_OUTPUT_TOKENS = 16384
THINKING_LEVEL = "HIGH"
MAX_SKILL_BYTES = 24000
SKILLS_DIR = Path(__file__).resolve().parent / "skills"
SHARED_SKILLS_DIR = Path.home() / ".agents/skills"
SKILL_CATALOG = {name: SKILLS_DIR / name / "SKILL.md" for name in (
    "gcp-infra-essencial", "gcp-custos", "gcp-desempenho-incidentes", "revisao-terceira-opiniao")}
SKILL_CATALOG.update({name: SHARED_SKILLS_DIR / name / "SKILL.md"
                      for name in ("dev-infra", "dev-testes", "dev-revisao",
                                   "negocios-ecossistema", "growth-receita-implantacao",
                                   "ux-essencial", "master-detail-ux",
                                   "minimalismo-essencial", "tabelas-interativas",
                                   "agro-gestao-conhecimento", "benchmark-top5", "dev-backend",
                                   "dev-ciclo-completo", "dev-frontend-mobile",
                                   "indicadores-satelite", "safrion-equipe")})
SKILL_REFERENCES = {"master-detail-ux": ("references/anatomia.md", "references/checklist.md")}
SYSTEM = ("Você colabora com o Safrion como terceira opinião por tarefa, com especialidade em Google Cloud, custos, desempenho e incidentes. "
          "Codex dirige produto/UX/QA; Codex e Claude implementam partes delimitadas e revisam reciprocamente. O revisor integra o PR do outro. "
          "Uma autoria ativa por agente, com contratos/arquivos separados. Você também critica fluxo, acessibilidade e contraexemplos materiais, sem consultas por rotina. Produção depende do aceite do proprietário. "
          "Você só conhece o contexto enviado; não tem ferramentas nem acesso direto ao ambiente. "
          "Distinga fatos fornecidos, hipóteses e evidência faltante. Proponha a menor solução "
          "que atende ao requisito; não acrescente serviços sem necessidade demonstrada. "
          "Não declare inspeções, aprovações, medições ou ações que não executou. "
          "Recomendações dependem de revisão e teste, não são comandos para execução automática.")

def load_skills(selected):
    """Carrega só arquivos explícitos; nunca segue instruções de leitura do conteúdo."""
    roots = (SKILLS_DIR.resolve(), SHARED_SKILLS_DIR.resolve())
    parts, manifest = [], []
    total = 0
    for name in dict.fromkeys(selected):
        source = SKILL_CATALOG[name]
        for relative in ("SKILL.md", *SKILL_REFERENCES.get(name, ())):
            path = (source.parent / relative).resolve(strict=True)
            if not any(path.is_relative_to(root) for root in roots):
                raise ValueError("Arquivo de skill fora das raízes permitidas.")
            with path.open("rb") as file:
                raw = file.read(MAX_SKILL_BYTES + 1)
            if not raw.strip():
                raise ValueError("Skill ou referência vazia.")
            # Referências/assets não listados aqui ficam explicitamente fora do envio.
            text = f"## Skill {name} / {relative}\n" + raw.decode("utf-8") + "\n"
            if relative == "SKILL.md":
                text += "Somente os arquivos identificados nesta requisição foram fornecidos; demais referências e assets não foram enviados.\n"
            total += len(text.encode("utf-8"))
            if total > MAX_SKILL_BYTES:
                raise ValueError("Skills maiores que o limite de contexto; selecione menos skills.")
            parts.append({"text": text})
            manifest.append({"name": name, "file": relative, "resolvedPath": str(path),
                             "sha256": hashlib.sha256(raw).hexdigest()})
    return parts, manifest

def authentication_context(cloud_shell):
    env = dict(os.environ)
    if cloud_shell:
        if env.get("CLOUD_SHELL") != "true":
            raise ValueError("Cloud Shell session required")
        gcloud = shutil.which("gcloud")
        if not gcloud:
            raise ValueError("gcloud unavailable")
        # A sessão oficial fornece identidade e runtime; não copiar o perfil do Mac.
        return gcloud, env, tempfile.gettempdir()
    home = Path.home()
    env["CLOUDSDK_CONFIG"] = str(home / ".config/safrion-gcloud")
    env["CLOUDSDK_PYTHON"] = str(home / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3")
    return str(home / ".local/share/safrion-google-cloud/google-cloud-sdk/bin/gcloud"), env, "/private/tmp"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Novo arquivo JSON de evidência (não sobrescreve).")
    parser.add_argument("--dry-run", action="store_true", help="Valida e mostra a requisição sem autenticar ou chamar API.")
    parser.add_argument("--cloud-shell", action="store_true", help="Usa gcloud e autenticação já disponíveis na sessão Cloud Shell, sem perfil local do Mac.")
    parser.add_argument("--skill", action="append", choices=sorted(SKILL_CATALOG), help="Carrega somente a skill necessária; pode repetir. Padrão: gcp-infra-essencial.")
    parser.add_argument("--list-skills", action="store_true", help="Lista as skills disponíveis sem autenticação ou API.")
    args = parser.parse_args()
    if args.list_skills:
        print(json.dumps({name:str(path) for name,path in SKILL_CATALOG.items()},ensure_ascii=False,indent=2))
        return 0
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES or not raw.strip():
        parser.error(f"Envie pelo stdin entre 1 e {MAX_INPUT_BYTES} bytes de contexto, sem segredos.")
    try:
        prompt = raw.decode("utf-8")
    except UnicodeDecodeError:
        parser.error("O texto precisa estar em UTF-8.")
    if args.output and (args.output.exists() or not args.output.parent.is_dir()):
        parser.error("O diretório de saída deve existir e o arquivo deve ser novo.")
    selected = list(dict.fromkeys(args.skill or ["gcp-infra-essencial"]))
    try:
        skill_parts, skill_manifest = load_skills(selected)
    except (OSError, ValueError):
        parser.error("Skill/referência inválida, inacessível ou acima do limite; nenhuma chamada foi enviada.")
    payload = {"systemInstruction":{"parts":[{"text":SYSTEM}, *skill_parts]},
               "contents":[{"role":"user","parts":[{"text":prompt}]}],
               "generationConfig":{"candidateCount":1,"maxOutputTokens":MAX_OUTPUT_TOKENS,
                                   "thinkingConfig":{"thinkingLevel":THINKING_LEVEL}}}
    if args.dry_run:
        print(json.dumps({"project":PROJECT,"model":MODEL,"skills":skill_manifest,"payload":payload},ensure_ascii=False,indent=2))
        return 0
    try:
        gcloud, env, auth_cwd = authentication_context(args.cloud_shell)
        auth = subprocess.run([gcloud,"auth","print-access-token"],env=env,cwd=auth_cwd,
                              capture_output=True,text=True,check=True,timeout=30)
        token = auth.stdout.strip()
        if not token:
            raise ValueError("empty token")
    except (subprocess.SubprocessError, OSError, ValueError):
        print("Falha ao obter autenticação do gcloud; nenhum token foi registrado.",file=sys.stderr)
        return 1
    url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/{MODEL}:generateContent"
    payload_bytes = json.dumps(payload).encode()
    request = urllib.request.Request(url,data=payload_bytes,
            headers={"Authorization":"Bearer "+token,"Content-Type":"application/json","X-Goog-User-Project":PROJECT},method="POST")
    record = {"at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"project":PROJECT,"modelRequested":MODEL,
              "generationConfig":payload["generationConfig"],"skills":skill_manifest,
              "payloadSha256":hashlib.sha256(payload_bytes).hexdigest(),
              "transportSha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "authenticationMode":"cloud-shell-session" if args.cloud_shell else "local-safrion-profile",
              "cloudShellEnvironment":env.get("CLOUD_SHELL") == "true",
              "runtime":{"system":platform.system(),"python":platform.python_version()}}
    try:
        with urllib.request.urlopen(request,timeout=180) as response:
            body = json.loads(response.read())
        candidates = body.get("candidates",[])
        candidate = candidates[0] if candidates else {}
        text = "\n".join(p["text"] for p in candidate.get("content",{}).get("parts",[]) if p.get("text") and not p.get("thought"))
        complete = bool(text.strip()) and candidate.get("finishReason") == "STOP"
        record.update(status="complete" if complete else "incomplete",text=text,
                      finishReason=candidate.get("finishReason"),modelVersion=body.get("modelVersion"),
                      usageMetadata=body.get("usageMetadata"),responseId=body.get("responseId"))
    except urllib.error.HTTPError as error:
        record.update(status="http_error",httpStatus=error.code)
        # Não grava resposta bruta que possa ecoar credenciais ou contexto sensível.
    except (TimeoutError, urllib.error.URLError, ValueError):
        record.update(status="connection_or_response_error")
    serialized = json.dumps(record,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        with args.output.open("x",encoding="utf-8") as file:
            os.chmod(args.output,0o600)
            file.write(serialized)
    print(serialized,end="")
    return 0 if record["status"] == "complete" else 1

if __name__ == "__main__":
    raise SystemExit(main())
