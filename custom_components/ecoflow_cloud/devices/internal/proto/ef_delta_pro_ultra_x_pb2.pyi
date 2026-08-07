from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DPUXPack(_message.Message):
    __slots__ = ("bay", "soc", "amp", "design", "temp")
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
    def __init__(self, bay: _Optional[int] = ..., soc: _Optional[int] = ..., amp: _Optional[float] = ..., design: _Optional[float] = ..., temp: _Optional[int] = ...) -> None: ...

class DPUXBpInfo(_message.Message):
    __slots__ = ("packs",)
    PACKS_FIELD_NUMBER: _ClassVar[int]
    packs: _containers.RepeatedCompositeFieldContainer[DPUXPack]
    def __init__(self, packs: _Optional[_Iterable[_Union[DPUXPack, _Mapping]]] = ...) -> None: ...

class DPUXDisplayPropertyExtra(_message.Message):
    __slots__ = ("bp_info",)
    BP_INFO_FIELD_NUMBER: _ClassVar[int]
    bp_info: DPUXBpInfo
    def __init__(self, bp_info: _Optional[_Union[DPUXBpInfo, _Mapping]] = ...) -> None: ...
