import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from vcf_hcx_automator.services.vcenter import VCenterClient
from vcf_hcx_automator.models import VCenterVM, VMFilters

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("vcf_hcx_automator.services.vcenter.settings") as mock:
        mock.vcf_host = "test-vcf.example.com"
        mock.vcf_username = "test_user"
        mock.vcf_password = "test_pass"
        mock.vcf_verify_ssl = False
        yield mock

@pytest.fixture
def vcenter_client(mock_settings):
    """Create VCenterClient instance for testing."""
    return VCenterClient()

@pytest.mark.asyncio
async def test_authenticate_success(vcenter_client):
    """Test successful authentication."""
    # Mock the response object
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"value": "test_session_id"}

    with patch.object(vcenter_client.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        result = await vcenter_client.authenticate()
        
        assert result is True
        assert vcenter_client.session_id == "test_session_id"
        assert vcenter_client.client.headers["vmware-api-session-id"] == "test_session_id"

@pytest.mark.asyncio
async def test_authenticate_failure(vcenter_client):
    """Test authentication failure."""
    with patch.object(vcenter_client.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = Exception("Auth failed")
        
        result = await vcenter_client.authenticate()
        
        assert result is False
        assert vcenter_client.session_id is None

@pytest.mark.asyncio
async def test_get_vms(vcenter_client):
    """Test getting VMs."""
    mock_response_data = {
        "value": [
            {
                "vm": "vm-1",
                "name": "test-vm-1",
                "power_state": "POWERED_ON",
                "cpu_count": 2,
                "memory_size_MiB": 4096,
                "guest_OS": "UBUNTU_64"
            }
        ]
    }
    
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.status_code = 200

    with patch.object(vcenter_client.client, "request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        vms = await vcenter_client.get_vms()
        
        assert len(vms) == 1
        assert isinstance(vms[0], VCenterVM)
        assert vms[0].id == "vm-1"
        assert vms[0].name == "test-vm-1"
        assert vms[0].power_state == "POWERED_ON"

@pytest.mark.asyncio
async def test_get_vms_with_filter(vcenter_client):
    """Test getting VMs with filter."""
    mock_response_data = {"value": []}
    
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.status_code = 200

    with patch.object(vcenter_client.client, "request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        filters = VMFilters(names=["test-vm"])
        await vcenter_client.get_vms(filters=filters)
        
        # Verify query params were passed
        call_args = mock_request.call_args
        assert call_args.kwargs["params"] == {"names": ["test-vm"]}

@pytest.mark.asyncio
async def test_get_networks(vcenter_client):
    """Test getting networks."""
    mock_response_data = {
        "value": [
            {
                "network": "net-1",
                "name": "test-net",
                "type": "DISTRIBUTED_PORTGROUP"
            }
        ]
    }
    
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.status_code = 200

    with patch.object(vcenter_client.client, "request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        networks = await vcenter_client.get_networks()
        
        assert len(networks) == 1
        assert networks[0].id == "net-1"
        assert networks[0].network_type == "DISTRIBUTED_PORTGROUP"
