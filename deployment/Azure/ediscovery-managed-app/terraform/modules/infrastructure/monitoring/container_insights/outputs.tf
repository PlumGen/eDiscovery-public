output "workspace_id" {
  value = azurerm_log_analytics_workspace.ci.id
}

output "workspace_name" {
  value = azurerm_log_analytics_workspace.ci.name
}

output "workspace_customer_id" {
  value = azurerm_log_analytics_workspace.ci.workspace_id
}

output "workspace_region" {
  value = azurerm_log_analytics_workspace.ci.location
}



output "arc_agent_cert" {
  value     = tls_self_signed_cert.arc.cert_pem
  sensitive = true
}

output "arc_agent_private_key" {
  value     = tls_private_key.arc.private_key_pem
  sensitive = true
}