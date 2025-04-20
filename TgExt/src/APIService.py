import requests
import logging
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    def _request(
        self,
        method: str,
        base_url: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        try:
            response = self.session.request(
                method=method,
                url=base_url,
                params=params,
                json=json_data,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            return None
        except ValueError as e:
            self.logger.error(f"JSON decode error: {str(e)}")
            return None

    def get(
        self,
        base_url,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        return self._request("GET", params=params, headers=headers, base_url=base_url)

    def post(
        self,
        base_url,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        return self._request("POST", json_data=json_data, headers=headers, base_url=base_url)
