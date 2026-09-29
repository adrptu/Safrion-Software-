# Contas de serviço da HML, sem chave JSON. Os nomes são usados pelo infra/terraform/hml: mudar aqui exige mudar lá.
# Conta padrão do Compute: fora do Terraform (procedimento no README.md).

locals {
  contas = merge({
    "sa-web"             = "Safrion HML: web"
    "sa-preparo"         = "Safrion HML: job de preparo do banco"
    "sa-demo"            = "Safrion HML: job de reset da demonstração"
    "sa-deploy-github"   = "Safrion HML: publicação pelo GitHub Actions"
    "sa-infra-github"    = "Safrion HML: Terraform da HML pelo GitHub Actions"
    "sa-agentes-leitura" = "Safrion HML: leitura pelos agentes"
  }, var.criar_sa_vertex ? { "sa-vertex" = "Safrion HML: Vertex AI dos agentes" } : {})

  runtime = toset(["sa-web", "sa-preparo", "sa-demo"])

  papeis_agentes = toset([
    "roles/run.viewer",
    "roles/cloudsql.viewer",
    "roles/logging.viewer",
    "roles/monitoring.viewer",
    "roles/artifactregistry.reader",
  ])

  # O que o apply da HML cria e administra. Cada papel é de um serviço; nenhum dá IAM do projeto.
  # Exceção ENG-005 de cada papel admin: README.md. Segredos ficam no papel customizado abaixo.
  papeis_infra = toset(concat([
    "roles/artifactregistry.admin",
    "roles/cloudsql.admin",
    "roles/run.admin",
  ], var.habilitar_iap ? ["roles/iap.admin"] : []))

  # Cada conta de CI só aceita o token do seu workflow (wif.tf).
  fluxo_da_conta = {
    "sa-deploy-github" = "publicar"
    "sa-infra-github"  = "infra"
  }

  # Quem pode agir como cada conta de runtime (actAs): publicação e Terraform da HML.
  act_as = {
    for par in setproduct(["sa-deploy-github", "sa-infra-github"], local.runtime) :
    "${par[0]}/${par[1]}" => { quem = par[0], conta = par[1] }
  }

  membro = { for id in keys(local.contas) : id => "serviceAccount:${google_service_account.contas[id].email}" }
}

resource "google_service_account" "contas" {
  for_each = local.contas

  account_id   = each.key
  display_name = each.value

  depends_on = [google_project_service.apis]
}

# --- Federação: cada conta só para o seu workflow; a condição do provider WIF filtra o resto ---

resource "google_service_account_iam_member" "wif" {
  for_each = local.fluxo_da_conta

  service_account_id = google_service_account.contas[each.key].name
  role               = "roles/iam.workloadIdentityUser"
  member             = local.principal_fluxo[each.value]
}

resource "google_service_account_iam_member" "act_as" {
  for_each = local.act_as

  service_account_id = google_service_account.contas[each.value.conta].name
  role               = "roles/iam.serviceAccountUser"
  member             = local.membro[each.value.quem]
}

# --- Terraform da HML pela CI (sa-infra-github) ---

resource "google_project_iam_member" "infra" {
  for_each = local.papeis_infra

  project = var.projeto_id
  role    = each.value
  member  = local.membro["sa-infra-github"]
}

# Segredos sem valor: cria, lê os metadados, atualiza e dá IAM. Sem ler, gravar, destruir versão
# nem apagar segredo (secretmanager.admin faria tudo isso). NÃO isola o valor: com setIamPolicy a conta pode se dar
# acesso, e com run.admin e actAs roda código como as contas de runtime, que leem os segredos (R-006, 43e9497).
resource "google_project_iam_custom_role" "segredos_sem_valor" {
  role_id     = "safrionInfraSegredos"
  title       = "Safrion HML: segredos sem valor"
  description = "Terraform da HML: segredos e IAM, sem acesso às versões."
  permissions = [
    "secretmanager.secrets.create",
    "secretmanager.secrets.get",
    "secretmanager.secrets.list",
    "secretmanager.secrets.update",
    "secretmanager.secrets.getIamPolicy",
    "secretmanager.secrets.setIamPolicy",
  ]

  depends_on = [google_project_service.apis]
}

# Job de vínculo (R-006 §3c): só o que a fila usa no hml-vinculo-pedido, vinculado no próprio segredo pelo hml/.
# Sem versions.add, versions.enable nem secrets.rotate, que o secretVersionManager daria: a conta do job não grava
# pedido nem reativa versão desativada (que ainda tem o código). Aqui, e não no hml/, porque criar papel pede
# iam.roles.create, que a sa-infra-github não tem. checar_travas.py confere o conjunto exato.
resource "google_project_iam_custom_role" "vinculo_pedido" {
  role_id     = "safrionVinculoPedido"
  title       = "Safrion HML: fila de pedidos de vínculo"
  description = "Job safrion-vinculo: lista, lê, desativa e destrói versões do hml-vinculo-pedido."
  permissions = [
    "secretmanager.versions.list",
    "secretmanager.versions.get",
    "secretmanager.versions.access",
    "secretmanager.versions.disable",
    "secretmanager.versions.destroy",
  ]

  depends_on = [google_project_service.apis]
}

resource "google_project_iam_member" "infra_segredos" {
  project = var.projeto_id
  role    = google_project_iam_custom_role.segredos_sem_valor.name
  member  = local.membro["sa-infra-github"]
}

# State da HML: o backend gcs pede Storage Object Admin no bucket (R-006, F44). O do bootstrap fica noutro bucket, fora
# do Terraform e sem este acesso (README.md, "State do bootstrap"); checar_travas.py confere.
resource "google_storage_bucket_iam_member" "infra_state" {
  bucket = google_storage_bucket.state.name
  role   = "roles/storage.objectAdmin"
  member = local.membro["sa-infra-github"]
}

# --- Acesso ao banco e aos logs (no projeto) ---

# Só as contas de runtime. O operador não conecta mais ao banco da HML: sem IP público, o Auth Proxy do notebook, que
# usava este papel, não tem caminho (ADR 0006).
resource "google_project_iam_member" "cloudsql_client" {
  for_each = { for id in local.runtime : id => local.membro[id] }

  project = var.projeto_id
  role    = "roles/cloudsql.client"
  member  = each.value
}

resource "google_project_iam_member" "operador_logs" {
  project = var.projeto_id
  role    = "roles/logging.viewer"
  member  = var.operador
}

# --- Agentes: só leitura, por personificação, sem secretAccessor ---

resource "google_project_iam_member" "agentes_leitura" {
  for_each = local.papeis_agentes

  project = var.projeto_id
  role    = each.value
  member  = local.membro["sa-agentes-leitura"]
}

resource "google_service_account_iam_member" "agentes_token" {
  for_each = toset(var.agentes)

  service_account_id = google_service_account.contas["sa-agentes-leitura"].name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = each.value
}

resource "google_project_iam_member" "vertex" {
  count = var.criar_sa_vertex ? 1 : 0

  project = var.projeto_id
  role    = "roles/aiplatform.user"
  member  = local.membro["sa-vertex"]
}

resource "google_service_account_iam_member" "agentes_token_vertex" {
  for_each = var.criar_sa_vertex ? toset(var.agentes) : toset([])

  service_account_id = google_service_account.contas["sa-vertex"].name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = each.value
}
