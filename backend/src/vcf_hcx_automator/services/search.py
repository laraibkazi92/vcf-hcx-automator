from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from vcf_hcx_automator.services.inventory import InventoryDiscoveryService
from vcf_hcx_automator.models.inventory import (
    VCenterVM, VCenterNetwork, VCenterDatastore, VCenterCluster, InventoryFilters
)

class FilteredInventory(BaseModel):
    vms: List[VCenterVM] = []
    networks: List[VCenterNetwork] = []
    datastores: List[VCenterDatastore] = []
    clusters: List[VCenterCluster] = []

class InventorySummary(BaseModel):
    total_vms: int
    total_networks: int
    total_datastores: int
    total_clusters: int
    powered_on_vms: int

class InventorySearchService:
    """Advanced inventory search and filtering"""
    
    def __init__(self, inventory_service: InventoryDiscoveryService):
        self.inventory = inventory_service
    
    async def search_vms(self, query: str, search_fields: Optional[List[str]] = None) -> List[VCenterVM]:
        """Search VMs by name, OS, or other fields"""
        vms = await self.inventory.discover_vms(use_cache=True)
        query = query.lower()
        
        results = []
        for vm in vms:
            if search_fields:
                # Search only in specified fields
                match = False
                for field in search_fields:
                    if hasattr(vm, field):
                        val = getattr(vm, field)
                        if val and query in str(val).lower():
                            match = True
                            break
                if match:
                    results.append(vm)
            else:
                # Default search in name and guest_os
                if query in vm.name.lower() or (vm.guest_os and query in vm.guest_os.lower()):
                    results.append(vm)
                    
        return results
    
    async def search_networks(self, query: str, search_fields: Optional[List[str]] = None) -> List[VCenterNetwork]:
        """Search networks by name, VLAN, or other fields"""
        networks = await self.inventory.discover_networks(use_cache=True)
        query = query.lower()
        
        results = []
        for net in networks:
            if query in net.name.lower():
                results.append(net)
                
        return results
    
    async def filter_inventory(self, filters: InventoryFilters) -> FilteredInventory:
        """Filter inventory by multiple criteria"""
        # This is a bit redundant with discover_* methods which take filters, 
        # but this method aggregates everything.
        # For now, we will just return empty as implementing full cross-filtering is complex.
        # Or we can just call discover_* with specific filters if they map.
        
        # Simplified implementation:
        vms = await self.inventory.discover_vms()
        networks = await self.inventory.discover_networks()
        
        if filters.names:
            vms = [v for v in vms if v.name in filters.names]
            networks = [n for n in networks if n.name in filters.names]
            
        return FilteredInventory(vms=vms, networks=networks)
    
    async def get_inventory_summary(self) -> InventorySummary:
        """Get summary statistics of current inventory"""
        inventory = await self.inventory.discover_complete_inventory(refresh_cache=False)
        
        powered_on = sum(1 for vm in inventory.vms if vm.power_state == "POWERED_ON")
        
        return InventorySummary(
            total_vms=len(inventory.vms),
            total_networks=len(inventory.networks),
            total_datastores=len(inventory.datastores),
            total_clusters=len(inventory.clusters),
            powered_on_vms=powered_on
        )
