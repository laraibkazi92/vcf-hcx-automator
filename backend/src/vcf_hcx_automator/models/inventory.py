from typing import List, Optional, Dict, Any
from pydantic import Field
from .base import BaseDataModel

# --- vCenter Models ---

class VCenterEntity(BaseDataModel):
    """Base model for vCenter entities"""
    id: str
    name: str
    type: str

class VCenterDatacenter(VCenterEntity):
    """vCenter Datacenter model"""
    type: str = "Datacenter"

class VCenterFolder(VCenterEntity):
    """vCenter Folder model"""
    type: str = "Folder"
    parent_id: Optional[str] = None

class VCenterCluster(VCenterEntity):
    """vCenter Cluster model"""
    type: str = "ClusterComputeResource"
    resource_pool_id: Optional[str] = None
    datastore_ids: List[str] = Field(default_factory=list)
    network_ids: List[str] = Field(default_factory=list)

class VCenterResourcePool(VCenterEntity):
    """vCenter Resource Pool model"""
    type: str = "ResourcePool"
    cluster_id: Optional[str] = None

class VCenterDatastore(VCenterEntity):
    """vCenter Datastore model"""
    type: str = "Datastore"
    capacity: int
    free_space: int
    type_info: Optional[str] = None  # VMFS, NFS, vSAN, etc.

class VCenterNetwork(VCenterEntity):
    """vCenter Network model"""
    type: str = "Network"
    network_type: str  # Standard, Distributed, Opaque

class VCenterVM(VCenterEntity):
    """vCenter Virtual Machine model"""
    type: str = "VirtualMachine"
    power_state: str
    cpu_count: int
    memory_mb: int
    guest_os: str
    folder_id: Optional[str] = None
    resource_pool_id: Optional[str] = None
    cluster_id: Optional[str] = None
    host_id: Optional[str] = None
    datastore_ids: List[str] = Field(default_factory=list)
    network_ids: List[str] = Field(default_factory=list)
    is_template: bool = False

# --- Filter Models ---

class InventoryFilters(BaseDataModel):
    """Base filters for inventory discovery"""
    names: Optional[List[str]] = None
    ids: Optional[List[str]] = None
    tags: Optional[Dict[str, str]] = None

class VMFilters(InventoryFilters):
    """Filters for VM discovery"""
    power_states: Optional[List[str]] = None
    guest_os_patterns: Optional[List[str]] = None
    cluster_ids: Optional[List[str]] = None
    host_ids: Optional[List[str]] = None
    folder_ids: Optional[List[str]] = None
    resource_pool_ids: Optional[List[str]] = None
    datastore_ids: Optional[List[str]] = None
    network_ids: Optional[List[str]] = None
    min_cpu: Optional[int] = None
    min_memory_mb: Optional[int] = None

class NetworkFilters(InventoryFilters):
    """Filters for Network discovery"""
    network_types: Optional[List[str]] = None

class DatastoreFilters(InventoryFilters):
    """Filters for Datastore discovery"""
    types: Optional[List[str]] = None
    min_free_space: Optional[int] = None

class ClusterFilters(InventoryFilters):
    """Filters for Cluster discovery"""
    pass

class ResourcePoolFilters(InventoryFilters):
    """Filters for Resource Pool discovery"""
    cluster_ids: Optional[List[str]] = None

class FolderFilters(InventoryFilters):
    """Filters for Folder discovery"""
    parent_ids: Optional[List[str]] = None

class DatacenterFilters(InventoryFilters):
    """Filters for Datacenter discovery"""
    pass

class ComputeFilters(InventoryFilters):
    """Filters for Compute discovery"""
    cluster_ids: Optional[List[str]] = None

# --- NSX Models ---

class NSXEntity(BaseDataModel):
    """Base model for NSX entities"""
    id: str
    display_name: str
    resource_type: str

class NSXLogicalSwitch(NSXEntity):
    """NSX Logical Switch model"""
    resource_type: str = "LogicalSwitch"
    transport_zone_id: str
    vlan: Optional[int] = None

class NSXTransportZone(NSXEntity):
    """NSX Transport Zone model"""
    resource_type: str = "TransportZone"
    tz_type: str  # OVERLAY, VLAN

class NSXSegment(NSXEntity):
    """NSX Segment model"""
    resource_type: str = "Segment"
    transport_zone_path: Optional[str] = None
    subnets: List[Dict[str, Any]] = Field(default_factory=list)

class NSXSwitchingProfile(NSXEntity):
    """NSX Switching Profile model"""
    resource_type: str = "SwitchingProfile"
    category: str

# --- HCX Models ---

class HCXSiteSystem(BaseDataModel):
    """HCX Site System model"""
    system_id: str
    name: str
    type: str  # source, destination
    url: str
    state: str
    version: str

class HCXServiceMesh(BaseDataModel):
    """HCX Service Mesh model"""
    mesh_id: str
    name: str
    source_site_id: str
    destination_site_id: str
    status: str
    appliances: List[Dict[str, Any]] = Field(default_factory=list)

class HCXMobilityGroup(BaseDataModel):
    """HCX Mobility Group model"""
    group_id: str
    name: str
    source_site_id: str
    destination_site_id: str
    service_mesh_id: str
    migration_type: str
    state: str
    migrations: List[Dict[str, Any]] = Field(default_factory=list)

class HCXMobilityGroupRequest(BaseDataModel):
    """Request model for creating/updating mobility groups"""
    name: str
    source_site_id: str
    destination_site_id: str
    service_mesh_id: str
    migration_type: str
    vm_ids: List[str]
    schedule_time: Optional[str] = None
    # Add other migration parameters as needed

class HCXValidationResult(BaseDataModel):
    """HCX Validation Result model"""
    is_valid: bool
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)

class HCXMigrationResult(BaseDataModel):
    """HCX Migration Result model"""
    migration_id: str
    status: str
    message: Optional[str] = None

# --- Unified Models ---

class CompleteInventory(BaseDataModel):
    """Complete inventory from all sources"""
    datacenters: List[VCenterDatacenter] = Field(default_factory=list)
    clusters: List[VCenterCluster] = Field(default_factory=list)
    hosts: List[Dict[str, Any]] = Field(default_factory=list) # Placeholder for Host model if needed
    resource_pools: List[VCenterResourcePool] = Field(default_factory=list)
    folders: List[VCenterFolder] = Field(default_factory=list)
    datastores: List[VCenterDatastore] = Field(default_factory=list)
    networks: List[VCenterNetwork] = Field(default_factory=list)
    vms: List[VCenterVM] = Field(default_factory=list)
    nsx_segments: List[NSXSegment] = Field(default_factory=list)
    hcx_sites: List[HCXSiteSystem] = Field(default_factory=list)

class InventorySummary(BaseDataModel):
    """Summary statistics of inventory"""
    total_vms: int
    total_networks: int
    total_datastores: int
    total_clusters: int
    total_segments: int
    total_sites: int
