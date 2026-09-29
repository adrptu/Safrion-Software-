provider "google" {
  project = var.projeto_id
  region  = var.regiao

  default_labels = {
    sistema  = "safrion"
    ambiente = "hml"
  }
}

locals {
  # storage entra porque o bucket do state depende dela (costuma vir ligada).
  # compute e servicenetworking são da rede privada (rede.tf). Ligar o compute cria a conta padrão do Compute (README).
  apis = toset(concat([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "storage.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
  ], var.habilitar_iap ? ["iap.googleapis.com"] : []))

  bucket_state = "${var.projeto_id}-tfstate-hml"
}

resource "google_project_service" "apis" {
  for_each = local.apis

  service = each.value

  # Nunca desligar API pelo Terraform: derrubaria a HML.
  disable_on_destroy = false
}

# State da HML. Acesso: dono do projeto (papéis básicos) e sa-infra-github só no prefixo hml/.
resource "google_storage_bucket" "state" {
  name                        = local.bucket_state
  location                    = var.regiao
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false

  versioning {
    enabled = true
  }

  # Guarda a versão atual e as 10 anteriores de cada arquivo de state.
  # O GCS conta a versão atual entre as mais novas: 11 apaga a partir da 11ª anterior.
  lifecycle_rule {
    condition {
      with_state         = "ARCHIVED"
      num_newer_versions = 11
    }

    action {
      type = "Delete"
    }
  }

  # Planos do infra-hml.yml (planos/<run_id>/<tentativa>/): o plano vale para uma revisão, e o hash fica no recibo, fora
  # do bucket. Apagado em 30 dias; a versão arquivada, no dia seguinte (a regra acima não apaga objeto de versão única).
  lifecycle_rule {
    condition {
      age            = 30
      matches_prefix = ["planos/"]
    }

    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      with_state                 = "ARCHIVED"
      matches_prefix             = ["planos/"]
      days_since_noncurrent_time = 1
    }

    action {
      type = "Delete"
    }
  }

  lifecycle {
    prevent_destroy = true
  }

  depends_on = [google_project_service.apis]
}
