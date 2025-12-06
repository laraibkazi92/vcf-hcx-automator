from typing import List, Optional, Dict, Any
from vcf_hcx_automator.services.base import BaseHTTPClient
from vcf_hcx_automator.config import settings
from vcf_hcx_automator.models import (
    NSXLogicalSwitch, NSXTransportZone, NSXSegment, NSXSwitchingProfile,
    NetworkFilters
)

class NSXClient(BaseHTTPClient):
    """NSX REST API client for network discovery"""

    def __init__(self):
        super().__init__(
            base_url=f"https://{settings.nsx_manager}/policy/api/v1",
            verify_ssl=settings.nsx_verify_ssl
        )
        # NSX usually supports basic auth directly on requests
        self.client.auth = (settings.nsx_username, settings.nsx_password)

    async def authenticate(self) -> bool:
        """Authenticate with NSX manager"""
        # NSX uses basic auth per request, but we can check connectivity
        try:
            await self.get("/infra/sites")
            return True
        except Exception as e:
            self.logger.error(f"NSX authentication failed: {str(e)}")
            return False

    async def get_transport_zones(self) -> List[NSXTransportZone]:
        """Get NSX transport zones"""
        # Note: Transport Zones are in the Management Plane API (/api/v1), not Policy API
        # But we initialized with Policy API base URL. We might need to adjust or use full URL.
        # Or use Policy API equivalent if available.
        # For simplicity, let's assume we can access /api/v1 if we change base_url or use absolute path
        # Actually, let's use the Policy API "Transport Zones" if they exist, or fallback to MP.
        # Policy API usually abstracts this. Let's try to stick to Policy API "Segments" which reference TZs.
        
        # However, to get list of TZs, we might need MP API.
        # Let's try to query /api/v1/transport-zones by overriding base URL for this call if needed.
        # But BaseHTTPClient uses fixed base_url.
        
        # Let's assume we use Policy API for everything we can.
        # Segments are the main thing.
        
        # If we really need TZs, we might need a separate client or method to handle MP API.
        # For now, let's implement get_segments first as it's most important.
        return []

    async def get_segments(self, filters: Optional[NetworkFilters] = None) -> List[NSXSegment]:
        """Get NSX segments"""
        data = await self.get("/infra/segments")
        segments = []
        for item in data.get("results", []):
            segments.append(NSXSegment(
                id=item.get("id"),
                display_name=item.get("display_name"),
                transport_zone_path=item.get("transport_zone_path"),
                subnets=item.get("subnets", [])
            ))
        return segments

    async def get_logical_switches(self) -> List[NSXLogicalSwitch]:
        """Get NSX logical switches"""
        # Logical Switches are MP API. In Policy API they are Segments.
        # We'll map Segments to Logical Switches if needed, or just return empty if we strictly want LS.
        # For migration purposes, Segments are what matters in NSX-T.
        return []

    async def get_switching_profiles(self) -> List[NSXSwitchingProfile]:
        """Get NSX switching profiles"""
        # Policy API: /infra/qos-profiles, etc.
        # Let's fetch QoS profiles as an example
        data = await self.get("/infra/qos-profiles")
        profiles = []
        for item in data.get("results", []):
            profiles.append(NSXSwitchingProfile(
                id=item.get("id"),
                display_name=item.get("display_name"),
                category="QoS"
            ))
        return profiles
