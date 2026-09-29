output "url_web" {
  description = "URL do serviço web (nula enquanto criar_cloud_run = false). Deve bater com SAFRION_ORIGEM."
  value       = one(google_cloud_run_v2_service.web[*].uri)
}

output "origem" {
  description = "Valor usado em SAFRION_ORIGEM e no URI de retorno do cliente OAuth (/entrar/retorno)."
  value       = local.origem
}

output "conexao_cloud_sql" {
  description = "Nome de conexão do Cloud SQL: SAFRION_CLOUDSQL_INSTANCIA do conector ipType PRIVATE (ADR 0006)."
  value       = google_sql_database_instance.hml.connection_name
}

output "repositorio_imagens" {
  description = "Caminho Docker do Artifact Registry para o pipeline."
  value       = "${var.regiao}-docker.pkg.dev/${var.projeto_id}/${google_artifact_registry_repository.safrion.repository_id}"
}

output "segredos" {
  description = "IDs dos segredos. As versões entram fora do Terraform."
  value       = sort(concat([for s in google_secret_manager_secret.hml : s.secret_id], [google_secret_manager_secret.vinculo_pedido.secret_id]))
}

output "jobs" {
  description = "Nomes dos jobs do Cloud Run (vazio enquanto criar_cloud_run = false)."
  value       = local.jobs
}
