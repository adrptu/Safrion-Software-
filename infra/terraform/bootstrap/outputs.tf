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

# Entradas do hml/ (TF_VAR_rede_self_link, TF_VAR_subrede_self_link e TF_VAR_faixa_psa_nome): sem bloco data lá.
output "rede_self_link" {
  description = "Rede privada da HML: variável rede_self_link do hml/."
  value       = google_compute_network.hml.self_link
}

output "subrede_self_link" {
  description = "Sub-rede do Direct VPC egress: variável subrede_self_link do hml/."
  value       = google_compute_subnetwork.run.self_link
}

output "faixa_psa_nome" {
  description = "Nome da faixa do Private Service Access: variável faixa_psa_nome do hml/."
  value       = google_compute_global_address.psa.name
}
