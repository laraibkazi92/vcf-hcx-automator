from typing import Dict, Any
import asyncio
from vcf_hcx_automator.services.vcenter import VCenterClient
from vcf_hcx_automator.services.nsx import NSXClient
from vcf_hcx_automator.services.hcx import HCXClient
from vcf_hcx_automator.models import CompleteInventory

class UnifiedAPIClient:
    """Unified interface for all VMware API clients"""

    def __init__(
        self, 
        vcenter_client: VCenterClient, 
        nsx_client: NSXClient, 
        hcx_client: HCXClient
    ):
        self.vcenter = vcenter_client
        self.nsx = nsx_client
        self.hcx = hcx_client

    async def authenticate_all(self) -> Dict[str, bool]:
        """Authenticate with all API clients"""
        results = await asyncio.gather(
            self.vcenter.authenticate(),
            self.nsx.authenticate(),
            self.hcx.authenticate(),
            return_exceptions=True
        )
        
        return {
            "vcenter": results[0] if isinstance(results[0], bool) else False,
            "nsx": results[1] if isinstance(results[1], bool) else False,
            "hcx": results[2] if isinstance(results[2], bool) else False
        }

    async def get_complete_inventory(self) -> CompleteInventory:
        """Get complete inventory from all sources"""
        # Fetch all inventory in parallel
        # Note: Some calls might depend on others in a real scenario, but for discovery we can usually parallelize
        
        # vCenter calls
        vcenter_tasks = [
            self.vcenter.get_datacenters(),
            self.vcenter.get_clusters(),
            self.vcenter.get_resource_pools(),
            self.vcenter.get_folders(),
            self.vcenter.get_datastores(),
            self.vcenter.get_networks(),
            self.vcenter.get_vms()
        ]
        
        # NSX calls
        nsx_tasks = [
            self.nsx.get_segments()
        ]
        
        # HCX calls
        hcx_tasks = [
            self.hcx.get_site_systems()
        ]
        
        all_tasks = vcenter_tasks + nsx_tasks + hcx_tasks
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # Unpack results
        # vCenter
        datacenters = results[0] if not isinstance(results[0], Exception) else []
        clusters = results[1] if not isinstance(results[1], Exception) else []
        resource_pools = results[2] if not isinstance(results[2], Exception) else []
        folders = results[3] if not isinstance(results[3], Exception) else []
        datastores = results[4] if not isinstance(results[4], Exception) else []
        networks = results[5] if not isinstance(results[5], Exception) else []
        vms = results[6] if not isinstance(results[6], Exception) else []
        
        # NSX
        nsx_segments = results[7] if not isinstance(results[7], Exception) else []
        
        # HCX
        hcx_sites = results[8] if not isinstance(results[8], Exception) else []
        
        return CompleteInventory(
            datacenters=datacenters,
            clusters=clusters,
            resource_pools=resource_pools,
            folders=folders,
            datastores=datastores,
            networks=networks,
            vms=vms,
            nsx_segments=nsx_segments,
            hcx_sites=hcx_sites
        )
