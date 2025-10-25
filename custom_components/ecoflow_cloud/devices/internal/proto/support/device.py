from typing import Any, cast

from homeassistant.util import dt # pyright: ignore[reportMissingImports]

from .....api.message import JSONDict, JSONMessage, Message
from .const import AddressId, Command, CommandFuncAndId
from .message import ProtoMessage


class PrivateAPIProtoDeviceMixin(object):
    def private_api_extract_quota_message(self, message: JSONDict) -> dict[str, Any]:
        if (
            "cmdFunc" in message
            and "cmdId" in message
        ):
            command_desc = CommandFuncAndId(
                func=message.cmd_func, id=message.cmd_id
            )

            try:
                command = Command(command_desc)
            except ValueError:
                pass
            
            if command in [Command.PRIVATE_API_POWERSTREAM_HEARTBEAT,
                           Command.PRIVATE_API_SMART_METER_DISPLAY_PROPERTY_UPLOAD, Command.PRIVATE_API_SMART_METER_RUNTIME_PROPERTY_UPLOAD
                        ]:
                return {"params": message["params"], "time": dt.utcnow()}
        raise ValueError("not a quota message")

    def private_api_get_quota(self) -> Message:
        json_prepared_payload = JSONMessage.prepare_payload({})

        return ProtoMessage(
            src=AddressId.APP,
            dest=AddressId.APP,
            from_=cast(str, json_prepared_payload["from"]),
        )
