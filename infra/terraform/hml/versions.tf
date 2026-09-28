terraform {
  required_version = ">= 1.11"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 8.3"
    }
  }

  # O bucket vem do bootstrap (saída bucket_state): terraform init -backend-config="bucket=<bucket>".
  backend "gcs" {
    prefix = "hml"
  }
}
