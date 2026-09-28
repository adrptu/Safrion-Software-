# Cloud SQL da HML. Sem root_password e sem google_sql_user do postgres: a senha nunca entra no state nem no plan.
# O banco safrion_hml e os papéis migrator, app_runtime e app_sessao nascem só pelo job de preparo.
resource "google_sql_database_instance" "hml" {
  name                = "safrion-hml"
  region              = var.regiao
  database_version    = "POSTGRES_17"
  deletion_protection = true

  settings {
    # PG 16+ nasce Enterprise Plus; db-f1-micro só existe na Enterprise.
    edition                     = "ENTERPRISE"
    tier                        = "db-f1-micro"
    availability_type           = "ZONAL"
    disk_type                   = "PD_SSD"
    disk_size                   = 10
    disk_autoresize             = true
    disk_autoresize_limit       = 20
    deletion_protection_enabled = true

    # Se a instância for apagada fora do Terraform, os backups ficam pela retenção configurada.
    retain_backups_on_delete = true

    # Só Auth Proxy ou conectores; o Cloud Run usa o Auth Proxy embutido no socket /cloudsql.
    connector_enforcement = "REQUIRED"

    user_labels = {
      sistema  = "safrion"
      ambiente = "hml"
    }

    # PRD 30.5: 35 backups retidos e PITR de 7 dias (máximo da Enterprise), tudo em São Paulo.
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      location                       = var.regiao

      backup_retention_settings {
        retained_backups = 35
        retention_unit   = "COUNT"
      }
    }

    # IP público sem redes autorizadas: só conector com IAM, sempre com TLS.
    ip_configuration {
      ipv4_enabled   = true
      ssl_mode       = "ENCRYPTED_ONLY"
      server_ca_mode = "GOOGLE_MANAGED_INTERNAL_CA"
    }
  }

  lifecycle {
    prevent_destroy = true

    # Com autoaumento, o disco cresce fora do Terraform; sem isto o apply tentaria recriar a instância.
    ignore_changes = [settings[0].disk_size]
  }
}
