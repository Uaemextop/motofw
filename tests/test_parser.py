"""Unit tests for parser module."""

import pytest

from motofw.parser import ResponseParser


class TestResponseParser:
    """Test ResponseParser class."""

    def test_parse_check_update_response_available(self):
        """Test parsing check update response with update available."""
        response = {
            "proceed": True,
            "trackingId": "test-tracking-123",
            "contextTimeStamp": 1234567890,
        }

        result = ResponseParser.parse_check_update_response(response)

        assert result["update_available"] is True
        assert result["tracking_id"] == "test-tracking-123"
        assert result["context_timestamp"] == 1234567890

    def test_parse_check_update_response_not_available(self):
        """Test parsing check update response with no update."""
        response = {
            "proceed": False,
            "message": "Device is up to date",
        }

        result = ResponseParser.parse_check_update_response(response)

        assert result["update_available"] is False
        assert result["message"] == "Device is up to date"
        assert "tracking_id" not in result

    def test_parse_check_update_response_missing_tracking_id(self):
        """Test parsing response with proceed=true but missing tracking ID."""
        response = {
            "proceed": True,
            "contextTimeStamp": 1234567890,
        }

        with pytest.raises(ValueError, match="missing required 'trackingId'"):
            ResponseParser.parse_check_update_response(response)

    def test_parse_check_update_response_invalid_format(self):
        """Test parsing invalid response format."""
        with pytest.raises(ValueError, match="Invalid response format"):
            ResponseParser.parse_check_update_response("not a dict")

    def test_parse_download_descriptor_response(self):
        """Test parsing download descriptor response."""
        response = {
            "proceed": True,
            "trackingId": "test-tracking-123",
            "contentResponse": {
                "contentResources": [
                    {
                        "url": "https://example.com/update.zip",
                        "headers": "Authorization: Bearer token123",
                        "tags": ["WIFI", "CELL"],
                    },
                    {
                        "url": "https://example.com/update-cell.zip",
                        "headers": None,
                        "tags": ["CELL"],
                    },
                ]
            },
        }

        result = ResponseParser.parse_download_descriptor_response(response)

        assert result["proceed"] is True
        assert result["tracking_id"] == "test-tracking-123"
        assert len(result["resources"]) == 2

        # First resource
        assert result["resources"][0]["url"] == "https://example.com/update.zip"
        assert result["resources"][0]["headers"]["Authorization"] == "Bearer token123"
        assert "WIFI" in result["resources"][0]["tags"]

        # Second resource
        assert result["resources"][1]["url"] == "https://example.com/update-cell.zip"
        assert result["resources"][1]["headers"] == {}

    def test_parse_download_descriptor_response_no_proceed(self):
        """Test parsing descriptor response with proceed=false."""
        response = {
            "proceed": False,
            "trackingId": "test-tracking-123",
        }

        result = ResponseParser.parse_download_descriptor_response(response)

        assert result["proceed"] is False
        assert result["resources"] == []

    def test_parse_headers(self):
        """Test header string parsing."""
        headers_str = "Authorization: Bearer token123\nContent-Type: application/json"

        headers = ResponseParser._parse_headers(headers_str)

        assert headers["Authorization"] == "Bearer token123"
        assert headers["Content-Type"] == "application/json"

    def test_parse_headers_empty(self):
        """Test parsing empty headers."""
        assert ResponseParser._parse_headers(None) == {}
        assert ResponseParser._parse_headers("") == {}

    def test_get_download_url_for_network_wifi(self):
        """Test getting download URL for WiFi network."""
        resources = [
            {"url": "https://example.com/cell.zip", "tags": ["CELL"]},
            {"url": "https://example.com/wifi.zip", "tags": ["WIFI"]},
        ]

        resource = ResponseParser.get_download_url_for_network(resources, "WIFI")

        assert resource["url"] == "https://example.com/wifi.zip"

    def test_get_download_url_for_network_cell(self):
        """Test getting download URL for cellular network."""
        resources = [
            {"url": "https://example.com/cell.zip", "tags": ["CELL"]},
            {"url": "https://example.com/wifi.zip", "tags": ["WIFI"]},
        ]

        resource = ResponseParser.get_download_url_for_network(resources, "CELL")

        assert resource["url"] == "https://example.com/cell.zip"

    def test_get_download_url_for_network_fallback(self):
        """Test fallback to first resource when network type not found."""
        resources = [
            {"url": "https://example.com/first.zip", "tags": ["WIFI"]},
            {"url": "https://example.com/second.zip", "tags": ["CELL"]},
        ]

        resource = ResponseParser.get_download_url_for_network(resources, "ADMIN_APN")

        # Should return first resource as fallback
        assert resource["url"] == "https://example.com/first.zip"

    def test_get_download_url_for_network_empty(self):
        """Test getting URL from empty resource list."""
        resource = ResponseParser.get_download_url_for_network([], "WIFI")

        assert resource is None
