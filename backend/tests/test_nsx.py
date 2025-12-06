import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from vcf_hcx_automator.services.nsx import NSXClient
from vcf_hcx_automator.models import NSXSegment

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("vcf_hcx_automator.services.nsx.settings") as mock:
        mock.nsx_manager = "test-nsx.example.com"
        mock.nsx_username = "admin"
        mock.nsx_password = "password"
        mock.nsx_verify_ssl = False
        yield mock

@pytest.fixture
def nsx_client(mock_settings):
    """Create NSXClient instance for testing."""
    return NSXClient()

@pytest.mark.asyncio
async def test_authenticate_success(nsx_client):
    """Test successful authentication."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"results": []}
    mock_response.status_code = 200

    with patch.object(nsx_client.client, "request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        result = await nsx_client.authenticate()
        
        assert result is True

@pytest.mark.asyncio
async def test_get_segments(nsx_client):
    """Test getting segments."""
    mock_response_data = {
        "results": [
            {
                "id": "seg-1",
                "display_name": "test-segment",
                "transport_zone_path": "/infra/sites/default/enforcement-points/default/transport-zones/tz-1",
                "subnets": [{"cidr": "192.168.1.0/24"}]
            }
        ]
    }
    
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.status_code = 200

    with patch.object(nsx_client.client, "request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        segments = await nsx_client.get_segments()
        
        assert len(segments) == 1
        assert isinstance(segments[0], NSXSegment)
        assert segments[0].id == "seg-1"
        assert segments[0].display_name == "test-segment"
