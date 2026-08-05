from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class DPUXPack(_message.Message):
    __slots__ = ("amp", "bay", "design", "soc", "temp")
    BAY_FIELD_NUMBER: _ClassVar[int]
    SOC_FIELD_NUMBER: _ClassVar[int]
    AMP_FIELD_NUMBER: _ClassVar[int]
    DESIGN_FIELD_NUMBER: _ClassVar[int]
    TEMP_FIELD_NUMBER: _ClassVar[int]
    bay: int
    soc: int
    amp: float
    design: float
    temp: int
    def __init__(self, bay: int | None = ..., soc: int | None = ..., amp: float | None = ..., design: float | None = ..., temp: int | None = ...) -> None: ...

class DPUXBpInfo(_message.Message):
    __slots__ = ("packs",)
    PACKS_FIELD_NUMBER: _ClassVar[int]
    packs: _containers.RepeatedCompositeFieldContainer[DPUXPack]
    def __init__(self, packs: _Iterable[DPUXPack | _Mapping] | None = ...) -> None: ...

class DPUXDisplayPropertyExtra(_message.Message):
    __slots__ = ("bp_info",)
    BP_INFO_FIELD_NUMBER: _ClassVar[int]
    bp_info: DPUXBpInfo
    def __init__(self, bp_info: DPUXBpInfo | _Mapping | None = ...) -> None: ...
