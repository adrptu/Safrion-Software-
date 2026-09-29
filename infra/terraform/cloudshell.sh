#!/usr/bin/env bash
# Bootstrap da HML pelo Cloud Shell do Google, sem depender de uma máquina local (ordem do proprietário, 29/09/2026).
# O Adrianus cola os comandos, guiado pelo Codex; o Claude responde pelo plan; as três IAs revisam pelo hash.
#
#   infra/terraform/cloudshell.sh conferir                  cópia = main atual do GitHub, com os 10 checks verdes
#   infra/terraform/cloudshell.sh state <projeto>           bucket do state do bootstrap, conferido no servidor
#   infra/terraform/cloudshell.sh planejar <projeto>        Terraform e TFLint pelo checksum, travas e plan
#   infra/terraform/cloudshell.sh aplicar <projeto> <hash>  aplica só o plano com esse SHA-256
#   infra/terraform/cloudshell.sh depois <projeto>          conta padrão do Compute e rede default, com s/n
#   infra/terraform/cloudshell.sh variaveis <projeto>       variáveis dos environments hml e hml-infra
#   infra/terraform/cloudshell.sh config-hml <projeto>      JSON privado da fase 1 para o infra-hml.yml (geração e SHA)
#   infra/terraform/cloudshell.sh senhas <projeto>          as 3 senhas do banco, sem eco; mostra só as versões
#   infra/terraform/cloudshell.sh destravar <projeto> <ID>  solta o lock do state deixado por uma sessão que caiu
#   infra/terraform/cloudshell.sh limpar <projeto>          apaga os arquivos locais do projeto
#
# Arquivos de trabalho (tfvars, plano, .terraform, saídas, logs) ficam em ~/.safrion/<projeto>, fora do checkout, só
# para o dono. Na tela vai só o que se cola no chat: hash, contagens e endereços, com e-mails mascarados, inclusive nos
# erros do gcloud e do gh. Senha só no subcomando senhas, depois da fase 1 do hml/: nasce e sai pela entrada padrão.
set -euo pipefail
umask 077

REPO_GH='adrptu/Safrion-Software-'
REGIAO='southamerica-east1'
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$AQUI/../.." && pwd)"
BOOT="$AQUI/bootstrap"
BASE="${SAFRION_DIR:-$HOME/.safrion}"
COPIA=''
# Agentes de serviço que o próprio Google cria no projeto (docs.cloud.google.com/iam/docs/service-agents), pelo
# número do projeto. Outro domínio, número ou conta com acesso ao Storage para a conferência.
AGENTES_GOOGLE='serverless-robot-prod gcp-sa-cloud-sql gcp-sa-artifactregistry gcp-sa-secretmanager compute-system service-networking gs-project-accounts gcp-sa-iap gcp-sa-logging'

falha() {
  echo "PARE: $*" >&2
  exit 1
}

mascarar() { sed -E 's/[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+)/***@\1/g'; }

# Erros de permissão do Google trazem o e-mail da conta ("<e-mail> doesn't have …"): só o stderr passa pela máscara,
# antes de o comando terminar, e o código de saída continua o do gcloud ou do gh (pipefail).
gcloud() { { command gcloud "$@" 2>&1 1>&3 3>&- | mascarar >&2; } 3>&1; }
gh() { { command gh "$@" 2>&1 1>&3 3>&- | mascarar >&2; } 3>&1; }

case "$BASE" in
  /*) ;;
  *) falha 'SAFRION_DIR precisa ser um caminho absoluto' ;;
esac
# Checagem pelo texto antes de criar qualquer pasta; a pelo caminho real (links) fica no projeto().
case "$BASE/" in
  "$RAIZ"/*) falha 'SAFRION_DIR não pode ficar dentro da cópia do repositório' ;;
esac

exigir() {
  local c
  for c in "$@"; do
    command -v "$c" >/dev/null || falha "comando $c não encontrado neste terminal (README do bootstrap, \"Ferramentas no Cloud Shell\")"
  done
}

projeto() {
  [[ "${1:-}" =~ ^[a-z][a-z0-9-]{4,28}[a-z0-9]$ ]] || falha "ID de projeto inválido: '${1:-}'"
  mkdir -p "$BASE"
  BASE="$(cd "$BASE" && pwd -P)"
  case "$BASE/" in
    "$(cd "$RAIZ" && pwd -P)"/*) falha 'SAFRION_DIR não pode ficar dentro da cópia do repositório' ;;
  esac
  DIR="$BASE/$1"
  mkdir -p "$DIR"
  chmod 700 "$BASE" "$DIR"
  # Um comando por vez neste projeto: outra aba não troca o plano enquanto este lê ou aplica.
  mkdir "$DIR/.trava" 2>/dev/null ||
    falha "outro comando do cloudshell.sh está em andamento neste projeto; se não estiver, apague ~/.safrion/$1/.trava"
  trap '[ -z "$COPIA" ] || rm -f "$COPIA"; rmdir "$DIR/.trava" 2>/dev/null || true' EXIT
}

confirmar() {
  local r='' resto
  # No terminal, linhas coladas junto com o comando anterior não viram resposta: o buffer é descartado antes da pergunta.
  if [ -t 0 ]; then
    while read -r -t 0.2 resto; do :; done
  fi
  read -r -p "$1 [s/n] " r || true
  case "$r" in
    s | S) return 0 ;;
    *) return 1 ;;
  esac
}

numero_do_projeto() {
  local n
  n="$(gcloud projects describe "$1" --format='value(projectNumber)')" || falha "não li o projeto $1"
  [[ "$n" =~ ^[1-9][0-9]{0,19}$ ]] || falha "número do projeto $1 ilegível"
  printf '%s' "$n"
}

conta_logada() {
  local c
  c="$(gcloud config get-value account 2>/dev/null)" || falha 'sem conta logada no gcloud'
  [[ "$c" =~ ^[^@[:space:]]+@[^@[:space:]]+$ ]] || falha 'sem conta logada no gcloud'
  printf '%s' "$c"
}

# Credencial de vida curta da conta logada no Cloud Shell, só no ambiente deste processo (R-006 §3: sem arquivo ADC).
token() {
  GOOGLE_OAUTH_ACCESS_TOKEN="$(gcloud auth print-access-token 2>/dev/null)" || falha 'sem login no gcloud'
  [ -n "$GOOGLE_OAUTH_ACCESS_TOKEN" ] || falha 'sem login no gcloud'
  export GOOGLE_OAUTH_ACCESS_TOKEN
}

# Nada herdado do shell muda o plano: TF_VAR_*, TF_CLI_ARGS* e ~/.terraformrc ficam de fora.
ambiente_tf() {
  local v
  for v in $(compgen -e); do
    case "$v" in
      TF_VAR_* | TF_CLI_ARGS* | TF_LOG* | TF_PLUGIN_CACHE_DIR | TF_WORKSPACE) unset "$v" ;;
    esac
  done
  : >"$DIR/terraformrc"
  export TF_CLI_CONFIG_FILE="$DIR/terraformrc" TF_DATA_DIR="$DIR/.terraform" TF_IN_AUTOMATION=1 TF_INPUT=0
  PATH="$DIR/bin:$PATH"
}

# Lock do state preso (sessão do Cloud Shell que caiu no meio): mostra o ID, que não é segredo, e o comando.
lock_preso() {
  local id
  grep -q 'Error acquiring the state lock' "$2" 2>/dev/null || return 0
  id="$(sed -n 's/^[[:space:]]*ID:[[:space:]]*\([0-9A-Za-z-]\{1,64\}\)[[:space:]]*$/\1/p' "$2" | head -1)"
  echo "O state do bootstrap está travado (ID ${id:-não lido}). Se nenhum outro comando estiver rodando:" >&2
  echo "  infra/terraform/cloudshell.sh destravar $1 ${id:-<ID>}" >&2
}

cmd_conferir() {
  exigir git gh python3
  local url ramo local_ remoto checks mudancas
  url="$(git -C "$RAIZ" remote get-url origin)"
  case "$url" in
    https://github.com/"$REPO_GH" | https://github.com/"$REPO_GH".git | git@github.com:"$REPO_GH".git) ;;
    *) falha "a cópia não é do $REPO_GH" ;;
  esac
  ramo="$(git -C "$RAIZ" rev-parse --abbrev-ref HEAD)"
  [ "$ramo" = main ] || falha "a cópia está em '$ramo', não na main"
  mudancas="$(git -C "$RAIZ" status --porcelain)" || falha 'não li o estado da cópia'
  [ -z "$mudancas" ] || falha 'a cópia tem mudanças locais'
  # O .gitignore esconde *.tfvars e *.auto.tfvars, que o Terraform carrega sozinho e mudariam o plano.
  mudancas="$(git -C "$RAIZ" status --porcelain --ignored -- infra/terraform/bootstrap infra/terraform/hml)" ||
    falha 'não li o estado da cópia'
  [ -z "$mudancas" ] || falha 'há arquivos ignorados pelo Git nos módulos do Terraform (tfvars?); tire-os antes'
  git -C "$RAIZ" fetch -q origin main
  local_="$(git -C "$RAIZ" rev-parse HEAD)"
  # A main de verdade vem do servidor, não do ref local, que um refspec trocado deixaria parado.
  remoto="$(gh api "repos/$REPO_GH/branches/main" --jq .commit.sha)" || falha 'não li a main no GitHub'
  [ "$local_" = "$remoto" ] || falha "a cópia ($local_) não é a main atual ($remoto): rode git pull"
  checks="$(mktemp)"
  gh api "repos/$REPO_GH/commits/$local_/check-runs?per_page=100" >"$checks" || falha 'não li os checks no GitHub'
  python3 - "$RAIZ/tools/github/protecao-main.json" "$checks" <<'PY' || falha "os checks obrigatórios não estão todos verdes em $local_"
import json, sys
regras = json.load(open(sys.argv[1], encoding='utf-8'))['rules']
exigidos = next(r for r in regras if r['type'] == 'required_status_checks')['parameters']['required_status_checks']
feitos = json.load(open(sys.argv[2], encoding='utf-8')).get('check_runs', [])
faltam = [c['context'] for c in exigidos
          if not any(r.get('name') == c['context'] and r.get('conclusion') == 'success'
                     and (r.get('app') or {}).get('id') == c['integration_id'] for r in feitos)]
for f in faltam:
    print(f'check sem success: {f}', file=sys.stderr)
sys.exit(1 if faltam else 0)
PY
  rm -f "$checks"
  echo "OK: main $local_, com os checks obrigatórios verdes."
}

cmd_state() {
  projeto "${1:-}"
  exigir gcloud python3
  local p="$1" b="gs://$1-tfstate-bootstrap" regras politica membro papel numero dono
  numero="$(numero_do_projeto "$p")"
  if ! gcloud storage buckets describe "$b" --format='value(name)' >/dev/null 2>"$DIR/describe.err"; then
    grep -qiE '404|not ?found' "$DIR/describe.err" || falha "não consegui ler $b (permissão ou rede); nada foi criado"
    gcloud storage buckets create "$b" --project="$p" --location="$REGIAO" \
      --uniform-bucket-level-access --public-access-prevention >/dev/null ||
      falha "não consegui criar $b (o nome pode já existir noutro projeto)"
    echo "Criado: $b"
  fi
  # Nome de bucket é global: só se mexe nele depois de confirmar que é deste projeto (inclusive numa retomada).
  dono="$(gcloud storage buckets describe "$b" --raw --format='value(projectNumber)')" || falha "não li $b; nada foi alterado"
  [ "$dono" = "$numero" ] || falha "o bucket $b não é do projeto $p; nada foi alterado"
  # Mesma regra do bucket do state da HML (bootstrap/main.tf): versões arquivadas além das 11 mais novas são apagadas.
  regras="$DIR/ciclo-de-vida.json"
  printf '%s\n' '{"lifecycle": {"rule": [{"action": {"type": "Delete"}, "condition": {"isLive": false, "numNewerVersions": 11}}]}}' >"$regras"
  gcloud storage buckets update "$b" --versioning --lifecycle-file="$regras" >/dev/null || falha "não consegui ajustar $b"
  # Vínculos de conveniência de editor e leitor do projeto saem, só os presentes: fica só o dono.
  politica="$DIR/politica-state.json"
  gcloud storage buckets get-iam-policy "$b" --format=json >"$politica" || falha "não li o IAM de $b"
  python3 - "$politica" >"$DIR/vinculos-a-tirar.txt" <<'PY'
import json, sys
for b in json.load(open(sys.argv[1], encoding='utf-8')).get('bindings', []):
    for m in b.get('members', []):
        if m.startswith(('projectEditor:', 'projectViewer:')):
            print(m, b['role'])
PY
  while read -r membro papel; do
    [ -n "$membro" ] || continue
    gcloud storage buckets remove-iam-policy-binding "$b" --member="$membro" --role="$papel" >/dev/null ||
      falha "não consegui tirar $membro de $b"
  done <"$DIR/vinculos-a-tirar.txt"
  verificar_state "$p"
  echo "OK: $b do projeto $p, com acesso uniforme, sem acesso público, versionado, sem pasta gerenciada e só o dono no IAM."
  echo "No IAM do projeto, fora o dono e os agentes do Google listados, ninguém alcança objetos, muda IAM ou gera credencial"
  echo "de conta de serviço. A conferência não cobre abuso dos próprios agentes do Google."
}

# Só leitura: o bucket é do projeto, está como o README exige, e ninguém além do dono alcança objetos, nem pelo bucket,
# nem por pasta gerenciada, nem pelo projeto.
verificar_state() {
  local p="$1" b="gs://$1-tfstate-bootstrap" numero descricao politica pastas
  numero="$(numero_do_projeto "$p")"
  descricao="$DIR/state.json"
  politica="$DIR/politica-state.json"
  gcloud storage buckets describe "$b" --raw --format=json >"$descricao" || falha "não li $b: rode state"
  gcloud storage buckets get-iam-policy "$b" --format=json >"$politica" || falha "não li o IAM de $b"
  pastas="$(gcloud storage managed-folders list "$b/" --format='value(name)')" ||
    falha "não consegui listar as pastas gerenciadas de $b"
  [ -z "$pastas" ] || falha "$b tem pasta gerenciada, com IAM próprio; o state não fica só com o dono"
  python3 - "$descricao" "$politica" "$p" "$numero" <<'PY' || falha "o bucket $b não está como o README exige; nada foi planejado"
import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
p = json.load(open(sys.argv[2], encoding='utf-8'))
projeto, numero = sys.argv[3], sys.argv[4]
erros = []
if str(d.get('projectNumber')) != numero:
    erros.append('o bucket não é deste projeto')
iam = d.get('iamConfiguration') or {}
if (iam.get('uniformBucketLevelAccess') or {}).get('enabled') is not True:
    erros.append('acesso uniforme desligado')
if iam.get('publicAccessPrevention') != 'enforced':
    erros.append('prevenção de acesso público não está enforced')
if (d.get('versioning') or {}).get('enabled') is not True:
    erros.append('versionamento desligado')
outros = {m for b in p.get('bindings', []) for m in b.get('members', []) if m != f'projectOwner:{projeto}'}
if outros:
    erros.append(f'{len(outros)} membro(s) além do dono do projeto')
for e in erros:
    print(e, file=sys.stderr)
sys.exit(1 if erros else 0)
PY
  iam_efetivo "$p" "$numero"
}

# O IAM do bucket não mostra o acesso que vem do projeto (revisão do Codex no PR #20). Sem pasta nem organização acima,
# o projeto é a única herança. Para quem não é o dono nem agente de serviço do Google deste projeto, cada papel é
# expandido (básico, predefinido ou customizado), e para o que dá objetos, IAM do bucket ou do projeto, ou muda papéis.
# O dono só pode ser um: outro roles/owner alcançaria o bucket pelos valores de conveniência.
iam_efetivo() {
  local p="$1" numero="$2" conta pai politica papeis papel alvo primeiro=1
  conta="$(conta_logada)"
  pai="$(gcloud projects describe "$p" --format='value(parent.type)')" || falha "não li o projeto $p"
  [ -z "$pai" ] || falha "o projeto tem $pai acima: o acesso herdado ao state não é conferível daqui"
  politica="$DIR/politica-projeto.json"
  papeis="$DIR/papeis-expandidos.json"
  gcloud projects get-iam-policy "$p" --format=json >"$politica" || falha "não li o IAM do projeto $p"
  python3 - "$politica" "user:$conta" "$numero" "$AGENTES_GOOGLE" >"$DIR/papeis-a-expandir.txt" <<'PY'
import json, sys
dono, numero, dominios = sys.argv[2], sys.argv[3], sys.argv[4].split()
agentes = {f'serviceAccount:{numero}@cloudservices.gserviceaccount.com'} | \
          {f'serviceAccount:service-{numero}@{d}.iam.gserviceaccount.com' for d in dominios}
papeis = sorted({b['role'] for b in json.load(open(sys.argv[1], encoding='utf-8')).get('bindings', [])
                 for m in b.get('members', []) if m != dono and m not in agentes})
print('\n'.join(papeis))
PY
  printf '{' >"$papeis"
  while read -r papel; do
    [ -n "$papel" ] || continue
    [ "$primeiro" = 1 ] || printf ',' >>"$papeis"
    primeiro=0
    printf '"%s":' "$papel" >>"$papeis"
    case "$papel" in
      projects/*/roles/*)
        alvo="${papel#projects/}"
        gcloud iam roles describe "${papel##*/}" --project="${alvo%%/*}" --format=json >>"$papeis"
        ;;
      organizations/*/roles/*)
        alvo="${papel#organizations/}"
        gcloud iam roles describe "${papel##*/}" --organization="${alvo%%/*}" --format=json >>"$papeis"
        ;;
      *) gcloud iam roles describe "$papel" --format=json >>"$papeis" ;;
    esac || falha "não li as permissões do papel $papel"
  done <"$DIR/papeis-a-expandir.txt"
  printf '}\n' >>"$papeis"
  python3 - "$politica" "$papeis" "user:$conta" "$numero" "$AGENTES_GOOGLE" <<'PY' || falha 'alguém além do dono alcança o state pelo projeto; nada foi planejado'
import json, sys
politica = json.load(open(sys.argv[1], encoding='utf-8'))
papeis = json.load(open(sys.argv[2], encoding='utf-8'))
dono, numero, dominios = sys.argv[3], sys.argv[4], sys.argv[5].split()
agentes = {f'serviceAccount:{numero}@cloudservices.gserviceaccount.com'} | \
          {f'serviceAccount:service-{numero}@{d}.iam.gserviceaccount.com' for d in dominios}
# Acesso indireto: mudar IAM ou papéis, ou agir como conta de serviço (token, assinatura, chave, actAs, federação),
# conforme docs.cloud.google.com/iam/docs/service-account-permissions.
perigosas = {'storage.buckets.setIamPolicy', 'resourcemanager.projects.setIamPolicy', 'iam.roles.update',
             'iam.serviceAccounts.getAccessToken', 'iam.serviceAccounts.getOpenIdToken',
             'iam.serviceAccounts.implicitDelegation', 'iam.serviceAccounts.signBlob', 'iam.serviceAccounts.signJwt',
             'iam.serviceAccounts.actAs', 'iam.serviceAccounts.setIamPolicy', 'iam.serviceAccountKeys.create',
             'iam.workloadIdentityPoolProviders.create', 'iam.workloadIdentityPoolProviders.update'}
compute = f'serviceAccount:{numero}-compute@developer.gserviceaccount.com'
erros, pulados = 0, set()
for b in politica.get('bindings', []):
    papel = b['role']
    for m in b.get('members', []):
        if m == dono:
            continue
        if m in agentes:
            pulados.add(m.split('@', 1)[1])
            continue
        perms = papeis.get(papel, {}).get('includedPermissions', [])
        if (papel == 'roles/owner' or papel.startswith('roles/storage.')
                or any(x.startswith(('storage.objects.', 'storage.managedFolders.')) or x in perigosas for x in perms)):
            dica = ' (conta padrão do Compute: rode depois antes)' if m == compute else ''
            print(f'{m.split(":", 1)[0]} com {papel} alcança o state ou pode se dar acesso{dica}', file=sys.stderr)
            erros += 1
for d in sorted(pulados):
    print(f'agente de serviço do Google ({d}): gerenciado pelo Google, fora da conferência')
sys.exit(1 if erros else 0)
PY
}

# Terraform e TFLint nas versões e com os SHA-256 fixados no infra.yml (a mesma fonte da CI), sem depender de unzip.
ferramentas() {
  exigir curl sha256sum python3
  [ "$(uname -m)" = x86_64 ] || falha "arquitetura $(uname -m) sem binário conferido no infra.yml"
  local nome versao sha url
  mkdir -p "$DIR/bin"
  python3 - "$RAIZ/.github/workflows/infra.yml" >"$DIR/ferramentas.txt" <<'PY' || falha 'versões ou SHA-256 ausentes no infra.yml'
import re, sys
t = open(sys.argv[1], encoding='utf-8').read()
v = {k: re.search(rf'^\s*{k}:\s*"?([^"\s]+)"?\s*$', t, re.M) for k in
     ('TERRAFORM_VERSAO', 'TERRAFORM_SHA256', 'TFLINT_VERSAO', 'TFLINT_SHA256')}
if not all(v.values()):
    sys.exit(1)
print('terraform', v['TERRAFORM_VERSAO'][1], v['TERRAFORM_SHA256'][1])
print('tflint', v['TFLINT_VERSAO'][1], v['TFLINT_SHA256'][1])
PY
  while read -r nome versao sha; do
    if [ "$nome" = terraform ]; then
      url="https://releases.hashicorp.com/terraform/${versao}/terraform_${versao}_linux_amd64.zip"
    else
      url="https://github.com/terraform-linters/tflint/releases/download/${versao}/tflint_linux_amd64.zip"
    fi
    curl --fail --silent --show-error --location --retry 3 --connect-timeout 15 --max-time 120 \
      --output "$DIR/$nome.zip" "$url" || falha "não baixei o $nome"
    printf '%s  %s\n' "$sha" "$DIR/$nome.zip" | sha256sum --check --quiet - || falha "SHA-256 do $nome diferente do infra.yml"
    rm -f "$DIR/bin/$nome"
    python3 -c 'import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extract(sys.argv[2], sys.argv[3])' \
      "$DIR/$nome.zip" "$nome" "$DIR/bin" || falha "não extraí o $nome"
    chmod 700 "$DIR/bin/$nome"
    sha256sum "$DIR/bin/$nome" | cut -d' ' -f1 >"$DIR/bin/$nome.sha256"
    rm -f "$DIR/$nome.zip"
  done <"$DIR/ferramentas.txt"
}

# O terraform extraído no planejar é o mesmo que roda depois.
terraform_conferido() {
  [ -x "$DIR/bin/terraform" ] && [ -f "$DIR/bin/terraform.sha256" ] || return 1
  [ "$(sha256sum "$DIR/bin/terraform" | cut -d' ' -f1)" = "$(cat "$DIR/bin/terraform.sha256")" ]
}

# Terraform pronto para ler o state do bootstrap: ferramentas conferidas, credencial curta, ambiente limpo e init.
preparar_tf() {
  local p="$1"
  terraform_conferido || ferramentas
  token
  ambiente_tf
  (
    cd "$BOOT"
    terraform init -input=false -lockfile=readonly -no-color -backend-config="bucket=$p-tfstate-bootstrap" >"$DIR/init.log" 2>&1 ||
      falha "terraform init falhou (detalhes só no seu terminal: ~/.safrion/$p/init.log)"
  )
}

tfvars() {
  local p="$1" repo_id dono_id conta agentes='' email="${SAFRION_AGENTES:-}"
  repo_id="$(gh api "repos/$REPO_GH" --jq .id)" || falha 'não li o repositório no GitHub'
  dono_id="$(gh api "repos/$REPO_GH" --jq .owner.id)" || falha 'não li o repositório no GitHub'
  conta="$(conta_logada)"
  [[ "$repo_id" =~ ^[0-9]+$ && "$dono_id" =~ ^[0-9]+$ ]] || falha 'não li os IDs do repositório no GitHub'
  # Conta Google dos agentes (roteiro, D06), se já existir e a decisão E03 a mantiver. Perguntada aqui, e não na linha
  # de comando, para o e-mail não ficar no histórico do shell.
  if [ -z "$email" ] && [ -t 0 ]; then
    read -r -p 'E-mail da conta Google dos agentes (Enter se ainda não existe): ' email || true
  fi
  if [ -n "$email" ]; then
    [[ "$email" =~ ^[^@[:space:],\"]+@[^@[:space:],\"]+$ ]] || falha 'e-mail da conta dos agentes inválido'
    agentes="\"user:$email\""
  fi
  cat >"$DIR/bootstrap.tfvars" <<EOF
projeto_id           = "$p"
github_repositorio   = "$REPO_GH"
github_repository_id = "$repo_id"
github_owner_id      = "$dono_id"
operador             = "user:$conta"
agentes              = [$agentes]
EOF
}

resumo() {
  terraform show -json "$1" | python3 -c '
import json, sys
p = json.load(sys.stdin)
conta = {"create": 0, "update": 0, "delete": 0}
linhas = []
for m in p.get("resource_changes", []):
    a = m["change"]["actions"]
    if a == ["no-op"] or a == ["read"]:
        continue
    for x in a:
        conta[x] = conta.get(x, 0) + 1
    linhas.append("/".join(a) + " " + m["address"])
print("Criar {create} · mudar {update} · destruir {delete}".format(**conta))
print("\n".join(sorted(linhas)))
if conta["delete"]:
    print("ATENÇÃO: o plan destrói recursos; não aplicar sem revisão específica (README.md, antes de cada apply).")
' | mascarar
}

cmd_planejar() {
  projeto "${1:-}"
  local p="$1" commit hash novo="$DIR/bootstrap.tfplan.novo"
  # Um plano anterior não sobrevive a um planejar que pare no meio: o hash na tela é sempre o do plano que existe.
  rm -f "$DIR/bootstrap.tfplan" "$DIR/bootstrap.tfplan.sha256" "$DIR/resumo.txt" "$novo"
  cmd_conferir
  commit="$(git -C "$RAIZ" rev-parse HEAD)"
  exigir gcloud gh
  verificar_state "$p"
  ferramentas
  tfvars "$p"
  preparar_tf "$p"
  (
    cd "$BOOT"
    terraform fmt -check -recursive >/dev/null || falha 'formatação do Terraform'
    terraform validate -no-color >/dev/null || falha 'terraform validate'
    tflint --config=/dev/null --enable-plugin=terraform --no-color >/dev/null || falha 'TFLint'
  )
  python3 "$AQUI/checar_travas.py" >/dev/null || falha 'checar_travas.py recusou o código'
  (
    cd "$BOOT"
    terraform plan -input=false -lock-timeout=60s -no-color -var-file="$DIR/bootstrap.tfvars" \
      -out="$novo" >"$DIR/plan.log" 2>&1 || {
      lock_preso "$p" "$DIR/plan.log"
      falha "terraform plan falhou (detalhes só no seu terminal: ~/.safrion/$p/plan.log)"
    }
  )
  # Hash e resumo saem do mesmo arquivo, que só então vira o plano da revisão.
  hash="$(sha256sum "$novo" | cut -d' ' -f1)"
  (cd "$BOOT" && resumo "$novo") >"$DIR/resumo.txt"
  mv "$novo" "$DIR/bootstrap.tfplan"
  printf '%s  %s\n' "$hash" "$commit" >"$DIR/bootstrap.tfplan.sha256"
  echo "Plano do bootstrap · projeto $p · commit $commit"
  echo "SHA-256: $hash"
  cat "$DIR/resumo.txt"
  echo 'Cole estas linhas no chat. Aplicar só depois dos pareceres pelo hash, com o comando:'
  echo "  infra/terraform/cloudshell.sh aplicar $p $hash"
}

cmd_aplicar() {
  projeto "${1:-}"
  local p="$1" esperado="${2:-}" real
  [[ "$esperado" =~ ^[0-9a-f]{64}$ ]] || falha 'informe o SHA-256 aprovado (64 caracteres hexadecimais)'
  [ -f "$DIR/bootstrap.tfplan" ] || falha "sem plano em ~/.safrion/$p: rode planejar"
  # O apply recebe uma cópia privada, conferida pelo hash: o arquivo original pode mudar, a cópia não.
  COPIA="$(mktemp "$DIR/aplicar.XXXXXX")"
  cp "$DIR/bootstrap.tfplan" "$COPIA"
  real="$(sha256sum "$COPIA" | cut -d' ' -f1)"
  [ "$real" = "$esperado" ] || falha "o plano local tem outro SHA-256 ($real); nada foi aplicado"
  terraform_conferido || falha 'o Terraform local mudou desde o planejar; rode planejar de novo'
  exigir gcloud python3
  verificar_state "$p"
  preparar_tf "$p"
  echo 'Aplicando. Não feche esta aba até o fim.'
  (
    cd "$BOOT"
    terraform apply -input=false -lock-timeout=60s -no-color "$COPIA" >"$DIR/apply.log" 2>&1 || {
      lock_preso "$p" "$DIR/apply.log"
      falha "terraform apply falhou (detalhes só no seu terminal: ~/.safrion/$p/apply.log)"
    }
  )
  rm -f "$DIR/bootstrap.tfplan"
  echo "Aplicado o plano $esperado no projeto $p."
  if (cd "$BOOT" && terraform output -json >"$DIR/saidas.json" 2>/dev/null); then
    echo 'Agora, um comando por vez:'
  else
    echo 'As saídas não foram lidas agora; o variaveis as lê de novo. Agora, um comando por vez:'
  fi
  echo "  infra/terraform/cloudshell.sh depois $p"
  echo "  infra/terraform/cloudshell.sh variaveis $p"
}

# Saídas do bootstrap lidas do state (só leitura), sem depender de um arquivo do aplicar.
saidas() {
  preparar_tf "$1"
  (cd "$BOOT" && terraform output -json >"$DIR/saidas.json" 2>"$DIR/output.log") ||
    falha "não li as saídas do bootstrap (detalhes só no seu terminal: ~/.safrion/$1/output.log)"
}

cmd_depois() {
  projeto "${1:-}"
  exigir gcloud python3
  local p="$1" numero conta existe regras r redes
  numero="$(numero_do_projeto "$p")"
  conta="$numero-compute@developer.gserviceaccount.com"
  existe="$(gcloud iam service-accounts list --project="$p" --filter="email=$conta" --format='value(email)')" ||
    falha 'não consegui listar as contas de serviço'
  if [ -n "$existe" ]; then
    if confirmar 'A conta padrão do Compute existe. Tirar o papel Editor dela e desativá-la?'; then
      gcloud projects get-iam-policy "$p" --format=json >"$DIR/politica-projeto.json" || falha "não li o IAM do projeto $p"
      if python3 - "$DIR/politica-projeto.json" "serviceAccount:$conta" <<'PY'; then
import json, sys
p = json.load(open(sys.argv[1], encoding='utf-8'))
sys.exit(0 if any(b['role'] == 'roles/editor' and sys.argv[2] in b.get('members', []) for b in p.get('bindings', [])) else 1)
PY
        gcloud projects remove-iam-policy-binding "$p" --member="serviceAccount:$conta" --role=roles/editor \
          --condition=None >/dev/null || falha 'não consegui tirar o Editor da conta padrão do Compute'
      fi
      gcloud iam service-accounts disable "$conta" --project="$p" >/dev/null || falha 'não consegui desativar a conta padrão do Compute'
      gcloud projects get-iam-policy "$p" --format=json >"$DIR/politica-projeto.json" || falha "não li o IAM do projeto $p"
      python3 - "$DIR/politica-projeto.json" "serviceAccount:$conta" <<'PY' || falha 'a conta padrão do Compute ainda tem Editor'
import json, sys
p = json.load(open(sys.argv[1], encoding='utf-8'))
sys.exit(1 if any(b['role'] == 'roles/editor' and sys.argv[2] in b.get('members', []) for b in p.get('bindings', [])) else 0)
PY
      [ "$(gcloud iam service-accounts describe "$conta" --project="$p" --format='value(disabled)')" = True ] ||
        falha 'a conta padrão do Compute não ficou desativada'
      echo 'Conta padrão do Compute: sem Editor e desativada (conferido).'
    else
      echo 'Conta padrão do Compute: mantida (resposta diferente de s).'
    fi
  else
    echo 'Conta padrão do Compute: não existe.'
  fi
  redes="$(gcloud compute networks list --project="$p" --filter='name=default' --format='value(name)')" ||
    falha 'não consegui listar as redes do projeto'
  if [ -n "$redes" ]; then
    regras="$(gcloud compute firewall-rules list --project="$p" --filter='network~/default$' --format='value(name)')" ||
      falha 'não consegui listar as regras de firewall'
    if confirmar "A rede default existe, com $(printf '%s' "$regras" | grep -c . || true) regra(s) de firewall. Apagar as regras e a rede?"; then
      for r in $regras; do
        gcloud compute firewall-rules delete "$r" --project="$p" --quiet >/dev/null || falha "não consegui apagar a regra $r"
      done
      gcloud compute networks delete default --project="$p" --quiet >/dev/null || falha 'não consegui apagar a rede default'
      redes="$(gcloud compute networks list --project="$p" --filter='name=default' --format='value(name)')" ||
        falha 'não consegui conferir a rede default depois de apagar'
      [ -z "$redes" ] || falha 'a rede default continua no projeto'
      echo 'Rede default: apagada (conferido).'
    else
      echo 'Rede default: mantida (resposta diferente de s).'
    fi
  else
    echo 'Rede default: não existe.'
  fi
}

cmd_variaveis() {
  projeto "${1:-}"
  local p="$1" numero
  exigir gcloud python3
  numero="$(numero_do_projeto "$p")"
  saidas "$p"
  python3 - "$DIR/saidas.json" "$p" "$REGIAO" "$numero" <<'PY'
import json, sys
s = {k: v['value'] for k, v in json.load(open(sys.argv[1], encoding='utf-8')).items()}
projeto, regiao, numero = sys.argv[2:5]
print('Environment hml (variáveis, nenhuma é segredo):')
for k, v in (('WIF_PROVIDER', s['wif_provider']), ('DEPLOY_SA', s['sa_deploy_github']),
             ('GCP_PROJECT_ID', projeto), ('GCP_REGION', regiao)):
    print(f'  {k} = {v}')
print('Environment hml-infra (variável, não é segredo):')
print(f'  HML_PROJECT_NUMBER = {numero}')
print('Os valores da fase 1 vão no JSON privado do bucket, com o comando:')
print(f'  infra/terraform/cloudshell.sh config-hml {projeto}')
PY
}

# JSON privado da fase 1 que o infra-hml.yml lê pela geração e pelo SHA-256 (tools/hml/README.md), a partir das saídas
# do bootstrap e da conta logada. Destino e aceitação vêm do próprio tools/hml/planejar.py (PROJETO e validar_config),
# fonte única com o workflow. Grava uma vez; nunca sobrescreve outra versão; relê pela geração antes de dar os valores.
cmd_config_hml() {
  projeto "${1:-}"
  local p="$1" objeto numero conta sha geracao lida novo=0
  exigir gcloud python3 sha256sum
  [ -f "$RAIZ/tools/hml/planejar.py" ] || falha 'tools/hml/planejar.py ausente nesta cópia: atualize a main'
  numero="$(numero_do_projeto "$p")"
  conta="$(conta_logada)"
  saidas "$p"
  # -B: o import não deixa __pycache__ na cópia nem reaproveita bytecode de outra versão do planejar.py.
  python3 -B - "$RAIZ/tools/hml" "$DIR/saidas.json" "$p" "$numero" "user:$conta" "$DIR/hml.tfvars.json" <<'PY' ||
import hashlib, json, sys
sys.path.insert(0, sys.argv[1])
import planejar
projeto, numero, operador, destino = sys.argv[3:7]
if projeto != planejar.PROJETO:
    print(f'o infra-hml.yml só planeja o projeto {planejar.PROJETO}; este é {projeto}', file=sys.stderr)
    sys.exit(1)
s = {k: v['value'] for k, v in json.load(open(sys.argv[2], encoding='utf-8')).items()}
cfg = {'projeto_id': projeto, 'projeto_numero': numero, 'rede_self_link': s.get('rede_self_link'),
       'subrede_self_link': s.get('subrede_self_link'), 'faixa_psa_nome': s.get('faixa_psa_nome'),
       'operador': operador, 'criar_cloud_run': False}
raw = (json.dumps(cfg, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
try:
    planejar.validar_config(raw, {'config_sha': hashlib.sha256(raw).hexdigest(), 'projeto_numero': numero})
except planejar.Recusa as e:
    print(f'validar_config do tools/hml/planejar.py recusou: {e}', file=sys.stderr)
    sys.exit(1)
open(destino, 'wb').write(raw)
PY
    falha 'a configuração da fase 1 não passou na conferência; nada foi gravado'
  sha="$(sha256sum "$DIR/hml.tfvars.json" | cut -d' ' -f1)"
  objeto="gs://$p-tfstate-hml/config/hml.tfvars.json"
  if ! geracao="$(gcloud storage objects describe "$objeto" --format='value(generation)' 2>"$DIR/objeto.err")" || [ -z "$geracao" ]; then
    grep -qiE '404|not ?found' "$DIR/objeto.err" || falha "não consegui ler $objeto (permissão ou rede)"
    gcloud storage cp "$DIR/hml.tfvars.json" "$objeto" --if-generation-match=0 >/dev/null || falha "não gravei $objeto"
    geracao="$(gcloud storage objects describe "$objeto" --format='value(generation)')" || falha "não li $objeto"
    novo=1
  fi
  [[ "$geracao" =~ ^[1-9][0-9]{0,19}$ ]] || falha 'geração da configuração ilegível'
  lida="$DIR/config-lida.json"
  rm -f "$lida"
  gcloud storage cp "$objeto#$geracao" "$lida" >/dev/null || falha "não li $objeto na geração $geracao"
  if [ "$(sha256sum "$lida" | cut -d' ' -f1)" != "$sha" ]; then
    [ "$novo" = 1 ] || falha "já existe outra configuração ($objeto, geração $geracao); revise antes de substituir"
    falha "a configuração lida do bucket (geração $geracao) difere da gravada; não use estes valores"
  fi
  echo 'Configuração da fase 1 no bucket da HML, relida pela geração (tem o seu e-mail: não cole o arquivo no chat).'
  echo "Entradas do infra-hml.yml: config_generation = $geracao · config_sha256 = $sha"
}

# Senhas do banco da HML (R-006, passo 4; roteiro E09), depois da fase 1, que cria a instância e os segredos sem versão.
# Cada senha nasce aqui (openssl, 32 hexadecimais) e só passa pela entrada padrão: nunca em argumento, eco, arquivo ou
# log, e ninguém a lê de volta (sem `secrets versions access`). Segredo com versão ativa fica como está; só com
# versão desativada, o comando para sem gerar nem reativar.
# A do admin troca primeiro a senha do postgres e só depois vira versão do segredo. Se a troca não se confirmar ou a
# gravação falhar, o postgres pode ficar com uma senha não guardada até rodar de novo, que gera outra e troca de novo.
# A troca vai pela API REST do Cloud SQL (users.update), com o
# corpo pela entrada padrão: o --prompt-for-password do gcloud lê do terminal, não de um pipe.
SEGREDOS_BANCO='hml-db-admin-senha hml-db-migrator-senha hml-db-app-runtime-senha'
INSTANCIA='safrion-hml'

senha_postgres() {
  local p="$1" cabecalho="$DIR/cabecalho-sql" resposta="$DIR/sql-users.json" operacao
  token
  # O token vai num arquivo privado lido pelo curl (-H @arquivo), não em argumento visível no ps.
  printf 'Authorization: Bearer %s\n' "$GOOGLE_OAUTH_ACCESS_TOKEN" >"$cabecalho"
  if ! printf '{"password": "%s"}' "$2" | curl --fail --silent --show-error --connect-timeout 15 --max-time 120 \
    -X PUT -H @"$cabecalho" -H 'Content-Type: application/json' --data-binary @- --output "$resposta" \
    "https://sqladmin.googleapis.com/v1/projects/$p/instances/$INSTANCIA/users?name=postgres" 2>"$DIR/sql-users.err"; then
    rm -f "$cabecalho"
    mascarar <"$DIR/sql-users.err" >&2
    return 1
  fi
  rm -f "$cabecalho"
  operacao="$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1], encoding="utf-8")).get("name", ""))' "$resposta")" ||
    return 1
  [[ "$operacao" =~ ^[A-Za-z0-9-]{1,100}$ ]] || return 1
  gcloud sql operations wait "$operacao" --project="$p" --timeout=300 >/dev/null
}

# Situação de um segredo: "ativa N", "desativada N" ou "vazia". Só versão ativa conta como pronta: a desativada não
# serve à web nem aos jobs, e gerar outra por cima dela esconderia o motivo de ela ter sido desativada.
situacao_do_segredo() {
  # $3 = "inicial" na conferência antes de gerar, quando ainda é verdade que nada foi gerado.
  local p="$1" s="$2" versoes nome estado ativa='' desativada='' sufixo=''
  [ "${3:-}" != inicial ] || sufixo='; nada foi gerado'
  versoes="$(gcloud secrets versions list "$s" --project="$p" --filter='state!=DESTROYED' --format='value(name,state)')" ||
    falha "não li as versões de $s$sufixo"
  while read -r nome estado; do
    [ -n "$nome" ] || continue
    case "$estado" in
      ENABLED) [ -n "$ativa" ] || ativa="${nome##*/}" ;;
      *) desativada="${nome##*/}" ;;
    esac
  done <<<"$versoes"
  if [ -n "$ativa" ]; then
    echo "ativa $ativa"
  elif [ -n "$desativada" ]; then
    echo "desativada $desativada"
  else
    echo vazia
  fi
}

senha_do_segredo() {
  local p="$1" s="$2" situacao senha versao
  # Relida na hora de gerar: entre a conferência inicial e aqui, outra sessão pode ter mudado o segredo.
  situacao="$(situacao_do_segredo "$p" "$s")"
  case "$situacao" in
    ativa\ *)
      echo "$s: já tem a versão ${situacao#ativa } ativa; mantida, sem gerar outra."
      return 0
      ;;
    desativada\ *) falha "$s passou a ter só versão desativada (${situacao#desativada }); pare e confira no Secret Manager" ;;
  esac
  senha="$(openssl rand -hex 16)" || falha 'o openssl não gerou a senha'
  [[ "$senha" =~ ^[0-9a-f]{32}$ ]] || falha 'o openssl não gerou a senha'
  if [ "$s" = hml-db-admin-senha ]; then
    senha_postgres "$p" "$senha" ||
      falha 'não confirmei a troca da senha do postgres; o segredo não foi gravado. Confira a operação no Cloud SQL e rode senhas de novo'
  fi
  versao="$(printf %s "$senha" | gcloud secrets versions add "$s" --project="$p" --data-file=- --format='value(name)')" ||
    falha "não confirmei a gravação da versão de $s; rode senhas de novo: versão ativa já gravada é preservada, e só o que faltar é gerado"
  senha=''
  versao="${versao##*/}"
  [[ "$versao" =~ ^[1-9][0-9]{0,5}$ ]] || falha "versão de $s ilegível"
  echo "$s: versão $versao"
}

cmd_senhas() {
  projeto "${1:-}"
  local p="$1" s estado
  # Com rastreamento (bash -x ou SHELLOPTS), a senha apareceria no terminal.
  case "$-" in
    *x*) falha 'rode sem -x: o rastreamento mostraria as senhas' ;;
  esac
  exigir gcloud curl python3 openssl
  estado="$(gcloud sql instances describe "$INSTANCIA" --project="$p" --format='value(state)')" ||
    falha "não li a instância $INSTANCIA: aplique a fase 1 do hml/ antes"
  [ "$estado" = RUNNABLE ] || falha "a instância $INSTANCIA está em '$estado', não RUNNABLE"
  for s in $SEGREDOS_BANCO; do
    gcloud secrets describe "$s" --project="$p" --format='value(name)' >/dev/null ||
      falha "segredo $s ausente: aplique a fase 1 do hml/ antes"
  done
  # Antes de gerar qualquer senha: um segredo só com versão desativada para tudo, sem mudar nada.
  local situacao bloqueados=''
  for s in $SEGREDOS_BANCO; do
    situacao="$(situacao_do_segredo "$p" "$s" inicial)"
    case "$situacao" in
      desativada\ *) bloqueados="$bloqueados $s (versão ${situacao#desativada })" ;;
    esac
  done
  [ -z "$bloqueados" ] ||
    falha "só com versão desativada:$bloqueados. Reative ou destrua no Secret Manager antes; nada foi gerado"
  confirmar 'Gerar as 3 senhas do banco da HML sem eco? A do admin também troca a senha do postgres.' ||
    falha 'nada foi gerado'
  for s in $SEGREDOS_BANCO; do
    senha_do_segredo "$p" "$s"
  done
  echo 'Nenhuma senha foi mostrada nem lida de volta. Cole no chat só os números das versões acima: vão para'
  echo 'versoes_segredos da fase 2 (admin, migrator, app_runtime; oidc é a versão criada no console).'
}

cmd_destravar() {
  projeto "${1:-}"
  local p="$1" id="${2:-}"
  [[ "$id" =~ ^[0-9A-Za-z-]{1,64}$ ]] || falha 'informe o ID do lock mostrado pelo planejar ou pelo aplicar'
  confirmar "Soltar o lock $id do state do bootstrap? Só faça isso se nenhum outro comando estiver rodando." ||
    falha 'lock mantido'
  exigir gcloud
  preparar_tf "$p"
  (cd "$BOOT" && terraform force-unlock -force "$id" >"$DIR/destravar.log" 2>&1) ||
    falha "não soltei o lock (detalhes só no seu terminal: ~/.safrion/$p/destravar.log)"
  echo "Lock $id solto. Rode de novo o comando que tinha caído."
}

cmd_limpar() {
  projeto "${1:-}"
  rm -rf "${DIR:?}"
  echo "Apagado ~/.safrion/$1 (plano, tfvars, .terraform, saídas e logs). O state continua no bucket."
  echo 'Ao encerrar a janela: gh auth logout --hostname github.com e revogar o gcloud (README do bootstrap).'
}

uso() {
  sed -n '5,14p' "${BASH_SOURCE[0]}" | sed 's/^#   //'
  exit 2
}

case "${1:-}" in
  conferir) cmd_conferir ;;
  state) cmd_state "${2:-}" ;;
  planejar) cmd_planejar "${2:-}" ;;
  aplicar) cmd_aplicar "${2:-}" "${3:-}" ;;
  depois) cmd_depois "${2:-}" ;;
  variaveis) cmd_variaveis "${2:-}" ;;
  config-hml) cmd_config_hml "${2:-}" ;;
  senhas) cmd_senhas "${2:-}" ;;
  destravar) cmd_destravar "${2:-}" "${3:-}" ;;
  limpar) cmd_limpar "${2:-}" ;;
  *) uso ;;
esac
