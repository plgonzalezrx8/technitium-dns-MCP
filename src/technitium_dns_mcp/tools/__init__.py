from technitium_dns_mcp.tools.admin_cluster import (
    register_admin_cluster_mutation_tools,
    register_admin_cluster_tools,
)
from technitium_dns_mcp.tools.admin_groups import (
    register_admin_group_mutation_tools,
    register_admin_group_tools,
)
from technitium_dns_mcp.tools.admin_permissions import (
    register_admin_permission_mutation_tools,
    register_admin_permission_tools,
)
from technitium_dns_mcp.tools.admin_sessions import (
    register_admin_session_mutation_tools,
    register_admin_session_tools,
)
from technitium_dns_mcp.tools.admin_users import (
    register_admin_user_mutation_tools,
    register_admin_user_tools,
)
from technitium_dns_mcp.tools.allowed import (
    register_allowed_mutation_tools,
    register_allowed_tools,
)
from technitium_dns_mcp.tools.apps import register_app_mutation_tools, register_app_tools
from technitium_dns_mcp.tools.blocked import (
    register_blocked_mutation_tools,
    register_blocked_tools,
)
from technitium_dns_mcp.tools.cache import register_cache_mutation_tools, register_cache_tools
from technitium_dns_mcp.tools.dhcp import register_dhcp_mutation_tools, register_dhcp_tools
from technitium_dns_mcp.tools.diagnostics import register_diagnostic_tools
from technitium_dns_mcp.tools.dns_client import register_dns_client_tools
from technitium_dns_mcp.tools.logs import register_log_mutation_tools, register_log_tools
from technitium_dns_mcp.tools.mutations import register_zone_mutation_tools
from technitium_dns_mcp.tools.settings import (
    register_settings_mutation_tools,
    register_settings_tools,
)
from technitium_dns_mcp.tools.zone_dnssec import (
    register_zone_dnssec_mutation_tools,
    register_zone_dnssec_tools,
)
from technitium_dns_mcp.tools.zones import register_zone_tools

__all__ = [
    "register_admin_cluster_mutation_tools",
    "register_admin_cluster_tools",
    "register_admin_group_mutation_tools",
    "register_admin_group_tools",
    "register_admin_permission_mutation_tools",
    "register_admin_permission_tools",
    "register_admin_session_mutation_tools",
    "register_admin_session_tools",
    "register_admin_user_mutation_tools",
    "register_admin_user_tools",
    "register_allowed_mutation_tools",
    "register_allowed_tools",
    "register_app_mutation_tools",
    "register_app_tools",
    "register_blocked_mutation_tools",
    "register_blocked_tools",
    "register_cache_mutation_tools",
    "register_cache_tools",
    "register_dhcp_mutation_tools",
    "register_dhcp_tools",
    "register_diagnostic_tools",
    "register_dns_client_tools",
    "register_log_mutation_tools",
    "register_log_tools",
    "register_settings_mutation_tools",
    "register_settings_tools",
    "register_zone_dnssec_mutation_tools",
    "register_zone_dnssec_tools",
    "register_zone_mutation_tools",
    "register_zone_tools",
]
