import pytest
from unittest.mock import AsyncMock
from vcf_hcx_automator.services.compatibility import ResourceCompatibilityService
from vcf_hcx_automator.models.inventory import VCenterVM, VCenterNetwork, VCenterDatastore, VCenterCluster

@pytest.fixture
def mock_inventory_service():
    service = AsyncMock()
    service.discover_vms.return_value = [
        VCenterVM(id="vm-1", name="test-vm-1", power_state="POWERED_ON", cpu_count=2, memory_mb=4096, guest_os="Ubuntu")
    ]
    service.discover_networks.return_value = [
        VCenterNetwork(id="net-1", name="test-net-1", network_type="Standard")
    ]
    service.discover_datastores.return_value = [
        VCenterDatastore(id="ds-1", name="test-ds-1", capacity=1000, free_space=500, type_info="VMFS")
    ]
    service.discover_compute_resources.return_value = [
        VCenterCluster(id="cluster-1", name="test-cluster-1")
    ]
    return service

@pytest.mark.asyncio
async def test_check_vm_network_compatibility(mock_inventory_service):
    service = ResourceCompatibilityService(mock_inventory_service)
    
    # Valid case
    result = await service.check_vm_network_compatibility("vm-1", "net-1")
    assert result.is_compatible
    
    # Invalid VM
    result = await service.check_vm_network_compatibility("invalid-vm", "net-1")
    assert not result.is_compatible
    assert "VM invalid-vm not found" in result.reason
    
    # Invalid Network
    result = await service.check_vm_network_compatibility("vm-1", "invalid-net")
    assert not result.is_compatible
    assert "Network invalid-net not found" in result.reason

@pytest.mark.asyncio
async def test_check_vm_datastore_compatibility(mock_inventory_service):
    service = ResourceCompatibilityService(mock_inventory_service)
    
    result = await service.check_vm_datastore_compatibility("vm-1", "ds-1")
    assert result.is_compatible

@pytest.mark.asyncio
async def test_check_vm_compute_compatibility(mock_inventory_service):
    service = ResourceCompatibilityService(mock_inventory_service)
    
    result = await service.check_vm_compute_compatibility("vm-1", "cluster-1")
    assert result.is_compatible
