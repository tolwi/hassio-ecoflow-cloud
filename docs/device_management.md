# Device Management

This guide explains how to add, remove, and configure your EcoFlow devices within Home Assistant using the EcoFlow Cloud integration.

## 1. Adding a Device

To add a new device to an existing integration entry, you must use the **Reconfigure** option.

**Steps:**
1. In Home Assistant, go to **Settings** > **Devices & Services**.
2. Find the **EcoFlow Cloud** integration card.
3. Click the **three dots** (vertical ellipsis) menu on the integration card.
4. Select **Reconfigure**.
5. The integration will authenticate (using your existing API keys or App credentials).
6. You will be presented with a menu:
   *   **Add device**
   *   **Remove device**
   *   **Finish**
7. Select **Add device** and click **Next**.
8. Follow the prompts to select and confirm the new device.

---

## 2. Removing a Device

Removing a device is also done via the **Reconfigure** menu.

**Steps:**
1. In Home Assistant, go to **Settings** > **Devices & Services**.
2. Find the **EcoFlow Cloud** integration card.
3. Click the **three dots** (vertical ellipsis) menu.
4. Select **Reconfigure**.
5. In the menu, select **Remove device** and click **Next**.
6. Choose the device you want to remove from the dropdown list.
7. Click **Submit**.

The device and all its associated entities will be removed from Home Assistant.

---

## 3. Configuring Device Options

Use the **Configure** button to adjust specific settings for your devices, such as refresh intervals and charging limits.

**Steps:**
1. Go to **Settings** > **Devices & Services**.
2. Find the **EcoFlow Cloud** integration card.
3. Click the **Configure** button.
4. You will be prompted to **Select device**. Choose the device you wish to adjust and click **Submit**.
5. You will see a form with the following options:

**Configuration Options:**

*   **Charging power slider step**:
    *   Defines the increment size for the charging power slider (e.g., changing power by 10W or 50W steps).
*   **Data refresh period (sec)**:
    *   Controls how often Home Assistant updates the device entities with the latest data received from the cloud.
    *   *Note: This integration does **not** poll the device. Data is pushed by the cloud via MQTT, and this setting only determines how frequently Home Assistant reflects the latest received values.*
*   **Diagnostic mode**:
    *   Enables the collection of raw MQTT messages (commands, replies, status) in memory.
    *   This data is included when you download the integration diagnostics, which is useful for debugging issues.
    *   *Note: This does not force the creation of additional entities, it only affects the "Download Diagnostics" feature.*
*   **Assume offline timeout (sec)**:
    *   Time in seconds after which the device status changes to `assume_offline` if no new data is received.
    *   After 3x this duration without data, the status changes to `offline`.
    *   *Note: For some devices, this state triggers sending a quota message to attempt to recover data reception or obtain the real device status.*
*   **Verbose status mode**:
    *   Enables the display of the intermediate `assume_offline` status in the Main Status Entity.
    *   If disabled (default), the status will remain `online` during the assume offline timeout, and then switch directly to `offline`.
    *   If enabled, the status will change to `assume_offline` as soon as the initial data timeout is reached.
*   **BLE Wi-Fi recovery options**:
    *   These options are shown only for supported devices.
    *   Supported today: `RIVER_2`, `RIVER_2_MAX`, `RIVER_2_PRO`.
    *   Requires the private/app API login flow. Public API entries do not support BLE Wi-Fi recovery.
    *   Newly added supported devices enable BLE Wi-Fi recovery by default. Existing entries keep their saved setting.
    *   The available fields are:
        *   **Enable BLE Wi-Fi recovery**
        *   **Recovery Wi-Fi SSID**
        *   **Recovery Wi-Fi password**
        *   **Recovery Wi-Fi BSSID**
        *   **Recovery Wi-Fi channel**
        *   **BLE recovery timeout (sec)**
        *   **BLE recovery cooldown (sec)**

Click **Submit** to save your changes. The integration will reload with the new settings.

---

## 4. BLE Wi-Fi Recovery Behavior

For supported River 2 family devices, the integration can try to restore Wi-Fi over Bluetooth when the device drops off MQTT and falls back to BLE-only visibility.

The recovery flow is designed to reduce manual setup:

*   The integration learns the active Wi-Fi SSID from live MQTT data when the device exposes it while still online.
*   If one EcoFlow device already has a saved password for that SSID, another supported device can reuse it automatically.
*   If credentials are still missing, or if recovery fails while the device is visible over BLE, Home Assistant raises a Repairs issue prompting for the SSID and password.
*   The Repairs form pre-fills the SSID when the integration has already learned or saved it.

For more detail, see [BLE Wi-Fi Recovery](ble_wifi_recovery.md).

---

## 5. Manual BLE Recovery

Supported devices also expose manual recovery actions:

*   A device button entity named **Recover Wi-Fi via BLE**
*   A service named `ecoflow_cloud.recover_wifi_via_ble`

The service accepts:
*   `serial_number` or `device_id`
*   optional one-shot overrides for `ssid`, `password`, `bssid`, and `channel`

These overrides are useful for testing or for recovering a device before you save its credentials permanently.
