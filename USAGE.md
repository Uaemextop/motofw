# 📦 Motofw - Usage Guide

This guide provides detailed examples for using the `motofw` command-line tool to query and download Motorola OTA firmware updates.

## Installation

```bash
# Install from source
git clone https://github.com/Uaemextop/motofw.git
cd motofw
pip install -e .

# Or install from PyPI (when published)
pip install motofw
```

## Configuration (Optional)

Create a `config.ini` file to customize API endpoints and HTTP settings:

```bash
cp config.ini.example config.ini
```

Edit `config.ini` as needed. If no config file is provided, default settings are used.

## Basic Usage

### 1. Query Available Updates

Check if firmware updates are available for your device:

```bash
motofw query \
  --serial ZY1234567890 \
  --model "moto g power" \
  --product cebu \
  --build-id S3RC33.18-52-1
```

**Output:**
```
✓ Update available!
  Tracking ID: abc123-tracking-id
  Timestamp: 1234567890
```

### 2. Query with Download URLs

Get update information including download URLs:

```bash
motofw query \
  --serial ZY1234567890 \
  --model "moto g power" \
  --product cebu \
  --build-id S3RC33.18-52-1 \
  --get-url
```

**Output:**
```
✓ Update available!
  Tracking ID: abc123-tracking-id
  Timestamp: 1234567890

Download URLs:
  Resource 1:
    URL: https://moto-cds.appspot.com/path/to/update.zip
    Tags: WIFI, CELL
    Headers: {'Authorization': 'Bearer token...'}
```

### 3. Download Firmware

Download the OTA package:

```bash
motofw download \
  --serial ZY1234567890 \
  --model "moto g power" \
  --product cebu \
  --build-id S3RC33.18-52-1 \
  --output ./firmware/update.zip
```

**Output:**
```
✓ Update found, fetching download URLs...
Downloading from: https://moto-cds.appspot.com/path/to/update.zip
Progress: [==================================] 100.0% (512.5 MB/512.5 MB)
✓ Download complete: ./firmware/update.zip
```

### 4. Download with Checksum Verification

Download and verify file integrity:

```bash
motofw download \
  --serial ZY1234567890 \
  --model "moto g power" \
  --product cebu \
  --build-id S3RC33.18-52-1 \
  --output ./firmware/update.zip \
  --checksum a1b2c3d4e5f6... \
  --checksum-algorithm sha256
```

### 5. Using Different Network Types

Specify network type for download (WIFI, CELL, or ADMIN_APN):

```bash
motofw download \
  --serial ZY1234567890 \
  --model "moto g power" \
  --product cebu \
  --build-id S3RC33.18-52-1 \
  --output ./firmware/update.zip \
  --network-type CELL
```

## Advanced Options

### Device-Specific Parameters

Provide additional device information for more accurate queries:

```bash
motofw query \
  --serial ZY1234567890 \
  --model "moto g power" \
  --product cebu \
  --build-id S3RC33.18-52-1 \
  --build-device cebu_retail \
  --carrier vzw \
  --color blue \
  --language en-US
```

### PRC (China) Region Devices

Use different API endpoints for PRC region devices:

```bash
motofw query \
  --serial ZY1234567890 \
  --model "moto edge 50" \
  --product pstar \
  --build-id S1SC33.123-45-6 \
  --prc
```

### Staging Environment

Use staging API endpoints for testing:

```bash
motofw query \
  --serial ZY1234567890 \
  --model "moto g power" \
  --product cebu \
  --build-id S3RC33.18-52-1 \
  --staging
```

### Custom Configuration File

Use a custom configuration file:

```bash
motofw query \
  --config /path/to/custom-config.ini \
  --serial ZY1234567890 \
  --model "moto g power" \
  --product cebu \
  --build-id S3RC33.18-52-1
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
motofw --debug query \
  --serial ZY1234567890 \
  --model "moto g power" \
  --product cebu \
  --build-id S3RC33.18-52-1
```

## Using as a Python Library

You can also use Motofw programmatically in your Python projects:

```python
from pathlib import Path
from motofw import OTAClient, DeviceInfo, ResponseParser, FirmwareDownloader

# Create device info
device = DeviceInfo(
    serial_number="ZY1234567890",
    model="moto g power",
    product="cebu",
    build_id="S3RC33.18-52-1",
)

# Create OTA client
with OTAClient(device) as client:
    # Check for updates
    response = client.check_for_update()

    # Parse response
    parser = ResponseParser()
    result = parser.parse_check_update_response(response)

    if result["update_available"]:
        print(f"Update available: {result['tracking_id']}")

        # Get download descriptor
        descriptor = client.get_download_descriptor(
            result["tracking_id"],
            result["context_timestamp"]
        )

        # Parse descriptor
        desc_result = parser.parse_download_descriptor_response(descriptor)

        # Get WiFi resource
        resource = parser.get_download_url_for_network(
            desc_result["resources"],
            "WIFI"
        )

        if resource:
            # Download firmware
            downloader = FirmwareDownloader(client.session)
            downloader.download_with_progress_bar(
                url=resource["url"],
                output_path=Path("firmware.zip"),
                headers=resource.get("headers"),
            )
```

## Common Device Parameters

Here are some example device parameters for different Motorola devices:

### Moto G Power (2021)
```bash
--model "moto g power"
--product cebu
--build-id S3RC33.18-52-1
```

### Moto Edge 50
```bash
--model "moto edge 50"
--product pstar
--build-id S1SC33.123-45-6
```

### Motorola Razr
```bash
--model "motorola razr"
--product voyager
--build-id R2RC33.67-89-10
```

## Troubleshooting

### No Update Available

If you get "No update available", possible causes:
- Device is already on the latest firmware
- Build ID is incorrect
- Device model/product mismatch
- Server-side update availability

### Connection Errors

If you get connection errors:
- Check your internet connection
- Verify proxy settings in `config.ini`
- Try using `--staging` for testing
- Enable debug mode with `--debug`

### Checksum Verification Failed

If checksum verification fails:
- Download may have been corrupted
- Wrong checksum algorithm specified
- Network interruption during download

Retry the download or verify the expected checksum value.

## Getting Device Information

To find your device's parameters:

1. **Serial Number**: Settings → About Phone → Status → Serial Number
2. **Model**: Settings → About Phone → Model
3. **Build ID**: Settings → About Phone → Build Number
4. **Product**: Extract from build.prop or system properties

Or use tools like `adb`:

```bash
adb shell getprop ro.serialno           # Serial number
adb shell getprop ro.product.model      # Model
adb shell getprop ro.product.name       # Product
adb shell getprop ro.build.id           # Build ID
adb shell getprop ro.product.device     # Build device
```

## License

See [LICENSE](LICENSE) file for details.
