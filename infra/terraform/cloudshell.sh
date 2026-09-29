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
#   infra/terraform/cloudshell.sh limpar <projeto>          apaga os arquivos locais do projeto
#
# Arquivos de trabalho (tfvars, plano, .terraform, saídas) ficam em ~/.safrion/<projeto>, fora do checkout, só para o
# dono. Na tela vai só o que se cola no chat: hash, contagens e endereços, com e-mails mascarados. Nenhuma senha passa
# por aqui (senhas: passo próprio, depois da fase 1 do hml/).
set -euo pipefail
umask 077

REPO_GH='adrptu/Safrion-Software-'
REGIAO='southamerica-east1'
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$AQUI/../.." && pwd)"
BOOT="$AQUI/bootstrap"
BASE="${SAFRION_DIR:-$HOME/.safrion}"

falha() {
  echo "PARE: $*" >&2
  exit 1
}

mascarar() { sed -E 's/[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+)/***@\1/g'; }

exigir() {
  local c
  for c in "$@"; do
    command -v "$c" >/dev/null || falha "comando $c não encontrado neste terminal"
  done
}

projeto() {
  [[ "${1:-}" =~ ^[a-z][a-z0-9-]{4,28}[a-z0-9]$ ]] || falha "ID de projeto inválido: '${1:-}'"
  DIR="$BASE/$1"
  mkdir -p "$DIR"
  chmod 700 "$BASE" "$DIR"
}

confirmar() {
  local r
  read -r -p "$1 [s/n] " r
  [ "$r" = s ]
}

# Credencial de vida curta da conta logada no Cloud Shell, só no ambiente deste processo (R-006 §3: sem arquivo ADC).
token() {
  GOOGLE_OAUTH_ACCESS_TOKEN="$(gcloud auth print-access-token 2>/dev/null)" || falha 'sem login no gcloud'
  [ -n "$GOOGLE_OAUTH_ACCESS_TOKEN" ] || falha 'sem login no gcloud'
  export GOOGLE_OAUTH_ACCESS_TOKEN
}

cmd_conferir() {
  exigir git gh python3
  local url ramo local_ remoto checks
  url="$(git -C "$RAIZ" remote get-url origin)"
  case "$url" in
    https://github.com/"$REPO_GH" | https://github.com/"$REPO_GH".git | git@github.com:"$REPO_GH".git) ;;
    *) falha "a cópia não é do $REPO_GH" ;;
  esac
  ramo="$(git -C "$RAIZ" rev-parse --abbrev-ref HEAD)"
  [ "$ramo" = main ] || falha "a cópia está em '$ramo', não na main"
  [ -z "$(git -C "$RAIZ" status --porcelain)" ] || falha 'a cópia tem mudanças locais'
  git -C "$RAIZ" fetch -q origin main
  local_="$(git -C "$RAIZ" rev-parse HEAD)"
  remoto="$(git -C "$RAIZ" rev-parse origin/main)"
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
  local p="$1" b="gs://$1-tfstate-bootstrap" regras politica descricao membro papel
  if ! gcloud storage buckets describe "$b" --format='value(name)' >/dev/null 2>&1; then
    gcloud storage buckets create "$b" --project="$p" --location="$REGIAO" \
      --uniform-bucket-level-access --public-access-prevention >/dev/null
    echo "Criado: $b"
  fi
  # Mesma regra do bucket do state da HML (bootstrap/main.tf): versões arquivadas além das 11 mais novas são apagadas.
  regras="$DIR/ciclo-de-vida.json"
  printf '%s\n' '{"lifecycle": {"rule": [{"action": {"type": "Delete"}, "condition": {"isLive": false, "numNewerVersions": 11}}]}}' >"$regras"
  gcloud storage buckets update "$b" --versioning --lifecycle-file="$regras" >/dev/null
  # Vínculos de conveniência de editor e leitor do projeto saem: fica só o dono (README.md, "State do bootstrap").
  politica="$DIR/politica-state.json"
  gcloud storage buckets get-iam-policy "$b" --format=json >"$politica"
  python3 - "$politica" >"$DIR/vinculos-a-tirar.txt" <<'PY'
import json, sys
for b in json.load(open(sys.argv[1], encoding='utf-8')).get('bindings', []):
    for m in b.get('members', []):
        if m.startswith(('projectEditor:', 'projectViewer:')):
            print(m, b['role'])
PY
  while read -r membro papel; do
    [ -n "$membro" ] || continue
    gcloud storage buckets remove-iam-policy-binding "$b" --member="$membro" --role="$papel" >/dev/null
  done <"$DIR/vinculos-a-tirar.txt"
  verificar_state "$p"
  echo "OK: $b com acesso uniforme, sem acesso público, versionado e só com o dono do projeto."
}

# Só leitura: o bucket do state como o README exige e ninguém além do dono alcançando objetos pelo projeto.
verificar_state() {
  local p="$1" b="gs://$1-tfstate-bootstrap" descricao politica
  descricao="$DIR/state.json"
  politica="$DIR/politica-state.json"
  gcloud storage buckets describe "$b" --format=json >"$descricao" || falha "bucket $b não encontrado: rode state"
  gcloud storage buckets get-iam-policy "$b" --format=json >"$politica"
  python3 - "$descricao" "$politica" <<'PY' || falha "o bucket $b não está como o README exige; nada foi planejado"
import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
p = json.load(open(sys.argv[2], encoding='utf-8'))
erros = []
if d.get('uniform_bucket_level_access') is not True:
    erros.append('acesso uniforme desligado')
if d.get('public_access_prevention') != 'enforced':
    erros.append('prevenção de acesso público não está enforced')
if d.get('versioning_enabled') is not True:
    erros.append('versionamento desligado')
outros = sorted({m for b in p.get('bindings', []) for m in b.get('members', []) if not m.startswith('projectOwner:')})
if outros:
    erros.append(f'{len(outros)} membro(s) além do dono do projeto')
for e in erros:
    print(e, file=sys.stderr)
sys.exit(1 if erros else 0)
PY
  iam_efetivo "$p"
}

# O IAM do bucket não mostra o acesso que vem do projeto (revisão do Codex no PR #20). Sem pasta nem organização acima,
# o projeto é a única herança: cada papel de quem não é o dono é expandido (básico, predefinido ou customizado) e
# nenhum pode dar storage.objects.*. Agentes de serviço gerenciados pelo Google (service-<número>@…) ficam listados, sem
# bloquear, porque não são contas que nós usamos.
iam_efetivo() {
  local p="$1" conta pai politica papeis papel
  conta="$(gcloud config get-value account 2>/dev/null)"
  pai="$(gcloud projects describe "$p" --format='value(parent.type)')"
  [ -z "$pai" ] || falha "o projeto tem $pai acima: o acesso herdado ao state não é conferível daqui"
  politica="$DIR/politica-projeto.json"
  papeis="$DIR/papeis-expandidos.json"
  gcloud projects get-iam-policy "$p" --format=json >"$politica"
  printf '{' >"$papeis"
  local primeiro=1
  python3 - "$politica" "user:$conta" >"$DIR/papeis-a-expandir.txt" <<'PY'
import json, re, sys
dono = sys.argv[2]
agente = re.compile(r'^serviceAccount:service-[0-9]+@[a-z0-9-]+\.iam\.gserviceaccount\.com$')
papeis = sorted({b['role'] for b in json.load(open(sys.argv[1], encoding='utf-8')).get('bindings', [])
                 for m in b.get('members', []) if not (m == dono and b['role'] == 'roles/owner') and not agente.match(m)})
print('\n'.join(papeis))
PY
  while read -r papel; do
    [ -n "$papel" ] || continue
    [ "$primeiro" = 1 ] || printf ',' >>"$papeis"
    primeiro=0
    printf '"%s":' "$papel" >>"$papeis"
    gcloud iam roles describe "$papel" --format=json >>"$papeis" || falha "não li as permissões do papel $papel"
  done <"$DIR/papeis-a-expandir.txt"
  printf '}\n' >>"$papeis"
  python3 - "$politica" "$papeis" "user:$conta" <<'PY' || falha 'alguém além do dono alcança objetos do Storage pelo projeto; nada foi planejado'
import json, re, sys
politica = json.load(open(sys.argv[1], encoding='utf-8'))
papeis = json.load(open(sys.argv[2], encoding='utf-8'))
dono = sys.argv[3]
agente = re.compile(r'^serviceAccount:service-[0-9]+@[a-z0-9-]+\.iam\.gserviceaccount\.com$')
erros = 0
for b in politica.get('bindings', []):
    for m in b.get('members', []):
        if (m == dono and b['role'] == 'roles/owner') or agente.match(m):
            continue
        perms = papeis.get(b['role'], {}).get('includedPermissions', [])
        if any(x.startswith('storage.objects.') for x in perms):
            tipo = m.split(':', 1)[0]
            print(f'{tipo} com {b["role"]} alcança objetos do Storage', file=sys.stderr)
            erros += 1
sys.exit(1 if erros else 0)
PY
}

# Terraform e TFLint nas versões e com os SHA-256 fixados no infra.yml (a mesma fonte da CI).
ferramentas() {
  exigir curl unzip sha256sum python3
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
    curl --fail --silent --show-error --location --retry 3 --output "$DIR/$nome.zip" "$url"
    printf '%s  %s\n' "$sha" "$DIR/$nome.zip" | sha256sum --check --quiet - || falha "SHA-256 do $nome diferente do infra.yml"
    unzip -o -q "$DIR/$nome.zip" "$nome" -d "$DIR/bin"
    rm -f "$DIR/$nome.zip"
  done <"$DIR/ferramentas.txt"
  [ -x "$DIR/bin/terraform" ] && [ -x "$DIR/bin/tflint" ] || falha 'Terraform ou TFLint não instalados'
  PATH="$DIR/bin:$PATH"
}

tfvars() {
  local p="$1" repo_id dono_id conta agentes=''
  repo_id="$(gh api "repos/$REPO_GH" --jq .id)"
  dono_id="$(gh api "repos/$REPO_GH" --jq .owner.id)"
  conta="$(gcloud config get-value account 2>/dev/null)"
  [[ "$repo_id" =~ ^[0-9]+$ && "$dono_id" =~ ^[0-9]+$ ]] || falha 'não li os IDs do repositório no GitHub'
  [[ "$conta" =~ ^[^@[:space:]]+@[^@[:space:]]+$ ]] || falha 'sem conta logada no gcloud'
  # Conta Google dos agentes (roteiro, D06), se já existir e a decisão E03 a mantiver: SAFRION_AGENTES=email.
  if [ -n "${SAFRION_AGENTES:-}" ]; then
    [[ "$SAFRION_AGENTES" =~ ^[^@[:space:],]+@[^@[:space:],]+$ ]] || falha 'SAFRION_AGENTES deve ser um e-mail'
    agentes="\"user:$SAFRION_AGENTES\""
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
  terraform show -json "$DIR/bootstrap.tfplan" | python3 -c '
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
  local p="$1" commit hash
  cmd_conferir
  commit="$(git -C "$RAIZ" rev-parse HEAD)"
  exigir gcloud gh
  verificar_state "$p"
  ferramentas
  token
  tfvars "$p"
  export TF_DATA_DIR="$DIR/.terraform" TF_IN_AUTOMATION=1 TF_INPUT=0
  (
    cd "$BOOT"
    terraform init -input=false -lockfile=readonly -no-color -backend-config="bucket=$p-tfstate-bootstrap" >"$DIR/init.log" 2>&1 ||
      falha 'terraform init falhou (detalhes só no seu terminal: ~/.safrion/<projeto>/init.log)'
    terraform fmt -check -recursive >/dev/null || falha 'formatação do Terraform'
    terraform validate -no-color >/dev/null || falha 'terraform validate'
    tflint --config=/dev/null --enable-plugin=terraform --no-color >/dev/null || falha 'TFLint'
  )
  python3 "$AQUI/checar_travas.py" >/dev/null || falha 'checar_travas.py recusou o código'
  (
    cd "$BOOT"
    terraform plan -input=false -lock-timeout=60s -no-color -var-file="$DIR/bootstrap.tfvars" \
      -out="$DIR/bootstrap.tfplan" >"$DIR/plan.log" 2>&1 ||
      falha 'terraform plan falhou (detalhes só no seu terminal: ~/.safrion/<projeto>/plan.log)'
  )
  hash="$(sha256sum "$DIR/bootstrap.tfplan" | cut -d' ' -f1)"
  printf '%s  %s\n' "$hash" "$commit" >"$DIR/bootstrap.tfplan.sha256"
  echo "Plano do bootstrap · projeto $p · commit $commit"
  echo "SHA-256: $hash"
  (cd "$BOOT" && resumo)
  echo "Cole estas linhas no chat. Aplicar só depois dos pareceres pelo hash: cloudshell.sh aplicar $p $hash"
}

cmd_aplicar() {
  projeto "${1:-}"
  local p="$1" esperado="${2:-}" real
  [[ "$esperado" =~ ^[0-9a-f]{64}$ ]] || falha 'informe o SHA-256 aprovado (64 caracteres hexadecimais)'
  [ -f "$DIR/bootstrap.tfplan" ] || falha "sem plano em ~/.safrion/$p: rode planejar"
  real="$(sha256sum "$DIR/bootstrap.tfplan" | cut -d' ' -f1)"
  [ "$real" = "$esperado" ] || falha "o plano local tem outro SHA-256 ($real); nada foi aplicado"
  [ -x "$DIR/bin/terraform" ] || falha 'Terraform não instalado: rode planejar'
  PATH="$DIR/bin:$PATH"
  token
  export TF_DATA_DIR="$DIR/.terraform" TF_IN_AUTOMATION=1 TF_INPUT=0
  (
    cd "$BOOT"
    terraform apply -input=false -lock-timeout=60s -no-color "$DIR/bootstrap.tfplan" >"$DIR/apply.log" 2>&1 ||
      falha 'terraform apply falhou (detalhes só no seu terminal: ~/.safrion/<projeto>/apply.log)'
    terraform output -json >"$DIR/saidas.json"
  )
  echo "Aplicado o plano $esperado no projeto $p."
  echo "Agora: cloudshell.sh depois $p e cloudshell.sh variaveis $p"
}

cmd_depois() {
  projeto "${1:-}"
  exigir gcloud
  local p="$1" numero conta regras r
  numero="$(gcloud projects describe "$p" --format='value(projectNumber)')"
  conta="$numero-compute@developer.gserviceaccount.com"
  if gcloud iam service-accounts describe "$conta" --project="$p" >/dev/null 2>&1; then
    if confirmar 'A conta padrão do Compute existe. Tirar o papel Editor dela e desativá-la?'; then
      if gcloud projects get-iam-policy "$p" --format=json |
        python3 -c 'import json,sys; c=sys.argv[1]; sys.exit(0 if any(b["role"]=="roles/editor" and c in b.get("members",[]) for b in json.load(sys.stdin).get("bindings",[])) else 1)' "serviceAccount:$conta"; then
        gcloud projects remove-iam-policy-binding "$p" --member="serviceAccount:$conta" --role=roles/editor --condition=None >/dev/null
      fi
      gcloud iam service-accounts disable "$conta" --project="$p" >/dev/null
      echo 'Conta padrão do Compute: sem Editor e desativada.'
    fi
  else
    echo 'Conta padrão do Compute: não existe.'
  fi
  if gcloud compute networks describe default --project="$p" >/dev/null 2>&1; then
    regras="$(gcloud compute firewall-rules list --project="$p" --filter='network~/default$' --format='value(name)')"
    if confirmar "A rede default existe, com $(printf '%s' "$regras" | grep -c . || true) regra(s) de firewall. Apagar as regras e a rede?"; then
      for r in $regras; do
        gcloud compute firewall-rules delete "$r" --project="$p" --quiet >/dev/null
      done
      gcloud compute networks delete default --project="$p" --quiet >/dev/null
      echo 'Rede default: apagada.'
    fi
  else
    echo 'Rede default: não existe.'
  fi
}

cmd_variaveis() {
  projeto "${1:-}"
  local p="$1"
  [ -f "$DIR/saidas.json" ] || falha "sem saídas em ~/.safrion/$p: rode aplicar"
  exigir gcloud python3
  python3 - "$DIR/saidas.json" "$p" "$REGIAO" "$(gcloud projects describe "$p" --format='value(projectNumber)')" \
    "$(gcloud config get-value account 2>/dev/null)" <<'PY'
import json, sys
s = {k: v['value'] for k, v in json.load(open(sys.argv[1], encoding='utf-8')).items()}
projeto, regiao, numero, conta = sys.argv[2:6]
print('Environment hml (variáveis, nenhuma é segredo):')
for k, v in (('WIF_PROVIDER', s['wif_provider']), ('DEPLOY_SA', s['sa_deploy_github']),
             ('GCP_PROJECT_ID', projeto), ('GCP_REGION', regiao)):
    print(f'  {k} = {v}')
print('Environment hml-infra (variáveis, nenhuma é segredo):')
for k, v in (('WIF_PROVIDER', s['wif_provider']), ('INFRA_SA', s['sa_infra_github']),
             ('BUCKET_STATE', s['bucket_state']), ('TF_VAR_projeto_id', projeto), ('TF_VAR_projeto_numero', numero),
             ('TF_VAR_operador', f'user:{conta}'), ('TF_VAR_rede_self_link', s['rede_self_link']),
             ('TF_VAR_subrede_self_link', s['subrede_self_link']), ('TF_VAR_faixa_psa_nome', s['faixa_psa_nome']),
             ('TF_VAR_criar_cloud_run', 'false')):
    print(f'  {k} = {v}')
print('Grave no GitHub (Settings > Environments). TF_VAR_operador tem o seu e-mail: não cole esta lista no chat.')
PY
}

cmd_limpar() {
  projeto "${1:-}"
  rm -rf "${DIR:?}"
  echo "Apagado ~/.safrion/$1 (plano, tfvars, .terraform e saídas). O state continua no bucket."
}

uso() {
  sed -n '4,11p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 2
}

case "${1:-}" in
  conferir) cmd_conferir ;;
  state) cmd_state "${2:-}" ;;
  planejar) cmd_planejar "${2:-}" ;;
  aplicar) cmd_aplicar "${2:-}" "${3:-}" ;;
  depois) cmd_depois "${2:-}" ;;
  variaveis) cmd_variaveis "${2:-}" ;;
  limpar) cmd_limpar "${2:-}" ;;
  *) uso ;;
esac
