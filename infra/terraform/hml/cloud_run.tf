# Web e jobs nascem com imagem provisória. A imagem real é só do pipeline (ignore_changes);
# sem isso, o próximo apply reverteria a HML em silêncio.
# Tudo aqui só existe com criar_cloud_run = true, depois que as versões dos segredos existirem.

locals {
  url_app_runtime = "postgresql://app_runtime@/${local.banco}?host=${local.socket}"

  env_web = {
    DATABASE_URL           = local.url_app_runtime
    SAFRION_AMBIENTE       = "hml"
    SAFRION_ORIGEM         = local.origem
    SAFRION_OIDC_ISSUER    = "https://accounts.google.com"
    SAFRION_OIDC_CLIENT_ID = var.oidc_client_id
  }

  segredos_web = {
    PGPASSWORD                 = "hml-db-app-runtime-senha"
    SAFRION_OIDC_CLIENT_SECRET = "hml-oidc-client-secret"
  }

  env_preparo = {
    SAFRION_ADMIN_URL = "postgresql://postgres@/postgres?host=${local.socket}"
  }

  segredos_preparo = {
    PGPASSWORD                = "hml-db-admin-senha"
    SAFRION_SENHA_MIGRATOR    = "hml-db-migrator-senha"
    SAFRION_SENHA_APP_RUNTIME = "hml-db-app-runtime-senha"
  }

  env_demo = {
    DATABASE_URL     = local.url_app_runtime
    SAFRION_AMBIENTE = "hml"
  }

  segredos_demo = {
    PGPASSWORD = "hml-db-app-runtime-senha"
  }

  jobs = var.criar_cloud_run ? {
    preparo = google_cloud_run_v2_job.preparo[0].name
    demo    = google_cloud_run_v2_job.demo_reset[0].name
  } : {}
}

# --- Web ---

resource "google_cloud_run_v2_service" "web" {
  count = var.criar_cloud_run ? 1 : 0

  name                = "safrion-web"
  location            = var.regiao
  ingress             = "INGRESS_TRAFFIC_ALL"
  iap_enabled         = local.iap
  deletion_protection = true

  template {
    service_account                  = local.sa.web
    max_instance_request_concurrency = 20

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }

    volumes {
      name = "cloudsql"

      cloud_sql_instance {
        instances = [google_sql_database_instance.hml.connection_name]
      }
    }

    containers {
      image = local.imagem_web_provisoria

      # CPU só durante a requisição.
      resources {
        cpu_idle = true

        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      # /saude trava a revisão sem banco. Sem liveness_probe: /saude responde 503 quando o banco cai
      # e derrubaria instâncias sadias.
      startup_probe {
        period_seconds    = 10
        timeout_seconds   = 5
        failure_threshold = 6

        http_get {
          path = "/saude"
        }
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      dynamic "env" {
        for_each = local.env_web

        content {
          name  = env.key
          value = env.value
        }
      }

      dynamic "env" {
        for_each = local.segredos_web

        content {
          name = env.key

          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.hml[env.value].secret_id
              version = local.versao[env.value]
            }
          }
        }
      }
    }
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
      client,
      client_version,
    ]
  }

  depends_on = [google_secret_manager_secret_iam_member.acesso]
}

# IAP: o agente de serviço do IAP é o único invocador; quem entra é a lista iap_permitidos.
resource "google_cloud_run_v2_service_iam_member" "iap_invoker" {
  count = var.criar_cloud_run && local.iap ? 1 : 0

  location = var.regiao
  name     = google_cloud_run_v2_service.web[0].name
  role     = "roles/run.invoker"
  member   = "serviceAccount:service-${var.projeto_numero}@gcp-sa-iap.iam.gserviceaccount.com"
}

resource "google_iap_web_cloud_run_service_iam_member" "permitidos" {
  for_each = var.criar_cloud_run && local.iap ? toset(var.iap_permitidos) : toset([])

  location               = var.regiao
  cloud_run_service_name = google_cloud_run_v2_service.web[0].name
  role                   = "roles/iap.httpsResourceAccessor"
  member                 = each.value
}

# Exceção ENG-005 (url_controlada = "publico"): allUsers só na web, nunca nos jobs.
resource "google_cloud_run_v2_service_iam_member" "publico" {
  count = var.criar_cloud_run && !local.iap ? 1 : 0

  location = var.regiao
  name     = google_cloud_run_v2_service.web[0].name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# A publicação só troca a imagem; a versão dos segredos é só do Terraform (rotação no README.md).
# Confirmar na 1ª publicação se run.developer basta com os segredos já declarados.
resource "google_cloud_run_v2_service_iam_member" "deploy_web" {
  count = var.criar_cloud_run ? 1 : 0

  location = var.regiao
  name     = google_cloud_run_v2_service.web[0].name
  role     = "roles/run.developer"
  member   = "serviceAccount:${local.sa.deploy}"
}

# --- Jobs ---

resource "google_cloud_run_v2_job" "preparo" {
  count = var.criar_cloud_run ? 1 : 0

  name                = "safrion-preparo"
  location            = var.regiao
  deletion_protection = true

  template {
    task_count = 1

    template {
      service_account = local.sa.preparo
      max_retries     = 0
      timeout         = "600s"

      volumes {
        name = "cloudsql"

        cloud_sql_instance {
          instances = [google_sql_database_instance.hml.connection_name]
        }
      }

      containers {
        image = local.imagem_job_provisoria
        args  = ["--ambiente", "hml", "--banco", local.banco]

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }

        volume_mounts {
          name       = "cloudsql"
          mount_path = "/cloudsql"
        }

        dynamic "env" {
          for_each = local.env_preparo

          content {
            name  = env.key
            value = env.value
          }
        }

        dynamic "env" {
          for_each = local.segredos_preparo

          content {
            name = env.key

            value_source {
              secret_key_ref {
                secret  = google_secret_manager_secret.hml[env.value].secret_id
                version = local.versao[env.value]
              }
            }
          }
        }
      }
    }
  }

  lifecycle {
    ignore_changes = [
      template[0].template[0].containers[0].image,
      client,
      client_version,
    ]
  }

  depends_on = [google_secret_manager_secret_iam_member.acesso]
}

resource "google_cloud_run_v2_job" "demo_reset" {
  count = var.criar_cloud_run ? 1 : 0

  name                = "safrion-demo-reset"
  location            = var.regiao
  deletion_protection = true

  template {
    task_count = 1

    template {
      service_account = local.sa.demo
      max_retries     = 0
      timeout         = "600s"

      volumes {
        name = "cloudsql"

        cloud_sql_instance {
          instances = [google_sql_database_instance.hml.connection_name]
        }
      }

      containers {
        image   = local.imagem_job_provisoria
        command = ["node"]
        args    = ["dist/cli/demo-reset.js", "--confirmar", "hml"]

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }

        volume_mounts {
          name       = "cloudsql"
          mount_path = "/cloudsql"
        }

        dynamic "env" {
          for_each = local.env_demo

          content {
            name  = env.key
            value = env.value
          }
        }

        # O secretAccessor da sa-demo autoriza a leitura, mas não cria a variável (F40).
        dynamic "env" {
          for_each = local.segredos_demo

          content {
            name = env.key

            value_source {
              secret_key_ref {
                secret  = google_secret_manager_secret.hml[env.value].secret_id
                version = local.versao[env.value]
              }
            }
          }
        }
      }
    }
  }

  lifecycle {
    ignore_changes = [
      template[0].template[0].containers[0].image,
      client,
      client_version,
    ]
  }

  depends_on = [google_secret_manager_secret_iam_member.acesso]
}

# Publicação troca a imagem e executa os jobs; o operador humano executa os jobs.
resource "google_cloud_run_v2_job_iam_member" "deploy_jobs" {
  for_each = local.jobs

  location = var.regiao
  name     = each.value
  role     = "roles/run.developer"
  member   = "serviceAccount:${local.sa.deploy}"
}

resource "google_cloud_run_v2_job_iam_member" "operador_jobs" {
  for_each = local.jobs

  location = var.regiao
  name     = each.value
  role     = "roles/run.invoker"
  member   = var.operador
}
