# Rede privada da HML (ADR 0006). Aplicada no bootstrap, na sessão do dono, ANTES do apply do hml/ que cria a
# instância: o IP privado não sai mais da instância, e a faixa nomeada só vale na criação (numa instância existente,
# ligar o IP privado a reinicia e não aceita faixa). Sem NAT, conector VPC, regra de firewall, bastion ou VPN.

resource "google_compute_network" "hml" {
  name                    = "safrion-hml"
  auto_create_subnetworks = false

  lifecycle {
    prevent_destroy = true
  }

  depends_on = [google_project_service.apis]
}

# Sub-rede do Direct VPC egress do Cloud Run (mínimo /26; a /24 dá folga aos blocos de IP que o Cloud Run reserva).
# private_ip_google_access fecha o GCP-0075. Sem log_config: flow logs custam (GCP-0076 e GCP-0029 ficam abaixo do gate).
resource "google_compute_subnetwork" "run" {
  name                     = "safrion-hml-run"
  region                   = var.regiao
  network                  = google_compute_network.hml.id
  ip_cidr_range            = var.subrede_cidr
  private_ip_google_access = true

  lifecycle {
    prevent_destroy = true
  }
}

# Faixa do Private Service Access, onde o Cloud SQL recebe o IP privado. Endereço explícito, porque a escolha
# automática não diz a faixa, o PRIVATE_RANGES_ONLY só leva à VPC destinos RFC 1918 e o Cloud SQL só autoriza
# sozinho origens RFC 1918. O /20 vem validado em variables.tf.
resource "google_compute_global_address" "psa" {
  name          = "safrion-hml-psa"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  address       = split("/", var.faixa_psa_cidr)[0]
  prefix_length = 20
  network       = google_compute_network.hml.id

  lifecycle {
    prevent_destroy = true
  }
}

# A conexão não tem custo. prevent_destroy recusa no plan; deletion_policy PREVENT recusa no apply mesmo que o bloco
# saia do código. Desmontar exige apagar a instância e esperar o Cloud SQL liberar a faixa (doc do provider 8.3.0).
resource "google_service_networking_connection" "psa" {
  network                 = google_compute_network.hml.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.psa.name]
  deletion_policy         = "PREVENT"

  lifecycle {
    prevent_destroy = true
  }

  depends_on = [google_project_service.apis]
}
