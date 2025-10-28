from .devices.internal.proto import (
    ecopacket_pb2,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    platform_pb2,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    powerstream_pb2,  # noqa: F401 # pyright: ignore[reportUnusedImport]
)

from .devices.internal.proto.ecoflow import (
# TODO: Switch everything to the new protos, but loading current and new at once leads to conflicts
    # Common,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    dev_apl_comm,  # noqa: F401 # pyright: ignore[reportUnusedImport]
)
