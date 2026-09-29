# Cloud SQL da HML. Sem root_password e sem google_sql_user do postgres: a senha nunca entra no state nem no plan.
# O banco safrion_hml e os papéis migrator, app_runtime e app_sessao nascem só pelo job de preparo.
# Só IP privado (ADR 0006). A rede e a conexão PSA são do bootstrap, em outro state: o depends_on que a doc do provider
# pede não alcança, e a ordem vem do procedimento (bootstrap aplicado antes da 1ª criação desta instância).
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

    # Só Auth Proxy ou conectores; web e jobs usam o conector Node.js com ipType PRIVATE (ADR 0006).
    connector_enforcement = "REQUIRED"

    # ExecuteSql (Cloud SQL Studio) fechado de forma explícita: o provider calcula o campo, e sem valor no código uma
    # mudança no console não voltaria no apply nem sairia conhecida no plan (checar_travas.py --plano recusa desconhecido).
    data_api_access = "DISALLOW_DATA_API"

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

    # Sem IP público e sem redes autorizadas: só IP privado, só conector com IAM, sempre com TLS. ipv4_enabled fica
    # false literal, porque o Trivy trata ausente ou não resolvido como true (GCP-0017). O IP privado não sai mais da
    # instância, e a faixa só vale na criação.
    ip_configuration {
      ipv4_enabled       = false
      private_network    = var.rede_self_link
      allocated_ip_range = var.faixa_psa_nome
      ssl_mode           = "ENCRYPTED_ONLY"
      server_ca_mode     = "GOOGLE_MANAGED_INTERNAL_CA"
    }
  }

  lifecycle {
    prevent_destroy = true

    # Com autoaumento, o disco cresce fora do Terraform; sem isto o apply tentaria recriar a instância.
    ignore_changes = [settings[0].disk_size]
  }
}
