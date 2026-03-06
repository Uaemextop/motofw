"""
Response parser module for Motofw.

Provides ResponseParser class to parse and extract information
from Motorola OTA server responses.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ResponseParser:
    """Parser for Motorola OTA server responses."""

    @staticmethod
    def parse_check_update_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse check update response.

        Args:
            response: Raw response from check update API

        Returns:
            Dictionary with parsed update information:
                - update_available: bool
                - tracking_id: str (if update available)
                - context_timestamp: int (if update available)
                - message: str (error message if applicable)

        Raises:
            ValueError: If response format is invalid
        """
        if not isinstance(response, dict):
            raise ValueError("Invalid response format: expected dictionary")

        proceed = response.get("proceed", False)

        result = {
            "update_available": proceed,
        }

        if proceed:
            result["tracking_id"] = response.get("trackingId")
            result["context_timestamp"] = response.get("contextTimeStamp", 0)

            if not result["tracking_id"]:
                raise ValueError("Response missing required 'trackingId' field")

            logger.info(
                f"Update available: trackingId={result['tracking_id']}, "
                f"timestamp={result['context_timestamp']}"
            )
        else:
            result["message"] = response.get("message", "No update available")
            logger.info(f"No update available: {result['message']}")

        return result

    @staticmethod
    def parse_download_descriptor_response(
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse download descriptor response.

        Args:
            response: Raw response from download descriptor API

        Returns:
            Dictionary with parsed download information:
                - proceed: bool
                - tracking_id: str
                - resources: List[Dict] with url, headers, tags for each resource

        Raises:
            ValueError: If response format is invalid
        """
        if not isinstance(response, dict):
            raise ValueError("Invalid response format: expected dictionary")

        proceed = response.get("proceed", False)
        tracking_id = response.get("trackingId")

        result = {
            "proceed": proceed,
            "tracking_id": tracking_id,
            "resources": [],
        }

        if not proceed:
            logger.warning("Download descriptor response has proceed=false")
            return result

        # Extract content resources
        content_response = response.get("contentResponse", {})
        content_resources = content_response.get("contentResources", [])

        for resource in content_resources:
            parsed_resource = {
                "url": resource.get("url"),
                "headers": ResponseParser._parse_headers(resource.get("headers")),
                "tags": resource.get("tags", []),
            }

            if parsed_resource["url"]:
                result["resources"].append(parsed_resource)
                logger.info(
                    f"Found resource: {parsed_resource['url']} "
                    f"(tags: {', '.join(parsed_resource['tags'])})"
                )

        if not result["resources"]:
            logger.warning("No download resources found in response")

        return result

    @staticmethod
    def _parse_headers(headers_str: Optional[str]) -> Dict[str, str]:
        """
        Parse headers string into dictionary.

        Args:
            headers_str: Headers as string (e.g., "Authorization: Bearer token")

        Returns:
            Dictionary of header name -> value
        """
        if not headers_str:
            return {}

        headers = {}
        for line in headers_str.strip().split("\n"):
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        return headers

    @staticmethod
    def get_download_url_for_network(
        resources: List[Dict[str, Any]], network_type: str = "WIFI"
    ) -> Optional[Dict[str, Any]]:
        """
        Get download URL for specific network type.

        Args:
            resources: List of resources from parsed descriptor response
            network_type: Network type ("WIFI", "CELL", "ADMIN_APN")

        Returns:
            Resource dictionary with url, headers, tags or None if not found
        """
        for resource in resources:
            tags = resource.get("tags", [])
            if network_type.upper() in [tag.upper() for tag in tags]:
                logger.info(f"Selected resource for {network_type}: {resource['url']}")
                return resource

        # Fallback: return first resource if no specific match
        if resources:
            logger.warning(
                f"No resource found for {network_type}, using first available"
            )
            return resources[0]

        return None
