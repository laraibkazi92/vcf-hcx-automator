from typing import Optional, List, Dict, Any
import difflib
from vcf_hcx_automator.services.inventory import InventoryDiscoveryService
from vcf_hcx_automator.models.inventory import (
    VCenterVM, VCenterNetwork, VCenterDatastore, VCenterCluster
)

class NameResolutionService:
    """Intelligent name-to-ID resolution with fuzzy matching"""
    
    def __init__(self, inventory_service: InventoryDiscoveryService):
        self.inventory = inventory_service
    
    async def resolve_vm_by_name(self, vm_name: str, exact_match: bool = True) -> Optional[VCenterVM]:
        """Resolve VM name to VM inventory object"""
        vms = await self.inventory.discover_vms()
        
        # Exact match
        for vm in vms:
            if vm.name == vm_name:
                return vm
                
        if exact_match:
            return None
            
        # Fuzzy match if not exact match required
        similar_names = self.find_similar_names(vm_name, "vm", max_results=1)
        if similar_names:
            best_match_name = similar_names[0]
            for vm in vms:
                if vm.name == best_match_name:
                    return vm
                    
        return None
    
    async def resolve_network_by_name(self, network_name: str, exact_match: bool = True) -> Optional[VCenterNetwork]:
        """Resolve network name to network inventory object"""
        networks = await self.inventory.discover_networks()
        
        for net in networks:
            if net.name == network_name:
                return net
                
        if exact_match:
            return None
            
        similar_names = self.find_similar_names(network_name, "network", max_results=1)
        if similar_names:
            best_match_name = similar_names[0]
            for net in networks:
                if net.name == best_match_name:
                    return net
                    
        return None
    
    async def resolve_datastore_by_name(self, datastore_name: str, exact_match: bool = True) -> Optional[VCenterDatastore]:
        """Resolve datastore name to datastore inventory object"""
        datastores = await self.inventory.discover_datastores()
        
        for ds in datastores:
            if ds.name == datastore_name:
                return ds
                
        if exact_match:
            return None
            
        similar_names = self.find_similar_names(datastore_name, "datastore", max_results=1)
        if similar_names:
            best_match_name = similar_names[0]
            for ds in datastores:
                if ds.name == best_match_name:
                    return ds
                    
        return None
    
    async def resolve_compute_by_name(self, compute_name: str, exact_match: bool = True) -> Optional[VCenterCluster]:
        """Resolve compute resource name to compute inventory object"""
        clusters = await self.inventory.discover_compute_resources()
        
        for cluster in clusters:
            if cluster.name == compute_name:
                return cluster
                
        if exact_match:
            return None
            
        similar_names = self.find_similar_names(compute_name, "compute", max_results=1)
        if similar_names:
            best_match_name = similar_names[0]
            for cluster in clusters:
                if cluster.name == best_match_name:
                    return cluster
                    
        return None
    
    async def resolve_multiple_resources(self, names: Dict[str, str]) -> Dict[str, Any]:
        """Resolve multiple resource names in batch"""
        results = {}
        
        if "vm" in names:
            results["vm"] = await self.resolve_vm_by_name(names["vm"])
        if "network" in names:
            results["network"] = await self.resolve_network_by_name(names["network"])
        if "datastore" in names:
            results["datastore"] = await self.resolve_datastore_by_name(names["datastore"])
        if "compute" in names:
            results["compute"] = await self.resolve_compute_by_name(names["compute"])
            
        return results
    
    def find_similar_names(self, name: str, resource_type: str, max_results: int = 5) -> List[str]:
        """Find similar names for fuzzy matching suggestions"""
        # This needs synchronous access to inventory names, which might be tricky if inventory is async.
        # Ideally, we should cache names or fetch them. 
        # For now, I'll assume we can get them from the cache if populated, or we might need to make this async.
        # However, the interface is synchronous. 
        # Let's check if we can access the cache directly from the inventory service.
        
        if not self.inventory._cache:
             # If cache is empty, we can't really do much synchronously without blocking.
             # In a real app, we might want to ensure cache is warm or make this async.
             # For this implementation, I will return empty list if cache is not warm.
             return []
             
        candidates = []
        if resource_type == "vm":
            candidates = [vm.name for vm in self.inventory._cache.vms]
        elif resource_type == "network":
            candidates = [n.name for n in self.inventory._cache.networks]
        elif resource_type == "datastore":
            candidates = [d.name for d in self.inventory._cache.datastores]
        elif resource_type == "compute":
            candidates = [c.name for c in self.inventory._cache.clusters]
            
        return difflib.get_close_matches(name, candidates, n=max_results, cutoff=0.6)
