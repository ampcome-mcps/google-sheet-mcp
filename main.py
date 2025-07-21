#!/usr/bin/env python3
"""
Google Sheets API v4 MCP Server
A comprehensive MCP server with structured output for all Google Sheets API v4 endpoints.
Uses Nango for authentication.
"""


import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

import requests
from pydantic import BaseModel
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)  # Load environment variables from .env file

# Custom exceptions for better error handling
class GoogleSheetsAPIError(Exception):
    """Base exception for Google Sheets API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)

class AuthenticationError(GoogleSheetsAPIError):
    """Raised when authentication fails"""
    pass

class AuthorizationError(GoogleSheetsAPIError):
    """Raised when user lacks permission for the operation"""
    pass

class ResourceNotFoundError(GoogleSheetsAPIError):
    """Raised when requested resource is not found"""
    pass

class QuotaExceededError(GoogleSheetsAPIError):
    """Raised when API quota is exceeded"""
    pass

class ValidationError(GoogleSheetsAPIError):
    """Raised when request validation fails"""
    pass

# Initialize FastMCP server
mcp = FastMCP("Google Sheets API v4")

# Base URL for Google Sheets API
BASE_URL = "https://sheets.googleapis.com"

# Global variable to cache access token
_cached_access_token = None

def get_connection_credentials() -> dict[str, Any]:
    """Get credentials from Nango"""
    # Validate required environment variables
    required_vars = ["NANGO_CONNECTION_ID", "NANGO_INTEGRATION_ID", "NANGO_BASE_URL", "NANGO_SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise AuthenticationError(f"Missing required environment variables: {', '.join(missing_vars)}")

    id = os.environ.get("NANGO_CONNECTION_ID")
    integration_id = os.environ.get("NANGO_INTEGRATION_ID")
    base_url = os.environ.get("NANGO_BASE_URL")
    secret_key = os.environ.get("NANGO_SECRET_KEY")
    
    url = f"{base_url}/connection/{id}"
    params = {
        "provider_config_key": integration_id,
        "refresh_token": "true",
    }
    headers = {"Authorization": f"Bearer {secret_key}"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise AuthenticationError("Timeout while connecting to Nango authentication service")
    except requests.exceptions.ConnectionError:
        raise AuthenticationError("Failed to connect to Nango authentication service")
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            raise AuthenticationError("Invalid Nango secret key")
        elif response.status_code == 404:
            raise AuthenticationError("Nango connection not found")
        else:
            raise AuthenticationError(f"Nango API error: {response.status_code} - {response.text}")
    except Exception as e:
        raise AuthenticationError(f"Unexpected error getting Nango credentials: {str(e)}")

def get_access_token() -> str:
    """Get access token from Nango, with caching"""
    global _cached_access_token
    
    if _cached_access_token is None:
        credentials = get_connection_credentials()
        _cached_access_token = credentials.get("credentials", {}).get("access_token")
        
        if not _cached_access_token:
            raise AuthenticationError("No access token found in Nango credentials")
    
    return _cached_access_token

def refresh_access_token() -> str:
    """Force refresh access token from Nango"""
    global _cached_access_token
    _cached_access_token = None
    return get_access_token()

# Structured output models
class APIResponse(BaseModel):
    """Standard API response structure"""
    success: bool
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SpreadsheetProperties(BaseModel):
    """Spreadsheet properties structure"""
    spreadsheetId: Optional[str] = None
    title: Optional[str] = None
    locale: Optional[str] = None
    autoRecalc: Optional[str] = None
    timeZone: Optional[str] = None
    defaultFormat: Optional[Dict[str, Any]] = None
    spreadsheetTheme: Optional[Dict[str, Any]] = None

class Sheet(BaseModel):
    """Sheet structure"""
    properties: Optional[Dict[str, Any]] = None
    data: Optional[List[Dict[str, Any]]] = None
    merges: Optional[List[Dict[str, Any]]] = None
    conditionalFormats: Optional[List[Dict[str, Any]]] = None
    filterViews: Optional[List[Dict[str, Any]]] = None
    protectedRanges: Optional[List[Dict[str, Any]]] = None
    basicFilter: Optional[Dict[str, Any]] = None
    charts: Optional[List[Dict[str, Any]]] = None
    bandedRanges: Optional[List[Dict[str, Any]]] = None
    developerMetadata: Optional[List[Dict[str, Any]]] = None
    rowGroups: Optional[List[Dict[str, Any]]] = None
    columnGroups: Optional[List[Dict[str, Any]]] = None

class Spreadsheet(BaseModel):
    """Spreadsheet structure"""
    spreadsheetId: Optional[str] = None
    properties: Optional[SpreadsheetProperties] = None
    sheets: Optional[List[Sheet]] = None
    namedRanges: Optional[List[Dict[str, Any]]] = None
    spreadsheetUrl: Optional[str] = None
    developerMetadata: Optional[List[Dict[str, Any]]] = None
    dataSources: Optional[List[Dict[str, Any]]] = None
    dataSourceSchedules: Optional[List[Dict[str, Any]]] = None

class BatchUpdateResponse(BaseModel):
    """Batch update response structure"""
    spreadsheetId: Optional[str] = None
    replies: Optional[List[Dict[str, Any]]] = None
    updatedSpreadsheet: Optional[Spreadsheet] = None

class ValueRange(BaseModel):
    """Value range structure"""
    range: Optional[str] = None
    majorDimension: Optional[str] = None
    values: Optional[List[List[Any]]] = None

class BatchGetValuesResponse(BaseModel):
    """Batch get values response structure"""
    spreadsheetId: Optional[str] = None
    valueRanges: Optional[List[ValueRange]] = None

class BatchUpdateValuesResponse(BaseModel):
    """Batch update values response structure"""
    spreadsheetId: Optional[str] = None
    totalUpdatedRows: Optional[int] = None
    totalUpdatedColumns: Optional[int] = None
    totalUpdatedCells: Optional[int] = None
    totalUpdatedSheets: Optional[int] = None
    responses: Optional[List[Dict[str, Any]]] = None

class BatchClearValuesResponse(BaseModel):
    """Batch clear values response structure"""
    spreadsheetId: Optional[str] = None
    clearedRanges: Optional[List[str]] = None

class DeveloperMetadata(BaseModel):
    """Developer metadata structure"""
    metadataId: Optional[int] = None
    metadataKey: Optional[str] = None
    metadataValue: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    visibility: Optional[str] = None

class SearchDeveloperMetadataResponse(BaseModel):
    """Search developer metadata response structure"""
    matchedDeveloperMetadata: Optional[List[Dict[str, Any]]] = None

def _raise_for_status(response: requests.Response) -> None:
    """Raise appropriate exception based on HTTP status code"""
    if response.ok:
        return
    
    status_code = response.status_code
    
    try:
        error_data = response.json()
        error_message = error_data.get('error', {}).get('message', response.text)
    except:
        error_message = response.text or f"HTTP {status_code} error"
    
    if status_code == 400:
        raise ValidationError(f"Bad request: {error_message}", status_code, error_data if 'error_data' in locals() else None)
    elif status_code == 401:
        raise AuthenticationError(f"Authentication failed: {error_message}", status_code, error_data if 'error_data' in locals() else None)
    elif status_code == 403:
        raise AuthorizationError(f"Permission denied: {error_message}", status_code, error_data if 'error_data' in locals() else None)
    elif status_code == 404:
        raise ResourceNotFoundError(f"Resource not found: {error_message}", status_code, error_data if 'error_data' in locals() else None)
    elif status_code == 429:
        raise QuotaExceededError(f"Quota exceeded: {error_message}", status_code, error_data if 'error_data' in locals() else None)
    elif 500 <= status_code < 600:
        raise GoogleSheetsAPIError(f"Server error: {error_message}", status_code, error_data if 'error_data' in locals() else None)
    else:
        raise GoogleSheetsAPIError(f"HTTP {status_code}: {error_message}", status_code, error_data if 'error_data' in locals() else None)

# Helper function to make API requests
def make_api_request(
    method: str,
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    retry_auth: bool = True
) -> Dict[str, Any]:
    """Make HTTP request to Google Sheets API with automatic token refresh"""
    url = f"{BASE_URL}{endpoint}"
    
    # Get access token if not provided in headers
    if not headers or "Authorization" not in headers:
        access_token = get_access_token()
        if not headers:
            headers = {}
        headers["Authorization"] = f"Bearer {access_token}"
        headers["Content-Type"] = "application/json"
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            data=data,
            timeout=30
        )
        
        # If we get a 401 and retry_auth is True, try to refresh the token
        if response.status_code == 401 and retry_auth:
            access_token = refresh_access_token()
            headers["Authorization"] = f"Bearer {access_token}"
            # Retry the request with the new token
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                data=data,
                timeout=30
            )
        
        # Raise appropriate exception for non-successful responses
        _raise_for_status(response)
        
        # Parse response data
        response_data = None
        if response.content:
            try:
                response_data = response.json()
            except:
                response_data = {"content": response.text}
        
        return response_data
        
    except requests.exceptions.Timeout:
        raise GoogleSheetsAPIError("Request timeout - Google Sheets API did not respond in time")
    except requests.exceptions.ConnectionError:
        raise GoogleSheetsAPIError("Connection error - Unable to reach Google Sheets API")
    except requests.exceptions.RequestException as e:
        raise GoogleSheetsAPIError(f"Request failed: {str(e)}")

# Spreadsheets resource tools
@mcp.tool()
def spreadsheets_create(
    title: str = "Untitled spreadsheet",
    locale: Optional[str] = None,
    auto_recalc: Optional[str] = None,
    time_zone: Optional[str] = None,
    sheets: Optional[List[Dict[str, Any]]] = None
) -> Spreadsheet:
    """Creates a spreadsheet, returning the newly created spreadsheet."""
    if not title:
        raise ValidationError("title is required")
    
    properties = {"title": title}
    if locale:
        properties["locale"] = locale
    if auto_recalc:
        properties["autoRecalc"] = auto_recalc
    if time_zone:
        properties["timeZone"] = time_zone
    
    json_data = {"properties": properties}
    if sheets:
        json_data["sheets"] = sheets
    
    response_data = make_api_request("POST", "/v4/spreadsheets", json_data=json_data)
    return Spreadsheet(**response_data)

@mcp.tool()
def spreadsheets_get(
    spreadsheet_id: str,
    ranges: Optional[List[str]] = None,
    include_grid_data: Optional[bool] = None,
    fields: Optional[str] = None
) -> Spreadsheet:
    """Returns the spreadsheet at the given ID."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    
    params = {}
    if ranges:
        params["ranges"] = ranges
    if include_grid_data is not None:
        params["includeGridData"] = include_grid_data
    if fields:
        params["fields"] = fields
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}"
    response_data = make_api_request("GET", endpoint, params=params)
    return Spreadsheet(**response_data)

@mcp.tool()
def spreadsheets_batch_update(
    spreadsheet_id: str,
    requests: List[Dict[str, Any]],
    include_spreadsheet_in_response: Optional[bool] = None,
    response_ranges: Optional[List[str]] = None,
    response_include_grid_data: Optional[bool] = None
) -> BatchUpdateResponse:
    """Applies one or more updates to the spreadsheet."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not requests:
        raise ValidationError("requests is required")
    
    json_data = {"requests": requests}
    if include_spreadsheet_in_response is not None:
        json_data["includeSpreadsheetInResponse"] = include_spreadsheet_in_response
    if response_ranges:
        json_data["responseRanges"] = response_ranges
    if response_include_grid_data is not None:
        json_data["responseIncludeGridData"] = response_include_grid_data
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}:batchUpdate"
    response_data = make_api_request("POST", endpoint, json_data=json_data)
    return BatchUpdateResponse(**response_data)

@mcp.tool()
def spreadsheets_get_by_data_filter(
    spreadsheet_id: str,
    data_filters: List[Dict[str, Any]],
    include_grid_data: Optional[bool] = None
) -> Spreadsheet:
    """Returns the spreadsheet at the given ID with data filtered by the provided filters."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not data_filters:
        raise ValidationError("data_filters is required")
    
    json_data = {"dataFilters": data_filters}
    if include_grid_data is not None:
        json_data["includeGridData"] = include_grid_data
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}:getByDataFilter"
    response_data = make_api_request("POST", endpoint, json_data=json_data)
    return Spreadsheet(**response_data)

# Values resource tools
@mcp.tool()
def values_get(
    spreadsheet_id: str,
    range: str,
    major_dimension: Optional[str] = None,
    value_render_option: Optional[str] = None,
    date_time_render_option: Optional[str] = None
) -> ValueRange:
    """Returns a range of values from a spreadsheet."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not range:
        raise ValidationError("range is required")
    
    params = {}
    if major_dimension:
        params["majorDimension"] = major_dimension
    if value_render_option:
        params["valueRenderOption"] = value_render_option
    if date_time_render_option:
        params["dateTimeRenderOption"] = date_time_render_option
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}/values/{range}"
    response_data = make_api_request("GET", endpoint, params=params)
    return ValueRange(**response_data)

@mcp.tool()
def values_update(
    spreadsheet_id: str,
    range: str,
    values: List[List[Any]],
    value_input_option: str = "USER_ENTERED",
    major_dimension: Optional[str] = None,
    include_values_in_response: Optional[bool] = None,
    response_value_render_option: Optional[str] = None,
    response_date_time_render_option: Optional[str] = None
) -> Dict[str, Any]:
    """Sets values in a range of a spreadsheet."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not range:
        raise ValidationError("range is required")
    if not values:
        raise ValidationError("values is required")
    if value_input_option not in ["RAW", "USER_ENTERED"]:
        raise ValidationError("value_input_option must be 'RAW' or 'USER_ENTERED'")
    
    params = {"valueInputOption": value_input_option}
    if include_values_in_response is not None:
        params["includeValuesInResponse"] = include_values_in_response
    if response_value_render_option:
        params["responseValueRenderOption"] = response_value_render_option
    if response_date_time_render_option:
        params["responseDateTimeRenderOption"] = response_date_time_render_option
    
    json_data = {"values": values}
    if major_dimension:
        json_data["majorDimension"] = major_dimension
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}/values/{range}"
    return make_api_request("PUT", endpoint, params=params, json_data=json_data)

@mcp.tool()
def values_append(
    spreadsheet_id: str,
    range: str,
    values: List[List[Any]],
    value_input_option: str = "USER_ENTERED",
    major_dimension: Optional[str] = None,
    insert_data_option: Optional[str] = None,
    include_values_in_response: Optional[bool] = None,
    response_value_render_option: Optional[str] = None,
    response_date_time_render_option: Optional[str] = None
) -> Dict[str, Any]:
    """Appends values to a spreadsheet."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not range:
        raise ValidationError("range is required")
    if not values:
        raise ValidationError("values is required")
    if value_input_option not in ["RAW", "USER_ENTERED"]:
        raise ValidationError("value_input_option must be 'RAW' or 'USER_ENTERED'")
    
    params = {"valueInputOption": value_input_option}
    if insert_data_option:
        params["insertDataOption"] = insert_data_option
    if include_values_in_response is not None:
        params["includeValuesInResponse"] = include_values_in_response
    if response_value_render_option:
        params["responseValueRenderOption"] = response_value_render_option
    if response_date_time_render_option:
        params["responseDateTimeRenderOption"] = response_date_time_render_option
    
    json_data = {"values": values}
    if major_dimension:
        json_data["majorDimension"] = major_dimension
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}/values/{range}:append"
    return make_api_request("POST", endpoint, params=params, json_data=json_data)

@mcp.tool()
def values_clear(
    spreadsheet_id: str,
    range: str
) -> Dict[str, Any]:
    """Clears values from a spreadsheet."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not range:
        raise ValidationError("range is required")
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}/values/{range}:clear"
    return make_api_request("POST", endpoint, json_data={})

@mcp.tool()
def values_batch_get(
    spreadsheet_id: str,
    ranges: List[str],
    major_dimension: Optional[str] = None,
    value_render_option: Optional[str] = None,
    date_time_render_option: Optional[str] = None
) -> BatchGetValuesResponse:
    """Returns one or more ranges of values from a spreadsheet."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not ranges:
        raise ValidationError("ranges is required")
    
    params = {"ranges": ranges}
    if major_dimension:
        params["majorDimension"] = major_dimension
    if value_render_option:
        params["valueRenderOption"] = value_render_option
    if date_time_render_option:
        params["dateTimeRenderOption"] = date_time_render_option
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}/values:batchGet"
    response_data = make_api_request("GET", endpoint, params=params)
    return BatchGetValuesResponse(**response_data)

@mcp.tool()
def values_batch_update(
    spreadsheet_id: str,
    data: List[Dict[str, Any]],
    value_input_option: str = "USER_ENTERED",
    include_values_in_response: Optional[bool] = None,
    response_value_render_option: Optional[str] = None,
    response_date_time_render_option: Optional[str] = None
) -> BatchUpdateValuesResponse:
    """Sets values in one or more ranges of a spreadsheet."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not data:
        raise ValidationError("data is required")
    if value_input_option not in ["RAW", "USER_ENTERED"]:
        raise ValidationError("value_input_option must be 'RAW' or 'USER_ENTERED'")
    
    json_data = {
        "data": data,
        "valueInputOption": value_input_option
    }
    if include_values_in_response is not None:
        json_data["includeValuesInResponse"] = include_values_in_response
    if response_value_render_option:
        json_data["responseValueRenderOption"] = response_value_render_option
    if response_date_time_render_option:
        json_data["responseDateTimeRenderOption"] = response_date_time_render_option
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}/values:batchUpdate"
    response_data = make_api_request("POST", endpoint, json_data=json_data)
    return BatchUpdateValuesResponse(**response_data)

@mcp.tool()
def values_batch_clear(
    spreadsheet_id: str,
    ranges: List[str]
) -> BatchClearValuesResponse:
    """Clears one or more ranges of values from a spreadsheet."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not ranges:
        raise ValidationError("ranges is required")
    
    json_data = {"ranges": ranges}
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}/values:batchClear"
    response_data = make_api_request("POST", endpoint, json_data=json_data)
    return BatchClearValuesResponse(**response_data)

@mcp.tool()
def values_batch_get_by_data_filter(
    spreadsheet_id: str,
    data_filters: List[Dict[str, Any]],
    major_dimension: Optional[str] = None,
    value_render_option: Optional[str] = None,
    date_time_render_option: Optional[str] = None
) -> Dict[str, Any]:
    """Returns one or more ranges of values that match the specified data filters."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not data_filters:
        raise ValidationError("data_filters is required")
    
    json_data = {"dataFilters": data_filters}
    if major_dimension:
        json_data["majorDimension"] = major_dimension
    if value_render_option:
        json_data["valueRenderOption"] = value_render_option
    if date_time_render_option:
        json_data["dateTimeRenderOption"] = date_time_render_option
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}/values:batchGetByDataFilter"
    return make_api_request("POST", endpoint, json_data=json_data)

@mcp.tool()
def values_batch_update_by_data_filter(
    spreadsheet_id: str,
    data: List[Dict[str, Any]],
    value_input_option: str = "USER_ENTERED",
    include_values_in_response: Optional[bool] = None,
    response_value_render_option: Optional[str] = None,
    response_date_time_render_option: Optional[str] = None
) -> Dict[str, Any]:
    """Sets values in one or more ranges of a spreadsheet using data filters."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not data:
        raise ValidationError("data is required")
    if value_input_option not in ["RAW", "USER_ENTERED"]:
        raise ValidationError("value_input_option must be 'RAW' or 'USER_ENTERED'")
    
    json_data = {
        "data": data,
        "valueInputOption": value_input_option
    }
    if include_values_in_response is not None:
        json_data["includeValuesInResponse"] = include_values_in_response
    if response_value_render_option:
        json_data["responseValueRenderOption"] = response_value_render_option
    if response_date_time_render_option:
        json_data["responseDateTimeRenderOption"] = response_date_time_render_option
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}/values:batchUpdateByDataFilter"
    return make_api_request("POST", endpoint, json_data=json_data)

@mcp.tool()
def values_batch_clear_by_data_filter(
    spreadsheet_id: str,
    data_filters: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Clears one or more ranges of values from a spreadsheet using data filters."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not data_filters:
        raise ValidationError("data_filters is required")
    
    json_data = {"dataFilters": data_filters}
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}/values:batchClearByDataFilter"
    return make_api_request("POST", endpoint, json_data=json_data)

# Developer metadata resource tools
@mcp.tool()
def developer_metadata_get(
    spreadsheet_id: str,
    metadata_id: int
) -> DeveloperMetadata:
    """Returns the developer metadata with the specified ID."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not metadata_id:
        raise ValidationError("metadata_id is required")
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}/developerMetadata/{metadata_id}"
    response_data = make_api_request("GET", endpoint)
    return DeveloperMetadata(**response_data)

@mcp.tool()
def developer_metadata_search(
    spreadsheet_id: str,
    data_filters: List[Dict[str, Any]]
) -> SearchDeveloperMetadataResponse:
    """Returns all developer metadata matching the specified DataFilter."""
    if not spreadsheet_id:
        raise ValidationError("spreadsheet_id is required")
    if not data_filters:
        raise ValidationError("data_filters is required")
    
    json_data = {"dataFilters": data_filters}
    
    endpoint = f"/v4/spreadsheets/{spreadsheet_id}/developerMetadata:search"
    response_data = make_api_request("POST", endpoint, json_data=json_data)
    return SearchDeveloperMetadataResponse(**response_data)

# Utility tools
@mcp.tool()
def get_server_info() -> Dict[str, Any]:
    """Get information about the MCP server and current configuration."""
    try:
        # Check if we can get a token
        has_token = bool(_cached_access_token or get_access_token())
    except Exception:
        has_token = False
    
    return {
        "server_name": "Google Sheets API v4 MCP Server",
        "base_url": BASE_URL,
        "auth_method": "nango_oauth",
        "auth_configured": has_token,
        "environment_variables": {
            "nango_connection_id": bool(os.environ.get("NANGO_CONNECTION_ID")),
            "nango_integration_id": bool(os.environ.get("NANGO_INTEGRATION_ID")),
            "nango_base_url": bool(os.environ.get("NANGO_BASE_URL")),
            "nango_secret_key": bool(os.environ.get("NANGO_SECRET_KEY"))
        },
        "available_tools": [
            "spreadsheets_create", "spreadsheets_get", "spreadsheets_batch_update", "spreadsheets_get_by_data_filter",
            "values_get", "values_update", "values_append", "values_clear",
            "values_batch_get", "values_batch_update", "values_batch_clear",
            "values_batch_get_by_data_filter", "values_batch_update_by_data_filter", "values_batch_clear_by_data_filter",
            "developer_metadata_get", "developer_metadata_search",
            "get_server_info", "test_connection", "refresh_nango_token"
        ]
    }

@mcp.tool()
def test_connection() -> Dict[str, Any]:
    """Test the connection to Google Sheets API by attempting to create a minimal spreadsheet."""
    try:
        # Create a test spreadsheet
        test_spreadsheet = spreadsheets_create(title="MCP Nango Connection Test")
        
        return {
            "success": True,
            "message": "Connection test successful with Nango authentication",
            "test_spreadsheet_id": test_spreadsheet.spreadsheetId,
            "test_spreadsheet_url": test_spreadsheet.spreadsheetUrl,
            "note": "A test spreadsheet was created to verify the Nango connection"
        }
        
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return {
            "success": False,
            "error": f"Connection test failed: {str(e)}",
            "message": "Please check your Nango configuration and try again"
        }

@mcp.tool()
def refresh_nango_token() -> Dict[str, Any]:
    """Manually refresh the access token from Nango."""
    try:
        access_token = refresh_access_token()
        
        return {
            "success": True,
            "message": "Token refreshed successfully from Nango",
            "token_length": len(access_token) if access_token else 0,
            "refresh_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        return {
            "success": False,
            "error": f"Nango token refresh failed: {str(e)}",
            "message": "Please check your Nango configuration"
        }

def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Google Sheets API v4 MCP Server with Nango Authentication...")
    
    # Try to initialize Nango authentication on startup
    try:
        required_vars = [
            "NANGO_CONNECTION_ID", "NANGO_INTEGRATION_ID", 
            "NANGO_BASE_URL", "NANGO_SECRET_KEY"
        ]
        
        if all(os.environ.get(var) for var in required_vars):
            get_access_token()
            logger.info("Nango authentication initialized successfully on startup")
        else:
            missing_vars = [var for var in required_vars if not os.environ.get(var)]
            logger.warning(f"Missing Nango environment variables: {', '.join(missing_vars)}")
            logger.info("Please set all required Nango environment variables")
    except Exception as e:
        logger.warning(f"Failed to initialize Nango authentication on startup: {str(e)}")
        logger.info("Authentication will be attempted on first API call")
    
    # Run the FastMCP server
    mcp.run()

if __name__ == "__main__":
    main()