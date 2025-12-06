from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from vcf_hcx_automator.services.inventory import InventoryDiscoveryService

class CompatibilityResult(BaseModel):
    is_compatible: bool
    reason: Optional[str] = None
    warnings: List[str] = []

class MigrationRecommendation(BaseModel):
    vm_id: str
    recommended_network_id: Optional[str] = None
    recommended_datastore_id: Optional[str] = None
    recommended_compute_id: Optional[str] = None
    reason: str

class ResourceCompatibilityService:
    """Resource compatibility checking for migrations"""
    
    def __init__(self, inventory_service: InventoryDiscoveryService):
        self.inventory = inventory_service
    
    async def check_vm_network_compatibility(self, vm_id: str, target_network_id: str) -> CompatibilityResult:
        """Check if VM can connect to target network"""
        # In a real implementation, this would check VLANs, subnets, etc.
        # For now, we'll just check if both exist.
        vms = await self.inventory.discover_vms(use_cache=True)
        networks = await self.inventory.discover_networks(use_cache=True)
        
        vm = next((v for v in vms if v.id == vm_id), None)
        network = next((n for n in networks if n.id == target_network_id), None)
        
        if not vm:
            return CompatibilityResult(is_compatible=False, reason=f"VM {vm_id} not found")
        if not network:
            return CompatibilityResult(is_compatible=False, reason=f"Network {target_network_id} not found")
            
        return CompatibilityResult(is_compatible=True)
    
    async def check_vm_datastore_compatibility(self, vm_id: str, target_datastore_id: str) -> CompatibilityResult:
        """Check if VM can be stored on target datastore"""
        vms = await self.inventory.discover_vms(use_cache=True)
        datastores = await self.inventory.discover_datastores(use_cache=True)
        
        vm = next((v for v in vms if v.id == vm_id), None)
        datastore = next((d for d in datastores if d.id == target_datastore_id), None)
        
        if not vm:
            return CompatibilityResult(is_compatible=False, reason=f"VM {vm_id} not found")
        if not datastore:
            return CompatibilityResult(is_compatible=False, reason=f"Datastore {target_datastore_id} not found")
            
        # Simple capacity check (assuming VM size is available and datastore free space is available)
        # Note: VCenterVM has memory_mb but not disk size in the current model. 
        # We'll skip size check for now or assume a default.
        
        return CompatibilityResult(is_compatible=True)
    
    async def check_vm_compute_compatibility(self, vm_id: str, target_compute_id: str) -> CompatibilityResult:
        """Check if VM can run on target compute resource"""
        vms = await self.inventory.discover_vms(use_cache=True)
        clusters = await self.inventory.discover_compute_resources(use_cache=True)
        
        vm = next((v for v in vms if v.id == vm_id), None)
        cluster = next((c for c in clusters if c.id == target_compute_id), None)
        
        if not vm:
            return CompatibilityResult(is_compatible=False, reason=f"VM {vm_id} not found")
        if not cluster:
            return CompatibilityResult(is_compatible=False, reason=f"Cluster {target_compute_id} not found")
            
        return CompatibilityResult(is_compatible=True)
    
    async def get_migration_recommendations(self, vm_id: str) -> List[MigrationRecommendation]:
        """Get migration recommendations for a VM"""
        # Placeholder for recommendation logic
        return []
