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

  # O bucket vem do bootstrap (saída bucket_state): terraform init -backend-config="bucket=<bucket>".
  backend "gcs" {
    prefix = "hml"
  }
}
