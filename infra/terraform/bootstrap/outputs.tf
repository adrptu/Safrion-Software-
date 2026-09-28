output "bucket_state" {
  description = "Bucket do state da HML: terraform init -backend-config=\"bucket=<valor>\" em infra/terraform/hml."
  value       = google_storage_bucket.state.name
}

output "wif_provider" {
  description = "Nome completo do provider WIF (variável WIF_PROVIDER do GitHub)."
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "sa_deploy_github" {
  description = "Conta da publicação das imagens e revisões (variável DEPLOY_SA do GitHub)."
  value       = google_service_account.contas["sa-deploy-github"].email
}

output "sa_infra_github" {
  description = "Conta que aplica infra/terraform/hml pela CI."
  value       = google_service_account.contas["sa-infra-github"].email
}

output "contas" {
  description = "E-mail de cada conta de serviço criada."
  value       = { for id, sa in google_service_account.contas : id => sa.email }
}
