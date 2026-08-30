from types import SimpleNamespace
from typing import Self, cast
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from custom_components.ecoflow_cloud import (
    CONF_ACCESS_KEY,
    CONF_API_HOST,
    CONF_GROUP,
    CONF_PASSWORD,
    CONF_SECRET_KEY,
    CONF_USERNAME,
    CONFIG_VERSION,
    async_setup_entry,
)
from custom_components.ecoflow_cloud.api import (
    EcoflowAuthException,
    EcoflowPrivateApiLoginRejected,
)
from custom_components.ecoflow_cloud.api.private_api import EcoflowPrivateApiClient


class _RejectedResponse:
    status = 200
    reason = "OK"
    text = ""

    async def json(self) -> dict[str, str]:
        return {"message": "Account doesn't exist or incorrect password", "code": "1000"}


class _RejectedSession:
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    async def post(self, *_args: object, **_kwargs: object) -> _RejectedResponse:
        return _RejectedResponse()


class SetupAuthTest(IsolatedAsyncioTestCase):
    def _entry(self, data: dict[str, str]) -> SimpleNamespace:
        return SimpleNamespace(
            version=CONFIG_VERSION,
            data={CONF_API_HOST: "api.example", CONF_GROUP: "Home", **data},
            options={},
            entry_id="entry-id",
        )

    async def test_ambiguous_private_rejection_stays_retryable(self) -> None:
        entry = self._entry({CONF_USERNAME: "user", CONF_PASSWORD: "password"})
        client = AsyncMock()
        client.login.side_effect = EcoflowPrivateApiLoginRejected("rejected", code="1000")

        with (
            patch(
                "custom_components.ecoflow_cloud.api.private_api.EcoflowPrivateApiClient",
                return_value=client,
            ),
            patch("custom_components.ecoflow_cloud.extract_devices", return_value={}),
            self.assertRaises(ConfigEntryNotReady),
        ):
            await async_setup_entry(
                cast(HomeAssistant, SimpleNamespace(data={})), cast(ConfigEntry, entry)
            )

        client.login.assert_awaited_once_with()

    async def test_private_coded_rejection_is_classified_as_ambiguous(self) -> None:
        client = EcoflowPrivateApiClient("api.example", "user", "password", "Home")

        with (
            patch(
                "custom_components.ecoflow_cloud.api.private_api.aiohttp.ClientSession",
                return_value=_RejectedSession(),
            ),
            self.assertRaises(EcoflowPrivateApiLoginRejected) as raised,
        ):
            await client.login()

        self.assertEqual(raised.exception.code, "1000")

    async def test_definitive_public_auth_failure_starts_reauth(self) -> None:
        entry = self._entry({CONF_ACCESS_KEY: "key", CONF_SECRET_KEY: "secret"})
        client = AsyncMock()
        client.login.side_effect = EcoflowAuthException("rejected", code="8513")

        with (
            patch(
                "custom_components.ecoflow_cloud.api.public_api.EcoflowPublicApiClient",
                return_value=client,
            ),
            patch("custom_components.ecoflow_cloud.extract_devices", return_value={}),
            self.assertRaises(ConfigEntryAuthFailed),
        ):
            await async_setup_entry(
                cast(HomeAssistant, SimpleNamespace(data={})), cast(ConfigEntry, entry)
            )

        client.login.assert_awaited_once_with()
