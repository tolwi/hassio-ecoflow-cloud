from .devices.internal.proto import (
    ecopacket_pb2,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    ef_dp3_iobroker_pb2,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    ef_river3_pb2,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    platform_pb2,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    powerstream_pb2,  # noqa: F401 # pyright: ignore[reportUnusedImport]
)

# TODO: Switch everything to the new protos, but loading current and new at once leads to conflicts
