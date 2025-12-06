import pytest
from unittest.mock import AsyncMock, MagicMock
from vcf_hcx_automator.services.inventory import InventoryDiscoveryService
from vcf_hcx_automator.models.inventory import CompleteInventory, VCenterVM, VCenterNetwork

@pytest.fixture
def mock_unified_client():
    client = AsyncMock()
    # Setup default return value
    inventory = CompleteInventory(
        vms=[
            VCenterVM(id="vm-1", name="test-vm-1", power_state="POWERED_ON", cpu_count=2, memory_mb=4096, guest_os="Ubuntu"),
            VCenterVM(id="vm-2", name="test-vm-2", power_state="POWERED_OFF", cpu_count=1, memory_mb=2048, guest_os="Windows")
        ],
        networks=[
            VCenterNetwork(id="net-1", name="test-net-1", network_type="Standard"),
            VCenterNetwork(id="net-2", name="test-net-2", network_type="Distributed")
        ]
    )
    client.get_complete_inventory.return_value = inventory
    return client

@pytest.mark.asyncio
async def test_discover_complete_inventory(mock_unified_client):
    service = InventoryDiscoveryService(mock_unified_client)
    inventory = await service.discover_complete_inventory()
    
    assert len(inventory.vms) == 2
    assert len(inventory.networks) == 2
    mock_unified_client.get_complete_inventory.assert_called_once()

@pytest.mark.asyncio
async def test_caching(mock_unified_client):
    service = InventoryDiscoveryService(mock_unified_client)
    
    # First call
    await service.discover_complete_inventory()
    mock_unified_client.get_complete_inventory.assert_called_once()
    
    # Second call (should use cache)
    await service.discover_complete_inventory()
    mock_unified_client.get_complete_inventory.assert_called_once()
    
    # Refresh cache
    await service.discover_complete_inventory(refresh_cache=True)
    assert mock_unified_client.get_complete_inventory.call_count == 2

@pytest.mark.asyncio
async def test_discover_vms_filtering(mock_unified_client):
    service = InventoryDiscoveryService(mock_unified_client)
    from vcf_hcx_automator.models.inventory import VMFilters
    
    # Filter by name
    filters = VMFilters(names=["test-vm-1"])
    vms = await service.discover_vms(filters=filters)
    assert len(vms) == 1
    assert vms[0].name == "test-vm-1"
    
    # Filter by power state
    filters = VMFilters(power_states=["POWERED_OFF"])
    vms = await service.discover_vms(filters=filters)
    assert len(vms) == 1
    assert vms[0].name == "test-vm-2"

@pytest.mark.asyncio
async def test_discover_networks_filtering(mock_unified_client):
    service = InventoryDiscoveryService(mock_unified_client)
    from vcf_hcx_automator.models.inventory import NetworkFilters
    
    filters = NetworkFilters(names=["test-net-1"])
    networks = await service.discover_networks(filters=filters)
    assert len(networks) == 1
    assert networks[0].name == "test-net-1"
