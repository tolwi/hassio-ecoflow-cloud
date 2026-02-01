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

Click **Submit** to save your changes. The integration will reload with the new settings.
