terraform {
  required_version = ">= 1.11"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 8.3"
    }
  }

  # State local na 1ª aplicação. Migração para o bucket: ver README.md.
}
