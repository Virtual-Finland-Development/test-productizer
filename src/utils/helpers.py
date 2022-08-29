from typing import Dict, Any, Optional
from datetime import datetime, timezone


def omit_empty_dict_attributes(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove empty dict attributes from a dict
    """
    return {
        key: value for key, value in data.items() if value is not None and value != {}
    }


def ensure_json_content_type_header(
    headers: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Add the content type header for JSON requests, but only if not already present
    """
    if headers is not None and (
        "Content-Type" not in headers or "content-type" not in headers
    ):
        headers["Content-Type"] = "application/json; charset=utf-8"
    return headers


def ensure_dict(data: Any, allow_empty: bool = True) -> Dict[str, Any]:
    """
    Ensure that the data is a dict
    """
    if isinstance(data, dict):
        return data  # type: ignore
    if allow_empty:
        return {}
    raise ValueError("Data must be a dict")


#
# Datetime transformers
# @see: https://stackoverflow.com/a/68198142
#
def convert_datetime_to_iso_8601_with_z_suffix(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def transform_to_utc_datetime(dt: datetime) -> datetime:
    return dt.astimezone(tz=timezone.utc)
