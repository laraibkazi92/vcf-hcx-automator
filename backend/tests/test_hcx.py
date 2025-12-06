import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from vcf_hcx_automator.services.hcx import HCXClient
from vcf_hcx_automator.models import HCXSiteSystem, HCXMobilityGroupRequest

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("vcf_hcx_automator.services.hcx.settings") as mock:
        mock.hcx_manager = "test-hcx.example.com"
        mock.hcx_username = "admin"
        mock.hcx_password = "password"
        mock.hcx_verify_ssl = False
        yield mock

@pytest.fixture
def hcx_client(mock_settings):
    """Create HCXClient instance for testing."""
    return HCXClient()

@pytest.mark.asyncio
async def test_authenticate_success(hcx_client):
    """Test successful authentication."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.headers = {"x-hm-authorization": "test-token"}
    mock_response.status_code = 200

    with patch.object(hcx_client.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        result = await hcx_client.authenticate()
        
        assert result is True
        assert hcx_client.auth_token == "test-token"
        assert hcx_client.client.headers["x-hm-authorization"] == "test-token"

@pytest.mark.asyncio
async def test_get_site_systems(hcx_client):
    """Test getting site systems."""
    mock_response_data = {
        "items": [
            {
                "id": "site-1",
                "name": "test-site",
                "type": "source",
                "url": "https://site1",
                "state": "active",
                "version": "4.0"
            }
        ]
    }
    
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.status_code = 200

    with patch.object(hcx_client.client, "request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        sites = await hcx_client.get_site_systems()
        
        assert len(sites) == 1
        assert isinstance(sites[0], HCXSiteSystem)
        assert sites[0].system_id == "site-1"
        assert sites[0].name == "test-site"

@pytest.mark.asyncio
async def test_create_mobility_group(hcx_client):
    """Test creating mobility group."""
    request = HCXMobilityGroupRequest(
        name="mg-1",
        source_site_id="site-1",
        destination_site_id="site-2",
        service_mesh_id="mesh-1",
        migration_type="v2v",
        vm_ids=["vm-1"]
    )
    
    mock_response_data = {
        "id": "mg-1",
        "name": "mg-1",
        "sourceId": "site-1",
        "destinationId": "site-2",
        "serviceMeshId": "mesh-1",
        "type": "v2v",
        "state": "draft",
        "migrations": []
    }
    
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.status_code = 200

    with patch.object(hcx_client.client, "request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        group = await hcx_client.create_mobility_group(request)
        
        assert group.group_id == "mg-1"
        assert group.name == "mg-1"
