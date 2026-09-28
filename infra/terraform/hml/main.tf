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
  origem = coalesce(var.origem, "https://safrion-web-${var.projeto_numero}.${var.regiao}.run.app")
  iap    = var.url_controlada == "iap"

  # Nome de conexão (<projeto>:<região>:safrion-hml): o conector ipType PRIVATE chega ao IP privado por ele (ADR 0006).
  instancia = google_sql_database_instance.hml.connection_name

  # O Direct VPC egress recebe o nome completo do recurso (projects/…), como na doc do Cloud Run, e não a URL do self_link.
  rede    = trimprefix(var.rede_self_link, "https://www.googleapis.com/compute/v1/")
  subrede = trimprefix(var.subrede_self_link, "https://www.googleapis.com/compute/v1/")

  # Contas criadas pelo bootstrap (mesmos nomes de infra/terraform/bootstrap/contas.tf).
  sa = {
    web     = "sa-web@${var.projeto_id}.iam.gserviceaccount.com"
    preparo = "sa-preparo@${var.projeto_id}.iam.gserviceaccount.com"
    demo    = "sa-demo@${var.projeto_id}.iam.gserviceaccount.com"
    deploy  = "sa-deploy-github@${var.projeto_id}.iam.gserviceaccount.com"
  }

  # Imagens provisórias públicas do Google. A imagem real é só do pipeline, por digest.
  # Imagens provisórias públicas do Google, por digest (lidas em 28/09/2026 no registro; tag móvel não entra).
  # Só existem até o pipeline publicar a imagem do Safrion; resposta 200 delas não é saúde do produto.
  imagem_web_provisoria = "us-docker.pkg.dev/cloudrun/container/hello@sha256:2010579f8f7ce243767c2875e4c481f7388484f3ecab83d27a4288a599981f35"
  imagem_job_provisoria = "us-docker.pkg.dev/cloudrun/container/job@sha256:2181d939d7606e32befcb266a7e9f76dcf0e8bd5e7319f13d71ba5233d658acb"
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
