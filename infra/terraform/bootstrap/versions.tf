# Versões exatas, com a quarentena de 7 dias do projeto. Fonte: releases oficiais no GitHub (hashicorp/terraform e
# hashicorp/terraform-provider-google), lidas em 28/09/2026: Terraform 1.16.3 de 16/09 e provider 8.3.0 de 15/09.
# 1.16.4 (23/09) e 8.4.0 (22/09) ainda não cumprem os 7 dias. Subir só com nova leitura das datas e novo lock.
terraform {
  required_version = "= 1.16.3"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "= 8.3.0"
    }
  }

  # State remoto desde o 1º init, num bucket só do bootstrap, criado fora do Terraform antes do init (README.md,
  # "State do bootstrap"): terraform init -backend-config="bucket=<projeto>-tfstate-bootstrap". A sa-infra-github não o
  # alcança: não tem papel de Storage no projeto e só tem objectAdmin no bucket do state da HML (contas.tf).
  backend "gcs" {
    prefix = "bootstrap"
  }
}
