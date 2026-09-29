# Federação de identidade do GitHub Actions, sem chave JSON (R-006, identidades).
# Sem workflow_ref e event_name, qualquer workflow na main (inclusive pull_request_target) receberia as contas.
# Cada workflow vira só a sua conta (contas.tf): publicar-hml.yml → sa-deploy-github; infra-hml.yml → sa-infra-github.
# Condição canônica do R-006: cada workflow só no seu environment (publicar → hml; infra → hml-infra). Sem environment, nada.

locals {
  # Fluxo → arquivo do workflow. O fluxo vira attribute.fluxo e separa as contas nos vínculos.
  fluxos = {
    publicar = { arquivo = "publicar-hml.yml", environment = "hml" }
    infra    = { arquivo = "infra-hml.yml", environment = "hml-infra" }
  }

  prefixo_fluxo = { for f, x in local.fluxos : f => "${var.github_repositorio}/.github/workflows/${x.arquivo}@" }

  condicao_wif = join(" && ", concat([
    "assertion.repository_id == '${var.github_repository_id}'",
    "assertion.repository_owner_id == '${var.github_owner_id}'",
    "assertion.ref == 'refs/heads/main'",
    "assertion.event_name in ['push', 'workflow_dispatch']",
    "(${join(" || ", [for f, x in local.fluxos : "(assertion.workflow_ref.startsWith('${local.prefixo_fluxo[f]}') && assertion.environment == '${x.environment}')"])})",
  ]))

  # publicar, infra ou outro (outro é recusado pela condição acima).
  expressao_fluxo = join(" : ", concat(
    [for f, p in local.prefixo_fluxo : "assertion.workflow_ref.startsWith('${p}') ? '${f}'"],
    ["'outro'"],
  ))

  mapeamento_wif = {
    "google.subject"                = "assertion.sub"
    "attribute.repository_id"       = "assertion.repository_id"
    "attribute.repository_owner_id" = "assertion.repository_owner_id"
    "attribute.ref"                 = "assertion.ref"
    "attribute.event_name"          = "assertion.event_name"
    "attribute.workflow_ref"        = "assertion.workflow_ref"
    "attribute.environment"         = "assertion.environment"
    "attribute.fluxo"               = local.expressao_fluxo
  }

  # Um principal por fluxo. O pool só tem este provider; outro provider no pool exige rever os vínculos.
  principal_fluxo = {
    for f in keys(local.fluxos) :
    f => "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.fluxo/${f}"
  }
}

resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github-hml"
  display_name              = "GitHub HML"
  description               = "Tokens OIDC do GitHub Actions para publicar a HML e aplicar o Terraform dela."

  lifecycle {
    prevent_destroy = true
  }

  depends_on = [google_project_service.apis]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-oidc"
  display_name                       = "GitHub OIDC"
  description                        = "Só publicar-hml.yml (hml) e infra-hml.yml (hml-infra) na main, por push ou disparo manual."
  attribute_condition                = local.condicao_wif
  attribute_mapping                  = local.mapeamento_wif

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  lifecycle {
    prevent_destroy = true
  }
}
