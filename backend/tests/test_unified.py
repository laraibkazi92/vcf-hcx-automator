import pytest
from unittest.mock import AsyncMock, MagicMock
from vcf_hcx_automator.services.unified import UnifiedAPIClient
from vcf_hcx_automator.models import (
    CompleteInventory, VCenterVM, NSXSegment, HCXSiteSystem
)

@pytest.fixture
def mock_clients():
    """Mock API clients."""
    vcenter = MagicMock()
    vcenter.authenticate = AsyncMock(return_value=True)
    vcenter.get_datacenters = AsyncMock(return_value=[])
    vcenter.get_clusters = AsyncMock(return_value=[])
    vcenter.get_resource_pools = AsyncMock(return_value=[])
    vcenter.get_folders = AsyncMock(return_value=[])
    vcenter.get_datastores = AsyncMock(return_value=[])
    vcenter.get_networks = AsyncMock(return_value=[])
    vcenter.get_vms = AsyncMock(return_value=[])

    nsx = MagicMock()
    nsx.authenticate = AsyncMock(return_value=True)
    nsx.get_segments = AsyncMock(return_value=[])

    hcx = MagicMock()
    hcx.authenticate = AsyncMock(return_value=True)
    hcx.get_site_systems = AsyncMock(return_value=[])

    return vcenter, nsx, hcx

@pytest.fixture
def unified_client(mock_clients):
    """Create UnifiedAPIClient instance for testing."""
    vcenter, nsx, hcx = mock_clients
    return UnifiedAPIClient(vcenter, nsx, hcx)

@pytest.mark.asyncio
async def test_authenticate_all_success(unified_client):
    """Test successful authentication of all clients."""
    results = await unified_client.authenticate_all()
    
    assert results["vcenter"] is True
    assert results["nsx"] is True
    assert results["hcx"] is True
    
    unified_client.vcenter.authenticate.assert_called_once()
    unified_client.nsx.authenticate.assert_called_once()
    unified_client.hcx.authenticate.assert_called_once()

@pytest.mark.asyncio
async def test_authenticate_all_partial_failure(unified_client):
    """Test partial authentication failure."""
    unified_client.nsx.authenticate.return_value = False
    
    results = await unified_client.authenticate_all()
    
    assert results["vcenter"] is True
    assert results["nsx"] is False
    assert results["hcx"] is True

@pytest.mark.asyncio
async def test_get_complete_inventory(unified_client):
    """Test getting complete inventory."""
    # Setup mock returns
    vm = VCenterVM(
        id="vm-1", name="test-vm", power_state="POWERED_ON",
        cpu_count=2, memory_mb=4096, guest_os="ubuntu", type="VirtualMachine"
    )
    unified_client.vcenter.get_vms.return_value = [vm]
    
    segment = NSXSegment(
        id="seg-1", display_name="test-seg", resource_type="Segment",
        transport_zone_path="tz-1"
    )
    unified_client.nsx.get_segments.return_value = [segment]
    
    site = HCXSiteSystem(
        system_id="site-1", name="test-site", type="source",
        url="https://site1", state="active", version="4.0"
    )
    unified_client.hcx.get_site_systems.return_value = [site]
    
    inventory = await unified_client.get_complete_inventory()
    
    assert isinstance(inventory, CompleteInventory)
    assert len(inventory.vms) == 1
    assert inventory.vms[0].id == "vm-1"
    assert len(inventory.nsx_segments) == 1
    assert inventory.nsx_segments[0].id == "seg-1"
    assert len(inventory.hcx_sites) == 1
    assert inventory.hcx_sites[0].system_id == "site-1"
