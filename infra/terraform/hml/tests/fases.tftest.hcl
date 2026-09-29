# Fase 1 sem o client ID de login; a fase 2 exige (contrato de 29/09). Sem credencial nem nuvem: o provider é simulado.
# Uso, no módulo hml/: terraform init -backend=false && terraform test

mock_provider "google" {}

variables {
  projeto_id        = "safrion-hml-teste"
  projeto_numero    = "123456789012"
  operador          = "user:operador@example.com"
  rede_self_link    = "https://www.googleapis.com/compute/v1/projects/safrion-hml-teste/global/networks/safrion-hml"
  subrede_self_link = "https://www.googleapis.com/compute/v1/projects/safrion-hml-teste/regions/southamerica-east1/subnetworks/safrion-hml"
  faixa_psa_nome    = "safrion-hml-psa"
}

run "fase1_sem_client_id" {
  command = plan

  variables {
    criar_cloud_run = false
  }
}

run "fase2_com_client_id_em_branco" {
  command = plan

  variables {
    criar_cloud_run  = true
    oidc_client_id   = "   "
    versoes_segredos = { admin = 1, migrator = 1, app_runtime = 1, oidc = 1 }
  }

  expect_failures = [var.oidc_client_id]
}

run "fase2_sem_client_id" {
  command = plan

  variables {
    criar_cloud_run  = true
    versoes_segredos = { admin = 1, migrator = 1, app_runtime = 1, oidc = 1 }
  }

  expect_failures = [var.oidc_client_id]
}

run "fase2_com_client_id" {
  command = plan

  variables {
    criar_cloud_run  = true
    oidc_client_id   = "000000000000-exemplo.apps.googleusercontent.com"
    versoes_segredos = { admin = 1, migrator = 1, app_runtime = 1, oidc = 1 }
  }
}
