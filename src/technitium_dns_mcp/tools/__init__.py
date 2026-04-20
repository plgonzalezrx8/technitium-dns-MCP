from technitium_dns_mcp.tools.diagnostics import register_diagnostic_tools
from technitium_dns_mcp.tools.mutations import register_zone_mutation_tools
from technitium_dns_mcp.tools.zones import register_zone_tools

__all__ = [
    "register_diagnostic_tools",
    "register_zone_mutation_tools",
    "register_zone_tools",
]
