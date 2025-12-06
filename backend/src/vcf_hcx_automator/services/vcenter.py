from typing import List, Optional, Dict, Any
from vcf_hcx_automator.services.base import BaseHTTPClient
from vcf_hcx_automator.config import settings
from vcf_hcx_automator.models import (
    VCenterVM, VCenterNetwork, VCenterDatastore, VCenterCluster,
    VCenterResourcePool, VCenterFolder, VCenterDatacenter,
    VMFilters, NetworkFilters, DatastoreFilters, ClusterFilters,
    ResourcePoolFilters, FolderFilters, DatacenterFilters
)

class VCenterClient(BaseHTTPClient):
    """vCenter REST API client for inventory discovery"""

    def __init__(self):
        super().__init__(
            base_url=f"https://{settings.vcf_host}/rest",
            verify_ssl=settings.vcf_verify_ssl
        )
        self.session_id: Optional[str] = None

    async def authenticate(self) -> bool:
        """Authenticate with vCenter and establish session"""
        try:
            # Basic auth to get session
            response = await self.client.post(
                "/com/vmware/cis/session",
                auth=(settings.vcf_username, settings.vcf_password)
            )
            response.raise_for_status()
            self.session_id = response.json()["value"]
            self.client.headers["vmware-api-session-id"] = self.session_id
            return True
        except Exception as e:
            self.logger.error(f"vCenter authentication failed: {str(e)}")
            return False

    async def get_vms(self, filters: Optional[VMFilters] = None) -> List[VCenterVM]:
        """Get VM inventory with optional filtering"""
        params = {}
        if filters and filters.names:
            params["names"] = filters.names
        
        # Note: The actual vCenter REST API filtering capabilities might be limited
        # We might need to fetch all and filter client-side for some criteria
        
        data = await self.get("/vcenter/vm", params=params)
        vms = []
        for item in data.get("value", []):
            # We might need to fetch details for each VM if the list response is sparse
            # For now, let's assume we map what we have
            vms.append(VCenterVM(
                id=item.get("vm"),
                name=item.get("name"),
                power_state=item.get("power_state", "POWERED_OFF"),
                cpu_count=item.get("cpu_count", 0),
                memory_mb=item.get("memory_size_MiB", 0),
                guest_os=item.get("guest_OS", "UNKNOWN")
            ))
        return vms

    async def get_networks(self, filters: Optional[NetworkFilters] = None) -> List[VCenterNetwork]:
        """Get network inventory"""
        data = await self.get("/vcenter/network")
        networks = []
        for item in data.get("value", []):
            networks.append(VCenterNetwork(
                id=item.get("network"),
                name=item.get("name"),
                network_type=item.get("type", "STANDARD_PORTGROUP")
            ))
        return networks

    async def get_datastores(self, filters: Optional[DatastoreFilters] = None) -> List[VCenterDatastore]:
        """Get datastore inventory"""
        data = await self.get("/vcenter/datastore")
        datastores = []
        for item in data.get("value", []):
            datastores.append(VCenterDatastore(
                id=item.get("datastore"),
                name=item.get("name"),
                capacity=item.get("capacity", 0),
                free_space=item.get("free_space", 0),
                type_info=item.get("type")
            ))
        return datastores

    async def get_clusters(self, filters: Optional[ClusterFilters] = None) -> List[VCenterCluster]:
        """Get cluster inventory"""
        data = await self.get("/vcenter/cluster")
        clusters = []
        for item in data.get("value", []):
            clusters.append(VCenterCluster(
                id=item.get("cluster"),
                name=item.get("name"),
                resource_pool_id=item.get("resource_pool")
            ))
        return clusters

    async def get_resource_pools(self, filters: Optional[ResourcePoolFilters] = None) -> List[VCenterResourcePool]:
        """Get resource pool inventory"""
        data = await self.get("/vcenter/resource-pool")
        pools = []
        for item in data.get("value", []):
            pools.append(VCenterResourcePool(
                id=item.get("resource_pool"),
                name=item.get("name")
            ))
        return pools

    async def get_folders(self, filters: Optional[FolderFilters] = None) -> List[VCenterFolder]:
        """Get folder inventory"""
        data = await self.get("/vcenter/folder")
        folders = []
        for item in data.get("value", []):
            folders.append(VCenterFolder(
                id=item.get("folder"),
                name=item.get("name"),
                type=item.get("type", "VIRTUAL_MACHINE") # VIRTUAL_MACHINE, NETWORK, DATASTORE, HOST
            ))
        return folders

    async def get_datacenters(self, filters: Optional[DatacenterFilters] = None) -> List[VCenterDatacenter]:
        """Get datacenter inventory"""
        data = await self.get("/vcenter/datacenter")
        datacenters = []
        for item in data.get("value", []):
            datacenters.append(VCenterDatacenter(
                id=item.get("datacenter"),
                name=item.get("name")
            ))
        return datacenters
