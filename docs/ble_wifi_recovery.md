# BLE Wi-Fi Recovery

This document describes the Bluetooth-based Wi-Fi recovery flow implemented by the EcoFlow Cloud integration.

## Scope

BLE Wi-Fi recovery currently targets:
- `RIVER_2`
- `RIVER_2_MAX`
- `RIVER_2_PRO`

The recovery flow depends on the EcoFlow private/app API login because the BLE authentication step requires the EcoFlow user ID. Public API entries can monitor devices normally, but they do not support BLE Wi-Fi recovery.

## What the Feature Does

When a supported device stops sending MQTT data and appears on Bluetooth, the integration can:

1. Detect that the device has likely fallen off Wi-Fi.
2. Connect to the device over BLE.
3. Authenticate using the same account context used by the private/app API flow.
4. Send Wi-Fi credentials back to the device.
5. Wait for the device to rejoin Wi-Fi and resume normal MQTT updates.

Recovery is considered successful only after the device resumes normal cloud/MQTT communication.

## How Credentials Are Handled

The integration tries to minimize manual input:

- While the device is still online, the integration learns the current Wi-Fi SSID from live device data when that SSID is exposed by MQTT payloads.
- If one EcoFlow device already has a saved password for a given SSID, another supported device on the same SSID can reuse that password automatically.
- If that shared password succeeds, it is saved to the recovering device's own options for future use.

The integration does not attempt to read the stored Wi-Fi password back from the EcoFlow device.

## Configuration Options

Supported devices expose these additional options in **Settings** > **Devices & Services** > **EcoFlow Cloud** > **Configure**:

Newly added supported devices enable BLE Wi-Fi recovery by default. Existing entries keep their saved setting, and you can disable recovery per device if you prefer to keep it manual.

- **Enable BLE Wi-Fi recovery**
  Enables automatic recovery attempts when the device enters the `assume_offline` state.
- **Recovery Wi-Fi SSID**
  The SSID sent during BLE recovery. This may be filled automatically from live MQTT data if the device exposes it.
- **Recovery Wi-Fi password**
  The password used for BLE recovery.
- **Recovery Wi-Fi BSSID**
  Optional AP BSSID to target, in `AA:BB:CC:DD:EE:FF` format.
- **Recovery Wi-Fi channel**
  Optional AP channel to target. This is useful when the same SSID is advertised on both 2.4 GHz and 5 GHz and the device only supports the 2.4 GHz AP.
- **BLE recovery timeout (sec)**
  Maximum time allowed for a BLE recovery attempt and cloud rejoin wait.
- **BLE recovery cooldown (sec)**
  Minimum time between automatic recovery attempts for the same device.

## Automatic Recovery Flow

When a supported device stops updating:

1. The status sensor moves into `assume_offline`.
2. The integration checks whether BLE recovery is enabled and whether the device is currently visible through Home Assistant Bluetooth.
3. The integration selects credentials in this order:
   - the device's saved SSID/password
   - a learned SSID from recent MQTT data
   - a saved password from another EcoFlow device on the same SSID
4. If usable credentials exist, the integration attempts BLE recovery.
5. If credentials are missing or the recovery attempt fails while the device is visible over BLE, a Repairs issue is created.

## Repairs Flow

If the integration needs user input, Home Assistant will show a Repairs issue for the affected device.

The Repairs form:
- prefills the SSID when it was learned or already saved
- asks for the Wi-Fi password
- allows the SSID to be adjusted before saving

After the credentials are submitted, the integration stores them in the device options and can use them on the next recovery attempt.

## Manual Recovery

Two manual entry points are available for supported devices:

- The device button entity **Recover Wi-Fi via BLE**
- The service `ecoflow_cloud.recover_wifi_via_ble`

The service accepts:
- `serial_number` or `device_id`
- optional one-shot overrides for `ssid`, `password`, `bssid`, and `channel`

These overrides apply only to that service call.

## Diagnostics

The device status entity exposes BLE recovery state attributes including:
- whether a recovery is active
- attempt count
- last attempt time
- last result
- last error

The integration diagnostics output also includes BLE recovery state for supported devices.

## Limitations

- Recovery is currently limited to the River 2 family listed above.
- Recovery requires Home Assistant Bluetooth support to see and connect to the device.
- Recovery support is only available for private/app API entries, not public API entries.
- Success depends on the device being visible over BLE and able to rejoin the configured Wi-Fi network after provisioning.
