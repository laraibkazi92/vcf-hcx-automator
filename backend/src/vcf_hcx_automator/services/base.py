import httpx
import logging
import asyncio
from typing import Optional, Dict, Any, Union
from vcf_hcx_automator.config.constants import DEFAULT_TIMEOUT, MAX_RETRIES, DEFAULT_CONNECT_TIMEOUT
from vcf_hcx_automator.utils.exceptions import APIError, AuthenticationError, ResourceNotFoundError
from vcf_hcx_automator.utils.logging import get_logger

class BaseService:
    """Base service class"""
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

class BaseHTTPClient(BaseService):
    """
    Base HTTP client with retry logic, logging, and error handling.
    """
    def __init__(
        self, 
        base_url: str, 
        verify_ssl: bool = True,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__()
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        self.headers = headers or {}
        self.client = httpx.AsyncClient(
            base_url=base_url,
            verify=verify_ssl,
            headers=self.headers,
            timeout=httpx.Timeout(DEFAULT_TIMEOUT, connect=DEFAULT_CONNECT_TIMEOUT)
        )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Any = None,
        retry_count: int = 0
    ) -> httpx.Response:
        """
        Make an HTTP request with retry logic.
        """
        try:
            self.logger.debug(f"Request: {method} {endpoint}", extra={"params": params})
            
            response = await self.client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
                data=data
            )
            
            self.logger.debug(
                f"Response: {response.status_code} {method} {endpoint}",
                extra={"status_code": response.status_code}
            )
            
            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
            # This line is unreachable because _handle_http_error raises exception
            return e.response # type: ignore

        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
            if retry_count < MAX_RETRIES:
                wait_time = 2 ** retry_count
                self.logger.warning(
                    f"Request failed: {str(e)}. Retrying in {wait_time}s ({retry_count + 1}/{MAX_RETRIES})"
                )
                await asyncio.sleep(wait_time)
                return await self._request(
                    method, endpoint, params, json_data, data, retry_count + 1
                )
            
            self.logger.error(f"Request failed after {MAX_RETRIES} retries: {str(e)}")
            raise APIError(
                message=f"Connection failed: {str(e)}",
                status_code=0,
                provider="http"
            )

        except Exception as e:
            self.logger.exception(f"Unexpected error during request: {str(e)}")
            raise APIError(
                message=f"Unexpected error: {str(e)}",
                status_code=500,
                provider="http"
            )

    def _handle_http_error(self, error: httpx.HTTPStatusError):
        """
        Handle HTTP errors and raise appropriate exceptions.
        """
        status_code = error.response.status_code
        message = str(error)
        
        try:
            error_details = error.response.json()
        except Exception:
            error_details = {"text": error.response.text}

        if status_code == 401:
            raise AuthenticationError(message="Authentication failed", provider="http")
        
        if status_code == 403:
            raise APIError(
                message="Permission denied",
                status_code=status_code,
                provider="http",
                details=error_details
            )
            
        if status_code == 404:
            raise ResourceNotFoundError(
                message="Resource not found",
                provider="http",
                resource_type="unknown",
                resource_id="unknown"
            )
            
        raise APIError(
            message=f"HTTP Error {status_code}: {message}",
            status_code=status_code,
            provider="http",
            details=error_details
        )

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = await self._request("GET", endpoint, params=params)
        return response.json()

    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = await self._request("POST", endpoint, json_data=data)
        return response.json()
        
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = await self._request("PUT", endpoint, json_data=data)
        return response.json()
        
    async def delete(self, endpoint: str) -> None:
        await self._request("DELETE", endpoint)
