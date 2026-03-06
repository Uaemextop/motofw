"""Unit tests for config module."""

import tempfile
from pathlib import Path

import pytest

from motofw.config import Config


class TestConfig:
    """Test Config class."""

    def test_default_config(self):
        """Test configuration with defaults (no config file)."""
        config = Config()

        assert config.get_api_host() == "moto-cds.appspot.com"
        assert config.get_api_host(is_prc=True) == "moto-cds.svcmot.cn"
        assert config.get_http_timeout() == 30
        assert config.get_http_retries() == 3
        assert config.use_https() is True

    def test_staging_hosts(self):
        """Test staging environment hosts."""
        config = Config()

        assert config.get_api_host(use_staging=True) == "moto-cds-staging.appspot.com"
        assert (
            config.get_api_host(is_prc=True, use_staging=True)
            == "ota-cn-sdc.blurdev.com"
        )

    def test_custom_config_file(self):
        """Test loading custom configuration file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("""
[api]
production_host = custom.example.com

[http]
timeout = 60
retries = 5
use_https = false
            """)
            config_path = Path(f.name)

        try:
            config = Config(config_path)

            assert config.get_api_host() == "custom.example.com"
            assert config.get_http_timeout() == 60
            assert config.get_http_retries() == 5
            assert config.use_https() is False
        finally:
            config_path.unlink()

    def test_proxy_configuration(self):
        """Test proxy settings."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("""
[http]
proxy_host = proxy.example.com
proxy_port = 8080
            """)
            config_path = Path(f.name)

        try:
            config = Config(config_path)

            assert config.get_proxy_host() == "proxy.example.com"
            assert config.get_proxy_port() == 8080
        finally:
            config_path.unlink()

    def test_no_proxy(self):
        """Test default proxy settings (no proxy)."""
        config = Config()

        assert config.get_proxy_host() is None
        assert config.get_proxy_port() is None

    def test_endpoints(self):
        """Test API endpoint configuration."""
        config = Config()

        assert config.get_check_update_endpoint() == "/check"
        assert config.get_download_descriptor_endpoint() == "/descriptor"

    def test_user_agent(self):
        """Test user agent configuration."""
        config = Config()

        assert "motofw" in config.get_user_agent().lower()
