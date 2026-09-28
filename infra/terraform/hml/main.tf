provider "google" {
  project = var.projeto_id
  region  = var.regiao

  default_labels = {
    sistema  = "safrion"
    ambiente = "hml"
  }
}

locals {
  banco  = "safrion_hml"
  socket = "/cloudsql/${google_sql_database_instance.hml.connection_name}"
  origem = coalesce(var.origem, "https://safrion-web-${var.projeto_numero}.${var.regiao}.run.app")
  iap    = var.url_controlada == "iap"

  # Contas criadas pelo bootstrap (mesmos nomes de infra/terraform/bootstrap/contas.tf).
  sa = {
    web     = "sa-web@${var.projeto_id}.iam.gserviceaccount.com"
    preparo = "sa-preparo@${var.projeto_id}.iam.gserviceaccount.com"
    demo    = "sa-demo@${var.projeto_id}.iam.gserviceaccount.com"
    deploy  = "sa-deploy-github@${var.projeto_id}.iam.gserviceaccount.com"
  }

  # Imagens provisórias públicas do Google. A imagem real é só do pipeline, por digest.
  imagem_web_provisoria = "us-docker.pkg.dev/cloudrun/container/hello"
  imagem_job_provisoria = "us-docker.pkg.dev/cloudrun/container/job"
}

# Imagens da HML: tags imutáveis; o pipeline publica o mesmo digest que o Trivy varreu.
resource "google_artifact_registry_repository" "safrion" {
  repository_id          = "safrion"
  location               = var.regiao
  format                 = "DOCKER"
  description            = "Imagens da HML do Safrion."
  cleanup_policy_dry_run = false

  docker_config {
    immutable_tags = true
  }

  # KEEP vence DELETE: as 10 versões mais recentes ficam mesmo sem tag.
  cleanup_policies {
    id     = "apagar-sem-tag-14d"
    action = "DELETE"

    condition {
      tag_state  = "UNTAGGED"
      older_than = "14d"
    }
  }

  cleanup_policies {
    id     = "manter-10-recentes"
    action = "KEEP"

    most_recent_versions {
      keep_count = 10
    }
  }
}

resource "google_artifact_registry_repository_iam_member" "deploy_writer" {
  location   = google_artifact_registry_repository.safrion.location
  repository = google_artifact_registry_repository.safrion.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${local.sa.deploy}"
}
