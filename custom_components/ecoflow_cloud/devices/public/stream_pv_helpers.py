"""Per-PV computed watts for the EcoFlow Stream family.

Stream family firmware (Stream Ultra, Stream Ultra X, Stream AC Pro, Stream
Microinverter) starting from version 1.0.1.88 stopped emitting the legacy
``powGetPv{N}`` per-PV keys. Instead, per-PV data is now published as
``plugInInfoPv{N}Amp`` and ``plugInInfoPv{N}Vol``. As a consequence, the
upstream ``WattsSensorEntity`` mappings against ``powGetPv*`` stay forever
``unknown`` for devices running the newer firmware.

This module provides a drop-in ``WattsSensorEntity`` subclass that:

1. Computes per-PV watts as ``Amp x Vol`` from the same payload tick.
2. Uses a synthetic ``mqtt_key`` so its ``unique_id`` cannot collide with
   an ``AmpSensorEntity`` that legitimately subscribes to the same
   ``plugInInfoPv{N}Amp`` key for the per-PV current sensor.
3. Auto-derives the ``vol_key`` from the ``amp_key`` via suffix replacement,
   so the device file only specifies ``amp_key`` once per PV input - less
   verbose, harder to typo.
4. Falls through to the upstream base class for attribute mapping, default
   value handling, ``with_energy()`` integration helpers, etc., by injecting
   the computed value back under the synthetic key and delegating
   ``_updated`` to ``super()``.

Registering both the legacy ``powGetPv*`` entity and this new helper with
``auto_enable=True`` keeps the integration firmware-agnostic: HA enables
whichever variant first sees a non-zero value.

References:
- https://github.com/tolwi/hassio-ecoflow-cloud/issues/584
- https://github.com/tolwi/hassio-ecoflow-cloud/issues/582
"""
from typing import Any

from custom_components.ecoflow_cloud.sensor import WattsSensorEntity


class StreamPvWattsSensorEntity(WattsSensorEntity):
    """Compute per-PV watts as ``amp x vol`` from EcoFlow Stream payloads.

    Example:
        StreamPvWattsSensorEntity(client, self, "plugInInfoPv2Amp",
                                  const.STREAM_POWER_PV_2)
        # subscribes to plugInInfoPv2Amp + plugInInfoPv2Vol, exposes watts
    """

    # Synthetic key prefix - chosen so it cannot exist as a real EcoFlow
    # payload field and cannot collide with sibling sensor unique_ids.
    _SYNTHETIC_KEY_PREFIX = "pvWatts"

    def __init__(
        self,
        client,
        device,
        amp_key: str,
        title,
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        if not amp_key.endswith("Amp"):
            raise ValueError(
                f"StreamPvWattsSensorEntity expects an amp_key ending in 'Amp', "
                f"got: {amp_key!r}"
            )
        self._amp_key = amp_key
        self._vol_key = amp_key[:-3] + "Vol"  # plugInInfoPv2Amp -> plugInInfoPv2Vol
        synthetic_key = f"{self._SYNTHETIC_KEY_PREFIX}_{amp_key}"
        super().__init__(client, device, synthetic_key, title, enabled, auto_enable)

    def _updated(self, data: dict[str, Any]) -> None:  # type: ignore[override]
        amp = data.get(self._amp_key)
        vol = data.get(self._vol_key)
        if amp is None or vol is None:
            # Let the upstream pipeline handle offline / default-value reset
            super()._updated(data)
            return
        try:
            watts = float(amp) * float(vol)
        except (TypeError, ValueError):
            return
        # Inject the computed value under our synthetic mqtt_key and let the
        # upstream _updated() do the rest (auto-enable, attribute mapping,
        # _update_value, schedule_update_ha_state). We deliberately mutate a
        # shallow copy to avoid surprising other sensors that read the same
        # payload dict afterwards.
        super()._updated({**data, self.mqtt_key: watts})
