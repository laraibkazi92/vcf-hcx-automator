import pytest
from unittest.mock import AsyncMock
from vcf_hcx_automator.services.search import InventorySearchService
from vcf_hcx_automator.models.inventory import CompleteInventory, VCenterVM, VCenterNetwork, VCenterDatastore, VCenterCluster

@pytest.fixture
def mock_inventory_service():
    service = AsyncMock()
    service.discover_vms.return_value = [
        VCenterVM(id="vm-1", name="test-vm-1", power_state="POWERED_ON", cpu_count=2, memory_mb=4096, guest_os="Ubuntu"),
        VCenterVM(id="vm-2", name="prod-db-01", power_state="POWERED_ON", cpu_count=4, memory_mb=8192, guest_os="Windows")
    ]
    service.discover_networks.return_value = [
        VCenterNetwork(id="net-1", name="vlan-100", network_type="Standard"),
        VCenterNetwork(id="net-2", name="vlan-200", network_type="Distributed")
    ]
    service.discover_datastores.return_value = [
        VCenterDatastore(id="ds-1", name="ds-1", capacity=1000, free_space=500, type_info="VMFS")
    ]
    service.discover_compute_resources.return_value = [
        VCenterCluster(id="cluster-1", name="cluster-1")
    ]
    service.discover_complete_inventory.return_value = CompleteInventory(
        vms=service.discover_vms.return_value,
        networks=service.discover_networks.return_value,
        datastores=service.discover_datastores.return_value,
        clusters=service.discover_compute_resources.return_value
    )
    return service

@pytest.mark.asyncio
async def test_search_vms(mock_inventory_service):
    service = InventorySearchService(mock_inventory_service)
    
    # Search by name
    results = await service.search_vms("test")
    assert len(results) == 1
    assert results[0].name == "test-vm-1"
    
    # Search by OS
    results = await service.search_vms("windows")
    assert len(results) == 1
    assert results[0].name == "prod-db-01"
    
    # Search specific field
    results = await service.search_vms("ubuntu", search_fields=["guest_os"])
    assert len(results) == 1
    
    # Search specific field (no match)
    results = await service.search_vms("ubuntu", search_fields=["name"])
    assert len(results) == 0

@pytest.mark.asyncio
async def test_search_networks(mock_inventory_service):
    service = InventorySearchService(mock_inventory_service)
    
    results = await service.search_networks("vlan")
    assert len(results) == 2
    
    results = await service.search_networks("100")
    assert len(results) == 1
    assert results[0].name == "vlan-100"

@pytest.mark.asyncio
async def test_get_inventory_summary(mock_inventory_service):
    service = InventorySearchService(mock_inventory_service)
    
    summary = await service.get_inventory_summary()
    assert summary.total_vms == 2
    assert summary.total_networks == 2
    assert summary.total_datastores == 1
    assert summary.total_clusters == 1
    assert summary.powered_on_vms == 2
