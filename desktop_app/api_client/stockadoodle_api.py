import requests
import base64
import os
from typing import Dict, Any, Optional


class APIResponse:
    """Standardized response object"""
    def __init__(self, success: bool, data=None, error: str = None, status_code: int = None):
        self.success = success
        self.data = data
        self.error = error
        self.status_code = status_code


class StockaDoodleAPI:
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Content-Type": "application/json"}
        self.timeout = 10
        
        # Initialize sub-clients
        self.products = ProductClient(self)

    def _request(self, method: str, path: str, json_data: Dict = None, params: Dict = None) -> APIResponse:
        url = f"{self.base_url}/api/v1/{path.lstrip('/')}"
        
        try:
            if method == "GET":
                r = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            elif method == "POST":
                r = requests.post(url, json=json_data, headers=self.headers, timeout=self.timeout)
            elif method == "PUT":
                r = requests.put(url, json=json_data, headers=self.headers, timeout=self.timeout)
            elif method == "PATCH":
                r = requests.patch(url, json=json_data, headers=self.headers, timeout=self.timeout)
            elif method == "DELETE":
                r = requests.delete(url, headers=self.headers, timeout=self.timeout)
            else:
                return APIResponse(False, error=f"Unsupported method: {method}")

            if r.status_code >= 200 and r.status_code < 300:
                try:
                    return APIResponse(True, data=r.json(), status_code=r.status_code)
                except ValueError:
                    return APIResponse(True, data=r.text, status_code=r.status_code)
            else:
                return APIResponse(False, error=r.text or "Unknown error", status_code=r.status_code)

        except requests.exceptions.Timeout:
            return APIResponse(False, error="Request timeout — server not responding")
        except requests.exceptions.ConnectionError:
            return APIResponse(False, error="Cannot connect to server — is it running?")
        except Exception as e:
            return APIResponse(False, error=f"Unexpected error: {str(e)}")


class ProductClient:
    """Product management client — mirrors API endpoints"""
    
    def __init__(self, api: StockaDoodleAPI):
        self.api = api

    def list(self, search: str = None, category_id: int = None, include_image: bool = False) -> APIResponse:
        params = {}
        if search: params["search"] = search
        if category_id: params["category_id"] = category_id
        if include_image: params["include_image"] = "true"
        return self.api._request("GET", "products", params=params)

    def get(self, product_id: int, include_image: bool = False) -> APIResponse:
        params = {"include_image": "true"} if include_image else {}
        return self.api._request("GET", f"products/{product_id}", params=params)

    def create(self, data: Dict[str, Any]) -> APIResponse:
        payload = data.copy()
        if payload.get("image_path") and os.path.exists(payload["image_path"]):
            with open(payload["image_path"], "rb") as f:
                payload["image_base64"] = base64.b64encode(f.read()).decode("utf-8")
            payload.pop("image_path", None)
        return self.api._request("POST", "products", json_data=payload)

    def update(self, product_id: int, data: Dict[str, Any]) -> APIResponse:
        payload = data.copy()
        if payload.get("image_path") and os.path.exists(payload["image_path"]):
            with open(payload["image_path"], "rb") as f:
                payload["image_base64"] = base64.b64encode(f.read()).decode("utf-8")
            payload.pop("image_path", None)
        return self.api._request("PUT", f"products/{product_id}", json_data=payload)
    
    def patch(self, product_id: int, data: Dict[str, Any]) -> APIResponse:
        """Partial update — only send changed fields"""
        payload = data.copy()

        if payload.get("image_path") and os.path.exists(payload["image_path"]):
            with open(payload["image_path"], "rb") as f:
                payload["image_base64"] = base64.b64encode(f.read()).decode("utf-8")
            payload.pop("image_path", None)

        return self.api._request("PATCH", f"products/{product_id}", json_data=payload)


    def delete(self, product_id: int) -> APIResponse:
        return self.api._request("DELETE", f"products/{product_id}")


# Global instance
api = StockaDoodleAPI()