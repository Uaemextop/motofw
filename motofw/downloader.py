"""
Firmware downloader module for Motofw.

Provides FirmwareDownloader class for downloading OTA packages
with progress reporting and integrity verification.
"""

import hashlib
import logging
from pathlib import Path
from typing import Dict, Optional, Callable
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


class FirmwareDownloader:
    """Downloader for OTA firmware packages."""

    def __init__(self, session: Optional[requests.Session] = None):
        """
        Initialize firmware downloader.

        Args:
            session: Existing requests session to use (creates new if None)
        """
        self.session = session or requests.Session()

    def download(
        self,
        url: str,
        output_path: Path,
        headers: Optional[Dict[str, str]] = None,
        expected_checksum: Optional[str] = None,
        checksum_algorithm: str = "sha1",
        progress_callback: Optional[Callable[[int, int], None]] = None,
        chunk_size: int = 8192,
    ) -> bool:
        """
        Download firmware package from URL.

        Args:
            url: Download URL
            output_path: Path where to save the downloaded file
            headers: Optional custom headers for the request
            expected_checksum: Expected checksum for verification (hex string)
            checksum_algorithm: Algorithm to use (sha1, sha256, md5)
            progress_callback: Optional callback(bytes_downloaded, total_bytes)
            chunk_size: Size of download chunks in bytes

        Returns:
            True if download and verification successful, False otherwise

        Raises:
            requests.RequestException: If download fails
            ValueError: If checksum verification fails
        """
        logger.info(f"Downloading from {url}")
        logger.info(f"Output path: {output_path}")

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare headers
        request_headers = headers or {}

        # Start download with streaming
        response = self.session.get(url, headers=request_headers, stream=True)
        response.raise_for_status()

        # Get total size if available
        total_size = int(response.headers.get("content-length", 0))
        if total_size > 0:
            logger.info(f"Total size: {self._format_size(total_size)}")

        # Initialize checksum calculator if needed
        if expected_checksum:
            hasher = self._get_hasher(checksum_algorithm)
        else:
            hasher = None

        # Download file
        downloaded = 0
        try:
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if hasher:
                            hasher.update(chunk)

                        if progress_callback:
                            progress_callback(downloaded, total_size)

            logger.info(f"Downloaded {self._format_size(downloaded)}")

            # Verify checksum if provided
            if expected_checksum and hasher:
                actual_checksum = hasher.hexdigest()
                if actual_checksum.lower() != expected_checksum.lower():
                    logger.error(
                        f"Checksum mismatch! Expected: {expected_checksum}, "
                        f"Got: {actual_checksum}"
                    )
                    # Remove corrupted file
                    output_path.unlink()
                    raise ValueError("Checksum verification failed")

                logger.info(f"Checksum verified: {actual_checksum}")

            return True

        except Exception as e:
            logger.error(f"Download failed: {e}")
            # Clean up partial download
            if output_path.exists():
                output_path.unlink()
            raise

    def download_with_progress_bar(
        self,
        url: str,
        output_path: Path,
        headers: Optional[Dict[str, str]] = None,
        expected_checksum: Optional[str] = None,
        checksum_algorithm: str = "sha1",
    ) -> bool:
        """
        Download with text-based progress bar.

        Args:
            url: Download URL
            output_path: Path where to save the downloaded file
            headers: Optional custom headers
            expected_checksum: Expected checksum for verification
            checksum_algorithm: Algorithm to use (sha1, sha256, md5)

        Returns:
            True if download successful
        """

        def progress_callback(downloaded: int, total: int) -> None:
            """Display progress bar."""
            if total > 0:
                percentage = (downloaded / total) * 100
                bar_length = 50
                filled = int(bar_length * downloaded / total)
                bar = "=" * filled + "-" * (bar_length - filled)
                print(
                    f"\rProgress: [{bar}] {percentage:.1f}% "
                    f"({self._format_size(downloaded)}/{self._format_size(total)})",
                    end="",
                    flush=True,
                )
            else:
                print(
                    f"\rDownloaded: {self._format_size(downloaded)}",
                    end="",
                    flush=True,
                )

        result = self.download(
            url=url,
            output_path=output_path,
            headers=headers,
            expected_checksum=expected_checksum,
            checksum_algorithm=checksum_algorithm,
            progress_callback=progress_callback,
        )

        print()  # New line after progress bar
        return result

    def verify_checksum(
        self, file_path: Path, expected_checksum: str, algorithm: str = "sha1"
    ) -> bool:
        """
        Verify checksum of a file.

        Args:
            file_path: Path to file
            expected_checksum: Expected checksum (hex string)
            algorithm: Hash algorithm (sha1, sha256, md5)

        Returns:
            True if checksum matches

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        hasher = self._get_hasher(algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)

        actual_checksum = hasher.hexdigest()
        matches = actual_checksum.lower() == expected_checksum.lower()

        if matches:
            logger.info(f"Checksum verified: {actual_checksum}")
        else:
            logger.error(
                f"Checksum mismatch! Expected: {expected_checksum}, "
                f"Got: {actual_checksum}"
            )

        return matches

    @staticmethod
    def _get_hasher(algorithm: str):
        """
        Get hash function for algorithm.

        Args:
            algorithm: Hash algorithm name

        Returns:
            Hash object

        Raises:
            ValueError: If algorithm is not supported
        """
        algorithm = algorithm.lower()
        if algorithm == "sha1":
            return hashlib.sha1()
        elif algorithm == "sha256":
            return hashlib.sha256()
        elif algorithm == "md5":
            return hashlib.md5()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """
        Format size in bytes to human-readable string.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
