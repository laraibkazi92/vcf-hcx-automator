import pytest
from unittest.mock import AsyncMock, MagicMock
from vcf_hcx_automator.services.resolution import NameResolutionService
from vcf_hcx_automator.models.inventory import CompleteInventory, VCenterVM, VCenterNetwork

@pytest.fixture
def mock_inventory_service():
    service = AsyncMock()
    # Setup default return values
    service.discover_vms.return_value = [
        VCenterVM(id="vm-1", name="test-vm-1", power_state="POWERED_ON", cpu_count=2, memory_mb=4096, guest_os="Ubuntu"),
        VCenterVM(id="vm-2", name="prod-db-01", power_state="POWERED_ON", cpu_count=4, memory_mb=8192, guest_os="Linux")
    ]
    service.discover_networks.return_value = [
        VCenterNetwork(id="net-1", name="vlan-100", network_type="Standard"),
        VCenterNetwork(id="net-2", name="vlan-200", network_type="Distributed")
    ]
    # Mock cache for synchronous find_similar_names
    service._cache = CompleteInventory(
        vms=service.discover_vms.return_value,
        networks=service.discover_networks.return_value
    )
    return service

@pytest.mark.asyncio
async def test_resolve_vm_by_name_exact(mock_inventory_service):
    resolver = NameResolutionService(mock_inventory_service)
    
    vm = await resolver.resolve_vm_by_name("test-vm-1")
    assert vm is not None
    assert vm.id == "vm-1"
    
    vm = await resolver.resolve_vm_by_name("non-existent")
    assert vm is None

@pytest.mark.asyncio
async def test_resolve_vm_by_name_fuzzy(mock_inventory_service):
    resolver = NameResolutionService(mock_inventory_service)
    
    # "test-vm" should match "test-vm-1"
    vm = await resolver.resolve_vm_by_name("test-vm", exact_match=False)
    assert vm is not None
    assert vm.name == "test-vm-1"

@pytest.mark.asyncio
async def test_resolve_network_by_name(mock_inventory_service):
    resolver = NameResolutionService(mock_inventory_service)
    
    net = await resolver.resolve_network_by_name("vlan-100")
    assert net is not None
    assert net.id == "net-1"

def test_find_similar_names(mock_inventory_service):
    resolver = NameResolutionService(mock_inventory_service)
    
    matches = resolver.find_similar_names("test-vm", "vm")
    assert "test-vm-1" in matches
    
    matches = resolver.find_similar_names("vlan", "network")
    assert "vlan-100" in matches
    assert "vlan-200" in matches
