# API Coverage

`src/technitium_dns_mcp/client/endpoint_catalog.py` is the source of truth for the exposed Technitium API surface.

Current coverage:

- **116 Technitium API endpoints** mapped to MCP tools
- **34 readonly**, **39 mutation**, **17 destructive**, and **26 admin/critical** endpoint registrations
- **117 live tools** in write-enabled mode once `dns_health_check` is included
- Log read/list/query/export tools stay available, while delete tools are hidden so the server is **readonly-only when TECHNITIUM_READONLY=true**

## Safety interpretation

- **readonly**: always registered
- **mutation**: requires `confirm=True`
- **destructive**: requires destructive confirmation via `confirm=True`
- **admin**: requires `confirm=True` and an acknowledgement string for critical actions

## Family map

| Family | MCP tools | Technitium API paths |
| --- | --- | --- |
| dashboard | `dns_get_top_stats`, `dns_delete_all_stats` | `/api/dashboard/stats/getTop`, `/api/dashboard/stats/deleteAll` |
| zones | `dns_list_zones`, `dns_list_catalog_zones`, `dns_get_zone_options`, `dns_set_zone_options`, `dns_get_zone_permissions`, `dns_set_zone_permissions`, `dns_create_primary_zone`, `dns_create_zone`, `dns_clone_zone`, `dns_convert_zone`, `dns_enable_zone`, `dns_disable_zone`, `dns_delete_zone`, `dns_resync_zone` | `/api/zones/list`, `/api/zones/catalogs/list`, `/api/zones/options/get`, `/api/zones/options/set`, `/api/zones/permissions/get`, `/api/zones/permissions/set`, `/api/zones/create`, `/api/zones/clone`, `/api/zones/convert`, `/api/zones/enable`, `/api/zones/disable`, `/api/zones/delete`, `/api/zones/resync` |
| records | `dns_get_records`, `dns_add_record`, `dns_update_record`, `dns_delete_record` | `/api/zones/records/get`, `/api/zones/records/add`, `/api/zones/records/update`, `/api/zones/records/delete` |
| dnssec | `dns_get_zone_ds_info`, `dns_get_zone_dnssec_properties`, `dns_sign_zone`, `dns_unsign_zone`, `dns_convert_zone_to_nsec`, `dns_convert_zone_to_nsec3`, `dns_update_zone_nsec3_parameters`, `dns_update_zone_dnskey_ttl`, `dns_add_zone_private_key`, `dns_update_zone_private_key`, `dns_delete_zone_private_key`, `dns_publish_all_zone_private_keys`, `dns_rollover_zone_dnskey`, `dns_retire_zone_dnskey` | `/api/zones/dnssec/viewDS`, `/api/zones/dnssec/properties/get`, `/api/zones/dnssec/sign`, `/api/zones/dnssec/unsign`, `/api/zones/dnssec/properties/convertToNSEC`, `/api/zones/dnssec/properties/convertToNSEC3`, `/api/zones/dnssec/properties/updateNSEC3Params`, `/api/zones/dnssec/properties/updateDnsKeyTtl`, `/api/zones/dnssec/properties/addPrivateKey`, `/api/zones/dnssec/properties/updatePrivateKey`, `/api/zones/dnssec/properties/deletePrivateKey`, `/api/zones/dnssec/properties/publishAllPrivateKeys`, `/api/zones/dnssec/properties/rolloverDnsKey`, `/api/zones/dnssec/properties/retireDnsKey` |
| cache | `dns_list_cache`, `dns_delete_cached_zone`, `dns_flush_cache` | `/api/cache/list`, `/api/cache/delete`, `/api/cache/flush` |
| allowed | `dns_list_allowed_zones`, `dns_export_allowed_zones`, `dns_add_allowed_zone`, `dns_delete_allowed_zone`, `dns_flush_allowed_zones`, `dns_import_allowed_zones` | `/api/allowed/list`, `/api/allowed/export`, `/api/allowed/add`, `/api/allowed/delete`, `/api/allowed/flush`, `/api/allowed/import` |
| blocked | `dns_list_blocked_zones`, `dns_export_blocked_zones`, `dns_add_blocked_zone`, `dns_delete_blocked_zone`, `dns_flush_blocked_zones`, `dns_import_blocked_zones` | `/api/blocked/list`, `/api/blocked/export`, `/api/blocked/add`, `/api/blocked/delete`, `/api/blocked/flush`, `/api/blocked/import` |
| apps | `dns_list_apps`, `dns_list_store_apps`, `dns_get_app_config`, `dns_download_and_install_app`, `dns_download_and_update_app`, `dns_install_app`, `dns_update_app`, `dns_uninstall_app`, `dns_set_app_config` | `/api/apps/list`, `/api/apps/listStoreApps`, `/api/apps/config/get`, `/api/apps/downloadAndInstall`, `/api/apps/downloadAndUpdate`, `/api/apps/install`, `/api/apps/update`, `/api/apps/uninstall`, `/api/apps/config/set` |
| dns_client | `dns_resolve_query` | `/api/dnsClient/resolve` |
| settings | `dns_get_settings`, `dns_get_tsig_key_names`, `dns_set_settings`, `dns_force_update_block_lists`, `dns_temporary_disable_blocking`, `dns_backup_settings`, `dns_restore_settings` | `/api/settings/get`, `/api/settings/getTsigKeyNames`, `/api/settings/set`, `/api/settings/forceUpdateBlockLists`, `/api/settings/temporaryDisableBlocking`, `/api/settings/backup`, `/api/settings/restore` |
| logs | `dns_list_logs`, `dns_download_log`, `dns_delete_log`, `dns_delete_all_logs`, `dns_query_logs`, `dns_export_query_logs` | `/api/logs/list`, `/api/logs/download`, `/api/logs/delete`, `/api/logs/deleteAll`, `/api/logs/query`, `/api/logs/export` |
| dhcp | `dns_list_dhcp_leases`, `dns_remove_dhcp_lease`, `dns_convert_dhcp_lease_to_reserved`, `dns_convert_dhcp_lease_to_dynamic`, `dns_list_dhcp_scopes`, `dns_get_dhcp_scope`, `dns_set_dhcp_scope`, `dns_add_dhcp_reserved_lease`, `dns_remove_dhcp_reserved_lease`, `dns_enable_dhcp_scope`, `dns_disable_dhcp_scope`, `dns_delete_dhcp_scope` | `/api/dhcp/leases/list`, `/api/dhcp/leases/remove`, `/api/dhcp/leases/convertToReserved`, `/api/dhcp/leases/convertToDynamic`, `/api/dhcp/scopes/list`, `/api/dhcp/scopes/get`, `/api/dhcp/scopes/set`, `/api/dhcp/scopes/addReservedLease`, `/api/dhcp/scopes/removeReservedLease`, `/api/dhcp/scopes/enable`, `/api/dhcp/scopes/disable`, `/api/dhcp/scopes/delete` |
| admin_sessions | `dns_list_admin_sessions`, `dns_create_admin_api_token`, `dns_delete_admin_session` | `/api/admin/sessions/list`, `/api/admin/sessions/createToken`, `/api/admin/sessions/delete` |
| admin_users | `dns_list_admin_users`, `dns_create_admin_user`, `dns_get_admin_user`, `dns_set_admin_user`, `dns_delete_admin_user` | `/api/admin/users/list`, `/api/admin/users/create`, `/api/admin/users/get`, `/api/admin/users/set`, `/api/admin/users/delete` |
| admin_groups | `dns_list_admin_groups`, `dns_create_admin_group`, `dns_get_admin_group`, `dns_set_admin_group`, `dns_delete_admin_group` | `/api/admin/groups/list`, `/api/admin/groups/create`, `/api/admin/groups/get`, `/api/admin/groups/set`, `/api/admin/groups/delete` |
| admin_permissions | `dns_list_admin_permissions`, `dns_get_admin_permission`, `dns_set_admin_permission` | `/api/admin/permissions/list`, `/api/admin/permissions/get`, `/api/admin/permissions/set` |
| cluster | `dns_get_cluster_state`, `dns_initialize_cluster`, `dns_delete_cluster`, `dns_join_cluster`, `dns_remove_cluster_secondary_node`, `dns_delete_cluster_secondary_node`, `dns_update_cluster_secondary_node`, `dns_transfer_cluster_config`, `dns_set_cluster_options`, `dns_initialize_and_join_cluster`, `dns_leave_cluster`, `dns_notify_cluster`, `dns_resync_cluster`, `dns_update_cluster_primary_node`, `dns_promote_to_cluster_primary`, `dns_update_cluster_node_ip_addresses` | `/api/admin/cluster/state`, `/api/admin/cluster/init`, `/api/admin/cluster/primary/delete`, `/api/admin/cluster/primary/join`, `/api/admin/cluster/primary/removeSecondary`, `/api/admin/cluster/primary/deleteSecondary`, `/api/admin/cluster/primary/updateSecondary`, `/api/admin/cluster/primary/transferConfig`, `/api/admin/cluster/primary/setOptions`, `/api/admin/cluster/initJoin`, `/api/admin/cluster/secondary/leave`, `/api/admin/cluster/secondary/notify`, `/api/admin/cluster/secondary/resync`, `/api/admin/cluster/secondary/updatePrimary`, `/api/admin/cluster/secondary/promote`, `/api/admin/cluster/updateIpAddress` |

## Notes for deployment

- Treat `endpoint_catalog.py` as the contract between tool registration, docs, and audit tests.
- When adding a new Technitium endpoint, update the endpoint catalog, the relevant tool module, readonly gating in `app.py`, and the live tool-surface audit.
- For mcp-behemoth deployment, prefer `TECHNITIUM_READONLY=true` first, then enable writes only after validating required acknowledgement strings and downstream RBAC expectations.
