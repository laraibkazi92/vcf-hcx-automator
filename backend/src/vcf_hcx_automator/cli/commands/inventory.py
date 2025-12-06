import typer
from pathlib import Path
from typing import Optional
import asyncio
from rich.console import Console

from ...services.inventory import InventoryDiscoveryService
from ...services.unified import UnifiedAPIClient
from ...services.vcenter import VCenterClient
from ...services.nsx import NSXClient
from ...services.hcx import HCXClient
from ...config import settings
from ..formatting import OutputFormatter
from ..app import coro

app = typer.Typer(help="Inventory management commands")
console = Console()
formatter = OutputFormatter()

@app.command("discover")
@coro
async def discover_inventory(
    vcenter_server: str = typer.Option(..., "--vcenter-server", help="vCenter server hostname"),
    nsx_manager: Optional[str] = typer.Option(None, "--nsx-manager", help="NSX manager hostname"),
    resource_type: str = typer.Option("all", "--resource-type", help="Resource type to discover (all, vm, network, datastore, compute)"),
    datacenter: Optional[str] = typer.Option(None, "--datacenter", help="Filter by datacenter"),
    cluster: Optional[str] = typer.Option(None, "--cluster", help="Filter by cluster"),
    format: str = typer.Option("table", "--format", help="Output format (table, json, yaml)"),
    output_file: Optional[Path] = typer.Option(None, "--output-file", help="Save output to file"),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
    cache_only: bool = typer.Option(False, "--cache-only", help="Use only cached data"),
    refresh_cache: bool = typer.Option(False, "--refresh-cache", help="Refresh cache before discovery")
):
    """Discover and display infrastructure inventory."""
    
    if verbose:
        formatter.display_info(f"Discovering inventory from {vcenter_server}")

    # Initialize clients
    # In a real app, we might want to dependency inject these or load from config
    # For now, we instantiate them here
    vcenter_client = VCenterClient(host=vcenter_server, username=settings.vcf_username, password=settings.vcf_password, verify_ssl=settings.vcf_verify_ssl)
    
    nsx_client = None
    if nsx_manager:
        nsx_client = NSXClient(host=nsx_manager, username=settings.vcf_username, password=settings.vcf_password, verify_ssl=settings.vcf_verify_ssl)
    
    # We need an HCX client for UnifiedAPIClient, but inventory discovery might not strictly need it if only vCenter/NSX
    # But UnifiedAPIClient requires it. We can pass a dummy or None if allowed, or we need HCX info.
    # The spec for UnifiedAPIClient says it takes vcenter, nsx, hcx.
    # Let's assume we can pass None or we need to ask for HCX info if we want full unified client.
    # For inventory discovery, we might just need vCenter and NSX.
    # Let's check UnifiedAPIClient signature.
    
    # For now, I'll pass None for HCX client if not needed, or mock it.
    # Or I'll instantiate it if I have settings.
    hcx_client = HCXClient(host="dummy", username="dummy", password="dummy") # Placeholder if not used
    
    unified_client = UnifiedAPIClient(vcenter_client=vcenter_client, nsx_client=nsx_client, hcx_client=hcx_client)
    
    # We need a cache. The spec says "InventoryCache".
    # I'll check where InventoryCache is defined. Probably in services/inventory.py or utils.
    inventory_service = InventoryDiscoveryService(api_client=unified_client)

    try:
        with formatter.create_progress() as progress:
            task = progress.add_task("Discovering inventory...", total=None)
            
            # Authenticate
            if not cache_only:
                await vcenter_client.authenticate()
                if nsx_client:
                    await nsx_client.authenticate()
            
            # Discover
            if resource_type == "all":
                inventory = await inventory_service.discover_complete_inventory(refresh_cache=refresh_cache)
                data = inventory.dict() # Assuming pydantic model
            elif resource_type == "vm":
                vms = await inventory_service.discover_vms(use_cache=not refresh_cache)
                data = [vm.dict() for vm in vms]
            elif resource_type == "network":
                networks = await inventory_service.discover_networks(use_cache=not refresh_cache)
                data = [n.dict() for n in networks]
            elif resource_type == "datastore":
                datastores = await inventory_service.discover_datastores(use_cache=not refresh_cache)
                data = [d.dict() for d in datastores]
            elif resource_type == "compute":
                compute = await inventory_service.discover_compute_resources(use_cache=not refresh_cache)
                data = [c.dict() for c in compute]
            else:
                formatter.display_error(f"Unknown resource type: {resource_type}")
                return

            progress.update(task, completed=100)

        # Output
        if format == "table":
            if isinstance(data, list):
                formatter.display_table(data, f"{resource_type.title()} Inventory")
            else:
                formatter.display_json(data) # Fallback for complex objects
        elif format == "json":
            formatter.display_json(data)
        elif format == "yaml":
            formatter.display_yaml(data)
            
        if output_file:
            # Save to file
            with open(output_file, "w") as f:
                if format == "json":
                    import json
                    json.dump(data, f, indent=2, default=str)
                elif format == "yaml":
                    import yaml
                    yaml.dump(data, f, sort_keys=False)
                else:
                    f.write(str(data))
            formatter.display_success(f"Output saved to {output_file}")

    except Exception as e:
        formatter.display_error(f"Failed to discover inventory: {e}")
        if verbose:
            console.print_exception()
